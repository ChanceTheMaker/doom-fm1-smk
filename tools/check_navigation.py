#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Reproduce Test02's turn crash, compare fixed textures, and exercise longer play."""
import argparse, hashlib, json, os, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('fixed',type=Path);p.add_argument('reference',type=Path)
a=p.parse_args();fixed=a.fixed.resolve();reference=a.reference.resolve()
wad=ROOT/'build/fixtures/miniwad-room.wad'
assert hashlib.sha256(wad.read_bytes()).hexdigest()=='5382808534297f82d29873d9132410dcb20f314e01f58f1ec4c653f7f0ddf98d'
scenarios={
 'turn-right':[(1,1,174),(10000,0,174)],
 'turn-left':[(1,1,172),(10000,0,172)],
 'move-fire-use':[(1,1,173),(1,1,174),(1,1,163),(400,1,162),(450,0,162),(3000,0,174),(3000,1,172),(10000,0,173),(10000,0,172),(10000,0,163)],
 'strafe-back':[(1,1,160),(1,1,174),(2000,0,160),(2000,1,161),(4000,0,161),(4000,1,175),(6000,0,175),(10000,0,174)],
 'menu':[(i+d,v,27) for i in range(10,9000,200) for d,v in [(0,1),(1,0),(80,1),(81,0)]]}
results=[]
def run(exe,zone,name,events,frames,export=False):
 d=Path(tempfile.mkdtemp(prefix='navigation-'+name+'-',dir=fixed.parent))
 (d/'events.txt').write_text(''.join(f'{t} {v} {k}\n' for t,v,k in events))
 env=dict(os.environ,DOOM_ZONE_KIB=str(zone),DOOM_FRAME_LIMIT=str(frames),DOOM_FIXED_TICS='1',DOOM_INPUT_SCRIPT=str(d/'events.txt'),DOOM_MEMORY_REPORT='memory.json',DOOM_INPUT_REPORT='input.json')
 if export:env['DOOM_TEXTURE_REPORT']='textures.bin'
 with (d/'run.log').open('w') as f:
  result=subprocess.run([str(exe),'-iwad',str(wad),'-nosound','-warp','1','-skill','2'],cwd=d,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=60)
 return d,result.returncode
# Keep a failing old-path test: this is the hardware-reported allocation size.
d,code=run(reference,256,'old-crash',scenarios['turn-right'],2100)
assert code!=0 and 'failed on allocation of 16408 bytes' in (d/'run.log').read_text()
print('Reproduced Test02: turning fails on 16408-byte allocation.',flush=True)
for name,events in scenarios.items():
 paths=[]
 for exe,zone in [(reference,1024),(fixed,256)]:
  d,code=run(exe,zone,name,events,10500,export=True)
  assert code==0,(name,exe,(d/'run.log').read_text()[-1200:])
  mem=json.loads((d/'memory.json').read_text());inp=json.loads((d/'input.json').read_text())
  assert mem['frames']==10500 and mem['gamestate']==0
  assert inp['events_delivered']==len(events) and inp['controls_released'],inp
  assert 'failed 0' in (d/'run.log').read_text()
  paths.append(d)
  if exe==fixed:results.append(dict(scenario=name,directory=str(d),memory=mem,input=inp))
 for filename in ['textures.bin','frame.ppm']:
  assert (paths[0]/filename).read_bytes()==(paths[1]/filename).read_bytes(),(name,filename)
 print(name,': 10500 frames; all room composite columns and final image match reference.',flush=True)
(fixed.parent/'navigation-check.json').write_text(json.dumps(results,indent=2)+'\n')
print('PASS: crash reproduced; fixed 256 KiB play matches reference in all five scenarios.')
