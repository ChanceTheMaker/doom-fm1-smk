# Source provenance

## Engine

DoomGeneric: https://github.com/ozkl/doomgeneric
Pinned revision: e257a09527062bfb986b6e5e0780839b6cbd5b71.
Stored as a Git submodule with its original history, LICENSE and source notices. Core Doom sources state GPL version 2 or later. Preserve per-file notices when adapting sources.

## Hardware adapters

- ChanceTheMaker/felucca-smk and ChanceTheMaker/sloop-smk: board research and tested SMK control mappings.
- ChanceTheMaker/melodee-smk, initial port ee9cd18: shared SMK driver reference.
- Felucca by Leo Kuroshita / Hugelton Instruments: FM-1 hardware driver reference.

Existing hardware adapter files carry GPL-3.0-only notices. Retain their exact notices and record source commit/file hashes when importing them; do not copy unrelated synthesizer engines, vendor firmware or private device backups.

## Optimization research

- https://github.com/kilograham/rp2040-doom : low-memory renderer and compressed assets; RP2040-specific hardware is not directly portable.
- https://github.com/doomhack/GBADoom : another memory-constrained port to evaluate.
- GBADoom is research only; it has not been imported. Some files retain older Doom source license wording and need per-file review before any reuse.

## Test assets

[Miniwad](https://github.com/fragglet/miniwad) is derived from Freedoom and carries the retained BSD-style notice in [licenses/miniwad.txt](licenses/miniwad.txt). Copyright 2001–2018, Contributors to the Freedoom project. License source: https://raw.githubusercontent.com/fragglet/miniwad/trunk/COPYING.adoc

`tools/fetch_test_wad.py` explicitly downloads https://soulsphere.org/random/miniwad.zip into ignored build output. Archive SHA-256: `b4c9804343be34e485fddab802c18ecf836168d733c2f03441d8a9dff80b2393`. WAD SHA-256: `daed5e9dc341a9ff4b9c6901cb8467a630bd31b87f3ecb58a93a8b2bc186fbfb`.

`tools/pack_test_wad.py` modifies that pinned fixture for local measurement. It retains MAP01, optionally prunes texture definitions, and rebuilds an aligned, deduplicated container. The asset license also applies to these generated files; the downloader places a notice alongside them. No WAD assets are tracked, and the compiler does not download them. No commercial Doom artwork is included.

## Imported native HAL and updater tools

The selected HAL headers/assembly are copied from local `melodee-smk/public-dev1`, revision `5859bc4d07e7f51a3ee8702464a8d777384da801`. Exact paths and hashes are recorded in `src/native/hal/PROVENANCE.json`. Original Felucca and SMK contributor notices remain intact.

Local package/backup helpers and browser update transport are copied from `felucca-smk` revision `cc13e146f11d93328b4fc13ec92c4d69f6bc6e76`. See `docs/UPDATER_PROVENANCE.json`. No stock firmware, calibration or private backup is tracked.

## Embedded runtime

[mpaland/printf](https://github.com/mpaland/printf), revision `d3b984684bb8a8bdc48cc7a1abecb93ce59bbe3e`, is an MIT-licensed submodule. Its original license and notices are retained. The native linker also uses libc, libm and compiler runtime from the separately installed JieLi Linux toolchain; those toolchain libraries are not vendored here. Preserve their licensing materials before distributing compiled releases.
