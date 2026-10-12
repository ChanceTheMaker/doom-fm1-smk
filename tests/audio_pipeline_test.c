/* SPDX-License-Identifier: GPL-3.0-only */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#define AUDIO_FRAMES 128u
static unsigned holds,faults,renders,recovers,clock_value;
#define AW_WORD uint32_t
#define AW_LOAD(p) (*(p))
#define AW_STORE(p,v) (*(p)=(v))
#define AW_TICKS() (clock_value++)
#define AW_TIMEOUT_TICKS 10u
#define AW_HOLD() (holds++)
#define AW_FAULTS() faults
#define AW_RAM_LOOP static
#include "../src/native/audio_worker.h"
static void dp_sfx_render(int32_t *out,unsigned frames){
 renders++;for(unsigned i=0;i<2*frames;i++)out[i]=(int32_t)renders;
}
static void dp_sfx_recover(void){assert(holds);recovers++;}
#include "../src/native/audio_pipeline.h"
int main(void){
 int32_t dma[2*AUDIO_FRAMES];uint32_t done=0;
 dp_audio_fill(dma);assert(renders==1&&dma[0]==1); /* serial startup fallback */
 audio_worker_online=1;dp_audio_prime();assert(renders==1);
 audio_worker_poll(&done);assert(renders==2);
 dp_audio_fill(dma);assert(dma[0]==2&&dma[255]==2&&dp_audio_blocks==1);
 assert(renders==2&&audio_worker.request!=audio_worker.complete);
 /* CPU0 does not render, wait, or consume partially written worker output. */
 dp_audio_scratch[0]=999;dp_audio_fill(dma);
 assert(holds==1&&recovers==1&&dp_audio_deadlines==1&&!audio_worker_online);
 assert(dma[0]==0&&dma[255]==0&&renders==2);
 dp_audio_fill(dma);assert(dma[0]==3&&renders==3);
 /* Fault after completion still drops the block, and never replays that job. */
 audio_worker_online=1;done=audio_worker.complete;dp_audio_prime();
 audio_worker_poll(&done);faults=1;dp_audio_fill(dma);
 assert(holds==2&&recovers==2&&renders==4&&dma[0]==0);
 faults=0;dp_audio_fill(dma);assert(renders==5&&dma[0]==5);
 /* A rejected mailbox also forces ownership back before recovery. */
 audio_worker_online=1;audio_worker.rejected=1;dp_audio_fill(dma);
 assert(holds==3&&recovers==3&&dp_audio_fallbacks==3&&dma[0]==0);
 puts("PASS audio pipeline: asynchronous CPU1 blocks, private DMA staging, deadline/fault/misread retirement, serial recovery");
}
