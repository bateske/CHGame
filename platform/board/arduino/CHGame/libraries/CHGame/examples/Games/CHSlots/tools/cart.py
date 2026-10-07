"""docs/cart.png, CHSlots' cover in the visual menu (docs/cover-art.md).
`chgame boxart` redraws it; edit this, not the PNG.

THE BRIEF (revision 2)
  Message: JACKPOT! The instant the third 7 lands: the machine blazes, the
  sign says it, and the money erupts out of it and flies at you.

  Composition (a thumbnail in words):
  - Focal point: 777 on the payline, a little left of centre, in the lower
    middle. A red one-armed bandit in a clean three-quarter view from its
    right (so its lever shows), the camera level with the sign: true
    two-point perspective, verticals upright, every line on the front
    running to one vanishing point far off to the left (the sign level, the
    window's edges leaning a little more the lower they are). It fills the
    middle of the frame below the title, a clear black gap between them.
  - The window is the brightest big shape: three backlit drums, cream on
    the payline falling to pearl, steel and black toward the bezel. Three
    red 7s, embossed (rose on the edges facing the key, wine on the
    others), rimmed in amber lit on the upper left, inked; a cream star of
    light on the third, one diagonal glint (pearl, cream, pearl) on the
    glass at the top left.
  - The bezel: polished chrome (pearl on top and left, grey and steel
    right and below, a cream lip), set with chaser bulbs in the rainbow
    colour (they turn through the colour wheel on the Rainbow menu), each
    with a cream filament; no bulb is drawn where a coin would cut it.
  - The marquee: JACKPOT in neon on black glass (cream tubes, a solid red
    halo hugging them, wine beyond), level: the second read.
  - The cabinet: red lacquer lit from the upper left in flat bands with
    narrow seams: rose by the top-left corner and along the top and left
    edges, a cream specular on the top edge toward the key, red, then wine
    low down and along the right; the side panel in shade, wine falling to
    black toward the back.
  - The payout tray: chrome, its lip pearl with a cream specular at the
    lit end, its front in steel shade, a black mouth and a black shadow
    under it; below it everything is black (the install bar's band).
  - The lever: a chrome shaft lit on the left, a chrome hub, a glossy red
    ball (rose, a cream hot spot, wine core).
  - The money: a fountain out of the tray. Small coins just out of it, by
    the ledge, casting shadows on the machine; then up and out on both
    sides, growing as they come at the viewer, the nearest breaking the
    left and right edges and the bottom; two small dark ones at the crest.
    Every coin: amber gold lit from the upper left (coin2 falling to coin1
    across the face), a cream rim toward the key, a struck ring on the big
    ones, a $ stamped in wine on the face-on ones, the milled edge in
    shade, inked. Curved 1-px speed lines (gold, amber, wine) follow the
    arcs back toward the tray behind the six nearest, over the room and
    the dark lacquer only.
  - Behind: the blaze, flat violet wedges (dusk) on black from the 777,
    night next to the machine, seams only where wedges meet, falling to
    black at the frame and ending in an arch under the title's band. Two
    cream glints in the air.
  - The title: SLOTS across the top band, big, bouncy and cartoon-heavy,
    in gold chrome (a pale sky, gold, a dark horizon, its bright
    reflection, gold, a short dark ground), a 1-px red lip and wine depth,
    inked, a drop shadow, bevelled on its outer contour (cream up and
    left, gold0 down and right), the S's thin hooks flat gold, glints on
    the gold below the S's and the T's top left. Nothing else uses its
    gold; the black band round it keeps it the first read.
  - The frame: the outer two rows and columns step every colour down two
    or three levels, so the installed border sits on dark.
  Reading order: SLOTS, JACKPOT, 777, the coins.

  Palette (11 own + cream, grey, black, red, and the rainbow colour):
    night dusk            the room: the blaze's wedges (with black)
    steel pearl           chrome (with grey, black, cream), the reels' falloff
    wine rose             red lacquer's shade and light (with red, cream);
                          wine also the coins' rims, their $ and the title's depth
    coin1 coin2           the coins' amber gold (with wine, cream), the 7s' rims
    gold0 gold1 gold2     the title's own: nothing else uses them
  Lettering: title.txt, SLOTS in "ONE HUNDRED AND SEVENTY THREE" (the bmf
  collection; author and terms not stated: a `?` face, chosen because no
  clear-terms face has its bouncy cartoon weight at this size; set with a
  1-px letter gap; touched up by hand: the T's stem straight, the L's toe
  an even diagonal). jackpot.txt, JACKPOT in Chunky Monkey by Damien Guard
  (ZX Origins: free for games, with a credit).
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import numpy as np  # noqa: E402
import artkit as ak  # noqa: E402
from artkit import render3d as R  # noqa: E402

TITLE = HERE / "art" / "title.txt"
TITLE_ROWS = ["gold2"] * 6 + ["gold1"] * 5 + ["gold0"] + ["gold2"] * 3 + ["gold1"] * 10 + ["gold0"] * 3
SIGN = HERE / "art" / "jackpot.txt"

PAL = {
    "night": "#160D3A", "dusk": "#40258F",
    "wine": "#5C0A22", "rose": "#FF7A6E",
    "steel": "#4E5C82", "pearl": "#B4C0DA",
    "coin1": "#CC6A10", "coin2": "#FFB238",
    "gold0": "#985008", "gold1": "#FFD23C", "gold2": "#FFF4B0",
}
BG = ["black", "night", "dusk"]
CABR = ["black", "wine", "red", "rose", "cream"]
CHR = ["black", "steel", "grey", "pearl", "cream"]
REELR = ["black", "steel", "pearl", "cream"]
COINR = ["black", "wine", "coin1", "coin2", "cream"]

# one step darker: shadows and the frame
DARKER = {"red": "wine", "rose": "red", "cream": "pearl", "pearl": "grey", "grey": "steel", "steel": "black",
          "wine": "black", "coin2": "coin1", "coin1": "wine", "rainbow": "wine", "night": "black",
          "dusk": "night", "gold2": "gold1", "gold1": "gold0"}

YY, XX = np.mgrid[0:128, 0:128]
KEY = np.array([-0.5, 0.7, 0.5])
KEY = KEY / np.linalg.norm(KEY)

# ---- the machine (world: x right, y up, z toward the viewer; its front at z = ZF) --------

CAB, BEZEL, REEL0, REEL1, REEL2, KNOB, DARK, HUB, LEVER, GLASS, TRAY = range(11)
NMAT = 11
ZF = 0.3
HW = 0.56                                      # the cabinet's half width
TOP = 1.305                                    # its top
PAY_Y = 0.80                                   # the payline's height
WIN = (0.41, 0.215)                            # the window's half size
BEZ = 0.06                                     # the bezel's width
REEL_R = 0.34                                  # the reels' radius
REEL_Z = ZF - 0.03 - REEL_R                    # their axis' depth
REEL_X = (-0.272, 0.0, 0.272)
REEL_HL = 0.122                                # half a reel's width
MARQ_Y = 1.172                                 # the sign's middle
PANEL = (0.44, 0.076)                          # its glass panel's half size
TRAY_P = (0.0, 0.415, ZF + 0.10)               # the payout tray under the window
TRAY_H = (0.42, 0.05, 0.11)
HUB_P = (HW + 0.04, 0.80, -0.02)
KNOB_P = (HW + 0.14, 1.13, 0.10)
KNOB_R = 0.075
# the camera level with the sign: two-point perspective, verticals upright
CAM = R.Camera((1.5, MARQ_Y, 3.3), (0.05, MARQ_Y, ZF), fov=28, shift=(-6, -12))

SEVEN = [(-1.0, 1.0), (1.0, 1.0), (1.0, 0.56), (0.16, -1.0), (-0.52, -1.0), (0.36, 0.44), (-1.0, 0.44)]
SEVEN_H = 0.118                                # half a 7's height on the reel (world)

# the money: a fountain out of the payout tray. Each coin: where it is on
# the picture, its width there (px), its turn about the view axis and its
# tilt toward the camera (0 face on, 90 edge on), and the control point of
# the arc it flew along from the tray (None: no trail)
SRC = (52.0, 103.0)                            # the tray's mouth on the picture
COINS = [
    (14, 47, 5, 10, 50, None), (121, 45, 5, -20, 40, None),                      # far, at the crest
    (40, 99, 6, 20, 62, None), (66, 98, 6, -25, 58, None),                       # just out of the tray
    (25, 90, 8, -30, 45, None), (91, 94, 9, 35, 50, None),                       # rising
    (15, 75, 12, 35, 35, (24, 104)), (109, 100, 12, -20, 40, (86, 112)),          # nearer
    (6, 56, 17, -30, 28, (0, 98)), (121, 77, 17, 40, 32, (118, 108)),             # the nearest, breaking the frame
    (28, 118, 14, 15, 40, (40, 104)), (92, 121, 16, -20, 38, (76, 106)),          # at the viewer, low
]
SPARKLES = [(5, 93, 2), (124, 60, 1)]                # glints in the air
COIN_R, COIN_T = 0.04, 0.0065
FPX = 64.0 / np.tan(np.radians(14.0))          # the camera's focal length in pixels (fov 28)


def coin_nodes(cam):
    out = []
    for k, (sx, sy, wpx, turn, tilt, _arc) in enumerate(COINS):
        dist = min(2 * COIN_R * FPX / wpx, 3.05)          # no farther than the tray: the far ones are made smaller
        size = wpx * dist / (2 * COIN_R * FPX)
        o, d = cam.rays(np.array([sx + 0.5]), np.array([sy + 0.5]))
        pos = o[0] + d[0] * dist
        f = -cam.f
        ax = np.cos(np.radians(turn)) * cam.r + np.sin(np.radians(turn)) * cam.u
        a = np.radians(tilt)
        axis = f * np.cos(a) + np.cross(ax, f) * np.sin(a)
        y = axis / np.linalg.norm(axis)
        x = np.cross(y, ax if abs(ax @ y) < 0.9 else cam.f)
        x /= np.linalg.norm(x)
        z = np.cross(x, y)
        rot = np.stack([x, y, z], axis=1)
        # the face's own up and right: the picture's up laid on the coin
        up_ = cam.u - (cam.u @ y) * y
        up_ /= np.linalg.norm(up_)
        rt_ = np.cross(up_, y)
        if rt_ @ cam.r < 0:
            rt_ = -rt_
        out.append(dict(k=NMAT + k, pos=pos, rot=rot, r=COIN_R * size, axis=y, up=up_, right=rt_, w=wpx,
                        tilt=tilt, node=R.xf(R.prim(R.cylinder(COIN_R * size, COIN_T * size, 0.004), NMAT + k),
                                             pos, rot)))
    return out


def rounded_slab(f2, h, rr):
    """A 2D outline f2(x, y) extruded 2h deep, its edges rounded by rr."""
    ex = R.extrude(lambda x, y: f2(x, y) + rr, h - rr)
    return lambda p: ex(p) - rr


def scene(extra=()):
    sil = lambda x, y: ak.box((x, y), 0, (TOP - 0.6) / 2, HW, (TOP + 0.6) / 2, 0.13)   # noqa: E731
    body = R.prim(rounded_slab(sil, 0.3, 0.05), CAB)
    body = R.Sub(body, R.xf(R.prim(R.box((PANEL[0], PANEL[1], 0.02), 0.012), GLASS), (0, MARQ_Y, ZF)))
    body = R.Sub(body, R.xf(R.prim(R.box((WIN[0], WIN[1], 0.4)), DARK), (0, PAY_Y, ZF)))
    bez = R.Sub(R.xf(R.prim(R.box((WIN[0] + BEZ, WIN[1] + BEZ, 0.025), 0.025), BEZEL), (0, PAY_Y, ZF + 0.005)),
                R.xf(R.prim(R.box((WIN[0], WIN[1], 0.1)), BEZEL), (0, PAY_Y, ZF)))
    reels = [R.xf(R.prim(R.cylinder(REEL_R, REEL_HL), REEL0 + k), (x, PAY_Y, REEL_Z), R.rot_z(90))
             for k, x in enumerate(REEL_X)]
    hub = R.xf(R.prim(R.cylinder(0.085, 0.05, 0.012), HUB), HUB_P, R.rot_z(90))
    lever = R.prim(R.capsule((HUB_P[0] + 0.03, HUB_P[1], HUB_P[2]), KNOB_P, 0.026), LEVER)
    knob = R.xf(R.prim(R.sphere(KNOB_R), KNOB), KNOB_P)
    tray = R.Sub(R.xf(R.prim(R.box(TRAY_H, 0.03), TRAY), TRAY_P),
                 R.xf(R.prim(R.box((TRAY_H[0] - 0.025, TRAY_H[1], TRAY_H[2] - 0.025), 0.02), TRAY),
                      (TRAY_P[0], TRAY_P[1] + 0.03, TRAY_P[2])))
    return R.U(body, bez, *reels, hub, lever, knob, tray, *extra)


def geometry(cam, sc, nmat):
    """What each pixel shows (the majority of 2 x 2 rays), and at the
    pixel's centre the surface point and its normal."""
    big = ak.Canvas("#000000")
    out = R.render(big, sc, cam, [R.Mat("#FFFFFF", spec=0.0)] * nmat, lights=[(tuple(KEY), "#FFFFFF", 1.0)],
                   ambient="#303030", ss=2, shadows=False, ao=False)
    mat = R.majority(out, big.s)
    one = ak.Canvas("#000000", ss=1)
    o1 = R.render(one, sc, cam, [R.Mat("#FFFFFF", spec=0.0)] * nmat, lights=[(tuple(KEY), "#FFFFFF", 1.0)],
                  ambient="#000000", ss=None, shadows=False, ao=False)
    o, d = cam.rays((XX + 0.5).reshape(-1).astype(np.float64), (YY + 0.5).reshape(-1).astype(np.float64))
    dep = o1["depth"].reshape(-1)
    z = np.where(np.isfinite(dep), dep, 0)
    p = (o + d * z[:, None]).reshape(128, 128, 3)
    n = o1["normal"].astype(np.float64)
    return dict(mat=mat, p=p, n=n)


def reel_uv(cam, k, ss=4):
    """Each pixel's ss x ss samples on reel k: u across it (-1..1), s along
    its rim from the payline (world units, up positive); NaN where a ray
    misses it."""
    c = (np.arange(128 * ss) + 0.5) / ss
    X, Y = np.meshgrid(c, c)
    o, d = cam.rays(X.reshape(-1), Y.reshape(-1))
    oy, oz = o[:, 1] - PAY_Y, o[:, 2] - REEL_Z
    a = d[:, 1] ** 2 + d[:, 2] ** 2
    b = 2 * (oy * d[:, 1] + oz * d[:, 2])
    cc = oy ** 2 + oz ** 2 - REEL_R ** 2
    disc = b * b - 4 * a * cc
    t = (-b - np.sqrt(np.maximum(disc, 0))) / (2 * a)
    h = o + d * t[:, None]
    u = (h[:, 0] - REEL_X[k]) / REEL_HL
    s = np.arctan2(h[:, 1] - PAY_Y, h[:, 2] - REEL_Z) * REEL_R
    ok = (disc > 0) & (np.abs(u) <= 1)
    u = np.where(ok, u, np.nan).reshape(128 * ss, 128 * ss)
    s = np.where(ok, s, np.nan).reshape(128 * ss, 128 * ss)
    return u, s


def seven_cov(u, s, ss=4):
    """How much of each pixel the reel's 7 covers."""
    d = ak.polygon((u * 0.8, s / SEVEN_H), [(x * 0.8, y) for x, y in SEVEN])
    inside = np.where(np.isnan(u), False, d < 0)
    return inside.reshape(128, ss, 128, ss).mean(axis=(1, 3))


DOLLAR = ["..#..",                             # the coins' $, a hand stamp
          ".####",
          "#.#..",
          ".###.",
          "..#.#",
          "####.",
          "..#.."]


def smooth(a, b, v):
    t = np.clip((v - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def draw():
    P = ak.Palette(PAL, ramps=[BG, CABR, CHR, REELR, COINR, ["gold0", "gold1", "gold2", "cream"]])
    pic = ak.Picture.blank(P, "black")
    cam = CAM
    coins = coin_nodes(cam)
    G = geometry(cam, scene([c["node"] for c in coins]), NMAT + len(coins))
    mat, p, n = G["mat"], G["p"], G["n"]
    on = {k: mat == k for k in range(NMAT)}
    nx = (n * cam.r).sum(-1)                   # the normal on the picture: right
    ny = (n * cam.u).sum(-1)                   # up
    wz = n[..., 2]
    room = mat < 0
    mach = (mat >= 0) & (mat < NMAT)
    allc = mat >= NMAT
    proj = cam.project
    fx, fy = p[..., 0], p[..., 1]

    # ---- the room: the blaze, a burst of flat wedges from the 777, dusk on
    # black with night next to the machine, seams only where wedges meet,
    # dark at the frame and dying out before the title's band
    cx, cy = proj((0.0, PAY_Y, ZF))
    ang = np.degrees(np.arctan2(YY + 0.5 - cy, XX + 0.5 - cx))
    SEG = 12.0
    a = (ang + 360 + 5.0) / SEG
    frac = a - np.floor(a)
    bright = (np.floor(a) % 2) == 0
    rr = np.hypot(XX + 0.5 - cx, YY + 0.5 - cy)
    seam_px = np.minimum(frac, 1 - frac) * np.radians(SEG) * rr     # how far from the wedge's edge
    w = np.clip(seam_px / 1.0, 0, 1)
    w = np.where(bright, 0.5 + 0.5 * w, 0.5 - 0.5 * w)               # 1 deep in a bright wedge, 0 in a dark one
    dm = ak.distance_px(mach, 40)
    hi_ = 2.0 - smooth(9, 14, dm) - smooth(17, 24, dm)
    lo_ = 1.0 - smooth(2, 7, dm)
    lv = w * hi_ + (1 - w) * lo_
    edge_d = np.minimum(np.minimum(XX, 127 - XX), np.minimum(YY, 127 - YY)) + 0.5
    lv = lv * smooth(1.5, 6, edge_d)                                   # the frame: dark
    arch = 38.0 + 0.0016 * (XX + 0.5 - cx) ** 2                        # the title's band stays calm: the
    lv = lv * smooth(arch + 1.5, arch + 7.0, YY)                       # blaze ends in an arch under it
    ak.by_level(pic, ak.terrace(np.maximum(lv, 0), 0.3), BG, room, q=4)

    # ---- the cabinet: red lacquer
    cab = on[CAB]
    front = cab & (wz > 0.9)
    side = cab & (n[..., 0] > 0.9)
    edge = cab & ~front & ~side & ((np.abs(p[..., 0]) > HW - 0.08) | (p[..., 1] > TOP - 0.08))
    front = cab & ~side & ~edge                                      # (creases by the tray count as front)
    u_, v_ = fx + HW, TOP - fy                                         # from the front's top-left corner
    # the front: lacquer lit from the upper left, in flat bands (rose by the
    # top-left corner, red, wine low down), rose along the top and left
    # edges, a step darker along the right edge; black under the tray
    t_ = u_ * 0.55 + v_                                                 # 0 at the corner nearest the key
    lvf = 3.0 - smooth(0.10, 0.16, t_) - smooth(0.80, 0.86, t_)
    lvf = lvf + smooth(0.05, 0.02, v_) + smooth(0.05, 0.02, u_)       # the edges facing the key
    lvf = lvf - smooth(0.035, 0.015, HW - fx)
    lvf = np.clip(lvf, 1.0, 3.0)
    lvf = np.where(fy < TRAY_P[1] + 0.02, 0.0, lvf)
    lvc = np.where(front, lvf, 2.0)
    # the rounded edges: lit facing the key, dark turned away
    lit_e = (n * KEY).sum(-1)
    spec_e = lit_e - 0.25 * smooth(0.25, 0.6, u_)                     # the specular: toward the key
    lvc = np.where(edge, np.where(spec_e > 0.8, 4.0, np.where(lit_e > 0.5, 3.0, np.where(lit_e > 0.1, 2.0, 1.0))), lvc)
    lvc = np.where(edge & (n[..., 0] > 0.3), np.minimum(lvc, np.maximum(lvf, 1.0) + (lvf > 1.5)), lvc)
    lvc = np.where(edge & (fy < TRAY_P[1]), np.minimum(lvc, 1.0), lvc)
    # the side: wine at the front edge, falling to black toward the back
    lvc = np.where(side, 1.0 - smooth(0.12, -0.12, p[..., 2]), lvc)
    lvc = np.where(side & (fy < TRAY_P[1]), np.minimum(lvc, 0.5), lvc)
    ak.by_level(pic, ak.terrace(lvc, 0.3), CABR, cab, q=4)

    # ---- the bezel: polished chrome round the window
    bz = on[BEZEL]
    flat = bz & (wz > 0.9)
    rail_top = flat & (fy > PAY_Y + WIN[1])
    rail_bot = flat & (fy < PAY_Y - WIN[1])
    rail_l = flat & ~rail_top & ~rail_bot & (fx < 0)
    rail_r = flat & ~rail_top & ~rail_bot & (fx > 0)
    pic.put(bz, "steel")
    pic.put(rail_top, "pearl")
    pic.put(rail_l, "pearl")
    pic.put(rail_r, "grey")
    pic.put(rail_bot, "steel")
    rnd = bz & ~flat
    pic.put(rnd & (ny > 0.35), "cream")
    pic.put(rnd & (ny < -0.35), "black")
    pic.put(rnd & (nx < -0.35) & (np.abs(ny) <= 0.35), "pearl")
    pic.put(rnd & (nx > 0.35) & (np.abs(ny) <= 0.35), "black")

    # ---- the payout tray: a chrome bin under the window, its lip pearl with
    # a cream specular toward the key, its front in shade, a black mouth and a
    # black shadow under it
    tr = on[TRAY]
    pz = p[..., 2]
    t_front = TRAY_P[2] + TRAY_H[2]
    tfront = tr & (wz > 0.9) & (pz > t_front - 0.012)
    inside = tr & (pz < t_front - 0.02) & (fy < TRAY_P[1] + TRAY_H[1] - 0.004)
    lvt = np.where(ny > 0.45, np.where(fx < -0.22, 4.0, 3.0), np.where(nx < -0.5, 2.0, 1.0))
    lvt = np.where(tfront, 1.0 + smooth(TRAY_P[1] + 0.02, TRAY_P[1] + 0.04, fy) - smooth(TRAY_P[1] + 0.0, TRAY_P[1] - 0.03, fy), lvt)
    ak.by_level(pic, ak.terrace(lvt, 0.3), CHR, tr, q=2)
    pic.put(tr & ~tfront & ~inside & (ny > 0.2) & (ny <= 0.45), "pearl")
    pic.put(inside | (tr & ~tfront & (pz < t_front - 0.035)), "black")    # the mouth and its far rim, in shade
    pic.put(cab & (ak.shift(tr, 0, 1) | ak.shift(tr, 0, 2)) & ~tr, "black")

    # ---- the lever and the hub: chrome, lit on the left
    lev = on[LEVER]
    pic.put(lev, "grey")
    pic.put(lev & (nx < -0.25), "pearl")
    pic.put(lev & (nx < -0.65), "cream")
    pic.put(lev & (nx > 0.35), "steel")
    pic.put(lev & (nx > 0.7), "black")
    hb = on[HUB]
    cap = hb & (n[..., 0] > 0.8)
    drum = hb & ~cap
    pic.put(drum, "grey")
    pic.put(drum & (ny > 0.35), "pearl")
    pic.put(drum & (ny > 0.8), "cream")
    pic.put(drum & (ny < -0.3), "steel")
    pic.put(cap, "steel")
    pic.put(cap & ~ak.erode(cap, 1) & (ak.shift(drum, 0, 1) | ak.shift(drum, 1, 0)), "grey")
    pic.put(on[DARK], "black")

    # ---- the marquee: JACKPOT in neon on black glass
    gl = on[GLASS]
    pic.put(gl, "black")
    sm = ak.load_mask(SIGN)
    gx, gy = proj((0.0, MARQ_Y, ZF))
    sign = ak.place(sm, int(round(gx - sm.shape[1] / 2)), int(round(gy - sm.shape[0] / 2)))
    halo1 = ak.dilate(sign, 1) & ~sign
    halo2 = ak.dilate(sign, 1, diag=True) & ~sign & ~halo1
    pic.put(ak.dilate(sign, 2) & ~sign & gl, "wine")
    pic.put(halo2, "wine")
    pic.put(halo1, "red")
    pic.put(sign, "cream")

    # ---- reels: backlit, a bloom on the payline; a red 7 on each
    for k in range(3):
        m = on[REEL0 + k]
        u, s = reel_uv(cam, k)
        sa = np.abs(np.where(np.isnan(s), 1.0, s))
        bands = np.digitize(sa, [0.15, 0.195, 0.215])                 # 0 cream .. 3 black
        votes = np.stack([(bands == j).reshape(128, 4, 128, 4).mean(axis=(1, 3)) for j in range(4)], -1)
        lvr = 3 - votes.argmax(-1)
        ak.put_levels(pic, m, lvr, REELR)
        sv = (seven_cov(u, s) >= 0.5) & m
        ring1 = ak.dilate(sv, 1) & ~sv & m
        ring2 = ak.dilate(sv | ring1, 1) & ~(sv | ring1) & m
        pic.put(ring2, "black")
        pic.put(ring1, "coin1")
        lit_rim = ring1 & (ak.shift(sv, -1, -1) | ak.shift(sv, 0, -1) | ak.shift(sv, -1, 0))
        pic.put(lit_rim, "coin2")
        pic.put(sv, "red")
        # embossed: rose on the edges facing the key (top, left), wine on
        # the others (bottom, right; they win at the corners)
        top_e, left_e = sv & ~ak.shift(sv, 0, 1), sv & ~ak.shift(sv, 1, 0)
        bot_e, right_e = sv & ~ak.shift(sv, 0, -1), sv & ~ak.shift(sv, -1, 0)
        pic.put(top_e | left_e, "rose")
        pic.put(bot_e | (right_e & ~top_e), "wine")

    # one glint on the glass over the reels' top left (pearl, cream, pearl),
    # and a star of light on the nearest 7
    reels_m = on[REEL0] | on[REEL1] | on[REEL2]
    wx0, wy0 = proj((-WIN[0], PAY_Y + WIN[1], ZF))
    ak.ink(pic, [(wx0 + 2.5, wy0 + 10.5), (wx0 + 10.5, wy0 + 2.5)], None, where=reels_m,
           colours=[("pearl", 0.2), ("cream", 0.75), ("pearl", 1.0)])
    s3 = on[REEL2] & pic.where("red", "rose")
    ys3, xs3 = np.nonzero(s3)
    if len(xs3):
        j = np.argmin(xs3 + ys3 * 1.5)
        gx3, gy3 = ak.glint_in(s3, int(xs3[j]) + 2, int(ys3[j]) + 1, 1, 3)
        ak.glint(pic, gx3, gy3, 2, tip="rose")

    # ---- the bulbs round the bezel: the rainbow colour, a cream filament;
    # only where a coin hides none of it
    cover_c = ak.dilate(allc, 1)
    bulbs = np.zeros((128, 128), bool)
    hw, hh = WIN[0] + BEZ * 0.5, WIN[1] + BEZ * 0.5
    per = 2 * (2 * hw + 2 * hh)
    nb = 30
    for i in range(nb):
        t = (i + 0.5) / nb * per
        if t < 2 * hw:
            wx, wy = -hw + t, PAY_Y + hh
        elif t < 2 * hw + 2 * hh:
            wx, wy = hw, PAY_Y + hh - (t - 2 * hw)
        elif t < 4 * hw + 2 * hh:
            wx, wy = hw - (t - 2 * hw - 2 * hh), PAY_Y - hh
        else:
            wx, wy = -hw, PAY_Y - hh + (t - 4 * hw - 2 * hh)
        bx, by = proj((wx, wy, ZF + 0.03))
        bx, by = int(np.floor(bx - 0.5)), int(np.floor(by - 0.5))
        if cover_c[max(by - 1, 0):by + 3, max(bx - 1, 0):bx + 3].any():
            continue
        ak.patch(pic, bx - 1, by - 1, [".kk.", "kcrk", "krrk", ".kk."], {"k": "wine", "c": "cream", "r": "rainbow"})
        bulbs[max(by - 1, 0):by + 3, max(bx - 1, 0):bx + 3] = True

    # ---- the knob: a glossy red ball
    kw = np.array(KNOB_P)
    kx, ky = proj(kw)
    kr = np.hypot(*(np.array(proj(kw + KNOB_R * cam.r)) - (kx, ky)))
    ux, uy = (XX + 0.5 - kx) / kr, (YY + 0.5 - ky) / kr
    ball = ux * ux + uy * uy <= 1.0
    uz = np.sqrt(np.clip(1 - ux * ux - uy * uy, 0, 1))
    kl_ = np.array([-0.55, -0.6, 0.58])
    kl_ /= np.linalg.norm(kl_)
    sh_ = ux * kl_[0] + uy * kl_[1] + uz * kl_[2]
    pic.put(ak.dilate(ball, 1, diag=True) & ~ball, "black")
    pic.put(ball, "red")
    pic.put(ball & (sh_ > 0.72), "rose")
    pic.put(ball & (sh_ < 0.22), "wine")
    pic.put(ball & (((ux + 0.38) / 0.26) ** 2 + ((uy + 0.42) / 0.2) ** 2 <= 1), "cream")

    # ---- the coins' shadows on the machine (the ones close to it), down and
    # to the right; lights (bulbs, the knob's spot) keep their light
    for c in coins:
        if c["w"] > 9:
            continue
        m = mat == c["k"]
        sh = ak.shift(m, 2, 3) & mach & ~m & ~bulbs & ~ball & ~pic.where("rainbow")
        before = pic.idx.copy()
        for a_, b_ in DARKER.items():
            pic.idx[sh & (before == P[a_])] = P[b_]

    # ---- the trails: clean 1-px speed lines along the arcs the coins flew
    # from the tray (gold, amber, wine; the middle one doubled near the coin),
    # over the room and the dark lacquer only
    trail_ok = room | (on[CAB] & pic.where("black", "wine"))
    for c, spec in zip(coins, COINS):
        arc = spec[5]
        if arc is None:
            continue
        m = mat == c["k"]
        ys_, xs_ = np.nonzero(m)
        if not len(xs_):
            continue
        P2 = np.array((xs_.mean() + 0.5, ys_.mean() + 0.5))
        P0, P1 = np.array(SRC), np.array(arc, float)
        rad = c["w"] / 2
        for off, t0, thick_ in ((-0.5, 0.5, 0), (0.0, 0.3, 1), (0.5, 0.6, 0)):
            # the arc's last stretch, from the coin back toward the tray
            B0 = (1 - t0) ** 2 * P0 + 2 * t0 * (1 - t0) * P1 + t0 * t0 * P2
            Q1 = (1 - t0) * P1 + t0 * P2
            tg = P2 - Q1
            tg = tg / max(np.hypot(*tg), 1e-6)
            side_ = np.array((-tg[1], tg[0]))
            nrm = side_ * rad * off
            pts = ak.bezier(tuple(P2 + nrm), tuple(Q1 + nrm * 0.6), tuple(B0 + nrm * 0.2), n=16)
            ak.ink(pic, pts, None, where=trail_ok, colours=[("coin2", 0.25), ("coin1", 0.6), ("wine", 1.0)])
            if thick_:                                                  # the middle one doubled near the coin
                k_ = len(pts) // 2
                ak.ink(pic, [(x + side_[0], y + side_[1]) for x, y in pts[:k_]], None, where=trail_ok,
                       colours=[("coin2", 0.5), ("coin1", 1.0)])

    # ---- the coins: amber gold lit from the upper left (coin2 falling to
    # coin1 across the face), a raised rim (cream toward the key, coin1 and
    # wine away from it), a struck ring and a $ on the big ones, the milled
    # edge in shade, inked all round
    order = sorted(coins, key=lambda c: -np.linalg.norm(c["pos"] - cam.pos))
    for i, c in enumerate(order):
        m = mat == c["k"]
        if not m.any():
            continue
        loc = n @ c["rot"]
        face = m & (np.abs(loc[..., 1]) > 0.7)
        rim = m & ~face
        q = p - c["pos"]
        uu = (q @ c["right"]) / c["r"]
        vv = (q @ c["up"]) / c["r"]
        lit = np.clip(vv * 0.75 - uu * 0.65, -1.2, 1.2)
        far = c["w"] <= 5                                               # the far ones: a step darker
        lvl = 3.0 - far + 0.45 * lit
        ak.by_level(pic, ak.terrace(lvl, 0.35), COINR, face, q=4)
        pic.put(rim, "wine" if far else "coin1")
        pic.put((rim & (ny < -0.3)) | (rim & (nx > 0.5)), "wine")
        bound = face & ~ak.erode(face, 1)
        pic.put(bound & (lit > 0.15), "coin2" if far else "cream")
        pic.put(bound & (lit < -0.25), "wine" if far else "coin1")
        if c["w"] >= 11:
            # the struck ring, a step in from the rim: dark on its lit side
            # (in the rim's shadow), light on the other
            rho = np.hypot(uu, vv)
            ring_ = face & (rho > 0.62) & (rho <= 0.80) & ak.erode(face, 1)
            pic.put(ring_ & (lit > 0), "coin1")
            pic.put(ring_ & (lit <= 0), "coin2")
        dm_ = np.zeros((128, 128), bool)
        if c["w"] >= 13 and c["tilt"] <= 45:
            # a $ struck in the face: a hand stamp, wine, centred on it
            fyy, fxx = np.nonzero(face)
            cxf, cyf = int(round(fxx.mean() - 2.5)), int(round(fyy.mean() - 3.5))
            for yy_, row in enumerate(DOLLAR):
                for xx_, ch in enumerate(row):
                    if ch == "#" and face[cyf + yy_, cxf + xx_]:
                        pic.px(cxf + xx_, cyf + yy_, "wine")
                        dm_[cyf + yy_, cxf + xx_] = True
        if c["w"] >= 11:
            fyy, fxx = np.nonzero(face)
            gx_, gy_ = ak.glint_in(face & pic.where("coin2", "cream"), int(fxx.mean() - c["w"] * 0.2),
                                   int(fyy.mean() - c["w"] * 0.2), 1, 3)
            ak.glint(pic, gx_, gy_, 1)
        nearer = np.zeros((128, 128), bool)
        for c2 in order[i + 1:]:
            nearer |= mat == c2["k"]
        pic.put(ak.dilate(m, 1) & ~m & ~nearer, "black")

    # lone pixels: the edges' crumbs (bulbs and glints kept)
    keep = pic.where("rainbow", "cream") | ak.dilate(pic.where("rainbow"), 1)
    ak.despeckle(pic, 5, keep=keep, passes=2)

    # ---- sparkles in the air: the jackpot's glitter, on the dark room only
    for sx_, sy_, sz_ in SPARKLES:
        ak.glint(pic, sx_, sy_, sz_, tip="pearl" if sz_ > 1 else None)

    # ---- the title: gold chrome (a pale sky, gold, a dark horizon, its
    # bright reflection, gold, a short dark ground), a 1-px red lip and wine
    # depth, inked, a drop shadow, bevelled on its outer contour
    tm = ak.load_mask(TITLE)
    tx, ty = ak.centred_x(tm) - 1, 3
    rows = TITLE_ROWS
    TM = ak.place(tm, tx, ty)
    # the pockets between the letters (with their depth and shadow) shut in black
    foot = TM
    for k in range(1, 4):
        foot = foot | ak.shift(TM, k, k)
    foot = ak.dilate(foot, 1)
    foot = foot | ak.shift(foot, 1, 2) | ak.shift(foot, 1, 1)
    closed = ak.erode(ak.dilate(foot, 3, diag=True), 3, diag=True)
    pic.put(closed & ~foot, "black")
    T = ak.title(pic, tm, tx, ty, fill=None, rows=rows, hi=None, lo=None,
                 extrude=dict(dx=1, dy=1, depth=3, colours=["red", "wine", "wine"]),
                 shadow=dict(dx=1, dy=2, colour="black"))
    M = T["face"]
    # soft seams between the bands, only where the strokes are wide
    wide = ak.thick(M, 2)
    for r, col in ((ty + 6, "gold2"), (ty + 25, "gold1")):
        row = np.zeros_like(M)
        row[r, :] = True
        pic.put(row & wide & ak.checker(), col)
    # each letter parted from its neighbours' depth
    lab = ak.letters(M)
    for i in range(1, lab.max() + 1):
        Mi = lab == i
        Ei = np.zeros_like(Mi)
        for k in range(1, 4):
            Ei |= ak.shift(Mi, k, k)
        Ei &= ~M
        pic.put(ak.dilate(Mi, 1) & ~Mi & T["extrude"] & ~Ei, "black")
    ak.bevel_contour(pic, M, "cream", "gold0")
    TA = T["all"] | ak.shift(T["all"], 1, 2)
    ak.despeckle(pic, 3, within=ak.dilate(TA, 1))
    # the thin hooks of the S's: flat gold1, a gold0 edge on their right
    rn_ = ak.runs(M, 1)
    hook = M & (rn_ <= 3) & (YY >= ty + 5) & (YY <= ty + 12)
    pic.put(hook, "gold1")
    pic.put(hook & ~ak.shift(M, -1, 0) & (rn_ >= 2), "gold0")
    # the key catches the gold below the first S's and the T's top left
    for gx_, gy_ in ((tx + 7, ty + 8), (tx + 78, ty + 8)):
        gx2, gy2 = ak.glint_in(M & pic.where("gold1"), gx_, gy_, 2, 4)
        ak.glint(pic, gx2, gy2, 2, tip="gold2")

    # ---- the frame: the outer two rows and columns step down into the dark
    fr1 = np.zeros((128, 128), bool)
    fr1[[0, -1], :] = True
    fr1[:, [0, -1]] = True
    fr2 = ak.dilate(fr1, 1) & ~fr1
    pic.idx[(fr1 | fr2) & allc & (pic.idx == P["cream"])] = P["coin2"]    # a coin's glint dims to gold, not grey
    for rng, steps in ((fr2, 2), (fr1, 3)):
        for _ in range(steps):
            before = pic.idx.copy()
            for a_, b_ in DARKER.items():
                pic.idx[rng & (before == P[a_])] = P[b_]
    return pic.image()


def title_lines():
    """The title's lettering as drawn here, and its depth, for the title
    screen (tools/titleart.py: the game paints it in the house gold)."""
    return [dict(mask=ak.load_mask(TITLE), depth=3, side="wine")]


if __name__ == "__main__":
    import boxart
    boxart.save(draw(), HERE.parent / "docs" / "cart.png")
