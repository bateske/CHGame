"""docs/cart.png, SD TO SERIAL's picture in the visual menu
(docs/cover-art.md). `chgame boxart` redraws it; edit this, not the PNG.

THE BRIEF
  Message: the website reads the card down the wire. The same hero shot as
  the SD card reader's cover (the apps are a set), recoloured into SD TO
  SERIAL's own screen palette: a red microSD slams into the glowing slot in
  the side of a CHGame, the handheld's screen is this app's instrument
  panel, and its USB cable carries the card's data away to a laptop in the
  dark whose browser shows the CHGame website.

  The look is the apps' secret-agent one (CHSDtoUSB's and CHStlView's: a
  gadget in a dark room, a grid floor, gold chrome lettering), but the glow,
  the grid, the slot light and both screens are this app's greens, from its
  dark glass up to its lime accent, instead of the reader's pure green:

      +----------------------------+
      |      S D   T O             |   the title: wide gold chrome on calm black
      |       S E R I A L          |
      |              .------.      |   black void; a lime glow hugs the device
      | ==[ red card ]#*|[panel ]  |   the camera at the slot's height
      | ==[    /     ]# |[      ] _|   the cable runs to a laptop at the horizon
      |   grid          |[ + oo ]~[]|  whose browser shows the website
      +----------------------------+

  - Focal point: the slot, where the card goes in. The card's contact end
    overlaps the side face and disappears into a lime-lit slit; a cream
    four-point star sits on the entry's top corner, a tight lime halo runs
    along the slit, and the card's edges turn lime where they meet it. The
    eye goes from the title to the star, back along the card, to the screen
    and out along the cable to the laptop.
  - The camera is low, at the slot's height, so the card's contacts and the
    screen's rows run nearly flat. Above the device is black void, calm
    under the title; the horizon runs behind the device's middle; the
    floor's grid converges to it, in the app's grey-greens.
  - The card is a hero-sized microSD, as wide as the device: red glossy
    plastic (the colour that breaks the green; the buttons share it), brass
    contacts, one cream reflection band, and a red smear off its trailing
    end: it is still moving into the slot.
  - The device (a CHGame handheld) stands on the floor turned 39 degrees,
    its slotted left side to the card, its front dark gunmetal. The screen
    is this app's panel in whole pixels: the status bar (a card, the state,
    the gold speed), the fill gauge, the graph (lime bars for data to the
    card, one mint cap for a read, a gold tick for verify), the strip, and
    two log rows (one coral tag). A lime rim of backlight runs down its right
    edge.
  - The USB cable leaves a port in the device's back, crosses the floor and
    plugs into a laptop at the horizon, whose lid glows: a browser window
    with a title bar, an address bar and the website's page. Two data pulses
    (a cream core, a lime comet tail) run along it toward the laptop: the
    card's bytes going to the browser.
  - Depth: the card in front, the device in the middle, the laptop far back;
    the grid brightens toward us and fades into haze at the horizon; the
    device's shadow lies on the floor behind it.
  - Light: the house key from the top left, the slot's lime as the second
    light, the glow round the device as a back light.

PALETTE (11 own + cream, grey, black, red) - SD TO SERIAL's screen palette
  g0 g1 g2 g3      the app's glass, grid, mid and lime (its graph's accent):
                   the glow, haze, grid, slot light, both screens, the pulses
  m0 m1            gunmetal (black, m0, m1, grey, cream): the device, the
                   cable, the plug, the laptop
  br0 br1          brass and rust: the contacts (brass over a rust lip), the
                   red card's shade, the screens' gold readouts
  gold0 gold1 gold2  the title's own: nothing else uses them
  red              the card and its smear, the buttons, the power light,
                   a log tag (the app's coral role)

FONT  title.txt (SD TO) and title2.txt (SERIAL): CHARSET-DNS_FONT 5 from the
      bmf collection, the face CHSDtoUSB's and CHStlView's titles use, so the
      three apps match. Set at the font's own size (64 and 67 px), gold chrome
      with dithered seams, a gold0-to-rust extrusion, a black drop shadow, a
      bevel, and a cream star on an outer corner of each line.
"""

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[9] / "tools"))     # the repository's tools/
import numpy as np  # noqa: E402
import artkit as ak  # noqa: E402
from artkit import render3d as R  # noqa: E402

TITLE = HERE / "art" / "title.txt"
TITLE2 = HERE / "art" / "title2.txt"
TITLE_Y = (4, 23)
TITLE_ROWS = ["gold2"] * 6 + ["gold1"] * 2 + ["gold0"] + ["gold2"] * 2 + ["gold1"] * 5   # chrome: sky, horizon, ground
TITLE_SEAMS = ((5, "gold1"), (11, "gold2"))     # rows (of the face) dithered half into the next band
TITLE_EXTRUDE = ["gold0", "br0"]
TITLE_GLINTS = ((1, 1, 3), (98, 1, 2))          # on a letter's outer corner, its arms out into the black: (x, y in the line, arm)

COL = {
    # SD TO SERIAL's own screen greens: dark glass, grey-green grid, mid, lime.
    "g0": "#0B2417", "g1": "#334433", "g2": "#66AA44", "g3": "#CCEE88",
    "m0": "#16201C", "m1": "#3E524A",
    "br0": "#62200E", "br1": "#C49A36",
    "gold0": "#7A3408", "gold1": "#E4991C", "gold2": "#FFE27A",
}
GREEN = ["black", "g0", "g1", "g2", "g3", "cream"]
METAL = ["black", "m0", "m1", "grey", "cream"]
RED = ["black", "br0", "red", "cream"]

YY, XX = np.mgrid[0:128, 0:128]
X1, Y1 = XX + 0.5, YY + 0.5

# ---- the scene (world: x right, y up, z toward us; the floor at y 0) ---------------------

CAM = dict(pos=(0.30, 1.22, 3.7), target=(0.30, 0.95, 0.0), fov=43, shift=(-7, 21))
DEV = dict(pos=(0.92, 0.85, -0.40), turn=39, half=(0.62, 0.85, 0.17), r=0.09)
SCREEN = (-0.47, 0.47, 0.10, 0.68)           # x0, x1, y0, y1 on the front (local)
BEZEL = 0.06
SLOT_Y = 0.34                                # the slot's centre on the left side (local y)
CARD = dict(len=1.20, wide=0.74, thick=0.05, insert=0.10)
NOTCH = (0.45, 0.05, 0.15)                   # the notch: where along (of L), its run (of L), its depth (of W)
PADS = 0.36                                  # the contacts' length (of L)
PAD = (-0.30, -0.42)                         # the cross pad's centre (local)
BUTTONS = [(0.04, -0.44), (0.36, -0.24)]     # the red buttons' centres
PILLS = [(-0.10, -0.70), (0.10, -0.70)]      # start / select
GRILLE = (0.36, -0.66)                       # the speaker's slots
PORT = (0.25, -0.70)                         # the USB-C port in the back (local x, y)
CABLE_R = 0.05
CABLE = [(1.40, 0.05, -0.85), (2.20, 0.05, -1.60)]   # its path on the floor to the laptop (world): from, a quadratic's control
LAPTOP = dict(pos=(3.25, 0.0, -4.60), turn=24, tilt=14, base=(0.42, 0.022, 0.29), lid=(0.42, 0.28, 0.018))
KEY = np.array([-0.55, 0.75, 0.45])
KEY = KEY / np.linalg.norm(KEY)
GRID = 0.5                                   # the floor's grid pitch

GLOW = (0, 4, 12, 1.45)                      # the backlight round the device: -, half-way (px), reach (px), level
CALM = (50, 60)                              # rows over which the void's glow dies away under the title
HAZE = ([6.0, 11.0, 28.0, 90.0], [0.0, 0.5, 0.95, 1.35])  # the floor's haze by distance (world): levels
PULSES = [2.20, 3.00]                       # data on the cable (arc length from the device's far side)
GRAPH = [0.55, 0.80, 0.45, 0.90, 0.70, 0.95, 0.75, 0.88]   # the graph's bars (of its height)
WRITES = (6, 7)                              # the bars that are writes (amber)
GLOSS = (0.36, 0.44)                         # the reflection band across the card's face (q), its cream core in the middle
SMEAR = [(0.88, 12, 1.1), (0.62, 19, 1.2), (0.34, 9, 1.0), (0.06, 23, 1.3), (-0.22, 14, 1.1), (-0.48, 20, 1.2),
         (-0.76, 11, 1.0)]                   # the red smear off its trailing end: across it (of W/2), length, root radius (px)


def card_outline(L, W):
    """The microSD's outline in its own plane (u along its length, from the
    trailing end at -L/2 to the contacts at +L/2; v across it, up): a step
    in its lower long side, the contact end the narrower."""
    a, b = L / 2, W / 2
    u0 = -a + NOTCH[0] * L
    s = NOTCH[2] * W
    return [(-a, -b), (u0, -b), (u0 + NOTCH[1] * L, -b + s), (a, -b + s), (a, b), (-a, b)]


def catmull(pts, n):
    """A Catmull-Rom curve through the points, n samples a span."""
    pts = [np.asarray(p, float) for p in pts]
    pts = [2 * pts[0] - pts[1]] + pts + [2 * pts[-1] - pts[-2]]
    out = []
    for i in range(1, len(pts) - 2):
        a, b, c, d = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * (2 * b + (c - a) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (3 * b - a - 3 * c + d) * t ** 3))
    out.append(pts[-2])
    return np.array(out)


def camera():
    return R.Camera(CAM["pos"], CAM["target"], fov=CAM["fov"], shift=CAM["shift"])


def scene():
    hx, hy, hz = DEV["half"]
    rot = R.rot_y(DEV["turn"])
    pos = np.asarray(DEV["pos"], float)
    body = R.prim(R.box((hx, hy, hz), DEV["r"]), 0)
    L, W, T = CARD["len"], CARD["wide"], CARD["thick"]
    pts = card_outline(L, W)
    cshape = R.prim(R.extrude(lambda x, y: ak.polygon((x, y), pts), T / 2), 1)
    lead = pos + rot @ np.array([-hx + CARD["insert"], SLOT_Y, 0.0])   # the contacts' edge, inside the slot
    crot = rot
    cpos = lead - crot @ np.array([L / 2, 0.0, 0.0])
    # the cable: out of a port in the back, down to the floor and away to
    # the right, to the laptop at the horizon; its plug in the laptop's side
    p0 = pos + rot @ np.array([PORT[0], PORT[1], -hz])
    p1 = pos + rot @ np.array([PORT[0], PORT[1], -hz - 0.14])
    p2 = pos + rot @ np.array([PORT[0] + 0.05, -hy + CABLE_R, -hz - 0.35])
    lrot = R.rot_y(LAPTOP["turn"])
    lpos = np.asarray(LAPTOP["pos"], float)
    bw, bh, bd = LAPTOP["base"]
    port = lpos + lrot @ np.array([-bw - 0.02, bh, 0.10])
    plug_out = lpos + lrot @ np.array([-bw - 0.10, bh, 0.10])
    a_, c_ = (np.array(q, float) for q in CABLE)
    e_ = plug_out.copy()
    e_[1] = CABLE_R
    bend = [(1 - t) ** 2 * a_ + 2 * (1 - t) * t * c_ + t * t * e_ for t in np.linspace(0, 1, 10)]
    cab = np.concatenate([catmull([p0, p1, p2, bend[0]], 6)[:-1], np.array(bend), [plug_out]])
    caps = [R.prim(R.capsule(tuple(a), tuple(b), CABLE_R), 2) for a, b in zip(cab[:-1], cab[1:])]
    plug = R.prim(R.capsule(tuple(plug_out), tuple(port), CABLE_R * 1.8), 3)
    base = R.xf(R.prim(R.box((bw, bh, bd), 0.02), 4), lpos + np.array([0, bh, 0]), lrot)
    lw, lh, lt = LAPTOP["lid"]
    lid_rot = lrot @ R.rot_x(-LAPTOP["tilt"])
    hinge = lpos + lrot @ np.array([0, 2 * bh, -bd])
    lid = R.xf(R.prim(R.box((lw, lh, lt), 0.02), 5), hinge + lid_rot @ np.array([0, lh, lt]), lid_rot)
    node = R.U(R.xf(body, pos, rot), R.xf(cshape, cpos, crot), plug, base, lid, *caps)
    return dict(node=node, rot=rot, pos=pos, cpos=cpos, crot=crot, cable=cab, lrot=lrot, lid_rot=lid_rot,
                hinge=hinge)


def geometry(cam, sc):
    """Per pixel: the material most of its rays hit (-1 none), and at the
    pixel's centre the normal and the hit point; where its ray meets the
    floor, and the shadow the scene throws there."""
    cv = ak.Canvas("#000000")
    mats = [R.Mat("#FFFFFF", spec=0.0)] * 6
    out = R.render(cv, sc["node"], cam, mats, ss=2, shadows=False, ao=False)
    mat = R.majority(out, cv.s)
    one = ak.Canvas("#000000", ss=1)
    o1 = R.render(one, sc["node"], cam, mats, lights=[(tuple(KEY), "#FFFFFF", 1.0)],
                  ambient="#000000", shadows=False, ao=False)
    o, d = cam.rays(X1.reshape(-1).astype(np.float64), Y1.reshape(-1).astype(np.float64))
    dep = o1["depth"].reshape(-1)
    z = np.where(np.isfinite(dep), dep, 0)
    p = (o + d * z[:, None]).reshape(128, 128, 3)
    n = o1["normal"].astype(np.float64)
    n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-9)
    dn = d[:, 1]
    tf = np.where(dn < -1e-6, -o[:, 1] / np.where(dn < -1e-6, dn, -1), np.inf)
    fp = (o + d * np.where(np.isfinite(tf), tf, 0)[:, None]).reshape(128, 128, 3)
    shadow = ak.px_mean(R.ground(cv, sc["node"], cam, y=0.0, light=tuple(KEY), ss=2, k=5.0, ao=False), cv.s)
    return dict(mat=mat, p=p, n=n, floor=fp, tf=tf.reshape(128, 128), shadow=shadow)


def smooth(a, b, v):
    t = np.clip((np.asarray(v, float) - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


DIM = {"cream": "grey", "grey": "m1", "m1": "m0", "m0": "black", "g3": "g2", "g2": "g1", "g1": "g0", "g0": "black",
       "br1": "br0", "br0": "black", "red": "br0"}


def dim(pic, mask, n=1):
    """Every colour in `mask` n steps down its ramp toward black."""
    lut = np.arange(256, dtype=pic.idx.dtype)
    for a, b in DIM.items():
        lut[pic.pal[a]] = pic.pal[b]
    for _ in range(n):
        pic.idx[mask] = lut[pic.idx[mask]]


def line_mask(pts):
    m = np.zeros((128, 128), bool)
    for x, y in ak.line_px(pts):
        if 0 <= x < 128 and 0 <= y < 128:
            m[y, x] = True
    return m


def cross_stamp():
    """The cross pad: 3-px arms, slate, its top and left edges grey, a black
    lip under and right of it."""
    C = np.zeros((7, 7), bool)
    C[:, 2:5] = True
    C[2:5, :] = True
    rows = []
    for y in range(8):
        r = ""
        for x in range(8):
            inside = y < 7 and x < 7 and C[y, x]
            if inside:
                lit = (y == 0 or not C[y - 1, x]) or (x == 0 or not C[y, x - 1])
                r += "h" if lit else "m"
            else:
                up_ = y > 0 and x < 7 and C[y - 1, x]
                lf_ = x > 0 and y < 7 and C[y, x - 1]
                r += "k" if (up_ or lf_) else "."
        rows.append(r)
    return rows


BUTTON = [".rrrr.",
          "rcrrrr",
          "rrrrrb",
          "rrrrrb",
          "rrrrbb",
          ".bbbb."]
SPEAKER = ["...k.k.k",
           "..k.k.k.",
           ".k.k.k..",
           "k.k.k..."]


# ---- the picture ------------------------------------------------------------------------

def draw():
    P = ak.Palette(COL, ramps=[GREEN, METAL, RED, ["black", "br0", "br1", "cream"], ["gold0", "gold1", "gold2", "cream"]])
    pic = ak.Picture.blank(P, "black")
    cam = camera()
    sc = scene()
    G = geometry(cam, sc)
    rot, pos, crot, cpos = sc["rot"], sc["pos"], sc["crot"], sc["cpos"]
    hx, hy, hz = DEV["half"]
    L, W = CARD["len"], CARD["wide"]
    dev = G["mat"] == 0
    card = G["mat"] == 1
    cab = G["mat"] == 2
    plug = G["mat"] == 3
    lbase = G["mat"] == 4
    lid = G["mat"] == 5
    things = G["mat"] >= 0
    keep = np.zeros((128, 128), bool)                      # deliberate glints: despeckling leaves them

    def dev_at(lx, ly, lz=0.0):
        return np.array(cam.project(pos + rot @ np.array([lx, ly, lz], float)))

    def card_at(u, v, w=0.0):
        return np.array(cam.project(cpos + crot @ np.array([u, v, w], float)))

    u_in = L / 2 - CARD["insert"]                          # where the card meets the side face (u)
    E_top = card_at(u_in, W / 2, CARD["thick"] / 2)        # the entry's top corner: the focal point
    E_bot = card_at(u_in, -W / 2 + NOTCH[2] * W, CARD["thick"] / 2)
    horizon = cam.project((CAM["pos"][0], CAM["pos"][1], -500.0))[1]

    # ---- the room: black void with a green glow hugging the device (calm
    # under the title), a band of haze along the horizon, the floor hazing
    # over toward it, the device's shadow on it
    sky = ~things & ~np.isfinite(G["tf"])
    floor = np.isfinite(G["tf"]) & ~things
    dist = np.where(np.isfinite(G["tf"]), G["tf"], 99.0)
    near_dev = ak.distance_px(dev, GLOW[2])                       # a soft glow hugging the device
    lv = np.interp(near_dev, [0, GLOW[1], GLOW[2]], [GLOW[3], GLOW[3] - 0.6, 0.0]) * smooth(CALM[0], CALM[1], Y1)
    lv = np.maximum(lv, np.interp(np.abs(Y1 - horizon), [0, 3, 9], [1.2, 0.8, 0.0]))   # the horizon's band of haze
    lv = np.where(floor, np.maximum(np.interp(dist, HAZE[0], HAZE[1]), lv * smooth(4.0, 9.0, dist)), lv)
    shade = G["shadow"] * floor
    bg = np.clip(lv - shade * 1.6, 0, 4.0)
    plateau = np.floor(ak.terrace(bg, 0.12) + 0.5)
    ak.by_level(pic, ak.terrace(bg, 0.12), GREEN, ~things & ~sky)
    ak.by_level(pic, ak.terrace(bg, 0.16), GREEN, sky)

    # ---- the floor's grid: continuous 1-px lines, one level over the
    # ground they cross, fading into the haze; none in the deep shadow
    lines = np.zeros((128, 128), bool)
    zc = CAM["pos"][2]
    for k in range(-14, 16):
        a_, b_ = cam.project((k * GRID, 0.0, zc - 0.6)), cam.project((k * GRID, 0.0, -9.0))
        lines |= line_mask([a_, b_])
    for j in range(0, 14):
        z_ = zc - 0.9 - j * GRID
        if zc - z_ > 9.0:
            break
        a_, b_ = cam.project((-14.0, 0.0, z_)), cam.project((14.0, 0.0, z_))
        lines |= line_mask([a_, b_])
    lines &= floor & (dist < 9.5)
    glv = np.clip(np.maximum(plateau + 1, 1 + (dist < 7.0) + (dist < 4.5)) - (shade > 0.5) * 1, 0, 3)
    glv = np.where(dist > 7.5, np.minimum(glv, plateau + 0.0), glv)
    for k, c in ((1, "g0"), (2, "g1"), (3, "g2")):
        pic.put(lines & (glv == k), c)

    # ---- the laptop at the horizon, the cable's end: a dark shape, its
    # screen glowing (a window of files: the card, mounted as a drive)
    lrot, lid_rot = sc["lrot"], sc["lid_rot"]
    cl = np.clip(G["n"] @ KEY, 0, 1)
    ln_b = G["n"] @ lrot
    pic.put(lbase, "m0")
    deck = lbase & (ln_b[..., 1] > 0.5)
    pic.put(deck, "m1")
    pic.put(deck & ~ak.shift(deck, 0, -1) & ak.shift(lbase, 0, -1), "grey")     # its front lip, toward the key
    lloc = (G["p"] - sc["hinge"]) @ lid_rot
    lnl = G["n"] @ lid_rot
    lw, lh, lt = LAPTOP["lid"]
    lface = lid & (lnl[..., 2] > 0.6)
    pic.put(lid, "m0")
    lu = (lloc[..., 0] + lw) / (2 * lw)
    lv_ = 1 - lloc[..., 1] / (2 * lh)
    lscr = lface & (lu > 0.08) & (lu < 0.92) & (lv_ > 0.10) & (lv_ < 0.88)
    pic.put(lscr, "g1")
    pic.put(lscr & (lv_ < 0.24), "g2")                                   # the window's title bar
    for r0 in (0.36, 0.56):                                                # two rows of files
        pic.put(lscr & (lv_ > r0) & (lv_ < r0 + 0.12) & (lu > 0.16) & (lu < 0.30), "br1")
        pic.put(lscr & (lv_ > r0) & (lv_ < r0 + 0.12) & (lu > 0.38) & (lu < 0.80), "g2")
    ak.outline(pic, lid | lbase, "black", where=~things)
    keep |= lscr

    # ---- the cable: dark rubber with a lit top line, from the device's
    # back across the floor to the laptop; its plug a metal sleeve
    ak.by_level(pic, np.round(0.7 + 1.6 * cl ** 1.5), METAL, cab)
    ak.outline(pic, cab, "black", where=floor)
    top_line = cab & ~ak.shift(cab, 0, 1) & ak.shift(cab, 0, -1)
    pic.put(top_line & (cl > 0.30), "m1")
    ak.by_level(pic, np.round(1.6 + 2.0 * cl), METAL, plug)
    ak.outline(pic, plug, "black", where=floor)
    # data pulses running along it, away from the device
    cpts = sc["cable"]
    seg = np.linalg.norm(np.diff(cpts, axis=0), axis=1)
    arc = np.concatenate([[0], np.cumsum(seg)])
    hp = G["p"][cab]
    near = np.argmin(((hp[:, None, :] - cpts[None, :, :]) ** 2).sum(-1), axis=1)
    s_px = np.zeros((128, 128))
    s_px[cab] = arc[near]
    for s0 in PULSES:
        core = cab & (np.abs(s_px - s0) < 0.07)
        trail = cab & (s_px < s0 - 0.07) & (s_px > s0 - 0.40)
        pic.put(trail, "g2")
        pic.put(trail & (s_px > s0 - 0.20), "g3")
        pic.put(core, "cream")
        keep |= core

    # ---- the device: gunmetal, each face flat by how it meets the key
    loc = (G["p"] - pos) @ rot
    ln = G["n"] @ rot
    lx, ly, lz = loc[..., 0], loc[..., 1], loc[..., 2]
    ax = np.argmax(np.abs(ln), -1)
    srt = np.sort(np.abs(ln), -1)
    flat = srt[..., 1] < 0.3
    front = dev & flat & (ax == 2) & (ln[..., 2] > 0)
    left = dev & flat & (ax == 0) & (ln[..., 0] < 0)
    rnd = dev & ~(front | left)
    nx_, ny_, nz_ = ln[..., 0], ln[..., 1], ln[..., 2]
    fu = np.clip((lx + hx) / (2 * hx), 0, 1)
    fv = np.clip((hy - ly) / (2 * hy), 0, 1)
    dl = np.zeros((128, 128))
    dl[front] = np.interp(fu * 0.5 + fv, [0.0, 0.16, 0.30], [2.0, 1.5, 1.0])[front]   # a sheen falling off from the top left
    dl[left] = np.interp(fv, [0.0, 0.45, 0.62, 1.0], [3.0, 3.0, 2.0, 2.0])[left]
    edge = np.full((128, 128), 1.0)
    edge[ny_ > 0.3] = 3.0                                                         # the top's lip, toward the key
    vc_ = (np.abs(ny_) <= 0.3) & (nx_ < -0.3) & (nz_ > 0.3)
    edge[vc_] = 2.0                                                               # the corner between side and front: slate
    edge[(nx_ > 0.3) & (ny_ > -0.3)] = 1.0                                        # the far corner, in shade
    edge[ny_ < -0.3] = 0.5                                                        # the underside
    dl[rnd] = edge[rnd]
    ak.by_level(pic, ak.terrace(dl, 0.25), METAL, dev)
    # an outline on its shadow side; the haze's green rims its right edge
    ring_d = ak.dilate(dev, 1) & ~dev & ~things
    pic.put(ring_d & (ak.shift(dev, 1, 0) | ak.shift(dev, 0, 1)), "black")
    right_rim = dev & ~ak.shift(dev, -1, 0) & (ak.shift(dev, 1, 0)) & (XX > dev_at(0, 0)[0])
    pic.put(right_rim & (Y1 > dev_at(hx, hy)[1] + 3) & (Y1 < horizon + 14), "g1")

    # the screen: its bezel, then the instrument panel (the app's own
    # layout: status bar, fill gauge, graph, strip, event log)
    sx0, sx1, sy0, sy1 = SCREEN
    bez = front & (lx > sx0 - BEZEL) & (lx < sx1 + BEZEL) & (ly > sy0 - BEZEL) & (ly < sy1 + BEZEL)
    scr = front & (lx > sx0) & (lx < sx1) & (ly > sy0) & (ly < sy1)
    pic.put(bez, "black")
    u = (lx - sx0) / (sx1 - sx0)
    v = (sy1 - ly) / (sy1 - sy0)
    pic.put(scr, "g0")
    # laid out in whole pixels: rows and columns counted across the screen
    H = int(round(dev_at(sx0, sy0, hz)[1] - dev_at(sx0, sy1, hz)[1]))
    Wd = int(round(dev_at(sx1, (sy0 + sy1) / 2, hz)[0] - dev_at(sx0, (sy0 + sy1) / 2, hz)[0]))
    r = np.floor(v * H).astype(int)
    c = np.floor(u * Wd).astype(int)

    def cell(r0, r1, c0, c1, colour, extra=True):
        pic.put(scr & (r >= r0) & (r <= r1) & (c >= c0) & (c <= c1) & extra, colour)
    # the status bar: the card, its state, the speed (amber)
    cell(1, 2, 1, 3, "g3")
    cell(1, 2, 5, Wd // 2, "g2")
    cell(1, 2, Wd - 7, Wd - 2, "br1")
    # the fill gauge, 2 px
    cell(4, 5, 1, int(Wd * 0.66), "g2")
    cell(4, 5, int(Wd * 0.66) + 1, Wd - 2, "g1")
    # the graph: a bar a command, its height the speed: green reads, a bright
    # cap on each; the newest two are writes, in amber
    g0r, g1r = 7, H - 9
    nb = len(GRAPH)
    sw = (Wd - 2) / nb
    for k, h in enumerate(GRAPH):
        cx = 1 + int(round(k * sw))
        top = g1r - int(round(h * (g1r - g0r)))
        am = k in WRITES
        bm = scr & (r >= top) & (r <= g1r) & (c >= cx) & (c <= cx + 1)
        pic.put(bm, "br1" if am else "g2")
        if not am:
            pic.put(bm & ~ak.shift(bm, 0, 1), "g3")                       # its cap: the top pixel of each column
    # the strip: what each command touched
    cell(H - 7, H - 7, 1, Wd - 2, "g2")
    cell(H - 7, H - 7, 1 + int(round(WRITES[0] * sw)), Wd - 2, "br1")
    # the event log: two rows (a tag, a name, a size); the second a delete, red
    for k, r0 in enumerate((H - 5, H - 2)):
        cell(r0, r0 + 1, 1, 3, ("g3", "red")[k])
        cell(r0, r0 + 1, 5, int(Wd * (0.66, 0.55)[k]), "g2")
        cell(r0, r0 + 1, Wd - 5, Wd - 2, "g1")
    keep |= scr

    # the controls, stamped by hand at their places (too small to sample)
    def stamp(local, rows, key):
        x_, y_ = dev_at(*local, hz)
        h_, w_ = len(rows), len(rows[0])
        x0, y0 = int(round(x_ - w_ / 2)), int(round(y_ - h_ / 2))
        ak.patch(pic, x0, y0, rows, key)
        for j, r_ in enumerate(rows):
            for i, ch in enumerate(r_):
                if ch in key and 0 <= y0 + j < 128 and 0 <= x0 + i < 128:
                    keep[y0 + j, x0 + i] = True
    stamp(PAD, cross_stamp(), {"h": "grey", "m": "m1", "d": "m0", "k": "black"})
    for b_ in BUTTONS:
        stamp(b_, BUTTON, {"r": "red", "c": "cream", "b": "br0", "k": "black"})
    for p_ in PILLS:
        stamp(p_, ["mmm", "kkk"], {"m": "m1", "k": "black"})
    stamp(GRILLE, SPEAKER, {"k": "black"})
    led = bez & ~scr & (np.hypot(lx - (sx0 + 0.02), ly - (sy1 + 0.03)) < 0.035)
    pic.put(led, "red")
    keep |= led

    # ---- the slot: a black slit where the card goes in, a cream lip
    # over it, a tight green halo round the entry on the side face
    span = (ly < SLOT_Y + W / 2 + 0.10) & (ly > SLOT_Y - W / 2 + NOTCH[2] * W - 0.10)
    pic.put(left & span & (np.abs(lz) < 0.085), "g1")
    pic.put(left & span & (np.abs(lz) < 0.06) & (ly < SLOT_Y + W / 2 + 0.06) & (ly > SLOT_Y - W / 2 + NOTCH[2] * W - 0.06), "g2")
    slit = left & (ly < SLOT_Y + W / 2 + 0.04) & (ly > SLOT_Y - W / 2 + NOTCH[2] * W - 0.04) & (np.abs(lz) < 0.035)
    pic.put(slit, "g3")
    # and spills into the air at the slit's ends, above and below the card
    ends = slit & ~ak.dilate(card, 2)
    air = ~things & (ak.distance_px(ends, 4) < 4)
    pic.put(air, "g1")
    pic.put(air & (ak.distance_px(ends, 4) < 2), "g2")

    # ---- the card: red glossy plastic, brass contacts, its edges lit
    cl_ = (G["p"] - cpos) @ crot
    cn = G["n"] @ crot
    cu, cvv = cl_[..., 0], cl_[..., 1]
    cface = card & (np.abs(cn[..., 2]) > 0.7)
    rim = card & ~cface
    q = (cu / L + 0.5) * 0.9 + (0.5 - cvv / W) * 0.55               # 0 at the upper trailing corner
    pic.put(cface, "red")
    pic.put(cface & (cvv < -W / 2 + 0.07 * W), "br0")                 # the lower edge in shade
    pic.put(cface & (cu > u_in - 0.10 * L), "br0")                   # dark toward the slot
    band = cface & (q > GLOSS[0]) & (q < GLOSS[1])
    pic.put(band, "grey")
    pic.put(cface & (np.abs(q - GLOSS[1] - 0.06) < 0.012), "grey")    # a thin second line beside it
    pic.put(band & (np.abs(q - (GLOSS[0] + GLOSS[1]) / 2) < 0.022) & (cvv < W * 0.36) & (cvv > -W * 0.30), "cream")
    pic.put(rim & (cn[..., 1] > 0.5), "grey")                        # the top edge, toward the key
    pic.put(rim & (cn[..., 0] < -0.5), "m1")                         # the trailing end
    # the eight contacts: parallel ribs (brass, a rust lip, a black gap)
    contact = np.zeros((128, 128), bool)
    v_lo, v_hi = -W / 2 + NOTCH[2] * W + 0.02, W / 2 - 0.03
    pitch = (v_hi - v_lo) / 8
    u0, u1 = L / 2 - PADS * L, u_in
    area = cface & (cu > u0 - 0.01) & (cvv > v_lo) & (cvv < v_hi)
    pic.put(area, "black")
    for k in range(8):
        vk = v_hi - (k + 0.3) * pitch
        a_, b_ = card_at(u0, vk, CARD["thick"] / 2), card_at(u1 + 0.05, vk, CARD["thick"] / 2)
        for dy_, c_ in ((0.0, "br1"), (1.0, "br0")):
            for x_, y_ in ak.ink(pic, [tuple(a_ + (0, dy_)), tuple(b_ + (0, dy_))], c_, where=area):
                if 0 <= x_ < 128 and 0 <= y_ < 128 and area[y_, x_]:
                    contact[y_, x_] = True
    ring = ak.dilate(card, 1) & ~card & ~dev
    pic.put(ring, "black")
    # the light wraps round its leading corners: green on its edges by the slot
    edge_ = card & ~ak.erode(card, 1)
    near_e = (np.hypot(X1 - E_top[0], Y1 - E_top[1]) < 5) | (np.hypot(X1 - E_bot[0], Y1 - E_bot[1]) < 4)
    pic.put(edge_ & near_e & ~contact, "g3")
    halo = ring & near_e
    pic.put(halo, "g2")
    # the glint on its top edge, at the trailing corner
    tg = card_at(-L / 2 + 0.06 * L, W / 2, CARD["thick"] / 2)
    gx_, gy_ = int(round(tg[0])), int(round(tg[1]))
    ak.glint(pic, gx_, gy_, 2, arms=(2, 3, 2, 2))
    keep[gy_ - 2:gy_ + 3, gx_ - 2:gx_ + 4] = True

    # ---- motion: a red smear off the card's trailing end, tapering away
    t0, t1 = card_at(-L / 2, 0.0), card_at(L / 2, 0.0)
    back = (t0 - t1) / np.linalg.norm(t0 - t1)
    perp = np.array([-back[1], back[0]])
    if perp[1] < 0:
        perp = -perp
    free = ~things & ~ak.dilate(card, 1) & (XX > 1)
    for vf, length, r0 in SMEAR:                                   # the smear: red streaks off the trailing end
        root = card_at(-L / 2, vf * W / 2) + back * 1
        end = root + back * length + perp * length * 0.12
        ctrl = (root + end) / 2
        ak.streak(pic, tuple(root), tuple(ctrl), tuple(end), r0, 0.3, ok=free, cols=(("red", 0.35), ("br0", 1.0)))

    # ---- the burst on the entry's top corner
    gx, gy = int(round(E_top[0])), int(round(E_top[1])) - 1
    arms = (6, 5, 6, 4)
    ak.glint(pic, gx, gy, 6, tip="g3", arms=arms)
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        pic.px(gx + dx, gy + dy, "g3")
    keep[gy - 1:gy + 2, gx - 1:gx + 2] = True                          # the star's own pixels stay
    keep[gy, gx - arms[0]:gx + arms[1] + 1] = True
    keep[gy - arms[2]:gy + arms[3] + 1, gx] = True

    # ---- clean-up: lone pixels go (the glints stay); the frame's edges
    # step down into the dark
    ak.despeckle(pic, need=5, keep=keep)
    dim(pic, (XX < 2) | (XX > 125) | (YY > 125), 2)

    # ---- the title: wide gold chrome, a gold0-to-rust extrusion, a black
    # drop shadow, a bevel on its outer contour, one star on each line
    ck = ak.checker()
    for path, y, gl in ((TITLE, TITLE_Y[0], TITLE_GLINTS[0]), (TITLE2, TITLE_Y[1], TITLE_GLINTS[1])):
        m = ak.load_mask(path)
        tx = ak.centred_x(m)
        t = ak.title(pic, m, tx, y, fill=None, rows=TITLE_ROWS, hi=None, lo=None,
                     extrude=dict(dx=1, dy=1, depth=2, colours=TITLE_EXTRUDE), shadow=dict(dx=1, dy=2, colour="black"))
        F = t["face"]
        wide = ak.thick(F, 2)
        for r_, c_ in TITLE_SEAMS:
            pic.put(F & wide & (YY == y + r_) & ck, c_)
        ak.bevel_runs(pic, F, "cream", "gold0")
        ak.glint(pic, tx + gl[0], y + gl[1], gl[2])
    return pic.image()


if __name__ == "__main__":
    import boxart
    boxart.save(draw(), HERE.parent / "docs" / "cart.png")
