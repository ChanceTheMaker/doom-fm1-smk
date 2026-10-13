/* SPDX-License-Identifier: GPL-3.0-only */
#pragma once
#include <stdint.h>
enum {DP_BANG,DP_PUMP,DP_GROWL,DP_HURT,DP_DEATH,DP_PICKUP,DP_SWITCH,DP_FIREBALL,DP_HIT,DP_SFX_COUNT};
/* One main-thread producer, one audio-IRQ consumer; no allocation or engine access. */
int dp_sfx_post(unsigned effect,unsigned volume,unsigned priority);
void dp_sfx_master(unsigned volume); /* 0..1023 */
void dp_sfx_trim(unsigned volume); /* K1, 0..1023; multiplied by hardware MASTER */
void dp_sfx_reset(void); /* enqueue a clear, processed by the consumer */
void dp_sfx_recover(void); /* consumer stopped: discard partial worker state */
void dp_sfx_render(int32_t *stereo,unsigned frames); /* signed 24-bit I2S words */
