"""The simulator's SD card for CHStlView: out/card.img, a FAT16 image made
with CHSd's tools/fatimg.py.

    python tools/make_card.py [OUT.img]

What is on it:
    CUBE.STL              in the root, beside the folders
    MODELS/               the samples in sdcard/MODELS (KNOT.STL in 3 pieces,
                          TORUS.STL in 2, so the viewer follows a fragmented file)
    MODELS/OLD/ASCII.STL  an ASCII STL: refused, with a message
    MODELS/OLD/HALF.STL   a binary STL cut short: refused
    EMPTY/                a folder with nothing in it
Long names are written too (as Windows would), and the viewer must skip them.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
APP = HERE.parent


def chsd_tools():
    for up in APP.parents:
        t = up / "CHSd" / "tools"
        if (t / "fatimg.py").exists():
            return t
    raise SystemExit("CHSd's tools/fatimg.py was not found above this sketch")


sys.path.insert(0, str(chsd_tools()))
import fatimg  # noqa: E402


def main(argv):
    out = Path(argv[1]) if len(argv) > 1 else APP / "out" / "card.img"
    out.parent.mkdir(parents=True, exist_ok=True)
    models = APP / "sdcard" / "MODELS"
    files = {f"MODELS/{p.name}": p.read_bytes() for p in sorted(models.glob("*.STL"))}
    files["CUBE.STL"] = (models / "CUBE.STL").read_bytes()
    files["MODELS/OLD/ASCII.STL"] = b"solid cube\n  facet normal 0 0 1\n    outer loop\n" + b" " * 200
    files["MODELS/OLD/HALF.STL"] = (models / "TORUS.STL").read_bytes()[:3000]
    files["EMPTY/"] = None
    fatimg.build_image(str(out), files, fs="fat16", lfn=True, label="CHSTLVIEW",
                       fragment={"MODELS/KNOT.STL": 3, "MODELS/TORUS.STL": 2})
    print(f"{out}: {out.stat().st_size // (1 << 20)} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
