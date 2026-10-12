#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Inspect a stock SMK flash layout in memory; output metadata, never firmware.

Reads the offset-zero JieLi flash header, top directory and first application
directory. Reserved regions are descriptors, not file-backed data. No device
access, binary extraction or package generation is provided.
"""
import argparse
import json
from pathlib import Path
import re
import struct

from fm1pkg_make import chipkey_decode, crc16, enc, sfc
from smk37_package import MAX_BYTES, inspect_bytes, sha


def bounded(data, offset, size, label):
    if offset < 0 or size < 0 or offset + size > len(data):
        raise ValueError(f'{label}: outside supplied flash payload')
    return data[offset:offset + size]


def entry(data):
    if len(data) != 32 or crc16(data[2:]) != struct.unpack_from('<H', data)[0]:
        raise ValueError('JLFS entry header CRC mismatch')
    checksum, offset, size, flags, reserved, index, name = struct.unpack_from('<HIIBBH16s', data, 2)
    return dict(name=name.split(b'\0', 1)[0].decode('ascii', errors='replace'),
                offset=offset, bytes=size, flags=flags, index=index, stored_crc16=checksum)


def single(entries, name):
    matches = [e for e in entries if e['name'] == name]
    if len(matches) != 1:
        raise ValueError(f'expected exactly one {name}')
    return matches[0]


def boot_config(data):
    """Length byte, NUL-terminated uppercase key, then exactly length bytes.

    Expects the config bytes after the 34-byte chip-key prefix. See JieLi
    new-firmware format research; integer interpretations are raw LE values,
    not a promise about the running hardware configuration.
    """
    result, pos = {}, 0
    while pos < len(data):
        size = data[pos]
        pos += 1
        end = data.find(b'\0', pos, min(pos + 65, len(data)))
        if end < 0 or not re.fullmatch(rb'[A-Z][A-Z0-9_]*', data[pos:end]):
            raise ValueError('invalid boot configuration key')
        name = data[pos:end].decode('ascii')
        value = bounded(data, end + 1, size, 'boot configuration value')
        if name in result:
            raise ValueError('duplicate boot configuration key')
        item = dict(hex=value.hex())
        if size == 4:
            item['uint32_le'] = int.from_bytes(value, 'little')
        if value and all(32 <= b < 127 for b in value):
            item['ascii'] = value.decode('ascii')
        result[name] = item
        pos = end + 1 + size
    return result


def decode_flash(flash):
    head = bytearray(bounded(flash, 0, 32, 'flash header'))
    enc(head, 0, 32)
    if crc16(head[2:]) != struct.unpack_from('<H', head)[0]:
        raise ValueError('flash header CRC mismatch (only offset-zero format supported)')
    root = []
    for i in range(64):
        record = bytearray(bounded(flash, 32 + 32*i, 32, 'root directory'))
        enc(record, 0, 32)
        item = entry(record)
        root.append(item)
        if item['index']:
            break
    else:
        raise ValueError('unterminated root directory')
    config = single(root, 'isd_config.ini')
    if config['bytes'] < 34:
        raise ValueError('isd_config.ini is too short for chip key')
    blob = bounded(flash, config['offset'], config['bytes'], 'isd_config.ini')
    if crc16(blob) != config['stored_crc16']:
        raise ValueError('boot configuration CRC mismatch')
    if crc16(blob[:32]) != struct.unpack_from('<H', blob, 32)[0]:
        raise ValueError('chip key CRC mismatch')
    key = chipkey_decode(blob[:32])
    settings = boot_config(blob[34:])
    descriptor = single(root, 'app_dir_head')
    if descriptor['flags'] != 0x81 or descriptor['offset'] % 32:
        raise ValueError('unsupported application directory descriptor')
    base = descriptor['offset']
    if base < 32 + 32*len(root):
        raise ValueError('application overlaps root directory')
    area = bytearray(bounded(flash, base, len(flash) - base, 'application area'))
    sfc(area, 0, len(area), 0, key)
    apphead = entry(bounded(area, 0, 32, 'application header'))
    if apphead['name'] != 'app_area_head' or apphead['flags'] != 0x83 or apphead['bytes'] < 32:
        raise ValueError('unsupported application area header')
    block = bounded(area, 32, apphead['bytes'] - 32, 'application block')
    if crc16(block) != apphead['stored_crc16']:
        raise ValueError('application block CRC mismatch')
    files, regions, extents, payloads = [], [], [], {}
    directory_end = 32
    for i in range(128):
        pos = 32 + 32*i
        if pos + 32 > apphead['bytes']:
            raise ValueError('application directory outside block')
        item = entry(bounded(area, pos, 32, 'application directory'))
        directory_end = pos + 32
        if item['flags'] & 0x10:
            # Addresses in region descriptors may exceed the supplied update
            # payload, refer to preserved storage or overlap other descriptors.
            regions.append(item)
        elif item['flags'] == 0x82:
            start, length = item['offset'], item['bytes']
            if start + length > apphead['bytes']:
                raise ValueError('application file outside block')
            if any(start < hi and start + length > lo for lo, hi in extents):
                raise ValueError('overlapping application files')
            extents.append((start, start + length))
            body = bounded(area, start, length, item['name'])
            if crc16(body) != item['stored_crc16']:
                raise ValueError('application file CRC mismatch')
            if item['name'] in payloads:
                raise ValueError('duplicate application filename')
            payloads[item['name']] = bytes(body)
            files.append(dict(**item, flash_payload_offset=base + start, sha256=sha(body)))
        else:
            raise ValueError('unsupported application entry flags')
        if item['index']:
            break
    else:
        raise ValueError('unterminated application directory')
    if any(lo < directory_end for lo, hi in extents):
        raise ValueError('application file overlaps directory')
    if 'app.bin' not in payloads:
        raise ValueError('missing app.bin')
    return dict(header_flash_size_field=struct.unpack_from('<I', head, 8)[0],
                supplied_flash_bytes=len(flash), chip_key=key, root=root,
                boot_configuration=settings,
                application_base=base, entry_point=apphead['offset'],
                application_block_bytes=apphead['bytes'], files=files, regions=regions,
                region_offset_semantics='Raw JLFS fields; not validated physical erase/write addresses',
                validation='header, directory, key, application block and file CRCs checked',
                limitations='No physical capacity, RAM map, bootloader execution, resource directory or recovery validation'), payloads


def inspect_layout(raw):
    package = inspect_bytes(raw)
    blocks = package['marker_blocks']
    logical = b''.join(raw[i:i+47] for i in range(0, blocks*48, 48)) + raw[blocks*48:]
    flash = single(package['entries'], 'flash.bin')
    if flash['type'] != 0 or not flash['raw_crc_matches']:
        raise ValueError('unsupported flash payload type or CRC')
    report, payloads = decode_flash(logical[flash['offset']:flash['offset'] + flash['bytes']])
    return dict(product=package['product'], package_sha256=package['sha256'], **report), payloads


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('packages', type=Path, nargs='+')
    args = ap.parse_args()
    reports = []
    try:
        for path in args.packages:
            with path.open('rb') as source:
                report, _ = inspect_layout(source.read(MAX_BYTES + 1))
            reports.append(dict(file=path.name, **report))
    except (OSError, ValueError) as error:
        ap.exit(2, f'smk37_layout: {error}\n')
    print(json.dumps(reports, indent=2))


if __name__ == '__main__':
    main()
