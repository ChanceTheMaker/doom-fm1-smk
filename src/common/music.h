/* SPDX-License-Identifier: GPL-3.0-only */
#pragma once

/* Main-thread controls. A single packed word crosses to the audio IRQ. */
void dp_music_start(void);
void dp_music_stop(void);
void dp_music_pause(int paused);
void dp_music_volume(unsigned volume); /* Doom menu range: 0..127 */

/* Audio consumer only, shared by native, host and browser renderers. */
void dp_music_begin(void);
void dp_music_recover(void); /* only after stopping the audio consumer */
int dp_music_sample(void);
