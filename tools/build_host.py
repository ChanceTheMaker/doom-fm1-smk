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
p.add_argument('--display', choices=['rgba','strip'], default='strip')
p.add_argument('--no-wipe', action='store_true')
p.add_argument('--mapped-wad', action='store_true')
p.add_argument('--small-room', action='store_true')
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

out = ROOT / 'build' / a.board / (a.display + ('-no-wipe' if a.no_wipe else '') + ('-mapped' if a.mapped_wad else '') + ('-small' if a.small_room else ''))
out.mkdir(parents=True, exist_ok=True)
if a.small_room:
    from prepare_engine import prepare
    engine=prepare(out/'engine')
    sources=[engine/s.name for s in sources]
# Keep upstream pinned and clean; append introspection only in a generated copy.
zone=out/'z_zone_probe.c'
zone.write_text((engine/'z_zone.c').read_text()+'\n'+(ROOT/'src/host/zone_probe.inc').read_text())
sources=[zone if s.name=='z_zone.c' else s for s in sources]
flags=['-I'+str(ROOT/'src/host'), '-I'+str(ROOT/'src/common'),
       '-Wl,--wrap=I_ZoneBase', '-Wl,--wrap=Z_Malloc', '-fstack-usage']
if a.display=='strip':
    sources=[ROOT/'src/common/doomgeneric_create.c' if s.name=='doomgeneric.c' else s for s in sources]
    sources.append(ROOT/'src/common/lcd_frame.c')
    flags+=['-DCMAP256','-DDP_STRIP','-Wl,--wrap=I_FinishUpdate']
if a.mapped_wad:
    sources=[ROOT/'src/host/w_file_mmap.c' if s.name=='w_file_stdc.c' else s for s in sources]
    sources.append(ROOT/'src/common/wad_view.c')
if a.no_wipe:
    sources=[ROOT/'src/common/wipe_disabled.c' if s.name=='f_wipe.c' else s for s in sources]
sources += [ROOT/'src/host/doomgeneric_host.c',ROOT/'src/host/memory_probe.c',ROOT/'src/host/input_smoke.c']
command = [a.cc, '-std=c11', '-O2', '-D_DEFAULT_SOURCE', '-DNORMALUNIX', '-DLINUX',
           '-DDOOMGENERIC_RESX=320', '-DDOOMGENERIC_RESY=200', '-I' + str(engine),
           *flags, *map(str, sources), '-lm', '-o', str(out / 'doom-host')]
subprocess.run(command, check=True, cwd=out)
(out / 'target.json').write_text(json.dumps({'build_kind': 'host-only', 'profile': profile,
    'small_room': a.small_room, 'mapped_wad': a.mapped_wad, 'display': a.display, 'no_wipe': a.no_wipe, 'output_framebuffer_bytes': 320 * 200 * 4 if a.display=='rgba' else 0, 'native_firmware': False}, indent=2) + '\n')
print('Built host baseline for', profile['name'], 'at', out / 'doom-host')
print('This is NOT flashable firmware.')
