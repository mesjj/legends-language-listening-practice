"""The eighteen bosses (three per zone), drawn in code: original pixel art, no outside files.

Each boss is a strip of N frames (an idle loop) in two rows: row 0 as you meet it, row 1 its second
phase (from half its life). Dark, towering silhouettes with glowing eyes, each with the shape its legend
gives it: the Silbón's hat and sack, the Mohán's hair in the river, the Madremonte's leaves, the
fireball's skull, the Llorona's hair over her face, the Mandingas's horns and cape.

Writes public/rpg/bosses/<id>.png and public/rpg/bosses/bosses.json ({id: [frame w, frame h, frames]}).
usage: .venv/bin/python scripts/build_bosses.py [id ...]   (no ids: all of them)
"""
import json, math, os, random, sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "public", "rpg", "bosses")
N = 8  # frames per loop
TAU = math.tau
INK = (12, 9, 14, 255)  # the outline


def rgb(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


class Pic:
    """An RGBA canvas with shapes in float coordinates."""

    def __init__(self, w, h):
        self.im = Image.new("RGBA", (w, h))
        self.d = ImageDraw.Draw(self.im)
        self.w, self.h = w, h

    def poly(self, pts, col):
        self.d.polygon([(round(x), round(y)) for x, y in pts], fill=rgb(col) if isinstance(col, str) else col)

    def ell(self, cx, cy, rx, ry, col):
        self.d.ellipse((round(cx - rx), round(cy - ry), round(cx + rx), round(cy + ry)), fill=rgb(col) if isinstance(col, str) else col)

    def line(self, pts, col, w=1):
        self.d.line([(round(x), round(y)) for x, y in pts], fill=rgb(col) if isinstance(col, str) else col, width=w)

    def px(self, x, y, col):
        x, y = round(x), round(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            self.im.putpixel((x, y), rgb(col) if isinstance(col, str) else col)

    def rect(self, x0, y0, x1, y1, col):
        self.d.rectangle((round(x0), round(y0), round(x1), round(y1)), fill=rgb(col) if isinstance(col, str) else col)

    def paste(self, other, dx=0, dy=0):
        self.im.alpha_composite(other.im if isinstance(other, Pic) else other, (round(dx), round(dy)))


def limb(p, pts, w0, w1, col):
    """A tapering limb along a polyline: width w0 at the start, w1 at the end."""
    n = len(pts) - 1
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        a, b = w0 + (w1 - w0) * i / n, w0 + (w1 - w0) * (i + 1) / n
        L = math.hypot(x1 - x0, y1 - y0) or 1
        nx, ny = -(y1 - y0) / L, (x1 - x0) / L
        p.poly([(x0 + nx * a / 2, y0 + ny * a / 2), (x1 + nx * b / 2, y1 + ny * b / 2), (x1 - nx * b / 2, y1 - ny * b / 2), (x0 - nx * a / 2, y0 - ny * a / 2)], col)
        p.ell(x1, y1, b / 2, b / 2, col)


def wave_line(p, x, y0, y1, amp, ph, col, freq=0.18, w=1):
    pts = [(x + amp * math.sin(ph + (y - y0) * freq) * (y - y0) / max(1, y1 - y0), y) for y in range(round(y0), round(y1) + 1)]
    p.line(pts, col, w)


def outline(im, col=INK, keep=None):
    """A 1px dark line around everything opaque (keep: pixels that stay without one, e.g. glows)."""
    src = im.copy()
    a = src.split()[3].load()
    px = im.load()
    W, H = im.size
    for y in range(H):
        for x in range(W):
            if a[x, y] > 100:
                continue
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < W and 0 <= ny < H and a[nx, ny] > 100:
                    px[x, y] = col
                    break
    return im


def glow(im, x, y, col, r=3.0, peak=0.75):
    """A soft halo of col around (x, y), over whatever is there."""
    c = rgb(col)
    px = im.load()
    W, H = im.size
    for yy in range(int(y - r - 1), int(y + r + 2)):
        for xx in range(int(x - r - 1), int(x + r + 2)):
            if not (0 <= xx < W and 0 <= yy < H):
                continue
            d = math.hypot(xx - x, yy - y)
            if d > r:
                continue
            k = peak * (1 - d / r) ** 1.4
            R, G, B, A = px[xx, yy]
            if A == 0:
                px[xx, yy] = (c[0], c[1], c[2], round(255 * k))
            else:
                px[xx, yy] = (round(R + (c[0] - R) * k), round(G + (c[1] - G) * k), round(B + (c[2] - B) * k), max(A, round(255 * k)))


def shear(im, y0, dx, y_top=0):
    """Rows above y0 slide sideways, more the higher they are (a sway from the hips)."""
    out = Image.new("RGBA", im.size)
    for y in range(im.height):
        s = 0 if y >= y0 else round(dx * (y0 - y) / max(1, y0 - y_top))
        out.paste(im.crop((0, y, im.width, y + 1)), (s, y))
    return out


BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def fade_down(im, y0, y1):
    """Dither the picture away between rows y0 (whole) and y1 (gone): a ghost's missing feet."""
    px = im.load()
    for y in range(im.height):
        k = 0 if y <= y0 else 1 if y >= y1 else (y - y0) / (y1 - y0)
        if not k:
            continue
        for x in range(im.width):
            if px[x, y][3] and (BAYER[y % 4][x % 4] + 0.5) / 16 < k:
                px[x, y] = (0, 0, 0, 0)


def shade(base, k):
    """base colour darker (k < 1) or lighter (k > 1)."""
    r, g, b = rgb(base)[:3]
    if k < 1:
        return (round(r * k), round(g * k), round(b * k), 255)
    return (round(r + (255 - r) * (k - 1)), round(g + (255 - g) * (k - 1)), round(b + (255 - b) * (k - 1)), 255)


# ---------------------------------------------------------------- El Silbón
# Impossibly tall and thin, a wide drooping hat over a face you can't see, arms bent out and down to his
# knees with long claws, a sack of bones on his back. Second phase: he grows (his legend says he can
# reach the treetops) and starts to whistle.
def silbon(t, ph):
    W, H = 84, 164
    p = Pic(W, H)
    g = H - 2
    grow = 30 if ph else 0
    hip = g - 52 - grow
    sh = hip - 44  # shoulders
    cx = 40
    sw = math.sin(TAU * t)
    coat, coat2, coat3 = "#1b1d24", "#111217", "#2b2e38"
    # legs: two sticks, boots
    for lx, fx in ((cx - 4, cx - 8), (cx + 4, cx + 7)):
        limb(p, [(lx, hip), ((lx + fx) / 2, (hip + g) / 2), (fx, g - 2)], 4, 3, "#101116")
        p.rect(fx - 3, g - 2, fx + 2, g, "#0a0a0d")
    # the sack on his back: lumpy burlap, bones poking out of it
    sx, sy = cx + 17 + 2 * math.sin(TAU * t + 1), sh + 20
    p.ell(sx, sy, 12, 16, "#5e533f")
    p.ell(sx + 3, sy + 6, 9, 10, "#4a4132")
    p.ell(sx - 3, sy - 6, 6, 6, "#766a52")
    for k in range(6):
        p.px(sx - 6 + k * 2, sy + 3 + (k % 2) * 3, "#3d3428")
    p.line([(sx - 3, sy - 15), (sx - 7, sy - 23)], "#ddd3bd", 3)        # a femur
    p.ell(sx - 8, sy - 24, 2, 2, "#ddd3bd")
    p.ell(sx + 4, sy - 16, 4.5, 4, "#cfc5ad")                            # a skull
    p.px(sx + 3, sy - 16, "#2a241c"); p.px(sx + 5, sy - 16, "#2a241c")
    p.line([(cx + 6, sh + 2), (sx - 4, sy - 12)], "#8a7a5a", 1)           # the rope
    # the coat: long, to below the knees, shoulders sharp, its hem in rags that move
    hem = hip + 10
    pts = [(cx - 12, sh + 1), (cx - 8, sh - 2), (cx + 8, sh - 2), (cx + 12, sh + 1)]
    for i in range(9):
        x = cx + 13 - i * 26 / 8
        pts.append((x, hem + (7 if i % 2 else 0) + round(1.5 * math.sin(TAU * t * 2 + i))))
    p.poly(pts, coat)
    p.poly([(cx + 2, sh), (cx + 12, sh + 1), (cx + 13, hem + 3), (cx + 4, hem + 5)], coat2)
    p.line([(cx - 11, sh + 3), (cx - 13, hem)], coat3, 1)
    p.line([(cx - 1, sh + 6), (cx - 1, hip + 10)], coat2, 1)
    # arms: elbows out, ragged sleeves to the wrist, bone hands with long claws down at the knees
    for side in (-1, 1):
        s0 = (cx + side * 12, sh + 1)
        el = (cx + side * 25, sh + 24)
        wr = (cx + side * 21 + (sw if side < 0 else 0), hip + 20 + grow // 3)
        limb(p, [s0, el], 5, 4, coat)
        limb(p, [el, (el[0] - side * 1.5, el[1] + 12)], 4, 4, coat)
        limb(p, [(el[0] - side * 1.5, el[1] + 12), wr], 2, 2, "#8d887c")
        for k in range(3):  # rags hanging from the sleeve
            p.line([(el[0] + side * (k - 1) * 2, el[1] + 2), (el[0] + side * (k - 1) * 2 - side, el[1] + 7 + k * 2)], coat, 2)
        hx, hy = wr[0], wr[1] + 2
        p.ell(hx, hy, 2.5, 2, "#8d887c")
        for f in (-3, -1, 1, 3):
            tip = (hx + f * 1.3, hy + 10 + (1 if f in (-1, 1) else 0))
            p.line([(hx + f * 0.6, hy), (hx + f * 1.1, hy + 6), tip], "#b0aa9a", 1)
            p.px(tip[0], tip[1] + 1, "#e8e2d0")
    # the head: pushed forward, a face in shadow, a pale jaw
    hx0, hy = cx - 3, sh - 11
    limb(p, [(cx, sh), (hx0 + 1, hy + 6)], 3, 3, "#3a3834")
    p.ell(hx0, hy, 6, 7.5, "#22221f")
    p.poly([(hx0 - 5, hy + 2), (hx0 + 5, hy + 2), (hx0 + 3, hy + 8), (hx0 - 3, hy + 8)], "#8d887c")
    p.poly([(hx0 + 1, hy + 2), (hx0 + 5, hy + 2), (hx0 + 3, hy + 8), (hx0 + 1, hy + 8)], "#6e6a60")
    if ph:
        p.ell(hx0, hy + 5, 1.5, 1.8, "#050506")                         # lips pursed: whistling
        p.px(hx0 - 1, hy + 3, "#b8b2a4"); p.px(hx0 + 1, hy + 3, "#b8b2a4")
    else:
        for k in range(-3, 4, 2):
            p.px(hx0 + k, hy + 5, "#d6d0c0")                             # teeth
        p.line([(hx0 - 3, hy + 6), (hx0 + 3, hy + 6)], "#111111", 1)
    # the hat: a wide brim drooping at the edges, a tall dented crown, a band
    by = hy - 6
    p.poly([(hx0 - 21, by + 4), (hx0 - 14, by - 1), (hx0, by - 3), (hx0 + 14, by - 1), (hx0 + 21, by + 4), (hx0 + 14, by + 2), (hx0, by + 1), (hx0 - 14, by + 2)], "#16171c")
    p.line([(hx0 - 14, by - 1), (hx0, by - 2), (hx0 + 14, by - 1)], "#2a2c33", 1)
    p.poly([(hx0 - 8, by - 1), (hx0 - 7, by - 11), (hx0 - 3, by - 14), (hx0, by - 12), (hx0 + 4, by - 14), (hx0 + 8, by - 11), (hx0 + 9, by - 1)], "#1c1d23")
    p.rect(hx0 - 8, by - 4, hx0 + 9, by - 3, "#4a3626")
    im = shear(p.im, hip, round(2 * sw), sh - 30)
    outline(im)
    e = 1.5 if ph else 1.1
    for ex in (hx0 - 3, hx0 + 2):
        ex += round(2 * sw * (hip - hy) / (hip - sh + 30))
        glow(im, ex, hy - 1, "#7fe6ff", 3.4 * e, 0.65)
        im.putpixel((ex, hy - 1), rgb("#f2fdff"))
    return im


# ---------------------------------------------------------------- El Mohán
# A hulking heap of wet hair in the river, a beard down into the water, gold eyes, gold on his hands.
# Second phase: he rises out of the water, eyes burning, mouth open on gold teeth.
def mohan(t, ph):
    W, H = 140, 136
    p = Pic(W, H)
    water = H - 16
    up = 12 if ph else 0
    R = random.Random(7)
    base = water + 6 - up
    cx = 70
    # the mass: shoulders and a hunched head thrust forward (left)
    body = Pic(W, H)
    body.ell(cx + 6, base - 30, 46, 32, "#1f271c")       # the bulk
    body.ell(cx + 14, base - 56, 28, 22, "#1f271c")      # the hump
    body.poly([(cx - 36, base - 72), (cx - 12, base - 80), (cx - 2, base - 50), (cx - 34, base - 40)], "#1f271c")  # the neck
    body.ell(cx - 24, base - 80, 16, 16, "#1f271c")      # the head, thrust forward and up
    a = body.im.split()[3]
    p.paste(body)
    # hair: strands hanging from the top of the mass, swaying
    tops = {}
    for x in range(W):
        for y in range(H):
            if a.getpixel((x, y)) > 0:
                tops[x] = y
                break
    cols = ["#2f3a29", "#3e4b35", "#4f5f42", "#1c231a", "#33402c", "#6c7d5c"]
    for i in range(190):
        x = R.uniform(min(tops), max(tops))
        y0 = tops[round(x)] + R.uniform(0, 8)
        L = R.uniform(30, 95)
        wave_line(p, x, y0, min(base + 4, y0 + L), 1.5, TAU * t + R.uniform(0, TAU), R.choice(cols), 0.2)
    # the arm reaching out of the hair toward you, a hand on the water, gold rings
    hx, hy = 16, water - 3 + round(math.sin(TAU * t))
    limb(p, [(cx - 14, base - 50), (cx - 40, base - 30), (hx + 8, hy - 4)], 15, 9, "#26301f")
    for i in range(16):
        wave_line(p, cx - 14 - i * 2.6, base - 50 + i * 1.4, base - 36 + i * 1.8, 1, TAU * t + i, R.choice(cols), 0.3)
    # the other hand, down in the water on his far side
    rx = cx + 50
    limb(p, [(cx + 36, base - 44), (cx + 50, base - 24), (rx, water)], 13, 9, "#26301f")
    for k in (-4, 0, 4):
        p.line([(rx + k, water - 2), (rx + k - 2, water + 2)], "#d8cfb4", 1)
    p.ell(hx + 6, hy - 3, 7, 4.5, "#4a3a2c")
    for k, fx in enumerate((hx - 2, hx + 1, hx + 4, hx + 8)):
        p.line([(fx + 2, hy - 3), (fx - 2, hy + 1)], "#4a3a2c", 2)
        p.line([(fx - 2, hy + 1), (fx - 3, hy + 3)], "#d8cfb4", 1)
    p.px(hx + 1, hy - 3, "#f0c43a"); p.px(hx + 4, hy - 4, "#f0c43a"); p.px(hx + 5, hy - 4, "#fff0a0")
    # the face, deep under the hair: a dark hollow, a heavy nose, gold eyes
    fx, fy = cx - 28, base - 78
    p.ell(fx, fy, 11, 7, "#0d110b")
    p.ell(fx - 1, fy + 5, 3.5, 3, "#5a3f2c")
    # the beard: long strands from the face down into the water, narrowing
    for i in range(30):
        u = i / 29
        x0 = fx - 10 + u * 20 + R.uniform(-1, 1)
        x1 = fx + (x0 - fx) * 0.45 + R.uniform(-2, 2)
        y1 = water + 2 - R.uniform(0, 14) * abs(u - 0.5) * 2
        pts = [(x0 + (x1 - x0) * k / 12 + 1.6 * math.sin(TAU * t + i * 0.7 + k * 0.6), fy + 7 + (y1 - fy - 7) * k / 12) for k in range(13)]
        p.line(pts, R.choice(["#4f5a44", "#5c684f", "#3c4635", "#6f7a62"]), 1)
    if ph:  # the mouth open in the beard, gold teeth
        p.ell(fx, fy + 11, 6, 3.5, "#160808")
        for k in range(-4, 5, 2):
            p.px(fx + k, fy + 9, "#f0c43a"); p.px(fx + k + 1, fy + 13, "#c89a28")
    # hair falling over the brow
    for i in range(16):
        x = fx - 12 + i * 1.6
        wave_line(p, x, fy - 14, fy - 4 + R.uniform(0, 4), 1, TAU * t + i, R.choice(cols), 0.4)
    im = p.im
    outline(im)
    # the river: he stands in it; ripples move, rings spread from him
    q = im.load()
    for y in range(water, H):
        d = (y - water) / (H - water)
        for x in range(W):
            r_, g_, b_, a_ = q[x, y]
            wc = (24, 54, 58)
            if a_:
                k = 0.55 + 0.4 * d
                q[x, y] = (round(r_ + (wc[0] - r_) * k), round(g_ + (wc[1] - g_) * k), round(b_ + (wc[2] - b_) * k), 255)
            elif 6 < x < W - 6:
                edge = min(x - 6, W - 6 - x) / 22
                if R.random() < min(1, edge) * (1 - d * 0.6):
                    q[x, y] = (*wc, 200)
    pd = ImageDraw.Draw(im)
    for k in range(4):
        y = water + 2 + k * 3
        off = (t * 12 + k * 7) % 12
        for x0 in range(int(8 + off), W - 10, 12):
            if q[min(W - 1, x0), y][3]:
                pd.line((x0, y, x0 + 4 + k % 2, y), fill=rgb("#5f9c98" if k % 2 else "#8fc8c0"))
    # drips from the beard
    for i in range(4):
        dx = fx - 7 + i * 5
        dy = fy + 10 + ((t * 30 + i * 9) % (water - fy - 8))
        if dy < water:
            im.putpixel((round(dx), round(dy)), rgb("#9fd6ec"))
    for ex in (fx - 4, fx + 4):
        glow(im, ex, fy, "#ff5a1a" if ph else "#ffc83a", 4 if ph else 3.2, 0.7)
        im.putpixel((ex, fy), rgb("#fff4b0"))
        im.putpixel((ex + 1, fy), rgb("#ffd34a"))
    return im


# ---------------------------------------------------------------- La Madremonte
# A tall woman of moss and leaves, a hat of leaves over a dark face with two green eyes, branches for
# arms, antlers of twigs. Second phase: the eyes go red, thorns and red flowers open all over her.
def madremonte(t, ph):
    W, H = 110, 146
    p = Pic(W, H)
    g = H - 2
    cx = 58
    R = random.Random(11)
    greens = ["#0f2410", "#1b3d19", "#2c5e24", "#3f7a2c", "#5e9a36"]
    # antlers of twigs above the hat, the arms' branches
    hat_y = g - 104
    def twig(x, y, ang, L, depth):
        if depth == 0 or L < 3:
            return
        x2, y2 = x + math.cos(ang) * L, y + math.sin(ang) * L
        p.line([(x, y), (x2, y2)], "#3a2a1a" if depth > 1 else "#4f3a24", 2 if depth > 2 else 1)
        twig(x2, y2, ang - 0.5 + R.uniform(-0.2, 0.2), L * 0.68, depth - 1)
        twig(x2, y2, ang + 0.45 + R.uniform(-0.2, 0.2), L * 0.62, depth - 1)
    grow = 1.25 if ph else 1
    twig(cx - 8, hat_y - 2, -2.0, 13 * grow, 4)
    twig(cx + 8, hat_y - 2, -1.15, 13 * grow, 4)
    # the skirt: roots and hanging moss spreading on the ground
    waist = g - 66
    for i in range(70):
        u = i / 69
        x0 = cx - 13 + u * 26
        x1 = cx - 36 + u * 72 + R.uniform(-3, 3)
        sway = 1.6 * math.sin(TAU * t + u * 5)
        p.line([(x0, waist), ((x0 + x1) / 2 + sway, (waist + g) / 2), (x1 + sway * 0.4, g - R.uniform(0, 5))], R.choice(greens[:4] + ["#2a2416"]), 2)
    for k in range(7):  # roots on the ground
        x = cx - 34 + k * 11 + R.uniform(-2, 2)
        p.line([(x, g - 2), (x + R.choice((-6, 6)), g)], "#3a2a1a", 2)
    # the body: leaves overlapping
    body = [(cx - 12, waist + 2), (cx - 9, g - 92), (cx + 9, g - 92), (cx + 13, waist + 2)]
    p.poly(body, "#1b3d19")
    # arms: branches, one held out toward you with twig fingers, the other down
    sway = math.sin(TAU * t)
    la = [(cx - 9, g - 90), (cx - 24, g - 80), (cx - 40, g - 76 + sway), (cx - 50, g - 80 + sway)]
    limb(p, la, 5, 3, "#3a2a1a")
    hx, hy = la[-1]
    for ang in (-2.6, -2.9, 3.0, 2.6):
        p.line([(hx, hy), (hx + math.cos(ang) * 8, hy + math.sin(ang) * 8)], "#4f3a24", 1)
    ra = [(cx + 9, g - 90), (cx + 20, g - 76), (cx + 24, g - 58), (cx + 22 + sway, g - 46)]
    limb(p, ra, 5, 3, "#3a2a1a")
    for ang in (1.2, 1.6, 2.0):
        p.line([ra[-1], (ra[-1][0] + math.cos(ang) * 7, ra[-1][1] + math.sin(ang) * 7)], "#4f3a24", 1)
    # leaves all over the body and the arms; some rustle each frame
    spots = [(R.uniform(cx - 13, cx + 13), R.uniform(g - 94, waist + 6)) for _ in range(90)]
    spots += [(x + R.uniform(-3, 3), y + R.uniform(-3, 3)) for (x, y) in la + ra for _ in range(6)]
    for i, (x, y) in enumerate(spots):
        j = 1 if (i * 7 + int(t * N)) % 9 == 0 else 0
        p.ell(x + j, y, R.choice((1.5, 2, 2.5)), R.choice((1, 1.5)), R.choice(greens[1:]))
    # vines hanging from the arms and the hat
    for (x, y) in la[1:] + [(cx - 22, hat_y + 6), (cx + 20, hat_y + 6)]:
        L = R.uniform(10, 22)
        wave_line(p, x, y, y + L, 2, TAU * t + x, "#2c5e24", 0.3)
        p.px(x + 1, y + L, "#5e9a36")
    # the hat of leaves, and the dark under it where the face should be
    p.ell(cx, hat_y + 12, 13, 12, "#050805")
    p.ell(cx, hat_y + 3, 27, 7, "#1b3d19")
    for k in range(38):
        a = R.uniform(0, TAU)
        rr = R.uniform(0.3, 1)
        p.ell(cx + math.cos(a) * 25 * rr, hat_y + 3 + math.sin(a) * 6 * rr, 2.5, 1.5, R.choice(greens[1:]))
    p.ell(cx, hat_y - 3, 10, 5, "#2c5e24")
    for k in range(10):
        p.ell(cx + R.uniform(-9, 9), hat_y - 3 + R.uniform(-3, 3), 2, 1.5, R.choice(greens[2:]))
    for k in range(8):  # leaves hanging from the brim
        x = cx - 24 + k * 7
        wave_line(p, x, hat_y + 6, hat_y + 10 + (k % 3) * 2, 1, TAU * t + k, R.choice(greens[1:3]), 0.5)
    if ph:  # thorns and red flowers
        for (x, y) in spots[::5]:
            p.px(x, y, "#c8202a"); p.px(x + 1, y, "#ff5a5a")
        for (x, y) in spots[2::9]:
            p.px(x - 2, y - 1, "#d8cfa0")
    im = p.im
    outline(im)
    ey = hat_y + 13
    for ex in (cx - 5, cx + 4):
        glow(im, ex, ey, "#ff3a1a" if ph else "#c8ff3a", 3.6, 0.7)
        im.putpixel((ex, ey), rgb("#fff6c0" if ph else "#f4ffc0"))
    return im


# ---------------------------------------------------------------- La Bola de Fuego
# A skull in a ball of fire, rolling at you with a tail of flames. Second phase: the fire turns blue-white.
def noise_grid(seed, gw, gh):
    R = random.Random(seed)
    return [[R.random() for _ in range(gw)] for _ in range(gh)]


def vnoise(G, x, y):
    gh, gw = len(G), len(G[0])
    x0, y0 = math.floor(x), math.floor(y)
    fx, fy = x - x0, y - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    v = lambda i, j: G[j % gh][i % gw]
    a = v(x0, y0) + (v(x0 + 1, y0) - v(x0, y0)) * fx
    b = v(x0, y0 + 1) + (v(x0 + 1, y0 + 1) - v(x0, y0 + 1)) * fx
    return a + (b - a) * fy


FIRE = ["#4a0a06", "#9a1c0c", "#e0480e", "#ff8a1a", "#ffc83a", "#fff2b0"]
BLUE = ["#0c1250", "#1a3aa8", "#2f7ae8", "#5ab8ff", "#bfe8ff", "#ffffff"]
G1, G2 = noise_grid(3, 16, 16), noise_grid(5, 32, 32)


def bolafuego(t, ph):
    W, H = 140, 124
    im = Image.new("RGBA", (W, H))
    q = im.load()
    pal = [rgb(c) for c in (BLUE if ph else FIRE)]
    cx, cy, Rr = 54, 64, 37
    for y in range(H):
        for x in range(W):
            dx, dy = (x - cx), (y - cy)
            # the ball, stretched into a tail behind it (to the right) and licking upward
            tail = max(0, dx) * 0.45
            d = math.hypot(dx - tail, dy * (1.0 if dy > 0 else 0.8)) / Rr
            n = vnoise(G1, x / 8, y / 8 + t * 16) * 0.65 + vnoise(G2, x / 4, y / 4 + t * 32) * 0.35
            v = 1.15 - d + (n - 0.5) * 0.9 - max(0, -dy) / 80 + max(0, dx) / 260
            if v < 0.12:
                continue
            k = min(len(pal) - 1, int((v - 0.12) / 0.17))
            q[x, y] = pal[k]
    # the skull, in the middle of the fire, facing you, scowling; its jaw chattering
    p = Pic(W, H)
    sx, sy = cx + 1, cy
    S = lambda v: v * 1.32
    jaw = round(1 + math.sin(TAU * t * 2) * 1.5)
    bone, bone2, crack, hole = "#efe0bc", "#b8a078", "#4a3020", "#120402"
    p.ell(sx, sy - S(5), S(14), S(13), bone)
    p.ell(sx + S(5), sy - S(2), S(9), S(11), bone2)
    p.ell(sx - S(2), sy - S(7), S(10), S(9), bone)
    p.poly([(sx - S(10), sy + S(2)), (sx + S(10), sy + S(2)), (sx + S(7), sy + S(10)), (sx - S(7), sy + S(10))], bone)
    p.poly([(sx + S(2), sy + S(2)), (sx + S(10), sy + S(2)), (sx + S(7), sy + S(10)), (sx + S(2), sy + S(10))], bone2)
    p.rect(sx - S(8), sy + S(9) + jaw, sx + S(8), sy + S(14) + jaw, bone2)              # the jaw
    p.rect(sx - S(6), sy + S(8), sx + S(6), sy + S(9) + jaw, "#1a0604")
    for k in range(-8, 9, 3):
        p.rect(sx + k, sy + S(8) - 1, sx + k + 1, sy + S(8), "#fff8e0")
        p.rect(sx + k, sy + S(9) + jaw, sx + k + 1, sy + S(9) + jaw + 1, "#fff8e0")
    for side in (-1, 1):  # eye holes under a scowling brow
        ex = sx + side * S(5)
        p.ell(ex, sy - S(1), S(4.2), S(4), hole)
        p.poly([(ex - side * S(5), sy - S(2.5)), (ex + side * S(5), sy - S(7.5)), (ex + side * S(5), sy - S(5)), (ex - side * S(5), sy - S(0.5))], bone2)
    p.poly([(sx, sy + S(3)), (sx - S(2), sy + S(6)), (sx + S(2), sy + S(6))], hole)       # nose
    p.line([(sx + S(2), sy - S(17)), (sx + S(4), sy - S(12)), (sx + S(2), sy - S(8))], crack, 1)
    p.line([(sx - S(9), sy - S(11)), (sx - S(6), sy - S(7))], crack, 1)
    skull = p.im
    outline(skull, (60, 12, 6, 255))
    im.alpha_composite(skull)
    # flames licking over the skull's top
    for y in range(round(sy - S(22)), round(sy - S(8))):
        for x in range(round(sx - S(14)), round(sx + S(14))):
            n = vnoise(G2, x / 3, y / 3 + t * 32)
            if skull.getpixel((x, y))[3] and n > 0.72 - (sy - S(8) - y) * 0.008:
                q[x, y] = pal[3 if n < 0.85 else 4]
    hot = "#dff4ff" if ph else "#ffe27a"
    for side in (-1, 1):
        ex, ey = round(sx + side * S(5)), round(sy - S(0.5))
        glow(im, ex, ey, "#6ac8ff" if ph else "#ff7a1a", 4.5, 0.85)
        for ddx, ddy in ((0, 0), (1, 0), (0, -1)):
            im.putpixel((ex + ddx, ey + ddy), rgb(hot))
    return im


# ---------------------------------------------------------------- La Llorona
# A woman in white, floating, her long black hair over her face, arms out toward you; her dress fades
# to nothing before it reaches the ground. Second phase: the hair parts and you see her face, screaming.
def llorona(t, ph):
    W, H = 96, 150
    p = Pic(W, H)
    bob = round(2 * math.sin(TAU * t))
    cx = 50
    top = 18 + bob
    sh = top + 22
    hem = H - 14 + bob
    # the dress: long, white, its folds and ragged hem swaying
    waist = sh + 18
    pts = [(cx - 10, sh), (cx + 10, sh), (cx + 7, waist)]
    for i in range(13):
        u = i / 12
        x = cx + 30 - u * 60
        pts.append((x + 2 * math.sin(TAU * t + u * 6), hem + (6 if i % 2 else 0) + round(2 * math.sin(TAU * t * 2 + i))))
    pts.append((cx - 7, waist))
    p.poly(pts, "#dfe7ec")
    for k, x0 in enumerate((-6, -1, 4, 9)):
        x1 = x0 * 2.6
        p.line([(cx + x0 * 0.6, waist + 2), (cx + x1 + 2 * math.sin(TAU * t + k), hem)], "#a9b8c4" if k % 2 else "#c2ced8", 2)
    p.poly([(cx + 4, sh + 2), (cx + 10, sh), (cx + 7, waist), (cx + 30, hem), (cx + 16, hem + 4)], "#b9c7d2")
    # the arms, reaching toward you, sleeves hanging from them like rags
    for k, (yo, reach) in enumerate(((6, 34), (13, 30))):
        ax, ay = cx - 8, sh + 3 + k * 3
        hy = sh + yo + round(1.5 * math.sin(TAU * t + k * 2))
        hx = cx - reach
        el = ((ax + hx) / 2 + 2, (ay + hy) / 2 + 3)
        # the sleeve: wide at the shoulder, hanging in a rag under the forearm
        drape = [(ax + 2, ay - 2), el, (hx + 7, hy), (hx + 8, hy + 3)]
        for j in range(6):
            u = j / 5
            drape.append((hx + 8 + u * (ax - hx - 6), hy + 10 + 6 * math.sin(u * math.pi) + (3 if j % 2 else 0) + 1.5 * math.sin(TAU * t + j)))
        p.poly(drape, "#c3cfd8" if k else "#e3eaee")
        limb(p, [el, (hx + 3, hy)], 2, 2, "#c9d3da")
        for f in range(4):
            a = math.pi + (f - 1.5) * 0.28
            p.line([(hx + 2, hy), (hx + 2 + math.cos(a) * 6, hy + math.sin(a) * 6 + 1)], "#d8e2e8", 1)
    # the head and the hair: black, long, straight down over the face to the waist
    p.ell(cx, top + 9, 8, 10, "#16161e")
    face_open = 7 if ph else 0
    if ph:  # the face: grey skin pulled tight, black eyes, the mouth open in a scream
        p.ell(cx, top + 12, 6, 9, "#b4c0c8")
        p.ell(cx - 3, top + 9, 2, 2.5, "#020203"); p.ell(cx + 3, top + 9, 2, 2.5, "#020203")
        p.ell(cx, top + 17, 2.2, 3.8, "#0a0204")
        p.line([(cx - 3, top + 11), (cx - 4, top + 17)], "#3a4a6a", 1); p.line([(cx + 3, top + 11), (cx + 4, top + 18)], "#3a4a6a", 1)
    hairc = ["#0b0b10", "#16161e", "#202029", "#2c2c38"]
    R = random.Random(5)
    for i in range(46):
        u = i / 45
        x = cx - 11 + u * 22
        if ph and abs(x - cx) < face_open:
            x = cx + (face_open + 1) * (1 if x >= cx else -1) + (x - cx) * 0.3
        L = 30 + 26 * math.sin(u * math.pi) + R.uniform(-4, 4)
        wave_line(p, x, top + 1, top + L, 2.2 if ph else 1.5, TAU * t + u * 4, R.choice(hairc), 0.15)
    p.ell(cx, top + 2, 8, 3, "#16161e")
    im = p.im
    outline(im)
    fade_down(im, H - 46 + bob, H - 6 + bob)
    if ph:
        for ex in (cx - 3, cx + 3):
            im.putpixel((ex, top + 9), rgb("#ffffff"))
            glow(im, ex, top + 9, "#bfe6ff", 2.4, 0.5)
    else:  # through the hair, one eye
        glow(im, cx - 2, top + 11, "#cfeeff", 2.6, 0.55)
        im.putpixel((cx - 2, top + 11), rgb("#f2fbff"))
    return im


# ---------------------------------------------------------------- El Mandingas
# The devil as a gentleman: tall, horns, black frock coat, a cape lined in red, a gold-topped cane, a flame
# in his open hand, a grin. Second phase: his true form, bat wings open behind him, the hem on fire.
def mandingas(t, ph):
    W, H = 150, 156
    p = Pic(W, H)
    g = H - 2
    cx = 76
    sw = math.sin(TAU * t)
    hip = g - 46
    sh = hip - 40
    hy = sh - 12
    if ph:  # wings
        for side in (-1, 1):
            root = (cx + side * 8, sh + 4)
            tips = [(cx + side * 70, sh - 34 + 3 * sw), (cx + side * 62, sh + 6 + 2 * sw), (cx + side * 52, sh + 30), (cx + side * 34, sh + 42)]
            arm = (cx + side * 44, sh - 30 + 2 * sw)
            p.poly([root, arm, tips[0], tips[1], (cx + side * 54, sh + 14), tips[2], (cx + side * 40, sh + 28), tips[3], (cx + side * 12, sh + 30)], "#4a0c12")
            p.poly([root, arm, tips[0], (cx + side * 60, sh - 20)], "#64121a")
            for tp in tips:
                p.line([arm, tp], "#1a080c", 2)
            p.line([root, arm], "#1a080c", 3)
            p.line([arm, (arm[0] + side * 2, arm[1] - 6)], "#d8ccb0", 2)
    # the cape behind him, its red lining showing where it flares
    flare = 3 * math.sin(TAU * t)
    p.poly([(cx - 14, sh), (cx + 14, sh), (cx + 26 + flare, g - 6), (cx + 10, g - 2), (cx - 10, g - 2), (cx - 26 - flare, g - 6)], "#0c0a0e")
    p.poly([(cx + 14, sh + 2), (cx + 26 + flare, g - 6), (cx + 19 + flare, g - 4), (cx + 10, sh + 8)], "#9a1420")
    p.poly([(cx - 14, sh + 2), (cx - 26 - flare, g - 6), (cx - 19 - flare, g - 4), (cx - 10, sh + 8)], "#7a0e18")
    # legs: black trousers, goat hooves
    for lx, fx in ((cx - 5, cx - 7), (cx + 5, cx + 7)):
        limb(p, [(lx, hip), (fx, g - 4)], 6, 5, "#141016")
        p.poly([(fx - 3, g - 4), (fx + 3, g - 4), (fx + 3, g), (fx - 3, g)], "#2a2226")
        p.px(fx, g, "#0a0808"); p.px(fx, g - 1, "#0a0808")
    # the frock coat, a red waistcoat, a white collar
    p.poly([(cx - 12, sh), (cx + 12, sh), (cx + 14, hip + 6), (cx + 16, hip + 22), (cx + 6, hip + 14), (cx - 6, hip + 14), (cx - 16, hip + 22), (cx - 14, hip + 6)], "#17131b")
    p.poly([(cx - 4, sh + 2), (cx + 4, sh + 2), (cx + 4, hip + 2), (cx, hip + 6), (cx - 4, hip + 2)], "#7a1018")
    p.line([(cx, sh + 8), (cx, hip + 2)], "#a8a090", 1)
    for k in range(3):
        p.px(cx + 2, sh + 12 + k * 7, "#e8b830")
    p.poly([(cx - 6, sh), (cx + 6, sh), (cx + 3, sh + 6), (cx, sh + 3), (cx - 3, sh + 6)], "#e6ded2")
    p.poly([(cx - 2, sh + 3), (cx + 2, sh + 3), (cx, sh + 9)], "#c41a2a")
    p.line([(cx + 8, sh + 2), (cx + 10, hip + 4)], "#2a2430", 1)
    # arms: the right on the cane, the left held out, palm up, a flame over it
    limb(p, [(cx + 12, sh + 2), (cx + 18, sh + 20), (cx + 22, hip)], 7, 6, "#17131b")
    p.ell(cx + 22, hip + 1, 3, 2.5, "#7a1e18")
    p.line([(cx + 23, hip - 4), (cx + 25, g)], "#1a1010", 2)
    p.ell(cx + 23, hip - 5, 2.5, 2.5, "#e8b830"); p.px(cx + 22, hip - 6, "#fff0a0")
    hx, hy2 = cx - 30, sh + 18 + round(sw)
    limb(p, [(cx - 12, sh + 2), (cx - 18, sh + 18), (hx + 4, hy2 + 1)], 7, 6, "#17131b")
    p.ell(hx + 1, hy2, 4, 2.5, "#7a1e18")
    for f in range(4):
        p.line([(hx - 2, hy2 - 1 + f * 0.6), (hx - 6, hy2 - 3 + f)], "#7a1e18", 1)
    # the head: dark red skin, a pointed beard, a grin
    skin, skin2 = ("#9a2218", "#5a120c") if ph else ("#7e2a20", "#521810")
    p.rect(cx - 2, sh - 4, cx + 2, sh, skin2)
    p.ell(cx, hy, 8, 10, skin)
    p.ell(cx + 3, hy + 1, 5, 9, skin2)
    p.poly([(cx - 4, hy + 6), (cx + 4, hy + 6), (cx, hy + 17)], "#0c080a")        # the beard
    p.poly([(cx - 9, hy - 2), (cx - 12, hy - 6), (cx - 8, hy + 1)], skin)          # pointed ears
    p.poly([(cx + 9, hy - 2), (cx + 12, hy - 6), (cx + 8, hy + 1)], skin2)
    p.line([(cx - 5, hy + 4), (cx - 2, hy + 6), (cx + 2, hy + 6), (cx + 5, hy + 4)], "#f0e8d8", 1)  # the grin
    p.line([(cx - 4, hy + 3), (cx - 1, hy + 4), (cx + 1, hy + 4), (cx + 4, hy + 3)], "#0c080a", 1)  # moustache
    p.line([(cx - 6, hy - 4), (cx - 1, hy - 2)], "#1a0606", 1); p.line([(cx + 6, hy - 4), (cx + 1, hy - 2)], "#1a0606", 1)
    p.rect(cx - 7, hy - 10, cx + 7, hy - 7, "#0c080a")                          # hair, slicked back
    # horns, curling out and up
    hl = 1.25 if ph else 1
    for side in (-1, 1):
        pts = [(cx + side * (5 + 7 * hl * math.sin(u * 2.2)), hy - 7 - 18 * hl * u ** 1.3) for u in (k / 8 for k in range(9))]
        limb(p, pts, 5, 1, "#cfc2a4")
        for k in range(1, len(pts) - 2, 2):
            p.px(pts[k][0] - side, pts[k][1], "#8a7a60")
    if ph:  # the hem burns
        R = random.Random(int(t * N) + 3)
        for k in range(30):
            x = cx - 16 + R.uniform(0, 32)
            y = hip + 14 + R.uniform(-2, 8)
            p.px(x, y, R.choice(["#ff8a1a", "#ffc83a", "#e0480e"]))
    im = shear(p.im, hip, round(1.5 * sw), sh - 40)
    outline(im)
    # the flame in his palm
    fl = 1.5 if ph else 1
    fp = Pic(W, H)
    for k, (col, wd, ht) in enumerate((("#c42010", 5, 15), ("#ff8a1a", 3.8, 12), ("#ffc83a", 2.6, 8), ("#fff2b0", 1.4, 4.5))):
        tip = 1.8 * math.sin(TAU * t * 2 + k)
        base_y = hy2 - 3
        fp.poly([(hx - wd * fl, base_y - 2), (hx - wd * 0.9 * fl, base_y - ht * 0.45 * fl), (hx + tip, base_y - ht * fl), (hx + wd * 0.9 * fl, base_y - ht * 0.45 * fl), (hx + wd * fl, base_y - 2), (hx, base_y)], col)
    glow(im, hx, hy2 - 9 * fl, "#ff8a1a", 9 * fl, 0.4)
    im.alpha_composite(fp.im)
    ex = round(1.5 * sw * (hip - hy) / (hip - sh + 40))
    for e in (cx - 3, cx + 3):
        glow(im, e + ex, hy - 2, "#ff2a1a" if ph else "#ffcf3a", 3.4, 0.75)
        im.putpixel((e + ex, hy - 2), rgb("#fff6c0"))
    return im


# ================================================================ the other two bosses of each zone
# Each episode meets one of a zone's three bosses (data.js ZONES bosses). Same rules as the first six:
# an 8-frame loop, a second row for the second phase.

def flame(im, cx, by, w, h, t, pal, seed=0, lean=0.0):
    """A licking flame standing on (cx, by), w wide and h tall, its tip leaning by lean px; pal: rgb tuples."""
    q = im.load()
    W, H = im.size
    for y in range(max(0, int(by - h - 3)), min(H, int(by + w * 0.4) + 1)):
        u = (by - y) / h
        for x in range(max(0, int(cx - w)), min(W, int(cx + w) + 1)):
            off = x - (cx + lean * max(0.0, u) ** 2)
            if u < 0:
                d = math.hypot(off / (w / 2), (y - by) / (w * 0.4))
            else:
                half = (w / 2) * (1 - min(u, 1)) ** 0.7
                d = abs(off) / half if half > 0.3 else 9
            n = vnoise(G2, (x + seed * 7) / 4, (y + seed * 11) / 4 + t * 32)
            v = 1.1 - d + (n - 0.5) * 0.9 - max(0.0, u) * 0.3
            if v < 0.12:
                continue
            q[x, y] = pal[min(len(pal) - 1, int((v - 0.12) / 0.17))]


def fade_side(im, x0, x1):
    """Dither the picture away from column x0 (whole) to x1 (gone): a beast only half there."""
    px = im.load()
    for x in range(im.width):
        k = 0 if (x - x0) * (x1 - x0) <= 0 else min(1, (x - x0) / (x1 - x0))
        if not k:
            continue
        for y in range(im.height):
            if px[x, y][3] and (BAYER[y % 4][x % 4] + 0.5) / 16 < k:
                px[x, y] = (0, 0, 0, 0)


def eyes(im, pts, col, r=3.0, hot="#ffffff", peak=0.75):
    for x, y in pts:
        x, y = round(x), round(y)
        glow(im, x, y, col, r, peak)
        if 0 <= x < im.width and 0 <= y < im.height:
            im.putpixel((x, y), rgb(hot))


def arcs(p, cx, cy, t, col, n=3, r0=8, step=9, a0=150, a1=210, w=2):
    """Sound going out to the left: rings that grow and fade."""
    for k in range(n):
        r = r0 + (k + t) * step
        p.d.arc((cx - r, cy - r, cx + r, cy + r), a0, a1, fill=rgb(col, round(255 * (1 - (k + t) / (n + 0.5)))), width=w)


def embers(im, seed, x0, x1, y0, rise, t, cols, n=14):
    """Sparks drifting up from between x0 and x1 at y0, each on its own loop."""
    R = random.Random(seed)
    for _ in range(n):
        ph, x, sp = R.random(), R.uniform(x0, x1), R.choice((1, 1, 2))
        u = (t * sp + ph) % 1
        px_, py = x + 3 * math.sin(TAU * (u + ph)), y0 - u * rise
        if 0 <= px_ < im.width and 0 <= py < im.height and u < 0.92:
            im.putpixel((round(px_), round(py)), rgb(R.choice(cols)))


def fog(im, y0, y1, t, col=(200, 210, 220), a=110, seed=1):
    """A band of mist drifting sideways (a whole loop per cycle), dithered, under whatever is there."""
    q = im.load()
    G = noise_grid(seed, 16, 8)
    W = im.width
    for y in range(max(0, y0), min(im.height, y1)):
        k = 1 - abs((y - y0) / max(1, y1 - y0) * 2 - 1)
        for x in range(W):
            n = vnoise(G, x / W * 16 + t * 16, y / 10)
            v = n * k
            if v > 0.32 and (BAYER[y % 4][x % 4] + 0.5) / 16 < (v - 0.32) * 2.2 and q[x, y][3] < 60:
                q[x, y] = (*col, a)


def hat_vueltiao(p, hx, by, t, lift=0):
    """A wide hat of woven cane, cream and black rings round the brim and crown."""
    p.poly([(hx - 21, by + 3 - lift), (hx - 11, by - 1), (hx + 11, by - 1 + lift * 0.3), (hx + 22, by + 4 + lift), (hx + 11, by + 2.5), (hx - 11, by + 2.5)], "#d8c494")
    for k, c in ((-17, "#2a1e14"), (-13, "#2a1e14"), (13, "#2a1e14"), (17, "#2a1e14")):
        p.line([(hx + k, by + (1 if abs(k) < 15 else 2)), (hx + k + (1 if k > 0 else -1), by + 2.5)], c, 1)
    p.line([(hx - 20, by + 3 - lift), (hx - 11, by + 2.5), (hx + 11, by + 2.5), (hx + 21, by + 4 + lift)], "#9a8456", 1)
    p.poly([(hx - 8, by), (hx - 7, by - 11), (hx - 2, by - 13), (hx + 3, by - 13), (hx + 7, by - 11), (hx + 9, by)], "#e2d0a2")
    p.poly([(hx + 2, by - 13), (hx + 7, by - 11), (hx + 9, by), (hx + 3, by)], "#bfa978")
    for y in (by - 9, by - 6):
        p.line([(hx - 7, y), (hx + 8, y)], "#2a1e14", 1)
    p.rect(hx - 8, by - 3, hx + 9, by - 1, "#1a120c")


# ---------------------------------------------------------------- El Gritón
# A gaunt man of the high hills: a striped ruana with a fringe, a woven mochila, a machete in its sheath,
# alpargatas, a cane hat; a hand cupped at his mouth, shouting, the mist round his feet. Second phase: head
# thrown back, arms out, the shout going out in rings and the veins standing on his neck.
def griton(t, ph):
    W, H = 116, 152
    p = Pic(W, H)
    g = H - 2
    cx = 62
    hip = g - 50
    sh = hip - 36
    sway = 2 * math.sin(TAU * t)
    R = random.Random(21)
    # legs: rolled-up trousers, thin shins, alpargatas laced up the ankle
    for k, (lx, fx) in enumerate(((cx - 5, cx - 10), (cx + 5, cx + 8))):
        knee = ((lx + fx) / 2 + (1 if k else -1), (hip + g) / 2)
        limb(p, [(lx, hip), knee], 7, 6, "#3a3428" if k else "#2e2a20")
        p.rect(knee[0] - 3, knee[1] - 1, knee[0] + 3, knee[1] + 2, "#4a4234")      # the rolled cuff
        limb(p, [(knee[0], knee[1] + 2), (fx, g - 4)], 4, 3, "#8a7a66")
        p.poly([(fx - 6, g - 3), (fx + 4, g - 3), (fx + 4, g), (fx - 7, g)], "#c8b890")
        p.line([(fx - 6, g), (fx + 4, g)], "#5a4a34", 1)
        for j in range(3):
            p.line([(fx - 2, g - 4 - j * 2), (fx + 2, g - 3 - j * 2)], "#2a2016", 1)
    # the mochila on its strap, hanging at his right hip: woven in zigzags
    mx, my = cx + 18, hip - 4
    p.line([(cx - 6, sh), (mx, my - 8)], "#7a3a1e", 2)
    p.rect(mx - 7, my - 8, mx + 7, my + 8, "#b8642a")
    for j in range(4):
        y = my - 6 + j * 4
        for i in range(-6, 7, 3):
            p.line([(mx + i, y), (mx + i + 1.5, y + 2), (mx + i + 3, y)], "#3a1a0e" if j % 2 else "#f0d8a0", 1)
    p.line([(mx - 7, my + 8), (mx + 7, my + 8)], "#5a2a12", 1)
    for i in range(-6, 7, 2):
        p.line([(mx + i, my + 9), (mx + i, my + 11)], "#7a3a1e", 1)
    # the machete on the other hip, in a tooled leather sheath
    p.poly([(cx - 16, hip - 6), (cx - 13, hip - 7), (cx - 20, hip + 26), (cx - 23, hip + 25)], "#5a3a1e")
    p.line([(cx - 15, hip - 4), (cx - 21, hip + 22)], "#8a6a3a", 1)
    p.rect(cx - 16, hip - 12, cx - 13, hip - 6, "#2a1a10")
    # the ruana: a wide blanket from the shoulders to the hips, stripes, a fringe that swings
    ru_l, ru_r = cx - 25 + sway, cx + 25 + sway
    p.poly([(cx - 7, sh - 3), (cx + 7, sh - 3), (ru_r, hip + 8), (ru_l, hip + 8)], "#6e5c44")
    p.poly([(cx + 1, sh - 3), (cx + 7, sh - 3), (ru_r, hip + 8), (cx + 6 + sway, hip + 8)], "#584a38")
    for j, c in enumerate(("#3a2f24", "#b0783a", "#d8c8a0", "#b0783a", "#3a2f24")):
        y = hip + 7 - j
        f = (y - sh + 3) / (hip + 11 - sh)
        p.line([(cx - 7 - 18 * f + sway * f, y), (cx + 7 + 18 * f + sway * f, y)], c, 1)
    for j, c in ((10, "#5a4a36"), (22, "#5a4a36")):  # folds
        p.line([(cx - 3, sh + 2), (cx - j * 0.9 + sway * 0.6, hip + 5)], c, 1)
        p.line([(cx + 4, sh + 2), (cx + j * 0.9 + sway * 0.6, hip + 5)], "#4a3e2e", 1)
    for i in range(int(ru_l) + 1, int(ru_r), 2):  # the fringe
        p.line([(i, hip + 9), (i + 0.6 * math.sin(TAU * t + i * 0.4), hip + 12 + (i % 3))], "#8a7454", 1)
    p.ell(cx, sh - 2, 6, 2.5, "#4a3e2e")                                      # the neck hole
    # arms: one hand at his mouth (phase 1), or both thrown out (phase 2); a white shirt sleeve
    skin, skin2 = "#a49280", "#7e6e5e"
    hx, hy = cx - 4, sh - 11
    if ph:
        for side, lift in ((-1, 0), (1, 3)):
            s0 = (cx + side * 10, sh + 4)
            el = (cx + side * 23, sh - 4 + lift)
            wr = (cx + side * 33, sh - 19 + lift + sway * side)
            limb(p, [s0, el], 7, 6, "#6e5c44")
            limb(p, [el, wr], 4, 3, "#d8d0c0")
            p.ell(wr[0], wr[1], 3, 3, skin)
            for f in range(4):
                a = -math.pi / 2 + side * (0.3 + f * 0.3)
                p.line([wr, (wr[0] + math.cos(a) * 6, wr[1] + math.sin(a) * 6)], skin, 1)
                p.px(wr[0] + math.cos(a) * 6, wr[1] + math.sin(a) * 6, skin2)
    else:
        el = (cx - 21, sh + 8)
        limb(p, [(cx - 8, sh + 2), el], 7, 6, "#6e5c44")
        limb(p, [el, (hx - 9, hy + 7)], 4, 3, "#d8d0c0")
        p.ell(hx - 10, hy + 5, 3.5, 4.5, skin)
        p.line([(hx - 12, hy + 2), (hx - 12, hy + 8)], skin2, 1)
        limb(p, [(cx + 11, sh + 4), (cx + 20, hip - 2)], 4, 3, "#d8d0c0")
        p.ell(cx + 20, hip, 2.5, 3, skin)
    # the head: long, hollow-cheeked, stubble, grey hair to the collar; the mouth open, pulsing
    tilt = -6 if ph else 0
    hy2 = hy + tilt * 0.3
    limb(p, [(cx, sh - 2), (hx + 1, hy + 6)], 5, 4, skin)
    if ph:
        for k in (-1, 1):
            p.line([(hx + k * 2, hy + 8), (hx + k * 2 + 1, sh - 3)], "#c0a890", 1)  # veins on the neck
    p.poly([(hx + 3, hy2 - 4), (hx + 9, hy2 - 2), (hx + 9, hy2 + 8), (hx + 5, hy2 + 6)], "#8a8478")  # grey hair
    p.ell(hx, hy2, 7, 9, skin)
    p.ell(hx + 3, hy2 + 1, 4, 7.5, skin2)
    p.line([(hx - 5, hy2 + 1), (hx - 4, hy2 + 5)], skin2, 1)                 # cheekbone
    for k in range(12):
        p.px(hx - 5 + R.uniform(0, 8), hy2 + 4 + R.uniform(0, 4), "#5e5246")  # stubble
    p.line([(hx - 6, hy2 - 4), (hx - 2, hy2 - 3)], "#3a3028", 1)
    p.line([(hx + 1, hy2 - 3), (hx + 4, hy2 - 4)], "#3a3028", 1)
    p.px(hx - 6, hy2 + 1, "#c8b8a4")                                          # nose
    mo = 2.6 + 1.4 * abs(math.sin(TAU * t * 2)) + (1.6 if ph else 0)
    p.ell(hx - 3, hy2 + 5, 2.8 + (1 if ph else 0), mo, "#120a06")
    p.line([(hx - 5, hy2 + 5 - mo + 1), (hx - 1, hy2 + 5 - mo + 1)], "#e8e0d0", 1)  # top teeth
    p.ell(hx - 3, hy2 + 5 + mo * 0.5, 1.5, 1, "#7a2a22")                         # tongue
    # the hat, tipped back in phase 2
    hat_vueltiao(p, hx, hy - 6 + tilt, t, lift=4 if ph else 0)
    if ph:
        arcs(p, hx - 10, hy2 + 4, t, "#f0e0b0", n=3, r0=10, step=11, a0=135, a1=225, w=2)
        for k in range(5):  # spit and breath
            u = (t + k / 5) % 1
            p.px(hx - 8 - u * 16, hy2 + 4 - u * 5 + k - 2, (230, 230, 220, round(220 * (1 - u))))
    im = shear(p.im, hip, round(sway), sh - 30)
    outline(im)
    eyes(im, [(hx - 4, hy2 - 2), (hx + 1, hy2 - 2)], "#ffe9a0", 2.8 if ph else 2.2, "#fffbe0", 0.65)
    fog(im, g - 14, g + 2, t, (200, 214, 224), 120, seed=21)
    return im


# ---------------------------------------------------------------- La Muelona
# A beautiful woman on the road: a white dress with lace, an embroidered red shawl with a fringe, a red
# flower and gold earrings, black hair to her waist, a crow on her shoulder; she smiles, and the smile is all
# teeth. Second phase: the jaw drops to her chest on rows of teeth like gravestones, her hair rises.
def muelona(t, ph):
    W, H = 108, 152
    p = Pic(W, H)
    g = H - 2
    cx = 56
    sw = math.sin(TAU * t)
    top = 14
    sh = top + 26
    waist = sh + 22
    R = random.Random(23)
    hairs = ["#0e0a12", "#16101c", "#201828", "#2e2438"]
    # the hair behind her: long, blowing out to the right (standing up in phase 2)
    for i in range(26):
        u = i / 25
        x0 = cx - 7 + u * 16
        L = 52 + 14 * math.sin(u * math.pi) + R.uniform(-5, 5)
        pts = []
        for y in range(top + 2, top + round(L)):
            v = (y - top) / L
            lift = (-16 * v * (u - 0.3)) if ph else 0
            pts.append((x0 + (9 + 12 * u) * v + 2.2 * math.sin(TAU * t + u * 5 + y * 0.12) * v, y + lift))
        p.line(pts, R.choice(hairs), 2)
    # bare feet with talons peeking from the hem (phase 2)
    if ph:
        for fx in (cx - 8, cx + 6):
            p.ell(fx, g - 1, 4, 2, "#c8b49c")
            for k in (-3, -1, 1):
                p.line([(fx + k, g), (fx + k - 1, g + 1)], "#2a1a12", 1)
    # the dress, to the ground, swaying; lace at the hem and the bodice
    hem = g - (4 if ph else 0)
    pts = [(cx - 9, sh), (cx + 9, sh), (cx + 7, waist)]
    for i in range(13):
        u = i / 12
        pts.append((cx + 25 - u * 50 + 2 * sw * (1 - u * 0.5), hem - (3 if i % 2 else 0)))
    pts.append((cx - 7, waist))
    p.poly(pts, "#ece4d0")
    p.poly([(cx + 3, sh), (cx + 9, sh), (cx + 7, waist), (cx + 25 + 2 * sw, hem), (cx + 11, hem)], "#c8bda6")
    for k in (-14, -6, 2, 10, 18):
        p.line([(cx + k * 0.25, waist + 3), (cx + k * 1.3 + 2 * sw * 0.6, hem - 3)], "#bcb09a" if k < 6 else "#a89c86", 1)
    for i in range(int(cx - 24), int(cx + 26), 3):  # lace scallops
        x = i + 2 * sw * 0.6
        p.ell(x, hem - 4, 1.5, 1.2, "#fffaf0")
        p.px(x, hem - 6, "#d8ceb8")
    p.line([(cx - 7, waist), (cx + 7, waist)], "#9a1e2a", 2)                   # a red sash
    p.poly([(cx + 6, waist), (cx + 10, waist + 12 + sw), (cx + 8, waist + 12 + sw), (cx + 5, waist + 2)], "#9a1e2a")
    # the shawl, red, embroidered with gold, a fringe that swings
    shw = [(cx - 13, sh + 1), (cx, sh - 3), (cx + 13, sh + 1), (cx + 10, sh + 15), (cx, sh + 19), (cx - 11, sh + 14)]
    p.poly(shw, "#a01e2c")
    p.poly([(cx, sh - 3), (cx + 13, sh + 1), (cx + 10, sh + 15), (cx, sh + 19)], "#7a1622")
    for k in range(6):
        x = cx - 9 + k * 3.6
        p.ell(x, sh + 9 + abs(k - 2.5) * 1.2, 1, 1, "#e8b830")
    p.line([(cx - 11, sh + 14), (cx, sh + 19), (cx + 10, sh + 15)], "#e8b830", 1)
    for k in range(-10, 11, 2):
        y = sh + 19 - abs(k) * 0.45
        p.line([(cx + k, y), (cx + k + 0.5 * sw, y + 3)], "#7a1622", 1)
    # arms: one reaching for you, long nails; the other at her side holding the shawl
    skin, skin2 = "#e0ccb2", "#bda68c"
    reach = 31 + (7 if ph else 0)
    hx, hy = cx - reach, sh + 12 + round(1.5 * sw)
    el = (cx - 19, sh + 15)
    limb(p, [(cx - 11, sh + 4), el], 5, 4, "#a01e2c")
    limb(p, [el, (hx, hy)], 3, 2, skin)
    p.ell(hx, hy, 2.5, 2.2, skin)
    for f in range(4):
        a = math.pi + (f - 1.5) * 0.33
        L = 6 + (3 if ph else 0)
        p.line([(hx, hy), (hx + math.cos(a) * L, hy + math.sin(a) * L)], skin, 1)
        p.px(hx + math.cos(a) * (L + 1), hy + math.sin(a) * (L + 1), "#3a0a10" if ph else "#c84a5a")
    p.ell(el[0] + 5, el[1] - 1, 2, 2, "#e8b830")                              # a bracelet
    limb(p, [(cx + 11, sh + 5), (cx + 15, waist + 4)], 3, 2.5, skin)
    p.ell(cx + 15, waist + 5, 2.5, 2.5, skin)
    # the crow on her shoulder, head turning
    bx, by = cx + 10, sh - 3
    p.ell(bx + 2, by - 2, 5, 3.5, "#141218")
    p.poly([(bx + 6, by - 2), (bx + 13, by + 2), (bx + 6, by + 1)], "#141218")     # tail
    p.ell(bx - 2, by - 6, 3, 3, "#1c1a22")
    look = 1 if (int(t * N) // 2) % 2 else 0
    p.poly([(bx - 4, by - 6), (bx - 8 - look, by - 5), (bx - 4, by - 5)], "#3a3640")
    p.line([(bx + 1, by - 3), (bx + 5, by - 1)], "#2c2a34", 1)
    p.line([(bx, by + 1), (bx, by + 3)], "#3a3640", 1)
    # the head
    hx0, hy0 = cx - 2, top + 12
    limb(p, [(cx, sh - 2), (hx0, hy0 + 6)], 4, 3.5, skin)
    p.ell(hx0, hy0 + (2 if ph else 0), 8, 10 + (3 if ph else 0), skin)
    p.ell(hx0 + 4, hy0 + 1, 4, 8, skin2)
    p.ell(hx0, hy0 - 7, 9.5, 5, "#14101a")                                     # hair on top, parted
    p.line([(hx0 - 1, hy0 - 11), (hx0 - 2, hy0 - 4)], "#2e2438", 1)
    p.poly([(hx0 - 9, hy0 - 6), (hx0 - 10, hy0 + 10), (hx0 - 7, hy0 - 1)], "#14101a")
    p.ell(hx0 - 7, hy0 - 9, 3, 2.5, "#d8202c")                                  # the flower
    p.ell(hx0 - 7, hy0 - 9, 1.2, 1.2, "#ffd84a")
    p.ell(hx0 + 7, hy0 + 3, 1, 1.5, "#e8b830")                                  # an earring
    p.px(hx0 + 7, hy0 + 5, "#ffe880")
    p.line([(hx0 - 5, hy0 - 5), (hx0 - 2, hy0 - 4)], "#2a1a1a", 1)              # brows
    p.line([(hx0 + 1, hy0 - 4), (hx0 + 4, hy0 - 5)], "#2a1a1a", 1)
    p.px(hx0 - 5, hy0 + 1, "#c8a48c")
    if ph:  # the jaw dropped to her chest: rows of big teeth, red gums, a tongue
        mt, mb = hy0 + 3, hy0 + 15 + abs(math.sin(TAU * t * 2)) * 2
        p.poly([(hx0 - 9, mt), (hx0 + 6, mt), (hx0 + 5, mb), (hx0 - 8, mb)], "#2a0608")
        p.rect(hx0 - 9, mt, hx0 + 6, mt + 2, "#b02a3a")
        p.rect(hx0 - 8, mb - 2, hx0 + 5, mb, "#b02a3a")
        p.ell(hx0 - 2, mb - 3, 3, 1.5, "#c84a5a")
        for k in range(-8, 5, 3):
            p.rect(hx0 + k, mt + 2, hx0 + k + 1, mt + 4 + (k % 2), "#f6f0dc")
            p.px(hx0 + k + 1, mt + 4, "#c8c0a8")
            p.rect(hx0 + k + 1, mb - 4 - (k % 2), hx0 + k + 2, mb - 2, "#f6f0dc")
    else:  # a smile, too wide, every tooth showing, red lips
        p.ell(hx0 - 1, hy0 + 5, 6.5, 3.2, "#b0283a")
        p.ell(hx0 - 1, hy0 + 5, 5.5, 2.4, "#2a0608")
        for k in range(-6, 5, 2):
            p.rect(hx0 + k, hy0 + 3, hx0 + k + 1, hy0 + 6, "#f6f0dc")
        p.line([(hx0 - 6, hy0 + 5), (hx0 + 4, hy0 + 5)], "#c8c0a8", 1)
    im = p.im
    outline(im)
    eyes(im, [(hx0 - 4, hy0 - 2), (hx0 + 2, hy0 - 2)], "#ff4a4a" if ph else "#fff0b0", 2.4, "#ffffff", 0.6)
    eyes(im, [(bx - 2, by - 7)], "#ffcf3a", 1.6, "#fff6c0", 0.6)
    fog(im, g - 12, g + 2, t, (200, 214, 224), 110, seed=23)
    return im


# ---------------------------------------------------------------- El Hombre Caimán
# A caiman in the Magdalena with a man's head: moustache, a straw hat, the torn collar of the shirt he went
# in with; ridged scutes down his back, pale belly plates. Water lilies and reeds round him. Second phase: he
# rears out of the water, red-eyed, and the mouth under his moustache is a caiman's.
def hombrecaiman(t, ph):
    W, H = 156, 116
    p = Pic(W, H)
    wl = 84
    sw = math.sin(TAU * t)
    rise = 15 if ph else 0
    hide, hide2, hide3, belly = "#3f5a2a", "#2b401e", "#5a7a38", "#b8b880"
    # reeds behind him
    for k, x in enumerate((122, 128, 133, 140, 146)):
        top_ = wl - 34 - (k % 3) * 8
        bend = 2 * math.sin(TAU * t + k)
        p.line([(x, wl + 4), (x + bend, top_)], "#4a6a2a" if k % 2 else "#5e7e34", 1)
        if k % 2 == 0:
            p.ell(x + bend, top_ + 4, 1.5, 4, "#6a4a24")
    # the tail, out behind, lashing; a row of double crests
    tail = [(98, wl - 6)]
    for k in range(1, 9):
        u = k / 8
        tail.append((98 + u * 52, wl - 6 + 6 * math.sin(TAU * t + u * 3) * u - u * 4))
    for k in range(len(tail) - 1):
        limb(p, [tail[k], tail[k + 1]], 15 * (1 - k / 8) + 2, 15 * (1 - (k + 1) / 8) + 2, hide)
    for k in range(1, 8):
        x, y = tail[k]
        h_ = 9 - k
        p.poly([(x - 2, y - h_ + 2), (x, y - h_ - 2), (x + 2, y - h_ + 2)], hide2)
        p.px(x, y - h_ - 1, hide3)
        p.line([(x - 1, y), (x + 1, y + 3)], hide2, 1)
    # the body, long and low, tilted up at the front in phase 2: rows of scutes, the belly
    for k in range(10):
        u = k / 9
        x = 40 + u * 62
        y = wl - 8 - rise * (1 - u)
        p.ell(x, y, 12, 10 - u * 2, hide)
        p.ell(x + 2, y + 2, 9, 6 - u, hide2)
        p.ell(x, y + 6, 10, 3, belly)
        for j in (-6, 0, 6):
            p.line([(x + j - 1, y + 5), (x + j + 1, y + 8)], "#8a8a5a", 1)
    for k in range(13):  # the scutes: two rows of ridged plates down the back
        u = k / 12
        x = 38 + u * 64
        y = wl - 17 - rise * (1 - (x - 40) / 62) + u * 2
        for j in (-2, 2):
            p.poly([(x + j - 2, y + 3), (x + j, y - 2), (x + j + 2, y + 3)], hide2)
            p.px(x + j, y - 1, hide3)
        p.px(x, y + 5, hide3)
    # front legs, claws on the bank
    for k, lx in enumerate((44, 60)):
        ly = wl - 6 - rise * (1 - (lx - 40) / 62)
        foot = (lx - 10 + k * 2, wl + 4 - (rise * 0.6 if ph else 0) + (sw * 1.5 if k else 0))
        limb(p, [(lx, ly), (lx - 6, ly + 8), foot], 7, 4, hide)
        for j in range(3):
            p.px(lx - 3 + j, ly + 4 + j, hide3)
        for f in (-1, 0, 1):
            p.line([foot, (foot[0] - 5, foot[1] + 2 + f * 2)], "#d8d0a8", 1)
    # the neck, scaled, and the torn collar of his shirt
    hx, hy = 26, wl - 26 - rise
    limb(p, [(42, wl - 10 - rise), (hx + 4, hy + 7)], 13, 10, hide)
    for j in range(4):
        p.ell(32 + j * 3, wl - 14 - rise + j, 1.5, 1, hide3)
    p.poly([(hx + 2, hy + 10), (hx + 12, hy + 8), (hx + 14, hy + 14), (hx + 8, hy + 12), (hx + 4, hy + 16)], "#d8d0c0")
    p.line([(hx + 8, hy + 9), (hx + 8, hy + 12)], "#9a9488", 1)
    # the head: a man's, weathered; moustache, an ear; a straw hat
    skin, skin2 = "#a87e58", "#86644a"
    p.ell(hx, hy, 9, 10.5, skin)
    p.ell(hx + 4, hy + 1, 5, 8.5, skin2)
    p.ell(hx + 8, hy + 1, 2, 3, skin2)                                          # ear
    p.line([(hx - 6, hy - 4), (hx - 2, hy - 3)], "#2a1a10", 1)
    p.line([(hx + 1, hy - 3), (hx + 4, hy - 4)], "#2a1a10", 1)
    p.poly([(hx - 8, hy + 1), (hx - 5, hy - 1), (hx - 5, hy + 3)], skin)         # nose
    p.line([(hx - 4, hy + 6), (hx + 2, hy + 5)], "#8a6448", 1)                 # wrinkle
    if ph:  # a caiman's jaws where his mouth should be
        p.poly([(hx - 20, hy + 3), (hx + 2, hy + 2), (hx + 2, hy + 6), (hx - 20, hy + 6)], hide)
        p.poly([(hx - 20, hy + 10), (hx + 2, hy + 9), (hx + 2, hy + 15), (hx - 18, hy + 15)], hide)
        p.rect(hx - 19, hy + 6, hx + 1, hy + 10, "#6a0e0e")
        p.ell(hx - 8, hy + 9, 4, 1, "#c84a4a")
        for k in range(-18, 0, 3):
            p.poly([(k + hx, hy + 6), (k + hx + 1, hy + 9), (k + hx + 2, hy + 6)], "#f4f0dc")
            p.poly([(k + hx + 1, hy + 10), (k + hx + 2, hy + 7), (k + hx + 3, hy + 10)], "#f4f0dc")
        p.ell(hx - 18, hy + 3, 1.5, 1, "#1a2a10")                              # nostrils
        for j in range(5):
            p.px(hx - 16 + j * 3, hy + 4, hide3)
    p.poly([(hx - 7, hy + 4), (hx - 1, hy + 3), (hx + 1, hy + 6), (hx - 3, hy + 5), (hx - 8, hy + 7)], "#2a1a10")  # moustache
    if not ph:
        p.line([(hx - 4, hy + 8), (hx, hy + 8)], "#4a2a1a", 1)
    by = hy - 8
    p.poly([(hx - 18, by + 3), (hx - 9, by - 1), (hx + 9, by - 1), (hx + 18, by + 3), (hx + 9, by + 1.5), (hx - 9, by + 1.5)], "#c8b07a")
    p.line([(hx - 17, by + 3), (hx - 9, by + 1.5), (hx + 9, by + 1.5), (hx + 17, by + 3)], "#8a7448", 1)
    p.poly([(hx - 7, by), (hx - 5, by - 9), (hx + 6, by - 9), (hx + 8, by)], "#d4bd88")
    p.line([(hx - 5, by - 6), (hx + 6, by - 6)], "#b09a68", 1)
    for k in range(-6, 8, 3):
        p.px(hx + k, by - 4, "#a08a58")
    p.rect(hx - 7, by - 2, hx + 8, by - 1, "#3a2416")
    im = p.im
    outline(im)
    eyes(im, [(hx - 4, hy - 1), (hx + 2, hy - 1)], "#ff3a2a" if ph else "#e8ff7a", 2.6, "#ffffff", 0.7)
    # the river over his lower half: dark water, ripples catching the light, lilies
    q = im.load()
    for y in range(wl, H):
        for x in range(W):
            r, gg, b, a = q[x, y]
            band = (y + round(2 * math.sin(x * 0.2 + TAU * t * 2))) % 6
            col = (60, 110, 96) if band == 0 else (32, 66, 62) if band < 3 else (22, 48, 46)
            if a:
                q[x, y] = (round(r * 0.3 + col[0] * 0.7), round(gg * 0.3 + col[1] * 0.7), round(b * 0.3 + col[2] * 0.7), 255)
            elif y < wl + 26 and 6 < x < 152 and (BAYER[y % 4][x % 4] + 0.5) / 16 > (y - wl) / 28:
                q[x, y] = (*col, 210)
    for x in range(8, 150, 2):
        y = wl + round(1.2 * math.sin(x * 0.25 + TAU * t * 2))
        q[x, y] = (160, 210, 190, 255)
    lp = Pic(W, H)
    for k, (lx, ly) in enumerate(((10, wl + 6), (74, wl + 14), (136, wl + 9))):
        ly += round(math.sin(TAU * t + k))
        lp.ell(lx, ly, 7, 2.5, "#3e7a34")
        lp.poly([(lx, ly), (lx + 7, ly - 1), (lx + 7, ly + 1)], (0, 0, 0, 0))
        lp.line([(lx - 6, ly), (lx + 4, ly)], "#2a5a24", 1)
        if k != 1:
            lp.ell(lx - 1, ly - 2, 2.5, 2, "#f0c8e0"); lp.px(lx - 1, ly - 3, "#ffe8f4"); lp.px(lx - 1, ly - 2, "#e8c040")
    im.alpha_composite(lp.im)
    if ph:  # drops flung up as he rears
        for k in range(8):
            u = (t + k / 8) % 1
            x = 50 + k * 6 + u * 4 * (1 if k % 2 else -1)
            y = wl - 2 - 22 * u + 26 * u * u
            if 0 <= y < H:
                im.putpixel((round(x), round(y)), (190, 230, 220, 255))
    return im


# ---------------------------------------------------------------- El Riviel
# Half a canoe gliding on black water, its planks and a net over the side, a gourd in it; a hooded figure in
# a frayed cloak holds up a candle dripping wax, its light under the hood just showing a face of bone. Mist on
# the water, fireflies. Second phase: the flame grows, and you see the skull clearly.
def riviel(t, ph):
    W, H = 144, 138
    im = Image.new("RGBA", (W, H))
    p = Pic(W, H)
    wl = 114
    bob = 1.5 * math.sin(TAU * t)
    # the canoe: cut off square at the back, the front curving up; planks, ribs, the cut end splintered
    cy = wl - 4 + bob
    p.poly([(16, cy - 13), (25, cy - 6), (116, cy - 6), (116, cy + 6), (34, cy + 6), (21, cy - 2)], "#3a2616")
    p.poly([(25, cy - 6), (116, cy - 6), (116, cy - 3), (27, cy - 3)], "#5e3e22")
    p.line([(30, cy + 1), (116, cy + 1)], "#2a1a0e", 1)
    p.line([(36, cy + 4), (116, cy + 4)], "#2e1e10", 1)
    for x in range(40, 112, 14):
        p.line([(x, cy - 6), (x - 1, cy + 5)], "#24160c", 1)
    p.poly([(114, cy - 7), (118, cy - 5), (116, cy - 1), (119, cy + 2), (116, cy + 7), (113, cy + 7)], "#24160c")
    p.px(18, cy - 12, "#7a5a34")
    # the net over the side, dripping
    for i in range(6):
        x = 46 + i * 4
        p.line([(x, cy - 6), (x - 1, cy + 9 + (i % 2) * 2)], "#8a8470", 1)
    for j in range(3):
        p.line([(46, cy - 2 + j * 4), (66, cy - 1 + j * 4)], "#8a8470", 1)
    # a gourd and a paddle laid in the canoe
    p.ell(100, cy - 9, 5, 4, "#a8742a"); p.ell(100, cy - 13, 2, 2, "#8a5a1e"); p.px(98, cy - 10, "#d8a050")
    p.line([(26, cy - 9), (60, cy - 7)], "#6a4a2a", 2)
    p.ell(24, cy - 9, 3, 2, "#6a4a2a")
    # the figure: a hood and a cloak with folds and a frayed hem; it never looks at you
    fx = 80
    top = cy - 66
    pts = [(fx - 13, cy - 6)]
    for i in range(7):
        u = i / 6
        pts.append((fx - 13 + u * 28, cy - 6 + (2 if i % 2 else 0)))
    pts += [(fx + 15, cy - 6), (fx + 10, top + 18), (fx, top + 3), (fx - 10, top + 18)]
    p.poly(pts, "#1e1c26")
    p.poly([(fx, top + 3), (fx + 10, top + 18), (fx + 15, cy - 6), (fx + 3, cy - 6)], "#14121a")
    for k in (-6, 2, 8):
        p.line([(fx + k * 0.5, top + 24), (fx + k, cy - 7)], "#2a2834", 1)
    p.line([(fx - 9, top + 18), (fx - 6, top + 10), (fx, top + 4)], "#2e2c3a", 1)   # hood rim
    p.ell(fx - 1, top + 15, 7, 8.5, "#08060c")                                     # inside the hood
    # the face of bone, lit from below by the candle
    bone = "#c8c0a8" if ph else "#5a5448"
    p.ell(fx - 2, top + 16, 4.5, 5.5, bone)
    p.ell(fx - 4, top + 15, 1.5, 1.8, "#08060c"); p.ell(fx, top + 15, 1.5, 1.8, "#08060c")
    p.line([(fx - 4, top + 19), (fx, top + 19)], "#08060c", 1)
    for k in range(-4, 1, 2):
        p.px(fx + k, top + 20, bone)
    # the arm, holding the candle up and out in front; bony fingers
    hx, hy = fx - 24, top + 18 + bob * 0.5
    limb(p, [(fx - 7, top + 26), (fx - 17, top + 27), (hx + 1, hy + 3)], 6, 4, "#1e1c26")
    for k in range(3):  # the sleeve's rags
        p.line([(fx - 15 + k * 3, top + 30), (fx - 16 + k * 3, top + 34 + k)], "#1e1c26", 1)
    for k in range(4):
        p.line([(hx - 1 + k * 1.2, hy + 2), (hx - 1 + k * 1.2, hy - 1)], "#c8c0b0", 1)
    p.rect(hx - 2, hy - 15, hx + 2, hy, "#efe6cc")                               # the candle
    p.rect(hx - 1, hy - 15, hx, hy, "#fffaf0")
    for k, dl in ((-2, 5), (2, 8), (-2, 10)):                                      # wax runs
        p.line([(hx + k, hy - 15), (hx + k, hy - 15 + dl)], "#fff6e0", 1)
        p.px(hx + k, hy - 14 + dl, "#e0d4b0")
    p.ell(hx, hy + 1, 3.5, 1.2, "#d8ccaa")
    p.px(hx, hy - 16, "#2a2016")
    im.alpha_composite(p.im)
    outline(im)
    fh = 28 if ph else 17
    pal = [rgb(c) for c in ("#6a3a08", "#c8780e", "#ffb020", "#ffe07a", "#fff6cc", "#ffffff")]
    glow(im, hx, hy - 20, "#ffe07a", 16 if ph else 11, 0.32)
    flame(im, hx, hy - 16, 9 if ph else 6, fh, t, pal, seed=2, lean=3 * math.sin(TAU * t))
    eyes(im, [(fx - 4, top + 15), (fx, top + 15)], "#ffe07a", 2.2 if ph else 1.6, "#fff6cc", 0.6)
    # the water: black, a long shimmer under the flame, ripples behind the canoe
    q = im.load()
    for y in range(wl + 2, H):
        for x in range(W):
            dist = abs(x - hx) / 34 + (y - wl) / 32
            light = max(0.0, 1 - dist) * (1.4 if ph else 1.0)
            if abs(x - hx + 2 * math.sin(y * 0.9 + TAU * t * 2)) < 2 and (y + int(t * 8)) % 3:
                light += 0.6 * max(0.0, 1 - (y - wl) / 24)
            base = (8, 14, 24)
            col = tuple(min(255, round(base[i] + light * (110, 84, 24)[i])) for i in range(3))
            r, gg, b, a = q[x, y]
            if a:
                q[x, y] = (round(r * 0.35 + col[0] * 0.65), round(gg * 0.35 + col[1] * 0.65), round(b * 0.35 + col[2] * 0.65), 255)
            elif (BAYER[y % 4][x % 4] + 0.5) / 16 > 0.42 + (y - wl) / 50 - light * 0.4:
                q[x, y] = (*col, 230)
    for k in range(5):  # the wake
        x0 = 118 + k * 6 + round(t * 6)
        for x in range(x0, min(W, x0 + 4)):
            q[x, wl + 3 + k % 2] = (120, 140, 150, 200)
    fog(im, wl - 10, wl + 4, t, (170, 190, 200), 90, seed=31)
    R = random.Random(31)  # fireflies
    for k in range(6):
        ph0 = R.random()
        x = R.uniform(10, 130) + 6 * math.sin(TAU * (t + ph0))
        y = R.uniform(20, 90) + 4 * math.cos(TAU * (t * 2 + ph0))
        if math.sin(TAU * (t + ph0)) > -0.3:
            glow(im, x, y, "#d8ff8a", 2.2, 0.6)
    return im


# ---------------------------------------------------------------- La Patasola
# A woman on one thick leg ending in a hoof, crouched to jump; wild hair full of leaves and twigs, a torn
# green dress with a vine for a belt, long arms with long nails, the jungle's mud on her. Second phase: her
# face draws out into a snout of fangs, eyes red, hair standing, and she jumps twice as fast.
def patasola(t, ph):
    W, H = 112, 158
    p = Pic(W, H)
    g = H - 2
    cx = 58
    hop = abs(math.sin(TAU * t * (2 if ph else 1)))
    lift = round(14 * hop)
    crouch = round(8 * (1 - hop))
    hip = g - 46 - lift + crouch
    sh = hip - 34
    R = random.Random(41)
    skin, skin2, skin3 = "#8a6650", "#6a4c3a", "#a8806a"
    # the hair behind her, wild: long strands, leaves and twigs caught in it
    hx, hy = cx - 3, sh - 10
    for i in range(44):
        a = math.pi * 0.85 + (i / 43) * math.pi * 1.3 + R.uniform(-0.08, 0.08)
        L = 18 + R.uniform(0, 14) + (8 if ph else 0)
        mid = (hx + math.cos(a) * L * 0.5, hy + math.sin(a) * L * 0.4 + 6)
        end = (hx + math.cos(a) * L + 2.5 * math.sin(TAU * t + i), hy + math.sin(a) * L * (0.5 if ph else 0.9) + (8 if ph else 22))
        p.line([(hx, hy - 3), mid, end], R.choice(("#1a1410", "#241a14", "#2e241c", "#3a2c20")), 2)
    for i in range(9):
        a = math.pi * 0.9 + R.uniform(0, math.pi * 1.2)
        L = R.uniform(8, 20)
        x, y = hx + math.cos(a) * L, hy + math.sin(a) * L * 0.6 + 8
        if i % 3:
            p.ell(x, y, 2, 1.2, R.choice(("#3d6a2c", "#5a8a34", "#7a6a2a")))
        else:
            p.line([(x, y), (x + 4, y - 2)], "#5a3e24", 1)
    # the one leg: a thick thigh, the knee forward, the shin to a hoof
    knee = (cx - 8, hip + 20 + crouch * 0.3 - lift * 0.2)
    foot = (cx - 2, g - 4 - lift)
    limb(p, [(cx, hip), knee], 13, 9, skin)
    limb(p, [knee, foot], 9, 6, skin)
    p.line([(cx - 3, hip + 4), (knee[0] + 1, knee[1] - 2)], skin3, 1)
    p.line([(knee[0] + 3, knee[1] + 2), (foot[0] + 2, foot[1] - 3)], skin2, 1)
    p.ell(knee[0] - 1, knee[1], 4, 3, skin3)
    for j in range(5):  # mud splashed up the shin
        p.px(foot[0] - 3 + R.uniform(0, 6), foot[1] - 2 - R.uniform(0, 10), "#3a2a1a")
    p.poly([(foot[0] - 7, foot[1]), (foot[0] + 5, foot[1]), (foot[0] + 4, foot[1] + 5), (foot[0] - 1, foot[1] + 5), (foot[0] - 1, foot[1] + 2), (foot[0] - 2, foot[1] + 5), (foot[0] - 8, foot[1] + 5)], "#241812")
    p.line([(foot[0] - 7, foot[1] + 1), (foot[0] + 4, foot[1] + 1)], "#4a3428", 1)
    # the dress: green, torn into strips, a leaf pattern, a vine for a belt
    pts = [(cx - 12, sh + 2), (cx + 12, sh + 2), (cx + 13, hip)]
    for i in range(10):
        u = i / 9
        pts.append((cx + 17 - u * 34, hip + 9 + (9 if i % 2 else 0) + round(2 * math.sin(TAU * t + i))))
    pts.append((cx - 13, hip))
    p.poly(pts, "#3d5a34")
    p.poly([(cx + 3, sh + 2), (cx + 12, sh + 2), (cx + 13, hip), (cx + 17, hip + 9), (cx + 7, hip + 15)], "#2c4426")
    for k in range(14):
        x, y = cx - 10 + R.uniform(0, 20), sh + 6 + R.uniform(0, hip - sh)
        p.line([(x, y), (x + 2, y - 1)], "#4e7040" if k % 2 else "#2a3e22", 1)
    for k in (-9, -2, 5):
        p.line([(cx + k, hip + 2), (cx + k * 1.3, hip + 14)], "#2c4426", 1)
    p.line([(cx - 12, hip - 4), (cx - 4, hip - 2), (cx + 4, hip - 3), (cx + 13, hip - 4)], "#5a7a2a", 2)
    p.ell(cx - 6, hip - 2, 2, 1.3, "#7aa83a"); p.ell(cx + 6, hip - 3, 2, 1.3, "#7aa83a")
    p.line([(cx + 8, hip - 3), (cx + 10, hip + 8 + sw2(t))], "#5a7a2a", 1)
    # arms: long, reaching down and forward, veins, long nails
    nails = "#3a0a0a" if ph else "#d8ccb0"
    for side, reach in ((-1, 36), (1, 18)):
        s0 = (cx + side * 11, sh + 4)
        el = (cx + side * 18 - (6 if side < 0 else 0), sh + 21)
        wr = (cx - reach if side < 0 else cx + reach, sh + 41 - lift * 0.3)
        limb(p, [s0, el], 6, 5, skin)
        limb(p, [el, wr], 5, 3, skin)
        p.line([(el[0], el[1] + 2), ((el[0] + wr[0]) / 2, (el[1] + wr[1]) / 2 + 1)], skin2, 1)
        p.ell(wr[0], wr[1], 3, 2.5, skin)
        for f in range(4):
            a = math.pi / 2 + side * -0.3 + (f - 1.5) * 0.3 + (0.6 if side < 0 else 0)
            L = 7 + (4 if ph else 0)
            p.line([wr, (wr[0] + math.cos(a) * L * 0.6, wr[1] + math.sin(a) * L * 0.6)], skin, 1)
            p.line([(wr[0] + math.cos(a) * L * 0.6, wr[1] + math.sin(a) * L * 0.6), (wr[0] + math.cos(a) * L, wr[1] + math.sin(a) * L)], nails, 1)
    # the head
    p.ell(hx, hy, 8, 9.5, skin)
    p.ell(hx + 3, hy + 1, 4.5, 8, skin2)
    p.line([(hx - 6, hy + 1), (hx - 5, hy + 5)], skin2, 1)
    p.line([(hx - 6, hy - 4), (hx - 2, hy - 3)], "#1a0e0a", 1)
    p.line([(hx + 1, hy - 3), (hx + 4, hy - 4)], "#1a0e0a", 1)
    if ph:  # the snout, the fangs
        p.poly([(hx - 13, hy + 2), (hx - 1, hy - 1), (hx + 2, hy + 9), (hx - 11, hy + 9)], skin)
        p.poly([(hx - 13, hy + 2), (hx - 11, hy + 9), (hx - 5, hy + 9), (hx - 9, hy + 5)], skin2)
        p.ell(hx - 12, hy + 2, 1.5, 1, "#1a0806")
        p.rect(hx - 11, hy + 5, hx, hy + 8, "#2a0606")
        for k in (-10, -7, -4, -1):
            p.poly([(hx + k, hy + 5), (hx + k + 1, hy + 9 + (k % 2) * 2), (hx + k + 2, hy + 5)], "#f4eedc")
    else:
        p.px(hx - 6, hy + 2, skin3)
        p.line([(hx - 5, hy + 5), (hx + 1, hy + 5)], "#200606", 1)
        p.px(hx - 3, hy + 6, "#5a3020")
    p.ell(hx, hy - 7, 9, 4, "#1a1410")
    im = p.im
    outline(im)
    eyes(im, [(hx - 4, hy - 1), (hx + 2, hy - 1)], "#ff2a2a" if ph else "#ffb070", 2.6, "#ffffff", 0.7)
    # mud kicked up as she lands
    if hop < 0.35:
        for k in range(8):
            a = math.pi + k / 7 * math.pi
            r = (0.35 - hop) * 30
            x, y = foot[0] + math.cos(a) * r, g - 2 + math.sin(a) * r * 0.4
            if 0 <= x < W and 0 <= y < H:
                im.putpixel((round(x), round(y)), rgb("#4a3420"))
    return im


def sw2(t):
    return round(1.5 * math.sin(TAU * t + 1))


# ---------------------------------------------------------------- La Tunda
# A figure in a long purple shawl with an embroidered border and a fringe, a gentle face under it: the face
# of someone you know. In her other hand a calabash of river shrimp to lure you. Purple lights float round
# her. Second phase: the face falls away like a mask; under it, bark, moss and two lights, and below the skirt
# one leg is a carved wooden stick (her pata de molinillo).
def tunda(t, ph):
    W, H = 112, 150
    p = Pic(W, H)
    g = H - 2
    cx = 58
    sw = math.sin(TAU * t)
    top = 16
    sh = top + 24
    hem = g - (15 if ph else 2)
    R = random.Random(43)
    if ph:  # the legs: one a gnarled foot, one the molinillo
        limb(p, [(cx + 6, hem - 4), (cx + 8, g - 2)], 7, 6, "#3a2a22")
        p.line([(cx + 6, hem), (cx + 8, g - 4)], "#5a4232", 1)
        p.ell(cx + 6, g - 1, 6, 2, "#241812")
        for k in (-4, -1, 2):
            p.line([(cx + 6 + k, g), (cx + 4 + k, g + 1)], "#120a06", 1)
        p.rect(cx - 11, hem - 4, cx - 7, g - 7, "#8a6a42")
        p.line([(cx - 10, hem - 4), (cx - 10, g - 7)], "#b08a58", 1)
        for y in (hem + 1, hem + 6):
            p.rect(cx - 12, y, cx - 6, y + 1, "#5a4228")
        p.ell(cx - 9, g - 4, 4.5, 4, "#9a7a4e")
        for k in range(-4, 5, 2):
            p.line([(cx - 9 + k, g - 7), (cx - 9 + k * 1.1, g - 1)], "#5a4228", 1)
    # the shawl: over the head, down to the hem; a border of zigzags, a fringe
    pts = [(cx - 7, top), (cx + 7, top), (cx + 13, sh)]
    for i in range(12):
        u = i / 11
        pts.append((cx + 25 - u * 52 + 2 * sw, hem + (3 if i % 2 else 0)))
    pts.append((cx - 15, sh))
    p.poly(pts, "#4c2a60")
    p.poly([(cx + 2, top), (cx + 7, top), (cx + 13, sh), (cx + 25 + 2 * sw, hem), (cx + 11, hem + 2)], "#3a2048")
    for k in (-14, -6, 2, 10):
        p.line([(cx + k * 0.4, sh + 4), (cx + k * 1.6 + 2 * sw, hem - 4)], "#5e3a74" if k < 4 else "#2e1a3a", 1)
    for i in range(12):  # the border, a zigzag in gold and pink
        u = i / 11
        x0 = cx + 25 - u * 52 + 2 * sw
        p.line([(x0, hem - 4), (x0 + 2, hem - 6), (x0 + 4, hem - 4)], "#e8b830" if i % 2 else "#e86aa8", 1)
    for x in range(int(cx - 27 + 2 * sw), int(cx + 26 + 2 * sw), 2):  # the fringe
        p.line([(x, hem + 2), (x + 0.6 * sw, hem + 5 + (x % 3))], "#6a3a84", 1)
    p.line([(cx - 7, top), (cx - 15, sh), (cx - 17, sh + 20)], "#6a4284", 1)
    # a hand out of the shawl, beckoning; the other holding a calabash of shrimp
    skin = "#4a3a32" if ph else "#c8b4a4"
    bk = 3 * math.sin(TAU * t * 2)
    hx, hy = cx - 31, sh + 14
    limb(p, [(cx - 12, sh + 8), (cx - 22, sh + 16), (hx, hy)], 6, 4, "#4c2a60")
    p.ell(hx, hy, 2.5, 2.5, skin)
    p.line([(hx, hy), (hx - 4, hy - 3 + bk)], skin, 1)
    p.line([(hx, hy), (hx - 3, hy - 5 + bk)], skin, 1)
    p.ell(hx + 5, hy - 1, 1.5, 1.5, "#e8b830")                                  # a ring
    bx, by = cx + 20, sh + 26
    limb(p, [(cx + 12, sh + 8), (cx + 18, sh + 20), (bx - 2, by - 1)], 6, 4, "#3a2048")
    p.poly([(bx - 9, by - 2), (bx + 9, by - 2), (bx + 6, by + 5), (bx - 6, by + 5)], "#9a6a2a")
    p.line([(bx - 8, by), (bx + 8, by)], "#5a3a14", 1)
    p.line([(bx - 6, by + 3), (bx + 6, by + 3)], "#c88a3a", 1)
    for k in range(5):  # shrimp, pink, curled
        x = bx - 6 + k * 3
        p.ell(x, by - 3 - (k % 2), 1.8, 1.4, "#ff8a8a")
        p.px(x - 1, by - 4 - (k % 2), "#ffc8b8")
        p.line([(x + 1, by - 4), (x + 3, by - 7 - (k % 2))], "#ffb0a0", 1)
    # the face inside the hood
    fx, fy = cx - 3, top + 12
    p.ell(fx, fy, 7.5, 9.5, "#1a0e20")
    if ph:  # bark, cracked, mossy; a hole of a mouth with thorns; the mask on the ground
        p.ell(fx, fy + 1, 6.5, 8.5, "#4a3a2e")
        p.ell(fx + 2, fy + 2, 3.5, 6.5, "#3a2c22")
        for k in range(4):
            p.line([(fx - 4 + k * 2.5, fy - 7), (fx - 5 + k * 2.5 + (k % 2) * 2, fy + 8)], "#241812", 1)
        for k in range(6):
            p.px(fx - 5 + R.uniform(0, 10), fy - 6 + R.uniform(0, 4), "#4e7a34")
        p.ell(fx - 1, fy + 5, 3, 2.5, "#0a0404")
        for k in (-3, -1, 1):
            p.px(fx + k, fy + 3, "#d8c8a0")
        mx, my = cx - 28, g - 3
        p.ell(mx, my, 6.5, 4, "#d8c8b8")
        p.ell(mx + 2, my, 3, 3, "#bfae9e")
        p.px(mx - 2, my - 1, "#3a2a2a"); p.px(mx + 2, my - 1, "#3a2a2a")
        p.line([(mx - 2, my + 2), (mx, my + 2.5), (mx + 2, my + 2)], "#9a5a6a", 1)
        p.line([(mx + 3, my - 3), (mx + 1, my + 3)], "#8a7a6a", 1)          # cracked
    else:  # a gentle face, eyes half closed, a small smile, hair under the hood
        p.ell(fx, fy + 1, 6.5, 8.5, "#d8c8b8")
        p.ell(fx + 3, fy + 2, 3, 6.5, "#bfae9e")
        p.poly([(fx - 7, fy - 5), (fx + 5, fy - 7), (fx + 6, fy - 3), (fx - 6, fy - 2)], "#2a1a20")
        p.line([(fx - 5, fy - 1), (fx - 2, fy)], "#5a4a4a", 1)
        p.line([(fx + 1, fy), (fx + 3, fy - 1)], "#5a4a4a", 1)
        p.px(fx - 4, fy + 2, "#e8b0b0"); p.px(fx + 3, fy + 2, "#d8a0a0")
        p.line([(fx - 2, fy + 5), (fx, fy + 6), (fx + 2, fy + 5)], "#a85a6a", 1)
        p.px(fx - 5, fy + 1, "#c8a89a")
    im = p.im
    outline(im)
    if ph:
        eyes(im, [(fx - 3, fy - 1), (fx + 2, fy - 1)], "#c88aff", 3.2, "#ffffff", 0.85)
    else:
        glow(im, fx, fy, "#d8b8ff", 10, 0.22)
    Rl = random.Random(44)  # will-o'-the-wisps
    for k in range(5):
        ph0 = Rl.random()
        x = Rl.uniform(8, 104) + 5 * math.sin(TAU * (t + ph0))
        y = Rl.uniform(30, 120) - 6 * math.sin(TAU * (t + ph0 * 2))
        glow(im, x, y, "#c88aff", 2.6, 0.7)
    return im


# ---------------------------------------------------------------- El Bracamonte
# Nobody has seen it: a bull-shaped dark as big as a hut; shaggy fur, a hump, horns ridged and chipped, old
# scars, moonlight along its back, its breath steaming; the back of it not quite there. Second phase: it rears,
# four eyes, horns longer, the mouth open on teeth, red light breaking through cracks along its spine.
def bracamonte(t, ph):
    W, H = 160, 128
    p = Pic(W, H)
    g = H - 2
    sw = math.sin(TAU * t)
    rear = 11 if ph else 0
    body, body2, rim = "#1e1812", "#2c2219", "#4a4038"
    R = random.Random(45)
    # legs, with knees and fetlocks, cloven hooves
    for k, (lx, ly) in enumerate(((52, 76), (68, 78), (106, 78), (122, 76))):
        front = k < 2
        top_ = (lx, ly - (rear if front else 0))
        foot = (lx - 2 + (sw * 2 if k % 2 else -sw * 2), g - 3 - (rear * 1.4 if front else 0))
        knee = ((top_[0] + foot[0]) / 2 + 2, (top_[1] + foot[1]) / 2)
        limb(p, [top_, knee], 12, 8, body if k % 2 else body2)
        limb(p, [knee, foot], 7, 6, body)
        p.ell(knee[0], knee[1], 4, 3, body2)
        for j in range(3):  # shaggy hair at the fetlock
            p.line([(foot[0] - 3 + j * 3, foot[1] - 5), (foot[0] - 4 + j * 3, foot[1] - 1)], "#2e261e", 1)
        p.poly([(foot[0] - 5, foot[1] - 1), (foot[0] + 5, foot[1] - 1), (foot[0] + 5, foot[1] + 2), (foot[0] + 1, foot[1] + 2), (foot[0], foot[1]), (foot[0] - 1, foot[1] + 2), (foot[0] - 5, foot[1] + 2)], "#0c0a08")
    # the body: a hump over the shoulders, a long back, the tail with its tuft
    p.ell(92, 68 - rear * 0.5, 46, 23, body)
    p.ell(64, 55 - rear, 27, 27, body)
    p.ell(70, 48 - rear, 18, 16, body2)
    tail = [(132, 60), (140, 56 + 4 * sw), (146, 64 + 5 * sw), (148, 76 + 4 * sw)]
    limb(p, tail, 4, 2, body)
    for j in range(5):
        p.line([tail[-1], (tail[-1][0] - 3 + j * 1.5, tail[-1][1] + 6)], "#14100c", 1)
    # fur: shaggy strokes all over, the moonlight catching the top of the back
    for i in range(180):
        x = R.uniform(40, 136)
        y = R.uniform(30, 90)
        inside = ((x - 92) / 46) ** 2 + ((y - 68 + rear * 0.5) / 23) ** 2 < 1 or ((x - 64) / 27) ** 2 + ((y - 55 + rear) / 27) ** 2 < 1
        if not inside:
            continue
        L = R.uniform(2, 5)
        a = math.pi / 2 + R.uniform(-0.5, 0.5)
        top_edge = y < 52 - rear if x < 80 else y < 50
        p.line([(x, y), (x + math.cos(a) * L, y + math.sin(a) * L)], rim if top_edge else R.choice(("#14100c", "#2a2018", "#342a20")), 1)
    for x in range(44, 132, 2):  # the rim of moonlight
        y = (55 - rear - math.sqrt(max(0, 27 ** 2 - (x - 64) ** 2))) if x < 82 else (68 - rear * 0.5 - 23 * math.sqrt(max(0, 1 - ((x - 92) / 46) ** 2)))
        p.px(x, y + 1, "#6a6458")
    for (x0, y0) in ((84, 62), (100, 70)):  # old scars
        p.line([(x0, y0), (x0 + 8, y0 + 5)], "#4a3a30", 1)
        p.line([(x0 + 2, y0 + 3), (x0 + 4, y0)], "#4a3a30", 1)
    # the dewlap and the head, low, horns out wide, a ring through the nose
    hx, hy = 32, 63 - rear * 1.6
    limb(p, [(54, 56 - rear), (hx + 4, hy)], 23, 17, body)
    p.poly([(hx + 6, hy + 8), (hx + 22, hy + 10), (hx + 14, hy + 20)], body)
    p.ell(hx, hy, 13, 11.5, body)
    for j in range(12):  # the forelock
        x = hx - 4 + j
        p.line([(x, hy - 10), (x - 1 + math.sin(j), hy - 3 + (j % 3))], "#2e261e", 1)
    p.ell(hx - 8, hy + 6, 7.5, 6.5, body2)                                     # the muzzle
    p.ell(hx - 12, hy + 6, 1.5, 1.5, "#050403"); p.ell(hx - 9, hy + 8, 1.5, 1.5, "#050403")
    p.d.arc((hx - 13, hy + 7, hx - 7, hy + 13), 20, 200, fill=rgb("#b8a060"), width=1)
    if ph:
        p.poly([(hx - 14, hy + 10), (hx - 2, hy + 9), (hx - 4, hy + 15), (hx - 12, hy + 15)], "#3a0806")
        for k in range(-13, -3, 3):
            p.poly([(hx + k, hy + 10), (hx + k + 1, hy + 13), (hx + k + 2, hy + 10)], "#e8e0c8")
    hl = 23 if ph else 17
    for side in (-1, 1):
        base = (hx + 3, hy - 8)
        mid = (base[0] + side * hl * 0.6, base[1] - hl * 0.3)
        tip = (hx + 3 + side * hl * 0.6 - 6, hy - 8 - hl)
        col, col2 = ("#d8ccb0", "#9a8e74") if side > 0 else ("#bfb294", "#857a62")
        limb(p, [base, mid, tip], 7, 2, col)
        for j in range(1, 4):  # ridges
            u = j / 4
            x = base[0] + (mid[0] - base[0]) * u * 1.6 if u < 0.6 else mid[0] + (tip[0] - mid[0]) * (u - 0.6) * 2.5
            y = base[1] + (mid[1] - base[1]) * u * 1.6 if u < 0.6 else mid[1] + (tip[1] - mid[1]) * (u - 0.6) * 2.5
            p.px(x, y, col2); p.px(x + 1, y, col2)
    p.px(hx + 3 + hl * 0.6 - 6, hy - 6 - hl, "#1e1812")                             # a chipped tip
    im = p.im
    outline(im)
    if ph:  # red light through cracks along the spine
        for k in range(7):
            x = 58 + k * 10
            y = (32 - rear) if x < 80 else 47 + (x - 80) * 0.05
            for j in range(4):
                xx, yy = round(x + j * (1 if k % 2 else -1)), round(y + j * 2)
                if 0 <= xx < W and 0 <= yy < H:
                    im.putpixel((xx, yy), rgb("#ff5a1a" if j < 3 else "#ffb070"))
            glow(im, x, y + 3, "#ff3a1a", 5, 0.35 + 0.2 * math.sin(TAU * t * 2 + k))
    fade_side(im, 104, 156)
    ey = [(hx - 5, hy - 2), (hx + 4, hy - 2)]
    if ph:
        ey += [(hx - 3, hy - 7), (hx + 6, hy - 6)]
    eyes(im, ey, "#ff3a1a" if ph else "#ffb040", 3.0, "#fff0c0", 0.8)
    if ph:
        glow(im, hx, hy, "#ff3a1a", 26, 0.16)
    # breath: puffs out of the nostrils, drifting forward and up
    q = im.load()
    for k in range(3):
        u = (t + k / 3) % 1
        bx, by = hx - 15 - u * 22, hy + 7 - u * 9
        r = 2 + u * 7
        for y in range(int(by - r), int(by + r) + 1):
            for x in range(int(bx - r), int(bx + r) + 1):
                if 0 <= x < W and 0 <= y < H and math.hypot(x - bx, y - by) <= r and (BAYER[y % 4][x % 4] + 0.5) / 16 > u * 0.8:
                    if not q[x, y][3]:
                        q[x, y] = (210, 214, 220, round(200 * (1 - u)))
    fog(im, g - 10, g + 2, t, (150, 140, 120), 100, seed=45)
    return im


# ---------------------------------------------------------------- La Sayona
# A tall woman in a white dress with lace and pintucks, a sheer veil to her waist with long black hair and
# a sad pale face behind it, a rosary in her clasped hands, gliding along the road. Second phase: she lifts the
# veil; behind it, a cracked skull, black tears, and the dress torn open on bare ribs.
def sayona(t, ph):
    W, H = 100, 160
    p = Pic(W, H)
    bob = round(2 * math.sin(TAU * t))
    cx = 52
    top = 12 + bob
    sh = top + 24
    waist = sh + 20
    hem = H - 10 + bob
    R = random.Random(47)
    # black hair down her back, under the veil
    for i in range(16):
        u = i / 15
        x = cx - 9 + u * 18
        wave_line(p, x, top + 4, sh + 22 + 6 * math.sin(u * math.pi), 1.4, TAU * t + u * 4, R.choice(("#0e0c12", "#18161e", "#22202a")), 0.15, 2)
    # the dress, long, narrow, pintucks, lace at the hem, the cuffs
    pts = [(cx - 9, sh), (cx + 9, sh), (cx + 7, waist)]
    for i in range(14):
        u = i / 13
        pts.append((cx + 21 - u * 42 + 2 * math.sin(TAU * t + u * 5), hem + (4 if i % 2 else 0)))
    pts.append((cx - 7, waist))
    p.poly(pts, "#f2eff6")
    p.poly([(cx + 3, sh), (cx + 9, sh), (cx + 7, waist), (cx + 21, hem), (cx + 9, hem + 3)], "#cfcadb")
    for k in (-10, -5, 0, 5, 10):
        p.line([(cx + k * 0.4, waist + 2), (cx + k * 1.7 + 2 * math.sin(TAU * t + k), hem - 3)], "#dcd8e6" if k < 4 else "#bcb6cc", 1)
    for k in range(-5, 6, 2):
        p.line([(cx + k, sh + 3), (cx + k * 0.8, waist - 1)], "#dad6e4", 1)
    for i in range(14):  # lace, two rows of little holes
        u = i / 13
        x = cx + 21 - u * 42 + 2 * math.sin(TAU * t + u * 5)
        p.px(x, hem - 3, "#bcb6cc"); p.px(x + 1.5, hem - 6, "#c8c2d6")
    p.line([(cx - 7, waist), (cx + 7, waist)], "#d8d0e8", 2)
    if ph:  # torn open: ribs
        p.poly([(cx - 6, sh + 4), (cx + 4, sh + 3), (cx + 3, waist - 2), (cx - 5, waist)], "#1a1418")
        for k in range(4):
            y = sh + 7 + k * 3.5
            p.line([(cx - 5, y + 1), (cx - 1, y - 0.5), (cx + 3, y + 1)], "#e0d8c4", 1)
        p.line([(cx - 1, sh + 5), (cx - 1, waist - 2)], "#c8c0ac", 1)
    # arms: hands clasped on a rosary (phase 1); lifting the veil and reaching for you (phase 2)
    skin = "#d8d4dc" if not ph else "#c8c0b8"
    if ph:
        limb(p, [(cx - 8, sh + 3), (cx - 18, sh + 10), (cx - 33, sh + 10 + bob)], 4, 2, "#f2eff6")
        hx_, hy_ = cx - 33, sh + 10 + bob
        for f in range(4):
            a = math.pi + (f - 1.5) * 0.3
            p.line([(hx_, hy_), (hx_ + math.cos(a) * 7, hy_ + math.sin(a) * 7)], "#efe8e0", 1)
            p.px(hx_ + math.cos(a) * 4, hy_ + math.sin(a) * 4, "#a89a8a")
        limb(p, [(cx + 8, sh + 3), (cx + 15, sh - 6), (cx + 9, top + 3)], 4, 2, "#f2eff6")
    else:
        limb(p, [(cx - 8, sh + 3), (cx - 11, sh + 14), (cx - 2, waist - 1)], 4, 3, "#f2eff6")
        limb(p, [(cx + 8, sh + 3), (cx + 9, sh + 14), (cx + 1, waist - 1)], 4, 3, "#e0dcea")
        p.ell(cx - 1, waist - 1, 3.5, 2.5, skin)
        for k in range(10):  # the rosary
            p.px(cx - 1 + math.sin(k * 0.7) * 3, waist + 2 + k * 2.2, "#6a5a8a")
        p.line([(cx - 3, waist + 25), (cx + 1, waist + 25)], "#c8b070", 1)
        p.line([(cx - 1, waist + 23), (cx - 1, waist + 29)], "#c8b070", 1)
    # the head and the veil
    hx, hy = cx - 1, top + 11
    if ph:  # a skull, cracked, black tears, the jaw hanging open; the veil thrown back
        p.ell(hx, hy, 7, 8.5, "#ece4d0")
        p.ell(hx + 3, hy + 1, 3.5, 7, "#c8bea8")
        p.ell(hx - 3, hy - 1, 2.5, 2.8, "#0a0606"); p.ell(hx + 3, hy - 1, 2.5, 2.8, "#0a0606")
        p.line([(hx - 3, hy + 2), (hx - 4, hy + 8)], "#1a0a10", 1); p.line([(hx + 3, hy + 2), (hx + 4, hy + 7)], "#1a0a10", 1)
        p.line([(hx + 1, hy - 8), (hx + 2, hy - 4), (hx + 1, hy - 2)], "#8a8070", 1)
        p.poly([(hx, hy + 2), (hx - 1, hy + 4), (hx + 1, hy + 4)], "#0a0606")
        jaw = 2 + abs(math.sin(TAU * t * 2)) * 2.5
        p.rect(hx - 4, hy + 5, hx + 4, hy + 6 + jaw, "#1a0a0a")
        for k in range(-4, 5, 2):
            p.px(hx + k, hy + 5, "#ffffff"); p.px(hx + k, hy + 6 + jaw, "#ffffff")
        vt = top - 4
        veil = Pic(W, H)
        veil.poly([(hx - 7, vt + 4), (hx + 6, vt - 1), (hx + 20, vt + 34 + 2 * math.sin(TAU * t)), (hx + 10, vt + 38)], (236, 232, 246, 200))
        veil.line([(hx + 6, vt - 1), (hx + 20, vt + 34 + 2 * math.sin(TAU * t))], (255, 255, 255, 230), 1)
        p.im.alpha_composite(veil.im)
    else:  # a sad pale face behind the sheer veil
        p.ell(hx, hy, 7, 8.5, "#d8d0c8")
        p.ell(hx + 3, hy + 1, 3, 7, "#bfb6ae")
        p.line([(hx - 4, hy - 1), (hx - 2, hy)], "#4a4050", 1)
        p.line([(hx + 1, hy), (hx + 3, hy - 1)], "#4a4050", 1)
        p.line([(hx - 2, hy + 5), (hx, hy + 4.5), (hx + 2, hy + 5)], "#9a7a8a", 1)
        veil = Pic(W, H)
        pts = [(hx - 9, top - 1), (hx + 9, top - 1)]
        for i in range(10):
            u = i / 9
            pts.append((hx + 14 - u * 28 + 1.5 * math.sin(TAU * t + i), sh + 14 + (3 if i % 2 else 0)))
        veil.poly(pts, (240, 236, 250, 150))
        veil.ell(hx, top + 1, 9, 4.5, (245, 242, 252, 220))
        for i in range(10):
            u = i / 9
            veil.px(hx + 14 - u * 28 + 1.5 * math.sin(TAU * t + i), sh + 13 + (3 if i % 2 else 0), (255, 255, 255, 240))
        veil.line([(hx - 9, top), (hx - 13, sh + 14)], (255, 255, 255, 200), 1)
        p.im.alpha_composite(veil.im)
    im = p.im
    outline(im)
    fade_down(im, H - 38 + bob, H - 4 + bob)
    if ph:
        eyes(im, [(hx - 3, hy - 1), (hx + 3, hy - 1)], "#bfe0ff", 2.8, "#ffffff", 0.8)
    else:
        eyes(im, [(hx - 3, hy), (hx + 2, hy)], "#a8b8ff", 1.8, "#e8f0ff", 0.35)
    fog(im, H - 18, H, t, (210, 214, 230), 110, seed=47)
    return im


# ---------------------------------------------------------------- El Cura sin Cabeza
# A priest in a black cassock with a row of buttons, a purple sash and a stole with gold crosses; a chained
# breviary at his belt, a rosary; a bronze bell held out ringing, a candle dripping in the other hand. Above
# his collar, nothing but a blue flame, and candles float round him. Second phase: he carries his own skull,
# and it looks at you; the bones of the ruins rise.
def curasincabeza(t, ph):
    W, H = 112, 154
    im = Image.new("RGBA", (W, H))
    p = Pic(W, H)
    g = H - 2
    cx = 58
    sw = math.sin(TAU * t)
    sh = 44
    # the cassock to the ground, folds, buttons down the front, its hem swinging; shoes
    for fx in (cx - 6, cx + 6):
        p.ell(fx, g - 1, 4, 2, "#0a080c"); p.px(fx - 2, g - 2, "#3a3444")
    pts = [(cx - 13, sh), (cx + 13, sh)]
    for i in range(11):
        u = i / 10
        pts.append((cx + 21 - u * 42 + 2 * sw, g - 3 - (2 if i % 2 else 0)))
    p.poly(pts, "#16141c")
    p.poly([(cx + 3, sh), (cx + 13, sh), (cx + 21 + 2 * sw, g - 3), (cx + 7, g - 3)], "#0e0c12")
    for k in (-14, -8, 9, 15):
        p.line([(cx + k * 0.5, sh + 22), (cx + k + 2 * sw * 0.7, g - 5)], "#22202a" if k < 0 else "#08060a", 1)
    for y in range(sh + 4, g - 6, 4):
        p.px(cx - 1, y, "#4a4454")
    p.line([(cx - 13, sh + 30), (cx + 13, sh + 30)], "#5a2a6a", 3)                 # the sash
    p.poly([(cx + 8, sh + 31), (cx + 11, sh + 46 + sw), (cx + 6, sh + 46 + sw), (cx + 5, sh + 31)], "#5a2a6a")
    p.line([(cx + 6, sh + 46 + sw), (cx + 11, sh + 46 + sw)], "#7a4a8a", 1)
    for side in (-1, 1):  # the stole, gold crosses
        x = cx + side * 6
        p.rect(x - 2, sh, x + 2, sh + 40, "#7a1a2a")
        p.line([(x - 1, sh + 33), (x + 1, sh + 33)], "#e8b830", 1); p.line([(x, sh + 31), (x, sh + 36)], "#e8b830", 1)
        p.rect(x - 2, sh + 40, x + 2, sh + 42, "#e8b830")
    # the breviary, chained at the belt
    p.line([(cx - 10, sh + 31), (cx - 14, sh + 40)], "#8a8a92", 1)
    p.rect(cx - 19, sh + 40, cx - 10, sh + 51, "#3a1a14")
    p.rect(cx - 18, sh + 41, cx - 17, sh + 50, "#d8ceb0")
    p.line([(cx - 15, sh + 43), (cx - 15, sh + 48)], "#e8b830", 1); p.line([(cx - 16, sh + 45), (cx - 14, sh + 45)], "#e8b830", 1)
    # the collar
    p.rect(cx - 8, sh - 3, cx + 8, sh + 1, "#f0f0f0")
    p.rect(cx - 2, sh - 3, cx + 2, sh + 1, "#16141c")
    p.ell(cx, sh - 3, 6, 2, "#060408")
    # the rosary, swinging
    rx = cx + 3 + sw
    for k in range(10):
        p.px(rx + math.sin(k * 0.6) * 2, sh + 34 + k * 2.5, "#c8b070")
    p.line([(rx - 2, sh + 60), (rx + 2, sh + 60)], "#c8b070", 1); p.line([(rx, sh + 58), (rx, sh + 63)], "#c8b070", 1)
    # arms: the bell held out toward you, ringing; the candle (or his skull) in the other hand; white cuffs
    ring = 3 * math.sin(TAU * t * 2)
    bx, by = cx - 31, sh + 18
    limb(p, [(cx - 11, sh + 3), (cx - 21, sh + 16), (bx + 5, by)], 7, 6, "#16141c")
    p.rect(bx + 3, by - 3, bx + 7, by + 2, "#e8e8e8")
    p.ell(bx + 2, by, 2.5, 2.5, "#c8c0b0")
    p.rect(bx + ring * 0.3 - 1, by - 2, bx + ring * 0.3 + 1, by + 2, "#4a2a14")
    p.poly([(bx + ring * 0.3 - 2, by + 2), (bx - 7 + ring, by + 14), (bx + 7 + ring, by + 14), (bx + ring * 0.3 + 2, by + 2)], "#b08a3a")
    p.poly([(bx + ring * 0.3, by + 2), (bx + 7 + ring, by + 14), (bx + 3 + ring, by + 14)], "#7a5a24")
    p.line([(bx - 5 + ring, by + 11), (bx + 5 + ring, by + 11)], "#e0c060", 1)
    p.line([(bx - 7 + ring, by + 14), (bx + 7 + ring, by + 14)], "#5a4018", 1)
    p.ell(bx + ring * 1.3, by + 15, 1.6, 1.6, "#5a4018")
    if abs(ring) > 2:
        p.d.arc((bx - 14, by - 2, bx + 14, by + 26), 150, 210, fill=rgb("#e0c060", 120), width=1)
    ox, oy = cx + 27, sh + 16
    limb(p, [(cx + 11, sh + 3), (cx + 21, sh + 14), (ox - 2, oy)], 7, 6, "#16141c")
    p.rect(ox - 4, oy - 3, ox, oy + 2, "#e8e8e8")
    p.ell(ox, oy, 2.5, 2.5, "#c8c0b0")
    if ph:  # the skull in his hand, eyes on you, a crack, a few teeth gone
        sx, sy = ox, oy - 8
        p.ell(sx, sy, 7.5, 7.5, "#e8dcc0")
        p.ell(sx + 2, sy + 1, 4, 6, "#c4b896")
        p.ell(sx - 3, sy, 2.2, 2.4, "#0a0606"); p.ell(sx + 2, sy, 2.2, 2.4, "#0a0606")
        p.poly([(sx, sy + 2), (sx - 1, sy + 4), (sx + 1, sy + 4)], "#0a0606")
        p.rect(sx - 3, sy + 5, sx + 3, sy + 7, "#1a0a0a")
        for k in (-3, -1, 3):
            p.px(sx + k, sy + 5, "#ffffff")
        p.line([(sx - 2, sy - 7), (sx - 1, sy - 3)], "#8a7a5a", 1)
    else:
        p.rect(ox - 1, oy - 13, ox + 1, oy - 3, "#efe6cc")
        p.line([(ox + 1, oy - 13), (ox + 1, oy - 8)], "#fff8e8", 1)
        p.ell(ox, oy - 2, 3, 1, "#d8ccaa")
    im.alpha_composite(p.im)
    outline(im)
    blue = [rgb(c) for c in BLUE]
    glow(im, cx, sh - 14, "#5ab8ff", 16, 0.25)
    flame(im, cx, sh - 4, 13 if ph else 10, 32 if ph else 24, t, blue, seed=4, lean=2 * sw)
    embers(im, 7, cx - 6, cx + 6, sh - 20, 30, t, ["#bfe8ff", "#5ab8ff", "#ffffff"], 8)
    pal = [rgb(c) for c in ("#6a3a08", "#c8780e", "#ffb020", "#ffe07a", "#fff6cc")]
    if not ph:
        flame(im, ox, oy - 14, 4, 8, t, pal, seed=6)
    else:
        eyes(im, [(ox - 3, oy - 8), (ox + 2, oy - 8)], "#7ab8ff", 2.6, "#ffffff", 0.85)
    # floating candles round him
    for k in range(3):
        a = TAU * (t + k / 3)
        x, y = cx + math.cos(a) * 40, 30 + math.sin(a) * 6 + k * 6
        if 2 < x < W - 3:
            cp = Pic(W, H)
            cp.rect(x - 1, y, x + 1, y + 6, "#efe6cc")
            im.alpha_composite(cp.im)
            flame(im, x, y - 1, 3, 6, t, pal, seed=10 + k)
    if ph:  # bones rising from the ground
        for k, bx2 in enumerate((14, 96)):
            u = (t + k * 0.5) % 1
            y = g - 4 - u * 10
            bp = Pic(W, H)
            bp.line([(bx2 - 4, y), (bx2 + 4, y - 2)], "#d8ceb0", 2)
            bp.ell(bx2 - 5, y, 1.5, 1.5, "#d8ceb0"); bp.ell(bx2 + 5, y - 2, 1.5, 1.5, "#d8ceb0")
            im.alpha_composite(bp.im)
    return im


# ---------------------------------------------------------------- La Mano Peluda
# A hand as big as a dog, on its own, walking on its fingertips like a spider: wrinkled knuckles, veins, long
# yellowed nails, an old gold ring, coarse black hair on its back, a torn lace cuff and a gold cufflink at the
# wrist. Second phase: the nails grow long and red, veins glow, and an eye opens on its back.
def manopeluda(t, ph):
    W, H = 148, 116
    p = Pic(W, H)
    g = H - 2
    skin, skin2, skin3 = "#b08868", "#8a6a50", "#c8a080"
    walk = TAU * t * (2 if ph else 1)
    bx, by = 78, 54 + round(2 * math.sin(walk * 2))
    # the cuff at the wrist: a frilled shirt cuff, torn, a velvet sleeve end, a gold cufflink
    p.poly([(bx + 28, by - 14), (bx + 48, by - 17), (bx + 53, by + 11), (bx + 48, by + 7), (bx + 44, by + 14), (bx + 39, by + 9), (bx + 32, by + 14)], "#6a1a22")
    p.poly([(bx + 36, by - 16), (bx + 48, by - 17), (bx + 53, by + 11), (bx + 44, by + 10)], "#4a1018")
    for k in range(6):  # lace frill
        y = by - 12 + k * 4.5
        p.ell(bx + 28 - (k % 2), y, 2.5, 2.2, "#ece4d0")
        p.px(bx + 27 - (k % 2), y, "#c8c0ac")
    p.ell(bx + 40, by - 2, 2.2, 2.2, "#e8b830"); p.px(bx + 39, by - 3, "#fff0a0")
    p.ell(bx + 49, by - 3, 4, 12, "#2a060c")
    # fingers: four legs walking on their tips; nails; the thumb in front
    nail = "#c8202a" if ph else "#e0d4a8"
    nl = 8 if ph else 3
    for k in range(4):
        ph_k = walk + k * math.pi / 2
        up = max(0.0, math.sin(ph_k)) * 8
        base = (bx - 26 + k * 3, by - 8 + k * 5)
        tipx = bx - 66 + k * 13 + math.cos(ph_k) * 3
        knuckle = ((base[0] + tipx) / 2 + 4, by - 28 + k * 5 - up)
        joint = ((knuckle[0] + tipx) / 2 - 2, knuckle[1] + 12 + k)
        tip = (tipx, g - 3 - up * 0.6)
        col = skin if k % 2 else skin2
        limb(p, [base, knuckle], 9 - k * 0.5, 7, col)
        limb(p, [knuckle, joint], 7, 6, col)
        limb(p, [joint, tip], 6, 5, col)
        for j in range(3):  # wrinkles at the knuckles
            p.line([(knuckle[0] - 3, knuckle[1] + j - 1), (knuckle[0] + 2, knuckle[1] + j - 2)], "#6a4a34", 1)
            p.line([(joint[0] - 3, joint[1] + j - 1), (joint[0] + 2, joint[1] + j - 1)], "#7a5a40", 1)
        p.line([(knuckle[0] - 1, knuckle[1] - 3), (base[0], base[1] - 4)], skin3, 1)
        p.line([tip, (tip[0] - 2, tip[1] + 2 + nl * 0.4), (tip[0] - nl * 0.6, tip[1] + nl * 0.5)], nail, 2)
        if k == 2:  # the old ring
            rx_, ry_ = (base[0] + knuckle[0]) / 2, (base[1] + knuckle[1]) / 2
            p.ell(rx_, ry_, 4.5, 2.5, "#c8981e"); p.ell(rx_ - 1, ry_ - 2, 2, 2, "#2a8a5a"); p.px(rx_ - 2, ry_ - 3, "#8affc8")
    tb = (bx - 10, by + 12)
    tt = (bx - 14 + math.sin(walk) * 3, g - 4)
    limb(p, [tb, (bx - 8, by + 24), tt], 10, 7, skin)
    p.line([(bx - 10, by + 22), (bx - 6, by + 23)], "#6a4a34", 1)
    p.line([tt, (tt[0] - nl * 0.6, tt[1] + 2)], nail, 2)
    # the back of the hand, knuckles, veins, the hair
    p.ell(bx, by, 32, 18, skin)
    p.ell(bx + 6, by + 5, 24, 11, skin2)
    p.ell(bx - 6, by - 7, 20, 7, skin3)
    for k in range(4):
        p.ell(bx - 24 + k * 6, by - 4 + k * 2, 5, 4, "#c8a080")
        p.px(bx - 25 + k * 6, by - 6 + k * 2, "#e0c0a0")
    vein = "#ff4a2a" if ph else "#7a6aa0"
    for k in range(3):
        p.line([(bx + 24, by - 2 + k * 3), (bx + 8, by - 4 + k * 4), (bx - 12 + k * 6, by - 2 + k * 3)], vein, 1)
    R = random.Random(4)
    for i in range(130):
        x = bx + R.uniform(-26, 28)
        y = by + R.uniform(-16, 9)
        if ((x - bx) / 30) ** 2 + ((y - by) / 17) ** 2 > 1:
            continue
        a = -math.pi / 2 + R.uniform(-0.6, 0.9) + 0.25 * math.sin(walk + i) + (-0.5 if ph else 0)
        L = R.uniform(4, 7) + (2 if ph else 0)
        p.line([(x, y), (x + math.cos(a) * L, y + math.sin(a) * L)], R.choice(("#1a120c", "#1a120c", "#3a2a1e", "#4a3a2a")), 1)
    if ph:
        p.ell(bx + 4, by - 4, 7, 4.5, "#f4ecd8")
        p.ell(bx + 3, by - 4, 3, 3.5, "#8a0a0a")
        p.ell(bx + 3, by - 4, 1.2, 2.2, "#0a0202")
        p.line([(bx - 3, by - 8), (bx + 4, by - 9), (bx + 11, by - 7)], "#6a4a34", 1)
    im = p.im
    outline(im)
    if ph:
        eyes(im, [(bx + 3, by - 4)], "#ff3a2a", 3.6, "#ffffff", 0.7)
    q = im.load()  # its shadow
    for x in range(30, 130):
        y = g
        if not q[x, y][3] and (BAYER[y % 4][x % 4] + 0.5) / 16 < 0.5:
            q[x, y] = (0, 0, 0, 120)
    return im


# ---------------------------------------------------------------- La Candileja
# Three flames that run together through the hills; in the middle one, an old woman: a black shawl, white hair
# streaming up into the fire, bony hands, a face screaming; sparks and smoke going up. Second phase: they split,
# and each flame has a face of its own (the old woman, a skull, a crying child), burning hotter.
def candileja(t, ph):
    W, H = 144, 150
    im = Image.new("RGBA", (W, H))
    fire = [rgb(c) for c in FIRE]
    hot = [rgb(c) for c in ("#6a1808", "#c8400e", "#ff8a1a", "#ffc83a", "#fff2b0", "#ffffff")]
    g = H - 6
    # smoke over it all, drifting up
    sp = Pic(W, H)
    for k in range(6):
        u = (t + k / 6) % 1
        x = 72 + 18 * math.sin(k * 2.1) + u * 10
        y = 30 - u * 26
        sp.ell(x, y, 5 + u * 7, 3 + u * 4, (60, 50, 48, round(55 * (1 - u))))
    im.alpha_composite(sp.im)
    if ph:
        heads = [(32, g - 10, 36, 74, 1), (72, g, 42, 104, 3), (112, g - 10, 36, 74, 5)]
    else:
        heads = [(44, g - 4, 28, 60, 1), (72, g, 48, 118, 3), (100, g - 4, 28, 60, 5)]
    # the old woman's dark shape inside the middle flame (phase 1)
    if not ph:
        sx = 72 + 2 * math.sin(TAU * t + 3)
        bp = Pic(W, H)
        bp.poly([(sx - 16, g), (sx - 12, g - 40), (sx - 6, g - 58), (sx + 6, g - 58), (sx + 12, g - 40), (sx + 16, g)], (30, 8, 4, 200))
        im.alpha_composite(bp.im)
    for x, y, w, h, s in heads:
        flame(im, x + 2 * math.sin(TAU * t + s), y, w, h, t, hot if ph else fire, seed=s, lean=4 * math.sin(TAU * t + s))
    p = Pic(W, H)
    faces = heads if ph else heads[1:2]
    kinds = ("vieja", "calavera", "nino") if ph else ("vieja",)
    for (x, y, w, h, s), kind in zip(faces if ph else faces, kinds if ph else ("vieja",)):
        if ph:
            kind = {1: "calavera", 3: "vieja", 5: "nino"}[s]
        fx, fy = x + 2 * math.sin(TAU * t + s), y - h * 0.44
        r = w * 0.2
        if kind == "vieja":
            # white hair streaming up into the fire
            for i in range(9):
                a = -math.pi / 2 + (i - 4) * 0.22
                L = r * 2.2 + 3 * math.sin(TAU * t * 2 + i)
                p.line([(fx + (i - 4) * 1.2, fy - r * 0.8), (fx + math.cos(a) * L, fy - r * 0.6 + math.sin(a) * L)], "#f0e8d8" if i % 2 else "#c8c0b0", 1)
            p.ell(fx, fy, r, r * 1.2, (40, 10, 4, 200))
            p.ell(fx, fy + r * 0.15, r * 0.82, r * 1.02, "#6a3418")
            p.ell(fx + r * 0.35, fy + r * 0.2, r * 0.4, r * 0.8, "#4a200e")
            for k in (-1, 1):
                p.line([(fx + k * r * 0.65, fy + r * 0.2), (fx + k * r * 0.45, fy + r * 0.8)], "#2a0e06", 1)
                p.line([(fx + k * r * 0.2, fy - r * 0.15), (fx + k * r * 0.55, fy - r * 0.15)], "#2a0e06", 1)
            p.line([(fx - r * 0.6, fy - r * 0.55), (fx - r * 0.1, fy - r * 0.4)], "#e8e0d0", 1)
            p.line([(fx + r * 0.1, fy - r * 0.4), (fx + r * 0.6, fy - r * 0.55)], "#e8e0d0", 1)
            p.poly([(fx, fy - r * 0.1), (fx - r * 0.25, fy + r * 0.35), (fx + r * 0.05, fy + r * 0.3)], "#7a4020")
            p.ell(fx, fy + r * 0.65, r * 0.35, r * 0.25 + abs(math.sin(TAU * t * 2 + s)) * 1.5, "#1a0402")
            p.px(fx - r * 0.15, fy + r * 0.5, "#e8dcc0")
            if not ph:  # the black shawl round the face, bony hands up
                p.d.arc((fx - r * 1.3, fy - r * 1.4, fx + r * 1.3, fy + r * 1.5), 100, 260, fill=rgb("#1a0a06"), width=3)
                for side in (-1, 1):
                    hx_, hy_ = fx + side * r * 2.2, fy + r * 1.4 + 2 * math.sin(TAU * t + side)
                    p.line([(fx + side * r, fy + r * 2.4), (hx_, hy_)], "#2a1008", 2)
                    for f in range(3):
                        a = -math.pi / 2 + side * (0.3 + f * 0.3)
                        p.line([(hx_, hy_), (hx_ + math.cos(a) * 4, hy_ + math.sin(a) * 4)], "#5a2a14", 1)
        elif kind == "calavera":
            p.ell(fx, fy, r, r * 1.1, "#e8d8b0")
            p.ell(fx + r * 0.3, fy + r * 0.1, r * 0.5, r * 0.9, "#c0a478")
            p.ell(fx - r * 0.4, fy - r * 0.05, r * 0.3, r * 0.32, "#1a0402"); p.ell(fx + r * 0.4, fy - r * 0.05, r * 0.3, r * 0.32, "#1a0402")
            p.poly([(fx, fy + r * 0.3), (fx - r * 0.15, fy + r * 0.5), (fx + r * 0.15, fy + r * 0.5)], "#1a0402")
            p.rect(fx - r * 0.45, fy + r * 0.7, fx + r * 0.45, fy + r * 0.9 + abs(math.sin(TAU * t * 2)) * 1.5, "#1a0402")
            for k in range(-2, 3):
                p.px(fx + k * r * 0.18, fy + r * 0.7, "#fff8e0")
        else:  # a child, crying
            p.ell(fx, fy, r * 0.95, r, (40, 10, 4, 200))
            p.ell(fx, fy + r * 0.1, r * 0.8, r * 0.85, "#7a4020")
            p.ell(fx + r * 0.3, fy + r * 0.15, r * 0.35, r * 0.65, "#5a2a14")
            p.ell(fx, fy + r * 0.5, r * 0.3, r * 0.3 + abs(math.sin(TAU * t * 2 + 1)), "#1a0402")
            for k in (-1, 1):
                p.line([(fx + k * r * 0.35, fy), (fx + k * r * 0.4, fy + r * 0.5)], "#ffe8a0", 1)
    im.alpha_composite(p.im)
    for x, y, w, h, s in faces:
        fx, fy = x + 2 * math.sin(TAU * t + s), y - h * 0.44
        r = w * 0.2
        eyes(im, [(fx - r * 0.4, fy - r * 0.05), (fx + r * 0.4, fy - r * 0.05)], "#fff2b0", 2.4, "#ffffff", 0.8)
    embers(im, 51, 20, 124, g - 30, 90, t, ["#ffc83a", "#ff8a1a", "#fff2b0", "#e0480e"], 26)
    # scorched ground under the flames
    q = im.load()
    for x in range(14, 132):
        for y in (g + 3, g + 4):
            if not q[x, y][3] and (BAYER[y % 4][x % 4] + 0.5) / 16 < 0.6:
                q[x, y] = (40, 14, 6, 200)
    return im


# ---------------------------------------------------------------- El Ánima Sola
# A woman rising out of flames as on the old prints: long dark hair, eyes turned up, tears; a pale dress with
# folds, torn sleeves; heavy shackles on her wrists and chains falling into the fire; sparks and smoke. Second
# phase: she throws her arms wide and the chains swing, the fire climbs, and a cold light falls on her from above.
def anima(t, ph):
    W, H = 116, 156
    im = Image.new("RGBA", (W, H))
    p = Pic(W, H)
    cx = 58
    bob = round(1.5 * math.sin(TAU * t))
    top = 20 + bob
    sh = top + 22
    waist = sh + 26
    R = random.Random(53)
    if ph:  # the light from above
        lp = Pic(W, H)
        lp.poly([(cx - 8, 0), (cx + 8, 0), (cx + 26, H - 30), (cx - 26, H - 30)], (160, 255, 220, 40))
        lp.poly([(cx - 4, 0), (cx + 4, 0), (cx + 14, H - 30), (cx - 14, H - 30)], (200, 255, 236, 40))
        im.alpha_composite(lp.im)
    # hair behind her
    for i in range(18):
        u = i / 17
        x = cx - 10 + u * 20
        wave_line(p, x, top + 2, sh + 22 + 8 * math.sin(u * math.pi) + R.uniform(-3, 3), 1.6, TAU * t + u * 4, R.choice(("#2a1e18", "#3a2a20", "#4a3628")), 0.15, 2)
    # her body to the fire: a pale dress, folds, a dark sash
    p.poly([(cx - 11, sh), (cx + 11, sh), (cx + 17, H - 8), (cx - 17, H - 8)], "#bccad6")
    p.poly([(cx + 3, sh), (cx + 11, sh), (cx + 17, H - 8), (cx + 5, H - 8)], "#96a8b6")
    for k in (-10, -4, 2, 8):
        p.line([(cx + k * 0.5, waist), (cx + k * 1.4, H - 10)], "#a8b8c6" if k < 0 else "#8496a4", 1)
    p.poly([(cx - 9, sh), (cx, sh + 7), (cx + 9, sh)], "#a8b8c6")
    p.line([(cx - 12, waist), (cx + 12, waist)], "#4a3a5a", 2)
    # the hair over her shoulders, both sides of the face
    for i in range(10):
        side = -1 if i < 5 else 1
        x = cx + side * (6 + (i % 5) * 1.2)
        wave_line(p, x, top + 4, sh + 14 + (i % 5) * 2, 1.2, TAU * t + i, R.choice(("#2a1e18", "#3a2a20")), 0.2, 2)
    # arms: hands raised palm to palm (phase 1); thrown wide (phase 2); shackles and chains
    skin, skin2 = "#dccfc2", "#b8a898"
    chain = []
    if ph:
        for side in (-1, 1):
            el = (cx + side * 23, sh + 2)
            wr = (cx + side * 37, sh - 15 + side * 2 * math.sin(TAU * t))
            limb(p, [(cx + side * 10, sh + 3), el], 6, 5, "#bccad6" if side < 0 else "#96a8b6")
            for j in range(3):
                p.line([(el[0] + side * j * 2, el[1] + 2), (el[0] + side * j * 2, el[1] + 6 + j)], "#a8b8c6", 1)
            limb(p, [el, wr], 4, 3, skin)
            p.ell(wr[0], wr[1] - 2, 2.5, 3.5, skin)
            for f in range(4):
                a = -math.pi / 2 + side * (f - 1.5) * 0.25
                p.line([(wr[0], wr[1] - 3), (wr[0] + math.cos(a) * 5, wr[1] - 3 + math.sin(a) * 5)], skin, 1)
            cuff = (wr[0] - side * 3, wr[1] + 2)
            chain.append((cuff, (cuff[0] + side * 6 + 6 * math.sin(TAU * t + side), H - 22)))
    else:
        for side in (-1, 1):
            el = (cx + side * 16, sh + 12)
            wr = (cx + side * 2.5, sh - 6)
            limb(p, [(cx + side * 10, sh + 3), el], 6, 5, "#bccad6" if side < 0 else "#96a8b6")
            limb(p, [el, wr], 4, 3, skin)
            cuff = ((el[0] + wr[0]) / 2 + side, (el[1] + wr[1]) / 2 + 2)
            chain.append((cuff, (el[0] + side * 5 + 2 * math.sin(TAU * t + side), H - 24)))
        p.poly([(cx - 3, sh - 4), (cx, sh - 15), (cx + 3, sh - 4)], skin)
        p.line([(cx, sh - 14), (cx, sh - 4)], skin2, 1)
    for a, b in chain:  # the shackles, the links
        p.ell(a[0], a[1], 3.5, 2.5, "#5a5a64"); p.ell(a[0], a[1] - 0.5, 2.5, 1.5, "#8a8a94")
        n = 11
        for j in range(n):
            u = j / (n - 1)
            x = a[0] + (b[0] - a[0]) * u + 3 * math.sin(u * math.pi) * (1 if b[0] > a[0] else -1)
            y = a[1] + (b[1] - a[1]) * u
            if j % 2:
                p.ell(x, y, 1.5, 2.6, "#8a8a92"); p.px(x, y, "#2a2a30")
            else:
                p.ell(x, y, 2.6, 1.5, "#6a6a72"); p.px(x, y, "#2a2a30"); p.px(x - 1, y - 1, "#b8b8c0")
    # the face: pale, eyes turned up, tears; parted hair
    hx, hy = cx, top + 10
    p.ell(hx, hy, 7, 9, skin)
    p.ell(hx + 3, hy + 1, 3.5, 7, skin2)
    p.ell(hx, hy - 6, 8, 4, "#2a1e18")
    p.line([(hx, hy - 9), (hx, hy - 4)], "#4a3628", 1)
    p.line([(hx - 5, hy - 3), (hx - 2, hy - 4)], "#3a2a20", 1); p.line([(hx + 2, hy - 4), (hx + 5, hy - 3)], "#3a2a20", 1)
    p.px(hx - 1, hy + 2, "#c8b4a4")
    p.line([(hx - 2, hy + 5), (hx + 2, hy + 5)], "#8a5a5a", 1)
    tear = (t * 2) % 1
    for ex in (hx - 3, hx + 3):
        p.px(ex, hy + 1 + tear * 5, "#bfefff")
    im.alpha_composite(p.im)
    outline(im)
    # the fire she stands in, over her lower half; embers and smoke
    fire = [rgb(c) for c in FIRE]
    fb = H - 2
    for k, x in enumerate(range(12, W - 6, 13)):
        hgt = (44 if ph else 32) + 10 * math.sin(k * 1.7) + (12 if abs(x - cx) < 20 else 0)
        flame(im, x, fb, 19, hgt, t, fire, seed=k + 1, lean=2 * math.sin(TAU * t + k))
    embers(im, 53, 10, W - 10, H - 30, 80, t, ["#ffc83a", "#ff8a1a", "#fff2b0"], 20)
    eyes(im, [(hx - 3, hy - 1), (hx + 3, hy - 1)], "#8affd8", 2.8 if ph else 2.0, "#e8fff8", 0.75 if ph else 0.5)
    return im


BOSSES = {"silbon": silbon, "mohan": mohan, "madremonte": madremonte, "bolafuego": bolafuego, "llorona": llorona, "mandingas": mandingas,
          "griton": griton, "muelona": muelona, "hombrecaiman": hombrecaiman, "riviel": riviel, "patasola": patasola, "tunda": tunda,
          "bracamonte": bracamonte, "sayona": sayona, "curasincabeza": curasincabeza, "manopeluda": manopeluda, "candileja": candileja, "anima": anima}


def build(ids):
    os.makedirs(OUT, exist_ok=True)
    meta_path = os.path.join(OUT, "bosses.json")
    meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
    for bid in ids:
        frames = [[BOSSES[bid](i / N, ph) for i in range(N)] for ph in (0, 1)]
        w, h = frames[0][0].size
        sheet = Image.new("RGBA", (w * N, h * 2))
        for ph in (0, 1):
            for i, f in enumerate(frames[ph]):
                sheet.paste(f, (i * w, ph * h))
        sheet.save(os.path.join(OUT, f"{bid}.png"), optimize=True)
        meta[bid] = [w, h, N]
        print(bid, w, h)
    json.dump(meta, open(meta_path, "w"), separators=(",", ":"))


if __name__ == "__main__":
    build(sys.argv[1:] or list(BOSSES))
