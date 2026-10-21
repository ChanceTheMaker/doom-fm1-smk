/* SPDX-License-Identifier: GPL-3.0-only
 * IRQ convention from fm1_isr.S, Copyright (C) 2026
 * Leo Kuroshita (@kurogedelic), Hugelton Instruments. */
#if DP_SMK
 .section .text.dp_scan_isr,"ax",@progbits
 .globl dp_scan_isr
dp_scan_isr:
 [--sp] = {psr, rets, reti}
 [--sp] = {r3-r0}
 call dp_scan_irq
 {r3-r0} = [sp++]
 {psr, rets, reti} = [sp++]
 csync
 rti
#endif
