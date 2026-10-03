"""Drive CHSDtoUSB in the simulator with a script.

    chgame run <script> <outdir>

The repository's tools/chsim/chdrivelib.py does the driving and has the
common script commands (wait, tap, hold, snap, gif, rec ...). There is no
device mode: on the board the sketch owns USB, and tools/chsd_test.py
tests it there.

The simulator's PC (tools/chsim/host/pc_host.cpp) plays a session that
tools/chsim/pcsession.py writes: the scenario named like the script
(demo.txt plays `demo`, edge.txt `edge`), else `demo`. The card is the
session's 16 GB FAT32 one. CHSDtoUSB adds:
    pcto NAME       let the PC go on until it reaches its `snap NAME` marker
                    (then the script snaps, records, presses ...)
    state           print the H line: USB state, card, events, the PC's place
--id names the handshake reply (default CHSU).
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


class ReaderDriver(Driver):
    def pc_state(self):
        line = self.query("H", "STATE")
        return dict(kv.split("=", 1) for kv in line.split()[2:] if "=" in kv)

    def op(self, name, args, outdir):
        if name == "pcto":
            self.cmd("G")
            for _ in range(20000):
                self.frames(5)
                s = self.pc_state()
                if s.get("at") == args[0] and s.get("paused") == "1":
                    return True
                if s.get("done") == "1":
                    raise SystemExit(f"pcto {args[0]}: the session ended without reaching it")
            raise SystemExit(f"pcto {args[0]}: not reached")
        if name == "state":
            print(self.query("H", "STATE"), flush=True)
            return True
        return False


def session():
    """$CHSD_PC for this run: the scenario named like the script, made once."""
    if os.environ.get("CHSD_PC"):
        return
    scripts = [a for a in sys.argv[1:] if a.endswith(".txt")]
    stem = Path(scripts[0]).stem if scripts else "demo"
    pcs = APP / "tools" / "chsim" / "pcsession.py"
    known = ("demo", "edge")
    scenario = stem if stem in known else "demo"
    out = APP / "out" / "pc" / scenario
    if not (out / "trace.txt").exists() or (out / "trace.txt").stat().st_mtime < pcs.stat().st_mtime:
        subprocess.run([sys.executable, str(pcs), str(out), "--scenario", scenario], check=True,
                       stdout=subprocess.DEVNULL)
    os.environ["CHSD_PC"] = str(out)


DRIVER, IDENT = ReaderDriver, "CHSU"      # what the shared tools load from this file

if __name__ == "__main__":
    session()
    main(DRIVER, ident=IDENT)
