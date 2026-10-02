# Status of the games (as of 2026-10-02)

**What the columns mean:**
- **Image:** the release build (`opt=oslto,rtlib=nano,periph=game,usb=uploadonly`,
  core 0.2.4, CHGfx 1.3.0).
- **Save room:** what is left under 50,432 B, the largest image that still
  leaves both A/B save pages at 0xF500/0xF600 (see
  [platform.md](platform.md#saving-flash-pages-instead-of-eeprom)).
- **RAM:** static RAM out of 18,416 B.
- **Simulator / Device:** what has been verified where. Each game's
  `NOTES.md` has the details and its open items. The Device column is the
  session of 2026-10-02 ([hardware-2026-10-02.md](hardware-2026-10-02.md)):
  debug builds driven by script, with each game's render times and stack
  there. No release build has been played through yet.

| Game | Image | Save room | RAM | Simulator | Device |
|---|---|---|---|---|---|
| CHBackgammon | 50,224 | 208 | 16,892 | check.py | debug build: `gameplay` ran; render times and stack measured |
| CHBingo | 36,320 | 14,112 | 14,912 | tests, scripts, sim_save, diffdrive | debug build: `gameplay` and `perf` ran; 5 of 6 clips equal the simulator's |
| CHBlackjack | 45,572 | 4,860 | 15,436 | tests, scripts | **runs; render times measured**; debug build: `gameplay` ran, every clip equal to the simulator's |
| CHBoardwalk | 49,668 | 764 | 15,052 | tests, scripts | debug build: `gameplay` and `perf` ran |
| CHCheckers | 42,168 | 8,264 | 17,108 | check.py | debug build: `perf` ran; `gameplay` needs a command the lean build lacks |
| CHChess | 48,764 | 1,668 | 17,544 | tests, scripts | **runs; render and think times, stack measured**; `gameplay` needs a command the lean build lacks |
| CHCraps | 49,876 | 556 | 15,568 | tests, scripts, sim_save | debug build: `perf` ran (23 ms worst); `gameplay` needs a command the lean build lacks |
| CHCrossword | 50,352 | 80 | 17,276 | check.py (incl. FAT card images) | debug build: `gameplay` and `perf` ran |
| CHDominoes | 42,728 | 7,704 | 16,864 | check.py | debug build: `gameplay` and `perf` ran |
| CHFour | 36,728 | 13,704 | 16,348 | check.py | debug build: `gameplay`, `perf` and `ui` ran; the release build starts |
| CHMahjong | 48,516 | 1,916 | 17,812 | tests, scripts | debug build: starts, part of `perf` ran; the scripts need a command the lean build lacks |
| CHPoker | 48,480 | 1,952 | 15,500 | tests, scripts | debug build: `gameplay` and `perf` ran |
| CHRoulette | 49,848 | 584 | 16,072 | tests, scripts, ball tests, diffdrive | debug build: `gameplay` and `perf` ran; 4 of 5 clips equal the simulator's |
| CHSlots | 47,596 | 2,836 | 14,916 | tests, scripts, diffdrive | debug build: `gameplay` and `perf` ran (24 ms worst); every clip equal to the simulator's |
| CHSnakes | 37,204 | 13,228 | 15,360 | check.py | **debug build runs the title; title render time and stack measured** (2026-10-02); the release build was played briefly |
| CHSolitaire | 30,812 | 19,620 | 16,188 | check.py | debug build: `gameplay` ran, most of `perf` |
| CHTicTacToe | 49,644 | 788 | 14,580 | tests, scripts, diffdrive | debug build: `gameplay` and `perf` ran; every clip equal to the simulator's |
| CHWords | 50,324 | 108 | 15,788 | check.py (incl. the SD dictionary) | debug build: four of `gameplay`'s clips; the CPU's `auto` outlasts the driver |
| CHWordWheel | 50,312 | 120 | 14,956 | check.py (incl. the SD bank, diffdrive) | debug build: `gameplay` and `perf` ran; 4 of 5 clips equal the simulator's |
| CHYacht | 44,036 | 6,396 | 15,260 | tests, scripts, sim_save | debug build: `gameplay` and `perf` ran; every clip equal to the simulator's |

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

**Still owed on the board, for each game** (the scripted debug-build runs
of 2026-10-02 covered frame times and stack):
- the release build played from the SD menu;
- CPU thinking time where there is a CPU;
- the sound by ear;
- saving across a power cycle;
- for the SD games, their files on a real card. The bootloader's C fork of
  CHSd reads the card for the menu; the library itself has not been seen
  to read a game's file on a board.

## The bootloader with the SD game menu

[platform/bootloader](../platform/bootloader) (BOOT_VERSION 2):

| | Verified | Device |
|---|---|---|
| Menu bootloader (release, 12,032 B) | PC suite (`test/native/run_tests.py`): flash/SD/panel models, every package error, power cuts at every flash operation of an install and of an upload, all 21 real packages installed in turn, 26 pinned menu frames (three colour themes) | **installed and checked on 2026-10-01** ([RESULTS](../platform/bootloader/test/hil/RESULTS-2026-10-01.md)); on 2026-10-02 written from the Arduino side over USB (*Burn Bootloader*, programmer CHGame USB), to and from the 0.2.4 and no-menu bootloaders |
| Card builder (`tools/sdcard/mkcard.py`) | all 20 games and CHSDtoUSB built and packed; payloads equal the release images above | |

What that run left open (a fragmented card, a second card, install times)
is at the end of its results. [HARDWARE.md](../platform/bootloader/HARDWARE.md)
has the steps for another board.

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

- **The USB serial port could go mute (fixed 2026-10-02).** The core's
  `CDC_flush()` armed a packet before it set the busy flag; an interrupt
  between the two left the flag set for good and every later write was
  dropped. On the board it showed as debug-protocol scripts that stopped
  answering at a different step each run (12 of the first 34 runs of the
  hardware session). Release games have no serial path. The fix is in
  `platform/board`, so it reaches a build with the next board package.
- **A debug build could stop at its first frame (fixed 2026-10-02).** The
  library's `dbg::begin()` painted the stack, for the `P` command's
  high-water mark, up to 64 B below one of its own locals. With LTO it is
  inlined into `main()`, whose frame reaches further down, so the paint
  went into `main()`'s saved values. CHSnakes' debug build faulted on it,
  with the title's first note left sounding; every game's debug build had
  the same code. It paints up to the stack pointer now, and a fault
  silences the piezo. Release builds and the simulator never ran it.

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
| CHBackgammon | 80cf126 | CHMahjong | debug build: `gameplay` ran; render times and stack measured |
| CHBingo | dd6295b | CHPoker | debug build: `gameplay` and `perf` ran; 5 of 6 clips equal the simulator's |
| CHBlackjack | 88d8fc7 | CHRoulette | **runs; render times measured**; debug build: `gameplay` ran, every clip equal to the simulator's |
| CHBoardwalk | a99a4f8 | CHSlots | debug build: `gameplay` and `perf` ran |
| CHCheckers | a9ec530 | CHSnakes | debug build: `perf` ran; `gameplay` needs a command the lean build lacks |
| CHChess | 34e4382 | CHSolitaire | **runs; render and think times, stack measured**; `gameplay` needs a command the lean build lacks |
| CHCraps | fa1fd77 | CHTicTacToe | debug build: `perf` ran (23 ms worst); `gameplay` needs a command the lean build lacks |
| CHCrossword | 68c482e | CHWords | debug build: `gameplay` and `perf` ran |
| CHDominoes | ddace41 | CHWordWheel | debug build: `gameplay` and `perf` ran |
| CHFour | 6c3fd6a | CHYacht | debug build: `gameplay`, `perf` and `ui` ran; the release build starts |

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
