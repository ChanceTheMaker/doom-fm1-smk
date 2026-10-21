/* SPDX-License-Identifier: GPL-3.0-only */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
static uint32_t regs[0x52000/4];
#define SMK37_ADC_REG(a) regs[(a)/4]
#define SMK37_SCAN_REG(a) regs[(a)/4]
#define SMK37_SCAN_BAUD 95u
#include "../src/native/hal/smk37_adc.h"
#include "../src/native/hal/smk37_scanner.h"
static unsigned attaches;
static void isr(void){}
static void attach(uint32_t irq,void (*handler)(void),uint32_t priority){
    assert(irq==37&&handler==isr&&priority==5);attaches++;
}
int main(void){
    /* Simulate a warm handoff with unrelated ADC/GPIO/SPI state. */
    for(unsigned i=0;i<sizeof regs/sizeof *regs;i++)regs[i]=0xffffffff;
    smk37_adc_t adc;smk37_adc_init(&adc);
    assert(!regs[0x13100/4]&&adc.enabled&&!adc.scan.pending&&!adc.samples);
    const unsigned pa=(1u<<8)|(1u<<10),pc=1u<<9;
    assert((regs[0x50008/4]&pa)==pa&&!(regs[0x5000c/4]&pa));
    assert(!(regs[0x50010/4]&pa)&&!(regs[0x50014/4]&pa));
    assert((regs[0x50088/4]&pc)&&!(regs[0x5008c/4]&pc));
    smk37_scan_set_analog(smk37_analog_mask(&adc.scan));
    smk37_scan_init(attach,isr);
    assert(attaches==1&&regs[0x11e04/4]==95&&regs[0x11e00/4]==0x6021);
    assert(!smk37_scan_slot&&!smk37_scan_warm);
    for(unsigned i=0;i<16;i++)assert(smk37_scan_frame[i]==255);
    /* Each conversion is tagged with its PREVIOUS mux index; feeding the
     * incremented index used to cause wrong controls/colors in other ports. */
    for(unsigned i=0;i<24;i++){
        unsigned index=adc.scan.index;assert(index==i);
        for(unsigned n=0;n<3;n++)assert(!smk37_adc_spi_done(&adc));
        assert(adc.scan.pending);
        assert(((regs[0x13100/4]>>8)&15)==(i<8?1:i<16?8:2));
        regs[0x13100/4]|=0x80;regs[0x13104/4]=i*40;
        assert(smk37_adc_spi_done(&adc)==1&&adc.scan.raw[index]==i*40);
        assert(adc.scan.index==(i+1)%24);
        smk37_scan_set_analog(smk37_analog_mask(&adc.scan));
        assert((smk37_scan_analog_mask&~0x38u)==0xffffffc7u);
    }
    assert(adc.samples==24&&adc.scan.valid==0xffffff);
    for(unsigned n=0;n<3;n++)assert(!smk37_adc_spi_done(&adc));
    for(unsigned n=0;n<127;n++)assert(!smk37_adc_spi_done(&adc));
    assert(smk37_adc_spi_done(&adc)==-1&&!adc.enabled&&adc.timeouts==1);
    smk37_scan_stop();assert(regs[0x11e00/4]==0x4000);
    assert((regs[0x16a0c/4]&0x7000f)==0x7000f);
    puts("PASS: dirty warm-start ADC/scanner reset, mux sample ownership, game scan rate and bounded failure/stop");
}
