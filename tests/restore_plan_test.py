# SPDX-License-Identifier: GPL-3.0-only
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from plan_restore import plan, LO, HI, SIZE

class RestorePlanTest(unittest.TestCase):
    def setUp(self):
        self.stock = bytes(SIZE)
        self.doom = bytearray(self.stock)
        self.doom[LO:LO+4096] = b'X'*4096
        self.doom = bytes(self.doom)

    def test_preserves_current_persistent_data(self):
        current = bytearray(self.doom)
        current[HI:HI+4096] = b'P'*4096
        target, report = plan(bytes(current), bytes(current), self.stock, self.doom)
        self.assertEqual(target[:LO], bytes(current[:LO]))
        self.assertEqual(target[HI:], bytes(current[HI:]))
        self.assertEqual(target[LO:HI], self.stock[LO:HI])
        self.assertEqual([s['address'] for s in report['sectors']], [hex(LO)])

    def test_rejects_mismatched_or_unrecognized_reads(self):
        for offset in (0, LO+4096, 0xc1000):
            changed = bytearray(self.doom)
            changed[offset] ^= 1
            with self.assertRaises(ValueError):
                plan(bytes(changed), bytes(changed), self.stock, self.doom)
        with self.assertRaises(ValueError):
            plan(self.doom, self.stock, self.stock, self.doom)
        with self.assertRaises(ValueError):
            plan(self.doom[:-1], self.doom[:-1], self.stock, self.doom)

    def test_already_stock(self):
        _, report = plan(self.stock, self.stock, self.stock, self.doom)
        self.assertEqual(report['sectors'], [])

if __name__ == '__main__': unittest.main()
