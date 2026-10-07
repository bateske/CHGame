"""docs/cart.png, Solitaire's picture in the visual menu (docs/cover-art.md).
`chgame boxart` redraws it; edit this, not the PNG.

THE BRIEF (revision 3)
  Message: you won. The last king has gone up and the pack is bouncing off
  the foundations, leaving its trail across the felt: the Windows victory
  cascade, and the King of Hearts himself springing out of it at us off
  its bounce, grinning, sword thrust high.

  Composition (a loop: title, king, sword, the piles, down the trail's V,
  back up to the king; trail and king together make a check mark):
  - Focal point: the King of Hearts, a big card (42 x 58) on the left, tilted
    14 degrees (its top leaning left, into his leap: an even 1-in-4 step on
    its edges), the only cream card and the brightest, most contrasty shape
    under the title. He is a cartoon, not a print: built from rounded parts
    in the card's own frame (his head upright: only the card leans). A crown
    breaking out over the card's top edge, pearls on its points; shining
    black pie eyes on us, brows up, a bulb nose with a shine, a white
    handlebar moustache over a wide-open grin (teeth, tongue), a beard, an
    ermine collar, stripe and hem; a red robe lit on its left, one narrow
    seam to wine on its right, tapering folds, a gold (amber) braid on the
    hem; a heart medallion. His left arm bursts out of the card's right edge
    in a red sleeve with an ermine cuff and thrusts the sword up and out:
    a broad blade (a cream lit edge, ivory, a grey shaded edge), an amber
    guard, a star glint at the tip. His index (K and heart) sits upright in
    the corner, crisp. He is the trail's newest copy: the trail runs in
    behind his card, his shadow darkening it there (a dark gap that lifts
    him off it), and his shadow on the felt below and right of him.
  - The trail (middle ground, the right half): the iconic image, a V. The
    card left the hearts pile (it comes out from under the piles), fell to
    the left, bounced on the felt in the pool of light (a contact shadow
    under it) and rose up and in behind the king, who springs on out of it.
    Each copy is stamped over the last as the game does, so each shows only
    a strip: the top strip with its K and heart on the fall, the bottom strip
    with its turned index on the rise. The copies swell (0.24 to 0.35 of the
    hero) as they come nearer, 4.5 to 9 px apart (no screen door). The
    oldest third is grey with felt edges (far, gone by), the rest ivory faces
    with grey edges inside the ribbon, black only round its silhouette; an
    index is drawn only where it shows whole. The ribbon casts a short
    shadow on the felt.
  - Background: the four foundations in a row under the title, small, dim
    and far: grey cards (a black or wine K and suit, a lit top edge) over two
    stacked edges, the deeper dimmer; the hearts pile shows its queen (the
    king has left it).
  - Light: the house key from the top left. One lit table: a pool of light
    lies on the felt round the bounce, an ellipse in perspective, terraced
    felt3 > felt2 > felt1 > felt0 > black with narrow seams along it; the
    felt sinks to black toward the title and at every edge, the edge's seams
    wandering (no straight dotted rows along the frame). Nothing that
    matters under the install bar (only the hero card's corner reaches it).
  - Title: SOLITAIRE across the top band (y 4-37), alone in gold: gold leaf
    banded light, a gold0 horizon (one row in the S, kept off its bevel),
    light again; a bevel on the outer contour (cream / gold0), a red then
    wine extrusion, black outline and shadow, drawn letter by letter from
    the left so each letter's outline cuts the extrusion of the one before;
    the notches between letters closed in black; a calm glow of felt hugging
    the closed footprint (felt1 then felt0, no dots). Star glints on the
    outer corners of the S's cap and the A's apex, their arms out over the
    outline.

  Palette (11 own + cream, grey, black, red):
    felt0 felt1 felt2 felt3  the baize, hue-shifted: teal-black shadow to a
                             warm green at the pool's heart, with black below
    ivory                    the copies' faces, the beard's and ermine's mid
                             tone, the blade, the hero card's shade side
    wine                     the reds' shadow: the robe's shade, far
                             indices, the crown's underside, the title's depth
    peach amber              the king's skin, his crown, the robe's braid,
                             the sword's guard (amber is the king's gold, so
                             the title's golds stay the title's own)
    gold0 gold1 gold2        the title's own: nothing else uses them
    cream (the hero card, highlights, glints), grey (the far copies and
    piles, the blade, edges inside the ribbon), red (the hearts, robe,
    indices), black (outlines, the void).

  Font: BAZAR, from the bmf collection (tools/art/title.txt; author and
  terms not stated: a `?` face, chosen because no clear-terms face sets
  SOLITAIRE this heavy (5 px stems, room for a bevel and extrusion) and
  this tall in 120 px). Five rows of its straight lower stems taken out by
  hand (35 -> 30 px tall). The small K, Q, indices and suit glyphs are
  drawn by hand here.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import numpy as np  # noqa: E402
import artkit as ak  # noqa: E402

TITLE = HERE / "art" / "title.txt"

COL = {
    "felt0": "#03161A", "felt1": "#0A4428", "felt2": "#1E7C3A", "felt3": "#56A040",
    "ivory": "#CDBE9C",
    "wine": "#6A0A1E", "peach": "#F6BA80", "amber": "#D2741A",
    "gold0": "#8E4808", "gold1": "#F2B21E", "gold2": "#FFEE8A",
}
FELT_R = ["black", "felt0", "felt1", "felt2", "felt3"]
TITLE_Y = 4
SS = 4                                  # samples a pixel, for the hero's parts

# ---- the hero card: where it is and how it leans
CARD_C = (31.0, 80.0)                   # its centre on the picture
CW, CH = 42, 58                         # its size
TILT = 14.0                             # degrees, its top leaning left
HEAD = (21.0, 19.0)                     # the head's anchor in the card's frame (the head stays upright)
HERO_SHADOW = (5, 9)                    # its shadow's offset on the felt
HERO_ON_TRAIL = (3, 2)                  # and on the trail just behind it
SWORD = dict(angle=37.0, length=20.5)   # the blade's lean in the card's frame, its length

# ---- the foundations and the trail
FOUND = ((66, 80, 94, 108), 43, 11, 15)     # the foundations: x of each (s d c h), y, w, h
S0, S1 = 0.24, 0.40                     # the oldest and newest copy's scale (of the hero)
LAUNCH = (-1.55, 0.6)                   # its speed off the pile (px a tick, at S0)
GRAV, BOUNCE_E = 0.22, 0.70             # gravity; the speed a bounce keeps
FLOOR = 104                             # where the copies' feet bounce
TICKS = 60                              # ticks over which the copies grow to S1
END_X = 40.0                            # after its bounce the trail rises to here, behind the king
STAMP = (2.0, 4.5, 9.0)                 # a copy each 2 ticks (the game stamps every tick), but 4.5 to 9 px apart
AGE_DIM = 0.3                           # the oldest part of the trail, grey and dim
POOL = (78, 96, 62, 34)                 # the key light's pool on the felt: centre, radii
EDGE = (12.0, 2.0, 7.0)                 # the vignette: its width, depth, and how much its seams wander
CONTACT = (9.0, 2.2, 1.0)               # the bounce's contact shadow: radii, depth
NAP = 0.06                              # the cloth's nap: how much it stirs the pool's edge
TRIM = (50.6, 2.6)                      # the robe's gold braid above the hem: from v, how deep
SHADE = {"cream": "ivory", "ivory": "grey", "grey": "felt1", "red": "wine", "wine": "black", "felt1": "felt0"}
TITLE_ROWS = ["gold2"] * 9 + ["gold1"] * 5 + ["gold0"] * 2 + ["gold1"] * 8 + ["gold2"] * 6
HORIZON = (14, 15)                      # the horizon's rows in the lettering
GLINTS = ((13, 4, (2, 1, 2, 1)), (78, 4, (1, 2, 2, 1)))    # star glints on the outer corners of the S's cap and the A's apex
KEY = {"k": "black", "w": "cream", "i": "ivory", "g": "grey", "r": "red", "m": "wine",
       "p": "peach", "a": "amber", "1": "felt1", "0": "felt0"}

GLYPH_K = ["##.##", "##.##", "####.", "###..", "####.", "##.##", "##.##"]
GLYPH_H = [".#.#.", "#####", "#####", ".###.", "..#.."]
GLYPH_K3 = ["#.#", "#.#", "##.", "#.#", "#.#"]
GLYPH_Q3 = [".#.", "#.#", "#.#", "#.#", ".##"]
HEART3 = ["#.#", "###", ".#."]
SUITS = {   # 7 x 7 suit symbols for the foundations
    "s": ["...#...", "..###..", ".#####.", "#######", "#######", "..#.#..", ".#####."],
    "h": [".##.##.", "#######", "#######", "#######", ".#####.", "..###..", "...#..."],
    "d": ["...#...", "..###..", ".#####.", "#######", ".#####.", "..###..", "...#..."],
    "c": ["..###..", "..###..", "##.#.##", "#######", "###.###", "...#...", "..###.."],
}
MEDALLION = ["..kk...kk..", ".kaak.kpak.", "kaappkpppak", "kaapppppaak", "kmaapppaamk",
             ".kmaaaaamk.", "..kmaaamk..", "...kmamk...", "....kmk....", ".....k....."]
EYE = [".kkk.", "kwwkk", "kwkkk", "kkkkk", "kkkkk", ".kkk."]       # pie eyes, a shine top left
BROW_L = ["..kkk", ".k...", "k...."]                              # raised, arched out
BROW_R = ["kkk..", "...k.", "....k"]


def mask_of(rows, ch="#"):
    return np.array([[c == ch for c in r] for r in rows], bool)


def blur(m, n=2):
    k = np.array([1, 4, 6, 4, 1], float) / 16
    b = m.astype(float)
    for _ in range(n):
        b = np.apply_along_axis(lambda v: np.convolve(v, k, "same"), 1, b)
        b = np.apply_along_axis(lambda v: np.convolve(v, k, "same"), 0, b)
    return b


def rounded(x, y, w, h):
    """A card's silhouette: a rectangle with its corner pixels cut."""
    m = np.zeros((128, 128), bool)
    m[max(0, y):max(0, min(128, y + h)), max(0, x):max(0, min(128, x + w))] = True
    for cx, cy in ((x, y), (x + w - 1, y), (x, y + h - 1), (x + w - 1, y + h - 1)):
        if 0 <= cx < 128 and 0 <= cy < 128:
            m[cy, cx] = False
    return m


# ---- the hero's frames: the card's own coordinates, and the upright head's ------------

_T = np.radians(TILT)
_C, _S = np.cos(_T), np.sin(_T)


def to_local(X, Y):
    dx, dy = X - CARD_C[0], Y - CARD_C[1]
    return dx * _C - dy * _S + CW / 2, dx * _S + dy * _C + CH / 2


def to_screen(u, v):
    du, dv = u - CW / 2, v - CH / 2
    return du * _C + dv * _S + CARD_C[0], -du * _S + dv * _C + CARD_C[1]


def to_head(X, Y):
    """The head's frame: the card's units, upright, its anchor on HEAD."""
    hx, hy = to_screen(*HEAD)
    return X - hx + HEAD[0], Y - hy + HEAD[1]


def head_screen(u, v):
    hx, hy = to_screen(*HEAD)
    return u - HEAD[0] + hx, v - HEAD[1] + hy


def sword_geom():
    a = np.radians(SWORD["angle"])
    d = np.array([np.sin(a), -np.cos(a)])            # up the blade
    p = np.array([-d[1], d[0]])                      # across it
    fist = np.array([44.0, 21.0])
    guard = fist + d * 3.6
    tip = guard + d * SWORD["length"]
    return fist, guard, tip, d, p


def head_parts(P):
    """The king's head, upright (he is alive; only his card leans): crown,
    hair, face, nose, moustache, open grin, beard. [(label, field)], front
    to back."""
    E, Cc, B = ak.ellipse, ak.circle, ak.box
    face = E(P, 21.0, 19.8, 8.8, 8.4)
    nose = Cc(P, 21.0, 23.0, 2.9)
    mous = ak.union(E(P, 16.0, 25.9, 5.4, 2.1, angle=16), E(P, 26.0, 25.9, 5.4, 2.1, angle=-16),
                    Cc(P, 10.6, 24.0, 1.6), Cc(P, 31.4, 24.0, 1.6))
    mouth = ak.inter(E(P, 21.0, 27.4, 5.8, 5.4), ak.halfplane(P, 21.0, 26.8, 0.0, -1.0))
    teeth = ak.inter(mouth, ak.halfplane(P, 21.0, 28.3, 0.0, 1.0))
    tongue = ak.inter(mouth, Cc(P, 21.0, 33.0, 3.4))
    beard = ak.smin(E(P, 21.0, 29.6, 11.0, 7.4), ak.polygon(P, [(12.0, 31.0), (30.0, 31.0), (21.0, 40.0)]), 2.0)
    hair = ak.union(E(P, 11.4, 20.0, 3.2, 5.0), E(P, 30.6, 20.0, 3.2, 5.0))
    crown = ak.polygon(P, [(11.2, 10.0), (10.4, 0.4), (16.0, 4.6), (21.0, -4.0), (26.0, 4.6), (31.6, 0.4),
                           (30.8, 10.0)])
    band = B(P, 21.0, 9.8, 10.6, 2.0, r=0.8)
    balls = ak.union(Cc(P, 10.4, -0.6, 2.2), Cc(P, 21.0, -4.6, 2.3), Cc(P, 31.6, -0.6, 2.2))
    return [("T", teeth), ("Q", tongue), ("M", mouth), ("N", nose), ("U", mous), ("W", beard), ("F", face),
            ("Z", hair), ("J", balls), ("B", band), ("C", crown)]


def body_parts(P):
    """The king's body and sword arm and his card, in the card's frame (u
    across 0..42, v down 0..58; the arm breaks out of it), front to back."""
    E, Cc, B, G = ak.ellipse, ak.circle, ak.box, ak.segment
    collar = E(P, 21.0, 35.4, 13.6, 3.4)
    stripe = B(P, 21.0, 45.6, 2.4, 9.6)
    hem = B(P, 21.0, 54.2, 16.0, 1.6, r=0.6)
    robe = B(P, 21.0, 46.0, 16.0, 10.6, r=4.0)
    fist, guard, tip, d, p = sword_geom()
    sleeve = ak.polyline(P, [(31.0, 38.5), (39.5, 32.5), (43.0, 26.5)], r=3.8, r1=2.9)
    cuff = G(P, 42.8, 27.0, 43.6, 24.4, 3.2)
    hand = E(P, fist[0], fist[1], 3.0, 3.2)
    gd = G(P, *(guard - p * 5.0), *(guard + p * 5.0), 1.3)
    b0 = guard + d * 0.8
    nt = tip - d * 3.5
    blade = ak.polygon(P, [tuple(b0 - p * 2.6), tuple(nt - p * 2.4), tuple(tip), tuple(nt + p * 2.4),
                           tuple(b0 + p * 2.6)])
    pommel = Cc(P, *(fist - d * 3.9), 1.5)
    card = B(P, CW / 2, CH / 2, CW / 2, CH / 2, r=2.6)
    return [("P", pommel), ("H", hand), ("G", gd), ("S", blade), ("c", cuff), ("E", ak.union(collar, stripe, hem)),
            ("A", sleeve), ("R", robe), ("K", card)]


ORDER = "TQMNUWFZJBCPHGScEARK"          # every part, front to back


def hero_labels():
    """The hero's part map at pixel size: each pixel takes the part most of
    its samples fall in (front parts first), or '.' when most fall outside."""
    c = (np.arange(128 * SS) + 0.5) / SS
    X, Y = np.meshgrid(c, c)
    parts = head_parts(to_head(X, Y)) + body_parts(to_local(X, Y))
    names = [n for n, _ in parts]
    lab = np.full(X.shape, -1, np.int16)
    for k, (_, d) in enumerate(parts):
        lab[(d < 0) & (lab < 0)] = k
    cnt = np.zeros((len(parts) + 1, 128, 128), np.int16)
    blk = lab.reshape(128, SS, 128, SS)
    for k in range(-1, len(parts)):
        cnt[k + 1] = (blk == k).sum(axis=(1, 3))
    best = cnt[1:].argmax(0)
    inside = cnt[0] < SS * SS / 2
    out = np.full((128, 128), ".", "<U1")
    out[inside] = np.array(names)[best[inside]]
    return out


def glyph_on_card(rows, u0, v0, flip=False):
    """A glyph laid on the tilted card upright, where its middle lands: a
    small index stays crisp (a shear at this lean breaks its 2-px stems)."""
    m = mask_of(rows)
    if flip:
        m = m[::-1, ::-1]
    h, w = m.shape
    x, y = to_screen(u0 + w / 2, v0 + h / 2)
    return ak.place(m, int(round(x - w / 2)), int(round(y - h / 2)))


DOME = {"F": "FNMTQ", "W": "WU", "U": "U", "Z": "Z", "R": "RAE", "A": "A", "C": "CBJ", "B": "CBJ", "J": "J",
        "E": "E", "c": "c", "H": "H", "G": "G", "N": "N", "P": "P"}
PART_RAMP = {                    # part -> its colours by light, dark to light
    "C": ["wine", "amber", "amber", "peach"],
    "B": ["wine", "amber", "amber", "peach"],
    "J": ["amber", "peach", "cream", "cream"],
    "F": ["amber", "peach", "peach", "peach"],
    "N": ["amber", "peach", "peach", "cream"],
    "W": ["grey", "ivory", "cream", "cream"],
    "U": ["grey", "ivory", "cream", "cream"],
    "Z": ["grey", "ivory", "cream", "cream"],
    "E": ["ivory", "ivory", "cream", "cream"],
    "c": ["ivory", "ivory", "cream", "cream"],
    "H": ["amber", "peach", "peach", "peach"],
    "G": ["wine", "amber", "peach", "peach"],
    "P": ["wine", "amber", "peach", "peach"],
    "M": ["black"] * 4, "T": ["cream"] * 4, "Q": ["red"] * 4,
}
SHADE_LINE = {                   # a part's colour where a nearer part sits on it (its shadow side)
    "W": "grey", "Z": "grey", "E": "ivory", "R": "black", "A": "black",
    "C": "wine", "B": "wine", "H": "wine", "G": "wine", "c": "ivory",
}


def light_level(m, L=(-0.6, -0.7, 0.55), soft=2, k=3.0):
    """0..1: how lit each pixel of a shape is, lit as a dome from the key."""
    L = np.array(L) / np.linalg.norm(L)
    B = blur(m, soft)
    gy, gx = np.gradient(B)
    n = np.stack([-gx * k, -gy * k, np.full(B.shape, 0.6)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return np.clip(n @ L, 0, 1)


def hero(pic, yy, xx):
    """The King of Hearts on his tilted card, lit and outlined. Returns the
    part map."""
    lab = hero_labels()
    card = lab == "K"
    fig = (lab != ".") & ~card
    whole = lab != "."                              # the card and everything breaking out of it
    # the card: cream, falling to ivory toward the lower right
    U, V = to_local(xx + 0.5, yy + 0.5)
    pic.put(card, "cream")
    shade = (U / CW) * 0.5 + (V / CH) * 0.7
    pic.put(card & (shade > 0.98) & ak.checker(), "ivory")
    pic.put(card & (shade > 1.08), "ivory")
    # indices
    idx = np.zeros((128, 128), bool)                # only where one shows whole, clear of the figure
    for rows, u0, v0, flip in ((GLYPH_K, 1.6, 2.4, False), (GLYPH_H, 1.6, 10.6, False),
                               (GLYPH_K, CW - 6.6, CH - 9.4, True), (GLYPH_H, CW - 6.6, CH - 16.6, True)):
        g = glyph_on_card(rows, u0, v0, flip)
        if not (ak.dilate(g, 1, diag=True) & ~card).any() and not (ak.dilate(g, 2, diag=True) & fig).any():
            idx |= g
    pic.put(idx, "red")
    # the figure: each part lit as a dome from the key, flat steps of its ramp
    for p, ramp in PART_RAMP.items():
        pm = lab == p
        if not pm.any():
            continue
        dm = np.isin(lab, list(DOME.get(p, p)))
        q = np.clip((light_level(dm) * 4).astype(int), 0, 3)
        for k in range(4):
            pic.put(pm & (q == k), ramp[k])
    # the robe: red lit on the left, one narrow seam to wine on its shaded
    # right, black only deep in the corner under the arm
    R_ = lab == "R"
    lv = 2.0 - np.clip((U - 27.5) / 2.5, 0, 1) - np.clip((U - 33.0) / 3.0 + (V - 50.0) / 4.0, 0, 1) * 0.8
    ak.by_level(pic, ak.terrace(lv, 0.25), ["black", "wine", "red"], R_, q=2)
    # the sleeve: lit on its upper side, wine underneath
    A_ = lab == "A"
    lv = light_level(np.isin(lab, list(DOME["A"])), soft=2, k=4.0) * 2.4
    ak.by_level(pic, ak.terrace(np.clip(lv, 1, 2), 0.25), ["black", "wine", "red"], A_, q=2)
    # folds: tapering strokes falling from the collar, wine in the light, black in the shade
    for (u0, v0), (u1, v1), col in (((9.5, 41.0), (8.6, 50.5), "wine"), ((14.0, 41.5), (14.6, 48.0), "wine"),
                                    ((29.5, 43.0), (30.4, 53.0), "black"), ((34.0, 47.0), (34.6, 52.5), "black")):
        ak.ink(pic, [to_screen(u0, v0), to_screen(u1, v1)], col, where=R_ & ~ak.nbrs(~R_, diag=True))
    if TRIM:
        # gold braid: down both sides of the ermine stripe and round the hem
        # (amber in the light, wine where the robe turns from it)
        E_ = (lab == "E") & (V > 38.5)
        braid = R_ & (ak.shift(E_, 1, 0) | ak.shift(E_, -1, 0) | ak.shift(E_, 0, -1))
        braid |= R_ & (V >= TRIM[0]) & (V < TRIM[0] + TRIM[1])
        pic.put(braid, "amber")
        pic.put(braid & (U > 30.0) & ak.checker(), "wine")
        pic.put(braid & (U > 33.0), "wine")
    # the blade: a cream lit edge, an ivory middle, its shaded edge grey
    S = lab == "S"
    pic.put(S, "ivory")
    pic.put(S & (~ak.shift(S, -1, 0) | ~ak.shift(S, 0, -1)), "grey")
    pic.put(S & (~ak.shift(S, 1, 0) | ~ak.shift(S, 0, 1)), "cream")
    # outlines: black round the whole figure and the card
    pic.put(ak.dilate(whole, 1) & ~whole, "black")
    pic.put(card & ~ak.erode(whole, 1), "black")
    pic.put(ak.dilate(fig, 1) & card, "black")
    # the card's thickness on the shadow side: an ivory inner edge, right and bottom
    edge = card & ~ak.erode(whole, 1)
    inner = card & ~edge & ~ak.dilate(fig, 1) & ak.nbrs(edge, diag=True)
    pic.put(inner & ((U > CW - 3.0) | (V > CH - 3.0)), "ivory")
    # a nearer part's shadow line on the part behind it (below and right of it)
    rank = {n: i for i, n in enumerate(ORDER)}
    for p, col in SHADE_LINE.items():
        pm = lab == p
        for q in ORDER:
            if rank[q] >= rank[p] or q == "K":
                continue
            Q = lab == q
            pic.put(pm & (ak.shift(Q, 0, 1) | ak.shift(Q, 1, 0)), col)
    # the face: an amber line inside it wherever the white hair, moustache and beard meet it
    face = lab == "F"
    whites = np.isin(lab, list("WUZ"))
    pic.put(face & (ak.shift(whites, 1, 0) | ak.shift(whites, -1, 0) | ak.shift(whites, 0, 1) | ak.shift(whites, 0, -1)), "amber")
    nose = lab == "N"
    pic.put(nose & ~ak.shift(nose, 0, -1), "amber")
    pic.put(nose & ~ak.shift(nose, -1, 0) & (yy > np.nonzero(nose.any(axis=1))[0].mean()), "amber")
    # inside the mouth: a black line round it
    mouth = np.isin(lab, list("MTQ"))
    pic.put(ak.dilate(mouth, 1) & ~mouth & np.isin(lab, list("WUFN")), "black")

    # hand-placed detail
    def stamp(x, y, rows):
        ak.patch(pic, int(round(x)) - len(rows[0]) // 2, int(round(y)) - len(rows) // 2, rows, KEY)
    stamp(*head_screen(17.0, 18.6), EYE)
    stamp(*head_screen(25.4, 18.6), EYE)
    stamp(*head_screen(16.4, 13.6), BROW_L)
    stamp(*head_screen(25.6, 13.6), BROW_R)
    stamp(*head_screen(20.0, 22.0), ["w"])         # the nose's shine
    stamp(*to_screen(21.0, 44.0), MEDALLION)
    for u, v in ((21.0, 38.5), (21.5, 49.0), (20.5, 52.0), (12.0, 54.0), (17.0, 54.0), (26.0, 54.0),
                 (31.0, 54.0), (11.5, 35.0), (16.0, 36.6), (26.5, 36.6), (31.0, 35.0)):
        x, y = to_screen(u, v)
        x, y = int(round(x)), int(round(y))
        for t in (0, 1):
            if lab[y + t, x] == "E":
                pic.px(x, y + t, "black")
    for u, v, rows in ((15.6, 9.8, ["rr", "mr"]), (21.0, 9.8, ["rw", "rr"]), (26.4, 9.8, ["rr", "mr"])):
        stamp(*head_screen(u, v), rows)
    # a sweep for lone pixels over him (the indices and the nose's shine stay)
    keep = idx.copy()
    nx, ny = head_screen(20.0, 22.0)
    keep[int(round(ny)), int(round(nx))] = True
    ak.despeckle(pic, need=4, keep=keep, within=ak.dilate(whole, 2), passes=2)
    return lab


# ---- the far cards ---------------------------------------------------------------------

def pile(pic, x, suit, yy, xx):
    """A foundation: far, small and dim; a grey top card (a black or wine K,
    the hearts' Q, and the suit) over the stacked edges of the pile."""
    fy, fw, fh = FOUND[1], FOUND[2], FOUND[3]
    for k, face in ((2, "felt1"), (1, "grey")):          # the pile's stacked edges, the deeper dimmer
        mm = rounded(x, fy + 2 * k, fw, fh)
        pic.put(mm, "black")
        pic.put(ak.erode(mm, 1), face)
    mm = rounded(x, fy, fw, fh)
    pic.put(mm, "black")
    pic.put(ak.erode(mm, 1), "grey")
    pic.put(ak.erode(mm, 1) & (yy == fy + 1), "ivory")
    col = "wine" if suit in "hd" else "black"
    pic.put(ak.place(mask_of(SUITS[suit]), x + 2, fy + 7), col)
    pic.put(ak.place(mask_of(GLYPH_Q3 if suit == "h" else GLYPH_K3), x + 2, fy + 2), col)


# ---- the trail -----------------------------------------------------------------------

def trail_pts():
    """The king's flight, oldest first: (cx, cy, scale): off the hearts
    pile, down to a bounce on the felt and up into the hero, who is its
    newest copy. The game stamps the card once a tick, so the copies spread
    out where it is fast (near the bounce) and crowd where it is slow; here
    a stamp each STAMP[0] ticks, kept between STAMP[1] and STAMP[2] px apart
    (each shows a strip of its face: no 1-px screen door, no gaps)."""
    fx, fy, fw, fh = FOUND[0][3], FOUND[1], FOUND[2], FOUND[3]
    x, y = fx + fw / 2, fy + fh / 2
    vx, vy = LAUNCH
    pts = []
    bounces = 0
    sub = 8
    for k in range(4000):
        t = k / sub
        s = S0 + (S1 - S0) * min(1.0, t / TICKS)
        h = CH * s
        pts.append((x, y, s, vx * s / S0, vy))
        x += vx * s / S0 / sub
        vy += GRAV / sub
        y += vy / sub
        if y + h / 2 > FLOOR and vy > 0:
            y = FLOOR - h / 2
            vy = -vy * BOUNCE_E
            bounces += 1
        if bounces and x <= END_X:
            break
    out = [pts[0][:3]]
    acc = 0.0
    for (x0, y0, s0, _, _), (x1, y1, s1, vx1, vy1) in zip(pts, pts[1:]):
        dist = np.hypot(x1 - x0, y1 - y0)
        acc += dist
        sp = np.hypot(vx1, vy1)
        step = min(STAMP[2], max(STAMP[1], sp * STAMP[0]))
        if acc >= step:
            out.append((x1, y1, s1))
            acc = 0.0
    if np.hypot(out[-1][0] - pts[-1][0], out[-1][1] - pts[-1][1]) < 2.5:
        out.pop()
    out.append(pts[-1][:3])
    return out


def draw():
    P = ak.Palette(COL, ramps=[FELT_R, ["black", "grey", "ivory", "cream"], ["black", "wine", "red"],
                               ["wine", "amber", "peach", "cream"], ["gold0", "gold1", "gold2", "cream"]])
    pic = ak.Picture.blank(P, "felt0")
    yy, xx = np.mgrid[0:128, 0:128]
    X1, Y1 = xx + 0.5, yy + 0.5
    ALL = np.ones((128, 128), bool)

    # ---- the cards' footprints (the felt needs their shadows)
    pts = trail_pts()
    cards = []
    for cx, cy, s in pts:
        w, h = int(round(CW * s)), int(round(CH * s))
        cards.append((int(round(cx - w / 2)), int(round(cy - h / 2)), w, h))
    trail_m = np.zeros((128, 128), bool)
    for (x, y, w, h) in cards:
        trail_m |= rounded(x, y, w, h)
    lab = hero_labels()
    hero_m = lab != "."

    # ---- the felt: one lit table, a pool of light round the first bounce
    nz = ak.noise((X1, Y1), 9, seed=3, octaves=2) - 0.5
    t = np.clip(ak.radial((X1, Y1), *POOL) + NAP * nz, 0, 1.6)
    level = np.interp(t, [0, 0.3, 0.55, 0.8, 1.05, 1.35, 1.6], [4.2, 3.6, 3.0, 2.3, 1.6, 1.0, 0.5])
    edge_d = np.minimum(np.minimum(X1, 128 - X1), 128 - Y1) + EDGE[2] * (ak.noise((X1, Y1), 7, seed=11, octaves=2) - 0.5)
    level -= np.clip((EDGE[0] - edge_d) / EDGE[0], 0, 1) * EDGE[1]   # the edges sink to dark (wandering seams)
    level -= np.clip((62 - Y1) / 22, 0, 1) * 2.2            # the far felt behind the title sinks to dark
    sh = ak.shift(trail_m, 2, 3) & ~trail_m
    level = np.where(sh, level - 1.0, level)
    bx, by = min(pts, key=lambda q: -q[1] - CH * q[2] / 2)[:2]          # the bounce: a contact shadow on the cloth
    cs = ak.ellipse((X1, Y1), bx + 1.5, FLOOR + 1.0, CONTACT[0], CONTACT[1])
    level = np.where(cs < 0, level - CONTACT[2], level)
    hs = blur(ak.shift(hero_m, *HERO_SHADOW), 2)
    level = level - np.clip(hs * 2.2, 0, 1.8)
    ak.by_level(pic, ak.terrace(level, 0.3), FELT_R, ALL)
    ak.despeckle(pic, need=5, passes=2)

    # ---- the trail, oldest first, each copy stamped over the last: the
    # oldest grey and dim (far, and gone by), then ivory faces, grey edges
    # inside the ribbon
    n = len(cards)
    owner = np.full((128, 128), -1, int)
    tone_of = []
    for i, (x, y, w, h) in enumerate(cards):
        tone = 1 if i < n * AGE_DIM else 0
        tone_of.append(tone)
        m = rounded(x, y, w, h)
        face, edgec = (("ivory", "grey") if tone == 0 else ("grey", "felt1"))
        pic.put(m, edgec)
        pic.put(ak.erode(m, 1), face)
        owner[m] = i
    # indices (the game's: rank and suit side by side), only where one shows whole
    for i, (x, y, w, h) in enumerate(cards):
        redc = "red" if tone_of[i] == 0 else "wine"
        for gx, gy, rows, flip in ((x + 2, y + 2, GLYPH_K3, False), (x + 6, y + 3, HEART3, False),
                                   (x + w - 5, y + h - 7, GLYPH_K3, True), (x + w - 9, y + h - 6, HEART3, True)):
            gm = mask_of(rows)
            if flip:
                gm = gm[::-1, ::-1]
            G = ak.place(gm, gx, gy)
            bx = ak.place(np.ones_like(gm), gx, gy)
            need = bx | ak.shift(bx, 1, 0) | ak.shift(bx, -1, 0) | (ak.shift(bx, 0, 1) if flip else ak.shift(bx, 0, -1))
            if (owner[need] == i).all():
                pic.put(G, redc)
    # the ribbon's silhouette in black
    pic.put(trail_m & ~ak.erode(trail_m, 1), "black")

    # ---- the foundations under the title, over the trail's start (it comes
    # out from under them): a king on each but the hearts' (its king has
    # left it: its queen shows)
    for fx, suit in zip(FOUND[0], "sdch"):
        pile(pic, fx, suit, yy, xx)

    # ---- the hero's shadow on the trail behind him: a dark gap that lifts him off it
    hsh = ak.shift(hero_m, *HERO_ON_TRAIL) & trail_m & ~hero_m
    for c0, c1 in SHADE.items():
        pic.put(hsh & pic.where(c0), c1)

    # ---- the hero, and the glint on his sword's tip
    hero(pic, yy, xx)
    tip = sword_geom()[2]
    tx, ty = to_screen(*tip)
    ak.glint(pic, int(round(tx)), int(round(ty)), arms=(2, 2, 2, 2), tip="ivory")

    # ---- the title, letter by letter from the left, so each letter's
    # outline cuts the extrusion of the one before it (no joins)
    m = ak.load_mask(TITLE)
    tx, ty = ak.centred_x(m), TITLE_Y
    M = ak.place(m, tx, ty)
    labs = ak.letters(M)
    order = sorted(range(1, labs.max() + 1), key=lambda k: np.nonzero(labs == k)[1].min())
    allm = np.zeros_like(M)
    for k in order:
        d = ak.title(pic, labs == k, 0, 0, fill=["gold1"], hi=None, lo=None, outline="black",
                     extrude=dict(dx=1, dy=1, depth=2, colours=["red", "wine"]),
                     shadow=dict(dx=1, dy=2, colour="black"))
        allm |= d["all"]
    # a calm glow of felt hugging the closed footprint
    foot = allm | ak.shift(allm, 1, 2) | ak.shift(allm, 1, 1)
    closed = ak.erode(ak.dilate(foot, 3, diag=True), 3, diag=True) | foot
    pic.put(closed & ~foot, "black")
    dist = ak.distance_px(closed, 6)
    pic.put((dist == 1) & ~closed, "felt1")
    pic.put((dist >= 2) & (dist <= 3) & ~closed, "felt0")
    # the face: gold leaf banded light, a gold0 horizon, light again
    top = int(np.nonzero(M.any(axis=1))[0].min())
    for j, c in enumerate(TITLE_ROWS):
        pic.put(M & (yy == top + j), c)
    hi, lo = ak.bevel_contour(pic, M, "cream", "gold0")
    caps = M & (yy < ty + 2)
    pic.put(caps & pic.where("gold0"), "gold2")
    # the S's spine runs across the horizon: there it is one row, kept off its bevel
    S_ = labs == order[0]
    hz = S_ & ~lo & ~hi & (yy >= top + HORIZON[0]) & (yy <= top + HORIZON[1])
    pic.put(hz & ((yy == top + HORIZON[0]) | ak.nbrs(lo & S_, diag=True)), "gold1")
    # a sweep for lone pixels over the lettering (a bevel step, an extrusion's tip)
    ak.despeckle(pic, need=4, within=ak.dilate(closed, 1), passes=2)
    star = np.zeros((128, 128), bool)
    for gx, gy, arms in GLINTS:
        ak.glint(pic, gx, gy, arms=arms, tip="gold2")
        star[gy - arms[2]:gy + arms[3] + 1, gx] = True
        star[gy, gx - arms[0]:gx + arms[1] + 1] = True
    ak.despeckle(pic, need=3, keep=star, within=ak.dilate(star, 1, diag=True))   # the halo between its arms
    return pic.image()


def title_lines():
    """The title's lettering as drawn here, and its depth, for the title
    screen (tools/titleart.py: the game paints it in the house gold)."""
    return [dict(mask=ak.load_mask(TITLE), depth=2, side="wine")]


if __name__ == "__main__":
    import boxart
    boxart.save(draw(), HERE.parent / "docs" / "cart.png")
