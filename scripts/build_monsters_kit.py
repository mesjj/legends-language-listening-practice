"""The 240 monsters of the zones added on 2026-11-27 (scripts/zones_more.py), drawn in code: original pixel
art in the stable's style (build_stable.Pic: flat shapes, shaded and outlined). Each monster is an
archetype (biped, quad, bird, serpent, ...) given its colours "main,second,accent,eye" and options.
Drawn facing right, then turned to face the player. Writes art/monsters/<id>.png; build_lpc.py packs them.
usage: .venv/bin/python scripts/build_monsters_kit.py [id ...] [--sheet out.png]
"""
import math
import os
import random
import sys

from PIL import Image

from build_stable import Pic, dk, lt, mix
import zones_more as Z

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "art", "monsters")
BIG = (64, 61)
SMALL = (52, 40)


def cols(s):
    m, s2, a, e = s.split(",")
    return dict(main=m, second=s2, accent=a, eye=e)


def eye(p, x, y, col, r=1.0):
    p.ell(x, y, r, r, col, shade=False)
    p.px(x, y, "#ffffff")


def glow_eyes(p, pts, col):
    for x, y in pts:
        p.px(x, y, col)
        p.px(x + 1, y, col)


# ================================================================== people and humanoids (64 x 61)
def head_at(p, c, o, hx, hy):
    kind = o.get("head", "human")
    m, s2, a, e = c["main"], c["second"], c["accent"], c["eye"]
    if kind == "human":
        p.ell(hx, hy, 5, 5.5, m)
        p.px(hx + 2.5, hy - 1, "#1a1010") if not o.get("fx") in ("ghost",) else glow_eyes(p, [(hx + 2, hy - 1)], e)
        p.px(hx + 5, hy + 1, dk(m, .3))
        if o.get("beard"):
            p.poly([(hx - 2, hy + 2), (hx + 5, hy + 2), (hx + 2, hy + 9), (hx - 1, hy + 6)], "#d8d0c0" if o.get("fx") != "ghost" else lt(m, .4))
        if o.get("paint") or o.get("fx") == "painted":
            p.line([(hx - 1, hy + 1), (hx + 5, hy + 1)], a)
    elif kind in ("skull", "bone"):
        p.ell(hx, hy, 5, 5, m)
        p.rect(hx - 1, hy + 3, hx + 4, hy + 6, m)
        glow_eyes(p, [(hx + 1, hy - 1)], e)
        p.px(hx + 4, hy - 1, "#1a1010")
        for x in range(int(hx), int(hx + 4), 2):
            p.px(x, hy + 5, "#1a1010")
    elif kind == "fur":
        p.ell(hx, hy, 6.5, 6, m)
        p.ell(hx + 3, hy + 1, 3, 2.6, s2, shade=False)
        glow_eyes(p, [(hx + 2, hy - 2)], e)
    elif kind == "hood":
        p.poly([(hx - 6, hy + 7), (hx - 5, hy - 5), (hx + 1, hy - 8), (hx + 6, hy - 3), (hx + 6, hy + 7)], s2)
        p.ell(hx + 2, hy + 1, 3.5, 4, dk(s2, .7), shade=False)
        glow_eyes(p, [(hx + 2, hy)], e)
    elif kind == "fish":
        p.ell(hx + 1, hy, 6, 5, m)
        p.poly([(hx - 5, hy - 4), (hx - 1, hy - 9), (hx + 3, hy - 5)], s2)
        eye(p, hx + 3, hy - 1.5, e, 1.2)
        p.line([(hx + 4, hy + 2.5), (hx + 7, hy + 2)], dk(m, .5))
    elif kind == "helm":
        p.ell(hx, hy, 5.5, 6, s2)
        p.rect(hx - 1, hy - 1, hx + 5, hy + 1, "#141018", shade=False)
        glow_eyes(p, [(hx + 2, hy - 1)], e)
        p.poly([(hx - 2, hy - 6), (hx, hy - 11), (hx + 2, hy - 6)], a)
    elif kind in ("ox", "horse", "horned", "demon", "jaguar", "ice", "mask"):
        if kind == "ox":
            p.ell(hx, hy, 6, 6, m); p.ell(hx + 5, hy + 3, 3.5, 3, lt(m, .2))
            for s in (-1, 1):
                p.curve([(hx - 1 + s * 3, hy - 4), (hx + s * 8, hy - 8), (hx + s * 9, hy - 13)], 2.5, "#e8dcc0", taper=0.4)
        elif kind == "horse":
            p.poly([(hx - 4, hy - 6), (hx + 4, hy - 5), (hx + 10, hy + 4), (hx + 7, hy + 7), (hx - 4, hy + 4)], m)
            p.poly([(hx - 3, hy - 6), (hx - 1, hy - 11), (hx + 1, hy - 5)], m)
            p.curve([(hx - 5, hy - 6), (hx - 7, hy), (hx - 6, hy + 6)], 3, s2)
        elif kind in ("horned", "demon"):
            p.ell(hx, hy, 5.5, 6, m)
            for s in (-1, 1):
                p.poly([(hx + s * 3 - 1.5, hy - 4), (hx + s * 6, hy - 12), (hx + s * 3 + 1.5, hy - 4)], "#2a1a14" if kind == "horned" else a)
            p.line([(hx + 1, hy + 3), (hx + 5, hy + 3)], "#1a0a08")
        elif kind == "jaguar":
            p.ell(hx, hy, 6, 5.5, a)
            p.ell(hx - 3, hy - 5, 2, 2, a); p.ell(hx + 3, hy - 5, 2, 2, a)
            for (x, y) in ((-2, -2), (2, 2), (-3, 2)):
                p.px(hx + x, hy + y, "#1a1010")
        elif kind == "ice":
            p.poly([(hx - 5, hy + 5), (hx - 6, hy - 3), (hx - 2, hy - 8), (hx + 3, hy - 9), (hx + 6, hy - 2), (hx + 5, hy + 5)], m)
            p.line([(hx - 2, hy - 8), (hx, hy + 4)], lt(m, .5))
        elif kind == "mask":
            p.rect(hx - 5, hy - 6, hx + 5, hy + 6, a)
            p.rect(hx - 3, hy - 3, hx - 1, hy - 1, "#1a1410", shade=False); p.rect(hx + 1, hy - 3, hx + 3, hy - 1, "#1a1410", shade=False)
            p.line([(hx - 3, hy + 3), (hx + 3, hy + 3)], "#1a1410")
        glow_eyes(p, [(hx + 2, hy - 1)], e)
    hat = o.get("hat")
    if hat == "crown":
        p.poly([(hx - 5, hy - 4), (hx - 5, hy - 9), (hx - 2.5, hy - 6), (hx, hy - 10), (hx + 2.5, hy - 6), (hx + 5, hy - 9), (hx + 5, hy - 4)], a)
    elif hat == "feathers":
        p.rect(hx - 5, hy - 5, hx + 5, hy - 3, a)
        for k in range(5):
            p.poly([(hx - 4 + k * 2, hy - 5), (hx - 6 + k * 2.5, hy - 13 - (k % 2) * 2), (hx - 3 + k * 2, hy - 5)], ["#e0302a", "#f0c030", "#2a6ae0", "#3ac040", "#e0302a"][k])
    elif hat == "wide":
        p.poly([(hx - 10, hy - 3), (hx + 10, hy - 3), (hx + 7, hy - 5), (hx + 4, hy - 9), (hx - 4, hy - 9), (hx - 7, hy - 5)], mix(s2, "#c8a870", .5))
    elif hat == "cap":
        p.poly([(hx - 5, hy - 3), (hx - 4, hy - 7), (hx + 4, hy - 7), (hx + 5, hy - 3), (hx + 9, hy - 2), (hx + 5, hy - 2)], s2)
    elif hat == "helm":
        p.poly([(hx - 6, hy - 2), (hx - 5, hy - 7), (hx + 5, hy - 7), (hx + 6, hy - 2)], mix(s2, "#c8a040", .3))
        if o.get("lamp", True):
            p.ell(hx + 5, hy - 5, 1.6, 1.6, a, shade=False)
    elif hat == "cone":
        p.poly([(hx - 6, hy - 3), (hx + 1, hy - 18), (hx + 6, hy - 3)], s2)
        p.px(hx + 1, hy - 10, a); p.px(hx - 1, hy - 6, a)
    elif hat == "tricorn":
        p.poly([(hx - 8, hy - 3), (hx - 3, hy - 9), (hx + 4, hy - 9), (hx + 8, hy - 3)], "#1a1a24")
        p.line([(hx - 6, hy - 4), (hx + 6, hy - 4)], a)
    elif hat == "bandana":
        p.poly([(hx - 5, hy - 2), (hx - 5, hy - 6), (hx + 5, hy - 6), (hx + 5, hy - 2)], a)
        p.poly([(hx - 5, hy - 4), (hx - 10, hy - 1), (hx - 9, hy + 2)], a)
    elif hat == "morion":
        p.poly([(hx - 9, hy - 3), (hx - 4, hy - 7), (hx - 2, hy - 12), (hx + 2, hy - 12), (hx + 4, hy - 7), (hx + 9, hy - 3)], "#a8a8b8")
    return hx, hy


def held_at(p, c, o, x, y, g):
    kind = o.get("held", "none")
    a, wood, metal = c["accent"], "#6a4a2a", "#b8b8c8"
    if kind in ("staff", "spear", "trident", "halberd", "oar"):
        p.line([(x, y - 18), (x + 1, g - 2)], wood, 2)
        if kind == "staff":
            p.ell(x, y - 19, 2.4, 2.4, a, shade=False)
        elif kind == "spear":
            p.poly([(x - 2, y - 17), (x, y - 25), (x + 2, y - 17)], metal)
        elif kind == "trident":
            for dx in (-3, 0, 3):
                p.line([(x + dx, y - 17), (x + dx, y - 24)], a, 1)
            p.line([(x - 3, y - 17), (x + 3, y - 17)], a)
        elif kind == "halberd":
            p.poly([(x, y - 22), (x + 6, y - 19), (x + 6, y - 13), (x, y - 16)], metal)
            p.poly([(x - 1, y - 22), (x, y - 28), (x + 1, y - 22)], metal)
        elif kind == "oar":
            p.ell(x + 1, g - 5, 2.4, 5, wood)
    elif kind in ("club", "hammer"):
        p.line([(x, y + 2), (x + 6, y - 12)], wood, 2)
        if kind == "club":
            p.ell(x + 7, y - 14, 4, 5, mix(wood, c["main"], .3))
        else:
            p.rect(x + 3, y - 17, x + 11, y - 12, metal)
    elif kind in ("pick", "axe"):
        p.line([(x, y + 3), (x + 4, y - 12)], wood, 2)
        if kind == "pick":
            p.curve([(x - 2, y - 11), (x + 4, y - 14), (x + 10, y - 10)], 2, metal, taper=0.6)
        else:
            p.poly([(x + 3, y - 13), (x + 10, y - 15), (x + 10, y - 7), (x + 4, y - 9)], metal)
    elif kind in ("machete", "saber", "sword"):
        p.rect(x - 1, y - 1, x + 2, y + 1, "#3a2a1a", shade=False)
        p.curve([(x + 1, y - 1), (x + 6, y - 9), (x + 9, y - 18)], 2.4, metal, taper=0.5)
    elif kind == "lantern":
        p.line([(x, y), (x, y + 4)], "#2a2a2a")
        p.rect(x - 2.5, y + 4, x + 2.5, y + 10, a)
        p.px(x, y + 7, "#ffffff")
    elif kind == "basket":
        p.ell(x + 2, y + 4, 5, 3.5, "#a8803a")
        p.line([(x - 2, y + 3), (x + 6, y + 3)], "#6a4a1a")
    elif kind == "net":
        p.poly([(x, y), (x + 9, y + 4), (x + 6, g - 4), (x - 2, g - 8)], mix(c["second"], "#c8c0a0", .5)[:3] + (150,), shade=False)
        for k in range(4):
            p.line([(x + k * 2, y + 1), (x - 1 + k * 2, g - 7)], "#5a5040")
    elif kind == "chain":
        for k in range(7):
            p.ell(x + k * 1.8, y + k * 2.5, 1.3, 1.6, metal, shade=False)
        if o.get("keys"):
            p.ell(x + 13, y + 18, 2, 2, a, shade=False)
    elif kind == "whip":
        p.curve([(x, y), (x + 8, y - 4), (x + 14, y + 4), (x + 16, y + 14)], 1.6, "#5a3a1a", taper=0.6)


def biped(p, c, o):
    W_, H_ = p.w, p.h
    g = H_ - 1
    m, s2, a = c["main"], c["second"], c["accent"]
    k = 1.08 if o.get("big") else (0.82 if o.get("small") else 0.96)
    cx = 30
    body = o.get("body", "tunic")
    hip, sh = g - 20 * k, g - 38 * k
    legcol = m if body in ("bare",) else dk(s2, .25)
    if o.get("pegleg"):
        p.limb(cx - 4, hip, cx - 5, g, 4.5 * k, legcol, foot=dk(legcol, .4))
        p.line([(cx + 3, hip), (cx + 4, g)], "#6a4a2a", 2)
    else:
        for lx, dx in ((cx - 4, -1.5), (cx + 3, 1.5)):
            p.limb(lx, hip, lx + dx, g, 5 * k, legcol, foot=dk(legcol, .5))
    if o.get("tail"):
        p.curve([(cx - 4, hip), (cx - 14, hip + 2), (cx - 18, hip - 8)], 2, m, taper=0.4)
        p.poly([(cx - 20, hip - 9), (cx - 18, hip - 13), (cx - 15, hip - 9)], m)
    # the far arm
    p.limb(cx - 6, sh + 3, cx - 10, hip + 1, 4 * k, dk(m if body == "bare" else s2, .2), foot=dk(m, .1))
    if o.get("arms") == 4:
        p.limb(cx - 6, sh + 6, cx - 13, sh - 4, 3.5 * k, dk(m, .2))
        p.limb(cx + 6, sh + 6, cx + 13, sh - 2, 3.5 * k, dk(m, .2))
    if o.get("pack"):
        p.rect(cx - 13, sh + 2, cx - 6, hip - 2, "#6a5a3a")
    # the torso
    if body == "robe":
        p.poly([(cx - 8 * k, sh), (cx + 8 * k, sh), (cx + 11 * k, g - 2), (cx - 11 * k, g - 2)], s2)
        p.line([(cx + 1, sh + 2), (cx + 1, g - 3)], a)
    elif body in ("ruana",):
        p.poly([(cx - 7 * k, sh), (cx + 7 * k, sh), (cx + 8 * k, hip + 1), (cx - 8 * k, hip + 1)], dk(s2, .2))
        p.poly([(cx - 12 * k, sh + 4), (cx + 12 * k, sh + 4), (cx + 9 * k, hip - 2), (cx - 10 * k, hip - 2)], s2)
        for y in range(int(sh + 7), int(hip - 2), 3):
            p.line([(cx - 9, y), (cx + 9, y)], a)
    else:
        col = {"bare": m, "fur": s2, "armor": mix(s2, "#a8a8b8", .3), "coat": s2, "tunic": s2, "rags": s2}.get(body, s2)
        p.poly([(cx - 8 * k, sh), (cx + 8 * k, sh), (cx + 7 * k, hip + 1), (cx - 7 * k, hip + 1)], col)
        if body == "armor":
            p.line([(cx - 7, sh + 7), (cx + 7, sh + 7)], dk(col, .35))
            p.ell(cx + 7, sh + 1, 3.5, 2.6, lt(col, .15))
        elif body == "rags":
            for x in range(int(cx - 7), int(cx + 8), 3):
                p.poly([(x, hip), (x + 1.5, hip + 4), (x + 3, hip)], col)
        elif body == "coat":
            p.poly([(cx - 8 * k, hip), (cx + 7 * k, hip), (cx + 9 * k, hip + 9), (cx - 10 * k, hip + 9)], col)
            p.line([(cx + 1, sh + 1), (cx + 1, hip + 8)], a)
        elif body == "fur":
            for x in range(int(cx - 7), int(cx + 8), 3):
                p.px(x, sh + 5, lt(col, .3)); p.px(x + 1, sh + 11, lt(col, .3))
        elif body == "bare":
            p.line([(cx - 4, sh + 9), (cx + 5, sh + 9)], dk(m, .25))
            if o.get("paint") or o.get("fx") == "painted":
                for y in (sh + 4, sh + 12):
                    p.line([(cx - 6, y), (cx + 6, y + 1)], a)
        if body != "bare":
            p.rect(cx - 7 * k, hip - 2, cx + 7 * k, hip, dk(col, .45), shade=False)
    hx, hy = cx + 2, sh - 6 * k
    head_at(p, c, o, hx, hy)
    if o.get("hook"):
        pass
    # the near arm and what it holds
    held = o.get("held", "none")
    p.limb(cx + 6, sh + 3, cx + 12, sh + 12, 4.2 * k, m if body == "bare" else s2, foot=m)
    if o.get("hook"):
        p.curve([(cx + 12, sh + 12), (cx + 15, sh + 15), (cx + 13, sh + 18)], 1.4, "#c8c8d8", taper=1)
    held_at(p, c, o, cx + 13, sh + 12, g)
    if o.get("pipe"):
        p.line([(hx + 4, hy + 2), (hx + 9, hy + 3)], "#3a2a1a")
        p.rect(hx + 8, hy + 1, hx + 10, hy + 3, "#3a2a1a")
    base = o.get("base")
    if base == "raft":
        p.rect(4, g - 2, 56, g, "#a8904a")
        for x in range(6, 56, 5):
            p.px(x, g - 1, "#6a5a2a")
    elif base == "boat":
        p.poly([(2, g - 6), (60, g - 6), (54, g), (8, g)], "#3a2a24")
    fx = o.get("fx")
    rnd = random.Random(str(o))
    sparks = {"gold": "#ffe060", "ice": "#c8f0ff", "flame": "#ffb040", "ash": "#8a8480", "mud": "#5a5a30", "silver": "#e8e8ff", "stars": "#fffbe0",
              "smoke": "#d8d060", "leaves": "#6aaa3a", "birds": "#e0302a"}.get(fx)
    if sparks:
        for i in range(9):
            x, y = rnd.randint(8, 56), rnd.randint(6, g - 6)
            p.px(x, y, sparks)
            if fx in ("stars", "gold", "silver"):
                p.px(x + 1, y, lt(sparks, .3))
    if o.get("animals"):
        p.ell(cx - 12, g - 3, 3, 2, "#3a6ac8"); p.px(cx - 10, g - 4, "#ff3020")
    if o.get("lamp") and o.get("hat") != "helm":
        pass


# ================================================================== four-legged (64 x 61)
def quad_head(p, c, o, hx, hy, k):
    kind = o.get("head", "dog")
    m, s2, a, e = c["main"], c["second"], c["accent"], c["eye"]
    if kind == "bear":
        p.ell(hx, hy, 8 * k, 7 * k, m)
        p.ell(hx + 6 * k, hy + 2 * k, 3.6 * k, 3 * k, a)
        p.ell(hx - 4 * k, hy - 6 * k, 2.4 * k, 2.4 * k, m)
        if o.get("spectacles"):
            p.ell(hx + 2 * k, hy - 1 * k, 3 * k, 2.4 * k, a, shade=False)
        p.px(hx + 9 * k, hy + 1 * k, "#1a1010")
    elif kind in ("dog", "fox", "wolf"):
        p.ell(hx, hy, 6 * k, 5.5 * k, m)
        p.poly([(hx + 3 * k, hy - 2 * k), (hx + 12 * k, hy + 1 * k), (hx + 11 * k, hy + 4 * k), (hx + 3 * k, hy + 4 * k)], m)
        p.px(hx + 11.5 * k, hy + 1 * k, "#1a1010")
        for s in (-1, 1):
            p.poly([(hx - 3 * k + s * 2, hy - 3 * k), (hx - 2 * k + s * 2, hy - (11 if kind == "fox" else 9) * k), (hx + 1 * k + s * 2, hy - 3 * k)], m)
        if kind == "fox":
            p.ell(hx + 4 * k, hy + 3 * k, 3 * k, 1.6 * k, a, shade=False)
    elif kind == "cat":
        p.ell(hx, hy, 7 * k, 6 * k, m)
        p.ell(hx + 5 * k, hy + 2.5 * k, 3.2 * k, 2.4 * k, lt(m, .25))
        for s in (-1, 1):
            p.poly([(hx - 3 * k + s * 3, hy - 3 * k), (hx - 2 * k + s * 3, hy - 9 * k), (hx + 1 * k + s * 3, hy - 3 * k)], m)
        p.px(hx + 8 * k, hy + 1.5 * k, "#1a1010")
    elif kind in ("goat", "deer", "bull", "horse"):
        p.poly([(hx - 3 * k, hy - 4 * k), (hx + 4 * k, hy - 4 * k), (hx + 11 * k, hy + 3 * k), (hx + 9 * k, hy + 6 * k), (hx - 2 * k, hy + 4 * k)], m)
        p.ell(hx + 9 * k, hy + 4 * k, 2.6 * k, 2.2 * k, dk(m, .2))
        p.poly([(hx - 3 * k, hy - 3 * k), (hx - 5 * k, hy - 8 * k), (hx, hy - 4 * k)], m)
        if o.get("horns"):
            if kind == "goat":
                p.curve([(hx, hy - 4 * k), (hx - 4 * k, hy - 11 * k), (hx - 9 * k, hy - 9 * k), (hx - 8 * k, hy - 4 * k)], 2.4 * k, a, taper=0.5)
            elif kind == "deer":
                for s in (0, 3):
                    p.line([(hx + s, hy - 4 * k), (hx - 2 + s, hy - 14 * k), (hx - 6 + s, hy - 18 * k)], a, 2)
                    p.line([(hx - 1 + s, hy - 10 * k), (hx + 3 + s, hy - 14 * k)], a)
            else:
                p.curve([(hx, hy - 3 * k), (hx + 5 * k, hy - 9 * k), (hx + 9 * k, hy - 10 * k)], 2.6 * k, a, taper=0.4)
        if kind == "horse":
            p.curve([(hx - 3 * k, hy - 4 * k), (hx - 9 * k, hy + 2 * k), (hx - 10 * k, hy + 10 * k)], 3 * k, s2)
    elif kind in ("tapir", "pig", "capybara", "otter", "rat", "mole", "bone"):
        long_ = {"tapir": 10, "pig": 8, "capybara": 7, "otter": 6, "rat": 8, "mole": 9, "bone": 9}[kind]
        p.ell(hx, hy, 6.5 * k, 6 * k, m)
        p.poly([(hx + 2 * k, hy - 3 * k), (hx + long_ * k, hy), (hx + (long_ + 1) * k, hy + 4 * k), (hx + 2 * k, hy + 5 * k)], m)
        if kind == "tapir":
            p.curve([(hx + 9 * k, hy + 1 * k), (hx + 13 * k, hy + 4 * k), (hx + 12 * k, hy + 8 * k)], 2.6 * k, m, taper=0.7)
        if kind in ("pig",) and o.get("tusks"):
            p.poly([(hx + 6 * k, hy + 4 * k), (hx + 8 * k, hy - 1 * k), (hx + 8 * k, hy + 4 * k)], "#f0e8d8")
        if kind in ("rat", "mole"):
            p.px(hx + (long_ + 1) * k, hy + 2 * k, a)
            for s in (0, 2):
                p.line([(hx + long_ * k, hy + 2 + s), (hx + (long_ + 5) * k, hy + 1 + s * 2)], dk(m, .4))
        if kind == "bone":
            for x in range(0, int(long_ * k), 2):
                p.px(hx + 3 + x, hy + 4 * k, "#1a1010")
        p.ell(hx - 3 * k, hy - 5 * k, 2 * k, 2.2 * k, m)
    glow = o.get("fire") or kind in ("bone",)
    if kind == "bear":
        ex = (hx + 3 * k, hy - 2 * k)
    elif kind in ("goat", "deer", "bull", "horse"):
        ex = (hx + 2 * k, hy - 1 * k)
    else:
        ex = (hx + 2 * k, hy - 1.5 * k)
    if glow:
        glow_eyes(p, [ex], e)
    else:
        eye(p, ex[0], ex[1], e, 0.9 * k)


def quad(p, c, o):
    g = p.h - 1
    m, s2, a = c["main"], c["second"], c["accent"]
    big = o.get("big")
    k = 1.0 if big else 0.78
    cx, cy = 28, g - 24 * k
    rx, ry = 19 * k, 10 * k
    kind = o.get("head", "dog")
    tail = {"cat": "long", "dog": "brush", "fox": "brush", "rat": "thin", "otter": "thick", "horse": "hair", "bull": "thin", "deer": "short",
            "goat": "short", "bone": "spikes"}.get(kind)
    if tail == "long":
        p.curve([(cx - rx + 2, cy - 2), (cx - rx - 8, cy - 2), (cx - rx - 10, cy - 12), (cx - rx - 6, cy - 16)], 3.6 * k, m, taper=0.7)
    elif tail == "brush":
        p.curve([(cx - rx + 2, cy - 2), (cx - rx - 8, cy + 2), (cx - rx - 12, cy + 8)], 5 * k, m, taper=0.6)
        if kind == "fox":
            p.ell(cx - rx - 12, cy + 8, 2.4, 2.4, "#f0e8d8", shade=False)
    elif tail == "thin":
        p.curve([(cx - rx + 2, cy), (cx - rx - 10, cy + 4), (cx - rx - 16, cy + 2)], 1.6, dk(m, .1), taper=0.8)
    elif tail == "thick":
        p.curve([(cx - rx + 2, cy + 2), (cx - rx - 10, cy + 8)], 5 * k, m, taper=0.4)
    elif tail == "hair":
        p.curve([(cx - rx + 2, cy - 2), (cx - rx - 4, cy + 4), (cx - rx - 5, cy + 14)], 4 * k, s2, taper=0.6)
    elif tail == "spikes":
        p.curve([(cx - rx + 2, cy), (cx - rx - 10, cy + 2)], 6 * k, m, taper=0.6)
        for i in range(3):
            p.poly([(cx - rx - 2 - i * 4, cy - 2), (cx - rx - 4 - i * 4, cy - 7), (cx - rx - 6 - i * 4, cy - 1)], a)
    paw = kind in ("bear", "dog", "fox", "cat", "rat", "mole", "otter", "capybara", "bone")
    legcol = dk(m, .25)
    # legs: far ones, body, near ones
    for lx in (cx - rx * 0.6 + 3, cx + rx * 0.6 + 3):
        p.limb(lx, cy + ry * 0.3, lx + 0.5, g, 4.5 * k, legcol, foot=dk(legcol, .4), taper=0.85 if paw else 0.55)
    if kind == "bone" or o.get("bones"):
        p.ell(cx, cy, rx, ry, m)
        for i in range(5):
            x = cx - rx + 6 + i * 6
            p.line([(x, cy - ry + 2), (x + 1, cy + ry - 2)], dk(m, .45))
    else:
        p.ell(cx, cy, rx, ry, m)
        p.ell(cx + 2, cy + ry * 0.55, rx * 0.7, ry * 0.3, lt(m, .15) if kind not in ("bear",) else dk(m, .1), shade=False)
    for lx in (cx - rx * 0.6, cx + rx * 0.6):
        p.limb(lx, cy + ry * 0.3, lx - 0.5, g, 5 * k, m, foot=dk(m, .45), taper=0.85 if paw else 0.55)
    spots = o.get("spots")
    if spots is True:  # a boss's "spots": the accent colour
        spots = a if kind != "cat" or a != m else dk(m, .5)
    if spots:
        rnd = random.Random(spots + kind)
        for i in range(14):
            x, y = cx + rnd.uniform(-rx * .8, rx * .8), cy + rnd.uniform(-ry * .6, ry * .4)
            p.ell(x, y, 1.4 * k, 1.1 * k, spots, shade=False)
    if o.get("fire"):
        rnd = random.Random(kind)
        for i in range(7):
            x = cx - rx + 4 + i * (2 * rx - 8) / 6
            p.poly([(x - 2, cy - ry + 2), (x + rnd.uniform(-1, 1), cy - ry - 4 - rnd.randint(0, 4)), (x + 2, cy - ry + 2)], a, shade=False)
    if o.get("scars"):
        for i in range(3):
            p.line([(cx - 4 + i * 3, cy - 6), (cx + i * 3, cy + 1)], lt(m, .4))
    neck_up = kind in ("goat", "deer", "bull", "horse")
    if neck_up:
        p.poly([(cx + rx * 0.5, cy - ry * 0.6), (cx + rx * 0.5 + 8 * k, cy - ry - 8 * k), (cx + rx * 0.5 + 13 * k, cy - ry - 4 * k), (cx + rx * 0.8, cy + 2)], m)
        quad_head(p, c, o, cx + rx * 0.5 + 10 * k, cy - ry - 8 * k, k)
    else:
        quad_head(p, c, o, cx + rx * 0.9, cy - ry * 0.55, k)


# ================================================================== birds (52 x 40, or big)
def bird(p, c, o):
    g = p.h - 2
    m, s2, a, e = c["main"], c["second"], c["accent"], c["eye"]
    style = o.get("style", "perch")
    beak = o.get("beak", "short")
    if style == "flying":
        cx, cy = 26, g - 18
        p.poly([(cx - 4, cy), (cx - 22, cy - 12), (cx - 18, cy - 4), (cx - 22, cy + 2), (cx - 2, cy + 4)], dk(m, .15))
        p.poly([(cx - 12, cy + 2), (cx - 20, cy + 6), (cx - 10, cy + 6)], m)
        p.ell(cx, cy + 1, 9, 4.5, m)
        p.poly([(cx - 2, cy), (cx + 6, cy - 16), (cx + 10, cy - 14), (cx + 6, cy + 1)], m)
        for i in range(3):
            p.line([(cx + 1 + i * 2, cy - 2), (cx + 6 + i * 2, cy - 13)], dk(m, .3))
        hx, hy = cx + 10, cy - 1
        p.ell(hx, hy, 3.6, 3.2, s2 if o.get("bald") is None else s2)
        if o.get("crest"):
            p.poly([(hx - 2, hy - 2), (hx - 5, hy - 7), (hx, hy - 3)], s2)
    elif style == "wader":
        cx, cy = 22, g - 16
        for lx in (cx - 1, cx + 2):
            p.line([(lx, cy + 4), (lx, g)], dk(a, .2))
        p.poly([(cx - 8, cy + 2), (cx - 14, cy + 6), (cx - 6, cy + 5)], s2)
        p.ell(cx, cy, 8, 5, m)
        p.poly([(cx - 6, cy - 2), (cx + 2, cy - 1), (cx - 2, cy + 4)], s2)
        p.curve([(cx + 6, cy - 2), (cx + 9, cy - 9), (cx + 6, cy - 14), (cx + 8, cy - 18)], 2.6, m, taper=0.8)
        hx, hy = cx + 9, cy - 19
        p.ell(hx, hy, 3, 2.6, m)
    elif style == "owl":
        cx, cy = 24, g - 12
        p.line([(cx - 2, g - 2), (cx - 2, g)], "#7a6a5a"); p.line([(cx + 2, g - 2), (cx + 2, g)], "#7a6a5a")
        p.ell(cx, cy, 9, 11, m)
        p.ell(cx + 1, cy + 3, 6, 7, s2, shade=False)
        for i in range(4):
            p.px(cx - 1 + (i % 2) * 3, cy + 1 + i * 2, a)
        p.ell(cx, cy - 10, 8, 7, m)
        p.poly([(cx - 6, cy - 14), (cx - 8, cy - 20), (cx - 3, cy - 16)], m)
        p.poly([(cx + 6, cy - 14), (cx + 8, cy - 20), (cx + 3, cy - 16)], m)
        for ex in (cx - 3, cx + 4):
            p.ell(ex, cy - 10, 2.6, 2.6, lt(s2, .3), shade=False)
            eye(p, ex, cy - 10, e, 1.2)
        p.poly([(cx, cy - 8), (cx + 2, cy - 8), (cx + 1, cy - 5)], "#c89030")
        return
    elif style == "duck":
        cx, cy = 24, g - 6
        p.ell(cx, cy, 10, 5.5, m)
        p.poly([(cx - 8, cy - 2), (cx - 14, cy - 5), (cx - 9, cy + 1)], m)
        p.poly([(cx - 5, cy - 2), (cx + 3, cy - 2), (cx - 1, cy + 3)], s2)
        p.curve([(cx + 6, cy - 3), (cx + 8, cy - 10)], 3.6, a, taper=0.9)
        hx, hy = cx + 9, cy - 12
        p.ell(hx, hy, 3.6, 3.2, a)
        p.poly([(hx + 2, hy), (hx + 8, hy + 1), (hx + 7, hy + 2.5), (hx + 2, hy + 2)], "#e0a020")
        eye(p, hx + 1, hy - 1, e, 0.8)
        return
    else:  # perched
        cx, cy = 22, g - 12
        for lx in (cx - 1, cx + 2):
            p.line([(lx, cy + 6), (lx, g)], "#7a6a5a")
        p.poly([(cx - 4, cy + 4), (cx - 10, cy + 14), (cx - 6, cy + 14), (cx, cy + 5)], dk(m, .1))
        p.ell(cx, cy, 6, 7, m)
        p.ell(cx + 2, cy + 2, 3.5, 4, s2, shade=False)
        p.poly([(cx - 6, cy - 3), (cx + 1, cy - 2), (cx - 1, cy + 7), (cx - 7, cy + 5)], dk(m, .2))
        hx, hy = cx + 2, cy - 8
        p.ell(hx, hy, 4.4, 4, m if not o.get("bald") else s2)
        if o.get("crest"):
            p.poly([(hx - 3, hy - 2), (hx - 3, hy - 9), (hx + 3, hy - 3)], m)
        if o.get("patch"):
            p.ell(hx + 2, hy - 1, 1.6, 1.6, "#1a1a1a", shade=False)
    # the beak
    bc = a
    if beak == "short":
        p.poly([(hx + 2, hy - 1), (hx + 7, hy + 0.5), (hx + 2, hy + 2)], bc)
    elif beak in ("hook", "iron"):
        bc = "#b8b8c8" if beak == "iron" else bc
        p.poly([(hx + 2, hy - 2), (hx + 7, hy - 1), (hx + 7, hy + 3), (hx + 5, hy + 2), (hx + 2, hy + 2)], bc)
    elif beak == "long":
        p.poly([(hx + 2, hy - 1), (hx + 12, hy + 1), (hx + 2, hy + 2)], bc)
    elif beak == "toucan":
        p.poly([(hx + 2, hy - 3), (hx + 11, hy - 1), (hx + 12, hy + 2), (hx + 2, hy + 2)], bc)
        p.line([(hx + 3, hy), (hx + 11, hy + 1)], dk(bc, .4))
    elif beak == "pouch":
        p.poly([(hx + 2, hy - 1), (hx + 13, hy), (hx + 2, hy + 1)], bc)
        p.poly([(hx + 3, hy + 1), (hx + 12, hy + 1), (hx + 6, hy + 5)], lt(bc, .2))
    elif beak == "bent":
        p.poly([(hx + 2, hy - 1), (hx + 7, hy), (hx + 8, hy + 4), (hx + 6, hy + 4), (hx + 5, hy + 2), (hx + 2, hy + 2)], "#f0e8e0")
        p.poly([(hx + 6, hy + 2), (hx + 8, hy + 4), (hx + 6, hy + 4)], "#1a1a1a")
    if style == "wader" and beak == "short":
        p.poly([(hx + 2, hy - 1), (hx + 11, hy + 0.5), (hx + 2, hy + 1.5)], bc)
    if o.get("metal"):
        for i in range(3):
            p.px(hx - 6 - i * 3, hy + 6 + i, "#e8e8f0")
    if o.get("fire"):
        for (x, y) in ((hx - 8, hy + 2), (hx - 12, hy + 4), (hx - 16, hy + 1)):
            p.ell(x, y, 1.4, 2, a, shade=False)
    eye(p, hx + 1, hy - 1, e, 0.9)
    if o.get("spots"):
        for i in range(5):
            p.px(hx - 8 + i * 2, hy + 8 + (i % 2) * 2, "#ffffff")


# ================================================================== serpents and lizards
def serpent(p, c, o):
    g = p.h - 2
    m, s2, a, e = c["main"], c["second"], c["accent"], c["eye"]
    style = o.get("style", "coil")
    big = p.w > 52
    k = 1.25 if big else 1.0
    if style == "coil":
        p.ell(24 * k, g - 5 * k, 14 * k, 5 * k, m)
        p.ell(22 * k, g - 10 * k, 11 * k, 4.5 * k, lt(m, .05))
        pts = [(28 * k, g - 12 * k), (34 * k, g - 18 * k), (34 * k, g - 24 * k), (38 * k, g - 27 * k)]
    elif style == "rise":
        p.curve([(4, g - 3), (14, g - 2), (24, g - 4), (30, g - 10)], 6 * k, m, taper=0.8)
        pts = [(30, g - 10), (32 * k, g - 20 * k), (36 * k, g - 26 * k)]
    else:  # wave
        p.curve([(3, g - 3), (10, g - 8), (18, g - 2), (26, g - 8), (32, g - 4)], 4.4 * k, m, taper=0.8)
        pts = [(32, g - 4), (38, g - 8)]
    p.curve(pts, 5 * k, m, taper=0.85)
    hx, hy = pts[-1]
    if o.get("hood"):
        p.ell(hx - 1, hy + 3, 5 * k, 6 * k, s2)
    p.ell(hx + 2, hy, 5 * k, 3.6 * k, m)
    p.poly([(hx + 5 * k, hy + 1), (hx + 9 * k, hy + 3), (hx + 7 * k, hy + 1.5)], "#e04040")
    eye(p, hx + 3 * k, hy - 1, e, 0.9)
    pat = o.get("pattern")
    rnd = random.Random(str(o) + m)
    if pat == "x":
        for i in range(5):
            x = 12 + i * 6
            p.line([(x - 2, g - 9), (x + 2, g - 4)], s2); p.line([(x + 2, g - 9), (x - 2, g - 4)], s2)
    elif pat == "spots":
        for i in range(9):
            p.ell(rnd.uniform(10, 34) * k, g - rnd.uniform(4, 12) * k, 1.4, 1.1, s2, shade=False)
    elif pat in ("bands", "coral"):
        for i in range(6):
            x = 10 + i * 5
            p.line([(x, g - 12 * k), (x, g - 2)], s2 if pat == "bands" else (s2 if i % 2 else a), 2)
    if o.get("crest"):
        for i in range(3):
            p.poly([(hx - 3 - i * 3, hy - 2), (hx - 4 - i * 3, hy - 7), (hx - 1 - i * 3, hy - 3)], a)
    if o.get("water"):
        p.ell(24 * k, g, 20 * k, 2, "#5aa0c8", shade=False)
    if o.get("rainbow"):
        for i, col in enumerate(["#d0304a", "#f0c040", "#40a060", "#3a6ae0"]):
            p.line([(10 + i * 6, g - 9), (12 + i * 6, g - 3)], col, 2)
    if o.get("fire"):
        for i in range(4):
            p.ell(14 + i * 6, g - 12, 1.4, 2.2, a, shade=False)
    if o.get("crystal"):
        for i in range(4):
            p.poly([(12 + i * 6, g - 9), (14 + i * 6, g - 15), (16 + i * 6, g - 9)], a)
    if o.get("spots") is True:
        for i in range(9):
            p.ell(rnd.uniform(10, 34) * k, g - rnd.uniform(4, 12) * k, 1.4, 1.1, s2, shade=False)
    if o.get("bands") is True:
        for i in range(6):
            p.line([(10 + i * 5, g - 12 * k), (10 + i * 5, g - 2)], s2, 2)


def lizard(p, c, o):
    g = p.h - 2
    m, s2, a, e = c["main"], c["second"], c["accent"], c["eye"]
    style = o.get("style", "low")
    big = p.w > 52
    k = 1.2 if big else 1.0
    croc = style == "croc"
    cy = g - (5 if croc else 6) * k
    p.curve([(14 * k, cy), (6 * k, cy + 1), (1, cy + 4)], 6 * k if croc else 4 * k, m, taper=0.3)
    for lx in (14 * k, 28 * k):
        p.limb(lx + 2, cy + 1, lx + 4, g, 3 * k, dk(m, .25), taper=0.9)
    p.ell(22 * k, cy, 11 * k, 4.5 * k, m)
    p.ell(22 * k, cy + 2.5 * k, 8 * k, 1.6 * k, a if not croc else lt(a, .1), shade=False)
    for lx in (12 * k, 26 * k):
        p.limb(lx, cy + 1, lx - 2, g, 3.4 * k, m, taper=0.9)
    hx, hy = 33 * k, cy - 2 * k
    if croc:
        p.poly([(hx - 2, hy - 2), (hx + 16 * k, hy), (hx + 16 * k, hy + 4), (hx - 2, hy + 4)], m)
        for x in range(int(hx + 2), int(hx + 15 * k), 3):
            p.px(x, hy + 2, "#f0ece0")
        p.ell(hx + 1, hy - 2, 2, 1.8, m)
        eye(p, hx + 1, hy - 2.5, e, 0.8)
        for i in range(6):
            p.poly([(10 * k + i * 4, cy - 4 * k), (12 * k + i * 4, cy - 7 * k), (14 * k + i * 4, cy - 4 * k)], s2)
        return
    p.ell(hx + 3, hy, 5 * k, 3.4 * k, m)
    eye(p, hx + 4, hy - 1, e, 0.8)
    if style in ("frill",):
        p.poly([(hx - 2, hy - 5), (hx - 4, hy + 6), (hx + 1, hy + 3)], a)
    if style == "crest":
        for i in range(7):
            p.poly([(12 * k + i * 3, cy - 4 * k), (13 * k + i * 3, cy - 8 * k), (14 * k + i * 3, cy - 4 * k)], s2)
    if style == "horned":
        for i in range(4):
            p.poly([(hx - 1 + i * 2, hy - 3), (hx - 2 + i * 2, hy - 6), (hx + i * 2, hy - 3)], s2)
        for i in range(6):
            p.px(14 + i * 3, cy - 4, s2)
    if o.get("fire"):
        for i in range(5):
            p.ell(12 * k + i * 5, cy - 5 * k, 1.2, 2, s2, shade=False)
            p.px(12 * k + i * 5, cy - 5 * k, a)


def frog(p, c, o):
    g = p.h - 2
    m, s2, a, e = c["main"], c["second"], c["accent"], c["eye"]
    bx, by = 24, g - 7
    p.ell(bx - 7, by + 3, 6, 4, m)
    p.ell(bx, by, 9, 6.5, m)
    p.ell(bx + 2, by + 3, 6, 2.6, a if not o.get("glass") else lt(m, .4), shade=False)
    p.ell(bx + 6, by - 4, 5.5, 4, m)
    for ex in (bx + 4, bx + 8):
        p.ell(ex, by - 8, 2.2, 2.2, m)
        eye(p, ex, by - 8.5, e, 1.0)
    p.line([(bx + 7, by), (bx + 11, by - 0.5)], dk(m, .5))
    p.limb(bx + 6, by + 2, bx + 9, g, 2.6, m, taper=0.9)
    p.line([(bx - 13, g), (bx - 4, g)], m, 2)
    rnd = random.Random(m + s2)
    if o.get("spots") or o.get("warts"):
        for i in range(7):
            p.ell(bx + rnd.uniform(-8, 6), by + rnd.uniform(-4, 1), 1.2, 1.0, s2, shade=False)
    if o.get("stripes"):
        for i in range(4):
            p.line([(bx - 6 + i * 4, by - 5), (bx - 4 + i * 4, by + 2)], s2, 2)
    if o.get("glass"):
        p.ell(bx - 1, by, 3, 2, "#c85050", shade=False)


def turtle(p, c, o):
    g = p.h - 2
    m, s2, a, e = c["main"], c["second"], c["accent"], c["eye"]
    for lx in (14, 32):
        p.limb(lx, g - 6, lx, g, 4, s2, taper=0.9)
    p.poly([(4, g - 6), (8, g - 16), (20, g - 21), (32, g - 18), (40, g - 8), (40, g - 5), (4, g - 5)], m)
    for (x, y) in ((14, g - 13), (24, g - 15), (32, g - 11)):
        p.poly([(x - 4, y), (x, y - 3), (x + 4, y), (x, y + 3)], a)
    p.rect(4, g - 7, 40, g - 5, dk(m, .3), shade=False)
    p.curve([(38, g - 8), (44, g - 9), (47, g - 11)], 4, s2, taper=0.9)
    eye(p, 47, g - 12, e, 0.8)


def fish(p, c, o):
    g = p.h - 2
    m, s2, a, e = c["main"], c["second"], c["accent"], c["eye"]
    style = o.get("style", "fish")
    big = p.w > 52
    k = 1.25 if big else 1.0
    cy = g - 14 * k
    L = {"shark": 16, "barracuda": 18, "catfish": 15, "manatee": 15, "piranha": 10, "fish": 11, "big": 17}.get(style, 12) * k
    H_ = {"shark": 7, "barracuda": 4, "catfish": 7, "manatee": 9, "piranha": 9, "fish": 7, "big": 8}.get(style, 6) * k
    cx = 26 * k
    if style == "manatee":
        p.ell(cx - L - 2, cy + 2, 6, 6, m)
    else:
        p.poly([(cx - L + 2, cy), (cx - L - 8 * k, cy - H_ * 0.9), (cx - L - 6 * k, cy), (cx - L - 8 * k, cy + H_ * 0.9)], s2 if style != "shark" else m)
    p.ell(cx, cy, L, H_, m)
    p.ell(cx + 2, cy + H_ * 0.5, L * 0.8, H_ * 0.35, s2 if style in ("shark", "barracuda", "catfish", "piranha") else lt(m, .2), shade=False)
    if style == "shark":
        p.poly([(cx - 4, cy - H_ + 1), (cx + 1, cy - H_ - 8 * k), (cx + 5, cy - H_ + 1)], m)
        for i in range(3):
            p.line([(cx + L - 9 + i * 2, cy - 2), (cx + L - 10 + i * 2, cy + 2)], dk(m, .4))
        p.line([(cx + L - 5, cy + 3), (cx + L, cy + 2)], "#f0f0f0")
    elif style in ("piranha",):
        p.poly([(cx + L - 6, cy + 2), (cx + L + 1, cy + 1), (cx + L - 2, cy + 5)], dk(m, .3))
        for x in range(int(cx + L - 6), int(cx + L), 2):
            p.px(x, cy + 2, "#ffffff")
        p.poly([(cx - 4, cy - H_ + 1), (cx, cy - H_ - 4), (cx + 4, cy - H_ + 1)], s2)
    elif style == "catfish":
        for s in (0, 2):
            p.curve([(cx + L - 2, cy + 1 + s), (cx + L + 6, cy + 4 + s * 2), (cx + L + 8, cy + 8 + s)], 1.2, dk(m, .3), taper=1)
    elif style == "barracuda":
        p.poly([(cx + L - 5, cy + 1), (cx + L + 5, cy + 1), (cx + L - 5, cy + 3)], dk(m, .2))
        for x in range(int(cx + L - 4), int(cx + L + 4), 2):
            p.px(x, cy + 1, "#ffffff")
    elif style == "manatee":
        p.limb(cx + 4, cy + 4, cx + 8, cy + H_ + 3, 3, dk(m, .15), taper=0.8)
        p.ell(cx + L - 1, cy + 1, 5, 4, lt(m, .1))
    else:
        p.poly([(cx - 4, cy - H_ + 1), (cx, cy - H_ - 4), (cx + 4, cy - H_ + 1)], a)
    eye(p, cx + L - 5, cy - 2, e, 1.0)
    if o.get("rainbow"):
        for i, col in enumerate(["#e0302a", "#f0c040", "#40a060", "#3a6ae0"]):
            p.line([(cx - L + 4 + i * 4, cy - H_ + 2), (cx - L + 4 + i * 4, cy + H_ - 2)], col)
    p.ell(cx, g, L + 6, 1.4, "#5a90b0", shade=False)


def crab(p, c, o):
    g = p.h - 2
    m, s2, a, e = c["main"], c["second"], c["accent"], c["eye"]
    big = p.w > 52
    k = 1.25 if big else 1.0
    cx, cy = 26, g - 7 * k
    for s in (-1, 1):
        for i in range(3):
            p.line([(cx + s * (4 + i * 3), cy + 2), (cx + s * (9 + i * 3), cy + 4), (cx + s * (11 + i * 3), g)], s2, 1)
    if o.get("shell"):
        p.ell(cx - 6, cy - 5, 10, 8, "#c8a070")
        p.curve([(cx - 12, cy - 5), (cx - 6, cy - 10), (cx, cy - 6)], 1.6, dk("#c8a070", .3), taper=1)
    p.ell(cx, cy, 11 * k, 6 * k, m)
    p.ell(cx, cy + 2, 8 * k, 2.4, s2, shade=False)
    for s in (-1, 1):
        p.curve([(cx + s * 9 * k, cy - 2), (cx + s * 14 * k, cy - 8 * k), (cx + s * 16 * k, cy - 11 * k)], 3 * k, m, taper=0.9)
        p.ell(cx + s * 17 * k, cy - 13 * k, 4 * k, 3 * k, m)
        p.poly([(cx + s * 17 * k, cy - 14 * k), (cx + s * 22 * k, cy - 18 * k), (cx + s * 19 * k, cy - 12 * k)], a if a != m else lt(m, .3))
    for ex in (cx - 3, cx + 3):
        p.line([(ex, cy - 5), (ex, cy - 9)], m)
        eye(p, ex, cy - 10, e, 1.0)


def bug(p, c, o):
    g = p.h - 2
    m, s2, a, e = c["main"], c["second"], c["accent"], c["eye"]
    style = o.get("style", "beetle")
    cx, cy = 24, g - 7
    if style == "spider":
        abd = 9 if o.get("hairy") else 8
        for s in (-1, 1):
            for kk in range(4):
                x0 = cx + 2 + kk * 2
                span = 12 if o.get("long") else 8
                p.line([(x0, cy - 1), (x0 + (kk - 1.5) * 5, cy - 9 + abs(kk - 1.5) * 2), (x0 + (kk - 1.5) * span + s * 2, g)], s2, 1 if s < 0 else 2)
        p.ell(cx - 7, cy - 3, abd, abd * 0.8, m)
        if o.get("hairy"):
            for i in range(10):
                p.px(cx - 14 + i * 1.5, cy - 3 - abd * 0.8 + (i % 2), lt(m, .3))
        p.poly([(cx - 9, cy - 6), (cx - 6, cy - 8), (cx - 3, cy - 6), (cx - 6, cy - 2)], a)
        p.ell(cx + 4, cy - 1, 5, 4, m)
        for ex, ey in ((cx + 6, cy - 3), (cx + 8, cy - 2), (cx + 7, cy - 4)):
            p.px(ex, ey, e)
        return
    if style == "scorpion":
        p.curve([(cx - 8, cy), (cx - 15, cy - 3), (cx - 16, cy - 11), (cx - 11, cy - 16), (cx - 5, cy - 14)], 4, m, taper=0.5)
        p.poly([(cx - 5, cy - 16), (cx - 1, cy - 13), (cx - 5, cy - 12)], a)
        for kk in range(4):
            p.line([(cx - 6 + kk * 4, cy + 2), (cx - 8 + kk * 4, g)], s2)
        p.ell(cx, cy, 10, 4, m)
        for s in (-1, 1):
            p.curve([(cx + 8, cy + s), (cx + 14, cy - 2 + s * 2), (cx + 16, cy - 4 + s * 3)], 2.4, m, taper=0.9)
            p.ell(cx + 18, cy - 5 + s * 3, 3, 2, m)
        p.px(cx + 8, cy - 2, e)
        return
    if style == "dragonfly":
        p.line([(cx - 16, cy - 8), (cx + 4, cy - 8)], m, 2)
        for s in (-1, 1):
            p.ell(cx - 2, cy - 8 + s * 5, 9, 2.6, a[:7] if isinstance(a, str) else a, shade=False)
        p.ell(cx + 6, cy - 8, 3, 3, m)
        eye(p, cx + 7, cy - 9, e, 1.0)
        for kk in range(3):
            p.line([(cx + kk * 2, cy - 7), (cx + kk * 2 - 1, cy - 2)], s2)
        return
    if style == "cricket":
        p.limb(cx - 2, cy - 2, cx - 12, cy - 10, 3, m, taper=0.7)
        p.line([(cx - 12, cy - 10), (cx - 14, g)], s2)
        for kk in range(2):
            p.line([(cx + kk * 4, cy + 1), (cx + kk * 4 + 2, g)], s2)
        p.ell(cx, cy - 1, 10, 4, m)
        p.ell(cx + 9, cy - 3, 4, 3.6, m)
        p.line([(cx + 11, cy - 6), (cx + 20, cy - 16)], s2)
        p.line([(cx + 10, cy - 6), (cx + 16, cy - 18)], s2)
        p.px(cx + 10, cy - 4, e)
        return
    # ants and beetles
    for kk in range(3):
        x = cx - 3 + kk * 4
        p.line([(x, cy + 1), (x - 3 + kk * 2, cy + 4), (x - 5 + kk * 3, g)], s2)
    if style == "ant":
        fat = o.get("fat")
        p.ell(cx - 9, cy - 1, 7 if fat else 5.5, 5.5 if fat else 4.2, m)
        p.ell(cx, cy - 2, 3.5, 2.8, m)
        p.ell(cx + 7, cy - 3, 4.5 if o.get("big_jaw") else 4, 3.8, m)
        p.poly([(cx + 10, cy - 1), (cx + 15, cy + 1), (cx + 11, cy + 2)], a)
        p.poly([(cx + 10, cy - 4), (cx + 15, cy - 6), (cx + 11, cy - 6)], a)
        p.line([(cx + 8, cy - 6), (cx + 11, cy - 12), (cx + 14, cy - 13)], s2)
        eye(p, cx + 8, cy - 4, e, 0.8)
        if o.get("leaf"):
            p.poly([(cx + 4, cy - 6), (cx + 2, cy - 18), (cx + 12, cy - 16)], "#4a8a2a")
        return
    p.ell(cx - 2, cy - 2, 11, 7, m)
    p.line([(cx - 2, cy - 9), (cx - 2, cy + 4)], dk(m, .45))
    p.ell(cx - 5, cy - 5, 3, 1.6, lt(m, .35), shade=False)
    p.ell(cx + 10, cy, 4, 3.4, s2)
    p.poly([(cx + 12, cy - 2), (cx + 17, cy - 6), (cx + 14, cy)], a)
    eye(p, cx + 11, cy - 1, e, 0.8)
    if o.get("glow"):
        for i in range(4):
            p.px(cx - 8 + i * 4, cy - 3 + (i % 2), a)


def bat(p, c, o):
    g = p.h - 2
    m, s2, a, e = c["main"], c["second"], c["accent"], c["eye"]
    cx, cy = 26, g - 16
    for s in (-1, 1):
        p.poly([(cx, cy - 2), (cx + s * 10, cy - 10), (cx + s * 22, cy - 6), (cx + s * 19, cy + 2), (cx + s * 14, cy), (cx + s * 10, cy + 4), (cx + s * 5, cy + 2)], s2)
        p.line([(cx, cy - 2), (cx + s * 10, cy - 10), (cx + s * 22, cy - 6)], dk(s2, .4))
    p.ell(cx, cy, 5, 6, m)
    p.ell(cx, cy - 7, 4, 3.6, m)
    for s in (-1, 1):
        p.poly([(cx + s * 1, cy - 9), (cx + s * 4, cy - 15), (cx + s * 4, cy - 8)], m)
    glow_eyes(p, [(cx - 2, cy - 8), (cx + 1, cy - 8)], e)
    p.px(cx - 1, cy - 5, "#ffffff"); p.px(cx + 1, cy - 5, "#ffffff")
    if o.get("vamp"):
        p.px(cx, cy - 4, "#c02020")


def worm(p, c, o):
    g = p.h - 2
    m, s2, a, e = c["main"], c["second"], c["accent"], c["eye"]
    pts = [(4, g - 3), (12, g - 6), (20, g - 3), (28, g - 7), (33, g - 14), (36, g - 20)]
    p.curve(pts, 8, m, taper=0.8)
    for i, (x, y) in enumerate(pts[:-1]):
        p.line([(x - 1, y - 3), (x + 1, y + 3)], s2 if not o.get("iron") else "#c8c8d8")
    hx, hy = pts[-1]
    p.ell(hx + 1, hy, 4.5, 4, m)
    p.ell(hx + 3, hy + 1, 2.4, 2, dk(a, .2), shade=False)
    for k in range(4):
        a_ = k * 1.57 + 0.4
        p.px(hx + 3 + math.cos(a_) * 2.4, hy + 1 + math.sin(a_) * 2, "#f0ece0")
    glow_eyes(p, [(hx - 1, hy - 3)], e)


def monkey(p, c, o):
    g = p.h - 1
    m, s2, a, e = c["main"], c["second"], c["accent"], c["eye"]
    L = 1.3 if o.get("long") else 1.0
    cx, cy = 26, g - 20
    p.curve([(cx - 6, cy + 6), (cx - 16, cy + 4), (cx - 20, cy - 6), (cx - 16, cy - 12)], 2.4, m, taper=0.8)
    for lx, dx in ((cx - 4, -2), (cx + 3, 2)):
        p.limb(lx, cy + 6, lx + dx, g, 3.6, dk(m, .15), foot=dk(m, .3))
    p.ell(cx, cy, 7, 9, m)
    p.ell(cx + 1, cy + 2, 4, 5, a if a else lt(m, .3), shade=False)
    p.limb(cx + 4, cy - 5, cx + 12, cy - 18 * L, 3, m, foot=s2)
    p.limb(cx - 4, cy - 4, cx - 8, cy + 8 * L, 3, dk(m, .2))
    hx, hy = cx + 2, cy - 13
    p.ell(hx, hy, 6, 5.5, m)
    p.ell(hx + 2, hy + 1, 3.6, 3.2, a, shade=False)
    eye(p, hx + 1, hy - 1, e, 0.8); eye(p, hx + 4, hy - 1, e, 0.8)
    if o.get("howl"):
        p.ell(hx + 4, hy + 3, 1.6, 1.8, "#2a0a0a", shade=False)
        p.ell(hx, hy + 6, 4, 3, s2)


def snail(p, c, o):
    g = p.h - 2
    m, s2, a, e = c["main"], c["second"], c["accent"], c["eye"]
    p.poly([(6, g), (10, g - 5), (38, g - 5), (44, g - 10), (46, g - 2), (42, g)], s2)
    p.ell(22, g - 13, 11, 10, m)
    p.curve([(22, g - 13), (26, g - 15), (25, g - 19), (19, g - 19), (15, g - 13)], 2, a, taper=1, shade=False)
    for s in (0, 3):
        p.line([(42 + s, g - 9), (44 + s, g - 17)], s2)
        p.px(44 + s, g - 18, e)


# ================================================================== spirits (52 x 40 or 64 x 61)
def spirit(p, c, o):
    g = p.h - 2
    m, s2, a, e = c["main"], c["second"], c["accent"], c["eye"]
    style = o.get("style", "ghost")
    W_ = p.w
    cx = W_ // 2
    cy = g - p.h * 0.45
    R = p.h * 0.28
    rnd = random.Random(style + m)
    if style in ("ghost", "woman", "water", "rainbow", "painting", "rings", "wind", "cloud", "dust", "flame", "crystal", "lantern", "scream", "eye", "skull"):
        pass
    if style == "flame":
        for i in range(5):
            dx = (i - 2) * R * 0.3
            p.poly([(cx + dx - R * 0.4, cy + R * 0.6), (cx + dx + rnd.uniform(-2, 2), cy - R * (1.2 + rnd.random() * 0.6)), (cx + dx + R * 0.4, cy + R * 0.6)], m if i % 2 else s2, shade=False)
        p.ell(cx, cy + R * 0.3, R * 0.9, R * 0.7, m)
        p.ell(cx, cy + R * 0.4, R * 0.5, R * 0.4, s2, shade=False)
        glow_eyes(p, [(cx - 3, cy), (cx + 2, cy)], e)
        if o.get("mouth"):
            p.ell(cx, cy + R * 0.5, 3, 2, "#3a0a04", shade=False)
        return
    if style == "skull":
        p.ell(cx, cy, R * 0.9, R * 0.85, m)
        p.rect(cx - R * 0.5, cy + R * 0.5, cx + R * 0.5, cy + R * 0.95, m)
        for ex in (cx - R * 0.35, cx + R * 0.35):
            p.ell(ex, cy, R * 0.22, R * 0.25, "#1a1410", shade=False)
            p.px(ex, cy, e)
        for x in range(int(cx - R * 0.4), int(cx + R * 0.5), 2):
            p.px(x, cy + R * 0.8, "#1a1410")
        if s2 != m:
            p.line([(cx - R * 0.6, cy - R * 0.4), (cx + R * 0.6, cy - R * 0.5)], s2, 2)
        if o.get("chatter"):
            p.rect(cx - R * 0.5, cy + R * 1.05, cx + R * 0.5, cy + R * 1.25, m)
        return
    if style == "eye":
        p.ell(cx, cy, R, R * 0.6, s2)
        p.ell(cx + 2, cy, R * 0.45, R * 0.45, m)
        p.ell(cx + 2, cy, R * 0.2, R * 0.2, "#1a1010", shade=False)
        p.px(cx + 3, cy - 2, "#ffffff")
        for i in range(6):
            a_ = math.pi * (1 + i / 5)
            p.line([(cx + math.cos(a_) * R, cy + math.sin(a_) * R * 0.6), (cx + math.cos(a_) * R * 1.4, cy + math.sin(a_) * R)], m)
        return
    if style == "lantern":
        R *= 1.5
        cy = g - R * 1.0
        p.line([(cx, cy - R * 1.2), (cx, cy - R * 0.7)], m)
        p.poly([(cx - R * 0.5, cy - R * 0.7), (cx + R * 0.5, cy - R * 0.7), (cx + R * 0.6, cy + R * 0.7), (cx - R * 0.6, cy + R * 0.7)], m)
        p.poly([(cx - R * 0.4, cy - R * 0.5), (cx + R * 0.4, cy - R * 0.5), (cx + R * 0.45, cy + R * 0.5), (cx - R * 0.45, cy + R * 0.5)], s2, shade=False)
        p.ell(cx, cy, R * 0.25, R * 0.4, a, shade=False)
        glow_eyes(p, [(cx - 3, cy - 2), (cx + 2, cy - 2)], "#3a2a1a")
        return
    if style == "crystal":
        for i in range(5):
            a_ = -math.pi / 2 + (i - 2) * 0.45
            L = R * (1.3 if i == 2 else 0.9)
            p.poly([(cx - 3 + i * 1.5, cy + R * 0.6), (cx + math.cos(a_) * L, cy + math.sin(a_) * L), (cx + 3 + i * 1.5, cy + R * 0.6)], m if i % 2 else s2)
        p.ell(cx, cy + R * 0.5, R * 0.6, R * 0.4, m)
        glow_eyes(p, [(cx - 3, cy + 1), (cx + 2, cy + 1)], e)
        return
    if style in ("cloud", "dust", "wind"):
        for i in range(6):
            p.ell(cx + rnd.uniform(-R, R), cy + rnd.uniform(-R * 0.5, R * 0.3), R * rnd.uniform(0.4, 0.65), R * rnd.uniform(0.35, 0.5), m if i % 2 else s2, shade=style == "cloud")
        if style in ("dust", "wind"):
            for i in range(4):
                p.curve([(cx - R + i * 3, cy + R * 0.4 + i * 2), (cx, cy + R * 0.7 + i * 2), (cx + R * 0.6 - i * 2, cy + R * 1.1 + i * 2)], 1.6, s2, taper=0.6)
        glow_eyes(p, [(cx - 3, cy - 1), (cx + 3, cy - 1)], e)
        if o.get("rain"):
            for i in range(6):
                x = cx - R + i * R * 0.4
                p.line([(x, cy + R * 0.6), (x - 1, cy + R * 1.2)], "#80a8ff")
        return
    if style == "scream":
        p.ell(cx, cy, R * 0.9, R, m)
        p.ell(cx, cy + R * 0.3, R * 0.4, R * 0.55, "#2a0604", shade=False)
        glow_eyes(p, [(cx - 4, cy - R * 0.4), (cx + 3, cy - R * 0.4)], e)
        for i in range(3):
            p.curve([(cx - R * 0.9, cy + i * 3), (cx - R * 1.4, cy - 4 + i * 4)], 2, s2, taper=0.5)
            p.curve([(cx + R * 0.9, cy + i * 3), (cx + R * 1.4, cy - 4 + i * 4)], 2, s2, taper=0.5)
        return
    # ghostly figures: a head and a body that frays into a tail
    tail = [(cx - 2, cy + R * 0.6), (cx - R * 0.6, cy + R * 1.2), (cx - R * 1.1, cy + R * 1.4)]
    p.curve(tail, R * 0.9, s2 if style != "painting" else m, taper=0.2)
    p.ell(cx, cy + R * 0.1, R * 0.7, R * 0.8, m)
    if style == "woman":
        p.poly([(cx - R * 0.6, cy - R * 0.5), (cx + R * 0.6, cy - R * 0.5), (cx + R * 0.9, cy + R * 1.1), (cx - R * 0.9, cy + R * 1.1)], m)
        p.ell(cx + 1, cy - R * 0.75, R * 0.4, R * 0.42, lt(m, .2))
        p.curve([(cx - 1, cy - R * 1.0), (cx - R * 0.5, cy - R * 0.3), (cx - R * 0.6, cy + R * 0.4)], R * 0.3, s2 if not o.get("veil") else "#ffffff", taper=0.6)
        glow_eyes(p, [(cx + 2, cy - R * 0.8)], e)
        p.limb(cx + R * 0.4, cy - R * 0.3, cx + R * 0.9, cy + R * 0.2, 2.4, lt(m, .1))
        return
    glow_eyes(p, [(cx - 3, cy - R * 0.1), (cx + 2, cy - R * 0.1)], e)
    p.ell(cx, cy + R * 0.35, 1.6, 2.2, dk(m, .6), shade=False)
    if style == "water":
        for i in range(4):
            p.px(cx - R * 0.5 + i * 3, cy + R * 0.6, a)
    elif style == "rainbow":
        for i, col in enumerate([m, s2, a, "#3a6ae0"]):
            p.line([(cx - R * 0.6, cy - R * 0.5 + i * 3), (cx + R * 0.6, cy - R * 0.5 + i * 3)], col)
        glow_eyes(p, [(cx - 3, cy - R * 0.1), (cx + 2, cy - R * 0.1)], e)
    elif style == "painting":
        p.line([(cx - R * 0.6, cy + R * 0.4), (cx + R * 0.6, cy + R * 0.4)], s2, 2)
        p.poly([(cx - 3, cy - R * 0.8), (cx, cy - R * 1.3), (cx + 3, cy - R * 0.8)], s2)
    elif style == "rings":
        for r in (R * 1.1, R * 1.4):
            p.line([(cx - r, cy), (cx - r + 2, cy - 4), (cx - r + 2, cy + 4)], lt(m, .3))
            p.line([(cx + r, cy), (cx + r - 2, cy - 4), (cx + r - 2, cy + 4)], lt(m, .3))


# ================================================================== plants (64 x 61)
def plant(p, c, o):
    g = p.h - 1
    m, s2, a, e = c["main"], c["second"], c["accent"], c["eye"]
    style = o.get("style", "reeds")
    cx = 30
    rnd = random.Random(style + m)
    if style in ("cactus", "cardon"):
        h = 46 if style == "cardon" else 40
        p.rect(cx - 6, g - h, cx + 6, g, m)
        p.ell(cx, g - h, 6, 4, m)
        for s, y, L in ((-1, g - 24, 12), (1, g - 30, 10)):
            p.rect(min(cx + s * 6, cx + s * 14), y - 3, max(cx + s * 6, cx + s * 14), y + 3, m)
            p.rect(cx + s * 14 - 3, y - L - 3, cx + s * 14 + 3, y + 3, m)
            p.ell(cx + s * 14, y - L - 3, 3, 2, m)
        for x in range(int(cx - 4), int(cx + 5), 3):
            p.line([(x, g - h + 2), (x, g - 2)], s2)
        for i in range(14):
            p.px(rnd.uniform(cx - 6, cx + 6), rnd.uniform(g - h, g - 4), a)
        if style == "cactus":
            p.ell(cx, g - h - 3, 3, 2, "#e04080")
        glow_eyes(p, [(cx - 3, g - h + 8), (cx + 2, g - h + 8)], e)
        p.line([(cx - 3, g - h + 13), (cx + 3, g - h + 14)], dk(m, .6))
        return
    if style in ("flytrap", "pitcher", "lotus"):
        p.curve([(cx, g), (cx - 2, g - 14), (cx + 2, g - 26)], 4, s2 if style != "lotus" else "#2a5a2a", taper=0.8)
        for s in (-1, 1):
            p.poly([(cx, g - 6), (cx + s * 14, g - 14), (cx + s * 10, g - 4)], s2 if style != "lotus" else "#3a7a3a")
        if style == "flytrap":
            p.poly([(cx + 2, g - 26), (cx + 18, g - 36), (cx + 14, g - 26)], m)
            p.poly([(cx + 2, g - 26), (cx + 18, g - 18), (cx + 14, g - 26)], m)
            for i in range(5):
                p.px(cx + 6 + i * 2.4, g - 30 + i * 0.8, a)
                p.px(cx + 6 + i * 2.4, g - 22 - i * 0.8, a)
            glow_eyes(p, [(cx + 6, g - 29)], e)
        elif style == "pitcher":
            p.ell(cx + 4, g - 32, 7, 10, m)
            p.ell(cx + 4, g - 41, 6, 2.4, dk(m, .5), shade=False)
            p.poly([(cx, g - 42), (cx + 10, g - 48), (cx + 8, g - 42)], a)
            glow_eyes(p, [(cx + 1, g - 33), (cx + 6, g - 33)], e)
        else:
            for i in range(7):
                a_ = math.pi * (1.1 + i * 0.13)
                tip = (cx + 2 + math.cos(a_) * 14, g - 28 + math.sin(a_) * 14)
                p.poly([(cx + 2, g - 26), (tip[0] - 3, tip[1] + 3), tip, (tip[0] + 3, tip[1] + 3)], m if i % 2 else s2)
                if o.get("cracked"):
                    p.line([(cx + 2, g - 26), tip], a)
            glow_eyes(p, [(cx - 1, g - 30), (cx + 4, g - 30)], e)
        return
    if style == "mushroom":
        p.rect(cx - 4, g - 22, cx + 4, g, s2 if s2 else lt(m, .5))
        p.ell(cx, g - 24, 16, 10, m)
        for i in range(6):
            p.ell(cx - 10 + i * 4, g - 26 + (i % 2) * 3, 1.6, 1.4, a, shade=False)
        glow_eyes(p, [(cx - 3, g - 14), (cx + 2, g - 14)], e)
        return
    if style == "swordtree":
        p.poly([(cx - 5, g), (cx - 3, g - 50), (cx + 3, g - 50), (cx + 5, g)], m)
        for i in range(5):  # branches, each ending in a blade pointing down
            y = g - 50 + i * 8
            for s in (-1, 1):
                L = 16 - i * 2
                p.line([(cx, y + 2), (cx + s * L, y - 4)], m, 2)
                p.poly([(cx + s * L - 1.5, y - 4), (cx + s * L + 1.5, y - 4), (cx + s * L, y + 8)], s2)
                p.px(cx + s * L, y - 2, lt(s2, .5))
        glow_eyes(p, [(cx - 3, g - 30), (cx + 2, g - 30)], e)
        return
    # trunk-and-leaves plants: reeds, fern, root, algae, vine
    if style == "root":
        for s in (-1, 1):
            p.curve([(cx, g - 18), (cx + s * 10, g - 6), (cx + s * 18, g)], 4, m, taper=0.5)
        p.ell(cx, g - 24, 9, 12, m)
        for i in range(4):
            p.curve([(cx + rnd.uniform(-6, 6), g - 32), (cx + rnd.uniform(-14, 14), g - 44), (cx + rnd.uniform(-10, 10), g - 52)], 2.4, m, taper=0.4)
        p.ell(cx + 2, g - 46, 10, 5, s2)
        glow_eyes(p, [(cx - 3, g - 26), (cx + 2, g - 26)], e)
        p.line([(cx - 3, g - 20), (cx + 3, g - 19)], "#1a1008")
        return
    n = {"reeds": 9, "fern": 7, "algae": 8, "vine": 6}.get(style, 7)
    for i in range(n):
        x0 = cx + (i - n / 2) * 2.4
        top = (x0 + rnd.uniform(-10, 10), g - rnd.uniform(34, 52))
        mid_ = ((x0 + top[0]) / 2 + rnd.uniform(-5, 5), (g + top[1]) / 2)
        p.curve([(x0, g), mid_, top], 3.4 if style != "reeds" else 2.4, m if i % 2 else s2, taper=0.4)
        if style == "reeds":
            p.ell(top[0], top[1] + 3, 1.6, 3.4, "#6a4a24")
        elif style == "fern":
            for t in range(4):
                fx, fy = mid_[0] + (top[0] - mid_[0]) * t / 4, mid_[1] + (top[1] - mid_[1]) * t / 4
                p.line([(fx, fy), (fx + 4, fy + 2)], a); p.line([(fx, fy), (fx - 4, fy + 2)], a)
        elif style == "vine":
            p.ell(top[0], top[1], 3, 2, a)
    p.ell(cx, g - 20, 7, 8, m)
    glow_eyes(p, [(cx - 3, g - 22), (cx + 2, g - 22)], e)
    p.line([(cx - 2, g - 17), (cx + 2, g - 17)], dk(m, .6))


# ================================================================== golems and things (64 x 61)
def golem(p, c, o):
    g = p.h - 1
    m, s2, a, e = c["main"], c["second"], c["accent"], c["eye"]
    style = o.get("style", "stone")
    cx = 30
    rnd = random.Random(style + m)
    if style in ("ball",):
        p.ell(cx, g - 14, 14, 14, m)
        p.ell(cx - 4, g - 19, 4, 3, lt(m, .3), shade=False)
        if o.get("fuse"):
            p.curve([(cx + 6, g - 26), (cx + 10, g - 32), (cx + 14, g - 33)], 1.6, "#6a4a2a", taper=1)
            p.ell(cx + 15, g - 34, 2, 2, a, shade=False); p.px(cx + 15, g - 34, e)
        glow_eyes(p, [(cx + 2, g - 16), (cx + 7, g - 16)], e if not o.get("fuse") else a)
        for i in range(5):
            p.line([(cx - 10 + i * 4, g - 6), (cx - 8 + i * 4, g - 10)], dk(m, .4))
        return
    if style in ("icicle", "stalagmite"):
        p.poly([(cx - 12, g), (cx - 4, g - 46), (cx + 2, g - 52), (cx + 8, g - 40), (cx + 13, g)], m)
        p.line([(cx - 2, g - 46), (cx - 4, g - 4)], lt(m, .4))
        for i in range(4):
            p.poly([(cx - 18 + i * 12, g), (cx - 15 + i * 12, g - 16 - (i % 2) * 6), (cx - 12 + i * 12, g)], s2)
        glow_eyes(p, [(cx - 3, g - 30), (cx + 3, g - 30)], e)
        p.line([(cx - 3, g - 24), (cx + 4, g - 23)], dk(m, .5))
        return
    if style == "ram":
        p.rect(cx - 18, g - 34, cx + 16, g - 4, m)
        p.ell(cx + 18, g - 22, 8, 10, s2)
        for s in (-1, 1):
            p.curve([(cx + 18, g - 30), (cx + 24, g - 38), (cx + 28, g - 30)], 3, a, taper=0.5)
        glow_eyes(p, [(cx + 18, g - 24)], e)
        for i in range(6):
            p.line([(cx - 16 + i * 6, g - 32), (cx - 14 + i * 6, g - 6)], a)
        return
    # stone figures: legs, a heavy body, arms, a small head
    for lx in (cx - 8, cx + 6):
        p.rect(lx - 4, g - 16, lx + 4, g, dk(m, .1))
    body = [(cx - 15, g - 38), (cx + 14, g - 40), (cx + 16, g - 14), (cx - 14, g - 14)]
    p.poly(body, m)
    for s in (-1, 1):
        x = cx + s * 18
        p.poly([(x - 4, g - 38), (x + 4, g - 38), (x + 5 * s + 3, g - 14), (x + 5 * s - 3, g - 14)], dk(m, .05) if s < 0 else m)
        p.ell(x + 5 * s, g - 12, 5, 4, m)
    p.poly([(cx - 6, g - 40), (cx + 7, g - 41), (cx + 8, g - 50), (cx - 5, g - 51)], m)
    glow_eyes(p, [(cx - 2, g - 46), (cx + 3, g - 46)], e)
    if style in ("stone", "statue", "salt"):
        for i in range(6):
            x, y = rnd.uniform(cx - 12, cx + 12), rnd.uniform(g - 36, g - 18)
            p.line([(x, y), (x + rnd.uniform(-4, 4), y + rnd.uniform(2, 6))], dk(m, .35))
        if o.get("gold"):
            for (x, y) in ((cx - 8, g - 30), (cx + 6, g - 24), (cx, g - 34)):
                p.ell(x, y, 2, 2, a, shade=False)
        if style == "statue":
            for y in (g - 32, g - 22):
                for x in range(int(cx - 12), int(cx + 12), 6):
                    p.poly([(x, y), (x + 3, y - 3), (x + 6, y), (x + 3, y + 3)], a)
        if style == "salt":
            for i in range(5):
                x = cx - 12 + i * 6
                p.poly([(x - 2, g - 38), (x, g - 46 - (i % 2) * 4), (x + 2, g - 38)], s2 if s2 != m else "#ffffff")
    elif style in ("ice",):
        for i in range(5):
            p.poly([(cx - 14 + i * 7, g - 38), (cx - 12 + i * 7, g - 48 - (i % 2) * 5), (cx - 10 + i * 7, g - 38)], s2)
        p.line([(cx - 8, g - 36), (cx - 2, g - 18)], lt(m, .5))
    elif style == "lava":
        for i in range(7):
            x, y = rnd.uniform(cx - 12, cx + 12), rnd.uniform(g - 36, g - 16)
            p.line([(x, y), (x + rnd.uniform(-5, 5), y + rnd.uniform(3, 8))], a, 1)
        p.ell(cx, g - 26, 4, 3, e, shade=False)
    if o.get("sad"):
        p.line([(cx - 2, g - 43), (cx + 4, g - 42)], dk(m, .6))
        p.px(cx - 2, g - 44, "#80c0ff")


def object_(p, c, o):
    g = p.h - 1
    m, s2, a, e = c["main"], c["second"], c["accent"], c["eye"]
    style = o.get("style", "urn")
    cx = 30
    eyes_at = None
    if style in ("urn", "jar", "pot"):
        if style == "pot":
            p.ell(cx, g - 14, 15, 12, m)
            p.rect(cx - 16, g - 26, cx + 16, g - 22, s2)
            for i in range(4):
                p.ell(cx - 6 + i * 4, g - 30 - (i % 2) * 3, 2.4, 2.4, lt(a, .2), shade=False)
            p.poly([(cx - 8, g - 2), (cx - 4, g + 0), (cx + 4, g), (cx + 8, g - 2)], a)
            eyes_at = (cx - 4, g - 16)
        else:
            p.ell(cx, g - 18, 13, 17, m)
            p.rect(cx - 6, g - 40, cx + 6, g - 32, m)
            p.rect(cx - 8, g - 42, cx + 8, g - 39, dk(m, .1))
            for y in (g - 24, g - 12):
                for x in range(cx - 10, cx + 10, 5):
                    p.poly([(x, y), (x + 2.5, y - 2.5), (x + 5, y), (x + 2.5, y + 2.5)], s2)
            if style == "jar":
                p.line([(cx + 4, g - 34), (cx + 8, g - 22), (cx + 5, g - 12)], "#1a1008")
            eyes_at = (cx - 4, g - 28)
    elif style == "cannon":
        p.poly([(cx - 22, g - 20), (cx + 18, g - 26), (cx + 20, g - 18), (cx - 22, g - 12)], m)
        p.ell(cx + 20, g - 22, 3, 4, dk(m, .5))
        for s in (-8, 8):
            p.ell(cx + s, g - 8, 7, 7, s2)
            p.ell(cx + s, g - 8, 2, 2, dk(s2, .4))
        eyes_at = (cx + 4, g - 23)
    elif style == "anchor":
        p.rect(cx - 2, g - 46, cx + 2, g - 6, m)
        p.ell(cx, g - 48, 5, 5, m); p.ell(cx, g - 48, 2, 2, (0, 0, 0, 0), shade=False)
        p.rect(cx - 10, g - 40, cx + 10, g - 37, m)
        p.curve([(cx - 16, g - 18), (cx - 10, g - 4), (cx, g - 4), (cx + 10, g - 4), (cx + 16, g - 18)], 4, m, taper=1)
        for k in range(8):
            p.ell(cx + 8 + k * 2, g - 44 + k * 4, 1.4, 1.8, s2, shade=False)
        eyes_at = (cx - 3, g - 30)
    elif style == "rocker":
        p.curve([(cx - 20, g - 6), (cx, g), (cx + 20, g - 6)], 3, m, taper=1)
        p.rect(cx - 12, g - 44, cx - 8, g - 4, m)
        p.rect(cx - 12, g - 24, cx + 12, g - 20, m)
        p.rect(cx + 8, g - 24, cx + 12, g - 4, m)
        for y in range(int(g - 42), int(g - 24), 3):
            p.line([(cx - 11, y), (cx - 9, y)], a)
        eyes_at = (cx - 12, g - 36)
    elif style == "bell":
        p.poly([(cx - 6, g - 40), (cx + 6, g - 40), (cx + 16, g - 6), (cx - 16, g - 6)], m)
        p.ell(cx, g - 40, 6, 3, m)
        p.ell(cx, g - 6, 16, 3, dk(m, .2))
        p.ell(cx, g - 2, 3, 3, s2)
        p.line([(cx + 2, g - 30), (cx + 6, g - 18), (cx + 4, g - 10)], "#1a1008")
        eyes_at = (cx - 4, g - 26)
    elif style == "clock":
        p.rect(cx - 12, g - 50, cx + 12, g, m)
        p.ell(cx, g - 38, 9, 9, s2)
        p.line([(cx, g - 38), (cx, g - 45)], "#1a1008", 2); p.line([(cx, g - 38), (cx + 5, g - 38)], "#1a1008")
        p.rect(cx - 3, g - 26, cx + 3, g - 6, dk(m, .4))
        p.ell(cx, g - 10, 3, 3, "#d8a840")
        eyes_at = (cx - 5, g - 40)
    elif style == "cart":
        p.poly([(cx - 20, g - 26), (cx + 20, g - 26), (cx + 16, g - 8), (cx - 16, g - 8)], m)
        for s in (-10, 10):
            p.ell(cx + s, g - 6, 6, 6, "#3a3a3a")
        for i in range(5):
            p.poly([(cx - 14 + i * 7, g - 26), (cx - 11 + i * 7, g - 34), (cx - 8 + i * 7, g - 26)], s2)
        eyes_at = (cx - 4, g - 20)
    elif style == "door":
        p.rect(cx - 14, g - 54, cx + 14, g, m)
        for x in (cx - 7, cx, cx + 7):
            p.line([(x, g - 54), (x, g)], dk(m, .4))
        p.rect(cx - 16, g - 56, cx + 16, g - 53, s2)
        p.ell(cx + 10, g - 26, 2, 2, s2)
        p.ell(cx, g - 18, 5, 3, "#1a0a08", shade=False)
        eyes_at = (cx - 5, g - 36)
    elif style == "pillar":
        p.rect(cx - 9, g - 52, cx + 9, g, m)
        p.rect(cx - 12, g - 56, cx + 12, g - 50, s2)
        p.rect(cx - 12, g - 4, cx + 12, g, s2)
        for x in (cx - 5, cx, cx + 5):
            p.line([(x, g - 50), (x, g - 4)], dk(m, .2))
        eyes_at = (cx - 4, g - 36)
    elif style == "stove":
        p.rect(cx - 18, g - 26, cx + 18, g, m)
        p.ell(cx, g - 12, 8, 7, "#1a0a08")
        p.ell(cx, g - 10, 6, 4, a, shade=False)
        p.ell(cx, g - 10, 3, 2, e, shade=False)
        p.ell(cx - 6, g - 32, 9, 6, s2)
        eyes_at = (cx - 10, g - 20)
    elif style == "rope":
        p.curve([(cx - 20, g - 46), (cx - 6, g - 40), (cx + 4, g - 28), (cx - 4, g - 14), (cx + 12, g - 4)], 4, m, taper=1)
        for i in range(10):
            t = i / 9
            p.px(cx - 20 + t * 32, g - 46 + t * 42, s2)
        eyes_at = (cx - 9, g - 42)
    elif style == "broom":
        p.line([(cx - 6, g - 54), (cx + 2, g - 16)], "#6a4a2a", 3)
        p.poly([(cx - 4, g - 18), (cx + 8, g - 18), (cx + 14, g), (cx - 8, g)], m)
        for x in range(int(cx - 6), int(cx + 13), 2):
            p.line([(x + 1, g - 16), (x + 2, g)], s2)
        eyes_at = (cx - 4, g - 12)
    elif style == "stump":
        p.rect(cx - 12, g - 24, cx + 12, g, m)
        p.ell(cx, g - 24, 12, 4, s2)
        p.ell(cx, g - 24, 6, 2, dk(s2, .3), shade=False)
        p.line([(cx + 2, g - 26), (cx + 10, g - 40)], "#6a4a2a", 2)
        p.poly([(cx + 8, g - 42), (cx + 16, g - 44), (cx + 15, g - 36)], "#b8b8c8")
        eyes_at = (cx - 5, g - 14)
    elif style == "blade":
        p.poly([(cx - 3, g - 8), (cx + 3, g - 8), (cx + 2, g - 52), (cx, g - 56), (cx - 2, g - 52)], m)
        p.line([(cx, g - 54), (cx, g - 10)], lt(m, .4))
        p.rect(cx - 9, g - 10, cx + 9, g - 7, s2)
        p.rect(cx - 2, g - 7, cx + 2, g, a)
        eyes_at = (cx - 2, g - 30)
    elif style == "boat":
        p.poly([(cx - 26, g - 12), (cx + 26, g - 12), (cx + 20, g), (cx - 20, g)], m)
        p.curve([(cx - 14, g - 12), (cx, g - 28), (cx + 14, g - 12)], 3, a, taper=1)
    if eyes_at:
        x, y = eyes_at
        glow_eyes(p, [(x, y), (x + 6, y)], e)


def blob(p, c, o):
    g = p.h - 2
    m, s2, a, e = c["main"], c["second"], c["accent"], c["eye"]
    style = o.get("style", "slime")
    cx = 26
    rnd = random.Random(style + m)
    if style == "octopus":
        for i in range(6):
            x0 = cx - 10 + i * 4
            p.curve([(x0, g - 10), (x0 + rnd.uniform(-6, 6), g - 4), (x0 + rnd.uniform(-10, 10), g)], 3, s2 if i % 2 else m, taper=0.4)
        p.ell(cx, g - 16, 11, 10, m)
        glow_eyes(p, [(cx + 2, g - 17), (cx + 7, g - 17)], e)
        for i in range(4):
            p.px(cx - 6 + i * 3, g - 22 + (i % 2), a)
        return
    p.poly([(cx - 18, g), (cx - 16, g - 8), (cx - 10, g - 16), (cx, g - 20), (cx + 10, g - 16), (cx + 16, g - 8), (cx + 18, g)], m)
    p.ell(cx, g - 12, 14, 9, m)
    p.ell(cx - 4, g - 16, 4, 2.4, lt(m, .35), shade=False)
    if style == "moss":
        for i in range(16):
            p.px(rnd.uniform(cx - 14, cx + 14), rnd.uniform(g - 18, g - 2), s2 if i % 2 else a)
    elif style == "lava":
        for i in range(5):
            x = rnd.uniform(cx - 12, cx + 12)
            p.line([(x, g - 16), (x + rnd.uniform(-3, 3), g - 4)], a)
        p.ell(cx + 4, g - 9, 5, 3, s2, shade=False)
    elif style == "mud":
        for i in range(5):
            p.ell(rnd.uniform(cx - 12, cx + 12), g - rnd.uniform(4, 16), 2, 1.6, s2, shade=False)
    elif style == "blister":
        for i in range(7):
            p.ell(rnd.uniform(cx - 12, cx + 12), g - rnd.uniform(6, 18), 2.6, 2.4, a)
    elif style == "manatee":
        pass
    if o.get("crystals"):
        for i in range(4):
            p.poly([(cx - 10 + i * 6, g - 16), (cx - 8 + i * 6, g - 26), (cx - 6 + i * 6, g - 16)], a)
    glow_eyes(p, [(cx + 2, g - 13), (cx + 7, g - 13)], e)
    p.line([(cx + 2, g - 8), (cx + 8, g - 8)], dk(m, .6))


KINDS = {"biped": (biped, True), "quad": (quad, True), "bird": (bird, False), "serpent": (serpent, False), "lizard": (lizard, False), "frog": (frog, False),
         "turtle": (turtle, False), "fish": (fish, False), "crab": (crab, False), "bug": (bug, False), "bat": (bat, False), "worm": (worm, False),
         "monkey": (monkey, True), "snail": (snail, False), "spirit": (spirit, False), "plant": (plant, True), "golem": (golem, True),
         "object": (object_, True), "blob": (blob, False)}

MONSTERS = {m["id"]: m for m in Z.all_monsters()}


def build(mid):
    m = MONSTERS[mid]
    kind, cs, o = m["art"]
    fn, big = KINDS[kind]
    if o.get("big") or (kind in ("serpent", "lizard", "fish", "crab", "spirit", "bird") and o.get("big")):
        big = True
    if kind in ("quad",) and not o.get("big"):
        big = True  # quads need the room, drawn smaller
    p = Pic(*(BIG if big else SMALL))
    fn(p, cols(cs), o)
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
        k, ncol, cw, chh = 2, 20, 70 * 2, 66 * 2
        rows = (len(made) + ncol - 1) // ncol
        sh = Image.new("RGBA", (ncol * cw, rows * chh), (58, 52, 44, 255))
        for i, (_, im) in enumerate(made):
            b = im.resize((im.width * k, im.height * k), Image.NEAREST)
            sh.alpha_composite(b, ((i % ncol) * cw + (cw - b.width) // 2, (i // ncol) * chh + chh - b.height - 4))
        sh.save(sheet)


if __name__ == "__main__":
    main()
