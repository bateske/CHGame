"""docs/cart.png, Tic Tac Toe Royale's cover in the visual menu
(docs/cover-art.md). `chgame boxart` redraws it; edit this, not the PNG.

THE BRIEF (revision 2)
  Message: the world's simplest game, played for a king's ransom. X has
  won, and X wears the crown: three lacquered crosses in a row on a walnut
  board with a brass grid, the winning line through them, the middle one,
  the biggest, crowned. You read "tic tac toe" from the pieces before you
  read a word, and "royale" from the crown and the gold.

  Composition (a thumbnail in words):
  - A three-quarter camera 31 degrees up, low enough that the board's far
    edge drops behind the pieces: the crown and the crossed arms stand
    against the calm navy of the room, right under the title (title, crown,
    X: one vertical axis). The board is turned a little (34 degrees), so
    the winning row runs across the picture, falling gently to the right.
  - Value hierarchy, in order: the title; the crowned X (the only rose
    face: broad rose with a red sheen on its lower right, cream on the
    edges facing the key) and its brass crown; the near pieces; the far X
    and the board.
  - The crowned X is the king piece, bigger than the others (1.18 x), its
    raised arms flanking the crown like shoulders round a head. The far X
    (0.9 x) sits back in wine with red top edges, the near X (cut by the
    right edge) red with rose top edges. Every piece is turned a little to
    the left, so its shaded right side shows as a wine (or navy) depth band:
    chunky lacquered toys, painted in flat bands (no dither on lacquer).
  - One O, the foil: a big sapphire ring in the foreground at the bottom
    left, lit on its upper left (a clean terminator to navy on its right,
    a navy crescent inside the hole), flat felt seen through the hole, one
    tapered cream glint along its upper left.
  - The strike, the game's own win line, in the rainbow colour (index 15:
    it turns through the colour wheel on the device), thin and outlined in
    black: from beyond the far X, across it, behind the crowned one (the
    king is never struck through), ending at the near X's heart, clear of
    the install bar.
  - The crown is drawn by hand (25 px: a ray-marched one this small reads
    as a blob): three points with pearls, the back of the band dark through
    the valleys, the band seen from above (its foot curving down in the
    middle), lit brass from the left with a cream edge and lip, brown only
    on its last 4 px, one cut ruby in the middle (no row of stones that
    could read as a face), outlined in black, a wine shadow on the cross
    under its foot. A small star (cream, sapphire tips) on its right pearl.
  - Light: the house key from the top left (each piece lit as if it faced
    us, the key turned with it, so every face reads the same); a pool of
    light on the board round the crowned X, the felt in flat plateaus with
    narrow seams, the grid's bars brass in the pool and walnut outside it;
    short shadows falling to the lower right (every piece casts one); the
    near board and the bottom rows falling into shade; the room flat navy
    with one narrow seam down to black low at the sides. The frame's outer
    two pixels step a level down, so nothing bright touches the border.
  - Title: TIC TAC TOE over ROYALE, a bookish serif (New Century
    Schoolbook Bold) in gold leaf on the navy, alone in its golds. TIC TAC
    TOE in plain bands (a cream top row, light gold, gold: its 3 px strokes
    take no horizon or seams); ROYALE with a dark horizon, dithered seams
    only on strokes 6 px wide, a bevel on its outer contour (lone bevel
    pixels dropped). Depth in wine, a black outline and shadow, the
    pockets between letters closed in black, catch-light stars on ROYALE's
    A apex and TOE's last serif.

  Palette (11 own + cream, grey, black, red):
    gold1 gold2            the title's own: nothing else uses them
    wine rose              the lacquered crosses with red and cream (wine
                           also the title's depth, the crown's ruby)
    wood0 wood1 wood2      the walnut, the grid's brass bars (wood2, a dull
                           brass well clear of the title's gold) and the
                           crown; wood1 is also ROYALE's horizon and bevel
    felt0 felt1            the felt, with black
    sap0 sap1              the room (navy) and the O (sapphire)
    grey                   the pearls' shade
    rainbow                the strike

  Fonts: TIC TAC TOE is ncenB12 and ROYALE ncenB18, u8g2's bitmaps of the
  X11 New Century Schoolbook Bold (Adobe; the X11 notice permits use and
  modification with the notice kept): tools/art/title.txt and
  title_royale.txt, with their credits in their headers. By hand: TIC TAC
  TOE's word spaces opened to 7 px; ROYALE's Y and A hairlines evened to
  2 px.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import numpy as np  # noqa: E402
import artkit as ak  # noqa: E402
from artkit import render3d as R  # noqa: E402

TITLE = HERE / "art" / "title.txt"
TITLE2 = HERE / "art" / "title_royale.txt"
TITLE_ROWS = ["cream"] + ["gold2"] * 5 + ["gold1"] * 6       # TIC TAC TOE: a cream top row, light gold, gold
TITLE2_ROWS = ["cream"] + ["gold2"] * 4 + ["gold1"] * 3 + ["wood1"] * 2 + ["gold1"] * 4 + ["gold2"] * 3 + ["gold1"]

G = 1.4                                    # cell pitch on the board (world units)
VIEW = dict(el=31, yaw=34, d=5.6, fov=37, shift=(0, 24), target=(0.0, 0.3, 0.0))
TILT = 15                                  # pieces lean back toward the camera (degrees)
TURN = -24                                 # and turn their fronts to the left, so the shaded right sides show
X_CELLS = [(0, 1), (1, 1), (2, 1)]         # (column, row): row 0 far; the winning row
X_SCALE = [0.9, 1.18, 1.0]                 # far, crowned, near: the king is the biggest piece
HERO = 1                                   # the X (index) that wears the crown: the middle one
O_CELLS = [(1, 2)]
O_SCALE = [1.0]
O_NUDGE = (0.0, 0.12)                      # the O sits a little toward us on its cell, clear of the far X
PIECE_S = 1.25                             # the pieces' size
PAD = 0.57                                 # a felt pad's half width: the walnut strips between are G - 2 PAD wide
PIECE_Y = 0.54                             # a piece's centre above the felt (at scale 1)
CROWN_DROP = 1                             # the crown's foot below the notch of its cross's arms (pixels)

FLOOR, WOOD, FELT = 0, 1, 2
XS = [3, 4, 5]
OS = [6]
NMAT = 7


def camera():
    v = VIEW
    e, a = np.radians(v["el"]), np.radians(v["yaw"])
    t = np.asarray(v["target"], float)
    pos = t + v["d"] * np.array([np.sin(a) * np.cos(e), np.sin(e), np.cos(a) * np.cos(e)])
    return R.Camera(tuple(pos), tuple(t), fov=v["fov"], shift=v["shift"])


def cell_pos(i, j):
    return ((i - 1) * G, (j - 1) * G)


def piece_pos(i, j, is_x=True):
    x, z = cell_pos(i, j)
    return (x, z) if is_x else (x + O_NUDGE[0], z + O_NUDGE[1])


def facing(cam, x, z):
    """The turn about y that faces a piece at (x, z) to the camera."""
    return np.degrees(np.arctan2(cam.pos[0] - x, cam.pos[2] - z))


def x_piece(mat, sc):
    k = PIECE_S * sc
    arm = R.box((0.52 * k, 0.135 * k, 0.15 * k), 0.07 * k)
    return R.U(R.xf(R.prim(arm, mat), rot=R.rot_z(45)), R.xf(R.prim(arm, mat), rot=R.rot_z(-45)))


def o_piece(mat, sc):
    k = PIECE_S * sc
    return R.xf(R.prim(R.torus(0.32 * k, 0.125 * k), mat), rot=R.rot_x(90))


def piece_rot(cam, x, z):
    return R.rot_y(facing(cam, x, z) + TURN) @ R.rot_x(-TILT)


def pieces():
    """(material, cell, scale, is_x) for every piece."""
    return ([(XS[k], c, X_SCALE[k], True) for k, c in enumerate(X_CELLS)]
            + [(OS[k], c, O_SCALE[k], False) for k, c in enumerate(O_CELLS)])


def scene(cam):
    half = 1.5 * G + 0.16
    slab = R.xf(R.prim(R.box((half, 0.15, half), 0.06), WOOD), (0, -0.15, 0))
    cuts, pads = [], []
    for i in range(3):
        for j in range(3):
            x, z = cell_pos(i, j)
            cuts.append(R.xf(R.prim(R.box((PAD, 0.1, PAD), 0.02), WOOD), (x, 0.0, z)))
            pads.append(R.xf(R.prim(R.box((PAD, 0.05, PAD), 0.0), FELT), (x, -0.09, z)))
    board = R.U(R.Sub(slab, R.U(*cuts)), *pads)
    floor = R.prim(lambda p: p[:, 1] + 0.3, FLOOR)
    parts = [floor, board]
    for mat, (i, j), sc, is_x in pieces():
        x, z = piece_pos(i, j, is_x)
        shape = x_piece(mat, sc) if is_x else o_piece(mat, sc)
        parts.append(R.xf(shape, (x, PIECE_Y * sc, z), piece_rot(cam, x, z)))
    return R.U(*parts)


def level_of(v, table):
    """A float level from v through (v, level) pairs (piecewise linear)."""
    a = np.array(table, float)
    return np.interp(v, a[:, 0], a[:, 1])


# The crown, drawn by hand (a ray-marched one this small reads as a blob):
# 25 px across, three points with a pearl on each (cream, grey in shade),
# the back of the band dark through the valleys, the band seen from above
# (its foot curving down in the middle), lit from the left (a cream edge and
# lip, brass, brown only on its last 4 px), one cut ruby in the middle with
# a cream glint, outlined in black.
CROWN = [
    "............k............",
    "...........kck...........",
    "..........kccxk..........",
    "...k.......kxk.......k...",
    "..kck......kgk......kck..",
    ".kccxk....kcgmk....kccxk.",
    "..kxk.....kcgmk.....kxk..",
    "..kgk....kcggmmk....kmk..",
    ".kcgmk...kcggmmk...kgmdk.",
    ".kcgmkkkkcgggmmdkkkkgmdk.",
    "kcggmmmmkcgggmmdkdmmgmmdk",
    "kccgggmmmgggggmmmmmmmmmdk",
    "kcccccgggggmmmggggggmmmdk",
    "kcggggggggmwwwmggggggmmdk",
    "kcgggggggmwRcrwmgggggmmdk",
    "kcgggggggmwrRrwmggggggmdk",
    "kcggggggggmwrwmgggggggmdk",
    ".kggggggggggmggggggggmdk.",
    "..kkmmmmgggggggggmmmmkk..",
    "....kkkkmmmmmmmmmkkkk....",
    "........kkkkkkkkk........",
]
CROWN_FOOT = 19                            # the sprite's row at the band's foot (in the middle)
INK = {"k": "black", "d": "wood0", "m": "wood1", "g": "wood2", "c": "cream", "x": "grey", "r": "red",
       "R": "rose", "w": "wine"}


def edge_pass(pic, width=2):
    """The frame's outer `width` rows and columns a step darker on their own
    ramps, so nothing bright touches the border."""
    down = {"cream": "rose", "rose": "red", "red": "wine", "sap1": "sap0", "felt1": "felt0",
            "wood2": "wood1", "wood1": "wood0", "rainbow": "black", "grey": "wood0"}
    yy, xx = np.mgrid[0:128, 0:128]
    ring = (xx < width) | (xx > 127 - width) | (yy < width) | (yy > 127 - width)
    before = pic.idx.copy()
    for a, b in down.items():
        pic.put(ring & (before == pic.pal[a]), b)


def lone_bevel(pic, mask, face):
    """Bevel pixels in `mask` with no 8-neighbour of their own colour go back
    to the face colour under them (`face`: a name per pixel row, or one name)."""
    a = pic.idx
    ys, xs = np.nonzero(mask)
    for y, x in zip(ys, xs):
        k = a[y, x]
        nb = a[max(y - 1, 0):y + 2, max(x - 1, 0):x + 2]
        if (nb == k).sum() <= 1:
            pic.px(x, y, face[y] if isinstance(face, dict) else face)


def draw():
    P = ak.Palette({
        "sap0": "#141A58", "sap1": "#2C68E0",
        "felt0": "#0B4026", "felt1": "#1F8048",
        "wine": "#6A0A20",
        "wood0": "#2E1008", "wood1": "#6E3014", "wood2": "#C08A38",
        "rose": "#F26A5A", "gold1": "#EAA622", "gold2": "#FFEA8C",
    }, ramps=[["black", "sap0", "sap1", "cream"], ["black", "felt0", "felt1"], ["black", "wine", "red", "rose", "cream"],
              ["black", "wood0", "wood1", "wood2", "cream"], ["wood1", "gold1", "gold2", "cream"]])
    cv = ak.Canvas("#000000")
    s = cv.s
    yy, xx = np.mgrid[0:128, 0:128]
    cam = camera()
    key = -0.6 * cam.r + 0.62 * cam.u - 0.45 * cam.f                 # shading: up-left and toward us, as the picture shows it
    key /= np.linalg.norm(key)
    fwd = np.array([cam.f[0], 0.0, cam.f[2]])
    fwd /= np.linalg.norm(fwd)
    key_r = -0.4 * cam.r + 1.0 * np.array([0.0, 1.0, 0.0]) + 0.22 * fwd     # shadows: from high up-left, so short
    key_r /= np.linalg.norm(key_r)                                           # and falling to the lower right
    view = -cam.f

    # ---- the 3D: everything white under the light, for its geometry and shadows
    mats = [R.Mat("#FFFFFF", spec=0.0) for _ in range(NMAT)]
    out = R.render(cv, scene(cam), cam, mats, lights=[(tuple(key_r), "#FFFFFF", 1.0)], ambient="#000000", ss=2)
    own = R.majority(out, s)
    nrm = np.zeros((128, 128, 3))
    for k in range(NMAT):
        nk = ak.px_mean(out["normal"] * (out["mat"] == k)[..., None], s)
        nrm[own == k] = nk[own == k]
    nrm /= np.maximum(np.linalg.norm(nrm, axis=-1, keepdims=True), 1e-6)
    lam = np.clip(nrm @ key, 0, 1)
    lam_r = np.clip(nrm @ key_r, 0, 1)
    lum = ak.px_mean(out["rgb"].mean(-1), s)
    shadow = np.where(lam_r > 0.05, np.clip(lum / np.maximum(lam_r, 1e-3), 0, 1), 1.0)     # 0 where something shades it
    o_, d_ = cam.rays((xx + 0.5).ravel().astype(float), (yy + 0.5).ravel().astype(float))
    dep = ak.at_px(out["depth"], s).ravel()
    world = (o_ + d_ * np.where(np.isfinite(dep), dep, 0)[:, None]).reshape(128, 128, 3)
    pic = ak.Picture.blank(P, "black")

    hx, hz = cell_pos(*X_CELLS[HERO])
    pool = np.hypot(world[..., 0] - hx, world[..., 2] - hz)                # the light's pool, on the board's plane,
    pool += level_of(yy, [(98, 0.0), (126, 1.3)])                          # the near board falling into shade

    # where the crown goes: on the middle X, its foot a little under the
    # notch between the cross's raised arms
    hs = X_SCALE[HERO]
    rh = piece_rot(cam, hx, hz)
    notch = np.array((hx, PIECE_Y * hs, hz)) + rh @ np.array((0.0, 0.135 * PIECE_S * hs * 1.414, 0.0))
    nx_, ny_ = cam.project(notch)
    crown_xy = (int(round(nx_)), int(round(ny_ + CROWN_DROP)))
    cx0, cy0 = crown_xy[0] - len(CROWN[0]) // 2, crown_xy[1] - CROWN_FOOT
    cm = np.zeros((128, 128), bool)
    for j, row in enumerate(CROWN):
        for i, ch in enumerate(row):
            if ch != ".":
                cm[cy0 + j, cx0 + i] = True

    # ---- the room: flat navy, one narrow seam down to black low at the sides
    room = (own == FLOOR) | (own < 0)
    lr = level_of(np.hypot((xx + 0.5 - 64) / 1.0, (yy + 0.5 - 20) * 1.25), [(0, 1.0), (70, 1.0), (72.5, 0.0)])
    ak.by_level(pic, lr, ["black", "sap0"], room)

    # ---- the felt: a pool of light round the crowned X, the pieces' shadows
    # a step down
    felt = own == FELT
    nap = ak.noise((xx + 0.5, yy + 0.5), 9, seed=5, octaves=2) - 0.5          # the cloth's nap stirs the seams
    vig = level_of(yy, [(122, 0.0), (124, 1.0)])                             # the bottom rows fall into shade
    lf = level_of(pool + 0.12 * nap, [(0, 2.0), (1.7, 2.0), (1.82, 1.0), (2.5, 1.0), (2.62, 0.0)])
    lf -= (shadow < 0.5) * 1.0 + vig
    ak.by_level(pic, lf, ["black", "felt0", "felt1"], felt)

    # ---- the walnut: tops lit by the pool (the grid's bars brass in its light),
    # walls by how they face the key
    wood = own == WOOD
    top = nrm[..., 1] > 0.85
    lw = np.where(top, level_of(pool + 0.12 * nap, [(0, 3.0), (1.8, 3.0), (1.9, 2.0), (2.3, 2.0), (2.4, 1.0), (2.8, 1.0), (2.9, 0.0)]),
                  level_of(lam, [(0, 0.0), (0.3, 1.0), (0.6, 2.0)])
                  - level_of(pool, [(0, 0), (2.2, 0), (2.6, 1.0)]))
    lw -= (shadow < 0.5) * 1.0 + vig
    ak.by_level(pic, lw, ["black", "wood0", "wood1", "wood2"], wood)

    # ---- the pieces: lacquer in flat bands, by how they face the key (each
    # piece turns to face the camera, so each is lit as the crowned one is:
    # the key turned with it). The crowned X gets broad rose; the near X red
    # with rose on its top edges; the far X wine and red only.
    for mat, cell, sc, is_x in pieces():
        m = own == mat
        rk = piece_rot(cam, *piece_pos(*cell, is_x))
        kk = rk @ rh.T @ key
        lk = np.clip(nrm @ kk, 0, 1)
        hv = (kk + view) / np.linalg.norm(kk + view)
        sk = np.clip(nrm @ hv, 0, 1)
        if not is_x:                                   # the O: sapphire where the key reaches
            rp = ["black", "sap0", "sap1", "cream"]
            lp = level_of(lk, [(0, 1.0), (0.35, 1.0), (0.38, 2.0)])
        elif mat == XS[HERO]:
            rp = ["black", "wine", "red", "rose", "cream"]
            lp = level_of(lk, [(0, 1.0), (0.08, 1.0), (0.12, 2.0), (0.19, 2.0), (0.22, 3.0), (0.78, 3.0), (0.82, 4.0)])
        elif mat == XS[0]:
            rp = ["black", "wine", "red", "red"]
            lp = level_of(lk, [(0, 0.6), (0.06, 1.0), (0.5, 1.0), (0.56, 2.0)])
        else:
            rp = ["black", "wine", "red", "rose"]
            lp = level_of(lk, [(0, 0.8), (0.06, 1.0), (0.1, 1.0), (0.14, 2.0), (0.62, 2.0), (0.68, 3.0)])
        if is_x:
            lp -= (shadow < 0.5) * 0.6
        if mat == XS[HERO]:                            # a sheen: the upper left of the front rose, the lower right red
            hcx, hcy = cam.project((hx, PIECE_Y * hs, hz))
            sheen = (xx + 0.5 - hcx) + (yy + 0.5 - hcy)
            lp = np.where((lp > 2.9) & (lp < 3.9), 3.0 - level_of(sheen, [(9, 0.0), (13, 0.75)]), lp)
            lp = np.where((sk ** 60 > 0.5) & (shadow > 0.5), 4.0, lp)
        ak.by_level(pic, lp, rp, m, q=1)                # lacquer: flat bands, no dither
        if not is_x:                                   # the board through the O's hole: flat felt
            hole = ~m & ~ak.outside_of(m) & ~np.isin(own, XS)
            pic.put(hole, "felt1")

    # outlines: black on each piece's shadow side, and all round where it
    # stands in front of a farther piece
    allp = [p[0] for p in pieces()]
    order = sorted(allp, key=lambda k: -np.nanmean(np.where(own == k, dep.reshape(128, 128), np.nan)))
    for n_, k in enumerate(order):
        m = own == k
        ring = ak.dilate(m, 1) & ~m
        nearer = np.zeros_like(m)
        for k2 in order[n_ + 1:]:
            nearer |= own == k2
        behind = np.isin(own, order[:n_])
        shade_side = ring & (ak.shift(m, 1, 0) | ak.shift(m, 0, 1))
        pic.put(ring & ~nearer & (behind | shade_side), "black")

    # ---- the strike: the winning line, in the rainbow colour, from beyond the
    # far cross to the near one's heart, passing behind the crowned one
    cs = [np.array(cam.project((cell_pos(i, j)[0], PIECE_Y * X_SCALE[n], cell_pos(i, j)[1])))
          for n, (i, j) in enumerate(X_CELLS)]
    u = (cs[-1] - cs[0]) / np.linalg.norm(cs[-1] - cs[0])
    a_, b_ = cs[0] - u * 10, cs[-1] + u * 1
    hero_m = ak.dilate((own == XS[HERO]) | cm, 1)
    sm = ak.streak(pic, tuple(a_), tuple((a_ + b_) / 2), tuple(b_), 1.0, 1.7, cols=((None, 1.0),))
    sm &= ~hero_m
    pic.put(ak.dilate(sm, 1) & ~sm & ~hero_m, "black")
    pic.put(sm, "rainbow")

    # ---- the crown on the middle X, its shadow on the cross under its foot
    under = ak.shift(cm, 1, 1) & ~cm & (own == XS[HERO])
    pic.put(under & pic.where("red", "rose", "cream"), "wine")
    ak.patch(pic, cx0, cy0, CROWN, INK)

    # a last sweep for lone pixels in the scene (where levels meet)
    ak.despeckle(pic, need=3, within=(yy > 44) & ~cm, passes=2)

    # glints: the crown's top pearl and a star on its right one
    ak.glint(pic, crown_xy[0], cy0 + 1, 1)
    ak.glint(pic, cx0 + 21, cy0 + 5, 2, tip="sap1")                  # a star on its right pearl
    # the O's lacquer: one tapered cream glint along its upper left
    for mat, cell, sc, is_x in pieces():
        if is_x:
            continue
        m = own == mat
        ys_, xs_ = np.nonzero(m)
        ocx, ocy = (xs_.min() + xs_.max() + 1) / 2, (ys_.min() + ys_.max() + 1) / 2
        rad = np.hypot(xx + 0.5 - ocx, yy + 0.5 - ocy)
        ang = np.degrees(np.arctan2(-(yy + 0.5 - ocy), xx + 0.5 - ocx))
        r_out = rad[m & (ang > 100) & (ang < 170)].max()
        w = level_of(ang, [(108, 0.0), (122, 0.75), (138, 0.75), (152, 0.0)])
        arc = m & (np.abs(rad - (r_out - 3.2)) < w)
        pic.put(arc & (ak.nbrs(arc, diag=True)), "cream")                  # no lone pixel at its tapered ends
    edge_pass(pic)

    # ---- the title: gold leaf on the navy. Faces in bands (a cream top
    # row, light gold, on ROYALE a dark horizon, light again), a bevel on
    # ROYALE's outer contour, depth in wine, a black outline and shadow
    m1 = ak.load_mask(TITLE)
    m2 = ak.load_mask(TITLE2)
    x1, y1 = ak.centred_x(m1), 4
    x2, y2 = ak.centred_x(m2), 19
    M2 = ak.place(m2, x2, y2)
    rows1 = TITLE_ROWS
    t1 = ak.title(pic, m1, x1, y1, fill=None, rows=rows1, hi=None, lo=None,
                  extrude=dict(dx=1, dy=1, depth=1, colours=["wine"]), shadow=dict(dx=1, dy=2, colour="black"))
    rows2 = TITLE2_ROWS
    t2 = ak.title(pic, m2, x2, y2, fill=None, rows=rows2, hi=None, lo=None,
                  extrude=dict(dx=1, dy=1, depth=2, colours=["wine", "wine"]), shadow=dict(dx=1, dy=2, colour="black"))
    ck = ak.checker()
    wide = ak.erode(M2, 1) & (ak.runs(M2, 1) >= 6)
    for r_, c_ in [(y2 + 5, "gold2"), (y2 + 10, "wood1"), (y2 + 14, "gold1")]:
        pic.put(wide & (yy == r_) & ck, c_)
    face = {y2 + r: c for r, c in enumerate(rows2)}
    hi_, lo_ = ak.bevel_contour(pic, M2, "cream", "wood1")
    lone_bevel(pic, hi_ | lo_, face)
    ak.despeckle(pic, need=4, within=ak.dilate(t1["all"] | t2["all"], 2) & (yy < 48), passes=2)
    blk = pic.where("black")
    nb = ak.shift(blk, 1, 0).astype(int) + ak.shift(blk, -1, 0) + ak.shift(blk, 0, 1) + ak.shift(blk, 0, -1)
    pic.put((nb >= 3) & pic.where("sap0", "wine", "wood1") & ~t1["all"] & ~t2["all"] & (yy < 46), "black")
    ak.lonely(pic, "wine", ak.dilate(t1["all"] | t2["all"], 1) & (yy < 46), into="black")   # lone depth pixels in notches
    # catch-lights: four-pointed stars on ROYALE's A (its apex) and TOE's last serif
    ak.glint(pic, x2 + 68, y2, 2, arms=(2, 2, 2, 1), tip="gold2")         # the A's apex is its columns 68-69
    ak.glint(pic, x1 + m1.shape[1] - 2, y1, 1, arms=(1, 2, 2, 1), tip="gold2")
    return pic.image()


def title_lines():
    """The title's lettering as drawn here, and its depth, for the title
    screen (tools/titleart.py: the game paints it in the house gold).
    TIC TAC TOE, then ROYALE."""
    return [dict(mask=ak.load_mask(TITLE), depth=1, side="wine"),
            dict(mask=ak.load_mask(TITLE2), depth=2, side="wine")]


if __name__ == "__main__":
    import boxart
    boxart.save(draw(), HERE.parent / "docs" / "cart.png")
