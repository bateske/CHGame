"""docs/cart.png, the game's picture in the visual menu: the Snakes &
Ladders logo over a ladder and a snake reaching for a token (tools/boxart.py:
the house style; the logos, head and token are the game's own,
tools/art/sprites.txt). `chgame boxart` redraws it; edit this, not the PNG."""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import boxart as bx  # noqa: E402
from boxart import INK, FELT, FELT_DK, FELT_LT, WOOD, GOLD, RED, WINE  # noqa: E402

SPRITES = bx.sprites(HERE / "art" / "sprites.txt")


def ladder(fb, x0, y0, x1, y1):
    """Two rails and their rungs, from (x0, y0) up to (x1, y1)."""
    for dx in (0, 14):
        for t in range(3):
            fb.line(x0 + dx + t, y0, x1 + dx + t, y1, WOOD if t < 2 else INK)
    for k in range(1, 7):
        x, y = x0 + (x1 - x0) * k // 7, y0 + (y1 - y0) * k // 7
        fb.hline(x + 1, y, 14, GOLD)
        fb.hline(x + 1, y + 1, 14, INK)


def snake(fb, cx, top, bottom, phase):
    """A snake's body winding down from its head: a fat green line."""
    for y in range(top, bottom):
        x = cx + [0, 2, 4, 5, 6, 5, 4, 2, 0, -2, -4, -5, -6, -5, -4, -2][(y + phase) // 3 % 16]
        fb.hline(x - 4, y, 9, INK)
        fb.hline(x - 3, y, 7, FELT_LT if (y // 3) % 2 else FELT)


def draw():
    fb = bx.canvas()
    bx.felt(fb, FELT, FELT_DK)
    bx.logo(fb, bx.mask(SPRITES["LOGO_SNAKES"]), 6)
    bx.logo(fb, bx.mask(SPRITES["LOGO_LADDERS"]), 36)
    ladder(fb, 14, 122, 44, 56)
    snake(fb, 92, 76, 123, 0)
    lay = bx.layer()
    bx.letters(lay, SPRITES["SNAKE_HEAD_OPEN"], 0, 0)
    bx.letters(lay, SPRITES["TOKEN_CHERRIES"], 12, 0)
    bx.blit(fb, lay, 79, 52, 3, (0, 0, 9, 9))
    bx.blit(fb, lay, 50, 92, 2, (12, 0, 11, 11))
    return fb


if __name__ == "__main__":
    print(bx.save(draw(), HERE.parent / "docs" / "cart.png"))
