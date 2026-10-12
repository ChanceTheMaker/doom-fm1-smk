#!/usr/bin/env python3
"""Offline failure-path tests: no serial imports or hardware access."""
import contextlib
import io
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from fm1_recovery import SIZE, LO, HI, SECTOR, apply, changed_sectors, make_plan


class MemoryDevice:
    def __init__(self, before, failure=None):
        self.data = bytearray(before)
        self.failure = failure
        self.writes = []

    def read(self, address, length):
        return bytes(self.data[address:address+length])

    def write(self, address, data):
        self.writes.append(address)
        if self.failure == 'write':
            return 'ERR'
        if self.failure != 'readback':
            self.data[address:address+len(data)] = data
        return 'OK'


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.before = bytes(SIZE)
        target = bytearray(self.before)
        target[LO] = target[HI-SECTOR] = 1
        self.target = bytes(target)
        self.sectors = [LO, HI-SECTOR]

    def run_apply(self, device, target=None, sectors=None):
        with contextlib.redirect_stdout(io.StringIO()):
            return apply(device, self.before, target or self.target,
                         self.sectors if sectors is None else sectors, lambda event: None)

    def test_complete_readback_and_bounded_writes(self):
        device = MemoryDevice(self.before)
        self.assertEqual(self.run_apply(device), self.target)
        self.assertEqual(device.writes, self.sectors)

    def test_protected_ranges_rejected_before_write(self):
        for address in (0, LO-1, HI, SIZE-1):
            target = bytearray(self.target)
            target[address] = 1
            device = MemoryDevice(self.before)
            with self.assertRaises(ValueError):
                self.run_apply(device, bytes(target))
            self.assertEqual(device.writes, [])

    def test_incomplete_and_out_of_bounds_plan_rejected(self):
        for sectors in ([], [LO], [0, LO], [LO, HI], self.sectors[::-1]):
            device = MemoryDevice(self.before)
            with self.assertRaises(ValueError):
                self.run_apply(device, sectors=sectors)
            self.assertEqual(device.writes, [])

    def test_stale_backup_rejected(self):
        device = MemoryDevice(self.before)
        device.data[LO+1] = 2
        with self.assertRaises(ValueError):
            self.run_apply(device)
        self.assertEqual(device.writes, [])

    def test_write_and_readback_failure_stop_without_retry(self):
        for failure in ('write', 'readback'):
            device = MemoryDevice(self.before, failure)
            with self.assertRaises(ValueError):
                self.run_apply(device)
            self.assertEqual(device.writes, [LO])

    def test_mismatching_fresh_reads_rejected(self):
        with self.assertRaises(ValueError):
            make_plan(self.before, self.target, b'', '')

    def test_noop_has_no_writes(self):
        device = MemoryDevice(self.before)
        self.assertEqual(self.run_apply(device, self.before, []), self.before)
        self.assertEqual(device.writes, [])


if __name__ == '__main__':
    unittest.main()
