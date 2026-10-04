"""docs/cart.png, the app's picture in the visual menu: SD CARD READER in the
app's green, an SD card linked to a USB plug, the corner marks of its screen
(tools/boxart.py: the house style, in the apps' secret-agent colours).
`chgame boxart` redraws it; edit this, not the PNG."""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import boxart as bx  # noqa: E402
from boxart import INK, WHITE, SILVER, GOLD, NAVY, FELT_DK, FELT, FELT_LT, GREY  # noqa: E402

GREEN = (WHITE, FELT_LT, FELT)


def corners(fb, x, y, w, h, c, n=6):
    for cx, cy, dx, dy in ((x, y, 1, 1), (x + w - 1, y, -1, 1), (x, y + h - 1, 1, -1), (x + w - 1, y + h - 1, -1, -1)):
        fb.hline(min(cx, cx + dx * (n - 1)), cy, n, c)
        fb.vline(cx, min(cy, cy + dy * (n - 1)), n, c)


def sd_card(fb, x, y):
    """A microSD card, 34 x 44: the notch, the contacts, a label."""
    fb.fill_rect(x, y + 6, 34, 38, INK)
    fb.fill_rect(x + 8, y, 26, 7, INK)
    fb.fill_rect(x + 1, y + 7, 32, 36, SILVER)
    fb.fill_rect(x + 9, y + 1, 24, 7, SILVER)
    for k in range(5):
        fb.fill_rect(x + 11 + k * 4, y + 2, 2, 7, GOLD)
    fb.fill_rect(x + 4, y + 16, 26, 22, NAVY)
    rows = bx.text_rows("SD")
    bx.lettering(fb, rows, x + 17 - len(rows[0]) // 2, y + 21, colours=GREEN, shadow=INK)


def usb_plug(fb, x, y):
    """A USB-A plug, 20 x 40, its cable going left."""
    fb.fill_rect(x + 2, y, 16, 14, INK)
    fb.fill_rect(x + 3, y + 1, 14, 12, SILVER)
    fb.fill_rect(x + 6, y + 4, 3, 3, INK)
    fb.fill_rect(x + 11, y + 4, 3, 3, INK)
    fb.fill_rect(x, y + 14, 20, 20, INK)
    fb.fill_rect(x + 1, y + 15, 18, 18, GREY)
    fb.fill_rect(x + 8, y + 34, 4, 6, INK)


def draw():
    fb = bx.canvas(INK)
    for y in range(28, 124, 8):                         # the scan lines of its screen
        fb.hline(4, y, 120, FELT_DK)
    corners(fb, 4, 4, 120, 120, FELT_LT, 8)
    bx.title(fb, "SD CARD", 8, scale=1, colours=GREEN, shadow=FELT_DK)
    bx.title(fb, "READER", 22, scale=1, colours=GREEN, shadow=FELT_DK)
    sd_card(fb, 16, 52)
    usb_plug(fb, 92, 50)
    for k in range(0, 34, 6):                           # the data, flowing
        fb.fill_rect(54 + k, 72, 4, 3, FELT_LT)
    fb.line(52, 73, 49, 70, FELT_LT)
    fb.line(52, 73, 49, 76, FELT_LT)
    return fb


if __name__ == "__main__":
    print(bx.save(draw(), HERE.parent / "docs" / "cart.png"))
