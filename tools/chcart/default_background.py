"""Draws spec/assets/menu-default.png, the menu's background on every card the
tools prepare when a cart has none of its own (chcart/runtime.py):

    python tools/chcart/default_background.py [--ttf DejaVuSans-Bold.ttf]

Black; the CHGAME logo, a full-resolution one-bit rendering of DejaVu Sans
Bold, in #FF00FF (the rainbow: spec/card.md) above a rainbow rule; the keys
in the menu's grey, in the bootloader's own 5x7 font, at the foot. The list
draws its ten rows over y 20-119. DejaVu is freely redistributable
(https://dejavu-fonts.github.io/License.html).
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

from PIL import Image, ImageDraw, ImageFont

REPO = pathlib.Path(__file__).resolve().parents[2]
OUT = REPO / "spec" / "assets" / "menu-default.png"
FONT57 = REPO / "platform" / "bootloader" / "src" / "font5x7.h"
sys.path.insert(0, str(REPO / "tools"))
from fonts.serif import find_ttf  # noqa: E402

RAINBOW, GREY, BLACK = (255, 0, 255), (128, 128, 128), (0, 0, 0)


def glyphs57():
    src = FONT57.read_text()
    body = src[src.index("font5x7[(FONT5X7_LAST - 31) * 5] = {"):].split("};")[0]
    return [int(v, 16) for v in re.findall(r"0x([0-9A-Fa-f]{2})", body)]


def text57(d, x, y, s, fill, g):
    for ch in s:
        col = g[(ord(ch) - 32) * 5:(ord(ch) - 32) * 5 + 5]
        for c in range(5):
            for r in range(7):
                if col[c] >> r & 1:
                    d.point((x + c, y + r), fill=fill)
        x += 6


def draw(ttf):
    im = Image.new("RGB", (128, 128), BLACK)
    d = ImageDraw.Draw(im)
    logo = Image.new("1", (128, 24), 0)
    ld = ImageDraw.Draw(logo)
    ld.fontmode = "1"                           # one bit: no grey edges
    ld.text((0, 0), "CHGAME", font=ImageFont.truetype(ttf, 21), fill=1)
    logo = logo.crop(logo.getbbox())
    im.paste(RAINBOW, ((128 - logo.size[0]) // 2, (17 - logo.size[1]) // 2), logo)
    d.line([(0, 17), (127, 17)], fill=RAINBOW)
    text57(d, 2, 120, "A:PLAY B:BACK", GREY, glyphs57())
    return im


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ttf", help="DejaVuSans-Bold.ttf (found in the usual font folders otherwise)")
    a = ap.parse_args(argv)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    draw(find_ttf("DejaVuSans-Bold.ttf", a.ttf)).save(OUT, optimize=True)
    print(OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
