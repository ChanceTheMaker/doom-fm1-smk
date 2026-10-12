# Test08: bottom HUD correction

Status: Test08 experimental release; FM-1 hardware acceptance passed.

The native frame dispatcher now skips the legacy bottom status-bar LCD writes
when the face HUD owns rows 210–239. Gameplay writes each LCD row once, in order;
menus and campaign overlays keep their full-screen rendering. There is no extra
framebuffer or RAM allocation. The native build remains single-core with
`MELODEE_DUAL_CORE=0` and `MELODEE_CACHE_RAM=0`.

## Version strategy

Published Test07 artifacts remain immutable. The hardware-tested local correction
was named Test07 HUD1 and retained `_007`; its exact FM-1 binary and package were
preserved before rebuilding. Test08 uses `doom-<board>-test08.bin`, package product
`FM-1_997` / `SMK-37_997`, and runtime identities `Doom-FM-1_008` /
`Doom-SMK-37_008` (prefixed `ota-` in RAM updater mode). The installer must reject
an old `_007` identity as proof of successful Test08 boot.

## Evidence by model

| Model | Evidence |
| --- | --- |
| FM-1 | HUD1 recovery write/full readback verified. Normal-USB update from HUD1 to Test08 completed and returned `_008`. Owner confirms Test08 steady HUD, gameplay and audio. |
| SMK-37 Pro | Published Test07 boot and normal-USB reinstall confirmed by owner. HUD correction and Test08 hardware tests pending. |
| SMK-37 Elite | Offline tests only; hardware validation pending. |

The real native frame-dispatcher regression checks gameplay, menu and overlay
row ordering plus display-error propagation. The FM-1 recovery writer rejects
changed protected bytes, stale device state, incomplete/out-of-range plans and
write/readback failures without automatically retrying or booting.

## Release gates

Build all three application-only images and RAM loaders; verify package round
trips/protected bytes, both USB transports and exact Test08 boot identities.
The FM-1 normal-USB update completed on 2026-10-12: the existing `_007` RAM loader
transferred Test08 and the browser confirmed `Doom-FM-1_008` after restart. The
owner confirmed a steady HUD, working gameplay and normal audio. Pro/Elite
Test08 hardware acceptance remains pending. USB reconnect/soak and same-version
Test08 reinstall remain separate future checks.

| Application | Bytes | SHA-256 |
| --- | ---: | --- |
| FM-1 | 533496 | `b5fdb9373f9423367c3b497f9602d9c10406a2d14d36ea1893ec8304876864ef` |
| SMK-37 Pro | 533640 | `2ccaac71c1fe85203720d504d29b3f78dd08c0cd4911794bacf505d0c985f8e9` |
| SMK-37 Elite | 533640 | `e846581f54a8cc07495ac04f149bc9487e383573f28744258c067eb99dc96e02` |

The FM-1 application physically tested over USB had SHA-256
`7c1cf50411aa720f53e9fd9e18d18a1661daa10e61974b569bbce657f5859529`.
The final published build differs by exactly one byte: the splash label now
says TEST08 instead of TEST07. The same single-byte label correction was
verified for Pro and Elite; code and all other bytes are unchanged. Final
packages passed offline round-trip and protected-byte checks. The final
label correction has not been separately installed on hardware.

Only reviewed app-only binaries belong in `site/firmware/`. Vendor packages,
complete flash images, calibration and recovery journals stay in ignored local
build output. The main development checkout's browser simulator and artwork
remain separate uncommitted work to integrate after release reconciliation.
