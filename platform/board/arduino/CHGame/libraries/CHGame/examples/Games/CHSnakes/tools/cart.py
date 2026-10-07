"""docs/cart.png, the game's picture in the visual menu (docs/cover-art.md).
`chgame boxart` redraws it; edit this, not the PNG.

THE BRIEF
  Message: climb the ladders, dodge the snakes: one bad roll and you're
  swallowed.

  Composition (the cartoon-character pilot of the collection):
  - Focal point: the gap between the tongue's fork and the cherries, a third
    of the way down and just left of centre. A big viper strikes in from the
    right: a wedge of a snout, a black lid sloping down to the snout (the
    scowl) over an amber eye with red smouldering in its lower rows and a
    black slit turned on the cherries, a spade-broad skull, jaws flung open
    (upper 25 degrees up; the lower jaw slender, ending in a round chin well
    clear of the coil), two long fangs, a sly grin hooked into the cheek,
    speed lines trailing off the back of its skull (it has just lunged) and
    its shadow on the board under the chin (it is off the ground). Its
    forked tongue runs out of the black throat, level at the end, a 2-px tip
    and two clean 1-px prongs, and stops a hair short of a pair of cherries
    (the game's token), over a lit square of the board. The cherries hang
    from a rung by thin stems that join under a leaf and hook over it:
    glossy (a solid wood crescent hugging the upper-left rim, a cream
    specular, red, a wine terminator, a black crescent, a violet bounce),
    wide white eyes with pinprick pupils fixed on the snake, worried brows
    tilted up to the middle, mouths open in a scream, two teardrops of sweat
    flung off the left one's crown (round end out, the point trailing back).
    The gap is the tension.
  - The story's third beat: a die has just rolled to a stop on the board
    between them, one red pip up (snake eyes, the bad roll), its face lit
    cream, its side in the board's violet shade, its shadow cast down right.
  - Camera low, three-quarter. The ladder rises from the bottom-left
    foreground and leans away into the dark (its rungs in perspective, each
    gap 0.9 of the last): it carries the eye up to the cherries and on to
    the word LADDERS, and runs on behind the coil to the bottom edge (a lit
    wood edge on its rails). The snake's body crosses in front of the ladder
    and runs off the left edge, a row of regular diamonds down its lit side,
    each lit on its upper edges; its neck runs down the right edge, so the
    body frames the scene. The left of the picture is calm dark board, so
    the cherries read against it.
  - Behind: the board's squares (crisp, one square a pixel) recede to a
    dithered far edge under the title and sink to dark in the corners.
  - Light: warm key from the top left (lime tops, cream glints), a violet
    rim from the board on the shadow side (and under the lower jaw), a lime
    back-light on the skull's top right; the light gathers on the cherries
    and the jaws and falls off to a dark frame. The coil's lower and right
    parts sink to teal.
  - The mouth, rendered: black deep in the throat, a checkered seam, wine
    toward the lips; the palate (in the upper jaw's shadow) darker than the
    floor; red gums just inside both lips, which are outlined in black, so
    the fangs and tongue sit inside a mouth.
  - The title sits in an even violet halo hugging everything it draws (a
    1-px dusk rim, vmid falling off to night), alone in gold: SNAKES big and
    chrome-banded (a crisp horizon, its soft seams one checkered row), &
    LADDERS stacked under it, two black rows between them; the glints sit
    wholly on the faces. It is the first read; the head the second, the
    cherries the third, the die the fourth.

PALETTE (11 own + cream, grey, black, red)
  night, vmid, dusk  violet, dark to light: the void, the halo behind the
                     title, the board's squares, the snake's, cherries' and
                     jaw's cool bounce, the die's shaded side, the speed
                     lines, the sweat's shade (green's complement: the snake
                     pops)
  snk0, snk1, snk2   the snake, its markings, the stalks: teal shadow to lime
  wine, wood         the ladder (cel: wood lit, wine shade), the mouth, the
                     cherries' terminator and lit crescent, the snake's iris,
                     the title's extrusion
  gold0-2            the title's own: nothing else uses them
  red                cherries, tongue, gums, the eye's lower rows, the die's
                     pip; cream the glints, fangs, eyes, die, sweat; grey the
                     fangs' shade and points, the die's lower edge

FONT  title.txt (SNAKES): DRD, from the bmf collection (author and terms not
      stated: a `?` face, chosen because no clear-terms face is this heavy and
      round at its own size; the clear ones that are, Starseed Pro and
      Superstar, are drawn doubled). The N redrawn as a capital and the K
      given a wedge by hand.
      title2.txt (& LADDERS): JoyquestSample by narehop (commercial use); the
      & redrawn by hand with open counters so it cannot read as an 8, the R's
      bowl notched.
"""
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import artkit as ak  # noqa: E402
from artkit import color as C  # noqa: E402

TITLE = HERE / "art" / "title.txt"
TITLE2 = HERE / "art" / "title2.txt"
# chrome gold: a bright sky, a dark horizon, its bright reflection, the ground
TITLE_ROWS = ["gold2"] * 7 + ["gold1"] * 3 + ["gold0", "gold2"] + ["gold1"] * 6 + ["gold0"] * 4
TITLE2_ROWS = ["gold2"] * 4 + ["gold1"] * 5 + ["gold0"] * 3

COL = {
    "night": "#120A2A", "vmid": "#2A1A62", "dusk": "#4C2E94",
    "snk0": "#0B4A3A", "snk1": "#3C9C2E", "snk2": "#A6E04A",
    "wine": "#5E1430", "wood": "#E8A456",
    "gold0": "#A4500C", "gold1": "#F4B41C", "gold2": "#FFEE84",
}
FIX = {"cream": "#FFF4D6", "grey": "#808080", "black": "#000000", "red": "#D62020"}


def c(name):
    return C.to_float(COL.get(name) or FIX[name])


# ---- helpers ----------------------------------------------------------------------

def smooth(a, b, v):
    t = np.clip((v - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def smax(a, b, k=2.0):
    """A rounded intersection (the corner where two cuts meet, filleted)."""
    return -ak.smin(-a, -b, k)


def cel(v, names, edges, soft=0.05):
    """Toon shading: v (0..1) through flat tones `names`, changing at `edges`,
    each change `soft` wide (the quantiser dithers just that seam)."""
    out = np.broadcast_to(c(names[0]), np.shape(v) + (3,)).copy()
    for k, e in enumerate(edges):
        w = smooth(e - soft, e + soft, v)[..., None]
        out += w * (c(names[k + 1]) - c(names[k]))
    return out


def tube(P, pts, radii, s0=0.0):
    """A tube along a polyline: its distance field, its round normal (as if
    a cylinder seen side on), the arc length along it and its direction."""
    X, Y = P
    pts = np.asarray(pts, dtype=np.float64)
    radii = np.interp(np.linspace(0, 1, len(pts)), np.linspace(0, 1, len(radii)), radii)
    best = np.full(X.shape, 1e9, np.float32)
    nx, ny, s, tx, ty, rr = (np.zeros(X.shape, np.float32) for _ in range(6))
    cum = s0
    for k in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[k], pts[k + 1]
        dx, dy = x1 - x0, y1 - y0
        L = float(np.hypot(dx, dy)) or 1e-6
        t = np.clip(((X - x0) * dx + (Y - y0) * dy) / (L * L), 0, 1)
        r = radii[k] + (radii[k + 1] - radii[k]) * t
        ox, oy = X - (x0 + t * dx), Y - (y0 + t * dy)
        d = np.hypot(ox, oy) - r
        m = d < best
        best = np.where(m, d, best)
        nx = np.where(m, ox / r, nx)
        ny = np.where(m, oy / r, ny)
        s = np.where(m, cum + t * L, s)
        tx = np.where(m, dx / L, tx)
        ty = np.where(m, dy / L, ty)
        rr = np.where(m, r, rr)
        cum += L
    nx, ny = np.clip(nx, -1, 1), np.clip(ny, -1, 1)
    nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
    return {"d": best, "n": np.stack([nx, ny, nz], -1).astype(np.float32), "s": s, "t": (tx, ty),
            "r": rr, "len": cum}


def path(*segs, n=14):
    """Bezier segments joined into one list of points."""
    out = []
    for sg in segs:
        pts = ak.bezier(*sg, n=n)
        out += pts if not out else pts[1:]
    return out


def ring_out(m, front):
    """The pixels just outside mask m that no nearer object covers."""
    return ak.dilate(m, 1) & ~m & ~front


def line_px(pts, n=240):
    """The pixels of a 1-pixel line through the points, pixel-perfect: no
    doubled corners, so its steps stay clean."""
    pts = np.asarray(pts, dtype=np.float64)
    seg = np.cumsum(np.r_[0, np.hypot(*np.diff(pts, axis=0).T)])
    t = np.linspace(0, seg[-1], n)
    xs, ys = np.interp(t, seg, pts[:, 0]), np.interp(t, seg, pts[:, 1])
    px = []
    for x, y in zip(np.floor(xs).astype(int), np.floor(ys).astype(int)):
        if not px or px[-1] != (x, y):
            px.append((x, y))
    out = [px[0]]
    for k in range(1, len(px) - 1):
        a, b = out[-1], px[k + 1]
        if abs(a[0] - b[0]) == 1 and abs(a[1] - b[1]) == 1:
            continue                                   # an L corner: skip the elbow
        out.append(px[k])
    if len(px) > 1:
        out.append(px[-1])
    return out


def ink_line(pic, pts, colour, n=240, where=None):
    out = line_px(pts, n)
    for x, y in out:
        if 0 <= x < 128 and 0 <= y < 128 and (where is None or where[y, x]):
            pic.px(x, y, colour)
    return out


def despeck(pic, protect=None, passes=2):
    """Lone pixels (unlike all eight neighbours and not part of a dither: no
    pixel of their colour two away) take their neighbours' commonest colour."""
    a = pic.idx
    n = 0
    for _ in range(passes):
        pad = np.pad(a, 2, mode="edge")
        H, W = a.shape
        nb8 = [pad[2 + dy:2 + dy + H, 2 + dx:2 + dx + W] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dx or dy]
        lone = np.ones_like(a, dtype=bool)
        for q in nb8:
            lone &= q != a
        two = np.zeros_like(lone)
        for dy, dx in ((-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)):
            two |= pad[2 + dy:2 + dy + H, 2 + dx:2 + dx + W] == a
        lone &= ~two
        lone[0, :] = lone[-1, :] = lone[:, 0] = lone[:, -1] = False
        if protect is not None:
            lone &= ~protect
        if not lone.any():
            break
        stack = np.stack(nb8, -1)
        ys, xs = np.nonzero(lone)
        for y, x in zip(ys, xs):
            vals, cnt = np.unique(stack[y, x], return_counts=True)
            a[y, x] = vals[np.argmax(cnt)]
        n += len(ys)
    return n


def outside_of(M):
    """The background region connected to the picture's border (so a
    letter's enclosed counters are not in it)."""
    out = np.zeros_like(M)
    out[0, :] = ~M[0, :]
    out[-1, :] = ~M[-1, :]
    out[:, 0] |= ~M[:, 0]
    out[:, -1] |= ~M[:, -1]
    while True:
        g = ak.dilate(out, 1) & ~M
        if (g == out).all():
            return out
        out = g


def bevel(pic, M, hi, lo):
    """A title's bevel on its outer contour: the light colour only on top-
    and left-facing edges, the dark one on every bottom- and right-facing
    edge (it wins at corners), where the stroke is 3 px thick; enclosed
    counters get none, so small letters stay clean."""
    sh = ak.shift
    out = outside_of(M)
    thick_v = M & sh(M, 0, 1) & sh(M, 0, -1)
    thick_h = M & sh(M, 1, 0) & sh(M, -1, 0)
    top = M & sh(out, 0, 1)                   # the pixel above is outside
    bot = M & sh(out, 0, -1)
    left = M & sh(out, 1, 0)
    right = M & sh(out, -1, 0)
    low = (bot & sh(thick_v, 0, 1)) | (right & sh(thick_h, 1, 0))
    high = ((top & sh(thick_v, 0, -1)) | (left & sh(thick_h, -1, 0))) & ~bot & ~right
    pic.put(low, lo)
    pic.put(high, hi)
    return high, low


def distance_px(M, n):
    """Pixel distance (0..n, n = farther) from mask M, octagonal."""
    d = np.full(M.shape, float(n), np.float32)
    acc = M.copy()
    d[acc] = 0
    for k in range(1, n):
        acc = ak.dilate(acc, 1, diag=k % 2 == 0)
        d[acc & (d == n)] = k
    return d


def up(a, s):
    """A pixel-sized array blown up to the canvas's samples."""
    return np.repeat(np.repeat(a, s, 0), s, 1)


def at_px(a, s):
    """A canvas-sized array sampled at the pixels' centres."""
    return a[s // 2::s, s // 2::s]


def glint_in(face, x, y, size=1, reach=4):
    """The nearest spot to (x, y) where a sparkle of `size` lies wholly on
    the face, a pixel clear of its edge (so it never breaks an outline)."""
    inner = ak.erode(face, 1, diag=True)
    best = None
    for dy in range(-reach, reach + 1):
        for dx in range(-reach, reach + 1):
            px, py = x + dx, y + dy
            pts = [(px, py)] + [(px + k * a, py + k * b) for k in range(1, size + 1)
                                for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            if all(0 <= u < 128 and 0 <= v < 128 and inner[v, u] for u, v in pts):
                d = dx * dx + dy * dy
                if best is None or d < best[0]:
                    best = (d, px, py)
    return best[1:] if best else (x, y)


RIM = np.array([0.75, 0.45, 0.0])          # the cool rim light, from the right and below
BACK = np.array([0.5, -0.86, 0.0])         # the back light: a lime edge on the top right


# ---- the picture ---------------------------------------------------------------------

def draw():
    P_ = ak.Palette(COL, ramps=[["black", "night", "vmid", "dusk"],
                                ["black", "night", "snk0", "snk1", "snk2", "cream"],
                                ["black", "wine", "red"],
                                ["wood", "cream"],
                                ["gold0", "gold1", "gold2", "cream"]],
                    pairs=[("grey", "cream"), ("red", "wood")])
    cv = ak.Canvas("#000000")
    P = cv.P
    X, Y = P
    S = cv.s

    # the title's footprint, known up front for the halo behind it
    m1 = ak.load_mask(TITLE)
    m2 = ak.load_mask(TITLE2)
    x1, y1 = ak.centred_x(m1) - 1, 3
    x2, y2 = ak.centred_x(m2), 30
    TM = ak.place(m1, x1, y1) | ak.place(m2, x2, y2)
    # everything the title will draw: faces, extrusions, outlines, shadows
    def drawn(m, x, y, depth, sdx, sdy):
        F = ak.place(m, x, y)
        for k in range(1, depth + 1):
            F = F | ak.shift(ak.place(m, x, y), k, k)
        F = ak.dilate(F, 1)
        return F | ak.shift(F, sdx, sdy) | ak.shift(F, int(sdx > 0), int(sdy > 0))
    TF = drawn(m1, x1, y1, 3, 1, 2) | drawn(m2, x2, y2, 2, 1, 1)

    # the stage's falloff: light gathers on the cherries and the jaws
    VIG = smooth(30, 74, np.hypot((X - 64) * 0.9, (Y - 76) * 1.15))

    # -- the void, and a calm violet halo round the title: an even glow
    # hugging everything the title draws, the same on both sides
    t = ak.radial(P, 64, 22, 90, 42)
    cv.paint(1.0, ak.stops(t, [(0, COL["night"]), (0.55, "#0A0618"), (1, "#000000")]), dither=1)
    dt = up(distance_px(TF, 12), S)
    halo = np.clip(1 - (dt - 1) / 5.0, 0, 1) * 0.9 * smooth(-1.0, 3.0, Y) * smooth(49.5, 45.5, Y)
    cv.paint(np.minimum(halo * 2.0, 1.0), ak.stops(halo, [(0, COL["night"]), (0.75, COL["vmid"]), (1, COL["dusk"])]),
             dither=1)

    # -- the board: the game's squares in violet (green is the snake's alone),
    # on a plane receding into the dark; crisp flat squares near, dithered far
    HZ = 57.5
    quad = [(-8, HZ), (136, HZ), (300, 170), (-172, 170)]
    U, V = ak.quad_uv(P, quad, 10, 10)
    on = ak.inside_uv(U, V, 10, 10) < 0
    iu, iv = np.floor(U).astype(int), np.floor(V).astype(int)
    chk = ((iu + iv) % 2 == 0)
    near = np.clip(V / 7.0, 0, 1)
    pool = np.clip(1 - ak.radial(P, 70, 92, 50, 26), 0, 1)
    left_dark = smooth(34, 6, X) * 0.5                           # the left is calm: the cherries read on it
    corner = smooth(44, 14, np.hypot(128 - X, 128 - Y)) * 0.75                # the bottom right sinks to the dark
    lite = np.clip(0.05 + 0.35 * near + 0.9 * pool - left_dark - corner, 0, 1)
    # one light value a square (its mean), so near squares are flat
    sq = np.where(on, (np.clip(iv, 0, 9) * 10 + np.clip(iu, 0, 9)), 100)
    mean = np.bincount(sq.ravel(), lite.ravel(), minlength=101) / np.maximum(np.bincount(sq.ravel(), minlength=101), 1)
    lsq = mean[sq]
    farw = 1 - smooth(1.6, 3.2, V)                      # far rows: a smooth dithered fade
    lv = lsq * (1 - farw) + lite * farw
    lit_sq = ak.stops(lv, [(0, "#000000"), (0.3, COL["night"]), (0.62, COL["vmid"]), (1, COL["dusk"])])
    dark_sq = ak.stops(lv, [(0, "#000000"), (0.45, "#000000"), (0.62, COL["night"]), (1, COL["vmid"])])
    L3 = lv[..., None]
    near_lit = np.where(L3 > 0.55, c("dusk"), np.where(L3 > 0.3, c("vmid"), c("night")))
    near_dark = np.where(L3 > 0.55, c("night"), np.where(L3 > 0.3, c("night"), c("black")))
    fl = np.where(chk[..., None], near_lit, near_dark)
    sm = np.where(chk[..., None], lit_sq, dark_sq)
    board = sm * farw[..., None] + fl * (1 - farw[..., None])
    fade_edge = smooth(-0.05, 0.6, V)                      # the far edge melts into the dark
    # one square per pixel (sampled at its centre): the seams come out clean
    board = up(at_px(board, S), S)
    cv.paint(up(at_px((on * fade_edge).astype(np.float32), S), S), board)
    cv.dith[on & (farw < 0.5)] = 0.0
    cv.dith[on & (farw >= 0.5)] = 1.0

    # -- the ladder: rails from the bottom-left foreground leaning away
    Lb, Lt = np.array([3.0, 136.0]), np.array([38.0, 49.0])
    Rb, Rt = np.array([44.0, 136.0]), np.array([61.0, 49.0])

    def rail_pt(a, b, f):
        return a + (b - a) * f

    def depth_of(y):
        return np.clip((136 - y) / 90.0, 0, 1)

    def wood(T, lift=0.0):
        dif, spec = ak.light(T["n"])
        rim = smooth(0.55, 0.85, (T["n"][..., :2] * RIM[:2]).sum(-1))
        frame = np.maximum(smooth(10, 0, X), smooth(112, 128, Y))
        v = np.clip(dif * 1.15 + lift - depth_of(Y) * 0.32 - VIG * 0.3 - frame * 0.6, 0, 1)
        col = cel(v, ["black", "wine", "wood"], [0.1, 0.62], 0.03)
        col += ((spec > 0.55) & (v > 0.5))[..., None] * (c("cream") - col) * 0.85
        col += (rim * (v < 0.5) * (v > 0.1))[..., None] * (c("dusk") - col) * 0.8
        return col

    # the ladder's shadow on the board
    sh = ak.cover(cv, ak.ellipse(P, 30, 128, 36, 10), soft=28) * 0.8
    cv.paint(sh * on, "#000000", dither=1)

    rungs = [0.117, 0.247, 0.364, 0.47, 0.565, 0.651, 0.728, 0.797, 0.859, 0.915]   # perspective: each gap 0.9 of the last
    CHR = 0.797                                            # the cherries' rung
    lad_id = cv.new_id("ladder")
    for f in rungs:
        a, b = rail_pt(Lb, Lt, f), rail_pt(Rb, Rt, f)
        rr = 2.1 - 1.0 * f
        T = tube(P, [tuple(a), tuple(b)], [rr, rr])
        cv.paint(ak.cover(cv, T["d"]), wood(T, 0.25 if f == CHR else 0.0), dither=0, oid=lad_id)
    for a, b in ((Lb, Lt), (Rb, Rt)):
        T = tube(P, [tuple(a), tuple(b)], [3.0, 1.5])
        cv.paint(ak.cover(cv, T["d"]), wood(T), dither=0, oid=lad_id)

    # -- the snake's body: the neck down the right, in front of the ladder,
    # across the front of its left rail and off the edge
    front_pts = path(((112, 78), (125, 92), (124, 111), (106, 119)),
                     ((106, 119), (86, 126), (58, 120), (30, 103)),
                     ((30, 103), (16, 97), (4, 94), (-12, 92)), n=16)

    def snake_col(T, side, dim=0.0, fall=0.55, soft=0.02):
        n = T["n"]
        dif, spec = ak.light(n)
        tx, ty = T["t"]
        cross = (tx * n[..., 1] - ty * n[..., 0]) * side
        belly = smooth(0.42, 0.52, cross)
        scute = (np.mod(T["s"], 2.8) < 0.95) & (belly > 0.5)
        rim = smooth(0.7, 0.85, (n[..., :2] * RIM[:2]).sum(-1))
        frame = np.maximum(np.maximum(smooth(9, 0, X), smooth(118, 128, Y)), smooth(119, 128, X))
        v = np.clip(0.12 + dif * 0.95 - VIG * fall - dim - frame * 0.4, 0, 1)
        # cel bands, crisp: teal shadow, green, a lime top; never black inside
        back = cel(v, ["snk0", "snk1", "snk2"], [0.34, 0.7], soft)
        bel = cel(v - scute * 0.25, ["snk0", "snk1", "snk2"], [0.3, 0.62], soft)
        col = back + (bel - back) * belly[..., None]
        col += (rim * (v < 0.34))[..., None] * (c("dusk") - col)               # the violet bounce off the board
        brim = smooth(0.8, 0.9, (n[..., :2] * BACK[:2]).sum(-1)) * (v < 0.6) * (v > 0.12) * (1 - belly)
        col += brim[..., None] * (c("snk1") - col)
        col += ((spec > 0.5) & (VIG < 0.3))[..., None] * (c("cream") - col) * 0.9
        snake_col.crisp = scute & (belly > 0.5)
        return col

    radii_f = [7.0, 7.4, 7.6, 7.2, 7.0, 7.2, 7.4, 7.6]
    Tf = tube(P, front_pts, radii_f)
    # the neck shows its throat (belly to the left); past the turn it twists
    # so the belly runs along the coil's underside
    s_turn = 46.0
    side_f = np.where(Tf["s"] < s_turn, 1.0, -1.0) * smooth(0, 1, np.abs(Tf["s"] - s_turn) / 6.0)
    front_id = cv.new_id("snake_front")
    # the band's shadow falls on the rungs
    Ts = tube(P, [(x + 1.0, y + 2.2) for x, y in front_pts], radii_f)
    cv.paint(ak.cover(cv, Ts["d"]) * (cv.oid == lad_id) * 0.8, "#000000")
    cv.paint(ak.cover(cv, Tf["d"]), snake_col(Tf, side_f, fall=0.38), dither=0, oid=front_id)
    cv.tag(snake_col.crisp & (Tf["d"] < 0), dither=0)

    # -- the head: striking in from the right, jaws flung wide
    HO = (1.0, 3.0)                                        # where the head sits (5 px clear of LADDERS)
    Ph = (X - HO[0], Y - HO[1])

    def hp(x, y):
        return int(round(x + HO[0])), int(round(y + HO[1]))

    head_id = cv.new_id("head")
    mouth_id = cv.new_id("mouth")
    hx, hy = 106.0, 81.0                                   # the jaws' hinge
    UP = np.tan(np.radians(25.0))                          # the upper lip's rise
    DN = np.tan(np.radians(27.0))                          # the lower lip's fall
    skull = ak.ellipse(Ph, 103.0, 63.5, 14.5, 14.0)
    cheek = ak.circle(Ph, 111.5, 73.0, 8.5)                # the jaw muscles: a spade at the back
    snout = ak.polyline(Ph, [(100.0, 61.0), (86.0, 59.0), (72.5, 61.0)], r=10.5, r1=4.6)   # a wedge
    brow = ak.polyline(Ph, [(86.0, 55.6), (96.5, 52.3)], r=3.4)                         # over the eye
    upper = ak.smin(ak.smin(ak.smin(skull, cheek, 4), snout, 4), brow, 2.5)
    lip_u = ak.halfplane(Ph, hx, hy - 1, -UP, 1.0)         # below the upper lip: cut
    upper = smax(upper, lip_u, 1.6)
    # the lower jaw: slender, ending in a round chin well clear of the coil
    lowcap = ak.polyline(Ph, [(hx + 2, hy + 4.5), (92.0, 92.2), (78.6, 98.0)], r=6.6, r1=2.9)
    lip_l = ak.halfplane(Ph, hx, hy + 1, -DN, -1.0)        # above the lower lip: cut
    lower = smax(lowcap, lip_l, 2.2)
    tip_u = (hx - 37.5, hy - 1 - 37.5 * UP)
    tip_l = (hx - 29.5, hy + 1 + 29.5 * DN)
    mouth = ak.polygon(Ph, [(hx + 4, hy - 6), (hx + 4, hy + 6), (tip_l[0] + 1.5, tip_l[1] + 2.0),
                            (tip_u[0] + 1.5, tip_u[1] - 2.0)])          # its top and bottom hide under the jaws
    # inside: black deep in the throat, wine toward the lips; the palate (in
    # the upper jaw's shadow) darker than the floor the key light reaches
    dh = np.hypot(Ph[0] - (hx - 1), Ph[1] - hy)
    floor_ = smooth(hy - 4, hy + 8, Ph[1] + (hx - Ph[0]) * 0.12)
    depth_ = np.clip((dh - 4.0) / 25.0, 0, 1) * (0.62 + 0.38 * floor_)
    cv.paint(ak.cover(cv, mouth), ak.stops(depth_, [(0, "#000000"), (0.35, "#000000"), (0.9, COL["wine"]), (1, COL["wine"])]),
             dither=1, oid=mouth_id)

    def head_col(d, w, belly_from=None, gl=None):
        n = ak.dome(cv, d, w)
        dif, spec = ak.light(n)
        rim = smooth(0.55, 0.85, (n[..., :2] * RIM[:2]).sum(-1))
        v = np.clip(dif * 1.05, 0, 1)
        col = cel(v, ["snk0", "snk1", "snk2"], [0.36, 0.7], 0.06)
        bm = None
        if belly_from is not None:
            bel = cel(v, ["snk1", "snk2"], [0.4], 0.04)
            bm = smooth(-0.4, 0.4, belly_from)
            col = col + (bel - col) * bm[..., None]
        k = (rim * (v < 0.36))
        if bm is not None:
            k = k * (1 - bm)
        col += k[..., None] * (c("dusk") - col) * 0.9
        brim = smooth(0.8, 0.9, (n[..., :2] * BACK[:2]).sum(-1)) * (v < 0.7)
        col += brim[..., None] * (c("snk2") - col)
        if gl is not None:
            col += ((spec > 0.45) & gl)[..., None] * (c("cream") - col) * 0.9
        return col

    # the lower jaw: a lit lip, a green side, a teal underside; crisp cel bands
    lj_gl = np.hypot(Ph[0] - 85.0, Ph[1] - 94.0) < 2.2
    cv.paint(ak.cover(cv, lower), head_col(lower, 3.0, gl=lj_gl), dither=0.5, oid=head_id)
    cv.tag(lower < 0, dither=0)

    up_gl = (np.hypot(Ph[0] - 78.0, Ph[1] - 55.5) < 3.2) | (np.hypot(Ph[0] - 104.0, Ph[1] - 51.0) < 2.6)
    cv.paint(ak.cover(cv, upper), head_col(upper, 6.0, gl=up_gl), dither=0.5, oid=head_id)

    # fangs: two long ones from the upper lip, cream lit, grey shade and point
    fang_id = cv.new_id("fangs")

    def lip_y(x):
        return hy - 1 - (hx - x) * UP

    fangs = []
    for x0, w, ln in ((71.2, 5.4, 12.5), (82.0, 5.0, 10.5)):
        a, b = (x0, lip_y(x0) - 1.5), (x0 + w, lip_y(x0 + w) - 1.5)
        tip = (x0 + w * 0.45, lip_y(x0 + w * 0.5) + ln)
        d = ak.polygon(Ph, [a, b, (x0 + w * 0.7, lip_y(x0 + w) + ln * 0.55), tip])
        g = np.clip((Ph[0] - x0) / w, 0, 1)
        tipz = (Ph[1] > tip[1] - 2.2).astype(np.float32)
        col = ak.lerp(FIX["cream"], FIX["grey"], np.maximum((g > 0.62).astype(np.float32), tipz))
        cv.paint(ak.cover(cv, d), col, dither=0, oid=fang_id)
        fangs.append(tip)

    # the tongue, forked: out of the black throat, through the mouth, flicking
    # out over a lit square and stopping just short of the cherries
    tg_id = cv.new_id("tongue")
    # (it arrives level, so its fork can be set by hand, two clean prongs)
    tpath = ak.bezier((hx - 4, hy + 1), (88, 76.0), (76.5, 81.0), (63.6, 81.0), n=40)
    tg = ak.polyline(Ph, tpath, r=1.0)
    cv.paint(ak.cover(cv, tg), FIX["red"], dither=0, oid=tg_id)

    # the eye: amber, a slit pupil fixed on the cherries, under a heavy brow
    eye_id = cv.new_id("eye")
    LID = ((85.0, 61.2), (102.0, 52.2))
    ecx, ecy = 93.6, 59.6
    sclera = ak.inter(ak.circle(Ph, ecx, ecy, 5.8), ak.halfplane(Ph, *LID[0], LID[1][1] - LID[0][1], -(LID[1][0] - LID[0][0])))
    sclera = ak.sub(sclera, ak.circle(Ph, 95.0, 72.4, 8.4))          # the cheek pushes up: a sly grin
    cv.paint(ak.cover(cv, sclera), FIX["cream"], dither=0, oid=eye_id)
    iris = ak.inter(ak.circle(Ph, 91.2, 60.6, 4.2), sclera)
    cv.paint(ak.cover(cv, iris), COL["wood"], dither=0, oid=eye_id)

    # -- the cherries: hanging from a rung by their stalks, terrified
    stalk_id = cv.new_id("stalks")
    cher_ids = [cv.new_id("cherryA"), cv.new_id("cherryB")]
    ry = rail_pt(Lb, Lt, CHR)[1]
    CH = ((29.5, ry + 13.8, 10.4), (46.0, ry + 17.6, 10.9))
    (ax, ay, ar), (bx, by, br) = CH
    J = (41.0, ry - 3.0)
    leaf = ak.ellipse(P, 37.2, ry - 5.6, 4.6, 2.0, angle=-30)       # sprouting from the stems' join
    dif, _ = ak.light(ak.dome(cv, leaf, 1.6))
    cv.paint(ak.cover(cv, leaf), cel(dif, ["snk1", "snk2"], [0.5]), dither=0, oid=stalk_id)
    for cx, cy, r in CH:                                   # their shadow on the ladder
        cv.paint(ak.cover(cv, ak.circle(P, cx + 2, cy + 2.5, r)) * (cv.oid == lad_id) * 0.8, "#000000")
    for (cx, cy, r), cid in zip(CH, cher_ids):
        d = ak.circle(P, cx, cy, r)
        n = ak.sphere_normal(P, cx, cy, r)
        w = ((n * ak.KEY).sum(-1) + 0.45) / 1.45
        col = cel(w, ["black", "wine", "red"], [0.08, 0.24], 0.025)
        cv.paint(ak.cover(cv, d), col, dither=0, oid=cid)

    # -- to pixels: each object keeps to its own colours
    snake = ["black", "night", "snk0", "snk1", "snk2", "cream", "dusk"]
    pic = cv.quantize(P_, exclude=["gold0", "gold1", "gold2"],
                      allow={"cherryA": ["black", "wine", "red", "wood", "dusk"],
                             "cherryB": ["black", "wine", "red", "wood", "dusk"],
                             "stalks": ["black", "snk0", "snk1", "snk2"],
                             "ladder": ["black", "wine", "wood", "cream", "dusk"],
                             "snake_front": snake, "head": snake,
                             "eye": ["black", "cream", "wood"],
                             "mouth": ["black", "wine"], "tongue": ["black", "red"],
                             "fangs": ["black", "cream", "grey"],
                             "background": ["black", "night", "vmid", "dusk"]})
    yy, xx = np.mgrid[0:128, 0:128]

    # the striking head's shadow on the board under its chin (it is off the
    # ground): each square a step darker, so the board still reads
    hsh = at_px(ak.ellipse(P, 97.0, 107.6, 16.0, 6.4, angle=-8), S) < 0
    hsh &= pic.obj("background") & (yy > 90)
    for a_, b_ in (("vmid", "night"), ("dusk", "vmid")):
        pic.put(hsh & pic.where(a_), b_)

    # -- the body's diamonds: regular, a tone down, each lit on its upper
    # edges, stamped along the band's middle where they fit whole
    Bm = pic.obj("snake_front")
    seg = np.cumsum(np.r_[0, np.hypot(*np.diff(np.asarray(front_pts), axis=0).T)])
    DIA = ["....l....", "..llgll..", "llgggggll", "ggggggggg", "..ggggg..", "....g...."]
    inner = ak.erode(Bm, 2)
    for sk in np.arange(58.0, seg[-1], 12.5):
        px_ = np.interp(sk, seg, [p_[0] for p_ in front_pts])
        py_ = np.interp(sk, seg, [p_[1] for p_ in front_pts])
        # each sits where the band is lit green (not down in its teal shade)
        best = None
        for dy_ in (0, -1, -2, -3):
            qx, qy = int(round(px_)) - 4, int(round(py_ - 1.5)) - 3 + dy_
            cells = [(qx + i, qy + j) for j, row in enumerate(DIA) for i, ch in enumerate(row) if ch != "."]
            if not all(0 <= u < 128 and 0 <= v < 128 and inner[v, u] for u, v in cells):
                continue
            lit = sum(pic.idx[v, u] != P_["snk0"] for u, v in cells)
            if best is None or lit > best[0]:
                best = (lit, qx, qy)
        if best:
            ak.patch(pic, best[1], best[2], DIA, {"l": "snk2", "g": "snk0"})

    # the ladder runs on behind the coil to the bottom edge: a lit wood edge
    # down its rails' left sides and along the near rung's top
    Lm = pic.obj("ladder")
    pic.put(Lm & ~ak.shift(Lm, 1, 0) & (yy >= 100) & (yy <= 122) & pic.where("wine"), "wood")
    pic.put(Lm & ~ak.shift(Lm, 0, 1) & (yy >= 105) & (yy <= 118) & (xx >= 12) & (xx <= 40) & pic.where("wine"), "wood")
    # the neck's inner edge: one clean lime line, not the scutes' checker
    Bn = pic.obj("snake_front")
    inner_e = Bn & ~ak.shift(Bn, 1, 0) & (xx >= 100) & (yy >= 84) & (yy <= 111)
    pic.put(inner_e & pic.where("snk1", "snk2"), "snk2")

    # -- outlines, back to front
    order = [pic.obj("ladder"), pic.obj("snake_front"),
             pic.obj("mouth") | pic.obj("tongue") | pic.obj("fangs") | pic.obj("head") | pic.obj("eye"),
             pic.obj("stalks"), pic.obj("cherryA"), pic.obj("cherryB")]
    for k, m in enumerate(order):
        nearer = np.zeros_like(m)
        for m2_ in order[k + 1:]:
            nearer |= m2_
        ring = ring_out(m, nearer)
        if k == 3:                                          # the stalks: no black against the wine rung
            ring &= ~(pic.obj("ladder") & pic.where("wine"))
        pic.put(ring, "black")
    # the lips: a black line where the jaws meet the mouth
    Hd = pic.obj("head")
    Mo = pic.obj("mouth")
    lips = Mo & ak.dilate(Hd, 1)
    pic.put(lips, "black")
    # inside the mouth, by hand: black throat, a checkered seam, wine toward
    # the lips; the palate under the upper jaw a step darker than the floor
    inside = Mo & ~lips & pic.where("black", "wine")
    dpx = at_px(depth_, S)
    under_lip = (yy + 0.5) - ((hy - 1 - (hx - (xx + 0.5)) * UP) + HO[1])      # rows below the upper lip
    v_ = dpx - 0.30 * smooth(6.5, 3.5, under_lip)                              # the palate in shadow
    ck = ak.checker()
    pic.put(inside & (v_ < 0.30), "black")
    pic.put(inside & (v_ >= 0.30) & (v_ < 0.58) & ck, "black")
    pic.put(inside & (v_ >= 0.30) & (v_ < 0.58) & ~ck, "wine")
    pic.put(inside & (v_ >= 0.58), "wine")
    # gums: red just inside both lips, from the front to the throat's dark
    gum = inside & ak.dilate(lips, 1) & (dpx >= 0.42)
    pic.put(gum, "red")
    # the tongue and the fangs get their own black outline
    tgm = pic.obj("tongue")
    pic.put(ak.dilate(tgm, 1) & ~tgm & ~Hd & ~pic.obj("fangs"), "black")
    fm = pic.obj("fangs")
    pic.put(ak.dilate(fm, 1) & ~fm & Mo & ~tgm, "black")
    despeck(pic)                                            # the quantiser's lone pixels, everywhere
    upl = Hd & ak.shift(Mo, 0, -1) & (yy < (hy - 1 - (hx - xx) * UP) + HO[1] + 1.5) & (xx < hx - 4 + HO[0])
    pic.put(upl, "snk1")
    pic.put(ak.shift(upl, 0, -1) & Hd & pic.where("snk0"), "snk1")
    # the back-light: one clean lime line along the skull's top right
    Hm = Hd | pic.obj("eye")
    bl = Hm & ~ak.shift(Hm, -1, 0) & (xx >= 108 + HO[0]) & (yy >= 50 + HO[1]) & (yy <= 70 + HO[1])
    pic.put(bl & Hd, "snk2")

    ink = {"c": "cream", "k": "black", "w": "wine", "r": "red", "g": "snk0", "l": "snk2", "d": "dusk",
           "1": "snk1", "o": "wood", "v": "vmid", "n": "night", "e": "grey"}
    # the eye, set by hand: amber under a heavy black lid that slopes down
    # to the snout (the scowl), red smouldering in its lower rows, a black
    # slit pupil turned toward the cherries, one cream glint
    E = pic.obj("eye")
    pic.put(E, "snk1")                                      # the painted eye is only a placeholder
    lid = {x: 62 - (x - 86) // 2 for x in range(86, 104)}   # 2-px steps, (86-87, 62) to (102-103, 54)
    ecx, ecy, erx, ery = 94.0, 59.0, 5.8, 6.5               # the lower lid's arc
    eye_px = []
    for x in range(88, 100):
        bot = int(np.floor(ecy + ery * np.sqrt(max(0.0, 1 - ((x + 0.5 - ecx) / erx) ** 2))))
        eye_px += [(x, y) for y in range(lid[x] + 1, bot + 1)]
    EM = np.zeros((128, 128), bool)
    for x, y in eye_px:
        EM[y, x] = True
    ring_e = ak.dilate(EM, 1) & ~EM
    pic.put(ring_e & (yy >= 56), "black")                   # the rim round it, joining the lid
    pic.put(ak.shift(ring_e & ~ak.shift(EM, 0, -1), 0, 1) & Hd & ~EM & (yy >= 63) & (xx >= 89), "snk0")   # a shadow under it
    pic.put(EM, "wood")
    pic.put(EM & (yy >= 64), "red")
    pic.put(EM & (xx == 93) & (yy >= 61) & (yy <= 64), "black")      # the slit, turned on the cherries
    for x in range(86, 104):                                 # the lid: hard on top
        pic.px(x, lid[x], "black")
    pic.px(85, 63, "snk1")
    ak.patch(pic, 90, 61, ["cc"], ink)                       # the glint
    ak.patch(pic, *hp(70, 59), ["kk"], ink)                 # nostril
    ak.patch(pic, *hp(94.6, 50.4), ["cc"], ink)             # a glint on the brow: the head is glossy
    # the grin: the mouth's corner hooks up into a lime cheek
    gpts = ink_line(pic, [(x + HO[0], y + HO[1]) for x, y in ak.bezier((hx + 2.0, hy + 1.0), (hx + 5.5, hy + 0.5), (hx + 7.0, hy - 5.5), n=20)], "black")
    for x, y in gpts[2:-1]:
        if Hd[y - 1, x - 1] and not any((x - 1, y - 1) == q for q in gpts):
            pic.px(x - 1, y - 1, "snk2")
    # the fangs: cream all down the lit side, grey on the shade side and the point
    F = pic.obj("fangs")
    lit_side = F & ~ak.shift(F, 1, 0)
    for k_, (tx_, ty_) in enumerate(fangs):
        tip_y = int(round(ty_ + HO[1])) - 2
        pic.put(lit_side & pic.where("grey") & (yy < tip_y) & (np.abs(xx - (tx_ + HO[0])) < 5), "cream")
    # the upper jaw's underside: one clean step from green into its shade
    G = {n_: P_[n_] for n_ in ("snk0", "snk1", "snk2")}
    for x in range(69, 89):
        fd = 64 if x <= 77 else 65
        for y in range(60, 67):
            if not Hd[y, x] or pic.idx[y, x] not in G.values():
                continue
            if y >= fd:
                pic.px(x, y, "snk0")
            elif pic.idx[y, x] == G["snk0"] and x > 70:
                pic.px(x, y, "snk1")
    # the lower jaw's underside catches the board's violet
    low_j = Hd & (yy > hy + HO[1] + 1 + (hx + HO[0] - xx) * DN) & ~ak.shift(Hd, 0, -1)
    pic.put(ak.shift(low_j, 0, -1) & Hd & pic.where("snk0") & (xx >= 82) & (xx <= 104), "dusk")

    # the tongue's fork, by hand: a 2-px tip and two 1-px prongs, outlined
    tgm = pic.obj("tongue")
    ys_, xs_ = np.nonzero(tgm)
    tx0 = int(xs_.min())
    ty0 = int(ys_[xs_ == tx0].min())                        # the tip's upper row
    fork = [(tx0 - 1, ty0), (tx0 - 1, ty0 + 1),
            (tx0 - 2, ty0 - 1), (tx0 - 3, ty0 - 2), (tx0 - 4, ty0 - 3),
            (tx0 - 2, ty0 + 2), (tx0 - 3, ty0 + 3), (tx0 - 4, ty0 + 4)]
    FK = np.zeros((128, 128), bool)
    for x, y in fork:
        FK[y, x] = True
    pic.put(ak.dilate(FK, 1) & ~FK & ~tgm, "black")
    pic.put(FK, "red")
    # no pinches where the tongue steps: each column at least 2 px thick
    TG = pic.obj("tongue") & pic.where("red")
    for x in range(tx0 + 1, 105):
        ys_ = np.nonzero(TG[:, x])[0]
        if len(ys_) == 1:
            y = int(ys_[0])
            if TG[y + 1, x - 1] or TG[y + 1, x + 1]:
                pic.px(x, y + 1, "red")
            elif TG[y - 1, x - 1] or TG[y - 1, x + 1]:
                pic.px(x, y - 1, "red")

    # speed lines: the head has just lunged; they trail off the back of the skull
    Hm = Hd | pic.obj("eye")
    for y, n_, tail in ((59, 5, 1), (65, 4, 1), (71, 3, 1)):
        xs_ = np.nonzero(Hm[y])[0]
        x0_ = int(xs_.max()) + 3
        for k in range(n_):
            pic.px(x0_ + k, y, "dusk")
        for k in range(tail):
            if x0_ + n_ + 1 + 2 * k < 127:
                pic.px(x0_ + n_ + 1 + 2 * k, y, "dusk")

    # the cherries: a violet back-light on the rim of their shadow side, a
    # cream specular in the lit band, and faces: eyes popping, fixed on the
    # snake, brows up in the middle, mouths open in a scream
    for (cx, cy, r), nm in zip(CH, ("cherryA", "cherryB")):
        Cm = pic.obj(nm)
        other = (pic.obj("cherryB") if nm == "cherryA" else np.zeros_like(Cm))
        ang = np.arctan2(yy + 0.5 - cy, xx + 0.5 - cx)
        open_r = ~ak.shift(Cm, -1, 0) & ~ak.shift(other, -1, 0)
        open_b = ~ak.shift(Cm, 0, -1) & ~ak.shift(other, 0, -1)
        rimz = Cm & (open_r | open_b) & (ang > 0.1) & (ang < 1.5)
        pic.put(rimz & pic.where("black", "wine"), "dusk")
        # the lit edge: a solid wood crescent hugging the upper-left rim, 2 px
        # in the middle and 1 px at its tips, one checkered row inside it
        rr = np.hypot(xx + 0.5 - cx, yy + 0.5 - cy)
        ad = np.degrees(ang)
        red_ = Cm & pic.where("red")
        cres = red_ & (rr > r - 2.1) & (ad > -160) & (ad < -108)
        cres |= red_ & (rr > r - 1.2) & (ad > -176) & (ad < -94)
        pic.put(cres, "wood")
        pic.put(red_ & ~cres & (rr > r - 3.1) & (ad > -150) & (ad < -118) & ak.checker(), "wood")
    # faces: (eyes' gap x, eye row), the specular's corner
    FACES = (((28, 79), (22, 72)), ((48, 82), (39, 76)))
    eye = [".ccc.", "ccccc", "ccckc", "ccccc", ".ccc."]          # wide, pinprick pupils on the snake
    for (fx, fy), (sx, sy) in FACES:
        ak.patch(pic, sx, sy, [".c", "cc", "cc"], ink)            # the specular
        ak.patch(pic, fx - 5, fy, eye, ink)
        ak.patch(pic, fx + 1, fy, eye, ink)
        ak.patch(pic, fx - 5, fy - 3, ["..kk", "kk.."], ink)     # worried brows, up in the middle
        ak.patch(pic, fx + 2, fy - 3, ["kk..", "..kk"], ink)
        ak.patch(pic, fx - 5, fy - 1, ["rrrr"], ink)              # a red gap over each eye
        ak.patch(pic, fx + 2, fy - 1, ["rrrr"], ink)
        ak.patch(pic, fx - 1, fy + 6, [".k.", "kwk", "kwk", ".k."], ink)
    # the stems: up from their crowns to a join, hooked over the rung
    for pts in (ak.bezier((ax + 0.5, ay - ar + 0.2), (ax + 2.0, ry + 0.5), (37.5, ry - 2.6), (40.6, ry - 2.6), n=20),
                ak.bezier((bx - 0.6, by - br + 0.2), (bx - 1.6, ry + 1.0), (43.0, ry - 2.6), (41.4, ry - 2.6), n=20)):
        ink_line(pic, pts, "snk1")
    hook = ink_line(pic, ak.bezier((41.0, ry - 2.8), (42.8, ry - 5.4), (46.2, ry - 5.2), (46.8, ry - 0.6), n=20), "snk1")
    for x, y in hook[1:4]:
        pic.px(x, y - 1, "snk2")
    # sweat flying off the left one's crown (set below, after the sweep)

    # a last sweep for lone pixels, sparing the faces' pupils and the eye's glint
    keep = np.zeros((128, 128), bool)
    for (fx, fy), _ in FACES:
        keep[fy - 3:fy + 10, fx - 6:fx + 7] = True
    keep[54:68, 84:104] = True
    despeck(pic, protect=keep)

    # the die, just rolled to a stop in front of the snake: one red pip up,
    # snake eyes, the bad roll (a face lit cream, its side in violet shade,
    # its shadow cast down to the right)
    DX0, DY0 = 59, 90
    for x, y in ((DX0 + 10, DY0 + 9), (DX0 + 9, DY0 + 10), (DX0 + 10, DY0 + 10), (DX0 + 11, DY0 + 8),
                 (DX0 + 11, DY0 + 9), (DX0 + 3, DY0 + 10), (DX0 + 4, DY0 + 10), (DX0 + 5, DY0 + 10)):
        if pic.obj("background")[y, x]:
            pic.px(x, y, "black")
    ak.patch(pic, DX0, DY0, ["..kkkkkkk..",
                             ".kcccccccvk",
                             "kcccccccvvk",
                             "kccrrrccvvk",
                             "kccrrwccvvk",
                             "kccrwwccvvk",
                             "kcccccccvvk",
                             "kcccccccvvk",
                             "keeeeeeevk.",
                             ".kkkkkkkk.."], ink)

    # the frame's lower edges: black, so the border sits on dark
    fr = np.zeros((128, 128), bool)
    fr[-1, :] = fr[:, 0] = fr[:, -1] = True
    pic.put(fr & (yy > 48) & pic.obj("background") & pic.where("night", "vmid", "dusk"), "black")
    pic.put((xx >= 120) & (yy >= 50) & (yy <= 63) & pic.obj("background") & pic.where("night"), "black")   # the far dark behind the skull

    # sweat flung off the left one's crown: teardrops, round end out, the
    # point trailing back toward the cherry (cream lit, dusk shade)
    for x0, y0, rows in ((18, 64, [".cc.", "cccd", "ccdd", ".ddd", "..dd", "...d"]),
                         (13, 70, [".c.", "ccd", ".dd", "..d"])):
        ak.patch(pic, x0, y0, rows, ink)

    # -- the title
    # chrome gold: a bright sky, a dark horizon, its bright reflection, the ground
    rows1 = TITLE_ROWS
    t1 = ak.title(pic, m1, x1, y1, fill=None, rows=rows1, hi=None, lo=None,
                  extrude=dict(dx=1, dy=1, depth=3, side="wine", bottom="wine"),
                  shadow=dict(dx=1, dy=2, colour="black"))
    ck = ak.checker()
    pic.put(t1["face"] & (yy == y1 + 7) & ck, "gold2")      # the soft seams dithered; the horizon stays crisp
    pic.put(t1["face"] & (yy == y1 + 18) & ck, "gold1")
    bevel(pic, t1["face"], "cream", "gold0")
    rows2 = TITLE2_ROWS
    t2 = ak.title(pic, m2, x2, y2, fill=None, rows=rows2, hi=None, lo=None,
                  extrude=dict(dx=1, dy=1, depth=2, side="wine", bottom="wine"),
                  shadow=dict(dx=1, dy=1, colour="black"))
    pic.put(t2["face"] & (yy == y2 + 4) & ck, "gold2")
    pic.put(t2["face"] & (yy == y2 + 9) & ck, "gold1")
    bevel(pic, t2["face"], "cream", "gold0")
    # the notches between SNAKES' letter tops: solid black, so its top
    # outline runs unbroken and no halo shows through
    A1 = t1["all"]
    Lh = ak.shift(A1, 1, 0) | ak.shift(A1, 2, 0) | ak.shift(A1, 3, 0)
    Rh = ak.shift(A1, -1, 0) | ak.shift(A1, -2, 0) | ak.shift(A1, -3, 0)
    pic.put(Lh & Rh & ~A1 & (yy >= y1 - 1) & (yy <= y1 + 2), "black")
    # close the extrusion's teeth under the slits
    for t in (t1, t2):
        E_ = t["extrude"]
        gap = ~t["face"] & ~E_ & ak.shift(E_, 1, 0) & ak.shift(E_, -1, 0)
        pic.put(gap, "wine")
    # the final S's lower notch: wine like the other letters' gaps, not a black wedge
    pic.put(pic.where("black") & (xx >= x1 + 78) & (xx <= x1 + 83) & (yy >= y1 + 10) & (yy <= y1 + 15), "wine")
    # no lone pixels in the lettering or the halo round it
    allT = t1["all"] | t2["all"]
    despeck(pic, protect=~ak.dilate(allT, 4, diag=True))
    ak.sparkle(pic, *glint_in(t1["face"], x1 + 4, y1 + 3, 1), 1, "cream")
    ak.sparkle(pic, *glint_in(t2["face"], x2 + 86, y2 + 2, 1), 1, "cream")
    return pic.image()


def title_lines():
    """The title's lettering as drawn here, and its depth, for the title
    screen (tools/titleart.py: the game paints it in the house gold).
    SNAKES, then & LADDERS."""
    return [dict(mask=ak.load_mask(TITLE), depth=3, side="wine"),
            dict(mask=ak.load_mask(TITLE2), depth=2, side="wine")]


if __name__ == "__main__":
    import boxart
    print(boxart.save(draw(), HERE.parent / "docs" / "cart.png"))
