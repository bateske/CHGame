"""docs/cart.png, the game's picture in the visual menu: CHESS in the
game's own title lettering over a white king facing a black queen on the
board (tools/boxart.py: the house style). `chgame boxart` redraws it; edit
this, not the PNG."""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import boxart as bx  # noqa: E402
import pixkit as pk  # noqa: E402
from boxart import INK, WHITE, SILVER, BLUE, NAVY, CYAN, GOLD, WOOD, WINE, FX_B, FELT, FELT_LT, SKIN  # noqa: E402

PIECES = HERE / "art" / "pieces"
BLACK = {WHITE: SILVER, SILVER: BLUE, BLUE: NAVY, CYAN: WHITE}     # tools/art/sides.txt, Black's column


def board(fb, y):
    """The board seen from a player's chair: four rows of squares, each nearer
    one taller and wider, about a centre line."""
    top = y
    for r in range(4):
        w, h = 13 + 4 * r, 5 + 2 * r
        for c in range(-6, 7):
            x0 = 64 + c * w - (w // 2 if r % 2 else 0)
            fb.fill_rect(x0, top, w, h, FELT if (r + c) % 2 else SKIN)
        top += h
    fb.hline(0, y - 1, 128, INK)


def draw():
    fb = bx.canvas(NAVY)
    fb.dither(0, 0, 128, 44, INK, 0)
    board(fb, 92)
    king, queen = bx.piece(PIECES / "king.png"), bx.piece(PIECES / "queen.png")
    pieces = bx.layer()
    pieces.sprite(king, 0, 0)
    pieces.sprite(queen, 20, 0, [BLACK.get(i, i) for i in range(16)])
    bx.blit(fb, pieces, 24, 46, 2, (0, 0, 13, 26))
    bx.blit(fb, pieces, 72, 52, 2, (20, 0, 13, 23))
    fb.rect(2, 2, 124, 124, GOLD)
    pk.title35(fb, "CHESS", 8, 4, FX_B, GOLD, WOOD, WINE, 17)
    return fb


if __name__ == "__main__":
    print(bx.save(draw(), HERE.parent / "docs" / "cart.png"))
