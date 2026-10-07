"""docs/cart.png, Yacht Dice's picture in the visual menu (docs/cover-art.md).
`chgame boxart` redraws it; edit this, not the PNG.

THE BRIEF (revision 4)
  Message: five of a kind, the thrill of the Yacht. Four sixes are down and
  the fifth is still in the air, tumbling in on its corner: you read "five
  sixes" at a glance, and the one about to make it.
  Composition: the camera looks steeply down (about 58 degrees) into a
  mahogany dice tray, a real 3D one: its back rail runs under the title,
  its side rails come toward you out of the bottom corners, widening, so the
  tray frames the dice like a stage. A pool of light lies on the baize
  round the landing spot under the hero; the tray's far corners fall to
  navy. The four landed dice, every one a six, sit at the pool's edge in an
  arc round it: a small far one at the back left (grey top, darker); near
  ones at the left, the bottom (cropped by the frame, turned so its six
  reads as two rows: thrown dice land any way) and the right. The fifth,
  the hero, is the biggest and the only cream thing in the tray: balanced
  on its bottom corner, its six turned to us, three faces showing (the
  cream six, an ivory1 face on the lower left, a steel shadow face on the
  right that falls to navy at its foot, with a 1 px sea1 rim of reflected
  baize), its top corner breaking in front of the back rail under a
  four-pointed glint. Three curved speed lines stream back to the right
  from its trailing corner, thick at the root and tapering, ivory2 to
  ivory1 to steel. Its shadow waits on the brightest felt a pixel or two
  under its bottom corner: the footprint a cube throws, shrunk (a soft key
  far above), a navy core fading through sea1 into the pool. The eye runs
  title, hero, its streaks and shadow, then round the sixes.
  Light: the house key from the top left (the dice's lit edges by where
  they face in the picture). Everything below the rail is painted per pixel
  from the 3D renders as a level on its ramp, dithered by hand (Bayer 4x4 in
  quarter steps, 25, 50 and 75%: no lone dots): the felt from the pool,
  stirred by low noise (the cloth's nap), less the contact shadows (a
  steeper light keeps them compact) and the hero's shadow; the wood flat per
  surface (tops lit, the inner faces and the back rail's front in shade, its
  ends dithered down, three varnish glints on its lip, one on each side
  rail); the dice face by face, flat colours, crisp edges; the bottom rows
  step every ramp down into the dark.
  The dice by distance: the hero cream, ivory1, steel; the near dice ivory1
  tops with an unbroken ivory2 rim on the top and left edges, grey lit
  sides, steel fronts, a grey bevel between; the left one's top falls off
  to grey at its far corner; the far one a grey top with ivory1 rims. Pips:
  one round template a face (3-5-5-5-3 on the hero, 4 x 4 with the corners
  cut on the near tops, 3 x 2 on the far one), each with a pixel of face all
  round it, black and drilled on the tops (the inner wall facing the key a
  step lighter; a cream spark in the hero's top-left pip); side pips a step
  darker than their face, and none on a face too narrow for a 2 x 2 dot.
  Outlines: black on each die's shadow side and between overlapping dice,
  navy on the hero's lit side.
  Title: YACHT in a big bold Roman, gold leaf as painted on a yacht's
  transom (light gold, a dark horizon band, light again; strokes under 5 px
  step without dither), carved depth (a red lip under the feet and the A's
  bar, mahogany behind), a bevel (cream on the edges facing the key, gold0
  on the others), black outline and shadow, a glint on the A's apex; DICE
  under it between two gold rules (a cove stripe), each with a small
  diamond inboard. It sits on the calm navy of the room; nothing else uses
  the golds.
  Palette (11 own + cream, grey, black, red):
    navy0 sea1 sea2       the room and the baize: one hue-shifted ramp, navy
                          in the shadows, warm green at the pool's heart
    steel ivory1 ivory2   the dice, with grey between steel and ivory1 and
                          cream above (steel the cool shadow side)
    wood0 wood1           the mahogany tray (and the title's depth, with red)
    gold0 gold1 gold2     the title's own: nothing else uses them
  Font: timB24 (YACHT) and timB14 (DICE), u8g2's bitmaps of the X11 Times
  Bold (Adobe; the X11 notice permits use and modification with the notice
  kept) (tools/art/title.txt, title_dice.txt; credits in their headers).
  YACHT is kerned by hand (Y-A tighter, A-C 2 px tighter, H-T looser), its
  Y and A hairlines evened to 2 px, the C's beak opened under its arc;
  DICE's E kerned in.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import numpy as np  # noqa: E402
import artkit as ak  # noqa: E402
from artkit import render3d as R  # noqa: E402

TITLE = HERE / "art" / "title.txt"
TITLE2 = HERE / "art" / "title_dice.txt"
# YACHT's gold leaf: light, a dark horizon band, light again (a pair: a dithered seam)
TITLE_ROWS = (["gold2"] * 7 + [("gold2", "gold1")] + ["gold1"] * 3 + [("gold1", "gold0"), "gold0", ("gold0", "gold1")]
              + ["gold1"] * 4 + [("gold1", "gold2")] + ["gold2"] * 4)

# ---- the scene ----------------------------------------------------------------------

CAMERA = ((0.2, 7.4, 5.6), (0.2, 0.0, 1.0), 44, (0, 14))       # pos, target, fov, lens shift
RAIL = 53                                                        # the back rail's top row
FOOT = 60                                                        # where it meets the felt (screen row, x 64)
SIDES = (17, 111)                                                # the side rails' inner feet at the back (screen x)
SIDE_T = 0.6                                                     # the side rails' thickness (the back rail's is 0.25)
# where things land on the picture (pixels); the world positions follow
LANDED = [((28, 73), 98, "back", 0.8),                           # (centre on screen, turn about y, tier, size)
          ((25, 101), -6, "left", 1.0),
          ((53, 122), 95, "near", 1.0),
          ((101, 104), -7, "near", 1.0)]
HERO = dict(at=(63, 78), h=1.9, six=(-0.12, 0.5, 0.86), spin=30, size=1.18)   # the fifth, in the air
# (six: where its six looks, in screen terms: x right, y up, z toward us; its
# three faces take cream, ivory1 and steel by how lit they are)
LIGHTS = [((-0.6, 0.75, -0.12), "#FFF0D8", 1.0), ((0.8, 0.3, 0.5), "#6080C0", 0.25)]
SUN = (-0.42, 0.85, -0.32)                                       # the felt's contact shadows: steeper, so short
POOL = (68, 98, 66, 46)                                          # the light's pool on the felt
NAP = (10, 0.2)                                                  # the cloth's nap: noise scale (px), strength
SHADOW = dict(scale=0.42, gap=1, dx=3, depth=2.3, soft=3.4)      # the hero's shadow: its footprint, scaled, under it
BOUNCE = "sea1"                                                  # the felt's light in the hero's shadow side
# speed lines from the hero's trailing corner: root, control, end (px from
# it: a curve rising gently out along the arc it fell along), radius at the
# root and at the tip
STREAKS = [((2, 0), (11, -4), (25, -3), 1.5, 0.3),
           ((1, 7), (12, 2), (27, 1), 1.4, 0.3),
           ((-2, 13), (9, 10), (22, 8), 1.0, 0.3)]
GLINT = (-1, -1, (2, 2, 2, 2))                                   # the hero's glint: offset from its top corner, arms
HOT = 0.6                                                        # an edge facing the key (n . the screen's key)
FALL_FROM = 0.25                                                 # a top falls off from here (0 its middle) to its far corner
VIGNETTE = 6                                                     # rows the bottom edge darkens over

FELT_R = ["black", "navy0", "sea1", "sea2"]
DICE_R = ["black", "navy0", "steel", "grey", "ivory1", "ivory2", "cream"]
WOOD_R = ["black", "wood0", "wood1"]
BAY = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) + 0.5) / 16
TH = np.tile(BAY, (32, 32))

# ---- the dice -----------------------------------------------------------------------

S = 0.25                                              # pip spacing on a face (die edge 1)
PIPS = {1: [(0, 0)], 2: [(-S, -S), (S, S)], 3: [(-S, -S), (0, 0), (S, S)],
        4: [(-S, -S), (S, -S), (-S, S), (S, S)], 5: [(-S, -S), (S, -S), (-S, S), (S, S), (0, 0)],
        6: [(-S, -S), (-S, 0), (-S, S), (S, -S), (S, 0), (S, S)]}
FACES = {6: ((0, 1, 0), (1, 0, 0), (0, 0, 1)), 1: ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
         2: ((0, 0, 1), (1, 0, 0), (0, 1, 0)), 5: ((0, 0, -1), (1, 0, 0), (0, 1, 0)),
         3: ((1, 0, 0), (0, 0, 1), (0, 1, 0)), 4: ((-1, 0, 0), (0, 0, 1), (0, 1, 0))}
FACE_TAB = np.array([[4, 3], [1, 6], [5, 2]])          # (axis, outward?) -> the face's pips
AXIS = {6: 1, 1: 1, 2: 2, 5: 2, 3: 0, 4: 0}
PIP_R = 0.088
# each tier: how lit a face is (0..1) -> its level on DICE_R; `hi` the level of
# an edge that faces the key; `fall` how far a top's far corner falls off
TIERS = {
    "hero": dict(face=[(0.0, 1), (0.12, 2), (0.4, 4), (0.62, 5), (0.75, 6)], hi=6, fall=0.0),
    "near": dict(face=[(0.0, 1), (0.15, 2), (0.5, 3), (0.72, 4)], hi=5, fall=0.0),
    "left": dict(face=[(0.0, 1), (0.15, 2), (0.5, 3), (0.72, 4)], hi=5, fall=0.5),
    "back": dict(face=[(0.0, 1), (0.15, 2), (0.72, 3)], hi=4, fall=0.0),
}


def face_of(loc):
    """The face (pip count) each local normal points out of."""
    k = np.argmax(np.abs(loc), axis=-1)
    out = np.take_along_axis(loc, k[..., None], -1)[..., 0] > 0
    return FACE_TAB[k, out.astype(int)]


def orient(six, spin):
    """A rotation (local -> world) that turns a die's six (local +y) to `six`
    and spins it `spin` degrees about that axis."""
    y = np.asarray(six, float)
    y /= np.linalg.norm(y)
    x = np.cross(y, (0.0, 0.0, 1.0))
    x /= np.linalg.norm(x)
    z = np.cross(x, y)
    a = np.radians(spin)
    x, z = np.cos(a) * x + np.sin(a) * z, -np.sin(a) * x + np.cos(a) * z
    return np.stack([x, y, z], axis=1)


def lightness(n, key, fill):
    return np.clip(n @ key, 0, 1) * 0.85 + np.clip(n @ fill, 0, 1) * 0.15 + 0.1


def by_level(pic, level, ramp, where, q=4):
    """An ordered (Bayer 4x4) dither of a float level (0 is ramp[0], 1 the
    next ...) over `where`, in steps of 1/q (4: 25, 50, 75%, so no lone
    dots)."""
    b = np.floor(level)
    f = np.round((level - b) * q) / q
    i = np.clip(b + (f > TH), 0, len(ramp) - 1).astype(int)
    for k, nm in enumerate(ramp):
        pic.put(where & (i == k), nm)


def px_mean(a, s):
    """A canvas-sized array averaged down to pixels."""
    return a.reshape((128, s, 128, s) + a.shape[2:]).mean(axis=(1, 3))


def nbrs(m, diag=False):
    out = np.zeros_like(m)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) + (((1, 1), (-1, 1), (1, -1), (-1, -1)) if diag else ()):
        out |= ak.shift(m, dx, dy)
    return out


def hull(pts):
    """Convex hull, counter-clockwise (monotone chain)."""
    pts = sorted(map(tuple, pts))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


# ---- the title ----------------------------------------------------------------------

def runs(m, axis):
    """For each True pixel, the length of the run it is in: along rows
    (axis 1) or columns (axis 0)."""
    out = np.zeros(m.shape, int)
    a = m if axis == 1 else m.T
    o = out if axis == 1 else out.T
    for r in range(a.shape[0]):
        row, x = a[r], 0
        while x < len(row):
            if row[x]:
                e = x
                while e < len(row) and row[e]:
                    e += 1
                o[r, x:e] = e - x
                x = e
            else:
                x += 1
    return out


def gold_face(pic, M, rows):
    """The letters' face row by row: each entry a colour, or (a, b) for a
    seam: a, with a 50% checker of b where the stroke is 5 px or wider (a
    narrower stroke steps cleanly: no lone pixels)."""
    top = int(np.nonzero(M.any(axis=1))[0].min())
    ck = ak.checker()
    wide = M & (runs(M, 1) >= 5) & ak.shift(M, 1, 0) & ak.shift(M, -1, 0)
    for j, c in enumerate(rows):
        row = np.zeros_like(M)
        row[top + j, :] = True
        row &= M
        if isinstance(c, tuple):
            pic.put(row, c[0])
            pic.put(row & wide & ~ck, c[1])
        else:
            pic.put(row, c)


def bevel(pic, M, hi, lo, L=(-1.0, -0.3), t=0.1, long=3):
    """A light edge where a stroke faces the key (up and left) and a dark one
    where it faces away.
    - Straight edges (runs of 3 px or more) go by their side: a top or left
      edge is light, a bottom or right one dark, the whole run one colour
      (the longer run wins at a corner).
    - The rest (diagonals) go by the outward normal of the blurred letter,
      the side before the top, so a diagonal edge is one colour all along.
    - Bars exposed on both sides (a 1 px crossbar) and strokes 2 px wide or
      less keep their face, and so does a bevel pixel with no neighbour of
      its own kind."""
    sh = ak.shift
    up, dn = M & ~sh(M, 0, 1), M & ~sh(M, 0, -1)
    lf, rt = M & ~sh(M, 1, 0), M & ~sh(M, -1, 0)
    ru, rd, rl, rr = runs(up, 1), runs(dn, 1), runs(lf, 0), runs(rt, 0)
    cls = np.zeros(M.shape, int)
    best = np.zeros(M.shape, int)
    for r, c in ((ru, 1), (rd, -1), (rl, 1), (rr, -1)):
        take = (r >= long) & (r > best)
        cls[take] = c
        best[take] = r[take]
    k = np.array([1, 4, 6, 4, 1], float) / 16
    B = np.apply_along_axis(lambda v: np.convolve(v, k, "same"), 1, M.astype(float))
    B = np.apply_along_axis(lambda v: np.convolve(v, k, "same"), 0, B)
    gy, gx = np.gradient(B)
    d = (-gx * L[0] - gy * L[1]) / np.hypot(*L) / np.maximum(np.hypot(gx, gy), 1e-6)
    rest = (up | dn | lf | rt) & (best == 0) & ~((up & dn) | (lf & rt))
    cls[rest & (d > t)] = 1
    cls[rest & (d < -t)] = -1
    cls[(up & dn) & (ru >= 5) & (rd >= 5)] = 0
    cls[(lf & rt) & (rl >= 5) & (rr >= 5)] = 0
    cls[(runs(M, 1) <= 2) & (ru < long) & (rd < long)] = 0
    for c in (1, -1):
        m = cls == c
        cls[m & ~nbrs(m, diag=True)] = 0
    pic.put(cls == -1, lo)
    pic.put(cls == 1, hi)
    return cls


def extrude(pic, M, steps, outline="black"):
    """Depth under the letters: `steps` is [(dx, dy, colour)] from the face
    back. A layer's lone pixels (no 4-way neighbour in it: the stair steps
    of a diagonal) are left to the outline, unless they touch the face (the
    depth under a hairline, which would otherwise show a pinhole). Returns
    everything drawn (face included), the outline and the layers."""
    acc = M.copy()
    layers = []
    for dx, dy, c in steps:
        L0 = ak.shift(M, dx, dy) & ~acc
        L = L0 & nbrs(L0)
        L |= L0 & ak.shift(M, 0, 1) & ak.shift(acc, 1, 0)        # under a hairline, beside the depth
        layers.append((L, c))
        acc |= L
    O = ak.dilate(acc, 1) & ~acc
    return acc, O, layers


# ---- pixel work ---------------------------------------------------------------------

def glint(pic, x, y, size, tip="ivory2", arms=None):
    """A four-pointed star: cream, its arms' last pixel `tip` (a taper).
    arms: (left, right, up, down) lengths, when they differ."""
    pic.px(x, y, "cream")
    arms = arms or (size,) * 4
    for (dx, dy), n in zip(((-1, 0), (1, 0), (0, -1), (0, 1)), arms):
        for k in range(1, n + 1):
            pic.px(x + dx * k, y + dy * k, tip if k == n and n > 1 else "cream")


def pip_template(w, h):
    """A round dot w x h px: a square up to 3, an ellipse's pixels from 4
    (4 x 4 loses its corners, 5 x 5 is 3-5-5-5-3)."""
    if min(w, h) < 3 or max(w, h) < 4:
        return np.ones((h, w), bool)
    j, i = np.meshgrid((np.arange(w) + 0.5 - w / 2) / (w / 2), (np.arange(h) + 0.5 - h / 2) / (h / 2))
    return i * i + j * j < 0.98


def pips(pic, cam, pos, nw, uw, vw, face, inner, size, col, cup=None, min_px=2):
    """A face's pips, one template each: a round dot the size the
    perspective gives them on average (a pixel out of round at most), and
    smaller if neighbours would touch. A pip keeps a pixel of face all
    round it (nudged in toward the face's middle if it would touch an edge;
    `inner` is the face without its rounded edges). `cup` lights the inner
    wall that faces the key (the dot's lower right) a step lighter: a
    drilled pip. A face whose dots would be under min_px x min_px gets none.
    Returns the cup pixels."""
    cs, ws, hs = [], [], []
    for a, b in PIPS[face]:
        c = pos + (nw * 0.5 + uw * a + vw * b) * size
        ring = np.array([cam.project(c + PIP_R * size * (np.cos(t) * uw + np.sin(t) * vw))
                         for t in np.linspace(0, 2 * np.pi, 24, endpoint=False)])
        cs.append(cam.project(c))
        ws.append(np.ptp(ring[:, 0]))
        hs.append(np.ptp(ring[:, 1]))
    w, h = int(round(np.mean(ws))), int(round(np.mean(hs)))
    w, h = min(w, h + 1, 5), min(h, w + 1, 5)
    cups = np.zeros((128, 128), bool)
    if not inner.any():
        return cups
    ys, xs = np.nonzero(inner)
    mx, my = xs.mean(), ys.mean()
    while w >= min_px and h >= min_px:
        tpl = pip_template(w, h)
        placed = []
        for cx, cy in cs:
            x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
            for k in range(4):                                 # nudge toward the middle until it fits
                m = ak.place(tpl, x0, y0)
                if (ak.dilate(m, 1) & ~inner).sum() == 0:
                    placed.append((x0, y0, m))
                    break
                ex, ey = mx - (x0 + w / 2), my - (y0 + h / 2)
                x0 += int(np.sign(ex)) if abs(ex) > 0.5 else 0
                y0 += int(np.sign(ey)) if abs(ey) > 0.5 else 0
        clash = any((ak.dilate(a[2], 1) & b[2]).any() for i, a in enumerate(placed) for b in placed[i + 1:])
        if len(placed) == len(cs) and not clash:
            break
        w, h = w - 1, h - 1                                    # too big for the face: one size down
    else:
        return cups
    lit = np.zeros_like(tpl)
    if cup and w >= 4 and h >= 4:
        lit[h - 2, w - 2] = True
    for x0, y0, m in placed:
        pic.put(m, col)
        c = ak.place(lit, x0, y0)
        if cup:
            pic.put(c, cup)
        cups |= c
    return cups


def streak(pic, root, ctrl, end, r0, r1, ok, cols=(("ivory2", 0.3), ("ivory1", 0.65), ("steel", 1.0)), ss=4, cut=0.5):
    """A speed line: a quadratic curve from `root` (by the die) through
    `ctrl` to `end`, `r0` px in radius at the root tapering to `r1`, set
    where `ok` is: a pixel is in when `cut` of it is covered (4 x 4 samples).
    Its colour steps along it: cols [(name, up to t)]. Returns its mask."""
    pts = ak.bezier(root, ctrl, end, n=40)
    c = (np.arange(128 * ss) + 0.5) / ss
    X, Y = np.meshgrid(c, c)
    d = ak.polyline((X, Y), pts, r0, r1)
    cov = (d < 0).reshape(128, ss, 128, ss).mean(axis=(1, 3))
    m = (cov >= cut) & ok
    ys, xs = np.nonzero(m)
    Pt = np.array(pts)
    t = ((xs[:, None] + 0.5 - Pt[None, :, 0]) ** 2 + (ys[:, None] + 0.5 - Pt[None, :, 1]) ** 2).argmin(1) / (len(pts) - 1)
    lo = 0.0
    for name, hi in cols:
        sel = (t >= lo) & (t <= hi)
        if name:
            pic.idx[ys[sel], xs[sel]] = pic.pal[name]
        lo = hi
    return m


# ---- the picture --------------------------------------------------------------------

def draw():
    P = ak.Palette({
        "navy0": "#0A1A30", "sea1": "#0D4446", "sea2": "#188258",
        "steel": "#5A6E7C", "ivory1": "#B4A286", "ivory2": "#E0CDA6",
        "wood0": "#3A0E06", "wood1": "#7A2810",
        "gold0": "#94500E", "gold1": "#EAA622", "gold2": "#FFEA8C",
    }, ramps=[FELT_R, DICE_R, WOOD_R, ["gold0", "gold1", "gold2", "cream"]])
    cv = ak.Canvas("#0A1A30")
    s = cv.s
    yy, xx = np.mgrid[0:128, 0:128]
    pic = ak.Picture.blank(P, "navy0")

    cp, ct, cf, csh = CAMERA
    cam = R.Camera(cp, ct, fov=cf, shift=csh)
    key = np.array(LIGHTS[0][0], float)
    key /= np.linalg.norm(key)
    fill = np.array(LIGHTS[1][0], float)
    fill /= np.linalg.norm(fill)

    key_screen = -0.6 * cam.r + 0.6 * cam.u - 0.5 * cam.f       # up-left and toward us, as the picture shows it
    key_screen /= np.linalg.norm(key_screen)

    def at(sx, sy, h):
        o, d = cam.rays(np.array([sx], float), np.array([sy], float))
        return o[0] + d[0] * (h - o[0, 1]) / d[0, 1]

    # ---- the 3D: the tray, the felt and the landed dice in one render (lit
    # by the steep SUN, for the felt's shadows), the hero in its own
    zb = at(64, FOOT, 0)[2]
    xl, xr = at(SIDES[0], FOOT, 0)[0], at(SIDES[1], FOOT, 0)[0]
    t = 0.25
    lo_, hi_ = 0.05, 2.0
    for _ in range(40):                                   # the height that puts the rail's back edge on RAIL
        hw = (lo_ + hi_) / 2
        if cam.project((0.2, hw, zb - t))[1] < RAIL:
            hi_ = hw
        else:
            lo_ = hw
    rr = min(t, hw) * 0.35
    Lr = 30.0
    WALL = 1
    tray = R.U(R.xf(R.prim(R.box((Lr, hw / 2, t / 2), rr), WALL), (0.2, hw / 2, zb - t / 2)),
               R.xf(R.prim(R.box((SIDE_T / 2, hw / 2, Lr), rr), WALL), (xl - SIDE_T / 2, hw / 2, zb - t + Lr)),
               R.xf(R.prim(R.box((SIDE_T / 2, hw / 2, Lr), rr), WALL), (xr + SIDE_T / 2, hw / 2, zb - t + Lr)))
    FELT = 0
    mats = [R.Mat("#FFFFFF", spec=0.0), R.Mat("#FFFFFF", spec=0.0)]
    dice = []
    for k, (scr, turn, tier, size) in enumerate(LANDED):
        pos = at(*scr, 0.5 * size)
        rot = R.rot_y(turn)
        mats.append(R.Mat("#FFFFFF", spec=0.0, amb=1.0))
        node = R.xf(R.prim(R.box((0.5 * size,) * 3, 0.12 * size), 2 + k), pos, rot)
        dice.append(dict(k=2 + k, node=node, pos=pos, rot=rot, tier=tier, size=size))
    HK = 2 + len(dice)
    hs = HERO["size"]
    sv = HERO["six"]
    hrot = orient(sv[0] * cam.r + sv[1] * cam.u - sv[2] * cam.f, HERO["spin"])
    hpos = at(*HERO["at"], HERO["h"])
    mats.append(R.Mat("#FFFFFF", spec=0.0, amb=1.0))
    hero = dict(k=HK, node=R.xf(R.prim(R.box((0.5 * hs,) * 3, 0.07 * hs), HK), hpos, hrot),
                pos=hpos, rot=hrot, tier="hero", size=hs)
    felt = R.prim(lambda p: p[:, 1] + 0.0 * p[:, 0], FELT)
    out = R.render(cv, R.U(felt, tray, *[d["node"] for d in dice]), cam, mats,
                   lights=[(SUN, "#FFFFFF", 1.0)], ambient="#202020", ss=2, region=(0, RAIL - 2, 128, 128))
    hx, hy = cam.project(hpos)
    out2 = R.render(cv, hero["node"], cam, mats, lights=LIGHTS, ss=2,
                    region=(int(hx) - 32, int(hy) - 32, int(hx) + 32, int(hy) + 32))

    # each pixel's owner: the object most of its samples hit (the hero over all)
    ids = [-1, FELT, WALL] + [d["k"] for d in dice]
    cnt = np.stack([px_mean((out["mat"] == k).astype(np.float32), s) for k in ids], -1)
    owner = np.array(ids)[cnt.argmax(-1)]
    hero_px = px_mean(((out2["mat"] == HK) & (out2["alpha"] > 0.5)).astype(np.float32), s) >= 0.5
    owner[(owner == FELT) & (yy < FOOT - 2)] = -1                       # the floor seen over the rail is the room
    owner[hero_px] = HK
    room = owner == -1
    felt_px = owner == FELT
    wood_px = owner == WALL

    # the vignette: the last rows step down every ramp into the dark
    vig = np.clip((yy - (127 - VIGNETTE)) / VIGNETTE, 0, 1) ** 1.3 * 3.2

    # ---- the room: navy, falling to black in the top corners
    v = np.hypot((xx + 0.5 - 64) / 84, (yy + 0.5 - 40) / 60)
    dark = np.round(np.clip((v - 0.8) / 0.25, 0, 1) * 4) / 4
    pic.put(room, "navy0")
    pic.put(room & (TH < dark), "black")

    # ---- the felt: one pool of light round the landing spot, sea green at
    # its heart through sea1 and navy to black, its falloff stirred by low
    # noise (light on cloth, not rings); the render's contact shadows and
    # the hero's own shadow taken off its level
    lumw = np.array([0.299, 0.587, 0.114], np.float32)
    lum = px_mean(out["rgb"] @ lumw, s)
    fl = felt_px & (yy > FOOT - 3)
    lit = np.clip(lum / np.percentile(lum[fl], 97), 0, 1)
    lit = np.clip((lit - 0.3) / 0.45, 0, 1)
    X1, Y1 = xx + 0.5, yy + 0.5
    nz_ = ak.noise((X1, Y1), NAP[0], seed=7, octaves=2) - 0.5
    tp = np.clip(ak.radial((X1, Y1), *POOL) + NAP[1] * nz_, 0, 1.2)
    level = np.interp(tp, [0, 0.3, 0.55, 0.8, 1.0, 1.2], [3.3, 2.95, 2.3, 1.5, 0.9, 0.5])
    level -= (1 - lit) * 0.75

    # the hero's shadow: the footprint a cube throws straight down, shrunk
    # (a soft key far above) and hung just under its bottom corner: a navy
    # core through a navy/sea1 dither, sea1 and sea1/sea2 into the felt
    hm = hero_px
    hy0, hx0 = np.nonzero(hm)
    yb = hy0.max()
    xb = hx0[hy0 >= yb - 1].mean()
    corners = [hpos + hrot @ (np.array([a, b, c]) * 0.5 * hs) for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)]
    foot = np.array([cam.project((p[0], 0.0, p[2])) for p in corners])
    poly = np.array(hull(foot))
    cx_, cy_ = poly.mean(axis=0)
    poly = (poly - (cx_, cy_)) * SHADOW["scale"]
    top = poly[:, 1].min()
    poly += (xb + SHADOW["dx"], yb + 1 + SHADOW["gap"] - top)
    dsh = ak.polygon((X1, Y1), [tuple(p) for p in poly])
    shd = np.clip((0.5 - dsh) / SHADOW["soft"], 0, 1) * SHADOW["depth"]
    level = np.where(shd > 0, np.maximum(level - shd, np.minimum(level, 1.0)), level)   # its core navy, never black
    by_level(pic, level - vig, FELT_R, felt_px)

    # ---- the tray: mahogany by how each part faces the key (tops lit, the
    # back rail's front and the left rail's inner face in shade, the right
    # rail's inner face toward the key), varnish glints on the lips
    nW = px_mean(out["normal"] * (out["mat"] == WALL)[..., None], s)
    nW /= np.maximum(np.linalg.norm(nW, axis=-1, keepdims=True), 1e-6)
    lw = 0.5 * np.clip(nW[..., 1], 0, 1) + 0.5 * np.clip(nW @ key, 0, 1)   # the tops lit, every inner face in shade
    wl = np.round(np.interp(lw, [0.0, 0.25, 0.45, 0.62, 0.8], [0.9, 1.0, 1.25, 1.8, 2.0]))   # each surface flat
    wl -= np.clip((np.abs(xx - 64) - 44) / 30, 0, 1) * 0.5 * (yy < FOOT)        # the back rail's ends
    by_level(pic, wl - vig, WOOD_R, wood_px)
    lip = wood_px & (nW[..., 1] > 0.3) & (nW[..., 1] < 0.9) & (nW[..., 2] > 0.3) & (yy < FOOT)
    glx = np.zeros((128, 128), bool)
    for a, b in ((9, 22), (27, 34), (40, 43)):
        glx[:, a:b + 1] = True
    lip_row = lip & ~ak.shift(lip, 0, 1)                    # the lip's top row only: a clean line
    pic.put(lip_row & glx, "ivory1")
    # the side rails' varnish: a short glint near the back of each top
    for side in (-1, 1):
        topm = wood_px & (nW[..., 1] > 0.85) & (yy > FOOT) & ((xx < 64) if side < 0 else (xx > 64))
        topm &= (yy < FOOT + 22)
        inner_edge = topm & ~ak.shift(topm, side, 0)        # the edge toward the felt
        pic.put(inner_edge & (yy > FOOT + 3) & (yy < FOOT + 13), "ivory1")
    # the tray's foot: a black contact line where the felt meets the wood
    pic.put(felt_px & (ak.shift(wood_px, 0, 1) | ak.shift(wood_px, 1, 0) | ak.shift(wood_px, -1, 0)), "black")

    # ---- the dice, face by face
    o_all, d_all = cam.rays(cv.X.reshape(-1).astype(np.float64), cv.Y.reshape(-1).astype(np.float64))

    def die_pixels(o, d):
        """Per pixel of one die: its face, whether on a rounded edge, its
        mean normal, its mean local position (die edge 1)."""
        k, rot, pos, size = d["k"], d["rot"], np.asarray(d["pos"], float), d["size"]
        sel = (o["mat"] == k) & (o["alpha"] > 0.5)
        nrm = o["normal"].astype(np.float64)
        loc_n = nrm @ rot
        fc = face_of(loc_n)
        srt = np.sort(np.abs(loc_n), axis=-1)
        edge = srt[..., 1] > 0.35
        cntf = np.stack([px_mean((sel & (fc == f)).astype(np.float32), s) for f in range(1, 7)], -1)
        face = cntf.argmax(-1) + 1
        nsel = np.maximum(px_mean(sel.astype(np.float32), s), 1e-6)
        edge_px = px_mean((sel & edge).astype(np.float32), s) / nsel > 0.5
        nmean = px_mean(nrm * sel[..., None], s)
        nmean /= np.maximum(np.linalg.norm(nmean, axis=-1, keepdims=True), 1e-6)
        dep = np.where(sel, o["depth"], 0.0).reshape(-1)
        hit = o_all + d_all * dep[:, None]
        loc = ((hit - pos) @ rot / size).reshape(cv.N, cv.N, 3) * sel[..., None]
        lmean = px_mean(loc, s) / nsel[..., None]
        wy = px_mean(hit[:, 1].reshape(cv.N, cv.N) * sel, s) / nsel
        return face, edge_px, nmean, lmean, wy

    order = sorted(dice + [hero], key=lambda d: -np.linalg.norm(np.asarray(d["pos"]) - cam.pos))
    die_mask = {}
    for d in order:
        k, rot, tier, size = d["k"], d["rot"], d["tier"], d["size"]
        T = TIERS[tier]
        o = out2 if k == HK else out
        m = owner == k
        die_mask[k] = m
        face, edge, nmean, lmean, wy = die_pixels(o, d)
        lvl = np.zeros((128, 128))
        cut = np.array([a for a, _ in T["face"]])
        lv_tab = np.array([b for _, b in T["face"]], float)
        flat = np.zeros((128, 128), bool)               # pixels that stay one flat colour (no dither)
        shown = [f for f in range(1, 7) if (m & (face == f) & ~edge).any()]
        rank = sorted(shown, key=lambda f: -(rot @ np.array(FACES[f][0], float)) @ key_screen)
        for f in range(1, 7):
            fm = m & (face == f) & ~edge
            if not fm.any():
                continue
            nf = rot @ np.array(FACES[f][0], float)
            lf_ = lightness(nf, key, fill)
            base = lv_tab[np.searchsorted(cut, lf_, side="right") - 1]
            if k == HK:                                 # the hero: cream, ivory1, steel by rank
                base = [6, 4, 2, 2][rank.index(f)]
            lvl[fm] = base
            ax = [i for i in range(3) if i != AXIS[f]]
            kl = (key_screen if k == HK else key) @ rot
            kk = kl[ax] / max(np.linalg.norm(kl[ax]), 1e-6)
            far = np.clip((-(lmean[..., ax] @ kk) - FALL_FROM) / (0.62 - FALL_FROM), 0, 1)
            if f == 6 and T["fall"]:                    # the top's far corner falls off
                lvl[fm] -= far[fm] * T["fall"]
            if k == HK and base <= 2:                   # the hero's shadow side: steel down to navy
                ys_ = wy[fm]
                dn = np.clip((ys_.max() - ys_) / max(np.ptp(ys_), 1e-6), 0, 1)
                lvl[fm] -= np.clip((dn - 0.25) / 0.75, 0, 1) ** 1.2 * 0.75
        em = m & edge
        le = lightness(nmean, key, fill)
        lvl[em] = lv_tab[np.searchsorted(cut, le[em], side="right") - 1]
        hot = em & ((nmean @ key_screen) > HOT)        # an edge that faces the key as the picture shows it
        if k != HK:                                     # and a top's upper and left rims, unbroken
            outside = ~m
            rim_ = m & (face == 6) & (ak.shift(outside, 0, 1) | ak.shift(outside, 1, 0))
            hot |= rim_
            flat |= rim_
        lvl[hot] = T["hi"]
        if k == HK:                                     # the hero: no ivory2 seam where cream meets ivory1
            lvl[em & (lvl == 5)] = 6
        flat |= em
        lv_d = lvl - vig
        lv_d[flat] = np.round(lv_d[flat])
        by_level(pic, lv_d, DICE_R, m)
        # pips: black and drilled on the tops (and all over the hero),
        # a step darker than their face on the landed dice's sides
        pos = np.asarray(d["pos"], float)
        for f, (nn_, uu, vv) in FACES.items():
            nw = rot @ np.array(nn_, float)
            if nw @ (cam.pos - pos) <= 0.2:
                continue
            fm = m & (face == f)
            inner = fm & ~edge
            if not inner.any():
                continue
            uw, vw = rot @ np.array(uu, float), rot @ np.array(vv, float)
            fcol = np.bincount(pic.idx[inner], minlength=16).argmax()
            fname = next((nm for nm in DICE_R if pic.pal[nm] == fcol), "steel")
            if f == 6:                                  # the tops: black, drilled
                col, cup, mn = "black", ("steel" if tier != "back" else None), 2
            elif k == HK:                               # the hero's sides: black, on a face wide enough
                col, cup, mn = "black", None, 3
                if not ak.erode(inner, 2).any():
                    continue
            else:                                       # the landed dice's sides: a step darker, quiet
                col = {"ivory2": "steel", "ivory1": "steel", "grey": "steel", "steel": "navy0"}.get(fname, "black")
                cup, mn = None, 2
                if not ak.erode(inner, 2).any():
                    continue
            cp_ = pips(pic, cam, pos, nw, uw, vw, f, inner, size, col, cup, min_px=mn)
            if k == HK and f == 6 and cp_.any():            # the hero's top-left pip catches the key: a cream spark
                cy_, cx_ = np.nonzero(cp_)
                j = np.argmin(cx_ + cy_)
                pic.px(int(cx_[j]), int(cy_[j]), "cream")
        if k == HK:
            hero_face, hero_rank = face, rank

    # outlines: black on each die's shadow side where it meets the felt or
    # the wood, and a black seam where a nearer die overlaps a farther one
    ground = felt_px | wood_px
    for i, d in enumerate(order):
        m = die_mask[d["k"]]
        ring = ak.dilate(m, 1) & ~m
        nearer = np.zeros((128, 128), bool)
        for d2 in order[i + 1:]:
            nearer |= die_mask[d2["k"]]
        Bm = np.apply_along_axis(lambda r: np.convolve(r, [1 / 16, 4 / 16, 6 / 16, 4 / 16, 1 / 16], "same"), 1, m.astype(float))
        Bm = np.apply_along_axis(lambda r: np.convolve(r, [1 / 16, 4 / 16, 6 / 16, 4 / 16, 1 / 16], "same"), 0, Bm)
        gy, gx = np.gradient(Bm)
        shade_side = ring & ((-gx - gy) > 0.02)
        shade_side &= nbrs(shade_side, diag=True)
        if d["k"] == HK:
            pic.put(ring & ground, "navy0")                 # the hero: navy on its lit side
        pic.put(shade_side & ground, "black")
        pic.put(ring & ~nearer & ~ground & ~room & ~m, "black")    # over a farther die

    # the hero's shadow side picks up the felt along its lower edge: a 1 px
    # sea1 rim inside the outline (reflected baize, darker than the steel)
    dark_f = hero_rank[-1]
    dfm = hm & (hero_face == dark_f)
    below = ak.shift(~hm, 0, -1) | ak.shift(~hm, -1, 0)      # the pixel under or right of it is outside
    rim_ = dfm & below & (yy > np.nonzero(dfm)[0].mean())
    pic.put(rim_ & nbrs(rim_, diag=True), BOUNCE)

    # ---- the motion: three speed lines from the hero's trailing corner,
    # curving out to the right (the arc it fell along), thick at the root
    # and tapering, ivory2 to ivory1 to steel, on the felt only
    hm_out = ak.dilate(hm, 1)
    others = np.zeros((128, 128), bool)
    for d in dice:
        others |= ak.dilate(die_mask[d["k"]], 2)
    j_ = max(range(len(hy0)), key=lambda j: hx0[j] * 4 - hy0[j])     # the trailing (right) corner
    vx, vy = int(hx0[j_]), int(hy0[j_])
    ok = felt_px & ~others & ~hm_out & ~ak.dilate(wood_px, 2)       # clear of the dice and the rails' foot
    for (rx, ry), (cx_, cy_), (ex, ey), r0, r1 in STREAKS:
        streak(pic, (vx + rx, vy + ry), (vx + cx_, vy + cy_), (vx + ex, vy + ey), r0, r1, ok)

    # the hero's glint: a four-pointed star on its top corner
    top_row = hy0.min()
    gx0, gy0 = int(hx0[hy0 == top_row].min()) + GLINT[0], int(top_row) + GLINT[1]
    glint(pic, gx0, gy0, 2, arms=GLINT[2])

    # ---- the title: gold leaf (light, a dark horizon band, light again),
    # carved depth from red to mahogany, black outline and shadow, a bevel
    m1 = ak.load_mask(TITLE)
    x1, y1 = ak.centred_x(m1), 4
    M1 = ak.place(m1, x1, y1)
    body, O, layers = extrude(pic, M1, [(0, 1, "red"), (1, 2, "wood0")])
    sh1 = (ak.shift(body | O, 1, 1) | ak.shift(body | O, 1, 2)) & ~(body | O)
    pic.put(sh1, "black")
    pic.put(O, "black")
    for Lm, c in layers:
        if c == "red":                                    # a lip under the feet only: the serifs' undersides go to wood
            lone = Lm & ~(ak.shift(Lm, 1, 0) | ak.shift(Lm, -1, 0))
            pic.put(Lm & (lone | (yy < y1 + 14)), "wood0")
            Lm = Lm & ~lone & (yy >= y1 + 14)
        pic.put(Lm, c)
    gold_face(pic, M1, TITLE_ROWS)
    bevel(pic, M1, "cream", "gold0")
    for dx, dy, c in ((53, 21, "cream"), (63, 18, "gold2")):   # the C: its bowl's bevel, its lower beak's tip
        pic.px(x1 + dx, y1 + dy, c)

    m2 = ak.load_mask(TITLE2)
    x2, y2 = ak.centred_x(m2), 34
    M2 = ak.place(m2, x2, y2)
    body2, O2, layers2 = extrude(pic, M2, [(0, 1, "wood0")])
    pic.put((ak.shift(body2 | O2, 1, 1)) & ~(body2 | O2), "black")
    pic.put(O2, "black")
    for Lm, c in layers2:
        pic.put(Lm, c)
    gold_face(pic, M2, ["gold2"] * 4 + [("gold2", "gold1")] + ["gold1"] * 5 + [("gold1", "gold0")] + ["gold0"] * 2)
    bevel(pic, M2, "cream", "gold0")
    for dy in (3, 9):                                     # the D's dark right bevel, unbroken
        pic.px(x2 + 10, y2 + dy, "gold0")
    for dx, dy, c in ((20, 1, "black"), (28, 4, "black"), (11, 9, "black"), (50, 10, "gold0")):
        pic.px(x2 + dx, y2 + dy, c)                       # lone depth pixels and the E's serif tip
    ry2 = y2 + 6                                          # the cove stripes, a diamond inboard
    w2 = m2.shape[1]
    for xa, xb_, xd in ((10, x2 - 7, x2 - 5), (x2 + w2 + 7, 117, x2 + w2 + 4)):
        line = np.zeros((128, 128), bool)
        line[ry2:ry2 + 2, xa:xb_] = True
        dia = np.zeros((128, 128), bool)
        dia[ry2 - 1:ry2 + 3, xd] = True
        dia[ry2:ry2 + 2, xd - 1:xd + 2] = True
        ak.outline(pic, line | dia, "black")
        pic.put(line, "gold0")
        pic.put(line & ~ak.shift(line, 0, 1), "gold2")
        pic.put(dia, "gold1")
        pic.px(xd, ry2 - 1, "cream")
        pic.px(xd - 1, ry2, "gold2")
    # pinholes of room shut in by the outlines go black
    blk = pic.where("black")
    hole = ~blk & ak.shift(blk, 1, 0) & ak.shift(blk, -1, 0) & ak.shift(blk, 0, 1) & ak.shift(blk, 0, -1)
    hole[RAIL:, :] = False
    pic.put(hole & pic.where("navy0"), "black")

    # the title's glint: the A's apex
    glint(pic, x1 + 32, y1 + 1, 2, tip="gold2", arms=(3, 3, 3, 2))
    return pic.image()


def title_lines():
    """The title's lettering as drawn here, and its depth, for the title
    screen (tools/titleart.py: the game paints it in the house gold).
    YACHT only: DICE has no room under it there, the game sets it small."""
    return [dict(mask=ak.load_mask(TITLE), depth=2, side="wine")]


if __name__ == "__main__":
    import boxart
    boxart.save(draw(), HERE.parent / "docs" / "cart.png")
