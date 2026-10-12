#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Create a MAP01-only, aligned, deduplicated Miniwad test image (local build output)."""
import argparse,hashlib,json,re,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--trim-textures',action='store_true')
args=parser.parse_args()
src=ROOT/'build/fixtures/miniwad.wad';data=src.read_bytes()
if hashlib.sha256(data).hexdigest()!='daed5e9dc341a9ff4b9c6901cb8467a630bd31b87f3ecb58a93a8b2bc186fbfb':raise SystemExit('Only the pinned Miniwad fixture is accepted')
magic,count,directory=struct.unpack_from('<4sII',data)
entries=[];skip=0;removed=0
for i in range(count):
 off,size,name=struct.unpack_from('<II8s',data,directory+16*i)
 text=name.rstrip(b'\0').decode('ascii')
 if re.fullmatch(r'MAP\d\d',text) and text!='MAP01':skip=11
 if skip:skip-=1;removed+=1;continue
 entries.append((name,data[off:off+size]))
texture_counts=None
if args.trim_textures:
    lumps={name.rstrip(b'\0').decode('ascii'):blob for name,blob in entries}
    needed={'SKY1','SKY2','SKY3','SKY4'}
    sides=lumps['SIDEDEFS']
    for i in range(0,len(sides),30):
        for o in (4,12,20):needed.add(sides[i+o:i+o+8].rstrip(b'\0').decode('ascii'))
    engine=ROOT/'third_party/doomgeneric/doomgeneric'
    switches=re.findall(r'\{\s*"(SW[12][A-Z0-9]+)"\s*,\s*"(SW[12][A-Z0-9]+)"',(engine/'p_switch.c').read_text())
    assert len(switches)==40,'Review changed upstream switch list'
    for pair in switches:needed.update(pair)
    textures=lumps['TEXTURE1'];n=struct.unpack_from('<I',textures)[0]
    records=[]
    for i in range(n):
        off=struct.unpack_from('<I',textures,4+4*i)[0]
        count=struct.unpack_from('<H',textures,off+20)[0]
        record=textures[off:off+22+count*10]
        records.append((record[:8].rstrip(b'\0').decode('ascii'),record))
    names=[name for name,_ in records];needed.add(names[0])
    animations=re.findall(r'\{true,\s*"([A-Z0-9]+)"\s*,\s*"([A-Z0-9]+)"',(engine/'p_spec.c').read_text())
    for end,start in animations:
        if start in names and end in names:needed.update(names[names.index(start):names.index(end)+1])
    selected=[(name,blob) for name,blob in records if name in needed]
    assert needed-{'-','SKY4'}<=set(names),'Required texture missing'
    new=bytearray(4+4*len(selected));struct.pack_into('<I',new,0,len(selected))
    for i,(_,blob) in enumerate(selected):
        struct.pack_into('<I',new,4+4*i,len(new));new.extend(blob)
    entries=[(name,bytes(new) if name.rstrip(b'\0')==b'TEXTURE1' else blob) for name,blob in entries]
    texture_counts={'original':n,'retained':len(selected)}
# MAP headers plus the following ten vanilla map lumps. Preserve every non-map lump.
out=bytearray(12);positions={};result=[]
for name,blob in entries:
 if blob not in positions:
  out.extend(b'\0'*(-len(out)%4));positions[blob]=len(out);out.extend(blob)
 result.append((positions[blob],len(blob),name))
out.extend(b'\0'*(-len(out)%4));directory=len(out)
for entry in result:out.extend(struct.pack('<II8s',*entry))
struct.pack_into('<4sII',out,0,magic,len(result),directory)
for (name,blob),(off,size,storedname) in zip(entries,result):
 assert name==storedname and bytes(out[off:off+size])==blob and off%4==0
path=ROOT/'build/fixtures'/('miniwad-room.wad' if args.trim_textures else 'miniwad-map01.wad');path.write_bytes(out)
report={'source_sha256':hashlib.sha256(data).hexdigest(),'sha256':hashlib.sha256(out).hexdigest(),'source_bytes':len(data),'bytes':len(out),'kept_lumps':len(result),'removed_map_lumps':removed,'alignment':4,'textures':texture_counts}
path.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
