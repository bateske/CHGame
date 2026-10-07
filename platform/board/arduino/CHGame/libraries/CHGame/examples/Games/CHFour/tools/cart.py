"""docs/cart.png, Four in a Row's cover in the visual menu (docs/cover-art.md).
`chgame boxart` redraws it; edit this, not the PNG.

THE BRIEF (revision 1)
  Message: the winning drop. Three of your red chips are lined up and lit
  on the top row, the fourth hole beside them stands empty under a ring of
  light, and your last chip is swooping in, its foot already in the slot
  over that hole. One more inch and it is FOUR IN A ROW.
  Composition: a three-quarter camera a little above the board's top edge
  and to its right: the standing blue board runs in perspective from the
  near right (big) to the far left (small, dark), its top edge a long
  diagonal from under the title's left down to the end post at the right.
  The winning row rides that diagonal left to right (chips about 14, 16
  and 19 px, the hole 21) and leads the eye to the hero: the falling chip,
  24 px, the brightest, most contrasty thing under the title, against the
  dark at the upper right, 10 px clear of IN A ROW. It is stamped in the
  picture's own pixels: a red face turned to us with six 3 x 3 cream
  inserts, a wine ring inked round its centre, its edge in shade (wine,
  the inserts crossing it in red), a cream rim where the key catches its
  upper left, a black outline; the lip in front hides its foot, and it
  shades the back plate's top beside it. Its path streams back from its
  upper left: three curved, tapered lines of different lengths, cream
  near the chip through light blue into the dark, steep by the chip and
  flattening behind it (it was flicked in from the left). Below the
  winning row the rest of the board falls into shadow; the far columns
  and the second row are dim chips (a step down their own ramps, no
  ring). At the right, the end post: a bevelled upright, lit on its left
  edge and top, its outer side navy. Behind the board's back edge, a
  9-row band of felt (the table, seen over the board) lit behind the chip
  and cooling to navy at the left, its far edge a clean line into the
  black. The title sits on black above all of it.
  Light: the house key from the top left, and a spotlight on the winning
  row: the plastic is painted per pixel as levels on the blue ramp (blue2
  in the pool, blue1, navy0 at the far left and bottom) with 1-2 px
  checker seams only. Every edge of the board's top comes from the
  projected lines themselves, so each band steps evenly: the lip (blue3,
  a cream gloss over the winning chips), the slot (black, a divider
  between each two columns) and the back plate's top. Each hole is cut:
  its upper-left rim a step darker, its lower-right a step lighter; the
  holes' walls lit on their lower right, the chips' faces in the lip's
  shadow on their upper left. The four holes of the row are ringed in
  cream with a blue3 halo, clean rings with no dithered fringe. The chips
  in the board are stamped like the hero: inserts in blocks (3 x 3 or
  2 x 2 by size), rings inked. The outer two rows and columns step down
  into the dark.
  Title: FOUR in gold chrome: a pale sky band, a gold body, a dark
  horizon and its bright reflection, the ground darkening to the foot,
  with one-row checker seams between the wide bands; a cream bevel on
  the outer contour (counters flat), a 3-step extrusion from red into
  wine with each letter parted by black, a drop shadow, and two
  catch-lights on the chrome's horizon (the F's left edge, the R's
  right). IN A ROW under it in the same gold with a red extrusion, its
  letters parted, between gold rules that each end in a little red chip.
  Palette (11 own + cream, grey, black, red; grey unused):
    navy0 blue1 blue2 blue3   the board's ramp, hue-shifted: indigo shadows,
                              icy highlights (cream above)
    wine                      the red chips' shade and the title's depth
    amber0 amber1             the dealer's gold chips
    felt1                     the table behind (with navy0)
    gold0 gold1 gold2         the title's own: nothing else uses them
  Fonts: KISS 91 (FOUR; bmf collection, freeware, author not stated:
  unclear terms, to list in docs/cover-art.md's credits) and NicoBold by
  emhuo (IN A ROW; free for commercial or non-commercial use), at their
  own sizes; credits in tools/art/title.txt and title2.txt.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import numpy as np  # noqa: E402
import artkit as ak  # noqa: E402
from artkit import render3d as R  # noqa: E402

TITLE = HERE / "art" / "title.txt"
TITLE2 = HERE / "art" / "title2.txt"

PAL = {
    "navy0": "#100C4A", "blue1": "#1C3CB0", "blue2": "#2E72EC", "blue3": "#8CD0FF",
    "wine": "#6E0C22", "felt1": "#13643C",
    "amber0": "#7A3E0A", "amber1": "#D89024",
    "gold0": "#9C4C08", "gold1": "#FFC832", "gold2": "#FFF0A0",
}
BLUE = ["black", "navy0", "blue1", "blue2", "blue3", "cream"]
REDR = ["black", "wine", "red", "cream"]
FELT = ["black", "navy0", "felt1"]
GOLDR = ["black", "amber0", "amber1", "cream"]
TITLE_R = ["gold0", "gold1", "gold2", "cream"]

YY, XX = np.mgrid[0:128, 0:128]
SS = 4                                        # samples a pixel side

# ---- the board (its own frame: x right, y up, z toward the front; a hole's pitch is 1) ----
# rows top (0) to bottom (5), columns 0..6: R the player's red, G the dealer's gold, . empty.
# A real position: 17 red, 18 gold (the dealer went first), no four yet; red to move:
# the drop in column 6 makes the one four (the top row), and anything else loses to
# gold's threat in column 1. The dealer has blocked the row's left end.
BOARD = ["..GRRR.",
         "..GRGRG",
         ".GGRGRR",
         ".GRGRGG",
         "RGRRGRG",
         "GRGRGRG"]
WIN = [(3, 0), (4, 0), (5, 0)]
TARGET = (6, 0)
GRID = np.array([[{"R": 1, "G": 2}.get(c, 0) for c in row] for row in BOARD])
RH, RC, CT, ZC, BT = 0.40, 0.385, 0.08, 0.04, 0.26   # hole and chip radius, chip half thickness and z, board half thickness
TOP, BOT, HW = 3.10, -3.3, 3.56
PW, PD, PT = 0.40, 0.42, TOP + 0.06           # the end post: width, half depth, top
SLW = 0.10                                   # a slot's half width (front to back)
ROT = -24                                    # the board turned so its right end comes toward us
ROLL = 3.0                                   # the camera rolled a little: the top edge falls less steeply
ROTM = R.rot_y(ROT)
CAM = R.Camera((4.0, 5.0, 9.0), (1.4, 1.8, 0), fov=28, shift=(6, 42),
               up=(np.sin(np.radians(ROLL)), np.cos(np.radians(ROLL)), 0))
LS = np.array([-0.36, 0.5, 0.79]) @ ROTM      # the key for the holes' shading (board frame): frontal, thin crescents
LS = LS / np.linalg.norm(LS)
DROP = (3.0, TOP + 0.34, 0.0)                 # the falling chip's centre: over the slot, its foot in it

# the falling chip, stamped: its face's half axes (px), turn, the edge's offset,
# where its inserts sit (degrees round the face) and its nudge from DROP
HERO = dict(a=10.4, b=11.6, rot=-24, edge=(2.4, 1.4), inserts=(-75, -15, 45, 105, 165, 225), dx=0, dy=0)
GLINTS = [(14, 15, (3, 3, 2, 2)), (110, 16, (3, 3, 2, 2))]   # the title's catch-lights: x, y, arms (l, r, u, d)
TRAIL = [(104, 12, 1, 0.9), (128, 23, 2, 1.3), (152, 14, 1, 0.9)]   # its path: where round it, length back, rise, root radius
GLOSS = (-0.6, 2.2)                           # where the lip's glint runs (board x)
FELT_H = 9                                    # the felt seen over the board's back edge (rows)
INSERTS = (-90, -30, 30, 90, 150, 210)        # the board's chips' inserts (degrees round the face, y up)

# what each pixel shows
ROOM, FACE, TOPF, SLOT, BORE, THRU, CHIP, CWALL, PFRONT, PSIDE, PTOP = range(11)


def trace(X, Y):
    """Every ray through (X, Y) on the picture against the board: its class,
    a light level (walls, chips) and its hit point (in the board's frame)."""
    o, d = CAM.rays(X.ravel().astype(np.float64), Y.ravel().astype(np.float64))
    o, d = o @ ROTM, d @ ROTM
    n = len(d)
    cls = np.full(n, ROOM, np.int8)
    lev = np.zeros(n)
    aux = np.zeros((n, 3))
    tF = (BT - o[:, 2]) / d[:, 2]
    F = o + d * tF[:, None]
    onF = (tF > 0) & (np.abs(F[:, 0]) < HW) & (F[:, 1] < TOP) & (F[:, 1] > BOT)
    i = np.clip(np.round(F[:, 0] + 3), 0, 6).astype(int)
    j = np.clip(np.round(2.5 - F[:, 1]), 0, 5).astype(int)
    cx, cy = i - 3.0, 2.5 - j
    kind = GRID[j, i]
    inh = onF & (np.hypot(F[:, 0] - cx, F[:, 1] - cy) < RH)
    cls[onF & ~inh] = FACE
    aux[onF] = F[onF]
    # where the ray leaves the hole's cylinder
    ox, oy = o[:, 0] - cx, o[:, 1] - cy
    a = d[:, 0] ** 2 + d[:, 1] ** 2
    b = 2 * (ox * d[:, 0] + oy * d[:, 1])
    c = ox ** 2 + oy ** 2 - RH ** 2
    t2 = (-b + np.sqrt(np.maximum(b * b - 4 * a * c, 0))) / (2 * a)
    W = o + d * t2[:, None]
    tC = (ZC + CT - o[:, 2]) / d[:, 2]
    Cp = o + d * tC[:, None]
    rC = np.hypot(Cp[:, 0] - cx, Cp[:, 1] - cy)
    chipc = inh & (kind > 0)
    onchip = chipc & (tC < t2) & (rC < RC)
    cls[onchip] = CHIP
    aux[onchip] = np.stack([Cp[:, 0] - cx, Cp[:, 1] - cy, np.zeros(n)], 1)[onchip]
    # the chip's face in the lip's shadow: the ray to the key leaves through the wall
    sF = (BT - Cp[:, 2]) / LS[2]
    Q = Cp + LS[None, :] * sF[:, None]
    lev[onchip] = (np.hypot(Q[:, 0] - cx, Q[:, 1] - cy) < RH)[onchip]
    # the wall: lit by its normal, unless the far wall shades it
    wall = (chipc & ~onchip) | (inh & (kind == 0) & (W[:, 2] > -BT))
    nx, ny = -(W[:, 0] - cx) / RH, -(W[:, 1] - cy) / RH
    dif = np.clip((nx * LS[0] + ny * LS[1]) / np.hypot(LS[0], LS[1]), 0, 1)
    wx, wy = W[:, 0] - cx, W[:, 1] - cy
    la = LS[0] ** 2 + LS[1] ** 2
    lb = 2 * (wx * LS[0] + wy * LS[1])
    lc = wx ** 2 + wy ** 2 - RH ** 2
    s2 = (-lb + np.sqrt(np.maximum(lb * lb - 4 * la * lc, 0))) / (2 * la)
    sunlit = (W[:, 2] + s2 * LS[2] >= BT) & (dif > 0)
    lev[wall] = (dif * sunlit)[wall]
    cls[wall & (kind > 0)] = CWALL
    cls[wall & (kind == 0)] = BORE
    aux[wall] = np.stack([W[:, 0] - cx, W[:, 1] - cy, W[:, 2]], 1)[wall]
    thru = inh & (kind == 0) & ~wall
    cls[thru] = THRU
    # the top face and its slots
    tT = (TOP - o[:, 1]) / d[:, 1]
    T = o + d * tT[:, None]
    onT = (d[:, 1] < 0) & (np.abs(T[:, 2]) < BT) & (np.abs(T[:, 0]) < HW) & ~onF & (F[:, 1] >= TOP)
    cls[onT] = TOPF
    aux[onT] = T[onT]
    ti = np.clip(np.round(T[:, 0] + 3), 0, 6)
    slot = onT & (np.abs(T[:, 0] - (ti - 3)) < 0.42) & (np.abs(T[:, 2]) < SLW)
    cls[slot] = SLOT
    # the end post (a box at the right end)
    lo = np.array([HW, -9.0, -PD])
    hi = np.array([HW + PW, PT, PD])
    with np.errstate(divide="ignore", invalid="ignore"):
        t1 = (lo - o) / d
        t3 = (hi - o) / d
    tmn, tmx = np.minimum(t1, t3), np.maximum(t1, t3)
    te, ax, tl = tmn.max(1), tmn.argmax(1), tmx.min(1)
    tb = np.where(onF, tF, np.where(onT, tT, np.inf))
    post = (te < tl) & (te > 0) & (te < tb)
    Pp = o + d * te[:, None]
    for k, cl in ((0, PSIDE), (1, PTOP), (2, PFRONT)):
        m = post & (ax == k)
        cls[m] = cl
        aux[m] = Pp[m]
    sh = (128 * SS, 128 * SS)
    return cls.reshape(sh), lev.reshape(sh), aux.reshape(sh + (3,)), i.reshape(sh), j.reshape(sh)


def blocks(a, s=SS):
    return a.reshape(128, s, 128, s).transpose(0, 2, 1, 3).reshape(128, 128, s * s)


def majority(a, s=SS, among=None):
    """Each pixel's commonest value among its s x s samples (only the samples
    where `among` is, when given)."""
    blk = blocks(a, s)
    w = np.ones_like(blk, bool) if among is None else blocks(among, s)
    vals = np.unique(blk)
    cnt = np.stack([((blk == v) & w).sum(-1) for v in vals], -1)
    return vals[cnt.argmax(-1)]


def class_mean(v, cls_s, maj, s=SS):
    """Each pixel's mean of v over its samples of the pixel's own class."""
    vb = blocks(v, s)
    w = blocks(cls_s, s) == maj[..., None]
    return (vb * w).sum(-1) / np.maximum(w.sum(-1), 1)


def proj(x, y, z=BT):
    """A point in the board's frame on the picture."""
    return CAM.project(ROTM @ np.array([x, y, z], float))


def hole_mask(cls, ci, cj, col, row):
    return np.isin(cls, (BORE, THRU, CHIP, CWALL)) & (ci == col) & (cj == row)


def hero_chip(pic, cx, cy, hide):
    """The falling chip, stamped in the picture's own pixels: a red casino
    chip seen nearly face on, tilted, its edge showing on its lower right. Six
    cream inserts round the rim of its face (3 x 3 each), a wine ring inked
    round the centre, the edge wine (it turns from the key) with the inserts
    running across it in red, a cream rim on its upper left, outlined black.
    `hide`: the pixels in front of it (the front plate's lip and face).
    Returns its mask."""
    a, b, rot, (ex, ey) = HERO["a"], HERO["b"], np.radians(HERO["rot"]), HERO["edge"]
    s = 4
    c = (np.arange(128 * s) + 0.5) / s
    X, Y = np.meshgrid(c, c)

    def ell(x0, y0, X=X, Y=Y):
        dx, dy = X - x0, Y - y0
        uu = dx * np.cos(rot) + dy * np.sin(rot)
        vv = -dx * np.sin(rot) + dy * np.cos(rot)
        return np.hypot(uu / a, vv / b), np.degrees(np.arctan2(vv / b, uu / a))

    def to_px(m):
        return m.reshape(128, s, 128, s).mean(axis=(1, 3)) >= 0.5

    face = to_px(ell(cx, cy)[0] < 1)
    sil = np.zeros((128 * s, 128 * s), bool)
    for t in np.linspace(0, 1, 9):
        sil |= ell(cx + ex * t, cy + ey * t)[0] < 1
    sil = to_px(sil) | face
    side = sil & ~face
    vis = sil & ~hide
    # the edge: wine, the inserts across it red
    _, ae = ell(cx + ex * 0.5, cy + ey * 0.5, XX + 0.5, YY + 0.5)
    ang = (np.asarray(HERO["inserts"]) + 0.0)
    near = np.min(np.abs((ae[..., None] - ang[None, None, :] + 180) % 360 - 180), axis=-1) < 11
    pic.put(vis & side, "wine")
    pic.put(vis & side & near, "red")
    # the face: red, the inserts cream
    pic.put(vis & face, "red")
    for ph in HERO["inserts"]:
        t = np.radians(ph)
        uu, vv = 0.80 * a * np.cos(t), 0.80 * b * np.sin(t)
        ix = cx + uu * np.cos(rot) - vv * np.sin(rot)
        iy = cy + uu * np.sin(rot) + vv * np.cos(rot)
        x0, y0 = int(np.floor(ix - 1.0)), int(np.floor(iy - 1.0))
        blk = (XX >= x0) & (XX < x0 + 3) & (YY >= y0) & (YY < y0 + 3)
        pic.put(vis & face & blk, "cream")
    # the ring round its centre
    pts = []
    for t in np.linspace(0, 2 * np.pi, 61):
        uu, vv = 0.5 * a * np.cos(t), 0.5 * b * np.sin(t)
        pts.append((cx + uu * np.cos(rot) - vv * np.sin(rot), cy + uu * np.sin(rot) + vv * np.cos(rot)))
    ak.ink(pic, pts, "wine", where=vis & face)
    # the rim catching the key on its upper left
    ys, xs = np.nonzero(face)
    xc, yc = xs.mean(), ys.mean()
    bnd = face & ~ak.erode(face, 1)
    dx, dy = XX - xc, YY - yc
    cosl = (-dx * 0.8 - dy) / np.maximum(np.hypot(dx, dy), 1e-6) / np.hypot(0.8, 1)
    pic.put(vis & bnd & (cosl > 0.55), "cream")
    pic.put(ak.dilate(vis, 1) & ~vis & ~hide, "black")
    return vis


def line_y(p, q):
    """Where the straight line through two picture points crosses each column (floats)."""
    (x0, y0), (x1, y1) = p, q
    return y0 + (np.arange(128) + 0.5 - x0) * (y1 - y0) / (x1 - x0)


def draw():
    P = ak.Palette(PAL, ramps=[BLUE, REDR, GOLDR, TITLE_R, FELT])
    pic = ak.Picture.blank(P, "black")
    c = (np.arange(128 * SS) + 0.5) / SS
    X, Y = np.meshgrid(c, c)
    cls_s, lev_s, aux_s, i_s, j_s = trace(X, Y)
    cls = majority(cls_s)
    lev = class_mean(lev_s, cls_s, cls)
    aux = np.stack([class_mean(aux_s[..., k], cls_s, cls) for k in range(3)], -1)
    ci, cj = majority(i_s), majority(j_s)
    u, v = aux[..., 0], aux[..., 1]
    postm = np.isin(cls, (PFRONT, PSIDE, PTOP))
    holes = np.isin(cls, (BORE, THRU, CHIP, CWALL))

    # ---- the board's top edge, from the lines themselves (so every band
    # steps evenly): the lip (the front plate's rounded top) on row r0, the
    # slot and the back plate's top over it, the room above rb
    yfront = line_y(proj(-HW, TOP, BT), proj(HW, TOP, BT))
    yback = line_y(proj(-HW, TOP, -BT), proj(HW, TOP, -BT))
    r0 = np.floor(yfront).astype(int)[None, :] + 0 * YY
    rb = np.floor(yback).astype(int)[None, :] + 0 * YY
    xpost = int(np.floor(proj(HW, TOP, PD)[0]))
    inb = (XX < xpost) & ~postm
    lip = inb & (YY == r0)
    band = inb & (YY >= rb) & (YY < r0)
    slot = band & (YY == r0 - 1)
    face = inb & (YY > r0) & ~holes
    room = ~postm & ~holes & ~face & ~lip & ~band

    # ---- the room behind: felt in a band of light just over the board's back
    # edge, cooling through navy into black (bands parallel to the edge)
    above = rb - YY                                   # rows above the back edge
    dcx, dcy = proj(*DROP)
    across = np.clip((XX + 0.5 - (dcx - 70)) / 50.0, 0, 1)          # 0 at the left, 1 behind the chip
    fl = (2.45 - above * 0.17) * (0.6 + 0.4 * across)
    fl = np.where(above > FELT_H, 0.0, np.maximum(fl, 1.0))     # the far edge: a clean line into the dark
    ak.by_level(pic, ak.terrace(np.clip(fl, 0, 2), 0.25), FELT, room & (XX < xpost), q=2)

    # ---- the plastic: a pool of light on the winning row, falling off to navy
    def light(uu, vv):
        pool = np.exp(-(((uu - 1.8) / 2.6) ** 2 + ((vv - 2.55) / 0.9) ** 2))
        return np.minimum(1.25 + 1.95 * pool - np.clip((-uu - 0.5) / 2.0, 0, 1) * 0.3, 3.0)
    Lf = light(u, v)
    lvl = ak.terrace(Lf, 0.12)
    ak.by_level(pic, lvl, BLUE, face, q=2)
    # each hole's rim: the plastic a step darker on its upper left (the edge
    # turns away from the key), a step lighter on its lower right
    rim = face & ak.nbrs(holes)
    lt = (u - (ci - 3.0)) * LS[0] + (v - (2.5 - cj)) * LS[1]
    base = np.floor(lvl).astype(int)
    ak.put_levels(pic, rim & (lt > 0.1), base - 1, BLUE)
    ak.put_levels(pic, rim & (lt < -0.12), base + 1, BLUE)

    # the walls of the holes: lit on their lower right, a step darker out of the pool
    hole_lit = light(ci - 3.0, 2.5 - cj) > 2.2
    ak.put_levels(pic, cls == BORE, np.round(lev * 2).astype(int), ["navy0", "blue2", "blue3"])
    ak.put_levels(pic, (cls == CWALL) & hole_lit, np.round(lev * 3).astype(int), ["black", "navy0", "blue2", "blue3"])
    ak.put_levels(pic, (cls == CWALL) & ~hole_lit, np.round(lev * 3).astype(int), ["black", "navy0", "blue1", "blue2"])
    pic.put(cls == THRU, "black")

    # ---- the chips in the board: casino chips stamped like the falling one
    # (inserts in blocks, a ring inked), the lip's shadow on their upper left;
    # lit in the pool, a step darker out of it
    chip = cls == CHIP
    shade = majority(np.where(cls_s == CHIP, (lev_s < 0.5).astype(np.int8), -1), among=cls_s == CHIP) == 1
    #                body      shade     insert   insert in shade  ring
    LOOK = {(1, True): ["red", "wine", "cream", "red", "wine"],
            (1, False): ["wine", "black", "red", "wine", None],
            (2, True): ["amber1", "amber0", "cream", "amber1", "amber0"],
            (2, False): ["amber0", "black", "amber1", "amber0", None]}
    for row in range(6):
        for col in range(7):
            kk = GRID[row, col]
            vis = chip & (ci == col) & (cj == row)
            if not kk or not vis.any():
                continue
            cols = LOOK[(kk, bool(light(col - 3.0, 2.5 - row) > 2.2))]
            cx, cy = col - 3.0, 2.5 - row
            zc = ZC + CT
            pic.put(vis & ~shade, cols[0])
            pic.put(vis & shade, cols[1])
            rim = [proj(cx + RC * np.cos(t), cy + RC * np.sin(t), zc) for t in np.linspace(0, 2 * np.pi, 13)]
            w = max(p_[0] for p_ in rim) - min(p_[0] for p_ in rim)
            n = 3 if w >= 15 else 2
            for ph in INSERTS:
                t = np.radians(ph)
                ix, iy = proj(cx + 0.80 * RC * np.cos(t), cy + 0.80 * RC * np.sin(t), zc)
                x0, y0 = int(np.floor(ix - n / 2 + 0.5)), int(np.floor(iy - n / 2 + 0.5))
                blk = (XX >= x0) & (XX < x0 + n) & (YY >= y0) & (YY < y0 + n) & vis
                pic.put(blk & ~shade, cols[2])
                pic.put(blk & shade, cols[3])
            ring = [proj(cx + 0.5 * RC * np.cos(t), cy + 0.5 * RC * np.sin(t), zc) for t in np.linspace(0, 2 * np.pi, 61)]
            if cols[4]:
                ak.ink(pic, ring, cols[4], where=vis & ak.erode(vis, 1))

    # ---- the top: the lip catching the key, the slot dark (a divider between
    # each two columns), the back plate's top a step down
    pic.put(lip, "blue3")
    pic.put(band, "blue2")
    pic.put(slot, "black")
    # the lip's gloss: one cream glint along it where the pool is brightest
    gx0, gx1 = proj(GLOSS[0], TOP, BT)[0], proj(GLOSS[1], TOP, BT)[0]
    gt = (XX + 0.5 - gx0) / (gx1 - gx0)
    pic.put(lip & (gt > 0.22) & (gt < 0.78), "cream")
    for k in range(-3, 4):
        xd = int(np.floor(proj(k + 0.5, TOP, 0)[0]))
        if xd < xpost - 1:
            pic.put(slot & (XX == xd), "blue1")
    # ---- the end post: a bevelled bar, lit on its left
    pf = cls == PFRONT
    pu = (aux[..., 0] - HW) / PW
    pdn = np.clip((TOP - aux[..., 1]) / 1.6, 0, 1.2)
    plv = np.where(pu < 0.14, 4.0, np.where(pu < 0.8, 2.9, 2.0)) - pdn
    ak.by_level(pic, ak.terrace(plv, 0.15), BLUE, pf, q=2)
    pic.put(cls == PSIDE, "navy0")
    pic.put(cls == PTOP, "blue2")
    pic.put((cls == PTOP) & ak.shift(pf, 0, -1), "blue3")
    pic.put((face | lip | band) & ak.shift(postm, -1, 0), "navy0")

    # ---- the four in a row: each hole ringed in light, the empty one too
    for col, row in WIN + [TARGET]:
        H = hole_mask(cls, ci, cj, col, row)
        r1 = ak.dilate(H, 1) & ~H & face
        r2 = ak.dilate(H, 2, diag=True) & ~H & ~r1 & face
        pic.put(r2, "blue3")
        pic.put(r1, "cream")

    # ---- the falling chip, its foot just into the slot (the front plate hides it)
    hx, hy = proj(*DROP)
    dm = hero_chip(pic, hx + HERO["dx"], hy + HERO["dy"], YY >= r0)
    # it shades the back plate's top beside its foot, down the key's way
    foot = dm & (YY == r0 - 2)
    if foot.any():
        fx1 = np.nonzero(foot.any(0))[0].max()
        pic.put(band & ~slot & (XX > fx1) & (XX <= fx1 + 4), "navy0")
    ys_, xs_ = np.nonzero(dm)
    xc_, yc_ = xs_.mean(), ys_.mean()
    # it was flicked in from the left: its path streams back from its upper
    # left, steep by the chip (it is dropping) and flattening behind it
    rad = (xs_.max() - xs_.min() + 1) / 2.0
    for th, back, rise, rr in TRAIL:
        a_ = np.radians(th)
        root = (xc_ + 0.5 + np.cos(a_) * (rad + 2.5), yc_ + 0.5 - np.sin(a_) * (rad + 2.5))
        end = (root[0] - back, root[1] - rise - back * 0.25)
        ctrl = (root[0] - back * 0.25, root[1] - rise - back * 0.25)
        ak.streak(pic, root, ctrl, end, rr, 0.3, ok=~ak.dilate(dm, 1) & (YY > 49) & (YY < r0 - 1),
                  cols=(("cream", 0.3), ("blue3", 0.65), ("blue1", 1.0)))

    # lone pixels left by the stamps and seams take their neighbours' colour
    ak.despeckle(pic, 4, within=YY > 47, passes=2)

    # the frame: its outer two rows and columns step down into the dark
    edge2 = (XX < 2) | (XX > 125) | (YY > 125)
    for a_, b_ in (("navy0", "black"), ("felt1", "navy0"), ("blue1", "navy0"), ("blue2", "navy0"), ("blue3", "navy0"),
                   ("wine", "black"), ("red", "wine"), ("amber0", "black"), ("amber1", "amber0"), ("cream", "navy0")):
        pic.put(edge2 & (pic.idx == P[a_]), b_)
    draw_title(pic)
    return pic.image()


def draw_title(pic):
    """FOUR in gold chrome (a pale sky, a dark horizon, its bright reflection,
    the ground darkening to the foot), a cream bevel, a three-step extrusion
    from red into wine with every letter parted by black, a drop shadow and two
    catch-lights; IN A ROW under it in the same gold, between two gold rules
    that each end in a little red chip."""
    m1 = ak.load_mask(TITLE)
    x1, y1 = ak.centred_x(m1), 2
    rows1 = ["gold2"] * 7 + ["gold1"] * 6 + ["gold0"] * 2 + ["gold2"] * 2 + ["gold1"] * 7 + ["gold0"] * 4
    t1 = ak.title(pic, m1, x1, y1, fill=None, rows=rows1, hi=None, lo=None,
                  extrude=dict(dx=1, dy=1, depth=3, colours=["red", "wine", "wine"]),
                  shadow=dict(dx=1, dy=2, colour="black"))
    part_letters(pic, t1, 3)
    # the seams between the chrome's wide bands, half and half for a row
    ck = ak.checker()
    f1 = t1["face"]
    pic.put(f1 & (YY == y1 + 7) & ck, "gold2")
    pic.put(f1 & (YY == y1 + 24) & ck, "gold1")
    ak.bevel_contour(pic, t1["face"], "cream", "gold0")
    m2 = ak.embolden(ak.load_mask(TITLE2))
    x2, y2 = ak.centred_x(m2), y1 + m1.shape[0] + 4
    rows2 = ["gold2"] * 5 + ["gold1"] * 5 + ["gold0"] * 2
    t2 = ak.title(pic, m2, x2, y2, fill=None, rows=rows2, hi=None, lo=None,
                  extrude=dict(dx=1, dy=1, depth=1, colours=["red"]),
                  shadow=dict(dx=1, dy=1, colour="black"))
    part_letters(pic, t2, 1)
    ak.bevel_contour(pic, t2["face"], "cream", "gold0")
    ak.despeckle(pic, 3, within=t1["all"] | t2["all"], passes=2)
    for gx, gy, arms in GLINTS:
        ak.glint(pic, gx, gy, arms=arms, tip="gold2")
    ry_ = y2 + 5
    w2 = m2.shape[1]
    MINI = ["..kkk..", ".kcrck.", "krrrrrk", "kcrrrck", "krrrrrk", ".kcrck.", "..kkk.."]
    for xa, xb, xc in ((4, x2 - 11, x2 - 10), (x2 + w2 + 4, 123, x2 + w2 + 3)):
        line = np.zeros((128, 128), bool)
        line[ry_:ry_ + 2, xa:xb + 1] = True
        ak.outline(pic, line, "black")
        pic.put(line, "gold1")
        pic.put(line & ~ak.shift(line, 0, 1), "gold2")
        pic.put(line & ~ak.shift(line, 0, -1), "gold0")
        ak.patch(pic, xc, ry_ - 2, MINI, {"k": "black", "r": "red", "c": "cream"})
    return t1, t2, (x1, y1), (x2, y2)


def part_letters(pic, t, depth):
    """Each letter parted from its neighbours' extrusion by black."""
    M = t["face"]
    lab = ak.letters(M)
    allE = t["extrude"]
    for k in range(1, lab.max() + 1):
        Mi = lab == k
        Ei = np.zeros_like(Mi)
        for d in range(1, depth + 1):
            Ei |= ak.shift(Mi, d, d)
        Ei &= ~M
        pic.put(ak.dilate(Mi, 1) & ~Mi & allE & ~Ei, "black")


if __name__ == "__main__":
    import boxart
    print(boxart.save(draw(), HERE.parent / "docs" / "cart.png"))
