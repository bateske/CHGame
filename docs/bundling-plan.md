# The libraries in the board package

What was left of [roadmap](roadmap.md) step 3, done on 2026-10-02: `CHGame`,
`CHGfx` and `CHSd` are in the board package's `libraries/` folder, beside
`SPI`, `Wire` and `EEPROM`, and the generated copies of CHSd in three games
are gone. This page records what was decided, what changed and how it was
checked.

## What changed for whom

| | Before | Now |
|---|---|---|
| Where the libraries are edited | `platform/libraries/{CHGame,CHGfx,CHSd}` | `platform/board/arduino/CHGame/libraries/{CHGame,CHGfx,CHSd}`: the folder that is released is the folder that is edited |
| A build in this repository | `tools/device.py` passed `--library` for CHGfx and CHGame | it passes all three from the new folder (Arduino links only the ones a sketch includes) |
| The three SD games | compiled a generated copy in `src/sd/` | `#include <Fat.h>` / `<SdSpi.h>` from CHSd |
| The simulator | each SD game kept the pretend card in `tools/chsim/host/` | `chsim.py` adds CHSd's `src/Fat.cpp` and `host/sd_host.cpp` for a sketch that includes CHSd |
| The simulator's card | `CHWD_CARD`, `CHCW_CARD`, `CHWW_CARD` | one name, `CHSD_CARD` |
| Someone with the board package | installs the core, then copies CHGfx and CHGame into the sketchbook | the same until the first release from this repository; then `#include <CHGame.h>` works with nothing else installed |

## Decisions

- **The master copies moved** (`git mv`), rather than being copied in by a
  release script: one copy, nothing to go stale.
- **`--library` stays for good.** arduino-cli compiles the core from the
  *installed* package (0.2.4), which has no bundled libraries. A
  `--library` path wins over a bundled library of the same name, so a clone
  always builds against its own sources, before and after the release.
- **Versions.** Each library keeps its own number in `library.properties`
  (CHGfx 1.3.0, CHSd 1.0.0, CHGame 0.1.0), as the libraries bundled with
  other Arduino cores do: the number says when the library's API changed,
  the package version says what was shipped together.
- **CHGfx on its own.** `python tools/libzip.py CHGfx` makes
  `out/CHGfx-<version>.zip` from the bundled folder for *Add .ZIP Library*
  or a release attachment: one source, two ways to get it. The Library
  Manager index takes a repository with the library at its root, so a
  listing there would need a mirror repository filled from that ZIP.
- **`architectures=ch32v`** for all three.
- **Gone:** `CHSd/tools/vendor.py`; `platform/board/arduino/CHGame/libraries/CHGame/examples/games/{CHWords,CHCrossword,CHWordWheel}/src/sd/`
  and their `tools/chsim/host/{VCard.h,sd_host.cpp}`; CHCrossword's
  `tools/puzzles/fatimg.py` (its `mkcard.py` imports CHSd's).
- **Stays:** the bootloader's C fork of CHSd (`platform/bootloader/src/sd.c`,
  `fat.c`): a fix to one belongs in the other.

## How it was checked

Baseline first: all 20 release images (size and hash), every script of the
three SD games in the simulator (236 screenshots and GIFs), and the hash of
every game's README reel.

**Step 1, CHSd as a library (the only step that changes what is compiled).**

| Game | Image before | Image now | Room under 50,432 B | RAM |
|---|---|---|---|---|
| CHWords | 50,328 | 50,324 | 108 | 15,788 (same) |
| CHCrossword | 50,360 | 50,352 | 80 | 17,276 (same) |
| CHWordWheel | 50,368 | 50,312 | 120 | 14,956 (+4) |

- All three keep both save pages.
- Their `check.py` passes (host tests against CHSd's sources, FAT card
  images, every script), and all 236 images are pixel for pixel the ones
  from before.
- CHSd's own `tests/run_tests.py` passes.

**Step 2, the move.**

- All 20 games rebuilt: the 17 that do not use the card are byte for byte
  the images from before the move; the three SD games are as in the table.
- All 20 simulators rebuilt from the new folder and every README reel
  recorded again: all 20 GIFs identical.
- From the new paths: `tools/sdcard/mkcard.py` built and packed all 21
  packages and `chgpack.py verify` accepts them; every game's host tests
  pass (20 of 20); the sound preview runs.
- The bootloader's PC suite passes. It forks a process per boot, so on
  Windows it now cross-compiles its test programs for Linux with zig and
  runs them under WSL (`platform/bootloader/README.md`, Testing).

**Step 3, the games as examples** (roadmap step 4, the same day).

`games/` and `utilities/CHSDtoUSB` moved into the CHGame library:
`examples/games/<Name>` and `examples/apps/CHSDtoUSB`, beside
`examples/Hello`. Each game kept its whole folder. What changed with it:

- every path from a game up to the repository's `tools/` and `platform/`
  (nine folders now, not two);
- `tools/run.py` in each sketch, which runs a shared tool from the game's
  folder (`python tools/run.py readme_gif.py`);
- `tools/paths.py`, by which the shared tools take a game by name from
  anywhere (`python tools/readme_gif.py CHFour`,
  `python tools/device.py --sketch CHFour build`).

Checked: all 20 release images byte for byte the ones from before this
step; all 20 README reels identical; all 20 games' host tests; the nine
`check.py`; the save tests; the card builder; the bootloader suite.

## Still to do, with the first release

- The package archive carries `libraries/CHGame`, `CHGfx`, `CHSd` (roadmap
  step 1 brings the release scripts here).
- Acceptance test: install it, build one game with plain
  `arduino-cli compile` and no `--library`.
- Then drop "copy CHGfx into your sketchbook" from the root README and the
  `--library` flags from the plain `arduino-cli` lines in the docs.
- The games as the library's examples (roadmap step 4) go in
  `libraries/CHGame/examples/`.
