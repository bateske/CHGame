"""Whole-boot scenarios (test_boot.c): builds the package zoo and a FAT32
card, writes the manifest in the menu's display order, runs the scenarios,
converts the panel dumps to PNG and checks them against frames.json.

frames.json pins the SHA-256 of every frame. A change that alters a frame
fails until the new hashes are recorded (python3 run_tests.py --pin-frames),
CLAUDE.md rule 2: the pictures are the test."""
import hashlib
import json
import pathlib
import struct
import zlib

import chgpack
import fatimg

HERE = pathlib.Path(__file__).resolve().parent
TITLE_COLS = 19


def display_title(name, data):
    """What the menu shows: the header title, or the 8.3 name for a bad header."""
    try:
        chgpack.parse(data, check_payload=False)
        t = data[0x20:0x40].split(b"\0", 1)[0].decode("ascii")[:TITLE_COLS]
    except chgpack.ChgError:
        t = name.split(".")[0][:8]
    return t.ljust(TITLE_COLS)


def zoo(pk):
    z = {n: d for n, (d, _) in pk.items()}
    alpha = z["ALPHA.CHG"]
    # a bootloader image disguised as a game: valid header and CRCs, signature at payload offset 8
    p = bytearray(alpha[512:])
    struct.pack_into("<I", p, 8, chgpack.BOOT_SIG)
    h = bytearray(alpha[:512])
    h[0x20:0x40] = b"BOOT IMAGE".ljust(32, b"\0")
    struct.pack_into("<I", h, 0x14, zlib.crc32(bytes(p)) & 0xFFFFFFFF)
    struct.pack_into("<I", h, 0x1FC, zlib.crc32(bytes(h[:0x1FC])) & 0xFFFFFFFF)
    z["BOOTIMG.CHG"] = bytes(h) + bytes(p)
    # header fine, payload damaged
    h = bytearray(alpha[:512])
    h[0x20:0x40] = b"BAD PAYLOAD".ljust(32, b"\0")
    struct.pack_into("<I", h, 0x1FC, zlib.crc32(bytes(h[:0x1FC])) & 0xFFFFFFFF)
    p = bytearray(alpha[512:])
    p[5000] ^= 0x40
    z["BADPCRC.CHG"] = bytes(h) + bytes(p)
    return z


def cart_background_png():
    """The cart cards' picture: dark blue, a band in the rainbow colour at the
    top, a green block, a yellow strip at the foot."""
    import io
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (128, 128), (0, 0, 64))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 127, 15], fill=(255, 0, 255))
    d.rectangle([100, 30, 127, 127], fill=(0, 96, 0))
    d.rectangle([0, 120, 60, 127], fill=(200, 200, 0))
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return buf.getvalue()


def cart_cards(build_dir, pk):
    """Three cards made by the reference implementation (tools/chcart), as
    test_boot.c's t_cart_* expect them:

      cart        GAMES/ in MENU.IDX's order: ZULU (BRAVO's payload), the
                  folder FOLDER ONE (ALPHA GAME, then the folder INNER with
                  BRAVO), MIKE; then EXTRA.CHG ("AAA EXTRA"), copied in by
                  hand and not in the index, and an empty folder EMPTY (by
                  hand too); the index also names GHOST.CHG, which is not on
                  the card. A background of four colours with a band in the
                  rainbow colour.
      cartlaunch  the same cart launching ALPHA GAME (inside FOLDER ONE)
      cartbadbg   cart with its MENU.BG cut short: the menu's own look

    Returns ({name: image path}, {pkg name: CHG bytes}) for the extra
    payloads (MIKE, EXTRA)."""
    from chcart import model, runtime
    def payload(n):
        return pk[n][0][512:512 + chgpack.parse(pk[n][0])["payload_bytes"]]
    alpha, bravo = payload("ALPHA.CHG"), payload("BRAVO.CHG")
    mike = bytes((i * 7 + 3) & 0xFF for i in range(6000))
    extra = bytes((i * 13 + 5) & 0xFF for i in range(3000))

    def cart(launch=""):
        G = model.Game
        return model.Cart(title="TEST CART", launch=launch, background=cart_background_png(), games=[
            G("zulu", "ZULU", {"rev0": bravo}),
            G("alpha", "ALPHA GAME", {"rev0": alpha}, folder="FOLDER ONE"),
            G("bravo", "BRAVO", {"rev0": bravo}, folder="FOLDER ONE/INNER"),
            G("mike", "MIKE", {"rev0": mike})])

    out, extras = {}, {}
    for name, c in (("cart", cart()), ("cartlaunch", cart("alpha")), ("cartbadbg", cart())):
        files = runtime.prepare(c)
        files["GAMES/EXTRA.CHG"] = chgpack.pack(extra, "AAA EXTRA")
        files["GAMES/EMPTY/"] = None
        files["GAMES/MENU.IDX"] += b"GHOST   CHG".ljust(32, b"\0")
        if name == "cartbadbg":
            files["GAMES/MENU.BG"] = files["GAMES/MENU.BG"][:-512]
        out[name] = build_dir / f"{name}.img"
        fatimg.build_image(str(out[name]), files, fs="fat32", lfn=True, fragment={"GAMES/MENU.BG": 3})
    extras["MIKE.CHG"] = chgpack.pack(mike, "MIKE")
    extras["EXTRA.CHG"] = chgpack.pack(extra, "AAA EXTRA")
    # cartbig: 250 games in GAMES/, more than a folder lists (MENU_MAX_GAMES,
    # 240): the menu keeps the first 240 the directory holds, GAME 000-239
    big = {f"GAMES/G{i:03d}.CHG": chgpack.pack(bytes((j * 7 + i * 13) & 0xFF for j in range(64 + i)), f"GAME {i:03d}")
           for i in range(250)}
    out["cartbig"] = build_dir / "cartbig.img"
    fatimg.build_image(str(out["cartbig"]), big, fs="fat32")
    extras["G239.CHG"] = big["GAMES/G239.CHG"]
    return out, extras


def run_all(build_dir, build, run, imgs, lay, pk, quick, pin=False):
    z = zoo(pk)
    pkdir = build_dir / "pk"
    pkdir.mkdir(exist_ok=True)
    files = {}
    for n, d in z.items():
        (pkdir / n).write_bytes(d)
        files["GAMES/" + n] = d
    files["WORDS.DIC"] = bytes(5000)
    card = build_dir / "boot_fat32.img"
    fatimg.build_image(str(card), files, fs="fat32", lfn=True, decoys=True,
                       fragment={"GAMES/ALPHA.CHG": 7, "GAMES/BRAVO.CHG": 3}, dir_pieces={"GAMES": 2})
    order = sorted(z, key=lambda n: display_title(n, z[n]))
    from run_tests import hostpath   # noqa: E402  (paths as the test program sees them)
    carts, extras = cart_cards(build_dir, pk)
    man = [f"img fat32 {hostpath(card)}", f"img fat16 {hostpath(imgs['fat16'])}",
           f"img nogames {hostpath(imgs['nogames'])}"]
    man += [f"img {k} {hostpath(v)}" for k, v in carts.items()]
    for n in order + sorted(extras):             # (the zoo first: menu_index() is its position)
        d = z.get(n) or extras[n]
        if n in extras:
            (pkdir / n).write_bytes(d)
        try:
            info = chgpack.parse(d, check_payload=False)
            ln, crc = info["payload_bytes"], info["payload_crc32"]
        except chgpack.ChgError:
            ln, crc = 0, 0
        man.append(f"pkg {n} 0 {ln} {crc:x} {hostpath(pkdir / n)}")
    mpath = build_dir / "boot_manifest.txt"
    mpath.write_text("\n".join(man) + "\n")
    fdir = build_dir / "frames"
    fdir.mkdir(exist_ok=True)
    for old in fdir.glob("*"):
        old.unlink()
    from run_tests import CORE, MENU   # noqa: E402
    exe = build("boot", "test_boot.c", ["-DCHBOOT_MENU=1", "-DCHGAME_ALLOW_SELFUPDATE=1"], CORE + MENU)
    ok = run("boot", exe, mpath, fdir)
    wexe = build("boot_white", "test_boot.c", ["-DCHBOOT_MENU=1", "-DCHGAME_ALLOW_SELFUPDATE=1",
                                              "-DMENU_STYLE=MENU_STYLE_WHITE"], CORE + MENU)
    ok &= run("boot_white", wexe, mpath, fdir, "style", "white_")     # the white style still works and draws
    real = HERE.parents[3] / "out" / "sdcard.img"
    if real.exists():
        ok &= run_real(build_dir, exe, real, fdir)
    else:
        print(f"{'boot_real':12s} {'skip':6s} no out/sdcard.img (python tools/sdcard/mkcard.py --image out/sdcard.img)")
    ok &= check_frames(fdir, pin)
    ok &= check_preview(fdir)
    return ok


def check_preview(fdir):
    """`chgame background --preview` (tools/chcart/background.py) draws the
    menu as the bootloader does: the cart card's frame against its preview.
    The rainbow style: every pixel but colour 15's (its hue depends on the
    time). The white style: every pixel."""
    from PIL import Image
    from chcart import background, runtime
    png = cart_background_png()
    ui = dict(background.model.UI_COLORS)
    idx = runtime.menu_background(png, ui)
    diff = {}
    for style, frame in (("rainbow", "cart_menu.png"), ("white", "white_cart_menu.png")):
        pv = background.preview(png, ui, titles=["ZULU", "FOLDER ONE", "MIKE", "AAA EXTRA", "EMPTY"], scale=1,
                                installed=(), folders=(1, 4), style=style)
        real = Image.open(fdir / frame).convert("RGB").load()
        mine = pv.load()
        n = 0
        for y in range(128):
            for x in range(128):
                b = idx[512 + y * 64 + x // 2]
                if style == "rainbow" and ((b >> 4 if x % 2 == 0 else b & 15) == 15 or 20 <= y < 30):
                    continue
                n += real[x, y] != mine[x, y]
        diff[style] = n
    bad = {k: v for k, v in diff.items() if v}
    print(f"{'preview':12s} {'ok' if not bad else 'FAILED':6s} chcart's menu preview vs the bootloader's frames"
          " (rainbow, white)" + (f": pixels differ {bad}" if bad else ""))
    return not bad


def run_real(build_dir, exe, img, fdir):
    from run_tests import run, hostpath   # noqa: E402
    vol = fatimg.FatVolume(str(img))
    g, _, _ = vol.find("GAMES", is_dir=True)
    pkgs = {}
    for raw, attr, _, _ in vol.listdir(g):
        if attr & 0x10 or raw[8:11] != b"CHG":
            continue
        name = raw[:8].decode().rstrip() + ".CHG"
        pkgs[name] = vol.read_file("GAMES/" + name)
    pkdir = build_dir / "realpk"
    pkdir.mkdir(exist_ok=True)
    man = [f"img fat32 {hostpath(img)}"]
    for n in sorted(pkgs, key=lambda n: display_title(n, pkgs[n])):
        (pkdir / n).write_bytes(pkgs[n])
        info = chgpack.parse(pkgs[n])
        man.append(f"pkg {n} 0 {info['payload_bytes']} {info['payload_crc32']:x} {hostpath(pkdir / n)}")
    mpath = build_dir / "real_manifest.txt"
    mpath.write_text("\n".join(man) + "\n")
    return run("boot_real", exe, mpath, fdir, "real")


def check_frames(fdir, pin):
    from PIL import Image
    pinned_path = HERE / "frames.json"
    pinned = json.loads(pinned_path.read_text()) if pinned_path.exists() else {}
    now = {}
    for ppm in sorted(fdir.glob("*.ppm")):
        im = Image.open(ppm).convert("RGB")
        im.save(ppm.with_suffix(".png"))
        now[ppm.stem] = hashlib.sha256(im.tobytes()).hexdigest()
    if pin or not pinned:
        if not pin:
            pinned.clear()
        pinned.update(now)
        pinned_path.write_text(json.dumps(pinned, indent=1, sort_keys=True) + "\n", newline="\n")
        print(f"{'frames':12s} {'pinned':6s} {len(now)} frames recorded in frames.json")
        return True
    # real_* frames come from out/sdcard.img, which only exists after mkcard.py
    keys = set(now) | {k for k in pinned if not k.startswith("real_")}
    diff = sorted(k for k in keys if now.get(k) != pinned.get(k))
    print(f"{'frames':12s} {'ok' if not diff else 'FAILED':6s} {len(now)} frames vs frames.json" + (f": changed {diff}" if diff else ""))
    return not diff
