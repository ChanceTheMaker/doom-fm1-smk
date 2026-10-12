# Test10: lower-cost music rendering

Release 10 music build, accepted on FM-1 and SMK-37 Pro over normal USB.
Published on 2026-10-12 in commit 0a77485. Pages deployment succeeded; all three live application hashes were independently verified. Test09's owner check confirmed music,
effects, volume and HUD, but reported gameplay slower than Release 08.
The FM-1 owner accepted this optimized build as-is: “It's fien for now push it.”
This is release acceptance, not a measurement of frame-rate parity with Release 08.
The Pro owner subsequently confirmed steady HUD, music, sound effects and
acceptable gameplay speed: “Everything works.” Elite hardware testing is pending.

“Circuit Breaker” is an original eight-bar, 140 BPM heavy loop with power-chord
riff, bass, kick, snare and hats. Its GPL-3.0-only score and synthesizer contain
no commercial Doom music or sampled audio. Options → Sound → Music sets its gain;
music volume zero preserves the clock, pause holds the position, and a level
change restarts the loop.

The music synthesis now runs at 11025 Hz, with linear interpolation to the
existing 44100 Hz stereo mixer. This runs the oscillator, percussion and envelope
work once per four output samples. Sound effects keep their original sample
rate. The sequencer carries fractional step timing to retain 140 BPM without
drift, and pause holds the interpolation position as well as the score position.
Constant power-of-two scaling replaces the music path's divisions by 127 and
98304. There is no PCM buffer, heap allocation, extra core or new framebuffer.
The four-sample interpolation state adds 8 bytes to linked data/BSS after
alignment (FM-1: 437272 bytes, still below Release 08's 438280).

## Evidence

- All three native builds and package round-trip/protected-byte checks passed.
- Music regression passed with address/undefined-behavior sanitizers; effects
  regression and real native LCD row-dispatch regression passed.
- Runtime identities are `Doom-FM-1_010` / `Doom-SMK-37_010` and package products
  are `FM-1_999` / `SMK-37_999`. Installer boot checks reject prior `_009`.
- The connected FM-1 was queried and verified as `_009` before the update.
- The isolated normal-USB installer at `http://127.0.0.1:18810/#install`, serving
  only `build/test10-site/`, transferred the candidate through
  `ota-Doom-FM-1_009` and confirmed runtime `Doom-FM-1_010` after restart on
  2026-10-12. The owner accepted the result as-is; reduced synthesis work alone
  does not prove restored gameplay speed on hardware.
- SMK-37 Pro was identified as stock `SMK-37 Pro_016`, entered its official
  `ota-SMK-37 Pro_016` loader, completed the transfer and restarted as
  `Doom-SMK-37_010`. The owner confirmed the physical game, steady HUD, music,
  effects and acceptable speed on 2026-10-12. This was normal USB, without the
  recovery adapter, and is distinct from the earlier Pro Test07 validation.
- Public app filenames use `doom-<board>-10.bin`; their bytes and hashes are
  identical to the candidates below. Historical release 08 artifacts remain
  immutable. The website displays “Release 10”; internal package and build
  identifiers retain `TEST10` for protocol compatibility and traceability.

| Model | Application bytes | SHA-256 |
| --- | ---: | --- |
| FM-1 | 532424 | `bf6b7d24d6907910a143a73ffe1af019eeae22d33b09b843d788cee2206c373a` |
| SMK-37 Pro | 532564 | `a5847d71f5459beb4fc37f099796ae38762e632e5feef84e48cc1981b502341f` |
| SMK-37 Elite | 532568 | `956462034c0cfcab4fdf49783f9b557977422bf01255d1c0822de277168dca23` |

The Test09 FM-1 binary, its original synthesizer source and USB-install evidence
are retained privately in `build/music-test09/`. Vendor packages and recovery
backups are excluded from publication. Browser simulator source inputs include
music; its generated JS/Wasm still needs rebuilding during integration.
