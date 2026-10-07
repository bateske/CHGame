"""docs/cart.png, CHBackgammon's cover in the visual menu (docs/cover-art.md).
`chgame boxart` redraws it; edit this, not the PNG.

THE BRIEF (revision 1)
  Message: the double, the stakes raised as high as they go. The doubling
  cube, turned to 64, hangs in the air over the board like the prize it is,
  still turning; under it the dice have just come up double sixes.
  BACKGAMMON over it all in gold. It reads in that order: the title, the 64,
  the sixes, then the board.

  Composition (a thumbnail in words):
  - Camera at the player's side, high (about 40 degrees down), the whole
    board in view from its far rail (under the title) to its near rail (at
    the foot, under the install bar). The board is unmistakable: two rows of
    long points, crimson and ivory, their bases on the rails, the near ones
    fanning up from the bottom, the far ones hanging from the far rail; the
    mahogany bar up the middle, left of the cube (never into its foot).
  - Focal point: the cube, right of the middle, about 44 px tall, hanging
    high over the near right points, tipped as it turns: the 64 face to us
    (the brightest thing below the title: a cream top-left half falling
    across a short seam to ivory2, the 64 bold and black), a thin ivory2
    top, its dark side ivory1 into grey with the felt's green bounced up its
    foot; clean cream lines on its edges toward the key, a black outline, a
    glint on its top-left corner. Tapered arcs of motion (cream to ivory1,
    edged in black so they stand off the points) trail two opposite corners:
    two down its left, one down its right. Its shadow lies on the felt below
    it to the right, clearly apart from it: cast along the key, shrunk (a
    soft light far above), a felt0 core with a ring a step lighter, the
    points vanishing under it.
  - The light: felt0 over the whole board, one pool of light round the
    cube's shadow (felt1, then felt2 at its heart) in flat steps with short
    seams, stirred by the cloth's nap, in world space (ellipses in
    perspective, not screen circles); the far side of the board falls to
    black under the title. The points step with it, always a clear step of
    value from the felt round them (crimson red1, wine in the dark; ivory1,
    grey in the dark, gone in the black), crisp, never dithered; the wood
    flat (tops wood1 or wine, sides a step down), a varnish gleam on the bar.
  - Foreground: two casino-red dice, lower left, six up (the double): the
    tops bright red (the only bright red in the picture), the sides toward
    the key red1, the others wine, pips stamped round from pixels, black on
    their shadow sides, a small glint on each one's top-left corner.
  - Background: the black of the room, calm under the title.
  - Light: the house key from the top left; shadows to the lower right.
  - The frame: the outer two rows and columns a step down every ramp (the
    outermost two), so nothing bright meets the border.
  - Title: the top band (y 3-35) on the black: a bold hand-lettered face,
    gold chrome (a cream top edge, a bright gold2 sky, gold1 below it, a
    gold0 horizon under every crossbar, its gold2 reflection, gold1 ground:
    the feet stay gold1, so the face has a bottom edge over its depth), a
    gold2 lit left edge on the stems above the horizon, a four-step
    extrusion (gold0, gold0, wine, wine), each letter's depth parted from its
    neighbours' by black, a black outline, glints on the B and the N.
    Nothing else uses the golds.

  Palette (11 own + cream, grey, black, red):
    felt0 felt1 felt2   the felt, a cool casino green (black below), the
                        cube's bounce light, its shadow
    wine red1           the crimson points, the dice's sides; the bar's
                        shade; the title's depth (red: the dice's tops)
    wood1               the mahogany's lit tops (wine and black below it)
    ivory1 ivory2       the cube and the ivory points, with grey and cream
    gold0 gold1 gold2   the title's own

  Font: Arc24 from the bmf collection, at its own 27 px (author and terms
  not stated: a `?` face, chosen as the bold hand-lettered face that sets
  BACKGAMMON in 121 px and reads at 1x); the B and the A, the A and the M,
  and the two Ms parted at their feet by hand, the A's plinths filled
  (tools/art/title.txt, credits in its header).
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import numpy as np  # noqa: E402
import artkit as ak  # noqa: E402
from artkit import render3d as R  # noqa: E402

TITLE = HERE / "art" / "title.txt"
YY, XX = np.mgrid[0:128, 0:128]

# ---- the camera and the light ---------------------------------------------------------------
CAM = R.Camera((0.6, 9.5, 12.5), (0.6, 0.0, -0.3), fov=46, shift=(0, 6))
KEY = np.array([-0.6, 0.8, 0.35])   # the house key, top left
KEY = KEY / np.linalg.norm(KEY)
SUN = (-0.25, 0.95, -0.1)           # the board's contact shadows: a steep light, so short ones
DROP = (-0.45, 1.0, 0.22)           # toward the light the cube's shadow is cast by: the key's side (it falls right)
SHADOW_SCALE = 0.66                 # the cube's shadow: its footprint shrunk (a soft light far above)
POOL = ((2.6, 2.2), (8.6, 7.4))     # the pool of light on the board: centre (x, z) and radii
POOL_GAIN, POOL_SOFT = 3.2, 0.14    # its levels over the felt0 the whole board gets, and their seams' width
NAP = (1.6, 0.12)                   # the cloth's nap stirring the seams: noise scale (world units), strength
BACK = (3.0, 2.0)                   # the far side's fall into the dark: from this depth (behind the middle), over this

# ---- the title ---------------------------------------------------------------------------------
TITLE_Y = 3
# the face row by row (27 rows): gold chrome: a bright sky, its lower part
# gold1, a dark horizon under every crossbar, its bright reflection, gold1
# ground (the feet stay gold1, so the face has a bottom edge over its depth)
TITLE_ROWS = ["gold2"] * 11 + ["gold1"] * 5 + ["gold0", "gold0", "gold2"] + ["gold1"] * 8
TITLE_DEPTH = ["gold0", "gold0", "wine", "wine"]   # the extrusion, step by step from the face
TITLE_GLINTS = [(1, 1, 2), (119, 1, 2)]    # on the title's mask: the B's and the N's top corners

# ---- the board (world units: a point is 1 wide; y up, z toward us) -------------------------
PW = 1.0                    # a point's width
PB = 0.44                   # a point's half base (of its width): a sliver of felt between bases
BAR = 1.1                   # the bar's width
X0 = BAR / 2
D = 5.6                     # the field's half depth (rail to rail)
PL = 4.7                    # a point's length
W = 6 * PW + X0             # the field's half width
RAIL, RH = 0.6, 0.3         # the frame's width and height over the felt

# ---- the cube and the dice ------------------------------------------------------------------
CUBE_S = 2.1                        # the doubling cube's edge (a box-art cube: big)
CUBE_AT = (84, 63, 4.2)             # its centre on the picture (px), its height over the felt
CUBE_FACE = (-0.45, -0.3, 0.84)     # where the 64 face looks, in screen terms (x right, y up, z to us)
CUBE_SPIN = -16.0                   # its turn about that axis (degrees)
CUBE_ROUND = 0.08                   # its edges' rounding (of its edge)
NUM = ("64", 1.15, 0.12, (0.0, 0.0))   # its number: text, height, stroke radius (half edges), nudge
FALL = (0.36, 0.25)                 # the 64 face's light falls a step from here, over this (along its diagonal)
GLINT = (0, 0, (3, 2, 3, 2))        # the cube's glint: from its top-left corner (px), arms (left, right, up, down)
# arcs of motion round the cube: (the corner they trail: its angle on the
# picture, degrees clockwise from the right; where the arc starts past it;
# how far it sweeps; its gap outside the corner (px); root and tip radii)
ARCS = [(135, 4, 62, 3.0, 1.8, 0.4), (135, 10, 44, 7.5, 1.3, 0.3), (-45, 4, 50, 3.0, 1.6, 0.4)]
DS = 1.55                           # a die's edge
DICE = [((17, 90), 30), ((38, 104), -12)]           # their centres on the picture (px), turn about y

FELT, WOOD, CUBE, DIE0 = 0, 1, 2, 3                  # materials; then one per die

WHITE_R = ["black", "grey", "ivory1", "ivory2", "cream"]
RED_R = ["black", "wine", "red1", "red"]
FELT_R = ["black", "felt0", "felt1", "felt2"]
WOOD_R = ["black", "wine", "wood1"]
# the points by the light's level (black, felt0, felt1, felt2 on the felt):
# always a clear step of value from the felt round them; the bright red is
# the dice's alone
RED_PT = ["wine", "red1", "red1", "red1"]
IVORY_PT = ["black", "grey", "ivory1", "ivory1"]
DARKER = {"cream": "ivory2", "ivory2": "ivory1", "ivory1": "grey", "grey": "black", "red": "red1",
          "red1": "wine", "wine": "black", "felt2": "felt1", "felt1": "felt0", "felt0": "black",
          "wood1": "wine"}


# ---- the scene ------------------------------------------------------------------------------

def orient(face, spin, cam):
    """A rotation (local -> world) that turns a cube's +z face toward `face`
    (screen terms) with its +y as near the picture's up as it can be, then
    `spin` degrees about the face."""
    z = face[0] * cam.r + face[1] * cam.u - face[2] * cam.f
    z = z / np.linalg.norm(z)
    y = cam.u - (cam.u @ z) * z
    y = y / np.linalg.norm(y)
    x = np.cross(y, z)
    a = np.radians(spin)
    x, y = np.cos(a) * x + np.sin(a) * y, -np.sin(a) * x + np.cos(a) * y
    return np.stack([x, y, z], axis=1)


def at(cam, sx, sy, h):
    """The world point at height h that lands on pixel (sx, sy)."""
    o, d = cam.rays(np.array([sx], float), np.array([sy], float))
    return o[0] + d[0] * (h - o[0, 1]) / d[0, 1]


def cube_pos():
    return at(CAM, CUBE_AT[0], CUBE_AT[1], CUBE_AT[2])


def cube_rot():
    return orient(CUBE_FACE, CUBE_SPIN, CAM)


def dice():
    return [(at(CAM, sx, sy, DS / 2), R.rot_y(a)) for (sx, sy), a in DICE]


def scene(with_cube=True):
    rails = R.U(
        R.xf(R.prim(R.box((W + RAIL, RH / 2, RAIL / 2), 0.05), WOOD), (0, RH / 2, -D - RAIL / 2)),
        R.xf(R.prim(R.box((W + RAIL, RH / 2, RAIL / 2), 0.05), WOOD), (0, RH / 2, D + RAIL / 2)),
        R.xf(R.prim(R.box((RAIL / 2, RH / 2, D + RAIL), 0.05), WOOD), (-W - RAIL / 2, RH / 2, 0)),
        R.xf(R.prim(R.box((RAIL / 2, RH / 2, D + RAIL), 0.05), WOOD), (W + RAIL / 2, RH / 2, 0)),
        R.xf(R.prim(R.box((X0, RH / 2, D), 0.05), WOOD), (0, RH / 2, 0)),
        R.xf(R.prim(R.box((W + RAIL, 0.2, D + RAIL), 0.0), WOOD), (0, -0.2, 0)))
    felt = R.xf(R.prim(R.box((W, 0.01, D), 0.0), FELT), (0, -0.005, 0))
    cube = R.xf(R.prim(R.box((CUBE_S / 2,) * 3, CUBE_ROUND * CUBE_S), CUBE), cube_pos(), cube_rot())
    dd = [R.xf(R.prim(R.box((DS / 2,) * 3, 0.09 * DS), DIE0 + j), pos, rot) for j, (pos, rot) in enumerate(dice())]
    return R.U(rails, felt, *([cube] if with_cube else []), *dd)


def geometry(cam, sc, sc_lit, nmat):
    """Per pixel: the material most of its rays hit; how lit it is by the
    steep SUN in the scene without the cube (the board's contact shadows:
    the cube's own is drawn apart; 2 x 2 rays a pixel); at the pixel's
    centre the surface point and normal (one ray)."""
    white = [R.Mat("#FFFFFF", spec=0.0)] * nmat
    out = R.render(ak.Canvas("#000000"), sc, cam, white, lights=[(SUN, "#FFFFFF", 1.0)], ambient="#000000", ss=2,
                   shadows=False, ao=False)
    lit = R.render(ak.Canvas("#000000"), sc_lit, cam, white, lights=[(SUN, "#FFFFFF", 1.0)], ambient="#000000", ss=2)
    o1 = R.render(ak.Canvas("#000000", ss=1), sc, cam, white, lights=[(SUN, "#FFFFFF", 1.0)], ambient="#000000",
                  ss=None, ao=False, shadows=False)
    o, d = cam.rays((XX + 0.5).reshape(-1).astype(np.float64), (YY + 0.5).reshape(-1).astype(np.float64))
    dep = o1["depth"].reshape(-1)
    z = np.where(np.isfinite(dep), dep, 0)
    p = (o + d * z[:, None]).reshape(128, 128, 3)
    return dict(mat=R.majority(out, 4), lum=ak.px_mean(lit["rgb"][..., 0], 4), p=p, n=o1["normal"].astype(np.float64))


def box_faces(cam, pos, rot, half, ss=4):
    """The cube as a sharp box, ray-cast at ss x ss points a pixel: how much
    of each pixel it covers, the face most of that is on (0 -x, 1 +x, 2 -y,
    3 +y, 4 -z, 5 +z) and the mean hit point in the cube's own coordinates
    (-1..1)."""
    c = (np.arange(ss) + 0.5) / ss
    g = (np.arange(128)[:, None] + c[None, :]).reshape(-1)
    GX, GY = np.meshgrid(g, g)
    o, d = cam.rays(GX.reshape(-1), GY.reshape(-1))
    ol, dl = (o - pos) @ rot / half, d @ rot / half
    with np.errstate(divide="ignore", invalid="ignore"):
        t1, t2 = (-1 - ol) / dl, (1 - ol) / dl
    tn = np.nanmax(np.minimum(t1, t2), axis=1)
    tf = np.nanmin(np.maximum(t1, t2), axis=1)
    hit = (tn < tf) & (tf > 0)
    ax = np.argmax(np.minimum(t1, t2), axis=1)
    q = ol + dl * tn[:, None]
    face = ax * 2 + (np.take_along_axis(q, ax[:, None], 1)[:, 0] > 0)
    face = np.where(hit, face, -1).reshape(128, ss, 128, ss).transpose(0, 2, 1, 3).reshape(128, 128, ss * ss)
    cnt = np.stack([(face == f).sum(-1) for f in range(6)], -1)
    q = np.where(hit[:, None], q, 0).reshape(128, ss, 128, ss, 3).transpose(0, 2, 1, 3, 4).reshape(128, 128, ss * ss, 3)
    nh = np.maximum((face >= 0).sum(-1), 1)
    return dict(cover=(face >= 0).mean(-1), face=cnt.argmax(-1), lp=q.sum(2) / nh[..., None])


def spot(x, z):
    (cx, cz), (rx, rz) = POOL
    return np.clip(1 - np.hypot((x - cx) / rx, (z - cz) / rz), 0, 1)


# ---- the cube's numerals: bold strokes in a digit's own units (y up, the
# digit 1 tall, about 0.6 wide), drawn on a face through its plane --------------------------

def glyph(ch, X, Y, r):
    """The distance to digit `ch` centred on (0, 0) (negative inside)."""
    def seg(a, b):
        return ak.segment((X, Y), a[0], a[1], b[0], b[1], r)
    if ch == "6":
        bowl = np.abs(ak.ellipse((X, Y), 0.0, -0.2, 0.25, 0.28)) - r
        hook = ak.polyline((X, Y), ak.bezier((-0.25, -0.2), (-0.27, 0.36), (0.0, 0.5), (0.22, 0.4), n=24), r)
        return np.minimum(bowl, hook)
    if ch == "4":
        return np.minimum(np.minimum(seg((0.12, -0.5), (0.12, 0.5)), seg((0.12, 0.5), (-0.28, -0.14))),
                          seg((-0.28, -0.14), (0.28, -0.14)))
    raise ValueError(ch)


def number(text, X, Y, h, r, gap=0.1, w=0.6):
    """The distance to a number set on a face: digits h tall, centred on (0, 0)."""
    tot = len(text) * w + (len(text) - 1) * gap
    d = None
    for i, ch in enumerate(text):
        cx = -tot / 2 + w / 2 + i * (w + gap)
        dk = glyph(ch, X / h - cx, Y / h, r / h) * h
        d = dk if d is None else np.minimum(d, dk)
    return d


def face_cover(cam, pos, rot, half, axis, up, right, text, h, r, ss=8, shift=(0.0, 0.0)):
    """How much of each pixel a number covers on one face of a cube (pos,
    rot, half its edge): the face whose normal is local `axis`, the number's
    up and right along local `up` and `right`. Rays are cast at ss x ss
    points a pixel onto the face's plane."""
    c = (np.arange(ss) + 0.5) / ss
    g = (np.arange(128)[:, None] + c[None, :]).reshape(-1)
    GX, GY = np.meshgrid(g, g)
    o, d = cam.rays(GX.reshape(-1), GY.reshape(-1))
    nw = rot @ np.asarray(axis, float)
    q = np.asarray(pos, float) + nw * half
    t = ((q - o) @ nw) / (d @ nw)
    hit = o + d * t[:, None] - pos
    U = (hit @ (rot @ np.asarray(right, float))) / half - shift[0]
    V = (hit @ (rot @ np.asarray(up, float))) / half - shift[1]
    ink = (number(text, U, V, h, r) < 0).astype(np.float32)
    return ink.reshape(128, ss, 128, ss).mean(axis=(1, 3))


# ---- pixel work -----------------------------------------------------------------------------

def two_faces(ln):
    """For each local normal of a cube: the face it is most on and the one
    next most (0 -x, 1 +x, 2 -y, 3 +y, 4 -z, 5 +z)."""
    o = np.argsort(-np.abs(ln), axis=-1)
    s0 = np.take_along_axis(ln, o[..., :1], -1)[..., 0] > 0
    s1 = np.take_along_axis(ln, o[..., 1:2], -1)[..., 0] > 0
    return o[..., 0] * 2 + s0, o[..., 1] * 2 + s1


def stamp_pips(pic, cam, pos, rot, half, axis, u_ax, v_ax, count, face_m, colour, size=(4, 4), spread=0.5,
               smallest=1):
    """Pips on one face of a die: a round dot at each place (artkit's PIPS,
    `spread` of the half edge from the middle), as big as the perspective
    allows with a pixel between neighbours, all on the face; none if they
    would be under `smallest` px."""
    nw = rot @ np.asarray(axis, float)
    uw, vw = rot @ np.asarray(u_ax, float), rot @ np.asarray(v_ax, float)
    cs = [cam.project(pos + (nw + (uw * a + vw * b) * spread) * half) for a, b in ak.PIPS[count]]
    w, h = size
    inner = ak.erode(face_m, 1)
    while w >= smallest and h >= smallest:
        tpl = ak.pip_template(w, h)
        ms = [ak.place(tpl, int(np.floor(cx - w / 2 + 0.5)), int(np.floor(cy - h / 2 + 0.5))) for cx, cy in cs]
        ok = all((m & ~inner).sum() == 0 for m in ms)
        clash = any((ak.dilate(a, 1) & b).any() for i, a in enumerate(ms) for b in ms[i + 1:])
        if ok and not clash:
            for m in ms:
                pic.put(m, colour)
            return True
        if w >= h:
            w -= 1
        else:
            h -= 1
    return False


def outline_shadow_side(pic, m, ground, colour="black"):
    """`colour` where an object's 1-px ring lies on `ground` on its side away
    from the light (the blurred mask's gradient), unbroken."""
    ring = ak.dilate(m, 1) & ~m
    k = np.array([1, 4, 6, 4, 1], float) / 16
    B = np.apply_along_axis(lambda v: np.convolve(v, k, "same"), 1, m.astype(float))
    B = np.apply_along_axis(lambda v: np.convolve(v, k, "same"), 0, B)
    gy, gx = np.gradient(B)
    side = ring & ((gx + gy) > 0.01)
    side &= ak.nbrs(side, diag=True)
    pic.put(side & ground, colour)


def arc_pts(c, rad, a0, a1, n=40):
    """Points along a circle's arc (picture coordinates, degrees clockwise from the right)."""
    t = np.radians(np.linspace(a0, a1, n))
    return [(c[0] + rad * np.cos(a), c[1] + rad * np.sin(a)) for a in t]


def taper(pic, pts, r0, r1, ok, cols, ss=4, cut=0.5):
    """A tapered stroke along a polyline: r0 px in radius at its first point,
    r1 at its last, painted where `ok` is; its colour steps along it
    (cols [(name, up to t)]). Returns its mask."""
    c = (np.arange(128 * ss) + 0.5) / ss
    X, Y = np.meshgrid(c, c)
    d = ak.polyline((X, Y), pts, r0, r1)
    m = ((d < 0).reshape(128, ss, 128, ss).mean(axis=(1, 3)) >= cut) & ok
    ys, xs = np.nonzero(m)
    Pt = np.array(pts)
    t = ((xs[:, None] + 0.5 - Pt[None, :, 0]) ** 2 + (ys[:, None] + 0.5 - Pt[None, :, 1]) ** 2).argmin(1) / (len(pts) - 1)
    lo = 0.0
    for name, hi in cols:
        sel = (t >= lo) & (t <= hi)
        pic.idx[ys[sel], xs[sel]] = pic.pal[name]
        lo = hi
    return m


def darken_frame(pic):
    """No bright pixels on the frame (the installed border is drawn there):
    the outer two rows and columns step every colour a level down its ramp,
    the outermost row and column two levels."""
    for band in ((XX < 2) | (XX > 125) | (YY < 2) | (YY > 125), (XX < 1) | (XX > 126) | (YY < 1) | (YY > 126)):
        was = pic.idx.copy()
        for src, dst in DARKER.items():
            pic.put(band & (was == pic.pal[src]), dst)


# ---- the picture ----------------------------------------------------------------------------

def draw():
    P = ak.Palette({
        "felt0": "#062622", "felt1": "#0A3E30", "felt2": "#1E8A50",
        "wine": "#5C0A1E", "red1": "#A0142A",
        "wood1": "#7E3414",
        "ivory1": "#B8A282", "ivory2": "#E8D8B6",
        "gold0": "#94500E", "gold1": "#EAA622", "gold2": "#FFEA8C",
    }, ramps=[FELT_R, RED_R, WOOD_R, WHITE_R, ["gold0", "gold1", "gold2", "cream"]])
    pic = ak.Picture.blank(P, "black")
    G = geometry(CAM, scene(), scene(False), DIE0 + len(DICE))
    mat, lum, p, n = G["mat"], G["lum"], G["p"], G["n"]
    X, Z = p[..., 0], p[..., 2]
    room = mat < 0
    cpos, crot, half = cube_pos(), cube_rot(), CUBE_S / 2

    # ---- the light on the board: felt0 all over, one pool of light round
    # the cube's shadow (felt1, felt2) in flat steps with short seams stirred
    # by the cloth's nap, the far side falling to black; a step down in a
    # contact shadow; the cube's shadow cast along the key, shrunk (a soft
    # light), a crisp core and a ring a step lighter
    back = np.clip((-Z - BACK[0]) / BACK[1], 0, 1)
    nap = (ak.noise((X, Z), NAP[0], seed=7, octaves=2) - 0.5) * NAP[1]
    lit = ak.terrace(np.clip(1 + (spot(X, Z) + nap) * POOL_GAIN - back, 0, 3), POOL_SOFT)
    contact = (lum < 0.5) & (mat >= 0)
    corners = [cpos + crot @ (np.array([a, b, c]) * half) for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)]
    dl = np.asarray(DROP, float)
    foot = [(q[0] - dl[0] * q[1] / dl[1], q[2] - dl[2] * q[1] / dl[1]) for q in corners]
    poly = np.array(ak.hull(foot))
    cen = poly.mean(axis=0)
    poly = cen + (poly - cen) * SHADOW_SCALE
    dsh = ak.polygon((X, Z), [tuple(q) for q in poly])
    sh = np.clip((0.1 - dsh) / 0.4, 0, 1)                     # world units: 1 in the core, 0 outside
    core, seam = sh > 0.55, (sh > 0.12) & (sh <= 0.55)
    board = (mat == FELT) | (mat == WOOD)
    level = lit - contact * 1.0
    level = np.where(board & seam, np.maximum(level - 1, np.minimum(level, 1.0)), level)

    # ---- the felt and its points: crimson and ivory, alternating, crisp
    # (no dither), each a clear step of value from the felt round it; under
    # the core of the cube's shadow all of it felt0 (the points vanish into
    # it), its ring a step down
    felt = mat == FELT
    ax = np.abs(X) - X0
    k = np.floor(ax / PW)
    u = ax - (k + 0.5) * PW
    dz = D - np.abs(Z)
    inpt = felt & (ax > 0) & (k < 6) & (dz < PL) & (np.abs(u) < PB * PW * (1 - dz / PL))
    red_pt = ((k.astype(int) + (Z > 0) + (X > 0)) % 2) == 0
    ak.by_level(pic, level, FELT_R, felt & ~inpt)
    ak.by_level(pic, level, RED_PT, inpt & red_pt, q=1)
    ak.by_level(pic, level, IVORY_PT, inpt & ~red_pt, q=1)
    pic.put(felt & core & (lit >= 1), "felt0")

    # ---- the wood (mahogany): tops by the pool, sides a step down, flat;
    # a varnish gleam along the bar's lit edge where the pool is bright
    wood = mat == WOOD
    top = n[..., 1] > 0.8
    wl = np.interp(level, [0, 1, 2, 3], [0, 1, 2, 2])
    ak.by_level(pic, np.round(np.where(top, wl, wl - 1) - core), WOOD_R, wood, q=1)
    pts = [CAM.project((-X0 + 0.14, RH, z)) for z in np.linspace(-D, D, 80)]
    ak.ink(pic, pts, "ivory1", where=wood & top & (lit > 1.9) & ~contact & (sh == 0))

    # ---- the dice: casino red, six up; the side toward the key red1, the
    # other wine; cream pips; black on their shadow sides; a glint on each
    dice_glints = []
    for j, (pos, rot) in enumerate(dice()):
        m = mat == DIE0 + j
        f0, _ = two_faces(n @ rot)
        sides = [f for f in (0, 1, 4, 5) if (m & (f0 == f)).sum() > 4]
        lit_side = max(sides, key=lambda f: (rot @ np.eye(3)[f // 2] * (1 if f % 2 else -1)) @ KEY)
        ak.by_level(pic, np.where(f0 == 3, 3, np.where(f0 == lit_side, 2, 1)), RED_R, m, q=1)
        stamp_pips(pic, CAM, pos, rot, DS / 2, (0, 1, 0), (0, 0, 1), (1, 0, 0), 6, m & (f0 == 3), "cream")
        outline_shadow_side(pic, m, ~m & ~room)
        ys_, xs_ = np.nonzero(m)                                  # a glint on its top-left corner
        jj = np.argmin(xs_ * 0.6 + ys_)
        dice_glints.append((int(xs_[jj]), int(ys_[jj])))

    # ---- the cube (its faces ray-cast as a sharp box): the 64 face lit (a
    # cream top-left half falling across a short seam to ivory2), a thin
    # ivory2 top, the side away from the key ivory1 into grey with the felt's
    # green bounced up its foot; the 64 in black; its edges toward the key
    # drawn as clean cream lines from its own geometry; a black outline
    cm = mat == CUBE
    bx = box_faces(CAM, cpos, crot, half)
    f0, lp = bx["face"], bx["lp"]
    diag = ((lp[..., 0] - lp[..., 1]) / 2 + 1) / 2                # 0 at the 64 face's top-left corner, 1 at its bottom-right
    g = ak.terrace(np.clip((diag - FALL[0]) / FALL[1], 0, 1), 0.2)
    gs = ak.terrace(np.clip((-lp[..., 1] + 0.1) / 0.5, 0, 1), 0.2)   # down the dark side
    lvl = np.select([f0 == 5, f0 == 3, f0 == 1, f0 == 0], [4 - g, 3, 2 - gs, 3], 1)
    ak.by_level(pic, lvl, WHITE_R, cm)
    txt, hh, r_, sh_ = NUM
    nm = cm & (f0 == 5) & (face_cover(CAM, cpos, crot, half, (0, 0, 1), (0, 1, 0), (1, 0, 0), txt, hh, r_,
                                      shift=sh_) >= 0.5)
    pic.put(nm, "black")
    edges = [((0, 0, 1), (0, 1, 0), "cream"), ((0, 0, 1), (-1, 0, 0), "cream"), ((0, 1, 0), (-1, 0, 0), "cream"),
             ((0, 0, 1), (1, 0, 0), "ivory1"), ((0, 1, 0), (1, 0, 0), "ivory2")]
    for a, b, col in edges:
        a, b = np.asarray(a, float), np.asarray(b, float)
        free = np.array([1.0, 1.0, 1.0]) - np.abs(a) - np.abs(b)
        off = 1 - CUBE_ROUND * 2 * 0.29
        ak.ink(pic, [CAM.project(cpos + crot @ ((a + b) * off + free * t) * half) for t in np.linspace(-0.8, 0.8, 30)],
               col, where=cm & ~nm)
    below = ak.shift(~cm, 0, -1) | ak.shift(~cm, 0, -2) | ak.shift(~cm, -1, -1)
    pic.put(cm & (f0 == 1) & below & (lp[..., 1] < -0.15), "felt1")
    pic.put(ak.dilate(cm, 1) & ~cm, "black")

    # ---- the turning: tapered arcs (cream to ivory1, edged in black so
    # they stand off the points) trailing two opposite corners of the cube's
    # outline: it turns counter-clockwise
    hull2 = np.array(ak.hull([CAM.project(c) for c in corners]))
    cc = hull2.mean(axis=0)
    ang = np.degrees(np.arctan2(hull2[:, 1] - cc[1], hull2[:, 0] - cc[0]))
    clear = ~ak.dilate(cm, 1) & (YY > 36)
    for target, lead, sweep, gap, w0, w1 in ARCS:
        j = int(np.argmin(np.abs((ang - target + 180) % 360 - 180)))
        rad = float(np.hypot(*(hull2[j] - cc))) + gap
        m = taper(pic, arc_pts(cc, rad, ang[j] + lead, ang[j] + lead + sweep), w0, w1, clear,
                  [("cream", 0.25), ("ivory2", 0.6), ("ivory1", 1.0)])
        pic.put(ak.dilate(m, 1) & ~m & clear, "black")

    # ---- lone pixels (the edges' stair steps) take their neighbours'
    # colour; the cube and the creams stay; then the frame steps down
    keep = pic.where("cream") | cm
    for need in (5, 4, 3):
        ak.despeckle(pic, need, keep=keep)
    darken_frame(pic)
    # the cube's glint on its top-left corner, over the arcs and the clean-up
    gx, gy = hull2[np.argmin(hull2[:, 0] * 0.6 + hull2[:, 1])]
    ak.glint(pic, int(gx) + GLINT[0], int(gy) + GLINT[1], 3, tip="ivory2", arms=GLINT[2])
    for x_, y_ in dice_glints:
        ak.glint(pic, x_, y_, 1)

    # ---- the title: gold chrome, a four-step extrusion (gold0, then wine),
    # each letter parted from its neighbours' depth by black, a cream top
    # edge, a gold2 lit left edge on the stems above the horizon, glints
    tm = ak.load_mask(TITLE)
    tx, ty = ak.centred_x(tm), TITLE_Y
    drawn = ak.title(pic, tm, tx, ty, fill=["gold2"], rows=TITLE_ROWS, hi=None, lo=None,
                     extrude=dict(dx=1, dy=1, depth=len(TITLE_DEPTH), colours=TITLE_DEPTH),
                     shadow=dict(dx=1, dy=1, colour="black"))
    M = drawn["face"]
    lab = ak.letters(M)
    for i in range(1, lab.max() + 1):
        Mi = lab == i
        Ei = np.zeros_like(Mi)
        for kk in range(1, len(TITLE_DEPTH) + 1):
            Ei |= ak.shift(Mi, kk, kk)
        pic.put(ak.dilate(Mi, 1) & ~Mi & drawn["extrude"] & ~(Ei & ~M), "black")
    out = ak.outside_of(M)
    thick_h = M & ak.shift(M, 1, 0) & ak.shift(M, -1, 0)
    pic.put(M & ak.shift(out, 1, 0) & ak.shift(thick_h, -1, 0) & (YY < ty + 16), "gold2")
    edge_top = M & ak.shift(out, 0, 1)
    edge_top &= ak.shift(edge_top, 1, 0) | ak.shift(edge_top, -1, 0)
    pic.put(edge_top, "cream")
    for gx_, gy_, sz in TITLE_GLINTS:
        ak.glint(pic, tx + gx_, ty + gy_, sz, tip="gold2")
    return pic.image()


if __name__ == "__main__":
    import boxart
    boxart.save(draw(), HERE.parent / "docs" / "cart.png")
