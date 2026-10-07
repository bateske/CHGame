# Status of the games (as of 2026-10-02; sizes of 2026-10-07)

**What the columns mean:**
- **Image:** the release build (`opt=oslto,rtlib=nano,periph=game,usb=uploadonly`,
  board package 0.3.0 as staged on 2026-10-07, CHGfx 1.3.1). A release build
  that leaves fewer than two save pages fails (`SAVE_PAGES`).
- **Save room:** what is left under 50,432 B, the largest image that still
  leaves both A/B save pages at 0xF500/0xF600 (see
  [platform.md](platform.md#saving-flash-pages-instead-of-eeprom)).
- **RAM:** static RAM out of 18,416 B.
- **Simulator / Device:** what has been verified where. Every game has
  `chgame check` (host tests, every script twice, the device build; its
  `tools/game.py` adds the rest). Each game's `NOTES.md` has the details
  and its open items. The Device column is the
  session of 2026-10-02 ([hardware-2026-10-02.md](hardware-2026-10-02.md)):
  debug builds driven by script, with each game's render times and stack
  there. No release build has been played through yet.

| Game | Image | Save room | RAM | Simulator | Device |
|---|---|---|---|---|---|
| CHBackgammon | 49,488 | 944 | 16,524 | `chgame check` | debug build: `gameplay` ran; render times and stack measured |
| CHBingo | 36,912 | 13,520 | 14,800 | `chgame check`, sim_save, redraw | debug build: `gameplay` and `perf` ran; 5 of 6 clips equal the simulator's |
| CHBlackjack | 46,064 | 4,368 | 15,332 | `chgame check` | **runs; render times measured**; debug build: `gameplay` ran, every clip equal to the simulator's |
| CHBoardwalk | 49,832 | 600 | 14,924 | `chgame check` | debug build: `gameplay` and `perf` ran |
| CHCheckers | 41,864 | 8,568 | 16,932 | `chgame check` | debug build: `perf` ran; `gameplay` needs a command the lean build lacks |
| CHChess | 48,480 | 1,952 | 17,368 | `chgame check` | **runs; render and think times, stack measured**; `gameplay` needs a command the lean build lacks |
| CHCraps | 50,428 | 4 | 15,464 | `chgame check`, sim_save | debug build: `perf` ran (23 ms worst); `gameplay` needs a command the lean build lacks |
| CHCrossword | 50,008 | 424 | 17,100 | `chgame check` (incl. FAT card images) | debug build: `gameplay` and `perf` ran |
| CHDominoes | 43,424 | 7,008 | 16,744 | `chgame check` | debug build: `gameplay` and `perf` ran |
| CHFour | 36,456 | 13,976 | 16,172 | `chgame check` | debug build: `gameplay`, `perf` and `ui` ran; the release build starts |
| CHMahjong | 48,776 | 1,656 | 17,700 | `chgame check` | debug build: starts, part of `perf` ran; the scripts need a command the lean build lacks |
| CHPoker | 48,952 | 1,480 | 15,384 | `chgame check` | debug build: `gameplay` and `perf` ran |
| CHRoulette | 49,872 | 560 | 15,968 | `chgame check`, ball tests, redraw | debug build: `gameplay` and `perf` ran; 4 of 5 clips equal the simulator's |
| CHSlots | 48,076 | 2,356 | 14,796 | `chgame check`, redraw | debug build: `gameplay` and `perf` ran (24 ms worst); every clip equal to the simulator's |
| CHSnakes | 37,280 | 13,152 | 15,240 | `chgame check` | **debug build runs the title; title render time and stack measured** (2026-10-02); the release build was played briefly |
| CHSolitaire | 31,304 | 19,128 | 16,580 | `chgame check` | debug build: `gameplay` ran, most of `perf` |
| CHTicTacToe | 50,232 | 200 | 14,540 | `chgame check`, redraw | debug build: `gameplay` and `perf` ran; every clip equal to the simulator's |
| CHWords | 50,036 | 396 | 15,612 | `chgame check` (incl. the SD dictionary) | debug build: four of `gameplay`'s clips; the CPU's `auto` outlasts the driver |
| CHWordWheel | 49,832 | 600 | 14,776 | `chgame check` (incl. the SD bank), redraw | debug build: `gameplay` and `perf` ran; 4 of 5 clips equal the simulator's |
| CHYacht | 44,704 | 5,728 | 15,140 | `chgame check`, sim_save | debug build: `gameplay` and `perf` ran; every clip equal to the simulator's |

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

[platform/bootloader](../platform/bootloader):

| | Verified | Device |
|---|---|---|
| Menu v2 (BOOT_VERSION 3, release 11,908 B, 2026-10-03; Rainbow and White styles): folders of up to 240 entries, MENU.IDX order, MENU.BG (the logo is in the picture), launch at power-on | PC suite: flash/SD/panel models, every CHG error, power cuts at every flash operation of an install and of an upload, the real casino card's games installed in turn, cards made by `tools/chcart` (order, folders, an empty folder, a folder of 250, launch, START held, a broken background), both styles, 26 pinned menu frames | **installed and checked on 2026-10-03**, Rainbow and White ([RESULTS](../platform/bootloader/test/hil/RESULTS-2026-10-03.md)); the binaries in `release/` |
| The first menu (BOOT_VERSION 2, 12,032 B; kept in git history) | the same suite as it was then | **installed and checked on 2026-10-01** ([RESULTS](../platform/bootloader/test/hil/RESULTS-2026-10-01.md)); on 2026-10-02 written from the Arduino side over USB (*Burn Bootloader*, programmer CHGame USB), to and from the 0.2.4 and no-menu bootloaders |
| The casino cart (`chgame card`: `tools/sdcard/casino.json`, `tools/chcart`) | all 20 games and both apps built into `out/CHGame-Casino.chgame` and its card; the payloads are the release images | |

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
  The hardware session of 2026-10-02 ran both before those fixes were in.
- **The games are the CHGame library's examples (2026-10-02).** `games/`
  and `utilities/CHSDtoUSB` moved to
  `platform/board/arduino/CHGame/libraries/CHGame/examples/Games/`
  and `.../examples/Apps/`. Every release image is byte for byte unchanged
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

CHSDtoUSB came from `bateske/CHSDtoUSB` at 379583e; on 2026-10-02 it was replaced by CHCasino's later version (`utilities/CHSDtoUSB` at 53e5064: the instrument panel and file events), moved onto the CHGame library without its sparks. CHStlView came from `bateske/CHStlView` at b3d6430 the same day. CHGfx is tag 1.3.0
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
