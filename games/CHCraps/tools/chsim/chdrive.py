"""Drive CHCraps - in the simulator or on the device - with a script.

    python tools/chsim/chdrive.py --sim . <script> <outdir>
    python tools/chsim/chdrive.py --device [--port COMx] <script> <outdir>

The repository's tools/chsim/chdrivelib.py does the driving and has the
common script commands (wait, tap, hold, snap, gif, rec, say, perf, cal ...).
CHCraps adds:
    goto ZONE [GAP]     (simulator) walk the cursor to spot ZONE with D-pad taps
    idle [W]            run until the dice cam and the payout are over, then W frames
--id names the game's handshake reply (default CHCR).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools" / "chsim"))
from chdrivelib import Driver, SerialTransport, SimTransport, main, mask_of  # noqa: E402,F401


class CrapsDriver(Driver):
    def op(self, name, args, outdir):
        if name == "idle":
            # idle [W]: run until the dice cam and the payout show are
            # over (the game's H state), then W frames more.
            for _ in range(2000):
                st = self.query("H", "STATE").split("|")[0].split()
                if st[5] == "0" and st[6] == "0":
                    break
                self.frames(4)
            self.frames(int(args[0]) if args else 0)
        elif name == "goto":
            # goto ZONE [GAP]: walk the cursor to spot ZONE (an index in
            # src/render/Zones.cpp's table) with D-pad taps, GAP frames
            # apart (default 8); the game plans the route (simulator).
            route = self.query(f"Z {args[0]}", "ROUTE").split()[1:]
            steps = route[0] if route else ""
            if "?" in steps:
                raise SystemExit(f"no route to {args[0]}")
            gap = int(args[1]) if len(args) > 1 else 8
            for ch in steps:
                self.buttons(mask_of({"U": "UP", "D": "DOWN", "L": "LEFT", "R": "RIGHT"}[ch]))
                self.frames(3)
                self.buttons(0)
                self.frames(gap)
        else:
            return False
        return True


if __name__ == "__main__":
    main(CrapsDriver, ident="CHCR")
