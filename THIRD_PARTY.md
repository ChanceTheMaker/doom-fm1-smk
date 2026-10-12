# Source provenance

## Engine

DoomGeneric: https://github.com/ozkl/doomgeneric
Pinned revision: e257a09527062bfb986b6e5e0780839b6cbd5b71.
Stored as a Git submodule with its original history, LICENSE and source notices. Core Doom sources state GPL version 2 or later. Preserve per-file notices when adapting sources.

## Hardware references (not copied into the engine)

- ChanceTheMaker/felucca-smk and ChanceTheMaker/sloop-smk: board research and tested SMK control mappings.
- ChanceTheMaker/melodee-smk, initial port ee9cd18: shared SMK driver reference.
- Felucca by Leo Kuroshita / Hugelton Instruments: FM-1 hardware driver reference.

Existing hardware adapter files carry GPL-3.0-only notices. Retain their exact notices and record source commit/file hashes when importing them; do not copy unrelated synthesizer engines, vendor firmware or private device backups.

## Optimization research

- https://github.com/kilograham/rp2040-doom : low-memory renderer and compressed assets; RP2040-specific hardware is not directly portable.
- https://github.com/doomhack/GBADoom : another memory-constrained port to evaluate.
- https://github.com/fragglet/miniwad : potential small test IWAD; inspect its license before vendoring assets.

No WAD assets are bundled or downloaded by the build scripts.
