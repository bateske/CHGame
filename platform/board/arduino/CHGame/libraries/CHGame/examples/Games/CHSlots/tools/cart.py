"""docs/cart.png, the game's picture in the visual menu: the Slots logo over
a machine's window, three sevens on the line (tools/boxart.py: the house
style; the symbols are the game's own, tools/art/symbols.png). `chgame
boxart` redraws it; edit this, not the PNG."""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import boxart as bx  # noqa: E402
from boxart import INK, WHITE, RED, GOLD, WOOD, WINE, CREAM, GREY  # noqa: E402

SYMBOLS = HERE / "art" / "symbols.png"
CELL, SEVEN, CHERRY, BELL = 22, 4, 0, 2               # tools/assets.py CLASSIC: cherry lemon bell bar seven ...


def symbol(k, row=0):
    return bx.rgb_sprite(SYMBOLS, (k * CELL, row * CELL, CELL, CELL))


def draw():
    fb = bx.canvas()
    bx.felt(fb, WINE, INK)
    bx.logo(fb, bx.load_logo(HERE / "art" / "logo.txt"), 7)
    fb.fill_round(8, 34, 112, 78, 6, INK)                # the machine
    fb.fill_round(10, 35, 108, 74, 5, GOLD)
    fb.fill_round(12, 37, 104, 70, 4, WOOD)
    reels = bx.layer()
    for k, s in enumerate((CHERRY, SEVEN, BELL, SEVEN, SEVEN, SEVEN, BELL, CHERRY, SEVEN)):
        reels.sprite(symbol(s), (k % 3) * 24 + 1, (k // 3) * 24 + 1)
    for k in range(3):
        x = 16 + k * 33
        fb.fill_rect(x, 40, 30, 64, CREAM)
        fb.rect(x - 1, 39, 32, 66, INK)
        bx.blit(fb, reels, x + 4, 42, 1, (k * 24, 0, 24, 72))
    fb.fill_rect(13, 70, 102, 2, RED)                    # the pay line
    fb.fill_rect(13, 72, 102, 1, INK)
    return fb


if __name__ == "__main__":
    print(bx.save(draw(), HERE.parent / "docs" / "cart.png"))
