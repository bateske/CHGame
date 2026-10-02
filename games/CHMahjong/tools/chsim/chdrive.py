"""Drive CHMahjong - in the simulator or on the device - with a script.

    python tools/chsim/chdrive.py --sim . <script> <outdir>
    python tools/chsim/chdrive.py --device [--port COMx] <script> <outdir>

The repository's tools/chsim/chdrivelib.py does the driving and has the
common script commands (wait, tap, snap, gif, rec, say, perf ...).
CHMahjong adds:
    goto TILE [W]       (simulator) walk the glove to tile TILE with D-pad taps
    solve N [W]         (simulator) take the deal's own next N pairs, as a player would
    takehint [W]        (simulator) take the pair the hint is showing, the same way
    auto N              take N pairs (the first there is each time), no glove work
    state               print the game's state
    idle                run until the game takes input again
    hold BTN[+BTN]      keep held until `release` (taps and walks press theirs as well)
    cal                 (simulator) calibrate host time against the board's, so
                        perf prints estimated device render times
--id names the game's handshake reply (default CHMJ).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools" / "chsim"))
from chdrivelib import Driver, SerialTransport, SimTransport, main, mask_of  # noqa: E402,F401


class MahjongDriver(Driver):
    def buttons(self, mask):
        # Buttons held with `hold` stay down under taps and walks.
        self.cmd(f"K {mask | getattr(self, 'base', 0):x}")

    def walk(self, tile, gap):
        """D-pad presses that take the glove to a tile (the game plans the route)."""
        route = self.query(f"R {tile}", "ROUTE").split()[1:]
        steps = route[0] if route else ""
        if "?" in steps:
            raise SystemExit(f"no route to {tile}")
        for ch in steps:
            self.buttons(mask_of({"U": "UP", "D": "DOWN", "L": "LEFT", "R": "RIGHT"}[ch]))
            self.frames(3)
            self.buttons(0)
            self.frames(gap)

    def idle(self, limit=600):
        """Run frames until the game is taking input again."""
        for _ in range(limit):
            if "busy=0" in self.query("H", "STATE"):
                return
            self.frames(1)

    def op(self, name, args, outdir):
        if name == "hold":
            self.base = mask_of(args[0])
            self.buttons(0)
        elif name == "release":
            self.base = 0
            self.buttons(0)
        elif name == "goto":
            # Walk the glove to tile N with D-pad presses (simulator: the
            # game plans the route), W frames apart (default 8).
            self.walk(args[0], int(args[1]) if len(args) > 1 else 8)
        elif name == "idle":
            self.idle()
        elif name in ("solve", "takehint"):
            # (simulator) the deal's own way of clearing the table, played
            # with the D-pad and A: W frames between presses (default 6).
            gap = int(args[1]) if len(args) > 1 else 6
            hint = name == "takehint"
            for _ in range(1 if hint else int(args[0])):
                self.idle()
                a, b = self.query("W" if hint else "O", "NEXT").split()[1:3]
                for tile in (a, b):
                    self.walk(tile, gap)
                    self.buttons(mask_of("A"))
                    self.frames(3)
                    self.buttons(0)
                    self.frames(gap)
                self.idle()
        elif name == "auto":
            for _ in range(int(args[0])):
                self.t.send("A")
                if self.expect(("OK", "ERR")).startswith("ERR"):
                    break
                self.idle()
        elif name == "state":
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
        elif name == "perf":
            # The PERF line; after `cal`, the estimated device render times.
            line = self.cmd("P", "PERF")
            kv = dict(f.split("=") for f in line.split()[1:] if "=" in f)
            if getattr(self, "ratio", None) and "pcrnd" in kv:
                avg = int(kv["pcrnd"]) * self.ratio / 1e6
                mx = int(kv["pcmax"]) * self.ratio / 1e6
                print(f"perf {' '.join(args)}: est. device render avg {avg:.1f} ms, max {mx:.1f} ms ({kv['frames']} frames)")
            else:
                print(line)
        else:
            return False
        return True


if __name__ == "__main__":
    main(MahjongDriver, ident="CHMJ")
