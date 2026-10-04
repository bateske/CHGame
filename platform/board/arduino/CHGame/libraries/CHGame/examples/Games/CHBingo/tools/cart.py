"""docs/cart.png, the game's picture in the visual menu: the Bingo logo over
three called balls and a daubed card (tools/boxart.py: the house style).
`chgame boxart` redraws it; edit this, not the PNG."""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import boxart as bx  # noqa: E402
from boxart import INK, WHITE, RED, BLUE, GOLD, NAVY, FELT_LT, CREAM, WINE  # noqa: E402


def ball(fb, cx, cy, colour, label):
    """A bingo ball: its colour, a white face with the number, a glint."""
    fb.fill_ellipse(cx + 1, cy + 1, 13, 13, INK)
    fb.fill_ellipse(cx, cy, 13, 13, colour)
    fb.fill_ellipse(cx, cy, 8, 8, WHITE)
    fb.ellipse(cx, cy, 13, 13, INK)
    fb.centred57(cy - 3, label, INK, cx + 1)
    fb.fill_rect(cx - 8, cy - 9, 3, 2, WHITE)


def card(fb, x, y):
    """A corner of a bingo card: the B-I-N-G-O header and daubed numbers."""
    fb.fill_rect(x, y, 74, 46, INK)
    fb.fill_rect(x + 1, y + 1, 72, 44, CREAM)
    fb.fill_rect(x + 1, y + 1, 72, 9, RED)
    for k, ch in enumerate("BINGO"):
        fb.text57(x + 4 + k * 14, y + 2, ch, WHITE)
    nums = [["7", "21", "38"], ["12", "**", "41"], ["3", "29", "33"]]
    for r, row in enumerate(nums):
        for c, n in enumerate(row):
            cx, cy = x + 12 + c * 24, y + 17 + r * 10
            if (r, c) in ((0, 0), (1, 1), (2, 2)):
                fb.fill_ellipse(cx, cy + 3, 5, 4, BLUE)       # daubed
            elif n != "**":
                fb.centred57(cy, n, INK, cx + 1)


def draw():
    fb = bx.canvas()
    bx.felt(fb, NAVY, INK)
    bx.logo(fb, bx.load_logo(HERE / "art" / "logo.txt"), 7)
    card(fb, 46, 66)
    ball(fb, 24, 52, RED, "7")
    ball(fb, 54, 44, GOLD, "22")
    ball(fb, 24, 88, FELT_LT, "61")
    return fb


if __name__ == "__main__":
    print(bx.save(draw(), HERE.parent / "docs" / "cart.png"))
