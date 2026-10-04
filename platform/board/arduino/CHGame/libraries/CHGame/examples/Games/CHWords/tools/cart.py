"""docs/cart.png, the game's picture in the visual menu: WORDS over its own
name in tiles, laid across the board's premium squares (tools/boxart.py:
the house style).
`chgame boxart` redraws it; edit this, not the PNG."""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import boxart as bx  # noqa: E402
from boxart import INK, NAVY, RED, BLUE, CYAN, SKIN, GOLD, FELT, FELT_DK, WOOD  # noqa: E402

SCORES = {"W": 4, "O": 1, "R": 1, "D": 2, "S": 1}


def draw():
    fb = bx.canvas()
    bx.felt(fb, FELT, FELT_DK)
    bx.title(fb, "WORDS", 8, scale=2)
    board = [RED, SKIN, CYAN, SKIN, BLUE, SKIN, RED]
    for r in range(3):                                  # the board, a few squares of it
        for c in range(7):
            col = board[(c + r * 3) % 7] if (r + c) % 2 == 0 else FELT_DK
            fb.fill_rect(8 + c * 16, 48 + r * 16, 15, 15, col)
    for k, ch in enumerate("WORDS"):
        x = 13 + k * 21
        bx.tile(fb, x, 62, ch, None, 20, 21, score=SCORES[ch], edge=WOOD)
    return fb


if __name__ == "__main__":
    print(bx.save(draw(), HERE.parent / "docs" / "cart.png"))
