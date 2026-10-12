/* SPDX-License-Identifier: GPL-3.0-only */
#include "menu_view.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned rows;
static unsigned char image[240][240];
static int sink(void *ctx,unsigned y,const uint16_t *row,unsigned width) {
    (void)ctx;assert(y==rows++&&y<240&&width==240);
    for(unsigned x=0;x<240;x++)image[y][x]=row[x]==0?1:row[x]==0xffff?2:0;
    return 1;
}
static int fail(void *ctx,unsigned y,const uint16_t *row,unsigned width) {
    (void)ctx;(void)y;(void)row;(void)width;return 0;
}
int main(void) {
    dp_menu_view v={0};strcpy(v.title,"DOOM");strcpy(v.rows[0],"NEW GAME");v.count=1;v.selected=0;
    assert(dp_menu_present(&v,sink,0)&&rows==240);
    /* Selected glyph strokes are complete 2x2 blocks at the LCD's native size. */
    unsigned ink=0;
    for(unsigned y=49;y<63;y+=2)for(unsigned x=14;x<24;x+=2) {
        unsigned b=image[y][x];ink+=b==1;
        assert(image[y+1][x]==b&&image[y][x+1]==b&&image[y+1][x+1]==b);
    }
    assert(ink>10);
    v.count=8;v.selected=7;v.message=1;
    for(unsigned i=0;i<8;i++){memset(v.rows[i],'W',DP_MENU_COLS);v.rows[i][DP_MENU_COLS]=0;}
    rows=0;assert(dp_menu_present(&v,sink,0)&&rows==240);
    assert(!dp_menu_present(&v,fail,0));assert(!dp_menu_present(0,sink,0));
    v.count=9;assert(!dp_menu_present(&v,sink,0));
    puts("PASS menu: native-size strokes, full rows, longest messages, sink failure and bounds");
}
