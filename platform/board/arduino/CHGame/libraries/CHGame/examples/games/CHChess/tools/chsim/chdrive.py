"""Drive CHChess - in the simulator or on the device - with a script.

    python tools/chsim/chdrive.py --sim . <script> <outdir>
    python tools/chsim/chdrive.py --device [--port COMx] <script> <outdir>

The repository's tools/chsim/chdrivelib.py does the driving and has the
common script commands (wait, tap, hold, snap, gif, rec, free, freegif,
say, perf, cal ...; `say` keeps a command the game answered HELD going with
frames until the CPU's search is over). CHChess adds:
    goto SQ [W]         (simulator) walk the glove to square SQ (0..63) with
                        D-pad taps, W frames apart (default 8)
    board               (simulator) print the board
    waitturn [W]        (simulator) run until it is your move, then W frames more
--id names the game's handshake reply (default CHCS).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[11] / "tools" / "chsim"))
from chdrivelib import Driver, SerialTransport, SimTransport, main, mask_of  # noqa: E402,F401


class ChessDriver(Driver):
    def op(self, name, args, outdir):
        if name == "goto":
            # Walk the glove to square N with D-pad presses (simulator: the
            # game plans the route, debug R), W frames apart (default 8).
            route = self.query(f"R {args[0]}", "ROUTE").split()[1:]
            steps = route[0] if route else ""
            if "?" in steps:
                raise SystemExit(f"no route to {args[0]}")
            gap = int(args[1]) if len(args) > 1 else 8
            for ch in steps:
                self.buttons(mask_of({"U": "UP", "D": "DOWN", "L": "LEFT", "R": "RIGHT"}[ch]))
                self.frames(3)
                self.buttons(0)
                self.frames(gap)
        elif name == "waitturn":
            # (simulator) until the game waits for your move (debug H), then
            # W more frames. CHECK! against you is answered with A after 90
            # frames.
            waited = 0
            for _ in range(5000):
                state = self.query("H", "BOARD").split()
                if state[3] == "1":
                    break
                waited = waited + 1 if state[4] == "1" else 0
                if waited > 90:
                    self.buttons(mask_of("A"))
                    self.frames(3)
                    self.buttons(0)
                self.frames(1)
            self.frames(int(args[0]) if args else 0)
        elif name == "board":
            print(self.query("H", "BOARD"), flush=True)
        else:
            return False
        return True


if __name__ == "__main__":
    main(ChessDriver, ident="CHCS")
