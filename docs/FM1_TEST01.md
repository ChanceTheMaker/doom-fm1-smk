# Historical FM-1 recovery and staging notes

**Current release: [Test06](TEST06.md). Use the [public installer](https://chancethemaker.github.io/doom-fm1-smk/).** The Test05 details below are retained as development history; Test06 adds confirmed graphics and sound, uses product `FM-1_995`, and still requires the adapter when already running Doom.

# FM-1 Test05

Test05 adds three connected-room levels, 18 enemies, a shotgun with original pixel art, pickups and readable score/health/ammo indicators. Guards award 100 points; imps 200. Face the wall switch in the final room and press Use to exit. Fire/Use continues at the level results screen; Use retries after death. After the third level, continue starts a fresh campaign. No sound or persistent saves.

Test04 was installed through the adapter with matching full-flash readback, and the user confirmed readable menus. Test05 passes host combat/progression/death checks. It has now been installed through the adapter; all 140 changed application sectors and the final 1 MiB readback match. Bootloader and device data are unchanged. Physical combat feedback is pending.

**Already running Doom:** use the XIAO adapter update procedure; Doom has no USB updater. The normal-USB page cannot detect the running game.

Open the local FM-1 installer at `http://127.0.0.1:8785/`. Connect the FM-1 directly by normal USB while running firmware with the standard FM-1 MIDI updater. Close other MIDI applications. Have the FM-1 XIAO recovery adapter ready, but leave it disconnected during normal USB installation. The installer rejects SMK identities and never starts automatically.

The package is derived from the pinned Felucca Salt14 FM-1 release (package SHA-256 `efb516a7131d12eb5c008ff9af5a380d07e82eb1040bd03990f28d1233417e28`). It retains its loader byte-for-byte (`2c9f43bf7dff81a953c07f3c82cedf5f5899aac14e5b62c2cb23ba7f560ce7db`). Only application bytes, their CRC fields, and the enclosing package metadata change. Package identity is `FM-1_994`; that identity is for installation only because Doom has no MIDI stack.

The inherited loader writes application sectors `0x4000..0x93000`, validates the chip key, and verifies sectors. It preserves the bootloader. The running synth stages the loader and the loader clears its update records outside that range, so this is not a promise that no update-metadata flash is touched. Back up synth projects using that synth before installing.

## First check

Expected: `DOOM TEST 05`, then The Outpost with a shotgun and a guard ahead. Count white touch keys from the left: turn left, forward, turn right, back, fire, use, menu, enter, run, strafe left, strafe right. Test movement and release. No sound is expected. Photograph any `DOOM STOPPED` message; report a black screen rather than repeatedly reinstalling.

## Return to synth firmware

USB MIDI disappearing is expected after installation. Hold both OCT buttons for two seconds to request ROM recovery if the scanner works. Otherwise use the XIAO FM-1 power-off/USB-key recovery procedure that previously restored this device. This build's software shortcut is not hardware-validated yet.

`build/try-fm1/felucca-salt14-restore.fwsc` retains the known source release. `felucca-restore-application-region.bin` is **only** its application region, intended for the FM-1 bounded adapter writer at offset `0x4000`, length `0x8f000`. It is not a full flash image. Obtain two matching fresh reads first, preserve the current prefix and tail, precheck each sector, and verify all written bytes. The SMK restore planner/writer bounds do not apply. No device writes are performed by the staging script.

The previous successful FM-1 adapter recovery and verified readback are recorded locally in `Felucca/recovery-backups/bad-fm1-20261010T210809Z/restore-result.json`. That is evidence for the adapter procedure, not evidence that this Doom build works. Use fresh device reads for any new restore, especially if testing the other FM-1.

## Rebuild package

```powershell
python tools/stage_fm1_test.py --base ../Felucca/Felucca-site-publish/firmware/felucca-0.9-salt14.fwsc
python -m http.server 8785 --bind 127.0.0.1 --directory build/try-fm1/site
```

Native app details and limitations are in `docs/NATIVE_TEST01.md`. Both native runtime tests and package checks run without hardware. Test02 booted and accepted movement input on FM-1. The adapter replacement of Test01 was fully read back and verified. Test03 gameplay and recovery shortcut remain to be tested on hardware.

## Test02 memory regression checks

Test01 tried to allocate 2,097 lump records (58,716 bytes on the native 32-bit ABI) from a 24,576-byte C heap. Test02 generates an immutable directory in XIP flash and validates the mapped WAD directory against it before use. There is no runtime directory allocation or mutable hash-chain allocation. Additional WADs are deliberately rejected.

A new 32-bit host build uses the actual bounded C allocator for engine allocations. It also revealed that the old 240 KiB zone was too small during rendering. For this single-player test, reducing command history from 128 to 16 tics recovers space for a 256 KiB zone without moving the stack or boot-record boundaries. The 120-frame play test crosses the smaller ring repeatedly.

Reproduce the stronger check:

```sh
python3 tools/build_host.py --board fm1 --no-wipe --mapped-wad --small-room --static-wad --bounded-heap --abi32
python3 tools/check_play.py build/fm1/strip-no-wipe-mapped-small-static-heap24-abi32/doom-host --zone 256 --static-room
```

This requires GCC multilib. It verifies startup, movement, turning, firing and release with an identical reference frame. It still does not emulate the JieLi processor or scanner. The error display now clears stale loader pixels and explicitly labels the OCT recovery shortcut.

Final Test02 validation: the 32-bit host completed four 120-frame runs with a 262,144-byte zone (peak 248,612 bytes) and the native C allocator (peak 312 bytes, no failures). FM-1 binary: 539,900 bytes; data+BSS: 434,624 bytes including the zone. The linker places all 58,716 directory bytes in XIP at `0x02034e44`. Firmware SHA-256: `5bd39672416887b69415fec7d13702eef0d6cb9742751f3f868215f8f710a35b`.

## Test03 turning regression

The Test02 host checks covered only 120 frames and a short turn. A longer right turn reproduces the exact hardware error: the 16,384-byte DLEVSIGN composite plus the 24-byte zone header cannot be allocated. Idle and menu tests do not reproduce it. This is a rendering allocation failure, not a damaged installation.

`tools/static_textures.py` builds all six composite textures reachable in the embedded room, including both switch states, into immutable column data. Deduplication needs 2,688 pixel bytes plus 960 index bytes in XIP. The renderer returns those columns directly rather than allocating composites during play. Non-room textures retain the original path. The WAD and RAM/stack layout are unchanged.

The regression first reproduces the old failure, then compares five 10,500-frame scenarios (right/left turns, movement/fire/use, strafe/back, and repeated menus) against the original compositor with a larger host zone. Every composite column and each final frame match byte-for-byte. The fixed build uses the device's 256 KiB zone and 24 KiB C heap, with no C-heap allocation failures. These are accelerated host tests, not real-time hardware endurance tests.

```sh
python3 tools/build_host.py --board fm1 --no-wipe --mapped-wad --small-room --static-wad --bounded-heap --abi32
python3 tools/build_host.py --board fm1 --no-wipe --mapped-wad --small-room --static-wad --bounded-heap --abi32 --reference-textures
python3 tools/check_navigation.py build/fm1/strip-no-wipe-mapped-small-static-heap24-abi32/doom-host build/fm1/strip-no-wipe-mapped-small-static-heap24-abi32-reference/doom-host
```

FM-1 Test03 application: 543,784 bytes, SHA-256 `a924d3fe640389d8140e510f8db23d010e6c2b1e4a39729ddbd6f9c91a07c86a`. Data+BSS remains 434,624 bytes. Test01 and Test02 are withdrawn; do not repeat their installation.

## Test04 readable menus

The original Miniwad menu artwork is tiny and loses letter strokes in the 320x200-to-240x180 nearest-neighbor conversion. Test04 displays menus directly at 240x240, using 14-pixel-high text with complete 2x2 strokes, a solid selection highlight, titles, and option values. Gameplay scaling is unchanged. The display snapshots the engine's current menu and selected item; the original menu navigation remains in charge.

White keys from the left: **2 up, 4 down, 1/3 adjust, 8 select, 7 close/cancel**. Select also confirms yes/no prompts. Save/load selections show an unavailable notice because this build has no save storage; they do not attempt filesystem writes. Sound remains disabled.

Twelve host cases cover main/options/difficulty/sound pages, changed values, confirmations, cancel, and save/load notices. An ASan/UBSan renderer test checks full-size glyph strokes, longest message rows, bounds and output failure. The original gameplay frame hashes and five extended navigation scenarios still pass. Native FM-1 application: 546,792 bytes; SHA-256 `6ef85fcee41f5fa72d9736dadf0c5d8889520397f0599118526bf8b69c313789`. Data+BSS remains 434,624 bytes; menu state uses bounded stack storage, not dynamic allocation.

```sh
python3 tools/check_menu.py build/fm1/strip-no-wipe-mapped-small-static-heap24-abi32/doom-host
```

## Test05 campaign verification

The deterministic host driver uses normal movement, aiming, fire and use key events. It never teleports the player, gives health or kills enemies directly. Three 8,000-frame runs cover the campaign in high/low detail and a harder difficulty; each clears all levels repeatedly, scores the expected 2,600 points in a clean run, and stays inside the 256 KiB zone and 24 KiB C heap. A separate idle run exercises enemy damage, death and retry. Three previews check direct level startup. These accelerated checks do not measure physical frame rate.

Application: 570,904 bytes; SHA-256 `07d48f0761c2aaaac0997c4bc1218b3ab5235f668389069598413f9047607ab7`. Data+BSS: 434,640 bytes. Campaign assets: 226,024 bytes, SHA-256 `c6474d4196278e1e790cd09529ccb483a9a0a2122fe97db0c28298d058aa2ce6`. Original authored map/sprite/wall source is `tools/build_campaign.py`; its Miniwad base retains the existing asset notices.

Test05 installation readback SHA-256: `4551cbb56f49bdad0763aad2f9b55961e0102c775a311b825a345d673f39e2f2`. Private recovery backups and the per-sector journal are retained under the ignored `build/try-fm1/` directory.
