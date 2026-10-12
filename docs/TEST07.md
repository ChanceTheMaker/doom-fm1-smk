# Test07 experimental release: USB updates and native artwork

Test07 is published for FM-1, SMK-37 Pro and SMK-37 Elite as an experimental USB-updater release after withdrawal of Test06. The owner's SMK-37 Pro has booted and completed a reported normal-USB reinstall. FM-1 and Elite Test07 hardware validation remains pending.

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

### SMK-37 Pro initial test, 2026-10-12

The published Pro application (`b9d37c032d6b81d230f6e262f74ac7a2177d92213b93c2d11896a1cf095fcf7d`)
was installed through the SMK recovery adapter after two matching fresh 1 MiB
backups and comparison against this device's stock boot header and calibration.
All 142 changed application sectors and the complete final image verified.
Bootloader and all bytes outside `0x4000..0x9d000` remained unchanged.
The owner reports that the game works after restarting. On direct USB, Windows
exposed MIDI ports named `Doom`. A read-only identity query returned
`Doom-SMK-37_007` with a valid reply checksum. Windows PnP initially retained
the older `Felucca` display name; the MIDI API and firmware reply identify Doom.
Earlier checks found no instrument ports before it appeared, so those checks
alone do not establish a firmware enumeration defect. The owner subsequently
reported that the normal-USB reinstall worked. Reconnect scenarios remain to be
tested; none of this establishes FM-1 or Elite operation.

### Local HUD correction after the Pro test

The owner reported a flashing bottom player HUD. The native frame dispatcher
sent the legacy campaign status rows 210..239 to the LCD and then overwrote
them with the face HUD every frame. The correction suppresses those legacy
bottom-row transfers, leaving exactly one ordered LCD write per row. Menus and
campaign overlays retain the full screen. No extra framebuffer is allocated.

The build remains single-core (`MELODEE_DUAL_CORE=0`, `MELODEE_CACHE_RAM=0`).
The host regression test `tests/native_frame_test.c` exercises the real native
frame dispatcher, checking gameplay, menus, overlays and LCD failure handling.
The correction was tested locally as **Test07 HUD1**, retaining runtime identity
`Doom-FM-1_007` while using a distinct candidate filename and application SHA-256
`9e233e18f7920b9902475727290b92a746e6372595f90ef6ac495ae69813f42b`.
The published Test07 images have not been replaced with these same-version bytes.

### FM-1 HUD1 acceptance, 2026-10-12

The owner switched testing from Pro to FM-1. Two new complete flash reads matched
each other and the previously verified Test06 installation. The candidate was
built from those fresh bytes; 137 changed application sectors were written
within `0x4000..0x93000`, with per-sector and full 1 MiB readback verification.
The bootloader and all device data outside the application range were unchanged.
Backups and journals remain private under ignored `build/try-fm1/`.

After disconnecting the adapter and restarting, the owner reported: "doom boots
and no more flickering on the UI sound and gameplay work". Direct normal USB then
returned `Doom-FM-1_007` with a verified identity checksum. This establishes the
HUD correction on FM-1, not Pro or Elite, and is separate from a USB reinstall.

The exact tested application/package is retained locally under
`build/local-test07-hud1-fm1/`. The next public revision is **Test08**, with new
`test08` filenames and `_008` runtime/loader identities. Its validation and release
state are tracked in [TEST08.md](TEST08.md).

1. For a device still running Test06 or earlier, install the matching application through the recovery path,
   preserving and verifying all bytes outside that model's application range.
2. Boot the game normally; check sound, new splash/HUD, movement and full turns.
3. Connect normal USB and confirm the expected Doom identity. Test reconnect
   after unplugging, and connecting USB after the game has already started.
4. Perform a same-version update over normal USB and verify readback and restart.
5. Verify installer resume with the RAM loader already active, then normal boot.

Offline tests do not replace the hardware acceptance checks above.
