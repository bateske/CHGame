"""The two uploaders against one board: the same commands through the Go
tool and the Python package must give the same exit codes and the same
upload report. Needs a board (CLAUDE.md, "The device": say so first, and
check nothing else is using it).

    python test/hil/test_parity.py [--port COMx] [--go PATH] [--image test/sketches/.../x.bin]

The Go tool is --go, else out/chgame-upload/<this host>/chgame-upload[.exe]
(python tools/release/build_uploader.py), else the one the board package
installed. Without --image only the commands that do not write flash run.
"""
import argparse
import os
import pathlib
import platform
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
REPO = ROOT.parents[1]
PY = [sys.executable, "-m", "chgame_upload"]
KEEP = ("crc32", "region", "readback", "installed", "mode", "protocol", "bootloader")


def go_tool(explicit):
    if explicit:
        return [explicit]
    host = {"Windows": "x86_64-mingw32", "Linux": "x86_64-pc-linux-gnu" if platform.machine() in ("x86_64", "AMD64") else "aarch64-linux-gnu",
            "Darwin": "arm64-apple-darwin" if platform.machine() == "arm64" else "x86_64-apple-darwin"}[platform.system()]
    exe = REPO / "out" / "chgame-upload" / host / ("chgame-upload.exe" if os.name == "nt" else "chgame-upload")
    if exe.exists():
        return [str(exe)]
    base = pathlib.Path(os.environ.get("LOCALAPPDATA", str(pathlib.Path.home()))) / "Arduino15" if os.name == "nt" \
        else pathlib.Path.home() / ".arduino15"
    found = sorted((base / "packages" / "CHGame" / "tools" / "chgame-upload").glob("*/chgame-upload*"))
    if found:
        return [str(found[-1])]
    raise SystemExit("no Go chgame-upload: pass --go or run python tools/release/build_uploader.py")


def run(cmd, cwd):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    kept = [ln.strip() for ln in (r.stdout + r.stderr).splitlines() if ln.split(":")[0].strip() in KEEP]
    return r.returncode, kept


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--port")
    ap.add_argument("--go")
    ap.add_argument("--image", help="a sketch .bin to flash (both tools flash it, in turn)")
    a = ap.parse_args()
    go = go_tool(a.go)
    port = ["-port", a.port] if a.port else []
    cases = [["probe"], port + ["info"], port + ["touch"], port + ["run"], ["noop"],
             ["burn", "-method", "nope", "-bootloader", "x.bin"],
             port + ["selfupdate", str(ROOT / "test" / "sketches" / "Empty" / "Empty.ino")]]   # refused: not a bootloader
    if a.image:
        cases += [port + ["flash", a.image, "-run"], port + ["flash", a.image, "-verify"]]
    bad = 0
    for args in cases:
        g = run(go + args, cwd=ROOT / "host" / "py")
        p = run(PY + args, cwd=ROOT / "host" / "py")
        same = (g[0] == 0) == (p[0] == 0) and g[1] == p[1]
        bad += not same
        print(("ok   " if same else "FAIL ") + " ".join(args))
        if not same:
            print(f"     go {g[0]}: {g[1]}\n     py {p[0]}: {p[1]}")
    print(f"{len(cases) - bad} of {len(cases)} agree")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
