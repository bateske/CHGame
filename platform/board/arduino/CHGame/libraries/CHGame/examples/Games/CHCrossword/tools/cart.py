"""docs/cart.png, the game's picture in the visual menu: CROSSWORD over a
corner of a grid, WORDS across and CODE down (tools/boxart.py: the house
style).
`chgame boxart` redraws it; edit this, not the PNG."""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import boxart as bx  # noqa: E402
from boxart import INK, WHITE, NAVY, CREAM, GOLD, GREY, BLUE  # noqa: E402

GRID = ["#C###",
        "WORDS",
        "#D#.#",
        ".E...",
        "##.##"]
CELL = 19


def draw():
    fb = bx.canvas(NAVY)
    fb.dither(0, 0, 128, 128, INK, 0)
    bx.title(fb, "CROSSWORD", 10, scale=1)
    x0, y0 = 64 - len(GRID[0]) * CELL // 2, 30
    fb.fill_rect(x0 - 2, y0 - 2, len(GRID[0]) * CELL + 3, len(GRID) * CELL + 3, INK)
    for r, row in enumerate(GRID):
        for c, ch in enumerate(row):
            x, y = x0 + c * CELL, y0 + r * CELL
            if ch == "#":
                fb.fill_rect(x, y, CELL - 1, CELL - 1, INK)
                continue
            fb.fill_rect(x, y, CELL - 1, CELL - 1, WHITE if ch == "." else CREAM)
            if ch != ".":
                bx.tile(fb, x, y, ch, None, CELL - 1, CELL, face=CREAM, edge=CREAM)
    fb.fill_rect(x0, y0 + CELL, 5 * CELL - 1, 2, BLUE)  # (the clue being solved)
    fb.rect(2, 2, 124, 124, GOLD)
    return fb


if __name__ == "__main__":
    print(bx.save(draw(), HERE.parent / "docs" / "cart.png"))
