"""Drive CHBingo - in the simulator or on the device - with a script.

    python tools/chsim/chdrive.py --sim . <script> <outdir>
    python tools/chsim/chdrive.py --device [--port COMx] <script> <outdir>

The repository's tools/chsim/chdrivelib.py does the driving and has the
common script commands (wait, tap, hold, snap, gif, rec, say, perf, cal ...).
CHBingo adds:
The game's own protocol commands (say R/J/C/F/G/D/W/I/H/X/M/A/Y/V/E) are
listed at the top of CHBingo.ino.
--id names the game's handshake reply (default CHBN).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[11] / "tools" / "chsim"))
from chdrivelib import Driver, SerialTransport, SimTransport, main, mask_of  # noqa: E402,F401


class BingoDriver(Driver):
    """No script commands of its own yet: they would go in op() (see Driver.op)."""


if __name__ == "__main__":
    main(BingoDriver, ident="CHBN")
