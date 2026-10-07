"""docs/cart.png, CHCrossword's cover in the visual menu (docs/cover-art.md).
`chgame boxart` redraws it; edit this, not the PNG.

THE BRIEF (revision 2: the owner swapped the colours, so the title is gold
  like every game's and the jackpot word silver)
  Message: the jackpot word. The pencil has just written the last letter
  and the word pays out: JACKPOT bursts out of the crossword in silver, each
  tile blasted up on its own shaft of light. A crossword you can win big at.

  Composition (a thumbnail in words):
  - The title alone in the top band, on black: CROSSWORD in gold chrome.
  - Focal point, the middle band: the seven JACKPOT tiles in the air in a
    rainbow arc over the board, J low at the left, the crest over C, K and
    P, the T low at the right just off the pencil's point. They grow toward
    the crest (13 to 16 px, as if nearer), so the letters are 9 to 11 px
    serifs that read at 1x. Each is stamped by hand, not rendered: a square
    ice-chrome face turned to us (cream lit edges up and left, a sheen to
    sky in its far corner across a one-row checker seam), two pixels of
    depth under it and one to its right (sky, then navy), a black
    outline, a black serif letter (sky half ink only where it runs).
  - The leap: under the word the row it came from is an empty black trough
    across the board, its far lip white hot in the middle. From it a shaft
    of light rises to each tile (all from one point under the board, so the
    shafts fan out as the tiles did): sky at the trough, navy at their
    edges and toward the tiles, falling off in checker seams. Three small
    sparks rise in them. Each tile also throws its shadow on the row in
    front of the trough, down and right of the point under it (the key is
    up and left): a rounded dark footprint whose dithered edge widens with
    its lift. Black shows between the tiles' feet and the trough: the word
    is off the board.
  - The board: a 13 x 13 crossword in perspective (camera 44 degrees up,
    turned 8), the near rows bigger. Each square is a flat tile cut by
    clean gaps (each edge one pixel per row or column, so the gaps are
    even, straight and evenly stepped), its near edge a level darker; the
    black squares are bare felt. The light pools in front of the trough:
    blank squares ivory1 at most (never brighter than the silver), falling to
    felt1 and felt0 tiles over black squares and gaps, so the black-and-
    white pattern holds into the dark; the felt's falloff in narrow checker
    seams. The board behind the trough is dim felt0 (the shafts burn over
    it). KING, a filled word across the lit row (ivory2 tiles, black
    letters): a crossword being solved, at a casino.
  - The pencil comes in from the bottom right corner, its graphite point
    at the trough's end with a silver spark where it writes; the wood cone
    lit up and left (ivory2 edge, ivory1, wine in shade), a red hexagonal
    body, a wine underside, a short cream gleam, black outline, its shadow
    to the right. It lies over the darker squares, so its wood stands clear.
  - A red casino chip lies in the bottom left corner (cream inserts round
    its rim, a wine ring, a wine and red edge), the foreground's other
    weight and the casino's sign.
  - Sparkle: a big four-pointed glint on the K's corner, small ones on the
    J and the O.
  - Read order: the title, the silver word, the shafts and trough, KING, the
    pencil, the chip. The frame's outer three pixels step down into the
    dark (the pencil through its own reds).

  Palette (11 own + cream, grey, black, red):
    felt0 felt1          the felt (gaps, black squares), the squares out of
                         the light
    ivory1 ivory2        the squares in the light (ivory2 only the filled
                         ones); the pencil's wood
    navy sky ice         the jackpot: its tiles, shafts, sparks and the
                         trough's lip
    wine                 the pencil's underside and its wood in shade, the
                         chip's ring and edge (red their paint)
    gold0 gold1 gold2    the title's own: nothing else uses them
    grey                 the graphite

  Fonts: title.txt (CROSSWORD), CUPID OF PADUA AND HITMEN (bmf collection,
  author and terms not stated: a `?` face, chosen because it is the
  heaviest that sets CROSSWORD in the width at its own size; the clear-terms
  faces that fit are light or small); its W redrawn by hand (the face's
  own W is a U). letters.txt (the tiles' letters): DejaVu Serif Bold, as
  the game's close-up uses it, rasterized at sizes 8 to 15 (J's hook
  redrawn at the small sizes).
"""
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import numpy as np  # noqa: E402
import artkit as ak  # noqa: E402
from artkit import render3d as R  # noqa: E402

TITLE = HERE / "art" / "title.txt"
LETTERS = HERE / "art" / "letters.txt"

# ---- the puzzle ------------------------------------------------------------------------
# 13 x 13, '#' a black square (bare felt), '.' an empty square, a letter a filled one.
GRID = ["....#....#...",
        "....#....#...",
        "..........#..",
        "###...#......",
        "....#....#...",
        ".#.....#.....",
        "...#.#.......",
        "##JACKPOT#...",
        "#.......##...",
        "...#KING#....",
        "..#...#......",
        "...#.#..#....",
        "...#....#...."]
JACKPOT = (7, 2, 7)                       # row, first column, length

# ---- the camera and the light ----------------------------------------------------------------
YAW, ELEV, DIST, FOV = 8.0, 44.0, 12.0, 46.0
TARGET = (-0.5, 0.0, 1.0)
SLOT_AT = (64.0, 82.0)                    # where the K's slot lands on the picture
POOL = (6.0, 8.8, 1.4, 0.8, 1.6)          # the light's pool on the board: centre column, row, half width, falloff near, far
BACK = ([4.0, 5.0, 6.5], [0.0, 0.8, 1.4], 0.10)   # the dim board behind the word: level by row, less per column off centre

# ---- the leap ------------------------------------------------------------------------------------
# each letter's tile in the air: centre x, centre y, face size (px), lift (squares)
FLY = [(10, 63, 13, 1.6), (26, 53, 14, 2.4), (43, 46, 15, 2.9), (61, 43, 16, 3.1),
       (79, 46, 15, 2.9), (96, 53, 14, 2.4), (110, 68, 13, 1.2)]
SUN = (0.30, 0.34)                        # a lifted tile's shadow moves this far (squares) per square of lift
SHEEN = (0.66, 0.76)                      # where a tile's face turns from gold2 to gold1 (0 its top-left corner, 1 its bottom-right)
BEAMS = (60, 108, 30, 0.75)               # the shafts of light: their common source (px), the radius they show from, width (of a tile)
HOT = 2.0                                 # the trough's lip is white hot this far (squares) each side of its middle
MOTES = [(47, 64, (1, 1, 1, 1)), (75, 67, (1, 1, 1, 1)), (33, 71, (1, 1, 1, 1))]   # sparks in the shafts: x, y, arms
# glints: (tile, dx, dy from its face's top-left corner, arms left, right, up, down)
SPARKS = [(3, 0, 0, (5, 5, 3, 5)), (0, 11, 1, (2, 2, 2, 2)), (5, 12, 0, (2, 2, 2, 2))]

# ---- the pencil (drawn on the picture: a tip, an axis, widths along it) -------------------
PEN_TIP = (104.0, 84.0)                   # the lead's point, at the trough's end where the T was written
PEN_DIR = 56.0                            # degrees below the horizontal, toward the bottom right
PEN_LEAD = 5.0                            # px of graphite
PEN_CONE = 16.0                           # px from the point to where the paint starts
PEN_W = 6.6                               # the body's half width where the cone meets it
PEN_GROW = 0.05                           # px of half width gained a px down the body (perspective)
PEN_SCALLOP = 2.5                         # how far the paint's tongues reach into the wood

CHIP = (13, 106, 13, 8.5, 3.5)            # the chip in the foreground: centre, radii, edge (px)

TITLE_Y = 4
TITLE_GLINTS = [(31, 2, (2, 2, 2, 2)), (116, 2, (2, 2, 2, 2))]   # on the first O's shoulder and the D's
TITLE_ROWS = (["gold1"] * 3 + [("gold1", "gold2")] + ["gold2"] * 6 + ["gold0"] * 2 + ["gold1"] * 5
              + [("gold1", "gold2")] + ["gold2"] * 5)

FELT_R = ["black", "felt0", "felt1"]
TILE_R = ["black", "felt0", "felt1", "ivory1", "ivory2", "cream"]
JACK_R = ["black", "navy", "sky", "ice", "cream"]


def camera():
    a, e = math.radians(YAW), math.radians(ELEV)

    def make(shift):
        tx, ty, tz = TARGET
        pos = (tx + DIST * math.cos(e) * math.sin(a), ty + DIST * math.sin(e), tz + DIST * math.cos(e) * math.cos(a))
        return R.Camera(pos, TARGET, fov=FOV, shift=shift)
    c = make((0, 0))
    r0, c0, _ = JACKPOT
    x, y = c.project((c0 + 3 - 6, 0, r0 - 6))
    return make((SLOT_AT[0] - x, SLOT_AT[1] - y))


def board_uv(cam, X, Y, h=0.0):
    """Board coordinates (column, row: 0..13 across the grid) where the rays
    through picture points (X, Y) meet the plane at height h."""
    o, d = cam.rays(np.asarray(X, np.float64).reshape(-1), np.asarray(Y, np.float64).reshape(-1))
    t = (h - o[:, 1]) / d[:, 1]
    p = o + d * t[:, None]
    shp = np.shape(X)
    return (p[:, 0] + 6.5).reshape(shp), (p[:, 2] + 6.5).reshape(shp)


def to_px(cam, u, v, h=0.0):
    return cam.project((u - 6.5, h, v - 6.5))


# ---- letters ---------------------------------------------------------------------------------------

def load_letters():
    out, cur, rows = {}, None, []
    for ln in LETTERS.read_text(encoding="utf-8").splitlines():
        if ln.startswith("//"):
            continue
        if ln.startswith("= "):
            if cur:
                out[cur] = rows
            _, size, ch = ln.split()
            cur, rows = (int(size), ch), []
        elif ln.strip():
            rows.append(ln)
    if cur:
        out[cur] = rows
    return out


def glyph_mask(rows):
    w = max(len(r) for r in rows)
    ink = np.array([[q == "#" for q in r.ljust(w, ".")] for r in rows])
    hm = np.array([[q == "+" for q in r.ljust(w, ".")] for r in rows])
    return ink, hm


def fit_letter(L, ch, face, cx, cy, margin=1, sizes=range(15, 7, -1)):
    """The biggest size of `ch` whose ink lies wholly on `face` `margin`
    pixels in from its edge, as near (cx, cy) as it can: (ink, half) masks."""
    inner = ak.erode(face, margin)
    for size in sizes:
        ink, hm = glyph_mask(L[(size, ch)])
        gh, gw = ink.shape
        for oy, ox in ((0, 0), (0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            x0, y0 = int(round(cx - gw / 2)) + ox, int(round(cy - gh / 2)) + oy
            m = ak.place(ink, x0, y0)
            if (m & ~inner).any():
                continue
            return m, ak.place(hm, x0, y0) & inner
    return None, None


def face_rows(pic, M, rows):
    """The letters' face row by row: a colour, or (a, b) for a seam: a with
    a 50% checker of b where the stroke is 5 px or wider."""
    top = int(np.nonzero(M.any(axis=1))[0].min())
    ck = ak.checker()
    wide = M & (ak.runs(M, 1) >= 5)
    for j, c in enumerate(rows):
        row = np.zeros_like(M)
        row[top + j, :] = True
        row &= M
        if isinstance(c, tuple):
            pic.put(row, c[0])
            pic.put(row & wide & ~ck, c[1])
        else:
            pic.put(row, c)


def pencil_parts(ss=4):
    """The pencil's regions on the picture (masks). The key comes from the
    upper left, so its lower-left side is the lit one."""
    N = 128 * ss
    c = (np.arange(N) + 0.5) / ss
    X, Y = np.meshgrid(c, c)
    a = math.radians(PEN_DIR)
    ux, uy = math.cos(a), math.sin(a)                    # along it, from the point
    vx, vy = uy, -ux                                     # across it, toward its upper right (the side in shade)
    t = (X - PEN_TIP[0]) * ux + (Y - PEN_TIP[1]) * uy
    o = (X - PEN_TIP[0]) * vx + (Y - PEN_TIP[1]) * vy
    w_cone = PEN_W * np.clip(t / PEN_CONE, 0, None) + 0.4
    w_body = PEN_W + np.clip(t - PEN_CONE, 0, None) * PEN_GROW
    w = np.where(t < PEN_CONE, w_cone, w_body)
    s = o / np.maximum(w_body, 1e-6)                     # across the body, -1..1
    inside = (t > -0.3) & (np.abs(o) <= w)
    fac_c = np.array([0.67, 0.0, -0.67])
    fac_h = np.array([0.33, 0.34, 0.33])
    k = np.argmin(np.abs(s[..., None] - fac_c), axis=-1)
    uu = np.clip(np.abs(s - fac_c[k]) / fac_h[k], 0, 1)
    edge_t = PEN_CONE - PEN_SCALLOP * (1 - uu * uu)
    paint = inside & (t >= edge_t)
    wood = inside & ~paint & (t >= PEN_LEAD)
    lead = inside & (t < PEN_LEAD)

    def px(m):
        return m.reshape(128, ss, 128, ss).mean(axis=(1, 3)) >= 0.5
    sw = o / np.maximum(w, 1e-6)
    out = {"all": px(inside), "lead": px(lead), "lead_lit": px(lead & (sw < -0.1) & (t > 0.8))}
    out["wood_lit"] = px(wood & (sw < -0.33))
    out["wood_dark"] = px(wood & (sw > 0.33))
    out["wood_mid"] = px(wood) & ~out["wood_lit"] & ~out["wood_dark"]
    out["lit"] = px(paint & (s < -0.34))
    out["dark"] = px(paint & (s > 0.34))
    out["mid"] = px(paint) & ~out["lit"] & ~out["dark"]
    out["t"] = t.reshape(128, ss, 128, ss).mean(axis=(1, 3))
    out["s"] = s.reshape(128, ss, 128, ss).mean(axis=(1, 3))
    for m in ("lead", "lead_lit", "wood_lit", "wood_mid", "wood_dark", "lit", "mid", "dark"):
        out[m] &= out["all"]
    return out


def gold_tile(pic, L, ch, cx, cy, S):
    """A jackpot tile in the air, facing us: a gold-leaf face S px square
    (cream lit edges up and left, a sheen falling to gold1 in its far
    corner), two pixels of depth under it and one to its right (gold1 then
    gold0), black outline, its letter in black with gold1 half ink."""
    x0, y0 = int(round(cx - S / 2)), int(round(cy - S / 2))
    face = np.zeros((128, 128), bool)
    face[y0:y0 + S, x0:x0 + S] = True
    side = (ak.shift(face, 0, 1) | ak.shift(face, 0, 2) | ak.shift(face, 1, 1) | ak.shift(face, 1, 2)) & ~face
    body = face | side
    pic.put(ak.dilate(body, 1) & ~body, "black")
    pic.put(side, "navy")
    pic.put(side & ak.shift(face, 0, 1) & ~ak.shift(face, -1, 0), "sky")
    yy, xx = np.mgrid[0:128, 0:128]
    t = ((xx - x0) + (yy - y0)) / (2.0 * (S - 1))
    pic.put(face, "ice")
    seam = face & (t > SHEEN[0]) & (t <= SHEEN[1])
    pic.put(seam & ak.checker(), "sky")
    pic.put(face & (t > SHEEN[1]), "sky")
    pic.put(face & ~ak.shift(face, 0, 1), "cream")
    pic.put(face & ~ak.shift(face, 1, 0), "cream")
    ink, hm = fit_letter(L, ch, face, cx, cy, margin=2)
    if ink is not None:
        hm &= ak.nbrs(hm)                                              # half ink only in runs: no lone dots
        pic.put(hm & (t <= SHEEN[0]), "sky")
        pic.put(hm & (t > SHEEN[0]), "navy")
        pic.put(ink, "black")
    return x0, y0, S


def chip_parts(cx, cy, rx, ry, th, ss=4):
    """A casino chip lying on the board, seen from above at the board's
    angle: its face (an ellipse), its edge (th px of it showing under the
    face), the six inserts round its rim (on the face and down the edge),
    the ring inside them. Masks, each pixel by most of its ss x ss samples."""
    N = 128 * ss
    c = (np.arange(N) + 0.5) / ss
    X, Y = np.meshgrid(c, c)
    ex, ey = (X - cx) / rx, (Y - cy) / ry
    rr = np.hypot(ex, ey)
    face = rr <= 1
    edge = np.zeros_like(face)
    for k in range(1, int(th * ss) + 1):
        edge |= np.hypot(ex, (Y - k / ss - cy) / ry) <= 1
    edge &= ~face
    ang = np.degrees(np.arctan2(ey, ex))
    ins = (np.abs(((ang + 15) % 60) - 30) < 10)
    ang_e = np.degrees(np.arctan2(ey * 0, ex))                     # on the edge: by how far round it is
    ex_e = np.clip(ex, -1, 1)
    ang_e = np.degrees(np.arctan2(np.sqrt(1 - ex_e ** 2), ex_e))   # the rim point straight above
    ins_e = np.abs(((ang_e + 15) % 60) - 30) < 10

    def px(m):
        return m.reshape(128, ss, 128, ss).mean(axis=(1, 3)) >= 0.5
    out = {"face": px(face), "edge": px(edge), "ins": px(face & ins & (rr > 0.72)), "ring": px(face & (rr > 0.56) & (rr <= 0.68)),
           "ins_e": px(edge & ins_e), "lit_e": px(edge & (ex < -0.2))}
    out["edge"] &= ~out["face"]
    return out


def draw():
    P = ak.Palette({
        "felt0": "#08301A", "felt1": "#14603A",
        "ivory1": "#BCA682", "ivory2": "#ECDDB6",
        "gold0": "#8C4A0C", "gold1": "#E8A01C", "gold2": "#FFE070",
        "wine": "#5E0C1E",
        "navy": "#1A2A78", "sky": "#4AA0F0", "ice": "#D0F4FF",
    }, ramps=[FELT_R, TILE_R, JACK_R, ["black", "wine", "red", "cream"], ["gold0", "gold1", "gold2", "cream"]])
    cam = camera()
    pic = ak.Picture.blank(P, "black")
    yy, xx = np.mgrid[0:128, 0:128]
    L = load_letters()
    r0, c0, nw = JACKPOT

    # ---- the board, per pixel: its square, and the gaps as clean lines (a
    # column's edge takes the one pixel of each row it crosses, a row's
    # edge the one pixel of each column)
    u, v = board_uv(cam, xx + 0.5, yy + 0.5)
    uL, _ = board_uv(cam, xx + 0.0, yy + 0.5)
    uR, _ = board_uv(cam, xx + 1.0, yy + 0.5)
    _, vT = board_uv(cam, xx + 0.5, yy + 0.0)
    _, vB = board_uv(cam, xx + 0.5, yy + 1.0)
    colgap = np.floor(uL) != np.floor(uR)
    rowgap = np.floor(vT) != np.floor(vB)
    col = np.floor(u).astype(int)
    row = np.floor(v).astype(int)
    on = (col >= 0) & (col < 13) & (row >= 0) & (row < 13)
    cc, rr = np.clip(col, 0, 12), np.clip(row, 0, 12)
    cid = rr * 13 + cc
    black_sq = np.array([[ch == "#" for ch in r] for r in GRID])
    slot = np.zeros((13, 13), bool)
    slot[r0, c0:c0 + nw] = True
    tile = on & ~colgap & ~rowgap & ~black_sq[rr, cc] & ~slot[rr, cc]
    lip = tile & ak.shift(rowgap, 0, -1)                      # the near edge of each tile (its side, in shade)
    top = tile & ~lip

    # the light: a pool in front of the trough, falling off with the
    # distance in squares (dim felt behind the trough), less a vignette at
    # the picture's sides and foot; each square's top one flat level (the
    # filled ones a level up), its near edge a level down, the felt's
    # falloff in narrow checker seams
    def light(uu, vv):
        du = np.maximum(np.abs(uu - POOL[0]) - POOL[2], 0)
        dv = (vv - POOL[1]) * np.where(vv > POOL[1], POOL[3], POOL[4])
        d = np.hypot(du * 1.25, dv)
        pool = np.interp(d, [0, 1.0, 1.8, 2.6, 3.6, 4.8], [3.0, 3.0, 2.5, 2.0, 1.2, 0.2])
        back = np.interp(vv, BACK[0], BACK[1]) - np.abs(uu - POOL[0]) * BACK[2]     # the board behind the word, dim
        return np.maximum(pool, back)

    def vignette(x, y):
        return np.clip((np.abs(x - 63.5) - 44) / 18, 0, 1) * 1.2 + np.clip((y - 112) / 14, 0, 1) * 1.2

    lv_cell = np.zeros((13, 13))
    for r in range(13):
        for c in range(13):
            sx, sy = to_px(cam, c + 0.5, r + 0.5)
            lv_cell[r, c] = light(c + 0.5, r + 0.5) - vignette(sx, sy)
    filled = np.array([[ch.isalpha() for ch in r] for r in GRID])
    tl = np.round(lv_cell)
    tl = np.where(filled & (tl >= 3), 4, tl)
    tlev = tl[rr, cc].astype(float)
    flev = ak.terrace(np.clip(light(u, v) - vignette(xx, yy) - 2.0, 0, 2), 0.35)

    # the lifted tiles' shadows on the board: under each, moved away from
    # the key with its lift; a rounded footprint two levels down, its edge
    # one level down and wider the higher the tile is
    fly_g = []
    for cx, cy, S, h in FLY:
        gu, gv = board_uv(cam, np.array([cx + 0.5]), np.array([cy + 0.5]), h)
        fly_g.append((float(gu[0]), float(gv[0])))
    shadow = np.zeros((128, 128))
    for (gu, gv), (cx, cy, S, h) in zip(fly_g, FLY):
        su, sv = gu + SUN[0] * h, gv + SUN[1] * h
        d = (np.abs(u - su) ** 4 + np.abs(v - sv) ** 4) ** 0.25          # a rounded square
        core = d < 0.27 - 0.02 * h
        pen_ = (d < 0.27 + 0.06 * h) & ~core
        shadow = np.maximum(shadow, np.where(core, 2.0, np.where(pen_, 1.0, 0.0)))
    shadow *= on
    t_lv = tlev - shadow
    lip_lv = np.where(tlev >= 4, 3, np.where(tlev >= 3, 2, tlev - 1)) - shadow
    f_lv = flev - shadow
    ak.by_level(pic, t_lv, TILE_R, top)
    ak.by_level(pic, lip_lv, TILE_R, lip)
    felt = on & ~tile
    ak.by_level(pic, f_lv, FELT_R, felt, q=2)
    # the row the word left: a black trough, its far lip lit by the shafts
    trough = on & (u >= c0) & (u < c0 + nw) & ((row == r0) | (rowgap & (np.floor(vB) == r0)))
    pic.put(trough, "black")
    lipline = trough & rowgap & (np.floor(vB) == r0)                    # its far edge: sky,
    pic.put(lipline, "sky")                                            # white hot in the middle
    pic.put(lipline & (np.abs(u - (c0 + nw / 2)) < HOT), "ice")

    # ---- the letters already in: black on their squares
    for r, line in enumerate(GRID):
        for c, ch in enumerate(line):
            if not ch.isalpha() or slot[r, c]:
                continue
            face = top & (cid == r * 13 + c)
            if face.sum() < 20:
                continue
            ys_, xs_ = np.nonzero(face)
            ink, hm = fit_letter(L, ch, face, xs_.mean() + 0.5, ys_.mean() + 0.5, margin=1)
            if ink is not None:
                pic.put(hm, "ivory1")
                pic.put(ink, "black")

    ak.despeckle(pic, need=4, passes=2, within=on)                       # lone pixels on the board take their neighbours'

    # ---- the beams: a shaft of light from the trough up to each tile (all
    # from one point under the board, so they fan out as the tiles do),
    # sky at the trough fading to navy and into the dark under the tile
    bx, by, rin, width = BEAMS
    sx_, sy_ = (xx + 0.5 - bx) * 0.85, yy + 0.5 - by
    ang = np.arctan2(sy_, sx_)
    rad = np.hypot(sx_, sy_)
    behind = on & (row < r0)
    bg = pic.where("black", "felt0", "felt1") & (behind | ~on)
    beam_lv = np.zeros((128, 128))
    for cx, cy, S, h in FLY:
        tx_, ty_ = (cx - bx) * 0.85, cy + S / 2 - by
        a_k, r_k = math.atan2(ty_, tx_), math.hypot(tx_, ty_)
        half = math.atan2(width * S / 2, r_k)
        da = np.abs((ang - a_k + math.pi) % (2 * math.pi) - math.pi) / half      # 0 on its axis, 1 at its edge
        along = np.clip((rad - rin) / max(r_k - rin, 1), 0, 1)                    # 0 at the trough, 1 at the tile
        lv = np.interp(along, [0, 0.45, 0.6, 0.85, 1.0], [2.0, 2.0, 1.5, 1.0, 0.6]) - np.clip(da - 0.4, 0, None) * 2.5
        beam_lv = np.maximum(beam_lv, np.where((da < 1) & (rad >= rin) & (rad <= r_k + 2), lv, 0))
    ak.by_level(pic, ak.terrace(beam_lv, 0.3), ["black", "navy", "sky"], bg & (beam_lv > 0), q=2)

    # ---- the flying tiles, the far ones first
    order = sorted(range(len(FLY)), key=lambda k: FLY[k][2])
    faces = {}
    for k in order:
        cx, cy, S, h = FLY[k]
        faces[k] = gold_tile(pic, L, "JACKPOT"[k], cx, cy, S)
    for k, dx, dy, arms in SPARKS:
        x0, y0, S = faces[k]
        ak.glint(pic, x0 + dx, y0 + dy, arms=arms, tip="ice")
    for x, y, arms in MOTES:                                             # sparks rising in the shafts
        ak.glint(pic, x, y, arms=arms, core="ice" if max(arms) < 2 else "cream", tip="ice")

    # ---- a chip in the foreground, lying on the board's near corner: red,
    # cream inserts round its rim, a wine ring inside them and a wine edge
    # (red where it faces the key), black outline, its shadow down right
    cx_, cy_, crx, cry, cth = CHIP
    ch_ = chip_parts(cx_, cy_, crx, cry, cth)
    body = ch_["face"] | ch_["edge"]
    csh = (ak.shift(body, 2, 1) | ak.shift(body, 3, 2)) & ~body
    pic.put(csh & pic.where("ivory1", "ivory2"), "felt1")
    pic.put(csh & pic.where("felt1", "felt0"), "black")
    pic.put(ch_["edge"], "wine")
    pic.put(ch_["edge"] & ch_["lit_e"], "red")
    pic.put(ch_["edge"] & ch_["ins_e"], "ivory1")
    pic.put(ch_["face"], "red")
    pic.put(ch_["ring"], "wine")
    pic.put(ch_["ins"], "cream")
    pic.put(ak.dilate(body, 1) & ~body, "black")

    # ---- the pencil
    pen = pencil_parts()
    pen_all = pen["all"]
    psh = (ak.shift(pen_all, 2, 0) | ak.shift(pen_all, 3, 1) | ak.shift(pen_all, 1, 0)) & ~pen_all & on
    pic.put(psh & (pic.where("ivory1", "ivory2")), "felt1")
    pic.put(psh & (pic.where("felt1")), "felt0")
    pic.put(pen["lit"], "red")
    pic.put(pen["mid"], "red")
    pic.put(pen["dark"], "wine")
    gl = pen["lit"] & (np.abs(pen["s"] + 0.62) < 0.12) & (pen["t"] > PEN_CONE + 1.5) & (pen["t"] < PEN_CONE + 13)
    pic.put(gl, "cream")
    pic.put(pen["wood_lit"], "ivory2")
    pic.put(pen["wood_mid"], "ivory1")
    pic.put(pen["wood_dark"], "wine")
    pic.put(pen["lead"], "black")
    pic.put(pen["lead_lit"], "grey")
    pic.put(ak.dilate(pen_all, 1) & ~pen_all, "black")
    ak.glint(pic, int(PEN_TIP[0]) - 1, int(PEN_TIP[1]) - 1, arms=(2, 1, 2, 1), tip="ice")   # the point, writing

    # ---- the title: gold chrome (a sky that pales to the horizon, a hard
    # dark horizon, the ground below paling again), cream and gold0 bevel,
    # gold0 depth, black outline and shadow
    tm = ak.load_mask(TITLE)
    tx, ty = ak.centred_x(tm), TITLE_Y
    M = ak.place(tm, tx, ty)
    acc = M.copy()
    layers = []
    for k in (1, 2):
        Lk = ak.shift(M, k, k) & ~acc
        layers.append(Lk)
        acc |= Lk
    O = ak.dilate(acc, 1, diag=True) & ~acc
    S_ = (ak.shift(acc | O, 1, 1) | ak.shift(acc | O, 0, 1)) & ~(acc | O)
    pic.put(S_, "black")
    pic.put(O, "black")
    holes = ~ak.outside_of(M) & ~M
    for Lk in layers:
        pic.put(Lk, "gold0")
        pic.put(Lk & holes, "black")
    face_rows(pic, M, TITLE_ROWS)
    ak.bevel_runs(pic, M, "cream", "gold0")
    nb = sum(ak.shift(acc, dx, dy).astype(int) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
    for _ in range(2):                                             # pinholes of outline shut in the depth
        blk = pic.where("black")
        lone = blk & O & ~ak.shift(blk, 0, 1) & ~ak.shift(blk, 0, -1) & ak.shift(acc, 1, 0) & ak.shift(acc, -1, 0)
        alone = blk & ~ak.nbrs(blk) & (acc | O)
        pic.put((blk & O & ((nb >= 3) | lone)) | alone, "gold0")
    for gx, gy, arms in TITLE_GLINTS:
        ak.glint(pic, tx + gx, ty + gy, arms=arms)

    # ---- the frame: the outer pixels step down into the dark, so the
    # menu's border frames the picture (the pencil through its own reds)
    down = {"cream": "ivory2", "ivory2": "ivory1", "ivory1": "felt1", "felt1": "felt0", "felt0": "black",
            "ice": "sky", "sky": "navy", "navy": "black", "red": "wine", "wine": "black",
            "grey": "felt0", "gold2": "gold1", "gold1": "gold0", "gold0": "black"}
    pdown = dict(down, cream="red", ivory1="wine", ivory2="ivory1")
    ring = np.minimum(np.minimum(xx, 127 - xx), np.minimum(yy, 127 - yy))
    for steps, m in ((3, ring == 0), (2, ring == 1), (1, ring == 2)):
        for _ in range(steps):
            idx = pic.idx.copy()
            for mp, where in ((down, ~pen_all), (pdown, pen_all)):
                for k_, v_ in mp.items():
                    pic.idx[m & where & (idx == pic.pal[k_])] = pic.pal[v_]
    return pic.image()


if __name__ == "__main__":
    import boxart
    boxart.save(draw(), HERE.parent / "docs" / "cart.png")
