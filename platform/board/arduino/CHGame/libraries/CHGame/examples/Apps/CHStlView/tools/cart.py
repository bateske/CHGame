r"""docs/cart.png, CHStlView's cover in the visual menu (docs/cover-art.md).
`chgame boxart` redraws it; edit this, not the PNG.

THE BRIEF
  Message: a spy's gadget for 3D models. The agent holds out his gloved
  fist and his diver's watch throws the model off the card into the air: a
  diamond in depth-cued wireframe (the near edges ice, the far ones dim
  teal behind the glass, as the app's X-RAY draws them), standing in the
  watch's cone of light, locked in the HUD's brackets.
  Composition:
      +----------------------------+
      |     S T L   V I E W E R    |  gold chrome in the top band, calm black round it
      |      [   /\/\/\/\   ]      |  the hologram: a wireframe diamond in scan lines,
      |      [   \  |  /   ]      |  a glow hugging it, two glints of fire, the app's
      |~~~~~~~~~~ \ | / ~~~~~~~~~~~|  brackets clear of the watch; the beam's edges
      | ____       \|/   _________ |  widen from the crystal to its girdle. Behind, a
      |(fist)====( watch )=c(sleeve|  teal haze at the horizon; under the arm a pool of
      | ""     #  grid  #   floor  |  the model's light on a clean converging grid
      +----------------------------+
  The arm crosses the frame from the sleeve (right edge) to the fist
  (left), which faces the key: the four fingers curled and stacked, each a
  rounded leather tube (a steel top, a navy body, black creases between),
  a short pearl dash where the key catches it (a cream glint on the
  first), the thumb along the bottom. The watch sits on the wrist in the
  middle, turned toward us: a navy dial, lume at 12, 3, 6 and 9, pearl
  hands at ten past ten, a teal bezel with the red pip at 12, a chrome
  rim, a steel case side in three flat planes. Between it and the sleeve
  the white shirt cuff and a red cufflink. The black glove and sleeve read
  in silhouette against the haze and the pool (a dark edge under them),
  with a teal rim where the hologram lights their whole top contour; the
  beam lifts the far bezel a level (it is in front of it). The eye climbs
  from the fist and the watch up the beam to the model and the title.
  Depth: the arm in front, the hologram over it, the grid and the pool far
  below, the haze at the horizon behind.
  Palette (11): the title's own gold0, gold1, gold2 (nothing else uses
  them); the hologram, the night, the bezel and the dial on one
  hue-shifted ramp: black, deep, navy, teal0, teal1, cyan, ice, cream;
  the leather on black, deep, navy, steel, pearl; the steel and the cotton
  on black, steel, grey, pearl, cream. Red only for the pip and the
  cufflink: the warm accents under the title.
  Lettering: CHARSET-DNS_FONT 5 (bmf), the face and the gold chrome of the
  SD card reader's cover, the other app (tools/art/title.txt credits it):
  bands of gold2 and gold1 (its counters kept open), a gold0 and teal0
  extrusion, a cream and gold0 bevel, one cream glint on the S.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import numpy as np  # noqa: E402
import artkit as ak  # noqa: E402
from artkit import render3d as R  # noqa: E402

TITLE = HERE / "art" / "title.txt"
TITLE_Y = 4
TITLE_ROWS = ["gold2"] * 6 + ["gold1"] * 3 + ["gold2"] * 2 + ["gold1"] * 5   # chrome: sky, horizon, ground
TITLE_EXTRUDE = ["gold0", "teal0"]
TITLE_GLINT = (1, 1)                       # the key glinting on the title (from its top-left)
TITLE_CLEAR = 27                           # nothing but black above this row, round the title

PAL = {
    "gold0": "#7A3408", "gold1": "#E4991C", "gold2": "#FFE27A",      # the title's own
    "deep": "#050C18", "navy": "#0C1E36",
    "teal0": "#0E4456", "teal1": "#1B7F8E", "cyan": "#43C8D2", "ice": "#B4F4F0",
    "steel": "#46566C", "pearl": "#C4D0DC",
}
GLOW = ["black", "deep", "navy", "teal0", "teal1", "cyan", "ice", "cream"]
CHROME = ["black", "steel", "grey", "pearl", "cream"]
WOOL = ["black", "deep", "navy", "teal0"]
COTTON = ["steel", "grey", "pearl", "cream"]
LEATHER = ["black", "deep", "navy", "steel", "pearl", "cream"]
LEATHER_KEY = ([0, 0.1, 0.2, 0.55, 1], [0.6, 1.2, 1.8, 2.5, 3.2])   # the key light to a level on it
TUBE = (0.34, 0.72)                        # a finger's steel top and navy body, down its run
LEATHER_EDGE = 0.30                        # where a part's top edge catches the key (steel)
YY, XX = np.mgrid[0:128, 0:128]
PX = (XX + 0.5, YY + 0.5)
ODD = (YY % 2) == 1                                          # the scan lines

GLOVE, CUFF, SLEEVE, CASE, BEZEL, GLASS, BAND, CROWN, THUMB, LINK, FING = range(11)
NMAT = FING + 4                            # the four fingers are FING..FING+3

# ---- the arm and the watch (the arm's frame: x along the forearm toward the hand, y up) ----

W_S = 1.50                                 # the watch's scale
W_Y = 0.58                                 # where its case sits on the wrist
WT = 0.43                                  # the bezel's top (watch units)
TILT = 18                                  # the forearm rises toward the hand (degrees)
ROLL = -30                                 # and turns about itself, the dial toward us
ARM = R.rot_y(180) @ R.rot_z(TILT) @ R.rot_x(ROLL)          # the hand to the left of the picture

E = np.radians(32)
YAW = np.radians(-25)
TARGET = (0.0, 0.8, 0.0)
DIST = 11.0
SHIFT = (-3, 20)                            # the lens shift (pixels)
CAM = R.Camera((TARGET[0] + DIST * np.cos(E) * np.sin(YAW), TARGET[1] + DIST * np.sin(E),
                TARGET[2] + DIST * np.cos(E) * np.cos(YAW)), TARGET, fov=50, shift=SHIFT)
KEY = -0.55 * CAM.r + 0.70 * np.array([0.0, 1.0, 0.0]) - 0.55 * CAM.f     # top left, a little from our side
KEY = KEY / np.linalg.norm(KEY)


def wpos(x, y, z):
    """A point in the watch's own units (y up from the case's back) in the world."""
    return ARM @ np.array([W_S * x, W_Y + W_S * y, W_S * z])


LENS = wpos(0.0, WT, 0.0)


def ell_cyl(hy, hz):
    """An elliptic cylinder along x (half sizes hy, hz), infinite."""
    def f(p):
        k = np.sqrt((p[:, 1] / hy) ** 2 + (p[:, 2] / hz) ** 2)
        return (k - 1) * min(hy, hz)
    return f


def slab_x(f, x0, x1):
    def g(p):
        return np.maximum(f(p), np.maximum(x0 - p[:, 0], p[:, 0] - x1))
    return g


FIST_AT = (1.55, 0.0, 0.0)                  # the fist's wrist on the arm, and its bend (degrees)
FIST_TURN = (12, -17, 4)                    # the fist turned about y, x, z (degrees) on the wrist
TH = -1                                    # the thumb's side (the arm's -z faces us)
KNUCKLES = [(-1.0, 0.27, 1.82), (-0.34, 0.31, 1.95), (0.32, 0.30, 1.92), (0.94, 0.26, 1.80)]   # across, radius, forward
KN_Y = 0.42


def fist_rot():
    return R.rot_y(FIST_TURN[0]) @ R.rot_x(FIST_TURN[1]) @ R.rot_z(FIST_TURN[2])


def fist():
    """A gloved fist, its wrist at the origin: the back of the hand, a row of
    four knuckles, each finger curled under its knuckle (its own material,
    for the creases between them), the thumb across their front."""
    back = R.xf(R.prim(R.box((0.95, 0.40, 1.08), 0.38), GLOVE), (0.95, 0.08, 0.0))
    fingers = []
    for i, (z, r, x) in enumerate(KNUCKLES):
        zz = z * -TH
        f_ = R.U(R.xf(R.prim(R.sphere(r), FING + i), (x, KN_Y, zz)),
                 R.prim(R.capsule((x, 0.36, zz), (x + 0.42, -0.18, zz), r), FING + i),
                 R.prim(R.capsule((x + 0.42, -0.24, zz), (x + 0.05, -0.74, zz), r * 0.95), FING + i))
        fingers.append(f_)
    palm = R.xf(R.prim(R.box((0.8, 0.35, 1.0), 0.3), GLOVE), (1.1, -0.45, 0))
    thumb = R.U(R.prim(R.capsule((0.55, -0.15, 1.15 * TH), (1.75, -0.38, 1.15 * TH), 0.32), THUMB),
                R.prim(R.capsule((1.75, -0.38, 1.15 * TH), (2.50, -0.48, 0.30 * TH), 0.29), THUMB))
    return R.SU(R.SU(back, R.U(*fingers), 0.14), R.SU(palm, thumb, 0.1), 0.05)


def scene():
    band = R.prim(slab_x(lambda p: np.abs(ell_cyl(0.76, 1.06)(p)) - 0.06, -0.48, 0.48), BAND)
    cuff = R.prim(slab_x(ell_cyl(0.84, 1.12), -3.2, -1.95), CUFF)
    sleeve = R.prim(slab_x(ell_cyl(1.10, 1.42), -14.0, -2.28), SLEEVE)
    link = R.xf(R.prim(R.box((0.10, 0.16, 0.10), 0.04), LINK), (-2.10, -0.05, 1.14 * TH))
    case = R.prim(R.lathe([(0.0, 0.0), (0.76, 0.0), (0.84, 0.05), (0.875, 0.15), (0.875, 0.30), (0.86, 0.34),
                           (0.0, 0.34)]), CASE)
    bezel = R.prim(R.lathe([(0.69, 0.33), (0.875, 0.33), (0.885, 0.38), (0.865, WT), (0.71, WT), (0.69, 0.40)]), BEZEL)
    glass = R.prim(R.lathe([(0.0, 0.33), (0.70, 0.33), (0.70, 0.41), (0.4, 0.425), (0.0, WT)]), GLASS)
    crown = R.xf(R.prim(R.cylinder(0.12, 0.08, 0.02), CROWN), (0.95, 0.19, 0), R.rot_z(90))
    lugs = [R.xf(R.prim(R.box((0.10, 0.08, 0.17), 0.03), CASE), (sx * 0.36, 0.14, sz * 0.84))
            for sx in (-1, 1) for sz in (-1, 1)]
    watch = R.xf(R.U(case, bezel, glass, crown, *lugs), (0, W_Y, 0), scale=W_S)
    wrist = R.prim(slab_x(ell_cyl(0.70, 0.98), -2.0, 2.2), GLOVE)
    hand = R.xf(fist(), FIST_AT, fist_rot())
    return R.xf(R.U(band, cuff, sleeve, link, watch, wrist, hand), (0, 0, 0), ARM)


def geometry(cam, sc):
    """What is at each pixel: its material (the majority of 2x2 rays), and at
    the pixel's centre the point, its normal, the view ray and whether the
    key light reaches it."""
    big = ak.Canvas("#000000")
    out = R.render(big, sc, cam, [R.Mat("#FFFFFF", spec=0.0)] * NMAT, ss=2, shadows=False, ao=False)
    mat = R.majority(out, big.s)
    one = ak.Canvas("#000000", ss=1)
    o1 = R.render(one, sc, cam, [R.Mat("#FFFFFF", spec=0.0)] * NMAT, lights=[(tuple(KEY), "#FFFFFF", 1.0)],
                  ambient="#000000", ss=None, shadows=True, ao=False)
    o, d = cam.rays((XX + 0.5).reshape(-1).astype(np.float64), (YY + 0.5).reshape(-1).astype(np.float64))
    dep = o1["depth"].reshape(-1)
    z = np.where(np.isfinite(dep), dep, 0)
    p = (o + d * z[:, None]).reshape(128, 128, 3)
    nrm = o1["normal"].astype(np.float64)
    occ = np.ones((128, 128))
    hit = np.isfinite(o1["depth"])
    occ[hit] = occlusion(sc, p[hit], nrm[hit])
    return dict(mat=mat, p=p, n=nrm, lit=o1["rgb"][..., 0].astype(np.float64), d=d.reshape(128, 128, 3), ao=occ)


def occlusion(sc, p, n, step=0.07, k=2.2):
    """How open each surface point is (1 open, 0 in a crease): the scene's
    distance sampled a few steps out along the normal."""
    occ = np.zeros(len(p))
    w = 1.0
    for i in range(1, 6):
        h = step * i
        occ += w * (h - sc(p + n * h)[0])
        w *= 0.7
    return np.clip(1 - k * occ, 0, 1)


# ---- the model: a diamond, faceted as an STL holds one ------------------------------------

GEM_S = 1.02
GEM_RISE = 1.75                            # the culet's height over the crystal (world units)
GEM_TILT = (-6, -12)                       # turned about z, then about x (degrees): it tumbles
GEM_SPIN = 12                              # and about its own axis
NG = 8                                     # the girdle's corners
GEM_FACE = (3.4, 3.4, 1.2)                 # the crown's and pavilion's level, light
GEM_ALT = 0.9                              # the brilliant's light/dark facets
GEM_SCAN = 1.0                             # the scan lines' dip
CASE_LIGHT = (200, 0.88, 0.0)               # the case's side: where the key is round it (degrees), pearl from, grey from
GLARE = (196, 232)                         # the crystal's glare: from, to (directions on the picture)
HALO = (1, 3, 8)                           # the model's glow: teal0, navy (in scan lines), deep out to (pixels)
RIM2 = 0.35                                # where the hologram's rim on the arm gets a second pixel
BEAM_EDGE = [(None, 0.12), ("cyan", 0.35), ("teal1", 0.8), (None, 1.0)]   # the beam's edges, from the lens up
HANDS = ((205, 0.36, 0.09), (322, 0.56, 0.065))    # hour, minute: direction on the picture (0 right, 90 down), length, width
BRACKET = (6, 3, 5)                            # the HUD's brackets: margin across, up and down, arm (pixels)

# ---- the room: a haze at the horizon, a grid floor converging under the model --------------

HORIZON = 82                               # the horizon's row
HAZE = (3.4, 12.0, 5.0)                    # the horizon's glow: level, its fall above, below (rows)
POOL = (62.0, 30.0, 3.8, 6.0)              # the model's light round the watch: radii, level, below the lens
FLOOR_A = 64.0                             # the floor's rows: y = HORIZON + A / depth
FLOOR_Z = (1.0, 1.4, 1.9, 2.6, 3.6, 5.2)    # the depths of its cross lines
FLOOR_K = 26                               # the converging lines' spacing at the bottom row (pixels)


def gem_mesh():
    """A brilliant, low-poly: a table, a crown, a girdle of NG corners, a
    pavilion down to the culet. y up."""
    v = []
    for i in range(NG):                                  # the girdle
        a = np.radians(GEM_SPIN + i * 360 / NG)
        v.append((1.25 * np.cos(a), 0.0, 1.25 * np.sin(a)))
    for i in range(NG):                                  # the table, half a step round
        a = np.radians(GEM_SPIN + (i + 0.5) * 360 / NG)
        v.append((0.72 * np.cos(a), 0.50, 0.72 * np.sin(a)))
    v.append((0.0, -1.45, 0.0))                          # the culet
    tri = []
    cul = 2 * NG
    for i in range(NG):
        j = (i + 1) % NG
        tri += [(i, j, NG + i), (NG + i, NG + j, j), (i, cul, j)]
    return np.array(v, np.float64), tri


def gem_world():
    """The gem in the world, balanced on its culet over the crystal."""
    V, F = gem_mesh()
    M = R.rot_z(GEM_TILT[0]) @ R.rot_x(GEM_TILT[1])
    W = V @ M.T * GEM_S
    return W - W[2 * NG] + LENS + np.array([0.0, GEM_RISE, 0.0]), F


def depth(p):
    return (np.asarray(p) - CAM.pos) @ CAM.f


# ---- helpers ------------------------------------------------------------------------------

def poly_mask(pts):
    return ak.polygon(PX, [tuple(q) for q in pts]) < 0


def cur_levels(pic, ramp):
    """What each pixel already is, as a level on `ramp` (-1 where it is not on it)."""
    cur = np.full((128, 128), -1)
    for k, nm in enumerate(ramp):
        cur[pic.where(nm)] = k
    return cur


def tube_pos(m):
    """For each pixel of m, where it lies down its column's run: 0 at the
    run's top, 1 at its bottom (a tube lit from above)."""
    up = np.zeros(m.shape, np.float64)
    dn = np.zeros(m.shape, np.float64)
    for y in range(1, 128):
        up[y] = np.where(m[y] & m[y - 1], up[y - 1] + 1, 0)
    for y in range(126, -1, -1):
        dn[y] = np.where(m[y] & m[y + 1], dn[y + 1] + 1, 0)
    return np.where(m, up / np.maximum(up + dn, 1), 0)


def top_of(m):
    """The mask's top contour (pixels with nothing of it above)."""
    return m & ~ak.shift(m, 0, 1)


def adist(a, b):
    return np.abs(((a - b) + 180) % 360 - 180)


FRAME = ((0, 3), (1, 2), (2, 1))           # (pixels in from the edge, levels down)


def frame_dark(pic):
    """Everything steps down its own ramp toward the picture's left, right
    and bottom edges, so the installed game's border sits on dark."""
    edge_d = np.minimum(np.minimum(XX, 127 - XX), 127 - YY)
    drop = np.zeros((128, 128), np.int64)
    for k, d_ in FRAME:
        drop[edge_d == k] = d_
    orig = pic.idx.copy()
    done = np.zeros((128, 128), bool)
    for ramp in (GLOW, CHROME, LEATHER, COTTON):
        lut = np.array([pic.pal[nm] for nm in ramp], np.uint8)
        for k, nm in enumerate(ramp):
            sel = (orig == pic.pal[nm]) & (drop > 0) & ~done
            pic.idx[sel] = lut[np.maximum(k - drop[sel], 0)]
            done |= sel


def draw():
    P = ak.Palette(PAL, ramps=[GLOW, CHROME, ["gold0", "gold1", "gold2", "cream"]])
    pic = ak.Picture.blank(P, "black")
    G = geometry(CAM, scene())
    mat, p, n, lit, dv, ao = G["mat"], G["p"], G["n"], G["lit"], G["d"], G["ao"]
    on = {k: mat == k for k in range(NMAT)}
    solid = mat >= 0
    detail = np.zeros((128, 128), bool)                         # hand-drawn pixels: never despeckled

    def recorded(fn):
        def f(*a, **k):
            before = pic.idx.copy()
            r = fn(pic, *a, **k)
            detail[...] |= pic.idx != before
            return r
        return f
    ink, patch, glint = recorded(ak.ink), recorded(ak.patch), recorded(ak.glint)

    lx, ly = CAM.project(LENS)
    V, F = gem_world()
    xy = np.array([CAM.project(v) for v in V])
    dz = depth(V)
    gem = poly_mask(ak.hull(list(map(tuple, xy))))
    gc0 = V[:2 * NG].mean(0)                                    # the model's centre
    gc = V[:NG].mean(0)                                         # the girdle's centre
    gx_, gy_ = CAM.project(gc)

    # ---- light: the key (with shadows) and the hologram's own, from the model
    shadowed = (lit < 0.02) & ((n * KEY).sum(-1) > 0.05)
    dif = np.clip((n * KEY).sum(-1), 0, 1) * ~shadowed
    hv = gc0 - p
    hd = np.linalg.norm(hv, axis=-1)
    hl = np.clip((n * hv).sum(-1) / np.maximum(hd, 1e-6), 0, 1)

    # ---- the room: black under the title, a teal haze at the horizon
    # (behind the arm's top), the model's light pooled round the watch far
    # below, a clean grid on the floor converging under the model
    H = HORIZON
    sky = YY < H
    pool = POOL[2] * np.clip(1 - np.hypot((XX + 0.5 - lx) / POOL[0], (YY + 0.5 - ly - POOL[3]) / POOL[1]), 0, 1) ** 1.3
    hz = np.where(sky, HAZE[0] * np.exp(-(H - 0.5 - YY) / HAZE[1]), HAZE[0] * np.exp(-(YY + 0.5 - H) / HAZE[2]))
    room = np.maximum(hz, pool) * (YY >= TITLE_CLEAR)
    ak.by_level(pic, ak.terrace(room, 0.15), GLOW[:5], where=YY >= 0)
    fl = ~sky
    grid = np.zeros((128, 128), np.float64)                     # each grid pixel's level
    for z_ in FLOOR_Z:
        y_ = int(round(H + FLOOR_A / z_))
        if H < y_ < 128:
            grid[y_, :] = np.maximum(grid[y_, :], 2.0 + 1.0 * (y_ > H + 14))
    vx = lx
    for i in range(-9, 10):
        bx = vx + i * FLOOR_K
        for x_, y_ in ak.line_px([(vx + 0.5 * i, H + 0.5), (bx, 127.5)]):
            if 0 <= x_ < 128 and H + 6 <= y_ < 128:
                grid[y_, x_] = max(grid[y_, x_], 2.0 + 1.0 * (y_ > H + 16))
    gap = ak.dilate(solid, 2, diag=True)                       # a dark gap round the arm
    lv_g = np.where(grid > 0, grid, 0).astype(np.int64)
    gm = (grid > 0) & ~gap & fl
    ak.put_levels(pic, gm, np.maximum(lv_g, cur_levels(pic, GLOW)), GLOW)

    # ---- the arm: black wool and black leather, read in silhouette against
    # the haze and the pool. The sleeve: the hologram lights its top teal;
    # the cuff white, the cufflink red
    pa = p @ ARM
    fall = np.clip(1.25 - 0.08 * hd, 0, 1)
    hlv = hl * fall
    sl = on[SLEEVE]
    cu = on[CUFF]
    leather = on[GLOVE] | on[THUMB] | (mat >= FING)
    crease = 2.2 * (1 - ao)
    ak.by_level(pic, np.clip(ak.terrace(0.5 + 1.2 * dif + 2.2 * hlv ** 1.5 - crease, 0.1), 0, 3), WOOL, where=sl)
    ak.put_levels(pic, cu, np.clip(np.round(1.2 + 1.6 * dif - crease), 0, 2).astype(np.int64), COTTON)
    pic.put(on[LINK], "red")

    # the leather: the back of the hand and the wrist by the key (navy where
    # it reaches them, deep where they turn away, black in the creases); the
    # fingers and the thumb as rounded tubes lit from above (a steel top, a
    # navy body, a deep underside), each with a short pearl dash toward the
    # key, the first a cream glint
    body = np.interp(dif, LEATHER_KEY[0], LEATHER_KEY[1]).round().astype(np.int64) - (ao < 0.6)
    ak.put_levels(pic, leather, np.clip(body, 0, 3), LEATHER)
    pic.put(on[GLOVE] & top_of(on[GLOVE]) & (dif > LEATHER_EDGE) & ~top_of(solid), "steel")
    tubes = [on[FING + i] for i in range(4)] + [on[THUMB]]
    first = int(np.argmin([np.nonzero(m_)[0].min() if m_.any() else 999 for m_ in tubes]))   # the top one
    for k_, pm in enumerate(tubes):
        t_ = tube_pos(pm)
        ak.put_levels(pic, pm, np.where(t_ <= TUBE[0], 3, np.where(t_ <= TUBE[1], 2, 1)), LEATHER)
        top_ = pm & (t_ <= TUBE[0])
        if not top_.any():
            continue
        ys_, xs_ = np.nonzero(top_)
        far = xs_.min() + 2                                     # toward the front of the fist (the key)
        row = top_ & ak.shift(top_of(pm), 0, 1) & (XX >= far) & (XX <= far + 2)
        pic.put(row, "pearl")
        detail[...] |= row
        if k_ == first and row.any():
            yy_, xx_ = np.nonzero(row)
            pic.px(xx_[0], yy_[0], "cream")

    # the creases between the fingers, and round the thumb
    for a_ in range(FING, FING + 4):
        for b_ in list(range(a_ + 1, FING + 4)) + [THUMB]:
            ma, mb = on[a_], on[b_]
            pic.put(ma & (ak.shift(mb, 1, 0) | ak.shift(mb, -1, 0) | ak.shift(mb, 0, 1) | ak.shift(mb, 0, -1)), "black")

    # the hologram's light along the arm's top contour: one continuous rim
    # where the cloth and the leather face the model
    arm = sl | leather | cu | on[LINK]
    out_ = ~solid
    top1 = arm & (ak.shift(out_, 0, 1) | (ak.shift(out_, 1, 0) & (XX > lx)) | (ak.shift(out_, -1, 0) & (XX < lx)))
    top1 &= ak.shift(out_, 0, 1) | ak.shift(out_, 0, 2) | ak.shift(out_, 1, 1) | ak.shift(out_, -1, 1)
    top2 = (sl | leather) & ak.shift(top1, 0, 1) & ~top1 & (hlv > RIM2)   # nearer the model the rim is wider
    pic.put(top2, "teal0")
    pic.put(top1 & (sl | leather) & (hl > 0.02), "teal1")
    ak.selout(pic, solid, "black")                             # a dark edge under and right of the arm
    pic.put(top1 & cu, "pearl")

    # ---- the watch's own frame
    q = (p @ ARM - np.array([0.0, W_Y, 0.0])) / W_S
    rq = np.hypot(q[..., 0], q[..., 2])

    def wpt(r_, a_, y_=WT):
        a_ = np.radians(a_)
        return CAM.project(wpos(r_ * np.cos(a_), y_, r_ * np.sin(a_)))

    def ring_pts(r_, y_=WT, a0=0.0, a1=360.0, n_=720):
        return [wpt(r_, t, y_) for t in np.linspace(a0, a1, n_)]

    def disc(r_, y_=WT):
        return poly_mask(ring_pts(r_, y_, n_=240))

    def scr_ang(x_, y_):
        """The angle on the picture round the dial's centre (0 right, 90 down)."""
        return np.degrees(np.arctan2(y_ - ly, x_ - lx)) % 360

    angs = np.arange(0.0, 360.0, 0.5)                           # the dial's 12 at the picture's top
    pts_ = np.array([wpt(0.6, a_) for a_ in angs])
    up_ = pts_[:, 1] < ly
    a12 = angs[up_][np.argmin(np.abs(pts_[up_, 0] - lx))]

    watch = on[CASE] | on[BEZEL] | on[GLASS] | on[CROWN]
    topm = disc(0.878) & watch
    glass_m = disc(0.705) & watch
    insert = topm & ~glass_m
    sa = scr_ang(XX + 0.5, YY + 0.5)

    # the case's side, the lugs, the crown and the bracelet: polished steel
    # in three flat planes by the key, a black edge under it
    lug = on[CASE] & (rq > 0.90)
    side_ = watch & ~topm & ~on[CROWN] & ~lug
    steel_ = side_ | lug | on[CROWN] | on[BAND]
    f_side = np.cos(np.radians(sa - CASE_LIGHT[0]))            # round the case: lit toward the key
    ak.put_levels(pic, steel_, np.where(f_side > CASE_LIGHT[1], 3, np.where(f_side > CASE_LIGHT[2], 2, 1)), CHROME)
    pic.put(steel_ & ~ak.shift(solid, 0, -1), "black")
    pic.put(on[BAND] & (np.abs(np.abs(pa[..., 0]) - 0.17) < 0.035), "black")      # three rows of links

    # ---- the bezel: a glossy teal insert, lit on the side toward the key and
    # the model, darker toward us; pearl ticks at the quarters, the red pip at
    # 12; a chrome rim, bright toward the key; a black step down to the crystal
    sheen = np.cos(np.radians(sa - 240))
    ak.put_levels(pic, insert, np.where(sheen > 0.2, 4, 3), GLOW)
    for k in (3, 6, 9):
        ink([wpt(0.76, a12 + k * 30), wpt(0.84, a12 + k * 30)], "pearl", where=insert)
    for x_, y_, t_ in ak.raster(ring_pts(0.868)):
        if 0 <= x_ < 128 and 0 <= y_ < 128 and watch[y_, x_]:
            f_ = 1 - adist(scr_ang(x_ + 0.5, y_ + 0.5), 215) / 80
            pic.px(x_, y_, "cream" if f_ > 0.8 else "pearl" if f_ > 0.25 else "grey" if f_ > -0.5 else "steel")
    tx_, ty_ = wpt(0.79, a12)                                   # the red pip at 12
    patch(int(round(tx_)) - 1, int(round(ty_)) - 1, ["rrr", ".r."], {"r": "red"})

    # ---- the dial: navy, deep round its edge; lume at 12, 3, 6 and 9; the
    # hands in its lower half, clear of the beam (twenty to five)
    inner = ak.erode(glass_m, 1, diag=True)
    pic.put(glass_m & ~inner, "black")                          # the step down to the crystal
    ak.put_levels(pic, inner, np.where(ak.erode(inner, 1, diag=True), 2, 1), GLOW)
    for k in range(0, 12, 3):
        x_, y_ = wpt(0.58, a12 + k * 30)
        xi, yi = int(np.floor(x_)), int(np.floor(y_))
        patch(xi - (1 if k in (0, 6) else 0), yi - (0 if k in (0, 6) else 1),
              ["iii", "iii"] if k == 0 else ["ii", "ii"], {"i": "ice"})

    def dial_angle(screen_deg, r_=0.5):
        """The dial angle whose point lies in that direction on the picture."""
        return angs[np.argmin(adist(np.array([scr_ang(*wpt(r_, a_)) for a_ in angs]), screen_deg))]

    def hand(a_, r_, w_, tail=0.10):
        a_ = np.radians(a_)
        u = np.array([np.cos(a_), np.sin(a_)])
        v_ = np.array([-u[1], u[0]])
        pts = [-u * tail + v_ * w_ * 0.6, u * r_ * 0.8 + v_ * w_, u * r_, u * r_ * 0.8 - v_ * w_, -u * tail - v_ * w_ * 0.6]
        return [CAM.project(wpos(a[0], WT, a[1])) for a in pts]
    g0_, g1_ = dial_angle(GLARE[0], 0.64), dial_angle(GLARE[1], 0.64)   # the key's reflection on the crystal
    if adist(g0_, g1_) > 0:
        span = np.linspace(g0_, g0_ + ((g1_ - g0_ + 180) % 360 - 180), 40)
        ink([wpt(0.64, t_) for t_ in span], None, colours=[("cyan", 0.25), ("ice", 0.75), ("cyan", 1.0)], where=inner)
    for sd_, r_, w_ in HANDS:
        hm = poly_mask(hand(dial_angle(sd_), r_, w_))
        pic.put(ak.dilate(hm, 1) & inner & ~hm, "black")
        pic.put(hm, "pearl")

    # ---- the beam: a soft column of light from the crystal widening up round
    # the model; a veil over the watch's top (one level up), in front of it
    rim_ = np.array([CAM.project((gc[0] + 1.55 * GEM_S * np.cos(t), gc[1], gc[2] + 1.55 * GEM_S * np.sin(t)))
                     for t in np.linspace(0, 2 * np.pi, 181)])
    cone = poly_mask(ak.hull(list(map(tuple, rim_)) + [(lx, ly)])) & (YY + 0.5 >= gy_ - 2)
    over = cone & topm & (YY + 0.5 < ly)
    cone &= ~solid
    dd = ak.distance_px(~cone, 8).astype(np.float64)            # how far in from its edge
    ty = np.clip((YY + 0.5 - gy_) / max(ly - gy_, 1), 0, 1)     # 0 at the girdle, 1 at the lens
    bl = (2.4 + 2.0 * ty ** 1.2) * np.clip(dd / 3.0, 0, 1)
    lv = np.maximum(ak.levels(bl, True), cur_levels(pic, GLOW))
    ak.put_levels(pic, cone & ~gem, lv, GLOW)
    cur = cur_levels(pic, GLOW)
    ak.put_levels(pic, over & (cur >= 1) & (cur < 4), cur + 1, GLOW)
    ang = np.unwrap(np.arctan2(rim_[:, 1] - ly, rim_[:, 0] - lx))  # its edges: the tangents from the lens
    for e_ in (tuple(rim_[np.argmax(ang)]), tuple(rim_[np.argmin(ang)])):
        ink([(lx, ly), e_], None, colours=BEAM_EDGE, where=~solid & ~gem)
    lxi, lyi = int(np.floor(lx)), int(np.floor(ly))
    patch(lxi - 3, lyi - 1, ["..cic..", "tciwict", "..cic.."], {"t": "teal1", "c": "cyan", "i": "ice", "w": "cream"})

    # ---- the model: a halo hugging it, its facets in scan lines (a
    # brilliant's light/dark pattern, the table brightest), then every edge by
    # depth: the far ones dim behind the glass (the app's X-RAY), the near ones ice
    dg = ak.distance_px(gem, HALO[2] + 1).astype(np.float64)
    halo_lv = np.where(dg <= HALO[0], 3, np.where(dg <= HALO[1], 2, np.where(dg <= HALO[2], 1, 0)))
    halo_lv = np.where(ODD & (dg > HALO[0]) & (dg <= HALO[1]), halo_lv - 1, halo_lv)   # scan lines near it
    ak.put_levels(pic, ~gem & ~solid, np.maximum(halo_lv, cur_levels(pic, GLOW)), GLOW)
    face_front, face_lv = {}, {}
    for i, (a, b, c) in enumerate(F):
        nrm = np.cross(V[b] - V[a], V[c] - V[a])
        nrm /= np.linalg.norm(nrm)
        cen = V[[a, b, c]].mean(0)
        if nrm @ (cen - gc0) < 0:
            nrm = -nrm
        face_front[i] = nrm @ (CAM.pos - cen) > 0
        g_, kind = i // 3, i % 3
        f = np.clip(nrm @ KEY, 0, 1)
        alt = GEM_ALT if (g_ + kind) % 2 == 0 else -GEM_ALT
        face_lv[i] = (GEM_FACE[0] if kind < 2 else GEM_FACE[1]) + GEM_FACE[2] * f + alt
    for i in sorted(range(len(F)), key=lambda i: -dz[list(F[i])].mean()):
        if not face_front[i]:
            continue
        m = poly_mask(xy[list(F[i])])
        fl_ = face_lv[i]
        ak.put_levels(pic, m, np.clip(np.round(np.where(ODD, fl_ - GEM_SCAN, fl_)), 2, 5).astype(np.int64), GLOW)
    tab = poly_mask(xy[NG:2 * NG])
    tcx = xy[NG:2 * NG, 0].mean()
    lv = np.where(XX + 0.5 < tcx, 5, 4) - np.where(ODD, 1, 0)
    ak.put_levels(pic, tab, lv.astype(np.int64), GLOW)
    edge_front = {}
    for i, f_ in enumerate(F):
        for j in range(3):
            e = tuple(sorted((f_[j], f_[(j + 1) % 3])))
            edge_front.setdefault(e, []).append(face_front[i])
    z0, z1 = dz.min(), dz.max()
    back = [e for e, fr in edge_front.items() if not any(fr)]
    front = [e for e, fr in edge_front.items() if all(fr)]
    sil = [e for e, fr in edge_front.items() if any(fr) and not all(fr)]
    for a, b in sorted(back, key=lambda e: -(dz[e[0]] + dz[e[1]])):
        ink([xy[a], xy[b]], "teal1", where=~tab)
    for a, b in sorted(front, key=lambda e: -(dz[e[0]] + dz[e[1]])):
        t = 1 - ((dz[a] + dz[b]) / 2 - z0) / (z1 - z0)
        ink([xy[a], xy[b]], "cyan" if t < 0.55 else "ice")
    for a, b in sil:
        ink([xy[a], xy[b]], "ice")

    # ---- the HUD: brackets locked on the model, as the app draws them
    bx0, by0 = int(np.floor(xy[:, 0].min())) - BRACKET[0], int(np.floor(xy[:, 1].min())) - BRACKET[1]
    bx1, by1 = int(np.ceil(xy[:, 0].max())) + BRACKET[0], int(np.ceil(xy[:, 1].max())) + BRACKET[1]
    L_ = BRACKET[2]
    for cx_, cy_, sx_, sy_ in ((bx0, by0, 1, 1), (bx1, by0, -1, 1), (bx0, by1, 1, -1), (bx1, by1, -1, -1)):
        ink([(cx_ + 0.5, cy_ + 0.5), (cx_ + sx_ * L_ + 0.5, cy_ + 0.5)], "cyan")
        ink([(cx_ + 0.5, cy_ + 0.5), (cx_ + 0.5, cy_ + sy_ * L_ + 0.5)], "cyan")

    for need in (5, 4):
        ak.despeckle(pic, need, keep=detail)

    # ---- sparkle: the diamond's fire on the corner the key catches, a spark
    # on another, the chrome rim's glint toward the key
    k0 = NG + int(np.argmin(xy[NG:2 * NG, 0] + 0.8 * xy[NG:2 * NG, 1]))
    k1 = int(np.argmax(xy[:NG, 0]))
    glint(int(xy[k0][0]), int(xy[k0][1]), 3, tip="ice")
    glint(int(xy[k1][0]), int(xy[k1][1]), 2, tip="ice")

    # ---- the frame: the outer rows and columns step down into the dark
    frame_dark(pic)

    ak.despeckle(pic, 5, keep=detail)
    ak.despeckle(pic, 3, keep=detail, within=ak.dilate(solid, 1, diag=True))   # the arm and the watch: no stray pixels

    # ---- the title
    m = ak.load_mask(TITLE)
    tx = ak.centred_x(m)
    res = ak.title(pic, m, tx, TITLE_Y, fill=None, rows=TITLE_ROWS, hi=None, lo=None,
                   extrude=dict(dx=1, dy=1, depth=2, colours=TITLE_EXTRUDE), shadow=dict(dx=1, dy=2, colour="black"))
    M = ak.place(m, tx, TITLE_Y)
    # the counters between the bars stay open: the back depth goes black there
    ext = res["extrude"] & pic.where(TITLE_EXTRUDE[-1])
    above = ak.shift(M, 0, 1) | ak.shift(M, 0, 2)
    below = ak.shift(M, 0, -1) | ak.shift(M, 0, -2)
    pic.put(ext & above & below, "black")
    hi_, lo_ = ak.bevel_contour(pic, M, "cream", "gold0")
    # a left edge running down to the right (the V, the R's leg) is lit,
    # though each of its steps also faces down
    out = ak.outside_of(M)
    step = lo_ & ak.shift(out, 1, 0) & ak.shift(out, 0, -1) & ak.shift(M, -1, -1)
    pic.put(step, "cream")
    gx_, gy_ = tx + TITLE_GLINT[0], TITLE_Y + TITLE_GLINT[1]     # the key glinting on the S's corner
    ak.glint(pic, gx_, gy_, 3, tip="gold2")
    return pic.image()


if __name__ == "__main__":
    import boxart
    print(boxart.save(draw(), HERE.parent / "docs" / "cart.png"))
