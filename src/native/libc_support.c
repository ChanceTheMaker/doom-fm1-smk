/* SPDX-License-Identifier: GPL-3.0-only */
/* Narrow freestanding runtime for Doom: bounded heap and read-only stdio. */
#include "platform.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <stdint.h>
#include <errno.h>
#include <fcntl.h>
typedef struct block {size_t size;struct block *next;unsigned available,reserved;} block;
static unsigned char arena[24*1024] __attribute__((aligned(8),section(".lowheap")));
static block *head;
void *malloc(size_t n){
    if(!n)n=1;if(n>sizeof(arena)-sizeof(block)-7)return NULL;n=(n+7)&~(size_t)7;
    if(!head){head=(block *)arena;head->size=sizeof(arena)-sizeof(block);head->available=1;head->next=NULL;}
    for(block *b=head;b;b=b->next)if(b->available && b->size>=n){
        if(b->size>=n+sizeof(block)+8){block *rest=(block *)((unsigned char *)(b+1)+n);rest->size=b->size-n-sizeof(block);rest->available=1;rest->next=b->next;b->next=rest;b->size=n;}
        b->available=0;return b+1;
    }
    errno=ENOMEM;return NULL;
}
void free(void *p){
    if(!p)return;block *found=NULL;
    for(block *b=head;b;b=b->next)if(b+1==p){found=b;break;}
    if(!found||found->available)dp_panic("INVALID HEAP FREE");found->available=1;
    for(block *b=head;b&&b->next;){if(b->available&&b->next->available){b->size+=sizeof(block)+b->next->size;b->next=b->next->next;}else b=b->next;}
}
void *calloc(size_t count,size_t size){if(size&&count>SIZE_MAX/size)return NULL;size_t n=count*size;void *p=malloc(n);if(p)memset(p,0,n);return p;}
void *realloc(void *p,size_t n){if(!p)return malloc(n);if(!n){free(p);return NULL;}block *b=(block *)p-1;if(b->size>=n)return p;void *q=malloc(n);if(q){memcpy(q,p,b->size);free(p);}return q;}
struct _reent;
void *_malloc_r(struct _reent *r,size_t n){(void)r;return malloc(n);}
void _free_r(struct _reent *r,void *p){(void)r;free(p);}
void *_realloc_r(struct _reent *r,void *p,size_t n){(void)r;return realloc(p,n);}
void *_calloc_r(struct _reent *r,size_t a,size_t b){(void)r;return calloc(a,b);}
extern int vsnprintf_(char *,size_t,const char *,va_list);
int vsnprintf(char *buf,size_t n,const char *fmt,va_list ap){return vsnprintf_(buf,n,fmt,ap);}
int snprintf(char *buf,size_t n,const char *fmt,...){va_list ap;va_start(ap,fmt);int r=vsnprintf_(buf,n,fmt,ap);va_end(ap);return r;}
int printf(const char *fmt,...){(void)fmt;return 0;}
int fprintf(FILE *fp,const char *fmt,...){(void)fp;(void)fmt;return 0;}
int puts(const char *s){(void)s;return 0;}
void _putchar(char c){(void)c;}
/* Doom uses only one integer conversion, with optional literal radix prefix. */
#ifndef DP_SCANF
#define DP_SCANF sscanf
#endif
int DP_SCANF(const char *s,const char *fmt,...){
    while(*fmt && *fmt!='%'){
        if(*fmt==' '){while(*s==' '||*s=='\t'||*s=='\n'||*s=='\r')s++;fmt++;continue;}
        if(*fmt++!=*s++)return 0;
    }
    if(*fmt++!='%')return 0;
    int base=*fmt=='x'?16:*fmt=='o'?8:*fmt=='i'?0:*fmt=='d'?10:-1;
    if(base<0||fmt[1])return 0;
    char *end;long value=strtol(s,&end,base);if(end==s)return 0;
    va_list ap;va_start(ap,fmt);int *out=va_arg(ap,int *);va_end(ap);*out=(int)value;return 1;
}
extern int _open(const char *,int,...),_close(int),_read(int,void *,size_t);
extern off_t _lseek(int,off_t,int);
static FILE wad_handle;
FILE *fopen(const char *name,const char *mode){if(!mode||mode[0]!='r'||strchr(mode,'+')){errno=EROFS;return NULL;}return _open(name,O_RDONLY)<0?NULL:&wad_handle;}
int fclose(FILE *f){return f==&wad_handle?_close(3):EOF;}
size_t fread(void *p,size_t size,size_t count,FILE *f){if(f!=&wad_handle||!size||count>SIZE_MAX/size)return 0;int n=_read(3,p,count*size);return n<0?0:(size_t)n/size;}
size_t fwrite(const void *p,size_t size,size_t count,FILE *f){(void)p;(void)size;(void)count;(void)f;errno=EROFS;return 0;}
int fseek(FILE *f,long off,int whence){return f==&wad_handle&&_lseek(3,off,whence)>=0?0:-1;}
long ftell(FILE *f){return f==&wad_handle?_lseek(3,0,SEEK_CUR):-1;}
int fflush(FILE *f){(void)f;return 0;}
int remove(const char *s){(void)s;errno=EROFS;return -1;}
int rename(const char *a,const char *b){(void)a;(void)b;errno=EROFS;return -1;}
void exit(int n){(void)n;dp_panic("PROGRAM EXIT");}
