# From a cart to a CHGame: runtime preparation and the card, version 2

What a `.chgame` ([chgame.md](chgame.md)) becomes on a CHGame: the files on
its SD card that the bootloader's game menu reads, and the game in its flash.
This is for whoever implements a card builder, an uploader or an emulator.
Game developers never need it: `chgame cart prepare` and `chgame cart deploy`
do all of it, and `chgame cart backup` the way back (the last section).

**The reference** is [tools/chcart/runtime.py](../tools/chcart/runtime.py)
and [deploy.py](../tools/chcart/deploy.py); the bootloader's side is
[shared/chgame_card.h](../platform/bootloader/shared/chgame_card.h),
[src/card.c](../platform/bootloader/src/card.c), the list menu
[src/menu.c](../platform/bootloader/src/menu.c) and the visual menu
[src/visual.c](../platform/bootloader/src/visual.c). Every step below is
deterministic, so two implementations write the same bytes.
[fixtures/](fixtures) pins the results.

**Which bootloader.** This layout is read by the menu bootloader v2
(BOOT_VERSION 3) in either of its faces (*Tools > Bootloader*): the **list
menu**, a text list over `MENU.BG`, and the **visual menu**, one picture at
a time and no text (the covers, `SYSTEM.PIC` and the games' pictures). Each
reads its own files and skips the other's, so one card serves both. The
menu before v2 (BOOT_VERSION 2, board package 0.3.0) lists only the CHG
files directly in `GAMES/`: a cart without folders still works there, minus
its order, launch game, background and pictures. A cart with folders needs v2.

## The card

```
GAMES/                    the menu's tree; nothing else may use this folder
  MENU.IDX                this folder's entries in the cart's order, folder titles, launch flags
  MENU.BG                 the list menu's background (always at the top; in a folder only if it has its own)
  COVER.PIC               the visual menu's cover of the folder (always at the top: the splash;
                          in a folder only if it has its own)
  SYSTEM.PIC              (top only) the visual menu's own screens: the about page, then the others
  BLACKJAC.CHG            a game: its binary behind a 512-byte header (chg.md), then its picture
  CARDGAME/               a folder: the same again (MENU.IDX, maybe MENU.BG and COVER.PIC, CHG files, folders)
WORDS.DIC, CHCW/, ...     the games' SD files, at their paths (chgame.md, sdcard)
```

The card is FAT16 or FAT32, one volume, 8.3 names: no long names are
needed, since every name below is 8.3 in capitals. Where files sit on the
volume, and the order of directory entries, do not matter.

## Runtime preparation, step by step

Preparation takes one cart and a device (`rev0`, the default) and gives a
set of files, `{card path: bytes}`. Every game must have a binary for the
device (else `bad-device`) and the cart must pass every rule of chgame.md.

**A card is for one board.** Its CHG files carry that device's target id
(chgame.md, "Devices and revisions"), and a bootloader installs only its own
board's: on another board the menu lists them greyed under their 8.3 names
and starting one shows ERROR 5, with nothing erased. Someone with two
boards keeps a card for each. The menu's own files and the SD files do not
depend on the board.

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
| payload | the game's binary for the device, padded with 0xFF to a multiple of 4 |
| target id, layout id | the device's (chgame.md's device table): `CX35`, `0x003000F7` for `rev0` |
| title | the game's `title` |
| author | the game's `author` if it is printable ASCII, cut to 15 characters; else empty |
| version | the game's `version` the same way, cut to 7 characters |
| app_version, flags | 0 |
| picture (offset 0x060) | the game's `cartImage` made into a picture (step 7) if it follows the picture rule: written at the first multiple of 512 after the payload, the gap 0, and named in the header's field: offset, 8,704, CRC-32 of those bytes. Otherwise 0 and no picture |
| record (offset 0x06C) | the game's record (chg.md): its `info.json` entry, `binaryBytes`, its `cartImage`, licence files and SD files' sizes and CRCs, written at the first multiple of 512 after the picture (or the payload), the gap 0. Always written; a record over 1 MiB (huge licence files) is the error `record-size` |

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

**From the PNG** (128x128, opaque, read as 8-bit RGB). Carts hold PNGs
that already follow these rules; `chgame background` (tools/chcart/background.py)
converts any image into one, outside this format, so its choices (scaling,
reducing colours) never have to be repeated by another implementation. The menu's colours
are the cart's `menu.colors`, defaults filled in. Each pixel's index is:

1. **15** if the pixel is exactly `#FF00FF`. Colour 15 is the menu's
   own: a rainbow bootloader draws it as one colour turning through the
   colour wheel, a static one as its palette entry: the colour as painted.
2. Otherwise, if it equals a menu colour, that colour's index: **11**
   `text`, **12** `disabled`, **13** `selectedText`, **14** `mark`. If
   several menu colours are equal, the lowest index wins.
3. Otherwise **0-10**: each other colour gets the next index the first time
   it appears, reading the rows top to bottom and each row left to right.
   More than 11 such colours is an error (`bad-background`).

**The palette:** entries 0-10 are those colours, the unused ones 0; 11-14
are the menu colours; 15 is `#FF00FF` itself (0xF81F). Each colour is RGB565: red's top 5 bits
(15-11), green's top 6 (10-5), blue's top 5 (4-0).

No colours are reduced or merged: reducing is a choice of taste that two
implementations would make differently, so the PNG must already have few
enough. The default background uses four: black (= `selectedText`), grey
(= `disabled`), `#C0C0C0` and `#FF00FF`.

### 6. SD files

Every game's `sdcard` files, at their paths. Games carrying the same file
give one copy.

### 7. The visual menu's pictures

Every picture is a 128x128 PNG made into 8,704 bytes exactly as step 5 makes
MENU.BG (the same header, palette and rows), with one difference: **the menu
colours are always the defaults** (`text` `#FFF4D6`, `disabled` `#808080`,
`selectedText` `#000000`, `mark` `#D62020`), whatever the cart's
`menu.colors`, so a game's picture is the same in every cart. That is the
**picture rule**: opaque, at most 11 colours besides `#FF00FF` and those
four (`bad-picture` otherwise).

- **COVER.PIC** at the top: the cart's `menu.cover`, or, without it,
  [assets/cover-default.png](assets/cover-default.png). In a folder: the
  `cover` of its `menu.folders` entry, if it has one; else no file.
- **SYSTEM.PIC** at the top only: nine pictures one after another (78,336
  bytes), in this order (shared/chgame_card.h `CARD_SYS_*`):

  | | Picture | Shown |
  |---|---|---|
  | 0 | the cart's `menu.about`, or [assets/about-default.png](assets/about-default.png) | B on the cart's cover, or SELECT at the root: how the menu works |
  | 1 | `menu.systemImages.installed`, or [assets/system/installed.png](assets/system/installed.png) | the program in flash, when no game on the card holds it |
  | 2 | `menu.systemImages.game`, or [assets/system/game.png](assets/system/game.png) | a game without a picture |
  | 3 | `menu.systemImages.folder`, or [assets/system/folder.png](assets/system/folder.png) | a folder without a cover |
  | 4-8 | `menu.systemImages.error-1` ... `error-5`, or [assets/system/error-1.png](assets/system/error-1.png) ... `error-5.png` | install errors 1-5 |

  Each slot is the cart's picture when `menu.systemImages` (chgame.md)
  gives one, else the default in `assets/`, so a cart that gives none
  prepares the same bytes as before the key existed. The defaults are part
  of this specification: a new default changes the fixtures' expected
  results on purpose. These pictures are a layer above the bootloader's
  built-in screens, which it still draws when the card cannot give a
  picture: a cart cannot remove that fallback.

- **A game's picture** goes in its CHG file (step 3), from `cartImage`. A
  `cartImage` that breaks the picture rule is only a warning (`bad-picture`:
  older carts stay valid); the game then gets no picture.

### The result

| | |
|---|---|
| The set of files | for each folder, top level first, then its subfolders as they were created: `MENU.IDX`, `MENU.BG` if any, `COVER.PIC` if any, at the top `SYSTEM.PIC`, then its CHG files in list order; then the SD files, paths sorted. The order is only the order chcart writes them in: on the card it means nothing |
| A card image (optional) | `chgame cart prepare --image` writes a FAT32 image with the volume label `CHGAME` (CHSd's `tools/fatimg.py`). An emulator can run the real bootloader binary against it |

## How the menu reads the card

What bootloader v2 does with these files (docs/sd-menu.md tells players):

- **At power-on** with no request, B not held and START not held, it reads
  the top-level `MENU.IDX`:
  - a flagged entry that is a folder: it reads that folder's index the same
    way, down to 4 levels;
  - a flagged game that is the one in flash: it starts it at once, and the
    panel is never switched on;
  - a flagged game that is not in flash: the menu opens on it, in its
    folder, and waits. A on it installs and starts it. A power-on never
    writes flash by itself, so the game that was in flash is not written
    over by switching on;
  - a flagged file it cannot read: the menu opens on it, greyed.
- **START held at power-on, or a reset by a game** (its 3 s START exit):
  the menu, never the launch game.
- **A list** is a folder's directory: its `*.CHG` files and subfolders,
  except hidden and system entries and names starting with `.` or `_`, 240
  at most (each row takes 32 B of the bootloader's RAM). Beyond that, the
  first 240 the directory holds are listed. Runtime preparation never
  writes a fuller folder: a cart with one is refused (`full-folder`,
  chgame.md), and more games go in folders, which have no limit.
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
  ignored, and the list is drawn on black (the logo is the picture's:
  without one there is none).
- **What the menu draws over the picture**, and nothing else:
  - the list, over rows 20-119: ten rows of ten pixels, titles in colours
    11-14 from x 8;
  - the selection bar, the whole width;
  - the installed game's chip at x 2-4 (rows 2-7 of its row);
  - a folder's `>` at x 122;
  - message boxes over rows 36-87.

  Rows 0-19 and 120-127 are the picture's alone: the CHGAME logo of the
  default picture is part of it, as is anything a cart puts there.
- **Colour 15** is the selection bar, the boxes and every `#FF00FF` pixel
  of the picture. The bootloader comes in two styles (*Tools > Bootloader*):
  - **Rainbow**, the default: one colour, turning through the colour wheel
    (a turn in about 4 s);
  - **Static**: the menu's text colour (palette entry 11, the cart's
    `text`), so the bar, the boxes and the picture's `#FF00FF` match the
    titles. (Until 2026-10-06 it was the palette's entry 15, `#FF00FF`
    itself. The visual menu's Static style still shows entry 15 as painted.)

  Nothing else differs between them.
- **Errors** are shown as a number (docs/sd-menu.md lists them). Nothing
  is erased until a game has passed every check.

## How the visual menu reads the card

What the visual menu (*Tools > Bootloader: SD Graphic Menu*) does with the
same card; docs/visual-menu.md tells players. It reads the folders, their
order, the launch flags and the CHG headers exactly as the list menu does
(above), and draws no text.

- **Pictures:** `COVER.PIC` and each slot of `SYSTEM.PIC` are used when the
  file holds 8,704 bytes there that start with `CHB1`. A game's picture is
  used when its header's field at 0x060 names 8,704 bytes at a multiple of
  512 below 128 KiB that start with `CHB1`; readers may skip the CRC. A
  picture it cannot read is drawn from the bootloader's built-in screens.
- **The rows** of a folder are its cover, then its entries in the list
  menu's order; a sub-folder shows as its cover. `GAMES/` itself lists only
  its games: its folders are the categories. UP and DOWN go round the rows.
- **The ring:** LEFT and RIGHT step to the folder beside this one: at the
  top, `GAMES/` and its folders, round; below, the folders of the same
  parent. They land on that folder's cover. With nowhere to go (`GAMES/`
  without folders; a folder with no sibling) they do nothing.
- **Keys:** A plays a game (installs it first if need be), opens a
  sub-folder (on its first row), and on a folder's cover goes to the first
  row; on the cart's cover (`GAMES/`'s) it shows the installed program's
  picture, where A runs it and B goes back. B goes up a level from a folder's
  folder; at the root or in one of its folders it goes to the cart's cover,
  and on that cover it shows the about page (`SYSTEM.PIC` slot 0), which any
  key closes. SELECT goes to the cart's cover from anywhere, and at the root
  shows the about page. START does nothing.
- **At power-on**, a launch game that is the one in flash starts at once,
  the panel never lit (as the list menu). Otherwise the cover fades in and
  stays: it is the menu's first picture, whatever is installed. Behind it
  the menu looks for the installed game (`GAMES/`'s games first, then each
  folder in order, depth first; the first copy found is the one); if no
  game holds it, `GAMES/` gets a first row for it (`SYSTEM.PIC` slot 1). A
  on the cover shows the installed game's picture (A runs it, B goes back).
  A launch game that is not installed comes up after the cover, on its own
  picture, without a border, and waits for A: nothing is written at
  power-on. (Until 2026-10-06 the installed game came up after the cover by
  itself, and a launch game was installed and started unasked.)
- **What it draws over a picture:** over the installed game, a border one
  pixel wide round the whole picture (rows 0 and 127, columns 0 and 127), in
  colour 15 (Static: colour 11, the
  menu's `#FFF4D6`); while installing, a bar: a frame of colour 15 over rows
  110-119 (x 8-119), black inside, filling with colour 15. Everything else
  is the picture's.

## Deploy rules

How a cart gets onto a CHGame (`chgame cart deploy`). A web uploader
follows the same rules. Everything is for one device, `rev0` unless the
user says otherwise (`--device`): the card's CHG files and the binary
flashed. Before flashing, an uploader that knows the device checks it
against the board's `HELLO` and refuses another board
(platform/board/docs/protocol.md, "Which board").

**One game without SD files:** flash its binary over USB.
- With a card given, its CHG file is also added to `GAMES/`, so the menu
  lists it.

**One game with SD files:** a mounted card is needed.
- Its SD files and its CHG file go onto the card, then its binary is
  flashed.
- The card's own `MENU.IDX`, `MENU.BG`, `COVER.PIC` and `SYSTEM.PIC` are
  left alone (the game's picture travels in its CHG file).
- A CHG file in `GAMES/` with the same title is the same game, and is
  replaced under its own name. Otherwise the new file's name follows step 2
  against the names already in `GAMES/`.

**Several games:** a mounted card is needed.
- The prepared files are written to the card. The cart's `MENU.IDX`,
  `MENU.BG`, `COVER.PIC` and `SYSTEM.PIC` replace the card's, and other
  files stay.
- `--clean` empties `GAMES/` first.
- If the cart names a `launch` game, that game is flashed.

**The card:** any mounted FAT16/FAT32 folder: a card reader, or the CHGame
itself running CHSDtoUSB (the menu's SD CARD READER). Each file is flushed
as it is written. Eject the card before the CHGame reads it.

## Backing up a card

How a CHGame's card becomes a cart again, from the card alone: a mounted
card, an image of it, or its files (`chgame cart backup`,
[tools/chcart/backup.py](../tools/chcart/backup.py); [fixtures/](fixtures)
has cards to back up and the results). It rests on the record in each CHG
file (chg.md), which runtime preparation writes since 2026-10-06.

1. **The games, in the menu's order.** `GAMES/` is walked as the menu lists
   it: in each folder its CHG files and subfolders (not hidden or system
   entries, no name starting with `.` or `_`); first those named in its
   `MENU.IDX`, in record order; then the rest by title (a CHG file's header
   title as the menu shows it: capitals, `?` for what its font lacks, the
   first 19 characters; a folder's 8.3 name), then by 8.3 name. A folder's
   games come where the folder is. Folders deeper than 4 levels are left out
   (warning `bad-folder`).
2. **A folder's name** is its title in its parent's `MENU.IDX` when that
   is a valid folder name (chgame.md), else its 8.3 name.
3. **Each CHG file** is checked as the bootloader checks it (chg.md, checks
   1-7), taking the target id of any board the reader knows. One that fails
   is left out (`bad-chg`). Its binary goes under the device its target id
   names, so a card for rev1 backs up as `rev1` binaries.
   - **With a record:** the game is the record's `game`, its folder the one
     the file is in; its binary the payload's first `binaryBytes` bytes
     (the rest must be 0xFF padding, else the record is not used); its
     `cartImage` and licence files the record's.
   - **Without one** (`no-record`; a damaged record, one of another
     version or one that breaks a rule: `bad-record`): the title, author
     and version from the header; the id from the title (lower case, runs
     of other characters as one `-`, none at either end, 32 at most, `game`
     if nothing is left: `WORD WHEEL` gives `word-wheel`); the
     binary is the payload; the picture, if any, made back into a PNG
     (step 7 the other way: the menu's colours and `#FF00FF` exactly, the
     other colours as RGB565 gives them back, below). Its SD files are not
     known: the user names them.
4. **Ids are unique:** a game whose id is taken (a copy in another folder)
   gets `-2`, `-3`, ... (`renamed-id`).
5. **SD files:** each file a record names is read at its path:
   - not on the card: left out (`sd-missing`);
   - another size or CRC: backed up as the card has it (`sd-changed`): a
     hand edit, or another game's file at that path;
   - files no record names belong to no game, and are not backed up.
6. **The menu**, when the whole card is backed up (when only some games
   are, there is no menu and no launch game):
   - `launch`: the first game flagged in its folder's `MENU.IDX` whose
     folders are each flagged in their parent's;
   - `menu.colors`: the top `MENU.BG`'s palette entries 11-14; one that is
     the default colour's RGB565 is the default (left out), another is that
     colour as RGB565 gives it back;
   - `menu.background`: the top `MENU.BG` as a PNG, unless preparing the
     default background with those colours gives the same bytes; a
     folder's `MENU.BG` is its background;
   - `menu.cover`, `menu.about` and `menu.systemImages`: `COVER.PIC` and the
     slots of `SYSTEM.PIC`, each unless it is the default's bytes; a
     folder's `COVER.PIC` is its cover;
   - the cart's title is not on the card: the user gives it.

   **RGB565 back to a colour:** red `r * 255 / 31`, green `g * 255 / 63`,
   blue `b * 255 / 31`, each rounded down. That colour gives the same RGB565
   again, so the backup prepares the same picture.
7. **The result** is a cart that follows chgame.md (a backup that breaks a
   rule is refused). A card as runtime preparation wrote it backs up to a
   cart that prepares the same card again, byte for byte: the same games,
   files, folders, menu and launch game, less the screenshots and the
   cart's own title, author and the like, which only the cart holds.
