/* SPDX-License-Identifier: GPL-3.0-only */
#pragma once
#include "lcd_frame.h"
int dp_splash_present(unsigned board,dp_row_sink sink,void *context);

#include "menu_view.h"
int dp_title_present(const dp_menu_view *menu,dp_row_sink sink,void *context);
void dp_title_start(void);
