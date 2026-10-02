# Writing for CHGame, coming from the Arduboy

CHGame is built to feel familiar to an Arduboy developer:
- the button names are the same;
- `nextFrame()` and `pollButtons()` work the same way;
- you can play your game on the PC before you put it on the device.

This page covers what is the same, what is different, and what happens behind the scenes. It ends with a sketch you can build today.

> **Where things stand.** The plan is one `#include <CHGame.h>` that brings buttons, graphics, sound, saving and the debug protocol, as `Arduboy2.h` does ([chgame-library.md](chgame-library.md)). **That library does not exist yet.** Today a sketch uses the CHGfx graphics library, plus a copy of the small `CHGame.h` that every game carries. This page shows both: how it works now, and what will change.

## The machine

| | Arduboy | CHGame |
|---|---|---|
| CPU | ATmega32U4, 8-bit, 16 MHz | CH32X035, 32-bit RISC-V, 48 MHz |
| Flash for a sketch | 28 KB | **50,944 B** (the bootloader with the game menu takes 12 KB) |
| RAM | 2.5 KB | **20 KB**, of which a sketch may use 18,416 B statically; the stack is 2 KB |
| Screen | 128x64, 1 bit | **128x128, 16 colours out of 4,096** (or 65,536 at 16 bpp), ST7735S over SPI |
| Buttons | 6 | **8**: the Arduboy six plus START and SELECT |
| Sound | two-pin piezo | one piezo, driven by a timer |
| LED | RGB | one status LED |
| Storage | 1 KB EEPROM | **no EEPROM**: two 256 B flash pages for saves, and a microSD card |
| USB | upload + Serial | upload with no buttons, + Serial |

[platform.md](platform.md) has the pins, the memory map and measured speeds. Its section [C++ on this chip](platform.md#c-on-this-chip-coming-from-avrarduboy) lists the AVR habits that do not apply here. For example, `int` is 32 bits, and `PROGMEM` is not needed.

## The four things that are different

1. **Colours are palette indices.** The framebuffer has 4 bits a pixel: 8 KB for 128x128. A colour is a number 0-15, and the palette (16 RGB565 values) decides what each number looks like. Changing a palette entry recolours every pixel that uses it, at no cost; the games use this for fades, flashes and cycling colours.
2. **The screen is sent in the background.** `gfx_flushAsync()` starts sending the frame by DMA and returns at once.
   - The next frame's logic runs while the picture goes out (about 8 ms at 12 bpp).
   - Before you draw again, call `gfx_wait()`.
   - Drawing into rows that are still being sent shows as tearing on the device. In the simulator it is reported as a `BUG:` line.
3. **Saving writes flash, not EEPROM.**
   - The games keep their settings and a game in progress in two flash pages that survive uploads ([platform.md](platform.md#saving-flash-pages-instead-of-eeprom)).
   - A save takes about 1.4 ms, and must run after `gfx_wait()`.
   - All games share the pages, and each recognises its own records by a magic number.
4. **There is a game menu.**
   - The bootloader shows the games on the SD card at power-on ([sd-menu.md](sd-menu.md)).
   - Holding START for 3 s in any game goes back to it. `CHGame.h` does this for you (`arduboy.startExits`).
   - Uploading from the IDE works from the menu or from a running game, with no buttons.

## Arduboy2 calls and their CHGame equivalents

`arduboy` is a ready-made global, as in Arduboy2 sketches. Graphics come from CHGfx: either the `gfx_*` functions the games use, or the `Gfx.` object, whose method names follow Adafruit_GFX and Arduboy2. The sound, save and number-formatting calls below are each game's own modules (`src/audio`, `src/save`, `src/gfx/Fmt`) until the library collects them.

| Arduboy2 | CHGame today |
|---|---|
| `arduboy.begin()` | `arduboy.boot(); gfx_begin(GFX_DIV2, GFX_12BPP); gfx_setPalette(pal, 16);` |
| `setFrameRate`, `nextFrame`, `everyXFrames`, `frameCount` | the same |
| `pollButtons`, `pressed`, `anyPressed`, `justPressed`, `justReleased` | the same, plus `repeat(b)` for auto-repeat; `notPressed(b)` is `!anyPressed(b)` |
| `A_BUTTON` … `RIGHT_BUTTON` | the same, plus `START_BUTTON`, `SELECT_BUTTON` |
| `clear()` | `gfx_clear(colour)` |
| `display()` | `gfx_flushAsync()` (with `gfx_wait()` before the next drawing), or `gfx_flush()` to wait. `gfx_flushRectAsync()` sends only part of the screen. |
| `drawPixel`, `drawLine`, `drawRect`, `fillRect`, `drawCircle`, `fillCircle`, `drawRoundRect`, `fillRoundRect`, `drawFastHLine`, `drawFastVLine` | `gfx_pixel`, `gfx_line`, `gfx_rect`, `gfx_fillRect`, `gfx_circle`, `gfx_fillCircle`, `gfx_roundRect`, `gfx_fillRoundRect`, `gfx_hline`, `gfx_vline`, or `Gfx.` with the Arduboy names |
| `drawBitmap`, `Sprites::drawOverwrite` / `drawPlusMask` | `gfx_blit(spr, x, y, w, h, transparent)` for 4 bpp images; `gfx_sprite4(spr, x, y, remap, scale)` for packed sprites that can be scaled and recoloured (make them with `extras/sprite4.py`) |
| `setCursor` + `print` | `gfx_text(x, y, "text", colour)` (5x7), `gfx_setFont()` for larger fonts. There is no cursor or `Print` stream; format numbers into a buffer (the games' `fmtInt`; `snprintf` costs 3.5 KB). |
| `BLACK`, `WHITE`, `invert()` | your own palette indices; `gfx_setInverted()` |
| `setRGBled`, `digitalWriteRGB` | the games' `audio::led(pattern)`, or `digitalWrite(LED_BUILTIN, …)` |
| `ArduboyTones`, `audio.on()`/`off()` | the games' `audio::sfx(effect)`, `audio::blip(hz, ms)`, `audio::setOn(on)` (`src/audio`). Arduino's `tone()` is compiled out by the default *Peripherals* setting. |
| `EEPROM.put`/`get` | the games' `save::store` / `save::load` (`src/save`). The core's `EEPROM` library emulates only 26 bytes. |
| `initRandomSeed()` | `randomSeed(micros())` once the player has pressed something; the games use their own xorshift `fx::rnd` |
| `PROGMEM`, `pgm_read_byte`, `F()` | not needed: `const` data stays in flash and is read normally |
| `exitToBootloader()` | `arduboy.exitToMenu()` (the SD menu) |
| `idle()`, `boot` logo, `systemButtons()` | none |

## A first sketch, today

This builds as it stands, in the Arduino IDE or with `arduino-cli`. It uses 7,756 B of flash and 11,608 B of RAM, most of the RAM being the 8 KB framebuffer.

1. Make a sketch folder `Hello/`.
2. Copy `games/CHFour/src/CHGame.h` and `CHGame.cpp` into `Hello/src/`. They are the same in every game.
3. Write `Hello/Hello.ino`:

```cpp
// Hello - a square that moves with the D-pad and turns green while A is held.
#include <CHGfx.h>
#include "src/CHGame.h"         // copied from games/CHFour/src/CHGame.h and .cpp

enum : uint8_t { BLACK, WHITE, RED, GREEN };    // palette indices, not colours
static const uint16_t palette[4] = { 0x0000, 0xFFFF, 0xF800, 0x07E0 };   // RGB565

static int x = 60, y = 60;

void setup() {
    arduboy.boot();                         // the eight buttons
    gfx_begin(GFX_DIV2, GFX_12BPP);         // panel on, 24 MHz SPI, 12 bpp out
    gfx_setPalette(palette, 4);
    arduboy.setFrameRate(60);
}

void loop() {
    if (!arduboy.nextFrame()) return;
    arduboy.pollButtons();
    if (arduboy.pressed(LEFT_BUTTON)  && x > 0)   x--;
    if (arduboy.pressed(RIGHT_BUTTON) && x < 120) x++;
    if (arduboy.pressed(UP_BUTTON)    && y > 12)  y--;
    if (arduboy.pressed(DOWN_BUTTON)  && y < 120) y++;

    gfx_wait();                             // the last frame has been sent
    gfx_clear(BLACK);
    gfx_text(4, 2, "HELLO CHGAME", WHITE);
    gfx_fillRect(x, y, 8, 8, arduboy.pressed(A_BUTTON) ? GREEN : RED);
    gfx_flushAsync();                       // DMA sends it while loop() runs again
}
```

**To build it:**
- **Arduino IDE:**
  1. Install the CHGame board package ([README](../README.md#installing)).
  2. Copy `platform/libraries/CHGfx` into your sketchbook's `libraries/`.
  3. Choose *Tools > Optimize > Smallest + LTO*, then *Upload*.
- **arduino-cli, from the repository:**
  ```bash
  arduino-cli compile -b CHGame:ch32v:CHGame:opt=oslto,rtlib=nano,periph=game,usb=uploadonly \
      --library platform/libraries/CHGfx path/to/Hello
  arduino-cli upload -b CHGame:ch32v:CHGame -p <port> path/to/Hello
  ```

**The Tools menus:**
- *Peripherals: Game* (the default) leaves out `Serial1`, `tone()` and PWM, which saves about 4 KB.
- *USB: Upload only* drops `Serial`, which saves about 0.7 KB. Uploading still needs no buttons.

### Running it on the PC

The simulator (`tools/chsim`) compiles a sketch with the real CHGfx drawing code and runs it in lockstep, producing screenshots and GIFs. It drives the sketch through the **serial debug protocol**: screenshot, hold buttons, run *n* frames. A sketch that does not speak the protocol builds (`python tools/chsim/chsim.py build path/to/Hello`) but stays paused.

Today the protocol lives in each game's `src/debug/`. To simulate your own sketch, start from a game, as the next section describes. Moving the protocol into the library, so that every sketch gets the simulator for free, is one of the main reasons for the library.

## A real game, today

Copy the game closest to yours. CHFour is small and recent, and has the full tooling: `check.py`, tests, scripts and the asset pipeline. Then follow [CLAUDE.md's "Starting a new game"](../CLAUDE.md#starting-a-new-game). You get everything the games have:
- the frame loop;
- the palette effects;
- the sound sequencer;
- saving;
- the debug protocol;
- the simulator scripts;
- the size report.

[game-anatomy.md](game-anatomy.md) explains how a game is put together, and [performance.md](performance.md) what costs time on this chip.

## Behind the scenes

**When the board is switched on:**
- The bootloader (12 KB at 0x0000) runs first.
- It shows the SD card's games, with the installed one preselected. A starts it.
- A game is installed from the card only after it has been checked completely.
- The sketch itself lives at 0x3000 ([memory-map.md](../platform/board/docs/memory-map.md), [boot-flow.md](../platform/board/docs/boot-flow.md)).

**An upload:**
- `chgame-upload` touches the USB serial port at 1200 baud, the sketch resets into the bootloader, and the image is written and verified in about half a second.
- After an upload the sketch starts directly.

**One frame of a game:**
1. Logic runs at a fixed 60 Hz. If drawing fell behind, up to three logic ticks run back to back.
2. `gfx_wait()`, then the frame is drawn into the 8 KB framebuffer.
3. `gfx_flushAsync()` sends it. CHGfx converts each pair of rows through the palette into a small buffer and DMA sends it at 24 MHz SPI, while the CPU is already working on the next frame.

   A full flush costs about 5 ms of CPU for the conversion. The games redraw only what changed, and draw still lettering once.

**Code in RAM.** Flash has three wait states and no cache, so code from flash runs at about a third of the speed of code from SRAM. Hot loops are marked `RAMFUNC(name)` to run from SRAM ([performance.md](performance.md)).

**The simulator** compiles the same sources for the PC, with stand-ins for the SPI/DMA and the timer. Time is virtual, so scripted runs give the same frames every time. That makes "pixels are the test" possible: a change that should not alter the picture must give identical frames.
