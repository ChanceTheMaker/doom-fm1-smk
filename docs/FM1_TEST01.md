# FM-1 Test01

This is a private first hardware test, not a tested firmware release. It contains the real Doom engine and an open-content Miniwad room, without sound or USB updating.

Open the local FM-1 installer at `http://127.0.0.1:8785/`. Connect the FM-1 directly by normal USB while running firmware with the standard FM-1 MIDI updater. Close other MIDI applications. Have the FM-1 XIAO recovery adapter ready, but leave it disconnected during normal USB installation. The installer rejects SMK identities and never starts automatically.

The package is derived from the pinned Felucca Salt14 FM-1 release (package SHA-256 `efb516a7131d12eb5c008ff9af5a380d07e82eb1040bd03990f28d1233417e28`). It retains its loader byte-for-byte (`2c9f43bf7dff81a953c07f3c82cedf5f5899aac14e5b62c2cb23ba7f560ce7db`). Only application bytes, their CRC fields, and the enclosing package metadata change. Package identity is `FM-1_990`; that identity is for installation only because Doom has no MIDI stack.

The inherited loader writes application sectors `0x4000..0x93000`, validates the chip key, and verifies sectors. It preserves the bootloader. The running synth stages the loader and the loader clears its update records outside that range, so this is not a promise that no update-metadata flash is touched. Back up synth projects using that synth before installing.

## First check

Expected: `DOOM TEST 01`, then the room. Count white touch keys from the left: turn left, forward, turn right, back, fire, use, menu, enter, run, strafe left, strafe right. Test movement and release. No sound is expected. Photograph any `DOOM STOPPED` message; report a black screen rather than repeatedly reinstalling.

## Return to synth firmware

USB MIDI disappearing is expected after installation. Hold both OCT buttons for two seconds to request ROM recovery if the scanner works. Otherwise use the XIAO FM-1 power-off/USB-key recovery procedure that previously restored this device. This build's software shortcut is not hardware-validated yet.

`build/try-fm1/felucca-salt14-restore.fwsc` retains the known source release. `felucca-restore-application-region.bin` is **only** its application region, intended for the FM-1 bounded adapter writer at offset `0x4000`, length `0x8f000`. It is not a full flash image. Obtain two matching fresh reads first, preserve the current prefix and tail, precheck each sector, and verify all written bytes. The SMK restore planner/writer bounds do not apply. No device writes are performed by the staging script.

The previous successful FM-1 adapter recovery and verified readback are recorded locally in `Felucca/recovery-backups/bad-fm1-20261010T210809Z/restore-result.json`. That is evidence for the adapter procedure, not evidence that this Doom build works. Use fresh device reads for any new restore, especially if testing the other FM-1.

## Rebuild package

```powershell
python tools/stage_fm1_test.py --base ../Felucca/Felucca-site-publish/firmware/felucca-0.9-salt14.fwsc
python -m http.server 8785 --bind 127.0.0.1 --directory build/try-fm1/site
```

Native app details and limitations are in `docs/NATIVE_TEST01.md`. Both native runtime tests and package checks run without hardware. Hardware boot, LCD, controls, runtime memory headroom and restore remain to be tested.
