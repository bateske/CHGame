"""Build, upload and drive CHRoulette on the attached CHGame.

    python tools/device.py build [--debug]         compile (release by default)
    python tools/device.py upload [--debug]        compile + upload
    python tools/device.py run SCRIPT OUTDIR       debug build, upload, run a chdrive script
    python tools/device.py shot OUT.png            screenshot of a running debug build

The repository's tools/device.py, on this game (it has the details).
"""
import sys
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GAME.parents[1] / "tools"))
import device  # noqa: E402

if __name__ == "__main__":
    device.main(GAME)
