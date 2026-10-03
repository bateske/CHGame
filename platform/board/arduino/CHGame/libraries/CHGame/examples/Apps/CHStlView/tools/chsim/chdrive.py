"""Drive CHStlView - in the simulator or on the device - with a script.

    chgame run <script> <outdir>
    python tools/chsim/chdrive.py --device [--port COMx] <script> <outdir>

The repository's tools/chsim/chdrivelib.py does the driving and has the
common script commands (wait, tap, hold, snap, gif, rec, say, perf, cal ...).
CHStlView adds:
    state               print what is on screen (the H command): in the viewer the
                        model, its triangles, runs, full-frame ms, fps, mode
In the simulator the card is $CHSD_CARD, or else out/card.img (made by
tools/make_card.py when it is missing): every script has the sample models.
--id names the sketch's handshake reply (default STLV).
"""
import os
import subprocess
import sys
from pathlib import Path

APP = Path(__file__).resolve().parents[2]


def _tools():
    """The repository's tools/ above this sketch; a copy in a sketchbook has none."""
    for up in Path(__file__).resolve().parents:
        if (up / "tools" / "chsim" / "chsim.py").exists() and (up / "platform").is_dir():
            return up / "tools"
    raise SystemExit(f"{Path(__file__).name}: the CHGame repository's tools/ was not found above this sketch "
                     "(this file needs tools/chsim/chdrivelib.py); run it from a checkout")


sys.path.insert(0, str(_tools() / "chsim"))
from chdrivelib import Driver, SerialTransport, SimTransport, main, mask_of  # noqa: E402,F401


class StlDriver(Driver):
    def op(self, name, args, outdir):
        if name == "state":
            print(self.query("H", "STATE"), flush=True)
            return True
        return False


def default_card():
    if os.environ.get("CHSD_CARD") or "--device" in sys.argv:
        return
    card = APP / "out" / "card.img"
    if not card.exists():
        subprocess.run([sys.executable, str(APP / "tools" / "make_card.py"), str(card)], check=True)
    os.environ["CHSD_CARD"] = str(card)


DRIVER, IDENT = StlDriver, "STLV"         # what the shared tools load from this file

if __name__ == "__main__":
    default_card()
    main(DRIVER, ident=IDENT)
