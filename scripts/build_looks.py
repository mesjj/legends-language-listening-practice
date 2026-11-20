"""Build the parts of the player's look (body, head, face, hair, beard, clothes ...) for the
character editor, from the Universal LPC Spritesheet Character Generator.

Every part is stored once, in its LPC base colours (light skin, orange hair, blue eyes, white
cloth), as an animation sheet like the ones in lpc/anim/. The game recolours them in the browser
with the LPC palettes written next to them, so any skin, hair, eye and cloth colour costs nothing.

  public/rpg/lpc/look/*.png         one sheet per part (deduplicated)
  public/rpg/lpc/look.json          slots, options, palettes and where each sheet's rows are
  public/rpg/lpc/CREDITS-looks.txt  authors and licences of every LPC file used (required)

usage: .venv/bin/python scripts/build_looks.py
"""
import csv
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_lpc as B  # noqa: E402

BODIES = ("male", "female")
HEAD_KINDS = ("male", "female", "elderly")

# (option id, Spanish label, sheet definition path under sheet_definitions/)
HEADS = [
    ("human_male", "Rasgos marcados", "head/heads/human/heads_human_male", "male"),
    ("human_female", "Rasgos suaves", "head/heads/human/heads_human_female", "female"),
    ("male_plump", "Cara redonda", "head/heads/human/heads_human_male_plump", "male"),
    ("male_gaunt", "Cara chupada", "head/heads/human/heads_human_male_gaunt", "male"),
    ("male_elderly", "Anciano", "head/heads/human/heads_human_male_elderly", "elderly"),
    ("female_elderly", "Anciana", "head/heads/human/heads_human_female_elderly", "elderly"),
]
FACES = [
    ("neutral", "Serena", "head/faces/face_neutral"), ("happy", "Alegre", "head/faces/face_happy"),
    ("angry", "Enfadada", "head/faces/face_angry"), ("sad", "Triste", "head/faces/face_sad"),
    ("shock", "Asombrada", "head/faces/face_shock"), ("closed", "Ojos cerrados", "head/faces/face_closed"),
]
NOSES = [("big", "Grande", "head/nose/head_nose_big"), ("button", "Respingada", "head/nose/head_nose_button"),
         ("straight", "Recta", "head/nose/head_nose_straight"), ("large", "Ancha", "head/nose/head_nose_large"),
         ("elderly", "De anciano", "head/nose/head_nose_elderly")]
EARS = [("elven", "Élficas", "head/ears/head_ears_elven"), ("medium", "Puntiagudas", "head/ears/head_ears_medium"),
        ("big", "Grandes", "head/ears/head_ears_big"), ("long", "Muy largas", "head/ears/head_ears_long"),
        ("down", "Caídas", "head/ears/head_ears_down")]
BROWS = [("thick", "Pobladas", "head/eyebrows/eyebrows_thick"), ("thin", "Finas", "head/eyebrows/eyebrows_thin")]
WRINKLES = [("wrinkles", "Arrugas", "head/head_wrinkles")]
HAIR = [
    ("plain", "Corto", "hair/short/hair_plain"), ("buzzcut", "Rapado", "hair/bald/hair_buzzcut"),
    ("balding", "Entradas", "hair/bald/hair_balding"), ("high_and_tight", "Militar", "hair/bald/hair_high_and_tight"),
    ("parted", "Raya al lado", "hair/short/hair_parted"), ("messy", "Despeinado", "hair/short/hair_messy1"),
    ("bedhead", "Recién levantado", "hair/short/hair_bedhead"), ("pixie", "Pixie", "hair/short/hair_pixie"),
    ("bangs", "Flequillo", "hair/short/hair_bangs"), ("mop", "Tazón", "hair/short/hair_mop"),
    ("spiked", "De punta", "hair/spiky/hair_spiked"), ("shorthawk", "Cresta", "hair/bald/hair_shorthawk"),
    ("longhawk", "Cresta larga", "hair/bald/hair_longhawk"),
    ("bob", "Melena corta", "hair/bob/hair_bob"), ("lob", "Media melena", "hair/bob/hair_lob"),
    ("long", "Largo", "hair/long/hair_long"), ("long_straight", "Largo y liso", "hair/long/hair_long_straight"),
    ("wavy", "Ondulado", "hair/long/hair_wavy"), ("long_messy", "Largo revuelto", "hair/long/hair_long_messy"),
    ("loose", "Suelto", "hair/long/hair_loose"), ("xlong", "Muy largo", "hair/xlong/hair_xlong"),
    ("xlong_wavy", "Muy largo ondulado", "hair/xlong/hair_xlong_wavy"),
    ("ponytail", "Coleta", "hair/braids/hair_ponytail"), ("high_ponytail", "Coleta alta", "hair/braids/hair_high_ponytail"),
    ("braid", "Trenza", "hair/braids/hair_braid"), ("pigtails", "Dos coletas", "hair/pigtails/hair_pigtails"),
    ("bun", "Moño", "hair/braids/hair_topknot_short"), ("bangs_bun", "Moño con flequillo", "hair/braids/hair_bangs_bun"),
    ("half_up", "Semirrecogido", "hair/braids/hair_half_up"),
    ("curly_short", "Rizado corto", "hair/curly/hair_curly_short"), ("curly_long", "Rizado largo", "hair/curly/hair_curly_long"),
    ("curls_large", "Rizos grandes", "hair/curly/hair_curls_large"), ("afro", "Afro", "hair/afro/hair_afro"),
    ("natural", "Natural", "hair/afro/hair_natural"), ("cornrows", "Trenzas pegadas", "hair/afro/hair_cornrows"),
    ("dreadlocks_short", "Rastas cortas", "hair/afro/hair_dreadlocks_short"), ("dreadlocks_long", "Rastas largas", "hair/afro/hair_dreadlocks_long"),
    ("twists", "Twists", "hair/afro/hair_twists_straight"), ("flat_top", "Flat top", "hair/afro/hair_flat_top_fade"),
]
BEARDS = [("5oclock", "Sombra de barba", "hair/beards/beards_5oclock_shadow"), ("trimmed", "Recortada", "hair/beards/beards_trimmed"),
          ("medium", "Mediana", "hair/beards/beards_medium"), ("beard", "Poblada", "hair/beards/beards_beard"),
          ("winter", "Larga", "hair/beards/beards_winter")]
STACHES = [("mustache", "Bigote", "hair/mustaches/beards_mustache"), ("bigstache", "Bigotón", "hair/mustaches/beards_bigstache"),
           ("handlebar", "Manillar", "hair/mustaches/beards_handlebar"), ("french", "Francés", "hair/mustaches/beards_french"),
           ("walrus", "Morsa", "hair/mustaches/beards_walrus"), ("chevron", "Chevron", "hair/mustaches/beards_chevron"),
           ("horseshoe", "Herradura", "hair/mustaches/beards_horseshoe")]
SHIRTS = [("longsleeve", "Manga larga", "torso/shirts/longsleeve/torso_clothes_longsleeve"),
          ("laced", "Con cordones", "torso/shirts/longsleeve/torso_clothes_longsleeve_laced"),
          ("tshirt", "Camiseta", "torso/shirts/shortsleeve/torso_clothes_tshirt"),
          ("sleeveless", "Sin mangas", "torso/shirts/sleeveless/torso_clothes_sleeveless"),
          ("tanktop", "Tirantes", "torso/shirts/sleeveless/torso_clothes_sleeveless_tanktop"),
          ("tunic", "Túnica", "torso/shirts/torso_clothes_tunic"),
          ("blouse", "Blusa", "torso/shirts/torso_clothes_blouse"),
          ("blouse_long", "Blusa de manga larga", "torso/shirts/torso_clothes_blouse_longsleeve"),
          ("corset", "Corsé", "torso/shirts/torso_clothes_corset")]
LEGS = [("pants", "Pantalón", "legs/pants/legs_pants"), ("widepants", "Pantalón ancho", "legs/pants/legs_widepants"),
        ("pantaloons", "Bombachos", "legs/pants/legs_pantaloons"), ("cuffed", "Remangado", "legs/pants/legs_cuffed"),
        ("skirt", "Falda", "legs/skirts/legs_skirts_plain"), ("skirt_slit", "Falda con abertura", "legs/skirts/legs_skirts_slit"),
        ("overskirt", "Falda larga", "legs/skirts/legs_skirt_overskirt")]

# slot id, label, options, which colours recolour it, which colour choice it follows, can be left out
SLOTS = [
    ("head", "Cara", HEADS, ["body", "eye"], None, False),
    ("face", "Expresión", FACES, ["body", "eye"], None, False),
    ("nose", "Nariz", NOSES, ["body"], None, True),
    ("ears", "Orejas", EARS, ["body"], None, True),
    ("wrinkles", "Arrugas", WRINKLES, ["body"], None, True),
    ("brows", "Cejas", BROWS, ["hair"], "hairColor", True),
    ("hair", "Pelo", HAIR, ["hair"], "hairColor", True),
    ("beard", "Barba", BEARDS, ["hair"], "hairColor", True),
    ("stache", "Bigote", STACHES, ["hair"], "hairColor", True),
    ("shirt", "Camisa", SHIRTS, ["cloth"], "shirtColor", True),
    ("legs", "Piernas", LEGS, ["cloth"], "legsColor", False),
]

# colour choices, in palette names, with their Spanish names
COLORS = {
    "body": [("light", "Clara"), ("amber", "Ámbar"), ("olive", "Oliva"), ("taupe", "Trigueña"), ("bronze", "Bronce"),
             ("brown", "Morena"), ("black", "Negra"), ("lavender", "Lavanda"), ("blue", "Azul"), ("green", "Verde"),
             ("zombie_green", "Pálida verdosa")],
    "eye": [("brown", "Marrones"), ("blue", "Azules"), ("green", "Verdes"), ("gray", "Grises"), ("purple", "Violetas"),
            ("red", "Rojos"), ("orange", "Ámbar"), ("yellow", "Dorados")],
    "hair": [("black", "Negro"), ("raven", "Azabache"), ("dark_brown", "Castaño oscuro"), ("chestnut", "Castaño"),
             ("light_brown", "Castaño claro"), ("sandy", "Arena"), ("blonde", "Rubio"), ("platinum", "Platino"),
             ("ash", "Ceniza"), ("gray", "Canoso"), ("white", "Blanco"), ("ginger", "Jengibre"), ("redhead", "Pelirrojo"),
             ("red", "Rojo"), ("strawberry", "Fresa"), ("pink", "Rosa"), ("purple", "Morado"), ("blue", "Azul"), ("green", "Verde")],
    "cloth": [("white", "Blanco"), ("gray", "Gris"), ("charcoal", "Carbón"), ("black", "Negro"), ("tan", "Beis"),
              ("leather", "Cuero"), ("brown", "Marrón"), ("walnut", "Nogal"), ("yellow", "Amarillo"), ("orange", "Naranja"),
              ("rose", "Rosa palo"), ("pink", "Rosa"), ("red", "Rojo"), ("maroon", "Granate"), ("lavender", "Lavanda"),
              ("purple", "Morado"), ("sky", "Celeste"), ("blue", "Azul"), ("navy", "Marino"), ("bluegray", "Azul grisáceo"),
              ("slate", "Pizarra"), ("teal", "Verde azulado"), ("green", "Verde"), ("forest", "Verde bosque")],
}
BODY_DEF = "body/body"


def defname(path):
    name = "look:" + path
    B.DEF_PATHS[name] = path
    return name


def sources(path, mats):
    """{material: source colours} where a part isn't drawn in its palette's usual base colours
    (some faces bring their own eye colours, some heads start green)."""
    d = B.sheet_def(defname(path))
    r = d.get("recolors") or {}
    specs = [r] if "material" in r else [v for k, v in sorted(r.items()) if k.startswith("color_")]
    out = {}
    for sp in specs:
        mat = sp.get("material")
        if mat not in mats:
            continue
        if sp.get("source"):
            out[mat] = sp["source"]
        elif sp.get("base") and sp["base"].split(".")[-1] != "None":
            out[mat] = B.palette(mat)[1][sp["base"].split(".")[-1]]
    return out


def variants(path):
    """Colour variants of an item that isn't recoloured with a palette (blouse, corset, tunic)."""
    d = B.sheet_def(defname(path))
    return [] if d.get("recolors") else d.get("variants") or []


def build():
    out = os.path.join(B.ROOT, "public", "rpg", "lpc", "look")
    store = B.AnimStore(out)

    def add(key, path, body, head=None, variant=None):
        layers = B.anim_layers(defname(path), body, head=head, variant=variant)
        if not layers:
            return None
        store.add(key, layers)
        return key

    slots = [{"id": "body", "label": "Cuerpo", "mats": ["body"], "opts": [
        {"id": b, "label": {"male": "Hombre", "female": "Mujer"}[b], "k": {b: add(f"body:{b}", BODY_DEF, b)}} for b in BODIES]}]
    for sid, label, opts, mats, color, optional in SLOTS:
        print("slot", sid)
        S = {"id": sid, "label": label, "mats": mats, "none": optional, "opts": []}
        if color:
            S["color"] = color
        for o in opts:
            oid, olabel, path = o[0], o[1], o[2]
            vs = [c for c, _ in COLORS["cloth"] if c in variants(path)] if "cloth" in mats else []
            if sid == "face":  # a face is drawn for its head's shape: male, female or elderly
                k = {hk: add(f"face:{oid}:{hk}", path, "male", head=hk) for hk in HEAD_KINDS}
            elif vs:  # one sheet per colour
                v = {c: {a: x for a, x in ((b, add(f"{sid}:{oid}:{c}:{b}", path, b, variant=c)) for b in BODIES) if x} for c in vs}
                v = {c: x for c, x in v.items() if x}
                k = v.get("white") or next(iter(v.values()), {})
            else:
                k = {b: add(f"{sid}:{oid}:{b}", path, b) for b in BODIES}
            k = {a: x for a, x in k.items() if x}
            if not k:
                print(f"  ! {oid}: nothing")
                continue
            opt = {"id": oid, "label": olabel, "k": k}
            if vs:
                opt["v"] = v
            src = sources(path, mats)
            if src:
                opt["src"] = src
            if sid == "head":
                opt["kind"] = o[3]
            S["opts"].append(opt)
        slots.append(S)

    pal = {}
    for mat, choices in COLORS.items():
        base, pals = B.palette(mat)
        pal[mat] = {"base": pals[base], "c": {c: pals[c] for c, _ in choices if c in pals},
                    "names": {c: n for c, n in choices if c in pals}}
    json.dump({"anims": B.ANIMS, "slots": slots, "pal": pal, "looks": store.looks},
              open(os.path.join(B.OUT, "look.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"{len(store.files)} sheets for {len(store.looks)} parts")
    write_credits()


def write_credits():
    rows = list(csv.DictReader(io.StringIO(B.fetch("CREDITS.csv").decode("utf-8"))))
    by = {r["filename"].strip(): r for r in rows}
    lines = ["Character look parts (body, heads, faces, hair, beards, clothes):",
             "Universal LPC Spritesheet Character Generator",
             "https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator",
             "Cropped for Leyendas and recoloured in the browser with the LPC palettes. Licences as listed per file.", ""]
    for f in sorted(B.USED_FILES):
        r = by.get(f) or next((v for k, v in by.items() if k.startswith(os.path.dirname(f) + "/")), None) \
            or next((v for k, v in by.items() if k.startswith(os.path.dirname(os.path.dirname(f)) + "/")), None)
        if r:
            lines.append(f"{f}\n  by {r['authors'].strip()}\n  licence: {r['licenses'].strip()}\n  {r['notes'].strip()}\n  {r['urls'].strip()}\n")
        else:
            lines.append(f"{f}\n  (see the generator's CREDITS.csv)\n")
    open(os.path.join(B.OUT, "CREDITS-looks.txt"), "w", encoding="utf-8").write("\n".join(lines))


if __name__ == "__main__":
    build()
