/* SPDX-License-Identifier: GPL-3.0-only */
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
void *dp_malloc(size_t);void dp_free(void *);void *dp_calloc(size_t,size_t);void *dp_realloc(void *,size_t);
int dp_snprintf(char *,size_t,const char *,...);int dp_sscanf(const char *,const char *,...);
FILE *dp_fopen(const char *,const char *);int dp_fclose(FILE *);size_t dp_fread(void *,size_t,size_t,FILE *);
size_t dp_fwrite(const void *,size_t,size_t,FILE *);int dp_fseek(FILE *,long,int);long dp_ftell(FILE *);
void dp_panic(const char *msg){fprintf(stderr,"Unexpected panic: %s\n",msg);abort();}
__asm__(".section .rodata\n.globl dp_wad_start\n.globl dp_wad_end\ndp_wad_start:\n.byte 1,2,3,4\ndp_wad_end:\n.text\n");
int main(void){
    void *slots[64]={0};size_t lengths[64]={0};uint32_t seed=42;
    for(unsigned i=0;i<10000;i++){
        seed=seed*1664525u+1013904223u;unsigned slot=(seed>>12)&63;
        if(slots[slot]){for(size_t k=0;k<lengths[slot];k++)assert(((unsigned char *)slots[slot])[k]==slot);dp_free(slots[slot]);slots[slot]=0;}
        else {size_t n=(seed>>20)+1;void *p=dp_malloc(n);if(p){assert(!((uintptr_t)p&7));memset(p,slot,n);slots[slot]=p;lengths[slot]=n;}}
    }
    for(unsigned i=0;i<64;i++)dp_free(slots[i]);
    void *large=dp_malloc(23*1024);assert(large);assert(!dp_malloc(24*1024));dp_free(large);
    unsigned char *a=dp_calloc(32,4);assert(a);for(unsigned i=0;i<128;i++)assert(!a[i]);memset(a,0xab,128);
    a=dp_realloc(a,4096);assert(a);for(unsigned i=0;i<128;i++)assert(a[i]==0xab);
    assert(!dp_realloc(a,SIZE_MAX));for(unsigned i=0;i<128;i++)assert(a[i]==0xab);dp_free(a);
    assert(!dp_calloc(SIZE_MAX,2));assert(!dp_malloc(SIZE_MAX));dp_free(NULL);
    char text[20];assert(dp_snprintf(text,sizeof text,"ST%02d %s",7,"OK")==7);assert(!strcmp(text,"ST07 OK"));
    assert(dp_snprintf(text,4,"HELLO")==5);assert(!strcmp(text,"HEL"));
    int value;assert(dp_sscanf(" 0x2a"," 0x%x",&value)==1&&value==42);
    assert(dp_sscanf("-17"," %d",&value)==1&&value==-17);
    assert(dp_sscanf("030"," 0%o",&value)==1&&value==24);
    assert(dp_sscanf("garbage","%i",&value)==0);
    assert(!dp_fopen("save.dsg","wb"));assert(!dp_fopen("miniwad.wad","r+"));
    FILE *f=dp_fopen("miniwad.wad","rb");assert(f);assert(!dp_fopen("miniwad.wad","rb"));
    unsigned char b[8]={0};assert(dp_fread(b,1,8,f)==4);assert(b[0]==1&&b[3]==4);assert(dp_ftell(f)==4);
    assert(dp_fseek(f,-2,SEEK_END)==0);assert(dp_fread(b,1,3,f)==2&&b[0]==3);
    assert(dp_fseek(f,5,SEEK_SET)==-1);assert(dp_fwrite(b,1,2,f)==0);assert(dp_fclose(f)==0);
    puts("PASS: bounded native heap stress, formatting, parsing, read-only virtual WAD");
}
