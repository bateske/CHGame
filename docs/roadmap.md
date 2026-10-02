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
| The `CHGame` library: buttons and pacing, palette, drawing, the 3x5 font, lettering, effects maths, sound, saving, the debug protocol, `RAMFUNC` | `platform/libraries/CHGame` | every game is built on it ([its README](../platform/libraries/CHGame/README.md)); not yet bundled in the board package |
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

**Done in this repository** (2026-10-02). `platform/libraries/CHGame` is
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

**What is left for the board package:**

- Bundle `CHGame` (and `CHGfx`, `CHSd`) in the platform's `libraries/`
  folder, beside `SPI`, `Wire` and `EEPROM`. `tools/device.py` and the
  simulator use the copies in `platform/libraries` until then.
- With CHSd bundled, the three SD games no longer need generated copies
  and `platform/libraries/CHSd/tools/vendor.py` goes away. The bootloader's
  C fork (`src/sd.c`, `fat.c`) remains.

### 4. The games as examples

The Arduino IDE lists a library's `examples/` folder under *File >
Examples*. The library has one already, `examples/Hello` (the smallest
complete sketch); the games become the rest.

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
- The root `LICENSE` file is missing (the README states Apache-2.0 for root
  files and `docs/`). (The working name "CHCasino" left the code and
  comments on 2026-10-02.)

## Order

1 and 2 give a release from this repository that matches what people have
now plus the menu. 3 is done but for the bundling, which goes with 4.
5 and 6 can be done at any time.
