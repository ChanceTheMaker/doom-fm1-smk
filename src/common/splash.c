/* SPDX-License-Identifier: GPL-3.0-only */
#include "splash.h"
#include "menu_view.h"
int dp_splash_present(unsigned board,dp_row_sink sink,void *ctx){
 uint16_t row[240];
 for(unsigned y=0;y<240;y++){
  for(unsigned x=0;x<240;x++){
   unsigned heat=y>140?(y-140)/4:0;row[x]=(uint16_t)((3+heat)<<11);
   if((x*17+y*29)%433==0)row[x]=0x8a20;
   if(y>148&&y<180&&((x+y/2)%27<2))row[x]=0xe260;
   if(y>=179&&y<202){unsigned k=x/15;row[x]=x%15==0?0:0xce59;if(y<193&&(k%7==1||k%7==2||k%7==4||k%7==5||k%7==6)&&x%15<7)row[x]=0;}
   /* A tiny demon face rising over the keys. */
   if(y>=113&&y<145&&x>=100&&x<140)row[x]=0x9920;
   if(y>=119&&y<123&&((x>=105&&x<115)||(x>=125&&x<135)))row[x]=0xff80;
   if(y>=133&&y<140&&x>=109&&x<131)row[x]=(x%6<3)?0xffbd:0;
   if(y>=100&&y<119&&((x>=96&&x<103+(y-100)/3)||(x>137-(y-100)/3&&x<144)))row[x]=0xffbd;
  }
  dp_text_row(row,y,47,14,"YOUR SYNTH. THEIR DOOM.",1,0xfdc0);
  dp_text_row(row,y,27,43,"DOOM",8,0x0000);
  dp_text_row(row,y,24,39,"DOOM",8,y<66?0xffb0:0xe9e0);
  const char *name=board==0?"FM-1":board==1?"SMK-37 PRO":"SMK-37 ELITE";
  dp_text_row(row,y,board==0?96:board==1?60:48,91,name,2,0xffff);
  dp_text_row(row,y,54,158,"RIP. TEAR. REPEAT.",1,0xffbd);
  dp_text_row(row,y,42,213,"WHITE KEYS: 5 FIRE / 6 USE",1,0xffff);
  dp_text_row(row,y,66,228,"TEST06 / SOUND ON",1,0xfdc0);
  if(!sink(ctx,y,row,240))return 0;
 }
 return 1;
}
