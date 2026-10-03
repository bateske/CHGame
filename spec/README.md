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
| [chgame.md](chgame.md) | The `.chgame` format, version 1: the ZIP, `info.json`, devices, the rules and their codes | anyone reading or writing carts |
| [card.md](card.md) | Runtime preparation and the SD card's layout v2 (`GAMES/`, `MENU.IDX`, `MENU.BG`), how the menu reads it, the deploy rules | card builders, uploaders, emulators |
| [chg.md](chg.md) | The CHG file the menu installs: a program behind a 512-byte header | the same, and anyone writing a CHG file by hand |
| [info.schema.json](info.schema.json) | JSON Schema for `info.json`: its shape, for editors and quick checks. chgame.md has rules a schema cannot say (files, pictures, SD paths, the cart as a whole) | tools, editors (`"$schema"`) |
| [assets/menu-default.png](assets/menu-default.png) | The background runtime preparation uses when a cart has none | card builders |
| [fixtures/](fixtures) | Carts, good and bad, with what reading and preparing each must give | every implementation |

**The reference implementation** is [tools/chcart](../tools/chcart)
(`chgame cart ...`; `pip install -e .` in the repository root). Its tests,
`python -m unittest discover -s tools/chcart/tests`, include the fixtures.

**Versions.** chgame.md's `schemaVersion` (1) and card.md's layout version
(2, read by the bootloader with BOOT_VERSION 3) change only when an old
reader would go wrong. Adding a device, an optional key or a fixture does
not change them.

**Who changes what.** The bootloader's side of card.md is
[platform/bootloader](../platform/bootloader) (`shared/chgame_card.h`,
`src/menu.c`). A change to the card's layout is made there, in
`tools/chcart/runtime.py`, in card.md and in the fixtures together, and the
bootloader's PC tests (`test/native`, which boot the menu on cards that
`runtime.prepare()` makes) must pass.
