# Changelog

The version is the `version=` line in `arduino/CHGame/platform.txt`. That is the
number Boards Manager compares with what a user has installed, so every release
bumps it. `python tools/release/release.py --repo bateske/CHGame` (in the
repository root) publishes the release and uses the matching section of this
file as the GitHub release notes.

## 0.4.1 (2026-11-24)

New box art and one game change; the core, the libraries and the
bootloaders are as in 0.4.0.

### Changed

- **New box art for 19 programs**, the pictures the SD Graphic Menu shows:
  Backgammon, Blackjack, Boardwalk, Checkers, Chess, Dominoes, Four in a
  Row, Mahjong, Poker, Roulette, Slots, Snakes & Ladders, Solitaire, Tic Tac
  Toe Royale, Word Wheel, Words, SD Card Reader, SD to Serial and STL
  Viewer, repainted by hand (each example's `tools/art/cart.png`, which now
  wins over its `tools/cart.py`). The casino cart and the SD cards carry
  them.
- **CHBingo: EASY picks the card up first.** A on a card with a number
  waiting picks it up and the glove glides to that number; each further A
  daubs one cell, and the card goes down when none is left or on a swipe.
  B still spends the power-up.

## 0.4.0 (2026-11-21)

### Added

- **The CHGame Rev1 board, also for Rev 1.5** (*Tools > Board > CHGame
  Boards > CHGame Rev1*), FQBN `CHGame:ch32v:rev1`, device `rev1`, variant
  `CH32X035/CHGame_Rev1`, board macro `ARDUINO_CHGAME_REV1`. Rev 1.5 is
  the same board with USB-PD, a battery USB host and a protected power
  output added; it uses this entry. **Rev1 is an attempt at a stable
  pinout.** Rev1 has
  other pins than Rev0, so a sketch is built for one board or the other:
  - buttons UP PB0, DOWN PB1 (PB5 is the same pad: never driven), LEFT
    PC3, RIGHT PC0, A PB11, B PB6, SELECT PB7, START PB8; LCD DC PB4 (CS
    PA4 and RST PB12 as before); SD CS PB3; the LED on PB10; the buzzer on
    PA1, TIM2_CH2 at remap 0, a magnetic buzzer switched by a MOSFET, which
    the CHGame library's audio leaves low when silent;
  - new: `PIN_LCD_BL` (PB9, active high), the backlight, which stays low
    until the panel shows a defined picture: the core drives it low before
    `setup()` (`pre_init()`), so the panel's power-up noise never shows
    between the reset and CHGfx's `gfx_begin()`, which lights it after a
    black frame (R20's pull-down alone did not hold it off); `PIN_VBUS_SENSE` (PA0, VBUS /
    101, analog input only); `PIN_TP14` / `PIN_TP15` (PC14 / PC15, test
    pads on Rev 1, CC1 / CC2 on Rev 1.5). `PIN_GPIO1`-`4` are gone with
    the H1 header: Serial1 is USART2 on CN3 (PA2 TX, PA3 RX), Wire is I2C1
    on CN2 (PC18 SDA, PC19 SCL);
  - PWM (`analogWrite()`, *Peripherals: Full*) only on PB9 and PB10 (TIM1
    CH1/CH2) and PA1 (TIM2 CH2), all at remap 0; no complementary outputs
    or break input, which would land on buttons. `Servo` moves off TIM2
    (the CHGame library's audio) to TIM3, which it shares with `tone()`;
  - the core's `noTone()` and `tone(pin, 0)` leave the pin low on Rev1
    (they left it at its last level, high about half the time, which on
    Rev1's buzzer is a steady current);
  - after a crash the buzzer (PA1) is driven low and the LED (PB10) lit;
    the backlight is left as it is. PA0's latch is cleared too, so on a
    Rev 1.5 a crash turns host power (PA0 high: the battery boost onto
    VBUS) off; elsewhere PA0 is an input and nothing changes. A debug
    build's "press A to restart" reads PB11.

  Rev1's five bootloaders, under the same names as Rev0's, are in
  `bootloaders/CHGame/rev1/`, and the Bootloader menu of each board offers
  only its own. Rev0's board entry and bootloader files are unchanged.
- **The board macro is defined**: `platform.txt` passes
  `-DARDUINO_{build.board}` to every C, C++ and assembler file
  (`ARDUINO_CHGAME_REV0`, `ARDUINO_CHGAME_REV1`). 0.3.0's notes named
  `ARDUINO_CHGAME_REV0`, but nothing defined it. The Rev1 variant stops
  the build with an `#error` if the macro is missing.
- **Upload, Burn Bootloader and Upload Using Programmer refuse the other
  board.** `platform.txt` passes `-device {build.chgame_device}` (`rev0`
  unless the board entry says otherwise) to chgame-upload's `pack` hook
  (the `.chg` file carries the board's target id, which the SD menu
  checks), its `flash` upload and its `burn`: a sketch is not flashed onto
  a board whose bootloader names another board, and a bootloader image for
  another board is refused before anything is written. This needs
  chgame-upload 0.3.0, which the package installs with it.
- **An API reference**, <https://bateske.github.io/CHGame/>: every public
  function, class and constant of CHGame, CHGfx, CHSd, SPI, Wire and EEPROM,
  documented in their headers with Doxygen.

### Changed

- **The bootloaders keep the system settings block** (bootloader version
  4, both boards). The last 32 bytes of flash, `0xF7E0`-`0xF7FF` at the
  end of the metadata page, are reserved for settings that belong to the
  handheld rather than to a game; none is defined yet. Programs cannot
  reach them, and from version 4 the bootloader keeps them when it
  installs a program, aborts an upload or updates itself, where earlier
  versions erased them at every install. To keep them on a board in the
  field, update its bootloader (*Burn Bootloader* with the CHGame USB
  programmer). The core's `chgame_map.h` names the block
  (`CHGAME_SYS_ADDR`, `CHGAME_SYS_SIZE`); a sketch must not write it.
- **The libraries know Rev1.** Each Rev1 difference is under
  `ARDUINO_CHGAME_REV1` or comes from the Rev1 variant, so Rev0's builds
  are unchanged: the 20 games' and the 3 apps' release images are
  byte-identical.
  - **CHGfx 1.3.3** takes the panel's and the card's pins from the board's
    variant (`CHGFX_*`; its own defaults stay Rev0's) and drives a switched
    backlight (`CHGFX_BL_PORT` / `CHGFX_BL_PIN`, PB9 on Rev1): low from the
    start, and high only after `gfx_begin()` has sent the panel a black
    frame, so the panel's power-up noise is never lit.
  - **CHSd**: the card's chip select is PB3 on Rev1.
  - **CHGame**: Rev1's buttons; the sound on TIM2 channel 2 (PA1), driven
    low whenever it is silent, with a pitch under 16 Hz played as silence
    (the timer cannot make it without holding the pin high); the LED
    patterns on PB10.
- **chgame-upload 0.3.0** knows rev1 and takes `-device` on `burn`,
  `selfupdate` and `provision` too: a bootloader image built for another
  board (its board word, offset `0x14`) is refused before the board is
  touched, over USB and through the factory ISP alike. The factory ISP
  cannot see which board it is on, so `provision` also refuses while more
  than one chip is in ISP mode, prints the chip, its UID and the image's
  board, and asks before it erases (`-yes` does not ask). `burn -method
  isp`, what Burn Bootloader runs with *WCH factory ISP*, never asks.
- **The casino cart carries both boards' binaries, and its SD card comes
  as one zip per board**, `CHGame-sdcard-<version>-rev0.zip` and
  `CHGame-sdcard-<version>-rev1.zip`: a card is for one board, since its
  CHG files hold that board's programs.
- **CHGfx, CHGame and CHSd link from archives** (`dot_a_linkage=true` in
  their `library.properties`), so an object of theirs is linked only when
  the sketch calls into it. Arduino otherwise links every object of an
  included library whole, and CHGfx's DMA interrupt handler (its
  `DMA1_Channel3_IRQHandler` replaces the core's weak default) kept the 8 KB
  framebuffer, the 1 KB chunk buffers and the SRAM converters alive in any
  sketch that included `CHGame.h`, drawing with it or not. A sketch that
  uses `audio::` and `chgame_readButtons()` and draws through its own code
  now takes 352 B of static RAM instead of 9,712 B. The 20 games' and the
  3 apps' release images are byte-identical. (Reported by a developer.)

### Fixed

- **Serial1 receives.** It is USART2, on PA2/PA3 (Rev0's H1 header, Rev1's
  CN3), but the core set up USART2's receive interrupt only for a
  `Serial2`, which these boards do not have, so `Serial1.read()` never saw
  a byte; sending worked. (*Tools > Peripherals: Full*, as before.)
- **chgame-upload keeps the flags given before its command.** It read
  `-port`, `-timeout`, `-verbose` and `-quiet` before the command and then
  reset them to their defaults when it read the command's own flags. The
  Upload and Burn Bootloader recipes give `-port` there, so the selected
  port was ignored: the tool looked for the board itself, and with two
  CHGame boards plugged in it stopped with "several CHGame devices found".
  (The Go tool, which the package installs; the Python one was right.)
- **CHSd works with more microSD cards.** It sent each command right after
  the card's previous response, where the SD Physical Layer Simplified
  Specification asks for at least 8 clocks in between (N_RC, SPI mode
  timing). Many cards do without them; a strict one (a SanDisk 32 GB,
  "SK32G") took the next command misaligned and stopped answering, so every
  sketch on CHSd (CHStlView, the word games' card files) said there was no
  card while the SD menu bootloader read it. `cmd()` now clocks one idle
  byte first, as the bootloader's `sd.c` does: one byte per command, not per
  block.
- **EEPROM no longer writes the CH32X035's option bytes.** The library is
  the CH32V003's: its `commit()` erased the option-byte block and rewrote it
  a half-word at a time, which the CH32X035 is not documented to accept. A
  write that did not take would leave the chip read-protected (recovery
  erases the whole flash, bootloader included) or with its user options
  changed. On this chip `commit()` now writes nothing and returns `false`,
  `begin()` reads only `Data0`/`Data1`, and including `EEPROM.h` prints a
  compiler message (`#define EEPROM_NO_WARNING` silences it). Save with the
  CHGame library's `save::`.
- **Wire reports a missing or refusing device as Arduino does.**
  `endTransmission()` returns 2 when no device acknowledges the address and
  3 when a data byte is not acknowledged, at once and with a STOP; it
  returned 4 after the timeout. A byte that never leaves now times out
  instead of hanging, and `requestFrom()` to an absent device releases the
  bus. (Not yet run on hardware.)
- **CHGfx 1.3.2: `gfx_setSpiDiv()` sets SPI1 up afresh** (clock enabled, master, mode 0,
  MSB first), not only its clock divider, so `gfx_setSpiDiv(gfx_spiDiv())`
  hands SPI1 back to CHGfx after the Arduino SPI class, whatever mode, bit
  order or `SPI.end()` it left behind. No game calls it: their images are
  unchanged.

## 0.3.0 (2026-10-07)

The first release from the CHGame repository: one Boards Manager URL now
installs the core, the menu bootloader, the libraries and the games. The
package's maintainer is shown as **bateske**.

### Changed

- **The board is "CHGame Rev0"** (*Tools > Board > CHGame Boards > CHGame
  Rev0*), FQBN `CHGame:ch32v:rev0` (it was `CHGame:ch32v:CHGame`), variant
  `CH32X035/CHGame_Rev0`, `ARDUINO_CHGAME_REV0`. A later hardware revision
  gets its own board entry and variant.
- **The CHGame library's instance is `chgame`** (`chgame.boot()`,
  `chgame.pressed()`, `chgame.exitToMenu()` ...); it was `arduboy`. CHGame
  is the platform and the product, Arduboy the maker. A sketch written for
  0.2.4 with the copied library renames `arduboy.` to `chgame.`.
- **The games' code is in their sketch folders**, so the Arduino IDE shows
  it as tabs; `src/` keeps generated art, scores and tables.
- **Smallest + LTO links as one partition** (`-flto-partition=one`). gcc
  split the larger sketches in two and could not inline or merge across the
  split: nine of the examples are 40-376 B smaller, none bigger.
- **CHGfx 1.3.1: a 12 bpp sketch carries no 16 or 18 bpp code.**
  `gfx_begin(..., GFX_12BPP)` with no `gfx_setColorMode()` leaves those
  converters out: 0.2-0.4 KB of flash and 176 B of SRAM back in every game.

### Added

- **Box art for every game.** Each example has a painted cover for the SD
  Graphic Menu (`docs/cart.png`, from its `tools/cart.py`). The menu's own
  pictures, which every card falls back on (the cover, the text menu's
  picture, the about page, installed, no picture, no cover, the errors),
  are painted to match, and so are the casino card's cover and folders;
  the graphic menu's built-in icons are new.
- **One casino chip.** The betting chips (Blackjack, Roulette, Craps, Yacht,
  Poker, Tic Tac Toe), the rail racks and the chip-styled pieces (Checkers'
  men, Backgammon's checkers, Four in a Row's discs, the GOBBLE chips,
  Boardwalk's carpet stacks, Solitaire's chip card back, Poker's seat
  avatars) are redrawn as one family: a lit label, edge inserts as dashes,
  rims in the chip's shade, stacks whose inserts alternate so they can be
  counted. The shared sprites are `tools/art/common/chip_*.txt`.
- **The libraries come with the package.** `#include <CHGame.h>` (buttons,
  frame pacing, palette, drawing, sound, saving, the debug protocol), CHGfx
  (graphics) and CHSd (SD card / FAT) are in the package's `libraries/`,
  beside SPI, Wire and EEPROM. Nothing to copy into the sketchbook.
- **Twenty casino games and two apps as examples:** *File > Examples >
  CHGame > Games* (CHBlackjack, CHChess, CHPoker ...) and *Apps*:
  **CHStlView**, a 3D wireframe viewer for the `.STL` files on the SD card,
  **CHSDtoUSB**, the SD card reader, and **CHSDtoSerial**, the SD card helper
  the CHGame website uploads (a framed serial protocol); with *Hello*, the
  smallest complete sketch.
- **SD menu packages from the IDE.** Every build also writes
  `<sketch>.ino.chg`, the package the bootloader's game menu installs from
  the card's `GAMES` folder; *Sketch > Export Compiled Binary* puts it in the
  sketch's `build` folder. Its title is the sketch's name in capitals.
  (`chgame-upload pack`, with `-title`, `-author` and `-gameversion` when
  run by hand.)
- **Every game and app as one `.chgame` cart** beside the release
  (`CHGame-Casino-<version>.chgame`; the format is the repository's
  `spec/chgame.md`), and its SD card's contents as a zip
  (`CHGame-sdcard-<version>.zip`): built from this package's own examples.
  Each example has a `chgame.json` describing it.
- **Tools > Bootloader** chooses what *Burn Bootloader* writes: the **SD
  Text Menu (Rainbow)**, the default, or **(Static)**, the same menu with
  nothing turning: the selection bar, the boxes and the picture's magenta
  parts in the menu's text colour; or **USB Only**, the same bootloader
  without the menu, for a board built without an SD card: it drives the
  LED and USB and leaves every other pin alone (high-Z), so the card's and
  the panel's pins are free for other circuits. Every bootloader leaves the
  pins it does not use high-Z. The 0.2.4 bootloader is no longer shipped.
- **A card's launch game never installs by itself.** If it is the game in
  flash it starts at once, with the panel dark; otherwise the menu opens on
  it and A installs it, so switching on never writes over the game you
  were playing. The SD Graphic Menu stays on the card's cover at power-on
  (A there shows the installed game), and LEFT/RIGHT do nothing on a card
  without folders.
- **The SD Graphic Menu** (*Tools > Bootloader*, Rainbow or Static): the same
  card shown one picture at a time and no text, in the manner of the
  Arduboy FX. The card's cover at power-on, a cover for each folder
  (LEFT/RIGHT), each game's box art (UP/DOWN), a bar over the picture while
  a game installs, fades and slides between pictures, an about page on B.
  Every example game and app comes with its box art (`docs/cart.png`), and
  the casino card sorts them into genre folders. Switch between the two
  menus at any time with Burn Bootloader: the card works with both.
- **The SD Text Menu takes its look from the card:** the picture behind it
  (`GAMES/MENU.BG`; every card the tools prepare has the CHGAME logo, its
  colour turning), the order of the games and folders of up to 240 games
  (`GAMES/MENU.IDX`), and optionally a game started at power-on instead of
  the menu (hold START while switching on for the menu). Errors are shown as
  a number (the repository's docs/sd-menu.md lists them).
- **Programmer "CHGame USB (requires CHGame bootloader, no drivers)"**:
  *Burn Bootloader* through the bootloader that
  is already on the board. No driver and no buttons; a port must be
  selected, as for Upload. The installed sketch is erased. *Upload Using
  Programmer* does the same and then uploads the sketch. "WCH factory ISP
  (Hold BOOT on power-up, requires driver)" remains for a board whose bootloader is missing, damaged or locked, and no
  longer needs a port selected.
- `chgame-upload` 0.2.0: `selfupdate <boot.bin>`, `burn -method usb|isp`
  and `pack`. It refuses an image that is not a bootloader for this board.
  Its source is in this repository now (`platform/bootloader/host/go`).
  Ready for board revisions (the repository's docs/hardware-revisions.md):
  it shows the board a bootloader reports (`probe`, `info`), refuses a
  bootloader built for another board, and takes `-device rev0` on `flash`
  (refusing another board) and `pack`. The Upload recipe does not pass it
  yet; that comes with the first board after Rev0.

### Fixed

- **The word games could find no card after CHSDtoUSB.** CHSDtoUSB turns
  the card's CRC checking on, the card stays powered across a reset, and a
  game uploaded while it ran started without the menu (which turns it
  off). CHSd sends fixed CRCs, so a card that kept checking on through the
  reset refused it. CHSd now turns checking off itself.
- **Linux builds.** `cores/arduino/ch32/lib/ch32yyxx.h` included
  `core_riscv_cH32yyxx.h` with a capital H; the file is
  `core_riscv_ch32yyxx.h`, so the core only compiled on case-insensitive file
  systems.
- **A crash no longer leaves the piezo sounding.** A hard fault, or an
  interrupt with no handler, used to spin with interrupts off, and the timer
  driving the piezo held the note that was playing. Now the piezo pin is
  driven low and the status LED stays on (`chgame_fault()`, 58 B). A debug
  build (`-DCHGAME_DEBUG=1`) also keeps mcause, mepc, mtval, ra and sp at
  the bottom of the stack. A sketch that provides `chgame_fault_park()` (the
  CHGame library's debug protocol) goes on answering its PC; otherwise a
  press of A restarts it, for the library's debug command `!` to report.
- **A sketch header named like a core header broke the build** on Windows
  and macOS: the core was compiled with the sketch's folder ahead of its own
  on the include path, so a sketch's `Board.h`, `Variant.h`, `Timer.h` ...
  replaced the core's `board.h`, `variant.h`, `timer.h` (the file systems
  ignore case). The sketch's folder now comes last, and `wiring.h` includes
  `"board.h"` rather than `<board.h>`.
- Comments that still described the 8 KB bootloader and a sketch at 0x2000
  (`link_chgame_app.ld`, `chgame_map.h`), and one in `boards.txt` naming a
  generator that does not exist.

## 0.2.4 (2026-09-30)

### Added

- **USB → Upload only** board menu option (`usb=uploadonly`): compiles out
  `Serial` (the USB serial class, Stream/Print and the CDC data path) but
  keeps the USB device and the 1200-baud upload handshake, so the COM port
  still appears and Upload still works with no button presses. About
  0.6–0.7 KB smaller: an empty sketch 3,968 → 3,288 B, CHChess (LTO)
  49,444 → 48,824 B. Using `Serial` in this mode is a compile error naming the
  menu setting, rather than a stub that silently prints nothing, and it no
  longer falls back to `Serial1` with Peripherals → Full. **Serial** is the
  default, and FQBNs without `usb=` build exactly as before. Proposed from
  HypeRunner, which is close to the flash limit. Tested on the board with
  `-Os` and LTO: the port appears, uploading over an Upload-only sketch works
  with no button presses (also one stuck in `setup()`), and typing into its
  port in a serial monitor neither crashes it nor stops the next upload.

### Changed

- Every sketch is smaller and has more RAM: an empty sketch 4,668 → 3,968 B
  flash and 704 → 544 B RAM with `-Os`, CHChess (LTO) 50,036 → 49,444 B and
  18,000 → 17,844 B. Two changes:
  - `USB_init()` sets up its clocks and the USB pins with direct register
    writes instead of the vendor `RCC_*ClockCmd()`/`GPIO_Init()` helpers.
    The register values are identical. It saves ~350–480 B when nothing else
    uses the helpers, less when `pinMode()` pulls in `GPIO_Init` anyway.
  - The startup code no longer registers `__libc_fini_array` with `atexit()`.
    `main()` never returns, so global destructors never ran anyway, and the
    registration linked newlib's exit handling and a 140 B table in RAM
    (~224 B flash, 144 B RAM).
  - Checked on the board: Serial output, re-uploading, global constructors,
    and the USB pin and clock registers read back identical to 0.2.3.

## 0.2.3 (2026-09-30)

### Added

- **Optimize → Smallest + LTO** (`opt=oslto`): `-Os` plus link-time
  optimisation across the core, libraries and sketch. Usually 1–5 KB smaller
  than `-Os`: CHBlackjack 50,048 → 47,528 B, CHSDtoUSB 23,788 → 20,144 B, an
  empty sketch 4,668 → 4,248 B, and CHChess fits only with it (50,036 B; it
  overflows by 5.2 KB without). Static RAM drops too, by 200–800 B. Built
  cleanly on 15 sketches and the core's library examples, and tested on the
  board: USB serial, re-uploading through the 1200-baud handshake,
  `millis()`/`micros()`/`delay()`, the `osSystickHandler` hook and SRAM
  functions all behave as with `-Os`. `-Os` stays the default.

### Changed

- The RAM report is now measured against 18,416 B, the space the linker
  actually allows for static data (20 KB SRAM less the boot block and the
  fixed 2 KB stack), instead of 20,480 B. The percentage now matches when the
  link would fail; "left for local variables" is what remains for the heap.
  The "Low memory available" warning fires at 95% of that instead of 75%, so
  it no longer appears on every sketch with a framebuffer.

### Fixed

- Wire called `GetTick()` without a prototype, so it was implicitly declared
  as returning `int` while the core defines it as `uint64_t`. It happened to
  work, but LTO flagged it as a type mismatch that could be misoptimised.

## 0.2.2 (2026-09-28)

### Changed

- New **Peripherals** board menu (Tools menu in the IDE, `periph=` in an
  FQBN). The default, "Game", compiles out Serial1, `tone()`, `analogWrite()`
  PWM and HardwareTimer; "Full" keeps them. USB Serial, SPI, Wire,
  `analogRead()`, `attachInterrupt()` and CHGameSound (which has its own timer
  path) are the same in both. With "Game" an empty sketch is 4,668 B instead
  of 8,712 B, CHSDtoUSB is 22,528 B instead of 27,100 B, and CHBlackjack
  builds again at 48,632 B instead of overflowing the app region by 2,140 B.
- Why the menu exists: those sizes were what everyone was used to, but they
  came from a hand-edited `platform.local.txt` in the installed 0.1.0 folder,
  added for CH32Doom and never part of a release. Installing 0.2.1 replaced
  that folder and the defines with it, and core.a is linked `--whole-archive`,
  so the unused peripherals' constructors and interrupt handlers cost about
  4 KB in every sketch. The defines now live in their own build property
  (`build.flags.periph`) appended to the compiler flags, so a sketch or CLI
  user overriding `compiler.*.extra_flags` no longer drops them.

## 0.2.1 (2026-09-28)

First Boards Manager release since 0.1.0; it also carries the 0.2.0 changes
below.

### Fixed

- `micros()` ran backwards inside every millisecond and jumped about 2 ms
  forward at each tick. The CH32X035 SysTick is configured to count up, but
  `getCurrentMicros()` was inherited from a down-counting STM32 SysTick and used
  `CMP + 1 - CNT` for the sub-millisecond part. Anything timed with `micros()`,
  including `pulseIn()`, saw elapsed times that were wrong by up to 2 ms and
  often negative. `millis()` and `delay()` were not affected.
- A SysTick tick that lands while interrupts are off, or while an interrupt that
  outranks SysTick is running, is now counted by `micros()` instead of being
  lost until the handler runs. The tick handler updates its flag and count as
  one unit so a nested interrupt cannot count a tick twice.

### Added

- `test/sketches/MicrosMonotonic`: on-hardware check that `micros()` never
  steps backwards and stays in step with `millis()`, with interrupts on and off.
  Verified on a board: 0 backwards steps in 143k samples, against 103k with the
  old core.
- `test/native/sim_micros.py`: host-side model of the SysTick and of both
  versions of the code, showing why each part of the fix is there.

## 0.2.0 (2026-09-04)

Not published to Boards Manager; included in 0.2.1.

### Changed

- `Serial.begin()` no longer blocks until the host enumerates the device. USB
  enumeration completes in the USB interrupt while `setup()` runs, so a sketch
  is running within a few milliseconds of power-on instead of about 1.1 s.
- Writes to a port no host has opened are discarded rather than blocking, and
  writes to a host that has stopped reading time out, so a closed serial
  monitor or a board on batteries can never stall a sketch.
  `Serial.enumerated()` and `Serial.waitForPC(ms)` are there for sketches that
  want to wait, and `-DCHGAME_USB_TX_TIMEOUT_MS=n` sets the transmit timeout.

### Added

- `test/sketches/BootTiming`: measures time to `setup()` and to enumeration.

## 0.1.0 (2026-08-21)

First release: driverless USB CDC bootloader for the CH32X035, the CHGame
Arduino board package with the toolchain, `wchisp` and `chgame-upload`
delivered as Boards Manager dependencies, host tooling and documentation.
