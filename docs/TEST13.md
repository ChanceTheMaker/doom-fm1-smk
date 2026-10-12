# Nine-level dual-core candidate

Candidate 13 was built on 2026-10-12. It is not publicly released. Release 10
remains the public firmware. Candidates 11 (six levels) and 12 (nine levels,
single core) were local build stages and were not flashed or published.

## Content and processor ownership

Nine original maps contain 76 enemies. Maps 1–3 are unchanged; the added maps
are Cooling Works, Switchback, The Foundry, Freight Line, Blackout and Last
Transmission. Music is the original Circuit Breaker loop, with existing sound
effects and independent music volume. No commercial Doom music is included.

CPU0 runs gameplay, display, controls, USB and peripheral interrupts. CPU1
renders each 128-frame music/effects block into a private 1 KiB scratch buffer.
CPU0 copies completed blocks into audio DMA and queues the next job. It never
waits for CPU1 inside the audio interrupt. A failed start, worker fault or missed
deadline holds CPU1 and returns to serial audio. CPU1 has private 8 KiB stacks;
its polling loop runs from SRAM. Flash/update and recovery paths hold CPU1
before SRAM or XIP is reused. This does not parallelize the Doom renderer.

## Local validation

- All three native targets compiled and passed application, SRAM and private
  stack bounds. The Pro application occupies 567,052 of 581,564 available bytes
  (14,512 bytes free). Main static data/BSS is 438,696 bytes; the CPU1 stacks
  occupy a separate previously unused RAM region.
- Mailbox and actual audio dispatcher tests passed with address/undefined
  behavior sanitizers: corrupt/rejected jobs, worker faults, late partial
  blocks, serial recovery and wraparound timeouts.
- Music recovery, sound effects, native HUD row dispatch and diagnostic reply
  validation tests passed.
- Package round trips and protected-byte checks passed for FM-1, Pro and Elite.
  The local browser installer requires the exact model and runtime version 013.
- Native-art host gameplay passed 24,000-frame normal, low-detail and hard runs:
  all nine maps, 32 exits and repeated campaign restart per run, including three
  deaths/retries. Individual spawns and explicit death/retry checks also passed.
  Peak observed Doom-zone use was 221,840 / 262,144 bytes. Host checks do not
  establish physical frame rate or hardware acceptance.

| Model | Application bytes | SHA-256 |
| --- | ---: | --- |
| FM-1 | 566864 | `904ea82e6a1300a46471263de3408896d76d45aa4b8bab461a488782d0cb9839` |
| SMK-37 Pro | 567052 | `a66ebb3f07cc5857d7bab4b32c491fce69cc46594e19e569fb07c6155a323a41` |
| SMK-37 Elite | 567056 | `1e8965c372ba4b6081f87faf4c9cfcf1b2fc13fc717ed58de29087437cba4f39` |

## Hardware evidence

The user confirmed the SMK-37 Pro is connected directly by USB and ready for
candidate 13. The installer identified `Doom-SMK-37_010`, entered its existing
USB updater and identified `ota-Doom-SMK-37_010`. The first attempt stopped;
one explicit retry with detailed logging served only the two 512-byte header
requests (offsets 0 and 0x200), then the loader stopped requesting data.
The current loader validates its header and protected boot/calibration guards
before fetching application sectors, and validates the complete application
before any erase. Therefore neither attempt reached programming. The owner
power-cycled and confirmed Doom still boots. The precise failed preflight guard
is under investigation; no guard has been disabled or bypassed.

Candidate 13 boot, dual-core runtime counters and physical acceptance remain pending.
FM-1 and Elite have not been physically tested with this candidate.

The read-only `tools/read_runtime_status.py` query reports active core count,
audio core ID, completed jobs, missed deadlines, faults and maximum job time.
It never enters the updater or writes flash. Growing jobs on core 1 and no
fallback are required before claiming dual-core operation on hardware.

Local packages, host screenshots, diagnostic records and installer preview stay
under ignored `build/` directories. Private recovery backups are never release
inputs. Original simulator changes remain preserved in the development checkout.
