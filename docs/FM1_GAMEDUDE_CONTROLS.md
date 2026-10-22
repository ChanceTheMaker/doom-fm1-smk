# FM-1 GameDude-style controls - release 26

This FM-1-only release follows GameDude's direction cluster, middle
Select/Start positions and far-right B/A pair. Doom's matching actions are
Menu/Select and Use/Fire. The existing SMK release 24 controls are unchanged.
Count white and black piano keys separately from the left.

| Keys | Doom action | Illustration color |
| --- | --- | --- |
| White 1 / 2 | Turn left | Cyan |
| Black 2 / 3 | Forward | Cyan |
| White 3 | Back | Cyan |
| White 4 / 5 | Turn right | Cyan |
| White 6 | Run | Amber |
| White 7 / 8 | Menu / Select | White |
| White 9 / 10 | Strafe left / right | Amber |
| White 11 | Next weapon | Purple |
| White 15 / 16 (last two) | Use / Fire | Green / red |

PLAY and REC also provide Menu and Select, matching GameDude's panel order.
K1 volume, K2 menu navigation, master volume and the recovery chord remain.
Assigned piano LEDs are on when idle and go dark while their action is held.
Duplicate direction keys stay dark until both are released. Unassigned keys
stay dark. FM-1 hardware LEDs are on/off; the illustration's colors identify
actions and do not imply RGB LEDs in the FM-1.

Firmware, simulator and existing hero illustration use this layout. All
shell variants, camera animation and screen artwork are retained. The live installer uses the owner-tested FM-1 release 26.

Validation: native mapping/chord/duplicate-key/light tests pass with address
and undefined-behavior sanitizers. Firmware and simulator maps agree for all
27 chromatic notes. The actual browser simulator starts its engine and passes
Fire press/release checks. Build 25 is 578,256 bytes, SHA-256
`e485fe9d33cb1803668da01395c4895cefea45f2771638b8599a1035007ae65c`.
The pinned-base package validates checksums, reopens successfully and preserves
all protected bytes. Package SHA-256:
`243648556975527d9e0fd2d1480445ddaf9a5dda3a048ddcfa209d5935b3a164`.
Hardware installation and owner acceptance are recorded below.

Hardware: installed on the owner FM-1; restart verified as
`Doom-FM-1_025`. The source was Felucca `FM-1_969`; its RAM loader reports
`ota-FM-1_900`. Initial exact-version handoff prediction stopped before
programming; read-only discovery identified that loader, then programming
and restart completed. The owner confirmed the controls, key lights and sound, then reported that
FM-1 performance feels slower than SMK. That report led to the incremental scan improvement in build 26.

Post-restart audio telemetry: both cores active, audio blocks increased
7,568 to 7,920 across three samples, with zero missed deadlines, worker
faults or rejected jobs. Maximum observed worker time: 258 microseconds.
The stop-message query is not supported by this FM-1 build and did not reply;
that query is not counted as a passed check.

## Release 26: FM-1 scan performance

Replaces the blocking full-matrix scan in the gameplay loop with the same
incremental scan HAL used by GameDude. The shared timer runs input at 10 kHz
and preserves USB polling at 2 kHz; SMK timer behavior is unchanged. Key LED
masks are rebuilt only when held actions change. Native FM-1 screen hints
now name the new physical key positions. Read-only performance counters
report frame rate, scan cost, light updates and LCD timeouts.

The real timer ISR passes host checks for both FM-1 and SMK schedules. Build
26 is 578,648 bytes; application SHA-256:
`853d7aa5c3200226c516e1edb9bbe9f521e90eec063bb8bee8c18978c206f780`.
Its checked package SHA-256:
`4eba164e953e2f598d35d4718bddca155e73de12eff138c5e9f705f248238600`.

Release 26 was installed and restarted as `Doom-FM-1_026`. A 60-second
read-only monitor recorded about 9,983 scan ticks/sec, 9.75% CPU spent in
the scan ISR and a 23.79-microsecond maximum scan cost. Both audio cores
stayed active with zero missed deadlines, worker faults or rejected jobs;
LCD timeouts were zero and stop messages empty. No held actions appeared
in this capture (light update count stayed 1), so its 9.60 displayed
frames/sec is an idle-screen observation, not a gameplay benchmark. The owner then reported "way better" when comparing responsiveness. No numerical gameplay speedup or speed-parity claim is made. A physical cold start and original-firmware round trip were not repeated for build 26; the existing restore installer remains available.

The GameDude helper mismatch reported during this work was a separate local
configuration issue: an older 939 helper was still running for the live 952
page. It was replaced with the current public helper and its application
hash was verified against the live manifest; no SMK flash was performed.
