# CHGame: guide for agents

The one repository for the CHGame handheld: the Arduino board package, the
bootloader with the SD game menu (`platform/bootloader`), the graphics and
SD libraries, twenty casino games that are the CHGame library's examples
(`platform/board/arduino/CHGame/libraries/CHGame/examples/games/`), and the
PC tools. It is the source of truth: the repositories the pieces came from
(CH32SerialBoot, CHGfx, one per game) are frozen and are not synced with.
The aim is one board package that delivers all of it, with one `CHGame.h`
library. The library exists (`platform/board/arduino/CHGame/libraries/CHGame`, its
[README](platform/board/arduino/CHGame/libraries/CHGame/README.md)) and every game is built on
it. It sits with CHGfx and CHSd in the board package's `libraries/`
folder, so the first release from this repository delivers them with the core.
[docs/roadmap.md](docs/roadmap.md) says what is done and what is not,
[docs/chgame-library.md](docs/chgame-library.md) why the library is as it
is, and [docs/unification.md](docs/unification.md) what changed when the
games moved onto it.

Read [README.md](README.md) for the overview. This file is the working
manual: setup, commands, limits, rules and gotchas. Each game also has a
`NOTES.md` with its design decisions and open items. Read it before
changing that game.

## Rules

1. **Simulator first.** Everything except timing and sound can be checked on
   the PC. The real board may be in someone's hands; see "The device" below.
2. **Pixels are the test.** The simulator is deterministic. A change that
   should not alter the picture must give identical frames. Run the game's
   scripts before and after and compare (`chgame check --compare A B`, or
   hash the PNG/GIF frames). A change that does alter the picture must
   re-record the game's README GIF (`chgame gif`).
   Each game's README has one GIF, `docs/gameplay.gif`, of at most 1 MB,
   and one format: [docs/game-readme.md](docs/game-readme.md).
3. **Measure size after every change.** `chgame build`
   prints flash and RAM. Most games are within 1 KB of full (see Limits).
4. **Generated files are not edited by hand:**
   - `src/assets/Assets.*` comes from `tools/assets.py` and `tools/art/`, plus
     the shared `tools/art/common/` at the repository root (the dealer and his
     faces, the glove, the display font, the card art, the chips, the
     end-screen lettering: `tools/artlib.py` looks in the game's folder
     first). The three `make_music.py` use `tools/music/composer.py`, the font
     tools `tools/fonts/`, the mock-ups `tools/pixkit.py`.
   - Several games generate other tables, e.g. CHWords `src/dict/DictData.*`,
     CHWordWheel `src/bank/BankData.*`, CHCrossword `src/game/PuzzleData.*`,
     CHSlots `src/game/Strips.h`, CHMahjong `src/game/Layouts.cpp`. The header
     of each says what makes it.
   - Nothing of CHSd is copied any more: the three SD games include
     `<Fat.h>` / `<SdSpi.h>` from the library. After changing CHSd, run its
     `tests/run_tests.py` and `chgame check` in the three games.
5. **The shared `tools/` serve all 20 games.** After changing anything in
   `tools/chsim` or `tools/*.py`, run `chgame check` in several games and
   compare sim frames against a run from before the change.
6. **`platform/` holds the master copies** of the board package, the CHGame
   library, CHGfx, CHSd and the bootloader. Changes are made here, not sent anywhere else. Every
   game builds on them, so a change needs all 20 games rebuilt (size) and
   their sim frames compared; record it in
   [platform/README.md](platform/README.md) (the bootloader's README lists
   its own). Two things to know:
   - `platform/board` is what the *next* board package release will contain.
     Builds use the installed package (0.2.4) for the core, so an edit to
     the core, variant or `boards.txt` has no effect on a build until it is
     released or the installed copy is patched.
   - The three libraries in `platform/board/arduino/CHGame/libraries/` are
     the exception: `tools/device.py`, `tools/sdcard/mkcard.py` and the
     simulator pass them explicitly, so an edit there takes effect at once.
   - `platform/bootloader/src/sd.c` and `src/fat.c` are a C fork of CHSd: a
     fix to one belongs in the other too.
7. **Credits stay exactly as each game's `NOTICE` and README give them.** Do
   not add names from upstream projects' credit lists.
8. **Every game needs its own save magic, debug handshake id and
   `config.h` prefix.** All games share the same two flash save pages. The
   last collisions were fixed on 2026-10-01 (docs/status.md); check a new
   game's values against every other game's.

## Setup

**Linux, macOS or a cloud container:**

```bash
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | BINDIR=$HOME/.local/bin sh
arduino-cli config init --overwrite
arduino-cli config add board_manager.additional_urls https://github.com/bateske/CHGame/releases/latest/download/package_chgame_index.json
arduino-cli core update-index && arduino-cli core install CHGame:ch32v
pip install -e .[sim]      # the tools (Pillow, pyserial) and the `chgame` command; zig is the simulator's compiler
```

**Windows:** the same `arduino-cli` commands (or the Arduino IDE's Boards
Manager), then `pip install -e .[sim]` in the repository root.

**Notes:**
- **The Boards Manager URL** above is this repository's. Until 0.3.0, the
  first release cut from here, is published, 0.2.4 is still served from
  `https://github.com/bateske/CH32SerialBoot/releases/latest/download/package_chgame_index.json`
  (use that URL and `CHGame:ch32v@0.2.4` meanwhile). The URL is given here,
  in the README and in `platform/README.md`: change the three together.
- The board package brings its own RISC-V GCC 8.2 and the `chgame-upload`
  tool, so nothing else is needed for device builds.
- **Linux:** the installed core 0.2.4's `ch32yyxx.h` includes
  `core_riscv_cH32yyxx.h` with a capital H, which only resolves on
  case-insensitive file systems. It is fixed in `platform/board` (ships with
  0.3.0); for 0.2.4:
  `ln -s core_riscv_ch32yyxx.h ~/.arduino15/packages/CHGame/hardware/ch32v/0.2.4/cores/arduino/ch32/lib/core_riscv_cH32yyxx.h`.
- **The libraries need no install.** `chgame build` compiles with
  `--library` for CHGfx, CHGame and CHSd from
  `platform/board/arduino/CHGame/libraries/`, and the simulator uses the same
  copies. With plain `arduino-cli compile`, add those `--library` flags
  yourself, until a board package that bundles them is installed.
- **The simulator's compiler:** `$CHSIM_CXX` (for example `"zig c++"` or a
  full path plus ` c++`), otherwise zig on the PATH, otherwise
  `python -m ziglang`, otherwise clang++ or g++.

## Commands

The games are the CHGame library's examples:
`platform/board/arduino/CHGame/libraries/CHGame/examples/games/<Name>/`
(apps, such as CHSDtoUSB, are beside them in `examples/apps/`). Run these
from a game's folder (or any folder below it): `chgame` finds the sketch by
itself. From anywhere else it takes a game or app by name or folder
(`chgame --sketch CHFour build`). `pip install -e .[sim]` in the repository
root makes the `chgame` command (one environment for every tool); without
it, `python tools/chgame.py` is the same thing. The shared tools under
`tools/` also run on their own (`python tools/readme_gif.py CHFour`,
`python tools/chsim/chsim.py build CHFour`):

| What | Command |
|---|---|
| Release build + size | `chgame build` |
| Debug build (serial debug protocol on) | `chgame build --debug` |
| Upload release / debug | `chgame upload [--debug]` |
| Everything checkable without a board | `chgame check` (9 games have one; `--quick`, `--no-device`) |
| Host unit tests | `chgame test` |
| Build the simulator | `chgame sim` |
| Run a script in the simulator | `chgame run tools/scripts/<s>.txt out/<s>` |
| The same script on the board | `chgame run --device tools/scripts/<s>.txt out/<s>` (debug build + upload) |
| Screenshot of a running debug build | `chgame shot out/shot.png` |
| Sound effects (and songs) to WAV | `chgame audio out/audio` (prints a hash per effect) |
| Regenerate art | `python tools/assets.py` |
| What fills the flash | `chgame size --top 30` |
| Record the README's GIF (`tools/scripts/gameplay.txt` to `docs/gameplay.gif`, at most 1 MB) | `chgame gif` (`--check` from the root checks all 20) |
| Redraw check (5 games) | `chgame redraw <script> <outdir> [ticks]` |
| Memory check (valgrind) | see `tools/chsim/chsim.py`'s docstring (`CHSIM_FLAGS`, `CHSIM_WRAP`) |
| Any sketch (from the root) | `chgame --sketch <dir> build`, `chgame --sketch <dir> run <script> <out>` |

**The bootloader and the SD card** (from the repository root):

| What | Command |
|---|---|
| Build the bootloader (+ size report) | `platform/bootloader/build.sh [release\|locked\|nomenu\|app] [--theme=rainbow\|plain\|casino]` |
| Its PC test suite (flash/SD/panel models, power cuts, menu frames) | `python3 platform/bootloader/test/native/run_tests.py` |
| Refresh the committed binaries | `platform/bootloader/tools/dist.sh` |
| Build and pack every game into `out/sdcard/` (+ FAT32 image) | `python tools/sdcard/mkcard.py [--image out/sdcard.img]` |
| Package one sketch / check packages / list a card | `python tools/chgpack.py pack\|verify\|info` |
| Install the menu bootloader on a board | `platform/bootloader/HARDWARE.md` (self-update over USB) |
| Build the uploader, `chgame-upload` (Go, five hosts, into `out/chgame-upload/`) | `python tools/release/build_uploader.py` |
| The uploaders' parity tests (Python and Go against one vector file) | `python -m unittest discover -s platform/bootloader/test/protocol`; `go test ./...` in `host/go` |
| A release, dry or real (`platform/board/docs/building.md`) | `python tools/release/release.py [--dry-run]` |

The release FQBN is
`CHGame:ch32v:CHGame:opt=oslto,rtlib=nano,periph=game,usb=uploadonly`. A debug
build drops `usb=uploadonly` and adds
`--build-property build.extra_flags=-DCHGAME_DEBUG=1` (the library's switch;
a game's `config.h` derives its own, such as `<PFX>_LEAN`, from it). Pass
sketch-level defines only through `build.extra_flags`: the library is
compiled apart and sees nothing else. It is empty on this platform. Never
override `compiler.cpp.extra_flags`.

## Limits

| | |
|---|---|
| Flash for the image | **50,944 B** (0x3000-0xF6FF). The bootloader takes 12 KB (the menu build uses 12,032 B of it, `platform/bootloader/SIZES.md`), and one page of metadata sits at 0xF700. |
| Save pages | Two 256 B pages at the top of the app region. Keep the image ≤ **50,432 B** for both (A/B with CRC), ≤ 50,688 B for one. Past that, saving switches itself off. |
| Static RAM | **18,416 B**: 20 KB less the 16 B boot block and the 2 KB stack. Under ~900 B free, Arduino warns. |
| Stack | 2 KB (games report the high-water mark with the debug `P` command) |
| CPU | 48 MHz, no PLL. Flash has 3 wait states and no cache: code runs at ~5 cycles per instruction from flash vs ~2 from SRAM. |
| Display | 128x128 ST7735S on SPI1 at 24 MHz. CHGfx's 4-bit framebuffer is 8 KB. A full async flush costs ~5 ms of CPU. |

**Tactics that pay:**
- `opt=oslto`.
- `RAMFUNC(name)` (the library's `chgame/RamFunc.h`; names must be unique
  within a sketch) for per-pixel loops. Every RAMFUNC also costs RAM.
- `#pragma GCC optimize("Os")`.
- Word-sized loop counters.
- Drawing static layers once instead of every frame.
- Avoid newlib's `memmove`: it is a byte loop in flash.
- See [docs/platform.md](docs/platform.md) and
  [docs/performance.md](docs/performance.md).

## The simulator (`tools/chsim`)

The one simulator: the games, CHGfx's examples and CHGfx's own tests all
run on it (`chgame sim`, `chgame sim --free`, `chgame --sketch CHGfx test`;
`python tools/chsim/chsim.py build|run|test` without the entry point).
`chsim.py build <sketch>` compiles the sketch's `.ino` and `src/` plus
CHGfx's portable code and, when the sketch includes it, the CHGame library.
`host/chgfx_host.cpp` stands in for the SPI/DMA part with a model of the
panel (the wire rate and setup the board measured, scaled by the SPI
divider; rows converted two 512 B chunks ahead of the DMA as on the board;
each row landing on a simulated panel, `sim_panel`, as it converts), and
`host/main.cpp` runs the sketch on virtual time: in lockstep for a sketch on
the CHGame library, or free-running (`--frames N`, with `--input` for the
buttons and the panel's frames to a GIF or PNGs) for anything else.

**How it is driven.** `chdrive.py` talks to the sim, or to a debug build on
the board, over the library's serial debug protocol (`chgame/Debug.h`). The
driver is `tools/chsim/chdrivelib.py`; each game's `tools/chsim/chdrive.py`
extends it with the game's own script commands:

| Command | Does |
|---|---|
| `?` | handshake |
| `S` | screenshot (8 KB framebuffer + palette) |
| `K` | hold buttons |
| `L1` / `L0` | lockstep on / off |
| `N k` | run k frames |
| `P` | perf |
| `B` | reboot into the bootloader |
| `Q` | (sim) time CHGfx's primitives, for `cal`/`perf` estimates |

Anything else goes to the game's hook (`dbg::hook`).

**Scripts** in `tools/scripts/*.txt` are lists of `wait`, `tap`, `hold`,
`snap`, `gif`, `rec` and the like (the header of `chdrivelib.py`, and each
game's `chdrive.py` for its own).

**What a run produces.** Screenshots and GIFs go to the output folder
(screenshots are the framebuffer; `chgame sim --free --gif` shows the panel
instead, torn frames included). A `BUG:` line on stderr, with exit code 3,
means a row landed on the panel with pixels that differ from the frame
that was flushed: the game drew into rows still being sent (the message
names the row and the `gfx_waitRow()` that would make it safe), or wrote
`gfx_chunkScratch()` during a flush.

**Behaviour.** The sim always runs with the debug protocol on and with fixed
work slices instead of timers, so scripted runs repeat exactly: a pass of
`loop()` costs 100 µs of virtual time, a full 12 bpp flush 8,384 µs. Scripts
that use `free` / `freegif` run on wall-clock time and do not repeat.

**Extra host shims.** A game can add its own in `tools/chsim/host/`.

**The pretend SD card.** A sketch that includes CHSd gets the card in
CHSd's `host/` folder: set `CHSD_CARD` to a file (a `.img` is a whole card,
any other file is put on a FAT16 card made for it), or pass `--card <img>`
for CHCrossword. Unset means no card.

## The device

**Uploading.** `chgame-upload` (from the board package) uploads over USB
CDC. It does the 1200-baud touch, flash, verify and restart itself; no
buttons are needed.

**With the menu bootloader** (`platform/bootloader`, see
[docs/sd-menu.md](docs/sd-menu.md)):
- **Power-on** shows the SD game menu with the installed program
  preselected. A starts it.
- **After an upload** the sketch starts directly (RUN reset). It appears in
  the menu as INSTALLED PROGRAM if it is not on the card.
- **Uploads work while the menu is on screen**, and so do `device.py run`
  and the debug protocol.
- **Holding START for 3 s** in any game goes back to the menu (the shared
  core's `pollButtons()`; `arduboy.startExits = false` opts out,
  `arduboy.exitToMenu()` leaves on purpose). The games don't show it; it is
  the platform's gesture. In the simulator the exit prints a line and ends
  the run, so no script should hold START that long by accident.
- **Holding B at power-on** skips the card and the panel: USB mode.

The board is USB VID:PID `16C0:27DD`, and `tools/serialcap.py` /
`device.py` find its port by that.

**The board may be in use.** Someone may be playing it or listening to it,
and other sessions may share it.

**Before a device run:**
- Say that you are about to upload a debug build or run device scripts. A
  debug build can drop music or screens to fit the protocol, and a lockstep
  script freezes the game, so both look like crashes from the outside.
- Check that no other `device.py`, `chgame-upload` or `chdrive.py --device`
  process is using the board.
- Never probe the port with a bare pyserial open: it can hang holding the
  port. `chgame uploader probe` (or `chgame-upload -port <PORT> probe`) is
  the safe check. A crashed
  sketch (the core's HardFault handler spins, which also stops USB) and a
  board busy in its bootloader look the same.

**After a device run:** put the release build back
(`chgame upload`) and say it is ready.

**Recovery:** [platform/board/docs/recovery.md](platform/board/docs/recovery.md)
(hold BOOT across power-on for the factory ISP).

## Putting files on the SD card without removing it

[`platform/board/arduino/CHGame/libraries/CHGame/examples/apps/CHSDtoUSB`](platform/board/arduino/CHGame/libraries/CHGame/examples/apps/CHSDtoUSB) turns the board into a USB card
reader, with its serial port still working beside the drive:

1. Upload it from `platform/board/arduino/CHGame/libraries/CHGame/examples/apps/CHSDtoUSB`:
   `arduino-cli compile -b CHGame:ch32v:CHGame --library ../../platform/board/arduino/CHGame/libraries/CHGfx .`
   then `arduino-cli upload -b CHGame:ch32v:CHGame -p <PORT> .`.
   After it starts, the board enumerates on a new serial port.
2. A removable drive appears whose SCSI vendor is "CHGame" and product "SD
   Card Reader" (`tools/chsd_test.py`'s `find_drive()` finds it on Windows).
3. Copy the files to the card. It must be FAT16 or FAT32: CHSd cannot read
   exFAT. Then eject. Sending any byte to the serial port returns a status
   line (`... CARD <blocks> RW CONNECTED`).
4. Upload the game again (on the new port). This works while the drive is
   mounted, with no buttons. Holding B for 1 s, or START for 3 s, resets the
   board (with the menu bootloader: back to the menu).

**From the menu:** a card built by `tools/sdcard/mkcard.py` has CHSDtoUSB as
the **SD CARD READER** entry. Pick it, copy, eject, then hold B to go back to
the menu (B now resets instead of entering the bootloader).

**What each game reads from the card:**
- CHWords: `WORDS.DIC` in the root.
- CHWordWheel: `PHRASES.BNK` in the root.
- CHCrossword: `CHCW/*.CWD`.

Each is in the game's `sdcard/` folder. See [docs/sd-card.md](docs/sd-card.md).

## Starting a new game

[docs/getting-started.md](docs/getting-started.md) is the guide for
developers coming from the Arduboy, and the library's `examples/Hello` the
smallest complete sketch. For a full game, copy the closest existing one;
every game has `chgame check`; the newest have the most scripts and tests.
Then:
1. Rename the folder, the `.ino`, the `config.h` prefix (`<PFX>_VERSION`,
   `<PFX>_LEAN` ...), the debug hello (`dbg::begin("<ID> " ...)`, and
   `ident=` in `tools/chsim/chdrive.py`) and the save magic
   (`save::magic("....")` in `src/save/Save.cpp`); check them against every
   other game (rule 8).
2. Give it its own sounds (`src/audio/Sounds.cpp`) and save data.
3. Keep the START-held-3-s exit to the menu (the library's) unless the game
   needs a long START hold for itself (`arduboy.startExits = false` in
   `setup()`).
4. Write its README in the one format ([docs/game-readme.md](docs/game-readme.md))
   and record its one GIF with `tools/readme_gif.py`.

## Gotchas

- **SPI is shared.** The default `SS` (PA4) is the LCD's CS; the card's CS is
  PB11 (`PIN_SD_CS`). Touch the SD card only between `gfx_wait()` and the
  next flush. CHSd and CHSDtoUSB hand SPI1 back as CHGfx left it.
- **Arduino macros clash with names:** `sq()`, `map()`, `word()`, `min`/`max`.
- **Line endings are LF everywhere** (`.gitattributes`). On Windows, write
  files with explicit `newline="\n"`/UTF-8 from Python; the default cp1252
  fails on non-ASCII.
- **Git Bash heredocs mangle backslash escapes.** Write code containing
  `\n` with a file-writing tool, not a heredoc.
- **The debug protocol costs flash** (~2 KB with USB Serial). Some games
  have a `<PFX>_LEAN` switch (derived from `CHGAME_DEBUG`) that drops
  saving or screens from device debug builds so they fit. A device debug build is therefore not the whole game. Say so
  if someone will be playing it.
- **Sibling assets:** the art several games share is in `tools/art/common/`
  at the repository root, but four `tools/assets.py` (CHBingo, CHRoulette,
  CHTicTacToe, CHWordWheel) still check their generated arrays against
  `../CHBlackjack`'s and `../CHChess`'s `src/assets/Assets.cpp`, and
  CHRoulette's `logo_preview.py` reads the former. The games must stay side
  by side in `examples/games/`.
- `tools/chsim/build/`, `build/` and `out/` are build output and ignored.
