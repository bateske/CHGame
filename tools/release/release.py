"""Build and publish a CHGame board package release.

    python tools/release/release.py [VERSION] [--repo bateske/CHGame] [--dry-run] [--skip-go] [--skip-tests]
                                    [--no-accept]

Checks the tree, runs the uploader's parity tests, builds the Go uploader
for every host, archives it, packs the platform and writes the index, runs
the new-user test against them (acceptance.py: a fresh arduino-cli installs
them from a local server, every example compiles from the installed package
for every board, and the casino cart, with every board's binaries, and one
SD card's contents per board, CHGame-sdcard-<version>-<board>.zip, are made
from those builds),
then publishes all of it as a GitHub release tagged v<version> (notes: the
matching section of platform/board/CHANGELOG.md) and re-uploads the index
to every earlier v* release, so a user on an explicit version URL is
offered the update too. --dry-run builds everything into out/dist/ and
publishes nothing.

VERSION defaults to platform.txt's version= line and must equal it (that
number is what Boards Manager compares with an installed package; a release
without a bump there prompts nobody). The tag and every archive URL derive
from it, because an index whose URLs do not match where the assets land
installs nothing, with a checksum error as the only clue.

Preconditions (each is checked, with the fix in the message):
  - platform/board/CHANGELOG.md has a `## <version>` section (to publish,
    dated: `## 0.3.0 (2026-10-05)`, not `(not yet released)`);
  - the committed bootloader binaries in platform/board/arduino/CHGame/
    bootloaders/CHGame (rev0's five there, each later board's in its own
    folder, rev1/) are tracked by git and match
    platform/bootloader/release/SHA256SUMS (the bootloader is rebuilt with
    platform/bootloader/build.sh and tools/dist.sh, not here), and they are
    every file boards.txt's Tools > Bootloader names;
  - the Go tool's version (main.go) equals the Python package's;
  - the README's casino downloads list this version first, the latest
    (tools/release/downloads.py writes the row; a dry run only warns);
  - to publish: gh is installed and logged in, the tree is clean, and HEAD
    is origin/main (gh creates the tag on the remote).
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (BIN_DIR, BOOTLOADER, CHANGELOG, DIST, GO_DIR, HOSTS, PLATFORM, PLATFORM_TXT, REPO,  # noqa: E402
                     changelog_section, fail, platform_version, python_uploader_version, run, say, sha256,
                     uploader_version)
import acceptance  # noqa: E402
import build_uploader  # noqa: E402
import downloads  # noqa: E402
import make_package  # noqa: E402
import make_tool_archives  # noqa: E402

BOOTLOADERS = PLATFORM / "bootloaders" / "CHGame"
SUMS = BOOTLOADER / "release" / "SHA256SUMS"
# committed path under bootloaders/CHGame -> its name in release/SHA256SUMS. Each
# board's five (Tools > Bootloader): rev0's at the top, rev1's in rev1/, as
# platform/bootloader/tools/dist.sh writes both folders and SHA256SUMS lists them
# ("rev1/chgame_sdboot.bin").
BOOT_NAMES = ("chgame_sdboot.bin", "chgame_sdboot_static.bin", "chgame_sdvisual.bin",
              "chgame_sdvisual_static.bin", "chgame_boot_nomenu.bin")
BOOT_FILES = {f"{sub}{n}": f"{sub}{n}" for sub in ("", "rev1/") for n in BOOT_NAMES}


def check_preconditions(version: str, publish: bool) -> str:
    pv = platform_version()
    if version != pv:
        fail(f"{PLATFORM_TXT.relative_to(REPO)} says version={pv}, not {version}.\n"
             "Bump it first: Boards Manager compares that number to decide whether to offer an update.")
    notes = changelog_section(version)
    if not notes:
        fail(f"{CHANGELOG.relative_to(REPO)} has no '## {version}' section; move Unreleased under it first.")
    if publish and f"## {version} (not yet released)" in CHANGELOG.read_text(encoding="utf-8"):
        fail(f"{CHANGELOG.relative_to(REPO)}: date the '## {version}' heading before publishing.")
    sums = {ln.split()[1].lstrip("*"): ln.split()[0] for ln in SUMS.read_text(encoding="utf-8").splitlines() if ln.strip()}
    tracked = set(make_package.tracked_files())         # what the platform archive packs (tracked files only)
    for committed, released in BOOT_FILES.items():
        f = BOOTLOADERS / committed
        if not f.exists() or sums.get(released) != sha256(f):
            fail(f"bootloaders/CHGame/{committed} does not match {SUMS.relative_to(REPO)}: run "
                 "platform/bootloader/build.sh and platform/bootloader/tools/dist.sh, commit, then release.")
        if f not in tracked:
            fail(f"bootloaders/CHGame/{committed} is not tracked by git, so the platform archive would not "
                 "carry it: commit it, then release.")
    named = re.findall(r"(?m)^\s*[A-Za-z0-9_]+\.menu\.boot\.\w+\.bootloader\.file=CHGame/(.+?)\s*$",
                       (PLATFORM / "boards.txt").read_text(encoding="utf-8"))
    unchecked = sorted(set(named) - set(BOOT_FILES))
    if unchecked or not named:
        fail("boards.txt's Tools > Bootloader names " + (", ".join(f"bootloaders/CHGame/{n}" for n in unchecked)
             or "no bootloaders/CHGame file") + f", which release.py's BOOT_FILES does not check against "
             f"{SUMS.relative_to(REPO)}: add it there (and to platform/bootloader/tools/dist.sh).")
    gv, pyv = uploader_version(), python_uploader_version()
    if gv != pyv:
        fail(f"chgame-upload versions differ: host/go/main.go says {gv}, host/py says {pyv}")
    # The README's casino downloads list this release first (its links are known before it exists).
    if downloads.top_version() != version:
        msg = (f"README.md's casino downloads do not list {version} first: run "
               f"`python tools/release/downloads.py {version}` and commit it")
        if publish:
            fail(msg + " before releasing.")
        say("warning: " + msg + ".")
    if publish:
        if not shutil.which("gh"):
            fail("gh CLI not found; install it (or use --dry-run and upload the assets by hand)")
        if run(["gh", "auth", "status"], check=False).returncode:
            fail("gh is not logged in: gh auth login")
        if run(["git", "status", "--porcelain"], cwd=REPO).stdout.strip():
            fail("working tree is not clean; commit before releasing")
        run(["git", "fetch", "-q", "origin"], cwd=REPO)
        head = run(["git", "rev-parse", "HEAD"], cwd=REPO).stdout.strip()
        main = run(["git", "rev-parse", "origin/main"], cwd=REPO).stdout.strip()
        if head != main:
            fail("HEAD is not origin/main; push first, the release tag is created on the remote")
    return notes


def run_tests() -> None:
    say("=== the uploader's parity tests ===")
    r = run([sys.executable, "-m", "unittest", "discover", "-s", str(BOOTLOADER / "test" / "protocol")],
            cwd=REPO, check=False)
    if r.returncode:
        fail((r.stdout or "") + (r.stderr or ""))
    say("  python: ok")
    go = build_uploader.find_go()
    r = run([go, "test", "./..."], cwd=GO_DIR, check=False, env=None)
    if r.returncode:
        fail((r.stdout or "") + (r.stderr or ""))
    say("  go:     ok")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("version", nargs="?", help="defaults to platform.txt's, and must match it")
    ap.add_argument("--repo", default="bateske/CHGame", help="OWNER/REPO on GitHub")
    ap.add_argument("--dry-run", action="store_true", help="build everything, publish nothing")
    ap.add_argument("--skip-go", action="store_true", help="use the binaries already in out/chgame-upload/")
    ap.add_argument("--skip-tests", action="store_true")
    ap.add_argument("--no-accept", action="store_true",
                    help="skip the new-user test, and with it the cart and the SD card zips (not for a real release)")
    a = ap.parse_args(argv)
    version = a.version or platform_version()
    tag = f"v{version}"
    base_url = f"https://github.com/{a.repo}/releases/download/{tag}"
    index_url = f"https://github.com/{a.repo}/releases/latest/download/package_chgame_index.json"

    notes = check_preconditions(version, publish=not a.dry_run)
    if not a.skip_tests:
        run_tests()
    say("=== the uploader for every host ===")
    if a.skip_go:
        missing = [h for h, _, _, s in HOSTS if not (BIN_DIR / h / f"chgame-upload{s}").is_file()]
        if missing:
            fail("--skip-go, but these are not built: " + ", ".join(missing))
    else:
        build_uploader.build()
    say("=== packaging ===")
    DIST.mkdir(parents=True, exist_ok=True)
    make_tool_archives.package_tool(base_url)
    archive = make_package.build_archive(version)
    index = make_package.build_index(version, archive, base_url)

    assets = [index, archive] + sorted(DIST.glob(f"chgame-upload-{uploader_version()}-*.tar.bz2"))
    if a.no_accept:
        if not a.dry_run:
            fail("--no-accept is for dry runs: a release is tested as a new user would install it")
    else:
        # One SD card zip per board (acceptance fills in {board}), and the cart, with every board's binaries.
        card = DIST / f"CHGame-sdcard-{version}-{{board}}.zip"
        if acceptance.run(DIST, acceptance.serve.DEFAULT_PORT, True, card, acceptance.DEFAULT_JOBS):
            fail("the new-user test failed (above); nothing published")
        made = [acceptance.card_zip(card, b) for b in acceptance.package_boards(PLATFORM)]
        made.append(card.with_name(f"CHGame-Casino-{version}.chgame"))
        missing = [f.name for f in made if not f.is_file()]
        if missing:
            fail(f"the new-user test did not write {', '.join(missing)}; nothing published")
        assets += made
    say("=== release assets ===")
    for f in assets:
        say(f"  {f.name:60s} {f.stat().st_size:>10,} B")
    say(f"=== release notes ({tag}, from CHANGELOG.md) ===\n{notes}\n")
    notes_file = DIST / f"release-notes-{version}.md"
    notes_file.write_text(notes + "\n\nAdd this to Arduino IDE, Preferences -> Additional Boards Manager URLs:\n\n"
                          f"    {index_url}\n\nAlready installed? Boards Manager offers this version as an update.\n",
                          encoding="utf-8", newline="\n")
    if a.dry_run:
        say(f"dry run: nothing published. Boards Manager URL once released:\n  {index_url}")
        return 0

    say(f"=== publishing {tag} to {a.repo} ===")
    exists = run(["gh", "release", "view", tag, "--repo", a.repo], check=False).returncode == 0
    if exists:
        run(["gh", "release", "upload", tag, *assets, "--repo", a.repo, "--clobber"], capture=False)
        run(["gh", "release", "edit", tag, "--repo", a.repo, "--notes-file", notes_file], capture=False)
    else:
        # A normal release, never --prerelease: /releases/latest/ skips pre-releases,
        # and that alias is the URL users have.
        run(["gh", "release", "create", tag, *assets, "--repo", a.repo, "--title", f"CHGame {version}",
             "--notes-file", notes_file], capture=False)
    say("=== refreshing the index on earlier releases ===")
    tags = run(["gh", "release", "list", "--repo", a.repo, "--json", "tagName", "--jq", ".[].tagName"]).stdout.split()
    for old in tags:
        if old.startswith("v") and old != tag:
            run(["gh", "release", "upload", old, index, "--repo", a.repo, "--clobber"], capture=False)
            say(f"  {old}")
    say(f"done. Boards Manager URL:\n  {index_url}\n\nNow commit tools/release/chgame_upload_tool.json, which points at {tag}, "
        "and run `git fetch --tags`.\nVerify from a clean state before announcing it (platform/board/docs/building.md, "
        "\"Verifying a release\").")
    return 0


if __name__ == "__main__":
    sys.exit(main())
