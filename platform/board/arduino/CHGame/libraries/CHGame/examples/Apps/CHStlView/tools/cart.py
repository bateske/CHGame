"""docs/cart.png, the app's picture in the visual menu: STL VIEWER in the
app's cyan over a depth-cued wireframe, a turned icosahedron, inside the
corner marks of its screen (tools/boxart.py: the house style, in the apps'
secret-agent colours). `chgame boxart` redraws it; edit this, not the PNG."""
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import boxart as bx  # noqa: E402
from boxart import INK, WHITE, CYAN, BLUE, NAVY  # noqa: E402

TEAL = (WHITE, CYAN, BLUE)


def icosahedron():
    p = (1 + 5 ** 0.5) / 2
    v = [(-1, p, 0), (1, p, 0), (-1, -p, 0), (1, -p, 0), (0, -1, p), (0, 1, p),
         (0, -1, -p), (0, 1, -p), (p, 0, -1), (p, 0, 1), (-p, 0, -1), (-p, 0, 1)]
    e = sorted({tuple(sorted((i, j))) for i in range(12) for j in range(12)
                if i != j and abs(sum((a - b) ** 2 for a, b in zip(v[i], v[j])) - 4) < 1e-6})
    return v, e


def project(v, ax, ay, cx, cy, s):
    x, y, z = v
    x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
    y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
    k = 4 / (4 + z * 0.5)
    return cx + x * s * k, cy - y * s * k, z


def corners(fb, x, y, w, h, c, n=7):
    for cx, cy, dx, dy in ((x, y, 1, 1), (x + w - 1, y, -1, 1), (x, y + h - 1, 1, -1), (x + w - 1, y + h - 1, -1, -1)):
        fb.hline(min(cx, cx + dx * (n - 1)), cy, n, c)
        fb.vline(cx, min(cy, cy + dy * (n - 1)), n, c)


def draw():
    fb = bx.canvas(INK)
    fb.fill_rect(0, 0, 128, 3, NAVY)
    fb.hline(0, 3, 128, CYAN)
    corners(fb, 6, 30, 116, 92, BLUE)
    bx.title(fb, "STL VIEWER", 10, scale=1, colours=TEAL, shadow=NAVY)
    v, edges = icosahedron()
    pts = [project(p, 0.45, 0.6, 64, 78, 22) for p in v]
    for far in (True, False):                           # the far edges first, dark; the near ones bright
        for i, j in edges:
            z = (pts[i][2] + pts[j][2]) / 2
            if (z > 0) == far:
                fb.line(round(pts[i][0]), round(pts[i][1]), round(pts[j][0]), round(pts[j][1]),
                        BLUE if far else (CYAN if z > -0.8 else WHITE))
    return fb


if __name__ == "__main__":
    print(bx.save(draw(), HERE.parent / "docs" / "cart.png"))
