"""Drive CHSolitaire - in the simulator or on the device - with a script.

    python tools/chsim/chdrive.py --sim . <script> <outdir>
    python tools/chsim/chdrive.py --device [--port COMx] <script> <outdir>

The repository's tools/chsim/chdrivelib.py does the driving and has the
common script commands (wait, tap, hold, snap, gif, rec, say, perf ...).
CHSolitaire adds:
    waitstate S [W]     run until the table is in state S (1 play, 3 cascade, 4 done), then W frames more
    table               print the table in numbers
    expect KEY=VALUE..  check them against the table's numbers (score, moves, stock, waste, up...)
    cal                 (simulator) calibrate host time against the board's, so
                        perf prints estimated device render times
--id names the game's handshake reply (default CHSO).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools" / "chsim"))
from chdrivelib import Driver, SerialTransport, SimTransport, main, mask_of  # noqa: E402,F401


class SolitaireDriver(Driver):
    def table(self):
        """The game's H line (TABLE key=value ...) as a dict."""
        return dict(kv.split("=") for kv in self.query("H", "TABLE").split()[1:])

    def op(self, name, args, outdir):
        if name == "waitstate":
            # Run until the table is in state S (src/stage/Stage.h: 0
            # dealing, 1 play, 2 playing itself out, 3 cascade, 4 done),
            # then W frames more (default 0). Gives up after 20000 frames.
            for _ in range(20000):
                if self.table()["state"] == args[0]:
                    break
                self.frames(1)
            else:
                raise SystemExit(f"waitstate {args[0]}: never got there")
            self.frames(int(args[1]) if len(args) > 1 else 0)
        elif name == "expect":
            # expect KEY=VALUE ...: check the TABLE line.
            got = self.table()
            for kv in args:
                key, want = kv.split("=")
                if got.get(key) != want:
                    raise SystemExit(f"expect {kv}: the table says {key}={got.get(key)}")
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
    main(SolitaireDriver, ident="CHSO")
