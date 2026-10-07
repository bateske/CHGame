"""The contacts the scope picks up, as 1-bpp bitmaps in flash: the sketch's Shapes.h.

    python tools/shapes.py

Each shape is drawn here as text (X = a lit pixel, at most 16 wide) and
packed a row at a time, the leftmost pixel in bit 15, the layout the CHGame
library's glyph16() draws. The sketch indexes them by stage (Ui.cpp).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SHAPES = {
    "AIRPLANE": """
.....X.....
....XXX....
.....X.....
.XXXXXXXXX.
XXXXXXXXXXX
.....X.....
....XXX....
""",
    "BOAT": """
.....X......
.....XX.....
.....XXX....
.....XXXX...
.....XXXXX..
.....X......
XXXXXXXXXXXX
.XXXXXXXXXX.
..XXXXXXXX..
""",
    "ROCKET": """
....X....
...XXX...
...XXX...
..XXXXX..
..X.X.X..
..XXXXX..
.XXXXXXX.
X..XXX..X
...X.X...
""",
    "RABBIT": """
.XX...XX.
.XX...XX.
.XX...XX.
.XXX.XXX.
XXXXXXXXX
XX.XXX.XX
XXXXXXXXX
.XXXXXXX.
..XXXXX..
""",
    "BANANA": """
..........X.
.........XX.
........XXX.
.......XXXX.
.....XXXXX..
X..XXXXXX...
XXXXXXXX....
.XXXXXX.....
..XXX.......
""",
}


def main():
    out = ["/* SPDX-License-Identifier: GPL-3.0-or-later",
           " * What the scope picks up between its pings: 1-bpp bitmaps, a row a word, the",
           " * leftmost pixel in bit 15 (the library's glyph16). Made by",
           " * tools/shapes.py; not edited by hand.",
           " */", "#pragma once", "#include <stdint.h>", "",
           "struct Shape { uint8_t w, h; uint16_t rows[10]; };",
           f"#define SHAPE_COUNT {len(SHAPES)}",
           "static const Shape SHAPES[SHAPE_COUNT] = {"]
    for name, art in SHAPES.items():
        rows = [r for r in art.strip("\n").splitlines()]
        w = max(len(r) for r in rows)
        assert w <= 16 and len(rows) <= 10, name
        words = []
        for r in rows:
            v = 0
            for i, ch in enumerate(r.ljust(w, ".")):
                if ch == "X":
                    v |= 1 << (15 - i)
            words.append(f"0x{v:04X}")
        out.append(f"    {{{w}, {len(rows)}, {{{', '.join(words)}}}}},   // {name}")
    out += ["};", ""]
    path = ROOT / "Shapes.h"
    path.write_text("\n".join(out), encoding="utf-8", newline="\n")
    print(f"{path}: {len(SHAPES)} shapes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
