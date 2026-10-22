#include <assert.h>
#include <stdio.h>
#include "../src/native/fm1_doom_controls.h"
int main(void){
 /* Independently stated physical contract: F3=0, final whites F5/G5=24/26. */
 const unsigned notes[]={0,2,3,5,4,6,7,24,26,11,12,9,14,16,18};
 const unsigned actions[]={0,0,1,1,3,2,2,5,4,6,7,8,9,10,11};
 uint32_t all=0;
 for(unsigned i=0;i<15;i++){assert(dp_fm1_actions(1u<<notes[i],0)==(1u<<actions[i]));all|=1u<<notes[i];}
 for(unsigned n=0;n<27;n++)if(!(all&(1u<<n)))assert(dp_fm1_actions(1u<<n,0)==0);
 assert(dp_fm1_actions(0,(1u<<12)|(1u<<13))==((1u<<6)|(1u<<7)));
 uint32_t chord=(1u<<3)|(1u<<26)|(1u<<9);assert(dp_fm1_actions(chord,0)==((1u<<1)|(1u<<4)|(1u<<8)));
 assert(dp_fm1_lights(0)==all);assert(dp_fm1_lights(4095)==0);
 /* Releasing one duplicate must not release the action or relight either key. */
 assert(dp_fm1_actions((1u<<0)|(1u<<2),0)==dp_fm1_actions(1u<<2,0));
 assert(!(dp_fm1_lights(dp_fm1_actions(1u<<2,0))&((1u<<0)|(1u<<2))));
 assert((dp_fm1_lights(1u<<4)&~(1u<<26))==(all&~(1u<<26)));
 puts("FM-1 GameDude layout, chord, duplicate-key release and light feedback passed");
}
