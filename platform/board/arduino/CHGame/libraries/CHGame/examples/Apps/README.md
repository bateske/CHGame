# Apps/

Sketches for the CHGame that are not games. They are examples of the CHGame
library, like the games beside them in `../Games/`, so the Arduino IDE lists
them under *File > Examples > CHGame > Apps*.

| Sketch | What it does | Licence |
|---|---|---|
| [CHSDtoUSB](CHSDtoUSB) | Turns the CHGame into a USB microSD card reader. A PC sees the card as a drive, and the board's serial port keeps working beside it, so uploads need no button presses. Use it to put game data on the card without taking the card out. The steps are in the root [CLAUDE.md](../../../../../../../../CLAUDE.md). | GPL-3.0 |

CHSDtoUSB has its own SD driver: read-write, CRC-checked, with DMA. It
comes from sdfatlib, which is why the sketch is GPL. Keep that code inside
this sketch. The games use the MIT-licensed, read-only
[CHSd](../../../CHSd) instead.

Build it from this folder against the repository's CHGfx:

```bash
cd platform/board/arduino/CHGame/libraries/CHGame/examples/Apps/CHSDtoUSB
arduino-cli compile -b CHGame:ch32v:CHGame --library ../../../../CHGfx .
arduino-cli upload  -b CHGame:ch32v:CHGame -p <PORT> .
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
