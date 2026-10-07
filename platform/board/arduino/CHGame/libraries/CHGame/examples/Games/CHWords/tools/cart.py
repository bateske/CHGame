"""docs/cart.png, WORDS' picture in the visual menu (docs/cover-art.md).
`chgame boxart` redraws it; edit this, not the PNG.

THE BRIEF (revision 6)
  Message: the game's tiles come alive. WORDS has sprung up off the board
  in five ivory tiles and dances above it in an arch, each with its score,
  each throwing its shadow on the cloth below; a big Z, worth ten, tumbles
  down in the foreground; between them the fifteen-by-fifteen board waits,
  its premium squares set in like enamel, the gold star glowing on its
  square where the first word must land. You read the name, the tiles in
  the air and the board at a glance.
  Composition (thumbnail):
      . . . . . . . R . . . . . . .      the room: a wine dome behind the
      . . . O . . R R R . . D . . .      title, black at the top corners
      . W W O O . R R R . D D S S .      five tiles in a fanned arch, the R
      . W W O O . . 1 . . D D S S .      highest, the outer ones turned 10
      . . 4 . 1 . . . . . . 2 . 1 .      degrees, the inner 5
      ~~~~ the board's far rows ~~~~     in the key's pool
      ( )  ( )   ( )   ( )  ( )          their shadows, a band of green
      Z Z  TL . . . . . . . . . TL .     below each foot: smaller and
      Z Z Z .  DL . . . . DL . . . .     lighter the higher the hop
      Z Z Z ) . . [ * ] . . . . . .      the Z cut by the frame, its shadow
      Z Z ) ) . . . . . . . . DL . .     right of it; the star in its glow
  Depth: the Z (foreground, nearest, darkest ivory), the board and its star
  (middle), the dancing title over the far rows (back), the room behind.
  Camera: above the near edge, looking down the board at about 25 degrees,
  so the squares grow from 12 px at the far edge to 29 px at the bottom;
  the centre square is 25 x 17 px, so the star (18 x 11) sits on it with
  its wine enamel showing all round.
  Light: the house key from the top left. The board is painted per pixel
  as levels on the felt's ramp: the key's pool over the middle rows (the
  tiles' stage), the star's own glow round it, both stirred by the cloth's
  nap and falling to black at the frame; dithered only in narrow seams, and
  never on the thin far rows. Every square is a raised pillow: a lit lip on
  its top and left, a shaded edge on its right and foot, solid grooves
  between (one step below the shade), drawn as clean lines: the rows flat,
  the columns converging. Premium squares are enamel set in: their far and
  left walls in shade; the far rows' and the dark ones a step down; the
  two lit DLs with a gleam; the near ones labelled; those cut by the frame
  left plain. The star: its outline is a flat star seen through the camera,
  each arm two facets lit by where they face (cream, gold, ivory0), a red
  rim toward the key and black away, a glint on the arm facing the key.
  Shadows: an oval under each title tile, thrown right as it rises, the
  darkest green with a dithered rim, the grooves inside black; the Z's, its
  own shape thrown down and right.
  The title: the tiles are the lettering. Each is a block built from its
  geometry (a clean silhouette at any turn): a face, a 3 px top face and,
  away from the middle, its side (those left of the middle show their right
  side, in shade; those right of it their left, lit), shaded as a pillow (a
  cream top and left rim, the face ivory2 falling through ivory1 to an
  ivory0 rim along its foot and right side, round the corners); its letter
  turned RotSprite's way (Scale2x three times, sampled at each pixel, breaks
  mended), cut in black with the cut's lower right wall lit (tan); its digit
  stamped upright on the face's lower right, two pixels clear of the letter
  and the rim. Drawn right to left, so each casts a shadow on the one behind
  it to its right and no digit is covered; black outlines, a black drop
  shadow on the room, glints on the R's and the W's top corners.
  The Z: the same block, bigger (32 x 35, a 5 px top, its right side
  showing) and turned 20 degrees, in the near shade: ivory1 and darker
  only, so the title keeps ivory2 and cream; its 10 on the lower right.
  Palette (11 own + cream, black, red; grey unused):
    felt0 felt1 felt2           the board's felt: deep teal to warm green
    navy blue                   the DL / TL enamel
    wine gold                   the room, the DW enamel and the star's square;
                                the star (with ivory0, cream; red its rim)
    tan ivory0 ivory1 ivory2    the tiles: ivory2 and the cream faces are the
                                title's alone (cream also the glints, the
                                star's lit facets and the enamel's gleam)
  Font: ncenB18 (the title) and ncenB24 (the Z), u8g2's bitmaps of the X11
  distribution's New Century Schoolbook Bold (Adobe; the X11/Adobe notice,
  as Yacht Dice's timB: use, copy, modify and distribute with the notice
  kept), at their own sizes (tools/art/title.txt, hero_z.txt, credits in
  their headers); the W trimmed to 20 px so it fits its tile with rim to
  spare. The labels and digits (3 x 5) and the star are drawn here.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import numpy as np  # noqa: E402
import artkit as ak  # noqa: E402
from artkit import render3d as R  # noqa: E402

TITLE = HERE / "art" / "title.txt"
HERO_GLYPH = HERE / "art" / "hero_z.txt"

# ---- the board ----------------------------------------------------------------------
CAMERA = ((0.0, 3.6, 4.6), (0.0, 0.0, -3.2), 46, (0, 0))     # pos, target, fov, lens shift
QUARTER = [[4, 0, 0, 1, 0, 0, 0, 4],         # the game's own layout (Words.cpp): 1 DL, 2 TL, 3 DW, 4 TW
           [0, 3, 0, 0, 0, 2, 0, 0],
           [0, 0, 3, 0, 0, 0, 1, 0],
           [1, 0, 0, 3, 0, 0, 0, 1],
           [0, 0, 0, 0, 3, 0, 0, 0],
           [0, 2, 0, 0, 0, 2, 0, 0],
           [0, 0, 1, 0, 0, 0, 1, 0],
           [4, 0, 0, 1, 0, 0, 0, 3]]
LABEL = {1: "DL", 2: "TL", 3: "DW", 4: "TW"}
FELT_R = ["black", "felt0", "felt1", "felt2"]
INSET, ROUND = 0.13, 0.16                    # an inlay's margin and corner radius (squares)
STAR_INSET = 0.04                            # the star's square: nearly the whole square
STAR_TONES = ["cream", "cream", "gold1", "gold1", "gold1", "gold1",          # its ten facets, the one facing
              "gold0", "gold0", "gold0", "gold0"]                    # the key most first
FAR_ROWS = 3                                 # the inlays this far back sit in the title's shade
ROOM = "wine"                                # the room behind the title
POOL = (0.0, -2.8, 5.2, 3.2)                 # the key's pool: centre x, z, radius x, z (squares)
POOL_RP = [0.0, 0.5, 0.85, 1.2, 1.7]         # its falloff: distance ...
POOL_LV = [3.4, 2.7, 1.7, 1.0, 0.4]          # ... -> level on the felt
GLOW = (2.1, 1.7)                            # the star's glow: radius x, z (squares)
GLOW_RP = [0.0, 0.5, 0.85, 1.3]
GLOW_LV = [3.5, 2.7, 1.7, 0.9]
NAP = 0.06                                   # the cloth's nap: how much it stirs the pool's seams

# ---- the tiles ----------------------------------------------------------------------
FW, FH, TOP = 26, 30, 3                      # a tile's face and its top face (px)
RAD = 2.6                                    # its corners
CX = [18, 41, 64, 87, 110]                   # each tile's middle (x)
FOOT = [52, 45, 38, 45, 52]                  # where its foot would be, upright (y)
TURN = [-10, -5, 2, 5, 10]                   # each tile's turn as it dances (degrees, clockwise)
SIDE = [2, 1, 0, -1, -2]                     # how much of each tile's side shows (px): the camera is in the middle
ORDER = [4, 3, 2, 1, 0]                      # back to front: right to left, so no digit is covered
SHADOW_Y = [66, 65, 66, 65, 66]              # where each tile's shadow lies on the board (centre y)
TONES = dict(top="cream", lit_side="gold1", dark_side="gold0", face="gold2", crease="gold2", rim="cream",
             band="gold1", edge="gold0", wall="brown")      # a title tile's parts
HERO = dict(glyph="Z", score="10", cx=19, foot=117, deg=-20, side=3, top=5, fw=32, fh=35,
            tones=dict(top="gold1", lit_side="gold0", dark_side="gold0", face="gold1", crease="gold0",
                       rim="gold1", band="gold0", edge="brown", wall="gold0"))   # the tile flying in, in the near shade
HERO_SHADOW = (9, 13)                        # where its shadow falls, from it (px)
GLINTS = [(2, (2, 2, 3, 1)), (0, (2, 2, 2, 1))]   # (tile, arms: left, right, up, down) on its top left corner
SCORE = {"W": "4", "O": "1", "R": "1", "D": "2", "S": "1"}       # the game's own values (Words.cpp)
DIGITS = {"1": [".#.", "##.", ".#.", ".#.", "###"],
          "2": ["##.", "..#", ".#.", "#..", "###"],
          "4": ["#.#", "#.#", "###", "..#", "..#"],
          "0": [".#.", "#.#", "#.#", "#.#", ".#."]}
SMALL = {"D": ["##.", "#.#", "#.#", "#.#", "##."], "L": ["#..", "#..", "#..", "#..", "###"],
         "T": ["###", ".#.", ".#.", ".#.", ".#."], "W": ["#...#", "#...#", "#.#.#", "#.#.#", ".#.#."]}


def premium(r, c):
    r = np.where(r > 7, 14 - r, r)
    c = np.where(c > 7, 14 - c, c)
    return np.array(QUARTER)[np.clip(r, 0, 7), np.clip(c, 0, 7)]


def stamp(rows):
    return np.array([[c == "#" for c in r] for r in rows], bool)


def word_mask(s):
    """A label in the small letters (SMALL), a pixel apart."""
    parts = [stamp(SMALL[c]) for c in s]
    m = np.zeros((5, sum(p.shape[1] for p in parts) + len(parts) - 1), bool)
    x = 0
    for p in parts:
        m[:, x:x + p.shape[1]] = p
        x += p.shape[1] + 1
    return m


def letters_of(m):
    """The title's letters, split at the empty columns between them."""
    cols = m.any(axis=0)
    out, x = [], 0
    while x < m.shape[1]:
        if cols[x]:
            e = x
            while e < m.shape[1] and cols[e]:
                e += 1
            out.append(m[:, x:e])
            x = e
        else:
            x += 1
    return out


def mode_px(a, s, values):
    """Each pixel's most common value among its s x s samples (from `values`)."""
    blk = a.reshape(128, s, 128, s).transpose(0, 2, 1, 3).reshape(128, 128, s * s)
    best = np.full((128, 128), values[0])
    cnt = np.full((128, 128), -1)
    for v in values:
        c = (blk == v).sum(-1)
        take = c > cnt
        best = np.where(take, v, best)
        cnt = np.where(take, c, cnt)
    return best


def step_down(pic, mask, pairs):
    """Every pixel in `mask` one step along `pairs` (colour -> colour)."""
    base = pic.idx.copy()
    for a_, b_ in pairs:
        pic.idx[mask & (base == pic.pal[a_])] = pic.pal[b_]


def scale2x(m):
    """A mask blown up 2x by Scale2x (EPX): diagonals come out smooth."""
    h, w = m.shape
    P = np.pad(m, 1)
    A, D = P[0:h, 1:w + 1], P[2:h + 2, 1:w + 1]
    C, B = P[1:h + 1, 0:w], P[1:h + 1, 2:w + 2]
    out = np.zeros((2 * h, 2 * w), bool)
    out[0::2, 0::2] = np.where((C == A) & (C != D) & (A != B), A, m)
    out[0::2, 1::2] = np.where((A == B) & (A != C) & (B != D), B, m)
    out[1::2, 0::2] = np.where((D == C) & (D != B) & (C != A), C, m)
    out[1::2, 1::2] = np.where((B == D) & (B != A) & (D != C), D, m)
    return out


def bridge(m, n):
    """A turned letter's breaks mended: while it falls into more than n
    8-connected parts, the background pixel that touches two parts (the
    fewest new neighbours first) joins them."""
    m = m.copy()
    for _ in range(12):
        lab = parts8(m)
        if lab.max() <= n:
            break
        best = None
        for y, x in zip(*np.nonzero(~m & ak.dilate(m, 1, diag=True))):
            nb = lab[max(0, y - 1):y + 2, max(0, x - 1):x + 2]
            ks = set(nb[nb > 0].tolist())
            if len(ks) >= 2:
                c = int((nb > 0).sum())
                if best is None or c < best[0]:
                    best = (c, y, x)
        if best is None:
            break
        m[best[1], best[2]] = True
    return m


def parts8(m):
    """The 8-connected parts of a small mask, labelled 1..n."""
    lab = np.zeros(m.shape, np.int32)
    n = 0
    for y0, x0 in zip(*np.nonzero(m)):
        if lab[y0, x0]:
            continue
        n += 1
        st = [(y0, x0)]
        lab[y0, x0] = n
        while st:
            y, x = st.pop()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < m.shape[0] and 0 <= xx < m.shape[1] and m[yy, xx] and not lab[yy, xx]:
                        lab[yy, xx] = n
                        st.append((yy, xx))
    return lab


def rbox(x, y, x0, y0, x1, y1, r):
    """A rounded box's distance field (negative inside)."""
    cx, cy, hw, hh = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
    qx = np.abs(x - cx) - hw + r
    qy = np.abs(y - cy) - hh + r
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r


# ---- a title tile -------------------------------------------------------------------

def tile(cv, glyph, cx, foot, deg, side, FW=FW, FH=FH, TOP=TOP, tones=None, gy=2):
    """One tile in the air, its foot at `foot`, turned `deg` about its
    middle: a block whose back is `side` px across and TOP px up from its
    face on the picture (so the tiles left of the middle show their right
    side, those right of it their left), its silhouette from the geometry
    (clean whatever the turn). Shaded as a pillow lit from the top left: a
    cream top face, the side toward the key ivory1 and the one away ivory0,
    a cream left rim on the face, the face ivory2 falling through ivory1 to
    an ivory0 rim along its foot and right side, curving round the corners;
    its letter turned RotSprite's way, cut in black with the cut's lower
    right wall lit (tan). Returns its colours {name: mask}, body, face,
    letter and where its digit goes. tones: other colours for its parts."""
    t_ = dict(TONES, **(tones or {}))
    s = cv.s
    px, py = cx, foot - FH / 2                       # the face's middle on the picture
    th = np.radians(deg)
    c, sn = np.cos(th), np.sin(th)

    def local(X, Y):                                 # picture -> the face's own pixels (x 0..FW, y 0..FH)
        dx, dy = X - px, Y - py
        return c * dx + sn * dy + FW / 2, -sn * dx + c * dy + FH / 2
    bx, by = c * side + sn * -TOP, -sn * side + c * -TOP      # the back's offset, in the face's frame

    def block(x, y):
        return np.minimum.reduce([rbox(x - t * bx, y - t * by, 0, 0, FW, FH, RAD) for t in np.linspace(0, 1, 7)])
    lx, ly = local(cv.X, cv.Y)
    body = ak.px_mean((block(lx, ly) < 0).astype(np.float32), s) >= 0.5
    yy, xx = np.mgrid[0:128, 0:128]
    ux, uy = local(xx + 0.5, yy + 0.5)
    fy = uy
    face = body & (rbox(ux, uy, 0, 0, FW, FH, RAD) < 0)
    back = body & ~face
    if side:
        u = np.where(side > 0, ux - FW, -ux) / max(abs(bx), 1e-6)
        v = uy / by
        sidef = back & (u > 0) & ((uy >= 0) | (v <= u))
    else:
        sidef = np.zeros_like(back)
    sidef |= back & (uy >= FH / 2)                  # the back seen past the face's lower corners
    top = back & ~sidef
    cols = {}

    def put(m, nm):
        for k in cols:
            cols[k] &= ~m
        cols[nm] = cols.get(nm, np.zeros((128, 128), bool)) | m
    put(top, t_["top"])
    put(sidef, t_["lit_side"] if side < 0 else t_["dark_side"])
    put(face, t_["face"])
    put(face & ak.paint.nbrs(top) & (ux > 1.5), t_["crease"])
    put(face & (ux < 1.15) & (fy < FH - 3.5), t_["rim"])
    put(face & (rbox(ux + 2.2, fy + 3.6, 0, 0, FW, FH, RAD) > 0), t_["band"])
    put(face & (rbox(ux + 1.0, fy + 1.0, 0, 0, FW, FH, RAD) > 0), t_["edge"])
    # the letter: upright in the tile's own pixels, turned RotSprite's way
    # (blown up 8x by Scale2x, so its diagonals stay smooth, then sampled
    # at each pixel's middle); any break mended
    gh, gw = glyph.shape
    gx = (FW - gw) / 2
    G = glyph
    for _ in range(3):
        G = scale2x(G)
    ix = np.floor((ux - gx) * 8).astype(int)
    iy = np.floor((uy - gy) * 8).astype(int)
    inside = (ix >= 0) & (iy >= 0) & (ix < G.shape[1]) & (iy < G.shape[0])
    letter = np.zeros((128, 128), bool)
    letter[inside] = G[iy[inside], ix[inside]]
    letter = bridge(letter, parts8(glyph).max()) & face
    wall = letter & ~ak.shift(letter, -1, -1) & ak.shift(ak.erode(letter, 1), 1, 1)
    wall &= ak.paint.nbrs(wall, diag=True)           # a lone lit pixel stays black
    put(letter, "black")
    put(wall, t_["wall"])
    # where the digit goes: the face's lower right, turned with it
    ax, ay = FW - 6.0 - (2 if FW > 28 else 0), FH - 7.5
    ax, ay = ax - FW / 2, ay - FH / 2
    at = (px + c * ax - sn * ay, py + sn * ax + c * ay)
    return dict(cols=cols, body=body, face=face, letter=letter, at=at)


def seat_digit(T, digit):
    """The digit, upright, at the spot nearest the tile's `at` that lies two
    pixels in from the face's rim and two clear of the letter."""
    parts = [stamp(DIGITS[d]) for d in digit]
    dst = np.zeros((5, sum(q.shape[1] for q in parts) + len(parts) - 1), bool)
    x_ = 0
    for q in parts:
        dst[:, x_:x_ + q.shape[1]] = q
        x_ += q.shape[1] + 1
    ok = ak.erode(T["face"], 2) & ~ak.dilate(T["letter"], 2, diag=True)
    best = None
    ax, ay = int(round(T["at"][0])), int(round(T["at"][1]))
    for dy in range(-4, 4):
        for dx in range(-4, 4):
            m = ak.place(dst, ax + dx, ay + dy)
            if m.sum() == dst.sum() and not (m & ~ok).any():
                if best is None or dx * dx + dy * dy < best[0]:
                    best = (dx * dx + dy * dy, m)
    return best[1] if best else ak.place(dst, ax, ay)


def star_px(cv, cam, ro=0.40, ri=0.185):
    """The centre star's facets on the picture: {colour: mask}, and its
    whole mask. Its outline is the star drawn flat on the board (ro, ri: its
    outer and inner radius, squares) seen through the camera; each arm is
    two facets sloping down from its ridge, lit by where its outer edge
    faces on the picture, ranked: STAR_TONES, from the one facing the key
    (top left) most. Also returns each facet's light."""
    Lk = np.array([-0.62, -0.78])
    O, I_ = [], []
    for i in range(5):
        a = np.radians(-90 + 72 * i)
        O.append(np.array(cam.project((ro * np.cos(a), 0.0, ro * np.sin(a)))))
        b = a + np.radians(36)
        I_.append(np.array(cam.project((ri * np.cos(b), 0.0, ri * np.sin(b)))))
    C = np.array(cam.project((0.0, 0.0, 0.0)))
    lab = np.full((cv.N, cv.N), -1, np.int16)
    vals = []
    for i in range(5):
        for k, (p, q) in enumerate(((I_[i - 1], O[i]), (O[i], I_[i]))):
            e = q - p
            n = np.array([e[1], -e[0]])
            if n @ ((p + q) / 2 - C) < 0:
                n = -n
            n /= np.linalg.norm(n)
            d = ak.polygon((cv.X, cv.Y), [tuple(C), tuple(p), tuple(q)])
            lab[d < 0] = len(vals)
            vals.append(float(n @ Lk))
    best = mode_px(lab, cv.s, [-1] + list(range(len(vals))))
    out = {}
    rank = np.argsort(np.argsort(-np.array(vals)))           # 0: the facet facing the key most
    for k, v in enumerate(vals):
        nm = STAR_TONES[rank[k]]
        out[nm] = out.get(nm, np.zeros((128, 128), bool)) | (best == k)
    return out, best >= 0, vals


# ---- the picture --------------------------------------------------------------------

def draw():
    P = ak.Palette({
        "felt0": "#062A22", "felt1": "#0E5634", "felt2": "#2A8A48",
        "navy": "#142C66", "blue": "#3A74D8",
        "wine": "#6A1430",
        "brown": "#4E2408", "gold0": "#9C5810", "gold1": "#E8A01C", "gold2": "#FFE07A",
    }, ramps=[FELT_R, ["black", "navy", "blue"], ["black", "wine", "red"],
              ["black", "brown", "gold0", "gold1", "gold2", "cream"]])
    cv = ak.Canvas("#000000")
    s = cv.s
    pic = ak.Picture.blank(P, "black")
    yy, xx = np.mgrid[0:128, 0:128]
    X, Y = xx + 0.5, yy + 0.5
    cp, ct, fov, sh = CAMERA
    cam = R.Camera(cp, ct, fov=fov, shift=sh)

    def board_uv(Xs, Ys):
        o, d = cam.rays(Xs.reshape(-1).astype(np.float64), Ys.reshape(-1).astype(np.float64))
        down = d[:, 1] < -1e-6
        t = np.where(down, -o[:, 1] / np.where(down, d[:, 1], -1), 1e9)
        p = o + d * t[:, None]
        return ((p[:, 0] + 7.5).reshape(Xs.shape), (p[:, 2] + 7.5).reshape(Xs.shape),
                down.reshape(Xs.shape))

    def proj(u, v, h=0.0):
        return cam.project((u - 7.5, h, v - 7.5))

    # ---- the board: each pixel's place on it
    U, V, dn = board_uv(X, Y)
    board = dn & (V >= 0) & (V < 15)
    us, vs, dns = board_uv(cv.X, cv.Y)
    on_s = dns & (vs >= 0) & (vs < 15)
    row, col = np.floor(V).astype(int), np.floor(U).astype(int)

    # ---- the room: a wine dome behind the title, falling to black at the top corners
    rv = np.hypot((X - 64) / 86, (Y - 52) / 58)
    room = ~board
    ak.by_level(pic, ak.terrace(np.clip((1.02 - rv) / 0.2, 0, 1), 0.3), ["black", ROOM], room)

    # ---- the light: the key's pool over the middle rows (the tiles' stage)
    # and the star's own glow round it; stirred by the cloth's nap
    nap = NAP * (ak.noise((X, Y * 1.6), 9.0, seed=3, octaves=2) - 0.5)
    rp = np.hypot((U - 7.5 - POOL[0]) / POOL[2], (V - 7.5 - POOL[1]) / POOL[3])
    lv = np.interp(rp + nap, POOL_RP, POOL_LV)
    rg = np.hypot((U - 7.5) / GLOW[0], (V - 7.5) / GLOW[1])
    lv = np.maximum(lv, np.interp(rg + nap, GLOW_RP, GLOW_LV))
    lv -= np.clip((Y - 108) / 20, 0, 1) * 1.6                    # the frame's foot into the dark
    lv -= np.clip((np.abs(X - 64) - 40) / 22, 0, 1) * 1.2         # and its sides
    lv = np.where(board, lv, 0)

    # ---- the grid: rows are flat lines, columns clean converging lines
    grid = np.zeros((128, 128), bool)
    hrow = {}
    for k in range(0, 16):
        y_ = int(np.floor(proj(7.5, k)[1]))
        if 0 <= y_ < 128:
            grid[y_, :] = True
            hrow[k] = y_
    for j in range(0, 16):
        a, b = proj(j, 0.0), proj(j, 10.5)
        for x_, y_ in ak.paint.line_px([a, b]):
            if 0 <= x_ < 128 and 0 <= y_ < 128:
                grid[y_, x_] = True
    grid &= board
    sq = board & ~grid
    rowh = np.zeros((128, 128))
    for k in range(15):
        if k in hrow and k + 1 in hrow:
            rowh[(row == k)] = hrow[k + 1] - hrow[k] - 1
        elif k in hrow:
            rowh[(row == k)] = 30
    lip_t = sq & ak.shift(grid, 0, 1) & (rowh >= 7)
    lip_l = sq & ak.shift(grid, 1, 0)
    sh_b = sq & ak.shift(grid, 0, -1) & (rowh >= 9)
    sh_r = sq & ak.shift(grid, -1, 0)

    # ---- the felt in levels, every square a raised pillow: a lit lip on its
    # top and left, a shaded edge on its right and foot, solid grooves between
    rl = np.round(lv).astype(int)
    ak.by_level(pic, ak.terrace(lv, 0.16), FELT_R, sq & (rowh >= 8))
    ak.paint.put_levels(pic, sq & (rowh < 8), rl, FELT_R)        # thin far rows: flat, no one-row seams
    ak.paint.put_levels(pic, sh_b | sh_r, np.maximum(rl - 1, 0), FELT_R)
    ak.paint.put_levels(pic, (lip_t | lip_l) & ~sh_b, np.minimum(rl + 1, 3), FELT_R)
    ak.paint.put_levels(pic, grid, np.maximum(rl - 2, 0), FELT_R)

    # ---- the inlays: enamel set into the squares, lit in the pool
    fx, fy = us - np.floor(us), vs - np.floor(vs)
    rs_, cs_ = np.floor(vs).astype(int), np.floor(us).astype(int)
    prs = np.where(on_s, premium(rs_, cs_), 0)
    ins = np.where((rs_ == 7) & (cs_ == 7), STAR_INSET, INSET)
    q = np.maximum(np.abs(fx - 0.5) - (0.5 - ins - ROUND), 0)
    r_ = np.maximum(np.abs(fy - 0.5) - (0.5 - ins - ROUND), 0)
    inl = np.hypot(q, r_) < ROUND
    cell = np.where(on_s & inl & (prs > 0), rs_ * 15 + cs_, -1)
    ids = [-1] + sorted(set(np.unique(cell).tolist()) - {-1})
    pc = mode_px(cell, s, ids)
    star_cell = 7 * 15 + 7
    for cid in ids[1:]:
        mm = (pc == cid) & sq
        if mm.sum() < 3:
            continue
        rr, cc = divmod(cid, 15)
        kind = int(premium(np.array(rr), np.array(cc)))
        ys_, xs_ = np.nonzero(mm)
        if xs_.min() <= 5 or xs_.max() >= 122:
            continue                                          # cut by the frame: left plain
        L_ = float(lv[ys_, xs_].mean())
        lit = L_ > 2.0
        wall = mm & (~ak.shift(mm, 0, 1) | ~ak.shift(mm, 1, 0))
        if kind == 1:
            face_c, wall_c = ("blue", "navy") if lit else ("navy", "black")
        elif kind == 2:
            face_c, wall_c = ("navy", "black")
        elif kind == 3:
            face_c, wall_c = ("wine", "black")
        else:
            face_c, wall_c = ("red", "wine") if lit else ("wine", "black")
        if L_ < 0.7 or rr <= FAR_ROWS:                        # the far rows and the dark: a step down
            face_c, wall_c = {"blue": "navy", "navy": "black", "wine": "black", "red": "wine"}[face_c], "black"
        pic.put(mm, face_c)
        pic.put(wall, wall_c)
        if face_c == "blue":                                      # lit enamel: a gleam near its far left corner
            inner = mm & ~wall
            ys2, xs2 = np.nonzero(inner)
            y_ = ys2.min()
            xr = xs2[ys2 == y_]
            for x_ in range(int(xr.min()) + 2, int(xr.min()) + 5):
                if inner[y_, x_]:
                    pic.px(x_, y_, "cream" if x_ < xr.min() + 4 else "gold1")
        if (xs_.max() - xs_.min() >= 15 and ys_.max() - ys_.min() >= 9 and cid != star_cell and rr > FAR_ROWS
                and xs_.min() > 2 and xs_.max() < 125):
            lab = word_mask(LABEL[kind])
            lx = int(round(xs_.mean() - lab.shape[1] / 2 + 0.5))
            ly = int(round(ys_.mean() - 2.0))
            ink = {"blue": "navy", "navy": "blue", "wine": "red", "red": "wine"}.get(face_c)
            if ink:
                pic.put(ak.place(lab, lx, ly) & mm & ~wall, ink)

    # ---- the board's far rim: a band of the room's wine, its inner face black
    rim_top = (yy >= int(np.floor(proj(7.5, -0.45, 0.2)[1]))) & (yy < int(np.floor(proj(7.5, 0, 0.2)[1])))
    rim_in = (yy >= int(np.floor(proj(7.5, 0, 0.2)[1]))) & ~board & (yy < 60)
    pic.put(rim_top, ROOM)
    pic.put(rim_in, "black")
    room &= ~(rim_top | rim_in)

    # ---- the centre star: a raised five-point star on its square, its facets
    # lit by where they face (cream toward the key, gold, ivory0 away)
    star, sall, _ = star_px(cv, cam)
    ak.selout(pic, sall, "black", "red")                          # its glow toward the key, its shade away
    for nm, mk in star.items():
        pic.put(mk, nm)
    ak.despeckle(pic, need=3, within=ak.dilate(sall, 1, diag=True), passes=2)

    # ---- the tiles
    glyphs = letters_of(ak.load_mask(TITLE))
    tiles = []
    for k, ch in enumerate("WORDS"):
        T = tile(cv, glyphs[k], CX[k], FOOT[k], TURN[k], SIDE[k])
        dm = seat_digit(T, SCORE[ch])
        for c_ in T["cols"]:
            T["cols"][c_] &= ~dm
        T["cols"]["black"] = T["cols"].get("black", np.zeros((128, 128), bool)) | dm
        T["digit"] = dm
        tiles.append(T)
    allb = np.zeros((128, 128), bool)
    for T in tiles:
        allb |= T["body"]

    # ---- the tiles' shadows on the board, where each will land: smaller and
    # lighter the higher it hops, thrown right as it rises
    m = board & ~allb
    one = (("felt2", "felt1"), ("felt1", "felt0"), ("felt0", "black"), ("blue", "navy"), ("navy", "black"),
           ("red", "wine"), ("wine", "black"))
    deep = (("felt2", "felt0"), ("felt1", "felt0"), ("blue", "navy"), ("navy", "black"), ("red", "wine"),
            ("wine", "black"))
    for k, T in enumerate(tiles):
        lift = SHADOW_Y[k] - FOOT[k]
        ex = CX[k] + 0.18 * lift
        e = np.hypot((X - ex) / (12.5 - 0.2 * lift), (Y - SHADOW_Y[k]) / (3.7 - 0.05 * lift))
        core = m & (e < 0.8)
        rim = m & (e < 1.0) & ~core & (ak.paint.BAYER < 0.5) & ~grid
        if lift < 20:
            step_down(pic, core, deep)
            pic.put(core & grid, "black")
        else:
            step_down(pic, core, one)
        step_down(pic, rim, one)

    # ---- the title: a black drop shadow on the room, every tile's outline,
    # then back to front each tile's outline (over the one behind) and paint
    drop = np.zeros((128, 128), bool)
    for dx, dy in ((1, 1), (2, 2), (1, 2)):
        drop |= ak.shift(ak.dilate(allb, 1), dx, dy)
    pic.put(drop & room & ~ak.dilate(allb, 1), "black")
    drawn = np.zeros((128, 128), bool)
    for k in ORDER:
        T = tiles[k]
        cast = np.zeros((128, 128), bool)                         # its shadow on the tile behind, to the right
        for dx, dy in ((1, 0), (2, 0), (3, 1), (2, 1), (3, 2)):
            cast |= ak.shift(T["body"], dx, dy)
        step_down(pic, cast & drawn & ~ak.dilate(T["body"], 1),
                  (("cream", "gold1"), ("gold2", "gold1"), ("gold1", "gold0"), ("gold0", "brown")))
        ak.outline(pic, T["body"], "black")
        for c_, mk in T["cols"].items():
            pic.put(mk, c_)
        drawn |= T["body"]

    # ---- the tile flying in: a Z, nearest of all, in the near shade, tumbling
    # down onto the board, cropped by the frame; its shadow on the board
    # below it to the right
    H = HERO
    Z = tile(cv, ak.load_mask(HERO_GLYPH), H["cx"], H["foot"], H["deg"], H["side"], FW=H["fw"], FH=H["fh"],
             TOP=H["top"], tones=H["tones"], gy=3)
    zd = seat_digit(Z, H["score"])
    for c_ in Z["cols"]:
        Z["cols"][c_] &= ~zd
    Z["cols"]["black"] |= zd
    Z["digit"] = zd
    zsh = ak.shift(ak.erode(Z["body"], 2), HERO_SHADOW[0], HERO_SHADOW[1]) & board & ~Z["body"]
    step_down(pic, zsh, deep)
    pic.put(zsh & grid, "black")
    ak.outline(pic, Z["body"], "black")
    for c_, mk in Z["cols"].items():
        pic.put(mk, c_)
    tiles_all = tiles + [Z]

    # ---- clean-up: lone pixels take their neighbours' colour (the letters,
    # digits and the star kept as drawn)
    keep = sall.copy()
    for T in tiles_all:
        keep |= T["letter"] | T["digit"]
    ak.despeckle(pic, need=4, keep=keep, passes=2)

    # ---- the frame: the outer two pixels step down into the dark
    FRAME = (("cream", "gold1"), ("gold2", "gold0"), ("gold1", "gold0"), ("gold0", "brown"),
             ("brown", "black"), ("felt2", "felt0"), ("felt1", "felt0"), ("felt0", "black"), ("blue", "navy"),
             ("navy", "black"), ("red", "wine"), ("wine", "black"))
    ring2 = np.zeros((128, 128), bool)
    ring2[:2, :] = ring2[-2:, :] = ring2[:, :2] = ring2[:, -2:] = True
    ring1 = np.zeros((128, 128), bool)
    ring1[0, :] = ring1[-1, :] = ring1[:, 0] = ring1[:, -1] = True
    step_down(pic, ring2, FRAME)
    step_down(pic, ring1, FRAME)
    ak.despeckle(pic, need=3, keep=keep, passes=1)               # what the frame's step left alone

    # ---- glints: the key catching the top corners of the highest tiles, and
    # the star's arm toward it
    for k, arms in GLINTS:
        ys_, xs_ = np.nonzero(tiles[k]["body"])
        i = int(np.argmin(xs_ + ys_ * 1.3))
        ak.glint(pic, int(xs_[i]), int(ys_[i]), 2, tip="gold1", arms=arms)
    a = np.radians(-90 + 72 * 4)
    gx, gy = cam.project((0.40 * np.cos(a), 0.0, 0.40 * np.sin(a)))
    ak.glint(pic, int(np.floor(gx)) + 1, int(np.floor(gy)), 2, tip="gold1", arms=(2, 1, 2, 1))
    return pic.image()


if __name__ == "__main__":
    import boxart
    boxart.save(draw(), HERE.parent / "docs" / "cart.png")
