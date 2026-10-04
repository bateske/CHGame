"""docs/cart.png, the game's picture in the visual menu: BACKGAMMON over the
board's points, checkers stacked on them and a double thrown (tools/boxart.py:
the house style; the checkers and dice are the game's own). `chgame boxart`
redraws it; edit this, not the PNG."""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import boxart as bx  # noqa: E402
from boxart import INK, WHITE, SILVER, RED, WINE, NAVY, BLUE, SKIN, CREAM, WOOD, GOLD  # noqa: E402

GEN = HERE / "art" / "gen"
RED_SIDE = {WHITE: RED, SKIN: SKIN, SILVER: WINE, BLUE: WHITE}     # tools/art/sides.txt [checker], the second side


def point(fb, x, base, w, h, colour, up=True):
    """One of the board's points: a triangle w wide, h tall."""
    for r in range(h):
        half = (w * (h - r)) // (2 * h)
        y = base - r if up else base + r
        fb.hline(x + w // 2 - half, y, 2 * half + (w % 2), colour)


def draw():
    fb = bx.canvas()
    bx.felt(fb, NAVY, INK)
    fb.fill_rect(6, 40, 116, 82, WOOD)
    fb.fill_rect(8, 42, 112, 78, CREAM)
    for k in range(6):
        point(fb, 9 + k * 18, 118, 18, 46, WINE if k % 2 else INK)
    checker = bx.piece(GEN / "checker_big.png")
    dice = bx.piece(GEN / "dice.png")
    for k in range(3):
        fb.sprite(checker, 10, 102 - k * 15)
        fb.sprite(checker, 46, 102 - k * 15, [RED_SIDE.get(i, i) for i in range(16)])
    for k in range(2):
        fb.sprite(checker, 82, 102 - k * 15)
    face = [row[5 * 12:6 * 12] for row in dice]        # the six
    lay = bx.layer()
    lay.sprite(face, 0, 0)
    bx.blit(fb, lay, 76, 52, 2, (0, 0, 12, 12))
    bx.blit(fb, lay, 98, 60, 2, (0, 0, 12, 12))
    fb.rect(2, 2, 124, 124, GOLD)
    bx.title(fb, "BACKGAMMON", 12, scale=1)
    return fb


if __name__ == "__main__":
    print(bx.save(draw(), HERE.parent / "docs" / "cart.png"))
