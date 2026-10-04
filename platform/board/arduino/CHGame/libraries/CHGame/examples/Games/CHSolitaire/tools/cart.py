"""docs/cart.png, the game's picture in the visual menu: the Solitaire logo
over a column of the tableau, red on black down from the king, beside the
deck's back (tools/boxart.py: the house style). `chgame boxart` redraws it;
edit this, not the PNG."""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import boxart as bx  # noqa: E402

BACK = HERE / "art" / "backs" / "cherry.txt"


def back(fb, x, y):
    """The deck, face down: a card's frame round tools/art/backs' cherry."""
    rows = [r for r in BACK.read_text(encoding="utf-8").splitlines() if r.strip() and not r.startswith("#")]
    fb.vline(x + bx.CARD_W, y + 2, bx.CARD_H - 1, bx.FELT_DK)
    fb.hline(x + 2, y + bx.CARD_H, bx.CARD_W - 1, bx.FELT_DK)
    fb.panel(x, y, bx.CARD_W, bx.CARD_H, 2, bx.WHITE, bx.INK)
    fb.fill_rect(x + 2, y + 2, bx.CARD_W - 4, bx.CARD_H - 4, bx.WINE)
    w = max(len(r) for r in rows)
    bx.letters(fb, rows, x + (bx.CARD_W - w) // 2, y + (bx.CARD_H - len(rows)) // 2)


def draw():
    fb = bx.canvas()
    bx.felt(fb, bx.FELT, bx.FELT_DK)
    bx.logo(fb, bx.load_logo(HERE / "art" / "logo.txt"), 7)
    cards = bx.layer()
    back(cards, 0, 0)
    for k, (r, s) in enumerate((("K", "s"), ("Q", "h"), ("J", "c"))):
        bx.card(cards, 30, k * 9, r, s)
    bx.blit(fb, cards, 10, 38, 2, (0, 0, 23, 29))
    bx.blit(fb, cards, 62, 31, 2, (30, 0, 23, 47))
    return fb


if __name__ == "__main__":
    print(bx.save(draw(), HERE.parent / "docs" / "cart.png"))
