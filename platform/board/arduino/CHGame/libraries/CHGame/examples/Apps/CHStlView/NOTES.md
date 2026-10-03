# CHStlView: notes

For anyone changing the viewer. The README says what it is; StlRender.h
says how the renderer works and why.

## Where it came from

`bateske/CHStlView` (b3d6430), a sketch with its own copy of the Arduino SD
library (sdfatlib, GPL-3.0, with DMA streaming added) and a
`src/CHGame.*` button helper from CHSpriteView. It was ported into the
repository on 2026-10-02:

| Then | Now |
|---|---|
| `src/SD` (Arduino SD 1.3.0 + DMA, GPL) | CHSd: `fat::list()` and `fat::root()` for the folders, `sd::stream()` for the DMA multi-block reads, both added to CHSd for this app. The sketch is now MIT throughout. |
| `src/CHGame.*` (buttons, frame timer) | the CHGame library: `chgame`, `pal::`, `audio::`, `dbg::`, `fmt*`, `text35`, `chgame/Sizzle` |
| blocking waits for a button | screens as states (`Scr`), one frame a pass, so the simulator's lockstep and the debug protocol drive it |
| `tools/sim/appsim`, `run_app.py`, `stlsim.cpp`, `preview.py` | the repository's simulator (`chgame run`), with CHSd's pretend card |
| `tools/sim/accuracy.cpp` | `tools/tests/accuracy.cpp`, run by `chgame test` on every sample and edge case |
| `sample/` | `sdcard/MODELS/` (`tools/make_samples.py` writes them) |
| built with `-O2` | the release FQBN (Smallest + LTO); `StlRender.cpp` keeps `-O2` with a pragma |
| Serial report of each file and frame rate | the debug protocol's `H` (in the simulator, or a debug build) and the HUD |

The renderer (`StlRender.*`) is unchanged apart from its includes: the
library's `RAMFUNC` and CHGfx's framebuffer.

## The look: "secret agent"

A spy's wristwatch LCD (the one a certain N64 game pauses on), as
CHSDtoUSB's instrument panel draws it: a status bar with an icon, a word
and a seven-segment readout, a thin gauge under it, tag chips, key chips,
tabs, brackets that lock on, and a bracketed alert box with outlined
lettering. `Agent.h/.cpp` is the same file in CHSDtoUSB (it was taken out
of that sketch's screen); change both.

Here the status bar shows the folder and its model count, or the model and
its frame rate (FR/S while it moves, the full render's MS at rest); the
gauge shows where the list is, or how much of the model is on the glass
(none for the draft, filling up as a slow model streams in).

The palette: slots 0-7 are the chrome, Agent.h's roles under the house
names the Sizzle banners use (BG, PALE, GRID, MID, LIVE, DIM, ALERT,
PANEL); slots 8-15 the wire ramp. The whole screen is CHStlView's blue-teal:
the glass (`0x001`) and the wires are the original ones, and the chrome
is cut from the wires' hue (`0xCFF, 0x024, 0x379, 0x5DE, 0x267` with red
for alerts and `0x013` for the panels), where CHSDtoUSB fills the same
roles with greens. The ramp is the old formula in 8 steps instead of 9
(`0x135 ... 0xDFF`, the same two ends), which freed the slot the chrome
needed. FX_A and FX_B are wire shades, so `pal::setCycling(false)`.

## Sizes (release FQBN, 2026-10-02)

| | Flash | Static RAM |
|---|---|---|
| CHStlView 2.0 | 32,272 B | 16,324 B |
| the old sketch (`-O2`, its SD library) | 42,824 B | 17,352 B |

## The simulator

`chgame run tools/scripts/<s>.txt out/<s>`. The card is `out/card.img`,
which `tools/make_card.py` builds with CHSd's `fatimg.py` (the driver makes
it when it is missing): the samples in `MODELS/` with KNOT in 3 pieces and
TORUS in 2, `MODELS/OLD/` with an ASCII and a cut-short STL, `CUBE.STL` in
the root, an `EMPTY/` folder, and long names beside the short ones.

- `tour.txt`: every screen, the refusals, back and forth.
- `gameplay.txt`: the README's GIF (`chgame gif`).
- `state` (script command) prints the `H` line: the model, triangles, runs,
  blocks, full-frame ms, fps, mode, draft, zoom.

**Timing in the simulator.** The card is CHSd's host card: `sd::stream()`
charges 0.6 ms a call and 0.17 ms a block, as the board's DMA would, so the
full-frame time and the fps the HUD shows are the simulator's estimate of
the board's. The viewer's own clock (turning, spin, the HUD's 3 s, the
START hold) advances at least a frame period a frame, so it behaves the
same under lockstep. A frame that puts nothing on the glass (a model at
rest, a render cut short by a button) flushes a 2x1 rect in the simulator
only, or the lockstep would wait for its driver.

## Tests

`chgame test`: `accuracy` checks the fixed-point pipeline against double
precision over 7 views for every sample and the edge cases
(`tools/tests/make_edge_cases.py`: far from the origin, micrometres,
kilometres, NaN and infinite triangles, a flat open mesh). The worst error
is under 0.5 px at x16 zoom.

## Open items

- **Not run on a board yet** (nor was the original). The first session
  should measure the full-frame times against the simulator's (TORUS
  ~24 ms, KNOT ~230 ms), check `sd::stream()` on a real card (CHSDtoUSB's
  driver does the same at 24 MHz), and tune `SLOW_MS` and `DRAFT_POINTS`.
- **No CRC on the stream.** A block garbled on the wire draws one wrong
  line for a frame; during the scan it could spoil the bounding box until
  the file is opened again. CHSDtoUSB checks CRC16 alongside the DMA; the
  same could go into `sd::stream()` as an option if a board shows errors.
- **ASCII STL**: a text parser feeding the same record pipeline (about 5x
  slower, as the file is 5x bigger).
- **Long file names**: CHSd skips them; `fat::list()` could assemble them.
- **Feature edges**: hide edges between coplanar triangles, so CAD parts
  draw as clean line drawings.
- **Nothing is saved.** The save pages could keep the last folder and mode
  (a magic of its own, rule 7).
