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
p.add_argument('--campaign',action='store_true')
p.add_argument('--small-room', action='store_true')
p.add_argument('--static-wad', action='store_true')
p.add_argument('--bounded-heap', action='store_true')
p.add_argument('--reference-textures', action='store_true', help='Keep vanilla runtime composites for comparison')
p.add_argument('--abi32', action='store_true', help='32-bit host ABI for native memory-budget checks')
a = p.parse_args()
if a.campaign and not (a.small_room and a.static_wad):p.error('--campaign needs --small-room --static-wad')
if a.reference_textures and not a.static_wad:p.error('--reference-textures needs --static-wad')
if a.static_wad and not (a.small_room and a.mapped_wad): p.error('--static-wad needs --small-room --mapped-wad')
profile = json.loads((ROOT / 'targets' / (a.board + '.json')).read_text())
engine = ROOT / 'third_party/doomgeneric/doomgeneric'
if not (engine / 'Makefile').exists():
    p.error('Run git submodule update --init first.')
# Use exactly the upstream portable source set; replace only the X11 frontend.
line = re.search(r'^SRC_DOOM\s*=\s*(.+)$', (engine / 'Makefile').read_text(), re.M)
if not line:
    p.error('Pinned upstream source list missing.')
sources = [engine / (name[:-2] + '.c') for name in line[1].split() if name != 'doomgeneric_xlib.o']

out = ROOT / 'build' / a.board / (a.display + ('-no-wipe' if a.no_wipe else '') + ('-mapped' if a.mapped_wad else '') + ('-small' if a.small_room else '') + ('-static' if a.static_wad else '') + ('-heap24' if a.bounded_heap else '') + ('-abi32' if a.abi32 else '') + ('-reference' if a.reference_textures else '')+('-campaign' if a.campaign else ''))
out.mkdir(parents=True, exist_ok=True)
if a.small_room:
    from prepare_engine import prepare
    engine=prepare(out/'engine',campaign=a.campaign)
    sources=[engine/s.name for s in sources]
if a.static_wad:
    from static_wad import freeze
    freeze(engine,ROOT/'build/fixtures'/('campaign.wad' if a.campaign else 'miniwad-room.wad'),static_textures=not a.reference_textures,campaign=a.campaign)
if a.static_wad:
    with (engine/'r_data.c').open('a') as f:
        f.write('\n'+(ROOT/'src/host/texture_probe.inc').read_text())
# Keep upstream pinned and clean; append introspection only in a generated copy.
zone=out/'z_zone_probe.c'
zone.write_text((engine/'z_zone.c').read_text()+'\n'+(ROOT/'src/host/zone_probe.inc').read_text())
sources=[zone if s.name=='z_zone.c' else s for s in sources]
flags=['-I'+str(ROOT/'src/host'), '-I'+str(ROOT/'src/common'),
       '-Wl,--wrap=I_ZoneBase', '-Wl,--wrap=Z_Malloc', '-fstack-usage']
if a.display=='strip':
    sources=[ROOT/'src/common/doomgeneric_create.c' if s.name=='doomgeneric.c' else s for s in sources]
    sources.append(ROOT/'src/common/lcd_frame.c')
    flags+=['-DDP_TEXTURE_PROBE'] if a.static_wad else []
    if a.small_room:
        sources.append(ROOT/'src/common/menu_view.c');flags+=['-DDP_READABLE_MENU']
    flags+=['-DCMAP256','-DDP_STRIP','-Wl,--wrap=I_FinishUpdate']
if a.mapped_wad:
    sources=[ROOT/'src/host/w_file_mmap.c' if s.name=='w_file_stdc.c' else s for s in sources]
    sources.append(ROOT/'src/common/wad_view.c')
if a.no_wipe:
    sources=[ROOT/'src/common/wipe_disabled.c' if s.name=='f_wipe.c' else s for s in sources]
if a.campaign:
    sources.extend([ROOT/'src/common/campaign.c',ROOT/'src/host/campaign_bot.c',ROOT/'src/common/sfx.c',ROOT/'src/common/music.c',ROOT/'src/common/game_sound.c',ROOT/'src/common/splash.c',ROOT/'src/host/audio_capture.c']);flags+=['-DDP_CAMPAIGN']
sources += [ROOT/'src/host/doomgeneric_host.c',ROOT/'src/host/memory_probe.c',ROOT/'src/host/input_smoke.c']
abi=['-m32'] if a.abi32 else []
command = [a.cc, *abi, '-std=c11', '-O2', '-D_DEFAULT_SOURCE', '-D_FILE_OFFSET_BITS=64', '-DNORMALUNIX', '-DLINUX',
           '-DDOOMGENERIC_RESX=320', '-DDOOMGENERIC_RESY=200', '-I' + str(engine),
           *flags, *map(str, sources), '-lm', '-o', str(out / 'doom-host')]
if a.bounded_heap:
    from concurrent.futures import ThreadPoolExecutor
    renames=['-D'+n+'=dp_'+n for n in ['malloc','free','calloc','realloc','strdup']]
    base=command[:command.index(str(sources[0]))]
    def compile_one(pair):
        i,src=pair;obj=out/(str(i)+'-'+src.stem+'.o')
        bounded=src.parent==engine or src==zone
        subprocess.run([*base,*(renames if bounded else []),'-c',str(src),'-o',str(obj)],check=True,cwd=out)
        return obj
    with ThreadPoolExecutor(4) as pool: objects=list(pool.map(compile_one,enumerate(sources)))
    heap=out/'bounded-heap.o'
    subprocess.run([a.cc,*abi,'-O2','-fno-builtin','-DDP_HEAP_ONLY',*renames,'-c',str(ROOT/'src/native/libc_support.c'),'-o',str(heap)],check=True)
    subprocess.run([a.cc,*abi,*flags,*map(str,objects),str(heap),str(ROOT/'src/host/native_heap_probe.c'),'-lm','-o',str(out/'doom-host')],check=True)
else:
    subprocess.run(command, check=True, cwd=out)
(out / 'target.json').write_text(json.dumps({'build_kind': 'host-only', 'profile': profile,
    'reference_textures':a.reference_textures,'abi32': a.abi32, 'bounded_heap': a.bounded_heap, 'static_wad': a.static_wad, 'small_room': a.small_room, 'mapped_wad': a.mapped_wad, 'display': a.display, 'no_wipe': a.no_wipe, 'output_framebuffer_bytes': 320 * 200 * 4 if a.display=='rgba' else 0, 'native_firmware': False}, indent=2) + '\n')
print('Built host baseline for', profile['name'], 'at', out / 'doom-host')
print('This is NOT flashable firmware.')
