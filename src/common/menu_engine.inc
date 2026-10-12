/* SPDX-License-Identifier: GPL-3.0-only */
/* Appended to the generated m_menu.c; upstream input/menu state remain in charge. */
#include "menu_view.h"
static const struct {const char *patch,*label;} dp_labels[]={
 {"M_NGAME","NEW GAME"},{"M_OPTION","OPTIONS"},{"M_LOADG","LOAD GAME"},
 {"M_SAVEG","SAVE GAME"},{"M_RDTHIS","CONTROLS"},{"M_QUITG","QUIT GAME"},
 {"M_JKILL","TOO YOUNG TO DIE"},{"M_ROUGH","NOT TOO ROUGH"},{"M_HURT","HURT ME PLENTY"},
 {"M_ULTRA","ULTRA-VIOLENCE"},{"M_NMARE","NIGHTMARE"},
 {"M_EPI1","KNEE-DEEP IN DEAD"},{"M_EPI2","SHORES OF HELL"},
 {"M_EPI3","INFERNO"},{"M_EPI4","THY FLESH CONSUMED"},
 {"M_ENDGAM","END GAME"},{"M_MESSG","MESSAGES"},{"M_DETAIL","DETAIL"},
 {"M_SCRNSZ","SCREEN SIZE"},{"M_MSENS","MOUSE SENS"},{"M_SVOL","SOUND VOLUME"},
 {"M_SFXVOL","SOUND FX"},{"M_MUSVOL","MUSIC"}
};
static void dp_menu_line(dp_menu_view *v,const char *s) {
    if(v->count<DP_MENU_ROWS)snprintf(v->rows[v->count++],DP_MENU_COLS+1,"%s",s);
}
int dp_menu_snapshot(dp_menu_view *v) {
    memset(v,0,sizeof(*v));v->selected=-1;
    if(!menuactive&&!messageToPrint)return 0;
    snprintf(v->footer,sizeof(v->footer),"1 / 3 ADJUST     EXPERIMENTAL BUILD");
    if(messageToPrint) {
        v->message=1;snprintf(v->title,sizeof(v->title),"%s",messageNeedsInput?"CONFIRM":"NOTICE");
        const char *s=messageString;
        if(messageRoutine==M_QuitResponse)s="QUIT THE GAME?";
        else if(messageRoutine==M_EndGameResponse)s="END THIS GAME?";
        else if(messageRoutine==M_VerifyNightmare)s="START NIGHTMARE?";
        while(*s&&v->count<DP_MENU_ROWS) {
            while(*s==' '||*s=='\n')s++;
            if(!*s)break;
            unsigned n=0;while(s[n]&&s[n]!='\n'&&n<DP_MENU_COLS)n++;
            if(n==DP_MENU_COLS&&s[n]&&s[n]!=' '&&s[n]!='\n') {
                unsigned end=n;while(end&&s[end]!=' ')end--;if(end)n=end;
            }
            memcpy(v->rows[v->count],s,n);v->rows[v->count++][n]=0;s+=n;
        }
        snprintf(v->footer,sizeof(v->footer),"%s",messageNeedsInput?"8 YES / 7 NO":"8 OR 7 TO RETURN");return 1;
    }
    const char *title=currentMenu==&MainDef?"DOOM":currentMenu==&OptionsDef?"OPTIONS":
        currentMenu==&NewDef?"DIFFICULTY":currentMenu==&EpiDef?"EPISODE":
        currentMenu==&SoundDef?"SOUND":currentMenu==&SaveDef?"SAVE GAME":
        currentMenu==&LoadDef?"LOAD GAME":"CONTROLS";
    snprintf(v->title,sizeof(v->title),"%s",title);
    if(currentMenu==&ReadDef1||currentMenu==&ReadDef2) {
        v->message=1;dp_menu_line(v,"WHITE KEYS L TO R");dp_menu_line(v,"1 LEFT / 2 FORWARD");
        dp_menu_line(v,"3 RIGHT / 4 BACK");dp_menu_line(v,"5 FIRE / 6 USE");
        dp_menu_line(v,"7 MENU / 8 SELECT");dp_menu_line(v,"9 RUN / 10-11 STRAFE");return 1;
    }
    for(int i=0;i<currentMenu->numitems&&v->count<DP_MENU_ROWS;i++) {
        menuitem_t *item=&currentMenu->menuitems[i];if(item->status==-1)continue;
        if(i==itemOn)v->selected=v->count;
        char *line=v->rows[v->count++];const char *label=item->name;
        for(unsigned j=0;j<sizeof(dp_labels)/sizeof(dp_labels[0]);j++)
            if(!strcmp(item->name,dp_labels[j].patch)){label=dp_labels[j].label;break;}
        if(currentMenu==&SaveDef||currentMenu==&LoadDef)snprintf(line,DP_MENU_COLS+1,"%d %s",i+1,savegamestrings[i]);
        else if(currentMenu==&OptionsDef&&i==messages)snprintf(line,DP_MENU_COLS+1,"MESSAGES %s",showMessages?"ON":"OFF");
        else if(currentMenu==&OptionsDef&&i==detail)snprintf(line,DP_MENU_COLS+1,"DETAIL %s",detailLevel?"LOW":"HIGH");
        else if(currentMenu==&OptionsDef&&i==scrnsize)snprintf(line,DP_MENU_COLS+1,"SCREEN SIZE %d",screenSize);
        else if(currentMenu==&OptionsDef&&i==mousesens)snprintf(line,DP_MENU_COLS+1,"MOUSE SENS %d",mouseSensitivity);
        else if(currentMenu==&SoundDef)snprintf(line,DP_MENU_COLS+1,"%s %d",label,i==sfx_vol?sfxVolume:musicVolume);
        else snprintf(line,DP_MENU_COLS+1,"%s",label);
    }
    return 1;
}
