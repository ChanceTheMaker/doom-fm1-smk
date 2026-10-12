/* SPDX-License-Identifier: GPL-3.0-only */
/* Readable 240px status bar with credited Freedoom face patches, in XIP. */
#include "doomstat.h"
#include "d_items.h"
#include "w_wad.h"
#include "z_zone.h"
#include "menu_view.h"
#include <stdio.h>
static unsigned rd16(const unsigned char *p){return p[0]|(unsigned)p[1]<<8;}
static unsigned rd32(const unsigned char *p){return rd16(p)|rd16(p+2)<<16;}
int dp_native_hud(const unsigned short *palette,dp_row_sink sink,void *ctx){
 player_t *p=&players[consoleplayer];
 const char *name=p->health<=0?"STFDEAD0":p->health<35?"STFST40":p->health<70?"STFST20":"STFST00";
 const unsigned char *face=W_CacheLumpName(name,PU_CACHE);
 unsigned w=rd16(face),h=rd16(face+2);
 char health[12],ammo[12],armor[12];
 ammotype_t type=weaponinfo[p->readyweapon].ammo;
 snprintf(health,sizeof health,"%d",p->health<0?0:p->health);
 snprintf(ammo,sizeof ammo,"%d",type<NUMAMMO?p->ammo[type]:0);
 snprintf(armor,sizeof armor,"%d",p->armorpoints);
 for(unsigned y=210;y<240;y++){
  unsigned fy=(y-210)*h/30;uint16_t row[240];
  for(unsigned x=0;x<240;x++){
   row[x]=y==210?0xb596:y==239?0x0841:((x/3+y)%3?0x4208:0x39c7);
   if(x==68||x==171)row[x]=0x1082;
   if(x>=108&&x<132){
    unsigned fx=(x-108)*w/24;const unsigned char *post=face+rd32(face+8+4*fx);
    while(post[0]!=255){
     if(fy>=post[0]&&fy<post[0]+post[1]){row[x]=palette[post[3+fy-post[0]]];break;}
     post+=post[1]+4;
    }
   }
  }
  dp_text_row(row,y,8,213,ammo,2,0xfa20);dp_text_row(row,y,8,231,"AMMO",1,0xffff);
  dp_text_row(row,y,72,213,health,2,0xfa20);dp_text_row(row,y,72,231,"HP",1,0xffff);
  dp_text_row(row,y,180,213,armor,2,0xfa20);dp_text_row(row,y,180,231,"ARMOR",1,0xffff);
  if(!sink(ctx,y,row,240))return 0;
 }
 return 1;
}
