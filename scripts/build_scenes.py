"""Fight backdrops, one per zone: public/rpg/scenes/<zone>.png.

The ground the fighters stand on is LPC terrain (Lanea Zimmerman "Sharm", LPC Base Assets,
CC-BY-SA 3.0 / GPL 3.0 / OGA-BY 3.0, https://opengameart.org/content/liberated-pixel-cup-lpc-base-assets-sprites-map-tiles),
tinted to the zone. The sky, the horizon and everything on it are drawn here in code (original).

Scenes are built at 1x (W x H) and shown at 2x, pixelated, like the figures.
Run: .venv/bin/python scripts/build_scenes.py [zone ...]
"""
import json
import math
import os
import random
import sys
import urllib.request
import zipfile

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, ".lpc-cache", "terrain")
OUT = os.path.join(ROOT, "public", "rpg", "scenes")
ZIP_URL = "https://opengameart.org/sites/default/files/lpc_base_assets.zip"
W, H = 480, 150
T = 32  # LPC tile


def tiles(name):
    path = os.path.join(CACHE, "lpc_base_assets.zip")
    if not os.path.exists(path):
        os.makedirs(CACHE, exist_ok=True)
        req = urllib.request.Request(ZIP_URL, headers={"User-Agent": "Mozilla/5.0 (leyendas build script)"})
        open(path, "wb").write(urllib.request.urlopen(req, timeout=120).read())
    from io import BytesIO
    data = zipfile.ZipFile(path).read(f"LPC Base Assets/tiles/{name}.png")
    return Image.open(BytesIO(data)).convert("RGBA")


def tile(sheet, cx, cy):
    return sheet.crop((cx * T, cy * T, cx * T + T, cy * T + T))


def tint(im, mul, add=(0, 0, 0)):
    """Multiply each channel (0..1+) and add an offset: to move a tile toward a zone's light."""
    px = im.load()
    out = im.copy()
    po = out.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            po[x, y] = (min(255, int(r * mul[0] + add[0])), min(255, int(g * mul[1] + add[1])), min(255, int(b * mul[2] + add[2])), a)
    return out


def colorize(im, dark, light, gamma=1.0):
    """Recolour a tile by its brightness, from `dark` to `light`: keeps the LPC shading, takes the
    zone's palette (a moor's tawny grass instead of LPC's green)."""
    px = im.load()
    lums = [(0.3 * r + 0.59 * g + 0.11 * b) for (r, g, b, a) in im.getdata() if a]
    if not lums:
        return im
    lo, hi = min(lums), max(lums)
    out = im.copy()
    po = out.load()
    d0, d1 = hexrgb(dark), hexrgb(light)
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if not a:
                continue
            t = ((0.3 * r + 0.59 * g + 0.11 * b) - lo) / max(1, hi - lo)
            c = lerp(d0, d1, t ** gamma)
            po[x, y] = (c[0], c[1], c[2], a)
    return out


def hexrgb(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(len(c1)))


def gradient(im, y0, y1, top, bottom, steps=10):
    """A banded (dithered-looking) vertical gradient, in pixel-art steps rather than smooth."""
    d = ImageDraw.Draw(im)
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0 - 1)
        q = math.floor(t * steps) / steps
        # checker dither between two bands at their seam
        for x in range(im.width):
            tt = q + (1 / steps if (x + y) % 2 and (t * steps) % 1 > 0.5 else 0)
            im.putpixel((x, y), lerp(hexrgb(top), hexrgb(bottom), min(1, tt)))


def skyline(im, base_y, amp, col, seed, bumps=0.09, jag=2.0):
    """A silhouette of treetops along base_y: smooth noise plus small jags, filled to the bottom."""
    rnd = random.Random(seed)
    phase = [rnd.random() * 6.28 for _ in range(4)]
    d = ImageDraw.Draw(im)
    for x in range(im.width):
        h = (math.sin(x * bumps + phase[0]) * 0.5 + math.sin(x * bumps * 2.3 + phase[1]) * 0.3 + math.sin(x * bumps * 5.1 + phase[2]) * 0.2) * amp
        h += rnd.random() * jag
        d.line([(x, int(base_y - h)), (x, im.height)], fill=col)


# ---------- Ciénaga del Mohán ----------
def cienaga():
    im = Image.new("RGBA", (W, H))
    # an evening over the swamp: a dark green sky going sickly yellow at the horizon
    gradient(im, 0, 78, "#0f1c1a", "#6f7f4c", steps=9)
    d = ImageDraw.Draw(im)
    # a low moon, half in the haze
    mx, my = 352, 40
    d.ellipse([mx - 11, my - 11, mx + 11, my + 11], fill=hexrgb("#d9dcae"))
    d.ellipse([mx - 11, my - 11, mx + 11, my + 11], outline=hexrgb("#b7bd8a"))
    d.ellipse([mx - 4, my - 6, mx + 1, my - 2], fill=hexrgb("#c3c792"))
    d.ellipse([mx + 3, my + 2, mx + 7, my + 6], fill=hexrgb("#c3c792"))
    # haze over the moon's lower half
    for y in range(my, my + 14):
        for x in range(mx - 14, mx + 15):
            if (x + y) % 2 == 0:
                r, g, b, a = im.getpixel((x, y))
                im.putpixel((x, y), lerp((r, g, b, a), hexrgb("#7d8a58"), 0.55))
    # far treeline, then a nearer one with mangrove trunks and hanging moss
    skyline(im, 70, 7, hexrgb("#33493a"), 1, bumps=0.07)
    skyline(im, 80, 9, hexrgb("#1f3129"), 2, bumps=0.05, jag=3)
    rnd = random.Random(7)
    for x in range(10, W, 37):
        x += rnd.randint(-10, 10)
        top = 70 + rnd.randint(-5, 4)
        lean = rnd.choice((-1, 0, 1))
        for y in range(top, 93):
            xx = x + (lean if y > 86 else 0)
            d.line([(xx, y), (xx + 1, y)], fill=hexrgb("#14201b"))
        # a few roots splaying into the water
        for k in (-1, 1):
            d.line([(x, 88), (x + k * 4, 93)], fill=hexrgb("#14201b"))
        for i in range(rnd.randint(2, 4)):  # moss hanging from the canopy
            sx = x + rnd.randint(-8, 8)
            sy = top - rnd.randint(0, 5)
            d.line([(sx, sy), (sx, sy + rnd.randint(5, 12))], fill=hexrgb("#47613d"))
    # mist lying on the water: soft drifting banks
    mist = Image.new("RGBA", (W, H))
    md = ImageDraw.Draw(mist)
    rnd = random.Random(11)
    for i in range(16):
        cx, cy = rnd.randint(-20, W + 20), rnd.randint(80, 94)
        rw, rh = rnd.randint(30, 70), rnd.randint(3, 6)
        md.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=(185, 200, 165, 46))
    im.alpha_composite(mist)
    # the water: LPC water, darkened and turned brackish
    water = tints_water(tiles("water"))
    for x in range(0, W, T):
        im.alpha_composite(water[(x // T) % 3], (x, 92))
    im.alpha_composite(mist.transpose(Image.FLIP_LEFT_RIGHT).crop((0, 0, W, H)), (0, 10))
    # reflections of the moon and the treeline
    for i, y in enumerate(range(96, 118, 3)):
        w = max(2, 9 - i)
        d.line([(mx - w, y), (mx + w, y)], fill=hexrgb("#c3c792", 150 - i * 15))
    # the bank you fight on: LPC grass meeting the water (water above, grass below), muddy and dark
    wg = tiles("watergrass")
    edge = tint(tile(wg, 1, 4), (0.5, 0.56, 0.4), (8, 6, 0))
    grass = [tint(tile(tiles("grass"), i, 5), (0.48, 0.55, 0.38), (12, 8, 0)) for i in range(3)]
    for x in range(0, W, T):
        im.alpha_composite(edge, (x, 104))
        im.alpha_composite(grass[(x // T) % 3], (x, 136))
    # bushes from the LPC treetops at both ends of the bank, in the swamp's shade
    tt = tiles("treetop")
    bush = tint(tt.crop((0, 0, 96, 96)), (0.55, 0.62, 0.48))
    bush = bush.crop(bush.getbbox())
    im.alpha_composite(bush.resize((bush.width * 2 // 3, bush.height * 2 // 3), Image.NEAREST), (-18, 96))
    b2 = bush.transpose(Image.FLIP_LEFT_RIGHT)
    im.alpha_composite(b2.resize((b2.width * 2 // 3, b2.height * 2 // 3), Image.NEAREST), (W - b2.width * 2 // 3 + 16, 100))
    # cattails along the waterline (code)
    rnd = random.Random(3)
    for x in list(range(4, 120, 5)) + list(range(360, W, 5)) + list(range(200, 260, 9)):
        x += rnd.randint(-2, 2)
        hgt = rnd.randint(8, 16)
        base = 112 + rnd.randint(0, 3)
        d.line([(x, base), (x + rnd.choice((-1, 0, 0, 1)), base - hgt)], fill=hexrgb("#4f6b33"))
        if rnd.random() < 0.55:
            d.rectangle([x, base - hgt - 3, x + 1, base - hgt + 1], fill=hexrgb("#5a3a22"))
    vignette(im)
    return im


def tints_water(sheet):
    return [tint(tile(sheet, i, 5), (0.22, 0.34, 0.24), (16, 22, 10)) for i in range(3)]


def vignette(im, strength=0.45):
    """Darker towards the top corners and sides, so the fighters stand out in the middle."""
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            dx = (x - im.width / 2) / (im.width / 2)
            dy = (y - im.height * 0.8) / im.height
            k = min(1, (dx * dx * 0.6 + dy * dy * 1.2)) * strength
            r, g, b, a = px[x, y]
            px[x, y] = (int(r * (1 - k)), int(g * (1 - k)), int(b * (1 - k)), a)



# ---------- shared bits ----------
_pal_cache = {}


def sheet_in(sheet, pal):
    """A whole terrain sheet recoloured at once, so all its tiles share one brightness scale."""
    k = (sheet, pal)
    if k not in _pal_cache:
        _pal_cache[k] = colorize(tiles(sheet), *pal)
    return _pal_cache[k]


def ground(im, sheet, y, mul, add=(0, 0, 0), row=5, pal=None):
    fills = [tile(sheet_in(sheet, pal), i, row) if pal else tint(tile(tiles(sheet), i, row), mul, add) for i in range(3)]
    rnd = random.Random(sheet)
    for yy in range(y, H, T):
        for x in range(0, W, T):
            im.alpha_composite(fills[rnd.randrange(3)], (x, yy))


def edge_row(im, sheet, y, mul, add=(0, 0, 0), pal=None):
    """The bottom edge of a terrain's 3x3 block (that terrain above, transparent below), all along y."""
    e = tile(sheet_in(sheet, pal), 1, 4) if pal else tint(tile(tiles(sheet), 1, 4), mul, add)
    for x in range(0, W, T):
        im.alpha_composite(e, (x, y))


def mountains(im, base_y, amp, col, seed, bumps=0.02, peaks=0.6, snow=None, line=None):
    """A range in silhouette. snow=(colour, height): caps on what rises above that height;
    line=colour: a lit ridgeline."""
    rnd = random.Random(seed)
    ph = [rnd.random() * 6.28 for _ in range(3)]
    d = ImageDraw.Draw(im)
    for x in range(W):
        h = abs(math.sin(x * bumps + ph[0])) * amp * peaks + math.sin(x * bumps * 2.7 + ph[1]) * amp * 0.3 + math.sin(x * bumps * 7 + ph[2]) * amp * 0.1
        top = int(base_y - h)
        d.line([(x, top), (x, H)], fill=col)
        if snow and h > snow[1]:
            # the cap reaches further down on the left of each peak (light from the left), ragged
            depth = int((h - snow[1]) * (0.8 if (x // 3) % 2 else 0.6)) + 1
            d.line([(x, top), (x, top + depth)], fill=snow[0])
        if line:
            d.point((x, top), fill=line)


def snow_caps(im, col, below, seed):
    """Lighten the topmost pixels of whatever silhouette has colour `below` (its ridgeline)."""
    px = im.load()
    for x in range(W):
        for y in range(H):
            if px[x, y][:3] == below[:3]:
                for k in range(2):
                    if y + k < H and px[x, y + k][:3] == below[:3]:
                        px[x, y + k] = col
                break


def shade(im, y0, y1, col, a):
    """A flat wash over a band (fog, haze, darkness)."""
    over = Image.new("RGBA", (W, H))
    ImageDraw.Draw(over).rectangle([0, y0, W, y1], fill=col[:3] + (a,))
    im.alpha_composite(over)


def blobs(im, n, y0, y1, col, a, seed, rw=(30, 70), rh=(3, 6)):
    over = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(over)
    rnd = random.Random(seed)
    for _ in range(n):
        cx, cy = rnd.randint(-20, W + 20), rnd.randint(y0, y1)
        w, h = rnd.randint(*rw), rnd.randint(*rh)
        d.ellipse([cx - w, cy - h, cx + w, cy + h], fill=col[:3] + (a,))
    im.alpha_composite(over)


# a frailejón: a shaggy trunk of dead leaves, crowned by a dense rosette of silver-green woolly
# leaves, sometimes yellow flowers on stalks. h: trunk height, r: rosette radius.
def frailejon(d, x, base, h, r=4, far=False):
    trunk, shag = (hexrgb("#4a4440"), hexrgb("#5d5650")) if far else (hexrgb("#6b5640"), hexrgb("#8a7252"))
    dark_leaf, leaf, light = (hexrgb("#5f6c66"), hexrgb("#7d8a82"), hexrgb("#97a39b")) if far else (hexrgb("#7f9078"), hexrgb("#a9b99c"), hexrgb("#dbe4cf"))
    tw = max(1, r // 3)
    for y in range(base - h, base):
        d.line([(x - tw, y), (x + tw, y)], fill=trunk)
        if y % 2 == 0:  # the skirt of dead leaves hanging down the trunk
            d.point((x - tw - 1, y), fill=shag)
            d.point((x + tw + 1, y + 1), fill=shag)
    top = base - h
    d.ellipse([x - r * 0.8, top - r * 1.1, x + r * 0.8, top + r * 0.3], fill=dark_leaf)
    for i in range(11):  # leaves radiating up and out, a rosette taller than wide
        a = math.pi * (1.12 + 0.76 * i / 10)
        d.line([(x, top), (x + math.cos(a) * r * 0.9, top + math.sin(a) * r * 1.2)], fill=leaf)
    d.line([(x - r + 1, top - 1), (x + r - 1, top - 1)], fill=light)
    d.point((x, top - int(r * 0.6)), fill=light)
    if not far and (x * 13 + h) % 3 == 0:  # in flower
        for k in (-1, 1):
            fx, fy = x + k * (r // 2), top - r - 2
            d.line([(x + k, top - 2), (fx, fy)], fill=hexrgb("#7b7a4a"))
            d.point((fx, fy - 1), fill=hexrgb("#f0cf3a"))
            d.point((fx + k, fy), fill=hexrgb("#f0cf3a"))


def paramo():
    im = Image.new("RGBA", (W, H))
    gradient(im, 0, 90, "#62717c", "#c3cbcb", steps=8)  # cold grey morning
    mountains(im, 66, 40, hexrgb("#55636f"), 4, bumps=0.017, snow=(hexrgb("#dfe6e8"), 22))
    blobs(im, 14, 40, 66, (214, 220, 222), 80, 21, rw=(40, 90), rh=(4, 8))
    mountains(im, 82, 18, hexrgb("#4a5a4c"), 5, bumps=0.03, peaks=0.4)
    blobs(im, 14, 72, 90, (210, 216, 216), 90, 22, rw=(40, 90), rh=(3, 7))
    d = ImageDraw.Draw(im)
    # the moor: LPC grass recoloured to tawny pajonal
    pal = ("#4f4a2a", "#c2b070")
    ground(im, "grass", 96, None, pal=pal)
    edge_row(im, "grassalt", 88, None, pal=pal)
    rnd = random.Random(9)
    for i in range(40):  # a far field of frailejones in the fog
        x = rnd.randint(0, W)
        frailejon(d, x, 93 + rnd.randint(-2, 3), rnd.randint(3, 6), 2, far=True)
    blobs(im, 12, 86, 98, (218, 224, 224), 70, 23, rw=(30, 70), rh=(2, 4))
    for x, h, r in ((12, 26, 7), (42, 18, 6), (74, 12, 5), (408, 14, 5), (438, 22, 6), (468, 28, 7), (140, 8, 4), (330, 7, 4)):
        frailejon(d, x + rnd.randint(-3, 3), 140 + rnd.randint(-4, 4) - (20 if r == 4 else 0), h, r)
    rock = tiles("rock")
    for x, y, k in ((100, 122, 0), (368, 126, 1), (250, 106, 1)):
        im.alpha_composite(colorize(rock.crop((k * 32, 0, k * 32 + 32, 32)), "#3d4040", "#a7aca6"), (x, y))
    vignette(im, 0.35)
    return im


def palm(d, x, base, h, col):
    """A moriche palm in silhouette: a straight thin trunk and a fan of fronds."""
    for y in range(base - h, base):
        d.point((x + (1 if y < base - h * 0.6 and (y // 5) % 2 else 0), y), fill=col)
        d.point((x + 1, y), fill=col)
    top = base - h
    for i in range(11):
        a = math.pi * (1.05 + i * 0.09)
        L = 9 + (i % 3)
        pts = [(x + math.cos(a) * t, top + math.sin(a) * t + (t / L) ** 2 * 5) for t in range(0, L)]
        d.line(pts, fill=col)


def llano():
    im = Image.new("RGBA", (W, H))
    gradient(im, 0, 96, "#2a1622", "#e8743a", steps=10)  # dusk turning to fire
    d = ImageDraw.Draw(im)
    # the sun low and red behind smoke
    d.ellipse([88, 52, 116, 80], fill=hexrgb("#ffb15a"))
    d.ellipse([92, 56, 112, 76], fill=hexrgb("#ffd08a"))
    # smoke columns leaning with the wind
    over = Image.new("RGBA", (W, H))
    od = ImageDraw.Draw(over)
    rnd = random.Random(5)
    for cx in (60, 190, 300, 420):
        for i in range(26):
            y = 88 - i * 3.4
            x = cx + i * 1.6 + math.sin(i * 0.6) * 3
            r = 4 + i * 0.7
            od.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=(40, 28, 32, max(0, 120 - i * 4)))
    im.alpha_composite(over)
    # the far plain and the fire line along the horizon
    d.rectangle([0, 90, W, 96], fill=hexrgb("#3a1a14"))
    for x in range(W):
        f = int(3 + abs(math.sin(x * 0.21)) * 4 + abs(math.sin(x * 0.53)) * 3 + rnd.random() * 2)
        for k in range(f):
            col = "#fff0a0" if k < 1 else "#ffb03a" if k < 3 else "#e8502a" if k < 6 else "#8a2418"
            d.point((x, 90 - k), fill=hexrgb(col))
    for x in (30, 52, 140, 160, 340, 352, 455):
        palm(d, x, 92, 24 + (x % 9), hexrgb("#1c0d10"))
    # dry grass you stand on (LPC grass, burnt yellow) with patches of bare earth
    pal = ("#5a3414", "#e8b85a")
    ground(im, "grass", 96, None, pal=pal)
    edge_row(im, "grassalt", 88, None, pal=pal)
    shade(im, 96, H, (255, 120, 40), 22)  # firelight on the ground
    vignette(im, 0.45)
    return im


def selva():
    im = Image.new("RGBA", (W, H))
    gradient(im, 0, 100, "#0c1f17", "#2f5a3a", steps=7)
    d = ImageDraw.Draw(im)
    # light breaking through the canopy far back
    over = Image.new("RGBA", (W, H))
    od = ImageDraw.Draw(over)
    for x0 in (90, 230, 380):
        od.polygon([(x0, 0), (x0 + 14, 0), (x0 + 44, 100), (x0 + 22, 100)], fill=(190, 230, 160, 26))
    im.alpha_composite(over)
    # far trunks and canopy (LPC trunk and treetop, darkened), three depths
    trunk = tiles("trunk")
    tops = tiles("treetop").crop((0, 0, 192, 96))
    for depth, (mul, y, step, scale) in enumerate([((0.28, 0.4, 0.34), 30, 44, 0.6), ((0.4, 0.55, 0.42), 42, 58, 0.8)]):
        rnd = random.Random(depth + 30)
        for x in range(-30, W, step):
            x += rnd.randint(-10, 10)
            t = tint(trunk.crop((0, 0, 96, 96)), mul)
            t = t.crop(t.getbbox())
            t = t.resize((max(1, int(t.width * scale)), int(t.height * scale * 1.3)), Image.NEAREST)
            im.alpha_composite(t, (x, y + 18))
            c = tint(tops.crop((0, 0, 96, 96) if rnd.random() < 0.5 else (96, 0, 192, 96)), mul)
            c = c.crop(c.getbbox())
            k = scale * rnd.uniform(0.8, 1.3)
            c = c.resize((int(c.width * k * 1.2), int(c.height * k)), Image.NEAREST)
            im.alpha_composite(c, (x - c.width // 2 + t.width // 2, y - 20 + rnd.randint(-12, 6)))
    # vines hanging from the top
    rnd = random.Random(31)
    for x in range(0, W, 17):
        x += rnd.randint(-5, 5)
        L = rnd.randint(14, 60)
        for y in range(0, L):
            xx = x + int(math.sin(y * 0.25 + x) * 1.5)
            d.line([(xx, y), (xx + 1, y)], fill=hexrgb("#2f5a2a"))
            if y % 7 == 3:  # a leaf on the vine
                d.line([(xx + 2, y), (xx + 4, y - 1)], fill=hexrgb("#5b8a3e"))
    # the forest floor: LPC dirt and grass, wet and dark
    ground(im, "dirt2", 100, None, pal=("#1e140c", "#7a5a38"))
    edge_row(im, "grass", 94, None, pal=("#13301a", "#4f8a3e"))
    # big leaves at the sides (pointed, with a midrib), and a heliconia flower
    def leaf(cx, cy, ang, L, col, rib):
        pts = []
        for t in range(0, L + 1):
            w = math.sin(math.pi * t / L) * L * 0.28
            pts.append((t, w))
        ca, sa = math.cos(ang), math.sin(ang)
        up = [(cx + t * ca - w * sa, cy + t * sa + w * ca) for t, w in pts]
        dn = [(cx + t * ca + w * sa, cy + t * sa - w * ca) for t, w in reversed(pts)]
        d.polygon(up + dn, fill=col)
        d.line([(cx, cy), (cx + L * ca, cy + L * sa)], fill=rib)
    for side, x0 in ((1, -6), (-1, W + 6)):
        for i, (ang, L) in enumerate([(-0.5, 34), (-0.9, 30), (-0.15, 28), (-1.25, 24), (0.15, 22)]):
            a = ang if side == 1 else math.pi - ang
            leaf(x0, 150 - i * 4, a, L, hexrgb("#2f6e35" if i % 2 else "#3f8a40"), hexrgb("#1d4a24"))
        fx = x0 + side * 26
        for k in range(4):  # heliconia: red bracts stepping up a stem
            y = 118 - k * 6
            d.polygon([(fx, y), (fx + side * 7, y - 3), (fx + side * 2, y + 2)], fill=hexrgb("#e2462e"))
            d.point((fx + side * 6, y - 3), fill=hexrgb("#f0c23a"))
        d.line([(fx, 122), (fx, 96)], fill=hexrgb("#3a6a2a"))
    vignette(im, 0.5)
    return im


def guardian(d, x, base, h, col, dark, light):
    """A carved stone guardian, original: a blocky figure with a wide head, round eyes, fangs and
    arms folded over its belly, half sunk in the ground."""
    w = h // 2
    d.rectangle([x - w // 2, base - h, x + w // 2, base], fill=col)
    d.rectangle([x - w // 2 - 2, base - h, x + w // 2 + 2, base - h + h // 3], fill=col)  # the wide head
    d.line([(x - w // 2 - 2, base - h), (x + w // 2 + 2, base - h)], fill=light)
    for ex in (x - w // 4 - 1, x + w // 4):
        d.rectangle([ex, base - h + 4, ex + 2, base - h + 6], fill=dark)
    d.line([(x - 3, base - h + h // 3 - 3), (x + 3, base - h + h // 3 - 3)], fill=dark)  # the mouth
    for fx in (x - 2, x + 2):
        d.point((fx, base - h + h // 3 - 2), fill=light)
    d.line([(x - w // 2, base - h // 2), (x + w // 2, base - h // 2 + 2)], fill=dark)  # folded arms
    d.line([(x - w // 2, base - h // 2 + 3), (x + w // 2, base - h // 2 + 1)], fill=dark)
    d.line([(x + w // 2, base - h), (x + w // 2, base)], fill=dark)


def ruinas():
    im = Image.new("RGBA", (W, H))
    gradient(im, 0, 96, "#3e5559", "#a9b7a4", steps=8)  # overcast, green-grey
    mountains(im, 78, 22, hexrgb("#6d8170"), 12, bumps=0.025, peaks=0.5)
    blobs(im, 10, 60, 84, (200, 210, 196), 60, 41, rw=(40, 90), rh=(3, 6))
    d = ImageDraw.Draw(im)
    # broken walls from the LPC castle wall, the tops knocked off
    cw = tiles("castlewalls")
    wall = tint(cw.crop((0, 192, 128, 320)), (0.78, 0.86, 0.8))
    rnd = random.Random(42)
    for x0, top, w in ((24, 52, 96), (310, 60, 112), (196, 70, 48)):
        piece = wall.crop((0, 0, w, 128 - (top - 50)))
        px = piece.load()
        # broken a block at a time: the top steps down in brick-sized chunks
        steps = [rnd.randint(4, 34) for _ in range(piece.width // 8 + 1)]
        cut = [steps[i // 8] + (rnd.randint(0, 2) if i % 8 in (0, 7) else 0) for i in range(piece.width)]
        for x in range(piece.width):
            for y in range(min(cut[x], piece.height)):
                px[x, y] = (0, 0, 0, 0)
        im.alpha_composite(piece, (x0, top))
    arch = tint(cw.crop((0, 352, 160, 480)), (0.7, 0.8, 0.74))
    arch = arch.crop((0, 0, 160, 128)).resize((80, 64), Image.NEAREST)
    im.alpha_composite(arch, (130, 34))
    blobs(im, 8, 84, 100, (200, 210, 196), 50, 43, rw=(30, 60), rh=(2, 4))
    # the paved court you fight on (LPC outside castle floor), grass in the cracks
    floor = tiles("castlefloors_outside")
    pave = [colorize(floor.crop((0, 128, 32, 160)), "#4a4a3e", "#a8a68e"), colorize(floor.crop((32, 128, 64, 160)), "#4a4a3e", "#a8a68e")]
    for yy in range(100, H, 32):
        for x in range(0, W, 32):
            im.alpha_composite(pave[(x // 32 + yy // 32) % 2], (x, yy))
    edge_row(im, "grass", 94, None, pal=("#2c3a22", "#7d9460"))
    for i in range(60):
        x, y = rnd.randint(0, W), rnd.randint(104, H)
        d.line([(x, y), (x + rnd.choice((-1, 1)), y - 2)], fill=hexrgb("#5d7a45"))
    guardian(d, 24, 146, 52, hexrgb("#8a8f80"), hexrgb("#4e5248"), hexrgb("#b9bdae"))
    guardian(d, 454, 142, 44, hexrgb("#7d8274"), hexrgb("#45493f"), hexrgb("#a9ad9e"))
    guardian(d, 268, 96, 18, hexrgb("#6d7366"), hexrgb("#3e4239"), hexrgb("#8f9486"))
    vignette(im, 0.4)
    return im


def abismo():
    im = Image.new("RGBA", (W, H))
    gradient(im, 0, 110, "#0d080d", "#4a1c18", steps=8)  # the dark, warming toward the lava below
    d = ImageDraw.Draw(im)
    # cavern walls: jagged rock layers, then stalactites from the roof
    mountains(im, 96, 46, hexrgb("#2a171a"), 50, bumps=0.035, peaks=0.8, line=hexrgb("#43231f"))  # the glow catching the ridges
    mountains(im, 102, 22, hexrgb("#3a1f1e"), 51, bumps=0.06, peaks=0.5, line=hexrgb("#6a3424"))
    rnd = random.Random(52)
    for x in range(0, W, 6):
        x += rnd.randint(-2, 2)
        L = rnd.randint(6, 34)
        for y in range(L):
            w = max(0, int((1 - y / L) * 3))
            d.line([(x - w, y), (x + w, y)], fill=hexrgb("#1e1216"))
            if w:
                d.point((x + w, y), fill=hexrgb("#3e2224"))
    # a river of lava far below, its glow on the walls
    lava = [tint(tile(tiles("lava"), i, 5), (1.1, 0.9, 0.8)) for i in range(3)]
    for x in range(0, W, T):
        im.alpha_composite(lava[(x // T) % 3].crop((0, 0, 32, 12)), (x, 98))
    over = Image.new("RGBA", (W, H))
    od = ImageDraw.Draw(over)
    for i in range(10):
        od.rectangle([0, 98 - i * 5, W, 98 - i * 5 + 4], fill=(255, 110, 40, max(0, 60 - i * 6)))
    im.alpha_composite(over)
    # the ledge you fight on: LPC dark lava rock, with glowing cracks
    ground(im, "lavarock", 112, None, pal=("#140c0e", "#5a3a36"))
    edge_row(im, "lavarock", 104, None, pal=("#140c0e", "#5a3a36"))
    for i in range(14):
        x, y = rnd.randint(0, W), rnd.randint(118, H - 4)
        L = rnd.randint(4, 12)
        pts = [(x + k, y + int(math.sin(k * 0.9 + i) * 1.5)) for k in range(L)]
        d.line(pts, fill=hexrgb("#ff7a2a"))
        d.point(pts[L // 2], fill=hexrgb("#ffe08a"))
    vignette(im, 0.55)
    return im


SCENES = {"cienaga": cienaga, "paramo": paramo, "selva": selva, "llano": llano, "ruinas": ruinas, "abismo": abismo}


# ---------- the village: one banner per tab (480 x 110) ----------
VW_, VH_ = 480, 110


def sheet(name):
    return tiles(name)


def sprite(name, box, k=1.0, mul=None, pal=None):
    im = sheet(name).crop(box)
    if pal:
        im = colorize(im, *pal)
    elif mul:
        im = tint(im, mul)
    if k != 1.0:
        im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.NEAREST)
    return im


def put(im, spr, x, base):
    """Paste a sprite standing with its feet on y=base."""
    im.alpha_composite(spr, (int(x), int(base - spr.height)))


def plaster_wall(im, y1, col="#d9cdb2", shade="#b9aa8a", beam="#5a3a22"):
    """A whitewashed adobe wall with a dado and ceiling beams."""
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, VW_, y1], fill=hexrgb(col))
    rnd = random.Random(5)
    for i in range(500):  # the plaster's unevenness
        x, y = rnd.randrange(VW_), rnd.randrange(y1)
        d.point((x, y), fill=hexrgb(shade))
    d.rectangle([0, y1 - 18, VW_, y1], fill=hexrgb("#8a5a3a"))  # the painted dado, ochre-red
    d.line([(0, y1 - 19), (VW_, y1 - 19)], fill=hexrgb("#5a3420"))
    d.rectangle([0, 0, VW_, 6], fill=hexrgb(beam))
    for x in range(10, VW_, 60):
        d.rectangle([x, 0, x + 5, 9], fill=hexrgb(beam))


def tile_floor(im, y0, a="#a8573a", b="#8f4630", grout="#5a2a1c"):
    """Terracotta tiles in perspective-free rows."""
    d = ImageDraw.Draw(im)
    for y in range(y0, VH_, 8):
        off = 8 if (y // 8) % 2 else 0
        for x in range(-16, VW_, 16):
            d.rectangle([x + off, y, x + off + 15, y + 7], fill=hexrgb(a if (x // 16 + y // 8) % 3 else b))
        d.line([(0, y), (VW_, y)], fill=hexrgb(grout))
    for x in range(0, VW_, 16):
        for y in range(y0, VH_, 8):
            d.point((x + (8 if (y // 8) % 2 else 0), y + 3), fill=hexrgb(grout))


def wood_floor(im, y0, a="#6a4428", b="#5a3820", line="#3a2414"):
    d = ImageDraw.Draw(im)
    d.rectangle([0, y0, VW_, VH_], fill=hexrgb(a))
    for y in range(y0, VH_, 5):
        d.line([(0, y), (VW_, y)], fill=hexrgb(line))
        rnd = random.Random(y)
        for x in range(rnd.randint(0, 40), VW_, rnd.randint(50, 90)):
            d.line([(x, y + 1), (x, y + 4)], fill=hexrgb(line))
            d.line([(x + 1, y + 1), (x + 30, y + 1)], fill=hexrgb(b))


def window(d, x, y, w, h, sky=("#2a3a5a", "#d88a4a")):
    d.rectangle([x - 2, y - 2, x + w + 2, y + h + 2], fill=hexrgb("#4a2c18"))
    for yy in range(h):
        d.line([(x, y + yy), (x + w, y + yy)], fill=lerp(hexrgb(sky[0]), hexrgb(sky[1]), yy / h))
    d.line([(x + w // 2, y), (x + w // 2, y + h)], fill=hexrgb("#4a2c18"))
    d.line([(x, y + h // 2), (x + w, y + h // 2)], fill=hexrgb("#4a2c18"))


def bottle(d, x, base, col, h=8, w=4):
    d.rectangle([x, base - h, x + w - 1, base - 1], fill=hexrgb(col))
    d.rectangle([x + 1, base - h - 3, x + w - 2, base - h], fill=hexrgb("#c9c2b0"))
    d.point((x + 1, base - h + 1), fill=hexrgb("#ffffff"))
    d.point((x, base - 1), fill=hexrgb("#1a1010"))


def house_front(d, x, w, top, base, wall, roof):
    """A colonial village house: whitewashed, a red tile roof, a wooden door and a window with bars."""
    d.rectangle([x, top, x + w, base], fill=hexrgb(wall))
    for i in range(6):
        d.line([(x - 4 + i, top - 6 + i), (x + w + 4 - i, top - 6 + i)], fill=hexrgb(roof if i % 2 else "#8a2a1c"))
    for xx in range(x - 4, x + w + 4, 3):
        d.point((xx, top - 6), fill=hexrgb("#5a1a12"))
    dx = x + w // 3
    d.rectangle([dx, base - 16, dx + 8, base], fill=hexrgb("#4a2a16"))
    d.rectangle([dx + 1, base - 15, dx + 7, base], fill=hexrgb("#6a3e20"))
    wx = x + w * 2 // 3
    d.rectangle([wx, top + 6, wx + 8, top + 14], fill=hexrgb("#2a1a12"))
    for k in range(3):
        d.line([(wx + 2 + k * 2, top + 6), (wx + 2 + k * 2, top + 14)], fill=hexrgb("#7a5a3a"))
    d.rectangle([x, base - 4, x + w, base], fill=hexrgb("#6a3a2a"))  # the painted plinth


def v_merchant():
    """The plaza at dusk: whitewashed houses, the fire you rest by, the potion seller's stall."""
    im = Image.new("RGBA", (VW_, VH_))
    gradient(im, 0, 60, "#2a2a4a", "#e09a5a", steps=8)
    d = ImageDraw.Draw(im)
    mountains(im, 46, 14, hexrgb("#3a3a52"), 61, bumps=0.025, peaks=0.5)
    for x, w, top, wall, roof in ((-10, 80, 34, "#e4dccb", "#b3402a"), (76, 64, 30, "#d8cfa8", "#a63a26"), (300, 70, 32, "#e6dfd0", "#b3402a"), (376, 120, 28, "#d9d2bf", "#9e3424")):
        house_front(d, x, w, top, 78, wall, roof)
    # the church tower behind
    d.rectangle([214, 8, 240, 78], fill=hexrgb("#e8e0cc"))
    d.polygon([(210, 8), (227, -4), (244, 8)], fill=hexrgb("#a63a26"))
    d.rectangle([222, 16, 232, 28], fill=hexrgb("#3a2a20"))
    d.ellipse([224, 18, 230, 26], fill=hexrgb("#c9a040"))
    # the plaza: cobblestones (code)
    d.rectangle([0, 78, VW_, VH_], fill=hexrgb("#6a5442"))
    rnd = random.Random(19)
    for y in range(79, VH_, 4):
        off = rnd.randint(0, 5)
        for x in range(-6 + off, VW_, 7):
            c = rnd.choice(["#9a8268", "#8a7058", "#a88e72", "#7e6650"])
            d.rounded_rectangle([x, y, x + 5, y + 2], radius=1, fill=hexrgb(c))
    # the stall: posts, a striped awning, a counter with potions
    sx = 300
    d.rectangle([sx, 52, sx + 2, 98], fill=hexrgb("#4a2a16"))
    d.rectangle([sx + 118, 52, sx + 120, 98], fill=hexrgb("#4a2a16"))
    for i in range(12):
        d.polygon([(sx - 4 + i * 11, 48), (sx + 7 + i * 11, 48), (sx + 7 + i * 11, 58), (sx - 4 + i * 11, 58)], fill=hexrgb("#c23a2a" if i % 2 else "#efe6d0"))
        d.pieslice([sx - 4 + i * 11, 54, sx + 7 + i * 11, 63], 0, 180, fill=hexrgb("#c23a2a" if i % 2 else "#efe6d0"))
    d.rectangle([sx - 2, 80, sx + 122, 98], fill=hexrgb("#7a4a26"))
    d.line([(sx - 2, 80), (sx + 122, 80)], fill=hexrgb("#a8703a"))
    for i, col in enumerate(["#d23a3a", "#3a6ad2", "#a04ad2", "#d23a3a", "#3a6ad2", "#d23a3a", "#a04ad2", "#3a6ad2"]):
        bottle(d, sx + 8 + i * 14, 80, col, h=7 + (i % 3))
    put(im, sprite("signs", (72, 4, 96, 28)), sx + 50, 48)
    put(im, sprite("barrel", (64, 2, 112, 63), 0.8), sx + 126, 104)
    put(im, sprite("buckets", (5, 5, 26, 29)), sx - 26, 102)
    # the fire you rest by, ringed with stones
    fx, fy = 120, 98
    for i in range(9):
        a = i * math.pi * 2 / 9
        d.ellipse([fx + math.cos(a) * 11 - 3, fy + math.sin(a) * 3 - 2, fx + math.cos(a) * 11 + 3, fy + math.sin(a) * 3 + 2], fill=hexrgb("#6a645a"))
    d.line([(fx - 8, fy), (fx + 8, fy - 3)], fill=hexrgb("#4a2a16"), width=2)
    d.line([(fx - 8, fy - 3), (fx + 8, fy)], fill=hexrgb("#5a3418"), width=2)
    d.polygon([(fx - 6, fy - 2), (fx, fy - 16), (fx + 6, fy - 2)], fill=hexrgb("#f08a2a"))
    d.polygon([(fx - 3, fy - 2), (fx, fy - 10), (fx + 3, fy - 2)], fill=hexrgb("#ffe08a"))
    shade(im, 60, VH_, (40, 20, 40), 30)
    vignette(im, 0.4)
    return im


def glyph(d, kind, x, y, col, k=1):
    """Petroglyphs, original: a spiral, a frog, a sun face, a zigzag, a figure, an eye."""
    c = hexrgb(col)
    if kind == "spiral":
        for r in range(1, 4):
            d.arc([x - r * 2 * k, y - r * 2 * k, x + r * 2 * k, y + r * 2 * k], 0 if r % 2 else 180, 180 if r % 2 else 360, fill=c)
    elif kind == "frog":
        d.ellipse([x - 2 * k, y - 3 * k, x + 2 * k, y + 2 * k], outline=c)
        for sx in (-1, 1):
            d.line([(x + sx * 2 * k, y - 2 * k), (x + sx * 4 * k, y - 4 * k)], fill=c)
            d.line([(x + sx * 2 * k, y + 1 * k), (x + sx * 4 * k, y + 4 * k)], fill=c)
    elif kind == "sun":
        d.ellipse([x - 3 * k, y - 3 * k, x + 3 * k, y + 3 * k], outline=c)
        d.point((x - k, y - k), fill=c)
        d.point((x + k, y - k), fill=c)
        for i in range(8):
            a = i * math.pi / 4
            d.line([(x + math.cos(a) * 4 * k, y + math.sin(a) * 4 * k), (x + math.cos(a) * 6 * k, y + math.sin(a) * 6 * k)], fill=c)
    elif kind == "zigzag":
        d.line([(x - 6 * k + i * 2 * k, y + (k if i % 2 else -k)) for i in range(7)], fill=c)
    elif kind == "figure":
        d.ellipse([x - k, y - 5 * k, x + k, y - 3 * k], outline=c)
        d.line([(x, y - 3 * k), (x, y + 2 * k)], fill=c)
        d.line([(x - 3 * k, y - 3 * k), (x - 2 * k, y - k), (x + 2 * k, y - k), (x + 3 * k, y - 3 * k)], fill=c)
        d.line([(x - 2 * k, y + 5 * k), (x, y + 2 * k), (x + 2 * k, y + 5 * k)], fill=c)
    elif kind == "eye":
        d.arc([x - 4 * k, y - 2 * k, x + 4 * k, y + 4 * k], 200, 340, fill=c)
        d.arc([x - 4 * k, y - 4 * k, x + 4 * k, y + 2 * k], 20, 160, fill=c)
        d.point((x, y), fill=c)


def rune_pebble(d, x, y, rnd):
    w, h = rnd.randint(8, 11), rnd.randint(6, 8)
    d.ellipse([x, y, x + w, y + h], fill=hexrgb(rnd.choice(["#6a6a62", "#7a766a", "#5a5a58"])), outline=hexrgb("#2a2826"))
    d.point((x + 2, y + 1), fill=hexrgb("#9a968a"))
    gx, gy = x + w // 2, y + h // 2
    m = rnd.randrange(3)  # a carved mark, catching the light
    col = hexrgb("#e8d48a")
    if m == 0:
        d.line([(gx - 2, gy), (gx + 2, gy)], fill=col)
        d.line([(gx, gy - 2), (gx, gy + 2)], fill=col)
    elif m == 1:
        d.arc([gx - 2, gy - 2, gx + 2, gy + 2], 0, 270, fill=col)
    else:
        d.line([(gx - 2, gy + 1), (gx, gy - 2), (gx + 2, gy + 1)], fill=col)


def tunjo(d, x, base, h, gold="#d8a83a", dark="#7a5418", hi="#f8e08a"):
    """A tunjo: a flat gold votive figure, wire filigree for face, arms and belt (drawn, original)."""
    w = max(4, h * 5 // 12)
    top = base - h
    hh = max(3, h // 3)  # the head, a rounded block with a headdress
    d.rectangle([x - w // 2, top, x + w // 2, top + hh], fill=hexrgb(gold), outline=hexrgb(dark))
    d.line([(x - w // 2 - 1, top), (x + w // 2 + 1, top)], fill=hexrgb(hi))
    if h >= 14:
        d.point((x - w // 4, top + hh // 2), fill=hexrgb(dark))
        d.point((x + w // 4, top + hh // 2), fill=hexrgb(dark))
        d.line([(x - 1, top + hh - 2), (x + 1, top + hh - 2)], fill=hexrgb(dark))
    d.polygon([(x - w // 2 + 1, top + hh), (x + w // 2 - 1, top + hh), (x + w // 2 + 1, base), (x - w // 2 - 1, base)], fill=hexrgb(gold), outline=hexrgb(dark))
    if h >= 20:  # the big ones wear a crown of points and round ear ornaments (orejeras)
        for k in range(-2, 3):
            cx = x + k * w // 5
            d.polygon([(cx - 1, top), (cx, top - 4), (cx + 1, top)], fill=hexrgb(gold), outline=hexrgb(dark))
        for sx in (-1, 1):
            ex = x + sx * (w // 2 + 2)
            d.ellipse([ex - 2, top + hh // 2 - 2, ex + 2, top + hh // 2 + 2], fill=hexrgb(gold), outline=hexrgb(dark))
        d.line([(x, top + hh // 2 - 1), (x, top + hh // 2 + 2)], fill=hexrgb(dark))  # the nose
        for k in range(3):  # wire spirals on the body
            d.arc([x - 3, base - 8 - k * 5, x + 3, base - 4 - k * 5], 0, 300, fill=hexrgb(dark))
    if h >= 10:
        my = top + hh + (h - hh) // 3  # the arms, wire across the chest
        d.line([(x - w // 2 + 1, my), (x, my + 2), (x + w // 2 - 1, my)], fill=hexrgb(dark))
        d.line([(x - w // 2, base - (h - hh) // 3), (x + w // 2, base - (h - hh) // 3)], fill=hexrgb(dark))
        d.line([(x - w // 2 + 1, top + hh + 1), (x - w // 2 + 1, base - 2)], fill=hexrgb(hi))


def v_casetes():
    """Tunjos que hablan: Doña Remedios's bohío by the lagoon. A wattle-and-daub wall under thatch, an
    opening onto the lagoon at night with the moon in it, her woven cloth lined with little gold tunjos,
    a big tunjo standing on a stone (it glows and speaks, CSS), a shelf of offerings, candles, Don
    Eusebio's chair with his sombrero vueltiao."""
    im = Image.new("RGBA", (VW_, VH_))
    d = ImageDraw.Draw(im)
    rnd = random.Random(37)
    # bahareque: earth plaster over cane, the cane showing where it's worn
    d.rectangle([0, 0, VW_, 82], fill=hexrgb("#7a5e40"))
    for i in range(700):
        d.point((rnd.randrange(VW_), rnd.randrange(82)), fill=hexrgb(rnd.choice(["#6e5438", "#86684a", "#705638"])))
    for x0, x1, y0, y1 in ((150, 200, 30, 50), (300, 330, 54, 72), (420, 470, 18, 36)):
        d.rectangle([x0, y0, x1, y1], fill=hexrgb("#5a4228"))
        for x in range(x0 + 2, x1, 4):
            d.line([(x, y0 + 1), (x, y1 - 1)], fill=hexrgb("#a88a52"))
    d.rectangle([0, 76, VW_, 82], fill=hexrgb("#5e4630"))  # the plinth, darker earth
    # the thatch: a ragged fringe of straw along the top
    for x in range(0, VW_, 2):
        h = 6 + rnd.randint(0, 6)
        d.line([(x, 0), (x + rnd.randint(-1, 1), h)], fill=hexrgb(rnd.choice(["#b89048", "#a07a38", "#c8a058", "#8a6a2e"])))
    d.line([(0, 3), (VW_, 3)], fill=hexrgb("#5a4020"))
    # the opening onto the lagoon at night
    ox0, ox1, oy0, oy1 = 22, 112, 20, 78
    d.rectangle([ox0 - 4, oy0 - 4, ox1 + 4, oy1 + 2], fill=hexrgb("#4a3420"))
    for y in range(oy0, oy1):
        d.line([(ox0, y), (ox1, y)], fill=lerp(hexrgb("#0e1430"), hexrgb("#34365a"), (y - oy0) / (oy1 - oy0)))
    d.ellipse([88, 26, 98, 36], fill=hexrgb("#f0ecd0"))
    for sx, sy in ((34, 28), (52, 24), (70, 34), (44, 38)):
        d.point((sx, sy), fill=hexrgb("#d8d4c0"))
    d.polygon([(ox0, 58), (40, 48), (62, 52), (80, 46), (100, 50), (ox1, 54), (ox1, 62), (ox0, 62)], fill=hexrgb("#1a2030"))  # the crater's rim
    d.rectangle([ox0, 60, ox1, oy1], fill=hexrgb("#14243a"))  # the lagoon
    for k in range(5):
        d.line([(91 - k, 62 + k * 3), (95 + k, 62 + k * 3)], fill=hexrgb("#c8c4a8" if k < 3 else "#6a6a78"))
    for x in (26, 30, 33, 104, 108):  # reeds
        d.line([(x, oy1), (x + rnd.randint(-2, 2), oy1 - rnd.randint(8, 14))], fill=hexrgb("#2a3a26"))
    d.rectangle([ox0 - 4, oy1, ox1 + 4, oy1 + 4], fill=hexrgb("#4a3420"))  # the sill
    # the floor: packed earth
    d.rectangle([0, 82, VW_, VH_], fill=hexrgb("#4e3c2a"))
    for i in range(70):
        x, y = rnd.randrange(VW_), rnd.randrange(84, VH_)
        d.ellipse([x, y, x + rnd.randint(6, 16), y + rnd.randint(2, 4)], fill=hexrgb(rnd.choice(["#5a4632", "#443424"])))
    d.line([(0, 82), (VW_, 82)], fill=hexrgb("#2a2018"))
    # her low table with the woven cloth and a row of little tunjos
    tx0, tx1, ty = 130, 214, 74
    d.rectangle([tx0, ty, tx1, ty + 3], fill=hexrgb("#4a2c16"))
    d.rectangle([tx0 + 4, ty + 3, tx0 + 8, 104], fill=hexrgb("#3a2210"))
    d.rectangle([tx1 - 8, ty + 3, tx1 - 4, 104], fill=hexrgb("#3a2210"))
    cols = ["#7a2a22", "#a8782a", "#2a4a40", "#b8ac90", "#5a2a2a"]
    for y in range(ty, ty + 18):
        for x in range(tx0 + 10, tx1 - 10):
            zig = abs(((x + (y - ty) * 2) % 12) - 6)
            im.putpixel((x, y), hexrgb(cols[((y - ty) // 4 + (1 if zig < 2 else 0)) % len(cols)]))
    for x in range(tx0 + 10, tx1 - 10, 3):
        d.line([(x, ty + 18), (x, ty + 21)], fill=hexrgb("#c9a070"))
    for i, x in enumerate(range(142, 204, 11)):
        tunjo(d, x, ty, 10 + (i * 5) % 4)
    # the big tunjo on its stone
    mx = 252
    d.polygon([(mx - 16, 84), (mx - 13, 70), (mx + 13, 70), (mx + 16, 84)], fill=hexrgb("#6a6458"), outline=hexrgb("#2a2622"))
    d.line([(mx - 12, 71), (mx + 12, 71)], fill=hexrgb("#8a8476"))
    tunjo(d, mx, 70, 34)
    # a shelf of offerings: small tunjos, a clay bowl of gold dust, candles
    lx = 360
    d.rectangle([lx, 44, lx + 80, 47], fill=hexrgb("#5a3418"))
    d.line([(lx, 48), (lx + 80, 48)], fill=hexrgb("#2a1a10"))
    d.chord([lx + 34, 36, lx + 50, 48], 0, 180, fill=hexrgb("#8a4a2a"))
    d.line([(lx + 35, 42), (lx + 49, 42)], fill=hexrgb("#e8c04a"))
    for x in (lx + 28, lx + 56):
        tunjo(d, x, 44, 9)
    for x in (lx + 8, lx + 20, lx + 62, lx + 72):
        d.rectangle([x, 36, x + 4, 44], fill=hexrgb("#e8dcc0"))
    # Don Eusebio's chair, his sombrero vueltiao hanging on it
    cw, CW = hexrgb("#6a4224"), hexrgb("#3e2412")
    d.rectangle([326, 60, 328, 104], fill=CW)
    d.rectangle([344, 60, 346, 104], fill=CW)
    for y in (64, 70, 76):
        d.rectangle([326, y, 346, y + 2], fill=cw)
    d.rectangle([322, 82, 350, 85], fill=cw)
    d.line([(322, 86), (350, 86)], fill=CW)
    d.rectangle([322, 86, 324, 104], fill=CW)
    d.rectangle([348, 86, 350, 104], fill=CW)
    for x in range(326, 346, 2):
        d.point((x, 83), fill=hexrgb("#c9a070"))
    hx, hy = 336, 58
    d.ellipse([hx - 12, hy + 2, hx + 12, hy + 7], fill=hexrgb("#e8dcc0"))
    for k in range(-10, 11, 3):
        d.point((hx + k, hy + 4), fill=hexrgb("#2a1a10"))
    d.ellipse([hx - 6, hy - 6, hx + 6, hy + 5], fill=hexrgb("#e8dcc0"))
    for yy in range(hy - 5, hy + 4, 2):
        d.line([(hx - 5, yy), (hx + 5, yy)], fill=hexrgb("#2a1a10"))
    put(im, sprite("castle_lightsources", (29, 6, 35, 31)), 216, 84)
    put(im, sprite("castle_lightsources", (29, 6, 35, 31)), 118, 84)
    shade(im, 0, VH_, (20, 12, 8), 40)
    vignette(im, 0.55)
    return im


def scale(d, x, base):
    """A brass balance."""
    g, G = hexrgb("#d8a83a"), hexrgb("#8a6a1a")
    d.rectangle([x - 6, base - 2, x + 6, base], fill=G)
    d.line([(x, base - 2), (x, base - 22)], fill=g, width=2)
    d.line([(x - 18, base - 22), (x + 18, base - 20)], fill=g)
    for px, py in ((x - 18, base - 22), (x + 18, base - 20)):
        d.line([(px, py), (px - 5, py + 8)], fill=G)
        d.line([(px, py), (px + 5, py + 8)], fill=G)
        d.chord([px - 7, py + 5, px + 7, py + 12], 0, 180, fill=g)
    d.ellipse([x - 2, base - 25, x + 2, base - 21], fill=g)


def v_sell():
    """The trader's counter: a balance, coins, chests and drawers behind."""
    im = Image.new("RGBA", (VW_, VH_))
    plaster_wall(im, 80, col="#cdbf9c", shade="#b8a982")
    d = ImageDraw.Draw(im)
    put(im, sprite("cabinets", (0, 5, 128, 74), 0.8, mul=(0.9, 0.85, 0.8)), 30, 76)
    put(im, sprite("cabinets", (0, 101, 160, 170), 0.7), 300, 78)
    window(d, 220, 18, 30, 32, sky=("#7ab0d8", "#e8e0b0"))
    tile_floor(im, 80)
    d.rectangle([120, 66, 380, 106], fill=hexrgb("#6a3e1e"))
    d.rectangle([120, 64, 380, 68], fill=hexrgb("#8a5a2e"))
    for x in range(130, 380, 40):
        d.rectangle([x, 72, x + 30, 100], outline=hexrgb("#4a2a14"))
    scale(d, 250, 64)
    for i, x in enumerate((168, 176, 184, 300, 308)):  # stacks of coins
        for k in range(3 + (i * 7) % 5):
            d.ellipse([x, 62 - k * 2, x + 6, 64 - k * 2], fill=hexrgb("#e8c040"), outline=hexrgb("#8a6a1a"))
    d.ellipse([330, 58, 344, 64], fill=hexrgb("#6a4a2a"))  # a purse
    d.rectangle([334, 54, 340, 59], fill=hexrgb("#7a5a32"))
    put(im, sprite("chests", (32, 0, 64, 32)), 404, 104)
    put(im, sprite("chests", (0, 0, 32, 32)), 436, 106)
    put(im, sprite("barrel", (2, 10, 30, 48)), 70, 106)
    put(im, sprite("signs", (40, 4, 64, 28)), 240, 16)
    vignette(im, 0.4)
    return im


def v_stash():
    """The cellar where your things wait: stone walls, an arch, chests and barrels by torchlight."""
    im = Image.new("RGBA", (VW_, VH_))
    d = ImageDraw.Draw(im)
    rnd = random.Random(12)
    for y in range(0, 84, 8):  # stone courses
        off = 0 if (y // 8) % 2 else 10
        for x in range(-20, VW_, 20):
            c = rnd.choice(["#4a4440", "#55504a", "#3e3a36"])
            d.rectangle([x + off, y, x + off + 19, y + 7], fill=hexrgb(c), outline=hexrgb("#2a2624"))
    # an arch into the dark
    ax = 240
    d.rectangle([ax - 26, 24, ax + 26, 84], fill=hexrgb("#141010"))
    d.pieslice([ax - 26, 4, ax + 26, 44], 180, 360, fill=hexrgb("#141010"))
    d.arc([ax - 28, 2, ax + 28, 46], 180, 360, fill=hexrgb("#6a645a"), width=3)
    d.rectangle([ax - 28, 24, ax - 25, 84], fill=hexrgb("#6a645a"))
    d.rectangle([ax + 25, 24, ax + 28, 84], fill=hexrgb("#6a645a"))
    wood_floor(im, 84, a="#3e3028", b="#342820", line="#1e1612")
    for i, x in enumerate((30, 66, 104, 340, 376, 414)):
        put(im, sprite("chests", (32 * (i % 2), 0, 32 * (i % 2) + 32, 32)), x, 104 + (i % 3))
    put(im, sprite("barrel", (64, 2, 112, 63)), 168, 100)
    put(im, sprite("barrel", (34, 26, 62, 64)), 290, 104)
    for x in (150, 320):
        put(im, sprite("castle_lightsources", (72, 4, 88, 60), 0.8), x, 60)
    over = Image.new("RGBA", (VW_, VH_))
    od = ImageDraw.Draw(over)
    for x in (156, 326):
        for r, a in ((60, 18), (36, 26), (18, 34)):
            od.ellipse([x - r, 30 - r * 0.8, x + r, 30 + r * 0.8], fill=(255, 170, 80, a))
    im.alpha_composite(over)
    vignette(im, 0.65)
    return im


def alembic(d, x, base):
    """A copper still: the pot on its fire, the swan neck, a coil, a flask catching the drops."""
    cu, CU, hi = hexrgb("#c46a32"), hexrgb("#7a3a1a"), hexrgb("#f0a060")
    d.ellipse([x - 16, base - 30, x + 16, base - 4], fill=cu, outline=CU)
    d.arc([x - 12, base - 27, x + 4, base - 10], 180, 270, fill=hi)
    d.rectangle([x - 5, base - 38, x + 5, base - 28], fill=cu, outline=CU)
    d.ellipse([x - 8, base - 44, x + 8, base - 34], fill=cu, outline=CU)
    pts = [(x + 6, base - 40), (x + 22, base - 46), (x + 38, base - 40), (x + 48, base - 30)]
    d.line(pts, fill=CU, width=3)
    d.line(pts, fill=cu, width=1)
    cx = x + 52
    d.rectangle([cx - 6, base - 34, cx + 10, base - 10], fill=hexrgb("#5a3a22"), outline=hexrgb("#3a2414"))  # the cooling barrel
    for k in range(4):
        d.arc([cx - 6, base - 32 + k * 6, cx + 10, base - 26 + k * 6], 0, 180, fill=cu)
    d.line([(cx + 10, base - 14), (cx + 18, base - 12)], fill=cu)
    fx = cx + 22
    d.ellipse([fx - 6, base - 12, fx + 6, base], fill=hexrgb("#8ad8a0"), outline=hexrgb("#3a6a4a"))
    d.rectangle([fx - 2, base - 18, fx + 2, base - 11], fill=hexrgb("#b8e8c8"), outline=hexrgb("#3a6a4a"))
    for i in range(3):  # the fire under the pot
        d.polygon([(x - 10 + i * 8, base), (x - 7 + i * 8, base - 6), (x - 4 + i * 8, base)], fill=hexrgb("#f08a2a"))


def v_alembic():
    """The still-room: shelves of bottles, the stove, the copper alembic bubbling."""
    im = Image.new("RGBA", (VW_, VH_))
    plaster_wall(im, 82, col="#bfb293", shade="#a89a7a")
    d = ImageDraw.Draw(im)
    rnd = random.Random(14)
    for sy in (22, 44):  # shelves of bottles and jars
        d.rectangle([20, sy, 170, sy + 2], fill=hexrgb("#5a3418"))
        d.rectangle([320, sy, 460, sy + 2], fill=hexrgb("#5a3418"))
        for x in list(range(24, 168, 9)) + list(range(324, 458, 9)):
            if rnd.random() < 0.8:
                bottle(d, x, sy, rnd.choice(["#3a8a5a", "#8a3ad2", "#d23a3a", "#3a6ad2", "#d2a03a", "#6a4a2a"]), h=rnd.randint(6, 12), w=rnd.choice((4, 5, 6)))
    # bundles of herbs hanging from the beam
    for x in range(200, 300, 16):
        d.line([(x, 6), (x, 14)], fill=hexrgb("#5a3a22"))
        d.polygon([(x - 4, 14), (x + 4, 14), (x + 2, 26), (x - 2, 26)], fill=hexrgb("#5a7a3a" if x % 32 else "#7a6a3a"))
    tile_floor(im, 82)
    put(im, sprite("kitchen", (0, 0, 64, 123), 0.75), 380, 106)  # the stove
    # the work table with flasks, the still on it
    d.rectangle([120, 74, 330, 80], fill=hexrgb("#6a3e1e"))
    d.rectangle([126, 80, 132, 106], fill=hexrgb("#4a2a14"))
    d.rectangle([318, 80, 324, 106], fill=hexrgb("#4a2a14"))
    alembic(d, 170, 74)
    for i, (x, col) in enumerate(((268, "#d23a8a"), (284, "#3ab0d2"), (300, "#e8c03a"))):
        d.ellipse([x - 5, 66, x + 5, 74], fill=hexrgb(col), outline=hexrgb("#2a2a2a"))
        d.rectangle([x - 1, 58, x + 1, 66], fill=hexrgb("#c9e0e0"), outline=hexrgb("#2a2a2a"))
    put(im, sprite("buckets", (37, 21, 58, 45)), 90, 106)
    vignette(im, 0.45)
    return im


# one per set, in its colours: (cord, pendant, shine); in the game's set order (SETS in data.js)
NECKLACES = {
    "arriero": ("#8a5a2a", "#c87a3a", "#f0b070"), "cacique": ("#3a6a2a", "#d8a83a", "#fff0a0"), "centinela": ("#5a6a7a", "#9ab0c8", "#e8f0ff"),
    "patasola": ("#5a1a1a", "#c83a3a", "#ff9a8a"), "jaguar": ("#6a5a2a", "#e0b040", "#fff0b0"), "cienaga": ("#2a3a1a", "#8ab43a", "#e6ffb0"),
    "mohan": ("#14485a", "#3c8fa6", "#bff0ff"), "yogui": ("#5a2a2a", "#e8e4d8", "#ffffff"), "vajra": ("#7a2a14", "#f2c12e", "#fff4cf"),
    "averno": ("#2a0a08", "#ff5a1a", "#ffd27a"), "trueno": ("#252a3a", "#7fc4ff", "#fffbd0"), "sol": ("#8a5a0a", "#ffcf3a", "#fff8d0"),
    "guardian": ("#1a1a2a", "#efe8d6", "#ff8a1a"), "laguna": ("#7a2a4a", "#e07aa0", "#ffd0e0"), "condor": ("#3a1a14", "#e5512f", "#ffb347"),
    "origen": ("#0c3558", "#3fc4e4", "#e0ffff"),
    "bachue": ("#a8781e", "#4fb3b0", "#f7d76a"), "nevado": ("#8a9aa8", "#bfeaff", "#ffffff"), "vientos": ("#5fb8e8", "#e8f8ff", "#ffffff"),
    "montana": ("#5a4a3a", "#ff7a1a", "#ffb347"), "kalachakra": ("#f2c12e", "#2f6fd0", "#ffe38a"), "luzclara": ("#f2f2ee", "#ffffff", "#f28a2a"),
    "osario": ("#c4b496", "#ff9a1a", "#fff4c0"), "tairona": ("#7e3420", "#d4a02c", "#f8d868"), "dorado": ("#a8701a", "#22a8a4", "#ffe07a"),
    "relampago": ("#4e1e8a", "#4ae0ff", "#ffffff"), "vigilia": ("#5e5878", "#e4e0f2", "#ffffff"), "pacto": ("#201414", "#e0201a", "#ff7040"),
    "firmamento": ("#1a2a74", "#e0b040", "#ffffff"),
    "madreagua": ("#0e6268", "#e8b030", "#8ae0d4"),
    "caiman": ("#2a4a1e", "#e8d040", "#9ab45a"), "andes": ("#8e2216", "#eef2f8", "#f2d12e"),
    "arhuaco": ("#6a4a2e", "#f4f0e6", "#ffffff"),
    "galeon": ("#1e4a52", "#d8a830", "#ffe07a"),
    "frailejon": ("#56685a", "#d8c030", "#f8ea7a"),
    "bochica": ("#7a5a32", "#2a8ad0", "#d0f4ff"),
    "bufeo": ("#6a4e26", "#d07a98", "#f6c0d2"),
    "llanero": ("#7a4a1a", "#f06a1a", "#ffb060"),
    "madremonte": ("#1e5218", "#8ac85a", "#e0ffc0"),
    "silbon": ("#1a1a26", "#b8ac90", "#ffffff"),
    "tunda": ("#14504a", "#e06a3a", "#ffa880"),
    "mahamudra": ("#1a5aa8", "#c4ccd6", "#ffffff"),
    "candileja": ("#4a423a", "#e04a0e", "#fff0a0"),
    "sombreron": ("#1e1a18", "#e01a1a", "#ff6a5a"),
    "marimba": ("#7a4a16", "#2a7ac0", "#7ac0f0"),
    "huitaca": ("#6a2a8e", "#e8d040", "#fff48a"),
    "canocristales": ("#a01a24", "#3ac08a", "#f0e040"),
    "dzogchen": ("#1e3a8e", "#f0b030", "#ffffff"),
    "pastor": ("#b8a48a", "#5aa040", "#fffaf0"),
    "barquero": ("#3a7ab0", "#c8a850", "#e8f6ff"),
    "rey": ("#5a1e8a", "#e8b030", "#ffe07a"),
    "shakya": ("#e8961a", "#a02a3a", "#fff2d0"),
    "tsokye": ("#0e3e8a", "#e0609a", "#ffb0d4"),
    "loden": ("#d0d6de", "#4a96c8", "#ffffff"),
    "pemagyalpo": ("#d83a3a", "#e8b030", "#ffe4dc"),
    "pandita": ("#b8402a", "#d8b030", "#f8e070"),
    "nyima": ("#e0c020", "#e06a10", "#fffce0"),
    "sengedradrok": ("#1a3a90", "#f06a10", "#fff0a0"),
    "drollo": ("#8e2a14", "#e8801a", "#ffc060"),
    "teyuna": ("#3a5a2a", "#8ab45a", "#e0f0b0"),
    "tatacoa": ("#8a3a1a", "#e07a3a", "#ffd0a0"),
    "sanagustin": ("#5a5a4a", "#c8c0a0", "#fff8e0"),
    "tierradentro": ("#2a1a1a", "#c83a2a", "#f0e0d0"),
    "taraverde": ("#1a6a3a", "#3ac870", "#d0ffe0"),
    "chia": ("#5a6a8a", "#e0e8f8", "#ffffff"),
    "sue": ("#a8701a", "#ffcf3a", "#fff8d0"),
    "catedralsal": ("#6a7a8a", "#d8e8f0", "#ffffff"),
    "choco": ("#1a4a4a", "#3aa8a0", "#c0f0e8"),
    "milarepa": ("#a8a8b0", "#f4f4f0", "#ffffff"),
    "yurupari": ("#3a2a1a", "#e05a1a", "#ffd060"),
    "pulowi": ("#8a2a5a", "#f070a0", "#ffe0f0"),
    "juya": ("#2a3a6a", "#7fc4ff", "#fffbd0"),
    "quimbaya": ("#8a5a0a", "#f0c040", "#fff8d0"),
    "zenu": ("#6a5a2a", "#d8c070", "#fff0b0"),
    "manjushri": ("#c8701a", "#f0a020", "#fff0c0"),
    "mompox": ("#5a3a2a", "#e8b060", "#fff0c0"),
    "nevadoruiz": ("#3a2a2a", "#ff5a1a", "#ffd27a"),
    "chingaza": ("#3a5a6a", "#8ac8d8", "#e8ffff"),
    "chenrezig": ("#e8e8f0", "#ffffff", "#c8e0ff"),
    "magdalena": ("#5a4a2a", "#a8803a", "#e8d0a0"),
    "karagabi": ("#1a1a2a", "#e0d040", "#ffffff"),
    "tutruica": ("#1a2a2a", "#3a8a6a", "#a0e0c0"),
    "naropa": ("#7a1a1a", "#e04a2a", "#ffc0a0"),
    "serankua": ("#a8a090", "#f4f0e6", "#ffffff"),
    "aluna": ("#0e2a4a", "#4a8ad0", "#d0f0ff"),
    "murallas": ("#7a5a3a", "#e8c890", "#fff4d8"),
    "tilopa": ("#8a6a3a", "#f0d080", "#fffae0"),
    "chiminigagua": ("#0e0e1e", "#ffe070", "#ffffff"),
    "nencatacoa": ("#5a3a1a", "#d07a3a", "#ffd0a0"),
    "marpa": ("#3a4a7a", "#c8d0e8", "#ffffff"),
    "zaque": ("#6a2a0a", "#e0802a", "#ffd090"),
    "zipa": ("#1e4a3a", "#4ac08a", "#e0ffd0"),
    "cauca": ("#4a3a2a", "#8a7a4a", "#d8c890"),
    "yeshe": ("#8a1a3a", "#e05a7a", "#ffd0e0"),
    "orinoco": ("#2a3a4a", "#5a9ac8", "#d0f0ff"),
    "machig": ("#2a2a3a", "#e8e0d8", "#ffffff"),
    "calima": ("#7a5a1a", "#e8b040", "#fff4c0"),
    "barnizpasto": ("#3a1a4a", "#e04ac0", "#ffd0f0"),
    "medicina": ("#0e2a8a", "#3a6ae0", "#c0d8ff"),
    "gampopa": ("#c8a030", "#f0e0a0", "#ffffff"),
    "sanandres": ("#0e5a7a", "#3ad0e0", "#e0ffff"),
    "coronanegra": ("#0e0e12", "#d8a030", "#ffe8a0"),
    "malpelo": ("#1a2a3a", "#6a8aa8", "#d0e8ff"),
    "nagarjuna": ("#2a5a5a", "#80e0d0", "#ffffff"),
    "selva": ("#1a4a1a", "#4ab03a", "#d0ffb0"),
    "vajrasattva": ("#d8e0ec", "#ffffff", "#e0f0ff"),
    "llorona": ("#2a2a3a", "#a8b8d0", "#ffffff"),
    "shantideva": ("#8a6a1a", "#f0c860", "#fff8e0"),
    "mulatrespatas": ("#2a1a14", "#e0401a", "#ffb060"),
    "vajrayogini": ("#8a0e1a", "#ff3a2a", "#ffc0a0"),
    "mahakala": ("#0e0e1a", "#3a5ad0", "#ff8a2a"),
    "sayona": ("#3a3a3a", "#f0f0f0", "#ffffff"),
    "amitabha": ("#a01a1a", "#ff7a3a", "#fff0c0"),
    "prajna": ("#c8a020", "#ffe080", "#ffffff"),
    "bardo": ("#1a1a3a", "#8a8ae0", "#e0e0ff"),
    "samantabhadra": ("#0e1a5a", "#4a7ae8", "#ffffff"),
    "cincobudas": ("#a01a24", "#3ac08a", "#f0e040"),
    "ruedadharma": ("#c8a020", "#ffffff", "#ffe070"),
}
# hung by tier (plain sets, then ancestral, legendary, mythic), each tier by level, as the Collares cards are
NECK_ORDER = ["arriero", "cacique", "patasola", "centinela", "cienaga", "mohan", "yogui", "jaguar", "vajra", "averno", "trueno", "sol",
              "guardian", "tairona", "dorado", "pastor", "relampago", "vigilia", "shakya", "andes", "loden", "frailejon", "llanero", "silbon",
              "candileja", "marimba", "canocristales", "teyuna", "tatacoa", "tierradentro", "chia", "catedralsal", "choco", "yurupari", "juya", "zenu",
              "mompox", "chingaza", "magdalena", "tutruica", "serankua", "murallas", "nencatacoa", "zaque", "cauca", "orinoco", "calima", "barnizpasto",
              "sanandres", "malpelo", "selva", "llorona", "mulatrespatas", "sayona", "laguna", "bachue", "nevado", "osario", "madreagua", "barquero",
              "caiman", "tsokye", "bochica", "pandita", "tunda", "huitaca", "sanagustin", "sue", "pulowi", "nevadoruiz", "karagabi", "aluna",
              "marpa", "yeshe", "gampopa", "nagarjuna", "shantideva", "bardo", "condor", "vientos", "montana", "arhuaco", "rey", "pacto",
              "galeon", "pemagyalpo", "madremonte", "nyima", "sombreron", "taraverde", "milarepa", "manjushri", "naropa", "tilopa", "zipa", "machig",
              "coronanegra", "vajrasattva", "mahakala", "prajna", "origen", "kalachakra", "luzclara", "firmamento", "bufeo", "mahamudra", "sengedradrok", "drollo",
              "dzogchen", "quimbaya", "chenrezig", "chiminigagua", "medicina", "vajrayogini", "amitabha", "samantabhadra", "cincobudas", "ruedadharma"]
assert sorted(NECK_ORDER) == sorted(NECKLACES)
NECKLACES = {k: NECKLACES[k] for k in NECK_ORDER}
NECK_CELL = (16, 40)  # each necklace's own picture, hung from the top centre


RACK_Y = (10, 34, 58)  # three rails, a third of the shirts on each, top first
PER_RACK = -(-len(NECKLACES) // len(RACK_Y))


def neck_x(i, n=len(NECKLACES)):
    row, k = divmod(i, PER_RACK)
    step = (VW_ - 60) / (PER_RACK - 1)
    return 30 + k * step + (step / 2 if row % 2 else 0)


def neck_y(i):
    return RACK_Y[i // PER_RACK]


def necklace(cord, pend, shine, drop):
    """A set's magic undershirt on a wooden hanger (the cell kept the necklaces' size and name).
    drop: how far down the hook it hangs, so the row isn't a straight line."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from set_art import shirt_pic
    im = Image.new("RGBA", NECK_CELL)
    d = ImageDraw.Draw(im)
    x = NECK_CELL[0] // 2
    hy = drop - 8
    d.line([(x, 0), (x, hy)], fill=hexrgb("#c8a060"))  # the hook
    d.line([(x - 6, hy + 3), (x, hy), (x + 6, hy + 3)], fill=hexrgb("#8a5a2a"))  # the hanger's arms
    im.alpha_composite(shirt_pic(cord, pend, shine), (0, hy + 1))
    return im


def v_collares():
    """The tailor's back room: a velvet wall with three long rails of empty pegs, two candles,
    a dark wooden floor. The sets' undershirts are drawn apart (v-camisetas-shirts.png): the game hangs the
    ones you have. (They were necklaces once: the names inside still say neck.)"""
    im = Image.new("RGBA", (VW_, VH_))
    d = ImageDraw.Draw(im)
    gradient(im, 0, 84, "#2a0e14", "#4a1a22")
    for x in range(0, VW_, 40):  # velvet panels in carved frames
        d.rectangle([x + 3, 6, x + 36, 80], outline=hexrgb("#6a4a22"))
        d.rectangle([x + 5, 8, x + 34, 78], outline=hexrgb("#24080c"))
    d.rectangle([0, 0, VW_, 4], fill=hexrgb("#5a3a1a"))
    wood_floor(im, 84, a="#3a2418", b="#301c12", line="#1a0e08")
    for ry in RACK_Y:
        d.rectangle([14, ry - 4, VW_ - 14, ry], fill=hexrgb("#6a4422"), outline=hexrgb("#3a2410"))
    for i in range(len(NECKLACES)):
        x, ry = neck_x(i), neck_y(i)
        d.rectangle([x - 1, ry, x + 1, ry + 3], fill=hexrgb("#c8a060"))
    for x in (140, 340):
        d.rectangle([x - 2, 62, x + 2, 74], fill=hexrgb("#efe6cf"))
        d.polygon([(x, 54), (x + 3, 60), (x, 63), (x - 3, 60)], fill=hexrgb("#ffb347"))
    over = Image.new("RGBA", (VW_, VH_))
    od = ImageDraw.Draw(over)
    for x in (140, 340):
        for r, a in ((70, 16), (40, 24), (18, 34)):
            od.ellipse([x - r, 58 - r * 0.8, x + r, 58 + r * 0.8], fill=(255, 170, 80, a))
    im.alpha_composite(over)
    vignette(im, 0.55)
    # the necklaces: one strip of cells, and where each hangs (in % of the scene, for the page)
    strip = Image.new("RGBA", (NECK_CELL[0] * len(NECKLACES), NECK_CELL[1]))
    place = {}
    for i, (sid, (cord, pend, shine)) in enumerate(NECKLACES.items()):
        strip.alpha_composite(necklace(cord, pend, shine, 12 + (i % 3) * 3), (i * NECK_CELL[0], 0))
        x0, y0 = neck_x(i) - NECK_CELL[0] / 2, neck_y(i) + 2
        place[sid] = [round(x0 / VW_ * 100, 3), round(y0 / VH_ * 100, 3), i]
    strip.save(os.path.join(OUT, "v-camisetas-shirts.png"))
    json.dump({"cell": NECK_CELL, "scene": [VW_, VH_], "n": len(NECKLACES), "at": place},
              open(os.path.join(OUT, "v-camisetas-shirts.json"), "w"), separators=(",", ":"))
    return im



def _shade(c, t):
    """A hex colour darker (t<0) or lighter (t>0)."""
    r, g, b = hexrgb(c)[:3]
    to = 255 if t > 0 else 0
    t = abs(t)
    return "#%02x%02x%02x" % tuple(round(v + (to - v) * t) for v in (r, g, b))


def v_establo():
    """The stable: a plank barn at sundown, the big door open on green Andean hills, stalls along the
    back wall, hay stacked up, a lantern on the beam, straw on the floor. The animals stand in front."""
    W, H = VW_, VH_
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    rnd = random.Random(31)
    # plank wall
    x = 0
    while x < W:
        w = rnd.choice((7, 8, 9))
        c = rnd.choice(["#5a3c24", "#4e3420", "#62422a", "#563a22"])
        d.rectangle([x, 0, x + w - 1, 88], fill=hexrgb(c))
        d.line([(x, 0), (x, 88)], fill=hexrgb("#2e1e12"))
        for _ in range(2):  # grain and knots
            yy = rnd.randrange(4, 84)
            d.line([(x + 2, yy), (x + 2, yy + rnd.randrange(4, 10))], fill=hexrgb(_shade(c, -0.18)))
        if rnd.random() < 0.25:
            ky = rnd.randrange(20, 80)
            d.ellipse([x + 2, ky, x + 4, ky + 2], fill=hexrgb("#2e1e12"))
        x += w
    # the open door (left): sky, hills, a wax palm
    dx0, dx1, dy0 = 34, 112, 16
    for y in range(dy0, 88):
        t = (y - dy0) / (88 - dy0)
        top, bot = hexrgb("#f0a860"), hexrgb("#ffe0a0")
        d.line([(dx0, y), (dx1, y)], fill=tuple(round(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    d.ellipse([84, 30, 98, 44], fill=hexrgb("#fff2c8"))  # the sun going down
    for (base, col, amp, ph) in ((60, "#6a8a5a", 7, 0.0), (70, "#4a7040", 6, 1.3), (80, "#3a5a30", 4, 2.1)):
        pts = [(dx0, 88)] + [(xx, base - amp * math.sin(xx / 13 + ph) - amp * 0.5 * math.sin(xx / 5 + ph)) for xx in range(dx0, dx1 + 1, 2)] + [(dx1, 88)]
        d.polygon(pts, fill=hexrgb(col))
    px = 52  # a wax palm on the hill
    d.line([(px, 82), (px + 1, 46)], fill=hexrgb("#c8c0a8"), width=1)
    for a in (-150, -120, -60, -30, -95):
        r_ = math.radians(a)
        d.line([(px + 1, 46), (px + 1 + 9 * math.cos(r_), 46 + 9 * math.sin(r_) + 3)], fill=hexrgb("#2e5a2a"), width=2)
    for k in range(3):  # cows far off
        cx, cy = 70 + k * 9, 72 - k
        d.rectangle([cx, cy, cx + 4, cy + 2], fill=hexrgb("#f0e8e0" if k != 1 else "#3a2a20"))
    # door frame and the door swung open against the wall, with its Z brace
    d.rectangle([dx0 - 4, dy0 - 4, dx1 + 4, dy0 - 1], fill=hexrgb("#3a2414"))
    d.rectangle([dx0 - 4, dy0, dx0 - 1, 88], fill=hexrgb("#3a2414"))
    d.rectangle([dx1 + 1, dy0, dx1 + 4, 88], fill=hexrgb("#3a2414"))
    d.rectangle([4, dy0 + 2, dx0 - 6, 88], fill=hexrgb("#7a4a2a"), outline=hexrgb("#3a2414"))
    d.line([(6, dy0 + 6), (dx0 - 8, dy0 + 6)], fill=hexrgb("#3a2414"), width=2)
    d.line([(6, 82), (dx0 - 8, 82)], fill=hexrgb("#3a2414"), width=2)
    d.line([(6, 82), (dx0 - 8, dy0 + 6)], fill=hexrgb("#3a2414"), width=2)
    # beam and rafters
    d.rectangle([0, 6, W, 13], fill=hexrgb("#3e2816"))
    d.line([(0, 6), (W, 6)], fill=hexrgb("#6a4828"))
    d.line([(0, 13), (W, 13)], fill=hexrgb("#24160c"))
    for x in range(140, W, 70):
        d.polygon([(x, 0), (x + 6, 0), (x + 6, 6), (x, 6)], fill=hexrgb("#2e1e10"))
    # stalls along the back: low plank walls with a cross brace, a window in the middle one
    for k, sx in enumerate(range(128, W - 76, 60)):
        d.rectangle([sx, 54, sx + 56, 88], fill=hexrgb("#6e4828"), outline=hexrgb("#2e1e12"))
        for yy in (60, 68, 76):
            d.line([(sx + 1, yy), (sx + 55, yy)], fill=hexrgb("#4a301a"))
        d.line([(sx + 2, 56), (sx + 54, 86)], fill=hexrgb("#8a5c32"), width=2)
        d.line([(sx + 54, 56), (sx + 2, 86)], fill=hexrgb("#8a5c32"), width=2)
        d.rectangle([sx - 2, 48, sx + 2, 88], fill=hexrgb("#3a2414"))
        if k == 2:  # a little window with the sky
            d.rectangle([sx + 16, 24, sx + 40, 42], fill=hexrgb("#f4c078"), outline=hexrgb("#2e1e12"))
            d.line([(sx + 28, 24), (sx + 28, 42)], fill=hexrgb("#2e1e12"))
            d.line([(sx + 16, 33), (sx + 40, 33)], fill=hexrgb("#2e1e12"))
        if k == 0:  # a horseshoe for luck, points up
            d.arc([sx + 22, 30, sx + 32, 40], 0, 180, fill=hexrgb("#a8a8a8"), width=2)
        if k == 1:  # a saddle on its peg
            d.rectangle([sx + 26, 30, sx + 28, 34], fill=hexrgb("#2e1e12"))
            d.pieslice([sx + 16, 30, sx + 40, 48], 180, 360, fill=hexrgb("#8a3a1e"), outline=hexrgb("#3a1a0c"))
            d.line([(sx + 22, 39), (sx + 22, 47)], fill=hexrgb("#6a2a14"))
            d.rectangle([sx + 20, 47, sx + 24, 49], fill=hexrgb("#a8a8a8"))
        if k == 3:  # a woven ruana hung over the wall
            for i, c in enumerate(("#b02a2a", "#e0b030", "#2a6ab0", "#b02a2a", "#2a8a4a")):
                d.rectangle([sx + 8 + i * 3, 50, sx + 10 + i * 3, 66], fill=hexrgb(c))
    # hay stacked in the right corner, a pitchfork leaning on it
    for (bx, by) in ((W - 72, 66), (W - 40, 66), (W - 56, 46), (W - 26, 46)):
        d.rectangle([bx, by, bx + 30, by + 20], fill=hexrgb("#d8b050"), outline=hexrgb("#7a5a1e"))
        for i in range(bx + 3, bx + 28, 3):
            d.line([(i, by + 2), (i + 1, by + 18)], fill=hexrgb("#b8902e"))
        d.line([(bx, by + 6), (bx + 30, by + 6)], fill=hexrgb("#8a5a2a"))
        d.line([(bx, by + 14), (bx + 30, by + 14)], fill=hexrgb("#8a5a2a"))
    d.line([(W - 84, 94), (W - 64, 40)], fill=hexrgb("#8a6a40"), width=2)
    for o in (-3, 0, 3):
        d.line([(W - 64 + o, 40), (W - 62 + o, 32)], fill=hexrgb("#b8b8b8"))
    # the straw floor
    for y in range(88, H):
        t = (y - 88) / (H - 88)
        d.line([(0, y), (W, y)], fill=hexrgb(_shade("#c49a4a", -0.25 * t)))
    for _ in range(900):
        x0, y0 = rnd.randrange(0, W), rnd.randrange(88, H)
        c = rnd.choice(["#e8c870", "#a87a30", "#f4dc90", "#8a6428"])
        d.line([(x0, y0), (x0 + rnd.choice((-3, -2, 2, 3)), y0 + rnd.choice((-1, 0, 1)))], fill=hexrgb(c))
    d.line([(0, 88), (W, 88)], fill=hexrgb("#4a301a"))
    # warm light: the sun through the door across the floor, the lantern on the beam
    over = Image.new("RGBA", (W, H))
    od = ImageDraw.Draw(over)
    od.polygon([(dx0, 88), (dx1, 88), (dx1 + 70, H), (dx0 + 40, H)], fill=(255, 210, 130, 60))
    lx = 300
    od.ellipse([lx - 70, 4, lx + 70, 90], fill=(255, 190, 90, 22))
    od.ellipse([lx - 36, 16, lx + 36, 64], fill=(255, 200, 110, 30))
    im.alpha_composite(over)
    d = ImageDraw.Draw(im)
    d.line([(lx, 13), (lx, 22)], fill=hexrgb("#2a2a2a"))
    d.rectangle([lx - 4, 22, lx + 4, 34], fill=hexrgb("#2e2a26"))
    d.rectangle([lx - 3, 24, lx + 3, 32], fill=hexrgb("#ffd070"))
    d.point([(lx, 27), (lx, 28)], fill=hexrgb("#ffffff"))
    d.polygon([(lx - 5, 22), (lx + 5, 22), (lx, 18)], fill=hexrgb("#2e2a26"))
    vignette(im, 0.5)
    return im


def v_monton():
    """The Montón: a cave mouth high in the cordillera at night. Crystal veins glow in its walls, the
    peaks stand white under the stars outside, and the gems pile up on the rock floor in the middle."""
    W, H = 480, 160
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    rnd = random.Random(47)
    for y in range(H):  # night sky
        t = y / H
        a, b = hexrgb("#0a0820"), hexrgb("#2a2050")
        d.line([(0, y), (W, y)], fill=tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3)))
    for _ in range(140):
        x0, y0 = rnd.randrange(W), rnd.randrange(0, 90)
        d.point((x0, y0), fill=hexrgb(rnd.choice(["#ffffff", "#c8d0ff", "#8a90c0", "#fff0c0"])))
    d.ellipse([352, 18, 366, 32], fill=hexrgb("#f4f0dc"))  # the moon
    d.ellipse([356, 16, 370, 30], fill=hexrgb("#141030"))
    # the cordillera, back to front, snow on the high peaks
    for k, (base, col, amp, step) in enumerate(((120, "#3e4078", 70, 44), (132, "#2c2c5a", 30, 52), (144, "#1c1c3a", 12, 70))):
        pts, x0 = [(0, H)], -10
        r2 = random.Random(80 + k)
        up = True
        while x0 < W + step:  # alternating peaks and saddles
            pts.append((x0, base - (r2.uniform(0.65, 1) if up else r2.uniform(0.15, 0.4)) * amp))
            up = not up
            x0 += r2.uniform(step * 0.4, step * 0.8)
        pts.append((W, H))
        d.polygon(pts, fill=hexrgb(col))
        lit = _shade(col, 0.18)
        for (ax_, ay_), (bx_, by_) in zip(pts[1:-2], pts[2:-1]):  # moonlit west faces
            if by_ > ay_:
                d.polygon([(ax_, ay_), (bx_, by_), (ax_ + (bx_ - ax_) * 0.35, by_)], fill=hexrgb(lit))
        if k == 0:  # snow on the high peaks, following the slopes down a little
            for (ax_, ay_), (px_, py_), (bx_, by_) in zip(pts[1:-2], pts[2:-1], pts[3:]):
                if py_ < base - amp * 0.6 and py_ < ay_ and py_ < by_:
                    dl, dr = min(0.35, 9 / max(1, ay_ - py_)), min(0.35, 9 / max(1, by_ - py_))
                    L = (px_ + (ax_ - px_) * dl, py_ + (ay_ - py_) * dl)
                    R = (px_ + (bx_ - px_) * dr, py_ + (by_ - py_) * dr)
                    d.polygon([(px_, py_), L, (L[0] + (px_ - L[0]) * 0.4, L[1] - 1), ((L[0] + R[0]) / 2, (L[1] + R[1]) / 2 + 3), (R[0] - (R[0] - px_) * 0.4, R[1] - 2), R], fill=hexrgb("#e8ecff"))
    # the cave: rock walls on both sides and a ceiling with stalactites, framing the opening
    rock, rock2, rock3 = "#2a2228", "#3a3036", "#1a1418"

    def wall(xs):
        pts = [(xs[0][0], 0)] + xs + [(xs[-1][0], H)]
        d.polygon(pts, fill=hexrgb(rock))
    left = [(0, 0), (70, 0), (60, 18), (74, 36), (58, 56), (66, 80), (48, 104), (56, 128), (40, 150), (0, H)]
    right = [(W, 0), (W - 64, 0), (W - 52, 20), (W - 70, 40), (W - 56, 64), (W - 66, 90), (W - 46, 112), (W - 58, 136), (W - 36, 152), (W, H)]
    d.polygon(left, fill=hexrgb(rock))
    d.polygon(right, fill=hexrgb(rock))
    ceil = [(0, 0), (W, 0), (W, 12)] + [(x0, 12 + 6 * math.sin(x0 / 17) + (8 if x0 % 37 < 6 else 0)) for x0 in range(W, -1, -6)]
    d.polygon(ceil, fill=hexrgb(rock))
    for x0 in range(76, W - 70, 23):  # stalactites
        l_ = rnd.randrange(6, 18)
        d.polygon([(x0 - 3, 14), (x0 + 3, 14), (x0, 14 + l_)], fill=hexrgb(rock2))
        d.point((x0, 14 + l_ + 3), fill=hexrgb("#8ab8ff"))
    for poly, sh in ((left, 1), (right, -1)):  # light edge on the rim, cracks
        for (a, b) in zip(poly[1:-2], poly[2:-1]):
            d.line([a, b], fill=hexrgb(rock2), width=2)
    for _ in range(40):
        side = rnd.random() < 0.5
        x0 = rnd.randrange(4, 50) if side else rnd.randrange(W - 48, W - 4)
        y0 = rnd.randrange(10, 150)
        d.line([(x0, y0), (x0 + rnd.randrange(-6, 7), y0 + rnd.randrange(3, 9))], fill=hexrgb(rock3))
    # crystal veins in the walls, each a cluster of points glowing
    over = Image.new("RGBA", (W, H))
    od = ImageDraw.Draw(over)
    clusters = [(22, 44, "#e03a6a"), (40, 96, "#3ad08a"), (16, 132, "#3a8aff"), (W - 26, 30, "#f0c030"), (W - 40, 80, "#b04af0"), (W - 18, 124, "#f0f0ff"), (140, 16, "#3ad0e0"), (330, 18, "#e03a6a")]
    for cx, cy, col in clusters:
        c = hexrgb(col)
        for r, a in ((16, 14), (9, 26), (5, 40)):
            od.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c[:3] + (a,))
    im.alpha_composite(over)
    d = ImageDraw.Draw(im)
    for cx, cy, col in clusters:
        down = cy < 24  # the ones in the ceiling hang down
        for k in range(5):  # hexagonal prisms fanning out of the rock: a body and a pointed tip
            ang = math.radians((60 if down else -150) + k * 15 + rnd.randrange(-5, 6))
            L_ = rnd.choice((9, 12, 15, 11, 8))
            u = (math.cos(ang), math.sin(ang))
            n = (-u[1] * 2.2, u[0] * 2.2)
            b0 = (cx, cy)
            b1 = (cx + u[0] * L_ * 0.7, cy + u[1] * L_ * 0.7)
            tip = (cx + u[0] * L_, cy + u[1] * L_)
            body = [(b0[0] + n[0], b0[1] + n[1]), (b1[0] + n[0], b1[1] + n[1]), tip, (b1[0] - n[0], b1[1] - n[1]), (b0[0] - n[0], b0[1] - n[1])]
            d.polygon(body, fill=hexrgb(_shade(col, -0.15)), outline=hexrgb(_shade(col, -0.6)))
            d.polygon([(b0[0] + n[0] * 0.2, b0[1] + n[1] * 0.2), (b1[0] + n[0] * 0.2, b1[1] + n[1] * 0.2), tip, (b1[0] + n[0] * 0.9, b1[1] + n[1] * 0.9), (b0[0] + n[0] * 0.9, b0[1] + n[1] * 0.9)], fill=hexrgb(_shade(col, 0.35)))
            d.point((round(tip[0] - u[0] * 2), round(tip[1] - u[1] * 2)), fill=hexrgb("#ffffff"))
    # the floor: a rock shelf, worn smooth where the pile sits
    floor = [(0, H)] + [(x0, 146 + 3 * math.sin(x0 / 23) + (2 if 150 < x0 < 330 else 0)) for x0 in range(0, W + 1, 8)] + [(W, H)]
    d.polygon(floor, fill=hexrgb("#241c22"))
    d.line(floor[1:-1], fill=hexrgb("#4a3e48"), width=1)
    for _ in range(30):
        x0 = rnd.randrange(W)
        y0 = 150 + rnd.randrange(0, 6)
        d.ellipse([x0, y0, x0 + rnd.randrange(3, 7), y0 + 2], fill=hexrgb("#3a3036"))
    vignette(im, 0.45)
    return im

VILLAGE = {"v-camisetas": v_collares, "v-merchant": v_merchant, "v-casetes": v_casetes, "v-sell": v_sell, "v-stash": v_stash, "v-alembic": v_alembic, "v-establo": v_establo, "v-monton": v_monton}

SCENES.update(VILLAGE)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for z in sys.argv[1:] or SCENES:
        im = SCENES[z]()
        im.save(os.path.join(OUT, f"{z}.png"))
        print(z, im.size)
    open(os.path.join(OUT, "CREDITS.txt"), "w").write(
        "Fight backdrops for Leyendas (scripts/build_scenes.py).\n\n"
        "Ground and scenery tiles (water, grass, grassalt, watergrass, dirt, dirt2, lava, lavarock, rock, trunk, treetop, castlewalls,\ncastlefloors_outside) and village props (barrel, buckets, cabinets, castle_lightsources, chests, country, kitchen, signs, victoria), tinted: LPC Base Assets by Lanea Zimmerman (Sharm),\n"
        "Liberated Pixel Cup. CC-BY-SA 3.0 / GPL 3.0 / OGA-BY 3.0.\n"
        "https://opengameart.org/content/liberated-pixel-cup-lpc-base-assets-sprites-map-tiles\n\n"
        "Skies, mountains, mist, treelines, mangroves, reeds, frailejones, moriche palms, fire, smoke, vines, leaves,\nthe stone guardians and the stalactites; in the village the houses, walls, floors, stall, card table,\nthe bohío, the lagoon, the tunjos, the woven cloth, the sombrero, balance, coins, the copper still, the tailor's room, the stable, the Montón's cave and the sets' undershirts: original, drawn in code for Leyendas.\n")
