# How far the games are from one `CHGame` library

The goal is the Arduboy model:
- one `#include <CHGame.h>`;
- one board package;
- the games as its examples.

This page measured how far the twenty games' copies of the "shared" code were from that, layer by layer, and then records how they became one library. [chgame-library.md](chgame-library.md) has the decisions, and [roadmap.md](roadmap.md) puts the rest of the release in order.

## The result (2026-10-02)

**Every game is built on `platform/libraries/CHGame`.** What each carried a
copy of is gone from its `src/`: `CHGame.h/.cpp`, `RamFunc.h`, `debug/`, the
save engine, `gfx/{Draw,Fmt,Mask,Palette}`, `fx/Ease` and the sound engine
(`audio/Audio.*`). A game keeps its rules, screens, art, its own effects,
its sound tables (`src/audio/Sounds.cpp`), what it saves, its debug
commands and its frame loop. The games' sources lost about 30,600 lines
(their tools another 11,700: one `device.py`, one script driver, one sound
preview); the library is about 2,400.

**How it was checked**, step by step and game by game:
- **Pixels.** Every simulator script of every game before and after. All
  identical, except these changes, made on purpose and measured:
  - the CHFour family (CHFour, CHBackgammon, CHCrossword, CHDominoes,
    CHWords): the common 3x5 font's `M`, and the common easing curves (a
    pixel here and there in animations);
  - CHWordWheel: one bevel corner pixel;
  - CHBingo: the title's clipping;
  - CHBlackjack and CHYacht: the screen shake's edge rows.

  Their README GIFs were recorded again.
- **Sound.** Every effect rendered by the old engine and by the library's,
  compared a millisecond at a time: identical in the five games that had
  3-byte steps; elsewhere pitches within 10 Hz (the 20 Hz grid) and odd
  lengths by 1 ms (runs of 45 ms notes were written 46/44 so they keep
  time). Songs compared the same way.
- **Saves.** Each game's old record and its new data checked offset by
  offset: a save from before still loads.
- **Size.** Every game fits, both save pages kept:

  | Game | Image before | now | | RAM before | now | |
  |---|---|---|---|---|---|---|
  | CHBackgammon | 49,580 | 50,224 | +644 | 16,924 | 16,892 | -32 |
  | CHBingo | 36,748 | 36,320 | -428 | 15,208 | 14,912 | -296 |
  | CHBlackjack | 45,872 | 45,572 | -300 | 15,736 | 15,436 | -300 |
  | CHBoardwalk | 49,884 | 49,668 | -216 | 15,404 | 15,052 | -352 |
  | CHCheckers | 42,048 | 42,168 | +120 | 17,444 | 17,108 | -336 |
  | CHChess | 48,904 | 48,764 | -140 | 17,880 | 17,544 | -336 |
  | CHCraps | 50,064 | 49,876 | -188 | 15,520 | 15,568 | +48 |
  | CHCrossword | 50,312 | 50,360 | +48 | 17,540 | 17,276 | -264 |
  | CHDominoes | 42,364 | 42,728 | +364 | 17,296 | 16,864 | -432 |
  | CHFour | 36,356 | 36,728 | +372 | 16,388 | 16,348 | -40 |
  | CHMahjong | 48,456 | 48,516 | +60 | 18,084 | 17,812 | -272 |
  | CHPoker | 48,940 | 48,480 | -460 | 15,868 | 15,500 | -368 |
  | CHRoulette | 49,804 | 49,848 | +44 | 16,084 | 16,072 | -12 |
  | CHSlots | 47,092 | 47,596 | +504 | 14,788 | 14,916 | +128 |
  | CHSnakes | 37,348 | 37,204 | -144 | 15,704 | 15,360 | -344 |
  | CHSolitaire | 31,184 | 30,812 | -372 | 16,540 | 16,188 | -352 |
  | CHTicTacToe | 50,352 | 49,644 | -708 | 15,176 | 14,580 | -596 |
  | CHWordWheel | 50,348 | 50,368 | +20 | 15,244 | 14,952 | -292 |
  | CHWords | 50,416 | 50,328 | -88 | 15,836 | 15,788 | -48 |
  | CHYacht | 43,732 | 44,036 | +304 | 14,996 | 15,260 | +264 |

  In all, 564 B of flash and 4.2 KB of RAM fewer. The games without music
  pay ~150-190 B for the one sound engine's generality; the tightest made
  that back inside the game (CHWords: no newlib `strncpy`, an unused effect,
  one more optimisation flag; CHCrossword: casino effects it never used).
- **Memory.** Every script once more on an `-O0` simulator under valgrind.

**Bugs found on the way**, fixed: CHBoardwalk dealt from an uninitialised
count (a new game could deal the wrong deeds; its `save` script crashed the
simulator); CHCrossword's debug STATE line overflowed its buffer; the
library's `blip()` comment and code disagreed (the code now does what most
old engines did).

The rest of this page is the survey from before the move, kept for the
record. Its numbers come from comparing the copies in `games/*/src` by md5,
by line diff against CHFour, and by hashing function bodies; the commands
are at the end.

## Summary

| Layer | Copies | Families | State |
|---|---|---|---|
| Buttons, pacing, exit to menu (`CHGame.h/.cpp`) | 20 | 1 (4 pragma lines) | **Ready.** Shared in all but location. |
| `RamFunc.h` | 20 | 2 (comment text only) | **Ready.** The section prefix is the only difference, and it is cosmetic. |
| Number formatting (`gfx/Fmt`) | 20 | 1 + single-game additions | **Ready.** The union of the variants changes nothing. |
| Saving (`save/`) | 20 | 1 engine, 20 payloads; CHBlackjack apart | **Close.** The engine splits off cleanly; CHBlackjack needs a compatibility path. |
| Debug protocol (`debug/`) | 20 | 6 | **Close.** One protocol with optional parts; CHBlackjack answers differently. |
| Frame loop (`Frame` or `loop()`) | 20 | 2 orders, 3 shapes | **Close.** One helper with hooks and an order flag. |
| Palette (`gfx/Palette`) | 20 | 13 `.cpp` variants | **Mid-way.** A superset is feasible; themes and modes become data. |
| Drawing helpers (`gfx/Draw`) | 20 | 14 files, most functions identical | **Mid-way.** The 3x5 font has a real pixel conflict. |
| Banner lettering (`gfx/Mask`) | 20 | 4 API families | **Mid-way.** One signature covers the others. |
| Effects (`fx/Fx`, `fx/Ease`) | 20 | 13 | **Mid-way** for the maths and particles; banners and particle kinds stay per game. |
| Sound (`audio/`) | 20 | 14 distinct engines | **Far.** The hardest layer. |
| CHGfx | 1 library | | **Ready.** Already a library; every game builds against `platform/libraries/CHGfx`. |
| CHSd | 1 library + 3 generated copies | | **Ready** once the board package bundles it. |

In one line: the device interface (`CHGame.h`), `RamFunc`, `Fmt`, CHGfx and CHSd could move into a library today without changing a pixel. Saving, debugging and the frame loop need small hooks. The house-style drawing helpers need two decisions. Sound needs a superset engine and per-game conversion.

## The constraints every step has to meet

- **Flash.** Most games are close to full. The "save room" column of [status.md](status.md) is the real budget, because an image above 50,432 B switches saving off:

  | Game | Save room |
  |---|---|
  | CHWords | 16 B |
  | CHTicTacToe | 80 B |
  | CHWordWheel | 84 B |
  | CHCrossword | 120 B |
  | CHCraps | 368 B |
  | CHBoardwalk | 548 B |

  Shared code must cost no more than the copy it replaces. Identical code under `-flto` costs the same. Parameters can cost bytes: a pointer to a table instead of a constant, or a callback instead of a direct call. Measure each game after each step (`python tools/device.py build`).
- **Pixels.** The simulator is deterministic. Every script of every game must give the same frames before and after (CLAUDE.md rule 2). That is the test for the whole move.
- **Sounds and saves.** `tools/audio/preview.py` prints a hash per effect, and those hashes must not change. Saves must still load: an existing save on a player's board is a record with a magic, a version and a CRC.
- **`config.h` is invisible to library code.** Arduino compiles a library's `.cpp` files without the sketch's folder in view, so a library `.cpp` never sees `CHF4_DEBUG` or `CHF4_VERSION`. Settings that library code needs must arrive by one of three routes:
  - generic build flags (`-DCHGAME_DEBUG=1` through `build.extra_flags`, which `device.py` already uses, and `-D` in the simulator);
  - run-time arguments (`dbg::begin("CHF4 0.1")`);
  - inline or template code in the headers.
- **RAMFUNC names merge.** `RAMFUNC(name)` puts each function in `.gnu.linkonce.r.<prefix>.<name>`, and the linker keeps only one section of a given name. The names `save`, `text35`, `glyph` and `maskruns` appear in every game. If library and game code ever share a prefix and a name, one function silently replaces the other. The library needs its own prefix, distinct from CHGfx's `chgfx.`.
- **Two headers called `CHGame.h`.** Every game includes its own `src/CHGame.h` with quotes. Quotes find the local file first, so the library's header is only picked up by a game that includes `<CHGame.h>` and has deleted its own copy. Move a game over in one commit, never halfway.

## Layer by layer

### Buttons, frame pacing, exit to menu: `src/CHGame.h/.cpp`

- `CHGame.h` is byte-identical in all 20 games.
- `CHGame.cpp` differs only in line 1, the `#pragma GCC optimize`:

  | Pragma | Games |
  |---|---|
  | `"Os", "no-ipa-sra"` | CHBackgammon, CHCrossword, CHDominoes, CHFour, CHWords |
  | `"Os"` | CHBingo, CHBlackjack, CHBoardwalk, CHCheckers, CHChess, CHCraps, CHMahjong, CHPoker, CHRoulette, CHSlots, CHSnakes, CHSolitaire, CHTicTacToe, CHYacht |
  | `"Os", "no-ipa-sra", "no-inline-functions-called-once", "no-jump-tables", "no-guess-branch-probability"` | CHWordWheel |

- **What it provides:**
  - `pollButtons`, `pressed` / `justPressed` / `justReleased` / `repeat`;
  - `nextFrame` with a microsecond accumulator;
  - `everyXFrames`;
  - lockstep for the debug protocol;
  - the START-held-3-s exit (`startExits`, `exitToMenu`).
- **On the device**, `chgame_readButtons()` reads GPIOB/GPIOC directly in `CHGame.cpp`. **In the simulator** it is `tools/chsim/host/main.cpp` and returns 0; all input arrives through the debug `K` command into `arduboy.injected`.
- **For the library:** take the file as it is. The pragma changes size, not behaviour. Measure CHWordWheel's set, which `CHWordWheel/NOTES.md` reports as about 1 KB smaller across that game, on this file in every game, and keep whichever is smallest.

### `RamFunc.h`

- One mechanism: `__attribute__((section(".gnu.linkonce.r.<prefix>." #name), noinline))` on the device, `noinline` elsewhere.
- Two texts:
  - 12 games test `defined(__riscv) && !defined(CHSIM)`;
  - 8 (the CHBlackjack lineage) test `#ifdef CHSIM` and carry a longer comment.
- **Prefixes:** each game has its own, except that CHCrossword reuses CHBackgammon's `chbg`, and CHSlots and CHSolitaire both use `chsl`. Each game is its own binary, so neither reuse matters.
- **For the library:** one `CHGAME_RAMFUNC(name)` with the prefix `chg.` for library functions. Games may keep a `RAMFUNC` of their own with a game prefix, so their names cannot meet the library's.

### Number formatting: `gfx/Fmt`

- `fmtInt`, `fmtMoney` and `fmtStr` are in all 20. The files differ only in pragmas and added functions.
- Additions in single games: CHPoker `fmtShort`, CHSolitaire `fmtTime`, CHWordWheel `fmtCash`.
- The debug protocol uses `fmtStr`/`fmtInt`, so `Fmt` moves with it.
- **For the library:** the union. Unused functions cost nothing.

### Saving: `save/`

The engine is the same in every game:
- the two pages 0xF500/0xF600;
- `imageEnd()` from `_data_lma + (_edata - _data_vma)`, `twoPages()`, `available()`;
- the RAMFUNC page write after `gfx_wait()`, built in `gfx_chunkScratch()`;
- `crc32`, and the simulator's `simFlash[2][256]`;
- the newer of the two records by `seq`, alternating pages by `seq & 1`.

19 games store `{u32 magic; u8 version; u8 hasGame|pad; u16 seq; payload; u32 crc}`. The payload is each game's own `Options`, `Stats` and, usually, a game in progress.

**Differences:**
- **CHBlackjack** has a different header (`u16 version, u16 seq`), builds the record on the stack, and reports a saved game only when `purse > 0`.
- **CHPoker and CHSolitaire** use the `hasGame` byte as padding.
- **The CRC length** is `offsetof(Record, crc)` in five games (the CHFour lineage) and `sizeof - 4` in the rest. They agree unless the struct has trailing padding.
- **Zeroing:** CHBingo, CHBlackjack, CHRoulette, CHTicTacToe and CHWordWheel zero the record before filling it.
- **`allowWrites()`:** CHBingo, CHRoulette, CHTicTacToe and CHWordWheel block writes on device debug builds until the debug `E` command enables them.
- **No LEAN stub:** CHBlackjack and CHMahjong have no stub for their LEAN builds.

**For the library:**
- An engine with this API, which owns the header, the sequence and the CRC:
  ```cpp
  save::read(magic, version, void *payload, size_t n, bool *flag)
  save::write(magic, version, const void *payload, size_t n, bool flag)
  ```
- Each game keeps its payload struct and its magic.
- The record is then byte-for-byte what 17 games write today. CHPoker and CHSolitaire pass no flag.
- CHBlackjack either keeps its own `Save.cpp` or the engine reads its old header once.

The magics, which CLAUDE.md rule 8 requires to be unique:

| Game | Magic | Game | Magic |
|---|---|---|---|
| CHBackgammon | CHBG v2 | CHMahjong | CHMJ v1 |
| CHBingo | CHBN v1 | CHPoker | CHPK v1 |
| CHBlackjack | CHBJ v1 (u16) | CHRoulette | CHRL v1 |
| CHBoardwalk | CHBW v1 | CHSlots | CHSL v1 |
| CHCheckers | CHCK v1 | CHSnakes | CHSN v1 |
| CHChess | CHCS v2 | CHSolitaire | CHSO v1 |
| CHCraps | CHCR v1 | CHTicTacToe | CHTT v2 |
| CHCrossword | CHCW v1 | CHWordWheel | CHWW v1 |
| CHDominoes | CHDM v1 | CHWords | CHWD v1 |
| CHFour | CHF4 v1 | CHYacht | CHYD v1 |

### The debug protocol: `debug/`

**One protocol everywhere:**
- `?` handshake, `S` screenshot, `K` buttons, `L1`/`L0` lockstep, `N k` frames, `P` perf and stack, `T` profile, `B` bootloader;
- `dbg::hook` for the game's own commands, with the same signature in all 20.

**What varies:**
- **The handshake id and version.** CHChess answers `CHCS`, though its macro prefix is `CHCH`.
- **The input line:** 100 bytes in most games, 64 in the CHBingo lineage (CHBingo, CHRoulette, CHTicTacToe, CHWordWheel), 48 in CHBlackjack.
- **Optional pieces:**
  - `waitInput()`: CHBoardwalk, CHCheckers, CHChess, CHCraps, CHMahjong, CHPoker, CHSlots, CHSnakes, CHSolitaire, CHYacht.
  - `holdGame()`, which answers `HELD` and replays the command when the game is free: CHBoardwalk, CHSnakes, CHPoker, CHChess, CHCheckers, CHSolitaire.
  - A second frame stack in `P` (` fstk=`): CHChess, CHCheckers, CHPoker, CHSolitaire.
- **CHSnakes** times its profiler in host nanoseconds in the simulator.
- **CHBlackjack, the ancestor,** answers differently:
  - `?` adds `frame=` and `lock=`;
  - `L` answers `OK <frame>`;
  - `P` has `wait=` and no `stk=`;
  - unknown commands get no reply.

  Its `chdrive.py` expects all of that.

**For the library:**
- One `Debug.cpp`, with the id given at run time and the optional pieces always present (each is a few bytes).
- Line length 100.
- Compiled in by `CHGAME_DEBUG`.
- CHBlackjack either keeps its copy or its `chdrive.py` learns the common answers.

### The frame loop: `Frame.cpp` or `loop()`

- **The same steps everywhere:**
  1. `dbg::poll`, then `nextFrame`.
  2. Up to three logic ticks: `pollButtons`, `pal::tick`, `audio::update`, `screens::update`.
  3. Then `gfx_wait`, `pal::commit`, `screens::render(frameCount)`, `gfx_flushAsync`.
- **Where it lives:** 10 games have `Frame.cpp`; the other 10 have the same loop in the `.ino`.
- **Order:** 8 games call `pal::commit()` *before* `gfx_wait()`: CHBingo, CHBlackjack, CHCraps, CHRoulette, CHSlots, CHTicTacToe, CHWordWheel and CHYacht. The order decides which frame a palette fade lands on, so it changes screenshots.
- **CHChess and CHCheckers** add a 1 KB second stack so the search can draw while it thinks (`thinkPoll()`).
- **For the library:** `chgame::run(update, render)` with a flag for the commit order. CHChess and CHCheckers keep their own loop.

### Palette: `gfx/Palette`

- **Common to all 20:** the 16-entry `BASE` table and the colour names (`INK` … `FX_B`). CHDominoes changes two slots, `BONE` and `SLATE` in place of `SKIN` and `CYAN`.
- **In all 20:** `init`, `setFade`, `tick`, `resetClock`, `commit`.
- **In most:**
  - `fade` and `rgb444`: 18 games;
  - `setFx`, `setCycling`: 15;
  - `setTheme`/`theme` and `flash`: 13;
  - `setDesaturate`: 10;
  - `setMode`: 9.
- **The `Mode` enum** differs by game (`CASINO, HOVER, TARGETS, FIRE` in four combinations), and CHSlots has its own themes.
- **For the library:** one superset, with `BASE`, themes and modes supplied by the game as data. Pixels do not change, because enum values are only used by name.

### Drawing helpers: `gfx/Draw`

- **Same function bodies:**

  | Function | Games |
  |---|---|
  | `fillRound`, `text35Width`, `plot` | all 20 |
  | `glyph` (CHTicTacToe clips to a band) | 19 |
  | `roundRect` | 19 |
  | `pairRun` | 16 |
  | `dither` | 15 |
  | `rotSpan` | 9 |
  | `spriteRot` | 8 |

- **`sprite4`** has five variants. Each adds to the CHChess one:
  - a null remap;
  - a negative scale to flip;
  - ±256 to mirror;
  - a clip window in CHTicTacToe.

  A superset draws the same pixels for every existing call.
- **The 3x5 font is the one real conflict:**
  - 14 games use the CHChess table, with lower case.
  - CHBackgammon, CHCrossword, CHDominoes, CHFour and CHWords use an upper-case-only table whose `M` is `{0x1F,0x02,0x1F}` where CHChess's is `{0x1F,0x06,0x1F}`.
  - CHCrossword adds `"`, `&` and `;`.
  - CHWordWheel folds lower case to capitals.
- **`text35x2`** has five implementations. They differ in `\n` and `~` handling.
- **CHGfx already has most of these** (`gfx_fillRoundRect`, `gfx_dither`, `gfx_remapRect`, `gfx_sprite4`, `gfx_sprite4Rot`, `gfx_scroll`, `gfx_textFx` with `CHGfx_Tiny3x5`). The games kept their copies on purpose, because they are smaller and in two cases draw different pixels ([CHChess/docs/CHGfx-notes.md](../games/CHChess/docs/CHGfx-notes.md)). Only CHBlackjack, CHCraps, CHSlots and CHYacht call CHGfx's versions.
- **For the library:** a `chgame` draw module with the identical functions and the `sprite4` superset. Then **decide the font**: ship both tables (a per-game choice), or accept a one-pixel change to `M` in five games and re-record their GIFs.

### Banner lettering: `gfx/Mask`

- `struct Mask {bits, stride, w, h}` and `maskBegin` are common.
- `maskDraw` has two signatures:
  - CHChess and CHFour families: `(m, x, y, outline, shadow, ramp)`;
  - CHBingo and CHCraps families: `(m, x, y, fill, outline = -1, shadow = -1, ramp = nullptr)`.

  The second covers the first by reordering at the call sites. Pixels are the same.
- `maskText35` is in 15 games, in two equivalent implementations.
- **The CHFour family** has a 13 px display font (`maskFont`, `fontText`). Its glyph data is in each game's `assets/`; CHDominoes' is anti-aliased.
- **For the library:** the CHBingo/CHCraps signature, `maskBlit1` with a scale, and the display font as a hook (the data stays with the game).

### Effects: `fx/Fx`, `fx/Ease`

**Shared:**

| Piece | Games |
|---|---|
| `isin` | all 20 |
| `spawn` | 17 |
| `shake`/`applyShake` | 15 |

The xorshift `rnd` is the same everywhere; only the particle pool size around it differs (48 or 64).

**Not shared:**
- `ease` is the CHChess form in 14 games. The CHFour family uses a half-precision table with no `LINEAR`, so values can differ by one: a pixel risk.
- `banner`, the particle kinds and their drawing differ in every game.
- `Presenter`, `stage/` and `render/` are per game in pattern only.

**For the library:** `isin`, `rnd`, `spawn`, `shake`, and `ease` in both tables, or one after a decision. Particle kinds and banners stay with the games.

### Sound: `audio/`

**Common:**
- the hardware (TIM1 channel 2 on PB10, the LED on PB9);
- the 1 kHz SysTick stepper;
- priority pre-emption;
- the LED patterns.

**The sequencers have drifted into 14 different engines, along these axes:**
- **Step format:** CHBackgammon, CHCrossword, CHDominoes, CHFour and CHWords store `{u8 hz/20, endHz/20, ms/2}`; the other 15 store `{u16 hz, endHz, ms}`.
- **Soft (narrow-pulse) effects:** in about half the games.
- **The one-note call:**

  | Signature | Games |
  |---|---|
  | `blip(u16, u8)` | CHFour |
  | `blip(u16, u16)` | 9 games |
  | `blip(u16, u16, bool soft)` | the CHBingo lineage |
  | `note(u16, u8)` at priority 2 | CHWords, CHCrossword |
  | none | 3 games |

- **Glide:** `tone(hz, smooth)` in five games.
- **On and off:**
  - `begin(bool)` / `setOn`;
  - an `enabled` flag (CHCraps, CHYacht, CHSlots);
  - `setMode` off/arpeggio/lead (CHBingo lineage, CHTicTacToe);
  - `mute()` (CHBlackjack).
- **Music, in three mechanisms:**
  - **Playtune scores:** CHBingo, CHRoulette and CHWordWheel share one engine, built from `make_music.py`; CHBlackjack has its own, and CHBingo's `Music.h` is an empty stub.
  - **CHSlots:** looping songs.
  - **CHCheckers:** a semitone tune table that also transposes the effects.

**For the library:** one superset engine. Its pieces:
- 6-byte steps;
- soft pulse;
- glide;
- a mode;
- an optional score player behind a flag;
- effect tables passed in by the game (`audio::begin(table, count, ...)`).

Every game then needs its tables converted and its preview hashes compared, and the 3-byte games have their own step quantisation (20 Hz, 2 ms) to keep. Do this layer last, one lineage at a time.

### CHGfx and CHSd

- **CHGfx** is a library already:
  - every game builds against `platform/libraries/CHGfx`, through `--library` in `device.py` and `chgfx_dir()` in `tools/chsim/chsim.py`;
  - its `library.properties` still points at the CH32SerialBoot URL.
- **CHSd** is a library too, but a sketch can only compile its own folder unless the library is installed. So CHWords, CHCrossword and CHWordWheel carry generated copies, made by `platform/libraries/CHSd/tools/vendor.py`. Once the board package bundles CHSd, the copies and `vendor.py` go.

## What the tools need

| Tool | Today | For a library |
|---|---|---|
| `games/*/tools/device.py` (20 copies, 4-26 lines apart) | `--library platform/libraries/CHGfx`, `-D<PFX>_DEBUG=1` | also `--library platform/libraries/CHGame`, and `-DCHGAME_DEBUG=1` beside the game's flag |
| `tools/sdcard/mkcard.py` | `--library` CHGfx for CHSDtoUSB | the same addition |
| `tools/chsim/chsim.py` | compiles `<sketch>/src/**` + CHGfx's `src/*.cpp` | a resolver like `chgfx_dir()` for the CHGame library, its `src/**`, and `-I` |
| `games/*/tools/audio/preview.py` | compiles `src/audio/Audio.cpp` | the library's audio source |
| `platform/libraries/CHSd/tools/vendor.py` | copies CHSd into three games | retired once CHSd is bundled |
| CI | none | one job: every game's release build size, every simulator script, the host tests |

## Repeating the survey

From `games/`:

```bash
# identical copies of a file
for f in CHGame.h CHGame.cpp RamFunc.h debug/Debug.cpp save/Save.cpp audio/Audio.cpp gfx/Fmt.cpp; do
  echo "== $f"; md5sum */src/$f | awk '{print $1}' | sort | uniq -c | sort -rn; done
# how far each copy is from CHFour's
for g in *; do printf '%s:%s ' $g $(diff CHFour/src/save/Save.cpp $g/src/save/Save.cpp | grep -c '^[<>]'); done
# RAMFUNC prefixes
for g in *; do printf '%s:%s ' $g $(grep -o 'linkonce\.r\.[a-z0-9]*' $g/src/RamFunc.h | sed 's/.*r\.//'); done
# palette commit before or after gfx_wait
for g in *; do f=$(ls $g/src/Frame.cpp 2>/dev/null || echo $g/$g.ino)
  echo "$g commit@$(grep -n 'pal::commit' $f | head -1 | cut -d: -f1) wait@$(grep -n 'gfx_wait()' $f | head -1 | cut -d: -f1)"; done
# sound step format
grep -h 'struct Step' */src/audio/Audio.cpp | sort | uniq -c
```
