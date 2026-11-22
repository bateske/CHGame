#!/usr/bin/env python3
"""The repository's cart and its SD cards, one per board.

    chgame card                          build every program for every installed board;
                                         write the cart and a card per board
    chgame card --no-build               use the release builds already there (build/<board>/release)
    chgame card --image                  also a FAT32 card image per board, out/sdcard-<board>.img
    chgame card --image F.img            ... named F-<board>.img (or a path with {board} in it)
    chgame card --only CHFour CHChess    just these programs
    chgame --board rev0 card             one board's alone (or --board here)

The programs, their order and their genre folders are tools/sdcard/casino.json,
a cart recipe (`chgame cart build`, tools/chcart/cli.py); each sketch's
chgame.json gives its title, details, SD files and picture. Each program is
built for every board the installed CHGame core has (tools/device.py; a board
it lacks is skipped, and said so). The cart, out/CHGame-Casino.chgame,
carries every one of those boards' binaries. A card is for one board (its CHG
files carry that board's binaries and target: spec/card.md), so each board
gets its own, made from the cart (tools/chcart/runtime.py: GAMES/ with the
CHG files, MENU.IDX, MENU.BG, COVER.PIC and SYSTEM.PIC, and the data files
the games read): out/sdcard-<board>/, side by side, each a card's root. Copy
the CONTENTS of the board's folder to the root of a FAT16/FAT32 card (for
example through the CHGame's SD CARD READER, in the menu's APPS folder), or
`chgame cart deploy out/CHGame-Casino.chgame --card E:\\ --device <board>`.

The same inputs give the same bytes, so a card can be rebuilt and compared.
"""
from __future__ import annotations

import argparse
import os
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
import chgpack  # noqa: E402
from chcart import cli, runtime, zipio  # noqa: E402
from chcart.model import CartError  # noqa: E402

RECIPE = pathlib.Path(__file__).with_name("casino.json")
PLATFORM = REPO / "platform" / "board" / "arduino" / "CHGame"
CART = REPO / "out" / "CHGame-Casino.chgame"
CARD_DIR = REPO / "out" / "sdcard-{board}"          # a card's root per board
CARD_IMAGE = REPO / "out" / "sdcard-{board}.img"    # --image without a path


def per_board(template, board, several=True):
    """A path for one board's card: {board} in `template` replaced; without
    one, -<board> added to its name when there are several boards."""
    t = str(template)
    if "{board}" in t:
        return pathlib.Path(t.replace("{board}", board))
    if not several:
        return pathlib.Path(t)
    p = pathlib.Path(t)
    return p.with_name(f"{p.stem}-{board}{p.suffix}")


def programs(only=None) -> list[str]:
    """The recipe's sketch names, in menu order."""
    names = cli.recipe_sketches(RECIPE)
    return [n for n in names if n in only] if only else names


def folder(name: str, platform_dir: pathlib.Path = PLATFORM) -> pathlib.Path:
    """A program's sketch folder: in this repository, or in an installed board
    package (tools/release/acceptance.py builds the release's card from that)."""
    return cli._in_platform(name, platform_dir)


def make_cart(only=None, binary=None, platform_dir: pathlib.Path = PLATFORM, version: str = "", boards=None,
              build=True):
    """The casino cart, each program with a binary for every board in
    `boards` (default: every board the installed core has).
    binary(sketch folder, board) gives each release .bin (a callback of the
    folder alone: rev0's); None builds them (tools/device.py), or with
    build=False takes each build/<board>/release .bin as it is (a missing
    one is a CartError that says how to build it)."""
    cart = cli.build_recipe(RECIPE, build=build and binary is None, binary=binary, only=only,
                            platform_dir=None if platform_dir == PLATFORM else platform_dir, devices=boards)
    cart.version = version or cart.version
    return cart


def make_card(cart, out: pathlib.Path, image: str | None = None, device: str = "rev0") -> dict:
    """The cart's card for `device` into out/ (replacing it), a table of what
    is on it, and a FAT32 image if asked. Returns {card path: bytes}."""
    files = runtime.prepare(cart, device, log=print)
    cart = runtime.for_device(cart, device)[0]      # (what the card holds)
    runtime.write_folder(files, out)
    print(f"{'game':16s} {'file':24s} {'image':>7s}  crc32     title")
    for g, path in zip_games(cart, files, device):
        i = chgpack.parse(files[path])
        print(f"{g.id:16s} {path:24s} {i['payload_bytes']:7d}  {i['payload_crc32']:08x}  {g.title}")
    print(f"\n{len(cart.games)} games, {len(files)} files in {out} (a {device} card)")
    if image:
        pathlib.Path(image).parent.mkdir(parents=True, exist_ok=True)
        runtime.write_image(files, image)
        print(f"card image: {image}")
    return files


def zip_games(cart, files, device="rev0"):
    """(game, its CHG file's card path) on `device`'s card, matched by the CHG's payload."""
    by_payload = {}
    for p, data in files.items():
        if p.endswith(".CHG"):
            by_payload.setdefault(data[512:512 + chgpack.parse(data)["payload_bytes"]], p)   # (a picture may follow)
    return [(g, by_payload[chgpack.pad_image(g.binaries[device])]) for g in cart.games]


def main(argv=None, boards=None) -> int:
    """boards: `chgame --board B card`'s board (default every board the
    installed core has)."""
    import device                           # tools/device.py
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(CARD_DIR),
                    help="the card folders, {board} the board's name (default out/sdcard-{board})")
    ap.add_argument("--cart", default=str(CART), help="where the .chgame goes")
    ap.add_argument("--image", nargs="?", const=str(CARD_IMAGE), metavar="F.img",
                    help="also a FAT32 card image per board: out/sdcard-<board>.img, or F-<board>.img "
                         "(or F with {board} in it)")
    ap.add_argument("--no-build", action="store_true", help="use the existing build/<board>/release/*.ino.bin")
    ap.add_argument("--only", nargs="*", help="sketch names to include (default: all)")
    ap.add_argument("--board", action="append", choices=device.BOARDS,
                    help="only this board (again for more; default every board the installed core has)")
    a = ap.parse_args(argv)
    boards = a.board or boards or device.installed_boards()
    if not boards:
        raise SystemExit(device.not_installed(device.BOARDS[0]))     # no CHGame core (or no arduino-cli)
    for b in boards:
        if not device.installed(b):
            print(device.not_installed(b), file=sys.stderr)
            return 1
    try:
        return write(a, boards)
    except CartError as e:
        print(e, file=sys.stderr)
        return 1


def write(a, boards) -> int:
    """main()'s work: the cart and each board's card (and image), as `a` asks."""
    cart = make_cart(a.only, boards=boards, build=not a.no_build)
    pathlib.Path(a.cart).parent.mkdir(parents=True, exist_ok=True)
    data = zipio.write(cart, a.cart)
    print(f"{a.cart}: {len(cart.games)} games for {', '.join(boards)}, {len(data)} B")
    written = [f"{a.cart}  (the cart: {', '.join(boards)})"]
    for b in boards:
        out = per_board(a.out, b, len(boards) > 1)
        image = str(per_board(a.image, b, len(boards) > 1)) if a.image else None
        print(f"\n== the {b} card: {out}")
        make_card(cart, out, image, b)
        written.append(f"{out}{os.sep}  (a {b} card: copy its contents to the card's root)")
        if image:
            written.append(f"{image}  (the {b} card's FAT32 image)")
    old = REPO / "out" / "sdcard"
    if a.out == str(CARD_DIR) and old.is_dir():
        print(f"\nnote: {old} is from before cards were per board: delete it")
    print("\nwritten:\n" + "\n".join("  " + w for w in written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
