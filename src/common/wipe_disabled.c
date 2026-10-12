/* SPDX-License-Identifier: GPL-3.0-only */
/* A direct transition avoids two temporary 64,000-byte screen copies. */
#include "f_wipe.h"
int wipe_StartScreen(int x,int y,int width,int height) {(void)x;(void)y;(void)width;(void)height;return 0;}
int wipe_EndScreen(int x,int y,int width,int height) {(void)x;(void)y;(void)width;(void)height;return 0;}
int wipe_ScreenWipe(int wipeno,int x,int y,int width,int height,int ticks) {(void)wipeno;(void)x;(void)y;(void)width;(void)height;(void)ticks;return 1;}
