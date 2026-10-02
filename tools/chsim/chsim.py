"""Build a CHGame sketch for the PC simulator.

    chgame sim [-D NAME=VAL ...]                                        (from a game's folder)
    python tools/chsim/chsim.py build <sketch dir> [-D NAME=VAL ...]   -> prints the .exe path

This is the repository's shared simulator: every game builds with it (a
sketch dir may also be a game's or app's name: `chsim.py build CHFour`),
and so does any other sketch on the CHGame library.

Compiles the sketch's .ino and every .cpp/.c under its src/ folder, CHGfx's
portable code (every src/*.cpp except CHGfx.cpp, unmodified: drawing,
extras, text effects, palette), the CHGame library (every .cpp under its
src/), and the host shims in host/, where chgfx_host.cpp stands in for
CHGfx.cpp.

A sketch that includes CHSd (<Fat.h> or <SdSpi.h>) also gets CHSd's FAT
reader and, in place of its SPI driver, the pretend card in CHSd's host/
folder: the file named by $CHSD_CARD is in the slot (a *.img as a whole
card, any other file on a FAT16 card made for it; unset: no card).

A game may add shims of its own in <sketch>/tools/chsim/host/: its .cpp
files are compiled too, and one
with the same name as a shared shim replaces it. Its headers come first on
the include path, so a header there must not share a name with one here.

CHGfx is $CHSIM_CHGFX (its src folder) if set, else the repository's own copy in
platform/board/arduino/CHGame/libraries/CHGfx, else the Arduino sketchbook's libraries/CHGfx, or
libraries/CHGfx* (a GitHub zip installs as CHGfx-main). The sketchbook is
$CHSIM_SKETCHBOOK, else what `arduino-cli config get directories.user`
reports, else ~/Documents/Arduino (~/Arduino on Linux). The CHGame library
is found the same way: $CHSIM_CHGAME (its src folder), else
platform/board/arduino/CHGame/libraries/CHGame, else the sketchbook's libraries/CHGame.

Compiler: $CHSIM_CXX (e.g. "zig c++"), else zig on the PATH, else the
ziglang pip package (`pip install ziglang`), else clang++ or g++.
$CHSIM_FLAGS are added after the usual flags. A memory check of a game
(out-of-bounds writes, uninitialised reads), with valgrind:

    CHSIM_FLAGS="-O0 -g -fno-sanitize=undefined -mcpu=baseline" \
    CHSIM_WRAP="valgrind -q --error-exitcode=9" \
        chgame run tools/scripts/<s>.txt out/<s>

(-mcpu=baseline: zig otherwise targets this PC's CPU, whose newest
instructions valgrind may not know; zig's -O0 also turns UBSan on, which
the -fno-sanitize keeps out of the way.) chdrive runs the simulator under
$CHSIM_WRAP when it is set. A report of an uninitialised value in
save::read() is a game's struct padding copied into its save: harmless
(the CRC covers the bytes as stored), though zeroing the struct first
silences it.

The executable is <sketch>/tools/chsim/build/<name>/sim.exe.
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent                  # tools/chsim
sys.path.insert(0, str(HERE.parent))
import paths  # noqa: E402
VENDORED_CHGFX = HERE.parents[1] / "platform" / "board" / "arduino" / "CHGame" / "libraries" / "CHGfx" / "src"
VENDORED_CHGAME = HERE.parents[1] / "platform" / "board" / "arduino" / "CHGame" / "libraries" / "CHGame" / "src"
VENDORED_CHSD = HERE.parents[1] / "platform" / "board" / "arduino" / "CHGame" / "libraries" / "CHSd"


def sketchbook():
    env = os.environ.get("CHSIM_SKETCHBOOK")
    if env:
        return Path(env)
    try:
        r = subprocess.run(["arduino-cli", "config", "get", "directories.user"],
                           capture_output=True, text=True, timeout=30)
        if r.returncode == 0 and r.stdout.strip():
            return Path(r.stdout.strip())
    except (OSError, subprocess.TimeoutExpired):
        pass
    home = Path.home()
    return home / "Arduino" if sys.platform.startswith("linux") else home / "Documents" / "Arduino"


def chgfx_dir():
    env = os.environ.get("CHSIM_CHGFX")
    if env:
        d = Path(env)
    elif (VENDORED_CHGFX / "CHGfx_draw.cpp").exists():
        d = VENDORED_CHGFX
    else:
        d = sketchbook() / "libraries" / "CHGfx" / "src"
        if not (d / "CHGfx_draw.cpp").exists():
            # A GitHub zip installs as libraries/CHGfx-main (or -1.3.0, ...).
            found = sorted((sketchbook() / "libraries").glob("CHGfx*/src/CHGfx_draw.cpp"))
            if found:
                d = found[-1].parent
    if not (d / "CHGfx_draw.cpp").exists():
        raise SystemExit(f"CHGfx not found at {d}: install the library or set CHSIM_CHGFX")
    return d


def chgame_dir():
    """The CHGame library's src folder: $CHSIM_CHGAME, else this repository's
    platform/board/arduino/CHGame/libraries/CHGame, else the sketchbook's libraries/CHGame."""
    env = os.environ.get("CHSIM_CHGAME")
    d = Path(env) if env else VENDORED_CHGAME
    if not (d / "CHGame.h").exists():
        d = sketchbook() / "libraries" / "CHGame" / "src"
    if not (d / "CHGame.h").exists():
        raise SystemExit(f"the CHGame library was not found at {d}: set CHSIM_CHGAME")
    return d


def chsd_dir(sketch, inos):
    """CHSd's folder if the sketch includes it, else None: $CHSIM_CHSD, else
    this repository's copy, else the sketchbook's libraries/CHSd."""
    import re
    uses = re.compile(r'#\s*include\s*<(Fat|SdSpi)\.h>')
    files = list(inos) + [p for p in (sketch / "src").rglob("*") if p.suffix in (".cpp", ".c", ".h", ".hpp")]
    if not any(uses.search(p.read_text(encoding="utf-8", errors="replace")) for p in files):
        return None
    env = os.environ.get("CHSIM_CHSD")
    d = Path(env) if env else VENDORED_CHSD
    if not (d / "src" / "Fat.h").exists():
        d = sketchbook() / "libraries" / "CHSd"
    if not (d / "src" / "Fat.h").exists():
        raise SystemExit(f"the CHSd library was not found at {d}: set CHSIM_CHSD")
    return d


def find_cxx():
    env = os.environ.get("CHSIM_CXX")
    if env:
        return env.split()
    if shutil.which("zig"):
        return ["zig", "c++"]
    try:
        import ziglang  # noqa: F401
        return [sys.executable, "-m", "ziglang", "c++"]
    except ImportError:
        pass
    for c in ("clang++", "g++"):
        if shutil.which(c):
            return [c]
    raise SystemExit("no C++ compiler: set CHSIM_CXX, put zig/clang++/g++ on the PATH, "
                     "or `pip install ziglang`")


def build(sketch, defines=(), out=None):
    sketch = paths.sketch(sketch)
    name = sketch.name
    chgfx = chgfx_dir()
    chgame = chgame_dir()
    game = sketch / "tools" / "chsim"
    bdir = game / "build" / name
    bdir.mkdir(parents=True, exist_ok=True)
    own = game / "host"
    clash = sorted({p.name for p in own.glob("*.h")} & {p.name for p in (HERE / "host").glob("*.h")})
    if clash:
        raise SystemExit(f"{name}: tools/chsim/host/{clash[0]} has the name of a shared shim header")
    shims = {p.name: p for p in (HERE / "host").glob("*.cpp")}
    shims.update({p.name: p for p in own.glob("*.cpp")})
    inos = sorted(sketch.glob("*.ino"))
    main_ino = sketch / f"{name}.ino"
    if main_ino in inos:
        inos.remove(main_ino)
        inos.insert(0, main_ino)
    unit = bdir / "sketch_ino.cpp"
    with open(unit, "w", encoding="utf-8") as f:
        f.write("#include <Arduino.h>\n")
        for ino in inos:
            f.write(f'#line 1 "{ino.as_posix()}"\n')
            f.write(ino.read_text(encoding="utf-8"))
            f.write("\n")
    srcs = [unit]
    srcs += sorted(p for p in (sketch / "src").rglob("*") if p.suffix in (".cpp", ".c"))
    srcs += sorted(p for p in chgfx.glob("*.cpp") if p.name != "CHGfx.cpp")
    srcs += sorted(p for p in chgame.rglob("*") if p.suffix in (".cpp", ".c"))
    chsd = chsd_dir(sketch, inos)
    if chsd:
        # The FAT reader as it is; SdSpi.cpp compiles to nothing under
        # CHSIM, and host/sd_host.cpp is the card.
        srcs += sorted((chsd / "src").glob("*.cpp"))
        shims.setdefault("sd_host.cpp", chsd / "host" / "sd_host.cpp")
    srcs += [shims[n] for n in sorted(shims)]
    exe = Path(out) if out else bdir / "sim.exe"
    cmd = find_cxx() + [
        "-std=gnu++17", "-O1", "-g0", "-w",
        "-DCHSIM", "-DCH32X035", "-DARDUINO=10800",
    ]
    cmd += [f"-I{d}" for d in (own, HERE / "host") if d.is_dir()]
    cmd += [f"-I{sketch}", f"-I{chgfx}", f"-I{chgame}"]
    if chsd:
        cmd += [f"-I{chsd / 'src'}", f"-I{chsd / 'host'}"]
    for d in defines:
        cmd.append(f"-D{d}")
    cmd += os.environ.get("CHSIM_FLAGS", "").split()      # after the defaults, so they win
    cmd += [str(s) for s in srcs] + ["-o", str(exe)]
    # zig treats .c as C; everything here is compiled as C++ on purpose.
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit(f"chsim build failed for {name}")
    return exe


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("sketch")
    b.add_argument("-D", dest="defines", action="append", default=[])
    a = ap.parse_args(argv)
    if a.cmd == "build":
        print(build(a.sketch, a.defines))


if __name__ == "__main__":
    main()
