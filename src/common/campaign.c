/* SPDX-License-Identifier: GPL-3.0-only */
#include "campaign.h"
#include "sfx.h"
#include "doomstat.h"
#include "d_items.h"
#include <stdio.h>
#include <string.h>
unsigned dp_score;
static unsigned entry_score;
static int entered_map;
void dp_campaign_kill(unsigned points){if(dp_score<999000)dp_score+=points;}
void dp_campaign_reset(void){dp_score=entry_score=0;entered_map=0;}
void dp_campaign_load(void){dp_sfx_reset();if(entered_map==gamemap)dp_score=entry_score;else{entered_map=gamemap;entry_score=dp_score;}}
int dp_campaign_overlay(dp_menu_view *v){
 if(gamestate!=GS_INTERMISSION && (gamestate!=GS_LEVEL||players[consoleplayer].playerstate!=PST_DEAD))return 0;
 memset(v,0,sizeof(*v));v->selected=-1;v->message=1;
 snprintf(v->title,sizeof(v->title),"%s",gamestate==GS_LEVEL?"YOU DIED":gamemap==3?"CAMPAIGN CLEAR":"LEVEL COMPLETE");
 snprintf(v->rows[v->count++],20,"SCORE %u",dp_score);
 snprintf(v->rows[v->count++],20,"KILLS %d / %d",players[consoleplayer].killcount,totalkills);
 if(gamestate==GS_INTERMISSION){snprintf(v->rows[v->count++],20,"TIME %d SECONDS",(leveltime/35)%100000);snprintf(v->rows[v->count++],20,"%s",gamemap==3?"THREE LEVELS CLEAR":"NEXT SECTOR AHEAD");}
 snprintf(v->footer,sizeof(v->footer),"%s",gamestate==GS_LEVEL?"6 USE TO RETRY / 7 MENU":"5 FIRE OR 6 USE TO CONTINUE");
 return 1;
}
typedef struct {dp_row_sink sink;void *ctx;char score[20],level[12],status[32];} hud_context;
static int hud_row(void *opaque,unsigned y,const uint16_t *src,unsigned width){
 hud_context *c=opaque;if(y>=30&&y<210)return c->sink(c->ctx,y,src,width);
 uint16_t row[240];for(unsigned x=0;x<240;x++)row[x]=0;
 dp_text_row(row,y,8,8,c->score,2,0xffff);dp_text_row(row,y,180,8,c->level,2,0xfdc0);
 dp_text_row(row,y,8,218,c->status,2,0xffff);
 return c->sink(c->ctx,y,row,width);
}
int dp_campaign_present(const unsigned char *pixels,const unsigned short *palette,dp_row_sink sink,void *ctx){
 hud_context c={.sink=sink,.ctx=ctx};player_t *p=&players[consoleplayer];
 ammotype_t type=weaponinfo[p->readyweapon].ammo;int ammo=type<NUMAMMO?p->ammo[type]:0;
 snprintf(c.score,sizeof(c.score),"SCORE %06u",dp_score);snprintf(c.level,sizeof(c.level),"L%d/3",gamemap);
 snprintf(c.status,sizeof(c.status),"HP%d AM%d K%d/%d",p->health<0?0:p->health,ammo,p->killcount,totalkills);
 return dp_lcd_present(pixels,palette,hud_row,&c);
}
