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
| Bootloader with the SD game menu | `platform/bootloader` | built and tested on the PC; its first hardware session is still to come (`HARDWARE.md`) |
| Uploader source (`chgame-upload`) | `platform/bootloader/host/py` | in use |
| Graphics | `platform/libraries/CHGfx` | 1.3.0 |
| SD card / FAT | `platform/libraries/CHSd` | 1.0.0; never yet run against a real card on a board |
| Buttons, frame pacing, exit to menu | `games/*/src/CHGame.h/.cpp` | identical in all 20 games |
| Sound | `games/*/src/audio/` | the same sequencer in every game, each with its own effect list; some add `Music` |
| Saving, debug protocol, `RamFunc.h` | `games/*/src/save`, `debug`, `RamFunc.h` | the same code, with per-game ids (save magic, handshake, section prefix) |
| Twenty games, one utility | `games/`, `utilities/CHSDtoUSB` | building; verification per game in [status.md](status.md) |
| PC tools | `tools/`, per-game `tools/` | in use |

## What the first release needs

### 1. Release tooling

The board package's release scripts stayed behind in CH32SerialBoot:
`tools/release.sh`, `make_package.py`, `make_tool_archives.py` and the
package index they write (`platform/board/docs/building.md` describes
them). They have to come here before a release can be cut from this
repository.

- The package index then lives at
  `https://github.com/bateske/CHGame/releases/latest/download/package_chgame_index.json`.
- Every place that gives the old URL changes with it: the root README's
  *Installing* section, `CLAUDE.md`, `platform/README.md` and
  `utilities/CHSDtoUSB/README.md`. The games' READMEs link to the root
  README instead of repeating it.
- Decide how people on the old URL find the new one. An index is not
  redirected by itself; a last release on the old URL that says so is one
  way.
- The toolchain and `wchisp` archives are referenced by the index, not
  stored here (`platform/board/THIRD-PARTY.md`). That stays as it is unless
  they are to be mirrored.

### 2. The menu bootloader in the package

The package's `bootloaders/CHGame/chgame_bootloader.bin` is the 0.2.4
bootloader. The release must carry `platform/bootloader/release/chgame_sdboot.bin`
for *Burn Bootloader* and for the self-update. Do this after the hardware
session in `platform/bootloader/HARDWARE.md` has passed.

### 3. One `CHGame` library

A board package can bundle libraries (`libraries/` inside the platform
folder, where `SPI`, `Wire` and `EEPROM` are now). The unified library goes
there, with `CHGame.h` as its one include and the existing cores under it:

| Layer | Source today | Notes for the move |
|---|---|---|
| Buttons, pacing, exit to menu | `games/*/src/CHGame.*` | Identical already. The `.cpp` differs only by a pragma. |
| Graphics | `platform/libraries/CHGfx` | Keeps its own sources, tests and `extras/`. Its `library.properties` still gives the CH32SerialBoot URL. |
| SD card | `platform/libraries/CHSd` | Once it is a library the board package provides, the three SD games no longer need generated copies, and `tools/vendor.py` goes away. The bootloader's C fork (`src/sd.c`, `fat.c`) remains. |
| Sound | `games/*/src/audio` | The sequencer is shared; the effect and song tables are per game and stay with the game. |
| Saving | `games/*/src/save` | Shared mechanism; the magic is per game and must stay unique. |
| Debug protocol | `games/*/src/debug` | Shared protocol; the handshake id and hook are per game. The simulator and every `chdrive.py` depend on it. |
| `RamFunc.h` | `games/*/src/RamFunc.h` | The section prefix is per game. |

Constraints that the move has to respect:

- **Flash.** Most games are within 1 KB of full. A library build must not
  cost bytes compared with the in-sketch copies; with `-flto` it should not,
  but each game's size has to be measured before and after.
- **Pixels.** The simulator frames of every game must be identical before
  and after (CLAUDE.md rule 2). That is the test for this whole step.
- **The simulator** (`tools/chsim/chsim.py`) compiles a game's `src/` plus
  CHGfx. It has to learn where the library's sources are.
- **Adapted copies.** Some games changed their copy of a shared module
  (`gfx/`, `fx/`, and in places `audio/`). Only what is truly common moves;
  [game-anatomy.md](game-anatomy.md) says which is which.

### 4. The games as examples

The Arduino IDE lists a library's `examples/` folder under *File >
Examples*. The games become the `CHGame` library's examples.

- A sketch opened from *Examples* is read-only and is copied to the
  sketchbook when saved. A game must build from that copy with nothing but
  the board package installed.
- The games' `tools/` folders find the shared tools by the layout
  `games/<Name>/tools -> ../../tools`. Decide whether the package ships the
  games with their tools, or the sketches only, with the tools used from a
  clone.
- `utilities/CHSDtoUSB` is GPL-3.0. If it ships in the package, it ships as
  its own example with its own licence, as it is kept apart here.
- Size: the games' art sources and README GIFs are much larger than their
  code. Decide what goes in the package archive.

### 5. The PC tools

They are here already. What a release should add is a way to use them
without reading the source:

- one requirements file and one entry point per job (simulator, upload,
  screenshot, pack, card), documented in `tools/README.md`;
- the uploader's source (`platform/bootloader/host/py`) named among the
  tools, since it is the thing people outside Arduino need first;
- the candidates for sharing already listed at the end of
  [tools/README.md](../tools/README.md).

### 6. Known problems to fix on the way

These were recorded as "for upstream" while the board package was a copy.
It is ours now:

- Linux: `ch32yyxx.h` includes `core_riscv_cH32yyxx.h` (capital H).
- Stale comments about an 8 KB bootloader and an app at 0x2000.
- The names: the root `LICENSE` file is missing (the README states
  Apache-2.0 for root files and `docs/`), and "CHCasino" remains in code
  comments, `tools/NOTICE`, a variable in each `device.py` and the
  bootloader's `casino` theme description. None of it affects a build.

## Order

1 and 2 give a release from this repository that matches what people have
now plus the menu. 3 and 4 are the unification and depend on each other.
5 and 6 can be done at any time.
