/* SPDX-License-Identifier: GPL-3.0-only */
#include "sfx.h"
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
int main(void){int32_t out[256];
 for(unsigned effect=0;effect<DP_SFX_COUNT;effect++){
  dp_sfx_reset();dp_sfx_render(out,128);dp_sfx_master(1023);assert(dp_sfx_post(effect,127,4));unsigned active=0;
  for(int block=0;block<200;block++){dp_sfx_render(out,128);for(int i=0;i<256;i++){assert(abs(out[i])<=16000*128);if(out[i])active++;if(i%2)assert(out[i]==out[i-1]);}}
  assert(active>100);for(int i=0;i<256;i++)assert(out[i]==0);
 }
 dp_sfx_master(0);assert(dp_sfx_post(DP_BANG,127,9));dp_sfx_render(out,128);for(int i=0;i<256;i++)assert(out[i]==0);
 unsigned accepted=0;for(int i=0;i<100;i++)accepted+=dp_sfx_post(DP_BANG,127,5);assert(accepted==15);dp_sfx_render(out,128);
 assert(!dp_sfx_post(999,1,1));dp_sfx_reset();dp_sfx_render(out,128);for(int i=0;i<256;i++)assert(out[i]==0);
 puts("PASS effects: finite tails, stereo, mute, bounded mix, queue overflow, invalid event, reset");
}
