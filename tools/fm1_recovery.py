#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Plan from two fresh FM-1 reads; explicitly write only reviewed application sectors.

Private session files belong under ignored build/try-fm1. Never boot automatically.
The XIAO must already be running the verified FM-1 transporter firmware.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

from stage_fm1_test import replace_app
from smk37_layout import decode_flash

SIZE, LO, HI, SECTOR = 0x100000, 0x4000, 0x93000, 4096


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(path, data):
    with path.open('xb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def make_plan(first, second, app, app_sha):
    if len(first) != SIZE or first != second:
        raise ValueError('Require two identical complete fresh 1 MiB reads')
    if sha(app) != app_sha:
        raise ValueError('Application hash differs from reviewed candidate')
    layout, _ = decode_flash(first)
    if layout['chip_key'] != 0x980f or layout['application_base'] != LO:
        raise ValueError('Unexpected FM-1 chip key or application layout')
    # replace_app also rejects SMK slot sizes and corrupt original CRCs.
    target = replace_app(first[:HI], app) + first[HI:]
    _, files = decode_flash(target)
    if files['app.bin'][:len(app)] != app:
        raise ValueError('Decoded target application mismatch')
    sectors = changed_sectors(first, target)
    return target, dict(board='FM-1', app_sha256=app_sha,
                       before_sha256=sha(first), target_sha256=sha(target),
                       write_min=LO, write_end_exclusive=HI, sectors=sectors,
                       bootloader_preserved=True, device_data_preserved=True)


def changed_sectors(before, target):
    if len(before) != SIZE or len(target) != SIZE:
        raise ValueError('Invalid full image size')
    if before[:LO] != target[:LO] or before[HI:] != target[HI:]:
        raise ValueError('Protected bootloader or device data changed')
    return [a for a in range(LO, HI, SECTOR)
            if before[a:a+SECTOR] != target[a:a+SECTOR]]


def apply(io, before, target, sectors, log):
    if sectors != changed_sectors(before, target):
        raise ValueError('Sector plan differs from the complete bounded diff')
    if io.read(0, SIZE) != before:
        raise ValueError('Device changed since fresh backups; no writes')
    for n, address in enumerate(sectors, 1):
        if io.read(address, SECTOR) != before[address:address+SECTOR]:
            raise ValueError(f'Device changed at {address:#x}; stopped')
        log(dict(event='sector_begin', address=address))
        if io.write(address, target[address:address+SECTOR]) != 'OK':
            raise ValueError(f'Write failed at {address:#x}; no automatic retry')
        if io.read(address, SECTOR) != target[address:address+SECTOR]:
            raise ValueError(f'Readback mismatch at {address:#x}; stopped')
        log(dict(event='sector_verified', address=address))
        print(f'{n}/{len(sectors)} verified {address:#x}', flush=True)
    result = io.read(0, SIZE)
    if result != target:
        raise ValueError('Final full flash mismatch; do not boot')
    log(dict(event='complete', sha256=sha(result)))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['plan', 'write'])
    p.add_argument('--session', type=Path, required=True)
    p.add_argument('--app', type=Path, required=True)
    p.add_argument('--app-sha256', required=True)
    p.add_argument('--transporter-tools', type=Path)
    p.add_argument('--port')
    p.add_argument('--adapter-serial')
    a = p.parse_args()
    folder = a.session.resolve()
    before = (folder/'flash-read-1.bin').read_bytes()
    second = (folder/'flash-read-2.bin').read_bytes()
    target, plan = make_plan(before, second, a.app.read_bytes(), a.app_sha256)
    if a.mode == 'plan':
        save(folder/'expected-hud1.bin', target)
        save(folder/'preflight.json', (json.dumps(plan, indent=2)+'\n').encode())
        print(json.dumps({**plan, 'sectors': len(plan['sectors'])}, indent=2))
        print('No device accessed or written.')
        return
    # Reconstruct from the two reads and pinned application, never trust a
    # saved full-device target as input to flashing.
    if json.loads((folder/'preflight.json').read_text()) != plan:
        raise ValueError('Reviewed plan changed')
    if (folder/'expected-hud1.bin').read_bytes() != target:
        raise ValueError('Reviewed expected image changed')
    if not a.port or not a.adapter_serial or not a.transporter_tools:
        p.error('write requires port, adapter serial and transporter tools')
    sys.path.insert(0, str(a.transporter_tools.resolve()))
    import fm1t
    from serial.tools.list_ports import comports
    port = next((port for port in comports() if port.device == a.port), None)
    if not port or (port.vid, port.pid, port.serial_number) != (0x2e8a, 0x000a, a.adapter_serial):
        raise ValueError('Recovery adapter identity mismatch')
    with fm1t.find_port(a.port) as connection:
        connection.write_timeout = 5
        # Legacy FM-1 build has no caps command. Reject the separate SMK writers.
        if fm1t.request(connection, 'caps', timeout=3) != 'ERR unknown':
            raise ValueError('Not the verified legacy FM-1 transporter')
        if fm1t.status(connection).get('uboot') != '1':
            raise ValueError('FM-1 not in recovery')
        if fm1t.request(connection, 'info') != 'OK key=980F type=3 id=856014':
            raise ValueError('Chip identity mismatch')

        class Transport:
            def read(self, address, length):
                return fm1t.read_flash(connection, address, length, progress=False)

            def write(self, address, data):
                if address not in plan['sectors'] or len(data) != SECTOR:
                    raise ValueError('Write outside reviewed sector plan')
                return fm1t.write_sector(connection, address, data)

        with (folder/'write-journal.jsonl').open('x', buffering=1) as journal:
            def log(event):
                journal.write(json.dumps(event)+'\n')
                journal.flush()
                os.fsync(journal.fileno())
            log(dict(event='preflight', adapter_serial=a.adapter_serial, **plan))
            try:
                result = apply(Transport(), before, target, plan['sectors'], log)
                save(folder/'post-hud1.bin', result)
                save(folder/'write-result.json', (json.dumps(dict(
                    success=True, app_sha256=a.app_sha256, sha256=sha(result),
                    sectors_written=len(plan['sectors']), bootloader_preserved=True,
                    device_data_preserved=True), indent=2)+'\n').encode())
            except BaseException as error:
                log(dict(event='stopped', reason=str(error)))
                raise
    print('Complete flash verified; bootloader and device data preserved. No automatic boot.')


if __name__ == '__main__':
    main()
