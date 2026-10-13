/* SPDX-License-Identifier: GPL-3.0-only */
#pragma once
#include "lcd_frame.h"
#define DP_MENU_ROWS 8
#define DP_MENU_COLS 19
typedef struct {
    char title[20], rows[DP_MENU_ROWS][DP_MENU_COLS+1], footer[40];
    int count, selected, message;
} dp_menu_view;
/* Snapshot of engine menu state; no allocations or input handling. */
int dp_menu_snapshot(dp_menu_view *view);
void dp_menu_scroll(int steps); /* clockwise/down; ignores gameplay and messages */
int dp_menu_present(const dp_menu_view *view, dp_row_sink sink, void *ctx);

void dp_text_row(uint16_t *row,unsigned y,int x,int top,const char *s,unsigned scale,uint16_t color);
