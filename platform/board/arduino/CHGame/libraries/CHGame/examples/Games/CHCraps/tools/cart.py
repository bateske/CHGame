"""docs/cart.png, CHCraps' cover in the visual menu (docs/cover-art.md).
`chgame boxart` redraws it; edit this, not the PNG.

THE BRIEF (revision 1)
  Message: SEVEN! The throw has just hit the rubber pyramids of the far
  wall in a flash of light, and two red glass casino dice come tumbling back
  down the table straight at you, showing a one and a six: a natural on the
  come-out. Speed, heat and red glass (Yacht Dice is a lamplit still life
  in ivory and wood; this one is the moment of the throw).
  Composition: the camera sits low at the near end of the table and looks
  down its length, a wide lens. The table is a tunnel: the felt a wedge
  widening toward us, the padded side rails (wine leather rolls) running in
  from the frame's edges to the far wall's corners. Everything radiates
  from the impact, at the vanishing point right under the title: the
  rails, the layout's lines, the dice's speed trails, the sparks.
  - Title (y 3-32): CRAPS alone on the calm navy of the room, black round
    it; nothing else uses its golds.
  - The far end (y 35-56): the far rail, black leather with a wine roll,
    a short red-to-rose sheen over the flash and its shadow on the rubber;
    under it the pyramid rubber, a diamond lattice (8 x 6 px), each pyramid
    lit whole by the lamp over the middle: grey up-left faces, steel
    up-right, navy down-left, black down-right, falling to black at the
    ends. Round the impact the faces turned to the flash catch it, red in
    the first ring, wine in the next.
  - The impact: a cartoon flash, a cream core in a rose star (four long
    spikes, four short), a wine rim and a black ring against the lattice;
    four sparks flung off it, tapered, cream at the head.
  - The dice, the focal pair, fly out of it toward us. The one is smaller
    and nearer the wall, at the left; the six is the biggest thing in the
    picture, at the lower right. Each is an exact perspective cube with
    flat faces (the lit top ember, the number face red, the shaded side
    wine) and the marks of red glass: the light that came in at the top
    glows out along each face's lower and right edges (solid ember or red
    rows, then 50% and 25% into the face), hottest (rose) at the die's
    lowest corner, with the silhouette's far edge a step darker (the
    glass's thickness) inside the black outline. The edges facing the key
    are clean lines: cream to rose on the top's back edges with a shorter
    second line inside (glass shows its edge twice), a rose crease where
    the top meets the number face, a red one on the shaded side, a rose
    line down the six's lit left edge. Pips are round stamps (ovals on a
    foreshortened top), evenly spaced, cream, each with a pixel of face
    round it; none on a face too narrow for that. The one's pip is
    enlarged. A four-pointed glint on each top's back corner, clear of the
    pips and the trails.
  - Motion: two or three speed trails per die, from 2.5 px off its
    trailing edge back to the impact, bowing (the bounce's arc), 3-4 px at
    the root tapering to a pixel, rose to ember to red to wine, with a
    cream core near the die.
  - The felt: a pool of light under the dice falling to black at the
    frame's edges and the bottom, the walls' foot in shadow, the flash's
    glow at the far wall's foot; the layout a step lighter (a step darker
    on the brightest plateau): the pass line's band round the far end, the
    field's two lines, the centre's box under the dice.
  - Shadows: each die's, apart from it (it is in the air) down and to the
    right (the six's beside its low corner, by the frame), a felt0 lens
    with a wine heart: light through red glass.
  - A bet down: a stack of three blue chips in the near left corner, cut
    by the frame (traced as exact cylinders): steel tops with a navy inlay
    ring, cream edge spots and a grey sheen on the label's lit side, sides
    lit grey to navy round into the
    shade, spots running down them; its shadow on the felt to the right;
    stepped down the ramp at the frame's edges. Cool and quiet, it
    balances the six's red and gives the near ground a layer.
  - Depth: the six and the chips in front; the one, the pool and the
    centre box in the middle; the wall, the rails and the flash behind;
    the room's dark at the back. The key light from the top left; every
    shadow agrees.
  Palette (11 own + cream, grey, black, red):
    navy0 steel ........... the room; the lattice in shade (grey its lit
                            faces); the chips
    felt0 felt1 felt2 ..... the table (black under them), the layout, the shadows
    wine .................. the leather rails, the dice's shaded side and
                            thickness, the shadows' hearts, the flash's rim,
                            the trails' tails, the title's depth
    ember rose ............ the dice's lit tops and glow, creases and hot
                            corners, the flash's star, the trails, sparks
    gold0 gold1 gold2 ..... the title's own (cream its bevel and glints)
    fixed: red (the number faces, lit pyramids, the title's first depth
    step), cream (pips, the flash's core, glints), black (outline, void).
  Font: luBIS24 from u8g2 (the X11 bitmap of Bigelow & Holmes' Lucida Sans
  Bold Italic; the scout records its terms as "see u8g2's font licence
  list", which points to the X11 B&H notice: royalty-free use with the
  notice kept). Not a clear-terms face: it belongs in the credits table of
  docs/cover-art.md, checked before a release (tools/art/title.txt keeps
  the header). The S is kerned a pixel right, off the P's depth.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import numpy as np  # noqa: E402
import artkit as ak  # noqa: E402
from artkit import render3d as R  # noqa: E402

TITLE = HERE / "art" / "title.txt"

YY, XX = np.mgrid[0:128, 0:128]
X1, Y1 = XX + 0.5, YY + 0.5
BAY = ak.paint.BAYER                                   # the 4x4 thresholds

PAL = {
    "navy0": "#0C1230", "steel": "#2E3E66",
    "felt0": "#06301E", "felt1": "#0C5C34", "felt2": "#1E9048",
    "wine": "#5C0618", "rose": "#FF8058",
    "ember": "#FF4C2C",
    "gold0": "#8E4A06", "gold1": "#E8A020", "gold2": "#FFE67A",
}
DICE = ["black", "wine", "red", "ember", "rose", "cream"]
FELT = ["black", "felt0", "felt1", "felt2"]
COOL = ["black", "navy0", "steel", "grey"]

# ---- the camera: low at the near end of the table, looking down its length
# at the far end (the game's dice cam, lower and wider)
CAM = R.Camera((0, 0.46, 2.1), (0, 0.1, 0), fov=56, shift=(0, -14))
KEY = np.array([-0.55, 0.75, 0.45])
KEY = KEY / np.linalg.norm(KEY)
KEY2 = np.array([-0.62, -0.78])                        # the key as the picture shows it (up left)
KEY_EDGE = 0.25                                         # an edge facing it more than this catches a line of light

# ---- the table (world units: the felt at y 0, the far wall's face at z 0,
# the table running toward the camera in +z)
W = 0.52                                    # the felt's half width (to the side rails)
WALL = 0.26                                 # the pyramid rubber's height
RAIL = 0.35                                 # the rails' height (the far one sits on the rubber)
THICK = 0.14                                # the rails' width
ROLL = 0.07                                 # the side rails' padded roll, under their tops
FLASH_H = 0.12                              # the impact's height on the far wall
PYR = (8, 6)                                # the rubber's pyramids on the picture (px)
RINGS = (12, 22)                            # the flash's light on them: red, then wine (px)
STAR = ((9.5, 13, 9.5, 13), 5.5, 2.8, 3.2)  # the flash: long spikes (up, right, down, left), short, valleys, core
SPARKS = [((-11, -4), (-21, -9), -1.0), ((12, -4), (22, -9), -1.0), ((-12, 5), (-20, 8), 1.0), ((12, 5), (21, 8), 1.0)]   # from the flash (px)

# the dice: centre on the picture, distance, size, the face toward us (and
# where it looks, relative to the line of sight: x right, y up, z back at
# the camera), spun about it
DIE2 = dict(at=(35, 73), dist=6.4, size=1.0, face=1, dir=(-0.4, -0.5, 1.0), spin=24)
HERO = dict(at=(92, 88), dist=3.9, size=1.0, face=6, dir=(-0.5, -0.85, 1.0), spin=10)
PIP_R = 0.08
S = 0.27                                     # pip spacing (die edge 1)
PIPS = {1: [(0, 0)], 2: [(-S, -S), (S, S)], 3: [(-S, -S), (0, 0), (S, S)],
        4: [(-S, -S), (S, -S), (-S, S), (S, S)], 5: [(-S, -S), (S, -S), (-S, S), (S, S), (0, 0)],
        6: [(-S, -S), (-S, 0), (-S, S), (S, -S), (S, 0), (S, S)]}
FACES = {6: ((0, 1, 0), (1, 0, 0), (0, 0, 1)), 1: ((0, -1, 0), (1, 0, 0), (0, 0, 1)),     # normal, u, v
         2: ((0, 0, 1), (1, 0, 0), (0, 1, 0)), 5: ((0, 0, -1), (1, 0, 0), (0, 1, 0)),
         3: ((1, 0, 0), (0, 0, 1), (0, 1, 0)), 4: ((-1, 0, 0), (0, 0, 1), (0, 1, 0))}
# the light through the glass along a face's far edges, in pixel rows in
# from the edge: solid, 50%, 25% (the bottom edges; the right ones thinner)
GLOW_DOWN = (5, 6, 7)
GLOW_RIGHT = (3, 4, 4)
HOT = (4.5, 6.5)                               # the glow's hot spot at the lowest corner: solid, 50% (px)
CREASE = (None, "rose", "red")                 # a lit crease where faces meet: on the number face, the side
FIELD = (0.42, 0.62)                                                   # the layout: the field's lines (z)
PROPS = (-0.2, 0.2, 0.9, 1.45)                                         # the centre's box: x0, x1, z0, z1
TRAILS = [((-0.5, 0.72, 1.6, -4.0), (0.45, 0.6, 1.4, -2.5)),          # (across, reach, r0, bow) per die
          ((-0.55, 0.76, 1.6, 5.0), (0.38, 0.68, 2.0, 3.5), (0.76, 0.58, 1.4, 2.0))]
# shadows on the felt (the dice are in the air): centre, radii
SHADOWS = [(119, 113, 12, 3.4), (49, 99, 13, 3.0)]
# a stack of blue chips in the near left corner (a bet down: depth, and the
# cool against the dice's red): where it stands on the felt (world x, z),
# a chip's radius and thickness, each chip's nudge (x, z) and turn (degrees)
CHIPS = dict(at=(-0.29, 1.52), r=0.076, h=0.021,
             stack=[(0.0, 0.0, 0), (0.0, 0.0, 14), (0.0, 0.0, 31)])
CHIP_SHADOW = (24, 114, 12, 5)                                          # the stack's on the felt, to its right
SPOTS = 8                                                               # edge spots round a chip
SPOT_W = 0.34                                                           # each spot's share of its turn
GLARE = ((0.2, 0.6, 2.5), (0.4, 0.75, 2.5))                          # the tops' inner glare: from, to (along the lit edge), inset (px)
TITLE_Y = 4
TITLE_ROWS = ["gold2"] * 9 + ["gold1"] * 3 + ["gold0"] + ["gold2"] * 4 + ["gold1"] * 6 + ["gold0"] * 2
TITLE_GLINTS = [(17, 2, (2, 3, 2, 1)), (115, 1, (3, 3, 3, 2))]   # on the mask: x, y, arms (left, right, up, down)


# ---- the table ------------------------------------------------------------------------

def table():
    """Per pixel, what its ray meets first and where: kind 0 the room, 1 the
    far rail's face, 2 a rail's top, 3 the far wall's rubber, 4 a side
    rail's inner face, 5 the felt; the hit point (x, y, z)."""
    o, d = CAM.rays(X1.reshape(-1).astype(np.float64), Y1.reshape(-1).astype(np.float64))
    n = d.shape[0]
    best = np.full(n, np.inf)
    kind = np.zeros(n, int)
    hit = np.zeros((n, 3))

    def take(t, ok, k):
        ok = ok & (t > 1e-6) & (t < best)
        best[ok] = t[ok]
        kind[ok] = k
        hit[ok] = o[ok] + d[ok] * t[ok, None]

    def at(t):
        return o + d * t[:, None]
    dz = np.where(np.abs(d[:, 2]) < 1e-9, -1e-9, d[:, 2])
    dy = np.where(np.abs(d[:, 1]) < 1e-9, -1e-9, d[:, 1])
    dx = np.where(np.abs(d[:, 0]) < 1e-9, 1e-9, d[:, 0])
    t = -o[:, 2] / dz
    p = at(t)
    take(t, (np.abs(p[:, 0]) <= W) & (p[:, 1] >= 0) & (p[:, 1] <= WALL), 3)
    take(t, (np.abs(p[:, 0]) <= W + THICK) & (p[:, 1] > WALL) & (p[:, 1] <= RAIL), 1)
    t = (RAIL - o[:, 1]) / dy
    p = at(t)
    far = (p[:, 2] >= -THICK) & (p[:, 2] <= 0) & (np.abs(p[:, 0]) <= W + THICK)
    side = (np.abs(p[:, 0]) >= W) & (np.abs(p[:, 0]) <= W + THICK) & (p[:, 2] >= -THICK)
    take(t, far | side, 2)
    for sg in (-1, 1):
        t = (sg * W - o[:, 0]) / dx
        p = at(t)
        take(t, (p[:, 1] >= 0) & (p[:, 1] <= RAIL) & (p[:, 2] >= 0), 4)
    t = -o[:, 1] / dy
    p = at(t)
    take(t, (np.abs(p[:, 0]) < W) & (p[:, 2] >= 0), 5)
    sh = (128, 128)
    return dict(kind=kind.reshape(sh), x=hit[:, 0].reshape(sh), y=hit[:, 1].reshape(sh), z=hit[:, 2].reshape(sh))


def project(p):
    return np.array(CAM.project(np.asarray(p, float)))


# ---- the dice's geometry -------------------------------------------------------------

def world_at(sx, sy, dist):
    o, d = CAM.rays(np.array([sx], float), np.array([sy], float))
    return o[0] + d[0] * dist


def view_dir(v, pos):
    """A direction given relative to the line of sight to `pos`: z straight
    back at the camera, x to the picture's right, y up."""
    z = CAM.pos - pos
    z /= np.linalg.norm(z)
    x = np.cross(CAM.u, z)
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    v = np.asarray(v, float)
    w = v[0] * x + v[1] * y + v[2] * z
    return w / np.linalg.norm(w)


def orient(face, d, spin):
    """A rotation (local -> world) turning `face`'s normal to d and spinning
    it `spin` degrees about it."""
    n_l, u_l, v_l = (np.array(a, float) for a in FACES[face])
    L = np.stack([n_l, u_l, v_l], 1)
    a = CAM.u - (CAM.u @ d) * d
    a /= np.linalg.norm(a)
    b = np.cross(d, a)
    t = np.radians(spin)
    a, b = np.cos(t) * a + np.sin(t) * b, -np.sin(t) * a + np.cos(t) * b
    Wm = np.stack([d, a, b], 1)
    if np.linalg.det(Wm) * np.linalg.det(L) < 0:
        Wm[:, 2] = -Wm[:, 2]
    return Wm @ L.T


def inside(pts):
    """The pixels whose centres lie inside a polygon."""
    return ak.polygon((X1, Y1), [tuple(p) for p in pts]) < 0


def cube(D):
    """A die as a sharp-edged cube in perspective: its visible faces (quad,
    pixel mask, normal, axes, its edges on the picture), ranked by how lit
    they are, and its silhouette. Each edge knows its outward normal on the
    picture, every pixel's row counted in from it (0 the edge's own pixel
    line: one pixel per column, or per row, so a clean line), whether it is
    on the silhouette, and whether it faces the key."""
    size = D["size"]
    pos = world_at(*D["at"], D["dist"])
    rot = orient(D["face"], view_dir(D["dir"], pos), D["spin"])
    faces = {}
    for f, (nl, ul, vl) in FACES.items():
        n, u, v = (rot @ np.array(a, float) for a in (nl, ul, vl))
        c = pos + n * 0.5 * size
        if n @ (CAM.pos - c) <= 0:
            continue
        q = [np.array(CAM.project(c + (su * u + sv * v) * 0.5 * size)) for su, sv in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
        faces[f] = dict(q=q, n=n, u=u, v=v, c=c, m=inside(q), lit=float(n @ KEY))
    sil = np.zeros((128, 128), bool)
    for F in faces.values():
        sil |= F["m"]
    for F in faces.values():
        q = F["q"]
        mid = sum(q) / 4
        F["edges"] = []
        for k in range(4):
            a, b = q[k], q[(k + 1) % 4]
            e = b - a
            nrm = np.array([e[1], -e[0]]) / np.hypot(*e)
            if nrm @ ((a + b) / 2 - mid) < 0:
                nrm = -nrm
            dist = -((X1 - a[0]) * nrm[0] + (Y1 - a[1]) * nrm[1])
            m2 = (a + b) / 2 + nrm * 2.0
            outer = not sil[int(np.clip(m2[1], 0, 127)), int(np.clip(m2[0], 0, 127))]
            F["edges"].append(dict(a=a, b=b, n=nrm, row=np.floor(dist / max(abs(nrm[0]), abs(nrm[1]))),
                                   outer=outer, key=float(nrm @ KEY2)))
    rank = sorted(faces, key=lambda f: -faces[f]["lit"])
    return dict(pos=pos, rot=rot, size=size, faces=faces, rank=rank, sil=sil)


# ---- painting the dice ----------------------------------------------------------------

def pip_stamps(C, F, f, r):
    """A face's pips as round stamps, evenly spaced (the perspective's pip
    grid rounded to whole pixels), each the size the perspective gives it on
    average, a pixel out of round at most; then a size smaller, and so on.
    Yields the candidate sets, biggest first."""
    c0 = np.array(CAM.project(F["c"]))
    U = np.array(CAM.project(F["c"] + F["u"] * S * C["size"])) - c0
    V = np.array(CAM.project(F["c"] + F["v"] * S * C["size"])) - c0
    ring = np.array([CAM.project(F["c"] + r * C["size"] * (np.cos(t) * F["u"] + np.sin(t) * F["v"]))
                     for t in np.linspace(0, 2 * np.pi, 32, endpoint=False)])
    w, h = int(round(np.ptp(ring[:, 0]))), int(round(np.ptp(ring[:, 1])))
    w, h = max(1, min(w, h + 2)), max(1, min(h, w + 2))
    Ui, Vi = np.round(U), np.round(V)
    for k in range(4):
        ww, hh = w - k, h - k
        if min(ww, hh) < 3:
            return
        tpl = ak.pip_template(ww, hh)
        ox, oy = c0[0] - ww / 2, c0[1] - hh / 2
        yield [ak.place(tpl, int(round(ox + a_ / S * Ui[0] + b_ / S * Vi[0])), int(round(oy + a_ / S * Ui[1] + b_ / S * Vi[1])))
               for a_, b_ in PIPS[f]]


def nudge(m, inner, mid, steps=2):
    """A pip moved a pixel at a time toward the face's middle (at most
    `steps`) until it lies wholly inside `inner`."""
    for _ in range(steps):
        if (m & ~inner).sum() == 0:
            break
        ys, xs = np.nonzero(m)
        ex, ey = mid[0] - xs.mean(), mid[1] - ys.mean()
        m = ak.shift(m, int(np.sign(ex)) if abs(ex) > 0.5 else 0, int(np.sign(ey)) if abs(ey) > 0.5 else 0)
    return m


def paint_die(pic, C, glare, pip_scale=None):
    """A red glass die, face by face on the dice ramp: the lit top ember,
    the number face red, the shaded side wine, each one flat. The light that
    came in by the top glows out along each face's far edges (down and
    right) a step lighter: solid rows by the edge, then one 50% row; the
    silhouette's far edge itself a step darker (the glass's thickness), the
    black outline outside. Every edge that faces the key is one clean line:
    cream to rose on the top's back edges, a lit crease where faces meet."""
    faces, rank = C["faces"], C["rank"]
    base = dict(zip(rank, (3, 2, 1)))
    lvl = {}
    allq = np.array([q for F in faces.values() for q in F["q"]])
    low = allq[np.argmax(allq[:, 1])]                     # the die's lowest corner: the light pools there
    hot = np.hypot(X1 - low[0], (Y1 - low[1]) * 1.2)
    for f in rank:
        F = faces[f]
        b = base[f]
        i = np.full((128, 128), b)
        if f != rank[0]:
            for E in F["edges"]:
                r, (nx, ny) = E["row"], E["n"]
                if not E["outer"]:
                    continue
                if ny > 0.6:
                    prof = GLOW_DOWN
                elif nx > 0.55:
                    prof = GLOW_RIGHT
                else:
                    continue
                g = (r < prof[0]) | ((r < prof[1]) & ak.checker()) | ((r < prof[2]) & (BAY < 0.25))
                i = np.where(g, b + 1, i)
            near_low = any(np.hypot(*(q - low)) < 0.5 for q in F["q"])
            if near_low:
                i = np.where(hot < HOT[0], b + 2, np.where((hot < HOT[1]) & ak.checker(), b + 2, i))
            for E in F["edges"]:
                r, (nx, ny) = E["row"], E["n"]
                if E["outer"] and (ny > 0.6 or nx > 0.55):
                    i = np.where(r < 1, max(b - 1, 1), i)     # the glass's thickness
        lvl[f] = i
        ak.put_levels(pic, F["m"], i, DICE)
    # the edges facing the key: one clean line each
    for f in rank:
        F = faces[f]
        b = base[f]
        for E in F["edges"]:
            if E["key"] < KEY_EDGE:
                continue
            line = F["m"] & (E["row"] == 0)
            if f == rank[0]:
                if not E["outer"]:
                    continue
                a, bb = E["a"], E["b"]
                t = ((X1 - a[0]) * (bb - a)[0] + (Y1 - a[1]) * (bb - a)[1]) / max(np.hypot(*(bb - a)) ** 2, 1e-6)
                if a @ KEY2 < bb @ KEY2:
                    t = 1 - t
                pic.put(line, "rose")
                pic.put(line & (t > 0.4), "cream")
            else:
                pic.put(line, CREASE[rank.index(f)] if not E["outer"] else DICE[min(b + 2, 4)])
    # pips: cream on the lit faces, red on the shaded one, only where every
    # pip keeps a pixel of face round it and its neighbours' too
    real = np.zeros((128, 128), bool)
    for f in rank:
        F = faces[f]
        inner = ak.erode(F["m"], 1, diag=True)
        r = PIP_R * (pip_scale if (pip_scale and f == 1) else 1.0)
        ys_, xs_ = np.nonzero(inner)
        mid = np.array([xs_.mean(), ys_.mean()]) if len(xs_) else np.zeros(2)
        for stamps in pip_stamps(C, F, f, r):
            stamps = [nudge(m, inner, mid) for m in stamps]
            ok = all((m & ~inner).sum() == 0 for m in stamps)
            ok &= not any((ak.dilate(a, 1, diag=True) & bb).any() for j, a in enumerate(stamps) for bb in stamps[j + 1:])
            if ok:
                for m in stamps:
                    pic.put(m, "cream" if f != rank[-1] else "red")
                    real |= m
                break
    # the glare: a second, shorter line inside the top's lit back edge, a
    # couple of pixels in (glass shows its edge twice), cream at the corner
    # end tapering to rose, a pixel clear of the pips
    if glare:
        T = faces[rank[0]]
        E = max((E for E in T["edges"] if E["outer"]), key=lambda E: E["key"] * np.hypot(*(E["b"] - E["a"])))
        a, bb = E["a"], E["b"]
        if a @ KEY2 < bb @ KEY2:
            a, bb = bb, a                                   # a: the end nearer the key
        t0, t1, inset = glare
        p0 = a + (bb - a) * t0 - E["n"] * inset
        p1 = a + (bb - a) * t1 - E["n"] * inset
        ak.ink(pic, [tuple(p0), tuple(p1)], "cream", where=ak.erode(T["m"], 2, diag=True) & ~ak.dilate(real, 2, diag=True),
               colours=[("cream", 0.4), ("rose", 1.0)])
    return lvl


def pips_of(pic, C):
    """A die's cream pixels away from its edges: its pips."""
    return pic.where("cream") & ak.erode(C["sil"], 2, diag=True)


def trail(pic, C, imp, specs, ok, cols, gap=2.5):
    """Speed lines from a die's trailing edge back along its path to the
    impact, bowing (the bounce's arc), tapering from r0 to a pixel. specs:
    (where across the die, -1..1; how far toward the impact, 0..1; r0; bow
    in px, to the right of the way back)."""
    imp = np.array(imp, float)
    ctr = np.array(CAM.project(C["pos"]))
    dv = imp - ctr
    dv /= np.linalg.norm(dv)
    pv = np.array([-dv[1], dv[0]])
    ys, xs = np.nonzero(C["sil"])
    rel = np.stack([xs + 0.5 - ctr[0], ys + 0.5 - ctr[1]], 1)
    half = np.abs(rel @ pv).max()
    out = np.zeros((128, 128), bool)
    for off, rch, r0, bow in specs:
        o = off * half
        on = np.abs(rel @ pv - o) < 1.0
        along = (rel @ dv)[on].max() if on.any() else 0
        root = ctr + pv * o + dv * (along + gap)
        end = root + rch * (imp - root)
        ctrl = (root + end) / 2 + pv * bow
        out |= ak.streak(pic, tuple(root), tuple(ctrl), tuple(end), r0, 0.45, ok=ok, cols=cols)
    return out


def chip_stack():
    """The chips, traced exactly (each a cylinder standing on the felt): per
    pixel the chip it shows (-1 none, counted from the bottom), whether on
    its top, the angle round it (degrees) and how far out (0..1) on a top,
    and the side's normal's light."""
    ss = 2
    c = (np.arange(128 * ss) + 0.5) / ss
    Xs, Ys = np.meshgrid(c, c)
    o, d = CAM.rays(Xs.reshape(-1), Ys.reshape(-1))
    n = d.shape[0]
    best = np.full(n, np.inf)
    cid = np.full(n, -1)
    top = np.zeros(n, bool)
    ang = np.zeros(n)
    rad = np.zeros(n)
    lit = np.zeros(n)
    x0, z0 = CHIPS["at"]
    r, h = CHIPS["r"], CHIPS["h"]
    for k, (dx, dz, turn) in enumerate(CHIPS["stack"]):
        cx, cz, y0 = x0 + dx, z0 + dz, k * h
        ox, oz = o[:, 0] - cx, o[:, 2] - cz
        a = d[:, 0] ** 2 + d[:, 2] ** 2
        b = 2 * (ox * d[:, 0] + oz * d[:, 2])
        cc = ox ** 2 + oz ** 2 - r * r
        disc = b * b - 4 * a * cc
        ok = disc >= 0
        t = np.where(ok, (-b - np.sqrt(np.maximum(disc, 0))) / (2 * a), np.inf)
        y = o[:, 1] + d[:, 1] * t
        ok &= (t > 0) & (y >= y0) & (y <= y0 + h) & (t < best)
        px, pz = ox + d[:, 0] * t, oz + d[:, 2] * t
        best = np.where(ok, t, best)
        cid = np.where(ok, k, cid)
        top = np.where(ok, False, top)
        with np.errstate(invalid="ignore"):
            th = np.degrees(np.arctan2(pz, px))
        ang = np.where(ok, np.nan_to_num(th + turn) % 360, ang)
        with np.errstate(invalid="ignore"):
            lw = (px * KEY[0] + pz * KEY[2]) / r
        lit = np.where(ok, lw, lit)
        t2 = (y0 + h - o[:, 1]) / np.where(np.abs(d[:, 1]) < 1e-9, -1e-9, d[:, 1])
        qx, qz = ox + d[:, 0] * t2, oz + d[:, 2] * t2
        rr = np.hypot(qx, qz) / r
        ok2 = (t2 > 0) & (rr <= 1) & (t2 < best)
        best = np.where(ok2, t2, best)
        cid = np.where(ok2, k, cid)
        top = np.where(ok2, True, top)
        ang = np.where(ok2, (np.degrees(np.arctan2(qz, qx)) + turn) % 360, ang)
        rad = np.where(ok2, rr, rad)
    def px(a, f):
        return a.reshape(128, ss, 128, ss).transpose(0, 2, 1, 3).reshape(128, 128, ss * ss)
    ids = px(cid, None)
    who = np.full((128, 128), -1)
    cnt = (ids == -1).sum(-1)
    for k in range(len(CHIPS["stack"])):
        m = (ids == k).sum(-1)
        who = np.where(m > cnt, k, who)
        cnt = np.maximum(m, cnt)
    j = 0                                                       # the sample nearest each pixel's centre
    return dict(id=who, top=px(top, None)[..., j], ang=px(ang, None)[..., j], rad=px(rad, None)[..., j],
                lit=px(lit, None)[..., j])


def paint_chips(pic, Ch):
    """Blue chips: steel tops with a navy inlay ring, cream edge spots and
    a grey rim where the top's edge meets the key; their sides lit by the
    key (grey, steel, navy round into the shade), the spots running down
    them (cream in the light, grey, then steel in the shade), a navy line
    between chips on the shaded side, a black outline."""
    who = Ch["id"]
    m = who >= 0
    seg = 360 / SPOTS
    spot = (Ch["ang"] % seg) < seg * SPOT_W
    topm = m & Ch["top"]
    side = m & ~Ch["top"]
    L = Ch["lit"]
    lv = np.where(L > 0.45, 3, np.where(L > -0.1, 2, np.where(L > -0.6, 1, 0)))
    ak.put_levels(pic, side, lv, COOL)
    pic.put(side & spot & (lv >= 2), "cream")
    pic.put(side & spot & (lv == 1), "grey")
    pic.put(side & spot & (lv == 0), "steel")
    for k in range(len(CHIPS["stack"]) - 1):
        mk = side & (who == k)
        pic.put(mk & ak.shift(who > k, 0, 1) & (lv <= 1), "black")
        pic.put(mk & ak.shift(who > k, 0, 1) & (lv == 2), "navy0")
    pic.put(topm, "steel")
    pic.put(topm & (np.abs(Ch["rad"] - 0.6) < 0.08), "navy0")
    pic.put(topm & (Ch["rad"] < 0.5) & (Ch["ang"] > 150) & (Ch["ang"] < 290), "grey")
    pic.put(topm & (Ch["rad"] > 0.78) & spot, "cream")
    rim_ = topm & ak.shift(~m, 0, 1)
    pic.put(rim_ & ~spot, "grey")
    pic.put(ak.dilate(m, 1, diag=True) & ~m, "black")
    # the frame's edges stay dark: a step down the ramp within 3 px of
    # them, two within 1
    edge = np.minimum(np.minimum(XX, 127 - XX), np.minimum(YY, 127 - YY))
    down = {"cream": "grey", "grey": "steel", "steel": "navy0", "navy0": "black"}
    for lim in (3, 1):
        for a in ("navy0", "steel", "grey", "cream"):
            pic.put(m & (edge < lim) & pic.where(a), down[a])
    return m


# ---- the picture ----------------------------------------------------------------------

def draw():
    P = ak.Palette(PAL, ramps=[DICE, FELT, COOL, ["gold0", "gold1", "gold2", "cream"]])
    pic = ak.Picture.blank(P, "navy0")
    T = table()
    kind = T["kind"]
    X, Y, Z = T["x"], T["y"], T["z"]
    c2, c1 = cube(DIE2), cube(HERO)
    dice = c2["sil"] | c1["sil"]
    imp = project((0, FLASH_H, 0))
    iy = int(np.floor(imp[1]))

    # ---- the room: navy behind the title, black at the corners and round
    # the table
    room = kind == 0
    v = np.hypot((X1 - 64) / 70, (Y1 - 26) / 34)
    pic.put(room, "black")
    pic.put(room & (v < 1.0), "navy0")

    # ---- the far wall: pyramid rubber, a diamond lattice (PYR px), each
    # pyramid lit whole: its level by where it is (the lamp over the middle),
    # a step per face by where it faces (the key from the top left: up-left
    # a step up, down-right two down)
    wall = kind == 3
    top_w = int(np.nonzero(wall.any(axis=1))[0].min())
    pw, ph = PYR
    u = (X1 - 64) / pw
    vv = (Y1 - top_w) / ph
    best = np.full((128, 128), 1e9)
    du_ = np.zeros((128, 128))
    dv_ = np.zeros((128, 128))
    cu = np.zeros((128, 128))
    cvv = np.zeros((128, 128))
    for o in (0.0, 0.5):
        gu = np.round(u - o) + o
        gv = np.round(vv - 0.5 - o) + 0.5 + o
        du, dv = u - gu, vv - gv
        d1 = np.abs(du) + np.abs(dv)
        b = d1 < best
        best = np.where(b, d1, best)
        du_ = np.where(b, du, du_)
        dv_ = np.where(b, dv, dv_)
        cu = np.where(b, gu, cu)
        cvv = np.where(b, gv, cvv)
    px_c, py_c = 64 + cu * pw, top_w + cvv * ph            # each pyramid's centre on the picture
    face = np.select([(du_ < 0) & (dv_ < 0), (du_ > 0) & (dv_ < 0), (du_ < 0) & (dv_ > 0)], [1.0, 0.0, -1.0], -2.0)
    span = np.clip(1 - np.abs(px_c - 64) / 36, 0, 1)
    lamp = 0.8 + 2.2 * span ** 0.9 - np.where(py_c < top_w + 1, 0.8, 0.0)
    cool = np.clip(np.floor(lamp + face), 0, 3).astype(int)
    ak.put_levels(pic, wall, cool, COOL)
    # round the impact the faces turned to the flash catch it: red in the
    # first ring, wine in the next (the rest keep the lamp's light)
    fn = {1.0: (-1, -1), 0.0: (1, -1), -1.0: (-1, 1), -2.0: (1, 1)}
    nx_ = np.select([face == k for k in fn], [fn[k][0] for k in fn])
    ny_ = np.select([face == k for k in fn], [fn[k][1] for k in fn])
    ex, ey = imp[0] - px_c, imp[1] - py_c
    dd = np.hypot(ex, ey * 1.5)
    tw = (nx_ * ex + ny_ * ey) / np.maximum(np.hypot(ex, ey), 1e-6) / 1.414
    pic.put(wall & (tw > 0.2) & (dd < RINGS[1]) & (dd >= RINGS[0]), "wine")
    pic.put(wall & (tw > 0.2) & (dd < RINGS[0]), "red")

    # ---- the rails: black leather, padded. The far one's roll: a line of
    # wine along its top with a short red-to-rose sheen over the flash, its
    # body wine fading to black at the ends, its foot black with the flash's
    # wine on its underside; its shadow lies on the rubber's top row. The
    # side rails' inner faces wine by the far end (the right one, facing the
    # key, more), black toward us; their tops a line of red to wine, fading
    rf = kind == 1
    topm = kind == 2
    side = kind == 4
    pic.put(rf | topm | side, "black")
    rows_rf = np.nonzero(rf.any(axis=1))[0]
    r0_, r1_ = int(rows_rf.min()), int(rows_rf.max())
    span_r = np.abs(X1 - imp[0])
    pic.put(rf & (YY <= r0_ + 2) & (span_r < 34 - (YY - r0_) * 4), "wine")
    pic.put(rf & (YY == r0_) & (span_r < 13), "red")
    pic.put(rf & (YY == r0_) & (np.abs(X1 - imp[0] + 3) < 3.5), "rose")
    pic.put(rf & (YY == r1_) & (span_r < 8), "wine")
    pic.put(wall & ak.shift(rf, 0, 1), "black")                 # the rail's shadow on the rubber
    pic.put(side & (Y > RAIL - ROLL), "wine")
    for sg in (-1, 1):
        pts = [project((sg * W, RAIL - 0.01, z)) for z in np.linspace(0.0, 2.4, 80)]
        ak.ink(pic, [tuple(q) for q in pts], "wine", where=side | topm,
               colours=[("rose", 0.03), ("red", 0.12 if sg > 0 else 0.08), ("wine", 0.5 if sg > 0 else 0.35), (None, 1.0)])

    # ---- the felt: a pool of light under the dice, the walls' shadow along
    # its edges, a glow from the flash at the far wall's foot; the layout's
    # lines a step lighter
    felt = kind == 5
    pool = np.hypot((X1 - 62) / 78, (Y1 - 88) / 44)
    nz_ = ak.noise((X1, Y1), 14, seed=5, octaves=2) - 0.5
    fl = np.interp(np.clip(pool + 0.08 * nz_, 0, 1.5), [0, 0.45, 0.8, 1.05, 1.5], [3.0, 2.6, 1.7, 1.0, 0.3])
    fl -= np.clip(1 - (X + W) / 0.1, 0, 1) * 1.0
    fl -= np.clip(1 - (W - X) / 0.06, 0, 1) * 0.5
    fl -= np.clip(1 - Z / 0.06, 0, 1) * 0.8
    glow = np.hypot((X1 - imp[0]) / 22, (Y1 - imp[1] - 7) / 5)
    fl = np.maximum(fl, (1.15 - glow) * 2.8)
    fl -= np.clip((Y1 - 118) / 10, 0, 1) * 1.2
    fl -= np.clip((np.abs(X1 - 64) - 57) / 6, 0, 1) * 1.2                 # the frame's edges dark
    shade = np.zeros((128, 128))
    for sx, sy, rx, ry in SHADOWS + [CHIP_SHADOW]:
        e = np.hypot((X1 - sx) / rx, (Y1 - sy) / ry)
        shade = np.maximum(shade, np.clip((1.15 - e) / 0.4, 0, 1) * 0.85)
    fl = ak.terrace(np.clip(fl - 2.0 * shade, 0, 3), 0.25)
    fl = np.where(shade > 0.6, np.minimum(fl, 1.0), fl)             # the shadows' cores felt0, never black
    ak.by_level(pic, fl, FELT, felt)
    # the layout: the pass line's band round the far end, in perspective
    lines = np.zeros((128, 128), bool)
    for inset, zc in ((0.07, 0.10), (0.15, 0.20)):
        r_ = 0.12
        pts = [(-W + inset, z) for z in np.linspace(2.4, zc + r_, 30)]
        pts += [(-W + inset + r_ - r_ * np.cos(a), zc + r_ - r_ * np.sin(a)) for a in np.linspace(0, np.pi / 2, 8)]
        pts += [(x, zc) for x in np.linspace(-W + inset + r_, W - inset - r_, 30)]
        pts += [(W - inset - r_ + r_ * np.sin(a), zc + r_ - r_ * np.cos(a)) for a in np.linspace(0, np.pi / 2, 8)]
        pts += [(W - inset, z) for z in np.linspace(zc + r_, 2.4, 30)]
        for x, y in ak.line_px([tuple(project((px_, 0, pz))) for px_, pz in pts]):
            if 0 <= x < 128 and 0 <= y < 128:
                lines[y, x] = True
    segs = [((-W + 0.15, z), (W - 0.15, z)) for z in FIELD]                  # the field
    x0_, x1_, z0_, z1_ = PROPS                                                # the centre's box
    segs += [((x0_, z0_), (x1_, z0_)), ((x0_, z1_), (x1_, z1_)), ((x0_, z0_), (x0_, z1_)), ((x1_, z0_), (x1_, z1_))]
    for (ax_, az), (bx_, bz) in segs:
        for x, y in ak.line_px([tuple(project((ax_, 0, az))), tuple(project((bx_, 0, bz)))]):
            if 0 <= x < 128 and 0 <= y < 128:
                lines[y, x] = True
    lines &= felt
    flr = np.round(fl).astype(int)
    ak.put_levels(pic, lines & (flr >= 1), np.where(flr >= 3, 2, flr + 1), FELT)   # a step lighter (darker on the brightest)
    # the shadows: a light through red glass, its heart wine
    for sx, sy, rx, ry in SHADOWS:
        e = np.hypot((X1 - sx + rx * 0.08) / (rx * 0.36), (Y1 - sy) / (ry * 0.62))
        pic.put(felt & (e < 1), "wine")

    # ---- the chips in the near corner, their shadow on the felt to the right
    Ch = chip_stack()
    paint_chips(pic, Ch)

    # ---- the impact: a cartoon flash, a cream core in a rose star (four
    # long spikes, four short), a wine rim and a black ring against the
    # lattice
    pts = []
    for k in range(16):
        ang = k * 22.5
        r = STAR[0][k // 4] if k % 4 == 0 else (STAR[1] if k % 2 == 0 else STAR[2])
        ca, sa = np.cos(np.radians(ang - 90)), np.sin(np.radians(ang - 90))
        pts.append((imp[0] + r * ca, imp[1] + r * sa))
    burst = inside(pts)
    corem = (np.abs(X1 - imp[0]) + np.abs(Y1 - imp[1])) < STAR[3]
    rim = ak.dilate(burst, 1, diag=True) & ~burst
    ring2 = ak.dilate(burst | rim, 1) & ~burst & ~rim
    pic.put(ring2 & (wall | rf), "black")
    pic.put(rim & ~felt, "wine")
    pic.put(rim & felt, "felt0")
    pic.put(burst, "rose")
    pic.put(corem, "cream")
    # sparks flung off it: short lines, red at the flash, cream at the head
    for (x0, y0), (x1, y1), bend in SPARKS:
        head, tail = np.array((imp[0] + x1, imp[1] + y1)), np.array((imp[0] + x0, imp[1] + y0))
        mid = (head + tail) / 2 + np.array((0, bend))
        ak.streak(pic, tuple(head), tuple(mid), tuple(tail), 0.95, 0.4, ok=~felt | (YY > iy),
                  cols=(("cream", 0.25), ("rose", 0.6), ("red", 1.0)))

    # ---- each die's path back to the wall: speed lines from its trailing edge
    ok = ~ak.dilate(dice, 1) & ~ak.dilate(burst | rim, 1) & (kind != 0)
    cols = (("rose", 0.25), ("ember", 0.45), ("red", 0.72), ("wine", 1.0))
    core = (("cream", 0.6), (None, 1.0))
    trails = np.zeros((128, 128), bool)
    for C, specs in ((c2, TRAILS[0]), (c1, TRAILS[1])):
        trails |= trail(pic, C, imp, specs, ok, cols)
        trail(pic, C, imp, [(o_, r_ * 0.45, 0.75, b_ * 0.45) for o_, r_, _, b_ in specs], ok, core)

    # ---- the dice, the far one first, outlined in black
    paint_die(pic, c2, GLARE[0], pip_scale=2.8)
    paint_die(pic, c1, GLARE[1])
    for c in (c2, c1):
        pic.put(ak.dilate(c["sil"], 1, diag=True) & ~c["sil"] & ~c1["sil"], "black")

    ak.despeckle(pic, need=4, passes=2, within=~(burst | rim) & ~dice)
    ak.despeckle(pic, need=3, passes=1, within=(wall | (felt & ak.dilate(trails, 1, diag=True))) & ~(burst | rim) & ~dice)

    # ---- the dice's glints: a star on each top's back corner, where the
    # lamp catches the edge, its arms kept a pixel clear of the pips
    for C, arms in ((c1, (2, 3, 3, 2)), (c2, (2, 2, 2, 2))):
        T_ = C["faces"][C["rank"][0]]
        q = np.array(T_["q"])
        j = int(np.argmin(q @ -KEY2))
        gx, gy = int(np.floor(q[j][0])) - 1, int(np.floor(q[j][1])) - 1
        clear = ~ak.dilate(pips_of(pic, C) | trails, 1, diag=True)
        arms = [next((k for k in range(n, -1, -1) if all(clear[gy + dy * i, gx + dx * i] for i in range(1, k + 1))), 0)
                for (dx, dy), n in zip(((-1, 0), (1, 0), (0, -1), (0, 1)), arms)]
        ak.glint(pic, gx, gy, arms=tuple(arms), tip="rose")

    # ---- the title: gold chrome, a red-to-wine depth, black outline and
    # shadow, a bevel on the outer contour, glints on the C and the S
    m = title_mask()
    tx, ty = ak.centred_x(m) - 2, TITLE_Y
    drawn = ak.title(pic, m, tx, ty, fill=["gold2", "gold1", "gold0"], hi=None, lo=None,
                     extrude=dict(dx=1, dy=1, depth=3, colours=["red", "wine", "wine"]),
                     shadow=dict(dx=1, dy=2, colour="black"))
    M = ak.place(m, tx, ty)
    top = int(np.nonzero(M.any(axis=1))[0].min())
    for j, c in enumerate(TITLE_ROWS):
        pic.put(M & (YY == top + j), c)
    ak.bevel_contour(pic, M, "cream", "gold0")
    pic.put(M & (YY < ty + 2) & pic.where("gold0"), "gold2")
    ak.despeckle(pic, need=3, within=ak.dilate(drawn["all"], 2), passes=2)
    for c in ("red", "wine"):                       # the depth's lone stair steps go to the outline
        ak.lonely(pic, c, drawn["extrude"], into="black")
    for gx, gy, arms in TITLE_GLINTS:
        ak.glint(pic, tx + gx, ty + gy, arms=arms, tip="gold2")
    return pic.image()


def title_mask():
    """The title's lettering, the S kerned a pixel right, off the P's depth."""
    m = ak.load_mask(TITLE)
    lab = ak.letters(m)
    last = lab[:, -3].max()
    S_ = lab == last
    m = np.pad(m, ((0, 0), (0, 1)))
    S_ = np.pad(S_, ((0, 0), (0, 1)))
    return (m & ~S_) | np.roll(S_, 1, axis=1)


def title_lines():
    """The title's lettering as drawn here, and its depth, for the title
    screen (tools/titleart.py: the game paints it in the house gold)."""
    return [dict(mask=title_mask(), depth=3, side="wine")]


if __name__ == "__main__":
    import boxart
    boxart.save(draw(), HERE.parent / "docs" / "cart.png")
