# Release 16

Release 16 adds the `FM-1/SMK` splash subtitle, centered HUD face, K1 combined
music/effects volume and K2 menu scrolling. It fixes the reproduced guard/imp
overkill-death crash by supplying all engine-referenced sprite frames. The nine
existing maps, three weapons and dual-core audio remain unchanged.

K1 scales the full audio mix. FM-1 MASTER remains an overall output limit.
K2 scrolls active menus without injecting gameplay movement; Select still
confirms choices. The browser panels support drag, wheel and keyboard control.

## Evidence and scope

All three native applications compiled and passed package round-trip and
protected-byte checks. The real host engine reproduced both missing-frame
crashes before the correction and projects all 66 guard/imp states afterward.
Expanded asset coverage passes 211 state references across 23 included sprite
families. Repeated nine-level host campaigns, native memory limits, sound/mute,
encoder detents, real WASM gameplay/menu tests and deployment checks pass.

The owner reported an SMK-37 install from the page still showing the old splash;
that installer still selected Release 15. A separate local revision 16 Pro
installer was prepared, its package built and verified, and its reboot check
tested to require `Doom-SMK-37_016`. The owner then said **"Looks good publish
it"**. This records publication approval, not a captured runtime identity or
an explicit full hardware gameplay/knob checklist. FM-1, Pro and Elite detailed
revision 16 hardware acceptance therefore remains pending.

A later pre-candidate error was transcribed as "9 8 0", possibly on level 2.
Its exact diagnostic values and cause were not confirmed. The known sprite
correction is tested locally; this additional report remains for hardware
retesting. Earlier hardware evidence is retained in [Release 15](RELEASE15.md).

## Immutable application artifacts

| Target | Bytes | Free application bytes | SHA-256 |
| --- | ---: | ---: | --- |
| FM-1 | 577820 | 3744 | `e890ca2efa216f763a8ae10037d979fc08c0803bd4fff30285a82f2317959610` |
| SMK-37 Pro | 578160 | 3404 | `6c0c0cb7172b7ef7257cc2e2195c4c169d3264f73c5527f9fec19a8f694c6840` |
| SMK-37 Elite | 578160 | 3404 | `fffc0911e17d893066e51c0e387f462a3670c4c9c0d1aa281a9cbd58a8d943aa` |

Runtime and RAM-loader identities end in `_016`. The public filenames end in
`-16.bin`. The website requires the exact runtime model and revision after a
transfer; Release 15 cannot satisfy its success check. The original Release 15
binaries remain byte-identical in `archive-release15.json`. Any future firmware
change must receive a new public revision rather than replacing these files.

Only `site/` is published. Private recovery evidence, native intermediates and
complete locally generated packages remain ignored under `build/`. The original
dirty development and safety worktrees are preserved. See the archived
[candidate notes](CANDIDATE16.md) for implementation details.
