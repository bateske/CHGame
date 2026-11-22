# Hardware revisions

What to do when the CHGame handheld gets a new board: whether it needs a
new device, what it is called, what already keeps a game or a bootloader
off the wrong board, and the checklist for adding one. The rules
themselves (names, target ids, what readers do) are normative in
[spec/chgame.md, "Devices and revisions"](../spec/chgame.md#devices-and-revisions);
this page is the working guide.

## The registry

| Device | Board | Target id | State |
|---|---|---|---|
| `rev0` | CHGame Rev0, CH32X035G8U6 | `CX35` (`0x35335843`) | released; legacy. Named after its MCU before boards had ids, kept for good |
| `rev1` | CHGame Rev1 and Rev 1.5, CH32X035G8U6 | `CGR1` (`0x31524743`) | **defined** (2026-11-17; reserved since 2026-10-07), in board package 0.4.0: rev0's chip and memory map on other pins, the backlight switched (PB9), the SD card's DI gated ("For rev1: the SD card's DI gate", below). Rev 1.5 is the same device: its power section is for libraries and apps, not a board entry. The current board, and an attempt at a stable pinout: later boards keep these pins where they can. Ran on a Rev 1.5 board on 2026-11-20 (bootloader v4: uploads, a self-update, an install from the card; [roadmap.md](roadmap.md) §8) |
| `rev2` ... `rev9` | | `CGR2` ... `CGR9` | free, in that order |
| `rev10` ... `rev99` | | `CG10` ... `CG99` | free |

The table in spec/chgame.md is the authority: register a board there first.
These stay in step with it (chcart's and the uploaders' tests check):
`tools/chcart/model.py` `DEVICES` / `RESERVED_DEVICES`, `tools/chgpack.py`
`BOARDS` / `RESERVED`, `platform/bootloader/shared/chg_format.h`
`CHG_TARGET_*`, the uploaders' `chg.go` / `chg.py`.

## Does the new board need a new device?

Yes when a binary built for the board before might not run correctly on
it. Typical reasons:

- a pin moved: the screen (CS, DC, RST, SPI), the SD card's CS, a button,
  the buzzer, the LED;
- another MCU, clock or crystal;
- another flash or RAM map, or another bootloader reservation;
- another screen or panel controller.

No when every existing binary runs on it unchanged: another PCB colour,
battery, case or connector, or a part swapped for an equivalent on the same
pins. Such a board keeps its device (it is still `rev0`) and needs nothing
here.

When in doubt, make it a new device. A needless one costs a rebuild per
game. A missing one means games that run but misbehave, with nothing to say
why.

## Names

- **`rev<n>`**: lowercase, the number in decimal, no leading zeros. The same
  name is used everywhere:

  | Where | rev1 |
  |---|---|
  | the `.chgame` device | `rev1` |
  | the board package's FQBN | `CHGame:ch32v:rev1` |
  | the IDE's board menu | CHGame Rev1 (Rev 1.5 boards pick it too) |
  | the variant | `variants/CH32X035/CHGame_Rev1` |
  | the board macro | `ARDUINO_CHGAME_REV1` |
  | the target id (CHG files, `HELLO`, bootloader image) | `CGR1`, `0x31524743` |
  | the bootloader build | `build.sh --board=rev1` (`CHBOOT_BOARD_TARGET=0x31524743`) |
  | the bootloader files | `bootloaders/CHGame/rev1/`, `platform/bootloader/release/rev1/` (rev0's names) |
  | the developer tools | `chgame --board rev1`, `$CHGAME_BOARD`; builds in `build/rev1/` |

- **Numbers go up in release order and are never given twice.** A revision
  abandoned before release keeps its number, unused. Board-level fixes that
  keep binaries compatible do not take a number.
- **Target ids:** `CGR<n>` for rev1-rev9, `CG<nn>` for rev10-rev99. They
  are four ASCII bytes read as a little-endian u32: `CGR1` is
  `0x31524743` (bytes `43 47 52 31`).
- **A board that is not a handheld revision** (another product, a
  development board) gets a name of its own (`a-z`, `0-9`, `-`, starting
  with a letter) and four characters of its own (letters and digits, not
  starting `CG` or `CX`, not one of the formats' magic numbers).
- **Never** reuse a name or an id, give one to another board, or change
  rev0's `CX35`. Do not put the board in a game's title, a cart's title or
  a file name (`CHGAME-REV0`): the device says it, and every tool reads the
  device. **The one exception** is a distribution file that holds one
  board's contents alone: the casino card's zips,
  `CHGame-sdcard-<version>-rev0.zip` and `-rev1.zip`, since a card is for
  one board. Game titles, cart titles and CHG file names never name a
  board; a cart holds every board's binaries under one name.

## What already keeps things on the right board

Done 2026-10-07, ahead of rev1, so that the boards already in use stay as
they are and the tools that read carts today keep working once a rev1
exists; completed with rev1 on 2026-11-17 (board package 0.4.0,
chgame-upload 0.3.0):

| Path | What happens with the wrong board |
|---|---|
| **A `.chgame` cart** | Each binary names its device; a reader picks by name and never falls back to another board's. A reader made before a board exists warns (`unknown-device`), ignores that binary, keeps it when it rewrites the cart, and uses the rest. The repository's carts carry a binary per board (`<id>/rev0.bin`, `<id>/rev1.bin`). |
| **The SD menu** | A CHG file carries its board's target id. A bootloader installs only its own board's: another board's files show greyed under their 8.3 names, and starting one shows ERROR 5, with nothing erased. A card is prepared for one board (`chgame cart prepare --device`, or `chgame --board`), and the casino card comes as one per board. |
| **A sketch over USB** | `chgame-upload flash -device <board>` refuses a board whose `HELLO` names another device. A rev0 bootloader sends no board field, which means rev0. `chgame upload`, `chgame cart flash` / `deploy` and, from board package 0.4.0, Arduino's Upload pass the board. With 0.3.0, which knows Rev0 alone, nothing is checked: a Rev0 build uploaded to a Rev1 drives pins the Rev1 uses as buttons, and switching the board on brings up the menu, from which the right build can be uploaded. |
| **A bootloader over USB** (`selfupdate`, Burn Bootloader with *CHGame USB*) | Refused when the image's board word (offset 0x14; 0 means rev0) names another board than the one running, and, given `-device` (Burn Bootloader from 0.4.0), another board than the one selected. |
| **A bootloader through the factory ISP** (Burn Bootloader and Upload Using Programmer with *WCH factory ISP*, `chgame-upload provision`) | The image's board word is checked against the board selected (`-device`, which the board package passes from 0.4.0), but **the chip cannot say which board it is on**: its ROM knows nothing of boards, so the IDE's board menu is the only guard. `provision` refuses when wchisp lists more than one device, prints the chip's UID and the image's board, and asks before it erases (`-yes` does not ask). A wrong menu bootloader does not merely leave the board dark: it drives pins the board uses as buttons as outputs (a rev0 menu drives a Rev1's UP and A, PB0 and PB11; a rev1 menu a Rev0's LEFT and UP, PB3 and PB4), so a button press shorts an output. A wrong USB Only bootloader drives only its LED pin: a Rev1's backlight (PB9), or a Rev0's piezo (PB10). Do not press buttons; put the right bootloader on through the ISP ([recovery](../platform/board/docs/recovery.md)). |
| **The web emulator** | Emulates rev0 and takes `rev0` binaries (spec/README.md, "Board revisions"). |

**What is still open** (2026-11-17): nothing in the board package, the
bootloader, the libraries or the tools is rev0-only. Rev1 has not run on a
board yet: step 8 of the checklist is the bring-up's. Boards Manager offers
0.3.0, which has no Rev1, until 0.4.0 is released (CLAUDE.md, Setup: a
staged install). The tools default to the newest board (CLAUDE.md, rule
9), the bootloader's `build.sh` included; chcart and chgpack run on their
own still default to `rev0`. The web emulator emulates rev0 alone.

## Adding a board: the checklist

In this order. rev1 is the example: steps 1-7 and 9 were done for it on
2026-11-17, and step 8 is its bring-up, still to come. The list stays the
guide for the next board (`rev2`, `CGR2`): where a step says what was done
for rev1, do the same for the new board. Every step is checkable without
the new board except 8.

1. **Register it in the spec.** Fill in its row of spec/chgame.md's
   device table (rev1's was reserved first; no device is reserved now, so
   a new board gets a new row): board name and FQBN, MCU, load address,
   largest image, save-safe size, layout id. If the memory map changes,
   note it in spec/chg.md ("The target") too. Tell the web emulator
   project (spec/README.md, which has a "what rev1 changes" note for it).
2. **The reference tools.** Put the board in `DEVICES` in
   `tools/chcart/model.py` and in `BOARDS` in `tools/chgpack.py`, with the
   same values (rev1 moved there from `RESERVED_DEVICES` and `RESERVED`,
   which are now empty; the tests of a reserved board patch in `rev2` for
   themselves). `--device` then takes it for `chgame cart prepare`, `flash`
   and `deploy`, and for `chgpack.py pack`.
   Run `python tools/chcart/fixtures.py`: for rev1, `good/devices`' `rev1`
   binary became a known device. It is a valid 64 B image, and
   `other-board` kept the `unknown-device` warning, so the expected results
   did not change. Review the diff, then run chcart's tests.
3. **The uploaders.** Put the board in `chgDevices` (`host/go/chg.go`) and
   `DEVICES` (`host/py/chgame_upload/chg.py`). Regenerate the shared vectors
   (`python -m chgame_upload.vectors --write ...`, see its docstring) and run
   both suites. **Bump the uploader's version** (`host/go/main.go` and
   `host/py/chgame_upload/__init__.py`, which must agree): Arduino keeps an
   installed tool whose version has not changed. For rev1 it became 0.3.0,
   which also added `-device` to `burn` and `provision`, since step 4
   makes `platform.txt` pass it, which older uploaders do not know.
4. **The board package** (`platform/board`; it takes effect at the next
   release, see CLAUDE.md rule 6):
   - `boards.txt`: a `rev1.*` entry, "CHGame Rev1", `build.variant=CH32X035/CHGame_Rev1`,
     `build.board=CHGAME_REV1`, its own bootloader files in the Bootloader
     menu (`bootloaders/CHGame/rev1/`, rev0's names), and
     `rev1.build.chgame_device=rev1`;
   - `platform.txt` (done once, for rev1, and the same for every later
     board): a default `build.chgame_device=rev0` (so a board entry
     without one, rev0's included, still builds); `-device
     {build.chgame_device}` on the `pack` hook, the `flash` upload recipe,
     Burn Bootloader and Upload Using Programmer, so the wrong board
     selected is refused; and `-DARDUINO_{build.board}` in
     `build.info.flags`, the board macro every file sees;
   - the variant `variants/CH32X035/CHGame_Rev1/`, a copy of Rev0's with the
     new pins (`PIN_LCD_*`, `PIN_SD_CS`, `PIN_BTN_*`, `PIN_BUZZER`,
     `PIN_LED`, and rev1's new `PIN_LCD_BL`, `PIN_VBUS_SENSE`,
     `PIN_TP14`/`15`), CHGfx's `CHGFX_*` pins, its `PeripheralPins.c`
     (which timers and UARTs reach which pins), and an `#error` when the
     board macro is missing;
   - the core's own pin code under `#if defined(ARDUINO_CHGAME_REV1)`:
     `cores/arduino/ch32/chgame_boot.c` (the crash handler's LED and
     buzzer, a debug build's wait for A) and `Tone.cpp` (`noTone()` leaves
     rev1's buzzer pin low);
   - the CHANGELOG.
5. **The libraries' pins.** CHGfx (`CHGFX_*_PORT/PIN`, from the variant;
   `CHGfx.h` keeps rev0's as its defaults; rev1's backlight,
   `CHGFX_BL_PIN`), CHSd (`SdSpi.cpp`), and the CHGame library's
   `Input.cpp` (the buttons, read by register; the START hold that leaves
   for the menu is there too, in `CHGame::pollButtons()`) and `Audio.cpp`
   (the buzzer's timer and the LED) address GPIO ports directly. Take them
   from the variant or `#if defined(ARDUINO_CHGAME_REV1)`, leaving rev0's
   code as it is in the `#else`, so one source builds for both boards.
   Rebuild all 20 games for rev0 and check that their images are
   byte-identical and their sim frames unchanged (rules 2, 3 and 6).
6. **The bootloader.** Its pins are in `src/hal.h` (the `HAL_GPIO*_CFG*`
   words and the button bits, `HAL_KEYS`). `build.sh --board=rev1` selects
   them and sets `CHBOOT_BOARD_TARGET` to rev1's id; the board word in the
   image and `HELLO`'s board field come with that switch. The field cost
   16 B on rev0's pins (2026-10-07: 11,936 B list, 12,076 B visual, over
   the visual gate); with rev1's own pins and some crunching the rev1
   builds are 11,928 B list and 12,064 B visual (224 B free against the
   192 B gate), the backlight's 40 ms wait after DISPON included. `dist.sh` builds each board's files, rev1's under rev0's
   names in `release/rev1/` and `bootloaders/CHGame/rev1/`, and SIZES.md
   records them. The PC suite runs `core_rev1` and the boot and visual
   suites again for rev1 (`HELLO` with the board field, CHG files for the
   other board refused, the key bits, the backlight). Rev0's binaries must
   stay byte-identical.
7. **The build tools.** Done once, for rev1: `tools/device.py` and
   `chgame` read the device table, take a global `--board` (default: the
   newest board the installed core has, so a new board becomes the default
   by itself), build into `build/<board>/`, and `chgame check`, `export`
   and `card` take every installed board: one `.chgame` carries a binary
   per board, and the casino card is prepared per board. `chgame gif` and
   the simulator need nothing: the simulator has no board. For a later
   board, add it where boards are still listed by name: `build.sh`'s
   `--board`, `dist.sh` and `release.py`'s `BOOT_FILES`, and
   `check_size.py`'s limits if its memory map differs.
8. **On the boards.** Upload with the wrong board selected and check that it
   is refused; install a card for each board on the other and check for
   ERROR 5; burn the other board's bootloader over USB and check that it is
   refused. Run `tools/sketches/CHBoardTest` first on a new board. For
   rev1: still to do.
9. **The docs.** This registry, CLAUDE.md (Limits, the FQBN, the device),
   the README's board section, `platform/README.md`, `docs/platform.md`
   (the pins), `docs/sd-card.md`,
   `platform/board/docs/hardware-pinmap.md` and `recovery.md`.

## For rev1: the SD card's DI gate

Fitted on Rev1 and Rev 1.5 (the card's CS is PB3 there). Rev0 has no gate.

**The change.** One OR gate, a 74LVC1G32 (SOT-23-5), between MOSI and the
card: its inputs are MOSI and SD_CS, its output is the card's DI. While
SD_CS is low the card gets MOSI as now; while it is high the card's DI is
held at 1, whatever the panel is sent. SCK stays shared and ungated. The
gate adds about 4 ns, nothing at 12 or 24 MHz. No firmware changes.

**Why.** On rev0 the panel and the card share SCK and MOSI, and the card is
trusted to ignore the bus while its CS is high, as the SD specification
says it must. Some cheap cards do not. The 128 MB cards given away with the
first boards (CID maker 05, product "asdfg", 2025-12, SDSC) decode the
panel's pixels as commands while deselected, and sooner or later one of
them leaves the card answering nothing, not even CMD0, until it loses
power. On rev0 that shows as the SD Graphic Menu's cover and then only
built-in icons (the cover is read before the panel's first fade), and as a
white screen after picking a game. No driver can prevent it: the panel has
to be sent its pixels on those wires.

**What showed it** (2026-10-20, with the bench `tools/sketches/CHSDtest`,
traffic of 16,384 frames between reads, neither chip selected):

| Traffic while the card is deselected | 128 MB gift card | 16 GB SDHC ("SD16G") |
|---|---|---|
| all zeros, 24 MHz | reads go on | reads go on |
| all ones, 24 MHz and 187.5 kHz (what the gate makes it) | 190 reads, all CRCs right | |
| pseudo-random, 187.5 kHz, 1.5 MHz, 24 MHz | hung at the next read, every time | 260 reads, all CRCs right |

At 187.5 kHz the edges are far too slow for crosstalk, so the card is
acting on the data, not on noise. A run of ones holds no command's start
bits (each command begins 0, 1), which is why the gate makes any card safe.

**Why DI and not SCK.** Gating the clock also works while a card is in use,
but the specification asks for at least 74 clocks with CS high (and DI
high) before the first command: a clock gated by SD_CS never delivers
them. The DI gate leaves those clocks, and the one after each deselect that
releases DO, as they are. A transistor pulling the card's side low would
need a series resistor against MOSI's push-pull drive, waste current on
every panel transfer and round the edges at 24 MHz.

**To check a board or a card:** CHSDtest's `MIX` with `SET PATTERN 1`
(pseudo-random traffic) between reads; on a gated board the gift cards
must pass it as the 16 GB card does.

## Why not a target name in the title

The question came up for rev0: call games `CHGAME-REV0` and leave the
format alone. A name does not stop anything. The bootloader would install
any file whatever its title, an uploader would flash any image, and a cart
could not carry both builds of a game. The device field already gives each
binary a board. The target id puts the same fact where the hardware and the
uploaders check it.
