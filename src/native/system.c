/* SPDX-License-Identifier: GPL-3.0-only */
#include "i_system.h"
#include "platform.h"
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
static unsigned char zone[240*1024] __attribute__((aligned(8)));
byte *I_ZoneBase(int *size){*size=sizeof zone;return zone;}
void I_Init(void){}
void I_AtExit(atexit_func_t f,boolean error){(void)f;(void)error;}
void I_Tactile(int a,int b,int c){(void)a;(void)b;(void)c;}
void I_BindVariables(void){}
boolean I_ConsoleStdout(void){return false;}
boolean I_GetMemoryValue(unsigned int off,void *value,int size){(void)off;memset(value,0,size);return false;}
void I_PrintBanner(char *s){dp_message(s);}
void I_PrintStartupBanner(char *s){dp_message(s);}
void I_PrintDivider(void){}
void I_Quit(void){dp_panic("QUIT - POWER OFF");}
void I_Error(char *fmt,...){char msg[160];va_list ap;va_start(ap,fmt);vsnprintf(msg,sizeof msg,fmt,ap);va_end(ap);dp_panic(msg);}
ticcmd_t *I_BaseTiccmd(void){static ticcmd_t c;return &c;}
