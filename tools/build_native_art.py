#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Fit credited Freedoom monsters into the native app slot without changing maps.

Uses front-facing sprites with walk/attack/death animation. Browser keeps eight
directions. Unreferenced texture patches are removed; texture definitions stay.
"""
import hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def read(path):
    b=path.read_bytes();_,n,d=struct.unpack_from('<4sII',b)
    return [(name.rstrip(b'\0').decode(),b[o:o+s]) for o,s,name in
            (struct.unpack_from('<II8s',b,d+16*i) for i in range(n))]

def build():
    from static_wad import CAMPAIGN_SHA
    base=ROOT/'build/fixtures/campaign.wad';browser=ROOT/'build/fixtures/browser-campaign.wad'
    if hashlib.sha256(base.read_bytes()).hexdigest()!=CAMPAIGN_SHA:raise ValueError('Base mismatch')
    art=json.loads(browser.with_suffix('.json').read_text())
    if hashlib.sha256(browser.read_bytes()).hexdigest()!=art['sha256']:raise ValueError('Browser artwork mismatch')
    rows=read(base);lumps=dict(rows);newart=dict(read(browser))
    # Keep every texture, remapping PNAMES to only the referenced patches.
    tex=bytearray(lumps['TEXTURE1']);used=set();refs=[]
    for i in range(struct.unpack_from('<I',tex)[0]):
        off=struct.unpack_from('<I',tex,4+4*i)[0]
        for j in range(struct.unpack_from('<H',tex,off+20)[0]):
            pos=off+22+10*j+4;index=struct.unpack_from('<H',tex,pos)[0];used.add(index);refs.append((pos,index))
    used=sorted(used);remap={v:i for i,v in enumerate(used)}
    for pos,index in refs:struct.pack_into('<H',tex,pos,remap[index])
    pn=lumps['PNAMES'];names=[pn[4+i*8:12+i*8] for i in used]
    keep={x.rstrip(b'\0').decode() for x in names}
    replacements={'TEXTURE1':bytes(tex),'PNAMES':struct.pack('<I',len(names))+b''.join(names)}
    for name in ['STFST00','STFST20','STFST40','STFDEAD0']:replacements[name]=newart[name]
    enemies=[]
    for family,last in [('POSS','L'),('TROO','M')]:
        for code in range(ord('A'),ord(last)+1):
            frame=chr(code);front=family+frame+'1';death=family+frame+'0'
            # Alternating A/B gait saves flash while retaining clear walking.
            source=family+({'C':'A','D':'B'}.get(frame,frame))+'1'
            candidates=[name for name in newart if name.startswith(source)]
            if not candidates: candidates=[name for name in newart if name.startswith(front)]
            if death in newart:blob=newart[death]
            elif candidates:blob=newart[candidates[0]]
            else:raise ValueError('Missing enemy frame '+front)
            enemies.append((family+frame+'0',blob))
    outrows=[];patches=False
    for name,blob in rows:
        if name=='P_START':patches=True
        if name=='P_END':patches=False
        if patches and not name.endswith(('_START','_END')) and name not in keep:continue
        if name.startswith(('POSS','TROO')):continue
        if name=='S_END':outrows.extend(enemies)
        outrows.append((name,replacements.get(name,blob)))
    out=bytearray(12);seen={};directory=[]
    for name,blob in outrows:
        if blob not in seen:out.extend(b'\0'*(-len(out)%4));seen[blob]=len(out);out.extend(blob)
        directory.append((seen[blob],len(blob),name.encode().ljust(8,b'\0')))
    out.extend(b'\0'*(-len(out)%4));off=len(out)
    for entry in directory:out.extend(struct.pack('<II8s',*entry))
    struct.pack_into('<4sII',out,0,b'IWAD',len(outrows),off)
    path=ROOT/'build/fixtures/native-art.wad';path.write_bytes(out)
    report={'sha256':hashlib.sha256(out).hexdigest(),'bytes':len(out),'artwork':'Freedoom v0.13.0, front-facing native animation','source_art_sha256':art['sha256'],'lumps':len(outrows)}
    path.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
    return path
if __name__=='__main__':build()
