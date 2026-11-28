"""The 66 monsters added on 2026-11-27 (scripts/new_foes.py), drawn in code: original pixel art in the
stable's style (flat shapes, shaded and outlined by build_stable.Pic). Small ones on the pet canvas (52x40),
big ones on the mount canvas (64x61); drawn facing right, then turned to face the player (left).

Writes art/monsters/<id>.png; build_lpc.py packs them into the monster atlas with the rest.
usage: .venv/bin/python scripts/build_monsters.py [id ...] [--sheet out.png]
"""
import math
import os
import random
import sys

from PIL import Image

import build_stable as BS
from build_stable import G, MG, MH, MW, PH, PW, Pic, bird, cat_mount, d_armadillo, d_colibri, d_cuy, dk, lt, m_chiguiro, m_toro, m_venado, quad
from stable_more import d_carey, d_cangrejo, d_garza, d_iguana, d_puercoespin, d_salamandra, d_tunjo, horse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "art", "monsters")


def eyes(p, pts, col, r=1.0):
    for x, y in pts:
        p.ell(x, y, r, r, col, shade=False)
        p.px(x, y, "#ffffff")


# ---------------------------------------------------------------- páramo
def ventisca(p, c):
    cx, cy = 26, G - 16
    for k in range(6):
        a = k * 1.1
        p.curve([(cx - 4 + k, cy + 6 + k), (cx - 12 + k * 2, cy + 12), (cx - 18 + k * 3, cy + 18 - k)], 4 - k * 0.4, c["swirl"] if k % 2 else c["main"], shade=False, taper=0.3)
    p.ell(cx, cy, 9, 10, c["main"])
    p.ell(cx + 2, cy + 3, 6, 6, c["light"], shade=False)
    for k in range(5):
        a = k * 1.25
        p.curve([(cx + math.cos(a) * 9, cy + math.sin(a) * 9), (cx + math.cos(a + 0.6) * 14, cy + math.sin(a + 0.6) * 13)], 2, c["swirl"], shade=False, taper=0.3)
    eyes(p, [(cx - 2, cy - 2), (cx + 4, cy - 2)], c["eye"], 1.4)
    p.poly([(cx - 1, cy + 3), (cx + 4, cy + 3), (cx + 2, cy + 6)], dk(c["main"], 0.5))
    for (x, y) in ((6, 6), (44, 10), (10, 30), (46, 28), (38, 3)):
        p.line([(x - 1.5, y), (x + 1.5, y)], c["flake"]); p.line([(x, y - 1.5), (x, y + 1.5)], c["flake"])


def curi(p, c):
    d_cuy(p, c)
    for (x, y) in ((18, G - 13), (23, G - 14), (28, G - 13)):
        p.poly([(x - 1.5, y + 2), (x, y - 3), (x + 1.5, y + 2)], c["ice"], shade=False)
    p.px(33, G - 9, "#e03030")


def aguila(p, c):
    hx, hy = bird(p, c, 22, G - 12, 1.35, tail=8)
    p.poly([(12, G - 20), (2, G - 32), (8, G - 33), (22, G - 22)], c["wing"])
    for k in range(3):
        p.line([(14 - k * 3, G - 22 - k * 2), (6 - k * 2, G - 31 + k)], dk(c["wing"], 0.3))
    p.poly([(hx + 3, hy - 2), (hx + 8, hy), (hx + 7, hy + 3), (hx + 3, hy + 1)], c["beak"])
    p.px(hx + 7, hy + 3, dk(c["beak"], 0.4))
    p.line([(hx - 1, hy - 2.5), (hx + 3, hy - 2)], dk(c["head"], 0.5))
    p.px(hx + 1.5, hy - 1, "#e8c030")


def frailejonero(p, c):
    cx = 30
    for lx, dx in ((cx - 6, -2), (cx + 6, 2)):
        p.limb(lx, MG - 20, lx + dx, MG, 5, c["trunk"], foot=dk(c["trunk"], 0.4))
    p.poly([(cx - 9, 20), (cx + 9, 20), (cx + 8, MG - 16), (cx - 8, MG - 16)], c["trunk"])
    for y in range(22, MG - 18, 4):
        p.line([(cx - 8, y), (cx + 8, y + 2)], dk(c["trunk"], 0.35))
    for s in (-1, 1):
        p.curve([(cx + s * 8, 26), (cx + s * 16, 30), (cx + s * 22, 24)], 4, c["trunk"], taper=0.6)
        for k in range(4):
            a = -math.pi / 2 + (k - 1.5) * 0.5
            x0, y0 = cx + s * 22, 24
            p.poly([(x0, y0), (x0 + s * math.cos(a) * 9 + s * 2, y0 + math.sin(a) * 9), (x0 + s * math.cos(a) * 10, y0 + math.sin(a) * 10 + 2)], c["leaf"])
    for i, a in enumerate(range(0, 360, 24)):
        r = math.radians(a)
        p.poly([(cx, 14), (cx + math.cos(r - 0.2) * 16, 14 + math.sin(r - 0.2) * 10), (cx + math.cos(r) * 19, 14 + math.sin(r) * 12),
                (cx + math.cos(r + 0.2) * 16, 14 + math.sin(r + 0.2) * 10)], c["leaf"] if i % 2 else c["leaf2"])
    p.ell(cx, 14, 9, 6, c["leaf2"])
    eyes(p, [(cx - 3, 13), (cx + 3, 13)], c["eye"], 1.4)
    p.line([(cx - 5, 10), (cx - 1, 12)], dk(c["leaf2"], 0.6)); p.line([(cx + 5, 10), (cx + 1, 12)], dk(c["leaf2"], 0.6))
    p.line([(cx - 3, 17), (cx + 3, 17)], dk(c["leaf2"], 0.6))


def lagartija(p, c):
    d_iguana(p, c)
    for x in (10, 20, 28):
        p.px(x, G - 12, c["flake"])


def pastorhelado(p, c):
    cx = 30
    p.line([(cx + 14, 10), (cx + 13, MG)], c["staff"], 2)
    p.curve([(cx + 14, 10), (cx + 18, 6), (cx + 21, 9)], 2, c["staff"], shade=False, taper=1)
    for lx in (cx - 4, cx + 4):
        p.limb(lx, MG - 18, lx, MG, 4.5, c["pants"], foot=dk(c["pants"], 0.5))
    p.poly([(cx - 16, MG - 16), (cx + 16, MG - 16), (cx, 20)], c["ruana"])
    for k in range(3):
        p.line([(cx - 14 + k * 2, MG - 16 - k * 3), (cx + 14 - k * 2, MG - 16 - k * 3)], c["stripe"])
    p.limb(cx + 8, 28, cx + 13, 34, 3, c["skin"])
    p.ell(cx, 16, 6, 6.5, c["skin"])
    p.poly([(cx - 4, 18), (cx + 4, 18), (cx, 26)], c["beard"])
    p.ell(cx, 10, 12, 2.5, c["hat"])
    p.poly([(cx - 6, 10), (cx + 6, 10), (cx + 5, 3), (cx - 5, 3)], c["hat"])
    eyes(p, [(cx - 2.5, 15), (cx + 2.5, 15)], c["eye"], 0.9)
    for (x, y) in ((cx - 10, 30), (cx + 6, 44), (cx - 4, 36), (cx + 10, 22)):
        p.px(x, y, c["frost"])


def venadoespectral(p, c):
    m_venado(p, c)
    for (x, y) in ((44, 18), (47, 18)):
        p.px(x, y, c["eye"])
    for (x, y) in ((6, 40), (14, 48), (52, 44), (30, 52)):
        p.px(x, y, c["mist"]); p.px(x + 1, y, c["mist"])


def piedrarueda(p, c):
    cx, cy = 26, G - 12
    p.ell(cx, cy, 13, 12, c["main"])
    for (a, b) in (((cx - 8, cy - 6), (cx - 2, cy - 2)), ((cx + 3, cy - 10), (cx + 6, cy - 3)), ((cx - 10, cy + 5), (cx - 4, cy + 8))):
        p.line([a, b], dk(c["main"], 0.45))
    for (x, y, r) in ((cx - 6, cy - 9, 3), (cx + 2, cy - 11, 2.5), (cx + 9, cy - 7, 2)):
        p.ell(x, y, r, r * 0.6, c["moss"], shade=False)
    eyes(p, [(cx + 2, cy - 1), (cx + 8, cy - 1)], c["eye"], 1.3)
    p.line([(cx + 2, cy + 5), (cx + 9, cy + 4)], dk(c["main"], 0.6), 1)
    for k in range(3):
        p.line([(cx - 18 - k * 3, cy - 4 + k * 4), (cx - 15 - k * 3, cy - 4 + k * 4)], c["dust"])


def barbamusgo(p, c):
    cx, cy = 26, G - 10
    for k in range(9):
        x = cx - 12 + k * 3
        p.line([(x, cy), (x + (k % 3 - 1), G)], c["beard"], 2)
    p.ell(cx, cy - 2, 14, 9, c["main"])
    for (x, y) in ((cx - 8, cy - 7), (cx - 2, cy - 10), (cx + 6, cy - 8), (cx + 10, cy - 4)):
        p.ell(x, y, 3, 2, lt(c["main"], 0.2), shade=False)
    eyes(p, [(cx + 1, cy - 3), (cx + 7, cy - 3)], c["eye"], 1.4)
    p.poly([(cx, cy + 2), (cx + 8, cy + 2), (cx + 4, cy + 5)], "#1a1410")


def colibrihelado(p, c):
    d_colibri(p, c)
    for (x, y) in ((8, 6), (40, 12), (12, 28)):
        p.line([(x - 1, y), (x + 1, y)], "#ffffff"); p.line([(x, y - 1), (x, y + 1)], "#ffffff")


# ---------------------------------------------------------------- ciénaga
def bocachico(p, c):
    cx, cy = 26, G - 14
    p.poly([(cx - 13, cy), (cx - 22, cy - 8), (cx - 20, cy), (cx - 22, cy + 8)], c["fin"])
    p.ell(cx, cy, 14, 8, c["main"])
    p.ell(cx + 2, cy + 3, 10, 4, c["belly"], shade=False)
    p.poly([(cx - 4, cy - 7), (cx + 2, cy - 14), (cx + 6, cy - 7)], c["fin"])
    p.poly([(cx + 10, cy - 3), (cx + 18, cy - 1), (cx + 17, cy + 4), (cx + 10, cy + 3)], "#2a0a0a")
    for x in range(cx + 11, cx + 18, 2):
        p.poly([(x, cy - 2), (x + 1, cy + 1), (x + 2, cy - 2)], "#f4f0e0")
        p.poly([(x, cy + 3), (x + 1, cy), (x + 2, cy + 3)], "#f4f0e0")
    eyes(p, [(cx + 8, cy - 3)], "#e03020", 1.5)
    for k in range(3):
        p.line([(cx - 6 + k * 5, cy - 4), (cx - 4 + k * 5, cy + 1)], dk(c["main"], 0.25))
    for (x, y) in ((cx - 4, G - 2), (cx + 4, G - 1), (cx - 12, G)):
        p.ell(x, y, 2, 1, c["water"], shade=False)


def garzanegra(p, c):
    d_garza(p, c)
    p.px(33, G - 31, "#ff3a2a")


def anguila(p, c):
    pts = [(2, G - 4), (10, G - 12), (18, G - 6), (26, G - 14), (34, G - 8), (42, G - 16)]
    p.curve(pts, 6, c["main"], taper=0.5)
    p.ell(44, G - 17, 4, 3.2, c["main"])
    p.line([(45, G - 15), (48, G - 15)], "#1a1a1a")
    eyes(p, [(45, G - 18.5)], c["eye"], 0.9)
    for (a, b) in (((12, G - 20), (16, G - 16)), ((28, G - 22), (30, G - 18)), ((38, G - 2), (40, G - 6)), ((4, G - 14), (8, G - 16))):
        p.line([a, ((a[0] + b[0]) / 2 + 2, (a[1] + b[1]) / 2), b], c["spark"])
    for (x, y) in pts[1:-1]:
        p.px(x, y - 2, c["dot"])


def tortugamordedora(p, c):
    d_carey(p, c)
    for x in (18, 24, 30):
        p.poly([(x - 2, G - 13), (x, G - 18), (x + 2, G - 13)], c["mark"], shade=False)
    p.poly([(43, G - 9), (46, G - 7), (43, G - 6)], "#e8e0c8")
    p.px(42, G - 10, "#e03020")


def zancudos(p, c):
    R = random.Random(7)
    for k in range(6):
        x, y = 10 + R.uniform(0, 30), 6 + R.uniform(0, 22)
        for s in (-1, 1):
            p.poly([(x, y), (x - 4, y - 4 * s * 0.2 - 4), (x - 1, y - 1)], c["wing"], shade=False)
        p.ell(x, y, 2.6, 1.3, c["main"])
        p.line([(x + 2, y), (x + 6, y + 1)], c["main"])
        for k2 in range(3):
            p.line([(x - 1 + k2, y + 1), (x - 3 + k2 * 2, y + 5)], c["main"])
        p.px(x + 1.5, y - 0.5, c["eye"])


def raya(p, c):
    cx, cy = 24, G - 7
    p.line([(cx - 10, cy), (cx - 22, cy + 3)], c["main"], 2)
    p.poly([(cx - 22, cy + 3), (cx - 24, cy), (cx - 21, cy + 1)], c["barb"])
    p.poly([(cx - 10, cy), (cx + 2, cy - 7), (cx + 16, cy), (cx + 2, cy + 6)], c["main"])
    for (x, y) in ((cx - 3, cy - 2), (cx + 4, cy - 3), (cx + 8, cy + 1), (cx, cy + 2), (cx - 6, cy + 1)):
        p.ell(x, y, 1.3, 1.1, c["spot"], shade=False)
    eyes(p, [(cx + 9, cy - 2), (cx + 11, cy - 1)], c["eye"], 0.8)


def ranatoro(p, c):
    cx, cy = 26, G - 9
    p.limb(cx - 10, cy + 2, cx - 16, G, 4, c["dark"])
    p.ell(cx - 16, G, 4, 1.2, c["dark"])
    p.ell(cx, cy, 13, 9, c["main"])
    p.ell(cx + 3, cy + 4, 9, 4, c["belly"], shade=False)
    p.limb(cx + 8, cy + 4, cx + 10, G, 3, c["main"], foot=c["dark"])
    for (x, y) in ((cx - 5, cy - 5), (cx - 8, cy), (cx + 2, cy - 6)):
        p.ell(x, y, 2, 1.5, c["dark"], shade=False)
    for ex in (cx + 4, cx + 10):
        p.ell(ex, cy - 8, 3, 3, c["main"])
        p.ell(ex, cy - 8, 1.8, 1.8, c["eye"], shade=False)
        p.line([(ex - 1, cy - 8), (ex + 1, cy - 8)], "#111")
    p.line([(cx + 4, cy - 1), (cx + 13, cy - 2)], dk(c["main"], 0.5))


def hombrelodo(p, c):
    cx = 30
    for k in range(7):
        p.ell(cx - 15 + k * 5, MG - 2, 4, 2, c["dark"])
    p.poly([(cx - 14, MG - 2), (cx - 12, 22), (cx + 12, 22), (cx + 15, MG - 2)], c["main"])
    p.ell(cx, 20, 11, 10, c["main"])
    for s in (-1, 1):
        p.curve([(cx + s * 11, 28), (cx + s * 18, 38), (cx + s * 17, 48)], 6, c["main"], taper=0.6)
        for k in range(3):
            p.line([(cx + s * (15 + k), 48), (cx + s * (15 + k), 52 + k)], c["dark"])
    for (x, y) in ((cx - 6, 34), (cx + 4, 40), (cx - 2, 46), (cx + 8, 30)):
        p.ell(x, y, 2, 3, dk(c["main"], 0.25), shade=False)
    eyes(p, [(cx - 3, 18), (cx + 4, 18)], c["eye"], 1.6)
    p.ell(cx, 25, 4, 2, "#1a1008", shade=False)


def chiguirorabioso(p, c):
    m_chiguiro(p, c)
    p.px(54, 26, "#ff2a2a"); p.px(55, 26, "#ff2a2a")
    for (x, y) in ((58, 36), (59, 38), (57, 39)):
        p.px(x, y, "#ffffff")


def liriocarnivoro(p, c):
    cx = 22
    p.curve([(cx, G), (cx - 2, G - 10), (cx + 2, G - 18), (cx + 6, G - 22)], 3, c["stem"], taper=0.8)
    for s, y in ((-1, G - 6), (1, G - 12)):
        p.poly([(cx, y), (cx + s * 12, y - 6), (cx + s * 8, y + 2)], c["leaf"])
    hx, hy = cx + 12, G - 26
    for k in range(6):
        a = k * math.pi / 3 + 0.3
        p.poly([(hx, hy), (hx + math.cos(a - 0.3) * 9, hy + math.sin(a - 0.3) * 9), (hx + math.cos(a) * 12, hy + math.sin(a) * 12), (hx + math.cos(a + 0.3) * 9, hy + math.sin(a + 0.3) * 9)], c["petal"])
    p.ell(hx, hy, 6, 5, "#3a0a14", shade=False)
    for k in range(6):
        a = k * math.pi / 3
        p.poly([(hx + math.cos(a) * 5.5, hy + math.sin(a) * 4.5), (hx + math.cos(a) * 3, hy + math.sin(a) * 2.5), (hx + math.cos(a + 0.3) * 5, hy + math.sin(a + 0.3) * 4)], "#f4f0e0", shade=False)
    for (x, y) in ((hx - 2, hy + 6), (hx + 1, hy + 9)):
        p.px(x, y, c["drool"])


# ---------------------------------------------------------------- selva
def jaguarsombra(p, c):
    cat_mount(p, c, rosettes=c["mark"])
    for (x, y) in ((50, 20), (52, 20)):
        p.px(x, y, c["glow"])
    for (x, y) in ((6, 44), (2, 36), (12, 52)):
        p.ell(x, y, 2, 1.5, c["smoke"], shade=False)


def insect(p, c, cx, cy, segs=((-9, 4.5, 3.5), (0, 3.5, 3), (7, 4, 3.5)), legs=3, antenna=True):
    for k in range(legs):
        x = cx - 3 + k * 3
        p.line([(x, cy + 1), (x - 3 + k * 2, cy + 5), (x - 5 + k * 3, G)], c["leg"])
    for dx, rx, ry in segs:
        p.ell(cx + dx, cy, rx, ry, c["main"])
    if antenna:
        hx = cx + segs[-1][0]
        p.line([(hx + 2, cy - 3), (hx + 5, cy - 9), (hx + 8, cy - 10)], c["leg"])
        p.line([(hx + 1, cy - 3), (hx + 2, cy - 10), (hx + 5, cy - 12)], c["leg"])


def conga(p, c):
    cx, cy = 22, G - 8
    insect(p, c, cx, cy, segs=((-10, 6, 4.5), (-1, 3.5, 3), (7, 4.5, 4)))
    p.poly([(cx + 11, cy + 1), (cx + 16, cy + 3), (cx + 12, cy + 4)], c["jaw"])
    p.poly([(cx + 11, cy - 1), (cx + 16, cy - 3), (cx + 12, cy - 3.5)], c["jaw"])
    eyes(p, [(cx + 9, cy - 2)], c["eye"], 0.9)
    p.line([(cx - 16, cy), (cx - 19, cy + 2)], c["sting"], 1)


def spider(p, c, cx, cy, abd=8, mark=None):
    for s in (-1, 1):
        for k in range(4):
            x0 = cx + 2 + k * 2
            p.line([(x0, cy), (x0 + s * 0 + (k - 1.5) * 5, cy - 7 + abs(k - 1.5) * 2), (x0 + (k - 1.5) * 8 + s * 2, G)], c["leg"], 1 if s < 0 else 2)
    p.ell(cx - 6, cy - 1, abd, abd * 0.8, c["main"])
    if mark:
        mark(p, cx - 6, cy - 1)
    p.ell(cx + 4, cy + 1, 5, 4, c["main"])
    eyes(p, [(cx + 6, cy - 1), (cx + 8, cy)], c["eye"], 0.9)


def tarantula(p, c):
    spider(p, c, 26, G - 10, 9)
    for k in range(10):
        a = k * 0.6
        p.px(20 + math.cos(a) * 8, G - 11 + math.sin(a) * 6, c["hair"])
    p.ell(20, G - 5, 6, 1.6, c["skirt"], shade=False)


def escorpion(p, c):
    cx, cy = 20, G - 6
    for k in range(4):
        x = cx - 4 + k * 3
        p.line([(x, cy), (x - 2, G)], c["leg"])
    p.ell(cx, cy, 9, 4, c["main"])
    tail = [(cx - 8, cy - 1), (cx - 14, cy - 6), (cx - 14, cy - 14), (cx - 8, cy - 19), (cx - 2, cy - 18)]
    p.curve(tail, 4, c["main"], taper=0.7)
    p.poly([(cx - 2, cy - 18), (cx + 3, cy - 16), (cx - 1, cy - 14)], c["sting"])
    for s in (-1, 1):
        p.line([(cx + 7, cy), (cx + 13, cy - 2 + s * 2)], c["main"], 2)
        p.ell(cx + 16, cy - 2 + s * 3, 3.5, 2.4, c["main"])
        p.poly([(cx + 18, cy - 3 + s * 3), (cx + 23, cy - 2 + s * 4), (cx + 19, cy - 1 + s * 3)], c["main"])
    eyes(p, [(cx + 6, cy - 2)], c["eye"], 0.8)


def boa(p, c):
    cx = 24
    p.ell(cx, G - 4, 18, 5, c["main"])
    p.ell(cx + 1, G - 9, 14, 5, c["dark"])
    p.ell(cx, G - 14, 10, 5, c["main"])
    p.curve([(cx + 8, G - 16), (cx + 14, G - 22), (cx + 16, G - 28)], 6, c["main"], taper=0.8)
    p.ell(cx + 18, G - 29, 5, 3.6, c["main"])
    p.line([(cx + 22, G - 28), (cx + 25, G - 26), (cx + 26, G - 28)], "#d02a2a")
    eyes(p, [(cx + 19, G - 31)], c["eye"], 0.9)
    for (x, y) in ((cx - 12, G - 5), (cx - 4, G - 3), (cx + 6, G - 4), (cx + 14, G - 5), (cx - 6, G - 10), (cx + 4, G - 9), (cx - 4, G - 15), (cx + 6, G - 14), (cx + 12, G - 20)):
        p.ell(x, y, 2.2, 1.2, c["mark"], shade=False)


def maicero(p, c):
    bx, by = 22, G - 10
    p.curve([(bx - 5, by + 5), (bx - 12, by + 2), (bx - 14, by - 6), (bx - 10, by - 10)], 2.6, c["main"], taper=0.8)
    p.ell(bx, by + 1, 6.5, 7.5, c["main"])
    for lx in (bx - 3, bx + 3):
        p.limb(lx, by + 6, lx, G, 2.6, c["main"], foot=c["dark"])
    hx, hy = bx + 2, by - 9
    p.ell(hx, hy, 5, 4.6, c["main"])
    p.ell(hx + 1.5, hy + 0.5, 3.5, 3, c["face"], shade=False)
    p.ell(hx, hy - 4, 4, 1.6, c["dark"], shade=False)
    eyes(p, [(hx, hy), (hx + 3, hy)], "#3a1a10", 0.7)
    p.limb(bx + 4, by - 2, bx + 11, by + 2, 2.4, c["main"])
    p.ell(bx + 13, by + 1, 2.4, 5, c["corn"])
    for y in range(-3, 5, 2):
        p.px(bx + 13, by + 1 + y, dk(c["corn"], 0.3))
    p.poly([(bx + 12, by - 5), (bx + 15, by - 7), (bx + 14, by - 3)], "#6a9a3a")


def ranaveneno(p, c):
    cx, cy = 26, G - 6
    p.limb(cx - 6, cy + 1, cx - 10, G, 2.6, c["main"])
    p.ell(cx, cy, 8, 5.5, c["main"])
    p.limb(cx + 5, cy + 2, cx + 7, G, 2.2, c["main"])
    for (x, y, r) in ((cx - 3, cy - 2, 1.8), (cx + 2, cy - 3, 1.4), (cx - 5, cy + 2, 1.4), (cx + 3, cy + 1, 1.2)):
        p.ell(x, y, r, r, c["spot"], shade=False)
    p.ell(cx + 5, cy - 4, 2.2, 2.2, c["main"])
    p.ell(cx + 5, cy - 4, 1.2, 1.2, "#111", shade=False)
    for (x, y) in ((cx - 9, cy - 7), (cx + 11, cy - 9)):
        p.ell(x, y, 1.2, 1.6, c["drip"], shade=False)


def guacharaca(p, c):
    hx, hy = bird(p, c, 26, G - 12, 1.1, tail=2)
    p.poly([(22, G - 10), (2, G - 6), (4, G - 3), (24, G - 7)], c["tail"])
    p.poly([(hx + 3, hy - 1), (hx + 7, hy + 0.5), (hx + 3, hy + 1.5)], "#4a4a4a")
    p.ell(hx + 1, hy + 4, 1.6, 2, c["throat"], shade=False)
    p.px(hx + 1.5, hy - 0.5, "#ff3a2a")
    p.poly([(hx - 2, hy - 3), (hx - 3, hy - 7), (hx, hy - 3.5)], c["head"])


def liana(p, c):
    vines = [[(6, MG), (10, 44), (4, 30), (12, 16), (22, 8)], [(30, MG), (26, 46), (34, 34), (28, 22), (36, 12)], [(54, MG), (50, 46), (56, 34), (48, 24)]]
    for v in vines:
        p.curve(v, 5, c["vine"], taper=0.5)
        for (x, y) in v[1:]:
            p.poly([(x, y), (x + 6, y - 3), (x + 4, y + 2)], c["leaf"])
            p.poly([(x, y), (x - 6, y - 2), (x - 3, y + 3)], dk(c["leaf"], 0.15))
    cx, cy = 32, 24
    p.ell(cx, cy, 10, 9, c["vine"])
    p.ell(cx, cy + 3, 6, 3.5, "#2a0a0a", shade=False)
    for k in range(5):
        p.poly([(cx - 5 + k * 2.5, cy + 1), (cx - 4 + k * 2.5, cy + 3.5), (cx - 3 + k * 2.5, cy + 1)], "#e8e0c8", shade=False)
    eyes(p, [(cx - 4, cy - 3), (cx + 4, cy - 3)], c["eye"], 1.6)
    for (x, y) in ((20, 6), (46, 14), (12, 40)):
        p.ell(x, y, 2, 2, c["flower"], shade=False)


def chamanperdido(p, c):
    cx = 28
    p.line([(cx + 15, 6), (cx + 14, MG)], c["staff"], 2)
    for (x, y, r) in ((cx + 15, 3, 2.5), (cx + 18, -1, 2), (cx + 13, -3, 1.6)):
        p.ell(x, y + 4, r, r, c["smoke"], shade=False)
    for lx in (cx - 4, cx + 4):
        p.limb(lx, MG - 14, lx, MG, 4, c["skin"], foot=dk(c["skin"], 0.4))
    p.poly([(cx - 12, MG - 12), (cx + 12, MG - 12), (cx + 8, 22), (cx - 8, 22)], c["robe"])
    for y in (MG - 18, MG - 24, MG - 30):
        p.line([(cx - 10, y), (cx + 10, y)], c["band"])
    p.limb(cx + 7, 26, cx + 14, 34, 3, c["skin"])
    p.ell(cx, 16, 6, 6.5, c["skin"])
    for k, col in enumerate(c["feathers"]):
        a = math.radians(200 + k * 28)
        p.poly([(cx + math.cos(a) * 5, 12 + math.sin(a) * 4), (cx + math.cos(a) * 15, 12 + math.sin(a) * 12), (cx + math.cos(a + 0.12) * 13, 12 + math.sin(a + 0.12) * 11)], col)
    p.rect(cx - 6, 10, cx + 6, 12, c["band"])
    p.line([(cx - 3, 18), (cx + 3, 18)], c["paint"])
    eyes(p, [(cx - 2.5, 15), (cx + 2.5, 15)], c["eye"], 0.9)
    for k in range(5):
        p.px(cx - 4 + k * 2, 24, c["beads"])


# ---------------------------------------------------------------- llano
def torocandela(p, c):
    m_toro(p, c)
    for x in range(10, 40, 4):
        h = 6 + (x % 3) * 3
        p.poly([(x - 2, 21), (x, 21 - h), (x + 2, 21)], c["flame"], shade=False)
        p.px(x, 19, c["flame2"])
    p.px(52, 23, "#ffd040")


def garrapata(p, c):
    cx, cy = 24, G - 9
    for s in (-1, 1):
        for k in range(4):
            a = math.radians(-60 + k * 40) if s > 0 else math.radians(120 + k * 40)
            p.line([(cx + math.cos(a) * 8, cy + 2), (cx + math.cos(a) * 14, cy + 4), (cx + math.cos(a) * 15, G)], c["leg"])
    p.ell(cx, cy, 11, 9, c["main"])
    p.ell(cx - 2, cy - 3, 6, 4, lt(c["main"], 0.2), shade=False)
    p.ell(cx + 11, cy + 1, 3.5, 3, c["head"])
    p.poly([(cx + 13, cy + 2), (cx + 17, cy + 3), (cx + 13, cy + 4)], c["head"])
    eyes(p, [(cx + 11, cy)], "#ff2a2a", 0.8)


def cimarron(p, c):
    horse(p, c, mane=c["mane"], tail=c["mane"])
    p.poly([(35, 6), (32, 2), (37, 4)], c["mane"])
    p.px(49, 12, "#ff3a2a")
    for (x, y) in ((2, 58), (8, 60), (40, 59)):
        p.ell(x, y, 3, 1.4, c["dust"], shade=False)


def halconfuego(p, c):
    hx, hy = bird(p, c, 24, G - 13, 1.2, tail=6)
    p.poly([(14, G - 18), (4, G - 30), (10, G - 30), (24, G - 20)], c["wing"])
    for (x, y, h) in ((6, G - 31, 6), (10, G - 31, 5), (18, G - 6, 6), (14, G - 5, 5)):
        p.poly([(x - 2, y), (x, y - h), (x + 2, y)], c["flame"], shade=False)
    p.poly([(hx + 3, hy - 2), (hx + 7, hy), (hx + 6, hy + 2.5), (hx + 3, hy + 1)], c["beak"])
    p.px(hx + 1.5, hy - 1, "#fff0a0")


def espantosabana(p, c):
    cx = 30
    pts = [(cx - 12, 22), (cx + 12, 22), (cx + 16, MG - 4)]
    for k in range(7):
        pts.append((cx + 16 - k * 5.3, MG - 4 + (5 if k % 2 else 0)))
    p.poly(pts, c["sheet"])
    p.ell(cx, 18, 11, 10, c["sheet"])
    p.ell(cx, 9, 17, 3, c["hat"])
    p.poly([(cx - 8, 9), (cx + 8, 9), (cx + 6, 1), (cx - 6, 1)], c["hat"])
    p.line([(cx - 8, 7), (cx + 8, 7)], c["band"], 2)
    p.ell(cx - 4, 18, 2.4, 3, "#141018", shade=False); p.ell(cx + 4, 18, 2.4, 3, "#141018", shade=False)
    eyes(p, [(cx - 4, 18), (cx + 4, 18)], c["eye"], 0.9)
    p.ell(cx, 25, 2, 2.6, "#141018", shade=False)
    for s in (-1, 1):
        p.curve([(cx + s * 10, 28), (cx + s * 18, 34), (cx + s * 20, 40)], 4, c["sheet"], taper=0.4)


def iguanafuego(p, c):
    d_salamandra(p, c)


def remolino(p, c):
    R = random.Random(11)
    for k in range(9):
        y = MG - 2 - k * 6
        w = 4 + k * 2.6
        cx = 30 + math.sin(k * 0.8) * 4
        p.ell(cx, y, w, 3, c["main"] if k % 2 else c["light"])
        p.line([(cx - w + 2, y), (cx + w - 2, y + 1)], dk(c["main"], 0.25))
    for k in range(12):
        x, y = R.uniform(6, 56), R.uniform(4, 50)
        p.rect(x, y, x + 1, y + 1, R.choice((c["debris"], c["debris2"])))
    eyes(p, [(26, 22), (34, 22)], c["eye"], 1.4)


def coplero(p, c):
    cx = 28
    for lx in (cx - 4, cx + 4):
        p.line([(lx, MG - 16), (lx, MG)], c["bone"], 2)
        p.line([(lx - 1, MG), (lx + 2, MG)], c["bone"])
    p.poly([(cx - 9, MG - 16), (cx + 9, MG - 16), (cx + 7, 24), (cx - 7, 24)], c["shirt"])
    p.line([(cx - 7, 34), (cx + 7, 34)], c["sash"], 2)
    p.ell(cx + 6, 38, 7, 5, c["wood"])
    p.ell(cx + 6, 38, 2, 2, "#1a1008", shade=False)
    p.line([(cx + 10, 36), (cx + 22, 28)], c["wood"], 2)
    p.line([(cx - 4, 28), (cx + 4, 37)], c["bone"], 1)
    p.ell(cx, 17, 6, 6.5, c["bone"])
    p.ell(cx, 9, 13, 2.6, c["hat"])
    p.poly([(cx - 7, 9), (cx + 7, 9), (cx + 5, 2), (cx - 5, 2)], c["hat"])
    p.ell(cx - 2.5, 16, 1.8, 2, "#141010", shade=False); p.ell(cx + 2.5, 16, 1.8, 2, "#141010", shade=False)
    eyes(p, [(cx - 2.5, 16), (cx + 2.5, 16)], c["eye"], 0.8)
    for k in range(4):
        p.px(cx - 3 + k * 2, 21, "#141010")
    for (x, y) in ((cx + 24, 18), (cx + 28, 12), (cx + 20, 10)):
        p.line([(x, y), (x, y - 4)], c["note"]); p.ell(x - 1, y, 1.4, 1.1, c["note"], shade=False)


def armadillobrasa(p, c):
    d_armadillo(p, c)
    for (a, b) in (((16, G - 12), (19, G - 6)), ((24, G - 13), (24, G - 7)), ((30, G - 12), (28, G - 6))):
        p.line([a, b], c["lava"])
    for x in (18, 24, 30):
        p.poly([(x - 1.5, G - 13), (x, G - 18), (x + 1.5, G - 13)], c["lava"], shade=False)


def cascabel(p, c):
    cx = 22
    p.ell(cx, G - 4, 14, 4.5, c["main"])
    p.ell(cx + 1, G - 8, 10, 4, c["main"])
    p.curve([(cx - 12, G - 6), (cx - 16, G - 12), (cx - 15, G - 18)], 3, c["main"], taper=0.8)
    for k in range(4):
        p.ell(cx - 15, G - 19 - k * 2, 2, 1.2, c["rattle"])
    p.curve([(cx + 6, G - 10), (cx + 10, G - 18), (cx + 14, G - 20)], 5, c["main"], taper=0.8)
    p.ell(cx + 17, G - 21, 4.6, 3.4, c["main"])
    p.poly([(cx + 19, G - 19), (cx + 23, G - 16), (cx + 20, G - 15)], "#f4f0e0")
    p.line([(cx + 21, G - 21), (cx + 25, G - 21), (cx + 26, G - 23)], "#d02a2a")
    eyes(p, [(cx + 18, G - 23)], c["eye"], 0.8)
    for x in range(cx - 10, cx + 12, 4):
        p.poly([(x - 2, G - 5), (x, G - 7), (x + 2, G - 5), (x, G - 3)], c["mark"], shade=False)


# ---------------------------------------------------------------- ruinas
def gargola(p, c):
    cx, cy = 24, G - 10
    for s, dx in ((-1, -2), (1, 2)):
        p.poly([(cx + dx, cy - 6), (cx + dx - 10, cy - 20), (cx + dx - 16, cy - 16), (cx + dx - 14, cy - 10), (cx + dx - 18, cy - 6), (cx + dx - 6, cy - 2)], c["wing"] if s < 0 else dk(c["wing"], 0.15))
    for lx in (cx - 6, cx + 6):
        p.limb(lx, cy + 2, lx, G, 3.5, c["main"], foot=dk(c["main"], 0.4))
    p.ell(cx, cy, 9, 7, c["main"])
    p.ell(cx + 9, cy - 6, 5.5, 5, c["main"])
    p.poly([(cx + 7, cy - 10), (cx + 6, cy - 16), (cx + 9, cy - 11)], c["main"])
    p.poly([(cx + 11, cy - 10), (cx + 12, cy - 16), (cx + 13, cy - 10)], c["main"])
    p.poly([(cx + 12, cy - 4), (cx + 16, cy - 3), (cx + 12, cy - 2)], "#f0ece0")
    eyes(p, [(cx + 10, cy - 7)], c["eye"], 1.2)
    for (a, b) in (((cx - 6, cy - 3), (cx - 2, cy + 2)), ((cx + 2, cy - 4), (cx + 4, cy + 1))):
        p.line([a, b], dk(c["main"], 0.45))


def calavera(p, c):
    cx, cy = 26, G - 12
    p.ell(cx, cy - 2, 12, 11, c["bone"])
    p.poly([(cx - 7, cy + 5), (cx + 9, cy + 5), (cx + 7, cy + 12), (cx - 5, cy + 12)], c["bone"])
    for x in range(cx - 5, cx + 8, 3):
        p.line([(x, cy + 6), (x, cy + 11)], dk(c["bone"], 0.4))
    p.ell(cx - 3, cy - 1, 3.4, 4, "#1a1010", shade=False); p.ell(cx + 6, cy - 1, 3.4, 4, "#1a1010", shade=False)
    eyes(p, [(cx - 3, cy - 1), (cx + 6, cy - 1)], c["eye"], 1)
    p.poly([(cx + 1, cy + 3), (cx + 3, cy + 3), (cx + 2, cy + 1)], "#1a1010")
    p.line([(cx - 6, cy - 10), (cx - 2, cy - 6), (cx - 4, cy - 3)], dk(c["bone"], 0.4))
    for k in range(3):
        p.line([(cx - 16 - k * 4, cy + 2 + k * 3), (cx - 13 - k * 4, cy + 2 + k * 3)], c["dust"])


def idolo(p, c):
    cx = 30
    p.rect(cx - 14, MG - 6, cx + 14, MG, dk(c["main"], 0.2))
    p.rect(cx - 12, 12, cx + 12, MG - 6, c["main"])
    p.rect(cx - 14, 6, cx + 14, 14, c["main"])
    for x in range(cx - 12, cx + 13, 5):
        p.rect(x, 2, x + 2, 6, c["main"])
    p.rect(cx - 9, 18, cx - 3, 24, "#1a1410"); p.rect(cx + 3, 18, cx + 9, 24, "#1a1410")
    eyes(p, [(cx - 6, 21), (cx + 6, 21)], c["eye"], 1.6)
    p.rect(cx - 8, 30, cx + 8, 36, "#1a1410")
    for x in (cx - 7, cx + 5):
        p.poly([(x, 30), (x + 1, 39), (x + 2, 30)], "#f0ece0", shade=False)
    for x in range(cx - 5, cx + 5, 2):
        p.px(x, 30, "#f0ece0")
    for s in (-1, 1):
        p.rect(cx + s * 12 - (2 if s > 0 else 2), 34, cx + s * 12 + 2, 50, dk(c["main"], 0.1))
    p.line([(cx - 10, 42), (cx + 10, 42)], dk(c["main"], 0.4))
    p.line([(cx - 10, 48), (cx + 10, 48)], dk(c["main"], 0.4))
    for (x, y) in ((cx - 13, 16), (cx + 12, 26), (cx - 8, 52)):
        p.ell(x, y, 2.5, 1.2, c["moss"], shade=False)


def tunjomaldito(p, c):
    d_tunjo(p, c)
    p.px(24, G - 23, "#ff2a2a"); p.px(28, G - 23, "#ff2a2a")


def sacerdotehueso(p, c):
    cx = 28
    p.line([(cx + 14, 4), (cx + 13, MG)], c["staff"], 2)
    p.ell(cx + 14, 4, 3.5, 3.5, c["bone"])
    p.px(cx + 13, 3.5, "#1a1010"); p.px(cx + 15, 3.5, "#1a1010")
    p.poly([(cx - 13, MG), (cx + 13, MG), (cx + 8, 22), (cx - 8, 22)], c["robe"])
    p.poly([(cx - 3, 22), (cx + 3, 22), (cx + 2, MG), (cx - 2, MG)], c["trim"], shade=False)
    for s in (-1, 1):
        p.line([(cx + s * 8, 26), (cx + s * 12, 36), (cx + s * 13 + (1 if s > 0 else 0), 30)], c["bone"], 2)
    p.poly([(cx - 9, 22), (cx, 4), (cx + 9, 22)], c["robe"])
    p.ell(cx, 16, 5, 5.5, c["bone"])
    p.ell(cx - 2, 15, 1.6, 2, "#141010", shade=False); p.ell(cx + 2, 15, 1.6, 2, "#141010", shade=False)
    eyes(p, [(cx - 2, 15), (cx + 2, 15)], c["eye"], 0.7)
    for k in range(3):
        p.px(cx - 2 + k * 2, 20, "#141010")
    for (x, y) in ((cx - 18, 30), (cx - 20, 20), (cx + 20, 12)):
        p.ell(x, y, 1.6, 1.6, c["eye"], shade=False)


def serpientepiedra(p, c):
    cx = 22
    p.ell(cx, G - 4, 16, 5, c["main"])
    p.ell(cx, G - 10, 11, 4.5, c["main"])
    p.curve([(cx + 8, G - 12), (cx + 12, G - 20), (cx + 13, G - 28)], 7, c["main"], taper=0.8)
    p.rect(cx + 8, G - 34, cx + 20, G - 26, c["main"])
    p.rect(cx + 18, G - 31, cx + 24, G - 27, c["main"])
    for x in (cx + 19, cx + 22):
        p.poly([(x, G - 27), (x + 1, G - 24), (x + 2, G - 27)], "#f0ece0", shade=False)
    eyes(p, [(cx + 15, G - 31)], c["eye"], 1.1)
    for x in range(cx - 12, cx + 14, 5):
        p.rect(x, G - 6, x + 2, G - 3, dk(c["main"], 0.35))
        p.rect(x + 2, G - 12, x + 4, G - 9, dk(c["main"], 0.35))
    p.ell(cx - 10, G - 8, 2.5, 1.2, c["moss"], shade=False)


def aranatumba(p, c):
    def skull(p_, x, y):
        p_.ell(x, y - 1, 3, 2.6, c["mark"], shade=False)
        p_.px(x - 1, y - 1, "#141010"); p_.px(x + 1, y - 1, "#141010")
        p_.rect(x - 1.5, y + 1, x + 1.5, y + 2, c["mark"], shade=False)
    spider(p, c, 28, G - 10, 9, mark=skull)
    p.line([(20, 0), (20, G - 19)], c["web"])


def guerreroespectro(p, c):
    cx = 28
    p.line([(cx + 14, 2), (cx + 13, MG)], c["spear"], 2)
    p.poly([(cx + 14, 2), (cx + 12, 8), (cx + 16, 8)], c["tip"])
    for lx in (cx - 4, cx + 4):
        p.limb(lx, MG - 18, lx, MG - 4, 4, c["main"])
    p.poly([(cx - 4, MG - 4), (cx - 1, MG - 4), (cx - 2, MG)], c["main"], shade=False)
    p.poly([(cx - 10, MG - 16), (cx + 10, MG - 16), (cx + 8, 22), (cx - 8, 22)], c["main"])
    p.rect(cx - 9, MG - 20, cx + 9, MG - 17, c["band"])
    p.ell(cx - 10, 34, 7, 9, c["shield"])
    p.ell(cx - 10, 34, 3, 4, c["band"], shade=False)
    p.limb(cx + 7, 26, cx + 13, 32, 3, c["main"])
    p.ell(cx, 15, 6, 6.5, c["main"])
    for k in range(7):
        a = math.radians(200 + k * 23)
        p.line([(cx + math.cos(a) * 5, 11 + math.sin(a) * 4), (cx + math.cos(a) * 13, 11 + math.sin(a) * 11)], c["feather"], 2)
    eyes(p, [(cx - 2, 15), (cx + 3, 15)], c["eye"], 1.1)
    for (x, y) in ((cx - 16, 48), (cx + 4, 54), (cx - 8, 56)):
        p.ell(x, y, 3, 1.4, c["mist"], shade=False)


def ratatumba(p, c):
    bx, by = 22, G - 6
    p.curve([(bx - 8, by + 1), (bx - 15, by + 3), (bx - 21, by)], 2, c["tail"], taper=0.5)
    p.ell(bx, by, 10, 5.5, c["main"])
    for lx in (bx - 6, bx + 5):
        p.limb(lx, by + 3, lx, G, 2.2, c["dark"])
    p.poly([(bx + 6, by - 4), (bx + 17, by + 1), (bx + 6, by + 3)], c["main"])
    p.ell(bx + 5, by - 5, 2.6, 2.6, c["ear"])
    eyes(p, [(bx + 10, by - 2)], "#ff2a2a", 0.9)
    p.px(bx + 17, by + 1, "#e0a0a0")
    p.poly([(bx + 13, by + 2), (bx + 14, by + 4), (bx + 15, by + 2)], "#f0ece0", shade=False)


def ojocripta(p, c):
    cx, cy = 26, G - 18
    for k in range(7):
        a = math.radians(30 + k * 20)
        p.curve([(cx + math.cos(a) * 8, cy + math.sin(a) * 8), (cx + math.cos(a) * 14 + math.sin(k) * 2, cy + math.sin(a) * 14), (cx + math.cos(a) * 18, cy + math.sin(a) * 18 + 2)], 2.4, c["flesh"], taper=0.3)
    p.ell(cx, cy, 11, 10, c["flesh"])
    p.ell(cx, cy, 8, 7, "#f4ecdc")
    for (a, b) in (((cx - 7, cy - 2), (cx - 3, cy)), ((cx + 7, cy + 2), (cx + 3, cy + 1)), ((cx - 4, cy + 5), (cx - 1, cy + 2))):
        p.line([a, b], "#c04040")
    p.ell(cx + 1, cy, 4.5, 4.5, c["iris"], shade=False)
    p.ell(cx + 1, cy, 2, 2.6, "#111", shade=False)
    p.px(cx - 1, cy - 2, "#ffffff")
    p.poly([(cx - 11, cy - 3), (cx, cy - 11), (cx + 11, cy - 3), (cx, cy - 7)], dk(c["flesh"], 0.2))


# ---------------------------------------------------------------- easy (small)
def mariquita(p, c):
    cx, cy = 26, G - 5
    for k in range(3):
        p.line([(cx - 3 + k * 3, cy + 2), (cx - 4 + k * 3, G)], "#1a1a1a")
    p.ell(cx, cy, 7, 5, c["main"])
    p.line([(cx - 1, cy - 5), (cx - 1, cy + 5)], "#1a1a1a")
    for (x, y) in ((cx - 4, cy - 1), (cx + 2, cy - 2), (cx - 3, cy + 2), (cx + 3, cy + 2)):
        p.ell(x, y, 1.2, 1.2, "#1a1a1a", shade=False)
    p.ell(cx + 7, cy, 3, 2.6, "#1a1a1a")
    p.px(cx + 8, cy - 1, "#ffffff")


def polilla(p, c):
    cx, cy = 26, G - 12
    for s in (-1, 1):
        p.poly([(cx, cy), (cx + s * 10, cy - 8), (cx + s * 12, cy + 1), (cx + s * 5, cy + 5)], c["wing"])
        p.ell(cx + s * 7, cy - 2, 1.8, 1.8, c["eye"], shade=False)
    p.ell(cx, cy + 1, 2, 6, c["body"])
    p.line([(cx - 1, cy - 5), (cx - 4, cy - 9)], c["body"]); p.line([(cx + 1, cy - 5), (cx + 4, cy - 9)], c["body"])


def pajarito(p, c):
    hx, hy = bird(p, c, 24, G - 7, 0.75, tail=4)
    p.poly([(hx + 2, hy - 0.5), (hx + 5, hy + 0.5), (hx + 2, hy + 1.5)], c["beak"])


def caracol(p, c):
    p.poly([(10, G), (36, G), (38, G - 4), (34, G - 6), (12, G - 3)], c["body"])
    p.line([(35, G - 6), (37, G - 11)], c["body"]); p.line([(33, G - 6), (34, G - 10)], c["body"])
    p.px(37, G - 12, "#111"); p.px(34, G - 11, "#111")
    p.ell(22, G - 9, 9, 8, c["shell"])
    for k in range(3):
        p.ell(23 - k, G - 9 - k * 0.5, 6 - k * 2, 5 - k * 1.6, lt(c["shell"], 0.15 + k * 0.1), shade=False)


def cangrejito(p, c):
    d_cangrejo(p, c)


def pececito(p, c):
    cx, cy = 26, G - 10
    p.poly([(cx - 7, cy), (cx - 13, cy - 5), (cx - 12, cy), (cx - 13, cy + 5)], c["fin"])
    p.ell(cx, cy, 8, 5.5, c["main"])
    for x in (cx - 3, cx + 1):
        p.line([(x, cy - 5), (x, cy + 5)], c["stripe"], 2)
    eyes(p, [(cx + 4, cy - 1)], "#111", 1)
    for (x, y, r) in ((cx + 10, cy - 6, 1.3), (cx + 13, cy - 10, 1)):
        p.ell(x, y, r, r, "#a0e0ff", shade=False)


def gusanito(p, c):
    for k in range(6):
        x = 12 + k * 4.5
        y = G - 4 - abs(math.sin(k * 0.9)) * 4
        p.ell(x, y, 3.4, 3.4, c["main"] if k % 2 else lt(c["main"], 0.15))
    eyes(p, [(36, G - 8)], "#111", 0.9)
    p.line([(35, G - 11), (34, G - 14)], c["main"]); p.line([(37, G - 11), (38, G - 14)], c["main"])


def abejita(p, c):
    cx, cy = 26, G - 12
    for s in (-1, 1):
        p.ell(cx - 1, cy - 6, 4, 3, "#e0f0ff", shade=False)
    p.ell(cx, cy, 7, 5, c["main"])
    for x in (cx - 3, cx + 1):
        p.line([(x, cy - 5), (x, cy + 5)], "#2a2018", 2)
    p.poly([(cx - 7, cy), (cx - 10, cy + 1), (cx - 7, cy + 2)], "#2a2018")
    p.ell(cx + 7, cy, 3, 3, "#2a2018")
    p.px(cx + 8, cy - 1, "#ffffff")


def hongo(p, c):
    cx = 26
    p.rect(cx - 4, G - 10, cx + 4, G, c["stem"])
    eyes(p, [(cx - 2, G - 6), (cx + 2, G - 6)], "#111", 0.8)
    p.ell(cx, G - 12, 12, 7, c["cap"])
    p.rect(cx - 12, G - 12, cx + 12, G - 10, c["cap"])
    for (x, y, r) in ((cx - 6, G - 15, 2), (cx + 3, G - 16, 1.6), (cx + 8, G - 12, 1.4), (cx - 1, G - 12, 1.2)):
        p.ell(x, y, r, r, "#f8f0e0", shade=False)


def grillo(p, c):
    cx, cy = 24, G - 6
    p.line([(cx - 2, cy), (cx - 10, cy - 8), (cx - 12, G)], c["main"], 2)
    p.ell(cx, cy, 9, 3.6, c["main"])
    p.poly([(cx - 9, cy - 1), (cx + 5, cy - 4), (cx + 4, cy)], dk(c["main"], 0.2))
    for x in (cx + 2, cx + 5):
        p.line([(x, cy + 2), (x + 1, G)], c["main"])
    p.ell(cx + 9, cy - 1, 3, 2.6, c["main"])
    p.line([(cx + 10, cy - 3), (cx + 16, cy - 12)], c["main"]); p.line([(cx + 11, cy - 3), (cx + 19, cy - 9)], c["main"])
    p.px(cx + 10, cy - 2, "#111")


def lagartijita(p, c):
    d_iguana(p, c)


def pollito(p, c):
    cx, cy = 26, G - 7
    for lx in (cx - 2, cx + 2):
        p.line([(lx, cy + 4), (lx, G)], c["leg"])
    p.ell(cx, cy, 6.5, 6, c["main"])
    p.ell(cx + 4, cy - 6, 4.2, 4, c["main"])
    p.poly([(cx + 7, cy - 6), (cx + 10, cy - 5), (cx + 7, cy - 4)], c["leg"])
    p.px(cx + 5, cy - 7, "#111")
    p.poly([(cx - 4, cy - 1), (cx - 8, cy + 1), (cx - 3, cy + 3)], lt(c["main"], 0.2))


def ratoncito(p, c):
    bx, by = 24, G - 5
    p.curve([(bx - 6, by + 1), (bx - 12, by + 2), (bx - 16, by - 2)], 1.6, c["tail"], taper=0.6)
    p.ell(bx, by, 7, 4.5, c["main"])
    p.poly([(bx + 4, by - 3), (bx + 12, by + 1), (bx + 4, by + 3)], c["main"])
    p.ell(bx + 4, by - 4, 2.4, 2.4, c["ear"])
    p.px(bx + 8, by - 1, "#111")
    p.px(bx + 12, by + 1, "#e0a0a0")


def erizo(p, c):
    d_puercoespin(p, c)


def hormiguita(p, c):
    insect(p, c, 22, G - 5, segs=((-7, 4.5, 3.5), (0, 2.6, 2.2), (5, 3.2, 3)))
    p.px(28, G - 6, "#111")


def tortuguita(p, c):
    d_carey(p, c)


# id: (big canvas?, function, palette)
MONSTERS = {
    "ventisca": (False, ventisca, dict(main="#d8ecff", light="#ffffff", swirl="#a8d0f0", eye="#3a8ae0", flake="#ffffff")),
    "curi": (False, curi, dict(main="#c8b8a0", dark="#7a6a58", light="#f0e8dc", ear="#d8a8a0", eye="#201010", ice="#c8f0ff")),
    "aguila": (False, aguila, dict(main="#6a5a48", belly="#e8dcc8", head="#5a4a3a", wing="#4a3a2c", tail="#3a2e22", beak="#e8c040", eye="#e8c030")),
    "frailejonero": (True, frailejonero, dict(trunk="#5a4a3a", leaf="#a8b890", leaf2="#c8d4b0", eye="#ffd040")),
    "lagartija": (False, lagartija, dict(main="#8ac0d8", dark="#5a8aa8", light="#e0f4ff", crest="#e8f8ff", dewlap="#b0e0f0", eye="#2a4a8a", flake="#ffffff")),
    "pastorhelado": (True, pastorhelado, dict(staff="#6a5a48", pants="#4a5060", ruana="#6a7a9a", stripe="#c8d8f0", skin="#b8c8d8", beard="#f0f4ff", hat="#3a3a44", eye="#80d0ff", frost="#ffffff")),
    "venadoespectral": (True, venadoespectral, dict(main="#a8b8c8", dark="#788898", light="#e8f0f8", antler="#e0f0ff", spots=None, eye="#80f0ff", mist="#d8e8f8")),
    "piedrarueda": (False, piedrarueda, dict(main="#8a8680", moss="#6a8a4a", eye="#ffb040", dust="#a89a88")),
    "barbamusgo": (False, barbamusgo, dict(main="#6a8a4a", beard="#4a6a34", eye="#f0e040")),
    "colibrihelado": (False, colibrihelado, dict(main="#60b8d8", belly="#e0f8ff", head="#80d0e8", wing="#3a90b8", tail="#2a7898")),
    "bocachico": (False, bocachico, dict(main="#a0a8a0", belly="#e0e8e0", fin="#c06a4a", water="#6aa8c8")),
    "garzanegra": (False, garzanegra, dict(main="#3a3a40", wing="#2a2a30", plume="#5a5a64", leg="#c8a040", beak="#e8c040", eye="#ff3a2a")),
    "anguila": (False, anguila, dict(main="#4a5a4a", eye="#f0e040", spark="#a0f0ff", dot="#d8e870")),
    "tortugamordedora": (False, tortugamordedora, dict(main="#4a4a30", mark="#6a6a40", rim="#2a2a1a", skin="#6a6a4a")),
    "zancudos": (False, zancudos, dict(main="#3a2e2a", wing="#c8d8e0", eye="#ff3a2a")),
    "raya": (False, raya, dict(main="#8a7a5a", spot="#e8c070", barb="#e8e0c8", eye="#f0d040")),
    "ranatoro": (False, ranatoro, dict(main="#5a7a34", dark="#3a5020", belly="#d8d098", eye="#e8c030")),
    "hombrelodo": (True, hombrelodo, dict(main="#6a5038", dark="#4a3626", eye="#f0c040")),
    "chiguirorabioso": (True, chiguirorabioso, dict(main="#7a5434", dark="#4a3420")),
    "liriocarnivoro": (False, liriocarnivoro, dict(stem="#3a7a3a", leaf="#4a9a4a", petal="#d070a8", drool="#c0f0a0")),
    "jaguarsombra": (True, jaguarsombra, dict(main="#2e2a36", dark="#1e1a24", light="#46404e", mark="#14121a", eye="#a0ff60", glow="#d0ff80", smoke="#3a3444")),
    "conga": (False, conga, dict(main="#2a1e18", leg="#3a2a20", jaw="#7a3a1a", eye="#e8c040", sting="#c0a060")),
    "tarantula": (False, tarantula, dict(main="#4a3428", leg="#3a2a20", eye="#ff3a2a", hair="#c88a5a", skirt="#e06a8a")),
    "escorpion": (False, escorpion, dict(main="#2a2428", leg="#3a3438", sting="#c03a2a", eye="#ff4a2a")),
    "boa": (False, boa, dict(main="#9a8a5a", dark="#7a6a40", mark="#4a3a20", eye="#e8c030")),
    "maicero": (False, maicero, dict(main="#5a4232", dark="#3a2a20", face="#e8d0b0", corn="#f0c840")),
    "ranaveneno": (False, ranaveneno, dict(main="#f0c820", spot="#1a1a1a", drip="#80f060")),
    "guacharaca": (False, guacharaca, dict(main="#7a5a3a", belly="#b09068", head="#6a4a2e", wing="#5a4028", tail="#4a3420", throat="#d03a2a", eye="#ff3a2a")),
    "liana": (True, liana, dict(vine="#3a6a2a", leaf="#5a9a3a", eye="#ffe040", flower="#e04a8a")),
    "chamanperdido": (True, chamanperdido, dict(staff="#5a3a20", smoke="#a8a0b8", skin="#8a6048", robe="#5a3a6a", band="#e0b040", feathers=["#e03a2a", "#f0c030", "#2a8ae0", "#3ac060", "#e03a2a", "#f0c030", "#2a8ae0"], paint="#d02a2a", eye="#c080ff", beads="#f0f0e0")),
    "torocandela": (True, torocandela, dict(main="#3a1e18", dark="#24120e", muzzle="#5a2a20", horn="#f0c040", flame="#f07a1a", flame2="#fff0a0")),
    "garrapata": (False, garrapata, dict(main="#6a3a3a", head="#4a2a2a", leg="#3a2020")),
    "cimarron": (True, cimarron, dict(main="#6a4a30", dark="#4a3020", light="#c8a878", mane="#2a1e14", eye="#ff3a2a", dust="#c8a870")),
    "halconfuego": (False, halconfuego, dict(main="#c05a20", belly="#f0b060", head="#a04a18", wing="#8a3a14", tail="#a04a18", beak="#f0e0a0", flame="#f8a020", eye="#fff0a0")),
    "espantosabana": (True, espantosabana, dict(sheet="#e8e0c8", hat="#c8a860", band="#5a3a20", eye="#ff5a2a")),
    "iguanafuego": (False, iguanafuego, dict(main="#c0501a", dark="#8a3410", spot="#f8d040", flame="#f8a020", flame2="#ffffff", eye="#fff0a0")),
    "remolino": (True, remolino, dict(main="#c8a870", light="#e0c890", debris="#6a8a3a", debris2="#5a4030", eye="#ff6a2a")),
    "coplero": (True, coplero, dict(bone="#e0d8c0", shirt="#e8e4dc", sash="#c02a2a", wood="#8a5a2a", hat="#c8a860", eye="#80a0ff", note="#c8b8ff")),
    "armadillobrasa": (False, armadillobrasa, dict(main="#4a2a1e", skin="#8a4a2a", lava="#f06a1a")),
    "cascabel": (False, cascabel, dict(main="#a08a5a", mark="#5a4428", rattle="#d8c8a0", eye="#e8c030")),
    "gargola": (False, gargola, dict(main="#7a7a80", wing="#5a5a60", eye="#ff4a2a")),
    "calavera": (False, calavera, dict(bone="#e0d8c0", eye="#a0ff80", dust="#a89a88")),
    "idolo": (True, idolo, dict(main="#9a8a6a", eye="#ff8a2a", moss="#5a7a3a")),
    "tunjomaldito": (False, tunjomaldito, dict(main="#a8801a", dark="#5a3a0a", glint="#ff4a2a", glint2="#ffa070")),
    "sacerdotehueso": (True, sacerdotehueso, dict(staff="#4a3a2a", bone="#d8d0b8", robe="#3a2a3a", trim="#a08a3a", eye="#80ffd0")),
    "serpientepiedra": (False, serpientepiedra, dict(main="#8a8478", eye="#ff6a2a", moss="#5a7a3a")),
    "aranatumba": (False, aranatumba, dict(main="#3a3440", leg="#2a2430", eye="#ff3a2a", mark="#e0d8c0", web="#c8c8d0")),
    "guerreroespectro": (True, guerreroespectro, dict(main="#7aa0b0", spear="#5a4a3a", tip="#d0d8e0", band="#e0c060", shield="#5a7a8a", feather="#c0e8f8", eye="#ffffff", mist="#a8d0e0")),
    "ratatumba": (False, ratatumba, dict(main="#5a5048", dark="#3a3028", tail="#c8a0a0", ear="#c8a0a0")),
    "ojocripta": (False, ojocripta, dict(flesh="#9a4a6a", iris="#e0a020")),
    "mariquita": (False, mariquita, dict(main="#e03a2a")),
    "polilla": (False, polilla, dict(wing="#c8b898", body="#6a5a48", eye="#5a4a3a")),
    "pajarito": (False, pajarito, dict(main="#d8a050", belly="#f0e0b0", head="#c89040", wing="#a87030", tail="#8a5a28", beak="#e88a30", eye="#111")),
    "caracol": (False, caracol, dict(body="#c8b8a0", shell="#b07a4a")),
    "cangrejito": (False, cangrejito, dict(main="#e07040", claw="#f08a50", leg="#c05a30", eye="#111")),
    "pececito": (False, pececito, dict(main="#f0a030", fin="#f08a20", stripe="#ffffff")),
    "gusanito": (False, gusanito, dict(main="#a0c060")),
    "abejita": (False, abejita, dict(main="#f0c030")),
    "hongo": (False, hongo, dict(stem="#f0e8d8", cap="#d04a3a")),
    "grillo": (False, grillo, dict(main="#6a8a3a")),
    "lagartijita": (False, lagartijita, dict(main="#80b050", dark="#5a8a34", light="#d0e8a8", crest="#5a8a34", dewlap="#e0e070", eye="#201010")),
    "pollito": (False, pollito, dict(main="#f8e060", leg="#e88a30")),
    "ratoncito": (False, ratoncito, dict(main="#a09080", tail="#e0b0b0", ear="#e0b0b0")),
    "erizo": (False, erizo, dict(main="#8a7060", dark="#5a4838", quill="#c8b098", tip="#4a3a2a", face="#c8a888", nose="#2a2020")),
    "hormiguita": (False, hormiguita, dict(main="#6a2a20", leg="#4a1e18")),
    "tortuguita": (False, tortuguita, dict(main="#5a8a4a", mark="#a0d080", rim="#3a6a2a", skin="#a0c080")),
}
SMALL = {"mariquita", "polilla", "pajarito", "caracol", "cangrejito", "pececito", "gusanito", "abejita", "hongo", "grillo", "lagartijita", "pollito",
         "ratoncito", "erizo", "hormiguita", "tortuguita"}


def build(mid):
    big, fn, pal = MONSTERS[mid]
    p = Pic(MW, MH) if big else Pic(PW, PH)
    fn(p, pal)
    im = p.render()
    im = im.crop(im.getbbox()).transpose(Image.FLIP_LEFT_RIGHT)
    os.makedirs(OUT, exist_ok=True)
    im.save(os.path.join(OUT, f"{mid}.png"))
    return im


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sheet = sys.argv[sys.argv.index("--sheet") + 1] if "--sheet" in sys.argv else None
    if sheet in args:
        args.remove(sheet)
    made = [(m, build(m)) for m in (args or MONSTERS)]
    print(len(made), "monsters")
    if sheet:
        k, cols, cw, chh = 3, 10, 70 * 3, 66 * 3
        rows = (len(made) + cols - 1) // cols
        sh = Image.new("RGBA", (cols * cw, rows * chh), (58, 52, 44, 255))
        for i, (_, im) in enumerate(made):
            b = im.resize((im.width * k, im.height * k), Image.NEAREST)
            sh.alpha_composite(b, ((i % cols) * cw + (cw - b.width) // 2, (i // cols) * chh + chh - b.height - 4))
        sh.save(sheet)


if __name__ == "__main__":
    main()
