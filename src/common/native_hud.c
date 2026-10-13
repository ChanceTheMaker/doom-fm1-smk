/* SPDX-License-Identifier: GPL-3.0-only */
/* Classic status layout, compiled to 240x30; one LCD row buffer, no heap. */
#include "doomstat.h"
#include "d_items.h"
#include "w_wad.h"
#include "z_zone.h"
#include "menu_view.h"
#include <stdio.h>
#include <string.h>
static unsigned rd16(const unsigned char *p){return p[0]|(unsigned)p[1]<<8;}
static unsigned rd32(const unsigned char *p){return rd16(p)|rd16(p+2)<<16;}
static const unsigned char *patch(const char *name){return W_CacheLumpName(name,PU_CACHE);}
static void draw(uint16_t *row,unsigned y,int left,int top,const unsigned char *p,const uint16_t *pal){
 int sy=(int)y-top,w=rd16(p),h=rd16(p+2);if(sy<0||sy>=h)return;
 for(int x=0;x<w;x++){
  if(left+x<0||left+x>=240)continue;
  const unsigned char *post=p+rd32(p+8+4*x);
  while(post[0]!=255){
   if(sy>=post[0]&&sy<post[0]+post[1]){row[left+x]=pal[post[3+sy-post[0]]];break;}
   post+=post[1]+4;
  }
 }
}
static void number(uint16_t *row,unsigned y,int right,int top,int value,const unsigned char *const *digits,const uint16_t *pal){
 if(value<0)return;if(value>999)value=999;
 do{const unsigned char *p=digits[value%10];right-=rd16(p);draw(row,y,right,top,p,pal);value/=10;}while(value);
}
int dp_native_hud(const unsigned short *palette,dp_row_sink sink,void *ctx){
 player_t *p=&players[consoleplayer];
 const unsigned char *large[10],*small[10],*gray[10],*keys[6];char name[12];
 for(int i=0;i<10;i++){
  snprintf(name,sizeof name,"STTNUM%d",i);large[i]=patch(name);
  snprintf(name,sizeof name,"STYSNUM%d",i);small[i]=patch(name);
  snprintf(name,sizeof name,"STGNUM%d",i);gray[i]=patch(name);
 }
 for(int i=0;i<6;i++){snprintf(name,sizeof name,"STKEYS%d",i);keys[i]=patch(name);}
 int tier=p->health<35?4:p->health<70?2:0;
 if(p->health<=0)strcpy(name,"STFDEAD0");
 else if(p->damagecount>0)snprintf(name,sizeof name,"STFOUCH%d",tier);
 else{int glance=(leveltime/17)%8;snprintf(name,sizeof name,"STFST%d%d",tier,glance==3?1:glance==7?2:0);}
 const unsigned char *face=patch(name),*bar=patch("STBAR"),*arms=patch("STARMS"),*percent=patch("STTPRCNT");
 /* Center each expression within the status bar's 26 x 30 face window. */
 const int face_x=108+(26-(int)rd16(face))/2;
 const int face_y=(30-(int)rd16(face+2))/2;
 ammotype_t type=weaponinfo[p->readyweapon].ammo;
 const int ammo_order[]={am_clip,am_shell,am_misl,am_cell};
 for(unsigned y=0;y<30;y++){
  uint16_t row[240];memset(row,0,sizeof row);draw(row,y,0,0,bar,palette);
  draw(row,y,78,0,arms,palette);draw(row,y,face_x,face_y,face,palette);
  number(row,y,33,3,type<NUMAMMO?p->ammo[type]:-1,large,palette);
  number(row,y,67,3,p->health<0?0:p->health,large,palette);draw(row,y,67,3,percent,palette);
  number(row,y,165,3,p->armorpoints,large,palette);draw(row,y,165,3,percent,palette);
  for(int i=0;i<6;i++){
   int owned=p->weaponowned[i+1];draw(row,y,83+(i%3)*9,4+(i/3)*9,(owned?small:gray)[i+2],palette);
  }
  for(int i=0;i<3;i++){int key=p->cards[i+3]?i+3:p->cards[i]?i:-1;if(key>=0)draw(row,y,179,3+i*9,keys[key],palette);}
  for(int i=0;i<4;i++){
   number(row,y,216,5+i*6,p->ammo[ammo_order[i]],small,palette);
   number(row,y,235,5+i*6,p->maxammo[ammo_order[i]],small,palette);
  }
  if(!sink(ctx,210+y,row,240))return 0;
 }
 return 1;
}
