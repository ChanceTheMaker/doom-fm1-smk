/* SPDX-License-Identifier: GPL-3.0-only */
#pragma once
#include "menu_view.h"
extern unsigned dp_score;
void dp_campaign_kill(unsigned points);
void dp_campaign_reset(void);
void dp_campaign_load(void);
int dp_campaign_overlay(dp_menu_view *view);
int dp_campaign_present(const unsigned char *pixels,const unsigned short *palette,dp_row_sink sink,void *ctx);
