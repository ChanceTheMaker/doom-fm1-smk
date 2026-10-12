/* SPDX-License-Identifier: GPL-3.0-only */
#include "lcd_frame.h"
#include <assert.h>
#include <stdio.h>
static uint8_t pixels[320*200];
static uint16_t palette[256];
static unsigned rows;
static int sink(void *ctx,unsigned y,const uint16_t *row,unsigned width) {
    (void)ctx;assert(y==rows++);assert(width==240);
    for(unsigned x=0;x<width;++x) {
        unsigned expected=0;
        if(y>=30&&y<210) expected=palette[pixels[((y-30)*200/180)*320+x*320/240]];
        assert(row[x]==expected);
    }
    return 1;
}
static int fail_sink(void *ctx,unsigned y,const uint16_t *row,unsigned width) {(void)ctx;(void)y;(void)row;(void)width;return 0;}
int main(void) {
    for(unsigned i=0;i<sizeof pixels;++i)pixels[i]=(uint8_t)(i^(i/320));
    for(unsigned i=0;i<256;++i)palette[i]=(uint16_t)(i*257);
    assert(dp_lcd_present(pixels,palette,sink,0));assert(rows==240);
    assert(!dp_lcd_present(pixels,palette,fail_sink,0));
    assert(!dp_lcd_present(0,palette,sink,0));
    puts("LCD: mapping, letterbox rows, bounds and sink failure passed");
}
