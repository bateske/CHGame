"""The new-user test: install a built release into an empty Arduino setup and
use it the way someone who only has the board package would.

    python tools/release/acceptance.py [--dist out/stage] [--all]
                                       [--card out/stage/CHGame-sdcard-<v>-{board}.zip]

It serves --dist on localhost (serve.py), points a fresh arduino-cli at it
(its own data folder, sketchbook and config under out/newuser/; your own
Arduino setup is not touched), and checks:

  - Boards Manager installs CHGame from the one URL, with its three tools;
  - Tools > Board lists every board the tools build for (chcart.model.DEVICES:
    CHGame Rev0, CHGame Rev1), and the package defines no other;
  - CHGame, CHGfx and CHSd come with it for each board (platform libraries,
    nothing to add);
  - File > Examples has CHGame's Hello, the twenty games, CHStlView and CHSDtoUSB;
  - for each board, Tools > Bootloader offers its five bootloaders (rev0's in
    bootloaders/CHGame/, a later board's in bootloaders/CHGame/<board>/), and
    their files are there, and Tools > Programmer offers CHGame USB and the
    WCH factory ISP;
  - examples copied to the sketchbook (what the IDE does when one is saved)
    compile for each board with plain `arduino-cli compile`, no --library,
    and Export Compiled Binary leaves a .bin and a .chg for that board's SD
    menu in build/CHGame.ch32v.<board>/ (the .chg checked as that board's
    bootloader checks it).

--all compiles every game and app for every board from the installed package
(release options, or a sketch's own FQBN in its tools/game.py, the board
field swapped: tools/device.py fqbn()), each image leaving the save pages
its game needs (SAVE_PAGES: two up to 50,432 B), and --card then makes the
casino cart from them (tools/sdcard/casino.json), one cart with every
board's binaries, beside the zips as CHGame-Casino-<version>.chgame, and
packs one card per board (chcart's runtime preparation for that board) as
CHGame-sdcard-<version>-<board>.zip ({board} in --card replaced, else
-<board> added to its name), each with a README naming its board: the cart
and the cards that go with the release, built from exactly what it delivers.

Nothing here touches a board. The bootloader and upload paths are for a
person with a board in hand (platform/board/docs/building.md).
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "sdcard"))
from _common import OUT, fail, say  # noqa: E402
import serve  # noqa: E402
import chgpack  # noqa: E402
import device  # noqa: E402
import gamecfg  # noqa: E402
import mkcard  # noqa: E402
from chcart import runtime, zipio  # noqa: E402

# Rev0's: the IDE's default options, and the release options. Each board's
# build swaps the board field (device.with_board()).
FQBN = "CHGame:ch32v:rev0"
RELEASE_FQBN = device.FQBN_RELEASE
# Tools > Bootloader, the same five for every board (boards.txt's menu.boot).
BOOT_MENU = ["sdmenu", "sdstatic", "sdvisual", "sdvisualstatic", "nomenu"]
NEWUSER = OUT / "newuser"
DOWNLOADS = OUT / "arduino-downloads"     # kept between runs: the toolchain is ~100 MB; our archives are deleted
DEFAULT_JOBS = max(1, min(4, (os.cpu_count() or 2) // 2))
# What the sketchbook test compiles, and what it expects: None is a build, a
# string is a compile error containing it. The smallest sketch and a large game
# with the IDE's default options (Smallest + LTO), a game with the release
# options, and an SD game, which needs USB > Upload only and says so. Each is
# compiled for every board, its FQBN's board field swapped.
SKETCHES = [("Hello", FQBN, None), ("Games/CHChess", FQBN, None), ("Games/CHFour", RELEASE_FQBN, None),
            ("Games/CHWords", FQBN, "needs Tools > USB > Upload only"), ("Games/CHWords", RELEASE_FQBN, None)]


class Cli:
    def __init__(self, root: Path, index_url: str):
        self.root = root
        self.config = root / "arduino-cli.yaml"
        self.data, self.user = root / "arduino15", root / "sketchbook"
        root.mkdir(parents=True, exist_ok=True)
        self.config.write_text(
            "board_manager:\n  additional_urls:\n    - " + index_url + "\n"
            "directories:\n"
            f"  data: {self.data.as_posix()}\n  user: {self.user.as_posix()}\n  downloads: {DOWNLOADS.as_posix()}\n"
            "network:\n  connection_timeout: 600s\n",
            encoding="utf-8", newline="\n")

    def __call__(self, *args, check=True, json_out=False):
        cmd = ["arduino-cli", "--config-file", str(self.config), *args] + (["--json"] if json_out else [])
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if check and r.returncode:
            fail(f"FAILED: arduino-cli {' '.join(args)}\n{r.stdout[-4000:]}{r.stderr[-4000:]}")
        return json.loads(r.stdout) if json_out and r.returncode == 0 else r


class Checks:
    def __init__(self):
        self.rows = []

    def __call__(self, ok: bool, what: str, detail: str = ""):
        self.rows.append((ok, what, detail))
        say(f"  {'ok  ' if ok else 'FAIL'} {what}" + (f": {detail}" if detail else ""))
        return ok

    @property
    def failed(self):
        return [r for r in self.rows if not r[0]]


def compile_sketch(cli: Cli, sketch: Path, fqbn: str, build: Path, export: bool = False, flags: str = ""):
    args = ["compile", "-b", fqbn, "--build-path", str(build), "--warnings", "none"]
    if flags:
        args += ["--build-property", "build.extra_flags=" + flags]
    if export:
        args.append("--export-binaries")
    r = cli(*args, str(sketch), check=False)
    return r.returncode == 0, (r.stdout + r.stderr)


def package_boards(plat: Path) -> dict[str, str]:
    """The boards a board package defines, {id: its Tools > Board name}, in
    boards.txt's order: {"rev0": "CHGame Rev0", "rev1": "CHGame Rev1"}."""
    text = (Path(plat) / "boards.txt").read_text(encoding="utf-8", errors="replace")
    return dict(re.findall(r"(?m)^([A-Za-z0-9_]+)\.name=(.+?)\s*$", text))


def card_zip(card: Path, board: str) -> Path:
    """One board's SD card zip: {board} in `card` replaced, else -<board>
    added to its name (CHGame-sdcard-0.4.0.zip: CHGame-sdcard-0.4.0-rev1.zip)."""
    return mkcard.per_board(card, board, several=True)


def export_dir(sketch: Path, board: str) -> Path:
    """Where Export Compiled Binary puts a sketch's files for a board: its
    build/<vendor>.<arch>.<board>/ (the FQBN without options, : as .)."""
    return Path(sketch) / "build" / device.DEVICES[board].fqbn.replace(":", ".")


def save_pages(size: int, board: str) -> int:
    """The save pages an image of `size` bytes leaves free on `board`
    (tools/check_size.py's rule): two up to its save_safe (50,432 B), one
    up to 256 B more, else none."""
    safe = device.DEVICES[board].save_safe
    return 2 if size <= safe else (1 if size <= safe + 256 else 0)


def run(dist: Path, port: int, build_all: bool, card: Path | None, jobs: int) -> int:
    check = Checks()
    server, index_url = serve.start(dist, port)
    expected = json.loads((dist / serve.INDEX).read_text(encoding="utf-8"))["packages"][0]["platforms"][0]["version"]
    say(f"=== a new user installs CHGame {expected} from {index_url} ===")
    if NEWUSER.exists():
        shutil.rmtree(NEWUSER)
    pkgdir = DOWNLOADS / "packages"
    if pkgdir.is_dir():                  # our archives change between builds of the same version
        for f in list(pkgdir.glob("CHGame-ch32v-*")) + list(pkgdir.glob("chgame-upload-*")):
            f.unlink()
    cli = Cli(NEWUSER, index_url)
    try:
        cli("core", "update-index")
        r = cli("core", "install", "CHGame:ch32v")
        say("  " + "\n  ".join(ln for ln in (r.stdout + r.stderr).splitlines()
                                if ln.strip() and not ("%" in ln and " / " in ln)))     # not the progress bars
    finally:
        server.shutdown()                # everything after this works offline, as an installed package must

    plat = cli.data / "packages" / "CHGame" / "hardware" / "ch32v" / expected
    check(plat.is_dir(), "the platform is installed", str(plat.relative_to(OUT)))
    tools = cli.data / "packages" / "CHGame" / "tools"
    for t in ("riscv-none-embed-gcc", "wchisp", "chgame-upload"):
        check(any((tools / t).glob("*")), f"tool {t}", ", ".join(p.name for p in (tools / t).glob("*")))

    say("=== Tools > Board ===")
    board_names = package_boards(plat)
    boards = [b for b in board_names if b in device.DEVICES]     # the package's, in its order
    unknown = [b for b in board_names if b not in device.DEVICES]
    missing = [b for b in device.BOARDS if b not in board_names]
    check(bool(boards) and not unknown, "the package's boards",
          "; ".join(f"{n} ({b})" for b, n in board_names.items())
          + (f"; not in tools/chcart/model.py's DEVICES: {', '.join(unknown)}" if unknown else ""))
    check(not missing, "every board the tools build for", f"missing: {', '.join(missing)}" if missing
          else ", ".join(device.BOARDS))
    if not boards:
        fail("the package defines no board the tools know: nothing more to check")

    say("=== libraries ===")
    for b in boards:
        libs = cli("lib", "list", "--all", "-b", device.DEVICES[b].fqbn, json_out=True).get("installed_libraries", [])
        found = {l["library"]["name"]: l["library"] for l in libs}
        for name in ("CHGame", "CHGfx", "CHSd"):
            lib = found.get(name)
            check(bool(lib) and lib.get("location") == "platform", f"{b}: library {name}",
                  f"{lib.get('version')}, {lib.get('location')}" if lib else "missing")
    user_libs = list((cli.user / "libraries").glob("*")) if (cli.user / "libraries").is_dir() else []
    check(not user_libs, "nothing installed in the sketchbook's libraries")

    say("=== File > Examples ===")
    ex = cli("lib", "examples", "CHGame", "-b", device.DEVICES[boards[0]].fqbn, json_out=True).get("examples", [])
    paths = [Path(p) for e in ex for p in e.get("examples", [])]
    rel = sorted(p.relative_to(plat / "libraries" / "CHGame" / "examples").as_posix() for p in paths
                 if (plat / "libraries" / "CHGame" / "examples") in p.parents)
    games = [r for r in rel if r.startswith("Games/")]
    apps = [r for r in rel if r.startswith("Apps/")]
    check("Hello" in rel, "CHGame > Hello")
    check(len(games) == 20, "CHGame > Games", f"{len(games)}: " + " ".join(g.split("/")[1] for g in games))
    check({"Apps/CHSDtoUSB", "Apps/CHSDtoSerial", "Apps/CHStlView"} <= set(apps), "CHGame > Apps", " ".join(apps))
    gfx = cli("lib", "examples", "CHGfx", "-b", device.DEVICES[boards[0]].fqbn, json_out=True).get("examples", [])
    check(sum(len(e.get("examples", [])) for e in gfx) > 0, "CHGfx's examples",
          str(sum(len(e.get("examples", [])) for e in gfx)))

    say("=== Tools menus ===")
    boards_txt = (plat / "boards.txt").read_text(encoding="utf-8", errors="replace")
    for b in boards:
        det = cli("board", "details", "-b", device.DEVICES[b].fqbn, json_out=True)
        check(bool(det), f"{b}: board details", board_names[b])
        opts = {o["option"]: [v["value"] for v in o["values"]] for o in det.get("config_options", [])}
        check(opts.get("boot", []) == BOOT_MENU, f"{b}: Tools > Bootloader", ", ".join(opts.get("boot", [])))
        progs = {p["id"]: p["name"] for p in det.get("programmers", [])}
        check({"chgameusb", "wchisp"} <= set(progs), f"{b}: Tools > Programmer", "; ".join(progs.values()))
        # rev0's files are in bootloaders/CHGame/, each later board's in bootloaders/CHGame/<board>/.
        folder = "CHGame/" if b == "rev0" else f"CHGame/{b}/"
        files = {}
        for ln in boards_txt.splitlines():
            m = re.match(rf"\s*{re.escape(b)}\.menu\.boot\.(\w+)\.bootloader\.file=(.+?)\s*$", ln)
            if m:
                files[m.group(1)] = m.group(2)
        check(sorted(files) == sorted(BOOT_MENU), f"{b}: a bootloader file for each entry", ", ".join(files))
        for entry, name in files.items():
            f = plat / "bootloaders" / name
            here = name.startswith(folder) and "/" not in name[len(folder):]
            check(f.is_file() and here, f"{b}: bootloader {entry}",
                  (f"{name}, {f.stat().st_size:,} B" if f.is_file() else f"{f} missing")
                  + ("" if here else f" (not in bootloaders/{folder})"))
    ptxt = (plat / "platform.txt").read_text(encoding="utf-8")
    check(f"version={expected}" in ptxt, "platform.txt's version", expected)

    say("=== sketches saved to the sketchbook, compiled with no --library ===")
    examples = plat / "libraries" / "CHGame" / "examples"
    for b in boards:
        for rel_sketch, fqbn, error in SKETCHES:
            src = examples / rel_sketch
            dst = cli.user / src.name
            if not dst.exists():
                shutil.copytree(src, dst)
            default = fqbn == FQBN
            options = "the IDE's default options" if default else "release options"
            ok, log = compile_sketch(cli, dst, device.with_board(fqbn, b),
                                     NEWUSER / "build" / b / f"{src.name}-{'default' if default else 'release'}",
                                     export=True)
            if error:
                check(not ok and error in log, f"{b}: {src.name} with {options} stops with a message", error)
                continue
            if not check(ok, f"{b}: {src.name} compiles with {options}"):
                say(log[-3000:])
                continue
            out = export_dir(dst, b)
            exported = list(out.glob(f"{src.name}.ino.*"))
            names = sorted(p.suffix for p in exported)
            chg = next((p for p in exported if p.suffix == ".chg"), None)
            info = ""
            if chg:
                try:                        # as this board's bootloader checks it: its target, no other
                    i = chgpack.parse(chg.read_bytes(), target=chgpack.target_of(b))
                    info = f"{i['title']}, {i['payload_bytes']:,} B, {i['device']}"
                except chgpack.ChgError as e:
                    chg, info = None, str(e)
            check(".bin" in names and chg is not None,
                  f"{b}: {src.name}: Export Compiled Binary gives .bin and .chg in build/{out.name}",
                  info or " ".join(names) or "nothing there")

    if build_all:
        say(f"=== every game and app for {', '.join(boards)}, from the installed package ({jobs} at a time) ===")
        progs_ = mkcard.programs()

        def build_one(job):
            b, name = job
            d = mkcard.folder(name, plat)
            out = NEWUSER / "build" / "all" / b / d.name
            ok, log = compile_sketch(cli, d, device.fqbn(d, False, b), out, flags=device.defines(d))
            return b, name, d, out / f"{d.name}.ino.bin", ok, log

        # One per board first: each fills the core cache that board's other builds share.
        first = [(b, progs_[0]) for b in boards]
        results = [build_one(j) for j in first]
        with cf.ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
            results += list(pool.map(build_one, [(b, n) for b in boards for n in progs_[1:]]))
        results.sort(key=lambda r: (boards.index(r[0]), progs_.index(r[1])))     # by board, in menu order
        bins = {}
        for b, name, d, binf, ok, log in results:
            size = binf.stat().st_size if ok and binf.is_file() else 0
            need = gamecfg.load(d).SAVE_PAGES
            fits = save_pages(size, b) >= need
            detail = (f"{size:,} B (room under {device.DEVICES[b].save_safe:,}: {device.DEVICES[b].save_safe - size:,})"
                      + ("" if fits else f"; leaves {save_pages(size, b)} save pages, the game needs {need}")
                      if size else "failed")
            if not check(ok and size > 0 and fits, f"{b}: {d.name}", detail):
                say(log[-2000:])
            bins[(b, d.name)] = binf
        if card and not check.failed:
            say("=== the casino cart and its SD cards ===")
            cart = mkcard.make_cart(binary=lambda d, b: bins[(b, d.name)], platform_dir=plat, version=expected,
                                    boards=boards)
            cart_file = card.with_name(f"CHGame-Casino-{expected}.chgame")
            card.parent.mkdir(parents=True, exist_ok=True)
            data = zipio.write(cart, cart_file)
            lacking = [f"{g.id} ({b})" for g in cart.games for b in boards if b not in g.binaries]
            check(not [i for i in zipio.check(cart_file) if i.error] and not lacking, "the cart",
                  f"{cart_file.name}, {len(cart.games)} games for {', '.join(boards)}, {len(data):,} B"
                  + (f"; no binary for {', '.join(lacking)}" if lacking else ""))
            for b in boards:
                z_path = card_zip(card, b)
                n, wrong = write_card(cart, z_path, b, board_names[b], expected,
                                      [card_zip(card, o).name for o in boards if o != b])
                check(not wrong, f"{b}: SD card contents", f"{z_path.name}, {n} files, {z_path.stat().st_size:,} B"
                      + (f"; not {b}'s: {'; '.join(wrong)}" if wrong else ""))

    say("")
    if check.failed:
        say(f"{len(check.failed)} of {len(check.rows)} checks FAILED")
        return 1
    say(f"all {len(check.rows)} checks passed: a new user gets everything from the one URL.")
    return 0


CARD_README = """{title}
{rule}

This card is for the {name} ({board}). Each board revision has its own card,
because its games are built for that board's pins: a board of another
revision shows them greyed out and will not install them.{others}

Copy everything in this zip (the GAMES folder and the files beside it) to the
root of a FAT32 (or FAT16) microSD card. Put the card in the CHGame and
switch it on: the game menu lists every game. A starts one; holding START
for 3 seconds in a game goes back to the menu.

The menu is part of the CHGame bootloader. A board that does not show it
needs the menu bootloader once: in the Arduino IDE, choose Tools > Board >
CHGame Boards > {name}, Tools > Bootloader > SD Text Menu (Rainbow or Static),
Tools > Programmer > CHGame USB,
then Tools > Burn Bootloader.

The same games come as one file, CHGame-Casino-{version}.chgame, beside this
zip, with every board's programs: the format games are shared in (the
repository's spec/chgame.md).
`chgame cart deploy CHGame-Casino-{version}.chgame --card E:\\ --device {board}`
writes this card from it.

Your own sketches: with Tools > Board > {name}, Sketch > Export Compiled
Binary leaves a .chg file in the sketch's build folder. Copy it into GAMES
(a short name, like MYGAME.CHG).
"""


def write_card(cart, z_path: Path, board: str, name: str, version: str, others: list[str]):
    """One board's SD card contents (chcart's runtime preparation for that
    board) as a zip, with a README.txt naming the board (name: its Tools >
    Board name; others: the other boards' zips). Returns (the number of card
    files, the CHG files its bootloader would refuse)."""
    files = runtime.prepare(cart, board)
    wrong = []
    for path in files:
        if path.upper().endswith(".CHG"):
            try:
                chgpack.parse(files[path], target=chgpack.target_of(board))
            except chgpack.ChgError as e:
                wrong.append(f"{path}: {e}")
    Path(z_path).parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(z_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("README.txt", card_readme(version, board, name, others))
        for path in sorted(files):
            zi = zipfile.ZipInfo(path, date_time=(2026, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, files[path])
    return len(files), wrong


def card_readme(version: str, board: str, name: str, others: list[str]) -> str:
    """The README.txt of one board's card zip: it names the board. others:
    the other boards' card zips."""
    title = f"CHGame {version}: the SD card for the game menu, {name}"
    note = ("" if not others else f"\nThe other board's card is {others[0]}." if len(others) == 1
            else f"\nThe other boards' cards are {', '.join(others)}.")
    return CARD_README.format(title=title, rule="=" * len(title), name=name, board=board, version=version,
                              others=note)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dist", type=Path, default=OUT / "stage")
    ap.add_argument("--port", type=int, default=serve.DEFAULT_PORT)
    ap.add_argument("--all", action="store_true", help="also compile every game and app from the installed package")
    ap.add_argument("--card", type=Path,
                    help="with --all: write each board's SD card contents to this zip, {board} its name "
                         "(without {board}, -<board> is added to the zip's name); the cart goes beside them")
    ap.add_argument("--jobs", type=int, default=DEFAULT_JOBS)
    a = ap.parse_args(argv)
    if a.card and not a.all:
        ap.error("--card needs --all")
    if not shutil.which("arduino-cli"):
        fail("arduino-cli is not on the PATH")
    return run(a.dist, a.port, a.all, a.card, a.jobs)


if __name__ == "__main__":
    sys.exit(main())
