/* SPDX-License-Identifier: GPL-3.0-only */
#include "sfx.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
static void u32(FILE *f,unsigned v){for(int i=0;i<4;i++)fputc(v>>(i*8),f);}
void dp_audio_capture(int final){
 static FILE *f;static int started,peak;static unsigned samples,nonzero;
 if(!started){started=1;const char *path=getenv("DOOM_AUDIO_OUTPUT");if(path){f=fopen(path,"wb");if(!f)exit(2);for(int i=0;i<44;i++)fputc(0,f);}}
 int32_t out[256];
 for(unsigned done=0;done<1260;){unsigned n=1260-done;if(n>128)n=128;dp_sfx_render(out,n);done+=n;
  for(unsigned i=0;i<n*2;i++){int v=out[i]/128;if(v)nonzero++;if(abs(v)>peak)peak=abs(v);if(f){fputc(v&255,f);fputc((v>>8)&255,f);}samples++;}
 }
 if(final){
  const char *report=getenv("DOOM_AUDIO_REPORT");if(report){FILE *r=fopen(report,"w");if(!r)exit(2);fprintf(r,"{\"peak\":%d,\"nonzero\":%u,\"samples\":%u}\n",peak,nonzero,samples);fclose(r);}
  if(f){rewind(f);fwrite("RIFF",1,4,f);u32(f,36+samples*2);fwrite("WAVEfmt ",1,8,f);u32(f,16);u32(f,0x00020001);u32(f,44100);u32(f,176400);u32(f,0x00100004);fwrite("data",1,4,f);u32(f,samples*2);if(fclose(f))exit(2);}
 }
}
