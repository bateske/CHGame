"""Drive CHSDtest from the PC: send its commands, print what it answers.

    python tools/chsdtest.py [--port COMx] [--timeout S] [--log FILE] COMMAND ...

Each COMMAND is one line of PROTOCOL.md ("INIT", "SET DATABR 0", "READ 0
200"); quote it when it has spaces. Each runs to its OK or ERR line (or the
timeout) before the next is sent. With no COMMAND it reads lines from
stdin, so a session can be piped in. --log appends everything to FILE.

The port is opened as tools/serialcap.py opens it (DTR set, a write that
does not drain gives up), so a board that stops reading never holds the
port.
"""
import argparse
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))   # tools/sketches/CHSDtest/tools
sys.path.insert(0, os.path.join(REPO, "tools"))
import serialcap  # noqa: E402


def run(s, cmd, timeout, log):
    s.reset_input_buffer()
    s.write((cmd + "\n").encode("ascii"))
    end = time.time() + timeout
    buf = b""
    lines = []
    while time.time() < end:
        buf += s.read(4096)
        while b"\n" in buf:
            raw, buf = buf.split(b"\n", 1)
            line = raw.decode("latin-1").rstrip("\r")
            lines.append(line)
            print(line, flush=True)
            if log:
                log.write(line + "\n")
            if line == "OK" or line.startswith("ERR"):
                return lines
    print(f"(no OK within {timeout:.0f} s)", flush=True)
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port")
    ap.add_argument("--timeout", type=float, default=120.0)
    ap.add_argument("--log")
    ap.add_argument("commands", nargs="*")
    a = ap.parse_args()
    log = open(a.log, "a", encoding="utf-8", newline="\n") if a.log else None
    s = serialcap.open_port(a.port)
    time.sleep(0.3)
    s.read(65536)                                       # whatever it said at start-up
    cmds = a.commands or [ln.strip() for ln in sys.stdin if ln.strip()]
    try:
        for c in cmds:
            print("> " + c, flush=True)
            if log:
                log.write("> " + c + "\n")
            run(s, c, a.timeout, log)
    finally:
        s.close()
        if log:
            log.close()


if __name__ == "__main__":
    main()
