#!/usr/bin/env python3
"""M6: repeated end-to-end upload cycles, unattended.

    python test/hil/test_soak.py --cycles 100 [--board rev0]

The images are built for --board (default: the newest board the installed
CHGame core has, tools/device.py's default_board()), and a board whose
bootloader says it is another one is refused before anything is written.

Each cycle is the complete user-visible operation: 1200-baud touch on a running
sketch, wait for the bootloader, erase, write, device-side CRC, host-side
readback, launch, and confirm the sketch re-enumerated.

Two different images are alternated deliberately. Uploading the same bytes
repeatedly would pass even if the device quietly ignored the write and kept
running the previous sketch; alternating means every cycle has to actually
change what is in flash, and the readback proves it did.

Failures are recorded and the soak continues, because the interesting question
is the failure RATE, not the first failure.
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys
import time
import zlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
REPO = ROOT.parents[1]
sys.path.insert(0, str(ROOT / "host" / "py"))
sys.path.insert(1, str(REPO / "tools"))

from chgame_upload.client import Client, ensure_bootloader, find_ports   # noqa: E402
from chgame_upload import upload as up                                   # noqa: E402
from chgame_upload import protocol as P                                  # noqa: E402
from chgame_upload.chg import board_name, target_of                      # noqa: E402
import device                                                            # noqa: E402  (tools/device.py)


def fqbn(board: str) -> str:
    """The board's FQBN, with the IDE's default options (CHGame:ch32v:rev0)."""
    return device.DEVICES[board].fqbn


def build(sketch: pathlib.Path, out: pathlib.Path, board: str) -> bytes:
    r = subprocess.run(
        ["arduino-cli", "compile", "-b", fqbn(board), str(sketch), "--build-path", str(out)],
        capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"compile failed for {sketch.name}:\n{r.stdout}\n{r.stderr}")
    return (out / f"{sketch.name}.ino.bin").read_bytes()


class WrongBoard(RuntimeError):
    """The board attached is not the one the images are built for: the soak stops."""


def wait_for_port(timeout: float = 10.0) -> str:
    """Wait for a CHGame port to exist.

    Needed because Windows finishes tearing down and rebuilding the device stack
    slightly after the port becomes usable, so a cycle that starts the instant
    the previous one finished can find nothing. That is a host-side race, not a
    device fault - treating it as a failure would make the soak measure Windows
    enumeration timing rather than upload reliability.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        ports = find_ports()
        if ports:
            return ports[0]
        time.sleep(0.2)
    raise RuntimeError("no CHGame device appeared")


def one_cycle(image: bytes, timeout: float, board: str) -> dict:
    port = wait_for_port(timeout)

    t0 = time.monotonic()
    boot = ensure_bootloader(port, timeout=timeout)
    t_touch = time.monotonic() - t0

    with Client(boot, timeout=timeout) as c:
        h = c.hello()
        if h.board != target_of(board):     # as the uploader's -device: never another board's image
            raise WrongBoard(f"the images are built for {board_name(target_of(board))}, but this board's "
                             f"bootloader is {board_name(h.board)}'s: pass --board")
        info = up.upload(c, image, verify_readback=True)
        if not info.get("readback_ok"):
            raise RuntimeError("readback mismatch")
        c.run()

    # Confirm the sketch is back: a CHGame port that no longer answers HELLO.
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        for cand in find_ports():
            try:
                with Client(cand, timeout=0.8) as c:
                    if c.hello().mode == P.MODE_BOOTLOADER:
                        continue
            except Exception:
                info["touch_s"] = t_touch
                info["cycle_s"] = time.monotonic() - t0
                return info
        time.sleep(0.2)
    raise RuntimeError("application did not re-enumerate")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=100)
    ap.add_argument("--timeout", type=float, default=15.0)
    ap.add_argument("--board", choices=device.BOARDS,
                    help="the board attached (default: the newest the installed CHGame core has)")
    args = ap.parse_args()
    board = args.board or device.default_board()

    sketches = [ROOT / "test" / "sketches" / "BlinkSerial",
                ROOT / "test" / "sketches" / "Empty"]
    print(f"building images for {board} ({fqbn(board)})...")
    images = [build(s, pathlib.Path(f"/tmp/soak_{board}_{s.name}"), board) for s in sketches]
    for s, img in zip(sketches, images):
        print(f"  {s.name:12s} {len(img):6d} B  crc32=0x{zlib.crc32(img) & 0xFFFFFFFF:08X}")

    failures: list[tuple[int, str]] = []
    times: list[float] = []
    t_start = time.monotonic()

    for i in range(1, args.cycles + 1):
        img = images[i % len(images)]
        name = sketches[i % len(sketches)].name
        try:
            info = one_cycle(img, args.timeout, board)
            times.append(info["cycle_s"])
            print(f"  {i:4d}/{args.cycles}  {name:12s} {info['cycle_s']:5.2f}s "
                  f"(touch {info['touch_s']:.2f}s, write {info['write_s']:.2f}s) OK")
        except WrongBoard as e:            # nothing written: stop, every cycle would be refused
            print(f"  {i:4d}/{args.cycles}  {name:12s} STOPPED - {e}")
            return 1
        except Exception as e:
            failures.append((i, f"{type(e).__name__}: {e}"))
            print(f"  {i:4d}/{args.cycles}  {name:12s} FAILED - {type(e).__name__}: {e}")
            time.sleep(2)      # let USB settle before the next attempt

    elapsed = time.monotonic() - t_start
    print(f"\n{args.cycles - len(failures)}/{args.cycles} cycles passed "
          f"in {elapsed / 60:.1f} min")
    if times:
        print(f"cycle time: min {min(times):.2f}s  median "
              f"{sorted(times)[len(times) // 2]:.2f}s  max {max(times):.2f}s")
    if failures:
        print("\nfailures:")
        for i, msg in failures:
            print(f"  cycle {i}: {msg}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
