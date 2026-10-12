# Port work queue

- [x] Create standalone local Git repository, with no publishing remote.
- [x] Pin DoomGeneric and retain upstream license/provenance.
- [x] Define FM-1, SMK-37 Pro and SMK-37 Elite target profiles.
- [x] Add Linux/WSL host compilation and bounded frame-output harness.
- [ ] Run a small IWAD and capture first rendered level on host.
- [ ] Measure engine heap, static data, stack and framebuffer peak use.
- [ ] Choose low-memory engine strategy after measurement; compare RP2040 Doom/GBADoom.
- [ ] Design asset packing within a validated application-only flash budget.
- [ ] Import versioned FM-1 and SMK HAL subsets with provenance.
- [ ] Implement separate board startup, clocks, input and LCD adapters.
- [ ] Implement fixed-size allocator and file-free asset access on device.
- [ ] Cross-compile each native target and inspect linker/binary bounds.
- [ ] Bring up color bars and input feedback, then one Doom level on each device.
- [ ] Add sound effects, then assess music and optional saves.
- [ ] Verify board-specific update/recovery route before creating install packages.

No current task requires publishing or flashing a device automatically.
