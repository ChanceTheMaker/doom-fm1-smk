# Doom-FM1-SMK

A local experimental Doom port targeting the M-VAVE FM-1 and SMK-37 Pro / Elite.
Created by Chance Roth (@ChanceTheMaker).

## Current status

**Doom renders and executes a scripted play test on the host. No flashable firmware or confirmed device compatibility yet.** This local repository has no publication remote or deployment workflow.

- Shared 240x240 LCD conversion: 240x180 active view, black letterboxing, RGB565 rows.
- Removed the additional 256,000-byte RGBA output buffer; the engine's indexed screen remains.
- Read-only mapped assets and a reduced open-content test room.
- Movement, turning, firing and key release pass with a 280 KiB engine zone on Linux/WSL.
- Memory reports, deterministic frame comparisons, and display/asset-boundary tests.
- Separate FM-1, SMK-37 Pro and Elite profiles; these select metadata, not working hardware drivers.

Total device memory fit remains unresolved. The host executable still has 354,756 bytes of writable static data, plus its zone, stack and other allocations. Its 64-bit ABI differs from the native processor. See [baseline results](docs/BASELINE_RESULTS.md).

## Build and exercise the host

Use Linux or WSL with Python 3, GCC and binutils. From the repository:

```sh
git submodule update --init
python3 tools/fetch_test_wad.py
python3 tools/pack_test_wad.py --trim-textures
python3 tools/build_host.py --board smk37-pro --no-wipe --mapped-wad
python3 tools/check_adapters.py
python3 tools/check_play.py build/smk37-pro/strip-no-wipe-mapped/doom-host --zone 280
python3 tools/measure_host.py build/smk37-pro/strip-no-wipe-mapped/doom-host --wad miniwad-room --zones 384 320 288 280 272 256
python3 tools/report_memory_layout.py build/smk37-pro/strip-no-wipe-mapped/doom-host
```

The downloader explicitly fetches checksum-pinned [Miniwad](https://github.com/fragglet/miniwad). The compiler does not download assets. The packer accepts only that exact fixture, retaining MAP01 and necessary textures. This is a test room, not a complete campaign. License and provenance accompany the ignored assets in `build/fixtures/`.

The output is a **Linux executable**, not a JieLi firmware image. Use `--board fm1` or `--board smk37-elite` for the other profiles. `--display rgba` retains the original output-buffer path for comparison. Strip output is the default. `--no-wipe` disables the memory-intensive melt transition. `--mapped-wad` models immutable flash assets using Linux file mapping; it does not implement device flash access.

Checks create fresh session directories beside the executable with PPM images, logs and JSON reports. Aggregate reports are `play-check.json`, `miniwad-room-measurements.json` and `layout.json`.

## Run another IWAD

Supply a legally obtained compatible Doom IWAD locally:

```sh
mkdir -p build/session
cd build/session
DOOM_FRAME_LIMIT=120 DOOM_FRAME_OUTPUT=frame.ppm ../smk37-pro/strip-no-wipe-mapped/doom-host -iwad /absolute/path/doom1.wad -nosound -warp 1 1
```

The default host zone is 16 MiB; the 280 KiB result does not apply to arbitrary WADs. Output is a 240x240 PPM in strip mode, or 320x200 in RGBA mode. Run in a disposable build directory because Doom may write configuration files. The harness has scripted input only, no interactive window or audio.

## Port plan

Next: reduce renderer working sets, measure a native build, then implement separate board startup, LCD and input adapters. First hardware milestone: one room with movement and fire. See [PORTING.md](docs/PORTING.md) and [TASKS.md](TASKS.md).

FM-1 and SMK update images must remain separate. Existing Felucca, Sloop and Melodee projects are unchanged. No device has been accessed or flashed by this work.

## License and assets

New code is GPL-3.0-only; see [LICENSE](LICENSE). [DoomGeneric](https://github.com/ozkl/doomgeneric) is pinned at `e257a09527062bfb986b6e5e0780839b6cbd5b71` and retains its upstream notices. See [THIRD_PARTY.md](THIRD_PARTY.md) and [Miniwad's notice](licenses/miniwad.txt). Commercial Doom assets, vendor packages, device backups and calibration dumps are not tracked.
