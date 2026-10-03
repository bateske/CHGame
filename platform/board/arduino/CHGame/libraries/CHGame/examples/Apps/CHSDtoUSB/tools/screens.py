"""The README's still picture, docs/screens.png: five of the demo session's
screens side by side (a copy in progress, the event log, the STATS and
CARD pages, ejected), from the simulator.

    python tools/screens.py

Runs tools/scripts/demo.txt (into out/demo/) and joins its snaps at 2x
with a gap between them. (docs/gameplay.gif, the reel, is `chgame gif`.)
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image

APP = Path(__file__).resolve().parents[1]
SHOTS = ["copying", "events", "stats", "card", "ejected"]
SIDE, GAP = 256, 12


def main():
    out = APP / "out" / "demo"
    r = subprocess.run([sys.executable, str(APP / "tools" / "chsim" / "chdrive.py"), "--sim", str(APP),
                        str(APP / "tools" / "scripts" / "demo.txt"), str(out)], cwd=APP)
    if r.returncode:
        raise SystemExit(f"demo.txt failed (exit {r.returncode})")
    sheet = Image.new("RGB", (len(SHOTS) * SIDE + (len(SHOTS) - 1) * GAP, SIDE), (255, 255, 255))
    for i, name in enumerate(SHOTS):
        im = Image.open(out / f"{name}.png").convert("RGB").resize((SIDE, SIDE), Image.NEAREST)
        sheet.paste(im, (i * (SIDE + GAP), 0))
    dst = APP / "docs" / "screens.png"
    sheet.save(dst, optimize=True)
    print(f"{dst}: {dst.stat().st_size:,} B")
    return 0


if __name__ == "__main__":
    sys.exit(main())
