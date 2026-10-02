# platform/

The CHGame platform: the board package, the bootloader, the libraries and
the hardware files. **These are the master copies.** Each piece began in a
repository of its own; those are frozen, and every fix and feature is made
here. The table's "Came from" column is history, not something to sync with.

| Folder | What | Version | Came from | Licence |
|---|---|---|---|---|
| `board/arduino/CHGame/` | The CHGame Arduino board package: core, variant, linker scripts, bootloader binary, `boards.txt` / `platform.txt` | 0.2.4 | CH32SerialBoot tag `v0.2.4` (5de3006), folder `arduino/CHGame` | MIT (`board/LICENSE`, `board/THIRD-PARTY.md`) |
| `board/docs/` | The board's docs: hardware pin map, flash/RAM map, boot flow, upload protocol, recovery, CH32X035 gotchas, building the bootloader | 0.2.4 | same tag, folder `docs` | MIT |
| `board/arduino/CHGame/libraries/CHGame/` | The CHGame library: `CHGame.h`, the one include of a sketch (buttons, pacing, palette, drawing, sound, saving, the debug protocol) | 0.1.0 | built here (2026-10-02) from the code the twenty games shared | Apache-2.0 (`LICENSE`, `NOTICE`) |
| `board/arduino/CHGame/libraries/CHGfx/` | The graphics library | 1.3.0 | CHGfx tag `1.3.0` (838bbb0) | MIT (+ font notices in its `LICENSE`) |
| `board/arduino/CHGame/libraries/CHSd/` | Read-only SD card + FAT16/32 library | 1.0.0 | never had a repository of its own | MIT |
| `bootloader/` | The bootloader with the SD game menu: sources, PC test suite, built binaries, and the uploader's source (`host/go`; `host/py` is the Python reference) | 0.2.4 + the SD menu (BOOT_VERSION 2) | CH32SerialBoot tag `v0.2.4` (5de3006): `bootloader/`, `shared/`, `host/py/`, `test/` | MIT (+ BSD font, `bootloader/NOTICE`) |
| `hardware/` | Rev 0 schematic (PDF) and netlist (EasyEDA `.tel`) | 2026-08-21 | | |

The third-party code inside these (the WCH core and SPL, the USB CDC stack,
fonts) keeps its own notices: `board/THIRD-PARTY.md`,
`bootloader/THIRD-PARTY.md`, `bootloader/vendor/usbcdc/VENDORED.md` and
CHGfx's `LICENSE`.

## Where this is going

The board package is to carry everything: the core, the menu bootloader,
the `CHGame` library (with CHGfx and CHSd under it) and the casino games as
examples, so that installing or updating "CHGame" in the
Boards Manager brings all of it at once.
[../docs/roadmap.md](../docs/roadmap.md) lists the steps. Until they are
done, the pieces are used as described below.

## The board package (`board/`)

**Installing.** Install the board package through the Arduino Boards
Manager. That also installs the RISC-V GCC 8.2 toolchain, `chgame-upload`
and `wchisp`:

```bash
arduino-cli config add board_manager.additional_urls https://github.com/bateske/CHGame/releases/latest/download/package_chgame_index.json
arduino-cli core update-index
arduino-cli core install CHGame:ch32v
```

Until 0.3.0, the first release cut from this repository, is published, 0.2.4
is still served from
`https://github.com/bateske/CH32SerialBoot/releases/latest/download/package_chgame_index.json`
(install `CHGame:ch32v@0.2.4` from there meanwhile).

**What the copy here is:**
- the source of the next release. A change made here does not reach a build
  until a release is installed (or the installed package is patched by
  hand), because arduino-cli compiles against the installed package, not
  this folder;
- the place to read the core, variant and linker script (the pin names are
  in `variants/CH32X035/CHGame/variant_CHGame.h`; the menus and their flags
  in `boards.txt`);
- today, byte-for-byte what 0.2.4 installs, so it is also the reference for
  exactly what the games were built with.

**Gaps:**
- The board docs sometimes refer to `bootloader/`, `host/` or `tools/`
  paths as they were in CH32SerialBoot. `bootloader/` and `host/py` are now
  under [bootloader/](bootloader). The release scripts they mention
  (`tools/release.sh`, `make_package.py`, `make_tool_archives.py`) were not
  brought over; see the roadmap.
- `board/docs/hardware-pinmap.md` leaves some ports as "—". The variant
  header has them all; the summary is in
  [../docs/platform.md](../docs/platform.md).
- The core has no README of its own here. The Tools menus, `Serial`
  behaviour and memory report are described in
  [../README.md](../README.md) and [../CLAUDE.md](../CLAUDE.md).

**Fixed here, not yet released:**
- **Linux builds failed.** `cores/arduino/ch32/lib/ch32yyxx.h` included
  `core_riscv_cH32yyxx.h`; the file is `core_riscv_ch32yyxx.h`, so it only
  resolved on case-insensitive file systems (Windows, default macOS). Fixed
  in this copy (ships with 0.3.0); CLAUDE.md gives the symlink workaround
  for an installed 0.2.4.

**Known problems, to fix here:**
- **Stale comments.** Several say the bootloader is 8 KB and the app starts
  at 0x2000 (`link_chgame_app.ld`, `chgame_map.h`); the code says 12 KB and
  0x3000.

## CHGame (`board/arduino/CHGame/libraries/CHGame/`)

The library every game is built on; [its README](board/arduino/CHGame/libraries/CHGame/README.md)
is the reference and [../docs/chgame-library.md](../docs/chgame-library.md)
the record of its decisions. Like CHGfx it is not in the board package yet:
- `tools/device.py` passes `--library <repo>/platform/board/arduino/CHGame/libraries/CHGame`;
- the simulator compiles its `src/` unless `CHSIM_CHGAME` points elsewhere;
- Arduino IDE users copy this folder into their sketchbook's `libraries/`.

A change to it is a change to every game: rebuild all twenty (size), and
compare their simulator frames (and, for `chgame/Audio`, the sound preview
hashes: `tools/audio/preview.py`).

## CHGfx (`board/arduino/CHGame/libraries/CHGfx/`)

The games compile against this copy:
- `tools/device.py` passes `--library <repo>/platform/board/arduino/CHGame/libraries/CHGfx` to
  arduino-cli. That takes priority over a CHGfx installed in the sketchbook.
- The simulator (`tools/chsim/chsim.py`) uses its `src/` unless
  `CHSIM_CHGFX` points elsewhere.
- Arduino IDE users copy this folder into their sketchbook's `libraries/`.

**Documentation:**
- Its README documents the API, draw modes and configuration macros.
- Its README links `../PERFORMANCE.md`. Here that document is
  [../docs/performance.md](../docs/performance.md).
- `extras/sim` is CHGfx's own small simulator, used to test the library
  itself. It is a different program from the repository's `tools/chsim`,
  which runs whole games.

## CHSd (`board/arduino/CHGame/libraries/CHSd/`)

The SD reader of CHWords, CHCrossword and CHWordWheel. They include it as
a library (`<Fat.h>`, `<SdSpi.h>`); there are no copies in the games.

To change it:

```bash
cd platform/board/arduino/CHGame/libraries/CHSd
python tests/run_tests.py          # FAT16/FAT32 images, every failure mode
```

Then run `tools/check.py` in each of the three games. Its `tools/fatimg.py`
builds and reads FAT16/FAT32 card images; it is useful for any SD work.

## The bootloader (`bootloader/`)

The board's permanent bootloader with a game menu that installs games from
the SD card ([../docs/sd-menu.md](../docs/sd-menu.md)).
[bootloader/README.md](bootloader/README.md) has the design, the
differences from 0.2.4, building, testing and installing.

**It is in `platform/board`, not in a released package yet** (2026-10-02).
- `board/arduino/CHGame/bootloaders/CHGame/` carries the menu bootloader,
  the no-menu build and the 0.2.4 bootloader. *Tools > Bootloader* chooses
  one, and the programmer **CHGame USB** writes it through the bootloader
  already on the board (`chgame-upload burn`, tool version 0.2.0,
  `bootloader/host/go`); **WCH factory ISP** remains for recovery.
- Tried on a board through `arduino-cli burn-bootloader`: every change
  between the three, 0.2.4 to the menu included, then an upload.
- The installed package 0.2.4 has none of this: it offers the factory ISP
  only and writes the 0.2.4 bootloader.
- Games build against core 0.2.4 unchanged; the menu bootloader is
  compatible with it.
- To ship it through the Boards Manager, the release must also publish the
  `chgame-upload` 0.2.0 archives and name them in the package index.

## Changing a platform piece

1. Make the change here and say what it is for in the commit. For the
   bootloader, also list it in its README.
2. Rebuild every game. `python tools/device.py build` in each game must still
   fit, and the simulator frames must be unchanged or deliberately changed
   (CLAUDE.md rules 2 and 3).
3. `bootloader/src/sd.c` and `fat.c` are a C fork of CHSd: a fix to one
   belongs in the other too.
4. When a version number changes, update this table, `CLAUDE.md` and the
   root README.

## Changes since the copies were taken

- `board/`: the core is as released; `arduino/CHGame/libraries/` gained CHGame, CHGfx and CHSd.
- `board/arduino/CHGame/libraries/CHGfx/`: `library.properties` gives this repository's URL.
- `board/arduino/CHGame/libraries/CHGame/`: new.
- `board/arduino/CHGame/libraries/CHSd/`: used as a library by the three SD
  games since 2026-10-02 (`tools/vendor.py` and the games' copies are gone);
  `architectures=ch32v`; the simulator's card is `$CHSD_CARD`.
- 2026-10-02: the three libraries moved from `platform/libraries/` into the
  board package's `libraries/` folder. Checked: 17 release images byte for
  byte the same, the three SD games 4 to 56 B smaller, every game's README
  reel frame for frame the same from the simulator.
- `bootloader/`: the SD menu work, listed in its README.
- 2026-10-02: the core's crash handler (`cores/arduino/ch32/chgame_boot.c`
  `chgame_fault()`, reached from `HardFault_Handler` and `while1_handler`)
  silences the piezo and lights the LED; debug builds also keep the crash
  for the CHGame library's `!` command (CHANGELOG). Release images grow
  64-72 B (CHCrossword 50,416 B, still under 50,432). Builds see it only
  through a patched installed 0.2.4 until the next release.
