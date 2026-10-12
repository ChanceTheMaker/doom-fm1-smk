/* SPDX-License-Identifier: GPL-3.0-only */
/* SPL entry convention used by the existing FM-1/SMK ports. */
    .section .text.crt0,"ax",@progbits
    .globl _start
_start:
    goto 1f
    rts
1:
    cli
    sp = _ustack_top
    ssp = _sstack_top
    call dp_cstart
    goto .

#if DP_DUAL_CORE
    .section .text.core1,"ax",@progbits
    .globl dp_core1_start
dp_core1_start:
    cli
    icfg = 0
    usp = _cpu1_ustack_top
    sp = _cpu1_sstack_top
    ssp = _cpu1_sstack_top
    reti = dp_core1_main
    rti
#endif
