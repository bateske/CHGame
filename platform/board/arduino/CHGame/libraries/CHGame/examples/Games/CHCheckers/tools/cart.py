"""docs/cart.png, the game's picture in the visual menu: CHECKERS in the
game's own title lettering over a crowned red king and a black man on the
board (tools/boxart.py: the house style; the men are the game's chips,
tools/art/chip.txt). `chgame boxart` redraws it; edit this, not the PNG."""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import boxart as bx  # noqa: E402
import pixkit as pk  # noqa: E402
from boxart import INK, WHITE, SILVER, RED, WINE, GOLD, WOOD, NAVY, BLUE, FX_B, CREAM  # noqa: E402

def man(fb, cx, cy, top, side, rim):
    """A checker seen from a little above: a thick disc, 29 wide."""
    fb.fill_ellipse(cx, cy + 7, 14, 6, INK)
    fb.fill_rect(cx - 14, cy, 29, 7, INK)
    fb.fill_ellipse(cx, cy + 6, 13, 5, side)
    fb.fill_rect(cx - 13, cy, 27, 6, side)
    fb.fill_ellipse(cx, cy, 14, 6, INK)
    fb.fill_ellipse(cx, cy, 13, 5, top)
    fb.ellipse(cx, cy, 9, 3, rim)


def crown(fb, cx, cy):
    for k in (-6, 0, 6):
        fb.fill_rect(cx + k - 1, cy - 4, 3, 4, GOLD)
    fb.fill_rect(cx - 7, cy - 1, 15, 3, GOLD)
    fb.hline(cx - 7, cy + 2, 15, WOOD)


def board(fb, y):
    """The board from a player's chair: rows of squares, nearer ones bigger."""
    top = y
    for r in range(4):
        w, h = 13 + 4 * r, 5 + 2 * r
        for c in range(-6, 7):
            x0 = 64 + c * w - (w // 2 if r % 2 else 0)
            fb.fill_rect(x0, top, w, h, RED if (r + c) % 2 else INK)
        top += h
    fb.hline(0, y - 1, 128, INK)


def draw():
    fb = bx.canvas(NAVY)
    fb.dither(0, 0, 128, 44, INK, 0)
    board(fb, 92)
    man(fb, 40, 92, RED, WINE, WINE)                     # the red king: two men, crowned
    man(fb, 40, 84, RED, WINE, WINE)
    crown(fb, 40, 84)
    man(fb, 90, 100, NAVY, INK, SILVER)                  # a black man
    fb.rect(2, 2, 124, 124, GOLD)
    pk.title35(fb, "CHECKERS", 10, 3, FX_B, GOLD, WOOD, WINE, 13)
    return fb


if __name__ == "__main__":
    print(bx.save(draw(), HERE.parent / "docs" / "cart.png"))
