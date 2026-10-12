/* SPDX-License-Identifier: GPL-3.0-only */
#include "w_file.h"
#include "wad_view.h"
#include <string.h>
extern const unsigned char dp_wad_start[],dp_wad_end[];
extern wad_file_class_t stdc_wad_file;
static wad_file_t file;
static wad_file_t *open_wad(char *path){
    if(strcmp(path,"miniwad.wad") || !dp_wad_validate(dp_wad_start,dp_wad_end-dp_wad_start))return NULL;
    file.file_class=&stdc_wad_file;file.mapped=(byte *)dp_wad_start;file.length=dp_wad_end-dp_wad_start;return &file;
}
static void close_wad(wad_file_t *f){(void)f;}
static size_t read_wad(wad_file_t *f,unsigned off,void *out,size_t n){if(off>f->length)return 0;if(n>f->length-off)n=f->length-off;memcpy(out,f->mapped+off,n);return n;}
wad_file_class_t stdc_wad_file={open_wad,close_wad,read_wad};
