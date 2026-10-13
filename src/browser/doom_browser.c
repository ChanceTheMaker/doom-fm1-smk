/* SPDX-License-Identifier: GPL-3.0-only */
/* Browser peripherals only; shared Doom engine, maps, LCD and sound. */
#include "doomgeneric.h"
#include "doomkeys.h"
#include "doomstat.h"
#include "i_video.h"
#include "st_stuff.h"
#include "lcd_frame.h"
#include "menu_view.h"
#include "campaign.h"
#include "splash.h"
#include "sfx.h"
int dp_native_hud(const unsigned short *,dp_row_sink,void *);
#include <emscripten.h>
#include <stdio.h>
#include <string.h>
extern struct color colors[256];
extern boolean singletics;
static unsigned ticks,rd,wr;
static unsigned char events[256][2],held[12];
static uint8_t screen[240*240*4];
static int32_t audio[1260*2];
static float mono[1260];
static const unsigned char keys[]={KEY_LEFTARROW,KEY_UPARROW,KEY_RIGHTARROW,KEY_DOWNARROW,KEY_FIRE,KEY_USE,KEY_ESCAPE,KEY_ENTER,KEY_RSHIFT,KEY_STRAFE_L,KEY_STRAFE_R,']'};
static int row(void *ctx,unsigned y,const uint16_t *pixels,unsigned width){
 (void)ctx;for(unsigned x=0;x<width;x++){unsigned c=pixels[x],i=(y*240+x)*4;
 screen[i]=((c>>11)&31)*255/31;screen[i+1]=((c>>5)&63)*255/63;screen[i+2]=(c&31)*255/31;screen[i+3]=255;}return 1;
}
void DG_Init(void){}
void DG_DrawFrame(void){
 uint16_t pal[256];for(unsigned i=0;i<256;i++)pal[i]=((colors[i].r>>3)<<11)|((colors[i].g>>2)<<5)|(colors[i].b>>3);
 dp_menu_view menu;
 if(dp_menu_snapshot(&menu)||dp_campaign_overlay(&menu)){if(!menu.message&&!strcmp(menu.title,"DOOM"))dp_title_present(&menu,row,0);else dp_menu_present(&menu,row,0);}
 else {dp_campaign_present(I_VideoBuffer,pal,row,0);dp_native_hud(pal,row,0);}

}
void DG_SleepMs(uint32_t ms){ticks+=ms;}
uint32_t DG_GetTicksMs(void){return ticks;}
int DG_GetKey(int *down,unsigned char *key){if(rd==wr)return 0;*down=events[rd][0];*key=events[rd][1];rd=(rd+1)&255;return 1;}
void DG_SetWindowTitle(const char *s){(void)s;}
void dp_message(const char *s){(void)s;}
void dp_panic(const char *s){fprintf(stderr,"Doom: %s\n",s);emscripten_force_exit(1);__builtin_unreachable();}
EMSCRIPTEN_KEEPALIVE void browser_init(int preview_level){
 static char warp[]={'1',0};
 static char *args[]={"doom","-iwad","miniwad.wad","-nosound","-warp",warp,"-skill","2"};
 /* UI passes zero; capture tooling can choose any of the nine real levels. */
 warp[0]='0'+(preview_level>=1&&preview_level<=DP_CAMPAIGN_LEVELS?preview_level:1);
 /* Engine discovery checks stdio before the mapped WAD reader takes over. */
 FILE *marker=fopen("miniwad.wad","wb");if(!marker)dp_panic("ASSET DISCOVERY FAILED");fputs("IWAD",marker);fclose(marker);
 singletics=true;dp_sfx_master(700);doomgeneric_Create(8,args);if(!preview_level)dp_title_start();
}
EMSCRIPTEN_KEEPALIVE void browser_key(int action,int down){
 if(action<0||action>=12||held[action]==!!down)return;
 unsigned next=(wr+1)&255;if(next==rd)return;
 held[action]=!!down;events[wr][0]=!!down;events[wr][1]=keys[action];wr=next;
}
EMSCRIPTEN_KEEPALIVE void browser_release(void){for(int i=0;i<12;i++)browser_key(i,0);}
EMSCRIPTEN_KEEPALIVE void browser_menu_scroll(int steps){dp_menu_scroll(steps);}
EMSCRIPTEN_KEEPALIVE void browser_step(void){ticks+=29;doomgeneric_Tick();}
EMSCRIPTEN_KEEPALIVE void browser_splash(void){dp_splash_present(0,row,0);}
EMSCRIPTEN_KEEPALIVE void *browser_frame(void){return screen;}
EMSCRIPTEN_KEEPALIVE void *browser_audio(void){dp_sfx_render(audio,1260);for(unsigned i=0;i<1260;i++)mono[i]=audio[i*2]/8388608.0f;return mono;}
EMSCRIPTEN_KEEPALIVE int browser_stat(int field){
 player_t *p=&players[consoleplayer];
 switch(field){case 0:return gametic;case 1:return p->health;case 2:return dp_score;case 3:return gamemap;case 4:return p->mo?p->mo->x:0;case 5:return p->mo?p->mo->y:0;case 6:return p->mo?p->mo->angle:0;case 7:return p->ammo[am_shell];case 8:return p->readyweapon;case 9:return menuactive;default:return 0;}
}
