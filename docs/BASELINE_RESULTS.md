# Host baseline ? 2026-10-11

## Rendering

DoomGeneric renders Miniwad MAP01 through the normal game loop. Shared LCD conversion produces a 240x240 image with a 240x180 active view and 30-pixel top/bottom bars, preserving Doom's intended 4:3 display aspect ratio.

The strip path keeps the 64,000-byte indexed engine screen but avoids the extra 256,000-byte RGBA screen. Conversion uses a 480-byte row and 512-byte palette. The sink must consume each row synchronously; an asynchronous LCD driver needs explicit buffer-lifetime handling.

## Zone memory

Measured on x86-64 Linux/WSL, GCC -O2, 120 frames, no sound or melt wipe. Zone figures include block headers; they exclude other malloc allocations, static data, stack, mapped pages and OS overhead.

| Configuration | Peak non-purgeable zone bytes, idle | Result |
| --- | ---: | --- |
| Original Miniwad, standard file cache | 602,136 | 16 MiB passes; 512 KiB fails |
| Original Miniwad, read-only mapping | 580,024 | 16 MiB passes; 512 KiB fails |
| MAP01-only, read-only mapping | 577,296 | 16 MiB passes; 512 KiB fails |
| MAP01 + trimmed textures, read-only mapping | 268,976 | 280 KiB passes; 272 KiB fails |

The trimmed room's peak allocated zone size including purgeable blocks is 283,432 bytes idle, 283,960 during movement/fire. Non-purgeable peak remains 268,976. Zones of 288, 320 and 384 KiB also pass. **280 KiB is the smallest tested passing zone, not a guarantee for other views, maps or longer sessions.**

Host mapping exercises Doom's mapped-WAD path and avoids copies into the zone, but still consumes host memory through mapped pages. Direct device flash access is unimplemented.

## Play test

`tools/check_play.py` uses one game tic per rendered frame. Six key events exercise forward press/release, right-turn press/release and fire press/release. Over 119 elapsed gameplay tics, position and angle change, bullets decrease from 50 to 47, and the tested movement/fire commands return to released state.

Original assets at 16 MiB and trimmed assets at 280 KiB produce the same final image. Independent trimmed runs agree; the play image differs from the idle image.

- Idle PPM SHA-256: `09581ee8db0b5a2c0c0ea79410eec225154c5cc632f23afc3a5bcb3c976afb61`
- Movement/fire PPM SHA-256: `9039fbabf77d34201496b57d78c06ee636d307ac198139c6bbbf5d5800d1d5cb`

This short path does not establish full-game compatibility, device controls, audio or frame-rate performance. Fixed-tic execution bypasses wall-clock pacing.

## Static data and stack

Current instrumented mapped-strip host ELF:

| Section | Bytes |
| --- | ---: |
| Text/read-only section reported by size | 402,287 |
| Data | 82,748 |
| BSS | 272,008 |
| Writable static data + BSS | 354,756 |

Largest writable symbols: visplanes 84,992; openings 40,960; states 38,680; ticdata 20,480; several rendering arrays 16,384 bytes each. A 280 KiB reserved zone plus static sections already totals 641,476 bytes, exceeding the devices' 512 KiB SRAM window before other costs.

Largest compiler-reported individual stack frame: I_Error, 784 bytes. LCD conversion uses 576 bytes including its row and local overhead. These are **not whole-call-chain stack peaks**, particularly with recursive BSP traversal. Native stack high-water measurement remains required.

Host pointer widths, C library, instrumentation and linker behavior differ from native pi32v2. These measurements locate problems; they cannot replace the native linker map or prove RAM/flash fit.

## Assets

Source: [Miniwad](https://github.com/fragglet/miniwad), with its [retained license](../licenses/miniwad.txt). The source is 230,497 bytes. The packed room is 201,152 bytes, keeps 2,097 lumps, aligns payloads to four bytes and deduplicates identical payloads. Texture definitions drop from 638 to 159, retaining room textures, engine switch pairs and animation ranges. Patch indices remain unchanged.

- Source SHA-256: `daed5e9dc341a9ff4b9c6901cb8467a630bd31b87f3ecb58a93a8b2bc186fbfb`
- Trimmed room SHA-256: `5382808534297f82d29873d9132410dcb20f314e01f58f1ec4c653f7f0ddf98d`

Only MAP01 remains; exiting to MAP02 is unsupported. This is a purpose-built fixture, not a general WAD optimizer or install package. The approximately 568 KiB music application slot must eventually hold native code and assets; no game-specific flash layout is established.

## Validation

Reproduction commands are in [README](../README.md). Download checks verify archive and WAD hashes. Packing reproduces the hash above. Portable C tests cover LCD mapping/letterbox rows, sink failure, null inputs, and WAD header/directory/lump bounds and overflow cases. WAD envelope validation does not validate every internal map/texture structure.

Reports and images remain under ignored build/. Upstream is unchanged; instrumentation is appended only to a generated source copy. No hardware or MIDI devices were accessed.
