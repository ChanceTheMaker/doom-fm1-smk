/* SPDX-License-Identifier: GPL-3.0-only */
#pragma once
#include "hal/smk37_analog_controls.h"

/* Physical order: top row 0..7, bottom row 8..15, left to right.
 * Values are bit positions in board.c's action_keys, not Doom key codes. */
static const uint8_t dp_pad_action[16]={9,1,10,255,255,255,255,255,
                                     0,3,2,255,255,255,5,4};
#define DP_PAD_MASK 0xc707u
typedef struct {
    smk37_pad_state_t pad[16];
    uint16_t held,pressed;
} dp_pads_t;
static inline void dp_pad_sample(dp_pads_t *s,unsigned p,unsigned raw){
    if(p>=16)return;
    smk37_pad_change_t c=smk37_pad_sample(&s->pad[p],raw);
    uint16_t bit=(uint16_t)(1u<<p);
    if(c.velocity){s->held|=bit;s->pressed|=bit;}
    if(c.release)s->held&=(uint16_t)~bit;
}
static inline uint32_t dp_pad_actions(uint16_t pads){
    uint32_t actions=0;
    for(unsigned p=0;p<16;p++)if((pads&(1u<<p))&&dp_pad_action[p]!=255)
        actions|=1u<<dp_pad_action[p];
    return actions;
}
static inline uint32_t dp_pad_merge(uint32_t *pending,uint32_t returned,
                                     uint16_t held,uint16_t pressed){
    *pending=(*pending|dp_pad_actions(pressed))&~returned;
    return dp_pad_actions(held)|*pending;
}
static inline void dp_pad_colors(uint32_t rgb[16],uint16_t held,unsigned level){
    if(level>255)level=255;
    for(unsigned p=0;p<16;p++){
        uint32_t color=0;
        if((DP_PAD_MASK&(1u<<p))&&!(held&(1u<<p))){
            if(p==0||p==2)color=(level<<16)|((level/2)<<8); /* amber strafe */
            else if(p>=14)color=(level<<16)|level; /* magenta Use / Fire */
            else color=((level*2/3)<<8)|level; /* cyan movement */
        }
        rgb[p]=color;
    }
}
