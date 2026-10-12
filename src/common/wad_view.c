/* SPDX-License-Identifier: GPL-3.0-only */
#include "wad_view.h"
#include <string.h>
static uint32_t le32(const uint8_t *p){return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
int dp_wad_validate(const uint8_t *p,size_t length) {
    if(!p||length<12||length>0x7fffffffU)return 0;
    if(memcmp(p,"IWAD",4)&&memcmp(p,"PWAD",4))return 0;
    uint32_t n=le32(p+4),dir=le32(p+8);
    if(n>65535||dir>length||n>(length-dir)/16)return 0;
    for(uint32_t i=0;i<n;++i) {
        const uint8_t *entry=p+dir+16*i;
        uint32_t off=le32(entry),bytes=le32(entry+4);
        if(off>length||bytes>length-off)return 0;
    }
    return 1;
}
