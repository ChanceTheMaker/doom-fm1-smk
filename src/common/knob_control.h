/* SPDX-License-Identifier: GPL-3.0-only */
#pragma once
/* SMK reports quarter transitions, FM-1 reports complete detents. */
typedef struct { int volume,menu,phase[2]; } dp_knobs;
static inline int dp_knob_turn(dp_knobs *s,unsigned knob,int delta,int transitions) {
    if(knob>1)return 0;
    int phase=s->phase[knob]+delta,steps=phase/transitions;
    s->phase[knob]=phase%transitions;
    if(!steps)return 0;
    if(!knob){
        s->volume+=steps*32;
        if(s->volume<0)s->volume=0;
        if(s->volume>1023)s->volume=1023;
    }else{
        s->menu+=steps;
        if(s->menu< -16)s->menu=-16;
        if(s->menu>16)s->menu=16;
    }
    return 1;
}
