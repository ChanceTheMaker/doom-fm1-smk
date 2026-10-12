#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Run bounded host-only Miniwad checks and record memory/artifact results."""
import argparse,hashlib,json,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('executable',type=Path)
p.add_argument('--wad',choices=['miniwad','miniwad-map01','miniwad-room'],default='miniwad')
p.add_argument('--zones',nargs='+',type=int,default=[16384,512,384,256])
a=p.parse_args();exe=a.executable.resolve()
if any(kib<64 or kib>65536 for kib in a.zones):p.error('Zones must be 64..65536 KiB.')
wad=ROOT/'build/fixtures'/(a.wad+'.wad')
if not wad.exists():p.error('Run python3 tools/fetch_test_wad.py first.')
expected={'miniwad':'daed5e9dc341a9ff4b9c6901cb8467a630bd31b87f3ecb58a93a8b2bc186fbfb','miniwad-room':'5382808534297f82d29873d9132410dcb20f314e01f58f1ec4c653f7f0ddf98d','miniwad-map01':'1c260ea99e45dafbc81384383e687242d86aeaf534d0c7738b7b3d3da3f9965a'}[a.wad]
if hashlib.sha256(wad.read_bytes()).hexdigest()!=expected:p.error('Fixture hash mismatch.')
results=[]
for kib in a.zones:
    run=Path(tempfile.mkdtemp(prefix=a.wad+'-zone-'+str(kib)+'-',dir=exe.parent))
    env=dict(os.environ,DOOM_ZONE_KIB=str(kib),DOOM_FRAME_LIMIT='120',DOOM_FRAME_OUTPUT='frame.ppm',DOOM_MEMORY_REPORT='memory.json',DOOM_FIXED_TICS='1',DOOM_INPUT_SMOKE='0')
    with (run/'run.log').open('w') as log:
        try:result=subprocess.run([str(exe),'-iwad',str(wad),'-nosound','-warp','1'],cwd=run,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=30);code=result.returncode
        except subprocess.TimeoutExpired:code='timeout'
    record={'zone_kib':kib,'exit_code':code,'directory':str(run)}
    if code==0:
        record.update(json.loads((run/'memory.json').read_text()))
        frame=(run/'frame.ppm').read_bytes();record['frame_sha256']=hashlib.sha256(frame).hexdigest()
        assert record['gamestate']==0 and record['frames']==120,'Not in a playing level'
    else:
        record['failure_tail']=(run/'run.log').read_text(errors='replace')[-500:]
    results.append(record);print(kib,code,record.get('zone_peak_nonpurgeable_bytes','failed'))
(exe.parent/(a.wad+'-measurements.json')).write_text(json.dumps(results,indent=2)+'\n')
# A low-memory failure is an experiment result, but the baseline must run.
if not results or results[0]['exit_code']!=0:raise SystemExit('Baseline run failed; see run.log')
