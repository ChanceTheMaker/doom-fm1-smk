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

No current task requires publishing or flashing a device automatically.
