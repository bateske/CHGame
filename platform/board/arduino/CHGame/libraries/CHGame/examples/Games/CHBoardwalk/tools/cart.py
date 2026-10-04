"""docs/cart.png, the game's picture in the visual menu: the Boardwalk logo
over a street of houses with a hotel, a cherry token and the die
(tools/boxart.py: the house style; the sprites are the game's own,
tools/art/sprites.txt). `chgame boxart` redraws it; edit this, not the PNG."""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import boxart as bx  # noqa: E402
from boxart import INK, FELT, FELT_DK, CREAM, BLUE, RED, GOLD  # noqa: E402

SPRITES = bx.sprites(HERE / "art" / "sprites.txt")


def draw():
    fb = bx.canvas()
    bx.felt(fb, FELT, FELT_DK)
    bx.logo(fb, bx.mask(SPRITES["LOGO"]), 9)
    fb.fill_rect(8, 86, 112, 22, CREAM)                 # a street on the board
    fb.fill_rect(8, 86, 112, 6, BLUE)
    fb.rect(7, 85, 114, 24, INK)
    lay = bx.layer()
    bx.letters(lay, SPRITES["HOUSE"], 0, 0)
    bx.letters(lay, SPRITES["HOTEL"], 8, 0)
    bx.letters(lay, SPRITES["TOKEN_CHERRIES"], 18, 0)
    bx.letters(lay, SPRITES["DIE"], 32, 0)
    for k in range(3):
        bx.blit(fb, lay, 12 + k * 17, 68, 3, (0, 0, 5, 6))
    bx.blit(fb, lay, 64, 53, 3, (8, 0, 7, 8))
    bx.blit(fb, lay, 90, 40, 3, (18, 0, 11, 11))
    bx.blit(fb, lay, 24, 32, 2, (32, 0, 13, 13))
    for px, py in ((6, 6), (16, 6), (11, 11), (6, 16), (16, 16)):     # (the game draws the pips: a five)
        fb.fill_rect(24 + px, 32 + py, 3, 3, INK)
    return fb


if __name__ == "__main__":
    print(bx.save(draw(), HERE.parent / "docs" / "cart.png"))
