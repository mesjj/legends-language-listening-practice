"""One-off generator (2026-11-27): the 59 sets of levels 404-600, written into data.js, build_lpc.py and
build_scenes.py by new_sets_400.write, the same way as the 204-400 ones.

Each one takes its tier, element, listening, kit, weapon and pieces from the set at the same place in the
204-400 list, so the mix is the same (27 plain, 12 ancestral, 11 legendary, 9 mythic) and no two-handed
weapon comes with a shield. Its piece names are a noun for the piece and a phrase of the set's, in turn.
Its look (new_sets_400_art.py reads LOOK and HATS here): a hat, a body, its colours, a motif and the
colours of its effects; gloves, shoes, belt, shield and wings come from that same 204-400 set.

usage: python3 scripts/new_sets_600.py   (run once; it refuses if the sets are already there)
"""
import new_sets_400 as N4

LO, HI = 404, 600
# id, name, three phrases, hat, body, main colour, accent, motif, effect colours[, wings override]
TABLE = [
    ("villaleyva", "Los Fósiles de Villa de Leyva", ["del Amonita", "de la Plaza Empedrada", "del Kronosaurio"], "STRAW", "weaver", "#8a7a5a", "#e0d0a0", "spiral", ("#f0e0b0",)),
    ("chicamocha", "El Cañón del Chicamocha", ["del Cañón Hondo", "del Viento Seco", "de la Cabra de Monte"], "BANDANA", "leather", "#8a4a2a", "#e0a060", "sun", ("#ffb060",)),
    ("tequendama", "El Salto del Tequendama", ["del Salto", "de la Niebla que Cae", "de Bochica el Viejo"], "hood", "ghost", "#3a5a6a", "#c0e8f0", "drop", ("#c0f0ff", "#ffffff")),
    ("cocora", "El Valle del Cocora", ["de la Palma de Cera", "del Valle Verde", "del Barranquero"], "LEAVES", "cotton", "#3a6a3a", "#a0d070", "leaf", ("#c0f090",)),
    ("tarablanca", "Tara Blanca, la de los Siete Ojos", ["de los Siete Ojos", "de la Larga Vida", "de la Luna Llena"], "LOTUS", "dress", "#e8ecf4", "#c8a040", "eye", ("#ffffff", "#e0f0ff")),
    ("barichara", "Los Caminos de Barichara", ["del Camino Real", "de la Piedra Amarilla", "de la Tapia Pisada"], "STRAW", "tunic", "#b08040", "#f0d890", "dot", ("#ffe0a0",)),
    ("chibchacum", "Chibchacum, el que Carga la Tierra", ["del que Carga la Tierra", "de la Lluvia Castigada", "del Temblor"], "GOLD_BAND", "vest", "#6a5030", "#e0b040", "bolt", ("#ffd060", "#fff4c0")),
    ("laslajas", "El Santuario de Las Lajas", ["del Puente sobre el Guáitara", "de la Piedra Pintada", "del Peregrino"], "hood", "robe", "#6a6a7a", "#e8e0d0", "cross", ("#f0f0ff",)),
    ("gorgona", "La Isla Gorgona", ["de la Ballena Jorobada", "de la Isla de las Serpientes", "del Mar Verde"], "WRAP", "sea", "#1a5a4a", "#6ac0a0", "wave", ("#8af0d0",)),
    ("longchenpa", "Longchenpa, el Espacio Inmenso", ["del Espacio Inmenso", "de los Siete Tesoros", "de la Mente Abierta"], "PANDITA", "monk", "#8a2a2a", "#e8c040", "star", ("#fff0a0", "#ffffff")),
    ("sibundoy", "El Valle de Sibundoy", ["del Arcoíris Kamëntšá", "de la Máscara de Madera", "del Valle Alto"], "FEATHERS", "skirt", "#8a1a2a", "#e8c030", "feather", ("#ff8a4a", "#ffe060")),
    ("furatena", "Fura y Tena", ["de las Dos Rocas", "del Llanto Esmeralda", "del Río Minero"], "VEIL", "dancer", "#1a6a4a", "#8af0b0", "drop", ("#6af0a0", "#ffffff")),
    ("cocuy", "La Sierra del Cocuy", ["del Glaciar", "del Púlpito de Piedra", "del Frailejón Nevado"], "WOOL_CAP", "trench", "#4a5a7a", "#e8f0ff", "moon", ("#e8f0ff",)),
    ("shambhala", "El Reino de Shambhala", ["del Reino Escondido", "de la Rueda de Ocho Radios", "del Rey de la Rueda"], "SUN", "robe", "#3a2a8a", "#f0d040", "sun", ("#ffe070", "#a0a0ff", "#ffffff")),
    ("raquira", "Los Alfareros de Ráquira", ["del Barro Cocido", "del Torno", "de la Vasija Pintada"], "STRAW", "weaver", "#a8582a", "#f0c080", "spiral", ("#ffb070",)),
    ("vajrapani", "Vajrapani, el del Rayo en la Mano", ["del Rayo en la Mano", "de la Fuerza del Buda", "del Guardián Azul"], "WRATH", "plate", "#1a3aa8", "#f0c040", "bolt", ("#6a8aff", "#ffffff")),
    ("popayan", "La Ciudad Blanca de Popayán", ["de las Procesiones", "de la Ciudad Blanca", "del Puente del Humilladero"], "hood", "noble", "#d8d8d0", "#3a3a5a", "cross", ("#ffffff",)),
    ("galeras", "El Volcán Galeras", ["del Cráter Humeante", "de la Ceniza Gris", "del Fuego de Pasto"], "HORNS", "plate", "#3a2a2a", "#ff7a2a", "ember", ("#ff8a3a", "#ffd080")),
    ("sumapaz", "El Páramo de Sumapaz", ["del Páramo Inmenso", "de la Laguna Fría", "del Oso de Anteojos"], "WOOL_CAP", "cotton", "#4a6a5a", "#d8e8c0", "moss", ("#d8f0c0",)),
    ("maitreya", "Maitreya, el que Vendrá", ["del que Vendrá", "del Cielo Tushita", "de la Bondad Amorosa"], "FIVE", "robe", "#e0a040", "#ffffff", "sun", ("#ffffff", "#ffe080", "#ffc0e0")),
    ("cienagagrande", "La Ciénaga Grande", ["de los Palafitos", "del Manglar", "de la Red del Pescador"], "STRAW", "sea", "#4a6a5a", "#c8b070", "shell", ("#a0e0d0",)),
    ("juantama", "Juan Tama, Hijo de la Estrella", ["de la Estrella", "de la Laguna de Juan Tama", "del Bastón de Mando"], "FEATHERS", "vest", "#2a3a2a", "#e0e040", "star", ("#fff48a",)),
    ("duende", "El Duende de la Quebrada", ["del Duende", "de la Quebrada Oscura", "del Sombrero Grande"], "VUELTIAO", "trench", "#2a3a1a", "#a0c040", "eye", ("#c0f060",)),
    ("atisha", "Atisha, la Lámpara del Camino", ["de la Lámpara del Camino", "del Mar de Sumatra", "del Corazón Tierno"], "PANDITA", "monk", "#b02a2a", "#f0d070", "flame", ("#ffb040", "#fff0c0")),
    ("mamos", "Los Mamos de la Sierra", ["del Poporo", "de la Línea Negra", "del Pensamiento Bueno"], "TUTUSOMA", "cotton", "#e0dcd0", "#6a5a3a", "spiral", ("#ffffff",)),
    ("cuchavira", "Cuchavira, el Arcoíris", ["del Arcoíris", "de la Fiebre Curada", "de las Siete Bandas"], "FLOWERS", "dancer", "#8a2ab0", "#f0c030", "flower", ("#ff7070", "#ffe060", "#70c0ff")),
    ("buziraco", "Buziraco, el del Cerro de la Popa", ["del Cerro de la Popa", "del Fuego Nocturno", "del Diablo Desterrado"], "HORNS", "leather", "#3a1a1a", "#e04a1a", "ember", ("#ff6a2a",)),
    ("dorjephagmo", "Dorje Phagmo, la Cerda de Diamante", ["de la Cerda de Diamante", "del Lago Yamdrok", "de la Danza Roja"], "DAKINI", "dancer", "#a01a4a", "#f0a0c0", "skull", ("#ff4a7a", "#ffd0e0")),
    ("kailash", "El Monte Kailash", ["del Monte de Cristal", "de la Vuelta al Monte", "de los Cuatro Ríos"], "STARS", "robe", "#e8f0ff", "#4a7ae0", "five", ("#ffffff", "#c0e0ff", "#ffe080")),
    ("marimonda", "La Marimonda de Barranquilla", ["del Carnaval", "de la Trompa Larga", "de las Orejas de Burla"], "MARIMONDA", "vest", "#2a4ab0", "#f0d030", "dot", ("#ffe060",)),
    ("tsongkhapa", "Tsongkhapa, el del Gorro Amarillo", ["del Gorro Amarillo", "del Gran Camino", "de la Lámpara de Mantequilla"], "LAMA", "monk", "#c8a020", "#8a2a2a", "dot", ("#fff0a0",)),
    ("chiva", "La Chiva de los Pueblos", ["de la Escalera del Techo", "de los Colores Vivos", "del Camino de Montaña"], "STRAW", "noble", "#c03a2a", "#f0d040", "coin", ("#ffe080",)),
    ("hayagriva", "Hayagriva, el Relincho", ["del Relincho", "de la Cabeza de Caballo", "del Fuego que Ahuyenta"], "HORSEHEAD", "plate", "#8a1a1a", "#3ad070", "flame", ("#ff6a2a", "#a0ff80")),
    ("purace", "El Volcán Puracé", ["del Azufre", "del Río Vinagre", "del Cóndor del Volcán"], "CREST", "leather", "#6a6a3a", "#e8e050", "ember", ("#f0f070",)),
    ("mandarava", "Mandarava, la Flor del Coral", ["de la Flor del Coral", "de la Cueva de Maratika", "del Agua de Vida Larga"], "LOTUS", "dress", "#c03a5a", "#f0e0e0", "flower", ("#ff8aa0", "#ffffff")),
    ("amazonas", "El Gran Río Amazonas", ["del Delfín Rosado", "de la Victoria Regia", "de la Canoa Larga"], "FEATHERS", "sea", "#2a5a3a", "#f08aa0", "wave", ("#ffa0c0",)),
    ("rechungpa", "Rechungpa, el del Algodón", ["del Algodón Blanco", "de la Oreja que Escucha", "del Viaje a la India"], "YOGI_KNOT", "cotton", "#d0d0c8", "#4a6a8a", "note", ("#ffffff", "#c0e0ff")),
    ("silleteros", "Los Silleteros de Santa Elena", ["de la Silleta", "de las Mil Flores", "del Camino de Santa Elena"], "FLOWERS", "weaver", "#3a6a2a", "#f04a8a", "flower", ("#ff80b0",)),
    ("tarumama", "La Tarumama", ["de la Vieja del Río", "de los Pies al Revés", "de la Orilla Lodosa"], "VEIL", "ghost", "#3a3a2a", "#8a9a5a", "eye", ("#a0c070",)),
    ("vairochana", "Vairochana, el Iluminador", ["del que Ilumina", "de la Rueda Blanca", "del Espacio sin Bordes"], "FIVE", "robe", "#f0f0f8", "#2a5ae0", "sun", ("#ffffff", "#a0c0ff", "#ffe080")),
    ("garabdorje", "Garab Dorje, el Gozo", ["del Gozo", "de los Tres Golpes", "del Lago Dhanakosha"], "YOGI_KNOT", "yogi", "#2a6ab0", "#f0f0f0", "dot", ("#a0e0ff", "#ffffff")),
    ("providencia", "La Isla de Providencia", ["del Arrecife", "del Cangrejo Negro", "del Cerro Alto"], "STRAW", "sea", "#1a8ab0", "#f0e070", "shell", ("#70f0ff",)),
    ("palden", "Palden Lhamo, la Protectora", ["de la Mula Roja", "del Lago de Sangre", "de la Protectora"], "WRATH", "dancer", "#3a1a4a", "#e03a3a", "skull", ("#ff3a3a", "#ffa0a0")),
    ("kaliawiri", "Kaliawirinae, el Árbol de la Vida", ["del Árbol de la Vida", "de los Frutos del Mundo", "de la Raíz Profunda"], "LEAVES", "vest", "#3a5a1a", "#e0a030", "leaf", ("#a0e060",)),
    ("vimalamitra", "Vimalamitra, el Amigo sin Mancha", ["del Amigo sin Mancha", "del Cuerpo de Arcoíris", "de los Cinco Picos"], "PANDITA", "monk", "#8a3a8a", "#f0d0f0", "five", ("#e0a0ff", "#ffffff")),
    ("boraro", "El Boraro", ["del Boraro", "de las Huellas Torcidas", "de la Selva Honda"], "HORNS", "leather", "#2a2a1a", "#c0402a", "bone", ("#e06040",)),
    ("virupa", "Virupa, el que Paró el Sol", ["del que Paró el Sol", "de la Taberna", "del Gran Mahasiddha"], "YOGI_KNOT", "yogi", "#b0601a", "#ffe070", "sun", ("#ffc040", "#fff8c0")),
    ("hojarasquin", "El Hojarasquín del Monte", ["de la Hojarasca", "del Monte Espeso", "del Guardián Verde"], "LEAVES", "ghost", "#3a4a1a", "#8ab040", "leaf", ("#a0d050",)),
    ("saraha", "Saraha, el Arquero", ["del Arquero", "de la Flecha que Apunta Dentro", "de las Canciones del Reino"], "BANDANA", "vest", "#5a3a1a", "#e0c060", "note", ("#ffe090",)),
    ("pollomaligno", "El Pollo Maligno", ["del Pollo Maligno", "de la Selva del Pacífico", "del Grito Nocturno"], "CREST", "ghost", "#1a1a1a", "#c03a1a", "feather", ("#e04a2a",)),
    ("kurukulla", "Kurukulla, la del Arco de Flores", ["del Arco de Flores", "del Poder Rojo", "de la Danza que Atrae"], "DAKINI", "dancer", "#c01a2a", "#f0a040", "flower", ("#ff3a3a", "#ffc0a0", "#ffffff"), "monarch"),
    ("ekajati", "Ekajati, la del Ojo Único", ["del Ojo Único", "del Diente Único", "de la Trenza Única"], "WRATH", "plate", "#1a2a5a", "#e0e8ff", "eye", ("#a0c0ff", "#ffffff")),
    ("poira", "El Poira", ["del Poira", "de la Cueva del Río", "del Cuarto de Luna"], "hood", "ghost", "#2a3a4a", "#a0b8c8", "moon", ("#c0d8e8",)),
    ("akshobhya", "Akshobhya, el Inamovible", ["del Inamovible", "del Gran Espejo", "de la Tierra Tocada"], "FIVE", "robe", "#1a3aa8", "#e0e8ff", "dot", ("#4a7aff", "#ffffff", "#c0d8ff")),
    ("patrul", "Patrul, el Vagabundo", ["del Vagabundo", "de la Montaña de Dzagyal", "de las Palabras del Maestro"], "WOOL_CAP", "trench", "#6a4a2a", "#e0c8a0", "note", ("#ffe0b0", "#ffffff")),
    ("jigme", "Jigme Lingpa, el León sin Miedo", ["del León sin Miedo", "de la Esencia del Corazón", "de la Visión del Cielo"], "PANDITA", "monk", "#2a2a8a", "#f0e070", "star", ("#fff070",)),
    ("ratnasambhava", "Ratnasambhava, la Joya", ["de la Joya que Nace", "del Gesto de Dar", "de la Igualdad"], "FIVE", "robe", "#e0a020", "#ffffff", "coin", ("#ffe060", "#ffffff", "#fff4c0")),
    ("amoghasiddhi", "Amoghasiddhi, el Logro sin Falla", ["del Logro sin Falla", "del Gesto sin Miedo", "del Viento Verde"], "FIVE", "robe", "#1a8a4a", "#f0e070", "five", ("#6af0a0", "#ffffff", "#fff48a")),
    ("dharmakaya", "El Cuerpo de la Verdad", ["de la Verdad", "del Cielo sin Nubes", "de la Luz sin Centro"], "STARS", "robe", "#1a1a40", "#ffffff", "star", ("#ffffff", "#c0d0ff", "#ffe080", "#a0ffe0")),
]
assert len(TABLE) == len(N4.SETS) == 59, len(TABLE)

HEAD_NOUN = {"SUN": "Corona", "FIVE": "Corona", "STARS": "Corona", "GOLD_BAND": "Corona", "LOTUS": "Corona", "DAKINI": "Corona", "WRATH": "Corona",
             "FEATHERS": "Corona", "FLOWERS": "Tocado", "LEAVES": "Tocado", "hood": "Capucha", "VEIL": "Velo", "STRAW": "Sombrero", "VUELTIAO": "Sombrero",
             "WOOL_CAP": "Gorro", "PANDITA": "Gorro", "LAMA": "Gorro", "YOGI_KNOT": "Moño", "MARIMONDA": "Máscara", "HORSEHEAD": "Yelmo", "HORNS": "Yelmo",
             "CREST": "Yelmo", "BANDANA": "Pañuelo", "TUTUSOMA": "Tutusoma", "WRAP": "Turbante"}
NOUN = {
    "A": dict(b="Vestidura", s="Escudo", g="Guantes", f="Zapatillas", t="Fajín"),
    "S": dict(b="Coraza", s="Escudo", g="Guantes", f="Pezuñas", t="Cinto"),
    "L": dict(b="Manto", s="Rodela", g="Brazales", f="Zapatos", t="Cordón"),
}
WEAPON_NOUN = {"espadaastral": "Espada", "lanzaastral": "Lanza", "arcoastral": "Arco", "mangualsombra": "Mangual", "mandoblesombra": "Mandoble",
               "varasombra": "Vara", "sableluna": "Sable", "tridenteluna": "Tridente", "arcoluna": "Arco"}
LPC_CLOTH = {"forest": "#3a6a3a", "orange": "#e07a3a", "tan": "#c8a878", "maroon": "#6a1a2a", "navy": "#2a3a6a", "yellow": "#e0c040",
             "white": "#e8e8e8", "teal": "#2a8a8a", "brown": "#6a4a2a", "red": "#b02a2a", "blue": "#2a5ab0", "purple": "#6a2a8a"}


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _mix(a, b, t):
    a, b = _rgb(a), _rgb(b)
    return "#%02x%02x%02x" % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _nearest(h, table):
    c = _rgb(h)
    return min(table, key=lambda k: sum((x - y) ** 2 for x, y in zip(c, _rgb(table[k]))))


SETS, LOOK = [], {}
for i, row in enumerate(TABLE):
    sid, name, phrases, hat, body, main_c, acc_c, motif, fx = row[:9]
    wings_over = row[9] if len(row) > 9 else False
    t_sid, _, tier, elem, listen, kit, weapon, slots, *_ = N4.SETS[i]
    names = []
    for k, code in enumerate("hbw" + slots):
        noun = HEAD_NOUN[hat] if code == "h" else WEAPON_NOUN[weapon] if code == "w" else "Amuleto" if code == "a" else "Anillo" if code == "r" else NOUN[kit][code]
        names.append(f"{noun} {phrases[k % 3]}")
    neck = (_mix(main_c, "#000000", 0.35), acc_c, _mix(acc_c, "#ffffff", 0.6))
    metal = "gold" if tier in ("legendario", "mitico") else "silver" if sum(_rgb(main_c)) > 480 else "bronze" if tier else "iron"
    lpc = (metal, _nearest(main_c, LPC_CLOTH), "gold" if tier == "mitico" else "dark" if sum(_rgb(main_c)) < 300 else "medium")
    SETS.append((sid, name, tier, elem, listen, kit, weapon, slots, names, neck, lpc))
    LOOK[sid] = dict(template=t_sid, hat=hat, body=body, main=main_c, acc=acc_c, motif=motif, fx=fx, wings=wings_over)

# hats drawn for these sets (letters as in new_sets_400_art.HATS; G a light leaf green)
HATS = {
    "PANDITA": """
........Y........
.......MMM.......
......MmmmM......
.....MmmmmmM.....
....MmmmmmmmM....
...MmmmYmmmmmM...
..MMMMMMMMMMMMM..
.MAAAAAAAAAAAAAM.
.MM...........MM.
.MM...........MM.
.MM...........MM.
..M...........M..
""",
    "LOTUS": """
.......B.......
......BaB......
...B..BaB..B...
..BaB.BaB.BaB..
..BaaBaaaBaaB..
.BaaaaaaaaaaaB.
YYYYYYYYYYYYYYY
YyyAyyyyyyyAyyY
""",
    "WRATH": """
.r..y..r..y..r..y.
ryr.yry.ryr.yry.ry
.r.r.r.r.r.r.r.r.r
.WWW.WWW.WWW.WWW..
.WkW.WkW.WkW.WkW..
.WWW.WWW.WWW.WWW..
YYYYYYYYYYYYYYYYYY
YyyyyyyyyyyyyyyyyY
""",
    "FLOWERS": """
.r.Y.b.W.r.Y.b.W.r.
rYrYbYbWbrYrYbYbWbr
.r.Y.b.W.r.Y.b.W.r.
ggggggggggggggggggg
.g.g.g.g.g.g.g.g.g.
""",
    "MARIMONDA": """
.MMM...........MMM.
MmmmM.MMMMMMM.MmmmM
MmmmMMmmmmmmmMMmmmM
.MMMMmmmmmmmmmMMMM.
....MmWWmmmWWmM....
....MmWkmmmWkmM....
....MmmmmmmmmmM....
.....MmmAAAmmM.....
.......MaaM........
.......MaaM........
.......MaaM........
........MM.........
""",
    "LEAVES": """
..g...g...g...g...g..
.gGg.gGg.gGg.gGg.gGg.
.gGg.gGg.gGg.gGg.gGg.
..g...g...g...g...g..
MMMMMMMMMMMMMMMMMMMMM
MmmAmmmmAmmmmAmmmmAmM
""",
    "HORSEHEAD": """
.......gggg.......
......gGGGGg......
.....gGGkGGGg.....
....gGGGGGGGGg....
....gGGGg.gGGg....
......gGg.........
.Y..r..Y..r..Y..r.
YYYYYYYYYYYYYYYYYY
YyWyyyWyyyWyyyWyyY
""",
}
LIFT = {"PANDITA": 7, "LOTUS": 3, "WRATH": 3, "FLOWERS": 3, "MARIMONDA": 10, "LEAVES": 3, "HORSEHEAD": 3}


if __name__ == "__main__":
    N4.write(SETS, LO, HI, "  // levels 404-600 (2026-11-27, scripts/new_sets_600.py): more Colombian places and legends, and more of the lineages",
             {t: [s[0] for s in N4.SETS if s[2] == t][-1] for t in N4.TIER})
