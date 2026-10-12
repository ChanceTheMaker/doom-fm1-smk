/* SPDX-License-Identifier: GPL-3.0-only */
/* The engine owns one indexed screen; no duplicate RGBA output framebuffer. */
#include "doomgeneric.h"
#include "m_argv.h"
pixel_t *DG_ScreenBuffer = NULL;
extern void M_FindResponseFile(void);
extern void D_DoomMain(void);
void doomgeneric_Create(int argc, char **argv) {
    myargc=argc; myargv=argv;
    M_FindResponseFile();
    DG_Init();
    D_DoomMain();
}
