# Test06 release evidence

2026-10-12: FM-1 owner confirmed “New graphics and sound both work” after adapter installation and normal restart. White key 5 fires the shotgun. SMK Pro and Elite builds have not received a physical Doom test.

## Firmware

- FM-1 app: 557,576 bytes; SHA-256 `31135feb6077b9f4d5b34260975ef109b8008680eb8eeff889bf60377b744027`.
- Pro app: 557,452 bytes; SHA-256 `5ed13020fd1f560ea3b7244bce8b6da0a47407d73fcc87112fe6998f56c26100`.
- Elite app: 557,452 bytes; SHA-256 `dac610b713fe857f7eab515f2582e88cb32296e7eb08ea85b39436f4202d5ea0`.
- Data+BSS: FM-1 437,032 bytes; SMK 437,080 bytes. Both remain below linker RAM limit `0x1c74000`, including the 256 KiB Doom zone; the separate C heap remains 24 KiB.
- Runtime flash writes and USB updater: disabled. Audio uses a bounded event queue and four fixed voices at 44.1 kHz, with no heap allocation in the sound path.
- Campaign WAD SHA-256: `00c26fa84d199c5800edb471edf5b079e8f752463fa34bcd6e94a1f13f617d8c`.

## Checks

- Host campaign, low-detail and hard-mode runs: 8,000 frames each, 17 level completions, 100 kills, peak score 2,600; no deaths in scripted play.
- Idle death/retry: 2,000 frames, two deaths/retries; all three level starts checked.
- Sound renderer sanitizer checks: effects finite/nonzero, stereo channels, output bounds, mute, reset and queue overflow.
- Actual FM-1 package and loader host checks: protected bytes, allowed sectors, foreign-key refusal and idempotence.
- FM-1 physical installation: two matching pre-write full reads, 140 changed application sectors, per-sector readback and complete 1 MiB readback verified. Boot and saved-data tail preserved. Private dumps remain local.
- Website package checks: all three real release apps packaged with their pinned bases; round-trip integrity, protected bytes and corrupted inputs checked. Mocked transport covers model/version filtering, handoff failures, explicit generic Elite confirmation and successful completion without a returning MIDI identity.
- SMK portable-loader integration: actual Pro and Elite candidate packages applied to synthetic flash under ASan/UBSan; 152 changed sectors per model, boot and saved-data tail preserved. Loader test source: Sloop SMK `090588d112a4a6230fe71d2f3263bdcca2203820`, `tests/smk37_update_test.c`.
- Chrome: automatic base download and package build tested for each model. Browser package preparation is not a physical USB installation test.

## Remaining

Physical SMK boot, controls, audio, gameplay and recovery checks; native stack high-water and extended gameplay soak; a runtime USB updater; music and persistent saves. Published SMK status must remain distinct from the confirmed FM-1 result.
