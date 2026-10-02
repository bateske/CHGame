"""Drive CHFour - in the simulator or on the device - with a script.

    python tools/chsim/chdrive.py --sim . <script> <outdir>
    python tools/chsim/chdrive.py --device [--port COMx] <script> <outdir>

The repository's tools/chsim/chdrivelib.py does the driving and has the
common script commands (wait, tap, hold, snap, gif, rec, say, perf ...).
CHFour adds:
    col N               move your disc over column N (1..7) with D-pad taps and drop it
    auto [TURNS]        (simulator) play on for the human (the A command: the SHARK's choices)
                        to the end of the game, or for TURNS of the human's
    board               print the game's state (the H command)
    waitturn [W]        run until the game waits for your move, or is over; then W frames more
    waitover [W]        run until the result is up (hurrying the ending along); then W frames more
    cal                 (simulator) calibrate host time against the board's, so
                        perf prints estimated device render times
--id names the game's handshake reply (default CHF4).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools" / "chsim"))
from chdrivelib import Driver, SerialTransport, SimTransport, main, mask_of  # noqa: E402,F401


class FourDriver(Driver):
    def press(self, spec, hold=3):
        self.buttons(mask_of(spec))
        self.frames(hold)
        self.buttons(0)
        self.frames(1)

    def op(self, name, args, outdir):
        if name == "col":
            # The cursor starts wherever it was left: the game says where
            # by taking the disc there (D-pad taps, as a player would).
            want = int(args[0]) - 1
            for _ in range(7):
                self.press("LEFT", 2)
            for _ in range(want):
                self.press("RIGHT", 2)
            self.frames(4)
            self.press("A")
        elif name == "waitturn":
            # Until the game waits for the player (state M and nothing
            # moving) or the game is over (W: its ending is playing).
            for _ in range(20000):
                state = self.query("H", "BOARD").split()
                if (state[4] == "M" and state[5] == "1") or state[4] in "OW":
                    break
                self.frames(1)
            self.frames(int(args[0]) if args else 0)
        elif name == "waitover":
            waited = 0
            for _ in range(20000):
                state = self.query("H", "BOARD").split()
                if state[4] == "O":
                    break
                waited = waited + 1 if state[4] == "W" else 0
                if waited > 400:
                    self.press("A")
                self.frames(1)
            self.frames(int(args[0]) if args else 0)
        elif name == "auto":
            turns = int(args[0]) if args else 10000
            for _ in range(200000):
                state = self.query("H", "BOARD").split()
                if state[4] in "OW" or turns <= 0:
                    break
                if state[4] == "M" and state[5] == "1":
                    self.cmd("A")
                    turns -= 1
                self.frames(2)
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
            if "pcrnd" in kv:
                avg = int(kv["pcrnd"]) * self.ratio / 1e6
                mx = int(kv["pcmax"]) * self.ratio / 1e6
                print(f"perf {' '.join(args)}: est. device render avg {avg:.1f} ms, max {mx:.1f} ms ({kv['frames']} frames)")
            else:
                print(line)
        else:
            return False
        return True


if __name__ == "__main__":
    main(FourDriver, ident="CHF4")
