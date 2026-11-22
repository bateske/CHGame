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

**Since (2026-11-17):** a second board, CHGame Rev1 (Rev 1.5 uses it too),
in board package 0.4.0, released 2026-11-21: everything builds for both
boards, and the tools default to the newest. Its bootloader has run on a
Rev 1.5 board, and the Rev0 version 4 bootloader on a Rev0
([7. Board revisions](#7-board-revisions)).

**Next, after 0.4.0:** a newer compiler, GCC 16, beside WCH's GCC 8.2, for
Apple silicon, ARM Linux and smaller games ([9. A newer
compiler](#9-a-newer-compiler)).

This page records what is in place and what each step involved.

## What is in place

| | Where | State |
|---|---|---|
| Arduino core, variants, linker scripts, Tools menus | `platform/board/arduino/CHGame` | 0.4.0, released 2026-11-21 (CHGame Rev0 and CHGame Rev1); 0.3.0 (2026-10-07) had Rev0 alone |
| Bootloader with the SD game menu | `platform/bootloader` | menu v2 (2026-10-03), Rainbow and Static (White until that evening, when colour 15 became the picture's magenta as painted; that build has not run on a board): the PC suite, and installed and checked on a board the same day (`test/hil/RESULTS-2026-10-03.md`; the first menu on 2026-10-01) |
| The visual menu: the same bootloader, one picture at a time, no text ([visual-menu.md](visual-menu.md)) | `platform/bootloader` (`--ui=visual`), `tools/artkit`, each example's `tools/cart.py` | 2026-10-03: Rainbow and Static, in Burn Bootloader; the PC suite passes on test cards and the real casino card (which is now in genre folders, with box art for all 22 programs, repainted on 2026-10-04 with the menu's own pictures: [cover-art.md](cover-art.md)). Not yet run on a board (`platform/bootloader/HARDWARE.md`, "The visual menu") |
| The `.chgame` format and the SD card's layout | `spec/`, `tools/chcart` | version 1 and layout 2 (with the visual menu's pictures: `menu.cover`, `menu.about`, folder covers, `cartImage` in each CHG file); reference implementation, 24 unit tests, 27 conformance fixtures; the repository's games and release use it |
| Uploader: `chgame-upload` in Go (the executable the board package installs; Windows, Linux, macOS) and the same tool in Python (`chgame_upload`, what the repository's tools use) | `platform/bootloader/host/go`, `host/py` | 0.3.0 here (2026-11-17: rev1, and the board checked on `flash`, `pack`, `burn` and `provision`), for 0.4.0; 0.2.0 brought the bootloader update over USB and `burn`. Shared test vectors (`test/protocol/`) hold the two together |
| Graphics | `platform/board/arduino/CHGame/libraries/CHGfx` | 1.3.3 (Rev1's pins and backlight) |
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

Done on 2026-10-07, ahead of Rev1: the naming rule and the registry
(`rev1` reserved as `CGR1`), board ids in CHG files, in `HELLO` and in the
bootloader image, the uploaders' board checks, chcart's `--device`, and
readers that use a cart's rev0 binaries when it also carries a board they
do not know ([hardware-revisions.md](hardware-revisions.md)).

**Rev1 is in** (2026-11-17), for board package 0.4.0, by that page's
checklist, steps 1-7 and 9: the CHGame Rev1 board entry and variant (Rev
1.5 boards use it too), `-device` and the board macro in `platform.txt`,
Rev1's pins in the core, CHGfx (1.3.3, with the backlight), CHSd and the
CHGame library, five rev1 bootloaders within their size gates,
chgame-upload 0.3.0, the tools' `--board` (the newest board by default),
carts with a binary per board, the casino card per board (one zip each in
a release), and the bench sketch `tools/sketches/CHBoardTest`. Every rev0
image and bootloader stayed byte for byte the same.

**Not yet done: Rev1 on a board** (step 8). CHBoardTest first, then every
game and app from the rev1 card, the refusals both ways (a card, an upload
and a bootloader for the other board), and power: a music soak, battery
play. Then 0.4.0 is released (item 7 below); until then Boards Manager
offers 0.3.0, which has Rev0 alone.

**Next: Rev 1.5's power section.** Rev 1.5 is the same device, and Rev1
firmware runs on it unchanged. Its USB-PD sink, battery-powered USB host
and protected output need a library (working name CHPower), a hook that
leaves the power section as power-on left it across resets, and four test
apps. Built (2026-11-19, run on the owner's Rev 1.5): the library and two
apps, CHPDTrigger and CHUSBHost; the reset hook covers the exits through
the CHGame library, not yet an upload's touch. Moved out on 2026-11-20 into
a repository of its own (CHPower: the libraries CHPower and CHUSBHost, their
two apps and the design), an add-on rather than part of the platform, since
later boards may not have the power section.

### 8. System settings

**Reserved** (2026-11-20, for 0.4.0): the last 32 B of flash, `0xF7E0`-`0xF7FF`
at the end of the metadata page, for settings that belong to the handheld
rather than to a game, as the Arduboy reserves EEPROM's first 16 B (where
sketches kept overwriting them). No game can reach the end of flash, and
bootloader version 4 keeps the block across installs (spec/chgame.md, "The
system settings block").

**Not yet done:**
- **Format version 1**: which settings (sound, brightness, a player's name
  or id were asked for), their encoding, defaults and an integrity check.
- **Something that writes it**: a settings app in the card's APPS folder,
  or the menu. Once the block is written, each install erases the metadata
  page twice instead of once; a probe of programming over a programmed
  page on the board could bring that back to one.
- **The library's read API** and the simulator's model of the block.
- **Getting v4 onto the boards in the field**, which erase the block at
  every install until their bootloader is updated.

v4 ran on the Rev 1.5 board on 2026-11-20: a pattern in the block came
through uploads, ABORT, a self-update and an install from the card
(platform/bootloader/README.md, "Changes of 2026-11-20"). Rev0 has not run
v4 yet; it is the same code, built for its pins.

### 9. A newer compiler

**Planned for the release after 0.4.0; not started.** 0.4.0 is finished
and made stable first.

The package's compiler is WCH's GCC 8.2 (`riscv-none-embed-gcc`), a fork
of the 2018 GCC that WCH ships as binaries only. It is the one tool in the
package with no build for Apple silicon Macs, which run it through Rosetta
(Apple keeps Rosetta for general use through macOS 27 only), and none for
ARM Linux, where the package cannot be installed at all.

The way forward was suggested and worked out by **Julien Dorra**
([bateske/CHGame#23](https://github.com/bateske/CHGame/pull/23)): GCC 16.2
and binutils 2.47 with three small patches for our chip (WCH's compressed
byte and halfword loads and stores, and `interrupt("WCH-Interrupt-fast")`,
which the core's handlers use), built for Apple silicon and Intel Macs,
Linux and Windows, and checked on a Rev0 with a test sketch. Every game
and app came out smaller with it: 444 to 2,044 B, about 950 B in the
middle (CHCraps from 48 B under the save line to 1,128 B; measured here on
2026-11-20), and CHSDtoUSB moved data 5 to 7% faster in his tests. The PR
is not merged as it is: we build our own, from that work, and credit his
patches and scripts in `platform/board/THIRD-PARTY.md` where they are used.

The plan, keeping every computer that works today working:

1. **GCC 16 beside GCC 8.2**, chosen in a Tools menu (*Compiler*), with
   GCC 8.2 the default and the same choice in `chgame`. Nothing changes
   for anyone who does not pick it; Apple silicon gets a native compiler
   at once. We build it in GitHub Actions from pinned GNU sources and host
   it on this repository's releases with its source archive. It links
   WCH's C library from the installed GCC 8.2, as Julien's installer does.
   The cost: a bigger first download.
2. **GCC 16 the default**, once every game and app has been built with it
   for both boards and played on each (the simulator is compiled on the
   PC, so it cannot test the board's compiler). GCC 8.2 stays in the menu
   for a release or two. ARM Linux comes in here: Boards Manager refuses a
   package with a tool that has no build for the computer, so GCC 16 must
   bring its own C library and GCC 8.2 become optional.
3. **The bootloader on GCC 16**, separately and later: it is nearly full,
   so the room would help, but it needs its own size and power-cut tests.

All of it before macOS 28.

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
7. **0.4.0, with Rev1.** Released 2026-11-21, with the cart and an SD
   card zip per board (`CHGame-sdcard-0.4.0-rev0.zip`, `-rev1.zip`). Left:
   the rest of Rev1's bring-up on the boards (above, and
   [hardware-revisions.md](hardware-revisions.md), step 8), and installing
   from the SD card on a Rev0 with bootloader version 4.
