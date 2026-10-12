# Native Test01 — private device test

Built 2026-10-11. No hardware was flashed during preparation. Compilation and host checks are not proof of a successful hardware boot.

## Try the SMK-37 Pro build

The local kit is `build/try-smk-pro/`. Serve only its `site` subdirectory, bound to loopback:

```powershell
python -m http.server 8784 --bind 127.0.0.1 --directory build/try-smk-pro/site
```

Open `http://127.0.0.1:8784/` in Chrome or Edge. Connect the same SMK Pro used for the verified stock backups by normal USB, running updater-enabled Felucca/Sloop/Melodee SMK. Close other MIDI applications. Keep the XIAO recovery adapter and the private restore kit available. Read the notice and click Install only when ready. Do not connect the recovery adapter during normal USB installation.

The package is unit-bound by boot-header and calibration CRCs, using the existing V1 SMK updater format. Browser validation checks package identity, SHA-256, header CRC, data CRC and each sector CRC. The device updater remains responsible for checking the unit and restricting flash writes to `0x4000..0x9d000`. The page does not accept FM-1 or stock 016 first-install targets.

After transfer, USB MIDI disappearing is expected: this test build has no USB stack. Transfer completion is not proof that Doom booted. Look for `DOOM TEST 01`, then the room. A brief startup message may be followed by loading time. If the display says `DOOM STOPPED`, photograph the complete message. If it stays black, stop and inspect rather than repeating installation.

## Controls

Count white keys from the far left of the physical keyboard:

| White key | Action |
| --- | --- |
| 1 | Turn left |
| 2 | Forward |
| 3 | Turn right |
| 4 | Backward |
| 5 | Fire |
| 6 | Use / open |
| 7 | Menu |
| 8 | Enter |
| 9 | Run, held with movement |
| 10 | Strafe left |
| 11 | Strafe right |

On SMK, PATCH also opens the menu and PARA selects. Pads, wheels and knobs are not mapped yet. The room is intentionally small and silent; this is not the commercial Doom campaign. Save/load menu functionality is unsupported.

Hold both OCT buttons for two seconds to request ROM recovery. That shortcut requires working input scanning; the adapter power-off/USB-key procedure remains the fallback. The retained boot guard requests recovery after repeated unfinished boots, but retention and recovery behavior still require physical validation.

## Restore synth firmware

Doom cannot receive a normal browser firmware update. Use the SMK-capable XIAO recovery adapter, as previously used with this device. The kit retains the two-read-verified original stock image as `stock-restore.bin`; it is private and must never be programmed wholesale.

Before restoring, obtain two matching fresh full-flash reads through the adapter. This offline command verifies the kit and current application, then prepares a bounded stock restore plan:

```powershell
python tools/plan_restore.py --reads fresh-read-1.bin fresh-read-2.bin --out build/restore-plan
```

It writes files only, never a device. Its reference image preserves the **current** bootloader, calibration and persistent data outside `0x4000..0x9d000`. A subsequent adapter operation must check the SMK writer bounds, precheck each changed sector, write only the listed application sectors, read each back, and verify the final image. The old test-build bootstrap scripts have different hash pins and must not be used unchanged. An interrupted or unexpected application fails the planner and requires inspection.

Restoring stock does not convert projects created by custom synth firmware. To return directly to that synth, use its separately verified application image and the same bounded recovery procedure.

## Build from source

In WSL Ubuntu-22.04, after initializing submodules and preparing the pinned trimmed fixture:

```sh
python3 tools/build_native.py --board smk37-pro --toolchain /mnt/e/AI_Apps/Felucca/Felucca-review/.build-deps/jieli/toolchain
```

Repeat with `--board fm1` and `--board smk37-elite`. Each produces its own application binary, ELF, linker-section report and hash manifest under `build/native/<board>/`. These are raw application binaries, not interchangeable installer packages.

For this owner's private Pro kit only:

```powershell
python tools/stage_smk_test.py --backups path/to/flash-read-1.bin path/to/flash-read-2.bin --stock-package path/to/pro016.fwsc
```

The packager validates both reads against the pinned stock package, checks calibration, replaces only the application, and checks protected bytes. Re-stage after any native or installer changes. Do not serve the kit's parent directory: it contains private full-flash images.

## Measured limits and checks

| Target | Application bytes | Data + BSS | Doom zone | Separate C heap |
| --- | ---: | ---: | ---: | ---: |
| FM-1 | 481,896 | 436,600 | 245,760 | 24,576 |
| SMK Pro | 482,000 | 436,640 | 245,760 | 24,576 |
| SMK Elite | 482,004 | 436,640 | 245,760 | 24,576 |

Data + BSS includes the Doom zone. Stack/reserved regions are additional. Linker assertions bound application flash and main SRAM. Stack canaries are checked after frames. The requested boot clock is inherited rather than reconfigured.

The reduced renderer uses 64 draw segments, 32 visible sprites, 32 visplanes and bounded openings. The same host movement/turn/fire/release test renders an identical image with the reduced limits. Host 64-bit play passes with a 280 KiB zone; the native 32-bit build has a 240 KiB zone whose real runtime sufficiency is still unmeasured.

Runtime allocator/read-only-file tests pass with AddressSanitizer and UndefinedBehaviorSanitizer. Package corruption, truncation and wrong-hash tests pass. Restore-plan tests reject mismatched reads and unknown applications while preserving current non-application data.

Outstanding: native boot, heap/stack high-water, LCD orientation, key mapping/release, frame rate, ROM recovery, and a complete restore cycle. FM-1 has a separate local test installer: see [FM1_TEST01.md](FM1_TEST01.md). Both FM-1 and Elite still need separate physical checks; Elite also needs packaging. Sound, normal USB updating, additional levels and persistence are future work.
