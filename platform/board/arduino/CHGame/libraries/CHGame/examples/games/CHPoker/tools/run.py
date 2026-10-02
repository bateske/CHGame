"""Run one of the repository's shared tools on this sketch.

    python tools/run.py readme_gif.py
    python tools/run.py chsim/chsim.py build .
    python tools/run.py check_size.py build/release --top 20
    python tools/run.py audio/preview.py . out/audio

The sketch is an example of the CHGame library, nine folders below the
repository's tools/: this finds that folder and runs the tool from here,
with the same arguments.
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def tools():
    for up in HERE.parents:
        if (up / "tools" / "chsim" / "chsim.py").exists() and (up / "platform").is_dir():
            return up / "tools"
    raise SystemExit("the repository's tools/ folder was not found above this sketch")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    sys.exit(subprocess.run([sys.executable, str(tools() / sys.argv[1]), *sys.argv[2:]]).returncode)
