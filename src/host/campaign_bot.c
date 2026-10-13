/* SPDX-License-Identifier: GPL-3.0-only */
/* Host-only playthrough driver. Uses ordinary key events, never changes game state. */
#include "doomstat.h"
#include "doomkeys.h"
#include "p_local.h"
#include "campaign.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
extern int detailLevel;
static int observed;
static int desired[256],held[256],lastmap,waypoint,visited,completions,deaths;
static int was_intermission,was_dead,peak_score,total_kills,lastkills;
static const int routes[DP_CAMPAIGN_LEVELS][8][2]={
 {{704,192},{704,704},{192,704},{192,192},{704,192},{704,704},{704,864}},
 {{1216,192},{1216,352},{1216,352},{1216,352}},
 {{704,192},{704,704},{1216,704},{1216,864}},
 {{704,192},{704,704},{192,704},{192,864}},
 {{192,192},{192,704},{704,704},{704,1216},{704,1376}},
 {{704,192},{704,704},{192,704},{192,864}},
 {{704,192},{1216,192},{1728,192},{1728,352}},
 {{192,192},{192,704},{-320,704},{-320,1216},{-320,1376}},
 {{704,192},{704,704},{1216,704},{1216,192},{1216,704},{1216,864}}};
static const int route_len[DP_CAMPAIGN_LEVELS]={7,2,4,4,5,4,4,5,6};
void dp_bot_observe(int final){
 if(!getenv("DOOM_CAMPAIGN_BOT"))return;
 player_t *p=&players[consoleplayer];memset(desired,0,sizeof(desired));
 if((int)dp_score>peak_score)peak_score=dp_score;
 int dead=p->playerstate==PST_DEAD,inter=gamestate==GS_INTERMISSION;
 if(dead&&!was_dead)deaths++;
 if(inter&&!was_intermission)completions++;
 was_dead=dead;was_intermission=inter;
 if(gamestate==GS_LEVEL&&p->mo&&gamemap>=1&&gamemap<=DP_CAMPAIGN_LEVELS){
  visited|=1<<(gamemap-1);
  if(lastmap!=gamemap){waypoint=0;lastmap=gamemap;lastkills=0;}
  if(p->killcount>lastkills)total_kills+=p->killcount-lastkills;
  lastkills=p->killcount;
  if(dead)desired[KEY_USE]=(gametic/20)%2;
  else if(strcmp(getenv("DOOM_CAMPAIGN_BOT"),"idle")){
   double x=p->mo->x/65536.,y=p->mo->y/65536.;
   const int (*route)[2]=routes[gamemap-1];
   double dx=route[waypoint][0]-x,dy=route[waypoint][1]-y;
   if(hypot(dx,dy)<28&&waypoint<route_len[gamemap-1]-1){waypoint++;dx=route[waypoint][0]-x;dy=route[waypoint][1]-y;}
   mobj_t *enemy=NULL;double nearest=640;
   for(thinker_t *th=thinkercap.next;th!=&thinkercap;th=th->next){
    if(th->function.acp1!=(actionf_p1)P_MobjThinker)continue;
    mobj_t *mo=(mobj_t*)th;
    if(!(mo->flags&MF_COUNTKILL)||mo->health<=0||!P_CheckSight(p->mo,mo))continue;
    double d=hypot(mo->x/65536.-x,mo->y/65536.-y);if(d<nearest){nearest=d;enemy=mo;}
   }
   if(enemy){dx=enemy->x/65536.-x;dy=enemy->y/65536.-y;}
   else if(waypoint==route_len[gamemap-1]-1&&hypot(dx,dy)<28){dx=0;dy=64;desired[KEY_USE]=(gametic/12)%2;}
   double angle=p->mo->angle*(6.283185307179586/4294967296.);
   double error=atan2(dy,dx)-angle;while(error>3.14159265)error-=6.283185307;while(error< -3.14159265)error+=6.283185307;
   if(error>0.035)desired[KEY_LEFTARROW]=1;else if(error< -0.035)desired[KEY_RIGHTARROW]=1;
   if(enemy){if(fabs(error)<0.09)desired[KEY_FIRE]=1;}
   else if(fabs(error)<0.15){desired[KEY_UPARROW]=1;desired[KEY_USE]=gametic%140==0;}
  }
 }else if(inter)desired[KEY_FIRE]=(gametic/20)%2;
 if(getenv("DOOM_BOT_LOW_DETAIL") && observed++==0)desired[KEY_F5]=1;
 if(final){
  const char *path=getenv("DOOM_CAMPAIGN_REPORT");FILE *f=fopen(path?path:"campaign.json","w");if(!f)exit(2);
  fprintf(f,"{\"detail\":%d,\"skill\":%d,\"maps\":%d,\"completions\":%d,\"deaths\":%d,\"kills\":%d,\"peak_score\":%d,\"score\":%u,\"map\":%d,\"health\":%d,\"shells\":%d,\"x\":%d,\"y\":%d,\"waypoint\":%d,\"state\":%d}\n",detailLevel,gameskill,visited,completions,deaths,total_kills,peak_score,dp_score,gamemap,p->health,p->ammo[am_shell],p->mo?p->mo->x/65536:0,p->mo?p->mo->y/65536:0,waypoint,gamestate);fclose(f);
 }
}
int dp_bot_key(int *pressed,unsigned char *key){for(int i=0;i<256;i++)if(desired[i]!=held[i]){*key=i;*pressed=held[i]=desired[i];return 1;}return 0;}
