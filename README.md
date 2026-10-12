# Doom-FM1-SMK

A local experimental Doom port targeting the M-VAVE FM-1 and SMK-37 Pro / Elite.
Created by Chance Roth (@ChanceTheMaker).

## Current status

**FM-1 Test05 adds a three-level combat campaign.** Test04 is installed and its readable menus are confirmed on the FM-1. Test05 adds 18 enemies, a shotgun with new pixel art, health and ammo pickups, kill scoring and readable health/ammo/level indicators. Host combat, level transitions, campaign replay and death/retry pass under the native memory limits; Test05 is installed with matching full-flash readback; physical combat feedback is next. This repository is local-only, with no publication remote or deployment workflow.

The real Doom engine renders a 240x180 game view on the 240x240 LCD. Menus and the new HUD render at LCD resolution. There is **no sound, persistent saving, USB MIDI or USB updater**. Installing another build from Doom requires the XIAO adapter; the local normal-USB installer only works when the device is running synth firmware with a compatible updater.

Use [FM-1 Test05 instructions](docs/FM1_TEST01.md). The local package page is on port 8785. The old SMK candidate is withdrawn; SMK builds need their own hardware validation. Do not install an FM-1 package on an SMK.

The FM-1 Test05 application is 570,904 bytes. Data+BSS uses 434,640 bytes, including a 256 KiB Doom zone; a separate 24 KiB C heap is retained. The campaign playthrough peaks at 238,540 zone bytes. These are host/linker measurements, not measured native frame rate or full stack high-water.

## Build and test the campaign

Use Linux/WSL with GCC multilib, Python 3 and zdbsp 1.19. The asset generator authors three maps and original enemy, shotgun and wall art over checksum-pinned Miniwad assets. No commercial Doom data is included.

```sh
python3 tools/fetch_test_wad.py
python3 tools/pack_test_wad.py --trim-textures
python3 tools/build_campaign.py
python3 tools/build_host.py --board fm1 --no-wipe --mapped-wad --small-room --static-wad --bounded-heap --abi32 --campaign
python3 tools/check_campaign.py build/fm1/strip-no-wipe-mapped-small-static-heap24-abi32-campaign/doom-host
python3 tools/check_menu.py build/fm1/strip-no-wipe-mapped-small-static-heap24-abi32-campaign/doom-host --campaign
python3 tools/build_native.py --board fm1 --campaign --toolchain /path/to/jieli/toolchain
```

The three levels are **The Outpost**, **Iron Halls**, and **Reactor Core**. Guards award 100 points and imps 200. Face the wall switch in the last room and press Use to exit. Fire or Use advances at the results screen. Use retries after death; retry restores the score from level entry. Completing all three levels offers another run with a fresh score.

## Build and exercise the host

Use Linux or WSL with Python 3, GCC and binutils. From the repository:

```sh
git submodule update --init
python3 tools/fetch_test_wad.py
python3 tools/pack_test_wad.py --trim-textures
python3 tools/build_host.py --board smk37-pro --no-wipe --mapped-wad --small-room
python3 tools/check_adapters.py
python3 tools/check_play.py build/smk37-pro/strip-no-wipe-mapped-small/doom-host --zone 280
python3 tools/measure_host.py build/smk37-pro/strip-no-wipe-mapped-small/doom-host --wad miniwad-room --zones 384 320 288 280 272 256
python3 tools/report_memory_layout.py build/smk37-pro/strip-no-wipe-mapped-small/doom-host
```

The downloader explicitly fetches checksum-pinned [Miniwad](https://github.com/fragglet/miniwad). The compiler does not download assets. The packer accepts only that exact fixture, retaining MAP01 and necessary textures. This is a test room, not a complete campaign. License and provenance accompany the ignored assets in `build/fixtures/`.

The output is a **Linux executable**, not a JieLi firmware image. Use `--board fm1` or `--board smk37-elite` for the other profiles. `--display rgba` retains the original output-buffer path for comparison. Strip output is the default. `--no-wipe` disables the memory-intensive melt transition. `--mapped-wad` models immutable flash assets using Linux file mapping; it does not implement device flash access.

Checks create fresh session directories beside the executable with PPM images, logs and JSON reports. Aggregate reports are `play-check.json`, `miniwad-room-measurements.json` and `layout.json`.

## Run another IWAD

Supply a legally obtained compatible Doom IWAD locally:

```sh
mkdir -p build/session
cd build/session
DOOM_FRAME_LIMIT=120 DOOM_FRAME_OUTPUT=frame.ppm ../smk37-pro/strip-no-wipe-mapped-small/doom-host -iwad /absolute/path/doom1.wad -nosound -warp 1 1
```

The default host zone is 16 MiB; the 280 KiB result does not apply to arbitrary WADs. Output is a 240x240 PPM in strip mode, or 320x200 in RGBA mode. Run in a disposable build directory because Doom may write configuration files. The harness has scripted input only, no interactive window or audio.

## Port plan

Next: physically test Test05 combat on FM-1, then validate the SMK Pro and Elite separately. Sound and persistence follow only after memory and timing measurements. See [PORTING.md](docs/PORTING.md) and [TASKS.md](TASKS.md).

FM-1 and SMK update images must remain separate. Existing Felucca, Sloop and Melodee projects are unchanged. FM-1 Test04 has been flashed and tested; SMK Doom validation is still pending.

## License and assets

New code is GPL-3.0-only; see [LICENSE](LICENSE). [DoomGeneric](https://github.com/ozkl/doomgeneric) is pinned at `e257a09527062bfb986b6e5e0780839b6cbd5b71` and retains its upstream notices. See [THIRD_PARTY.md](THIRD_PARTY.md) and [Miniwad's notice](licenses/miniwad.txt). Commercial Doom assets, vendor packages, device backups and calibration dumps are not tracked.
