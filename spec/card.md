# From a cart to a CHGame: runtime preparation and the card, version 2

What a `.chgame` ([chgame.md](chgame.md)) becomes on a CHGame: the files on
its SD card that the bootloader's game menu reads, and the game in its flash.
This is for whoever implements a card builder, an uploader or an emulator.
Game developers never need it: `chgame cart prepare` and `chgame cart deploy`
do all of it.

**The reference** is [tools/chcart/runtime.py](../tools/chcart/runtime.py)
and [deploy.py](../tools/chcart/deploy.py); the bootloader's side is
[shared/chgame_card.h](../platform/bootloader/shared/chgame_card.h) and
[src/menu.c](../platform/bootloader/src/menu.c). Every step below is
deterministic, so two implementations write the same bytes.
[fixtures/](fixtures) pins the results.

**Which bootloader.** This layout is read by the menu bootloader v2
(BOOT_VERSION 3). The menu before it (BOOT_VERSION 2, board package 0.3.0)
lists only the CHG files directly in `GAMES/`: a cart without folders still
works there, minus its order, launch game and background. A cart with
folders needs v2.

## The card

```
GAMES/                    the menu's tree; nothing else may use this folder
  MENU.IDX                this folder's entries in the cart's order, folder titles, launch flags
  MENU.BG                 the background (always at the top; in a folder only if it has its own)
  BLACKJAC.CHG            a game: its binary behind a 512-byte header (chg.md)
  CARDGAME/               a folder: the same again (MENU.IDX, maybe MENU.BG, CHG files, folders)
WORDS.DIC, CHCW/, ...     the games' SD files, at their paths (chgame.md, sdcard)
```

The card is FAT16 or FAT32, one volume, 8.3 names: no long names are
needed, since every name below is 8.3 in capitals. Where files sit on the
volume, and the order of directory entries, do not matter.

## Runtime preparation, step by step

Preparation takes one cart and a device (`rev0`) and gives a set of files,
`{card path: bytes}`. Every game must have a binary for the device (else
`bad-device`) and the cart must pass every rule of chgame.md.

### 1. The folders

Each folder's entries come from walking `games` in order. A game's folder
path is split at `/`; each folder along it is created in its parent's list
the first time it is met, at that point; then the game is appended to its
folder's list. The top level is `GAMES/` itself.

### 2. Names

Each folder's entries are named in list order, each name unique within that
folder:

- **A game** is named from its `title`; **a folder** from its own name (the
  last part of its path).
- **The base:** the letters A-Z and digits 0-9 of that text, with a-z
  turned to capitals, cut to 8 characters. When there are none, `GAME` or
  `FOLDER`.
- **The extension:** a game's file is `<base>.CHG`; a folder has none.
- **Taken names.** Games and folders are separate (`WORDS.CHG` and a folder
  `WORDS` can sit side by side). A name already used in the folder, or one
  of Windows' device names (`CON`, `PRN`, `AUX`, `NUL`, `COM1`-`COM9`,
  `LPT1`-`LPT9`), is taken.
- **A taken name** is tried again with n = 2, 3, ...: the base cut to
  `8 - len(str(n))` characters, then n.
- **Examples:** WORDS, WORDS2; BLACKJAC (from "BLACKJACK"), BLACKJA2;
  SNAKESLA (from "SNAKES & LADDERS"); CON2.

### 3. CHG files

Each game becomes `<folder>/<name>.CHG`: chg.md's format, built as
`tools/chgpack.py pack` builds it:

| Field | Value |
|---|---|
| payload | the game's binary, padded with 0xFF to a multiple of 4 |
| title | the game's `title` |
| author | the game's `author` if it is printable ASCII, cut to 15 characters; else empty |
| version | the game's `version` the same way, cut to 7 characters |
| app_version, flags, image slot | 0 |

### 4. MENU.IDX

One per folder, in every folder, top level included. It is made of 32-byte
records:

| | Bytes | Value |
|---|---|---|
| record 0 | 0-3 | `CHX1` (0x43 0x48 0x58 0x31) |
| | 4-31 | 0 |
| one record per entry, in list order | 0-10 | the entry's 8.3 name as a directory stores it: the base padded with spaces to 8, then the extension padded to 3 (`BLACKJACCHG`, `CARDGAME   `) |
| | 11 | flags: bit 0 = launch (below); the rest 0 |
| | 12-31 | a folder: its name as given (not the 8.3 one), ASCII, NUL-padded. A game: 0 |

**Launch.** When the cart has `launch`, the launch game's record is
flagged, and so is the record of every folder on the way to it, from the
top level down. Nothing else is flagged.

### 5. MENU.BG

The top level always gets one: the cart's `menu.background`, or, without
it, [assets/menu-default.png](assets/menu-default.png) (the CHGAME logo in
the rainbow colour). A folder gets one only if `menu.folders` gives it a
background.

**The file** is 8,704 bytes:

| Bytes | Value |
|---|---|
| 0-3 | `CHB1` (0x43 0x48 0x42 0x31) |
| 4-7 | 0 |
| 8-39 | the palette: 16 colours, RGB565, little-endian u16 |
| 40-511 | 0 |
| 512-8703 | 128 rows of 64 bytes, top row first; two pixels a byte, the left one in the high nibble; each a palette index |

**From the PNG** (128x128, opaque, read as 8-bit RGB). The menu's colours
are the cart's `menu.colors`, defaults filled in. Each pixel's index is:

1. **15** if the pixel is exactly `#FF00FF`. Colour 15 is drawn as the
   rainbow, so its palette entry is 0.
2. Otherwise, if it equals a menu colour, that colour's index: **11**
   `text`, **12** `disabled`, **13** `selectedText`, **14** `mark`. If
   several menu colours are equal, the lowest index wins.
3. Otherwise **0-10**: each other colour gets the next index the first time
   it appears, reading the rows top to bottom and each row left to right.
   More than 11 such colours is an error (`bad-background`).

**The palette:** entries 0-10 are those colours, the unused ones 0; 11-14
are the menu colours; 15 is 0. Each colour is RGB565: red's top 5 bits
(15-11), green's top 6 (10-5), blue's top 5 (4-0).

No colours are reduced or merged: reducing is a choice of taste that two
implementations would make differently, so the PNG must already have few
enough. The default background uses three: black (= `selectedText`), grey
(= `disabled`) and `#FF00FF`.

### 6. SD files

Every game's `sdcard` files, at their paths. Games carrying the same file
give one copy.

### The result

| | |
|---|---|
| The set of files | for each folder, top level first, then its subfolders as they were created: `MENU.IDX`, `MENU.BG` if any, then its CHG files in list order; then the SD files, paths sorted. The order is only the order chcart writes them in: on the card it means nothing |
| A card image (optional) | `chgame cart prepare --image` writes a FAT32 image with the volume label `CHGAME` (CHSd's `tools/fatimg.py`). An emulator can run the real bootloader binary against it |

## How the menu reads the card

What bootloader v2 does with these files (docs/sd-menu.md tells players):

- **At power-on** with no request, B not held and START not held, it reads
  the top-level `MENU.IDX`:
  - a flagged entry that is a folder: it reads that folder's index the same
    way, down to 4 levels;
  - a flagged game: it starts it; if that game is not the one in flash, it
    installs it first, showing progress, then starts it;
  - anything failing: it shows the menu there, with the error.
- **START held at power-on, or a reset by a game** (its 3 s START exit):
  the menu, never the launch game.
- **A list** is a folder's directory: its `*.CHG` files and subfolders,
  except hidden and system entries and names starting with `.` or `_`, 128
  at most.
  - Entries named in `MENU.IDX` come first, in record order.
  - The rest follow, sorted by title (a folder's title is its index title,
    or its 8.3 name). So a game copied onto the card by hand still shows,
    after the cart's own.
  - Records naming no entry are skipped.
  - At the top level, "INSTALLED PROGRAM" heads the list when the program
    in flash is not in it.
- **Keys:** A or START opens a folder or plays a game, and B goes back.
- **Backgrounds:** a folder without `MENU.BG` keeps its parent's. A
  `MENU.BG` that is not 8,704 bytes, or does not start with `CHB1`, is
  ignored, and the menu uses its own look: black, a grey band, the title
  CHGAME.
- **Text:** titles are drawn over the background in colours 11-14. The
  selection bar, the boxes and every colour-15 pixel turn through the colour
  wheel, the hue moving with x + y and with time.
- **Errors** are shown as a number (docs/sd-menu.md lists them). Nothing
  is erased until a game has passed every check.

## Deploy rules

How a cart gets onto a CHGame (`chgame cart deploy`). A web uploader
follows the same rules.

**One game without SD files:** flash its binary over USB.
- With a card given, its CHG file is also added to `GAMES/`, so the menu
  lists it.

**One game with SD files:** a mounted card is needed.
- Its SD files and its CHG file go onto the card, then its binary is
  flashed.
- The card's own `MENU.IDX` and `MENU.BG` are left alone.
- Its CHG file's name follows step 2 against the names already in `GAMES/`.
  A CHG file there with the same title is the same game and is replaced.

**Several games:** a mounted card is needed.
- The prepared files are written to the card. The cart's `MENU.IDX` and
  `MENU.BG` replace the card's, and other files stay.
- `--clean` empties `GAMES/` first.
- If the cart names a `launch` game, that game is flashed.

**The card:** any mounted FAT16/FAT32 folder: a card reader, or the CHGame
itself running CHSDtoUSB (the menu's SD CARD READER). Each file is flushed
as it is written. Eject the card before the CHGame reads it.
