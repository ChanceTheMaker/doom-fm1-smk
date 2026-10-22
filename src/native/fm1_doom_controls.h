/* SPDX-License-Identifier: GPL-3.0-only */
#pragma once
#include <stdint.h>
/* GameDude-style FM-1 layout, indexed chromatically from F3.
 * 0 left, 1 forward, 2 right, 3 back, 4 fire, 5 use, 6 menu,
 * 7 select, 8 run, 9 strafe left, 10 strafe right, 11 weapon.
 * Unmapped notes use -1. SMK keeps its existing mapping. */
static const int8_t dp_fm1_note_actions[27]={
 0,-1,0,1,3,1,2,2,-1,8,-1,6,7,-1,9,-1,10,-1,11,-1,-1,-1,-1,-1,5,-1,4
};
static inline uint32_t dp_fm1_actions(uint32_t notes,uint32_t buttons){
 uint32_t actions=0;
 for(unsigned n=0;n<27;n++)if((notes&(1u<<n))&&dp_fm1_note_actions[n]>=0)
  actions|=1u<<dp_fm1_note_actions[n];
 if(buttons&(1u<<12))actions|=1u<<6; /* PLAY = GameDude Select / Doom menu */
 if(buttons&(1u<<13))actions|=1u<<7; /* REC = GameDude Start / Doom select */
 return actions;
}
static inline uint32_t dp_fm1_lights(uint32_t actions){
 uint32_t lights=0;
 for(unsigned n=0;n<27;n++)if(dp_fm1_note_actions[n]>=0&&!(actions&(1u<<dp_fm1_note_actions[n])))lights|=1u<<n;
 return lights;
}
