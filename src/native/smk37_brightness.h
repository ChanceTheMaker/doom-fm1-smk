/* SPDX-License-Identifier: (GPL-3.0-only OR MPL-2.0) */
#pragma once
#include <stdint.h>
#include "hal/smk37_analog_controls.h"
typedef struct {uint16_t initial,filtered;uint8_t ready,active,movement;} smk_brightness_t;
/* Keep startup brightness until sustained Fader 2 movement. Hardware captured
 * raw 215..224 at rest: an 8-count single-sample threshold armed spuriously.
 * Smooth over four samples; require three filtered readings 16 counts from
 * startup. The same smoothing rejects brief dips after takeover. */
static inline uint32_t smk_brightness_sample(smk_brightness_t *s,uint32_t previous,unsigned input,unsigned raw){
    if(input!=smk37_fader_input[1])return previous;
    if(raw>1023)raw=1023;
    if(!s->ready){s->initial=(uint16_t)raw;s->filtered=(uint16_t)(raw*16);s->ready=1;return previous;}
    int filter_delta=(int)(raw*16)-(int)s->filtered;
    s->filtered=(uint16_t)((int)s->filtered+filter_delta/4);
    raw=(s->filtered+8u)/16u;
    if(!s->active){
        unsigned delta=raw>s->initial?raw-s->initial:s->initial-raw;
        if(delta<16){s->movement=0;return previous;}
        if(++s->movement<3)return previous;
        s->active=1;
    }
    uint32_t level=raw<=8?0:raw>=1015?255:(raw-8)*255/1007;
    unsigned delta=level>previous?level-previous:previous-level;
    return !level||level==255||delta>=2?level:previous;
}
