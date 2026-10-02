# CHCrossword — development notes

Agent-facing notes for continuing work here; rules, controls and build are in README.md, the platform in the repo-root CLAUDE.md and docs/.

## Snapshot

- Imported from https://github.com/bateske/CHCrossword at commit 68c482e (2026-10-01); develop here now, not in the old repo.
- Release build (`opt=oslto,rtlib=nano,periph=game,usb=uploadonly`, core 0.2.4, CHGfx 1.3.0): flash 50,006 of 50,944 B (938 spare), static RAM 17,276 of 18,416 B (1,140 spare) (2026-10-02, on the CHGame library's sound engine, debug protocol and saving).
- Flash is full in practice: the image (`../../tools/check_size.py`'s `image:` line, 50,352 B) sits only 80 B under the 50,432 B that keeps both A/B save pages (0xF500/0xF600, the CHGame library's `chgame/Save.cpp`). Any new feature needs a cut first.
- Verification: simulator only. `python tools/check.py` passes: puzzle check, host tests (decoder vs the Python reference, rules and score, saving, FAT16/FAT32 card images with a read failure at every point), every script twice with identical frames, device compile and size.
- As of 2026-10-01 it has never run on the device, and CHSd (its SD driver) has never read a real card in any game.

## Design decisions

- Chosen: full-size 13x13 puzzles; 20 built in (flash) plus packs on the SD card (`CHCW/*.CWD`, up to 15x15 at 7 px squares, SD only).
- Chosen: score attack - timer, score, combo streaks, best times, stars. No chips or betting.
- Chosen: a pop-up letter board for typing.
- Chosen, at the owner's direction, after the first build:
  - the series' zoom-in: a 2x close-up while the letter board is up or B is held (Options VIEW WHOLE/CLOSE);
  - bevelled 16 px tiles with clue numbers; letters anti-aliased from DejaVu Serif Bold, one half-tone per tile colour, also on the keys;
  - keys as green tiles with white letters; drop shadows;
  - a rainbow rounded cursor outline with CHChess's glove over the cursor (it flips below the cursor on the top rows);
  - a red triangle for rub-out;
  - a x3 JACKPOT word per puzzle, star ranks on the puzzle list, a deal-in;
  - the title rebuilt in close-up tiles with a serif menu and a side-on glove selector (no navy/gold box).
- The owner liked the look in this direction; keep it.
- Rejected (tried, failed): themed grid fills. Grids are unthemed.

## Open items

- Awaiting the owner's verdict (built without explicit sign-off):
  - the whole grid at 8 px cells: white tiles on dark felt, cyan active word, gold locked words;
  - no numbers in the small cells (the clue bar shows 14A); the side HUD column; wide M/W glyphs in cells;
  - the glove only pokes keys; auto-check locks words (CHECKING OFF as the option);
  - 15x15 at 7 px for SD packs only; light casino flavour in titles and clues; the COMBO / CROSS! / SOLVED! banners.
- First device run, which is also the first hardware test of CHSd: `python tools/device.py run tools/scripts/device/perf.txt OUTDIR` for render times, then `python tools/check.py --compare` against the simulator's run of the same script. Try a FAT32 card, a FAT16 card, an exFAT card (should say FORMAT IT AS FAT32), no `CHCW` folder, and pulling the card mid-puzzle.
- The clues were written for the game and only spot-checked; a full proofread has not been done.

## Gotchas

- Flash: a built-in puzzle is ~700 B. The save page holds records for exactly the 20 built-in puzzles, so adding built-ins also needs a save-layout change (and a cut elsewhere).
- Device debug builds are `CHCW_LEAN` (config.h derives it from `CHGAME_DEBUG` on the board; the simulator is never lean; `-DCHCW_FULL` turns it off, and does not fit): only the first three built-in puzzles, no saving, no Options; start puzzles with `say G <i>`.
- SD code is generated. CHSd's master copy is `platform/libraries/CHSd` (MIT, HypeRunner's clean-room driver). This game's `src/sd/*`, `tools/chsim/host/VCard.h`, `tools/chsim/host/sd_host.cpp` and `tools/puzzles/fatimg.py` are copies; never edit them here. Edit CHSd, run its tests (`python platform/libraries/CHSd/tests/run_tests.py`), then from the repo root `python platform/libraries/CHSd/tools/vendor.py` (`--check` verifies the copies), then `python tools/check.py` here.
- The card shares SPI1 with the LCD: it is read only between frames and only on the puzzle list; a card puzzle is copied into 2 KB of RAM at start. Keep card access out of play and out of an in-flight flush.
- Simulator card: `tools/chsim/chdrive.py --card IMG` (sets `CHCW_CARD`); images come from `tools/puzzles/mkcard.py`. `check.py` runs `card_*.txt` scripts with `out/card.img` in the slot. `say X 0|1` (simulator) pulls / inserts the card.
- `check.py` runs every script twice and fails on any frame difference or a simulator BUG line (drawing into a frame still being sent): keep the game deterministic.
- Puzzle pipeline: `tools/puzzles/newgrid.py` fills a grid, clues are written into `tools/puzzles/src/*.txt`, `build_pack.py` checks them and regenerates `src/game/PuzzleData.cpp`. `tools/puzzles/cwformat.py` holds the reference decoder the host tests hold the game to: change the format in both.
- The grid maker needs `wordfreq` (`pip install wordfreq`, or `pip install --target tools/puzzles/data/pylib wordfreq`; that folder is gitignored). `tools/puzzles/avoid.txt` is the curated block list of junk words: add to it rather than hand-editing fills.
- Letters: `tools/tilefont.py` rasterizes DejaVu Serif Bold into `tools/art/tilefont.txt`; `tools/assets.py` packs the art into `src/assets/`.
- Sound: the CHGame library's engine (`chgame/Audio.h`); the effect tables are `src/audio/Sounds.*` in `Sfx` order. A locking word's rising notes (and the deal, title and result ticks) are `audio::note(hz, ms, 2)`: they give way only to the fanfares. `frame::begin()` starts the engine (`audio::begin(..., false)`), `applyOptions()` switches it with `audio::setOn()` (calling `begin()` there instead would be 8 B smaller). WAVs: `python ../../tools/audio/preview.py . out/audio`.
- Debug hooks (above the hook in `src/states/Screens.cpp`): `G` start puzzle, `H` STATE line, `W` next word, `C` cursor, `Z` fill all but the last k words, `U` advance the clock, `J` jump, `X` and `Q` simulator only. chdrive extras: `state`, `expect`, `waitstate`, `type`, `solve [N]`, `wrong`, `mark`/`delta`, `solveto`, `solvemost`, `rec pause/resume`, `cal` and a calibrated `perf`, `--card`.
- The debug protocol is the CHGame library's (`chgame/Debug.h`, on with `CHGAME_DEBUG`); the save record's pages and CRC are the library's too (`chgame/Save.cpp`), the game's `src/save/Save.*` says what goes in it (unchanged layout: magic "CHCW", version 1, the puzzle-in-progress flag in the header). The script driver is the shared `../../tools/chsim/chdrivelib.py`; tools/chsim/chdrive.py adds the commands above.
- `src/fx` has only what the game uses: SPARK, CONFETTI and STAR particles, RAINBOW and GOLD banners (the DUST puffs and the RED, CYAN and WHITE banners copied from the casino games were never used, and were cut for 140 B on 2026-10-02).
- `tools/scripts/gameplay.txt` makes the README reel (`docs/gameplay.gif`).
- Credits are exactly those in NOTICE (Press Play On Tape's 3x5 font, DejaVu, CHSd/HypeRunner, ENABLE and wordfreq as build-time aids); add no others. `src/sd` and `fatimg.py` are MIT, the rest Apache-2.0.
- The simulator is `../../tools/chsim/chsim.py` (shared); per-game tools stay in `tools/`. For host builds set `CHSIM_CXX` or have zig/clang++/g++ on PATH (see root CLAUDE.md).
- Device debug builds leave out saving and most puzzles; the board may be in use, so announce a debug upload and put the release back afterwards.
