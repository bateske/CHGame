"""docs/cart.png, Word Wheel's cover in the visual menu (docs/cover-art.md).
`chgame boxart` redraws it; edit this, not the PNG.

THE BRIEF
Message: spin it! The dealer's white glove has just flung the big wheel;
it whirs up past the pointer, the bulbs blaze round its rim, the pointer
is knocked aside with a clack, and across the wheel's lit top the wedges
spell it out: S P I | N I T. Which letter will it stop on?

Composition (a thumbnail in words):
- The title fills the top band (y 3-51), two stacked lines of heavy
  rounded capitals on calm black, ringed by a thin navy halo that hugs
  them and runs as a straight rail under WHEEL: the first read. Nothing
  else on the cover is gold.
- Under it, the pointer: a red rubber wedge, faceted (its left face to the
  lamp with a cream edge, its right face wine), pivoting on a chrome cap
  on a bar that comes down from behind the title. Its point is knocked to
  the right by the peg going by, a clack star where they meet, its shadow
  cast down right on the wedges.
- The wheel fills the lower 60%, face on, a little right of centre, and
  breaks the frame right and below (the hub is the chrome dome on the
  bottom edge). Face on keeps the letters crisp: twenty wedges, so the
  six across the top lean 9, 27 and 45 degrees, angles that step evenly.
  Its thickness shows as a lit chrome band down its left side (the face
  drawn over its back, set 8 px left: an oblique view).
- Six letters on the six wedges under the lamp, S P I | N I T, the pointer
  between the I and the N: a heavy rounded face drawn as shapes in the
  wheel's own frame (counters open, 2 px clear of every groove), cream
  with a grey side. The other wedges carry no letters: the lower wheel is
  one calm dark mass.
- The dealer's glove (the casino's white cartoon glove) at the left edge,
  fingers spread on the rim's lit side: the hand that spun it. A tapered
  speed arc runs off its fingertips up round the rim; another trails the
  right side, each swelling from a point to a sky head.
- Light: the house key from the top left. Each wedge is a raised panel
  (black grooves, a whole step darker on its lower right edge) in flat
  plateaus: S and P lit to near the hub, I and N a step less, I and T in
  their shade colour below a lit cap, the wedges past them dark; every
  seam is a clean arc round the hub (no dither on the face). The rim's lip
  shades a crescent inside its upper left.
- The rim: chrome beads each side of a dark track, lit on the upper left
  (a cream crest on the outer bead, sky on the inner) and falling to navy
  and night on the right. In the track a bulb per wedge in the rainbow
  colour (palette 15: under the Rainbow bootloader they cycle like marquee
  lights), each with a cream filament and a blue glow; two flare. Chrome
  studs (pegs) at the wedges' outer corners.
- Behind: a stage curtain in wide even folds (16 px) of night and navy,
  rising out of the dark, kept clear of the title; the wheel casts its
  shadow on it to the right. The frame's edges step down to black.
- Depth: the title in front, the pointer, the glove, the wheel and its
  side band, the curtain.

Palette (11 own + cream, grey, black, red, and the rainbow):
- night navy blue sky .. the stage, the curtain, the halo; chrome (with
                         black and cream); the blue and purple wedges'
                         shade; the speed arcs; the glove's wrist.
- wine ................. the red wedges' shade, the pointer's shade side,
                         the dealer's sleeve, the title's extrusion.
- green0 green1 ........ the green wedges (felt green, the casino's accent).
- purple ............... the purple wedges.
- gold0 gold1 gold2 .... the title's own: nothing else uses them.
- fixed: cream (letters, glints, filaments, the glove), grey (the letters'
  sides, the glove's shade), black (outlines, grooves, the void), red
  (wedges, the pointer), rainbow (the bulbs).

How it is painted: the wheel is analytic (face on, every pixel's angle and
radius in the wheel's own units); each surface is painted on the pixels as
levels of a ramp in flat plateaus. The letters are signed-distance shapes
sampled 4x4 a pixel in each wedge's frame. Crisp lines (grooves, crests)
are rasterised from the wheel's own circles; the glove is modelled in 3D
(artkit.render3d) and painted in cel bands.

Font: Bent 3 round by crs/broncs (bmf collection), at its own size, for
the title (tools/art/title.txt). Terms: freeware, authors vary, few gave
terms (a `?` face, chosen because no clear-terms face this heavy and round
stacks the two words at a size that fills the band). The wedges' letters
are drawn here, after its look; no font.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import numpy as np  # noqa: E402
import artkit as ak  # noqa: E402

TITLE = HERE / "art" / "title.txt"
TITLE_Y = 3

PAL = {
    "night": "#0A0C2C", "navy": "#1E2A7A", "blue": "#3A70E8", "sky": "#9CD4FF",
    "wine": "#600C2C", "green0": "#0A5A30", "green1": "#30B04A", "purple": "#8A2EC8",
    "gold0": "#9A4A08", "gold1": "#F0A818", "gold2": "#FFEA80",
}
CHROME = ["black", "night", "navy", "blue", "sky", "cream"]

YY, XX = np.mgrid[0:128, 0:128]
TAU = 2 * np.pi
D = np.radians

# ---- the wheel, face on: picture px = hub + S * (x, -y) in the wheel's own units ---------------
HX, HY = 71.0, 132.0                          # the hub's centre on the picture
S = 70.0                                      # px a unit
NW = 20                                       # wedges: the letters lean 9, 27 and 45 degrees,
SECTOR = TAU / NW                             # angles that step evenly in pixels
LETTERS = "NITRAEDOHLCMBGUKWSPI"              # clockwise from the clicker: across the top, S P I | N I T
WEDGE = [("navy", "blue"), ("wine", "red"), ("green0", "green1"), ("navy", "purple")]   # shade, body
R_FACE, R_IN, R_OUT, R_RIM = 0.935, 0.975, 1.035, 1.08   # the face's edge, the track, the rim's edge
R_PEG = 0.905
R_LET, H_LET = 0.725, 0.19                    # the letters' centre radius and height
R_HUB = 0.19
DRUM = (-8.0, 2.0)                            # where the wheel's back lies (px): its lit side shows on the left
GLOVE = dict(at=(7.0, 99.0), px=8.5, roll=-16.0, turn=-25.0, tilt=-18.0)   # the palm's centre, px a unit, turned, tipped
R_GROOVE = (0.30, 0.93)
FLARES = (18, 1)                              # the bulbs that flare (their wedge's number)
# the lamp's pool, wedge by wedge (its middle's angle): the radius where the
# body steps down to the shade, and where the shade steps down to black
LIGHT_AT = [-180, -135, -117, -99, -81, -63, -45, -27, -9, 9, 27, 45, 63, 81, 99, 180]
LIGHT_R1 = [1.0, 1.0, 1.0, 1.0, 1.0, 0.80, 0.42, 0.40, 0.46, 0.55, 0.68, 0.80, 0.98, 1.0, 1.0, 1.0]
LIGHT_R2 = [1.0, 1.0, 1.0, 0.9, 0.86, 0.55, 0.235, 0.235, 0.235, 0.26, 0.34, 0.46, 0.66, 0.86, 0.9, 1.0]


def polar(a, r):
    """The picture point at angle a (radians from straight up, clockwise) and radius r."""
    return HX + S * r * np.sin(a), HY - S * r * np.cos(a)


def wheel_xy(ss=1):
    """The wheel's own coordinates (x right, y up) at each sample's centre."""
    c = (np.arange(128 * ss) + 0.5) / ss
    X, Y = np.meshgrid(c, c)
    return (X - HX) / S, (HY - Y) / S


def angle_of(lx, ly):
    """Clockwise from straight up, -pi..pi."""
    return np.arctan2(lx, ly)


def wedge_of(lx, ly):
    return np.floor(np.mod(angle_of(lx, ly), TAU) / SECTOR).astype(np.int64) % NW


def centre_deg(j):
    return (np.degrees((j + 0.5) * SECTOR) + 180) % 360 - 180


# ---- the letters: a heavy rounded face drawn as shapes on a 9 x 13 grid, so that they
# turn with their wedge without losing their steps -------------------------------------------

def rbox(gx, gy, x0, y0, x1, y1, r=0.0):
    cx, cy, hx, hy = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 - r, (y1 - y0) / 2 - r
    qx, qy = np.abs(gx - cx) - hx, np.abs(gy - cy) - hy
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r


def seg(gx, gy, ax, ay, bx, by, w):
    dx, dy = bx - ax, by - ay
    t = np.clip(((gx - ax) * dx + (gy - ay) * dy) / (dx * dx + dy * dy), 0, 1)
    return np.hypot(gx - ax - t * dx, gy - ay - t * dy) - w / 2


def glyph(ch, gx, gy):
    """The signed distance to a letter (design units, 9 wide, 13 tall, y down)."""
    b = lambda *a: rbox(gx, gy, *a)              # noqa: E731
    if ch == "I":
        return b(3, 0, 6, 13, 0.5)
    if ch == "T":
        return np.minimum(b(0, 0, 9, 3, 0.5), b(3, 0, 6, 13, 0.5))
    if ch == "N":
        d = np.minimum(b(0, 0, 3, 13, 0.5), b(6, 0, 9, 13, 0.5))
        diag = np.maximum(seg(gx, gy, 1.4, 1.2, 7.6, 11.8, 3.3), b(0, 0, 9, 13))
        return np.minimum(d, diag)
    if ch == "P":
        bowl = np.maximum(b(0, 0, 9, 8.2, 2.4), -b(3, 2.7, 6.2, 5.5, 0.3))
        return np.minimum(b(0, 0, 3, 13, 0.5), bowl)
    if ch == "S":
        parts = [b(0, 0, 9, 3, 1.2), b(0, 0, 3, 8, 1.2), b(0, 5, 9, 8, 1.2), b(6, 5, 9, 13, 1.2), b(0, 10, 9, 13, 1.2)]
        return np.minimum.reduce(parts)
    return np.full(gx.shape, 9.0)


def letter_masks(which, ss=4):
    """Each wedge's letter (only the wedges in `which`) on the picture: the
    pixels at least half covered. Returns {wedge: mask}."""
    lx, ly = wheel_xy(ss)
    out = {}
    u = H_LET / 13.0
    for j in which:
        a = (j + 0.5) * SECTOR
        up = np.array([np.sin(a), np.cos(a)])
        rt = np.array([np.cos(a), -np.sin(a)])
        s = (lx - up[0] * R_LET) * rt[0] + (ly - up[1] * R_LET) * rt[1]
        t = (lx - up[0] * R_LET) * up[0] + (ly - up[1] * R_LET) * up[1]
        d = glyph(LETTERS[j], s / u + 4.5, -t / u + 6.5)
        out[j] = ak.px_mean((d < 0).astype(np.float32), ss) >= 0.5
    return out


def swoosh(pts, widths, ss=4):
    """A tapered stroke along points: the half-width at each point (px)."""
    c = (np.arange(128 * ss) + 0.5) / ss
    X, Y = np.meshgrid(c, c)
    d = np.full(X.shape, 1e9, np.float32)
    for (x0, y0), (x1, y1), w0, w1 in zip(pts, pts[1:], widths, widths[1:]):
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy or 1.0
        t = np.clip(((X - x0) * dx + (Y - y0) * dy) / L2, 0, 1)
        d = np.minimum(d, np.hypot(X - x0 - t * dx, Y - y0 - t * dy) - (w0 + (w1 - w0) * t))
    return ak.px_mean((d < 0).astype(np.float32), ss) >= 0.5


def arc_pts(r, a0, a1, n=60):
    return [polar(D(a), r) for a in np.linspace(a0, a1, n)]


# ---- the clicker -----------------------------------------------------------------------------
CAP = (70.5, 58.5)                            # the chrome cap it pivots on
FLAP = [(62.8, 57.2), (78.2, 57.2), (75.0, 73.4)]   # the pointer: top left, top right, its point (knocked right)


def clicker():
    """The pointer: a red rubber wedge, faceted (its left face to the lamp,
    its right face in shade), its point knocked to the right by the peg
    going by, pivoting on a chrome cap carried by a bar out from behind the
    title. Returns (pointer, left face, cap, bar)."""
    ss = 4
    c = (np.arange(128 * ss) + 0.5) / ss
    X, Y = np.meshgrid(c, c)
    (ax_, ay_), (bx, by), (tx_, ty_) = FLAP

    def side(p, q):
        return (q[0] - p[0]) * (Y - p[1]) - (q[1] - p[1]) * (X - p[0])
    inside = (side((ax_, ay_), (tx_, ty_)) < 0) & (side((tx_, ty_), (bx, by)) < 0) & (Y > ay_)
    flap = ak.px_mean(inside.astype(np.float32), ss) >= 0.5
    mid = (ax_ + 0.68 * (bx - ax_), ay_)                         # the ridge: two thirds lit
    left = ak.px_mean((inside & (side(mid, (tx_, ty_)) > 0)).astype(np.float32), ss) >= 0.5
    cap = ((XX + 0.5 - CAP[0]) ** 2 + (YY + 0.5 - CAP[1]) ** 2) <= 3.0 ** 2
    bar = (XX >= int(CAP[0]) - 2) & (XX <= int(CAP[0]) + 1) & (YY >= 46) & (YY <= int(CAP[1]))
    return flap, left & flap, cap, bar


def comet(r, a0, a1, w, ss=4):
    """A speed arc round the wheel from its tail (a0) to its head (a1): it
    swells from a point to a rounded head. Returns (mask, t along it)."""
    pts = arc_pts(r, a0, a1, 40)
    n = len(pts) - 1
    wid = [w * (0.15 + 0.85 * min(i / n / 0.78, 1.0) ** 0.9) * (1.0 if i / n < 0.78 else 1 - 0.55 * (i / n - 0.78) / 0.22)
           for i in range(n + 1)]
    mk = swoosh(pts, wid, ss)
    ang = np.degrees(angle_of((XX + 0.5 - HX) / S, (HY - YY - 0.5) / S))
    t = np.clip((ang - a0) / (a1 - a0), 0, 1)
    return mk, t


def glove(pic):
    """The dealer's white glove, the hand that has just flung the wheel: the
    back of the hand to us, three fat fingers and the thumb spread, up along
    the rim, a flared cuff and his wine jacket's sleeve off the corner.
    Modelled in 3D, painted in flat cel bands (cream to the lamp, grey away
    from it, navy where it sinks into the corner), black creases where one
    part lies on another, a black outline. Returns its mask."""
    from artkit import render3d as R
    G = GLOVE
    parts = [R.prim(R.box((1.0, 0.95, 0.42), 0.45), 0),                                    # the back of the hand
             R.prim(R.capsule((-0.66, 0.6, 0.05), (-1.12, 2.0, 0.14), 0.42), 1),
             R.prim(R.capsule((0.0, 0.7, 0.08), (0.02, 2.35, 0.16), 0.44), 2),
             R.prim(R.capsule((0.66, 0.6, 0.05), (1.14, 1.9, 0.14), 0.42), 3),
             R.prim(R.capsule((-0.95, -0.35, 0.2), (-1.85, 0.55, 0.34), 0.38), 4),              # the thumb
             R.xf(R.prim(R.cylinder(1.2, 0.34, 0.14), 5), (0, -1.32, 0)),                    # the glove's cuff
             R.xf(R.prim(R.cylinder(1.06, 1.8, 0.2), 6), (0, -3.4, 0))]                      # the sleeve
    rot = R.rot_z(G["roll"]) @ R.rot_y(G["turn"]) @ R.rot_x(G["tilt"])
    scene = R.xf(R.U(*parts), (0, 0, 0), rot)
    cam = R.Camera((0, 0, 20), (0, 0, 0), ortho=128.0 / G["px"], shift=(G["at"][0] - 64, G["at"][1] - 64))
    cv = ak.Canvas("#000000")
    out = R.render(cv, scene, cam, [R.Mat("#FFFFFF")] * 7, region=(0, 64, 48, 128), ss=2, shadows=False, ao=False)
    m = R.majority(out, cv.s)
    allm = m >= 0
    s_ = cv.s
    n = out["normal"].reshape(128, s_, 128, s_, 3).mean(axis=(1, 3))
    n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-6)
    z = np.where(np.isfinite(out["depth"]), out["depth"], 1e9).reshape(128, s_, 128, s_).min(axis=(1, 3))
    Ld = np.array([-0.55, 0.75, 0.45])
    Ld /= np.linalg.norm(Ld)
    dif = np.clip(n @ Ld, 0, 1)
    white = allm & (m < 6)
    sleeve = m == 6
    lv = 1.5 + 2.0 * dif - np.clip((YY - 108.0) / 10.0, 0, 1) * 0.7          # sinking into the dark corner
    lv = np.where(m == 5, np.minimum(lv, 2.4), lv)                         # the cuff a step under the hand
    ak.by_level(pic, np.clip(np.floor(lv), 2, 3) - (YY > 112), ["black", "navy", "grey", "cream"], white, q=1)
    ak.by_level(pic, np.clip(np.floor(1.6 + 1.2 * dif - np.clip((YY - 114.0) / 8.0, 0, 1)), 0, 2), ["black", "wine", "red"], sleeve, q=1)
    crease = np.zeros_like(allm)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        mo = np.roll(np.roll(m, dy, 0), dx, 1)
        zo = np.roll(np.roll(z, dy, 0), dx, 1)
        crease |= allm & (mo >= 0) & (mo != m) & (zo < z - 0.02)
    crease &= ak.paint.nbrs(crease, diag=True)
    pic.put(crease & white, "black")
    pic.put(crease & sleeve, "black")
    pic.put(ak.dilate(allm, 1) & ~allm, "black")
    ak.despeckle(pic, need=4, within=ak.erode(allm, 1), passes=2)
    return allm


def draw():
    P = ak.Palette(PAL, ramps=[["black", "wine", "red"], CHROME, ["black", "green0", "green1"],
                               ["navy", "purple"], ["gold0", "gold1", "gold2", "cream"]])
    pic = ak.Picture.blank(P, "black")
    lx, ly = wheel_xy()
    rr = np.hypot(lx, ly)
    ang = np.degrees(angle_of(lx, ly))
    wheel = rr <= R_RIM
    face = rr < R_FACE
    rim = wheel & ~face
    bx_, by_ = (XX + 0.5 - HX - DRUM[0]) / S, (HY + DRUM[1] - YY - 0.5) / S
    drum = (np.hypot(bx_, by_) <= R_RIM) & ~wheel
    solid = wheel | drum
    k = wedge_of(lx, ly)

    # the title's footprint (everything it will draw), for the halo behind it
    m = ak.load_mask(TITLE)
    tx = ak.centred_x(m)
    M = ak.place(m, tx, TITLE_Y)
    TF = M.copy()
    for k_ in range(1, 4):
        TF |= ak.shift(M, k_, k_)
    TF = ak.dilate(TF, 1)
    TF |= ak.shift(TF, 1, 2) | ak.shift(TF, 1, 1)
    ys_, xs_ = np.nonzero(TF)
    yb = ys_.max()
    xb = xs_[ys_ >= yb - 2]
    TF |= (YY >= yb - 4) & (YY <= yb) & (XX >= xb.min()) & (XX <= xb.max())   # a straight rail under WHEEL
    dt = ak.distance_px(TF, 8)

    # ---- the stage: a curtain in wide even folds, lit from the front, rising
    # out of the dark; calm round the title
    fold = np.abs(((XX + 5) % 16) - 7.5) / 7.5                     # 0 at a crest, 1 in a trough
    rise = np.clip((YY - 56) / 30.0, 0, 1) * np.clip((np.minimum(XX, 127 - XX) - 2) / 16.0, 0.3, 1)
    cur = (1.0 - fold) * 1.9 * rise + 0.7 * np.clip((YY - 50) / 20.0, 0, 1)
    cur *= np.clip((dt - 5) / 4.0, 0, 1)
    ak.by_level(pic, np.clip(cur, 0, 2), ["black", "night", "navy"], ~solid, q=1)
    pic.put(ak.shift(solid, 5, 3) & ~solid, "black")             # the wheel's shadow on the curtain
    pic.put(~solid & (dt <= 1) & (YY > 2), "navy")
    pic.put(~solid & (dt == 2) & (YY > 2), "night")
    pic.put(TF, "black")                                          # behind the title: calm black

    # ---- the face: the lamp's pool on the upper left; each wedge falls off
    # like a drum toward the hub in two flat steps, seams following the rim
    ac = np.array([centre_deg(j) for j in range(NW)])
    r1 = np.interp(ac, LIGHT_AT, LIGHT_R1)                      # body to shade
    r2 = np.interp(ac, LIGHT_AT, LIGHT_R2)                      # shade to black
    L = 2.0 - (rr < r1[k]) - (rr < r2[k])                         # clean arcs, no dither
    # the rim's lip shades a crescent inside its upper left
    lip = (rr > R_FACE - 0.035) & (ang > -110) & (ang < 25)
    L = np.where(lip, np.minimum(L, 1.0), L)
    # the grooves between the wedges: clean 1 px lines from the hub out
    groove = np.zeros((128, 128), bool)
    for j in range(NW):
        for x_, y_ in ak.paint.line_px([polar(j * SECTOR, r_) for r_ in np.linspace(R_GROOVE[0], R_GROOVE[1], 40)]):
            if 0 <= x_ < 128 and 0 <= y_ < 128:
                groove[y_, x_] = True
    groove &= face
    # each wedge a raised panel: a whole step darker where its edge faces
    # down or right, onto a groove
    bev = face & ~groove & (ak.shift(groove, -1, 0) | ak.shift(groove, 0, -1))
    Lf = np.where(bev, np.floor(L) - 1, L)
    kc = k % 4
    for j, (sh, body) in enumerate(WEDGE):
        ak.by_level(pic, np.clip(Lf, 0, 2), ["black", sh, body], face & (kc == j), q=4)
    pic.put(groove, "black")

    # ---- the letters: S P I | N I T across the top
    lit6 = [17, 18, 19, 0, 1, 2]
    LM = letter_masks(lit6)
    let = np.zeros((128, 128), bool)
    for j in lit6:
        let |= LM[j]
    for j in lit6:
        Wj = face & (k == j)
        side = ak.shift(LM[j], 1, 1) & ~let & Wj & ak.outside_of(LM[j])
        side &= ak.paint.nbrs(side, diag=True)                     # no lone side pixels
        pic.put(side, "grey" if np.abs(ac[j] + 35) < 60 else "black")
    pic.put(let, "cream")

    # ---- the wheel's thickness: its chrome side, lit where it faces the lamp
    ab = np.degrees(np.arctan2(bx_, by_))
    nb = np.stack([np.sin(D(ab)), np.cos(D(ab))], -1)
    lb = nb @ (np.array([-0.55, 0.75]) / np.linalg.norm([-0.55, 0.75]))
    ak.by_level(pic, np.select([lb > 0.93, lb > 0.6, lb > 0.25], [4.0, 3.0, 2.0], 1.0), CHROME, drum, q=1)
    pic.put(ak.dilate(drum, 1) & ~solid & (XX < HX), "black")              # its far edge
    pic.put(drum & ak.dilate(wheel, 1), "black")                           # the seam at the face's edge
    # ---- the rim: a chrome bead each side of a dark track for the bulbs,
    # lit on the upper left, falling to navy and night on the right
    a_r = D(ang)
    nx_, ny_ = np.sin(a_r), np.cos(a_r)                          # outward, on the picture (y up)
    KEY2 = np.array([-0.55, 0.75])
    KEY2 = KEY2 / np.linalg.norm(KEY2)
    out_lit = nx_ * KEY2[0] + ny_ * KEY2[1]                      # an outward-facing slope's light
    dim = np.clip(np.abs(ang + 40) / 130.0, 0, 1)
    bead_in = rim & (rr < R_IN)
    track = rim & (rr >= R_IN) & (rr < R_OUT)
    bead_out = rim & (rr >= R_OUT)
    for bead, c, hw in ((bead_in, (R_FACE + R_IN) / 2, (R_IN - R_FACE) / 2), (bead_out, (R_OUT + R_RIM) / 2, (R_RIM - R_OUT) / 2)):
        nr = np.clip((rr - c) / hw, -1, 1)                       # across the bead: -1 inside, 1 outside
        lv = 3.0 + 1.7 * nr * out_lit - 2.6 * dim
        ak.by_level(pic, np.clip(lv, 1, 5), CHROME, bead, q=1)
    pic.put(track, "night")
    pic.put(track & (dim > 0.6), "black")
    # the lamp caught along both beads on the upper left: crisp crests
    for r_, a0, a1, cols in ((R_RIM - 0.012, -66, -18, [("sky", 0.22), ("cream", 0.75), ("sky", 1.0)]),
                             (R_IN - 0.006, -58, -30, [("sky", 1.0)])):
        ak.ink(pic, arc_pts(r_, a0, a1, 300), None, where=rim, colours=cols)

    # ---- the bulbs in the track, in the rainbow colour, a cream filament; each
    # lights the track round it
    bulb_at = []
    for b in range(NW):
        a = (b + 0.5) * SECTOR
        x_, y_ = polar(a, (R_IN + R_OUT) / 2)
        bulb_at.append((int(np.floor(x_)), int(np.floor(y_)), a))
    for xi, yi, a in bulb_at:
        dd = np.hypot(XX - xi, YY - yi)
        pic.put(track & (dd <= 4.2), "navy")
        pic.put(track & (dd <= 3.3), "blue")
    hand0 = glove(ak.Picture.blank(P, "black"))                   # where the glove will be
    bulbs_all = bulb_at
    bulb_at = [(xi, yi, a) for xi, yi, a in bulb_at if not ak.dilate(hand0, 2)[min(max(yi, 0), 127), min(max(xi, 0), 127)]]
    for xi, yi, a in bulb_at:
        ak.patch(pic, xi - 2, yi - 2, [".bbb.", "bcbbb", "bbbbb", "bbbbb", ".bbb."], {"b": "rainbow", "c": "cream"})

    # ---- the pegs at the wedges' outer corners: chrome studs, a shadow down right
    for j in range(NW):
        x_, y_ = polar(j * SECTOR, R_PEG)
        xi, yi = int(np.floor(x_)), int(np.floor(y_))
        ak.patch(pic, xi - 1, yi - 1, ["cs.", "ssk", ".kk"], {"c": "cream", "s": "sky", "k": "black"})

    # ---- the hub: a chrome boss, its shadow cast down right
    hub = rr <= R_HUB
    hsh = (np.hypot(lx - 0.04, ly + 0.04) <= R_HUB) & ~hub
    pic.put(hsh & face, "black")
    hx_, hy_ = lx / R_HUB, ly / R_HUB
    hz = np.sqrt(np.clip(1 - hx_ ** 2 - hy_ ** 2, 0, 1))
    hl = (-0.55 * hx_ + 0.75 * hy_ + 0.45 * hz) / np.linalg.norm([0.55, 0.75, 0.45])
    lvh = np.where(hy_ > 0.25, 2.6, 1.2) + 1.2 * hl
    lvh = np.where(hl > 0.95, 5, lvh)
    ak.by_level(pic, np.clip(lvh, 1, 5), CHROME, hub, q=1)
    pic.put(ak.dilate(hub, 1) & ~hub & (rr > R_HUB), "black")

    # ---- the dealer's glove at the lower left: it has just flung the wheel
    hand = glove(pic)

    # ---- speed arcs round the rim, a point swelling to a head where the rim is going
    clear = ~solid & ~ak.dilate(solid | hand, 2) & (dt >= 3) & (XX >= 2) & (XX <= 125)
    for r_, a0, a1, w in ((1.25, -54, -28, 1.8), (1.15, 21, 41, 1.6)):
        mk, t = comet(r_, a0, a1, w)
        mk &= clear
        pic.put(mk, "navy")
        pic.put(mk & (t > 0.35), "blue")
        pic.put(mk & (t > 0.72), "sky")

    # ---- the clicker: a chrome bar out from behind the title, a cap, a red
    # rubber pointer knocked right by the peg going by
    flap, fleft, cap, bar = clicker()
    allc = flap | cap | bar
    shadow = (ak.shift(allc, 2, 2) | ak.shift(allc, 3, 2)) & ~allc
    pic.put(shadow & wheel, "black")
    pic.put(ak.dilate(allc, 1, diag=True) & ~allc, "black")
    pic.put(bar, "blue")
    pic.put(bar & (XX == int(CAP[0]) - 2), "sky")
    pic.put(bar & (XX == int(CAP[0]) + 1), "navy")
    pic.put(flap, "wine")
    pic.put(fleft, "red")
    edge_l = fleft & ~ak.shift(fleft, 1, 0) & (YY > CAP[1] + 2) & (YY < CAP[1] + 9)
    pic.put(ak.shift(edge_l, 1, 0) & fleft, "cream")             # the lamp along its left edge
    cx_, cy_ = int(CAP[0]), int(CAP[1])
    ak.patch(pic, cx_ - 3, cy_ - 3, [".kkkk.", "kbsbnk", "ksccnk", "kbsbnk", "knbnnk", ".kkkk."],
             {"k": "black", "c": "cream", "s": "sky", "b": "blue", "n": "navy"})
    # the clack: a star where the peg strikes it
    px_, py_ = polar(0.0, R_PEG)
    sx_, sy_ = int(np.floor(px_)) - 3, int(np.floor(py_))
    ak.glint(pic, sx_, sy_, arms=(2, 0, 2, 2), tip="sky")

    # ---- lone pixels (the bulbs, the pegs, the letters, the glints and the
    # pointer kept), then two bulbs flare
    keep = ak.dilate(let | flap | cap | hand, 1, diag=True)
    for xi, yi, a in bulb_at:
        keep[max(yi - 2, 0):yi + 3, max(xi - 2, 0):xi + 3] = True
    for j in range(NW):
        x_, y_ = polar(j * SECTOR, R_PEG)
        keep[int(y_) - 1:int(y_) + 2, int(x_) - 1:int(x_) + 2] = True
    keep[int(py_) - 3:int(py_) + 3, int(px_) - 6:int(px_) + 1] = True
    ak.despeckle(pic, 4, keep=keep, within=(YY > 50) & (dt >= 2), passes=2)
    ak.despeckle(pic, 4, within=hand | hub, passes=2)
    for b in FLARES:
        xi, yi, a = bulbs_all[b]
        for (dx_, dy_) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            for k_ in (3, 4):
                x_, y_ = xi + dx_ * k_, yi + dy_ * k_
                if 0 <= x_ < 128 and 0 <= y_ < 128 and dt[y_, x_] >= 2 and not let[y_, x_]:
                    pic.px(x_, y_, "cream" if k_ == 3 else "sky")

    # ---- the frame's edges, where the menu's border sits
    DARKER = {"cream": "grey", "grey": "navy", "sky": "blue", "blue": "navy", "navy": "night", "night": "black",
              "red": "wine", "wine": "black", "green1": "green0", "green0": "black", "purple": "navy",
              "rainbow": "rainbow"}
    edge = np.minimum(np.minimum(XX, 127 - XX), 127 - YY)
    for ring_, steps in ((1, 2), (2, 1)):
        for _ in range(steps):
            before = pic.idx.copy()
            for nm, dk in DARKER.items():
                pic.put((edge == ring_) & (before == P[nm]), dk)
    pic.put(edge == 0, "black")

    # ---- the title: gold chrome (a bright sky, a dark horizon, its
    # reflection, the ground) in crisp bands, cream and gold0 bevel, a wine
    # extrusion, black outline and shadow
    line = ["gold2"] * 8 + ["gold1"] * 2 + ["gold0"] + ["gold2"] * 2 + ["gold1"] * 8
    rows = line + ["gold1"] * 2 + line
    drawn = ak.title(pic, m, tx, TITLE_Y, fill=None, rows=rows, hi=None, lo=None,
                     extrude=dict(dx=1, dy=1, depth=3, colours=["gold0", "wine", "wine"]),
                     shadow=dict(dx=1, dy=2, colour="black"))
    F = drawn["face"]
    A = drawn["all"]
    inside = ~ak.outside_of(A) & ~A
    pic.put(inside, "black")
    Lh = ak.shift(A, 1, 0) | ak.shift(A, 2, 0) | ak.shift(A, 3, 0)
    Rh = ak.shift(A, -1, 0) | ak.shift(A, -2, 0) | ak.shift(A, -3, 0)
    pic.put(Lh & Rh & ~A & (YY <= TITLE_Y + 47), "black")
    ak.bevel_contour(pic, drawn["face"], "cream", "gold0")
    ak.despeckle(pic, 3, within=ak.dilate(A, 1, diag=True), passes=2)
    ys, xs = np.nonzero(F[:TITLE_Y + 21])
    gx = int(xs[ys == ys.min()].min())
    ak.glint(pic, gx, int(ys.min()), arms=(2, 2, 1, 2))
    ys, xs = np.nonzero(F[TITLE_Y + 22:])
    top2 = int(ys.min()) + TITLE_Y + 22
    gx = int(xs[ys == ys.min()].max())
    ak.glint(pic, gx, top2, arms=(2, 2, 1, 2))
    return pic.image()


if __name__ == "__main__":
    import boxart
    print(boxart.save(draw(), HERE.parent / "docs" / "cart.png"))
