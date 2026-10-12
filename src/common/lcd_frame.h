/* SPDX-License-Identifier: GPL-3.0-only */
#pragma once
#include <stdint.h>
#define DP_LCD_WIDTH 240
#define DP_LCD_HEIGHT 240
#define DP_VIEW_HEIGHT 180 /* Doom's original 4:3 display aspect. */
typedef int (*dp_row_sink)(void *ctx, unsigned y, const uint16_t *row, unsigned width);
/* RGB565 values are host-endian here. Hardware sinks must serialize LCD order.
 * The sink consumes/copies each row before returning: the buffer is reused. */
int dp_lcd_present(const uint8_t *pixels, const uint16_t palette[256], dp_row_sink sink, void *ctx);
