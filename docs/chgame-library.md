# The `CHGame` library: how it was built, and why

`platform/board/arduino/CHGame/libraries/CHGame` is the one library the board package is to
carry, with `CHGame.h` as its single include: what `Arduboy2.h` is to the
Arduboy. All twenty games are built on it.

- **The reference** (modules, calls, rules of thumb) is the library's
  [README](../platform/board/arduino/CHGame/libraries/CHGame/README.md); the smallest complete
  sketch is [examples/Hello](../platform/board/arduino/CHGame/libraries/CHGame/examples/Hello/Hello.ino).
- **What it was built from:** the code the games carried copies of.
  [unification.md](unification.md) measured those copies before the move,
  and records what changed.
- **What is left:** bundling it in the board package (step 3 of
  [roadmap.md](roadmap.md)).

This page records the decisions, so the next change knows why things are
as they are.

## Layout

```
platform/board/arduino/CHGame/libraries/CHGame/
  library.properties        name=CHGame, includes=CHGame.h, depends=CHGfx
  src/CHGame.h              the one include: CHGfx and every module below
  src/chgame/Config.h       CHGAME_DEBUG, CHGAME_PROFILE
  src/chgame/Input.*        class CHGame, `arduboy`: buttons, pacing, exit to the menu
  src/chgame/Palette.*      the house colours, pal::
  src/chgame/Draw.*         panels, sprites, dither, the 3x5 font
  src/chgame/Mask.*         outlined, shadowed, gradient lettering
  src/chgame/Fx.h, Ease.cpp, Shake.cpp    fx:: easing, sine, randomness, shake
  src/chgame/Sizzle.h, Sizzle.inl         fx:: particles, banners, floating text (compiled in the game)
  src/chgame/Audio.*        audio:: the piezo engine and the LED
  src/chgame/Save.*         save:: the flash record
  src/chgame/Debug.*        dbg:: the serial debug protocol
  src/chgame/Fmt.*          number formatting
  src/chgame/RamFunc.h      RAMFUNC, CHGAME_RAMFUNC
  examples/Hello            the smallest complete sketch
```

The modules are global namespaces (`pal::`, `audio::`, `save::`, `dbg::`,
`fx::`) and the colour names are plain enums (`INK`, `GOLD` ...), as the
games had them: no `chgame::` prefix to type, and the games' code changed
least. Each header stands alone, so pure-logic files and host tests include
just the one they need (`<chgame/Fmt.h>`).

## Decisions

**One 3x5 font.** Five games (the CHFour family: CHFour, CHBackgammon,
CHCrossword, CHDominoes, CHWords) had an upper-case-only copy whose `M`
differed by one pixel. They now use the common table, `M` included.

**One set of easing curves.** The CHFour family's half-precision table gave
way to the common one; a few of their animation frames moved by a pixel.

**The frame loop stays in each game.** The plan had a `run(update, render)`
helper. In the end the loop is the part of a sketch a reader most needs to
see, it is twenty lines, and two games (CHChess, CHCheckers) draw from a
second stack while their search runs. Every game's loop has the same
shape; the library's README shows it.

**One sound engine, 3-byte steps.** A step is 20 Hz and 2 ms units (the
CHFour family's format), so a table costs half what the 6-byte games paid;
pitches move by at most 10 Hz and odd lengths by 1 ms, which the ear does
not notice and the comparison tool measured effect by effect. A step is at
most 510 ms (longer ones were split). Effects carry a priority and two
flags: `SOFT` (a narrow pulse: quieter) and `GLIDE` (sweeps change pitch at
a cycle's end). Music is either a Playtune score (CHBlackjack,
CHRoulette, CHWordWheel), rendered as an arpeggio or a lead line, or a
one-voice `Melody` of MIDI notes (CHSlots, CHCheckers). The music player is
reached through a function pointer that `music()` or `melody()` sets, so a
game without music links none of it. Tables live in flash through
`AUDIO_STEPS` (this core's link script copies small `const` data to SRAM).
`blip()` cuts off effects up to priority 1, as most old engines did; a game
whose blips never sound over an effect says so at the call:
`if (!audio::playing()) audio::blip(...)`.

**Saving keeps every game's record.** The header (`u32 magic; u8 version,
flag; u16 seq`), the data at offset 8, and the CRC at the next word are
exactly what the games wrote, so a save made before the move still loads;
every game's layout was checked field by field. CHBlackjack's older header
(`u16 version, u16 seq`) is the same bytes with flag 0. A game reads its
record in place in flash (`read()`) or copies it (`load()`), and builds a
new one in CHGfx's chunk scratch (`buffer()`, `write()`, or `store()`).

**The debug protocol is switched by `CHGAME_DEBUG`, and the hello is a
run-time argument.** Library code cannot see a sketch's `config.h`, so the
switch is a build flag (`chgame build --debug` passes
`-DCHGAME_DEBUG=1`; the simulator always has it), and the handshake
(`dbg::begin("CHCS " CHCH_VERSION)`: CHChess) is passed in. The games' own `<PFX>_DEBUG`
macros went: they test `CHGAME_DEBUG`. CHBlackjack, the ancestor, now gives
the common answers. The optional pieces cost nothing unless used: a held
game command's buffer exists only in a game that calls `dbg::holdWhile()`.
A held command runs before the frame ack, as every game had it (the other
order shifts a script's frames). In the simulator `Q` times CHGfx's
primitives for the drivers' `cal`, and puts the frame back.

**`RAMFUNC` sections by owner.** The library's functions are
`.gnu.linkonce.r.chg.<name>`, a sketch's `RAMFUNC(name)` is `app.<name>`,
CHGfx's `chgfx.<name>`: linkonce merges sections of the same name, so a
sketch's `save` can never replace the library's.

**No `#pragma GCC optimize` in the library.** GCC will not inline across
functions with different optimisation attributes, and the games' code is
built `-Os` with link-time optimisation already; the pragma cost 1.4 KB
over the twenty games.

**Small things measured over all twenty games before they were chosen:**
`audio::setOn()` inline (out of line cost 84 B in all); `save::read()`
inline (out of line saved 70-80 B in games that read twice but cost up to
40 B in others, the tightest included).

## Configuration

| Flag | Default | Set by |
|---|---|---|
| `CHGAME_DEBUG` | 1 in the simulator, else 0 | `chgame build --debug` |
| `CHGAME_PROFILE` | 0 | by hand (`-DCHGAME_PROFILE=1`) |

A game keeps its own `config.h` for its own switches (`<PFX>_LEAN`,
`<PFX>_FULL`, `<PFX>_VERSION`, `<PFX>_FPS`); it includes
`<chgame/Config.h>` to derive them. The `.ino` includes `<CHGame.h>` before
`config.h`, because Arduino finds a library from the first include that
names one of its headers.

### Sizzle: configured per game, compiled in the game

The particles, banners and floating texts (`chgame/Sizzle`, since
2026-10-02) are the one module that is not compiled in the library. The
games differ in what they need (48 or 64 particles; coins, rain or goo;
a pop-up 3x5 banner or one in the game's display font dropping in letter by
letter; floats or none) and in the size pragma on the file that holds the
code, and seven of them have less than 1 KB of flash to spare. A library
`Sizzle.cpp` would have been the superset in every game: 400-900 B of flash
and, in seventeen games, 128 B of RAM for particles they never spawn. So
`Sizzle.h` declares the API from a set of `SIZZLE_*` switches and
`Sizzle.inl` holds the bodies; a game's `src/fx/Fx.h` sets the switches
that differ from the defaults and includes `<chgame/Sizzle.h>`, and its
`src/fx/Fx.cpp` is the game's `#pragma GCC optimize` line, `#include
"Fx.h"` and `#include <chgame/Sizzle.inl>`. The switches are a build
setting of one translation unit, like `config.h`, not a `CHGAME_*` flag:
nothing else in the sketch or the library sees them, and `Sizzle.h` refuses
to be included without `SIZZLE_CONFIGURED`. Every call site kept its name
(`fx::burst`, `fx::banner`, `fx::floatText` ...), and every one of the
twenty release images is byte for byte what it was before the move.

A few switches exist only to reproduce the code shape a family's original
had (`SIZZLE_COLOUR_INLINE`, `SIZZLE_COIN_LATE`, `SIZZLE_BANNER_WRAP`,
`SIZZLE_BANNER_FILL`): the compiler lays out a function differently for a
local variable or a case order, and in the tight games 12 bytes is the
difference between two save pages and one. They are marked as such in
`Sizzle.h` and can go when a game has room to spare. What each game sets:

| Game | Switches (the rest at their defaults) |
|---|---|
| CHFour, CHBackgammon | `BANNER_DROP 1`, `FLOATS 0` |
| CHWords | as CHFour, plus `STYLE_RAMPS RAINBOW\|RED\|WHITE` |
| CHDominoes | as CHFour, plus its own `HUES` and `CONFETTI_COLOURS` (no cyan: that palette slot is a tile tone), `CYAN_INK BLUE`, `BANNER_AFTER` (the half ink of its serif) |
| CHCrossword | as CHFour, plus `KIND_DUST 0`, `STYLES RAINBOW\|GOLD` |
| CHChess, CHCheckers | `FLOATS 0` |
| CHBoardwalk, CHSnakes | `KIND_COIN 1`, `KIND_ORDER SPARK, CONFETTI, STAR, DUST, COIN`, `COIN_FLOOR 114`, `FOUNTAIN_GOLD_COINS 0`, `FLOAT_BLINK_FIRST 1`, `COIN_LATE 1` |
| CHBlackjack, CHCraps, CHYacht | `KIND_COIN 1`, `KIND_RAIN 1` (named `RAIN`), `DUST 1`, `HUES_EXPORT 0`, `HOLD_BANNER 0`, `BANNER_WRAP 0`, `BANNER_FILL WHITE`, `COLOUR_INLINE 1` |
| CHSlots | as CHBlackjack, plus `POOL 64`, `BANNER_CHARS 16`, `BANNER_ROWS_DOWN 38`; its own `explode()` |
| CHPoker, CHSolitaire | `KIND_COIN 1`, `KIND_RAIN 1` (named `RAIN`; the hues exported as `HUES`), `DUST 2`, `BANNER_CHARS 16`, `FLOAT_CHARS 10`, `FLOAT_CLAMP 1` |
| CHMahjong | `POOL 64`, `KIND_COIN 1`, `DUST 2`, `COIN_FLOOR_RUNTIME 1` |
| CHRoulette | `KIND_COIN 1`, `KIND_RAIN 1`, all seven styles, `BANNER_FILL WHITE`, `COLOUR_INLINE 1` |
| CHTicTacToe | as CHRoulette, with `STYLES RAINBOW\|RED\|CYAN` |
| CHBingo | as CHRoulette, plus `POOL 64`, `KIND_GOO 1`; its own `gack()` |
| CHWordWheel | `KIND_SPARK 0`, `KIND_STAR 0`, `KIND_DUST 0`, `KIND_COIN 1`, `BURST 0`, `HOLD_BANNER 0`, `SHAKE 0`, six styles (no black), `BANNER_FILL WHITE` |

## What stays in a game

- **Its rules, AI and logic:** `game/`, `rules/`, `ai/`, `engine/`.
- **Everything drawn and animated:** `stage/`, `render/`, `states/`,
  `fx/Presenter`; the `src/fx/Fx.h` that configures `chgame/Sizzle` for
  the game, and any effect of its own on top (CHSlots' `explode()`,
  CHBingo's `gack()`).
- **Its data:** effect and music tables (`src/audio/Sounds.cpp`), its save
  data and magic, its palette themes.
- **Its art:** `assets/`, generated by `tools/assets.py`.
- **Its frame loop**, in the `.ino` or `src/Frame.cpp`.
- **Its tools:** `tools/game.py` (what the shared `chgame check` and `chgame test` need to know),
  `tools/chsim/chdrive.py` (the shared driver plus the game's own script
  commands), its scripts and tests.

## Still open

- **What the package ships with the examples:** the sketches only, or
  their `tools/` and art too (roadmap step 4).
- **The instance name** stays `arduboy`: every game uses it and Arduboy
  developers already type it.
