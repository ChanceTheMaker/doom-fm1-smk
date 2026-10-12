#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Offline FWSC/UFW inventory. Never opens hardware, extracts or writes firmware.

Checks header/directory integrity and fingerprints payloads. This is not an
authenticity or device compatibility check. Vendor metadata CRCs are reported
without assuming the same encoding as the flash and OTA payloads.
The shared container cipher/CRC helpers come from Felucca's FM-1 packer;
none of that packer's flash layout assumptions are used here.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from fm1pkg_make import crc16, enc

MAX_BYTES = 32 * 1024 * 1024


def sha(data):
    return hashlib.sha256(data).hexdigest()


def inspect_bytes(raw):
    if not 960 <= len(raw) <= MAX_BYTES:
        raise ValueError("FWSC size outside supported range (960 bytes to 32 MiB)")
    logical = b''.join(raw[j:j + 47] for j in range(0, 960, 48)) + raw[960:]
    header = bytearray(logical[:64])
    enc(header, 0, 64)
    if crc16(header[2:]) != struct.unpack_from('<H', header)[0]:
        raise ValueError("UFW header CRC mismatch")
    total, count = struct.unpack_from('<IH', header, 4)
    blocks = len(raw) - total
    if blocks not in (20, 36) or len(raw) < blocks * 48:
        raise ValueError("unsupported FWSC marker count or incorrect declared size")
    markers = raw[47:blocks * 48:48]
    product = ''.join(chr((b - j - 1) & 255) for j, b in enumerate(markers) if b != 0x7d)
    if not product or any(not 32 <= ord(c) < 127 for c in product):
        raise ValueError("unrecognized FWSC product markers")
    logical = b''.join(raw[j:j + 47] for j in range(0, blocks * 48, 48)) + raw[blocks * 48:]
    end = 64 + count * 80
    if not 1 <= count <= 128 or end > total:
        raise ValueError("invalid UFW entry count")
    table = logical[64:end]
    if crc16(table) != struct.unpack_from('<H', header, 2)[0]:
        raise ValueError("UFW directory CRC mismatch")
    entries, regions = [], []
    for j in range(count):
        record = bytearray(table[j * 80:(j + 1) * 80])
        enc(record, 0, 80)
        kind, index, checksum, reserved, offset, size, aligned = struct.unpack_from('<HHHHIII', record)
        name = bytes(record[64:80]).split(b'\0', 1)[0].decode('ascii', errors='replace')
        if offset < end or offset + size > total or aligned < size:
            raise ValueError(f"entry {j} has invalid bounds")
        if size and any(offset < hi and offset + size > lo for lo, hi in regions):
            raise ValueError(f"entry {j} overlaps another entry")
        if size:
            regions.append((offset, offset + size))
        body = logical[offset:offset + size]
        matches = crc16(body) == checksum
        if kind in (0, 2, 100, 255) and not matches:
            raise ValueError(f"entry {j} payload CRC mismatch")
        entries.append(dict(name=name, type=kind, index=index, offset=offset,
                            bytes=size, sha256=sha(body), stored_crc16=checksum,
                            raw_crc_matches=matches))
    return dict(product=product, chip=bytes(header[16:32]).split(b'\0', 1)[0].decode('ascii', errors='replace'),
                bytes=len(raw), sha256=sha(raw), logical_sha256=sha(logical),
                marker_blocks=blocks, header_directory_crc_valid=True,
                compatibility='unverified', entries=entries)


def inspect_file(path):
    with path.open('rb') as source:
        raw = source.read(MAX_BYTES + 1)
    return dict(file=path.name, **inspect_bytes(raw))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('packages', type=Path, nargs='+')
    args = ap.parse_args()
    try:
        reports = [inspect_file(path) for path in args.packages]
    except (OSError, ValueError) as error:
        ap.exit(2, f"smk37_package: {error}\n")
    print(json.dumps(reports, indent=2))


if __name__ == '__main__':
    main()
