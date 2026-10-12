/* SPDX-License-Identifier: GPL-3.0-only */
#include "doomstat.h"
#include "sounds.h"
#include "sfx.h"
/* Compact original synthesized effects; no PCM lumps or dynamic sound buffers. */
void dp_game_sound(void *origin,int id,int volume){
 unsigned kind,priority=1;
 switch(id){
 case sfx_shotgn:case sfx_dshtgn:kind=DP_BANG;priority=5;break;
 case sfx_pistol:case sfx_chgun:kind=DP_BANG;priority=3;break;
 case sfx_sgcock:case sfx_dbopn:case sfx_dbcls:case sfx_dbload:kind=DP_PUMP;priority=4;break;
 case sfx_posit1:case sfx_posit2:case sfx_posit3:case sfx_bgsit1:case sfx_bgsit2:case sfx_posact:case sfx_bgact:kind=DP_GROWL;break;
 case sfx_plpain:case sfx_oof:kind=DP_HURT;priority=5;break;
 case sfx_popain:case sfx_dmpain:kind=DP_HURT;priority=2;break;
 case sfx_pldeth:case sfx_pdiehi:case sfx_podth1:case sfx_podth2:case sfx_podth3:case sfx_bgdth1:case sfx_bgdth2:kind=DP_DEATH;priority=3;break;
 case sfx_itemup:case sfx_wpnup:kind=DP_PICKUP;priority=4;break;
 case sfx_swtchn:case sfx_swtchx:case sfx_noway:case sfx_pstop:kind=DP_SWITCH;priority=2;break;
 case sfx_firsht:kind=DP_FIREBALL;priority=3;break;
 case sfx_firxpl:case sfx_claw:case sfx_punch:kind=DP_HIT;priority=3;break;
 default:return;
 }
 if(volume<=0)return;if(volume>127)volume=127;
 mobj_t *m=origin,*p=players[consoleplayer].mo;
 if(m&&p&&m!=p){int dx=(m->x-p->x)/FRACUNIT,dy=(m->y-p->y)/FRACUNIT;
  unsigned dist=(dx<0?-dx:dx)+(dy<0?-dy:dy);
  if(dist>=1000)return;volume=volume*(int)(1000-dist)/1000;
 }
 dp_sfx_post(kind,(unsigned)volume,priority);
}
