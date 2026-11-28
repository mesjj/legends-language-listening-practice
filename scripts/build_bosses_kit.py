"""The 72 bosses of the zones added on 2026-11-27 (scripts/zones_bosses.py), drawn in code: original pixel art.

Each is drawn with the monster archetypes of build_monsters_kit.py at boss size (a canvas that scales every
shape, so the detail is drawn at full resolution, not blown up), shaded and outlined like the stable, then
brought to life over N frames: breathing, swaying, its element in the air (embers, snow, spores, sparks),
water rippling round it if it stands in water; in the second phase it grows and a pulsing aura rises.
Facing left, toward you, like the other bosses. Sheets and bosses.json go where build_bosses.py puts them.
usage: .venv/bin/python scripts/build_bosses_kit.py [id ...] [--sheet out.png]
"""
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

import build_bosses as BB
import build_monsters_kit as K
import zones_bosses as ZB
from build_bosses import N, TAU, embers, outline, rgb, shear
from build_bosses_more import FIRE, BLUEFIRE, falling, river
from build_stable import Pic, dk, lt


class BigPic(Pic):
    """build_stable.Pic with every coordinate and width scaled by k: the monster archetypes at boss size."""

    def __init__(self, w, h, k):
        super().__init__(w, h)  # w, h: in the archetypes' units, which they read (the ground line)
        self.k = k
        self.RW, self.RH = round(w * k), round(h * k)  # the real canvas

    def _new(self):
        from PIL import ImageDraw
        m = Image.new("L", (self.RW, self.RH))
        return m, ImageDraw.Draw(m)

    def _merge_last(self, k, col, shade):
        parts = self.flat[-k:]
        del self.flat[-k:]
        m = Image.new("L", (self.RW, self.RH))
        for pm, _, _ in parts:
            m.paste(255, mask=pm)
        self._put(m, col, shade)

    def ell(self, cx, cy, rx, ry, col, shade=True):
        k = self.k
        super().ell(cx * k, cy * k, max(0.6, rx * k), max(0.6, ry * k), col, shade)

    def poly(self, pts, col, shade=True):
        super().poly([(x * self.k, y * self.k) for x, y in pts], col, shade)

    def line(self, pts, col, w=1, shade=False):
        super().line([(x * self.k, y * self.k) for x, y in pts], col, max(1, round(w * self.k)), shade)

    def rect(self, x0, y0, x1, y1, col, shade=True):
        k = self.k
        super().rect(x0 * k, y0 * k, x1 * k + k - 1, y1 * k + k - 1, col, shade)

    def px(self, x, y, col):
        k = self.k
        Pic.rect(self, x * k, y * k, x * k + k - 1, y * k + k - 1, col, False)

    def render(self):
        """Pic.render, only looking inside each layer's box (the big canvas has hundreds of layers)."""
        W, H = self.RW, self.RH
        im = Image.new("RGBA", (W, H))
        for m, col, sh in self.flat:
            bb = m.getbbox()
            if not bb:
                continue
            mp = m.load()
            layer = Image.new("RGBA", (W, H))
            lp = layer.load()
            light, dark, deep, rim = lt(col, 0.16), dk(col, 0.16), dk(col, 0.3), lt(col, 0.32)
            top, hh = bb[1], max(1, bb[3] - bb[1])
            left, ww = bb[0], max(1, bb[2] - bb[0])
            for y in range(bb[1], bb[3]):
                v = (y - top) / hh
                for x in range(bb[0], bb[2]):
                    if not mp[x, y]:
                        continue
                    c = col
                    if sh:
                        # volume: lit from the upper left, banded and dithered like the hand-drawn bosses
                        u = v * 0.75 + (x - left) / ww * 0.25
                        d = (BB.BAYER[y % 4][x % 4] + 0.5) / 16 * 0.12
                        c = light if u + d < 0.3 else col if u + d < 0.62 else dark if u + d < 0.88 else deep
                        if not mp[x, y - 1] if y > 0 else True:
                            c = rim
                        elif x > 0 and not mp[x - 1, y]:
                            c = light
                        elif y >= H - 2 or not mp[x, y + 1] or not mp[x, y + 2]:
                            c = deep
                    lp[x, y] = c
            im.alpha_composite(layer)
        return outline(im)


# the boss archetypes, as monster archetypes and their options
def as_monster(kind, o):
    o = dict(o)
    if kind == "figure":
        if o.get("hair") == "flame":
            o["fx"] = "flame"
        return "biped", o, (64, 61)
    if kind == "floater":
        st = o.get("style", "ghost")
        o["style"] = {"storm": "cloud", "meteor": "flame", "waterfall": "water", "lotus": "crystal"}.get(st, st)
        if st == "storm":
            o["rain"] = True
        return "spirit", o, (64, 61)
    if kind == "serpent":
        o.setdefault("style", "rise" if not o.get("water") else "coil")
        return "serpent", o, (64, 52)
    if kind == "colossus":
        o["style"] = {"snow": "ice", "lava": "lava", "stone": "stone", "twin": "ram", "castle": "statue", "salt": "salt"}.get(o.get("material"), "stone")
        return "golem", o, (64, 61)
    if kind == "beast":
        o["big"] = True
        o["head"] = {"wolf": "dog", "glypto": "bone"}.get(o.get("head"), o.get("head", "dog"))
        if o.get("head") == "bull":
            o["horns"] = True
        if o["head"] == "bone":
            o["bones"] = True
        return "quad", o, (64, 61)
    if kind == "tree":
        o["style"] = {"palm": "reeds", "ceiba": "root", "weed": "algae", "shalmali": "swordtree"}.get(o.get("style"), "root")
        return "plant", o, (64, 61)
    if kind == "object":
        return "object", o, (64, 61)
    if kind == "octopus":
        o["style"] = "octopus"
        return "blob", o, (52, 40)
    if kind == "blob":
        return "blob", o, (52, 40)
    if kind == "fish":
        return "fish", o, (64, 50)
    if kind == "bird":
        st = o.get("style")
        o["style"] = "perch" if st == "raven" else "flying"
        if st == "phoenix":
            o["fire"] = True
        if st == "raven":
            o["beak"] = "iron"
        return "bird", o, (52, 44)
    if kind == "spider":
        o["style"] = "spider"
        o["long"] = True
        return "bug", o, (52, 40)
    if kind == "ant":
        o["style"] = "ant"
        o["big_jaw"] = True
        o["fat"] = True
        return "bug", o, (52, 40)
    raise KeyError(kind)


# a few boss-only things the monster archetypes don't have
def extra(p, kind, o, c):
    st = o.get("style")
    if kind == "object" and st == "mouth":
        g = p.h - 1
        p.poly([(4, g), (8, g - 40), (22, g - 54), (42, g - 54), (56, g - 40), (60, g)], c["main"])
        p.poly([(16, g), (18, g - 32), (32, g - 40), (46, g - 32), (48, g)], "#0e0c0c", shade=False)
        for i in range(6):
            x = 20 + i * 5
            p.poly([(x - 2, g - 34 + abs(i - 2.5) * 2), (x, g - 24), (x + 2, g - 34 + abs(i - 2.5) * 2)], c["accent"])
            p.poly([(x - 2, g), (x, g - 8), (x + 2, g)], c["accent"])
        K.glow_eyes(p, [(26, g - 46), (36, g - 46)], c["eye"])
        return True
    if kind == "object" and st == "procession":
        g = p.h - 1
        for i, x in enumerate((10, 24, 40, 54)):
            p.poly([(x - 4, g), (x - 3, g - 26), (x, g - 32), (x + 3, g - 26), (x + 4, g)], c["main"])
            p.ell(x, g - 34, 3, 3.4, c["main"])
            K.glow_eyes(p, [(x, g - 35)], c["eye"])
        p.rect(4, g - 26, 60, g - 23, "#6a4a2a")
        p.poly([(14, g - 26), (50, g - 26), (48, g - 31), (16, g - 31)], c["second"])
        return True
    if kind == "object" and st == "galleon":
        g = p.h - 1
        p.poly([(2, g - 18), (62, g - 22), (54, g - 2), (10, g - 2)], c["main"])
        p.rect(44, g - 30, 60, g - 20, c["main"])
        for x in (18, 36):
            p.line([(x, g - 20), (x, g - 58)], "#3a2a1a", 2)
            p.poly([(x - 10, g - 54), (x + 10, g - 54), (x + 8, g - 30), (x - 8, g - 32)], c["second"])
            p.line([(x - 6, g - 46), (x + 4, g - 40)], "#2a3030")
        for x in range(12, 52, 8):
            p.ell(x, g - 12, 1.6, 1.6, "#1a1a1a")
        for i in range(6):
            p.line([(10 + i * 8, g - 16), (11 + i * 8, g - 6)], c["accent"])
        return True
    return False


ELEM = {"fire": "fire", "cold": "cold", "poison": "poison", "light": "light", None: None}


def particles(im, el, t, seed, strong, top):
    W, H = im.size
    n = 22 if strong else 12
    if el == "fire":
        embers(im, seed, 10, W - 10, H - 8, H - top, t, ["#ffc040", "#f07a1a", "#fff4c0"], n=n)
    elif el == "cold":
        falling(im, seed, 4, W - 4, 0, H, t, ["#ffffff", "#e0f4ff", "#a0d0ff"], n=n + 8, drift=5)
    elif el == "poison":
        embers(im, seed, 10, W - 10, H - 10, H * 0.7, t, ["#a0e060", "#d8f080", "#6ac040"], n=n)
    elif el == "light":
        R = random.Random(seed + int(t * N))
        for _ in range(n // 2):
            x, y = R.randint(8, W - 8), R.randint(8, H - 8)
            if im.getpixel((x, y))[3] == 0:
                for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                    im.putpixel((x + dx, y + dy), rgb("#fff8c0" if (dx, dy) == (0, 0) else "#f0d040", 200))
    else:
        falling(im, seed, 4, W - 4, H * 0.3, H, t, ["#a8a090", "#c8c0b0"], n=n // 2, drift=3)


def aura(im, col, t):
    """A ring of col round the boss, breathing: the second phase."""
    a = im.split()[3].point(lambda v: 255 if v > 100 else 0)
    ring = ImageChops.subtract(a.filter(ImageFilter.MaxFilter(7)), a)
    k = 0.45 + 0.3 * math.sin(TAU * t)
    ring = ring.point(lambda v: round(v * k))
    glow = Image.new("RGBA", im.size, rgb(col)[:3] + (0,))
    glow.putalpha(ring)
    out = Image.new("RGBA", im.size)
    out.alpha_composite(glow)
    out.alpha_composite(im)
    return out


BOSS = {b["id"]: b for b in ZB.BOSSES}
SCALE = 2.9


def draw(bid, ph):
    b = BOSS[bid]
    kind, cs, o = b["art"]
    c = K.cols(cs)
    mk, mo, (w, h) = as_monster(kind, o)
    k = SCALE * (1.08 if ph else 1.0) * (1.35 if w <= 52 else 1.0)
    p = BigPic(w, h, k)
    if not extra(p, kind, o, c):
        K.KINDS[mk][0](p, c, mo)
    im = p.render()
    return im.crop(im.getbbox()).transpose(Image.FLIP_LEFT_RIGHT)


def frames(bid):
    b = BOSS[bid]
    kind, cs, o = b["art"]
    c = K.cols(cs)
    el = ELEM[b["el"]]
    if o.get("fx") == "snow":
        el = "cold"
    floats = kind in ("floater",) or (kind == "bird" and o.get("style") != "raven")
    wet = o.get("water") or kind in ("fish", "octopus") or o.get("base") in ("raft", "boat") or o.get("style") in ("galleon",)
    still = kind in ("object", "colossus")
    bodies = [draw(bid, 0), draw(bid, 1)]
    W = max(im.width for im in bodies) + 24
    H = max(im.height for im in bodies) + (26 if floats else 14)
    out = []
    for ph in (0, 1):
        body = bodies[ph]
        row = []
        for i in range(N):
            t = i / N
            s = math.sin(TAU * t)
            im = Image.new("RGBA", (W, H))
            bob = round(s * ((5 if ph else 4) if floats else (2 if ph else 1)))
            fig = body
            if not still:
                fig = shear(body, body.height - 4, round(math.sin(TAU * t + 0.6) * (3 if ph else 2)))
            x = (W - fig.width) // 2
            y = H - fig.height - (12 if floats else 2) + bob
            if kind == "object" and ph and o.get("style") in ("door", "clock", "stove"):
                x += (1 if i % 2 else -1)  # it shakes
            im.alpha_composite(fig, (x, y))
            if ph:
                im = aura(im, c["accent"] if el is None else {"fire": "#ff7a1a", "cold": "#80d0ff", "poison": "#a0e060", "light": "#fff080"}[el], t)
            if wet:
                river(im, H - 12, t * (2 if ph else 1), rgb(c["main"])[:3] if False else (22, 52, 66), seed=hash(bid) % 97, ripple=("#4a88b0", "#8ac0e0"))
            particles(im, el, t, hash(bid) % 1000, ph, H * 0.9)
            row.append(im)
        out.append(row)
    return out


def build(ids):
    import json
    os.makedirs(BB.OUT, exist_ok=True)
    meta_path = os.path.join(BB.OUT, "bosses.json")
    meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
    for bid in ids:
        fr = frames(bid)
        w, h = fr[0][0].size
        sheet = Image.new("RGBA", (w * N, h * 2))
        for ph in (0, 1):
            for i, f in enumerate(fr[ph]):
                sheet.paste(f, (i * w, ph * h))
        sheet.save(os.path.join(BB.OUT, f"{bid}.png"), optimize=True)
        meta[bid] = [w, h, N]
        print(bid, w, h, flush=True)
    json.dump(meta, open(meta_path, "w"), separators=(",", ":"))


def contact(ids, path):
    ims = []
    for bid in ids:
        sh = Image.open(os.path.join(BB.OUT, f"{bid}.png"))
        w, h = sh.width // N, sh.height // 2
        ims.append((sh.crop((0, 0, w, h)), sh.crop((2 * w, h, 3 * w, 2 * h))))
    cw, ch = 200, 190
    cols = 6
    rows = (len(ims) + cols - 1) // cols
    out = Image.new("RGBA", (cols * cw * 2, rows * ch), (40, 36, 44, 255))
    for i, (a, b) in enumerate(ims):
        X, Y = (i % cols) * cw * 2, (i // cols) * ch
        out.alpha_composite(a, (X + (cw - a.width) // 2, Y + ch - a.height))
        out.alpha_composite(b, (X + cw + (cw - b.width) // 2, Y + ch - b.height))
    out.save(path)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sheet = sys.argv[sys.argv.index("--sheet") + 1] if "--sheet" in sys.argv else None
    if sheet in args:
        args.remove(sheet)
    ids = args or list(BOSS)
    build(ids)
    if sheet:
        contact(ids, sheet)
