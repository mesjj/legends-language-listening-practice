"""The 24 zones added on 2026-11-27: four more for each of the five zones of the road, and four Abismos
from the Tibetan hells. Each episode draws one zone per slot (main.js zonePick); the old zones stay in
the draw. This table is the source: scripts/new_zones.py writes the game's data from it,
build_monsters_kit.py draws the monsters, build_bosses_kit.py the bosses, scenes_more.py the backdrops.

A monster: (id, name, icon, colour, hp, dmg, tag, art). tag gives its element and what it resists:
  F fire, C cold, P poison, L lightning (elemental: deals half its hit as that element),
  U undead (cold and poison immune, weak to lightning), S stone, V plant (burns), W water animal, B beast,
  lower case: resistances only, no element. art: (kind, colours "main,second,accent,eye", options).
"""

# slot -> [zone, ...]
ZONES = {}


def Z(slot, id, name, blurb, scene, fx, music, easy, monsters, descents=None):
    ZONES.setdefault(slot, []).append(dict(id=id, slot=slot, name=name, blurb=blurb, scene=scene, fx=fx, music=music,
                                           easy=easy, monsters=monsters, descents=descents))


def M(id, name, icon, color, hp, dmg, tag, kind, cols, **opt):
    return dict(id=id, name=name, icon=icon, color=color, hp=hp, dmg=dmg, tag=tag, art=(kind, cols, opt))


# ======================================================================== páramo
Z("paramo", "guatavita", "Laguna de Guatavita",
  "Una laguna redonda en lo alto, donde el cacique se cubría de oro. Algo brilla en el fondo.",
  dict(sky=("#5a6a7a", "#e8d8b0"), far=("mountains", "#56646a", "#e8ecec"), mid=("hills", "#4a5a40"), water=("#3a5a5a", "#6a8a80", 94),
       ground=("grass", "#3e4a28", "#a8a868"), props=["reeds", "frailejon", "gold"], haze=(220, 214, 190)),
  [["fog", 5], ["mote", 10]], dict(base="paramo", seed=101, root=52, scale="DOR"), ["pajarito", "mariquita", "polilla", "caracol"], [
    M("garzaoro", "Garza de oro", "vulture", "#e8c040", 0.8, 1.1, "L", "bird", "#e8c040,#f8e8a0,#b08020,#3a1a0a", style="wader"),
    M("culebralaguna", "Culebra de la laguna", "snake", "#3a6a5a", 1.1, 1.1, "C", "serpent", "#3a6a5a,#24443a,#e8c040,#f0e060", style="rise"),
    M("sombracacique", "Sombra del cacique", "ghost", "#a89a60", 1.0, 1.2, "U", "spirit", "#3a3428,#a89a60,#e8c040,#ffe060", style="ghost", gold=True),
    M("juncoandante", "Junco andante", "evil-tree", "#8a9a4a", 1.4, 0.9, "V", "plant", "#6a8a3a,#4a6a2a,#c8b860,#f0e040", style="reeds"),
    M("patoniebla", "Pato de niebla", "raven", "#8a9aa0", 0.6, 0.9, "c", "bird", "#7a8a90,#d8e0e0,#3a5a4a,#201010", style="duck"),
    M("ofrendero", "Ofrendero dorado", "hooded-figure", "#d8a830", 1.1, 1.1, "L", "biped", "#c89030,#5a3a2a,#f0d060,#fff080", head="human", hat="crown", body="bare", held="staff", fx="gold"),
    M("ranaoro", "Rana de oro", "frog", "#e0b030", 0.7, 1.0, "L", "frog", "#e0b030,#8a6010,#fff0a0,#201010"),
    M("piedraofrenda", "Piedra de las ofrendas", "rock-golem", "#8a8478", 1.9, 0.9, "S", "golem", "#8a8478,#5a564e,#e8c040,#ffb040", style="stone", gold=True),
    M("chamanlaguna", "Chamán de la laguna", "hooded-figure", "#5a7a6a", 1.1, 1.2, "C", "biped", "#8a6048,#3a5a4a,#e8c040,#80e0ff", head="human", hat="feathers", body="robe", held="staff"),
    M("animacacica", "Ánima de la cacica", "floating-ghost", "#a0d8d0", 1.0, 1.2, "U", "spirit", "#a0d8d0,#e8f8f4,#e8c040,#40a0a0", style="woman"),
  ])
Z("paramo", "cocuy", "Glaciares del Cocuy",
  "Hielo azul y un viento que corta. Allá arriba no vive nadie, y sin embargo algo camina.",
  dict(sky=("#3a6aa8", "#c8e0f0"), far=("peaks", "#8aa8c8", "#ffffff"), mid=("ice", "#a8c8e0"), ground=("snow", "#8aa0b8", "#f4f8ff"),
       props=["icerock", "icicle"], haze=(230, 240, 250)),
  [["snow", 40], ["fog", 3]], dict(base="paramo", seed=103, root=55, scale="LOC"), ["pajarito", "polilla", "ratoncito"], [
    M("osoglaciar", "Oso del glaciar", "bear-head", "#e8f0f8", 1.8, 1.1, "C", "quad", "#e0e8f0,#a8b8c8,#ffffff,#202a40", head="bear", big=True),
    M("grietaviva", "Grieta viva", "ghost", "#60a8e0", 0.9, 1.2, "C", "spirit", "#3a7ab8,#a0d8ff,#ffffff,#e0f8ff", style="crystal"),
    M("caminantenieve", "Caminante de nieve", "ogre", "#d8e0e8", 1.5, 1.1, "C", "biped", "#c8d0d8,#e8f0f8,#8aa0b8,#3a8ae0", head="fur", body="fur", held="club", big=True),
    M("cuervoescarcha", "Cuervo de escarcha", "raven", "#4a5a7a", 0.6, 1.1, "C", "bird", "#3a4a6a,#8aa0c0,#c8e8ff,#80e0ff", style="perch"),
    M("cabrahielo", "Cabra de hielo", "charging-bull", "#c8d8e8", 1.1, 1.2, "C", "quad", "#c8d8e8,#8aa0b8,#a0e0ff,#202a40", head="goat", horns=True),
    M("loboblanco", "Lobo blanco", "wolf-head", "#e8ecf0", 1.0, 1.3, "c", "quad", "#e0e4e8,#a8b0b8,#f8fcff,#40a0e0", head="dog"),
    M("golemhielo", "Golem de hielo", "rock-golem", "#a0d0f0", 2.0, 1.0, "C", "golem", "#a0d0f0,#6098c8,#ffffff,#2a60c0", style="ice", big=True),
    M("halconviento", "Halcón del viento", "vulture", "#8a9aaa", 0.7, 1.3, "c", "bird", "#6a7a8a,#e8ecf0,#3a4a5a,#f0c030", style="flying"),
    M("caramabano", "Carámbano", "ghost", "#c8f0ff", 0.8, 1.2, "C", "golem", "#c8f0ff,#80c0e8,#ffffff,#2a70c0", style="icicle"),
    M("escaladorhelado", "Escalador helado", "shambling-zombie", "#8ab0c8", 1.3, 1.1, "U", "biped", "#a8c0d0,#c84a2a,#e8f0f8,#80e0ff", head="hood", body="coat", held="pick", fx="ice"),
  ])
Z("paramo", "niebla", "Bosque de Niebla",
  "Árboles cubiertos de musgo que gotean todo el día. Nadie ve más allá de diez pasos.",
  dict(sky=("#6a7a70", "#c0ccc0"), far=("trees", "#4a5a4a"), mid=("palms", "#3a4a3a"), ground=("grass", "#2a3a22", "#6a8a4a"),
       props=["mossytree", "fern", "palm"], haze=(214, 224, 216)),
  [["fog", 7], ["drip", 8], ["drizzle", 14]], dict(base="paramo", seed=107, root=50, scale="MIN"), ["gusanito", "caracol", "hongo"], [
    M("osoanteojos", "Oso de anteojos furioso", "bear-head", "#2a2220", 1.7, 1.2, "b", "quad", "#2a2220,#1a1410,#e8d0a0,#ff4020", head="bear", spectacles=True, big=True),
    M("musgoso", "Musgoso", "slime", "#5a8a3a", 1.3, 0.9, "V", "blob", "#5a8a3a,#3a6a2a,#a0c870,#f0e040", style="moss"),
    M("helechogigante", "Helecho gigante", "evil-tree", "#4a7a3a", 1.4, 1.0, "V", "plant", "#4a7a3a,#2e5a24,#8ab860,#f0e040", style="fern"),
    M("tucanmontana", "Tucán de montaña", "raven", "#3a4a6a", 0.6, 1.1, "b", "bird", "#3a4a6a,#e8d8a0,#e8803a,#201010", style="perch", beak="toucan"),
    M("dantasombria", "Danta sombría", "boar", "#3a3438", 1.6, 1.0, "b", "quad", "#3a3438,#24201f,#d8d0c8,#e8c040", head="tapir", big=True),
    M("orquidea", "Orquídea que muerde", "evil-tree", "#d06ab0", 0.9, 1.2, "P", "plant", "#d06ab0,#4a8a3a,#fff0a0,#201010", style="flytrap"),
    M("sombrarboles", "Sombra entre los árboles", "ghost", "#3a4a3a", 1.0, 1.2, "U", "spirit", "#2a342a,#4a5a4a,#a0c080,#c8ff60", style="ghost"),
    M("ranacristal", "Rana de cristal", "frog", "#a0e0b0", 0.6, 1.0, "W", "frog", "#a0e0b0,#60a070,#e8fff0,#201010", glass=True),
    M("lenador", "Leñador perdido", "shambling-zombie", "#6a7a6a", 1.3, 1.2, "U", "biped", "#8a9a8a,#5a3a2a,#c84a2a,#c8ff60", head="human", hat="wide", body="tunic", held="axe", fx="ghost"),
    M("buhoniebla", "Búho de niebla", "raven", "#8a8478", 0.7, 1.1, "c", "bird", "#8a8070,#c8c0b0,#5a5040,#f0c030", style="owl"),
  ])
Z("paramo", "azufre", "Volcán de Azufre",
  "Fumarolas amarillas y un olor que quema la garganta. El suelo está caliente bajo la nieve.",
  dict(sky=("#8a8a5a", "#e8e0a0"), far=("volcano", "#5a5448", "#f0f0e8"), mid=("hills", "#6a6448"), ground=("dirt", "#5a5030", "#d8c860"),
       props=["fumarole", "sulfur", "rock"], haze=(232, 226, 150)),
  [["smoke", 5], ["ash", 14], ["heat", 1]], dict(base="paramo", seed=109, root=49, scale="PHR"), ["hormiguita", "grillo", "lagartijita"], [
    M("fumarolaviva", "Fumarola viva", "ghost", "#e8e060", 0.9, 1.1, "P", "spirit", "#d8d060,#f8f4c0,#8a8030,#ff8020", style="cloud"),
    M("lagartoazufre", "Lagarto de azufre", "snake", "#d8c030", 1.1, 1.2, "P", "lizard", "#d8c030,#8a7a18,#fff080,#201010", style="frill"),
    M("mineroahumado", "Minero ahumado", "shambling-zombie", "#5a5448", 1.2, 1.1, "p", "biped", "#6a5a48,#4a4a40,#e8d040,#ff8020", head="human", hat="helm", body="tunic", held="pick"),
    M("condortiznado", "Cóndor tiznado", "vulture", "#3a3430", 0.9, 1.2, "b", "bird", "#2a2420,#d8d0c0,#8a8070,#ff6020", style="flying"),
    M("piedrahirviente", "Piedra hirviente", "rock-golem", "#8a5030", 1.9, 1.0, "F", "golem", "#6a4a3a,#3a2a24,#ff7020,#ffd040", style="lava"),
    M("gusanoceniza", "Gusano de ceniza", "leeching-worm", "#8a8070", 0.9, 1.0, "p", "worm", "#8a8070,#5a5048,#e8d040,#ff4020"),
    M("escarabajoamarillo", "Escarabajo amarillo", "wasp-sting", "#e0c020", 0.7, 1.1, "P", "bug", "#e0c020,#5a4a10,#2a2410,#ff2020", style="beetle"),
    M("espiritucrater", "Espíritu del cráter", "burning-skull", "#ff8030", 1.0, 1.3, "F", "spirit", "#ff8030,#ffd060,#8a2a10,#ffffff", style="flame"),
    M("venadoceniza", "Venado de ceniza", "charging-bull", "#7a746a", 1.1, 1.1, "b", "quad", "#7a746a,#4a4640,#c8c0b0,#ff6020", head="deer", horns=True, big=True),
    M("bocavolcan", "Boca del volcán", "slime", "#c84a1a", 1.4, 1.2, "F", "blob", "#c84a1a,#6a2010,#ffb030,#fff0a0", style="lava"),
  ])

# ======================================================================== ciénaga
Z("cienaga", "manglar", "Manglares del Pacífico",
  "Raíces que salen del agua como dedos. Con la marea alta, el bosque entero se hunde.",
  dict(sky=("#3a3a5a", "#d8906a"), far=("trees", "#2a3430"), mid=("mangrove", "#24302a"), water=("#2a3a3a", "#4a6a60", 98),
       ground=("dirt", "#2a241a", "#6a5a40"), props=["mangrove", "roots", "crab"], haze=(200, 170, 150)),
  [["mist", 5], ["firefly", 12]], dict(base="cienaga", seed=201, root=46, scale="DOR"), ["cangrejito", "caracol", "pececito"], [
    M("cangrejoazul", "Cangrejo azul gigante", "croc-jaws", "#3a6ac8", 1.3, 1.2, "W", "crab", "#3a6ac8,#24408a,#e8e0c8,#ff3020", big=True),
    M("pianguero", "Piangüero ahogado", "shambling-zombie", "#5a7a7a", 1.2, 1.1, "U", "biped", "#5a6a6a,#8a7a5a,#3a5a5a,#a0ffe0", head="human", hat="wide", body="rags", held="basket", fx="ghost"),
    M("pelicanonegro", "Pelícano negro", "vulture", "#3a3a40", 0.9, 1.1, "b", "bird", "#3a3a40,#8a8a90,#e8b040,#ff3020", style="perch", beak="pouch"),
    M("raizagarra", "Raíz que agarra", "evil-tree", "#5a4a30", 1.5, 1.0, "V", "plant", "#5a4a30,#3a2e1e,#6a8a3a,#f0e040", style="root"),
    M("tiburonestero", "Tiburón de estero", "croc-jaws", "#6a7a8a", 1.3, 1.3, "W", "fish", "#6a7a8a,#d8e0e8,#3a4a5a,#201010", style="shark"),
    M("mapana", "Mapaná", "cobra", "#7a6a4a", 0.9, 1.4, "P", "serpent", "#7a6a4a,#4a3a24,#c8b080,#f0c030", style="coil", pattern="x"),
    M("barracuda", "Barracuda", "croc-jaws", "#a0b0b8", 0.8, 1.3, "W", "fish", "#a0b0b8,#e8f0f0,#5a6a70,#201010", style="barracuda"),
    M("pulpomanglar", "Pulpo del manglar", "slime", "#a04a5a", 1.3, 1.0, "W", "blob", "#a04a5a,#6a2a3a,#e8a0a8,#f0e040", style="octopus"),
    M("garzaazul", "Garza azul", "vulture", "#5a6a9a", 0.7, 1.1, "b", "bird", "#5a6a9a,#8a9ac0,#3a4a6a,#f0c030", style="wader"),
    M("mareaviva", "Marea viva", "ghost", "#4a8a9a", 1.1, 1.1, "C", "spirit", "#3a7a8a,#a0e0e8,#ffffff,#e0ffff", style="water"),
  ])
Z("cienaga", "magdalena", "Río Grande de la Magdalena",
  "El río más ancho que has visto. De noche pasan champanes sin nadie que los reme.",
  dict(sky=("#141a2e", "#3a4a6a"), far=("trees", "#141a1a"), mid=("palms", "#101616"), water=("#1a2a3a", "#3a5a7a", 96),
       ground=("dirt", "#2a2418", "#7a6a48"), props=["champan", "palm", "reeds"], haze=(150, 170, 200), moon=True),
  [["firefly", 18], ["mist", 4]], dict(base="cienaga", seed=203, root=43, scale="MIN"), ["sapito", "pececito", "caracol"], [
    M("bagregigante", "Bagre gigante", "croc-jaws", "#6a6a5a", 1.6, 1.1, "W", "fish", "#6a6a5a,#a8a890,#3a3a30,#e8c040", style="catfish", big=True),
    M("caimanaguja", "Caimán aguja", "croc-jaws", "#5a6a3a", 1.5, 1.3, "W", "lizard", "#5a6a3a,#3a4a24,#d8d098,#f0c030", style="croc", big=True),
    M("bogafantasma", "Boga fantasma", "shambling-zombie", "#8aa0b0", 1.2, 1.2, "U", "biped", "#7a8a98,#c8d0d8,#5a4a3a,#a0e8ff", head="human", body="bare", held="oar", fx="ghost"),
    M("manatitriste", "Manatí triste", "slime", "#8a8a90", 1.8, 0.8, "W", "fish", "#8a8a90,#a8a8b0,#5a5a60,#201010", style="manatee", big=True),
    M("pescadorsombras", "Pescador de sombras", "hooded-figure", "#3a3a4a", 1.1, 1.2, "C", "biped", "#6a5040,#2a2a3a,#c8c8d8,#80a0ff", head="human", hat="wide", body="ruana", held="net"),
    M("chiguirorio", "Chigüiro de río", "boar", "#8a6440", 1.3, 1.0, "b", "quad", "#8a6440,#5a4028,#b08860,#201010", head="capybara"),
    M("patoaguja", "Pato aguja", "raven", "#2a2a30", 0.6, 1.2, "b", "bird", "#2a2a30,#c8c0b0,#5a5a60,#ff3020", style="wader"),
    M("tortugario", "Tortuga de río", "frog", "#5a6a3a", 1.7, 0.9, "W", "turtle", "#5a6a3a,#3a4a24,#a8b870,#201010"),
    M("sapochampan", "Sapo del champán", "frog", "#7a6a3a", 0.9, 1.0, "P", "frog", "#7a6a3a,#4a3a20,#d8c890,#e8c030", warts=True),
    M("remolinorio", "Remolino del río", "ghost", "#3a5a7a", 1.1, 1.1, "C", "spirit", "#3a5a7a,#8ab0d0,#d8f0ff,#ffffff", style="water"),
  ])
Z("cienaga", "atrato", "Delta del Atrato",
  "El Atrato se abre en cien brazos antes de llegar al mar. Llueve, y el agua sube.",
  dict(sky=("#4a5450", "#8a9890"), far=("trees", "#2a3a2e"), mid=("stilts", "#3a3028"), water=("#2a3a30", "#4a6a58", 100),
       ground=("grass", "#24341e", "#5a7a3a"), props=["reeds", "stilthouse", "palm"], haze=(190, 200, 196)),
  [["rain", 50], ["mist", 4]], dict(base="cienaga", seed=207, root=45, scale="DOR"), ["sapito", "culebrita", "pececito"], [
    M("anacondadelta", "Anaconda del delta", "cobra", "#4a6a2a", 1.8, 1.1, "W", "serpent", "#4a6a2a,#2a3a18,#1a2010,#f0c030", style="coil", pattern="spots", big=True),
    M("pirana", "Piraña", "croc-jaws", "#8a8a9a", 0.6, 1.4, "W", "fish", "#8a8a9a,#e0503a,#4a4a5a,#ff3020", style="piranha"),
    M("ranaarlequin", "Rana arlequín", "frog", "#e0602a", 0.6, 1.2, "P", "frog", "#e0602a,#1a1a1a,#f0e040,#201010", stripes=True),
    M("basilisco", "Lagarto basilisco", "snake", "#5a9a3a", 0.9, 1.1, "b", "lizard", "#5a9a3a,#3a6a24,#c8e070,#f0c030", style="crest"),
    M("garzamorena", "Garza morena", "vulture", "#6a5040", 0.7, 1.1, "b", "bird", "#6a5040,#c8b090,#3a2a20,#f0c030", style="wader"),
    M("pescadordelta", "Pescador del delta", "hooded-figure", "#5a4a3a", 1.1, 1.2, "c", "biped", "#6a4a34,#c8c0a0,#2a6a8a,#ffe060", head="human", hat="wide", body="tunic", held="spear"),
    M("nutriasalvaje", "Nutria salvaje", "rat", "#6a4a30", 0.9, 1.2, "W", "quad", "#6a4a30,#3a2a1a,#c8a880,#201010", head="otter"),
    M("babilla", "Babilla", "croc-jaws", "#6a7a4a", 1.4, 1.2, "W", "lizard", "#6a7a4a,#4a5a30,#d8d0a0,#f0c030", style="croc"),
    M("nubelluvia", "Nube de lluvia", "ghost", "#7a8a90", 1.0, 1.1, "L", "spirit", "#6a7a80,#c8d0d4,#ffffff,#f0f080", style="cloud", rain=True),
    M("hormigaagua", "Hormiga de agua", "wasp-sting", "#3a2a2a", 0.6, 1.1, "P", "bug", "#3a2a2a,#5a3a30,#a0d0e0,#ff3020", style="ant"),
  ])
Z("cienaga", "canocristales", "Caño Cristales",
  "El río de los cinco colores: rojo, amarillo, verde, azul y negro. Brilla como si estuviera vivo.",
  dict(sky=("#4a8ad0", "#e8f4f8"), far=("mesa", "#6a7a5a"), mid=("hills", "#5a7a3a"), water=("#c8304a", "#f0c040", 100),
       ground=("rock", "#4a4440", "#c8b8a0"), props=["redweed", "rock", "pool"], haze=(240, 240, 230)),
  [["mote", 16], ["mist", 2]], dict(base="cienaga", seed=211, root=50, scale="MAJ"), ["pececito", "abejita", "lagartijita"], [
    M("algaroja", "Alga roja viva", "evil-tree", "#d0304a", 1.2, 1.0, "V", "plant", "#d0304a,#8a1a2a,#f08aa0,#f0e040", style="algae"),
    M("piedrapulida", "Piedra pulida", "rock-golem", "#8a7a6a", 1.9, 0.9, "S", "golem", "#8a7a6a,#5a4e44,#c8b8a0,#40e0ff", style="stone"),
    M("pezcolores", "Pez de colores", "frog", "#f08a30", 0.6, 1.1, "W", "fish", "#f08a30,#3a8ae0,#f0e040,#201010", style="fish", rainbow=True),
    M("libelula", "Libélula de cristal", "wasp-sting", "#40c0e0", 0.5, 1.2, "L", "bug", "#40c0e0,#2a6a8a,#e0f8ff,#ff3020", style="dragonfly"),
    M("martinpescador", "Martín pescador", "raven", "#2a8ac0", 0.6, 1.2, "b", "bird", "#2a8ac0,#e88a40,#ffffff,#201010", style="perch", beak="long"),
    M("caracolrio", "Caracol de río", "slime", "#c8a060", 1.3, 0.8, "W", "snail", "#c8a060,#f0e0b0,#8a5a30,#201010"),
    M("garzablanca", "Garza blanca", "vulture", "#f0f0f0", 0.7, 1.1, "b", "bird", "#f0f0f0,#d8d8d8,#e8c040,#201010", style="wader"),
    M("espiritucano", "Espíritu del caño", "ghost", "#f0c040", 1.0, 1.2, "L", "spirit", "#d0304a,#f0c040,#40a060,#ffffff", style="rainbow"),
    M("lagartijacolores", "Lagartija de colores", "snake", "#40a0e0", 0.8, 1.1, "b", "lizard", "#40a0e0,#e0503a,#f0e040,#201010", style="low"),
    M("sapopintado", "Sapo pintado", "frog", "#40a060", 0.8, 1.1, "P", "frog", "#40a060,#d0304a,#f0e040,#201010", warts=True),
  ])

# ======================================================================== selva
Z("selva", "amazonas", "El Amazonas",
  "Árboles tan altos que no se ve el cielo, y un río que no termina nunca.",
  dict(sky=("#1a3a24", "#5a8a4a"), far=("trees", "#14301c"), mid=("bigtrees", "#0e2414"), water=("#3a3020", "#6a5a3a", 102),
       ground=("grass", "#14240e", "#3a6a24"), props=["bigtree", "liana", "heliconia"], haze=(160, 200, 150)),
  [["rain", 30], ["mote", 12], ["drip", 6]], dict(base="selva", seed=301, root=50, scale="DOR"), ["abejita", "gusanito", "hongo", "lagartijita"], [
    M("jaguarnegro", "Jaguar negro", "wolf-head", "#1e1a20", 1.4, 1.4, "b", "quad", "#1e1a20,#121014,#2e2830,#e8e040", head="cat", spots="#0e0c10", big=True),
    M("anacondaverde", "Anaconda verde", "cobra", "#4a7a2a", 1.8, 1.1, "W", "serpent", "#4a7a2a,#2a4a18,#1a2a10,#f0c030", style="coil", pattern="spots", big=True),
    M("pirarucu", "Pirarucú", "croc-jaws", "#6a5a4a", 1.6, 1.1, "W", "fish", "#6a5a4a,#c84a2a,#3a2a20,#e8c040", style="big", big=True),
    M("monoarana", "Mono araña", "monkey", "#3a2a24", 0.8, 1.2, "b", "monkey", "#3a2a24,#24180e,#c8a080,#201010", long=True),
    M("arpia", "Arpía", "vulture", "#5a5a5a", 1.1, 1.4, "b", "bird", "#5a5a5a,#e8e8e8,#2a2a2a,#f0c030", style="flying", crest=True),
    M("hormigabala", "Hormiga bala", "wasp-sting", "#4a1a10", 0.6, 1.5, "P", "bug", "#4a1a10,#2a0e08,#c84a2a,#ff3020", style="ant", big_jaw=True),
    M("ranadardo", "Rana dardo azul", "frog", "#2a6ae0", 0.5, 1.3, "P", "frog", "#2a6ae0,#1a1a2a,#80c0ff,#201010", spots=True),
    M("caimannegro", "Caimán negro", "croc-jaws", "#2a2a24", 1.7, 1.3, "W", "lizard", "#2a2a24,#1a1a14,#a8a880,#f0c030", style="croc", big=True),
    M("yacuruna", "Yacuruna", "hooded-figure", "#3a7a7a", 1.2, 1.2, "C", "biped", "#4a8a8a,#2a5a5a,#a0e0e0,#80ffff", head="fish", body="bare", held="trident"),
    M("hongoluz", "Hongo luminoso", "slime", "#60e0c0", 1.1, 1.0, "V", "plant", "#60e0c0,#2a8a7a,#e0fff8,#201010", style="mushroom", glow=True),
  ])
Z("selva", "chiribiquete", "Serranía de Chiribiquete",
  "Mesetas de piedra que salen de la selva, pintadas con jaguares hace miles de años.",
  dict(sky=("#4a7ab0", "#e0e8d0"), far=("tepui", "#6a4a3a", "#a83a2a"), mid=("trees", "#1e3a20"), ground=("grass", "#1a2a14", "#4a7a2a"),
       props=["painting", "waterfall", "bigtree"], haze=(220, 230, 210)),
  [["mist", 5], ["mote", 10]], dict(base="selva", seed=303, root=48, scale="MIN"), ["abejita", "gusanito", "pollito"], [
    M("jaguarpintado", "Jaguar pintado", "wolf-head", "#c87a30", 1.4, 1.3, "b", "quad", "#c87a30,#8a4a1a,#a8301a,#f0e040", head="cat", spots="#a8301a", big=True),
    M("hombrepintado", "Hombre pintado", "hooded-figure", "#a8401a", 1.1, 1.2, "L", "biped", "#a8401a,#6a2a10,#f0e0c0,#ffe060", head="human", body="bare", held="spear", paint=True),
    M("gallitorocas", "Gallito de las rocas", "raven", "#f05a1a", 0.6, 1.1, "b", "bird", "#f05a1a,#2a2a2a,#c03a10,#201010", style="perch", crest=True),
    M("murcielagocueva", "Murciélago de cueva", "evil-bat", "#4a3a3a", 0.6, 1.2, "b", "bat", "#4a3a3a,#2a2020,#c8a0a0,#ff3020"),
    M("dantameseta", "Danta de la meseta", "boar", "#4a4038", 1.6, 1.0, "b", "quad", "#4a4038,#2e2824,#8a8078,#201010", head="tapir", big=True),
    M("serpienteroca", "Serpiente de piedra roja", "cobra", "#a8401a", 1.3, 1.2, "S", "serpent", "#a8401a,#6a2a10,#f0c080,#ffe060", style="rise", pattern="bands"),
    M("guacamayaroja", "Guacamaya roja", "raven", "#e0302a", 0.7, 1.1, "b", "bird", "#e0302a,#f0c030,#2a6ae0,#201010", style="perch", beak="hook"),
    M("lianacascada", "Liana de la cascada", "evil-tree", "#3a7a4a", 1.4, 1.0, "V", "plant", "#3a7a4a,#24502e,#a0e0f0,#f0e040", style="vine"),
    M("monoaullador", "Mono aullador", "monkey", "#8a3a1a", 0.9, 1.1, "b", "monkey", "#8a3a1a,#5a2410,#3a1a0a,#201010", howl=True),
    M("espiritupintura", "Espíritu de la pintura", "ghost", "#c84a2a", 1.0, 1.3, "L", "spirit", "#c84a2a,#f0c080,#6a2a10,#ffffff", style="painting"),
  ])
Z("selva", "guacharos", "Cueva de los Guácharos",
  "Una cueva honda donde miles de pájaros gritan en la oscuridad. Un río corre por dentro.",
  dict(sky=("#1a2224", "#3a4644"), far=("cave", "#2e3836", "#5a6a66"), mid=("stalag", "#3a4442"), water=("#2a4444", "#4a7070", 104),
       ground=("rock", "#2a2e2c", "#7a7a70"), props=["stalagmite", "guacharo", "fern"], haze=(150, 170, 170)),
  [["drip", 10], ["mote", 8]], dict(base="ruinas", seed=307, root=46, scale="PHR"), ["ratoncito", "hormiguita", "hongo"], [
    M("guacharo", "Guácharo", "evil-bat", "#8a5a3a", 0.7, 1.2, "b", "bird", "#8a5a3a,#c8a070,#ffffff,#ff6020", style="flying", spots=True),
    M("vampiro2", "Murciélago vampiro", "evil-bat", "#3a2a2a", 0.6, 1.2, "b", "bat", "#3a2a2a,#1e1414,#c06060,#ff2020", vamp=True),
    M("cangrejocueva", "Cangrejo de cueva", "croc-jaws", "#d8c8c0", 1.0, 1.1, "W", "crab", "#d8c8c0,#a89890,#f0e8e0,#201010"),
    M("grillociego", "Grillo ciego", "centipede", "#a8a090", 0.6, 1.1, "b", "bug", "#a8a090,#6a6458,#e0d8c8,#a8a090", style="cricket"),
    M("pezciego", "Pez ciego", "frog", "#f0d8d0", 0.6, 1.0, "W", "fish", "#f0d8d0,#d8b8b0,#c08080,#f0d8d0", style="fish"),
    M("estalagmita", "Estalagmita viva", "rock-golem", "#7a7468", 2.0, 0.9, "S", "golem", "#7a7468,#4a4640,#a8a090,#40e0c0", style="stalagmite"),
    M("aranacueva", "Araña de cueva", "hanging-spider", "#6a6058", 0.9, 1.2, "P", "bug", "#6a6058,#4a4038,#c8c0b0,#ff3020", style="spider", long=True),
    M("sapocueva", "Sapo de la cueva", "frog", "#8a8a7a", 0.9, 1.0, "P", "frog", "#8a8a7a,#5a5a4e,#c8c8b0,#ff8020", warts=True),
    M("ermitano", "Ermitaño perdido", "shambling-zombie", "#6a6458", 1.2, 1.1, "U", "biped", "#8a8478,#5a4a3a,#e8d060,#a0ffa0", head="human", body="robe", held="lantern", beard=True),
    M("ecocueva", "Eco de la cueva", "floating-ghost", "#a0a8b0", 0.9, 1.2, "U", "spirit", "#5a6068,#a0a8b0,#e0e8f0,#ffffff", style="rings"),
  ])
Z("selva", "darien", "El Tapón del Darién",
  "Una selva sin caminos entre dos mares. Los que entran no siempre salen.",
  dict(sky=("#0e1a10", "#2a4a2a"), far=("trees", "#0a1a0e"), mid=("bigleaves", "#0e2a12"), ground=("dirt", "#1a1a10", "#4a4a24"),
       props=["bigleaf", "liana", "swamp"], haze=(120, 160, 120), dark=True),
  [["rain", 34], ["firefly", 12]], dict(base="selva", seed=311, root=47, scale="PHR"), ["culebrita", "abejita", "gusanito"], [
    M("serpienteequis", "Serpiente equis", "cobra", "#7a5a3a", 0.9, 1.5, "P", "serpent", "#7a5a3a,#3a2a1a,#c8a070,#f0c030", style="coil", pattern="x"),
    M("pecari", "Pecarí", "boar", "#4a4038", 1.2, 1.2, "b", "quad", "#4a4038,#2a2420,#a8a090,#ff3020", head="pig", tusks=True),
    M("hormigaarriera", "Hormiga arriera", "wasp-sting", "#8a3a1a", 0.6, 1.2, "P", "bug", "#8a3a1a,#5a2410,#4a8a2a,#ff3020", style="ant", leaf=True),
    M("ranalluvia", "Rana de lluvia", "frog", "#6a8a3a", 0.6, 1.0, "W", "frog", "#6a8a3a,#3a5a24,#c8e070,#e03020"),
    M("monocariblanco", "Mono cariblanco", "monkey", "#2a2420", 0.9, 1.2, "b", "monkey", "#2a2420,#1a1410,#f0e8d8,#201010"),
    M("tigrillosalvaje", "Tigrillo salvaje", "wolf-head", "#c8a050", 1.0, 1.3, "b", "quad", "#c8a050,#8a6a30,#f0e0c0,#a0ff60", head="cat", spots="#3a2a14"),
    M("tarantuladarien", "Tarántula del Darién", "hanging-spider", "#3a2a2a", 1.1, 1.2, "P", "bug", "#3a2a2a,#24181a,#e06a2a,#ff3020", style="spider", hairy=True),
    M("caminantesinrumbo", "Caminante sin rumbo", "shambling-zombie", "#6a6a5a", 1.3, 1.2, "U", "biped", "#8a8070,#4a5a3a,#c8b080,#e0ff80", head="human", hat="cap", body="rags", held="machete", fx="ghost"),
    M("plantased", "Planta de la sed", "evil-tree", "#6a8a2a", 1.4, 1.1, "V", "plant", "#6a8a2a,#3a5a18,#e8d040,#ff3020", style="pitcher"),
    M("murcielagodarien", "Murciélago pescador", "evil-bat", "#8a5a3a", 0.7, 1.2, "b", "bat", "#8a5a3a,#5a3a24,#e8b070,#f0e040"),
  ])

# ======================================================================== llano
Z("llano", "tatacoa", "Desierto de la Tatacoa",
  "Laberintos de tierra roja y gris bajo un cielo lleno de estrellas. De día quema; de noche, algo aúlla.",
  dict(sky=("#1a1a3a", "#e07a4a"), far=("badlands", "#a8402a", "#d86a40"), mid=("badlands", "#8a8478"), ground=("dirt", "#6a2a1a", "#d8704a"),
       props=["cactus", "cactus", "rock"], haze=(230, 140, 100), stars=True),
  [["heat", 1], ["dust", 20], ["star", 18]], dict(base="llano", seed=401, root=50, scale="PHR"), ["grillo", "lagartijita", "pollito"], [
    M("cactusandante", "Cactus andante", "evil-tree", "#4a8a4a", 1.4, 1.1, "V", "plant", "#4a8a4a,#2e5a2e,#f0e0c0,#ff3020", style="cactus"),
    M("zorrodesierto", "Zorro del desierto", "wolf-head", "#c8803a", 0.9, 1.2, "b", "quad", "#c8803a,#8a5020,#f0e0c0,#f0e040", head="fox"),
    M("escorpionrojo", "Escorpión rojo", "scorpion", "#c03a1a", 0.8, 1.4, "P", "bug", "#c03a1a,#6a1a0a,#f0a040,#ffe040", style="scorpion"),
    M("lagartocornudo", "Lagarto cornudo", "snake", "#a8704a", 1.1, 1.1, "b", "lizard", "#a8704a,#6a4028,#e0c090,#201010", style="horned"),
    M("gallinazo", "Gallinazo", "vulture", "#1a1a1a", 0.8, 1.1, "U", "bird", "#1a1a1a,#3a3a3a,#8a8a8a,#ff3020", style="perch", bald=True),
    M("armadillofosil", "Armadillo fósil", "skeleton", "#e0d8c0", 1.8, 1.0, "U", "quad", "#e0d8c0,#a89a80,#f8f0e0,#ff6020", head="bone", bones=True, big=True),
    M("polvorojo", "Polvo rojo", "ghost", "#d06a3a", 0.9, 1.1, "F", "spirit", "#d06a3a,#f0a070,#8a3a1a,#ffe060", style="dust"),
    M("tarantularoja", "Tarántula roja", "hanging-spider", "#8a2a1a", 1.0, 1.2, "P", "bug", "#8a2a1a,#4a1a0e,#e8804a,#ff3020", style="spider", hairy=True),
    M("coral2", "Serpiente coral", "cobra", "#e03020", 0.8, 1.4, "P", "serpent", "#e03020,#1a1a1a,#f0e040,#201010", style="wave", pattern="coral"),
    M("buscadorestrellas", "Buscador de estrellas", "hooded-figure", "#4a4a7a", 1.1, 1.2, "L", "biped", "#8a6048,#3a3a6a,#f0e080,#ffffa0", head="human", hat="cone", body="robe", held="staff", fx="stars"),
  ])
Z("llano", "guajira", "La Guajira",
  "Arena, viento y el mar al lado. Los cardones están de pie como gente que espera.",
  dict(sky=("#4a9ad8", "#f0e0b0"), far=("sea", "#3a8ab8", "#a0e0f0"), mid=("dunes", "#e0b070"), ground=("sand", "#a87a40", "#f0d090"),
       props=["cardon", "cardon", "flamingo"], haze=(250, 230, 190)),
  [["sand", 22], ["heat", 1]], dict(base="llano", seed=403, root=52, scale="HARM"), ["cangrejito", "lagartijita", "grillo"], [
    M("cardonvivo", "Cardón vivo", "evil-tree", "#5a8a5a", 1.5, 1.0, "V", "plant", "#5a8a5a,#3a6a3a,#f0e8c0,#ff3020", style="cardon"),
    M("chivosalvaje", "Chivo salvaje", "charging-bull", "#8a6a4a", 1.1, 1.2, "b", "quad", "#8a6a4a,#5a4028,#f0e8d8,#e8c030", head="goat", horns=True),
    M("flamenco", "Flamenco rojo", "vulture", "#f07a8a", 0.7, 1.1, "b", "bird", "#f07a8a,#f8b0b8,#1a1a1a,#201010", style="wader", beak="bent"),
    M("iguanaarena", "Iguana de la arena", "snake", "#c8a060", 1.1, 1.1, "b", "lizard", "#c8a060,#8a6a3a,#f0e0b0,#201010", style="crest"),
    M("remolinoarena", "Remolino de arena", "ghost", "#e0c080", 1.0, 1.2, "b", "spirit", "#d8b070,#f0e0b0,#a07a40,#ff6020", style="dust"),
    M("alacranarena", "Alacrán de la arena", "scorpion", "#d8b070", 0.8, 1.3, "P", "bug", "#d8b070,#8a6a3a,#f0e0b0,#201010", style="scorpion"),
    M("piratahogado", "Pirata ahogado", "skeleton", "#e0d8c0", 1.2, 1.3, "U", "biped", "#e0d8c0,#3a3a5a,#c02a2a,#40e0c0", head="skull", hat="tricorn", body="rags", held="saber"),
    M("ermitanoarena", "Cangrejo ermitaño", "croc-jaws", "#e07040", 1.3, 1.0, "W", "crab", "#e07040,#a04a24,#f0e0c8,#201010", shell=True),
    M("muladesierto", "Mula del desierto", "charging-bull", "#7a5a3a", 1.4, 1.1, "b", "quad", "#7a5a3a,#4a3420,#c8a880,#201010", head="horse", ears=True, big=True),
    M("gaviota", "Gaviota furiosa", "raven", "#e8e8e8", 0.5, 1.1, "b", "bird", "#e8e8e8,#a8a8a8,#f0c030,#201010", style="flying"),
  ])
Z("llano", "canon", "Cañón del Chicamocha",
  "Un cañón tan hondo que el río abajo parece un hilo. El calor sube por las paredes.",
  dict(sky=("#e0903a", "#f8e0a0"), far=("canyon", "#a8603a", "#e09060"), mid=("canyon", "#8a4a2a"), ground=("dirt", "#6a3a1e", "#c88050"),
       props=["rock", "cactus", "agave"], haze=(250, 200, 150)),
  [["heat", 1], ["dust", 18], ["ember", 8]], dict(base="llano", seed=407, root=48, scale="HARM"), ["grillo", "hormiguita", "pollito"], [
    M("cabracanon", "Cabra del cañón", "charging-bull", "#a8804a", 1.1, 1.2, "b", "quad", "#a8804a,#6a4a24,#f0e0c0,#e8c030", head="goat", horns=True),
    M("condorcanon", "Cóndor del cañón", "vulture", "#2a2420", 1.0, 1.2, "b", "bird", "#2a2420,#e8e0d0,#c88060,#ff6020", style="flying"),
    M("hormigaculona", "Hormiga culona", "wasp-sting", "#6a2a14", 0.8, 1.2, "F", "bug", "#6a2a14,#3a1408,#c84a2a,#ff3020", style="ant", fat=True),
    M("lagartijarisco", "Lagartija del risco", "snake", "#a86a3a", 0.8, 1.2, "F", "lizard", "#a86a3a,#6a3e20,#f0b070,#201010", style="low"),
    M("rocacae", "Roca que cae", "rock-golem", "#8a5a3a", 2.0, 1.0, "S", "golem", "#8a5a3a,#5a3a24,#c89060,#ff8020", style="ball"),
    M("arrierocanon", "Arriero del cañón", "hooded-figure", "#8a6a4a", 1.2, 1.2, "f", "biped", "#8a5a3a,#e8e0d0,#c84a2a,#ffe060", head="human", hat="wide", body="ruana", held="machete"),
    M("serpientecazadora", "Serpiente cazadora", "snake", "#8a7a4a", 1.0, 1.3, "P", "serpent", "#8a7a4a,#5a4a28,#d8c890,#f0c030", style="rise"),
    M("halconperegrino", "Halcón peregrino", "vulture", "#5a5a6a", 0.7, 1.4, "b", "bird", "#5a5a6a,#e8e0d0,#2a2a3a,#f0c030", style="flying"),
    M("vientocaliente", "Viento caliente", "ghost", "#f0a050", 0.9, 1.2, "F", "spirit", "#f0a050,#f8d0a0,#c86a2a,#ffffff", style="dust"),
    M("jabaliriscos", "Jabalí del risco", "boar", "#5a3a2a", 1.3, 1.2, "b", "quad", "#5a3a2a,#3a2418,#e8e0d0,#ff3020", head="pig", tusks=True),
  ])
Z("llano", "volcan", "Faldas del Volcán",
  "Ceniza caliente, ríos de lava y un trueno que viene de abajo.",
  dict(sky=("#2a1010", "#c84a1a"), far=("volcano", "#2a1a1a", "#ff6a1a"), mid=("hills", "#1e1414"), water=("#ff6a1a", "#ffc040", 100),
       ground=("lavarock", "#1a1010", "#5a3a30"), props=["lavarock", "deadtree", "fumarole"], haze=(255, 120, 60)),
  [["ember", 30], ["ash", 14], ["glow", 1]], dict(base="llano", seed=409, root=45, scale="PHR"), ["lagartijita", "grillo", "erizo"], [
    M("salamandralava", "Salamandra de lava", "snake", "#e05a1a", 1.1, 1.3, "F", "lizard", "#e05a1a,#8a2a0a,#ffd040,#ffffff", style="low", fire=True),
    M("perrobrasa", "Perro de brasa", "wolf-head", "#3a1a14", 1.1, 1.3, "F", "quad", "#3a1a14,#1e0e0a,#ff6a1a,#ffd040", head="dog", fire=True),
    M("pajaroceniza", "Pájaro de ceniza", "raven", "#6a6460", 0.7, 1.2, "F", "bird", "#6a6460,#3a3634,#ff8020,#ffd040", style="flying", fire=True),
    M("rocafundida", "Roca fundida", "rock-golem", "#3a2420", 2.0, 1.1, "F", "golem", "#3a2420,#1e1210,#ff6a1a,#ffe060", style="lava", big=True),
    M("espirituerupcion", "Espíritu de la erupción", "burning-skull", "#ff6a1a", 1.0, 1.3, "F", "spirit", "#ff6a1a,#ffd040,#8a1a0a,#ffffff", style="flame"),
    M("gusanofuego", "Gusano de fuego", "leeching-worm", "#d84a1a", 0.9, 1.2, "F", "worm", "#d84a1a,#8a2a0a,#ffd040,#ffffff"),
    M("torolava", "Toro de lava", "charging-bull", "#2a1a14", 1.7, 1.3, "F", "quad", "#2a1a14,#140a08,#ff6a1a,#ffd040", head="bull", horns=True, fire=True, big=True),
    M("murcielagohumo", "Murciélago de humo", "evil-bat", "#4a4448", 0.6, 1.2, "F", "bat", "#4a4448,#2a2628,#ff8020,#ffd040"),
    M("escarabajobrasa", "Escarabajo de brasa", "wasp-sting", "#3a1a10", 0.8, 1.2, "F", "bug", "#3a1a10,#1e0e08,#ff6a1a,#ffd040", style="beetle", glow=True),
    M("hombreceniza", "Hombre de ceniza", "shambling-zombie", "#7a7470", 1.3, 1.2, "F", "biped", "#7a7470,#4a4644,#ff6a1a,#ffd040", head="human", body="bare", held="none", fx="ash"),
  ])

# ======================================================================== ruinas
Z("ruinas", "tierradentro", "Hipogeos de Tierradentro",
  "Tumbas cavadas en la roca y pintadas de rojo y negro. Bajas por una escalera de caracol a la oscuridad.",
  dict(sky=("#1a1410", "#3a2a20"), far=("tomb", "#c8b8a0", "#a8301a"), mid=None, ground=("rock", "#2a2018", "#8a7a60"),
       props=["urn", "column", "torch"], haze=(180, 140, 100), dark=True),
  [["dust", 20], ["shaft", 2]], dict(base="ruinas", seed=501, root=47, scale="PHR"), ["ratoncito", "hormiguita", "erizo"], [
    M("guardiantumba", "Guardián de la tumba", "rock-golem", "#a89880", 1.9, 1.1, "S", "golem", "#a89880,#6a5a48,#a8301a,#ff8020", style="statue"),
    M("urnaviva", "Urna viva", "rock-golem", "#a86a3a", 1.6, 1.0, "S", "object", "#a86a3a,#6a3a1a,#2a1a10,#ffb040", style="urn"),
    M("murcielagotumba", "Murciélago de tumba", "evil-bat", "#3a2a24", 0.6, 1.2, "U", "bat", "#3a2a24,#1e1410,#a8301a,#ff3020"),
    M("sombrapintada", "Sombra pintada", "ghost", "#a8301a", 1.0, 1.3, "U", "spirit", "#1a1410,#a8301a,#f0e8d8,#ffe060", style="painting"),
    M("calaverapintada", "Calavera pintada", "death-skull", "#e0d0b0", 0.8, 1.2, "U", "spirit", "#e0d0b0,#a8301a,#1a1410,#ff6020", style="skull"),
    M("serpienteescalera", "Serpiente de la escalera", "cobra", "#6a5a48", 1.2, 1.2, "P", "serpent", "#6a5a48,#3a3028,#a8301a,#ffb040", style="coil", pattern="bands"),
    M("aranaurna", "Araña de la urna", "hanging-spider", "#4a3a30", 0.9, 1.2, "P", "bug", "#4a3a30,#2a2018,#a8301a,#ff3020", style="spider"),
    M("escarabajotumba", "Escarabajo de la tumba", "wasp-sting", "#3a5a4a", 0.7, 1.1, "P", "bug", "#3a5a4a,#1e3028,#c8a040,#ff3020", style="beetle"),
    M("saqueador", "Saqueador maldito", "shambling-zombie", "#6a5a4a", 1.3, 1.2, "U", "biped", "#8a7a68,#4a3a2a,#e8c040,#a0ff80", head="human", hat="cap", body="rags", held="pick", fx="ghost"),
    M("ojopintado", "Ojo pintado", "ghost", "#a8301a", 0.9, 1.3, "L", "spirit", "#a8301a,#f0e8d8,#1a1410,#ffffff", style="eye"),
  ])
Z("ruinas", "murallas", "Las Murallas de Cartagena",
  "Cañones viejos, garitas vacías y el mar golpeando la piedra. Los centinelas siguen de guardia.",
  dict(sky=("#141a34", "#4a5a8a"), far=("sea", "#1a2a4a", "#6a8ab0"), mid=("walls", "#8a7a60"), ground=("stone", "#4a443a", "#a89a80"),
       props=["garita", "cannon", "palm"], haze=(160, 170, 200), moon=True),
  [["mist", 4], ["mote", 8]], dict(base="ruinas", seed=503, root=50, scale="HARM"), ["cangrejito", "ratoncito", "pajarito"], [
    M("soldadofantasma", "Soldado fantasma", "shambling-zombie", "#8ab0c0", 1.3, 1.3, "U", "biped", "#8aa0b0,#c8c8d0,#c02a2a,#a0e8ff", head="human", hat="morion", body="armor", held="halberd", fx="ghost"),
    M("canonvivo", "Cañón vivo", "rock-golem", "#3a3a3a", 1.8, 1.3, "f", "object", "#3a3a3a,#1e1e1e,#8a5a2a,#ff6020", style="cannon"),
    M("piratesqueleto", "Pirata esqueleto", "skeleton", "#e0d8c0", 1.1, 1.3, "U", "biped", "#e0d8c0,#2a2a3a,#c02a2a,#ff6020", head="skull", hat="bandana", body="rags", held="saber"),
    M("gaviotamuralla", "Gaviota de la muralla", "raven", "#e0e0e0", 0.5, 1.1, "b", "bird", "#e0e0e0,#9a9a9a,#f0c030,#201010", style="flying"),
    M("cangrejofoso", "Cangrejo del foso", "croc-jaws", "#6a4a3a", 1.2, 1.1, "W", "crab", "#6a4a3a,#4a3024,#c8a080,#ff3020"),
    M("anclacadena", "Ancla con cadena", "rock-golem", "#5a5a60", 1.6, 1.2, "S", "object", "#5a5a60,#3a3a40,#8a5a3a,#ff6020", style="anchor"),
    M("balacanon", "Bala de cañón", "rock-golem", "#2a2a2a", 1.5, 1.3, "S", "golem", "#2a2a2a,#141414,#ff6020,#ffd040", style="ball", fuse=True),
    M("ratabarco", "Rata del barco", "rat", "#5a5048", 0.7, 1.1, "B", "quad", "#5a5048,#3a3028,#e0a0a0,#ff3020", head="rat"),
    M("loropirata", "Loro pirata", "raven", "#3ac040", 0.6, 1.1, "b", "bird", "#3ac040,#f0c030,#e0302a,#201010", style="perch", beak="hook", patch=True),
    M("espiritufoso", "Espíritu del foso", "floating-ghost", "#4a7a8a", 1.0, 1.2, "C", "spirit", "#3a6a7a,#a0d8e0,#ffffff,#e0ffff", style="water"),
  ])
Z("ruinas", "mompox", "Mompox",
  "Un pueblo de casas blancas junto al río, donde los relojes se pararon. Las mecedoras se mueven solas.",
  dict(sky=("#1a1430", "#6a4a6a"), far=("town", "#e8e0d0", "#8a5a3a"), mid=None, ground=("stone", "#3a342a", "#a89a7a"),
       props=["lamp", "rocker", "balcony"], haze=(200, 170, 190), moon=True),
  [["firefly", 14], ["mist", 3]], dict(base="ruinas", seed=507, root=48, scale="MIN"), ["ratoncito", "pajarito", "polilla"], [
    M("mecedora", "Mecedora que se mece", "rock-golem", "#6a4a2a", 1.4, 1.0, "U", "object", "#6a4a2a,#3a2a14,#d8c8a0,#ffe060", style="rocker"),
    M("iguanatejado", "Iguana del tejado", "snake", "#6a9a4a", 1.1, 1.1, "b", "lizard", "#6a9a4a,#3a6a2a,#e0c060,#201010", style="crest"),
    M("orfebre", "Orfebre maldito", "hooded-figure", "#c8c8d0", 1.2, 1.2, "L", "biped", "#8a6048,#3a3a4a,#e8e8f0,#a0e8ff", head="human", body="coat", held="hammer", fx="silver"),
    M("farolvivo", "Farol vivo", "ghost", "#f0c040", 0.9, 1.2, "F", "spirit", "#3a3a3a,#f0c040,#fff0a0,#ffffff", style="lantern"),
    M("gatotejados", "Gato de los tejados", "wolf-head", "#2a2a2a", 0.8, 1.2, "b", "quad", "#2a2a2a,#141414,#5a5a5a,#a0ff60", head="cat"),
    M("campanarota", "Campana rota", "rock-golem", "#a88a3a", 1.6, 1.1, "S", "object", "#a88a3a,#6a5420,#f0d880,#ff6020", style="bell"),
    M("murcielagocampanario", "Murciélago del campanario", "evil-bat", "#3a3030", 0.6, 1.2, "U", "bat", "#3a3030,#1e1818,#a08080,#ff3020"),
    M("noviabalcon", "Novia del balcón", "floating-ghost", "#e8e0f0", 1.0, 1.3, "U", "spirit", "#e8e0f0,#c8c0d8,#ffffff,#a080ff", style="woman", veil=True),
    M("relojparado", "Reloj parado", "rock-golem", "#8a6a3a", 1.5, 1.1, "S", "object", "#8a6a3a,#5a4424,#f0e8d8,#ff6020", style="clock"),
    M("bogapuerto", "Boga del puerto", "shambling-zombie", "#6a5a4a", 1.2, 1.2, "U", "biped", "#5a3a2a,#e8e0d0,#3a5a8a,#a0e8ff", head="human", hat="wide", body="tunic", held="oar", fx="ghost"),
  ])
Z("ruinas", "minassal", "Las Minas de Sal",
  "Galerías de sal bajo la montaña, iluminadas de azul y violeta. El techo cruje.",
  dict(sky=("#141428", "#2a2a4a"), far=("cave", "#3a3a5a", "#8a8ac0"), mid=("crystals", "#c8c8f0"), ground=("rock", "#3a3a4a", "#d0d0e0"),
       props=["saltcrystal", "minecart", "lamp"], haze=(170, 170, 240), dark=True),
  [["mote", 18], ["dust", 10]], dict(base="ruinas", seed=509, root=45, scale="LOC"), ["ratoncito", "hormiguita", "gusanito"], [
    M("golemsal", "Golem de sal", "rock-golem", "#e8e8f0", 2.0, 1.0, "S", "golem", "#e8e8f0,#a8a8c0,#ffffff,#6060ff", style="salt", big=True),
    M("cristalsal", "Cristal de sal", "ghost", "#c8c8ff", 0.9, 1.2, "L", "spirit", "#8a8ae0,#e0e0ff,#ffffff,#ffffff", style="crystal"),
    M("minerosal", "Minero de sal", "shambling-zombie", "#8a8a9a", 1.2, 1.2, "U", "biped", "#8a7a68,#5a5a6a,#e8e8f0,#a0a0ff", head="human", hat="helm", body="tunic", held="pick", fx="ghost"),
    M("murcielagosal", "Murciélago de sal", "evil-bat", "#c8c8d8", 0.6, 1.2, "b", "bat", "#c8c8d8,#8a8a9a,#ffffff,#6060ff"),
    M("gusanomina", "Gusano de la mina", "leeching-worm", "#a89a8a", 1.0, 1.1, "b", "worm", "#a89a8a,#6a5e50,#e8e0d8,#ff3020"),
    M("carretaviva", "Carreta viva", "rock-golem", "#6a5a4a", 1.7, 1.1, "S", "object", "#6a5a4a,#3a3028,#e8e8f0,#ff6020", style="cart"),
    M("lagartosal", "Lagarto de sal", "snake", "#e0e0e8", 1.0, 1.1, "b", "lizard", "#e0e0e8,#a8a8b8,#ffffff,#6060ff", style="low"),
    M("aguasalada", "Agua salada", "slime", "#80a0e0", 1.2, 1.0, "C", "blob", "#80a0e0,#4a6ab0,#e0f0ff,#ffffff", style="slime", crystals=True),
    M("lamparaminero", "Lámpara de minero", "ghost", "#f0d060", 0.8, 1.2, "F", "spirit", "#5a4a3a,#f0d060,#fff0a0,#ffffff", style="lantern"),
    M("topo", "Topo gigante", "rat", "#4a3a3a", 1.4, 1.1, "b", "quad", "#4a3a3a,#2a2020,#e0a0a0,#201010", head="mole"),
  ])

# ======================================================================== abismo: the Tibetan hells
Z("abismo", "infiernoscalientes", "Los Ocho Infiernos Calientes",
  "Un suelo de hierro al rojo bajo un cielo de fuego. Cada descenso es un infierno más hondo, y se sufre más tiempo.",
  dict(sky=("#3a0808", "#ff6a1a"), far=("flames", "#8a1a08", "#ffb040"), mid=("ironwall", "#2a0e0a"), ground=("iron", "#3a0e08", "#e8501a"),
       props=["ironspike", "flames", "flames"], haze=(255, 100, 40)),
  [["ember", 34], ["glow", 1], ["heat", 1]], dict(base="abismo", seed=601, root=44, scale="PHR", tempo=0.8), ["lagartijita", "grillo", "hormiguita", "erizo"], [
    M("cabezatoro", "Guardián con cabeza de toro", "minotaur", "#8a2a1a", 1.7, 1.4, "F", "biped", "#8a2a1a,#3a1410,#e8c040,#ffd040", head="ox", body="armor", held="club", big=True),
    M("cabezacaballo", "Guardián con cabeza de caballo", "minotaur", "#5a2a1a", 1.6, 1.4, "F", "biped", "#5a2a1a,#2a1410,#e8c040,#ffd040", head="horse", body="armor", held="trident", big=True),
    M("perrohierro", "Perro de hierro", "wolf-head", "#4a4448", 1.3, 1.4, "F", "quad", "#4a4448,#2a2628,#ff6a1a,#ffd040", head="dog", fire=True, big=True),
    M("cuervopico", "Cuervo de pico de hierro", "raven", "#2a2228", 0.8, 1.4, "F", "bird", "#2a2228,#141014,#a8a8b0,#ff3020", style="perch", beak="iron"),
    M("serquerevive", "Ser que revive", "shambling-zombie", "#c86a4a", 1.2, 1.2, "U", "biped", "#c86a4a,#8a3a2a,#ff6a1a,#ffd040", head="human", body="bare", held="none", fx="flame"),
    M("llamahambrienta", "Llama hambrienta", "small-fire", "#ff6a1a", 1.0, 1.4, "F", "spirit", "#ff6a1a,#ffd040,#8a1a0a,#ffffff", style="flame", mouth=True),
    M("herrero", "Herrero del infierno", "ogre", "#6a2a1a", 1.7, 1.4, "F", "biped", "#6a2a1a,#2a1410,#a8a8b0,#ffd040", head="horned", body="bare", held="hammer", big=True),
    M("rocaaplastadora", "Roca aplastadora", "rock-golem", "#4a2a24", 2.1, 1.2, "S", "golem", "#4a2a24,#2a1410,#ff6a1a,#ffd040", style="ram", big=True),
    M("gritofuego", "Grito de fuego", "shouting", "#ff8a3a", 0.9, 1.4, "F", "spirit", "#ff8a3a,#ffd040,#8a1a0a,#ffffff", style="scream"),
    M("gusanohierro", "Gusano de hierro", "leeching-worm", "#5a5458", 1.1, 1.3, "F", "worm", "#5a5458,#3a3638,#ff6a1a,#ffd040", iron=True),
  ], descents=["Revivir", "La Línea Negra", "El Aplastamiento", "Los Alaridos", "Los Grandes Alaridos", "El Calor", "El Calor Intenso", "Sin Respiro"])
Z("abismo", "infiernosfrios", "Los Ocho Infiernos Fríos",
  "Hielo y nieve sin luz, y un viento que parte la piel. Cada descenso es más frío y más largo.",
  dict(sky=("#04060e", "#1a2a4a"), far=("icewall", "#1a2a44", "#6a8ac0"), mid=("ice", "#2a3a5a"), ground=("snow", "#2a3448", "#a8b8d8"),
       props=["icerock", "icicle", "bluelotus"], haze=(140, 170, 230), dark=True),
  [["snow", 50], ["fog", 4]], dict(base="abismo", seed=603, root=42, scale="LOC", tempo=1.1), ["polilla", "ratoncito", "caracol", "tortuguita"], [
    M("serampollas", "Ser de ampollas", "slime", "#c8b8c0", 1.5, 1.0, "C", "blob", "#c8b8c0,#8a7a88,#f0e0e8,#40a0ff", style="blister"),
    M("castaneteo", "Dientes que castañetean", "death-skull", "#e0e8f0", 0.9, 1.4, "U", "spirit", "#e0e8f0,#8aa0c0,#1a2a4a,#80e0ff", style="skull", chatter=True),
    M("lamentohelado", "Lamento helado", "floating-ghost", "#a0c0e8", 1.0, 1.3, "U", "spirit", "#6a8ac0,#c8e0ff,#ffffff,#e0ffff", style="ghost"),
    M("gusanohielo", "Gusano del hielo", "leeching-worm", "#a0c8e8", 1.1, 1.2, "C", "worm", "#a0c8e8,#6a90b8,#e0f4ff,#2a60c0"),
    M("carcelerohielo", "Carcelero de hielo", "hooded-figure", "#4a6a9a", 1.7, 1.3, "C", "biped", "#8ab0d8,#3a5a8a,#e0f4ff,#80e0ff", head="helm", body="armor", held="chain", big=True),
    M("pajarohielo", "Pájaro de hielo negro", "raven", "#1a2a44", 0.8, 1.3, "C", "bird", "#1a2a44,#3a4a6a,#a0c8e8,#80e0ff", style="flying"),
    M("lotoazul", "Loto azul partido", "evil-tree", "#3a6ac8", 1.3, 1.2, "C", "plant", "#3a6ac8,#24408a,#a0c8ff,#ffffff", style="lotus", cracked=True),
    M("lotorojo", "Loto rojo partido", "evil-tree", "#c83a4a", 1.3, 1.3, "C", "plant", "#c83a4a,#8a2430,#ffa0a8,#ffffff", style="lotus", cracked=True),
    M("osooscuridad", "Oso de la oscuridad", "bear-head", "#1a2030", 1.9, 1.2, "C", "quad", "#1a2030,#0e1018,#6a8ac0,#80e0ff", head="bear", big=True),
    M("vientocorta", "Viento que corta", "ghost", "#c8e0ff", 0.9, 1.4, "C", "spirit", "#a0c0e8,#e8f4ff,#ffffff,#2a60c0", style="wind"),
  ], descents=["Las Ampollas", "Las Ampollas Reventadas", "El Castañeteo", "Los Lamentos", "Los Quejidos", "Grietas como Loto Azul", "Grietas como Loto Rojo", "El Gran Loto"])
Z("abismo", "infiernosvecinos", "Los Infiernos Vecinos",
  "A la salida de los infiernos: un pozo de brasas, una ciénaga podrida, una llanura de navajas, un bosque de espadas y un río de ceniza.",
  dict(sky=("#1a1424", "#6a4a5a"), far=("swordtrees", "#2a2430", "#a8a8c0"), mid=("hills", "#24202a"), water=("#4a4448", "#8a8288", 104),
       ground=("dirt", "#1e181c", "#6a5a60"), props=["swordtree", "razors", "bones"], haze=(180, 150, 170)),
  [["ash", 24], ["spark", 12]], dict(base="abismo", seed=607, root=43, scale="HARM", tempo=0.9), ["ratoncito", "erizo", "hormiguita"], [
    M("arbolespadas", "Árbol de espadas", "evil-tree", "#a8a8b8", 1.8, 1.3, "S", "plant", "#4a4448,#a8a8b8,#e8e8f0,#ff3020", style="swordtree", big=True),
    M("cuervohierro", "Cuervo de hierro", "raven", "#5a5a64", 0.9, 1.4, "S", "bird", "#5a5a64,#3a3a44,#a8a8b8,#ff3020", style="flying", metal=True),
    M("navajaviva", "Navaja viva", "plain-dagger", "#c8c8d8", 0.8, 1.5, "S", "object", "#c8c8d8,#6a6a78,#3a2a24,#ff3020", style="blade"),
    M("gusanocienaga", "Gusano de la ciénaga", "leeching-worm", "#6a6a4a", 1.1, 1.2, "P", "worm", "#6a6a4a,#4a4a30,#a8a870,#ff3020"),
    M("perrobrasas", "Perro de las brasas", "wolf-head", "#3a2420", 1.3, 1.4, "F", "quad", "#3a2420,#1e1210,#ff6a1a,#ffd040", head="dog", fire=True),
    M("cadavercienaga", "Cadáver de la ciénaga", "shambling-zombie", "#6a7a5a", 1.4, 1.2, "U", "biped", "#7a8a6a,#4a5a3a,#a8a870,#c8ff60", head="human", body="rags", held="none", fx="mud"),
    M("brasapozo", "Brasa del pozo", "small-fire", "#ff5a1a", 1.0, 1.4, "F", "spirit", "#ff5a1a,#ffd040,#6a1a0a,#ffffff", style="flame"),
    M("barqueroceniza", "Barquero de ceniza", "hooded-figure", "#8a8288", 1.4, 1.3, "U", "biped", "#8a8288,#4a4448,#e8e0e8,#ff8020", head="hood", body="robe", held="oar", fx="ash"),
    M("picohierro", "Gusano de pico de hierro", "leeching-worm", "#8a6a5a", 1.0, 1.4, "S", "worm", "#8a6a5a,#5a4038,#c8c8d8,#ff3020", iron=True),
    M("sombrario", "Sombra del río", "ghost", "#5a5458", 1.1, 1.3, "U", "spirit", "#3a3438,#8a8288,#c8c0c8,#ff8020", style="ghost"),
  ], descents=["El Pozo de Brasas", "La Ciénaga Podrida", "La Llanura de Navajas", "El Bosque de Espadas", "El Río de Ceniza"])
Z("abismo", "infiernosefimeros", "Los Infiernos Efímeros",
  "Seres atrapados en las cosas de todos los días: una puerta, un pilar, un fogón, una cuerda, una piedra. Sienten todo lo que les hacen.",
  dict(sky=("#141018", "#4a3a3a"), far=("room", "#3a2a24", "#6a5040"), mid=None, ground=("wood", "#2a1e18", "#7a5a40"),
       props=["door", "pillar", "stove"], haze=(200, 170, 150), dark=True),
  [["dust", 22], ["mote", 6]], dict(base="abismo", seed=609, root=46, scale="MIN", tempo=1.2), ["ratoncito", "polilla", "hormiguita"], [
    M("puertagime", "Puerta que gime", "rock-golem", "#6a4a30", 1.7, 1.1, "S", "object", "#6a4a30,#3a2a1a,#a8a8b0,#ffe060", style="door"),
    M("pilarsiente", "Pilar que siente", "rock-golem", "#a89a88", 2.0, 1.0, "S", "object", "#a89a88,#6a5e50,#c8b8a0,#ff6020", style="pillar"),
    M("fogonllora", "Fogón que llora", "small-fire", "#5a4a40", 1.5, 1.3, "F", "object", "#5a4a40,#3a2e28,#ff6a1a,#ffd040", style="stove"),
    M("cuerdatensa", "Cuerda tensa", "whip", "#c8a870", 1.0, 1.3, "b", "object", "#c8a870,#8a6a40,#e8d8b0,#ff3020", style="rope"),
    M("piedracamino", "Piedra del camino", "rock-golem", "#7a7468", 1.9, 1.0, "S", "golem", "#7a7468,#4a4640,#a8a090,#80c0ff", style="stone", sad=True),
    M("escobacansada", "Escoba cansada", "rock-golem", "#c8a050", 1.0, 1.2, "b", "object", "#8a6a3a,#c8a050,#5a4024,#ffe060", style="broom"),
    M("ollahirviendo", "Olla hirviendo", "round-bottom-flask", "#4a4440", 1.4, 1.2, "F", "object", "#4a4440,#2a2624,#ff6a1a,#ffd040", style="pot"),
    M("cantaroroto", "Cántaro roto", "rock-golem", "#b06a3a", 1.3, 1.1, "S", "object", "#b06a3a,#6a3a1a,#e0a070,#80c0ff", style="jar"),
    M("troncohacha", "Tronco del hacha", "evil-tree", "#6a4a2a", 1.6, 1.1, "V", "object", "#6a4a2a,#3a2a14,#c8a070,#ff6020", style="stump"),
    M("lamparaarde", "Lámpara que arde", "lantern-flame", "#f0c040", 0.9, 1.3, "F", "spirit", "#5a4a3a,#f0c040,#fff0a0,#ffffff", style="lantern"),
  ], descents=["La Puerta", "El Pilar", "El Fogón", "La Cuerda", "La Piedra", "La Escoba"])


def all_monsters():
    return [m for zs in ZONES.values() for z in zs for m in z["monsters"]]


def all_zones():
    return [z for zs in ZONES.values() for z in zs]


RES = {"F": {"fire": 100, "cold": -50}, "C": {"cold": 100, "fire": -50}, "P": {"poison": 100, "fire": -25}, "L": {"light": 100, "poison": -25},
       "U": {"cold": 100, "poison": 100, "light": -50}, "S": {"poison": 100, "light": 25, "cold": -25}, "V": {"poison": 75, "fire": -75},
       "W": {"cold": 25, "light": -50}, "B": {"poison": 25}, "b": {"light": -25}, "c": {"cold": 50, "fire": -25}, "f": {"fire": 50, "cold": -25},
       "p": {"poison": 50, "fire": -25}}
ELEM = {"F": "fire", "C": "cold", "P": "poison", "L": "light"}
