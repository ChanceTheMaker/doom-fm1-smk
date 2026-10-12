# Test07 experimental release: USB updates and native artwork

Test07 is built locally for FM-1, SMK-37 Pro and SMK-37 Elite. It is staged as an experimental USB-updater release after withdrawal of Test06. Hardware validation is still pending. No device was flashed during this work.

## USB path

The game exposes a MIDI-only USB interface named `Doom`. Its identities are
`Doom-FM-1_007` and `Doom-SMK-37_007`. An identity query does not write flash.
The existing upgrade command stops audio, disables interrupts, detaches USB,
copies a model-specific loader into RAM at `0x01c0a800`, and enters it.
The loader reconnects as `Doom Update`, with the same identity prefixed `ota-`.
The browser waits for that exact model before sending a package.

USB polling uses TIMER5 at 2 kHz, below the sound IRQ. USB SIE access has one
owner; main-loop retry stops that timer before reinitializing the controller.
Unknown SysEx and unused MIDI events cannot block the input queue. Game code
does not erase or program flash. Only the RAM loader performs updates.

The port reuses the proven transport and loader cores from Sloop SMK; source
revision and hashes are recorded in `src/native/update/PROVENANCE.json`.
Changes include Doom identities/descriptors, a direct RAM handoff, explicit
zeroing of the loader's `.pool` storage, and a tighter FM-1 write policy.

| Target | Loader write range | Protection |
| --- | --- | --- |
| FM-1 | `0x4000..0x93000` exclusive | Package CRC, device cipher key, full preflight, per-sector verification; boot and entire tail unchanged |
| SMK Pro / Elite | `0x4000..0x9d000` exclusive | Model/layout fingerprint, valid preserved key calibration, package and sector CRCs, full readback; boot and tail unchanged |

No flash loader record is staged. If power fails during programming, hardware
recovery may be required. A failed loader session remains in RAM for an explicit
retry; it does not automatically reboot a partly programmed application.

Test06 and earlier contain no USB driver. They can be installed **from synth
firmware over normal USB**, but cannot themselves receive another USB update.
An already-running Test06 needs one adapter installation of Test07. Test07 is
designed to make subsequent Doom updates possible with the normal cable.

## Native graphics

The hardware now includes the credited Freedoom monster splash, walking,
attacking and dying guards/imps, and a compact status bar with a health-dependent
face, ammo, health and armor. Native enemies are front-facing billboards;
the browser retains eight directional views and its full classic HUD.
Removing unreferenced texture patches leaves the existing texture definitions
and three maps intact while fitting within the application flash slot.

The splash is drawn after WAD initialization, so it can read real enemy assets.
No dynamic sprite copies or extra framebuffer are allocated. All art remains XIP.

## Evidence

- All three native images link within the existing flash and RAM bounds.
- RAM loaders' executable/data sections and required symbols lie wholly in RAM.
- Actual FM-1/Pro016/Elite016 packages round-trip with protected bytes unchanged.
- FM-1 loader simulation passes damaged packages, changed data between passes,
  foreign cipher key rejection, no-op reinstall, readback and protected-tail checks.
- SMK loader simulation passes foreign/corrupt headers, preflight, changed host
  data, write failure/retry, calibration protection and readback checks.
- USB descriptor and MIDI parser tests pass, including upgrade-command parsing.
- Browser transport tests pass direct Doom handoff/resume and reject cross-model
  loader replies without starting programming.
- The native 32-bit, 256 KiB zone / 24 KiB heap harness passes normal, low-detail,
  hard, death/retry and all three level scenarios with the new artwork.
- Native splash and gameplay previews are in `build/test07-preview/`.

## Build and verify

Run the existing campaign and browser-art generators first, then:

```sh
python3 tools/build_native_art.py
python3 tools/build_native.py --board fm1 --campaign --toolchain "$JIELI_TOOLCHAIN"
python3 tools/build_native.py --board smk37-pro --campaign --toolchain "$JIELI_TOOLCHAIN"
python3 tools/build_native.py --board smk37-elite --campaign --toolchain "$JIELI_TOOLCHAIN"
node tests/site_installer_test.mjs
node tests/midi_discovery_test.mjs
node tests/native_update_package_test.mjs /private/fm1-salt14.fwsc /private/Pro016.fwsc /private/Elite016.fwsc
```

Packages are written only to ignored `build/test07-packages/`. This test does
not stage a release, start an installer, or access MIDI hardware.

## Hardware acceptance still required

1. Install the matching Test07 application through the existing recovery path,
   preserving and verifying all bytes outside that model's application range.
2. Boot the game normally; check sound, new splash/HUD, movement and full turns.
3. Connect normal USB and confirm the expected Doom identity. Test reconnect
   after unplugging, and connecting USB after the game has already started.
4. Perform a same-version update over normal USB and verify readback and restart.
5. Verify installer resume with the RAM loader already active, then normal boot.

Offline tests do not replace the hardware acceptance checks above.
