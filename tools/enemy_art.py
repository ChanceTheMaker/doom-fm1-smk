# SPDX-License-Identifier: GPL-3.0-only
"""Original low-resolution enemy artwork, drawn as shaded pixel polygons."""
def draw(kind,frame,rotation,colors,patch):
 w,h=40,60;a=[[-1]*w for _ in range(h)]
 def poly(points,c):
  for y in range(h):
   hits=[]
   for (x1,y1),(x2,y2) in zip(points,points[1:]+points[:1]):
    if min(y1,y2)<=y<max(y1,y2):hits.append(x1+(y-y1)*(x2-x1)/(y2-y1))
   hits.sort()
   for left,right in zip(hits[::2],hits[1::2]):
    for x in range(max(0,int(left)),min(w,int(right)+1)):a[y][x]=colors[c]
 def box(x,y,ww,hh,c):poly([(x,y),(x+ww-1,y),(x+ww-1,y+hh),(x,y+hh)],c)
 guard=kind=='POSS';death=frame>='H' if guard else frame>='I'
 hurt=frame=='G' if guard else frame=='H';attack=frame in ('EF' if guard else 'EFG')
 # Back and side silhouettes share animation data where possible to fit flash.
 back=rotation in (4,5,6);side=rotation in (3,7)
 body='green' if guard else 'brown';hi='armor' if guard else 'skin';lit='light' if guard else 'orange'
 if death:
  fall=ord(frame)-ord('H' if guard else 'I')
  if fall==0:
   poly([(7,57),(10,38),(15,23),(24,20),(32,39),(34,58)],'black')
   poly([(11,45),(14,26),(24,24),(30,43),(23,52)],body);box(17,18,11,10,hi)
   poly([(9,54),(21,46),(28,54),(35,57),(35,59),(6,59)],'dark')
  else:
   poly([(2,55),(7,47),(21,46),(28,50),(37,53),(39,59),(2,59)],'black')
   poly([(6,54),(10,48),(22,48),(26,53),(22,57),(5,57)],body)
   box(26,50,9,6,hi);box(10,49,9,3,lit);box(3,56,11,3,'dark')
  return patch(a,20,60)
 step=3 if frame in 'BD' else 0
 # Heavy boots, staggered legs, narrow waist, sloped shoulders.
 poly([(10,35),(19,34),(20,46),(16,56-step),(18,58-step),(5,58-step),(7,54-step),(10,45)],'black')
 poly([(21,34),(29,35),(30,47),(35,55+step//2),(35,59),(23,59),(22,54),(20,44)],'black')
 poly([(12,36),(18,36),(17,46),(13,54-step),(8,54-step),(11,45)],'dark' if guard else 'brown')
 poly([(22,36),(27,36),(28,47),(31,55),(25,55),(23,47)],body)
 box(11,39,4,8,hi);box(23,40,3,7,hi);box(7,54-step,10,2,'metal' if guard else 'skin')
 poly([(10,17),(15,14),(25,14),(31,18),(29,34),(25,40),(14,39),(10,32)],'black')
 poly([(12,18),(17,16),(25,16),(29,20),(26,34),(23,38),(15,36),(12,30)],body)
 poly([(13,20),(19,18),(20,29),(15,31),(12,27)],hi)
 poly([(21,18),(27,20),(26,28),(22,30)],hi)
 box(14,32,12,3,'dark');box(18,33,4,2,'metal' if guard else 'orange')
 # Muscular arms and elbow highlights.
 poly([(9,18),(13,19),(12,29),(8,37),(3,34),(5,24)],'black')
 poly([(7,21),(11,20),(10,28),(6,33),(4,32)],hi)
 poly([(28,18),(33,20),(37,31),(34,37),(29,33),(28,28)],'black')
 poly([(30,21),(33,24),(35,31),(32,33),(30,29)],hi)
 if guard:
  poly([(14,4),(18,2),(25,3),(28,8),(27,15),(22,18),(16,15),(13,9)],'black')
  poly([(16,5),(20,3),(25,5),(26,10),(24,15),(18,15),(15,10)],'metal')
  box(15,5,11,3,'green');box(16,5,6,1,'armor')
  if not back:box(16,9,10,3,'black');box(17,9,7,1,'red');box(20,13,4,2,'dark')
  else:box(18,9,6,5,'dark');box(20,20,5,10,'dark');box(21,21,3,6,'metal')
  if not back:
   poly([(7,28),(12,25),(31,27),(33,30),(26,32),(9,32)],'black')
   box(13,27,18,2,'metal');box(21,26,7,2,'light');box(11,30,6,5,'brown');box(8,28,5,3,'skin')
   if attack:poly([(30,25),(35,22),(34,27),(39,29),(34,31),(35,35),(30,32)],'orange');box(31,27,5,3,'yellow')
 else:
  poly([(12,8),(17,4),(24,5),(29,10),(26,17),(20,20),(14,16)],'black')
  poly([(15,8),(20,6),(25,9),(26,13),(23,17),(17,16)],'skin')
  poly([(13,10),(9,5),(10,0),(14,6),(17,9)],'white');poly([(24,8),(28,3),(32,0),(30,7),(27,12)],'white')
  if not back:box(15,11,4,2,'yellow');box(23,11,3,2,'yellow');box(18,15,6,2,'black');box(19,15,4,1,'white')
  else:poly([(20,7),(23,10),(21,29),(18,29)],'dark')
  for x in (4,7,31,34):box(x,34,2,4,'white')
  if attack:poly([(4,31),(0,25),(3,18),(8,21),(11,27),(7,34)],'orange');box(3,23,5,6,'yellow');box(4,24,2,3,'white')
 if hurt:box(15,22,3,4,'red');box(22,27,2,3,'red')
 if side:
  b=[[-1]*w for _ in range(h)]
  for y in range(h):
   for x in range(6,34):b[y][13+(x-6)*2//3]=a[y][x]
  a=b
 return patch(a,20,60)
