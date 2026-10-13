/* SPDX-License-Identifier: GPL-3.0-only */
/* Host only: exercise real overkill damage and every enemy sprite state. */
#include "p_local.h"
#include "r_local.h"
#include <assert.h>
extern void R_ProjectSprite(mobj_t *thing);
static void dp_sprite_regression(void) {
    const char *mode=getenv("DOOM_SPRITE_REGRESSION");
    if(!mode || gamestate!=GS_LEVEL || !players[consoleplayer].mo || leveltime<3)return;
    const mobjtype_t types[]={MT_POSSESSED,MT_TROOP};
    unsigned checked=0;
    for(unsigned i=0;i<2;i++) {
        if(strcmp(mode,"all") && strcmp(mode,i?"imp":"guard"))continue;
        mobj_t *mo=P_SpawnMobj(viewx+FixedMul(128*FRACUNIT,viewcos),
                              viewy+FixedMul(128*FRACUNIT,viewsin),ONFLOORZ,types[i]);
        P_DamageMobj(mo,players[consoleplayer].mo,players[consoleplayer].mo,
                     mo->info->spawnhealth*3+1);
        assert(mo->health < -mo->info->spawnhealth);
        assert(mo->state==&states[mo->info->xdeathstate]);
        printf("Checking %s real overkill state: sprite %d frame %d\n",i?"imp":"guard",mo->sprite,mo->frame);
        fflush(stdout);
        R_ClearSprites();R_ProjectSprite(mo);
        assert(vissprite_p==vissprites+1);
        for(int state=1;state<NUMSTATES;state++) {
            if(states[state].sprite!=(i?SPR_TROO:SPR_POSS))continue;
            mo->sprite=states[state].sprite;mo->frame=states[state].frame;
            R_ClearSprites();R_ProjectSprite(mo);
            assert(vissprite_p==vissprites+1);
            checked++;
        }
        P_RemoveMobj(mo);
    }
    assert(checked);
    printf("PASS: real overkill damage and %u projected enemy states\n",checked);
    exit(0);
}
