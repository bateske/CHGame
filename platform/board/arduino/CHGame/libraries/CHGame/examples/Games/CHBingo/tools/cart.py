"""docs/cart.png, CHBingo's cover in the visual menu (docs/cover-art.md).
`chgame boxart` redraws it; edit this, not the PNG.

THE BRIEF
  Message: B-I-N-G-O! The ball that wins it. The cage has just spat out
  the winning ball, O 66, and it is flying straight at you; on your card
  the top row is four daubs long and its last cell, 66, waits in the
  game's own rainbow frame (the frame the game puts round a number waiting
  to be daubed). The four red daubs march straight at the ball's 66: you
  read the win before the ball lands.

  Composition (a thumbnail in words):
  - Title: BINGO across the top band (y 1-38) on the black of the hall,
    bouncing like the game's title balls (B and O 2 px low, I and G 1 px:
    a gentle arch), puffy gold: each letter a balloon lit from the top
    left (a gold2 rim and one tapered cream shine up left, gold1 body, a
    gold0 rim down right), each in its own black outline over the wine
    extrusion of the letter before; one indigo rim round the whole closed
    silhouette, the pockets between letters black. One glint, on the O's
    shine. Nothing else up there: the hero's glow keeps 4 px clear of
    everything the title draws.
  - Focal point: the hero ball, right of centre, 58 px across and breaking
    the right edge (it is close, coming at us): glossy red, cel-lit in
    flat plateaus (a small coral cap toward the key, the red body, a wine
    crescent in shade) with one-pixel dithered seams; a cream window
    near its upper-left rim, clear of the disc, and a crisp star where the
    key grazes its top, flashing out over the hall; the felt reflected
    along its lower rim, the lit card as a coral crescent on its lower
    left, its back light as a blue rim on its upper right. Its printed disc
    faces us (cream, a silver crescent on its shaded side, a wine ring
    round it): a round bold "O" over a bold "66". Three thin, curved,
    tapered speed lines trail back along its arc toward the cage, stopping
    short of it. Its shadow is small and crisp (felt0, a black core),
    a few px below it in the pool of light: it is in the air.
  - Behind it: the black hall, a dim far wall of night low behind the
    table, and the hero's back light: a glow of indigo and night on its
    upper right, one sparkle in it.
  - The cage, at the back left, small, dark and cool (it is background):
    a wire globe on two posts and a grey plinth standing on the felt; four
    meridians and three hoops, silver and grey in front, indigo behind,
    one cream glint; three dim balls inside (blue, green, red: the game's
    B, G and I balls), the front wires kept off their faces; its crank on
    the far side; an open door facing the hero.
  - The table: a padded wine rail along its far edge, a highlight in red
    tapering along its top; the felt dark far away, lit in a pool round
    the hero's shadow.
  - The card, at the front left, lying on the felt and running out of the
    frame (the camera low over it): the game's own card, a checker of
    silver and grey cells with black numbers, a navy header with B I N G O
    in the game's ball colours; the top row daubed red (7 21 38 52, the
    ink see-through, the numbers in wine) up to 66 in the rainbow frame,
    right beside the hero. It falls off to indigo toward the frame.
  - Light: the house key from the top left; everything falls off to the
    frame. The value ladder: the title, the hero's cream disc, its coral
    cap and red body, the card's cells and daubs, the cage. The eye runs
    title, hero (its 66), the waiting 66, the daubs, the cage.

PALETTE (11 own + cream, grey, black, red; the rainbow on the waiting cell)
  night indigo blue       the hall, its far wall and the hero's glow, the
                          cage's back wires, the card's header and its
                          vignette; blue the hero's back-light rim and the
                          header's B
  wine coral              with red: the hero ball, the daubs and the rail
                          (wine the shade and the ink's numbers, coral the
                          lit cap); wine also the title's extrusion
  felt0 felt1             the table, the green ball, the hero's lower rim
  silver                  chrome (with grey and cream), the card's light
                          cells, the discs' shaded side, the speed lines
  gold0 gold1 gold2       the title's own: nothing else uses them

FONTS
  title.txt (BINGO): "ONE HUNDRED AND FIFTY FIVE" from the bmf collection
  (author and terms not stated: a `?` face, chosen as the roundest, most
  bubbly heavy face at its own size); its lower-case n redrawn by hand as
  a capital N; letters spaced 1 px wider here (SPREAD) so each sits in
  its own black outline. The hero's number: Green Flame by Extram Studios
  (public domain / GPL / OFL; art/greenflame.json); its "O" drawn by hand,
  9 px round and bold. Small lettering: the CHGame library's 3x5 font (its
  N redrawn 4 px wide and its I as a serifed bar on the card's header).
"""
import pathlib
import sys

import numpy as np
from scipy import ndimage

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import artkit as ak  # noqa: E402
import pixkit  # noqa: E402

TITLE = HERE / "art" / "title.txt"
LABEL_FONT = HERE / "art" / "greenflame.json"

COL = {
    "night": "#100A28", "indigo": "#2A1E66", "blue": "#2F6AE0",
    "wine": "#6A0C26", "coral": "#FF8458",
    "felt0": "#0B3A2E", "felt1": "#1E8048",
    "silver": "#A6A2BC",
    "gold0": "#A04A0C", "gold1": "#F2AE1E", "gold2": "#FFEC80",
}
yy, xx = np.mgrid[0:128, 0:128]
X1, Y1 = xx + 0.5, yy + 0.5
KEY = ak.KEY                                        # screen coords, y down, toward the light


# ---- helpers ------------------------------------------------------------------------

def cov(fn, ss=4):
    """Coverage (0..1) per pixel of a distance field fn((X, Y)) (negative inside)."""
    c = (np.arange(128 * ss) + 0.5) / ss
    X, Y = np.meshgrid(c, c)
    return (fn((X, Y)) < 0).reshape(128, ss, 128, ss).mean(axis=(1, 3))


def disc(cx, cy, r):
    return cov(lambda P: ak.circle(P, cx, cy, r)) >= 0.5


def oval(cx, cy, rx, ry, angle=0.0):
    return cov(lambda P: ak.ellipse(P, cx, cy, rx, ry, angle=angle)) >= 0.5


def sstep(a, b, v):
    t = np.clip((v - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def mask35(s):
    """Text in the CHGame library's 3x5 font as a mask."""
    w = pixkit.text35_width(s)
    m = np.zeros((5, max(w, 1)), bool)
    x = 0
    for ch in s:
        g = pixkit.glyph35(ch)
        if g >= 0:
            for col in range(3):
                bits = pixkit.FONT35[g][col]
                for row in range(5):
                    if bits & (1 << row):
                        m[row, x + col] = True
        x += 4
    return m


def rows_mask(rows):
    return np.array([[c == "#" for c in r] for r in rows])


O9 = rows_mask(["..#####..", ".#######.", "###...###", "##.....##", "##.....##", "##.....##", "###...###",
                ".#######.", "..#####.."])                 # the hero's round, bold O
N4 = rows_mask(["#..#", "##.#", "#.##", "#..#", "#..#"])   # the 3x5 N reads as n
I3 = rows_mask(["###", ".#.", ".#.", ".#.", "###"])       # and its I as a bar


def stamp(pic, m, cx, cy, colour, where=None):
    """A small mask centred on (cx, cy)."""
    h, w = m.shape
    M = ak.place(m, int(round(cx - w / 2)), int(round(cy - h / 2)))
    if where is not None:
        M &= where
    pic.put(M, colour)
    return M


def seams(v, cuts, width=0.9):
    """A float level from v through flat plateaus, one per cut, each change a
    seam about 2*width px wide (measured by v's own gradient), so a by_level
    dither only ever touches a pixel or two along the change."""
    gy, gx = np.gradient(v)
    g = np.maximum(np.hypot(gx, gy), 1e-4)
    lv = np.zeros_like(v)
    for c in cuts:
        lv += sstep(-width, width, (v - c) / g)
    return lv


def merge_lone(pic, within, need=3):
    """Pixels inside `within` with no 8-neighbour of their own colour take
    their neighbours' commonest colour (when `need` of them share it): the
    specks left where wires cross."""
    a = pic.idx
    pad = np.pad(a, 1, mode="edge")
    nb = np.stack([pad[1 + dy:129 + dy, 1 + dx:129 + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                   if dx or dy], -1)
    same = (nb == a[..., None]).sum(-1)
    best = np.zeros_like(a)
    cnt = np.zeros(a.shape, np.int32)
    for v in np.unique(nb):
        n = (nb == v).sum(-1)
        better = n > cnt
        best = np.where(better, v, best)
        cnt = np.where(better, n, cnt)
    fix = within & (same == 0) & (cnt >= need)
    a[fix] = best[fix]
    return int(fix.sum())


# ---- the balls ----------------------------------------------------------------------

RAMPS = {   # black, shade, body, light, specular
    "red": ["black", "wine", "red", "coral", "cream"],
    "blue": ["black", "night", "indigo", "blue", "cream"],
    "green": ["black", "night", "felt0", "felt1", "cream"],
    "white": ["black", "grey", "silver", "cream", "cream"],
}


def sphere(cx, cy, r):
    nx, ny = (X1 - cx) / r, (Y1 - cy) / r
    rr = np.hypot(nx, ny)
    nz = np.sqrt(np.clip(1 - rr * rr, 0, 1))
    n = np.stack([nx, ny, nz], -1)
    return n, (n * KEY).sum(-1), nx, ny, rr


def small_ball(pic, cx, cy, r, ramp, cuts=(0.3, 0.85), spec=True):
    """A dim ball in the cage: plateaus of its ramp, a one-pixel glint."""
    R = RAMPS[ramp]
    m = disc(cx, cy, r)
    n, dif, nx, ny, rr = sphere(cx, cy, r)
    ak.by_level(pic, 1 + seams(dif, cuts, 0.6), R[:4], m, q=2)
    if spec:
        pic.px(int(cx - 0.45 * r), int(cy - 0.45 * r), R[3])
    return m


# ---- the cage -----------------------------------------------------------------------

def rot(yaw, pitch):
    a, b = np.radians(yaw), np.radians(pitch)
    Ry = np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])
    Rx = np.array([[1, 0, 0], [0, np.cos(b), -np.sin(b)], [0, np.sin(b), np.cos(b)]])
    return Rx @ Ry


def cage_wires(C, R, M, n_merid=4, lats=(-0.6, 0.0, 0.6), samples=320):
    """The wires of a globe cage turning about its own x axis (y up, z toward
    us): each an array of (screen x, screen y, depth, light) points."""
    out = []
    t = np.linspace(0, 2 * np.pi, samples)
    A, U, V = np.eye(3)
    for k in range(n_merid):
        ph = np.pi * (k + 0.25) / n_merid
        P = np.cos(ph) * U + np.sin(ph) * V
        out.append(np.cos(t)[:, None] * A + np.sin(t)[:, None] * P)
    for s in lats:
        q = np.sqrt(1 - s * s)
        out.append(s * A + q * (np.cos(t)[:, None] * U + np.sin(t)[:, None] * V))
    L = np.array([-0.55, 0.65, 0.52])
    L /= np.linalg.norm(L)
    res = []
    for pts in out:
        w_ = pts @ M.T
        res.append(np.stack([C[0] + R * w_[:, 0], C[1] - R * w_[:, 1], w_[:, 2], w_ @ L], -1))
    return res


def draw_wire(pic, pts, front, cols, skip=None):
    """One wire's front or back half as clean 1-px runs, coloured by light."""
    sel = (pts[:, 2] >= 0) if front else (pts[:, 2] < 0)
    runs_, cur = [], []
    for p, s in zip(pts, sel):
        if s:
            cur.append(p)
        elif cur:
            runs_.append(cur)
            cur = []
    if cur:
        runs_.append(cur)
    if len(runs_) > 1 and sel[0] and sel[-1]:           # the run that wraps round joins up
        runs_[0] = runs_[-1] + runs_[0]
        runs_.pop()
    drawn = np.zeros((128, 128), bool)
    for r in runs_:
        if len(r) < 2:
            continue
        r = np.array(r)
        for x, y, tt in ak.paint.raster([tuple(p) for p in r[:, :2]]):
            i = min(int(round(tt * (len(r) - 1))), len(r) - 1)
            c = cols(r[i, 3])
            if c and 0 <= x < 128 and 0 <= y < 128 and (skip is None or not skip[y, x]):
                pic.px(x, y, c)
                drawn[y, x] = True
    return drawn


# ---- the picture --------------------------------------------------------------------

HERO = (99.0, 72.0, 29.0)                               # centre, radius
CAGE = ((26.0, 60.0), 15.0, (-30, 16))                  # centre, radius, (yaw, pitch)
DOOR = (40.0, 55.5)                                     # where the hero came out: the door's centre
INSIDE = [(20.5, 67.5, 4.2, "green"), (29, 69.5, 4.4, "red"), (24.5, 61.5, 3.8, "blue")]   # resting in the cage
HOR = 76                                                # the table's far edge
POOL = (94, 104, 42, 21)                                # the light's pool on the felt: centre, radii
SHADOW = (106.0, 107.5)                                 # the hero's shadow, far below it on the felt
CARD = [(2, 88), (72, 86), (86, 160), (-14, 164)]       # far left, far right, near right, near left
HEADER = 0.85                                           # the card's header, in rows
NUMS = [[7, 21, 38, 52, 66], [12, 17, 33, 49, 71], [3, 29, 0, 58, 63], [9, 24, 35, 60, 75], [14, 19, 44, 47, 64]]
DAUBS = {(0, 0), (0, 1), (0, 2), (0, 3)}                # the top row, marching at the hero
WAITING = (0, 4)                                        # the cell the hero ball wins: its frame the rainbow
SPEED = [(199, (50, 63), 3.0, 1.0), (215, (47, 55), 4.5, 1.2), (231, (55, 47), 4.0, 1.0)]   # the hero's speed
# lines: where on its rim (deg), where each ends (4 px clear of the cage), how far its arc bows up, its root radius
RAIL_LIT = (36, 22)                                     # the rail's highlight: centre x, half-length
WALL, WALL_Y = 1.0, 58                                  # the far wall's level (1 = night) and where it fades up to black
GLOW = ([0, 4, 8, 13, 19], [1.8, 1.6, 1.1, 0.8, 0.0])   # the hero's back light: level by px past its rim
STAR = -112                                            # the hero's glint: where on its rim (deg)
SPARKLES = [(122, 47, (1, 1, 1, 1))]
ARCH = [2, 1, 0, 1, 2]                                  # the title's bounce: each letter's drop (px)
SPREAD = [0, 1, 2, 3, 2]                                # and each letter's nudge right (px): room for outlines
TITLE_GLINT = (102, 6)                                   # the title's one glint (on the O's shine)
LIGHT_T = np.array([-0.6, -0.8])                        # the title's light, in screen x, y


def title_masks():
    """The title's letters, placed: a list of masks, one per letter."""
    m = ak.load_mask(TITLE)
    lab = ak.letters(m)
    order = sorted(range(1, lab.max() + 1), key=lambda k: np.nonzero(lab == k)[1].min())
    width = m.shape[1] + SPREAD[-1] + 3
    x0 = (128 - width) // 2
    return [ak.place(lab == k, x0 + SPREAD[i], 3 + ARCH[i]) for i, k in enumerate(order)]


def title_lines():
    """The title's lettering as drawn here, and its depth, for the title
    screen (tools/titleart.py: the game paints it in the house gold)."""
    M = np.zeros((128, 128), bool)
    for L in title_masks():
        M |= L
    return [dict(mask=M, depth=3, side="wine")]


def title_footprint(depth=3):
    """Everything the title draws: faces, extrusion, outlines, shadow."""
    M = np.zeros((128, 128), bool)
    for L in title_masks():
        M |= L
    F = M.copy()
    for k in range(1, depth + 1):
        F |= ak.shift(M, k, k)
    F = ak.dilate(F, 2)
    return F | ak.shift(F, 1, 2)


def hall(pic):
    """The black hall, and behind the hero its back light: a glow of indigo
    and night on its upper right, clear of the title and the cage."""
    hx, hy, hr = HERO
    Rc = CAGE[1]
    lv = WALL * sstep(WALL_Y - 4, WALL_Y + 4, Y1)          # the far wall: night low behind the table
    dist = np.hypot(X1 - hx, Y1 - hy) - hr                  # px outside the hero's rim
    side = np.clip(((X1 - hx) * 0.55 - (Y1 - hy) * 0.83) / np.maximum(np.hypot(X1 - hx, Y1 - hy), 1), -1, 1)
    glow = np.interp(dist, GLOW[0], GLOW[1]) * sstep(-0.6, 0.4, side)
    gap = ndimage.distance_transform_edt(~title_footprint())
    clear = sstep(4, 9, gap) * sstep(Rc + 3, Rc + 8, np.hypot(X1 - CAGE[0][0], Y1 - CAGE[0][1]))
    lv = np.maximum(lv, glow * clear)
    ak.by_level(pic, seams(lv, (0.5, 1.5), 0.6), ["black", "night", "indigo"], yy < HOR)


def table(pic):
    """The felt: a pool of light round the hero's shadow, dark at the frame."""
    nz_ = ak.noise((X1, Y1), 9, seed=3, octaves=2) - 0.5
    t = np.hypot((X1 - POOL[0]) / POOL[2], (Y1 - POOL[1]) / POOL[3])
    lv = np.interp(t + 0.08 * nz_, [0, 0.7, 1.1, 1.6], [2.2, 1.8, 1.0, 0.35])
    lv -= sstep(120, 128, Y1) * 0.6 + sstep(120, 128, X1) * 0.5
    lv = np.minimum(lv, 1.0 + np.clip((Y1 - 81) * 0.35, 0, 2))      # the far felt: a flat dark strip
    ak.by_level(pic, seams(lv, (0.6, 1.5), 0.9), ["black", "felt0", "felt1"], yy >= HOR)
    pic.put((yy == HOR), "black")
    # the table's padded rail along its far edge: wine leather, lit along its top
    r0 = HOR - 5
    pic.put((yy >= r0) & (yy < HOR), "wine")
    off = np.abs(xx - RAIL_LIT[0])                          # where the key catches its top: a highlight
    pic.put((yy == r0) & (off <= RAIL_LIT[1]), "red")       # tapering at both ends
    pic.put((yy == r0) & (off > RAIL_LIT[1]) & (off <= RAIL_LIT[1] + 8) & ak.checker(), "red")
    pic.put((yy == r0 + 1) & (off <= RAIL_LIT[1] - 8) & ak.checker(), "red")
    pic.put((yy == HOR - 1), "black")
    pic.put((yy == HOR - 2) & ak.checker(), "black")         # its underside turning away
    pic.put((yy == r0 - 1), "black")


def cage(pic):
    """The cage at the back left: background, darker and cooler."""
    (Cx, Cy), Rg, (yaw, pitch) = CAGE
    M = rot(yaw, pitch)
    wires = cage_wires((Cx, Cy), Rg, M)
    ax_ = M @ np.array([1.0, 0, 0])
    hubL = (Cx - Rg * 1.1 * ax_[0], Cy + Rg * 1.1 * ax_[1])
    hubR = (Cx + Rg * 1.1 * ax_[0], Cy - Rg * 1.1 * ax_[1])
    # the stand: a plinth whose lip stands on the felt, two posts
    bx0, bx1, by0, by1 = int(hubL[0]) - 5, int(hubR[0]) + 5, 79, 84
    shc = oval((bx0 + bx1) / 2 + 4, by1 + 1.5, (bx1 - bx0) / 2 + 3, 2.6)
    pic.put(shc & (yy > by1 - 1) & (yy > HOR) & pic.where("felt1"), "felt0")
    pic.put(shc & (yy > by1 - 1) & (yy > HOR) & pic.where("felt0"), "black")
    top_ = (xx >= bx0) & (xx <= bx1) & (yy >= by0) & (yy <= by0 + 1)
    front = (xx >= bx0) & (xx <= bx1) & (yy > by0 + 1) & (yy <= by1)
    pic.put(top_, "silver")
    pic.put(top_ & (xx > bx0 + 14), "grey")
    pic.put(front, "indigo")
    pic.put(front & (yy == by0 + 2), "grey")
    ak.outline(pic, top_ | front, "black")
    for h in (hubL, hubR):
        x_ = int(round(h[0]))
        post = (xx >= x_ - 1) & (xx <= x_) & (yy >= int(h[1])) & (yy < by0)
        pic.put(post, "grey")
        pic.put(post & (xx == x_ - 1), "silver" if h is hubL else "grey")
        pic.put(post & (xx == x_), "indigo")
        ak.outline(pic, post, "black", where=~(top_ | front))
    # its crank, on the far side: a short arm and a knob
    ak.ink(pic, [(hubL[0] - 1, hubL[1] + 1), (hubL[0] - 4, hubL[1] + 5)], "grey")
    kn = disc(hubL[0] - 4.5, hubL[1] + 6.5, 1.6)
    pic.put(kn, "grey")
    ak.outline(pic, kn, "black")

    def back_col(lt):
        return "indigo"

    def front_col(lt):
        return "silver" if lt > 0.3 else "grey" if lt > -0.35 else "indigo"
    inner = disc(Cx, Cy, Rg) & (yy < HOR - 5)            # the globe's dark inside: a volume against the wall
    pic.put(inner, "black")
    for w_ in wires:
        draw_wire(pic, w_, False, back_col)
    balls = np.zeros((128, 128), bool)
    for (bx, by, br, rp) in INSIDE:
        bm = small_ball(pic, bx, by, br, rp)
        ak.outline(pic, bm, "black")
        balls |= bm
    door = disc(DOOR[0], DOOR[1], 3.6)
    for w_ in wires:
        draw_wire(pic, w_, True, front_col, skip=door | ak.erode(balls, 1))
    for h in (hubL, hubR):
        hb = disc(h[0], h[1], 2.2)
        pic.put(hb, "grey")
        pic.put(hb & ~ak.shift(hb, 1, 1), "silver")
        ak.outline(pic, hb, "black")
    globe = disc(Cx, Cy, Rg + 1)
    merge_lone(pic, globe & ~balls)
    ak.glint(pic, int(Cx - 0.5 * Rg), int(Cy - 0.62 * Rg), arms=(1, 1, 1, 1))
    return globe | ak.dilate(top_ | front, 1)


def card(pic):
    """The card, lying on the felt at the front left, running out of the
    frame: the top row daubed, its fifth cell waiting in a rainbow frame
    for the hero's number."""
    HH = HEADER
    Hm = ak.homography([(0, 0), (5, 0), (5, 5 + HH), (0, 5 + HH)], CARD)

    def uvpt(u_, v_):
        p = Hm @ np.array([u_, v_, 1.0])
        return (p[0] / p[2], p[1] / p[2])
    cm = cov(lambda P_: ak.inside_uv(*ak.quad_uv(P_, CARD, 5, 5 + HH), 5, 5 + HH)) >= 0.5
    U, V = ak.quad_uv((X1, Y1), CARD, 5, 5 + HH)
    csh = (ak.shift(cm, 2, 1) | ak.shift(cm, 1, 1)) & ~cm & (yy > HOR)   # its shadow on the felt
    pic.put(csh & pic.where("felt1"), "felt0")
    pic.put(csh & pic.where("felt0"), "black")
    # the paper: the game's own checker of silver and grey cells, falling
    # off to the frame
    wr, wc = WAITING
    cell = cm & (U > wc) & (U < wc + 1) & (V > HH + wr) & (V < HH + wr + 1)
    par = ((np.floor(U) + np.floor(V - HH)) % 2 == 0)
    lvc = np.where(par, 2.0, 1.0) - sstep(114, 127, Y1) - 0.8 * sstep(9, 0, X1)     # the frame's vignette
    ak.by_level(pic, ak.terrace(lvc, 0.3), ["indigo", "grey", "silver"], cm & (V >= HH), q=2)
    pic.put(cell, "silver")                              # the waiting cell, lit
    hdr = cm & (V < HH)
    pic.put(hdr, "night")
    pic.put(hdr & ~ak.shift(hdr, 0, 1), "indigo")
    ak.lonely(pic, "indigo", hdr, into="night")
    pic.put(cm & (V >= HH) & ak.shift(hdr, 0, 1), "black")
    for k, (ch, c) in enumerate(zip("BINGO", ("blue", "red", "cream", "felt1", "coral"))):
        x, y = uvpt(k + 0.5, HH * 0.55)
        g_ = N4 if ch == "N" else I3 if ch == "I" else mask35(ch)
        stamp(pic, g_, x + 0.5, y + 0.5, c, cm)
    dm_all = np.zeros((128, 128), bool)
    for r_ in range(5):
        for c_ in range(5):
            x, y = uvpt(c_ + 0.5, HH + r_ + 0.5)
            num = mask35(str(NUMS[r_][c_])) if (r_, c_) != (2, 2) else mask35("*")
            if (r_, c_) in DAUBS:
                a_, b_ = uvpt(c_ + 0.1, HH + r_ + 0.5), uvpt(c_ + 0.9, HH + r_ + 0.5)
                e_, f_ = uvpt(c_ + 0.5, HH + r_ + 0.12), uvpt(c_ + 0.5, HH + r_ + 0.88)
                rx, ry = (b_[0] - a_[0]) / 2, (f_[1] - e_[1]) / 2
                d = oval(x, y, rx, ry) & cm
                pic.put(d, "red")
                pic.put(d & ~ak.shift(d, 1, 1) & ~ak.shift(d, 0, 1), "coral")     # its lit top-left lip
                pic.put(d & ~ak.shift(d, -1, -1) & ~ak.shift(d, 0, -1), "wine")    # its shaded lower edge
                stamp(pic, num, x + 0.5, y + 0.5, "wine", d)          # the ink is see-through
                dm_all |= d
            else:
                stamp(pic, num, x + 0.5, y + 0.5, "black", cm)
    pic.put(cell & ~ak.erode(cell, 1), "rainbow")
    ak.outline(pic, cm, "black")
    return cm, dm_all


def hero(pic, font):
    """The ball that wins it, flying at us."""
    hx, hy, hr = HERO
    # its shadow: small and crisp, far below it in the pool of light
    sx, sy = SHADOW
    sh = oval(sx, sy, 10.5, 2.4)
    core = oval(sx, sy, 7.0, 1.3)
    pic.put(sh, "felt0")
    pic.put(core, "black")
    hm = disc(hx, hy, hr)
    # speed lines: thin, curved, tapered, trailing back along its arc to the door
    ok = ~ak.dilate(hm, 1) & (yy < HOR) & pic.where("black", "night", "indigo")
    for ang_, end, bow, r0 in SPEED:
        a_ = np.radians(ang_)
        root = (hx + (hr + 1.5) * np.cos(a_), hy + (hr + 1.5) * np.sin(a_))
        ctrl = ((root[0] + end[0]) / 2, (root[1] + end[1]) / 2 - bow)
        ak.streak(pic, root, ctrl, end, r0, 0.25, ok=ok, cols=(("silver", 0.3), ("grey", 0.65), ("indigo", 1.0)))
    # the body: cel-lit plateaus, a small coral cap toward the key
    n, dif, nx, ny, rr = sphere(hx, hy, hr)
    lv = 1 + seams(dif, (-0.08, 0.82), 0.6)
    ak.by_level(pic, lv, ["black", "wine", "red", "coral"], hm)
    # the felt reflected along its lower rim
    down = nx * 0.3 + ny * 0.95
    bounce = hm & (rr > 1 - 2.0 / hr) & (down > 0.7)
    pic.put(bounce, "felt0")
    # its printed disc, facing us
    c = np.array([-0.1, -0.05, 1.0])
    c /= np.linalg.norm(c)
    cosang = (n * c).sum(-1)
    dm = hm & (cosang > 0.87) & (rr < 0.97)
    ringm = ak.dilate(dm, 1) & ~dm & hm
    pic.put(ringm, "wine")
    pic.put(dm, "cream")
    pic.put(dm & (dif < 0.42) & ~ak.erode(dm, 2), "silver")         # its shaded side: a crisp crescent
    dx_, dy_ = hx + c[0] * hr * 0.97, hy + c[1] * hr * 0.97
    nm = font.mask("66", gap=1)
    hgt = O9.shape[0] + 2 + nm.shape[0]
    top = dy_ - hgt / 2
    stamp(pic, O9, dx_ + 0.5, top + O9.shape[0] / 2, "black", dm)
    stamp(pic, nm, dx_ + 0.5, top + O9.shape[0] + 2 + nm.shape[0] / 2, "black", dm)
    # the glow behind it catches its upper right rim: a blue reflection
    rimh = hm & ~ak.erode(hm, 1) & (nx > 0.2) & (ny < 0.15) & (ny > -0.9)
    pic.put(rimh, "blue")
    # the lit card beside it shows in its lower left: a coral crescent inside the rim
    ah = np.degrees(np.arctan2(ny, nx))
    refl = hm & (rr > 1 - 2.6 / hr) & (rr < 1 - 1.0 / hr) & (ah > 122) & (ah < 158)
    refl |= hm & (rr > 1 - 1.6 / hr) & (rr < 1 - 1.0 / hr) & (ah > 112) & (ah < 166)
    pic.put(refl & ~bounce & ~ak.dilate(bounce, 1) & pic.where("wine", "red"), "coral")
    ak.outline(pic, hm, "black")
    # the specular window, near its upper-left rim, clear of the disc
    wxc, wyc = hx - 0.6 * hr, hy - 0.6 * hr
    win = oval(wxc, wyc, 4.4, 1.5, angle=-45) & hm & ~ak.dilate(ringm, 2)
    pic.put(win, "cream")
    # and a crisp star where the key grazes its top, flashing out over the hall
    a_ = np.radians(STAR)
    ak.glint(pic, int(hx + (hr - 0.5) * np.cos(a_)), int(hy + (hr - 0.5) * np.sin(a_)), arms=(3, 3, 3, 2), tip="silver")
    return hm, dm


def title_draw(pic):
    """BINGO in puffy gold: each letter its own balloon, bouncing."""
    Ls = title_masks()
    M2 = np.zeros((128, 128), bool)
    for L in Ls:
        M2 |= L
    depth = 3
    t = ak.title(pic, M2, 0, 0, fill=["gold1"], extrude=dict(dx=1, dy=1, depth=depth, side="wine", bottom="wine"),
                 shadow=dict(dx=1, dy=2, colour="black"), outline2="indigo")
    # each letter in its own black outline where it stands on the letter
    # before it's extrusion
    Es = []
    for L in Ls:
        E = np.zeros_like(L)
        for k in range(1, depth + 1):
            E |= ak.shift(L, k, k)
        Es.append(E & ~M2)
    for i, L in enumerate(Ls):
        others = np.zeros_like(L)
        for j, E in enumerate(Es):
            if j != i:
                others |= E
        pic.put(ak.dilate(L, 1) & ~L & others & ~Es[i] & ~M2, "black")
    # the face: a balloon lit from the top left; plateaus, no dither
    for L in Ls:
        d = ndimage.distance_transform_edt(L)
        B = ndimage.gaussian_filter(L.astype(float), 1.3)
        gy, gx = np.gradient(B)
        g = np.maximum(np.hypot(gx, gy), 1e-6)
        facing = -(gx * LIGHT_T[0] + gy * LIGHT_T[1]) / g          # outward normal toward the light
        ys_ = np.nonzero(L.any(axis=1))[0]
        tv = (yy - ys_.min()) / max(1, np.ptp(ys_))
        rimw = np.interp(d, [1, 2.5, 3.5, 4.2], [1.0, 1.0, 0.4, 0.0])
        lvl = 1 + rimw * np.clip(facing * 1.8, -1, 1) + 0.9 * (0.45 - tv)
        lv = np.where(lvl > 1.5, 2, np.where(lvl < 0.5, 0, 1))
        for v, nm in enumerate(("gold0", "gold1", "gold2")):
            pic.put(L & (lv == v), nm)
        # the shine: one cream stroke in the second ring, along the lit top
        # left, tapering at its ends into gold2
        xs_ = np.nonzero(L.any(axis=0))[0]
        cand = L & (d >= 1.9) & (d <= 2.3) & (facing > 0.72) & (xx < xs_.min() + 0.62 * np.ptp(xs_)) \
            & (tv < 0.55)
        lab_c = ak.letters(cand) if cand.any() else None
        if lab_c is not None and lab_c.max():
            big = max(range(1, lab_c.max() + 1), key=lambda j: (lab_c == j).sum())
            S = lab_c == big
            pic.put(S, "cream")
            nb_cnt = sum(ak.shift(S, dx, dy).astype(int) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy)
            pic.put(S & (nb_cnt <= 1), "gold2")
    ak.despeckle(pic, need=5, within=M2)
    face = ("gold0", "gold1", "gold2", "cream")             # a lone face pixel takes its face neighbours' colour
    for nm in face[:3]:
        m = pic.where(nm) & M2
        lone = m & ~(ak.shift(m, 1, 0) | ak.shift(m, -1, 0) | ak.shift(m, 0, 1) | ak.shift(m, 0, -1))
        for y_, x_ in zip(*np.nonzero(lone)):
            nb = [pic.idx[y_ + dy, x_ + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            nb = [v for v in nb if v in [pic.pal[f] for f in face] and v != pic.pal[nm]]
            if nb:
                pic.idx[y_, x_] = max(set(nb), key=nb.count)
    # the notches between letters: the outline's black, not the indigo rim
    body = t["face"] | t["extrude"]

    def near(dx, dy, n):
        out = np.zeros_like(body)
        for k in range(1, n + 1):
            out |= ak.shift(body, dx * k, dy * k)
        return out
    pocket = (near(1, 0, 8) & near(-1, 0, 8)) | (near(0, 1, 5) & near(0, -1, 5))
    closed = body | pocket
    closed |= ~ak.paint.outside_of(closed)                     # the counters
    pic.put(t["all"] & pic.where("indigo"), "black")
    rim = ak.dilate(closed, 2) & ~ak.dilate(closed, 1)         # the indigo rim round the closed silhouette
    pic.put(rim, "indigo")
    pic.put(closed & ~body, "black")
    # a glint where the O's shine starts
    gx_, gy_ = TITLE_GLINT
    ak.glint(pic, gx_, gy_, arms=(2, 1, 2, 2), tip="gold2")
    return t, M2


def draw():
    P = ak.Palette(COL, ramps=[["black", "night", "indigo", "blue"], ["black", "wine", "red", "coral", "cream"],
                               ["black", "felt0", "felt1"], ["grey", "silver", "cream"],
                               ["gold0", "gold1", "gold2", "cream"]])
    pic = ak.Picture.blank(P, "black")
    font = ak.Font(LABEL_FONT)

    hall(pic)
    table(pic)
    globe = cage(pic)
    cm, dm_all = card(pic)
    hm, dm = hero(pic, font)

    # ---- clean-up: lone pixels in the hall and on the felt take their neighbours' colour
    hall_ = pic.where("black", "night", "indigo") & (yy < HOR) & ~globe
    ak.despeckle(pic, need=4, within=hall_, passes=2)
    ak.despeckle(pic, need=5, within=(yy >= HOR) & ~cm & ~hm & ~globe)
    for gx, gy, arms in SPARKLES:
        ak.glint(pic, gx, gy, arms=arms, tip="silver")

    # ---- the frame: the outer two rows and columns a step darker, so the
    # installed border frames the picture
    edge = np.zeros((128, 128), bool)
    edge[:2, :] = edge[-2:, :] = edge[:, :2] = edge[:, -2:] = True
    for a_, b_ in (("wine", "black"), ("red", "wine"), ("coral", "red"), ("cream", "silver"), ("silver", "grey"),
                   ("felt0", "black"), ("felt1", "felt0"), ("blue", "indigo"), ("grey", "indigo")):
        pic.put(edge & pic.where(a_), b_)

    title_draw(pic)
    return pic.image()


if __name__ == "__main__":
    import boxart
    boxart.save(draw(), HERE.parent / "docs" / "cart.png")
