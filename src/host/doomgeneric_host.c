/* SPDX-License-Identifier: GPL-3.0-only */
/* Bounded host renderer. No MIDI, USB or physical device access. */
#include "doomgeneric.h"
#include <stdio.h>
#include <time.h>
#include <errno.h>
#include <limits.h>
#include "memory_probe.h"
#include "doomstat.h"
#include "input_smoke.h"
#ifdef DP_STRIP
#include "i_video.h"
#include "lcd_frame.h"
#ifdef DP_READABLE_MENU
#include "menu_view.h"
#ifdef DP_CAMPAIGN
#include "campaign.h"
#include "splash.h"
void dp_bot_observe(int final);
void dp_audio_capture(int final);
int dp_bot_key(int *pressed,unsigned char *key);
#endif
#endif
extern struct color colors[256];
static uint16_t palette565[256];
#endif

static unsigned frames, limit = 120;
static struct timespec start;
static const char *output;

void DG_Init(void) {
    const char *value = getenv("DOOM_FRAME_LIMIT");
    if (value) {
        char *end; errno = 0;
        unsigned long n = strtoul(value, &end, 10);
        if (errno || end == value || *end || n < 1 || n > 100000) {
            fprintf(stderr, "DOOM_FRAME_LIMIT must be 1..100000\n"); exit(2);
        }
        limit = (unsigned)n;
    }
    output = getenv("DOOM_FRAME_OUTPUT");
    if (!output) output = "frame.ppm";
#ifndef DP_STRIP
    if (!DG_ScreenBuffer) exit(2);
#endif
    if (clock_gettime(CLOCK_MONOTONIC, &start)) exit(2);
    dp_input_init();
}
#ifdef DP_STRIP
static int write_row(void *ctx,unsigned y,const uint16_t *row,unsigned width) {
    (void)y;
    FILE *f=ctx;
    for(unsigned x=0;x<width;++x) {
        uint16_t c=row[x];
        unsigned r=(c>>11)&31,g=(c>>5)&63,b=c&31;
        unsigned char rgb[3]={(unsigned char)((r<<3)|(r>>2)),(unsigned char)((g<<2)|(g>>4)),(unsigned char)((b<<3)|(b>>2))};
        if(fwrite(rgb,1,3,f)!=3)return 0;
    }
    return 1;
}
/* Linker wrapper prevents upstream I_FinishUpdate from using an RGBA buffer. */
void __wrap_I_FinishUpdate(void) { DG_DrawFrame(); }
#endif
void DG_DrawFrame(void) {
#ifdef DP_TEXTURE_PROBE
    extern void DP_ExportTextureColumns(void);
    if(!frames)DP_ExportTextureColumns();
#endif
    dp_input_observe(frames+1>=limit);
#ifdef DP_CAMPAIGN
    dp_bot_observe(frames+1>=limit);
    dp_audio_capture(frames+1>=limit);
#endif
    if (++frames < limit) return;
    FILE *f = fopen(output, "wb");
    if (!f) { perror(output); exit(2); }
#ifdef DP_STRIP
    if (fprintf(f,"P6\n240 240\n255\n")<0)exit(2);
    for(unsigned i=0;i<256;++i)palette565[i]=(uint16_t)(((colors[i].r>>3)<<11)|((colors[i].g>>2)<<5)|(colors[i].b>>3));
#ifdef DP_READABLE_MENU
    dp_menu_view menu;
#ifdef DP_CAMPAIGN
    int active=dp_menu_snapshot(&menu)||dp_campaign_overlay(&menu);
    int ok=getenv("DOOM_SPLASH")?dp_splash_present(atoi(getenv("DOOM_SPLASH")),write_row,f):active?dp_menu_present(&menu,write_row,f):dp_campaign_present(I_VideoBuffer,palette565,write_row,f);
#else
    int ok=dp_menu_snapshot(&menu)?dp_menu_present(&menu,write_row,f):dp_lcd_present(I_VideoBuffer,palette565,write_row,f);
#endif
    const char *menu_report=getenv("DOOM_MENU_REPORT");
    if(menu_report){FILE *report=fopen(menu_report,"w");if(!report)exit(2);fprintf(report,"%s\n%d\n",menu.title,menu.selected);for(int i=0;i<menu.count;i++)fprintf(report,"%s\n",menu.rows[i]);fclose(report);}
#else
    int ok=dp_lcd_present(I_VideoBuffer,palette565,write_row,f);
#endif
    if(!ok){fclose(f);exit(2);}
#else
    if (fprintf(f, "P6\n%d %d\n255\n", DOOMGENERIC_RESX, DOOMGENERIC_RESY) < 0) exit(2);
    for (unsigned i = 0; i < DOOMGENERIC_RESX * DOOMGENERIC_RESY; ++i) {
        uint32_t c = DG_ScreenBuffer[i];
        unsigned char rgb[3] = { (unsigned char)(c >> 16), (unsigned char)(c >> 8), (unsigned char)c };
        if (fwrite(rgb, 1, 3, f) != 3) { perror("frame write"); fclose(f); exit(2); }
    }
#endif
    if (fclose(f)) { perror("frame close"); exit(2); }
    printf("Rendered %u host frames; saved %s\n", frames, output);
    dp_memory_report(frames, (int)gamestate);
    exit(0);
}
void DG_SleepMs(uint32_t ms) {
    struct timespec t = { ms / 1000, (long)(ms % 1000) * 1000000L };
    while (nanosleep(&t, &t) && errno == EINTR) {}
}
uint32_t DG_GetTicksMs(void) {
    struct timespec now;
    if (clock_gettime(CLOCK_MONOTONIC, &now)) exit(2);
    int64_t ns = (int64_t)(now.tv_sec - start.tv_sec) * 1000000000LL + now.tv_nsec - start.tv_nsec;
    return (uint32_t)(ns / 1000000LL);
}
int DG_GetKey(int *pressed, unsigned char *key) {
#ifdef DP_CAMPAIGN
 if(getenv("DOOM_CAMPAIGN_BOT"))return dp_bot_key(pressed,key);
#endif
 return dp_input_next(pressed,key);
}
void DG_SetWindowTitle(const char *title) { printf("%s\n", title); }
int main(int argc, char **argv) {
    doomgeneric_Create(argc, argv);
    for (;;) doomgeneric_Tick();
}
