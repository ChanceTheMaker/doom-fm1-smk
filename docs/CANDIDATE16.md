# Revision 16 local candidate

Archived preparation notes. This candidate was approved for publication as
[Release 16](RELEASE16.md); the local-only statements below describe preparation.

Not published or hardware validated. Release 15 public firmware is unchanged.
The existing nine level layouts are unchanged; a level redesign is separate work.

## Splash and HUD

The shared native/browser title screen places `FM-1/SMK` beneath the DOOM logo,
with the existing Start Game, Options and Controls menu below. The logo moves
eight pixels upward to make room. The subtitle uses the existing bitmap font;
it adds no image asset or framebuffer. The centered HUD face refinement already
available in the browser is also included in this native candidate.

## Enemy death crash

The owner reported an FM-1 renderer error while playing level 1 for roughly
30 seconds, then reported that the device worked again after reconnecting.
The photo shows `R_ProjectSprite invalid sprite frame 0`. This does not establish
that a bootloader interruption caused the failure.

The actual engine reproduces the failure when a guard or imp takes overkill
damage. Seventeen frames referenced by its extended death states were absent
from the compact artwork WAD: `POSS M..U` and `TROO N..U`. The imp reproduces
`R_ProjectSprite: invalid sprite frame 0 : 13`; the guard reproduces `29 : 12`.

The missing names now reuse the existing five-stage death artwork. Immutable
WAD deduplication avoids adding 31,387 bytes of separate extended-death images.
The engine retains its damage rules and state timing; this is not new gib art.
The host-only regression invokes real damage and sprite projection, requiring
visible projection for all 66 guard/imp states. The expanded asset coverage check
passes all 211 state references across the 23 included sprite families.

The owner later reported another invalid-sprite-frame error, transcribed as
"9 8 0", possibly on level 2. No revision 16 update had been performed in this
session. The exact diagnostic numbers are not confirmed and do not establish
the same cause; retain this as a separate report for the hardware retest.

## K1 volume and K2 menus

K1 adjusts music and effects together, from mute to full output. On FM-1 it is
multiplied by the physical MASTER setting, so regular ADC polling cannot undo a
K1 adjustment and MASTER can still mute the output. SMK starts at its previous
output level. FM-1 uses encoder indices 2/3; SMK uses 0/1 with four quadrature
transitions per detent. Physical direction and feel remain to be checked.

K2 clockwise scrolls down and counterclockwise scrolls up through active menus.
It uses the engine menu responder directly, skipping hidden entries, without
injecting movement keys into gameplay. It ignores confirmation/help screens.
White key 8 / Enter / SMK PARA still selects; white key 7 / Esc / PATCH goes back.
Both simulator panels support dragging, mouse wheel and keyboard arrow control.
Their volume controls stay synchronized, and K2 has no gameplay tick effect.

## Local validation

- Both formerly failing overkill cases and all sprite state checks pass.
- The actual host engine passes repeated nine-level campaigns at normal/low
  detail and hard difficulty, death/retry, and separate loading of all nine maps
  within the native 256 KiB zone and 24 KiB C heap limits.
- All three native targets compile. Offline update-package round trips pass,
  including protected-byte preservation. No device was contacted or flashed.
- The browser engine is rebuilt and its rendered splash visually checked.
  Menu/gameplay/audio and 2,000-tick soak checks pass, as do input ownership,
  44.1/48 kHz audio queues, Worker scheduling/pause and site integrity checks.
- Runtime and RAM-loader identities end in `_016`. Outputs remain ignored in
  `build/native/<board>/` and `build/test16-packages/`, separate from public 15.

| Target | Application bytes | Free within 581,564-byte limit |
| --- | ---: | ---: |
| FM-1 | 577,820 | 3,744 |
| SMK-37 Pro | 578,160 | 3,404 |
| SMK-37 Elite | 578,160 | 3,404 |

These are local build measurements, not evidence of physical acceptance.
Per-board manifests contain the corresponding SHA-256 values and memory totals.
