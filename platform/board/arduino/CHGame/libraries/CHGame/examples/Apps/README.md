# Apps/

Sketches for the CHGame that are not games. They are examples of the CHGame
library, like the games beside them in `../Games/`, so the Arduino IDE lists
them under *File > Examples > CHGame > Apps*.

| Sketch | What it does | Licence |
|---|---|---|
| [CHStlView](CHStlView) | A 3D wireframe viewer for `.STL` files on the SD card: the models you would send to a 3D printer, streamed off the card every frame and turned, zoomed and spun in your hands. Reads the card with CHSd. | MIT |
| [CHSDtoUSB](CHSDtoUSB) | Turns the CHGame into a USB microSD card reader. A PC sees the card as a drive, and the board's serial port keeps working beside it, so uploads need no button presses. Its screen is an instrument panel for the card: a graph of every command, the files the PC creates, deletes and renames by name, the speed, the fill, the card's identity. Use it to put game data on the card without taking the card out. The steps are in the root [CLAUDE.md](../../../../../../../../CLAUDE.md). | GPL-3.0 |
| [CHSDtoSerial](CHSDtoSerial) | The helper the CHGame website uploads to manage the SD card over USB. [play.chgame.website](https://play.chgame.website) reads and writes the card through a framed serial protocol ([its PROTOCOL.md](CHSDtoSerial/PROTOCOL.md)) instead of mounting it as a drive: installs games, backs the card up, reads files back, all without taking the card out. CHSDtoUSB's cousin, with the same SD driver and the same instrument panel, in the website's palette. | GPL-3.0 |

All three are drawn in the same "secret agent" style: a spy's wristwatch. It is
CHSDtoUSB's instrument panel taken apart into `Agent.h`/`Agent.cpp`
(status bar, seven-segment readouts, gauges, chips, tabs, brackets, the
alert box), one file carried by each; its colours are roles each app fills
with its own: CHSDtoUSB green on black, CHSDtoSerial the website's lime and
grey-greens, CHStlView the blue-teal of its wires. All use the library's
Sizzle with its particles off.

CHSDtoUSB and CHSDtoSerial have their own SD driver: read-write,
CRC-checked, with DMA. It comes from sdfatlib, which is why both sketches
are GPL. Keep that code inside each sketch. The games use the
MIT-licensed, read-only [CHSd](../../../CHSd) instead. CHSDtoSerial builds
with *USB: Serial* (its serial port is the website's protocol); its README
and NOTES describe it.

Build it from this folder (the board package 0.3.0 brings CHGfx; it has been tested on the board with `-Os`, hence `opt=osstd`):

```bash
cd platform/board/arduino/CHGame/libraries/CHGame/examples/Apps/CHSDtoUSB
arduino-cli compile -b CHGame:ch32v:rev0:opt=osstd .
arduino-cli upload  -b CHGame:ch32v:rev0:opt=osstd -p <PORT> .
```

`tools/chsd_test.py` is its hardware test suite. It needs a test build
(`--build-property build.extra_flags=-DCHSD_TEST=1`) and runs on Windows;
see its README.

## Elsewhere

- **FlashProbe** is a probe sketch that proved a sketch can erase and
  program flash pages, and that those pages survive a re-upload. Every
  game's save system rests on that. It stays with the game that first
  needed it, in
  [platform/board/arduino/CHGame/libraries/CHGame/examples/Games/CHBlackjack/tools/probes/FlashProbe](../Games/CHBlackjack/tools/probes/FlashProbe),
  because that game's source refers to it. It is left out of the board
  package (a sketch inside a game's folder would show in *File > Examples*
  nested in the game), so it is only in the repository.
