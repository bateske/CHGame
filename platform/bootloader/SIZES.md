# Bootloader size record

All numbers are measured, not estimated. The toolchain is the board
package's riscv-none-embed-gcc 8.2.0. Flags: `-Os -flto -ffunction-sections
-fdata-sections -msmall-data-limit=8 -msave-restore -fno-jump-tables`, and
`--gc-sections` at link time. `./build.sh <mode>` prints the same table,
from `tools/size_report.py`.

**The reservation:** 12,288 B at 0x0000-0x2FFF, unchanged, so `APP_START`
stays at 0x3000 and every game keeps its 50,944 B. The size gate (gate A) is
a boot image of at most 12,288 B with at least 256 B to spare.

## Current builds (2026-10-03, menu v2)

| Build | `.text` | `.ramfunc` | `.data` | Boot image | Free | `.bss` | RAM in use |
|---|---|---|---|---|---|---|---|
| **release** (menu + USB upload + self-update) | 11,336 | 596 | 84 | **12,016** | **272** | 14,628 | 17,372 |
| locked (menu + USB upload) | 11,120 | 496 | 80 | 11,696 | 592 | 14,628 | 17,268 |
| nomenu (USB upload + self-update, for HW2a) | 4,728 | 596 | 76 | 5,400 | 6,888 | 984 | 3,720 |
| app (the menu as a program at 0x3000, dry run) | 6,496 | 0 | 16 | 6,512 | - | 13,504 | 15,584 |

The colour themes (`--theme=plain`, `casino`) went with menu v2: the look
is the card's `MENU.BG` now.

Notes:
- `.text` includes `.init` and the vector table. `.ramfunc` and `.data`
  count twice: in flash as their load image, and in RAM.
- RAM in use is the 16 B retained block, `.ramfunc`, `.data`, `.bss` and the
  2 KB stack, out of 20,480 B.
- The release `.bss` is mostly the menu's framebuffer (8,192 B), its game
  table (128 x 32 B), the colour wheel's row of 255 colours (510 B), one
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
- **The fallback look's title at scale 2, about 40 B.** It shows only on a
  card without `MENU.BG`, and on the USB notice.
- **Nested folders, about 30 B.** One level would do for most carts.
- **The INSTALLED PROGRAM row, about 60 B.** An uploaded sketch that is not
  on the card would then have to be found another way (a key).
- **The locked build** drops self-update: 324 B.
