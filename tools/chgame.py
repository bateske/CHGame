"""chgame: the one entry point for the CHGame tools.

    chgame [--sketch NAME|DIR] <command> [args]

From inside a game's folder (or any folder below it) the sketch is found by
itself; from anywhere else pass --sketch with a game's or app's name
(CHFour, CHSDtoUSB, Hello) or its folder. `pip install -e .` in the
repository root makes the `chgame` command; `python tools/chgame.py` is the
same thing uninstalled.

  build   [--debug] [-D FLAG ...]        compile for the board (release by default), print the size
  upload  [--debug] [--port P] [--arduino]
                                         compile and flash through the Python uploader
                                         (--arduino: through arduino-cli and the Go tool instead)
  sim     [-D NAME[=V] ...]              build the PC simulator, print the executable
  run     SCRIPT OUTDIR [--device] [--port P] [--card IMG] [-D ...]
                                         run a chdrive script in the simulator (default) or,
                                         with --device, as a debug build on the board
  shot    OUT.png [--port P]             screenshot of the debug build running on the board
  check   [--quick] [--no-device] [--compare A B]
                                         everything checkable without a board
  test    [ARGS ...]                     the host unit tests
  redraw  SCRIPT OUTDIR [TICKS]          the incremental-redraw check against a full redraw
  gif     [--check] [--no-run] [--every N] [--hold MS]
                                         record the README's docs/gameplay.gif (--check: all games)
  size    [BUILDDIR] [--top N] [--symbols]
                                         flash and RAM report of a build (default build/release)
  audio   OUTDIR [--only NAME ...]       the sound effects and songs as WAV, with a hash each
  uploader ARGS ...                      the uploader itself: probe, info, flash, selfupdate, burn ...
  pack    ...                            .CHG packages (tools/chgpack.py)
  card    ...                            build the whole SD card (tools/sdcard/mkcard.py)

Exit codes: 0 done, 1 the thing run failed (a compile, a test, a check),
2 usage or configuration (no sketch, a bad tools/game.py). `run` returns
the driver's own code (3: the simulator reported a BUG).
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TOOLS / "chsim"))        # before tools/: `chsim` is the module chsim.py
import paths  # noqa: E402

NEEDS_SKETCH = {"build", "upload", "sim", "run", "shot", "check", "test", "redraw", "size", "audio"}


def sketch_of(a):
    if a.sketch:
        return paths.sketch(a.sketch)
    s = paths.here()
    if s is None:
        print(f"{a.cmd}: not inside a sketch folder: pass --sketch CHFour (a game's or app's name, or its folder)",
              file=sys.stderr)
        raise SystemExit(2)
    return s


def py(script, *args, env=None, cwd=None):
    """Run one of the tools as a child, the way it runs by hand."""
    return subprocess.run([sys.executable, str(script), *map(str, args)], env=env, cwd=cwd).returncode


def where(sketch, p, must_exist=False):
    """A script or output path given on the command line: as written, from
    the current folder; else (from the root with --sketch) under the sketch."""
    q = Path(p)
    if q.is_absolute() or (must_exist and q.exists()) or (not must_exist and q.resolve().is_relative_to(sketch)):
        return q.resolve()
    return (sketch / q) if (not must_exist or (sketch / q).exists()) else q.resolve()


def game_tool(sketch, *rel):
    """A tool in the sketch's own tools/ folder, or None."""
    p = sketch.joinpath("tools", *rel)
    return p if p.exists() else None


def cmd_build(a, sketch):
    import device
    device.build(sketch, a.debug, " ".join(a.D))
    return 0


def cmd_upload(a, sketch):
    import device
    device.upload(sketch, device.build(sketch, a.debug), a.port, arduino=a.arduino)
    return 0


def cmd_sim(a, sketch):
    from chsim import build
    print(build(sketch, a.D))
    return 0


def cmd_run(a, sketch):
    if a.device:
        import device
        return device.run(sketch, where(sketch, a.script, must_exist=True), where(sketch, a.outdir), a.port)
    drv = game_tool(sketch, "chsim", "chdrive.py") or TOOLS / "chsim" / "chdrive.py"
    env = dict(os.environ)
    env.pop("CHSD_CARD", None)
    if a.card:
        env["CHSD_CARD"] = str(Path(a.card).resolve())
    args = ["--sim", sketch] + [f"-D{d}" for d in a.D]
    args += [where(sketch, a.script, must_exist=True), where(sketch, a.outdir)]
    return py(drv, *args, env=env, cwd=sketch)


def cmd_shot(a, sketch):
    import device
    device.shot(sketch, a.out, a.port)
    return 0


def cmd_check(a, sketch):
    tool = game_tool(sketch, "check.py")
    if tool is None:
        raise SystemExit(f"{sketch.name}: no tools/check.py")
    return py(tool, *a.rest, cwd=sketch)


def cmd_test(a, sketch):
    tool = game_tool(sketch, "tests", "run_tests.py")
    if tool is None:
        print(f"{sketch.name}: host tests: none")
        return 0
    return py(tool, *a.rest, cwd=sketch)


def cmd_redraw(a, sketch):
    tool = game_tool(sketch, "chsim", "diffdrive.py")
    if tool is None:
        raise SystemExit(f"{sketch.name}: no redraw check (tools/chsim/diffdrive.py)")
    return py(tool, *a.rest, cwd=sketch)


def cmd_gif(a, sketch):
    import readme_gif
    if a.check:
        return readme_gif.main(["--check"])
    return readme_gif.main([str(sketch), *a.rest])


def cmd_size(a, sketch):
    import check_size
    rest = list(a.rest)
    build = rest.pop(0) if rest and not rest[0].startswith("-") else str(sketch / "build" / "release")
    return check_size.main([build, *rest])


def cmd_audio(a, sketch):
    from audio import preview
    return preview.main([str(sketch), *a.rest])


def cmd_uploader(a, _sketch):
    return subprocess.run([sys.executable, str(paths.UPLOADER), *a.rest]).returncode


def cmd_pack(a, _sketch):
    import chgpack
    return chgpack.main(list(a.rest))


def cmd_card(a, _sketch):
    from sdcard import mkcard
    return mkcard.main(list(a.rest))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="chgame", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sketch", help="a game's or app's name (CHFour, CHSDtoUSB, Hello) or folder")
    sub = ap.add_subparsers(dest="cmd", required=True, metavar="command")

    p = sub.add_parser("build", help="compile for the board and print the size")
    p.add_argument("--debug", action="store_true", help="debug build: USB Serial and the debug protocol on")
    p.add_argument("-D", action="append", default=[], metavar="FLAG", help="extra build.extra_flags (e.g. -DX=1)")
    p = sub.add_parser("upload", help="compile and flash")
    p.add_argument("--debug", action="store_true")
    p.add_argument("--port")
    p.add_argument("--arduino", action="store_true", help="upload through arduino-cli (the Go tool)")
    p = sub.add_parser("sim", help="build the PC simulator")
    p.add_argument("-D", action="append", default=[], metavar="NAME[=V]")
    p = sub.add_parser("run", help="run a chdrive script")
    p.add_argument("script")
    p.add_argument("outdir")
    p.add_argument("--device", action="store_true", help="debug build, upload, and run on the board")
    p.add_argument("--sim", action="store_true", help="(the default)")
    p.add_argument("--port")
    p.add_argument("--card", help="an SD card image or file for the simulator ($CHSD_CARD)")
    p.add_argument("-D", action="append", default=[], metavar="NAME[=V]")
    p = sub.add_parser("shot", help="screenshot of the running debug build")
    p.add_argument("out")
    p.add_argument("--port")
    for name, help_ in (("check", "everything checkable without a board"),
                        ("test", "the host unit tests"),
                        ("redraw", "the incremental-redraw check"),
                        ("size", "flash and RAM report"),
                        ("audio", "sound effects and songs to WAV"),
                        ("uploader", "the uploader: probe, info, flash, selfupdate, burn ..."),
                        ("pack", ".CHG packages"),
                        ("card", "build the SD card")):
        sub.add_parser(name, help=help_, add_help=False)
    p = sub.add_parser("gif", help="record the README's GIF", add_help=False)
    p.add_argument("--check", action="store_true")

    # The pass-through commands take whatever follows them as it is.
    a, rest = ap.parse_known_args(argv)
    a.rest = rest
    if rest and a.cmd in {"build", "upload", "sim", "run", "shot"}:
        ap.error(f"unrecognized arguments: {' '.join(rest)}")
    sketch = None
    if a.cmd in NEEDS_SKETCH or (a.cmd == "gif" and not a.check):
        sketch = sketch_of(a)
        print(f"{sketch.name}: {a.cmd}", flush=True)
    fn = globals()[f"cmd_{a.cmd}"]
    rc = fn(a, sketch)
    return int(rc or 0)


if __name__ == "__main__":
    sys.exit(main())
