/* SPDX-License-Identifier: GPL-3.0-only */
/* Launch sequence adapted from Melodee's fm1_multicore.h (see THIRD_PARTY).
 * CPU1 has private stacks and no peripheral interrupts. All flash/recovery
 * paths hold it before reusing SRAM or disabling XIP. Polling stays in RAM to
 * avoid competing with CPU0's instruction fetch while idle. */
#pragma once
#define AW_WORD volatile uint32_t
static inline __attribute__((always_inline)) uint32_t dp_shared_load(volatile uint32_t *p){
 uint32_t value=*p;__asm__ volatile("csync" ::: "memory");return value;
}
static inline __attribute__((always_inline)) void dp_shared_store(volatile uint32_t *p,uint32_t value){
 __asm__ volatile("csync" ::: "memory");*p=value;__asm__ volatile("csync" ::: "memory");
}
#define AW_LOAD(p) dp_shared_load(p)
#define AW_STORE(p,v) dp_shared_store(p,v)
#define AW_TICKS() fm1_ticks()
#define AW_TIMEOUT_TICKS (10000u*FM1_TICKS_PER_US)
#define AW_HOLD() fm1_core1_stop()
#define AW_FAULTS() fm1_core1_fault.count
#define AW_RAM_LOOP __attribute__((section(".dsp_text"),noinline,noreturn,used))
#include "audio_worker.h"
#include "audio_pipeline.h"
extern void dp_core1_start(void);
extern uint32_t _cpu1_stacks_lo[],_cpu1_stacks_hi[];
static volatile uint32_t dp_audio_core;
void __attribute__((section(".dsp_text"),noreturn,used)) dp_core1_main(void){
 uint32_t lo=(uint32_t)(uintptr_t)_cpu1_stacks_lo+256u;
 uint32_t hi=(uint32_t)(uintptr_t)_cpu1_stacks_hi-1u;
 *(volatile uint32_t *)0x1EEF2D8u=hi;*(volatile uint32_t *)0x1EEF2DCu=lo;
 *(volatile uint32_t *)0x1EEF2E0u=hi;*(volatile uint32_t *)0x1EEF2E4u=lo;
 *(volatile uint32_t *)0x1EEF2D0u=(*(volatile uint32_t *)0x1EEF2D0u&~((1u<<2)|(31u<<16)))|(1u<<3);
 uint32_t core;__asm__ volatile("%0 = cnum" : "=r"(core));
 dp_shared_store(&dp_audio_core,core);
 audio_worker_loop();
}
static void dp_multicore_start(void){
 fm1_core1_stop();audio_worker_online=0;
 /* A failed previous boot retries with serial audio. No persistent flash flag. */
 if(dp_boot.failures)return;
 for(unsigned i=0;i<64;i++)_cpu1_stacks_lo[i]=0x5aa55aa5;
 for(unsigned i=0;i<32;i++)*(volatile uint32_t *)(0x1EEF300u+4u*i)=0;
 *(volatile uint32_t *)0x01C7FFF8u=(uint32_t)(uintptr_t)dp_core1_start;
 uint32_t div=*(volatile uint32_t *)0x10008u;
 *(volatile uint32_t *)0x10008u=div|8u;
 __asm__ volatile("csync" ::: "memory");
 *(volatile uint32_t *)0x1EEE004u|=8u;
 *(volatile uint32_t *)0x1EEE004u&=~2u;
 uint32_t start=fm1_ticks();
 while(!AW_LOAD(&audio_worker.ready)&&(uint32_t)(fm1_ticks()-start)<10000u*FM1_TICKS_PER_US);
 audio_worker_online=AW_LOAD(&audio_worker.ready)&&AW_LOAD(&dp_audio_core)==1u;
 if(!audio_worker_online)fm1_core1_stop();
 *(volatile uint32_t *)0x10008u=div;
 dp_audio_prime();
}
static void dp_multicore_stop(void){fm1_core1_stop();audio_worker_online=0;}
/* Called by CPU0 main, with audio IRQ masked only during this short snapshot. */
void dp_audio_stats(uint32_t words[8]){
 fm1_irq_off();
 words[0]=audio_worker_online?2u:1u;words[1]=dp_audio_core;
 words[2]=dp_audio_blocks;words[3]=audio_worker.jobs;
 words[4]=dp_audio_deadlines;words[5]=fm1_core1_fault.count;
 words[6]=audio_worker.rejected;words[7]=audio_worker.max_job_ticks;
 fm1_irq_on();
}
