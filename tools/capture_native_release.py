#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Capture the native-art host harness, keeping browser thumbnails separate."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import struct
import zlib

def png_from_ppm(data):
    header=re.match(rb'P6\s+(\d+)\s+(\d+)\s+255\s',data)
    if not header or tuple(map(int,header.groups()))!=(240,240):
        raise ValueError('Expected 240x240 RGB PPM capture')
    pixels=data[header.end():]
    if len(pixels)!=240*240*3:raise ValueError('Incomplete PPM capture')
    def chunk(kind,body):
        return struct.pack('>I',len(body))+kind+body+struct.pack('>I',zlib.crc32(kind+body)&0xffffffff)
    rows=b''.join(b'\0'+pixels[y*720:(y+1)*720] for y in range(240))
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',240,240,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(rows))+chunk(b'IEND',b'')

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--exe',type=Path,required=True)
p.add_argument('--out',type=Path,default=ROOT/'build/native-release/screenshots')
a=p.parse_args();exe=a.exe.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
report={'source':'Native-art 240x240 host harness; not a photograph of hardware',
        'engine_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),
        'wad_sha256':hashlib.sha256((ROOT/'build/fixtures/native-art.wad').read_bytes()).hexdigest(),
        'files':{}}
for name,level,frames,mode,splash in [('splash',1,1,'idle',True),('outpost',1,140,'idle',False),('combat',2,110,'play',False),('reactor',3,200,'idle',False)]:
    folder=ROOT/'build/native-release'/name;folder.mkdir(parents=True,exist_ok=True)
    env={**os.environ,'DOOM_ZONE_KIB':'256','DOOM_FRAME_LIMIT':str(frames),'DOOM_FIXED_TICS':'1','DOOM_CAMPAIGN_BOT':mode}
    env.pop('DOOM_SPLASH',None)
    if splash:env['DOOM_SPLASH']='0'
    with (folder/'run.log').open('w') as log:
        subprocess.run([str(exe),'-iwad',str(ROOT/'build/fixtures/native-art.wad'),'-nosound','-warp',str(level),'-skill','2'],
                       cwd=folder,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    images=list(folder.glob('*.ppm'))
    if len(images)!=1:raise ValueError('Expected one captured frame: '+name)
    target=out/(name+'.png');target.write_bytes(png_from_ppm(images[0].read_bytes()))
    report['files'][target.name]={'level':level,'frames':frames,'mode':mode,'splash':splash,
                                'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
(out/'capture.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
