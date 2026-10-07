"""docs/cart.png, Dominoes' picture in the visual menu (docs/cover-art.md).
`chgame boxart` redraws it; edit this, not the PNG.

THE BRIEF (revision 2)
  Message: the first push of a chain reaction. The double six, the king of
  the set, comes crashing down onto a line of standing tiles, and the rest
  are next. At a glance: "dominoes" (twelve crisp pips on the biggest,
  brightest tile) and "here it goes" (the tilt, the swish behind it, the
  comic crash where it hits). It is what the game ends on: play your last
  tile and the whole line goes off.
  Composition: one strong diagonal from the lower left to the upper right.
  - Camera: low over the felt, a 54-degree lens, rolled 7 degrees (a Dutch
    angle) so the whole picture leans the way the chain falls.
  - The tiles are a real 3D chain (render3d): feet placed along a line given
    as picture points, each tile square to it; the double six tilted about
    its leading foot until it touches the struck tile (an SDF contact search),
    so the lean is physically right.
  - Front left, the hero: the double six, the biggest and only all-cream
    thing, leaning about 40 degrees, its pips facing us, its foot clear of
    the install bar.
  - Middle: the struck tile, just going (9 degrees), and the crash on its
    top corner: a fat ten-spiked star, red with a cream heart, ringed in
    black (the only red in the picture).
  - Right and back: two more standing tiles marching out of the frame, a
    level darker each, their faces stamped with pips (3-5, 5-1: the line
    is played end to end, as in the game).
  - Left: three speed lines, the arcs the hero's lit edge swept as it fell,
    bowed a little, staggered in length, cream at the root tapering through
    ivory2 to ivory1, each with a dark felt edge under it.
  - Top: the title on the black room above the felt, 5 rows of black
    between it and anything below.
  Light: a lamp above and to the front left (the house key). Every surface
  is painted as a level on its ramp from the render's geometry, not through
  the quantiser:
  - Tiles face by face, flat: faces lit toward the top (the far ones a level
    lower: haze), top ends a level above their face, long sides slate, a
    black seam where tiles overlap and on each shadow side against the felt
    (none on the lit side). Pips are stamped from one round template a half
    (sized by the perspective), black; the hero's drilled (the lamp-side
    wall slate) and its bar an engraved 2-px groove.
  - The felt: a pool of light round the hero's foot (perspective ellipses,
    flat plateaus with narrow 25/50/75% seams) falling off with distance into
    the dark, a curved vignette to the frame, shade boxed in between tiles,
    and every tile's cast shadow to the lower right in two crisp steps.
  Title: DOMINOES across the top in a tall condensed face, gold chrome (a
  bright sky, a dark horizon band, its pale reflection, the ground), a
  4-deep carved depth in wine, black outline and drop shadow, a bevel on the
  outer contour only (cream on top/left, gold below the horizon; gold0 on
  the bottom/right), two four-point glints on the D's and the second O's
  corners. Nothing else uses the golds or the wine.
  Palette (11 own + cream, black, red; grey unused):
    felt0 felt1 felt2 felt3   the baize: teal-black shadows to a lime heart
    ivory0 ivory1 ivory2      the tiles, with cream above: slate (the cool
                              shadow side) to warm ivory
    gold0 gold1 gold2         the title's own
    wine                      the title's carved depth
    cream                     the hero's face, tops, speed lines, the crash's heart
    black                     the room, pips, seams, outlines
    red                       the crash
  Font: BAZAR from the bmf collection (bmf-cz; author not stated, terms
  "freeware", unclear: listed for the credits check), set at its own size
  (tools/art/title.txt; its header has the source).
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import numpy as np  # noqa: E402
import artkit as ak  # noqa: E402
from artkit import render3d as R  # noqa: E402

TITLE = HERE / "art" / "title.txt"
TITLE_Y = 2
TITLE_GLINTS = [(0, 1, (2, 3, 1, 3)), (75, 1, (3, 3, 1, 3))]
TITLE_ROWS = ["gold2"] * 12 + ["gold1"] * 5 + ["gold0"] * 2 + ["gold2"] * 2 + ["gold1"] * 9 + ["gold0"] * 5     # (x, y in the title, arms left, right, up, down)

# ---- the scene ----------------------------------------------------------------------

W, H, T = 1.0, 2.0, 0.36                       # a tile: width, height (standing), thickness
ROUND = 0.04                                   # its corners rounded
CAM = ((0.0, 3.6, 5.2), (0.8, 0.7, 0.0), 54)   # pos, target, fov
CAM_UP = (-0.12, 1.0, 0.0)                      # the camera's roll (a Dutch angle)
# the line on the felt, as picture points (where the tiles' feet stand): the
# double six's first, then the line it falls on, out of the right edge
LINE = [(22, 110), (54, 98), (84, 92), (112, 88), (138, 84), (164, 80)]
GAPS = (1.4, 1.32)                             # foot to foot: the double six to the next, then the rest
STRUCK_TILT = 9                                # the tile it hits, just going
FACES = [(6, 6), (6, 3), (3, 5), (5, 1), (1, 4), (4, 4), (4, 2), (2, 0), (0, 3)]   # (top, foot): end to end, as in play
# each tile's tones (levels on TILE_R): its face (below, above) the lamp's
# edge (`cut`, a fraction of the way up; `soft`, its seam), its long side, its top end
TONES = [dict(face=(3, 4), cut=0.14, soft=0.04, side=1, top=4),    # the double six
         dict(face=(3, 3), cut=0.6, soft=0.03, side=1, top=4),     # struck
         dict(face=(2, 3), cut=0.74, soft=0.05, side=1, top=4),
         dict(face=(2, 2), cut=0.5, soft=0.03, side=1, top=3)]
SUN = (-0.35, 0.92, -0.05)                       # the felt's cast shadows fall to the lower right, short
POOL_AT = (30, 86)                             # the pool's heart (a picture point on the felt)
FAR = (6.4, 8.8)                               # the felt fades out between these distances from the camera
VIG = (58, 70, 72, 62)                         # the vignette: centre, half-width, half-height (px)
POOL_SQUASH = 0.8                              # the pool is longer in depth than across
POOL = ([0, 1.2, 1.8, 3.6, 5.6, 7.6], [3.9, 3.5, 3.1, 2.5, 1.4, 0.2])   # the felt's level by distance
# speed lines: arcs the double six's lit edge swept, round its foot: from
# (x across, height up its face, as fractions), degrees back, radius at the root (px)
SWING = [(0.5, 1.0, 36, 2.6), (0.5, 0.8, 27, 2.2), (0.5, 0.6, 20, 1.8)]
SWING_BOW = 2.0                                # their middles bowed up (px), as cartoon arcs
BURST_AT = (1, -2)                             # the crash: offset from the contact (px)
BURST = dict(r_out=(11.0, 8.0), r_in=5.2, n=10, turn=-8.0, core=0.5)   # its spikes (long, short), body, count

FELT_R = ["black", "felt0", "felt1", "felt2", "felt3"]
TILE_R = ["black", "ivory0", "ivory1", "ivory2", "cream"]


def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def catmull(pts, k=40):
    P = np.vstack([pts[0], pts, pts[-1]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in np.linspace(0, 1, k, endpoint=False):
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-2])
    return np.array(out)


def ground_at(cam, sx, sy, h=0.0):
    o, d = cam.rays(np.array([sx], float), np.array([sy], float))
    return o[0] + d[0] * (h - o[0, 1]) / d[0, 1]


def pose(tl, tilt):
    """A tile's centre and rotation, tilted forward by `tilt` degrees about its
    front foot."""
    piv = tl["base"] + tl["R"][:, 2] * (T / 2)
    Rt = tl["R"] @ R.rot_x(tilt)
    return piv + Rt @ np.array([0, H / 2, -T / 2]), Rt


BOX = R.box((W / 2, H / 2, T / 2), ROUND)


def lean(tl, nxt):
    """The tilt at which a tile's face first touches the next tile (as posed)."""
    cn, Rn = pose(nxt, nxt["tilt"])
    loc = np.array([(x, y, T / 2 - 0.02) for x in np.linspace(-0.42, 0.42, 7) for y in np.linspace(0.2, H / 2 - 0.02, 8)])
    for a in np.arange(0, 86, 0.25):
        c, Rt = pose(tl, a)
        if (BOX((c + loc @ Rt.T - cn) @ Rn) < 0).any():
            return a
    return 86.0


def chain(cam):
    """The tiles along LINE, each square to it: the first (the double six)
    leaning on the second (struck, STRUCK_TILT), the rest standing."""
    pts = np.array([ground_at(cam, *p)[[0, 2]] for p in LINE])
    path = catmull(pts)
    seg = np.diff(path, axis=0)
    L = np.r_[0, np.cumsum(np.hypot(seg[:, 0], seg[:, 1]))]
    ts = []
    s = 0.0
    while s < L[-1] - 0.2 and len(ts) < len(FACES):
        x, z = np.interp(s, L, path[:, 0]), np.interp(s, L, path[:, 1])
        x2, z2 = np.interp(s + 0.05, L, path[:, 0]), np.interp(s + 0.05, L, path[:, 1])
        ez = unit((x2 - x, 0, z2 - z))
        ey = np.array([0, 1.0, 0])
        ts.append(dict(base=np.array([x, 0, z]), R=np.stack([np.cross(ey, ez), ey, ez], axis=1), tilt=0.0))
        s += GAPS[0] if len(ts) == 1 else GAPS[1]
    ts[1]["tilt"] = STRUCK_TILT
    ts[0]["tilt"] = lean(ts[0], ts[1])
    for i, tl in enumerate(ts):
        tl["c"], tl["Rt"] = pose(tl, tl["tilt"])
        tl["k"] = 1 + i
        tl["faces"] = FACES[i]
        tl["tone"] = TONES[min(i, len(TONES) - 1)]
    return ts


def face_point(t, x, yf, tilt):
    """A point on a tile's face toward us (x across, yf up it, as fractions
    of its width and height) as it stands at `tilt`."""
    piv = t["base"] + t["R"][:, 2] * (T / 2)
    return piv + (t["R"] @ R.rot_x(tilt)) @ np.array([x * W, yf * H, -T])


def top_point(t, x, tilt=None, out=0.0):
    """A point on a tile's top edge (x across, -0.5..0.5 of its width), on
    its back face, as it stands at `tilt` (its own by default), `out` above it."""
    piv = t["base"] + t["R"][:, 2] * (T / 2)
    Rt = t["R"] @ R.rot_x(t["tilt"] if tilt is None else tilt)
    return piv + Rt @ np.array([x * W, H + out, -T])


def smooth_faces(face, m, passes=2):
    """Which face each pixel shows, voted over its 3 x 3 neighbourhood (on
    the tile), so the rounded edges' mixed normals leave no notches."""
    for _ in range(passes):
        cnt = np.zeros((6,) + face.shape, int)
        for f in range(6):
            k = (m & (face == f)).astype(int)
            pad = np.pad(k, 1)
            cnt[f] = sum(pad[1 + dy:129 + dy, 1 + dx:129 + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1))
        best = cnt.argmax(0)
        own = np.take_along_axis(cnt, face[None], 0)[0]
        flip = m & (cnt.max(0) > own) & (own <= 3)
        face = np.where(flip, best, face)
    return face


# ---- pips -------------------------------------------------------------------------------

PIP_A = 0.25                                   # pip spacing in a half (tile width 1)
PIP_R = 0.1


def pips(pic, cam, t, fm, ok, min_px=2):
    """A tile's pips on its back face (the one toward us): one round
    template a half, the size the perspective gives the dots on average,
    a pixel of face clear of its edges (`ok`: the face, eroded, plus what a
    nearer tile hides). All or none per half. Returns the dots and their
    templates' sizes."""
    c, Rt = t["c"], t["Rt"]
    ux, uy, nz = Rt[:, 0], Rt[:, 1], -Rt[:, 2]
    face_c = c + nz * (T / 2)
    out = np.zeros((128, 128), bool)
    sizes = []
    for half, n in ((0.5, t["faces"][0]), (-0.5, t["faces"][1])):
        if n == 0:
            continue
        cs, ws, hs = [], [], []
        for a, b in ak.PIPS[n]:
            p = face_c + ux * (a * PIP_A) + uy * (half - b * PIP_A)
            ring = np.array([cam.project(p + PIP_R * (np.cos(q) * ux + np.sin(q) * uy)) for q in np.linspace(0, 2 * np.pi, 16, endpoint=False)])
            cs.append(cam.project(p))
            ws.append(np.ptp(ring[:, 0]))
            hs.append(np.ptp(ring[:, 1]))
        w, h = int(round(np.mean(ws))), int(round(np.mean(hs)))
        w, h = min(w, h + 1), min(h, w + 1)
        if min(w, h) < min_px:
            continue
        tpl = ak.pip_template(w, h)
        these = [ak.place(tpl, int(round(cx - w / 2)), int(round(cy - h / 2))) for cx, cy in cs]
        if all(not (mm & ~ok).any() for mm in these) and any((mm & fm).any() for mm in these):
            for mm in these:
                out |= mm & fm
            sizes.append((w, h))
    return out, sizes


# ---- effects ----------------------------------------------------------------------------

def burst(pic, x, y, r_out=(9.0, 5.5), r_in=3.0, n=8, turn=-12.0, core=0.5):
    """A comic crash: a jagged star (long and short spikes in turn), red,
    a cream heart, ringed in black so it pops on anything."""
    yy, xx = np.mgrid[0:128, 0:128]
    X, Y = xx + 0.5 - x, yy + 0.5 - y
    ang = np.degrees(np.arctan2(Y, X)) - turn
    rr = np.hypot(X, Y)
    k = (ang % (360 / n)) / (360 / n)
    seg = np.floor((ang % 360) / (360 / n)).astype(int)
    tip = np.where(seg % 2 == 0, r_out[0], r_out[1])
    edge = r_in + (tip - r_in) * (1 - np.abs(k * 2 - 1))
    S = rr < edge
    C = rr < edge * core
    ring = ak.dilate(S, 1) & ~S
    pic.put(ring, "black")
    pic.put(S, "red")
    pic.put(C, "cream")
    return S | ring


# ---- the picture --------------------------------------------------------------------

def draw():
    P = ak.Palette({
        "felt0": "#04201E", "felt1": "#0B4A30", "felt2": "#1F7A3A", "felt3": "#4FA43C",
        "ivory0": "#45465C", "ivory1": "#A89A7C", "ivory2": "#E2D6B8",
        "gold0": "#8A400C", "gold1": "#E89A1C", "gold2": "#FFE68A",
        "wine": "#5A0A16",
    }, ramps=[FELT_R, TILE_R, ["wine", "gold0", "gold1", "gold2", "cream"]])
    cv = ak.Canvas("#000000")
    s = cv.s
    yy, xx = np.mgrid[0:128, 0:128]
    pic = ak.Picture.blank(P, "black")
    cam = R.Camera(*CAM[:2], fov=CAM[2], up=CAM_UP)
    ts = chain(cam)
    n = len(ts)
    hero = ts[0]

    mats = [R.Mat("#FFFFFF", spec=0)] + [R.Mat("#FFFFFF", spec=0) for _ in range(n)]
    felt = R.prim(lambda p: p[:, 1], 0)
    scene = R.U(*[R.xf(R.prim(BOX, t["k"]), t["c"], t["Rt"]) for t in ts])
    reg = (0, 40, 128, 128)
    out = R.render(cv, R.U(felt, scene), cam, mats, ss=2, region=reg, shadows=False, ao=False)
    owner = R.majority(out, s)
    owner[:reg[1]] = -1
    shadow = ak.px_mean(R.ground(cv, scene, cam, light=SUN, ss=2, region=reg, k=6.0), s)
    felt_px = owner == 0
    tile_px = owner > 0

    # ---- the felt: a pool of lamp light round the double six, in plateaus
    # (perspective ellipses) with narrow seams, falling into the dark
    o_px, d_px = cam.rays((xx.reshape(-1) + 0.5).astype(float), (yy.reshape(-1) + 0.5).astype(float))
    tt = -o_px[:, 1] / np.minimum(d_px[:, 1], -1e-6)
    gp = (o_px + d_px * tt[:, None]).reshape(128, 128, 3)
    pc = ground_at(cam, *POOL_AT)
    r = np.hypot(gp[..., 0] - pc[0], (gp[..., 2] - pc[2]) * POOL_SQUASH)
    lv = np.interp(r, POOL[0], POOL[1])
    lv[(d_px[:, 1] > -0.02).reshape(128, 128)] = 0
    dist = np.hypot(gp[..., 0] - cam.pos[0], gp[..., 2] - cam.pos[2])
    lv -= np.clip((dist - FAR[0]) / (FAR[1] - FAR[0]), 0, 1) * 2.4    # the far felt falls into the dark
    vig = np.hypot((xx + 0.5 - VIG[0]) / VIG[2], (yy + 0.5 - VIG[1]) / VIG[3])
    lv -= np.clip((vig - 0.8) / 0.3, 0, 1) * 1.8                      # and the frame's edges (curved bands)
    left_of = np.any([ak.shift(tile_px, d, 0) for d in range(1, 7)], axis=0)
    right_of = np.any([ak.shift(tile_px, -d, 0) for d in range(1, 7)], axis=0)
    lv -= (left_of & right_of) * 1.0                                 # felt boxed in between two tiles is in their shade
    lv = ak.terrace(lv, 0.1)
    lv = np.maximum(lv - (shadow > 0.4) * 1.0 - (shadow > 0.8) * 1.0, np.minimum(lv, 1.0))   # the cast shadows: crisp-edged, a core, never a hole
    ak.by_level(pic, lv, FELT_R, felt_px | (owner == -1))

    # ---- the tiles, face by face, flat (a face steps up a level toward its
    # top, the lamp being above, with a 1 px seam)
    o_all, d_all = cam.rays(cv.X.reshape(-1).astype(np.float64), cv.Y.reshape(-1).astype(np.float64))
    depth = np.full((128, 128), np.inf)
    for t in ts:
        m = owner == t["k"]
        t["mask"] = m
        t["face"] = None
        if not m.any():
            continue
        sel = (out["mat"] == t["k"])
        cnt = np.maximum(ak.px_mean(sel.astype(np.float32), s), 1e-6)
        depth = np.where(m, ak.px_mean(np.where(sel, out["depth"], 0.0), s) / cnt, depth)
        nrm = ak.px_mean(out["normal"] * sel[..., None], s)
        nrm /= np.maximum(np.linalg.norm(nrm, axis=-1, keepdims=True), 1e-6)
        loc = nrm @ t["Rt"]
        ax = np.abs(loc).argmax(-1)
        sg = np.take_along_axis(loc, ax[..., None], -1)[..., 0] > 0
        face = ax * 2 + (~sg)                       # 0 +x, 1 -x, 2 top, 3 foot, 4 front, 5 back (toward us: pips)
        for f in range(6):                          # slivers of a face seen edge-on join their neighbour
            fm_ = m & (face == f)
            if 0 < fm_.sum() < 6:
                nb = ak.dilate(fm_, 1, diag=True) & m & (face != f)
                if nb.any():
                    face[fm_] = np.bincount(face[nb]).argmax()
        face = smooth_faces(face, m)
        dep = np.where(sel, out["depth"], 0.0).reshape(-1)
        hit = (o_all + d_all * dep[:, None]).reshape(cv.N, cv.N, 3)
        ly = ak.px_mean(((hit - t["c"]) @ t["Rt"])[..., 1] * sel, s) / cnt
        g = np.clip(ly / H + 0.5, 0, 1)            # 0 at the foot, 1 at the top
        tn = t["tone"]
        lvl = np.full((128, 128), float(tn["side"]))
        lo, hi = tn["face"]
        lvl[face == 5] = (lo + np.clip((g - tn["cut"]) / tn["soft"] + 0.5, 0, 1) * (hi - lo))[face == 5]
        lvl[(face == 2) | (face == 4)] = tn["top"]
        lvl[face == 3] = tn["side"]
        t["face"], t["g"] = face, g
        ak.by_level(pic, lvl, TILE_R, m, q=2)

    # ---- seams: black wherever two tiles meet (on the farther one), and on
    # each tile's shadow side against the felt
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        o2 = np.roll(np.roll(owner, dy, 0), dx, 1)
        d2 = np.roll(np.roll(depth, dy, 0), dx, 1)
        pic.put(tile_px & (o2 > 0) & (o2 != owner) & (depth > d2), "black")
    for t in ts:
        m = t["mask"]
        ring = ak.dilate(m, 1) & ~m
        right_of = ak.shift(m, 1, 0)
        under = (ak.shift(m, 0, 1) | ak.shift(m, 1, 1)) & ~ak.shift(m, -1, 0)
        pic.put(ring & felt_px & (right_of | under), "black")

    # ---- the double six's lit edges: a cream rim down its face's left edge
    # (one pixel a row: a clean line), and a bevel where face meets side
    fm = hero["mask"] & (hero["face"] == 5)
    left = np.zeros_like(fm)
    for y in range(128):
        xs_ = np.nonzero(fm[y])[0]
        if len(xs_) and not hero["mask"][y, xs_[0] - 1]:
            left[y, xs_[0]] = True
    pic.put(left, "cream")
    side = hero["mask"] & (hero["face"] == 1)
    pic.put(fm & ak.shift(side, -1, 0) & ~ak.shift(left, 1, 0), "ivory1")

    # ---- pips on the faces toward us (a nearer tile may hide some of a dot)
    pips_px = np.zeros((128, 128), bool)
    for t in ts:
        if t["face"] is None:
            continue
        fm = t["mask"] & (t["face"] == 5)
        if fm.sum() < 20:
            continue
        nearer = np.zeros((128, 128), bool)
        for t2 in ts:
            if t2 is not t and t2["mask"].any() and depth[t2["mask"]].mean() < depth[t["mask"]].mean():
                nearer |= t2["mask"]
        ok = ak.erode(fm | nearer, 1) | (nearer & ~ak.dilate(t["mask"] & ~fm, 1))
        dots, sizes = pips(pic, cam, t, fm, ok)
        if not dots.any():
            continue
        tn = t["tone"]
        c, Rt = t["c"], t["Rt"]
        fc = c - Rt[:, 2] * (T / 2)
        a = cam.project(fc + Rt[:, 0] * -0.38)
        b = cam.project(fc + Rt[:, 0] * 0.38)
        bar = TILE_R[max(tn["face"][0] - 1, 1)]
        if t is hero:                                   # engraved: a dark groove, its upper wall in shade
            clear = ak.erode(fm, 1) & ~ak.dilate(dots, 1)
            px_ = ak.ink(pic, [a, b], "ivory1", where=clear)
            for x, y in px_:
                if 0 <= y - 1 < 128 and clear[y - 1, x] and (x, y - 1) not in px_:
                    pic.px(x, y - 1, "ivory2")
        else:
            ak.ink(pic, [a, b], bar, where=ak.erode(fm, 1) & ~ak.dilate(dots, 1))
        pic.put(dots, "black")
        if t is hero:                                   # drilled: the wall facing the lamp catches it
            lit = dots & ~ak.shift(dots, -1, -1) & ak.shift(dots, 1, 1) & ~ak.shift(dots, 0, -1)
            pic.put(lit, "ivory0")
        pips_px |= dots

    # ---- motion: arcs the double six's edge swept as it fell, round its
    # foot, trailing back from it, tapering, each with a dark edge under it
    effects = np.zeros((128, 128), bool)
    ok = (felt_px | (owner == -1)) & ~ak.dilate(tile_px, 2) & (yy > 45)
    for x_, yf, back, r0 in SWING:
        pts = [cam.project(face_point(hero, x_, yf, hero["tilt"] - a)) for a in np.linspace(2, back, 3)]
        p0, p1, p2 = (np.array(p) for p in pts)
        ctrl = 2 * p1 - 0.5 * (p0 + p2)              # through the middle point
        nrm = np.array([p2[1] - p0[1], p0[0] - p2[0]]) / max(np.hypot(*(p2 - p0)), 1e-6)
        ctrl = ctrl + nrm * SWING_BOW * (1 if nrm[1] < 0 else -1)   # bowed up: an arc over the fall
        before = pic.idx.copy()
        mk = ak.streak(pic, tuple(p0), tuple(ctrl), tuple(p2), r0, 0.3, ok,
                       cols=(("cream", 0.35), ("ivory2", 0.7), ("ivory1", 1.0)))
        tip = mk & ~ak.paint.nbrs(mk)                    # a lone pixel at the taper's end
        pic.idx[tip] = before[tip]
        mk &= ~tip
        under = (ak.shift(mk, 0, 1) | ak.shift(mk, 1, 1)) & ~mk & ok & ~effects
        pic.put(under, "felt0")
        effects |= mk | under

    # ---- the crash: where the double six's top meets the next tile, a burst
    cx, cy = cam.project(top_point(hero, 0.2, out=0.0) + hero["Rt"][:, 2] * T)
    bx, by = int(round(cx)) + BURST_AT[0], int(round(cy)) + BURST_AT[1]
    effects |= burst(pic, bx, by, **BURST)

    ak.despeckle(pic, keep=effects | pips_px, within=(yy >= 44))
    ak.despeckle(pic, need=3, keep=effects | pips_px, within=felt_px & ak.dilate(tile_px, 1, diag=True))  # the felt's dither against a tile

    # ---- the title: gold chrome (a bright sky, a dark horizon, its
    # reflection, the ground), carved depth in wine, a black outline and
    # shadow, a bevel on the outer contour, glints
    m1 = ak.load_mask(TITLE)
    x1, y1 = ak.centred_x(m1), TITLE_Y
    rows = TITLE_ROWS
    t1 = ak.title(pic, m1, x1, y1, fill=None, rows=rows, hi=None, lo=None,
                  extrude=dict(dx=1, dy=1, depth=4, colours=["wine"] * 4),
                  shadow=dict(dx=1, dy=2, colour="black"))
    face = t1["face"]
    face_idx = pic.idx.copy()
    hi_, lo_ = ak.bevel_contour(pic, face, "cream", "gold0")
    for b in (hi_, lo_):                                     # a bevel pixel with none of its kind round it keeps the face
        lone = b & ~ak.paint.nbrs(b, diag=True)
        pic.idx[lone] = face_idx[lone]
    pic.put(hi_ & (yy >= y1 + 17), "gold2")                 # below the horizon the lit edge is gold, not cream
    pic.put(hi_ & (yy >= y1 + 30), "gold1")
    ak.lonely(pic, "black", yy < 44)                          # pinholes between the face and its depth
    for gx, gy, arms in TITLE_GLINTS:
        ak.glint(pic, x1 + gx, y1 + gy, tip="gold2", arms=arms)
    return pic.image()


def title_lines():
    """The title's lettering as drawn here, and its depth, for the title
    screen (tools/titleart.py: the game paints it in the house gold)."""
    return [dict(mask=ak.load_mask(TITLE), depth=4, side="wine")]


if __name__ == "__main__":
    import boxart
    boxart.save(draw(), HERE.parent / "docs" / "cart.png")
