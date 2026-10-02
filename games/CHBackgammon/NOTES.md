# CHBackgammon — development notes

Agent-facing notes for continuing work on this game. Rules, controls and build steps are in [README.md](README.md); the platform is covered by the repo-root [CLAUDE.md](../../CLAUDE.md) and [docs/](../../docs).

## Snapshot

- Imported from https://github.com/bateske/CHBackgammon at commit 80cf126 (2026-10-01). Develop here now, not in the old repo.
- Release build (`CHGame:ch32v:CHGame:opt=oslto,rtlib=nano,periph=game,usb=uploadonly`, core 0.2.4, CHGfx 1.3.0): flash 49,268 of 50,944 B (1,676 spare), static RAM 16,924 of 18,416 B (1,492 spare).
- Save pages: `python ../../tools/check_size.py build/release` reports the image as 49,524 B. Both A/B save pages (0xF500/0xF600) need the image to stay at or below 50,432 B, so the real margin was about 900 B at import. On the CHGame library's sound engine (2026-10-02) the image is 50,152 B; on its debug protocol, saving and RAMFUNC (below) 50,232 B: 200 B left. The pages are the CHGame library's (`chgame/Save.cpp`). Treat flash as full.
- The debug protocol (`chgame/Debug.h`, `CHGAME_DEBUG`), the flash save record (`chgame/Save.h`; `src/save/Save.cpp` says only what the record holds, byte for byte the old layout) and RAMFUNC are the CHGame library's since 2026-10-02, and `tools/chsim/chdrive.py` is the shared `tools/chsim/chdrivelib.py` plus this game's `goto`, `move`, `auto`, `board`, `waitturn` and `cal`. Image 50,152 -> 50,232 B (the library's `audio::setOn()` out of line, about +18 B; the rest its save code and LTO's inlining), static RAM 16,892 B unchanged; debug image 49,728 -> 49,844 B; frames unchanged.
- Verification as of 2026-10-01: simulator only. `python tools/check.py` passes. It runs the host tests (UBSan, rules against a naive reference, whole matches, the CPU), runs every script twice with identical frames, checks that the network's evaluation is bit-identical in the simulator and on the host, and compiles the release build.
- It has never run on the board. Frame times, CPU thinking time, sound and saving on the hardware are all unmeasured.

## Design decisions

- Chosen: a top-down view with the whole board always visible. A 2x punch-in whip zoom is kept for the big moments only.
- Chosen: the default is a single game without the cube. Match play (MATCH TO 3/5/7) with the doubling cube, Crawford and the game's own match equity table (`tools/train/met.py`) is opt-in on the setup screen.
- Chosen: at the end of a turn the glove goes to the dice. A picks them up and passes the turn; B takes the last move back. Nothing is final until the dice are up.
- Chosen: the game has its own slab-serif display font (`tools/art/font.txt`) for the logo, banners and headings, like Blackjack's title lettering.
  - The logo uses a plain lower-case 'o'.
  - Rejected: a checker as the logo's 'o'.
  - Rejected: a dark red (WINE) drop shadow on display-font lettering.
  - Rejected: marquee chasing bulbs on the title.
- Chosen: the title/BEGIN menus use the 3x5 font at 2x (`text35x2`), as at the other tables, with at least 2 px of padding inside the gold selector.
- Chosen: the cube is odd-sized so its value sits exactly in the centre, with no stray corner pixels.
- Chosen: the rules, the network, its trainer and weights, and the match equity table are this project's own code (Apache-2.0). Keep credits exactly as `NOTICE` has them: Press Play On Tape for the 3x5 font, and nobody else added.

## Open items

- Device run (kit ready, never run; follow "The device" in the root CLAUDE.md).
  - `python tools/device.py run tools/scripts/device_render.txt out/dev_render`: render cost per section (`say Y`) and whole-frame perf.
  - `python tools/device.py run tools/scripts/device_think.txt out/dev_think`: `say W` prints positions weighed, ms and `slice_us`. The longest slice should stay under about 8 ms; tune `QUANTUM` (64 positions a tick) in `src/game/Match.cpp`.
  - Then run `python tools/check.py --compare out/<sim run> out/<device run>`.
  - Simulator estimates (host-time, unreliable): play averages about 5-7 ms and peaks at about 11-13 ms; the title takes about 12 ms.
- Device checks still to do: sound by ear, saving and CONTINUE on hardware, and `say E` on the board, which should match the host network value.
- Choices the owner has not reviewed yet:
  - The glove is drawn turned over (a vertical flip) when it works from below: the top-half points, and the bar/tray on Red's turn (`fromBelow()` in `src/stage/Stage.cpp`). The owner has objected to mirrored art elsewhere because flipped shading reads wrong, so this may need a separate drawing, which costs flash.
  - Red vs ivory chips, points printed on the felt, and a wood frame with a gold inlay.
  - The centred cube shows 64.
  - The 3x5 font is now the CHGame library's (`platform/libraries/CHGame/src/chgame/Draw.cpp`), so its 'M' is PPOT's, as at the other tables. This game's own copy had an 'M' with a lighter middle (one row, not two), because two of PPOT's side by side, as in BACKGAMMON, read as HH at title size.
- Cut earlier to fit flash, and not reviewed by the owner: party rays, the bear-off chip flip, and dice on the title. Re-adding any of them needs a flash cut first.

## Gotchas

- Flash tactics already in use:
  - Every hand-written `.cpp` starts with `#pragma GCC optimize("Os", "no-ipa-sra")`; no-ipa-sra saved about 256 B under LTO. Keep it in new files.
  - Avoid 64-bit division: it pulls in `__divdi3` (about 1.2 KB). See the 32-bit maths in `src/ai/Cube.cpp`.
  - The glove is one `HAND` sprite, turned over with `SPR_FLIP_V` in `sprite4`.
- Size levers measured earlier:
  - `-flto-partition=one` would save about 260 B, but it needs link flags in the board package.
  - The biggest remaining items are features: match/cube about 2 KB, display font + mask about 1.8 KB, tumbling-dice rotation about 0.7 KB.
- Arduino's `binary.h` defines `B0`, `B1`, ... as macros. Don't use those names as identifiers.
- `bg::Board` is `alignas(4)` (the network compares boards a word at a time) and has padding. Compare, hash or copy `.n` only, never the whole struct.
- CPU:
  - It thinks a slice per frame, with no second stack. Its choice must not depend on how the work is sliced, and the tests check this.
  - The incremental evaluation keeps the last hidden sums. That, plus the evaluator and move generator running from SRAM, makes a position about 3x cheaper on the host.
  - Races use a 25-entry table fitted to the exact bear-off database.
- Generated files, don't hand-edit:
  - `src/ai/NetData.cpp` comes from `tools/train/train.py export`, and `tools/train/net.bin` is the network that ships.
  - `src/ai/RaceData.cpp` comes from `train.py race`.
  - `src/ai/MetData.cpp` comes from `tools/train/met.py`.
  - `src/assets/` comes from `tools/assets.py`.
- Saves:
  - `VERSION` 2 in `src/save/Save.cpp`. Bump it on any change to the `Data` layout (the header, whose flag byte says a game is saved, and the CRC are the library's, `chgame/Save.h`).
  - A save holds the position as the turn began, its roll and the dice generator's state, so a reload can never change a roll.
  - The save pages are shared with every other CHGame game; records are told apart by magic "CHBG".
  - CHFour used the same magic value (`0x47424843`, "CHBG") by mistake until 2026-10-01; it is "CHF4" now (../../docs/status.md).
- Device debug builds (`CHGAME_DEBUG` on the board) are `CHBG_LEAN`: no saving, no setup/options screens, no hint or coach, and games start with `say G` (or at once from the title's menu). `-DCHBG_FULL` forces those parts in, but don't expect it to fit.
- Debug protocol (the CHGame library's `chgame/Debug.h`):
  - The letters `? S K L N P B` belong to the protocol, and `T` too in a `CHGAME_PROFILE=1` build.
  - The game's commands are documented above `debugHook()` in `src/states/Screens.cpp`.
  - `A` (play for the human, used by chdrive's `auto`) and `Q` (calibration) are simulator-only. `G C D V X R W Y E H J` also work on the board.
- The simulator's `cal`/`perf` render estimates are host time. Don't trust them for small differences.
- Art: `python tools/assets.py` writes each drawing to `tools/art/gen/` as a PNG. To redraw one, copy it up to `tools/art/` (see README).
  - `tools/art/sides.txt` is the per-side palette swap.
  - `python tools/font_preview.py` draws the display font.
  - `tools/lookdev.py` is a Python mock-up of the board for choosing colours, written to `docs/mockups/` (gitignored). It is not the renderer.
- Shared tools: the simulator is `../../tools/chsim/chsim.py` (game-side driver: `tools/chsim/chdrive.py`). Set `CHSIM_CXX` or have zig/clang++/g++ on PATH (see root CLAUDE.md).
