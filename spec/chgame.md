# The .chgame format, version 1

A `.chgame` file is how CHGame games are shared and distributed: one file
holding one or more compiled games, what they are called and who made them,
the files they read from the SD card, and pictures of them. Uploaders,
card builders and emulators take it as their input. Like the Arduboy's
`.arduboy`, from which it borrows, it is a ZIP file with a manifest,
`info.json`, at its root.

This document is the format's definition. The reference implementation is
[tools/chcart](../tools/chcart) (`chgame export`, `chgame cart ...`), and
[fixtures/](fixtures) holds conformance cases with the results an
implementation must give. What a CHGame does with a cart, its menu and SD
card, is [card.md](card.md): a separate step, so that this format stays the
same when the card's layout changes.

**Words.** A *cart* is a `.chgame` file; it holds one *game* or several.
"Must" and "must not" are requirements; a file that breaks one is not a
`.chgame`, and a reader refuses it.

## The container

- **A ZIP file** (PKWARE APPNOTE), named `*.chgame`. Each entry is stored
  (method 0) or deflated (method 8). Entries must not be encrypted. ZIP64 is
  not needed and need not be read.
- **Paths:**
  - printable ASCII, with `/` between folders;
  - relative, so no leading `/`, no drive letter or `:`;
  - no empty, `.` or `..` part, and no `\`;
  - two entries must not have the same path, even ignoring case;
  - an entry whose name ends in `/` is a folder and is ignored.
- **The manifest** is `info.json` at the root: UTF-8 JSON, one object.
- **Every other file is named by the manifest.** A file it does not name is
  ignored, with the warning `unused-file`. Where files sit inside the ZIP is
  up to the writer: readers go by the manifest's paths.
- **Limits** a reader may enforce: 4,096 files, 512 MiB uncompressed in all.
- **Writing.** chcart writes the same bytes for the same cart: `info.json`
  first, then the paths in sorted order, every entry dated 1980-01-01 00:00,
  deflate level 9, no extra attributes. Its layout is `<id>/<device>.bin`,
  `<id>/LICENSE`, `<id>/cart.png`, `<id>/screenshot-<k>.<png|gif>`,
  `<id>/sdcard/...` and `menu/...`. Readers must not depend on that layout.

## info.json

### The cart

| Key | | Value |
|---|---|---|
| `schemaVersion` | required | `1` |
| `title` | required | the cart's name: any text, not blank |
| `version`, `author`, `description`, `license`, `url`, `sourceUrl` | | text. `license` is an SPDX expression |
| `date` | | ISO 8601: `2026-10-03`, or with a time |
| `launch` | | the `id` of the game a CHGame starts at power-on instead of showing its menu (card.md) |
| `menu` | | how the cart's menu looks: below |
| `games` | required | the games, one or more, in menu order |

### `menu`

| Key | Value |
|---|---|
| `background` | path of a PNG, 128x128, opaque: the whole picture behind the menu, its title or logo included. The menu draws over rows 20-119 only (card.md). Pixels of exactly `#FF00FF` are drawn in the menu's colour 15: one colour turning through the rainbow, or as painted on a bootloader in the Static style. Besides `#FF00FF` and the four menu colours below, at most 11 colours (card.md says why, and how it is converted). `chgame background` makes any image into one (docs/menu-image.md) |
| `colors` | the menu's own colours, `#RRGGBB`: `text` (titles, default `#FFF4D6`), `disabled` (a file the menu cannot install, `#808080`), `selectedText` (the title on the selection bar, `#000000`), `mark` (the installed game's chip, `#D62020`) |
| `folders` | a list of `{"name": "CARD GAMES", "background": "path.png"}`: a folder's own background, the same kind of PNG. Folders without one show their parent's |

### A game

| Key | | Value |
|---|---|---|
| `id` | required | the game's handle within the cart: `a-z`, `0-9` and `-`, 1 to 32 characters, not starting with `-`; unique in the cart |
| `title` | required | what the menu shows: printable ASCII, 1 to 31 characters. The menu shows 19, in capitals (`a-z` are drawn as `A-Z`; characters after `_`, except `a-z`, as `?`) |
| `folder` | | the menu folder the game is in: `""` or absent for the top level, `"CARD GAMES"`, `"CARD GAMES/CLASSIC"` for one inside another. Each name is printable ASCII, 1 to 19 characters, no `/`, no space at either end; 4 levels at most |
| `version`, `author`, `description`, `genre`, `license`, `url`, `sourceUrl` | | text |
| `licenseFiles` | | paths of the game's licence and notice files (for example LICENSE and NOTICE), kept with its binary as its licence asks. Their last part is a plain file name |
| `buttons` | | `[{"control": "A", "action": "Lay a tile"}]`, as in `.arduboy` |
| `binaries` | required | `[{"device": "rev0", "filename": "path.bin"}]`: the game built for each board it runs on, at most one per device (below) |
| `sdcard` | | a folder in the ZIP, ending in `/`: every file under it goes onto the SD card's root at the same relative path (below) |
| `cartImage` | | path of a 128x128 PNG: the game's own title picture, kept for menus that show one |
| `screenshots` | | `[{"filename": "path", "title": "..."}]`: PNG or GIF (animated allowed), square, 128, 256, 384 or 512 pixels wide (the screen at 1x to 4x) |

### Order and folders

- **The order of `games` is the menu's order.**
- **A folder lists at most 240 entries** (games and folders), and so does
  the top level (`full-folder`). Folders hold any number of games between
  them.
- **A folder** takes its place in its parent's list where its first game
  is, in that order.
- **`menu.folders` only adds a background.** It never orders anything.

Example: games `A` (top level), `B` (folder `F`), `C` (top level), `D`
(folder `F`). The top level lists `A`, `F`, `C`, and `F` lists `B`, `D`.
To put a folder first, put its games first: `chgame cart order cart.chgame
F/` does that (an item ending in `/` is a folder's games).

### Binaries and devices

A binary is the raw program image (`.bin`), exactly what the board
package's build writes as `<sketch>.ino.bin`, linked to run at the device's
load address. It is never a `.hex` or a `.chg`: tools convert those on the
way in, so readers only ever see one format.

| `device` | Board | MCU | Load address | Largest image | Notes |
|---|---|---|---|---|---|
| `rev0` | CHGame Rev0 (`CHGame:ch32v:rev0`) | CH32X035G8U6 | 0x3000 | 50,944 B | saving needs the image at 50,432 B or less (above that a game's saves switch off: warning `save-pages`); the menu's CHG target `CX35`, layout `0x003000F7` (chg.md) |

- **The image's length**, padded with 0xFF to a multiple of 4, must not
  exceed the device's largest image.
- **A bootloader image is refused** (`bootloader-image`): one with the
  signature `0x4C424843` ("CHBL") as a 32-bit little-endian word at offset
  8.
- **New boards are added to this table.** A game runs on a board only if it
  has a binary for it.

### SD card files

- **Paths.** Each part of a path under `sdcard` must be an 8.3 name in
  capitals: 1 to 8 characters, optionally `.` and 1 to 3 more, from `A-Z`,
  `0-9` and ``! # $ % & ' ( ) - @ ^ _ ` { } ~``. The CHGame's FAT readers
  know nothing else.
- **`GAMES/` belongs to the menu**: no game may put files there.
- **Two games may carry the same file** (same path, same bytes): it is
  written once.
- **The same path with different bytes is an error** (`sd-conflict`). A
  card holds one.

Example: `"sdcard": "chwords/sdcard/"` and the ZIP entry
`chwords/sdcard/WORDS.DIC` put `WORDS.DIC` in the card's root.

## Rules a reader checks

| Code | | When |
|---|---|---|
| `not-a-zip` | error | the file is not a ZIP |
| `bad-zip` | error | an encrypted entry, another method, an unsafe or clashing path, over the limits |
| `no-manifest` | error | no `info.json` at the root |
| `bad-json` | error | `info.json` is not UTF-8 JSON, or not an object |
| `schema-version` | error | `schemaVersion` missing, not a whole number, or newer than the reader knows |
| `missing-field` | error | a required key is missing; `games` or a game's `binaries` empty |
| `bad-field` | error | a value of the wrong kind or form (text, list, date, colour, file name, button) |
| `missing-file` | error | a path the manifest names is not in the ZIP |
| `bad-id` | error | an `id` breaks its rule |
| `duplicate-id` | error | two games share an `id` |
| `bad-title` | error | a title is blank, not printable ASCII, or over 31 characters |
| `bad-folder` | error | a folder name breaks its rule, or folders nest deeper than 4 |
| `bad-device` | error | an unknown device, or two binaries for one |
| `binary-size` | error | an image empty, or larger than the device takes |
| `bootloader-image` | error | a bootloader, not a program |
| `bad-sd-path` | error | an SD path that is not 8.3 capitals, or under `GAMES/` |
| `sd-conflict` | error | two games' SD files at one path with different bytes |
| `bad-image` | error | a picture of the wrong kind or size; a background with transparent pixels |
| `bad-background` | error | a background with too many colours |
| `bad-launch` | error | `launch` names no game |
| `full-folder` | error | a menu folder (or the top level) holds more than 240 entries, games and folders together: the menu could not list them all |
| `unknown-key` | warning | a key this version does not define: ignored |
| `unused-file` | warning | a file the manifest does not name; an `sdcard` folder with nothing in it; a folder background for a folder no game is in |
| `long-title` | warning | a title over 19 characters (the menu shows the first 19) |
| `title-chars` | warning | a title with characters the menu shows as `?` |
| `save-pages` | warning | an image too large to keep the save pages |

A reader that meets an error refuses the whole cart. Warnings change
nothing.

## Versions

- **`schemaVersion` changes when a reader that ignores the change would
  behave differently.** A reader refuses a version newer than it knows.
- **New optional keys that may safely be ignored** do not change it. Older
  readers warn (`unknown-key`) and go on.
- **New devices** are additions to the table above, not a new version.

## An example

```json
{
  "schemaVersion": 1,
  "title": "Word Night",
  "author": "bateske",
  "launch": "chwords",
  "menu": {"background": "menu/background.png", "colors": {"text": "#FFFFFF"}},
  "games": [
    {
      "id": "chwords",
      "title": "WORDS",
      "version": "0.1",
      "author": "bateske",
      "genre": "Word",
      "license": "Apache-2.0",
      "licenseFiles": ["chwords/LICENSE", "chwords/NOTICE"],
      "binaries": [{"device": "rev0", "filename": "chwords/rev0.bin"}],
      "sdcard": "chwords/sdcard/",
      "screenshots": [{"filename": "chwords/screenshot-1.gif"}]
    },
    {
      "id": "chcrossword",
      "title": "CROSSWORD",
      "folder": "PUZZLES",
      "binaries": [{"device": "rev0", "filename": "chcrossword/rev0.bin"}],
      "sdcard": "chcrossword/sdcard/"
    }
  ]
}
```

## What came from .arduboy, and what changed

**Kept:**
- a ZIP renamed, with `info.json` at its root;
- `schemaVersion`;
- the cart's text fields (`title`, `author`, `version`, `description`,
  `date`, `genre`, `url`, `sourceUrl`, `license`);
- `binaries` as a list of `{device, filename}`, one per board;
- `buttons`, `screenshots`, a cart image per game.

**Changed:**
- **One file holds several games.** `games` is the list, in menu order,
  with folders. A single game is a list of one.
- **Binaries are raw `.bin`, never `.hex`.** The load address comes from
  the device.
- **SD card files** (`sdcard`) take the place of FX flash data. There are no
  per-game save files yet: every game shares the board's two save pages.
- **Pictures are the colour screen's**: 128x128, and backgrounds have a
  palette rule.
- **The rules are exact, and their codes stable**, with fixtures, so that
  tools and emulators read a cart the same way. With `.arduboy`, tools that
  read the manifest differently, or not at all, made that hard.

## Making and reading carts

| | |
|---|---|
| A sketch as a cart | `chgame export` in its folder writes `build/<Name>.chgame`, described by the sketch's `chgame.json` (tools/chcart/sources.py: every key optional) |
| Carts from games and other carts | `chgame cart new OUT ITEM ...` (`.chgame`, `.bin`, `.hex`, `.chg`, sketch folders), `add`, `remove`, `order`, `set`, `launch`, `background` |
| Checking | `chgame cart verify FILE ...` prints every issue and exits 1 on an error; `chgame cart info FILE --json` prints the manifest as chcart reads it |
| The card | `chgame cart prepare FILE DIR [--image IMG]`, `chgame cart deploy FILE --card E:\` (card.md) |
