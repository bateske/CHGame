"""docs/cart.png, CHMahjong's cover in the visual menu (docs/cover-art.md).
`chgame boxart` redraws it; edit this, not the PNG.

THE BRIEF (revision 2)
  Message: calm mastery. The quiet last move of a perfect game: the sparrow
  (in Chinese the game's very name, ma que) has come down to perch on the
  summit of the turtle, in the lamplight, and looks over at the red dragon
  the player has lifted into the air; its free twin waits on the terrace
  below. Nothing is in a hurry; everything is in its place.

  Composition (a thumbnail in words):
  - Camera 30 degrees down, moved (not turned) a little right of the
    middle, so lines across the table stay level and the terraces' right
    ends show their sides; close: the pyramid breaks the frame left, right
    and below, a stepped mountain of ivory tiles on jade backs, the summit
    just under the middle.
  - Focal point: the sparrow on the summit, facing left into the key light,
    its head drawn by hand: grey crown lit along the brow, a stout horn
    beak (lit ridge, shaded jaw) joined to the forehead, the eye ringed
    apart from the black lores, chestnut from the eye round the nape, a
    cream cheek over the black bib; a streaked chestnut back, a cream wing
    bar, a warm breast (cream, ivory2, ivory1, ivory0 in its shade, never
    the felt's blue). Cream against black: the most contrasty shape below
    the title, set against the brightest felt.
  - Second read: the lifted red dragon (中), held face on at the bird's eye,
    tilted a few degrees toward it (two shears, a pixel's step every 8 px,
    so the steps are even), its top showing as the camera above sees it
    (ivory, then jade), its face lit toward the corner with a gloss; the
    glyph drawn for its size (a brush's weights, not a doubled sprite), its
    bars level, its stem leaning with the tile, carved. A soft night shadow
    lies on the felt under it: it floats. One tapered four-point star at its
    right, a small pip at its left; a small star on its twin, the leftmost
    tile of the front terrace, carved with the same red 中.
  - The lamp hangs over the summit: each tile is one flat level by how far
    it is from it, a top over its front over its side, so the light steps
    down the turtle ring by ring (ivory2 at the summit, ivory1 on the
    terrace below, ivory0, then the felt's blue, then night at the corners
    and the bottom edge): a lit stage, 144 tiles falling into the dark.
    Lit tops get a cream (or ivory2) bevel down the left edge and a lip on
    the front edge, the right edge a step down; lit jade backs a short
    cream glint at their left end. The key's cast shadows take a lit top
    down a step (never to blue). Seams and the gaps the camera looks down
    are night between lit tiles, black in the dark. Faces on every lit top
    (the front terrace's four big and carved: 中, one dot, four bamboo, two
    wan; small ones on the rest, each only where it fits whole); no other
    red dragon, so the pair's story stays clear.
  - Behind: the lamp's pool on the felt, a circle in perspective (a wide
    ellipse): flat felt1 behind the bird's head and body, a narrow night
    rim, black; seams 2.5 px of 25/50/75%, no noise. The title sits on
    black above it with three clear rows between.
  - Title: MAHJONG across the top in a bold Roman, gold leaf (light, a
    dimmer band, light again, a dimmer foot; the feet and bars end in gold),
    over a red lacquer lip and the dark, kerned so every letter's depth
    ends in a pixel of black before the next face; black outline and
    shadow, one solid rim of night round the whole word (the notches
    between letters closed and kept black), a cream bevel on the edges
    facing the key and gold0 on the right edges, glints on the M's top left
    corner and the G's shoulder. It owns the golds.

  Palette (11 own + cream, grey, black, red):
    night felt1          the felt and the dark (with black): the pool, the far
                         tiles, the dots' blue, the title's rim
    ivory0 ivory1 ivory2 bone in three lights (cream above: lips, bevels,
                         glints); ivory0 also the sparrow's tail and the
                         shade of its breast
    jade0 jade1          the tiles' jade backs, bamboo
    wood1                the sparrow's chestnut (black its streaks)
    gold0 gold1 gold2    the title's own: nothing else uses them
    red                  the dragons and characters, the title's lacquer lip
    grey                 the sparrow's crown and jaw

  How it is painted: render3d marches the turtle (its rows of tiles as a
  repeated rounded box) once, for each pixel's tile, face and cast shadow;
  every face is then a flat level on its ramp (no dither on the tiles),
  with seams, lips, bevels, rounded corners and glints. The faces are hand
  stamps placed on the projected middles of the tops (or the middle of what
  shows). The sparrow's body is distance fields lit as a dome and painted in
  flat regions; its head is a hand-drawn patch. The lifted tile is drawn
  upright on the pixels and turned by two shears. PICK rings the lifted tile
  in the menu's rainbow (index 15, as the game rings a picked tile): left
  off, as on a still cover the static magenta reads as a UI frame.

  Font: Pix Romana by helianthus-games (OFL), at its own size, every stroke
  a pixel bolder, kerned by set_title(); the J's tail a row shorter by hand
  (tools/art/title.txt).
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import numpy as np  # noqa: E402
import artkit as ak  # noqa: E402
from artkit import render3d as R  # noqa: E402

TITLE = HERE / "art" / "title.txt"

# ---- the scene ------------------------------------------------------------------------

TW, TD, TT = 1.0, 1.32, 0.62          # a tile: width (x), depth (z), thickness (y)
GAP, ROUND = 0.07, 0.09
BONE = 0.50                           # the ivory face's share of the thickness (the rest is the jade back)
LAYERS = [[12, 8, 10, 12, 12, 10, 8, 12], [6] * 6, [4] * 4, [2] * 2, [1]]    # the turtle, rows back to front
# the camera is moved, not turned, off the middle: lines across the table stay level
CAMERA = ((1.1, 6.9, 9.4), (1.1, 1.7, 0.6), 38, (27, 29))                   # pos, target, fov, lens shift
KEY = (-0.55, 0.75, 0.45)
LAMP = ((-0.3, 6.2, 1.0), 5.2, 3.2, 0.95)   # the lamp over the summit (world); a top's level at reach, the reach, the fall per unit
POOL = (70, 65, (56, 31), (66, 34), 2.5)   # the lamp's pool on the felt beyond the turtle (a circle in perspective):
                                            # centre, the felt's and the night's radii (px), the seams' width
BIRD = dict(dx=1, dy=0, k=1.6)        # the sparrow: nudge from the summit's middle, size
TITLE_Y = 4
TITLE_STEPS = [(0, 1, "red"), (1, 2, "black")]   # the letters' carved depth: a lacquer lip, then the dark
TITLE_ROWS = ["gold2"] * 5 + ["gold1"] * 4 + ["gold2"] * 3 + ["gold1"] * 6   # light, a dimmer band, light, the foot
EDGE_ROWS = 120                       # tiles below this row (screen), or on the side edges, sink a level: a vignette
LIFT = (19, 38)                       # the lifted tile's face: top-left (px)
LIFT_WH = (18, 24)
LIFT_STEPS = [(0, -1), (1, -2), (1, -3), (2, -4)]   # its thickness, row by row back from the face
SHEAR = 8                             # its tilt: a pixel's step every SHEAR px (clockwise, toward the bird)
LIFT_SHADOW = (35, 66, 9.5, 2.6)     # its shadow on the felt under it: centre, radii (px)
PICK = False                          # the rainbow rings (the menu turns index 15 through the colour wheel)

TILE_R = ["black", "night", "felt1", "ivory0", "ivory1", "ivory2", "cream"]
JADE_R = ["black", "night", "jade0", "jade1"]
FELT_R = ["black", "night", "felt1"]
WOOD_R = ["black", "wood1"]
BREAST_R = ["ivory0", "ivory1", "ivory2", "cream"]
YY, XX = np.mgrid[0:128, 0:128]


def _box(q, h, r):
    q = np.abs(q) - (h - r)
    return np.linalg.norm(np.maximum(q, 0), axis=1) + np.minimum(q.max(axis=1), 0) - r


def tile_at(p, L):
    """The row and column of layer L's tile nearest each point (clamped)."""
    rows = np.array(LAYERS[L])
    nr = len(rows)
    r = np.clip(np.round(p[:, 2] / TD + (nr - 1) / 2), 0, nr - 1).astype(int)
    n = rows[r]
    c = np.clip(np.round(p[:, 0] / TW + (n - 1) / 2), 0, n - 1).astype(int)
    return r, c


def centre(L, r, c):
    rows = LAYERS[L]
    n = np.asarray(rows)[r]
    return np.stack([(c - (n - 1) / 2) * TW, np.full(np.shape(r), (L + 0.5) * TT), (r - (len(rows) - 1) / 2) * TD], -1)


def pyramid(p):
    h = np.array([(TW - GAP) / 2, TT / 2 - 0.004, (TD - GAP) / 2])
    best = np.full(len(p), 1e9)
    for L, rows in enumerate(LAYERS):
        nr = len(rows)
        r0 = np.round(p[:, 2] / TD + (nr - 1) / 2)
        for dr in (0, -1, 1):
            r = np.clip(r0 + dr, 0, nr - 1).astype(int)
            n = np.asarray(rows)[r]
            c0 = np.round(p[:, 0] / TW + (n - 1) / 2)
            for dc in (0, -1, 1):
                c = np.clip(c0 + dc, 0, n - 1).astype(int)
                best = np.minimum(best, _box(p - centre(L, r, c), h, ROUND))
    return best


# ---- the faces: hand stamps, drawn for the size a top shows ----------------------------
# letters: r red, b blue (felt1), g jade1, d jade0, k black, n night, c cream, i ivory1, . the tile
STAMPS = {
    "chun": [".....rr.....",
             "rrrrrrrrrrrr",
             "rr...rr...rr",
             "rr...rr...rr",
             "rrrrrrrrrrrr",
             ".....rr.....",
             ".....rr....."],
    "dot1": ["...bbbbbb...",
             ".bbggggggbb.",
             "bgg.rrrr.ggb",
             "bg.rr..rr.gb",
             "bgg.rrrr.ggb",
             ".bbggggggbb.",
             "...bbbbbb..."],
    "bam4": ["..gg....gg..",
             "..dd....dd..",
             "..gg....gg..",
             "............",
             "..gg....gg..",
             "..dd....dd..",
             "..gg....gg.."],
    "wan2": ["...kkkkkk...",
             "............",
             ".kkkkkkkkkk.",
             "............",
             ".rr.r..r.rr.",
             "rrrrrrrrrrrr",
             "..rr.rr.rr.."],
}
SMALL = {                                        # the tops further off: 5-8 x 3-5
    "dot3": ["rr......", "rr.bb...", "...bb.rr", "......rr"],
    "dot2": ["bb...", "bb...", "...bb", "...bb"],
    "bam3": ["g..g..g", "g..g..g", "d..d..d"],
    "bam2": ["gg..gg", "dd..dd", "gg..gg"],
}
KEYS = {"r": "red", "b": "felt1", "g": "jade1", "d": "jade0", "k": "black", "n": "night", "c": "cream",
        "i": "ivory1"}
FACES = {(2, 3, 0): "chun", (2, 3, 1): "dot1", (2, 3, 2): "bam4", (2, 3, 3): "wan2",
         (3, 1, 0): "dot2", (3, 1, 1): "bam2", (2, 2, 0): "bam3", (2, 2, 3): "dot3", (2, 1, 0): "bam2",
         (2, 1, 3): "dot2"}
TWIN = (2, 3, 0)                      # the lifted red dragon's free twin


def stamp(pic, rows, cx, cy, where, keys=KEYS, carve=None):
    """A face's pixels centred on (cx, cy), only if the whole of it lies
    where `where` is (a face cut by an edge reads as specks). carve: a
    colour for the engraving's shadow, a pixel right of and under each
    stroke on the tile. Returns the ink (None if it did not fit)."""
    h, w = len(rows), len(rows[0])
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    ink_ = np.zeros((128, 128), bool)
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            x, y = x0 + i, y0 + j
            if ch in keys:
                if not (0 <= x < 128 and 0 <= y < 128 and where[y, x]):
                    return None
                ink_[y, x] = True
    if carve:
        pic.put((ak.shift(ink_, 1, 0) | ak.shift(ink_, 0, 1)) & ~ink_ & where, carve)
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            x, y = x0 + i, y0 + j
            if ch in keys and 0 <= x < 128 and 0 <= y < 128 and where[y, x]:
                pic.px(x, y, keys[ch])
    return ink_


def fit(rows, cx, cy, where, reach=6):
    """The nearest centre to (cx, cy) where the whole face lies on `where`
    (a top partly hidden behind another tile shows its face on what shows)."""
    h, w = len(rows), len(rows[0])
    ink_ = [(i, j) for j, row in enumerate(rows) for i, ch in enumerate(row) if ch != "."]
    best = None
    for dy in range(-reach, reach + 1):
        for dx in range(-reach, reach + 1):
            x0, y0 = int(round(cx - w / 2)) + dx, int(round(cy - h / 2)) + dy
            if all(0 <= x0 + i < 128 and 0 <= y0 + j < 128 and where[y0 + j, x0 + i] for i, j in ink_):
                d = dx * dx + dy * dy
                if best is None or d < best[0]:
                    best = (d, x0 + w / 2, y0 + h / 2)
    return best[1:] if best else None


# ---- the lifted tile: the red dragon the player has picked up, its twin below ---------

CHUN_BIG = [".....rr.....",                # 中 drawn for its size, a brush's weight: a heavier
            "....rrr.....",                # head to the stem, the box's left side thicker where
            "rrrrrrrrrrr.",                # the stroke turns, its top bar hooked down at the
            "rrrrrrrrrrrr",                # right, the tail tapering
            "rrr..rr...rr",
            "rr...rr...rr",
            "rr...rr...rr",
            "rr...rr...rr",
            "rrrrrrrrrrrr",
            "rrrrrrrrrrrr",
            ".....rr.....",
            ".....rr.....",
            ".....rr.....",
            ".....r......"]


def lifted(P, x, y, w, h, steps, bone=2):
    """A tile held up face on, drawn upright on a scratch picture, its
    top-left at (x, y): the face, its top and right edges as the camera
    above sees them (`steps` back from the face: ivory, then the jade back),
    a black outline. Returns the scratch picture, what it drew, the face
    and the glyph's mask (drawn after the tilt)."""
    pic = ak.Picture.blank(P, "rainbow")
    face = np.zeros((128, 128), bool)
    face[y:y + h, x:x + w] = True
    for cx, cy in ((x, y), (x + w - 1, y), (x, y + h - 1), (x + w - 1, y + h - 1)):
        face[cy, cx] = False                                   # rounded corners
    acc = face.copy()
    layers = []
    for dx_, dy_ in steps:
        lay = ak.shift(face, dx_, dy_) & ~acc
        layers.append(lay)
        acc |= lay
    ak.outline(pic, acc, "black")
    for k, lay in enumerate(layers, 1):
        topm = lay & (YY < y)                                  # the top edge, lit
        rightm = lay & ~topm                                   # the right edge, in shade
        if k <= bone:
            pic.put(topm, "cream" if k == 1 else "ivory2")
            pic.put(rightm, "ivory1" if k == 1 else "ivory0")
        else:
            pic.put(topm, "jade1")
            pic.put(rightm, "jade0")
    d = (XX - x) + (YY - y)
    pic.put(face, "ivory1")                                    # turned a little from the lamp: ivory2 only
    pic.put(face & (d < 22), "ivory2")                         # toward the top left corner
    pic.put(face & (d >= 4) & (d <= 5), "cream")               # a gloss: the lamp's reflection across the corner
    pic.put(face & ~ak.shift(face, 0, 1), "cream")             # the face's lit top and left bevel
    pic.put(face & ~ak.shift(face, 1, 0), "cream")
    pic.put(face & ~ak.shift(face, 0, -1), "ivory0")           # its bottom and right fall away
    pic.put(face & ~ak.shift(face, -1, 0), "ivory0")
    gm = np.zeros((128, 128), bool)
    gw, gh = len(CHUN_BIG[0]), len(CHUN_BIG)
    gx, gy = x + (w - gw) // 2, y + (h - gh) // 2
    for j, row in enumerate(CHUN_BIG):
        for i, ch in enumerate(row):
            if ch == "r":
                gm[gy + j, gx + i] = True
    drawn = pic.idx != pic.pal["rainbow"]
    return pic, drawn, face, gm


def sheared(xs, ys, cx, cy, step, rows_only=False):
    """Where the pixels (xs, ys) land, turned: rows shifted (a pixel per
    `step` rows), then columns (a pixel per `step` columns); rows_only keeps
    horizontal strokes level (the glyph: its bars stay straight, its stems
    lean with the tile), moved down as the tile is at its middle."""
    x1 = xs - np.floor((ys - cy) / step).astype(int)
    if rows_only:
        return x1, ys + int(np.floor((x1.mean() - cx) / step))
    return x1, ys + np.floor((x1 - cx) / step).astype(int)


def shear(src, drawn, cx, cy, step):
    """The scratch picture's pixels turned a few degrees clockwise by two
    shears (rows, then columns), each a pixel per `step`: every pixel lands
    on exactly one, so no holes and even steps. Returns (idx, mask)."""
    out = np.zeros((128, 128), np.int16) - 1
    ys, xs = np.nonzero(drawn)
    x1, y1 = sheared(xs, ys, cx, cy, step)
    ok = (x1 >= 0) & (x1 < 128) & (y1 >= 0) & (y1 < 128)
    out[y1[ok], x1[ok]] = src.idx[ys[ok], xs[ok]]
    return out, out >= 0


# ---- the sparrow ---------------------------------------------------------------------

def cov(cv, d):
    return ak.px_mean((d < 0).astype(np.float32), cv.s)


STREAKS = [((-0.5, -12.2), (1.5, -11.0)), ((2.0, -11.6), (4.4, -10.4)), ((6.5, -8.6), (9.5, -7.0)),
           ((5.0, -6.8), (8.6, -5.0))]                          # (local units, from the feet)
# the head, by hand (it carries the picture): cols -5..15 from the left, its
# middle at (7.5, 7.5). k black, g grey crown, h its lit brow, I ivory2,
# c cream cheek, w chestnut, W dark chestnut; the beak a cone: B its lit
# ridge, m its middle, b its shaded jaw; e the eye, o its glint
HEAD = ["..........kkkkkk.....",
        "........kkhhhgggkk...",
        ".......khhggggggwwk..",
        "......khhgggggggwwwk.",
        ".....khhgggggggwwwwwk",
        "....khgggggIwwwwwwwwk",
        ".kBBBggggoewwwwwwwwwk",
        "kmmmmkkkIeewwwwwwwwwk",
        ".kbbbkkkcccccccwwwwwk",
        "..kkkkkkccccccccwwww.",
        "....kkkkkcccccccwww..",
        ".....kkkkkccccccww...",
        "......kkkkkccccc.....",
        ".......kkkkk........."]
HEAD_KEYS = {"k": "black", "g": "grey", "h": "ivory1", "I": "ivory2", "c": "cream", "w": "wood1",
             "W": "ivory0", "B": "ivory2", "m": "ivory1", "b": "grey", "e": "black", "o": "cream"}


def sparrow(cv, pic, fx, fy, k):
    """A cock house sparrow perched facing left, its feet at (fx, fy):
    grey crown, chestnut from the eye to the nape, cream cheek, black bib,
    streaked chestnut back and wing with a cream bar, a warm pale breast.
    The body is distance fields lit as a dome; the head is drawn by hand."""
    Pp = cv.P

    def L(x, y):
        return fx + x * k, fy + y * k
    hx, hy = -5.0, -14.5                                # the head's middle (local units)
    body = ak.ellipse(Pp, *L(1.2, -7.4), 7.4 * k, 5.3 * k, angle=28)
    head = ak.circle(Pp, *L(hx, hy), 6.0)
    tail = ak.polygon(Pp, [L(5.5, -8.5), L(14.0, -3.8), L(13.4, -1.8), L(5.5, -4.5)])
    wing = ak.ellipse(Pp, *L(4.0, -8.4), 6.6 * k, 3.4 * k, angle=24)
    legs = ak.union(ak.segment(Pp, *L(-1.0, -2.5), *L(-1.5, 0.2), 0.55 * k),
                    ak.segment(Pp, *L(2.5, -2.5), *L(2.5, 0.2), 0.55 * k))
    trunk = ak.smin(body, head, 2.5 * k)
    whole = ak.union(trunk, tail, wing, legs)
    m = {nm: cov(cv, d) >= 0.5 for nm, d in dict(whole=whole, body=trunk, tail=tail,
                                                wing=wing, legs=legs).items()}
    lx, ly = (XX + 0.5 - fx) / k, (YY + 0.5 - fy) / k
    n = ak.dome(cv, trunk, 4.0 * k)
    dif, _ = ak.light(n)
    dif = ak.px_mean(dif, cv.s)
    hpx, hpy = L(hx, hy)
    ox, oy = int(round(hpx - 7.5)) - 5, int(round(hpy - 7.5))
    hm = np.zeros((128, 128), bool)
    for j, row in enumerate(HEAD):
        for i, ch in enumerate(row):
            if ch != "." and 0 <= ox + i < 128 and 0 <= oy + j < 128:
                hm[oy + j, ox + i] = True
    W = m["whole"] | hm
    ak.outline(pic, W, "black")
    bel = m["body"]
    ak.by_level(pic, ak.terrace(0.2 + dif * 3.2, 0.3), BREAST_R, bel, q=1)   # the breast: warm, pale in the light
    back = bel & (ly < -8.5 + (lx - 1.5) * 0.45) & (lx > -2)
    ak.by_level(pic, 0.6 + dif * 1.0, WOOD_R, back, q=1)
    bib = bel & ~back & (ly >= -12.6) & (ly < -8.6) & (lx < -3.6 - 0.6 * (ly + 12.6))
    pic.put(bib, "black")
    wg = m["wing"]
    ak.by_level(pic, 0.7 + dif * 1.0, WOOD_R, wg, q=1)
    pic.put(wg & (np.abs(ly - (-8.4 + (lx - 4.5) * 0.45)) < 0.6) & (lx < 5), "cream")
    for a, b in STREAKS:                                          # the mantle's and the wing's dark streaks
        for x_, y_ in ak.line_px([L(*a), L(*b)]):
            if 0 <= x_ < 128 and 0 <= y_ < 128 and (back | wg)[y_, x_]:
                pic.px(x_, y_, "black")
    pic.put(m["tail"] & ~bel & ~wg, "ivory0")
    pic.put(m["legs"] & ~bel, "wood1")
    for j, row in enumerate(HEAD):
        for i, ch in enumerate(row):
            if ch != ".":
                pic.px(ox + i, oy + j, HEAD_KEYS[ch])
    return W


# ---- the title ------------------------------------------------------------------------

def letter_masks(m):
    """The title's letters, each a mask (parts that overlap a letter's
    columns, like a detached serif, join it), left to right."""
    lab = ak.letters(m)
    comps = []
    for k in range(1, lab.max() + 1):
        xs = np.nonzero((lab == k).any(axis=0))[0]
        comps.append([xs.min(), xs.max(), lab == k])
    comps.sort(key=lambda c: c[0])
    out = []
    for c in comps:
        if out and (c[0] <= out[-1][1] + 1 and c[1] - c[0] < 5 or c[1] <= out[-1][1]):
            out[-1][2] = out[-1][2] | c[2]
            out[-1][1] = max(out[-1][1], c[1])
        elif out and out[-1][1] - out[-1][0] < 5 and c[0] <= out[-1][1] + 1:
            out[-1][2] = out[-1][2] | c[2]
            out[-1][1] = max(out[-1][1], c[1])
        else:
            out.append(c)
    return [c[2] for c in out]


def body_of(F, steps):
    acc = F.copy()
    for dx, dy, _ in steps:
        acc |= ak.shift(F, dx, dy)
    return acc


def set_title(m, y, steps, extra=None):
    """Kerns the letters: each as close to the last as leaves a pixel of
    black between the last one's depth and its face (8-way), plus `extra`
    px per pair. Returns the faces placed on the picture, centred."""
    L = letter_masks(m)
    extra = extra or [0] * len(L)
    faces, x = [], 0
    for i, g in enumerate(L):
        xs = np.nonzero(g.any(axis=0))[0]
        g = g[:, xs.min():xs.max() + 1]
        if faces:
            prev = ak.dilate(body_of(faces[-1], steps), 1, diag=True)
            while (ak.place(g, x, y) & prev).any():
                x += 1
            x += extra[i]
        faces.append(ak.place(g, x, y))
        x += 1
    allm = np.zeros((128, 128), bool)
    for F in faces:
        allm |= body_of(F, steps)
    xs = np.nonzero(allm.any(axis=0))[0]
    dx = (128 - (xs.max() - xs.min() + 1)) // 2 - xs.min()
    return [ak.shift(F, dx, 0) for F in faces]


def pring(m):
    """The pixels just outside a mask (4-way)."""
    return ak.dilate(m, 1) & ~m


def close(m, r):
    """Morphological closing (gaps up to about 2r px filled), clear of the
    picture's border."""
    p = r + 2
    big = ak.erode(ak.dilate(np.pad(m, p), r, diag=True), r, diag=True)
    return big[p:-p, p:-p]


def draw_title(pic, faces, steps, rows, glints):
    M = np.zeros((128, 128), bool)
    for F in faces:
        M |= F
    bodies = [body_of(F, steps) for F in faces]
    allb = np.zeros_like(M)
    for B in bodies:
        allb |= B
    out = ak.dilate(allb, 1)                                     # the black outline's reach
    sh = ak.shift(out, 1, 2) | ak.shift(out, 1, 1) | ak.shift(out, 0, 1)
    foot = close(out | sh, 3)                                    # notches between letters closed: kept black
    pic.put(foot, "black")
    pic.put(pring(foot) & ak.outside_of(foot), "night")       # one solid rim of night round it all
    for F, B in zip(faces, bodies):                             # left to right: each letter's outline cuts the last one's depth
        pic.put(pring(B), "black")
        acc = F.copy()
        for dx, dy, c in steps:
            lay = ak.shift(F, dx, dy) & ~acc
            pic.put(lay, c)
            acc |= lay
        pic.put(F, rows[0])
    lip = pic.where(steps[0][2]) & ak.dilate(allb, 1) & ~M          # the lip only in runs of 3+ (none under the top
    pic.put(lip & ((ak.runs(lip, 1) < 3) | ~ak.outside_of(M)), "black")   # serifs) and not in the counters
    top = int(np.nonzero(M.any(axis=1))[0].min())
    for j, c in enumerate(rows):
        row = np.zeros_like(M)
        row[top + j, :] = True
        pic.put(row & M, c)
    cls = ak.bevel_runs(pic, M, "cream", "gold0")
    keep = M & ~ak.shift(M, 0, -1) & (cls == -1)                 # the feet and bars end in gold over the red lip
    for j, c in enumerate(rows):
        pic.put(keep & (YY == top + j), c)
    for gx, gy, arms in glints:
        ak.glint(pic, gx, gy, arms=arms, tip="gold2")
    return M, out | sh


# ---- the picture ----------------------------------------------------------------------

def draw():
    P = ak.Palette({
        "night": "#0A1638", "felt1": "#1E4A94",
        "ivory1": "#BCAA8C", "ivory2": "#E8DABA",
        "jade0": "#0A5040", "jade1": "#1EA26A",
        "ivory0": "#8A7458", "wood1": "#B4602A",
        "gold0": "#94500E", "gold1": "#EAA622", "gold2": "#FFEA8C",
    }, ramps=[TILE_R, JADE_R, BREAST_R, ["gold0", "gold1", "gold2", "cream"]])
    cv = ak.Canvas("#000000")
    s, N = cv.s, cv.N
    pic = ak.Picture.blank(P, "black")

    cp, ct, cf, csh = CAMERA
    cam = R.Camera(cp, ct, fov=cf, shift=csh)
    scene = R.prim(pyramid, 0)
    out = R.render(cv, scene, cam, [R.Mat("#FFFFFF", spec=0.0)], lights=[(KEY, "#FFFFFF", 1.0)],
                   ambient="#000000", ss=2, region=(0, 40, 128, 128))
    o_all, d_all = cam.rays(cv.X.reshape(-1).astype(np.float64), cv.Y.reshape(-1).astype(np.float64))
    hit = (out["mat"] == 0).reshape(-1)
    dep = np.where(hit, out["depth"].reshape(-1), 0.0)
    pw = o_all + d_all * dep[:, None]
    nw = out["normal"].reshape(-1, 3).astype(np.float64)
    pin = pw - nw * 0.03
    Lr = np.clip(np.floor(pin[:, 1] / TT), 0, 4).astype(int)
    tid = np.full(len(pw), -1)
    for k in range(5):
        sel = hit & (Lr == k)
        r, c = tile_at(pin[sel], k)
        tid[sel] = k * 1000 + r * 20 + c
    cls = np.full(len(pw), -1)                       # 0 top, 1 front, 2 right, 3 left
    cls[hit & (nw[:, 1] > 0.6)] = 0
    cls[hit & (nw[:, 2] > 0.6)] = 1
    cls[hit & (nw[:, 0] > 0.6)] = 2
    cls[hit & (nw[:, 0] < -0.6)] = 3
    lum = out["rgb"].mean(-1).reshape(-1)

    c0 = s // 2
    tid_px = tid.reshape(N, N)[c0::s, c0::s]
    cls_px = cls.reshape(N, N)[c0::s, c0::s]
    lit_px = lum.reshape(N, N)[c0::s, c0::s]
    ly = (pin[:, 1].reshape(N, N) % TT)[c0::s, c0::s] / TT
    tiles = tid_px >= 0

    # ---- the lifted tile's shadow, a soft blot on the felt under it (a
    # level and more taken off the pool)
    sx_, sy_, srx, sry = LIFT_SHADOW
    rr_ = np.hypot((XX + 0.5 - sx_) / srx, (YY + 0.5 - sy_) / sry)
    lshadow = np.interp(rr_, [0, 0.8, 1.0, 1.2], [1.0, 1.0, 0.5, 0.0])

    # ---- behind: the lamp's pool on the felt beyond the turtle, a circle in
    # perspective (a wide ellipse), flat plateaus with narrow seams a fixed
    # number of pixels wide: felt, night, black
    pcx, pcy, r1, r2, sw = POOL
    Pc = (XX + 0.5, YY + 0.5)
    d1 = ak.ellipse(Pc, pcx, pcy, *r1)
    d2 = ak.ellipse(Pc, pcx, pcy, *r2)
    fl = 2.0 - np.clip(d1 / sw + 0.5, 0, 1) - np.clip(d2 / sw + 0.5, 0, 1) - lshadow
    ak.by_level(pic, np.clip(fl, 0, 2), FELT_R, ~tiles)

    # ---- the tiles: the lamp over the summit lights each tile by how far it
    # is, one flat level per face: the top, its front a step under, its side
    # turned from the key under that; the ivory face over the jade back; the
    # key's cast shadows a step down on the lit tiles
    lamp = np.array(LAMP[0])
    top_lv, reach, per = LAMP[1], LAMP[2], LAMP[3]
    keys = np.unique(tid_px[tiles])
    tl = np.zeros((128, 128))                        # each tile's level at its top's middle
    info = {}
    for k in keys:
        L, r, c = k // 1000, (k % 1000) // 20, k % 20
        cx_, _, cz_ = centre(L, np.array(r), np.array(c))
        tc = np.array((cx_, (L + 1) * TT, cz_))
        sx, sy = cam.project(tc)
        mine = tid_px == k
        edge_ = sy > EDGE_ROWS or mine[:, :2].any() or mine[:, 126:].any()    # the frame's vignette
        v = top_lv - (np.linalg.norm(lamp - tc) - reach) * per - (1.0 if edge_ else 0.0)
        tl[mine] = v
        info[k] = (L, r, c, sx, sy, v)
    top = tiles & (cls_px == 0)
    front = tiles & (cls_px == 1)
    right = tiles & (cls_px == 2)
    left = tiles & (cls_px == 3)
    edge = tiles & ~(top | front | right | left)
    bone = ly > 1 - BONE
    shade = lit_px < 0.2

    def same(dx, dy):
        return ak.shift(tid_px, dx, dy) == tid_px
    tlr = np.round(tl)
    lit = tlr >= 4                                               # the tops in the lamp: ivory1 and up
    lv = np.zeros((128, 128))
    lv[top] = (tlr - (shade & lit))[top]                         # the key's cast shadows only where they stay ivory
    lv[front | edge | left] = np.where(lit, np.maximum(tlr - 1 - shade, 3), tlr - 1)[front | edge | left]
    lv[right] = np.where(lit, tlr - 1, tlr - 2)[right]           # a side turned from the key: the tile's own thickness
    ak.by_level(pic, np.clip(lv, 0, 6), TILE_R, tiles & (top | bone), q=1)
    jl = np.zeros((128, 128))
    jl[front | left | edge] = np.where(lit, np.maximum(tlr - 1 - shade, 2), tlr - 2)[front | left | edge]
    jl[right] = np.where(lit, 2, tlr - 3)[right]
    ak.by_level(pic, np.clip(jl, 0, 3), JADE_R, tiles & ~bone & ~top, q=1)
    seam = tiles & (~same(1, 0) | ~same(0, 1))
    pic.put(seam, "black")
    pic.put(seam & (tl >= 3.5), "night")                         # between lit tiles: night, not a black cut
    corner = top & (~same(1, 0) | ~same(-1, 0)) & (~same(0, 1) | ~same(0, -1))
    pic.put(corner & ~seam & (tl >= 3.5), "night")
    pic.put(corner & ~seam & (tl < 3.5), "black")
    # the gaps between tiles, where the camera looks down to the felt: a
    # seam, night between lit tiles
    gap = ~tiles & (YY > 60)
    gap &= (ak.shift(tiles, 1, 0) | ak.shift(tiles, 2, 0)) & (ak.shift(tiles, -1, 0) | ak.shift(tiles, -2, 0))
    near = np.maximum(np.maximum(ak.shift(tl, 1, 0), ak.shift(tl, 2, 0)), np.maximum(ak.shift(tl, -1, 0), ak.shift(tl, -2, 0)))
    pic.put(gap, "black")
    pic.put(gap & (near >= 3.5), "night")
    # lit tops: a bevel down the left edge facing the key, the front lip
    # catching the lamp, the right edge a step down
    inner = top & ~seam & ~corner
    lip = inner & ak.shift(front | edge, 0, -1) & same(0, -1)
    lbev = inner & ak.shift(seam, 1, 0)
    rbev = inner & ~same(-1, 0)
    for lo, hi_, c_lip, c_r in ((4.5, 9, "cream", "ivory1"), (3.5, 4.5, "ivory2", "ivory0")):
        band = (tl >= lo) & (tl < hi_) & ~shade
        pic.put(rbev & band, c_r)
        pic.put((lbev | lip) & band, c_lip)
    # polished jade: a short glint along the top of each lit jade back, by
    # its left end (the side the key comes from)
    jade_top = (front | edge) & ~bone & ak.shift((front | edge) & bone, 0, 1) & same(0, 1) & lit & ~shade & ~seam
    jx = ak.shift(seam, 2, 0) | ak.shift(seam, 3, 0)
    pic.put(jade_top & jx & (tl >= 3.5), "cream")

    # ---- faces on the tops the lamp reaches: the front terrace's four by
    # hand (carved), small ones on the rest where they fit whole
    names = sorted(SMALL)
    twin_box = None
    for k in keys:
        L, r, c, sx, sy, v = info[k]
        m = top & (tid_px == k) & ~seam
        if L >= 4 or m.sum() < 12 or v < 3.5:
            continue
        where = ak.erode(m, 1)
        if (L, r, c) in FACES and FACES[(L, r, c)] in STAMPS:
            stamp(pic, STAMPS[FACES[(L, r, c)]], sx, sy + 0.6, where, carve="ivory1")
            if (L, r, c) == TWIN:
                twin_box = m
        else:
            nm = FACES.get((L, r, c)) or names[int(ak.ihash(k, seed=5) * len(names))]
            at = fit(SMALL[nm], sx, sy, where)
            if at:
                stamp(pic, SMALL[nm], *at, where)

    # ---- the red dragon, picked up and held at the bird's eye, tilted a
    # little toward it
    lx0, ly0 = LIFT
    lw, lh = LIFT_WH
    scratch, drawn, face0, gm0 = lifted(P, lx0, ly0, lw, lh, LIFT_STEPS)
    lcx, lcy = lx0 + lw / 2, ly0 + lh / 2
    idx_, lt_m = shear(scratch, drawn, lcx, lcy, SHEAR)
    pic.idx[lt_m] = idx_[lt_m].astype(np.uint8)
    face = np.zeros((128, 128), bool)
    face[sheared(*np.nonzero(face0)[::-1], lcx, lcy, SHEAR)[::-1]] = True
    gm = np.zeros((128, 128), bool)
    gm[sheared(*np.nonzero(gm0)[::-1], lcx, lcy, SHEAR, rows_only=True)[::-1]] = True
    inner_f = face & ~ak.edge(face, "right") & ~ak.edge(face, "bottom") & ~ak.edge(face, "left") & ~ak.edge(face, "top")
    pic.put((ak.shift(gm, 1, 0) | ak.shift(gm, 0, 1)) & ~gm & inner_f, "ivory1")   # the glyph carved: its shadow
    pic.put(gm & face, "red")
    ak.lonely(pic, "ivory2", face & ~gm, into="ivory1")           # no lone light pixel in the glyph's counters
    if PICK:
        pic.put(ak.dilate(lt_m, 1) & ~lt_m & ~tiles, "rainbow")

    # ---- clean-up: lone pixels in the scene (seam crossings, corners) take
    # their neighbours' colour
    ak.despeckle(pic, need=4, keep=lt_m | (YY < 30), passes=2)

    # ---- the sparrow on the summit, its feet's shadow on the tile
    bx_, by_ = cam.project((0.0, 5 * TT, 0.1))
    fx_, fy_ = bx_ + BIRD["dx"], by_ + BIRD["dy"]
    bird = sparrow(cv, pic, fx_, fy_, BIRD["k"])
    foot = ak.shift(bird, 1, 1) & ~bird & top & (YY >= fy_ - 1)
    pic.put(foot, "ivory1")

    # ---- sparkles: one star at the lifted tile's corner, a pip by it, and
    # one on its twin below
    ys_, xs_ = np.nonzero(lt_m)
    ak.glint(pic, int(xs_.max()) + 4, int(ys_.min()) + 7, arms=(3, 3, 3, 3), tip="ivory1")
    ak.glint(pic, int(xs_.min()) - 4, int(ys_.max()) - 6, arms=(1, 1, 1, 1), core="ivory2")
    if twin_box is not None:
        ys_, xs_ = np.nonzero(twin_box)
        ak.glint(pic, int(xs_.max()) - 2, int(ys_.min()) + 1, arms=(1, 2, 1, 1), tip="ivory2")

    # ---- the title: gold leaf on a bold Roman, a red lacquer lip and a
    # mahogany depth, a black outline, one rim of night round it, a bevel,
    # glints
    faces = title_faces()
    M0 = faces[0]
    ys_, xs_ = np.nonzero(M0)
    gl = [(int(xs_.min()) + 1, int(ys_.min()) + 1, (2, 2, 2, 2))]
    G = faces[-1]
    ys_, xs_ = np.nonzero(G)
    gl.append((int(xs_.max()) - 1, int(ys_.min()) + 1, (2, 1, 1, 2)))
    draw_title(pic, faces, TITLE_STEPS, TITLE_ROWS, gl)
    return pic.image()


def title_faces():
    """The title's letters, emboldened, kerned and placed."""
    m = ak.load_mask(TITLE)
    m = ak.embolden(np.pad(m, ((0, 0), (0, 1))))
    return set_title(m, TITLE_Y, TITLE_STEPS)


def title_lines():
    """The title's lettering as drawn here, and its depth, for the title
    screen (tools/titleart.py: the game paints it in the house gold).
    The lacquer lip is one red step: the black one is the outline there."""
    M = np.zeros((128, 128), bool)
    for F in title_faces():
        M |= F
    return [dict(mask=M, depth=1, side="red")]


if __name__ == "__main__":
    import boxart
    boxart.save(draw(), HERE.parent / "docs" / "cart.png")
