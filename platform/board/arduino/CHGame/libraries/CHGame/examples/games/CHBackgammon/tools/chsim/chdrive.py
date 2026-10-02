"""Drive CHBackgammon - in the simulator or on the device - with a script.

    python tools/chsim/chdrive.py --sim . <script> <outdir>
    python tools/chsim/chdrive.py --device [--port COMx] <script> <outdir>

The repository's tools/chsim/chdrivelib.py does the driving and has the
common script commands (wait, step, tap, hold, snap, gif, rec, free, say,
perf, prof ...). `say` sends a game command (the list above debugHook() in
src/states/Screens.cpp) and prints its reply lines (THINK, RPROF, NET).
CHBackgammon adds:
    goto SPOT [W]       walk the glove to a spot with D-pad taps, W frames apart (6): one of
                        the side's points 1..24, 25 = its bar, 0 = its tray (the R command)
    move FROM TO        goto FROM, A, goto TO, A: pick a checker up and set it down
    auto [TURNS]        (simulator) play on for the human (the A command: the EXPERT's choices)
                        to the end of the game, or for TURNS of the human's
    board               print the game's state (the H command)
    waitturn [W]        run until the game waits for you (a roll, a move, the dice to pick
                        up), answering "PRESS A"; then W frames more
--id names the game's handshake reply (default CHBG).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[11] / "tools" / "chsim"))
from chdrivelib import Driver, SerialTransport, SimTransport, main, mask_of  # noqa: E402,F401


class BackgammonDriver(Driver):
    def press(self, spec, hold=3):
        self.buttons(mask_of(spec))
        self.frames(hold)
        self.buttons(0)
        self.frames(1)

    def goto(self, spot, gap):
        """Walk the glove to a spot with D-pad presses (the game plans the route)."""
        route = self.query(f"R {spot}", "ROUTE").split()[1:]
        steps = route[0] if route else ""
        if "?" in steps:
            raise SystemExit(f"no route to {spot}")
        for ch in steps:
            self.press({"U": "UP", "D": "DOWN", "L": "LEFT", "R": "RIGHT"}[ch])
            self.frames(gap)

    def op(self, name, args, outdir):
        if name == "goto":
            self.goto(args[0], int(args[1]) if len(args) > 1 else 6)
        elif name == "move":
            # Pick the checker on FROM up and set it down on TO.
            self.goto(args[0], 6)
            self.press("A")
            self.frames(8)
            self.goto(args[1], 6)
            self.frames(6)
            self.press("A")
        elif name == "waitturn":
            # Until the game waits for the player (state R, M or C and
            # nothing moving); the last word of a game (W) is answered
            # with A after a while.
            waited = 0
            for _ in range(20000):
                state = self.query("H", "BOARD").split()
                if state[4] in "RMCD" and (state[5] == "1" or state[4] == "D"):
                    break
                if state[4] in "OB":
                    break
                waited = waited + 1 if state[4] == "W" else 0
                if waited > 90:
                    self.press("A")
                self.frames(1)
            self.frames(int(args[0]) if args else 0)
        elif name == "auto":
            turns = int(args[0]) if args else 10000
            for _ in range(200000):
                state = self.query("H", "BOARD").split()
                if state[4] == "O" or turns <= 0:
                    break
                if state[4] in "WB":
                    self.press("A")
                elif state[4] == "D" or (state[4] in "RMC" and state[5] == "1"):
                    self.cmd("A")
                    if state[4] == "C":
                        turns -= 1
                self.frames(2)
        elif name == "board":
            print(self.query("H", "BOARD"), flush=True)
        else:
            return False
        return True


if __name__ == "__main__":
    main(BackgammonDriver, ident="CHBG")
