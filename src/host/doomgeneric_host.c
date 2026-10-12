/* SPDX-License-Identifier: GPL-3.0-only */
/* Bounded host renderer. No MIDI, USB or physical device access. */
#include "doomgeneric.h"
#include <stdio.h>
#include <time.h>
#include <errno.h>
#include <limits.h>

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
    if (!DG_ScreenBuffer || clock_gettime(CLOCK_MONOTONIC, &start)) exit(2);
}
void DG_DrawFrame(void) {
    if (++frames < limit) return;
    FILE *f = fopen(output, "wb");
    if (!f) { perror(output); exit(2); }
    if (fprintf(f, "P6\n%d %d\n255\n", DOOMGENERIC_RESX, DOOMGENERIC_RESY) < 0) exit(2);
    for (unsigned i = 0; i < DOOMGENERIC_RESX * DOOMGENERIC_RESY; ++i) {
        uint32_t c = DG_ScreenBuffer[i];
        unsigned char rgb[3] = { (unsigned char)(c >> 16), (unsigned char)(c >> 8), (unsigned char)c };
        if (fwrite(rgb, 1, 3, f) != 3) { perror("frame write"); fclose(f); exit(2); }
    }
    if (fclose(f)) { perror("frame close"); exit(2); }
    printf("Rendered %u host frames; saved %s\n", frames, output);
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
int DG_GetKey(int *pressed, unsigned char *key) { (void)pressed; (void)key; return 0; }
void DG_SetWindowTitle(const char *title) { printf("%s\n", title); }
int main(int argc, char **argv) {
    doomgeneric_Create(argc, argv);
    for (;;) doomgeneric_Tick();
}
