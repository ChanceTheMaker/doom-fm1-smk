/* SPDX-License-Identifier: GPL-3.0-only */
#pragma once
#include <stdint.h>
void dp_service(void);
uint32_t dp_millis(void);
int dp_key(int *down,unsigned char *key);
int dp_lcd_row(void *context,unsigned y,const uint16_t *row,unsigned width);
void dp_message(const char *text);
void dp_frame_done(void);
void dp_panic(const char *text) __attribute__((noreturn));
