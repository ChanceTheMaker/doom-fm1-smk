# FM-1 / SMK Doom port design

## Scope

Standalone game firmware with shared engine code and separate board adapters. Running Doom concurrently with a synthesizer is outside the first milestone. The initial host baseline is a measuring tool, not an embedded-ready engine.

## Hardware evidence

Based on the existing local `sloop-smk/docs/smk37/HARDWARE_COMPARISON.md` (reviewed 2026-10-10) and existing firmware linker/driver definitions:

| Property | FM-1 | SMK-37 Pro / Elite |
| --- | --- | --- |
| CPU family in stock packages | JieLi AC791N / AC79 | Same family |
| Boot clock request | 360 MHz | 360 MHz |
| Main SRAM address window | 512 KiB | Same linker window |
| LCD | 240x240 | 240x240 |
| Flash evidence | 1 MiB driver profile | 1 MiB physically read on Pro; Elite layout inferred from stock package |
| Performance keys | 27 touch keys | 37 piano keys plus 16 pads |
| External SDRAM at boot | Disabled | Disabled |

The requested boot clock is not a measured runtime frequency. The SRAM window includes code, stacks and reserved boot records; it is not all free heap. Elite physical characteristics need their own device checks. Do not change PLL settings to try to force performance before establishing the inherited clock configuration.

## Memory / rendering

DoomGeneric currently requests a 32-bit output buffer; at 320x200 that alone is 256,000 bytes, in addition to the engine's internal screen, heap and static memory. Compiling it successfully on Linux says nothing about embedded fit.

Proposed embedded starting point: paletted rendering, a small level, reduced working sets, and RGB565 conversion one LCD strip at a time. A complete 240x240 RGB565 framebuffer costs 115,200 bytes; avoid double buffering by default. Select final rendering resolution after inspecting the engine, rather than setting unsupported Doom internal dimensions blindly. Preserve the image aspect ratio when fitting to the square LCD.

Flash is the likely asset bottleneck. Our existing music application slot is about 568 KiB, much less than the chip's full capacity. Bootloader, calibration and other persistent regions must not be treated as game storage. Determine a Doom-specific safe layout separately; never reuse an FM-1 flash writer on SMK by assumption. Start with one small level and stripped assets, not the complete shareware WAD.

## Adapter boundaries

- Shared: Doom engine, action mapping, asset decoder, frame palette conversion.
- Per family: startup/linker map, timers/watchdog, LCD transport, scanner and audio DMA.
- Per model: calibration/profile validation and update identity (Pro versus Elite).
- Host only: standard filesystem, Linux clock and memory allocation, PPM writer.

Proposed actions: piano/touch keys for forward/back/turn/strafe, separate keys or pads for fire/use/run/menu. All actions need press AND release. Analog wheels and encoder-based weapon selection are optional after digital control validation. Actual note/button assignments remain configurable until physical testing.

## First device milestone

1. Prove a minimal host level and record memory use.
2. Prove native startup, LCD strips and controls independently on each board.
3. Render the same small level without audio or persistence.
4. Add effects and measure frame latency, watchdog margin and input responsiveness.
5. Only then prepare separately identified FM-1 and SMK update packages.
