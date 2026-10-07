"""docs/cart.png, CHRoulette's cover in the visual menu (docs/cover-art.md).
`chgame boxart` redraws it; edit this, not the PNG.

THE BRIEF
Message: round and round she goes. The moment after "no more bets": the
rotor is a blur of red and black, the ivory ball sails over the pockets,
the chrome is hot, the lacquer gleams, and a chip is still in the air. It
says ROULETTE before it says anything else: the wheel, the ball, the chip.

Composition (a thumbnail in words):
- Camera low and close over the near rim, a wide lens, rolled 8 degrees (a
  Dutch angle: the whip of the game's own camera move). The wheel fills the
  lower two thirds and breaks the frame left, right and below.
- Focal point: the ball, lower left on the thirds, over the near pockets:
  a pearl lit up left (a rounded cream hot spot, steel at its terminator,
  grey in its core, red thrown up from the ring on its lower right edge),
  a cream glint where its edge catches the lamp, the pockets round it a
  step darker (wine) so it snaps. Three speed lines of unequal length run
  back along its orbit, pearl to steel to grey, each with a wine channel
  either side so they read on the red; its shadow, a wine ellipse with a
  black core, lies parted from it below right: it is in the air.
- The counterweight, lower right: a green chip flicked up past the camera,
  tilted to show its face (cream edge spots, a cream inlay, a dark ring),
  outlined in black, short speed lines behind it. Green on red: the
  complementary pair makes it pop without competing with the ball.
- The spin: a smear frame. Pockets alternate red and black; each red pocket
  keeps its body and trails streaks of differing length into the black one
  behind it (the far ends wine), in fine lanes, so the red/black identity
  holds even blurred. On the near arc the frets are crisp steel lines (grey
  at their feet); a wine step parts the number ring from the pockets; the
  zero goes past as a green streak.
- The cone is a lacquered DOME: lit up left by the key, a crisp crescent of
  gloss (wood2, a cream core) just in front of and left of the bell, a wide
  wood1 to wood0 fall to its rim, six lacquer streaks spiralling out with
  the spin, the ring mirrored in wine and red along its near rim. Round it
  the rotor's chrome band, a pixel-perfect ellipse: steel, pearl and two
  cream pings where the lamp catches it, steel over grey (2 px) on the near
  arc for the rim's thickness.
- The bowl is dark lacquered mahogany in flat bands (hard seams where the
  bands are thin, 50% checkers only in the wide parts), with crisp gleams:
  a continuous crest along the lip from the near left round the far side to
  the right edge (cream at its peak, 2 px nearest the light, wood2, wood1),
  sheen arcs on the ball track (cream cores on the left, wood2 on the far
  right).
- The chrome turret stands against the lit felt: each arm a tube drawn
  across its own axis (a pearl sky, steel, a hard black horizon, grey
  ground) and each knob a chrome ball (sky, a curved black horizon, grey
  ground, a steel rim of bounced light, a cream ping up left); the spindle,
  the bell's neck and the slim finial as upright chrome (a pearl streak
  left, black right), a star on the finial's tip; the bell's skirt with
  sky, a black horizon and the wheel's warm wood reflected below it; a
  black selective outline on its right and underside.
- The table: felt that recedes into the dark level with the (rolled)
  horizon, lit round the wheel, falling off with short Bayer seams; the
  betting layout's lines, a step darker, run off to the right in true
  perspective: a quiet sign of the table.
- Depth: front, the chip, the ball and the near pockets (contrasty,
  saturated); middle, the rotor, its band, the cone; back, the turret, the
  far rim and the felt falling off into black.
- The title: across the top band in a calm black sky, a bold italic that
  leans into the spin (re-kerned to an even 2 px), moved down to clear the
  menu's border. Gold chrome that nothing else uses: cream top edges, a
  bright sky, a dark horizon under the E's middle bar (stopping a pixel
  short of each stroke's right edge), light below it; a three-step
  extrusion (gold0 by the face, then wine), every letter parted from its
  neighbours' extrusion by black; a drop shadow; catch-light stars centred
  on the R's and the last E's outer top corners.

Palette plan (11 own + cream, grey, black, red):
- gold0 gold1 gold2 ... the title's face, bevel and extrusion's lit step,
                        nothing else.
- wine ................ red in shade, the streaks' ends, the ring's step,
                        the cone's mirror, the ball's halo and shadow, the
                        title's depth.
- wood0 wood1 wood2 ... lacquered mahogany, hue-shifted (cream the peak);
                        wood2 also the warm wheel seen in the chrome.
- steel1 pearl ........ chrome (with grey, black, cream) and the ball.
- felt1 felt2 ......... the table, the zero, the chip.
- fixed: red (the pockets), black (the void, outlines), cream (speculars,
  glints, the chip's spots), grey (chrome's ground, frets, speed lines).

How it is painted: render3d marches the wheel, the turret and the chip on
white surfaces twice (4 rays a pixel for which object each pixel shows, one
ray at each pixel's centre for the point, its normal and the key light) and
every surface is coloured by hand on the pixels: levels of a ramp in flat
bands with dithered seams only where a band is wide (lvq/terr below), the
rotor as a smear pattern, the chrome from matcaps and from tubes and balls
drawn on the picture. What must be
crisp is drawn as pixel-perfect one-pixel curves (raster below: no L
corners) projected from the wheel's own circles: the band, the gleams, the
crest, the frets, the lacquer streaks, the speed lines. Lone pixels are
cleaned, then the title.

Font: Syndor24j.Scn.Fnt from the Oberon system's fonts (hoard-of-bitfonts),
at its own size; terms: a system's font, its vendor's (tools/art/title.txt).
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import numpy as np  # noqa: E402
import artkit as ak  # noqa: E402
from artkit import render3d as R  # noqa: E402

TITLE = HERE / "art" / "title.txt"
TITLE_Y = 6
# the face, row by row: gold chrome (a bright sky, a dark horizon under the
# E's middle bar, the ground's light below it)
TITLE_ROWS = (["gold2"] * 6 + ["gold1"] * 3 + ["gold0"] + ["gold2"] * 3 + ["gold1"] * 4)
HORIZON = 9
GLINTS = ((2, 0), (115, 0))               # on the title's mask: the R's and the last E's top corners

TAU = 2 * np.pi
NP = 37                                   # the European wheel
SECTOR = TAU / NP
PHASE = np.radians(24) + SECTOR           # where the zero sits

PAL = {
    "gold0": "#8E4A06", "gold1": "#E8A018", "gold2": "#FFE77A",       # the title's own
    "wine": "#5C0A1C",
    "wood0": "#3E1206", "wood1": "#8E3412", "wood2": "#E27C2C",
    "steel1": "#8A9CBC", "pearl": "#D4DCEA",
    "felt1": "#0A4A2A", "felt2": "#1A7844",
}
FIX = {"black": "#000000", "cream": "#FFF4D6", "grey": "#808080", "red": "#D62020"}
C = {**PAL, **FIX}
WOOD = ["black", "wood0", "wood1", "wood2", "cream"]
FELT = ["black", "felt1", "felt2"]

BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float64) + 0.5) / 16
BAYER = np.tile(BAYER, (32, 32))
YY, XX = np.mgrid[0:128, 0:128]


# ---- the camera and the light ---------------------------------------------------------

E = np.radians(26)
ROLL = -8
TARGET = (-0.1, 0.0, 0.15)
CAM = R.Camera((TARGET[0], 1.25 * np.sin(E), TARGET[2] + 1.25 * np.cos(E)), TARGET, fov=76,
               up=(np.sin(np.radians(ROLL)), 1, 0), shift=(0, 14))
KEY = np.array([-0.45, 0.85, 0.35])                    # the house key, top left (high: short shadows)
KEY = KEY / np.linalg.norm(KEY)


# ---- levels: flat bands of a ramp, ordered dither only where asked ----------------------

def lvq(v, dither, steps=4):
    """Levels (floats, 0 = the ramp's first colour) to whole levels: a
    Bayer dither in `steps` steps where `dither`, plain rounding elsewhere."""
    fl = np.floor(v)
    fr = np.round((v - fl) * steps) / steps
    d = fl + (fr > BAYER)
    return np.where(dither, d, np.round(v)).astype(np.int64)


def put_levels(pic, mask, lv, names):
    lv = np.clip(lv, 0, len(names) - 1)
    lut = np.array([pic.pal[n] for n in names], np.uint8)
    pic.idx[mask] = lut[lv[mask]]


# ---- helpers ----------------------------------------------------------------------------

def ihash(k, seed):
    """A fixed random number in 0..1 per integer k (arrays welcome)."""
    k = np.asarray(k, dtype=np.int64)
    h = (k * 374761393 + seed * 668265263) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


def bump(a, centre, half):
    dd = np.abs((a - centre + 180) % 360 - 180)
    return np.clip(1 - dd / half, 0, 1)


def raster(pts, closed=False):
    """A picture-space polyline as pixels, 8-connected and one pixel thick
    (no L-shaped corners): [(x, y, t)], t the position along it (0..1)."""
    if closed:
        pts = list(pts) + [pts[0]]
    out = []
    n = len(pts) - 1
    for i, ((x0, y0), (x1, y1)) in enumerate(zip(pts, pts[1:])):
        k = int(max(abs(x1 - x0), abs(y1 - y0)) * 6) + 1
        for s in np.arange(k) / k:
            q = (int(np.floor(x0 + (x1 - x0) * s)), int(np.floor(y0 + (y1 - y0) * s)), (i + s) / n)
            if out and out[-1][:2] == q[:2]:
                continue
            out.append(q)
            while len(out) >= 3:
                a, b, c = out[-3], out[-2], out[-1]
                if a[:2] == c[:2]:
                    out.pop()
                    out.pop()
                    continue
                if abs(a[0] - c[0]) <= 1 and abs(a[1] - c[1]) <= 1:
                    out.pop(-2)                        # b is an L corner (or a doubled step)
                    continue
                break
    return out


def circle_pts(cam, r, y, a0, a1, n=720):
    """The wheel's circle of radius r at height y, from a0 to a1 degrees
    (0: right, 90: nearest the camera, 180: left, 270: far), on the picture."""
    return [cam.project((r * np.cos(t), y, r * np.sin(t))) for t in np.radians(np.linspace(a0, a1, n))]


def arc_px(cam, r, y, a0, a1, n=720):
    """A circle's pixels with their angle in degrees."""
    return [(x, y_, a0 + (a1 - a0) * t) for x, y_, t in raster(circle_pts(cam, r, y, a0, a1, n))]


def despeckle(pic, need=5, keep=None, within=None):
    """Lone pixels (unlike all eight neighbours, and not part of a dither:
    no pixel of their colour two steps away) take the colour most of their
    neighbours share, when at least `need` of the eight do."""
    a = pic.idx
    pad = np.pad(a, 2, mode="edge")
    c = a
    nb = [pad[2 + dy:130 + dy, 2 + dx:130 + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dx or dy]
    lone = np.ones_like(a, dtype=bool)
    for q in nb:
        lone &= q != c
    two = np.zeros_like(lone)
    for dy, dx in ((-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)):
        two |= pad[2 + dy:130 + dy, 2 + dx:130 + dx] == c
    lone &= ~two
    if keep is not None:
        lone &= ~keep
    if within is not None:
        lone &= within
    stack = np.stack(nb, -1)
    best = np.zeros_like(a)
    cnt = np.zeros(a.shape, dtype=np.int32)
    for k in np.unique(stack):
        n = (stack == k).sum(-1)
        better = n > cnt
        best = np.where(better, k, best)
        cnt = np.where(better, n, cnt)
    fix = lone & (cnt >= need)
    a[fix] = best[fix]
    return int(fix.sum())


def lonely(pic, colour, within, into=None):
    """Pixels of `colour` inside `within` with no 4-neighbour of their
    colour take the colour most of their 4 neighbours share (or `into`)."""
    a = pic.idx
    k = pic.pal[colour]
    m = a == k
    has = ak.shift(m, 1, 0) | ak.shift(m, -1, 0) | ak.shift(m, 0, 1) | ak.shift(m, 0, -1)
    lone = m & ~has & within
    if into is not None:
        a[lone] = pic.pal[into]
        return int(lone.sum())
    pad = np.pad(a, 1, mode="edge")
    nb = np.stack([pad[1:129, 2:130], pad[1:129, 0:128], pad[2:130, 1:129], pad[0:128, 1:129]], -1)
    best = nb[..., 0].copy()
    cnt = np.zeros(a.shape, np.int32)
    for v in np.unique(nb):
        n = (nb == v).sum(-1)
        better = n > cnt
        best = np.where(better, v, best)
        cnt = np.where(better, n, cnt)
    a[lone] = best[lone]
    return int(lone.sum())


def letters(M):
    """The title's letters, labelled 1.. (4-connected components)."""
    lab = np.zeros(M.shape, np.int32)
    n = 0
    for y0, x0 in zip(*np.nonzero(M)):
        if lab[y0, x0]:
            continue
        n += 1
        stack = [(y0, x0)]
        lab[y0, x0] = n
        while stack:
            y, x = stack.pop()
            for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= yy < M.shape[0] and 0 <= xx < M.shape[1] and M[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = n
                    stack.append((yy, xx))
    return lab


# ---- the wheel ----------------------------------------------------------------------------

BOWL, RING, POCKETS, CHROME, CONE = range(5)
CHIP = 5                                  # a chip flying past in the foreground
CHIP_AT = (0.25, 0.20, 0.76)
CHIP_R, CHIP_T = 0.095, 0.014
CHIP_TILT = (-25, 55)                     # turned about z, then about x (degrees)
CHIP_FLY = (1.0, 0.75)                    # behind it on the picture: where it came from
NMAT = 6
LAYOUT = [(1.2, -1.3, 4.0, -1.3), (1.2, -1.3, 1.2, -6.0), (1.2, -2.0, 4.0, -2.0),
          (1.75, -1.3, 1.75, -6.0)]               # the betting layout's lines on the table, (x, z) to (x, z)
R_CONE = 0.475
PATH_R = 0.74                             # the ball's path over the number ring
BALL_XY = (39, 96)                        # the ball's centre on the picture
BALL_PX = 8.2                             # its radius
BALL_H = 0.06                             # its height over the wheel (it is in the air)
TURRET_S = 1.32
TURRET_ROT = 16                           # the cross, turned round its spindle
ARM = 0.2


def turret_point(q):
    """A point given in the turret's own frame (the cross at y 0.35, before
    it is turned and enlarged) in the world."""
    a = np.radians(TURRET_ROT)
    x, y, z = q
    x, z = x * np.cos(a) + z * np.sin(a), -x * np.sin(a) + z * np.cos(a)
    return np.array([x * TURRET_S, 0.10 + (y - 0.10) * TURRET_S, z * TURRET_S])


def scene():
    bowl = R.lathe([(0.0, -0.3), (1.05, -0.3), (1.05, 0.06), (1.035, 0.09), (1.0, 0.1), (0.975, 0.085),
                    (0.965, 0.04), (0.95, 0.02), (0.81, -0.03), (0.795, -0.06), (0.795, -0.16), (0.0, -0.16)])
    ring = R.lathe([(0.0, -0.2), (0.795, -0.2), (0.795, -0.042), (0.785, -0.036), (0.635, -0.052),
                    (0.63, -0.07), (0.0, -0.07)])
    cone = R.lathe([(0.0, -0.2), (0.475, -0.2), (0.475, -0.06), (0.40, -0.02), (0.30, 0.04), (0.20, 0.09),
                    (0.15, 0.11), (0.0, 0.115)])
    ends = [R.xf(R.prim(R.sphere(0.035), CHROME), pos) for pos in [(ARM, 0, 0), (-ARM, 0, 0), (0, 0, ARM), (0, 0, -ARM)]]
    turret = R.U(R.prim(R.lathe([(0.0, 0.10), (0.12, 0.10), (0.10, 0.135), (0.055, 0.16), (0.03, 0.20),
                                 (0.0, 0.20)]), CHROME),
                 R.xf(R.prim(R.cylinder(0.022, 0.15), CHROME), (0, 0.29, 0)),
                 R.xf(R.U(R.prim(R.capsule((-ARM, 0.0, 0.0), (ARM, 0.0, 0.0), 0.021), CHROME),
                          R.prim(R.capsule((0.0, 0.0, -ARM), (0.0, 0.0, ARM), 0.021), CHROME), *ends),
                      (0, 0.35, 0), R.rot_y(TURRET_ROT)),
                 R.prim(R.lathe([(0.0, 0.40), (0.024, 0.402), (0.030, 0.418), (0.022, 0.434), (0.010, 0.452),
                                 (0.004, 0.485), (0.0, 0.50)]), CHROME))                         # the finial
    turret = R.xf(R.xf(turret, (0, -0.10, 0)), (0, 0.10, 0), scale=TURRET_S)    # a box-art turret: bigger
    chip = R.xf(R.prim(R.cylinder(CHIP_R, CHIP_T, 0.006), CHIP), CHIP_AT, R.rot_z(CHIP_TILT[0]) @ R.rot_x(CHIP_TILT[1]))
    return R.U(R.prim(bowl, BOWL), R.prim(ring, RING), R.prim(cone, CONE), turret, chip)


def geometry(cam, sc):
    """What the wheel is at each pixel: its material (the majority of 4
    rays), and at the pixel's centre the surface point, its normal and how
    much of the key light reaches it (shadows and occlusion)."""
    big = ak.Canvas("#000000")
    out = R.render(big, sc, cam, [R.Mat("#FFFFFF", spec=0.0)] * NMAT, lights=[(tuple(KEY), "#FFFFFF", 1.0)],
                   ambient="#383838", ss=2, shadows=False, ao=False)
    m = out["mat"].reshape(128, 4, 128, 4).transpose(0, 2, 1, 3).reshape(128, 128, 16)
    best = np.full((128, 128), -1, np.int64)
    cnt = (m == -1).sum(-1)
    for k in range(NMAT):
        c = (m == k).sum(-1)
        best = np.where(c > cnt, k, best)
        cnt = np.maximum(c, cnt)
    one = ak.Canvas("#000000", ss=1)
    o1 = R.render(one, sc, cam, [R.Mat("#FFFFFF", spec=0.0)] * NMAT, lights=[(tuple(KEY), "#FFFFFF", 1.0)],
                  ambient="#383838", ss=None)
    o, d = cam.rays((XX + 0.5).reshape(-1).astype(np.float64), (YY + 0.5).reshape(-1).astype(np.float64))
    dep = o1["depth"].reshape(-1)
    z = np.where(np.isfinite(dep), dep, 0)
    p = (o + d * z[:, None]).reshape(128, 128, 3)
    n = o1["normal"].astype(np.float64)
    v = o1["rgb"][..., 0]
    lit = np.clip((v - 0.22) / 0.95, 0, 1)
    gnd = R.ground(one, sc, cam, y=0.06, ss=None)
    return dict(mat=best, p=p, n=n, lit=lit, mat1=o1["mat"], gnd=gnd)


def ball_world(cam):
    """Where the ball is in the world: the angle and radius at height BALL_H
    that land on BALL_XY."""
    best = None
    for a in np.radians(np.linspace(90, 150, 241)):
        for r in np.linspace(0.62, 0.80, 37):
            x, y = cam.project((r * np.cos(a), BALL_H, r * np.sin(a)))
            e = (x - BALL_XY[0] - 0.5) ** 2 + (y - BALL_XY[1] - 0.5) ** 2 + 0.5 * (r - PATH_R) ** 2
            if best is None or e < best[0]:
                best = (e, a, r)
    return best[1], BALL_H, best[2]


# ---- the spinning rotor -------------------------------------------------------------------

LANES = 44.0                              # streak lanes per unit of radius


def rotor_pattern(x, z):
    """The spinning rotor at (x, z): 0 black, 1 wine, 2 red, 3 the zero.
    A smear frame: the rotor turns toward growing angles; each pocket keeps
    its body and its leading edge, and a red (or green) pocket's colour
    trails back into the black one behind it, a different length in each
    lane, its far end thinning to wine."""
    th = np.arctan2(z, x)
    r = np.hypot(x, z)
    lane = np.floor(r * LANES).astype(np.int64)
    xs = np.mod(th - PHASE, TAU) / SECTOR
    kf = np.floor(xs).astype(np.int64)
    f = xs - kf
    nxt = (kf + 1) % NP

    def col(j):
        return np.where(j == 0, 3, np.where(j % 2 == 1, 2, 0))
    base, ahead = col(kf), col(nxt)
    ext = 0.10 + 0.42 * ihash(lane * 64 + nxt, 9) ** 1.3
    trail = (f > 1 - ext) & (ahead != 0) & (base == 0)
    out = np.where(trail, ahead, base)
    out = np.where(trail & (ahead == 2) & (f < 1 - 0.6 * ext), 1, out)
    return out, kf, f


def terr(v, soft=0.4):
    """Levels pushed onto whole-level plateaus with short ramps between
    them: flat bands, dithered only at their seams."""
    k = np.floor(v)
    s = np.clip((v - k - 0.5) / soft + 0.5, 0, 1)
    return k + s


def thick(m, n=2):
    """The parts of a mask at least 2n+1 pixels thick (and a pixel round them)."""
    return ak.dilate(ak.erode(m, n), n) & m


def chrome(nx, ny, part, ly):
    """Hot chrome, by the normal's direction on the picture (nx right, ny
    up), the turret's part and the height on it: on the round parts a pearl
    sky, a hard black horizon below the middle, the grey room under it and
    a steel rim of reflected light; on the spindle and the bell's neck the
    same world standing up (a pearl streak on the lit left, black on the
    right); on the bell's skirt the sky above a black horizon and the lit
    wheel's wood below it; dark at the far right."""
    c = np.full(nx.shape, "steel1", object)
    rnd = part == 0
    c[rnd & (ny > 0.25)] = "pearl"
    c[rnd & (ny <= 0.0)] = "black"
    c[rnd & (ny < -0.32)] = "grey"
    c[rnd & (ny < -0.78)] = "steel1"
    c[rnd & (nx > 0.66) & (ny > 0.0)] = "grey"
    up = (part == 1) | ((part == 2) & (ly > 0.155))
    c[up & (nx < -0.2)] = "pearl"
    c[up & (nx > 0.2)] = "black"
    c[up & (nx > 0.62)] = "grey"
    sk = (part == 2) & (ly <= 0.155)
    c[sk] = "pearl"
    c[sk & (nx > 0.25)] = "steel1"
    c[sk & (nx > 0.70)] = "grey"
    c[sk & (ly <= 0.144)] = "black"
    c[sk & (ly <= 0.134)] = "wood2"
    c[sk & (ly <= 0.134) & (nx > 0.3)] = "grey"
    return c


def draw():
    P = ak.Palette(PAL, ramps=[["black", "wine", "red"], WOOD, ["black", "grey", "steel1", "pearl", "cream"],
                               FELT, ["gold0", "gold1", "gold2", "cream"]])
    pic = ak.Picture.blank(P, "black")
    cam = CAM
    sc = scene()
    G = geometry(cam, sc)
    mat, p, n, lit = G["mat"], G["p"], G["n"], G["lit"]
    rr = np.hypot(p[..., 0], p[..., 2])
    az = np.degrees(np.arctan2(p[..., 2], p[..., 0])) % 360
    py = p[..., 1]
    on = {k: mat == k for k in range(NMAT)}
    rot = on[RING]
    wheel = (mat >= 0) & (mat != CHIP)
    tx_, ty_ = cam.project((0, 0.33 * TURRET_S, 0))            # the turret's cross
    everywhere = np.ones((128, 128), bool)
    cx, cy = BALL_XY
    R_ = BALL_PX
    dx, dy = XX - cx, YY - cy
    disc = dx * dx + dy * dy <= R_ * (R_ + 0.8)                # the ball: a round disc, no one-pixel nubs
    # the pool of light: on the wheel's left, falling to dark at the frame's edges
    spot = np.clip(1.3 - np.hypot((XX - 48) / 100.0, (YY - 78) / 70.0), 0, 1)
    edge_v = (np.clip((np.minimum(XX, 127 - XX) - 0.5) / 7.0, 0.0, 1)
              * np.clip((127 - YY - 0.5) / 9.0, 0.0, 1))
    vig = np.clip(spot * edge_v, 0, 1)

    # ---- the table: felt in a soft pool of light round the turret, falling off into black
    rr_ = np.radians(ROLL)
    u = (XX + 0.5 - tx_) * np.cos(rr_) + (YY + 0.5 - ty_ - 4) * np.sin(rr_)
    w = -(XX + 0.5 - tx_) * np.sin(rr_) + (YY + 0.5 - ty_ - 4) * np.cos(rr_)
    far = np.clip((w + 16.0) / 20.0, 0, 1)                     # the table recedes into the dark, level with the horizon
    side = np.clip(1.0 - (np.abs(u) / 78.0) ** 2, 0, 1)
    pool = far * side * edge_v
    fv = np.clip(pool * 2.6, 0, 2.0) - 1.4 * np.clip(G["gnd"], 0, 1)
    put_levels(pic, ~wheel, lvq(terr(np.clip(fv, 0, 2), 0.4), everywhere), FELT)

    # ---- the betting layout's lines on the felt, far off to the right
    # (darker felt, only where the felt is lit): the sign of a table
    lay = np.zeros((128, 128), bool)
    for x0_, z0_, x1_, z1_ in LAYOUT:
        pts = [cam.project((x0_ + (x1_ - x0_) * t, 0.06, z0_ + (z1_ - z0_) * t)) for t in np.linspace(0, 1, 200)]
        for x_, y_, _ in raster(pts):
            if 0 <= x_ < 128 and 0 <= y_ < 128:
                lay[y_, x_] = True
    pic.put(lay & ~wheel & pic.where("felt2"), "felt1")

    # ---- the bowl: lacquered mahogany, zone by zone, flat bands
    bowl = on[BOWL]
    outer = bowl & (rr > 1.04) & (py < 0.05)
    lip = bowl & (rr >= 0.965) & ~outer
    trk = bowl & (rr >= 0.95) & (rr < 0.965)
    apr = bowl & (rr >= 0.81) & (rr < 0.95)
    inw = bowl & (rr < 0.81)
    L = np.zeros((128, 128))
    lipL = (1.55 + 0.85 * bump(az, 185, 70) + 0.6 * bump(az, 275, 70)
            - 0.55 * np.clip((np.abs(rr - 1.0) - 0.014) / 0.02, 0, 1))
    L = np.where(lip, lipL, L)
    L = np.where(trk, 0.55 + 0.4 * bump(az, 290, 60), L)
    aprL = (1.25 + 0.9 * bump(az, 180, 60) + 0.8 * bump(az, 300, 70)
            - 0.5 * np.clip((0.85 - rr) / 0.035, 0, 1) - 0.4 * np.clip((rr - 0.93) / 0.02, 0, 1))
    L = np.where(apr, aprL, L)
    L = np.where(inw, 0.3, L)
    L = np.where(outer, 0.9 + 0.5 * bump(az, 140, 50), L)
    L = L * np.clip(0.4 + 0.75 * vig, 0, 1.05)
    wide = (thick(lip) | thick(apr) | thick(outer)) & ak.erode(bowl, 1, diag=True)
    put_levels(pic, bowl, lvq(terr(np.clip(L, 0, 3), 0.45), wide, steps=2), WOOD)
    for c_ in ("wood1", "wood0", "black"):                      # no crumbs where the bands are thin
        lonely(pic, c_, bowl & ~wide)

    # ---- the rotor, spinning
    pat, kf, f = rotor_pattern(p[..., 0], p[..., 2])
    shade = np.clip(lit * vig, 0, 1)
    pat = np.where((pat == 2) & (shade < 0.30), 1, pat)
    pat = np.where((pat == 1) & (shade < 0.12), 0, pat)
    lut = np.array([P["black"], P["wine"], P["red"], P["felt2"]], np.uint8)
    pic.idx[rot] = lut[pat[rot]]
    lonely(pic, "wine", rot)
    # the step from the number ring down to the pockets: a dark line through the red
    for x, y, a in arc_px(cam, 0.632, -0.07, 0, 360, 1440):
        if 0 <= x < 128 and 0 <= y < 128 and rot[y, x] and pic.idx[y, x] == P["red"] and 15 < a < 175:
            pic.px(x, y, "wine")

    # ---- the cone: a lacquered dome, lit up left, a crescent of gloss in
    # front of the bell, lacquer streaks sweeping round with the spin
    cone = on[CONE]
    q = np.clip(rr / R_CONE, 0, 1)
    slope = 1.3 * np.sin(np.pi / 2 * q)
    nd = np.stack([p[..., 0] / np.maximum(rr, 1e-6) * slope, np.ones_like(rr),
                   p[..., 2] / np.maximum(rr, 1e-6) * slope], -1)
    nd /= np.linalg.norm(nd, axis=-1, keepdims=True)
    cd = np.clip((nd * KEY).sum(-1), 0, 1)
    cl = 0.6 + 2.05 * cd ** 1.9
    cl = cl - 0.5 * np.clip((q - 0.8) / 0.2, 0, 1) * bump(az, 60, 90)       # the near-right rim turns away
    hl = np.exp(-((q - 0.45) / 0.11) ** 2) * bump(az, 140, 46)
    cl = np.where(hl > 0.3, np.maximum(cl, 3.0), cl)
    cl = np.where(hl > 0.68, 4.0, cl)
    clv = lvq(terr(np.clip(cl, 0, 4), 0.32), ak.erode(cone, 1))
    put_levels(pic, cone, clv, WOOD)
    for k in range(6):                                          # lacquer streaks, spiralling out
        a0 = 200 + k * 60 + 17 * ihash(k, 5)
        pts = [cam.project(((0.17 + 0.27 * t) * np.cos(np.radians(a0 + 70 * t)), 0.11 - 0.17 * t,
                            (0.17 + 0.27 * t) * np.sin(np.radians(a0 + 70 * t)))) for t in np.linspace(0.12, 0.85, 120)]
        for x, y, t in raster(pts):
            if 0 <= x < 128 and 0 <= y < 128 and cone[y, x] and 1 <= clv[y, x] <= 2:
                pic.idx[y, x] = P[WOOD[clv[y, x] + 1]]
    # the spinning ring mirrored along the cone's near rim
    for x, y, a in arc_px(cam, 0.455, -0.048, 25, 165, 900):
        if 0 <= x < 128 and 0 <= y < 128 and cone[y, x]:
            pr, _, _ = rotor_pattern(np.array(0.7 * np.cos(np.radians(a))), np.array(0.7 * np.sin(np.radians(a))))
            pic.px(x, y, "red" if (pr == 2 and 50 < a < 140) else "wine")

    # ---- the rotor's chrome band round the cone: steel over grey on the
    # near arc, a few cream pings where the lamp catches it
    band = arc_px(cam, 0.478, -0.058, 0, 360, 1440)
    bandm = np.zeros((128, 128), bool)
    for x, y, a in band:
        if 0 <= x < 128 and 0 <= y < 128 and mat[y, x] in (RING, CONE):
            c = "pearl" if 165 < a < 200 else "steel1" if 60 < a < 255 else "grey"
            pic.px(x, y, c)
            bandm[y, x] = True
    for x, y, a in band:
        if 25 < a < 160 and 0 <= x < 128 and 0 <= y + 1 < 128 and rot[y + 1, x] and not bandm[y + 1, x]:
            pic.px(x, y + 1, "grey")
    for a_ in (176, 188):
        x, y = cam.project((0.478 * np.cos(np.radians(a_)), -0.058, 0.478 * np.sin(np.radians(a_))))
        pic.px(int(x), int(y), "cream")

    # ---- the frets: a bright edge at each pocket's front on the near arc
    for j in range(NP):
        a = np.degrees(PHASE + j * SECTOR) % 360
        if not 42 < a < 140:
            continue
        pts = [cam.project((r_ * np.cos(np.radians(a)), -0.085, r_ * np.sin(np.radians(a))))
               for r_ in np.linspace(0.50, 0.625, 40)]
        for x, y, t in raster(pts):
            if (x - cx) ** 2 + (y - cy) ** 2 < (R_ + 4) ** 2 or not (0 <= x < 128 and 0 <= y < 128) or not rot[y, x]:
                continue
            pic.px(x, y, "steel1" if t > 0.55 else "grey")

    # ---- the turret: hot chrome
    tur = on[CHROME]
    nx = (n * cam.r).sum(-1)
    ny = (n * cam.u).sum(-1)
    a_ = np.radians(-TURRET_ROT)
    lx = (p[..., 0] * np.cos(a_) + p[..., 2] * np.sin(a_)) / TURRET_S          # back in the turret's own frame
    lz = (-p[..., 0] * np.sin(a_) + p[..., 2] * np.cos(a_)) / TURRET_S
    ly = 0.10 + (py - 0.10) / TURRET_S
    part = np.where(ly < 0.205, 2, np.where((np.hypot(lx, lz) < 0.03) & ((ly < 0.33) | (ly > 0.395)), 1, 0))
    tcol = chrome(nx, ny, part, ly)
    for name in ("pearl", "steel1", "grey", "black", "cream", "wood2"):
        pic.put(tur & (tcol == name), name)
    # the cross drawn on the picture as tubes and balls, so each reads clean:
    # across each arm a pearl sky, steel, a black horizon and grey ground;
    # each knob a chrome ball with a cream ping up left
    ppu = 64 / np.tan(np.radians(38))
    c0 = turret_point((0, 0.35, 0))
    cxy = np.array(cam.project(c0))
    knobs = []
    for e in ((ARM, 0.35, 0), (-ARM, 0.35, 0), (0, 0.35, ARM), (0, 0.35, -ARM)):
        w_ = turret_point(e)
        kxy = np.array(cam.project(w_))
        knobs.append((kxy, 0.035 * TURRET_S * ppu / np.linalg.norm(w_ - cam.pos) + 0.35,
                      0.021 * TURRET_S * ppu / np.linalg.norm((w_ + c0) / 2 - cam.pos) + 0.3))
    px_, py_ = XX + 0.5, YY + 0.5
    arms_ = (part == 0) & tur
    best_d = np.full((128, 128), 1e9)
    vv = np.zeros((128, 128))
    for kxy, kr, aw in knobs:                                   # the arms: nearest tube
        d_ = kxy - cxy
        L2 = (d_ ** 2).sum()
        t_ = np.clip(((px_ - cxy[0]) * d_[0] + (py_ - cxy[1]) * d_[1]) / L2, 0, 1)
        ex, ey = px_ - (cxy[0] + t_ * d_[0]), py_ - (cxy[1] + t_ * d_[1])
        dist = np.hypot(ex, ey)
        nrm = np.array([-d_[1], d_[0]]) / np.sqrt(L2)
        if nrm[1] < 0:
            nrm = -nrm                                          # the side that is down on the picture
        better = dist < best_d
        best_d = np.where(better, dist, best_d)
        vv = np.where(better, (ex * nrm[0] + ey * nrm[1]) / aw, vv)
    tube = np.full((128, 128), "steel1", object)
    tube[vv < -0.42] = "pearl"
    tube[vv >= 0.05] = "black"
    tube[vv >= 0.55] = "grey"
    for name in ("pearl", "steel1", "grey", "black"):
        pic.put(arms_ & (tube == name), name)
    pings = []
    for kxy, kr, aw in knobs:                                   # the knobs
        u_, v_ = (px_ - kxy[0]) / kr, (py_ - kxy[1]) / kr
        ball = (u_ * u_ + v_ * v_ <= 1.0) & tur & (part == 0)
        bc = np.full((128, 128), "pearl", object)
        bc[u_ > 0.42] = "steel1"
        hz = v_ - 0.12 * u_ * u_
        bc[hz > 0.02] = "black"
        bc[hz > 0.34] = "grey"
        bc[hz > 0.72] = "steel1"
        bc[(u_ > 0.72) & (hz <= 0.02)] = "grey"
        for name in ("pearl", "steel1", "grey", "black"):
            pic.put(ball & (bc == name), name)
        hx, hy = int(np.floor(kxy[0] - 0.42 * kr)), int(np.floor(kxy[1] - 0.45 * kr))
        if ball[hy, hx]:
            pic.px(hx, hy, "cream")
            pings.append((hx, hy))
    tys, txs = np.nonzero(tur)
    k = np.argmin(tys)
    sx0, sy0 = int(txs[k]), int(tys[k]) + 1
    keep_star = np.zeros((128, 128), bool)
    for ddx, ddy, c_ in ((0, 0, "cream"), (1, 0, "cream"), (-1, 0, "cream"), (0, 1, "cream"), (0, -1, "cream"),
                         (2, 0, "pearl"), (-2, 0, "pearl"), (0, -2, "pearl")):
        pic.px(sx0 + ddx, sy0 + ddy, c_)
        keep_star[sy0 + ddy, sx0 + ddx] = True
    # a selective outline: black on its right and underside, against the felt and the bowl
    out_ = ak.dilate(tur, 1, diag=True) & ~tur & ~on[CONE]
    below_right = (ak.shift(tur, 1, 0) | ak.shift(tur, 0, 1) | ak.shift(tur, 1, 1) | ak.shift(tur, -1, 1))
    pic.put(out_ & below_right & ~ak.shift(tur, -1, 0), "black")

    # ---- the lacquer's gleam on the ball track: crisp arcs, brightest nearest the light
    for r_, y_, a0, a1, cols in ((0.895, -0.005, 128, 236, ((166, 194, "cream"), (146, 214, "wood2"), (0, 999, "wood1"))),
                                 (0.905, -0.003, 160, 202, ((172, 188, "cream"), (0, 999, "wood2"))),
                                 (0.86, -0.02, 150, 215, ((0, 999, "wood1"),)),
                                 (0.89, -0.006, 284, 372, ((318, 346, "wood2"), (0, 999, "wood1")))):
        for x, y, a in arc_px(cam, r_, y_, a0, a1, 1200):
            if 0 <= x < 128 and 0 <= y < 128 and apr[y, x]:
                for lo, hi, c in cols:
                    if lo <= a <= hi:
                        pic.px(x, y, c)
                        break

    # ---- the lacquer's crest along the lip
    for x, y, a in arc_px(cam, 0.988, 0.098, 140, 228, 900):     # swelling to 2 px nearest the light
        if 0 <= x < 128 and 0 <= y < 128 and bowl[y, x]:
            pic.px(x, y, "wood2")
    crest = []
    for r_, a0, a1 in ((1.0, 95, 232), (0.994, 232, 380)):          # on the far side just inside the silhouette
        crest += [(x, y, a) for x, y, a in arc_px(cam, r_, 0.1, a0, a1, 1400)]
    for x, y, a in crest:
        if 0 <= x < 128 and 0 <= y < 128 and bowl[y, x]:
            a = a % 360
            c = "cream" if 158 < a < 200 else "wood2" if (a > 112 and x < 119) else "wood1"
            pic.px(x, y, c)

    # ---- the ball: in the air over the near pockets, its shadow on them
    # below right, speed lines back along its orbit
    A, h, rp = ball_world(cam)
    near_ball = (dx * dx + dy * dy <= (R_ + 3.5) ** 2) & rot
    pic.put(near_ball & pic.where("red"), "wine")            # the pockets round it a step darker
    gx, gy = cam.project((rp * np.cos(A), -0.05, rp * np.sin(A)))
    gx, gy = gx + 3.0, gy + 2.0                                 # its shadow, parted from it: it is in the air
    sh = ((XX + 0.5 - gx) / 5.0) ** 2 + ((YY + 0.5 - gy) / 1.8) ** 2 <= 1
    core = ((XX + 0.5 - gx) / 3.2) ** 2 + ((YY + 0.5 - gy) / 1.0) ** 2 <= 1
    clear = ~ak.dilate(disc, 2, diag=True)
    pic.put(sh & clear & rot & pic.where("red"), "wine")
    pic.put(core & clear & rot, "black")
    # speed lines back along its path
    speed = np.zeros((128, 128), bool)
    lines_ = []
    orb = [cam.project((rp * np.cos(a), h, rp * np.sin(a))) for a in np.linspace(A, A + 0.9, 400)]
    seg = np.array([np.hypot(b_[0] - a_[0], b_[1] - a_[1]) for a_, b_ in zip(orb, orb[1:])])
    cum = np.concatenate([[0], np.cumsum(seg)])
    t0 = np.array(orb[1]) - np.array(orb[0])
    t0 /= np.linalg.norm(t0)
    # half the orbit's bend: the lines sweep along it without curling up the rim
    path = [tuple(0.5 * np.array(o_) + 0.5 * (np.array(orb[0]) + t0 * c_)) for o_, c_ in zip(orb, cum)]
    seg = np.array([np.hypot(b_[0] - a_[0], b_[1] - a_[1]) for a_, b_ in zip(path, path[1:])])
    cum = np.concatenate([[0], np.cumsum(seg)])
    tang = [(b_[0] - a_[0], b_[1] - a_[1]) for a_, b_ in zip(path, path[1:])]
    tang.append(tang[-1])
    for off, s0, length, gaps in ((-4.2, 2.0, 11, ((0.62, 0.76),)),
                                  (0.0, 0.0, 19, ((0.50, 0.60),)),
                                  (4.2, 3.0, 8, ())):
        pts = []
        for (x_, y_), (tx2, ty2), s_ in zip(path, tang, cum):
            L_ = np.hypot(tx2, ty2)
            ox, oy = -ty2 / L_ * off, tx2 / L_ * off
            dd = np.sqrt(max(R_ ** 2 - off ** 2, 0))           # where the line leaves the ball's edge
            if s_ < dd + 1.5 + s0 or s_ > dd + 1.5 + s0 + length:
                continue
            pts.append((x_ + ox, y_ + oy))
        if len(pts) < 2:
            continue
        dash = []
        for x_, y_, t_ in raster(pts):
            if any(g0 <= t_ < g1 for g0, g1 in gaps) or not (0 <= x_ < 128 and 0 <= y_ < 128) or disc[y_, x_]:
                if len(dash) > 1:                               # no one-pixel scraps at the gaps
                    lines_.extend(dash)
                dash = []
                continue
            dash.append((x_, y_, "pearl" if t_ < 0.45 else "steel1" if t_ < 0.78 else "grey"))
        if len(dash) > 1:
            lines_.extend(dash)
    for x_, y_, c in lines_:
        pic.px(x_, y_, c)
        speed[y_, x_] = True
    halo = (ak.shift(speed, 0, 1) | ak.shift(speed, 1, 1)) & ~speed & ~disc & rot
    pic.put(halo & pic.where("red"), "wine")                  # a dark edge under each: the lines read on the red
    # the ball itself: a pearl, lit up left (a rounded cream hot spot, pearl,
    # steel at its terminator, grey in its core shadow), red thrown up from
    # the ring along its lower right edge, outlined on its shadow side; a
    # glint where its edge catches the lamp
    nxb, nyb = dx / R_, dy / R_
    nzb = np.sqrt(np.clip(1 - nxb * nxb - nyb * nyb, 0, 1))
    Lb = np.array([-0.50, -0.55, 0.67])
    Lb /= np.linalg.norm(Lb)
    s = nxb * Lb[0] + nyb * Lb[1] + nzb * Lb[2]
    pic.put(disc, "pearl")
    pic.put(disc & (s <= 0.55), "steel1")
    pic.put(disc & (s <= 0.18), "grey")
    hot = disc & (((nxb + 0.30) / 0.24) ** 2 + ((nyb + 0.32) / 0.19) ** 2 <= 1)
    pic.put(hot, "cream")
    limb = disc & ak.dilate(~disc, 1)
    pic.put(limb & (nxb + nyb > 0.55), "red")
    ring_ = ak.dilate(disc, 1) & ~disc
    under = pic.idx.copy()
    dark_side = ring_ & (nxb + nyb > -0.2)
    pic.put(dark_side, "black")
    pic.put(ring_ & ~dark_side & (under == P["red"]), "wine")
    gl_x, gl_y = int(round(cx - 0.70 * R_)), int(round(cy - 0.70 * R_))
    glint = np.zeros((128, 128), bool)
    for k in range(0, 5):
        for ddx, ddy in ((k, 0), (-k, 0), (0, k), (0, -k)):
            if k < 2 or not disc[gl_y + ddy, gl_x + ddx]:
                pic.px(gl_x + ddx, gl_y + ddy, "cream" if k < 3 else "pearl")
                glint[gl_y + ddy, gl_x + ddx] = True

    # ---- a chip flying past in the foreground: green (red's complement, so
    # it pops off the rotor), cream edge spots running onto its face, a dark
    # inlay ring, its far side in the shade, outlined in black
    chip = on[CHIP]
    Rm = R.rot_z(CHIP_TILT[0]) @ R.rot_x(CHIP_TILT[1])
    q_ = (p - np.array(CHIP_AT)) @ Rm                            # into the chip's own frame
    ax = n @ Rm                                                  # its normals there
    face = chip & (np.abs(ax[..., 1]) > 0.7)
    rim_ = chip & ~face
    ang = np.degrees(np.arctan2(q_[..., 2], q_[..., 0])) % 360
    rad = np.hypot(q_[..., 0], q_[..., 2]) / CHIP_R
    cdif = np.clip((n * KEY).sum(-1), 0, 1)
    spot_ = ((ang + 15) // 30) % 2 == 0
    pic.put(chip, "felt2")
    pic.put(chip & (cdif < 0.45), "felt1")
    pic.put(rim_ & spot_, "cream")
    pic.put(rim_ & spot_ & (cdif < 0.45), "pearl")
    pic.put(face & (np.abs(rad - 0.86) < 0.10) & spot_, "cream")
    pic.put(face & (np.abs(rad - 0.60) < 0.07), "felt1")
    pic.put(ak.dilate(chip, 1, diag=True) & ~chip, "black")

    # it was flicked up from the lower right: speed lines behind it
    cys, cxs = np.nonzero(chip)
    ccx, ccy = cxs.mean(), cys.mean()
    dvx, dvy = CHIP_FLY
    L_ = np.hypot(dvx, dvy)
    dvx, dvy = dvx / L_, dvy / L_
    for off, s0, ln in ((-5.0, 3, 7), (0.0, 1, 11), (5.0, 4, 6)):
        ox_, oy_ = -dvy * off, dvx * off
        # from the chip's edge outward along the flight's back direction
        k0 = 0
        cd_ = ak.dilate(chip, 1, diag=True)

        def inside(k):
            x_, y_ = int(ccx + ox_ + dvx * k), int(ccy + oy_ + dvy * k)
            return 0 <= x_ < 128 and 0 <= y_ < 128 and cd_[y_, x_]
        while k0 < 40 and inside(k0):
            k0 += 1
        pts = [(ccx + ox_ + dvx * (k0 + s0 + t), ccy + oy_ + dvy * (k0 + s0 + t)) for t in np.linspace(0, ln, 30)]
        for x_, y_, t_ in raster(pts):
            if 0 <= x_ < 127 and 0 <= y_ < 127 and not chip[y_, x_]:
                pic.px(x_, y_, "steel1" if t_ < 0.5 else "grey")

    # ---- lone pixels (the glints, the ball, the chip and the lines kept)
    keep = ak.dilate(disc, 1, diag=True) | keep_star | (chip & pic.where("cream")) | speed | glint
    for x_, y_ in pings:
        keep[y_, x_] = True
    for need in (5, 4, 3):
        despeckle(pic, need, keep)

    # ---- the title
    m = ak.load_mask(TITLE)
    tx = ak.centred_x(m) - 1
    drawn = ak.title(pic, m, tx, TITLE_Y, fill=["gold2", "gold1", "gold0"], rows=TITLE_ROWS, hi=None, lo="gold1",
                     extrude=dict(dx=1, dy=1, depth=3, colours=["gold0", "wine", "wine"]),
                     shadow=dict(dx=1, dy=2, colour="black"))
    M = ak.place(m, tx, TITLE_Y)
    lab = letters(M)                                              # each letter parted from its neighbours' extrusion
    allE = drawn["extrude"]
    for i in range(1, lab.max() + 1):
        Mi = lab == i
        Ei = np.zeros_like(Mi)
        for k in range(1, 4):
            Ei |= ak.shift(Mi, k, k)
        Ei &= ~M
        pic.put(ak.dilate(Mi, 1) & ~Mi & allE & ~Ei, "black")
    hz = M & (YY == TITLE_Y + HORIZON) & ak.shift(M, -1, 0)       # the horizon, short of each stroke's right edge
    pic.put(hz, "gold0")
    top = M & ~ak.shift(M, 0, 1)                                  # the light on the top edges
    run = top & ak.shift(top, 1, 0) & ak.shift(top, -1, 0)
    run = run | ak.shift(run, 1, 0) | ak.shift(run, -1, 0)
    pic.put(run & top, "cream")
    despeckle(pic, 3, ~drawn["all"])                              # the italic's stair-step leftovers
    for gx_, gy_ in GLINTS:                                       # catch-lights centred on the corners
        gx_, gy_ = gx_ + tx, gy_ + TITLE_Y
        ak.sparkle(pic, gx_, gy_, 2, "cream")
    return pic.image()


def title_lines():
    """The title's lettering as drawn here, and its depth, for the title
    screen (tools/titleart.py: the game paints it in the house gold)."""
    return [dict(mask=ak.load_mask(TITLE), depth=3, side="wine")]


if __name__ == "__main__":
    import boxart
    print(boxart.save(draw(), HERE.parent / "docs" / "cart.png"))
