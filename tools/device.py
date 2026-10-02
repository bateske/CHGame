"""Build, upload and drive a CHGame sketch on the attached board.

    python tools/device.py [--sketch DIR] build [--debug]     compile (release by default)
    python tools/device.py [--sketch DIR] upload [--debug]    compile + upload
    python tools/device.py [--sketch DIR] run SCRIPT OUTDIR   debug build, upload, run a chdrive script
    python tools/device.py [--sketch DIR] shot OUT.png        screenshot of a running debug build

The sketch is DIR, else the current folder. Each game in games/ has a
tools/device.py that runs this one on itself, so from a game's folder
`python tools/device.py build` does the same.

Builds use the CHGfx and CHGame libraries in platform/libraries (the copies
the simulator uses too). Both use opt=oslto (Tools > Optimize > "Smallest +
LTO": -Os -flto, about 3.9 KB smaller than plain -Os) and periph=game (the
default Peripherals setting). Release builds add usb=uploadonly (Tools >
USB > "Upload only": compiles out Serial, which release code never uses,
but keeps the 1200-baud upload handshake, so uploading still needs no
button press). Debug builds keep USB Serial, which the debug protocol talks
over, and turn the protocol on with -DCHGAME_DEBUG=1 in build.extra_flags
(empty on this platform). A build ends with tools/check_size.py's report:
flash, the image against the save pages, and RAM.

`run` and `shot` talk to the sketch through its tools/chsim/chdrive.py.
Needs the CHGame board package 0.2.4+.
"""
import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LIBRARIES = REPO / "platform" / "libraries"
FQBN_DEBUG = "CHGame:ch32v:CHGame:opt=oslto,rtlib=nano,periph=game"
FQBN_RELEASE = FQBN_DEBUG + ",usb=uploadonly"


def build(sketch, debug, flags=""):
    out = sketch / "build" / ("debug" if debug else "release")
    cmd = ["arduino-cli", "compile", "-b", FQBN_DEBUG if debug else FQBN_RELEASE,
           "--build-path", str(out)]
    extra = ("-DCHGAME_DEBUG=1 " if debug else "") + flags
    if extra.strip():
        cmd += ["--build-property", "build.extra_flags=" + extra.strip()]
    cmd += ["--library", str(LIBRARIES / "CHGfx"), "--library", str(LIBRARIES / "CHGame")]
    cmd.append(str(sketch))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.stderr.write(r.stdout[-3000:] + r.stderr[-3000:])
        raise SystemExit("compile failed")
    subprocess.run([sys.executable, str(REPO / "tools" / "check_size.py"), str(out), "--top", "0"])
    return out


def upload(sketch, out, port=None):
    sys.path.insert(0, str(REPO / "tools"))      # tools/serialcap.py
    from serialcap import find_port
    port = port or find_port()
    if not port:
        raise SystemExit("no CHGame found on USB (VID 16C0:27DD): plug it in, or pass --port")
    r = subprocess.run(["arduino-cli", "upload", "-b", "CHGame:ch32v:CHGame", "-p", port,
                        "--input-dir", str(out), str(sketch)], capture_output=True, text=True)
    if r.returncode:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit("upload failed")
    print(r.stdout.strip().splitlines()[-1])


def main(sketch=None, flags=""):
    """flags: extra build.extra_flags for this sketch (both builds)."""
    ap = argparse.ArgumentParser()
    if sketch is None:
        ap.add_argument("--sketch", type=Path, default=Path.cwd(), help="the sketch's folder")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("build", "upload"):
        p = sub.add_parser(name)
        p.add_argument("--debug", action="store_true")
        p.add_argument("--port")
    p = sub.add_parser("run")
    p.add_argument("script")
    p.add_argument("outdir")
    p.add_argument("--port")
    p = sub.add_parser("shot")
    p.add_argument("out")
    p.add_argument("--port")
    a = ap.parse_args()
    sketch = Path(sketch or a.sketch).resolve()
    chsim = sketch / "tools" / "chsim"
    if a.cmd == "build":
        build(sketch, a.debug, flags)
    elif a.cmd == "upload":
        upload(sketch, build(sketch, a.debug, flags), a.port)
    elif a.cmd == "run":
        upload(sketch, build(sketch, True, flags), a.port)
        cmd = [sys.executable, str(chsim / "chdrive.py"), "--device", a.script, a.outdir]
        if a.port:
            cmd[3:3] = ["--port", a.port]
        raise SystemExit(subprocess.run(cmd).returncode)
    elif a.cmd == "shot":
        sys.path.insert(0, str(chsim))
        sys.path.insert(0, str(REPO / "tools" / "chsim"))
        from chdrive import Driver, SerialTransport
        from fbimage import to_image
        d = Driver(SerialTransport(a.port))
        d.handshake()
        to_image(d.shot(), 3).save(a.out)
        print(a.out)


if __name__ == "__main__":
    main()
