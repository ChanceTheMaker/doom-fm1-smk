/* SPDX-License-Identifier: GPL-3.0-only */
#include "lcd_frame.h"
int dp_lcd_present(const uint8_t *pixels, const uint16_t palette[256], dp_row_sink sink, void *ctx) {
    uint16_t row[DP_LCD_WIDTH];
    if (!pixels || !palette || !sink) return 0;
    for (unsigned y=0; y<DP_LCD_HEIGHT; ++y) {
        if (y < 30 || y >= 210) {
            for (unsigned x=0; x<DP_LCD_WIDTH; ++x) row[x]=0;
        } else {
            unsigned sy=(y-30)*200/DP_VIEW_HEIGHT;
            for (unsigned x=0; x<DP_LCD_WIDTH; ++x) row[x]=palette[pixels[sy*320+x*320/DP_LCD_WIDTH]];
        }
        if (!sink(ctx,y,row,DP_LCD_WIDTH)) return 0;
    }
    return 1;
}
