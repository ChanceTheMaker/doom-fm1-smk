# Port work queue

- [x] Create standalone local Git repository, with no publishing remote.
- [x] Pin DoomGeneric and retain upstream license/provenance.
- [x] Define FM-1, SMK-37 Pro and SMK-37 Elite target profiles.
- [x] Add Linux/WSL host compilation and bounded frame-output harness.
- [x] Run a small IWAD and capture first rendered level on host.
- [x] Replace duplicate RGBA output with a tested RGB565 row converter.
- [x] Model immutable flash assets with a read-only mapped host WAD adapter.
- [x] Build a reproducible MAP01 fixture with reduced texture definitions.
- [x] Verify movement, turning, firing and release with a 280 KiB zone.
- [x] Record host zone peaks, static sections and individual compiler stack frames.
- [ ] Measure engine heap, static data, stack and framebuffer peak use.
  Remaining: other heap allocations, full call-chain stack high-water and native target measurements.
- [x] Implement bounded reductions to the existing renderer; pass the same host play test.
- [x] Design asset packing within a validated application-only flash budget.
- [x] Import versioned FM-1 and SMK HAL subsets with provenance.
- [x] Implement separate board startup, clocks, input and LCD adapters.
- [x] Implement fixed-size allocator and file-free asset access on device.
- [x] Cross-compile each native target and inspect linker/binary bounds.
- [ ] Bring up color bars and input feedback, then one Doom level on each device.
- [ ] Add sound effects, then assess music and optional saves.
- [x] Stage a private Pro application-only package from two matching, verified stock reads.
- [x] Add an offline restore planner that preserves current data outside the application.
- [ ] Physically validate Doom boot and the adapter restore procedure.
- [x] Stage a separate FM-1 package and run the FM-1 loader host test.
- [ ] Validate FM-1 installation/boot on hardware, then package Elite separately.

Release 15 passed its FM-1 hardware check and is prepared for publication. Earlier Release 14 was physically accepted on FM-1 and Pro. See docs/RELEASE15.md for current evidence.

- [x] Reproduce and fix the Test01 lump-directory OOM; store fixed metadata in XIP.
- [x] Add a 32-bit host gameplay check with the native 24 KiB allocator and revised 256 KiB zone.
- [x] Recover FM-1 through the adapter and physically test Test02 (boots/plays, then turning OOM).
- [x] Reproduce the 16,408-byte turning allocation failure and eliminate room composite allocations.
- [x] Compare all room composite columns and five 10,500-frame play scenarios against the reference engine.
- [x] Install Test03 on FM-1; user reports it runs after turning-crash fix.
- [x] Diagnose tiny menu artwork; add full-resolution text menus and tested Select-key confirmations.
- [x] Install Test04 with verified full-flash readback; user confirms readable menus.
- [x] Build Test05 with three levels, enemies, shotgun, pickups and score/HUD.
- [x] Verify campaign progression, replay, combat and death/retry with native memory limits on host.
- [x] Install Test05 on FM-1; verify each changed sector and the complete 1 MiB flash image.
- [ ] Check Test05 combat, pickups, exits and frame rate on the physical FM-1.
- [ ] Refresh the private SMK candidate after the FM-1 check.

## Test06

- [x] Add synthesized sound effects and directional shaded enemy sprites.
- [x] Add and capture a new splash screen and campaign screenshots.
- [x] Build separate FM-1, SMK Pro and Elite applications.
- [x] Install Test06 with full readback; owner confirms graphics and sound on FM-1.
- [x] Validate three public browser builders and model-specific installer routing.
- [x] Prepare public repository, website and Pages workflow.
- [ ] Physically test Doom on Pro and Elite, including audio and recovery.
- [ ] Add runtime USB updater, then assess music and persistent saves.

## Test08 and follow-up

- [x] Eliminate duplicate bottom-HUD LCD transfers without another framebuffer.
- [x] Pass real dispatcher regression and package/loader/identity checks.
- [x] Verify FM-1 Test08 via normal USB and owner gameplay/audio/HUD test.
- [ ] Verify Pro and Elite Test08 on hardware.
- [x] Add original music, reduce synthesis load and verify Release 10 on FM-1 and Pro.
- [ ] Physically validate Release 10 on Elite.
- [x] Expand the campaign to nine levels and enable dual-core audio (Release 14).
- [x] Integrate the preserved FM-1 simulator and add Pro/Elite device views (Release 15).

## Release 15

- [x] Classic logo/title menus, weapon cycling, detailed weapons/HUD and revised opening level.
- [x] Browser/host/native/package regression checks and refreshed thumbnails.
- [x] Physically validate Release 15 on FM-1 through normal USB.
- [x] Prepare the exact verified artifacts and website for Release 15 publication.
- [ ] Physically validate Release 15 on Pro and Elite.

## Windows SMK Pro USB isolation (2026-10-16)

Ports Sloop 0a51b35's native Windows helper and disposable MIDI sessions.
Installation and original-firmware restore require the matching helper on Windows
Pro; errors never fall back to browser MIDI. Package construction uses this
project's own verified builders and pins the existing app. Expected boot identity:
Doom-SMK-37_016. No firmware, protected storage or protocol changes. Elite retains
its existing browser path. No upstream contribution was submitted.

Validation includes mocked native stages, cross-process exclusion, HTTP boundary
checks, package verification and browser install/restore routing. Hardware checks
passed on the connected SMK-37 Pro: original Pro 016 to Doom runtime
Doom-SMK-37_016, then original Pro 016. Both restart identities were verified.
The real installer page made zero Web MIDI requests and stayed responsive
(270 ticks at 100 ms during installation). Baseline: 25c1965; Test16 firmware
unchanged. Automatic FM-1 V15 preparation remains available and was checked
in the browser regression.
