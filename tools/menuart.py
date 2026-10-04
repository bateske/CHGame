"""The visual menu's own pictures: the defaults card preparation uses
(spec/card.md) when a cart has none of its own.

    spec/assets/cover-default.png    the cart's cover, the splash at power-on
    spec/assets/about-default.png    the about page (B at the top): how the menu works
    spec/assets/system/*.png         the screens SYSTEM.PIC carries after the about page:
                                     installed (the program in flash, when no card entry
                                     holds it), game (a game without a picture), folder (a
                                     folder without a cover), error-1 .. error-5

They are plain PNGs: edit them in any paint program (the picture rule:
128x128, at most 11 colours besides #FF00FF and the menu's four; `chgame
picture` converts any image). This script drew the first ones and draws only
the missing ones, so it never overwrites an edit; --force redraws them all.

    python tools/menuart.py [--force] [--sheet out/menuart.png]
"""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import boxart as bx  # noqa: E402
import pixkit as pk  # noqa: E402
from boxart import INK, WHITE, SILVER, RED, WINE, GOLD, WOOD, BLUE, NAVY, CYAN, FX_A, CREAM, GREY  # noqa: E402

ASSETS = HERE.parent / "spec" / "assets"
SYSTEM = ASSETS / "system"
LIST_BG = ASSETS / "menu-default.png"

# The errors: what install.h's codes mean to a player (docs/sd-menu.md)
ERRORS = {
    1: ("CARD ERROR", ["THE CARD STOPPED", "ANSWERING.", "", "RESEAT IT AND", "TRY AGAIN."]),
    2: ("FILE DAMAGED", ["THE GAME'S FILE IS", "DAMAGED. NOTHING", "WAS ERASED.", "", "COPY IT AGAIN."]),
    3: ("NOT A GAME", ["THE FILE HOLDS A", "BOOTLOADER, NOT A", "GAME. NOTHING WAS", "ERASED."]),
    4: ("INSTALL FAILED", ["THE CARD FAILED", "PARTWAY. THE OLD", "GAME IS GONE, BUT", "NO HALF GAME RUNS.", "PICK A GAME AGAIN."]),
    5: ("CAN'T INSTALL", ["DAMAGED, MADE FOR", "ANOTHER BOARD, OR", "FOR A NEWER MENU.", "NOTHING WAS", "ERASED."]),
}


def chg_logo():
    """The CHGAME logo of the list menu's default picture: its #FF00FF pixels
    in the top rows, as 1 bpp rows."""
    from PIL import Image
    im = Image.open(LIST_BG).convert("RGB")
    rows = ["".join("#" if im.getpixel((x, y)) == (255, 0, 255) else "." for x in range(128)) for y in range(20)]
    rows = [r for r in rows if "#" in r]
    a = min(r.index("#") for r in rows)
    b = max(r.rindex("#") for r in rows)
    return [r[a:b + 1] for r in rows]


def frame(fb, c=GOLD, body=None):
    if body is not None:
        fb.clear(body)
    fb.rect(2, 2, 124, 124, c)


def cover():
    fb = bx.canvas(INK)
    rows = chg_logo()
    w, h = len(rows[0]), len(rows)
    y = 64 - h // 2 - 6
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch == "#":
                fb.pixel(64 - w // 2 + i, y + j, FX_A)
    fb.hline(64 - w // 2, y + h + 3, w, FX_A)
    bx.small(fb, "GAMES ON THE SD CARD", y + h + 10, GREY)
    return fb


def key(fb, x, y, label, c=RED):
    """A round button with its letter."""
    fb.fill_ellipse(x + 5, y + 5, 5, 5, INK)
    fb.fill_ellipse(x + 5, y + 4, 5, 5, c)
    fb.text57(x + 3, y + 1, label, CREAM)


def dpad(fb, x, y, lit):
    """A D-pad, 21 pixels square; `lit`: the arms drawn in gold ('ud', 'lr')."""
    fb.fill_rect(x + 7, y, 7, 21, GREY)
    fb.fill_rect(x, y + 7, 21, 7, GREY)
    if "ud" in lit:
        fb.fill_rect(x + 8, y + 1, 5, 6, GOLD)
        fb.fill_rect(x + 8, y + 14, 5, 6, GOLD)
    if "lr" in lit:
        fb.fill_rect(x + 1, y + 8, 6, 5, GOLD)
        fb.fill_rect(x + 14, y + 8, 6, 5, GOLD)


def select_key(fb, x, y):
    """SELECT: a grey pill."""
    fb.fill_round(x, y + 3, 19, 7, 3, INK)
    fb.fill_round(x, y + 2, 19, 7, 3, GREY)


def about():
    fb = bx.canvas(NAVY)
    frame(fb)
    bx.title(fb, "HOW IT WORKS", 7, scale=1)
    y = 22
    dpad(fb, 8, y, "ud")
    bx.small(fb, "GAMES IN", y + 2, CREAM, 36)
    bx.small(fb, "A FOLDER", y + 11, CREAM, 36)
    y += 23
    dpad(fb, 8, y, "lr")
    bx.small(fb, "FOLDERS", y + 2, CREAM, 36)
    bx.small(fb, "SIDE BY SIDE", y + 11, CREAM, 36)
    y += 24
    key(fb, 13, y, "A")
    bx.small(fb, "PLAY, OPEN", y + 2, CREAM, 36)
    key(fb, 13, y + 12, "B", BLUE)
    bx.small(fb, "BACK", y + 14, CREAM, 36)
    select_key(fb, 9, y + 24)
    bx.small(fb, "HOME, THIS PAGE", y + 26, CREAM, 36)
    bx.small(fb, "IN A GAME, HOLD", 106, GOLD)
    bx.small(fb, "START 3 S: BACK HERE", 115, GOLD)
    return fb


def cartridge(fb, x, y, body=SILVER, label=GOLD):
    """A cartridge 40x48: label, grip and contacts."""
    fb.fill_round(x, y, 40, 48, 3, INK)
    fb.fill_round(x + 1, y + 1, 38, 46, 2, body)
    fb.fill_rect(x + 5, y + 5, 30, 24, INK)
    fb.fill_rect(x + 6, y + 6, 28, 22, label)
    for k in range(5):
        fb.fill_rect(x + 7 + k * 6, y + 40, 3, 6, GOLD)
    fb.hline(x + 6, y + 33, 28, GREY)
    fb.hline(x + 6, y + 35, 28, GREY)


def installed():
    fb = bx.canvas(INK)
    frame(fb, GOLD)
    cartridge(fb, 44, 14, SILVER, CYAN)
    fb.fill_rect(58, 22, 12, 12, INK)                  # a chip on the label
    for k in range(4):
        fb.pixel(56, 24 + k * 3, INK)
        fb.pixel(71, 24 + k * 3, INK)
    bx.title(fb, "INSTALLED", 70, scale=1)
    bx.small(fb, "A PROGRAM IN FLASH,", 92, CREAM)
    bx.small(fb, "NOT ON THE CARD", 101, CREAM)
    bx.small(fb, "A: RUN IT", 113, GOLD)
    return fb


def game():
    fb = bx.canvas(INK)
    frame(fb, GREY)
    cartridge(fb, 44, 16, SILVER, GREY)
    fb.text57(61, 28, "?", INK)
    bx.title(fb, "NO PICTURE", 72, scale=1)
    bx.small(fb, "A GAME WITHOUT ITS", 94, CREAM)
    bx.small(fb, "PICTURE", 103, CREAM)
    bx.small(fb, "A: PLAY", 113, GOLD)
    return fb


def folder_art(fb, x, y, body=GOLD, dark=WOOD):
    """A folder 56x40."""
    fb.fill_round(x, y, 22, 10, 2, dark)
    fb.fill_round(x, y + 5, 56, 35, 3, dark)
    fb.fill_round(x + 2, y + 9, 52, 29, 2, body)
    fb.hline(x + 4, y + 13, 48, WHITE)


def folder():
    fb = bx.folder()                                   # in a folder's place: a folder's look
    folder_art(fb, 36, 18)
    bx.title(fb, "FOLDER", 70, scale=1)
    bx.small(fb, "WITHOUT A COVER", 94, CREAM)
    bx.small(fb, "A: OPEN IT", 113, GOLD)
    bx.blues(fb)
    return fb


def error(n):
    head, lines = ERRORS[n]
    fb = bx.canvas(WINE)
    frame(fb, RED)
    fb.fill_rect(3, 3, 122, 22, RED)
    bx.title(fb, f"ERROR {n}", 7, scale=1, fill=CREAM, outline=INK, shadow=WINE)
    bx.small(fb, head, 32, GOLD)
    for k, ln in enumerate(lines):
        bx.small(fb, ln, 46 + k * 10, CREAM)
    bx.small(fb, "ANY KEY: BACK", 112, SILVER)
    return fb


PICTURES = {
    ASSETS / "cover-default.png": cover,
    ASSETS / "about-default.png": about,
    SYSTEM / "installed.png": installed,
    SYSTEM / "game.png": game,
    SYSTEM / "folder.png": folder,
    **{SYSTEM / f"error-{n}.png": (lambda n=n: error(n)) for n in ERRORS},
}


def main(argv):
    force = "--force" in argv
    for path, draw in PICTURES.items():
        if path.exists() and not force:
            print(f"kept {path.relative_to(HERE.parent)}")
            continue
        bx.save(draw(), path)
        print(f"drew {path.relative_to(HERE.parent)}")
    if "--sheet" in argv:
        out = argv[argv.index("--sheet") + 1]
        print(bx.sheet(list(PICTURES), out, scale=2, cols=5))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
