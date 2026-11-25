"""Original art for the bodhisattva and Guru Rinpoche sets: every piece drawn in code, frame by frame.

Used by build_lpc.py. None of these pieces takes pixels from the LPC library. To know where the body
is in each frame of each animation, a few LPC layers are rendered as *probes* and only measured: where
the headband sits (the head), the torso's top and sides (shoulders), the gloves (hands), the shoes
(feet), the belt (waist), the arms of a long-sleeved shirt (elbows), and for weapons and shields, the
base's own weapon or shield (where it's held and at what angle). From those points every garment,
hat, weapon and shield is drawn new, in the set's colours, in every frame: the front and side poses
and each fight animation (slash, thrust, shoot, spellcast, hurt, ride).

A frame is 64px; weapons with big swings keep the probe's bigger frame (128 or 192) so nothing is cut.
"""
import math

from PIL import Image, ImageDraw

F = 64
PROBES = {"band": "hat_headband_thick", "torso": "torso_clothes_sleeveless", "sleeves": "torso_clothes_longsleeve",
          "hands": "arms_gloves", "legs": "legs_pants", "feet": "feet_shoes_basic", "belt": "belt_leather"}


def hexrgb(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


# ---------------------------------------------------------------- masks and measuring
def _mask(im):
    """Set of (x, y) of the opaque pixels."""
    if im is None:
        return set()
    a = im.getchannel("A").load()
    w, h = im.size
    return {(x, y) for y in range(h) for x in range(w) if a[x, y] > 40}


def _components(pts):
    pts, out = set(pts), []
    while pts:
        stack, comp = [pts.pop()], []
        while stack:
            x, y = stack.pop()
            comp.append((x, y))
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    q = (x + dx, y + dy)
                    if q in pts:
                        pts.remove(q)
                        stack.append(q)
        out.append(comp)
    return sorted(out, key=len, reverse=True)


def _bbox(pts):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def _centre(pts):
    return sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)


def pose_of(m):
    """Keypoints of one frame from its probe masks (each a set of points in the 64px frame)."""
    P = {}
    if m["band"]:
        x0, y0, x1, y1 = _bbox(m["band"])
        P["head"] = ((x0 + x1) / 2, y0, x0, x1, y1)  # centre x, band top, band left/right, band bottom
    if m["torso"]:
        x0, y0, x1, y1 = _bbox(m["torso"])
        rows = {}
        for x, y in m["torso"]:
            rows.setdefault(y, []).append(x)
        top = min(rows)
        sh = rows[min(rows, key=lambda y: (y - top - 2) ** 2)]
        P["torso"] = (x0, y0, x1, y1)
        P["shoulders"] = (min(sh), max(sh), top + 1)
        P["rows"] = {y: (min(xs), max(xs)) for y, xs in rows.items()}
    hands = [_centre(c) for c in _components(m["hands"]) if len(c) >= 3][:2]
    P["hands"] = sorted(hands)
    feet = [c for c in _components(m["feet"]) if len(c) >= 3][:2]
    P["feet"] = sorted([_bbox(c) for c in feet])
    belt = _components(m["belt"])
    if belt:
        x0, y0, x1, y1 = _bbox(belt[0])
        P["waist"] = (x0, (y0 + y1) / 2, x1)
    if m["legs"]:
        P["legs"] = _bbox(m["legs"])
    # the elbows: on each arm (the sleeves without the torso), the point farthest off the shoulder-hand line
    arms = [c for c in _components(m["sleeves"] - m["torso"]) if len(c) >= 4][:2]
    P["arms"] = []
    for c in arms:
        cx, cy = _centre(c)
        hand = min(P["hands"], key=lambda h: (h[0] - cx) ** 2 + (h[1] - cy) ** 2) if P["hands"] else (cx, cy)
        top = min(c, key=lambda p: p[1])  # where the arm leaves the shoulder
        ax, ay, bx, by = top[0], top[1], hand[0], hand[1]
        L = math.hypot(bx - ax, by - ay) or 1
        elbow = max(c, key=lambda p: abs((bx - ax) * (ay - p[1]) - (ax - p[0]) * (by - ay)) / L)
        P["arms"].append(((ax, ay), elbow, (bx, by)))
    return P


def weapon_axis(pts, hand, heavy_tip=False):
    """(grip, tip, length) of a weapon probe: its main axis by moments, the tip its far end from the hand."""
    if len(pts) < 3:
        return None
    cx, cy = _centre(pts)
    sxx = sum((x - cx) ** 2 for x, _ in pts)
    syy = sum((y - cy) ** 2 for _, y in pts)
    sxy = sum((x - cx) * (y - cy) for x, y in pts)
    ang = 0.5 * math.atan2(2 * sxy, sxx - syy)
    ux, uy = math.cos(ang), math.sin(ang)
    proj = [(x - cx) * ux + (y - cy) * uy for x, y in pts]
    lo, hi = min(proj), max(proj)
    a = (cx + ux * lo, cy + uy * lo)
    b = (cx + ux * hi, cy + uy * hi)
    if heavy_tip:  # long staffs: the head is the end with more pixels (its ornament)
        k = (hi - lo) * 0.25
        if sum(1 for p in proj if p < lo + k) > sum(1 for p in proj if p > hi - k):
            a, b = b, a
    elif hand is not None and math.hypot(a[0] - hand[0], a[1] - hand[1]) > math.hypot(b[0] - hand[0], b[1] - hand[1]):
        a, b = b, a
    return a, b, hi - lo


# ---------------------------------------------------------------- frames of the probes
ZS = {}  # each probe's z (where the LPC layer it stands for is drawn)


def probe_frames(B, body, names=None):
    """{key: {probe: mask}} for every frame: ("south", 0), ("east", 0) and (anim, i) for each fight
    animation, measured in the 64px frame (bigger anim frames are centred on it)."""
    names = names or PROBES
    out = {}
    ZS.update({pk: max(z for z, _ in B.layer_frames(name, body)) for pk, name in names.items() if B.layer_frames(name, body)})
    for pk, name in names.items():
        for z, fr in B.layer_frames(name, body):
            for row, im in fr.items():
                key = ("south" if row == B.SOUTH else "east", 0)
                cell = im.crop((32, 32, 96, 96))
                out.setdefault(key, {}).setdefault(pk, set()).update(_mask(cell))
        for z, rows in B.anim_layers(name, body):
            for a, (strip, fs, n) in rows.items():
                o = (fs - F) // 2
                for i in range(n):
                    fr = strip.crop((i * fs + o, o, i * fs + o + F, o + F))
                    out.setdefault((a, i), {}).setdefault(pk, set()).update(_mask(fr))
    for k in out:
        for pk in names:
            out[k].setdefault(pk, set())
    return out


def anim_counts(B, name, body):
    """{anim: (frame size, n)} of a probe layer (the weapon's own, for its swing)."""
    out = {}
    for z, rows in B.anim_layers(name, body):
        for a, (strip, fs, n) in rows.items():
            out[a] = max(out.get(a, (0, 0)), (fs, n))
    return out


# ---------------------------------------------------------------- drawing
SIDE = {"east", "side", "slash", "thrust", "shoot", "spellcast", "ride"}  # facing east; the rest face the viewer


def _mix(c, d, t):
    return tuple(round(c[i] * (1 - t) + d[i] * t) for i in range(3)) + (c[3],)


def finish(im, dark="#100c08"):
    """Pixel-art finish: a light edge on top, a shadow under and to the right, then a dark outline."""
    a = im.load()
    w, h = im.size
    out = im.copy()
    o = out.load()
    D = hexrgb(dark)
    op = lambda x, y: 0 <= x < w and 0 <= y < h and a[x, y][3] > 0
    for y in range(h):
        for x in range(w):
            if a[x, y][3]:
                if not op(x, y - 1):
                    o[x, y] = _mix(a[x, y], (255, 255, 255, 255), 0.3)
                elif not op(x, y + 1) or not op(x + 1, y):
                    o[x, y] = _mix(a[x, y], (0, 0, 0, 255), 0.3)
            elif op(x - 1, y) or op(x + 1, y) or op(x, y - 1) or op(x, y + 1):
                o[x, y] = D
    return out


class Pen:
    def __init__(self, size, off=0):
        self.im = Image.new("RGBA", (size, size))
        self.d = ImageDraw.Draw(self.im)
        self.o = off  # 64px-frame coordinates + o = canvas coordinates

    def _p(self, pts):
        return [(round(x + self.o), round(y + self.o)) for x, y in pts]

    def poly(self, pts, col):
        self.d.polygon(self._p(pts), fill=hexrgb(col))

    def line(self, pts, col, w=1):
        self.d.line(self._p(pts), fill=hexrgb(col), width=w, joint="curve")
        if w >= 3:  # round the ends
            for x, y in self._p([pts[0], pts[-1]]):
                r = (w - 1) / 2
                self.d.ellipse([x - r, y - r, x + r, y + r], fill=hexrgb(col))

    def _box(self, x0, y0, x1, y1):
        (a, b), (c, d) = self._p([(x0, y0), (x1, y1)])
        return [min(a, c), min(b, d), max(a, c), max(b, d)]

    def ell(self, x0, y0, x1, y1, col):
        self.d.ellipse(self._box(x0, y0, x1, y1), fill=hexrgb(col))

    def px(self, x, y, col):
        x, y = round(x + self.o), round(y + self.o)
        if 0 <= x < self.im.width and 0 <= y < self.im.height:
            self.im.putpixel((x, y), hexrgb(col))

    def clear_ell(self, x0, y0, x1, y1):
        m = Image.new("L", self.im.size)
        ImageDraw.Draw(m).ellipse(self._box(x0, y0, x1, y1), fill=255)
        self.im.paste((0, 0, 0, 0), mask=m)

    def paste(self, pic, x, y):
        self.im.alpha_composite(pic, (round(x + self.o), round(y + self.o)))


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


# -- where things are in a frame, with fallbacks
def shoulders(P):
    if "shoulders" in P:
        return P["shoulders"]
    return None


def waist(P):
    if "waist" in P:
        return P["waist"]
    if "torso" in P:
        x0, y0, x1, y1 = P["torso"]
        return (x0, y1 - 2, x1)
    return None


def feet_top(P):
    return min((f[1] for f in P["feet"]), default=None)


def feet_span(P):
    if not P["feet"]:
        return None
    return min(f[0] for f in P["feet"]), max(f[2] for f in P["feet"])


def arms_in_order(P, side):
    """Far arm first, near arm last (from the side, the near arm is the bigger one in the probe)."""
    return list(reversed(P["arms"])) if side else P["arms"]


# -- garments
def torso_shape(pen, P, col, side):
    sh, w = shoulders(P), waist(P)
    if not sh or not w:
        return
    l, r, y = sh
    wl, wy, wr = w
    pen.poly([(l, y), (r, y), (wr, wy + 1), (wl, wy + 1)], col)


def skirt(pen, P, col, length, side, flare=2, folds=None, stripes=None, ragged=False):
    """From the waist down: to the knee ("knee") or the ankle ("ankle")."""
    w, ft, span = waist(P), feet_top(P), feet_span(P)
    if not w or ft is None:
        return
    wl, wy, wr = w
    hy = ft + 1 if length == "ankle" else (wy + ft) / 2 + 2
    t = (hy - wy) / max(1, ft - wy)
    hl = wl + (span[0] - flare - wl) * t
    hr = wr + (span[1] + flare - wr) * t
    pts = [(wl, wy), (wr, wy), (hr, hy), (hl, hy)]
    pen.poly(pts, col)
    if ragged:
        for x in range(round(hl), round(hr) + 1, 3):
            pen.poly([(x, hy), (x + 1.5, hy + 2), (x + 3, hy)], col)
    if folds:
        for k in (0.33, 0.66):
            a = lerp((wl, wy), (wr, wy), k)
            b = lerp((hl, hy), (hr, hy), k)
            pen.line([lerp(a, b, 0.3), b], folds)
    if stripes:
        for i, yy in enumerate(range(round(wy) + 2, round(hy), 3)):
            t2 = (yy - wy) / max(1, hy - wy)
            x0 = wl + (hl - wl) * t2
            x1 = wr + (hr - wr) * t2
            for x in range(round(x0) + 1 + i % 2 * 2, round(x1), 4):
                pen.line([(x, yy), (x + 1, yy + 1)], stripes)


def pants(pen, P, col, side, to="ankle"):
    w, ft = waist(P), feet_top(P)
    if not w or ft is None or not P["feet"]:
        return
    wl, wy, wr = w
    feet = P["feet"] if len(P["feet"]) == 2 else [(f[0], f[1], (f[0] + f[2]) / 2, f[3]) for f in P["feet"]] + [((f[0] + f[2]) / 2, f[1], f[2], f[3]) for f in P["feet"]]
    hips = [(wl + 3, wy + 2), (wr - 3, wy + 2)]
    for hip, f in zip(hips, sorted(feet)):
        foot = ((f[0] + f[2]) / 2, f[1] + 1)
        end = foot if to == "ankle" else lerp(hip, foot, 0.75)
        pen.line([hip, end], col, 6 if not side else 5)


def sleeves(pen, P, col, cuff=None, side=False, which=(0, 1), length=0.8):
    for k, (a, e, h) in enumerate(arms_in_order(P, side)):
        if k not in which:
            continue
        end = lerp(e, h, length)
        pen.line([a, e, end], col, 4)
        if cuff:
            pen.line([lerp(e, end, 0.8), end], cuff, 4)


def cape(pen, P, col, side, trim=None, ragged=False):
    sh, ft = shoulders(P), feet_top(P)
    if not sh or ft is None:
        return
    l, r, y = sh
    if side:
        pts = [(l + 1, y), (l + 5, y), (l - 1, ft), (l - 8, ft + 1)]
    else:
        pts = [(l - 1, y), (r + 1, y), (r + 5, ft), (l - 5, ft)]
    pen.poly(pts, col)
    if ragged:
        a, b = pts[3], pts[2]
        n = 5
        for i in range(n):
            p0, p1 = lerp(a, b, i / n), lerp(a, b, (i + 1) / n)
            pen.poly([p0, p1, ((p0[0] + p1[0]) / 2, p0[1] + 3)], col)
    if trim:
        pen.line([pts[3], pts[2]], trim, 1)


def shawl(pen, P, col, side, trim=None):
    sh, w = shoulders(P), waist(P)
    if not sh or not w:
        return
    l, r, y = sh
    wl, wy, wr = w
    if side:
        pen.poly([(l + 1, y - 1), (r, y - 1), (wr + 1, wy + 2), (wl + 2, wy + 2)], col)
    else:
        pen.poly([(l - 1, y - 1), (l + 6, y - 1), (wr + 1, wy + 3), (wr - 5, wy + 3)], col)
        if trim:
            pen.line([(l + 6, y - 1), (wr + 1, wy + 3)], trim)


def armour(pen, P, metal, dark, accent, side):
    sh, w = shoulders(P), waist(P)
    if not sh or not w:
        return
    torso_shape(pen, P, metal, side)
    l, r, y = sh
    wl, wy, wr = w
    for yy in range(round(y) + 3, round(wy), 3):
        t = (yy - y) / max(1, wy - y)
        pen.line([(l + (wl - l) * t + 1, yy), (r + (wr - r) * t - 1, yy)], dark)
    for x in ((l, ) if side else (l, r)):
        pen.ell(x - 3, y - 2, x + 3, y + 3, accent)


def tabard(pen, P, col, side, emblem=None):
    sh, w, ft = shoulders(P), waist(P), feet_top(P)
    if not sh or not w or ft is None:
        return
    l, r, y = sh
    wl, wy, wr = w
    cx = (l + r) / 2
    hw = 3 if side else 4
    hy = (wy + ft) / 2 + 3
    pen.poly([(cx - hw, y + 1), (cx + hw, y + 1), (cx + hw + 1, hy), (cx - hw - 1, hy)], col)
    if emblem:
        pen.ell(cx - 2, y + 5, cx + 2, y + 9, emblem)


def necklace(pen, P, cols, side, skulls=False):
    sh = shoulders(P)
    if not sh:
        return
    l, r, y = sh
    cx = (l + r) / 2
    span = (r - l) / 2 - 2
    if side:
        span *= 0.5
        cx += 2
    for i in range(-int(span), int(span) + 1, 2 if not skulls else 3):
        dy = 4 * (1 - (i / max(1, span)) ** 2)
        x, yy = cx + i, y + dy
        if skulls:
            pen.ell(x - 1, yy - 1, x + 1, yy + 1, cols[0])
            pen.px(x, yy, cols[1])
        else:
            pen.px(x, yy, cols[(i // 2) % len(cols)])
            pen.px(x, yy + 1, cols[(i // 2) % len(cols)])


def scarf(pen, P, col, side):
    sh = shoulders(P)
    if not sh:
        return
    l, r, y = sh
    cx = (l + r) / 2 + (2 if side else 0)
    pen.poly([(cx - 4, y - 1), (cx + 4, y - 1), (cx, y + 5)], col)


def belt(pen, P, col, side, kind="belt", tail=None, buckle=None, stripes=None):
    w = waist(P)
    if not w:
        return
    wl, wy, wr = w
    th = {"belt": 2, "rope": 1, "sash": 3, "obi": 4}[kind]
    pen.poly([(wl - 1, wy - th / 2), (wr + 1, wy - th / 2), (wr + 1, wy + th / 2), (wl - 1, wy + th / 2)], col)
    if stripes:
        for x in range(round(wl) + 1, round(wr), 3):
            pen.px(x, wy, stripes)
    cx = (wl + wr) / 2 if not side else wr - 2
    if kind in ("rope", "sash", "obi"):
        t = tail or col
        k = cx + (3 if kind != "rope" and not side else 0)
        pen.line([(k, wy), (k - 1, wy + 6)], t, 1 if kind == "rope" else 2)
        pen.line([(k + 1, wy), (k + 2, wy + 5)], t, 1 if kind == "rope" else 2)
    if buckle:
        pen.poly([(cx - 2, wy - 2), (cx + 2, wy - 2), (cx + 2, wy + 2), (cx - 2, wy + 2)], buckle)


def hands(pen, P, col, side, kind="glove", cuff=None):
    for a, e, h in P["arms"]:
        if kind == "glove":
            pen.ell(h[0] - 2, h[1] - 2, h[0] + 2, h[1] + 2, col)
            if cuff:
                pen.line([lerp(e, h, 0.6), lerp(e, h, 0.8)], cuff, 4)
        elif kind == "bracer":
            pen.line([lerp(e, h, 0.5), lerp(e, h, 0.85)], col, 4)
            if cuff:
                pen.line([lerp(e, h, 0.5), lerp(e, h, 0.58)], cuff, 4)
        elif kind == "beads":
            for t in (0.7, 0.8):
                p = lerp(e, h, t)
                pen.line([(p[0] - 2, p[1]), (p[0] + 2, p[1])], col, 2)


def feet(pen, P, col, side, kind="sandal", trim=None):
    for x0, y0, x1, y1 in P["feet"]:
        if kind == "sandal":
            pen.line([(x0, y1), (x1, y1)], col, 1)
            pen.line([(x0 + 1, y0 + 3), (x1 - 1, y0 + 3)], col, 1)
            pen.line([(x0 + (x1 - x0) / 2, y0 + 3), (x0 + (x1 - x0) / 2, y1)], col, 1)
        elif kind == "boot":
            pen.poly([(x0, y0 - 3), (x1, y0 - 3), (x1 + (1 if side else 0), y1), (x0, y1)], col)
            if trim:
                pen.line([(x0, y0 - 3), (x1, y0 - 3)], trim, 2)
        elif kind == "slipper":
            pen.ell(x0, y0 + 2, x1, y1, col)
            if trim:
                pen.px((x0 + x1) / 2 + (2 if side else 0), y0 + 3, trim)
        elif kind == "anklet":
            for x in range(round(x0), round(x1) + 1, 2):
                pen.px(x, y0 + 1, col)


# -- hats: pixel pictures (front), centred on the head, the lower edge `lift` rows below the band's top
def paint(grid, pal):
    rows = [r for r in grid.strip("\n").split("\n")]
    w = max(len(r) for r in rows)
    im = Image.new("RGBA", (w, len(rows)))
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in pal:
                im.putpixel((x, y), hexrgb(pal[ch]))
    return im


def mirror_grid(grid):
    rows = grid.strip("\n").split("\n")
    w = max(len(r) for r in rows)
    return "\n".join(r.ljust(w) + r.ljust(w)[-2::-1] for r in rows)


def hat(pen, P, pic, lift, side, dx_side=1):
    if "head" not in P:
        return
    cx, top = P["head"][0], P["head"][1]
    if side:
        cx += dx_side
    pen.paste(pic, cx - pic.width / 2 + 0.5, top + lift - pic.height)


def hood(pen, P, col, side, trim=None):
    if "head" not in P:
        return
    cx, top, l, r, _ = P["head"]
    sh = shoulders(P)
    sy = sh[2] if sh else top + 15
    pen.ell(l - 3, top - 4, r + 3, top + 17, col)
    if sh:
        pen.poly([(l - 3, top + 9), (r + 3, top + 9), (sh[1] + 1, sy + 3), (sh[0] - 1, sy + 3)], col)
    if side:
        pen.clear_ell(cx - 1, top + 3, r + 6, top + 14)
        if trim:
            pen.line([(cx - 1, top + 3), (cx - 2, top + 13)], trim)
    else:
        pen.clear_ell(cx - 7, top + 3, cx + 7, top + 15)
        if trim:
            pen.d.arc(pen._p([(cx - 8, top + 2), (cx + 8, top + 16)]), 180, 360, fill=hexrgb(trim))


# -- weapons, along the probe weapon's axis: grip g at the hand, tip t
def _uv(g, t):
    L = math.hypot(t[0] - g[0], t[1] - g[1]) or 1
    u = ((t[0] - g[0]) / L, (t[1] - g[1]) / L)
    return u, (-u[1], u[0]), L


def at(g, u, n, a, b=0):
    return (g[0] + u[0] * a + n[0] * b, g[1] + u[1] * a + n[1] * b)


def weapon(pen, kind, g, t, C):
    u, n, L = _uv(g, t)
    if kind == "crook":
        pen.line([g, t], C["wood"], 2)
        c = at(g, u, n, L, 3)
        pts = [(c[0] + 3 * (math.cos(th) * u[0] + math.sin(th) * n[0]), c[1] + 3 * (math.cos(th) * u[1] + math.sin(th) * n[1])) for th in [math.radians(a) for a in range(-90, 200, 30)]]
        pen.line([t] + pts, C["wood"], 2)
    elif kind == "pole":
        pen.line([g, t], C["wood"], 2)
        pen.line([at(g, u, n, L - 2), t], C["metal"], 2)
        pen.line([g, at(g, u, n, 2)], C["metal"], 2)
    elif kind == "sword":
        pen.line([at(g, u, n, 3), t], C["blade"], 3)
        pen.line([at(g, u, n, 4), at(g, u, n, L - 2)], C["shine"], 1)
        pen.line([at(g, u, n, 2, 4), at(g, u, n, 2, -4)], C["guard"], 2)
        pen.line([at(g, u, n, -3), at(g, u, n, 1)], C["grip"], 2)
        pen.ell(*at(g, u, n, -5), *at(g, u, n, -3), C["guard"])
    elif kind == "staff":
        pen.line([g, at(g, u, n, L - 3)], C["wood"], 2)
        c = at(g, u, n, L)
        pen.d.ellipse(pen._p([(c[0] - 3, c[1] - 3), (c[0] + 3, c[1] + 3)]), outline=hexrgb(C["metal"]), width=1)
        for b in (-3, 3):
            p = at(g, u, n, L - 1, b)
            pen.px(p[0], p[1] + 1, C["metal"])
            pen.px(p[0], p[1] + 2, C["metal"])
    elif kind == "vajra":
        c = at(g, u, n, 1)
        for s in (-1, 1):
            tip = at(c, u, n, s * 6)
            for b in (-2, 0, 2):
                pen.line([at(c, u, n, s * 2, 0), at(c, u, n, s * 4.5, b), tip], C["metal"], 1)
        pen.ell(c[0] - 1.5, c[1] - 1.5, c[0] + 1.5, c[1] + 1.5, C["core"])
    elif kind == "crystal":
        pen.line([at(g, u, n, -4), at(g, u, n, L * 0.75)], C["metal"], 2)
        tip = at(g, u, n, L * 0.75)
        pen.poly([at(tip, u, n, 0, 0), at(tip, u, n, 3, 3), at(tip, u, n, 8, 0), at(tip, u, n, 3, -3)], C["gem"])
    elif kind == "lotus":
        pen.line([at(g, u, n, -4), at(g, u, n, L * 0.7)], C["metal"], 2)
        tip = at(g, u, n, L * 0.7)
        for b, col in ((-3, C["petal"]), (3, C["petal"]), (0, C["petal2"])):
            p = at(tip, u, n, 3 if b else 5, b)
            pen.ell(p[0] - 2, p[1] - 2, p[0] + 2, p[1] + 2, col)
    elif kind == "khatvanga":
        pen.line([g, at(g, u, n, L - 4)], C["wood"], 2)
        for k, col in ((L - 10, C["head1"]), (L - 7, C["head2"]), (L - 4, C["skull"])):
            p = at(g, u, n, k)
            pen.ell(p[0] - 1.5, p[1] - 1.5, p[0] + 1.5, p[1] + 1.5, col)
        tip = at(g, u, n, L - 3)
        pen.line([tip, at(g, u, n, L + 3)], C["metal"], 1)
        for b in (-3, 3):
            pen.line([tip, at(tip, u, n, 2, b), at(tip, u, n, 5, b)], C["metal"], 1)
        pen.line([at(g, u, n, L - 9, 1), at(g, u, n, L - 14, 4)], C["ribbon"], 1)
    elif kind == "phurba":
        base_ = at(g, u, n, 4)
        tip = at(g, u, n, max(14, L * 0.9))
        pen.poly([at(base_, u, n, 0, -3), at(base_, u, n, 0, 3), tip], C["blade"])
        pen.line([at(base_, u, n, 1), tip], C["shine"], 1)
        pen.line([at(g, u, n, -3), at(g, u, n, 3)], C["grip"], 2)
        for k in (-4, 3):
            p = at(g, u, n, k)
            pen.ell(p[0] - 2, p[1] - 2, p[0] + 2, p[1] + 2, C["knot"])


def shield(pen, kind, box, C, side):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if kind == "kite":
        w, h = (x1 - x0) / 2, (y1 - y0) / 2
        pen.poly([(cx - w, cy - h), (cx + w, cy - h), (cx + w, cy), (cx, cy + h + 2), (cx - w, cy)], C["rim"])
        pen.poly([(cx - w + 2, cy - h + 2), (cx + w - 2, cy - h + 2), (cx + w - 2, cy), (cx, cy + h - 1), (cx - w + 2, cy)], C["face"])
        pen.ell(cx - 2, cy - 3, cx + 2, cy + 1, C["emblem"])
        for k in range(8):
            a = k * math.pi / 4
            pen.px(cx + math.cos(a) * 3.5, cy - 1 + math.sin(a) * 3.5, C["emblem"])
    elif kind == "mirror":
        r = min(x1 - x0, y1 - y0) / 2
        rx = r * (0.55 if side else 1)
        pen.ell(cx - rx, cy - r, cx + rx, cy + r, C["rim"])
        pen.ell(cx - rx + 1.5, cy - r + 1.5, cx + rx - 1.5, cy + r - 1.5, C["face"])
        pen.px(cx - rx / 3, cy - r / 3, C["shine"])
        pen.px(cx - rx / 3 + 1, cy - r / 3, C["shine"])
        pen.px(cx - rx / 3, cy - r / 3 + 1, C["shine"])


# ---------------------------------------------------------------- the hats (original pixel pictures)
REY_CROWN = """
.Y......Y.Y......Y.
.YY....YYYYY....YY.
.YyY..YyyPyyY..YyY.
.YyyYYyyyPyyyYYyyY.
.YyyyyyyyyyyyyyyyY.
YYYYYYYYYYYYYYYYYYY
YPyyWyyyyPyyyyWyyPY
YYYYYYYYYYYYYYYYYYY
"""
LOTUS_TIARA = """
........pp........
.......pPPp.......
...pp.pPPPPp.pp...
..pPPppPPPPppPPp..
..pPPPPPPPPPPPPp..
YYYYYYYYYYYYYYYYYY
YyyByyyyyyyyyByyyY
"""
DIADEM = """
........B........
.......BbB.......
.S....SBBBS....S.
SSSSSSSSSSSSSSSSS
SsssssssssssssssS
"""
LOTUS_CROWN = """
........YY.........
.......YrrY........
...Y..YrrrrY..Y....
..YrY.YrRRrY.YrY...
..YrrYYrRRrYYrrY...
.YrrrrrrrrrrrrrrY..
YYYYYYYYYYYYYYYYYY.
YyRyyyyyyRyyyyyyRY.
YYYYYYYYYYYYYYYYYY.
"""
SKULL_CROWN = """
WWW.WWW.WWW.WWW.WWW
kWk.kWk.kWk.kWk.kWk
WWW.WWW.WWW.WWW.WWW
.w...w...w...w...w.
YYYYYYYYYYYYYYYYYYY
YyRyyyyyRyyyyyRyyyY
"""
TOPKNOT = """
........yYy........
.......yYwYy.......
........yYy........
.........k.........
.......kkkkk.......
......kkkkkkk......
......YYYYYYY......
YYYYYYYYYYYYYYYYYYY
yOyyyOyyyOyyyOyyyOy
"""
CONE_HAT = """
...........HH...........
.........HHhhHH.........
.......HHhhkhhhHH.......
.....HHhhhhhhhkhhHH.....
...HHhkhhhhhhhhhhhhHH...
.HHhhhhhhhkhhhhhkhhhhHH.
HhhhhhhhhhhhhhhhhhhhhhhH
.HHHHHHHHHHHHHHHHHHHHHH.
"""
PANDITA_HAT = """
...........HH...........
..........HrrH..........
..........HrrH..........
.........HrrrrH.........
.........HrrrrH.........
........HrrrrrrH........
........HrryyrrH........
.......HrrrrrrrrH.......
......HrrrrrrrrrrH......
.....HrrrrrrrrrrrrH.....
....HyyyyyyyyyyyyyyH....
...HrrrrrrrrrrrrrrrrH...
..HrrrHHHHHHHHHHHHrrrH..
..Hrrr............rrrH..
..Hrrr............rrrH..
..Hrrr............rrrH..
..Hyyy............yyyH..
...HH..............HH...
"""
GOLD = ["#1a1002", "#5a3808", "#a8701a", "#e8b030", "#ffe07a", "#fffbe0"]
BONE = "#f0e8d0"
WOOD = "#7a4a22"


# ---------------------------------------------------------------- the eleven sets, piece by piece
# Each piece: a list of (layer, draw) where layer is "back" (behind the body), "main" (the probe's own
# z for that kind of piece) or "hat"; draw(pen, P, side, M, A) paints one frame. Weapons and shields
# are drawn on their own (WEAPONS, SHIELDS), along the base's probe weapon.
def _g(fn, *a, **k):
    return lambda pen, P, side, M, A: fn(pen, P, *[x(M, A) if callable(x) else x for x in a], side, **{kk: (v(M, A) if callable(v) else v) for kk, v in k.items()})


m = lambda i: (lambda M, A: M[i])
c = lambda i: (lambda M, A: A[i])


def _hat(grid, pal_fn, lift, mirror=False):
    def draw(pen, P, side, M, A):
        pal = pal_fn(M, A)
        hat(pen, P, paint(mirror_grid(grid) if mirror else grid, pal), lift, side)
    return draw


def _hood(pen, P, side, M, A):
    hood(pen, P, M[3], side, trim=A[3])


def _robe(length="ankle", sleeve=(0, 1), main=3, cuff=None, fold=True, sh=None, neck=None, beads=None, skulls=False, pants_=None, tab=None, stripes=None, ragged=False, sleeves_=True, skirt_col=None, bare=False):
    def draw(pen, P, side, M, A):
        arms = arms_in_order(P, side)
        col = M[main]
        if pants_:
            pants(pen, P, pants_(M, A), side)
        if sleeves_ and len(arms) > 1 and 0 in sleeve:
            sleeves(pen, P, col, cuff(M, A) if cuff else None, side, which=(0,))
        if not bare:
            torso_shape(pen, P, col, side)
        skirt(pen, P, skirt_col(M, A) if skirt_col else col, length, side, folds=M[max(0, main - 1)] if fold else None, stripes=stripes(M, A) if stripes else None, ragged=ragged)
        if tab:
            tabard(pen, P, tab(M, A), side)
        if sh:
            shawl(pen, P, sh(M, A), side, trim=A[4])
        if neck:
            scarf(pen, P, neck(M, A), side)
        if beads:
            necklace(pen, P, beads(M, A), side, skulls=skulls)
        if sleeves_:
            which = tuple(k for k in sleeve if k == 1 or len(arms) == 1)
            sleeves(pen, P, col, cuff(M, A) if cuff else None, side, which=which)
    return draw


def _armour(pen, P, side, M, A):
    pants(pen, P, M[1], side)
    sleeves(pen, P, A[2], None, side, which=(0,))
    armour(pen, P, A[3], A[1], A[4], side)
    tabard(pen, P, M[3], side, emblem=A[4])
    sleeves(pen, P, A[2], A[4], side, which=(1,))


def _cape(col, trim=None, ragged=False):
    return lambda pen, P, side, M, A: cape(pen, P, col(M, A), side, trim=trim(M, A) if trim else None, ragged=ragged)


SETS_ART = {
    "pastor": {
        "yelmotumbaga": [("hat", _hood)],
        "corazatumbaga": [("back", _cape(m(2))), ("main", _robe("knee", pants_=c(1), cuff=c(3)))],
        "cintotumbaga": [("main", _g(belt, c(3), kind="rope"))],
        "grebastumbaga": [("main", _g(feet, "#6a4422", kind="sandal"))],
    },
    "barquero": {
        "yelmoluna": [("hat", _hat(CONE_HAT, lambda M, A: {"H": A[1], "h": A[3], "k": A[2]}, 3))],
        "mantoluna": [("main", _robe("knee", pants_=m(2), main=3, fold=False, neck=c(3)))],
        "cordonluna": [("main", _g(belt, c(3), kind="sash"))],
        "zapatosluna": [("main", _g(feet, c(1), kind="sandal"))],
    },
    "rey": {
        "yelmosombra": [("hat", _hat(REY_CROWN, lambda M, A: {"Y": A[3], "y": A[2], "P": M[3], "W": "#ffffff"}, 3))],
        "corazasombra": [("back", _cape(m(2), trim=c(4))), ("main", _armour)],
        "guantessombra": [("main", _g(hands, c(3), kind="glove", cuff=c(4)))],
        "cintosombra": [("main", _g(belt, c(2), kind="belt", buckle=c(4)))],
    },
    "shakya": {
        "corazasombra": [("main", _robe("ankle", sleeve=(0,), sh=c(3), main=3))],
        "cintosombra": [("main", _g(belt, c(2), kind="rope"))],
        "pezunassombra": [("main", _g(feet, "#7a4a22", kind="sandal"))],
    },
    "tsokye": {
        "capiroteastral": [("hat", _hat(LOTUS_TIARA, lambda M, A: {"p": A[3], "P": A[4], "Y": GOLD[3], "y": GOLD[2], "B": M[3]}, 4))],
        "vestiduraastral": [("main", _robe("ankle", main=3, cuff=c(3), beads=lambda M, A: [A[4], GOLD[3]], stripes=None))],
        "guantesastral": [("main", _g(hands, c(3), kind="bracer", cuff=GOLD[3]))],
        "zapatillasastral": [("main", _g(feet, c(3), kind="slipper", trim=GOLD[4]))],
        "fajinastral": [("main", _g(belt, c(2), kind="sash", tail=c(3)))],
    },
    "loden": {
        "capiroteastral": [("hat", _hat(DIADEM, lambda M, A: {"B": A[3], "b": A[5], "S": M[4], "s": M[3]}, 4))],
        "vestiduraastral": [("main", _robe("ankle", main=4, cuff=c(3), sh=c(3)))],
        "guantesastral": [("main", _g(hands, m(4), kind="glove", cuff=c(3)))],
        "zapatillasastral": [("main", _g(feet, m(3), kind="slipper", trim=c(3)))],
        "fajinastral": [("main", _g(belt, c(3), kind="sash"))],
    },
    "pemagyalpo": {
        "capiroteastral": [("hat", _hat(LOTUS_CROWN, lambda M, A: {"Y": A[3], "y": A[2], "r": M[3], "R": M[4]}, 3))],
        "vestiduraastral": [("back", _cape(m(1), trim=c(3))), ("main", _robe("ankle", main=3, cuff=c(3), beads=lambda M, A: [A[3], A[4]]))],
        "guantesastral": [("main", _g(hands, c(3), kind="glove"))],
        "zapatillasastral": [("main", _g(feet, c(3), kind="slipper", trim="#ffffff"))],
    },
    "pandita": {
        "capiroteastral": [("hat", _hat(PANDITA_HAT, lambda M, A: {"H": M[0], "r": M[3], "y": A[4]}, 8))],
        "vestiduraastral": [("main", _robe("ankle", main=2, cuff=c(3), sh=m(3)))],
        "guantesastral": [("main", _g(hands, c(3), kind="bracer"))],
        "zapatillasastral": [("main", _g(feet, m(1), kind="boot", trim=c(3)))],
        "fajinastral": [("main", _g(belt, c(3), kind="sash"))],
    },
    "nyima": {
        "capiroteastral": [("hat", _hat(TOPKNOT, lambda M, A: {"Y": M[3], "y": M[2], "w": "#ffffff", "k": "#2a1a0a", "O": A[3]}, 6))],
        "vestiduraastral": [("main", _robe("knee", main=3, bare=True, sleeves_=False, fold=False, skirt_col=c(3), stripes=lambda M, A: "#140600", beads=lambda M, A: [BONE, "#c8b898"]))],
        "guantesastral": [("main", _g(hands, BONE, kind="beads"))],
        "zapatillasastral": [("main", _g(feet, BONE, kind="anklet"))],
        "fajinastral": [("main", _g(belt, c(3), kind="obi", stripes="#140600"))],
    },
    "sengedradrok": {
        "capiroteastral": [("hat", _hat(SKULL_CROWN, lambda M, A: {"W": BONE, "k": "#140a04", "w": BONE, "Y": GOLD[3], "y": GOLD[2], "R": "#e03030"}, 3))],
        "vestiduraastral": [("back", _cape(c(1), ragged=True)), ("main", _robe("knee", main=3, sleeves_=False, skirt_col=c(2), ragged=True, fold=False, beads=lambda M, A: [BONE, "#140a04"], skulls=True))],
        "guantesastral": [("main", _g(hands, c(3), kind="bracer", cuff=GOLD[3]))],
        "zapatillasastral": [("main", _g(feet, m(2), kind="boot", trim=c(3)))],
        "fajinastral": [("main", _g(belt, c(3), kind="sash", tail=c(4)))],
    },
    "drollo": {
        "capiroteastral": [("hat", _hat(SKULL_CROWN, lambda M, A: {"W": BONE, "k": "#140a04", "w": BONE, "Y": GOLD[3], "y": GOLD[2], "R": "#30c050"}, 3))],
        "vestiduraastral": [("back", _cape(m(2), ragged=True)), ("main", _robe("knee", main=3, sleeves_=False, skirt_col=c(3), stripes=lambda M, A: "#140600", ragged=True, fold=False, beads=lambda M, A: [BONE, "#140a04"], skulls=True))],
        "guantesastral": [("main", _g(hands, c(3), kind="bracer", cuff=GOLD[3]))],
        "zapatillasastral": [("main", _g(feet, m(3), kind="boot", trim=c(4)))],
        "fajinastral": [("main", _g(belt, c(3), kind="sash", stripes="#140600"))],
    },
}
WEAPONS = {  # (set, base): (kind, colours)
    ("pastor", "baculotumbaga"): ("crook", lambda M, A: {"wood": WOOD}),
    ("barquero", "tridenteluna"): ("pole", lambda M, A: {"wood": A[2], "metal": M[2]}),
    ("rey", "mandoblesombra"): ("sword", lambda M, A: {"blade": "#d8e0ea", "shine": "#ffffff", "guard": A[3], "grip": M[2]}),
    ("shakya", "varasombra"): ("staff", lambda M, A: {"wood": WOOD, "metal": GOLD[3]}),
    ("tsokye", "espadaastral"): ("vajra", lambda M, A: {"metal": GOLD[3], "core": A[4]}),
    ("loden", "espadaastral"): ("crystal", lambda M, A: {"metal": M[4], "gem": A[4]}),
    ("pemagyalpo", "espadaastral"): ("lotus", lambda M, A: {"metal": A[3], "petal": M[3], "petal2": M[4]}),
    ("pandita", "lanzaastral"): ("khatvanga", lambda M, A: {"wood": WOOD, "metal": GOLD[3], "head1": M[3], "head2": "#30c050", "skull": BONE, "ribbon": A[4]}),
    ("nyima", "lanzaastral"): ("khatvanga", lambda M, A: {"wood": M[2], "metal": M[4], "head1": "#e03030", "head2": "#30c050", "skull": BONE, "ribbon": A[3]}),
    ("sengedradrok", "espadaastral"): ("vajra", lambda M, A: {"metal": M[4], "core": A[4]}),
    ("drollo", "espadaastral"): ("phurba", lambda M, A: {"blade": "#9aa4b0", "shine": "#e8eef4", "grip": GOLD[2], "knot": GOLD[3]}),
}
SHIELDS = {
    ("rey", "escudosombra"): ("kite", lambda M, A: {"rim": A[3], "face": M[3], "emblem": A[4]}),
    ("pemagyalpo", "escudoastral"): ("mirror", lambda M, A: {"rim": A[3], "face": "#c8d8e8", "shine": "#ffffff"}),
}


def has_art(sid, base):
    return base in SETS_ART.get(sid, {}) or (sid, base) in WEAPONS or (sid, base) in SHIELDS


# ---------------------------------------------------------------- frames out, in build_lpc's formats
_POSES = {}


def poses(B, body):
    if body not in _POSES:
        _POSES[body] = {k: pose_of(m) for k, m in probe_frames(B, body).items()}
    return _POSES[body]


def slot_of(base):
    for pre, slot in (("yelmo", "head"), ("capirote", "head"), ("coraza", "body"), ("manto", "body"), ("vestidura", "body"),
                      ("cinto", "belt"), ("cordon", "belt"), ("fajin", "belt"), ("grebas", "feet"), ("zapat", "feet"),
                      ("pezunas", "feet"), ("guantes", "hands"), ("brazales", "hands")):
        if base.startswith(pre):
            return slot
    return None


def _z(kind, base):
    if kind == "back":
        return 5
    if kind == "hat":
        return 130
    return {"body": ZS.get("torso", 35) + 2, "belt": ZS.get("belt", 50) + 2, "feet": ZS.get("feet", 15) + 2,
            "hands": ZS.get("hands", 40) + 6}.get(slot_of(base), 50)


def _cell(img64_or_none):
    return img64_or_none


def garment(B, sid, base, body, M, A):
    P = poses(B, body)
    layers, alayers = [], []
    for kind, fn in SETS_ART[sid][base]:
        z = _z(kind, base)
        fr = {}
        for row, key in ((B.SOUTH, ("south", 0)), (B.EAST, ("east", 0))):
            if key in P:
                pen = Pen(128, 32)
                fn(pen, P[key], key[0] in SIDE, M, A)
                fr[row] = finish(pen.im)
        layers.append((z, fr))
        rows = {}
        for a in B.ANIMS:
            n = max((i for (aa, i) in P if aa == a), default=-1) + 1
            if not n:
                continue
            strip = Image.new("RGBA", (F * n, F))
            for i in range(n):
                pen = Pen(F, 0)
                fn(pen, P[(a, i)], a in SIDE, M, A)
                strip.alpha_composite(finish(pen.im), (i * F, 0))
            if strip.getbbox():
                rows[a] = (strip, F, n)
        alayers.append((z, rows))
    return layers, alayers


def _probe_layer(B, base, prefix):
    for name, _ in B.BAND_LOOKS[base]:
        if name.startswith(prefix):
            return name
    return None


def held(B, sid, base, body, M, A):
    """A weapon or shield, drawn along the base's own LPC weapon or shield in every frame."""
    P = poses(B, body)
    is_w = (sid, base) in WEAPONS
    kind, cols = (WEAPONS if is_w else SHIELDS)[(sid, base)]
    C = cols(M, A)
    probe = _probe_layer(B, base, "weapon_" if is_w else "shield_")

    def draw(mask, size, off, key):
        pen = Pen(size, 0)
        pts = mask
        if not pts:
            return pen.im
        pose = P.get(key, {})
        if is_w:
            hs = [(x + off, y + off) for x, y in pose.get("hands", [])]
            cx, cy = _centre(pts)
            hand = min(hs, key=lambda h: (h[0] - cx) ** 2 + (h[1] - cy) ** 2) if hs else None
            ax = weapon_axis(pts, hand, heavy_tip=kind in ("crook", "pole", "staff", "khatvanga"))
            if not ax:
                return pen.im
            g, t, L = ax
            if kind in ("crook", "pole", "staff", "khatvanga"):
                pass  # a long staff runs the probe's whole length, butt to head
            elif kind == "vajra" and hand is not None:
                g = hand  # held in the fist
            elif hand is not None and math.hypot(g[0] - hand[0], g[1] - hand[1]) < 8:
                g = hand
            weapon(pen, kind, g, t, C)
        else:
            shield(pen, kind, _bbox(pts), C, key[0] in SIDE)
        return finish(pen.im)

    lf = B.layer_frames(probe, body)
    z = max((zz for zz, _ in lf), default=140)
    fr = {}
    for row, key in ((B.SOUTH, ("south", 0)), (B.EAST, ("east", 0))):
        mask = set()
        for _, f in lf:
            if row in f:
                mask |= _mask(f[row])
        fr[row] = draw(mask, 128, 32, key)
    rows = {}
    by_anim = {}
    for _, rs in B.anim_layers(probe, body):
        for a, (strip, fs, n) in rs.items():
            by_anim.setdefault(a, []).append((strip, fs, n))
    for a, lst in by_anim.items():
        fs = max(x[1] for x in lst)
        n = max(x[2] for x in lst)
        strip = Image.new("RGBA", (fs * n, fs))
        for i in range(n):
            mask = set()
            for im, f2, n2 in lst:
                if i < n2:
                    o2 = (fs - f2) // 2
                    mask |= {(x + o2, y + o2) for x, y in _mask(im.crop((i * f2, 0, (i + 1) * f2, f2)))}
            strip.alpha_composite(draw(mask, fs, (fs - F) // 2, (a, i)), (i * fs, 0))
        if strip.getbbox():
            rows[a] = (strip, fs, n)
    return [(z, fr)], [(z, rows)]


def piece(B, sid, base, body, M, A):
    """(layers, alayers) for one piece of one of the eleven sets, all drawn here."""
    if (sid, base) in WEAPONS or (sid, base) in SHIELDS:
        return held(B, sid, base, body, M, A)
    return garment(B, sid, base, body, M, A)
