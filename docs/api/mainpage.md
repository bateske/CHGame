# CHGame API reference {#mainpage}

The reference for every library the **%CHGame** board package installs. %CHGame
is a small open colour handheld: a WCH CH32X035 RISC-V microcontroller
(48 MHz, 62 KB flash, 20 KB SRAM), a 128x128 ST7735S colour LCD, a microSD
slot, eight buttons, a piezo speaker, a status LED and USB-C. It is
programmed from the Arduino IDE or `arduino-cli`, like an Arduboy.

## The libraries

| Library | Header | What it is for |
|---|---|---|
| @ref lib_chgame "CHGame" | `CHGame.h` | **Start here.** Everything a game needs: buttons and frame pacing, the house palette, drawing helpers and the 3x5 font, outlined lettering, effects maths, particles, sound and music, saving to flash, number formatting, and the debug protocol the simulator drives a game through. Includes %CHGfx. |
| @ref lib_chgfx "CHGfx" | `CHGfx.h` | The screen: a 16-colour framebuffer sent to the panel by DMA at up to 119 fps, sprites, shapes, text and fonts, partial updates and full-colour streaming. |
| @ref lib_chsd "CHSd" | `SdSpi.h`, `Fat.h` | Reading files from the microSD card (FAT16/FAT32, read-only). |
| @ref lib_core "SPI, Wire, EEPROM" | `SPI.h`, `Wire.h`, `EEPROM.h` | The standard Arduino libraries, ported to the chip. |

## A first sketch

```cpp
#include <CHGame.h>

void setup() {
    chgame.boot();                    // buttons; START held 3 s goes back to the menu
    gfx_begin(GFX_DIV2, GFX_12BPP);   // the panel: 128x128, 16 colours on screen
    pal::init();                      // the house colours (INK, WHITE, FELT, GOLD ...)
    chgame.setFrameRate(60);
}

void loop() {
    if (!chgame.nextFrame()) return;  // 60 times a second
    chgame.pollButtons();
    // ... game logic: chgame.pressed(LEFT_BUTTON), chgame.justPressed(A_BUTTON) ...
    pal::tick();

    gfx_wait();                       // the last frame has gone out: draw the next
    pal::commit();
    gfx_clear(FELT);
    text35x2s(10, 9, "HELLO", WHITE);
    gfx_flushAsync();                 // sent by DMA while the next frame's logic runs
}
```

@ref Hello.ino "examples/Hello" adds a sound effect and a counter saved in
flash. The twenty casino games under *File > Examples > %CHGame > Games* are
complete programs built on the same loop.

## Finding your way

- **Topics** (above) lists each library's parts: for %CHGame, the buttons,
  the palette, drawing, sound, saving and so on, each with an overview and
  every call it offers.
- **Classes**, **Namespaces** and **Files** index the same things by name:
  the `chgame` object is a @ref CHGame, the palette calls are in `pal::`,
  sound in `audio::`, saving in `save::`.
- **Examples** has the Hello sketch and %CHGfx's examples.
- The search box (top right) finds any function, constant or type.

## Coming from the Arduboy?

The %CHGame library is modelled on Arduboy2: one global object with the same
button names (`A_BUTTON`, `UP_BUTTON` ...), `nextFrame()`, `pollButtons()`,
`pressed()`, `justPressed()` and `everyXFrames()`. The differences: the
screen is 128x128 in 16 colours chosen from 4096, drawing is %CHGfx's
`gfx_*` calls, and a frame is sent with `gfx_flushAsync()` instead of
`display()`. [Getting started](https://github.com/bateske/CHGame/blob/main/docs/getting-started.md)
maps Arduboy2 calls to %CHGame's one by one.

## More

- [The %CHGame repository](https://github.com/bateske/CHGame): the board
  package, the bootloader and SD game menu, the games, the simulator and
  the PC tools.
- [Installing the board package](https://github.com/bateske/CHGame#readme)
  (Arduino Boards Manager URL:
  `https://github.com/bateske/CHGame/releases/latest/download/package_chgame_index.json`).
- [Performance notes](https://github.com/bateske/CHGame/blob/main/docs/performance.md)
  and [platform notes](https://github.com/bateske/CHGame/blob/main/docs/platform.md):
  what things cost on this chip.
