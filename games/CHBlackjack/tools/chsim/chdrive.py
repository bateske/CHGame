"""Drive CHBlackjack - in the simulator or on the device - with a script.

    python tools/chsim/chdrive.py --sim . <script> <outdir>
    python tools/chsim/chdrive.py --device [--port COMx] <script> <outdir>

The repository's tools/chsim/chdrivelib.py does the driving and has the
script commands (wait, tap, hold, snap, gif, rec, free, say, perf, prof ...).
CHBlackjack adds none of its own: its game commands (reseed the shoe, stack
the deck, jump to a screen) go through `say` (see CHBlackjack.ino).
--id names the game's handshake reply (default CHBJ).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools" / "chsim"))
from chdrivelib import Driver, SerialTransport, SimTransport, main, mask_of  # noqa: E402,F401


class BlackjackDriver(Driver):
    """The common driver: the place for CHBlackjack's own commands (op())."""


if __name__ == "__main__":
    main(BlackjackDriver, ident="CHBJ")
