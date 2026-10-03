# Trying a release as a new user

How to install a board package built from this repository, before anything
is published, and see it the way someone who only has the Arduino IDE sees
it. The release itself is in [building.md](building.md).

## 1. Stage it

From the repository root:

```bash
python tools/release/stage.py
```

This builds what a release would (the uploader for the five hosts, its tool
archives, the platform archive, the Boards Manager index) into `out/stage/`,
as version **`<version>-local`** (for example `0.3.0-local`), with every
download URL on `http://localhost:8765`. Then it runs the new-user test,
`tools/release/acceptance.py`:

- a fresh `arduino-cli` with its own folders in `out/newuser/` (your own
  Arduino setup is not touched) installs CHGame from that URL;
- it checks that the libraries came with it, that *File > Examples* lists
  Hello, the twenty games and CHSDtoUSB, that *Tools > Bootloader* and
  *Tools > Programmer* offer what they should, and that the bootloader files
  are there;
- it copies Hello, CHFour and CHWords into the sketchbook, as the IDE does
  when an example is saved, and compiles them with no `--library`, checking
  that *Export Compiled Binary* leaves a `.bin` and a `.chg`;
- it compiles every game and app from the installed package and packs the
  SD card's contents from those builds:
  `out/stage/CHGame-sdcard-<version>.zip`.

`--quick` skips the twenty games and the card (a few minutes instead of
about fifteen). The toolchain (250 MB) is downloaded once and kept in
`out/arduino-downloads/`.

The `-local` version is a pre-release, so it sorts before the real one: when
the release is published, Boards Manager offers it as an update, and the
uploader is downloaded again rather than kept from the staged install.

## 2. Install it in the Arduino IDE

```bash
python tools/release/serve.py
```

serves `out/stage/` until Ctrl+C. In the Arduino IDE 2.x:

1. *File > Preferences > Additional boards manager URLs*: add
   `http://localhost:8765/package_chgame_index.json`. Until the release is
   published, the GitHub URL in the README has nothing behind it and the IDE
   reports an error for it; remove it while you test, and put it back after.
2. *Tools > Board > Boards Manager*, search **CHGame**, install
   **0.3.0-local** (listed as *CHGame Boards by bateske*). It brings the RISC-V toolchain, wchisp and
   `chgame-upload` with it.
3. Stop the server. Nothing is fetched after the install.

An IDE that already has CHGame installed upgrades in place. To start from
nothing, as a new user would, remove it in Boards Manager first, and delete
the cached index (`%LOCALAPPDATA%\Arduino15\package_chgame_index.json` on
Windows, `~/.arduino15/` on Linux, `~/Library/Arduino15/` on macOS) if the
IDE keeps showing an old version.

## 3. What to try

**Pick the board.** *Tools > Board > CHGame Boards > CHGame*, and the port
(the board is USB `16C0:27DD`).

**The examples.** *File > Examples*, under *Examples for CHGame*:

- *CHGame > Hello*: the smallest complete sketch. Upload it with the default
  options.
- *CHGame > Games > CHFour* (or any of the twenty). The games are written to
  fill the flash, so set *Tools > Optimize* to **Smallest + LTO** and
  *Tools > USB* to **Upload only** first; with the defaults the larger ones
  do not fit. Each game's README is in its folder (*Sketch > Show Sketch
  Folder*).
- *CHGame > Apps > CHSDtoUSB*: the board as a USB card reader.
- *CHGfx* has its own examples (*HelloGraphics*, *Demoscene* ...).

Nothing needs to be copied into the sketchbook's `libraries/`:
`#include <CHGame.h>` works in a new sketch.

**The bootloader.** The SD game menu comes with the package:

1. *Tools > Bootloader*: **SD Game Menu (Rainbow)** (the default),
   **SD Game Menu (Plain)**, **SD Game Menu (Casino)**, or **USB Only**.
   The three menus differ only in their colours.
2. *Tools > Programmer*: **CHGame USB (requires CHGame bootloader, no
   drivers)**. It goes through the bootloader already on the board, like
   Upload: no driver, no buttons, and the port must be selected.
3. *Tools > Burn Bootloader*. The installed sketch is erased; the board
   comes back in the new bootloader. With the menu bootloader it shows the
   game menu at power-on.

*Upload Using Programmer* (Sketch menu) does the same and then uploads the
open sketch. **WCH factory ISP** is for a board whose bootloader is missing
or broken: hold BOOT on power-up first, with the WinUSB driver on Windows
([recovery.md](recovery.md)).

**The SD card.** Unzip `CHGame-sdcard-<version>.zip` onto a FAT32 card
(everything at the root: the `GAMES` folder and the data files beside it),
put it in the board and switch on: the menu lists the games. To copy files
without taking the card out, pick **SD CARD READER** in the menu.

**Your own game on the card.** *Sketch > Export Compiled Binary* writes
`<sketch>.ino.chg` into the sketch's `build/` folder beside the `.bin`. Copy
it into the card's `GAMES` folder under a short name (`MYGAME.CHG`); the
menu shows the sketch's name in capitals. `chgame-upload pack` sets another
title (`-title "MY GAME"`).

## 4. Afterwards

Put the GitHub URL back in the Preferences once the release is published,
and remove the localhost one. The staged package can stay: Boards Manager
offers the release as an update.
