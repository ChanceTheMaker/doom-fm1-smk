/* SPDX-License-Identifier: GPL-3.0-only */
#include "memory_probe.h"
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
static uint32_t peak_allocated,peak_nonpurgeable;
extern void *__real_Z_Malloc(int size,int tag,void *user);
void *__wrap_Z_Malloc(int size,int tag,void *user) {
    void *p=__real_Z_Malloc(size,tag,user);
    dp_zone_snapshot s;dp_read_zone(&s);
    if(s.allocated>peak_allocated) peak_allocated=s.allocated;
    if(s.nonpurgeable>peak_nonpurgeable) peak_nonpurgeable=s.nonpurgeable;
    return p;
}
unsigned char *__wrap_I_ZoneBase(int *size) {
    const char *value=getenv("DOOM_ZONE_KIB");
    unsigned long kib=16384;
    if (value) {
        char *end;errno=0;kib=strtoul(value,&end,10);
        if(errno||end==value||*end||kib<64||kib>65536) {
            fputs("DOOM_ZONE_KIB must be 64..65536\n",stderr);exit(2);
        }
    }
    *size=(int)(kib*1024);
    unsigned char *p=malloc((size_t)*size);
    if(!p) {fputs("zone allocation failed\n",stderr);exit(2);}
    printf("Host test zone: %u bytes\n",(unsigned)*size);
    return p;
}
void dp_memory_report(unsigned frames,int gamestate) {
    dp_zone_snapshot s;dp_read_zone(&s);
    const char *name=getenv("DOOM_MEMORY_REPORT");if(!name)name="memory.json";
    FILE *f=fopen(name,"w");if(!f){perror(name);exit(2);}
#ifdef DP_STRIP
    const char *display="rgb565-strip";unsigned output=0,strip=480,palette=512;
#else
    const char *display="rgba";unsigned output=256000,strip=0,palette=0;
#endif
    fprintf(f,"{\n  \"frames\": %u,\n  \"gamestate\": %d,\n  \"display\": \"%s\",\n  \"zone_capacity_bytes\": %u,\n  \"zone_peak_allocated_bytes\": %u,\n  \"zone_peak_nonpurgeable_bytes\": %u,\n  \"zone_final_allocated_bytes\": %u,\n  \"output_framebuffer_bytes\": %u,\n  \"rgb565_strip_bytes\": %u,\n  \"rgb565_palette_bytes\": %u,\n  \"scope\": \"host zone and display only; excludes other heap, stack and static data\"\n}\n",frames,gamestate,display,s.capacity,peak_allocated,peak_nonpurgeable,s.allocated,output,strip,palette);
    if(fclose(f)){perror("memory report");exit(2);}
    printf("Zone peaks: %u allocated; %u nonpurgeable bytes\n",peak_allocated,peak_nonpurgeable);
}
