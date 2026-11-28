"""The art of the 59 sets of levels 204-400 (scripts/new_sets_400.py), for build_lpc.py.

Like the sets from 138 to 200 (set_art.py): every piece gets its own combination of generator layers in
the set's colours (two ramps, main and accent, made from two colours here), the heads of a few are drawn
(set_art's hat pictures), the small pieces get drawn icons (shape + motif), and the top tiers wear
effects: the mythic sets a glow on every piece, flames on the weapon and a bigger crown; the legendary
ones a strong touch on the weapon and one more; the ancestral ones one touch.

Imported by set_art.py at its end, which merges NEW_RECIPES, NEW_FX, NEW_ICONS, NEW_HEADS into its
own tables; build_lpc.py merges NEW_STOPS into SET_BAND_STOPS.
"""
from new_sets_400 import SETS

A = "accent"
L_ = "light"


def ramp(h):
    """Six stops, dark to light, through the colour h (as the hand-made ramps in build_lpc.py)."""
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    def mix(t, to):
        return "#%02x%02x%02x" % tuple(round(c + (to - c) * t) for c in (r, g, b))
    return [mix(0.88, 0), mix(0.62, 0), mix(0.32, 0), mix(0.0, 0), mix(0.45, 255), mix(0.85, 255)]


HEADS = {
    "crown": [("hat_formal_crown", A)],
    "tiara": [("hat_formal_tiara", A)],
    "hood": [("hat_hood_cloth", None)],
    "sack": [("hat_hood_sack_cloth", None), ("hat_headband_thick_rune", A)],
    "wizard": [("hat_magic_wizard", None), ("hat_magic_wizard_belt", A)],
    "moon": [("hat_magic_celestial_moon", None), ("hat_magic_celestial_moon_trim", A)],
    "viking": [("hat_helmet_barbarian_viking", None)],
    "nasal": [("hat_helmet_barbarian_nasal", None), ("hat_accessory_plumage", A)],
    "winged": [("hat_helmet_spangenhelm", None), ("hat_accessory_wings", A)],
    "horned": [("hat_helmet_barbarian_nasal", None), ("hat_accessory_horns_upward", A)],
    "crest": [("hat_helmet_spangenhelm", None), ("hat_accessory_plumage_centurion", A)],
    "veil": [("hat_hood_hijab", None), ("facial_earrings_moon", A)],
    "bandana": [("hat_bandana2", None)],
    "topknot": [("hairext_topknot_long", None), ("hat_headband_hairtie", A)],
    "tied": [("hat_headband_tied", A)],
    "mask": [("facial_mask_plain", None), ("hat_headband_thick_rune", A)],
    "longhair": [("hair_xlong_wavy", None), ("hat_formal_tiara", A)],
    "stand": [("hat_headband_tied", None)],  # under a hat drawn in set_art (NEW_HEADS)
}
BODIES = {
    "robe": [("legs_pants", None), ("torso_clothes_robe", None), ("shoulders_mantal", A)],
    "monk": [("legs_widepants", None), ("torso_clothes_longsleeve2_vneck", None), ("shoulders_mantal", A), ("neck_necklace_beaded_large", A)],
    "plate": [("legs_armour", None), ("torso_armour_plate", None), ("shoulders_pauldrons", A), ("cape_trim", A)],
    "legion": [("legs_skirts_legion", None), ("torso_armour_legion", None), ("shoulders_legion", A)],
    "chain": [("legs_pants2", None), ("torso_chainmail", None), ("torso_jacket_tabard", A)],
    "leather": [("legs_leggings", None), ("torso_armour_leather", None), ("shoulders_epaulets", A)],
    "dancer": [("legs_skirts_slit", None), ("torso_clothes_corset", A), ("neck_necklace_beaded_small", A), ("cape_tattered", None)],
    "dress": [("legs_skirt_belle", None), ("torso_clothes_blouse_longsleeve", None), ("neck_necklace_chain", A)],
    "tunic": [("legs_hose", None), ("torso_clothes_tunic_sara", None), ("cape_solid", A)],
    "weaver": [("legs_cuffed", None), ("torso_clothes_longsleeve2_cardigan", None), ("torso_aprons_apron", A)],
    "sea": [("legs_pantaloons", None), ("torso_clothes_shortsleeve", None), ("neck_scarf", A)],
    "noble": [("legs_formal", None), ("torso_jacket_frock_lapel", None), ("torso_clothes_blouse_longsleeve", A), ("neck_cravat", A)],
    "ghost": [("legs_skirt_straight", L_), ("torso_clothes_longsleeve_scoop", L_), ("cape_tattered", None)],
    "yogi": [("legs_shorts", None), ("torso_bandages", A), ("neck_necklace_beaded_large", A)],
    "trench": [("legs_pants", None), ("torso_jacket_trench", None), ("neck_capeclip", A), ("cape_solid", None)],
    "vest": [("legs_shorts_short", None), ("torso_clothes_vest_open", None), ("neck_necklace_beaded_large", A)],
    "cotton": [("legs_pants2", L_), ("torso_clothes_longsleeve2_buttoned", L_), ("neck_scarf", A)],
    "skirt": [("legs_skirts_plain", None), ("torso_clothes_sleeveless2_scoop", None), ("neck_necklace_beaded_large", A), ("shoulders_mantal", A)],
}
WINGS = {"feather": ("wings_feathered", A), "lunar": ("wings_lunar", A), "bat": ("wings_bat", None),
         "pixie": ("wings_pixie_transparent", A), "monarch": ("wings_monarch_edge", A), "dragonfly": ("wings_dragonfly_transparent", A)}
GLOVES = {"gloves": [("arms_gloves", None)], "bracers": [("arms_bracers", None), ("wrists_cuffs", A)], "armour": [("arms_armour", None)],
          "cuffs": [("arms_gloves", A), ("wrists_cuffs_lace", None)], "rings": [("arms_bracers", A), ("arms_hands_ring_stud", None)]}
FEET = {"sandals": [("feet_sandals", None)], "boots": [("feet_boots_fold", None)], "plate": [("feet_plate_toe_thick", None)],
        "slippers": [("feet_slippers", A)], "shoes": [("feet_shoes_revised", None)], "tabi": [("feet_socks_tabi", A), ("feet_sandals", None)],
        "rim": [("feet_boots_rim", None)], "ghillies": [("feet_shoes_ghillies", None)], "hoofs": [("feet_hoofs", None)], "high": [("feet_socks_high", A), ("feet_sandals", None)]}
BELTS = {"sash": [("belt_sash", A)], "obi": [("belt_obi", A), ("belt_obi_knot_left", None)], "rope": [("belt_robe", A)], "double": [("belt_double", None), ("buckles", A)],
         "mage": [("belt_mage", A)], "leather": [("belt_leather2", None), ("buckles", A)], "loose": [("belt_loose", A)], "narrow": [("belt_sash_narrow", A)]}
SHIELDS = {"kite": [("shield_kite", None)], "round": [("shield_round", A)], "scutum": [("shield_scutum", None), ("shield_scutum_trim", A)],
           "heater": [("shield_heater_revised_wood", None), ("shield_heater_revised_trim", A)], "paint": [("shield_heater_revised_paint", A), ("shield_heater_revised_trim", None)],
           "lozenge": [("shield_heater_revised_pattern_lozengy", A), ("shield_heater_revised_trim", None)]}
WEAPON_OF = {  # by base, a few shapes each (picked by the set's place in the list)
    "espadaastral": ["weapon_sword_arming", "weapon_sword_longsword", "weapon_sword_glowsword", "weapon_sword_rapier", "weapon_sword_longsword_alt"],
    "lanzaastral": ["weapon_polearm_spear", "weapon_polearm_dragonspear", "weapon_polearm_longspear"],
    "arcoastral": ["weapon_ranged_bow_recurve", "weapon_ranged_bow_normal"],
    "mangualsombra": ["weapon_blunt_flail", "weapon_blunt_mace"],
    "mandoblesombra": ["weapon_sword_longsword", "weapon_sword_longsword_alt"],
    "varasombra": ["weapon_magic_gnarled", "weapon_magic_crystal", "weapon_magic_loop", "weapon_magic_diamond", "weapon_magic_simple"],
    "sableluna": ["weapon_sword_saber"],
    "tridenteluna": ["weapon_polearm_trident", "weapon_polearm_longspear"],
    "arcoluna": ["weapon_ranged_bow_normal", "weapon_ranged_bow_recurve"],
}
ICON_OF = {"gloves": "glove", "bracers": "bracer", "armour": "gauntlet", "cuffs": "glove", "rings": "bracer",
           "sandals": "sandal", "boots": "tallboot", "plate": "sabaton", "slippers": "slipper", "shoes": "shortboot", "tabi": "sandal",
           "rim": "shortboot", "ghillies": "shortboot", "hoofs": "hoof", "high": "sandal",
           "sash": "sash", "obi": "sash", "rope": "rope", "double": "buckle", "mage": "sash", "leather": "buckle", "loose": "cord", "narrow": "cord"}

# id: (head, body, wings, gloves, feet, belt, shield, main colour, accent colour, motif, effect colours)
LOOK = {
    "teyuna": ("sack", "weaver", None, "bracers", "sandals", "rope", None, "#4e6a34", "#c8a848", "moss", ("#a8d070", "#e0f0b0")),
    "tatacoa": ("bandana", "vest", None, "gloves", "boots", "leather", None, "#a84a24", "#e8b060", "sun", ("#ff9a3a", "#ffd0a0")),
    "sanagustin": ("mask", "legion", None, "armour", "plate", "double", "scutum", "#7a7660", "#c8c0a0", "eye", ("#e8e0c0", "#ffffff")),
    "tierradentro": ("hood", "tunic", None, "bracers", "shoes", "loose", None, "#6a2a22", "#e8dcc8", "spiral", ("#e04a3a",)),
    "taraverde": ("tiara", "dress", None, "cuffs", "slippers", "sash", None, "#2a8a4a", "#e8c040", "flower", ("#7af0a0", "#ffffff")),
    "chia": ("stand", "skirt", None, "cuffs", "slippers", "narrow", None, "#4a5a8a", "#e0e8f8", "moon", ("#c8d8ff", "#ffffff")),
    "sue": ("stand", "legion", None, "bracers", "sandals", "sash", None, "#c88a1a", "#ffe070", "sun", ("#ffd040", "#fff8d0")),
    "catedralsal": ("hood", "robe", None, "gloves", "boots", "rope", None, "#8a9aa8", "#ffffff", "cross", ("#e8f4ff", "#ffffff")),
    "choco": ("bandana", "sea", None, "bracers", "sandals", "sash", None, "#1e6a62", "#8ae0d0", "drop", ("#8ae0d0",)),
    "milarepa": ("topknot", "cotton", None, "rings", "sandals", "rope", None, "#c8c8c0", "#7a5a3a", "note", ("#ffffff", "#e8f0ff")),
    "yurupari": ("crest", "vest", None, "bracers", "sandals", "loose", None, "#5a3a1e", "#e0601a", "feather", ("#ff8a2a", "#ffd060")),
    "pulowi": ("stand", "dancer", None, "cuffs", "slippers", "obi", None, "#a83a6a", "#f0c040", "drop", ("#f070a0", "#ffe0f0")),
    "juya": ("nasal", "leather", None, "gloves", "boots", "leather", None, "#2a3e6a", "#a0d0ff", "bolt", ("#a0d0ff", "#fffbd0")),
    "quimbaya": ("crown", "plate", "feather", "armour", "plate", "double", "round", "#c89a20", "#2a2a2a", "coin", ("#ffe07a", "#fff4c0")),
    "zenu": ("stand", "cotton", None, "bracers", "sandals", "narrow", None, "#d8c890", "#2a2018", "spiral", ("#fff0b0",)),
    "manjushri": ("crown", "monk", None, "cuffs", "slippers", "sash", "kite", "#d8801a", "#2a5ad0", "flame", ("#ffb040", "#fff0c0")),
    "mompox": ("tied", "noble", None, "cuffs", "shoes", "leather", None, "#6a4030", "#e8c070", "coin", ("#ffe0a0",)),
    "nevadoruiz": ("horned", "plate", None, "armour", "plate", "double", "heater", "#3a3030", "#ff5a1a", "ember", ("#ff7a2a", "#ffd27a")),
    "chingaza": ("hood", "trench", None, "gloves", "boots", "leather", None, "#4a6a7a", "#a8e0e8", "drop", ("#c0f0ff",)),
    "chenrezig": ("crown", "robe", "lunar", "cuffs", "slippers", "sash", None, "#e8ecf4", "#e8b030", "five", ("#ffffff", "#c8e0ff", "#ffe07a")),
    "magdalena": ("stand", "sea", None, "bracers", "sandals", "rope", None, "#7a5a30", "#3a8ab0", "wave", ("#7ac0f0",)),
    "karagabi": ("crest", "yogi", None, "bracers", "sandals", "loose", None, "#2a2026", "#e0d040", "star", ("#fff48a", "#ffffff")),
    "tutruica": ("hood", "ghost", None, "gloves", "hoofs", "loose", None, "#1e3a32", "#4ab08a", "eye", ("#4ab08a",)),
    "naropa": ("topknot", "yogi", None, "rings", "sandals", "obi", None, "#8a2020", "#f0a040", "flame", ("#ff6a2a", "#ffc0a0")),
    "serankua": ("stand", "cotton", None, "bracers", "sandals", "narrow", None, "#d8d0c0", "#6a4a2e", "spiral", ("#ffffff",)),
    "aluna": ("veil", "ghost", None, "cuffs", "slippers", "sash", None, "#1a3a6a", "#7ab8f0", "cloud", ("#a0d8ff", "#ffffff")),
    "murallas": ("winged", "chain", None, "armour", "plate", "double", "heater", "#8a7050", "#e8d0a0", "cross", ("#fff0c0",)),
    "tilopa": ("topknot", "vest", None, "rings", "sandals", "rope", None, "#a07840", "#f0e0a0", "dot", ("#ffe0a0", "#ffffff")),
    "chiminigagua": ("crown", "dancer", "feather", "cuffs", "slippers", "obi", None, "#141420", "#ffe070", "star", ("#ffe070", "#ffffff")),
    "nencatacoa": ("stand", "weaver", None, "bracers", "shoes", "sash", None, "#7a4a24", "#e07a3a", "note", ("#ffb060",)),
    "marpa": ("wizard", "noble", None, "cuffs", "boots", "mage", None, "#3a4a8a", "#e0e4f0", "spiral", ("#c8d0ff", "#ffffff")),
    "zaque": ("crown", "legion", None, "armour", "sandals", "double", "round", "#a8401a", "#f0b040", "sun", ("#ffb040",)),
    "zipa": ("stand", "plate", None, "armour", "plate", "double", "lozenge", "#1e6a52", "#e8c040", "coin", ("#6af0b0", "#fff48a")),
    "cauca": ("bandana", "leather", None, "gloves", "boots", "leather", None, "#5a4a32", "#a89058", "leaf", ("#d8c890",)),
    "yeshe": ("longhair", "dress", None, "cuffs", "slippers", "sash", None, "#a01e48", "#f0c060", "flower", ("#ff7aa0", "#ffe0f0")),
    "orinoco": ("tied", "sea", None, "bracers", "sandals", "rope", None, "#2a4a6a", "#e0a040", "wave", ("#7ac0f0",)),
    "machig": ("longhair", "ghost", None, "rings", "tabi", "narrow", None, "#3a3448", "#f0e8e0", "skull", ("#e0e0ff", "#ffffff")),
    "calima": ("mask", "skirt", None, "bracers", "sandals", "sash", None, "#a8781e", "#3a2410", "feather", ("#ffe07a",)),
    "barnizpasto": ("stand", "dress", None, "cuffs", "shoes", "obi", None, "#5a1e6a", "#e04ac0", "flower", ("#ff8ae0",)),
    "medicina": ("crown", "monk", None, "cuffs", "slippers", "sash", "round", "#1e3aa8", "#e8b030", "drop", ("#4a7aff", "#c0d8ff", "#ffffff")),
    "gampopa": ("wizard", "monk", None, "gloves", "boots", "mage", None, "#c8a030", "#8a2a2a", "dot", ("#fff0a0",)),
    "sanandres": ("tied", "sea", None, "bracers", "sandals", "sash", None, "#1e7a9a", "#f0f0e0", "shell", ("#7af0ff",)),
    "coronanegra": ("crown", "noble", None, "armour", "rim", "double", "kite", "#1a1a22", "#e0a830", "star", ("#ffd060", "#fff4c0")),
    "malpelo": ("winged", "chain", None, "armour", "plate", "leather", "heater", "#2a3a4a", "#8aaac8", "anchor", ("#a8d0ff",)),
    "nagarjuna": ("moon", "robe", None, "cuffs", "slippers", "sash", None, "#2a6a6a", "#c0f0e8", "spiral", ("#a0f0e0",)),
    "selva": ("bandana", "vest", None, "bracers", "sandals", "loose", None, "#2a5a24", "#8ac85a", "leaf", ("#8ac85a",)),
    "vajrasattva": ("crown", "robe", None, "cuffs", "slippers", "sash", "round", "#e8eef8", "#7ab0e8", "dot", ("#ffffff", "#c8e8ff")),
    "llorona": ("veil", "ghost", None, "cuffs", "slippers", "narrow", None, "#4a4a5a", "#c8d4e8", "drop", ("#c8d4e8",)),
    "shantideva": ("wizard", "monk", None, "gloves", "sandals", "rope", None, "#b08a30", "#f0e0b0", "star", ("#fff0b0",)),
    "mulatrespatas": ("horned", "leather", None, "gloves", "hoofs", "leather", None, "#2a1e18", "#e0401a", "ember", ("#ff6a2a",)),
    "vajrayogini": ("longhair", "dancer", "bat", "rings", "tabi", "obi", None, "#b0141e", "#f0e0c8", "skull", ("#ff3a2a", "#ffc0a0", "#ffffff")),
    "mahakala": ("horned", "plate", "bat", "armour", "plate", "double", "kite", "#141830", "#4a6ae0", "flame", ("#4a6ae0", "#ff8a2a")),
    "sayona": ("veil", "ghost", None, "cuffs", "slippers", "narrow", None, "#c8c8c8", "#3a3a3a", "eye", ("#ffffff",)),
    "amitabha": ("crown", "robe", "feather", "cuffs", "slippers", "sash", None, "#b01e1e", "#ffb040", "sun", ("#ff8a3a", "#fff0c0", "#ffffff")),
    "prajna": ("tiara", "dress", None, "cuffs", "slippers", "sash", None, "#d8a820", "#fff4d0", "sun", ("#ffe080", "#ffffff")),
    "bardo": ("hood", "trench", None, "gloves", "boots", "mage", None, "#2a2a5a", "#a0a0f0", "cloud", ("#c0c0ff",)),
    "samantabhadra": ("crown", "yogi", "lunar", "rings", "slippers", "sash", "round", "#1a2a8a", "#ffffff", "five", ("#4a7ae8", "#ffffff", "#c8d8ff")),
    "cincobudas": ("crown", "monk", "monarch", "cuffs", "slippers", "obi", "round", "#2a5ae0", "#f0d030", "five", ("#ffffff", "#f0d030", "#e03030", "#30c050", "#2a5ae0")),
    "ruedadharma": ("crown", "robe", "feather", "cuffs", "slippers", "sash", "round", "#e0b030", "#ffffff", "sun", ("#ffffff", "#ffe070", "#fff8d0")),
}
# heads drawn in set_art (its hat pictures): set -> (picture, palette from (main, acc), lift)
NEW_HEADS = {
    "chia": ("ZIPA_DIADEM", lambda m, a: {"H": a[0], "Y": a[4], "y": a[3], "e": "#c8d8ff"}, 3),
    "sue": ("ZIPA_DIADEM", lambda m, a: {"H": m[0], "Y": a[4], "y": a[3], "e": "#ff8a2a"}, 3),
    "zipa": ("ZIPA_DIADEM", lambda m, a: {"H": a[0], "Y": a[4], "y": a[3], "e": "#2ac060"}, 3),
    "pulowi": ("HEADWRAP", lambda m, a: {"W": m[1], "w": m[3], "y": a[3], "r": "#e04a8a"}, 3),
    "zenu": ("LLANERO_HAT", lambda m, a: {"H": a[0], "h": m[4], "b": a[2]}, 3),
    "magdalena": ("LLANERO_HAT", lambda m, a: {"H": m[0], "h": m[4], "b": a[3]}, 3),
    "nencatacoa": ("CHULLO", lambda m, a: {"H": m[0], "r": m[3], "w": a[4], "W": a[5]}, 9),
    "barnizpasto": ("HEADWRAP", lambda m, a: {"W": m[1], "w": m[3], "y": a[3], "r": a[4]}, 3),
    "serankua": ("CONE_HAT", lambda m, a: {"H": m[1], "h": m[4], "k": a[2]}, 3),
}


def _effects(sid, tier, base, slot, fx, lvl):
    """What a piece wears, by tier: the mythic all of it, the others less."""
    out = []
    if tier == "mitico":
        if slot == "w":
            out += [("big", (1.3, "center")), ("flames", (("#ffffff",) + tuple(fx), 9, 1.0))]
        elif slot == "h":
            out += [("big", (1.35, "bottom")), ("flames", (("#ffffff",) + tuple(fx[:2]), 7, 0.8))]
        elif slot in "fg":
            out += [("flames", (("#ffffff",) + tuple(fx[:2]), 5, 0.9))]
        elif slot == "s":
            out += [("specks", ((fx[0], "#ffffff"), 9, 0))]
    elif tier == "legendario":
        if slot == "w":
            out += [("flames", (("#ffffff",) + tuple(fx), 8, 0.9))]
        elif slot == "b":
            out += [("specks", ((fx[0], "#ffffff"), 9, 1))]
        elif slot == "h":
            out += [("glow", tuple(fx[:2]))]
    elif tier == "ancestral":
        if slot == "w":
            out += [("glow", tuple(fx[:2]))]
        elif slot == "h":
            out += [("specks", ((fx[0], "#ffffff"), 12, 0))]
    elif lvl >= 300 and slot == "w":  # the plain sets past 300: their weapon glows faintly
        out += [("glow", (fx[0],))]
    return out


# the sets of 404-600 (new_sets_600.py): their gloves, shoes, belt, shield and wings from the 204-400 set
# at the same place, their own hat, body, colours, motif and effects
import new_sets_600 as N6  # noqa: E402
LEVEL = {x[0]: round(204 + i * (400 - 204) / (len(SETS) - 1)) for i, x in enumerate(SETS)}
LEVEL.update({x[0]: round(N6.LO + i * (N6.HI - N6.LO) / (len(N6.SETS) - 1)) for i, x in enumerate(N6.SETS)})
for sid6, v in N6.LOOK.items():
    _h, _b, wings_t, gloves_t, feet_t, belt_t, shield_t, *_ = LOOK[v["template"]]
    LOOK[sid6] = ("x", v["body"], wings_t if v["wings"] is False else v["wings"], gloves_t, feet_t, belt_t, shield_t, v["main"], v["acc"], v["motif"], v["fx"])
SETS = list(SETS) + list(N6.SETS)

NEW_RECIPES, NEW_FX, NEW_ICONS, NEW_STOPS = {}, {}, {}, {}
from new_sets_400 import KIT, JEWEL  # noqa: E402
for i, (sid, name, tier, elem, listen, kit, weapon, slots, names, neck, lpc) in enumerate(SETS):
    head, body, wings, gloves, feet, belt, shield, main_c, acc_c, motif, fx = LOOK[sid]
    NEW_STOPS[sid] = (ramp(main_c), ramp(acc_c))
    lvl = LEVEL[sid]
    for code in "hbw" + slots:
        base = weapon if code == "w" else JEWEL[code] if code in "ar" else KIT[kit][code]
        icon = {"g": ICON_OF[gloves], "f": ICON_OF[feet], "t": ICON_OF[belt], "a": "pendant", "r": "ring"}.get(code)
        if icon:
            NEW_ICONS[(sid, base)] = (icon, motif)
        e = _effects(sid, tier, base, code, fx, lvl)
        if e:
            NEW_FX[(sid, base)] = e
    if tier == "mitico":
        NEW_FX[sid] = [("glow", tuple(fx[:2]))]
    NEW_RECIPES[sid] = {}  # drawn whole in orig_art (orig_tables); set_art only adds the effects
NEW_HEADS = {}


# ---------------------------------------------------------------- drawn whole (orig_art), piece by piece
# The hats are new pictures. Letters: D M m the set's main colour (dark, mid, light), A a B w its accent
# (dark to light), Y y gold, W white, k black, g r b green red blue.
HATS = {
    "FEATHERS": """
..r.g.b.Y.b.g.r..
..rMgMbMYMbMgMr..
..rMgMbMYMbMgMr..
...MMMMMMMMMMM...
.AAAAAAAAAAAAAAA.
.AaYaaaYaaaYaaaA.
.AAAAAAAAAAAAAAA.
""",
    "SUN": """
Y.......Y.......Y
.Y......Y......Y.
..Y...YYYYY...Y..
...Y.YyyyyyY.Y...
....YyyMMMyyY....
YYYYYyyMmMyyYYYYY
....YyyMMMyyY....
.YYYYYYYYYYYYYYY.
.YaYYYaYYYaYYYaY.
""",
    "FIVE": """
...b.....W.....Y...
..bbb...WWW...YYY..
.bbBbb.WWmWW.YYaYY.
.bbbbb.WWWWW.YYYYY.
.r...rrr...ggg...g.
rrr..rmr...gmg..ggg
YYYYYYYYYYYYYYYYYYY
YyAyyyyyAyyyyyAyyyY
YYYYYYYYYYYYYYYYYYY
""",
    "STONE_FACE": """
.DDDDDDDDDDDDDDD.
DMMMMMMMMMMMMMMMD
DMDDDMMMMMMMDDDMD
DMMMMMMMMMMMMMMMD
DMMMkMMMMMMMkMMMD
DMMMMMMMDMMMMMMMD
DMMMMMMMDMMMMMMMD
.DMWDWDDDDDWDWMD.
..DWDWMMMMMWDWD..
...DDDDDDDDDDD...
""",
    "CREST": """
........aaa.......
.......aBBBa......
......aBBaaBa.....
......aBa..Ba.....
....MMMMMMMMMMM...
...MmmmmmmmmmmmM..
..MMmmmmmmmmmmmMM.
..DMMMMMMMMMMMMMD.
..DDDDDDDDDDDDDDD.
..DW..........WD..
""",
    "HORNS": """
WW...............WW
.WW.............WW.
..WW...........WW..
...WWMMMMMMMMMMWW..
....MmmmmmmmmmmM...
...MMmmmmmmmmmmMM..
...DMMMMMMMMMMMMD..
...DDDDDaDDDDDDDD..
...DD....a....DD...
""",
    "VUELTIAO": """
.......kkkkk.......
......kwkwkwk......
.....kwkwkwkwk.....
.....wkwkwkwkw.....
..kkkkkkkkkkkkkkk..
kwkwkwkwkwkwkwkwkwk
.kkkkkkkkkkkkkkkkk.
""",
    "WRAP": """
....aaaaaaaaa....
..aaBBaaaaaBBaa..
.aaBaaaYaaaaaBaa.
.aBaaaYYYaaaaaBa.
.aaaaaaYaaaaaaaa.
..AAAAAAAAAAAAA..
..A...........A..
""",
    "MOON": """
.......WWW.......
......WWW........
......WW.........
......WWW........
.......WWW.......
MMMMMMMMMMMMMMMMM
MmmmBmmmmmmmBmmmM
MMMMMMMMMMMMMMMMM
""",
    "VEIL": """
.....MMMMMMM.....
...MMmmmmmmmMM...
..MmmmmmmmmmmmM..
.MmmmmmmmmmmmmmM.
.Mmm.........mmM.
Mmm...........mmM
Mmm...........mmM
Mm.............mM
Mm.............mM
M...............M
M...............M
""",
    "TUTUSOMA": """
........W........
.......WWW.......
......WWWWW......
.....WWwwWWW.....
....WWWWWWWWW....
...WWwWWWWWwWW...
..WWWWWWWWWWWWW..
..AAAAAAAAAAAAA..
""",
    "LAMA": """
........aa........
.......aMMa.......
......aMMMMa......
.....aMMMMMMa.....
....aMMMMMMMMa....
...aMMMYYYYMMMa...
..aMMMMMMMMMMMMa..
.MMMMMMMMMMMMMMMM.
.MDD..........DDM.
.MD............DM.
.MD............DM.
""",
    "BANDANA": """
...MMMMMMMMMMM....
..MmmmmmmmmmmmM...
.MmmWmmmmWmmmmmM..
.MMMMMMMMMMMMMMMMM
...............MMm
...............M.M
""",
    "YOGI_KNOT": """
.......kkkk.......
......kkkkkk......
......kkWWkk......
.......kkkk.......
......kkkkkk......
....kkkkkkkkkk....
...kkkkkkkkkkkk...
...WWWWWWWWWWWW...
""",
    "DAKINI": """
W.r.W.r.W.r.W.r.W
WkW.WkW.WkW.WkW.W
WWW.WWW.WWW.WWW.W
.Y...Y...Y...Y...
YYYYYYYYYYYYYYYYY
YyryyyyyryyyyyryY
""",
    "BLACK_CROWN": """
.......YYY.......
......YyYyY......
.......YYY.......
...kkkkkkkkkkk...
..kkkkkkkkkkkkk..
..kkkYkkYkkYkkk..
.kkkkkkkkkkkkkkk.
YYYYYYYYYYYYYYYYY
kkkkkkkkkkkkkkkkk
""",
    "BIRD": """
.........MMMM.....
.......MMmmmMM....
......MmmmmmmmMYY.
......MmWkmmmmYYYY
......MmmmmmmmMYY.
.....aMMMMMMMMMa..
....aBaBaBaBaBaBa.
""",
    "GOLD_BAND": """
..Y...Y...Y...Y...Y..
.YyY.YyY.YyY.YyY.YyY.
YYYYYYYYYYYYYYYYYYYYY
YyyByyyyyByyyyyByyyyY
YYYYYYYYYYYYYYYYYYYYY
""",
    "STRAW": """
.......aaaaa.......
.....aaBBBBBaa.....
....aBBBBBBBBBa....
....aMMMMMMMMMa....
aaaaaaaaaaaaaaaaaaa
.aBBBBBBBBBBBBBBBa.
..aaaaaaaaaaaaaaa..
""",
    "WOOL_CAP": """
.......MMMMM.......
.....MMmmmmmMM.....
....MmmAmmAmmmM....
...MmmmmmmmmmmmM...
...MAAAAAAAAAAAM...
...Mr.r.r.r.r.rM...
...MM.........MM...
...MM.........MM...
....B.........B....
""",
    "STARS": """
..W.....Y.....W..
.....W.....W.....
...kkkkkkkkkkk...
..kkYkkkkkkkYkk..
.kkkkkkWkkkkkkkk.
.kkkkkkkkkkkkkkk.
YYYYYYYYYYYYYYYYY
YkkYkkkYkkkYkkkYY
""",
}
# which hat, how far below the band's top its lower edge sits
HAT_OF = {
    "teyuna": ("TUTUSOMA", 3), "tatacoa": ("BANDANA", 3), "sanagustin": ("STONE_FACE", 10), "tierradentro": ("hood", 0),
    "taraverde": ("DAKINI", 3), "chia": ("MOON", 3), "sue": ("SUN", 3), "catedralsal": ("hood", 0), "choco": ("WRAP", 3),
    "milarepa": ("YOGI_KNOT", 4), "yurupari": ("FEATHERS", 3), "pulowi": ("WRAP", 3), "juya": ("CREST", 5),
    "quimbaya": ("SUN", 3), "zenu": ("VUELTIAO", 3), "manjushri": ("FIVE", 3), "mompox": ("VUELTIAO", 3),
    "nevadoruiz": ("HORNS", 5), "chingaza": ("hood", 0), "chenrezig": ("FIVE", 3), "magdalena": ("STRAW", 3),
    "karagabi": ("FEATHERS", 3), "tutruica": ("hood", 0), "naropa": ("YOGI_KNOT", 4), "serankua": ("TUTUSOMA", 3),
    "aluna": ("VEIL", 10), "murallas": ("CREST", 5), "tilopa": ("YOGI_KNOT", 4), "chiminigagua": ("STARS", 3),
    "nencatacoa": ("WOOL_CAP", 7), "marpa": ("LAMA", 7), "zaque": ("GOLD_BAND", 3), "zipa": ("GOLD_BAND", 3),
    "cauca": ("BANDANA", 3), "yeshe": ("DAKINI", 3), "orinoco": ("STRAW", 3), "machig": ("DAKINI", 3),
    "calima": ("BIRD", 6), "barnizpasto": ("WRAP", 3), "medicina": ("FIVE", 3), "gampopa": ("LAMA", 7),
    "sanandres": ("STRAW", 3), "coronanegra": ("BLACK_CROWN", 3), "malpelo": ("CREST", 5), "nagarjuna": ("MOON", 3),
    "selva": ("FEATHERS", 3), "vajrasattva": ("FIVE", 3), "llorona": ("VEIL", 10), "shantideva": ("LAMA", 7),
    "mulatrespatas": ("HORNS", 5), "vajrayogini": ("DAKINI", 3), "mahakala": ("DAKINI", 3), "sayona": ("VEIL", 10),
    "amitabha": ("SUN", 3), "prajna": ("FIVE", 3), "bardo": ("hood", 0), "samantabhadra": ("STARS", 3),
    "cincobudas": ("FIVE", 3), "ruedadharma": ("SUN", 3),
}
# body (by LOOK's body): what's drawn, as orig_art recipe pieces
GLOVE_DRAW = {"gloves": "glove", "bracers": "bracer", "armour": "bracer", "cuffs": "glove", "rings": "beads"}
FEET_DRAW = {"sandals": "sandal", "boots": "boot", "plate": "boot", "slippers": "slipper", "shoes": "boot", "tabi": "slipper",
             "rim": "boot", "ghillies": "slipper", "hoofs": "boot", "high": "sandal"}
BELT_DRAW = {"sash": "sash", "obi": "obi", "rope": "rope", "double": "belt", "mage": "sash", "leather": "belt", "loose": "rope", "narrow": "rope"}
WEAPON_DRAW = {  # base -> kinds (picked by the set's place)
    "espadaastral": ["sword", "vajra", "crystal", "lotus", "phurba", "sword"],
    "lanzaastral": ["spear", "khatvanga", "spear"],
    "arcoastral": ["bow"], "arcoluna": ["bow"],
    "mangualsombra": ["flail", "mace"], "mandoblesombra": ["sword"],
    "varasombra": ["staff", "crystal", "lotus"], "sableluna": ["saber"], "tridenteluna": ["trident", "pole"],
}
SHIELD_DRAW = {"kite": "kite", "round": "round", "scutum": "tower", "heater": "kite", "paint": "sun", "lozenge": "tower"}


HAT_OF_LIFT = {pic: lift for pic, lift in HAT_OF.values()}
HATS.update(N6.HATS)
HAT_OF.update({sid6: (v["hat"], N6.LIFT.get(v["hat"], dict(HAT_OF_LIFT).get(v["hat"], 3))) for sid6, v in N6.LOOK.items()})


def orig_tables(O):
    """{set: {base: [(layer, draw)]}}, {(set, base): weapon}, {(set, base): shield}, in orig_art's terms."""
    m, c, GOLD = O.m, O.c, O.GOLD

    def hat_pal(M, A_):
        return {"D": M[1], "M": M[3], "m": M[4], "A": A_[2], "a": A_[3], "B": A_[4], "w": A_[5], "W": "#ffffff", "k": "#141010",
                "Y": GOLD[3], "y": GOLD[2], "g": "#30c050", "G": "#80e060", "r": "#e03030", "b": "#2a5ae0"}

    def bodies(kind, wing):
        back = [("back", lambda pen, P, side, M, A_: O.wings(pen, P, A_[3], side, tips=A_[5]))] if wing else []
        R = O._robe
        if kind == "robe":
            return back + [("main", R("ankle", main=3, cuff=c(3), sh=c(3)))]
        if kind == "monk":
            return back + [("main", R("ankle", main=3, sh=c(3), beads=lambda M, A_: [A_[4], GOLD[3]]))]
        if kind in ("plate", "chain", "legion"):
            cap = [("back", O._cape(m(1), trim=c(3)))] if kind == "plate" else []
            return back + cap + [("main", O._armour)] + ([("main", R("knee", main=2, sleeves_=False, bare=True, fold=False))] if kind == "legion" else [])
        if kind == "leather":
            return back + [("main", R("knee", main=2, pants_=m(1), cuff=c(2), tab=c(2)))]
        if kind == "dancer":
            return back + [("back", O._cape(m(1), ragged=True)), ("main", R("knee", main=3, sleeves_=False, skirt_col=c(3), ragged=True, fold=False, beads=lambda M, A_: [A_[4], A_[2]]))]
        if kind == "dress":
            return back + [("main", R("ankle", main=3, cuff=c(4), beads=lambda M, A_: [A_[3], A_[5]]))]
        if kind == "tunic":
            return back + [("back", O._cape(c(2))), ("main", R("knee", main=3, pants_=m(1), cuff=c(3)))]
        if kind == "weaver":
            return back + [("main", R("knee", main=3, pants_=m(2), tab=c(3), stripes=lambda M, A_: A_[3]))]
        if kind == "sea":
            return back + [("main", R("knee", main=3, pants_=c(2), sleeve=(), neck=c(3), fold=False))]
        if kind == "noble":
            return back + [("back", O._cape(m(1), trim=lambda M, A_: GOLD[3])), ("main", R("knee", main=2, pants_=m(1), cuff=c(4), tab=c(3), neck=c(4)))]
        if kind == "ghost":
            return back + [("back", O._cape(m(2), ragged=True)), ("main", R("ankle", main=4, ragged=True, cuff=m(5)))]
        if kind == "yogi":
            return back + [("main", R("knee", main=3, bare=True, sleeves_=False, fold=False, skirt_col=c(4), beads=lambda M, A_: [O.BONE, A_[2]]))]
        if kind == "trench":
            return back + [("back", O._cape(m(1))), ("main", R("ankle", main=2, cuff=c(3), neck=c(3)))]
        if kind == "vest":
            return back + [("main", R("knee", main=3, pants_=m(2), bare=True, sleeves_=False, sh=c(3), beads=lambda M, A_: [A_[4], A_[2]]))]
        if kind == "cotton":
            return back + [("main", R("knee", main=5, pants_=m(5), cuff=c(3), neck=c(3), fold=True))]
        if kind == "skirt":
            return back + [("main", R("ankle", main=3, sleeves_=False, sh=c(3), beads=lambda M, A_: [A_[4], A_[5]], stripes=lambda M, A_: A_[3]))]
        raise ValueError(kind)

    arts, weapons, shields = {}, {}, {}
    for i, (sid, name, tier, elem, listen, kit, weapon, slots, names, neck, lpc) in enumerate(SETS):
        head, body, wing, gloves, feet, belt, shield, *_ = LOOK[sid]
        r = {}
        for code in "hbw" + slots:
            base = weapon if code == "w" else JEWEL[code] if code in "ar" else KIT[kit][code]
            if code == "h":
                pic, lift = HAT_OF[sid]
                r[base] = [("hat", O._hood)] if pic == "hood" else [("hat", (lambda g, l: lambda pen, P, side, M, A_: O.hat(pen, P, O.paint(g, hat_pal(M, A_)), l, side))(HATS[pic], lift))]
            elif code == "b":
                r[base] = bodies(body, wing)
            elif code == "g":
                r[base] = [("main", O._g(O.hands, c(3) if gloves != "armour" else m(4), kind=GLOVE_DRAW[gloves], cuff=c(4)))]
            elif code == "f":
                r[base] = [("main", O._g(O.feet, m(2) if feet in ("boots", "plate", "rim", "shoes", "hoofs") else c(3), kind=FEET_DRAW[feet], trim=c(4)))]
            elif code == "t":
                r[base] = [("main", O._g(O.belt, c(3), kind=BELT_DRAW[belt], buckle=GOLD[3] if BELT_DRAW[belt] == "belt" else None, tail=c(4)))]
            elif code == "w":
                kinds = WEAPON_DRAW[weapon]
                kind = kinds[i % len(kinds)]
                weapons[(sid, base)] = (kind, lambda M, A_: {"wood": M[1], "metal": A_[3], "blade": "#d8e0ea", "shine": "#ffffff", "guard": A_[3], "grip": M[1],
                                                             "core": A_[5], "gem": A_[4], "petal": M[3], "petal2": M[4], "head1": M[3], "head2": A_[3], "skull": O.BONE,
                                                             "ribbon": A_[4], "knot": GOLD[3], "string": "#e8e0d0", "tip": A_[4], "chain": "#a0a8b0", "head": A_[3], "spike": "#e8eef4"})
            elif code == "s":
                shields[(sid, base)] = (SHIELD_DRAW[shield or "round"], lambda M, A_: {"rim": A_[3], "face": M[3], "emblem": A_[5], "shine": "#ffffff"})
        arts[sid] = r
    return arts, weapons, shields
