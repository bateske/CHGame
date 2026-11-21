"""The README's casino downloads: a row for every release's cart and SD
cards, newest first and marked the latest.

    python tools/release/downloads.py [VERSION] [--repo bateske/CHGame]

Writes the table between the README's `<!-- downloads:start -->` and
`<!-- downloads:end -->` lines: the rows already there are kept, VERSION's
(platform.txt's by default) goes on top, with its date from its dated
CHANGELOG.md heading, and only it says "latest". Its links are the
release's assets, whose URLs are known before the release exists
(releases/download/v<version>/<file>), so this runs, and is committed,
before release.py publishes: release.py refuses a version the README does
not list first.

The files a release carries (release.py, acceptance.py): the cart
CHGame-Casino-<version>.chgame, with every board's binaries, and one SD
card per board, CHGame-sdcard-<version>-<board>.zip. (0.3.0, the first,
had Rev0 alone and one zip without the board in its name: its row was
written by hand.)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import CHANGELOG, PLATFORM, REPO, fail, platform_version, say  # noqa: E402
import acceptance  # noqa: E402

README = REPO / "README.md"
START, END = "<!-- downloads:start", "<!-- downloads:end -->"
HEAD = ("| Release | The cart: every game, every board | The SD card, per board (unzip onto a FAT32 card) |\n"
        "|---|---|---|")
# The first column: [**0.4.0**](tag url) (2026-12-01), the latest / [0.3.0](...) (2026-10-07)
FIRST = re.compile(r"^\| \[(?:\*\*)?(?P<v>\d+\.\d+\.\d+)(?:\*\*)?\]\((?P<u>[^)]*)\) \((?P<d>[^)]*)\)(?:, the latest)?"
                   r"(?P<rest> \|.*)$")


def released_date(version: str) -> str:
    m = re.search(r"(?m)^## " + re.escape(version) + r" \((\d{4}-\d{2}-\d{2})\)", CHANGELOG.read_text(encoding="utf-8"))
    if not m:
        fail(f"{CHANGELOG.relative_to(REPO)} has no dated '## {version} (YYYY-MM-DD)' heading: date it first.")
    return m.group(1)


def row(version: str, date: str, repo: str) -> str:
    base = f"https://github.com/{repo}/releases/download/v{version}"
    boards = acceptance.package_boards(PLATFORM)            # {"rev0": "CHGame Rev0", ...}, boards.txt's order
    names = ", ".join(n.replace("CHGame ", "") for n in boards.values())
    cart = f"CHGame-Casino-{version}.chgame"
    cards = " · ".join(f"[{n.replace('CHGame ', '')}]({base}/CHGame-sdcard-{version}-{b}.zip)"
                       for b, n in boards.items())
    tag = f"https://github.com/{repo}/releases/tag/v{version}"
    return f"| [{version}]({tag}) ({date}) | [`{cart}`]({base}/{cart}) ({names}) | {cards} |"


def section(text: str) -> tuple[int, int]:
    a, b = text.find(START), text.find(END)
    if a < 0 or b < a:
        fail(f"{README.relative_to(REPO)} has no '{START} ... {END}' lines for the downloads table.")
    return text.index("\n", a) + 1, b


def rows(text: str) -> list[str]:
    a, b = section(text)
    return [ln for ln in text[a:b].splitlines() if FIRST.match(ln)]


def top_version(text: str | None = None) -> str | None:
    """The version the README lists first (the latest), or None."""
    r = rows(text if text is not None else README.read_text(encoding="utf-8"))
    return FIRST.match(r[0]).group("v") if r else None


def write(version: str, repo: str) -> None:
    text = README.read_text(encoding="utf-8")
    keep = [ln for ln in rows(text) if FIRST.match(ln).group("v") != version]
    out = [row(version, released_date(version), repo)] + keep
    lines = []
    for i, ln in enumerate(out):
        m = FIRST.match(ln)
        v = f"**{m.group('v')}**" if i == 0 else m.group("v")
        lines.append(f"| [{v}]({m.group('u')}) ({m.group('d')}){', the latest' if i == 0 else ''}{m.group('rest')}")
    a, b = section(text)
    README.write_text(text[:a] + HEAD + "\n" + "\n".join(lines) + "\n" + text[b:], encoding="utf-8", newline="\n")
    say(f"{README.name}: {version} listed first, the latest; {len(keep)} older")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("version", nargs="?", help="defaults to platform.txt's")
    ap.add_argument("--repo", default="bateske/CHGame", help="OWNER/REPO on GitHub")
    a = ap.parse_args(argv)
    write(a.version or platform_version(), a.repo)
    return 0


if __name__ == "__main__":
    sys.exit(main())
