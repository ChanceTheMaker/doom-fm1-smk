/* SPDX-License-Identifier: GPL-3.0-only */
/* Appended to a build-directory copy of upstream z_zone.c; upstream is untouched. */
#include "memory_probe.h"
void dp_read_zone(dp_zone_snapshot *out) {
    *out=(dp_zone_snapshot){0};
    if (!mainzone) return;
    out->capacity=mainzone->size;
    out->allocated=out->nonpurgeable=sizeof(*mainzone);
    for (memblock_t *b=mainzone->blocklist.next;b!=&mainzone->blocklist;b=b->next) {
        if (b->tag!=PU_FREE) out->allocated+=b->size;
        if (b->tag!=PU_FREE && b->tag<PU_PURGELEVEL) out->nonpurgeable+=b->size;
    }
}
