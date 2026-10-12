#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Build browser-only campaign with Freedoom 0.13 enemy sprites (requires Pillow)."""
import hashlib,json,struct,re
from pathlib import Path
from PIL import Image
from static_wad import CAMPAIGN_SHA
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets/freedoom'

def patch(p,palette,offsets):
    data=p.read_bytes();pos=8;offset=None
    while pos<len(data):
        size=struct.unpack_from('>I',data,pos)[0]
        if data[pos+4:pos+8]==b'grAb':offset=struct.unpack_from('>ii',data,pos+8)
        pos+=size+12
    if offset is None:
        name=p.stem.upper()
        if name not in offsets and p.parent.name!='graphics':raise ValueError('Missing sprite origin: '+name)
        offset=offsets.get(name,(0,0))
    im=Image.open(p).convert('RGBA');w,h=im.size
    if h>=255:raise ValueError('Tall patch unsupported')
    colors={};pixels=[]
    for r,g,b,a in im.getdata():
        rgb=(r,g,b)
        if a and rgb not in colors:
            colors[rgb]=min(range(256),key=lambda i:sum((palette[i*3+j]-rgb[j])**2 for j in range(3)))
        pixels.append(colors[rgb] if a else -1)
    out=bytearray(struct.pack('<hhhh',w,h,*offset)+bytes(w*4))
    for x in range(w):
        struct.pack_into('<I',out,8+4*x,len(out));y=0
        while y<h:
            if pixels[y*w+x]<0:y+=1;continue
            top=y;column=[]
            while y<h and pixels[y*w+x]>=0:column.append(pixels[y*w+x]);y+=1
            out.extend(bytes([top,len(column),0,*column,0]))
        out.append(255)
    return bytes(out)

def build():
    manifest=json.loads((ASSETS/'manifest.json').read_text())
    for name,digest in manifest['files'].items():
        if hashlib.sha256((ASSETS/name).read_bytes()).hexdigest()!=digest:raise ValueError('Changed Freedoom source: '+name)
    source=ROOT/'build/fixtures/campaign.wad';data=source.read_bytes()
    if hashlib.sha256(data).hexdigest()!=CAMPAIGN_SHA:raise ValueError('Unexpected base campaign')
    magic,count,directory=struct.unpack_from('<4sII',data)
    entries=[]
    for i in range(count):
        off,size,name=struct.unpack_from('<II8s',data,directory+16*i)
        entries.append((name.rstrip(b'\0').decode(),data[off:off+size]))
    palette=dict(entries)['PLAYPAL'][:768]
    offsets={name:(int(x),int(y)) for name,x,y in re.findall(r'^([A-Z0-9]+)\s+(-?\d+)\s+(-?\d+)\s*$',(ASSETS/'buildcfg.txt').read_text(),re.M)}
    sprites=[(p.stem.upper(),patch(p,palette,offsets)) for p in sorted((ASSETS/'sprites').glob('*.png'))]
    graphics={p.stem.upper():patch(p,palette,offsets) for p in sorted((ASSETS/'graphics').glob('*.png'))}
    out=bytearray(12);rows=[];seen={};inside=False
    def add(name,blob):
        if blob not in seen:
            out.extend(b'\0'*(-len(out)%4));seen[blob]=len(out);out.extend(blob)
        rows.append((seen[blob],len(blob),name.encode().ljust(8,b'\0')))
    for name,blob in entries:
        if name=='S_START':inside=True
        if inside and name.startswith(('POSS','TROO')):continue
        if name=='S_END':
            for sprite,body in sprites:add(sprite,body)
            inside=False
        add(name,graphics.get(name,blob))
    out.extend(b'\0'*(-len(out)%4));directory=len(out)
    for row in rows:out.extend(struct.pack('<II8s',*row))
    struct.pack_into('<4sII',out,0,magic,len(rows),directory)
    path=ROOT/'build/fixtures/browser-campaign.wad';path.write_bytes(out)
    report={'sha256':hashlib.sha256(out).hexdigest(),'bytes':len(out),'base_sha256':CAMPAIGN_SHA,'artwork':'Freedoom v0.13.0','sprite_lumps':len(sprites),'hud_lumps':sum(name in graphics for name,_ in entries),'source_tree':manifest['tree']}
    path.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return path
if __name__=='__main__':build()
