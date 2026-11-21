# The bootloaders Burn Bootloader offers

*Tools > Bootloader* chooses one, *Tools > Programmer* how it is written
(**CHGame USB**: through the CHGame bootloader already on the board, no
driver; **WCH factory ISP**: hold BOOT on power-up, needs the driver), and
*Tools > Burn Bootloader* writes it. All five keep the same memory map and
upload protocol, so a sketch built for one runs under the others on the
same board.

| Menu entry | File | What it is |
|---|---|---|
| SD Text Menu (Rainbow) | `chgame_sdboot.bin` | the menu that installs games from the SD card (folders, the card's own picture and order, a game started at power-on), USB upload, bootloader update over USB. The selection bar, the boxes and the picture's magenta parts turn through the rainbow |
| SD Text Menu (Static) | `chgame_sdboot_static.bin` | the same menu with nothing turning: those parts in the menu's text colour, matching the titles |
| SD Graphic Menu (Rainbow) | `chgame_sdvisual.bin` | the same card shown one picture at a time and no text, as the Arduboy FX does: the card's cover at power-on, then each game's picture (its box art; the cover stays until a key: A shows the installed game); LEFT/RIGHT between folders, UP/DOWN through a folder, A plays, B goes back, B at the top explains the keys. Pictures slide in from the side pressed (up/down within a folder, left/right to the folder beside), A and B into and out of a folder fade; the install bar and the pictures' magenta parts turn through the rainbow |
| SD Graphic Menu (Static) | `chgame_sdvisual_static.bin` | the visual menu with nothing turning |
| USB Only | `chgame_boot_nomenu.bin` | the same code without the menu and the card, for a board built without an SD card: it drives the LED and USB and leaves every other pin high-Z (the card's and the panel's pins are free for other circuits). USB mode by the 1200-baud touch, or when no program is installed |

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

## One folder per board

The files above, in this folder, are **CHGame Rev0**'s. **CHGame Rev1**'s
(Rev 1.5 uses them too) are in `rev1/`, under the same five names: the same
menus and protocol, built for Rev1's pins (`platform/bootloader/build.sh
--board=rev1`) and copied there by `dist.sh`. Each board's Bootloader menu
(`boards.txt`) offers only its own folder. They are not interchangeable:
another board's bootloader drives this board's buttons as outputs.
chgame-upload refuses one: it checks the image's board word against the
board selected in the IDE (`-device`), and over USB also against the board
the bootloader's HELLO reports; through the factory ISP only the check
against the board selected in the IDE stands in the way.
