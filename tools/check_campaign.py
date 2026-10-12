#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Play the campaign through real input events with the native 256/24 KiB limits."""
import argparse,json,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('executable',type=Path);p.add_argument('--wad',type=Path,default=ROOT/'build/fixtures/campaign.wad');a=p.parse_args();exe=a.executable.resolve()
metadata=json.loads((ROOT/'build/fixtures/campaign.json').read_text())['levels']
count=len(metadata);kills=sum(len(m['enemies']) for m in metadata)
score=sum(200 if e[2]==3001 else 100 for m in metadata for e in m['enemies'])
results=[]
for name,skill,detail,frames,mode,level in [
 ('campaign',2,0,24000,'play',1),('low-detail',2,1,24000,'play',1),
 ('hard',4,0,24000,'play',1),('death-retry',2,0,2000,'idle',1),
 *[('room'+str(n),2,0,50,'idle',n) for n in range(1,count+1)]]:
 d=Path(tempfile.mkdtemp(prefix=name+'-',dir=exe.parent))
 # DoomGeneric disables config loading; low detail is selected via the normal F5 key.
 if detail:os.environ['DOOM_BOT_LOW_DETAIL']='1'
 else:os.environ.pop('DOOM_BOT_LOW_DETAIL',None)
 env=dict(os.environ,DOOM_ZONE_KIB='256',DOOM_FIXED_TICS='1',DOOM_FRAME_LIMIT=str(frames),DOOM_CAMPAIGN_BOT=mode,DOOM_CAMPAIGN_REPORT='combat.json',DOOM_MEMORY_REPORT='memory.json')
 with (d/'run.log').open('w') as f:
  subprocess.run([str(exe),'-iwad',str(a.wad.resolve()),'-nosound','-warp',str(level),'-skill',str(skill)],env=env,cwd=d,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=180)
 stats=json.loads((d/'combat.json').read_text());memory=json.loads((d/'memory.json').read_text())
 assert memory['zone_peak_allocated_bytes']<=262144
 assert stats['detail']==detail and stats['skill']==skill-1,stats
 assert 'failed 0' in (d/'run.log').read_text()
 if mode=='play':
  # Multiple campaigns prove the last map returns to MAP01, with no stop at
  # the commercial game's MAP06 story finale. Loops permit monster infighting;
  # only player kills award points, so the exact maximum is not mandatory.
  assert stats['maps']==(1<<count)-1 and stats['completions']>=count*2,(name,stats)
  assert stats['kills']>=kills*2 and score*4//5<=stats['peak_score']<=score,(name,stats)
 elif name=='death-retry':assert stats['deaths']>=1 and stats['health']>0 and stats['score']==0,stats
 else:assert stats['health']>0 and stats['shells']==40,stats
 results.append(dict(case=name,stats=stats,memory=memory,directory=str(d)));print('PASS',name,stats,flush=True)
(exe.parent/'campaign-check.json').write_text(json.dumps(results,indent=2)+'\n')
