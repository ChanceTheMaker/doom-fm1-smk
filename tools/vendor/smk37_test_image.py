#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Build a private, experimental recovery image. No device access or FWSC output.
Preserves the validated owner's stock layout, bootloader and all non-app data.
Hardware operation and SMK restore writes remain unverified.
"""
import argparse
import json
import struct
from pathlib import Path
from fm1pkg_make import crc16, sfc
from smk37_backup import inspect_backup, digest
from smk37_layout import decode_flash, entry


def replace_application(stock, app):
    layout, old_files = decode_flash(stock)
    base = layout['application_base']
    if base != 0x4000 or layout['entry_point'] != 0x02000120:
        raise ValueError('Unexpected application address or entry')
    if not app or len(app) % 4 or app[:4] != bytes.fromhex('04818000'):
        raise ValueError('Invalid application entry/alignment')
    original = next(f for f in layout['files'] if f['name'] == 'app.bin')
    if len(app) > original['bytes']:
        raise ValueError('Application exceeds stock slot')
    block_size = layout['application_block_bytes']
    extent = (block_size + 31) & ~31
    area = bytearray(stock[base:base + extent])
    sfc(area, 0, len(area), 0, layout['chip_key'])
    offset, length = original['offset'], original['bytes']
    replacement = app + b'\xff' * (length - len(app))
    area[offset:offset + length] = replacement
    matches = []
    for pos in range(32, offset, 32):
        item = entry(area[pos:pos + 32])
        if item['name'] == 'app.bin':
            matches.append(pos)
        if item['index']:
            break
    if len(matches) != 1:
        raise ValueError('Ambiguous application directory')
    pos = matches[0]
    struct.pack_into('<H', area, pos + 2, crc16(replacement))
    struct.pack_into('<H', area, pos, crc16(area[pos + 2:pos + 32]))
    struct.pack_into('<H', area, 2, crc16(area[32:block_size]))
    struct.pack_into('<H', area, 0, crc16(area[2:32]))
    sfc(area, 0, len(area), 0, layout['chip_key'])
    candidate = stock[:base] + bytes(area) + stock[base + extent:]
    checked, files = decode_flash(candidate)
    if files.pop('app.bin') != replacement:
        raise ValueError('Application round-trip mismatch')
    old_files.pop('app.bin')
    if files != old_files or checked['regions'] != layout['regions'] or checked['root'] != layout['root']:
        raise ValueError('Non-application contents changed')
    # Only the application bytes and four CRC16 fields (two entry fields and
    # two header fields = eight bytes total) may differ in the encrypted image.
    allowed = ((base, base + 4), (base + pos, base + pos + 4),
               (base + offset, base + offset + length))
    for i, (a, b) in enumerate(zip(stock, candidate)):
        if a != b and not any(lo <= i < hi for lo, hi in allowed):
            raise ValueError('Unexpected change outside application/CRC fields')
    return candidate


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--backups', nargs=2, type=Path, required=True)
    ap.add_argument('--stock-package', type=Path, required=True)
    ap.add_argument('--app-manifest', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    try:
        stock, second = (p.read_bytes() for p in args.backups)
        evidence = inspect_backup(stock, second, args.stock_package.read_bytes())
        manifest = json.loads(args.app_manifest.read_text())
        if manifest['board'] != 'SMK-37 Pro' or manifest['flash_write_support'] is not False:
            raise ValueError('Wrong board or flash-writing application')
        image_path = Path(manifest['image'])
        if image_path.name != str(image_path):
            raise ValueError('Application filename must be local to manifest')
        app = (args.app_manifest.parent / image_path).read_bytes()
        if digest(app) != manifest['sha256'] or len(app) != manifest['bytes']:
            raise ValueError('Application manifest mismatch')
        candidate = replace_application(stock, app)
        if candidate[:0x4000] != stock[:0x4000] or candidate[0x9d000:] != stock[0x9d000:]:
            raise ValueError('Protected data changed')
        sectors = [i for i in range(0, len(stock), 4096) if stock[i:i+4096] != candidate[i:i+4096]]
        if not sectors or any(i < 0x4000 or i >= 0x9d000 for i in sectors):
            raise ValueError('Unexpected write sector range')
        args.out.mkdir(parents=True, exist_ok=False)
        files = {'smk37-test01-device-image.bin': candidate,
                 'smk37-stock-restore-device-image.bin': stock,
                 'smk37-test01-app.bin': app}
        for name, data in files.items():
            (args.out / name).write_bytes(data)
        report = {'name': 'Felucca [Salt] SMK-37 Pro Test 01',
                  'status': 'EXPERIMENTAL - NOT HARDWARE TESTED',
                  'method': 'raw recovery-adapter image; not a web or vendor updater package',
                  'publishable': False, 'contains_private_stock_data': True,
                  'flashed': False, 'smk_restore_writes_tested': False,
                  'backup_evidence': evidence, 'application_manifest': manifest,
                  'changed_sectors': [hex(i) for i in sectors],
                  'preserved_ranges': ['0x000000-0x003fff', '0x09d000-0x0fffff'],
                  'files': {n: {'bytes': len(d), 'sha256': digest(d)} for n, d in files.items()}}
        (args.out / 'manifest.json').write_text(json.dumps(report, indent=2) + '\n')
        (args.out / 'SHA256SUMS').write_text(''.join(digest(d) + '  ' + n + '\n' for n, d in files.items()))
        (args.out / 'README.txt').write_text("""Felucca [Salt] SMK-37 Pro Test 01
EXPERIMENTAL: custom startup, display, audio and physical control mapping are untested.

This private build is for the owner's backed-up SMK-37 Pro running Pro 016.
The device image preserves the exact stock bootloader and all non-app bytes,
including calibration. Only app.bin and its directory/block CRCs change.
The restore image is the exact verified stock backup, not a generic firmware.
Do not publish or use either device image on another instrument.

This is a raw recovery-adapter build, NOT an .fwsc or UF2 file. Do not drag it
onto RPI-RP2 or use the web/vendor updater. The current read-only XIAO firmware
cannot install it. A separately reviewed SMK writer/restore workflow is required;
the FM-1 writer has the wrong address limit and must not be used unchanged.

Includes 37-key fixed-velocity playback, shared Felucca synthesis, provisional
encoder controls, sound pages and diagnostics. Saves, OTA, radio and TRS are
not enabled. Physical operation is unverified; stock functionality is not promised.
Flash installation has not been performed or authorized by creating this build.
""")
        print(json.dumps(report, indent=2))
    except (OSError, ValueError, KeyError, StopIteration) as exc:
        ap.exit(2, f'smk37_test_image: {exc}\n')


if __name__ == '__main__':
    main()
