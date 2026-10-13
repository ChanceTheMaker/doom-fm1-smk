#!/usr/bin/env python3
"""Every included sprite family must cover all of its engine animation states."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_native_art import read

wad = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'build/fixtures/native-art.wad'
rows = read(wad)
lumps = dict(rows)
inside = False
sprites = set()
for name, _ in rows:
    if name == 'S_START': inside = True
    elif name == 'S_END': inside = False
    elif inside: sprites.add(name)
families = {name[:4] for name in sprites}
assert {'POSS', 'TROO', 'PLAY', 'BAL1', 'CLIP'} <= families
states = (ROOT / 'third_party/doomgeneric/doomgeneric/info.c').read_text()
missing = []
checked = 0
for family, number, state in re.findall(
        r'\{SPR_(\w+),(\d+),[^\n]+//\s+(S_\w+)', states):
    if family not in families: continue
    frame = chr(ord('A') + (int(number) & 0x7fff))
    name = family + frame
    if not any(sprite.startswith(name) for sprite in sprites):
        missing.append(f'{state}: {name}')
    checked += 1
assert not missing, 'Missing reachable enemy frames:\n' + '\n'.join(missing)
assert checked >= 100, 'Sprite state parser did not cover the expected engine states'
print(f'PASS: {checked} states in {len(families)} sprite families have packed frames, including overkill deaths.')
