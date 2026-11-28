"""Eighteen more bosses (three more per zone, 2026-11-27), drawn in code like the first eighteen in
build_bosses.py, whose canvas and helpers they use: original pixel art, N frames of an idle loop in two rows
(row 1 is the second phase). They all face left, toward you.

build_bosses.py merges these into its BOSSES, so `.venv/bin/python scripts/build_bosses.py <id>` builds one.
usage: .venv/bin/python scripts/build_bosses_more.py [id ...] [--sheet out.png]   (no ids: all eighteen)
"""
import math
import random
import sys

from PIL import Image, ImageDraw

from build_bosses import (N, TAU, Pic, arcs, embers, eyes, fade_down, flame, fog, glow, limb, outline, rgb, shade, shear,
                          wave_line)

FIRE = [rgb(c) for c in ("#7a1a08", "#c0380c", "#f07a1a", "#ffc040", "#fff4c0")]
BLUEFIRE = [rgb(c) for c in ("#1a2a7a", "#2a5ac0", "#4aa0f0", "#a0e0ff", "#f0fcff")]


def rot(pts, cx, cy, a):
    c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def river(im, water, t, wc=(24, 54, 58), seed=3, ripple=("#5f9c98", "#8fc8c0")):
    """Everything below `water` sinks into a river; ripples drift."""
    R = random.Random(seed)
    W, H = im.size
    q = im.load()
    for y in range(water, H):
        d = (y - water) / max(1, H - water)
        for x in range(W):
            r_, g_, b_, a_ = q[x, y]
            if a_:
                k = 0.55 + 0.4 * d
                q[x, y] = (round(r_ + (wc[0] - r_) * k), round(g_ + (wc[1] - g_) * k), round(b_ + (wc[2] - b_) * k), 255)
            elif 6 < x < W - 6:
                edge = min(x - 6, W - 6 - x) / 22
                if R.random() < min(1, edge) * (1 - d * 0.6):
                    q[x, y] = (*wc, 200)
    pd = ImageDraw.Draw(im)
    for k in range(3):
        y = water + 2 + k * 4
        if y >= H:
            break
        off = (t * 12 + k * 7) % 12
        for x0 in range(int(8 + off), W - 10, 12):
            if q[min(W - 1, x0), y][3]:
                pd.line((x0, y, x0 + 4 + k % 2, y), fill=rgb(ripple[k % 2]))


def ground(p, W, g, col, col2, seed=1):
    """A low mound of earth under the feet."""
    R = random.Random(seed)
    p.ell(W / 2, g + 1, W / 2 - 6, 4, col)
    for _ in range(14):
        x = R.uniform(12, W - 12)
        p.line([(x, g + R.choice((0, 1, 2))), (x + R.uniform(2, 5), g + R.choice((0, 1, 2)))], col2, 1)


def falling(im, seed, x0, x1, y0, y1, t, cols, n=16, drift=4):
    """Particles falling (snow, leaves, sparks), each on its own loop."""
    R = random.Random(seed)
    for _ in range(n):
        ph, x = R.random(), R.uniform(x0, x1)
        u = (t + ph) % 1
        px_, py = x + drift * math.sin(TAU * (u + ph)), y0 + u * (y1 - y0)
        x_, y_ = round(px_), round(py)
        if 0 <= x_ < im.width and 0 <= y_ < im.height:
            im.putpixel((x_, y_), rgb(R.choice(cols)))


def hooves(p, x, y, col="#0c0a0c"):
    p.poly([(x - 3, y - 3), (x + 3, y - 3), (x + 4, y), (x - 4, y)], col)


def antler(p, x, y, ang, L, depth, col, w, tips):
    x2, y2 = x + math.cos(ang) * L, y + math.sin(ang) * L
    p.line([(x, y), (x2, y2)], col, w)
    if depth:
        antler(p, x2, y2, ang - 0.5, L * 0.72, depth - 1, col, max(1, w - 1), tips)
        antler(p, x2, y2, ang + 0.4, L * 0.6, depth - 1, col, max(1, w - 1), tips)
    else:
        tips.append((x2, y2))


# ---------------------------------------------------------------- El Venado Negro (páramo)
# A black stag standing in the fog, a crown of antlers like dead branches, two embers for eyes. Second phase:
# the antlers catch fire and the embers blaze.
def venadonegro(t, ph):
    W, H = 132, 148
    p = Pic(W, H)
    g = H - 4
    b = math.sin(TAU * t)
    fur, fur2, fur3 = "#17151b", "#0e0d11", "#2a2630"
    by = g - 52 + round(b * 0.8)
    # far legs
    for x in (60, 96):
        limb(p, [(x, by + 8), (x + 2, g - 24), (x - 1, g - 2)], 6, 3, fur2)
        hooves(p, x - 1, g)
    p.poly([(100, by - 6), (114, by - 2), (110, by + 4)], fur)  # the tail
    p.ell(80, by, 32, 17, fur)
    p.ell(84, by - 6, 22, 8, fur3)
    p.ell(80, by + 10, 24, 5, fur2)
    for x in (52, 90):
        limb(p, [(x, by + 8), (x + 3, g - 24), (x, g - 2)], 7, 3, fur)
        hooves(p, x, g)
    # the neck reaching up and forward, the head
    hx, hy = 30, g - 100 + round(b)
    p.poly([(54, by - 10), (62, by + 6), (40, hy + 14), (32, hy + 4)], fur)
    p.poly([(48, by - 6), (56, by + 2), (40, hy + 16), (36, hy + 10)], fur2)
    p.ell(hx, hy, 10, 8, fur)
    p.poly([(hx - 4, hy - 4), (hx - 18, hy + 3), (hx - 17, hy + 8), (hx - 2, hy + 7)], fur)
    p.ell(hx - 17, hy + 5, 2.5, 2, "#050406")
    for s in (-1, 1):  # ears
        p.poly([(hx + 4, hy - 5), (hx + 12 + s * 2, hy - 12 + s * 3), (hx + 8, hy - 2)], fur3)
    tips = []
    for a0, L in ((-2.1, 16), (-1.3, 18)):
        antler(p, hx + 2, hy - 7, a0, L, 3, "#2a2228" if not ph else "#3a2418", 3, tips)
    im = p.im
    outline(im)
    fog(im, g - 18, g + 3, t, (190, 200, 210), 140, seed=4)
    if ph:
        for i, (x, y) in enumerate(tips):
            flame(im, x, y + 1, 4, 7 + 2 * math.sin(TAU * t + i), t, FIRE, seed=i)
        embers(im, 5, 10, 70, g - 120, 30, t, ("#ffc040", "#f07a1a"), 10)
    # breath in the cold
    for k in range(3):
        u = (t + k / 3) % 1
        x, y = hx - 20 - u * 14, hy + 6 - u * 4
        glow(im, x, y, "#d0d8e0", 2 + u * 2, 0.35 * (1 - u))
    eyes(im, [(hx - 3, hy - 2)], "#ff4a1a", 4.2 if ph else 3.2, "#fff0a0", 0.8)
    return im


# ---------------------------------------------------------------- El Cóndor de Hielo (páramo)
# A condor as wide as the sky, ice on its feathers, a white ruff, a pale bald head. Its wings beat slowly.
# Second phase: icicles hang from its wings and snow falls round it.
def condorhielo(t, ph):
    W, H = 156, 132
    p = Pic(W, H)
    f = math.sin(TAU * t)
    cx, cy = 80, 70 + round(f * 2)
    dark, mid, white = "#20303e", "#3a5068", "#d8f0ff"
    tips = []
    for side in (1, -1):  # the far wing first
        sx = cx + side * 8
        tip = (cx + side * 72, cy - 34 + f * 22)
        midp = (cx + side * 40, cy - 24 + f * 12)
        low = (cx + side * 44, cy + 6 + f * 8)
        col = dark if side > 0 else mid
        p.poly([(sx, cy - 12), midp, tip, (tip[0] - side * 4, tip[1] + 8), low, (sx, cy + 10)], col)
        for k in range(5):  # the primaries: fingers at the tip
            a = math.atan2(tip[1] - midp[1], tip[0] - midp[0]) + (k - 2) * 0.16
            x0 = tip[0] - side * (4 + k * 3)
            y0 = tip[1] + 2 + k * 2
            p.line([(x0, y0), (x0 + math.cos(a) * 10, y0 + math.sin(a) * 10 + k)], col, 2)
        p.poly([(midp[0], midp[1] + 8), (tip[0] - side * 10, tip[1] + 10), (low[0], low[1] - 2)], white if side < 0 else "#9ab8cc")
        tips.append((low, tip))
    p.poly([(cx + 4, cy + 18), (cx + 22, cy + 40), (cx + 4, cy + 36)], dark)  # the tail
    p.ell(cx, cy, 15, 23, dark)
    p.ell(cx - 3, cy + 4, 9, 16, mid)
    for lx in (cx - 6, cx + 4):  # legs and talons
        p.line([(lx, cy + 20), (lx - 1, cy + 34)], "#8a9aa8", 3)
        for d in (-4, 0, 4):
            p.line([(lx - 1, cy + 34), (lx - 1 + d, cy + 38)], "#c8d8e8", 1)
    # the ruff, the neck and the head
    p.ell(cx - 6, cy - 22, 12, 6, white)
    for k in range(7):
        p.ell(cx - 16 + k * 3.5, cy - 19, 2.5, 3, "#f4fcff")
    hx, hy = cx - 22, cy - 36
    limb(p, [(cx - 8, cy - 24), (hx + 4, hy + 6)], 6, 5, "#a8b8c8")
    p.ell(hx, hy, 7, 6, "#c0d0dc")
    p.poly([(hx - 5, hy - 2), (hx - 14, hy + 1), (hx - 13, hy + 5), (hx - 9, hy + 6), (hx - 4, hy + 3)], "#e8eef0")
    p.px(hx - 13, hy + 5, "#5a6a78")
    p.poly([(hx - 3, hy - 6), (hx + 3, hy - 8), (hx + 1, hy - 4)], "#8aa0b0")  # the comb, iced
    im = p.im
    outline(im)
    if ph:
        q = ImageDraw.Draw(im)
        for low, tip in tips:
            for k in range(6):
                u = k / 5
                x = low[0] + (tip[0] - low[0]) * u * 0.8
                y = low[1] + (tip[1] - low[1]) * u * 0.8 + 2
                L = 5 + (k % 3) * 3
                q.polygon([(x - 1.5, y), (x + 1.5, y), (x, y + L)], fill=rgb("#c8f0ff"))
        falling(im, 9, 4, W - 4, 0, H, t, ("#ffffff", "#e0f4ff"), 26, 5)
    else:
        falling(im, 9, 4, W - 4, 0, H, t, ("#ffffff",), 8, 5)
    eyes(im, [(hx - 2, hy - 1)], "#5ad8ff", 3.6 if ph else 2.6, "#ffffff", 0.8)
    return im


# ---------------------------------------------------------------- El Arriero Fantasma (páramo)
# A muleteer of the old roads, see-through: a ruana, a wide cane hat, a whip, a hand held out for the toll;
# behind him the ghost of his mule with its load. Second phase: the whip cracks and more mules come out of the fog.
def arrierofantasma(t, ph):
    W, H = 144, 150
    p = Pic(W, H)
    g = H - 4
    b = math.sin(TAU * t)
    ghost, ghost2, pale = "#9aac9a", "#7a8a7a", "#d8e4cc"
    if ph:  # more mules in the fog, further back
        for k, x in enumerate((112, 128)):
            y = g - 44 - k * 6
            p.ell(x, y, 14, 8, "#5a685a")
            p.poly([(x - 12, y - 4), (x - 20, y - 16), (x - 16, y - 18), (x - 8, y - 8)], "#5a685a")
            p.poly([(x - 18, y - 18), (x - 20, y - 26), (x - 16, y - 20)], "#5a685a")
    # the mule behind him, with its load
    mx, my = 100, g - 40 + round(b * 0.6)
    for x in (88, 112):
        limb(p, [(x, my + 6), (x, g - 2)], 5, 3, ghost2)
    p.ell(mx, my, 22, 12, ghost2)
    p.rect(mx - 14, my - 22, mx + 10, my - 8, "#8a8670")
    p.rect(mx - 12, my - 30, mx + 6, my - 22, "#9a9478")
    p.line([(mx - 14, my - 15), (mx + 10, my - 15)], "#5a5444", 1)
    p.poly([(mx - 18, my - 6), (mx - 32, my - 22), (mx - 26, my - 26), (mx - 14, my - 12)], ghost2)
    p.ell(mx - 32, my - 22, 6, 4, ghost2)
    for e in (-1, 1):
        p.poly([(mx - 28 + e * 2, my - 26), (mx - 30 + e * 3, my - 36), (mx - 26 + e * 2, my - 28)], ghost2)
    for x in (94, 108):
        limb(p, [(x, my + 6), (x - 1, g - 2)], 5, 3, ghost)
        hooves(p, x - 1, g, "#3a4a3a")
    # the man: legs, the ruana, the hat
    cx, hip = 52, g - 40
    for lx, fx in ((cx - 5, cx - 9), (cx + 5, cx + 6)):
        limb(p, [(lx, hip), (fx, g - 2)], 6, 4, "#6a786a")
        p.rect(fx - 4, g - 3, fx + 3, g, "#4a564a")
    sh = hip - 34
    ruana = [(cx - 22, hip + 2), (cx - 10, sh - 2), (cx + 10, sh - 2), (cx + 22, hip + 2)]
    p.poly(ruana, ghost)
    for k in range(3):
        y = hip - 6 - k * 9
        p.line([(cx - 19 + k * 3, y), (cx + 19 - k * 3, y)], "#c8a888", 1)
    for x in range(cx - 21, cx + 22, 3):
        p.line([(x, hip + 2), (x, hip + 6)], ghost2, 1)
    # the arm holding out a hand for the toll (left), the whip (right)
    hand = (cx - 30, sh + 18 + round(b))
    limb(p, [(cx - 12, sh + 6), (cx - 22, sh + 16), hand], 5, 4, ghost)
    p.ell(hand[0] - 2, hand[1], 3.5, 2, pale)
    if not ph:
        whip = [(cx + 18, sh + 14), (cx + 26, sh + 26), (cx + 30 + 3 * b, g - 14), (cx + 22 + 4 * b, g - 4)]
    else:  # cracking out in front of him
        u = (t * 2) % 1
        whip = [(cx + 18, sh + 14), (cx + 12, sh - 12), (cx - 10 + 20 * u, sh - 22 - 6 * math.sin(TAU * u)), (cx - 34 + 24 * u, sh - 8)]
    limb(p, [(cx + 12, sh + 6), (cx + 18, sh + 14)], 5, 4, ghost)
    p.line(whip, "#4a3a2a", 1)
    p.line([(cx + 18, sh + 14), (cx + 18, sh + 4)], "#5a4a3a", 2)
    # the head: gaunt, a beard of fog, the hat
    hx, hy = cx - 2, sh - 9
    p.ell(hx, hy, 6, 7, pale)
    p.poly([(hx - 5, hy + 3), (hx + 5, hy + 3), (hx, hy + 11)], "#b8c8b0")
    p.ell(hx - 2.5, hy - 1, 1.8, 2, "#1a221a")
    p.ell(hx + 2.5, hy - 1, 1.8, 2, "#1a221a")
    by = hy - 6
    p.poly([(hx - 20, by + 4), (hx - 10, by), (hx + 10, by), (hx + 20, by + 4), (hx + 10, by + 3), (hx - 10, by + 3)], "#c8c0a0")
    p.poly([(hx - 8, by + 1), (hx - 7, by - 10), (hx + 7, by - 10), (hx + 8, by + 1)], "#d8d0b0")
    p.rect(hx - 8, by - 3, hx + 8, by - 1, "#2a221a")
    im = p.im
    outline(im, (20, 28, 22, 255))
    q = im.load()
    for y in range(H):  # see-through
        for x in range(W):
            r_, g_, b_, a_ = q[x, y]
            if a_:
                q[x, y] = (r_, g_, b_, min(a_, 205))
    fade_down(im, g - 16, g + 2)
    fog(im, g - 22, g + 4, t, (200, 214, 200), 150, seed=6)
    eyes(im, [(hx - 2.5, hy - 1), (hx + 2.5, hy - 1)], "#f0e060", 2.6 if ph else 2, "#ffffe0", 0.7)
    return im


# ---------------------------------------------------------------- La Mohana (ciénaga)
# A woman on a rock in the river combing her hair with a gold comb; her hair runs down the rock and into the
# water, and on along the water toward you. Second phase: she slides into the river and her hair rises round her.
def mohana(t, ph):
    W, H = 140, 140
    p = Pic(W, H)
    water = H - 22
    R = random.Random(12)
    b = math.sin(TAU * t)
    skin, skin2 = "#8a5a3e", "#6a4430"
    hair = ["#14201e", "#1c2c28", "#24383a", "#0e1614", "#2e4a44"]
    rx, ry = 84, water - 2
    p.ell(rx, ry, 36, 16, "#4a4a46")
    p.ell(rx - 6, ry - 6, 26, 10, "#5a5a54")
    p.ell(rx + 10, ry - 2, 14, 6, "#3e3e3a")
    sink = 18 if ph else 0
    cx, hip = 82, ry - 12 + sink
    # hair falling behind her, down the rock, into the water
    for i in range(70):
        x0 = cx - 4 + R.uniform(-6, 10)
        y0 = hip - 44 + R.uniform(0, 8)
        L = R.uniform(40, 70)
        wave_line(p, x0 + R.uniform(0, 14), y0, min(water + 8, y0 + L), 2, TAU * t + R.uniform(0, TAU), R.choice(hair), 0.15, 2 if i % 4 == 0 else 1)
    # the skirt of white cloth on the rock, the body
    p.poly([(cx - 20, hip + 4), (cx + 18, hip + 4), (cx + 12, hip - 10), (cx - 10, hip - 10)], "#d8d0c0")
    p.poly([(cx - 22, hip + 4), (cx - 30, hip + 8), (cx - 26, hip + 12), (cx - 16, hip + 6)], skin)  # a foot toward the water
    p.poly([(cx - 9, hip - 10), (cx + 9, hip - 10), (cx + 7, hip - 32), (cx - 7, hip - 32)], skin)
    p.poly([(cx - 9, hip - 18), (cx + 9, hip - 18), (cx + 8, hip - 24), (cx - 8, hip - 24)], "#e8e0d0")
    # the face turned toward you, the hair over one side
    hx, hy = cx - 4, hip - 40
    limb(p, [(cx - 1, hip - 32), (hx, hy + 4)], 4, 4, skin)
    p.ell(hx, hy, 6, 7, skin)
    p.ell(hx + 3, hy, 4, 7, skin2)
    p.ell(hx + 2, hy - 5, 8, 5, hair[0])
    for k in range(9):
        wave_line(p, hx - 2 + k * 1.4, hy - 6, hy + 14 + k, 1.2, TAU * t + k, R.choice(hair), 0.3)
    # the arm raised with the gold comb, moving down through the hair
    u = (t * 1.0) % 1
    comb = (hx + 9, hy - 6 + u * 22)
    limb(p, [(cx + 6, hip - 30), (cx + 14, hip - 40), comb], 4, 3, skin)
    p.rect(comb[0] - 1, comb[1] - 3, comb[0] + 4, comb[1] + 1, "#e8b830")
    for k in range(3):
        p.px(comb[0] + k * 2 - 1, comb[1] + 2, "#ffe070")
    # the other hand trailing in the water
    limb(p, [(cx - 7, hip - 28), (cx - 18, hip - 14), (cx - 24, water + 1)], 4, 3, skin)
    # hair along the water toward you
    for i in range(16):
        y = water + 2 + (i % 5) * 2
        x0 = cx - 26
        pts = [(x0 - k * 6, y + 1.5 * math.sin(TAU * t + i + k * 0.7)) for k in range(int(6 + i % 5))]
        p.line(pts, R.choice(hair), 1)
    if ph:  # tendrils of hair rising out of the river
        for i in range(5):
            x = 14 + i * 20
            pts = [(x + 4 * math.sin(TAU * t + i + k * 0.5), water + 4 - k * 6) for k in range(8)]
            p.line(pts, hair[i % 5], 3)
            p.line(pts, hair[(i + 2) % 5], 1)
    im = p.im
    outline(im)
    river(im, water, t, (20, 52, 54), seed=12)
    eyes(im, [(hx - 2.5, hy - 1)], "#5affd0", 3.4 if ph else 2.2, "#e8fff8", 0.7 if ph else 0.5)
    glow(im, comb[0] + 1, comb[1] - 1, "#ffd040", 3, 0.5)
    return im


# ---------------------------------------------------------------- El Bufeo Encantado (ciénaga)
# A man in a white suit and a white hat, dancing at the river's edge. Second phase: the hat comes off, and the
# head under it is a pink river dolphin's, a fountain of spray from the hole on top.
def bufeoencantado(t, ph):
    W, H = 116, 156
    p = Pic(W, H)
    g = H - 10
    s = math.sin(TAU * t)
    s2 = math.sin(TAU * t * 2)
    suit, suit2, pink = "#f0ece4", "#c8c0b4", "#f0a0b8"
    cx, hip = 56, g - 46 + round(abs(s2) * -2)
    # legs: a step to each side in turn
    for side, lift in ((-1, max(0, s)), (1, max(0, -s))):
        knee = (cx + side * 8, hip + 22 - lift * 6)
        foot = (cx + side * 12 + side * lift * 4, g - 2 - lift * 8)
        limb(p, [(cx + side * 4, hip), knee, foot], 7, 5, suit if side < 0 else suit2)
        p.poly([(foot[0] - 6, foot[1] - 1), (foot[0] + 3, foot[1] - 2), (foot[0] + 4, foot[1] + 2), (foot[0] - 6, foot[1] + 2)], "#2a2018")
    sh = hip - 36
    p.poly([(cx - 13, hip + 4), (cx - 14, sh + 2), (cx + 14, sh + 2), (cx + 13, hip + 4)], suit)
    p.poly([(cx + 2, sh + 2), (cx + 14, sh + 2), (cx + 13, hip + 4), (cx + 4, hip + 4)], suit2)
    p.poly([(cx - 4, sh + 2), (cx + 4, sh + 2), (cx, sh + 14)], pink)  # the shirt
    p.line([(cx, sh + 4), (cx, sh + 12)], "#c04070", 1)
    p.px(cx - 6, hip - 12, "#b8b0a4"); p.px(cx - 6, hip - 6, "#b8b0a4")
    # arms: one held out to ask you to dance, one on the hip, swaying
    hand = (cx - 30, sh + 6 + round(s * 3))
    limb(p, [(cx - 12, sh + 4), (cx - 22, sh + 8), hand], 6, 5, suit)
    p.ell(hand[0] - 2, hand[1], 3, 2.5, "#9a6a4a")
    limb(p, [(cx + 12, sh + 4), (cx + 20, sh + 16), (cx + 12, hip - 6)], 6, 5, suit2)
    hx, hy = cx - 2, sh - 10
    if not ph:
        limb(p, [(cx, sh + 2), (hx, hy + 4)], 4, 4, "#9a6a4a")
        p.ell(hx, hy, 7, 7.5, "#9a6a4a")
        p.ell(hx + 3, hy + 1, 4, 6, "#7a5038")
        p.line([(hx - 4, hy + 4), (hx + 1, hy + 5)], "#e8e0d0", 1)  # a smile
        hat_y = hy - 6
    else:  # the dolphin's head: a long beak, a round melon, a small eye
        hy -= 2
        limb(p, [(cx, sh + 2), (hx, hy + 4)], 6, 6, pink)
        p.ell(hx + 1, hy - 1, 9, 9, pink)
        p.ell(hx - 2, hy - 4, 7, 6, "#f8c0d0")
        p.poly([(hx - 6, hy + 1), (hx - 26, hy + 5), (hx - 27, hy + 8), (hx - 5, hy + 7)], pink)
        p.line([(hx - 24, hy + 7), (hx - 6, hy + 6)], "#c06080", 1)
        hat_y = hy - 24 - abs(s) * 6  # the hat floats off
        for k in range(5):  # spray
            u = (t * 2 + k / 5) % 1
            p.px(hx + 2 + (k - 2) * 3 * u, hy - 10 - u * 14 + u * u * 10, "#c8ecff")
    tilt = 0.12 * s
    brim = rot([(hx - 18, hat_y + 3), (hx - 10, hat_y), (hx + 10, hat_y), (hx + 18, hat_y + 3), (hx + 10, hat_y + 3), (hx - 10, hat_y + 3)], hx, hat_y, tilt)
    crown = rot([(hx - 8, hat_y + 1), (hx - 7, hat_y - 9), (hx, hat_y - 11), (hx + 7, hat_y - 9), (hx + 8, hat_y + 1)], hx, hat_y, tilt)
    band = rot([(hx - 8, hat_y - 3), (hx + 8, hat_y - 3), (hx + 8, hat_y - 1), (hx - 8, hat_y - 1)], hx, hat_y, tilt)
    p.poly(brim, "#f8f6f0")
    p.poly(crown, "#ffffff")
    p.poly(band, "#1a1a1a")
    im = p.im
    outline(im)
    river(im, g - 2, t, (30, 64, 72), seed=15)
    if ph:
        eyes(im, [(hx - 3, hy - 1)], "#ff7ab0", 2.6, "#ffffff", 0.7)
    return im


# ---------------------------------------------------------------- La Tarumama (ciénaga)
# A bent old woman on the muddy bank, hair like dry moss, a shawl, a cane, her feet on backwards (toes behind).
# Second phase: she screams, mud flying, the scream going out in rings.
def tarumama(t, ph):
    W, H = 128, 146
    p = Pic(W, H)
    g = H - 6
    b = math.sin(TAU * t)
    R = random.Random(21)
    ground(p, W, g, "#4a3a26", "#6a5236", 21)
    for k in range(7):  # reeds
        x = 92 + k * 4
        p.line([(x, g), (x + 2 * math.sin(TAU * t + k), g - 24 - (k % 3) * 8)], "#5a7a3a", 1)
    cx, hip = 66, g - 40
    # the skirt and the backward feet (toes pointing back, to the right)
    for fx in (cx - 6, cx + 6):
        p.poly([(fx - 3, g - 4), (fx + 10, g - 3), (fx + 10, g), (fx - 4, g)], "#6a4a34")
        for k in range(3):
            p.px(fx + 10, g - 2 + k, "#3a2a1a")
    p.poly([(cx - 18, g - 4), (cx + 16, g - 4), (cx + 10, hip - 4), (cx - 12, hip - 4)], "#3a4a3a")
    for x in range(cx - 16, cx + 16, 4):
        p.line([(x, g - 4), (x + 2, g - 1)], "#2a362a", 1)
    # hunched back under the shawl
    sh = hip - 22
    p.ell(cx + 4, sh + 6, 20, 16, "#6a6a3a")
    p.poly([(cx - 16, sh + 8), (cx + 22, sh + 4), (cx + 18, hip + 4), (cx - 14, hip + 2)], "#5a5a2e")
    for k in range(4):
        p.line([(cx - 12 + k * 8, hip + 2), (cx - 10 + k * 8, hip + 7)], "#4a4a24", 1)
    # the cane
    cane = (cx - 28, g)
    p.line([(cx - 24, sh + 12), cane], "#4a3420", 2)
    limb(p, [(cx - 8, sh + 8), (cx - 18, sh + 14), (cx - 24, sh + 12)], 4, 3, "#7a5a40")
    # the head thrust forward, the hair
    hx, hy = cx - 14, sh - 2 + round(b)
    p.ell(hx, hy, 8, 8, "#7a5a40")
    p.ell(hx - 1, hy + 2, 5, 5, "#6a4a34")
    p.poly([(hx - 7, hy + 1), (hx - 12, hy + 4), (hx - 7, hy + 5)], "#6a4a34")  # the nose
    if ph:
        p.ell(hx - 3, hy + 6, 4, 4, "#1a0a08")
        p.px(hx - 4, hy + 3, "#d8d0b0"); p.px(hx - 2, hy + 3, "#d8d0b0")
    else:
        p.line([(hx - 6, hy + 6), (hx - 1, hy + 7)], "#2a1a10", 1)
    for i in range(30):
        x0 = hx - 6 + R.uniform(0, 18)
        L = R.uniform(10, 26) + (8 if ph else 0)
        sway = (6 if ph else 2)
        wave_line(p, x0, hy - 8 + R.uniform(0, 4), hy - 8 + L, sway, TAU * t + R.uniform(0, TAU), R.choice(("#a8a090", "#8a8478", "#c8c0b0", "#6a6a5a")), 0.25)
    if ph:
        arcs(p, hx - 6, hy + 6, t, "#d8c8a0", n=3, r0=10, step=10, a0=145, a1=215)
    im = p.im
    outline(im)
    if ph:
        for k in range(8):  # mud flying
            u = (t + k / 8) % 1
            x = cx - 30 + k * 9 + (k % 2 * 2 - 1) * u * 12
            y = g - 4 - math.sin(math.pi * u) * 30
            for dx, dy in ((0, 0), (1, 0), (0, 1)):
                if 0 <= round(x + dx) < W and 0 <= round(y + dy) < H:
                    im.putpixel((round(x + dx), round(y + dy)), rgb("#5a4028"))
    eyes(im, [(hx - 4, hy - 1)], "#d8e060", 3 if ph else 2, "#ffffe0", 0.7)
    return im


# ---------------------------------------------------------------- El Pollo Maligno (selva)
# A huge dark chicken in the jungle, rust feathers, a blood-red comb, long sickle tail, yellow scaled legs and
# hooked talons. Second phase: it puffs up to twice its size, beak open.
def pollomaligno(t, ph):
    W, H = 144, 152
    p = Pic(W, H)
    g = H - 4
    b = math.sin(TAU * t)
    R = random.Random(30)
    k = 1.18 if ph else 1.0
    cx, cy = 78, g - 50 * k
    dark, rust, rust2 = "#24140e", "#7a2a14", "#a8441c"
    # tail: sickles of black-green
    for i in range(6):
        a = -0.6 - i * 0.22
        L = (44 - i * 3) * k
        pts = [(cx + 22, cy - 6), (cx + 22 + math.cos(a) * L * 0.6 + 6, cy - 6 + math.sin(a) * L * 0.8), (cx + 30 + math.cos(a + 0.9) * L * 0.4 + 14, cy + 8 + i * 3)]
        limb(p, pts, 5, 2, ("#142a24", "#1e3a32", "#0e1c18")[i % 3])
    # legs and talons
    for lx, d in ((cx - 10, -1), (cx + 8, 1)):
        top = (lx, cy + 22 * k)
        foot = (lx - 4, g - 2)
        limb(p, [top, foot], 7, 5, "#c8b050")
        for j in range(4):
            y = top[1] + 4 + j * 6
            p.line([(lx - 6 + j * -1, y), (lx + 2 + j * -1, y)], "#8a7a30", 1)
        for tx in (-12, -6, 0):
            p.line([(foot[0], foot[1]), (foot[0] + tx, g)], "#c8b050", 2)
            p.line([(foot[0] + tx, g), (foot[0] + tx - 2, g + 2)], "#f0e8d0", 1)
        p.line([(foot[0] + 2, foot[1]), (foot[0] + 8, g)], "#c8b050", 2)
    # the body
    p.ell(cx, cy, 34 * k, 28 * k, dark)
    p.ell(cx - 6, cy + 2, 26 * k, 22 * k, rust)
    for i in range(46):  # scale-like feathers, puffed up and ragged in phase 2
        x = cx + R.uniform(-28, 26) * k
        y = cy + R.uniform(-18, 22) * k
        rr = R.uniform(3, 5) * (1.3 if ph else 1)
        p.poly([(x - rr, y - 1), (x + rr, y - 1), (x, y + rr + (2 if ph else 0))], R.choice((rust2, rust, "#5a2010", dark)))
    # a wing folded on its side
    p.poly([(cx - 6, cy - 12 * k), (cx + 28 * k, cy - 4), (cx + 24 * k, cy + 18 * k), (cx, cy + 10)], "#3a1a10")
    for j in range(4):
        p.line([(cx + 4 + j * 6, cy + 4 + j * 2), (cx + 12 + j * 5, cy + 18 * k)], "#1a0c08", 1)
    # the neck and the head, bobbing
    hx, hy = cx - 30 * k + round(b * 2), cy - 38 * k + round(abs(b) * 2)
    p.poly([(cx - 24 * k, cy - 6), (cx - 4, cy - 20 * k), (hx + 8, hy + 2), (hx - 4, hy + 10)], rust2)
    for j in range(10):
        p.line([(hx - 2 + j * 2.4, hy + 6), (hx - 4 + j * 3, hy + 20 + j)], "#d0601c", 1)
    p.ell(hx, hy, 9, 8, rust2)
    for j in range(5):  # the comb
        p.ell(hx - 6 + j * 3.4, hy - 8 - (2 if j in (1, 2, 3) else 0), 3, 4, "#d01a1a")
    p.ell(hx - 8, hy + 8, 3, 5, "#c01414")  # the wattle
    if ph:
        p.poly([(hx - 7, hy - 1), (hx - 20, hy + 1), (hx - 8, hy + 2)], "#e0c040")
        p.poly([(hx - 7, hy + 3), (hx - 17, hy + 6), (hx - 7, hy + 5)], "#c0a030")
        p.ell(hx - 10, hy + 2.5, 3, 1.4, "#3a0808")
    else:
        p.poly([(hx - 7, hy - 1), (hx - 17, hy + 2), (hx - 7, hy + 4)], "#e0c040")
    im = p.im
    outline(im)
    falling(im, 31, 10, W - 10, 10, H, t, ("#a8441c", "#7a2a14"), 6, 6)
    eyes(im, [(hx - 2, hy - 2)], "#ff2a1a", 3.8 if ph else 2.8, "#ffe0a0", 0.8)
    return im


# ---------------------------------------------------------------- El Boraro (selva)
# A great hairy giant of the jungle: long ears hanging, a pot belly, arms to the knees, feet on backwards.
# Second phase: arms raised, a roar full of tusks.
def boraro(t, ph):
    W, H = 132, 164
    p = Pic(W, H)
    g = H - 4
    b = math.sin(TAU * t)
    R = random.Random(40)
    fur, fur2, fur3 = "#3a2a1e", "#2a1e14", "#5a4430"
    skin = "#8a6a50"
    cx, hip = 66, g - 46
    # legs, feet on backwards: heels toward you, toes behind
    for lx in (cx - 12, cx + 10):
        limb(p, [(lx, hip), (lx + 2, hip + 22), (lx, g - 4)], 14, 9, fur)
        p.poly([(lx - 6, g - 6), (lx + 16, g - 5), (lx + 18, g), (lx - 6, g)], skin)
        for k in range(4):
            p.line([(lx + 13 + k * 1.5, g - 4), (lx + 15 + k * 1.5, g)], "#4a3424", 1)
    sh = hip - 54
    p.poly([(cx - 30, sh + 6), (cx + 30, sh + 6), (cx + 26, hip + 6), (cx - 26, hip + 6)], fur)
    p.ell(cx - 2, hip - 16, 20, 18, skin)  # the belly
    p.ell(cx - 4, hip - 20, 12, 10, "#9a7a5a")
    p.px(cx - 3, hip - 12, "#4a3424")
    # arms
    for side in (-1, 1):
        s0 = (cx + side * 28, sh + 10)
        if ph:
            el = (cx + side * 40, sh - 4)
            hd = (cx + side * 38 + b * side, sh - 26)
        else:
            el = (cx + side * 40, sh + 34)
            hd = (cx + side * 36, hip + 22 + round(b * side * 2))
        limb(p, [s0, el, hd], 16, 10, fur if side < 0 else fur2)
        p.ell(hd[0], hd[1], 7, 6, skin)
        for f in (-4, 0, 4):
            p.line([(hd[0] + f, hd[1] + (3 if not ph else -3)), (hd[0] + f - 1, hd[1] + (8 if not ph else -8))], "#e8dcc0", 1)
    # the head, low between the shoulders, long ears
    hx, hy = cx - 4, sh - 6 + round(b)
    for side in (-1, 1):
        p.poly([(hx + side * 10, hy - 6), (hx + side * 24, hy + 8), (hx + side * 22, hy + 30), (hx + side * 14, hy + 6)], fur3)
        p.line([(hx + side * 14, hy), (hx + side * 20, hy + 22)], "#2a1a10", 1)
    p.ell(hx, hy, 14, 14, fur)
    p.ell(hx, hy + 4, 10, 8, skin)
    p.ell(hx - 1, hy + 2, 4, 3, "#5a4030")
    if ph:
        p.ell(hx, hy + 10, 7, 5, "#1a0806")
        for s in (-1, 1):
            p.poly([(hx + s * 5, hy + 14), (hx + s * 4, hy + 4), (hx + s * 3, hy + 14)], "#f0e8d0")
    else:
        p.line([(hx - 6, hy + 9), (hx + 6, hy + 9)], "#2a1a10", 1)
        for s in (-1, 1):
            p.poly([(hx + s * 5, hy + 9), (hx + s * 4, hy + 4), (hx + s * 3, hy + 9)], "#f0e8d0")
    for i in range(120):  # shaggy fur over everything
        x = R.uniform(cx - 34, cx + 34)
        y = R.uniform(sh - 18, hip + 6)
        if abs(x - (cx - 2)) < 18 and abs(y - (hip - 16)) < 16:
            continue
        if abs(x - hx) < 9 and hy - 2 < y < hy + 14:
            continue
        p.line([(x, y), (x + R.uniform(-1, 1) + math.sin(TAU * t + x) * 0.6, y + R.uniform(3, 6))], R.choice((fur2, fur3, "#4a3624")), 1)
    im = p.im
    outline(im)
    eyes(im, [(hx - 5, hy - 2), (hx + 5, hy - 2)], "#ff8a1a", 3.4 if ph else 2.6, "#fff0b0", 0.8)
    return im


# ---------------------------------------------------------------- El Hojarasquín (selva)
# A heap of dry leaves the shape of a man, twigs for horns, a beard of moss, two lights deep inside; leaves
# keep falling off him and growing back. Second phase: the leaves whirl round him.
def hojarasquin(t, ph):
    W, H = 136, 156
    p = Pic(W, H)
    g = H - 4
    R = random.Random(50)
    b = math.sin(TAU * t)
    leaves = ("#a85a1a", "#c8801e", "#8a3a14", "#d8a030", "#6a7a2a", "#5a3a1a", "#b8682a")
    cx = 68
    # the silhouette: a dark heap, wider at the base, a head, arms of branches
    body = [(cx - 34, g), (cx - 26, g - 50), (cx - 20, g - 86), (cx - 10, g - 104), (cx + 10, g - 104), (cx + 20, g - 86), (cx + 26, g - 50), (cx + 36, g)]
    p.poly(body, "#3a2a14")
    hx, hy = cx - 2, g - 114 + round(b)
    p.ell(hx, hy, 14, 13, "#3a2a14")
    for side in (-1, 1):  # twig horns
        tips = []
        antler(p, hx + side * 6, hy - 10, -math.pi / 2 - side * 0.6, 12, 2, "#5a3a1e", 2, tips)
        for x, y in tips:
            p.ell(x, y, 2.5, 1.6, R.choice(leaves))
    for side in (-1, 1):  # branch arms with leafy hands
        hand = (cx + side * 46, g - 50 + round(b * side * 3) - (24 if ph else 0))
        limb(p, [(cx + side * 18, g - 88), (cx + side * 36, g - 72), hand], 7, 3, "#5a3a1e")
        for j in range(5):
            a = (-0.8 + j * 0.4) + (0 if side > 0 else math.pi)
            p.line([hand, (hand[0] + math.cos(a) * 9, hand[1] + math.sin(a) * 9 + 3)], "#5a3a1e", 1)
            p.ell(hand[0] + math.cos(a) * 9, hand[1] + math.sin(a) * 9 + 3, 2.5, 1.5, R.choice(leaves))
    # leaves layered over the body
    for i in range(260):
        u = R.random()
        y = g - u * 106
        half = 34 - u * 22
        x = cx + R.uniform(-half, half)
        a = R.uniform(0, TAU)
        L = R.uniform(3, 5)
        pts = [(x + math.cos(a) * L, y + math.sin(a) * L), (x + math.cos(a + 1.8) * L * 0.4, y + math.sin(a + 1.8) * L * 0.4),
               (x - math.cos(a) * L, y - math.sin(a) * L), (x + math.cos(a - 1.8) * L * 0.4, y + math.sin(a - 1.8) * L * 0.4)]
        p.poly(pts, R.choice(leaves))
    for i in range(50):
        a = R.uniform(0, TAU)
        r = R.uniform(0, 12)
        x, y = hx + math.cos(a) * r, hy + math.sin(a) * r * 0.9
        p.ell(x, y, 3, 2, R.choice(leaves))
    # the face: a dark hollow, a moss beard
    p.ell(hx, hy + 1, 9, 6, "#140e08")
    for i in range(14):
        x = hx - 8 + i * 1.2
        wave_line(p, x, hy + 6, hy + 22 + (i % 4) * 4, 1.2, TAU * t + i, R.choice(("#4a6a2a", "#5a7a34", "#3a5a20")), 0.3)
    im = p.im
    outline(im)
    if ph:  # the whirlwind
        for i in range(36):
            a = TAU * (t + i / 36) + i
            r = 46 + (i % 5) * 6
            x = cx + math.cos(a) * r
            y = g - 30 - i * 2.4 + math.sin(a) * 8
            if 0 <= x < W - 2 and 0 <= y < H - 1:
                c = rgb(leaves[i % len(leaves)])
                im.putpixel((round(x), round(y)), c)
                im.putpixel((round(x) + 1, round(y)), c)
    falling(im, 51, cx - 30, cx + 30, g - 100, g, t, leaves, 10, 5)
    eyes(im, [(hx - 4, hy), (hx + 4, hy)], "#c8ff3a", 3.6 if ph else 2.8, "#f8ffd0", 0.8)
    return im


# ---------------------------------------------------------------- La Mula de Tres Patas (llano)
# A black mule with one front leg, galloping in threes, sparks from its hooves, fire in its eyes.
# Second phase: fire from its mouth and its mane alight.
def mulatrespatas(t, ph):
    W, H = 148, 132
    p = Pic(W, H)
    g = H - 4
    s = math.sin(TAU * t)
    c_ = math.cos(TAU * t)
    coat, coat2, coat3 = "#141216", "#0a090c", "#2a2630"
    bx, by = 82, g - 46 + round(abs(s) * -3)
    # the back legs (two), the single front leg in the middle of the chest
    for k, x in enumerate((96, 108)):
        sw = math.sin(TAU * t + k * 0.6)
        knee = (x + 4 + sw * 4, by + 22)
        foot = (x - 2 + sw * 12, g - 2 - max(0, -sw) * 8)
        limb(p, [(x, by + 6), knee, foot], 9, 4, coat2 if k == 0 else coat)
        hooves(p, foot[0], foot[1] + 2)
    p.poly([(112, by - 6), (126, by + 2 + s * 4), (128, by + 20 + s * 4), (118, by + 4)], coat2)  # the tail
    p.ell(bx, by, 32, 16, coat)
    p.ell(bx + 2, by - 6, 22, 6, coat3)
    fx = 60
    knee = (fx - 6 - c_ * 6, by + 22)
    foot = (fx - 4 - c_ * 14, g - 2 - max(0, c_) * 10)
    limb(p, [(fx, by + 4), knee, foot], 10, 4, coat)
    hooves(p, foot[0], foot[1] + 2)
    # neck and head, long ears
    hx, hy = 28, by - 30 + round(s * 2)
    p.poly([(56, by - 8), (66, by + 6), (38, hy + 12), (30, hy + 2)], coat)
    p.ell(hx, hy, 10, 8, coat)
    p.poly([(hx - 4, hy - 4), (hx - 20, hy + 4), (hx - 20, hy + 11), (hx - 2, hy + 8)], coat)
    p.ell(hx - 18, hy + 6, 2.5, 2, "#3a1a10")
    for e in (-1, 1):
        p.poly([(hx + 2 + e * 2, hy - 6), (hx + 8 + e * 5, hy - 22), (hx + 7 + e * 2, hy - 4)], coat3)
    im = p.im
    outline(im)
    if ph:
        for i in range(6):  # the mane alight
            x = 34 + i * 5
            y = hy - 2 + (by - 8 - hy) * i / 6
            flame(im, x + 4, y, 5, 9 + 2 * math.sin(TAU * t + i), t, FIRE, seed=i, lean=3)
        flame(im, hx - 30, hy + 8, 8, 18, t, FIRE, seed=9, lean=-10)
    for f, x in ((foot[0], foot[0]), (96, 96), (108, 108)):
        embers(im, int(x), x - 8, x + 8, g, 18, t, ("#ffc040", "#ff7a1a", "#fff4c0"), 6)
    eyes(im, [(hx - 4, hy - 2)], "#ff6a1a", 4 if ph else 3.2, "#fff0a0", 0.85)
    return im


# ---------------------------------------------------------------- Juan Machete (llano)
# A llanero in a white liqui-liqui and a wide dark hat, a long machete in his hand, a chest of gold at his feet.
# Second phase: the machete goes up, his eyes turn red and the shadow behind him grows horns.
def juanmachete(t, ph):
    W, H = 120, 156
    p = Pic(W, H)
    g = H - 4
    b = math.sin(TAU * t)
    cx, hip = 58, g - 48
    sh = hip - 38
    if ph:  # the shadow behind him, with horns
        p.ell(cx + 14, sh + 10, 30, 46, (40, 10, 10, 150))
        for s in (-1, 1):
            p.poly([(cx + 14 + s * 14, sh - 26), (cx + 14 + s * 28, sh - 56), (cx + 14 + s * 22, sh - 22)], (60, 14, 10, 170))
    # the chest of gold
    p.rect(cx + 18, g - 16, cx + 46, g, "#5a3a1a")
    p.rect(cx + 18, g - 16, cx + 46, g - 13, "#7a5024")
    for x in range(cx + 20, cx + 45, 4):
        p.ell(x, g - 18, 2.5, 1.6, "#f0c030")
    p.rect(cx + 30, g - 10, cx + 33, g - 6, "#c8a030")
    for lx, fx in ((cx - 6, cx - 10), (cx + 6, cx + 8)):
        limb(p, [(lx, hip), (fx, g - 2)], 8, 6, "#ece4d0")
        p.poly([(fx - 5, g - 3), (fx + 4, g - 3), (fx + 5, g), (fx - 6, g)], "#8a6a40")
    p.poly([(cx - 14, hip + 4), (cx - 15, sh + 2), (cx + 15, sh + 2), (cx + 14, hip + 4)], "#f4ecd8")
    p.poly([(cx + 3, sh + 2), (cx + 15, sh + 2), (cx + 14, hip + 4), (cx + 5, hip + 4)], "#d8ccb4")
    for y in range(sh + 6, hip, 6):
        p.px(cx - 1, y, "#c8a030")
    p.rect(cx - 14, hip - 4, cx + 14, hip - 1, "#5a3a1a")
    # the machete arm
    if ph:
        hand = (cx - 10, sh - 14 + round(b * 2))
        blade = [(hand[0], hand[1] - 2), (hand[0] + 6, hand[1] - 40), (hand[0] + 10, hand[1] - 38), (hand[0] + 3, hand[1])]
        limb(p, [(cx - 12, sh + 4), (cx - 18, sh - 6), hand], 6, 5, "#f4ecd8")
    else:
        hand = (cx - 22, hip - 4 + round(b))
        blade = [(hand[0] - 1, hand[1] + 1), (hand[0] - 32, hand[1] + 22), (hand[0] - 33, hand[1] + 18), (hand[0] - 2, hand[1] - 3)]
        limb(p, [(cx - 12, sh + 4), (cx - 20, sh + 18), hand], 6, 5, "#f4ecd8")
    p.poly(blade, "#c8d0d8")
    p.line(blade[:2], "#f8fcff", 1)
    p.ell(hand[0], hand[1], 3, 3, "#8a5a3a")
    limb(p, [(cx + 12, sh + 4), (cx + 18, sh + 20), (cx + 14, hip - 6)], 6, 5, "#d8ccb4")
    # the head, moustache, the hat
    hx, hy = cx - 2, sh - 10
    limb(p, [(cx, sh + 2), (hx, hy + 4)], 4, 4, "#8a5a3a")
    p.ell(hx, hy, 6.5, 7.5, "#8a5a3a")
    p.ell(hx + 3, hy + 1, 4, 6, "#6a4028")
    p.poly([(hx - 6, hy + 3), (hx - 1, hy + 2), (hx + 3, hy + 4), (hx - 1, hy + 5)], "#1a120c")
    by = hy - 6
    p.poly([(hx - 22, by + 3), (hx - 12, by - 1), (hx + 12, by - 1), (hx + 22, by + 3), (hx + 12, by + 3), (hx - 12, by + 3)], "#2a1e14")
    p.poly([(hx - 8, by), (hx - 7, by - 9), (hx + 7, by - 9), (hx + 8, by)], "#3a2a1c")
    p.rect(hx - 8, by - 3, hx + 8, by - 1, "#8a6a40")
    im = p.im
    outline(im)
    for k in range(4):
        u = (t + k / 4) % 1
        glow(im, cx + 22 + k * 7, g - 18 - u * 6, "#ffd040", 2.4, 0.5 * (1 - u))
    if ph:
        glow(im, hand[0] + 6, hand[1] - 38, "#ffffff", 3, 0.6)
    eyes(im, [(hx - 3, hy - 1), (hx + 1, hy - 1)], "#ff2a1a" if ph else "#f0d070", 2.6 if ph else 1.4, "#fff0d0", 0.7 if ph else 0.4)
    return im


# ---------------------------------------------------------------- El Tigre Mariposo (llano)
# The greatest jaguar of the plains, low in the grass; its rosettes are the shape of butterfly wings and beat
# as it breathes. Second phase: a roar, and the wings on its coat turn bright.
def tigremariposo(t, ph):
    W, H = 160, 124
    p = Pic(W, H)
    g = H - 4
    b = math.sin(TAU * t)
    gold, gold2, belly = "#d0902a", "#a8701e", "#f0dcb0"
    bx, by = 92, g - 40 + round(b)
    p.ell(bx, by, 40, 18, gold)
    p.ell(bx, by + 10, 32, 7, belly)
    # tail
    pts = [(bx + 36, by - 4), (bx + 52, by - 16), (bx + 60, by - 30 + b * 4), (bx + 54, by - 38 + b * 4)]
    limb(p, pts, 6, 4, gold2)
    for lx, off in ((bx - 26, 0), (bx - 12, 1), (bx + 18, 0), (bx + 30, 1)):
        limb(p, [(lx, by + 8), (lx - 2, g - 2)], 10, 8, gold if off else gold2)
        p.ell(lx - 4, g - 2, 6, 3, gold)
    # head, low and forward
    hx, hy = bx - 50, by - 8
    p.poly([(bx - 30, by - 14), (bx - 22, by + 10), (hx + 6, hy + 16), (hx + 4, hy - 6)], gold)
    p.ell(hx, hy, 16, 14, gold)
    for s in (-1, 1):
        p.ell(hx + 8 + s * 5, hy - 12, 4, 4, gold2)
    p.ell(hx - 8, hy + 6, 9, 7, belly)
    p.ell(hx - 14, hy + 2, 3, 2.5, "#3a1a14")
    if ph:
        p.ell(hx - 8, hy + 12, 8, 6, "#3a0a0a")
        for s in (-1, 1):
            p.poly([(hx - 8 + s * 5, hy + 6), (hx - 8 + s * 4, hy + 14), (hx - 8 + s * 3, hy + 6)], "#ffffff")
    else:
        p.line([(hx - 14, hy + 9), (hx - 4, hy + 10)], "#3a1a14", 1)
    for s in (-1, 1):
        for k in range(3):
            p.line([(hx - 10, hy + 6 + k * 2), (hx - 26, hy + 2 + k * 4 + s)], "#f8f0e0", 1)
    # rosettes like butterflies: each a pair of wings that open and close
    R = random.Random(60)
    spots = [(R.uniform(bx - 34, bx + 34), R.uniform(by - 12, by + 6)) for _ in range(14)]
    spots += [(R.uniform(hx - 6, hx + 12), R.uniform(hy - 8, hy + 2)) for _ in range(3)]
    wingc = ("#3a1a10", "#f05a1a", "#2a6ae0") if ph else ("#2a160c", "#5a3418", "#2a160c")
    for i, (x, y) in enumerate(spots):
        o = 0.5 + 0.5 * math.sin(TAU * t * 2 + i * 0.9)
        w = 2 + 2.6 * o
        for s in (-1, 1):
            p.poly([(x, y), (x + s * w, y - 3), (x + s * w * 0.9, y + 1), (x + s * w * 0.6, y + 3)], wingc[0])
            p.ell(x + s * w * 0.55, y - 0.5, max(0.6, w * 0.3), 1, wingc[1 + (i % 2)])
        p.line([(x, y - 2), (x, y + 2)], "#1a0c06", 1)
    im = p.im
    outline(im)
    if ph:
        arcs(ImageDrawPic(im), hx - 20, hy + 10, t, "#ffe0a0", n=3, r0=8, step=8, a0=150, a1=210)
    eyes(im, [(hx - 4, hy - 4), (hx + 4, hy - 5)], "#c8ff40", 3.2 if ph else 2.4, "#ffffe0", 0.8)
    return im


class ImageDrawPic:
    """Just enough of Pic over an existing image, for arcs() after the outline."""

    def __init__(self, im):
        self.d = ImageDraw.Draw(im)


# ---------------------------------------------------------------- El Poira (ruinas)
# A small dark imp under an enormous hat, feet on backwards, a staff with a purple light; spells circling him.
# Second phase: eyes open in every stone round him.
def poira(t, ph):
    W, H = 124, 136
    p = Pic(W, H)
    g = H - 4
    b = math.sin(TAU * t)
    skin, cloak = "#3a2a3a", "#2a1a34"
    ground(p, W, g, "#4a4440", "#6a625a", 70)
    stones = [(16, g - 4, 9, 6), (106, g - 6, 11, 8), (30, g - 2, 6, 4), (92, g - 2, 6, 4)]
    for x, y, rx, ry in stones:
        p.ell(x, y, rx, ry, "#6a645c")
        p.ell(x - 2, y - 2, rx * 0.6, ry * 0.5, "#7e786e")
    cx, hip = 62, g - 22 - round(abs(b) * 2)
    for lx in (cx - 5, cx + 5):  # backward feet
        limb(p, [(lx, hip), (lx, g - 3)], 5, 4, skin)
        p.poly([(lx - 2, g - 4), (lx + 8, g - 3), (lx + 8, g), (lx - 3, g)], skin)
    p.poly([(cx - 14, hip + 4), (cx - 8, hip - 26), (cx + 8, hip - 26), (cx + 14, hip + 4)], cloak)
    for x in range(cx - 13, cx + 14, 4):
        p.line([(x, hip + 4), (x + 1, hip + 8)], cloak, 1)
    # the staff with its light
    st = (cx - 22, hip - 36 + round(b * 2))
    p.line([(cx - 20, g), st], "#4a3420", 2)
    limb(p, [(cx - 8, hip - 20), (cx - 16, hip - 14), (cx - 20, hip - 16)], 4, 3, skin)
    hx, hy = cx, hip - 32
    p.ell(hx, hy, 8, 7, skin)
    p.poly([(hx - 7, hy + 1), (hx - 12, hy + 3), (hx - 7, hy + 4)], skin)
    p.line([(hx - 4, hy + 5), (hx + 2, hy + 4)], "#d8c8f0", 1)
    # the hat: much wider than he is tall
    lift = 6 + b * 2 if ph else 0
    by = hy - 6 - lift
    p.poly([(hx - 36, by + 4), (hx - 18, by - 2), (hx + 18, by - 2), (hx + 36, by + 4), (hx + 18, by + 5), (hx - 18, by + 5)], "#3a2a1a")
    p.poly([(hx - 12, by), (hx - 10, by - 20), (hx - 2, by - 26), (hx + 6, by - 24), (hx + 12, by)], "#4a3624")
    p.rect(hx - 12, by - 5, hx + 12, by - 2, "#7a3ac0")
    im = p.im
    outline(im)
    glow(im, st[0], st[1], "#b060ff", 7, 0.8)
    im.putpixel((round(st[0]), round(st[1])), rgb("#ffffff"))
    for i in range(6):  # spells circling him
        a = TAU * (t + i / 6)
        x, y = cx + math.cos(a) * 30, hip - 18 + math.sin(a) * 10
        glow(im, x, y, "#c890ff", 2.6, 0.7 if math.sin(a) > 0 else 0.35)
    if ph:
        eyes(im, [(x - 2, y - 1) for x, y, _, _ in stones] + [(x + 2, y - 1) for x, y, _, _ in stones[:2]], "#e060ff", 2.4, "#ffffff", 0.75)
    eyes(im, [(hx - 3, hy - 1), (hx + 2, hy - 1)], "#ffe040", 2.6 if ph else 2, "#ffffff", 0.8)
    return im


# ---------------------------------------------------------------- El Duende Mayor (ruinas)
# An old duende: a broad-brimmed hat, a white beard to his belt, pointed ears, a patched coat, juggling the
# stones he throws at you. Second phase: he grins, and the stones circle all round him.
def duendemayor(t, ph):
    W, H = 124, 140
    p = Pic(W, H)
    g = H - 4
    b = math.sin(TAU * t)
    coat, coat2 = "#4a5a2a", "#3a4620"
    cx, hip = 62, g - 26
    for lx, fx in ((cx - 5, cx - 9), (cx + 5, cx + 7)):
        limb(p, [(lx, hip), (fx, g - 3)], 6, 5, "#5a3a20")
        p.poly([(fx - 7, g - 4), (fx + 3, g - 4), (fx + 4, g), (fx - 8, g)], "#2a1a10")
    p.poly([(cx - 15, hip + 6), (cx - 12, hip - 30), (cx + 12, hip - 30), (cx + 15, hip + 6)], coat)
    p.rect(cx + 2, hip - 14, cx + 9, hip - 7, "#8a5a2a")  # a patch
    p.rect(cx - 11, hip - 4, cx - 5, hip + 2, "#6a2a3a")
    p.rect(cx - 15, hip - 6, cx + 15, hip - 3, "#3a2a14")
    hx, hy = cx - 2, hip - 38
    # arms up, juggling
    for side in (-1, 1):
        hd = (cx + side * 18, hip - 34 + round(b * side * 3))
        limb(p, [(cx + side * 11, hip - 26), (cx + side * 18, hip - 22), hd], 5, 4, coat if side < 0 else coat2)
        p.ell(hd[0], hd[1], 3, 3, "#c8906a")
    p.ell(hx, hy, 9, 8, "#c8906a")
    for side in (-1, 1):
        p.poly([(hx + side * 7, hy - 2), (hx + side * 16, hy - 8), (hx + side * 8, hy + 3)], "#c8906a")
    p.ell(hx - 5, hy + 2, 4, 3, "#d89a78")  # the nose
    beard = [(hx - 8, hy + 3), (hx + 8, hy + 3), (hx + 5, hip - 6), (hx, hip - 2), (hx - 5, hip - 6)]
    p.poly(beard, "#f0ece4")
    for k in range(4):
        p.line([(hx - 4 + k * 3, hy + 6), (hx - 3 + k * 2.4, hip - 6)], "#c8c4bc", 1)
    if ph:
        p.poly([(hx - 6, hy + 4), (hx + 4, hy + 4), (hx - 1, hy + 8)], "#2a0a0a")
        for k in range(4):
            p.px(hx - 5 + k * 2.4, hy + 4, "#ffffff")
    by = hy - 6
    p.poly([(hx - 30, by + 5), (hx - 16, by - 1), (hx + 16, by - 1), (hx + 30, by + 5), (hx + 16, by + 4), (hx - 16, by + 4)], "#6a4a2a")
    p.poly([(hx - 10, by), (hx - 8, by - 12), (hx + 8, by - 12), (hx + 10, by)], "#7a5834")
    p.rect(hx - 10, by - 4, hx + 10, by - 2, "#3a2414")
    n = 8 if ph else 3
    pts = []
    for i in range(n):
        if ph:
            a = TAU * (t + i / n)
            pts.append((cx + math.cos(a) * 44, hip - 30 + math.sin(a) * 26))
        else:  # juggling: an arc over his head
            u = (t + i / n) % 1
            pts.append((cx - 18 + 36 * u, hip - 36 - math.sin(math.pi * u) * 36))
    for x, y in pts:
        p.ell(x, y, 4, 3.4, "#7a7468")
        p.ell(x - 1, y - 1, 2, 1.6, "#9a9486")
    im = p.im
    outline(im)
    eyes(im, [(hx - 4, hy - 1), (hx + 2, hy - 1)], "#a0ff60", 2.6 if ph else 1.8, "#ffffff", 0.8)
    return im


# ---------------------------------------------------------------- El Centinela Dormido (ruinas)
# A stone guardian a thousand years old: a broad carved face with fangs, a headdress, a club, moss in the
# cracks. Second phase: the carved face cracks and falls, and under it there is an older face, glowing.
def centinela(t, ph):
    W, H = 132, 164
    p = Pic(W, H)
    g = H - 4
    b = math.sin(TAU * t)
    st, st2, st3 = "#8a826e", "#6a6454", "#a8a08a"
    R = random.Random(80)
    cx = 66
    p.rect(cx - 30, g - 10, cx + 30, g, st2)  # the plinth
    p.rect(cx - 30, g - 10, cx + 30, g - 8, st3)
    for lx in (cx - 12, cx + 12):
        p.rect(lx - 8, g - 40, lx + 8, g - 10, st)
        p.rect(lx - 10, g - 16, lx + 10, g - 10, st2)
    body = g - 40
    p.rect(cx - 24, body - 46, cx + 24, body, st)
    p.rect(cx + 6, body - 46, cx + 24, body, st2)
    p.rect(cx - 24, body - 10, cx + 24, body - 4, st3)
    for x in range(cx - 20, cx + 21, 8):
        p.rect(x, body - 9, x + 3, body - 5, st2)
    # the club across the body
    p.poly([(cx - 34, body - 60), (cx - 26, body - 64), (cx + 20, body - 6), (cx + 14, body - 2)], "#5a5444")
    p.ell(cx - 30, body - 62, 9, 8, "#5a5444")
    for s in (-1, 1):  # arms, forearms across the chest
        p.rect(cx + s * 24 - (6 if s > 0 else 0), body - 44, cx + s * 24 + (6 if s < 0 else 0), body - 16, st)
    p.rect(cx - 22, body - 30, cx + 22, body - 22, st3)
    # the head: big, square, fanged, a headdress of slabs
    hy = body - 46
    p.rect(cx - 28, hy - 44, cx + 28, hy, st)
    p.rect(cx + 8, hy - 44, cx + 28, hy, st2)
    for x in range(cx - 30, cx + 30, 10):
        p.rect(x, hy - 56, x + 7, hy - 44, st3 if (x // 10) % 2 else st)
    if not ph:
        p.rect(cx - 20, hy - 34, cx - 6, hy - 24, "#2a2620")
        p.rect(cx + 4, hy - 34, cx + 18, hy - 24, "#2a2620")
        p.rect(cx - 18, hy - 16, cx + 16, hy - 6, "#2a2620")
        for x in (cx - 16, cx + 10):
            p.poly([(x, hy - 16), (x + 4, hy - 16), (x + 2, hy - 2)], "#e8e0c8")
        for x in range(cx - 10, cx + 8, 4):
            p.rect(x, hy - 16, x + 2, hy - 13, "#e8e0c8")
        eye_pts = [(cx - 13, hy - 29), (cx + 11, hy - 29)]
    else:  # the older face under it: smooth dark stone, glowing lines
        p.rect(cx - 24, hy - 40, cx + 24, hy - 2, "#3a3630")
        for k in range(4):
            x = cx - 26 + R.uniform(0, 52)
            p.rect(x, hy - 2 + k * 3, x + 6, hy + 2 + k * 3, st3)  # fallen pieces
        eye_pts = [(cx - 10, hy - 26), (cx + 10, hy - 26)]
        p.ell(cx, hy - 10, 10, 3, "#1a1612")
    for i in range(14):  # moss and cracks
        x, y = R.uniform(cx - 26, cx + 26), R.uniform(hy - 50, g - 12)
        if R.random() < 0.5:
            p.ell(x, y, R.uniform(2, 4), 1.4, R.choice(("#5a7a3a", "#4a6a2e")))
        else:
            p.line([(x, y), (x + R.uniform(-4, 4), y + R.uniform(3, 7))], st2, 1)
    im = p.im
    outline(im)
    if ph:
        q = ImageDraw.Draw(im)
        for i in range(6):
            x0 = cx - 22 + i * 9
            pts = [(x0, hy - 40), (x0 + 3, hy - 30), (x0 - 2, hy - 20), (x0 + 2, hy - 4)]
            q.line(pts, fill=rgb("#ffb040" if (i + int(t * 8)) % 3 else "#fff0a0"), width=1)
        falling(im, 81, cx - 30, cx + 30, hy, g, t, ("#a8a08a", "#8a826e"), 10, 1)
    falling(im, 82, cx - 28, cx + 28, hy - 50, g, t, ("#c8c0a8",), 4, 1)
    e = 3.4 + (0.6 * b if ph else 0)
    eyes(im, eye_pts, "#ffa030" if not ph else "#fff060", e, "#ffffff", 0.85)
    return im


# ---------------------------------------------------------------- Chibchacum (abismo)
# The muisca god who flooded the savanna, now made to carry the earth on his shoulders: a huge painted man
# knee-deep in the water, a slab of land with hills, trees and a lake over his head. Second phase: he shifts it
# to the other shoulder, the land tilts and everything shakes.
def chibchacum(t, ph):
    W, H = 156, 168
    p = Pic(W, H)
    water = H - 26
    b = math.sin(TAU * t)
    shake = (1 if int(t * N) % 2 else -1) if ph else 0
    skin, skin2, paint = "#9a6a3e", "#7a5030", "#c02a1a"
    cx = 78 + shake
    hip = water - 6
    for lx in (cx - 14, cx + 14):
        limb(p, [(lx, hip - 6), (lx + (lx - cx) * 0.2, water + 14)], 16, 12, skin2)
    sh = hip - 56
    p.poly([(cx - 32, sh), (cx + 32, sh), (cx + 22, hip), (cx - 22, hip)], skin)
    p.poly([(cx + 8, sh), (cx + 32, sh), (cx + 22, hip), (cx + 6, hip)], skin2)
    p.rect(cx - 24, hip - 10, cx + 24, hip - 2, "#e8dcc0")  # the cotton mantle round the waist
    p.line([(cx - 24, hip - 6), (cx + 24, hip - 6)], paint, 1)
    for k in range(3):  # body paint
        y = sh + 12 + k * 10
        p.line([(cx - 20 + k * 2, y), (cx - 6, y + 4), (cx + 8, y), (cx + 18 - k * 2, y + 4)], paint, 1)
    hx, hy = cx - 2, sh - 12
    tilt = (0.16 * (1 if ph else 0) + 0.03 * b)
    # arms up, holding the earth
    for side in (-1, 1):
        hand = (cx + side * 40, sh - 34)
        hand = rot([hand], cx, sh - 40, tilt)[0]
        limb(p, [(cx + side * 28, sh + 4), (cx + side * 44, sh - 10), hand], 14, 10, skin if side < 0 else skin2)
        for k in range(3):
            p.line([(hand[0] - 3 + k * 3, hand[1] + 6), (hand[0] - 3 + k * 3, hand[1] + 10)], paint, 1)
    p.ell(hx, hy, 12, 13, skin)
    p.ell(hx + 4, hy + 1, 7, 11, skin2)
    p.poly([(hx - 10, hy + 4), (hx + 10, hy + 4), (hx + 6, hy + 22), (hx, hy + 26), (hx - 6, hy + 22)], "#1a1410")  # the beard
    p.line([(hx - 8, hy - 2), (hx - 2, hy - 1)], paint, 2)
    p.line([(hx + 2, hy - 1), (hx + 8, hy - 2)], paint, 2)
    p.rect(hx - 6, hy + 2, hx + 6, hy + 3, "#d8b040")  # a gold nose ring
    # the earth on his hands: a slab with hills, trees and a lake
    ey = sh - 46
    slab = [(cx - 66, ey + 8), (cx - 60, ey - 2), (cx + 60, ey - 2), (cx + 66, ey + 8), (cx + 56, ey + 16), (cx - 56, ey + 16)]
    hills = [(cx - 60, ey - 2), (cx - 44, ey - 22), (cx - 30, ey - 12), (cx - 12, ey - 30), (cx + 8, ey - 14), (cx + 28, ey - 26), (cx + 46, ey - 10), (cx + 60, ey - 2)]
    p.poly(rot(slab, cx, ey, tilt), "#6a4a2a")
    p.poly(rot(slab[:4] + [(cx + 60, ey + 4), (cx - 60, ey + 4)], cx, ey, tilt), "#8a6a3a")
    p.poly(rot(hills, cx, ey, tilt), "#4a7a34")
    p.poly(rot([(cx - 12, ey - 30), (cx - 6, ey - 24), (cx - 18, ey - 24)], cx, ey, tilt), "#f0f4f0")
    p.poly(rot([(cx + 10, ey - 4), (cx + 34, ey - 4), (cx + 30, ey - 1), (cx + 14, ey - 1)], cx, ey, tilt), "#3a8ac0")
    for x in (cx - 50, cx - 36, cx + 4, cx + 44, cx + 52):
        (tx, ty), = rot([(x, ey - 8)], cx, ey, tilt)
        p.line([(tx, ty), (tx, ty - 5)], "#4a3420", 1)
        p.ell(tx, ty - 7, 3, 3, "#2e5a24")
    for k in range(4):  # dust and stones dropping off the edge
        (tx, ty), = rot([(cx - 62 + k * 40, ey + 16)], cx, ey, tilt)
        u = (t + k / 4) % 1
        p.px(tx, ty + u * 20, "#6a4a2a")
    im = p.im
    outline(im)
    river(im, water, t * (2 if ph else 1), (20, 48, 70), seed=90, ripple=("#4a88b0", "#8ac0e0"))
    eyes(im, [(hx - 5, hy - 4), (hx + 4, hy - 4)], "#5ad8ff", 3.4 if ph else 2.4, "#ffffff", 0.8)
    return im


# ---------------------------------------------------------------- Buziraco (abismo)
# A goat-demon of fire on top of a dark hill: curled horns, a goat's beard and legs, a cloak of smoke.
# Second phase: his horns catch fire and the hill cracks red.
def buziraco(t, ph):
    W, H = 148, 168
    p = Pic(W, H)
    g = H - 4
    b = math.sin(TAU * t)
    R = random.Random(100)
    hide, hide2, horn = "#5a1a14", "#3a0e0a", "#d8c8a0"
    p.poly([(0, g), (24, g - 26), (60, g - 34), (96, g - 32), (130, g - 22), (W, g - 8), (W, g), (0, g)], "#1a1418")  # the hill
    top = g - 32
    cx = 74
    # the cloak of smoke behind him
    for i in range(10):
        x = cx + 8 + i * 4
        wave_line(p, x, top - 90, top - 4, 4, TAU * t + i * 0.7, R.choice(("#2a2228", "#3a3038", "#1e181c")), 0.12, 3)
    # goat legs: backward knees, hooves
    for lx in (cx - 10, cx + 10):
        limb(p, [(lx, top - 40), (lx + 8, top - 22), (lx - 2, top - 10), (lx, top - 2)], 11, 5, hide2 if lx > cx else hide)
        hooves(p, lx, top, "#0a0608")
    for i in range(18):
        x = cx - 14 + R.uniform(0, 30)
        y = top - 40 + R.uniform(0, 20)
        p.line([(x, y), (x + 1, y + 4)], "#2a0a08", 1)
    sh = top - 82
    p.poly([(cx - 22, sh), (cx + 22, sh), (cx + 16, top - 38), (cx - 16, top - 38)], hide)
    p.poly([(cx + 4, sh), (cx + 22, sh), (cx + 16, top - 38), (cx + 4, top - 38)], hide2)
    for k in range(3):
        p.line([(cx - 12, sh + 14 + k * 7), (cx - 2, sh + 16 + k * 7)], hide2, 1)
    # arms: one forward with claws, one back
    hand = (cx - 38, sh + 22 + round(b * 2))
    limb(p, [(cx - 20, sh + 4), (cx - 32, sh + 18), hand], 9, 6, hide)
    for k in range(3):
        p.line([(hand[0] - 2, hand[1] - 2 + k * 2), (hand[0] - 8, hand[1] + 1 + k * 3)], horn, 1)
    limb(p, [(cx + 20, sh + 4), (cx + 30, sh + 22), (cx + 24, sh + 38)], 9, 6, hide2)
    # the goat head
    hx, hy = cx - 6, sh - 12
    p.poly([(hx - 6, hy - 8), (hx + 8, hy - 8), (hx + 6, hy + 8), (hx - 10, hy + 14), (hx - 14, hy + 8)], hide)
    p.poly([(hx - 10, hy + 12), (hx - 4, hy + 12), (hx - 6, hy + 26), (hx - 8, hy + 26)], "#2a201c")  # the beard
    for s in (-1, 1):  # ears
        p.poly([(hx + s * 6, hy - 4), (hx + s * 16, hy), (hx + s * 6, hy + 2)], hide2)
    hornpts = {}
    for s in (-1, 1):  # big curled horns
        pts = [(hx + s * 3 + 8 * (1 - math.cos(a)) * s * 1.2, hy - 8 - 14 * math.sin(a)) for a in [i * 0.35 for i in range(10)]]
        limb(p, pts, 6, 2, horn if s < 0 else "#b8a880")
        hornpts[s] = pts
    im = p.im
    outline(im)
    if ph:
        q = ImageDraw.Draw(im)
        for i in range(5):  # the hill cracks
            x0 = 10 + i * 28 + R.uniform(-4, 4)
            q.line([(x0, g - 2), (x0 + 6, g - 14), (x0 + 2, g - 22)], fill=rgb("#ff5a1a"), width=1)
        for s in (-1, 1):
            for x, y in hornpts[s][3::2]:
                flame(im, x, y, 4, 8 + 2 * math.sin(TAU * t + x), t, FIRE, seed=int(x), lean=2)
    for x in range(cx - 18, cx + 20, 9):
        flame(im, x, top + 1, 7, 14 + 4 * math.sin(TAU * t + x * 0.3), t, FIRE, seed=x)
    embers(im, 101, cx - 40, cx + 40, top, 100, t, ("#ffc040", "#f07a1a", "#fff4c0"), 20 if ph else 12)
    eyes(im, [(hx - 6, hy - 1), (hx + 1, hy - 1)], "#ffd040", 3.6 if ph else 2.8, "#ffffff", 0.85)
    return im


# ---------------------------------------------------------------- La Madre de los Espantos (abismo)
# The mother of every fright: tall as the night, a black veil to the ground, a pale face, and in the folds of
# her dress the faces of her children drifting. Second phase: she opens her arms and they fly out round her.
def madreespantos(t, ph):
    W, H = 140, 176
    p = Pic(W, H)
    g = H - 4
    b = math.sin(TAU * t)
    veil, veil2, veil3 = "#1a1424", "#120e1a", "#2a2038"
    cx = 70
    sh = 52
    # the dress, wide at the bottom, ragged hem moving
    pts = [(cx - 16, sh)]
    for i in range(12):
        x = cx - 40 + i * 80 / 11
        pts.append((x, g - (6 if i % 2 else 0) + round(2 * math.sin(TAU * t + i))))
    pts.append((cx + 16, sh))
    p.poly(pts, veil)
    p.poly([(cx + 4, sh), (cx + 16, sh), (cx + 40, g), (cx + 10, g)], veil2)
    for k in range(4):
        p.line([(cx - 8 + k * 6, sh + 10), (cx - 26 + k * 16, g - 8)], veil3, 1)
    # the faces of her children in the folds
    R = random.Random(110)
    for i in range(9):
        y = sh + 30 + ((i * 14 + t * 30) % (g - sh - 44))
        half = 8 + (y - sh) * 0.3
        x = cx + R.uniform(-half, half)
        p.ell(x, y, 3.5, 4.5, "#4a4458")
        p.px(x - 1, y - 1, "#0a0810"); p.px(x + 1, y - 1, "#0a0810")
        p.px(x, y + 2, "#0a0810")
    # arms: long, hanging and slightly out; open wide in phase 2
    for side in (-1, 1):
        if ph:
            pts = [(cx + side * 14, sh + 4), (cx + side * 40, sh - 4), (cx + side * 62, sh - 16 + b * 3 * side)]
        else:
            pts = [(cx + side * 14, sh + 4), (cx + side * 26, sh + 34), (cx + side * 28, sh + 66 + b * 2 * side)]
        limb(p, pts, 10, 6, veil3 if side < 0 else veil2)
        for k in range(4):
            x, y = pts[-1]
            p.line([(x, y), (x + side * (k - 1.5) * 2, y + 9)], "#c8c0d8", 1)
    # the head under the veil
    hx, hy = cx - 2, sh - 16
    p.poly([(hx - 14, hy + 20), (hx - 12, hy - 8), (hx, hy - 18), (hx + 12, hy - 8), (hx + 14, hy + 20)], veil)
    p.ell(hx, hy, 8, 10, "#d8d0e0")
    p.ell(hx - 3, hy - 1, 2.5, 3.5, "#1a1424")
    p.ell(hx + 3, hy - 1, 2.5, 3.5, "#1a1424")
    p.ell(hx, hy + 6, 2, 2.6 if ph else 1.4, "#1a1424")
    for k in range(3):  # tears of black
        p.line([(hx - 3, hy + 2), (hx - 3, hy + 6 + k)], "#3a3048", 1)
    im = p.im
    outline(im)
    fade_down(im, g - 30, g + 2)
    if ph:  # her children flying out
        for i in range(6):
            a = TAU * (t + i / 6)
            x = cx + math.cos(a) * 54
            y = sh + 40 + math.sin(a) * 22 + math.sin(TAU * t * 2 + i) * 4
            gq = Pic(14, 16)
            gq.ell(7, 6, 5, 5, "#e8e4f0")
            gq.poly([(2, 6), (12, 6), (13, 15), (10, 12), (7, 15), (4, 12), (1, 15)], "#e8e4f0")
            gq.px(5, 5, "#1a1424"); gq.px(9, 5, "#1a1424"); gq.ell(7, 9, 1, 1.4, "#1a1424")
            gi = outline(gq.im, (40, 30, 60, 255))
            im.alpha_composite(gi, (round(x - 7), round(y - 8)))
    eyes(im, [(hx - 3, hy - 1), (hx + 3, hy - 1)], "#e080ff", 3.2 if ph else 2.4, "#ffffff", 0.8)
    return im


BOSSES = {"venadonegro": venadonegro, "condorhielo": condorhielo, "arrierofantasma": arrierofantasma,
          "mohana": mohana, "bufeoencantado": bufeoencantado, "tarumama": tarumama,
          "pollomaligno": pollomaligno, "boraro": boraro, "hojarasquin": hojarasquin,
          "mulatrespatas": mulatrespatas, "juanmachete": juanmachete, "tigremariposo": tigremariposo,
          "poira": poira, "duendemayor": duendemayor, "centinela": centinela,
          "chibchacum": chibchacum, "buziraco": buziraco, "madreespantos": madreespantos}


def sheet(ids, path, frames=(0, 3), k=2):
    """Contact sheet: each boss at two frames of each phase."""
    ims = [[BOSSES[b](f / N, ph) for ph in (0, 1) for f in frames] for b in ids]
    cw = max(i.width for row in ims for i in row) * k + 8
    chh = max(i.height for row in ims for i in row) * k + 8
    cols = len(ims[0])
    per = 3
    rows = -(-len(ids) // per)
    out = Image.new("RGBA", (cw * cols * per, chh * rows), (40, 38, 44, 255))
    for i, row in enumerate(ims):
        for j, im in enumerate(row):
            b_ = im.resize((im.width * k, im.height * k), Image.NEAREST)
            x = ((i % per) * cols + j) * cw + (cw - b_.width) // 2
            y = (i // per) * chh + chh - b_.height - 4
            out.alpha_composite(b_, (x, y))
    out.save(path)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--sheet" in sys.argv:
        out = sys.argv[sys.argv.index("--sheet") + 1]
        args.remove(out)
        sheet(args or list(BOSSES), out)
    else:
        import build_bosses
        build_bosses.build(args or list(BOSSES))
