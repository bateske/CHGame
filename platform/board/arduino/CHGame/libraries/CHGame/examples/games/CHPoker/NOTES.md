# CHPoker — development notes

Agent-facing notes for continuing work here; rules and controls are in README.md, the platform in the repo-root CLAUDE.md and docs/.

## Snapshot

- Imported from https://github.com/bateske/CHPoker at commit 0840afd (2026-10-01); develop here now, not in the old repo.
- Release build (CHGame core 0.2.4, CHGfx 1.3.0, the CHGame library, `opt=oslto,rtlib=nano,periph=game,usb=uploadonly`; 2026-10-02): image 48,480 of 50,944 B, static RAM 15,500 of 18,416 B (2,916 spare).
- On the CHGame library (`platform/board/arduino/CHGame/libraries/CHGame`, `<CHGame.h>`) since 2026-10-02: the input, palette, drawing, 3x5 font, masks, fx maths and shake, formatting, the debug protocol (`chgame/Debug.h`), saving (`chgame/Save.h`) and `RAMFUNC` are the library's; `src/fx/` keeps the game's particles, banners and floating texts.
- Sound: on the library's engine (`chgame/Audio.h`) since 2026-10-02; `src/audio/Sounds.*` holds the effect tables (3-byte steps, every sweep GLIDEs as the old sequencer did). `python tools/run.py audio/preview.py . out/audio` renders them to WAV.
- Save pages: the image (as `../../../../../../../../../tools/check_size.py` reports it) is 48,480 B. Both A/B pages (0xF500, 0xF600) fit while it is at most 50,432 B, so the real headroom is 1,952 B. Past that, saving (the CHGame library's `chgame/Save.cpp`; `src/save/Save.cpp` says what the record holds) uses page B only.
- Simulator-verified (as of 2026-10-01):
  - `python tools/tests/run_tests.py` passes. It builds under UBSan; `--long` adds the exhaustive 7-card enumeration.
  - It covers exact hand-category counts, betting spots, side pots, stud order, a fuzz of thousands of hands, CPU equity and honesty, and stats.
  - The scripts in `tools/scripts/` run in the simulator, and `gameplay.txt` makes the README's `docs/gameplay.gif` (through `../../../../../../../../../tools/readme_gif.py`).
- Device: never run on the board.

## Design decisions

- Chosen: all four games in ONE image: NL Hold'em, PL Omaha, FL Five Card Draw and FL Seven Card Stud.
  - Hold'em and Draw were the first priority.
  - Separate editions built from one source (a `CHPK_EDITION` switch) were the fallback. They were removed once all four games fit; don't reintroduce them unless flash forces it.
- Chosen: a cash game with a saved purse and a Blackjack-style goal / broke ending. You play against 3 CPUs.
- Chosen: difficulty is tied to the stakes: ROOKIE $1/$2, PRO $5/$10, SHARK $25/$50 (`UNIT` and the variant table in `src/game/Variant.cpp`).
- Chosen: CPU seats are anonymous plates named by colour, with no portraits.
- Chosen: the CPUs judge their hands by Monte Carlo play-outs over the cards they can't see, and never peek at hidden cards. The tests check that changing hidden cards never changes a decision; keep that property.
- Defaults the owner has not yet confirmed or vetoed:
  - the draw takes up to 3 cards (4 when keeping an ace);
  - stud: ante = bring-in = one unit, bets of 2 and 4 units;
  - every live hand is shown at the showdown;
  - a $500 starting purse, with goals of $10K, $50K or endless;
  - a NEXT HAND / LEAVE bar after each hand;
  - sound effects only, with no music player (the fanfares are effects too, see `src/audio/Sounds.cpp`).

## Open items

- Device checks: pace, CPU think time, mini-card legibility and sound by ear. Then leave the release build on the board.
  - `tools/scripts/device_perf.txt` runs each game at SHARK, free-running, and prints the frame `perf` and the CPUs' think time (`say W`).
- The owner's verdict on the unconfirmed defaults above.

## Gotchas

- Flash: 1,952 B before the image reaches save page A. Measure with `python tools/device.py build`, which runs the shared `../../../../../../../../../tools/check_size.py`.
- Device debug builds (`CHPK_LEAN`, set in `config.h`) leave saving out entirely (stubs in `src/save/Save.cpp`), so a debug run on the board never touches its save pages. The simulator and release builds keep saving. `-DCHPK_FULL` forces a full device debug build, which may not fit. On such a build the Stats page says "SAVING UNAVAILABLE" (it asks `!CHPK_LEAN && save::available()`); device debug build 50,396 B (2026-10-02).
- Debug hooks are sent with `say` in chdrive scripts; the list is in `src/states/Screens.cpp`:
  - `G` sit down (game, table, buy-in, seed), `D` stack the deck (card = rank*4 + suit), `$` set the purse;
  - `J` jump to a screen (T L O S W B), `H` table state, `W` CPU think time (last/max);
  - simulator only: `Z` "power cycle" (reload the save, back to the title) and `Q` (calibration for `cal`).
- The debug protocol is the CHGame library's (`chgame/Debug.h`, on with `CHGAME_DEBUG`; its hello is `CHPK <version>`). This game's `tools/chsim/chdrive.py` (on the shared `tools/chsim/chdrivelib.py`) adds the ops `waitturn`, `playto P`, `table` and `cal` (with `cal` first, `perf` prints estimated device render times).
- CPU tuning is the `Level` table at the top of `src/game/Ai.cpp`: samples, noise, slack, bet/raise thresholds, first-street fold floor, bluff, slow-play, fear, position.
  - Tuned targets: ROOKIE calls about 60%, PRO folds about 2/3, SHARK raises about as often as it calls.
  - Rerun `run_tests.py` after any change.
- CPU thinking runs a fixed number of play-outs, only on a frame's first logic tick. Keep it that way: it keeps the table animating and lockstep scripts deterministic.
- The royal flush and the four sevens in `tools/scripts/gameplay.txt` and `showcase.txt` come from stacked decks. Everything else in them is the CPUs playing, so a CPU tuning change alters the README GIF: record it again.
- Art: `tools/assets.py` packs local copies in `tools/art/` (CHBlackjack's card art, CHChess's glove, and `logo.txt`, "Poker" in the letters of PPOT's BlackJack logo); it does not read the sibling games. Credit Press Play On Tape as NOTICE does.
- Compiler: the simulator and tests need `CHSIM_CXX` set, or zig/clang++/g++ on PATH (see the root CLAUDE.md).

## How it fits

- Flash: all four games, every screen and the attract demo fit with LTO (`opt=oslto`, with `usb=uploadonly`: the game has no use for USB Serial). The presentation is the biggest part (cards, chips, plates, bar, animation: ~12 KB without LTO), then the rules (~7.5 KB), screens (~6.3 KB), CHGfx and the core. CHGfx's circle, ellipse and line drawing were replaced by the rounded-rect corner table and a 31-byte ellipse quadrant, which saved 736 bytes.
- The hand evaluator has no tables: a rank mask per suit, straights by four shifts and ANDs, flushes by counting bits, pairs, trips and quads by counting ranks, for 1 to 7 cards at once. The tests check the exact category counts over all 2,598,960 five-card and 133,784,560 seven-card hands, and the 7,462 distinct five-card scores.
- CPU thinking: 16 play-outs a frame in Hold'em, Stud and Draw, an estimated 2 ms on the board; one Omaha play-out is 60 five-card evaluations per player.
- A still table isn't redrawn: the frame is flushed again. A full redraw is estimated (from the simulator, calibrated against the board) at about 7.4 ms.

## Development

Everything can be checked on a PC (Python 3 with Pillow, and a C++ compiler for the host builds: root CLAUDE.md).

    python tools/tests/run_tests.py [--long]   # the evaluator, betting, pots, the CPUs, a fuzz of every game
    python tools/run.py chsim/chsim.py build .
    python tools/chsim/chdrive.py --sim . tools/scripts/showcase.txt out/showcase
    python tools/run.py readme_gif.py    # tools/scripts/gameplay.txt -> docs/gameplay.gif (the README's one GIF, <= 1 MB)
    python tools/assets.py              # art -> src/assets
    python tools/run.py audio/preview.py . out/audio   # the sound effects as WAV
    python tools/device.py upload [--debug]   # build and upload (--debug adds the serial protocol)
    python tools/run.py check_size.py build/release --top 20

- The tests cover: the evaluator (exhaustive), betting spots (no-limit minimum raises, short all-ins, pot-limit maximums, fixed-limit caps, the stud bring-in and order), side pots, odd chips, uncalled bets, the draw heuristic, CPU equity and honesty, statistics, and a fuzz of thousands of hands of every game at every table with random input, checking that no chip or card is ever lost or doubled and that every pot is paid.
- Scripts: `say G <game> <table> <buy-in> <seed>` sits down, `say D <cards>` stacks the deck (card = rank*4 + suit), `waitturn` runs until the table waits for you, `playto P` checks or calls until the table reaches phase P, `snap` and `rec` take pictures. The same scripts run on the device with a debug build (`python tools/device.py run SCRIPT OUTDIR`).
- `tools/scripts/gameplay.txt` records the README's clips: the title, a Hold'em royal flush and Five Card Draw's four sevens from stacked decks, and a Seven Card Stud hand that is the CPUs playing, so a CPU tuning change alters that clip. `showcase.txt` is the longer tour (lobby, Omaha, all in and busted, breaking the bank), kept as a test.
- Art is in `tools/art`: the cards, the glove, and `logo.txt`, the title's lettering as `#` and `.`.
- With plain `arduino-cli`: `arduino-cli compile -b CHGame:ch32v:CHGame:opt=oslto,rtlib=nano,periph=game,usb=uploadonly --library ../../../../CHGfx .` (`python tools/device.py build` does the same).

## Files

    CHPoker.ino            loop: logic ticks, then draw, then DMA flush
    config.h               build switches
    src/game/Hand.*        the hand evaluator
    src/game/Table.*       the rules and the flow of a hand (no graphics)
    src/game/Ai.*          the CPU players
    src/game/Variant.*     the four games and three tables as data
    src/stage/Stage.*      events -> motion; drawing the table
    src/render/*           cards and chips, the action bar, layout
    src/states/Screens.*   title, lobby, play, options, stats, the endings
    src/fx/*               particles, banners, floating texts (on the CHGame
                           library's palette, drawing, lettering and fx::)
    src/audio/Sounds.*     the sound effects (the CHGame library's engine)
    src/save/Save.*        what a save holds (the CHGame library keeps it in flash)
    tools/                 simulator driver, tests, asset pipeline, device tools
