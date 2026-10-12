# Nine levels, dual-core audio and blank-calibration compatibility

Release 14, built and hardware-checked 2026-10-12. This retains
candidate 13's nine-map campaign and dual-core audio design; see TEST13.md for
campaign and worker validation. It supersedes Release 10 with distinct app-only
filenames, hashes and runtime identities ending in `_014`. Earlier published
artifacts remain immutable.

## Why revision 13 could not be installed on the connected Pro

The running Release 10 USB loader accepted its identity but stopped after the
two package-header requests. The owner power-cycled and confirmed Doom still
booted. Two subsequent independent fresh 1 MiB dongle reads matched. Decoding
the application proved it was exactly the published Pro Release 10; the boot
profile CRC matched the official Pro/Elite profile. The full 4 KiB USRTRIM sector
was erased (all 0xff). The loader rejected its assumption that every device
contains a populated 37-key calibration record. The origin of this blank sector
is not established. No calibration restoration or invented defaults are applied.

The revised public loader accepts either a valid calibration record or a wholly
erased 4 KiB sector. An invalid partially erased/nonblank record still fails
before programming. It snapshots the existing sector and checks its complete
CRC after the update, in addition to the original boot and record checks. The
write bounds remain 0x4000..0x9d000. Private format-1 header compatibility is
retained. No writable range is expanded.

## Local checks and artifacts

- Public updater tests pass with address/undefined-behavior sanitizers; private
  format tests also pass. Added cases cover wholly blank sectors, partial erase,
  zeroed sectors and a changed byte beyond the original 556-byte record.
- The actual fresh Pro backup and candidate package passed the host loader
  simulation: 139 changed application sectors and all protected bytes preserved.
- All three native builds and package round-trip/protected-byte checks passed.

| Model | Application bytes | SHA-256 |
| --- | ---: | --- |
| FM-1 | 566864 | `5e51cbbe5fe677ca23e6f81291d007d4a093c0e4be8ae292c71fca2c9ad3add0` |
| SMK-37 Pro | 567120 | `758a463cf8ce820607855a398eda5b58951b6f1b47d2e6ee8a8bd678e7c6b664` |
| SMK-37 Elite | 567124 | `1c6f6d18b7f8bcf0aef1f76f26d804c5ba3255e21ca0858568a79a36b0bff5ec` |

The Pro recovery plan derives exclusively from the two fresh matching reads,
changes only app.bin and its directory/block CRC fields, and preserves every
byte below 0x4000 and at/above 0x9d000. Private backups, plan and journal belong
under ignored build/try-smk-pro. No old full-device image is a write input.

The owner explicitly approved revision 14 via the recovery dongle. All 139
changed application sectors verified, followed by a complete matching 1 MiB
readback. The bootloader and every byte outside the application range remained
identical to the fresh reads, including the blank calibration sector. No
automatic reboot was sent. The owner was asked to disconnect the dongle, boot
normally and reconnect direct USB.

The owner reported that Doom boots and "Plays good". Direct USB returned
`Doom-SMK-37_014`. Two samples showed two active cores, audio core ID 1, and
53,586 then 53,762 completed worker jobs, with zero missed deadlines, faults or
rejected requests. The maximum observed block time was 408.67 microseconds.

A same-version normal-USB reinstall then passed both package passes and complete
application readback, returning as `Doom-SMK-37_014`. After restart, the worker
again ran on core 1 (5,033 then 5,209 jobs), with zero errors. This exercises the
dual-core-to-loader handoff and the corrected blank-sector preflight on hardware;
the identical application does not require rewriting unchanged sectors.

## FM-1 check

The owner connected an FM-1 running official `FM-1_015`. The normal-USB installer
prepared `ota-FM-1_900`, transferred the model-checked package and confirmed
`Doom-FM-1_014` after restart. Runtime samples showed two active cores, audio
core ID 1, and 8,259 then 8,435 completed jobs with zero missed deadlines, faults
or rejected requests. The maximum observed block time was 359.38 microseconds.
The owner confirmed "Everything works" when asked about smooth gameplay, music,
sound effects, responsive controls and a steady HUD. A later runtime sample
reached 54,904 worker jobs with two cores still active and zero errors; its
maximum observed audio-block time was 422.46 microseconds. Elite hardware testing
remains pending. These observations do not claim a manual nine-map playthrough
or measured frame-rate parity with earlier single-core releases.
