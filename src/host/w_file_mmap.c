/* SPDX-License-Identifier: GPL-3.0-only */
/* Host model of immutable XIP WAD access. No hardware flash mapping here. */
#include "w_file.h"
#include "wad_view.h"
#include "z_zone.h"
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
extern wad_file_class_t stdc_wad_file;
static wad_file_t *open_wad(char *path) {
    int fd=open(path,O_RDONLY);
    if(fd<0)return NULL;
    struct stat st;
    if(fstat(fd,&st)||st.st_size<12||st.st_size>0x7fffffff){close(fd);return NULL;}
    size_t size=(size_t)st.st_size;
    void *ptr=mmap(NULL,size,PROT_READ,MAP_PRIVATE,fd,0);close(fd);
    if(ptr==MAP_FAILED)return NULL;
    if(!dp_wad_validate(ptr,size)){munmap(ptr,size);return NULL;}
    wad_file_t *wad=Z_Malloc(sizeof(*wad),PU_STATIC,0);
    wad->file_class=&stdc_wad_file;wad->mapped=ptr;wad->length=(unsigned)size;
    return wad;
}
static void close_wad(wad_file_t *wad){munmap(wad->mapped,wad->length);Z_Free(wad);}
static size_t read_wad(wad_file_t *wad,unsigned offset,void *out,size_t size) {
    if(offset>wad->length)return 0;
    if(size>wad->length-offset)size=wad->length-offset;
    memcpy(out,wad->mapped+offset,size);return size;
}
wad_file_class_t stdc_wad_file={open_wad,close_wad,read_wad};
