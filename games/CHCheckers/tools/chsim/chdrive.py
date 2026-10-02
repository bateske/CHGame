"""Drive CHCheckers - in the simulator or on the device - with a script.

    python tools/chsim/chdrive.py --sim . <script> <outdir>
    python tools/chsim/chdrive.py --device [--port COMx] <script> <outdir>

The repository's tools/chsim/chdrivelib.py does the driving and has the
common script commands (wait, tap, hold, snap, gif, rec, say, perf ...);
its `say` already waits out a HELD reply (the CPU searching) by running
frames. CHCheckers adds:
    goto SQ [W]         (simulator) walk the glove to square SQ with D-pad taps
    board               (simulator) print the board
    waitturn [W]        (simulator) run until it is your move, then W frames more
    auto [N] [GAP]      (simulator) play N of your moves with the pad, the game
                        choosing them
    cal                 (simulator) calibrate host time against the board's, so
                        perf prints estimated device render times
--id names the game's handshake reply (default CHCK).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools" / "chsim"))
from chdrivelib import Driver, SerialTransport, SimTransport, main, mask_of  # noqa: E402,F401


class CheckersDriver(Driver):
    def press(self, button, gap):
        self.buttons(mask_of(button))
        self.frames(3)
        self.buttons(0)
        self.frames(gap)

    def walk(self, sq, gap):
        route = self.query(f"R {sq}", "ROUTE").split()[1:]
        steps = route[0] if route else ""
        if "?" in steps:
            raise SystemExit(f"no route to {sq}")
        for ch in steps:
            self.press({"U": "UP", "D": "DOWN", "L": "LEFT", "R": "RIGHT"}[ch], gap)

    def wait_turn(self):
        """Until the game waits for your move (True) or is over (False). A
        banner waiting on a button is answered with A after 90 frames."""
        waited = 0
        for _ in range(8000):
            state = self.query("H", "BOARD").split()
            if state[3] == "1":
                return True
            if len(state) > 5 and state[5] == "1" and state[4] == "0":
                return False
            waited = waited + 1 if state[4] == "1" else 0
            if waited > 90:
                self.press("A", 0)
            self.frames(1)
        return False

    def op(self, name, args, outdir):
        if name == "goto":
            # Walk the glove to square N with D-pad presses (simulator: the
            # game plans the route), W frames apart (default 8).
            self.walk(args[0], int(args[1]) if len(args) > 1 else 8)
        elif name == "waitturn":
            # (simulator) until the game waits for your move (or is over),
            # then W more frames.
            self.wait_turn()
            self.frames(int(args[0]) if args else 0)
        elif name == "auto":
            # (simulator) play N of your moves (default 1) with the pad, the
            # game choosing them: the glove walks to the piece, A, to the
            # square, A - and on through a multiple jump. GAP frames
            # between presses (default 8). Stops when the game is over.
            gap = int(args[1]) if len(args) > 1 else 8
            moves = int(args[0]) if args else 1
            while moves > 0:
                if not self.wait_turn():
                    break
                hop = self.query("A", "AUTO").split()
                if hop[1] == "none":
                    break
                if hop[3] == "2":
                    self.frames(12)                 # the game jumps on by itself
                    continue
                if hop[3] == "0":
                    self.walk(hop[1], gap)
                    self.press("A", gap)
                self.walk(hop[2], gap)
                before = self.query("H", "BOARD").split()[2]
                self.press("A", gap)
                self.frames(4)
                state = self.query("H", "BOARD").split()
                if state[2] != before or state[5] == "1" or state[3] == "0":
                    moves -= 1                      # the turn passed (else: more to jump)
        elif name == "board":
            print(self.query("H", "BOARD"), flush=True)
        elif name == "cal":
            # Simulator: host time of the primitives the CHGfx benchmark
            # measured on the board -> device ns per host ns.
            self.t.send("Q")
            vals = [int(v) for v in self.expect("CAL").split()[1:]]
            self.expect("OK")
            device_us = [93, 4, 100, 246, 263]   # benchmark-results.txt, 12 bpp run
            ratios = [d * 1000.0 / max(h, 1) for d, h in zip(device_us, vals)]
            self.ratio = sum(ratios) / len(ratios)
            print(f"calibration: device/host = {self.ratio:.1f} (clear, hline, blit16, text24, circle: {[round(r) for r in ratios]})")
        elif name == "perf" and getattr(self, "ratio", None):
            line = self.cmd("P", "PERF")
            kv = dict(f.split("=") for f in line.split()[1:] if "=" in f)
            if "pcrnd" not in kv:
                print(line)
                return True
            avg = int(kv["pcrnd"]) * self.ratio / 1e6
            mx = int(kv["pcmax"]) * self.ratio / 1e6
            print(f"perf {' '.join(args)}: est. device render avg {avg:.1f} ms, max {mx:.1f} ms ({kv['frames']} frames)")
        else:
            return False
        return True


if __name__ == "__main__":
    main(CheckersDriver, ident="CHCK")
