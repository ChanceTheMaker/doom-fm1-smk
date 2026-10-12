#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Prepare an application-only stock restore plan from two fresh reads. Never writes a device."""
import argparse
import hashlib
import json
from pathlib import Path

LO, HI, SIZE = 0x4000, 0x9d000, 0x100000
def sha(data):
    return hashlib.sha256(data).hexdigest()

def plan(current, second, stock, candidate):
    if any(len(b) != SIZE for b in (current, second, stock, candidate)):
        raise ValueError('All inputs must be complete 1 MiB reads/images')
    if current != second:
        raise ValueError('Fresh reads disagree')
    if current[:LO] != stock[:LO] or current[0xc1000:0xc1000+556] != stock[0xc1000:0xc1000+556]:
        raise ValueError('Boot header or unit calibration differs from the verified backup')
    if candidate[:LO] != stock[:LO] or candidate[HI:] != stock[HI:]:
        raise ValueError('Candidate changed protected bytes')
    if current[LO:HI] not in (candidate[LO:HI], stock[LO:HI]):
        raise ValueError('Application is neither the staged Doom build nor verified stock; inspect manually')
    target = current[:LO] + stock[LO:HI] + current[HI:]
    sectors = [{'address': hex(a), 'before_sha256': sha(current[a:a+4096]),
                'after_sha256': sha(target[a:a+4096])}
               for a in range(LO, HI, 4096) if current[a:a+4096] != target[a:a+4096]]
    return target, {'operation': 'restore-stock-application-only', 'device_written': False,
                    'current_sha256': sha(current), 'target_sha256': sha(target),
                    'write_min': hex(LO), 'write_end_exclusive': hex(HI), 'sectors': sectors}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--kit', type=Path, default=Path('build/try-smk-pro'))
    p.add_argument('--reads', type=Path, nargs=2, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    manifest = json.loads((a.kit/'manifest.json').read_text())
    stock = (a.kit/'stock-restore.bin').read_bytes()
    candidate = (a.kit/'doom-device-image.bin').read_bytes()
    if sha(stock) != manifest['restore_sha256'] or sha(candidate) != manifest['image_sha256']:
        p.error('Kit hashes disagree; stop and inspect')
    target, report = plan(*(f.read_bytes() for f in a.reads), stock, candidate)
    a.out.mkdir(parents=True, exist_ok=False)
    (a.out/'restore-reference.bin').write_bytes(target)
    (a.out/'plan.json').write_text(json.dumps(report, indent=2)+'\n')
    print(f"Prepared {len(report['sectors'])} application sectors. No device accessed or written.")
    print('Use an SMK-bounded adapter writer with per-sector precheck/readback; never write the full reference image.')

if __name__ == '__main__':
    main()
