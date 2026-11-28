"""One-off (2026-11-27): writes the zones of scripts/zones_more.py and the bosses of scripts/zones_bosses.py
into public/rpg/data.js: their monsters (MONSTERS, MONSTER_RES), their bosses (BOSSES, MONSTER_RES) and
ZONE_VARIANTS, the zones each of the road's six slots can draw. Refuses if they're already there.
usage: python3 scripts/new_zones.py
"""
import json
import os

import zones_bosses as ZB
import zones_more as Z

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def js(v):
    return json.dumps(v, ensure_ascii=False)


def obj(d):
    return "{ " + ", ".join(f"{k}: {js(v)}" for k, v in d.items() if v is not None) + " }"


def special(sp):
    kind, name, every, mult = sp[:4]
    out = {"name": name, "every": every, "mult": mult}
    if kind == "hit":
        ready, hit, dodge = sp[4:7]
        out.update(ready=f"{ready} <b>Solo una frase perfecta</b> te aparta.", hit=hit, dodge=dodge)
    elif kind == "steal":
        ready, hit, dodge = sp[4:7]
        out.update(steal=True, ready=f"{ready} <b>Solo una frase perfecta</b> te deja pasar.", hit=hit, dodge=dodge)
    elif kind == "tangle":
        ready, lead, dodge, bound, warn, pron = sp[4:10]
        out.update(tangle=2, heal=0.08, bound=bound, boundWarn=warn, ready=f"{ready} <b>Solo una frase perfecta</b> te libra.",
                   hit=f"{lead}: <b>2 frases sin Despacio ni Pista</b>, y {pron} se cura.", dodge=dodge)
    elif kind == "burn":
        ready, lead, dodge = sp[4:7]
        out.update(burn=3, ready=f"{ready} <b>Solo una frase perfecta</b> te aparta.",
                   hit=f"{lead}: <b>ardes</b> durante 3 turnos. Una frase perfecta apaga el fuego.", dodge=dodge)
    elif kind == "wail":
        ready, hit, dodge, word = sp[4:8]
        noun = {"llanto": "llanto", "grito": "grito", "bramido": "bramido"}[word]
        out.update(wail=word, ready=f"{ready} <b>Su {noun} sonará encima de la próxima frase</b>: solo una frase perfecta te protege.", hit=hit, dodge=dodge)
    return out


def p2(t):
    kind, val, text = t
    if kind == "summon":
        return {"summon": [val, 2], "text": text}
    return {kind: val, "text": text}


def main():
    p = os.path.join(ROOT, "public", "rpg", "data.js")
    s = open(p, encoding="utf-8").read()
    if "export const ZONE_VARIANTS" in s:
        raise SystemExit("already there")

    def ins_before_end(anchor, text):
        nonlocal s
        i = s.index(anchor)
        j = s.index("\n};", i)
        s = s[:j] + text + s[j:]

    mons, res = [], []
    for z in Z.all_zones():
        mons.append(f"  // {z['name']}")
        for m in z["monsters"]:
            d = {"name": m["name"], "icon": m["icon"], "color": m["color"], "hp": m["hp"], "dmg": m["dmg"], "el": Z.ELEM.get(m["tag"])}
            mons.append(f"  {m['id']}: {obj(d)},")
            res.append(f"  {m['id']}: {obj(Z.RES[m['tag']])},")
    ins_before_end("export const MONSTERS = {", "\n  // the zones added on 2026-11-27 (scripts/zones_more.py; drawn by scripts/build_monsters_kit.py)\n" + "\n".join(mons))
    bres = {"fire": {"fire": 100, "cold": -50}, "cold": {"cold": 100, "fire": -50}, "poison": {"poison": 100, "fire": -50},
            "light": {"light": 100, "poison": -25}, None: {"poison": 50, "light": -25}}
    for b in ZB.BOSSES:
        res.append(f"  {b['id']}: {obj(bres[b['el']])},")
    ins_before_end("export const MONSTER_RES = {", "\n  // the 2026-11-27 zones' monsters and bosses\n" + "\n".join(res))
    lines = ["  // the 2026-11-27 zones' bosses (scripts/zones_bosses.py; art: scripts/build_bosses_kit.py)"]
    for b in ZB.BOSSES:
        d = {"name": b["name"], "title": b["title"], "icon": b["icon"], "color": b["color"], "hp": b["hp"], "dmg": b["dmg"], "el": b["el"],
             "mods": b["mods"], "minions": b["minion"], "intro": b["intro"], "special": special(b["special"]), "p2": p2(b["p2"]), "last": b["last"]}
        lines.append(f"  {b['id']}: {js(d)},")
    ins_before_end("export const BOSSES = {", "\n" + "\n".join(lines))
    # the variants, after ZONES
    by = {}
    for z in Z.all_zones():
        by.setdefault(z["slot"], []).append({
            "id": z["id"], "name": z["name"], "blurb": z["blurb"], "monsters": [m["id"] for m in z["monsters"]],
            "bosses": [b["id"] for b in ZB.BOSSES if b["zone"] == z["id"]], "easy": z["easy"], "fx": z["fx"], "music": z["music"],
            **({"descents": z["descents"]} if z["descents"] else {})})
    text = ("\n\n// The other zones each slot of the road can be (2026-11-27, scripts/zones_more.py). Each episode draws one per\n"
            "// slot, the slot's own zone above included, and keeps it until it's restarted (main.js zonePick). A variant\n"
            "// lends the slot its name, scene, monsters, bosses, easy roster, particles and music; levels and progress\n"
            "// stay the slot's. descents: the Abismo's, named (the Tibetan hells), one per descent, then numbered.\n"
            "export const ZONE_VARIANTS = {\n" + "".join(f"  {k}: [\n" + "".join(f"    {js(v)},\n" for v in vs) + "  ],\n" for k, vs in by.items()) + "};\n")
    i = s.index("export const ZONES = [")
    j = s.index("\n];", i) + 3
    s = s[:j] + text + s[j:]
    open(p, "w", encoding="utf-8").write(s)
    print("ok", len(mons), len(ZB.BOSSES))


if __name__ == "__main__":
    main()
