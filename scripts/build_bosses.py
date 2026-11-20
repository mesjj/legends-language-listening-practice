"""The six bosses, drawn in code: original pixel art, no outside files.

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


BOSSES = {"silbon": silbon, "mohan": mohan, "madremonte": madremonte, "bolafuego": bolafuego, "llorona": llorona, "mandingas": mandingas}


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
