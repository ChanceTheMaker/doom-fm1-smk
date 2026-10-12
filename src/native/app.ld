/* SPDX-License-Identifier: GPL-3.0-only */
/* Application-only XIP slot. Preserve boot records and low debug RAM. */
MEMORY {
    XIP (rx) : ORIGIN = 0x02000120, LENGTH = 0x8dfbc
    LOWHEAP (rw) : ORIGIN = 0x01c00000, LENGTH = 0x6000
    RAM (rwx) : ORIGIN = 0x01c08000, LENGTH = 0x6c000
    NOINIT (rw) : ORIGIN = 0x01c7c000, LENGTH = 0x3d50
}
SECTIONS {
    .text : { KEEP(*(.text.crt0)) *(.text*) *(.rodata*) . = ALIGN(4); } > XIP
    .data : { _data_start = .; *(.data*) *(.sdata*) *(.dsp_text*) . = ALIGN(4); _data_end = .; } > RAM AT > XIP
    _data_load = LOADADDR(.data);
    .bss (NOLOAD) : { _bss_start = .; *(.bss*) *(.sbss*) *(COMMON) . = ALIGN(8); _bss_end = .; } > RAM
    .lowheap (NOLOAD) : { *(.lowheap*) } > LOWHEAP
    .noinit (NOLOAD) : { *(.noinit*) . = ALIGN(4); } > NOINIT
    /* Private CPU1 stacks use previously unused retained SRAM, not Doom's
     * zone/heap or either CPU0 stack. First 256 bytes are a guard region. */
    .cpu1_stacks (NOLOAD) : {
        . = ALIGN(32); _cpu1_stacks_lo = .;
        . += 0x1800; _cpu1_ustack_top = .;
        . += 0x0800; _cpu1_sstack_top = .; _cpu1_stacks_hi = .;
    } > NOINIT
    _ustack_lo = 0x01c74100; _ustack_top = 0x01c7a000;
    _sstack_lo = 0x01c7a100; _sstack_top = 0x01c7c000;
    ASSERT(_bss_end <= 0x01c74000, "Doom exceeds application RAM")
    ASSERT(_cpu1_stacks_hi <= 0x01c7fd50, "CPU1 stack overlaps boot/vector area")
    /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
