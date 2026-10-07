"""docs/cart.png, Boardwalk's cover in the visual menu (docs/cover-art.md).
`chgame boxart` redraws it; edit this, not the PNG.

THE BRIEF
  Message: build it, own it, cash in. Your token hops along the priciest
  street on the board: houses on it, a hotel lit up at its end, and the rent
  raining down on you.

  Composition (a thumbnail in words):
  - Night on the board, camera low and three-quarter on the street's near
    end; the street of tiles runs away to the right; one warm key from the
    top left. Three reads left to right along it: the token, the houses, the
    hotel; the money arcs back over them from the hotel to the token.
  - Focal point: the cherry pair, the player's token and the hero, big on
    the left, caught at the top of a hop along their street: glossy (red, a
    wine terminator with a narrow checkered seam, a black core, a navy
    bounce underneath, a cream specular with an ivory bloom on the lit side),
    grinning (big cream eyes with the pupils turned up at the money, raised
    brows, a toothy grin); the back one winks. Their stems trail back up and
    to the left, two whoosh arcs (curved, tapered at both ends, grey to navy,
    different lengths) trail behind, and their shadow lies on the tile just
    under them.
  - Middle ground: two green houses on the blue band (each a lit grn2 gable
    to us with a black door and a lit window, a mid side and roof, a black
    eave line), a dark gap between them and clear of the cherries: build it.
    Then the hotel looming at the right: a wine end wall lit toward the
    cherries (a red cornice, warm windows), its long facade in shade (its
    windows set in black bands), a blue slate roof, ivory bargeboards, a
    marquee of six separate bulbs over a lit door and a neon blade sign on
    the corner, HOTEL, stacked: the bulbs and the letters are the rainbow
    index, so they cycle in the Rainbow bootloader (magenta in the Static
    one). Its door spills a little light on the street.
  - Bills fountain off the hotel's roof and arc over onto the cherries,
    turning (45, 26.6, 0, -26.6, -45 degrees: clean steps) and growing as
    they near, a faint tapered trail behind them, two glints: cash in.
  - The ground: the street's tiles, flat (one level a tile, bounded by black
    seams), each with a Boardwalk-blue colour band across its inner end and
    a price strip a step darker at its outer end; the tile under the
    cherries lit grey with a small cream hot spot (an ivory rim) up and left
    of their shadow (a navy core, a grey rim), the next tiles navy, the rest
    dark; the board's lip one navy line; the bottom rows and right edge in
    the dark for the menu's border.
  - The night, the table and the board's far reaches: one calm dark, black
    under the title, a dim haze along the horizon and behind the cherries.
  - The title across the top band on calm black: a Victorian wood-type face
    (bracketed slab serifs: an old boardwalk sign), gold leaf (a short pale
    sky, deep amber, a dark horizon under the middle, amber below), its
    depth dark navy (three steps; no lighter blue in it), a cream bevel on
    its outer top and left edges and a gold0 one bottom and right, a black
    outline and drop shadow, glints on the B and the K. It is the first read;
    the cherries the second, the hotel and its neon the third.

PALETTE (11 own + cream, grey, black, red; rainbow on purpose)
  navy0 navy1 blue   night, haze, the board, the colour band, the hotel's
                     slate roof, the cherries' bounce, the sign's panel; navy1
                     the title's depth
  grn0 grn1 grn2     the houses, the bills, the stems and leaf
  wine               the hotel's walls, the cherries' terminator, mouths
  ivory (a peach)    warm windows, the hot spot's rim, the specular's bloom,
                     the bargeboards
  gold0 gold1 gold2  the title's own: nothing else uses them
  fixed: cream (the hot spot, speculars, eyes, teeth, bill borders, glints),
  grey (the lit tile, the whoosh arcs), black (outlines, seams, the void),
  red (the cherries, their tongues, the hotel's cornice); rainbow: the neon
  sign and the bulbs.

FONT  title.txt: TWO HUNDRED AND TWENTY FOUR, from the bmf collection
      (author and terms not stated: a `?` face, chosen because no clear-terms
      face at this size has its heavy bracketed serifs). Narrowed by hand to
      fit (a column out of four counters and the L's foot, the outer serif
      tips trimmed), the B and O parted, the D and W parted (a column out of
      the W's middle stroke).
"""
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import artkit as ak  # noqa: E402
from artkit import render3d as R  # noqa: E402

TITLE = HERE / "art" / "title.txt"

COL = {
    "navy0": "#0A0E2C", "navy1": "#1C2A66", "blue": "#2E54CC",
    "grn0": "#0C4630", "grn1": "#2C9642", "grn2": "#A4DE58",
    "wine": "#6C1226", "ivory": "#E2B496",
    "gold0": "#A04E0C", "gold1": "#F0A818", "gold2": "#FFE47A",
}

# ---- the scene (world: x along the street, away to the right; y up; z across
# it, 0 the board's outer edge (near us), -D its inner edge, where the colour
# band is) -------------------------------------------------------------------------------
W, D, BAND, PRICE = 0.6, 1.6, 0.5, 0.26                # a tile: width, depth; its colour band, its price strip
CAM = dict(pos=(-0.2, 1.0, 1.6), target=(1.0, 0.3, -1.3), fov=60.0, shift=(6, 14))
HOUSES = [(1.0, 1.12), (1.56, 1.12)]                       # (x, scale): tile centres on the band
HROT = -8.0                                                # the houses turned a little, to show their lit side
HOTEL = dict(x=2.28, w=0.68, d=0.56, h=1.42, roof=0.3)
SLAB = 0.08                                               # the board's thickness
CHER = dict(back=(25, 57, 15), front=(45, 73, 17))        # (x, y, r) on the picture
SHADOW, SHADOW_R = (49, 104), (0.33, 0.18)                   # the cherries' shadow: where (picture), radii (world)
POOLC, HOT, LIT = (44, 101), 0.34, 3.0                             # the light: its centre (picture), the hot spot's radius (world)

TILE, TABLE, TBODY, TROOF, HOUSE0 = range(5)              # house k: body HOUSE0 + 2k, roof HOUSE0 + 2k + 1
TILE_R = ["black", "navy0", "navy1", "grey", "ivory", "cream"]
SKY_R = ["black", "navy0", "navy1"]
BAND_R = ["black", "navy0", "navy1", "blue"]
GRN_R = ["black", "grn0", "grn1", "grn2"]
INK = {"k": "black", "c": "cream", "i": "ivory", "r": "red", "w": "wine", "n": "navy0", "N": "navy1",
       "b": "blue", "g": "grn0", "G": "grn1", "l": "grn2", "e": "grey", "R": "rainbow"}


def house(k, x, s):
    """House k on the band, its gable to us, its ridge across the street."""
    w, d, h, rh = 0.36 * s, 0.34 * s, 0.30 * s, 0.24 * s
    z = -D + BAND / 2
    body = R.prim(R.box((w / 2, h / 2, d / 2), 0.01), HOUSE0 + 2 * k)
    tri = lambda X, Y: ak.polygon((X, Y), [(-w / 2 - 0.03, 0.0), (w / 2 + 0.03, 0.0), (0.0, rh)])
    roof = R.xf(R.prim(R.extrude(tri, d / 2 + 0.03), HOUSE0 + 2 * k + 1), (0, h / 2 - 0.01, 0))
    return R.xf(R.U(body, roof), (x, h / 2, z), R.rot_y(HROT))


def hotel():
    """The hotel: its long facade to us, a gable roof, the ridge along the street."""
    w, d, h, rh = HOTEL["w"], HOTEL["d"], HOTEL["h"], HOTEL["roof"]
    x, z = HOTEL["x"], -D + d / 2 - 0.02
    body = R.xf(R.prim(R.box((w / 2, h / 2, d / 2), 0.012), TBODY), (x, h / 2, z))
    tri = lambda X, Y: ak.polygon((X, Y), [(-d / 2 - 0.04, 0.0), (d / 2 + 0.04, 0.0), (0.0, rh)])
    roof = R.xf(R.prim(R.extrude(tri, w / 2 + 0.03), TROOF), (x, h - 0.01, z), R.rot_y(90))
    return R.U(body, roof)


def bill(pic, cx, cy, w, h, ang, keep=None):
    """A banknote flying: a w x h rectangle turned `ang` degrees (the clean
    pixel angles 0, 26.6, 45 step evenly); a cream border, a green field lit
    on its upper half, a dark oval. Outlined in black, kept to `keep`.
    Returns its mask."""
    yy, xx = np.mgrid[0:128, 0:128]
    a = np.radians(ang)
    ux, uy = np.cos(a), np.sin(a)
    px, py = xx + 0.5 - cx, yy + 0.5 - cy
    u = (px * ux + py * uy) / w + 0.5
    v = (-px * uy + py * ux) / h + 0.5
    m = (u >= 0) & (u < 1) & (v >= 0) & (v < 1)
    if keep is not None:
        m &= keep
    inner = ak.erode(m, 1)
    border = m & ~inner
    oval = inner & (((u - 0.5) / 0.17) ** 2 + ((v - 0.5) / 0.3) ** 2 < 1)
    pic.put(ak.dilate(m, 1) & ~m & (keep if keep is not None else True), "black")
    pic.put(inner, "grn1")
    pic.put(inner & (v < 0.42), "grn2")
    pic.put(border, "cream")
    pic.put(oval, "grn0")
    return m


def cher_mask(X1, Y1):
    m = np.zeros(X1.shape, bool)
    for cx, cy, r in (CHER["back"], CHER["front"]):
        m |= np.hypot(X1 - cx, Y1 - cy) < r
    return m


def paint_stems(pic, X1, Y1):
    """The stems, behind the balls: from each crown up and back to a knot
    (trailing the hop), a leaf off the knot, pointing back."""
    (bx, by_, br), (fx, fy, fr) = CHER["back"], CHER["front"]
    P1 = (X1, Y1)
    J = (bx - 7.0, by_ - br - 10.0)
    stem = np.zeros(X1.shape, bool)
    for (cx, cy, r), c1 in (((bx, by_, br), (bx - 1.0, by_ - br - 5.0)), ((fx, fy, fr), (fx - 3.0, fy - fr - 12.0))):
        pts = ak.bezier((cx + 0.5, cy - r + 2.0), c1, J, n=30)
        stem |= ak.polyline(P1, pts, 1.0) < 0
    leaf_d = ak.ellipse(P1, J[0] - 6.0, J[1] + 1.5, 6.5, 2.8, angle=20)
    leaf = leaf_d < 0
    pic.put(ak.dilate(stem | leaf, 1) & ~(stem | leaf), "black")
    pic.put(stem, "grn1")
    pic.put(stem & ~ak.shift(stem, 1, 0), "grn2")                    # the lit edge, left
    pic.put(leaf, "grn1")
    lx, ly = X1 - (J[0] - 6.0), Y1 - (J[1] + 1.5)
    a = np.radians(20)
    along, across = lx * np.cos(a) + ly * np.sin(a), -lx * np.sin(a) + ly * np.cos(a)
    pic.put(leaf & (across < -0.4), "grn2")
    pic.put(leaf & (np.abs(across) < 0.5) & (along > -5.0) & (along < 5.0), "grn0")   # the midrib
    return stem | leaf


def paint_cherries(pic, X1, Y1):
    """The token: two cherries, glossy and grinning."""
    key2 = np.array([-0.55, -0.62, 0.56])
    key2 /= np.linalg.norm(key2)
    P1 = (X1, Y1)
    (bx, by_, br), (fx, fy, fr) = CHER["back"], CHER["front"]
    for cx, cy, r in (CHER["back"], CHER["front"]):
        m = np.hypot(X1 - cx, Y1 - cy) < r
        pic.put(ak.dilate(m, 1) & ~m, "black")
        nx, ny = (X1 - cx) / r, (Y1 - cy) / r
        nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
        lam = nx * key2[0] + ny * key2[1] + nz * key2[2]
        pic.put(m, "red")
        pic.put(m & (lam < 0.16), "wine")
        pic.put(m & (lam < 0.16) & (lam >= 0.09) & ak.checker(), "red")
        pic.put(m & (lam < -0.3), "black")
        # a cool bounce off the night on the underside, 1 px
        rim = m & ~ak.erode(m, 1) & (ny > 0.5) & (nx > -0.3)
        pic.put(rim, "navy1")
        # the specular: a slanted streak with an ivory bloom round it
        sp = ak.ellipse(P1, cx - r * 0.55, cy - r * 0.42, r * 0.2, r * 0.09, angle=-50) < 0
        bloom = ak.ellipse(P1, cx - r * 0.52, cy - r * 0.4, r * 0.32, r * 0.2, angle=-50) < 0
        pic.put(m & bloom & ak.checker(), "ivory")
        pic.put(m & ak.dilate(sp, 1), "ivory")
        pic.put(m & sp, "cream")
        # the crown's dimple where the stem goes in
        pic.put(m & (np.hypot(X1 - (cx + 0.5), Y1 - (cy - r + 1.4)) < 1.8), "wine")
    # the back one's edge where the front one hangs over it: a shadow
    fm = np.hypot(X1 - fx, Y1 - fy) < fr
    bm = (np.hypot(X1 - bx, Y1 - by_) < br) & ~fm
    pic.put(bm & ak.dilate(fm, 2) & ~ak.dilate(fm, 1) & pic.where("red"), "wine")
    pic.put(ak.dilate(fm, 1) & ~fm & bm, "black")
    # faces: big eyes turned up at the money (cream whites, the pupils in
    # their top right corners), brows raised, a wide toothy grin; the back
    # one winks and leans in
    eye = [".kkkk.", "kcckkk", "kcckkk", "kcckkk", "kcccck", "kcccck", "kcccck", ".kkkk."]
    brow = [".kkkk.", "k....k"]
    grin = ["kkkkkkkkkkkkkkk", "kccccccccccccck", ".kwwwwwwwwwwwk.", "..kwwwrrrrwwk..", "...kkwrrrrwkk..", ".....kkkkkk...."]
    ex, ey = int(round(fx - 5)), int(round(fy - 11))
    ak.patch(pic, ex, ey, eye, INK)
    ak.patch(pic, ex + 8, ey - 1, eye, INK)
    ak.patch(pic, ex, ey - 4, brow, INK)
    ak.patch(pic, ex + 8, ey - 5, brow, INK)
    ak.patch(pic, ex - 1, ey + 10, grin, INK)
    ex, ey = int(round(bx - 5)), int(round(by_ - 8))
    ak.patch(pic, ex, ey + 2, ["..kk..", ".k..k.", "k....k"], INK)        # the wink: a happy arc
    ak.patch(pic, ex - 1, ey - 1, ["kkkkk."], INK)
    ak.patch(pic, ex + 8, ey - 1, eye[:4] + eye[5:], INK)
    ak.patch(pic, ex + 8, ey - 4, brow, INK)
    ak.patch(pic, ex, ey + 8, ["kkkkkkkkkkkkk", "kcccccccccccc", ".kwwwwwwwwwk.", "..kwwrrrwwk..", "...kkkkkkk..."], INK)


def draw():
    P = ak.Palette(COL, ramps=[SKY_R + ["blue"], TILE_R, GRN_R, ["black", "wine", "red"],
                               ["gold0", "gold1", "gold2", "cream"]])
    cv = ak.Canvas("#000000")
    s = cv.s
    yy, xx = np.mgrid[0:128, 0:128]
    X1, Y1 = xx + 0.5, yy + 0.5
    pic = ak.Picture.blank(P, "navy0")
    by = ak.by_level
    tr_ = ak.terrace
    cam = R.Camera(CAM["pos"], CAM["target"], fov=CAM["fov"], shift=CAM["shift"])

    # the key light in world terms: from the picture's top left and in front
    key = -0.55 * cam.r + 0.7 * cam.u - 0.45 * cam.f
    key /= np.linalg.norm(key)

    # ---- 3D: the buildings, the board's slab, the table under it
    slab = R.xf(R.prim(R.box((9.0, SLAB / 2, 3.0), 0.0), TILE), (0.0, -SLAB / 2, -3.0))
    table = R.prim(lambda p: p[:, 1] + SLAB, TABLE)
    blds = R.U(*[house(k, x, sc) for k, (x, sc) in enumerate(HOUSES)], hotel())
    out = R.render(cv, R.U(table, slab, blds), cam, [R.Mat("#FFFFFF", spec=0.0)] * (HOUSE0 + 2 * len(HOUSES)),
                   lights=[(tuple(key), "#FFFFFF", 1.0)], ambient="#000000", ss=2)
    mat = R.majority(out, s)
    nrm = ak.px_mean(out["normal"], s)
    nrm /= np.maximum(np.linalg.norm(nrm, axis=-1, keepdims=True), 1e-6)
    shadow_floor = ak.px_mean(R.ground(cv, blds, cam, y=0.0, light=tuple(key), ss=2), s)

    # the board's top: where each pixel's ray meets y = 0
    o, d = cam.rays(X1.reshape(-1).astype(np.float64), Y1.reshape(-1).astype(np.float64))
    t = np.where(d[:, 1] < -1e-6, -o[:, 1] / np.minimum(d[:, 1], -1e-6), np.inf)
    hit = o + d * t[:, None]
    wx = np.nan_to_num(hit[:, 0].reshape(128, 128), nan=99.0, posinf=99.0, neginf=-99.0)
    wz = np.nan_to_num(hit[:, 2].reshape(128, 128), nan=-99.0, posinf=99.0, neginf=-99.0)

    # ---- the void, the table and the board's far reaches: one calm dark,
    # black overhead, a soft haze rising behind the cherries (no edges in it)
    glow = np.clip(1 - np.hypot((X1 - 36) / 50.0, (Y1 - 66) / 36.0), 0, 1) ** 1.3
    hzn = cam.project((2.0, -SLAB, -400.0))[1]
    haze = np.clip(1 - np.abs(Y1 - hzn) / 16.0, 0, 1) * 1.25           # a dim band of haze along the horizon
    glow = np.maximum(glow * 2.0, haze)
    calm = (mat == -1) | (mat == TABLE)
    by(pic, tr_(glow, 0.35), SKY_R, calm)

    # ---- the board
    top = (mat == TILE) & (nrm[..., 1] > 0.7)
    side = (mat == TILE) & ~top
    on_strip = (wz <= 0) & (wz >= -D)
    band = top & on_strip & (wz < -D + BAND)
    inner = top & (wz < -D)                                           # the board's interior, past the band
    # the light: tile by tile, flat (one level a tile, bounded by its seams):
    # grey on the tile under the cherries, navy on the next, dark down the
    # street; the price strip a step under its tile; a small cream hot spot
    # (an ivory rim) up and left of the cherries' shadow, the shadow a navy
    # core with a grey rim; the hotel's door spills a little light
    def world(px_, py_):
        i_ = int(py_) * 128 + int(px_)
        return hit[i_, 0], hit[i_, 2]
    lx, lz = world(*POOLC)
    sxw, szw = world(*SHADOW)
    tid = np.floor(wx / W)
    dt = np.abs((tid + 0.5) * W - lx) / W                             # tiles from the lit one
    lt = np.where(dt < 0.5, LIT, 2.0 - (dt > 1.5)) - (tid * W > 1.7)
    dxw, dzw = world(*cam.project((HOTEL["x"], 0.0, -D + HOTEL["d"] + 0.25)))
    spill = np.hypot(wx - dxw, (wz - dzw) * 1.4)
    lt = np.where(spill < 0.45, np.maximum(lt, 2.0), lt)
    lt = np.where(spill < 0.22, np.maximum(lt, 3.0), lt)
    lt = np.maximum(lt, 1.0) - (shadow_floor > 0.45)                  # the buildings' cast shadows
    lt = np.where(wz > -PRICE, lt - 1, lt)                            # the price strip
    lt = lt - np.round(np.clip((X1 - 114.0) / 10.0, 0, 1))           # the right edge into the dark
    rp = np.hypot(wx - lx, (wz - lz) * 1.2)
    shd = np.hypot((wx - sxw) / SHADOW_R[0], (wz - szw) / SHADOW_R[1])
    lt = np.where((shd >= 1.0) & (rp < HOT * 1.35) & (wz <= -PRICE), np.maximum(lt, 4.0), lt)   # the hot spot
    lt = np.where((shd >= 1.0) & (rp < HOT) & (wz <= -PRICE), 5.0, lt)
    lt = np.where(shd < 1.0, np.where(shd < 0.62, 2.0, 3.0), lt)     # the cherries' shadow
    body = top & on_strip & ~band
    by(pic, np.clip(lt, 0, 5), TILE_R, body)
    lb = 3.0 - np.ceil(np.maximum(dt - 2.5, 0)) - (tid * W > 2.4)
    by(pic, np.clip(lb, 1, 3), BAND_R, band)
    by(pic, tr_(glow, 0.35), SKY_R, inner | (side & (wz <= -D)))
    lip = side & (wz > -D)
    pic.put(lip, "navy0")
    pic.put(lip & ak.shift(top, 0, 1) & (X1 < 112), "navy1")          # the lip catches a line of light
    # seams between tiles, under the band, over the price strip
    for i in range(-6, 14):
        ak.ink(pic, [cam.project((i * W, 0, 0)), cam.project((i * W, 0, -D))], "black", where=top & on_strip)
    ak.ink(pic, [cam.project((-4, 0, -D + BAND)), cam.project((9, 0, -D + BAND))], "black", where=top)
    ak.ink(pic, [cam.project((-4, 0, -D)), cam.project((9, 0, -D))], "black", where=top)
    ak.ink(pic, [cam.project((-4, 0, -PRICE)), cam.project((9, 0, -PRICE))], "black", where=top)

    # ---- the houses: each face one flat tone (the gable to us lit, grn2;
    # the side and the roof's near slope mid, its ridge catching the light;
    # the far slope dark), a black eave line, outlined in black
    hm = [(mat == HOUSE0 + 2 * k) | (mat == HOUSE0 + 2 * k + 1) for k in range(len(HOUSES))]
    hr = np.zeros((128, 128), bool)
    for k in range(len(HOUSES)):
        hr |= mat == HOUSE0 + 2 * k + 1
    hb_all = np.any(hm, axis=0)
    nh = nrm @ R.rot_y(HROT)                                          # normals in the houses' own frame
    lvh = np.where(nh[..., 2] > 0.6, 3.0, 2.0)                        # the gable lit, the side mid
    hslope = hr & (np.abs(nh[..., 2]) < 0.6)
    lvh = np.where(hslope, np.where(nh[..., 0] < -0.2, 2.0, 1.0), lvh)   # the roof: near slope, far slope
    by(pic, lvh, GRN_R, hb_all)
    pic.put(hslope & ~ak.shift(hslope | ~hb_all, 0, 1) & pic.where("grn1"), "grn2")   # the ridge's lit edge
    pic.put(hb_all & ~hslope & ak.shift(hslope, 0, 1), "black")      # the eave's line under the slopes
    tm = (mat == TBODY) | (mat == TROOF)
    for k in range(len(HOUSES)):
        pic.put(ak.dilate(hm[k], 1) & ~hm[k] & ~tm, "black")
    ry = R.rot_y(HROT)
    for x, sc in HOUSES:
        w_, d_ = 0.36 * sc, 0.34 * sc
        base = np.array([x, 0.0, -D + BAND / 2])
        door = cam.project(base + ry @ np.array([-0.15 * w_, 0.0, d_ / 2 + 0.003]))
        win = cam.project(base + ry @ np.array([0.2 * w_, 0.17 * sc, d_ / 2 + 0.003]))
        ak.patch(pic, int(round(door[0] - 1)), int(round(door[1])) - 4, ["kk"] * 4, INK)
        ak.patch(pic, int(round(win[0] - 1)), int(round(win[1] - 1)), ["ic", "ii"], INK)

    # ---- the hotel: the end toward the key lit (wine, a red cornice), the
    # long facade to us in shade (wine, its windows set in black bands); warm
    # windows, a neon blade sign on the corner, a marquee over a lit door
    tb, trf = mat == TBODY, mat == TROOF
    end = tb & (nrm[..., 0] < -0.6)
    fac = tb & ~end
    hp = (o + d * ak.at_px(out["depth"], s).reshape(-1)[:, None]).reshape(128, 128, 3)   # each pixel's point
    hx0, hw, hh = HOTEL["x"] - HOTEL["w"] / 2, HOTEL["w"], HOTEL["h"]
    zb, zf = -D - 0.02, -D + HOTEL["d"] - 0.02 + 0.004
    FLOORS = (1.24, 1.04, 0.84, 0.64, 0.44)
    pic.put(end, "wine")
    pic.put(fac, "wine")
    for wy in FLOORS:
        pic.put(fac & ak.shift(fac, -1, 0) & (np.abs(hp[..., 1] - wy) < 0.055), "black")    # the window bands
    pic.put(end & (hp[..., 1] > hh - 0.06), "red")                    # the cornice catches the key
    pic.put(fac & (hp[..., 1] > hh - 0.06), "black")
    lit_f = [[1, 0, 1], [1, 1, 1], [0, 1, 1], [1, 1, 0], [1, 0, 1]]
    lit_e = [[1, 1], [0, 1], [1, 0], [1, 1], [0, 1]]
    for j, wy in enumerate(FLOORS):
        for i, fu in enumerate((0.36, 0.58, 0.8)):
            px_, py_ = cam.project((hx0 + fu * hw, wy, zf))
            ak.patch(pic, int(round(px_ - 1)), int(round(py_ - 1)), ["ic", "ii"] if lit_f[j][i] else ["nn", "nn"], INK)
        for i, fz in enumerate((0.28, 0.66)):
            px_, py_ = cam.project((hx0 - 0.004, wy, zb + HOTEL["d"] * fz))
            ak.patch(pic, int(round(px_ - 1)), int(round(py_ - 1)), ["ci", "ii", "kk"] if lit_e[j][i] else ["nn", "nn", "kk"], INK)
    # the door, lit, under a marquee of bulbs (the rainbow: they chase)
    dx_, dy_ = cam.project((hx0 + 0.62 * hw, 0.0, zf))
    dx_, dy_ = int(round(dx_)), int(round(dy_))
    ak.patch(pic, dx_ - 2, dy_ - 6, ["kkkkk", "kciik", "kiiik", "kiiik", "kiiik", "kiiik"], INK)
    ak.patch(pic, dx_ - 6, dy_ - 9, ["kkkkkkkkkkkkk", "kRkRkRkRkRkRk", "kkkkkkkkkkkkk"], INK)
    slope = trf & (nrm[..., 2] > 0.25)
    gable = trf & (nrm[..., 0] < -0.6)
    pic.put(trf, "navy0")
    pic.put(slope, "blue")                                           # blue slates, lit
    pic.put(slope & ~ak.shift(slope, 0, -1), "navy1")                # the eave's edge
    pic.put(gable, "wine")
    pic.put(ak.dilate(tm, 1) & ~tm, "black")
    # the bargeboards: a clean light line up each edge of the lit gable
    rz = (zb + zf) / 2
    apex = cam.project((hx0 - 0.03, hh + HOTEL["roof"] - 0.01, rz))
    for zz in (zb - 0.04, zf + 0.04):
        ak.ink(pic, [cam.project((hx0 - 0.03, hh - 0.01, zz)), apex], "ivory", where=gable | trf)
    # the neon blade sign on the corner: HOTEL, stacked
    sx0, sy0 = cam.project((hx0, FLOORS[0] + 0.06, zf))
    letters = {"H": ["k.k", "k.k", "kkk", "k.k", "k.k"], "O": ["kkk", "k.k", "k.k", "k.k", "kkk"],
               "T": ["kkk", ".k.", ".k.", ".k.", ".k."], "E": ["kkk", "k..", "kk.", "k..", "kkk"],
               "L": ["k..", "k..", "k..", "k..", "kkk"]}
    x0s, y0s = int(round(sx0 - 3)), int(round(sy0))
    panel = np.zeros((128, 128), bool)
    panel[y0s:y0s + 31, x0s:x0s + 7] = True
    pic.put(ak.dilate(panel, 1) & ~panel, "black")
    pic.put(panel, "navy0")
    for j, ch in enumerate("HOTEL"):
        ak.patch(pic, x0s + 2, y0s + 2 + j * 6, letters[ch], {"k": "rainbow"})

    # ---- the cherries: two glossy balls in the air, grinning, their stems
    # trailing the hop
    paint_stems(pic, X1, Y1)
    paint_cherries(pic, X1, Y1)
    # the hop: two whoosh arcs trailing the back cherry, tapered at both
    # ends (grey in the middle, navy at the tips), on the calm dark
    okw = ~ak.dilate(cher_mask(X1, Y1), 2)
    bx_, by2, br_ = CHER["back"]
    for gap, a0, a1, wmax in ((3.5, 146.0, 234.0, 1.05), (7.5, 170.0, 222.0, 0.85)):
        rr_ = br_ + gap
        am = (a0 + a1) / 2
        for aa in (a0, a1):
            pa, pm = np.radians(aa), np.radians(am)
            p0 = (bx_ + rr_ * np.cos(pm), by2 + rr_ * np.sin(pm))
            p2 = (bx_ + rr_ * np.cos(pa), by2 + rr_ * np.sin(pa))
            k_ = rr_ / np.cos((pa - pm) / 2)                          # the tangents' meeting point
            p1 = (bx_ + k_ * np.cos((pa + pm) / 2), by2 + k_ * np.sin((pa + pm) / 2))
            ak.streak(pic, p0, p1, p2, wmax, 0.25, ok=okw, cols=(("grey", 0.6), ("navy1", 1.0)))

    # ---- money: bills off the hotel's roof, arcing over onto the cherries
    # (a faint tapered trail along their arc, thin and dark at the roof)
    keep = ~ak.dilate(cher_mask(X1, Y1), 1)
    arc = [(94, 33, 9, 5, 45), (83, 30, 10, 5, 26.57), (72, 32, 12, 6, 0), (63, 39, 13, 7, -26.57), (57, 50, 15, 8, -45)]
    ak.streak(pic, (57.0, 50.0), (65.5, 20.5), (101.0, 37.0), 1.1, 0.3, ok=keep & pic.where("black", "navy0"),
              cols=(("grey", 0.3), ("navy1", 1.0)))
    for bx2, by3, bw, bh, ang in arc:
        bill(pic, bx2, by3, bw, bh, ang, keep=keep)
    for gx_, gy_ in ((80, 40), (50, 41)):                             # the money shines
        ak.glint(pic, gx_, gy_, size=1)

    # ---- lone pixels the layers left, everywhere but the deliberate ones
    # (windows and their glints, the faces, the sign, the marquee)
    keepm = cher_mask(X1, Y1) & ~(ak.dilate(cher_mask(X1, Y1), 1) & ~ak.erode(cher_mask(X1, Y1), 1))
    keepm |= (mat == TBODY) | (mat == TROOF)
    keepm |= pic.where("rainbow")
    keepm |= ak.dilate(pic.where("cream") & ~ak.nbrs(pic.where("cream"), diag=True), 1)
    ak.despeckle(pic, need=5, keep=keepm, passes=2)

    # ---- the title: gold leaf (a short pale sky, deep amber, a dark horizon
    # under the middle, light below), dark navy for its depth, a
    # bevel, a black outline and shadow, two glints
    m1 = ak.load_mask(TITLE)
    x1, y1 = ak.centred_x(m1) - 1, 4
    M1 = ak.place(m1, x1, y1)
    rows = ["gold2"] * 3 + ["gold1"] * 7 + ["gold0"] + ["gold1"] * 5
    t1 = ak.title(pic, m1, x1, y1, fill=None, rows=rows, hi=None, lo=None,
                  extrude=dict(dx=1, dy=1, depth=3, colours=["navy1", "navy1", "navy1"]),
                  shadow=dict(dx=1, dy=2, colour="black"))
    ck = ak.checker()
    wide = M1 & (ak.runs(M1, 1) >= 4)
    pic.put(wide & (yy == y1 + 3) & ck, "gold2")                      # the sky's soft lower edge
    pic.put(wide & (yy == y1 + 9) & ck, "gold0")                      # and the horizon's upper one
    # the depth: a lone blue (a stair-step) goes to the navy behind it, and
    # one letter's depth never touches the next letter's face
    E1 = t1["extrude"]
    m = E1 & pic.where("blue")
    pic.put(m & ~ak.nbrs(m), "navy1")
    lab = ak.letters(M1)
    for k in range(1, int(lab.max()) + 1):
        own = ak.dilate(lab == k, 4) & E1
        other = M1 & (lab != k) & (lab > 0)
        pic.put(own & ak.nbrs(other), "black")
    ak.bevel_contour(pic, M1, "cream", "gold0")
    out1 = ak.outside_of(M1)
    pic.put(M1 & ak.shift(out1, 0, 1), "cream")                      # every outer top edge lit
    # no lone bevel pixels: a light or dark edge pixel with none of its kind
    # beside it goes back to the face's band
    face_col = np.full((128, 128), -1)
    for j, c in enumerate(rows):
        face_col[y1 + j, :] = pic.pal[c]
    for c in ("cream", "gold0"):
        m = M1 & pic.where(c)
        lone = m & ~ak.nbrs(m, diag=True)
        if c == "gold0":
            lone &= face_col != pic.pal["gold0"]
        pic.idx[lone] = face_col[lone]
    # lone pixels in the depth and the outline (stair-steps between letters)
    ak.despeckle(pic, need=4, within=ak.dilate(M1, 5) & ~M1, passes=2)
    ak.glint(pic, *ak.glint_in(M1, x1 + 4, y1 + 7, 2), size=2, tip="gold2")
    ak.glint(pic, *ak.glint_in(M1, x1 + 110, y1 + 7, 2), size=2, tip="gold2")
    return pic.image()


def title_lines():
    """The title's lettering as drawn here, and its depth, for the title
    screen (tools/titleart.py: the game paints it in the house gold)."""
    return [dict(mask=ak.load_mask(TITLE), depth=3, side="navy1")]


if __name__ == "__main__":
    import boxart
    boxart.save(draw(), HERE.parent / "docs" / "cart.png")
