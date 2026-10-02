# The `CHGame` library: how it was built, and why

`platform/libraries/CHGame` is the one library the board package is to
carry, with `CHGame.h` as its single include: what `Arduboy2.h` is to the
Arduboy. All twenty games are built on it.

- **The reference** (modules, calls, rules of thumb) is the library's
  [README](../platform/libraries/CHGame/README.md); the smallest complete
  sketch is [examples/Hello](../platform/libraries/CHGame/examples/Hello/Hello.ino).
- **What it was built from:** the code the games carried copies of.
  [unification.md](unification.md) measured those copies before the move,
  and records what changed.
- **What is left:** bundling it in the board package (step 3 of
  [roadmap.md](roadmap.md)).

This page records the decisions, so the next change knows why things are
as they are.

## Layout

```
platform/libraries/CHGame/
  library.properties        name=CHGame, includes=CHGame.h, depends=CHGfx
  src/CHGame.h              the one include: CHGfx and every module below
  src/chgame/Config.h       CHGAME_DEBUG, CHGAME_PROFILE
  src/chgame/Input.*        class CHGame, `arduboy`: buttons, pacing, exit to the menu
  src/chgame/Palette.*      the house colours, pal::
  src/chgame/Draw.*         panels, sprites, dither, the 3x5 font
  src/chgame/Mask.*         outlined, shadowed, gradient lettering
  src/chgame/Fx.h, Ease.cpp, Shake.cpp    fx:: easing, sine, randomness, shake
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
switch is a build flag (`tools/device.py build --debug` passes
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
| `CHGAME_DEBUG` | 1 in the simulator, else 0 | `tools/device.py build --debug` |
| `CHGAME_PROFILE` | 0 | by hand (`-DCHGAME_PROFILE=1`) |

A game keeps its own `config.h` for its own switches (`<PFX>_LEAN`,
`<PFX>_FULL`, `<PFX>_VERSION`, `<PFX>_FPS`); it includes
`<chgame/Config.h>` to derive them. The `.ino` includes `<CHGame.h>` before
`config.h`, because Arduino finds a library from the first include that
names one of its headers.

## What stays in a game

- **Its rules, AI and logic:** `game/`, `rules/`, `ai/`, `engine/`.
- **Everything drawn and animated:** `stage/`, `render/`, `states/`,
  `fx/Presenter`, its banners and particle kinds.
- **Its data:** effect and music tables (`src/audio/Sounds.cpp`), its save
  data and magic, its palette themes.
- **Its art:** `assets/`, generated by `tools/assets.py`.
- **Its frame loop**, in the `.ino` or `src/Frame.cpp`.
- **Its tools:** `tools/device.py` (a few lines that run the shared one),
  `tools/chsim/chdrive.py` (the shared driver plus the game's own script
  commands), its scripts and tests.

## Still open

- **What the package ships with the examples:** the sketches only, or
  their `tools/` and art too (roadmap step 4).
- **The instance name** stays `arduboy`: every game uses it and Arduboy
  developers already type it.
