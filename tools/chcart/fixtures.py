"""The conformance fixtures in spec/fixtures: carts, good and bad, and what
reading and preparing each must give.

    python tools/chcart/fixtures.py           write them (spec/fixtures/good, bad, expected)
    python tools/chcart/fixtures.py --check   compare chcart's results with expected/ (exit 1 on a difference)

Every game's program is spec/fixtures/src/hello.bin, the CHGame library's
Hello example (a real program: an emulator can run any of these). Pictures
are drawn here. expected/<name>.json holds, for a good cart, the games as
read (ids, titles, folders, sizes and SHA-256 of their binaries and SD
files), the warning codes, and every file of the prepared card (size and
SHA-256); for a bad one, the error codes. Nothing in it depends on where a
writer put files inside the ZIP, so another implementation can be held to
it. The test (tools/chcart/tests) runs --check.
"""
from __future__ import annotations

import hashlib
import io
import json
import pathlib
import struct
import sys
import zipfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from chcart import model, runtime, zipio  # noqa: E402
from chcart.model import Cart, Game, Screenshot  # noqa: E402

FIX = HERE.parents[1] / "spec" / "fixtures"
HELLO = FIX / "src" / "hello.bin"


def png(draw, size=128, fmt="PNG", frames=1):
    from PIL import Image, ImageDraw
    ims = []
    for f in range(frames):
        im = Image.new("RGB", (size, size), (0, 0, 0))
        draw(ImageDraw.Draw(im), f)
        ims.append(im)
    b = io.BytesIO()
    if frames > 1:
        ims[0].save(b, fmt, save_all=True, append_images=ims[1:], duration=200, loop=0)
    else:
        ims[0].save(b, fmt)
    return b.getvalue()


def background(d, f):
    d.rectangle([0, 0, 127, 127], fill=(10, 20, 60))
    d.rectangle([0, 0, 127, 16], fill=(255, 0, 255))           # the rainbow band
    d.rectangle([96, 24, 127, 127], fill=(0, 90, 40))
    d.rectangle([0, 118, 127, 127], fill=(128, 128, 128))       # = disabled: index 12
    d.line([(0, 17), (127, 17)], fill=(255, 244, 214))          # = text: index 11


def folder_background(d, f):
    d.rectangle([0, 0, 127, 127], fill=(60, 10, 10))
    d.ellipse([20, 20, 108, 108], fill=(255, 0, 255))


def shot(d, f):
    d.rectangle([8 + 8 * f, 8, 40 + 8 * f, 40], fill=(255, 200, 0))


def good():
    hello = HELLO.read_bytes()
    lic = {"LICENSE": b"Fixture licence text.\n"}
    single = Cart("HELLO", [Game("hello", "HELLO", {"rev0": hello}, version="1.0", author="fixtures",
                                 license="MIT", license_files=lic)])
    single_sd = Cart("HELLO WITH DATA", [Game(
        "hello-sd", "HELLO WITH DATA", {"rev0": hello}, description="Hello, with files for the SD card.",
        sd={"HELLO.TXT": b"hello, card\n", "DATA/INFO.DAT": bytes(range(256)) * 4},
        cart_image=png(shot), screenshots=[Screenshot(png(shot, 256, "GIF", 3), "moving"), Screenshot(png(shot))],
        buttons=[("A", "say hello")])])
    shared = b"shared by two games\n"
    multi = Cart("FIXTURE CART", version="2.0", author="fixtures", date="2026-10-03", launch="inner",
                 background=png(background), colors={"text": "#FFF4D6", "mark": "#FF8000"},
                 folder_backgrounds={"TOYS": png(folder_background)}, games=[
                     Game("zulu", "ZULU", {"rev0": hello}, sd={"SHARED.DAT": shared}),
                     Game("alpha", "Alpha game", {"rev0": hello}, folder="TOYS"),
                     Game("inner", "INNER GAME", {"rev0": hello}, folder="TOYS/BOX", sd={"SHARED.DAT": shared}),
                     Game("words", "WORDS", {"rev0": hello}),
                     Game("words-2", "WORDS", {"rev0": hello}, folder="TOYS"),
                     Game("con", "CON", {"rev0": hello}),
                     Game("long", "A TITLE LONGER THAN THE MENU", {"rev0": hello}, author="an author with a long name")])
    return {"single": single, "single-sd": single_sd, "multi": multi}


def raw(entries):
    """A ZIP of exactly these (name, bytes), stored: bad carts are written
    around chcart's checks."""
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        for n, d in entries:
            zi = zipfile.ZipInfo("x", (1980, 1, 1, 0, 0, 0))
            zi.filename = n
            z.writestr(zi, d)
    return b.getvalue()


def bad():
    """{error code: bytes of a cart that breaks exactly that rule}."""
    img = bytes(range(64))
    boot = bytearray(img)
    struct.pack_into("<I", boot, 8, model.BOOT_SIG)

    def cart(games, **top):
        m = {"schemaVersion": 1, "title": "BAD", **top, "games": games}
        return m

    def g(gid="a", title="A", **kw):
        return {"id": gid, "title": title, "binaries": [{"device": "rev0", "filename": "a.bin"}], **kw}

    def z(m, extra=()):
        return raw([("info.json", json.dumps(m).encode()), ("a.bin", img), *extra])

    from PIL import Image
    many = Image.new("RGB", (128, 128))
    for i in range(12):
        many.putpixel((i, 0), (i + 1, 0, 0))
    b = io.BytesIO()
    many.save(b, "PNG")
    return {
        "not-a-zip": b"this is not a ZIP file\n",
        "bad-zip": raw([("info.json", b"{}"), ("../escape.bin", img)]),
        "no-manifest": raw([("a.bin", img)]),
        "bad-json": raw([("info.json", b"{\"schemaVersion\": 1,")]),
        "schema-version": z(dict(cart([g()]), schemaVersion=2)),
        "missing-field": z({"schemaVersion": 1, "title": "BAD"}),
        "bad-field": z(cart([g(author=7)])),
        "missing-file": z(cart([g(cartImage="nope.png")])),
        "bad-id": z(cart([g("Not An Id")])),
        "duplicate-id": z(cart([g(), g(title="B")])),
        "bad-title": z(cart([g(title="T" * 32)])),
        "bad-folder": z(cart([g(folder="A/B/C/D/E")])),
        "bad-device": z(cart([{"id": "a", "title": "A", "binaries": [{"device": "rev7", "filename": "a.bin"}]}])),
        "binary-size": raw([("info.json", json.dumps(cart([g()])).encode()), ("a.bin", bytes(50948))]),
        "bootloader-image": raw([("info.json", json.dumps(cart([g()])).encode()), ("a.bin", bytes(boot))]),
        "bad-sd-path": z(cart([g(sdcard="sd/")]), [("sd/words.dic", b"x")]),
        "sd-conflict": z(cart([g(sdcard="a/"), g("b", "B", sdcard="b/")]), [("a/X.DAT", b"1"), ("b/X.DAT", b"2")]),
        "bad-image": z(cart([g(cartImage="c.png")]), [("c.png", png(shot, 64))]),
        "bad-background": z(cart([g()], menu={"background": "bg.png"}), [("bg.png", b.getvalue())]),
        "bad-launch": z(cart([g()], launch="nobody")),
        "full-folder": z(cart([g(f"g{i}", f"G{i}") for i in range(model.FOLDER_ENTRIES + 1)])),
    }


def warnings_cart():
    m = {"schemaVersion": 1, "title": "WARNINGS", "colour": "red", "games": [
        {"id": "a", "title": "A TITLE OF TWENTY ONE", "binaries": [{"device": "rev0", "filename": "a.bin"}]},
        {"id": "b", "title": "B{}", "binaries": [{"device": "rev0", "filename": "b.bin"}]}]}
    return raw([("info.json", json.dumps(m).encode()), ("a.bin", HELLO.read_bytes()),
                ("b.bin", HELLO.read_bytes() + bytes(50440 - len(HELLO.read_bytes()))), ("README.txt", b"stray\n")])


def sha(b):
    return hashlib.sha256(b).hexdigest()


def result(data):
    """What expected/ records for a cart's bytes."""
    issues = zipio.check(data)
    errors = sorted({i.code for i in issues if i.error})
    if errors:
        return {"errors": errors}
    cart = zipio.load(data)
    return {
        "warnings": sorted({i.code for i in issues if not i.error}),
        "games": [{"id": g.id, "title": g.title, "folder": g.folder,
                   "binaries": {d: {"size": len(b), "sha256": sha(b)} for d, b in g.binaries.items()},
                   "sdcard": {p: sha(b) for p, b in sorted(g.sd.items())}} for g in cart.games],
        "launch": cart.launch,
        "card": {p: {"size": len(b), "sha256": sha(b)} for p, b in runtime.prepare(cart).items()},
    }


def everything():
    out = {f"good/{n}.chgame": zipio.to_bytes(c) for n, c in good().items()}
    out["good/warnings.chgame"] = warnings_cart()
    out.update({f"bad/{code}.chgame": data for code, data in bad().items()})
    return out


def write():
    for rel, data in everything().items():
        f = FIX / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(data)
        e = FIX / "expected" / (f.stem + ".json")
        e.parent.mkdir(parents=True, exist_ok=True)
        e.write_text(json.dumps(result(data), indent=1) + "\n", newline="\n", encoding="utf-8")
        print(rel)


def check(log=print):
    """[(fixture, problem)] between chcart's results and expected/."""
    bad_ = []
    for f in sorted((FIX / "good").glob("*.chgame")) + sorted((FIX / "bad").glob("*.chgame")):
        want = json.loads((FIX / "expected" / (f.stem + ".json")).read_text(encoding="utf-8"))
        got = result(f.read_bytes())
        if f.parent.name == "bad" and want.get("errors") != [f.stem]:
            bad_.append((f.name, f"expected/{f.stem}.json should name exactly the error {f.stem}"))
        if got != want:
            bad_.append((f.name, "differs from expected/" + f.stem + ".json"))
    for name, why in bad_:
        log(f"{name}: {why}")
    return bad_


if __name__ == "__main__":
    if "--check" in sys.argv:
        problems = check()
        print("fixtures: " + ("ok" if not problems else f"{len(problems)} differ"))
        sys.exit(1 if problems else 0)
    write()
