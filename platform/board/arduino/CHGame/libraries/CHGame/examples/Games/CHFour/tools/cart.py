"""docs/cart.png, the game's picture in the visual menu: FOUR IN A ROW over
the rack, four red discs on a diagonal (tools/boxart.py: the house style;
the discs are the game's own, tools/art/gen/disc_big.png). `chgame boxart`
redraws it; edit this, not the PNG."""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import boxart as bx  # noqa: E402
from boxart import INK, WHITE, SILVER, RED, WINE, GOLD, WOOD, NAVY, BLUE, SKIN  # noqa: E402

DISC = bx.piece(HERE / "art" / "gen" / "disc_big.png")
SIDES = [{WHITE: RED, SKIN: SKIN, SILVER: WINE, BLUE: WHITE},     # tools/art/sides.txt [disc]
         {WHITE: GOLD, SKIN: WHITE, SILVER: WOOD, BLUE: WHITE}]
BOARD = ["....Y",
         "..RYR",
         ".RYYR",
         "RYRYY"]


def draw():
    fb = bx.canvas(NAVY)
    fb.dither(0, 0, 128, 128, INK, 0)
    bx.title(fb, "FOUR", 6, scale=2)
    bx.title(fb, "IN A ROW", 31, scale=1)
    fb.fill_round(9, 47, 110, 78, 4, INK)
    fb.fill_round(10, 46, 108, 76, 4, BLUE)
    for r, row in enumerate(BOARD):
        for c, ch in enumerate(row):
            x, y = 13 + c * 21, 50 + r * 18
            if ch == ".":
                fb.fill_ellipse(x + 10, y + 9, 8, 8, NAVY)
            else:
                fb.sprite(DISC, x, y - 1, [SIDES[ch == "Y"].get(i, i) for i in range(16)])
    fb.rect(2, 2, 124, 124, GOLD)
    return fb


if __name__ == "__main__":
    print(bx.save(draw(), HERE.parent / "docs" / "cart.png"))
