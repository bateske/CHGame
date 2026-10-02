# The `CHGame` library: design

This is the design for the one library the board package is to carry, with `CHGame.h` as its single include. It plays the part that `Arduboy2.h` plays for the Arduboy.

- **Status:** a design. Nothing here exists yet.
- **What it is built from:** the code the twenty games already share. [unification.md](unification.md) measures how alike their copies are.
- **What it fills in:** step 3 of [roadmap.md](roadmap.md).

## What a sketch will look like

```cpp
#include <CHGame.h>

static int x = 60, y = 60;

void setup() {
    arduboy.boot();                         // buttons
    gfx_begin(GFX_DIV2, GFX_12BPP);         // the panel, 24 MHz SPI, 12 bpp out
    chgame::pal::init();                    // the house palette (INK, WHITE, FELT, ...)
    arduboy.setFrameRate(60);
}

void loop() {
    chgame::dbg::poll();                    // the debug protocol: no code without CHGAME_DEBUG
    if (!arduboy.nextFrame()) return;
    arduboy.pollButtons();
    if (arduboy.pressed(LEFT_BUTTON))  x--;
    if (arduboy.pressed(RIGHT_BUTTON)) x++;
    if (arduboy.justPressed(A_BUTTON)) chgame::audio::blip(1500, 30);

    gfx_wait();                             // the last frame has left the framebuffer
    gfx_clear(chgame::pal::FELT);
    gfx_fillRect(x, y, 8, 8, chgame::pal::WHITE);
    gfx_flushAsync();                       // sent by DMA while the next frame is computed
}
```

**What the sketch gets for that one include:**
- buttons and frame pacing;
- the graphics;
- the house palette;
- sound;
- saving;
- the START-held-3-s exit to the menu;
- the debug protocol.

Because of the debug protocol, **the sketch runs in the PC simulator with no code of its own.** Today a new sketch has to copy a game's `debug/` folder to get that: the simulator starts every sketch paused and steps it only through the protocol.

## Layout

```
platform/libraries/CHGame/              (bundled at release as <package>/libraries/CHGame)
  library.properties                    name=CHGame, includes=CHGame.h, depends=CHGfx, CHSd
  src/CHGame.h                          the one include: every module below
  src/chgame/Input.h/.cpp               class CHGame, `arduboy`, buttons, pacing, exit to menu
  src/chgame/RamFunc.h                  CHGAME_RAMFUNC(name)
  src/chgame/Frame.h/.cpp               chgame::run(update, render): the frame loop
  src/chgame/Save.h/.cpp                chgame::save: the two-page engine
  src/chgame/Debug.h/.cpp               chgame::dbg: the serial protocol
  src/chgame/Audio.h/.cpp               chgame::audio: the piezo sequencer and the LED
  src/chgame/Fmt.h/.cpp                 chgame::fmtInt, fmtMoney, ...
  src/chgame/Palette.h/.cpp             chgame::pal: the staged house palette
  src/chgame/Draw.h/.cpp, Mask.h/.cpp   the house drawing helpers and the 3x5 font
  src/chgame/Fx.h/.cpp                  isin, ease, rnd, particles, shake
  examples/                             filled at release from games/ (roadmap step 4)
```

**CHGfx and CHSd stay separate libraries.** `CHGame.h` includes `<CHGfx.h>`, so a sketch never names it. CHSd is included only by sketches that use the card, through `<CHSd.h>`, so its 24 B of RAM are paid only where needed. Keeping them separate also keeps their own tests, `extras/` and versions.

**Namespaces.** Library code lives in `namespace chgame`. The Arduboy-style names stay global:
- the class `CHGame` and its instance `arduboy`;
- the button masks `A_BUTTON` … `SELECT_BUTTON`.

A game's own `pal`, `audio` or `fx` can then sit beside the library's while it moves over.

## The modules

Each module is listed with the per-game parts that become parameters. "Same as today" means the code is taken from the games as it is.

### Input, pacing, exit (`Input`)

- **Same as today:** the API of `games/*/src/CHGame.h` (identical in all twenty).
  ```cpp
  boot(); setFrameRate(fps); nextFrame(); pollButtons();
  pressed(b); anyPressed(b); justPressed(b); justReleased(b); repeat(b, delay, rate);
  everyXFrames(n); exitToMenu(); frameCount; startExits; injected; lockstep
  ```
- **Pragma:** take whichever of the four `#pragma GCC optimize` lines is smallest.
- **Simulator:** keeps providing `chgame_readButtons()` (`tools/chsim/host/main.cpp`).

### `CHGAME_RAMFUNC(name)`

```cpp
#define CHGAME_RAMFUNC(name) __attribute__((section(".gnu.linkonce.r.chg." #name), noinline))
```

- **The prefix `chg.`** is for library functions only.
- **Games can keep their own `RAMFUNC`** with a game prefix, so a game's `save` and the library's `save` never merge (see [unification.md](unification.md#the-constraints-every-step-has-to-meet)).

### The frame loop (`Frame`)

```cpp
namespace chgame {
struct Loop {
    void (*update)();                       // one logic tick (60 Hz)
    bool (*render)(uint32_t frame);         // false: nothing changed, the frame is sent again
    bool commitFirst;                       // pal::commit() before gfx_wait() (the CHBlackjack lineage)
};
bool run(const Loop &l);                    // true if a frame was due and ran
}
```

- **What it does:** the steps every game runs today:
  - `dbg::poll`;
  - up to three ticks of `pollButtons`, `pal::tick`, `audio::update` and `update`;
  - then `gfx_wait`, `pal::commit`, `render` and `gfx_flushAsync`.
- **`commitFirst`** keeps the eight games that commit the palette first frame-for-frame identical.
- **CHChess and CHCheckers** keep their own loop, because they draw from a second stack while the search runs.

### Saving (`Save`)

```cpp
namespace chgame::save {
bool available();                            // false: the image reaches the pages, or a write failed
bool read(uint32_t magic, uint8_t version, void *payload, uint16_t n, bool *flag = nullptr);
bool write(uint32_t magic, uint8_t version, const void *payload, uint16_t n, bool flag = false);
void allowWrites(bool on);                   // device debug builds: off until the debug E command
constexpr uint32_t magic(char a, char b, char c, char d);   // magic('C','H','F','4')
}
```

- **The engine owns the record format** that 19 games use today: header, sequence, CRC, the two pages 0xF500/0xF600 in turn, and the RAMFUNC write from `gfx_chunkScratch()` after `gfx_wait()`.
- **The game owns** its payload struct and its magic. The magic must stay unique (CLAUDE.md rule 8).
- **`flag`** is the "a game in progress" byte. CHPoker and CHSolitaire don't use it.
- **CHBlackjack's older header** is the one exception. That game either keeps its `Save.cpp`, or `read()` learns its layout once.

### The debug protocol (`Debug`)

```cpp
namespace chgame::dbg {
void begin(const char *id);                  // "CHF4 0.1": the ? answer
void poll();
extern bool (*hook)(char cmd, const char *args);   // the game's own commands
void paintStack(); void markUpdateStart(); void markRenderStart(); void markRenderEnd();
void print(const char *s);
uint32_t parseNum(const char *&p, uint8_t base);
void prof(uint8_t slot);                     // CHGAME_PROFILE
bool holdGame(char cmd); void waitInput();  // the optional pieces some games use
}
```

- **What it covers:** the full protocol (`?`, `S`, `K`, `L`, `N`, `P`, `T`, `B`) with a 100-byte line.
- **When it is compiled:** only with `CHGAME_DEBUG=1`. Every function is an empty inline otherwise, as today.
- **The handshake id** is passed at run time, because library code cannot see the game's `config.h`. This keeps CHChess's `CHCS`.
- **CHBlackjack** either keeps its copy or moves to the common answers together with its `chdrive.py`.

### Sound (`Audio`)

```cpp
namespace chgame::audio {
struct Step { uint16_t hz, endHz, ms; };            // hz 0 = rest
struct Effect { const Step *steps; uint8_t n, priority; bool soft; };
void begin(const Effect *table, uint8_t count, bool on);
void setOn(bool on);  bool on();
void sfx(uint8_t id);                                // an index into the game's table
void blip(uint16_t hz, uint16_t ms, bool soft = false);
void tone(uint16_t hz, bool smooth);
bool playing();
void update();                                       // once a frame: the LED patterns
enum Led : uint8_t { LED_OFF, LED_BLINK, LED_TRIPLE, LED_PARTY };
void led(Led pattern);
}
```

- **The engine** is the superset of the fourteen engines in the games: 6-byte steps, soft pulse, glide and modes.
- **Music** is the Playtune score player shared by CHBingo, CHRoulette and CHWordWheel, behind `CHGAME_AUDIO_MUSIC`.
- **The effect tables stay with each game.** The five games with 3-byte steps get their tables converted by a script, and their preview hashes must not change.

### The house style (`Fmt`, `Palette`, `Draw`, `Mask`, `Fx`)

- **`Fmt`:** the union of the games' functions (`fmtInt`, `fmtMoney`, `fmtStr`, `fmtShort`, `fmtTime`, `fmtCash`). They replace `snprintf`, which costs 3.5 KB.
- **`Palette`** (`chgame::pal`):
  - the 16-colour `BASE` table and its names (`INK`, `WHITE`, … `FX_A`, `FX_B`), which 19 games share;
  - staged changes, fade, flash, desaturate, colour cycling;
  - themes and modes are tables the game passes in.
- **`Draw` and `Mask`:**
  - `fillRound`, `roundRect`, `dither`, `glyph`;
  - `sprite4` with null remap, flip and mirror, and `spriteRot`;
  - the 3x5 font (`text35`, `text35x2`, `text35Width`);
  - outlined banner lettering (`maskBegin`, `maskText35`, `maskDraw`).

  These are the games' smaller copies of what CHGfx also offers. The library keeps both, and a sketch uses either.
- **`Fx`:** `isin`, `ease`, the xorshift `rnd`, a particle pool sized by the game, and `shake`. Particle kinds and banners stay with the games.

## Configuration

Library code is compiled without the sketch's folder in view, so its switches are generic and arrive as build flags:

| Flag | Default | Set by |
|---|---|---|
| `CHGAME_DEBUG` | 1 under `CHSIM`, else 0 | `tools/device.py build --debug` (beside the game's own `<PFX>_DEBUG`), the simulator |
| `CHGAME_PROFILE` | 0 | by hand |
| `CHGAME_AUDIO_MUSIC` | 0 | the games with scores |

A game keeps its own `config.h` for its own switches. Settings the library needs from the game at run time are passed as arguments: the debug id, the effect table, the save magic and the palette themes.

## What stays in a game

- **Its rules, AI and logic:** `game/`, `rules/`, `ai/`, `engine/`.
- **Everything drawn and animated:** `stage/`, `render/`, `states/`, `fx/Presenter`, banners, particle kinds.
- **Its data:** effect and music tables, the save payload and magic, the palette themes.
- **Its art:** `assets/`, generated by `tools/assets.py`.
- **Its tools:** `tools/`: `chdrive.py` commands, scripts, tests, `device.py`.

## Moving the games over

**Each step is done for all twenty games, and it is finished only when:**
- every simulator script of every game gives the same frames as before (`tools/check.py --compare`, or the frame hashes);
- every game's release image is no larger (`python tools/device.py build`);
- the host tests and the audio preview hashes are unchanged.

**One rule throughout:** a game moves a module over in one commit. Delete its copy, change the include, and build. Its `src/CHGame.h` and the library's `CHGame.h` must never both be in play.

| Step | What | Risk |
|---|---|---|
| A. Tooling | `chsim.py`: a library resolver beside `chgfx_dir()` that compiles `CHGame/src/**`. `device.py` (20 copies) and `mkcard.py`: `--library platform/libraries/CHGame` and `-DCHGAME_DEBUG=1`. `audio/preview.py`: the library's audio source. A CI job for sizes and frames. | none: no game uses it yet |
| B. Input, `RamFunc`, `Fmt` | Identical code. | size only (the pragma) |
| C. `Save` and `Debug` engines | Hooks and run-time ids. CHBlackjack last, with its `chdrive.py`. | save compatibility, the debug answers |
| D. `Palette`, `Draw`, `Mask`, `Fx`, `Frame` | Supersets. Decide the 3x5 font and `ease` first. | pixels |
| E. `Audio` | The superset engine; convert tables lineage by lineage. | sound |
| F. Package | Bundle `CHGame`, `CHGfx` and `CHSd` in the board package; retire CHSd's `vendor.py` copies; copy `games/` into `examples/` at release. | none if A-E held |

## Decisions still open

1. **The 3x5 font.** CHBackgammon, CHCrossword, CHDominoes, CHFour and CHWords draw `M` differently and have no lower case. The options:
   - ship both tables, which keeps every pixel;
   - one table, accepting the new `M` and re-recording those games' GIFs.
2. **`ease`.** The CHFour family's table is half precision with no `LINEAR`. The options are the same two.
3. **CHBlackjack's save header and debug answers.** Keep its copies, or convert once. Converting needs a one-time read of its old saves, and a new `chdrive.py`.
4. **The instance name.** The recommendation is to keep `arduboy`. Every game uses it, and Arduboy developers already type it. A `chgame` reference to the same object can be added at no cost if wanted.
5. **What the package ships with the examples.** The sketches only, or their `tools/` and art too (roadmap step 4).
