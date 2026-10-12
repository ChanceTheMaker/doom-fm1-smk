/* SPDX-License-Identifier: GPL-3.0-only */
#include "sfx.h"
#define NVOICE 4
#define QSIZE 16
typedef struct {unsigned kind,gain,priority;} event;
typedef struct {unsigned kind,left,total,phase,step,rng,gain,priority;int filter;} voice;
static voice voices[NVOICE];
static event queue[QSIZE];
static volatile unsigned read_at,write_at,master=512;
static void barrier(void){
#ifdef DP_NATIVE_AUDIO
 __asm__ volatile("csync" ::: "memory");
#else
 __asm__ volatile("" ::: "memory");
#endif
}
int dp_sfx_post(unsigned effect,unsigned volume,unsigned priority){
 if(effect>DP_SFX_COUNT)return 0;
 unsigned w=write_at,next=(w+1)&(QSIZE-1);if(next==read_at)return 0;
 queue[w]=(event){effect,volume>127?127:volume,priority};barrier();write_at=next;return 1;
}
void dp_sfx_master(unsigned volume){master=volume>1023?1023:volume;}
void dp_sfx_reset(void){dp_sfx_post(DP_SFX_COUNT,0,255);}
void dp_sfx_render(int32_t *out,unsigned frames){
 static const unsigned lengths[]={11025,3528,15435,7056,19845,8820,2205,11025,4410};
 static const unsigned hz[]={75,1000,110,175,140,660,880,330,95};
 /* Drain a bounded snapshot. Main cannot preempt this IRQ on the device. */
 unsigned end=write_at;barrier();
 while(read_at!=end){event e=queue[read_at];barrier();read_at=(read_at+1)&(QSIZE-1);
  if(e.kind==DP_SFX_COUNT){for(unsigned i=0;i<NVOICE;i++)voices[i].left=0;continue;}
  if(!e.gain)continue;
  unsigned slot=0;for(unsigned i=0;i<NVOICE;i++){if(!voices[i].left){slot=i;break;}if(voices[i].priority<voices[slot].priority || (voices[i].priority==voices[slot].priority && voices[i].left<voices[slot].left))slot=i;}
  if(voices[slot].left&&voices[slot].priority>e.priority)continue;
  voices[slot]=(voice){e.kind,lengths[e.kind],lengths[e.kind],0,hz[e.kind]*97392u,0x9e3779b9u+e.kind,e.gain,e.priority,0};
 }
 for(unsigned n=0;n<frames;n++){
  int mix=0;
  for(unsigned i=0;i<NVOICE;i++){voice *v=&voices[i];if(!v->left)continue;
   unsigned age=v->total-v->left;v->rng^=v->rng<<13;v->rng^=v->rng>>17;v->rng^=v->rng<<5;
   int noise=(int)(v->rng&65535)-32768;v->filter+=(noise-v->filter)/4;
   unsigned step=v->step;
   if(v->kind==DP_DEATH||v->kind==DP_HURT)step=(step/256)*(128+128*v->left/v->total);
   if(v->kind==DP_PICKUP)step*=1+age/(v->total/3+1);
   v->phase+=step;
   int tri=(int)(v->phase>>16);tri=tri<32768?tri*2-32768:98303-tri*2;
   int value;
   switch(v->kind){
    case DP_BANG:value=age<1300?noise:(v->filter*3+tri)/4;break;
    case DP_PUMP:value=((age/600)%3==1)?noise/2:noise/8;break;
    case DP_GROWL:case DP_DEATH:value=(tri*2+v->filter)/3;break;
    case DP_PICKUP:case DP_SWITCH:value=tri/2;break;
    case DP_FIREBALL:value=(noise+tri)/3;break;
    default:value=(tri+noise)/3;break;
   }
   int env=(int)(v->left*256/v->total);if(age<100)env=env*(int)age/100;
   value=(value*env)/256;mix+=(value*(int)v->gain)/512;v->left--;
  }
  mix=(mix*(int)master)/1023;if(mix>16000)mix=16000;if(mix< -16000)mix=-16000;
  out[n*2]=out[n*2+1]=mix*128;
 }
}
