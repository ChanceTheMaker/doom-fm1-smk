/* SPDX-License-Identifier: GPL-3.0-only */
/* Read-only virtual filesystem exposing only the embedded test WAD. */
#include "platform.h"
#include <sys/stat.h>
#include <sys/types.h>
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <string.h>
#include <stddef.h>
extern const unsigned char dp_wad_start[],dp_wad_end[];
static unsigned position;
static int opened;
int _open(const char *name,int flags,...){
    if(strcmp(name,"miniwad.wad") || (flags&O_ACCMODE)!=O_RDONLY || (flags&(O_CREAT|O_TRUNC|O_APPEND))){errno=ENOENT;return -1;}
    if(opened){errno=EMFILE;return -1;}opened=1;position=0;return 3;
}
int _close(int fd){if(fd==3){opened=0;return 0;}errno=EBADF;return -1;}
int _read(int fd,void *dst,size_t n){
    if(fd!=3||!opened){errno=EBADF;return -1;}
    size_t size=dp_wad_end-dp_wad_start;if(n>size-position)n=size-position;
    memcpy(dst,dp_wad_start+position,n);position+=n;return n;
}
int _write(int fd,const void *p,size_t n){(void)p;if(fd==1||fd==2)return n;errno=EROFS;return -1;}
off_t _lseek(int fd,off_t off,int whence){
    if(fd!=3||!opened){errno=EBADF;return -1;}
    int64_t next=off;if(whence==1)next+=position;else if(whence==2)next+=dp_wad_end-dp_wad_start;else if(whence!=0){errno=EINVAL;return -1;}
    if(next<0||next>dp_wad_end-dp_wad_start){errno=EINVAL;return -1;}position=next;return position;
}
int _fstat(int fd,struct stat *s){memset(s,0,sizeof *s);if(fd<3){s->st_mode=S_IFCHR;return 0;}if(fd==3&&opened){s->st_mode=S_IFREG;s->st_size=dp_wad_end-dp_wad_start;return 0;}errno=EBADF;return -1;}
int _stat(const char *name,struct stat *s){if(strcmp(name,"miniwad.wad")){errno=ENOENT;return -1;}memset(s,0,sizeof *s);s->st_mode=S_IFREG;s->st_size=dp_wad_end-dp_wad_start;return 0;}
int _isatty(int fd){return fd<3;}
int _unlink(const char *s){(void)s;errno=EROFS;return -1;}
int _link(const char *a,const char *b){(void)a;(void)b;errno=EROFS;return -1;}
int _getpid(void){return 1;}
int _kill(int p,int sig){(void)p;(void)sig;errno=EINVAL;return -1;}
void _exit(int code){(void)code;dp_panic("PROGRAM EXIT");}
int mkdir(const char *path,mode_t mode){(void)path;(void)mode;errno=EROFS;return -1;}
