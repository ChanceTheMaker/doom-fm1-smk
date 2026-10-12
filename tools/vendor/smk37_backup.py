#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Offline Pro 016 backup validation; no hardware, writes or installation approval."""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from smk37_package import inspect_bytes

PACKAGE_SHA = '2d98ce72530e71d617384963423820536f094501299e2cfec0a8d3c3fb6bcfb0'
FLASH_BYTES = 0x100000
TRIM_ADDRESS = 0xc1000
TRIM_BYTES = 556


def digest(data):
    return hashlib.sha256(data).hexdigest()


def validate_trim(record):
    if len(record) != TRIM_BYTES or record[548:] != b'trimdat\0':
        raise ValueError('Invalid calibration record length or marker')
    curves = [struct.unpack_from('<5H', record, 168 + key * 10) for key in range(37)]
    for key, curve in enumerate(curves):
        if any(v > 1023 for v in curve) or any(a >= b for a, b in zip(curve, curve[1:])):
            raise ValueError(f'Invalid calibration curve for key {key}')
    return {'address': TRIM_ADDRESS, 'bytes': len(record), 'sha256': digest(record),
            'validated_key_curves': len(curves)}


def compare_reads(first, second):
    if len(first) != FLASH_BYTES or len(second) != FLASH_BYTES:
        raise ValueError('Both backup reads must contain exactly the first 1 MiB')
    if first != second:
        raise ValueError('Independent backup reads differ')
    return validate_trim(first[TRIM_ADDRESS:TRIM_ADDRESS + TRIM_BYTES])


def inspect_backup(first, second, package):
    trim = compare_reads(first, second)
    if digest(package) != PACKAGE_SHA:
        raise ValueError('Expected the pinned SMK-37 Pro 016 vendor package')
    inventory = inspect_bytes(package)
    blocks = inventory['marker_blocks']
    logical = b''.join(package[i:i + 47] for i in range(0, blocks * 48, 48)) + package[blocks * 48:]
    entries = [e for e in inventory['entries'] if e['name'] == 'flash.bin' and e['type'] == 0]
    if len(entries) != 1:
        raise ValueError('Expected one stock flash payload')
    entry = entries[0]
    stock = logical[entry['offset']:entry['offset'] + entry['bytes']]
    if len(stock) != 0x9d000 or first[:len(stock)] != stock:
        raise ValueError('Backup firmware does not exactly match stock Pro 016')
    return {'model': inventory['product'], 'backup_sha256': digest(first),
            'verified_read_bytes': FLASH_BYTES, 'independent_reads_match': True,
            'stock_payload_exact_match': True, 'stock_payload_bytes': len(stock),
            'calibration': trim, 'preserved_tail_sha256': digest(first[len(stock):]),
            'physical_capacity_independently_verified': False,
            'custom_firmware_installation_approved': False}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('first', type=Path)
    ap.add_argument('second', type=Path)
    ap.add_argument('package', type=Path)
    args = ap.parse_args()
    try:
        result = inspect_backup(args.first.read_bytes(), args.second.read_bytes(), args.package.read_bytes())
    except (OSError, ValueError) as exc:
        ap.exit(2, f'smk37_backup: {exc}\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
