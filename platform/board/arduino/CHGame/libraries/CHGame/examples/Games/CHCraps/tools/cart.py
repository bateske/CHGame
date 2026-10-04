"""docs/cart.png, the game's picture in the visual menu: the Craps logo over
a pair of dice in mid-roll (a seven) and the chips riding on it
(tools/boxart.py: the house style). `chgame boxart` redraws it; edit this,
not the PNG."""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import boxart as bx  # noqa: E402
import pixkit as pk  # noqa: E402
from boxart import INK, WHITE, RED, WINE  # noqa: E402


def draw():
    fb = bx.canvas()
    bx.felt(fb)
    bx.logo(fb, bx.load_logo(HERE / "art" / "logo.txt"), 7)
    bx.die(fb, 18, 46, 3, 34, body=RED, pip=WHITE, shade=WINE)
    bx.die(fb, 62, 58, 4, 34, body=RED, pip=WHITE, shade=WINE)
    bx.chips(fb, 24, 121, 60, 3)
    bx.chips(fb, 104, 121, 150, 4)
    return fb


if __name__ == "__main__":
    print(bx.save(draw(), HERE.parent / "docs" / "cart.png"))
