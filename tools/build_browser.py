#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Build the shared Doom engine for a browser Worker. No device access."""
import argparse,json,re,subprocess,hashlib
from pathlib import Path
from prepare_engine import prepare,ROOT,UPSTREAM
from static_wad import freeze
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--emcc',default='emcc');a=p.parse_args()
out=ROOT/'build/browser';out.mkdir(parents=True,exist_ok=True)
engine=prepare(out/'engine',campaign=True);common=ROOT/'src/common';native=ROOT/'src/native'
wad=ROOT/'build/fixtures/native-art.wad'
if not wad.exists():p.error('Run tools/build_campaign.py and tools/build_browser_campaign.py first')
art=json.loads(wad.with_suffix('.json').read_text())
freeze(engine,wad,campaign=True,expected_sha=art['sha256'])
video=engine/'i_video.c';text=video.read_text();start=text.index('void I_FinishUpdate (void)');end=text.index('\n}',start)+2
video.write_text(text[:start]+'void I_FinishUpdate(void) { DG_DrawFrame(); }'+text[end:])
# Embed the campaign with the vendored Freedoom enemy replacements.
asset=out/'assets.c';blob=wad.read_bytes()
asset.write_text('const unsigned char dp_wad_start[]={'+','.join(str(b) for b in blob)+'};\nconst unsigned int dp_wad_size='+str(len(blob))+';\n')
wfile=out/'w_file_browser.c';wfile.write_text((native/'w_file_flash.c').read_text().replace('dp_wad_start[],dp_wad_end[]','dp_wad_start[];\nextern const unsigned int dp_wad_size').replace('dp_wad_end-dp_wad_start','dp_wad_size'))
line=re.search(r'^SRC_DOOM\s*=\s*(.+)$',(UPSTREAM/'Makefile').read_text(),re.M)
sources=[engine/(name[:-2]+'.c') for name in line[1].split() if name!='doomgeneric_xlib.o']
replace={'i_system.c':native/'system.c','w_file_stdc.c':wfile,'doomgeneric.c':common/'doomgeneric_create.c','f_wipe.c':common/'wipe_disabled.c'}
sources=[replace.get(s.name,s) for s in sources]
sources += [common/(n+'.c') for n in ['lcd_frame','menu_view','wad_view','campaign','sfx','music','game_sound','native_hud']]+[ROOT/'src/browser/doom_browser.c',ROOT/'src/browser/browser_splash.c',asset]
dest=ROOT/'site/simulator/doom-engine.js'
exports=['browser_'+n for n in ['init','key','release','step','splash','frame','audio','stat']]
cmd=[a.emcc,'-O2','-std=gnu11','-Wno-incompatible-function-pointer-types','-Wno-int-conversion','-DCMAP256','-DDP_CAMPAIGN','-DDP_NATIVE_ART','-DNORMALUNIX','-DLINUX','-DDOOMGENERIC_RESX=320','-DDOOMGENERIC_RESY=200','-I'+str(engine),'-I'+str(common),'-I'+str(native),*map(str,sources),'-lm','--no-entry','-sMODULARIZE=1','-sEXPORT_ES6=1','-sENVIRONMENT=web,worker,node','-sEXPORTED_FUNCTIONS='+json.dumps(['_'+n for n in exports]),'-sEXPORTED_RUNTIME_METHODS='+json.dumps(['HEAPU8','HEAPF32']),'-sALLOW_MEMORY_GROWTH=1','-sINITIAL_MEMORY=16777216','-sSTACK_SIZE=1048576','-sFILESYSTEM=1','-sEXIT_RUNTIME=1','-o',str(dest)]
subprocess.run(cmd,check=True)
manifest={'engine':'Development preview / native LCD artwork, nine maps','artwork':art,'toolchain':subprocess.check_output([a.emcc,'--version'],text=True).splitlines()[0],'wad_sha256':hashlib.sha256(blob).hexdigest(),'files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in [dest,dest.with_suffix('.wasm')]}}
(dest.parent/'build.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
