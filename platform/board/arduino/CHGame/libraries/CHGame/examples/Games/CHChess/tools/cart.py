"""docs/cart.png, CHChess's cover in the visual menu (docs/cover-art.md).
`chgame boxart` redraws it; edit this, not the PNG.

THE BRIEF (revision 3)
Message: CHECK. The black knight is in mid-leap, diving at the white king,
which rocks back on the square the game lights red when a king is in check.
A homage to the ray-traced chess boxes of the early 1990s (Chessmaster
3000): glossy pieces on a polished board under one lamp in the dark, with
the game's own drama (the knight's jump, the slow-motion capture, the CPU's
red).

Composition (a thumbnail in words):
- Camera a little above the board (about 20 degrees down), close in with a
  wide lens; the board turned 45 degrees, so its squares are diamonds
  running off in perspective: the game's own isometric board, in depth.
  It reads as a chessboard at a glance.
- A diagonal from the lower left to the upper right: the white king big
  in the lower left, standing on its red square; the knight high in the
  right, in the air, its muzzle a few pixels from the king's collar (the
  tension); two ghosts of its head trail back up the arc it came along.
- The white king: Staunton ivory, lit from the top left: its light per
  pixel (round its axis, tops lit, undersides and the crown's shadow
  down), smoothed, then cut into flat bands (ivory2, ivory1, grey) with
  short dithered seams, one cream streak down the stem where the gloss
  runs, a glint on the crown's rim, the cross stamped by hand (leaning a
  pixel with the king's 11 degrees of recoil, a cream glint on its head
  and arm). It is the brightest thing under the title: the focal point.
  Its shadow falls black to the right across the red square.
- The black knight: blue-black lacquer, leaning 20 degrees into the dive,
  shaded on the picture from its silhouette: the flat of the head falls
  from steel on the lamp's side through slate to navy; the rounded edges
  light up (steel, ice where the key grazes hardest: the brow, the bridge
  of the nose, the ears) only where they face the lamp and fall to navy
  where they turn away; a carved mane of slate ridges down the back of the
  neck; a black almond eye with a red pupil (the CPU's colour) and a cream
  catch-light under a heavy navy brow lowest at the front; a cream ping of
  gloss on the brow; the base turned like the king's.
- The leap: the knight's base hangs well clear of the board; its shadow
  waits straight below on a lit square, a navy ellipse in a felt1 ring,
  with lit felt between them. Two ghosts of its head step back up the arc
  (slate with a steel top edge, then navy with a slate one), each parted
  from what is in front of it by a black line; three long tapered speed
  lines follow the same arc (an ice root, steel, slate tails, a step
  lighter where they cross a ghost of their own colour).
- Depth: a dim white pawn far back on the left; a navy haze where the
  board meets the dark (the lamp's light in the room), the knight and its
  ghosts cut out of it by a black line; above it the black stage under the
  title is calm.
- The board: green marble and black lacquer in a pool of lamplight round
  the duel, flat plateaus with short Bayer seams (the squares' edges
  crisp), falling off into the dark; the pieces' shadows a level down; the
  king's square red. The outer rows and columns step down for the menu's
  border.
- Title: CHESS across the top in a bold Roman, gold leaf (a bright sky, a
  one-row gold0 horizon, light below), cream along every top edge, a gold0
  bevel on the shaded contour, a three-step carved depth (gold0, then
  slate, then navy) with each letter parted from its neighbours' by black
  and no slivers of depth left in the serifs' pockets, a black outline and
  shadow, glints on the C and the last S. Nothing else uses the golds.

Palette (11 own + cream, grey, black, red):
- gold0 gold1 gold2 ... the title's own (and nothing else).
- navy slate steel ice  the black knight (with black and cream), its ghosts
                        and speed lines, the title's depth (slate, navy);
                        navy is also the haze and the board's step into
                        the dark.
- ivory1 ivory2 ....... the white king and the far pawn (with grey below
                        and cream above).
- felt1 felt2 ......... the board's marble (navy and black below them).
- fixed: black (the void, outlines, cut lines), cream (gloss, glints,
  catch-lights), grey (the king's shade), red (the check square, the
  knight's pupil: the CPU's colour).

How it is painted: render3d marches the scene (a lathe king and pawn from
smoothed profiles, the knight as its profile given rounded depth with a
jowl and two cone ears on a lathe foot) on white, once for which piece
each pixel shows and once at the pixel centres for the point, the normal
and the key's shadow. Every surface is then coloured on the pixels as
levels of its ramp; the stamps (cross, eye, nostril), the ghosts and
streaks laid along one arc, lone pixels cleaned, then the title.

Font: ncenB24 (u8g2's bitmap of the X11/Adobe New Century Schoolbook Bold;
the X11/Adobe notice permits use and modification with the notice kept),
at its own size, letters spaced one pixel wider (tools/art/title.txt).
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import numpy as np  # noqa: E402
import artkit as ak  # noqa: E402
from artkit import render3d as R  # noqa: E402
from artkit import canvas as CV  # noqa: E402

TITLE = HERE / "art" / "title.txt"
TITLE_Y = 4
TITLE_ROWS = ["gold2"] * 7 + ["gold1"] * 4 + ["gold0"] + ["gold2"] * 4 + ["gold1"] * 9
HORIZON = 11                                           # the gold0 row (from the title's top)
GLINTS = [(4, 3, 2), (116, 1, 2)]                      # on the title's mask: (x, y, arm)

PAL = {
    "gold0": "#8E4A06", "gold1": "#E8A018", "gold2": "#FFE77A",       # the title's own
    "navy": "#0D1A3C", "slate": "#25396C", "steel": "#4A6AA8", "ice": "#A6DAF4",
    "ivory1": "#B6A68C", "ivory2": "#ECDFC4",
    "felt1": "#0F5434", "felt2": "#22844C",
}
KR = ["black", "grey", "ivory1", "ivory2", "cream"]                      # the white king
NR = ["black", "navy", "slate", "steel", "ice", "cream"]                 # the black knight
FR = ["black", "navy", "felt1", "felt2"]                                 # the board

YY, XX = np.mgrid[0:128, 0:128]

# ---- the scene ------------------------------------------------------------------------

KING, KNIGHT, FAR_W = 0, 1, 2
NMAT = 3
KING_PROF = [(0, 0), (0.44, 0), (0.44, 0.07), (0.40, 0.10), (0.40, 0.13), (0.42, 0.16), (0.39, 0.20), (0.31, 0.24),
             (0.25, 0.30), (0.20, 0.40), (0.17, 0.55), (0.15, 0.75), (0.14, 0.92), (0.17, 0.96), (0.24, 0.99),
             (0.24, 1.03), (0.18, 1.06), (0.20, 1.09), (0.16, 1.12), (0.17, 1.20), (0.21, 1.31), (0.25, 1.40),
             (0.28, 1.46), (0.28, 1.50), (0.24, 1.53), (0.20, 1.58), (0.14, 1.62), (0.08, 1.65), (0.06, 1.66),
             (0, 1.66)]
KNIGHT_BASE = [(0, 0), (0.40, 0), (0.40, 0.06), (0.37, 0.09), (0.36, 0.12), (0.38, 0.15), (0.36, 0.18),
               (0.30, 0.22), (0.27, 0.28), (0.0, 0.30)]
HEAD = [(0.27, 0.28), (0.31, 0.38), (0.33, 0.50), (0.32, 0.64), (0.29, 0.80), (0.25, 0.95), (0.20, 1.10),
        (0.15, 1.22), (0.09, 1.32), (0.03, 1.40), (-0.05, 1.44), (-0.13, 1.42), (-0.20, 1.37), (-0.26, 1.30),
        (-0.30, 1.24), (-0.37, 1.15), (-0.46, 1.04), (-0.55, 0.95), (-0.61, 0.88), (-0.63, 0.82), (-0.61, 0.77),
        (-0.55, 0.755), (-0.50, 0.77), (-0.53, 0.73), (-0.50, 0.68), (-0.42, 0.645), (-0.32, 0.65), (-0.22, 0.69),
        (-0.15, 0.71), (-0.12, 0.66), (-0.16, 0.57), (-0.24, 0.47), (-0.29, 0.38), (-0.25, 0.29)]
EARS = [((-0.06, 1.36, 0.06), (-0.04, 1.68, 0.07)), ((0.06, 1.33, -0.05), (0.12, 1.62, -0.06))]
PAWN_PROF = [(0, 0), (0.30, 0), (0.30, 0.06), (0.26, 0.09), (0.27, 0.12), (0.22, 0.15), (0.14, 0.22),
             (0.10, 0.45), (0.16, 0.50), (0.16, 0.53), (0.10, 0.56), (0.0, 0.56)]
FAR = [(FAR_W, (-2.0, 0, -1.6))]                      # a white pawn far off in the dark
KING_AT = np.array([-0.36, 0.0, 0.25])
KING_TILT = 11                                         # recoiling from the knight (degrees about z)
KNIGHT_AT = np.array([0.66, 0.64, -0.4])
KNIGHT_TURN = 16                                       # its face a little toward us
KNIGHT_LEAN = 20                                       # diving into the leap (degrees about z)
KNIGHT_ROLL = -8                                       # its foot's felt shows a sliver: it is off the board
KNIGHT_S = 0.9
CAM = R.Camera((0.35, 2.0, 3.7), (0.12, 0.85, 0.0), fov=50, shift=(0, 16))
KEY = np.array([-0.55, 0.75, 0.45])
KEY /= np.linalg.norm(KEY)
BOARD_YAW = 45.0                                       # the board's squares turned about the king's (degrees)
SQ = 1.2                                               # a square's side
POOL = (0.2, -0.4, 2.6, 2.0)                           # the pool of light on the board: centre (x, z), radii
HAZE_SEAM = 0.15                                       # its dithered edge, in levels
HAZE = (64, 90, 70, 17, 1.0)                           # the lamp's glow in the room behind the duel: centre, radii (px), strength
BOARD_LIGHT = (0.7, 2.6)                               # light squares: level at the dark's edge, gain in the pool
BOARD_DARK = (-0.5, 1.5)                               # dark squares
BOARD_SEAM = 0.2                                       # the dithered seams between its plateaus (levels)
FOG = (8.5, 3.0)                                       # the board fades out from this far from the camera, over this
KING_TOP, KING_UNDER = 0.5, 0.45                       # how much tops gain and undersides lose
KING_SOFT = 0.8                                        # the light smoothed over this (px) before it is cut
KING_CUTS = (0.30, 0.60)                               # grey | ivory1 | ivory2
KING_SEAM = 0.3                                        # how wide the dithered seams between them are (levels)
CROSS_ART = ["...cwi...",                              # the king's cross: w ivory2, i ivory1, g grey, c cream
             "...wwi...",
             "cwwwwwwwi",
             "iiiwwiiig",
             "...wwi...",
             "...wwi...",
             "....wwi..",
             "....wwi..",
             "....wwi.."]
CROSS_AT = (-5, 0)                                     # its bottom-left from the crown's top (px)
GLINT_K = (-0.27, 1.48, 0.08)                          # the glint on the crown's rim (the king's frame)
SHADOW_R = 0.3                                         # the knight's shadow straight below it (world radius)
KN_FALL = (17.0, 2.55, 1.0)                           # the head's fall from the lamp: over (px), middle level, slope
JOWL = (-0.25, 0.80, 0.15, 0.12)                       # the round cheek in the knight's frame: centre, radii
JAW = (-110, 50)                                       # the jaw line round it: from, to (degrees)
RIM = (0.35, 0.6, -0.3)                                # an edge lit (steel) above this facing, ice above, navy below
EYE_ART = ["...nnn",
           ".nnnbb",
           "nbbrrb",
           ".bbcrb",
           "..bbb."]
NOSTRIL_ART = ["bb"]
MANE = (0.0, 0.5, 1.33, 0.081, 0.075, 0.6)             # the mane: lx above, ly between, its depth, ridge spacing, slant
PING = (-0.18, 1.38, 0.1)                              # the gloss on the brow (the knight's frame)

ARC = ((22, -4), (64, -10))                             # the arc it came along: Bezier controls from its middle (px)
GHOSTS = [(26.0, "navy", "slate", 1), (13.0, "slate", "steel", 1)]   # (px back along the arc, fill, lit rim, its width), farthest first
GHOST_FROM = 0.5                                       # the ghosts are of the head above this (knight's frame)
# speed lines along the arc: (offset across it, gap from the knight, length, root radius) px
STREAKS = [(-9.0, 1, 30, 1.2), (1.0, 1, 40, 1.4), (11.0, 2, 26, 1.1)]
EYE = (-0.20, 1.16, 0.13)                              # in the knight's own frame
NOSTRIL = (-0.57, 0.88, 0.10)


def spline(prof, n=4):
    """A lathe profile through Catmull-Rom curves (n points a segment): smooth
    normals, so the bands follow the form instead of the polygon's facets."""
    P = np.array(prof, float)
    out = [P[0]]
    for i in range(len(P) - 1):
        p0, p1, p2, p3 = P[max(i - 1, 0)], P[i], P[i + 1], P[min(i + 2, len(P) - 1)]
        for t in np.arange(1, n + 1) / n:
            q = 0.5 * (2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (3 * p1 - p0 - 3 * p2 + p3) * t ** 3)
            out.append(np.maximum(q, (0.0, -1.0)))
    return [tuple(map(float, q)) for q in out]


def smin(a, b, k):
    s = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b + (a - b) * s - k * s * (1 - s)


def cone(p, a, b, r0, r1):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ab = b - a
    t = np.clip(((p - a) @ ab) / (ab @ ab), 0, 1)
    return np.linalg.norm(p - a - t[:, None] * ab, axis=1) - (r0 + (r1 - r0) * t)


def head_sdf(p):
    """The knight's horse head: its profile (HEAD, facing -x) given depth,
    thinner toward the muzzle, every edge rounded; a jowl and two ears."""
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    r = 0.07
    d2 = CV.polygon((x, y), HEAD).astype(np.float64)
    h = 0.16 - 0.06 * np.clip((-x - 0.05) / 0.45, 0, 1)
    a = d2 + r
    b = np.abs(z) - h + r
    d = np.minimum(np.maximum(a, b), 0) + np.hypot(np.maximum(a, 0), np.maximum(b, 0)) - r
    cheek = (np.sqrt(((x + 0.24) / 0.13) ** 2 + ((y - 0.84) / 0.11) ** 2 + (z / 0.15) ** 2) - 1.0) * 0.11
    d = smin(d, cheek, 0.04)
    e = np.minimum(*[cone(p, a_, b_, 0.085, 0.022) for a_, b_ in EARS])
    return smin(d, e, 0.03)


def knight_rot():
    return R.rot_y(KNIGHT_TURN) @ R.rot_x(KNIGHT_ROLL) @ R.rot_z(KNIGHT_LEAN)


def scene():
    k = R.lathe(spline(KING_PROF))
    pivot = np.array([-0.44, 0.0, 0.0])                    # the king rocks back onto the left of its foot
    king = R.xf(R.xf(R.prim(k, KING), -pivot), KING_AT + pivot, R.rot_z(KING_TILT))
    kn = R.SU(R.prim(R.lathe(spline(KNIGHT_BASE)), KNIGHT), R.prim(head_sdf, KNIGHT), 0.05)
    knight = R.xf(kn, KNIGHT_AT, knight_rot(), scale=KNIGHT_S)
    pawn_b, head = R.lathe(spline(PAWN_PROF)), R.sphere(0.15)

    def pawn(p):
        return np.minimum(pawn_b(p), head(p - np.array([0, 0.68, 0])))
    far = [R.xf(R.prim(pawn, m_), at) for m_, at in FAR]
    return R.U(king, knight, *far)


def king_point(q):
    """A point in the king's own frame (upright, its foot's centre at 0) in the world."""
    pivot = np.array([-0.44, 0.0, 0.0])
    return KING_AT + pivot + R.rot_z(KING_TILT) @ (np.asarray(q, float) - pivot)


def knight_point(q):
    """A point in the knight's own frame (its profile facing -x, the base on
    y 0) in the world."""
    return KNIGHT_AT + knight_rot() @ (np.asarray(q, float) * KNIGHT_S)


def knight_local(p):
    """World points (..., 3) in the knight's own frame."""
    return ((p - KNIGHT_AT) @ knight_rot()) / KNIGHT_S


def geometry(cam, sc, shadows=True):
    """Per pixel: the material (the majority of 16 samples), and at the
    pixel's centre the point, the normal, the view direction and how much
    of the key reaches it."""
    big = ak.Canvas("#000000")
    out = R.render(big, sc, cam, [R.Mat("#FFFFFF", spec=0.0)] * NMAT, ss=2, shadows=False, ao=False)
    mat = R.majority(out, big.s)
    one = ak.Canvas("#000000", ss=1)
    o1 = R.render(one, sc, cam, [R.Mat("#FFFFFF", spec=0.0)] * NMAT, ss=None, shadows=False, ao=False)
    o, d = cam.rays((XX + 0.5).reshape(-1).astype(np.float64), (YY + 0.5).reshape(-1).astype(np.float64))
    dep = o1["depth"].reshape(-1)
    hit = np.isfinite(dep)
    z = np.where(hit, dep, 0)
    p = o + d * z[:, None]
    n = o1["normal"].reshape(-1, 3).astype(np.float64)
    sh = np.ones(len(p))
    if shadows and hit.any():
        sh[hit] = R._shadow(sc, p[hit] + n[hit] * 2e-3, KEY, k=12.0)
    return dict(mat=mat, p=p.reshape(128, 128, 3), n=n.reshape(128, 128, 3), v=d.reshape(128, 128, 3),
                sh=sh.reshape(128, 128), hit=hit.reshape(128, 128))


def bands(l, cuts):
    """A value through flat bands: cuts [(threshold, level)] ascending."""
    out = np.full(l.shape, float(cuts[0][1]))
    for c, v in cuts[1:]:
        out = np.where(l >= c, float(v), out)
    return out


def rim2d(mask, towards=(0.8, -0.6), width=1, cut=0.3):
    """The pixels of a mask within `width` of its edge whose outward
    direction (on the picture) faces `towards` (x right, y down)."""
    k = np.array([1, 4, 6, 4, 1], float) / 16
    B = np.apply_along_axis(lambda v: np.convolve(v, k, "same"), 1, mask.astype(float))
    B = np.apply_along_axis(lambda v: np.convolve(v, k, "same"), 0, B)
    gy, gx = np.gradient(B)
    L = np.hypot(gx, gy)
    out = (-gx * towards[0] - gy * towards[1]) / np.hypot(*towards) / np.maximum(L, 1e-6)
    edge = mask & ~ak.erode(mask, width)
    return edge & (out > cut) & (L > 0.02)


def blur(a, sigma):
    """A separable Gaussian blur (numpy only)."""
    r = max(1, int(round(sigma * 3)))
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    k /= k.sum()
    out = np.apply_along_axis(lambda v: np.convolve(v, k, "same"), 1, np.asarray(a, float))
    return np.apply_along_axis(lambda v: np.convolve(v, k, "same"), 0, out)


def mblur(a, m, sigma):
    """A blur that stays inside the mask m (normalised convolution)."""
    w = blur(m.astype(float), sigma)
    return np.where(m, blur(np.where(m, a, 0.0), sigma) / np.maximum(w, 1e-6), a)


def outward(m, sigma=1.0):
    """Unit directions (x, y on the picture) pointing out of the mask."""
    B = blur(m.astype(float), sigma)
    gy, gx = np.gradient(B)
    L = np.maximum(np.hypot(gx, gy), 1e-6)
    return -gx / L, -gy / L


KEY2 = np.array([-0.6, -0.8])                              # the key on the picture: up and to the left


# ---- the pieces --------------------------------------------------------------------

def lathe_light(G, mask, rot, top=0.5, under=0.45, soft=0.8):
    """A turned piece's light per pixel: round its axis toward the key
    (0 away, 1 facing it), tops gaining, undersides and cast shadow losing,
    smoothed inside the mask so the bands it is cut into have clean
    edges; and where the gloss runs (the half-vector round the axis)."""
    nl = G["n"] @ rot                                     # normals in the piece's own (upright) frame
    kl = rot.T @ KEY
    hl = (KEY - G["v"]) @ rot
    ny = nl[..., 1]
    nxz = np.maximum(np.hypot(nl[..., 0], nl[..., 2]), 1e-6)
    c = (nl[..., 0] * kl[0] + nl[..., 2] * kl[2]) / nxz / np.hypot(kl[0], kl[2])
    ch = (nl[..., 0] * hl[..., 0] + nl[..., 2] * hl[..., 2]) / nxz / np.maximum(np.hypot(hl[..., 0], hl[..., 2]), 1e-6)
    L = 0.5 + 0.5 * c + top * np.clip(ny, 0, 1) - under * np.clip(-ny, 0, 1)
    L = np.where(G["sh"] < 0.5, L - 0.3, L)
    return mblur(L, mask, soft), ch, ny


def paint_king(pic, G, king, cam):
    """The white king, polished ivory: its light (lathe_light) cut into
    flat bands, grey, ivory1, ivory2, with short dithered seams between the
    wide ones, and one cream streak where the gloss runs down the stem; the
    cross stamped by hand."""
    L, ch, ny = lathe_light(G, king, R.rot_z(KING_TILT), KING_TOP, KING_UNDER, KING_SOFT)
    lv = ak.terrace(np.interp(L, [KING_CUTS[0] - 0.3, KING_CUTS[0], KING_CUTS[1], KING_CUTS[1] + 0.3], [0.5, 1.5, 2.5, 3.5]), KING_SEAM)
    lv = np.clip(lv, 1, 3)
    gloss = king & (ch > 0.988) & (np.abs(ny) < 0.3)
    lv = np.where(gloss, 4.0, lv)
    ak.by_level(pic, lv, KR, king, q=4)
    ak.despeckle(pic, 4, within=king, keep=gloss)
    # the cross, stamped by hand (its foot on the crown's top, its head a
    # pixel further over: the lean); a cream glint on its top-left
    tx, ty = (int(round(v)) for v in cam.project(king_point((0, 1.64, 0))))
    ak.patch(pic, tx + CROSS_AT[0], ty + CROSS_AT[1] - len(CROSS_ART) + 1, CROSS_ART,
             {"w": "ivory2", "i": "ivory1", "g": "grey", "c": "cream"})
    cross = np.zeros((128, 128), bool)
    for j, row in enumerate(CROSS_ART):
        for i, ch_ in enumerate(row):
            if ch_ != ".":
                cross[ty + CROSS_AT[1] - len(CROSS_ART) + 1 + j, tx + CROSS_AT[0] + i] = True
    # a glint where the crown's rim catches the lamp
    gx, gy = (int(round(v)) for v in cam.project(king_point(GLINT_K)))
    ak.glint(pic, gx, gy, 1)
    keep = ak.dilate(cross, 1) | gloss
    keep[gy - 1:gy + 2, gx - 1:gx + 2] = True
    return cross, keep


def paint_knight(pic, G, knight, cam):
    """The black knight, glossy blue-black lacquer, shaded on the picture
    from its silhouette: the flat of the head falls from steel on the lamp's
    side through slate to navy; its rounded edges light up (steel, then ice
    where the key grazes hardest: the brow, the bridge of the nose, the ear
    tips) only where they face the lamp, and fall to navy where they turn
    away; a carved mane of slate ridges down the back of the neck; a jaw
    line round the round cheek; one cream ping of gloss on the brow; the
    base turned like the king's, an ice lip where the key grazes it; the
    eye and the nostril stamped."""
    lp = knight_local(G["p"])
    ln = G["n"] @ knight_rot()
    lx, ly = lp[..., 0], lp[..., 1]
    base = knight & (ly < 0.31)
    head = knight & ~base
    d = ak.paint.distance_px(~head, 8)                     # 1 on the edge
    ox, oy = outward(head, 1.2)
    facing = ox * KEY2[0] + oy * KEY2[1]
    ys, xs = np.nonzero(head)
    cx, cy = xs.mean(), ys.mean()
    g = ((XX - cx) * -KEY2[0] + (YY - cy) * -KEY2[1]) / KN_FALL[0]
    L = KN_FALL[1] - KN_FALL[2] * g
    # the jowl: a round cheek, lit on its upper front, a navy crescent below
    jx, jy = (lx - JOWL[0]) / JOWL[2], (ly - JOWL[1]) / JOWL[3]
    jowl = head & (jx * jx + jy * jy < 1.0)
    jd = ak.paint.distance_px(~jowl, 4)
    jox, joy = outward(jowl, 0.8)
    jf = jox * KEY2[0] + joy * KEY2[1]
    L = np.where(jowl & (jd <= 2) & (jf < -0.3), np.minimum(L, 1.4), L)
    L = np.where(jowl & (jd <= 1) & (jf > 0.5), np.maximum(L, 3.0), L)
    L = mblur(L, head, 0.8)
    lv = bands(L, [(-9, 1), (1.5, 2), (2.5, 3)])
    # the rounded edges, by the way they face
    lit = head & (d <= 2) & (facing > RIM[0])
    lv = np.where(lit, np.maximum(lv, 3.0), lv)
    lv = np.where(lit & (d <= 1) & (facing > RIM[1]), 4.0, lv)
    turned = head & (d <= 2) & (facing < RIM[2])
    lv = np.where(turned, np.minimum(lv, 1.0 + (d >= 2)), lv)
    # the carved mane down the back of the neck: slate ridges across a navy band
    d2 = -CV.polygon((lx, ly), HEAD)                           # depth in from the profile's edge (the knight's units)
    mane = head & (lx > MANE[0]) & (ly > MANE[1]) & (ly < MANE[2]) & (d2 < MANE[3]) & (facing < 0.2)
    ridge = mane & (np.floor((ly + MANE[5] * lx) / MANE[4]) % 2 == 0)
    lv = np.where(mane, np.where(ridge, 2.0, 1.0), lv)
    ak.by_level(pic, lv, NR, head, q=1)
    ak.despeckle(pic, 4, within=head)
    # the jaw: a carved line round the back and bottom of the round cheek
    jaw = [cam.project(knight_point((JOWL[0] + JOWL[2] * np.cos(t), JOWL[1] + JOWL[3] * np.sin(t), 0.12)))
           for t in np.radians(np.linspace(*JAW, 12))]
    ak.paint.ink(pic, jaw, "navy", where=head & (d >= 2))
    # the gloss: one cream ping where the brow faces the lamp
    px_, py_ = (int(round(v)) for v in cam.project(knight_point(PING)))
    pic.px(px_, py_, "cream")
    # the base, a lathe: bands round its axis, tops lit
    Lb, chb, nyb = lathe_light(G, base, knight_rot(), 0.5, 0.5, 1.0)
    lb = bands(Lb, [(-9, 1), (0.45, 2), (0.8, 3)])
    ak.by_level(pic, lb, NR, base, q=1)
    ak.despeckle(pic, 3, within=base)
    bd = ak.paint.distance_px(~base, 3)
    box, boy = outward(base, 1.0)
    pic.put(base & (bd <= 1) & ((box * KEY2[0] + boy * KEY2[1]) > 0.5), "ice")      # its lip where the key grazes
    pad = base & (ln[..., 1] < -0.5) & (ly < 0.05)          # the felt under its foot, if it shows
    pic.put(pad, "felt1")
    ak.despeckle(pic, 4, within=base)
    # the eye: a black almond, a red pupil, a catch-light, a heavy brow lowest at the front
    ex, ey = (int(round(v)) for v in cam.project(knight_point(EYE)))
    ak.patch(pic, ex - 2, ey - 2, EYE_ART, {"b": "black", "c": "cream", "n": "navy", "r": "red", "s": "slate"})
    nx_, ny_ = (int(round(v)) for v in cam.project(knight_point(NOSTRIL)))
    ak.patch(pic, nx_, ny_, NOSTRIL_ART, {"b": "black", "n": "navy"})
    keep = np.zeros((128, 128), bool)
    keep[ey - 2:ey + 3, ex - 2:ex + 3] = True
    keep[ny_:ny_ + 2, nx_:nx_ + 3] = True
    keep[py_, px_] = True
    return keep | (lv >= 4)


# ---- the picture --------------------------------------------------------------------

def draw():
    P = ak.Palette(PAL, ramps=[KR, NR, FR, ["gold0", "gold1", "gold2", "cream"]])
    pic = ak.Picture.blank(P, "black")
    cam = CAM
    sc = scene()
    G = geometry(cam, sc)
    mat = G["mat"]
    pieces = mat >= 0
    king = mat == KING
    knight = mat == KNIGHT

    # ---- where each pixel's ray meets the floor
    o, d = cam.rays((XX + 0.5).reshape(-1).astype(np.float64), (YY + 0.5).reshape(-1).astype(np.float64))
    down = d[:, 1] < 0
    t = np.where(down, -o[:, 1] / np.minimum(d[:, 1], -1e-9), 1e9)
    bp = (o + d * t[:, None]).reshape(128, 128, 3)
    floor = down.reshape(128, 128) & ~pieces

    # ---- the board: green marble and black lacquer in a pool of lamplight
    # that falls off into the dark (flat plateaus, dithered only at their
    # seams; the squares' edges stay crisp)
    ca, sa = np.cos(np.radians(BOARD_YAW)), np.sin(np.radians(BOARD_YAW))
    rx, rz = bp[..., 0] - KING_AT[0], bp[..., 2] - KING_AT[2]          # the board turned about the king's square
    u, w = ca * rx - sa * rz, sa * rx + ca * rz
    sq_i = np.floor(u / SQ + 0.5)
    sq_j = np.floor(w / SQ + 0.5)
    light_sq = ((sq_i + sq_j) % 2) == 1                       # the king on a dark square, the knight's shadow on a light one
    pool = np.exp(-(((bp[..., 0] - POOL[0]) / POOL[2]) ** 2 + ((bp[..., 2] - POOL[1]) / POOL[3]) ** 2))
    ct = np.hypot(bp[..., 0] - cam.pos[0], bp[..., 2] - cam.pos[2])
    fog = np.clip((FOG[0] - ct) / FOG[1], 0, 1)
    pool = pool * fog
    # the dark squares flat, each by the light at its centre (lacquer: navy
    # in the pool's heart, black beyond); the marble by the light on it
    cu, cw = sq_i * SQ, sq_j * SQ
    cx_, cz_ = KING_AT[0] + ca * cu + sa * cw, KING_AT[2] - sa * cu + ca * cw
    pool_c = np.exp(-(((cx_ - POOL[0]) / POOL[2]) ** 2 + ((cz_ - POOL[1]) / POOL[3]) ** 2))
    pool_c = pool_c * np.clip((FOG[0] - np.hypot(cx_ - cam.pos[0], cz_ - cam.pos[2])) / FOG[1], 0, 1)
    blv = np.where(light_sq, (BOARD_LIGHT[0] + BOARD_LIGHT[1] * pool) * fog, np.round(BOARD_DARK[0] + BOARD_DARK[1] * pool_c))
    # the shadows, a level down: the king's from the key, the knight's
    # straight down (it is in the air), its core a level further (navy at
    # the least: a shadow, not a hole)
    shad = R.ground(ak.Canvas("#000000", ss=1), sc, cam, y=0.0, light=tuple(KEY), ss=None, ao=False, k=6.0)
    kx, kz = knight_point((0, 0.6, 0))[[0, 2]]
    dist = np.hypot(bp[..., 0] - kx, bp[..., 2] - kz)
    blv = ak.terrace(np.clip(blv, 0, 3), BOARD_SEAM)
    blv = blv - (shad > 0.5) - (dist < SHADOW_R) - (dist < SHADOW_R * 0.55)
    blv = np.where(dist < SHADOW_R, np.maximum(blv, 1.0), blv)        # its core navy, never a hole
    ak.by_level(pic, np.clip(blv, 0, 3), FR, floor, q=4)
    check = floor & (sq_i == 0) & (sq_j == 0)                  # the king's square: CHECK, in the game's red
    pic.put(check, "red")
    pic.put(check & (shad > 0.5), "black")

    # ---- the haze behind the duel: the lamp's light in the room's dark
    if HAZE:
        hz_ = np.exp(-(((XX - HAZE[0]) / HAZE[2]) ** 2 + ((YY - HAZE[1]) / HAZE[3]) ** 2)) * HAZE[4]
        sky = ~floor & ~pieces | (floor & (pic.idx == P["black"]))
        ak.by_level(pic, ak.terrace(hz_, HAZE_SEAM), ["black", "navy"], sky & (hz_ > 0.05) & (YY > 34), q=4)

    # ---- the far pawn, dim in the dark
    fw = mat == FAR_W
    Lf, _, _ = lathe_light(G, fw, np.eye(3), 0.5, 0.4, 0.6)
    ak.by_level(pic, bands(Lf, [(-9, 1), (0.55, 2)]), KR, fw, q=1)

    # ---- the knight's ghosts: its head where it was a moment ago, stepped
    # back along the arc it came along
    ys, xs = np.nonzero(knight)
    kc = np.array([xs.mean(), ys.mean()])
    arc = ak.bezier(tuple(kc), tuple(kc + ARC[0]), tuple(kc + ARC[1]), n=80)
    A = np.array(arc)
    seg0 = np.linalg.norm(np.diff(A, axis=0), axis=1)
    cum0 = np.concatenate([[0], np.cumsum(seg0)])
    headm = knight & (knight_local(G["p"])[..., 1] > GHOST_FROM)        # the ghosts are of the head
    front = pieces.copy()                                          # what is in front of the next ghost back
    ghosts = np.zeros((128, 128), bool)
    for back, col, rim, rw in reversed(GHOSTS):                    # nearest first: each is parted from the one before
        k = int(np.argmin(np.abs(cum0 - back)))
        dx, dy = (int(round(v)) for v in A[k] - A[0])
        gm = ak.shift(headm, dx, dy)
        vis = gm & ~ak.dilate(front, 1, diag=True)
        pic.put(gm & ~front & ~vis, "black")                       # the gap that parts it from what is in front
        pic.put(vis, col)
        pic.put(vis & rim2d(gm, towards=(-0.3, -0.95), width=rw, cut=0.55), rim)
        front |= gm
        ghosts |= vis

    # ---- in the haze, the knight and its ghosts are cut out by a black line
    if HAZE:
        gk = ghosts | knight
        pic.put(ak.dilate(gk, 1, diag=True) & ~gk & ~pieces & ~floor, "black")
        pic.put(ak.dilate(gk, 1) & ~gk & ~pieces & floor & pic.where("navy"), "black")

    # ---- the pieces
    cross, keep_k = paint_king(pic, G, king, cam)
    keep = paint_knight(pic, G, knight, cam)

    # ---- the leap: speed lines back along the arc it came on
    tang = np.gradient(A, axis=0)
    tang /= np.linalg.norm(tang, axis=1, keepdims=True)
    nrm = np.stack([-tang[:, 1], tang[:, 0]], 1)
    kd = ak.dilate(knight, 1, diag=True)
    ok = ~ak.dilate(pieces, 1, diag=True)
    speed = np.zeros((128, 128), bool)
    for off, gap, length, r0 in STREAKS:
        pts = A + nrm * off
        inside = np.array([0 <= int(x) < 128 and 0 <= int(y) < 128 and kd[int(y), int(x)] for x, y in pts])
        k0 = int(np.nonzero(inside)[0].max()) + 1 if inside.any() else 0
        seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
        cum = np.concatenate([[0], np.cumsum(seg)])
        cum = cum - cum[min(k0, len(cum) - 1)]                      # from where it leaves the knight
        i0 = int(np.argmin(np.abs(cum - gap)))
        i1 = int(np.argmin(np.abs(cum - gap - length)))
        im = (i0 + i1) // 2
        before = pic.idx.copy()
        m_ = ak.streak(pic, tuple(pts[i0]), tuple(2 * pts[im] - (pts[i0] + pts[i1]) / 2), tuple(pts[i1]), r0, 0.3,
                       ok=ok, cols=(("ice", 0.1), ("steel", 0.45), ("slate", 1.0)))
        # a step lighter where it crosses a ghost of its own colour, so it stays in sight
        for c_, up_ in (("slate", "steel"), ("steel", "ice")):
            pic.put(m_ & (before == P[c_]) & (pic.idx == P[c_]), up_)
        speed |= m_

    # ---- lone pixels
    ak.despeckle(pic, 5, keep=speed | keep | keep_k, passes=2)

    # ---- the frame: the outer two rows and columns a step darker (the
    # menu's border frames a dark edge)
    step = (("felt1", "navy"), ("felt2", "felt1"), ("navy", "black"), ("slate", "navy"), ("steel", "slate"),
            ("ice", "steel"), ("grey", "black"), ("ivory1", "grey"), ("ivory2", "ivory1"), ("cream", "ivory2"))
    for width in (2, 1):
        edge = np.zeros((128, 128), bool)
        edge[:, :width] = edge[:, -width:] = edge[-width:, :] = True
        before = pic.idx.copy()
        for a_, b_ in step:
            pic.put(edge & (before == P[a_]), b_)

    # ---- the title
    m = ak.load_mask(TITLE)
    tx = ak.centred_x(m)
    M_ = ak.place(m, tx, TITLE_Y)
    drawn = ak.title(pic, m, tx, TITLE_Y, fill=["gold2"], rows=TITLE_ROWS, hi=None, lo=None,
                     extrude=dict(dx=1, dy=1, depth=3, colours=["gold0", "slate", "navy"]),
                     shadow=dict(dx=1, dy=2, colour="black"))
    lab = ak.letters(M_)
    allE = drawn["extrude"]
    for i in range(1, lab.max() + 1):                             # each letter parted from its neighbours' depth
        Mi = lab == i
        Ei = np.zeros_like(Mi)
        for k in range(1, 4):
            Ei |= ak.shift(Mi, k, k)
        Ei &= ~M_
        pic.put(ak.dilate(Mi, 1) & ~Mi & allE & ~Ei, "black")
    for _ in range(2):                                            # slivers of depth in the serifs' and S's pockets: black
        for c_ in ("navy", "slate"):
            ak.lonely(pic, c_, allE & ~M_, into="black")
    hz = M_ & (YY == TITLE_Y + HORIZON) & ak.shift(M_, -1, 0)
    pic.put(hz, "gold0")
    ak.bevel_contour(pic, M_, "cream", "gold0")
    top = M_ & ~ak.shift(M_, 0, 1)                                # the light along every top edge, unbroken
    run = top & ak.shift(top, 1, 0) & ak.shift(top, -1, 0)
    pic.put((run | ak.shift(run, 1, 0) | ak.shift(run, -1, 0)) & top, "cream")
    ak.lonely(pic, "cream", M_)
    ak.lonely(pic, "gold0", M_)
    ak.lonely(pic, "gold2", M_)
    for gx, gy, sz in GLINTS:
        ak.glint(pic, tx + gx, TITLE_Y + gy, sz, tip="gold2")
    return pic.image()


if __name__ == "__main__":
    import boxart
    print(boxart.save(draw(), HERE.parent / "docs" / "cart.png"))
