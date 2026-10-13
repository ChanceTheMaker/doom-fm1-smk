#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Pack the shared LCD artwork within the native application slot.

Prune unreachable textures and retain their switch/animation dependencies.
Deduplicate patch columns; scale weapons and HUD for the 240-pixel display.
Append the separately credited classic logo. Maps remain byte-identical.
"""
import hashlib,json,struct
from native_art_pack import texture_subset,compact_patch,scale_patch
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
    # Keep only reachable textures and switch/animation partners. This frees
    # flash and texture-table RAM for the actual weapon and status-bar art.
    tex=bytearray(texture_subset(rows,ROOT/'third_party/doomgeneric/doomgeneric'));used=set();refs=[]
    for i in range(struct.unpack_from('<I',tex)[0]):
        off=struct.unpack_from('<I',tex,4+4*i)[0]
        for j in range(struct.unpack_from('<H',tex,off+20)[0]):
            pos=off+22+10*j+4;index=struct.unpack_from('<H',tex,pos)[0];used.add(index);refs.append((pos,index))
    used=sorted(used);remap={v:i for i,v in enumerate(used)}
    for pos,index in refs:struct.pack_into('<H',tex,pos,remap[index])
    pn=lumps['PNAMES'];names=[pn[4+i*8:12+i*8] for i in used]
    keep={x.rstrip(b'\0').decode() for x in names}
    replacements={'TEXTURE1':bytes(tex),'PNAMES':struct.pack('<I',len(names))+b''.join(names)}
    faces={'STFDEAD0'}
    for tier in (0,2,4):
        faces.update('STFST%d%d'%(tier,i) for i in range(3))
        faces.add('STFOUCH%d'%tier)
    for name in newart:
        if name in faces or name.startswith(('STTNUM','STYSNUM','STGNUM','STKEYS')) or name in ('STBAR','STARMS','STTPRCNT'):
            replacements[name]=scale_patch(newart[name],3,4,15,16)
    for name in lumps:
        if name.startswith(('SHTG','SHTF','PISG','PISF','PUNG')):
            replacements[name]=scale_patch(newart['SHTGD0' if name=='SHTGE0' else name],1,2,1,2)
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
            enemies.append((family+frame+'0',compact_patch(blob)))
    # Overkill damage enters the engine's XDIE states even with the shotgun.
    # Keep every referenced frame. Reuse the existing five-stage death art so
    # the immutable WAD deduplicator adds directory entries, not 31 KiB of art.
    packed_enemies=dict(enemies)
    for family,first,sequence in [('POSS','M','HHIIJJKKL'),('TROO','N','IIJJKLLM')]:
        for i,source in enumerate(sequence):
            enemies.append((family+chr(ord(first)+i)+'0',packed_enemies[family+source+'0']))
    outrows=[];patches=False
    for name,blob in rows:
        if name=='P_START':patches=True
        if name=='P_END':patches=False
        if patches and not name.endswith(('_START','_END')) and name not in keep:continue
        if name.startswith(('POSS','TROO')):continue
        if name=='S_END':outrows.extend(enemies)
        outrows.append((name,replacements.get(name,blob)))
    from build_logo import build_logo
    outrows.append(("DPLOGO",build_logo()))
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
