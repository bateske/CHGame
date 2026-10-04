"""docs/cart.png, the game's picture in the visual menu: TIC TAC TOE and
Royale over a won board, three crosses struck through (tools/boxart.py: the
house style; the pieces are the game's own, tools/art/pieces). `chgame
boxart` redraws it; edit this, not the PNG."""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import boxart as bx  # noqa: E402
from boxart import INK, GOLD, NAVY, CREAM, FX_A  # noqa: E402

PIECES = HERE / "art" / "pieces"
BOARD = ["XO.", "OXO", ".OX"]


def draw():
    fb = bx.game()                                      # the games' green felt
    fb.dither(0, 0, 128, 128, INK, 1)
    bx.logo(fb, bx.load_logo(HERE / "art" / "logo.txt"), 7)
    bx.logo(fb, bx.load_logo(HERE / "art" / "royale.txt"), 21)
    x0, y0, cell = 34, 48, 21
    for k in (1, 2):
        fb.fill_rect(x0 + k * cell - 1, y0, 2, 3 * cell, GOLD)
        fb.fill_rect(x0, y0 + k * cell - 1, 3 * cell, 2, GOLD)
    x, o = bx.piece(PIECES / "x_s.png"), bx.piece(PIECES / "o_s.png")
    for r, row in enumerate(BOARD):
        for c, ch in enumerate(row):
            if ch != ".":
                p = x if ch == "X" else o
                fb.sprite(p, x0 + c * cell + (cell - len(p[0])) // 2, y0 + r * cell + (cell - len(p)) // 2)
    for t in range(-1, 2):                             # the winning line, in the rainbow colour
        fb.line(x0 + 3, y0 + 3 + t, x0 + 3 * cell - 4, y0 + 3 * cell - 4 + t, FX_A)
    fb.rect(2, 2, 124, 124, GOLD)
    return fb


if __name__ == "__main__":
    print(bx.save(draw(), HERE.parent / "docs" / "cart.png"))
