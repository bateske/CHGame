# CHGame: guide for agents

The one repository for the CHGame handheld: the Arduino board package, the
bootloader with the SD game menu (`platform/bootloader`), the graphics and
SD libraries, twenty casino games that are the CHGame library's examples
(`platform/board/arduino/CHGame/libraries/CHGame/examples/Games/`), and the
PC tools. It is the source of truth: the repositories the pieces came from
(CH32SerialBoot, CHGfx, one per game) are frozen and are not synced with.
The aim is one board package that delivers all of it, with one `CHGame.h`
library. The library exists (`platform/board/arduino/CHGame/libraries/CHGame`, its
[README](platform/board/arduino/CHGame/libraries/CHGame/README.md)) and every game is built on
it. It sits with CHGfx and CHSd in the board package's `libraries/`
folder, so the first release from this repository delivers them with the core.
Games are shared as `.chgame` files: [spec/](spec/README.md) holds the
format, the SD card's layout and conformance fixtures, the contract with the
separate web emulator project, and `tools/chcart` is the reference
implementation.
[docs/roadmap.md](docs/roadmap.md) says what is done and what is not,
[docs/chgame-library.md](docs/chgame-library.md) why the library is as it
is, and [docs/unification.md](docs/unification.md) what changed when the
games moved onto it. The API reference, <https://bateske.github.io/CHGame/>,
is built from the libraries' headers ([docs/api/](docs/api/README.md)).
There are two boards, with different pins: CHGame Rev0 (device `rev0`)
and CHGame Rev1 (`rev1`, which Rev 1.5 boards use too). Every sketch and
bootloader is built for one of them, and a cart carries a binary for each.
[docs/hardware-revisions.md](docs/hardware-revisions.md) covers board
revisions: how boards are named, what keeps a binary off the wrong board,
and how one is added. **The tools always default to the most recent
board** (rule 9).

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
   prints flash and RAM (for the newest board; `chgame check` builds and
   gates every board). Most games are within 1 KB of full (see Limits).
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
   - Every picture the visual menu shows is painted by a Python recipe
     with `tools/artkit` (the house look and the method:
     [docs/cover-art.md](docs/cover-art.md); its title lettering is text art
     in `tools/art/title.txt`, set from Pixel Logo Lab's fonts by
     `python -m artkit.fontscout`). A program's `docs/cart.png` comes from
     its `tools/cart.py` (`chgame boxart`), unless it has a hand-finished
     `tools/art/cart.png` (`chgame boxart --export DIR` / `--import DIR`
     round-trips every program's picture through one folder; docs/visual-menu.md),
     which then wins over the recipe; so does its title screen's
     lettering: `title_lines()` there, packed into `src/assets/` by
     `tools/titleart.py` and drawn in the house gold by the library's
     `titleArt()` (13 games;
     docs/cover-art.md, "The same title on the title screen"). After
     changing a recipe's title, run `chgame boxart` and `tools/assets.py`;
     the casino's covers in
     `tools/sdcard/art/` and its `menu.png` from `tools/sdcard/art/src/*.py`
     (`tools/sdcard/covers.py`); the menu's defaults in `spec/assets/` from
     `tools/art/menu/*.py` (`tools/menuart.py`); the bootloader's
     `src/icons.h` from `platform/bootloader/art/icons/*.png`
     (`tools/icons.py`). Any sprite or picture follows the pixel-art rules in
     [docs/pixel-art.md](docs/pixel-art.md) (`python -m artkit.craft PNG`
     lists orphans and jaggies). Look at them all with `python tools/artsheet.py`;
     the README's galleries (`docs/cover-art.png`, `cover-art-defaults.png`)
     come from `python tools/artsheet.py --gallery`.
   - The brand's pictures in `docs/brand/` (the README's banner, which shows
     the box art, its buttons, caution and XOXO, the API reference's logo) come from
     `python tools/brand/make.py`; the look, palette and rules are
     [docs/brand/README.md](docs/brand/README.md), and the API reference's
     stylesheet `docs/api/extra.css` follows them. After a box art changes,
     remake the banner too.
5. **The shared `tools/` serve all 20 games.** After changing anything in
   `tools/chsim` or `tools/*.py`, run `chgame check` in several games and
   compare sim frames against a run from before the change.
6. **`platform/` holds the master copies** of the board package, the CHGame
   library, CHGfx, CHSd and the bootloader. Changes are made here, not sent anywhere else. Every
   game builds on them, so a change needs all 20 games rebuilt (size) and
   their sim frames compared; record it in
   [platform/README.md](platform/README.md) (the bootloader's README lists
   its own). A change to a library's public API changes its Doxygen comment
   too: every public item of the six libraries is documented in its header
   (the style: [docs/api/README.md](docs/api/README.md)), and
   `doxygen docs/api/Doxyfile` must stay free of warnings. Two things to know:
   - `platform/board` is what the *next* board package release will contain.
     Builds use the installed package for the core (0.3.0, the last
     release, which has Rev0 alone; or a `-local` version when a staged
     build is installed, such as `0.4.0-local` with both boards), so an edit to the core, variant,
     `platform.txt` or `boards.txt` has no effect on a build until it is
     released, staged and installed, or the installed copy is patched. A
     board the installed core lacks cannot be built: `chgame` skips it in
     `check`, `export` and `card`, and says so.
   - The three libraries in `platform/board/arduino/CHGame/libraries/` (CHGfx,
     CHGame and CHSd) are the exception: `chgame build`, `chgame card` and
     the simulator pass them explicitly, so an edit there takes effect at
     once. The Rev 1.5's power section (CHPower, CHUSBHost and their apps)
     is a repository of its own, an add-on beside this one
     (`D:/LocalProjects/CHPower`); the tools build a sketch from it too,
     with the libraries beside it (`tools/paths.py`'s `sketch_libraries()`).
   - `libraries/CHGame/src/chgame/Sizzle.inl` (particles, banners, floats)
     is not compiled in the library but inside each game's `Fx.cpp`,
     under that game's size pragma and `SIZZLE_*` switches (its `Fx.h`).
     A change there is a change to every game's image: rebuild all 20 and
     compare sizes and frames, as for the rest of the library.
   - `platform/bootloader/src/sd.c` and `src/fat.c` are a C fork of CHSd: a
     fix to one belongs in the other too.
   - The bootloader is full: flash 11,952 of 12,288 B on rev0 and 11,944 B
     on rev1 (gate A keeps 256 B spare), and RAM 20,416 of 20,480 B on
     both, since a menu folder lists as many
     entries (240, `MENU_MAX_GAMES`) as RAM allows. Every byte added must be
     paid for (`platform/bootloader/SIZES.md` lists where). Measure with
     `platform/bootloader/build.sh release` and `build.sh --board=rev1 release`.
   - It has two faces from one source: the list menu (`src/menu.c`) and the
     visual menu (`src/visual.c`, `build.sh --ui=visual`: 12,080 B on rev0,
     12,084 B on rev1; its gate keeps
     192 B spare, by the owner's choice, so 16 B and 12 B are left). Both read the card through `src/card.c`: a change
     there needs both built and both suites passed, and the list build's
     binaries should stay byte-identical unless the change is meant for it.
   - A third build, `nomenu` (*USB Only*), is the bootloader for a board
     without an SD card: it drives only the LED and USB. Every build leaves
     the pins it does not use high-Z (`src/hal.h`).
   - Every build is made per board: `build.sh --board=rev0|rev1` (rev1,
     the newest, without it; the pins are in `src/hal.h`, which stops any
     other id).
     `tools/dist.sh` makes both: rev0's binaries where they always were,
     rev1's in `release/rev1/` and the board package's
     `bootloaders/CHGame/rev1/`. A change for one board leaves the other's
     binaries byte-identical unless it is meant for both. On rev1 the
     backlight (PB9) comes on only after the panel has been sent a frame,
     and B held at power-on leaves it dark.
7. **Every game needs its own save magic, debug handshake id and
   `config.h` prefix.** All games share the same two flash save pages. The
   last collisions were fixed on 2026-10-01 (docs/status.md); check a new
   game's values against every other game's.
8. **`spec/` is a contract with another project.** A change to the
   `.chgame` format or the card's layout is made in `spec/`,
   `tools/chcart` (and, for the card, the bootloader's `card.c`, `menu.c`,
   `visual.c` and `shared/chgame_card.h`) together. Then `python tools/chcart/fixtures.py`
   regenerates the fixtures and their expected results; review the diff.
   chcart's tests and the bootloader's PC suite must pass.
   A new board is a new device in chgame.md's table, with a `rev<n>` name
   and a target id (`CX35` for rev0, `CGR<n>` after it), never a name in a
   title. Follow [docs/hardware-revisions.md](docs/hardware-revisions.md)'s
   checklist: the tables in chcart, chgpack, `chg_format.h` and the two
   uploaders must agree, and their tests check that they do.
   **So is the upload protocol.** The web emulator project's browser
   uploader is the fourth implementation of
   [platform/board/docs/protocol.md](platform/board/docs/protocol.md)
   (beside `proto.c`, the Go and the Python hosts) and changes nothing in
   the bootloader: it uses the `CG` frames, `HELLO` (upload mode, bootloader
   version 3 or later, application base 0x3000, the sizes from the answer),
   `BEGIN`/`WRITE`/`END`/`RUN` with `ABORT` on failure, the 1200-baud/DTR
   touch and the USB reconnection, 115200 for ordinary connections, and it
   never flashes bootloaders (older ones get the board package's upgrade
   procedure). Its SD-over-serial sketch is capped at 50,432 B so the save
   pages survive it, and must be built for the board it is sent to (that
   project's build helper builds rev0 alone today: tell the other side). Rev1 bootloaders add `HELLO`'s
   board field (34 bytes, ending `CGR1`); a browser uploader should send a
   cart's `rev1` binary only to a board that names `CGR1`
   ([spec/README.md](spec/README.md), "what rev1 changes"). A change to the frame, the command set, `HELLO`'s
   payload, `BOOT_VERSION`'s meaning, `shared/chgame_usb_identity.h` or the
   core's 1200-baud touch is a change to that contract: make it in
   protocol.md ("Host conventions") and the vectors
   (`python -m chgame_upload.vectors --write`) too, and tell the other side.
9. **The tools always default to the most recent board** (the owner's
   rule). `chgame build`, `upload`, `run --device` and `size` take the
   newest board the installed core has (rev1 with 0.4.0) unless `--board`
   or `$CHGAME_BOARD` names another; `check`, `export` and `card` take
   every board it has. When a board is added it becomes the default by
   itself (`tools/device.py`'s `default_board()` takes the highest
   `rev<n>` the core knows), and anything new that takes a board defaults
   the same way: the bootloader's `build.sh` (rev1 without `--board`;
   `tools/dist.sh` names both boards) and `chgame cart
   prepare|flash|deploy` (chcart itself still defaults to `rev0` when run
   on its own, as the format's reference tool).

## Setup

**Linux, macOS or a cloud container:**

```bash
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | BINDIR=$HOME/.local/bin sh
arduino-cli config init --overwrite
arduino-cli config add board_manager.additional_urls https://github.com/bateske/CHGame/releases/latest/download/package_chgame_index.json
arduino-cli core update-index && arduino-cli core install CHGame:ch32v
pip install -e .[sim]      # the tools (Pillow, pyserial, numpy) and the `chgame` command; zig is the simulator's compiler
```

**Windows:** the same `arduino-cli` commands (or the Arduino IDE's Boards
Manager), then `pip install -e .[sim]` in the repository root.

**Notes:**
- **The Boards Manager URL** above is this repository's; 0.3.0
  (2026-10-07) is the first release from here, with every game as one
  cart, `CHGame-Casino-0.3.0.chgame`, and its SD card's zip beside it. The
  URL is given here, in the README and in `platform/README.md`: change the
  three together. To install the next version before it is published:
  `python tools/release/stage.py` builds it as `<version>-local` and tests
  it as a new user, and
  `python tools/release/serve.py` serves it to Boards Manager at
  `http://localhost:8765/package_chgame_index.json`
  ([platform/board/docs/trying-a-release.md](platform/board/docs/trying-a-release.md)).
- **Rev1 needs 0.4.0.** 0.3.0 has the CHGame Rev0 board alone. 0.4.0, not
  yet released, adds CHGame Rev1 (for Rev 1 and Rev 1.5 boards), its
  bootloaders, chgame-upload 0.3.0 and the board checks on Upload and Burn
  Bootloader. To use it before it is published, stage it:
  `python tools/release/stage.py --include-untracked` (while the rev1
  variant and bootloaders are uncommitted: `release.py` packs committed
  files only), `python tools/release/serve.py`, then `arduino-cli core
  update-index` and `arduino-cli core install CHGame:ch32v@0.4.0-local`,
  both with `--additional-urls http://localhost:8765/package_chgame_index.json`.
  A re-stage takes a new `--suffix` (`local2`, ...), since Arduino keeps an
  installed version whose number has not changed. To go back, run `core
  update-index` from the GitHub URL first (both indexes are cached under
  one name), then `core install CHGame:ch32v@0.3.0`
  (trying-a-release.md, "Or in your own arduino-cli"). With 0.3.0
  installed the tools build rev0 alone.
- The board package brings its own RISC-V GCC 8.2 and the `chgame-upload`
  tool, so nothing else is needed for device builds.
- **Linux:** core 0.2.4's `ch32yyxx.h` includes
  `core_riscv_cH32yyxx.h` with a capital H, which only resolves on
  case-insensitive file systems. Fixed in 0.3.0; if 0.2.4 is still
  installed:
  `ln -s core_riscv_ch32yyxx.h ~/.arduino15/packages/CHGame/hardware/ch32v/0.2.4/cores/arduino/ch32/lib/core_riscv_cH32yyxx.h`.
- **The libraries need no install.** `chgame build` compiles with
  `--library` for CHGfx, CHGame and CHSd from
  `platform/board/arduino/CHGame/libraries/`, and the simulator uses the same
  copies. Plain `arduino-cli compile` needs those `--library` flags only
  with a package older than 0.3.0, which bundles the three.
- **The simulator's compiler:** `$CHSIM_CXX` (for example `"zig c++"` or a
  full path plus ` c++`), otherwise zig on the PATH, otherwise
  `python -m ziglang`, otherwise clang++ or g++.

## Commands

The games are the CHGame library's examples:
`platform/board/arduino/CHGame/libraries/CHGame/examples/Games/<Name>/`
(apps, CHStlView, CHSDtoUSB and CHSDtoSerial, are beside them in
`examples/Apps/`). Run these
from a game's folder (or any folder below it): `chgame` finds the sketch by
itself. From anywhere else it takes a game or app by name or folder
(`chgame --sketch CHFour build`). `pip install -e .[sim]` in the repository
root makes the `chgame` command (one environment for every tool); without
it, `python tools/chgame.py` is the same thing. The shared tools under
`tools/` also run on their own (`python tools/readme_gif.py CHFour`,
`python tools/chsim/chsim.py build CHFour`):

| What | Command |
|---|---|
| Release build + size (into `build/<board>/release`) | `chgame build` |
| Debug build (serial debug protocol on; `build/<board>/debug`) | `chgame build --debug` |
| Upload release / debug | `chgame upload [--debug]` |
| Everything checkable without a board | `chgame check` (every game; `--quick`, `--no-device`; what it runs comes from the game's `tools/game.py`; the device build and its size gate for every board the installed core has, the simulator once) |
| Host unit tests | `chgame test` |
| Build the simulator | `chgame sim` |
| Run a script in the simulator | `chgame run tools/scripts/<s>.txt out/<s>` |
| The same script on the board | `chgame run --device tools/scripts/<s>.txt out/<s>` (debug build + upload) |
| Screenshot of a running debug build | `chgame shot out/shot.png` |
| Sound effects (and songs) to WAV | `chgame audio out/audio` (prints a hash per effect) |
| Regenerate art | `python tools/assets.py` |
| What fills the flash (`build/<board>/release` by default) | `chgame size --top 30` |
| Record the README's GIF (`tools/scripts/gameplay.txt` to `docs/gameplay.gif`, at most 1 MB) | `chgame gif` (`--check` from the root checks all 20) |
| Redraw check (5 games) | `chgame redraw <script> <outdir> [ticks]` |
| Memory check (valgrind) | see `tools/chsim/chsim.py`'s docstring (`CHSIM_FLAGS`, `CHSIM_WRAP`) |
| Any sketch (from the root) | `chgame --sketch <dir> build`, `chgame --sketch <dir> run <script> <out>` |
| Another board than the newest | `chgame --board rev0 build`, `chgame --board rev0 --sketch CHFour upload` (or `CHGAME_BOARD=rev0`) |

**The board.** `--board rev0|rev1` is a global option: it goes before the
command (`chgame --board rev0 build`, not `chgame build --board rev0`), and
`$CHGAME_BOARD` does the same. Without it, `build`, `upload`, `run
--device` and `size` take the newest board the installed core has (rule 9),
and `check`, `export` and `card` take every board it has. Builds go to
`build/<board>/release` and `build/<board>/debug`. The simulator has no
board: `run` without `--device`, `sim`, `test`, `gif`, `redraw` and `audio`
are the same for both. `--board` is also the `--device` of `cart
prepare|flash|deploy|backup|new|add|build`, `pack pack` and `uploader
flash|pack` when the command has none of its own, and a binary taken from
`build/<board>/` names its board for `cart new|add`, `pack pack` and
`uploader flash|pack`.

**The bootloader and the SD card** (from the repository root):

| What | Command |
|---|---|
| Build the bootloader (+ size report; into `build/<mode>[-visual][-static][-rev1]/`) | `platform/bootloader/build.sh [release\|locked\|nomenu\|app] [--board=rev0\|rev1] [--ui=list\|visual] [--style=rainbow\|static]` (rev1 without `--board`) |
| Its PC test suite (flash/SD/panel models, power cuts, menu frames; rev1's builds and frames too) | `python3 platform/bootloader/test/native/run_tests.py` |
| Refresh the committed binaries (both boards: rev1's in `release/rev1/` and the package's `bootloaders/CHGame/rev1/`) | `platform/bootloader/tools/dist.sh` |
| The casino cart, `out/CHGame-Casino.chgame` (`tools/sdcard/casino.json`, every installed board's binaries), and a card per board in `out/sdcard-<board>/` (+ FAT32 images, `out/sdcard-<board>.img`) | `chgame card [--no-build] [--image]` (`chgame --board rev0 card`: one board's) |
| A sketch as a `.chgame` (`build/<Name>.chgame`, from its `chgame.json`; a binary per installed board, `<id>/rev0.bin` and `<id>/rev1.bin`) | `chgame export` (in its folder) |
| Carts: inspect, check, combine, edit, prepare a card, flash, deploy, back a card up (its games and their SD files, from the record in each CHG file: spec/card.md) | `chgame cart info\|verify\|new\|add\|remove\|order\|set\|launch\|background\|prepare\|flash\|deploy\|backup` |
| The menu's picture (logo included): the default to edit, any image converted, a preview of the menu on it, onto a card (docs/menu-image.md) | `chgame background --template F`, `chgame background IMAGE [--preview F.gif] [--out F] [--card DRIVE]` |
| chcart's tests (the conformance fixtures included) / remake the fixtures | `python -m unittest discover -s tools/chcart/tests` / `python tools/chcart/fixtures.py` |
| CHG files (the menu's install files): make one, check them, list a card | `chgame pack pack\|verify\|info` |
| Install the menu bootloader on a board | `platform/bootloader/HARDWARE.md` (self-update over USB) |
| The visual menu's pictures: convert any image, preview it, a template, onto a card; into a cart; placeholders for what has none (docs/visual-menu.md) | `chgame picture IMAGE [--preview F.gif] [--out F] [--card DRIVE]`, `chgame picture --template F`; `chgame cart picture\|art` |
| A game's box art, `docs/cart.png`, from its `tools/cart.py` (painted with `tools/artkit`: [docs/cover-art.md](docs/cover-art.md)) | `chgame boxart` (in its folder; `--check` from the root checks all 22, `--sheet F` shows them) |
| A picture's previews and the house checks, while painting it / a title's lettering from thousands of pixel fonts (needs Pixel Logo Lab beside the repository, or `$CHG_LOGOLAB`) | `python -m artkit show RECIPE.py` / `python -m artkit.fontscout scout "TITLE" OUT` |
| The casino card's covers (`tools/sdcard/art/`, from `art/src/*.py`) / the menu's default pictures (`spec/assets/`, from `tools/art/menu/*.py`) / its built-in icons (`art/icons/` -> `src/icons.h`) | `python tools/sdcard/covers.py` / `python tools/menuart.py` / `python platform/bootloader/tools/icons.py` |
| Every picture the menus show on one sheet (or before/after for some; or the README's galleries, `docs/cover-art*.png`, after a picture changes) | `python tools/artsheet.py [OUT]` / `python tools/artsheet.py --compare OUT NAME ...` / `python tools/artsheet.py --gallery` |
| The README's banner, buttons, caution and XOXO, and the API reference's logo (`docs/brand/`; one frame of the banner to look at) | `python tools/brand/make.py [banner\|buttons\|warning\|xoxo\|wordmark\|swatches]` / `python tools/brand/make.py banner --still out/banner.png` |
| Build the uploader, `chgame-upload` (Go, five hosts, into `out/chgame-upload/`) | `python tools/release/build_uploader.py` |
| The uploaders' parity tests (Python and Go against one vector file) | `python -m unittest discover -s platform/bootloader/test/protocol`; `go test ./...` in `host/go` |
| Stage a release locally and test it as a new user (fresh arduino-cli in `out/newuser/`, every example compiled from the installed package for each board, the casino cart and an SD card zip per board) | `python tools/release/stage.py [--quick] [--serve] [--include-untracked] [--suffix local2]` |
| Serve the staged release to the Arduino IDE | `python tools/release/serve.py` (URL `http://localhost:8765/package_chgame_index.json`) |
| A release, dry or real (`platform/board/docs/building.md`); first, the README's casino downloads list it (the cart and each board's SD card, newest first: release.py refuses otherwise) | `python tools/release/downloads.py VERSION` (commit it), then `python tools/release/release.py [--dry-run]` |
| The API reference (Doxygen, into `out/api-docs/html`; published to <https://bateske.github.io/CHGame/> by `.github/workflows/docs.yml`) | `mkdir -p out/api-docs && doxygen docs/api/Doxyfile` (or the Docker line in [docs/api/README.md](docs/api/README.md)) |

The release FQBN is
`CHGame:ch32v:<board>:opt=oslto,rtlib=nano,periph=game,usb=uploadonly`,
`<board>` `rev0` or `rev1`: the tools take a game's `tools/game.py` FQBN
(or this one) and swap its board field (`tools/device.py`'s `fqbn()`). The
board package (0.4.0 on) defines `ARDUINO_CHGAME_REV0` or
`ARDUINO_CHGAME_REV1` for every file, and the core and the libraries take
their pins from the board built for (that macro, or the variant's pin
names), so a sketch sets up no pins of its own. A debug
build drops `usb=uploadonly` and adds
`--build-property build.extra_flags=-DCHGAME_DEBUG=1` (the library's switch;
a game's `config.h` derives its own, such as `<PFX>_LEAN`, from it). Pass
sketch-level defines only through `build.extra_flags`: the library is
compiled apart and sees nothing else. It is empty on this platform. Never
override `compiler.cpp.extra_flags`.

## Limits

Rev0 and Rev1 have the same chip and the same memory map
([spec/chgame.md](spec/chgame.md)'s device table), so these hold for both.
A game is size-gated on each board (`chgame check`), since its image
differs a little between them.

| | |
|---|---|
| Flash for the image | **50,944 B** (0x3000-0xF6FF). The bootloader takes 12 KB (the menu builds use up to 12,084 B of it, `platform/bootloader/SIZES.md`), and one page of metadata sits at 0xF700. Its last 32 B, 0xF7E0-0xF7FF, are the **system settings block**: reserved for the platform, none defined yet, kept across installs by bootloader v4 (spec/chgame.md). A sketch never writes the metadata page. |
| Save pages | Two 256 B pages at the top of the app region. Keep the image ≤ **50,432 B** for both (A/B with CRC), ≤ 50,688 B for one. Past that, saving switches itself off. A release build fails when it leaves fewer than the game's `SAVE_PAGES` (`tools/game.py`, two by default). |
| Static RAM | **18,416 B**: 20 KB less the 16 B boot block and the 2 KB stack. Under ~900 B free, Arduino warns. |
| Stack | 2 KB (games report the high-water mark with the debug `P` command) |
| CPU | 48 MHz, no PLL. Flash has 3 wait states and no cache: code runs at ~5 cycles per instruction from flash vs ~2 from SRAM. |
| Display | 128x128 ST7735S on SPI1 at 24 MHz. CHGfx's 4-bit framebuffer is 8 KB. A full async flush costs 2.5-2.9 ms of CPU at 12 bpp (CHGfx's README). |

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
`chsim.py build <sketch>` compiles the sketch's `.ino`, the `.cpp` files
beside it and `src/`, plus
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

**Two boards.** CHGame Rev0 (`rev0`) and CHGame Rev1 (`rev1`) have
different pins, and a Rev 1.5 board is a Rev1: it takes the rev1 build. A
binary for one board drives pins the other uses as buttons, so it must
never run on the other. Know which board is on the bench before a device
run, and pass `--board rev0` for a Rev0 (the default is the newest board).
On Rev1 the LED is PB10 (PB9 on Rev0), PB9 is the backlight, which CHGfx
switches on only once the panel shows a black frame, and the buzzer is a
magnetic one on PA1 that the library leaves low when silent
([docs/platform.md](docs/platform.md) has every pin).

**Uploading.** `chgame-upload` (from the board package) uploads over USB
CDC. It does the 1200-baud touch, flash, verify and restart itself; no
buttons are needed. It is told the board (`-device`: `chgame upload`
passes it, and so does the IDE's Upload from 0.4.0) and refuses a board
whose bootloader names another in `HELLO`. A bootloader image for another
board is refused before anything is written (`selfupdate`, Burn
Bootloader). The factory ISP cannot tell the boards apart: there only the
image is checked against the board selected
([docs/hardware-revisions.md](docs/hardware-revisions.md)).

**A new or repaired board** gets `tools/sketches/CHBoardTest` first
(`chgame --sketch CHBoardTest upload`, with `--board rev0` before
`--sketch` for a Rev0; its README): the buttons, the LED, the backlight,
the buzzer, the SD card, the UART and I2C connectors and a deliberate
fault, and on Rev1 VBUS sense and the test pads. It is a bench sketch: not
in the package, not on the card.

**With the menu bootloader** (`platform/bootloader`, see
[docs/sd-menu.md](docs/sd-menu.md)):
- **Power-on** shows the SD game menu with the installed program
  preselected. A starts it.
- **After an upload** the sketch starts directly (RUN reset). It appears in
  the menu as INSTALLED PROGRAM if it is not on the card.
- **Uploads work while the menu is on screen**, and so do `chgame run
  --device` and the debug protocol.
- **Holding START for 3 s** in any game goes back to the menu (the CHGame
  library's `pollButtons()`; `chgame.startExits = false` opts out,
  `chgame.exitToMenu()` leaves on purpose). The games don't show it; it is
  the platform's gesture. In the simulator the exit prints a line and ends
  the run, so no script should hold START that long by accident.
- **Holding B at power-on** skips the card and the panel: USB mode. On
  Rev1 the screen stays dark in this mode (the backlight is never
  switched on); the LED, PB10, blinks.

The board is USB VID:PID `16C0:27DD` (both boards), and
`tools/serialcap.py` / `chgame` find its port by that. `chgame uploader
probe` names the board a bootloader reports (rev1 sends `CGR1` in `HELLO`;
rev0 sends no board).

**The board may be in use.** Someone may be playing it or listening to it,
and other sessions may share it.

**Before a device run:**
- Say that you are about to upload a debug build or run device scripts. A
  debug build can drop music or screens to fit the protocol, and a lockstep
  script freezes the game, so both look like crashes from the outside.
- Check that no other `chgame upload`, `chgame run --device`,
  `chgame-upload` or `chdrive.py --device` process is using the board.
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

[`platform/board/arduino/CHGame/libraries/CHGame/examples/Apps/CHSDtoUSB`](platform/board/arduino/CHGame/libraries/CHGame/examples/Apps/CHSDtoUSB) turns the board into a USB card
reader, with its serial port still working beside the drive:

1. Upload it: `chgame --sketch CHSDtoUSB upload` (`chgame --board rev0
   --sketch CHSDtoUSB upload` on a Rev0; its `tools/game.py`
   names its options, `opt=osstd` with USB Serial: it is tested on the
   board with `-Os`, not yet with LTO). Or by hand, with the board's
   FQBN (`rev0` or `rev1`):
   `arduino-cli compile -b CHGame:ch32v:rev1:opt=osstd .` then
   `arduino-cli upload -b CHGame:ch32v:rev1:opt=osstd -p <PORT> .`.
   After it starts, the board enumerates on a new serial port.
2. A removable drive appears whose SCSI vendor is "CHGame" and product "SD
   Card Reader" (`tools/chsd_test.py`'s `find_drive()` finds it on Windows).
3. Copy the files to the card. It must be FAT16 or FAT32: CHSd cannot read
   exFAT. Then eject. Sending any byte to the serial port returns a status
   line (`... CARD <blocks> RW CONNECTED`).
4. Upload the game again (on the new port). This works while the drive is
   mounted, with no buttons. Holding B for 1 s, or START for 3 s, resets the
   board (with the menu bootloader: back to the menu).

**From the menu:** the casino card (`chgame card`, `out/sdcard-<board>/`
for each board) has CHSDtoUSB as **SD
CARD READER** in its **APPS** folder (menu v2; the first menu shows no
folders). Pick it, copy, eject, then hold B to go back to the menu (B now
resets instead of entering the bootloader).

**A whole cart at once:** with the drive mounted,
`chgame --board <board> cart deploy <cart>.chgame --card <drive>` writes
the board's games, menu
and data files (`--clean` empties `GAMES/` first) and flashes what the
deploy rules say (spec/card.md). A card is for one board: another board's
menu greys its games and refuses them (ERROR 5).

**What each game reads from the card:**
- CHWords: `WORDS.DIC` in the root.
- CHWordWheel: `PHRASES.BNK` in the root.
- CHCrossword: `CHCW/*.CWD`.
- CHStlView (an app): any `.STL`, in any folder (samples in `sdcard/MODELS`).

Each is in the game's `sdcard/` folder. See [docs/sd-card.md](docs/sd-card.md).

## Starting a new game

[docs/getting-started.md](docs/getting-started.md) is the guide for
developers coming from the Arduboy, and the library's `examples/Hello` the
smallest complete sketch. For a full game, copy the closest existing one;
every game has `chgame check`; the newest have the most scripts and tests.
Nothing in a game is board-specific: the library, CHGfx and CHSd take the
pins from the board it is built for, and `chgame check` and `chgame
export` build it for every board. Then:
1. Rename the folder, the `.ino`, the `config.h` prefix (`<PFX>_VERSION`,
   `<PFX>_LEAN` ...), the debug hello (`dbg::begin("<ID> " ...)`, and
   `IDENT` in `tools/chsim/chdrive.py`) and the save magic
   (`save::magic("....")` in `Save.cpp`); check them against every
   other game (rule 7).
2. Give it its own sounds (`Sounds.cpp`) and save data.
   Its effects are the library's `chgame/Sizzle`: keep in `Fx.h`
   only the `SIZZLE_*` switches it needs (pool size, kinds, banner, floats).
   Its `tools/game.py` tells `chgame test`, `check` and `redraw` what to
   run (the schema is `tools/gamecfg.py`'s docstring; an empty file is
   every default); `tools/chsim/chdrive.py` holds its own script commands.
3. Keep the START-held-3-s exit to the menu (the library's) unless the game
   needs a long START hold for itself (`chgame.startExits = false` in
   `setup()`).
4. Write its README in the one format ([docs/game-readme.md](docs/game-readme.md))
   and record its one GIF with `chgame gif`. Credits go in the README and
   `NOTICE` only, never on screen. Give it its box art for the
   visual menu: a `tools/cart.py` (copy one; `chgame boxart` writes
   `docs/cart.png`) or a hand-drawn `docs/cart.png` (the picture rule:
   [docs/visual-menu.md](docs/visual-menu.md)).
5. Give it a `chgame.json` (title, author, genre, links; everything else
   has a default: chcart/sources.py), check `chgame export`, and add it to
   `tools/sdcard/casino.json` if it belongs on the casino card.

## Gotchas

- **SPI is shared.** The default `SS` (PA4) is the LCD's CS on both boards;
  the card's CS is `PIN_SD_CS`: PB11 on Rev0, PB3 on Rev1, where an OR gate
  holds the card's DI high while it is deselected
  ([docs/hardware-revisions.md](docs/hardware-revisions.md)). Touch the SD card only between `gfx_wait()` and the
  next flush. CHSd and CHSDtoUSB hand SPI1 back as CHGfx left it.
- **An old CHGfx, CHGame or CHSd in the sketchbook's `libraries/`**
  (installed by hand before the package carried them) is used instead of
  the board package's in the Arduino IDE and a plain `arduino-cli
  compile`. Copies from before 0.4.0 know only Rev0's pins, so a Rev1
  build made with them drives the wrong pins. Remove them.
- **Arduino macros clash with names:** `sq()`, `map()`, `word()`, `min`/`max`.
- **Sketches run in user mode** (the startup's `mret` leaves MPP at 0):
  touching `mstatus` outside an interrupt handler is an illegal
  instruction and a crash. Turn interrupts off with `noInterrupts()` or
  QingKe's CSR 0x800 (`gintenr`, what the core's `__disable_irq()` writes).
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
  by side in `examples/Games/`.
- `tools/chsim/build/`, `build/` and `out/` are build output and ignored.
  A `build/release` or `build/debug` folder is left from before the
  boards: the tools now use `build/<board>/`. Likewise `out/sdcard/` is
  no longer written (the cards are `out/sdcard-<board>/`).
