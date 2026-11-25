"""Build the Leyendas character art from the Universal LPC Spritesheet Character Generator.

Downloads the raw LPC layer sheets (cached in .lpc-cache/), recolours them for each
rarity with the LPC palettes, and packs the standing frame (facing the viewer) of every
look into one atlas:

  public/rpg/lpc/atlas.png    64x64 frames, figure layers
  public/rpg/lpc/icons.png    cropped item icons, drawn from the same layers
  public/rpg/lpc/atlas.json   index: looks (layers + z order) and icon rectangles
  public/rpg/lpc/CREDITS.txt  authors and licences of every LPC file used (required)

Rings have no LPC layer; their icons come from the Dungeon Crawl Stone Soup tiles (CC0),
pass the path to its releases/Nov-2015 folder with --dcss (cached after the first run).

usage: .venv/bin/python scripts/build_lpc.py [--dcss /path/to/tiles/releases/Nov-2015]
"""
import csv
import io
import hashlib
import json
import os
import re
import shutil
import sys
import urllib.error
import urllib.request

import colorsys
import zipfile

from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, ".lpc-cache")
OUT = os.path.join(ROOT, "public", "rpg", "lpc")
REPO = "https://raw.githubusercontent.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator/master/"
F = 64          # LPC frame size
C = 128         # atlas cell: big weapons (bows, katana) use 128px frames; 64px frames sit in the middle
SOUTH, EAST = 2, 3  # rows in a walk sheet: north, west, south, east

# ---------------------------------------------------------------- downloads
def fetch(rel):
    """Cached download of a repo file; None if it doesn't exist."""
    path = os.path.join(CACHE, rel)
    miss = path + ".404"
    if os.path.exists(path):
        return open(path, "rb").read()
    if os.path.exists(miss):
        return None
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        data = urllib.request.urlopen(REPO + rel, timeout=30).read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            open(miss, "w").close()
            return None
        raise
    open(path, "wb").write(data)
    return data


DEF_DIRS = {}


_TREE_DEFS = None


def _tree_def(name):
    """Where a definition lives, from the repo's file tree (for ones DEF_PATHS doesn't list)."""
    global _TREE_DEFS
    if _TREE_DEFS is None:
        t = json.load(open(os.path.join(CACHE, "tree.json")))["tree"]
        _TREE_DEFS = {p["path"].split("/")[-1][:-5]: p["path"][len("sheet_definitions/"):-5]
                      for p in t if p["path"].startswith("sheet_definitions/") and p["path"].endswith(".json")}
    return _TREE_DEFS[name]


def sheet_def(name):
    """Sheet definition JSON by file name (without .json)."""
    rel = DEF_PATHS.get(name) or _tree_def(name)
    return json.loads(fetch("sheet_definitions/" + rel + ".json"))


def palette(material):
    meta = json.loads(fetch(f"palette_definitions/{material}/meta_{material}.json"))
    pals = json.loads(fetch(f"palette_definitions/{material}/{material}_ulpc.json"))
    return meta["base"], pals


# where each definition lives under sheet_definitions/
DEF_PATHS = {
    # the second eight sets: pieces of their own (SET_LOOKS)
    "feet_plate_toe": "feet/accessory/feet_plate_toe",
    "torso_clothes_longsleeve2": "torso/shirts/longsleeve/torso_clothes_longsleeve2",
    # the second three top-tier sets
    "facial_earrings_moon": "headwear/accessories/earrings/facial_earrings_moon",
    "facial_earrings_princess": "headwear/accessories/earrings/facial_earrings_princess",
    "hat_bandana2": "headwear/coverings/bandana/hat_bandana2",
    "hat_headband_hairtie": "headwear/coverings/headbands/hat_headband_hairtie",
    "belt_sash_narrow": "torso/waist/belt_sash_narrow",
    "shield_two_engrailed_trim": "weapons/shields/engrailed/shield_two_engrailed_trim",
    "dress_kimono_longsleeve": "torso/dresses/kimono/dress_kimono_longsleeve",
    "dress_kimono_longsleeve_trim": "torso/dresses/kimono/dress_kimono_longsleeve_trim",
    "dress_sash": "torso/dresses/dress_sash",
    "feet_slippers": "feet/feet_slippers",
    "neck_gem_pearl": "headwear/neck/charms/neck_gem_pearl",
    "hat_magic_large": "headwear/hats/magic/hat_magic_large",
    "arms_armour": "arms/arms_armour",
    "bauldron": "arms/bauldron",
    "belt_belly": "torso/waist/belt_belly",
    "belt_obi_knot_left": "torso/waist/obi/belt_obi_knot_left",
    "belt_robe": "torso/waist/belt_robe",
    "belt_sash": "torso/waist/belt_sash",
    "belt_waistband": "torso/waist/belt_waistband",
    "cape_tattered": "torso/cape/cape_tattered",
    "cape_trim": "torso/cape/cape_trim",
    "dress_kimono_oversize_trim": "torso/dresses/kimono/dress_kimono_oversize_trim",
    "dress_kimono_split_trim": "torso/dresses/kimono/dress_kimono_split_trim",
    "feet_boots_fold": "feet/boots/feet_boots_fold",
    "feet_boots_revised": "feet/boots/feet_boots_revised",
    "feet_hoofs": "feet/feet_hoofs",
    "feet_sandals": "feet/feet_sandals",
    "feet_shoes_ghillies": "feet/shoes/feet_shoes_ghillies",
    "feet_socks_tabi": "feet/socks/feet_socks_tabi",
    "hat_accessory_crest_centurion": "headwear/helmets/accessories/hat_accessory_crest_centurion",
    "hat_accessory_horns_downward": "headwear/helmets/accessories/hat_accessory_horns_downward",
    "hat_accessory_horns_short": "headwear/helmets/accessories/hat_accessory_horns_short",
    "hat_accessory_horns_upward": "headwear/helmets/accessories/hat_accessory_horns_upward",
    "hat_accessory_wings": "headwear/helmets/accessories/hat_accessory_wings",
    "hat_formal_tiara": "headwear/hats/formal/hat_formal_tiara",
    "hat_headband_thick_rune": "headwear/coverings/headbands/hat_headband_thick_rune",
    "hat_headband_tied": "headwear/coverings/headbands/hat_headband_tied",
    "hat_helmet_barbarian_nasal": "headwear/helmets/helmets/hat_helmet_barbarian_nasal",
    "hat_helmet_bascinet": "headwear/helmets/helmets/hat_helmet_bascinet",
    "hat_helmet_close": "headwear/helmets/helmets/hat_helmet_close",
    "hat_helmet_flattop": "headwear/helmets/helmets/hat_helmet_flattop",
    "hat_helmet_horned": "headwear/helmets/helmets/hat_helmet_horned",
    "hat_helmet_maximus": "headwear/helmets/helmets/hat_helmet_maximus",
    "hat_helmet_pointed": "headwear/helmets/helmets/hat_helmet_pointed",
    "hat_helmet_spangenhelm": "headwear/helmets/helmets/hat_helmet_spangenhelm",
    "hat_helmet_spangenhelm_viking": "headwear/helmets/helmets/hat_helmet_spangenhelm_viking",
    "hat_helmet_sugarloaf": "headwear/helmets/helmets/hat_helmet_sugarloaf",
    "hat_helmet_xeon": "headwear/helmets/helmets/hat_helmet_xeon",
    "hat_hood_hijab": "headwear/coverings/hoods/hat_hood_hijab",
    "hat_hood_sack_cloth": "headwear/coverings/hoods/hat_hood_sack_cloth",
    "hat_magic_celestial": "headwear/hats/magic/hat_magic_celestial",
    "hat_magic_celestial_moon": "headwear/hats/magic/hat_magic_celestial_moon",
    "hat_magic_large": "headwear/hats/magic/hat_magic_large",
    "hat_magic_wizard_belt": "headwear/hats/magic/hat_magic_wizard_belt",
    "hat_tricorne_thatch": "headwear/hats/tricorne/hat_tricorne_thatch",
    "hat_visor_grated": "headwear/helmets/visors/hat_visor_grated",
    "hat_visor_horned": "headwear/helmets/visors/hat_visor_horned",
    "hat_visor_slit": "headwear/helmets/visors/hat_visor_slit",
    "legs_armour": "legs/legs_armour",
    "legs_skirts_legion": "legs/skirts/legs_skirts_legion",
    "neck_amulet_dangle": "headwear/neck/charms/neck_amulet_dangle",
    "neck_charm_ring": "headwear/neck/charms/neck_charm_ring",
    "neck_gem_trilliant": "headwear/neck/charms/neck_gem_trilliant",
    "neck_necklace_beaded_large": "headwear/neck/neck_necklace_beaded_large",
    "neck_scarf": "headwear/neck/neck_scarf",
    "shield_crusader": "weapons/shields/engrailed/shield_crusader",
    "shield_heater_revised_trim": "weapons/shields/heater/shield_heater_revised_trim",
    "shield_kite": "weapons/shields/shield_kite",
    "shield_spartan": "weapons/shields/shield_spartan",
    "shoulders_epaulets": "arms/shoulders/shoulders_epaulets",
    "shoulders_mantal": "arms/shoulders/shoulders_mantal",
    "torso_armour_plate": "torso/armour/torso_armour_plate",
    "torso_bandages": "torso/torso_bandages",
    "torso_clothes_robe": "torso/shirts/torso_clothes_robe",
    "torso_jacket_iverness": "torso/jacket/torso_jacket_iverness",
    "weapon_blunt_waraxe": "weapons/blunt/weapon_blunt_waraxe",
    "weapon_magic_crystal": "weapons/magic/weapon_magic_crystal",
    "weapon_magic_gnarled": "weapons/magic/weapon_magic_gnarled",
    "weapon_magic_loop": "weapons/magic/weapon_magic_loop",
    "weapon_magic_s": "weapons/magic/weapon_magic_s",
    "weapon_polearm_dragonspear": "weapons/polearm/weapon_polearm_dragonspear",
    "weapon_polearm_halberd": "weapons/polearm/weapon_polearm_halberd",
    "weapon_polearm_scythe": "weapons/polearm/weapon_polearm_scythe",
    "weapon_sword_glowsword": "weapons/sword/weapon_sword_glowsword",
    "weapon_sword_longsword": "weapons/sword/weapon_sword_longsword",
    "weapon_sword_longsword_alt": "weapons/sword/weapon_sword_longsword_alt",
    "wrists_cuffs_lace": "arms/wrists/wrists_cuffs_lace",
    # the newer ordinary bases
    "weapon_sword_rapier": "weapons/sword/weapon_sword_rapier",
    "weapon_blunt_club": "weapons/blunt/weapon_blunt_club",
    "weapon_polearm_longspear": "weapons/polearm/weapon_polearm_longspear",
    "weapon_polearm_trident": "weapons/polearm/weapon_polearm_trident",
    "weapon_polearm_dragonspear": "weapons/polearm/weapon_polearm_dragonspear",
    "tool_pickaxe": "tools/tool_pickaxe",
    "weapon_ranged_boomerang": "weapons/ranged/weapon_ranged_boomerang",
    "weapon_magic_loop": "weapons/magic/weapon_magic_loop",
    "shield_heater_wood": "weapons/shields/heater/shield_heater_wood",
    "shield_plus": "weapons/shields/engrailed/shield_plus",
    "hat_bandana": "headwear/coverings/bandana/hat_bandana",
    "hat_tricorne": "headwear/hats/tricorne/hat_tricorne",
    "hat_magic_wizard": "headwear/hats/magic/hat_magic_wizard",
    "hat_helmet_barbarian": "headwear/helmets/helmets/hat_helmet_barbarian",
    "hat_helmet_barbarian_viking": "headwear/helmets/helmets/hat_helmet_barbarian_viking",
    "hat_helmet_armet": "headwear/helmets/helmets/hat_helmet_armet",
    "torso_jacket_collared": "torso/jacket/torso_jacket_collared",
    "torso_jacket_trench": "torso/jacket/torso_jacket_trench",
    "torso_jacket_tabard": "torso/jacket/torso_jacket_tabard",
    "wrists_cuffs": "arms/wrists/wrists_cuffs",
    "feet_shoes_basic": "feet/shoes/feet_shoes_basic",
    "feet_boots_rim": "feet/boots/feet_boots_rim",
    "feet_plate_toe_thick": "feet/accessory/feet_plate_toe_thick",
    "belt_mage": "torso/waist/belt_mage",
    "belt_obi": "torso/waist/obi/belt_obi",
    "belt_formal": "torso/waist/belt_formal",
    "neck_charm_oval": "headwear/neck/charms/neck_charm_oval",
    "neck_necklace_chain": "headwear/neck/neck_necklace_chain",
    "body": "body/body", "heads_human_male": "head/heads/human/heads_human_male", "heads_human_female": "head/heads/human/heads_human_female",
    "face_neutral": "head/faces/face_neutral",
    "hair_plain": "hair/short/hair_plain", "hair_ponytail": "hair/braids/hair_ponytail", "hair_long": "hair/long/hair_long",
    "beards_beard": "hair/beards/beards_beard",
    "legs_pants": "legs/pants/legs_pants", "legs_armour": "legs/legs_armour",
    "torso_clothes_longsleeve": "torso/shirts/longsleeve/torso_clothes_longsleeve", "torso_clothes_sleeveless": "torso/shirts/sleeveless/torso_clothes_sleeveless",
    "torso_clothes_tunic": "torso/shirts/torso_clothes_tunic", "torso_clothes_vest": "torso/vest/torso_clothes_vest",
    "cape_solid": "torso/cape/cape_solid", "cape_tattered": "torso/cape/cape_tattered",
    "torso_armour_leather": "torso/armour/torso_armour_leather", "torso_chainmail": "torso/torso_chainmail",
    "torso_armour_plate": "torso/armour/torso_armour_plate", "torso_armour_legion": "torso/armour/torso_armour_legion",
    "shoulders_pauldrons": "arms/shoulders/shoulders_pauldrons", "shoulders_legion": "arms/shoulders/shoulders_legion",
    "arms_gloves": "arms/arms_gloves", "arms_bracers": "arms/wrists/arms_bracers", "arms_armour": "arms/arms_armour",
    "feet_sandals": "feet/feet_sandals", "feet_boots_basic": "feet/boots/feet_boots_basic",
    "feet_boots_fold": "feet/boots/feet_boots_fold", "feet_armour": "feet/feet_armour",
    "belt_sash": "torso/waist/belt_sash", "belt_leather": "torso/waist/belt_leather", "belt_double": "torso/waist/belt_double",
    "neck_necklace_beaded_small": "headwear/neck/neck_necklace_beaded_small", "neck_amulet_star": "headwear/neck/charms/neck_amulet_star",
    "hat_hood_cloth": "headwear/coverings/hoods/hat_hood_cloth", "hat_headband_thick": "headwear/coverings/headbands/hat_headband_thick",
    "hat_cap_leather": "headwear/hats/caps/hat_cap_leather", "hat_helmet_kettle": "headwear/helmets/helmets/hat_helmet_kettle",
    "facial_mask_plain": "headwear/accessories/facial_mask_plain", "hat_helmet_greathelm": "headwear/helmets/helmets/hat_helmet_greathelm",
    "hat_formal_crown": "headwear/hats/formal/hat_formal_crown", "hat_accessory_wings": "headwear/helmets/accessories/hat_accessory_wings",
    "hat_accessory_plumage": "headwear/helmets/accessories/hat_accessory_plumage", "hat_accessory_crest": "headwear/helmets/accessories/hat_accessory_crest",
    "hat_helmet_horned": "headwear/helmets/helmets/hat_helmet_horned",
    "weapon_sword_dagger": "weapons/sword/weapon_sword_dagger", "weapon_sword_saber": "weapons/sword/weapon_sword_saber",
    "weapon_sword_scimitar": "weapons/sword/weapon_sword_scimitar", "weapon_sword_arming": "weapons/sword/weapon_sword_arming",
    "weapon_sword_longsword": "weapons/sword/weapon_sword_longsword", "weapon_sword_katana": "weapons/sword/weapon_sword_katana",
    "tool_axe": "tools/tool_axe", "tool_hammer": "tools/tool_hammer",
    "weapon_blunt_mace": "weapons/blunt/weapon_blunt_mace", "weapon_blunt_flail": "weapons/blunt/weapon_blunt_flail",
    "weapon_blunt_waraxe": "weapons/blunt/weapon_blunt_waraxe", "weapon_polearm_halberd": "weapons/polearm/weapon_polearm_halberd",
    "weapon_polearm_spear": "weapons/polearm/weapon_polearm_spear", "weapon_polearm_scythe": "weapons/polearm/weapon_polearm_scythe",
    "weapon_ranged_slingshot": "weapons/ranged/weapon_ranged_slingshot", "weapon_ranged_bow_normal": "weapons/ranged/bow/weapon_ranged_bow_normal",
    "weapon_ranged_bow_great": "weapons/ranged/bow/weapon_ranged_bow_great", "weapon_ranged_bow_recurve": "weapons/ranged/bow/weapon_ranged_bow_recurve", "weapon_ranged_crossbow": "weapons/ranged/weapon_ranged_crossbow",
    "weapon_magic_simple": "weapons/magic/weapon_magic_simple", "weapon_magic_gnarled": "weapons/magic/weapon_magic_gnarled",
    "weapon_magic_crystal": "weapons/magic/weapon_magic_crystal", "weapon_magic_diamond": "weapons/magic/weapon_magic_diamond",
    # monsters
    "body_skeleton": "body/special/body_skeleton", "body_zombie": "body/special/body_zombie",
    "heads_skeleton": "head/heads/undead/heads_skeleton", "heads_zombie": "head/heads/undead/heads_zombie",
    "heads_vampire": "head/heads/undead/heads_vampire", "heads_lizard_male": "head/heads/reptile/heads_lizard_male",
    "heads_troll": "head/heads/fantasy/heads_troll", "heads_human_male_gaunt": "head/heads/human/heads_human_male_gaunt",
    "head_horns_curled": "head/appendages/head_horns_curled", "hair_long_messy": "hair/long/hair_long_messy",
    "hat_cap_cavalier": "headwear/hats/caps/hat_cap_cavalier", "torso_bandages": "torso/torso_bandages",
    "torso_clothes_robe": "torso/shirts/torso_clothes_robe", "torso_clothes_longsleeve_formal": "torso/shirts/longsleeve/torso_clothes_longsleeve_formal",
    "shield_round": "weapons/shields/shield_round", "shield_kite": "weapons/shields/shield_kite",
    "shield_spartan": "weapons/shields/shield_spartan", "shield_crusader": "weapons/shields/engrailed/shield_crusader", "shield_scutum": "weapons/shields/scutum/shield_scutum",
}

# ---------------------------------------------------------------- recolouring
def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def recolor(img, src_hex, dst_hex):
    m = {}
    for s_, d_ in zip(map(hexrgb, src_hex), map(hexrgb, dst_hex)):
        for dr in (-1, 0, 1):
            for dg in (-1, 0, 1):
                for db in (-1, 0, 1):
                    m.setdefault((s_[0] + dr, s_[1] + dg, s_[2] + db), d_)
    img.putdata([(*m[(r, g, b)], a) if a and (r, g, b) in m else (r, g, b, a) for r, g, b, a in img.getdata()])
    return img


def recolor_slow(img, src_hex, dst_hex):
    src = [hexrgb(h) for h in src_hex]
    dst = [hexrgb(h) for h in dst_hex]
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if not a:
                continue
            for s, d in zip(src, dst):
                if abs(r - s[0]) <= 1 and abs(g - s[1]) <= 1 and abs(b - s[2]) <= 1:
                    px[x, y] = (*d, a)
                    break
    return img


# ---------------------------------------------------------------- layer sheets
def walk_sheet(dir_, variant):
    """The walk sheet for a layer folder: palette items have dir/walk.png, variant items
    dir/walk/<v>.png, and some (bows) keep the animation in the folder name: dir/<v>.png."""
    cands = []
    if variant:
        v = variant.replace(" ", "_")
        cands += [f"{dir_}walk/{v}.png", f"{dir_}{v}.png", f"{dir_}{v}/walk.png", f"{dir_}walk/{variant}.png"]
    cands += [f"{dir_}walk.png"]
    for c in cands:
        data = fetch("spritesheets/" + c)
        if data:
            return Image.open(io.BytesIO(data)).convert("RGBA"), c
    return None, None


USED_FILES = set()


def recolour(sheet, rec, color):
    """A palette item's sheet in the wanted colour."""
    if color and rec:
        spec = rec.get("color_1", rec) if isinstance(rec, dict) else None
        if spec and "material" in spec:
            base, pals = palette(spec["material"])
            base = spec.get("base", base).split(".")[-1]
            target = pals.get(color)
            # items can also take another material's palette (cloth gloves: "cloth.ulpc")
            for extra in spec.get("palettes", []):
                if target is None and extra.endswith(".ulpc"):
                    target = palette(extra.split(".")[0])[1].get(color)
            if target and base in pals and color != base:
                sheet = recolor(sheet, pals[base], target)
    return sheet


# ---------------------------------------------------------------- fight animations
# Standing facing the viewer (idle) and side-on (side); the four attacks face east, towards the
# monsters; hurt only faces south in LPC. Weapons with big swings keep them in their own oversize layers.
ANIMS = {"idle": 1, "side": 1, "slash": 6, "thrust": 8, "shoot": 13, "spellcast": 7, "hurt": 6, "ride": 1}
SHEET_OF = {"ride": "sit"}   # ride: on horseback, the generator's "sit" sheet, east row, the third frame (seated on a chair)
FIRST_FRAME = {"ride": 2}
WALKS = ("idle", "side")
CUSTOM = {  # custom animation -> (the body animation it goes with, frame size)
    "slash_oversize": ("slash", 192), "slash_128": ("slash", 128), "thrust_oversize": ("thrust", 192),
    "tool_axe": ("slash", 128), "tool_hammer": ("slash", 128), "walk_128": ("idle", 128),
}
_FILES = None


def repo_has(rel):
    """Whether the repo has this spritesheet (from .lpc-cache/files.json, if there), to skip 404s."""
    global _FILES
    if _FILES is None:
        p = os.path.join(CACHE, "files.json")
        _FILES = set(json.load(open(p))) if os.path.exists(p) else False
    return _FILES is False or ("spritesheets/" + rel) in _FILES


def find_sheet(cands):
    for c in cands:
        if not repo_has(c):
            continue
        data = fetch("spritesheets/" + c)
        if data:
            return Image.open(io.BytesIO(data)).convert("RGBA"), c
    return None, None


def anim_layers(defname, body, color=None, variant=None, head=None):
    """[(z, {anim: (strip, frame size, frames)})], each strip one row of frames facing east."""
    d = sheet_def(defname)
    rec = d.get("recolors")
    if not variant and d.get("variants"):
        variant = color if color in d["variants"] else d["variants"][0]
    v = variant.replace(" ", "_") if variant else None
    allowed = d.get("animations")
    out = []
    for key in sorted(k for k in d if k.startswith("layer_")):
        L = d[key]
        dir_ = L.get(body) or L.get("adult") or L.get("male")
        if not dir_:
            continue
        dir_ = dir_.replace("${head}", head or body).rstrip("/")
        custom = L.get("custom_animation")
        if custom:
            if custom not in CUSTOM:
                continue
            a, fs = CUSTOM[custom]
            files = ([f"{dir_}/{v}.png"] if v else []) + [f"{dir_}.png"]
            want = [(w, fs, files) for w in WALKS] if a == "idle" else [(a, fs, files)]
        else:
            want = []
            for a in ANIMS:
                fa = "walk" if a in WALKS else SHEET_OF.get(a, a)
                if allowed is not None and fa not in allowed:
                    continue
                # bows and big swords stand with their own 128px walk layers
                if a in WALKS and allowed and "walk_128" in allowed:
                    continue
                want.append((a, None, ([f"{dir_}/{fa}/{v}.png", f"{dir_}/{v}/{fa}.png"] if v else []) + [f"{dir_}/{fa}.png"]))
        rows = {}
        for a, fs, cands in want:
            sheet, rel = find_sheet(cands)
            if sheet is None:
                continue
            USED_FILES.add(rel)
            if fs is None:
                fs = sheet.height if a == "hurt" else sheet.height // 4
            nrows = sheet.height // fs
            row = 0 if nrows == 1 else SOUTH if a == "idle" else EAST
            f0 = FIRST_FRAME.get(a, 0)
            if sheet.width // fs <= f0:
                continue
            n = min(sheet.width // fs - f0, ANIMS[a])
            strip = sheet.crop((f0 * fs, row * fs, (f0 + n) * fs, (row + 1) * fs))
            if not strip.getbbox():
                continue
            rows[a] = (recolour(strip, rec, color), fs, n)
        if rows:
            out.append((L.get("zPos", 50), rows))
    return out


def attack_anim(defname):
    """Which body animation a weapon attacks with."""
    d = sheet_def(defname)
    have = set(d.get("animations") or [])
    have |= {CUSTOM[c][0] for c in have if c in CUSTOM}
    for a in ("spellcast", "shoot", "slash", "thrust"):
        if a in have:
            return a
    return "slash"


class AnimStore:
    """One PNG per look (its layers' strips stacked), deduplicated, plus where each strip is."""
    def __init__(self, out_dir):
        self.dir = out_dir
        self.looks = {}
        self.files = set()
        if os.path.isdir(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)

    def add(self, key, layers):
        if not layers:
            return
        strips = [(z, a, im, fs, n) for z, rows in layers for a, (im, fs, n) in rows.items()]
        W = max(im.width for _, _, im, _, _ in strips)
        H = sum(im.height for _, _, im, _, _ in strips)
        sheet = Image.new("RGBA", (W, H))
        meta, y, i = [], 0, 0
        for z, rows in layers:
            lm = {}
            for a, (im, fs, n) in rows.items():
                sheet.paste(im, (0, y))
                lm[a] = [y, fs, n]
                y += im.height
            meta.append([z, lm])
        buf = io.BytesIO()
        sheet.save(buf, "PNG", optimize=True)
        name = hashlib.sha1(buf.getvalue()).hexdigest()[:12]
        if name not in self.files:
            open(os.path.join(self.dir, name + ".png"), "wb").write(buf.getvalue())
            self.files.add(name)
        self.looks[key] = {"f": name, "l": meta}


def layer_frames(defname, body, color=None, variant=None, head=None):
    """[(z, {row: 64x64 image})] for one sheet definition, recoloured.
    color: palette colour name (for palette items); variant: variant name (for list items)."""
    d = sheet_def(defname)
    rec = d.get("recolors")
    # list-of-variants items: a colour name picks the variant, otherwise take the first one
    if not variant and d.get("variants"):
        variant = color if color in d["variants"] else d["variants"][0]
    out = []
    for key in sorted(k for k in d if k.startswith("layer_")):
        L = d[key]
        dir_ = L.get(body) or L.get("adult") or L.get("male")
        if not dir_ or "128" in dir_ or "attack" in dir_ or "thrust/" in dir_ or "slash/" in dir_:
            continue
        if "${head}" in dir_:
            dir_ = dir_.replace("${head}", head or body)
        sheet, rel = walk_sheet(dir_, variant)
        if sheet is None:
            continue
        USED_FILES.add(rel)
        sheet = recolour(sheet, rec, color)
        frames = {}
        fs = sheet.height // 4  # 64, or 128 for the oversize walk sheets
        for row in (SOUTH, EAST):
            fr = sheet.crop((0, row * fs, fs, (row + 1) * fs))
            cell = Image.new("RGBA", (C, C))
            cell.paste(fr, ((C - fs) // 2, (C - fs) // 2))
            frames[row] = cell
        out.append((L.get("zPos", 50), frames))
    if not out:
        print(f"  ! nothing for {defname} ({body}, {color or variant})")
    return out


# ---------------------------------------------------------------- the looks
# Rarity -> colours. Metals, cloth and wood use the LPC palette names.
METAL = {"low": "iron", "normal": "steel", "magic": "silver", "rare": "brass", "unique": "gold"}
CLOTH = {"low": "gray", "normal": "leather", "magic": "blue", "rare": "yellow", "unique": "red"}
WOOD = {"low": "light", "normal": "medium", "magic": "silver", "rare": "gold", "unique": "red"}
SETS = {  # each set has its own colours
    "arriero": {"metal": "bronze", "cloth": "walnut", "wood": "dark"},
    "cacique": {"metal": "gold", "cloth": "forest", "wood": "gold"},
    "centinela": {"metal": "ceramic", "cloth": "navy", "wood": "iron"},
    "patasola": {"metal": "copper", "cloth": "maroon", "wood": "red"},
    "jaguar": {"metal": "gold", "cloth": "tan", "wood": "gold"},
    "cienaga": {"metal": "bronze", "cloth": "forest", "wood": "dark"},
    "mohan": {"metal": "ceramic", "cloth": "teal", "wood": "dark"},
    "yogui": {"metal": "bronze", "cloth": "white", "wood": "light"},
    "vajra": {"metal": "gold", "cloth": "maroon", "wood": "gold"},
    "averno": {"metal": "iron", "cloth": "red", "wood": "red"},
    "trueno": {"metal": "silver", "cloth": "navy", "wood": "silver"},
    "sol": {"metal": "gold", "cloth": "yellow", "wood": "gold"},
    "guardian": {"metal": "iron", "cloth": "black", "wood": "dark"},
    "bachue": {"metal": "gold", "cloth": "teal", "wood": "gold"},
    "nevado": {"metal": "silver", "cloth": "white", "wood": "silver"},
    "vientos": {"metal": "silver", "cloth": "sky", "wood": "light"},
    "montana": {"metal": "bronze", "cloth": "brown", "wood": "dark"},
    "kalachakra": {"metal": "gold", "cloth": "blue", "wood": "gold"},
    "luzclara": {"metal": "silver", "cloth": "white", "wood": "light"},
    "osario": {"metal": "ceramic", "cloth": "orange", "wood": "light"},
    "tairona": {"metal": "gold", "cloth": "red", "wood": "medium"},
    "dorado": {"metal": "gold", "cloth": "teal", "wood": "gold"},
    "relampago": {"metal": "silver", "cloth": "purple", "wood": "silver"},
    "vigilia": {"metal": "silver", "cloth": "lavender", "wood": "silver"},
    "pacto": {"metal": "iron", "cloth": "black", "wood": "red"},
    "firmamento": {"metal": "gold", "cloth": "navy", "wood": "gold"},
    "madreagua": {"metal": "gold", "cloth": "teal", "wood": "gold"},
    "caiman": {"metal": "bronze", "cloth": "forest", "wood": "dark"},
    "andes": {"metal": "silver", "cloth": "red", "wood": "medium"},
    "arhuaco": {"metal": "silver", "cloth": "white", "wood": "light"},
    "galeon": {"metal": "bronze", "cloth": "navy", "wood": "dark"},
    "frailejon": {"metal": "silver", "cloth": "forest", "wood": "light"},
    "bochica": {"metal": "gold", "cloth": "tan", "wood": "light"},
    "bufeo": {"metal": "silver", "cloth": "white", "wood": "light"},
    "llanero": {"metal": "bronze", "cloth": "tan", "wood": "medium"},
    "madremonte": {"metal": "bronze", "cloth": "forest", "wood": "dark"},
    "silbon": {"metal": "iron", "cloth": "black", "wood": "dark"},
    "tunda": {"metal": "ceramic", "cloth": "teal", "wood": "dark"},
    "mahamudra": {"metal": "silver", "cloth": "sky", "wood": "light"},
    "candileja": {"metal": "copper", "cloth": "orange", "wood": "red"},
    "sombreron": {"metal": "iron", "cloth": "black", "wood": "dark"},
    "marimba": {"metal": "gold", "cloth": "yellow", "wood": "medium"},
    "huitaca": {"metal": "gold", "cloth": "purple", "wood": "gold"},
    "canocristales": {"metal": "gold", "cloth": "red", "wood": "medium"},
    "dzogchen": {"metal": "gold", "cloth": "blue", "wood": "gold"},
    "pastor": {"metal": "bronze", "cloth": "tan", "wood": "light"},
    "barquero": {"metal": "silver", "cloth": "blue", "wood": "light"},
    "rey": {"metal": "gold", "cloth": "purple", "wood": "gold"},
    "shakya": {"metal": "gold", "cloth": "orange", "wood": "medium"},
    "tsokye": {"metal": "silver", "cloth": "blue", "wood": "light"},
    "loden": {"metal": "silver", "cloth": "white", "wood": "light"},
    "pemagyalpo": {"metal": "gold", "cloth": "red", "wood": "gold"},
    "pandita": {"metal": "gold", "cloth": "maroon", "wood": "medium"},
    "nyima": {"metal": "gold", "cloth": "yellow", "wood": "gold"},
    "sengedradrok": {"metal": "iron", "cloth": "navy", "wood": "dark"},
    "drollo": {"metal": "copper", "cloth": "red", "wood": "dark"},
}


def FX(name):
    """A palette layer in one fixed colour, whatever the rarity."""
    return ("palette", f"fixed:{name}")


def VAR(name):
    """A layer that comes in ready-made variants: always this one."""
    return ("variant", {"normal": name})


# The second eight sets don't recolour their base's art: each piece is its own combination of
# generator layers (by the set and the piece's root base). Weapons keep their base's kind of move
# (a slash stays a slash), so the attack animation still matches. The robe and kimono only exist
# for the female body: a shirt that fits the male body goes under them (on the female body, hidden).
SET_LOOKS = {
    "cienaga": {  # a swamp witch: sackcloth hood, mossy robe and shawl, a scythe
        "capucha": [("hat_hood_sack_cloth", FX("green")), ("neck_scarf", FX("forest"))],
        "gaban": [("torso_clothes_longsleeve2", FX("forest")), ("torso_clothes_robe", VAR("forest green")), ("shoulders_mantal", FX("charcoal")), ("belt_sash", VAR("black"))],
        "garras": [("weapon_polearm_scythe", VAR("scythe"))],
        "botas": [("feet_boots_fold", FX("charcoal"))],
    },
    "mohan": {  # the river's sorcerer: a wide straw hat, ragged cape like river weed, a fishing spear
        "sombrero": [("hat_magic_large", VAR("brown")), ("neck_scarf", FX("teal"))],
        "ruana": [("cape_tattered", FX("teal")), ("shoulders_mantal", FX("green"))],
        "tridente": [("weapon_polearm_dragonspear", VAR("ceramic"))],
        "brazales": [("wrists_cuffs_lace", FX("teal")), ("arms_bracers", FX("ceramic"))],
        "alpargatas": [("feet_shoes_ghillies", FX("teal"))],
    },
    "yogui": {  # a cotton-clad yogi of the snows: white robe, maroon shawl, a mala, felt boots
        "panoleta": [("hat_headband_tied", FX("white"))],
        "tunica": [("torso_clothes_longsleeve2", FX("white")), ("torso_clothes_robe", VAR("white")), ("shoulders_mantal", FX("maroon"))],
        "amuleto": [("neck_necklace_beaded_large", FX("bronze"))],
        "cordon": [("belt_sash", VAR("yellow"))],
        "alpargatas": [("feet_boots_fold", FX("maroon"))],
    },
    "vajra": {  # the ritual master: a gold crown, maroon and saffron robes, a crystal sceptre
        "corona": [("hat_formal_tiara", VAR("tiara_gold")), ("hat_accessory_crest", FX("gold"))],
        "jubon": [("torso_clothes_longsleeve2", FX("maroon")), ("dress_kimono_oversize_trim", VAR("maroon")), ("shoulders_mantal", FX("yellow")), ("belt_sash", VAR("yellow"))],
        "cetro": [("weapon_magic_crystal", VAR("orange"))],
        "cadena": [("neck_amulet_dangle", VAR("brass_orange"))],
        "guantes": [("wrists_cuffs_lace", FX("yellow"))],
    },
    "averno": {  # a pact with the underworld: horned visor, burning blade, hooves
        "yelmocornudo": [("hat_helmet_horned", FX("iron")), ("hat_visor_horned", FX("iron")), ("hat_accessory_horns_upward", FX("copper"))],
        "coraza": [("torso_armour_plate", FX("iron")), ("bauldron", FX("red")), ("cape_tattered", FX("red"))],
        "mandoble": [("weapon_sword_glowsword", VAR("red"))],
        "guanteletes": [("arms_armour", FX("iron")), ("wrists_cuffs_lace", FX("red"))],
        "grebas": [("feet_hoofs", FX("black"))],
        "cinturonplacas": [("belt_belly", VAR("charcoal")), ("belt_sash", VAR("red"))],
    },
    "trueno": {  # the storm rider: a winged helm, a navy cape over mail, a halberd
        "yelmo": [("hat_helmet_spangenhelm", FX("silver")), ("hat_accessory_wings", FX("silver"))],
        "lorica": [("torso_chainmail", FX("silver")), ("shoulders_epaulets", FX("navy")), ("cape_trim", FX("navy"))],
        "lanzalarga": [("weapon_polearm_halberd", VAR("halberd"))],
        "munequeras": [("arms_bracers", FX("silver")), ("wrists_cuffs_lace", FX("sky"))],
        "botasmontar": [("feet_boots_revised", FX("navy")), ("feet_plate_toe", FX("silver"))],
    },
    "sol": {  # the sun's guard: a crested gold helm, gold plate and cape, a longsword, a round shield
        "almete": [("hat_helmet_maximus", FX("gold")), ("hat_accessory_crest_centurion", FX("gold"))],
        "lorica": [("torso_armour_plate", FX("gold")), ("shoulders_legion", FX("gold")), ("cape_trim", FX("yellow"))],
        "espada": [("weapon_sword_longsword", VAR("longsword"))],
        "escudocruz": [("shield_spartan", VAR("spartan"))],
        "botaspunta": [("feet_armour", FX("gold")), ("feet_plate_toe_thick", FX("gold"))],
    },
    "guardian": {  # a wrathful protector: black and maroon, a skirt like a tiger's hide, a war axe
        "cascobarbaro": [("hat_headband_thick_rune", FX("maroon")), ("hat_formal_tiara", VAR("tiara_iron"))],
        "hacha": [("weapon_blunt_waraxe", VAR("waraxe"))],
        "tabardo": [("bauldron", FX("maroon")), ("cape_tattered", FX("black")), ("legs_skirts_legion", FX("orange"))],
        "brazales": [("arms_bracers", FX("iron")), ("wrists_cuffs_lace", FX("maroon"))],
        "grebas": [("feet_boots_fold", FX("black"))],
        "cinto": [("belt_obi_knot_left", VAR("red"))],
    },
    # the second three top-tier sets: these keep their own colours instead of the tier's gradient
    "bachue": {  # the mother who came out of the lake: a veil, water-blue robes, a serpent staff
        "capucha": [("hat_hood_hijab", FX("teal")), ("facial_earrings_moon", VAR("gold"))],
        "tunica": [("torso_clothes_longsleeve2", FX("teal")), ("dress_kimono_longsleeve_trim", VAR("teal")), ("dress_sash", VAR("yellow")), ("neck_necklace_beaded_large", FX("gold"))],
        "baston": [("weapon_magic_s", VAR("gold"))],
        "amuleto": [("neck_gem_pearl", VAR("blue"))],
        "alpargatas": [("feet_sandals", FX("gold"))],
    },
    "nevado": {  # the snow peak's silence: a white sugarloaf helm, frosted mail and pauldrons, an ice-blue blade
        "yelmo": [("hat_helmet_sugarloaf", FX("steel")), ("hat_accessory_plumage", FX("white"))],
        "cota": [("torso_chainmail", FX("silver")), ("shoulders_pauldrons", FX("ceramic")), ("cape_solid", FX("white"))],
        "espadon": [("weapon_sword_glowsword", VAR("blue"))],
        "guanteletes": [("arms_armour", FX("ceramic")), ("wrists_cuffs", FX("sky"))],
        "botasmontar": [("feet_boots_rim", FX("white")), ("feet_plate_toe", FX("silver"))],
    },
    "vientos": {  # lord of the winds: a feathered bandana, a long sky-blue coat, a curved sabre
        "panoleta": [("hat_bandana2", FX("blue")), ("hat_accessory_plumage", FX("white"))],
        "gaban": [("torso_clothes_longsleeve2", FX("sky")), ("dress_kimono_longsleeve", VAR("sky")), ("shoulders_mantal", FX("white")), ("cape_trim", FX("white"))],
        "espada": [("weapon_sword_scimitar", VAR("scimitar"))],
        "guantescetrero": [("arms_gloves", FX("white")), ("wrists_cuffs_lace", FX("sky"))],
        "botasviaje": [("feet_boots_revised", FX("sky"))],
        "fajin": [("belt_sash_narrow", VAR("white"))],
    },
    "montana": {  # the mountain's heart: a closed bronze helm, heavy plate, a great hammer, a wall of a shield
        "yelmocornudo": [("hat_helmet_close", FX("bronze"))],
        "coraza": [("torso_armour_plate", FX("bronze")), ("shoulders_pauldrons", FX("bronze")), ("legs_armour", FX("bronze")), ("cape_solid", FX("brown"))],
        "mangual": [("tool_hammer", FX("bronze"))],
        "pavés": [("shield_kite", VAR("kite gray orange"))],
        "grebas": [("feet_armour", FX("bronze")), ("feet_plate_toe_thick", FX("bronze"))],
        "cinturonplacas": [("belt_double", VAR("brown"))],
    },
    "kalachakra": {  # the wheel of time: a gold crown, deep-blue robes with a gold shawl, the wheel itself
        "corona": [("hat_formal_crown", VAR("crown_gold")), ("facial_earrings_princess", VAR("gold"))],
        "jubon": [("torso_clothes_longsleeve2", FX("blue")), ("dress_kimono_longsleeve_trim", VAR("blue")), ("shoulders_mantal", FX("gold")), ("belt_sash", VAR("yellow"))],
        "cetro": [("weapon_magic_loop", VAR("gold"))],
        "medallon": [("neck_charm_ring", VAR("gold"))],
        "zapatos": [("feet_slippers", FX("blue"))],
    },
    "arhuaco": {  # the Sierra Nevada: a necklace of white beads
        "amuleto": [("neck_necklace_beaded_large", FX("white"))],
    },
    "luzclara": {  # the clear light: a yogi's topknot, white robes and cloak, a clear crystal, a mirror on the heart
        "panoleta": [("hat_headband_hairtie", FX("white"))],
        "tunica": [("torso_clothes_longsleeve2", FX("white")), ("dress_kimono_longsleeve", VAR("white")), ("shoulders_mantal", FX("white")), ("cape_solid", FX("white")), ("belt_sash", VAR("sky"))],
        "bastonruna": [("weapon_magic_diamond", VAR("silver"))],
        "amuleto": [("neck_charm_oval", VAR("silver"))],
        "botaspunta": [("feet_slippers", FX("white"))],
    },
}


def P(kind):
    return ("palette", kind)


def V(mapping, default=None):
    if default:
        mapping = {**{k: default for k in ("low", "normal", "magic", "rare", "unique", *SETS)}, **mapping}
    return ("variant", mapping)


# ready-made colours (list items) by rarity and set, in the LPC cloth and metal names
CLOTH_V = {"low": "gray", "normal": "brown", "magic": "blue", "rare": "yellow", "unique": "red",
           "arriero": "walnut", "cacique": "forest", "centinela": "navy", "patasola": "maroon", "jaguar": "tan"}
TABARD_V = {**CLOTH_V, "normal": "leather", "low": "gray"}
METAL_V = {"low": "iron", "normal": "steel", "magic": "silver", "rare": "brass", "unique": "gold",
           "arriero": "bronze", "cacique": "gold", "centinela": "ceramic", "patasola": "copper", "jaguar": "gold"}


# Each base: list of (definition, colouring). colouring: P("metal"|"cloth") for palette items,
# P("wood") for list items whose variants are wood/metal names, V({...}) for other list items.
BASE_LOOKS = {
    "daga": [("weapon_sword_dagger", None)],
    "machete": [("weapon_sword_saber", None)],
    "garras": [("weapon_sword_scimitar", None)],
    "espada": [("weapon_sword_arming", P("metal"))],
    "hacha": [("tool_axe", P("metal"))],
    "maza": [("weapon_blunt_mace", None)],
    "mangual": [("weapon_blunt_flail", None)],
    "espadon": [("weapon_sword_longsword", None)],
    "mandoble": [("weapon_sword_katana", None)],
    "martillo": [("tool_hammer", P("metal"))],
    "alabarda": [("weapon_polearm_halberd", None)],
    "tridente": [("weapon_polearm_trident", P("wood"))],
    "guadana": [("weapon_polearm_scythe", None)],
    "hachagrande": [("weapon_blunt_waraxe", None)],
    "honda": [("weapon_ranged_slingshot", None)],
    "varita": [("weapon_magic_simple", None)],
    "arco": [("weapon_ranged_bow_normal", P("wood"))],
    "baston": [("weapon_magic_gnarled", P("wood"))],
    "ballesta": [("weapon_ranged_crossbow", None)],
    "arcocurvo": [("weapon_ranged_bow_recurve", P("wood"))],
    "arcolargo": [("weapon_ranged_bow_great", P("wood"))],
    "bastonruna": [("weapon_magic_crystal", V({"low": "blue", "normal": "blue", "magic": "purple", "rare": "yellow", "unique": "red",
                                               "arriero": "orange", "cacique": "green", "centinela": "blue", "patasola": "red"}))],
    "rodela": [("shield_round", V({"low": "brown", "normal": "brown", "magic": "silver", "rare": "gold", "unique": "gold",
                                    "arriero": "brown", "cacique": "green", "centinela": "black", "patasola": "yellow"}))],
    "escudo": [("shield_kite", V({"low": "kite gray", "normal": "kite gray gray", "magic": "kite blue gray", "rare": "kite orange",
                                   "unique": "kite red gray", "arriero": "kite gray orange", "cacique": "kite green gray",
                                   "centinela": "kite blue blue", "patasola": "kite red gray"}))],
    "escudotribal": [("shield_spartan", None)],
    "pavés": [("shield_crusader", None)],
    "capucha": [("hat_hood_cloth", P("cloth"))],
    "sombrero": [("hat_cap_leather", V({"low": "gray", "normal": "base", "magic": "blue", "rare": "yellow", "unique": "white",
                                         "arriero": "brown", "cacique": "forest", "centinela": "navy", "patasola": "maroon"}))],
    "casco": [("hat_helmet_kettle", P("metal"))],
    "mascara": [("facial_mask_plain", V({"low": "brown", "normal": "walnut", "magic": "blue", "rare": "brass", "unique": "gold",
                                          "arriero": "bronze", "cacique": "gold", "centinela": "iron", "patasola": "maroon"}))],
    "yelmo": [("hat_helmet_greathelm", P("metal"))],
    "corona": [("hat_formal_crown", V({"low": "crown_gray", "normal": "crown_gray", "magic": "crown_blue", "rare": "crown_gold",
                                        "unique": "crown_gold", "arriero": "crown_gray", "cacique": "crown_gold",
                                        "centinela": "crown_blue", "patasola": "crown_red"}))],
    "tunica": [("torso_clothes_vest", P("cloth"))],
    "ruana": [("cape_solid", P("cloth"))],
    "jubon": [("torso_armour_leather", P("cloth"))],
    "cota": [("torso_chainmail", P("metal"))],
    "coraza": [("torso_armour_plate", P("metal")), ("shoulders_pauldrons", P("metal"))],
    "guantes": [("arms_gloves", P("cloth"))],
    "brazales": [("arms_bracers", P("metal"))],
    "guanteletes": [("arms_armour", P("metal"))],
    "alpargatas": [("feet_sandals", P("cloth"))],
    "botas": [("feet_boots_basic", P("cloth"))],
    "botasviaje": [("feet_boots_fold", P("cloth"))],
    "grebas": [("feet_armour", P("metal"))],
    "faja": [("belt_sash", V({"low": "gray", "normal": "red", "magic": "blue", "rare": "yellow", "unique": "orange",
                               "arriero": "brown", "cacique": "forest", "centinela": "navy", "patasola": "maroon"}))],
    "cinturon": [("belt_leather", V({"low": "slate", "normal": "brown", "magic": "charcoal", "rare": "tan", "unique": "white",
                                       "arriero": "walnut", "cacique": "leather", "centinela": "slate", "patasola": "charcoal"}))],
    "cinturonplacas": [("belt_double", V({"low": "slate", "normal": "brown", "magic": "charcoal", "rare": "tan", "unique": "white",
                                            "arriero": "walnut", "cacique": "leather", "centinela": "slate", "patasola": "charcoal"}))],
    "collar": [("neck_necklace_beaded_small", P("metal"))],
    "amuleto": [("neck_amulet_star", V({"low": "bronze_blue", "normal": "silver_blue", "magic": "silver_purple", "rare": "gold_green",
                                         "unique": "gold_red", "arriero": "bronze_orange", "cacique": "gold_green",
                                         "centinela": "silver_blue", "patasola": "bronze_red"}))],
    # more ordinary bases
    "garrote": [("weapon_blunt_club", None)],
    "lanza": [("weapon_polearm_spear", P("wood"))],
    "estoque": [("weapon_sword_rapier", None)],
    "pico": [("tool_pickaxe", P("metal"))],
    "lanzalarga": [("weapon_polearm_longspear", P("wood"))],
    "lanzadentada": [("weapon_polearm_dragonspear", P("wood"))],
    "bumeran": [("weapon_ranged_boomerang", None)],
    "cetro": [("weapon_magic_diamond", P("wood"))],
    "varaanillada": [("weapon_magic_loop", P("wood"))],
    "escudomadera": [("shield_heater_wood", None)],
    "escudolargo": [("shield_scutum", None)],
    "escudocruz": [("shield_plus", None)],
    "panoleta": [("hat_bandana", P("cloth"))],
    "tricornio": [("hat_tricorne", V(CLOTH_V))],
    "sombrerobrujo": [("hat_magic_wizard", V(CLOTH_V))],
    "cascobarbaro": [("hat_helmet_barbarian", P("metal"))],
    "yelmocornudo": [("hat_helmet_barbarian_viking", P("metal"))],
    "almete": [("hat_helmet_armet", P("metal"))],
    "chaqueta": [("torso_jacket_collared", V(CLOTH_V))],
    "gaban": [("torso_jacket_trench", V({"low": "gray", "normal": "gray"}, default="dark gray"))],
    "tabardo": [("torso_chainmail", P("metal")), ("torso_jacket_tabard", V(TABARD_V))],
    "lorica": [("torso_armour_legion", P("metal")), ("shoulders_legion", P("metal"))],
    "munequeras": [("wrists_cuffs", P("cloth"))],
    "guantescetrero": [("arms_gloves", P("cloth")), ("wrists_cuffs", P("cloth"))],
    "zapatos": [("feet_shoes_basic", P("cloth"))],
    "botasmontar": [("feet_boots_rim", P("cloth"))],
    "botaspunta": [("feet_boots_basic", P("cloth")), ("feet_plate_toe_thick", P("metal"))],
    "cordon": [("belt_mage", V({"low": "iron", "normal": "brown", "magic": "silver", "rare": "gold", "unique": "gold",
                                "arriero": "bronze", "cacique": "gold", "centinela": "iron", "patasola": "black", "jaguar": "gold"}))],
    "fajin": [("belt_obi", V(CLOTH_V))],
    "cinto": [("belt_formal", None)],
    "medallon": [("neck_charm_oval", V(METAL_V))],
    "cadena": [("neck_necklace_chain", V(METAL_V))],
}
# Unique items: their colours, and sometimes an extra piece so they don't look like a recolour.
UNIQUE_EXTRA = {
    "Sombrero de Doce Vueltas": [("hat_accessory_plumage", P("cloth"))],
    "Oído de la Montaña": [("hat_accessory_wings", P("metal"))],
    "Coraza del Volcán": [("cape_tattered", ("palette", "fixed:red"))],
    "Ruana de la Abuela": [],
    "Corona del Dorado": [],
}
# The three rarities above unique look like nothing else: the whole item is redrawn in the tier's
# own colours (a gradient map over its shading), and helmets and body armour get a piece only they have.
TOP_STYLES = {
    "ancestral": ["#1c0b16", "#4f1a39", "#8f3a63", "#cf6f96", "#f5b9cf", "#fff0f6"],   # rose and bone
    "legendario": ["#1a0605", "#5c120d", "#a3221a", "#e5512f", "#ffb347", "#fff1c2"],  # embers into gold
    "mitico": ["#04101c", "#0c3558", "#1876a3", "#3fc4e4", "#aef3ff", "#ffffff"],      # deep water into light
}

# The high bands (data.js BANDS): every piece drawn wholly in its band's material, a gradient over its
# shading (BAND_STOPS), with some layers in the band's accent colours instead (BAND_ACCENT): the
# obsidian's embers, the emerald's gold. Only a "normal" look (rarity shows in the glow) and the three top tiers'.
BAND_STOPS = {
    "obsidiana": ["#08060c", "#1c1626", "#382c48", "#5e4a74", "#9a7ab0", "#e9dcf5"],
    "hueso": ["#120c08", "#3a2c20", "#76644e", "#b4a284", "#e4d8be", "#fffaf0"],
    "esmeralda": ["#03120b", "#073a22", "#0e6e40", "#22b068", "#86f2b6", "#effff6"],
    "tumbaga": ["#170a03", "#4a2308", "#8e4a14", "#cf862c", "#f4c75e", "#fff5cc"],
    "catatumbo": ["#06071a", "#191c4c", "#363c98", "#6676e0", "#b8c2ff", "#ffffff"],
    "luna": ["#080a14", "#1e2640", "#45537a", "#8a9bc6", "#d4ddf6", "#ffffff"],
    "sombra": ["#030104", "#12061a", "#2c0e38", "#58196a", "#9a3cb0", "#f0b8ff"],
    "astral": ["#04060e", "#141e44", "#26508a", "#2fb8a6", "#9ef0e0", "#ffffff"],
}
BAND_ACCENT = {
    "obsidiana": ["#1a0702", "#5a1606", "#b8360c", "#ff7a2a", "#ffc070", "#fff0c8"],   # embers
    "hueso": ["#120303", "#3e0a0a", "#7a1414", "#b02a22", "#e06048", "#ffc0a8"],       # old blood
    "esmeralda": ["#170a03", "#4a2308", "#8e5a14", "#d4a02c", "#f8d868", "#fff8d0"],   # gold
    "tumbaga": ["#03120b", "#073a22", "#0e6e40", "#22b068", "#86f2b6", "#effff6"],     # emeralds
    "catatumbo": ["#1a1602", "#4a4208", "#a09018", "#f0e040", "#fff8a0", "#ffffff"],   # lightning
    "luna": ["#04060f", "#0a1430", "#16306a", "#2c5cb8", "#6e9cf0", "#d8e8ff"],        # night blue
    "sombra": ["#120206", "#3a0618", "#7a0c30", "#d0184a", "#ff6080", "#ffd0dc"],      # red eyes
    "astral": ["#170a03", "#4a2308", "#8e5a14", "#d4a02c", "#f8d868", "#fff8d0"],      # star gold
}
A_ = "accent"
BAND_LOOKS = {
    # obsidiana: black glass, embers on the edges
    "macana": [("weapon_sword_longsword_alt", None)],
    "hachaobsidiana": [("weapon_blunt_waraxe", A_)],
    "arcoobsidiana": [("weapon_ranged_bow_normal", A_)],
    "escudoobsidiana": [("shield_heater_revised_wood", None), ("shield_heater_revised_trim", A_)],
    "yelmoobsidiana": [("hat_helmet_barbuta", None), ("hat_accessory_horns_short", A_)],
    "corazaobsidiana": [("torso_armour_plate", None), ("shoulders_pauldrons", None), ("cape_tattered", A_)],
    "guantesobsidiana": [("arms_armour", None), ("arms_hands_ring_stud", A_)],
    "grebasobsidiana": [("feet_armour", None), ("feet_plate_toe_thick", A_)],
    "cintoobsidiana": [("belt_leather2", A_)],
    # hueso: bone and old blood
    "sablehueso": [("weapon_sword_saber", None)],
    "guadanahueso": [("weapon_polearm_scythe", None)],
    "varahueso": [("weapon_polearm_cane", None)],
    "escudohueso": [("shield_scutum", None), ("shield_scutum_trim", A_)],
    "yelmohueso": [("hat_helmet_bascinet", None), ("hat_visor_pigface", None), ("hat_accessory_horns_downward", None)],
    "petohueso": [("torso_armour_legion", None), ("bauldron", None), ("legs_skirts_legion", A_)],
    "brazaleshueso": [("arms_bracers", None), ("wrists_cuffs", A_)],
    "botashueso": [("feet_boots_rim", A_), ("feet_plate_toe", None)],
    "cinturonhueso": [("belt_loose", None)],
    # esmeralda: green stone set in gold
    "estoqueesmeralda": [("weapon_sword_rapier", None)],
    "alabardaesmeralda": [("weapon_polearm_halberd", None)],
    "cetroesmeralda": [("weapon_magic_diamond", None)],
    "escudoesmeralda": [("shield_two_engrailed", None), ("shield_two_engrailed_trim", A_)],
    "yelmoesmeralda": [("hat_helmet_legion", None), ("hat_accessory_plumage_legion", A_)],
    "cotaesmeralda": [("torso_chainmail", None), ("torso_jacket_tabard", None), ("shoulders_mantal", A_)],
    "guantesesmeralda": [("arms_gloves", None), ("wrists_cuffs_lace", A_)],
    "zapatosesmeralda": [("feet_socks_high", A_), ("feet_shoes_revised", None)],
    "fajaesmeralda": [("belt_obi_knot_right", None)],
    # tumbaga: gold and copper, emeralds
    "mazatumbaga": [("weapon_blunt_mace", None)],
    "lanzatumbaga": [("weapon_polearm_dragonspear", None)],
    "baculotumbaga": [("weapon_magic_s", None)],
    "rodelatumbaga": [("shield_spartan", None)],
    "yelmotumbaga": [("hat_helmet_norman", None), ("hat_accessory_plumage_centurion", A_)],
    "corazatumbaga": [("torso_armour_plate", None), ("shoulders_legion", None), ("legs_armour", None), ("cape_trim", A_)],
    "guantestumbaga": [("arms_armour", None), ("wrists_cuffs", A_)],
    "grebastumbaga": [("feet_armour", None), ("feet_plate_toe", A_)],
    "cintotumbaga": [("belt_double", None)],
    # catatumbo: storm blue, lightning yellow
    "espadacatatumbo": [("weapon_sword_glowsword", A_)],
    "martillocatatumbo": [("tool_hammer", None)],
    "ballestacatatumbo": [("weapon_ranged_crossbow", None)],
    "escudocatatumbo": [("shield_kite", None)],
    "yelmocatatumbo": [("hat_helmet_xeon", None), ("hat_accessory_horns_upward", A_)],
    "corazacatatumbo": [("torso_armour_leather", None), ("shoulders_epaulets", A_), ("cape_solid", None)],
    "guantescatatumbo": [("arms_gloves", None), ("arms_bracers", A_)],
    "botascatatumbo": [("feet_boots_revised", None), ("feet_plate_toe_thick", A_)],
    "cintocatatumbo": [("belt_leather", A_)],
    # luna: pale silver, night blue
    "sableluna": [("weapon_sword_scimitar", None)],
    "tridenteluna": [("weapon_polearm_trident", None)],
    "arcoluna": [("weapon_ranged_bow_recurve", None)],
    "rodelaluna": [("shield_round", None)],
    "yelmoluna": [("hat_helmet_pointed", None), ("hat_visor_slit_narrow", A_)],
    "mantoluna": [("torso_jacket_iverness", A_), ("shoulders_mantal", None), ("cape_trim", None)],
    "brazalesluna": [("arms_bracers", None), ("arms_hands_ring_stud", A_)],
    "zapatosluna": [("feet_socks_ankle", A_), ("feet_shoes_sara", None)],
    "cordonluna": [("belt_robe", None)],
    # sombra: void purple, red eyes
    "mangualsombra": [("weapon_blunt_flail", None)],
    "mandoblesombra": [("weapon_sword_katana", None)],
    "varasombra": [("weapon_magic_crystal", A_)],
    "escudosombra": [("shield_crusader", None)],
    "yelmosombra": [("hat_helmet_bascinet_round", None), ("hat_visor_round", A_), ("hat_accessory_horns_downward", None)],
    "corazasombra": [("torso_armour_plate", None), ("shoulders_pauldrons", None), ("bauldron", None), ("cape_tattered", A_)],
    "guantessombra": [("arms_armour", None), ("bauldron", A_)],
    "pezunassombra": [("feet_hoofs", None)],
    "cintosombra": [("belt_belly", None)],
    # astral: night sky and star gold
    "espadaastral": [("weapon_sword_longsword", A_)],
    "lanzaastral": [("weapon_polearm_longspear", None)],
    "arcoastral": [("weapon_ranged_bow_great", A_)],
    "escudoastral": [("shield_plus", None)],
    "capiroteastral": [("hat_magic_celestial_moon", None), ("hat_magic_celestial_moon_trim", A_)],
    "vestiduraastral": [("torso_clothes_longsleeve2", None), ("torso_jacket_frock", None), ("shoulders_mantal", A_), ("cape_solid", None)],
    "guantesastral": [("arms_gloves", None), ("wrists_cuffs", A_), ("arms_hands_ring_stud", A_)],
    "zapatillasastral": [("feet_socks_tabi", None), ("feet_slippers", A_)],
    "fajinastral": [("belt_sash_narrow", A_)],
}
BAND_OF = {b: band for band, ids in {
    "obsidiana": "macana hachaobsidiana arcoobsidiana escudoobsidiana yelmoobsidiana corazaobsidiana guantesobsidiana grebasobsidiana cintoobsidiana",
    "hueso": "sablehueso guadanahueso varahueso escudohueso yelmohueso petohueso brazaleshueso botashueso cinturonhueso",
    "esmeralda": "estoqueesmeralda alabardaesmeralda cetroesmeralda escudoesmeralda yelmoesmeralda cotaesmeralda guantesesmeralda zapatosesmeralda fajaesmeralda",
    "tumbaga": "mazatumbaga lanzatumbaga baculotumbaga rodelatumbaga yelmotumbaga corazatumbaga guantestumbaga grebastumbaga cintotumbaga",
    "catatumbo": "espadacatatumbo martillocatatumbo ballestacatatumbo escudocatatumbo yelmocatatumbo corazacatatumbo guantescatatumbo botascatatumbo cintocatatumbo",
    "luna": "sableluna tridenteluna arcoluna rodelaluna yelmoluna mantoluna brazalesluna zapatosluna cordonluna",
    "sombra": "mangualsombra mandoblesombra varasombra escudosombra yelmosombra corazasombra guantessombra pezunassombra cintosombra",
    "astral": "espadaastral lanzaastral arcoastral escudoastral capiroteastral vestiduraastral guantesastral zapatillasastral fajinastral",
}.items() for b in ids.split()}
assert set(BAND_OF) == set(BAND_LOOKS)
# the sets on band pieces (data.js, levels 68-126): the band's shapes in the set's own colours, [main, accent]
SET_BAND_STOPS = {
    "osario": (["#120c08", "#3e3226", "#7e6e58", "#c4b496", "#ece2cc", "#fffaf0"], ["#1a0802", "#5a2206", "#b8560c", "#ff9a1a", "#ffd060", "#fff4c0"]),     # bone, marigolds
    "tairona": (["#140806", "#42190e", "#7e3420", "#b85a34", "#e09a6a", "#fbe0c4"], ["#170a03", "#4a2308", "#8e5a14", "#d4a02c", "#f8d868", "#fff8d0"]),    # terracotta, gold
    "dorado": (["#1a0e02", "#5a3808", "#a8701a", "#e8b030", "#ffe07a", "#fffbe0"], ["#02141a", "#06363e", "#0e6a70", "#22a8a4", "#7ae8dc", "#e4fffa"]),     # gold, lake water
    "relampago": (["#0c0418", "#2a0e4a", "#4e1e8a", "#8a4ad0", "#c8a0ff", "#f4ecff"], ["#06141a", "#0a3a4a", "#1a8aa8", "#4ae0ff", "#bff8ff", "#ffffff"],),  # violet, white-cyan
    "vigilia": (["#0e0c14", "#2e2a3e", "#5e5878", "#a49cc0", "#e4e0f2", "#ffffff"], ["#0c0614", "#26143e", "#4a2a7a", "#7e5ac0", "#b8a0ec", "#ece4ff"]),    # pearl, lavender
    "pacto": (["#000000", "#0c0808", "#201414", "#3a2424", "#6a3a3a", "#b07070"], ["#1a0000", "#4a0404", "#8a0a0a", "#e0201a", "#ff7040", "#ffd0a0"]),      # soot, hellfire
    "madreagua": (["#021014", "#06323a", "#0e6268", "#2a9a98", "#8ae0d4", "#eafffa"], ["#1a0e02", "#5a3808", "#a8701a", "#e8b030", "#ffe07a", "#fffbe0"]),  # river, golden hair
    "caiman": (["#040a04", "#122a12", "#2a4a1e", "#4e7030", "#9ab45a", "#e8f0b0"], ["#1a1402", "#4a3c08", "#a08a18", "#e8d040", "#fff48a", "#ffffff"]),   # swamp hide, yellow eyes
    "andes": (["#140404", "#4a0e0a", "#8e2216", "#c84a2a", "#f09a5a", "#fff0d8"], ["#0e1014", "#3a4048", "#7a8490", "#c4ccd6", "#eef2f8", "#ffffff"]),    # red wool, snow
    "firmamento": (["#02030c", "#0a1238", "#1a2a74", "#3e58c0", "#a0b8ff", "#ffffff"], ["#170a03", "#4a2308", "#8e5a14", "#e0b040", "#fff0a0", "#ffffff"]), # night, stars
    "arhuaco": (["#1e1a14", "#5a5246", "#a49a88", "#d8d0c0", "#f4f0e6", "#ffffff"], ["#120a06", "#3a2616", "#6a4a2e", "#9a7650", "#c8a87a", "#efe0c4"]),    # white cotton, natural wool
    "galeon": (["#020a10", "#0a2430", "#1e4a52", "#4a7a70", "#a8c8b0", "#f0fff4"], ["#1a1002", "#4a3008", "#8e6414", "#d8a830", "#ffe07a", "#fffbe0"]),  # sea-green barnacles, doubloons
    "frailejon": (["#0a100c", "#28362c", "#56685a", "#93a594", "#d2dccf", "#f8fbf6"], ["#1a1602", "#4a400a", "#8e7c18", "#d8c030", "#f8ea7a", "#fffbe0"]),  # páramo mist and moss, frailejón flowers
    "bochica": (["#140c04", "#3e2a14", "#7a5a32", "#b89464", "#e8d0a8", "#fff8ea"], ["#0a0a1a", "#1a3a7a", "#2a8ad0", "#7ad0f0", "#d0f4ff", "#ffffff"]),  # undyed cotton, the falls
    "bufeo": (["#120408", "#4a1424", "#8e3a5a", "#d07a98", "#f6c0d2", "#fff4f8"], ["#0e0a04", "#3a2a12", "#6a4e26", "#a08048", "#d8c090", "#fff4dc"]),  # river-dolphin pink, muddy water
    "llanero": (["#1e1a14", "#6a6050", "#b4aa96", "#e4dccb", "#f8f4ea", "#ffffff"], ["#140a02", "#40240a", "#7a4a1a", "#b88040", "#e8c088", "#fff4e0"]),  # white liquiliqui, saddle leather
    "madremonte": (["#020a02", "#0e2a0e", "#1e5218", "#3e8a2a", "#8ac85a", "#e0ffc0"], ["#0e0804", "#3a2410", "#6a4422", "#9a6a3a", "#c89a62", "#f0dcb8"]),  # leaves, bark
    "silbon": (["#000000", "#0a0a10", "#1a1a26", "#34344a", "#6a6a88", "#b0b0d0"], ["#0e0c08", "#3a342a", "#7a7058", "#b8ac90", "#e8e0cc", "#ffffff"]),  # night, dry bone
    "tunda": (["#02080a", "#082a2a", "#14504a", "#2a7a68", "#6ab49a", "#c8f0e0"], ["#140402", "#4a1408", "#8e3418", "#e06a3a", "#ffa880", "#ffe8dc"]),  # mangrove water, shrimp
    "mahamudra": (["#020a1a", "#0a2a5a", "#1a5aa8", "#4a96e0", "#a8d4ff", "#ffffff"], ["#0e1014", "#3a4048", "#7a8490", "#c4ccd6", "#eef2f8", "#ffffff"]),  # open sky, cloud
    "candileja": (["#140200", "#4a0a02", "#8e1e06", "#e04a0e", "#ff9a2a", "#fff0a0"], ["#0a0806", "#2a2420", "#4a423a", "#7a7068", "#b0a8a0", "#e8e4e0"]),  # fireballs, ash
    "sombreron": (["#000000", "#0a0808", "#1e1a18", "#3a3430", "#6a625a", "#a89c90"], ["#140000", "#4a0000", "#8a0a0a", "#e01a1a", "#ff6a5a", "#ffd0c8"]),  # black felt, red eyes
    "marimba": (["#140a02", "#3e2408", "#7a4a16", "#b8862e", "#e8c46a", "#fff4d0"], ["#02060e", "#0a1a3a", "#12407a", "#2a7ac0", "#7ac0f0", "#e0f4ff"]),  # chonta wood, Pacific blue
    "huitaca": (["#0e0414", "#34104a", "#6a2a8e", "#b05ad0", "#e8a8f8", "#fff0ff"], ["#1a1402", "#4a3c08", "#a08a18", "#e8d040", "#fff48a", "#ffffff"]),  # festival purple, moonlight gold
    "canocristales": (["#140204", "#4a0a12", "#a01a24", "#e0403a", "#ff9a7a", "#fff0e8"], ["#02100e", "#0a3a30", "#1a7a5a", "#3ac08a", "#f0e040", "#fffbe0"]),  # macarenia red, green and yellow water
    "dzogchen": (["#02040e", "#0a1840", "#1e3a8e", "#4a7ae0", "#b8d0ff", "#ffffff"], ["#140a02", "#4a1a08", "#a8301a", "#f0b030", "#7ae07a", "#ffffff"]),  # space blue, five lights
    "pastor": (["#140e08", "#3e3020", "#7a6650", "#b8a48a", "#e8dcc6", "#fffaf0"], ["#06140a", "#123a18", "#2a6a2a", "#5aa040", "#a8d878", "#effce0"]),  # undyed wool, pasture
    "barquero": (["#020a14", "#0a2440", "#1a4a7a", "#3a7ab0", "#8ab8e0", "#e8f6ff"], ["#140e02", "#4a3a10", "#8e7428", "#c8a850", "#f0dc98", "#fffbe8"]),  # river, straw
    "rey": (["#0c0414", "#2e0e4a", "#5a1e8a", "#8a4ac0", "#c8a0ec", "#f6ecff"], ["#1a1002", "#5a3808", "#a8701a", "#e8b030", "#ffe07a", "#fffbe0"]),  # royal purple, gold
    "shakya": (["#1a0a00", "#5a2a04", "#a85a0a", "#e8961a", "#ffc860", "#fff2d0"], ["#140204", "#3e0a12", "#6e1424", "#a02a3a", "#d86a74", "#ffd8dc"]),  # saffron, maroon
    "tsokye": (["#020814", "#06204a", "#0e3e8a", "#2a6ad0", "#8ab8ff", "#eef6ff"], ["#14040a", "#4a1028", "#8e2a52", "#e0609a", "#ffb0d4", "#fff0f6"]),  # lake blue, lotus pink
    "loden": (["#14161a", "#4a5058", "#8e96a0", "#d0d6de", "#f4f6f8", "#ffffff"], ["#020a14", "#0a2a4a", "#1a5a8a", "#4a96c8", "#a8d8f8", "#eaf8ff"]),  # white, pale blue
    "pemagyalpo": (["#140202", "#4a0a0a", "#8e1a1a", "#d83a3a", "#ff8a7a", "#ffe4dc"], ["#1a1002", "#5a3808", "#a8701a", "#e8b030", "#ffe07a", "#fffbe0"]),  # royal red, gold
    "pandita": (["#120404", "#3e0e0a", "#7a1e14", "#b8402a", "#e88a5a", "#ffe0c8"], ["#140e02", "#4a3a08", "#8e7414", "#d8b030", "#f8e070", "#fffbe0"]),  # maroon and red, ochre
    "nyima": (["#1a1202", "#4a3a06", "#8e7410", "#e0c020", "#fff07a", "#fffce0"], ["#140600", "#4a1a02", "#8e3a06", "#e06a10", "#ffa040", "#ffe0c0"]),  # sun gold, tiger orange
    "sengedradrok": (["#000208", "#020a24", "#0a1a50", "#1a3a90", "#5a7ad0", "#c0d0ff"], ["#1a0200", "#5a0a00", "#a82a04", "#f06a10", "#ffb040", "#fff0a0"]),  # wrathful blue, flame
    "drollo": (["#0a0000", "#2a0604", "#5a120a", "#8e2a14", "#c85a2a", "#f0b080"], ["#140600", "#4a1a02", "#8e3a06", "#e8801a", "#ffc060", "#fff4d0"]),  # dark red-brown, tiger
}
# a set on band pieces that doesn't take the band's shapes: its own layers (None: main colours, A_: accent)
SET_BAND_LOOKS = {
    "arhuaco": {  # white cotton: the tutusoma, the manta over white trousers, a sash of wool, a plain walking stick
        "yelmocatatumbo": [("hat_helmet_sugarloaf", None)],
        "corazacatatumbo": [("legs_pants", None), ("torso_clothes_tunic", None)],
        "cintocatatumbo": [("belt_sash_narrow", A_)],
        "baculotumbaga": [("weapon_polearm_cane", A_)],
    },
}
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import set_art as SET_ART  # noqa: E402  the sets from 138 to 200: a look of its own for every piece
import orig_art as ORIG  # noqa: E402  the eleven bodhisattva and Guru Rinpoche sets, drawn frame by frame
SET_BAND_LOOKS.update({sid: {b: [(n, "light" if c == "light" else A_ if c else None) for n, c in parts] for b, parts in r.items()} for sid, r in SET_ART.RECIPES.items()})
HEAD_BASES = {"capucha", "sombrero", "casco", "mascara", "yelmo", "corona"}
BODY_BASES = {"tunica", "jubon", "cota", "coraza"}
TOP_EXTRA = {
    "ancestral": {"head": [("hat_accessory_crest", P("metal"))], "body": [("shoulders_legion", P("metal"))]},
    "legendario": {"head": [("hat_accessory_plumage", P("cloth"))], "body": [("cape_solid", P("cloth"))]},
    "mitico": {"head": [("hat_accessory_wings", P("metal"))], "body": [("cape_tattered", P("cloth")), ("shoulders_legion", P("metal"))]},
}


def top_extra(style, base):
    t = TOP_EXTRA.get(style, {})
    return t.get("head", []) if base in HEAD_BASES else t.get("body", []) if base in BODY_BASES else []


def gmap(im, stops):
    """Redraw an image in a gradient by its lightness; the darkest outline stays as it is."""
    cols = [hexrgb(h) for h in stops]
    out = im.copy()
    px = out.load()
    n = len(cols) - 1
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if not a:
                continue
            L = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            if L < 0.09:
                continue
            t = min(0.999, L * 1.08) * n
            i, f = int(t), t - int(t)
            c0, c1 = cols[i], cols[i + 1]
            px[x, y] = (round(c0[0] + (c1[0] - c0[0]) * f), round(c0[1] + (c1[1] - c0[1]) * f), round(c0[2] + (c1[2] - c0[2]) * f), a)
    return out


def gmap_layers(layers, stops):
    return [(z, {k: gmap(im, stops) for k, im in frames.items()}) for z, frames in layers]


def gmap_anim(layers, stops):
    return [(z, {a: (gmap(im, stops), fs, n) for a, (im, fs, n) in rows.items()}) for z, rows in layers]


UNIQUE_COLORS = {  # override per unique: metal / cloth / wood colour
    "Ruana de la Abuela": {"cloth": "maroon"},
    "Capucha del Monaguillo": {"cloth": "white"},
    "Coraza del Volcán": {"metal": "copper"},
    "Oído de la Montaña": {"metal": "silver"},
    "Guantes del Escribano": {"cloth": "black"},
    "Jubón del Contrabandista": {"cloth": "black"},
    "Botas del Cartero": {"cloth": "navy"},
    "Alpargatas del Peregrino": {"cloth": "white"},
    "Collar de Chaquiras": {"metal": "copper"},
    "Corona del Dorado": {"metal": "gold"},
    "Arco del Pescador de Luna": {"wood": "silver"},
    "Arco de la Madremonte": {"wood": "dark"},
    "Arco de Bochica": {"wood": "gold"},
    "Arco de las Siete Lunas": {"wood": "steel"},
    "El Vigía del Páramo": {"wood": "ceramic"},
    "La Flecha que Vuelve": {"wood": "red"},
}
CLASS_LOOKS = {
    "guerrero": ("male", [("body", "light"), ("heads_human_male", "light"), ("face_neutral", "light"), ("hair_plain", "dark_brown"),
                          ("beards_beard", "dark_brown"), ("legs_pants", "brown"), ("torso_clothes_longsleeve", "white")]),
    "cazadora": ("female", [("body", "olive"), ("heads_human_female", "olive"), ("face_neutral", "olive"), ("hair_ponytail", "black"),
                            ("legs_pants", "forest"), ("torso_clothes_longsleeve", "tan")]),
    "chaman": ("male", [("body", "brown"), ("heads_human_male", "brown"), ("face_neutral", "brown"), ("hair_long", "black"),
                        ("legs_pants", "tan"), ("torso_clothes_sleeveless", "white")]),
}


# ---------------------------------------------------------------- monsters
# Humanoid monsters and most bosses are built from the generator, like the player.
MONSTER_LOOKS = {
    "osamenta": ("male", [("body_skeleton", None), ("heads_skeleton", None), ("weapon_sword_dagger", None)]),
    "ahogado": ("male", [("body_zombie", None), ("heads_zombie", None), ("legs_pants", "navy"), ("torso_clothes_sleeveless", "gray"),
                         ("weapon_polearm_spear", None)]),
    "momia": ("male", [("body", "taupe"), ("heads_human_male_gaunt", "taupe"), ("legs_pants", "tan"), ("torso_bandages", None)]),
    "caiman": ("male", [("body", "dark_green"), ("heads_lizard_male", "dark_green"), ("legs_pants", "brown"),
                        ("torso_clothes_vest", None), ("weapon_polearm_spear", None)]),
    "silbon": ("male", [("body", "taupe"), ("heads_human_male_gaunt", "taupe"), ("legs_pants", "black"),
                        ("torso_clothes_longsleeve", "charcoal"), ("cape_tattered", "black"), ("hat_cap_cavalier", "black")]),
    "mohan": ("male", [("body", "green"), ("heads_troll", "green"), ("hair_long_messy", "gray"), ("beards_beard", "gray"),
                       ("legs_pants", "brown"), ("cape_tattered", "forest"), ("weapon_polearm_spear", None)]),
    "madremonte": ("female", [("body", "dark_green"), ("heads_human_female", "dark_green"), ("face_neutral", "dark_green"),
                              ("hair_long_messy", "green"), ("torso_clothes_robe", "forest green"), ("cape_tattered", "green")]),
    "llorona": ("female", [("body", "light"), ("heads_vampire", "light"), ("hair_long", "black"),
                           ("torso_clothes_robe", "white"), ("cape_tattered", "white")]),
    "mandingas": ("male", [("body", "bronze"), ("heads_human_male", "bronze"), ("face_neutral", "bronze"), ("head_horns_curled", "black"),
                           ("beards_beard", "black"), ("legs_pants", "black"), ("torso_clothes_longsleeve", "black"), ("cape_solid", "red")]),
}

# Animals and creatures: LPC-style sheets from OpenGameArt. src = (download, member of the zip or None),
# pick = ("grid", w, h, col, row) or ("blob", n): the n-th separate sprite on the sheet, top to bottom.
OGA = "https://opengameart.org/sites/default/files/"
MON_PACK = ("lpc-monsters.zip", None)
def M(name): return ("lpc-monsters.zip", f"lpc-monsters/{name}.png")
CREATURES = {
    "espanto":     dict(src=M("ghost"), pick=("grid", 64, 64, 0, 2), sat=0.25, light=1.15, credit="monsters"),
    "cuervo":      dict(src=("birds_1.png", None), pick=("blob", 1), credit="raven"),
    "frailejon":   dict(src=M("man_eater_flower"), pick=("grid", 128, 128, 0, 2), credit="monsters"),
    "lobo":        dict(src=("wolfsheet1.png", None), pick=("rect", 320, 0, 64, 64), flip=True, credit="wolf"),
    "sapo":        dict(src=("frogman_1.png", None), pick=("blob", 8), credit="frogman"),
    "sanguijuela": dict(src=M("big_worm"), pick=("grid", 64, 64, 0, 2), hue=-25, credit="monsters"),
    "arana":       dict(src=("LPC_Spiders.zip", "LPC_Spiders/spider01.png"), pick=("blob", 8), credit="spider"),
    "coral":       dict(src=("snake-NESW.png", None), pick=("blob", 5), hue=185, sat=1.4, credit="snake"),
    "mico":        dict(src=("rat_1.png", None), pick=("blob", 4), credit="rat"),
    "avispa":      dict(src=M("bee"), pick=("grid", 32, 32, 0, 0), hue=-20, credit="monsters"),
    "toro":        dict(src=("bull_1.png", None), pick=("blob", 4), dark=0.28, credit="bull"),
    "jinete":      dict(src=("lpc_boarman.zip", "LPC Boarman/Boarman/Walk.png"), pick=("grid", 64, 64, 0, 2), credit="boarman"),
    "alacran":     dict(src=("lpc_centipede.zip", "[LPC] Centipede/png/lpc_centipede.png"), pick=("blob", 6), credit="centipede"),
    "chulo":       dict(src=("bird_2_black.png", None), pick=("blob", 3), credit="birds"),
    "guardian":    dict(src=("golem-walk.png", None), pick=("blob", 4), credit="golem"),
    "vampiro":     dict(src=("bat_2.png", None), pick=("blob", 8), credit="bat"),
    "duende":      dict(src=("goblin_0.png", None), pick=("blob", 2), credit="goblin"),
    "diablillo":   dict(src=("LPC%20imp_0.zip", "LPC imp/walk - vanilla.png"), pick=("blob", 7), credit="imp"),
    "baba":        dict(src=M("slime"), pick=("grid", 64, 64, 2, 2), credit="monsters"),
    "zaino":       dict(src=("boar.png", None), pick=("blob", 3), flip=True, credit="pigs"),
    "oso":         dict(src=("lpc_animals_2022_v1.1.zip", "lpc animals 2022 v1.1/individual creature spritesheets/bear, black.png"), pick=("blob", 5), flip=True, credit="bears"),
    # easy mode: smaller cousins
    "babosa":      dict(src=M("slime"), pick=("grid", 64, 64, 0, 2), hue=40, light=1.2, scale=0.8, credit="monsters"),
    "sapito":      dict(src=("frogman_1.png", None), pick=("blob", 8), scale=0.7, hue=25, credit="frogman"),
    "culebrita":   dict(src=M("snake"), pick=("grid", 64, 64, 0, 1), credit="monsters"),
    "duendecillo": dict(src=("goblin_0.png", None), pick=("blob", 2), scale=0.75, hue=30, credit="goblin"),
    "cuervito":    dict(src=("birds_1.png", None), pick=("blob", 4), scale=0.75, credit="raven"),
    "murcieguito": dict(src=("bat_2.png", None), pick=("blob", 9), scale=0.8, credit="bat"),
    "jabato":      dict(src=("boar.png", None), pick=("blob", 3), scale=0.7, flip=True, credit="pigs"),
    "conejo":      dict(src=("rabbit_2.png", None), pick=("blob", 4), flip=True, credit="rabbit"),
    # boss
    "bolafuego":   dict(src=M("pumpking"), pick=("grid", 64, 64, 0, 2), credit="monsters"),
}
CREATURE_CREDITS = {
    "monsters": ("[LPC] Monsters", "Charles Sanchez (CharlesGabriel), bagzie, bluecarrot16", "CC-BY-SA 3.0+ / GPL 3.0+", "https://opengameart.org/content/lpc-monsters"),
    "raven": ("LPC Raven and Seagull", "Tuomo Untinen (Reemax)", "CC-BY 3.0 / CC-BY-SA 3.0 / GPL", "https://opengameart.org/content/lpc-raven-and-seagull"),
    "wolf": ("[LPC] Wolf Animation", "Stephen Challener (Redshrike), William.Thompsonj", "CC-BY 3.0 / OGA-BY 3.0 / GPL", "https://opengameart.org/content/lpc-wolf-animation"),
    "frogman": ("LPC Frogman", "Stephen Challener (Redshrike), Evert", "CC-BY 3.0 / OGA-BY 3.0", "https://opengameart.org/content/lpc-frogman"),
    "spider": ("[LPC] Spider", "Stephen Challener (Redshrike), William.Thompsonj", "CC-BY 3.0 / OGA-BY 3.0 / GPL", "https://opengameart.org/content/lpc-spider"),
    "snake": ("Snake Rework", "yolkati, Sebastian Riedel (Baŝto)", "CC-BY-SA 4.0", "https://opengameart.org/content/snake-rework"),
    "rat": ("Rodents (Rat Rework)", "Tuomo Untinen (Reemax), Jordan Irwin (AntumDeluge)", "CC-BY 3.0 / CC-BY-SA 3.0", "https://opengameart.org/content/rodents-rat-rework"),
    "bull": ("LPC bull", "Daniel Eddeland (cow), Nila122 (horns), Evert", "CC-BY-SA 3.0 / GPL 3.0", "https://opengameart.org/content/lpc-bull"),
    "boarman": ("LPC Boarman", "Benjamin K. Smith (BenCreating), dalonedrau, Daniel Eddeland (daneeklu), ElizaWy, Johannes Sjölund (wulax), Stephen Challener (Redshrike), William.Thompsonj; commissioned by castelonia", "CC-BY-SA 3.0 / GPL 3.0", "https://opengameart.org/content/lpc-boarman"),
    "centaur": ("Centaur", "bluecarrot16, Svetlana Kushnariova (Cabbit), Jordan Irwin (AntumDeluge)", "CC-BY 3.0 / OGA-BY 3.0", "https://opengameart.org/content/centaur-0"),
    "centipede": ("[LPC] Centipede", "FiveBrosStopMosYT (thanks to bluecarrot16, bzt, Ragnar Random)", "CC-BY 3.0/4.0", "https://opengameart.org/content/lpc-centipede"),
    "birds": ("[LPC] Birds", "bluecarrot16, commissioned by castelonia", "CC-BY 4.0 / CC-BY-SA / GPL / OGA-BY 3.0", "https://opengameart.org/content/lpc-birds"),
    "golem": ("[LPC] Golem", "Stephen Challener (Redshrike), William.Thompsonj", "CC-BY 3.0 / OGA-BY 3.0 / GPL", "https://opengameart.org/content/lpc-golem"),
    "bat": ("[LPC] Bat combined/extended", "bagzie, bluecarrot16 (extended by Evert)", "OGA-BY 3.0", "https://opengameart.org/content/lpc-bat-combinedextended"),
    "goblin": ("[LPC] Goblin", "Stephen Challener (Redshrike), William.Thompsonj", "CC-BY 3.0 / OGA-BY 3.0 / GPL", "https://opengameart.org/content/lpc-goblin"),
    "imp": ("[LPC] Imp", "Stephen Challener (Redshrike), William.Thompsonj", "CC-BY 3.0 / OGA-BY 3.0 / GPL", "https://opengameart.org/content/lpc-imp"),
    "pigs": ("Pigs Rework", "Daniel Eddeland (daneeklu), Jordan Irwin (AntumDeluge)", "CC-BY 3.0", "https://opengameart.org/content/pigs-rework"),
    "bears": ("[LPC] bears, deer, lions and more", "tapatilorenzo, bluecarrot16 (bear), Sevarihk", "CC-BY 4.0", "https://opengameart.org/content/lpc-bears-deer-lions-and-more"),
    "rabbit": ("Reorganised LPC rabbit", "Stephen Challener (Redshrike), commissioned by Tebruno99 for PixelFarm; Evert", "CC-BY 3.0 / OGA-BY 3.0", "https://opengameart.org/content/reorganised-lpc-rabbit"),
}
USED_CREDITS = set()


def oga_sheet(src):
    """A creature sheet from OpenGameArt, cached in .lpc-cache/oga."""
    fname, member = src
    path = os.path.join(CACHE, "oga", fname.replace("%20", "_"))
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        req = urllib.request.Request(OGA + fname, headers={"User-Agent": "Mozilla/5.0 (leyendas build script)"})
        open(path, "wb").write(urllib.request.urlopen(req, timeout=60).read())
    data = zipfile.ZipFile(path).read(member) if member else open(path, "rb").read()
    return Image.open(io.BytesIO(data)).convert("RGBA")


def blobs(im):
    """Separate sprites on a sheet (alpha islands, grown 2px so a sprite's loose pixels stay together), top to bottom."""
    a = im.split()[3].point(lambda v: 255 if v > 20 else 0).filter(ImageFilter.MaxFilter(5))
    W, H = a.size
    px = a.load()
    seen = bytearray(W * H)
    out = []
    for y in range(H):
        for x in range(W):
            if px[x, y] and not seen[y * W + x]:
                st = [(x, y)]
                seen[y * W + x] = 1
                x0 = x1 = x
                y0 = y1 = y
                while st:
                    cx, cy = st.pop()
                    x0, x1, y0, y1 = min(x0, cx), max(x1, cx), min(y0, cy), max(y1, cy)
                    for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if 0 <= nx < W and 0 <= ny < H and px[nx, ny] and not seen[ny * W + nx]:
                            seen[ny * W + nx] = 1
                            st.append((nx, ny))
                if (x1 - x0) * (y1 - y0) > 60:
                    out.append((x0 + 2, y0 + 2, x1 - 1, y1 - 1))
    return out


def tint(im, hue=0, sat=1.0, light=1.0, dark=None):
    """Hue rotation (degrees), saturation and lightness factors; dark: darken the near-grey pixels (white cow -> black bull)."""
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if not a:
                continue
            h, l, s_ = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
            if dark is not None and s_ < 0.25:
                l *= dark + 0.25 * (1 - l)
            h = (h + hue / 360) % 1
            s_ = min(1, s_ * sat)
            l = min(1, l * light)
            r2, g2, b2 = colorsys.hls_to_rgb(h, l, s_)
            px[x, y] = (round(r2 * 255), round(g2 * 255), round(b2 * 255), a)
    return im


def creature(spec):
    sheet = oga_sheet(spec["src"])
    kind = spec["pick"][0]
    if kind == "grid":
        _, w, h, c, r = spec["pick"]
        im = sheet.crop((c * w, r * h, (c + 1) * w, (r + 1) * h))
    elif kind == "rect":
        _, x, y, w, h = spec["pick"]
        im = sheet.crop((x, y, x + w, y + h))
    else:
        im = sheet.crop(blobs(sheet)[spec["pick"][1]])
    im = im.crop(im.getbbox())
    if spec.get("flip"):
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if any(k in spec for k in ("hue", "sat", "light", "dark")):
        im = tint(im, spec.get("hue", 0), spec.get("sat", 1), spec.get("light", 1), spec.get("dark"))
    USED_CREDITS.add(spec["credit"])
    return im


def colouring_args(col, style, uname=None):
    """(color, variant) for a layer in a given style (rarity, set id or 'unique')."""
    if col is None:
        return None, None
    if style in TOP_STYLES:
        style = "unique"  # coloured as a unique first, then redrawn in the tier's colours
    kind, arg = col
    if kind == "variant":
        return None, arg.get(style) or arg.get("normal")
    if arg.startswith("fixed:"):
        return arg[6:], None
    over = UNIQUE_COLORS.get(uname, {}) if uname else {}
    if style in SETS:
        c = SETS[style][arg]
    else:
        c = over.get(arg) or {"metal": METAL, "cloth": CLOTH, "wood": WOOD}[arg][style]
    return (None, c) if arg == "wood" else (c, None)


# ---------------------------------------------------------------- packing
class Atlas:
    def __init__(self):
        self.frames = []
        self.index = {}

    def add(self, img):
        key = img.tobytes()
        if key in self.index:
            return self.index[key]
        self.frames.append(img)
        self.index[key] = len(self.frames) - 1
        return self.index[key]

    def save(self, path, cols=16):
        rows = (len(self.frames) + cols - 1) // cols
        sheet = Image.new("RGBA", (cols * C, rows * C))
        for i, im in enumerate(self.frames):
            sheet.paste(im, ((i % cols) * C, (i // cols) * C))
        sheet.save(path, optimize=True)
        return cols


def composite(layers, row):
    im = Image.new("RGBA", (C, C))
    for z, frames in sorted(layers, key=lambda t: t[0]):
        if row in frames:
            im.alpha_composite(frames[row])
    return im


def shelf_pack(imgs, path, W=1024):
    x = y = shelf = 0
    rects = {}
    for k, im in sorted(imgs.items(), key=lambda kv: -kv[1].height):
        if x + im.width > W:
            x, y, shelf = 0, y + shelf + 2, 0
        rects[k] = [x, y, im.width, im.height]
        x += im.width + 2
        shelf = max(shelf, im.height)
    out = Image.new("RGBA", (W, y + shelf + 1))
    for k, im in imgs.items():
        out.paste(im, tuple(rects[k][:2]))
    out.save(path, optimize=True)
    return rects


def build():
    dcss = None
    if "--dcss" in sys.argv:
        dcss = sys.argv[sys.argv.index("--dcss") + 1]
    os.makedirs(OUT, exist_ok=True)
    atlas = Atlas()
    looks, icon_imgs = {}, {}

    def store(key, layers):
        looks[key] = [[atlas.add(frames[SOUTH]), z] for z, frames in sorted(layers, key=lambda t: t[0]) if SOUTH in frames
                      and frames[SOUTH].getbbox()]

    SIDE_VIEW = {"guantes", "brazales", "guanteletes", "alpargatas", "botas", "botasviaje", "grebas",
                 "munequeras", "guantescetrero", "zapatos", "botasmontar", "botaspunta", *(b for b in BAND_LOOKS if b.startswith(("guantes", "brazales", "grebas", "botas", "zapatos", "pezunas"))), "zapatillasastral"}

    def icon_from(layers, base=None):
        # gloves and boots: from the side, so it's one hand or foot instead of two far apart
        best = None
        for row in ((EAST,) if base in SIDE_VIEW else (SOUTH, EAST)):
            im = composite(layers, row)
            bb = im.getbbox()
            if bb and (best is None or (bb[2] - bb[0]) * (bb[3] - bb[1]) > best[0]):
                best = ((bb[2] - bb[0]) * (bb[3] - bb[1]), im.crop(bb))
        return best[1] if best else None

    anim = AnimStore(os.path.join(OUT, "anim"))
    for cls, (body, parts) in CLASS_LOOKS.items():
        print("class", cls)
        layers, alayers = [], []
        for name, color in parts:
            layers += layer_frames(name, body, color=color, head=body)
            alayers += anim_layers(name, body, color=color, head=body)
        store(f"class:{cls}", layers)
        anim.add(f"class:{cls}", alayers)

    from_data = json.loads(open(os.path.join(ROOT, "scripts", "lpc_items.json"), encoding="utf-8").read())
    styles = ["low", "normal", "magic", "rare", "unique"]
    for base, parts in BASE_LOOKS.items():
        print("item", base)
        wanted = [(s, None) for s in styles + list(TOP_STYLES)]
        wanted += [(sid, None) for sid in from_data["sets"].get(base, []) if sid in SETS]  # the first three top-tier sets have no art of their own here
        wanted += [("unique", u) for u in from_data["uniques"].get(base, [])]
        for style, uname in wanted:
            key_style = f"u:{uname}" if uname else style
            for body in ("male", "female"):
                layers, alayers = [], []
                own = SET_LOOKS.get(style, {}).get(base)
                for name, col in (own or parts) + (UNIQUE_EXTRA.get(uname, []) if uname else []) + top_extra(style, base):
                    color, variant = colouring_args(col, style, uname)
                    layers += layer_frames(name, body, color=color, variant=variant)
                    alayers += anim_layers(name, body, color=color, variant=variant)
                if style in TOP_STYLES:
                    layers, alayers = gmap_layers(layers, TOP_STYLES[style]), gmap_anim(alayers, TOP_STYLES[style])
                store(f"item:{base}:{key_style}:{body}", layers)
                anim.add(f"item:{base}:{key_style}:{body}", alayers)
                if body == "male" and not base.startswith(("faja", "cinturon")):
                    ic = icon_from(layers, base)
                    if ic:
                        icon_imgs[f"item:{base}:{key_style}"] = ic

    # the high bands: one look in the band's material, and the three top tiers' looks over it
    for base, parts in BAND_LOOKS.items():
        print("band item", base)
        band = BAND_OF[base]
        sets_here = [sid for sid in from_data["sets"].get(base, []) if sid in SET_BAND_STOPS]
        for style in ["normal", *TOP_STYLES, *sets_here]:
            main_, acc_ = SET_BAND_STOPS.get(style, (BAND_STOPS[band], BAND_ACCENT[band]))
            for body in ("male", "female"):
                layers, alayers = [], []
                orig = ORIG.has_art(style, base)  # the bodhisattva and Guru Rinpoche sets: all drawn in scripts/orig_art.py
                if orig:
                    layers, alayers = ORIG.piece(sys.modules[__name__], style, base, body, main_, acc_)
                for name, acc in ([] if orig else SET_BAND_LOOKS.get(style, {}).get(base, parts)):
                    lf, af = layer_frames(name, body), anim_layers(name, body)
                    stops = acc_ if acc else main_
                    layers += gmap_layers(lf, stops)
                    alayers += gmap_anim(af, stops)
                if style in TOP_STYLES:  # the tier's colours over the band's shapes (the accents stay brighter)
                    layers, alayers = gmap_layers(layers, TOP_STYLES[style]), gmap_anim(alayers, TOP_STYLES[style])
                if style in SET_ART.RECIPES:  # the sets from 138 up: drawn hats and effects (scripts/set_art.py)
                    layers, alayers = SET_ART.piece(style, base, layers, alayers, main_, acc_, hat=not orig)
                if style == "arhuaco":  # the tutusoma and the mochila, drawn in scripts/custom_art.py
                    sys.path.insert(0, os.path.join(ROOT, "scripts"))
                    from custom_art import arhuaco_piece
                    layers, alayers = arhuaco_piece(base, layers, alayers)
                store(f"item:{base}:{style}:{body}", layers)
                anim.add(f"item:{base}:{style}:{body}", alayers)
                if body == "male":
                    ic = icon_from(layers, base)
                    if ic:
                        icon_imgs[f"item:{base}:{style}"] = ic

    # the three top-tier sets: original icons and the ornaments worn with them (scripts/custom_art.py)
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from custom_art import custom_icons, custom_looks
    icon_imgs.update(custom_icons())
    icon_imgs.update(SET_ART.piece_icons(SET_BAND_STOPS))  # gloves, boots, belts and rings of the sets from 138 up
    import build_scenes  # noqa: E402  the sets' colours for their undershirts (also hung on the Camisetas rack)
    icon_imgs.update(SET_ART.shirt_icons(build_scenes.NECKLACES))  # each set's magic undershirt
    # the tunjo's rainbow items: a drawn icon each, and their base's shape worn in rainbow (scripts/tunjo_art.py)
    import tunjo_art as TUNJO  # noqa: E402
    for tid, look in from_data.get("tunjo", []):
        print("tunjo", tid)
        icon_imgs[f"item:{look}:t:{tid}"] = TUNJO.icon(tid)
        if look not in BASE_LOOKS:
            continue  # rings aren't drawn on the figure
        for body in ("male", "female"):
            layers, alayers = [], []
            for name, col in BASE_LOOKS[look]:
                color, variant = colouring_args(col, "normal", None)
                layers += layer_frames(name, body, color=color, variant=variant)
                alayers += anim_layers(name, body, color=color, variant=variant)
            layers = [(z, {k: TUNJO.rainbow(im) for k, im in fr.items()}) for z, fr in layers]
            alayers = [(z, {a: (TUNJO.rainbow(im, fs), fs, n) for a, (im, fs, n) in rows.items()}) for z, rows in alayers]
            store(f"item:{look}:t:{tid}:{body}", layers)
            anim.add(f"item:{look}:t:{tid}:{body}", alayers)
    for key, layers, alayers in custom_looks():
        print("ornament", key)
        store(key, layers)
        anim.add(key, alayers)

    # rings: Dungeon Crawl tiles (CC0), 32px, cached so later builds don't need --dcss
    # LPC rings don't exist and LPC gloves are a few pixels: these icons come from Dungeon Crawl
    gloves = ["armour/glove1", "armour/glove2", "armour/glove3", "armour/glove4", "armour/glove5"]
    ring_tiles = {"anillo": ["ring/i-protection", "ring/i-str", "ring/i-dex", "ring/i-int", "ring/i-magical-power"],
                  "sortija": ["ring/ruby", "ring/tourmaline", "ring/i-r-fire", "ring/i-r-cold", "ring/i-wizardry"],
                  "guantes": gloves, "brazales": gloves[1:] + gloves[:1], "guanteletes": gloves[2:] + gloves[:2]}
    ring_cache = os.path.join(CACHE, "dcss-rings")
    os.makedirs(ring_cache, exist_ok=True)
    for base, names in ring_tiles.items():
        for style, name in zip(styles, names):
            dst = os.path.join(ring_cache, name.replace("/", "_") + ".png")
            if not os.path.exists(dst) and dcss:
                shutil.copy(os.path.join(dcss, "item", name + ".png"), dst)
            if os.path.exists(dst):
                im = Image.open(dst).convert("RGBA")
                icon_imgs[f"item:{base}:{style}"] = im.crop(im.getbbox())
                if style == "unique":
                    for top, stops in TOP_STYLES.items():
                        icon_imgs[f"item:{base}:{top}"] = gmap(im.crop(im.getbbox()), stops)

    # monsters: one cropped picture each, scale stored so a bat stays smaller than a bear
    mon_imgs, mon_scale = {}, {}
    for mid, (body, parts) in MONSTER_LOOKS.items():
        print("monster", mid)
        layers = []
        for name, color in parts:
            layers += layer_frames(name, body, color=color, head=body)
        im = composite(layers, SOUTH)
        mon_imgs[mid] = im.crop(im.getbbox())
    for mid, spec in CREATURES.items():
        print("creature", mid)
        mon_imgs[mid] = creature(spec)
        if spec.get("scale"):
            mon_scale[mid] = spec["scale"]
    mon_rects = shelf_pack(mon_imgs, os.path.join(OUT, "monsters.png"))
    for k, v in mon_scale.items():
        mon_rects[k].append(v)

    # icon atlas: simple shelf packing
    W = 1024
    x = y = shelf = 0
    rects = {}
    order = sorted(icon_imgs.items(), key=lambda kv: -kv[1].height)
    for k, im in order:
        if x + im.width > W:
            x, y, shelf = 0, y + shelf + 2, 0
        rects[k] = [x, y, im.width, im.height]
        x += im.width + 2
        shelf = max(shelf, im.height)
    icons = Image.new("RGBA", (W, y + shelf + 1))
    for k, im in icon_imgs.items():
        icons.paste(im, tuple(rects[k][:2]))
    icons.save(os.path.join(OUT, "icons.png"), optimize=True)

    cols = atlas.save(os.path.join(OUT, "atlas.png"))
    json.dump({"frame": C, "cols": cols, "looks": looks, "icons": rects, "monsters": mon_rects},
              open(os.path.join(OUT, "atlas.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"{len(atlas.frames)} frames, {len(looks)} looks, {len(rects)} icons")
    attacks = {base: attack_anim(parts[0][0]) for base, parts in BASE_LOOKS.items() if parts[0][0].startswith(("weapon_", "tool_"))}
    json.dump({"anims": ANIMS, "attack": attacks, "looks": anim.looks},
              open(os.path.join(OUT, "anim.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"{len(anim.files)} animation sheets for {len(anim.looks)} looks")
    make_favicon(atlas, looks)
    write_credits()


def make_favicon(atlas, looks):
    """The warrior's head, from the same art: public/favicon.png (64px) and apple-touch-icon.png (180px)."""
    im = Image.new("RGBA", (C, C))
    for f, z in looks["class:guerrero"] + looks["item:casco:magic:male"]:
        im.alpha_composite(atlas.frames[f])
    o = (C - F) // 2
    head = im.crop((o + 16, o + 9, o + 48, o + 41))  # 32x32 around the head
    pub = os.path.dirname(os.path.dirname(OUT))
    head.resize((64, 64), Image.NEAREST).save(os.path.join(pub, "favicon.png"))
    bg = Image.new("RGBA", (180, 180), (32, 26, 20, 255))
    bg.alpha_composite(head.resize((160, 160), Image.NEAREST), (10, 14))
    bg.save(os.path.join(pub, "apple-touch-icon.png"))


def write_credits():
    rows = list(csv.DictReader(io.StringIO(fetch("CREDITS.csv").decode("utf-8"))))
    by = {r["filename"].strip(): r for r in rows}
    lines = ["Character and item art: Universal LPC Spritesheet Character Generator",
             "https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator",
             "Recoloured with the LPC palettes and cropped for Leyendas. Licences as listed per file.",
             "Ring and glove icons: Dungeon Crawl Stone Soup tiles (CC0), https://github.com/crawl/tiles",
             "The icons of the sets Gesta del Cóndor and La Voz del Origen, and the wings, rings and motes worn with them,",
             "are original art drawn in code for Leyendas (scripts/custom_art.py).", ""]
    for f in sorted(USED_FILES):
        # credits are listed per animation file; a variant file is credited by its folder
        r = by.get(f)
        if not r:
            stem = re.sub(r"/walk/[^/]+\.png$", "/walk.png", f)
            r = by.get(stem) or next((v for k, v in by.items() if k.startswith(os.path.dirname(f) + "/")), None) \
                or next((v for k, v in by.items() if k.startswith(os.path.dirname(os.path.dirname(f)) + "/")), None)
        if r:
            lines.append(f"{f}\n  by {r['authors'].strip()}\n  licence: {r['licenses'].strip()}\n  {r['notes'].strip()}\n  {r['urls'].strip()}\n")
        else:
            lines.append(f"{f}\n  (see the generator's CREDITS.csv)\n")
    lines += ["", "Monster art: LPC-style creature sheets from OpenGameArt.org, cropped (some recoloured, flipped or scaled) for Leyendas.", ""]
    for k in sorted(USED_CREDITS):
        title, by, lic, url = CREATURE_CREDITS[k]
        lines.append(f"{title}\n  by {by}\n  licence: {lic}\n  {url}\n")
    open(os.path.join(OUT, "CREDITS.txt"), "w", encoding="utf-8").write("\n".join(lines))


if __name__ == "__main__":
    build()
