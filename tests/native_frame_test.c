/* SPDX-License-Identifier: GPL-3.0-only */
/* Exercise the real native frame dispatcher with instrumented display sinks. */
#include "doomgeneric.h"
#include "i_video.h"
#include "menu_view.h"
#include <assert.h>
#include <setjmp.h>
#include <stdio.h>
#include <string.h>
struct color colors[256];
byte *I_VideoBuffer;
static unsigned writes[240],next_row,frames,hud_calls;
static int menu_on,overlay_on,fail_row=-1,title_calls;
static jmp_buf panic_target;
int dp_menu_snapshot(dp_menu_view *v){memset(v,0,sizeof *v);strcpy(v->title,menu_on==2?"DOOM":"OPTIONS");return menu_on;}
int dp_campaign_overlay(dp_menu_view *v){(void)v;return overlay_on;}
static int emit(unsigned first,unsigned end,unsigned value,dp_row_sink sink,void *ctx){
    uint16_t row[240];for(unsigned x=0;x<240;x++)row[x]=value;
    for(unsigned y=first;y<end;y++)if(!sink(ctx,y,row,240))return 0;
    return 1;
}
int dp_campaign_present(const unsigned char *p,const unsigned short *pal,dp_row_sink sink,void *ctx){
    (void)p;(void)pal;return emit(0,240,1,sink,ctx);
}
int dp_menu_present(const dp_menu_view *v,dp_row_sink sink,void *ctx){
    (void)v;return emit(0,240,3,sink,ctx);
}
int dp_title_present(const dp_menu_view *v,dp_row_sink sink,void *ctx){(void)v;title_calls++;return emit(0,240,3,sink,ctx);}
int dp_native_hud(const unsigned short *pal,dp_row_sink sink,void *ctx){
    (void)pal;hud_calls++;return emit(210,240,2,sink,ctx);
}
int dp_lcd_row(void *ctx,unsigned y,const uint16_t *row,unsigned width){
    (void)ctx;assert(width==240);assert(y==next_row++);assert(++writes[y]==1);
    unsigned expected=(menu_on||overlay_on)?3:y<210?1:2;
    for(unsigned x=0;x<width;x++)assert(row[x]==expected);
    return (int)y!=fail_row;
}
void dp_panic(const char *s){assert(!strcmp(s,"LCD TRANSFER FAILED"));longjmp(panic_target,1);}
void dp_frame_done(void){frames++;}
void dp_service(void){}
uint32_t dp_millis(void){return 0;}
int dp_key(int *d,unsigned char *k){(void)d;(void)k;return 0;}
void dp_message(const char *s){(void)s;}
static void reset(void){memset(writes,0,sizeof(writes));next_row=frames=hud_calls=0;}
int main(void){
    for(int mode=0;mode<4;mode++){
        menu_on=mode==3?2:mode==1;overlay_on=mode==2;reset();DG_DrawFrame();
        assert(next_row==240&&frames==1&&hud_calls==(unsigned)(mode==0));
    }
    assert(title_calls==1);
    menu_on=overlay_on=0;
    for(int row=100;row<=220;row+=120){
        reset();fail_row=row;
        if(!setjmp(panic_target)){DG_DrawFrame();assert(!"expected display failure");}
        assert(next_row==(unsigned)row+1&&frames==0);
        assert(hud_calls==(unsigned)(row>=210));
    }
    puts("native frame: one ordered write per LCD row; menus, overlays and failures passed");
    return 0;
}
