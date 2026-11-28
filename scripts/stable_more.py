"""The stable's levels 21-40 (2026-11-27): twenty more pets and twenty more mounts, drawn the same way as
the first twenty in build_stable.py (flat shapes, shaded and outlined by Pic). build_stable imports this
and adds them to SPECIES_PET and SPECIES_MOUNT.
"""
import math

from build_stable import G, MG, Pic, bird, cat, cat_mount, dk, lt, m_venado, mix, quad  # noqa: F401


# ---------------------------------------------------------------- pets (52x40, ground G)
def d_iguana(p, c):
    by = G - 5
    p.curve([(15, by + 1), (9, by + 3), (4, by + 2), (1, by - 2)], 4.5, c["main"], taper=0.25)
    for x in (4, 8, 12):
        p.line([(x, by + 1), (x, by + 3)], c["dark"])
    for lx in (18, 31):
        p.limb(lx, by + 2, lx + 2, G, 2.4, c["dark"])
    p.ell(24, by, 10, 4.5, c["main"])
    for lx in (16, 29):
        p.limb(lx, by + 2, lx - 1, G, 2.6, c["main"], foot=c["dark"])
    for x in range(15, 34, 3):
        p.poly([(x - 1.2, by - 4), (x, by - 7), (x + 1.2, by - 4)], c["crest"], shade=False)
    p.ell(36, by - 3, 5, 3.6, c["main"])
    p.poly([(38, by - 2), (42, by - 1.5), (41, by + 0.5), (37, by + 1)], c["main"])
    p.poly([(33, by), (38, by), (35.5, by + 5)], c["dewlap"])
    p.ell(35, by - 1, 1.3, 1.3, c["light"], shade=False)
    p.px(37, by - 4, c["eye"])


def d_murcielago(p, c):
    bx, by = 26, G - 16
    for s in (-1, 1):
        pts = [(bx, by - 1), (bx + s * 6, by - 7), (bx + s * 14, by - 9), (bx + s * 22, by - 4), (bx + s * 19, by - 1),
               (bx + s * 16, by + 3), (bx + s * 12, by), (bx + s * 9, by + 4), (bx + s * 5, by + 1), (bx, by + 4)]
        p.poly(pts, c["wing"])
        for k in (8, 14, 19):
            p.line([(bx + s * 3, by - 1), (bx + s * k, by - (6 if k < 19 else 3))], c["bone"])
    p.ell(bx, by + 1, 4, 5.5, c["main"])
    p.ell(bx, by - 5, 3.6, 3.2, c["main"])
    for s in (-1, 1):
        p.poly([(bx + s * 1, by - 7), (bx + s * 3.5, by - 12), (bx + s * 3.5, by - 6)], c["main"])
    p.px(bx - 1.5, by - 5, c["eye"]); p.px(bx + 1.5, by - 5, c["eye"])
    p.px(bx, by - 3, c["nose"])
    for (x, y) in ((bx - 3, by + 7), (bx + 3, by + 7)):
        p.ell(x, y, 1.5, 1.8, c["fruit"])
    p.line([(bx - 1, by + 6), (bx - 3, by + 6)], c["main"])


def d_morpho(p, c):
    bx, by = 26, G - 14
    for s in (-1, 1):
        p.poly([(bx, by - 1), (bx + s * 6, by - 13), (bx + s * 17, by - 15), (bx + s * 20, by - 8), (bx + s * 14, by)], c["wing"])
        p.poly([(bx, by + 1), (bx + s * 13, by + 1), (bx + s * 16, by + 8), (bx + s * 9, by + 13), (bx + s * 3, by + 9)], c["wing2"])
        p.poly([(bx + s * 15, by - 14), (bx + s * 20, by - 8), (bx + s * 18, by - 7), (bx + s * 14, by - 12)], c["edge"], shade=False)
        p.ell(bx + s * 10, by - 7, 3, 2.4, c["shine"], shade=False)
        p.ell(bx + s * 11, by + 6, 1.6, 1.6, c["edge"], shade=False)
        p.px(bx + s * 11, by + 6, c["eye"])
    p.ell(bx, by, 1.6, 8, c["body"])
    p.ell(bx, by - 8, 1.8, 1.8, c["body"])
    p.line([(bx - 1, by - 9), (bx - 4, by - 15)], c["body"])
    p.line([(bx + 1, by - 9), (bx + 4, by - 15)], c["body"])


def d_cusumbo(p, c):
    bx, by = 22, G - 8
    tail = [(bx - 8, by - 1), (bx - 12, by - 8), (bx - 12, by - 16), (bx - 9, by - 22)]
    p.curve(tail, 4.5, c["main"], taper=0.6)
    for k in range(5):
        t = (k + 0.5) / 5
        i = min(2, int(t * 3))
        a, b = tail[i], tail[i + 1]
        u = t * 3 - i
        x, y = a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u
        p.ell(x, y, 2.2, 1, c["ring"], shade=False)
    for lx in (bx - 4, bx + 6):
        p.limb(lx, by + 2, lx + 1, G, 3, c["dark"])
    p.ell(bx, by, 10, 5.5, c["main"])
    for lx in (bx - 6, bx + 4):
        p.limb(lx, by + 2, lx - 1, G, 3.2, c["main"], foot=c["dark"])
    hx, hy = bx + 11, by - 3
    p.ell(hx, hy, 4.5, 4, c["main"])
    p.poly([(hx + 2, hy - 1.5), (hx + 11, hy + 1.5), (hx + 10.5, hy + 3), (hx + 2, hy + 3)], c["main"])
    p.ell(hx + 1, hy + 1, 2.6, 1.5, c["light"], shade=False)
    p.px(hx + 11, hy + 2, "#201818")
    p.poly([(hx - 3, hy - 2), (hx - 3, hy - 6), (hx, hy - 3.5)], c["main"])
    p.px(hx + 1, hy - 1.5, c["eye"])


def d_barranquero(p, c):
    bx, by = 24, G - 13
    p.line([(bx - 4, by + 4), (bx - 9, by + 17)], c["tail"], 1)
    p.ell(bx - 9.5, by + 17, 1.8, 2.4, c["tip"])
    p.line([(bx - 3, by + 4), (bx - 6, by + 18)], c["tail"], 1)
    p.ell(bx - 6.5, by + 18.5, 1.6, 2.2, c["tip"])
    hx, hy = bird(p, c, bx, by, 1.0, tail=4)
    p.poly([(hx + 3, hy - 1), (hx + 8, hy + 0.5), (hx + 3, hy + 1.5)], "#2a2a2a")
    p.poly([(hx - 3, hy - 0.5), (hx + 3.5, hy - 0.5), (hx + 3, hy + 1.2), (hx - 3, hy + 1.2)], c["mask"], shade=False)
    p.line([(hx - 3, hy - 3), (hx + 2, hy - 3.5)], c["crown"], 1)
    p.px(hx + 1.5, hy, c["eye"])


def d_aullador(p, c):
    bx, by = 24, G - 9
    p.curve([(bx - 6, by + 5), (bx - 13, by + 6), (bx - 16, by), (bx - 13, by - 5), (bx - 10, by - 3)], 2.6, c["main"], taper=0.7)
    p.ell(bx, by + 1, 7.5, 8, c["main"])
    for lx in (bx - 4, bx + 4):
        p.limb(lx, by + 6, lx, G, 3, c["dark"])
        p.ell(lx + 1, G, 2, 1, c["dark"])
    p.limb(bx + 5, by - 3, bx + 9, by + 5, 2.6, c["main"])
    p.limb(bx - 5, by - 3, bx - 8, by + 5, 2.6, c["dark"])
    hx, hy = bx + 1, by - 9
    p.ell(hx, hy, 5, 4.6, c["main"])
    p.ell(hx + 1, hy + 4, 4, 3.2, c["beard"])
    p.ell(hx + 1.5, hy + 0.5, 3, 2.4, c["face"], shade=False)
    p.px(hx, hy - 0.5, "#111"); p.px(hx + 3, hy - 0.5, "#111")
    p.line([(hx + 0.5, hy + 2), (hx + 2.5, hy + 2)], "#3a1a1a")


def d_carey(p, c):
    bx, by = 26, G - 7
    p.poly([(bx + 7, by + 2), (bx + 18, by + 6), (bx + 16, by + 8), (bx + 6, by + 5)], c["skin"])
    p.poly([(bx - 9, by + 2), (bx - 14, by + 7), (bx - 11, by + 8), (bx - 6, by + 4)], c["skin"])
    p.ell(bx, by, 13, 7, c["main"])
    for (x, y) in ((-7, -2), (-1, -4), (5, -2), (-4, 2), (2, 2), (8, 2), (-10, 1)):
        p.poly([(bx + x - 2.5, by + y), (bx + x, by + y - 2), (bx + x + 2.5, by + y), (bx + x, by + y + 2)], c["mark"], shade=False)
    p.poly([(bx - 13, by + 2), (bx + 13, by + 2), (bx + 11, by + 4), (bx - 11, by + 4)], c["rim"])
    p.ell(bx + 15, by - 1, 4, 3, c["skin"])
    p.poly([(bx + 17, by - 1.5), (bx + 20, by + 0.5), (bx + 17, by + 1.5)], dk(c["skin"], 0.3))
    p.px(bx + 16, by - 2, "#111")
    p.poly([(bx + 6, by + 5), (bx + 12, by + 10), (bx + 9, by + 11), (bx + 4, by + 6)], dk(c["skin"], 0.1))


def d_tigrillo(p, c):
    cat(p, c, spots=c["mark"], big=1.1)
    p.px(31, G - 19, c["light"]); p.px(32, G - 19, c["light"])


def d_gallito(p, c):
    hx, hy = bird(p, c, 24, G - 11, 1.15, tail=6)
    p.ell(hx + 0.5, hy - 2.5, 4.5, 5, c["head"])
    p.ell(hx + 2.5, hy - 2, 2.2, 3.5, lt(c["head"], 0.15), shade=False)
    p.px(hx + 2, hy - 0.5, c["eye"])
    p.poly([(hx + 4.5, hy + 0.5), (hx + 6, hy + 1.5), (hx + 4.5, hy + 2)], c["beak"])


def d_marteja(p, c):
    bx, by = 22, G - 9
    p.curve([(bx - 4, by + 5), (bx - 10, by + 8), (bx - 17, by + 6), (bx - 20, by + 1)], 2.4, c["dark"], taper=0.8)
    p.ell(bx, by + 1, 7, 7, c["main"])
    p.ell(bx + 1, by + 3, 4, 4.5, c["belly"], shade=False)
    for lx in (bx - 3, bx + 4):
        p.limb(lx, by + 6, lx, G, 2.6, c["dark"])
    hx, hy = bx + 2, by - 8
    p.ell(hx, hy, 5.5, 5, c["main"])
    for ex in (hx - 2.2, hx + 2.2):
        p.ell(ex, hy - 0.5, 2.2, 2.2, c["mask"], shade=False)
        p.ell(ex, hy - 0.5, 1.5, 1.5, c["eye"], shade=False)
        p.px(ex, hy - 0.5, "#111")
    p.line([(hx - 4, hy - 4), (hx + 4, hy - 4)], c["dark"])
    p.px(hx, hy + 2, "#3a2020")


def d_cangrejo(p, c):
    bx, by = 26, G - 7
    for s in (-1, 1):
        for k in range(3):
            x0 = bx + s * (4 + k * 2.5)
            p.line([(x0, by + 1), (x0 + s * 4, by + 3), (x0 + s * 5, G)], c["leg"], 1)
        p.line([(bx + s * 6, by - 2), (bx + s * 11, by - 8)], c["leg"], 2)
        cx, cy = bx + s * 13, by - 10
        p.ell(cx, cy, 4.2, 3.4, c["claw"])
        p.poly([(cx + s * 1, cy - 2.5), (cx + s * 6, cy - 4.5), (cx + s * 3, cy - 0.5)], c["claw"])
        p.px(cx + s * 2, cy - 1, dk(c["claw"], 0.4))
    p.ell(bx, by, 9, 5.5, c["main"])
    p.ell(bx, by - 2, 6, 2, lt(c["main"], 0.15), shade=False)
    for s in (-1, 1):
        p.line([(bx + s * 2.5, by - 4), (bx + s * 3, by - 8)], c["main"], 1)
        p.ell(bx + s * 3, by - 8.5, 1.2, 1.2, c["eye"], shade=False)
        p.px(bx + s * 3, by - 8.5, "#111")


def d_puercoespin(p, c):
    bx, by = 24, G - 7
    for lx in (bx - 5, bx + 5):
        p.limb(lx, by + 3, lx, G, 2.6, c["dark"])
    p.ell(bx, by, 11, 6.5, c["main"])
    for i, a in enumerate(range(150, 20, -9)):
        r = math.radians(a)
        x0, y0 = bx + math.cos(r) * 7, by - math.sin(r) * 4
        p.line([(x0, y0), (x0 + math.cos(r) * 7, y0 - math.sin(r) * 6)], c["quill"] if i % 2 else c["tip"], 1)
    p.ell(bx + 11, by + 1, 4, 3.3, c["face"])
    p.ell(bx + 14.5, by + 2, 1.6, 1.4, c["nose"])
    p.px(bx + 12, by, "#111")
    for lx in (bx - 7, bx + 3):
        p.limb(lx, by + 3, lx - 1, G, 2.8, c["face"], foot=dk(c["face"], 0.4))


def d_mapuro(p, c):
    bx, by = 22, G - 7
    p.curve([(bx - 8, by - 1), (bx - 14, by - 8), (bx - 12, by - 16), (bx - 6, by - 19)], 8, c["main"], taper=0.7)
    p.curve([(bx - 10, by - 4), (bx - 13, by - 10), (bx - 10, by - 16)], 3, c["stripe"], shade=False, taper=0.6)
    for lx in (bx - 5, bx + 5):
        p.limb(lx, by + 3, lx, G, 2.8, c["main"])
    p.ell(bx, by, 9.5, 6, c["main"])
    p.poly([(bx - 8, by - 4), (bx + 8, by - 6), (bx + 9, by - 4), (bx - 8, by - 2)], c["stripe"], shade=False)
    hx, hy = bx + 10, by - 2
    p.ell(hx, hy, 4.5, 4, c["main"])
    p.poly([(hx + 2, hy), (hx + 7, hy + 2), (hx + 2, hy + 3)], c["main"])
    p.line([(hx - 2, hy - 3.5), (hx + 4, hy - 1)], c["stripe"], 1)
    p.px(hx + 1, hy - 1, c["eye"])
    p.px(hx + 7, hy + 2, "#e8a0a0")


def d_ulama(p, c):
    bx, by = 22, G - 7
    p.curve([(bx - 10, by), (bx - 16, by + 3), (bx - 21, by + 1)], 4, c["main"], taper=0.6)
    for lx in (bx - 7, bx + 6):
        p.limb(lx, by + 2, lx + 1, G, 2.8, c["dark"])
    p.ell(bx, by, 12, 5, c["main"])
    for lx in (bx - 9, bx + 4):
        p.limb(lx, by + 2, lx - 1, G, 3, c["main"], foot=c["dark"])
    hx, hy = bx + 13, by - 4
    p.poly([(bx + 8, by - 3), (hx, hy - 3), (hx + 1, hy + 3), (bx + 9, by + 3)], c["head"])
    p.ell(hx, hy, 4.5, 3.8, c["head"])
    p.poly([(hx + 2, hy - 1), (hx + 7, hy + 1), (hx + 2, hy + 2.5)], c["head"])
    p.ell(hx - 2, hy - 3.5, 1.5, 1.5, c["head"])
    p.ell(bx + 8, by + 2, 2, 2, c["throat"], shade=False)
    p.px(hx + 1, hy - 1, c["eye"])
    p.px(hx + 7, hy + 1, "#111")


def d_paujil(p, c):
    hx, hy = bird(p, c, 22, G - 12, 1.3, tail=10)
    for k in range(4):
        x = hx - 3 + k * 1.6
        p.line([(x, hy - 3), (x - 1, hy - 7)], c["crest"], 1)
        p.px(x - 1.5, hy - 7.5, c["crest"])
    p.poly([(hx + 3.5, hy - 1.5), (hx + 7.5, hy + 0.5), (hx + 3.5, hy + 2)], c["beak"])
    p.ell(hx + 4, hy - 2.5, 1.6, 1.4, c["knob"])
    p.px(hx + 1.5, hy - 0.5, c["eye"])
    p.ell(18, G - 4, 3, 2, c["vent"], shade=False)


def d_tunjo(p, c):
    bx = 26
    top = G - 26
    p.poly([(bx - 6, top + 7), (bx + 6, top + 7), (bx + 5, G - 6), (bx - 5, G - 6)], c["main"])
    p.ell(bx, top + 3, 4.5, 4.5, c["main"])
    p.poly([(bx - 6, top - 2), (bx + 6, top - 2), (bx + 5, top + 1), (bx - 5, top + 1)], c["dark"])
    for k in range(-5, 6, 2):
        p.line([(bx + k, top - 2), (bx + k, top - 5)], c["main"], 1)
    p.line([(bx - 6, top + 9), (bx - 10, top + 16)], c["main"], 2)
    p.line([(bx + 6, top + 9), (bx + 10, top + 16)], c["main"], 2)
    p.ell(bx + 10.5, top + 16.5, 2, 2, c["dark"])
    for lx in (bx - 3, bx + 3):
        p.line([(lx, G - 6), (lx, G)], c["main"], 2)
        p.line([(lx - 1, G), (lx + 2, G)], c["dark"], 1)
    p.line([(bx - 2, top + 3), (bx - 0.5, top + 3)], c["dark"]); p.line([(bx + 0.5, top + 3), (bx + 2, top + 3)], c["dark"])
    p.line([(bx - 1, top + 6), (bx + 1, top + 6)], c["dark"])
    for y in range(top + 10, G - 6, 3):
        p.line([(bx - 4, y), (bx + 4, y)], c["dark"])
    for (x, y) in ((bx - 9, top), (bx + 9, top + 3), (bx - 12, top + 12), (bx + 13, top + 8)):
        p.px(x, y, c["glint"])
        p.px(x + 1, y, c["glint2"]); p.px(x - 1, y, c["glint2"]); p.px(x, y + 1, c["glint2"]); p.px(x, y - 1, c["glint2"])


def d_cocuyo(p, c):
    bx, by = 26, G - 12
    for s in (-1, 1):
        for k in range(3):
            p.line([(bx + s * 2, by + 1 + k * 2), (bx + s * 7, by + 2 + k * 3), (bx + s * 9, G)], c["leg"], 1)
        p.poly([(bx, by - 4), (bx + s * 9, by - 12), (bx + s * 14, by - 8), (bx + s * 6, by)], c["wing"], shade=False)
    p.ell(bx, by + 2, 5.5, 8, c["main"])
    p.line([(bx, by - 5), (bx, by + 10)], dk(c["main"], 0.4))
    p.ell(bx, by - 7, 4.5, 3.2, c["head"])
    for s in (-1, 1):
        p.ell(bx + s * 2.5, by - 8, 1.8, 1.5, c["lamp"], shade=False)
        p.px(bx + s * 2.5, by - 8, "#ffffff")
        p.line([(bx + s * 1.5, by - 10), (bx + s * 5, by - 15)], c["leg"], 1)
    p.ell(bx, by + 9, 3.5, 2.2, c["lamp"], shade=False)
    for (x, y) in ((bx - 14, by - 2), (bx + 15, by + 2), (bx - 10, G - 2), (bx + 12, by - 14)):
        p.px(x, y, c["lamp"])


def d_salamandra(p, c):
    by = G - 5
    p.curve([(14, by), (8, by + 2), (3, by), (1, by - 4)], 4.5, c["main"], taper=0.3)
    for lx in (18, 31):
        p.limb(lx, by + 1, lx + 3, G, 2.4, c["dark"])
    p.ell(24, by - 1, 10, 4.2, c["main"])
    for lx in (16, 29):
        p.limb(lx, by + 1, lx - 2, G, 2.6, c["main"], foot=c["dark"])
    for (x, y) in ((17, by - 2), (22, by - 1), (27, by - 2), (31, by - 1), (8, by + 1)):
        p.ell(x, y, 1.6, 1.2, c["spot"], shade=False)
    for x in range(13, 34, 3):
        h = 4 + (x % 2) * 2
        p.poly([(x - 1.5, by - 4), (x, by - 4 - h), (x + 1.5, by - 4)], c["flame"], shade=False)
        p.px(x, by - 5, c["flame2"])
    p.ell(36, by - 2, 5, 3.4, c["main"])
    p.poly([(38, by - 3), (42, by - 1.5), (38, by + 0.5)], c["main"])
    p.px(37, by - 3, c["eye"])


def d_garza(p, c):
    bx, by = 22, G - 14
    for lx in (bx - 1, bx + 2):
        p.line([(lx, by + 5), (lx, G)], c["leg"], 1)
        p.line([(lx, G), (lx + 2.5, G)], c["leg"])
    p.poly([(bx - 6, by + 1), (bx - 15, by + 5), (bx - 5, by + 6)], c["plume"])
    p.ell(bx, by + 1, 7, 5, c["main"])
    p.poly([(bx - 6, by - 1), (bx + 3, by - 2), (bx + 1, by + 5), (bx - 6, by + 4)], c["wing"])
    p.curve([(bx + 5, by - 1), (bx + 9, by - 6), (bx + 6, by - 11), (bx + 9, by - 16)], 2.6, c["main"], taper=0.8)
    p.ell(bx + 10, by - 17, 3, 2.5, c["main"])
    p.poly([(bx + 12, by - 18), (bx + 21, by - 16.5), (bx + 12, by - 15.5)], c["beak"])
    p.line([(bx + 9, by - 19), (bx + 3, by - 20)], c["plume"], 1)
    p.px(bx + 11, by - 17.5, c["eye"])


def d_frailejoncito(p, c):
    bx = 26
    for lx in (bx - 3, bx + 3):
        p.limb(lx, G - 6, lx + (1 if lx > bx else -1), G, 2.4, c["trunk"], foot=dk(c["trunk"], 0.4))
    p.poly([(bx - 5, G - 14), (bx + 5, G - 14), (bx + 4, G - 5), (bx - 4, G - 5)], c["trunk"])
    for k in range(4):
        p.line([(bx - 4, G - 13 + k * 2.4), (bx + 4, G - 12 + k * 2.4)], dk(c["trunk"], 0.3))
    cy = G - 19
    for i, a in enumerate(range(0, 360, 30)):
        r = math.radians(a)
        p.poly([(bx, cy), (bx + math.cos(r - 0.25) * 11, cy + math.sin(r - 0.25) * 7), (bx + math.cos(r) * 13, cy + math.sin(r) * 8),
                (bx + math.cos(r + 0.25) * 11, cy + math.sin(r + 0.25) * 7)], c["leaf"] if i % 2 else c["leaf2"])
    p.ell(bx, cy, 6.5, 4.5, c["leaf2"])
    for s in (-1, 1):
        p.ell(bx + s * 2.6, cy - 0.5, 1.5, 1.7, "#ffffff", shade=False)
        p.px(bx + s * 2.6, cy, "#111")
    for (x, y) in ((bx - 6, cy - 9), (bx + 2, cy - 11), (bx + 9, cy - 8)):
        p.line([(bx, cy - 3), (x, y)], c["stem"], 1)
        p.ell(x, y, 1.8, 1.6, c["flower"], shade=False)
        p.px(x, y, dk(c["flower"], 0.4))


PETS_MORE = {
    "iguana": (d_iguana, {
        "verde": dict(main="#5a9a3a", dark="#3a6a24", light="#b8d890", crest="#3a6a24", dewlap="#c8d070", eye="#c03020"),
        "naranja": dict(main="#d8803a", dark="#9a5424", light="#f0c890", crest="#7a3a1a", dewlap="#f0d060", eye="#2a1a10"),
        "azul": dict(main="#5a7ab0", dark="#3a5080", light="#c0d0f0", crest="#2a3a60", dewlap="#a0e0e0", eye="#e8c030"),
    }),
    "murcielago": (d_murcielago, {
        "pardo": dict(main="#6a4a3a", wing="#4a3428", bone="#8a6a54", eye="#f0d040", nose="#2a1a14", fruit="#e0802a"),
        "negro": dict(main="#2e2a30", wing="#221e24", bone="#4a4450", eye="#ff5a3a", nose="#111", fruit="#c02a4a"),
        "blanco": dict(main="#f0ece4", wing="#c8c0b8", bone="#e8e0d8", eye="#c03040", nose="#d08080", fruit="#f0c030"),
    }),
    "morpho": (d_morpho, {
        "azul": dict(wing="#2a70e8", wing2="#1a50c0", edge="#1a1a2a", shine="#a0d8ff", eye="#f0e0a0", body="#2a2420"),
        "verde": dict(wing="#2ab870", wing2="#1a8a50", edge="#14241a", shine="#b0ffd0", eye="#f0e0a0", body="#2a2420"),
        "blanco": dict(wing="#f0f4f8", wing2="#c8d8e8", edge="#5a6a8a", shine="#ffffff", eye="#2a5ae0", body="#3a3a4a"),
    }),
    "cusumbo": (d_cusumbo, {
        "pardo": dict(main="#8a6040", dark="#5a3e28", light="#e8d4b8", ring="#4a3020", eye="#201010"),
        "rojizo": dict(main="#b0603a", dark="#7a4028", light="#f0d8c0", ring="#5a2a18", eye="#201010"),
        "gris": dict(main="#8a8680", dark="#5a5650", light="#ece8e0", ring="#4a4640", eye="#201010"),
    }),
    "barranquero": (d_barranquero, {
        "verde": dict(main="#3a9a5a", belly="#a8d070", head="#3aa060", wing="#2a7a48", tail="#2a6a8a", tip="#1a3a5a", mask="#1a1a20", crown="#5ad0ff", eye="#d03020"),
        "azul": dict(main="#2a6ab0", belly="#80c0e0", head="#3a80c8", wing="#1a4a8a", tail="#1a3a6a", tip="#0e1a3a", mask="#1a1a20", crown="#a0f0ff", eye="#d03020"),
        "canela": dict(main="#b07a3a", belly="#e0b070", head="#c08a40", wing="#8a5a2a", tail="#3a6a5a", tip="#1a3a2a", mask="#1a1a20", crown="#7af0c0", eye="#d03020"),
    }),
    "aullador": (d_aullador, {
        "rojo": dict(main="#a84a24", dark="#6a2a14", beard="#c8682a", face="#3a2a24"),
        "negro": dict(main="#2e2828", dark="#1a1616", beard="#4a3a30", face="#2a2020"),
        "dorado": dict(main="#c8902a", dark="#8a5a1a", beard="#e8b040", face="#4a3020"),
    }),
    "carey": (d_carey, {
        "carey": dict(main="#8a5a2a", mark="#d8a040", rim="#5a3a1a", skin="#7a8a6a"),
        "verde": dict(main="#4a6a3a", mark="#a8c070", rim="#2a4a24", skin="#8a9a7a"),
        "oscura": dict(main="#3a3430", mark="#8a7a60", rim="#221e1a", skin="#6a6a5a"),
    }),
    "tigrillo": (d_tigrillo, {
        "dorado": dict(main="#d8a84a", dark="#a07830", light="#f4e8cc", mark="#3a2412", ear="#d89a8a", eye="#a0c040"),
        "gris": dict(main="#a8a498", dark="#7a766c", light="#ece8e0", mark="#3a3630", ear="#c8a0a0", eye="#c8b040"),
        "rojizo": dict(main="#c87a3a", dark="#8a5024", light="#f0dcc0", mark="#3a1a0a", ear="#d89a8a", eye="#a0c040"),
    }),
    "gallito": (d_gallito, {
        "naranja": dict(main="#f07a1a", belly="#f8a040", head="#f08020", wing="#1e1a1a", tail="#2a2020", eye="#f8f0a0", beak="#e8c030"),
        "rojo": dict(main="#d02a1a", belly="#f05a30", head="#e03a1a", wing="#1e1a1a", tail="#2a2020", eye="#f8f0a0", beak="#e8c030"),
        "dorado": dict(main="#e8b020", belly="#f8d860", head="#f0c030", wing="#2a2418", tail="#3a3020", eye="#3a1a10", beak="#f0e0a0"),
    }),
    "marteja": (d_marteja, {
        "gris": dict(main="#8a8478", dark="#5a564e", belly="#d8c098", mask="#f0ece0", eye="#e8a030"),
        "parda": dict(main="#8a6a4a", dark="#5a4430", belly="#e0b880", mask="#f0e4d0", eye="#e8a030"),
        "oscura": dict(main="#4a4440", dark="#2a2624", belly="#c89a6a", mask="#e8e0d0", eye="#f0c040"),
    }),
    "cangrejo": (d_cangrejo, {
        "negro": dict(main="#2a2a30", claw="#3a3440", leg="#e04a3a", eye="#f0c040"),
        "azul": dict(main="#2a5ab0", claw="#e8e0d0", leg="#3a6ac0", eye="#111"),
        "rojo": dict(main="#d03a2a", claw="#e05a3a", leg="#b02a1a", eye="#111"),
    }),
    "puercoespin": (d_puercoespin, {
        "pardo": dict(main="#6a5040", dark="#4a3628", quill="#d8c8a8", tip="#3a2a20", face="#8a6a50", nose="#d0a090"),
        "gris": dict(main="#6a6660", dark="#4a4640", quill="#e8e4dc", tip="#2a2824", face="#8a8478", nose="#c8a0a0"),
        "rubio": dict(main="#a88a5a", dark="#7a6040", quill="#f8f0d8", tip="#8a6a3a", face="#c0a070", nose="#e0a8a0"),
    }),
    "mapuro": (d_mapuro, {
        "negro": dict(main="#1e1c20", stripe="#f0ece4", eye="#e8c030"),
        "pardo": dict(main="#3a2a20", stripe="#f0e0c8", eye="#e8c030"),
        "luna": dict(main="#2a2a48", stripe="#c8d8ff", eye="#a0e0ff"),
    }),
    "ulama": (d_ulama, {
        "negra": dict(main="#26221e", dark="#141210", head="#a8906a", throat="#e8d890", eye="#e8c030"),
        "parda": dict(main="#4a3424", dark="#2a1e14", head="#c8a878", throat="#f0e0a0", eye="#e8c030"),
        "gris": dict(main="#4a4a48", dark="#2a2a28", head="#d8d0c0", throat="#f0f0e0", eye="#e8c030"),
    }),
    "paujil": (d_paujil, {
        "negro": dict(main="#1e1c20", belly="#2a2830", head="#1e1c20", wing="#2a2830", tail="#141216", crest="#2a2830", beak="#e8c030", knob="#d02a2a", eye="#e8e0d0", vent="#f0ece4"),
        "picoazul": dict(main="#22202a", belly="#2e2c38", head="#22202a", wing="#2e2c38", tail="#141216", crest="#3a3848", beak="#4a7ad0", knob="#2a5ab0", eye="#f0e0a0", vent="#c87a3a"),
        "canelo": dict(main="#7a4a24", belly="#a86a34", head="#2a2020", wing="#5a3418", tail="#3a2010", crest="#2a2020", beak="#e8c030", knob="#e04a2a", eye="#f0e0a0", vent="#f0d8b0"),
    }),
    "tunjo": (d_tunjo, {
        "oro": dict(main="#e0b030", dark="#9a6a18", glint="#ffffff", glint2="#fff0a0"),
        "tumbaga": dict(main="#c87848", dark="#8a4a28", glint="#ffffff", glint2="#ffd0a0"),
        "esmeralda": dict(main="#d8b030", dark="#2a8a4a", glint="#ffffff", glint2="#a0ffc0"),
    }),
    "cocuyo": (d_cocuyo, {
        "verde": dict(main="#3a4a2a", head="#4a5a34", wing="#6a7a4a", leg="#2a2a1e", lamp="#b0ff60"),
        "dorado": dict(main="#5a4420", head="#6a5428", wing="#a08a4a", leg="#2a2214", lamp="#fff060"),
        "azul": dict(main="#22283a", head="#2e3448", wing="#4a5a7a", leg="#1a1a24", lamp="#80e0ff"),
    }),
    "salamandra": (d_salamandra, {
        "brasa": dict(main="#2a2020", dark="#1a1414", spot="#f06020", flame="#f08020", flame2="#fff0a0", eye="#ffb030"),
        "fuego": dict(main="#c83a1a", dark="#8a2410", spot="#f8d040", flame="#f8a020", flame2="#ffffff", eye="#fff0a0"),
        "azul": dict(main="#1e2a5a", dark="#121a3a", spot="#60c0ff", flame="#60a0ff", flame2="#e8f8ff", eye="#ffffff"),
    }),
    "garza": (d_garza, {
        "plata": dict(main="#d8dce4", wing="#b0b8c8", plume="#f4f8ff", leg="#5a5a6a", beak="#e8c040", eye="#e8c040"),
        "blanca": dict(main="#f4f2ee", wing="#dcd8d0", plume="#ffffff", leg="#2a2a2a", beak="#f0c030", eye="#f0c030"),
        "azul": dict(main="#6a80b0", wing="#4a5a8a", plume="#c0d0f0", leg="#3a4050", beak="#e8d070", eye="#f0e040"),
    }),
    "frailejoncito": (d_frailejoncito, {
        "plata": dict(trunk="#5a4a3a", leaf="#b8c0a8", leaf2="#d8e0c8", stem="#6a7a4a", flower="#f0d030"),
        "dorado": dict(trunk="#5a4030", leaf="#c8b878", leaf2="#e8dca0", stem="#7a6a3a", flower="#fff0a0"),
        "niebla": dict(trunk="#4a4a50", leaf="#a8b8c0", leaf2="#d0e0e8", stem="#5a6a70", flower="#f0f4ff"),
    }),
}


# ---------------------------------------------------------------- mounts (64x61, back at y ~ 20, ground MG)
def m_cebu(p, c):
    p.curve([(6, 25), (3, 32), (3, 42)], 1.6, c["main"], taper=1)
    p.ell(3, 43, 1.6, 2.4, c["dark"])
    quad(p, c, body=(24, 32, 20, 12), leg=5, front=(36, 39), back=(11, 15), taper=0.6)
    p.ell(36, 21, 6, 6, c["main"])  # the hump
    p.poly([(38, 26), (48, 18), (53, 30), (44, 40), (40, 38)], c["main"])
    p.poly([(41, 34), (47, 30), (46, 44), (42, 42)], c["dewlap"])
    p.ell(51, 25, 4.5, 6.5, c["main"])
    p.ell(53, 31, 3.5, 2.6, c["muzzle"])
    p.poly([(47, 21), (44, 26), (42, 30), (46, 26)], c["dark"])
    p.poly([(49, 19), (50, 12), (52, 11), (51, 19)], c["horn"])
    p.px(52, 23, "#111")


def m_bufalo(p, c):
    p.curve([(6, 26), (3, 33), (3, 42)], 1.6, c["main"], taper=1)
    quad(p, c, body=(25, 32, 22, 13), leg=6, front=(37, 41), back=(11, 15), taper=0.65)
    p.poly([(39, 22), (51, 20), (55, 34), (44, 36)], c["main"])
    p.ell(52, 28, 5, 7, c["main"])
    p.ell(54, 34, 3.5, 2.6, c["muzzle"])
    p.curve([(48, 21), (42, 16), (36, 15), (32, 18)], 3.5, c["horn"], taper=0.4)
    p.curve([(52, 21), (58, 17), (61, 20)], 2.5, dk(c["horn"], 0.2), taper=0.4)
    p.px(53, 25, "#111")


def m_saino(p, c):
    quad(p, c, body=(26, 33, 22, 13), leg=4.6, front=(38, 41), back=(12, 15), taper=0.7)
    for x in range(10, 44, 3):
        p.poly([(x - 1.5, 21), (x, 15 + (x % 2) * 2), (x + 1.5, 21)], c["mane"])
    p.poly([(36, 24), (37, 42), (40, 42), (39, 24)], c["collar"], shade=False)
    p.poly([(42, 24), (56, 30), (61, 34), (60, 38), (46, 40)], c["main"])
    p.ell(60.5, 36, 2.5, 2.6, c["snout"])
    p.poly([(56, 38), (57, 42), (58, 38)], "#f0ece0")
    p.poly([(44, 22), (46, 17), (49, 23)], c["main"])
    p.px(51, 29, "#e04020")


def m_garzon(p, c):
    for lx in (22, 30):
        p.limb(lx, 38, lx + 1, MG, 2.6, c["leg"], shade=False)
        p.line([(lx - 2, MG), (lx + 4, MG)], c["leg"])
    p.poly([(9, 30), (1, 40), (5, 41), (13, 36)], c["tail"])
    p.ell(25, 30, 17, 10, c["main"])
    p.poly([(10, 24), (30, 21), (32, 31), (16, 38), (6, 33)], c["wing"])
    p.curve([(38, 26), (44, 18), (46, 10), (45, 4)], 5, c["neck"], taper=0.8)
    p.rect(39, 22, 45, 26, c["band"], shade=False)
    p.ell(46, 4, 4, 3.5, c["neck"])
    p.poly([(48, 2), (63, 7), (62, 9), (48, 6)], c["beak"])
    p.line([(49, 5), (62, 8)], lt(c["beak"], 0.25))
    p.px(46, 3, "#e8e0d0")


def m_anaconda(p, c):
    body = [(2, 52), (12, 46), (24, 50), (36, 42), (30, 30), (18, 26), (24, 18), (36, 22), (46, 24), (52, 18), (54, 12)]
    p.curve(body, 13, c["main"], taper=0.55)
    for (x, y) in body[1:-2]:
        p.ell(x - 2, y - 1, 2.6, 1.8, c["mark"], shade=False)
        p.ell(x + 3, y + 1, 1.8, 1.4, c["mark"], shade=False)
    p.ell(56, 11, 6, 4.2, c["main"])
    p.poly([(58, 10), (63, 12), (59, 14)], c["main"])
    p.px(57, 9, c["eye"])
    p.line([(62, 13), (64, 15)], "#d02a2a")
    p.ell(20, 24, 8, 3, c["belly"], shade=False)


def m_mulatres(p, c):
    p.curve([(6, 26), (2, 34), (3, 44)], 3.5, c["flame"], taper=0.5)
    cx, cy, rx, ry = 24, 29, 19, 9.5
    p.limb(15, cy + 2, 15.5, MG, 4.2, c["dark"], foot=c["hoof"])
    p.ell(cx, cy, rx, ry, c["main"])
    p.limb(12, cy + 2, 11.5, MG, 4.2, c["main"], foot=c["hoof"])
    p.limb(37, cy + 2, 38, MG, 4.6, c["main"], foot=c["hoof"])
    p.poly([(35, 25), (44, 10), (51, 12), (44, 32)], c["main"])
    for k in range(5):
        x, y = 37 + k * 2, 22 - k * 3
        p.poly([(x - 1, y + 2), (x - 4, y - 3), (x + 1, y)], c["flame"], shade=False)
    p.poly([(44, 8), (58, 14), (57, 19), (43, 17)], c["main"])
    p.poly([(44, 9), (42, 0), (45, 1), (47, 9)], c["main"])
    p.poly([(47, 9), (47, 0), (49.5, 1.5), (49, 10)], c["main"])
    p.px(50, 12, c["eye"]); p.px(51, 12, c["eye"])
    p.ell(57, 18, 1.6, 1.2, c["flame"], shade=False)
    for (x, y) in ((38, MG - 2), (40, MG - 4), (13, MG - 3)):
        p.px(x, y, c["flame2"])


def m_bufeo(p, c):
    p.ell(30, 54, 30, 6, c["water"], shade=False)
    for x in range(4, 60, 7):
        p.poly([(x, 50), (x + 3, 46), (x + 6, 50)], lt(c["water"], 0.3), shade=False)
    p.poly([(6, 34), (0, 26), (2, 36), (0, 44), (8, 40)], c["main"])
    p.curve([(8, 38), (18, 32), (30, 30), (42, 32)], 18, c["main"], taper=0.65)
    p.ell(46, 30, 7, 6, c["main"])
    p.poly([(51, 30), (63, 32), (63, 34), (51, 35)], c["main"])
    p.poly([(26, 22), (30, 17), (33, 23)], c["main"])
    p.poly([(28, 38), (24, 46), (32, 40)], dk(c["main"], 0.15))
    p.ell(30, 36, 14, 3, c["belly"], shade=False)
    p.px(49, 29, "#2a1a1a")
    for (x, y) in ((58, 44), (60, 40), (4, 46)):
        p.px(x, y, "#ffffff")


def m_pezoro(p, c):
    for (x, y, r) in ((20, 52, 2), (32, 56, 1.4), (44, 53, 1.8), (10, 56, 1.2)):
        p.ell(x, y, r, r, c["bubble"], shade=False)
        p.px(x - r * 0.4, y - r * 0.4, "#ffffff")
    p.poly([(10, 32), (0, 20), (3, 32), (0, 44)], c["fin"])
    p.ell(30, 32, 22, 13, c["main"])
    p.poly([(22, 20), (30, 9), (38, 13), (40, 21)], c["fin"])
    p.poly([(28, 42), (24, 50), (34, 44)], c["fin"])
    for y in range(24, 42, 4):
        for x in range(14 + (y % 8), 46, 6):
            p.line([(x, y), (x + 2, y + 2), (x + 4, y)], c["scale"])
    p.ell(48, 30, 3, 3, "#ffffff", shade=False)
    p.ell(48.5, 30, 1.8, 1.8, "#111", shade=False)
    p.poly([(51, 35), (54, 34), (53, 37)], dk(c["main"], 0.4))
    p.poly([(40, 30), (44, 26), (44, 36)], c["fin"])


def m_jaguaralado(p, c):
    for k, col in ((0, c["wing2"]), (1, c["wing"])):
        dx = -k * 4
        p.poly([(22 + dx, 22), (10 + dx, 2), (4 + dx, -1), (8 + dx, 8), (2 + dx, 10), (10 + dx, 16), (6 + dx, 20), (16 + dx, 24)], col)
        for i in range(3):
            p.line([(20 + dx, 22), (6 + dx + i * 2, 4 + i * 6)], dk(col, 0.25))
    cat_mount(p, c, rosettes=c["mark"])


def m_tortugamundo(p, c):
    p.curve([(48, 38), (54, 32), (58, 28)], 7, c["skin"])
    p.ell(59, 27, 5, 4, c["skin"])
    p.px(61, 26, "#111")
    for lx in (16, 40):
        p.limb(lx, 42, lx, MG, 8, dk(c["skin"], 0.2))
    p.ell(28, 34, 26, 15, c["main"])
    p.rect(2, 34, 54, 42, c["main"])
    p.poly([(2, 42), (54, 42), (51, 45), (5, 45)], c["rim"])
    for (x, y) in ((16, 28), (40, 28), (9, 36), (22, 34), (35, 34), (47, 36)):
        p.poly([(x - 5, y), (x - 2.5, y - 3.5), (x + 2.5, y - 3.5), (x + 5, y), (x + 2.5, y + 3.5), (x - 2.5, y + 3.5)], c["plate"], shade=False)
    p.ell(28, 21, 10, 2.4, c["grass"], shade=False)  # a meadow on top, where the rider sits
    p.rect(6, 12, 8, 26, c["trunk"], False)  # a little tree at the back
    p.ell(7, 10, 6, 5, c["leaf"])
    p.ell(3, 14, 3.5, 3, c["leaf"])
    p.line([(45, 22), (47, 30), (46, 40)], c["water"], 2)  # a spring running down the shell
    p.ell(46, 21, 2.5, 1.5, c["water"], shade=False)
    for lx in (10, 36):
        p.limb(lx, 43, lx, MG, 8.5, c["skin"], foot=dk(c["skin"], 0.5))


def m_iguanavolcan(p, c):
    p.curve([(10, 34), (3, 40), (1, 48), (4, 54)], 7, c["main"], taper=0.25)
    for lx in (18, 40):
        p.limb(lx, 36, lx + 3, MG - 1, 6, c["dark"], taper=0.8)
        p.ell(lx + 4, MG - 1, 3.5, 1.4, c["dark"])
    p.ell(27, 31, 20, 11, c["main"])
    for (a, b) in (((12, 28), (20, 34)), ((24, 26), (30, 36)), ((34, 28), (40, 33))):
        p.line([a, b], c["lava"], 1)
    for lx in (13, 36):
        p.limb(lx, 37, lx - 2, MG - 1, 7, c["main"], taper=0.8)
        p.ell(lx - 1, MG - 1, 4, 1.5, dk(c["main"], 0.25))
    for x in range(10, 44, 4):
        p.poly([(x - 2, 21.5), (x, 13 + (x % 3) * 2), (x + 2, 21.5)], c["flame"], shade=False)
        p.px(x, 19, c["flame2"])
    p.poly([(41, 24), (52, 17), (61, 20), (62, 25), (50, 30), (43, 32)], c["main"])
    p.poly([(44, 28), (50, 30), (47, 38)], c["lava"])
    p.px(53, 20, c["eye"])
    p.ell(52, 15, 1.5, 2.5, c["flame"], shade=False)


def m_caballomar(p, c):
    for (x, y, r) in ((12, 56, 1.6), (22, 58, 1.2), (8, 50, 1)):
        p.ell(x, y, r, r, c["bubble"], shade=False)
    p.curve([(24, 44), (20, 52), (26, 58), (32, 55), (30, 50)], 7, c["main"], taper=0.3)
    p.ell(26, 32, 13, 13, c["main"])
    for y in range(22, 44, 3):
        p.line([(17, y), (35, y)], dk(c["main"], 0.15))
    p.ell(30, 34, 6, 9, c["belly"], shade=False)
    p.poly([(14, 22), (6, 18), (5, 28), (12, 34)], c["fin"])
    for k in range(3):
        p.line([(13, 24 + k * 3), (6, 20 + k * 4)], dk(c["fin"], 0.3))
    p.curve([(34, 22), (40, 14), (44, 10)], 9, c["main"], taper=0.8)
    p.ell(45, 9, 6, 5, c["main"])
    p.poly([(48, 9), (62, 14), (61, 17), (48, 13)], c["main"])
    for x in range(36, 46, 3):
        p.poly([(x, 7), (x + 1.5, 2), (x + 3, 7)], c["fin"], shade=False)
    p.px(47, 8, "#111")


def m_murcielagon(p, c):
    bx, by = 30, 26
    for s in (-1, 1):
        pts = [(bx, by - 3), (bx + s * 10, by - 14), (bx + s * 22, by - 19), (bx + s * 31, by - 8), (bx + s * 27, by - 2),
               (bx + s * 23, by + 5), (bx + s * 17, by), (bx + s * 12, by + 7), (bx + s * 6, by + 2), (bx, by + 8)]
        p.poly([(max(0, min(63, x)), y) for x, y in pts], c["wing"])
        for k in (12, 22, 29):
            p.line([(bx + s * 4, by - 2), (max(0, min(63, bx + s * k)), by - (12 if k < 29 else 6))], c["bone"])
    p.ell(bx, by + 4, 9, 10, c["main"])
    hx, hy = bx + 5, by - 6
    p.ell(hx, hy, 6, 5.5, c["main"])
    for s in (-1, 1):
        p.poly([(hx + s * 2, hy - 4), (hx + s * 5, hy - 12), (hx + s * 6, hy - 3)], c["main"])
    p.px(hx - 1.5, hy - 1, c["eye"]); p.px(hx + 2.5, hy - 1, c["eye"])
    p.poly([(hx - 1, hy + 3), (hx + 0, hy + 6), (hx + 1, hy + 3)], "#f0ece0")
    for lx in (bx - 4, bx + 4):
        p.line([(lx, by + 13), (lx, by + 18)], c["bone"], 1)


def horse(p, c, mane=None, tail=None):
    p.curve([(7, 25), (3, 32), (2, 44)], 4.5, tail or c["dark"], taper=0.6)
    quad(p, c, body=(24, 29, 19, 9.5), leg=4.2, front=(36, 39), back=(12, 15))
    p.poly([(35, 25), (43, 9), (51, 11), (45, 32)], c["main"])
    p.poly([(43, 8), (58, 14), (57, 20), (43, 17)], c["main"])
    p.ell(56, 18, 3, 3, c["light"])
    p.poly([(44, 9), (44, 3), (47, 8)], c["main"])
    p.px(49, 12, c["eye"])
    p.curve([(36, 24), (39, 16), (43, 8)], 3.5, mane or c["dark"], taper=0.7)


def m_caballohumo(p, c):
    horse(p, c, mane=c["smoke"], tail=c["smoke"])
    for (x, y, r) in ((2, 22, 3), (5, 16, 2.4), (40, 4, 2.6), (35, 2, 2), (8, 52, 2.4), (44, 56, 2.2), (20, 57, 2)):
        p.ell(x, y, r, r * 0.8, c["smoke"], shade=False)
        p.px(x, y, lt(c["smoke"], 0.4))


def m_mariposa(p, c):
    # the wings rise in a V behind the rider, fore and hind on each side; the body is long and furry
    for s_, col, col2 in ((-1, c["wing2"], c["wing"]), (1, c["wing"], c["wing2"])):
        x0 = 30 + s_ * 3
        p.poly([(x0, 26), (x0 + s_ * 6, 8), (x0 + s_ * 16, 0), (x0 + s_ * 26, 2), (x0 + s_ * 26, 12), (x0 + s_ * 14, 26)], col)
        p.poly([(x0 + s_ * 16, 0), (x0 + s_ * 26, 2), (x0 + s_ * 26, 7), (x0 + s_ * 18, 4)], c["edge"], shade=False)
        p.ell(x0 + s_ * 15, 12, 4, 3, c["shine"], shade=False)
        p.poly([(x0, 32), (x0 + s_ * 14, 30), (x0 + s_ * 22, 38), (x0 + s_ * 16, 46), (x0 + s_ * 6, 42)], col2)
        p.ell(x0 + s_ * 14, 39, 2.4, 2.4, c["edge"], shade=False)
        p.px(x0 + s_ * 14, 39, c["eye"])
    for lx in (22, 30, 38):
        p.line([(lx, 34), (lx - 2, 46), (lx - 1, MG)], c["body"], 1)
    p.ell(26, 30, 16, 6, c["body"])
    p.ell(44, 28, 6, 5.5, c["body"])
    p.ell(52, 27, 4.5, 4, c["body"])
    p.px(54, 26, c["shine"])
    p.line([(53, 23), (57, 12)], c["body"]); p.line([(55, 24), (62, 15)], c["body"])
    p.ell(57, 12, 1.4, 1.4, c["edge"]); p.ell(62, 15, 1.4, 1.4, c["edge"])
    for x in range(14, 40, 5):
        p.line([(x, 26), (x, 34)], lt(c["body"], 0.15))


def m_quinde(p, c):
    for k in range(3):
        p.poly([(24 - k * 3, 24), (10 - k * 3, 2 + k * 3), (4 - k * 2, 4 + k * 3), (18 - k * 3, 28)], (c["wing"] if k == 0 else lt(c["wing"], 0.2 * k)), shade=k == 0)
    p.poly([(12, 34), (0, 42), (2, 46), (14, 38)], c["tail"])
    p.ell(26, 32, 17, 10, c["main"])
    p.ell(30, 36, 10, 5, c["belly"], shade=False)
    p.ell(44, 24, 7, 6.5, c["head"])
    p.ell(42, 28, 6, 3.5, c["throat"], shade=False)
    p.poly([(50, 22), (64, 25), (50, 25)], "#2a2626")
    p.px(46, 22, "#111")
    p.px(45, 21, "#ffffff")
    for lx in (24, 30):
        p.line([(lx, 41), (lx, 47)], "#3a3030", 1)
    for (x, y) in ((6, 30), (2, 22), (14, 8)):
        p.px(x, y, lt(c["wing"], 0.6))


def m_arcoiris(p, c):
    pts = [(2, 50), (10, 42), (20, 46), (30, 40), (26, 30), (18, 24), (24, 18), (36, 20), (46, 22), (52, 16), (54, 10)]
    bands = c["bands"]
    for k, col in enumerate(bands):
        w = 14 - k * 1.6
        p.curve(pts, w, col, shade=k == 0, taper=0.55)
    p.ell(56, 9, 6, 4.4, bands[0])
    p.poly([(58, 8), (64, 10), (59, 12)], bands[0])
    for k, col in enumerate(bands):
        p.line([(52 - k, 4), (49 - k * 2, -1)], col, 1)
    p.px(57, 7, "#ffffff")
    p.line([(63, 11), (64, 13)], "#ffffff")


def m_jaguarestrella(p, c):
    cat_mount(p, c, rosettes=c["mark"])
    for (x, y) in ((12, 24), (20, 22), (28, 24), (34, 23), (16, 30), (24, 30), (31, 29), (44, 14), (52, 18)):
        p.px(x, y, c["star"])
    for (x, y) in ((4, 12), (16, 8), (58, 6), (60, 40)):
        p.px(x, y, c["star"]); p.px(x - 1, y, lt(c["star"], 0.2)); p.px(x + 1, y, lt(c["star"], 0.2)); p.px(x, y - 1, lt(c["star"], 0.2)); p.px(x, y + 1, lt(c["star"], 0.2))


def m_venadosol(p, c):
    m_venado(p, c)
    cx, cy = 47, 4
    for k in range(9):
        a = math.radians(200 + k * 17)
        p.line([(cx + math.cos(a) * 4, cy + math.sin(a) * 4 + 4), (cx + math.cos(a) * 9, cy + math.sin(a) * 9 + 4)], c["ray"], 1)


def m_ballenanube(p, c):
    for (x, y, r) in ((8, 52, 7), (18, 55, 8), (30, 54, 8), (42, 55, 7), (52, 52, 6), (14, 48, 5), (36, 49, 6)):
        p.ell(x, y, r, r * 0.7, c["cloud"], shade=False)
    p.poly([(8, 30), (0, 20), (2, 28), (0, 36), (6, 34)], c["main"])
    p.curve([(6, 32), (16, 30), (30, 30), (44, 32)], 22, c["main"], taper=0.7)
    p.ell(46, 32, 13, 10, c["main"])
    p.poly([(36, 38), (58, 38), (58, 41), (38, 43)], c["belly"], shade=False)
    for y in (39, 41):
        p.line([(38, y), (56, y)], dk(c["belly"], 0.2))
    p.poly([(30, 38), (24, 48), (34, 42)], dk(c["main"], 0.15))
    p.px(52, 30, "#111")
    for (x, y) in ((50, 18), (52, 14), (48, 12)):
        p.ell(x, y, 1.6, 1.6, c["spout"], shade=False)
    for (x, y) in ((16, 22), (24, 21), (32, 22)):
        p.px(x, y, lt(c["main"], 0.4))


MOUNTS_MORE = {
    "cebu": (m_cebu, {
        "blanco": dict(main="#e8e2d8", dark="#b8b0a4", muzzle="#c8a8a0", horn="#c8b890", dewlap="#d8d0c4"),
        "gris": dict(main="#a8a4a0", dark="#787470", muzzle="#6a6060", horn="#2a2624", dewlap="#989490"),
        "rojo": dict(main="#a8583a", dark="#7a3a24", muzzle="#5a3a2a", horn="#e8dcc0", dewlap="#985034"),
    }),
    "bufalo": (m_bufalo, {
        "negro": dict(main="#2a2828", dark="#1a1818", muzzle="#4a4444", horn="#5a5048"),
        "gris": dict(main="#5a5a5a", dark="#3a3a3a", muzzle="#7a7470", horn="#3a3430"),
        "barro": dict(main="#6a5040", dark="#4a3628", muzzle="#8a7060", horn="#2a2420"),
    }),
    "saino": (m_saino, {
        "gris": dict(main="#4a4644", dark="#2e2a28", mane="#2a2624", collar="#c8c0b0", snout="#6a6060"),
        "pardo": dict(main="#5a4232", dark="#3a2a20", mane="#2a1e16", collar="#d8c8a8", snout="#7a6050"),
        "negro": dict(main="#22201e", dark="#141210", mane="#100e0c", collar="#a8a090", snout="#3a3434"),
    }),
    "garzon": (m_garzon, {
        "blanco": dict(main="#f2f0ea", wing="#dcd8d0", tail="#c8c4bc", neck="#1e1c1e", band="#d02a2a", beak="#1e1c1e", leg="#2a2a2a"),
        "rosado": dict(main="#f0b0b8", wing="#e08a98", tail="#c87080", neck="#4a3038", band="#f0e0a0", beak="#3a2a2a", leg="#a05a60"),
        "gris": dict(main="#a8acb4", wing="#8a8e98", tail="#6a6e78", neck="#2a2a30", band="#f0c030", beak="#2a2a30", leg="#3a3a40"),
    }),
    "anaconda": (m_anaconda, {
        "verde": dict(main="#5a6a2a", belly="#c8c070", mark="#1e2010", eye="#e8c030"),
        "amarilla": dict(main="#b0a030", belly="#f0e090", mark="#2a2410", eye="#e04020"),
        "oscura": dict(main="#2e3a2a", belly="#8a9a6a", mark="#141a10", eye="#e8c030"),
    }),
    "mulatres": (m_mulatres, {
        "brasa": dict(main="#2a2020", dark="#1a1414", hoof="#e04a1a", flame="#f07a1a", flame2="#fff0a0", eye="#ffd040"),
        "ceniza": dict(main="#6a6464", dark="#4a4444", hoof="#2a2626", flame="#e0e0e8", flame2="#ffffff", eye="#ff4a2a"),
        "azufre": dict(main="#3a3a1a", dark="#24240e", hoof="#c0c040", flame="#d8e040", flame2="#ffffe0", eye="#f0f060"),
    }),
    "bufeo": (m_bufeo, {
        "rosado": dict(main="#f0a0b0", belly="#f8d0d8", water="#3a8ab0"),
        "gris": dict(main="#9aa4b0", belly="#dce4ec", water="#2a6a90"),
        "colorado": dict(main="#e06070", belly="#f8b8c0", water="#4a7a5a"),
    }),
    "pezoro": (m_pezoro, {
        "oro": dict(main="#e0b030", fin="#c08018", scale="#fff0a0", bubble="#a0e0ff"),
        "tumbaga": dict(main="#c87848", fin="#8a4a28", scale="#ffd0a0", bubble="#a0e0ff"),
        "plata": dict(main="#c8d0dc", fin="#8a94a8", scale="#ffffff", bubble="#c0f0ff"),
    }),
    "jaguaralado": (m_jaguaralado, {
        "dorado": dict(main="#d8a040", dark="#a07028", light="#f8ecd0", mark="#2a1a10", eye="#a0c040", wing="#f4ecd8", wing2="#d8c8a8"),
        "negro": dict(main="#2e2a2a", dark="#1e1a1a", light="#4a4444", mark="#161212", eye="#e8c040", wing="#3a3440", wing2="#24202a"),
        "nieve": dict(main="#e8ecf0", dark="#b0b8c0", light="#ffffff", mark="#5a6070", eye="#60b0e0", wing="#ffffff", wing2="#d0e0f0"),
    }),
    "tortugamundo": (m_tortugamundo, {
        "verde": dict(main="#4a5a34", plate="#6a7a44", rim="#c8b878", skin="#7a7a5a", grass="#6aa040", trunk="#5a3a24", leaf="#3a8a3a", water="#6ac0f0"),
        "otono": dict(main="#5a4430", plate="#7a6040", rim="#d8c090", skin="#8a7a60", grass="#c8a040", trunk="#5a3a24", leaf="#d86a2a", water="#6ac0f0"),
        "nieve": dict(main="#5a6470", plate="#7a8490", rim="#e8ecf0", skin="#8a9098", grass="#f0f4f8", trunk="#4a3a30", leaf="#e8f0f8", water="#a0e0ff"),
    }),
    "iguanavolcan": (m_iguanavolcan, {
        "brasa": dict(main="#3a2a24", dark="#221814", lava="#f06020", flame="#f08020", flame2="#fff0a0", eye="#ffd040"),
        "ceniza": dict(main="#6a6464", dark="#4a4444", lava="#e04a2a", flame="#e8e0d8", flame2="#ffffff", eye="#ff6a2a"),
        "obsidiana": dict(main="#1e1a24", dark="#100e14", lava="#a04af0", flame="#c080ff", flame2="#f0e0ff", eye="#e0a0ff"),
    }),
    "caballomar": (m_caballomar, {
        "coral": dict(main="#e8704a", belly="#f8c0a0", fin="#f0a060", bubble="#a0e0ff"),
        "turquesa": dict(main="#2aa8a0", belly="#a0e8d8", fin="#60d0c0", bubble="#c0f0ff"),
        "oro": dict(main="#d8a830", belly="#f8e090", fin="#f0c860", bubble="#c0f0ff"),
    }),
    "murcielagon": (m_murcielagon, {
        "noche": dict(main="#2a2430", wing="#1e1a24", bone="#4a4058", eye="#ff4a3a"),
        "pardo": dict(main="#5a4232", wing="#3e2e24", bone="#7a6050", eye="#f0d040"),
        "luna": dict(main="#c8ccd8", wing="#8a90a8", bone="#e0e4f0", eye="#60b0ff"),
    }),
    "caballohumo": (m_caballohumo, {
        "humo": dict(main="#8a8a90", dark="#5a5a60", light="#c8c8d0", smoke="#d0d0d8", eye="#ffffff"),
        "noche": dict(main="#2a2a38", dark="#1a1a24", light="#4a4a60", smoke="#6a6a90", eye="#a0e0ff"),
        "ceniza": dict(main="#b8b0a8", dark="#8a8278", light="#e8e0d8", smoke="#f0ece8", eye="#ff6a3a"),
    }),
    "mariposa": (m_mariposa, {
        "azul": dict(wing="#2a70e8", wing2="#1a50c0", edge="#1a1a2a", shine="#a0d8ff", eye="#f0e0a0", body="#2a2420"),
        "oro": dict(wing="#e8b020", wing2="#c88a10", edge="#2a1a0a", shine="#fff0a0", eye="#2a5ae0", body="#2a2018"),
        "noche": dict(wing="#3a2a6a", wing2="#24184a", edge="#c0a0ff", shine="#8a70e0", eye="#ffe080", body="#141020"),
    }),
    "quinde": (m_quinde, {
        "esmeralda": dict(main="#2aa860", belly="#c8f0d0", head="#40c878", throat="#e03a6a", wing="#1a7a48", tail="#1a6a40"),
        "zafiro": dict(main="#2a5ad0", belly="#c8d8f8", head="#3a70e0", throat="#a0f0ff", wing="#1a3a9a", tail="#142a7a"),
        "fuego": dict(main="#e05020", belly="#f8c040", head="#f08030", throat="#f8e040", wing="#b03010", tail="#a02810"),
    }),
    "arcoiris": (m_arcoiris, {
        "dia": dict(bands=["#e03030", "#f08a20", "#f0d030", "#40b050", "#3a7ae0", "#6a40c0", "#c060d0"]),
        "noche": dict(bands=["#3a2a8a", "#4a5ac0", "#5a9ae0", "#70d0e0", "#a0f0e0", "#e0f8f0", "#ffffff"]),
        "fuego": dict(bands=["#7a1a10", "#b02a14", "#e04a1a", "#f07a20", "#f0b030", "#f8e060", "#fff8c0"]),
    }),
    "jaguarestrella": (m_jaguarestrella, {
        "noche": dict(main="#1e2448", dark="#121630", light="#3a4478", mark="#0a0c20", eye="#f8e070", star="#ffffff"),
        "violeta": dict(main="#3a2060", dark="#24123e", light="#5a3a88", mark="#140a24", eye="#a0ffe0", star="#ffe8ff"),
        "aurora": dict(main="#1a4a4a", dark="#0e2e2e", light="#2a7070", mark="#062020", eye="#f0a0ff", star="#c0fff0"),
    }),
    "venadosol": (m_venadosol, {
        "oro": dict(main="#d8a83a", dark="#a07828", light="#fff0c0", antler="#fff4b0", spots="#fff0c0", ray="#ffe060"),
        "alba": dict(main="#e8a080", dark="#b87058", light="#fff0e0", antler="#fff8e8", spots=None, ray="#ffd0a0"),
        "blanco": dict(main="#f4f2ee", dark="#c8c6c2", light="#ffffff", antler="#fff8d0", spots=None, ray="#fff0a0"),
    }),
    "ballenanube": (m_ballenanube, {
        "azul": dict(main="#4a6a9a", belly="#d8e4f0", cloud="#f4f8ff", spout="#c0e8ff"),
        "gris": dict(main="#6a7078", belly="#e0e4e8", cloud="#ffffff", spout="#e0f0ff"),
        "rosada": dict(main="#c08aa8", belly="#f8e0ec", cloud="#fff0f4", spout="#ffe0f0"),
    }),
}
