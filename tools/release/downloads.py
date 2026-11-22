"""The README's game downloads: one line with the latest release's cart and
SD card.

    python tools/release/downloads.py [VERSION] [--repo bateske/CHGame]

Writes the line between the README's `<!-- downloads:start -->` and
`<!-- downloads:end -->` lines, in "The built-in games": VERSION
(platform.txt's by default), its cart and the newest board's SD card zip.
Its links are the release's assets, whose URLs are known before the
release exists (releases/download/v<version>/<file>), so this runs, and is
committed, before release.py publishes: release.py refuses a version the
README does not list.

The files a release carries (release.py, acceptance.py): the cart
CHGame-Casino-<version>.chgame, with every board's binaries, and one SD
card per board, CHGame-sdcard-<version>-<board>.zip. (0.3.0, the first,
had Rev0 alone and one zip without the board in its name: its line was
written by hand.)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import PLATFORM, REPO, fail, platform_version, say  # noqa: E402
import acceptance  # noqa: E402

README = REPO / "README.md"
START, END = "<!-- downloads:start", "<!-- downloads:end -->"
# The line: **0.4.0**: [`CHGame-Casino-0.4.0.chgame`](url) · [`CHGame-sdcard-0.4.0-rev1.zip`](url)
LINE = re.compile(r"^\*\*(?P<v>\d+\.\d+\.\d+)\*\*")


def newest_board(boards: dict[str, str]) -> str:
    """The highest rev<n> the package defines (rule 9: the newest board)."""
    return max(boards, key=lambda b: int(re.sub(r"\D", "", b) or 0))


def line(version: str, repo: str) -> str:
    """The cart, the newest board's card, then each older board's as a
    short 'legacy' link."""
    base = f"https://github.com/{repo}/releases/download/v{version}"
    boards = acceptance.package_boards(PLATFORM)
    board = newest_board(boards)
    cart = f"CHGame-Casino-{version}.chgame"
    card = f"CHGame-sdcard-{version}-{board}.zip"
    older = " · ".join(f"[legacy {boards[b].replace('CHGame ', '')} card]({base}/CHGame-sdcard-{version}-{b}.zip)"
                       for b in boards if b != board)
    return f"**{version}**: [`{cart}`]({base}/{cart}) · [`{card}`]({base}/{card})" + (f" · {older}" if older else "")


def section(text: str) -> tuple[int, int]:
    a, b = text.find(START), text.find(END)
    if a < 0 or b < a:
        fail(f"{README.relative_to(REPO)} has no '{START} ... {END}' lines for the downloads.")
    return text.index("\n", a) + 1, b


def top_version(text: str | None = None) -> str | None:
    """The version the README lists (the latest), or None."""
    text = text if text is not None else README.read_text(encoding="utf-8")
    a, b = section(text)
    for ln in text[a:b].splitlines():
        m = LINE.match(ln)
        if m:
            return m.group("v")
    return None


def write(version: str, repo: str) -> None:
    text = README.read_text(encoding="utf-8")
    a, b = section(text)
    README.write_text(text[:a] + line(version, repo) + "\n" + text[b:], encoding="utf-8", newline="\n")
    say(f"{README.name}: {version} listed as the latest")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("version", nargs="?", help="defaults to platform.txt's")
    ap.add_argument("--repo", default="bateske/CHGame", help="OWNER/REPO on GitHub")
    a = ap.parse_args(argv)
    write(a.version or platform_version(), a.repo)
    return 0


if __name__ == "__main__":
    sys.exit(main())
