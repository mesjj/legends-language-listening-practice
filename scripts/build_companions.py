"""Pets and mounts: one standing frame each, facing east like the hero, in their coat colours.

Pets: the shiba from "[LPC] bears, deer, lions and more" (Sevarihk), recoloured into five coats.
Mounts: bluecarrot16's "[LPC] Horses", which already come in five colours.
Writes public/rpg/lpc/companions/{pet,mount}-<id>.png (trimmed, native size; the game scales them
like the hero) and public/rpg/lpc/CREDITS-companions.txt, which must ship with the game.

usage: .venv/bin/python scripts/build_companions.py   (downloads are cached in .lpc-cache/oga)"""
import colorsys, io, os, sys, urllib.request, zipfile
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, ".lpc-cache", "oga")
OUT = os.path.join(ROOT, "public", "rpg", "lpc", "companions")
OGA = "https://opengameart.org/sites/default/files/"


def fetch(name):
    path = os.path.join(CACHE, name)
    if not os.path.exists(path):
        os.makedirs(CACHE, exist_ok=True)
        req = urllib.request.Request(OGA + name, headers={"User-Agent": "Mozilla/5.0 (leyendas build script)"})
        open(path, "wb").write(urllib.request.urlopen(req, timeout=60).read())
    return path


def coat(im, hue=0.0, sat=1.0, light=1.0, lift=0.0):
    """Recolour the fur: hue shift (degrees), saturation and lightness factors, lift toward white."""
    im = im.copy()
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if not a:
                continue
            h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
            if l < 0.16:  # outline and eyes stay dark
                continue
            h = (h + hue / 360) % 1
            s = min(1, s * sat)
            l = min(1, l * light + lift * (1 - l))
            r2, g2, b2 = colorsys.hls_to_rgb(h, l, s)
            px[x, y] = (round(r2 * 255), round(g2 * 255), round(b2 * 255), a)
    return im


def trim(im):
    return im.crop(im.getbbox())


# the dog: 48px frames, the third row walks east; its first frame is a calm stance
z = zipfile.ZipFile(os.path.join(CACHE, "lpc_animals_2022_v1.1.zip"))
dog = Image.open(io.BytesIO(z.read("lpc animals 2022 v1.1/individual creature spritesheets/dog, shiba (Sevarihk).png"))).convert("RGBA")
dog = dog.crop((0, 96, 48, 144))
PETS = {
    "canela": dict(),                                     # the shiba's own red-gold
    "azabache": dict(sat=0.06, light=0.33),               # black
    "copito": dict(sat=0.08, light=1.0, lift=0.75),       # white
    "humo": dict(sat=0.05, light=0.85),                   # grey
    "cacao": dict(hue=-8, sat=0.75, light=0.55),          # chocolate
}
# the horses: 128px frames; the ninth row stands still in four directions, the fourth faces east
MOUNTS = {"noche": "black", "castano": "brown", "palomino": "golden", "tordo": "gray", "lucero": "white"}

os.makedirs(OUT, exist_ok=True)
for pid, k in PETS.items():
    trim(coat(dog, **k) if k else dog).save(os.path.join(OUT, f"pet-{pid}.png"), optimize=True)
for mid, colour in MOUNTS.items():
    sheet = Image.open(fetch(f"horse-{colour}_0.png")).convert("RGBA")
    trim(sheet.crop((384, 1024, 512, 1152))).save(os.path.join(OUT, f"mount-{mid}.png"), optimize=True)

open(os.path.join(ROOT, "public", "rpg", "lpc", "CREDITS-companions.txt"), "w").write(
    "Pets and mounts in Leyendas (public/rpg/lpc/companions/)\n\n"
    "pet-*.png: the shiba from \"[LPC] bears, deer, lions and more\" by tapatilorenzo, bluecarrot16, Sevarihk (dog: Sevarihk),\n"
    "  CC-BY 4.0, https://opengameart.org/content/lpc-bears-deer-lions-and-more. One frame, recoloured into five coats.\n"
    "mount-*.png: \"[LPC] Horses\" by bluecarrot16, CC-BY 3.0 / GPL 3.0 / GPL 2.0 / OGA-BY 3.0,\n"
    "  https://opengameart.org/content/lpc-horses (in the style of daneeklu's LPC farm animals). One standing frame of each colour.\n")
print("pets:", ", ".join(PETS), "| mounts:", ", ".join(MOUNTS))
