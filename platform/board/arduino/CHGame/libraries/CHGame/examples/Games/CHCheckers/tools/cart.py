"""docs/cart.png, CHCheckers' cover in the visual menu (docs/cover-art.md).
`chgame boxart` redraws it; edit this, not the PNG.

THE BRIEF (revision 1)
  Message: RAMPAGE! The red king, a cartoon checker with an evil grin,
  comes flying in and ploughs into a row of the house's navy men, who are
  knocked flying in terror. It reads as checkers at a glance (a red side
  and a dark side, ridged round pieces, a crown, the board), then as the
  game's show: a multi-jump nothing can stop.

  Composition:
  - The title on black at the top (y 3-31): nothing else near it.
  - The focal point, the king, right of centre (about 52 px across): two
    men stacked, a checker on edge like a wheel, turned to show his milled
    band on his trailing (upper right) side, a black seam between his two
    men, his face a recessed field in a raised rim. He leans left into the
    hit. His face is stamped by hand: brows slammed down into a V, eyes cut
    by them and glaring down-left at the man he is flattening, a grin of
    gritted teeth from cheek to cheek. A crown of three points sits upright
    on his top edge, so on the leaning king it reads as blown back by his
    speed; its centre jewel is the picture's one rainbow pixel pair (it
    turns through the colours on the Rainbow menu, magenta on Static).
  - His flight: three curved streaks from just off his back to the top
    right (cream at the root through tan to wine, a black edge under each),
    a red back light on his band's trailing edge.
  - The hit, the "right now": a comic burst (cream points, a tan ring, a
    coral heart, black outline) between his lower left rim and the nearest
    man, two shards flying off it.
  - The men, three navy checkers with steel faces, in an arc up and away to
    the left (near and big on the board, then up, then far and small),
    each tilted its own way so its ridged band shows. Terrified faces,
    stamped: wide eyes with pinprick pupils on the king, brows pushed up, a
    screaming O. The king's red light catches the side of each that faces
    him; motion arcs trail off the two in the air.
  - Behind: a low camera over the game's diamond board (tan and felt
    squares, one flat level each, crisp edges), lit in a pool round the hit
    and falling off to brown, felt0 and the dark toward the frame and far
    off (where it sinks into the glow); the king's shadow lies to his lower
    right. A navy glow (one plateau, a dithered seam) stands behind the
    action as a stage; the corners, the top and the frame stay black.
  - Order of reading: the title, the king's face, the burst, the near man,
    the men flying.
  Light: the house key from the top left: the king's face and rim by their
  profile (a raised rim, a groove, the field) as levels on the red ramp,
  terraced so they step in flat bands; his band by its waved normal (the
  milling); the men painted by rules (small pieces shaded per sample come
  out speckled): a groove ring, a grey rim toward the lamp with a cream
  glint, night away from it, the band milled with ticks.

PALETTE (11 own + cream, grey, black, red, and rainbow for two pixels)
  night, steel        the men (with black, grey and cream) and the glow
  felt0, felt1        the board's dark squares
  tan0, tan1          the board's light squares, the crown, the streaks
  wine, coral         the king (with black, red and cream), the board's
                      frame and far squares, the title's depth
  gold0, gold1, gold2 the title's own: nothing else uses them

FONT  title.txt: MIRRORED FONT by Scoopex, from the bmf collection (author
      and terms not stated: a `?` face, chosen for its chunky, embossed
      block letters at their own size), its mirrored lower rows left off and
      C, E, C, E and S one column narrower. Set in gold chrome bands (a
      horizon line), a cream and gold0 bevel on the outer contour, a 3 px
      wine extrusion, black outline and shadow, two glints.
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
    "night": "#0C1030", "steel": "#4A6498",
    "felt0": "#0B3A2A", "felt1": "#1D7A44",
    "tan0": "#8C4824", "tan1": "#E8AA56",
    "wine": "#5E0A22", "coral": "#FF7452",
    "gold0": "#A4500C", "gold1": "#F4B41C", "gold2": "#FFEE84",
}

# ---- the board: a diamond (the game's isometric table) under a low camera
THETA = 45.0                      # the board's turn (degrees): 45 shows it as diamonds, as the game does
CAM = dict(pos=(0.0, 4.0, 9.0), aim=(0.0, 0.0, -1.0), fov=50, shift=(14, 10))
# the light on it: where it is brightest (a picture point), how bright and how fast it falls off; the
# fall into the dark far off (camera distance), toward the frame, and on its far left (board units:
# where it starts, how wide) so the men fly over the glow
POOL = dict(at=(76, 102), top=1.38, fall=0.24, far=(9.0, 15.0), edge=0.55, left=(-0.6, 1.2))
SHADOWS = [(98, 102, 1.5, 0.6), (36, 112, 0.8, 0.35)]   # the king's and the near man's: picture point, radii (board units)
GLOW = dict(at=(72, 78), rx=76, ry=42, edge=0.95, soft=0.06)   # the navy glow behind the action (an ellipse)

# ---- the pieces: analytic checkers seen orthographically (picture terms:
# x right, y down, z toward us). Each: middle, radius (px), half thickness
# (px), the face's normal, roll (degrees, + clockwise).
KING = dict(c=(83, 71), r=24.0, h=9.0, n=(-0.44, 0.40, 0.80), roll=-14)
MEN = [dict(name="far", c=(34, 48), r=11.0, h=3.2, n=(0.52, -0.30, 0.80), roll=28),
       dict(name="mid", c=(15, 70), r=13.0, h=3.6, n=(-0.30, 0.56, 0.77), roll=-30),
       dict(name="near", c=(31, 93), r=16.0, h=4.4, n=(0.50, -0.36, 0.79), roll=22, sq=(0.88, 1.08, -20))]
KFACE_AT = (0.0, 0.08)                # where its middle sits on the face (radii)
KFACE = [
    ".kkk........................kkk.",
    ".kkkkkk..................kkkkkk.",
    ".kkkkkkkkk............kkkkkkkkk.",
    "kccckkkkkkkkk......kkkkkkkkkccck",
    "kcccccckkkkkkkk..kkkkkkkkcccccck",
    "kcckkkcccckkkkk..kkkkkccccccccck",
    ".kckkkccccccckk..kkckkkccccccck.",
    "..kkkkcccccccck..kcckkkcccccck..",
    "...kkccccccckk....kkkkkcccckk...",
    ".....kkkkkkk........kkkkkkk.....",
    "................................",
    "...kkkk..................kkkk...",
    "...kccckkkkkkkkkkkkkkkkkkccck...",
    "....kcccgcccgcccgcccgcccgcck....",
    ".....kccgcccgcccgcccgcccgck.....",
    "......kcgcccgcccgcccgcccgk......",
    ".......kkkkkkkkkkkkkkkkkk.......",
    "........kcgcccgcccgcccgk........",
    ".........kgcccgcccgccck.........",
    "..........kkccgcccgckk..........",
    "............kkkkkkkk............",
    "................................",
]
MFACE_AT = 0.06                    # where the men's faces sit (radii down the face)
MFACE = {
    "near": [
        ".....kk....kk.....",
        "...kk........kk...",
        ".kk............kk.",
        "..cccc......cccc..",
        ".cccccc....cccccc.",
        ".cccccc....cccccc.",
        ".cccckc....cccckc.",
        ".cccckc....cccckc.",
        ".cccccc....cccccc.",
        "..cccc......cccc..",
        ".......kkkk.......",
        "......kkkkkk......",
        "......kkkkkk......",
        "......kkkkkk......",
        "......kkrrkk......",
        ".......kkkk.......",
    ],
    "mid": [
        "...kk....kk...",
        ".kk........kk.",
        "..ccc....ccc..",
        ".ccccc..ccccc.",
        ".ccckc..ccckc.",
        ".ccckc..ccckc.",
        ".ccccc..ccccc.",
        "..ccc....ccc..",
        "......kk......",
        ".....kkkk.....",
        ".....kkkk.....",
        ".....krrk.....",
        "......kk......",
    ],
    "far": [
        "...k...k...",
        ".kk.....kk.",
        "..cc...cc..",
        ".cccc.cccc.",
        ".cckc.cckc.",
        ".cccc.cccc.",
        "..cc.k.cc..",
        "....kkk....",
        "....krk....",
        ".....k.....",
    ],
}
CROWN_AT = (73, 34)                # its top left corner
CROWN = [
    "............kkk............",
    "...........kCtTk...........",
    ".kkk.......ktTTk.......kkk.",
    "kCtTk.......kkk.......ktTTk",
    "ktTTk......kCCCk......kTTwk",
    ".kkk......kCttttk......kkk.",
    "kCCCk.....kCttttk.....kttTk",
    "kCtttk...kCttttttk...ktTTTk",
    "kCttttk..kCttttttk..ktTTTTk",
    "kCtttttkkCttttttttkktTTTTTk",
    "kCttttttkCttttttttkCTTTTTTk",
    "kC" + "t" * 18 + "T" * 6 + "k",
    "k" + "T" * 19 + "w" * 6 + "k",
    "kCttttorttttRRrtttttrrTTTTk",
    "kCttttrwttttrrwtttttrwTTTTk",
    "k" + "T" * 19 + "w" * 6 + "k",
    ".kkkkkkkkkkkkkkkkkkkkkkkkk.",
]
BURST = dict(at=(57, 87), ro=14.5, ri=7.5)           # the hit: middle, outer and inner radius
BURST_SHARDS = [(262, 19, 4.2, 1.5), (104, 18, 3.4, 1.2)]   # angle, distance, length, half width
FLUNG = {"far": [(-10, 70, 3), (2, 56, 6)], "mid": [(-40, 22, 3), (-28, 8, 6)]}   # motion arcs: from, to (degrees), gap (px)
SLIVER = 60                        # pieces of the board smaller than this (px) give way to the dark
MAN = dict(field=0.70, rim=0.82, band_lit=-0.30, band_hi=0.55, ridge_px=3.4, red_from=0.2)
L3 = np.array([-0.55, -0.75, 0.45])
L3 = L3 / np.linalg.norm(L3)
H3 = L3 + np.array([0.0, 0.0, 1.0])
H3 = H3 / np.linalg.norm(H3)


def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def coin(X, Y, c, r, h, n, roll=0.0, sq=None):
    """An upright cylinder (a checker) seen orthographically: per sample, what
    it hits (0 nothing, 1 the front face, 2 the band), the face's coordinates
    (u right, v down, in radii), the band's angle and height (-1..1) and its
    normal (picture terms). sq=(along, across, degrees) squashes it on the
    picture, a cartoon's impact."""
    M = np.eye(2)
    if sq:
        a_ = np.radians(sq[2])
        Rm = np.array([[np.cos(a_), -np.sin(a_)], [np.sin(a_), np.cos(a_)]])
        M = Rm @ np.diag([sq[0], sq[1]]) @ Rm.T
        Mi = np.linalg.inv(M)
        dx, dy = X - c[0], Y - c[1]
        X, Y = c[0] + Mi[0, 0] * dx + Mi[0, 1] * dy, c[1] + Mi[1, 0] * dx + Mi[1, 1] * dy
    n = unit(n)
    dn = np.array([0.0, 1.0, 0.0])
    ev = unit(dn - (dn @ n) * n)
    eu = unit(np.cross(ev, n))
    a = np.radians(roll)
    eu, ev = np.cos(a) * eu + np.sin(a) * ev, -np.sin(a) * eu + np.cos(a) * ev
    px, py = X - c[0], Y - c[1]
    ax0 = px * n[0] + py * n[1]
    u0 = px * eu[0] + py * eu[1]
    v0 = px * ev[0] + py * ev[1]
    zc = (h - ax0) / n[2]
    uc, vc = u0 + zc * eu[2], v0 + zc * ev[2]
    cap = uc * uc + vc * vc <= r * r
    A = eu[2] ** 2 + ev[2] ** 2
    B = 2 * (u0 * eu[2] + v0 * ev[2])
    Cq = u0 * u0 + v0 * v0 - r * r
    disc = B * B - 4 * A * Cq
    zs = (-B + np.sqrt(np.maximum(disc, 0))) / (2 * max(A, 1e-9))
    asd = ax0 + zs * n[2]
    us, vs = u0 + zs * eu[2], v0 + zs * ev[2]
    side = (disc >= 0) & (np.abs(asd) <= h) & (A > 1e-6)
    kind = np.where(cap, 1, np.where(side, 2, 0))
    nrm = (us[..., None] * eu + vs[..., None] * ev) / r
    return dict(kind=kind, u=uc / r, v=vc / r, th=np.arctan2(vs, us), a=asd / h, nrm=nrm,
                eu=eu, ev=ev, n=n, c=c, r=r, h=h, M=M)


def profile(rho):
    """The slope of a checker's face across its radius (dh/drho, in radii):
    the flat field, a groove, the raised ring, the rounded rim."""
    s = np.zeros_like(rho)
    s = np.where((rho > 0.66) & (rho <= 0.71), -1.6, s)
    s = np.where((rho > 0.71) & (rho <= 0.77), 1.6, s)
    s = np.where(rho > 0.88, -4.0 * np.clip((rho - 0.88) / 0.12, 0, 1), s)
    return s


def lit(cn, ridges, amp):
    """Per sample: the light on the face (by its profile) and on the band
    (milled: its normal waved round it)."""
    u, v = cn["u"], cn["v"]
    rho = np.hypot(u, v)
    eu, ev, n = cn["eu"], cn["ev"], cn["n"]
    rad = (u[..., None] * eu + v[..., None] * ev) / np.maximum(rho, 1e-6)[..., None]
    Nf = n[None, None, :] - profile(rho)[..., None] * rad
    Nf /= np.linalg.norm(Nf, axis=-1, keepdims=True)
    th = cn["th"]
    tang = -np.sin(th)[..., None] * eu + np.cos(th)[..., None] * ev
    Nb = cn["nrm"] + amp * np.sin(ridges * th)[..., None] * tang
    Nb /= np.maximum(np.linalg.norm(Nb, axis=-1, keepdims=True), 1e-6)
    face = cn["kind"] == 1
    N = np.where(face[..., None], Nf, Nb)
    dif = np.clip(N @ L3, 0, 1)
    spec = np.clip(N @ H3, 0, 1) ** 30
    return dif, spec


def to_px(cn, S, dif, spec):
    """A checker's samples averaged to pixels: its masks, face coordinates,
    the light on each part."""
    k = cn["kind"]
    m = ak.px_mean((k > 0).astype(np.float32), S) >= 0.5
    fcap = ak.px_mean((k == 1).astype(np.float32), S)
    fside = ak.px_mean((k == 2).astype(np.float32), S)
    face = m & (fcap >= fside)
    band = m & ~face

    def mean(a, sel):
        w = sel.astype(np.float32)
        return ak.px_mean(a * w, S) / np.maximum(ak.px_mean(w, S), 1e-6)
    u, v = mean(cn["u"], k == 1), mean(cn["v"], k == 1)
    a = mean(cn["a"], k == 2)
    fd, fs = mean(dif, k == 1), mean(spec, k == 1)
    bd, bs = mean(dif, k == 2), mean(spec, k == 2)
    bn = np.stack([mean(cn["nrm"][..., i], k == 2) for i in range(3)], -1)
    cs, sn = mean(np.cos(cn["th"]), k == 2), mean(np.sin(cn["th"]), k == 2)
    return dict(m=m, face=face, band=band, u=u, v=v, rho=np.hypot(u, v), a=a, bn=bn, th=np.arctan2(sn, cs),
                dif=np.where(face, fd, bd), spec=np.where(face, fs, bs))


def face_xy(cn, fu, fv, depth=None):
    """Where a point of the face (radii) lands on the picture (depth: along
    the axis, in half thicknesses; the face is at 1)."""
    d = 1.0 if depth is None else depth
    p = cn["n"] * cn["h"] * d + (cn["eu"] * fu + cn["ev"] * fv) * cn["r"]
    q = cn["M"] @ p[:2]
    return cn["c"][0] + q[0], cn["c"][1] + q[1]


def draw():
    P_ = ak.Palette(COL, ramps=[["black", "night", "steel", "grey", "cream"], ["black", "felt0", "felt1"],
                                ["black", "wine", "tan0", "tan1", "cream"],
                                ["black", "wine", "red", "coral", "cream"],
                                ["gold0", "gold1", "gold2", "cream"]])
    cv = ak.Canvas("#000000")
    S = cv.s
    yy, xx = np.mgrid[0:128, 0:128]
    X1, Y1 = xx + 0.5, yy + 0.5
    pic = ak.Picture.blank(P_, "black")

    # ---- the dark: a navy glow behind the action, a plateau with a dithered seam
    g = np.hypot((X1 - GLOW["at"][0]) / GLOW["rx"], (Y1 - GLOW["at"][1]) / GLOW["ry"])
    ak.by_level(pic, np.clip((GLOW["edge"] - g) / GLOW["soft"] + 0.5, 0, 1), ["black", "night"],
                np.ones((128, 128), bool), q=4)
    dark_idx = pic.idx.copy()                  # the dark as painted (what shows where the board is cut away)

    # ---- the board
    c_, s_ = np.cos(np.radians(THETA)), np.sin(np.radians(THETA))

    def to_board(p):
        return p[..., 0] * c_ + p[..., 2] * s_, -p[..., 0] * s_ + p[..., 2] * c_
    cam = R.Camera(CAM["pos"], CAM["aim"], fov=CAM["fov"], shift=CAM["shift"])
    o, d = cam.rays(cv.X.reshape(-1).astype(np.float64), cv.Y.reshape(-1).astype(np.float64))
    down = d[:, 1] < -1e-6
    t = np.where(down, -o[:, 1] / np.where(down, d[:, 1], -1), 1e3)
    hp = o + d * np.minimum(t, 1e3)[:, None]
    u, v = to_board(hp)
    u, v = u.reshape(cv.N, cv.N), v.reshape(cv.N, cv.N)
    t = t.reshape(cv.N, cv.N)
    on = (np.abs(u) < 4) & (np.abs(v) < 4) & (t < 1e3)
    rim = (np.abs(u) < 4.4) & (np.abs(v) < 4.4) & ~on & (t < 1e3)
    par = (np.floor(u) + np.floor(v)) % 2 == 0
    sq_on = ak.px_mean(on.astype(np.float32), S)
    sq_rim = ak.px_mean(rim.astype(np.float32), S)
    board = sq_on >= 0.5
    rimm = ~board & (sq_on + sq_rim >= 0.5)
    dark_sq = ak.at_px(par, S)                 # each pixel's square by its centre, as its light is
    ub, vb = ak.at_px(u, S), ak.at_px(v, S)
    dist = ak.at_px(t, S)

    def board_at(sx, sy):
        o1, d1 = cam.rays(np.array([sx], float), np.array([sy], float))
        q = o1[0] + d1[0] * (-o1[0, 1] / d1[0, 1])
        return to_board(q)
    # the light: a pool round the action, sinking into the dark far off and
    # toward the frame; each square one flat level (its mean), so the
    # squares' edges stay crisp
    pu, pv = board_at(*POOL["at"])
    light = POOL["top"] - POOL["fall"] * np.hypot(ub - pu, vb - pv)
    light -= np.clip((dist - POOL["far"][0]) / (POOL["far"][1] - POOL["far"][0]), 0, 1) * 0.6
    edge = np.maximum.reduce([np.clip((12 - X1) / 12, 0, 1), np.clip((X1 - 104) / 24, 0, 1),
                              np.clip((Y1 - 110) / 18, 0, 1)])
    light -= edge * POOL["edge"]
    light -= np.clip((POOL["left"][0] - ub) / POOL["left"][1], 0, 1)        # its far left sinks into the glow behind the men
    sq = (np.floor(ub).astype(int) + 20) * 64 + (np.floor(vb).astype(int) + 20)
    sq = np.clip(sq, 0, 64 * 64 - 1)
    cnt = np.bincount(sq[board], minlength=64 * 64)
    mean = np.bincount(sq[board], light[board], minlength=64 * 64) / np.maximum(cnt, 1)
    light = mean[sq]
    # the pieces' shadows: a step darker (an ellipse wider than a square,
    # so its curve reads across the squares)
    sh = np.zeros((128, 128))
    for sx_, sy_, ru_, rv_ in SHADOWS:
        su, sv = board_at(sx_, sy_)
        du, dv = ub - su, vb - sv
        e = np.hypot((du - dv) / np.sqrt(2) / ru_, (du + dv) / np.sqrt(2) / rv_)
        c1 = e < 1.0
        sh = np.maximum(sh, np.where(c1, 1.0, 0.0))
    for where_, cuts, ramp in ((board & ~dark_sq, [0.10, 0.40, 0.76], ["black", "wine", "tan0", "tan1"]),
                               (board & dark_sq, [0.20, 0.60], ["black", "felt0", "felt1"])):
        xs = [2 * cuts[0] - cuts[1]] + cuts + [2 * cuts[-1] - cuts[-2]]
        lv = np.round(np.interp(light, xs, [-0.5] + [k + 0.5 for k in range(len(cuts))] + [len(cuts) + 0.5]))
        lv = np.maximum(lv - sh, np.minimum(lv, 1))              # a shadow never sinks a square to black
        ak.by_level(pic, np.clip(lv, 0, len(ramp) - 1), ramp, where_, q=4)
    # where the board sinks to black far off, the dark behind shows instead
    # (a black wedge would cut a hole in the glow)
    sunk = board & pic.where("black")
    pic.idx[sunk] = dark_idx[sunk]
    # the board's wood frame, where the board near it still shows
    rimm &= ak.dilate(board & ~sunk, 3)
    pic.put(rimm, "wine")
    ak.despeckle(pic, need=4, within=board | rimm)

    # ---- the pieces
    king = coin(cv.X, cv.Y, KING["c"], KING["r"], KING["h"], KING["n"], KING["roll"])
    kd, ks = lit(king, 44, 0.9)
    kp = to_px(king, S, kd, ks)
    men = {}
    for mn in MEN:
        cn = coin(cv.X, cv.Y, mn["c"], mn["r"], mn["h"], mn["n"], mn["roll"], mn.get("sq"))
        dd, ss_ = lit(cn, 30, 0.9)
        men[mn["name"]] = (cn, to_px(cn, S, dd, ss_))
    kx, ky = KING["c"]

    # ---- the king's flight: concentric arcs from just off his back, cream
    # at the root through tan to wine, tapering, a dark edge under each
    clear = ak.dilate(kp["m"], 2)
    streaks = np.zeros((128, 128), bool)
    for root, ctrl, end, r0 in (((106, 52), (116, 40), (130, 37), 2.2),
                                ((110, 62), (120, 52), (131, 49), 1.8),
                                ((108, 76), (119, 68), (131, 63), 1.4)):
        streaks |= ak.streak(pic, root, ctrl, end, r0, 0.3, ok=~clear,
                             cols=(("cream", 0.25), ("tan1", 0.55), ("tan0", 0.8), ("wine", 1.0)))
    pic.put(ak.shift(streaks, 0, 1) & ~streaks & ~clear, "black")

    def paint_coin(cn, cp, kind):
        m, face, band = cp["m"], cp["face"], cp["band"]
        rho = cp["rho"]
        d0 = max(float(cn["n"] @ L3), 0.0)
        # the face: its rings by the light, the field a flat colour with a
        # sheen toward the lamp and a shade away from it
        q = np.stack([X1 - face_xy(cn, 0, 0)[0], Y1 - face_xy(cn, 0, 0)[1]], -1) / cn["r"]
        tow = q @ unit((-0.6, -0.8))
        lev = 2.0 + 3.2 * (cp["dif"] - d0) + 2.5 * cp["spec"]
        field = face & (rho <= 0.66)
        sheen = np.clip((tow - 0.30) / 0.12, 0, 1) * 0.75 - np.clip((-tow - 0.40) / 0.12, 0, 1) * 0.75
        lev = np.where(field, 2.0 + sheen, lev)
        blev = 0.7 + 2.4 * cp["dif"] + 2.0 * cp["spec"]
        ramp = ["black", "wine", "red", "coral", "cream"] if kind == "king" else ["black", "night", "steel", "grey", "cream"]
        ak.by_level(pic, ak.terrace(np.clip(lev, 0, 4), 0.3), ramp, face, q=2)
        ak.put_levels(pic, band, np.clip(np.round(blev), 0, 3).astype(int), ramp)
        if kind == "king":
            pos = band & (cp["a"] >= 0)
            pic.put(pos & ak.nbrs(band & ~pos), "black")                  # the seam between his two men
            # a back light on his trailing edge (from the glow he came out
            # of): the band's outermost pixels where they face up and right
            back = band & ~ak.erode(m, 1) & ((cp["bn"] @ unit((0.75, -0.66, 0.0))) > 0.55)
            pic.put(back & ~pic.where("coral", "cream"), "red")
        pic.put(band & ak.nbrs(face) & ~ak.shift(face, 0, 1) & ~ak.shift(face, 1, 0), ramp[1])
        pic.put(ak.dilate(m, 1) & ~m, "black")

    def paint_man(cn, cp):
        """A man painted by rules (small: shading worked out per sample comes
        out speckled): a steel face with a clean groove ring, its rim lit
        grey toward the lamp and night away from it; the band steel or
        night by its normal, milled with ticks; the king's red on the side
        that faces him."""
        m, face, band = cp["m"], cp["face"], cp["band"]
        rho = cp["rho"]
        fx0, fy0 = face_xy(cn, 0, 0)
        dx, dy = X1 - fx0, Y1 - fy0
        dl = np.maximum(np.hypot(dx, dy), 1e-6)
        tow = (dx * -0.6 + dy * -0.8) / dl                       # 1 toward the lamp, -1 away
        tk = (dx * (kx - fx0) + dy * (ky - fy0)) / dl / np.hypot(kx - fx0, ky - fy0)   # 1 toward the king
        pic.put(face, "steel")
        field = face & (rho <= MAN["field"])
        pic.put(face & ak.nbrs(field) & ~field & (tow > -0.45), "night")          # the groove
        rimz = face & (rho > MAN["rim"])
        pic.put(rimz & (tow > 0.30), "grey")
        pic.put(rimz & (tow < -0.30), "night")
        pic.put(rimz & (tow > 0.88) & (rho > 0.9), "cream")
        pic.put(field & (rho > MAN["field"] - 0.16) & (tow > 0.55), "grey")       # a sheen inside the groove
        lam = cp["bn"] @ L3
        pic.put(band, "night")
        pic.put(band & (lam > MAN["band_lit"]), "steel")
        pic.put(band & (lam > MAN["band_hi"]), "grey")
        nr = int(round(2 * np.pi * cn["r"] / MAN["ridge_px"]))
        ki = np.floor((cp["th"] + np.pi) / (2 * np.pi) * nr).astype(int)
        tick = band & ((ki != ak.shift(ki, 1, 0)) & ak.shift(band, 1, 0)) & (cp["bn"][..., 2] > 0.3)
        lit_b = pic.where("steel", "grey") & tick
        pic.put(tick & ~lit_b, "black")
        pic.put(lit_b, "night")
        pic.put(m & ~ak.erode(m, 1) & (tk > MAN["red_from"]), "wine")              # the king's red light
        pic.put(ak.dilate(m, 1) & ~m, "black")

    for nm in ("far", "mid"):
        paint_man(*men[nm])
    paint_coin(king, kp, "king")
    paint_man(*men["near"])

    # ---- the king's face, stamped by hand (a face this size drawn from
    # shapes comes out blobby): brows slammed down into a V, the eyes cut
    # by them and glaring down-left at the man he is flattening, a grin of
    # gritted teeth from cheek to cheek
    fx, fy = face_xy(king, *KFACE_AT)
    ak.patch(pic, int(round(fx - len(KFACE[0]) / 2)), int(round(fy - len(KFACE) / 2)), KFACE,
             {"k": "black", "c": "cream", "g": "grey", "w": "wine", "o": "coral", "r": "red"})

    # ---- the men's faces, stamped: eyes popping on the king (whites,
    # pinprick pupils), brows pushed up in fear, a screaming O
    for nm, (cn, cp) in men.items():
        st = MFACE[nm]
        x_, y_ = face_xy(cn, 0.0, MFACE_AT)
        ak.patch(pic, int(round(x_ - len(st[0]) / 2)), int(round(y_ - len(st) / 2)), st,
                 {"k": "black", "c": "cream", "r": "red"})

    # ---- the crown, stamped by hand: three points with a ball on each, a
    # band with three jewels, lit tan with a cream bevel toward the lamp,
    # its right quarter in shade. It sits upright on the leaning king, so
    # it reads as blown back by his speed
    ak.patch(pic, CROWN_AT[0], CROWN_AT[1], CROWN,
             {"k": "black", "C": "cream", "t": "tan1", "T": "tan0", "w": "wine", "r": "red", "o": "coral",
              "R": "rainbow"})

    # ---- impact: a comic burst in front of them both
    def burst(cx, cy, ro, ri, n, seed, rot0=0.0):
        pts = []
        for k in range(2 * n):
            a_ = np.radians(rot0 + k * 180.0 / n)
            j = ak.ihash(k + 7 * seed, seed)
            r = (ro * (0.78 + 0.4 * j)) if k % 2 == 0 else ri * (0.9 + 0.2 * j)
            pts.append((cx + r * np.cos(a_), cy + r * np.sin(a_)))
        return ak.polygon(cv.P, pts)
    bx_, by_ = BURST["at"]
    B = burst(bx_, by_, BURST["ro"], BURST["ri"], 9, 3, -14)
    Bm = ak.px_mean((B < 0).astype(np.float32), S) >= 0.5
    B2 = burst(bx_, by_, 8.5, 4.5, 9, 4, -4)
    B2m = ak.px_mean((B2 < 0).astype(np.float32), S) >= 0.5
    pic.put(ak.dilate(Bm, 1) & ~Bm, "black")
    pic.put(Bm, "cream")
    pic.put(B2m, "tan1")
    pic.put(ak.erode(B2m, 1) & ak.shift(ak.erode(B2m, 1), 1, 1), "coral")
    # shards of the hit flying off to the left, each a cream wedge outlined
    shards = np.zeros((128, 128), bool)
    for ang_, dist_, ln, w_ in BURST_SHARDS:
        a_ = np.radians(ang_)
        dv = np.array([np.cos(a_), np.sin(a_)])
        pv = np.array([-dv[1], dv[0]])
        c0 = np.array([bx_, by_]) + dist_ * dv
        tri = [tuple(c0 + dv * ln), tuple(c0 - dv * ln * 0.5 + pv * w_), tuple(c0 - dv * ln * 0.5 - pv * w_)]
        shards |= ak.px_mean((ak.polygon(cv.P, tri) < 0).astype(np.float32), S) >= 0.5
    shards &= ~ak.dilate(Bm, 1)
    pic.put(ak.dilate(shards, 1) & ~shards & ~Bm, "black")
    pic.put(shards, "cream")

    # ---- slivers of the board caught between the pieces and the burst
    # (small pieces of it cut off from the rest) give way to the dark behind:
    # they read as specks
    covered = ak.dilate(Bm, 1) | ak.dilate(shards, 1) | ak.dilate(kp["m"], 1)
    for cn_, cp_ in men.values():
        covered |= ak.dilate(cp_["m"], 1)
    left = (board | rimm) & ~covered & ~pic.where("black")
    while left.any():
        ys_, xs_ = np.nonzero(left)
        part = np.zeros((128, 128), bool)
        part[ys_[0], xs_[0]] = True
        while True:
            grown = ak.dilate(part, 1, diag=True) & left
            if (grown == part).all():
                break
            part = grown
        if part.sum() < SLIVER:
            pic.idx[part] = dark_idx[part]
        left &= ~part

    # ---- the men knocked flying: motion arcs hugging the trailing edge of
    # each one in the air (the side toward the hit), grey in the middle
    # and steel at the ends; lines hanging below them would read as legs
    for nm, arcs in FLUNG.items():
        cn = men[nm][0]
        for a0, a1, gap_ in arcs:
            rr = cn["r"] + gap_
            pts = [(cn["c"][0] + rr * np.cos(np.radians(a)), cn["c"][1] + rr * np.sin(np.radians(a)))
                   for a in np.linspace(a0, a1, 24)]
            ak.ink(pic, pts, None, colours=[("steel", 0.22), ("grey", 0.78), ("steel", 1.0)],
                   where=~kp["m"] & ~ak.dilate(Bm, 1))

    # ---- the frame: the outer two rows and columns a step darker, so the
    # menu's border sits on dark
    fr = np.zeros((128, 128), bool)
    fr[:2, :] = fr[-2:, :] = fr[:, :2] = fr[:, -2:] = True
    step = {"tan1": "tan0", "felt1": "felt0", "tan0": "wine", "cream": "tan1", "coral": "red", "steel": "night",
            "grey": "steel", "red": "wine"}
    was = {a_: pic.where(a_) for a_ in step}
    for a_, b_ in step.items():
        pic.put(fr & was[a_], b_)

    # ---- the title: gold chrome, alone on the dark
    m1 = ak.load_mask(TITLE)
    x1, y1 = ak.centred_x(m1) - 1, 3
    t1 = ak.title(pic, m1, x1, y1, fill=None,
                  rows=["gold2"] * 6 + ["gold1"] * 5 + ["gold0", "gold2"] + ["gold1"] * 5 + ["gold0"] * 4,
                  hi=None, lo=None, extrude=dict(dx=1, dy=1, depth=3, side="wine", bottom="wine"),
                  shadow=dict(dx=1, dy=2, colour="black"))
    TF = t1["face"]
    ak.bevel_contour(pic, TF, "cream", "gold0")
    blk = pic.where("black") & t1["all"] & ~ak.dilate(TF, 1, diag=True)
    wn = pic.where("wine")
    pic.put(blk & ((ak.shift(wn, 0, 1) & ak.shift(wn, 0, -1)) | (ak.shift(wn, 1, 0) & ak.shift(wn, -1, 0))), "wine")
    notch = pic.where("black") & t1["all"] & ak.shift(wn, 0, 1) & ak.shift(wn, 0, -1)
    pic.put(notch, "wine")
    for gx, gy, sz in [(3, 2, 2), (65, 2, 1)]:
        ak.glint(pic, *ak.glint_in(TF, x1 + gx, y1 + gy, sz), sz, tip="gold2")
    return pic.image()


if __name__ == "__main__":
    import boxart
    print(boxart.save(draw(), HERE.parent / "docs" / "cart.png"))
