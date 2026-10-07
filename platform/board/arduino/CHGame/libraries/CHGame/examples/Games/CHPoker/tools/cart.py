"""docs/cart.png, CHPoker's cover in the visual menu (docs/cover-art.md).
`chgame boxart` redraws it; edit this, not the PNG.

THE BRIEF (revision 2)
  Message: the bluff. A tough old bulldog card shark, cigar clamped in his
  underbite, peers from under his green dealer's visor with a poker face,
  and the viewer is in on it: he holds a royal flush. In the smoke at the
  next seat, a hound in a fedora, a black silhouette, is trying to read him.

  Composition (a character portrait at the table, camera low, at his chin):
  - Title band (y 2-35): POKER alone on black, the letters dropping in a
    gentle arch, gold chrome (each letter banded from its own top), a cream
    and gold0 bevel by edge runs with flat counters, a 3-step wine
    extrusion, a black outline and shadow, two star glints. First read.
  - Focal point: the bulldog's face, dead centre, the second read. The head
    is modelled, not drawn flat: ellipsoids blended into a skull, brows,
    cheeks, heavy jowls, a short white muzzle and a jutting jaw, ray-marched
    (artkit.render3d) and painted pixel by pixel as levels on the fur ramp
    (half-Lambert key from the top left, ambient occlusion in the folds, a
    slate rim where the cool fill grazes his shadow side). Turned 16 degrees
    toward the hound, cocked 6, tipped down 8: he is sizing the hound up.
    By hand on top: a cream shine across the bald dome, rose ears folded
    back at the skull's corners, heavy-lidded eyes under the visor's shade
    with the pupils slid toward the hound, the rope over the nose, a glossy
    nose (slate sheen, cream shine, nostrils, the groove), the underbite (a
    black mouth under the flews, 2x2 lower teeth, two outlined fangs).
  - The visor: a green celluloid bill over the brow (modelled too), dark at
    its band, a g2 sheen and lip along its front edge; its hard shade falls
    across his brow and eyes, so the whites under it pop.
  - The cigar, clamped in the corner of his mouth on our right and cocked
    up: dark leaf (wine, a tan top, a fawn lit line), a red band by his
    lips, a glowing end (red, a cream hot spot, grey ash), its smoke one
    tapered ribbon curling up and away, ending well below the title.
  - The hound (the bluff's other half): at the left, a black noir
    silhouette, a pinched fedora with a navy band, the brim, a long snout
    and drooping flews, his long ear (navy, its back edge lit), one green
    eye with a cream glint, the lamp grazing his top edges in grey; behind
    him the lamp's glow in the smoke, a slate pool, so the silhouette reads
    dark against light.
  - The fan: a royal flush in spades (10 J Q K A) on clean 1:3 and 1:6
    slopes round a pivot far below the frame: only the top of each card
    shows, so the cream mass stays small and every index reads above the
    install bar. The court cards a thin grey frame line, the ace a crisp
    big spade.
  - Foreground: the table's padded rail (wine, a tan lit top) and the felt;
    a red stack and a green stack of chips (a seam under every chip, cream
    and grey inlays in alternating columns) overlapping the fan's outer
    cards, so they sit in front of it.
  - The room: smoke hanging in the lamplight behind him, flat navy and
    slate plateaus with billowed edges (narrow dithered seams only),
    falling to black in the corners and under the title.
  - Light: warm key from the top left; the cool fill grazing his shadow
    side in slate; the frame's outer two rows and columns sink to the dark.

PALETTE (11 own + cream, grey, black, red)
  gold0-2      the title's own: nothing else uses them
  wine, tan,   the fur ramp (with black and cream), the cigar, the rail, the
  fawn         ears' folds, the eye bags
  navy, slate  the room, the smoke, the hound's glow and band, the suit, the
               nose's body and sheen, the fur's cool rim
  g0, g1, g2   the felt, the visor, the green chips, the hound's eye
  red          the cigar's band and ember, the red chips; cream the cards,
               teeth, eye whites, shines; grey the ash, smoke core, the
               hound's lit edges, the court frames, the fangs' shade

FONT  title.txt (POKER): ONE HUNDRED AND FIFTY FIVE, from the bmf collection
      (author and terms not stated: a `?` face, chosen because no
      clear-terms face is this heavy, round and cartoony at its own size).
"""
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import artkit as ak  # noqa: E402
from artkit import render3d as R  # noqa: E402

TITLE = HERE / "art" / "title.txt"
TITLE_ARCH = [2, 1, 0, 1, 2]              # each letter's drop: P O K E R
TITLE_ROWS = ["gold2"] * 9 + ["gold1"] * 3 + ["gold0"] * 2 + ["gold2"] * 2 + ["gold1"] * 7 + ["gold0"] * 4
TITLE_GLINTS = [(1, 3), (102, 3)]          # on the title's mask: the P's and the R's top corners

COL = {
    "gold0": "#94420A", "gold1": "#EEA820", "gold2": "#FFEC88",     # the title's own
    "wine": "#5A1420", "tan": "#A85C2C", "fawn": "#E4AC70",
    "navy": "#121834", "slate": "#3E4C74",
    "g0": "#0A3A26", "g1": "#1E7C40", "g2": "#6CC85A",
}
FUR = ["black", "wine", "tan", "fawn", "cream"]
FELT = ["black", "g0", "g1", "g2"]
ROOM = ["black", "navy", "slate"]
YY, XX = np.mgrid[0:128, 0:128]
INK = {"k": "black", "c": "cream", "w": "wine", "t": "tan", "f": "fawn", "n": "navy", "s": "slate",
       "e": "grey", "r": "red", "0": "g0", "1": "g1", "2": "g2"}


def M(cv, d):
    """A distance field to a pixel mask: pixels at least half covered."""
    return ak.px_mean((d < 0).astype(np.float32), cv.s) >= 0.5


def darken(pic, m, ramp=("black", "wine", "tan", "fawn", "cream")):
    """One step down the ramp where m is; darkest first, so no pixel steps twice."""
    for k in range(1, len(ramp)):
        pic.put(m & pic.where(ramp[k]), ramp[k - 1])


# ---- the bulldog, modelled: ellipsoids blended into a head, ray-marched ------------------

def ellipsoid(r):
    r = np.asarray(r, float)

    def f(p):
        k0 = np.linalg.norm(p / r, axis=1)
        k1 = np.linalg.norm(p / (r * r), axis=1)
        return k0 * (k0 - 1) / np.maximum(k1, 1e-9)
    return f


def E(pos, r, mat, rot=None):
    return R.xf(R.prim(ellipsoid(r), mat), pos, rot)


FURM, MUZ, NOSE, SUIT, VISOR, CIGAR, JAW = range(7)
SMOKE = dict(scale=12.0, seed=3, amp=0.9)        # the smoke's billows in the lamplight
ROOMGLOW = dict(peak=2.6, fall=2.4, right=0.7)    # the haze behind him
GLOW = dict(x=19.0, y=58.0, rx=24.0, ry=16.5, peak=3.5, fall=2.6)   # the lamp itself, behind the hound
YAW, PITCH, ROLL = -16.0, 8.0, 6.0          # his head turned toward the hound, cocked
KEY = np.array([-0.55, 0.75, 0.45]) / np.linalg.norm([-0.55, 0.75, 0.45])
FILL = np.array([0.85, 0.15, 0.2]) / np.linalg.norm([0.85, 0.15, 0.2])
CAM = dict(pos=(0, -0.9, 11), target=(0, -0.2, 0), fov=24.0, shift=(6, 8))


def bulldog():
    """The head in its own frame (x his left = our right, y up, z toward us):
    a skull, brows, cheeks, heavy jowls, a short white muzzle (the bridge and
    the flews), the jutting lower jaw, the nose; the visor; the cigar. And
    his shoulders. Returns (scene, the cigar alone, the head's rotation)."""
    k = 0.10
    skull = E((0, 0.36, -0.25), (0.98, 0.72, 0.92), FURM)
    parts = [E((-0.38, 0.40, 0.55), (0.38, 0.20, 0.30), FURM), E((0.38, 0.40, 0.55), (0.38, 0.20, 0.30), FURM),
             E((-0.72, -0.12, 0.28), (0.52, 0.50, 0.50), FURM), E((0.72, -0.12, 0.28), (0.52, 0.50, 0.50), FURM),
             E((-0.92, -0.62, 0.05), (0.50, 0.50, 0.48), FURM), E((0.92, -0.62, 0.05), (0.50, 0.50, 0.48), FURM)]
    h = skull
    for n in parts:
        h = R.SU(h, n, k)
    muzzle = R.SU(R.SU(E((0, 0.02, 0.75), (0.30, 0.36, 0.30), MUZ),
                       E((-0.40, -0.40, 0.80), (0.46, 0.36, 0.34), MUZ), 0.08),
                  E((0.40, -0.40, 0.80), (0.46, 0.36, 0.34), MUZ), 0.08)
    h = R.SU(h, muzzle, k)
    h = R.SU(h, E((0, -0.80, 0.92), (0.56, 0.22, 0.42), JAW), 0.04)
    nose = R.xf(R.prim(R.box((0.27, 0.14, 0.13), 0.10), NOSE), (0, -0.02, 1.10))
    bill = R.xf(R.Inter(R.prim(ellipsoid((1.02, 0.045, 1.05)), VISOR), R.prim(lambda p: -(p[:, 2] - 0.25), VISOR)),
                (0, 0.66, 0.42), R.rot_x(18))
    band = R.Inter(R.prim(lambda p: np.abs(p[:, 1] - 0.64) - 0.07, VISOR),
                   R.Sub(E((0, 0.36, -0.25), (1.02, 0.78, 0.96), VISOR), E((0, 0.36, -0.25), (0.96, 0.72, 0.90), VISOR)))
    cig = R.prim(R.capsule((0.55, -0.60, 0.92), (1.50, -0.12, 1.30), 0.105), CIGAR)
    rot = R.rot_y(YAW) @ R.rot_x(PITCH) @ R.rot_z(ROLL)
    body = E((0, -2.1, -0.7), (2.0, 1.2, 1.0), SUIT)
    scene = R.U(R.xf(R.U(h, nose, bill, band, cig), (0, 0, 0), rot), body)
    return scene, R.xf(cig, (0, 0, 0), rot), rot


def lighting(cam, scene, out, s, shadow_by):
    """Per pixel, from the render: each pixel's material, the key's and the
    fill's n.L, ambient occlusion and the cigar's shadow."""
    mat = R.majority(out, s)
    hit = mat >= 0
    X, Y = (XX[hit] + 0.5).astype(float), (YY[hit] + 0.5).astype(float)
    ro, rd = cam.rays(X, Y)
    t = ak.at_px(out["depth"], s)[hit]
    n = ak.at_px(out["normal"], s)[hit].astype(float)
    t = np.where(np.isfinite(t), t, 0)
    p = ro + rd * t[:, None]
    res = {"mat": mat, "hit": hit}
    for nm, v in (("kd", n @ KEY), ("fd", n @ FILL), ("ao", R._ao(scene, p, n, k=2.0)),
                  ("sh", R._shadow(shadow_by, p + n * 2e-3, KEY, k=12))):
        a = np.zeros((128, 128)) if nm != "ao" and nm != "sh" else np.ones((128, 128))
        a[hit] = v
        res[nm] = a
    return res


# ---- the cards ---------------------------------------------------------------------------

PIVOT = (64.0, 182.0)
CW, CH = 28, 40                          # a card, in pixels
CTOP = 84.0                              # how far from the pivot its top edge is
# the fan: slopes 1:3 and 1:6 (clean steps on every edge)
ANGLES = [-np.degrees(np.arctan(1 / 3)), -np.degrees(np.arctan(1 / 6)), 0.0,
          np.degrees(np.arctan(1 / 6)), np.degrees(np.arctan(1 / 3))]
RANKS = ["10", "J", "Q", "K", "A"]

GLYPH = {
    "A": ["..k..", ".k.k.", ".k.k.", "k...k", "kkkkk", "k...k", "k...k"],
    "K": ["k...k", "k..k.", "k.k..", "kk...", "k.k..", "k..k.", "k...k"],
    "Q": [".kkk.", "k...k", "k...k", "k...k", "k.k.k", "k..k.", ".kk.k"],
    "J": ["..kkk", "...k.", "...k.", "...k.", "...k.", "k..k.", ".kk.."],
    "10": [".k..k.", "kk.k.k", ".k.k.k", ".k.k.k", ".k.k.k", ".k.k.k", ".k..k."],
}
PIP = ["..k..", ".kkk.", "kkkkk", "kkkkk", "k.k.k", "..k..", ".kkk."]


def card_uv(theta):
    """Pixel centres in a card's own frame: u across (0 at its left edge), v
    down (0 at its top edge)."""
    t = np.radians(theta)
    dx, dy = XX + 0.5 - PIVOT[0], YY + 0.5 - PIVOT[1]
    u = dx * np.cos(t) + dy * np.sin(t)
    v = -dx * np.sin(t) + dy * np.cos(t)
    return u + CW / 2, v + CTOP


def card_xy(theta, u, v):
    """A point of a card's frame on the picture."""
    t = np.radians(theta)
    uu, vv = u - CW / 2, v - CTOP
    return PIVOT[0] + uu * np.cos(t) - vv * np.sin(t), PIVOT[1] + uu * np.sin(t) + vv * np.cos(t)


def card_P(P, theta):
    """The canvas's sample coordinates in a card's own frame."""
    t = np.radians(theta)
    dx, dy = P[0] - PIVOT[0], P[1] - PIVOT[1]
    return (dx * np.cos(t) + dy * np.sin(t) + CW / 2, -dx * np.sin(t) + dy * np.cos(t) + CTOP)


def stamp(pic, rows, theta, u0, v0, key, where=None):
    """Pixels set on a card: rows anchored at (u0, v0) of its frame, the
    lower half stepped one pixel with the card's lean (a pixel artist's
    rotation: a full shear on the outer cards made the 10 read as W)."""
    t = np.tan(np.radians(theta))
    x0, y0 = card_xy(theta, u0, v0)
    out = []
    h = len(rows)
    for j, r in enumerate(rows):
        lean = int(np.sign(t)) if abs(t) > 0.05 else 0     # one step at most: small letters stay legible
        sx = int(np.floor(x0 + 0.5)) - lean * (j >= h // 2)
        for i, ch in enumerate(r):
            if ch in key:
                x, y = sx + i, int(np.floor(y0 + j + 0.5))
                if 0 <= x < 128 and 0 <= y < 128 and (where is None or where[y, x]):
                    pic.px(x, y, key[ch])
                    out.append((x, y))
    return out


def spade(P, cx, cy, s):
    """A spade's distance field, s its half width."""
    lob = ak.union(ak.circle(P, cx - s * 0.5, cy + s * 0.15, s * 0.52), ak.circle(P, cx + s * 0.5, cy + s * 0.15, s * 0.52))
    top = ak.polygon(P, [(cx, cy - s * 1.15), (cx + s * 0.98, cy + 0.05 * s), (cx - s * 0.98, cy + 0.05 * s)])
    body = ak.smin(lob, top, s * 0.25)
    stem = ak.polygon(P, [(cx, cy + s * 0.2), (cx + s * 0.42, cy + s * 1.05), (cx - s * 0.42, cy + s * 1.05)])
    return ak.union(body, stem)


# ---- chips -------------------------------------------------------------------------------

# kind: (top face, lit side, shaded side, seam on the lit side, seam in the shade)
CHIPS = {"red": ("red", "red", "wine", "wine", "black"),
         "green": ("g2", "g1", "g0", "g0", "black"),
         "blue": ("slate", "navy", "navy", "black", "black")}


def chip_stack(pic, cv, cx, cy, r, n, kind, t=3.0, k=0.42):
    """A stack of n chips seen from a little above, the bottom chip's top
    face centred at (cx, cy): each chip's edge a band t px tall with a dark
    seam under it, cream inlays round it in columns that alternate chip by
    chip, the top chip's face ringed with inlays. Returns its mask."""
    X, Y = cv.P
    top_c, lit_c, dark_c, seam_l, seam_d = CHIPS[kind]
    allm = np.zeros((128, 128), bool)
    ux = (XX + 0.5 - cx) / r
    ang = np.degrees(np.arcsin(np.clip(ux, -1, 1)))
    for i in range(n):
        cyi = cy - i * t
        u = np.clip((X - cx) / r, -1, 1)
        e = ((X - cx) / r) ** 2 + ((Y - cyi) / (k * r)) ** 2 - 1
        low = cyi + t + k * r * np.sqrt(1 - u * u)
        side = np.maximum(np.abs(X - cx) - r, np.maximum(cyi - Y, Y - low))
        Em = M(cv, e)
        Sm = M(cv, side) & ~Em
        allm |= Em | Sm
        shaded = ux > 0.25
        ph = 22.5 if i % 2 else 0.0
        spot = np.abs(((ang + ph + 22.5) % 45) - 22.5) < 8.5
        seam = Sm & ~ak.shift(Sm, 0, -1)               # its lowest row: the gap to the chip under it
        pic.put(Sm, lit_c)
        pic.put(Sm & shaded, dark_c)
        pic.put(Sm & spot & ~shaded, "cream")
        pic.put(Sm & spot & shaded, "grey")
        pic.put(seam & ~shaded, seam_l)
        pic.put(seam & shaded, seam_d)
        pic.put(Em, top_c)
        if i == n - 1:
            er = np.sqrt(((XX + 0.5 - cx) / r) ** 2 + ((YY + 0.5 - cyi) / (k * r)) ** 2)
            a2 = np.degrees(np.arctan2((YY + 0.5 - cyi) / k, XX + 0.5 - cx))
            rim = Em & (er > 0.6) & (np.abs(((a2 + 22.5) % 45) - 22.5) < 9)
            pic.put(rim, "cream")
            pic.put(Em & (er < 0.42), lit_c if kind != "blue" else "navy")
    ak.outline(pic, allm, "black")
    return allm


# ---- the picture -------------------------------------------------------------------------

def draw():
    P_ = ak.Palette(COL, ramps=[["black", "navy", "slate", "grey", "cream"],
                                ["black", "wine", "tan", "fawn", "cream"],
                                ["black", "g0", "g1", "g2", "cream"],
                                ["gold0", "gold1", "gold2", "cream"]],
                    pairs=[("wine", "red")])
    cv = ak.Canvas("#000000")
    P = cv.P
    S = cv.s
    pic = ak.Picture.blank(P_, "black")
    xc, yc = XX + 0.5, YY + 0.5

    # -- the room: smoke hanging in the lamplight behind him, a glow that
    # falls off to the dark corners; black under the title
    nz = ak.noise((xc, yc), SMOKE["scale"], seed=SMOKE["seed"], octaves=2) - 0.5
    gr = np.hypot((xc - 62) / 66, (yc - 74) / 40)
    hz = ROOMGLOW["peak"] - ROOMGLOW["fall"] * gr - ROOMGLOW["right"] * np.clip((xc - 70) / 50, 0, 1) + SMOKE["amp"] * nz
    hz = np.minimum(hz, (yc - 37) / 5.0)
    gd = np.hypot((xc - GLOW["x"]) / GLOW["rx"], (yc - GLOW["y"]) / GLOW["ry"])
    hz = np.maximum(hz, GLOW["peak"] - GLOW["fall"] * gd + SMOKE["amp"] * nz * np.clip(gd - 0.5, 0, 1))   # the lamp's glow at the left
    hz = np.minimum(hz, (yc - 37) / 2.5)                          # black under the title
    ak.by_level(pic, np.clip(ak.terrace(hz, 0.25), 0, 2), ROOM, np.ones((128, 128), bool), q=4)
    pic.put((XX > 88) & (YY < 70), "black")                         # the far side: dark, so the smoke reads

    # -- at the next seat, in the glow: the hound in the fedora, a black
    # silhouette in profile (a pinched crown, the brim, a long snout and
    # flews, his long ear), the lamp grazing his top edges, one narrowed
    # green eye on our man
    crown = ak.smin(ak.polygon(P, [(5.5, 56.5), (6.5, 49.6), (9.0, 46.6), (13.5, 47.2), (18.0, 46.4), (20.5, 48.8), (21.5, 56.5)]),
                    ak.box(P, 13.5, 55, 8, 2), 1.0)
    brim = ak.polygon(P, [(-1, 55.2), (13, 54.8), (22.5, 55.2), (26.5, 56.4), (28.0, 58.0), (26.0, 58.6), (20, 57.9), (-1, 58.6)])
    skull = ak.ellipse(P, 12.5, 62.0, 8.0, 6.0)
    snout = ak.polygon(P, [(15, 60.5), (24.0, 61.4), (30.0, 62.4), (32.6, 64.6), (31.2, 67.0), (18, 68.5)])
    flews = ak.ellipse(P, 24.5, 69.0, 5.6, 2.6, angle=-8)
    ear = ak.ellipse(P, 9.0, 71.0, 3.6, 10.5, angle=8)
    neck = ak.box(P, 11, 80, 9, 9, r=4)
    collar = ak.polygon(P, [(0, 77), (13, 75), (23, 74.0), (25, 82), (17, 86), (0, 92)])
    body = ak.ellipse(P, 8, 104, 22, 22)
    hound = ak.union(crown, brim, ak.smin(ak.smin(skull, snout, 1.5), flews, 1.5), ear, neck, collar, body)
    Hd = M(cv, hound)
    pic.put(Hd, "black")
    Bd = M(cv, ak.box(P, 13.5, 54.0, 8.5, 1.1)) & M(cv, crown)
    pic.put(Bd, "navy")                                                   # the hat band
    lit = Hd & ~ak.shift(Hd, 0, 1)
    pic.put(lit & (XX > 2) & (YY < 64), "grey")                           # the lamp grazes his top edges
    ak.patch(pic, 29, 62, ["kkkk", "kkkkk", ".kkk"], INK)                 # the nose
    ak.patch(pic, 14, 59, ["kkkk", "k2ck", "k22k"], INK)                  # the eye under the brim
    Em_ = M(cv, ear) & ~M(cv, brim)                                       # his long ear, hanging
    pic.put(Em_ & ak.erode(Em_, 1), "navy")
    pic.put(Em_ & ak.erode(Em_, 1) & ~ak.shift(ak.erode(Em_, 1), 1, 0), "slate")
    ak.despeckle(pic, need=4, within=(YY > 36) & ~((XX >= 14) & (XX <= 17) & (YY >= 59) & (YY <= 62)), passes=2)

    # -- the bulldog
    scene, cig_only, rot = bulldog()
    cam = R.Camera(CAM["pos"], CAM["target"], fov=CAM["fov"], shift=CAM["shift"])
    mats = [R.Mat("#FFFFFF")] * 7
    out = R.render(cv, scene, cam, mats, ss=2, region=(0, 30, 128, 128), shadows=False, ao=False)
    L = lighting(cam, scene, out, S, cig_only)
    mat, kd, fd, ao, shd, hit = L["mat"], L["kd"], L["fd"], L["ao"], L["sh"], L["hit"]
    hl = np.clip(0.5 + 0.5 * kd, 0, 1) ** 2.0                    # half-Lambert: a cartoon's soft wrap
    lv = 0.7 + 3.1 * hl - 1.6 * (1 - ao) - 1.2 * (1 - shd)
    furm = mat == FURM
    muzm = (mat == MUZ) | (mat == JAW)
    ak.by_level(pic, np.clip(ak.terrace(lv, 0.2), 0, 3.0), FUR, furm, q=4)
    nose_top = np.nonzero((mat == NOSE).any(axis=1))[0].min()
    ak.by_level(pic, np.clip(ak.terrace(lv + 0.4, 0.2), 0, np.where(YY < nose_top, 3.0, 4.0)), FUR, mat == MUZ, q=4)
    ak.by_level(pic, np.clip(ak.terrace(lv - 0.2, 0.2), 0, 3), FUR, mat == JAW, q=4)
    vm = mat == VISOR
    # the visor: green celluloid, a sheen along its front edge, its lip
    # catching the lamp in cream on the lit side
    lip = vm & ~ak.shift(vm, 0, -1)                               # the bill's front edge
    dl = ak.distance_px(lip, 10)
    shade_side = XX > 84                                         # the bill turns away from the lamp
    pic.put(vm, "g1")
    pic.put(vm & (dl <= 3) & ~shade_side, "g2")                  # the sheen along the front
    pic.put(vm & (dl == 4) & ~shade_side & ak.checker(), "g2")
    pic.put(vm & (dl >= 9), "g0")                                # back at the band, the bill in its own shade
    pic.put(vm & (dl == 8) & ak.checker(), "g0")
    pic.put(lip, "g2")
    lx = np.nonzero(lip)[1]
    pic.put(lip & (XX < lx.min() + 0.5 * (lx.max() - lx.min())) & (XX > lx.min() + 3), "cream")
    ak.by_level(pic, np.clip(ak.terrace(0.3 + 1.4 * hl + 0.8 * np.clip(fd, 0, 1), 0.3), 0, 2), ROOM, mat == SUIT, q=4)
    under = ak.shift(vm, 0, 1) | ak.shift(vm, 0, 2) | ak.shift(vm, 0, 3) | ak.shift(vm, 1, 3)
    darken(pic, under & ~vm & (furm | muzm | (mat == NOSE)))
    rimm = furm & (fd > 0.6) & (kd < 0.0) & ~ak.erode(hit, 2)
    pic.put(rimm, "slate")
    ak.outline(pic, hit, "black")
    ak.despeckle(pic, need=5, within=hit, passes=2)                   # lone pixels from the levels

    def hp(p):
        """A point of the head's frame on the picture."""
        return cam.project(rot @ np.asarray(p, float))

    hand = np.zeros((128, 128), bool)                    # hand-placed pixels: the clean-up leaves them be

    def hstamp(p, rows, key=INK):
        x, y = hp(p)
        h, w = len(rows), max(len(r) for r in rows)
        x0, y0 = int(np.floor(x - w / 2 + 0.5)), int(np.floor(y - h / 2 + 0.5))
        ak.patch(pic, x0, y0, rows, key)
        hand[max(0, y0):y0 + h, max(0, x0):x0 + w] = True

    def hink(pts, colour, where=None):
        return ak.ink(pic, [hp(p) for p in pts], colour, where=where)

    head = hit & (mat != SUIT) & (mat != CIGAR)

    jm = mat == JAW

    # the lamp's shine on his bald dome
    hink([(-0.66, 0.82, 0.08), (-0.45, 0.89, 0.20), (-0.25, 0.93, 0.25), (-0.05, 0.98, 0.20)], "cream",
         where=furm & pic.where("fawn"))
    hink([(-0.50, 0.86, 0.22), (-0.32, 0.90, 0.28)], "cream", where=furm & pic.where("fawn"))

    # the folds from his nose down round the flews
    hink([(-0.30, -0.08, 1.05), (-0.52, -0.30, 0.94), (-0.64, -0.52, 0.78)], "tan", where=head & pic.where("fawn", "cream"))
    hink([(0.30, -0.08, 1.05), (0.52, -0.30, 0.94), (0.64, -0.50, 0.78)], "wine", where=head & pic.where("fawn", "tan"))

    # the rope: the fold of skin over his nose
    hink([(-0.28, 0.16, 1.02), (-0.13, 0.22, 1.07), (0.13, 0.22, 1.07), (0.28, 0.16, 1.02)], "wine",
         where=head & ~pic.where("black", "cream"))

    # the nose, glossy: a slate sheen across its top, a cream shine on the
    # lit side, two nostrils curling in, the groove between them
    nm = mat == NOSE
    nys, nxs = np.nonzero(nm)
    ny0, ny1, nx0, nx1 = nys.min(), nys.max(), nxs.min(), nxs.max()
    nw = nx1 - nx0
    pic.put(nm, "navy")
    pic.put(nm & (YY == ny0), "slate")
    pic.put(nm & (YY == ny0 + 1) & (XX < nx0 + 0.6 * nw), "slate")
    pic.put(nm & (YY >= ny1), "black")
    ak.patch(pic, nx0 + 2, ny0, ["scccs", ".cce", "..e"], INK)                    # the shine
    for f, rows in ((0.25, ["k..", "kk.", ".kk"]), (0.75, ["..k", ".kk", "kk."])):
        ak.patch(pic, int(round(nx0 + f * nw)) - 1, ny1 - 3, rows, INK)
    pic.put(nm & (XX == int(round(nx0 + 0.5 * nw))) & (YY >= ny1 - 2), "black")

    # eyes: heavy lids sloping down to the nose (the scowl), whites showing
    # under them, the pupils slid to our left: he is watching the hound
    hstamp((-0.50, 0.30, 0.72), ["kkkkk......",
                                 "kkkkkkkkk..",
                                 ".kkkkkkkkkk",
                                 "kckkcccccck",
                                 "kckkccccck.",
                                 ".kccccckk..",
                                 "..kkkkk....",
                                 "...www....."])
    hstamp((0.50, 0.30, 0.72), [".......kkkk",
                                "...kkkkkkkk",
                                "kkkkkkkkkk.",
                                "kckkcccck..",
                                "kckkccckk..",
                                ".kkkkkkk...",
                                "..wwwww....",
                                "..........."])

    # the underbite: the mouth a dark gap under the flews, the lower teeth
    # standing on the jutting jaw, two fangs over the upper lip
    gap = jm & (ak.shift(mat == MUZ, 0, 1) | ak.shift(mat == MUZ, 0, 2) | ak.shift(mat == MUZ, 0, 3))
    pic.put(gap, "black")
    cols = sorted(set(np.nonzero(gap)[1].tolist()))
    x0_, x1_ = cols[0], cols[-1]
    bottom = {x: np.nonzero(gap[:, x])[0].max() for x in cols}
    for xa in range(x0_, x1_ + 1, 3):                          # the incisors: 2 px wide, a black gap between
        f = (xa - x0_) / max(1, x1_ - x0_)
        if not (0.2 < f < 0.8) or xa + 1 not in bottom:
            continue
        yb = max(bottom[xa], bottom[xa + 1])
        for x in (xa, xa + 1):
            for y in (yb - 1, yb):
                if gap[y, x] or y == yb:
                    pic.px(x, y, "cream" if f < 0.62 or x == xa else "grey")
    for f, rows in ((0.16, [".k..", "kck.", "kcck", "kcck", "kcek"]), (0.84, ["..k.", ".kck", "kcek", "kcek", "keek"])):
        x = int(round(x0_ + f * (x1_ - x0_)))
        yb = np.nonzero(gap[:, x])[0].max()
        ak.patch(pic, x - 2, yb - 4, rows, INK)

    # rose ears, folded back at the skull's top corners: the flap lit on
    # its top edge, the inside of the fold dark
    def contour_x(y, side):
        xs = np.nonzero(head[y])[0]
        return xs.min() if side < 0 else xs.max()
    ey_ = int(round(hp((-0.86, 0.80, -0.30))[1])) - 4
    ak.patch(pic, contour_x(ey_, -1) - 9, ey_ - 3, [".....kkkkk..",
                                                    "...kkffffftk",
                                                    "..kfffttttwk",
                                                    ".kfttwwwwwk.",
                                                    "kfttwwkkkk..",
                                                    "kttwwk......",
                                                    "kwwkk.......",
                                                    ".kk........."], INK)
    ey_ = int(round(hp((0.86, 0.80, -0.30))[1])) + 1
    ak.patch(pic, contour_x(ey_, 1) - 2, ey_ - 3, ["..kkkkk....",
                                                   "ktttttttk..",
                                                   "kwwwwwtttk.",
                                                   ".kkwwwwwttk",
                                                   "...kkkwwwtk",
                                                   "......kkwwk",
                                                   "........kk."], INK)

    # -- the cigar, clamped in the corner of his mouth: dark leaf, a lit
    # top edge, a red band by his lips, a glowing end, ash
    A0, A1 = np.array(hp((0.55, -0.60, 0.92))), np.array(hp((1.50, -0.12, 1.30)))
    ax_ = (A1 - A0) / np.hypot(*(A1 - A0))
    Lc = np.hypot(*(A1 - A0))
    ct = ((xc - A0[0]) * ax_[0] + (yc - A0[1]) * ax_[1]) / Lc
    cacross = (xc - A0[0]) * ax_[1] - (yc - A0[1]) * ax_[0]            # + above the axis (toward the lamp)
    cm = mat == CIGAR
    pic.put(cm, "wine")
    pic.put(cm & (cacross > 0.3), "tan")
    pic.put(cm & (cacross > 1.6), "fawn")
    bandm = cm & (ct > 0.30) & (ct < 0.43)
    pic.put(bandm, "red")
    pic.put(bandm & (cacross < -0.8), "wine")
    pic.put(bandm & (cacross > 1.2) & (ct > 0.34) & (ct < 0.40), "cream")
    ak.outline(pic, cm, "black")
    tip = ct.copy()
    tip[~cm] = -1
    tmax = tip.max()
    endm = cm & (ct > tmax - 4.0 / Lc)                                  # the lit end
    pic.put(endm, "red")
    pic.put(endm & (ct > tmax - 1.2 / Lc), "grey")                      # ash on the very tip
    pic.put(endm & (np.abs(cacross) < 0.8) & (ct > tmax - 3.0 / Lc) & (ct < tmax - 1.2 / Lc), "cream")
    endm = cm & (ct > tmax - 4.0 / Lc)
    ex, ey = A1

    # smoke: one ribbon off the end, curling up and right, thinning out well
    # under the title: a grey core lit on its left, a slate body, its last
    # pixels broken
    sp = ak.path(((ex + 1.5, ey - 3.0), (ex + 7, ey - 7), (ex + 9, ey - 12), (ex + 4, ey - 15)),
                 ((ex + 4, ey - 15), (ex - 2, ey - 18), (ex - 1, ey - 23), (ex + 6, ey - 24)), n=24)
    T = ak.tube(P, sp, [0.6, 1.0, 1.4, 1.8, 2.0, 1.7, 1.2])
    tpos = ak.at_px(T["s"] / T["len"], S)
    cov = ak.px_mean((T["d"] < 0).astype(np.float32), S)
    nxs = ak.at_px(T["n"][..., 0], S)
    nys = ak.at_px(T["n"][..., 1], S)
    smk = (cov > 0.45) & ~head & ~cm & ~ak.dilate(endm, 1)
    keep_s = smk & ((tpos < 0.8) | (ak.paint.BAYER < 1 - (tpos - 0.8) / 0.2))
    pic.put(keep_s, "slate")
    pic.put(keep_s & ((((nxs * 0.8 + nys * 0.6) < -0.2) & (tpos < 0.7)) | (tpos < 0.2)), "grey")

    # -- the table: its far rail (padded leather, lit along its top) and the
    # felt in front, a pool of lamplight falling off to the corners
    RAIL = 104
    rail = (YY >= RAIL) & (YY < RAIL + 5)
    pic.put(rail, "wine")
    pic.put(rail & (YY == RAIL), "tan")
    pic.put(rail & (YY == RAIL + 1) & (ak.paint.BAYER < 0.5), "tan")
    pic.put(rail & (YY == RAIL + 4), "black")
    felt = YY >= RAIL + 5
    pool = np.clip(1 - np.hypot((xc - 64) / 80, (yc - 122) / 18), 0, 1)
    ak.by_level(pic, np.clip(ak.terrace(0.7 + 2.6 * pool, 0.3), 0, 2.6), FELT, felt, q=4)

    # -- the fan: its shadow on his suit and jowls first (the lamp is up to
    # the left), then the cards back to front
    fanm = np.zeros((128, 128), bool)
    for th in ANGLES:
        u, v_ = card_uv(th)
        fanm |= (u >= -1) & (u < CW + 1) & (v_ >= -1) & (v_ < CH + 1)
    fsh = (ak.shift(fanm, 2, 1) | ak.shift(fanm, 3, 2)) & ~fanm
    darken(pic, fsh & hit & (mat != SUIT))
    pic.put(fsh & (mat == SUIT) & pic.where("slate"), "navy")
    for th, rk in zip(ANGLES, RANKS):
        u, v_ = card_uv(th)
        Cm = (u >= 0) & (u < CW) & (v_ >= 0) & (v_ < CH)
        corner = ((u < 1) | (u >= CW - 1)) & ((v_ < 1) | (v_ >= CH - 1))
        Cm &= ~corner
        ak.outline(pic, Cm, "black")
        pic.put(Cm, "cream")
        if rk in ("J", "Q", "K"):
            fr = Cm & (u >= 8) & (u < CW - 3) & (v_ >= 3) & (v_ < CH - 3)
            pic.put(fr & ~ak.erode(fr, 1), "grey")
        elif rk == "10":
            for vv in (14, 24):
                stamp(pic, PIP, th, 10, vv, INK, where=Cm)
        stamp(pic, GLYPH[rk], th, 2, 2, INK)
        stamp(pic, PIP, th, 2 if rk != "10" else 3, 11, INK)
        if rk == "A":
            Pc = card_P(P, th)
            cov = ak.px_mean((spade(Pc, CW / 2, CH / 2 + 1.5, 7.0) < 0).astype(np.float32), S)
            pic.put((cov >= 0.5) & Cm, "black")

    # the last lone pixels round his jaw and collar
    ak.despeckle(pic, need=4, within=ak.dilate(hit, 3) & ~ak.dilate(hand | gap | nm | endm | cm, 1) & (YY > 38), passes=2)

    # -- chips on the felt: his stack and the pot
    for cx_, cy_, n_, kind in ((17, 121, 5, "red"), (111, 119, 6, "green")):
        sh_ = M(cv, ak.ellipse(P, cx_ + 4, cy_ + 3, 10.5, 4.5))                  # its shadow on the felt
        pic.put(sh_ & pic.where("g1", "g2"), "g0")
        chip_stack(pic, cv, cx_, cy_, 10, n_, kind)

    # the frame: its outer rows and columns sink to the dark
    edge = np.zeros((128, 128), bool)
    edge[:, :2] = edge[:, -2:] = True
    edge[-2:, :] = True
    for _ in range(2):
        for a_, b_ in (("navy", "black"), ("slate", "navy"), ("g0", "black"), ("g1", "g0"), ("g2", "g1"),
                       ("wine", "black"), ("red", "wine"), ("cream", "grey"), ("grey", "slate"), ("tan", "wine")):
            pic.put(edge & pic.where(a_), b_)
        edge[:, 1] = edge[:, -2] = edge[-2, :] = False

    # -- the title
    m, mrow = arch(ak.load_mask(TITLE), TITLE_ARCH)
    tx, ty = ak.centred_x(m), 2
    tm = ak.title(pic, m, tx, ty, fill=["gold1"], hi=None, lo=None,
                  extrude=dict(dx=1, dy=1, depth=3, side="wine", bottom="wine"),
                  shadow=dict(dx=1, dy=1, colour="black"))
    J = np.full((128, 128), -1)
    h, w = mrow.shape
    J[ty:ty + h, tx:tx + w] = mrow
    for j, c in enumerate(TITLE_ROWS):
        pic.put(tm["face"] & (J == j), c)
    cls = ak.bevel_runs(pic, tm["face"], "cream", "gold0")
    counter = ~tm["face"] & ~ak.paint.outside_of(tm["face"])
    flat = (cls != 0) & ak.paint.nbrs(counter)
    for j, c in enumerate(TITLE_ROWS):
        pic.put(flat & (J == j), c)
    for gx, gy in TITLE_GLINTS:
        ak.glint(pic, tx + gx, ty + gy, 3, tip="gold2")
    return pic.image()


def arch(m, offs):
    """The title's letters each dropped by its own offset (an arch), and each
    pixel's row counted from its own letter's top."""
    lab = ak.letters(m)
    xs = [np.nonzero(lab == k)[1].min() for k in range(1, lab.max() + 1)]
    order = np.argsort(xs)
    out = np.zeros((m.shape[0] + max(offs), m.shape[1]), bool)
    row = np.full(out.shape, -1)
    for j, k in enumerate(order):
        ys, xs_ = np.nonzero(lab == k + 1)
        out[ys + offs[j], xs_] = True
        row[ys + offs[j], xs_] = ys
    return out, row


def title_lines():
    """The title's lettering as drawn here, and its depth, for the title
    screen (tools/titleart.py: the game paints it in the house gold)."""
    m, _ = arch(ak.load_mask(TITLE), TITLE_ARCH)
    return [dict(mask=m, depth=3, side="wine")]


if __name__ == "__main__":
    import boxart
    print(boxart.save(draw(), HERE.parent / "docs" / "cart.png"))
