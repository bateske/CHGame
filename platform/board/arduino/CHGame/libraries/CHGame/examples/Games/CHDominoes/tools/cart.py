"""docs/cart.png, the game's picture in the visual menu: the Dominoes logo
over a double six and a five-three meeting it (tools/boxart.py: the house
style). `chgame boxart` redraws it; edit this, not the PNG."""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import boxart as bx  # noqa: E402
from boxart import INK, CREAM, SILVER, FELT_DK, GOLD  # noqa: E402

SPOTS = {0: [], 1: [(1, 1)], 2: [(0, 0), (2, 2)], 3: [(0, 0), (1, 1), (2, 2)],
         4: [(0, 0), (2, 0), (0, 2), (2, 2)], 5: [(0, 0), (2, 0), (1, 1), (0, 2), (2, 2)],
         6: [(0, 0), (2, 0), (0, 1), (2, 1), (0, 2), (2, 2)]}


def half(fb, x, y, n, s):
    """One end of a domino: s square, n pips."""
    for i, j in SPOTS[n]:
        fb.fill_round(x + 3 + i * (s - 10) // 2, y + 3 + j * (s - 10) // 2, 4, 4, 1, INK)


def domino(fb, x, y, a, b, s=26, upright=True):
    w, h = (s, 2 * s) if upright else (2 * s, s)
    fb.fill_round(x + 2, y + 3, w, h, 4, FELT_DK)
    fb.fill_round(x, y, w, h, 4, INK)
    fb.fill_round(x + 1, y + 1, w - 2, h - 2, 3, CREAM)
    fb.fill_round(x + 1, y + h - 4, w - 2, 3, 1, SILVER)
    if upright:
        fb.hline(x + 4, y + s, s - 8, INK)
        fb.pixel(x + s // 2, y + s, GOLD)
        half(fb, x + 1, y + 1, a, s - 2)
        half(fb, x + 1, y + s + 1, b, s - 2)
    else:
        fb.vline(x + s, y + 4, s - 8, INK)
        fb.pixel(x + s, y + s // 2, GOLD)
        half(fb, x + 1, y + 1, a, s - 2)
        half(fb, x + s + 1, y + 1, b, s - 2)


def draw():
    fb = bx.canvas()
    bx.felt(fb)
    bx.logo(fb, bx.logo_from_assets(HERE.parent), 8)
    domino(fb, 20, 38, 6, 6, 28)
    domino(fb, 52, 66, 6, 3, 28, upright=False)
    return fb


if __name__ == "__main__":
    print(bx.save(draw(), HERE.parent / "docs" / "cart.png"))
