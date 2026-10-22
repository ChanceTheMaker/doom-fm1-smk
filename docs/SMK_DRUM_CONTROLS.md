# SMK Doom drum controls ? release 24

Release 24 publishes the tested pad controls for Pro and Elite. FM-1 stays on
release 16. The current universal restore and protected-region checks are retained.

## Physical layout

Count each row from the left; there are eight pads per row.

| Row | 1 | 2 | 3 | 4–6 | 7 | 8 |
| --- | --- | --- | --- | --- | --- | --- |
| Top | Strafe left | Forward | Strafe right | Unassigned | Unassigned | Unassigned |
| Bottom | Turn left | Back | Turn right | Unassigned | Use | Fire |

Strafe is amber, movement cyan, Use green, and Fire red. Unassigned pads stay
dark. Held controls turn off until released. Brightness starts at 150/255;
Fader 2 takes over after movement, with noise rejection and 50 Hz coalescing.
K1 volume and K2 menu navigation are retained. REC opens the menu and PLAY
selects, alongside the existing PATCH/PARA buttons and white-key controls.

## Warm firmware switch

The previous Doom code scanned only digital keys/buttons and never drove the
pad LEDs or read the analog pads. Addressable LEDs can retain the preceding
firmware's last frame across an application restart. That accounts for the
lingering GameDude lights, but the exact reported transient green pattern has
not yet been reproduced on hardware.

The new startup stops inherited SPI1/SPI2 DMA and ADC activity before clearing
RAM, holds pad data low, initializes analog pins and scanner state, and sends
all 16 pad colors (including zeros for unused pads). The shared LCD/LED SPI
driver preserves display configuration, provides reset/latch gaps, and stops
DMA on failure. Updater/recovery handoff stops the scanner and ADC and sends
an all-dark frame before leaving Doom.

SPI2 interrupts run the same divided scan cadence used by GameDude, independent
of renderer timing. ADC samples retain their old mux index before advancement.
Short pad taps remain queued until Doom consumes their key-down event, including
multiple simultaneous taps; keys and pads can be used together.

## Validation

### Build 24: release acceptance (2026-10-21)

The owner confirmed movement, strafing, Fire, Use, steady colors, smooth Fader 2
brightness and sound on SMK-37 Pro. A separate three-minute gameplay monitor
captured 6,347 pad samples, 161 total LED writes, and multiple held-pad combinations.
Both audio cores stayed active: zero missed deadlines, worker faults, rejected
requests or LED errors. All stop-message queries were empty. Brightness stayed
150 during this capture; physical Fader 2 travel is covered by owner confirmation.

The public Pro package matches the hardware-tested packet byte-for-byte.
Doom 24 ? original firmware completed through the normal USB helper; the final
identity was `SMK-37 Pro_016`. The instrument was left on original firmware.
A physical Chrome cable-disconnect test was not repeated in this release.

Pro and Elite apps are each 580,292 bytes. Pro SHA-256:
`136b0185818cfaa786a92fd961bedd254443d048e13800dd50829d29d315030f`.
Elite SHA-256:
`ef1cc34be742beee0d2dac49e3046a52c733c732fe50682690ec04198b8180fc`.
Exact-packet updater simulations preserve protected boot/tail regions for both.
Elite hardware is not tested. USB product labels are `Doom SMK-37` and
`Doom SMK-37 Update`; runtime updater identity is `Doom-SMK-37_024`.

Host checks include pad/scan/LED transport sanitizers, 211-state sprite coverage,
66 real renderer states including overkill, and 70,000 campaign frames across
normal and hard/low-detail runs (72 level completions). Site, installer, native
helper, browser engine/audio/input and boot verification checks pass.

The earlier reported sprite-frame stop did not recur in these runs. No specific
renderer fix is claimed; compact stop reporting remains available if it recurs.

The existing animated hero retains its camera movement, alternating devices,
all shell finishes and screens. Only the eight mapped SMK pads gain illumination.

### Build 23: reject measured Fader 2 noise

The build 22 monitor recorded raw Fader 2 values 215..224, with individual
215 readings followed immediately by 222. The old 8-count takeover and
2-level deadband allowed startup brightness to fall to 54 and then oscillate
52/54. No held pads were captured in that 55-second monitor; it is not the
owner's separate visual pad acceptance test. Both cores stayed active and
audio advanced with zero missed deadlines.

Build 23 retains build 22's LED stream and adds a four-sample smoothing filter
plus three consecutive filtered readings at least 16 counts from the initial
position before Fader 2 takes over. Host regression replays the observed noise
for 2,000 samples both before and after takeover without brightness changes;
deliberate movement still takes over and both endpoints reach 0/255.

The Pro app is 580,268 bytes, SHA-256
`93605e82d8c65bc2ee28e9ea1a91fa21c87aabaa0170b61e8bda9b48cc60c678`.
Packet SHA-256:
`ed0d95090b728a67abc2c35e795f67673d6c4e431309a704b04615d62df4a542`.
Native flash/RAM/loader bounds and the exact-packet simulated updater checks
pass. The simulated update preserves protected boot and tail regions.

Installed using the native helper; restart verified as `Doom-SMK-37_023`.
A fresh 55-second monitor captured 1,945 pad-status samples: brightness stayed
150, brightness-change count remained zero, and LED-write count remained one
with no pads held. Both cores stayed active, audio blocks advanced 3,164 to
21,758, and all error-text queries were empty. No missed audio deadlines,
worker faults, rejected jobs or LED errors occurred. This verifies idle-noise
rejection on hardware; deliberate Fader 2 travel is host-tested, not newly
confirmed by the owner on build 23. The earlier sprite stop remains unresolved;
its exact error can now be retrieved if it recurs. No public site was changed.

### Build 22: reset gaps inside the LED SPI packet

The owner clarified that pressing Fire/Use changes movement lights and that
pressing movement pads also changes Fire/Use lights intermittently. Build 21
reported constant brightness and no game panic during these observations.

The prior packet contained 36 zero bytes before its 384 color bytes and no
trailing zeros. Its explicit 350-us GPIO delays ran while SPI route B still
selected PC10; GPIO writes alone did not establish that the pin was under
GPIO control during those delays. Build 22 puts 512 zero bytes before and
after the colors **inside the DMA stream**. At the existing divisor 8 these
spans last 614 us at a 60-MHz LSB clock, or 384 us at 96 MHz. This avoids
depending on the disabled SPI pin's idle state for the reset/latch gap.
The LED baud, colors, pad input mapping, interrupt policy and Fader 2 algorithm
are unchanged. The owner explicitly confirmed the gameplay pad test:
"Yes—other pads stay steady" while alternating Fire, Use and movement pads.
This validates the visible correction on this SMK; no electrical waveform
capture was performed.

The ASan/UBSan pad and transport tests pass, checking every brightness and
held-pad position, both zero spans, complete GRB encoding, LCD restoration
and timeout cleanup. The Pro app is 580,204 bytes, SHA-256
`1b924409069df952e9b6f362a7cca5262a86e35d493b393de00b5f953bef3fda`.
Its packet SHA-256 is
`4bcfcf6602c5d746a08164b556784233743024ca6c54bbb05f5f92bed9f2a7ad`.
The exact packet passed the real updater core on simulated flash: 152 changed
sectors, protected boot/tail preserved. RAM ends at 0x01c73818, below the
0x01c74000 guard. The game assets and dual-core audio are retained.

Installed from running build 21 using the native helper; the exact
`Doom-SMK-37_022` restart was verified. Initial runtime checks showed empty
stop text, brightness 150, no LED errors, and two active cores. Audio blocks
advanced from 3,069 to 3,245 with zero missed deadlines, faults or rejected
requests. This is not a Chrome disconnect test or a public release.
After the owner's acceptance, another snapshot showed 103 LED writes, brightness
150, zero brightness changes and no game panic. Its counters differ from the
earlier monitor, so these are recorded as separate observations, not one
continuous test session.

### Build 21: exact sprite failure reporting; gameplay validation pending

Build 20 subsequently showed `DOOM STOPPED`; the owner transcribed the error
as "Invalid sprite frame 9 8 0". Audio counters were frozen and pad presses
were no longer consumed by the game. Consequently the steady-light observation
below does **not** establish stable lights during gameplay. Release 16's notes
also record an unresolved "9 8 0" report; its relationship to this failure is
not yet established.

Build 21 preserves the game, controls and rendering bounds checks. It adds
compact sprite/frame/count/state error text and read-only USB message type 3
(`tools/read_runtime_status.py --error`) to capture the exact stop reason.
There is no sprite-rendering workaround in this build. Native asset coverage
passes 211 state references across 23 families; the real host renderer passes
all 66 guard/imp states plus overkill deaths. Hardware reproduction is pending.

The exact `Doom-SMK-37_021` restart was verified after installing from build 20.
Initial error text was empty, both cores were active, and audio blocks advanced
from 18,703 to 18,879 with zero missed deadlines, worker faults or rejected
requests. The Pro app is 580,156 bytes, SHA-256
`7837707d53402ff7a6e2eba3c27de76c4f105e397a13d6fad98f9a605fe2a350`.
Its package SHA-256 is
`956ffe446b9b5aa0822a7a567b18e897dc80796f1c2bf7e50c1149c849fea03c`.
The exact package passed the real updater core on simulated flash, preserving
the protected boot and tail regions. Build 21 Elite hardware is untested.

The owner subsequently reported the light changes again during gameplay on
build 21. USB confirmed empty stop text, two active cores, advancing audio
counters (44,960 to 45,136), brightness 150, zero brightness changes and zero
reported LED transfer errors. The intended light state was 0x96c707. This
rules out a commanded brightness change in that observation; it does not
prove the electrical LED waveform or actual colors are correct. No transport
fix is claimed. The distinction between changes only on pad transitions and
changes with hands off is awaiting the owner's observation.

The 50-second error monitor captured 99 empty-error responses. The exact
native WAD also passed the host campaign bot at normal, low-detail and hard
settings (26 level completions each), death/retry, and all nine map starts,
with native memory limits. Logs are in `build/pad-hardware21/`. These checks
did not reproduce or resolve the hardware sprite crash.

### Build 20: red Fire / green Use

The owner reported that build 19's movement-pad colors/brightness appeared to
change when pressing Fire or Use. Build 20 changes bottom pad 7 to green and
bottom pad 8 to red and adds read-only pad/brightness telemetry. The LED
transport and Fader 2 control algorithm are unchanged; a specific cause of the
earlier visual behavior has not been established.

Build 20 was installed from running Doom 19 using the native USB helper, with
transfer completion and exact `Doom-SMK-37_020` restart verified. The owner
then repeatedly pressed Fire/Use with Fader 2 untouched and confirmed:
"They stay steady now."

The corresponding 44.969-second recording contains 1,602 samples. Brightness
remained exactly 150 with zero brightness changes. Only the expected action
pad masks appeared (0x4000, 0x8000, 0xc000, or zero). LED writes advanced from
99 to 124 with zero reported transport errors. Fader 2 raw samples ranged
from 219 to 224. Evidence is retained locally in
`build/pad-hardware20/pad-observation.json` and `install-log.json`.

The Pro app is 580,296 bytes, SHA-256
`9ef4a8df5145f6c8ef9984e35a911e18dbb1f347029dec7ebc03b4a47f2158cd`.
Its package hash is
`e6398ab6e7f0dcfce8fc67aa2e1d1e5f2f0dff18569560305284e270643272d2`.
The actual package passed the simulated-flash updater, preserving protected
boot and tail data. Pad tests cover the new red/green colors at every brightness.

`tools/read_runtime_status.py --pads --samples 5` reads diagnostic message type
2. It reports brightness, Fader 2 samples, held/queued pads, the last sent light
state, write/error counts, and brightness-change counts. It cannot change the
device or write flash. Existing audio telemetry remains message type 1.

### Initial build 19

Host checks passed on 2026-10-20:

- Pad mapping, simultaneous/held inputs, short attacks, release events.
- Every brightness level and held-pad position through the actual GRB encoder;
  unused pads overwrite prior colors with zero.
- Shared light transport framing, DMA barriers, LCD restoration and timeout cleanup.
- Dirty-register ADC/scanner startup, mux ownership, bounded ADC failure and shutdown.
- Existing K1/K2, dual-core audio-worker and public SMK updater regressions.

New driver/control tests run with AddressSanitizer and UndefinedBehaviorSanitizer
and are included in CI. Native builds enforce application, RAM and loader bounds.
Exact build manifests are in `build/native/<board>/manifest.json`.

Pro application: 580,052 bytes, SHA-256
`bd02bde7d6b825a2496b2d46bb30acf3194fbb58fb111fd43c3b2235567e4fed`.
Elite application: 580,056 bytes, SHA-256
`377547b5135ce820c68fb436c090f8f406c94eac432f2f762f5c63ee85eb5491`.
Both leave at least 1,508 bytes inside the existing common app limit and
3,064 bytes before the CPU0 RAM guard; no game assets or audio are removed.
Both exact generated install packages passed the actual updater core on
simulated flash (152 changed sectors each, protected boot and tail preserved).

After the owner reconnected the SMK-37 Pro, USB identified Doom-SMK-37_017.
The pinned Pro package installed through that build's updater and restarted
as exactly `Doom-SMK-37_019`, without a power cycle. Native helper stages held
the shared USB lock, checked the target package hashes, and used separate
processes across USB re-enumeration. The raw local transfer log is in
`build/pad-hardware/install-log.json`.

Two post-install runtime samples reported two active cores and audio on CPU1.
Audio blocks advanced from 4,276 to 4,452; worker jobs from 4,277 to 4,453.
Both samples reported zero missed deadlines, worker faults and rejected
requests, with a maximum audio job of 320.79 microseconds.

The owner confirmed build 19's controls worked, while reporting the light
issue investigated in the build 20 observation above.
GameDude-to-Doom warm handoff, power-cycle behavior, and Elite hardware
validation remain pending. This was a native USB install, not a Chrome
disconnect test. Do not treat compiled or simulated results as physical
confirmation.

To repeat host checks (Linux/WSL), compile and run each of
`tests/smk_doom_pads.c`, `tests/smk_doom_scan.c`, and
`tests/smk37_light_transport.c` with
`cc -std=c11 -O1 -g -fsanitize=address,undefined`.

Build the candidate with the usual toolchain:
`python3 tools/build_native.py --board smk37-pro --campaign --revision 23 --toolchain <path>`.
Use `smk37-elite` for the separate Elite application. Applications under
`build/native/` are app-only images, not complete stock/recovery packages.
