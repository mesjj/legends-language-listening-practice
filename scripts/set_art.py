"""The sets from 68 to 200 on the high-level bases: a look of its own for every piece, and the effects the top tiers wear.

Used by build_lpc.py. Every piece of these sets has its own combination of generator layers
(RECIPES, by set and base: None = the set's main colours, "accent" = its accent), so no two pieces
share a shape the way they did when every Astral helmet was the same wizard's hat; where the generator
has nothing right (a llanero's hat, the Sombrerón's) the shape is drawn here and placed frame by frame
over a stand-in layer (custom_art.reanchor). Then effects worked out from each piece's own pixels,
frame by frame, so they follow every animation: a glow round the outline, flames licking up off the
top edges, drips, leaves, sparks, and pieces drawn bigger than life. The mythic sets get the most.

Icons: the worn look gives helmets, armour, weapons and shields theirs; gloves, boots, belts and
rings are a few pixels on the figure, so each gets a drawn icon (piece_icons).
"""
import math
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from custom_art import hexrgb, paint, reanchor

A = "accent"

RECIPES = {
    "galeon": {  # a drowned pirate captain, sea-green and doubloon gold
        "yelmosombra": [("hat_tricorne_captain", None), ("hat_tricorne_captain_skull", A)],
        "corazasombra": [("legs_pantaloons", None), ("torso_clothes_longsleeve_laced", A), ("torso_jacket_frock_lapel", None), ("torso_clothes_blouse_longsleeve", A), ("neck_jabot", A)],
        "sableluna": [("weapon_sword_saber", A)],
        "rodelaluna": [("shield_heater_revised_wood", None), ("shield_heater_revised_trim", A)],
        "guantessombra": [("arms_gloves", A), ("wrists_cuffs_lace", None)],
        "cintosombra": [("belt_double", None), ("buckles", A)],
    },
    "frailejon": {  # páramo: grey-green fuzz like a frailejón's leaves, mist
        "capiroteastral": [("hat_hood_cloth", None), ("neck_scarf", A)],
        "vestiduraastral": [("legs_cuffed", None), ("torso_clothes_longsleeve2_cardigan", None), ("shoulders_mantal", A)],
        "varasombra": [("weapon_magic_simple", A)],
        "guantesastral": [("arms_gloves", None)],
        "zapatillasastral": [("feet_boots_fold", None)],
        "fajinastral": [("belt_sash", A)],
    },
    "bochica": {  # the old weaver: undyed cotton, the falls' blue
        "capiroteastral": [("hat_hood_sack_cloth", None), ("hat_headband_thick_rune", A)],
        "vestiduraastral": [("torso_clothes_longsleeves2", None), ("torso_aprons_apron", A), ("cape_solid", None)],
        "varasombra": [("weapon_magic_loop", A)],
        "guantesastral": [("arms_bracers", None), ("wrists_cuffs", A)],
        "zapatillasastral": [("feet_socks_high", A), ("feet_sandals", None)],
    },
    "bufeo": {  # the enchanted river dolphin, a gentleman in white at the fiesta
        "capiroteastral": [("hat_formal_tophat", "light")],
        "vestiduraastral": [("legs_formal", "light"), ("torso_clothes_longsleeve_formal", "light"), ("torso_clothes_blouse_longsleeve", "light"), ("torso_jacket_collared", A), ("neck_bowtie", A), ("wings_dragonfly_transparent", A)],
        "lanzaastral": [("weapon_polearm_spear", A)],
        "fajinastral": [("belt_formal", None), ("belt_waistband", None), ("buckles", A)],
        "guantesastral": [("arms_gloves", A), ("arms_hands_ring_stud", None)],
        "zapatillasastral": [("feet_shoes_basic", None)],
    },
    "llanero": {  # the plains: a white liquiliqui, a hat drawn here, a lance
        "yelmoluna": [("hat_headband_tied", None)],  # stand-in for the hat
        "mantoluna": [("legs_pants2", None), ("torso_clothes_longsleeve2_buttoned", None)],
        "tridenteluna": [("weapon_polearm_longspear", A)],
        "brazalesluna": [("wrists_cuffs", A), ("arms_bracers", None)],
        "zapatosluna": [("feet_sandals", A)],
        "cordonluna": [("belt_leather2", A)],
    },
    "madremonte": {  # the forest's guardian, all moss, leaves and bark
        "yelmoluna": [("hat_headband_tied", None)],  # stand-in for the crown of moss
        "mantoluna": [("legs_skirts_slit", None), ("torso_clothes_sleeveless2", A), ("cape_tattered", None)],
        "varasombra": [("weapon_magic_gnarled", A)],
        "brazalesluna": [("arms_armour", A), ("wrists_cuffs_lace", None)],
        "zapatosluna": [("feet_boots_basic", A)],
        "cordonluna": [("belt_obi_knot_left", None)],
    },
    "silbon": {  # the whistler: long, thin, ragged, a sack of bones
        "yelmosombra": [("hat_headband_tied", None)],  # stand-in for the torn sombrero
        "corazasombra": [("legs_shorts", None), ("torso_clothes_shortsleeves2", None), ("torso_bandages", A)],
        "mangualsombra": [("weapon_blunt_club", A)],
        "guantessombra": [("arms_armour", A)],
        "pezunassombra": [("feet_shoes_ghillies", None)],
        "cintosombra": [("belt_mage", None), ("belt_formal", None)],
    },
    "tunda": {  # the mangrove's shape-shifter: one leg like a chocolate whisk
        "yelmoluna": [("hat_bandana2", None), ("hat_headband_tied", A)],
        "mantoluna": [("legs_skirts_plain", None), ("torso_clothes_longsleeves_cuffed", None), ("torso_clothes_corset", A)],
        "tridenteluna": [("weapon_polearm_trident", A)],
        "cordonluna": [("belt_sash_narrow", None), ("belt_waistband", A)],
        "brazalesluna": [("arms_gloves", None), ("wrists_cuffs", A)],
        "zapatosluna": [("feet_socks_ankle", A), ("prosthesis_peg_leg", None)],
    },
    "mahamudra": {  # the great seal: open sky, light as cloud
        "capiroteastral": [("hairext_topknot_long", None), ("hat_headband_hairtie", A)],
        "vestiduraastral": [("legs_pants", A), ("legs_widepants", A), ("torso_clothes_longsleeve_scoop", None), ("cape_trim", A), ("wings_pixie_transparent", None)],
        "arcoastral": [("weapon_ranged_bow_normal", A)],
        "fajinastral": [("belt_obi", None), ("belt_obi_knot_right", A)],
        "guantesastral": [("wrists_cuffs_lace", A)],
        "zapatillasastral": [("feet_slippers", None)],
    },
    "candileja": {  # the three balls of fire on the plains
        "capiroteastral": [("hat_magic_wizard", None), ("hat_magic_wizard_belt", A)],
        "vestiduraastral": [("legs_hose", None), ("torso_clothes_shortsleeve", A), ("torso_clothes_vest_open", None), ("torso_clothes_corset", None)],
        "espadaastral": [("weapon_sword_arming", A)],
        "escudoastral": [("shield_heater_paint", None), ("shield_heater_pattern_chevron", A)],
        "guantesastral": [("arms_gloves", None), ("arms_bracers", A)],
        "zapatillasastral": [("feet_boots_rim", None)],
    },
    "sombreron": {  # the black rider of the fairs: a hat bigger than he is
        "capiroteastral": [("hat_headband_tied", None)],  # stand-in for the huge hat
        "vestiduraastral": [("legs_formal_striped", None), ("torso_clothes_longsleeves", None), ("torso_jacket_trench", None), ("cape_solid", A)],
        "mandoblesombra": [("weapon_sword_longsword_alt", A)],
        "guantesastral": [("arms_armour", None), ("wrists_cuffs", A)],
        "zapatillasastral": [("feet_boots_revised", None), ("feet_plate_toe", A)],
        "cintosombra": [("belt_leather", None), ("buckles", A)],
    },
    "marimba": {  # the Pacific: chonta wood, a singer's head wrap, the sea
        "capiroteastral": [("hat_headband_tied", None)],  # stand-in for the head wrap
        "vestiduraastral": [("legs_shorts_short", None), ("legs_skirt_belle", None), ("torso_clothes_tshirt_scoop", A), ("torso_clothes_blouse", A), ("neck_necklace_beaded_small", A)],
        "arcoastral": [("weapon_ranged_bow_recurve", None)],
        "guantesastral": [("arms_hands_ring_stud", A), ("wrists_cuffs_lace", None)],
        "zapatillasastral": [("feet_socks_tabi", None)],
        "fajinastral": [("belt_sash_narrow", A), ("belt_robe", None)],
    },
    "huitaca": {  # the feast, the dance and the owl
        "capiroteastral": [("hat_formal_tiara", A)],
        "vestiduraastral": [("legs_leggings2", None), ("torso_clothes_sleeveless2_scoop", None), ("torso_clothes_tunic_sara", None), ("wings_feathered", A)],
        "espadaastral": [("weapon_sword_rapier", A)],
        "escudoastral": [("shield_heater_revised_paint", None), ("shield_heater_revised_pattern_lozengy", A)],
        "guantesastral": [("arms_gloves", A), ("wrists_cuffs_lace", None)],
        "zapatillasastral": [("feet_shoes_revised", None)],
    },
    "canocristales": {  # the river of five colours over stone
        "yelmosombra": [("hat_helmet_spangenhelm", None), ("hat_accessory_plumage", A)],
        "corazasombra": [("legs_leggings", None), ("torso_armour_leather", None), ("shoulders_pauldrons", A)],
        "lanzaastral": [("weapon_polearm_dragonspear", A)],
        "cintosombra": [("belt_loose", A)],
        "guantesastral": [("arms_bracers", A), ("arms_hands_ring_stud", None)],
        "zapatillasastral": [("feet_armour", None)],
    },
    "dzogchen": {  # the great perfection: space blue and the five lights, everything ablaze
        "capiroteastral": [("hat_formal_crown", A)],
        "vestiduraastral": [("legs_skirts_legion", None), ("torso_clothes_longsleeve2_vneck", None), ("shoulders_epaulets", A), ("wings_lunar", A)],
        "espadaastral": [("weapon_sword_glowsword", A)],
        "escudoastral": [("shield_round", A)],
        "guantesastral": [("arms_gloves", A), ("wrists_cuffs", None)],
        "zapatillasastral": [("feet_plate_toe_thick", None)],
    },
}


RECIPES.update({  # the older sets on band pieces (68-130), reworked the same way
    "osario": {  # the Day of the Dead's dancing skeleton: a catrín in a top hat, marigolds
        "yelmohueso": [("hat_formal_tophat", None), ("facial_mask_plain", "light")],
        "petohueso": [("legs_formal_striped", None), ("torso_clothes_longsleeve", None), ("torso_jacket_frock_lapel", None), ("neck_cravat", A)],
        "guadanahueso": [("weapon_polearm_scythe", A)],
        "brazaleshueso": [("arms_hands_ring_stud", None), ("wrists_cuffs_lace", A)],
        "botashueso": [("feet_shoes_revised", None), ("feet_socks_high", A)],
    },
    "tairona": {  # the Sierra's terraces: a woven manta, a gold-fronted band with plumes
        "yelmoesmeralda": [("hat_headband_thick_rune", A), ("hat_accessory_plumage_centurion", None)],
        "cotaesmeralda": [("legs_skirts_plain", None), ("torso_clothes_sleeveless", None), ("neck_necklace_beaded_large", A)],
        "estoqueesmeralda": [("weapon_sword_arming", A)],
        "guantesesmeralda": [("arms_bracers", A)],
        "fajaesmeralda": [("belt_sash", A)],
    },
    "dorado": {  # the Zipa on the raft, all gold dust; a diadem of rays drawn here
        "yelmotumbaga": [("hat_headband_tied", None)],  # stand-in for the diadem
        "corazatumbaga": [("legs_skirts_legion", None), ("torso_armour_legion", None), ("cape_trim", A), ("neck_necklace_beaded_large", A)],
        "baculotumbaga": [("weapon_magic_diamond", A)],
        "grebastumbaga": [("feet_sandals", None), ("feet_plate_toe", None)],
        "cintotumbaga": [("belt_loose", A)],
    },
    "madreagua": {  # the river's mother: long golden hair, a tiara, scales
        "yelmotumbaga": [("hair_xlong_wavy", A), ("hat_formal_tiara", None)],
        "corazacatatumbo": [("legs_skirts_slit", None), ("torso_chainmail", None), ("neck_necklace_beaded_small", A), ("cape_solid", A)],
        "lanzatumbaga": [("weapon_polearm_spear", None)],
        "guantestumbaga": [("arms_gloves", None), ("wrists_cuffs", A)],
        "botascatatumbo": [("feet_boots_fold", None)],
    },
    "relampago": {  # Catatumbo's lightning that never stops: a winged great helm, storm plate
        "yelmocatatumbo": [("hat_helmet_barbarian_nasal", None), ("hat_accessory_wings", A)],
        "corazacatatumbo": [("legs_armour", None), ("torso_armour_plate", None), ("shoulders_pauldrons", A), ("cape_tattered", None)],
        "martillocatatumbo": [("weapon_blunt_mace", A)],
        "guantescatatumbo": [("arms_armour", None), ("wrists_cuffs", A)],
        "botascatatumbo": [("feet_boots_rim", None), ("feet_plate_toe_thick", A)],
    },
    "vigilia": {  # the moon's watcher: a pale veil, moon earrings, a silver-clasped cloak
        "yelmoluna": [("hat_hood_hijab", "light"), ("facial_earrings_moon", A)],
        "mantoluna": [("legs_skirt_straight", None), ("legs_pants2", None), ("torso_clothes_longsleeve_scoop", "light"), ("cape_trim", A), ("neck_capeclip", A)],
        "arcoluna": [("weapon_ranged_bow_normal", A)],
        "cordonluna": [("belt_sash_narrow", A)],
        "brazalesluna": [("arms_gloves", "light"), ("wrists_cuffs_lace", A)],
        "zapatosluna": [("feet_slippers", None)],
    },
    "pacto": {  # the devil's bargain: horns, bat wings, a blade on fire
        "yelmosombra": [("hat_helmet_barbarian_viking", None), ("hat_accessory_horns_upward", A)],
        "corazasombra": [("legs_pantaloons", None), ("torso_clothes_longsleeves", None), ("torso_jacket_tabard", A), ("cape_tattered", None), ("wings_bat", None)],
        "mandoblesombra": [("weapon_sword_longsword", A)],
        "guantessombra": [("arms_armour", None), ("arms_hands_ring_stud", A)],
        "pezunassombra": [("feet_hoofs", None)],
        "cintosombra": [("belt_double", None), ("belt_sash_narrow", A)],
    },
    "caiman": {  # the man who became a caiman: its jaws for a hat drawn here, scales, a tail
        "yelmosombra": [("hat_headband_tied", None)],  # stand-in for the jaws
        "corazasombra": [("legs_leggings", None), ("torso_armour_legion", None), ("shoulders_legion", A)],
        "mangualsombra": [("weapon_blunt_flail", A)],
        "escudoastral": [("shield_scutum", None), ("shield_scutum_trim", A)],
        "guantessombra": [("arms_gloves", None), ("arms_bracers", A)],
        "pezunassombra": [("feet_boots_basic", None)],
    },
    "firmamento": {  # the first sky: a towering star hat, monarch wings of stars, a comet for a sword
        "capiroteastral": [("hat_magic_celestial_moon", None), ("hat_magic_celestial_moon_trim", A)],
        "vestiduraastral": [("legs_pants", None), ("torso_clothes_robe", None), ("torso_clothes_longsleeve2", None), ("cape_trim", A), ("wings_monarch_edge", A)],
        "espadaastral": [("weapon_sword_saber", "light")],
        "escudoastral": [("shield_round", None)],
        "guantesastral": [("arms_gloves", A)],
        "zapatillasastral": [("feet_slippers", A)],
    },
    "andes": {  # the high road: a chullo drawn here, a red ruana, snow
        "capiroteastral": [("hat_headband_tied", None)],  # stand-in for the chullo
        "vestiduraastral": [("legs_pants2", A), ("torso_clothes_longsleeve2", A), ("torso_jacket_tabard", None), ("shoulders_mantal", None)],
        "arcoastral": [("weapon_ranged_bow_recurve", A)],
        "guantesastral": [("arms_gloves", A)],
        "zapatillasastral": [("feet_sandals", None), ("feet_socks_ankle", A)],
        "fajinastral": [("belt_sash", None)],
    },
})


# ---------------------------------------------------------------- per-frame effects
# layers: [(z, {row: 128px cell})]; alayers: [(z, {anim: (strip, frame size, frames)})]

def _union(imgs):
    out = None
    for im in imgs:
        out = im.copy() if out is None else (out.alpha_composite(im) or out)
    return out


def _per_frame(layers, alayers, fn, z):
    """A new layer made by fn(mask image, phase) from the union of these layers, frame by frame."""
    rows = {}
    for _, fr in layers:
        for r, im in fr.items():
            rows.setdefault(r, []).append(im)
    new = (z, {r: fn(_union(ims), 0.0) for r, ims in rows.items()})
    strips = {}
    for _, rs in alayers:
        for a, (im, fs, n) in rs.items():
            strips.setdefault(a, []).append((im, fs, n))
    anew = {}
    for a, lst in strips.items():
        im0, fs, n = lst[0]
        tpl = _union([x for x, f2, _ in lst if f2 == fs and x.size == im0.size])
        strip = Image.new("RGBA", tpl.size)
        for i in range(n):
            strip.alpha_composite(fn(tpl.crop((i * fs, 0, (i + 1) * fs, fs)), i / max(1, n)), (i * fs, 0))
        anew[a] = (strip, fs, n)
    return new, (z, anew)


def _alpha(im):
    return im.getchannel("A").load(), im.size


def glow(cols, width=1):
    """A halo round the outline, behind the piece, its colours cycling along it frame by frame."""
    cs = [hexrgb(c) for c in cols]
    def fn(src, phase):
        solid = src.getchannel("A").point(lambda v: 255 if v > 60 else 0)
        ring = ImageChops.subtract(solid.filter(ImageFilter.MaxFilter(2 * width + 1)), solid)
        w, h = src.size
        key = (w, h, len(cs), int(phase * 12))
        if key not in _STRIPES:
            im = Image.new("RGBA", (w, h))
            px = im.load()
            for y in range(h):
                for x in range(w):
                    px[x, y] = cs[int((x + y + phase * 12) // 2) % len(cs)]
            _STRIPES[key] = im
        out = Image.new("RGBA", (w, h))
        out.paste(_STRIPES[key], (0, 0), ring.point(lambda v: 210 if v else 0))
        return out
    return fn, -1


_STRIPES = {}


def flames(cols, height=6, density=1.0):
    """Flames licking up off every top edge of the piece, flickering frame by frame."""
    cs = [hexrgb(c) for c in cols]  # from the root to the tips
    def fn(src, phase):
        a, (w, h) = _alpha(src)
        out = Image.new("RGBA", (w, h))
        px = out.load()
        tick = int(phase * 64)
        for x in range(w):
            for y in range(1, h):
                if a[x, y] > 60 and a[x, y - 1] <= 60:
                    rnd = random.Random(x * 7919 + y * 104729 + tick * 31)
                    if rnd.random() > density:
                        continue
                    L = max(1, int(height * (0.35 + 0.65 * rnd.random())))
                    sway = rnd.choice((-1, 0, 0, 1))
                    for k in range(L):
                        yy, xx = y - 1 - k, x + (sway if k > L // 2 else 0)
                        if 0 <= yy < h and 0 <= xx < w and a[xx, yy] <= 60:
                            c = cs[min(len(cs) - 1, k * len(cs) // L)]
                            px[xx, yy] = c[:3] + (int(255 * (1 - k / (L + 1)) ** 0.7),)
        return out
    return fn, +1


def specks(cols, every=9, drop=0):
    """Specks scattered over the piece (leaves, drops, sparks); drop > 0: they fall a little per frame."""
    cs = [hexrgb(c) for c in cols]
    def fn(src, phase):
        a, (w, h) = _alpha(src)
        out = Image.new("RGBA", (w, h))
        px = out.load()
        shift = int(phase * drop * 8)
        for y in range(h):
            for x in range(w):
                hh = ((x * 374761393 + y * 668265263) ^ 0x5bd1e995) & 0xffffffff  # scattered, not a lattice (a lattice reads as stripes)
                hh = ((hh ^ (hh >> 13)) * 1274126177) & 0xffffffff
                if a[x, y] > 60 and (hh >> 16) % every == 0:
                    yy = y + shift
                    if 0 <= yy < h:
                        px[x, yy] = cs[(x + y) % len(cs)]
        return out
    return fn, +1


def scaled(layers, alayers, s, anchor="bottom"):
    """The piece drawn s times bigger, from its bottom centre (a hat stays on the head) or its centre."""
    def big(im):
        bb = im.getbbox()
        if not bb:
            return im
        piece = im.crop(bb)
        nw, nh = max(1, round(piece.width * s)), max(1, round(piece.height * s))
        piece = piece.resize((nw, nh), Image.NEAREST)
        cx = (bb[0] + bb[2]) / 2
        out = Image.new("RGBA", im.size)
        if anchor == "bottom":
            out.alpha_composite(piece, (int(round(cx - nw / 2)), max(0, bb[3] - nh)))
        else:
            cy = (bb[1] + bb[3]) / 2
            out.alpha_composite(piece, (int(round(cx - nw / 2)), max(0, int(round(cy - nh / 2)))))
        return out
    nl = [(z, {r: big(im) for r, im in fr.items()}) for z, fr in layers]
    na = []
    for z, rs in alayers:
        d = {}
        for a, (im, fs, n) in rs.items():
            strip = Image.new("RGBA", im.size)
            for i in range(n):
                strip.alpha_composite(big(im.crop((i * fs, 0, (i + 1) * fs, fs))), (i * fs, 0))
            d[a] = (strip, fs, n)
        na.append((z, d))
    return nl, na


def add_fx(layers, alayers, fx):
    fn, side = fx
    zs = [z for z, _ in layers] or [50]
    z = (min(zs) - 1) if side < 0 else (max(zs) + 1)
    nl, na = _per_frame(layers, alayers, fn, z)
    return layers + [nl], alayers + [na]


FIVE = ("#2a5ae0", "#ffffff", "#f0d030", "#e03030", "#30c050")
FX = {  # (set, base) or set -> effects, in order; "big": (scale, anchor)
    "bufeo": [("glow", ("#ff9ac8", "#7ae8ff"))],
    ("bufeo", "capiroteastral"): [("big", (1.3, "bottom")), ("flames", (("#ffffff", "#7ae8ff", "#2a8ad0"), 7, 0.5))],
    ("bufeo", "lanzaastral"): [("flames", (("#ffffff", "#ffb0d8", "#e05a9a", "#7ae8ff"), 7, 0.9))],
    "mahamudra": [("glow", ("#a8d4ff", "#ffffff"))],
    ("mahamudra", "capiroteastral"): [("big", (1.45, "bottom"))],
    ("mahamudra", "arcoastral"): [("flames", (("#ffffff", "#a8d4ff", "#4a96e0"), 6, 0.8))],
    ("mahamudra", "zapatillasastral"): [("specks", (("#ffffff", "#e8f4ff"), 3, 0))],
    "dzogchen": [("glow", FIVE)],
    ("dzogchen", "capiroteastral"): [("big", (1.35, "bottom")), ("flames", (("#ffffff", "#f0d030", "#e03030"), 8, 0.9))],
    ("dzogchen", "espadaastral"): [("big", (1.3, "center")), ("flames", (("#ffffff", "#f0d030", "#e03030", "#30c050", "#2a5ae0"), 9, 1.0))],
    ("dzogchen", "escudoastral"): [("flames", (("#ffffff", "#30c050", "#2a5ae0"), 6, 0.8))],
    ("dzogchen", "zapatillasastral"): [("flames", (("#ffffff", "#f0d030", "#e03030"), 6, 1.0))],
    ("dzogchen", "guantesastral"): [("flames", (("#ffffff", "#f0d030", "#e03030"), 4, 1.0))],
    # the legendary sets: one strong effect each
    ("galeon", "corazasombra"): [("specks", (("#a8e0ff", "#ffffff"), 11, 1))],
    ("galeon", "sableluna"): [("glow", ("#7ae8c0",))],
    ("madremonte", "mantoluna"): [("specks", (("#8ac85a", "#3e8a2a", "#c89a62"), 7, 0))],
    ("madremonte", "varasombra"): [("specks", (("#8ac85a", "#3e8a2a"), 4, 0))],
    "sombreron": [],
    ("sombreron", "mandoblesombra"): [("glow", ("#ff2020", "#8a0a0a"))],
    ("candileja", "capiroteastral"): [("flames", (("#fff0a0", "#ff9a2a", "#e04a0e"), 5, 0.7))],
    ("candileja", "espadaastral"): [("flames", (("#fff0a0", "#ff9a2a", "#e04a0e"), 6, 0.9))],
    ("candileja", "escudoastral"): [("flames", (("#ff9a2a", "#e04a0e"), 4, 0.6))],
    ("canocristales", "lanzaastral"): [("glow", ("#e0403a", "#f0e040", "#3ac08a", "#2a7ac0"))],
    ("huitaca", "capiroteastral"): [("specks", (("#e8a8f8", "#fff48a", "#ffffff"), 3, 0))],
    # the older sets: the first sky is mythic and goes all out; the others get one or two touches
    "firmamento": [("glow", ("#3e58c0",))],
    ("firmamento", "capiroteastral"): [("specks", (("#fff0a0", "#ffffff"), 11, 0))],
    ("firmamento", "vestiduraastral"): [("specks", (("#fff0a0", "#ffffff"), 9, 0))],
    ("firmamento", "espadaastral"): [("big", (1.3, "center")), ("flames", (("#ffffff", "#fff0a0", "#a0b8ff", "#3e58c0"), 9, 1.0))],
    ("firmamento", "escudoastral"): [("specks", (("#fff0a0", "#ffffff"), 11, 0))],
    ("firmamento", "zapatillasastral"): [("flames", (("#ffffff", "#fff0a0", "#a0b8ff"), 6, 1.0))],
    ("firmamento", "guantesastral"): [("flames", (("#ffffff", "#a0b8ff"), 4, 0.8))],
    ("pacto", "mandoblesombra"): [("flames", (("#ffd0a0", "#ff7040", "#e0201a", "#4a0404"), 8, 1.0))],
    ("pacto", "yelmosombra"): [("flames", (("#ff7040", "#e0201a"), 4, 0.6))],
    ("osario", "guadanahueso"): [("specks", (("#ff9a1a", "#ffd060"), 4, 1))],
    ("osario", "yelmohueso"): [("specks", (("#ff9a1a", "#ffd060"), 14, 0))],
    ("dorado", "corazatumbaga"): [("specks", (("#ffe07a", "#fffbe0"), 5, 1))],
    ("dorado", "yelmotumbaga"): [("glow", ("#ffe07a",))],
    ("dorado", "baculotumbaga"): [("glow", ("#ffe07a", "#7ae8dc"))],
    ("tairona", "estoqueesmeralda"): [("glow", ("#f8d868",))],
    ("madreagua", "lanzatumbaga"): [("specks", (("#8ae0d4", "#eafffa"), 4, 1))],
    ("madreagua", "corazacatatumbo"): [("specks", (("#8ae0d4", "#2a9a98"), 8, 1))],
    ("relampago", "martillocatatumbo"): [("glow", ("#4ae0ff", "#ffffff")), ("specks", (("#ffffff", "#bff8ff"), 3, 0))],
    ("relampago", "yelmocatatumbo"): [("specks", (("#bff8ff", "#ffffff"), 5, 0))],
    ("vigilia", "arcoluna"): [("glow", ("#b8a0ec", "#ffffff"))],
    ("caiman", "mangualsombra"): [("specks", (("#9ab45a", "#4e7030"), 5, 1))],
    ("andes", "vestiduraastral"): [("specks", (("#ffffff", "#eef2f8"), 6, 1))],
    ("andes", "capiroteastral"): [("big", (1.2, "bottom")), ("specks", (("#ffffff",), 7, 1))],
    ("caiman", "yelmosombra"): [("big", (1.4, "bottom"))],
}


def _fx_list(sid, base):
    return FX.get(sid, []) + FX.get((sid, base), [])


# ---------------------------------------------------------------- hats drawn here
LLANERO_HAT = """
...........HHHHHHHH...........
..........HhhhhhhhhH..........
.........HhhhhhhhhhhH.........
.........HhhhhhhhhhhH.........
.........HhhhhhhhhhhH.........
.........HhhhhhhhhhhH.........
.........HhhhhhhhhhhH.........
.........HbbbbbbbbbbH.........
.HHHHHHHHHHHHHHHHHHHHHHHHHHHH.
HhhhhhhhhhhhhhhhhhhhhhhhhhhhhH
.HHHHHHHHHHHHHHHHHHHHHHHHHHHH.
"""
SILBON_HAT = """
.............HHHHHHH............
...........HHhhhhhhhH...........
..........Hhhhhhhh.hhH..........
..........HhhhhhhhhhhhH.........
.........Hhhhh.hhhhhhhH.........
.........HhhhhhhhhhhhhH.........
.........HhhhhhhhhhhhhH.........
.........HbbbbbbbbbbbbH.........
...HHHHHHHHHHHHHHHHHHHHHHHHHHH..
.HHhh.hhhhhhhhhhhhhhhhhhh.hhhhH.
HHhhhhhhhh.hhhhhhhhhhhhhhhhhh.HH
.HHH..HHHHHHH.HHHHHHH...HHHHHH..
"""
SOMBRERON_HAT = """
....................HHHHHHHHHHHHHHHH....................
..................HHgggggggggggggggHH...................
.................HhghhhhhhhhhhhhhhhhhH..................
.................HghhhhhhhhhhhhhhhhhhH..................
................HghhhhhhhhhhhhhhhhhhhhH.................
................HghhhhhhhhhhhhhhhhhhhhH.................
................HghhhhhhhhhhhhhhhhhhhhH.................
................HghhhhhhhhhhhhhhhhhhhhH.................
................HghhhhhhhhhhhhhhhhhhhhH.................
................HghhhhhhhhhhhhhhhhhhhhH.................
................HghhhhhhhhhhhhhhhhhhhhH.................
................HghhhhhhhhhhhhhhhhhhhhH.................
................HbbbbbbbbbbbbbbbbbbbbbH.................
................HbbbbbbbbbbbbbbbbbbbbbH.................
.......HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH.......
...HHHHgggggggggggggggggggggggggggggggggggggggggggHHHH...
.HHhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhHH.
HhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhH
.HHhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhHH.
...HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH...
"""
MOSS_CROWN = """
...L......l......L......l...
..LLl....lLl....lLL....lLL..
...Ll...LlL.l...Ll...lLl....
.L.lL..lLl..lL.lLl..lL..L...
.lLlLl.Ll.L.lLlLl.L.lLl.lL..
..lLlLlLlLlLlLlLlLlLlLlLl...
LlMmMMmMMmMMmMMmMMmMMmMMmMlL
MmmMmmMmmMmmMmmMmmMmmMmmMmmM
.MMMMMMMMMMMMMMMMMMMMMMMMMM.
"""
HEADWRAP = """
........WWWWWWWW........
......WWwwwwyywwwWW.....
.....WwwwyyyyyyywwwW....
....WwwyyrrrrrryyywwW...
....WyyrrrrwwrrrrryyW...
....WrrrwwwwwwwwrrrrW...
....WwwwyyyyyyyyywwwW...
....WyyyrrrrrrrrryyyW...
....WrrrwwwwwwwwwrrrW...
....WwwyyyyyyyyyyywwW...
.....WWWWWWWWWWWWWWW....
"""


ZIPA_DIADEM = """
..H....H....H....H....H..
.HYH..HYH..HYH..HYH..HYH.
.HYH..HYH.HYYYH.HYH..HYH.
.HyH.HYyYHHYyYHHYyYH.HyH.
.HyYHHYyYHHYyYHHYyYHHYyH.
HYYYYYYYYYYYYYYYYYYYYYYYH
HyyeyyyyyeyyyeyyyyyeyyyyH
HHHHHHHHHHHHHHHHHHHHHHHHH
"""
CAIMAN_JAWS = """
.....HHH............HHH.....
....HGYGH..........HGYGH....
....HGkGHHHHHHHHHHHHGkGH....
...HGGGGGGlGGlGGlGGGGGGGH...
..HGgGGlGGGGGGGGGGGGlGGgGH..
..HGGgGGGGgGGGGGGgGGGGgGGH..
.HGgGGGGlGGGGllGGGGlGGGGgGH.
.HGGgGGGGGGGGGGGGGGGGGGgGGH.
HGGGGGGGGGGGGGGGGGGGGGGGGGGH
HHtHtHtHtHtHtHtHtHtHtHtHtHHH
.Ht.t.t.t.t.t.t.t.t.t.t.tH..
"""
CHULLO = """
...........WW...........
..........WWWW..........
...........HH...........
..........HrrH..........
........HHrwwrHH........
......HHrrrrrrrrHH......
.....HrwrwrwrwrwrwH.....
....HrrrrrrrrrrrrrrH....
...HwwwwwwwwwwwwwwwwH...
..HrrwrrwrrwrrwrrwrrrH..
..HrrrrrrrrrrrrrrrrrrH..
..HwwwwwwwwwwwwwwwwwwH..
..Hrrr............rrrH..
..Hrwr............rwrH..
..Hrrr............rrrH..
..Hwww............wwwH..
...HH..............HH...
...W................W...
"""


def _hat(grid, pal, lift=0):
    """The picture, and where: centred on the stand-in headband, its lower edge `lift` rows below the band's top."""
    pic = paint(grid, pal)
    return pic, lambda bb, p=pic: ((bb[0] + bb[2]) // 2 - p.width // 2, bb[1] + lift - p.height)


def custom_head(sid, main, acc):
    """(picture, where) for the sets whose hat is drawn here; colours from the set's stops."""
    if sid == "llanero":
        return _hat(LLANERO_HAT, {"H": acc[0], "h": acc[2], "b": "#d83a2a"}, 3)
    if sid == "silbon":
        return _hat(SILBON_HAT, {"H": main[0], "h": main[3], "b": acc[2]}, 3)
    if sid == "sombreron":
        return _hat(SOMBRERON_HAT, {"H": "#000000", "h": main[2], "g": main[4], "b": acc[3]}, 3)
    if sid == "madremonte":
        return _hat(MOSS_CROWN, {"M": main[1], "m": main[3], "l": main[4], "L": acc[3]}, 2)
    if sid == "dorado":
        return _hat(ZIPA_DIADEM, {"H": acc[0], "Y": main[4], "y": main[3], "e": "#2ac060"}, 3)
    if sid == "caiman":
        return _hat(CAIMAN_JAWS, {"H": main[0], "g": main[2], "G": main[3], "l": main[4], "Y": acc[3], "k": "#000000", "t": "#fffbe8"}, 5)
    if sid == "andes":
        return _hat(CHULLO, {"H": main[0], "r": main[3], "w": acc[4], "W": acc[5]}, 9)
    if sid == "marimba":
        return _hat(HEADWRAP, {"W": main[1], "w": main[3], "y": acc[3], "r": "#d83a2a"}, 3)
    return None


HEAD_BASES = {"capiroteastral", "yelmosombra", "yelmoluna", "yelmohueso", "yelmoesmeralda", "yelmotumbaga", "yelmocatatumbo"}


def piece(sid, base, layers, alayers, main, acc):
    """build_lpc.py: the set's drawn hat and effects over the generator's layers, frame by frame."""
    if base in HEAD_BASES:
        h = custom_head(sid, main, acc)
        if h:
            pic, at = h
            layers, alayers = reanchor(layers, alayers, pic, at, 130)
    for kind, *args in _fx_list(sid, base):
        if kind == "big":
            s, anchor = args[0]
            layers, alayers = scaled(layers, alayers, s, anchor)
        elif kind == "glow":
            layers, alayers = add_fx(layers, alayers, glow(*args))
        elif kind == "flames":
            layers, alayers = add_fx(layers, alayers, flames(*args[0]))
        elif kind == "specks":
            layers, alayers = add_fx(layers, alayers, specks(*args[0]))
    return layers, alayers


# ---------------------------------------------------------------- icons for the small pieces
# Gloves, boots, belts and rings are a few pixels on the figure, so their icons are drawn: a shape
# (O outline, D/M/m main dark/mid/light, A/a accent, . empty) and a motif painted on its X mark.
SHAPES = {
    "gauntlet": """
......OOOOO.....
.....OmmmmMO....
....OmMMMMMMO...
...OmMMMMMMMMO..
..OOmMMMMXMMMDO.
.OAaOMMMMMMMMDO.
.OAAOMMMMMMMDDO.
.OAAOMMMMMMDDO..
.OAaODMMMMDDO...
.OAAOODDDDDO....
.OAAO.OOOOO.....
..OO............
""",
    "glove": """
.....O.O.O......
....OmOmOmO.....
....OmOmOmO.O...
....OMOMOMOOmO..
....OMMMMMMOMO..
....OMMMMMMMMO..
....OMMMXMMMDO..
....OMMMMMMMDO..
....ODMMMMMDDO..
.....OAAAAAAO...
.....OaAaAaAO...
.....OOOOOOOO...
""",
    "bracer": """
....OOOOOOOO....
...OaAAAAAAaO...
...OMMMMMMMMO...
...OmMMMMMMDO...
...OmMMXMMMDO...
...OmMMMMMMDO...
...OAAAAAAAAO...
...OmMMMMMMDO...
...OmMMMMMMDO...
...OaAAAAAAaO...
....OOOOOOOO....
""",
    "mitt": """
....O.O.O.O.....
....OmOmOmOO....
...OOMOMOMOmO...
...OMMMMMMMMO...
...OMMMMMMMMO...
...OMMMXMMMDO...
...OMMMMMMMDO...
...ODMMMMMDDO...
...OAAAAAAAAO...
...OAaAaAaAaO...
...OOOOOOOOOO...
""",
    "claw": """
..a...a...a.....
..Oa..Oa..Oa....
..OMO.OMO.OMO...
..OMMOMMMOMMO.a.
..OMMMMMMMMMOOa.
..OMMMMMMMMMMMO.
..OMMMMXMMMMMDO.
..OMMMMMMMMMDDO.
..ODMMMMMMMDDO..
...OAAAAAAAAO...
...OOOOOOOOOO...
""",
    "tallboot": """
...OOOOOOO......
...OaAAAAaO.....
...OMMMMMMO.....
...OmMMMMDO.....
...OmMXMMDO.....
...OmMMMMDO.....
...OmMMMMDO.....
...OmMMMMDOOO...
...OmMMMMMMMDO..
...OMMMMMMMMMDO.
...ODDDDDDDDDDO.
...OOOOOOOOOOOO.
""",
    "shortboot": """
................
................
....OOOOOO......
....OaAAaO......
....OmMMDO......
....OmXMDOOOO...
....OmMMMMMMDO..
....OMMMMMMMMDO.
....ODDDDDDDDDO.
....OOOOOOOOOOO.
""",
    "sandal": """
................
................
................
.....OO...OO....
....OAAO.OAAO...
...OA.OAOA.AO...
..OAOOOXOOOOAO..
.OmMMMMMMMMMMDO.
.ODDDDDDDDDDDDO.
.OOOOOOOOOOOOOO.
""",
    "slipper": """
................
................
..............O.
....OOOOOO...OaO
...OmMMMMMOOOMO.
...OmMMXMMMMMMO.
...OMMMMMMMMMDO.
...ODDDDDDDDDO..
...OOOOOOOOOO...
""",
    "sabaton": """
...OOOOOOO......
...OAAAAAAO.....
...OMMMMMMO.....
...OmMMMMDO.....
...OAAAAAAO.....
...OmMXMMDOOO...
...OAAAAAAMMMO..
...OmMMMMMMMMDO.
...ODDDDDDDDDDO.
...OOOOOOOOOOOO.
""",
    "whisk": """
.......OO.......
......OmMO......
......OmMO......
......OmMO......
......OAAO......
......OmMO......
.....OXmMDO.....
....OmO..ODO....
...OmO.OO.ODO...
...OMOOmMOODO...
....OMMMMMDO....
.....OOOOOO.....
""",
    "buckle": """
................
....OOOOOO......
OOOOOAAAAOOOOOOO
mMMMOA..AOMMMMMm
MMMMOA.XAOMMMMMM
DMMMOA..AOMMMMMD
OOOOOAAAAOOOOOOO
....OOOOOO......
""",
    "sash": """
................
OOOOOOOOOOOOOOOO
mMMMMMOOOMMMMMMm
MMMMMOAXAOMMMMMM
DDDDDDOAOODDDDDD
OOOOOOOMMOOOOOOO
......OMMMO.....
......OMODMO....
.....OMO.ODO....
.....OAO..OAO...
""",
    "rope": """
.....OOOOOO.....
...OOmMMMMDOO...
..OmMOOOOOODMO..
.OmMO......ODMO.
.OMO..OXXO..OMO.
.OMO..OXXO..OMO.
.ODMO......OMDO.
..ODMOOOOOOMDO..
...OODDDDDDOOAO.
.....OOOOOO..OaO
""",
    "cord": """
................
OOOOOOOOOOOOOOOO
mMMMMMMMMMMMMMMm
DDDDDDOXODDDDDDD
OOOOOOOAOOOOOOOO
......OAO.......
.....OAaAO......
.....OAAAO......
.....OaAaO......
......OOO.......
""",
    "bag": """
................
OOOOOOOOOOOOOOOO
mMMMMMMMMMMMMMMm
DDDDDDDDDDDDDDDD
OOOOOOAOOOOOOOOO
.....OAAO.......
....OmMMMO......
...OmMMXMMO.....
...OMMMMMMO.....
...ODMMMMDO.....
....ODDDDO......
.....OOOO.......
""",
    "pendant": """
.O..........O...
.OO........OO...
..Oa......aO....
...Oa....aO.....
....OaaaaO......
.....OAAO.......
....ODMMDO......
...ODMMMMDO.....
...OMMXMMMO.....
...ODMMMmDO.....
....ODDDDO......
.....OOOO.......
""",
    "hoof": """
................
....OOOOOO......
...ODMMMmO......
...ODMMMmO......
...ODMMMMO......
..ODMMXMMMO.....
..ODMMMMMMO.....
.ODMMMMMMMMO....
.OAAAAOAAAAO....
.OaaaaOaaaaO....
.OOOOOOOOOOO....
................
""",
    "ring": """
.....OOOO.......
....OaXXaO......
....OAXXAO......
...OOOAAOOO.....
..OmMO..OMDO....
..OMO....ODO....
..OMO....ODO....
..ODMO..ODDO....
...ODDOODDO.....
....OOOOOO......
""",
}
MOTIFS = {  # 3x3 or so, drawn from the X's top-left
    "coin": ["yYy", "YyY", "yYy"], "leaf": [".g.", "gGg", ".G."], "flame": [".r.", "ryr", "yYy"],
    "wave": ["b.b", "BbB", "..."], "note": [".W", ".W", "WW"], "eye": [".W.", "WkW", ".W."],
    "star": [".Y.", "YYY", ".Y."], "flower": [".p.", "pyp", ".p."], "shell": ["WwW", "wWw", ".w."],
    "spiral": ["WWW", "W.W", "WW."], "bone": ["W.W", ".W.", "W.W"], "chain": ["kWk", "W.W", "kWk"],
    "sun": ["y.y", ".Y.", "y.y"], "drop": [".b.", "bBb", ".b."], "cloud": [".WW", "WWW", "..."],
    "skull": ["WWW", "kWk", ".W."], "feather": ["..p", ".pP", "pP."], "five": ["bWy", "rgr", "yWb"],
    "anchor": [".k.", "kkk", "k.k"], "moss": ["g.G", ".Gg", "Gg."], "ember": ["r.y", ".Y.", "y.r"],
    "moon": [".W.", "W..", ".W."], "bolt": [".YY", "YY.", "Y.."], "cross": ["W.W", ".W.", "W.W"], "dot": [".W.", "WYW", ".W."],
}
MOTIF_COL = {"y": "#d8a830", "Y": "#ffe07a", "g": "#3e8a2a", "G": "#8ac85a", "r": "#e04a0e", "b": "#2a7ac0",
             "B": "#7ac0f0", "W": "#ffffff", "w": "#d8d0c0", "k": "#141010", "p": "#b05ad0", "P": "#e8a8f8"}

ICONS = {  # (set, base): (shape, motif)
    ("galeon", "guantessombra"): ("gauntlet", "coin"), ("galeon", "cintosombra"): ("buckle", "anchor"),
    ("frailejon", "guantesastral"): ("mitt", "moss"), ("frailejon", "zapatillasastral"): ("tallboot", "drop"),
    ("frailejon", "fajinastral"): ("sash", "flower"),
    ("bochica", "guantesastral"): ("bracer", "spiral"), ("bochica", "zapatillasastral"): ("sandal", "sun"),
    ("bochica", "anillo"): ("ring", "drop"),
    ("bufeo", "guantesastral"): ("glove", "wave"), ("bufeo", "zapatillasastral"): ("slipper", "shell"),
    ("bufeo", "fajinastral"): ("buckle", "drop"),
    ("llanero", "brazalesluna"): ("bracer", "sun"), ("llanero", "zapatosluna"): ("sandal", "note"),
    ("llanero", "cordonluna"): ("rope", "coin"),
    ("madremonte", "brazalesluna"): ("claw", "leaf"), ("madremonte", "zapatosluna"): ("shortboot", "leaf"),
    ("madremonte", "cordonluna"): ("cord", "moss"),
    ("silbon", "guantessombra"): ("claw", "bone"), ("silbon", "pezunassombra"): ("shortboot", "bone"),
    ("silbon", "cintosombra"): ("bag", "skull"),
    ("tunda", "brazalesluna"): ("mitt", "shell"), ("tunda", "zapatosluna"): ("whisk", "eye"),
    ("tunda", "cordonluna"): ("cord", "eye"),
    ("mahamudra", "guantesastral"): ("glove", "cloud"), ("mahamudra", "zapatillasastral"): ("slipper", "cloud"),
    ("mahamudra", "fajinastral"): ("sash", "moon"),
    ("candileja", "guantesastral"): ("gauntlet", "flame"), ("candileja", "zapatillasastral"): ("tallboot", "ember"),
    ("sombreron", "guantesastral"): ("gauntlet", "chain"), ("sombreron", "zapatillasastral"): ("sabaton", "cross"),
    ("sombreron", "cintosombra"): ("buckle", "skull"),
    ("marimba", "guantesastral"): ("glove", "note"), ("marimba", "zapatillasastral"): ("slipper", "wave"),
    ("marimba", "fajinastral"): ("sash", "note"),
    ("huitaca", "guantesastral"): ("glove", "feather"), ("huitaca", "zapatillasastral"): ("sandal", "flower"),
    ("canocristales", "guantesastral"): ("bracer", "five"), ("canocristales", "zapatillasastral"): ("sabaton", "drop"),
    ("canocristales", "cintosombra"): ("rope", "five"),
    ("dzogchen", "guantesastral"): ("claw", "five"), ("dzogchen", "zapatillasastral"): ("sabaton", "five"),
    # the older sets
    ("osario", "brazaleshueso"): ("bracer", "bone"), ("osario", "botashueso"): ("shortboot", "flower"),
    ("tairona", "guantesesmeralda"): ("bracer", "spiral"), ("tairona", "fajaesmeralda"): ("sash", "sun"),
    ("dorado", "grebastumbaga"): ("sandal", "coin"), ("dorado", "cintotumbaga"): ("buckle", "star"),
    ("dorado", "amuleto"): ("pendant", "sun"),
    ("madreagua", "guantestumbaga"): ("gauntlet", "wave"), ("madreagua", "botascatatumbo"): ("tallboot", "drop"),
    ("madreagua", "sortija"): ("ring", "shell"),
    ("relampago", "guantescatatumbo"): ("gauntlet", "bolt"), ("relampago", "botascatatumbo"): ("sabaton", "bolt"),
    ("vigilia", "brazalesluna"): ("glove", "moon"), ("vigilia", "zapatosluna"): ("slipper", "moon"),
    ("vigilia", "cordonluna"): ("cord", "star"),
    ("pacto", "guantessombra"): ("claw", "flame"), ("pacto", "pezunassombra"): ("hoof", "ember"),
    ("pacto", "cintosombra"): ("buckle", "flame"),
    ("caiman", "guantessombra"): ("claw", "eye"), ("caiman", "pezunassombra"): ("shortboot", "moss"),
    ("firmamento", "guantesastral"): ("glove", "star"), ("firmamento", "zapatillasastral"): ("slipper", "star"),
    ("andes", "guantesastral"): ("mitt", "flower"), ("andes", "zapatillasastral"): ("sandal", "dot"),
    ("andes", "fajinastral"): ("sash", "five"),
}


def draw_icon(shape, motif, main, acc):
    pal = {"O": "#0c0a08", "D": main[1], "M": main[2], "m": main[4], "A": acc[2], "a": acc[4], "X": main[2]}
    rows = SHAPES[shape].strip("\n").split("\n")
    im = paint(SHAPES[shape], pal)
    for y, r in enumerate(rows):
        x = r.find("X")
        if x >= 0:
            px = im.load()
            for dy, mr in enumerate(MOTIFS[motif]):
                for dx, ch in enumerate(mr):
                    if ch != "." and 0 <= x + dx - 1 < im.width and 0 <= y + dy - 1 < im.height and px[x + dx - 1, y + dy - 1][3]:
                        px[x + dx - 1, y + dy - 1] = hexrgb(MOTIF_COL[ch])
            break
    # twice the size, so they sit with the other icons (worn looks are cropped at about this scale)
    return im.resize((im.width * 2, im.height * 2), Image.NEAREST)


def piece_icons(stops):
    """{"item:<base>:<set>": icon} for the drawn small pieces; the mythic ones burn and glow."""
    out = {}
    for (sid, base), (shape, motif) in ICONS.items():
        main, acc = stops[sid]
        im = draw_icon(shape, motif, main, acc)
        im2 = Image.new("RGBA", (im.width + 8, im.height + 12))
        im2.alpha_composite(im, (4, 10))
        for kind, *args in _fx_list(sid, base):
            if kind == "glow":
                fn, _ = glow(*args)
                g = fn(im2, 0.0)
                g.alpha_composite(im2)
                im2 = g
            elif kind == "flames":
                fn, _ = flames(*args[0])
                im2.alpha_composite(fn(im2, 0.0))
        out[f"item:{base}:{sid}"] = im2.crop(im2.getbbox())
    return out


# ---------------------------------------------------------------- the sets' magic undershirts
# A whole set melts at the alembic into its undershirt; each set's is this shirt in the set's colours
# (the triples in build_scenes.NECKLACES: body, trim, shine). Its bag icon here, its sprite on the
# Camisetas rack in build_scenes.
SHIRT = """
...OOO....OOO...
.OOlccOttOccdOO.
OlccccctttcccddO
OlccccccccccccdO
OOOlcccccccccdOO
..OlcccccccccdO.
..OlccceeecccdO.
..OlcccceccccdO.
..OlcccccccccdO.
..OltttttttttdO.
..OOOOOOOOOOOOO.
"""


def _mix(a, b, t):
    a, b = hexrgb(a), hexrgb(b)
    return "#%02x%02x%02x" % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def shirt_pic(body, trim, shine):
    return paint(SHIRT, {"O": _mix(body, "#000000", 0.75), "c": body, "l": _mix(body, "#ffffff", 0.35), "d": _mix(body, "#000000", 0.35),
                         "t": trim, "e": shine})


def shirt_icons(triples):
    """{"item:camiseta:<set>": icon} for every set, twice the size like the other drawn icons."""
    out = {}
    for sid, (body, trim, shine) in triples.items():
        im = shirt_pic(body, trim, shine)
        out[f"item:camiseta:{sid}"] = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
    return out
