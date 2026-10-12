/* SPDX-License-Identifier: GPL-3.0-only */
#include "music.h"
#include <stdint.h>

/* "Circuit Breaker": an original eight-bar heavy loop, 140 BPM.
 * Synthesize at 11.025 kHz and interpolate to the 44.1 kHz effects mixer.
 * No Doom score, samples, PCM buffers, allocation or engine calls.
 * Each step is an eighth note; zero is a rest. D minor with a chromatic turn.
 */
static const uint8_t riff[64] = {
 1,1,0,4,1,0,3,2, 1,0,1,1,5,0,4,0,
 3,3,0,6,3,0,4,2, 3,0,3,4,2,0,1,0,
 7,7,0,4,7,0,3,4, 7,0,7,2,4,0,6,0,
 5,5,0,3,5,0,2,8, 1,0,4,3,2,0,8,0
};
/* Phase increments for D2, F2, G2, A2, C2, C3, Bb1, Eb2. */
static const uint32_t pitch[] = {
 0,7149946,8502750,9543902,10713070,6370045,12740091,5675148,7575107
};
enum { STEP_FRAMES=9450, RUN=128, PAUSE=256, GENERATION=65536 };
static volatile uint32_t requested=80;
static uint32_t applied;
static unsigned gain,playing,step,age;
static uint32_t root_phase,fifth_phase,bass_phase,kick_phase,rng;
static unsigned chord_env,kick_env,snare_env,hat_env;
static int guitar_filter;
static unsigned subframe;
static int previous_sample,next_sample;

static void publish(uint32_t state){
#ifdef DP_NATIVE_AUDIO
 __asm__ volatile("csync" ::: "memory");
#else
 __asm__ volatile("" ::: "memory");
#endif
 requested=state;
}
void dp_music_start(void){publish(((requested+GENERATION)&0xffff0000u)|(requested&127u)|RUN);}
void dp_music_stop(void){publish(requested&~(RUN|PAUSE));}
void dp_music_pause(int paused){publish(paused?requested|PAUSE:requested&~PAUSE);}
void dp_music_volume(unsigned volume){publish((requested&~127u)|(volume>127?127:volume));}

void dp_music_begin(void){
 uint32_t state=requested;
 if((state^applied)&0xffff0000u){
  step=age=0;root_phase=fifth_phase=bass_phase=kick_phase=0;
  chord_env=kick_env=snare_env=hat_env=0;guitar_filter=0;rng=0x714f3a21u;
  subframe=0;previous_sample=next_sample=0;
 }
 applied=state;gain=state&127;playing=(state&RUN)&&!(state&PAUSE);
}
static int triangle(uint32_t phase){
 int n=(int)(phase>>16);return n<32768?n*2-32768:98303-n*2;
}
static unsigned decay(unsigned env,unsigned shift){
 unsigned drop=(env>>shift)+4;return env>drop?env-drop:0;
}

static int synth_sample(void){
 unsigned beat=step&7,note=riff[step];
 if(age<4){
  if(beat==0||beat==3||(beat==4&&((step/8)&1)))kick_env=4096;
  if(beat==2||beat==6)snare_env=4096;
  hat_env=1800;
 }
 if(age>=STEP_FRAMES/2&&age<STEP_FRAMES/2+4&&(step/8==3||step/8==7))hat_env=1100;
 if(note&&age<6500){if(chord_env<4096)chord_env+=128;}
 else chord_env=chord_env>64?chord_env-64:0;
 if(note){
  root_phase+=pitch[note]*4;fifth_phase+=(pitch[note]+pitch[note]/2+17000)*4;
  bass_phase+=pitch[note]*2;
 }
 int square=(root_phase&0x80000000u?7000:-7000)+(fifth_phase&0x80000000u?4500:-4500);
 guitar_filter+=(square-guitar_filter)/2;
 int mix=(guitar_filter*(int)chord_env)/32768;
 mix+=(triangle(bass_phase)*(int)chord_env)/131072;
 rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;
 int noise=(int)(rng&65535)-32768;
 kick_phase+=(4674794u+kick_env*1800u)*4;
 mix+=(triangle(kick_phase)*(int)kick_env)/65536;
 mix+=(noise*(int)snare_env)/131072;
 mix+=(noise*(int)hat_env)/262144;
 kick_env=decay(kick_env,7);snare_env=decay(snare_env,8);hat_env=decay(hat_env,5);
 /* Carry the two-sample remainder: no tempo drift from downsampling. */
 age+=4;if(age>=STEP_FRAMES){age-=STEP_FRAMES;step=(step+1)&63;}
 return mix;
}
int dp_music_sample(void){
 if(!playing)return 0; /* Pause holds synthesis and interpolation position. */
 if(subframe==0){previous_sample=next_sample;next_sample=synth_sample();}
 int mix=previous_sample+(next_sample-previous_sample)*(int)subframe/4;
 subframe=(subframe+1)&3;
 return (mix*(int)gain)/128;
}
