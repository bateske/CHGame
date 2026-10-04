"""docs/cart.png, the game's picture in the visual menu: the Poker logo over
pocket aces and a stack going all in (tools/boxart.py: the house style).
`chgame boxart` redraws it; edit this, not the PNG."""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import boxart as bx  # noqa: E402
import pixkit as pk  # noqa: E402


def draw():
    fb = bx.canvas()
    bx.felt(fb, bx.FELT, bx.FELT_DK)
    bx.logo(fb, bx.load_logo(HERE / "art" / "logo.txt"), 8)
    cards = bx.layer()
    bx.card(cards, 0, 0, "A", "h")
    bx.card(cards, 30, 0, "A", "s")
    bx.blit(fb, cards, 12, 34, 2, (0, 0, 23, 29))
    bx.blit(fb, cards, 50, 42, 2, (30, 0, 23, 29))
    bx.chips(fb, 106, 120, 400, 6)
    return fb


if __name__ == "__main__":
    print(bx.save(draw(), HERE.parent / "docs" / "cart.png"))
