# Status of the games (as of 2026-10-02)

**What the columns mean:**
- **Image:** the release build (`opt=oslto,rtlib=nano,periph=game,usb=uploadonly`,
  core 0.2.4, CHGfx 1.3.0).
- **Save room:** what is left under 50,432 B, the largest image that still
  leaves both A/B save pages at 0xF500/0xF600 (see
  [platform.md](platform.md#saving-flash-pages-instead-of-eeprom)).
- **RAM:** static RAM out of 18,416 B.
- **Simulator / Device:** what has been verified where. Every game has
  `chgame check` (host tests, every script twice, the device build; its
  `tools/game.py` adds the rest). Each game's `NOTES.md` has the details
  and its open items.

| Game | Image | Save room | RAM | Simulator | Device |
|---|---|---|---|---|---|
| CHBackgammon | 50,296 | 136 | 16,892 | `chgame check` | never run |
| CHBingo | 36,388 | 14,044 | 14,912 | `chgame check`, sim_save, redraw | never run |
| CHBlackjack | 45,640 | 4,792 | 15,436 | `chgame check` | **runs; render times measured** (the last art-only commit not re-run) |
| CHBoardwalk | 49,732 | 700 | 15,052 | `chgame check` | never run |
| CHCheckers | 42,232 | 8,200 | 17,108 | `chgame check` | never run |
| CHChess | 48,832 | 1,600 | 17,544 | `chgame check` | **runs; render and think times, stack measured** |
| CHCraps | 49,940 | 492 | 15,568 | `chgame check`, sim_save | never run |
| CHCrossword | 50,416 | 16 | 17,276 | `chgame check` (incl. FAT card images) | never run |
| CHDominoes | 42,796 | 7,636 | 16,864 | `chgame check` | never run |
| CHFour | 36,792 | 13,640 | 16,348 | `chgame check` | never run |
| CHMahjong | 48,580 | 1,852 | 17,812 | `chgame check` | an early build ran well; current build not run |
| CHPoker | 48,544 | 1,888 | 15,500 | `chgame check` | never run |
| CHRoulette | 49,916 | 516 | 16,072 | `chgame check`, ball tests, redraw | never run |
| CHSlots | 47,664 | 2,768 | 14,916 | `chgame check`, redraw | never run |
| CHSnakes | 37,272 | 13,160 | 15,360 | `chgame check` | **debug build runs the title; title render time and stack measured** (2026-10-02) |
| CHSolitaire | 30,876 | 19,556 | 16,188 | `chgame check` | never run |
| CHTicTacToe | 49,712 | 720 | 14,580 | `chgame check`, redraw | never run |
| CHWords | 50,388 | 44 | 15,788 | `chgame check` (incl. the SD dictionary) | never run |
| CHWordWheel | 50,380 | 52 | 14,956 | `chgame check` (incl. the SD bank), redraw | never run |
| CHYacht | 44,100 | 6,332 | 15,260 | `chgame check`, sim_save | never run |

When the games were brought into this repository, every simulator script (211), host
test, audio preview, redraw check and release build was re-run and compared
with the original repositories. The frames, test results, WAVs and `.bin`
files were identical. The one exception was CHBoardwalk's `save` script,
which also differs between two runs of the original (see Known issues).
The release builds compiled against `platform/board/arduino/CHGame/libraries/CHGfx` with no
sketchbook libraries.

**On the CHGame library (2026-10-02).** Every game moved onto
`platform/board/arduino/CHGame/libraries/CHGame` (graphics helpers, sound, saving, the debug
protocol). Checked game by game:
- every simulator script against the frames from before (identical, but
  for the one-pixel changes listed in [unification.md](unification.md));
- every sound effect, millisecond by millisecond, against the old engine;
- every save layout, field by field (old saves still load);
- every script again under valgrind (`tools/chsim/chsim.py`'s memory check).

That turned up two bugs, both fixed: CHBoardwalk dealt from an
uninitialised count (its `save` script's frames changed from run to run, and
the simulator usually crashed), and CHCrossword's debug STATE line
overflowed its buffer late in a puzzle.

**The first device session for each game should cover:**
- frame times (debug build, `perf` scripts);
- CPU thinking time where there is a CPU;
- the sound by ear;
- saving across a power cycle;
- for the SD games, a real card. CHSd has never read one on a board.

## The bootloader with the SD game menu

[platform/bootloader](../platform/bootloader) (BOOT_VERSION 2):

| | Verified | Device |
|---|---|---|
| Menu bootloader (release, 12,032 B) | PC suite (`test/native/run_tests.py`): flash/SD/panel models, every package error, power cuts at every flash operation of an install and of an upload, all 21 real packages installed in turn, 26 pinned menu frames (three colour themes) | **never run**; [HARDWARE.md](../platform/bootloader/HARDWARE.md) has the steps |
| Card builder (`tools/sdcard/mkcard.py`) | all 20 games and CHSDtoUSB built and packed; payloads equal the release images above | |

The first device session follows HARDWARE.md:
- **HW1:** the menu as a program, under the current bootloader.
- **HW2a:** the new code without the menu.
- **HW2b:** the menu bootloader.
- **HW3:** the matrix.

Its open questions are the SD clock that real cards take (12 MHz is
assumed), the panel's colour order, install time, and the CHSd timings on
real cards.

## Known issues

### Save magics (fixed 2026-10-01)

All games keep their saves in the same two flash pages, and each must
recognise only its own records. A record is accepted when its magic **and**
version match. Until 2026-10-01 three pairs collided:

| Games | Old magic | Now |
|---|---|---|
| CHSlots, CHSolitaire | `0x4C534843` "CHSL", both version 1 (live), plus the same debug id and `CHSL_` prefix | CHSolitaire: magic `0x4F534843` "CHSO", handshake `CHSO`, prefix `CHSO_` |
| CHCraps, CHYacht | `0x52434843` "CHCR", both version 1 (live) | CHYacht: `0x44594843` "CHYD" |
| CHBackgammon, CHFour | `0x47424843` "CHBG", versions 2 and 1 (latent) | CHFour: `0x34464843` "CHF4" |

They were fixed with the SD game menu, which makes switching games routine.
A save written by an older build of those three games is ignored once. The
simulator frames of all three were compared before and after (identical:
69, 54 and 39 images) and their release images did not change size.

Every game still shares the two pages: the next game to save overwrites the
last one's record. [sd-menu.md](sd-menu.md) says so to players.

### Other

- **One tooling for the twenty games (2026-10-02).** One entry point,
  `chgame` (`pip install -e .`), replaced the twenty `tools/run.py` and
  `tools/device.py`; `chgame check`, `test`, `redraw` and the save tests
  are shared and every game has them (`tools/game.py` says what to run);
  `tools/chsim` is the one simulator (CHGfx's examples and tests run on
  it); the art the games had in common, the mock-up kit, the music
  composer and the font tools are shared; the particles, banners and
  floating texts are the library's `chgame/Sizzle`; the Python uploader
  is what the tools call, with the Go tool held to the same vectors; the
  release tooling is `tools/release/`. Checked at every step against a
  capture from before: all twenty release images byte for byte the same
  (the simulator's new panel model moved 11 timing-seeded script runs and
  CHCheckers' GIF, re-recorded; nothing else).
- **Two device debug builds do not fit (2026-10-02).** `chgame build
  --debug` overflows the flash for CHTicTacToe (by 332 B) and CHRoulette
  (by 140 B), lean variants included, since the core's crash handler and
  the library's protocol grew; their release builds are unaffected. Their
  device scripts need a trim first (a screen or a table behind `<PFX>_LEAN`).
- **The games are the CHGame library's examples (2026-10-02).** `games/`
  and `utilities/CHSDtoUSB` moved to
  `platform/board/arduino/CHGame/libraries/CHGame/examples/games/`
  and `.../examples/apps/`. Every release image is byte for byte unchanged
  and every README reel frame for frame; all host tests pass from there.
- **The bootloader's PC suite runs on Windows (2026-10-02)**, through zig
  and WSL. All of it passes; the twelve box frames owed since the first
  hardware run were re-pinned and the menu pictures redrawn.
- **The libraries are in the board package (2026-10-02).** CHGame, CHGfx
  and CHSd moved to `platform/board/arduino/CHGame/libraries/`, and the three
  SD games use CHSd as a library instead of a generated copy. 17 release
  images are byte for byte unchanged; CHWords, CHCrossword and CHWordWheel
  are 4, 8 and 56 B smaller; every simulator frame compared is identical
  ([bundling-plan.md](bundling-plan.md)).
- **Lean debug builds' Stats pages (fixed 2026-10-02).** On a device debug
  build that leaves saving out (CHPoker, CHTicTacToe, CHSolitaire with
  `-DCHSO_LEAN=1`), the Stats page said "SAVED IN FLASH" since the move to
  the library. It says "SAVING UNAVAILABLE" again. Release images are byte
  counts unchanged (48,480 / 49,644 / 30,812 B); the simulator is never
  lean, so its frames are unchanged.
- **One README GIF a game (2026-10-02).** Every game's README has the same
  format ([game-readme.md](game-readme.md)) and one `docs/gameplay.gif` of
  at most 1 MB, recorded by `tools/scripts/gameplay.txt` and joined by
  `tools/readme_gif.py`. The other GIFs and screenshots are gone, with the
  six that no script made any more.
- **Device-only scripts stop in the simulator.** CHBlackjack's `perf_free`,
  `prof` and `prof_hand` (wall-clock and profile-build scripts: `prof` needs
  `-DCHGAME_PROFILE=1`) and CHBoardwalk's and CHChess's `pace` are for the
  board; `chgame check` skips them (`SKIP_SCRIPTS` in their `tools/game.py`).
- **Generated files a fresh clone needs before some tests:**
  - CHWordWheel: `chgame test` needs `tools/phrases/build/bank_ref.txt`
    (run `tools/phrases/build_bank.py` or `chgame check` first).
  - CHWords: the full-word-list check runs only after
    `tools/dict/wordlist.py` has downloaded its lists.
- **`gifsheet.py` options changed.** The shared copy is the newest version,
  with `--every/--start/--count/--cols/--scale` options. CHBoardwalk and
  CHSnakes used to carry an older copy that took positional arguments.

## Where each game came from

Each game was copied, without history, from the head of its repository at
`https://github.com/bateske/<Name>`:

| Game | Commit | Game | Commit |
|---|---|---|---|
| CHBackgammon | 80cf126 | CHMahjong | 481dfdf |
| CHBingo | dd6295b | CHPoker | 0840afd |
| CHBlackjack | 88d8fc7 | CHRoulette | d8c2f67 |
| CHBoardwalk | a99a4f8 | CHSlots | 67fbef5 |
| CHCheckers | a9ec530 | CHSnakes | 89bba02 |
| CHChess | 34e4382 | CHSolitaire | 38d0309 |
| CHCraps | fa1fd77 | CHTicTacToe | db8274c |
| CHCrossword | 68c482e | CHWords | af15e9a |
| CHDominoes | ddace41 | CHWordWheel | 7c97419 |
| CHFour | 6c3fd6a | CHYacht | 751b026 |

CHSDtoUSB came from `bateske/CHSDtoUSB` at 379583e. CHGfx is tag 1.3.0
(838bbb0), the board package is CH32SerialBoot tag v0.2.4 (5de3006), and
CHSd is version 1.0.0.

**Changes made while moving each game in:**
- The shared tools (`chsim.py` and its host shims, `fbimage.py`,
  `gifsheet.py`, `serialcap.py`, `check_size.py`, `requirements.txt`) were
  removed from the games and now live in the root `tools/`.
- The games' own scripts found them through `../../tools` (since the games became the library's examples: nine folders up, or `tools/run.py`).
- `device.py` builds against `platform/board/arduino/CHGame/libraries/CHGfx`.
- Each README gained a repository banner and new paths.
- Each game gained a `NOTES.md`.
