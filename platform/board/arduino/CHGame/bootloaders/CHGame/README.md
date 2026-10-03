# The bootloaders Burn Bootloader offers

*Tools > Bootloader* chooses one, *Tools > Programmer* how it is written
(**CHGame USB**: through the CHGame bootloader already on the board, no
driver; **WCH factory ISP**: hold BOOT on power-up, needs the driver), and
*Tools > Burn Bootloader* writes it. All three keep the same memory map and
upload protocol, so a sketch built for one runs under the others.

| Menu entry | File | What it is |
|---|---|---|
| SD Game Menu (Rainbow) | `chgame_sdboot.bin` | the menu that installs games from the SD card (folders, the card's own picture and order, a game started at power-on), USB upload, bootloader update over USB. The selection bar, the boxes and the picture's magenta parts turn through the rainbow |
| SD Game Menu (White) | `chgame_sdboot_white.bin` | the same menu with those parts white |
| USB Only | `chgame_boot_nomenu.bin` | the same code without the menu and the card |

They are copies of `platform/bootloader/release/` in the CHGame repository,
put here by `platform/bootloader/tools/dist.sh`; the sources and what each
does are in `platform/bootloader`. The menu's look is the card's: a card
prepared by the tools (`chgame cart prepare`, `chgame card`) carries a
background in `GAMES/MENU.BG` (spec/card.md). The 0.2.4 bootloader is no
longer offered: every bootloader here accepts the same sketches and adds the
bootloader update over USB.
