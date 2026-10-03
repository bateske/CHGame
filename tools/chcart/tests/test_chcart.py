"""chcart's tests: the format's rules, the ZIP reader's refusals, the imports,
runtime preparation byte for byte, the editing commands.

    python -m unittest discover -s tools/chcart/tests
"""
import io
import json
import pathlib
import struct
import sys
import tempfile
import unittest
import zipfile

TOOLS = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TOOLS))

import chgpack  # noqa: E402
from chcart import cli, model, runtime, sources, zipio  # noqa: E402
from chcart.model import Cart, CartError, Game, Screenshot  # noqa: E402


def image(n, seed=1):
    return bytes((i * 31 + seed * 17) & 0xFF for i in range(n))


def png(size=(128, 128), colors=((0, 0, 0),), mode="RGB", fmt="PNG"):
    from PIL import Image
    im = Image.new(mode, size, colors[0])
    for k, c in enumerate(colors[1:], 1):
        im.putpixel((k % size[0], k // size[0]), c)
    b = io.BytesIO()
    im.save(b, fmt)
    return b.getvalue()


def game(gid="one", title="ONE", **kw):
    return Game(id=gid, title=title, binaries={"rev0": image(kw.pop("n", 1000), len(gid))}, **kw)


def codes(issues, errors=True):
    return sorted({i.code for i in issues if i.error == errors})


class Format(unittest.TestCase):
    def test_round_trip_and_same_bytes(self):
        c = Cart("CART", [game("one", "ONE", sd={"DATA/X.DAT": b"x"}, license_files={"LICENSE": b"L"},
                               screenshots=[Screenshot(png(), "title")], cart_image=png(), buttons=[("A", "go")]),
                          game("two", "TWO", folder="F/G")],
                 version="1.0", author="me", launch="two", background=png(), colors={"text": "#FFFFFF"},
                 folder_backgrounds={"F": png()})
        a = zipio.to_bytes(c)
        self.assertEqual(a, zipio.to_bytes(c))
        back = zipio.load(a)
        self.assertEqual(zipio.to_bytes(back), a)
        self.assertEqual(back.game("one").sd, {"DATA/X.DAT": b"x"})
        self.assertEqual(back.folders(), ["F", "F/G"])
        names = zipfile.ZipFile(io.BytesIO(a)).namelist()
        self.assertEqual(names[0], "info.json")
        self.assertIn("one/rev0.bin", names)
        self.assertIn("one/sdcard/DATA/X.DAT", names)

    def test_errors(self):
        bad = [
            ("duplicate-id", Cart("C", [game("a"), game("a", "B")])),
            ("bad-id", Cart("C", [game("A b")])),
            ("bad-title", Cart("C", [game("a", "")])),
            ("bad-title", Cart("C", [game("a", "X" * 32)])),
            ("bad-title", Cart("C", [game("a", "café")])),
            ("bad-folder", Cart("C", [game("a", folder="A/B/C/D/E")])),
            ("bad-folder", Cart("C", [game("a", folder=" A")])),
            ("bad-sd-path", Cart("C", [game("a", sd={"words.dic": b""})])),
            ("bad-sd-path", Cart("C", [game("a", sd={"GAMES/X.CHG": b""})])),
            ("bad-sd-path", Cart("C", [game("a", sd={"LONGFILENAME.DIC": b""})])),
            ("sd-conflict", Cart("C", [game("a", sd={"X.DAT": b"1"}), game("b", "B", sd={"X.DAT": b"2"})])),
            ("binary-size", Cart("C", [game("a", n=50945)])),
            ("bad-launch", Cart("C", [game("a")], launch="b")),
            ("bad-image", Cart("C", [game("a", cart_image=png((64, 64)))])),
            ("bad-image", Cart("C", [game("a", screenshots=[Screenshot(png((128, 64)))])])),
            ("bad-image", Cart("C", [game("a")], background=png(mode="RGBA", colors=((0, 0, 0, 0),)))),
            ("bad-background", Cart("C", [game("a")], background=png(colors=[(i, i, i) for i in range(1, 14)]))),
            ("missing-field", Cart("C", [])),
            ("bad-device", Cart("C", [Game("a", "A", {"rev9": image(10)})])),
            ("full-folder", Cart("C", [game(f"g{i}", f"G{i}", n=8) for i in range(model.FOLDER_ENTRIES + 1)])),
            ("full-folder", Cart("C", [game(f"g{i}", f"G{i}", n=8, folder=f"F{i}") for i in range(model.FOLDER_ENTRIES + 1)])),
        ]
        for code, c in bad:
            with self.subTest(code=code):
                self.assertIn(code, codes(model.validate(c)))
                with self.assertRaises(CartError):
                    zipio.to_bytes(c)
        boot = bytearray(image(100))
        struct.pack_into("<I", boot, 8, model.BOOT_SIG)
        self.assertIn("bootloader-image", codes(model.validate(Cart("C", [Game("a", "A", {"rev0": bytes(boot)})]))))

    def test_shared_sd_and_warnings(self):
        c = Cart("C", [game("a", "A" * 20, sd={"X.DAT": b"1"}), game("b", "B{", sd={"X.DAT": b"1"}, n=50436)])
        issues = model.validate(c)
        self.assertEqual(codes(issues), [])
        self.assertEqual(codes(issues, False), ["long-title", "save-pages", "title-chars"])
        self.assertEqual(model.validate(Cart("C", [game("a", "abc")])), [])     # a-z fold to capitals

    def test_manifest_shape(self):
        good = zipio.to_bytes(Cart("C", [game()]))
        files, m = zipio.read(good)

        def issues(m2, extra=None):
            f = dict(files, **(extra or {}))
            return model.from_manifest(m2, f)[1]
        self.assertIn("schema-version", codes(issues(dict(m, schemaVersion=2))))
        self.assertIn("schema-version", codes(issues({k: v for k, v in m.items() if k != "schemaVersion"})))
        self.assertIn("missing-file", codes(issues({**m, "games": [{**m["games"][0], "binaries": [
            {"device": "rev0", "filename": "nope.bin"}]}]})))
        self.assertIn("missing-field", codes(issues({k: v for k, v in m.items() if k != "games"})))
        self.assertIn("bad-field", codes(issues(dict(m, title=3))))
        w = issues(dict(m, colour="red"), {"stray.txt": b"x"})
        self.assertEqual(codes(w), [])
        self.assertEqual(codes(w, False), ["unknown-key", "unused-file"])


class Zip(unittest.TestCase):
    def zipped(self, entries, method=zipfile.ZIP_DEFLATED):
        b = io.BytesIO()
        with zipfile.ZipFile(b, "w", method) as z:
            for n, d in entries:
                zi = zipfile.ZipInfo("x")
                zi.filename = n                 # as given: ZipInfo() would turn '\' into '/' on Windows
                zi.compress_type = method
                z.writestr(zi, d)
        return b.getvalue()

    def code(self, data):
        with self.assertRaises(CartError) as e:
            zipio.read(data)
        return e.exception.code

    def test_refusals(self):
        info = json.dumps({"schemaVersion": 1}).encode()
        self.assertEqual(self.code(b"not a zip"), "not-a-zip")
        self.assertEqual(self.code(self.zipped([("x.txt", b"")])), "no-manifest")
        self.assertEqual(self.code(self.zipped([("info.json", b"{")])), "bad-json")
        self.assertEqual(self.code(self.zipped([("info.json", info), ("../evil", b"")])), "bad-zip")
        self.assertEqual(self.code(self.zipped([("info.json", info), ("/abs", b"")])), "bad-zip")
        self.assertEqual(self.code(self.zipped([("info.json", info), ("a\\b", b"")])), "bad-zip")
        self.assertEqual(self.code(self.zipped([("info.json", info), ("A.bin", b""), ("a.bin", b"")])), "bad-zip")
        self.assertEqual(self.code(self.zipped([("info.json", info)], zipfile.ZIP_BZIP2)), "bad-zip")
        self.assertEqual(zipio.read(self.zipped([("info.json", info), ("dir/", b"")]))[1], {"schemaVersion": 1})


class Sources(unittest.TestCase):
    def test_hex(self):
        def rec(addr, kind, data):
            b = bytes([len(data), addr >> 8, addr & 0xFF, kind]) + data
            return ":" + (b + bytes([-sum(b) & 0xFF])).hex().upper()
        text = "\n".join([rec(0, 4, b"\x00\x00"), rec(0x3000, 0, b"\x01\x02"), rec(0x3004, 0, b"\x05"),
                          rec(0, 1, b"")])
        self.assertEqual(sources.hex_to_bin(text), b"\x01\x02\xff\xff\x05")
        with self.assertRaises(ValueError):
            sources.hex_to_bin(rec(0x2FFF, 0, b"\x01"))
        with self.assertRaises(ValueError):
            sources.hex_to_bin(":0100000001FF")          # bad checksum

    def test_chg_and_bin(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "FOUR.CHG"
            p.write_bytes(chgpack.pack(image(4096), "FOUR IN A ROW", "me", "1.2"))
            g = sources.from_binary(p)
            self.assertEqual((g.id, g.title, g.author, g.version), ("four-in-a-row", "FOUR IN A ROW", "me", "1.2"))
            self.assertEqual(g.binary(), image(4096))
            b = pathlib.Path(d) / "My Game.ino.bin"
            b.write_bytes(image(10))
            self.assertEqual(sources.from_binary(b).title, "MY GAME")

    def test_merge(self):
        a, b = game("x"), game("x")
        c = game("x", n=999)
        log = []
        out = sources.merge([a], [b, c], log.append)
        self.assertEqual([g.id for g in out], ["x", "x-2"])
        self.assertEqual(len(log), 2)

    def test_sketch(self):
        with tempfile.TemporaryDirectory() as d:
            s = pathlib.Path(d) / "CHDemo"
            (s / "sdcard" / "SUB").mkdir(parents=True)
            (s / "sdcard" / "SUB" / "A.DAT").write_bytes(b"a")
            (s / "LICENSE").write_text("MIT License\n")
            (s / "README.md").write_text("# CHDemo\n\nA [demo](x) with *style*.\nMore.\n\n![gif](y)\n")
            (s / "config.h").write_text('#define DEMO_VERSION "2.5"\n')
            g = sources.from_sketch(s, image(64))
            self.assertEqual((g.id, g.title, g.version, g.license), ("chdemo", "CHDEMO", "2.5", "MIT"))
            self.assertEqual(g.description, "A demo with style. More.")
            self.assertEqual(g.sd, {"SUB/A.DAT": b"a"})
            self.assertEqual(list(g.license_files), ["LICENSE"])
            (s / "chgame.json").write_text(json.dumps({"title": "DEMO", "folder": "TOYS", "sdcard": ""}))
            g = sources.from_sketch(s, image(64))
            self.assertEqual((g.title, g.folder, g.sd), ("DEMO", "TOYS", {}))
            (s / "chgame.json").write_text(json.dumps({"titel": "X"}))
            with self.assertRaises(CartError):
                sources.from_sketch(s, image(64))


class Runtime(unittest.TestCase):
    def test_names(self):
        taken = set()
        got = [runtime.name83(t, taken, "CHG", "GAME") for t in ("WORDS", "WORDS", "Blackjack!", "BLACKJACK", "CON", "", "")]
        self.assertEqual(got, ["WORDS", "WORDS2", "BLACKJAC", "BLACKJA2", "CON2", "GAME", "GAME2"])
        self.assertEqual(runtime.name83("WORDS", taken, "", "FOLDER"), "WORDS")    # a folder: its own namespace

    def test_prepare(self):
        c = Cart("C", [game("z", "ZULU"), game("a", "ALPHA", folder="ONE"), game("b", "BRAVO", folder="ONE/TWO"),
                       game("m", "MIKE", sd={"M.DAT": b"m"})], launch="b")
        files = runtime.prepare(c)
        self.assertEqual(list(files), ["GAMES/MENU.IDX", "GAMES/MENU.BG", "GAMES/ZULU.CHG", "GAMES/MIKE.CHG",
                                       "GAMES/ONE/MENU.IDX", "GAMES/ONE/ALPHA.CHG", "GAMES/ONE/TWO/MENU.IDX",
                                       "GAMES/ONE/TWO/BRAVO.CHG", "M.DAT"])
        idx = files["GAMES/MENU.IDX"]
        recs = [idx[i:i + 32] for i in range(0, len(idx), 32)]
        self.assertEqual(recs[0], b"CHX1" + bytes(28))
        self.assertEqual([r[:12] for r in recs[1:]], [b"ZULU    CHG\0", b"ONE        \1", b"MIKE    CHG\0"])
        self.assertEqual(recs[2][12:], b"ONE".ljust(20, b"\0"))
        two = files["GAMES/ONE/MENU.IDX"]
        self.assertEqual(two[32:44], b"ALPHA   CHG\0")
        self.assertEqual(two[64:76], b"TWO        \1")
        self.assertEqual(files["GAMES/ONE/TWO/MENU.IDX"][32:44], b"BRAVO   CHG\1")
        info = chgpack.parse(files["GAMES/ZULU.CHG"])
        self.assertEqual((info["title"], info["payload_bytes"]), ("ZULU", 1000))
        self.assertEqual(files["GAMES/MENU.BG"], runtime.menu_background(runtime.DEFAULT_BACKGROUND.read_bytes(),
                                                                         c.ui_colors()))
        self.assertEqual(runtime.prepare(c), files)

    def test_chg_fields(self):
        g = game("a", "A", author="A very long author name", version="1.2.3-beta")
        info = chgpack.parse(runtime.chg_file(g))
        self.assertEqual((info["author"], info["version"]), ("A very long aut", "1.2.3-b"))
        g = game("a", "A", author="José")
        self.assertEqual(chgpack.parse(runtime.chg_file(g))["author"], "")

    def test_background(self):
        colors = [(255, 0, 255), (10, 20, 30), (255, 244, 214), (40, 50, 60), (10, 20, 30)]
        from PIL import Image
        im = Image.new("RGB", (128, 128), (0, 0, 0))
        for x, c in enumerate(colors):
            im.putpixel((x, 0), c)
        b = io.BytesIO()
        im.save(b, "PNG")
        bg = runtime.menu_background(b.getvalue(), dict(model.UI_COLORS))
        self.assertEqual(len(bg), runtime.BG_BYTES)
        self.assertEqual(bg[:4], b"CHB1")
        pal = struct.unpack_from("<16H", bg, 8)
        self.assertEqual(pal[0], runtime.rgb565(10, 20, 30))
        self.assertEqual(pal[1], runtime.rgb565(40, 50, 60))
        self.assertEqual(pal[11], runtime.rgb565(255, 244, 214))
        self.assertEqual(pal[13], 0)                     # selectedText: black
        self.assertEqual(pal[15], 0xF81F)                # colour 15: #FF00FF (the static style shows it)
        row = bg[512:512 + 3]
        # magenta 15, (10,20,30) 0, cream 11 (text), (40,50,60) 1, (10,20,30) 0, then black 13 (selectedText)
        self.assertEqual(row, bytes([0xF0, 0xB1, 0x0D]))


class Background(unittest.TestCase):
    def test_convert(self):
        from chcart import background
        from PIL import Image, ImageDraw
        default = background.template()
        self.assertEqual(background.convert(default), (default, []))      # ready: kept byte for byte
        im = Image.new("RGB", (300, 200))
        for x in range(300):
            for y in range(200):
                im.putpixel((x, y), (x * 255 // 299, y * 255 // 199, 90))
        ImageDraw.Draw(im).rectangle([140, 0, 160, 20], fill=(250, 12, 240))
        b = io.BytesIO()
        im.save(b, "PNG")
        png, notes = background.convert(b.getvalue())
        self.assertTrue(background.ready(png))
        self.assertEqual(len(notes), 3)                                   # scaled, magenta, colours
        px = model.rgb_pixels(png)
        self.assertIn(model.RAINBOW_RGB, px)
        self.assertLessEqual(len(model.background_colors(png, dict(model.UI_COLORS))), 11)
        big = Image.open(io.BytesIO(default)).resize((256, 256), Image.NEAREST)
        b = io.BytesIO()
        big.save(b, "PNG")
        self.assertEqual(model.rgb_pixels(background.convert(b.getvalue())[0]), model.rgb_pixels(default))
        rgba = Image.new("RGBA", (128, 128), (255, 255, 255, 0))
        b = io.BytesIO()
        rgba.save(b, "PNG")
        self.assertEqual(set(model.rgb_pixels(background.convert(b.getvalue())[0])), {(0, 0, 0)})

    def test_preview_and_card(self):
        from chcart import background
        im = background.preview(background.template())
        self.assertEqual(im.size, (384, 384))
        static = background.preview(background.template(), scale=1, style="static")
        self.assertEqual(static.getpixel((64, 25)), (255, 0, 255))    # the selection bar
        bars = {background.preview(background.template(), phase=p, scale=1).getpixel((64, 25)) for p in (0, 64, 128)}
        self.assertEqual(len(bars), 3)                                 # one colour, turning
        with tempfile.TemporaryDirectory() as d:
            f = background.write_to_card(background.template(), d)
            self.assertEqual(f.read_bytes(), runtime.menu_background(background.template(), dict(model.UI_COLORS)))
            background.save_preview(background.template(), pathlib.Path(d) / "p.gif")
            self.assertGreater((pathlib.Path(d) / "p.gif").stat().st_size, 0)
        self.assertEqual(background.colors_arg(["text=#ffffff"])["text"], "#FFFFFF")
        with self.assertRaises(ValueError):
            background.colors_arg(["txt=#FFFFFF"])

    def test_cart_command_converts(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as d:
            d = pathlib.Path(d)
            (d / "a.bin").write_bytes(image(100))
            pkg = str(d / "c.chgame")
            Image.new("RGB", (64, 32), (200, 30, 30)).save(d / "pic.jpg")
            self.assertEqual(cli.main(["new", pkg, str(d / "a.bin")]), 0)
            self.assertEqual(cli.main(["background", pkg, str(d / "pic.jpg"), "--color", "text=#FFFFFF"]), 0)
            c = zipio.load(pkg)
            self.assertEqual(model.image_info(c.background)[1:3], (128, 128))
            self.assertEqual(c.colors, {"text": "#FFFFFF"})
            self.assertEqual(cli.background_main([str(d / "pic.jpg"), "--card", str(d / "card")]), 0)
            self.assertEqual(len((d / "card" / "GAMES" / "MENU.BG").read_bytes()), runtime.BG_BYTES)


class Deploy(unittest.TestCase):
    def test_rules(self):
        from chcart import deploy
        quiet = lambda s: None
        with tempfile.TemporaryDirectory() as d:
            card = pathlib.Path(d)
            # one game with SD files needs a card
            with self.assertRaises(CartError):
                deploy.deploy(Cart("C", [game("a", "WORDS", sd={"W.DIC": b"w"})]), None, do_flash=False, log=quiet)
            # a hand-copied older WORDS under another name is replaced in place; another game keeps WORDS.CHG
            (card / "GAMES").mkdir()
            (card / "GAMES" / "OLDWORDS.CHG").write_bytes(chgpack.pack(image(10), "WORDS"))
            (card / "GAMES" / "WORDS.CHG").write_bytes(chgpack.pack(image(20), "OTHER"))
            (card / "GAMES" / "MENU.IDX").write_bytes(b"theirs")
            deploy.deploy(Cart("C", [game("a", "WORDS", sd={"W.DIC": b"w"})]), card, do_flash=False, log=quiet)
            self.assertEqual(chgpack.parse((card / "GAMES" / "OLDWORDS.CHG").read_bytes())["payload_bytes"], 1000)
            self.assertEqual(chgpack.parse((card / "GAMES" / "WORDS.CHG").read_bytes())["title"], "OTHER")
            self.assertEqual((card / "W.DIC").read_bytes(), b"w")
            self.assertEqual((card / "GAMES" / "MENU.IDX").read_bytes(), b"theirs")   # its menu left alone
            deploy.deploy(Cart("C", [game("b", "NEW")]), card, do_flash=False, log=quiet)
            self.assertTrue((card / "GAMES" / "NEW.CHG").exists())
            # several games: the cart's menu replaces the card's; --clean empties GAMES/ first
            multi = Cart("C", [game("x", "XRAY"), game("y", "YANKEE", folder="F")])
            with self.assertRaises(CartError):
                deploy.deploy(multi, None, do_flash=False, log=quiet)
            deploy.deploy(multi, card, do_flash=False, log=quiet)
            self.assertEqual((card / "GAMES" / "MENU.IDX").read_bytes(), runtime.prepare(multi)["GAMES/MENU.IDX"])
            self.assertTrue((card / "GAMES" / "NEW.CHG").exists())
            deploy.deploy(multi, card, clean=True, do_flash=False, log=quiet)
            self.assertEqual(sorted(p.relative_to(card).as_posix() for p in (card / "GAMES").rglob("*") if p.is_file()),
                             sorted(p for p in runtime.prepare(multi) if p.startswith("GAMES/")))


class Fixtures(unittest.TestCase):
    def test_expected(self):
        from chcart import fixtures
        self.assertEqual(fixtures.check(log=lambda s: None), [])

    def test_schema_agrees(self):
        """spec/info.schema.json accepts every good fixture's manifest and
        refuses the bad ones whose fault is the manifest's shape."""
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema is not installed")
        from chcart import fixtures
        schema = json.loads((fixtures.FIX.parent / "info.schema.json").read_text(encoding="utf-8"))
        v = jsonschema.Draft202012Validator(schema)
        for f in sorted((fixtures.FIX / "good").glob("*.chgame")):
            with self.subTest(f.name):
                self.assertEqual([e.message for e in v.iter_errors(zipio.read(f)[1])], [])
        for code in ("schema-version", "missing-field", "bad-field", "bad-id", "bad-title", "bad-folder", "bad-device"):
            with self.subTest(code):
                self.assertTrue(list(v.iter_errors(zipio.read(fixtures.FIX / "bad" / f"{code}.chgame")[1])))


class Commands(unittest.TestCase):
    def test_edit_and_prepare(self):
        with tempfile.TemporaryDirectory() as d:
            d = pathlib.Path(d)
            for n in ("ALPHA", "BRAVO", "CHARLIE"):
                (d / f"{n}.bin").write_bytes(image(500, len(n)))
            pkg = str(d / "c.chgame")
            run = lambda *a: self.assertEqual(cli.main([str(x) for x in a]), 0)
            run("new", pkg, d / "ALPHA.bin", d / "BRAVO.bin", "--title", "MINE")
            run("add", pkg, d / "CHARLIE.bin", "--folder", "MORE", "--at", 0)
            self.assertEqual([g.id for g in zipio.load(pkg).games], ["charlie", "alpha", "bravo"])
            run("order", pkg, "alpha", "MORE/")                       # a folder: its games
            self.assertEqual([g.id for g in zipio.load(pkg).games], ["alpha", "charlie", "bravo"])
            self.assertEqual(cli.main(["order", pkg, "NOPE/"]), 1)
            run("order", pkg, "bravo")
            run("set", pkg, "--game", "alpha", "title=ALPHA ONE", "folder=MORE")
            run("set", pkg, "author=me")
            run("launch", pkg, "alpha")
            run("remove", pkg, "charlie")
            c = zipio.load(pkg)
            self.assertEqual([(g.id, g.title, g.folder) for g in c.games],
                             [("bravo", "BRAVO", ""), ("alpha", "ALPHA ONE", "MORE")])
            self.assertEqual((c.title, c.author, c.launch), ("MINE", "me", "alpha"))
            run("verify", pkg)
            run("prepare", pkg, d / "card", "--image", d / "card.img")
            self.assertTrue((d / "card" / "GAMES" / "MORE" / "ALPHAONE.CHG").exists())
            self.assertTrue((d / "card.img").stat().st_size > 0)
            self.assertEqual(cli.main(["launch", pkg, "nobody"]), 1)


if __name__ == "__main__":
    unittest.main()
