/* SPDX-License-Identifier: GPL-3.0-only */
/* USB-MIDI update control only. No flash writes execute in the game. */
#include <stdint.h>
#include <string.h>
#include "platform.h"
#include "fm1_time.h"
#include "fm1_sys.h"
#include "fm1_timer.h"
#include "doom_update_config.h"
#include "doom_loader_image.h"
#define FELUCCA_OTA 1
#define FELUCCA_SYSEX 1
#define FELUCCA_CDC 0
#define FELUCCA_UAC 0
#define RING_PUBLISH() __asm__ volatile("" ::: "memory")
#include "update/usb.c"
static uint8_t ready;
static uint32_t ota_now_ms(void){return dp_millis();}
static void ota_idle(void){fm1_wdt_feed();}
extern void dp_usb_isr(void);
void dp_usb_irq(void){fm1_timer5_ack();usb_poll();}
void dp_usb_init(void){
    usb_start();
    FM1_T5_CON=0x4000u;FM1_T5_CNT=0;FM1_T5_PRD=3000u;
    fm1_irq_attach(FM1_IRQ_TIMER5,dp_usb_isr,2);
    ready=1;FM1_T5_CON=0x4019u; /* 6 MHz / 3000 = 2 kHz, below audio */
}
int dp_usb_service(void){
    if(!ready)return 0;
    /* usb_start may touch INDEX; the timer must not poll it concurrently. */
    if(!usb.up&&!usb.detached){
        FM1_T5_CON=0x4000u;
        usb_retry(dp_millis());
        FM1_T5_CNT=0;FM1_T5_CON=0x4019u;
    }
    mi_r=mi_w; /* game has no MIDI note consumer */
    const uint8_t *p;uint32_t n;
    static const uint8_t query[]={0,0x32,0x45,0,0,0,0x40,0x7f};
    if(ota_frame_get(&p,&n)){
        int identity=n==sizeof query&&!memcmp(p,query,n);
        ota_frame_done();
        if(identity)ota_wire_send(dp_identity_wire,sizeof dp_identity_wire);
    }
    if(usb.ota_req){usb.ota_req=0;return 1;}
    if(usb.uboot_req){usb.uboot_req=0;return 2;}
    return 0;
}
void dp_usb_enter(void){
    /* Caller stops audio/DMA first. Copy destroys game RAM and never returns. */
    fm1_irq_off();FM1_T5_CON=0x4000u;
    usb_detach();fm1_delay_ms(100);
    volatile uint8_t *dst=(volatile uint8_t *)0x01c0a800u;
    for(unsigned i=0;i<sizeof dp_loader_image;i++)dst[i]=dp_loader_image[i];
    __asm__ volatile("csync" ::: "memory");
    void (*volatile enter)(void)=(void (*)(void))0x01c0a800u;
    enter();for(;;);
}
