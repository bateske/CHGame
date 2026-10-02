# Roadmap: from this repository to one board package

The goal ([README](../README.md#what-this-repository-is-for)): someone
installs **CHGame** in the Arduino Boards Manager and has everything: the
core, the menu bootloader, one `CHGame.h` library, the casino games as
examples. An update delivers all of it together. The PC tools live in the
same repository.

Everything needed exists here already. Nothing below asks for a new
feature; it is all moving, joining and packaging what there is. This page
records what is in place and what each step involves, so the work can be
done in order and checked.

## What is in place

| | Where | State |
|---|---|---|
| Arduino core, variant, linker scripts, Tools menus | `platform/board/arduino/CHGame` | 0.2.4, as released |
| Bootloader with the SD game menu | `platform/bootloader` | built and tested on the PC; installed and checked on a board on 2026-10-01 (`test/hil/RESULTS-2026-10-01.md`) |
| Uploader: `chgame-upload` in Go (the executable the board package installs; Windows, Linux, macOS) and the same tool in Python (`chgame_upload`, what the repository's tools use) | `platform/bootloader/host/go`, `host/py` | 0.2.0 here, with the bootloader update over USB and `burn`; the installed package has 0.1.0. Shared test vectors (`test/protocol/`) hold the two together |
| Graphics | `platform/board/arduino/CHGame/libraries/CHGfx` | 1.3.0 |
| SD card / FAT | `platform/board/arduino/CHGame/libraries/CHSd` | 1.0.0; never yet run against a real card on a board |
| The `CHGame` library: buttons and pacing, palette, drawing, the 3x5 font, lettering, effects maths, sound, saving, the debug protocol, `RAMFUNC` | `platform/board/arduino/CHGame/libraries/CHGame` | every game is built on it ([its README](../platform/board/arduino/CHGame/libraries/CHGame/README.md)); in the board package's `libraries/` folder with CHGfx and CHSd |
| Twenty games, one app | the CHGame library's examples: `platform/board/arduino/CHGame/libraries/CHGame/examples/games/`, `apps/CHSDtoUSB` | building; verification per game in [status.md](status.md) |
| PC tools | `tools/` (one entry point, `chgame`; `pip install -e .`), per game a `tools/game.py`, a `chdrive.py` and scripts | in use; one simulator for the games, CHGfx's examples and its tests |

## What the first release needs

### 1. Release tooling

**Done in this repository** (2026-10-02): `tools/release/` (`release.py`,
`build_uploader.py`, `make_tool_archives.py`, `make_package.py`, all Python)
builds the uploader for the five hosts, the platform archive and the Boards
Manager index, and publishes them with `gh`
(`platform/board/docs/building.md`). `python tools/release/release.py
--dry-run` makes the whole set in `out/dist/`. What is left is the release
itself: bump `platform.txt` to 0.3.0, retitle the changelog's Unreleased
section, run it.

- The package index then lives at
  `https://github.com/bateske/CHGame/releases/latest/download/package_chgame_index.json`.
- Every place that gives the old URL changes with it: the root README's
  *Installing* section, `CLAUDE.md`, `platform/README.md` and
  `platform/board/arduino/CHGame/libraries/CHGame/examples/apps/CHSDtoUSB/README.md`. The games' READMEs link to the root
  README instead of repeating it.
- Decide how people on the old URL find the new one. An index is not
  redirected by itself; a last release on the old URL that says so is one
  way.
- The toolchain and `wchisp` archives are referenced by the index, not
  stored here (`platform/board/THIRD-PARTY.md`). That stays as it is unless
  they are to be mirrored.

### 2. The menu bootloader in the package

**Done in this repository** (2026-10-02). `bootloaders/CHGame/` carries the
menu bootloader, the no-menu build and the 0.2.4 one; *Tools > Bootloader*
chooses, and *Burn Bootloader* writes it over USB with the programmer
**CHGame USB** (`chgame-upload burn -method usb`, through the bootloader
already on the board) or through the factory ISP. Tried on a board with
`arduino-cli burn-bootloader`: every change between the three, then
*Upload Using Programmer* and a normal upload.

**What is left for the release:** the release itself. `tools/release/release.py`
builds the `chgame-upload` 0.2.0 archives for the five hosts and names 0.2.0
as the package's tool dependency in the index. `platform.txt` here needs
0.2.0: the 0.1.0 tool has no `burn` command.

### 3. One `CHGame` library

**Done in this repository** (2026-10-02). `platform/board/arduino/CHGame/libraries/CHGame` is
the library, `#include <CHGame.h>` its one include, and all twenty games
are built on it. What each game carried its own copy of is now the
library's:

| Layer | In the library | What was decided |
|---|---|---|
| Buttons, pacing, exit to menu | `chgame/Input` | as it was in every game |
| Palette | `chgame/Palette` | one superset; a game passes its own colours or felts as data |
| Drawing, the 3x5 font | `chgame/Draw` | one font for all: five games' `M` changed by a pixel; one `sprite4` superset |
| Lettering | `chgame/Mask` | the CHBingo/CHCraps signature |
| Effects maths | `chgame/Fx` | one `ease` table set; the CHFour family's moves a pixel here and there |
| Particles, banners, floating text | `chgame/Sizzle` (`Sizzle.h` + `Sizzle.inl`) | one body, configured per game with `SIZZLE_*` switches in its `src/fx/Fx.h` and compiled in its `src/fx/Fx.cpp` (the library is compiled apart and cannot see a sketch's defines); every release image byte for byte unchanged |
| Number formatting | `chgame/Fmt` | the union of all variants |
| Sound | `chgame/Audio` | one engine: 3-byte steps (20 Hz, 2 ms), priorities, soft and glide flags, semitone shifts, Playtune scores and one-voice melodies, the LED. Each game keeps its own effect tables (`src/audio/Sounds.cpp`) |
| Saving | `chgame/Save` | the record every game wrote, byte for byte (old saves still load); each game keeps its magic and what it saves |
| Debug protocol | `chgame/Debug`, `chgame/Config` | one protocol, on with `CHGAME_DEBUG`; CHBlackjack now gives the common answers |
| `RAMFUNC` | `chgame/RamFunc` | `RAMFUNC(name)` for a sketch, `CHGAME_RAMFUNC` inside the library |
| Frame loop | stays in each game | it is the part a reader should see; the shape is the same everywhere |

Tools moved with it: one `tools/device.py`, one script driver
(`tools/chsim/chdrivelib.py`, which each game's `chdrive.py` extends with
its own commands), one sound preview (`tools/audio/preview.py`).

How it was checked: every game's simulator frames before and after (all
identical, except the deliberate one-pixel changes above, measured and
listed in [unification.md](unification.md)); every sound effect
millisecond by millisecond against the old engine; every save layout
offset by offset; every game's size (each fits, both save pages kept);
and every script once more under valgrind.

**In the board package** (2026-10-02, recorded in
[bundling-plan.md](bundling-plan.md)): `CHGame`, `CHGfx` and `CHSd` are in
the platform's `libraries/` folder, beside `SPI`, `Wire` and `EEPROM`, and
are edited there. The three SD games include CHSd as a library; their
generated copies and `vendor.py` are gone. The bootloader's C fork
(`src/sd.c`, `fat.c`) remains.

**What is left:** the release. Until a package cut from this repository is
installed, `chgame build` passes the three folders with `--library`
(and keeps doing so afterwards, so a clone builds against its own sources).
The acceptance test of the first release is one game built with plain
`arduino-cli compile` and no `--library`.

### 4. The games as examples

**Done in this repository** (2026-10-02). The Arduino IDE lists a library's
`examples/` folder under *File > Examples*, with a submenu for each folder
in it. The CHGame library's examples are:

| Folder | What | Menu |
|---|---|---|
| `examples/Hello` | the smallest complete sketch | *CHGame > Hello* |
| `examples/games/<Name>` | the twenty casino games | *CHGame > games > CHFour* ... |
| `examples/apps/<Name>` | sketches that are not games: CHSDtoUSB | *CHGame > apps > CHSDtoUSB* |

Each game keeps its whole folder there: sketch, `src/`, `tools/`, `docs/`,
`NOTES.md`. The shared tools stay in the repository's `tools/`; a game
reaches them through the `chgame` command, and they take a game by name
(`tools/paths.py`). Every release image is byte for byte what it was in
`games/`, and every simulator reel frame for frame.

**What is left for the release:**

- A sketch opened from *Examples* is read-only and is copied to the
  sketchbook when saved. The sketch builds from that copy; its `tools/`
  need the repository (they look for its `tools/` folder above them) and
  say so when it is not there.
- Decide what the package archive carries: the sketches alone, or with
  their tools, art sources and README GIFs (much larger than the code).
- CHSDtoUSB is GPL-3.0 and keeps its own `LICENSE` in its folder, apart
  from the Apache-2.0 library it is an example of.

### 5. The PC tools

They are here already. What a release should add is a way to use them
without reading the source:

- ~~one requirements file and one entry point per job~~ done 2026-10-02:
  `pip install -e .` and the `chgame` command (`tools/chgame.py`), one
  environment for every tool, documented in `tools/README.md`;
- the uploader named among the tools: done; `chgame upload` and `chgame
  uploader` are the Python one, and the release attaches the Go binaries;
- the candidates for sharing listed at the end of
  [tools/README.md](../tools/README.md): `check.py`, `run_tests.py`, the
  redraw and save checks are shared since 2026-10-02 (`tools/game.py` per
  game, and every game has `chgame check`); so are the art the games had
  in common (`tools/art/common/`), the mock-up kit, the music composer and
  the font tools. `sheet.py` is the one left.
- one simulator: `tools/chsim` runs the games, CHGfx's examples and
  CHGfx's tests (2026-10-02); CHGfx's `extras/sim` is gone.

### 6. Known problems to fix on the way

These were recorded as "for upstream" while the board package was a copy.
It is ours now:

- ~~Linux: `ch32yyxx.h` includes `core_riscv_cH32yyxx.h` (capital H).~~
  Fixed in `platform/board` on 2026-10-02; ships with 0.3.0.
- Stale comments about an 8 KB bootloader and an app at 0x2000.
- ~~The root `LICENSE` file is missing.~~ Added on 2026-10-02 (Apache-2.0,
  with a `NOTICE`). (The working name "CHCasino" left the code and comments
  on 2026-10-02.)

## Order

1 and 2 give a release from this repository that matches what people have
now plus the menu. 3 is done; 4 puts the games beside the library as its examples.
5 and 6 can be done at any time.
