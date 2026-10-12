/* SPDX-License-Identifier: GPL-3.0-only */
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
extern size_t dp_heap_peak(void),dp_heap_failed(void);
void dp_panic(const char *s){fprintf(stderr,"NATIVE HEAP PANIC: %s\n",s);abort();}
static void report(void){fprintf(stderr,"Native C heap: capacity 24576 peak %zu failed %zu\n",dp_heap_peak(),dp_heap_failed());}
__attribute__((constructor)) static void start(void){atexit(report);}
