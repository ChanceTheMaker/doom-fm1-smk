# Doom-FM1-SMK

A local experimental Doom port targeting the M-VAVE FM-1 and SMK-37 Pro / Elite.
Created by Chance Roth (@ChanceTheMaker).

## Current status

Initial repository and host engine baseline. **No flashable firmware or confirmed device compatibility yet.** The Doom engine is pinned as a submodule; each board has an explicit profile. Existing Felucca, Sloop and Melodee projects are unchanged. This repository has no publication remote or deployment workflow.

- Engine: [DoomGeneric](https://github.com/ozkl/doomgeneric), revision `e257a09527062bfb986b6e5e0780839b6cbd5b71`.
- Targets: `fm1`, `smk37-pro`, `smk37-elite`.
- First milestone: one small level on the physical LCD with movement and fire.
- Host baseline: headless Doom renderer producing a PPM frame, without MIDI or hardware access.
- Native targets: display, input, timing, memory allocation and asset storage adapters remain to be implemented.

## Build the host baseline

Linux or WSL, Python 3 and a C compiler:

```sh
git submodule update --init
python3 tools/build_host.py --board fm1
python3 tools/build_host.py --board smk37-pro
python3 tools/build_host.py --board smk37-elite
```

These all build a **Linux host executable**, not a JieLi firmware image. Board selection records the intended hardware and checks its profile; it does not implement board drivers.

Supply a legally obtained Doom IWAD locally (game assets are not included):

```sh
mkdir -p build/session
cd build/session
DOOM_FRAME_LIMIT=120 DOOM_FRAME_OUTPUT=frame.ppm ../smk37-pro/doom-host -iwad /absolute/path/doom1.wad -nosound -warp 1 1
```

The host renderer exits after the selected number of frames and writes a 320x200 PPM. It has no interactive controls or audio yet. Run it from a disposable build directory because Doom may write configuration files. A successful host build does not establish device RAM fit or performance.

## Initial verification

The pinned engine and host adapter compile successfully with GCC under WSL. All three target profiles parse and retain explicit not-yet-implemented native status. No IWAD has been run and no device has been accessed. Upstream C sources emit compiler warnings; they remain unchanged in the pinned dependency.

## Port plan

See [PORTING.md](docs/PORTING.md) for the hardware budget, adapter boundaries and milestones, and [TASKS.md](TASKS.md) for the work queue. Hardware drivers and update packages must be separate per family; an SMK binary is never an FM-1 binary.

## License and assets

New project code is GPL-3.0-only; see LICENSE. DoomGeneric remains under its upstream notices and license in the pinned submodule. See [THIRD_PARTY.md](THIRD_PARTY.md) for provenance. Doom game data is separate from engine source and is not included. No vendor packages, device backups or calibration dumps are tracked.
