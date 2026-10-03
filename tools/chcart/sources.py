"""Where games come from: a sketch folder (built, described by its
chgame.json), a raw .bin, an Intel .hex, a .chg, or another .chgame.

A sketch's chgame.json describes the one game it makes, with paths relative
to the sketch; every key is optional (an unknown one is an error, so a typo
cannot drop a field):

    {"id": "words", "title": "WORDS", "author": "...", "version": "...",
     "description": "...", "genre": "...", "license": "Apache-2.0",
     "url": "...", "sourceUrl": "...", "folder": "WORD GAMES",
     "licenseFiles": ["LICENSE", "NOTICE"], "sdcard": "sdcard",
     "cartImage": "docs/cart.png", "screenshots": ["docs/gameplay.gif"],
     "buttons": [{"control": "A", "action": "Lay a tile"}]}

The defaults: id from the folder's name; title the folder's name in capitals
(as the IDE's Export Compiled Binary titles a .chg); version from config.h's
`#define <PFX>_VERSION "x"`; description the README's first paragraph;
license from the LICENSE file's first line; licenseFiles LICENSE and NOTICE
where they exist; sdcard `sdcard/` if it exists; screenshots
docs/gameplay.gif if it exists.
"""
from __future__ import annotations

import json
import pathlib
import re

from . import model, zipio
from .model import CartError, Game, Issue, Screenshot

SKETCH_KEYS = ("id", "title", "author", "version", "description", "genre", "license", "url", "sourceUrl",
               "folder", "licenseFiles", "sdcard", "cartImage", "screenshots", "buttons")
LICENSES = (("Apache License", "Apache-2.0"), ("MIT License", "MIT"),
            ("GNU GENERAL PUBLIC LICENSE", "GPL-3.0"), ("GNU LESSER GENERAL PUBLIC LICENSE", "LGPL-3.0"),
            ("BSD 3-Clause", "BSD-3-Clause"), ("BSD 2-Clause", "BSD-2-Clause"))


# ---- binaries ---------------------------------------------------------------------

def hex_to_bin(text, device="rev0"):
    """An Intel HEX file's bytes from the device's load address, gaps 0xFF."""
    d = model.DEVICES[device]
    mem, base = {}, 0
    for n, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        if not line.startswith(":"):
            raise ValueError(f"line {n}: not Intel HEX")
        b = bytes.fromhex(line[1:])
        if len(b) < 5 or len(b) != b[0] + 5 or sum(b) & 0xFF:
            raise ValueError(f"line {n}: bad length or checksum")
        count, addr, kind, data = b[0], b[1] << 8 | b[2], b[3], b[4:-1]
        if kind == 0:
            for i, v in enumerate(data):
                mem[base + addr + i] = v
        elif kind == 1:
            break
        elif kind == 2:
            base = int.from_bytes(data, "big") << 4
        elif kind == 4:
            base = int.from_bytes(data, "big") << 16
        elif kind not in (3, 5):
            raise ValueError(f"line {n}: record type {kind}")
    if not mem:
        raise ValueError("no data")
    lo, hi = min(mem), max(mem) + 1
    if lo < d.load_address:
        raise ValueError(f"data at 0x{lo:X}, below {device}'s load address 0x{d.load_address:X}: "
                         "is this a bootloader, or built for another board?")
    if hi - d.load_address > d.max_image:
        raise ValueError(f"data up to 0x{hi:X}: more than {d.max_image} B from 0x{d.load_address:X}")
    return bytes(mem.get(a, 0xFF) for a in range(d.load_address, hi))


def from_binary(path, title=None, gid=None, device="rev0"):
    """A Game from a .bin, .hex or .chg file (the .chg header gives its title,
    author and version)."""
    p = pathlib.Path(path)
    data = p.read_bytes()
    meta = {}
    if p.suffix.lower() == ".hex":
        img = hex_to_bin(data.decode("ascii", "replace"), device)
    elif p.suffix.lower() == ".chg":
        import chgpack                      # (tools/ is on the path: runtime.py)
        try:
            info = chgpack.parse(data)
        except chgpack.ChgError as e:
            raise CartError([Issue("bad-field", str(p), str(e))])
        img = data[chgpack.HEADER_BYTES:chgpack.HEADER_BYTES + info["payload_bytes"]]
        meta = {k: info[k] for k in ("author", "version") if info[k]}
        title = title or info["title"]
    else:
        img = data
    stem = p.name.split(".")[0]
    title = title or stem.upper()[:model.TITLE_MAX]
    return Game(id=gid or model.slug(title), title=title, binaries={device: img}, **meta)


# ---- sketches ---------------------------------------------------------------------

def sketch_meta(d):
    """The sketch's chgame.json, or {}; raises CartError on an unknown key."""
    f = pathlib.Path(d) / "chgame.json"
    if not f.exists():
        return {}
    try:
        meta = json.loads(f.read_text(encoding="utf-8"))
    except ValueError as e:
        raise CartError([Issue("bad-json", str(f), str(e))])
    if not isinstance(meta, dict):
        raise CartError([Issue("bad-json", str(f), "must be a JSON object")])
    bad = [k for k in meta if k not in SKETCH_KEYS]
    if bad:
        raise CartError([Issue("bad-field", str(f), f"unknown key {k!r} (known: {', '.join(SKETCH_KEYS)})")
                         for k in bad])
    return meta


def config_version(d):
    cfg = pathlib.Path(d) / "config.h"
    if cfg.exists():
        m = re.search(r'#define\s+\w+_VERSION\s+"([^"]+)"', cfg.read_text(encoding="utf-8", errors="replace"))
        if m:
            return m.group(1)
    return ""


def readme_paragraph(d):
    """The README's first paragraph of prose, as plain text."""
    f = pathlib.Path(d) / "README.md"
    if not f.exists():
        return ""
    para = []
    for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if not s:
            if para:
                break
            continue
        if s.startswith(("#", "![", "|", "```", "<")):
            if para:
                break
            continue
        para.append(s)
    t = " ".join(para)
    t = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", t)          # links and images: their text
    return re.sub(r"[*_`]", "", t)


def license_id(d):
    f = pathlib.Path(d) / "LICENSE"
    if f.exists():
        head = f.read_text(encoding="utf-8", errors="replace")[:400]
        for words, spdx in LICENSES:
            if words in head:
                return spdx
    return ""


def from_sketch(d, image, device="rev0"):
    """The Game a sketch folder makes, with `image` its release build's .bin."""
    d = pathlib.Path(d)
    meta = sketch_meta(d)
    g = Game(id=meta.get("id") or model.slug(d.name), title=meta.get("title") or d.name.upper()[:model.TITLE_MAX],
             binaries={device: image})
    g.version = meta.get("version") or config_version(d)
    g.description = meta.get("description") or readme_paragraph(d)
    g.license = meta.get("license") or license_id(d)
    for k in ("author", "genre", "url", "sourceUrl", "folder"):
        setattr(g, k, meta.get(k, ""))
    names = meta.get("licenseFiles", [n for n in ("LICENSE", "NOTICE") if (d / n).is_file()])
    for n in names:
        g.license_files[pathlib.PurePosixPath(n).name] = (d / n).read_bytes()
    sd = meta.get("sdcard", "sdcard" if (d / "sdcard").is_dir() else "")
    if sd:
        root = d / sd
        if not root.is_dir():
            raise CartError([Issue("missing-file", f"{d.name}/chgame.json: sdcard", f"no folder {root}")])
        for f in sorted(root.rglob("*")):
            if f.is_file():
                g.sd[f.relative_to(root).as_posix()] = f.read_bytes()
    if meta.get("cartImage"):
        g.cart_image = (d / meta["cartImage"]).read_bytes()
    shots = meta.get("screenshots", ["docs/gameplay.gif"] if (d / "docs" / "gameplay.gif").is_file() else [])
    for s in shots:
        if isinstance(s, dict):
            g.screenshots.append(Screenshot((d / s["filename"]).read_bytes(), s.get("title", "")))
        else:
            g.screenshots.append(Screenshot((d / s).read_bytes()))
    g.buttons = [(b["control"], b["action"]) for b in meta.get("buttons", [])]
    return g


def build_sketch(d, device="rev0"):
    """Compiles the sketch (release) and returns its Game."""
    import device as dev                    # tools/device.py
    out = dev.build(d)
    return from_sketch(d, (out / f"{pathlib.Path(d).name}.ino.bin").read_bytes(), device)


# ---- anything -----------------------------------------------------------------------

def load_item(item, build=True, title=None):
    """[Game] from a path: a .chgame (all its games), a .bin/.hex/.chg, or a
    sketch folder (built unless build=False, then its build/release .bin);
    or the name of a game or app in this repository (CHFour)."""
    p = pathlib.Path(item)
    if not p.exists() and p.name == str(item) and not p.suffix:
        import paths                        # tools/paths.py
        p = paths.sketch(str(item))
    if p.is_dir():
        if build:
            return [build_sketch(p)]
        b = p / "build" / "release" / f"{p.name}.ino.bin"
        if not b.exists():
            raise CartError([Issue("missing-file", str(p), f"{b} is missing: build it, or drop --no-build")])
        return [from_sketch(p, b.read_bytes())]
    if p.suffix.lower() == ".chgame":
        return zipio.load(p).games
    if p.suffix.lower() in (".bin", ".hex", ".chg"):
        return [from_binary(p, title)]
    raise CartError([Issue("bad-field", str(p), "not a .chgame, .bin, .hex, .chg or sketch folder")])


def merge(games, new, log=print):
    """Adds `new` games to the list: an identical game already there is
    skipped; a different one with the same id gets -2, -3 ..."""
    out = list(games)
    for g in new:
        same = next((h for h in out if h.id == g.id), None)
        if same is not None and same == g:
            log(f"{g.id}: already in the cart, skipped")
            continue
        if same is not None:
            base, n = g.id, 2
            while any(h.id == f"{base[:29]}-{n}" for h in out):
                n += 1
            g.id = f"{base[:29]}-{n}"
            log(f"{base}: another game has this id; this one is {g.id}")
        out.append(g)
    return out
