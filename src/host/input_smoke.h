/* SPDX-License-Identifier: GPL-3.0-only */
#ifndef DP_INPUT_SMOKE_H
#define DP_INPUT_SMOKE_H
void dp_input_init(void);
int dp_input_next(int *pressed, unsigned char *key);
void dp_input_observe(int final);
#endif
