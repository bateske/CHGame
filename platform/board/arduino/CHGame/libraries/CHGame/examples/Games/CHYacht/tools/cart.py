"""docs/cart.png, the game's picture in the visual menu: the Yacht Dice logo
over five sixes, the yacht itself (tools/boxart.py: the house style).
`chgame boxart` redraws it; edit this, not the PNG."""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import boxart as bx  # noqa: E402
from boxart import NAVY, INK, WHITE  # noqa: E402


def draw():
    fb = bx.game()                                      # the games' green felt
    bx.logo(fb, bx.load_logo(HERE / "art" / "logo.txt"), 8)
    for x, y in ((14, 40), (50, 36), (86, 40), (32, 74), (68, 74)):
        bx.die(fb, x, y, 6, 28)
    return fb


if __name__ == "__main__":
    print(bx.save(draw(), HERE.parent / "docs" / "cart.png"))
