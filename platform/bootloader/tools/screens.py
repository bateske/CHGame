#!/usr/bin/env python3
"""Rebuild the menu pictures in docs/ from the native suite's panel dumps.

    python3 test/native/run_tests.py -k boot     # writes test/native/build/frames/
    python3 tools/screens.py

docs/menu.png          the menu with the casino card (out/sdcard.img: `chgame card --image`)
docs/menu_screens.png  the menu with a game installed, and three messages
docs/menu_cards.png    the menu on the default picture (the casino card), on a
                       picture of a card's own, and on a card with none
docs/menu_rainbow.gif  the rainbow colour turning on the casino card (4 s)
docs/visual.png        the visual menu on the casino card: the splash, a folder's cover, games
docs/visual_screens.png  installing, the about page, an error and USB upload (built-in screens)
docs/visual_cards.png  every cover and game picture of the casino card, as the visual menu shows them
"""
import subprocess
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parents[1]
FRAMES = HERE / "test" / "native" / "build" / "frames"
DOCS = HERE / "docs"
GAP, GAP_RGB = 8, (24, 24, 24)


def frame(name):
    return Image.open(FRAMES / f"{name}.png").convert("RGB").resize((256, 256), Image.NEAREST)


def strip(names):
    out = Image.new("RGB", (len(names) * (256 + GAP) - GAP, 256), GAP_RGB)
    for i, n in enumerate(names):
        out.paste(frame(n), (i * (256 + GAP), 0))
    return out


def main():
    frame("real_menu").save(DOCS / "menu.png")
    strip(["real_menu_installed", "error_box", "usb_notice", "install_failed"]).save(DOCS / "menu_screens.png")
    strip(["real_menu", "cart_menu", "menu_installed"]).save(DOCS / "menu_cards.png")
    # the boot test binary in its picture mode, on the casino card
    native = HERE / "test" / "native" / "build"
    # (through run_tests' launcher: on Windows the binary is a Linux one, run under WSL)
    import sys
    sys.path.insert(0, str(native.parent))
    import run_tests
    argv = [run_tests.hostpath(native / "boot"), run_tests.hostpath(native / "real_manifest.txt"),
            run_tests.hostpath(FRAMES), "anim"]
    subprocess.run((run_tests.wsl_cmd() if run_tests.WSL else []) + argv, check=True, capture_output=True)
    anim = []
    for i in range(32):
        ppm = FRAMES / f"anim_{i:02d}.ppm"
        anim.append(Image.open(ppm).convert("RGB").resize((256, 256), Image.NEAREST))
        ppm.unlink()
    anim[0].save(DOCS / "menu_rainbow.gif", save_all=True, append_images=anim[1:], duration=120, loop=0)
    print("docs/menu.png, docs/menu_screens.png, docs/menu_cards.png, docs/menu_rainbow.gif")
    visual()


def grid(names, cols, scale=1):
    s = 128 * scale
    rows = (len(names) + cols - 1) // cols
    out = Image.new("RGB", (cols * (s + GAP) - GAP, rows * (s + GAP) - GAP), GAP_RGB)
    for i, n in enumerate(names):
        im = Image.open(FRAMES / f"{n}.png").convert("RGB").resize((s, s), Image.NEAREST)
        out.paste(im, ((i % cols) * (s + GAP), (i // cols) * (s + GAP)))
    return out


def visual():
    """The visual menu's pictures (test_visual.c, its real-card run)."""
    strip(["v_real_splash", "v_real_cover_0", "v_real_game_00", "v_real_game_04"]).save(DOCS / "visual.png")
    strip(["v_real_installing", "v_real_about", "v_error_icon", "v_usb_notice"]).save(DOCS / "visual_screens.png")
    covers = ["v_real_splash"] + [f"v_real_cover_{k}" for k in range(7)]
    games = sorted(p.stem for p in FRAMES.glob("v_real_game_*.png"))
    grid(covers + games, 8).save(DOCS / "visual_cards.png")
    print("docs/visual.png, docs/visual_screens.png, docs/visual_cards.png")


if __name__ == "__main__":
    main()
