/* SPDX-License-Identifier: GPL-3.0-only */
#include "wad_view.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
int main(void){
 uint8_t wad[32]={0};memcpy(wad,"IWAD",4);wad[4]=1;wad[8]=16;wad[16]=12;wad[20]=4;
 assert(dp_wad_validate(wad,sizeof wad));
 assert(!dp_wad_validate(wad,11));assert(!dp_wad_validate(0,32));
 wad[0]='X';assert(!dp_wad_validate(wad,32));wad[0]='I';
 wad[8]=31;assert(!dp_wad_validate(wad,32));wad[8]=16;
 wad[4]=255;assert(!dp_wad_validate(wad,32));wad[4]=1;
 wad[16]=31;assert(!dp_wad_validate(wad,32));wad[16]=12;
 wad[23]=128;assert(!dp_wad_validate(wad,32));wad[23]=0;
 wad[16]=32;wad[20]=0;assert(dp_wad_validate(wad,32));
 puts("WAD: valid ranges, truncated headers, overflow and invalid directory/lumps passed");
}
