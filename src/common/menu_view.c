/* SPDX-License-Identifier: GPL-3.0-only */
#include "menu_view.h"
#include <string.h>
static const uint8_t glyphs[36][7]={
 {14,17,17,31,17,17,17},{30,17,17,30,17,17,30},{14,17,16,16,16,17,14},
 {30,17,17,17,17,17,30},{31,16,16,30,16,16,31},{31,16,16,30,16,16,16},
 {14,17,16,23,17,17,14},{17,17,17,31,17,17,17},{31,4,4,4,4,4,31},
 {7,2,2,2,18,18,12},{17,18,20,24,20,18,17},{16,16,16,16,16,16,31},
 {17,27,21,21,17,17,17},{17,25,21,19,17,17,17},{14,17,17,17,17,17,14},
 {30,17,17,30,16,16,16},{14,17,17,17,21,18,13},{30,17,17,30,20,18,17},
 {15,16,16,14,1,1,30},{31,4,4,4,4,4,4},{17,17,17,17,17,17,14},
 {17,17,17,17,17,10,4},{17,17,17,21,21,27,17},{17,17,10,4,10,17,17},
 {17,17,10,4,4,4,4},{31,1,2,4,8,16,31},
 {14,17,19,21,25,17,14},{4,12,4,4,4,4,14},{14,17,1,2,4,8,31},
 {30,1,1,14,1,1,30},{2,6,10,18,31,2,2},{31,16,16,30,1,1,30},
 {14,16,16,30,17,17,14},{31,1,2,4,8,8,8},{14,17,17,14,17,17,14},{14,17,17,15,1,1,14}
};

static unsigned glyph(unsigned ch,unsigned row) {
    if(ch>='a'&&ch<='z')ch-=32;
    if(ch>='A'&&ch<='Z')return glyphs[ch-'A'][row];
    if(ch>='0'&&ch<='9')return glyphs[ch-'0'+26][row];
    if(ch=='-')return row==3?14:0;
    if(ch==':')return row==2||row==5?4:0;
    if(ch=='/')return 1u<<(row*4/6);
    if(ch=='?'){static const unsigned char q[7]={14,17,1,2,4,0,4};return q[row];}
    if(ch==39)return row<2?4:0;
    if(ch=='.')return row==6?4:0;
    if(ch=='!')return row<4||row==6?4:0;
    if(ch=='(')return row==0||row==6?2:4;
    if(ch==')')return row==0||row==6?8:4;
    return 0;
}
void dp_text_row(uint16_t *row,unsigned y,int x,int top,const char *s,unsigned scale,uint16_t color) {
    if((int)y<top || (int)y>=top+(int)(7*scale))return;
    unsigned gy=(y-top)/scale;
    for(;*s;s++,x+=6*scale) {
        unsigned bits=glyph((unsigned char)*s,gy);
        for(unsigned c=0;c<5;c++)if(bits&(16u>>c))
            for(unsigned k=0;k<scale;k++) {
                int px=x+c*scale+k;if(px>=0&&px<DP_LCD_WIDTH)row[px]=color;
            }
    }
}
int dp_menu_present(const dp_menu_view *v,dp_row_sink sink,void *ctx) {
    if(!v||!sink||v->count<0||v->count>DP_MENU_ROWS)return 0;
    uint16_t row[DP_LCD_WIDTH];
    for(unsigned y=0;y<DP_LCD_HEIGHT;y++) {
        for(unsigned x=0;x<DP_LCD_WIDTH;x++)row[x]=0x0841;
        if(y==37||y==38)for(unsigned x=10;x<230;x++)row[x]=0xb986;
        int title_x=(DP_LCD_WIDTH-(int)strlen(v->title)*12)/2;
        dp_text_row(row,y,title_x,14,v->title,2,0xffff);
        unsigned step=v->count>6?19:25;
        for(int i=0;i<v->count;i++) {
            int top=49+i*step;
            int selected=!v->message&&i==v->selected;
            if(selected&&(int)y>=top-4&&(int)y<top+18)
                for(unsigned x=8;x<232;x++)row[x]=0xfdc0;
            dp_text_row(row,y,14,top,v->rows[i],2,selected?0:0xffff);
        }
        dp_text_row(row,y,10,215,v->footer,1,0xbdf7);
        dp_text_row(row,y,10,229,v->message?"":"2 UP / 4 DOWN / 8 SELECT / 7 CLOSE",1,0xbdf7);
        if(!sink(ctx,y,row,DP_LCD_WIDTH))return 0;
    }
    return 1;
}
