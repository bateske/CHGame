# The CHGame platform

What a game developer needs to know about the hardware and the core. The
deeper references are in [../platform/board/docs](../platform/board/docs):
`memory-map.md`, `boot-flow.md`, `protocol.md`, `recovery.md` and
`ch32x035-gotchas.md`. For the graphics side, see
[performance.md](performance.md).

## Hardware

Two boards with one chip and one memory map: **CHGame Rev1** (device
`rev1`), the current board and an attempt at a stable pinout, and
**CHGame Rev0** (`rev0`), legacy. Rev 1.5 is a Rev1 with
a power section added (a USB-PD sink, a battery-powered USB host and a
protected output, driven by the [CHPower](https://github.com/bateske/CHPower) libraries) and takes the
Rev1 build.
Their pins differ, so every sketch is built for one board or the other
(*Tools > Board*, or `chgame --board`; [hardware-revisions.md](hardware-revisions.md)).
A binary for one drives pins the other uses as buttons.

| | |
|---|---|
| MCU | WCH **CH32X035G8U6**, QingKe V4C RISC-V (no FPU), **48 MHz** from the internal RC (there is no PLL) |
| Flash | 62 KB user flash in 256 B pages: 12 KB bootloader, **50,944 B** for the sketch, 256 B metadata |
| SRAM | 20 KB: 16 B boot block, **18,416 B** for statics and heap, a fixed **2 KB** stack |
| Display | 1.44" **128x128 ST7735S** on SPI1, 12 or 16 bpp, up to 24 MHz SPI |
| Storage | **microSD** on the same SPI1 bus as the display |
| Input | D-pad, A, B, SELECT, START (active low, internal pull-ups) |
| USB | full-speed USB-C: CDC serial and the upload path. VID:PID 16C0:27DD (shared test IDs for now) |
| Schematic | Rev0: [../platform/hardware](../platform/hardware) (PDF + EasyEDA netlist) |

What differs between the boards:

| | Rev0 | Rev1, Rev 1.5 |
|---|---|---|
| Sound | piezo on PB10 (TIM1 CH2) | magnetic buzzer on PA1 (TIM2 CH2), switched by a MOSFET from VSYS: never leave PA1 high |
| LED | one status LED on PB9, active high | one status LED on PB10, active high |
| Backlight | always on | PB9, active high, pulled down: off until CHGfx's `gfx_begin()` has sent the panel a black frame |
| SD card | CS PB11 | CS PB3; an OR gate holds the card's DI high while it is deselected, so it never sees the panel's data |
| Expansion | header H1: 4 GPIO and a UART (Serial1, *Peripherals: Full* only) | CN3: Serial1 (USART2, PA2 TX, PA3 RX, *Peripherals: Full*); CN2: Wire (I2C1, PC18 SDA, PC19 SCL, 4.7k pull-ups). Both 3.3 V |
| Other | | VBUS sense on PA0 (VBUS / 101, analog input only, never driven); test pads TP14 / TP15 on PC14 / PC15 (CC1 / CC2 on Rev 1.5: leave them alone there) |

### Pins

These are the names in the variants (`variant_CHGame_Rev0.h`,
`variant_CHGame_Rev1.h`). Sketches use the names, not the port numbers;
the CHGame library, CHGfx and CHSd take theirs from the board being built
for. [hardware-pinmap.md](../platform/board/docs/hardware-pinmap.md) has
the board's pin map.

| Name | Rev0 | Rev1, Rev 1.5 |
|---|---|---|
| `PIN_BTN_UP` | PB4 | PB0 |
| `PIN_BTN_DOWN` | PC14 | PB1 (the same pad as PB5: never drive PB5) |
| `PIN_BTN_LEFT` | PB3 | PC3 |
| `PIN_BTN_RIGHT` | PC15 | PC0 |
| `PIN_BTN_A` | PB1 | PB11 |
| `PIN_BTN_B` | PB6 | PB6 |
| `PIN_BTN_SELECT` | PB7 | PB7 |
| `PIN_BTN_START` | PB8 | PB8 |
| `PIN_LCD_CS` | PA4 (also SPI1 NSS / default `SS`) | PA4 (the same) |
| `PIN_LCD_DC` | PB0 | PB4 |
| `PIN_LCD_RST` | PB12 | PB12 |
| `PIN_LCD_BL` | (none: always on) | PB9 |
| `PIN_SD_CS` | PB11 | PB3 |
| SPI1 SCK / MISO / MOSI | PA5 / PA6 / PA7 | PA5 / PA6 / PA7 |
| `LED_BUILTIN` / `PIN_LED` | PB9 | PB10 |
| `PIN_BUZZER` | PB10 | PA1 |
| `PIN_GPIO1..4` | PC0, PC3, PA0, PA1 | (none) |
| `PIN_VBUS_SENSE` | (none) | PA0 |
| `PIN_TP14` / `PIN_TP15` | (none) | PC14 / PC15 |
| Serial1 TX / RX | PA2 / PA3 | PA2 / PA3 (CN3) |
| Wire SDA / SCL | PC18 / PC19 | PC18 / PC19 (CN2) |

**The default `SS` is the LCD's chip select.** A plain `SD.begin()`
selects the panel, not the card. The card's CS is `PIN_SD_CS` (PB11 on
Rev0, PB3 on Rev1).

**A sketch that knows its board** tests the board macro the package
defines (0.4.0 on): `ARDUINO_CHGAME_REV0` or `ARDUINO_CHGAME_REV1`. On
Rev1, PWM (`analogWrite()`, *Peripherals: Full*) reaches only PB9, PB10
(TIM1) and PA1 (TIM2), and `Servo` shares TIM3 with `tone()`.

There is no reset pin. PB7 is SELECT. The only resets are the power switch
and `NVIC_SystemReset()`.

## Boot, upload and USB

**Startup.**
- **With the 0.2.4 bootloader**, it checks the sketch's CRC and jumps to it
  within a few milliseconds of power-on.
- **With the SD menu bootloader** ([sd-menu.md](sd-menu.md)), power-on shows
  the game menu. The sketch starts when it is picked, after an upload, or at
  once when there is no card. It always starts from a real reset, never
  from a jump out of the menu.
- **USB** enumerates in the background while `setup()` runs.

**`Serial` is native USB CDC:**
- Writes to a port that no host has opened are dropped, never blocked, so a
  game on batteries never stalls on a `println`.
- `while (!Serial);` or `Serial.waitForPC(ms)` waits for a terminal.

**Upload.** The 1200-baud touch reboots into the bootloader on the same
port; then flash, verify, restart in about half a second. It works with
`usb=uploadonly` (no `Serial` in the sketch), and with a sketch stuck in a
loop, because the handshake lives in the USB interrupt. From board package
0.4.0 the uploader is told the board selected and refuses a board whose
bootloader names another, before anything is written.

**Recovery.** A sketch that kills USB (for example a HardFault: the core's
handler spins) needs a power cycle. As the last resort, hold BOOT across
power-on for the factory ISP; see `recovery.md`.

## The core's Tools menus

| Menu | Choices | Notes |
|---|---|---|
| Optimize `opt` | `oslto` (default from 0.3.0), `osstd` (the default before), `o1std`, `o2std`, `o3std`, `ogstd` | The games use `oslto` (`-Os -flto`). It is 1-5 KB smaller; CHChess and others only fit with it. |
| C library `rtlib` | `nano` (default), `nanofp`, `full` | |
| Peripherals `periph` | `game` (default), `full` | `game` adds `-DUART_MODULE_ONLY -DTIM_MODULE_ONLY`: no Serial1, `tone()`, PWM or HardwareTimer, which saves about 4 KB. |
| USB `usb` | `serial` (default), `uploadonly` | `uploadonly` saves 0.6-0.7 KB. Upload still works. A sketch that uses `Serial` then fails to build, on purpose. |

Defines for a sketch go in `--build-property build.extra_flags=...`. It is
empty on this platform. The `*_MODULE_ONLY` flags travel in
`build.flags.periph`; do not override `compiler.cpp.extra_flags`.

## Saving: flash pages instead of EEPROM

There is no EEPROM. The core's `EEPROM` library emulates 26 bytes in the
CH32V003's option bytes; on this chip its `commit()` is switched off (it writes
nothing and returns `false`, and including it prints a compiler message),
because rewriting the option bytes its way could leave the chip read-protected.
Instead:

- **Why it works.** The bootloader erases only the pages a new image covers.
  Pages between the end of the image and the metadata page at 0xF700
  survive re-uploads. This was proven on hardware by
  `platform/board/arduino/CHGame/libraries/CHGame/examples/Games/CHBlackjack/tools/probes/FlashProbe`.
- **Writing a page.** A sketch can erase and program a 256 B page from user
  mode in about 1.4 ms:
  - the code must run from SRAM (a RAMFUNC);
  - unlock with KEYR + MODEKEYR;
  - the controller wants the 0x08000000 alias of the address;
  - mask interrupts through CSR 0x800;
  - call `gfx_wait()` first, so no DMA flush is running.
- **What every game does** (the CHGame library's `chgame/Save.cpp`):
  - It uses two pages, **0xF500 and 0xF600**, in turn. Each record carries a
    magic, a version, a sequence number and a CRC, so a power cut can only
    lose the newest save.
  - Both pages fit only while the image is ≤ **50,432 B**. Up to 50,688 B
    it saves to the one page left, erasing it each time, so a power cut
    during a save loses everything saved; past that it switches saving off
    rather than overwrite code. The check uses `_data_lma + (_edata -
    _data_vma)`. A release build fails when the image leaves fewer pages
    than the game's `SAVE_PAGES` (`tools/game.py`, two by default).
  - **All games use the same two pages.** Each game must recognise only its
    own records by magic and version, and a new game's magic must differ
    from every other's (the collisions fixed on 2026-10-01 are in
    [status.md](status.md#save-magics-fixed-2026-10-01)).
- **The system settings block: not a sketch's to write.** The last 32 B
  of flash, 0xF7E0-0xF7FF (the end of the metadata page; `CHGAME_SYS_ADDR`
  in the core's `chgame_map.h`), are reserved for settings that belong to
  the handheld rather than to a game. None is defined yet
  ([spec/chgame.md](../spec/chgame.md#the-system-settings-block)).
  Bootloader version 4 keeps them across installs. A sketch must never
  erase or program the metadata page: the program installed is then
  invalid, and the block lost.

## Speed facts measured on this chip

- **Flash vs SRAM.** Code from flash runs at ~5 cycles per instruction (3
  wait states, no cache); code from SRAM at ~2. A function call per pixel
  from flash costs 2-3 µs. Put hot loops in SRAM. Each game's `RAMFUNC(name)`
  uses the `.gnu.linkonce.r.<prefix>.<name>` section trick from CHGfx 1.3.
  Every RAMFUNC costs its size in RAM as well.
- **newlib's `memmove`** is a byte loop in flash; write your own for big
  copies.
- **Frames.** A full-screen redraw of a busy game frame is 6-17 ms. The DMA
  flush itself (8.4 ms at 12 bpp) runs beside the CPU, but an async full
  flush still costs 2.5-2.9 ms of CPU for the chunk conversion (5.1 ms
  before CHGfx 1.3 put the converters in SRAM). Redraw only
  what changed (band-level dirty tracking), and draw static layers once.
- **Big outlined lettering** (mask + outline + shadow) costs 5-10 ms a word.
  Draw it once onto still screens, never per frame.
- **Logic and drawing.** Run logic at a fixed rate and let drawing catch up.
  A slow frame then costs smoothness, never game speed.
- **Flash budget.** The core with USB is about 6 KB and CHGfx about 7 KB.
  Sizeable wins from CHBlackjack:
  - `-Os` everywhere;
  - a 1.8 KB sound sequencer instead of a 6.5 KB library;
  - no `snprintf` (3.5 KB);
  - register GPIO instead of `pinMode` (2 KB);
  - no static constructors.

## C++ on this chip (coming from AVR/Arduboy)

| Assumption | Here |
|---|---|
| `int` is 16 bits | 32 bits |
| `double` is cheap | 64-bit software float, slow and ~8 KB. Use `float` or fixed point. |
| `PROGMEM`, `pgm_read_*`, `F()` | Flash is memory-mapped: plain reads |
| Unaligned access is free | Casting a byte array to `uint16_t*` gives unaligned loads; use `memcpy` |
| `min`/`max` are macros | `std::min`/`std::max`: both arguments must have the same type |
| `snprintf` is cheap-ish | It costs ~3.5 KB, has no `%l`, and its return value is unusable |
| `pinMode` is cheap | It pulls in ~2 KB of tables. GPIOB/GPIOC `CFGHR` is write-only: go through the core's shadows. |
| A static object costs nothing | Default member initialisers generate constructor code |
| `sq`, `map`, `word` are free names | They are Arduino macros and clash with identifiers |

## The SD card

See [sd-card.md](sd-card.md).
