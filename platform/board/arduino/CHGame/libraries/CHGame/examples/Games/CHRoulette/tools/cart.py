"""docs/cart.png, the game's picture in the visual menu: the Roulette logo
over the wheel, as wheel.py draws it (tools/boxart.py: the house style).
`chgame boxart` redraws it; edit this, not the PNG."""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import boxart as bx  # noqa: E402
import wheel  # noqa: E402


def draw():
    fb = bx.canvas()
    bx.felt(fb)
    n = 37                                             # the European wheel
    wheel.draw_wheel(fb, 64, 84, wheel.turns(n, 0.13), n, felt=False)
    fb.rect(2, 2, 124, 124, bx.GOLD)                   # (the wheel's band reaches the edges)
    bx.logo(fb, bx.load_logo(HERE / "art" / "logo.txt"), 9)
    return fb


if __name__ == "__main__":
    print(bx.save(draw(), HERE.parent / "docs" / "cart.png"))
