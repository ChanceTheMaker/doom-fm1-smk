#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Capture current campaign frames and a WAV with the built host harness."""
from pathlib import Path
import os,subprocess
root=Path(__file__).resolve().parents[1];exe=root/'build/fm1/strip-no-wipe-mapped-small-static-heap24-abi32-campaign/doom-host'
for name,level,frames,mode,splash in [('splash',1,1,'idle','0'),('outpost',1,140,'idle',None),('reactor',3,200,'idle',None),('combat',2,110,'play',None),('sound-demo',1,420,'play',None)]:
 d=root/'build/screenshots'/name;d.mkdir(parents=True,exist_ok=True)
 env={**os.environ,'DOOM_ZONE_KIB':'256','DOOM_FRAME_LIMIT':str(frames),'DOOM_FIXED_TICS':'1','DOOM_CAMPAIGN_BOT':mode,'DOOM_AUDIO_REPORT':'audio.json'}
 if splash is not None:env['DOOM_SPLASH']=splash
 if name=='sound-demo':env['DOOM_AUDIO_OUTPUT']='effects.wav'
 with (d/'run.log').open('w') as f:subprocess.run([str(exe),'-iwad',str(root/'build/fixtures/campaign.wad'),'-nosound','-warp',str(level),'-skill','2'],cwd=d,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
 print(name,(d/'audio.json').read_text())

from PIL import Image
for name in ["splash","outpost","combat","reactor"]:
 d=root/"build/screenshots"/name
 candidates=list(d.glob("*.ppm"))
 if len(candidates)!=1:raise RuntimeError(f"Expected one frame in {d}: {candidates}")
 Image.open(candidates[0]).save(root/"site/screenshots"/(name+".png"))
