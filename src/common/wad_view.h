/* SPDX-License-Identifier: GPL-3.0-only */
#pragma once
#include <stddef.h>
#include <stdint.h>
/* Validate a complete immutable WAD before exposing pointers into it. */
int dp_wad_validate(const uint8_t *data,size_t length);
