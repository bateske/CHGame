"""Where things are in the repository, for the shared tools.

The games and apps are the CHGame library's examples, so that the Arduino
IDE lists them under File > Examples > CHGame:

    platform/board/arduino/CHGame/libraries/CHGame/examples/games/<Name>
    platform/board/arduino/CHGame/libraries/CHGame/examples/apps/<Name>

That is a long way down, so the shared tools take a sketch by its name as
well as by its folder: `python tools/readme_gif.py CHFour` from the
repository root, `python tools/device.py --sketch CHSDtoUSB build`.
From inside a game's folder, `python tools/run.py <tool> ...` runs one of
the tools in this folder (each game has that small launcher).
"""
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LIBRARIES = REPO / "platform" / "board" / "arduino" / "CHGame" / "libraries"
EXAMPLES = LIBRARIES / "CHGame" / "examples"
GAMES = EXAMPLES / "games"
APPS = EXAMPLES / "apps"


def games():
    """Every game's folder, in name order."""
    return sorted(d for d in GAMES.iterdir() if (d / f"{d.name}.ino").exists())


def sketch(arg="."):
    """A sketch's folder from a path or from a bare name (CHFour, CHSDtoUSB,
    Hello)."""
    p = Path(arg)
    if p.is_dir() and list(p.resolve().glob("*.ino")):
        return p.resolve()
    for base in (GAMES, APPS, EXAMPLES):
        d = base / p.name
        if str(arg) == p.name and (d / f"{p.name}.ino").exists():
            return d
    if p.is_dir():
        return p.resolve()
    raise SystemExit(f"{arg}: not a sketch folder, and not the name of a game or app in {EXAMPLES}")
