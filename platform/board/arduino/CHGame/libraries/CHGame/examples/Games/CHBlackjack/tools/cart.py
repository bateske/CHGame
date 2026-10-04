"""docs/cart.png, the game's picture in the visual menu: the BlackJack logo
over an ace and a king, chips at their feet (tools/boxart.py: the house
style). `chgame boxart` redraws it; edit this, not the PNG."""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import boxart as bx  # noqa: E402
import pixkit as pk  # noqa: E402


def draw():
    fb = bx.canvas()
    bx.felt(fb)
    bx.logo(fb, bx.logo_from_assets(HERE.parent, "LOGO", 104), 7)
    cards = bx.layer()
    bx.card(cards, 0, 0, "A", "s")
    bx.card(cards, 30, 0, "K", "h")
    bx.blit(fb, cards, 15, 31, 2, (0, 0, 23, 29))
    bx.blit(fb, cards, 61, 39, 2, (30, 0, 23, 29))
    bx.chips(fb, 24, 121, 160, 4)
    bx.chips(fb, 106, 121, 35, 2)
    return fb


if __name__ == "__main__":
    print(bx.save(draw(), HERE.parent / "docs" / "cart.png"))
