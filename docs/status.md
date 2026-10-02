# Status of the games (as of 2026-10-02)

**What the columns mean:**
- **Image:** the release build (`opt=oslto,rtlib=nano,periph=game,usb=uploadonly`,
  core 0.2.4, CHGfx 1.3.0).
- **Save room:** what is left under 50,432 B, the largest image that still
  leaves both A/B save pages at 0xF500/0xF600 (see
  [platform.md](platform.md#saving-flash-pages-instead-of-eeprom)).
- **RAM:** static RAM out of 18,416 B.
- **Simulator / Device:** what has been verified where. Each game's
  `NOTES.md` has the details and its open items.

| Game | Image | Save room | RAM | Simulator | Device |
|---|---|---|---|---|---|
| CHBackgammon | 50,224 | 208 | 16,892 | check.py | never run |
| CHBingo | 36,320 | 14,112 | 14,912 | tests, scripts, sim_save, diffdrive | never run |
| CHBlackjack | 45,572 | 4,860 | 15,436 | tests, scripts | **runs; render times measured** (the last art-only commit not re-run) |
| CHBoardwalk | 49,668 | 764 | 15,052 | tests, scripts | never run |
| CHCheckers | 42,168 | 8,264 | 17,108 | check.py | never run |
| CHChess | 48,764 | 1,668 | 17,544 | tests, scripts | **runs; render and think times, stack measured** |
| CHCraps | 49,876 | 556 | 15,568 | tests, scripts, sim_save | never run |
| CHCrossword | 50,360 | 72 | 17,276 | check.py (incl. FAT card images) | never run |
| CHDominoes | 42,728 | 7,704 | 16,864 | check.py | never run |
| CHFour | 36,728 | 13,704 | 16,348 | check.py | never run |
| CHMahjong | 48,516 | 1,916 | 17,812 | tests, scripts | an early build ran well; current build not run |
| CHPoker | 48,480 | 1,952 | 15,500 | tests, scripts | never run |
| CHRoulette | 49,848 | 584 | 16,072 | tests, scripts, ball tests, diffdrive | never run |
| CHSlots | 47,596 | 2,836 | 14,916 | tests, scripts, diffdrive | never run |
| CHSnakes | 37,204 | 13,228 | 15,360 | check.py | never run |
| CHSolitaire | 30,812 | 19,620 | 16,188 | check.py | never run |
| CHTicTacToe | 49,644 | 788 | 14,580 | tests, scripts, diffdrive | never run |
| CHWords | 50,328 | 104 | 15,788 | check.py (incl. the SD dictionary) | never run |
| CHWordWheel | 50,368 | 64 | 14,952 | check.py (incl. the SD bank, diffdrive) | never run |
| CHYacht | 44,036 | 6,396 | 15,260 | tests, scripts, sim_save | never run |

When the games were brought into this repository, every simulator script (211), host
test, audio preview, redraw check and release build was re-run and compared
with the original repositories. The frames, test results, WAVs and `.bin`
files were identical. The one exception was CHBoardwalk's `save` script,
which also differs between two runs of the original (see Known issues).
The release builds compiled against `platform/libraries/CHGfx` with no
sketchbook libraries.

**On the CHGame library (2026-10-02).** Every game moved onto
`platform/libraries/CHGame` (graphics helpers, sound, saving, the debug
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

- **CHBlackjack's device-only scripts stop in the simulator.** They are
  `perf_free`, `prof` and `prof_hand` (wall-clock and profile-build
  scripts: `prof` needs `-DCHGAME_PROFILE=1`), and they are for the board.
- **Some device-only scripts stop in the simulator.** CHBoardwalk `pace` and
  CHChess `pace` exit with "game refused" there.
- **Generated files a fresh clone needs before some tests:**
  - CHWordWheel: `run_tests.py` needs `tools/phrases/build/bank_ref.txt`
    (run `tools/phrases/build_bank.py` or `check.py` first).
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
- The games' own scripts find them through `../../tools`.
- `device.py` builds against `platform/libraries/CHGfx`.
- Each README gained a repository banner and new paths.
- Each game gained a `NOTES.md`.
