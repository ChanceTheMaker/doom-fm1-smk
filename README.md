# Doom-FM1-SMK

A local experimental Doom port targeting the M-VAVE FM-1 and SMK-37 Pro / Elite.
Created by Chance Roth (@ChanceTheMaker).

## Current status

**FM-1 Test04 adds readable full-resolution menus. Test03 is running on the user's FM-1 after fixing the turning crash; the user could open menus, but the scaled test-WAD lettering was barely readable. Test04 adds crisp text, selection highlights, visible option values, Select-key confirmations, and explicit notices for unavailable saves. Host checks pass; physical Test04 validation is pending. Test01 and Test02 remain withdrawn, including the old SMK candidate.** This repository has no publication remote or deployment workflow.

The build embeds a small open-content Miniwad room in application flash. It uses the real Doom engine, a 240x180 RGB565 view on the 240x240 LCD, piano-key movement/fire controls, and separate FM-1/SMK startup and scanner drivers. It has **no sound, saves, USB MIDI, or USB updater**.

For the first FM-1 test, use [FM-1 Test04 instructions](docs/FM1_TEST01.md) and the local installer on port 8785. [Historical SMK instructions](docs/NATIVE_TEST01.md) describe the private Pro workflow; its old candidate on port 8784 is withdrawn pending the FM-1 menu check. The private Pro package is tied to the owner's verified backup. Elite currently has an application binary only; do not install an SMK package on FM-1.

Test03 stores its fixed lump directory and room composite texture columns in flash and uses a 256 KiB Doom zone plus a separate 24 KiB C heap. A 32-bit host gameplay test now exercises those limits. See the generated native manifest for section sizes. Linker bounds and runtime allocator tests pass. Actual heap/stack high-water, LCD orientation, controls and frame rate still need a device test.

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

Next: test native startup, the LCD, movement and fire on the SMK Pro, then validate the FM-1 and Elite separately. Sound and persistence follow only after memory and timing measurements. See [PORTING.md](docs/PORTING.md) and [TASKS.md](TASKS.md).

FM-1 and SMK update images must remain separate. Existing Felucca, Sloop and Melodee projects are unchanged. No device has been accessed or flashed by this work.

## License and assets

New code is GPL-3.0-only; see [LICENSE](LICENSE). [DoomGeneric](https://github.com/ozkl/doomgeneric) is pinned at `e257a09527062bfb986b6e5e0780839b6cbd5b71` and retains its upstream notices. See [THIRD_PARTY.md](THIRD_PARTY.md) and [Miniwad's notice](licenses/miniwad.txt). Commercial Doom assets, vendor packages, device backups and calibration dumps are not tracked.
