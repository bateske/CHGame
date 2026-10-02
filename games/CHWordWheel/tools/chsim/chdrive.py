"""Drive CHWordWheel - in the simulator or on the device - with a script.

    python tools/chsim/chdrive.py --sim . <script> <outdir>
    python tools/chsim/chdrive.py --device [--port COMx] <script> <outdir>

The repository's tools/chsim/chdrivelib.py does the driving and has the
common script commands (wait, tap, hold, snap, gif, rec, say, perf ...).
CHWordWheel adds:
    rec pause / rec resume   leave what is between these out of the `rec`
                        GIF (highlights)
    cal                 (simulator) calibrate host time against the board's, so
                        perf prints estimated device render times
The game's own protocol commands (say R/F/U/C/V/M/G/W/J/H/E/X) are listed
at the top of CHWordWheel.ino.
--id names the game's handshake reply (default CHWW).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools" / "chsim"))
from chdrivelib import Driver, SerialTransport, SimTransport, main, mask_of  # noqa: E402,F401


class WordWheelDriver(Driver):
    def op(self, name, args, outdir):
        if name == "rec" and args and args[0] == "pause":
            self.rec_held, self.rec = self.rec, None
        elif name == "rec" and args and args[0] == "resume":
            self.rec = self.rec_held
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
    main(WordWheelDriver, ident="CHWW")
