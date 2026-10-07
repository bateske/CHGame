# CHG files: what the SD menu installs

A CHG file is one program as the bootloader's game menu installs it from the
SD card ([../docs/sd-menu.md](../docs/sd-menu.md)): the sketch's ordinary
`.bin` with a 512-byte header in front. It is the runtime form, written by
runtime preparation ([card.md](card.md)) from a `.chgame`
([chgame.md](chgame.md)), which is the form games are shared in. Your sketch
itself does not change.

## The target

| | |
|---|---|
| MCU | WCH **CH32X035G8U6** (QFN28), RISC-V RV32IMAC at 48 MHz; marking and `wchisp` report agree |
| Program link origin | **0x3000** (the CHGame board package's `link_chgame_app.ld`, unchanged) |
| Largest program | **50,944 B** (0x3000-0xF6FF). Games that save keep it at 50,432 B or less ([../docs/platform.md](../docs/platform.md)) |
| Metadata page | 0xF700, written by the bootloader **last**, after the image's CRC checks out |
| RAM | 20 KB, of which the first 16 B (0x20000000) are the retained boot-request block; the board package's linker script reserves them. Stack 2 KB. |
| Boot region | 0x0000-0x2FFF belongs to the bootloader. Nothing in a CHG file can write there: the destination is always 0x3000, and the flash writer checks every page's address itself. |
| Layout id | `0x003000F7` (program at 0x3000, metadata at 0xF700) |

Build exactly as for an upload: the board package `CHGame:ch32v` (0.2.4 or
later); the games use
`opt=oslto,rtlib=nano,periph=game,usb=uploadonly`. From 0.3.0 every build
also writes the CHG file, `<sketch>.ino.chg`, beside the `.bin` (below).

## The file (format version 1)

The file is the 512-byte header followed by the payload, and optionally the
game's picture and its record. The payload is the `.bin`, padded with 0xFF to a multiple
of 4, which is exactly the image `chgame-upload` writes. Integers are
little-endian.

| Offset | Size | Field | Value |
|---|---|---|---|
| 0x000 | 4 | magic | `0x31474843` ("CHG1") |
| 0x004 | 2 | format version | 1 |
| 0x006 | 2 | header bytes | 512 |
| 0x008 | 4 | target id | `0x35335843` ("CX35": CHGame, CH32X035G8U6) |
| 0x00C | 4 | layout id | `0x003000F7` |
| 0x010 | 4 | payload bytes | 4 to 50,944, a multiple of 4 |
| 0x014 | 4 | payload CRC-32 | CRC-32/ISO-HDLC (zlib's `crc32`) of the payload |
| 0x018 | 4 | app version | free for you |
| 0x01C | 4 | flags | 0 |
| 0x020 | 32 | title | ASCII, NUL-padded; the menu shows the first 19 characters |
| 0x040 | 16 | author | ASCII, optional |
| 0x050 | 8 | version | ASCII, optional (e.g. "1.2") |
| 0x060 | 12 | picture | offset, bytes, CRC-32 of the game's picture for the visual menu (below); 0 = none |
| 0x06C | 12 | record | offset, bytes, CRC-32 of the game's record, for backups (below); 0 = none |
| 0x078 | ... | reserved | 0 |
| 0x1FC | 4 | header CRC-32 | CRC-32/ISO-HDLC of bytes 0x000-0x1FB |
| 0x200 | payload bytes | payload | |

**The CRC.** It is the same CRC, over the same padded bytes, that the
bootloader stores in the metadata page after a USB upload. So the menu can
tell that the program in flash is the one in a CHG file (same length and
CRC), and marks it as installed whichever way it got there. The
`app_version` field is not used for that.

**The picture.** The visual menu shows it while the game is selected
(card.md: "How the visual menu reads the card"). It is 8,704 bytes in
MENU.BG's encoding (card.md, steps 5 and 7: `CHB1`, a 16-colour palette, 128
rows of 64 bytes), at an offset that is a multiple of 512, after the payload
and below 128 KiB; the gap before it is 0. The field names its offset, its
size (8,704) and its CRC-32; a reader may skip the CRC. The install never
reads it: a file with a damaged or missing picture still installs, and the
menu shows its no-picture screen instead. `tools/chgpack.py pack --image`
adds one (any 128x128 PNG that follows the picture rule, or a `.PIC` file),
`verify` and `info` check and show it, and `chgame cart prepare` writes the
game's `cartImage` there. Menus before the visual one ignore it.

**Checks.** The bootloader checks, in this order, with nothing erased yet:
1. magic;
2. header CRC;
3. format version and header size;
4. target and layout ids;
5. payload size against the file size;
6. that the payload is not a bootloader image (signature `0x4C424843` "CHBL"
   at payload offset 8, where WCH's startup puts a reserved 0);
7. then the CRC of the whole payload.

Only then does it erase anything. Checks 1 to 5 report one code (the menu
shows a file that fails them greyed out, as ERROR 5);
[platform/bootloader](../platform/bootloader) has the transaction and its
tests. `tools/chgpack.py verify` reports which check failed.

**The record** (since 2026-10-06). What a backup needs to make the
game's cart again from the card alone (card.md, "Backing up a card"): the
game as its cart describes it, and the files it put on the SD card. No menu
reads it, and the install ignores it, as it does the picture: a file with a
damaged record still installs, and every bootloader, older ones included,
takes a file that has one. Runtime preparation writes one in every CHG
file; `chgpack.py pack` and `chgame-upload pack` (*Export Compiled Binary*)
do not, having no cart to describe.

- **Where:** at the first multiple of 512 after the payload, or after the
  picture if there is one, the gap 0; at most 1 MiB. The field names its
  offset, its size and its CRC-32. A reader checks all three; a record that
  fails them makes it a file without a record.
- **What:** UTF-8 JSON, one object:

  | Key | | Value |
  |---|---|---|
  | `chgRecord` | required | `1`. A reader that meets another number treats the file as one without a record |
  | `game` | required | the game's entry in the cart's `info.json` (chgame.md), with only these keys: `id` and `title` (both required, both following chgame.md's rules), `version`, `author`, `description`, `genre`, `license`, `url`, `sourceUrl`, `buttons`. Not `folder`: where the file sits on the card says that, so a file moved by hand goes with its new folder. Not `binaries`, `cartImage`, `licenseFiles` or `sdcard`, given below; not `screenshots`, left out for their size |
  | `binaryBytes` | required | the binary's length before padding (the payload is the binary padded with 0xFF to a multiple of 4) |
  | `cartImage` | | the game's `cartImage` as the cart held it: the PNG's bytes in base64. (The picture above is that PNG converted, and cannot always give it back) |
  | `licenseFiles` | | `{"LICENSE": base64, ...}`: the game's licence files, each under its file name |
  | `sdcard` | | the game's SD files, sorted by path: `[{"path": "CHCW/BONUS.CWD", "bytes": 18432, "crc32": "1a2b3c4d"}]`, the CRC-32 as for the payload, in 8 lower-case hex digits |

- **Written** so that two implementations write the same bytes: keys sorted
  by code point, no spaces, the keys a game lacks left out; in strings
  `\"`, `\\`, `\b`, `\f`, `\n`, `\r`, `\t`, the other characters below
  U+0020 as `\u00XX`, and every character above U+007F as `\uXXXX` in
  lower-case hex (two of them for one beyond U+FFFF), so the record is
  ASCII. Python's `json.dumps(r, sort_keys=True, separators=(",", ":"))`
  writes exactly this.

`chgpack.py verify` and `info` check it and show `[record]`.

## Making one

The usual way is not by hand: `chgame cart prepare` (or `chgame card`, or
`chgame cart deploy`) writes the CHG files of a `.chgame` with everything
else the menu needs (card.md). By hand:

```
python tools/chgpack.py pack build/release/MyGame.ino.bin MYGAME.CHG --title "MY GAME" [--author ME] [--version 1.0] [--image cart.png]
python tools/chgpack.py verify MYGAME.CHG
python tools/chgpack.py info E:\        # list the CHG files on a card (or a folder, or a FAT image)
```

`chgpack.py` needs only Python 3. With the board package 0.3.0 or later
nothing else is needed: every build runs `chgame-upload pack` (the uploader
the package installs; `-title`, `-author`, `-gameversion`, `-out`) and
*Sketch > Export Compiled Binary* copies `MyGame.ino.chg` into the sketch's
`build/` folder, titled with the sketch's name in capitals. The two tools
make the same bytes (the uploader's shared test vectors check it). Copy the
file into the card's `GAMES/` folder, or one of its folders, with an 8.3
file name.

## What a program may assume

- **It always starts from a real reset**, never from a jump out of the menu.
  The bootloader leaves a RUN request and resets, so every peripheral, the
  SD card's SPI bus and the panel are in their reset state. Initialise them
  as on a cold boot (CHGfx and CHSd already do).
- **The SD card may have been left mid-command** by whatever ran before.
  CHSd's `sd::init()` starts from CMD0, which is enough after the bootloader.
- **Returning to the menu.** Call `NVIC_SystemReset()`. With no request in
  the retained block, the bootloader shows the menu (never the card's
  launch game: that is for power-on only). The platform's gesture for it is
  **START held for 3 s**. The games on the CHGame library get it from it:
  `chgame.exitToMenu()` does the same on purpose, and
  `chgame.startExits = false` turns the hold off. A new game should keep the
  gesture, so players can leave any game the same way.
- **Uploading.** The board package's 1200-baud touch writes the USB request
  (`0x43484742` "CHGB" and its complement at 0x20000000) and resets. That is
  unchanged.
- **Saving.** The flash pages at 0xF500 and 0xF600 survive installs unless a
  program is large enough to cover them. They are shared by every program:
  give yours a unique magic in its save records
  ([../docs/status.md](../docs/status.md)).
