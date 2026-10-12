#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Exercise physical-key menu navigation and render previews at LCD resolution."""
import argparse,json,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('executable',type=Path);a=p.parse_args();exe=a.executable.resolve()
# Key taps: 7/menu=escape, 2/up, 4/down, 8/select=enter, 3/right.
cases=[
 ('main',[27],'DOOM',0,'NEW GAME'),
 ('options',[27,175,13],'OPTIONS',0,'END GAME'),
 ('messages-off',[27,175,13,175,13],'OPTIONS',1,'MESSAGES OFF'),
 ('detail-low',[27,175,13,175,175,13],'OPTIONS',2,'DETAIL LOW'),
 ('screen-size',[27,175,13,175,175,175,174],'OPTIONS',3,'SCREEN SIZE 8'),
 ('difficulty',[27,13],'DIFFICULTY',2,'HURT ME PLENTY'),
 ('nightmare-prompt',[27,13,175,175,13],'CONFIRM',-1,'START NIGHTMARE?'),
 ('cancel-prompt',[27,13,175,175,13,27],'',-1,''),
 ('select-confirms',[27,13,175,175,13,13],'',-1,''),
 ('save-notice',[27,175,175,175,13],'NOTICE',-1,'Saves are not'),
 ('load-notice',[27,175,175,13],'NOTICE',-1,'Saves are not'),
 ('sound',[27,175,13,175,175,175,175,175,13],'SOUND',0,'SOUND FX 8')]
results=[]
for name,keys,title,selected,line in cases:
 d=Path(tempfile.mkdtemp(prefix='menu-'+name+'-',dir=exe.parent))
 events=[]
 for i,key in enumerate(keys):events.extend([(5+8*i,1,key),(6+8*i,0,key)])
 (d/'events.txt').write_text(''.join(f'{t} {down} {key}\n' for t,down,key in events))
 env=dict(os.environ,DOOM_ZONE_KIB='256',DOOM_FRAME_LIMIT=str(30+8*len(keys)),DOOM_FIXED_TICS='1',DOOM_INPUT_SCRIPT=str(d/'events.txt'),DOOM_MENU_REPORT='menu.txt',DOOM_MEMORY_REPORT='memory.json')
 with (d/'run.log').open('w') as f:
  subprocess.run([str(exe),'-iwad',str(ROOT/'build/fixtures/miniwad-room.wad'),'-nosound','-warp','1','-skill','2'],cwd=d,env=env,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=30)
 report=(d/'menu.txt').read_text().splitlines()
 assert report[0]==title and report[1]==str(selected),(name,report)
 if line:assert line in report[2:],(name,report)
 assert 'failed 0' in (d/'run.log').read_text()
 results.append(dict(name=name,directory=str(d),report=report));print('PASS',name,flush=True)
(exe.parent/'menu-check.json').write_text(json.dumps(results,indent=2)+'\n')
