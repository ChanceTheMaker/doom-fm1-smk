/* SPDX-License-Identifier: GPL-3.0-only */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#define SMK37_LIGHT_MAX_LEVEL 255u
#include "../src/native/smk_doom_pads.h"
#include "../src/native/smk37_brightness.h"
#include "../src/native/hal/smk37_lights.h"
static unsigned decode(const uint8_t *p){
    unsigned v=0;
    for(unsigned i=0;i<24;i++){assert(p[i]==0xc0||p[i]==0xf0);v=(v<<1)|(p[i]==0xf0);}
    return v;
}
int main(void){
    /* Physical controls: top strafe/forward/strafe, bottom turn/back/turn,
     * then the final TWO pads (no skipped position) for Use and Fire. */
    assert(dp_pad_actions(1)==(1u<<9));assert(dp_pad_actions(2)==2);
    assert(dp_pad_actions(4)==(1u<<10));
    assert(dp_pad_actions(1u<<8)==1);assert(dp_pad_actions(1u<<9)==8);
    assert(dp_pad_actions(1u<<10)==4);
    assert(dp_pad_actions(1u<<14)==32);assert(dp_pad_actions(1u<<15)==16);
    assert(!dp_pad_actions((uint16_t)~DP_PAD_MASK));
    /* Each tap survives until its down event is consumed, including two
     * attacks/releases before Doom polls and chords held across frames. */
    dp_pads_t s={0};
    for(unsigned p=0;p<16;p++)dp_pad_sample(&s,p,20);
    assert(!s.held&&!s.pressed);
    dp_pad_sample(&s,0,100);dp_pad_sample(&s,0,0);
    dp_pad_sample(&s,15,200);dp_pad_sample(&s,15,0);
    assert(!s.held&&s.pressed==0x8001);
    uint32_t pending=0,returned=0,down=0,up=0;
    for(unsigned n=0;n<8;n++){
        uint32_t current=dp_pad_merge(&pending,returned,s.held,s.pressed);s.pressed=0;
        uint32_t changed=current^returned;
        if(!changed)break;
        uint32_t bit=changed&-changed;
        if(current&bit)down|=bit;else up|=bit;
        returned^=bit;
    }
    assert(down==((1u<<9)|(1u<<4))&&up==down&&!returned&&!pending);
    for(unsigned n=0;n<4;n++){dp_pad_sample(&s,1,180);dp_pad_sample(&s,15,400);}
    assert(s.held==0x8002);
    assert(dp_pad_merge(&pending,0,s.held,s.pressed)==18);
    s.pressed=0;assert(dp_pad_merge(&pending,18,s.held,0)==18);
    dp_pad_sample(&s,1,0);assert(dp_pad_merge(&pending,18,s.held,0)==16);
    dp_pad_sample(&s,15,0);assert(!dp_pad_merge(&pending,16,s.held,0));
    /* Every brightness and held-pad position passes through the real GRB
     * serializer; every unused pad must overwrite inherited colors with zero. */
    uint32_t rgb[16];uint8_t wire[SMK37_LIGHT_BYTES];
    for(unsigned level=0;level<=255;level++)for(unsigned held=0;held<=16;held++){
        memset(wire,0xff,sizeof wire);
        dp_pad_colors(rgb,held<16?(uint16_t)(1u<<held):0,level);
        smk37_light_encode_rgb(wire,rgb);
        for(unsigned i=0;i<SMK37_LIGHT_RESET_BYTES;i++)assert(!wire[i]);
        for(unsigned i=SMK37_LIGHT_RESET_BYTES+SMK37_LIGHT_COLOR_BYTES;i<SMK37_LIGHT_BYTES;i++)assert(!wire[i]);
        for(unsigned p=0;p<16;p++){
            unsigned c=rgb[p];
            if(!(DP_PAD_MASK&(1u<<p))||held==p)assert(!c);
            else if(p==0||p==2)assert(c==((level<<16)|((level/2)<<8)));
            else if(p==14)assert(c==(level<<8));
            else if(p==15)assert(c==(level<<16));
            else assert(c==(((level*2/3)<<8)|level));
            assert(decode(wire+SMK37_LIGHT_RESET_BYTES+24*smk37_pad_light_order[p])==(((c>>8)&255)<<16|((c>>16)&255)<<8|(c&255)));
        }
    }
    smk_brightness_t f={0};unsigned level=150;
    for(unsigned i=0;i<24;i++)if(i!=18)assert(smk_brightness_sample(&f,150,i,1023)==150&&!f.ready);
    assert(smk_brightness_sample(&f,150,18,500)==150);
    assert(smk_brightness_sample(&f,150,18,507)==150&&!f.active);
    for(unsigned n=0;n<100;n++)assert(smk_brightness_sample(&f,150,18,508)==150&&!f.active);
    for(unsigned n=0;n<24;n++)level=smk_brightness_sample(&f,level,18,560);
    assert(f.active&&level>130&&level<145);
    for(unsigned n=0;n<32;n++)level=smk_brightness_sample(&f,level,18,0);
    assert(level==0);
    for(unsigned n=0;n<32;n++)level=smk_brightness_sample(&f,level,18,1023);
    assert(level==255);
    /* Replay measured idle jitter and short dips: no takeover from 150. */
    f=(smk_brightness_t){0};level=150;
    const unsigned noise[]={222,224,219,222,215,222,223,222,219,224,222};
    for(unsigned n=0;n<2000;n++){
        level=smk_brightness_sample(&f,level,18,noise[n%11]);
        assert(level==150&&!f.active);
    }
    /* Deliberate movement still takes over; the same noise stays steady
     * once the fader has settled at its approximately 54/255 position. */
    for(unsigned n=0;n<32;n++)level=smk_brightness_sample(&f,level,18,400);
    assert(f.active);
    for(unsigned n=0;n<32;n++)level=smk_brightness_sample(&f,level,18,222);
    unsigned settled=level;
    for(unsigned n=0;n<2000;n++){
        level=smk_brightness_sample(&f,level,18,noise[n%11]);
        assert(level==settled);
    }
    puts("PASS: physical Doom pads, chords, retained short taps, releases, all LED colors/positions/brightness and F2 isolation");
}
