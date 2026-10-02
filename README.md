# CHGame

Everything for the **CHGame** handheld, in one repository: the Arduino board
package, the bootloader with its SD game menu, the graphics, SD-card and
sound code that games are built from, twenty casino games, and the PC tools
(simulator, uploader, packager, card builder).

**This repository is the source of truth for CHGame development.** It
replaces the separate repositories the pieces grew up in
(CH32SerialBoot, CHGfx and one repository per game). Those are frozen and
get no more updates; nothing here links to them at build time.

CHGame is a low-cost open colour handheld: a **WCH CH32X035** RISC-V
microcontroller (48 MHz, 62 KB flash, 20 KB SRAM), a **128x128 ST7735S**
colour LCD, a **microSD** slot on the same SPI bus as the screen, eight
buttons, a piezo speaker, a status LED and **USB-C**. It uploads over USB
with no button presses, like an Arduino Leonardo.

![The SD game menu](platform/bootloader/docs/menu.png)

> **For AI agents and new developers:** read [CLAUDE.md](CLAUDE.md) first.
> It has the build, simulator and test commands, the rules of the codebase,
> and the hardware limits.
>
> **Coming from the Arduboy?** [docs/getting-started.md](docs/getting-started.md)
> maps the Arduboy2 calls to CHGame's, explains what happens behind the
> scenes, and walks through a first sketch. The CHGame library's
> [README](platform/board/arduino/CHGame/libraries/CHGame/README.md) is the reference.

## What this repository is for

The aim is the Arduboy model, with one repository instead of several:

- **One board package.** Install "CHGame" in the Arduino Boards Manager and
  you have all you need to write for the device: the core, the toolchain,
  the uploader, the bootloaders, the libraries, and the casino games under
  *File > Examples*.
- **One include.** A sketch includes `CHGame.h` and gets the buttons, frame
  pacing, graphics, the house palette and drawing helpers, sound, saving and
  the debug protocol the simulator drives it through, with no per-sketch
  set-up of pins or drivers. The graphics (CHGfx) and SD (CHSd) libraries
  stay as separate layers underneath it.
- **One update.** A bug fix or a feature in any layer reaches everyone with
  the next board package release: core, libraries, bootloader and examples
  move together and are tested together.
- **One place for the PC side.** The tools that talk to the device outside
  Arduino (simulator, uploader, serial and screenshot tools, `.CHG` packager,
  SD card builder) live here too, not in separate repositories.

### Where that stands today

Every piece is in this repository and works from a clone. What is not done
yet is the packaging that makes the Boards Manager deliver all of it:

| Piece | In this repository | Delivered by the board package today |
|---|---|---|
| Core, variant, toolchain, `chgame-upload` | `platform/board/` (0.2.4) | yes (0.2.4, from the old release URL) |
| Bootloader with the SD game menu | `platform/bootloader/` | no: 0.2.4 ships the earlier bootloader without the menu |
| The CHGame library (`CHGame.h`: buttons, pacing, palette, drawing, sound, saving, debug protocol) | `platform/board/arduino/CHGame/libraries/CHGame/`; every game is built on it | not yet: it is in the package folder here (`libraries/`), for the next release; games build against it with `--library` |
| CHGfx, the graphics library | `platform/board/arduino/CHGame/libraries/CHGfx/` (1.3.0) | not yet: it is in the package folder here (`libraries/`), for the next release; games build against it with `--library` |
| CHSd, the SD/FAT reader | `platform/board/arduino/CHGame/libraries/CHSd/` (1.0.0) | not yet: it is in the package folder here (`libraries/`), for the next release; games build against it with `--library` |
| The casino games and CHSDtoUSB as examples | `platform/board/arduino/CHGame/libraries/CHGame/examples/games/`, `apps/` | not yet: they are the library's examples here, for the next release |
| PC tools | `tools/`, `platform/bootloader/host/` | `chgame-upload` only |

[docs/roadmap.md](docs/roadmap.md) lists what the first release from this
repository has to do to close that table.
[docs/chgame-library.md](docs/chgame-library.md) records why the library
is as it is, and [docs/unification.md](docs/unification.md) how the
games' twenty copies of their shared code became it.

## Installing

**The board package** (the toolchain and the uploader come with it):

```bash
arduino-cli config add board_manager.additional_urls https://github.com/bateske/CHGame/releases/latest/download/package_chgame_index.json
arduino-cli core update-index
arduino-cli core install CHGame:ch32v
```

(Until 0.3.0, the first release cut from this repository, is published,
0.2.4 is still served from
`https://github.com/bateske/CH32SerialBoot/releases/latest/download/package_chgame_index.json`.)

In the Arduino IDE 2.x: add the same URL under *File > Preferences >
Additional boards manager URLs*, then install **CHGame** from the Boards
Manager.

**This repository.** Clone or download it. The games, libraries and tools
are used from here:

- With the repository's own scripts, nothing more is needed: each game's
  `tools/device.py` builds against `platform/board/arduino/CHGame/libraries/CHGfx`.
- With the Arduino IDE, copy `platform/board/arduino/CHGame/libraries/CHGfx` into your
  sketchbook's `libraries/` folder, open `platform/board/arduino/CHGame/libraries/CHGame/examples/games/<Name>/<Name>.ino`, and set
  *Tools > Optimize* to **Smallest + LTO** and *Tools > USB* to **Upload
  only**.

**The menu bootloader** is installed over USB, through the bootloader a
board already has: no driver, no buttons. From the next board package
release that is *Tools > Programmer* **CHGame USB**, then *Tools > Burn
Bootloader* (*Tools > Bootloader* chooses between the SD game menu, no menu
and the 0.2.4 one). Until then:
`chgame uploader selfupdate platform/bootloader/release/chgame_sdboot.bin`
([platform/bootloader](platform/bootloader/README.md#installing-it-on-a-board)).
The WCH driver and the BOOT button are only for recovery.

## The games

Twenty casino and table games with one look: green felt, gold lettering,
casino chips and a dealer. They are the platform's examples and its test
load: most are within 1 KB of filling the flash. They all fit on one SD card
behind the **game menu built into the bootloader**: switch on, pick a game,
play, with no PC, like an Arduboy FX ([docs/sd-menu.md](docs/sd-menu.md)).

Each game is a standalone sketch in `platform/board/arduino/CHGame/libraries/CHGame/examples/games/<Name>/<Name>.ino` with its own
README (rules, controls, design) and NOTES.md (status, design decisions,
open items). The image column is the release build size, against the
**50,944 B** the bootloader leaves for a sketch.

| Game | What it is | Image |
|---|---|---|
| [CHBackgammon](platform/board/arduino/CHGame/libraries/CHGame/examples/games/CHBackgammon) | Backgammon on felt with chip checkers, a trained CPU, optional match play and doubling cube | 49,524 B |
| [CHBingo](platform/board/arduino/CHGame/libraries/CHGame/examples/games/CHBingo) | 75-ball bingo: up to nine cards against a hall of rivals, power-ups and a jackpot | 36,724 B |
| [CHBlackjack](platform/board/arduino/CHGame/libraries/CHGame/examples/games/CHBlackjack) | Press Play On Tape's Arduboy Blackjack rebuilt in colour: the series' first table | 45,812 B |
| [CHBoardwalk](platform/board/arduino/CHGame/libraries/CHGame/examples/games/CHBoardwalk) | BOARDWALK, a property-trading board game on an isometric board, with tap auctions | 49,856 B |
| [CHCheckers](platform/board/arduino/CHGame/libraries/CHGame/examples/games/CHCheckers) | Checkers on CHChess's isometric board, with its own engine and chip pieces | 42,024 B |
| [CHChess](platform/board/arduino/CHGame/libraries/CHGame/examples/games/CHChess) | Isometric chess with a pointing glove, whip-zoom camera and a CPU of three strengths | 48,884 B |
| [CHCraps](platform/board/arduino/CHGame/libraries/CHGame/examples/games/CHCraps) | Casino craps with 3D dice and Blackjack's dealer as the stickman | 50,032 B |
| [CHCrossword](platform/board/arduino/CHGame/libraries/CHGame/examples/games/CHCrossword) | 13x13 crosswords, built in and as packs on the SD card | 50,300 B |
| [CHDominoes](platform/board/arduino/CHGame/libraries/CHGame/examples/games/CHDominoes) | Dominoes (ALL FIVES and DRAW) with bevelled tiles and a close-up camera | 42,356 B |
| [CHFour](platform/board/arduino/CHGame/libraries/CHGame/examples/games/CHFour) | FOUR IN A ROW, against the dealer as a friendly coach | 36,332 B |
| [CHMahjong](platform/board/arduino/CHGame/libraries/CHGame/examples/games/CHMahjong) | Mahjong solitaire with the 144 traditional tiles and a close-up view | 48,364 B |
| [CHPoker](platform/board/arduino/CHGame/libraries/CHGame/examples/games/CHPoker) | Poker against three CPU players: Hold'em, Five Card Draw, Omaha and Seven Card Stud | 48,908 B |
| [CHRoulette](platform/board/arduino/CHGame/libraries/CHGame/examples/games/CHRoulette) | Roulette with a physically simulated ball and the dealer as croupier | 49,796 B |
| [CHSlots](platform/board/arduino/CHGame/libraries/CHGame/examples/games/CHSlots) | Three slot machines on one purse: LUCKY 7, SWEET and DRAGON FORTUNE | 47,112 B |
| [CHSnakes](platform/board/arduino/CHGame/libraries/CHGame/examples/games/CHSnakes) | SNAKES & LADDERS with procedural snakes, CLASSIC and ARCADE rules | 37,336 B |
| [CHSolitaire](platform/board/arduino/CHGame/libraries/CHGame/examples/games/CHSolitaire) | Klondike, after the Windows original | 31,144 B |
| [CHTicTacToe](platform/board/arduino/CHGame/libraries/CHGame/examples/games/CHTicTacToe) | TIC TAC TOE: ROYALE, sixteen tables on 3x3 and 5x5 boards, for money | 50,308 B |
| [CHWords](platform/board/arduino/CHGame/libraries/CHGame/examples/games/CHWords) | A crossword tile game (Scrabble rules) with a flash dictionary and a full one on SD | 50,396 B |
| [CHWordWheel](platform/board/arduino/CHGame/libraries/CHGame/examples/games/CHWordWheel) | WORD WHEEL, a word-puzzle game show: spin, call letters, solve | 50,312 B |
| [CHYacht](platform/board/arduino/CHGame/libraries/CHGame/examples/games/CHYacht) | YACHT DICE (five dice, thirteen boxes) with Craps's 3D dice | 43,732 B |

[docs/status.md](docs/status.md) lists what each game has been verified on
(the simulator or the device), its open items and the known issues.

## Repository map

```
CHGame/
├── CLAUDE.md          start here: commands, rules, limits, gotchas
├── platform/          the platform itself; these are the master copies
│   ├── board/           the Arduino board package (core, variant, linker scripts) + the board's docs
│   ├── bootloader/      the bootloader with the SD game menu: sources, PC test suite, binaries,
│   │                    and the uploader's source (host/go)
│   │   └── arduino/CHGame/libraries/  CHGame (CHGame.h), CHGfx (graphics), CHSd (SD/FAT), beside SPI, Wire, EEPROM
│   │       └── CHGame/examples/   Hello, games/ (the 20 casino games), apps/ (CHSDtoUSB)
│   └── hardware/        Rev 0 schematic and netlist
├── tools/             the PC tools shared by every game (device.py, the simulator and script
│                      driver, sound preview, size report, serial, chgpack.py for game
│                      packages, sdcard/mkcard.py for the whole card)
└── docs/              platform knowledge: hardware, performance, SD card, how a game is built,
                       status, the roadmap to the first release, the CHGame library's decisions
                       and history, and a getting-started guide for Arduboy developers
```

## Quick start for development

You need `arduino-cli` (or the Arduino IDE 2.x), Python 3.9+ and, for the
simulator and host tests, a C++ compiler. zig is the easiest; it comes with
pip.

```bash
# 1. The board package: see "Installing" above

# 2. Python tools and a compiler for the simulator
pip install -r tools/requirements.txt ziglang

# 3. Build a game (from its folder) against this repository's libraries
cd platform/board/arduino/CHGame/libraries/CHGame/examples/games/CHFour
chgame build              # release build + size report
chgame check --no-device         # host tests + every sim script, twice (games that have check.py)
chgame sim # just the PC simulator
chgame run tools/scripts/endings.txt out/endings   # screenshots in out/endings

# 4. On a board (plugged in by USB)
chgame upload

# 5. A card for the game menu: builds and packs every game into out/sdcard/
cd ../..
python tools/sdcard/mkcard.py             # copy out/sdcard/* to a FAT32 card
```

## The parts

### The board package: `platform/board/`

The Arduino core for the board: package `CHGame`, architecture `ch32v`,
version **0.2.4**. It is a fork of the WCH CH32 Arduino core. It adds the
CHGame variant (pin names such as `PIN_BTN_A` and `PIN_SD_CS`), the USB CDC
serial port, the app linker script (the sketch starts at 0x3000, above the
12 KB bootloader), and the `chgame-upload` tool, which uploads over USB in
about half a second with no button presses. This folder is its master copy;
releases of the board package are cut from here.

Its Tools menus matter for every game:

| Menu (FQBN key) | Games use | What it does |
|---|---|---|
| Optimize (`opt`) | `oslto` | `-Os -flto`. Usually 1-5 KB smaller than plain `-Os`; several games only fit with it. |
| Peripherals (`periph`) | `game` (default) | Compiles out Serial1, `tone()`, PWM and HardwareTimer: about 4 KB. |
| USB (`usb`) | `uploadonly` for release | Drops `Serial` (about 0.7 KB). Upload still works with no button presses. Debug builds keep `serial`. |
| C library (`rtlib`) | `nano` (default) | newlib-nano |

Release FQBN: `CHGame:ch32v:CHGame:opt=oslto,rtlib=nano,periph=game,usb=uploadonly`.

### The CHGame library: `platform/board/arduino/CHGame/libraries/CHGame/`

`#include <CHGame.h>` is the one include of a CHGame sketch. On top of
CHGfx it gives:
- `arduboy`: buttons (`pollButtons()`, `pressed`, `justPressed`,
  auto-repeat), frame pacing (`nextFrame()`, lockstep for the simulator),
  and the START-held-3-s exit to the game menu;
- the house palette with fades, flashes and cycling colours; panels,
  sprites, dithers and the 3x5 font; outlined, shadowed lettering; easing,
  integer sine and screen shake; number formatting;
- one sound engine for effects and music on the piezo, and the status LED;
- saving in two flash pages past the end of the image (there is no EEPROM);
- the serial debug protocol for screenshots, injected input and lockstep
  frames: how the simulator and the script driver run a game;
- `RAMFUNC`, which puts hot code in SRAM.

It was built from the code the twenty games carried copies of, and every
game is now built on it ([docs/unification.md](docs/unification.md)). Its
[README](platform/board/arduino/CHGame/libraries/CHGame/README.md) is the reference, and
`examples/Hello` the smallest complete sketch.

### CHGfx: `platform/board/arduino/CHGame/libraries/CHGfx/`

The graphics library, version **1.3.0**. A full 16-bit framebuffer would not
fit in 20 KB of RAM. CHGfx keeps a **4-bit indexed framebuffer** (8 KB, a
16-colour palette that can change every frame), converts it to the panel's
format in chunks, and streams it out by DMA at 24 MHz while the game draws
the next frame. It provides the drawing primitives, sprites (`sprite4`),
fonts, text effects, palette effects and partial updates. It also owns the
SPI bus that the SD card shares.
[docs/performance.md](docs/performance.md) explains the design and its
measured limits.

### CHSd: `platform/board/arduino/CHGame/libraries/CHSd/`

A small read-only SD library: a polled SPI block driver plus a FAT16/FAT32
reader, about 1.7 KB of flash and 24 B of RAM. CHWords, CHCrossword and
CHWordWheel use it to read their dictionary, puzzle packs and phrase bank
from the card. The games include it as a library (`<Fat.h>`, `<SdSpi.h>`); the
simulator swaps its SPI driver for a pretend card (`$CHSD_CARD`). CHSDtoUSB has its own faster, read-write SD driver, which
is GPL-3.0 and stays inside that sketch.

### The bootloader and the SD game menu: `platform/bootloader/`

The board's permanent bootloader (12 KB at 0x0000), with the game menu:
- the menu appears at every power-on and lists `GAMES/*.CHG` from a
  FAT16/FAT32 card;
- the installed game is preselected, and starting it writes nothing;
- holding START for 3 s in any game goes back to the menu;
- another game is checked completely before anything is erased;
- USB uploading, recovery and the memory map are those of board package
  0.2.4.

It has its own PC test suite, which runs the real C code against models of
the flash, SD card and panel, including a power cut at every flash
operation of an install. Its README covers building, testing and installing
it; [docs/sd-menu.md](docs/sd-menu.md) is the players' guide and
[docs/chg-format.md](docs/chg-format.md) the developers' one-pager.

### The PC tools: `tools/`

The tools for working with the system outside the Arduino IDE:
- **`device.py`**: builds, uploads and drives any sketch on the board (each
  `chgame` command runs it on the game it is started in);
- the **PC simulator** (`tools/chsim`): it compiles a sketch's real code
  with CHGfx's and the library's for the PC, runs it deterministically, and
  produces screenshots and GIFs; its **script driver** (`chdrivelib.py`,
  which each game's `chdrive.py` extends with its own commands) runs the
  same scripts in the simulator and on the board;
- the **sound preview** (`audio/preview.py`): renders a game's effects and
  songs to WAV from the real engine;
- the flash/RAM **size report** (`check_size.py`);
- the USB **serial** helper (`serialcap.py`);
- the **game package** tool (`chgpack.py`): wraps any sketch's `.bin` as a
  `.CHG` for the SD menu, checks packages, lists a card;
- the **card builder** (`sdcard/mkcard.py`): builds every game and lays out
  a whole card;
- the **uploader**: `chgame upload` and `chgame uploader ...` go through the
  Python one (`platform/bootloader/host/py`, the package `chgame_upload`);
  `platform/bootloader/host/go` is the same tool in Go, `chgame-upload`, the
  executable the board package installs for Windows, Linux and macOS. The
  two share their test vectors;
- the **release scripts** (`tools/release/`): the uploader for five hosts,
  the platform archive and the Boards Manager index, published with `gh`
  ([platform/board/docs/building.md](platform/board/docs/building.md)).

What is a game's own stays with it: its script commands (`chdrive.py`),
its description for the shared checks (`game.py`), the tests and the asset
pipeline. [tools/README.md](tools/README.md) classifies every tool in
the repository.

## Licences

Each folder carries its own licence:

| Path | Licence |
|---|---|
| `platform/board/arduino/CHGame/libraries/CHGame/examples/games/*` | Apache-2.0 (see each game's `LICENSE` and `NOTICE`). CHChess's engine `src/engine/ch2k.hpp` is MPL-2.0. |
| `tools/` | Apache-2.0 (`tools/LICENSE`, `tools/NOTICE`) |
| `platform/board/` | MIT (`platform/board/LICENSE`, `THIRD-PARTY.md`) |
| `platform/bootloader/` | MIT (`LICENSE`, `THIRD-PARTY.md`, `NOTICE`: its 5x7 font is Adafruit glcdfont, BSD); `host/` (the uploader, Go and Python) with it, `go.bug.st/serial` BSD-3-Clause in `THIRD-PARTY.md` |
| `platform/board/arduino/CHGame/libraries/CHGame/` | Apache-2.0 (`LICENSE`, `NOTICE`: the 3x5 font is Press Play On Tape's, by way of CHBlackjack) |
| `platform/board/arduino/CHGame/libraries/CHGfx/` | MIT; some fonts carry their own notices (in its `LICENSE`, e.g. the 3x5 font is Apache-2.0) |
| `platform/board/arduino/CHGame/libraries/CHSd/` | MIT |
| `platform/board/arduino/CHGame/libraries/CHGame/examples/apps/CHSDtoUSB/` | GPL-3.0 (its SD layer comes from sdfatlib) |
| `platform/hardware/` | No licence stated yet (schematic and netlist) |
| `docs/`, root files | Apache-2.0 (`LICENSE`, `NOTICE`) |

## History

The pieces were developed in separate repositories and brought together
here on 2026-10-01, without their histories:

- the board package and bootloader from CH32SerialBoot `v0.2.4`;
- CHGfx at `1.3.0`;
- each game from the head of its own repository, and CHSDtoUSB from its own
  (the commits are listed in [docs/status.md](docs/status.md));
- CHSd 1.0.0, which never had a repository of its own.

The collection was first assembled under the working name CHCasino (the
name went from the code and comments on 2026-10-02). Those repositories are
frozen. All development continues here.
