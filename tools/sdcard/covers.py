"""The casino card's covers for the visual menu (tools/sdcard/casino.json):
the cart's cover, which is the splash at power-on, and one cover per genre
folder. Each folder is a big word on the dark (the Arduboy FX's category
screens are a word on black) over its charm, so a folder never looks like a
game; the games are on felt (each game's tools/cart.py).

    python tools/sdcard/covers.py [--sheet OUT.png]     -> tools/sdcard/art/*.png

Edit this and run it, or edit the PNGs and drop the folder from GENRES here.
"""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))                  # the repository's tools/
import boxart as bx  # noqa: E402
import menuart  # noqa: E402
import pixkit as pk  # noqa: E402
from boxart import INK, WHITE, NAVY, GOLD, WOOD, RED, WINE, FELT, FELT_DK, FX_A, CREAM, GREY  # noqa: E402

ART = HERE / "art"


def logo(fb, y):
    """The CHGAME logo of the menu's default picture, in #FF00FF (it turns)."""
    rows = menuart.chg_logo()
    w = len(rows[0])
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch == "#":
                fb.pixel(64 - w // 2 + i, y + j, FX_A)
    return y + len(rows)


def cover():
    """The splash: CHGAME CASINO over a hand of cards, dice and chips, on the
    cart cover's black."""
    fb = bx.cart()
    y = logo(fb, 9)
    bx.title(fb, "CASINO", y + 4, scale=2)
    cards = bx.layer()
    for k, (r, s) in enumerate((("A", "s"), ("K", "h"), ("Q", "d"))):
        bx.card(cards, k * 30, 0, r, s)
    for k, x in enumerate((30, 50, 70)):
        bx.blit(fb, cards, x, 62 + abs(k - 1) * 3, 1, (k * 30, 0, 23, 29))
    bx.die(fb, 12, 74, 5, 14)
    bx.die(fb, 22, 88, 3, 14)
    pk.chip_stack(fb, 108, 106, 160, 7)
    pk.chip_stack(fb, 94, 110, 30, 3)
    return fb


def word_cover(word, charm):
    """A folder's cover: its name, big, over its charm, on the navy gradient,
    all in the folders' blues."""
    fb = bx.folder()
    charm(fb)
    bx.title(fb, word, 16, scale=2)
    bx.blues(fb)
    return fb


def cards_charm(fb):
    cards = bx.layer()
    for k, (r, s) in enumerate((("A", "s"), ("A", "h"), ("A", "d"), ("A", "c"))):
        bx.card(cards, k * 30, 0, r, s, shadow=INK)
    for k in range(4):
        bx.blit(fb, cards, 17 + k * 22, 62 + (k % 2) * 4, 1, (k * 30, 0, 23, 29))


def recipe(name):
    """A program's box-art recipe (its tools/cart.py) as a module, for its charms."""
    import importlib.util
    f = bx.recipes()[name] / "tools" / "cart.py"
    spec = importlib.util.spec_from_file_location(f"cart_{name}", f)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def casino_charm(fb):
    for k, amount in enumerate((60, 450, 135)):        # (chip_stack takes an amount: the chips that make it)
        bx.chips(fb, 34 + k * 30, 118 - (k == 1) * 4, amount, 8)


def dice_charm(fb):
    bx.die(fb, 26, 70, 5, 32, body=bx.RED, pip=bx.WHITE, shade=bx.WINE)
    bx.die(fb, 70, 80, 2, 32)


def board_charm(fb):
    chess = recipe("CHChess")
    lay = bx.layer()
    lay.sprite(bx.piece(chess.PIECES / "king.png"), 0, 0)
    bx.blit(fb, lay, 26, 66, 2, (0, 0, 13, 26))
    four = recipe("CHFour")
    lay = bx.layer()
    lay.sprite(four.DISC, 0, 0, [four.SIDES[0].get(i, i) for i in range(16)])
    bx.blit(fb, lay, 64, 76, 2, (0, 0, 20, 20))


def tiles_charm(fb):
    dom = recipe("CHDominoes")
    dom.domino(fb, 22, 66, 5, 2, 26)
    mj = recipe("CHMahjong")
    lay = bx.layer()
    mj.tile(lay, 1, 1, mj.faces()["dragons"][0])
    bx.blit(fb, lay, 62, 66, 2, (0, 0, 20, 29))


def words_charm(fb):
    for k, ch in enumerate("ABC"):
        bx.tile(fb, 25 + k * 27, 82 - (k == 1) * 6, ch, None, 24, 25)


def apps_cover():
    """The apps' folder: a folder like the others (the navy gradient), wearing
    the apps' secret-agent look: their green lettering, the corner marks and
    scan lines of their screens, the SD card and a wireframe. Two styles mixed,
    on purpose: what a cart of a user's own looks like next to ours."""
    sd = recipe("CHSDtoUSB")
    fb = bx.folder()
    fb.rect(2, 2, 124, 124, bx.CYAN)                    # the folders' frame (blues() makes theirs cyan)
    for y in range(78, 124, 6):                         # the scan lines, over the navy band
        fb.hline(4, y, 120, INK)
    sd.corners(fb, 6, 6, 116, 116, bx.FELT_LT, 8)
    bx.title(fb, "APPS", 16, scale=2, colours=sd.GREEN, shadow=INK)
    sd.sd_card(fb, 22, 64)
    stl = recipe("CHStlView")
    v, edges = stl.icosahedron()
    pts = [stl.project(q, 0.45, 0.6, 90, 88, 13) for q in v]
    for i, j in edges:
        fb.line(round(pts[i][0]), round(pts[i][1]), round(pts[j][0]), round(pts[j][1]), bx.FELT_LT)
    return fb


GENRES = {
    "CARDS": cards_charm,
    "CASINO": casino_charm,
    "DICE": dice_charm,
    "BOARD": board_charm,
    "TILES": tiles_charm,
    "WORDS": words_charm,
}


def main(argv):
    ART.mkdir(exist_ok=True)
    out = [bx.save(cover(), ART / "cover.png")]
    for name, charm in GENRES.items():
        out.append(bx.save(word_cover(name, charm), ART / f"{name.lower()}.png"))
    out.append(bx.save(apps_cover(), ART / "apps.png"))
    for p in out:
        print(p)
    if "--sheet" in argv:
        print(bx.sheet(out, argv[argv.index("--sheet") + 1], scale=2, cols=4))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
