/* SPDX-License-Identifier: GPL-3.0-only */
#include "doomgeneric.h"
#include "i_video.h"
#include "lcd_frame.h"
#include "menu_view.h"
#ifdef DP_CAMPAIGN
#include "campaign.h"
#endif
#include "platform.h"
#include "splash.h"
#include <string.h>
extern struct color colors[256];
static uint16_t palette[256];
int dp_native_hud(const unsigned short *,dp_row_sink,void *);
#ifdef DP_NATIVE_ART
/* The face HUD owns rows 210..239. Do not send the legacy campaign status
 * bar there first: the LCD displays writes immediately, exposing both bars. */
static int scene_row(void *ctx,unsigned y,const uint16_t *row,unsigned width){
    return y>=210?1:dp_lcd_row(ctx,y,row,width);
}
#else
#define scene_row dp_lcd_row
#endif
void DG_Init(void){}
void DG_DrawFrame(void){
    for(unsigned i=0;i<256;i++)palette[i]=(uint16_t)(((colors[i].r>>3)<<11)|((colors[i].g>>2)<<5)|(colors[i].b>>3));
    dp_menu_view menu;
#ifdef DP_CAMPAIGN
    int active=dp_menu_snapshot(&menu)||dp_campaign_overlay(&menu);
    int ok=active?(!menu.message&&!strcmp(menu.title,"DOOM")?dp_title_present(&menu,dp_lcd_row,0):dp_menu_present(&menu,dp_lcd_row,0)):dp_campaign_present(I_VideoBuffer,palette,scene_row,0);
#ifdef DP_NATIVE_ART
    if(ok&&!active)ok=dp_native_hud(palette,dp_lcd_row,0);
#endif
#else
    int ok=dp_menu_snapshot(&menu)?dp_menu_present(&menu,dp_lcd_row,0):dp_lcd_present(I_VideoBuffer,palette,dp_lcd_row,0);
#endif
    if(!ok)dp_panic("LCD TRANSFER FAILED");
    dp_frame_done();
    dp_service();
}
void DG_SleepMs(uint32_t ms){uint32_t t=dp_millis();while(dp_millis()-t<ms)dp_service();}
uint32_t DG_GetTicksMs(void){dp_service();return dp_millis();}
int DG_GetKey(int *down,unsigned char *key){return dp_key(down,key);}
void DG_SetWindowTitle(const char *title){dp_message(title);}
