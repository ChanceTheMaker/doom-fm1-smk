/* SPDX-License-Identifier: GPL-3.0-only */
#include "knob_control.h"
#include "sfx.h"
#include "music.h"
#include <assert.h>
#include <stdio.h>
int main(void){
 dp_knobs smk={512,0,{0,0}},fm1={512,0,{0,0}};
 for(int i=0;i<4;i++)dp_knob_turn(&smk,0,1,4);
 dp_knob_turn(&fm1,0,1,1);assert(smk.volume==544&&smk.volume==fm1.volume);
 dp_knob_turn(&smk,1,1,4);dp_knob_turn(&smk,1,-1,4);assert(smk.menu==0);
 for(int i=0;i<4;i++)dp_knob_turn(&smk,1,-1,4);assert(smk.menu==-1);
 dp_knob_turn(&fm1,0,-1000,1);assert(fm1.volume==0);
 dp_knob_turn(&fm1,0,1000,1);assert(fm1.volume==1023);
 dp_knob_turn(&fm1,1,1000,1);assert(fm1.menu==16);
 int32_t out[256];dp_music_start();dp_music_volume(127);dp_sfx_master(1023);
 dp_sfx_trim(0);dp_sfx_post(DP_BANG,127,9);dp_sfx_render(out,128);
 for(int i=0;i<256;i++)assert(!out[i]);
 dp_sfx_trim(1023);dp_sfx_render(out,128);int audible=0;
 for(int i=0;i<256;i++)audible|=out[i]!=0;assert(audible);
 dp_sfx_master(0);dp_sfx_render(out,128);for(int i=0;i<256;i++)assert(!out[i]);
 puts("PASS K1 clamp/mute/music+effects, MASTER mute, K2 detents and bounce cancellation");
}
