"""Original pixel art for the three top-tier sets, drawn in code (no outside files).

Icons: one character grid per piece, hand-placed pixels, a palette per set.
Ornaments: what the character wears around them when a piece of the set is on, painted
procedurally per animation frame so it moves (wings beat, ripples spread, motes orbit).

Used by build_lpc.py: custom_icons() -> {"item:<base>:<setid>": Image},
custom_looks() -> [(key, atlas_layers, anim_layers)] with key "orn:<setid>:<part|full>".
"""
import math

from PIL import Image, ImageDraw

F = 64  # frame size; the body stands at x 17-47, y 13-62, centre x 32

# ---------- the grid painter ----------
def hexrgb(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def paint(grid, pal):
    """A multi-line string into an RGBA image. '.' and ' ' are transparent; rows are padded."""
    rows = [r for r in grid.strip("\n").split("\n")]
    w = max(len(r) for r in rows)
    im = Image.new("RGBA", (w, len(rows)))
    px = im.load()
    for y, r in enumerate(rows):
        for x, ch in enumerate(r.ljust(w)):
            if ch in ". ":
                continue
            if ch not in pal:
                raise KeyError(f"no colour for {ch!r} in row {y}")
            px[x, y] = hexrgb(pal[ch])
    return im


def mirror(grid):
    """Half a symmetric picture (its left half, incl. the centre column) -> the whole."""
    rows = grid.strip("\n").split("\n")
    w = max(len(r) for r in rows)
    out = []
    for r in rows:
        r = r.ljust(w)
        out.append(r + r[-2::-1])
    return "\n".join(out)


# ---------- palettes ----------
# Gesta del Cóndor (legendario): black plumage, white ruff, crimson, a gold beak
CONDOR = {
    "o": "#1a0a0e",  # outline
    "k": "#2b2733", "K": "#443f4e", "L": "#6a6378",  # plumage dark / mid / light
    "w": "#f4f0e7", "W": "#cdc6b8", "v": "#a8a093",  # white ruff light / shade / deep
    "r": "#ff5a4a", "R": "#b2302a", "p": "#ffb0a4",  # crimson / dark / highlight
    "g": "#e8b93d", "G": "#9d7322", "y": "#fff0b0",  # gold / dark / shine
}
# La Voz del Origen (mítico): obsidian, pale stone, cyan light
ORIGEN = {
    "o": "#07171c",
    "k": "#1a2a33", "K": "#2d4553", "L": "#4a6d7d",  # obsidian dark / mid / light
    "w": "#eaf6f7", "W": "#b9d4d9", "v": "#8fb0b8",  # pale stone light / shade / deep
    "c": "#6fe6ff", "C": "#2a9fbb", "h": "#dffbff",  # cyan / dark / highlight
    "n": "#0d3340",  # deep cyan shadow
    "g": "#e8b93d", "G": "#9d7322",  # a little gold (the amulet's bail)
}

# ---------- Gesta del Cóndor ----------
# Yelmo del Cóndor: a black helm, the condor's head as its crest, the beak hooked over the brow,
# a crimson band and the white ruff at the neck.
YELMO = mirror("""
..........o
.........ok
........okK
.......okKk
.......okkk
........okk
.........og
..........o
......ooooo
....ookkKKK
...okkKKkkk
..okkKkkkkk
..okKkkkkkk
.okKkkkrrrr
.okkkkkRrRR
.okkkkkoooo
.okkkoo....
.okkko.....
.okkko.....
.okkkoo....
..okkkoo...
..oWwwwwooo
.oWwwwwwwww
.oWWwwwwWWW
..oWWWWWooo
...ooooo...
""")
# the beak: gold, hooked to one side, drawn over the mirrored head
YELMO_OVER = """
...........
...........
...........
...........
.........gg
.........Gg
..........G
"""

# Alas del Cóndor: a breastplate with the wings spread across the chest, the ruff as the collar.
CORAZA = mirror("""
.....ooWwww
....oWwwwWW
...oWwWWvvo
..okWvookkk
.okKkoKkkkk
.okKkKkkkkk
okKkkKkkkrr
okKkrkKkkRr
okKkrrkKkkR
.okkRrrkKkk
.okkkRrrkKk
..okkkRrrkK
..okkkkRrrk
...okkkkRrk
...ookkkkRk
....ookkkkk
.....ookkkk
......ookkk
.......oooo
""")

# Garra del Cóndor: a greatsword whose blade curves like a talon (the tip hooks back), black
# with a crimson edge, white feathers for a guard, a gold pommel.
ESPADON = """
....................oooo......
..................ooKKkoo.....
.................oKkkkkKko....
................oKkpoookKko...
................oKpo...oKko...
...............oKpo....okko...
...............oKpro...oko....
..............oKpro....oo.....
..............oKpro...........
.............oKprro...........
.............oKprro...........
............oKprro............
............oKprro............
...........oKprro.............
...........oKprro.............
..........oKprro..............
..........oKprro..............
.........oKprro...............
.........oKprro...............
........oKprro................
........oKprro................
.......oKprro.................
......ooKprroo................
....ooWwKrrowWoo..............
...oWwwWkRkWwwwWo.............
..oWwWooKKkooWwWo.............
..oWWo.oKKko.oWWo.............
...oo..okKko..oo..............
.......okKko..................
.......okKko..................
.......okKko..................
.......oGggo..................
......oGgyggo.................
.......oGGGo..................
"""

# Guanteletes del Cóndor: one gauntlet seen from the back: the cuff, a crimson stone on the hand,
# four plated fingers and a thumb, every finger ending in a gold talon.
GUANTELETES = """
...oooooooooo....
..oKKkkkkkkKKo...
..oKkkkkkkkkKo...
..oLLLLLLLLLLo...
...okkkkkkkko....
...okKkrrkKkoo...
...okKkRRkKkoKo..
...okkkkkkkkokKo.
..ookkkkkkkkokko.
.okKokKokKokKoko.
.okkokkokkokkokko
.okkokkokkokkoGgo
.ogGogGogGogGooyo
.oGyoGyoGyoGyo.o.
..oo.oo.oo.oo....
"""

# Grebas del Cóndor: a greave of overlapping feather plates, the knee in crimson, white at the foot.
GREBAS = mirror("""
....oooo
...oKLLL
..okKLkk
..okLrrr
..okKRrr
..okkRRR
..okLkkk
..okkLkk
..okkkLk
..okLkkk
..okkLkk
..okkkLk
..okLkkk
..okkLkk
..okkkLk
..okLkkk
..okkLkk
..oWwwww
..oWWwww
...ooooo
""")

# ---------- La Voz del Origen ----------
# Corona del Primer Sonido: pale stone, three arcs rising like a sound spreading, a spiral stone.
CORONA = mirror("""
.............o
............oc
...........ohc
...........ocC
......o....ocC
.....oc...oocC
....ohc...ocwW
....ocC..ocwwW
...oocC.ocwwkc
...ocwWoocwkch
...ocwwwwwwkcC
...ocwwwwwwkkC
...oCwWWWWwwwW
...oCWWWWWWWWW
....oCCCCCCCCC
.....ooooooooo
""")

# Arco del Eco Eterno: a longbow of pale bone, rings of cyan along the limbs, echo arcs at the grip.
ARCO = """
..............oo..........
.............owWo.........
............owwWo.........
...........owwWo..........
...........ocCo...........
..........owwWo...........
..........owwWo...........
.........owwWo............
.........ocCo.............
.........owwWo............
........owwWo.............
........owwWo.............
........ocCo..............
........owwWo.............
........okKko..h..........
........okKko.hc..........
........okKkohch..........
........okKko.hc..........
........okKko..h..........
........owwWo.............
........ocCo..............
........owwWo.............
........owwWo.............
.........owwWo............
.........ocCo.............
.........owwWo............
..........owwWo...........
..........owwWo...........
...........ocCo...........
...........owwWo..........
............owwWo.........
.............owWo.........
..............oo..........
"""
# the string, one pixel of cyan down the right, drawn over
ARCO_STRING = ("c", (15, 1), (15, 31))

# Túnica del Silencio Roto: a dark robe, split by a crack of light down the front.
TUNICA = mirror("""
.......ooWw
......oWwww
.....oWwkkk
....okWkkKk
...okkKkkKk
..okkKkkKkk
..okkKkkKkk
.okkKkkkKkk
.okkKkkkKkk
.okkkkkkKkk
.ookkkkkKkk
..okkkkkKkk
..okkkkkKkk
..okkkkkKkk
..okkkkkKkk
..okkkkkKkk
..okkkkkkKk
..okkkkkkKk
..okkkkkkKk
..okkkkkkKk
..okkkkkkkK
..oKKKKKKKK
...ooooooooo
""")
TUNICA_CRACK = """
......................
......................
......................
......................
......................
......................
..........h...........
..........hc..........
..........ch..........
...........h..........
..........hc..........
..........h...........
...........hc.........
...........ch.........
...........h..........
............hc........
...........ch.........
...........h..........
............c.........
............h.........
"""

# Sortija de la Voz Primera: an obsidian band, the stone a spiral of cyan.
SORTIJA = """
......oooooo......
....oochhccoo.....
...ochcCCCchco....
..ochCcnnnCchco...
..ocCcnhhhnCcCo...
.ochCnhcccnChco...
.ocCnhccCcnCcCo...
.ocCnhcCchnCcCo...
.ocCnhcccchCcCo...
.ochCnhhhhnChco...
..ocCCnnnnCcCo....
..okcCCCCCCckKo...
...okKcCCCckKo....
...okKkkkkkkKo....
....okKKkkKKo.....
.....okkkkko......
......oooooo......
"""

# Botas de Antes de la Palabra: a travelling boot, a ripple of light spreading from the sole.
BOTAS = """
........ooooo.........
.......okKKKko........
.......okKkkko........
.......okKkkko........
.......okKkkko........
.......okkkkko........
.......okkkkkoo.......
......ookkkkkkkoo.....
.....okkkkkkkkkkko....
....okKkkkkkkkkkkko...
...okKkkkkkkkkkkkkko..
...okkkkkkkkkkkkkkko..
...oKKKKKKKKKKKKKKKo..
...oCcCcCcCcCcCcCcCo..
....ooooooooooooooo...
..h..c..h..c..h..c..h.
.c....h....c....h....c
"""

# Pectoral del Origen: a disc of pale stone on a cord, a spiral of cyan cut into it.
AMULETO = """
o...............o
oK.............Ko
.oK...........Ko.
..oK.........Ko..
...oK.......Ko...
....oK.....Ko....
.....oK...Ko.....
......oKoKo......
.......oGo.......
......ooooo......
....ooWwwwWoo....
...oWwwwwwwwWo...
..oWwwCCCCCwwWo..
..oWwCchhhhCwWo..
.oWwCchcccchCwWo.
.oWwCchcCCchCwWo.
.oWwCchcChchCwWo.
.oWwCchccnhhCwWo.
.oWwCchhhhhCCwWo.
..oWwCCCCCCCwWo..
..oWwwwwwwwwwWo..
...oWWwwwwwWWo...
....ooWWWWWoo....
......ooooo......
"""


# ---------- Ofrendas de la Laguna (ancestral) ----------
# The Muisca offerings thrown into the lake: hammered gold and rose tumbaga, lake-green water,
# a ruana of dark wool. Palette: the ancestral pink lives in the tumbaga.
LAGUNA = {
    "o": "#2a1408",
    "g": "#e8b93d", "G": "#9d7322", "y": "#fff0b0",  # gold / dark / shine
    "p": "#e0679e", "P": "#9c3a68", "q": "#f7b3cf",  # rose tumbaga / dark / highlight
    "b": "#2f8f8a", "B": "#1c5459", "h": "#9fe3d6",  # lake water / deep / glint
    "k": "#3b2a3a", "K": "#5a4155",  # wool dark / light
}

# Máscara de la Laguna: a hammered gold face, slit eyes, ear spools of rose tumbaga, a crescent
# nose ring (nariguera) hanging over the mouth.
MASCARA_L = mirror("""
.....ooooooo
...ooyyggggg
..oyyggggggg
..oygggggggg
..ogggGGGggg
.ooyggggggGg
oqpoggoooogG
oPqPoggggggG
oPpPogggggyG
.oPoggggggyG
..oogggggGyG
...oggggGooG
...oggggoqpp
...ogggopPPP
...oGggoqPPP
....oGggoooo
....oGgGGooo
.....oGggggg
.....oGGgggg
......ooGGGG
........oooo
""")

# Pectoral de la Laguna: a gold plate on a cord, two lake stones set in it, and little plates
# dangling from its lower edge that would ring against each other.
PECTORAL_L = mirror("""
o........
oG.......
.oG......
..oG.....
...oG....
....oG...
.....oG..
......oGo
.......oq
..ooooooo
.oyyggggg
.oygGGGgg
.oyGbbbGg
.ogGbhbGg
.ogGBbbGg
.oggGGGgp
.ogggggpP
.ogGgggGg
..ogggggg
..oGGGGGG
..oo.oo.o
..oq.op.o
..op.og.o
..oP.oG.o
...o..o..
""")

# Manto de la Laguna: a ruana of dark wool with bands of gold and rose diamonds, the lake's
# ripples woven in green, a gold fringe.
RUANA_L = mirror("""
.......ooo..
.....ookkko.
....okkkkKo.
...okkkkkKKo
..okkkkkkkKo
.okkkkkkkkkK
okkkkkkkkkkk
okgGgGgGgGgG
okpkqkpkqkpk
okgGgGgGgGgG
okkkkkkkkkkk
okkbkkkbkkkb
okbkbkbkbkbk
okkkkkkkkkkk
okkBkkkBkkkB
okBkBkBkBkBk
okkkkkkkkkkk
okgGgGgGgGgG
okkkkkkkkkkk
oooooooooooo
.y.y.y.y.y.y
.G.G.G.G.G.G
""")

# Brazaletes de la Laguna: a pair of gold cuffs, ripples of the lake hammered round them.
BRAZAL_L = """
...oooooooo...
..oyyyyyyyyGo.
.oyggggggggGGo
.oybbhbbhbbbGo
.ogbBbbBbbBbGo
.ogggggggggGGo
.oqqpqqpqqpPGo
.ogggggggggGGo
.ogbbhbbhbbbGo
.ogBbbBbbBbbGo
.oGgggggggggGo
..oGGGGGGGGGo.
...ooooooooo..
"""

ICONS = {
    "condor": {"yelmo": (YELMO, YELMO_OVER), "coraza": CORAZA, "espadon": ESPADON, "guanteletes": GUANTELETES, "grebas": GREBAS},
    "laguna": {"mascara": MASCARA_L, "amuleto": PECTORAL_L, "ruana": RUANA_L, "brazales": BRAZAL_L, "arco": ARCO},
    "origen": {"corona": CORONA, "arcolargo": ARCO, "tunica": (TUNICA, TUNICA_CRACK), "sortija": SORTIJA, "botasviaje": BOTAS, "amuleto": AMULETO},
}
PAL = {"condor": CONDOR, "origen": ORIGEN, "laguna": LAGUNA}
# Arco de la Ofrenda: the Origen's bow drawing in the lake's colours: gold limbs, rose tumbaga
# rings, a grip wrapped in dark wool, a lake-water glint and string.
LAGUNA_BOW = {"o": LAGUNA["o"], "w": LAGUNA["g"], "W": LAGUNA["G"], "c": LAGUNA["p"], "C": LAGUNA["P"],
              "k": LAGUNA["k"], "K": LAGUNA["K"], "h": LAGUNA["h"]}


# ---------- El Tejido de la Sierra (legendario) ----------
# Mochila del Pensamiento: an Arhuaco mochila, natural wool woven in bands of zigzags and rhombuses,
# a long strap looping over the top. The figure wears it across the body (MOCHILA_WORN).
ARHUACO = {
    "o": "#1a0e08",  # outline
    "k": "#2e2016", "b": "#4a3020", "m": "#7a5636",  # dark wool / brown / mid brown
    "l": "#b8986c", "w": "#e8dcc2", "W": "#fbf5e8",  # beige / cream / highlight
}
MOCHILA = mirror("""
.....oooo
....ommmm
...om....
...om....
..om.....
..om.....
.oooooooo
okkkkkkkk
owWwwwwww
okwwwwwwk
owwwwwwkl
owkwwwklk
owwwwwwkl
okwwwwwwk
ommmmmmmm
omlmlmlml
ommmmmmmm
owwkwwwkw
owkwkwkwk
okwwwkwww
owwwwwwww
okkkkkkkk
obbbbbbbb
.obbbbbbb
..ooooooo
""")
# worn: the strap from the left shoulder down across the chest, the bag at the right hip
MOCHILA_WORN = """
.........................ob
........................ob.
.......................ob..
......................ob...
.....................ob....
....................ob.....
...................ob......
..................ob.......
.................ob........
................ob.........
...............ob..........
..............ob...........
.............ob............
............ob.............
...........oooooooo........
...........okkkkkko........
...........owkwwkwo........
...........okwbbwko........
...........owkwwkwo........
...........ommmmmmo........
...........owlwlwlo........
...........okkkkkko........
............oooooo.........
"""
def custom_icons():
    out = {}
    for sid, pieces in ICONS.items():
        for base, art in pieces.items():
            if isinstance(art, tuple):
                im = paint(art[0], PAL[sid])
                over = paint(art[1], PAL[sid])
                # the overlay is drawn from the top-left, over the mirrored picture
                im.alpha_composite(over.crop((0, 0, min(over.width, im.width), min(over.height, im.height))))
            elif base == "brazales":
                # the pair: one cuff behind and to the right of the other
                one = paint(art, PAL[sid])
                im = Image.new("RGBA", (one.width + 7, one.height + 5))
                im.alpha_composite(one, (7, 0))
                im.alpha_composite(one, (0, 5))
            else:
                im = paint(art, LAGUNA_BOW if art is ARCO and sid == "laguna" else PAL[sid])
            if art is ARCO:
                d = ImageDraw.Draw(im)
                ch, a, b = ARCO_STRING
                d.line([a, b], fill=hexrgb(LAGUNA["b"] if sid == "laguna" else PAL[sid][ch]))
            out[f"item:{base}:{sid}"] = im.crop(im.getbbox())
    # Ira del Protector: the diadem of five skulls on a maroon band with a dark iron rim
    im = paint(DIADEM, {"o": "#140a08", "w": "#efe8d6", "W": "#b8ad94", "k": "#2a1a14", "m": "#7a1e22", "M": "#4a1014",
                        "i": "#5a5a66", "I": "#8a8a98", "f": "#ff8a1a", "F": "#ffd86a"})
    out["item:cascobarbaro:guardian"] = im.crop(im.getbbox())
    im = paint(MOCHILA, ARHUACO)
    out["item:cintocatatumbo:arhuaco"] = im.crop(im.getbbox())
    return out


DIADEM = """
....f......f......f......f......f....
...fFf....fFf....fFf....fFf....fFf...
..owwwo..owwwo..owwwo..owwwo..owwwo..
..wkwkw..wkwkw..wkwkw..wkwkw..wkwkw..
..owwWo..owwWo..owwWo..owwWo..owwWo..
...wkw....wkw....wkw....wkw....wkw...
...www....www....www....www....www...
ooooooooooooooooooooooooooooooooooooo
oIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIo
ommmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmo
omMmmMmmMmmMmmMmmMmmMmmMmmMmmMmmMmmMo
ommmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmo
oiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiio
.ooooooooooooooooooooooooooooooooooo.
"""


# ---------- ornaments ----------
# Drawn on a 64px frame around the LPC body. Two layers each: one behind the body (z 4, under
# the cape backgrounds at 5) and one in front (z 150, over hats and weapons).
def ornament(sid, full, phase):
    back = Image.new("RGBA", (F, F))
    front = Image.new("RGBA", (F, F))
    {"condor": condor_wings, "laguna": laguna_offering, "origen": origen_voice,
     "cienaga": cienaga_mire, "mohan": mohan_river, "yogui": yogui_flags, "vajra": vajra_lotus,
     "averno": averno_fire, "trueno": trueno_storm, "sol": sol_disk, "guardian": guardian_aureole,
     "bachue": bachue_serpent, "nevado": nevado_frost, "vientos": vientos_whirl, "montana": montana_quake,
     "kalachakra": kalachakra_wheel, "luzclara": luzclara_rainbow,
     "osario": osario_dance, "tairona": tairona_terraces, "dorado": dorado_discs, "relampago": relampago_crown,
     "vigilia": vigilia_moon, "pacto": pacto_shadow, "firmamento": firmamento_stars, "madreagua": madreagua_river, "caiman": caiman_swamp, "andes": andes_peaks, "arhuaco": arhuaco_weave,
     "galeon": galeon_wreck, "frailejon": frailejon_mist, "bochica": bochica_falls, "bufeo": bufeo_river, "llanero": llanero_plains, "madremonte": madremonte_leaves, "silbon": silbon_whistle, "tunda": tunda_mangrove, "mahamudra": mahamudra_sky, "candileja": candileja_fire, "sombreron": sombreron_hat, "marimba": marimba_waves, "huitaca": huitaca_dance, "canocristales": canocristales_river, "dzogchen": dzogchen_thigle}[sid](back, front, full, phase)
    return [(4, back), (150, front)]


# ---------- the second eight sets ----------
def put(im, x, y, col):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < F and 0 <= y < F:
        im.putpixel((x, y), col)


def blob(im, x, y, r, col):
    """A small round dot, r 0 (a pixel) to 2."""
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r + (1 if r else 0):
                put(im, x + dx, y + dy, col)


def cienaga_mire(back, front, full, phase):
    """A murky pool at the feet, bubbles rising and popping; with the whole set, marsh lights drift round."""
    d, df = ImageDraw.Draw(back), ImageDraw.Draw(front)
    w = 15 if full else 11
    box = [32 - w, 57, 32 + w, 63]
    d.ellipse(box, fill=hexrgb("#1d2a12", 210), outline=hexrgb("#4d6b22", 230))
    df.arc(box, 10, 170, fill=hexrgb("#4d6b22", 230))
    for i in range(5 if full else 3):
        t = (phase + i / (5 if full else 3)) % 1
        x = 32 + ((i * 7) % 13 - 6) * (w / 8)
        y = 60 - t * (18 if full else 12)
        col = hexrgb("#a8d45a" if t < 0.85 else "#e6ffb0", int(255 * (1 - t * 0.6)))
        (front if i % 2 else back).putpixel((int(x), int(y)), col)
        if t < 0.6:
            put(front if i % 2 else back, x + 1, y, hexrgb("#6f9a2e", 180))
    if full:
        for i in range(3):
            a = phase * 2 * math.pi + i * 2.1
            x, y = 32 + math.cos(a) * 18, 30 + math.sin(a * 2) * 8 + i * 5
            near = math.sin(a) > 0
            blob(front if near else back, x, y, 1, hexrgb("#d8ff7a", 110))
            put(front if near else back, x, y, hexrgb("#f6ffd6", 255))


def mohan_river(back, front, full, phase):
    """River water running at the feet, ripples and a fish that leaps out and back in."""
    d, df = ImageDraw.Draw(back), ImageDraw.Draw(front)
    w = 16 if full else 12
    d.ellipse([32 - w, 57, 32 + w, 63], fill=hexrgb("#14485a", 200), outline=hexrgb("#3c8fa6", 230))
    df.arc([32 - w, 57, 32 + w, 63], 10, 170, fill=hexrgb("#3c8fa6", 230))
    for i in range(4):  # current lines sliding past
        t = (phase + i / 4) % 1
        x = 32 - w + 2 + t * (2 * w - 4)
        put(back, x, 59 + (i % 2) * 2, hexrgb("#9fe0f0", 230))
        put(back, x + 1, 59 + (i % 2) * 2, hexrgb("#9fe0f0", 150))
    fish = [(0, 0), (1, 0), (2, 0), (1, -1), (-1, 1), (-1, -1)]  # body, tail
    for k in range(2 if full else 1):
        t = (phase + k * 0.5) % 1
        side = -1 if k else 1
        x = 32 + side * (6 + t * 12)
        y = 60 - math.sin(t * math.pi) * (14 if full else 10)
        layer = front if k == 0 else back
        for dx, dy in fish:
            put(layer, x + side * dx, y + dy, hexrgb("#c9d6d8" if dx >= 0 else "#7d9aa0", 255))
        if 0.05 < t < 0.95:
            put(layer, x - side * 3, y + 2, hexrgb("#9fe0f0", 160))  # a drop


FLAG_COLOURS = ["#2f6fd0", "#f2f2ee", "#d83a2a", "#2f9a4a", "#f2c12e"]  # sky, wind, fire, water, earth


def yogui_flags(back, front, full, phase):
    """Inner heat: warm breath rising off the shoulders like steam in the cold. With the whole set,
    a string of prayer flags in the five colours, arched behind the head, fluttering."""
    for i in range(4 if full else 3):
        t = (phase + i / 4) % 1
        side = -1 if i % 2 else 1
        x = 32 + side * (9 + t * 3) + math.sin((t + i) * 6) * 1.2
        y = 30 - t * 20
        a = int(200 * (1 - t))
        blob(back, x, y, 1 if t < 0.5 else 0, hexrgb("#f4f1ea", a))
    if full:
        n = 9
        pts = []
        for i in range(n):
            u = i / (n - 1)
            x = 32 - 20 + u * 40
            y = 9 + (2 * u - 1) ** 2 * 11
            pts.append((x, y))
        ImageDraw.Draw(back).line(pts, fill=hexrgb("#8a7a5a", 220))
        for i, (x, y) in enumerate(pts[:-1]):
            col = hexrgb(FLAG_COLOURS[i % 5])
            sway = math.sin(phase * 2 * math.pi + i) * 0.8
            for dy in range(1, 5):
                for dx in range(0, 3):
                    put(back, x + dx + sway * (dy / 4), y + dy, col)
            put(back, x + 1 + sway, y + 2, hexrgb("#2b2733", 160))  # a mark printed on it


def vajra_lotus(back, front, full, phase):
    """A lotus opening at the feet. With the whole set, a halo of five lights behind, turning slowly."""
    d, df = ImageDraw.Draw(back), ImageDraw.Draw(front)
    petals = 6 if full else 4
    for i in range(petals):
        a = math.pi + (i + 0.5) * math.pi / petals
        x, y = 32 + math.cos(a) * 10, 61 + math.sin(a) * 3
        layer = df if i in (0, petals - 1) else d
        layer.ellipse([x - 3, y - 2, x + 3, y + 1], fill=hexrgb("#f2a6c0"), outline=hexrgb("#b2557a"))
    d.ellipse([28, 58, 36, 62], fill=hexrgb("#f7d36a"), outline=hexrgb("#b88a2a"))
    if full:
        hx, hy = 32, 22
        for k, col in enumerate(["#2f6fd0", "#f2f2ee", "#f2c12e", "#d83a2a", "#2f9a4a"]):
            r = 16 - k * 1.6
            d.arc([hx - r, hy - r, hx + r, hy + r], 190, 350, fill=hexrgb(col, 230))
        for i in range(10):  # rays turning round it
            a = math.pi * (1.1 + 0.8 * ((i / 10 + phase / 4) % 1))
            put(back, hx + math.cos(a) * 18, hy + math.sin(a) * 18, hexrgb("#fff4cf", 230))
    else:
        r = 13
        d.arc([32 - r, 22 - r, 32 + r, 22 + r], 200, 340, fill=hexrgb("#f2c12e", 150))


def flame(im, x, base_y, h, t, cols=("#7a0e08", "#e0401a", "#ff9a2a", "#ffe38a")):
    """One tongue of fire, h tall, wavering with t."""
    for k in range(h):
        u = k / max(1, h - 1)
        w = max(0, round((1 - u) * 2.2))
        sway = math.sin(t * 2 * math.pi + k * 0.7) * u * 1.4
        for dx in range(-w, w + 1):
            c = cols[min(3, int((1 - abs(dx) / (w + 1)) * 2 + (1 - u) * 1.6))]
            put(im, x + dx + sway, base_y - k, hexrgb(c, 255 if u < 0.85 else 170))


def averno_fire(back, front, full, phase):
    """Flames licking up round the feet, embers rising; the whole set burns a ring on the ground and the fire climbs higher."""
    d = ImageDraw.Draw(back)
    if full:
        d.ellipse([12, 57, 52, 63], outline=hexrgb("#ff5a1a", 220))
        d.ellipse([14, 58, 50, 62], outline=hexrgb("#7a0e08", 200))
    xs = [18, 24, 40, 46] + ([14, 50, 29, 35] if full else [])
    for i, x in enumerate(xs):
        h = (9 if full else 6) + (i * 3) % 5 + round(math.sin(phase * 2 * math.pi + i) * 2)
        flame(front if x in (24, 40, 29, 35) else back, x, 62, h, phase + i * 0.3)
    for i in range(6 if full else 3):
        t = (phase + i / 6) % 1
        x = 32 + math.sin(i * 2.3) * 16 + math.sin(t * 6 + i) * 1.5
        put(front if i % 2 else back, x, 58 - t * 46, hexrgb("#ffb347" if i % 3 else "#ff5a1a", int(255 * (1 - t))))


def trueno_storm(back, front, full, phase):
    """Sparks crackling round the body. With the whole set, a storm cloud overhead with rain, and a bolt now and then."""
    f = int(phase * 8)
    for i in range(5 if full else 3):  # little arcs that jump about
        a = (i * 2.4 + f * 1.7) % (2 * math.pi)
        x0, y0 = 32 + math.cos(a) * 15, 40 + math.sin(a) * 12
        layer = front if (i + f) % 2 else back
        x, y = x0, y0
        for k in range(7):
            nx, ny = x + (1 if (k + i + f) % 3 else -1), y + (1 if k % 2 else 0)
            put(layer, nx, ny, hexrgb("#fffbd0", 255))
            put(layer, nx + 1, ny, hexrgb("#7fc4ff", 200))
            x, y = nx, ny
        blob(layer, x0, y0, 1, hexrgb("#bfe4ff", 120))
    if full:
        d = ImageDraw.Draw(back)
        for cx, r in ((24, 5), (31, 7), (39, 6), (45, 4)):
            d.ellipse([cx - r, 2, cx + r, 2 + r * 1.3], fill=hexrgb("#3a4258"), outline=hexrgb("#252a3a"))
        for i in range(6):  # rain
            t = (phase * 2 + i / 6) % 1
            x = 22 + i * 4.5
            put(back, x, 11 + t * 10, hexrgb("#8fb8e8", int(220 * (1 - t))))
        if f in (2, 5):  # the bolt
            pts = [(36, 9), (33, 15), (37, 15), (31, 24)]
            ImageDraw.Draw(back).line(pts, fill=hexrgb("#fffbd0"), width=1)


def sol_disk(back, front, full, phase):
    """The sun behind the head; the whole set adds long turning rays and warm light at the feet."""
    d = ImageDraw.Draw(back)
    hx, hy = 32, 20
    r = 17 if full else 13
    d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=hexrgb("#ffcf3a", 120 if full else 90), outline=hexrgb("#ffb21a", 230))
    d.ellipse([hx - r + 2, hy - r + 2, hx + r - 2, hy + r - 2], outline=hexrgb("#fff1b0", 170))
    n = 12 if full else 8
    for i in range(n):
        a = 2 * math.pi * (i / n + phase / (n if full else 2 * n))
        long_ = (i % 2 == 0) and full
        for k in range(r + 1, r + (7 if long_ else 4)):
            put(back, hx + math.cos(a) * k, hy + math.sin(a) * k, hexrgb("#ffd84a" if k < r + 4 else "#ffefa0", 230))
    if full:
        d.ellipse([18, 58, 46, 63], fill=hexrgb("#ffcf3a", 70))
        for i in range(4):
            t = (phase + i / 4) % 1
            put(front if i % 2 else back, 32 + math.sin(i * 1.9) * 14, 58 - t * 30, hexrgb("#fff1b0", int(255 * (1 - t))))


SKULL = [".www.", "wwwww", "wkwkw", ".www.", ".w.w."]


def guardian_aureole(back, front, full, phase):
    """The fire of wisdom: an arch of flames standing behind the figure. With the whole set it rises
    taller and five small skulls ride along its top."""
    top = 4 if full else 12
    n = 19 if full else 13
    pts = []
    for i in range(n):
        u = i / (n - 1)
        a = math.pi * (1 + u)
        rx, ry = (21, 62 - top - 8) if full else (17, 62 - top - 10)
        x, y = 32 + math.cos(a) * rx, 58 + math.sin(a) * ry
        pts.append((x, y))
        h = (7 if full else 5) + round(math.sin(phase * 2 * math.pi * 2 + i * 1.3) * 1.5)
        flame(back, x, y + 2, h, phase + i * 0.17, ("#5a0a06", "#c9300f", "#ff8a1a", "#ffd86a"))
    if full:
        for k, i in enumerate((4, 6, 9, 12, 14)):
            x, y = pts[i]
            for yy, row in enumerate(SKULL):
                for xx, c in enumerate(row):
                    if c != ".":
                        put(back, x - 2 + xx, y - 6 + yy, hexrgb({"w": "#efe8d6", "k": "#2a1a14"}[c]))


# the wing shapes, from the shoulder outwards (x out, y down), for the right side; the left is mirrored.
# Leading edge first, then the trailing edge back with a notch per feather; notch tips get crimson.
# ---------- the second three top-tier sets ----------
def bachue_serpent(back, front, full, phase):
    """Lake water at the feet with mist on it; a golden serpent winds round the figure, rising as it turns
    (with part of the set it circles the feet)."""
    d, df = ImageDraw.Draw(back), ImageDraw.Draw(front)
    w = 16 if full else 12
    d.ellipse([32 - w, 57, 32 + w, 63], fill=hexrgb("#0f4a52", 200), outline=hexrgb("#4fb3b0", 230))
    df.arc([32 - w, 57, 32 + w, 63], 10, 170, fill=hexrgb("#4fb3b0", 230))
    for i in range(3):  # mist drifting over the water
        t = (phase + i / 3) % 1
        blob(back, 32 - w + t * 2 * w, 56 - (i % 2), 1, hexrgb("#d8f4f0", int(120 * math.sin(t * math.pi))))
    n = 40 if full else 20
    for k in range(n):  # the body, head first
        u = k / n
        a = 2 * math.pi * (phase - u * (1.4 if full else 0.9))
        y = (60 - (1 - u) * 40) if full else 60
        rx = 14 if full else w - 2
        x, yy = 32 + math.cos(a) * rx, y + math.sin(a) * 2.5
        near = math.sin(a) > 0
        layer = front if near else back
        col = "#f2c94a" if k % 3 else "#a8781e"
        blob(layer, x, yy + 1, 1, hexrgb("#7a5414"))
        put(layer, x, yy, hexrgb(col))
        put(layer, x + 1, yy, hexrgb(col))
        if k == 0:
            blob(layer, x, yy, 2, hexrgb("#f7d76a"))
            put(layer, x + (1 if math.cos(a + 0.3) > math.cos(a) else -1), yy - 1, hexrgb("#2a1a08"))  # the eye
            put(layer, x, yy + 2, hexrgb("#d83a2a"))  # the tongue


def snowflake(im, x, y, big, col):
    put(im, x, y, col)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) + (((1, 1), (-1, -1), (1, -1), (-1, 1)) if big else ()):
        put(im, x + dx, y + dy, col)


def nevado_frost(back, front, full, phase):
    """Snow falling round the figure and frost on the ground; with the whole set, a ring of ice
    shards turns round it and ice crystals stand at the feet."""
    d = ImageDraw.Draw(back)
    w = 17 if full else 12
    d.ellipse([32 - w, 57, 32 + w, 63], fill=hexrgb("#dff4ff", 150), outline=hexrgb("#ffffff", 220))
    for i in range(7 if full else 4):
        t = (phase + i / (7 if full else 4)) % 1
        x = 32 + ((i * 11) % 30 - 15) + math.sin((t + i) * 2 * math.pi) * 1.5
        snowflake(front if i % 2 else back, x, 4 + t * 52, i % 3 == 0, hexrgb("#ffffff", int(255 * min(1, 2 - 2 * t))))
    if full:
        for i in range(6):
            a = 2 * math.pi * (phase + i / 6)
            x, y = 32 + math.cos(a) * 20, 36 + math.sin(a) * 5
            layer = front if math.sin(a) > 0 else back
            for k in range(4):  # a shard: a thin crystal
                put(layer, x, y - k, hexrgb("#bfeaff" if k < 3 else "#ffffff"))
            put(layer, x + 1, y - 1, hexrgb("#7fc4ff"))
        for x, h in ((17, 6), (21, 9), (43, 8), (47, 5)):
            for k in range(h):
                put(front if x in (21, 43) else back, x, 62 - k, hexrgb("#9fdcff" if k < h - 2 else "#ffffff"))
                if k < h // 2:
                    put(front if x in (21, 43) else back, x + 1, 62 - k, hexrgb("#5fa8d8"))


LEAF = ("#7aa84a", "#c9a03a", "#b8562a")


def vientos_whirl(back, front, full, phase):
    """Wind wrapping round the figure in white streaks, with leaves caught up in it; with the
    whole set, a whirlwind round the legs and feathers carried on it."""
    rings = [(56, 19, 3), (42, 22, 4), (30, 20, 3)] + ([(18, 18, 3), (61, 24, 2)] if full else [])
    if full:  # the whirlwind's funnel round the legs
        for k in range(6):
            r = 6 + k * 2.4
            ImageDraw.Draw(back).arc([32 - r, 62 - k * 3 - 2, 32 + r, 62 - k * 3 + 2], 180 + (phase * 360 + k * 50) % 360, 180 + (phase * 360 + k * 50) % 360 + 120, fill=hexrgb("#9fd4f0", 170))
    for j, (y, rx, ry) in enumerate(rings[: 5 if full else 2]):
        for k in range(14 if full else 10):  # a streak: an arc that travels round
            a = 2 * math.pi * (phase * (1 if j % 2 else -1) + j * 0.3) + k * 0.12
            x, yy = 32 + math.cos(a) * rx, y + math.sin(a) * ry
            layer = front if math.sin(a) > 0 else back
            put(layer, x, yy, hexrgb("#e8f8ff", 120 + k * 9))
            put(layer, x, yy + 1, hexrgb("#5fb8e8", 120 + k * 9))
    for i in range(5 if full else 3):
        a = 2 * math.pi * (phase + i / (5 if full else 3))
        y = 58 - ((phase + i * 0.37) % 1) * 46
        x = 32 + math.cos(a) * (12 + (58 - y) * 0.2)
        layer = front if math.sin(a) > 0 else back
        col = hexrgb(LEAF[i % 3])
        put(layer, x, y, col)
        put(layer, x + 1, y - 1, col)
        if full and i % 2:  # a feather
            for k in range(4):
                put(layer, x - 2 + k, y + 2 - k // 2, hexrgb("#f4f1ea"))


def montana_quake(back, front, full, phase):
    """The ground cracks under the figure with fire in the cracks, pebbles lift and fall; with the
    whole set, boulders turn slowly round it and dust rises."""
    d = ImageDraw.Draw(back)
    w = 22 if full else 16
    d.ellipse([32 - w, 56, 32 + w, 63], fill=hexrgb("#4a3424", 230), outline=hexrgb("#2a1c12"))
    glow = int(170 + 85 * math.sin(phase * 2 * math.pi))
    cracks = [[(32, 60), (26, 61), (21, 59), (14, 60)], [(32, 60), (38, 62), (43, 59), (50, 61)], [(32, 60), (30, 57)], [(32, 60), (35, 63)]]
    for pts in cracks[: 4 if full else 2]:
        pts = [(32 + (x - 32) * w / 18, y) for x, y in pts]
        d.line(pts, fill=hexrgb("#ffb347", glow), width=1)
        d.line([(x, y + 1) for x, y in pts], fill=hexrgb("#c83a0a", glow))
    for i in range(3 if full else 2):  # embers out of the cracks
        t = (phase + i / 3) % 1
        put(front, 32 + (i * 11 % 30 - 15) * w / 18, 59 - t * 14, hexrgb("#ffb347", int(255 * (1 - t))))
    for i in range(4 if full else 3):  # pebbles hopping up and back down
        t = (phase + i / 4) % 1
        x = 32 + (i * 9 % 26 - 13)
        y = 60 - math.sin(t * math.pi) * 8
        put(front if i % 2 else back, x, y, hexrgb("#8a7a6a"))
        put(front if i % 2 else back, x + 1, y, hexrgb("#5a4a3a"))
    if full:
        for i in range(4):
            a = 2 * math.pi * (phase + i / 4)
            x, y = 32 + math.cos(a) * 22, 26 + math.sin(a) * 6 + i * 6
            layer = front if math.sin(a) > 0 else back
            ImageDraw.Draw(layer).polygon([(x - 3, y), (x - 1, y - 3), (x + 3, y - 2), (x + 3, y + 2), (x - 1, y + 3)],
                                          fill=hexrgb("#7a6a5a"), outline=hexrgb("#3a2c20"))
            put(layer, x - 1, y - 1, hexrgb("#b8a890"))
        for i in range(4):  # dust
            t = (phase + i / 4) % 1
            blob(back, 32 + (i * 13 % 34 - 17), 60 - t * 10, 1, hexrgb("#c8b090", int(110 * (1 - t))))


FIVE = ["#2f6fd0", "#f2f2ee", "#d83a2a", "#2f9a4a", "#f2c12e"]


def kalachakra_wheel(back, front, full, phase):
    """The wheel of time turning behind the figure: rings in the five colours and eight spokes;
    with the whole set it grows, a second ring turns the other way and seven planets go round."""
    d = ImageDraw.Draw(back)
    hx, hy = 32, 30
    R = 24 if full else 17
    for k, col in enumerate(FIVE):
        r = R - k * 1.2
        d.ellipse([hx - r, hy - r, hx + r, hy + r], outline=hexrgb(col, 200))
    for i in range(8):
        a = 2 * math.pi * (i / 8 + phase / 8)
        for k in range(4, int(R - 6)):
            if k % 2 == 0:
                put(back, hx + math.cos(a) * k, hy + math.sin(a) * k, hexrgb("#f2c12e", 200))
        blob(back, hx + math.cos(a) * (R - 6), hy + math.sin(a) * (R - 6), 1, hexrgb("#ffe38a"))
    if full:
        r2 = R + 4
        for i in range(16):
            a = 2 * math.pi * (i / 16 - phase / 16)
            put(back, hx + math.cos(a) * r2, hy + math.sin(a) * r2, hexrgb("#aef3ff" if i % 2 else "#3fc4e4"))
        planets = ["#f2f2ee", "#d83a2a", "#2f9a4a", "#f2c12e", "#2f6fd0", "#e07aa0", "#8a6a3a"]
        for i, col in enumerate(planets):
            a = 2 * math.pi * (phase + i / 7)
            x, y = hx + math.cos(a) * (r2 + 3), 58 + math.sin(a) * 3
            blob(front if math.sin(a) > 0 else back, x, y, 1 if i < 2 else 0, hexrgb(col))


RAINBOW = ["#d83a2a", "#f28a2a", "#f2d12e", "#2f9a4a", "#2f6fd0", "#8a4ad8"]


def luzclara_rainbow(back, front, full, phase):
    """A sphere of rainbow light round the figure, breathing; drops of light in five colours rise
    from it. With the whole set it holds the whole body, and the figure's own edges shine."""
    d = ImageDraw.Draw(back)
    hx, hy = 32, (36 if full else 22)
    R = (27 if full else 13) + round(math.sin(phase * 2 * math.pi))
    d.ellipse([hx - R + 4, hy - R + 4, hx + R - 4, hy + R - 4], fill=hexrgb("#ffffff", 50 if full else 70))
    for k, col in enumerate(RAINBOW):
        r = R - k
        d.ellipse([hx - r, hy - r, hx + r, hy + r], outline=hexrgb(col, 170 if full else 200))
    for i in range(7 if full else 4):  # drops of light rising
        t = (phase + i / 7) % 1
        x = hx + math.sin(i * 2.1) * (R - 6)
        y = (60 if full else 30) - t * (40 if full else 22)
        put(front if full and i % 2 else back, x, y, hexrgb(FIVE[i % 5], int(255 * (1 - t))))
    if full:
        for i in range(10):  # sparkles on the sphere
            a = 2 * math.pi * (i / 10 + phase / 3)
            if (i + int(phase * 8)) % 3 == 0:
                x, y = hx + math.cos(a) * R, hy + math.sin(a) * R
                for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                    put(front if math.sin(a) > 0.6 else back, x + dx, y + dy, hexrgb("#ffffff"))


WING_FULL = [(0, 0), (6, -6), (13, -9), (19, -8), (23, -5),  # leading edge to the tip
             (21, 0), (22, 4), (18, 5), (18, 10), (14, 10), (13, 14), (9, 13), (8, 16), (4, 14), (2, 15), (0, 10), (-1, 4)]
WING_FULL_TIPS = [(23, -5), (22, 4), (18, 10), (13, 14), (8, 16), (2, 15)]
WING_PART = [(0, 0), (3, -7), (6, -13), (8, -15), (8, -9), (7, -4), (7, 1), (4, 3), (2, 6), (0, 3)]  # folded, pointing up
WING_PART_TIPS = [(8, -15), (7, 1), (2, 6)]


def condor_wings(back, front, full, phase):
    """Two wings of black feathers behind the shoulders, crimson at the feather tips; they beat
    slowly. With part of the set they're folded; with the whole set, spread wide."""
    d = ImageDraw.Draw(back)
    beat = math.sin(phase * 2 * math.pi)
    shape, tips = (WING_FULL, WING_FULL_TIPS) if full else (WING_PART, WING_PART_TIPS)
    reach = max(abs(x) for x, _ in shape)
    def at(side, p):
        x, y = p
        lift = beat * 4 * (abs(x) / reach)  # the further out, the more the beat moves it
        return (32 + side * 6 + side * x, 25 + y - lift)
    for side in (-1, 1):
        pts = [at(side, p) for p in shape]
        d.polygon(pts, fill=hexrgb("#2b2733"), outline=hexrgb("#1a0a0e"))
        # feather lines from the wing root to each notch, lighter
        root = at(side, (1, 1))
        for p in tips:
            e = at(side, p)
            d.line([root, ((root[0] + e[0]) / 2, (root[1] + e[1]) / 2)], fill=hexrgb("#443f4e"))
        for p in tips:
            x, y = at(side, p)
            back.putpixel((int(round(x)), int(round(y))), hexrgb("#ff5a4a"))
            back.putpixel((int(round(x)) - side, int(round(y))), hexrgb("#b2302a"))
    # crimson embers drifting up around the figure, in front when on the near side of the orbit
    k = 5 if full else 2
    for i in range(k):
        a = phase * 2 * math.pi + i * 2 * math.pi / k
        x = 32 + math.cos(a) * 17
        y = 52 - ((phase + i / k) % 1) * 36
        col = hexrgb("#ff5a4a" if i % 2 else "#ffb0a4", 240)
        (front if math.sin(a) > 0 else back).putpixel((int(x), int(y)), col)


def origen_voice(back, front, full, phase):
    """Rings of sound spreading on the ground, motes of light orbiting the figure; the whole set
    adds a halo behind the head."""
    d = ImageDraw.Draw(back)
    df = ImageDraw.Draw(front)
    cx, cy = 32, 60
    rings = 3 if full else 2
    for i in range(rings):
        t = (phase + i / rings) % 1
        r = 5 + t * (16 if full else 12)
        a = int(255 * (1 - t) ** 0.8)
        col = hexrgb("#6fe6ff" if i % 2 == 0 else "#dffbff", a)
        box = [cx - r, cy - r / 3.2, cx + r, cy + r / 3.2]
        # the back half of the ring behind the figure, the front half over its feet
        d.arc(box, 180, 360, fill=col)
        df.arc(box, 0, 180, fill=col)
        if full:
            d.arc([cx - r, cy - r / 3.2 + 1, cx + r, cy + r / 3.2 + 1], 180, 360, fill=hexrgb("#2a9fbb", a // 2))
    if full:
        # the halo: an open ring behind the head, with sparks running round it
        hx, hy, hr = 32, 20, 12 + round(math.sin(phase * 2 * math.pi))
        d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], outline=hexrgb("#2a9fbb", 230), width=2)
        d.ellipse([hx - hr + 1, hy - hr + 1, hx + hr - 1, hy + hr - 1], outline=hexrgb("#6fe6ff", 250))
        for i in range(8):
            a = i * math.pi / 4 + phase * 2 * math.pi
            back.putpixel((int(hx + math.cos(a) * (hr + 2)), int(hy + math.sin(a) * (hr + 2))), hexrgb("#dffbff", 250))
    # motes: around the body, in an orbit tilted so they pass in front and behind
    k = 6 if full else 3
    for i in range(k):
        a = phase * 2 * math.pi * (1 if i % 2 else -1) + i * 2 * math.pi / k
        x = int(32 + math.cos(a) * (18 if full else 15))
        y = int(36 + math.sin(a) * 5 - (i % 3) * 9)
        near = math.sin(a) > 0
        layer = front if near else back
        layer.putpixel((x, y), hexrgb("#dffbff" if near else "#6fe6ff", 255))
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            layer.putpixel((x + dx, y + dy), hexrgb("#6fe6ff" if near else "#2a9fbb", 170 if full else 120))


TUNJO = [".g.", "gyg", ".g.", "g.g"]  # a little votive figure, the lake's offerings


def laguna_offering(back, front, full, phase):
    """Gold dust falling around the figure, as on the one who went out on the lake; a pool of lake
    water at the feet with gold glinting in it. The whole set adds three tunjos circling the waist."""
    d = ImageDraw.Draw(back)
    df = ImageDraw.Draw(front)
    # the pool: a flat ellipse, its back half behind the feet and its rim in front
    w = 15 if full else 11
    box = [32 - w, 57, 32 + w, 63]
    d.ellipse(box, fill=hexrgb("#1c5459", 200), outline=hexrgb("#2f8f8a", 230))
    df.arc(box, 10, 170, fill=hexrgb("#2f8f8a", 230))
    for i in range(3 if full else 2):  # glints moving across the water
        t = (phase + i / 3) % 1
        x = int(32 - w + 3 + t * (2 * w - 6))
        back.putpixel((x, 60), hexrgb("#9fe3d6" if i % 2 else "#e8b93d", 255))
    # gold dust: flakes falling on both sides of the body, some passing in front
    k = 9 if full else 4
    for i in range(k):
        t = (phase + i * 0.37) % 1
        side = -1 if i % 2 else 1
        x = int(32 + side * (11 + (i * 5) % 8) + math.sin((t + i) * 2 * math.pi) * 1.5)
        y = int(4 + t * 52)
        col = ("#fff0b0", "#e8b93d", "#f7b3cf")[i % 3]
        layer = front if i % 3 == 0 else back
        layer.putpixel((x, y), hexrgb(col, 255))
        if full and i % 2 == 0:
            layer.putpixel((x, y - 1), hexrgb("#9d7322", 160))
    if full:
        for i in range(3):
            a = phase * 2 * math.pi + i * 2 * math.pi / 3
            x = int(32 + math.cos(a) * 17) - 1
            y = int(40 + math.sin(a) * 4)
            near = math.sin(a) > 0
            layer = front if near else back
            for yy, row in enumerate(TUNJO):
                for xx, c in enumerate(row):
                    if c != ".":
                        layer.putpixel((x + xx, y + yy), hexrgb({"g": "#e8b93d" if near else "#9d7322", "y": "#e0679e"}[c], 255))



# ---------- the high bands' sets ----------
def osario_dance(back, front, full, phase):
    """Marigold petals drifting down round the figure; with the whole set, a ring of candles at the feet
    and three little skulls dancing round in a circle."""
    for i in range(9 if full else 7):  # petals falling, swaying
        t = (phase + i / 8) % 1
        x = 32 + math.sin(i * 2.7) * 17 + math.sin(t * 2 * math.pi + i) * 2
        layer = front if i % 2 else back
        put(layer, x, 6 + t * 54, hexrgb("#ff9a1a", int(255 * (1 - t * 0.6))))
        put(layer, x + 1, 6 + t * 54, hexrgb("#ffd060", int(220 * (1 - t * 0.6))))
    if full:
        for i in range(8):  # candles
            a = 2 * math.pi * i / 8
            x, y = 32 + math.cos(a) * 18, 60 + math.sin(a) * 3
            layer = front if math.sin(a) > 0 else back
            for k in range(3):
                put(layer, x, y - k, hexrgb("#efe6cf"))
            put(layer, x, y - 3 - (int(phase * 6 + i) % 2), hexrgb("#ffb347"))
        for i in range(3):  # skulls dancing round
            a = 2 * math.pi * (phase + i / 3)
            x, y = 32 + math.cos(a) * 21, 50 + math.sin(a) * 4 - abs(math.sin(phase * 6 * math.pi + i)) * 2
            layer = front if math.sin(a) > 0 else back
            for yy, row in enumerate(SKULL):
                for xx, c in enumerate(row):
                    if c != ".":
                        put(layer, x - 2 + xx, y - 4 + yy, hexrgb({"w": "#efe8d6", "k": "#2a1a14"}[c]))


def tairona_terraces(back, front, full, phase):
    """Rings of stone terraces at the feet, like the steps of the Lost City; with the whole set, two
    gold birds of the Sierra circle the figure, their wings beating."""
    d = ImageDraw.Draw(back)
    rings = ((22, "#5a4636"), (19, "#7a6048"), (16, "#9a7c5c")) if full else ((19, "#5a4636"), (16, "#7a6048"))
    for k, (r, col) in enumerate(rings):
        d.ellipse([32 - r, 58 - 2 * k, 32 + r, 63 - k], fill=hexrgb(col), outline=hexrgb("#2e2018"))
    for i in range(6):  # a glint of gold walking round the top step
        a = 2 * math.pi * (phase + i / 6)
        if i % 3 == 0:
            r = rings[-1][0]
            put(back, 32 + math.cos(a) * r, 61 - len(rings) + math.sin(a) * 1.5, hexrgb("#f8d868"))
    if full:
        for i in range(2):
            a = 2 * math.pi * (phase + i / 2)
            x, y = 32 + math.cos(a) * 20, 28 + math.sin(a) * 6
            layer = front if math.sin(a) > 0 else back
            up = int(phase * 8 + i) % 2
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (-2, -1 if up else 1), (2, -1 if up else 1), (-3, -2 if up else 1), (3, -2 if up else 1)):
                put(layer, x + dx, y + dy, hexrgb("#d4a02c" if dx else "#fff8d0"))


def dorado_discs(back, front, full, phase):
    """Hammered gold discs turning slowly round the figure, catching the light; with the whole set,
    more of them, and gold dust trailing behind each."""
    n = 6 if full else 3
    for i in range(n):
        a = 2 * math.pi * (phase + i / n)
        x, y = 32 + math.cos(a) * 19, 38 + math.sin(a) * 9 - 6 * math.cos(a + 1)
        layer = front if math.sin(a) > 0 else back
        edge = abs(math.cos(a * 2 + i))  # turning: a full disc, then edge-on
        w = 0 if edge < 0.3 else 1 if edge < 0.7 else 2
        for dx in range(-w, w + 1):
            for dy in (-2, -1, 0, 1, 2):
                if abs(dy) + (abs(dx) if w else 0) <= 2 + (w == 2):
                    put(layer, x + dx, y + dy, hexrgb("#fff0a0" if dx == -w and dy < 0 else "#e8b030" if abs(dy) < 2 else "#a8701a"))
        if full:
            for k in range(1, 4):
                b = a - k * 0.12
                put(back, 32 + math.cos(b) * 19, 38 + math.sin(b) * 9 - 6 * math.cos(b + 1), hexrgb("#ffe07a", 200 - k * 50))
    if full:
        d = ImageDraw.Draw(back)  # lake water at the feet, as on the raft
        d.ellipse([16, 58, 48, 63], fill=hexrgb("#0e6a70", 150), outline=hexrgb("#7ae8dc", 160))


def relampago_crown(back, front, full, phase):
    """A crown of lightning over the head, crackling; with the whole set, bolts strike the ground on
    either side now and then and the ground glows where they land."""
    f = int(phase * 8)
    hx, hy = 32, 8
    for i in range(7):  # zigzag points of the crown
        x = hx - 9 + i * 3
        h = 3 + ((i + f) % 3)
        for k in range(h):
            put(back, x + (k % 2), hy - k + 3, hexrgb("#bff8ff" if k == h - 1 else "#8a4ad0"))
    for x in range(hx - 9, hx + 10):
        put(back, x, hy + 3, hexrgb("#c8a0ff", 220))
    for i in range(3):  # sparks jumping off it
        a = (i * 2.1 + f) % 6.28
        put(front, hx + math.cos(a) * 11, hy + math.sin(a) * 4, hexrgb("#ffffff"))
    if full:
        for side, strike in ((-1, f in (1, 2)), (1, f in (5, 6))):
            if not strike:
                continue
            x0 = 32 + side * 20
            pts = [(x0, 0), (x0 - side * 3, 14), (x0 + side * 2, 22), (x0 - side * 2, 38), (x0 + side, 50), (x0, 61)]
            d = ImageDraw.Draw(back)
            d.line(pts, fill=hexrgb("#4ae0ff"), width=2)
            d.line(pts, fill=hexrgb("#ffffff"), width=1)
            d.ellipse([x0 - 5, 59, x0 + 5, 63], fill=hexrgb("#bff8ff", 140))


def vigilia_moon(back, front, full, phase):
    """A crescent moon behind the head; with the whole set it's full and silver, and pale moths
    flutter round the figure."""
    d = ImageDraw.Draw(back)
    hx, hy, r = 32, 14, (10 if full else 8)
    d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=hexrgb("#e4e0f2", 200 if full else 220))
    if not full:  # the dark bite that makes the crescent
        d.ellipse([hx - r + 5, hy - r - 2, hx + r + 5, hy + r - 2], fill=(0, 0, 0, 0))
    else:
        for cx, cy in ((-3, -2), (3, 2), (1, -4)):  # its seas
            put(back, hx + cx, hy + cy, hexrgb("#a49cc0"))
            put(back, hx + cx + 1, hy + cy, hexrgb("#a49cc0"))
        d.ellipse([hx - r - 3, hy - r - 3, hx + r + 3, hy + r + 3], outline=hexrgb("#b8a0ec", 90))
        for i in range(3):
            a = 2 * math.pi * (phase * 0.5 + i / 3)
            x, y = 32 + math.cos(a) * 18 + math.sin(phase * 12 + i) * 2, 36 + math.sin(a * 2) * 10
            layer = front if math.sin(a) > 0 else back
            up = int(phase * 12 + i) % 2
            put(layer, x, y, hexrgb("#ece4ff"))
            put(layer, x - 1, y - up, hexrgb("#b8a0ec"))
            put(layer, x + 1, y - up, hexrgb("#b8a0ec"))
    for i in range(4 if full else 2):  # star glints
        if (i + int(phase * 6)) % 3 == 0:
            put(back, 12 + i * 13, 6 + (i * 7) % 12, hexrgb("#ffffff"))


def pacto_shadow(back, front, full, phase):
    """Black smoke curling up round the feet; with the whole set a horned shadow stands behind the
    figure, taller than it, with two red eyes that blink."""
    if full:
        d = ImageDraw.Draw(back)
        sway = round(math.sin(phase * 2 * math.pi))
        d.ellipse([18 + sway, 2, 46 + sway, 30], fill=hexrgb("#0a0606", 200))  # the head and shoulders
        d.rectangle([12 + sway, 20, 52 + sway, 60], fill=hexrgb("#0a0606", 170))
        d.polygon([(20 + sway, 8), (14 + sway, -2), (23 + sway, 4)], fill=hexrgb("#0a0606", 220))  # horns
        d.polygon([(44 + sway, 8), (50 + sway, -2), (41 + sway, 4)], fill=hexrgb("#0a0606", 220))
        if int(phase * 8) != 3:
            for ex in (27, 37):
                put(back, ex + sway, 12, hexrgb("#ff2020"))
                put(back, ex + 1 + sway, 12, hexrgb("#ff7040"))
    for i in range(9 if full else 6):  # smoke
        t = (phase + i / 7) % 1
        x = 32 + math.sin(i * 2.3) * 14 + math.sin(t * 5 + i) * 2
        y = 62 - t * (30 if full else 20)
        blob(front if i % 3 == 0 else back, x, y, 2 if t < 0.35 else 1 if t < 0.7 else 0, hexrgb("#4a3a3a", int(200 * (1 - t))))
        blob(back, x + 1, y + 1, 1 if t < 0.5 else 0, hexrgb("#1a1010", int(220 * (1 - t))))
        if i % 2 == 1:
            put(front, x, y - 2, hexrgb("#ff4020", int(230 * (1 - t))))


def firmamento_stars(back, front, full, phase):
    """Stars wheeling round the figure on a tilted orbit; with the whole set, a band of the Milky Way
    across the back and lines joining the stars into constellations."""
    if full:
        for x in range(2, 62):  # the Milky Way, diagonal, sparkling
            y = 4 + x * 0.35
            for k in range(-3, 4):
                if (x * 7 + k * 13 + int(phase * 16)) % 11 == 0:
                    put(back, x, y + k, hexrgb("#ffffff", 220))
                elif abs(k) < 2 and x % 2 == 0:
                    put(back, x, y + k, hexrgb("#3e58c0", 70))
    n = 7 if full else 4
    pts = []
    for i in range(n):
        a = 2 * math.pi * (phase / 2 + i / n)
        x, y = 32 + math.cos(a) * 22, 32 + math.sin(a) * 8 - math.cos(a) * 6
        near = math.sin(a) > 0
        pts.append((x, y, near))
        layer = front if near else back
        put(layer, x, y, hexrgb("#ffffff"))
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            put(layer, x + dx, y + dy, hexrgb("#fff0a0", 200 if (i + int(phase * 8)) % 2 else 120))
    if full:
        d = ImageDraw.Draw(back)
        for (x0, y0, n0), (x1, y1, n1) in zip(pts, pts[1:]):
            if not n0 and not n1:
                d.line([(x0, y0), (x1, y1)], fill=hexrgb("#a0b8ff", 90))


def madreagua_river(back, front, full, phase):
    """A ribbon of river water spiralling up round the figure, with long gold strands of her hair
    in it; with the whole set, a pool at the feet and little gold fish leaping out and back."""
    turns = 2.2 if full else 1.4
    n = 46 if full else 30
    for k in range(n):
        u = k / n
        a = 2 * math.pi * (u * turns + phase)
        x, y = 32 + math.cos(a) * (19 - u * 4), 62 - u * (50 if full else 34) + math.sin(a) * 3
        layer = front if math.sin(a) > 0 else back
        put(layer, x, y, hexrgb("#2a9a98" if k % 3 else "#8ae0d4", 230))
        put(layer, x, y + 1, hexrgb("#0e6268", 200))
        if k % 7 == 3:  # a gold hair strand caught in the water
            put(layer, x + 1, y - 1, hexrgb("#ffe07a"))
            put(layer, x + 2, y - 1, hexrgb("#e8b030"))
    if full:
        d = ImageDraw.Draw(back)
        d.ellipse([12, 57, 52, 63], fill=hexrgb("#0e6268", 170), outline=hexrgb("#8ae0d4", 200))
        for i in range(2):
            t = (phase * 2 + i / 2) % 1
            x0 = 18 + i * 28
            x, y = x0 + t * 8 * (1 if i == 0 else -1), 59 - math.sin(t * math.pi) * 14
            layer = front if i else back
            for dx in (-1, 0, 1):
                put(layer, x + dx, y, hexrgb("#e8b030"))
            put(layer, x + (2 if i == 0 else -2), y - 1, hexrgb("#ffe07a"))


def caiman_swamp(back, front, full, phase):
    """Reeds round the feet swaying, fireflies drifting; with the whole set, dark water at the feet and
    two yellow caiman eyes rising out of it, blinking, with a ridge of scales behind."""
    for i, x in enumerate((15, 19, 45, 49) + ((12, 52) if full else ())):
        sway = math.sin(phase * 2 * math.pi + i) * 1.2
        h = 9 + (i * 3) % 4
        for k in range(h):
            put(front if x in (19, 45) else back, x + sway * k / h, 62 - k, hexrgb("#4e7030" if k < h - 2 else "#9ab45a"))
    for i in range(5 if full else 3):
        t = (phase + i / 5) % 1
        x, y = 32 + math.sin(i * 2.3 + t * 4) * 18, 30 + math.cos(i * 1.7 + t * 3) * 14
        if (i + int(phase * 10)) % 3:
            put(front if i % 2 else back, x, y, hexrgb("#e8f060"))
    if full:
        d = ImageDraw.Draw(back)
        d.ellipse([8, 57, 56, 63], fill=hexrgb("#0e1a0c", 200), outline=hexrgb("#2a4a1e", 220))
        rise = round(math.sin(phase * 2 * math.pi))
        for k in range(6):  # the ridge of scales
            put(back, 44 + k * 2, 58 - (k % 2) - rise, hexrgb("#4e7030"))
        if int(phase * 8) != 5:
            for ex in (10, 15):
                put(back, ex, 58 - rise, hexrgb("#fff48a"))
                put(back, ex + 1, 58 - rise, hexrgb("#e8d040"))


def andes_peaks(back, front, full, phase):
    """Snow falling softly round the figure; with the whole set, the white peaks of the Andes behind,
    the sun coming up between them and a band of the seven colours of a chumbe across the slopes."""
    if full:
        d = ImageDraw.Draw(back)
        sun = 16 + round(math.sin(phase * 2 * math.pi))
        d.ellipse([47, sun + 6, 57, sun + 16], fill=hexrgb("#ffcf3a", 220))
        for pk in ((4, 40, 22), (20, 46, 14), (34, 58, 18), (46, 62, 24)):
            x0, x1, top = pk
            mid = (x0 + x1) / 2
            d.polygon([(x0, 44), (mid, top), (x1, 44)], fill=hexrgb("#3a4048"), outline=hexrgb("#7a8490"))
            d.polygon([(mid - 3, top + 4), (mid, top), (mid + 3, top + 4)], fill=hexrgb("#eef2f8"))
        for k, col in enumerate(("#d83a2a", "#f28a2a", "#f2d12e", "#2f9a4a", "#2f6fd0", "#8a4ad8", "#e07aa0")):
            for x in range(4, 61):
                if (x + k) % 2 == 0:
                    put(back, x, 44 - k * 0.5 + (x % 7 == 0), hexrgb(col, 170))
    for i in range(10 if full else 6):
        t = (phase + i / 10) % 1
        x = 32 + math.sin(i * 2.7) * 20 + math.sin(t * 2 * math.pi + i) * 1.5
        put(front if i % 2 else back, x, 4 + t * 56, hexrgb("#ffffff", int(240 * (1 - t * 0.5))))

def arhuaco_weave(back, front, full, phase):
    """A mochila's base at the feet: woven in a spiral from the centre out, natural wool, the spiral
    turning slowly; with the whole set, a thread of white cotton winds up round the figure as if
    the weaving went on, and a few snowflakes of the Sierra's peaks drift past."""
    d = ImageDraw.Draw(back)
    rx = 20 if full else 16
    d.ellipse([32 - rx, 56, 32 + rx, 63], fill=hexrgb("#4a3020"), outline=hexrgb("#1a0e08"))
    cols = ("#7a5636", "#b8986c", "#e8dcc2", "#2e2016")
    # the spiral: a line of stitches going round and outwards
    n = 70 if full else 52
    for i in range(n):
        u = i / n
        a = 2 * math.pi * (u * 3.2 - phase)
        r = 1.5 + u * (rx - 2)
        put(back, 32 + math.cos(a) * r, 59.5 + math.sin(a) * r * 0.17, hexrgb(cols[(i // 6) % 4]))
    if full:
        for i in range(36):  # the thread: a helix climbing the figure, behind on one side, in front on the other
            u = i / 36
            a = 2 * math.pi * (u * 2.5 + phase)
            x, y = 32 + math.cos(a) * 19, 58 - u * 46
            put(front if math.sin(a) > 0 else back, x, y, hexrgb("#fbf5e8", int(255 * (0.35 + 0.65 * (1 - u)))))
        for i in range(5):
            t = (phase + i / 5) % 1
            put(front if i % 2 else back, 32 + math.sin(i * 2.3) * 22, 4 + t * 50, hexrgb("#ffffff", int(230 * (1 - t * 0.6))))


# ---------- the sets from 138 to 200 ----------
TAU = 2 * math.pi


def galeon_wreck(back, front, full, phase):
    """Bubbles rising round the figure and gold doubloons glinting as they sink; with the whole set,
    the ghost of the galleon behind: a hull, two masts and torn sails, swaying with the sea."""
    if full:
        d = ImageDraw.Draw(back)
        sw = math.sin(phase * TAU) * 1.5
        d.polygon([(4, 44 + sw), (60, 44 - sw), (54, 54 - sw), (10, 54 + sw)], fill=hexrgb("#1e4a52", 150), outline=hexrgb("#4a7a70", 170))
        for mx, top in ((22, 4), (42, 8)):
            d.line([(mx, 44), (mx + sw, top)], fill=hexrgb("#4a7a70", 170))
            d.polygon([(mx - 9 + sw, top + 6), (mx + 9 + sw, top + 6), (mx + 7, top + 22), (mx - 7, top + 22)], fill=hexrgb("#a8c8b0", 70))
    for i in range(10 if full else 6):
        t = (phase + i / 10) % 1
        x = 32 + math.sin(i * 2.9) * 21 + math.sin(t * TAU * 2 + i) * 1.5
        put(front if i % 3 == 0 else back, x, 62 - t * 56, hexrgb("#c8f0ff", int(220 * (1 - t))))
        if t > 0.6:
            put(back, x + 1, 62 - t * 56, hexrgb("#c8f0ff", 120))
    for i in range(4 if full else 2):  # coins, sinking and turning
        t = (phase * 0.7 + i / 4) % 1
        x, y = 32 + math.sin(i * 1.7 + 1) * 18, 10 + t * 50
        edge = abs(math.cos((t * 3 + i) * TAU))
        col = hexrgb("#ffe07a") if edge > 0.5 else hexrgb("#a8701a")
        put(front if i % 2 else back, x, y, col)
        if edge > 0.5:
            put(front if i % 2 else back, x + 1, y, hexrgb("#d8a830"))


def frailejon_mist(back, front, full, phase):
    """Páramo mist drifting across at knee height; with the whole set, two frailejones stand either
    side, grey-green rosettes on furry trunks, their yellow flowers nodding, and drops of water fall."""
    if full:
        d = ImageDraw.Draw(back)
        for fx, h in ((7, 30), (56, 24)):
            d.rectangle([fx - 2, 62 - h, fx + 2, 62], fill=hexrgb("#6a6a50"), outline=hexrgb("#3a3a2a"))
            top = 62 - h
            for k in range(10):
                a = k / 10 * TAU
                d.line([(fx, top), (fx + math.cos(a) * 6, top + math.sin(a) * 3 - 1)], fill=hexrgb("#93a594"))
            nod = round(math.sin(phase * TAU + fx))
            for k in (-4, 0, 4):
                blob(back, fx + k + nod, top - 5 - abs(k) // 2, 1, hexrgb("#f8ea7a"))
        for i in range(4):
            t = (phase + i / 4) % 1
            put(back, 10 + i * 14, 6 + t * 54, hexrgb("#bfe8ff", int(200 * (1 - t))))
    for band, y in ((0, 52), (1, 57)):
        for i in range(8 if full else 5):
            x = ((i * 13 + band * 6 + phase * 64 * (1 if band else -1)) % 76) - 6
            for dx in range(-5, 6):
                a = int((90 if full else 70) * (1 - abs(dx) / 6))
                put(front if band else back, x + dx, y + (dx % 3 == 0), hexrgb("#e4ece8", a))


def bochica_falls(back, front, full, phase):
    """A thin fall of water behind, pouring and foaming at the feet (Tequendama, opened by his staff);
    with the whole set, the fall is wide and a rainbow (Chuchaviva) arches over it."""
    d = ImageDraw.Draw(back)
    w = 16 if full else 8
    for x in range(32 - w, 32 + w + 1):
        for y in range(4 if full else 20, 60):
            if (y * 3 + x * 5 - int(phase * 24)) % 7 == 0:
                put(back, x, y, hexrgb("#d0f4ff", 170))
            elif (x + y) % 3 == 0:
                put(back, x, y, hexrgb("#2a8ad0", 70))
    for i in range(10 if full else 6):  # foam
        t = (phase + i / 10) % 1
        put(front if i % 2 else back, 32 + math.sin(i * 2.1) * (w + 2), 61 - t * 5, hexrgb("#ffffff", int(230 * (1 - t))))
    if full:
        for k, col in enumerate(("#e04040", "#f0a030", "#f0e040", "#40c060", "#4080e0", "#8a4ad8")):
            r = 28 - k
            for j in range(60):
                a = math.pi + j / 59 * math.pi
                put(back, 32 + math.cos(a) * r, 34 + math.sin(a) * r * 0.9, hexrgb(col, 150))


def bufeo_river(back, front, full, phase):
    """Dark river water rippling round the feet; with the whole set, a pink river dolphin leaps over the
    figure in an arc and dives back in, splashing."""
    d = ImageDraw.Draw(back)
    d.ellipse([6, 55, 58, 63], fill=hexrgb("#3a2a12", 160))
    for i in range(3):
        t = (phase + i / 3) % 1
        rx = 6 + t * 22
        d.ellipse([32 - rx, 59 - rx * 0.15, 32 + rx, 59 + rx * 0.15], outline=hexrgb("#d8c090", int(170 * (1 - t))))
    if full:
        t = phase
        a = math.pi * (1 - t)  # from the right, over the top, into the water on the left
        x, y = 32 + math.cos(a) * 26, 50 - math.sin(a) * 46
        ang = a - math.pi / 2
        layer = front if t > 0.5 else back
        for k in range(-5, 6):  # the body, along the arc
            bx, by = x + math.cos(ang) * k, y - math.sin(ang) * k
            blob(layer, bx, by, 1 if abs(k) < 4 else 0, hexrgb("#f6c0d2" if k < 3 else "#d07a98"))
        put(layer, x + math.cos(ang) * 6, y - math.sin(ang) * 6, hexrgb("#8e3a5a"))  # the long beak
        put(layer, x + math.cos(ang) * 7, y - math.sin(ang) * 7, hexrgb("#8e3a5a"))
        for sx in (6, 58):
            if (sx == 58 and t < 0.15) or (sx == 6 and t > 0.85):
                for k in range(5):
                    put(front, sx + (k - 2) * 2, 54 - (k % 2) * 3, hexrgb("#ffffff", 220))


def llanero_plains(back, front, full, phase):
    """Plains grass swaying at the feet; with the whole set, the sun going down huge and orange behind
    on a flat horizon, and a line of white herons crossing it."""
    if full:
        d = ImageDraw.Draw(back)
        d.ellipse([14, 20, 50, 56], fill=hexrgb("#f06a1a", 200))
        d.ellipse([18, 24, 46, 52], fill=hexrgb("#ffb060", 140))
        d.line([(0, 46), (63, 46)], fill=hexrgb("#a8300e", 220))
        for i in range(4):
            x = ((phase * 70 + i * 9) % 84) - 10
            y = 14 + i * 2 + math.sin(phase * TAU * 2 + i) * 1
            wing = (int(phase * 8) + i) % 2
            put(back, x, y, hexrgb("#ffffff"))
            put(back, x - 1, y - wing, hexrgb("#ffffff"))
            put(back, x + 1, y - wing, hexrgb("#ffffff"))
    for i in range(22 if full else 14):
        x = 4 + i * (56 / (21 if full else 13))
        h = 4 + (i * 7) % 4
        lean = math.sin(phase * TAU + i * 0.5) * 2
        col = hexrgb("#b88040") if i % 3 else hexrgb("#e8c088")
        for k in range(h):
            put(front if i % 2 else back, x + lean * k / h, 62 - k, col)


def madremonte_leaves(back, front, full, phase):
    """Leaves whirling round the figure, in front and behind; with the whole set, vines climb up both
    sides and over the top in a frame, and the leaves come thick as in a storm."""
    if full:
        for side in (-1, 1):
            for k in range(58):
                y = 62 - k
                x = 32 + side * (24 - (max(0, k - 44) * 1.6)) + math.sin(k * 0.4 + phase * TAU) * 1.2
                put(back, x, y, hexrgb("#3e8a2a"))
                if k % 6 == 0:
                    blob(back, x + side * 2, y, 1, hexrgb("#8ac85a"))
    n = 16 if full else 8
    for i in range(n):
        a = TAU * (phase + i / n)
        x, y = 32 + math.cos(a) * 20, 58 - ((i * 37) % 44) + math.sin(a) * 4
        layer = front if math.sin(a) > 0 else back
        col = ("#3e8a2a", "#8ac85a", "#6a4422")[i % 3]
        put(layer, x, y, hexrgb(col))
        put(layer, x + 1, y - (i % 2), hexrgb(col))


def silbon_whistle(back, front, full, phase):
    """Whistled notes, small and white, rising in a spiral (do re mi fa sol la si, the Silbón's tune);
    with the whole set, his long thin shadow behind the figure, taller than it, with the sack."""
    if full:
        d = ImageDraw.Draw(back)
        sw = round(math.sin(phase * TAU))
        d.rectangle([28 + sw, 0, 36 + sw, 60], fill=hexrgb("#0a0a10", 170))
        d.ellipse([27 + sw, -4, 37 + sw, 6], fill=hexrgb("#0a0a10", 190))
        d.polygon([(20 + sw, -1), (44 + sw, -1), (40 + sw, 2), (24 + sw, 2)], fill=hexrgb("#0a0a10", 200))  # the hat brim
        d.ellipse([40 + sw, 30, 54 + sw, 46], fill=hexrgb("#3a342a", 200))  # the sack
        for k in range(3):
            put(back, 44 + sw + k * 3, 36 + (k % 2) * 3, hexrgb("#e8e0cc"))
    n = 7 if full else 4
    for i in range(n):
        t = (phase + i / n) % 1
        a = TAU * (t * 1.5 + i / n)
        x, y = 32 + math.cos(a) * (10 + t * 12), 58 - t * 52
        layer = front if math.sin(a) > 0 else back
        c = hexrgb("#ffffff", int(240 * (1 - t * 0.7)))
        put(layer, x, y, c); put(layer, x + 1, y, c); put(layer, x + 1, y - 1, c); put(layer, x + 1, y - 2, c); put(layer, x + 2, y - 2, c)


def tunda_mangrove(back, front, full, phase):
    """Mangrove roots arching at the feet, in a grey-green fog; with the whole set, the roots climb
    high round the figure and pale eyes open and blink among them."""
    d = ImageDraw.Draw(back)
    h = 30 if full else 12
    for k, x0 in enumerate((4, 14, 50, 60)):
        top = 62 - h + (k % 2) * 4
        mid = (x0 + 32) / 2 if x0 < 32 else (x0 + 32) / 2
        d.line([(x0, 62), (x0 + (6 if x0 < 32 else -6), top)], fill=hexrgb("#14504a"), width=2)
        d.line([(x0 + (6 if x0 < 32 else -6), top), (mid, top - 3), (mid + (4 if x0 < 32 else -4), 62)], fill=hexrgb("#2a7a68"))
    for i in range(10 if full else 6):
        x = ((i * 11 + phase * 30) % 72) - 4
        for dx in range(-4, 5):
            put(front if i % 2 else back, x + dx, 56 + (i % 3), hexrgb("#c8f0e0", int(70 * (1 - abs(dx) / 5))))
    if full:
        blink = int(phase * 10)
        for k, (ex, ey) in enumerate(((10, 30), (52, 26), (8, 44), (56, 40))):
            if (blink + k * 3) % 10 not in (0, 1):
                put(back, ex, ey, hexrgb("#ffe8dc")); put(back, ex + 2, ey, hexrgb("#ffe8dc"))


def mahamudra_sky(back, front, full, phase):
    """A disc of clear blue sky behind the head, small clouds forming in it and dissolving again without
    trace; with the whole set, the open sky fills the whole background, clouds coming and going."""
    d = ImageDraw.Draw(back)
    if full:
        for k, col in enumerate(("#1a5aa8", "#4a96e0", "#a8d4ff")):
            d.ellipse([1 + k * 3, -6 + k * 3, 62 - k * 3, 50 - k * 3], fill=hexrgb(col, 60 + k * 25))
        box = (8, 0, 56, 40)
    else:
        d.ellipse([14, 0, 50, 30], fill=hexrgb("#4a96e0", 120), outline=hexrgb("#a8d4ff", 160))
        box = (17, 3, 47, 27)
    n = 5 if full else 2
    for i in range(n):
        t = (phase + i / n) % 1
        life = math.sin(t * math.pi)  # comes, stays a little, goes
        cx = box[0] + 4 + ((i * 17 + t * 6) % max(1, box[2] - box[0] - 8))
        cy = box[1] + 4 + (i * 11) % max(1, box[3] - box[1] - 8)
        for k in range(-2, 3):
            blob(back, cx + k * 2, cy + (abs(k) == 2), 1, hexrgb("#ffffff", int(220 * life)))


def candileja_fire(back, front, full, phase):
    """Three balls of fire circling the figure (the Candileja is three heads aflame); with the whole
    set, they leave trails of sparks, and the dry grass glows where they pass."""
    n = 3
    for i in range(n):
        a = TAU * (phase + i / n)
        x, y = 32 + math.cos(a) * 22, 36 + math.sin(a) * 7 - math.cos(a * 2) * 4
        layer = front if math.sin(a) > 0 else back
        blob(layer, x, y, 2, hexrgb("#e04a0e"))
        blob(layer, x, y, 1, hexrgb("#ff9a2a"))
        put(layer, x, y - 1, hexrgb("#fff0a0"))
        put(layer, x, y - 3, hexrgb("#ff9a2a", 200))
        if full:
            for k in range(1, 7):
                b = a - k * 0.12
                put(front if math.sin(b) > 0 else back, 32 + math.cos(b) * 22, 36 + math.sin(b) * 7 - math.cos(b * 2) * 4 - (k % 2), hexrgb("#ffd060", int(200 * (1 - k / 7))))
    if full:
        for x in range(6, 59):
            if (x * 5 + int(phase * 20)) % 9 < 2:
                put(back, x, 61, hexrgb("#e04a0e", 180))


def sombreron_hat(back, front, full, phase):
    """A ring of black chain links turning round the feet (he rides with dogs on chains); with the whole
    set, an enormous black hat hangs over the figure and two pairs of red dog eyes glow at its feet."""
    for i in range(14):
        a = TAU * (phase + i / 14)
        x, y = 32 + math.cos(a) * 20, 58 + math.sin(a) * 4
        layer = front if math.sin(a) > 0 else back
        c = hexrgb("#6a625a") if i % 2 else hexrgb("#3a3430")
        put(layer, x, y, c); put(layer, x + 1, y, c)
    if full:
        d = ImageDraw.Draw(back)
        bob = round(math.sin(phase * TAU))
        d.ellipse([2, 6 + bob, 62, 16 + bob], fill=hexrgb("#0a0808", 230))
        d.polygon([(20, 11 + bob), (24, -2 + bob), (40, -2 + bob), (44, 11 + bob)], fill=hexrgb("#0a0808", 240))
        d.line([(22, 8 + bob), (42, 8 + bob)], fill=hexrgb("#8a0a0a"))
        for ex in (8, 52):
            if int(phase * 6) % 6 != 2:
                put(back, ex, 56, hexrgb("#ff2020")); put(back, ex + 2, 56, hexrgb("#ff2020"))


def marimba_waves(back, front, full, phase):
    """A marimba's wooden bars laid at the feet, lighting up one after another as if struck; with the
    whole set, Pacific waves roll behind and a humpback whale's tail rises out of them."""
    if full:
        d = ImageDraw.Draw(back)
        for x in range(64):
            y = 44 + math.sin(x / 6 + phase * TAU) * 2
            d.line([(x, y), (x, 52)], fill=hexrgb("#12407a", 160))
            put(back, x, y, hexrgb("#7ac0f0", 200))
        rise = math.sin(phase * math.pi)
        ty = 44 - rise * 16
        d.line([(48, 46), (48, ty + 4)], fill=hexrgb("#0a1a3a"), width=3)
        d.polygon([(48, ty + 4), (38, ty - 2), (42, ty + 3)], fill=hexrgb("#0a1a3a"))
        d.polygon([(48, ty + 4), (58, ty - 2), (54, ty + 3)], fill=hexrgb("#0a1a3a"))
    hit = int(phase * 8) % 8
    for k in range(8):
        x0 = 6 + k * 7
        col = "#fff4d0" if k == hit else "#b8862e" if k % 2 else "#7a4a16"
        for x in range(x0, x0 + 5):
            for y in range(58 - k // 2, 62):
                put(front if k in (0, 7) else back, x, y, hexrgb(col))


def huitaca_dance(back, front, full, phase):
    """Petals whirling round the figure in a dancing ring (Huitaca, of feasts and dance); with the whole
    set, the full moon rises behind and an owl's wings open wide across it."""
    if full:
        d = ImageDraw.Draw(back)
        d.ellipse([20, 0, 44, 24], fill=hexrgb("#fff48a", 160))
        spread = 0.6 + 0.4 * math.sin(phase * TAU)
        for side in (-1, 1):
            for k in range(14):
                x = 32 + side * (4 + k * 2 * spread)
                for j in range(5 - k // 4):
                    put(back, x, 18 + k * 0.6 + j, hexrgb("#6a2a8e" if (k + j) % 3 else "#e8a8f8", 210))
    n = 14 if full else 8
    for i in range(n):
        a = TAU * (phase * 1.5 + i / n)
        h = 40 - (i % 4) * 8
        x, y = 32 + math.cos(a) * 21, h + math.sin(a) * 5
        layer = front if math.sin(a) > 0 else back
        col = ("#e8a8f8", "#fff48a", "#b05ad0")[i % 3]
        put(layer, x, y, hexrgb(col)); put(layer, x + 1, y + 1, hexrgb(col))


def canocristales_river(back, front, full, phase):
    """The river of five colours at the feet: red, yellow, green, blue and black water flowing past in
    stripes; with the whole set, the colours rise round the figure in waves and spray glitters."""
    cols = ("#e0403a", "#f0e040", "#3ac08a", "#2a7ac0", "#14100c")
    h = 12 if full else 6
    for row in range(h):
        y = 62 - row
        for x in range(64):
            k = int((x + phase * 40 + row * 3 + math.sin(x / 5 + row) * 2) / 5) % 5
            put(front if row < 2 else back, x, y, hexrgb(cols[k], 200 - row * (8 if full else 14)))
    if full:
        for i in range(10):
            t = (phase + i / 10) % 1
            x = 32 + math.sin(i * 2.4) * 24
            put(front if i % 2 else back, x, 50 - math.sin(t * math.pi) * 18, hexrgb("#ffffff", int(240 * math.sin(t * math.pi))))
            put(back, x, 49 - math.sin(t * math.pi) * 18, hexrgb(cols[i % 5], 200))


def dzogchen_thigle(back, front, full, phase):
    """A sphere of five-coloured light behind the figure, rings of blue, white, yellow, red and green
    breathing out from the centre; with the whole set, small spheres of the same light float all round,
    and rays spread out from the great one."""
    d = ImageDraw.Draw(back)
    cols = ("#2a5ae0", "#ffffff", "#f0d030", "#e03030", "#30c050")
    R = 24 if full else 16
    for k, col in enumerate(cols):
        r = R - k * (R / 5.5) + math.sin(phase * TAU) * 1
        d.ellipse([32 - r, 30 - r, 32 + r, 30 + r], outline=hexrgb(col, 210), width=2 if full else 1)
    d.ellipse([30, 28, 34, 32], fill=hexrgb("#0a1840"))
    if full:
        for i in range(16):
            a = TAU * (i / 16 + phase / 8)
            for rr in range(26, 32, 2):
                put(back, 32 + math.cos(a) * rr, 30 + math.sin(a) * rr, hexrgb(cols[i % 5], 150))
        for i in range(8):
            t = (phase + i / 8) % 1
            x, y = 32 + math.sin(i * 2.6) * 26, 62 - t * 58
            layer = front if i % 2 else back
            blob(layer, x, y, 1, hexrgb(cols[i % 5], int(230 * math.sin(t * math.pi))))
            put(layer, x, y, hexrgb("#ffffff", int(255 * math.sin(t * math.pi))))


ANIMS = {"idle": 1, "side": 1, "slash": 6, "thrust": 8, "shoot": 13, "spellcast": 7, "hurt": 6}
SOUTH = 2


def custom_looks():
    """[(key, atlas_layers, anim_layers)]: the standing frame for the portrait and a strip per animation."""
    out = []
    for sid in ("laguna", "condor", "origen", "cienaga", "mohan", "yogui", "vajra", "averno", "trueno", "sol", "guardian",
                "bachue", "nevado", "vientos", "montana", "kalachakra", "luzclara",
                "osario", "tairona", "dorado", "relampago", "vigilia", "pacto", "firmamento", "madreagua", "caiman", "andes", "arhuaco",
                "galeon", "frailejon", "bochica", "bufeo", "llanero", "madremonte", "silbon", "tunda", "mahamudra", "candileja", "sombreron", "marimba", "huitaca", "canocristales", "dzogchen"):
        for variant in ("part", "full"):
            full = variant == "full"
            # the atlas keeps 128px cells with the 64px frame in the middle (see build_lpc.py)
            def cell(im):
                c = Image.new("RGBA", (128, 128))
                c.paste(im, (32, 32))
                return c
            atlas_layers = [(z, {SOUTH: cell(im)}) for z, im in ornament(sid, full, 0)]
            rows_by_z = {}
            for a, n in ANIMS.items():
                strips = {}
                for i in range(n):
                    for z, im in ornament(sid, full, i / n if n > 1 else 0):
                        strips.setdefault(z, Image.new("RGBA", (n * F, F))).paste(im, (i * F, 0))
                for z, strip in strips.items():
                    rows_by_z.setdefault(z, {})[a] = (strip, F, n)
            anim_layers = [(z, rows) for z, rows in rows_by_z.items()]
            out.append((f"orn:{sid}:{variant}", atlas_layers, anim_layers))
    return out


MOCHILA_Z = 120

# Tutusoma de las Nieves: the white cotton hat of Arhuaco men, rising to a soft point (the snowy peaks).
TUTUSOMA = mirror("""
........oo
......ooWW
.....owwwW
....ovwwwW
....ovwwww
...ovwwwww
...ovwwwww
...ovwwwww
...ovwwwww
..ovwwwwww
..ovwwwwww
..ovwwwwww
..ovwwwwww
..ovssssss
...ooooooo
""")
TUT_PAL = {"o": "#4a443a", "v": "#cfc6b4", "w": "#f4f0e6", "W": "#ffffff", "s": "#b8ae9a"}


def reanchor(layers, alayers, pic, at, z, keep=False):
    """New layers drawing `pic` in every frame, placed by `at(bbox)` from where the template layers are
    in that frame (so it follows the head or the waist through every animation). keep: keep the template too."""
    def frame(src):
        bb = src.getbbox()
        out = Image.new("RGBA", src.size)
        if bb:
            out.alpha_composite(pic, at(bb))
        return out
    def union(frames):
        im = None
        for f in frames:
            im = f.copy() if im is None else (im.alpha_composite(f) or im)
        return im
    rows = {}
    for _, fr in layers:
        for r, im in fr.items():
            rows.setdefault(r, []).append(im)
    new = [(z, {r: frame(union(ims)) for r, ims in rows.items()})]
    strips = {}
    for _, rs in alayers:
        for a, (im, fs, n) in rs.items():
            strips.setdefault(a, []).append((im, fs, n))
    anew = {}
    for a, lst in strips.items():
        im0, fs, n = lst[0]
        tpl = union([x for x, f2, _ in lst if f2 == fs and x.size == im0.size])
        strip = Image.new("RGBA", tpl.size)
        for i in range(n):
            strip.alpha_composite(frame(tpl.crop((i * fs, 0, (i + 1) * fs, fs))), (i * fs, 0))
        anew[a] = (strip, fs, n)
    return (layers if keep else []) + new, (alayers if keep else []) + [(z, anew)]


def arhuaco_piece(base, layers, alayers):
    """build_lpc.py: the set's own shapes over the generator's, frame by frame."""
    if base == "yelmocatatumbo":  # the tutusoma where the helmet would be: its lower edge on the forehead
        pic = paint(TUTUSOMA, TUT_PAL)
        return reanchor(layers, alayers, pic, lambda bb: ((bb[0] + bb[2]) // 2 - pic.width // 2, bb[1] + 11 - pic.height + 1), 130)
    if base == "cintocatatumbo":  # the mochila hangs from the sash, its strap over the shoulder
        pic = paint(MOCHILA_WORN, ARHUACO)
        return reanchor(layers, alayers, pic, lambda bb: (bb[0] + 1 - 11, bb[1] - 14), MOCHILA_Z, keep=True)
    return layers, alayers


if __name__ == "__main__":
    # a preview sheet to look at: icons at 6x and the ornaments on a plain silhouette
    import sys
    icons = custom_icons()
    S = 6
    W = sum(im.width * S + 12 for im in icons.values())
    H = max(im.height for im in icons.values()) * S + 16
    sheet = Image.new("RGBA", (max(W, 4 * (F * 2 + 8)), H + 16 * 70 * 2), (40, 34, 30, 255))
    x = 6
    for k, im in icons.items():
        big = im.resize((im.width * S, im.height * S), Image.NEAREST)
        sheet.alpha_composite(big, (x, 8))
        x += big.width + 12
    y = H + 8
    for sid, variant, phases in [(s, v, 4) for s in (sys.argv[2].split(",") if len(sys.argv) > 2 else ("cienaga", "mohan", "yogui", "vajra", "averno", "trueno", "sol", "guardian")) for v in ("part", "full")]:
        x = 6
        for i in range(phases):
            fr = Image.new("RGBA", (F, F))
            layers = ornament(sid, variant == "full", i / phases)
            fr.alpha_composite(layers[0][1])
            d = ImageDraw.Draw(fr)  # a stand-in body
            d.rectangle([24, 13, 40, 28], fill=(90, 70, 60, 255))
            d.rectangle([21, 29, 43, 62], fill=(70, 60, 80, 255))
            fr.alpha_composite(layers[1][1])
            sheet.alpha_composite(fr.resize((F * 2, F * 2), Image.NEAREST), (x, y))
            x += F * 2 + 8
        y += 70 * 2
    sheet.save(sys.argv[1] if len(sys.argv) > 1 else "custom_art_preview.png")
    print({k: im.size for k, im in icons.items()})
