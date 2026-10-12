#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Compile a host-only Doom baseline. Never generates device firmware."""
import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--board', required=True, choices=['fm1', 'smk37-pro', 'smk37-elite'])
p.add_argument('--cc', default='cc')
a = p.parse_args()
profile = json.loads((ROOT / 'targets' / (a.board + '.json')).read_text())
engine = ROOT / 'third_party/doomgeneric/doomgeneric'
if not (engine / 'Makefile').exists():
    p.error('Run git submodule update --init first.')
# Use exactly the upstream portable source set; replace only the X11 frontend.
line = re.search(r'^SRC_DOOM\s*=\s*(.+)$', (engine / 'Makefile').read_text(), re.M)
if not line:
    p.error('Pinned upstream source list missing.')
sources = [engine / (name[:-2] + '.c') for name in line[1].split() if name != 'doomgeneric_xlib.o']
sources.append(ROOT / 'src/host/doomgeneric_host.c')
out = ROOT / 'build' / a.board
out.mkdir(parents=True, exist_ok=True)
command = [a.cc, '-std=c11', '-O2', '-D_DEFAULT_SOURCE', '-DNORMALUNIX', '-DLINUX',
           '-DDOOMGENERIC_RESX=320', '-DDOOMGENERIC_RESY=200', '-I' + str(engine),
           *map(str, sources), '-lm', '-o', str(out / 'doom-host')]
subprocess.run(command, check=True)
(out / 'target.json').write_text(json.dumps({'build_kind': 'host-only', 'profile': profile,
    'output_framebuffer_bytes': 320 * 200 * 4, 'native_firmware': False}, indent=2) + '\n')
print('Built host baseline for', profile['name'], 'at', out / 'doom-host')
print('This is NOT flashable firmware.')
