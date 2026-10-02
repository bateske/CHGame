"""Drive CHChess - in the simulator or on the device - with a script.

    python tools/chsim/chdrive.py --sim . <script> <outdir>
    python tools/chsim/chdrive.py --device [--port COMx] <script> <outdir>

The repository's tools/chsim/chdrivelib.py does the driving and has the
common script commands (wait, tap, hold, snap, gif, rec, free, freegif,
say, perf ...; `say` keeps a command the game answered HELD going with
frames until the CPU's search is over). CHChess adds:
    goto SQ [W]         (simulator) walk the glove to square SQ (0..63) with
                        D-pad taps, W frames apart (default 8)
    board               (simulator) print the board
    waitturn [W]        (simulator) run until it is your move, then W frames more
    cal                 (simulator) calibrate host time against the board's, so
                        perf prints estimated device render times
--id names the game's handshake reply (default CHCS).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools" / "chsim"))
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
    main(ChessDriver, ident="CHCS")
