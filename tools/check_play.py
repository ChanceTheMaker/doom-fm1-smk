#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Prove movement, turning, firing and release on the host with a bounded zone."""
import argparse, hashlib, json, os, subprocess, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('executable',type=Path)
p.add_argument('--zone',type=int,default=384,help='Trimmed-room zone size in KiB (default: 384)')
a=p.parse_args();exe=a.executable.resolve()
if not 64<=a.zone<=65536:p.error('Zone must be 64..65536 KiB.')
fixtures=ROOT/'build/fixtures'
hashes={'miniwad':'daed5e9dc341a9ff4b9c6901cb8467a630bd31b87f3ecb58a93a8b2bc186fbfb',
        'miniwad-room':'5382808534297f82d29873d9132410dcb20f314e01f58f1ec4c653f7f0ddf98d'}
results=[]
for name,zone,play in [('miniwad',16384,True),('miniwad-room',a.zone,False),
                       ('miniwad-room',a.zone,True),('miniwad-room',a.zone,True)]:
    wad=fixtures/(name+'.wad')
    if hashlib.sha256(wad.read_bytes()).hexdigest()!=hashes[name]:
        raise SystemExit('Fixture hash mismatch: '+name)
    run=Path(tempfile.mkdtemp(prefix='play-check-',dir=exe.parent))
    env=dict(os.environ,DOOM_ZONE_KIB=str(zone),DOOM_FRAME_LIMIT='120',
             DOOM_FIXED_TICS='1',DOOM_INPUT_SMOKE='1' if play else '0',
             DOOM_FRAME_OUTPUT='frame.ppm',DOOM_MEMORY_REPORT='memory.json',DOOM_INPUT_REPORT='input.json')
    with (run/'run.log').open('w') as log:
        subprocess.run([str(exe),'-iwad',str(wad),'-nosound','-warp','1'],
                       cwd=run,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=30,check=True)
    result={'wad':name,'zone_kib':zone,'play':play,'directory':str(run),
            'frame_sha256':hashlib.sha256((run/'frame.ppm').read_bytes()).hexdigest(),
            'memory':json.loads((run/'memory.json').read_text())}
    assert result['memory']['gamestate']==0 and result['memory']['frames']==120
    if play:
        report=json.loads((run/'input.json').read_text());result['input']=report
        assert report['events_delivered']==6 and report['ticks_elapsed']>=100,report
        assert all(report[k] for k in ('moved','turned','fired','controls_released')),report
    results.append(result)
    print(name,zone,'play' if play else 'idle',result['frame_sha256'])
# Trimmed assets must produce the same gameplay image; repeated runs must agree.
assert results[0]['frame_sha256']==results[2]['frame_sha256']==results[3]['frame_sha256']
assert results[1]['frame_sha256']!=results[2]['frame_sha256'],'Input did not change the rendered frame'
(exe.parent/'play-check.json').write_text(json.dumps(results,indent=2)+'\n')
print('PASS: moved, turned, fired, released; trimmed image matches original; repeatable.')
