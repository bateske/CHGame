"""Drive SNAKES & LADDERS - in the simulator or on the device - with a script.

    python tools/chsim/chdrive.py --sim . <script> <outdir>
    python tools/chsim/chdrive.py --device [--port COMx] <script> <outdir>

The repository's tools/chsim/chdrivelib.py does the driving and has the
common script commands (wait, tap, hold, snap, gif, rec, say, perf ...).
`say` sends a game command (src/states/Screens.cpp's debugHook); one the
stage is not ready for is answered HELD and run a few frames later, and
this game's `say` also takes the frame ack that comes after it.
CHSnakes adds:
    board               print the game's state line (BOARD ...)
    waitturn [W]        run until the game waits for you, then W frames more
    cal                 (simulator) calibrate host time against the board's, so
                        perf prints estimated device render times
--id names the game's handshake reply (default CHSN).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools" / "chsim"))
from chdrivelib import Driver, SerialTransport, SimTransport, main, mask_of  # noqa: E402,F401


class SnakesDriver(Driver):
    def say(self, text):
        self.t.send(text)
        owed = 0                                    # frame acks still to come
        for _ in range(10000):
            line = self.t.readline()
            if line.startswith("HELD"):
                # The stage is still showing something: game commands wait
                # for it, and in lockstep it needs frames to finish.
                self.t.send("N 5")
                owed += 1
                continue
            if line.startswith("OK ") and line[3:].strip().isdigit():
                self.t.send("N 5")                  # a frame ack, still waiting
                continue
            if line.startswith("OK"):
                break
            if line.startswith("ERR"):
                raise SystemExit(f"game refused: say {text}")
            print(line)                             # the hook's own reply lines
        # The command's own OK comes before the ack of the frames that let
        # it run: take that too, or every later reply is read one line late.
        while owed:
            line = self.t.readline()
            if line.startswith("OK ") and line[3:].strip().isdigit():
                owed = 0

    def op(self, name, args, outdir):
        if name == "say":
            self.say(" ".join(args))
        elif name == "waitturn":
            # Until the game waits for your choice, then W more frames. A
            # card or a banner held for a press is answered with A after
            # 90 frames.
            waited = 0
            for _ in range(20000):
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
            if "pcrnd" not in kv:               # the board: its own times
                print(line)
                return True
            avg = int(kv["pcrnd"]) * self.ratio / 1e6
            mx = int(kv["pcmax"]) * self.ratio / 1e6
            print(f"perf {' '.join(args)}: est. device render avg {avg:.1f} ms, max {mx:.1f} ms ({kv['frames']} frames)")
        else:
            return False
        return True


if __name__ == "__main__":
    main(SnakesDriver, ident="CHSN")
