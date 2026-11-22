"""The tunjo's rainbow items (data.js TUNJO_ITEMS): an icon drawn for each, and the worn shapes redrawn in rainbow.

Original art. Each icon is drawn on a 20x20 grid from a few shapes in three paints (rainbow, gold,
white), then outlined and shaded by the same rule for all: lighter on the edges facing up and left,
darker on the ones facing down and right. The rainbow runs across the item (or around it, for the
round shield and the amulet's halo). build_lpc.py puts the icons in the atlas as item:<look>:t:<id>
and the worn looks as item:<look>:t:<id>:<body>.

Preview: .venv/bin/python scripts/tunjo_art.py <out.png>
"""
import colorsys
import math
import sys

import numpy as np
from PIL import Image, ImageDraw

N = 20  # grid
OUTLINE = (26, 14, 36)
GOLD = [(122, 74, 20), (196, 138, 38), (242, 198, 74), (255, 240, 160)]  # dark, mid, light, shine


def _hue(x, y, mode, centre, span):
    if mode == "angle":
        a = math.atan2(y - centre[1], x - centre[0])
        return (a / (2 * math.pi)) % 1.0
    lo, hi = span  # red at one end of the item to violet at the other, whatever its size
    return 0.83 * (x + y - lo) / max(1, hi - lo)


def _rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (round(r * 255), round(g * 255), round(b * 255), 255)


# Each item: a function drawing on three masks (ImageDraw on "L" images): r rainbow, g gold, w white.
# The hue mode ("diag" or ("angle", centre)) is the second value.
def _filo(r, g, w):
    r.line([(7, 12), (18, 1)], fill=255, width=3)          # the blade
    w.line([(9, 11), (17, 3)], fill=255, width=1)          # its edge catching the light
    g.line([(3, 10), (9, 16)], fill=255, width=2)          # crossguard
    g.line([(5, 14), (2, 17)], fill=255, width=2)          # grip
    g.ellipse([0, 17, 3, 20], fill=255)                    # pommel


def _arco(r, g, w):
    r.arc([4, 1, 24, 19], 90, 270, fill=255, width=3)      # the bow, bulging left
    w.line([(14, 1), (14, 19)], fill=255, width=1)         # string
    g.line([(1, 10), (17, 10)], fill=255, width=1)         # arrow shaft
    g.polygon([(16, 7), (19, 10), (16, 13)], fill=255)     # arrowhead
    r.line([(0, 8), (2, 10), (0, 12)], fill=255, width=1)  # fletching
    g.rectangle([3, 9, 5, 11], fill=255)                   # grip


def _vara(r, g, w):
    g.line([(2, 19), (12, 8)], fill=255, width=2)          # the staff
    r.polygon([(15, 0), (19, 5), (15, 11), (11, 5)], fill=255)  # the crystal
    g.line([(10, 8), (13, 10)], fill=255, width=1)         # its setting
    w.point([(15, 3), (14, 4), (18, 12), (9, 2)], fill=255)  # glints


def _rodela(r, g, w):
    r.ellipse([1, 1, 19, 19], fill=255)
    g.ellipse([1, 1, 19, 19], outline=255, width=1)        # rim
    g.ellipse([8, 8, 12, 12], fill=255)                    # boss
    w.point([(5, 5), (6, 4)], fill=255)


def _corona(r, g, w):
    r.rectangle([2, 12, 18, 16], fill=255)                 # band
    r.polygon([(2, 12), (2, 5), (6, 10)], fill=255)        # points
    r.polygon([(6, 12), (10, 3), (14, 12)], fill=255)
    r.polygon([(14, 10), (18, 5), (18, 12)], fill=255)
    g.rectangle([2, 15, 18, 16], fill=255)                 # gold rim
    for x, y in ((2, 4), (10, 2), (18, 4)):
        g.ellipse([x - 1, y - 1, x + 1, y + 1], fill=255)  # gold balls on the tips
    w.point([(6, 14), (10, 14), (14, 14)], fill=255)       # stones in the band


def _manto(r, g, w):
    r.polygon([(6, 2), (14, 2), (19, 6), (19, 10), (16, 10), (16, 19), (4, 19), (4, 10), (1, 10), (1, 6)], fill=255)
    g.polygon([(7, 2), (10, 6), (13, 2)], fill=255)        # collar
    g.rectangle([4, 12, 16, 13], fill=255)                 # belt
    w.line([(10, 7), (10, 11)], fill=255)


def _manos(r, g, w):
    r.rectangle([4, 7, 14, 16], fill=255)                  # the back of the hand
    for x, top in ((4, 3), (7, 1), (10, 1), (13, 3)):
        r.rectangle([x, top, x + 1, 8], fill=255)  # fingers, a pixel apart
    r.polygon([(14, 10), (19, 6), (19, 9), (15, 14)], fill=255)  # thumb
    g.rectangle([3, 16, 15, 19], fill=255)                 # cuff
    w.line([(5, 4), (5, 6)], fill=255)


def _pasos(r, g, w):
    r.polygon([(5, 1), (12, 1), (12, 11), (18, 13), (18, 17), (5, 17)], fill=255)
    g.rectangle([4, 17, 19, 19], fill=255)                 # sole
    g.rectangle([5, 1, 12, 3], fill=255)                   # top cuff
    w.point([(7, 5), (7, 6)], fill=255)
    r.line([(1, 6), (4, 6)], fill=255)                     # little wings at the heel
    r.line([(2, 8), (4, 8)], fill=255)


def _faja(r, g, w):
    r.polygon([(0, 7), (6, 9), (14, 9), (20, 7), (20, 12), (14, 14), (6, 14), (0, 12)], fill=255)
    r.polygon([(9, 12), (5, 20), (8, 20), (10, 15)], fill=255)   # tails
    r.polygon([(11, 12), (15, 20), (12, 20), (10, 15)], fill=255)
    g.rectangle([8, 9, 12, 14], fill=255)                  # the knot
    w.point([(10, 11)], fill=255)


def _oyente(r, g, w):
    g.arc([2, -8, 18, 9], 20, 160, fill=255, width=1)      # chain
    r.ellipse([4, 6, 16, 19], outline=255, width=2)        # a rainbow halo
    g.ellipse([8, 8, 12, 11], fill=255)                    # the little gold figure: head
    g.rectangle([8, 11, 12, 15], fill=255)                 # body
    g.line([(7, 12), (6, 14)], fill=255)                   # arms
    g.line([(13, 12), (14, 14)], fill=255)
    g.line([(9, 15), (9, 17)], fill=255)                   # legs
    g.line([(11, 15), (11, 17)], fill=255)
    w.point([(9, 9)], fill=255)                            # its ear, listening


def _gota(r, g, w):
    g.ellipse([3, 10, 17, 19], outline=255, width=2)       # the band
    r.ellipse([6, 4, 14, 12], fill=255)                    # the drop
    r.polygon([(7, 6), (10, 0), (13, 6)], fill=255)
    w.point([(8, 6), (8, 7)], fill=255)


def _eco(r, g, w):
    r.ellipse([2, 6, 15, 19], outline=255, width=3)        # the band
    g.ellipse([6, 3, 11, 8], fill=255)                     # a small gold bead
    w.arc([12, 1, 20, 9], -60, 60, fill=255)               # the echo
    w.arc([14, -1, 22, 11], -50, 50, fill=255)


ITEMS = {
    "filo": (_filo, "diag"), "arco": (_arco, "diag"), "vara": (_vara, "diag"), "rodela": (_rodela, ("angle", (10, 10))),
    "corona": (_corona, "diag"), "manto": (_manto, "diag"), "manos": (_manos, "diag"), "pasos": (_pasos, "diag"),
    "faja": (_faja, "diag"), "oyente": (_oyente, ("angle", (10, 12.5))), "gota": (_gota, "diag"), "eco": (_eco, ("angle", (8.5, 12.5))),
}


def icon(tid, scale=2):
    draw, mode = ITEMS[tid]
    masks = {k: Image.new("L", (N + 1, N + 1)) for k in "rgw"}
    draw(*(ImageDraw.Draw(masks[k]) for k in "rgw"))
    m = {k: np.array(v) > 0 for k, v in masks.items()}
    shape = m["r"] | m["g"] | m["w"]
    H, W = shape.shape
    im = Image.new("RGBA", (W + 2, H + 2))
    px = im.load()
    inside = lambda x, y: 0 <= x < W and 0 <= y < H and shape[y, x]
    hm, centre = (mode, None) if isinstance(mode, str) else mode
    ry, rx = np.nonzero(m["r"])
    d = rx + ry
    span = (int(d.min()), int(d.max())) if len(d) else (0, 2 * N)
    if hm == "diag" and tid in ("filo", "vara"):  # these run from bottom left to top right
        d = rx - ry
        span = (int(d.min()), int(d.max()))
    for y in range(H):
        for x in range(W):
            if not shape[y, x]:
                continue
            lit = not inside(x - 1, y) or not inside(x, y - 1)
            shade = not inside(x + 1, y) or not inside(x, y + 1)
            if m["w"][y, x]:
                c = (255, 255, 255, 255)
            elif m["g"][y, x]:
                c = GOLD[3 if lit and not shade else 0 if shade and not lit else 2 if (x + y) % 5 == 0 else 1]
            else:
                h = _hue(x - y, 0, hm, centre, span) if tid in ("filo", "vara") else _hue(x, y, hm, centre, span)
                c = _rgb(h, 0.55 if lit and not shade else 0.9, 1.0 if lit and not shade else 0.62 if shade and not lit else 0.9)
            px[x + 1, y + 1] = c
    # the outline: every empty pixel touching the item
    a = np.array(im)[:, :, 3] > 0
    for y in range(H + 2):
        for x in range(W + 2):
            if a[y, x]:
                continue
            if any(0 <= x + dx < W + 2 and 0 <= y + dy < H + 2 and a[y + dy, x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                px[x, y] = OUTLINE + (255,)
    im = im.crop(im.getbbox())
    return im.resize((im.width * scale, im.height * scale), Image.NEAREST)


def rainbow(im, fs=None):
    """A worn piece redrawn in rainbow: its shading kept as brightness, the hue running across it
    (per frame of fs pixels, for the animation strips). The darkest outline stays dark."""
    a = np.array(im.convert("RGBA")).astype(np.float32)
    rgb, alpha = a[:, :, :3] / 255, a[:, :, 3]
    lum = rgb @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    H, W = lum.shape
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    if fs:
        xs, ys = xs % fs, ys % fs
    hue = ((xs + ys) / 28.0) % 1.0
    lo, hi = lum.min(where=alpha > 0, initial=1.0), lum.max(where=alpha > 0, initial=0.0)
    t = np.clip((lum - lo) / max(1e-3, hi - lo), 0, 1)
    v = 0.3 + 0.7 * t
    s = 0.9 - 0.45 * np.clip((t - 0.75) / 0.25, 0, 1)   # the brightest bits wash toward white
    i = np.floor(hue * 6).astype(int) % 6
    f = hue * 6 - np.floor(hue * 6)
    p, q, u = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    r = np.choose(i, [v, q, p, p, u, v]); g = np.choose(i, [u, v, v, q, p, p]); b = np.choose(i, [p, p, u, v, v, q])
    out = np.stack([r, g, b], -1) * 255
    dark = lum < 0.13                                     # outlines
    out[dark] = np.array(OUTLINE, dtype=np.float32)
    res = np.concatenate([out, alpha[:, :, None]], -1).clip(0, 255).astype(np.uint8)
    return Image.fromarray(res, "RGBA")


if __name__ == "__main__":
    ims = [icon(t, 4) for t in ITEMS]
    W = sum(i.width + 16 for i in ims) + 16
    sheet = Image.new("RGBA", (W, max(i.height for i in ims) + 32), (40, 32, 26, 255))
    x = 16
    for im in ims:
        sheet.alpha_composite(im, (x, 16))
        x += im.width + 16
    sheet.save(sys.argv[1] if len(sys.argv) > 1 else "tunjo_icons.png")
