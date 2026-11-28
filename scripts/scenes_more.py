"""Fight backdrops for the zones added on 2026-11-27 (scripts/zones_more.py): public/rpg/scenes/<zone>.png.

Built from each zone's `scene` spec: a sky, a far layer, a mid layer, maybe water, LPC ground recoloured
(see build_scenes.py's credits) and props at the sides, where they don't cover the fighters.
Everything but the ground tiles is drawn here in code (original).
Run: .venv/bin/python scripts/scenes_more.py [zone ...]
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw

import build_scenes as BS
import zones_more as Z
from build_scenes import W, H, hexrgb, lerp, gradient, skyline, mountains, blobs, shade, vignette, ground, edge_row, palm, frailejon

C = hexrgb


def mix(a, b, t):
    return lerp(C(a) if isinstance(a, str) else a, C(b) if isinstance(b, str) else b, t)


def dk(c, t=0.35):
    return mix(c, "#000000", t)


def lt(c, t=0.35):
    return mix(c, "#ffffff", t)


# ------------------------------------------------------------------ far layers (horizon ~ y 60-90)
def far_mountains(im, d, col, col2, rnd):
    mountains(im, 72, 40, C(col), rnd.randint(0, 99), bumps=0.018, snow=(C(col2), 22) if col2 else None)


def far_peaks(im, d, col, col2, rnd):
    mountains(im, 70, 56, C(col), rnd.randint(0, 99), bumps=0.03, peaks=0.9, line=lt(col, .3))
    px = im.load()
    for x in range(W):  # snow on the top third of each peak, a ragged lower edge
        for y in range(H):
            if px[x, y][:3] == C(col)[:3] or px[x, y][:3] == lt(col, .3)[:3]:
                if y < 44:
                    for yy in range(y, min(44 + int(math.sin(x * 0.5) * 3), H)):
                        px[x, yy] = C(col2) if (x + yy) % 7 else lt(col, .5)
                break
    mountains(im, 82, 22, dk(col, .15), rnd.randint(0, 99), bumps=0.05, peaks=0.6, line=lt(col, .2))


def far_trees(im, d, col, col2, rnd):
    skyline(im, 70, 9, dk(col, -0.0) if False else lt(col, .12), rnd.randint(0, 99), bumps=0.12)
    skyline(im, 80, 10, C(col), rnd.randint(0, 99), bumps=0.09)


def far_volcano(im, d, col, col2, rnd):
    mountains(im, 82, 16, dk(col, .1), rnd.randint(0, 99), bumps=0.03, peaks=0.4)
    cx, top = 300 + rnd.randint(-40, 40), 22
    for y in range(top, 90):
        w = 14 + (y - top) * 1.9
        d.line([(cx - w, y), (cx + w, y)], fill=C(col))
        d.point((cx - w, y), fill=lt(col, .2))
    d.line([(cx - 14, top), (cx + 14, top)], fill=C(col2))
    for i in range(6):  # snow or glow on the rim, running down
        x = cx - 12 + i * 5
        d.line([(x, top), (x - 2 + (i % 2) * 4, top + 6 + (i * 7) % 9)], fill=C(col2))
    plume = Image.new("RGBA", (W, H))
    pd = ImageDraw.Draw(plume)
    for i in range(9):
        r = 6 + i * 3
        pd.ellipse([cx - r + i * 6, top - 6 - i * 5 - r // 2, cx + r + i * 6, top - 6 - i * 5 + r // 2], fill=lt(col2, .2)[:3] + (70,))
    im.alpha_composite(plume)


def mesa_blocks(im, d, col, col2, rnd, tall=False):
    x = -20
    while x < W:
        w = rnd.randint(50, 110)
        top = rnd.randint(24, 44) if tall else rnd.randint(50, 66)
        for y in range(top, 92):
            s = (y - top) // 3
            d.line([(x - s, y), (x + w + s, y)], fill=C(col))
        d.line([(x, top), (x + w, top)], fill=lt(col, .25))
        if col2:
            for k in range(rnd.randint(1, 3)):  # bands (or old paintings)
                yy = top + 6 + k * 8
                d.line([(x + 4, yy), (x + w - 4, yy)], fill=C(col2))
        x += w + rnd.randint(30, 80)


def far_mesa(im, d, col, col2, rnd):
    mesa_blocks(im, d, col, col2, rnd)


def far_tepui(im, d, col, col2, rnd):
    mesa_blocks(im, d, col, None, rnd, tall=True)
    for i in range(14):  # red paintings on the walls: jaguars, hands, people
        x, y = rnd.randint(10, W - 10), rnd.randint(50, 80)
        if C(col) == im.getpixel((x, y))[:3] + (255,) or True:
            g = i % 3
            if g == 0:
                d.rectangle([x, y, x + 5, y + 2], fill=C(col2)); d.line([(x, y + 3), (x, y + 5)], fill=C(col2)); d.line([(x + 5, y + 3), (x + 5, y + 5)], fill=C(col2)); d.point((x + 6, y - 1), fill=C(col2))
            elif g == 1:
                d.line([(x, y), (x, y + 6)], fill=C(col2)); d.line([(x - 2, y + 2), (x + 2, y + 2)], fill=C(col2)); d.point((x, y - 1), fill=C(col2))
            else:
                d.ellipse([x, y, x + 4, y + 4], outline=C(col2))


def far_cave(im, d, col, col2, rnd):
    d.rectangle([0, 0, W, 100], fill=C(col))
    for x in range(0, W, 5):  # the roof, hanging
        L = rnd.randint(6, 30)
        for y in range(L):
            w = max(0, int((1 - y / L) * 3))
            d.line([(x - w, y), (x + w, y)], fill=dk(col, .3))
        d.point((x + 1, L - 1), fill=C(col2))
    for i in range(30):  # sheen on the walls
        x, y = rnd.randint(0, W), rnd.randint(30, 95)
        d.line([(x, y), (x + rnd.randint(2, 8), y + rnd.randint(-2, 2))], fill=C(col2))


def far_badlands(im, d, col, col2, rnd):
    mountains(im, 78, 36, C(col), rnd.randint(0, 99), bumps=0.06, peaks=0.8, line=lt(col, .3))
    px = im.load()
    for y in range(30, 92, 4):  # strata
        for x in range(W):
            if px[x, y][:3] == C(col)[:3]:
                px[x, y] = C(col2)


def far_sea(im, d, col, col2, rnd):
    d.rectangle([0, 70, W, 100], fill=C(col))
    for i in range(80):
        x, y = rnd.randint(0, W), rnd.randint(71, 98)
        d.line([(x, y), (x + rnd.randint(2, 7), y)], fill=C(col2))
    d.line([(0, 70), (W, 70)], fill=lt(col, .3))


def far_canyon(im, d, col, col2, rnd):
    for side in (0, 1):
        for x in range(W):
            t = x / W if side else 1 - x / W
            top = int(14 + ((1 - t) / 0.6) ** 1.6 * 86 + math.sin(x * 0.07 + side) * 4) if t > 0.4 else 200
            if top < 100:
                d.line([(x, top), (x, 100)], fill=C(col))
                d.point((x, top), fill=lt(col, .25))
    px = im.load()
    for y in range(20, 100, 5):
        for x in range(W):
            if px[x, y][:3] == C(col)[:3]:
                px[x, y] = C(col2)
    d.line([(214, 98), (266, 98)], fill=C("#6a9ab8"))


def far_tomb(im, d, col, col2, rnd):
    d.rectangle([0, 0, W, 100], fill=dk(col, .45))
    d.rectangle([40, 8, W - 40, 100], fill=C(col))  # the painted chamber
    for x in range(40, W - 40, 16):  # rhombus bands, red and black
        for y0 in (20, 64):
            d.polygon([(x, y0), (x + 8, y0 - 6), (x + 16, y0), (x + 8, y0 + 6)], outline=C(col2))
            d.point((x + 8, y0), fill=C("#1a1410"))
    d.line([(40, 30), (W - 40, 30)], fill=C("#1a1410"))
    d.line([(40, 54), (W - 40, 54)], fill=C("#1a1410"))
    for x in (120, 360):  # faces painted on the pillars
        d.rectangle([x - 8, 34, x + 8, 50], fill=C(col2))
        d.rectangle([x - 5, 38, x - 2, 41], fill=C("#1a1410")); d.rectangle([x + 2, 38, x + 5, 41], fill=C("#1a1410"))
        d.line([(x - 4, 46), (x + 4, 46)], fill=C("#1a1410"))
    d.ellipse([200, 30, 280, 110], fill=C("#0e0a08"))  # the way down


def far_town(im, d, col, col2, rnd):
    x = -10
    while x < W:
        w, h = rnd.randint(34, 60), rnd.randint(18, 32)
        base = 94
        d.rectangle([x, base - h, x + w, base], fill=C(col))
        d.line([(x, base - h), (x + w, base - h)], fill=dk(col, .15))
        d.polygon([(x - 3, base - h), (x + w + 3, base - h), (x + w - 4, base - h - 6), (x + 4, base - h - 6)], fill=C(col2))
        for k in range(rnd.randint(1, 3)):  # doors and windows with bars
            dx = x + 6 + k * 15
            if dx + 8 < x + w:
                d.rectangle([dx, base - 13, dx + 7, base], fill=dk(col2, .3))
                d.rectangle([dx, base - h + 5, dx + 6, base - h + 11], fill=C("#f0c060") if rnd.random() < .4 else dk(col2, .4))
        x += w + rnd.randint(0, 12)
    d.rectangle([380, 30, 400, 94], fill=C(col))  # the church tower
    d.polygon([(376, 30), (404, 30), (390, 16)], fill=C(col2))
    d.ellipse([385, 38, 395, 48], fill=C("#f0e8d0"), outline=dk(col2, .3))


def far_flames(im, d, col, col2, rnd):
    for x in range(W):
        h = 40 + math.sin(x * 0.11) * 14 + math.sin(x * 0.37) * 8 + rnd.random() * 6
        d.line([(x, int(100 - h)), (x, 100)], fill=C(col))
        if rnd.random() < 0.5:
            d.line([(x, int(100 - h)), (x, int(100 - h + 4))], fill=C(col2))
    for i in range(24):
        x = rnd.randint(0, W)
        L = rnd.randint(10, 28)
        for k in range(L):
            d.point((x + int(math.sin(k * 0.4 + i) * 2), 60 - k), fill=mix(col2, col, k / L))


def far_icewall(im, d, col, col2, rnd):
    mountains(im, 92, 70, C(col), rnd.randint(0, 99), bumps=0.08, peaks=0.9, line=C(col2))
    for i in range(40):
        x, y = rnd.randint(0, W), rnd.randint(30, 90)
        d.line([(x, y), (x + rnd.randint(-3, 3), y + rnd.randint(4, 12))], fill=C(col2))


def far_swordtrees(im, d, col, col2, rnd):
    mountains(im, 90, 20, C(col), rnd.randint(0, 99), bumps=0.04, peaks=0.5)
    for i in range(16):
        x, base, h = rnd.randint(0, W), 88, rnd.randint(30, 60)
        d.line([(x, base - h), (x, base)], fill=dk(col, .2))
        for k in range(6):
            y = base - h + k * (h // 7)
            for s in (-1, 1):
                d.line([(x, y), (x + s * (8 - k), y + 4)], fill=C(col2))


def far_room(im, d, col, col2, rnd):
    d.rectangle([0, 0, W, 100], fill=C(col))
    for x in range(0, W, 60):  # beams
        d.rectangle([x, 0, x + 5, 100], fill=C(col2))
    d.rectangle([0, 8, W, 13], fill=C(col2))
    for x in (90, 300):  # windows on a dark night
        d.rectangle([x, 30, x + 26, 60], fill=C("#141018"), outline=C(col2))
        d.line([(x + 13, 30), (x + 13, 60)], fill=C(col2))
        d.point((x + 6, 38), fill=C("#c8c8e0"))


FAR = {k[4:]: v for k, v in globals().items() if k.startswith("far_")}


# ------------------------------------------------------------------ mid layers (~ y 80-100)
def mid_hills(im, d, col, rnd):
    mountains(im, 90, 16, C(col), rnd.randint(0, 99), bumps=0.03, peaks=0.4)


def mid_ice(im, d, col, rnd):
    mountains(im, 94, 18, C(col), rnd.randint(0, 99), bumps=0.09, peaks=0.8, line=lt(col, .5))


def mid_palms(im, d, col, rnd):
    skyline(im, 92, 4, C(col), rnd.randint(0, 99))
    for i in range(14):
        palm(d, rnd.randint(0, W), 92, rnd.randint(14, 26), C(col))


def mid_mangrove(im, d, col, rnd):
    skyline(im, 86, 6, C(col), rnd.randint(0, 99), bumps=0.13)
    for i in range(30):  # arching prop roots
        x = rnd.randint(0, W)
        for k in range(3):
            a = x + (k - 1) * rnd.randint(3, 7)
            d.arc([min(x, a) - 2, 84, max(x, a) + 2, 100], 180, 360, fill=C(col))


def mid_stilts(im, d, col, rnd):
    skyline(im, 90, 4, dk(col, .2), rnd.randint(0, 99))
    for x in (40, 150, 330, 430):
        d.polygon([(x - 14, 76), (x + 14, 76), (x, 66)], fill=C(col))
        d.rectangle([x - 11, 76, x + 11, 84], fill=C(col))
        for k in (-9, -3, 3, 9):
            d.line([(x + k, 84), (x + k, 96)], fill=C(col))


def mid_bigtrees(im, d, col, rnd):
    for i in range(10):
        x = rnd.randint(0, W)
        d.rectangle([x, 20, x + rnd.randint(3, 6), 100], fill=C(col))
    skyline(im, 30, 14, C(col), rnd.randint(0, 99), bumps=0.08)
    over = Image.new("RGBA", (W, H))
    ImageDraw.Draw(over).rectangle([0, 0, W, 34], fill=C(col)[:3] + (255,))
    # the canopy hangs from the top: redraw it upside down
    for x in range(W):
        h = 30 + int(math.sin(x * 0.07) * 8 + math.sin(x * 0.23) * 4)
        d.line([(x, 0), (x, h)], fill=C(col))
    skyline(im, 94, 6, C(col), rnd.randint(0, 99))


def mid_stalag(im, d, col, rnd):
    for i in range(26):
        x, h = rnd.randint(0, W), rnd.randint(8, 30)
        for y in range(h):
            w = int((y / h) * 4)
            d.line([(x - w, 98 - h + y), (x + w, 98 - h + y)], fill=C(col))
        d.point((x, 98 - h), fill=lt(col, .3))


def mid_bigleaves(im, d, col, rnd):
    skyline(im, 88, 10, C(col), rnd.randint(0, 99), bumps=0.1)
    for i in range(22):
        x, y = rnd.randint(0, W), rnd.randint(70, 92)
        a = rnd.uniform(-0.8, 0.8)
        L = rnd.randint(10, 18)
        d.polygon([(x, y), (x + math.cos(a - .4) * L * .6, y - L * .4), (x + math.cos(a) * L, y - math.sin(a) * L * .3 - 6), (x + math.cos(a + .4) * L * .6, y + 2)], fill=lt(col, .08))


def mid_dunes(im, d, col, rnd):
    for x in range(W):
        h = 10 + math.sin(x * 0.025) * 6 + math.sin(x * 0.07 + 1) * 3
        d.line([(x, int(96 - h)), (x, 100)], fill=C(col))
        d.point((x, int(96 - h)), fill=lt(col, .3))


def mid_walls(im, d, col, rnd):
    d.rectangle([0, 76, W, 100], fill=C(col))
    for x in range(0, W, 12):
        d.rectangle([x, 70, x + 6, 76], fill=C(col))
    for y in range(80, 100, 5):
        for x in range((y // 5) % 2 * 6, W, 12):
            d.line([(x, y), (x + 10, y)], fill=dk(col, .2))


def mid_crystals(im, d, col, rnd):
    for i in range(30):
        x, h = rnd.randint(0, W), rnd.randint(6, 22)
        a = rnd.uniform(-0.4, 0.4)
        top = (x + math.sin(a) * h, 98 - h)
        d.polygon([(x - 3, 98), top, (x + 3, 98)], fill=C(col)[:3] + (200,))
        d.line([(x, 98), top], fill=lt(col, .5))


def mid_ironwall(im, d, col, rnd):
    d.rectangle([0, 60, W, 100], fill=C(col))
    for x in range(0, W, 24):
        d.line([(x, 60), (x, 100)], fill=dk(col, .3))
        for y in range(64, 100, 8):
            d.point((x + 3, y), fill=C("#ff6a1a"))
    for x in range(0, W, 8):
        d.polygon([(x, 60), (x + 4, 50), (x + 8, 60)], fill=C(col))


def mid_trees(im, d, col, rnd):
    skyline(im, 90, 10, C(col), rnd.randint(0, 99))


def mid_canyon(im, d, col, rnd):
    mountains(im, 96, 20, C(col), rnd.randint(0, 99), bumps=0.05, peaks=0.7, line=lt(col, .2))


def mid_badlands(im, d, col, rnd):
    mountains(im, 94, 22, C(col), rnd.randint(0, 99), bumps=0.08, peaks=0.8, line=lt(col, .25))


MID = {k[4:]: v for k, v in globals().items() if k.startswith("mid_")}


# ------------------------------------------------------------------ props (base: where they stand)
def p_reeds(d, x, b, r, k):
    for i in range(int(7 * k)):
        xx = x + r.randint(-8, 8)
        h = int(r.randint(8, 18) * k)
        d.line([(xx, b), (xx + r.randint(-2, 2), b - h)], fill=C("#7a8a3a"))
        if r.random() < .4:
            d.line([(xx, b - h), (xx, b - h + 3)], fill=C("#5a3a1e"))


def p_frailejon(d, x, b, r, k):
    frailejon(d, x, b, int(16 * k), int(5 * k))


def p_gold(d, x, b, r, k):  # tunjos left as offerings on a stone
    d.ellipse([x - 9, b - 5, x + 9, b + 1], fill=C("#5a564e"))
    for i in range(3):
        xx = x - 5 + i * 5
        d.rectangle([xx, b - 11, xx + 2, b - 5], fill=C("#d8a830"))
        d.point((xx + 1, b - 12), fill=C("#f8e08a"))


def p_icerock(d, x, b, r, k):
    w, h = int(14 * k), int(12 * k)
    d.polygon([(x - w, b), (x - w // 2, b - h), (x + w // 3, b - h - 3), (x + w, b)], fill=C("#a8c8e0"))
    d.line([(x - w // 2, b - h), (x + w // 3, b - h - 3)], fill=C("#ffffff"))
    d.line([(x, b - h + 2), (x - 2, b)], fill=C("#7a9ab8"))


def p_icicle(d, x, b, r, k):
    for i in range(4):
        xx, h = x + i * 5 - 8, int(r.randint(6, 16) * k)
        d.polygon([(xx - 2, b), (xx + 2, b), (xx, b - h)], fill=C("#c8e8ff"))


def p_mossytree(d, x, b, r, k):
    h = int(60 * k)
    d.rectangle([x - 3, b - h, x + 3, b], fill=C("#3a3428"))
    for y in range(b - h, b, 4):
        d.line([(x - 4, y), (x - 4, y + 2)], fill=C("#6a8a3a")); d.point((x + 4, y + 1), fill=C("#6a8a3a"))
    for i in range(6):  # beard moss hanging from the branches
        bx = x + r.randint(-16, 16)
        by = b - h + r.randint(0, 12)
        d.line([(x, by), (bx, by - 4)], fill=C("#3a3428"))
        d.line([(bx, by - 4), (bx, by + r.randint(4, 12))], fill=C("#8aa06a"))
    d.ellipse([x - 18, b - h - 10, x + 18, b - h + 8], fill=C("#2e4a24"))


def p_fern(d, x, b, r, k):
    for i in range(7):
        a = math.pi * (1.1 + i * 0.13)
        L = 12 * k
        pts = [(x + math.cos(a) * t, b + math.sin(a) * t + (t / L) ** 2 * 6) for t in range(int(L))]
        d.line(pts, fill=C("#4a8a3a"))
        for j, (px, py) in enumerate(pts[2::2]):
            d.point((px, py + 1), fill=C("#6aaa4a"))


def p_palm(d, x, b, r, k):
    palm(d, x, b, int(40 * k), C("#2e2a20"))


def p_fumarole(d, x, b, r, k):
    d.ellipse([x - 7, b - 3, x + 7, b + 1], fill=C("#d8c840"))
    d.ellipse([x - 3, b - 2, x + 3, b], fill=C("#3a3020"))


def p_sulfur(d, x, b, r, k):
    for i in range(5):
        xx = x + r.randint(-10, 10)
        d.polygon([(xx - 3, b), (xx, b - r.randint(3, 7)), (xx + 3, b)], fill=C("#f0e040"))


def p_rock(d, x, b, r, k):
    w, h = int(12 * k), int(8 * k)
    d.ellipse([x - w, b - h, x + w, b + 2], fill=C("#4a4440"))
    d.arc([x - w, b - h, x + w, b + 2], 190, 260, fill=C("#8a847a"))


def p_mangrove(d, x, b, r, k):
    h = int(50 * k)
    for i in range(6):  # roots like legs
        rx = x + (i - 2.5) * 6
        d.arc([min(x, rx) - 4, b - 22, max(x, rx) + 4, b + 18], 180, 360, fill=C("#3a2e20"), width=2)
    d.rectangle([x - 2, b - h, x + 2, b - 16], fill=C("#3a2e20"))
    d.ellipse([x - 22, b - h - 14, x + 22, b - h + 10], fill=C("#24382a"))
    d.ellipse([x - 14, b - h - 18, x + 10, b - h], fill=C("#2e4a34"))


def p_roots(d, x, b, r, k):
    for i in range(5):
        rx = x + r.randint(-14, 14)
        d.arc([rx - 6, b - 10, rx + 6, b + 8], 180, 360, fill=C("#3a2e20"))


def p_crab(d, x, b, r, k):
    d.ellipse([x - 3, b - 3, x + 3, b], fill=C("#c83a2a"))
    d.point((x - 4, b - 4), fill=C("#c83a2a")); d.point((x + 4, b - 4), fill=C("#c83a2a"))


def p_champan(d, x, b, r, k):
    d.polygon([(x - 24, b - 6), (x + 24, b - 6), (x + 18, b), (x - 18, b)], fill=C("#3a2a1a"))
    d.arc([x - 14, b - 20, x + 14, b + 6], 180, 360, fill=C("#8a7a4a"), width=3)
    d.point((x + 12, b - 16), fill=C("#ffd060"))


def p_stilthouse(d, x, b, r, k):
    d.polygon([(x - 16, b - 22), (x + 16, b - 22), (x, b - 34)], fill=C("#8a7a4a"))
    d.rectangle([x - 12, b - 22, x + 12, b - 12], fill=C("#5a4028"))
    d.rectangle([x - 3, b - 20, x + 3, b - 13], fill=C("#f0c060"))
    for s in (-10, -4, 4, 10):
        d.line([(x + s, b - 12), (x + s, b)], fill=C("#3a2a1a"))


def p_redweed(d, x, b, r, k):
    for i in range(10):
        xx = x + r.randint(-14, 14)
        col = r.choice(["#e0304a", "#c8203a", "#f0c040", "#40a060"])
        for y in range(int(r.randint(4, 10) * k)):
            d.point((xx + int(math.sin(y * 0.8 + i) * 1.5), b - y), fill=C(col))


def p_pool(d, x, b, r, k):
    d.ellipse([x - 16, b - 4, x + 16, b + 2], fill=C("#3a8ac0"))
    d.line([(x - 8, b - 2), (x + 2, b - 2)], fill=C("#a0e0ff"))


def p_bigtree(d, x, b, r, k):
    h = int(80 * k)
    d.rectangle([x - 5, b - h, x + 5, b], fill=C("#3a3020"))
    for s in (-1, 1):  # buttress roots
        d.polygon([(x, b - 18), (x + s * 14, b), (x + s * 4, b)], fill=C("#3a3020"))
    d.line([(x - 4, b - h), (x - 4, b)], fill=C("#5a4a30"))


def p_liana(d, x, b, r, k):
    for i in range(3):
        xx = x + i * 7
        pts = [(xx + math.sin(y * 0.15 + i) * 3, y) for y in range(0, b - 10, 2)]
        d.line(pts, fill=C("#3a5a24"))
        for px, py in pts[::6]:
            d.point((px + 1, py), fill=C("#6a9a3a"))


def p_heliconia(d, x, b, r, k):
    d.line([(x, b), (x, b - 22)], fill=C("#2e5a24"))
    for i in range(4):
        y = b - 20 + i * 4
        s = 1 if i % 2 else -1
        d.polygon([(x, y), (x + s * 7, y - 3), (x + s * 2, y + 2)], fill=C("#e0302a"))
        d.point((x + s * 6, y - 3), fill=C("#f0e040"))


def p_painting(d, x, b, r, k):
    d.rectangle([x - 14, b - 40, x + 14, b], fill=C("#6a4a3a"))
    far_tepui_glyphs(d, x, b)


def far_tepui_glyphs(d, x, b):
    c = C("#a83a2a")
    d.rectangle([x - 8, b - 30, x - 1, b - 27], fill=c); d.line([(x - 8, b - 26), (x - 8, b - 23)], fill=c); d.line([(x - 1, b - 26), (x - 1, b - 23)], fill=c)
    d.line([(x + 6, b - 20), (x + 6, b - 12)], fill=c); d.line([(x + 3, b - 17), (x + 9, b - 17)], fill=c)


def p_waterfall(d, x, b, r, k):
    d.rectangle([x - 6, 0, x + 6, b], fill=C("#9ad8f0"))
    for i in range(14):
        xx = x - 5 + (i * 7) % 11
        y0 = (i * 37) % (b - 10)
        d.line([(xx, y0), (xx, y0 + 12)], fill=C("#e8fbff"))
    d.ellipse([x - 12, b - 4, x + 12, b + 2], fill=C("#e0f8ff"))


def p_stalagmite(d, x, b, r, k):
    h = int(r.randint(18, 34) * k)
    for y in range(h):
        w = int((y / h) * 6) + 1
        d.line([(x - w, b - h + y), (x + w, b - h + y)], fill=C("#4a4844"))
    d.line([(x - 1, b - h + 2), (x - 3, b)], fill=C("#7a7870"))


def p_guacharo(d, x, b, r, k):  # birds' eyes shining in the dark
    for i in range(5):
        xx, yy = x + r.randint(-20, 20), r.randint(10, 50)
        d.point((xx, yy), fill=C("#ff8a3a")); d.point((xx + 2, yy), fill=C("#ff8a3a"))


def p_bigleaf(d, x, b, r, k):
    for i in range(3):
        a = -0.6 + i * 0.5
        L = int(26 * k)
        tip = (x + math.sin(a) * L, b - L)
        d.polygon([(x, b), (tip[0] - 7, (b + tip[1]) / 2), tip, (tip[0] + 7, (b + tip[1]) / 2)], fill=C("#1e4a1e"))
        d.line([(x, b), tip], fill=C("#3a7a3a"))


def p_swamp(d, x, b, r, k):
    d.ellipse([x - 18, b - 3, x + 18, b + 2], fill=C("#2a3a1e"))
    for i in range(3):
        d.ellipse([x - 10 + i * 8, b - 2, x - 8 + i * 8, b], outline=C("#5a6a3a"))


def p_cactus(d, x, b, r, k):
    h = int(30 * k)
    d.rectangle([x - 2, b - h, x + 2, b], fill=C("#3a6a3a"))
    for s, y in ((-1, b - h * 0.6), (1, b - h * 0.45)):
        y = int(y)
        d.line([(x, y), (x + s * 7, y)], fill=C("#3a6a3a"), width=3)
        d.line([(x + s * 7, y), (x + s * 7, y - 9)], fill=C("#3a6a3a"), width=3)
    d.line([(x - 1, b - h), (x - 1, b)], fill=C("#5a8a5a"))


def p_cardon(d, x, b, r, k):
    h = int(44 * k)
    for s in (-6, 0, 6):
        hh = h if s == 0 else int(h * 0.7)
        d.rectangle([x + s - 2, b - hh, x + s + 2, b], fill=C("#4a7a5a"))
        d.line([(x + s - 1, b - hh), (x + s - 1, b)], fill=C("#7aa07a"))
    d.rectangle([x - 6, b - 10, x + 6, b - 7], fill=C("#4a7a5a"))


def p_flamingo(d, x, b, r, k):
    d.line([(x, b), (x, b - 10)], fill=C("#e06070"))
    d.ellipse([x - 4, b - 15, x + 4, b - 9], fill=C("#f07a8a"))
    d.line([(x + 3, b - 13), (x + 4, b - 20), (x + 6, b - 19)], fill=C("#f07a8a"))


def p_agave(d, x, b, r, k):
    for i in range(7):
        a = math.pi * (1.1 + i * 0.13)
        d.line([(x, b), (x + math.cos(a) * 10 * k, b + math.sin(a) * 12 * k)], fill=C("#6a8a6a"), width=2)


def p_lavarock(d, x, b, r, k):
    p_rock(d, x, b, r, k)
    d.line([(x - 4, b - 3), (x + 3, b - 5)], fill=C("#ff6a1a"))


def p_deadtree(d, x, b, r, k):
    h = int(40 * k)
    d.line([(x, b), (x, b - h)], fill=C("#1a1210"), width=3)
    for i in range(5):
        y = b - h + i * 6
        s = 1 if i % 2 else -1
        d.line([(x, y), (x + s * (12 - i), y - 6)], fill=C("#1a1210"))


def p_urn(d, x, b, r, k):
    d.ellipse([x - 8, b - 18, x + 8, b], fill=C("#a86a3a"))
    d.rectangle([x - 4, b - 22, x + 4, b - 16], fill=C("#a86a3a"))
    d.line([(x - 7, b - 10), (x + 7, b - 10)], fill=C("#2a1a10"))
    d.point((x - 3, b - 14), fill=C("#2a1a10")); d.point((x + 3, b - 14), fill=C("#2a1a10"))


def p_column(d, x, b, r, k):
    h = int(50 * k)
    d.rectangle([x - 6, b - h, x + 6, b], fill=C("#c8b8a0"))
    d.rectangle([x - 8, b - h - 3, x + 8, b - h], fill=C("#a89880"))
    for y in range(b - h + 6, b, 10):
        d.polygon([(x - 5, y), (x, y - 4), (x + 5, y), (x, y + 4)], outline=C("#a8301a"))


def p_torch(d, x, b, r, k):
    d.line([(x, b - 30), (x, b - 18)], fill=C("#4a3020"), width=2)
    d.ellipse([x - 3, b - 38, x + 3, b - 29], fill=C("#ff8a2a"))
    d.ellipse([x - 1, b - 35, x + 1, b - 31], fill=C("#ffe080"))


def p_garita(d, x, b, r, k):
    d.rectangle([x - 8, b - 34, x + 8, b - 10], fill=C("#c8b890"))
    d.ellipse([x - 9, b - 44, x + 9, b - 28], fill=C("#c8b890"))
    d.rectangle([x - 2, b - 28, x + 2, b - 20], fill=C("#1a1a24"))
    d.polygon([(x - 8, b - 10), (x + 8, b - 10), (x, b)], fill=C("#a89a70"))


def p_cannon(d, x, b, r, k):
    d.polygon([(x - 14, b - 8), (x + 10, b - 12), (x + 10, b - 6), (x - 14, b - 3)], fill=C("#2a2a2a"))
    d.ellipse([x - 8, b - 6, x, b + 2], outline=C("#5a3a1e"), width=2)


def p_lamp(d, x, b, r, k):
    d.line([(x, b), (x, b - 40)], fill=C("#1a1a1a"))
    d.line([(x, b - 40), (x + 6, b - 40)], fill=C("#1a1a1a"))
    d.rectangle([x + 4, b - 39, x + 8, b - 33], fill=C("#f0c040"))


def p_rocker(d, x, b, r, k):
    d.arc([x - 10, b - 6, x + 10, b + 2], 0, 180, fill=C("#5a3a1e"))
    d.line([(x - 6, b - 4), (x - 6, b - 22)], fill=C("#5a3a1e"), width=2)
    d.line([(x - 6, b - 12), (x + 6, b - 12)], fill=C("#5a3a1e"), width=2)
    d.line([(x + 6, b - 4), (x + 6, b - 12)], fill=C("#5a3a1e"))
    for y in range(b - 21, b - 12, 2):
        d.point((x - 5, y), fill=C("#c8a870"))


def p_balcony(d, x, b, r, k):
    d.rectangle([x - 16, b - 60, x + 16, b], fill=C("#e8e0d0"))
    d.rectangle([x - 8, b - 50, x + 8, b - 30], fill=C("#2a1a14"))
    d.rectangle([x - 12, b - 32, x + 12, b - 28], fill=C("#5a3a1e"))
    for xx in range(x - 11, x + 12, 3):
        d.line([(xx, b - 40), (xx, b - 32)], fill=C("#5a3a1e"))
    d.rectangle([x - 6, b - 16, x + 6, b], fill=C("#6a4020"))


def p_saltcrystal(d, x, b, r, k):
    for i in range(4):
        xx, h = x + i * 6 - 9, int(r.randint(8, 22) * k)
        d.polygon([(xx - 3, b), (xx, b - h), (xx + 3, b)], fill=C(r.choice(["#c8c8ff", "#e0e0ff", "#a0a0f0"])))
        d.line([(xx, b - h), (xx, b)], fill=C("#ffffff"))


def p_minecart(d, x, b, r, k):
    d.polygon([(x - 12, b - 14), (x + 12, b - 14), (x + 9, b - 4), (x - 9, b - 4)], fill=C("#5a4a3a"))
    for s in (-6, 6):
        d.ellipse([x + s - 3, b - 6, x + s + 3, b], fill=C("#2a2a2a"))
    d.line([(x - 20, b), (x + 20, b)], fill=C("#6a5a4a"))
    for i in range(3):
        d.point((x - 6 + i * 6, b - 16), fill=C("#e0e0f0"))


def p_ironspike(d, x, b, r, k):
    for i in range(3):
        xx, h = x + i * 7 - 7, int(r.randint(14, 26) * k)
        d.polygon([(xx - 3, b), (xx, b - h), (xx + 3, b)], fill=C("#3a3034"))
        d.line([(xx, b - h), (xx + 2, b)], fill=C("#ff6a1a"))


def p_flames(d, x, b, r, k):
    for i in range(5):
        xx, h = x + r.randint(-10, 10), int(r.randint(10, 26) * k)
        for y in range(h):
            w = int(math.sin(y / h * math.pi) * 3) + 1
            d.line([(xx - w + int(math.sin(y * .5) * 1.5), b - y), (xx + w + int(math.sin(y * .5) * 1.5), b - y)], fill=mix("#ffe060", "#c81a0a", y / h))


def p_bluelotus(d, x, b, r, k):
    for i in range(6):
        a = math.pi * (1.1 + i * 0.16)
        d.polygon([(x, b), (x + math.cos(a - .2) * 10, b + math.sin(a - .2) * 10), (x + math.cos(a) * 14, b + math.sin(a) * 14), (x + math.cos(a + .2) * 10, b + math.sin(a + .2) * 10)], fill=C("#3a6ac8"))
        d.line([(x + math.cos(a) * 4, b + math.sin(a) * 4), (x + math.cos(a) * 12, b + math.sin(a) * 12)], fill=C("#c8e0ff"))


def p_swordtree(d, x, b, r, k):
    h = int(60 * k)
    d.line([(x, b), (x, b - h)], fill=C("#3a3438"), width=3)
    for i in range(9):
        y = b - h + i * 6
        for s in (-1, 1):
            d.line([(x, y), (x + s * (14 - i), y + 5)], fill=C("#c8c8d8"))
            d.point((x + s * (14 - i), y + 5), fill=C("#ffffff"))


def p_razors(d, x, b, r, k):
    for i in range(8):
        xx = x + r.randint(-18, 18)
        d.polygon([(xx - 1, b), (xx + 1, b - r.randint(4, 9)), (xx + 2, b)], fill=C("#d8d8e8"))


def p_bones(d, x, b, r, k):
    d.ellipse([x - 4, b - 7, x + 4, b], fill=C("#d8d0c0"))
    d.point((x - 2, b - 4), fill=C("#1a1410")); d.point((x + 1, b - 4), fill=C("#1a1410"))
    d.line([(x + 6, b - 1), (x + 16, b - 3)], fill=C("#d8d0c0"), width=2)


def p_door(d, x, b, r, k):
    d.rectangle([x - 10, b - 40, x + 10, b], fill=C("#5a3a20"))
    for xx in (x - 5, x, x + 5):
        d.line([(xx, b - 40), (xx, b)], fill=C("#3a2414"))
    d.point((x + 7, b - 20), fill=C("#c8a040"))
    d.point((x - 4, b - 28), fill=C("#ffe060")); d.point((x + 3, b - 28), fill=C("#ffe060"))  # it watches


def p_pillar(d, x, b, r, k):
    d.rectangle([x - 6, b - 70, x + 6, b], fill=C("#a89a88"))
    d.line([(x - 4, b - 70), (x - 4, b)], fill=C("#c8b8a8"))
    d.line([(x - 2, b - 40), (x + 2, b - 40)], fill=C("#3a2a24"))


def p_stove(d, x, b, r, k):
    d.rectangle([x - 14, b - 16, x + 14, b], fill=C("#5a4a40"))
    d.ellipse([x - 6, b - 12, x + 6, b - 2], fill=C("#1a0e08"))
    d.ellipse([x - 4, b - 9, x + 4, b - 3], fill=C("#ff6a1a"))
    d.ellipse([x - 10, b - 24, x + 2, b - 16], fill=C("#2a2624"))


PROPS = {k[2:]: v for k, v in globals().items() if k.startswith("p_")}


# ------------------------------------------------------------------ the scene
GROUND_SHEET = {"grass": "grass", "snow": "dirt", "dirt": "dirt", "rock": "dirt2", "sand": "dirt", "stone": "dirt2", "lavarock": "lavarock", "iron": "lavarock"}


def build(z):
    sp = z["scene"]
    rnd = random.Random(z["id"])
    im = Image.new("RGBA", (W, H))
    gradient(im, 0, 104, sp["sky"][0], sp["sky"][1], steps=10)
    d = ImageDraw.Draw(im)
    if sp.get("stars"):
        for i in range(70):
            d.point((rnd.randint(0, W), rnd.randint(0, 50)), fill=C("#fffbe0") if rnd.random() < .5 else C("#a8a8c8"))
    if sp.get("moon"):
        d.ellipse([390, 12, 404, 26], fill=C("#f0ecd8"))
        d.ellipse([394, 12, 406, 24], fill=lerp(C(sp["sky"][0]), C(sp["sky"][1]), 0.12))
    far = sp["far"]
    FAR[far[0]](im, d, far[1], far[2] if len(far) > 2 else None, rnd)
    haze = sp["haze"]
    blobs(im, 10, 60, 92, haze, 50, rnd.randint(0, 99), rw=(40, 90), rh=(3, 7))
    if sp.get("mid"):
        MID[sp["mid"][0]](im, d, sp["mid"][1], rnd)
    gy = 104
    if sp.get("water"):
        c1, c2, wy = sp["water"]
        for y in range(wy, gy + 6):
            t = (y - wy) / max(1, gy + 6 - wy)
            d.line([(0, y), (W, y)], fill=lerp(C(c1), C(c2), t))
        for i in range(60):
            x, y = rnd.randint(0, W), rnd.randint(wy, gy + 4)
            d.line([(x, y), (x + rnd.randint(3, 10), y)], fill=lt(c2, .3))
        if z["id"] == "canocristales":  # the five colours
            for i in range(40):
                x, y = rnd.randint(0, W), rnd.randint(wy, gy + 4)
                d.line([(x, y), (x + rnd.randint(4, 14), y)], fill=C(rnd.choice(["#40a060", "#3a6ae0", "#1a1a1a", "#f0c040"])))
        gy += 10
    kind, dark, light = sp["ground"]
    pal = (dark, light)
    if kind == "wood":
        d.rectangle([0, gy - 6, W, H], fill=C(light))
        for y in range(gy - 6, H, 6):  # planks
            d.line([(0, y), (W, y)], fill=C(dark))
            for x in range(random.Random(y).randint(0, 40), W, random.Random(y + 1).randint(50, 90)):
                d.line([(x, y + 1), (x, y + 5)], fill=C(dark))
                d.line([(x + 1, y + 2), (x + 30, y + 2)], fill=dk(light, .12))
    else:
        ground(im, GROUND_SHEET[kind], gy, None, pal=pal)
        edge_row(im, GROUND_SHEET[kind], gy - 8, None, pal=pal)
    if kind == "snow":
        for i in range(140):
            d.point((rnd.randint(0, W), rnd.randint(gy - 4, H)), fill=C("#ffffff"))
    if kind == "iron":  # glowing seams in the iron floor
        for y in range(gy, H, 9):
            d.line([(0, y), (W, y)], fill=C("#ff5a1a"))
        for x in range(0, W, 23):
            d.line([(x, gy), (x, H)], fill=C("#a8300a"))
    blobs(im, 8, gy - 8, gy + 6, haze, 50, rnd.randint(0, 99), rw=(30, 70), rh=(2, 4))
    props = sp["props"]
    # far, small: along the horizon; near, big: at the sides
    for i in range(10):
        PROPS[props[i % len(props)]](d, rnd.randint(0, W), gy - 2 + rnd.randint(-2, 3), rnd, 0.5)
    for j, (x, b) in enumerate(((16, 140), (58, 132), (100, 146), (380, 146), (424, 132), (466, 140))):
        PROPS[props[j % len(props)]](d, x + rnd.randint(-4, 4), b, rnd, 1.0)
    vignette(im, 0.6 if sp.get("dark") else 0.4)
    return im


if __name__ == "__main__":
    want = sys.argv[1:]
    for z in Z.all_zones():
        if want and z["id"] not in want:
            continue
        build(z).save(os.path.join(BS.OUT, f"{z['id']}.png"))
        print(z["id"])
