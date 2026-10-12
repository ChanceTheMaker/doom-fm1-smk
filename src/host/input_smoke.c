/* SPDX-License-Identifier: GPL-3.0-only */
/* Host-only deterministic exercise through DoomGeneric's normal key events. */
#include "input_smoke.h"
#include "doomstat.h"
#include "doomkeys.h"
#include "d_event.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int enabled, started, start_tic, x, y, bullets;
static unsigned angle, next_event;
static const struct { int tic, down; unsigned char key; } events[] = {
    {10,1,KEY_UPARROW}, {30,0,KEY_UPARROW},
    {40,1,KEY_RIGHTARROW}, {50,0,KEY_RIGHTARROW},
    {60,1,KEY_FIRE}, {100,0,KEY_FIRE}
};

void dp_input_init(void) {
    const char *mode=getenv("DOOM_INPUT_SMOKE");
    enabled=mode && strcmp(mode,"1")==0;
    /* Measurement runs can also use this to remove wall-clock variability. */
    const char *fixed=getenv("DOOM_FIXED_TICS");
    if(enabled || (fixed && strcmp(fixed,"1")==0)) singletics=true;
}
int dp_input_next(int *pressed,unsigned char *key) {
    if(!enabled || !started || next_event>=sizeof(events)/sizeof(events[0]) ||
       gametic-start_tic<events[next_event].tic) return 0;
    *pressed=events[next_event].down;
    *key=events[next_event++].key;
    return 1;
}
void dp_input_observe(int final) {
    if(!enabled) return;
    player_t *p=&players[consoleplayer];
    if(gamestate==GS_LEVEL && p->mo && !started) {
        started=1;start_tic=gametic;
        x=p->mo->x;y=p->mo->y;angle=p->mo->angle;bullets=p->ammo[am_clip];
    }
    if(!final) return;
    const char *path=getenv("DOOM_INPUT_REPORT");
    if(!path)path="input.json";
    FILE *f=fopen(path,"w");
    if(!f){perror(path);exit(2);}
    int valid=started && gamestate==GS_LEVEL && p->mo;
    fprintf(f,"{\n  \"events_delivered\": %u,\n  \"ticks_elapsed\": %d,\n"
        "  \"moved\": %s,\n  \"turned\": %s,\n  \"fired\": %s,\n"
        "  \"controls_released\": %s,\n  \"bullets_before\": %d,\n  \"bullets_after\": %d\n}\n",
        next_event,started?gametic-start_tic:0,
        valid && (x!=p->mo->x || y!=p->mo->y)?"true":"false",
        valid && angle!=p->mo->angle?"true":"false",
        valid && bullets>p->ammo[am_clip]?"true":"false",
        valid && next_event==6 && !p->cmd.forwardmove && !p->cmd.sidemove &&
            !p->cmd.angleturn && !(p->cmd.buttons&BT_ATTACK)?"true":"false",
        bullets,valid?p->ammo[am_clip]:0);
    if(fclose(f)){perror("input report");exit(2);}
}
