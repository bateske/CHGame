# Roadmap: from this repository to one board package

The goal ([README](../README.md#why-one-repository)): someone
installs **CHGame** in the Arduino Boards Manager and has everything: the
core, the menu bootloader, one `CHGame.h` library, the casino games as
examples. An update delivers all of it together. The PC tools live in the
same repository.

**Where it stands (2026-10-02):** release 0.3.0 is built from this
repository and passes the new-user test (`tools/release/stage.py`: a fresh
`arduino-cli` installs it from one URL and gets the core, the three
bootloaders, the three libraries and every example; all twenty games and
CHSDtoUSB compile from the installed package with no `--library`; the SD
card is packed from those builds). What is left is trying it on a board
from the IDE
([platform/board/docs/trying-a-release.md](../platform/board/docs/trying-a-release.md))
and publishing it. The list at the end, *Before and at the release*, has
it in order.

**Since (2026-10-03):** the `.chgame` format, the way games are shared
([spec/chgame.md](../spec/chgame.md)), with its reference implementation
(`tools/chcart`, `chgame export`, `chgame cart ...`) and conformance
fixtures; the release attaches every game as one cart. The bootloader's
menu v2 reads what runtime preparation writes ([spec/card.md](../spec/card.md)):
folders, the card's order and picture, a game started at power-on, in a
Rainbow and a Static style. It ran on the board on 2026-10-03
([RESULTS](../platform/bootloader/test/hil/RESULTS-2026-10-03.md)), and
`release/` and the board package carry it.

This page records what is in place and what each step involved.

## What is in place

| | Where | State |
|---|---|---|
| Arduino core, variant, linker scripts, Tools menus | `platform/board/arduino/CHGame` | 0.3.0, released 2026-10-07 |
| Bootloader with the SD game menu | `platform/bootloader` | menu v2 (2026-10-03), Rainbow and Static (White until that evening, when colour 15 became the picture's magenta as painted; that build has not run on a board): the PC suite, and installed and checked on a board the same day (`test/hil/RESULTS-2026-10-03.md`; the first menu on 2026-10-01) |
| The visual menu: the same bootloader, one picture at a time, no text ([visual-menu.md](visual-menu.md)) | `platform/bootloader` (`--ui=visual`), `tools/artkit`, each example's `tools/cart.py` | 2026-10-03: Rainbow and Static, in Burn Bootloader; the PC suite passes on test cards and the real casino card (which is now in genre folders, with box art for all 22 programs, repainted on 2026-10-04 with the menu's own pictures: [cover-art.md](cover-art.md)). Not yet run on a board (`platform/bootloader/HARDWARE.md`, "The visual menu") |
| The `.chgame` format and the SD card's layout | `spec/`, `tools/chcart` | version 1 and layout 2 (with the visual menu's pictures: `menu.cover`, `menu.about`, folder covers, `cartImage` in each CHG file); reference implementation, 24 unit tests, 27 conformance fixtures; the repository's games and release use it |
| Uploader: `chgame-upload` in Go (the executable the board package installs; Windows, Linux, macOS) and the same tool in Python (`chgame_upload`, what the repository's tools use) | `platform/bootloader/host/go`, `host/py` | 0.2.0 here, with the bootloader update over USB and `burn`; the installed package has 0.1.0. Shared test vectors (`test/protocol/`) hold the two together |
| Graphics | `platform/board/arduino/CHGame/libraries/CHGfx` | 1.3.0 |
| SD card / FAT | `platform/board/arduino/CHGame/libraries/CHSd` | 1.0.0; never yet run against a real card on a board |
| The `CHGame` library: buttons and pacing, palette, drawing, the 3x5 font, lettering, effects maths, sound, saving, the debug protocol, `RAMFUNC` | `platform/board/arduino/CHGame/libraries/CHGame` | every game is built on it ([its README](../platform/board/arduino/CHGame/libraries/CHGame/README.md)); in the board package's `libraries/` folder with CHGfx and CHSd |
| Twenty games, three apps | the CHGame library's examples: `platform/board/arduino/CHGame/libraries/CHGame/examples/Games/`, `apps/CHStlView`, `apps/CHSDtoUSB`, `apps/CHSDtoSerial` | building; verification per game in [status.md](status.md) |
| PC tools | `tools/` (one entry point, `chgame`; `pip install -e .`), per game a `tools/game.py`, a `chdrive.py` and scripts | in use; one simulator for the games, CHGfx's examples and its tests |

## What the first release needs

### 1. Release tooling

**Done in this repository** (2026-10-02): `tools/release/` (`release.py`,
`build_uploader.py`, `make_tool_archives.py`, `make_package.py`, all Python)
builds the uploader for the five hosts, the platform archive and the Boards
Manager index, and publishes them with `gh`
(`platform/board/docs/building.md`). `python tools/release/release.py
--dry-run` makes the whole set in `out/dist/`. `platform.txt` says 0.3.0
and the changelog has its section.

Also done the same day: `stage.py` builds the release as `0.3.0-local` with
localhost URLs, `serve.py` serves it to the Arduino IDE, and
`acceptance.py` is the new-user test, which `release.py` now runs before it
publishes anything; it also packs the release's SD card zip. **0.3.0 was
released on 2026-10-07** (`v0.3.0`, with the casino cart and its SD card
zip). What is left:

- (Done) The package index lives at
  `https://github.com/bateske/CHGame/releases/latest/download/package_chgame_index.json`,
  and the README, `CLAUDE.md` and `platform/README.md` give that URL only.
- Decide how people on the old URL find the new one. An index is not
  redirected by itself; a last release on the old URL that says so is one
  way.
- The toolchain and `wchisp` archives are referenced by the index, not
  stored here (`platform/board/THIRD-PARTY.md`). That stays as it is unless
  they are to be mirrored.

### 2. The menu bootloader in the package

**Done in this repository** (2026-10-02). `bootloaders/CHGame/` carries the
menu bootloader, the no-menu build and the 0.2.4 one (since replaced by the
menu's other two colour themes); *Tools > Bootloader*
chooses, and *Burn Bootloader* writes it over USB with the programmer
**CHGame USB** (`chgame-upload burn -method usb`, through the bootloader
already on the board) or through the factory ISP. Tried on a board with
`arduino-cli burn-bootloader`: every change between the three, then
*Upload Using Programmer* and a normal upload.

**What is left for the release:** the release itself. `tools/release/release.py`
builds the `chgame-upload` 0.2.0 archives for the five hosts and names 0.2.0
as the package's tool dependency in the index. `platform.txt` here needs
0.2.0: the 0.1.0 tool has no `burn` command (nor `pack`, which every build
now runs).

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

**What is left:** the release. `chgame build` passes the three folders with
`--library` and keeps doing so, so a clone builds against its own sources.
The acceptance test, every game built with plain `arduino-cli compile` and
no `--library` from an installed package, passes against the staged 0.3.0.

### 4. The games as examples

**Done in this repository** (2026-10-02). The Arduino IDE lists a library's
`examples/` folder under *File > Examples*, with a submenu for each folder
in it. The CHGame library's examples are:

| Folder | What | Menu |
|---|---|---|
| `examples/Hello` | the smallest complete sketch | *CHGame > Hello* |
| `examples/Games/<Name>` | the twenty casino games | *CHGame > Games > CHFour* ... |
| `examples/Apps/<Name>` | sketches that are not games: CHStlView, CHSDtoUSB, CHSDtoSerial | *CHGame > Apps > CHStlView*, *CHSDtoUSB*, *CHSDtoSerial* |

Each game keeps its whole folder there: sketch, `src/`, `tools/`, `docs/`,
`NOTES.md`. The shared tools stay in the repository's `tools/`; a game
reaches them through the `chgame` command, and they take a game by name
(`tools/paths.py`). Every release image is byte for byte what it was in
`games/`, and every simulator reel frame for frame.

**Decided and checked** (2026-10-02):

- The package carries each game's whole folder, tools, art sources and
  README GIF included (18 MB compressed, the GIFs most of it): the README
  a user opens from the sketch folder has its picture. Dropping the GIFs is
  one name in `_common.PACKAGE_EXCLUDE_NAMES`.
- A sketch opened from *Examples* is read-only and is copied to the
  sketchbook when saved. It builds from that copy (the new-user test
  compiles copies). Its `tools/` need the repository.
- The games' README line on installing points at the IDE route and at the
  repository's README by absolute URL, since the README is also read
  inside the package.
- *Smallest + LTO* is the default *Optimize* option from 0.3.0: with `-Os`
  the larger games do not fit (CHBackgammon, CHChess, CHCrossword and
  CHWords among them). With it, 17
  games fit with the IDE's defaults; the three SD games also need *USB:
  Upload only* and stop with a message that says so.
- CHBlackjack's `tools/probes/FlashProbe` is left out of the package: *File
  > Examples* showed it nested inside the game. The packager now refuses
  any sketch nested in another example.
- CHSDtoUSB and CHSDtoSerial are GPL-3.0 and keep their own `LICENSE` in
  their folders, apart from the Apache-2.0 library they are examples of.

### 5. The PC tools

What an Arduino user needs is in the package, in `chgame-upload` (the one
executable the IDE can run): upload, burn the bootloader, and, since
2026-10-02, `pack`, which every build runs so that *Export Compiled Binary*
leaves a `.chg` for the SD menu. Every game is a `.chgame` cart beside
each release, with its SD card as a zip. Making, editing and deploying carts
is Python (`chgame cart`), offline: the web emulator and its tools, a
separate project, build on `spec/`. The developer tools (simulator, scripts, screenshots,
GIFs, sound preview) are Python and need a clone. Before that, what was
done to use them without reading the source:

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
- the web project's suggestions of 2026-10-06: its system screens are
  `menu.systemImages` (`x-chgame-web` version 1 read as an alias); in place
  of its SD resource sidecar, each CHG file carries the game's record and
  `chgame cart backup` makes a card into a cart again, SD files included
  ([spec/README.md](../spec/README.md) says why).

### 6. Known problems to fix on the way

These were recorded as "for upstream" while the board package was a copy.
It is ours now:

- ~~Linux: `ch32yyxx.h` includes `core_riscv_cH32yyxx.h` (capital H).~~
  Fixed in `platform/board` on 2026-10-02; ships with 0.3.0.
- ~~Stale comments about an 8 KB bootloader and an app at 0x2000.~~ Fixed
  on 2026-10-02 (`link_chgame_app.ld`, `chgame_map.h`, and `boards.txt`'s
  mention of a `gen_ld.py` that does not exist).
- ~~The root `LICENSE` file is missing.~~ Added on 2026-10-02 (Apache-2.0,
  with a `NOTICE`). (The working name "CHCasino" left the code and comments
  on 2026-10-02.)
- ~~Nothing failed when a game lost a save page.~~ Since 2026-10-07 a
  release build fails below its `SAVE_PAGES` (two by default). The title
  art had taken CHCraps past both pages (saving off) and CHTicTacToe past
  one; CHGfx 1.3.1 brought them back (50,428 and 50,232 B).

### 7. Board revisions

A Rev1 board with other pins is planned. Done on 2026-10-07, ahead of it:
the naming rule and the registry (`rev1` reserved as `CGR1`), board ids in
CHG files, in `HELLO` and in the bootloader image, the uploaders' board
checks, chcart's `--device`, and readers that use a cart's rev0 binaries
when it also carries a board they do not know
([hardware-revisions.md](hardware-revisions.md)). Left until Rev1's pinout
is settled: that page's checklist, steps 1-9 (the board package's entry and
variant, `-device` in `platform.txt`, the pins in the libraries and the
bootloader, the build tools' device option, a run on both boards).

## Before and at the release

1. **The rest of menu v2 on a board** (optional; the PC suite covers it):
   the launch game at power-on and START held, the ERROR n boxes, the
   INSTALLED PROGRAM row, a picture of one's own
   ([RESULTS-2026-10-03](../platform/bootloader/test/hil/RESULTS-2026-10-03.md)
   lists them; [HARDWARE.md](../platform/bootloader/HARDWARE.md), "Menu v2",
   has the steps).
2. **On a board, from the IDE**, with the staged package
   ([trying-a-release.md](../platform/board/docs/trying-a-release.md)):
   *Burn Bootloader* with **CHGame USB** from the installed package
   (tried with `arduino-cli` already, not yet from the IDE); Hello and a
   game uploaded with the new *Smallest + LTO* default; a `.chg` from
   *Export Compiled Binary* started from the menu; the SD card zip on a
   real card (CHSd has never read a real card on a board). CHSDtoUSB stays
   on `-Os` on the card until it is tried with LTO. Also owed since
   2026-10-07 ([../platform/README.md](../platform/README.md)): CHGfx
   1.3.1 on the panel, a 12 bpp game and `Benchmark` (16 bpp; the
   simulator does not run `CHGfx.cpp`), a debug build linked with
   `-flto-partition=one`, and CHWords started by an upload from CHSDtoUSB
   without a power cycle (CHSd's CRC fix).
3. **Date the changelog heading**, then `python tools/release/release.py`
   (it runs the new-user test again and publishes v0.3.0 with the casino
   cart and the SD card zip).
4. **The old URL.** People with the CH32SerialBoot URL are not told about
   this one. A last release there that points here is one way.
5. **Third-party archives.** The toolchain and wchisp are referenced at
   their upstream URLs, not mirrored (`platform/board/THIRD-PARTY.md`).
6. **The box art's fonts.** Fifteen of the fonts the titles are lettered
   in (most of the games' titles, the casino cover and folders, the error
   title) come from the bmf archive and old systems, whose authors stated
   no terms. Check each one, or redraw that title in a clear-terms face,
   before the release ([cover-art.md](cover-art.md#credits-fonts-in-the-titles)
   marks them). The scout that finds a face, `artkit.fontscout`, reads
   Pixel Logo Lab, which is not public: the pictures rebuild without it,
   but a new title needs it.
