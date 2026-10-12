/* SPDX-License-Identifier: GPL-3.0-only */
#pragma once
#include <stdint.h>
typedef struct {uint32_t capacity, allocated, nonpurgeable;} dp_zone_snapshot;
void dp_read_zone(dp_zone_snapshot *out);
void dp_memory_report(unsigned frames, int gamestate);
