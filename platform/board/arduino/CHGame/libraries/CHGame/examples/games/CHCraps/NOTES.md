# CHCraps — development notes

Agent-facing notes for continuing work here; rules and controls are in README.md, the platform in the repo-root CLAUDE.md and docs/.

## Snapshot

- Imported from https://github.com/bateske/CHCraps at commit fa1fd77 (2026-10-01); develop here now, not in the old repo.
- Release build (`opt=oslto,rtlib=nano,periph=game,usb=uploadonly`, core 0.2.4, CHGfx 1.3.0): flash 49,776 of 50,944 B (1,168 spare), static RAM 15,520 of 18,416 B (2,896 spare).
- The image (`../../../../../../../../../tools/check_size.py`'s `image:` line; 50,032 B when last measured) is only ~400 B under the 50,432 B that keeps both A/B save pages (0xF500 and 0xF600, the CHGame library's `chgame/Save.cpp`). Past 0xF500 saving drops to one page; past 0xF600 it switches off.
- Verification: simulator only. `tools/tests/run_tests.py` (every bet against an independent oracle, exact house edges, dice physics, zone reachability), `tools/tests/sim_save.py` (save mid-hand, debug `V` reboot and continue, the broke case), and the chdrive scripts in `tools/scripts`. There is no `tools/check.py` in this game.
- As of 2026-10-01 it has never run on the device: frame times unmeasured, sound unheard.

## Design decisions

- Chosen: TABLE option CLASSIC / BEGINNER (Beginner keeps line, don't, odds, field, place 6/8 on a roomier layout).
- Chosen: hold A on ROLL to shake, release to throw.
- Chosen: CHBlackjack's split layout (wall, felt, bar) plus the 3D "dice cam".
- Chosen: CHBlackjack's dealer works the table as the stickman and calls every roll.
- Chosen: keep the lit ON puck - a white disc showing the point number in the 3x5 font, pinned to the number box.
- Chosen: the dice show pips whenever they are on screen. The result is repainted at the back-wall hit, choosing the labelling that changes the fewest faces.
- Chosen: music only if flash is left once the game is complete; there is none (`src/audio/Sounds.h` says so).
- Architecture to keep: the rules settle the whole roll in `Craps::throwDice()` (a result per spot); the presenter (`src/fx/Presenter.cpp`) only replays it - call, losers swept, pays, home, come moves. Money has already moved, so a save mid-show is always consistent.

## Open items

- First device run. Simulator estimates put the dice cam's shake and the result + banner at 9-15 ms a frame, over the ~8 ms drawing budget for 60 fps. Measure on the board (`python tools/device.py run tools/scripts/perf.txt OUTDIR`) before optimising.
- Listen to the sound effects on the piezo (`python tools/run.py audio/preview.py . out/audio` renders them to WAV meanwhile).
- Known issue (logged, not fixed; see ../../../../../../../../../docs/status.md): CHYacht uses this game's save magic `0x52434843` "CHCR" with the same
  version 1, so after playing one, the other accepts its save. The fix is a new magic in CHYacht.
- Music: deferred until flash allows (it does not now).

## Gotchas

- Flash is effectively full while both save pages are kept. Tactics already in use: chips and pucks are span sprites (the CHGame library's `sprite4`) recoloured by remap tables (drawn from CHBlackjack's chip, made by `tools/assets.py`); all 24 die orientations come from one walk of quarter turns stored in a 24-bit constant (`labelDie`, `WALK` 0x288A28 in `src/cam/Dice3D.cpp`); the dice share the game's sine table; no music.
- Device debug builds get `CHCR_LEAN` automatically (`config.h`): no saving, no Options or Stats. `-DCHCR_FULL` forces the whole game into a debug build (check it fits).
- Dice3D: integer Euler-angle cubes and a tilting pinhole camera; physics steps once per 60 Hz tick, so the dice keep their speed if a frame is slow. The throw is pre-simulated deterministically and the dice relabelled afterwards: any physics change moves where they land, so rerun `run_tests.py` after touching it.
- Drawing: the table redraws only the bands (wall, felt, bar) that changed or that something moving touched; the dice cam redraws everything each frame, so that is where frame time goes.
- Debug hooks (listed above the hook in `src/states/Screens.cpp`): `R` seed, `F` force rolls, `J` jump to a screen, `M` purse, `V` reboot (reload from flash), `E` set a bet, `X` point, `C` cursor zone, `Z` D-pad route, `H` state, `Q` (simulator) calibration. New hook letters must avoid the protocol's own: `? S K L N P T B`.
- chdrive extras: `goto ZONE` walks the cursor with real D-pad taps on the game's planned route; `idle` waits out the dice cam and the payout.
- Credits: the dealer's art and the 3x5 font are Press Play On Tape's (Simon Holmes / filmote, Stephane C / vampirics) by way of CHBlackjack. Credits are exactly those in NOTICE; add no others.
- Paths moved with the monorepo: the size report is `../../../../../../../../../tools/check_size.py`, the simulator `../../../../../../../../../tools/chsim/chsim.py`; per-game tools stay in `tools/`. For host builds set `CHSIM_CXX` or have zig/clang++/g++ on PATH (see root CLAUDE.md).
- Device debug builds leave out saving; the board may be in use, so announce a debug upload and put the release back afterwards.

## Development

Everything can be checked on a PC: Python 3 with `pip install -r ../../../../../../../../../tools/requirements.txt`, and a C++ compiler for the simulator and the tests (zig, clang++ or g++ on the PATH, `pip install ziglang`, or `CHSIM_CXX="path/to/zig c++"`; root CLAUDE.md).

    python tools/tests/run_tests.py          # rules, dice physics, layout reachability
    python tools/tests/sim_save.py           # save mid-hand, power-cycle, continue
    python tools/run.py chsim/chsim.py build .
    python tools/chsim/chdrive.py --sim . tools/scripts/sc_show.txt out/sc_show
    python tools/run.py readme_gif.py         # tools/scripts/gameplay.txt -> docs/gameplay.gif (the README's one GIF, <= 1 MB)
    python tools/assets.py                   # dealer, logo, chips -> src/assets/
    python tools/run.py audio/preview.py . out/audio  # every sound effect to WAV
    python tools/device.py build|upload [--debug]
    python tools/run.py check_size.py build/release

- The README GIF: `gameplay.txt` records five clips (`01_title`, `02_comeout`, `03_hardfour`, `04_hot`, `05_sevenout`). The come-out is played with the buttons alone; the later clips set bets with `say E` off camera, and every roll is forced with `say F`. The play clips use `rec start 4` to stay under 1 MB (the dice cam compresses badly).
- Other scripts are tests and look-dev, written to `out/`: `betting.txt` (the plaque, a refused bet, chips down and back, picking from the rack), `beginner.txt` (a Beginner-table hand: line and field, point 8, the 6 placed for $12, $20 odds, a hard six, winner eight), `showcase.txt`, `sc_show.txt`, `sc_screens.txt`, `look_table.txt`, `look_cam.txt`, `review_roll.txt`, `perf.txt`.
- The debug build (`--debug`) speaks the CHGame library's serial protocol (`chgame/Debug.h`). The game's commands are in `src/states/Screens.cpp`: reseed or force the dice, jump to a screen, set bets, the purse or the point, move the cursor, dump the table state (letters under Gotchas). The same scripts run on the board (`python tools/device.py run SCRIPT OUTDIR`); `goto` is simulator only.
- Installing by hand (Arduino IDE): board package 0.2.4 or later, CHGfx 1.3.0 and the CHGame library from `platform/board/arduino/CHGame/libraries/`, *Tools > Optimize > Smallest + LTO* (needed to fit) and *Tools > USB > Upload only*. `python tools/device.py build` does the same as `arduino-cli compile -b CHGame:ch32v:CHGame:opt=oslto,rtlib=nano,periph=game,usb=uploadonly CHCraps`.
- `tools/tests/test_craps.cpp` checks every bet against every point and all 36 rolls with an independent oracle, and works out each bet's house edge exactly by enumerating the dice (pass 1.414%, don't 1.364%, field 2.778%, place 6 1.515%, odds 0). It also runs a long fuzz for money conservation and a chi-square test of the dice.
- Dice3D details: Euler-angle rotation matrices, faces back-face culled, scanline filled, shaded in three levels and outlined. Physics: gravity, felt bounces that turn speed into a tumble, the back wall's kick, side rails, and the two dice pushing off each other. The relabelled die is always a real die (opposites add to 7); of the four ways to do it the game picks the one that changes the fewest pips, and the new pips go on at the back-wall hit, in a shower of sparks.
- The point puck: the black OFF puck turns over and slides to the number's box, where it sits as a round white badge on the box's top right corner, so the box's own number stays clear.
- The board beside the plaque colours the roll history: winners gold, craps wine, a seven-out red, hard numbers marked.

Files:

    CHCraps.ino, config.h   the frame loop and build switches
    src/game/Craps.*        the table: bets, payouts, the point, the dice
    src/cam/                the dice cam: 3D dice and physics, the scene
    src/render/             the wall, the layout and its spots, chips, the bar
    src/fx/                 particles and banners; the presenter
    src/states/Screens.*    title, play, options, stats, the two endings
    src/audio/Sounds.*      the sound effects (the CHGame library plays them)
    src/save/Save.*         what a save holds (the CHGame library keeps it in flash)
    tools/                  tests, assets, the driver and its scripts, device helper
