/* SPDX-License-Identifier: GPL-3.0-only
 * IRQ calling convention from fm1_isr.S, Copyright (C) 2026
 * Leo Kuroshita (@kurogedelic), Hugelton Instruments. */
 .section .text.dp_audio_isr,"ax",@progbits
 .globl dp_audio_isr
dp_audio_isr:
 [--sp] = {psr, rets, reti}
 [--sp] = {r3-r0}
 call dp_audio_irq
 {r3-r0} = [sp++]
 {psr, rets, reti} = [sp++]
 csync
 rti
