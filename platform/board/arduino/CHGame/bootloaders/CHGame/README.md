# The bootloaders Burn Bootloader offers

*Tools > Bootloader* chooses one, *Tools > Programmer* how it is written
(**CHGame USB**: through the CHGame bootloader already on the board, no
driver; **WCH factory ISP**: hold BOOT on power-up, needs the driver), and
*Tools > Burn Bootloader* writes it. All three keep the same memory map and
upload protocol, so a sketch built for one runs under the others.

| Menu entry | File | What it is |
|---|---|---|
| SD Text Menu (Rainbow) | `chgame_sdboot.bin` | the menu that installs games from the SD card (folders, the card's own picture and order, a game started at power-on), USB upload, bootloader update over USB. The selection bar, the boxes and the picture's magenta parts turn through the rainbow |
| SD Text Menu (Static) | `chgame_sdboot_static.bin` | the same menu with nothing turning: those parts in the picture's own magenta, as painted |
| SD Graphic Menu (Rainbow) | `chgame_sdvisual.bin` | the same card shown one picture at a time and no text, as the Arduboy FX does: the card's cover at power-on, then each game's picture (its box art); LEFT/RIGHT between folders, UP/DOWN through a folder, A plays, B goes back, B at the top explains the keys. Pictures slide in from the side pressed (up/down within a folder, left/right to the folder beside), A and B into and out of a folder fade; the install bar and the pictures' magenta parts turn through the rainbow |
| SD Graphic Menu (Static) | `chgame_sdvisual_static.bin` | the visual menu with nothing turning |
| USB Only | `chgame_boot_nomenu.bin` | the same code without the menu and the card |

They are copies of `platform/bootloader/release/` in the CHGame repository,
put here by `platform/bootloader/tools/dist.sh`; the sources and what each
does are in `platform/bootloader`. The menus' look is the card's: a card
prepared by the tools (`chgame cart prepare`, `chgame card`) carries the
list menu's background in `GAMES/MENU.BG`, and the visual menu's pictures
(`COVER.PIC`, `SYSTEM.PIC`, a picture in each game's CHG file; spec/card.md,
docs/visual-menu.md). Switch between them at any time with Burn Bootloader:
the card and the installed game stay as they are. The 0.2.4 bootloader is no
longer offered: every bootloader here accepts the same sketches and adds the
bootloader update over USB.
