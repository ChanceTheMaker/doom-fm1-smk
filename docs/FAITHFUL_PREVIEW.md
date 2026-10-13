# Faithful presentation preview — local revision 15

Historical development notes. Release 15 subsequently passed the FM-1 hardware
check; current release evidence is in [RELEASE15.md](RELEASE15.md).

Development worktree: `E:\AI_Apps\Doom-FM1-SMK-faithful`, branch
`feat/faithful-presentation`, based on published Release 14 (`f522001`).
The original dirty simulator checkout and the release worktree are preserved.
Public Release 14 binaries and its installer manifest are unchanged.

## Implemented

- Classic DOOM logo with a real title menu: Start Game, Options, Controls.
  Start Game uses the engine's difficulty selection. Menu/white key 7 returns
  through submenus, then closes the root menu to resume the game.
- Detailed Freedoom pistol, fist and shotgun view sprites. White key 12 cycles
  owned weapons; browser keyboard R or `]` does the same.
- Classic 240×30 status bar with ammo, health, face, armor, weapon ownership,
  keys and ammunition totals. Gameplay still sends each LCD row once.
- MAP01 has a looping route, optional secret room, a working manual door,
  stepped floors, varied ceiling heights and lighting, and shaped corners.
  All nine levels get patterned floor/ceiling tiles. The other eight maps
  retain their existing layout; these remain original maps, not id's campaign.
- Browser simulator with FM-1, SMK-37 Pro and Elite device views, using the
  shared engine and the same LCD assets. SMK layout derives from Sloop;
  previous FM-1 simulator work is preserved and integrated. One Worker drives
  both screens, audio and inputs. Model switching releases held controls.
  Inactive synth controls are deliberately disabled; no MIDI access is used.

The logo is separately credited in `assets/branding/provenance.json` and is
not claimed as GPL or Freedoom artwork. Weapon sources and hashes are in
`assets/freedoom/manifest.json`. See `THIRD_PARTY.md` and website credits.

## Space and candidate identity

| Board | App bytes | Free within 581,564-byte app limit | Static RAM |
|---|---:|---:|---:|
| FM-1 | 576,660 | 4,904 | 438,632 |
| SMK-37 Pro | 576,968 | 4,596 | 438,696 |
| SMK-37 Elite | 576,968 | 4,596 | 438,696 |

Native builds keep CPU1 audio with serial fallback and an 8,192-byte private
CPU1 stack, the 256 KiB Doom zone and 24 KiB bounded libc heap. The title/HUD
renderers use scanline buffers, not an additional framebuffer. Texture pruning
retains switch partners and animation cycles; identical patch columns share
storage. Weapon patches are stored at half resolution and projected at their
original size. Each package is explicitly revision 15 (`test15` / USB `_015`).

Local artifacts: `build/native/<board>/manifest.json` and matching app binary;
offline-validated packages: `build/test15-packages/`. These ignored outputs
have not been flashed or published. Device validation remains pending for all
three revision-15 candidates; earlier Release-14 hardware acceptance does not
validate this change. Do not copy these candidates over published Release 14.

Local validation passed: all three native builds and package round trips;
ordered single-write LCD regression; normal/low-detail/hard campaign loops,
death/retry and all nine level loads; real WASM title/options/controls/start
navigation, weapon switching, movement, firing/audio and 2,000-tick soak;
Worker quick taps and pause/resume; input ownership; 44.1/48 kHz audio queues;
website artifact allowlist and published Release-14 hashes. Chrome visually
checked the FM-1/Pro/Elite panels and title screen with no console errors.
Review captures are in ignored `build/faithful-preview/`.

## Build and validation

1. In WSL, run `python3 tools/build_campaign.py` with zdbsp installed.
2. Run `tools/build_browser_campaign.py` and `tools/build_native_art.py` using
   Python with Pillow. Both verify the pinned asset checksums.
3. Build the host with `tools/build_host.py --board fm1 --display strip
   --no-wipe --mapped-wad --small-room --static-wad --bounded-heap --abi32
   --campaign --native-art`. Run `tools/check_campaign.py <host> --wad
   build/fixtures/native-art.wad` for normal, low-detail, hard, death/retry and
   all-nine-map checks. The bot uses ordinary inputs, including timed door use.
4. Build each board with `tools/build_native.py --board <board> --campaign
   --toolchain /mnt/e/AI_Apps/Felucca/Felucca-review/.build-deps/jieli/toolchain`.
5. Run `tests/native_update_package_test.mjs` with the same pinned local FM-1,
   Pro and Elite bases as Release 14. It checks package round trips, loader
   identities and protected bytes without device access.
6. Build browser code with `tools/build_browser.py --emcc
   /mnt/e/AI_Apps/Doom-FM1-SMK/.cache/emsdk/upstream/emscripten/emcc` in WSL.
   Run the four `tests/browser_*_test.mjs` checks and `tools/check_site.py`.
   Website checks retain published release hashes and validate the WASM manifest.

Preview: serve `site/` and open `simulator.html`. The current local server is
`http://127.0.0.1:18815/simulator.html`. Click Play + sound, then Enter to select
Start Game and Enter again to accept a difficulty. The website's installer
still installs public Release 14; it is not a revision-15 hardware test page.

Browser behavior and host playthroughs cannot establish physical frame rate,
audio-worker timing, stack headroom or USB update acceptance. Check those on
hardware before a firmware release. Never publish device backups or recovery
reads from the original checkout's ignored `build/try-*` directories.
