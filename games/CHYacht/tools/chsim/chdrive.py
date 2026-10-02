"""Drive CHYacht - in the simulator or on the device - with a script.

    python tools/chsim/chdrive.py --sim . <script> <outdir>
    python tools/chsim/chdrive.py --device [--port COMx] <script> <outdir>

The repository's tools/chsim/chdrivelib.py does the driving and has the
common script commands (wait, tap, hold, snap, gif, rec, say, perf, cal ...).
CHYacht adds:
    idle [W]            run until the dice cam and the payout are over, then W frames
--id names the game's handshake reply (default CHYD).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools" / "chsim"))
from chdrivelib import Driver, SerialTransport, SimTransport, main, mask_of  # noqa: E402,F401


class YachtDriver(Driver):
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
        else:
            return False
        return True


if __name__ == "__main__":
    main(YachtDriver, ident="CHYD")
