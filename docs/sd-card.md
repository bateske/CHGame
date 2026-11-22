# The SD card

The microSD slot shares SPI1 with the display. Three games read data from
it, and one utility exposes it over USB.

## Who uses it, and with what

| | Driver | Reads | Licence |
|---|---|---|---|
| CHWords | CHSd (the library) | `WORDS.DIC` in the card's root: the full ENABLE word list (4 MB) | MIT |
| CHWordWheel | CHSd | `PHRASES.BNK` in the root: the phrase bank (39 KB) | MIT |
| CHCrossword | CHSd | `CHCW/*.CWD`: puzzle packs | MIT |
| CHSDtoUSB | its own read-write driver (from sdfatlib, CRC-checked, DMA) | the whole card, block by block, for the PC | GPL-3.0 |
| CHSDtoSerial | the same read-write driver, with FatFs on top | files, for the CHGame website over the serial port | GPL-3.0 |

The **bootloader** reads the card too: its game menu lists and installs
the CHG files in `GAMES/` and its folders, in the order and over the
picture the card gives it ([sd-menu.md](sd-menu.md),
[../spec/card.md](../spec/card.md)). It uses its own C port of
CHSd (`platform/bootloader/src/sd.c`, `fat.c`), which follows any amount of
fragmentation and recovers a card that a reset left mid-transfer.

The other 17 games never touch the card. Each SD game also works without
one, using its built-in data in flash. The card adds to that.

**CHSd** ([../platform/board/arduino/CHGame/libraries/CHSd](../platform/board/arduino/CHGame/libraries/CHSd)):
- **What it is.** A polled SPI block driver and a FAT16/FAT32 reader, about
  1.7 KB of flash and 24 B of RAM.
- **How a game reads a file.** `fat::open("WORDS   DIC", runs, max, buf)`
  finds the file by its 8.3 name once and returns a run count (0 = any
  failure). `fat::read(runs, n, k, buf)` then reads block `k`.
- **The buffer.** Each call borrows a 512 B buffer; the games lend CHGfx's
  chunk scratch, which is idle between `gfx_wait()` and the next flush.
- **Limits.** No writing, no cache, no file object. Its README covers the
  API, the bus rule, the error codes and why it is slow on purpose.

## Rules for code that touches the card

- **Use the card only between `gfx_wait()` and the next flush.** CHGfx
  streams the framebuffer by DMA on the same bus. Hand SPI1 back exactly as
  CHGfx left it.
- **Select the card by its own pin.** The card's chip select is `PIN_SD_CS`:
  PB11 on Rev0, PB3 on Rev1 (CHSd picks it from the board being built
  for). The default `SS` (PA4) is the LCD on both. On Rev1 an OR gate holds
  the card's DI high while its CS is high, so the panel's traffic never
  reaches it; on Rev0 the card sees that traffic and must ignore it, which
  some cheap cards do not ([hardware-revisions.md](hardware-revisions.md),
  "For rev1: the SD card's DI gate").
- **Card formats.** Players' cards are FAT16 or FAT32; cards up to 32 GB
  come that way. exFAT (64 GB and up) is reported as `E_EXFAT`, so a game
  can say "reformat as FAT32". A file in more pieces than the run list holds
  is refused (`E_FRAG`).
- **After a failed read, re-initialise** (`sd::init()` or `fat::open`) before
  the next read.
- **Some cards are slow.** They take 300-800 ms to deliver a block that has
  never been written, so CHSd waits up to 1 s per block and CHSDtoUSB up to
  1.5 s.
- **The games hold no copy of CHSd.** They include the library; change it
  there and run its tests and `chgame check` in the three games.

## In the simulator

The SD games' simulator shims (`tools/chsim/host/VCard.h`, `sd_host.cpp`,
generated from CHSd's `host/`) give the game a pretend card:
- A `.img` file is served as the whole card. CHSd's `tools/fatimg.py` and
  CHCrossword's `tools/puzzles/mkcard.py` make them.
- Any other file (e.g. `sdcard/WORDS.DIC`) is put on a pretend FAT16 card
  built on the fly, in two pieces, so the real FAT code runs.
- Choose the card with `CHSD_CARD=<file>`, or `chdrive.py --card <img>`
  (CHCrossword). Unset means
  no card.

## Putting files on a real card

**A card is for one board.** Its CHG files carry that board's binaries and
its target id, and the menu of another board greys them and refuses them
(ERROR 5, nothing erased). The data files (`WORDS.DIC` and the rest) are
the same for both.

**Everything at once:** `chgame card` builds every game for every board
the installed core has into one cart, `out/CHGame-Casino.chgame`, with
every board's binaries, and lays out a card per board in
`out/sdcard-<board>/` (`out/sdcard-rev0/`, `out/sdcard-rev1/`): `GAMES/`
(the CHG files, the APPS folder, `MENU.IDX`, `MENU.BG`), `WORDS.DIC`,
`PHRASES.BNK`, `CHCW/` and `MODELS/`. `--image` also writes a FAT32 image
per board, `out/sdcard-<board>.img`, and `chgame --board rev0 card` makes
one board's alone. Copy the contents of the board's folder to the card's
root, or `chgame --board <board> cart deploy out/CHGame-Casino.chgame
--card <drive>`. A release carries the same cards as one zip per board,
`CHGame-sdcard-<version>-rev0.zip` and `-rev1.zip`: unzip the one for the
board in hand.

**One game's files** travel in its `.chgame` (`chgame export`): its
`sdcard/` folder becomes the cart's SD files, and deploying the cart puts
them where the game reads them ([../spec/chgame.md](../spec/chgame.md)).

**From a PC with a card reader:** copy the game's files from its `sdcard/`
folder to the card. Follow the paths above exactly: the root for
`WORDS.DIC` and `PHRASES.BNK`, `CHCW/` for crossword packs.

**Without removing the card:** upload
[CHSDtoUSB](../platform/board/arduino/CHGame/libraries/CHGame/examples/Apps/CHSDtoUSB),
built for the board in hand. The board becomes a USB drive with its
serial port still working:
1. Copy the files to the drive and eject it.
2. Upload the game again. Upload works while the drive is mounted.

The exact steps for an agent are in [../CLAUDE.md](../CLAUDE.md).

## Status

CHSd has been tested extensively on the PC against FAT16/FAT32 images, and
in all three games' simulators. **It has not yet read a real card on a
board.** The first device session should check:
- a FAT32 SDHC card;
- a small FAT16 card;
- an exFAT card (the error message);
- pulling the card mid-game;
- the time `fat::open` and one `fat::read` take.

CHSDtoUSB has been tested on hardware: 78 checks pass on a test build, raw
reads at about 490 KB/s and writes at about 400 KB/s.

Rev1's card (CS on PB3, the DI gate) has been checked only on the PC so
far: CHSd's tests run its SPI driver for both boards, and the bootloader's
PC suite reads rev1 cards. On a Rev1 board, `tools/sketches/CHBoardTest`
reads the card, and CHSDtest's `MIX` with `SET PATTERN 1` should pass with
the cards that fail it on Rev0.
