"""docs/cart.png, the game's picture in the visual menu: the Mahjong logo
over three tiles, the one of dots, the red dragon and the one of bamboo,
with the visiting sparrow perched on them (tools/boxart.py: the house
style; the faces and the bird are the game's own, tools/art/classic2x.txt and
bird.txt). `chgame boxart` redraws it; edit this, not the PNG."""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import boxart as bx  # noqa: E402
from boxart import INK, CREAM, GOLD, WOOD, FELT, FELT_DK, FELT_LT  # noqa: E402

FACES = HERE / "art" / "classic2x.txt"
BIRD = HERE / "art" / "bird.txt"
FACE_W, FACE_H = 15, 23


def faces():
    """{section: [face rows]} from classic2x.txt ('# dots', '# bamboo' ...)."""
    out, cur = {}, None
    for ln in FACES.read_text(encoding="utf-8").splitlines():
        if ln.startswith("# ") and len(ln.split()) <= 6 and not ln.startswith("#   "):
            cur = out.setdefault(ln[2:].split(":")[0].strip(), [])
        elif cur is not None and ln.strip() and not ln.startswith("#"):
            cur.append(ln.rstrip().split(" "))
    return {k: [[r[i] for r in v] for i in range(len(v[0]))] for k, v in out.items() if v}


def sparrow():
    """The bird's first idle frame (bird.txt '@ idle w h')."""
    rows, on = [], False
    for ln in BIRD.read_text(encoding="utf-8").splitlines():
        if ln.startswith("@ idle "):
            on = True
            continue
        if on:
            if ln.startswith("#"):
                continue
            if not ln.strip():
                if rows:
                    break
                continue
            rows.append(ln.rstrip())
    return rows


def tile(lay, x, y, face):
    """A tile at 1x: the face, its edge below and right (the stack's depth)."""
    lay.fill_rect(x + 2, y + 2, FACE_W + 2, FACE_H + 2, GOLD)
    lay.fill_rect(x + 3, y + 3, FACE_W + 2, FACE_H + 2, WOOD)
    lay.rect(x - 1, y - 1, FACE_W + 2, FACE_H + 2, INK)
    lay.fill_rect(x, y, FACE_W, FACE_H, CREAM)
    bx.letters(lay, face, x, y, {"g": FELT_LT})


def draw():
    fb = bx.canvas()
    bx.felt(fb, FELT, FELT_DK)
    bx.logo(fb, bx.logo_from_assets(HERE.parent), 8)
    f = faces()
    lay = bx.layer()
    tile(lay, 1, 1, f["dots"][0])
    tile(lay, 21, 1, f["dragons"][0])
    tile(lay, 41, 1, f["bamboo"][0])
    bx.blit(fb, lay, 4, 50, 2, (0, 0, 62, 29))
    bx.letters(fb, sparrow(), 88, 36)
    return fb


if __name__ == "__main__":
    print(bx.save(draw(), HERE.parent / "docs" / "cart.png"))
