/* SPDX-License-Identifier: GPL-3.0-only */
#include "platform.h"
#include "doomgeneric.h"
#include "doomkeys.h"
#include "fm1_time.h"
#include "fm1_sys.h"
#include "fm1_irq.h"
#ifdef DP_USB_UPDATE
#include "usb_update.c" /* shared HAL owns one IRQ/vector state */
#endif
#include "smk37_time.h"
#include "smk37_boot.h"
#if DP_SMK
#include "smk37_audio.h"
#include "smk37_lcd_hw.h"
#include "smk37_panel.h"
#include "smk37_scanner.h"
#include "smk37_contacts.h"
#include "smk37_keyscan.h"
#include "smk37_controls.h"
static smk37_keyscan_t keys[37];
static smk37_controls_t controls;
static uint64_t notes;
static void no_attach(uint32_t n,void(*f)(void),uint32_t p){(void)n;(void)f;(void)p;}
static int cmd(uint8_t c){return smk37_lcd_command(c,4000000);}
static int data(const void *p,uint32_t n){return smk37_lcd_data(p,n,4000000);}
static const smk37_panel_io_t panel={cmd,data,fm1_delay_ms};
#else
#include "fm1_audio.h"
#include "fm1_adc.h"
#include "fm1_input.h"
#include "fm1_lcd_hw.h"
#include "smk37_panel.h" /* window protocol only; FM-1 uses its own init sequence */
static int cmd(uint8_t c){uint32_t before=fm1_lcd_timeouts;fm1_lcd_send_cmd(c);fm1_lcd_wait();fm1_lcd_deselect();return before==fm1_lcd_timeouts;}
static int data(const void *p,uint32_t n){uint32_t before=fm1_lcd_timeouts;fm1_lcd_send_data(p,n);fm1_lcd_wait();fm1_lcd_deselect();return before==fm1_lcd_timeouts;}
static const smk37_panel_io_t panel={cmd,data,fm1_delay_ms};
#endif
/* Retained only until a healthy game boot; available to CPU1 launch policy. */
volatile struct {uint32_t magic,pending,failures;} dp_boot __attribute__((section(".noinit")));
#ifdef DP_CAMPAIGN
#include "sfx.h"
#include "splash.h"
#define AUDIO_FRAMES 128u
static int32_t audio_buffer[4*AUDIO_FRAMES] __attribute__((aligned(4)));
#if DP_DUAL_CORE
#include "dual_core.h"
#else
#define dp_audio_fill(out) dp_sfx_render(out,AUDIO_FRAMES)
#endif
extern void dp_audio_isr(void);
void dp_audio_irq(void){
#if DP_SMK
 unsigned p=smk37_audio_pending();smk37_audio_ack_aux(p);
 if(p&SMK37_AUDIO_HALF){dp_audio_fill(audio_buffer+smk37_audio_free_half()*2*AUDIO_FRAMES);smk37_audio_ack_half();}
#else
 unsigned p=fm1_audio_pending();fm1_audio_ack_aux(p);
 if(p&FM1_AUDIO_HALF){dp_audio_fill(audio_buffer+fm1_audio_free_half()*2*AUDIO_FRAMES);fm1_audio_ack_half();}
#endif
}
static void audio_start(void){
#if DP_DUAL_CORE
 dp_multicore_start();
#endif
#if DP_SMK
 const smk37_audio_hooks_t hooks={fm1_delay_ms,fm1_irq_attach};
 if(!smk37_audio_init(audio_buffer,2*AUDIO_FRAMES,dp_audio_isr,3,&hooks))dp_panic("AUDIO INIT FAILED");
#else
 fm1_adc_init();int vol=fm1_adc_read(FM1_ADC_MASTER);dp_sfx_master(vol<0?256:vol);
 fm1_audio_init(audio_buffer,2*AUDIO_FRAMES,dp_audio_isr,3);
#endif
}
#endif
static void audio_stop(void){
 fm1_irq_mask(FM1_IRQ_ALNK0);
#if DP_DUAL_CORE
 dp_multicore_stop();
#endif
#if DP_SMK
 smk37_audio_stop();
#else
 fm1_audio_stop();
#endif
}
static uint8_t display_ready,input_ready;
static uint32_t millis,last_tick,remainder,scan_at,buttons,returned;
static uint16_t wire_row[240] __attribute__((aligned(4)));
static uint32_t actions;
static void guards_init(void){
    for(volatile uint32_t *p=(volatile uint32_t *)0x01c74000;p<(volatile uint32_t *)0x01c74100;p++)*p=0x5aa55aa5;
    for(volatile uint32_t *p=(volatile uint32_t *)0x01c7a000;p<(volatile uint32_t *)0x01c7a100;p++)*p=0x5aa55aa5;
}
void dp_frame_done(void){
    for(volatile uint32_t *p=(volatile uint32_t *)0x01c74000;p<(volatile uint32_t *)0x01c74100;p++)if(*p!=0x5aa55aa5)dp_panic("USER STACK GUARD");
    for(volatile uint32_t *p=(volatile uint32_t *)0x01c7a000;p<(volatile uint32_t *)0x01c7a100;p++)if(*p!=0x5aa55aa5)dp_panic("IRQ STACK GUARD");
    if(dp_millis()>30000){dp_boot.pending=0;dp_boot.failures=0;}
}
/* Lowest seven white keys: left, forward, right, back, fire, use, menu.
 * Next five: enter, run, strafe left, strafe right, cycle weapon. */
static const unsigned char action_keys[]={KEY_LEFTARROW,KEY_UPARROW,KEY_RIGHTARROW,
    KEY_DOWNARROW,KEY_FIRE,KEY_USE,KEY_ESCAPE,KEY_ENTER,KEY_RSHIFT,KEY_STRAFE_L,KEY_STRAFE_R,']'};
#if DP_SMK
static const uint8_t note_keys[]={0,2,4,5,7,9,11,12,14,16,17,19};
#else
static const uint8_t note_keys[]={0,2,4,6,7,9,11,12,14,16,18,19};
#endif
uint32_t dp_millis(void){uint32_t t=fm1_ticks();remainder+=t-last_tick;last_tick=t;millis+=remainder/24000u;remainder%=24000u;return millis;}
void dp_service(void){
    fm1_wdt_feed();uint32_t now=dp_millis();
#ifdef DP_USB_UPDATE
    int request=dp_usb_service();
    if(request){
        dp_boot.pending=0;audio_stop();
        if(request==1)dp_usb_enter();
        fm1_enter_uboot();
    }
#endif
    if(!input_ready || now-scan_at<2)return;
    scan_at=now;
#if DP_SMK
    for(unsigned i=0;i<16;i++){
        if(smk37_scan_tick()){
            smk37_controls_tick(&controls,smk37_scan_frame);buttons=controls.buttons;
            for(unsigned k=0;k<37;k++){
                unsigned raw=smk37_contact_closed(smk37_scan_frame,smk37_key_contacts[k][0]) |
                    (smk37_contact_closed(smk37_scan_frame,smk37_key_contacts[k][1])<<1);
                uint32_t duration;
                if(smk37_keyscan_tick(&keys[k],raw,&duration)){
                    if(duration)notes|=(uint64_t)1<<k;else notes&=~((uint64_t)1<<k);
                }
            }
        }
        fm1_delay_us(4);
    }
    uint64_t held=notes;
#else
    fm1_input_scan();
#ifdef DP_CAMPAIGN
    static uint32_t volume_at;
    if(now-volume_at>=30){volume_at=now;int vol=fm1_adc_read(FM1_ADC_MASTER);if(vol>=0)dp_sfx_master((unsigned)vol);}
#endif
    uint32_t held=fm1_in.notes;buttons=fm1_in.buttons;
#endif
    actions=0;
    for(unsigned i=0;i<sizeof(note_keys);i++)if(held&((uint64_t)1<<note_keys[i]))actions|=1u<<i;
#if DP_SMK
    if(buttons&(1u<<12))actions|=1u<<6; /* PATCH */
    if(buttons&(1u<<13))actions|=1u<<7; /* PARA */
    const uint32_t recovery=(1u<<4)|(1u<<5);
#else
    const uint32_t recovery=3;
#endif
    static uint32_t recovery_since;
    if((buttons&recovery)==recovery){if(!recovery_since)recovery_since=now?now:1;if(now-recovery_since>2000){dp_boot.pending=0;audio_stop();fm1_enter_uboot();}}
    else recovery_since=0;
}
int dp_key(int *down,unsigned char *key){
    dp_service();uint32_t changed=actions^returned;
    for(unsigned i=0;i<sizeof(action_keys);i++)if(changed&(1u<<i)){
        *down=!!(actions&(1u<<i));*key=action_keys[i];returned^=1u<<i;return 1;
    }
    return 0;
}
int dp_lcd_row(void *ctx,unsigned y,const uint16_t *row,unsigned width){
    (void)ctx;if(!display_ready || width!=240)return 0;
    for(unsigned x=0;x<width;x++)wire_row[x]=(row[x]>>8)|(row[x]<<8);
    int ok=smk37_panel_window(&panel,0,y,width,1)&&data(wire_row,width*2);
    dp_service();return ok;
}
/* Small diagnostic alphabet. Game text uses Doom's own fonts. */
static const uint8_t glyphs[36][7]={
 {14,17,17,31,17,17,17},{30,17,17,30,17,17,30},{14,17,16,16,16,17,14},
 {30,17,17,17,17,17,30},{31,16,16,30,16,16,31},{31,16,16,30,16,16,16},
 {14,17,16,23,17,17,14},{17,17,17,31,17,17,17},{31,4,4,4,4,4,31},
 {7,2,2,2,18,18,12},{17,18,20,24,20,18,17},{16,16,16,16,16,16,31},
 {17,27,21,21,17,17,17},{17,25,21,19,17,17,17},{14,17,17,17,17,17,14},
 {30,17,17,30,16,16,16},{14,17,17,17,21,18,13},{30,17,17,30,20,18,17},
 {15,16,16,14,1,1,30},{31,4,4,4,4,4,4},{17,17,17,17,17,17,14},
 {17,17,17,17,17,10,4},{17,17,17,21,21,27,17},{17,17,10,4,10,17,17},
 {17,17,10,4,4,4,4},{31,1,2,4,8,16,31},
 {14,17,19,21,25,17,14},{4,12,4,4,4,4,14},{14,17,1,2,4,8,31},
 {30,1,1,14,1,1,30},{2,6,10,18,31,2,2},{31,16,16,30,1,1,30},
 {14,16,16,30,17,17,14},{31,1,2,4,8,8,8},{14,17,17,14,17,17,14},{14,17,17,15,1,1,14}
};
static unsigned diagnostic_row=30;
void dp_message(const char *s){
    if(!display_ready)return;
    uint16_t pixels[240];
    for(unsigned line=0;*s && line<4;line++){
        char text[40];unsigned n=0;while(*s && *s!='\n' && n<39)text[n++]=*s++;
        if(*s=='\n')s++;
        if(diagnostic_row>210)diagnostic_row=30;
        for(unsigned y=0;y<9;y++){
            for(unsigned x=0;x<240;x++)pixels[x]=0;
            for(unsigned c=0;c<n;c++){
                unsigned ch=(unsigned char)text[c];if(ch>='a'&&ch<='z')ch-=32;
                int id=ch>='A'&&ch<='Z'?(int)(ch-'A'):ch>='0'&&ch<='9'?(int)(ch-'0'+26):-1;
                if(id>=0&&y<7)for(unsigned x=0;x<5;x++)if(glyphs[id][y]&(16u>>x))pixels[c*6+x]=0xffff;
            }
            dp_lcd_row(0,diagnostic_row+y,pixels,240);
        }
        diagnostic_row+=10;
    }
}
static void dp_clear_display(void){
    uint16_t pixels[240]={0};
    for(unsigned y=0;y<240;y++)dp_lcd_row(0,y,pixels,240);
    diagnostic_row=30;
}
void dp_panic(const char *text){
    audio_stop();
    dp_clear_display();
    dp_message("DOOM STOPPED");dp_message(text);
    dp_message("HOLD BOTH OCT FOR RECOVERY");
    for(;;)dp_service();
}
static void fm1_fault(const fm1_crash_t *record){(void)record;dp_panic("CPU FAULT - POWER OFF");}
extern uint32_t _data_start[],_data_end[],_data_load[],_bss_start[],_bss_end[];
void dp_cstart(const uint32_t *parameters){
    fm1_core1_stop(); /* before clearing shared RAM inherited from any firmware */
    fm1_wdt_arm(0x0f);
    if(dp_boot.magic!=0x444f4f4d){dp_boot.magic=0x444f4f4d;dp_boot.pending=dp_boot.failures=0;}
    if(dp_boot.pending)dp_boot.failures++;
    if(dp_boot.failures>=2){dp_boot.pending=dp_boot.failures=0;fm1_enter_uboot();}
    dp_boot.pending=1;
    /* Stop inherited audio DMA before reusing synth buffers. */
#if DP_SMK
    smk37_audio_stop();smk37_audio_pc_out(6,0);
#else
    fm1_audio_stop();
#endif
    /* Capture the SPL handoff before installing exception vectors. No flash writes. */
#if DP_SMK
    smk37_boot_capture(parameters);
#else
    (void)parameters;
#endif
    uint32_t *p,*s;
    for(p=_data_start,s=_data_load;p<_data_end;)*p++=*s++;
    for(p=_bss_start;p<_bss_end;)*p++=0;
    __asm__ volatile("csync" ::: "memory");
    fm1_reset_reason();fm1_wdt_arm(0x0f);smk37_time_init();fm1_irq_init();fm1_mailbox_clear();
    guards_init();
#if DP_SMK
    smk37_lcd_hw_init(4);display_ready=smk37_panel_init(&panel);
    smk37_scan_init(no_attach,0);
#else
    fm1_lcd_hw_init();cmd(0x01);fm1_delay_ms(150);cmd(0x11);fm1_delay_ms(120);
    uint8_t mode=0x55;cmd(0x3a);data(&mode,1);mode=0;cmd(0x36);data(&mode,1);cmd(0x21);cmd(0x13);cmd(0x29);
    display_ready=!fm1_lcd_timeouts;fm1_input_init();
#endif
    input_ready=1;
#ifdef DP_CAMPAIGN
    audio_start();
#endif
#ifdef DP_USB_UPDATE
    dp_usb_init();
#endif
    fm1_irq_enable_all();
    dp_clear_display();
    #ifdef DP_CAMPAIGN
    dp_message("DOOM - NINE LEVELS");
#if DP_DUAL_CORE
    dp_message(audio_worker_online?"DUAL CORE AUDIO":"SINGLE CORE FALLBACK");
#endif
    #else
    dp_message("DOOM TEST 04");
    #endif
#if DP_SMK
    dp_message("SMK37 - DOOM");
#else
    dp_message("FM1 - DOOM");
#endif
    char *args[]={"doom","-iwad","miniwad.wad","-nosound","-warp","1","-skill","2"};
    doomgeneric_Create(8,args);
#ifdef DP_CAMPAIGN
    if(!dp_splash_present(DP_SMK?(DP_ELITE?2:1):0,dp_lcd_row,0))dp_panic("SPLASH DISPLAY FAILED");
    dp_title_start();
#endif
    for(;;){doomgeneric_Tick();dp_service();}
}
