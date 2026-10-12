/* SPDX-License-Identifier: GPL-3.0-only */
#include "music.h"
#include "sfx.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int32_t baseline[8192],out[8192];
static void silence(unsigned frames){dp_sfx_render(out,frames);for(unsigned i=0;i<frames*2;i++)assert(out[i]==0);}
int main(void){
 dp_sfx_master(1023);silence(128); /* opt-in, no startup noise */
 dp_music_start();dp_music_volume(127);dp_sfx_render(baseline,4096);
 unsigned active=0;for(unsigned i=0;i<8192;i++)active+=baseline[i]!=0;assert(active>8000);
 dp_music_start();dp_sfx_render(out,2049);assert(!memcmp(out,baseline,4098*sizeof(int32_t)));
 dp_music_pause(1);silence(128);silence(128);
 dp_music_pause(0);dp_sfx_render(out,2047);assert(!memcmp(out,baseline+4098,4094*sizeof(int32_t)));
 dp_music_volume(0);silence(128);
 dp_music_volume(999);dp_music_start();dp_sfx_render(out,4096);assert(!memcmp(out,baseline,sizeof(out)));
 dp_sfx_master(0);silence(128);dp_sfx_master(1023);
 /* Across multiple loop boundaries, effects remain audible and bounded. */
 int64_t energy=0;for(unsigned block=0;block<1500;block++){
  if(block%37==0)assert(dp_sfx_post(DP_BANG,127,5));
  dp_sfx_render(out,1024);
  for(unsigned i=0;i<2048;i+=2){assert(out[i]==out[i+1]);assert(abs(out[i])<=16000*128);energy+=abs(out[i]);}
 }
 assert(energy>1000000);
 dp_music_stop();dp_sfx_reset();silence(128);
 dp_music_start();dp_sfx_render(out,4096);assert(!memcmp(out,baseline,sizeof(out)));
 puts("PASS original music: opt-in, deterministic restart, pause/resume, volume, master mute, loop endurance, effects mix and stop");
}
