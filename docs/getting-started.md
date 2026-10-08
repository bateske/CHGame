# Writing for CHGame, coming from the Arduboy

CHGame is built to feel familiar to an Arduboy developer:
- the button names are the same;
- `nextFrame()` and `pollButtons()` work the same way;
- you can play your game on the PC before you put it on the device.

This page covers what is the same, what is different, and what happens behind the scenes, and walks through a first sketch.

One `#include <CHGame.h>` brings buttons, graphics, the house palette and drawing helpers, sound, saving and the debug protocol, as `Arduboy2.h` does. The [API reference](https://bateske.github.io/CHGame/) documents every call (as the Arduboy2 library's Doxygen pages do), and the library's [README](../platform/board/arduino/CHGame/libraries/CHGame/README.md) is the guide; all twenty games in `games/` are built on it.

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
   - Holding START for 3 s in any game goes back to it. The library does this for you (`chgame.startExits`).
   - Uploading from the IDE works from the menu or from a running game, with no buttons.

## Arduboy2 calls and their CHGame equivalents

`chgame` is a ready-made global, where an Arduboy2 sketch has `arduboy`. Graphics come from CHGfx (which `CHGame.h` includes): either the `gfx_*` functions the games use, or the `Gfx.` object, whose method names follow Adafruit_GFX and Arduboy2. The library adds the house style on top: named colours, panels, sprites, the 3x5 font, lettering.

| Arduboy2 | CHGame |
|---|---|
| `arduboy.begin()` | `chgame.boot(); gfx_begin(GFX_DIV2, GFX_12BPP); pal::init();` (or `gfx_setPalette(yours, 16)`) |
| `setFrameRate`, `nextFrame`, `everyXFrames`, `frameCount` | the same |
| `pollButtons`, `pressed`, `anyPressed`, `justPressed`, `justReleased` | the same, plus `repeat(b)` for auto-repeat; `notPressed(b)` is `!anyPressed(b)` |
| `A_BUTTON` … `RIGHT_BUTTON` | the same, plus `START_BUTTON`, `SELECT_BUTTON` |
| `clear()` | `gfx_clear(colour)` |
| `display()` | `gfx_flushAsync()` (with `gfx_wait()` before the next drawing), or `gfx_flush()` to wait. `gfx_flushRectAsync()` sends only part of the screen. |
| `drawPixel`, `drawLine`, `drawRect`, `fillRect`, `drawCircle`, `fillCircle`, `drawRoundRect`, `fillRoundRect`, `drawFastHLine`, `drawFastVLine` | `gfx_pixel`, `gfx_line`, `gfx_rect`, `gfx_fillRect`, `gfx_circle`, `gfx_fillCircle`, `gfx_roundRect`, `gfx_fillRoundRect`, `gfx_hline`, `gfx_vline`, or `Gfx.` with the Arduboy names |
| `drawBitmap`, `Sprites::drawOverwrite` / `drawPlusMask` | `gfx_blit(spr, x, y, w, h, transparent)` for 4 bpp images; `gfx_sprite4(spr, x, y, remap, scale)` for packed sprites that can be scaled and recoloured (make them with `extras/sprite4.py`) |
| `setCursor` + `print` | `text35(x, y, "TEXT", colour)` (the 3x5 font), `text35x2` (twice the size), or CHGfx's `gfx_text` (5x7) and `gfx_setFont()` for larger fonts. There is no cursor or `Print` stream; format numbers into a buffer with `fmtInt`, `fmtMoney` ... (`snprintf` costs 3.5 KB). |
| `BLACK`, `WHITE`, `invert()` | the house colours `INK`, `WHITE`, `GOLD` ... (`pal::init()`), or your own palette; `gfx_setInverted()` |
| `setRGBled`, `digitalWriteRGB` | `audio::led(pattern)`, or `digitalWrite(LED_BUILTIN, …)` |
| `ArduboyTones`, `audio.on()`/`off()` | `audio::sfx(effect)` from a table of your effects, `audio::blip(hz, ms)`, `audio::music(score)` / `audio::melody(m)`, `audio::setOn(on)`. Arduino's `tone()` is compiled out by the default *Peripherals* setting. |
| `EEPROM.put`/`get` | `save::store(MAGIC, version, data)` / `save::load(...)`: up to 244 bytes, kept across power cycles and re-uploads. The core's `EEPROM` library does not save on this chip (`commit()` writes nothing). |
| `initRandomSeed()` | `randomSeed(micros())` once the player has pressed something; for presentation, `fx::rnd()` (repeatable in the simulator) |
| `PROGMEM`, `pgm_read_byte`, `F()` | not needed: `const` data stays in flash and is read normally |
| `exitToBootloader()` | `chgame.exitToMenu()` (the SD menu) |
| `idle()`, `boot` logo, `systemButtons()` | none |

## A first sketch

The library's example [Hello](../platform/board/arduino/CHGame/libraries/CHGame/examples/Hello/Hello.ino)
is a whole sketch in sixty lines: a ball to steer, a sound effect, a counter
saved in flash, the felt re-dyed with B. Its loop is the one every game
uses:

```cpp
void loop() {
    dbg::poll();                          // the simulator and tools/device.py talk through this
    if (!chgame.nextFrame()) return;

    // Logic.
    chgame.pollButtons();
    if (chgame.pressed(LEFT_BUTTON) && x > 8) x--;
    // ...
    if (chgame.justPressed(A_BUTTON)) audio::sfx(0);
    pal::tick();
    audio::update();

    // Drawing.
    gfx_wait();                           // the last frame has been sent
    pal::commit();
    gfx_clear(FELT);
    text35x2s(10, 9, "HELLO", WHITE);
    gfx_fillCircle(x, y, 7, FX_A);        // FX_A cycles through a rainbow by itself
    gfx_flushAsync();                     // DMA sends it while loop() runs again
}
```

It uses 10.8 KB of flash and 11.9 KB of RAM, most of the RAM being the
8 KB framebuffer.

**To build it:**
- **From the repository** (the library and CHGfx come from `platform/board/arduino/CHGame/libraries`):
  ```bash
  chgame --sketch Hello build
  chgame --sketch Hello upload
  ```
- **Arduino IDE:**
  1. Install the CHGame board package, 0.3.0 or later ([README](../README.md#1-install-the-board-package)).
     The CHGame and CHGfx libraries come with it. (With 0.2.4, copy
     `platform/board/arduino/CHGame/libraries/CHGfx` and `.../CHGame` into
     your sketchbook's `libraries/`, and choose *Tools > Optimize >
     Smallest + LTO*.)
  2. Open *File > Examples > CHGame > Hello*, then *Upload*. *Tools >
     Optimize* is *Smallest + LTO* by default.

**The Tools menus:**
- *Peripherals: Game* (the default) leaves out `Serial1`, `tone()` and PWM, which saves about 4 KB.
- *USB: Upload only* drops `Serial`, which saves about 0.7 KB. Uploading still needs no buttons. (`tools/device.py` sets both for a release build.)

### Running it on the PC

The simulator (`tools/chsim`) compiles a sketch with the real CHGfx drawing
code and runs it in lockstep, producing screenshots and GIFs. It drives the
sketch through the library's **serial debug protocol** (`dbg::begin()` in
`setup()`, `dbg::poll()` in `loop()`), so any sketch on the library can be
scripted:

```bash
chgame --sketch Hello run myscript.txt out/hello
```

A script is a list of `wait 30`, `tap A`, `hold RIGHT`, `snap name`,
`gif name 40 2` ... (the full list is at the top of
`tools/chsim/chdrivelib.py`). The same script runs on the board against a
debug build (`chgame build --debug`), so the screenshots can be
compared.

### Sharing it

A `.chgame` file is how CHGame games travel, as `.arduboy` files do for the
Arduboy: a ZIP with the program, its title, credits, pictures and the files
it reads from the SD card. Uploaders, card builders and emulators take it as
it is.

```bash
chgame --sketch Hello export        # build/Hello.chgame
```

What goes in comes from the sketch's `chgame.json`. Every key is optional:

```json
{"title": "HELLO", "author": "you", "genre": "Demo", "license": "MIT",
 "url": "https://example.com/hello"}
```

- **Defaults** fill in the rest: the folder's name in capitals for the
  title, the version from `config.h`, the README's first paragraph,
  `LICENSE` and `NOTICE`, the `sdcard/` folder (its tree goes onto the
  card's root). `docs/gameplay.gif` stays out of the cart; a game without
  a `docs/cart.png` gets a picture of its title drawn over its first frame.
- **On a CHGame:** `chgame cart deploy build/Hello.chgame` flashes it.
  Give it `--card E:\` with the card mounted, and it also lands in the
  menu, with its SD files.
- **Several games in one cart:** `chgame cart new MyCart.chgame Hello.chgame
  CHFour ...`, then `add`, `remove`, `order`, `set --game ID folder=PUZZLES`,
  `launch ID` (the game started at power-on), `background menu.png`.
- **The format** is [spec/chgame.md](../spec/chgame.md).

## A real game

Copy the game closest to yours. CHFour is small and recent, and has the full tooling: `check.py`, tests, scripts and the asset pipeline. Then follow [CLAUDE.md's "Starting a new game"](../CLAUDE.md#starting-a-new-game). From the library you already have the frame loop's parts, the palette effects, the sound engine, saving, the debug protocol and the simulator; the game folder holds its rules, its screens, its art, its sounds and its scripts.

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

   A full flush costs about 2.5-2.9 ms of CPU for the conversion. The games redraw only what changed, and draw still lettering once.

**Code in RAM.** Flash has three wait states and no cache, so code from flash runs at about a third of the speed of code from SRAM. Hot loops are marked `RAMFUNC(name)` to run from SRAM ([performance.md](performance.md)).

**The simulator** compiles the same sources for the PC, with stand-ins for the SPI/DMA and the timer. Time is virtual, so scripted runs give the same frames every time. That makes "pixels are the test" possible: a change that should not alter the picture must give identical frames.
