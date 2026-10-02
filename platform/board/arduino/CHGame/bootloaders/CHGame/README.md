# The bootloaders Burn Bootloader offers

*Tools > Bootloader* chooses one, *Tools > Programmer* how it is written
(**CHGame USB**: through the bootloader already on the board, no driver;
**WCH factory ISP**: hold BOOT across a power cycle), and *Tools > Burn
Bootloader* writes it. All three keep the same memory map and upload
protocol, so a sketch built for one runs under the others.

| Menu entry | File | What it is |
|---|---|---|
| SD game menu (default) | `chgame_sdboot.bin` | the menu that installs games from the SD card, USB upload, bootloader update over USB (version 2) |
| USB only, no menu | `chgame_boot_nomenu.bin` | the same code without the menu and the card (version 2) |
| Classic 0.2.4 | `chgame_bootloader.bin` | the bootloader of board package 0.2.4 (version 1) |

The first two are copies of `platform/bootloader/release/` in the CHGame
repository, put here by `platform/bootloader/tools/dist.sh`; the sources and
what each does are in `platform/bootloader`. The third is the binary
released with 0.2.4, kept as it was.
