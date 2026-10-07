# spec/: the contract

What other projects build against: the CHGame's game format, and what a
CHGame does with it. The web emulator and its cart builder and uploader
read and write these files; this repository's Python tools are the
reference implementation, and the fixtures here are the test both must
pass.

```
.chgame  ->  games and their files  ->  runtime preparation  ->  SD card + flash  ->  CHGame (or emulator)
(chgame.md)    (tools/chcart/model.py)    (card.md, runtime.py)     (chg.md, card.md)     (bootloader v2)
```

| File | What it is | Who needs it |
|---|---|---|
| [chgame.md](chgame.md) | The `.chgame` format, version 1: the ZIP, `info.json`, devices (the boards and their revisions, how they are named), the rules and their codes | anyone reading or writing carts |
| [card.md](card.md) | Runtime preparation and the SD card's layout v2 (`GAMES/`, `MENU.IDX`, `MENU.BG`, the visual menu's `COVER.PIC` and `SYSTEM.PIC`), how both menus read it, the deploy rules, and backing a card up into a cart | card builders, uploaders, emulators |
| [chg.md](chg.md) | The CHG file the menu installs: a program behind a 512-byte header, then its picture and its record | the same, and anyone writing a CHG file by hand |
| [info.schema.json](info.schema.json) | JSON Schema for `info.json`: its shape, for editors and quick checks. chgame.md has rules a schema cannot say (files, pictures, SD paths, the cart as a whole) | tools, editors (`"$schema"`) |
| [assets/menu-default.png](assets/menu-default.png) | The list menu's background runtime preparation uses when a cart has none | card builders |
| [assets/cover-default.png](assets/cover-default.png), [about-default.png](assets/about-default.png), [system/](assets/system) | The visual menu's defaults: the cover, the about page and its own screens (card.md, step 7) | card builders |
| [fixtures/](fixtures) | Carts, good and bad, with what reading and preparing each must give; cards, with what backing each up must give | every implementation |
| [../platform/board/docs/protocol.md](../platform/board/docs/protocol.md) | The upload protocol over USB CDC (the `CG` frames, `HELLO`, `BEGIN`/`WRITE`/`END`/`RUN`/`ABORT`), its versions, and the host conventions: the 1200-baud touch, the one USB identity across the switch (`platform/bootloader/shared/chgame_usb_identity.h`), the image rules, the save pages. Kept beside the bootloader rather than here, but a contract all the same: the web emulator's uploader is its fourth implementation | uploaders (the web project's included) |

**The reference implementation** is [tools/chcart](../tools/chcart)
(`chgame cart ...`; `pip install -e .` in the repository root). Its tests,
`python -m unittest discover -s tools/chcart/tests`, include the fixtures.

**Versions.** chgame.md's `schemaVersion` (1) and card.md's layout version
(2, read by the bootloader with BOOT_VERSION 3) change only when an old
reader would go wrong. Adding a device, an optional key or a fixture does
not change them. `menu.systemImages` (2026-10-06: a cart's own versions of
the visual menu's screens, `assets/system/` being the defaults) is such a
key; a reader from before it shows the defaults. So is the CHG file's record
(2026-10-06): no bootloader reads it, and a reader from before it sees a
longer file.

**`screenshots` left the format** (2026-10-07, before any release carried
it): a cart is for the device and the tools that prepare a card, and
gameplay GIFs made a cart of twenty games 18 MB where 2 MB holds what the
card needs. A reader meets the key in an older cart as an unknown one
(a warning) and drops it with its files; writers must not write it.

**The uploader's side of the contract** (2026-10-06, confirmed with the web
emulator project): its browser uploader uses the existing upload protocol
and changes nothing in the bootloader. It frames with `CG`; `HELLO` must
show upload mode, bootloader version 3 or later and an application base of
`0x3000`, and the sizes come from the answer; `BEGIN` carries the padded
length and CRC-32, `WRITE` the offsets, `END` verifies, `RUN` starts, and
`ABORT` is sent on failure; images are at most 50,944 B, its SD-over-serial
sketch at most 50,432 B so both shared save pages stay outside it; the
bootloader is entered by the 1200-baud/DTR touch and found again after the
USB reconnection, ordinary connections open at 115200; an older bootloader
is sent to the board package's upgrade procedure, the website flashes no
bootloaders. protocol.md's "Host conventions" says what each of these means
on the device.

**Board revisions** (2026-10-07). The handheld will get revisions whose
pins differ, so a game built for one does not run on the next. Each is a
device in chgame.md's table, named `rev<n>`, with a four-character target
id: `rev0` is `CX35`, as it always was, and `rev1`, reserved until its
pinout is settled, is `CGR1` (chgame.md, "Devices and revisions": the
naming rule for every later board). What it means for the web project:
- **Reading carts.** A binary for a device the reader does not know (a
  reserved one, or a board registered later) is now the warning
  `unknown-device`: the reader uses the rest of the cart and keeps that
  binary when it rewrites it. It used to be the error `bad-device`, which
  would have made every existing reader refuse a cart carrying rev0 and
  rev1 builds. `bad-device` is now a malformed device name or two binaries
  for one device. Fixtures: `bad/bad-device` breaks the name rule (`REV0`),
  and `good/devices` holds a game with a `rev1` binary and one with an
  `other-board` binary beside their rev0 ones.
- **Cards and CHG files.** A card is prepared for one device, and its CHG
  files carry that device's target id. Nothing changes for rev0: its bytes
  are those of before.
- **Uploading.** A bootloader built for a board after rev0 adds a field at
  offset 30 of `HELLO`: its target id. A reply without it comes from rev0.
  A host ignores bytes past the fields it knows, so an uploader written
  before this keeps working. An uploader that knows which device a binary
  is for refuses a board whose `HELLO` names another (protocol.md, "Which
  board"). Bootloaders for later boards also carry their id at offset 0x14
  of their image, for uploads of a bootloader.
- **The emulator** emulates rev0. When rev1 is defined, an emulator of rev1
  takes the `rev1` binaries, and never another board's.

**Backing a card up** (2026-10-06, asked for by the web emulator project,
whose cart builder reads carts back from cards). Each CHG file that runtime
preparation writes carries the game's **record** (chg.md, field 0x06C):
the game's `info.json` entry, its cart image and licence files as the cart
held them, the binary's length, and every SD file it put on the card with
its size and CRC-32. A backup reads the card alone and makes the cart again
(card.md, "Backing up a card"; `chgame cart backup`): one game or the whole
card, its SD files included, and a card as preparation wrote it comes back
as a cart that prepares the same card, byte for byte. Files that changed or
went missing are flagged, and a CHG file without a record (*Export Compiled
Binary*'s, or one written before) comes back from its header and picture,
its SD files named by hand.

The web project first proposed a sidecar file per game (`GAMES/<NAME>.RES`).
The record does the same job from inside the CHG file, which settles what a
sidecar would have to guard against: it cannot go stale or be separated
from its game (copied, moved, renamed or replaced by a deploy, the record
goes with it, under the header's CRC), it needs no identity beyond the file
itself, and it adds no file to `GAMES/`. No bootloader reads it, older ones
included (they check only that the file holds the payload). Nothing in it
names saves: CHSd cannot write, so a game's SD files are read-only, and one
that has changed is backed up as the card has it, with a warning. The cost
is the CHG files' size (about 21 KB each on the casino card, mostly the
Apache licence in base64) and, once, every fixture's prepared CHG bytes.

**Who changes what.** The bootloader's side of card.md is
[platform/bootloader](../platform/bootloader) (`shared/chgame_card.h`,
`src/card.c`, `src/menu.c`, `src/visual.c`). A change to the card's layout is made there, in
`tools/chcart/runtime.py`, in card.md and in the fixtures together, and the
bootloader's PC tests (`test/native`, which boot the menu on cards that
`runtime.prepare()` makes) must pass.
