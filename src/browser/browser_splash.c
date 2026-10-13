/* SPDX-License-Identifier: GPL-3.0-only */
/* Shared native/browser title menu. Logo provenance: assets/branding. */
#include "splash.h"
#include "w_wad.h"
#include "z_zone.h"
#include <string.h>
static unsigned le16(const unsigned char *p){return p[0]|(unsigned)p[1]<<8;}
int dp_title_present(const dp_menu_view *menu,dp_row_sink sink,void *ctx){
 const unsigned char *logo=W_CacheLumpName("DPLOGO",PU_CACHE);
 unsigned w=le16(logo),h=le16(logo+2);int left=(240-(int)w)/2;
 uint16_t row[240];
 for(unsigned y=0;y<240;y++){
  for(unsigned x=0;x<240;x++){
   row[x]=y<142?0:((x+y)%7==0?0x1082:0x0841);
   if(y>=12&&y<12+h&&(int)x>=left&&x<left+w){
    unsigned i=(y-12)*w+x-left,c=(logo[36+i/2]>>((i&1)*4))&15;
    if(c)row[x]=le16(logo+4+c*2);
   }
  }
  for(int i=0;i<menu->count&&i<3;i++){
   unsigned yy=150+i*22;int selected=i==menu->selected;
   if(selected&&y>=yy-3&&y<yy+17)for(unsigned x=22;x<218;x++)row[x]=0x2800;
   dp_text_row(row,y,selected?26:32,yy,selected?">":"",2,0xfd20);
   dp_text_row(row,y,48,yy,menu->rows[i],2,selected?0xffb0:0xbdd7);
  }
  dp_text_row(row,y,18,221,"2/4 MOVE  8 SELECT  7 BACK",1,0x9cf3);
  if(!sink(ctx,y,row,240))return 0;
 }
 return 1;
}
int dp_splash_present(unsigned board,dp_row_sink sink,void *ctx){
 (void)board;dp_menu_view menu;memset(&menu,0,sizeof menu);menu.selected=0;menu.count=3;
 strcpy(menu.rows[0],"START GAME");strcpy(menu.rows[1],"OPTIONS");strcpy(menu.rows[2],"CONTROLS");
 return dp_title_present(&menu,sink,ctx);
}
