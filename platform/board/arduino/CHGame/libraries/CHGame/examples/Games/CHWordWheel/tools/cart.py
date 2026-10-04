"""docs/cart.png, the game's picture in the visual menu: WORD WHEEL over a
wheel of letter tiles round a centre letter, the game show's lights about it
(tools/boxart.py: the house style).
`chgame boxart` redraws it; edit this, not the PNG."""
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import boxart as bx  # noqa: E402
from boxart import INK, NAVY, BLUE, GOLD, WOOD, FX_A, CREAM, RED  # noqa: E402

RING = "WHEELSOR"


def draw():
    fb = bx.canvas(NAVY)
    fb.dither(0, 0, 128, 128, INK, 1)
    bx.title(fb, "WORD WHEEL", 9, scale=1)
    cx, cy, r = 64, 78, 34
    fb.fill_ellipse(cx, cy, r + 12, r + 12, INK)
    fb.fill_ellipse(cx, cy, r + 10, r + 10, BLUE)
    for k in range(16):                                 # the lights round the rim, in the rainbow colour
        a = k * math.pi / 8
        fb.fill_rect(round(cx + (r + 10) * math.cos(a)) - 1, round(cy + (r + 10) * math.sin(a)) - 1, 3, 3,
                     FX_A if k % 2 else GOLD)
    for k, ch in enumerate(RING):
        a = -math.pi / 2 + k * 2 * math.pi / len(RING)
        bx.tile(fb, round(cx + r * math.cos(a)) - 8, round(cy + r * math.sin(a)) - 8, ch, None, 16, 17, edge=WOOD)
    bx.tile(fb, cx - 10, cy - 10, "D", None, 20, 21, face=GOLD, edge=WOOD)
    fb.rect(2, 2, 124, 124, GOLD)
    return fb


if __name__ == "__main__":
    print(bx.save(draw(), HERE.parent / "docs" / "cart.png"))
