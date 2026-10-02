"""Drive CHWords - in the simulator or on the device - with a script.

    python tools/chsim/chdrive.py --sim . <script> <outdir>
    python tools/chsim/chdrive.py --device [--port COMx] <script> <outdir>

The repository's tools/chsim/chdrivelib.py does the driving and has the
common script commands (wait, tap, hold, snap, gif, rec, say, perf ...).
CHWords adds:
    auto [TURNS]        (simulator) play on for the human (the A command: the best play found)
                        to the end of the game, or for TURNS of the human's
    board               print the game's state (the H command)
    waitturn [W]        run until the game waits for your move (answering a hand-over
                        with A), or is over; then W frames more
    cal                 (simulator) calibrate host time against the board's, so
                        perf prints estimated device render times
--id names the game's handshake reply (default CHWD).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools" / "chsim"))
from chdrivelib import Driver, SerialTransport, SimTransport, main, mask_of  # noqa: E402,F401


class WordsDriver(Driver):
    def press(self, spec, hold=3):
        self.buttons(mask_of(spec))
        self.frames(hold)
        self.buttons(0)
        self.frames(1)

    def op(self, name, args, outdir):
        if name == "waitturn":
            # Until the game waits for the player's move with nothing
            # moving (or is over); a hand-over is answered with A.
            for _ in range(20000):
                state = self.query("H", "STATE").split()
                if (state[2] == "M" and state[3] == "1") or state[2] == "O":
                    break
                if state[2] == "W":
                    self.press("A")
                self.frames(1)
            self.frames(int(args[0]) if args else 0)
        elif name == "auto":
            # Play the human's moves (the best play found) for N turns,
            # or to the end of the game.
            turns = int(args[0]) if args else 10000
            for _ in range(200000):
                state = self.query("H", "STATE").split()
                if state[2] == "O" or turns <= 0:
                    break
                if state[2] == "W":
                    self.press("A")
                elif state[2] == "M" and state[3] == "1":
                    self.cmd("A")
                    turns -= 1
                self.frames(2)
        elif name == "board":
            print(self.query("H", "STATE"), flush=True)
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
            avg = int(kv["pcrnd"]) * self.ratio / 1e6
            mx = int(kv["pcmax"]) * self.ratio / 1e6
            print(f"perf {' '.join(args)}: est. device render avg {avg:.1f} ms, max {mx:.1f} ms ({kv['frames']} frames)")
        else:
            return False
        return True


if __name__ == "__main__":
    main(WordsDriver, ident="CHWD")
