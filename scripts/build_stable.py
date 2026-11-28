"""The stable's animals, drawn in code: original pixel art, no outside files.

Levels 2-20 of pets and mounts (data.js PET_KINDS / MOUNT_KINDS), three coats each. The level-1 dog
and horse come from LPC art (scripts/build_companions.py). One standing frame, facing east like the
hero, at native size: the game scales them like the hero.

Mounts are drawn on the horse's 64x61 canvas with their back where the horse's is (top of the back at
y ~ 20 between x 16 and 34), because the rider is drawn sitting there (figure.js HX/HY).

Shapes are drawn flat; then every shape gets light from above (its top row lighter, its bottom row
darker) and the whole animal a dark outline in a shade of the colour next to it.

Writes public/rpg/lpc/companions/{pet,mount}-<kind>-<coat>.png
usage: .venv/bin/python scripts/build_stable.py [kind ...]   (no kinds: all) [--sheet out.png]
"""
import math, os, sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "public", "rpg", "lpc", "companions")


def rgb(h, a=255):
    if isinstance(h, tuple):
        return h if len(h) == 4 else (*h, a)
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def mix(c1, c2, t):
    c1, c2 = rgb(c1), rgb(c2)
    return tuple(round(a + (b - a) * t) for a, b in zip(c1[:3], c2[:3])) + (255,)


def dk(c, t=0.35):
    return mix(c, "#140c10", t)


def lt(c, t=0.3):
    return mix(c, "#fff6e0", t)


class Pic:
    """Flat shapes in float coordinates; each shape is its own layer for the shading."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.im = Image.new("RGBA", (w, h))
        self.flat = []  # (mask, colour, shade?) in drawing order

    def _new(self):
        m = Image.new("L", (self.w, self.h))
        return m, ImageDraw.Draw(m)

    def _put(self, m, col, shade):
        self.flat.append((m, rgb(col), shade))

    def ell(self, cx, cy, rx, ry, col, shade=True):
        m, d = self._new()
        d.ellipse((round(cx - rx), round(cy - ry), round(cx + rx), round(cy + ry)), fill=255)
        self._put(m, col, shade)

    def poly(self, pts, col, shade=True):
        m, d = self._new()
        d.polygon([(round(x), round(y)) for x, y in pts], fill=255)
        self._put(m, col, shade)

    def line(self, pts, col, w=1, shade=False):
        m, d = self._new()
        d.line([(round(x), round(y)) for x, y in pts], fill=255, width=w)
        self._put(m, col, shade)

    def rect(self, x0, y0, x1, y1, col, shade=True):
        m, d = self._new()
        d.rectangle((round(x0), round(y0), round(x1), round(y1)), fill=255)
        self._put(m, col, shade)

    def px(self, x, y, col):
        m, d = self._new()
        d.point((round(x), round(y)), fill=255)
        self._put(m, col, False)

    def limb(self, x0, y0, x1, y1, w, col, shade=True, foot=None, taper=0.7):
        """A leg: a tapered quad from (x0, y0) w wide to (x1, y1) narrower (taper)."""
        w2 = max(1.5, w * taper)
        self.poly([(x0 - w / 2, y0), (x0 + w / 2, y0), (x1 + w2 / 2, y1), (x1 - w2 / 2, y1)], col, shade)
        if foot:
            self.rect(x1 - w2 / 2, y1 - 1, x1 + w2 / 2, y1, foot, False)

    def curve(self, pts, w, col, shade=True, taper=0.4):
        """A thick curve through points (tails, necks): a chain of discs, thinning toward the end."""
        n = len(pts) - 1
        for i in range(n):
            (ax, ay), (bx, by) = pts[i], pts[i + 1]
            steps = max(2, int(math.hypot(bx - ax, by - ay) * 2))
            for s in range(steps + 1):
                t = s / steps
                u = (i + t) / n
                r = (w / 2) * (1 - (1 - taper) * u)
                self.ell(ax + (bx - ax) * t, ay + (by - ay) * t, r, r, col, shade=False)
        # one mask for the shading
        self._merge_last(sum(max(2, int(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) * 2)) + 1 for i in range(n)), col, shade)

    def _merge_last(self, k, col, shade):
        parts = self.flat[-k:]
        del self.flat[-k:]
        m = Image.new("L", (self.w, self.h))
        for pm, _, _ in parts:
            m.paste(255, mask=pm)
        self._put(m, col, shade)

    def render(self):
        im = Image.new("RGBA", (self.w, self.h))
        W, H = self.w, self.h
        for m, col, shade in self.flat:
            mp = m.load()
            layer = Image.new("RGBA", (W, H))
            lp = layer.load()
            for y in range(H):
                for x in range(W):
                    if not mp[x, y]:
                        continue
                    c = col
                    if shade:
                        up = y == 0 or not mp[x, y - 1]
                        down = y == H - 1 or not mp[x, y + 1]
                        if up:
                            c = lt(col, 0.28)
                        elif down or (y < H - 2 and not mp[x, y + 2]):
                            c = dk(col, 0.22)
                    lp[x, y] = c
            im.alpha_composite(layer)
        # the outline: transparent pixels touching the animal take a dark shade of their neighbour
        px = im.load()
        out = im.copy()
        op = out.load()
        for y in range(H):
            for x in range(W):
                if px[x, y][3]:
                    continue
                nb = [px[x + dx, y + dy] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= x + dx < W and 0 <= y + dy < H and px[x + dx, y + dy][3]]
                if nb:
                    c = min(nb, key=lambda c: sum(c[:3]))
                    op[x, y] = dk(c, 0.62)
        return out


# ---------------------------------------------------------------- pets (on a 52x40 canvas, trimmed)
PW, PH = 52, 40
G = PH - 2  # the ground line (feet end here)


def cat(p, c, spots=None, big=1.0, stripes=None):
    k = big
    bx, by = 22, G - 9 * k
    # tail curling up behind
    p.curve([(bx - 10 * k, by), (bx - 16 * k, by - 4 * k), (bx - 17 * k, by - 11 * k), (bx - 14 * k, by - 15 * k)], 3.2 * k, c["main"])
    for lx in (bx - 8 * k, bx - 5 * k):
        p.limb(lx, by + 2, lx - 0.5, G, 3.2 * k, c["dark"], foot=c["light"])
    p.ell(bx, by, 11 * k, 5.2 * k, c["main"])
    for lx in (bx + 6 * k, bx + 9 * k):
        p.limb(lx, by + 2, lx + 0.5, G, 3.2 * k, c["main"], foot=c["light"])
    p.ell(bx + 1, by + 3 * k, 8 * k, 2.2 * k, c["light"], shade=False)
    hx, hy = bx + 13 * k, by - 7 * k
    p.ell(hx, hy, 5.2 * k, 4.6 * k, c["main"])
    p.poly([(hx - 4.5 * k, hy - 2 * k), (hx - 3.5 * k, hy - 8 * k), (hx - 0.5 * k, hy - 3.5 * k)], c["main"])
    p.poly([(hx + 0.5 * k, hy - 3.5 * k), (hx + 2.5 * k, hy - 8.5 * k), (hx + 4.5 * k, hy - 2.5 * k)], c["main"])
    p.px(hx + 2.5 * k, hy - 5.5 * k, c["ear"])
    p.ell(hx + 3.2 * k, hy + 1.5 * k, 2.4 * k, 1.8 * k, c["light"], shade=False)
    p.px(hx + 2 * k, hy - 1 * k, c["eye"]); p.px(hx + 2 * k + 1, hy - 1 * k, c["eye"])
    p.px(hx + 5.2 * k, hy + 0.8 * k, "#3a2020")
    if stripes:
        for i in range(4):
            x = bx - 6 * k + i * 4 * k
            p.line([(x, by - 4.5 * k), (x + 1.5, by - 1.5 * k)], stripes, 1)
        p.line([(hx - 1, hy - 4 * k), (hx, hy - 2.5 * k)], stripes, 1)
    if spots:
        for (sx, sy) in ((-6, -2), (-2, -3), (2, -2), (6, -3), (-4, 1), (0, 0.5), (4, 1), (8, -0.5), (-8, 0)):
            p.ell(bx + sx * k, by + sy * k, 1.3 * k, 1.0 * k, spots, shade=False)
            p.px(bx + sx * k, by + sy * k, c["main"])


def d_gato(p, c):
    cat(p, c, stripes=c.get("mark"))


def d_ocelote(p, c):
    cat(p, c, spots=c["mark"], big=1.3)


def d_cuy(p, c):
    bx, by = 24, G - 6
    p.ell(bx, by, 10, 6.5, c["main"])
    if c.get("mark"):
        p.ell(bx - 4, by - 2, 4.5, 4, c["mark"], shade=False)
        p.ell(bx + 6, by - 3, 3, 3, c["mark"], shade=False)
    p.ell(bx + 1, by + 4, 7, 2, c["light"], shade=False)
    for lx in (bx - 6, bx - 2, bx + 4, bx + 7):
        p.rect(lx, G - 1, lx + 1, G, c["dark"], False)
    p.ell(bx + 8, by - 3, 1.8, 1.6, c["ear"])
    p.px(bx + 7, by - 1, c["eye"])
    p.px(bx + 10, by + 0, "#3a2020")


def d_conejo(p, c):
    bx, by = 22, G - 7
    p.ell(bx - 9, by - 1, 2.6, 2.6, c["light"])  # the scut
    p.ell(bx - 4, by + 2, 6, 5, c["dark"])  # the haunch
    p.ell(bx, by, 9.5, 6, c["main"])
    p.limb(bx + 6, by + 2, bx + 7, G, 2.4, c["main"], foot=c["light"])
    p.poly([(bx - 10, G), (bx - 1, G), (bx - 3, G - 2)], c["main"])
    hx, hy = bx + 9, by - 6
    p.ell(hx, hy, 4.6, 4.2, c["main"])
    p.poly([(hx - 3, hy - 2), (hx - 6, hy - 14), (hx - 3.5, hy - 14), (hx - 0.5, hy - 3)], c["main"])
    p.poly([(hx - 0.5, hy - 3), (hx, hy - 15), (hx + 2.5, hy - 14), (hx + 2, hy - 2)], c["main"])
    p.line([(hx + 1, hy - 4), (hx + 1.2, hy - 12)], c["ear"], 1)
    p.px(hx + 2, hy - 1, c["eye"])
    p.px(hx + 4.5, hy + 1, "#4a2a2a")


def d_morrocoy(p, c):
    bx, by = 24, G - 7
    p.curve([(bx + 9, by + 1), (bx + 13, by - 2), (bx + 15, by - 2)], 3.5, c["skin"])
    p.ell(bx + 16, by - 2.5, 3, 2.4, c["skin"])
    p.px(bx + 17, by - 3, c["eye"])
    for lx, mk in ((bx - 8, 0), (bx - 3, 1), (bx + 4, 0), (bx + 8, 1)):
        p.limb(lx, by + 2, lx, G, 3.2, c["skin"])
        if c.get("legspot") and mk:
            p.px(lx, G - 2, c["legspot"])
    p.poly([(bx - 13, by + 3), (bx + 12, by + 3), (bx + 10, by + 5), (bx - 11, by + 5)], c["dark"])
    p.ell(bx, by - 1, 12, 8, c["main"])
    p.rect(bx - 13, by + 2, bx + 12, by + 4, c["main"])
    for (sx, sy) in ((-6, -3), (0, -5), (6, -3), (-8, 1), (-2, 0), (4, 0), (9, 1)):
        p.poly([(bx + sx - 2, sy + by), (bx + sx, sy + by - 2), (bx + sx + 2, sy + by), (bx + sx, sy + by + 2)], c["mark"], shade=False)


def d_ardilla(p, c):
    bx, by = 26, G - 7
    p.curve([(bx - 6, by + 4), (bx - 13, by + 1), (bx - 15, by - 7), (bx - 11, by - 14), (bx - 6, by - 15)], 7, c["main"], taper=0.8)
    p.curve([(bx - 13, by - 2), (bx - 13, by - 8), (bx - 10, by - 12)], 2, c["light"], shade=False)
    p.ell(bx - 2, by + 1, 6, 6, c["main"])
    p.ell(bx + 3, by - 3, 4.5, 6, c["main"])
    p.ell(bx + 4, by, 2.5, 4, c["light"], shade=False)
    p.limb(bx - 4, by + 4, bx - 1, G, 3.5, c["dark"])
    p.limb(bx + 5, by - 1, bx + 7, by + 3, 2, c["main"])
    hx, hy = bx + 6, by - 9
    p.ell(hx, hy, 4.3, 3.8, c["main"])
    p.poly([(hx - 3, hy - 2), (hx - 2.5, hy - 7), (hx, hy - 3)], c["main"])
    p.px(hx + 1, hy - 1, c["eye"])
    p.px(hx + 4, hy + 1, "#3a2020")


def bird(p, c, bx, by, size=1.0, beak=None, tail=8, crest=False):
    k = size
    p.poly([(bx - 4 * k, by + 3 * k), (bx - 4 * k - tail * 0.3, by + 3 * k + tail), (bx - 1 * k - tail * 0.2, by + 3 * k + tail), (bx, by + 3 * k)], c["tail"])
    for lx in (bx - 1, bx + 2):
        p.line([(lx, by + 4 * k), (lx, G)], "#7a6a5a")
        p.line([(lx, G), (lx + 1.5, G)], "#7a6a5a")
    p.ell(bx, by, 5 * k, 6 * k, c["main"])
    p.ell(bx + 1.5 * k, by + 1.5 * k, 3 * k, 3.5 * k, c["belly"], shade=False)
    p.poly([(bx - 5 * k, by - 2 * k), (bx + 1 * k, by - 1 * k), (bx - 1 * k, by + 6 * k), (bx - 5.5 * k, by + 5 * k)], c["wing"])
    p.line([(bx - 4 * k, by + 2 * k), (bx - 1 * k, by + 4 * k)], dk(c["wing"], 0.3))
    hx, hy = bx + 2 * k, by - 6 * k
    p.ell(hx, hy, 3.8 * k, 3.5 * k, c["head"])
    if crest:
        p.poly([(hx - 2, hy - 3), (hx - 4, hy - 7), (hx, hy - 3.5)], c["head"])
    if c.get("face"):
        p.ell(hx + 1.2 * k, hy, 2 * k, 1.8 * k, c["face"], shade=False)
    p.px(hx + 1.5 * k, hy - 0.5 * k, c["eye"])
    return hx, hy


def d_loro(p, c):
    hx, hy = bird(p, c, 22, G - 10, 1.0, tail=8)
    p.poly([(hx + 3, hy - 1.5), (hx + 6, hy - 0.5), (hx + 5.5, hy + 2.5), (hx + 3, hy + 1.5)], c["beak"])
    p.px(hx + 5, hy + 2, dk(c["beak"], 0.4))


def d_guacamaya(p, c):
    hx, hy = bird(p, c, 26, G - 14, 1.25, tail=1)
    p.poly([(22, G - 10), (12, G + 0), (15, G + 1), (25, G - 9)], c["tail"])
    p.poly([(23, G - 10), (9, G - 3), (11, G - 1), (25, G - 9)], dk(c["tail"], 0.15))
    p.poly([(hx + 3.5, hy - 2), (hx + 7, hy - 1), (hx + 6.5, hy + 3), (hx + 3.5, hy + 2)], "#2a2626")
    p.ell(hx + 1.2, hy - 0.2, 1.8, 1.6, "#f4eee6", shade=False)
    p.px(hx + 1.5, hy - 0.4, "#111")


def d_tucan(p, c):
    hx, hy = bird(p, c, 20, G - 10, 1.05, tail=7)
    p.poly([(hx + 2.5, hy - 2.5), (hx + 14, hy - 1), (hx + 13, hy + 1.5), (hx + 2.5, hy + 2)], c["beak"])
    p.poly([(hx + 3, hy + 0.3), (hx + 13, hy + 0.8), (hx + 13, hy + 1.6), (hx + 3, hy + 2)], c["beak2"], shade=False)
    p.px(hx + 13.5, hy, "#2a1a1a")


def d_lechuza(p, c):
    bx, by = 24, G - 11
    for lx in (bx - 2, bx + 2):
        p.rect(lx - 0.5, G - 2, lx + 1, G, "#6a5a4a", False)
    p.ell(bx, by, 7, 9, c["main"])
    p.ell(bx + 1, by + 2, 4.5, 6, c["belly"], shade=False)
    for (sx, sy) in ((0, 0), (2, 3), (-1, 5), (2, 7)):
        p.px(bx + sx, by + sy, c["mark"])
    p.poly([(bx - 7, by - 2), (bx - 2, by), (bx - 4, by + 9), (bx - 7.5, by + 7)], c["wing"])
    hx, hy = bx + 1, by - 10
    p.ell(hx, hy, 6, 5.2, c["main"])
    p.ell(hx + 0.5, hy + 0.5, 4.6, 4, c["face"], shade=False)
    p.px(hx - 1.5, hy, "#111"); p.px(hx + 2.5, hy, "#111")
    p.px(hx + 0.5, hy + 2, "#c8a050")


def d_colibri(p, c):
    bx, by = 22, G - 10
    # it hovers: a faint shadow on the ground
    p.poly([(bx - 2, by - 1), (bx - 12, by - 9), (bx - 9, by - 2), (bx - 3, by + 2)], c["wing"], shade=False)
    p.poly([(bx - 6, by + 2), (bx - 12, by + 6), (bx - 9, by + 6), (bx - 5, by + 4)], c["tail"])
    p.ell(bx, by, 5.5, 3.2, c["main"])
    p.ell(bx + 1, by + 1.2, 3.5, 1.6, c["belly"], shade=False)
    p.ell(bx + 5, by - 2, 2.8, 2.6, c["head"])
    p.px(bx + 6, by - 2.5, "#111")
    p.line([(bx + 7.5, by - 1.5), (bx + 15, by - 0.5)], "#2a2020", 1)
    p.poly([(bx - 1, by - 2), (bx - 6, by - 11), (bx - 2, by - 10), (bx + 2, by - 2)], c["wing"])
    p.px(bx - 3, by - 7, lt(c["wing"], 0.5))


def d_armadillo(p, c):
    bx, by = 22, G - 6
    p.poly([(bx - 9, by + 2), (bx - 16, by + 4), (bx - 9, by + 4)], c["skin"])
    for lx in (bx - 6, bx - 2, bx + 4, bx + 7):
        p.limb(lx, by + 2, lx, G, 2.5, c["skin"])
    p.ell(bx, by, 10, 6.5, c["main"])
    p.rect(bx - 10, by, bx + 10, by + 3, c["main"])
    for i in range(-3, 4):
        p.line([(bx + i * 2.4, by - 6), (bx + i * 2.6, by + 3)], dk(c["main"], 0.28))
    p.poly([(bx + 8, by - 3), (bx + 15, by + 1), (bx + 14, by + 3), (bx + 8, by + 3)], c["skin"])
    p.ell(bx + 9, by - 3.5, 1.4, 2, c["skin"])
    p.px(bx + 11, by - 0.5, "#111")


def d_chucha(p, c):
    bx, by = 22, G - 6
    p.curve([(bx - 9, by + 1), (bx - 14, by + 3), (bx - 18, by), (bx - 17, by - 3)], 1.8, c["tail"], taper=0.7)
    for lx in (bx - 6, bx - 3, bx + 4, bx + 7):
        p.limb(lx, by + 2, lx + 0.5, G, 2.2, c["dark"], foot=c["tail"])
    p.ell(bx, by, 10, 5.5, c["main"])
    p.poly([(bx + 7, by - 5), (bx + 18, by - 1), (bx + 17, by + 1), (bx + 8, by + 2)], c["face"])
    p.ell(bx + 9, by - 6, 2, 2, "#2a2020")
    p.px(bx + 12, by - 2, "#111")
    p.px(bx + 18, by - 1, "#e08a9a")


def d_titi(p, c):
    bx, by = 24, G - 7
    p.curve([(bx - 4, by + 4), (bx - 10, by + 5), (bx - 14, by + 1), (bx - 14, by - 6), (bx - 11, by - 8)], 2.6, c["tail"], taper=0.8)
    p.ell(bx, by, 5.5, 6.5, c["main"])
    p.limb(bx - 2, by + 4, bx - 3, G, 3, c["dark"])
    p.limb(bx + 3, by + 4, bx + 4, G, 3, c["dark"])
    p.limb(bx + 3, by - 2, bx + 6, by + 5, 2.2, c["main"])
    hx, hy = bx + 2, by - 9
    p.ell(hx, hy, 4.5, 4.2, c["main"])
    if c.get("crest"):
        p.poly([(hx - 4, hy - 1), (hx - 6, hy - 8), (hx - 1, hy - 4.5), (hx + 2, hy - 6), (hx + 2, hy - 3)], c["crest"])
    p.ell(hx + 2, hy + 0.5, 2.4, 2.4, c["face"], shade=False)
    p.ell(hx - 3.6, hy, 1.3, 1.5, c["face"], shade=False)
    p.px(hx + 2, hy - 0.5, "#111"); p.px(hx + 3.5, hy - 0.5, "#111")


def d_perezoso(p, c):
    bx, by = 24, G - 8
    p.ell(bx, by, 9, 7.5, c["main"])
    p.curve([(bx + 4, by - 2), (bx + 10, by + 2), (bx + 11, G - 0.5)], 2.8, c["main"])
    p.curve([(bx - 4, by + 4), (bx - 7, G - 0.5)], 3, c["dark"])
    for i in range(3):
        p.px(bx + 10 + i, G, "#e8dcc0")
    hx, hy = bx + 4, by - 8
    p.ell(hx, hy, 5, 4.6, c["main"])
    p.ell(hx + 0.8, hy + 0.4, 3.8, 3, c["face"], shade=False)
    p.line([(hx - 2, hy - 0.5), (hx + 3.6, hy - 0.5)], c["mask"], 1)
    p.px(hx - 0.5, hy - 0.5, "#111"); p.px(hx + 2.5, hy - 0.5, "#111")
    p.px(hx + 1, hy + 2, "#2a1a1a")


def d_zorro(p, c):
    bx, by = 22, G - 9
    p.curve([(bx - 9, by - 1), (bx - 15, by + 1), (bx - 19, by + 4)], 6, c["main"], taper=0.7)
    p.ell(bx - 18.5, by + 4.5, 2, 1.8, c["tip"], shade=False)
    for lx in (bx - 7, bx - 4):
        p.limb(lx, by + 2, lx - 0.5, G, 2.6, c["dark"], foot=c["dark"])
    p.ell(bx, by, 10, 4.8, c["main"])
    for lx in (bx + 5, bx + 8):
        p.limb(lx, by + 2, lx + 0.5, G, 2.6, c["main"], foot=c["dark"])
    p.ell(bx + 2, by + 3, 6, 1.6, c["light"], shade=False)
    hx, hy = bx + 12, by - 5
    p.ell(hx, hy, 4.5, 3.8, c["main"])
    p.poly([(hx + 2, hy - 2), (hx + 9, hy + 1), (hx + 8, hy + 2.5), (hx + 1, hy + 3)], c["main"])
    p.poly([(hx + 1, hy + 1.5), (hx + 8.5, hy + 2), (hx + 7.5, hy + 3), (hx + 1, hy + 3.5)], c["light"], shade=False)
    p.poly([(hx - 3.5, hy - 2), (hx - 2.5, hy - 8), (hx, hy - 3)], c["main"])
    p.poly([(hx - 0.5, hy - 3), (hx + 1.5, hy - 8), (hx + 3, hy - 2)], c["main"])
    p.px(hx + 2.5, hy - 0.5, "#111")
    p.px(hx + 9, hy + 1, "#111")


def d_rana(p, c):
    bx, by = 24, G - 5
    p.ell(bx - 5, by + 2, 5, 3.5, c["main"])
    p.ell(bx, by, 7, 5, c["main"])
    p.ell(bx + 5, by - 3, 4.5, 3.5, c["main"])
    p.ell(bx + 5, by - 6.5, 2, 2, c["main"])
    p.px(bx + 5.5, by - 7, "#111")
    p.line([(bx + 4, by + 1), (bx + 7, G)], c["main"], 2)
    p.line([(bx - 9, G), (bx - 3, G)], c["main"], 2)
    for (sx, sy) in ((-3, -2), (1, -3), (-6, 1), (2, 1)):
        p.px(bx + sx, by + sy, c["mark"])
    p.line([(bx + 7, by - 1), (bx + 9.5, by - 1.5)], dk(c["main"], 0.5))


def d_nutria(p, c):
    bx, by = 22, G - 5
    p.curve([(bx - 11, by + 1), (bx - 17, by + 3), (bx - 21, by + 4)], 4, c["main"], taper=0.4)
    for lx in (bx - 8, bx - 5, bx + 6, bx + 9):
        p.limb(lx, by + 2, lx + 0.5, G, 2.4, c["dark"])
    p.ell(bx, by, 12, 4.5, c["main"])
    p.ell(bx + 2, by + 2.5, 8, 1.6, c["light"], shade=False)
    hx, hy = bx + 13, by - 3
    p.ell(hx, hy, 4, 3.4, c["main"])
    p.ell(hx + 2.4, hy + 1, 2.4, 1.8, c["light"], shade=False)
    p.ell(hx - 2, hy - 3, 1.1, 1, c["dark"])
    p.px(hx + 1.5, hy - 1, "#111")
    p.px(hx + 4.4, hy + 0.2, "#111")


def d_hormiguero(p, c):
    bx, by = 26, G - 10
    p.poly([(bx - 9, by - 4), (bx - 20, by - 12), (bx - 24, by - 6), (bx - 22, by + 1), (bx - 9, by + 3)], c["tail"])
    for i in range(4):
        p.line([(bx - 12 - i * 3, by - 7 + i), (bx - 13 - i * 3, by + 1)], dk(c["tail"], 0.25))
    for lx in (bx - 7, bx - 3):
        p.limb(lx, by + 2, lx, G, 3.2, c["dark"])
    p.ell(bx, by, 11, 6, c["main"])
    for lx in (bx + 5, bx + 8):
        p.limb(lx, by + 2, lx + 1, G, 3.2, c["light"], foot="#2a2020")
    p.poly([(bx - 6, by - 4), (bx + 8, by + 3), (bx + 6, by + 5), (bx - 9, by - 1)], c["stripe"], shade=False)
    p.poly([(bx - 4, by - 3), (bx + 7, by + 2), (bx + 6, by + 3), (bx - 6, by - 1)], "#f0e8d8", shade=False)
    p.poly([(bx + 9, by - 4), (bx + 22, by - 1), (bx + 22, by + 1), (bx + 10, by + 2)], c["light"])
    p.ell(bx + 11, by - 4.5, 1.3, 1.2, c["light"])
    p.px(bx + 13, by - 2, "#111")


SPECIES_PET = {
    "gato": (d_gato, {
        "atigrado": dict(main="#b07a44", dark="#8a5a30", light="#e8d2a8", mark="#6a4020", ear="#d88a8a", eye="#c8b040"),
        "negro": dict(main="#3a3640", dark="#2a2630", light="#5a5660", ear="#a86a7a", eye="#d8c040"),
        "blanco": dict(main="#ece6dc", dark="#c8c0b4", light="#ffffff", ear="#e8a0a8", eye="#60a0d8"),
    }),
    "cuy": (d_cuy, {
        "canela": dict(main="#c08a50", dark="#7a5030", light="#ead2b0", ear="#d89a8a", eye="#201010"),
        "pinto": dict(main="#efe6da", dark="#6a4a3a", light="#ffffff", mark="#a06838", ear="#e0a0a0", eye="#201010"),
        "blanco": dict(main="#f2ece4", dark="#b8b0a8", light="#ffffff", ear="#f0aab0", eye="#c03040"),
    }),
    "conejo": (d_conejo, {
        "pardo": dict(main="#9a7650", dark="#7a5a3a", light="#e8dcc8", ear="#d8a0a0", eye="#201010"),
        "gris": dict(main="#8e8c8a", dark="#6e6c6a", light="#e8e4e0", ear="#d8a8a8", eye="#201010"),
        "blanco": dict(main="#f0ece6", dark="#c8c2ba", light="#ffffff", ear="#f0a8b0", eye="#b02838"),
    }),
    "morrocoy": (d_morrocoy, {
        "verde": dict(main="#5a6a38", dark="#3a4424", mark="#c8a848", skin="#7a7258", eye="#111"),
        "rojo": dict(main="#3a3028", dark="#2a2018", mark="#e0b040", skin="#4a4038", legspot="#e04a2a", eye="#111"),
        "dorado": dict(main="#a8782a", dark="#6a4a18", mark="#f8d870", skin="#8a7a58", eye="#111"),
    }),
    "ardilla": (d_ardilla, {
        "roja": dict(main="#b0582a", dark="#7a3a1a", light="#f0c890", eye="#111"),
        "gris": dict(main="#88868a", dark="#5e5c60", light="#e8e4e0", eye="#111"),
        "negra": dict(main="#34302e", dark="#201c1c", light="#7a6a5a", eye="#e8d8a0"),
    }),
    "loro": (d_loro, {
        "verde": dict(main="#3aa040", wing="#2a7a30", tail="#2a6aa8", belly="#7ad050", head="#3aa040", face="#e8d040", beak="#e8e0c0", eye="#111"),
        "azul": dict(main="#3a78c8", wing="#2a58a0", tail="#2a4888", belly="#80b0e8", head="#3a78c8", face="#f0f0f0", beak="#2a2a2a", eye="#111"),
        "amarillo": dict(main="#e8c830", wing="#3aa040", tail="#3a8a40", belly="#f8e070", head="#e8c830", face="#f8e070", beak="#e8e0c0", eye="#111"),
    }),
    "armadillo": (d_armadillo, {
        "pardo": dict(main="#8a6a4a", skin="#b89070"),
        "gris": dict(main="#7a7470", skin="#a8a098"),
        "rosado": dict(main="#d89a90", skin="#f0c0b0"),
    }),
    "chucha": (d_chucha, {
        "gris": dict(main="#8a8684", dark="#4a4644", face="#e8e2d8", tail="#d8b8b0"),
        "parda": dict(main="#6a5040", dark="#3a2a20", face="#e8d8c0", tail="#d8b0a0"),
        "blanca": dict(main="#e8e2d8", dark="#a8a29a", face="#ffffff", tail="#e8c0b8"),
    }),
    "tucan": (d_tucan, {
        "negro": dict(main="#1e1c20", wing="#141216", tail="#141216", belly="#f0d830", head="#1e1c20", face="#f8f0d8", beak="#f08a20", beak2="#d83020", eye="#3a8ad8"),
        "verde": dict(main="#2a5a3a", wing="#1a4a2a", tail="#c83030", belly="#e8d040", head="#2a5a3a", face="#80c8e8", beak="#a8d040", beak2="#3a2a20", eye="#111"),
        "azul": dict(main="#22304a", wing="#1a2438", tail="#1a2438", belly="#f0f0f0", head="#22304a", face="#f0f0f0", beak="#40a8e0", beak2="#f0d020", eye="#111"),
    }),
    "titi": (d_titi, {
        "gris": dict(main="#8a8478", dark="#5a5448", tail="#3a3430", face="#f0e8dc"),
        "dorado": dict(main="#d89a3a", dark="#a8702a", tail="#8a5a20", face="#3a2a20"),
        "blanco": dict(main="#4a4038", dark="#c87a3a", tail="#4a4038", face="#2a2220", crest="#f4f0e8"),
    }),
    "perezoso": (d_perezoso, {
        "pardo": dict(main="#8a7458", dark="#6a5440", face="#e8dcc0", mask="#3a2a1a"),
        "gris": dict(main="#8a8680", dark="#6a6660", face="#e8e4dc", mask="#2a2622"),
        "claro": dict(main="#c8b898", dark="#a89878", face="#f4ece0", mask="#5a4230"),
    }),
    "zorro": (d_zorro, {
        "gris": dict(main="#7a7874", dark="#3a3634", light="#e8e2d8", tip="#2a2624"),
        "rojo": dict(main="#c0602a", dark="#3a2018", light="#f0e0c8", tip="#f8f0e8"),
        "negro": dict(main="#2e2a2c", dark="#1a1618", light="#8a8488", tip="#e8e4e0"),
    }),
    "guacamaya": (d_guacamaya, {
        "roja": dict(main="#d02a2a", wing="#2a6ac8", tail="#d02a2a", belly="#d02a2a", head="#d02a2a", eye="#111"),
        "azul": dict(main="#2a78c8", wing="#2a58a8", tail="#2a5aa8", belly="#f0c030", head="#3aa050", eye="#111"),
        "verde": dict(main="#3a9a40", wing="#2a6aa8", tail="#c83a2a", belly="#3a9a40", head="#d03a2a", eye="#111"),
    }),
    "rana": (d_rana, {
        "oro": dict(main="#f0c030", mark="#c89020"),
        "menta": dict(main="#70e0b0", mark="#1a3a2a"),
        "naranja": dict(main="#f07a20", mark="#2a2a3a"),
    }),
    "nutria": (d_nutria, {
        "parda": dict(main="#6a4a30", dark="#4a3220", light="#c8a888"),
        "oscura": dict(main="#3a2c24", dark="#241a14", light="#a89078"),
        "clara": dict(main="#a88a68", dark="#7a6048", light="#f0e0c8"),
    }),
    "lechuza": (d_lechuza, {
        "blanca": dict(main="#d8b880", wing="#b89860", belly="#f8f4ec", face="#fcf8f0", mark="#a88a60"),
        "parda": dict(main="#8a6a48", wing="#6a4a30", belly="#d8c8a8", face="#e8dcc8", mark="#5a4028"),
        "gris": dict(main="#8a8a8e", wing="#6a6a70", belly="#dcdce0", face="#ececf0", mark="#4a4a50"),
    }),
    "hormiguero": (d_hormiguero, {
        "gris": dict(main="#7a7470", dark="#4a4440", light="#c8c0b8", tail="#5a5450", stripe="#1e1a1a"),
        "pardo": dict(main="#7a5a3a", dark="#4a3420", light="#c8a880", tail="#5a4028", stripe="#1e1612"),
        "claro": dict(main="#b8a888", dark="#8a7a5a", light="#e8dcc0", tail="#9a8a6a", stripe="#2a2018"),
    }),
    "ocelote": (d_ocelote, {
        "dorado": dict(main="#d0a050", dark="#a07838", light="#f4e4c0", mark="#3a2410", ear="#3a2410", eye="#80b040"),
        "gris": dict(main="#b0aca0", dark="#807c70", light="#f0ece4", mark="#2a2622", ear="#2a2622", eye="#80b040"),
        "negro": dict(main="#3a3434", dark="#2a2424", light="#5a5050", mark="#1a1414", ear="#1a1414", eye="#e8c040"),
    }),
    "colibri": (d_colibri, {
        "oro": dict(main="#e8b830", belly="#f8e080", head="#f0c840", wing="#c89020", tail="#b07818"),
        "esmeralda": dict(main="#2aa860", belly="#c8f0d0", head="#40c878", wing="#1a7a48", tail="#1a6a40"),
        "fuego": dict(main="#e05020", belly="#f8c040", head="#f08030", wing="#b03010", tail="#a02810"),
    }),
}


# ---------------------------------------------------------------- mounts (64x61, the horse's canvas)
MW, MH = 64, 61
MG = MH - 1


def quad(p, c, body=(25, 30, 20, 10), leg=3.8, legs=None, front=(37, 40), back=(11, 15), hoof=None, taper=0.55, paw=False):
    """A big four-legged animal with its back at y ~ 20: body ellipse (cx, cy, rx, ry), legs down to the ground.
    Hooved legs thin toward the hoof (taper); paws stay thick and end in a wider foot."""
    cx, cy, rx, ry = body
    far = legs or c["dark"]

    def leg_at(lx, col, dx):
        top = cy + ry * 0.2
        if paw:
            p.limb(lx, top, lx + dx, MG - 1, leg, col, taper=0.85)
            p.ell(lx + dx + 1, MG - 1, leg * 0.55, 1.4, hoof or dk(col, 0.25))
        else:
            # thigh, then a thin shin from the knee down
            knee = top + (MG - top) * 0.5
            p.limb(lx, top, lx + dx * 0.5, knee, leg, col, taper=0.75, shade=False)
            p.limb(lx + dx * 0.5, knee - 1, lx + dx, MG, leg * 0.75, col, taper=taper / 0.75 if taper < 0.75 else 1, foot=hoof or dk(col, 0.45), shade=False)

    for lx in (back[0] + 3, front[0] + 3):
        leg_at(lx, far, 0.5)
    p.ell(cx, cy, rx, ry, c["main"])
    for lx in (back[0], front[0]):
        leg_at(lx, c["main"], -0.5)


def m_mula(p, c):
    p.curve([(6, 27), (3, 34), (3, 44)], 3.5, c["dark"], taper=0.8)
    quad(p, c, body=(24, 29, 19, 9.5), leg=4.2, front=(36, 39), back=(12, 15))
    p.poly([(35, 25), (44, 10), (51, 12), (44, 32)], c["main"])
    p.line([(37, 23), (45, 10)], c["dark"], 2)
    p.poly([(44, 8), (58, 14), (57, 19), (43, 17)], c["main"])
    p.ell(56, 17, 3, 3, c["light"])
    p.poly([(44, 9), (42, 0), (45, 1), (47, 9)], c["main"])
    p.poly([(47, 9), (47, 0), (49.5, 1.5), (49, 10)], c["main"])
    p.px(50, 12, "#111")
    p.ell(24, 34, 12, 3, c["light"], shade=False) if c.get("bellylight") else None


def m_llama(p, c):
    p.ell(7, 24, 3, 3.5, c["main"])
    quad(p, c, body=(23, 29, 17, 10), leg=3.8, front=(34, 37), back=(12, 15))
    for i in range(6):
        p.ell(12 + i * 4.5, 21, 3, 2.5, lt(c["main"], 0.12), shade=False)
    p.poly([(33, 26), (39, 4), (46, 5), (42, 30)], c["main"])
    p.ell(44, 6, 5, 4, c["main"])
    p.poly([(45, 4), (54, 7), (53, 11), (45, 10)], c["main"])
    p.poly([(40, 3), (40, -4), (42.5, -3.5), (43, 3)], c["main"])
    p.poly([(43.5, 3), (45, -4), (47, -3), (46, 3.5)], c["main"])
    p.px(47, 6, "#111")
    if c.get("blanket"):
        p.poly([(15, 20), (31, 20), (32, 30), (14, 30)], c["blanket"])
        for x in range(16, 31, 3):
            p.px(x, 29, c["blanket2"])
            p.px(x + 1, 25, c["blanket2"])


def m_venado(p, c, white=False):
    p.poly([(8, 25), (4, 27), (6, 31)], c["light"])
    quad(p, c, body=(25, 28, 19, 9), leg=3.4, front=(37, 40), back=(11, 14), taper=0.45)
    p.ell(25, 34, 13, 2.5, c["light"], shade=False)
    p.poly([(36, 24), (44, 10), (50, 12), (43, 31)], c["main"])
    p.ell(48, 11, 4.5, 4, c["main"])
    p.poly([(49, 8), (59, 13), (58, 17), (49, 15)], c["main"])
    p.px(59, 14, "#111")
    p.px(51, 10, "#111")
    p.poly([(44, 8), (40, 5), (43, 9)], c["main"])
    ant = c["antler"]
    p.line([(48, 7), (46, -2), (42, -6)], ant, 2)
    p.line([(46, 1), (50, -4)], ant, 1)
    p.line([(44, -3), (44, -7)], ant, 1)
    p.line([(50, 7), (52, 0), (56, -4)], ant, 2)
    p.line([(52, 2), (56, 1)], ant, 1)
    if c.get("spots"):
        for (x, y) in ((14, 24), (19, 23), (24, 24), (29, 23), (17, 27), (22, 27), (27, 27)):
            p.px(x, y, c["spots"])
    if c.get("glow"):
        p.ell(54, -4, 1.5, 1.5, c["glow"], shade=False)
        p.ell(42, -7, 1.2, 1.2, c["glow"], shade=False)


def m_chiguiro(p, c):
    for lx in (16, 38):
        p.limb(lx, 40, lx + 0.5, MG, 7, c["dark"], taper=0.9)
    p.ell(27, 35, 23, 16, c["main"])
    for lx in (11, 34):
        p.limb(lx, 42, lx, MG, 7.5, c["main"], foot=dk(c["main"], 0.5), taper=0.9)
    p.poly([(40, 22), (58, 26), (59, 38), (42, 40)], c["main"])
    p.rect(52, 26, 60, 37, c["main"])
    p.ell(44, 21, 2.5, 2, c["dark"])
    p.px(52, 27, "#111")
    p.rect(58, 31, 60, 32, dk(c["main"], 0.5), False)
    for i in range(5):
        p.px(14 + i * 6, 25 + (i % 2), dk(c["main"], 0.15))


def m_danta(p, c):
    p.ell(5, 27, 2, 2, c["main"])
    quad(p, c, body=(25, 33, 22, 14), leg=6.5, front=(37, 41), back=(11, 15), paw=True)
    if c.get("saddle"):
        p.poly([(15, 20), (31, 19), (35, 46), (13, 46)], c["saddle"])
    p.poly([(38, 22), (50, 22), (52, 38), (41, 42)], c["main"])
    p.ell(48, 27, 7, 8, c["main"])
    p.curve([(52, 25), (57, 28), (59, 34), (58, 37)], 3.6, c["main"], taper=0.8)
    p.ell(44, 19.5, 2, 2.2, c["main"])
    p.px(44, 19, "#e8e0d0")
    p.px(50, 24, "#111")


def m_toro(p, c):
    p.curve([(6, 25), (3, 32), (3, 42)], 1.6, c["main"], taper=1)
    p.ell(3, 43, 1.6, 2.2, c["dark"])
    quad(p, c, body=(24, 33, 21, 13), leg=5.5, front=(36, 40), back=(11, 15), taper=0.6)
    p.ell(33, 23, 9, 6, c["main"])
    if c.get("patch"):
        p.ell(19, 28, 6, 5, c["patch"], shade=False)
        p.ell(30, 33, 4, 3.5, c["patch"], shade=False)
        p.ell(10, 31, 3, 4, c["patch"], shade=False)
    p.poly([(38, 20), (50, 16), (55, 30), (44, 34)], c["main"])
    p.ell(51, 26, 5, 7, c["main"])
    p.ell(53, 32, 4, 3, c["muzzle"])
    p.poly([(46, 18), (52, 17), (58, 9), (55, 16), (51, 20)], c["horn"])
    p.poly([(45, 19), (42, 13), (40, 7), (44, 12), (48, 18)], dk(c["horn"], 0.15))
    p.px(52, 23, "#111")
    p.ell(46, 21, 2, 1.2, c["main"])


def m_oso(p, c):
    p.ell(6, 28, 2.5, 2, c["main"])
    quad(p, c, body=(25, 34, 22, 15), leg=7.5, front=(37, 41), back=(12, 16), paw=True)
    p.ell(39, 27, 8, 9, c["main"])
    hx, hy = 50, 24
    p.ell(hx, hy, 7.5, 6.5, c["main"])
    p.ell(hx - 4, hy - 6, 2.5, 2.5, c["main"])
    p.ell(hx + 5, hy + 2, 4, 3, c["muzzle"])
    p.px(hx + 8, hy + 1, "#111")
    for (gx, gy) in ((hx - 1, hy - 2), (hx + 3, hy - 2)):
        p.ell(gx, gy, 2, 1.6, c["glasses"], shade=False)
        p.px(gx, gy, "#111")
    p.poly([(hx - 2, hy + 6), (hx + 5, hy + 6), (hx + 2, hy + 12), (hx - 5, hy + 11)], c["glasses"], shade=False)


def reptile(p, c, gold=False):
    p.curve([(9, 33), (3, 38), (1, 46), (3, 52)], 8, c["main"], taper=0.25)
    for lx in (17, 40):
        p.limb(lx, 36, lx + 3, MG - 1, 6, c["dark"], taper=0.8)
        p.ell(lx + 4, MG - 1, 3.5, 1.4, c["dark"])
    p.ell(26, 32, 21, 12, c["main"])
    for lx in (12, 35):
        p.limb(lx, 38, lx - 2, MG - 1, 7, c["main"], taper=0.8)
        p.ell(lx - 1, MG - 1, 4, 1.5, dk(c["main"], 0.25))
    p.ell(26, 39, 16, 3.5, c["belly"], shade=False)
    for i in range(7):
        x = 10 + i * 5
        p.poly([(x - 1.5, 21.5), (x, 18.5), (x + 1.5, 21.5)], c["ridge"])
    p.poly([(40, 22), (48, 21), (63, 27), (63, 31), (48, 34), (41, 35)], c["main"])
    p.line([(50, 31), (63, 30)], dk(c["main"], 0.55))
    for x in range(52, 63, 3):
        p.px(x, 31, "#f0ece0")
    p.ell(47, 21, 2.2, 2, c["main"])
    p.px(47, 20.5, c["eye"])
    if gold:
        for (x, y) in ((16, 26), (24, 25), (32, 26), (20, 30), (28, 30), (36, 29)):
            p.px(x, y, c["glint"])


def m_caiman(p, c):
    reptile(p, c)


def m_caimanoro(p, c):
    reptile(p, c, gold=True)


def cat_mount(p, c, rosettes=None, moon=False):
    p.curve([(7, 26), (2, 32), (1, 42), (4, 47)], 4, c["main"], taper=0.7)
    quad(p, c, body=(25, 31, 20, 11), leg=5, front=(37, 40), back=(11, 15), paw=True)
    p.ell(25, 38, 14, 3, c["light"], shade=False)
    hx, hy = 48, 21
    p.poly([(37, 23), (44, 16), (50, 18), (46, 30)], c["main"])
    p.ell(hx, hy, 8, 7, c["main"])
    p.ell(hx + 6, hy + 3, 3.5, 2.6, c["light"])
    p.ell(hx - 3, hy - 5.5, 2.2, 2.4, c["main"])
    p.px(hx - 3, hy - 5.5, c["dark"])
    p.px(hx + 2, hy - 1, c["eye"]); p.px(hx + 3, hy - 1, c["eye"])
    p.px(hx + 8, hy + 1, "#2a1a1a")
    if rosettes:
        for (x, y) in ((12, 26), (17, 23), (22, 26), (27, 23), (32, 26), (14, 31), (20, 30), (26, 31), (31, 30), (36, 27), (9, 29)):
            p.ell(x, y, 1.6, 1.3, rosettes, shade=False)
            p.px(x, y, mix(c["main"], rosettes, 0.25))
    if moon:
        p.ell(hx - 1, hy - 9, 2.5, 2.5, c["moon"], shade=False)
        p.ell(hx, hy - 9.5, 2, 2, (0, 0, 0, 0), shade=False)
        for (x, y) in ((14, 24), (22, 23), (30, 25)):
            p.px(x, y, c["moon"])


def m_puma(p, c):
    cat_mount(p, c)


def m_jaguar(p, c):
    cat_mount(p, c, rosettes=c["mark"])


def m_jaguarluna(p, c):
    cat_mount(p, c, rosettes=c["mark"], moon=True)


def m_charapa(p, c):
    p.curve([(46, 36), (52, 30), (56, 26)], 6, c["skin"])
    p.ell(57, 25, 5, 4, c["skin"])
    p.px(59, 24, "#111")
    for lx in (16, 40):
        p.limb(lx, 40, lx, MG, 7, dk(c["skin"], 0.2))
    p.ell(27, 32, 25, 14, c["main"])
    p.rect(2, 32, 52, 40, c["main"])
    p.poly([(2, 40), (52, 40), (49, 43), (5, 43)], c["rim"])
    for (x, y) in ((14, 24), (27, 21), (40, 24), (9, 33), (21, 31), (33, 31), (45, 33)):
        p.poly([(x - 4, y), (x - 2, y - 3), (x + 2, y - 3), (x + 4, y), (x + 2, y + 3), (x - 2, y + 3)], c["plate"], shade=False)
    for lx in (10, 36):
        p.limb(lx, 41, lx, MG, 7.5, c["skin"], foot=dk(c["skin"], 0.5))
    if c.get("moss"):
        for (x, y) in ((18, 19), (24, 18), (33, 19), (38, 21), (12, 22)):
            p.ell(x, y, 2.5, 1.2, c["moss"], shade=False)


def big_bird(p, c, fire=False, light=False):
    for lx in (24, 32):
        p.limb(lx, 40, lx, MG, 3, c["leg"], shade=False)
        p.line([(lx - 2, MG), (lx + 3, MG)], c["leg"])
    p.poly([(10, 30), (0, 40), (3, 42), (13, 38)], c["tail"])
    p.ell(26, 31, 18, 11, c["main"])
    p.poly([(9, 23), (30, 20), (34, 30), (22, 40), (4, 36)], c["wing"])
    for i in range(4):
        p.line([(8 + i * 5, 34 - i), (12 + i * 6, 25)], dk(c["wing"], 0.25))
    p.poly([(4, 36), (-1, 40), (8, 40)], c["wing"])
    p.ell(41, 24, 6, 4.5, c["ruff"])
    p.curve([(42, 24), (47, 16), (50, 10)], 4, c["neck"])
    p.ell(51, 9, 4.5, 3.8, c["head"])
    p.poly([(54, 7), (60, 9), (59, 12), (54, 12)], c["beak"])
    p.px(52, 8, c["eye"])
    if fire or light:
        for (x, y, r) in ((6, 22, 2), (14, 19, 2.5), (22, 18, 2), (2, 30, 1.6), (49, 4, 1.6), (53, 3, 1.4)):
            p.ell(x, y, r, r * 1.4, c["flame"], shade=False)
            p.px(x, y, c["flame2"])


def m_condor(p, c):
    big_bird(p, c)


def m_condorfuego(p, c):
    big_bird(p, c, fire=True)


def m_ave(p, c):
    big_bird(p, c, light=True)
    for (x, y) in ((8, 15), (19, 12), (30, 14), (58, 2)):
        p.px(x, y, c["flame2"])


def m_venadoblanco(p, c):
    m_venado(p, c)


def m_torodorado(p, c):
    m_toro(p, c)
    for (x, y) in ((14, 27), (22, 25), (30, 27), (18, 33), (26, 33), (51, 24)):
        p.px(x, y, c["glint"])
    p.line([(21, 22), (29, 22)], c["glint"], 1)
    for x in range(14, 35, 4):
        p.poly([(x, 24), (x + 2, 27), (x + 4, 24)], c["glint"], shade=False)


def m_serpiente(p, c):
    # coils on the ground, the rider on the top coil, the head raised in front
    p.ell(28, 52, 26, 8, c["dark"])
    p.ell(26, 46, 21, 8, c["main"])
    p.ell(27, 38, 16, 8, c["dark"])
    p.ell(25, 30, 13, 9, c["main"])
    p.curve([(36, 30), (44, 24), (48, 14), (50, 8)], 8, c["main"], taper=0.7)
    p.ell(53, 7, 6, 4.2, c["main"])
    p.poly([(56, 6), (62, 8), (58, 10)], c["main"])
    p.px(55, 5, c["eye"])
    p.line([(61, 9), (63, 11)], "#d02a2a")
    for (x, y) in ((14, 46), (22, 49), (30, 48), (38, 46), (18, 37), (26, 40), (34, 37), (18, 28), (28, 26), (44, 20), (47, 13)):
        p.ell(x, y, 1.6, 1.2, c["mark"], shade=False)
    p.ell(26, 33, 10, 2, c["belly"], shade=False)
    for (x, y) in ((50, 4), (49, 2), (52, 1)):
        p.px(x, y, c["crest"])


SPECIES_MOUNT = {
    "mula": (m_mula, {
        "parda": dict(main="#7a5a40", dark="#5a4030", light="#c8b098"),
        "negra": dict(main="#3a3434", dark="#2a2424", light="#8a7a70"),
        "torda": dict(main="#a8a4a0", dark="#787470", light="#e8e4e0"),
    }),
    "llama": (m_llama, {
        "blanca": dict(main="#ece4d6", dark="#c8bea8", blanket="#c82a3a", blanket2="#f0c030"),
        "parda": dict(main="#9a7450", dark="#7a5638", blanket="#2a6ac8", blanket2="#f0f0e0"),
        "negra": dict(main="#3e3634", dark="#2a2422", blanket="#e8a020", blanket2="#2a8a5a"),
    }),
    "venado": (m_venado, {
        "pardo": dict(main="#9a7048", dark="#6a4a30", light="#ecdcc0", antler="#e8dcc0", spots=None),
        "rojizo": dict(main="#b05a30", dark="#7a3a20", light="#f0dcc0", antler="#f0e4c8", spots="#f0d8b8"),
        "gris": dict(main="#8a8480", dark="#5a5450", light="#e8e4e0", antler="#d8ccb0", spots=None),
    }),
    "chiguiro": (m_chiguiro, {
        "pardo": dict(main="#8a6440", dark="#5a4028"),
        "rojizo": dict(main="#a8603a", dark="#784028"),
        "oscuro": dict(main="#5a4434", dark="#3a2c22"),
    }),
    "danta": (m_danta, {
        "oscura": dict(main="#3e3a40", dark="#2a2630"),
        "parda": dict(main="#6a5040", dark="#4a3628"),
        "pinta": dict(main="#2e2a30", dark="#1e1a20", saddle="#e8e2d8"),
    }),
    "toro": (m_toro, {
        "negro": dict(main="#2e2a2c", dark="#1e1a1c", muzzle="#4a4040", horn="#e8dcc0"),
        "blanco": dict(main="#e8e2d8", dark="#b8b0a4", muzzle="#e0b0a8", horn="#c8b890"),
        "pinto": dict(main="#efe8dc", dark="#b8b0a4", muzzle="#e0b0a8", horn="#d8c8a0", patch="#5a3a28"),
    }),
    "oso": (m_oso, {
        "negro": dict(main="#2a2628", dark="#1a1618", muzzle="#c8b090", glasses="#e8d8b0"),
        "pardo": dict(main="#5a4030", dark="#3a2a20", muzzle="#d8c0a0", glasses="#f0e0c0"),
        "canelo": dict(main="#9a6a3a", dark="#6a4828", muzzle="#e8d0a8", glasses="#f8ecd0"),
    }),
    "caiman": (m_caiman, {
        "verde": dict(main="#4a6a3a", dark="#34482a", belly="#c8c090", ridge="#34482a", eye="#e8c030"),
        "pardo": dict(main="#6a5a3a", dark="#4a3e28", belly="#d8c8a0", ridge="#4a3e28", eye="#e8c030"),
        "negro": dict(main="#2e322e", dark="#1e221e", belly="#8a8a78", ridge="#1e221e", eye="#e86030"),
    }),
    "puma": (m_puma, {
        "leonado": dict(main="#c09060", dark="#8a6440", light="#f0e0c8", eye="#c8a040"),
        "gris": dict(main="#a09a90", dark="#6a6660", light="#ecE8e0".lower(), eye="#c8a040"),
        "rojizo": dict(main="#b0683a", dark="#7a4628", light="#f0d8c0", eye="#d8b040"),
    }),
    "jaguar": (m_jaguar, {
        "dorado": dict(main="#d8a040", dark="#a07028", light="#f8ecd0", mark="#2a1a10", eye="#a0c040"),
        "negro": dict(main="#2e2a2a", dark="#1e1a1a", light="#4a4444", mark="#161212", eye="#e8c040"),
        "claro": dict(main="#e8d0a0", dark="#b8a070", light="#fcf8ec", mark="#5a4430", eye="#80b0d0"),
    }),
    "charapa": (m_charapa, {
        "verde": dict(main="#4a5a34", plate="#6a7a44", rim="#c8b878", skin="#7a7a5a"),
        "parda": dict(main="#5a4430", plate="#7a6040", rim="#d8c090", skin="#8a7a60"),
        "musgosa": dict(main="#3a4a2e", plate="#4e6038", rim="#a8a070", skin="#6a6a50", moss="#6aa040"),
    }),
    "condor": (m_condor, {
        "negro": dict(main="#1e1c20", wing="#2a282c", tail="#141216", ruff="#f0ece4", neck="#c86a5a", head="#a04a40", beak="#e8dcc0", leg="#6a6060", eye="#e8c030"),
        "gris": dict(main="#5a5a60", wing="#7a7a80", tail="#3a3a40", ruff="#f4f0ea", neck="#d08070", head="#b05a50", beak="#e8dcc0", leg="#6a6060", eye="#e8c030"),
        "pardo": dict(main="#4a3a2c", wing="#6a5440", tail="#2e241a", ruff="#efe6d6", neck="#c87060", head="#a05040", beak="#e8dcc0", leg="#6a6060", eye="#e8c030"),
    }),
    "venadoblanco": (m_venadoblanco, {
        "nieve": dict(main="#f4f2ee", dark="#c8c6c2", light="#ffffff", antler="#e8f0ff", glow="#bfe8ff"),
        "luna": dict(main="#d8dcec", dark="#a8acc0", light="#f8f8ff", antler="#fff4c0", glow="#fff0a0"),
        "niebla": dict(main="#c8d0d0", dark="#98a0a0", light="#eef4f4", antler="#d0fff0", glow="#a0ffe0"),
    }),
    "jaguarluna": (m_jaguarluna, {
        "plata": dict(main="#c8ccd8", dark="#8a8ea0", light="#f4f6fc", mark="#4a5070", eye="#a0e0ff", moon="#f8f4d0"),
        "azul": dict(main="#4a5a9a", dark="#323e70", light="#a8b4e0", mark="#1e2448", eye="#f8e070", moon="#f8f4d0"),
        "sombra": dict(main="#2a2a3a", dark="#1a1a28", light="#4a4a60", mark="#4a5a90", eye="#a0e0ff", moon="#c8d8ff"),
    }),
    "caimanoro": (m_caimanoro, {
        "oro": dict(main="#d0a030", dark="#9a7020", belly="#f4dc80", ridge="#9a7020", eye="#2a8a40", glint="#fff4c0"),
        "tumbaga": dict(main="#c07848", dark="#8a5030", belly="#f0c890", ridge="#8a5030", eye="#2a8a40", glint="#ffe0b0"),
        "esmeralda": dict(main="#2a9a5a", dark="#1a6a3a", belly="#d0c060", ridge="#c8a030", eye="#f0d040", glint="#e0ffe8"),
    }),
    "condorfuego": (m_condorfuego, {
        "fuego": dict(main="#a02a18", wing="#d04a20", tail="#7a1a10", ruff="#f8d040", neck="#f08030", head="#e05a20", beak="#f8e0a0", leg="#7a4a30", eye="#fff0a0", flame="#f8a020", flame2="#fff4b0"),
        "brasa": dict(main="#3a1e1a", wing="#5a2a20", tail="#2a1410", ruff="#f06020", neck="#c04020", head="#a03018", beak="#e8d0a0", leg="#5a3a30", eye="#ffb040", flame="#e04018", flame2="#f8c040"),
        "azul": dict(main="#1e3a7a", wing="#2a5ab0", tail="#142a5a", ruff="#a0e0ff", neck="#4aa0e8", head="#3a80d0", beak="#e8f0ff", leg="#3a4a6a", eye="#ffffff", flame="#60c0ff", flame2="#e8f8ff"),
    }),
    "torodorado": (m_torodorado, {
        "oro": dict(main="#d0a030", dark="#9a7020", muzzle="#e8c060", horn="#fff0b0", glint="#fff4c8"),
        "tumbaga": dict(main="#c07848", dark="#8a5030", muzzle="#e0a070", horn="#f8e0a0", glint="#ffe0b0"),
        "noche": dict(main="#26222a", dark="#16121a", muzzle="#3a3440", horn="#f0c840", glint="#f0c840"),
    }),
    "serpiente": (m_serpiente, {
        "laguna": dict(main="#2a7a7a", dark="#1e5a5e", belly="#c8e8c0", mark="#e8d060", eye="#f8f0a0", crest="#80e8d0"),
        "oro": dict(main="#d0a030", dark="#9a7020", belly="#f8e8a0", mark="#5a3a10", eye="#2a8a40", crest="#fff0b0"),
        "niebla": dict(main="#9aa8b0", dark="#6e7a84", belly="#e8f0f0", mark="#4a5a68", eye="#a0e0ff", crest="#e0f8ff"),
    }),
    "ave": (m_ave, {
        "luz": dict(main="#1e1c24", wing="#2a2834", tail="#141218", ruff="#fff4c0", neck="#f8e080", head="#f8d860", beak="#fff8e0", leg="#5a5060", eye="#ffffff", flame="#fff0a0", flame2="#ffffff"),
        "alba": dict(main="#e88a6a", wing="#f0a890", tail="#c86a5a", ruff="#fff0e0", neck="#f8c8a0", head="#f8b080", beak="#fff4e0", leg="#8a6a60", eye="#5a2a40", flame="#ffd0a0", flame2="#fff8e8"),
        "noche": dict(main="#141428", wing="#22224a", tail="#0e0e1e", ruff="#a8b8ff", neck="#6a78d8", head="#5060c0", beak="#e0e8ff", leg="#3a3a5a", eye="#ffffff", flame="#8aa0ff", flame2="#ffffff"),
    }),
}


def build(kind, coat, fn, pal, mount):
    p = Pic(MW, MH) if mount else Pic(PW, PH)
    fn(p, pal)
    im = p.render()
    if not mount:
        im = im.crop(im.getbbox())
    else:
        # keep the canvas (the rider's seat depends on it) but nothing may spill out of it
        pass
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"{'mount' if mount else 'pet'}-{kind}-{coat}.png")
    im.save(path)
    return im


def main():
    from stable_more import MOUNTS_MORE, PETS_MORE  # levels 21-40
    SPECIES_PET.update(PETS_MORE)
    SPECIES_MOUNT.update(MOUNTS_MORE)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sheet_out = sys.argv[sys.argv.index("--sheet") + 1] if "--sheet" in sys.argv else None
    if sheet_out in args:
        args.remove(sheet_out)
    made = []
    for mount, table in ((False, SPECIES_PET), (True, SPECIES_MOUNT)):
        for kind, (fn, coats) in table.items():
            if args and kind not in args:
                continue
            for coat, pal in coats.items():
                made.append((kind, coat, build(kind, coat, fn, pal, mount), mount))
    print(f"{len(made)} animals")
    if sheet_out:
        k = 4
        cols = 6
        cw, chh = 70 * k, 66 * k
        rows = (len(made) + cols - 1) // cols
        sh = Image.new("RGBA", (cols * cw, rows * chh), (58, 52, 44, 255))
        for i, (_, _, im, mount) in enumerate(made):
            big = im.resize((im.width * k, im.height * k), Image.NEAREST)
            x, y = (i % cols) * cw, (i // cols) * chh
            sh.alpha_composite(big, (x + (cw - big.width) // 2, y + chh - big.height - 4))
        sh.save(sheet_out)


if __name__ == "__main__":
    main()
