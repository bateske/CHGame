# The bootloaders Burn Bootloader offers

*Tools > Bootloader* chooses one, *Tools > Programmer* how it is written
(**CHGame USB**: through the CHGame bootloader already on the board, no
driver; **WCH factory ISP**: hold BOOT on power-up, needs the driver), and
*Tools > Burn Bootloader* writes it. All four keep the same memory map and
upload protocol, so a sketch built for one runs under the others.

| Menu entry | File | What it is |
|---|---|---|
| SD Game Menu (Rainbow) | `chgame_sdboot.bin` | the menu that installs games from the SD card, USB upload, bootloader update over USB (version 2); black and grey, the highlight cycling through the colours |
| SD Game Menu (Plain) | `chgame_sdboot_plain.bin` | the same menu, black and grey with a gold highlight, no animation |
| SD Game Menu (Casino) | `chgame_sdboot_casino.bin` | the same menu on green felt with gold |
| USB Only | `chgame_boot_nomenu.bin` | the same code without the menu and the card (version 2) |

They are copies of `platform/bootloader/release/` in the CHGame repository,
put here by `platform/bootloader/tools/dist.sh` (the three menus are
`build.sh release --theme=rainbow|plain|casino`); the sources and what each
does are in `platform/bootloader`. The 0.2.4 bootloader (version 1) is no
longer offered: every bootloader here accepts the same sketches and adds
the bootloader update over USB.
