"""`chgame cart ...` and `chgame export`: .chgame files from the command line.

    chgame export [--no-build] [--out F]          in a sketch folder: build/<Name>.chgame
    chgame cart info PKG [--json]                 the games, their files, the warnings
    chgame cart verify PKG ...                    every rule of spec/chgame.md (exit 1 on an error)
    chgame cart extract PKG DIR                   the files, as laid out inside
    chgame cart new OUT ITEM ... [--title T ...]  a cart from .chgame/.bin/.hex/.chg files and sketches
    chgame cart build RECIPE.json [OUT]           a cart from a recipe (games named by sketch)
    chgame cart add PKG ITEM ... [--folder F] [--at N]
    chgame cart remove PKG ID ...
    chgame cart order PKG ID ...                  these first, in this order; the rest after
    chgame cart set PKG [--game ID] KEY=VALUE ... (KEY= clears; title, folder, author, ...)
    chgame cart launch PKG ID|none                the game started at power-on
    chgame cart background PKG PNG|none [--folder F]
    chgame cart prepare PKG OUTDIR [--image IMG]  the card's files (spec/card.md), and a FAT32 image
    chgame cart flash PKG [--game ID] [--port P]  upload one game
    chgame cart deploy PKG [--card DIR] [--port P] [--clean] [--no-flash]

A recipe is a manifest whose games may be {"sketch": "CHFour", "folder": ...,
other game keys to override}: chgame cart build compiles each sketch (unless
--no-build) and takes its game from it (chcart/sources.py: chgame.json).
Exit codes: 0 done, 1 an error in a cart or a failed step, 2 usage.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

from . import deploy, model, runtime, sources, zipio
from .model import CartError

GAME_SET = ("title", "folder", "version", "author", "description", "genre", "license", "url", "sourceUrl", "id")
CART_SET = ("title", "version", "author", "description", "date", "license", "url", "sourceUrl")


def _load(path):
    issues = []
    cart = zipio.load(path, issues)
    for i in issues:
        if not i.error:
            print(f"{path}: {i}", file=sys.stderr)
    return cart


def _save(cart, path):
    data = zipio.write(cart, path)
    print(f"{path}: {len(cart.games)} game{'s' * (len(cart.games) != 1)}, {len(data)} B")


def _game(cart, gid):
    g = cart.game(gid)
    if g is None:
        raise CartError([model.Issue("bad-id", gid, f"no game {gid!r} (games: {', '.join(x.id for x in cart.games)})")])
    return g


def cmd_info(a):
    cart = _load(a.pkg)
    if a.json:
        print(json.dumps(model.to_manifest(cart)[0], indent=2))
        return 0
    print(f"{cart.title}" + "".join(f"  {k} {getattr(cart, k)}" for k in ("version", "author") if getattr(cart, k)))
    if cart.launch:
        print(f"launch: {cart.launch}")
    for g in cart.games:
        img = g.binary("rev0")
        where = f"[{g.folder}] " if g.folder else ""
        print(f"  {g.id:20s} {where}{g.title!r}  {len(img) if img else 0} B"
              + (f", {len(g.sd)} SD file{'s' * (len(g.sd) != 1)} ({sum(map(len, g.sd.values()))} B)" if g.sd else "")
              + (f"  {g.version}" if g.version else ""))
    return 0


def cmd_verify(a):
    bad = 0
    for p in a.pkgs:
        issues = zipio.check(p)
        errors = [i for i in issues if i.error]
        print(f"{p}: {'BAD' if errors else 'ok'}")
        for i in issues:
            print(f"  {i}")
        bad += bool(errors)
    return 1 if bad else 0


def cmd_extract(a):
    files, manifest = zipio.read(a.pkg)
    out = pathlib.Path(a.dir)
    for n, data in files.items():
        (out / n).parent.mkdir(parents=True, exist_ok=True)
        (out / n).write_bytes(data)
    print(f"{out}: {len(files)} files")
    return 0


def _apply_cart_args(cart, a):
    for k in CART_SET:
        v = getattr(a, k, None)
        if v is not None:
            setattr(cart, k, v)


def cmd_new(a):
    games = []
    for item in a.items:
        games = sources.merge(games, sources.load_item(item, build=not a.no_build))
    first = next((zipio.load(i) for i in a.items if str(i).lower().endswith(".chgame")), None)
    cart = model.Cart(title=a.title or (first.title if first else games[0].title if len(games) == 1 else "CART"),
                      games=games)
    if first:                               # the first cart's menu and details carry over
        for k in CART_SET[1:] + ("background", "colors", "folder_backgrounds"):
            setattr(cart, k, getattr(first, k))
    _apply_cart_args(cart, a)
    _save(cart, a.out)
    return 0


def build_recipe(recipe_path, build=True, platform_dir=None, binary=None):
    """A Cart from a recipe file. `binary(sketch_dir)` may supply each release
    .bin instead of building (tools/release/acceptance.py)."""
    import paths
    r = json.loads(pathlib.Path(recipe_path).read_text(encoding="utf-8"))
    base = pathlib.Path(recipe_path).parent
    games = []
    for e in r.get("games", []):
        e = dict(e)
        name = e.pop("sketch")
        d = paths.sketch(name) if platform_dir is None else _in_platform(name, platform_dir)
        if binary is not None:
            g = sources.from_sketch(d, pathlib.Path(binary(d)).read_bytes())
        else:
            g = sources.load_item(d, build=build)[0]
        for k, v in e.items():
            if k not in GAME_SET:
                raise CartError([model.Issue("bad-field", f"{recipe_path}: {name}.{k}", "not a game key a recipe sets")])
            setattr(g, k, v)
        games = sources.merge(games, [g])
    menu = r.get("menu", {})
    cart = model.Cart(title=r.get("title", "CART"), games=games, launch=r.get("launch", ""),
                      colors=menu.get("colors", {}))
    for k in CART_SET[1:]:
        setattr(cart, k, r.get(k, ""))
    if menu.get("background"):
        cart.background = (base / menu["background"]).read_bytes()
    for f in menu.get("folders", []):
        cart.folder_backgrounds[f["name"]] = (base / f["background"]).read_bytes()
    return cart


def _in_platform(name, platform_dir):
    for sub in ("Games", "Apps"):
        d = pathlib.Path(platform_dir) / "libraries" / "CHGame" / "examples" / sub / name
        if d.is_dir():
            return d
    raise SystemExit(f"{name}: not in {platform_dir}")


def cmd_build(a):
    cart = build_recipe(a.recipe, build=not a.no_build)
    out = a.out or str(pathlib.Path(a.recipe).with_suffix(".chgame").name)
    _save(cart, out)
    return 0


def cmd_add(a):
    cart = _load(a.pkg)
    new = []
    for item in a.items:
        new += sources.load_item(item, build=not a.no_build)
    for g in new:
        if a.folder is not None:
            g.folder = a.folder
    merged = sources.merge(cart.games, new)
    if a.at is not None:
        added = merged[len(cart.games):]
        merged = cart.games[:a.at] + added + cart.games[a.at:]
    cart.games = merged
    _save(cart, a.pkg)
    return 0


def cmd_remove(a):
    cart = _load(a.pkg)
    for gid in a.ids:
        _game(cart, gid)
    cart.games = [g for g in cart.games if g.id not in a.ids]
    if cart.launch in a.ids:
        cart.launch = ""
    _save(cart, a.pkg)
    return 0


def cmd_order(a):
    cart = _load(a.pkg)
    first = [_game(cart, gid) for gid in a.ids]
    cart.games = first + [g for g in cart.games if g.id not in a.ids]
    _save(cart, a.pkg)
    return 0


def cmd_set(a):
    cart = _load(a.pkg)
    target, keys = (_game(cart, a.game), GAME_SET) if a.game else (cart, CART_SET)
    for kv in a.pairs:
        k, eq, v = kv.partition("=")
        if not eq or k not in keys:
            raise SystemExit(f"{kv}: KEY=VALUE with KEY one of {', '.join(keys)}")
        if k == "id" and cart.launch == target.id:
            cart.launch = v
        setattr(target, k, v)
    _save(cart, a.pkg)
    return 0


def cmd_launch(a):
    cart = _load(a.pkg)
    cart.launch = "" if a.id == "none" else _game(cart, a.id).id
    _save(cart, a.pkg)
    return 0


def cmd_background(a):
    cart = _load(a.pkg)
    png = None if a.png == "none" else pathlib.Path(a.png).read_bytes()
    if a.folder:
        if png is None:
            cart.folder_backgrounds.pop(a.folder, None)
        else:
            cart.folder_backgrounds[a.folder] = png
    else:
        cart.background = png
    _save(cart, a.pkg)
    return 0


def cmd_prepare(a):
    cart = _load(a.pkg)
    files = runtime.prepare(cart)
    runtime.write_folder(files, a.outdir)
    print(f"{a.outdir}: {len(files)} files, {sum(map(len, files.values()))} B; copy its contents to the card's root")
    if a.image:
        runtime.write_image(files, a.image)
        print(f"card image: {a.image}")
    return 0


def cmd_flash(a):
    cart = _load(a.pkg)
    g = _game(cart, a.game) if a.game else (cart.game(cart.launch) if cart.launch else cart.games[0])
    if not a.game and len(cart.games) > 1:
        print(f"note: flashing {g.id}; --game picks another", file=sys.stderr)
    deploy.flash(g, a.port)
    return 0


def cmd_deploy(a):
    deploy.deploy(_load(a.pkg), a.card, a.port, a.clean, do_flash=not a.no_flash)
    return 0


def cmd_export(a, sketch):
    g = sources.load_item(sketch, build=not a.no_build)[0]
    cart = model.Cart(title=g.title, games=[g], version=g.version, author=g.author, license=g.license,
                      url=g.url, sourceUrl=g.sourceUrl)
    out = pathlib.Path(a.out) if a.out else sketch / "build" / f"{sketch.name}.chgame"
    out.parent.mkdir(parents=True, exist_ok=True)
    _save(cart, out)
    return 0


def parser():
    ap = argparse.ArgumentParser(prog="chgame cart", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True, metavar="command")
    p = sub.add_parser("info", help="list a cart's games")
    p.add_argument("pkg")
    p.add_argument("--json", action="store_true", help="the normalized info.json")
    p = sub.add_parser("verify", help="check carts against the spec")
    p.add_argument("pkgs", nargs="+")
    p = sub.add_parser("extract", help="unpack a cart's files")
    p.add_argument("pkg")
    p.add_argument("dir")
    for name in ("new", "build"):
        p = sub.add_parser(name, help="a cart from items" if name == "new" else "a cart from a recipe")
        if name == "new":
            p.add_argument("out")
            p.add_argument("items", nargs="+")
        else:
            p.add_argument("recipe")
            p.add_argument("out", nargs="?")
        p.add_argument("--no-build", action="store_true", help="sketches: take build/release as it is")
        for k in CART_SET:
            p.add_argument(f"--{k}")
    p = sub.add_parser("add", help="add games")
    p.add_argument("pkg")
    p.add_argument("items", nargs="+")
    p.add_argument("--folder")
    p.add_argument("--at", type=int, help="position (0 = first)")
    p.add_argument("--no-build", action="store_true")
    p = sub.add_parser("remove", help="remove games")
    p.add_argument("pkg")
    p.add_argument("ids", nargs="+")
    p = sub.add_parser("order", help="reorder games")
    p.add_argument("pkg")
    p.add_argument("ids", nargs="+")
    p = sub.add_parser("set", help="edit details")
    p.add_argument("pkg")
    p.add_argument("pairs", nargs="+", metavar="KEY=VALUE")
    p.add_argument("--game", help="a game's id (default: the cart's own details)")
    p = sub.add_parser("launch", help="the game started at power-on")
    p.add_argument("pkg")
    p.add_argument("id")
    p = sub.add_parser("background", help="the menu's background (a 128x128 PNG)")
    p.add_argument("pkg")
    p.add_argument("png")
    p.add_argument("--folder")
    p = sub.add_parser("prepare", help="the card's files")
    p.add_argument("pkg")
    p.add_argument("outdir")
    p.add_argument("--image", help="also a FAT32 card image")
    p = sub.add_parser("flash", help="upload one game")
    p.add_argument("pkg")
    p.add_argument("--game")
    p.add_argument("--port")
    p = sub.add_parser("deploy", help="flash and/or write the card, by the deploy rules")
    p.add_argument("pkg")
    p.add_argument("--card", help="the mounted card's folder (drive)")
    p.add_argument("--port")
    p.add_argument("--clean", action="store_true", help="empty the card's GAMES/ first (several games)")
    p.add_argument("--no-flash", action="store_true")
    return ap


def main(argv=None):
    a = parser().parse_args(argv)
    try:
        return globals()[f"cmd_{a.cmd}"](a)
    except CartError as e:
        print(e, file=sys.stderr)
        return 1
    except (OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


def export_main(argv, sketch):
    ap = argparse.ArgumentParser(prog="chgame export", description="the sketch as a .chgame (build/<Name>.chgame)")
    ap.add_argument("--no-build", action="store_true", help="take build/release as it is")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    try:
        return cmd_export(a, sketch)
    except CartError as e:
        print(e, file=sys.stderr)
        return 1
    except (OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
