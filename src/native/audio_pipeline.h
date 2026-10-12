/* SPDX-License-Identifier: GPL-3.0-only */
/* CPU0 IRQ consumes one completed block, then launches CPU1 for the next.
 * A private scratch block keeps late worker writes away from live DMA memory.
 * No IRQ busy-wait: a missed deadline retires CPU1 before serial recovery.
 * Include after audio_worker.h. Host tests exercise this same dispatcher. */
#pragma once
static int32_t dp_audio_scratch[2*AUDIO_FRAMES] __attribute__((aligned(32)));
static uint32_t dp_audio_blocks,dp_audio_deadlines,dp_audio_fallbacks;
static void dp_audio_job(void *unused){
 (void)unused;dp_sfx_render(dp_audio_scratch,AUDIO_FRAMES);
}
static void dp_audio_prime(void){
 if(audio_worker_online)audio_worker_submit(dp_audio_job,0);
}
static void dp_audio_fill(int32_t *out){
 int was_online=audio_worker_online;
 audio_worker_check();
 if(audio_worker_online && AW_LOAD(&audio_worker.complete)!=AW_LOAD(&audio_worker.request)){
  dp_audio_deadlines++;audio_worker_retire();
 }
 if(was_online&&!audio_worker_online){
  /* Holding CPU1 above transfers sole ownership back. Discard the partial
   * block and reinitialize consumer state; never rerun a half-finished job. */
  dp_audio_fallbacks++;dp_sfx_recover();
  for(unsigned i=0;i<2*AUDIO_FRAMES;i++)out[i]=0;
  return;
 }
 if(!audio_worker_online){dp_sfx_render(out,AUDIO_FRAMES);return;}
 for(unsigned i=0;i<2*AUDIO_FRAMES;i++)out[i]=dp_audio_scratch[i];
 dp_audio_blocks++;
 audio_worker_submit(dp_audio_job,0);
}
