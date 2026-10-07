"""docs/cart.png, CHBlackjack's cover in the visual menu (docs/cover-art.md).
`chgame boxart` redraws it; edit this, not the PNG.

THE BRIEF (revision 3)
  Message: 21 beats the house. The dealer has just pitched you the ace of
  spades onto your king of hearts: blackjack, the instant before it lands.

  Composition: the camera sits at the player's seat, looking down across
  the table at three-quarter.
  - The table: a dark padded rail sweeps across under the title as the far
    arc of the table's ellipse, its ends running off both sides, so the
    felt is a stage and the black room beyond it is the title's ground. The
    rail is black leather; its crown catches the lamp in a wine band that
    thins toward the ends, with one clean red specular line in the middle.
    A printed arc (two lines, a flat level up from the cloth) follows it
    behind the cards.
  - Light: one lamp, the house key from the top left; everything casts its
    shadow to the lower right. The felt is painted as levels: a pool with a
    lamp-hot core under the ace, falling off in plateaus with narrow seams
    to teal at the rail and the frame (a spotlight: the cards and the bet
    sit in it, the table's edges sink into the dark).
  - Focal point: the ace of spades in the air, the biggest and brightest
    shape, leaning right and tipped back (a keystone), its top corner in
    front of the rail. Cream where the lamp strikes its upper left, falling
    to ivory through a narrow 25/50/75% seam; card stock (grey) along its
    right and bottom edges; a black outline. Its spade is drawn mirror-true
    and leaned a row at a time with the card (twin lobes), lacquered: a
    grey crescent on its upper left and a cream catch-light star. Its shadow
    lies well clear on the felt (an L beyond its right and bottom edges, a
    level or so down), with lit felt under its lower left: it is airborne.
  - The king of hearts lies on the felt at the left, leaning left, so the
    pair fans into a V. A hand-drawn double-headed court card: a three-point
    crown with cream pearls and red and cream jewels, brown hair, eyes
    turned toward the ace, a wine moustache curled up at the ends, a red
    mouth, a pointed beard, an ermine collar, a red robe with wine folds.
    It leans by rows (each row moves as a block, so eyes, brows and
    moustache stay whole and its sides step 5-5-5); ivory stock with cream
    lit edges, a black outline on its shadow sides; its K and heart in red.
  - The second beat: the dealer's left hand at the upper right, open and
    palm down, fingers spread from the release, the thumb on the far side,
    7+ px clear of the ace. Drawn by hand over a tube study: lit tops,
    skin0 undersides, wine where a finger meets the next, black splits,
    cream catch-lights on the fingertips, the thumb's knuckle and one
    knuckle cluster. A white cuff (cream on top, grey beneath) with a ruby
    link, the sleeve's dark mouth, the wine jacket sleeve (red on top,
    black beneath, as the game's dealer wears) running off the frame over
    the rail's end. The hand's shadow falls on the felt below it.
  - Motion: three curved speed lines trail from the ace's trailing edge back
    up toward the hand, of different lengths: cream roots a few pixels off
    the card, ivory, grey tails, a felt0 edge under each.
  - Foreground: the bet, a stack of red chips cropped by the lower right
    corner (render3d cylinders painted by hand: cream edge spots by angle,
    wine and black on the shaded side, a wine inlay ring, a glint on the
    top chip's rim), on its printed betting circle.
  - Eye path: title, ace (its spade's glint), hand, king, chips.
  - Title: BLACKJACK, alone in gold on the black room. A chrome face (gold2
    sky, gold1, a gold0 horizon, gold2, gold1 ground), cream along the
    letters' tops, the lower bands' left edges lit gold2 so the 3-px strokes
    read as rounded tubes, a bronze (gold0) edge where the face meets its
    wine extrusion (3 deep), a black outline and drop shadow, glints over
    black on the B's and the K's top corners.

PALETTE (11 own + cream, grey, black, red)
  felt0..felt3  the felt: teal in the dark to lamp-hot green (the cool depth)
  ivory         card stock (the ace's lower face, the king's paper), the
                streaks, the cuff
  wine          the rail's crown, the sleeve, the chips' shade, the king's
                moustache and folds, the title's depth
  skin0, skin1  the hand, the king's face, hair and crown
  gold0..gold2  the title's own: nothing else uses them
  cream the highlights and glints; grey the card stock, the cuff's shade,
  the streaks' tails; red the chips, the rail's specular, the king's robe
  and index; black the outlines and the room.

FONT  title.txt: ONE HUNDRED AND FIFTY NINE, from the bmf collection (bmf-cz;
      author and terms not stated: a `?` face, chosen for its rounded Vegas
      tubes), set at its own size.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import numpy as np  # noqa: E402
import artkit as ak  # noqa: E402
from artkit import render3d as R  # noqa: E402

TITLE = HERE / "art" / "title.txt"

PAL = {
    "felt0": "#072A34", "felt1": "#0E5A3A", "felt2": "#23904A", "felt3": "#62BA4C",
    "ivory": "#C6B294",
    "wine": "#5E0C22",
    "skin0": "#A4542C", "skin1": "#EAA46C",
    "gold0": "#8E4A08", "gold1": "#EAA21A", "gold2": "#FFE67A",
}
FELT = ["black", "felt0", "felt1", "felt2", "felt3"]
PAPER = ["black", "grey", "ivory", "cream"]
REDS = ["black", "wine", "red"]
SKIN = ["black", "wine", "skin0", "skin1", "cream"]
GOLD = ["gold0", "gold1", "gold2", "cream"]
# one step down each ramp: a cast shadow, the frame
STEP = {"felt3": "felt2", "felt2": "felt1", "felt1": "felt0", "felt0": "black",
        "cream": "ivory", "ivory": "grey", "grey": "black", "red": "wine", "wine": "black",
        "skin1": "skin0", "skin0": "wine"}

S = 4
YY, XX = np.mgrid[0:128, 0:128]
XC, YC = XX + 0.5, YY + 0.5

# ---- the layout ---------------------------------------------------------------------------
TITLE_Y = 4
TITLE_TUBE = True
TITLE_EXTRUDE = dict(dx=1, dy=1, depth=3, side="wine", bottom="wine", edge="gold0")
RAIL_O = (64.0, 95.0, 85.0, 59.0)        # the far rail's outer edge: an ellipse (centre, radii)
RAIL_I = (64.0, 95.0, 82.0, 51.0)        # its foot on the felt
RAIL_HI = [(0.2, 0.62, "red")]           # its specular: where across it (0 the far edge, 1 the foot), half-arc (rad)
PRINTED = (64.0, 95.0, 74.0, 42.0, 3.0)  # the printed arc on the felt: an ellipse, the band's width
ACE = dict(c=(58.5, 70.0), w=40.0, h=57.0, rot=10.0, key=0.86)     # in the air: centre, size, lean, keystone
SPADE_GLINT = 1                          # the spade's catch-light: arm length
ACE_SHADOW = dict(scale=0.82, dx=14.0, dy=17.0, soft=1.3, depth=1.5)          # on the felt far below
KING = dict(c=(26.0, 93.0), lean=0.2)                               # on the felt: centre, lean (px across per row)
POOL = (64, 100, 70, 50)                                            # the lamp's pool: centre, radii
POOL_T, POOL_LV = [0, 0.25, 0.5, 0.75, 0.95, 1.2], [4.2, 3.6, 2.8, 1.9, 1.1, 0.6]   # its fall-off: distance -> level
BET_R = (24.0, 10.0)                                                # the betting circle's radii
CHIPS_AT = (111, 122)
CHIP_TH = 0.19
CHIP_STACK = [(0.0, 0.0, 0.0), (0.05, 0.02, 0.6), (-0.04, 0.03, 0.2), (0.02, -0.03, 0.9), (0.06, 0.0, 0.4),
              (0.0, 0.03, 0.7)]
HAND_AT = (88, 39)                       # the hand sprite's top-left on the picture
HAND_SHADOW = (7, 16)
ARM_DIR = (1.0, -0.42)                   # from the wrist up the forearm
WRIST = (29.0, 16.0)                     # in the sprite: where the cuff starts
CUFF = (4.5, 7.0)                        # the shirt cuff: its length along the arm, its radius
SLEEVE = 8.4                             # the jacket sleeve's radius
# speed lines from the ace's trailing edge back up toward the hand: root, control, end, radii
STREAKS = [((83, 61), (89, 61.5), (93.5, 60), 0.85, 0.55), ((81.7, 70.5), (95, 71.5), (104, 66.5), 1.4, 0.55),
           ((80.4, 80.5), (92, 81.5), (101.5, 76.5), 1.1, 0.55)]


def card_quad(c, w, h, rot, key=1.0):
    """A card's corners (top-left, top-right, bottom-right, bottom-left): centred
    on c, its top leaning `rot` degrees right, its top edge `key` times the bottom's."""
    a = np.radians(rot)
    rx, ry = np.cos(a), np.sin(a)
    dx, dy = -np.sin(a), np.cos(a)
    cx, cy = c
    return [(cx - rx * w / 2 * key - dx * h / 2, cy - ry * w / 2 * key - dy * h / 2),
            (cx + rx * w / 2 * key - dx * h / 2, cy + ry * w / 2 * key - dy * h / 2),
            (cx + rx * w / 2 + dx * h / 2, cy + ry * w / 2 + dy * h / 2),
            (cx - rx * w / 2 + dx * h / 2, cy - ry * w / 2 + dy * h / 2)]


# ---- the king of hearts: drawn by hand, upright (the upper half; the lower is it turned round)
KING_HALF = [
    ".....kck.kck.kck.....",
    ".....k1k.k1k.k1k.....",
    "....kk11k111k11kk....",
    "....k1c111111111k....",
    "....k0r0c0r0c0r0k....",
    "...k00kkkkkkkkk00k...",
    "..k000111111111000k..",
    "..k00w1ww111ww10w0k..",
    "..k00w1ck111ck10w0k..",
    "..k00w1111101110w0k..",
    "..k00ww11www11w0w0k..",
    "..k00w1wwwwwww10w0k..",
    "..k000000rrr000000k..",
    "...k00000www00000k...",
    "..kk.k000w0w0000k.kk.",
    ".kccck.k00w000k.kcck.",
    "kckcckc.k00w0k.ckcckk",
    "kccckccc.k0w0k.ccckck",
    "krrrrrcccck0kccccrrrk",
    "krwrrrrrcccccccrrrwrk",
    "krrwrrrrrcckccrrrwrrk",
    "krrrwrrrrrkrkrrrwrrrk",
]
GLYPH = {
    "A": ["..##..", "..##..", ".####.", ".#..#.", "##..##", "######", "##..##", "##..##"],
    "K": ["##..##", "##.##.", "####..", "###...", "####..", "##.##.", "##..##", "##..##"],
    "s": ["..#..", ".###.", "#####", "#####", "..#.."],
    "h": [".#.#.", "#####", "#####", ".###.", "..#.."],
}
INK = {"k": "black", "1": "skin1", "0": "skin0", "w": "wine", "c": "cream", "i": "ivory", "r": "red",
       "s": "grey", "C": "ivory", ".": "ivory", "E": "cream"}

# ---- the dealer's hand: his left, palm down, fingers spread from the pitch,
# the thumb on the far side (drawn by hand over a tube study)
HAND = [
    "..............kkk..............",
    ".............kc11kk............",
    ".............k011111k..........",
    "....kkkkkkkk..k001111kk........",
    "...kc1111111kkkkw0111c1k.......",
    "...k00111111111kkk011111k......",
    "....kk00001111111k101111k......",
    "......kkkw00011111k101111k.....",
    ".........kkkw0001111101111k....",
    "............kkkw0cc11111111k...",
    "........kkkkkkkk1c111111111k...",
    "..kkkkkk11111111111111111111k..",
    ".kc11111111111111111111111111k.",
    "k1111111111111111111111111110k.",
    "k110000000000000011111111110k..",
    ".k0wkkkkkkkkkkkk1111111110000k.",
    "..kk.......kk11111111111000000k",
    "........kkk11111111110000000wk.",
    "......kk1111111101100000000wwk.",
    "....kk1111110000wk0000000wwwk..",
    "...kc1111100wkkkk100000wwwwk...",
    "...k110000kkk.k111100wwwwkk....",
    "...k00wkkk...k11110wkkkkk......",
    "....kkk....kk11100kk...........",
    ".........kk111100k.............",
    "........kc11100kk..............",
    "........k1100kk................",
    ".........k0kk..................",
    "..........k....................",
]


def king_grid():
    """The king of hearts upright, 37 x 52, as letters (INK; ' ' is not card)."""
    W, H = 37, 52
    g = np.full((H, W), "C", dtype="<U1")
    for x, y in [(0, 0), (1, 0), (0, 1), (W - 1, 0), (W - 2, 0), (W - 1, 1), (0, H - 1), (1, H - 1), (0, H - 2),
                 (W - 1, H - 1), (W - 2, H - 1), (W - 1, H - 2)]:
        g[y, x] = " "
    for y in range(H):                                   # the lit top and left edges of the stock
        x = next(i for i in range(W) if g[y, i] != " ")
        g[y, x] = "E"
    for x in range(W):
        y = next(j for j in range(H) if g[j, x] != " ")
        g[y, x] = "E"
    hh, hw = len(KING_HALF), len(KING_HALF[0])
    assert all(len(r) == hw for r in KING_HALF)
    ox, oy = 8, 4
    for j, r in enumerate(KING_HALF):
        for i, ch in enumerate(r):
            if ch != ".":
                g[oy + j, ox + i] = ch
                g[oy + 2 * hh - 1 - j, ox + hw - 1 - i] = ch
    for key, y0 in (("K", 2), ("h", 11)):
        for j, r in enumerate(GLYPH[key]):
            for i, ch in enumerate(r):
                if ch == "#":
                    g[y0 + j, 1 + i] = "r"
                    g[H - 1 - y0 - j, W - 2 - i] = "r"
    return g


def shearsprite(g, lean, cx, cy, bg=" "):
    """Pixel art leaning `lean` pixels across per row (its top to the left),
    its middle on (cx, cy): each row moves as a block, so a row of eyes or a
    moustache stays whole, and the sides step evenly. Returns a 128 x 128
    grid of letters (bg where it is not)."""
    H, W = g.shape
    out = np.full((128, 128), bg, dtype=g.dtype)
    x0, y0 = int(round(cx - W / 2)), int(round(cy - H / 2))
    for j in range(H):
        dx = int(np.floor(lean * (j - H / 2) + 0.5))
        y = y0 + j
        if not 0 <= y < 128:
            continue
        for i in range(W):
            x = x0 + i + dx
            if 0 <= x < 128 and g[j, i] != bg:
                out[y, x] = g[j, i]
    return out


def stamp(pic, key, x, y, colour, flip=False, lean=0.0):
    """A glyph with its top-left at (x, y), leaned `lean` px across per row up
    (each row moves as a block, like the spade)."""
    rows = GLYPH[key]
    if flip:
        rows = [r[::-1] for r in rows[::-1]]
    h = len(rows)
    for j, r in enumerate(rows):
        dx = int(np.floor(lean * ((h - 1) / 2 - j) + 0.5))
        ak.patch(pic, int(round(x)) + dx, int(round(y)) + j, [r], {"#": colour})


def cov(d):
    return ak.px_mean((d < 0).astype(np.float32), S)


def rrect_uv(U, V, w, h, r=4.5):
    qx = np.abs(U - w / 2) - (w / 2 - r)
    qy = np.abs(V - h / 2) - (h / 2 - r)
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r


def uv2xy(quad, u, v, w, h):
    Hm = ak.homography([(0, 0), (w, 0), (w, h), (0, h)], quad)
    p = Hm @ np.array([u, v, 1.0])
    return p[0] / p[2], p[1] / p[2]


def spade(P, cx, cy, s):
    """A spade: a pointed top, round shoulders, two lobes, a flared stem
    (a distance field in P's units)."""
    X, Y = P
    x, y = (X - cx) / s, (Y - cy) / s
    R_, a, yc = 1.19, 0.32, 0.12
    lens = np.maximum(np.hypot(x + a, y - yc) - R_, np.hypot(x - a, y - yc) - R_)
    lens = np.maximum(lens, y - yc - 0.2)
    lobes = np.minimum(np.hypot(x - 0.44, y - 0.2) - 0.45, np.hypot(x + 0.44, y - 0.2) - 0.45)
    stem = ak.polygon((x, y), [(-0.08, 0.35), (0.08, 0.35), (0.16, 0.85), (0.42, 1.2), (-0.42, 1.2), (-0.16, 0.85)])
    return np.minimum(np.minimum(lens, lobes), stem) * s


def spade_px(size, c, lean, n=4):
    """The big spade as pixels: drawn upright and mirror-true (an odd width,
    its axis on a pixel's middle), then leaned with the card a row at a time
    (each row moves as a block, so the lobes stay twins). c: where its
    middle lands; lean: pixels across per row up."""
    W = 2 * int(size * 1.6) + 1
    Hh = int(size * 3.0)
    yc = int(size * 1.4)
    o = (np.arange(n) + 0.5) / n - 0.5
    xs = (np.arange(W) - (W - 1) / 2)[None, :, None, None] + o[None, None, None, :]
    ys = (np.arange(Hh) - yc)[:, None, None, None] + o[None, None, :, None]
    xs, ys = np.broadcast_arrays(xs, ys)
    t = (spade((xs, ys), 0.0, 0.0, size) < 0).mean(axis=(2, 3)) >= 0.5
    out = np.zeros((128, 128), bool)
    x0, y0 = int(round(c[0] - (W - 1) / 2 - 0.5)), int(round(c[1] - yc - 0.5))
    for j in range(Hh):
        dx = int(np.floor(-lean * (j - yc) + 0.5))
        for i in np.nonzero(t[j])[0]:
            x, y = x0 + i + dx, y0 + j
            if 0 <= x < 128 and 0 <= y < 128:
                out[y, x] = True
    return out


def darken(pic, mask, steps=1):
    """Every pixel under the mask a step (or more) down its ramp, each step from
    the picture as it was (no cascade)."""
    P = pic.pal
    for _ in range(steps):
        src = pic.idx.copy()
        for a_, b_ in STEP.items():
            if a_ in P.index:
                pic.idx[mask & (src == P[a_])] = P[b_]


def soft_shadow(mask, soft):
    """A hard mask's shadow as 0..1, its edge softened over `soft` pixels."""
    d_in = ak.distance_px(~mask, 6)
    d_out = ak.distance_px(mask, 6)
    sd = np.where(mask, -d_in + 0.5, d_out - 0.5)
    return np.clip(0.5 - sd / (2 * soft), 0, 1)


def ell(e, x=None, y=None):
    """How far out a point is on an ellipse (cx, cy, rx, ry): 1 on it."""
    cx, cy, rx, ry = e[:4]
    x = XC if x is None else x
    y = YC if y is None else y
    return np.hypot((x - cx) / rx, (y - cy) / ry)


def sprite_mask(rows, x0, y0):
    """A letter sprite on the picture: its letters as a (128, 128) array ('' where none)."""
    g = np.full((128, 128), "", dtype="<U1")
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != "." and 0 <= y0 + j < 128 and 0 <= x0 + i < 128:
                g[y0 + j, x0 + i] = ch
    return g


def draw():
    P = ak.Palette(PAL, ramps=[FELT, PAPER, REDS, SKIN, GOLD])
    pic = ak.Picture.blank(P, "black")
    cv = ak.Canvas("#000000", ss=S)
    X, Y = cv.P
    glints = []

    # ---- where things are (masks first: the felt takes every shadow in its levels)
    aq = card_quad(ACE["c"], ACE["w"], ACE["h"], ACE["rot"], ACE["key"])
    CW, CH = ACE["w"], ACE["h"]
    aU, aV = ak.quad_uv(cv.P, aq, CW, CH)
    am = cov(rrect_uv(aU, aV, CW, CH)) >= 0.5
    sc, (sx_, sy_) = ACE_SHADOW["scale"], ACE["c"]
    sq = [(sx_ + (x - sx_) * sc + ACE_SHADOW["dx"], sy_ + (y - sy_) * sc + ACE_SHADOW["dy"]) for x, y in aq]
    sU, sV = ak.quad_uv(cv.P, sq, CW, CH)
    ash = cov(rrect_uv(sU, sV, CW, CH)) >= 0.5

    kg = shearsprite(king_grid(), KING["lean"], *KING["c"])
    km = kg != " "

    hg = sprite_mask(HAND, *HAND_AT)
    hand = hg != ""
    wx, wy = HAND_AT[0] + WRIST[0] + 0.5, HAND_AT[1] + WRIST[1] + 0.5
    axv = np.array(ARM_DIR) / np.hypot(*ARM_DIR)
    nxv = np.array([axv[1], -axv[0]])                  # across the arm, pointing up
    alg = (XC - wx) * axv[0] + (YC - wy) * axv[1]      # per pixel: along the arm, across it
    acr = (XC - wx) * nxv[0] + (YC - wy) * nxv[1]
    m_cf = (alg >= 0) & (alg < CUFF[0]) & (np.abs(acr) < CUFF[1])
    m_mo = (alg >= CUFF[0]) & (alg < CUFF[0] + 1) & (np.abs(acr) < SLEEVE) & (acr < SLEEVE - 1.6)
    m_sl = (alg >= CUFF[0]) & (np.abs(acr) < SLEEVE) & ~m_mo
    arm = hand | m_cf | m_sl | m_mo

    # the chips: render3d for the shapes (painted by hand below)
    E = np.radians(27)
    cam = R.Camera((0, 0.9 + 20 * np.sin(E), 20 * np.cos(E)), (0, 0.9, 0), ortho=8.2)
    fx, fy = cam.project((0, 0, 0))
    cam.shift = (CHIPS_AT[0] - fx, CHIPS_AT[1] - fy)
    cparts = [R.xf(R.prim(R.cylinder(1.0, CHIP_TH * 0.96, 0.05), k), (dx, CHIP_TH + 2 * CHIP_TH * k, dz))
              for k, (dx, dz, _) in enumerate(CHIP_STACK)]
    out = R.render(cv, R.U(*cparts), cam, [R.Mat("#FFFFFF", spec=0.0)] * len(CHIP_STACK), ss=2, shadows=False,
                   ao=False, region=(CHIPS_AT[0] - 18, CHIPS_AT[1] - 40, 128, 128))
    cmat = R.majority(out, S)
    allc = cmat >= 0

    # ---- the table: felt inside the far rail, the room black beyond it
    e_o, e_i = ell(RAIL_O), ell(RAIL_I)
    felt_m = (e_i < 1) | (YC > RAIL_I[1])
    rail_m = ~felt_m & ((e_o < 1) | (YC > RAIL_O[1]))

    # the felt: a pool of lamplight where the cards land, falling off into the
    # dark toward the far rail and the frame; the cloth's nap stirs it
    t = np.hypot((XC - POOL[0]) / POOL[2], (YC - POOL[1]) / POOL[3])
    nz = ak.noise((XC, YC), 9, seed=3, octaves=2) - 0.5
    lv = np.interp(t + 0.08 * nz, POOL_T, POOL_LV)
    lv -= np.clip((0.16 - (1 - e_i)) / 0.16, 0, 1) * 1.3            # the far felt, under the rail
    edge_px = np.minimum(np.minimum(XC, YC), np.minimum(128 - XC, 128 - YC))
    lv -= np.clip((6 - edge_px) / 6, 0, 1) ** 1.5 * 1.6            # the frame
    # shadows on the cloth, as levels: the ace's and the hand's (far below them), the
    # rail's foot, the king's and the chips' contact
    sh_ = soft_shadow(ash, ACE_SHADOW["soft"]) * ACE_SHADOW["depth"] + soft_shadow(ak.shift(arm, *HAND_SHADOW), 0.6) * 1.3
    lv = np.where(sh_ > 0, np.maximum(lv - sh_, np.minimum(lv, 1.0)), lv)     # shadows end at felt0
    lv -= (ak.shift(km, 1, 2) & ~km) * 1.0
    lv -= (ak.shift(allc, 3, 2) & ~allc) * 1.0
    ak.by_level(pic, ak.terrace(lv, 0.16), FELT, felt_m)
    pic.put(felt_m & ak.shift(rail_m, 0, 1), "black")                 # the rail's foot

    # the printed arc: two thin lines a flat level up from the cloth they are printed on
    cx_, cy_, rx_, ry_, bw = PRINTED
    ep = np.hypot((X - cx_) / rx_, (Y - cy_) / ry_)
    line1 = np.abs(ep - 1) * ry_ - 0.5
    line2 = np.abs(ep - 1 + bw / ry_) * ry_ - 0.5
    pr = ((cov(line1) >= 0.5) | (cov(line2) >= 0.5)) & felt_m & (YY < cy_)
    put_lv = np.clip(np.round(lv) + 1, 2, 4).astype(int)
    for k_, nm in enumerate(FELT):
        pic.put(pr & (put_lv == k_), nm)

    # the rail: padded black leather; its crown catches the lamp in a wine band,
    # with a red specular line that thins and stops away from the middle
    u = np.clip((1 - e_o) / np.maximum((1 - e_o) + (e_i - 1), 1e-6), 0, 1)
    pic.put(rail_m, "black")
    lamp = np.clip(1 - np.abs(XC - 64) / 74, 0, 1)
    pic.put(rail_m & (u > 0.07) & (u < 0.07 + 0.42 * (0.45 + 0.55 * lamp)), "wine")
    cxr, cyr = RAIL_O[0], RAIL_O[1]
    for frac, half, colour in RAIL_HI:
        rx_ = RAIL_O[2] + (RAIL_I[2] - RAIL_O[2]) * frac
        ry_ = RAIL_O[3] + (RAIL_I[3] - RAIL_O[3]) * frac
        a = np.linspace(np.pi / 2 - half, np.pi / 2 + half, 400)
        pts = [(cxr + rx_ * np.cos(t_), cyr - ry_ * np.sin(t_)) for t_ in a]
        ak.ink(pic, pts, colour, where=rail_m)

    # ---- the betting circle under the chips: printed, a level up from the cloth
    bx, by = CHIPS_AT
    ring_d = np.abs(np.hypot((X - bx) / BET_R[0], (Y - by + 1) / BET_R[1]) - 1) * BET_R[1] - 0.5
    ring_m = (cov(ring_d) >= 0.5) & ~allc
    src = pic.idx.copy()
    for a_, b_ in (("felt0", "felt1"), ("felt1", "felt2"), ("felt2", "felt3")):
        pic.idx[ring_m & (src == P[a_])] = P[b_]

    ak.despeckle(pic, need=5, within=felt_m & ~ak.dilate(km | allc | am, 1))

    # ---- the king, lying on the felt
    ring_k = ak.dilate(km, 1) & ~km
    shade_side = (ak.shift(km, 1, 0) | ak.shift(km, 0, 1) | ak.shift(km, 1, 1)) & ~ak.shift(km, -1, 0)
    pic.put(ring_k & shade_side, "black")
    for ch, nm in INK.items():
        pic.put(kg == ch, nm)

    # ---- the ace: in the air, lit from the top left; card stock along its shadow sides
    ru = np.hypot(ak.at_px(aU, S) / CW, ak.at_px(aV, S) / CH * 0.8)
    lit = 3 - np.clip((ru - 0.56) / 0.07, 0, 1)
    ak.by_level(pic, lit, ["black", "grey", "ivory", "cream"], am)
    au, av = ak.at_px(aU, S), ak.at_px(aV, S)
    rim_in = ak.erode(am, 1)
    stock = am & ~rim_in & ((au > CW * 0.55) | (av > CH * 0.55))
    darken(pic, stock)
    c0 = np.array(uv2xy(aq, CW / 2, CH * 0.48, CW, CH))
    up_ = np.array(uv2xy(aq, CW / 2, CH * 0.48 - 10, CW, CH)) - c0
    k_ = np.linalg.norm(up_) / 10
    sp = spade_px(13.0 * k_, c0, up_[0] / -up_[1]) & am
    pic.put(sp, "black")
    ul = sp & (~ak.shift(sp, 0, 1) | ~ak.shift(sp, 1, 0))
    inner = ak.erode(sp, 1)
    ys_, xs_ = np.nonzero(sp)
    scx, scy = xs_.mean(), ys_.min() + 0.62 * np.ptp(ys_)
    crest = inner & ak.dilate(ul, 1) & (XX < scx - 1) & (YY < scy)
    pic.put(crest, "grey")
    ln = up_[0] / -up_[1]
    x0, y0 = uv2xy(aq, 3.3, 3.5, CW, CH)
    stamp(pic, "A", x0, y0, "black", lean=ln)
    x0, y0 = uv2xy(aq, 4.0, 13.5, CW, CH)
    stamp(pic, "s", x0, y0, "black", lean=ln)
    x0, y0 = uv2xy(aq, CW - 9.3, CH - 11.5, CW, CH)
    stamp(pic, "A", x0, y0, "black", flip=True, lean=ln)
    x0, y0 = uv2xy(aq, CW - 9.0, CH - 18.5, CW, CH)
    stamp(pic, "s", x0, y0, "black", flip=True, lean=ln)
    pic.put(ak.dilate(am, 1) & ~am, "black")
    ys_, xs_ = np.nonzero(sp)                                       # the lacquer's catch-light: upper left of the spade
    gx, gy = ak.glint_in(sp & ~crest, int(np.percentile(xs_, 30)), int(np.percentile(ys_, 30)), size=SPADE_GLINT, reach=5)
    glints.append((gx, gy, (SPADE_GLINT,) * 4))

    # ---- the flick: speed lines from the ace's trailing edge back up toward the hand
    ok = ~ak.dilate(am, 2) & ~ak.dilate(arm, 1) & felt_m
    for root, ctrl, end, r0, r1 in STREAKS:
        sm = ak.streak(pic, root, ctrl, end, r0, r1, ok, cols=(("cream", 0.14), ("ivory", 0.55), ("grey", 1.0)))
        under = ak.shift(sm, 0, 1) & ~sm & ok
        pic.put(under & pic.where("felt1", "felt2", "felt3"), "felt0")

    # ---- the dealer's arm: a wine sleeve (its lit top red), its dark mouth, a white
    # cuff round the wrist (cream on top, grey beneath) with a ruby link; the hand
    for ch, nm in {"k": "black", "1": "skin1", "0": "skin0", "w": "wine", "c": "cream"}.items():
        pic.put(hg == ch, nm)
    sleeve = m_cf | m_sl | m_mo
    pic.put(ak.dilate(sleeve, 1) & ~sleeve & ~hand, "black")
    pic.put(m_sl, "wine")
    pic.put(m_sl & (acr > SLEEVE - 2.4), "red")
    pic.put(m_sl & (acr < -SLEEVE * 0.45), "black")
    pic.put(m_mo, "black")
    pic.put(m_cf, "ivory")
    pic.put(m_cf & (acr > 2.0), "cream")
    pic.put(m_cf & (acr < -3.5), "grey")
    pic.put(m_cf & ak.shift(hand & ~m_cf & ~pic.where("black"), 1, 0), "black")   # the wrist goes into the cuff
    lk = np.array([wx, wy]) + axv * 2.2 - nxv * 1.0
    ak.patch(pic, int(np.floor(lk[0])), int(np.floor(lk[1])), ["cr", "rr"], {"r": "red", "c": "cream"})

    # ---- the bet: a stack of red chips (stripes by the angle round each chip, lit on the left)
    cn = ak.at_px(out["normal"], S)
    dep = ak.at_px(out["depth"], S)
    o_, d_ = cam.rays(XC.reshape(-1).astype(float), YC.reshape(-1).astype(float))
    zz = np.where(np.isfinite(dep.reshape(-1)), dep.reshape(-1), 0)
    cp = (o_ + d_ * zz[:, None]).reshape(128, 128, 3)
    Lc = np.array([-0.55, 0.75, 0.45])
    Lc /= np.linalg.norm(Lc)
    for k, (dx, dz, ph) in enumerate(CHIP_STACK):
        m = cmat == k
        lx_, lz_ = cp[..., 0] - dx, cp[..., 2] - dz
        ang = np.arctan2(lz_, lx_) + ph
        rad = np.hypot(lx_, lz_)
        top = m & (cn[..., 1] > 0.6)
        side = m & ~top
        dfc = (cn * Lc).sum(-1)
        spot = (np.mod(ang, np.pi / 3) < 0.38) & (np.abs(cn[..., 0]) < 0.93)
        pic.put(side, "red")
        pic.put(side & (dfc < 0.25), "wine")
        pic.put(side & (dfc < -0.2), "black")
        pic.put(side & spot, "cream")
        pic.put(side & spot & (dfc < 0.25), "ivory")
        pic.put(side & spot & (dfc < -0.2), "grey")
        pic.put(top, "red")
        pic.put(top & (rad > 0.78) & spot, "cream")
        pic.put(top & (np.abs(rad - 0.55) < 0.07), "wine")
    for k in range(len(CHIP_STACK) - 1):
        pic.put((cmat == k) & ak.shift(cmat == k + 1, 0, 1), "black")
    ak.despeckle(pic, need=4, within=allc, passes=2)
    pic.put(ak.dilate(allc, 1) & ~allc, "black")
    tk = len(CHIP_STACK) - 1
    tdx, tdz, _ = CHIP_STACK[tk]
    gx_, gy_ = cam.project((tdx - 0.9, 2 * CHIP_TH * (tk + 1), tdz - 0.42))
    glints.append((int(gx_), int(gy_), (2, 2, 2, 2)))

    # ---- the frame: things (not the felt, which has its own vignette) step down into the dark
    edge_d = np.minimum(np.minimum(XX, YY), np.minimum(127 - XX, 127 - YY))
    things = ~(pic.where(*FELT[1:]) & felt_m)
    darken(pic, (edge_d == 2) & things)
    pic.put((edge_d <= 1) & things, "black")
    darken(pic, edge_d <= 0)
    ak.despeckle(pic, need=4, within=ak.dilate(allc, 1) & (edge_d <= 4), passes=2)

    # ---- the title
    m = ak.load_mask(TITLE)
    tx = ak.centred_x(m) - 1
    Mt = ak.place(m, tx, TITLE_Y)
    ak.title(pic, m, tx, TITLE_Y, fill=["gold2"], hi=None, lo=None,
             rows=["gold2"] * 8 + ["gold1"] * 2 + ["gold0"] + ["gold2"] * 2 + ["gold1"] * 8,
             extrude=TITLE_EXTRUDE,
             shadow=dict(dx=1, dy=2, colour="black"))
    top = Mt & ak.shift(ak.outside_of(Mt), 0, 1) & (YY < TITLE_Y + 9)
    top = top & (ak.shift(top, 1, 0) | ak.shift(top, -1, 0))
    pic.put(top, "cream")
    if TITLE_TUBE:                                                 # the lower bands' lit left edge: rounded tubes
        lo = Mt & (YY > TITLE_Y + 10) & ~ak.shift(Mt, 1, 0) & ak.shift(Mt, -1, 0) & ak.shift(Mt, -2, 0)
        lo &= ak.shift(lo, 0, 1) | ak.shift(lo, 0, -1)               # runs only, no lone pixels
        pic.put(lo & pic.where("gold1"), "gold2")
    for gx, gy, arms in glints:
        ak.glint(pic, gx, gy, tip="ivory", arms=arms)
    ys_, xs_ = np.nonzero(Mt)
    for gx, gy, arms in ((xs_[ys_ == TITLE_Y].min(), TITLE_Y, (2, 1, 2, 1)), (xs_[ys_ == TITLE_Y].max(), TITLE_Y, (1, 2, 2, 1))):
        ak.glint(pic, int(gx), int(gy), tip="gold2", arms=arms)
    return pic.image()


def title_lines():
    """The title's lettering as drawn here, and its depth, for the title
    screen (tools/titleart.py: the game paints it in the house gold)."""
    return [dict(mask=ak.load_mask(TITLE), depth=2, side="wine")]            # thin strokes: less depth than the cover's


if __name__ == "__main__":
    import boxart
    boxart.save(draw(), HERE.parent / "docs" / "cart.png")
