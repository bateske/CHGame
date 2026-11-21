# Hardware steps

Everything that could be checked without a board was done on the PC
(`test/native`, see [README.md](README.md)). These steps put the bootloader
on a real CHGame. They need a person to press buttons and switch the power,
and a computer with the board on USB: a local Claude Code session (Claude
Desktop, or `claude remote-control` in this repository) can run the commands.

There are two routes:
- **The direct route** goes straight to the menu bootloader, then runs the
  HW3 checklist. It is quicker, but a failure at first boot could come from
  the card driver, the panel code or the new upload path.
- **The staged route** gives each change its own step:
  - **HW1** tries the card, panel and menu code as an ordinary program, under
    the bootloader already on the board.
  - **HW2a** changes the bootloader without the menu.
  - **HW2b** adds the menu.

Every step can be rolled back over USB, and the factory ISP is the last
resort ([recovery.md](../board/docs/recovery.md)).

**Which board.** Everything after "Rev1" below was written for CHGame
Rev0. The tools build for the newest board, Rev1, unless told
otherwise, so for a Rev0 set `CHGAME_BOARD=rev0` (or run `chgame --board
rev0 ...`), and use the images in [release/](release), never those in
[release/rev1/](release/rev1). A Rev1 or a Rev 1.5 starts at "Rev1" and
uses only `release/rev1/`. One board's bootloader or sketch on the other
drives pins that are buttons there, and a press then shorts a driven
output.

## Rev1 (and Rev 1.5): bring-up and provisioning

A new Rev1 has no bootloader. It gets the USB-only one through the factory
ISP, a bench sketch checks the board, and then the SD menu goes on over USB
as on Rev0. A Rev 1.5 is a Rev1 here: the same pins, and with this
firmware its power parts (the CH211, the INA226, the host boost) stay as
they power up. `UP` is the uploader ("Before starting", below). The core
must have Rev1 (board package 0.4.0, or a staged `0.4.0-local`:
[trying-a-release.md](../board/docs/trying-a-release.md)). Keep Rev0
boards off the bench, and label each board with its edition.

1. **Preflight**, at the first power-on, with BOOT held (the factory ISP
   runs; every GPIO is still as reset leaves it), on a USB meter or a
   current-limited supply:
   - the idle current, and the 3V3 and `VSYS_SW` rails;
   - the buzzer silent and R27 cold;
   - the backlight dark;
   - `wchisp info`: record the chip (`CH32X035G8U6`), its UID, BTVER, RDPR,
     WRP and RST_MOD. **No option byte is changed.**
   - Optional, powered off: PA1 and PB9 about 100 kΩ to GND, PB3 about
     10 kΩ to 3V3, PA0 about 1 kΩ to GND.
2. **Provision the USB-only bootloader**, still in ISP mode:
   ```
   UP provision --device rev1 --bootloader platform/bootloader/release/rev1/chgame_boot_nomenu.bin
   ```
   It refuses an image that is not rev1's, and refuses while wchisp sees
   more than one chip in ISP mode; it prints the chip, its UID and the
   image's board, and asks before erasing (`--yes` does not ask). The same
   from the board package: `chgame-upload provision -device rev1
   -bootloader <package>/bootloaders/CHGame/rev1/chgame_boot_nomenu.bin`
   ([recovery.md](../board/docs/recovery.md)).
   Then **switch off and on** without BOOT: the reset that ends
   provisioning is a soft one. Check:
   - the screen stays dark (USB Only never touches the panel or its
     backlight) and the LED (PB10) blinks: USB mode, no program;
   - `UP probe` lists the board in its bootloader, board `rev1 (CGR1)`,
     and `UP info` reports bootloader v4 (v3 before 2026-11-20).
3. **The bench sketch**, `tools/sketches/CHBoardTest` (its README describes
   each check):
   ```
   chgame --sketch CHBoardTest upload
   ```
   - all eight buttons, each alone;
   - the LED;
   - the backlight comes on only over a black screen, at a cold start and
     after each upload;
   - SWEEP, then silence with nothing warm (R27, the buzzer); SOAK for the
     power checks of step 7;
   - the SD card (a FAT32 card);
   - VBUS about 5 V on USB;
   - CN3 with a wire from TX to RX, and CN2's two lines idle high;
   - TP14/15 (Rev 1 only, armed with SELECT): FREE and FREE, unplugged and
     with the USB-C cable either way round;
   - the deliberate fault, with a tone sounding: the sound stops (PA1 at
     0 V) and the LED stays lit.
4. **The SD menu.** Make Rev1's card: `chgame card` writes it to
   `out/sdcard-rev1/` (Rev0's beside it, in `out/sdcard-rev0/`). Copy the
   folder's contents to the root of a FAT32 card, with a PC's reader or the
   board itself (`chgame --sketch CHSDtoUSB upload` builds the reader for
   Rev1). Then install the text menu over USB:
   ```
   UP selfupdate platform/bootloader/release/rev1/chgame_sdboot.bin --device rev1 --yes
   ```
   `UP info` reports bootloader v4 (v3 before 2026-11-20), board `CGR1`. Switch off and on with
   the card in: the menu, the backlight coming on with its first picture.
   - **B held at power-on:** USB mode, the screen dark (the backlight stays
     off) and the LED blinking on PB10.
   - **The games:** install each of the 20 and the apps from the menu;
     play, save and restore; hold START 3 s to come back. CHWords,
     CHWordWheel and CHCrossword find their files; CHStlView reads an STL;
     the SD card reader works.
   - Then the points of "Menu v2", step 4, and HW3 that apply.
5. **Refusals**, with the text menu:
   - Rev0's card (`out/sdcard-rev0/`): its games are grey and A says
     ERROR 5; nothing is erased.
   - `chgame --board rev0 upload` of a game: refused, the installed program
     unchanged.
   - `UP selfupdate platform/bootloader/release/chgame_sdboot.bin --yes`
     (Rev0's): refused.
   - In a Rev0, Rev1's card: grey, ERROR 5, the installed game intact.

   Then the graphic menu (`release/rev1/chgame_sdvisual.bin`, as above): a
   Rev0 game shows the ERROR 5 picture. Once each from the IDE, board
   CHGame Rev1: *Burn Bootloader* and *Upload Using Programmer* with
   **CHGame USB**.
6. **Debug runs:** `chgame run --device` with a few games' scripts (say so
   first: CLAUDE.md, "The device"), then CHSDtest's `MIX` with `SET
   PATTERN 1` on one of the 128 MB gift cards, which the DI gate should now
   let pass.
7. **Power:** 10 minutes of CHBoardTest's SOAK on USB while charging,
   measuring the current and the temperatures of R27, the buzzer and the
   regulator; a sweep of the buzzer's range, written down; play on the
   battery alone; USB plugged and unplugged during play; a run down to a
   low battery.
8. **Rev 1.5**, with the same firmware: the checks of steps 3 and 4; CN1
   at 0 V throughout; no host power on the USB port on battery; charging
   from 5 V works.
9. **Afterwards.** Put a release build of a game back, and leave the
   bootloader the owner wants. Write `test/hil/RESULTS-<date>.md` with the
   measured numbers, `wchisp info` and each check.

## Menu v2 (BOOT_VERSION 3)

The steps below were written for the first menu, and they still describe
how to install a bootloader. Menu v2 (README.md, "Menu v2") ran on a board
on 2026-10-03 ([test/hil/RESULTS-2026-10-03.md](test/hil/RESULTS-2026-10-03.md):
steps 1, 3 and the first points of step 4, in both styles). These steps
install it on a board that has the first menu bootloader (or any bootloader
with self-update); `release/chgame_sdboot.bin` and `chgame_sdboot_static.bin`
are the images to install, and `build/release/` gives the same bytes.
(They were rebuilt later on 2026-10-03, when the White style became Static:
the images that ran that day differ in two bytes, the built-in palette's
colour 15.)

1. **The card.** The first menu does not show folders, and the casino card
   keeps SD CARD READER in its APPS folder. So upload the reader directly:
   - `chgame --sketch CHSDtoUSB upload` (its own options, `tools/game.py`);
   - a drive appears;
   - `chgame card`, then
     `chgame cart deploy out/CHGame-Casino.chgame --card <drive> --clean`;
   - eject.
2. **Dry run (optional, the bootloader untouched).**
   - Build with `./build.sh app`, then upload with
     `UP flash platform/bootloader/build/app/chgame_boot.bin --run --port <PORT>`.
   - The menu appears as a program. SELECT leaves to the installed
     bootloader's USB mode.
   - Check the points of step 4 that do not need a reset. A on a game says
     DRY RUN OK and writes nothing.
3. **Install it.** Build with `./build.sh release`, then run
   `UP selfupdate platform/bootloader/build/release/chgame_boot.bin --yes`.
   `UP info` should report bootloader v4 (v3 before 2026-11-20).
4. **What to check and report:**
   - **The look.** It should match [docs/menu.png](docs/menu.png):
     - the CHGAME logo, crisp, its colours turning, with the rule under it;
     - A:PLAY B:BACK at the foot;
     - the selection bar turning too.

     Report any tearing or flicker.
   - **Speed.** How scrolling feels: UP/DOWN once, and held (it repeats every
     80 ms). Each move reads the background from the card and sends the
     whole screen, about 70 ms. Is that slow?
   - **Folders.** APPS (the last row, with `>`): A opens it, B goes back to
     the APPS row. From APPS, STL VIEWER installs and starts.
   - **The games.** Install one at the top level. Hold START 3 s in it: the
     menu comes back with it marked.
   - **USB.** `chgame upload` in a game folder while the menu is up: the
     sketch starts. At the next power-on it is INSTALLED PROGRAM, the top
     row.
   - **Errors.** Copy a CHG file cut short to `GAMES/` (through the reader).
     Its row is grey, under its file name, and A says ERROR 5.
   - **Launch.**
     - Run `chgame cart launch out/CHGame-Casino.chgame chfour`, deploy
       again, then switch off and on: FOUR IN A ROW starts with no menu,
       after an install if it was not the installed game.
     - Hold START while switching on: the menu.
     - Hold START 3 s in the game: the menu, not the game again.
     - Undo with `chgame cart launch ... none` and deploy.
   - **A picture of your own.** `chgame background --template m.png`, paint
     on it, `chgame background m.png --card <drive>`: the menu shows it, and
     it looks like `--preview`.
   - **The Static style.** `./build.sh release --style=static`, then
     `UP selfupdate platform/bootloader/build/release-static/chgame_boot.bin --yes`:
     the bar, the boxes and the logo are magenta, as painted, and still;
     everything else as before. Back to the rainbow the same way with `build/release/`.
   - **B at power-on** still gives USB mode.
   - **The uploaders.** `UP flash <some .bin> -verify` ends with
     "readback: not available".
5. **Afterwards.** Record the run as for the first menu (below), then run
   `tools/dist.sh` to put menu v2 in `release/` and the board package, and
   commit.

## The visual menu (`--ui=visual`)

Not yet run on a board. It installs as menu v2 does (above), and switching
between the two menus is a self-update either way: the card and the
installed game stay. `UP` is the uploader as above (`chgame uploader` or
`chgame-upload`).

1. **The card.** As for menu v2, step 1, with the cart rebuilt by this
   branch's `chgame card`: the games in genre folders, each with its
   picture, and `COVER.PIC` and `SYSTEM.PIC` in `GAMES/`.
2. **Dry run (optional, the bootloader untouched).** `./build.sh app
   --ui=visual`, then `UP flash platform/bootloader/build/app-visual/chgame_boot.bin
   --run --port <PORT>` (or `release/chgame_visual_dryrun.bin`). The menu
   appears as a program: check the points of step 4 that need no install. A
   on a game shows the check mark and writes nothing; START leaves.
3. **Install it.** `./build.sh release --ui=visual`, then
   `UP selfupdate platform/bootloader/build/release-visual/chgame_boot.bin --yes`
   (or `release/chgame_sdvisual.bin`). `UP info` reports bootloader v4 (v3
   before 2026-11-20).
4. **What to check and report:**
   - **Power-on.** The cover fades in (CHGAME CASINO) and stays, whatever
     is installed (until 2026-10-06 the installed game's picture followed
     by itself). A on it: the installed game's picture with a one-pixel
     border round it (rainbow; Static: white); A again plays it, B comes
     back to the cover.
   - **The look.** Every picture as in
     [docs/visual_cards.png](docs/visual_cards.png): colours, no tearing.
     The CHGAME logo on the cover turns through the rainbow.
   - **Speed and feel.** UP/DOWN once and held: each picture slides in
     (eight steps, the panel's own pace). LEFT/RIGHT: the next folder's
     cover slides in from that side. A into a folder and B out of it fade
     through black. Too slow, too fast, jerky?
   - **The ring.** LEFT/RIGHT from the cover go through CARDS ... APPS and
     back round. In a folder, DOWN goes through its games and back to its
     cover.
   - **Install.** A on a game: the bar over its picture fills, the screen
     fades and the game starts. Hold START 3 s: back to the menu, on that
     game, with the border.
   - **The keys.** B from a game at the root or in a genre folder: the cart's
     cover; B there: the about page (any key closes it). SELECT from inside a
     folder: the cart's cover; SELECT there: the about page. START: nothing.
     A on the cart's cover: the installed game's picture; A plays it, B goes
     back to the cover, other keys do nothing.
   - **USB.** `chgame upload` with the menu up: the USB plug screen, then the
     sketch runs. At the next power-on the cover; A on it (or DOWN) shows
     the INSTALLED picture with the border; A runs it.
   - **Launch.** `chgame cart launch out/CHGame-Casino.chgame chfour`,
     deploy, switch off and on: if FOUR IN A ROW is the installed game it
     starts at once with the panel dark; otherwise the cover, then its
     picture without a border, and nothing more until A installs it.
     Undo with `chgame cart launch ... none` and deploy.
   - **No folders.** On a card whose `GAMES/` holds only games, LEFT and
     RIGHT do nothing.
   - **Errors.** A CHG file cut short in `GAMES/APPS/` (through the reader):
     its picture is ERROR 5, and A shows it too.
   - **Launch.** `chgame cart launch out/CHGame-Casino.chgame chfour`,
     deploy, power-cycle: the cover, then FOUR IN A ROW's picture, then the
     game (an install first if need be). START held at power-on: the menu.
   - **The Static style.** As for menu v2, with `--ui=visual --style=static`:
     the logo and the bar magenta and still.
   - **A card without pictures** (an older card, or `GAMES/` copied by hand):
     the built-in screens: a folder icon for the cover, a cartridge for each
     game. Nothing worse.
5. **Afterwards.** Record the run in `test/hil/`, then put back whichever
   menu the owner wants (`UP selfupdate release/chgame_sdboot.bin --yes`
   for the list menu).

## Before starting

- **Software.** This branch checked out. Python 3 with `pip install -r
  tools/requirements.txt`. arduino-cli with `CHGame:ch32v`
  (CLAUDE.md, Setup; these steps were run with 0.2.4, and a Rev1 needs
  0.4.0 or a staged `0.4.0-local`).
- **Commands.** Run from the repository root. `UP` is `chgame uploader`
  (the Python uploader, `platform/bootloader/host/py`; `python -m
  chgame_upload` from that folder is the same). `chgame-upload` is the board
  package's Go tool; both have the same verbs and flags.
- **Another session using the board.** Check that nothing else is using it
  (CLAUDE.md, "The device"). `UP probe` lists the board's port and what it
  is running.
- **Rollback image** (Rev0 only). Keep `platform/bootloader/release/0.2.4/chgame_bootloader.bin`
  (the 0.2.4 bootloader) at hand. It is Rev0's: never put it on a Rev1.
- **What gets flashed.** The binaries are in [release/](release) (Rev1's in
  [release/rev1/](release/rev1)), with SHA-256 sums. `tools/dist.sh`
  rebuilds them byte-identical.
- **Card contents.** `chgame card` builds the casino cart
  (`out/CHGame-Casino.chgame`: the 20 games, the STL viewer and the SD card
  reader, for both boards) and a card for each board, `out/sdcard-rev0/`
  and `out/sdcard-rev1/` (`out/sdcard/` until 2026-11-17). For the routes
  below, Rev0's. (For the first menu, which shows
  no folders, the two apps in APPS stay out of reach: copy their CHG files
  up into `GAMES/` by hand if you need them there.)

## The direct route

About an hour and a half, including the card build. Do "Before starting"
above first, and these as well:
- **The factory ISP is the safety net**, because this route skips the dry
  run.
  - Check that the BOOT button can be reached.
  - Check that `wchisp probe` sees the chip in ISP mode. On Windows it needs
    the WinUSB driver; see [recovery.md](../board/docs/recovery.md).
  - Switch off and on without BOOT to leave ISP mode.
- **Check the image** against [release/SHA256SUMS](release/SHA256SUMS). In
  Git Bash: `cd platform/bootloader/release && sha256sum -c SHA256SUMS`.

**D1. Build and load the card**, while the board still has its old
bootloader.
1. Run `chgame --board rev0 card`. It builds all 21 sketches into
   `out/sdcard-rev0/`, which takes 20-30 minutes.
2. Copy everything in `out/sdcard-rev0/` to the root of a FAT32 microSD card (32 GB
   or less). Use either:
   - a PC card reader;
   - the board itself as a card reader: HW1 step 1 (CHSDtoUSB).
3. `python tools/chgpack.py info <drive>` must list 21 packages, all "ok".
4. Eject the card, and put it in the CHGame if it is not there already.

**D2. Install the menu bootloader.** The uploader touches the port itself,
from whatever is running.
```
UP selfupdate platform/bootloader/release/chgame_sdboot.bin --yes
UP info                                  # BOOT_VERSION 2
```

**D3. The first boot.**
- The board resets into the new bootloader. Switch off and on once as well.
- The rainbow menu should appear in under half a second:
  - a black list with a dark grey header and footer;
  - 21 titles A-Z, BACKGAMMON first;
  - "1/21" in the footer.
- No game is installed yet, because the staging erased the sketch.
- A on BACKGAMMON: "INSTALLING", a progress bar, then the game starts.

**If D3 goes wrong**, try these in order:
1. **No picture, or a garbled one.**
   - Hold B while switching on. The bootloader skips the card and the panel
     and waits in USB mode (the LED blinks at 2 Hz; on Rev0 the backlight
     is lit whenever the board is on).
   - Check that `UP probe` answers.
   - Note exactly what the screen did.
   - To go back (Rev0 only): `UP selfupdate platform/bootloader/release/0.2.4/chgame_bootloader.bin --yes`.
2. **"NO GAMES FOUND" or "CAN'T INSTALL / CARD READ ERROR"** with a card
   that reads fine on the PC: this is the SD clock or the card driver.
   - Run the dry run, which works under any bootloader:
     `UP flash platform/bootloader/release/chgame_menu_dryrun.bin --run`.
   - Then follow HW1 step 3 and note which SD speeds work.
   - SELECT leaves it, to the "USB UPLOAD" screen.
3. **No USB at all, even with B held** (Rev0 only; a Rev1 takes a rev1
   image, as in "Rev1", step 2).
   - Hold BOOT across power-on.
   - Run `UP provision --device rev0 --bootloader platform/bootloader/release/0.2.4/chgame_bootloader.bin`,
     or `wchisp flash` the same image.

**D4. The HW3 checklist**, in this order (fewest power cycles):
1. Menu and install.
2. Leaving a game.
3. USB and uploads.
4. Cards.
5. Damaged packages.
6. Fragmentation.
7. Power cuts.
8. The boot region and the HIL tests: `tools/bootcheck.py`,
   `test/hil/test_protocol.py` and `test_powercut.py`. These stand in for
   the HW2a checks this route skips. `test_protocol.py` erases the installed
   game; reinstall one from the menu afterwards.

**D5. HW4**, the final state.

**The results.**
- Write `platform/bootloader/test/hil/RESULTS-<date>.md`:
  - every HW3 line as pass, fail or a note;
  - the install time of a few games;
  - the SD speeds tried and which worked;
  - the `wchisp info` chip marking, if it was read;
  - anything odd, with what the screen showed.
- Commit it and push it to the branch.
- Change no code during the run. Fixes are made against the PC models in
  `test/native` first, then tried on the board again.

## HW1: the menu as a program (the bootloader is not touched)

1. **Load the card.**
   ```
   cd platform/board/arduino/CHGame/libraries/CHGame/examples/Apps/CHSDtoUSB
   arduino-cli compile -b CHGame:ch32v:rev0 --library ../../platform/board/arduino/CHGame/libraries/CHGfx .
   arduino-cli upload  -b CHGame:ch32v:rev0 -p <PORT> .
   ```
   - A drive appears (vendor "CHGame"). Copy everything in `out/sdcard-rev0/`
     to its root, then eject it.
   - The card must be FAT32 or FAT16. `python tools/chgpack.py info <drive>`
     should list 21 packages, all "ok".
2. **Upload the dry-run menu.** The board enumerates on a new port after
   CHSDtoUSB.
   ```
   UP flash platform/bootloader/release/chgame_menu_dryrun.bin --run --port <PORT>
   ```
   This build has no USB, so the port disappears, which is expected.
3. **What to check and report:**
   - **The panel.** The menu appears:
     - a black list with a dark grey header and footer;
     - 21 titles sorted A-Z, with BACKGAMMON first;
     - "1/21" in the footer.

     The title, the selection bar and "A:PLAY" run slowly through the
     colours, as in [docs/menu_rainbow.gif](docs/menu_rainbow.gif). Report
     any flicker or tearing. The colour order (red and blue swapped or not)
     is checked in HW3.
   - **Keys.** UP/DOWN move and repeat when held; LEFT/RIGHT page by 10.
   - **The card.** A on a few games shows "DRY RUN OK" and "x.x MS PER
     BLOCK" after a moment, without installing anything. Note the
     milliseconds.
   - **The SD clock.** START cycles "SD 24 MHZ", "SD 12 MHZ" and "SD 6 MHZ".
     Try A at each speed and note any failure ("CARD READ ERROR"). The menu
     uses 12 MHz unless this says otherwise.
   - **A second card**, if one is at hand: one formatted on another
     computer, or FAT16.
4. **Leave.** Press SELECT. The board resets into the 0.2.4 bootloader's USB
   mode: the LED blinks and the port is back.

## HW2a: the USB-only bootloader (`nomenu`, Tools > Bootloader: USB Only)

This changes the proven USB upload path: page writes now go through the
shared update code, there is no second erase, and RUN resets instead of
jumping. It changes nothing else. It is also the bootloader for a board
built without an SD card: it never touches the card's, the panel's or the
keys' pins (only the LED and USB), so those pins are free for other
circuits. Without a menu there is no B escape: USB mode is entered by the
1200-baud touch, or when no valid program is installed.

1. **Install it** (from HW1's USB mode, or from any game: the uploader
   touches the port itself).
   ```
   UP selfupdate platform/bootloader/release/chgame_boot_nomenu.bin --yes
   ```
   - The board resets into the new bootloader. The staging erased the
     sketch, so it waits in USB mode.
   - `UP info` reports `BOOT_VERSION 2`.
2. **The HIL suite.** `test_protocol.py` destroys the installed sketch.
   ```
   python platform/bootloader/test/hil/test_protocol.py --port <PORT>
   python platform/bootloader/test/hil/test_powercut.py arm --at 50    # switch off when told
   python platform/bootloader/test/hil/test_powercut.py verify         # after switching on
   ```
3. **A normal upload.** `cd platform/board/arduino/CHGame/libraries/CHGame/examples/Games/CHFour && chgame upload`.
   The game runs. Switch off and on: it runs again.

## HW2b: the menu bootloader

1. **Install it**, from a running game.
   ```
   UP selfupdate platform/bootloader/release/chgame_sdboot.bin --yes
   ```
2. **Switch off and on with the card in.** The menu appears in under half a
   second. No game is installed, because the staging erased it.
3. **Record the MCU marking** (spec section 3).
   - Hold BOOT, switch on, run `wchisp info`. The expected chip is
     `CH32X035G8U6`.
   - Switch off and on without BOOT to leave the factory ISP.

## HW3: the matrix

Tick each line and note anything odd. Each line is one action and its
expected result.

**Menu and install**
- [ ] Power-on with the card shows the menu, nothing preselected beyond the
      first title.
- [ ] A on BACKGAMMON: "INSTALLING", a progress bar, about 1-2 s, then the
      game starts. Time it.
- [ ] Switch off and on: the menu shows BACKGAMMON selected, with a red mark
      at its left. If the mark is blue, red and blue are swapped: report it.
      A starts it at once, with no bar.
- [ ] Install each of the other 19 games and the SD card reader once; each
      one starts and plays.
- [ ] CHWords, CHWordWheel and CHCrossword find their card data
      (dictionary, phrases, packs).
- [ ] Hold UP for 3 s: the cursor repeats. LEFT/RIGHT page.

**USB and uploads**
- [ ] With the menu on screen, upload from the IDE (or
      `cd platform/board/arduino/CHGame/libraries/CHGame/examples/Games/CHFour && chgame upload`). The upload works,
      CHFour starts, and on the next power-on the menu shows
      INSTALLED PROGRAM.
- [ ] With the menu on screen, `UP probe` or `UP info` answers, and the menu
      stays (it does not switch to "USB UPLOAD").
- [ ] From a running game, upload: the touch reaches the bootloader as
      before.
- [ ] From a running game, the touch with no upload (`UP touch`) shows
      "USB UPLOAD / B: MENU"; B goes back to the menu. (Sent while the menu
      is already up, the touch changes nothing.)
- [ ] Hold B while switching on: no menu appears (the backlight is lit, as
      always), and the LED blinks at 2 Hz (USB mode). Release B, press it
      again: the menu.

**Leaving a game**
- [ ] In a game, hold START: after 3 s the menu appears, with that game
      selected. Releasing START then does nothing.
- [ ] A short press of START still does the game's own thing (pause, or
      start on a title screen).
- [ ] With no card, the same hold restarts the game.
- [ ] In the SD card reader, START held 3 s also returns to the menu.

**Cards**
- [ ] No card: the installed game starts straight away. With no game
      installed: "NO GAMES FOUND" and USB mode.
- [ ] Card in, no GAMES folder (another card): the installed game starts.
- [ ] Pull the card while the menu is up, then press A on another game:
      "CAN'T INSTALL / CARD READ ERROR", and the old game is still there.

**Damaged packages**
- [ ] Copy these into `GAMES/` through the SD card reader:
      `python platform/bootloader/test/native/run_tests.py -k boot` writes
      the zoo to `platform/bootloader/test/native/build/pk/`. Take
      BADHCRC, NOTCHG, WRONGTGT, ZEROLEN, TRUNC, BOOTIMG and BADPCRC.
- [ ] Each is greyed or refused with its message, nothing is erased, and
      the installed game still starts.

**Fragmentation**
- [ ] Use a card with clusters of 32 KB or less: a package is at most
      50,928 B, so with 64 KB clusters it is one cluster and cannot be
      fragmented.
- [ ] Through the SD card reader, fill the card with a few large filler
      files, delete every other one, then copy a game package.
- [ ] `python tools/chgpack.py info` on an image of the card (or `chkdsk`)
      shows it fragmented.
- [ ] It installs and runs.

**Power cuts**
- [ ] Start installing a large game (CHWords) and switch off during the
      progress bar, at three different points.
- [ ] Each time, the next power-on shows the menu with no game marked
      installed.
- [ ] A installs the game again, correctly.

**The boot region after all of the above**
- [ ] With the board at the menu, the whole region 0x0000-0x2FFF read back
      over USB matches the image (spec section 39):
      ```
      python platform/bootloader/tools/bootcheck.py platform/bootloader/release/chgame_sdboot.bin
      ```
- [ ] `test_protocol.py` and the power-cut test from HW2a pass again on this
      bootloader.

## HW4: final state

- [ ] The menu bootloader installed (`release/chgame_sdboot.bin`).
- [ ] The card holds all 20 casino games and the SD card reader.
- [ ] A game installed. After any debug upload, put the release build back
      (CLAUDE.md).

## Rolling back

- **Back to 0.2.4 over USB** (Rev0 only: 0.2.4 is Rev0's bootloader):
  `UP selfupdate platform/bootloader/release/0.2.4/chgame_bootloader.bin --yes`.
  The menu bootloader still has the self-update commands, which is the
  point of keeping them in the release.
- **If USB is gone** (Rev0; a Rev1 takes `UP provision --device rev1
  --bootloader platform/bootloader/release/rev1/<image>`, as in "Rev1",
  step 2):
  1. Hold BOOT across power-on (factory ISP).
  2. `wchisp flash <image>`. `wchisp flash` erases only what it writes
     (gotcha 5), so the old sketch stays.
  3. Re-upload or reinstall a game afterwards.
- **A Rev1** goes back only to another image in [release/rev1/](release/rev1),
  over USB (`UP selfupdate ... --device rev1 --yes`) or the ISP. There is
  no older Rev1 bootloader.
