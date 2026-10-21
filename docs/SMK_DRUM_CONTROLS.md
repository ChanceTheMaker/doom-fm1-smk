# SMK Doom drum controls — development build 19

Branch: `feat/smk-drum-controls`, based on tested release `94e1ec1`.
This branch retains the known-flash updater policy; it does not incorporate
the separate experimental SFDP branch. The published site and binaries are
unchanged. No FM-1 firmware is installed or promoted by this work.

## Physical layout

Count each row from the left; there are eight pads per row.

| Row | 1 | 2 | 3 | 4–6 | 7 | 8 |
| --- | --- | --- | --- | --- | --- | --- |
| Top | Strafe left | Forward | Strafe right | Unassigned | Unassigned | Unassigned |
| Bottom | Turn left | Back | Turn right | Unassigned | Use | Fire |

Strafe is amber, movement cyan, and Use/Fire magenta. Unassigned pads stay
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

Owner confirmation of physical pad/brightness response is pending.
GameDude-to-Doom warm handoff, power-cycle behavior, and Elite hardware
validation remain pending. This was a native USB install, not a Chrome
disconnect test. Do not treat compiled or simulated results as physical
confirmation.

To repeat host checks (Linux/WSL), compile and run each of
`tests/smk_doom_pads.c`, `tests/smk_doom_scan.c`, and
`tests/smk37_light_transport.c` with
`cc -std=c11 -O1 -g -fsanitize=address,undefined`.

Build the candidate with the usual toolchain:
`python3 tools/build_native.py --board smk37-pro --campaign --revision 19 --toolchain <path>`.
Use `smk37-elite` for the separate Elite application. Applications under
`build/native/` are app-only images, not complete stock/recovery packages.
