# Bootloader size record

All numbers are measured, not estimated. The toolchain is the board
package's riscv-none-embed-gcc 8.2.0. Flags: `-Os -flto -ffunction-sections
-fdata-sections -msmall-data-limit=8 -msave-restore -fno-jump-tables`, and
`--gc-sections` at link time. `./build.sh <mode>` prints the same table,
from `tools/size_report.py`.

**The reservation:** 12,288 B at 0x0000-0x2FFF, unchanged, so `APP_START`
stays at 0x3000 and every game keeps its 50,944 B. The size gate (gate A) is
a boot image of at most 12,288 B with at least 256 B to spare; for the
visual menu, by the owner's choice (2026-10-03, its key map), 192 B
(`build.sh` passes `--margin 192` for `--ui=visual`).

## Current builds (2026-10-06: power-on, launch, the static colour, the pins)

| Build | `.text` | `.ramfunc` | `.data` | Boot image | Free | `.bss` | RAM in use |
|---|---|---|---|---|---|---|---|
| **release** (list menu + USB upload + self-update; rainbow) | 11,240 | 596 | 84 | **11,920** | **368** | 17,704 | **20,448** |
| release `--style=static` | 11,036 | 596 | 84 | 11,716 | 572 | 17,564 | 20,308 |
| **release `--ui=visual`** (the visual menu; rainbow) | 11,404 | 580 | 76 | **12,060** | **228** | 17,536 | **20,256** |
| release `--ui=visual --style=static` | 11,220 | 580 | 76 | 11,876 | 412 | 17,524 | 20,244 |
| locked (list menu + USB upload) | 11,024 | 496 | 80 | 11,600 | 688 | 17,704 | 20,344 |
| locked `--ui=visual` | 11,208 | 484 | 76 | 11,768 | 520 | 17,532 | 20,156 |
| nomenu (the USB-only bootloader: USB upload + self-update; also HW2a) | 4,668 | 596 | 76 | 5,340 | 6,948 | 984 | 3,720 |
| app (the list menu as a program at 0x3000, dry run) | 6,392 | 0 | 16 | 6,408 | - | 16,580 | 18,660 |
| app `--ui=visual` (the visual menu's dry run) | 6,816 | 0 | 8 | 6,824 | - | 16,536 | 18,608 |

**A later board** (2026-10-07: `CHBOOT_BOARD_TARGET`, README "Changes of
2026-10-07") costs 16 B, all of it `HELLO`'s board field. The board word in
the image fills a reserved vector slot and costs nothing. Measured with
rev1's id (`0x31524743`) and rev0's pins: list 11,936 B (352 free), visual
12,076 B (20 B under its 192 B margin). The rev0 builds above are unchanged
to the byte.

Both faces share the card's code (`src/card.c`); `--ui=` picks `src/menu.c`
or `src/visual.c`. Splitting `card.c` out of `menu.c` left every list build
byte-identical to the one before (the release, static, locked, nomenu and
app binaries all compared equal).

**RAM is full on purpose.** A folder of the menu lists `MENU_MAX_GAMES`
entries (`src/menu.h`), 32 B each, and 240 take what the framebuffer, the
buffers and the 2 KB stack leave: 32 B of the 20,480 are left. Anything that
adds RAM to the menu build lowers that number (every 32 B, one entry). A
folder had 128 until 2026-10-03, then 224, then 240 once the rainbow's
gradient table went.

The colour themes (`--theme=plain`, `casino`) went with menu v2: the look
is the card's `MENU.BG` now.

Notes:
- `.text` includes `.init` and the vector table. `.ramfunc` and `.data`
  count twice: in flash as their load image, and in RAM.
- RAM in use is the 16 B retained block, `.ramfunc`, `.data`, `.bss` and the
  2 KB stack, out of 20,480 B.
- The release `.bss` is mostly the menu's framebuffer (8,192 B), its game
  table (240 x 32 B), one
  512 B sector buffer, the protocol's 512 B frame buffer and its 256 B page
  buffer.
- The binaries, with SHA-256 sums, are in [release/](release). They use the
  default theme (rainbow). Two independent builds give byte-identical files
  (`tools/dist.sh`).

## Milestones

| Step | Boot image | Free | What changed |
|---|---|---|---|
| Shipped 0.2.4 bootloader (CH32SerialBoot 5de3006) | 7,268 | 5,020 | Rebuilt here byte-identical to `chgame_bootloader.bin` |
| Proven trims, no menu | 6,060 | 6,228 | core 0.2.4's direct-register `USB_init`; no `atexit`/`__libc_init_array`; no SPL GPIO/RCC; LED patterns reduced to a 2 Hz blink; `memcpy` no longer pulled in; the shared update path |
| First menu build (with self-update) | 12,104 | 184 | SD + FAT + CHG + install + LCD + font + menu |
| Struct copies without `memcpy` | 11,944 | 344 | The game table is copied as words |
| `-fno-jump-tables` | 11,908 | 380 | The protocol's command switch and the menu's tables |
| Hardware-review fixes | 12,068 | 220 | CRC7 on every SD command and CMD59 to switch CRC checking off; the N_RC gap; SPI1 started on the USB-notice path; B debounced, and the B escape only at power-on (soft-reset flag); the panel field drawn as one counter |
| USB strings as `const` literals | 11,948 | 340 | Manufacturer, product and interface descriptors in flash, not built at start-up (same bytes on the wire) |
| Colour themes, rainbow by default | 12,032 | 256 | The colour wheel and its 40 ms step (+172 B over `plain`). Paid for by: list rows drawn in one pass as 6x10 text cells; the font cut to capitals (-155 B; titles are folded to upper case); the error table without its gap |
| Hardware-run fixes (2026-10-01) | 12,032 | 256 | The B escape tests the power-on flag; a wider box, the progress bar under the title. Constants only |
| Menu v2, first build (2026-10-03) | 12,472 | -184 | The framebuffer, colour 15 as the wheel, MENU.BG, folders, MENU.IDX, launch, START held; `fault.c` and the error texts gone (one ERROR n box), the themes gone. Over the region |
| SPI bytes out of line | 12,416 | -128 | One out-of-line copy of the SPI byte in `lcd.c` and `sd.c`; CASET set once in the panel's set-up |
| Edge cases slimmer | 12,304 | -16 | exFAT no longer told apart from other non-FAT volumes; `chg_check` one code; one place keeps the list scrolled; no font guard for text that is all `' '..'_'` |
| STATUS removed | 12,176 | 112 | A bench diagnostic (BOOT_VERSION 3: ST_ERR_BADCMD) |
| READ removed | 12,008 | 280 | `-verify`'s readback; END's CRC of the flash stays. Gate A passes |
| Tested on cards from the tools | 12,012 | 276 | Keys held at power-on count only after a release again (`k_prev` starts with every key down); a bad file's name shown as stored (`BADFILE CHG`) |
| Review | 12,016 | 272 | The font guard back for characters after `_` (a hand-made folder's 8.3 name, `CARDGA~1`); INSTALLED PROGRAM written by `set_title()` |
| The logo only in the picture; 224 a folder | 11,948 | 340 | No title drawn by the bootloader (the card's picture has the logo; without one the list is on black), so text is never scaled; the game table from 128 entries to 224 (RAM 17,372 to 20,444 B) |
| A solid rainbow; 240 a folder; the White style | 11,900 | 388 | Colour 15 one turning colour, not a gradient (no 510 B table); the table to 240 entries (RAM 20,448 B). `--style=white`: no animation, 11,684 B |
| No games: USB mode; an empty folder | 11,908 | 380 | With nothing to list the menu hands over to USB mode again, as the first menu did (LED, B looks at the card again); in an empty folder only B works (it was a trap, and UP/A used stale rows) |
| `card.c` split out of `menu.c` | 11,908 | 380 | The card's code shared by both faces; every list build byte-identical |
| Visual menu, first build | 12,664 | -376 | Pictures from the card and the CHG files, rows, the folder ring, the about page, the installed game searched for, built-in 16x16 icons, slides both ways, fades, the install dim, error marks. Over the region |
| Visual: fades by halving, vertical slides only | 12,372 | -84 | Fades halve the palette in `send()` instead of scaling it; LEFT/RIGHT fade through black (another folder) instead of sliding sideways; one modal for errors and the about page |
| Visual: 12x12 icons, the launch path in the search | 12,284 | 4 | The launch entry found by the same depth-first walk as the installed game |
| Visual: `lcd_flush` direct, no dim, no error marks | 12,044 | 244 | SYSTEM.PIC gives each error its own picture, so the built-in error icon has no marks; the install bar draws over the picture as it is |
| Visual: one cover lookup, `light()` on the USB path | 11,996 | 292 | Gate A passes. Static 11,744 |
| Visual: pixels as 16-bit frames at 24 MHz | 11,992 | 296 | After the first board run ("pretty damn slow": about 75 ms a screen, 46 instructions a pixel through `px()`, `out()` and the save/restore millicode, each byte awaiting its echo at 12 MHz). `send()` now writes one 16-bit frame a pixel, queued, at 24 MHz, as CHGfx does (`hal_spi_frames()`, `hal_spi_put16()`): about 11 instructions a pixel, some 19 ms a screen, so a slide (4.5 screens) about 90 ms and a folder change (12) about 230 ms. Paid for by dropping the rows-with-colour-15 table (`shows[]`, 128 B of RAM too): each 40 ms rainbow step resends the whole picture. Static 11,808 |
| Visual: sideways slides, faster card reads | 12,028 | 260 | The owner's Arduboy habit: LEFT/RIGHT slide the folder beside in from that side (`send()` takes a column window too; +116 B), A and B into and out of a folder, and the cover to the installed game at power-on, still fade. Card reads (+72 B): a block's 512 bytes as 16-bit frames at 24 MHz (the clock CHSd streams at on this board), and a block asked for again into the same buffer is not read again, so following a file's clusters reads its FAT block once instead of at every cluster (about 6 reads saved on the way into a game's picture). Paid for by: the SPI clock changes, the panel's byte and the card's byte through one out-of-line function each (`sd_frames()`, `sd_x()`; -68 B), CASET only per send, and three size flags for this build alone (`build.sh`: `-fno-guess-branch-probability -fno-shrink-wrap -fno-tree-scev-cprop`, -84 B; the pixel and card loops compile as before). Static 11,844 |
| Visual: paced animations | 12,020 | 268 | The owner, after the speed-ups: "so good now it's actually too fast". A slide in 16 steps (it was 8), each followed by 6 ms; a fade's 6 steps each way followed by 25 ms (`LCD_SLIDE_STEPS`, `LCD_SLIDE_STEP_MS`, `LCD_FADE_STEP_MS` in `lcd.h`, to tune by eye): about 0.25 s a slide and a fade each way. +24 B, paid for by dropping the cache clear in `sd_init()` (every path to a new card goes through a reset or a failed read, which clear it) and a fourth size flag, `-fno-caller-saves` (the loops again unchanged). Static 11,840 |
| Visual: the installed game's stripe | 12,020 | 268 | The owner found the 4x4 red chip hard to see. A one-pixel border round the picture would cost +56 B (four `lcd_fill()` calls) or +64 B (one loop over the framebuffer); a stripe along the top, rows 0-1 the whole width, is the same one `lcd_fill()` as the chip, so 0 B in the rainbow style: colour 15 there (it turns with the rest), colour 11 (#FFF4D6) in the static style (+4 B: a constant that does not fold). Static 11,844 |
| Visual: the owner's key map | 12,056 | 232 | START does nothing; SELECT goes to the cart's cover from anywhere and at the root shows the about page; B at the root or in a genre folder goes to the cart's cover, and on it shows the about page; A on the cart's cover shows the installed program's picture, where only A (run) and B (back) count (+104 B; the dry run now leaves on START). Paid for, by the owner's choice: the repeat-read card cache (-40 B) and the 16-bit card reads (-36 B) are gone (card reads as the list menu's: a byte at a time at 12 MHz), and gate A's margin for this build is 192 B instead of 256. Static 11,868 |
| Visual: the installed game's border | 12,080 | 208 | The owner asked for a one-pixel border round the picture instead of the stripe: four `lcd_fill()` calls, +52 B (a loop of two, or one pixel at a time, came out the same or larger). Paid for by a fifth size flag for this build, `-fno-tree-vrp` (-28 B; the pixel and card loops identical instruction for instruction), and 24 B of the 40 left under the 192 B margin. Static 11,896 |
| Power-on on the cover; the launch game never installs by itself; LEFT/RIGHT only where there is somewhere to go (2026-10-06) | 12,060 | 228 | The owner, after the cover-art work. The visual menu stays on the cover at power-on (the search for the installed game still runs behind it, for the stray row; A on the cover shows it): the fade to the installed game and the launch game's 1 s hold and `start()` call went. A launch game that is installed starts before the panel is lit (`boot_reset()` straight from the seek); one that is not waits on its picture after the cover (a second `seek()`). `flip()` reports whether it moved, so LEFT/RIGHT at `GAMES/` without folders do nothing (+16 B). Paid for, and 20 B more, by `flush_all()`: one out-of-line copy of `lcd_flush(0, LCD_H)`'s two constants for its six call sites (-36 B). Static 11,876. The list menu's launch loop became `sel = n` and a `start()` only for a folder or the installed game: 11,920 B (+12); its static build draws colour 15 in the text colour (`background()` sets `lcd_pal[15] = lcd_pal[11]` after either palette): 11,716 B (+32). The USB-only build's `hal_pins_init()` sets up the LED alone: 5,340 B (-60). The buzzer pin is left floating in every build (0 B) |

## Where the visual menu's bytes go

From `./build.sh release --ui=visual --nolto` (the same caveats as below):
`visual.c` 2,294 B (pictures, rows, the ring, the search, install, the
built-in screens with their 5 icons of 24 B), `card.c` 1,426 B, `lcd.c`
951 B (no font, no `lcd_text`; the shaded, offset `send()` and the slide).
Against the list build's release image the visual one drops the font (320
B), `lcd_text` (122), `draw_list` (212), `background` (208), `box` and
`text_c` (136) and the strings, and adds the picture loader (160), `show`
(156), `icon` (126) and its icons (96), `send` (+72 over the list's flush),
the search (132), `enter`/`leave` (140) and the fades.

**If bytes are needed in the visual build:** the slide (about 60 B: a cut
to plain flushes), the installed chip (14 B), the about page (about 40 B).

## Where the release bytes go

There is no per-object split with LTO: everything is attributed to the LTO
partitions. The split below is from `./build.sh release --nolto`, which is
about 450 B larger and does not fit the reservation. It is linked against a
16 KB analysis copy of the script and must never be flashed.

| Object | Bytes | |
|---|---|---|
| menu.c | 3,101 | the card's tree (scan, MENU.IDX, sort), the background, the list, keys, folders, launch, boxes |
| proto.c | 1,468 | USB upload protocol, self-update commands |
| lcd.c | 1,299 | ST7735 set-up table, the framebuffer's flush through the palette and the colour wheel, fill, text; includes the 320 B font (capitals) |
| wch_usbcdc_handler.c + _cdc.c + _descr.c | 1,968 | USB CDC device |
| fat.c | 808 | FAT16/FAT32 |
| sd.c | 750 | SD SPI driver, CRC7 on every command |
| flash.c | 694 | RAM-resident flash writer (the `.ramfunc` load image included) |
| startup | 376 | WCH startup with the CHGame changes |
| install.c | 364 | two-pass install |
| boot.c | 368 | boot decision, USB mode, B escape, START at power-on |
| update.c | 254 | the shared update transaction |
| the rest | ~720 | sys, chg, crc32, crc16, usb, appmeta, bootreq, jump, `-msave-restore` helpers, SystemInit |

## The size audit

The release map contains:
- no `memcpy`, `memset` or `printf`;
- no libgcc division helpers (RV32IMAC divides in hardware);
- no jump tables;
- only one library routine: `-msave-restore`'s register save/restore.

## If bytes are needed later

Largest first:
- **Nested folders, about 30 B.** One level would do for most carts.
- **The INSTALLED PROGRAM row, about 60 B.** An uploaded sketch that is not
  on the card would then have to be found another way (a key).
- **The locked build** drops self-update: 324 B.
