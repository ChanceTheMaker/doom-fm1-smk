# Release 15 — classic menus, artwork and browser simulator

Prepared 2026-10-12 (America/Los_Angeles). This release adds the classic DOOM
logo/title menu, Start Game/difficulty, Options and Controls; detailed Freedoom
pistol/fist/shotgun art and white-key-12 weapon cycling; a classic status HUD;
and a redesigned opening level with a door, loop, secret room, stepped floors
and varied lighting. Nine original levels contain 77 enemies. The other eight
layouts remain intact, with updated floor/ceiling tiles across the campaign.
CPU1 still mixes music/effects with serial fallback. No extra framebuffer.

The FM-1/Pro/Elite browser simulator shares the same engine and LCD assets.
Its device panels preserve prior FM-1 work and adapt the Sloop SMK layout.
The main-page thumbnails now show this release. Logo provenance and asset
licenses are retained separately; no commercial WAD or private backup is included.

## Hardware evidence

The owner connected only the FM-1 directly by normal USB and confirmed it was
ready. A read-only handshake returned `Doom-FM-1_014`. The tested browser
installer built the SHA-256-checked FM-1 package, entered `ota-Doom-FM-1_014`,
completed the transfer and confirmed `Doom-FM-1_015` after restart. No recovery
dongle, stale full-device image, or protected-range write was used.

The owner answered **“Everything works”** after being asked to check the logo
and menus, start a game, open the first door with white key 6, cycle weapons
with white key 12, and assess the HUD, controls, gameplay, music and effects.

Two diagnostic samples showed two active cores, audio core ID 1, and 81,256
then 81,433 worker jobs, with zero missed deadlines, faults or rejected requests.
Maximum observed audio job time was 412.67 microseconds. This is not a frame-rate
benchmark or evidence of a manual all-nine-level playthrough.

**Pro and Elite Release 15 hardware validation remains pending.** Earlier Pro
Release 14 acceptance does not establish this release's physical behavior.

## Immutable application artifacts

| Target | Bytes | SHA-256 |
| --- | ---: | --- |
| fm1 | 576660 | `0e4ff0544b233ff4cb9a376eb66bb3e4dd70638516651e02d460c412d1b0d23d` |
| smk37-pro | 576968 | `a1194c7abd4cbf99a79f5719774ff45fc1b386d7ba259b760d18b307289929b7` |
| smk37-elite | 576968 | `984b87ea3c132eb4f668d002767ba867ee836d8cc473b1388d64dd5cc9b42f4b` |

FM-1 has 4,904 bytes free in the common application limit; Pro/Elite have 4,596.
Static RAM is 438,632 bytes on FM-1 and 438,696 on SMK, with CPU1's private
8 KiB stack. USB identities end in `_015`; public app filenames end in `-15.bin`.
Release 14 files remain unchanged and are catalogued in `archive-release14.json`.

## Validation and publication

All three native builds and actual package round-trip/protected-byte checks
passed. The host completed repeated nine-level campaigns at normal/low detail
and hard difficulty, plus death/retry and per-map checks. Tests cover one ordered
LCD write per row, exact USB boot identity, loader failures, Worker input/pause,
real WASM menu/gameplay/weapon/audio behavior and 44.1/48 kHz audio queues.
The Pages workflow validates firmware hashes, the browser build manifest,
restore behavior, runtime/worker regressions and the deploy artifact allowlist.

Only `site/` is deployed. The official FM-1 restore package remains pinned;
private recovery evidence and local complete packages remain ignored under
`build/`. The original dirty development checkout and release worktree were
preserved. Implementation and memory notes: [FAITHFUL_PREVIEW.md](FAITHFUL_PREVIEW.md).
