#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Generate original small combat maps and pixel sprites over the pinned Miniwad.
Run under Linux/WSL with zdbsp. Does not access any device.
"""
import hashlib,json,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/fixtures';OUT.mkdir(exist_ok=True)
def readwad(b):
 magic,n,d=struct.unpack_from('<4sII',b);assert magic in (b'IWAD',b'PWAD')
 return [(name.rstrip(b'\0').decode(),b[o:o+s]) for o,s,name in (struct.unpack_from('<II8s',b,d+i*16) for i in range(n))]
def wad(entries,magic=b'IWAD'):
 out=bytearray(12);seen={};directory=[]
 for name,b in entries:
  if b not in seen:out.extend(b'\0'*(-len(out)%4));seen[b]=len(out);out.extend(b)
  directory.append((seen[b],len(b),name.encode().ljust(8,b'\0')))
 out.extend(b'\0'*(-len(out)%4));off=len(out)
 for e in directory:out.extend(struct.pack('<II8s',*e))
 struct.pack_into('<4sII',out,0,magic,len(entries),off);return bytes(out)
source=(OUT/'miniwad-room.wad').read_bytes()
assert hashlib.sha256(source).hexdigest()=='5382808534297f82d29873d9132410dcb20f314e01f58f1ec4c653f7f0ddf98d'
entries=readwad(source);lumps=dict(entries);pal=lumps['PLAYPAL'][:768]
def color(rgb):return min(range(256),key=lambda i:sum((pal[i*3+j]-rgb[j])**2 for j in range(3)))
colors={k:color(v) for k,v in dict(black=(12,14,18),dark=(34,42,50),metal=(98,110,120),light=(186,200,204),white=(248,245,215),red=(230,30,20),orange=(236,126,22),yellow=(255,218,72),green=(60,108,50),armor=(105,144,69),skin=(144,87,46),brown=(72,39,25)).items()}
def canvas(w,h):return [[-1]*w for _ in range(h)]
def rect(a,x,y,w,h,c):
 for yy in range(max(y,0),min(y+h,len(a))):
  for xx in range(max(x,0),min(x+w,len(a[0]))):a[yy][xx]=colors[c]
def patch(a,left,top):
 h=len(a);w=len(a[0]);out=bytearray(struct.pack('<hhhh',w,h,left,top)+bytes(4*w));columns={}
 for x in range(w):
  column=bytearray();y=0
  while y<h:
   if a[y][x]<0:y+=1;continue
   start=y
   while y<h and a[y][x]>=0:y+=1
   column.extend(bytes([start,y-start,0]));column.extend(a[t][x] for t in range(start,y));column.append(0)
  column.append(255);key=bytes(column)
  if key not in columns:columns[key]=len(out);out.extend(key)
  struct.pack_into('<I',out,8+x*4,columns[key])
 return bytes(out)

def monster(kind,frame):
 w,h=(32,48) if kind=='POSS' else (40,56);a=canvas(w,h);cx=w//2
 death=frame>='H' if kind=='POSS' else frame>='I'
 if death:
  rect(a,2,h-12,w-4,10,'dark');rect(a,5,h-13,w-12,7,'green' if kind=='POSS' else 'skin');rect(a,w-12,h-14,8,7,'metal' if kind=='POSS' else 'orange')
  rect(a,4,h-4,w-8,3,'black');return patch(a,cx,h)
 shift=1 if frame in 'BD' else -1
 rect(a,cx-10,h-20,8,18+shift,'dark');rect(a,cx+2,h-20,8,18-shift,'dark')
 rect(a,cx-12,h-4+shift,11,4,'black');rect(a,cx+1,h-4-shift,11,4,'black')
 body='green' if kind=='POSS' else 'skin';edge='armor' if kind=='POSS' else 'orange'
 rect(a,cx-12,17,w-8,h-31,body);rect(a,cx-10,18,7,h-33,edge);rect(a,cx+7,18,4,h-31,'brown')
 rect(a,cx-15,19,6,20,body);rect(a,cx+10,19,6,20,body)
 rect(a,cx-8,3,16,16,'dark');rect(a,cx-6,4,12,12,'metal' if kind=='POSS' else 'skin')
 rect(a,cx-5,9,10,3,'black');rect(a,cx-4,9,3,2,'red');rect(a,cx+2,9,3,2,'red');rect(a,cx-3,14,6,2,'white')
 if kind=='TROO':
  rect(a,cx-10,0,4,10,'white');rect(a,cx+6,0,4,10,'white')
  rect(a,cx-15,35,5,5,'orange');rect(a,cx+11,35,5,5,'orange')
 else:
  rect(a,cx-11,27,24,5,'black');rect(a,cx-8,27,22,2,'metal');rect(a,cx+8,25,4,8,'dark')
 if frame in ('EF' if kind=='POSS' else 'EFG'):
  rect(a,cx+11,22,5,8,'yellow');rect(a,cx+9,25,9,3,'white')
 return patch(a,cx,h)
def gun(frame,flash=False):
 a=canvas(96,100 if flash else 72);h=len(a)
 if flash:
  rect(a,45,0,6,30,'yellow');rect(a,31,11,34,6,'orange');rect(a,39,6,18,22,'yellow');rect(a,44,12,8,12,'white')
  return patch(a,-112,-68)
 shift=4 if frame in 'BC' else 0
 rect(a,24,54,48,18,'brown');rect(a,17,62,18,10,'skin');rect(a,63,62,18,10,'skin')
 rect(a,31,24+shift,34,48,'black');rect(a,35,26+shift,26,43,'dark');rect(a,37,29+shift,6,35,'metal');rect(a,54,29+shift,4,35,'light')
 rect(a,39,4+shift,18,41,'black');rect(a,42,6+shift,12,35,'metal');rect(a,43,8+shift,3,30,'light')
 rect(a,40,1+shift,16,7,'dark');rect(a,44,2+shift,8,3,'black');rect(a,46,0+shift,4,2,'red')
 rect(a,27,42+shift,42,12,'brown');rect(a,28,43+shift,40,2,'orange')
 for x in range(30,68,6):rect(a,x,46+shift,2,7,'dark')
 rect(a,43,59,10,6,'black');return patch(a,-112,-96)
replaced=[];new=[];skip=0
for name,b in entries:
 if name=='MAP01':skip=11
 if skip:skip-=1;continue
 if name.startswith(('POSS','TROO')) and len(name)>=6:b=monster(name[:4],name[4]);replaced.append(name)
 elif name.startswith('SHTG') and len(name)>=6:b=gun(name[4]);replaced.append(name)
 elif name.startswith('SHTF') and len(name)>=6:b=gun(name[4],True);replaced.append(name)
 new.append((name,b))
# Original panel wall art; opaque columns stay mapped in flash.
for texname,patchname,accent in [('DPSTEEL','DPWALL','metal'),('DPRUST','DPRPANEL','brown')]:
 a=canvas(64,128);rect(a,0,0,64,128,'dark');rect(a,3,3,58,122,accent)
 rect(a,5,5,54,3,'light');rect(a,58,8,3,116,'black');rect(a,4,62,56,4,'black')
 for yy in (12,76):
  rect(a,12,yy,38,34,'black');rect(a,14,yy+2,34,30,'dark')
  for row in range(yy+6,yy+28,6):rect(a,17,row,26,2,'metal')
 rect(a,6,53,8,3,'green');rect(a,17,53,8,3,'orange')
 new.append((patchname,patch(a,0,0)))
 pnames=dict(new)['PNAMES'];np=struct.unpack_from('<I',pnames)[0]
 newpn=struct.pack('<I',np+1)+pnames[4:]+patchname.encode().ljust(8,b'\0')
 textures=dict(new)['TEXTURE1'];nt=struct.unpack_from('<I',textures)[0];records=[]
 for i in range(nt):
  off=struct.unpack_from('<I',textures,4+i*4)[0];n=struct.unpack_from('<H',textures,off+20)[0];records.append(textures[off:off+22+n*10])
 records.append(struct.pack('<8sIhhIh',texname.encode(),0,64,128,0,1)+struct.pack('<hhhhh',0,0,np,0,0))
 out=bytearray(struct.pack('<I',len(records))+bytes(len(records)*4))
 for i,b in enumerate(records):struct.pack_into('<I',out,4+i*4,len(out));out.extend(b)
 new=[(name,newpn if name=='PNAMES' else bytes(out) if name=='TEXTURE1' else blob) for name,blob in new]
# All geometry is authored here: grid cells combine into rooms, with narrow connectors.
def make_map(number):
 rooms=([(0,0),(4,0),(4,4)] if number==1 else [(0,0),(4,0),(8,0)] if number==2 else [(0,0),(4,0),(4,4),(8,4)])
 cells={}
 for sec,(x,y) in enumerate(rooms):
  for xx in range(x,x+3):
   for yy in range(y,y+3):cells[xx,yy]=sec
 halls=[(3,1)] + ([(5,3)] if number==1 else [(7,1)] if number==2 else [(5,3),(7,5)])
 for xy in halls:cells[xy]=len(rooms)+halls.index(xy)
 lines=[];verts=[];vi={};sides=[]
 def vertex(p):
  p=(p[0]*128,p[1]*128)
  if p not in vi:vi[p]=len(verts);verts.append(p)
  return vi[p]
 def side(sec,mid):
  n=len(sides);sides.append(struct.pack('<hh8s8s8sh',0,0,b'-',b'-',mid.encode(),sec));return n
 ex,ey=rooms[-1];exit_edge=((ex+1,ey+3),(ex+2,ey+3))
 for (x,y),sec in sorted(cells.items()):
  edges=[((x,y),(x,y+1),(x-1,y)),((x,y+1),(x+1,y+1),(x,y+1)),((x+1,y+1),(x+1,y),(x+1,y)),((x+1,y),(x,y),(x,y-1))]
  for a,b,neighbor in edges:
   back=cells.get(neighbor)
   if back==sec:continue
   if back is not None and sec>back:continue
   special=11 if (a,b)==exit_edge else 0
   tex='SW1GRAY' if special else ('DPSTEEL' if sec%2==0 else 'DPRUST')
   front=side(sec,'-' if back is not None else tex);bs=side(back,'-') if back is not None else 65535
   lines.append(struct.pack('<HHHHHHH',vertex(a),vertex(b),4 if back is not None else 1,special,0,front,bs))
 sectors=[]
 for i in range(len(rooms)+len(halls)):
  sectors.append(struct.pack('<hh8s8shhh',0,128,b'FLOOR0_1',b'CEIL3_5',224 if i%2==0 else 176,0,0))
 things=[(64,192,0,1,7)];enemies=[]
 for i,(x,y) in enumerate(rooms):
  points=[(x*128+256,y*128+192,3004 if i%2==0 else 3001)]
  if number>=2 or i==len(rooms)-1:points.append((x*128+192,y*128+288,3001 if number==3 else 3004))
  for px,py,kind in points:things.append((px,py,180,kind,7));enemies.append((px,py,kind))
  things.extend([(x*128+96,y*128+96,0,2049,7),(x*128+96,y*128+288,0,2012,7)])
 lumps_out=[('THINGS',b''.join(struct.pack('<hhhhh',*t) for t in things)),('LINEDEFS',b''.join(lines)),('SIDEDEFS',b''.join(sides)),('VERTEXES',b''.join(struct.pack('<hh',*v) for v in verts)),('SEGS',b''),('SSECTORS',b''),('NODES',b''),('SECTORS',b''.join(sectors)),('REJECT',b''),('BLOCKMAP',b'')]
 return [('MAP%02d'%number,b''),*lumps_out],dict(level=number,rooms=len(rooms),enemies=enemies,exit=(ex*128+192,(ey+3)*128),start=(64,192),title=['THE OUTPOST','IRON HALLS','REACTOR CORE'][number-1])
metadata=[]
for number in range(1,4):
 level,meta=make_map(number);metadata.append(meta);new.extend(level)
raw=OUT/'campaign-input.wad';raw.write_bytes(wad(new))
built=OUT/'campaign-nodes.wad';subprocess.run(['zdbsp','-o',str(built),str(raw)],check=True)
entries=readwad(built.read_bytes());result=wad(entries)
for name,b in entries:
 if name=='NODES':assert not b.startswith((b'XNOD',b'ZNOD')) and len(b)%28==0
path=OUT/'campaign.wad';path.write_bytes(result)
report=dict(sha256=hashlib.sha256(result).hexdigest(),bytes=len(result),lumps=len(entries),levels=metadata,original_sprite_lumps=replaced,node_builder='zdbsp 1.19 normal Doom nodes')
path.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('original_sprite_lumps',)},indent=2))
