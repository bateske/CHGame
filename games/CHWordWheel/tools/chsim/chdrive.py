"""Drive CHWordWheel - in the simulator or on the device - with a script.

    python tools/chsim/chdrive.py --sim . <script> <outdir>
    python tools/chsim/chdrive.py --device [--port COMx] <script> <outdir>

The repository's tools/chsim/chdrivelib.py does the driving and has the
common script commands (wait, tap, hold, snap, gif, rec, say, perf, cal ...).
CHWordWheel adds:
    rec pause / rec resume   leave what is between these out of the `rec`
                        GIF (highlights)
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
        else:
            return False
        return True


if __name__ == "__main__":
    main(WordWheelDriver, ident="CHWW")
