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
