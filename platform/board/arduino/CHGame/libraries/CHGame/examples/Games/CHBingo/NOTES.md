# CHBingo — development notes

Agent-facing notes for continuing work on this game. Rules and controls are in [README.md](README.md), whose format is [docs/game-readme.md](../../../../../../../../../docs/game-readme.md); the platform is covered by the repo-root [CLAUDE.md](../../../../../../../../../CLAUDE.md) and [docs/](../../../../../../../../../docs).

## Snapshot

- Imported from https://github.com/bateske/CHBingo at commit dd6295b (2026-10-01). The public history was squashed to that single commit. Develop here now, not in the old repo.
- Release build (`CHGame:ch32v:rev0:opt=oslto,rtlib=nano,periph=game,usb=uploadonly`, board package 0.3.0, 2026-10-21): flash 40,383 of 50,944 B, static RAM 14,824 of 18,416 B (3,592 spare).
- Save pages: the repository's `tools/check_size.py` reports the image as 40,740 B, so both A/B save pages fit with about 9.5 KB to spare. This game has real flash room.
- Verification as of 2026-10-01: simulator only. These all passed:
  - `chgame test`: rules, races against the hall, money, power-ups, jackpot odds, round set-up against `tools/tests/ref_bingo.py`; about 1.24M checks.
  - `tools/tests/sim_save.py`: save mid-round, power-cycle, continue.
  - `chgame redraw` on `tools/scripts/diff/diff_soak.txt`: 0 stale pixels.
- `chgame check` runs the host tests, every script twice, the redraw check, the save test and the device build.
- It has never run on the board. Render times, pacing, sound and saving on hardware are unmeasured.

## Design decisions

Made by the owner:
- The dealer (CHBlackjack's PPOT dealer) announces every ball in his speech bubble.
- The win banner is a rainbow "BINGO!". Rarely it says "IT'S A BINGO!" instead, and the dealer's bubble corrects it: "You just say bingo....".
- Up to 9 cards, each bought separately. Every card needs its own daub: move to it and press A.
- One card is visible at a time, so play is swiping. A card holding a called, undaubed number gets a rainbow outline.
- Chosen (2026-10-21), because with A daubing the whole card play is swiping left and right: the card in play sits in the middle of the felt, the POWER tube (and the B button that spends it) on its left, the jackpot's stack of gold on its right. The bar is a centred row of every card in little (`cards::bar()`): its frame, header and 5x5 cells, daubs in the dauber's colour, waiting numbers and the winning line in the rainbow; cells 3x2 up to seven cards, 2x2 for eight or nine. The one in play stands 2 px higher, and the glove hovers over it whenever nothing waits on the card in play. This replaced the pips and the peek at the next card's first three columns. Neighbours wait off the screen (`CARD_PITCH` 104) and slide past over the side panels on a swipe.
- The player races a hall of rivals; the twists are power-ups and a progressive jackpot.
- Asked for (2026-10-21): three modes, picked when a game starts (the caller asks "EASY OR HARD?" over a picker on the felt; `Phase::Mode`). EASY is the game as it was. HARD has no rainbow frames or waiting cells, no glove on the waiting number and no power meter: A picks the card in play up and a cursor starts on its centre, the d-pad moves it, A daubs that one cell, B puts the card down. HARDCORE is HARD, but daubing a number not yet called voids the card (stamped VOID, it drops off the table and its little copy is crossed out); with none left the round is lost ("BUSTED!"). The hard modes pay more.
  - Implementer's defaults, not yet confirmed: the pot pays x2 (HARD) and x3 (HARDCORE), the jackpot is the same in every mode; the cursor stops at the card's edges; A on a cell already daubed (the free centre included) only buzzes, even in HARDCORE; in HARD a wrong cell is a miss (it ends the streak); the LED blink on a call that is on your cards is EASY only; the mode lasts the whole game and the picker offers EASY first.
- Asked for (2026-10-21): more depth on the power meter (a glass tube in brass caps, segments shaded blue to cyan to white, a glint, a scale, a raised B button) and a better jackpot (`jackpotPile()`: a sign, then coins at an angle in two stacks, a short one and a loose one, nine at the seed and one more for every $5, up to thirty).
- Depth everywhere: shaded panels, cards, daubs and the little cards, plus drop shadows.
  - Panels are layers of one rounded shape: the shadow follows the corners, the outline is one colour and the rims follow the curve (`panelLit()` in the CHGame library, `platform/board/arduino/CHGame/libraries/CHGame/src/chgame/Draw.cpp`).
  - The owner dislikes jagged edges and shadows that ignore the contour.
  - Ball shadows are a single shrinking line.
- Title:
  - The title is the cover's BINGO, its bouncing letters (2026-10-06): `tools/cart.py` `title_lines()` gives its lettering as the cover places it, `tools/titleart.py` packs it, the library's `titleArt()` draws it in the house gold as a smooth dithered gradient, with no bevel or glints (docs/cover-art.md, "The same title on the title screen"). "75 BALL CLASSIC" sits at y 40 and the balls' band starts at y 46 to make room. The earlier "Bingo" (`tools/art/logo.txt`, CHBlackjack-style) is no longer read.
  - Rejected: chips on the title, and a spotlight at the top.
  - The menu sits on a FELT_DK dither band at a pitch of 12.
  - The menu glove is CHChess's glove pointing right (`HAND_R`), thumb on top, cuffed in the dauber colour.
- Title balls (the owner loves them; tuned over four rounds, see `titleBalls()` in `Screens.cpp`):
  - A continuous stream spelling BINGO travels right to left with B leading. "Left to right" was a slip in the owner's earlier request.
  - All balls are the same size and bounce at one rate and height (`BOUNCE` 48 ticks), each a beat behind the ball ahead.
  - Each ball has its own slow ±3 px swing, which can never make one overtake another (`PITCH` 27).
- The DAUBER option (red/blue/green/cyan/peach) colours the daubs, their splat and the glove's cuff.
- A daub is CHChess's DUST puff, plus GOO "gack" particles (a Nickelodeon feel), plus a small shake.
- After a daub the glove holds on the cell with a press-and-kick `RECOIL` curve (22 ticks, `Presenter.cpp`), then slides on. A swipe cancels the hold.
- Chosen (2026-10-07): the owner's new dealer and faces (`tools/art/common/dealer.png`, `faces.png`), and behind him a spotlight of 25% white dots centred on his head (the library's `spotlight()`), where the wood rectangle was.

## Open items

- Device run: render profile, pacing, sound by ear, saving.
- Owner feedback on the overall look and feel.
- Defaults the implementer chose, not yet confirmed by the owner:
  - A daubs every waiting number on the card in play. Completing a line is the call. A press with nothing waiting resets the streak.
  - The hall has 8/20/40 rival cards. The pot is 90% of the hall's buy-in. A tie goes to the player.
  - A call every 2 s (1.3 s on FAST, 3 s on SLOW).
  - The rare banner comes 1 win in 10 (`RARE_ONE_IN`). The jackpot pays within 10 calls (`JACKPOT_CALLS`).
  - The power-ups are WILD, FREEZE and 2X POT.
  - The caller has nicknames for 13 numbers (`LINGO` in `Presenter.cpp`).
  - No music, and no win screen: play is endless until broke.

## Gotchas

- The skeleton was forked from CHRoulette (wheel, glove and music removed): macro prefix `CHBN_`, save magic "CHBN", and the protocol handshake is `CHBN`.
- The mode is saved with the game in what was the record's padding (`Data.mode`; 0 is EASY, so older saves load as EASY and `VERSION` stayed 1). A card thrown out in HARDCORE is bit 31 of its `RoundSave.daub`.
- A saved round is just its seed plus the daubs; the draw, the cards and the hall are dealt again from the seed. Any change to dealing order or random-number use breaks saved rounds, so bump `VERSION` in `Save.cpp`. The save pages are shared with every other CHGame game.
- The hall costs no RAM: each rival card is reduced to the call on which it completes, and only the earliest call is kept.
- Redraws are incremental, by band (wall, plaque, felt, bar).
  - `-DCHSIM_FORCE_FULL` (`Presenter.cpp`; `chgame redraw` sets it) forces full redraws.
  - After touching render or presenter code, run `chgame redraw tools/scripts/diff/diff_soak.txt out/diff`.
  - The title draws its felt and logo once (`titleReady`) and redraws only the ball band and the menu.
- Rainbow outlines, the little cards and the winning line all use one cycling palette entry. Animate through the palette, not with redraws.
- Debug protocol:
  - The game's commands are listed at the top of `CHBingo.ino`; `Q` (calibration) is simulator-only. A game command cannot use one of the protocol's own letters (`? S ! K L N P T Q B`): they never reach the hook. `O` sets the mode, `U` makes the next call land on a cell of the card in play.
  - Device debug builds do not write the save pages unless a script sends `say E 1`, because the pages are shared with the release and other games.
  - `CHBN_LEAN` (device debug) drops only the broke screen's lettering; saving stays in.
  - The protocol itself is the CHGame library's (`chgame/Debug.h`, on with `CHGAME_DEBUG`); the save record's pages and CRC are the library's too (`chgame/Save.cpp`), the game's `Save.*` says what goes in it.
- `python tools/chsim/autoplay.py out/autoplay.gif` is a buttons-only bot: it plays a round as a person would (reaction times, swiping toward the rainbow frames, power-ups in the quiet moments), searches for a seed the player wins, then records that seed. It made the README's GIF before the README had one reel of clips; that is `tools/scripts/gameplay.txt` now.
- Sound is the CHGame library's sequencer (`chgame/Audio.h`); the game's effect tables are `Sounds.*`. There is no music. Adding some costs flash (the library links its music code only for a game that calls `audio::music()`), but there is room: give the game generated scores and a `playSong()` in `Sounds.*`, which the shared preview (`chgame audio out/audio`) uses to render them. The SOUND option already asks for the lead rendering.
- `src/assets/Assets.cpp` is generated by `python tools/assets.py` from `tools/art/` (the logo) and the repository's shared `tools/art/common/` (dealer, faces, hand, broke lettering). Don't hand-edit it.
- Shared tools: the simulator is the repository's `tools/chsim/chsim.py` (game-side driver: `tools/chsim/chdrive.py`). Set `CHSIM_CXX` or have zig/clang++/g++ on PATH (see root CLAUDE.md).

## Development

Everything can be checked on a PC (Python 3 with `pip install -e .[sim]` in the repository root, and a C++ compiler for the simulator and tests: root CLAUDE.md).

    chgame test     # the rules (below)
    python tools/tests/sim_save.py      # in the simulator: save mid-round, power off and on, continue; options; going broke
    chgame sim
    chgame run tools/scripts/smoke.txt out/smoke
    chgame redraw tools/scripts/diff/diff_soak.txt out/diff   # incremental redraw against a full redraw, frame by frame
    chgame gif    # tools/scripts/gameplay.txt -> docs/gameplay.gif (the README's one GIF, <= 1 MB)
    python tools/assets.py              # art in tools/art and tools/art/common -> src/assets/Assets.*
    chgame audio out/audio    # the sound effects as WAVs
    chgame build [--debug]                            # also upload, run --device SCRIPT OUTDIR, shot OUT.png
    chgame size     # flash and RAM from the map

- `chgame test` covers the modes (the picker, the pot, the cursor, B, voids, a save with a void), the lines, the cards, the race against the hall over thousands of rounds (a player who daubs everything wins exactly when one of their cards is first or level), the money, the power-ups, the buttons, saving a round, the jackpot's odds, and the round set-up against an independent Python model.
- Scripts (`tools/scripts`): `smoke.txt` is every screen and a round as screenshots, `perf.txt` estimates render times, `showcase.txt` records the buy-in, swiping, both banners and a rival's win as separate GIFs (a test now, written to its output folder, not `docs/`), `gameplay.txt` records the README's clips (`01_title` ... `06_rival`), `modes.txt` the mode picker, HARD (pick up, cursor, daub, miss, put down) and HARDCORE (two voids and the bust). `say R 21` seeds the round, `say J P` jumps to the buy-in, `say H n` sets the call a rival wins on, `say W` makes a bingo, `say I 1` forces the rare banner; the full list is at the top of `CHBingo.ino`. The same scripts run on the device with a debug build.
- The device build wants *Optimize: Smallest + LTO* and *USB: Upload only* (the game has no use for USB Serial); `chgame build` sets both.
- Render times estimated from the simulator: a slide across the cards about 7 ms a frame, a daub with its splat about 8 ms, the title about 5 ms. None measured on the board.
- Saving: the two flash pages below the bootloader's metadata survive re-uploads; records alternate between them with a sequence number and a CRC.

Files:

    CHBingo.ino          the frame loop and the debug commands
    config.h             build switches
    Bingo.*              the rules (the modes too): no graphics, no sound, host-tested
    Presenter.*          events to motion: the caller, the carousel, the wins
    Fx.*                 the library's chgame/Sizzle configured (64 particles, GOO) plus gack()
    Table.*, Cards.*     the wall; the cards, the power (or mode) and jackpot sides, the mode picker, the buy-in and the bar
    Layout.h             every coordinate of the play screen
    Screens.*            title, play, pause, options, stats, broke
    Sounds.*             the sound effects (the CHGame library's sequencer plays them)
    Save.*               what a save holds (the CHGame library keeps it in flash)
    src/assets/          generated art (tools/assets.py)
    tools/               simulator, tests, scripts and art tools
