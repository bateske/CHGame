"""Drive CHPoker - in the simulator or on the device - with a script.

    python tools/chsim/chdrive.py --sim . <script> <outdir>
    python tools/chsim/chdrive.py --device [--port COMx] <script> <outdir>

The repository's tools/chsim/chdrivelib.py does the driving and has the
common script commands (wait, tap, hold, snap, gif, rec, say, perf ...).
CHPoker adds:
    waitturn [W]        run until the table waits for you, then W frames more
    table               print the table's phase, your turn and the stacks
    playto P [W]        check/call on your turns until the table reaches phase P
    cal                 (simulator) calibrate host time against the board's, so
                        perf prints estimated device render times
--id names the game's handshake reply (default CHPK).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools" / "chsim"))
from chdrivelib import Driver, SerialTransport, SimTransport, main, mask_of  # noqa: E402,F401


class PokerDriver(Driver):
    def op(self, name, args, outdir):
        if name == "waitturn":
            # Run until the table waits for you (a bet or the draw), then
            # W frames more (default 0). Gives up after 6000 frames.
            for _ in range(6000):
                state = self.query("H", "TABLE").split()
                if state[2] == "1":
                    break
                self.frames(1)
            self.frames(int(args[0]) if args else 0)
        elif name == "playto":
            # Check or call (A) whenever it is your turn, until the table
            # reaches phase P (src/game/Table.h: 11 showdown, 12 award,
            # 13 hand over), then W frames more.
            want = int(args[0])
            for _ in range(20000):
                state = self.query("H", "TABLE").split()
                if int(state[1]) == want:
                    break
                if state[2] == "1":
                    self.buttons(mask_of("A"))
                    self.frames(3)
                    self.buttons(0)
                self.frames(1)
            self.frames(int(args[1]) if len(args) > 1 else 0)
        elif name == "table":
            print(self.query("H", "TABLE"), flush=True)
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
            if "pcrnd" not in kv:                   # the board: its own times
                print(line)
                return True
            avg = int(kv["pcrnd"]) * self.ratio / 1e6
            mx = int(kv["pcmax"]) * self.ratio / 1e6
            print(f"perf {' '.join(args)}: est. device render avg {avg:.1f} ms, max {mx:.1f} ms ({kv['frames']} frames)")
        else:
            return False
        return True


if __name__ == "__main__":
    main(PokerDriver, ident="CHPK")
