"""Drive BOARDWALK - in the simulator or on the device - with a script.

    python tools/chsim/chdrive.py --sim . <script> <outdir>
    python tools/chsim/chdrive.py --device [--port COMx] <script> <outdir>

The repository's tools/chsim/chdrivelib.py does the driving and has the
common script commands (wait, tap, hold, snap, gif, rec, say, perf, cal ...).
`say` sends a game command (src/states/Screens.cpp's debugHook); one the
stage is not ready for is answered HELD and run a few frames later.
CHBoardwalk adds:
    board               print the game's state line (BOARD ...)
    waitturn [W]        run until the game waits for you, then W frames more
--id names the game's handshake reply (default CHBW).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[11] / "tools" / "chsim"))
from chdrivelib import Driver, SerialTransport, SimTransport, main, mask_of  # noqa: E402,F401


class BoardwalkDriver(Driver):
    def op(self, name, args, outdir):
        if name == "waitturn":
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
        else:
            return False
        return True


if __name__ == "__main__":
    main(BoardwalkDriver, ident="CHBW")
