/* SPDX-License-Identifier: GPL-3.0-only */
/* Browser splash using the same credited Freedoom monster as the campaign. */
#include "splash.h"
#include "menu_view.h"
#include "w_wad.h"
#include "z_zone.h"
static unsigned le16(const unsigned char *p){return p[0]|(unsigned)p[1]<<8;}
static unsigned le32(const unsigned char *p){return le16(p)|le16(p+2)<<16;}
static int pixel(const unsigned char *p,unsigned x,unsigned y){
 const unsigned char *post=p+le32(p+8+4*x);
 while(post[0]!=255){
  if(y>=post[0]&&y<post[0]+post[1])return post[3+y-post[0]];
  post+=post[1]+4;
 }
 return -1;
}
int dp_splash_present(unsigned board,dp_row_sink sink,void *ctx){
#ifdef DP_NATIVE_ART
 const unsigned char *monster=W_CacheLumpName("TROOA0",PU_CACHE);
 const char *label=board==0?"FM-1":board==1?"SMK-37 PRO":"SMK-37 ELITE";
#else
 (void)board;
 const unsigned char *monster=W_CacheLumpName("TROOA1",PU_CACHE);
 const char *label="FM-1 / BROWSER";
#endif
 const unsigned char *pal=W_CacheLumpName("PLAYPAL",PU_CACHE);
 const unsigned width=le16(monster),height=le16(monster+2);
 const int left=(240-(int)width*2)/2,top=88;
 uint16_t row[240];
 for(unsigned y=0;y<240;y++){
  for(unsigned x=0;x<240;x++){
   unsigned heat=y>100?(y-100)/9:0;row[x]=(uint16_t)((2+heat)<<11);
   if((x*17+y*29)%433==0)row[x]=0x8a20;
   if(y>95&&y<205&&((x+y/2)%43<2))row[x]=0x5100;
   if(y>=191&&y<209){unsigned key=x/15;row[x]=x%15==0?0:0x7b8c;
    if(y<203&&(key%7==1||key%7==2||key%7==4||key%7==5||key%7==6)&&x%15<7)row[x]=0;}
   if((int)x>=left&&x<left+width*2&&(int)y>=top&&y<top+height*2){
    int c=pixel(monster,(x-left)/2,(y-top)/2);
    if(c>=0)row[x]=((pal[c*3]>>3)<<11)|((pal[c*3+1]>>2)<<5)|(pal[c*3+2]>>3);
   }
  }
  dp_text_row(row,y,47,10,"YOUR SYNTH. THEIR DOOM.",1,0xfdc0);
  dp_text_row(row,y,27,30,"DOOM",8,0);
  dp_text_row(row,y,24,26,"DOOM",8,y<52?0xffb0:0xe9e0);
  dp_text_row(row,y,(240-6*__builtin_strlen(label))/2,215,label,1,0xffff);
#ifdef DP_NATIVE_ART
  dp_text_row(row,y,66,229,"TEST13 / 9 LEVELS",1,0xfdc0);
#else
  dp_text_row(row,y,66,229,"TEST06 / SOUND ON",1,0xfdc0);
#endif
  if(!sink(ctx,y,row,240))return 0;
 }
 return 1;
}
