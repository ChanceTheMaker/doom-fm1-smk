/* SPDX-License-Identifier: GPL-3.0-only */
#include "doomgeneric.h"
#include "i_video.h"
#include "lcd_frame.h"
#include "menu_view.h"
#include "platform.h"
extern struct color colors[256];
static uint16_t palette[256];
void DG_Init(void){}
void DG_DrawFrame(void){
    for(unsigned i=0;i<256;i++)palette[i]=(uint16_t)(((colors[i].r>>3)<<11)|((colors[i].g>>2)<<5)|(colors[i].b>>3));
    dp_menu_view menu;
    int ok=dp_menu_snapshot(&menu)?dp_menu_present(&menu,dp_lcd_row,0):dp_lcd_present(I_VideoBuffer,palette,dp_lcd_row,0);
    if(!ok)dp_panic("LCD TRANSFER FAILED");
    dp_frame_done();
    dp_service();
}
void DG_SleepMs(uint32_t ms){uint32_t t=dp_millis();while(dp_millis()-t<ms)dp_service();}
uint32_t DG_GetTicksMs(void){dp_service();return dp_millis();}
int DG_GetKey(int *down,unsigned char *key){return dp_key(down,key);}
void DG_SetWindowTitle(const char *title){dp_message(title);}
