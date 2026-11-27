"""One-off generator (2026-11-27): the 59 sets of levels 204-400, written into data.js, and their
colours into build_lpc.py (SETS) and build_scenes.py (NECKLACES, NECK_ORDER).

Their numbers follow the high sets already there (levels 150-200), as a share of the level:
a plain set's weapon +4%/level of damage, a head 2.55%/level of defence, and so on; ancestral x1.07,
legendary x1.18, mythic x1.3 (the same steps as theirs). Listening bonuses stay what they are
(free replays, slow listening, forgiven accents); the start-of-fight streak creeps up to 13.

usage: python3 scripts/new_sets_400.py   (run once; it refuses if the sets are already there)
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT = {
    "A": dict(h="capiroteastral", b="vestiduraastral", s="escudoastral", g="guantesastral", f="zapatillasastral", t="fajinastral"),
    "S": dict(h="yelmosombra", b="corazasombra", s="escudosombra", g="guantessombra", f="pezunassombra", t="cintosombra"),
    "L": dict(h="yelmoluna", b="mantoluna", s="rodelaluna", g="brazalesluna", f="zapatosluna", t="cordonluna"),
}
JEWEL = dict(a="amuleto", r="anillo")
ELEM = {"f": ("fire", "resFire"), "c": ("cold", "resCold"), "l": ("light", "resLight"), "p": ("poison", "resPoison")}
LISTEN = {"C": "dmgCloze", "D": "dmgDictation"}
TIER = {"": 1.0, "ancestral": 1.07, "legendario": 1.18, "mitico": 1.3}

# id, name, tier, element, listening, kit, weapon base, slots (after h b w), piece names, shirt colours (cord, pendant, shine), LPC (metal, cloth, wood)
SETS = [
    ("teyuna", "La Ciudad Perdida", "", "p", "C", "A", "lanzaastral", "gft",
     ["Corona de Teyuna", "Manto de las Mil Terrazas", "Lanza del Buritaca", "Guantes de Piedra Musgosa", "Sandalias de los Escalones", "Fajín de los Caminos de Piedra"],
     ("#3a5a2a", "#8ab45a", "#e0f0b0"), ("bronze", "forest", "dark")),
    ("tatacoa", "El Desierto de la Tatacoa", "", "f", "D", "S", "mangualsombra", "gft",
     ["Yelmo de las Cárcavas Rojas", "Coraza del Sol de Mediodía", "Mangual de Piedra Roja", "Guantes de Arena", "Pezuñas del Cauce Seco", "Cinto del Cactus"],
     ("#8a3a1a", "#e07a3a", "#ffd0a0"), ("copper", "orange", "red")),
    ("sanagustin", "Los Guardianes de San Agustín", "ancestral", "l", "C", "S", "mangualsombra", "sgf",
     ["Rostro de Piedra con Colmillos", "Coraza del Guardián Tallado", "Mangual del Doble Yo", "Escudo de la Mesita", "Manos de Toba Volcánica", "Pezuñas del Alto de los Ídolos"],
     ("#5a5a4a", "#c8c0a0", "#fff8e0"), ("ceramic", "tan", "iron")),
    ("tierradentro", "Las Tumbas de Tierradentro", "", "c", "D", "L", "tridenteluna", "gft",
     ["Yelmo del Hipogeo", "Manto Pintado en Rojo y Negro", "Tridente de la Escalera de Caracol", "Brazales de los Rombos", "Zapatos de la Bajada", "Cordón de los Muertos Antiguos"],
     ("#2a1a1a", "#c83a2a", "#f0e0d0"), ("iron", "maroon", "dark")),
    ("taraverde", "Tara Verde, la que Libera", "legendario", "p", "C", "A", "espadaastral", "gfa",
     ["Corona de las Cinco Joyas", "Vestidura Verde Esmeralda", "Espada del Loto Azul", "Guantes de la Mano que Da", "Zapatillas del Pie que se Levanta", "Amuleto de las Ocho Liberaciones"],
     ("#1a6a3a", "#3ac870", "#d0ffe0"), ("gold", "forest", "gold")),
    ("chia", "Chía, la Luna Muisca", "", "c", "D", "L", "arcoluna", "gft",
     ["Diadema de la Media Luna", "Manto de la Noche Muisca", "Arco de Plata Pálida", "Brazales de la Marea", "Zapatos del Rocío", "Cordón de las Fases"],
     ("#5a6a8a", "#e0e8f8", "#ffffff"), ("silver", "navy", "silver")),
    ("sue", "Sué, el Sol Muisca", "ancestral", "f", "D", "A", "lanzaastral", "gfa",
     ["Corona de Rayos de Oro", "Vestidura del Mediodía", "Lanza del Primer Amanecer", "Guantes Dorados de Sogamoso", "Zapatillas del Camino del Sol", "Disco del Templo del Sol"],
     ("#a8701a", "#ffcf3a", "#fff8d0"), ("gold", "yellow", "gold")),
    ("catedralsal", "La Catedral de Sal", "", "l", "C", "S", "varasombra", "gft",
     ["Yelmo de Halita", "Coraza de la Mina Honda", "Vara de la Cruz de Sal", "Guantes del Minero", "Pezuñas del Túnel", "Cinto de la Sal Blanca"],
     ("#6a7a8a", "#d8e8f0", "#ffffff"), ("ceramic", "white", "light")),
    ("choco", "La Lluvia del Chocó", "", "c", "D", "L", "sableluna", "gft",
     ["Sombrero de Hoja de Palma", "Manto que Nunca se Seca", "Sable del Atrato", "Brazales de Bejuco", "Zapatos del Barro Blando", "Cordón de la Manigua"],
     ("#1a4a4a", "#3aa8a0", "#c0f0e8"), ("bronze", "teal", "medium")),
    ("milarepa", "El Canto de Milarepa", "legendario", "c", "C", "A", "espadaastral", "gft",
     ["Gorro del Ermitaño", "Vestidura de Algodón Blanco", "Bastón del Cantor", "Guantes de la Cueva Fría", "Zapatillas del Tíbet Alto", "Fajín del Calor Interno"],
     ("#a8a8b0", "#f4f4f0", "#ffffff"), ("silver", "white", "light")),
    ("yurupari", "La Flauta de Yuruparí", "", "p", "D", "L", "arcoluna", "gft",
     ["Corona de Plumas de Guacamaya", "Manto de Corteza", "Arco del Vaupés", "Brazales de la Flauta Sagrada", "Zapatos del Raudal", "Cordón de Chambira"],
     ("#3a2a1a", "#e05a1a", "#ffd060"), ("bronze", "brown", "medium")),
    ("pulowi", "Pulowi, la de la Lluvia Escondida", "ancestral", "c", "C", "A", "lanzaastral", "gfa",
     ["Velo de la Arena Mojada", "Manta Wayuu de Mil Colores", "Lanza del Pozo Escondido", "Guantes del Tejido", "Zapatillas del Cabo de la Vela", "Mochila de la Lluvia Guardada"],
     ("#8a2a5a", "#f070a0", "#ffe0f0"), ("copper", "purple", "red")),
    ("juya", "Juyá, el que Trae la Lluvia", "", "l", "D", "A", "arcoastral", "gft",
     ["Capirote del Nubarrón", "Vestidura del Viento Alisio", "Arco del Trueno Lejano", "Guantes de Agua Fresca", "Zapatillas del Jagüey", "Fajín del Cazador"],
     ("#2a3a6a", "#7fc4ff", "#fffbd0"), ("silver", "sky", "silver")),
    ("quimbaya", "El Tesoro Quimbaya", "mitico", "f", "C", "A", "espadaastral", "sgfa",
     ["Casco de Oro Batido", "Vestidura de los Caciques", "Espada del Poporo", "Escudo de la Mujer Sentada", "Guantes del Orfebre", "Zapatillas del Cauca Medio", "Poporo de Tumbaga"],
     ("#8a5a0a", "#f0c040", "#fff8d0"), ("gold", "black", "gold")),
    ("zenu", "La Filigrana Zenú", "", "p", "C", "L", "sableluna", "gft",
     ["Yelmo de Hilo de Oro", "Manto de los Canales", "Sable de la Ciénaga", "Brazales Tejidos", "Zapatos del Sombrero Vueltiao", "Cordón de Caña Flecha"],
     ("#6a5a2a", "#d8c070", "#fff0b0"), ("gold", "tan", "gold")),
    ("manjushri", "Mañjushri, la Espada que Corta la Duda", "legendario", "f", "C", "A", "espadaastral", "sgf",
     ["Corona del Joven Príncipe", "Vestidura Color Azafrán", "Espada Llameante de la Sabiduría", "Libro de la Perfección", "Guantes del Debate Ganado", "Zapatillas del León"],
     ("#c8701a", "#f0a020", "#fff0c0"), ("gold", "orange", "gold")),
    ("mompox", "Las Noches de Mompox", "", "f", "D", "S", "mandoblesombra", "gft",
     ["Yelmo de la Albarrada", "Coraza de las Mecedoras", "Mandoble del Río Lento", "Guantes de Filigrana", "Pezuñas de la Calle Real", "Cinto de la Procesión"],
     ("#5a3a2a", "#e8b060", "#fff0c0"), ("copper", "walnut", "dark")),
    ("nevadoruiz", "El Volcán Dormido", "ancestral", "f", "D", "S", "mangualsombra", "sgf",
     ["Yelmo del Cráter Arenas", "Coraza de Ceniza y Hielo", "Mangual de la Lava", "Escudo de la Nieve Negra", "Guantes de Azufre", "Pezuñas del Glaciar"],
     ("#3a2a2a", "#ff5a1a", "#ffd27a"), ("iron", "red", "red")),
    ("chingaza", "Las Lagunas de Chingaza", "", "c", "C", "L", "tridenteluna", "gft",
     ["Yelmo de la Niebla", "Manto del Páramo Mojado", "Tridente de la Laguna Seca", "Brazales de Musgo", "Zapatos del Frailejón", "Cordón del Agua de Bogotá"],
     ("#3a5a6a", "#8ac8d8", "#e8ffff"), ("silver", "teal", "silver")),
    ("chenrezig", "Chenrezig, los Mil Brazos", "mitico", "l", "D", "A", "lanzaastral", "gfta",
     ["Corona de las Once Caras", "Vestidura de Piel de Antílope", "Lanza de la Compasión", "Mil Guantes de las Mil Manos", "Zapatillas de los Seis Reinos", "Fajín de la Joya", "Rosario de Cristal"],
     ("#e8e8f0", "#ffffff", "#c8e0ff"), ("silver", "white", "silver")),
    ("magdalena", "El Río Grande de la Magdalena", "", "p", "D", "L", "tridenteluna", "gft",
     ["Sombrero del Champán", "Manto de las Dos Orillas", "Tridente del Pescador de Bocachico", "Brazales de Remero", "Zapatos de la Playa", "Cordón de la Atarraya"],
     ("#5a4a2a", "#a8803a", "#e8d0a0"), ("bronze", "brown", "medium")),
    ("karagabi", "Karagabí, el que Hizo el Mundo", "ancestral", "l", "C", "A", "arcoastral", "gfa",
     ["Corona de Jagua", "Vestidura del Primer Día", "Arco que Separó las Aguas", "Guantes Pintados", "Zapatillas de la Selva Alta", "Collar de Chaquiras"],
     ("#1a1a2a", "#e0d040", "#ffffff"), ("gold", "black", "dark")),
    ("tutruica", "Tutruica, el del Agua de Abajo", "", "p", "D", "S", "varasombra", "gft",
     ["Yelmo del Río Profundo", "Coraza de Escamas Negras", "Vara de las Aguas de Abajo", "Guantes del Ahogado", "Pezuñas del Lodo", "Cinto de Raíz"],
     ("#1a2a2a", "#3a8a6a", "#a0e0c0"), ("iron", "forest", "dark")),
    ("naropa", "Las Seis Yogas de Naropa", "legendario", "f", "D", "A", "espadaastral", "gft",
     ["Gorro del Gran Erudito", "Vestidura del Calor Interior", "Espada del Cuerpo Ilusorio", "Guantes del Sueño Lúcido", "Zapatillas de la Luz Clara", "Fajín del Tránsito"],
     ("#7a1a1a", "#e04a2a", "#ffc0a0"), ("gold", "maroon", "red")),
    ("serankua", "Serankua, el que Ordenó la Sierra", "", "c", "C", "A", "lanzaastral", "gft",
     ["Tutusoma Blanco", "Vestidura de Algodón de la Sierra", "Lanza de los Cuatro Picos", "Guantes del Hilo", "Zapatillas Descalzas", "Fajín de los Pagamentos"],
     ("#a8a090", "#f4f0e6", "#ffffff"), ("ceramic", "white", "light")),
    ("aluna", "Aluna, la Madre del Pensamiento", "ancestral", "c", "D", "A", "espadaastral", "gfa",
     ["Corona del Primer Pensamiento", "Vestidura del Agua Oscura", "Espada de lo Pensado", "Guantes del Mundo Antes del Mundo", "Zapatillas de la Laguna Sagrada", "Poporo de la Madre"],
     ("#0e2a4a", "#4a8ad0", "#d0f0ff"), ("silver", "navy", "silver")),
    ("murallas", "Las Murallas de Cartagena", "", "f", "C", "S", "espadaastral", "sgf",
     ["Yelmo del Baluarte", "Coraza de Coral y Cal", "Espada de la Puerta del Reloj", "Escudo de San Felipe", "Guantes del Cañonero", "Pezuñas de la Garita"],
     ("#7a5a3a", "#e8c890", "#fff4d8"), ("iron", "tan", "dark")),
    ("tilopa", "Tilopa a Orillas del Ganges", "legendario", "l", "C", "A", "lanzaastral", "gft",
     ["Moño del Mendigo Sabio", "Vestidura de Harapos de Luz", "Lanza del Pescador del Río", "Guantes del Molino de Sésamo", "Zapatillas de la Orilla", "Fajín de las Seis Palabras"],
     ("#8a6a3a", "#f0d080", "#fffae0"), ("gold", "tan", "gold")),
    ("chiminigagua", "Chiminigagua, la Luz Encerrada", "mitico", "l", "D", "A", "arcoastral", "agft",
     ["Corona del Primer Resplandor", "Vestidura de la Oscuridad Abierta", "Arco de las Aves Negras", "Joya que Guardaba la Luz", "Guantes del Aire Brillante", "Zapatillas del Amanecer del Mundo", "Fajín de las Aves de Luz"],
     ("#0e0e1e", "#ffe070", "#ffffff"), ("gold", "black", "gold")),
    ("nencatacoa", "Nencatacoa, el Oso de los Tejedores", "", "f", "C", "L", "sableluna", "gft",
     ["Yelmo de Piel de Oso", "Manto Pintado a Mano", "Sable del Telar", "Brazales del Pintor", "Zapatos de la Chicha", "Cordón de Mil Hilos"],
     ("#5a3a1a", "#d07a3a", "#ffd0a0"), ("bronze", "walnut", "medium")),
    ("marpa", "Marpa el Traductor", "ancestral", "c", "D", "A", "espadaastral", "gft",
     ["Gorro del Granjero de Lhodrak", "Vestidura del Viajero a la India", "Espada de la Palabra Traducida", "Guantes del Oro Ofrecido", "Zapatillas de los Tres Viajes", "Fajín de la Torre de Nueve Pisos"],
     ("#3a4a7a", "#c8d0e8", "#ffffff"), ("silver", "blue", "silver")),
    ("zaque", "El Zaque de Hunza", "", "f", "D", "S", "mangualsombra", "sgf",
     ["Corona del Zaque", "Coraza de Hunza", "Mangual de la Guerra con el Zipa", "Escudo del Cercado", "Guantes del Tributo", "Pezuñas de la Plaza"],
     ("#6a2a0a", "#e0802a", "#ffd090"), ("gold", "red", "gold")),
    ("zipa", "El Zipa de Bacatá", "legendario", "c", "C", "S", "espadaastral", "sgf",
     ["Corona del Zipa", "Coraza de Mantas Finas", "Espada de Bacatá", "Escudo de la Sabana", "Guantes de Esmeralda", "Pezuñas del Cercado Real"],
     ("#1e4a3a", "#4ac08a", "#e0ffd0"), ("gold", "teal", "gold")),
    ("cauca", "El Cañón del Cauca", "", "p", "C", "S", "varasombra", "gft",
     ["Yelmo de la Garganta", "Coraza del Desfiladero", "Vara del Río Bravo", "Guantes de Roca", "Pezuñas del Puente Colgante", "Cinto del Arriero del Cañón"],
     ("#4a3a2a", "#8a7a4a", "#d8c890"), ("bronze", "brown", "dark")),
    ("yeshe", "Yeshe Tsogyal, Reina del Lago de Sabiduría", "ancestral", "f", "C", "A", "espadaastral", "gfa",
     ["Corona de la Dakini", "Vestidura de Hueso y Seda", "Espada que Guarda los Tesoros", "Guantes de la Escritura Escondida", "Zapatillas del Lago", "Espejo de la Reina"],
     ("#8a1a3a", "#e05a7a", "#ffd0e0"), ("gold", "maroon", "gold")),
    ("orinoco", "Los Raudales del Orinoco", "", "c", "D", "L", "tridenteluna", "gft",
     ["Yelmo del Raudal", "Manto de las Piedras Pintadas", "Tridente de la Corriente", "Brazales del Remolino", "Zapatos de la Laja", "Cordón del Bongo"],
     ("#2a3a4a", "#5a9ac8", "#d0f0ff"), ("silver", "blue", "medium")),
    ("machig", "Machig Labdrön, el Corte", "legendario", "c", "D", "A", "lanzaastral", "gft",
     ["Corona de la Yoguini", "Vestidura del Cementerio", "Lanza del Cuerpo Ofrecido", "Guantes del Tambor de Damaru", "Zapatillas de los Lugares Temibles", "Fajín de la Trompeta de Hueso"],
     ("#2a2a3a", "#e8e0d8", "#ffffff"), ("ceramic", "lavender", "light")),
    ("calima", "El Oro Calima", "", "l", "C", "A", "arcoastral", "gft",
     ["Máscara del Hombre Pájaro", "Vestidura de los Alfareros", "Arco del Lago Calima", "Guantes de Oro Martillado", "Zapatillas del Valle", "Fajín de las Narigueras"],
     ("#7a5a1a", "#e8b040", "#fff4c0"), ("gold", "tan", "gold")),
    ("barnizpasto", "El Barniz de Pasto", "", "p", "D", "L", "sableluna", "gft",
     ["Yelmo del Mopa-Mopa", "Manto Barnizado", "Sable del Galeras", "Brazales de Colores", "Zapatos del Carnaval", "Cordón de los Negros y Blancos"],
     ("#3a1a4a", "#e04ac0", "#ffd0f0"), ("copper", "purple", "red")),
    ("medicina", "El Buda de la Medicina", "mitico", "c", "C", "A", "espadaastral", "sgfa",
     ["Corona de Lapislázuli", "Vestidura Azul Profundo", "Espada del Mirobálano", "Cuenco de las Medicinas", "Guantes del que Cura", "Zapatillas de la Tierra Pura del Este", "Amuleto de los Doce Votos"],
     ("#0e2a8a", "#3a6ae0", "#c0d8ff"), ("gold", "blue", "gold")),
    ("gampopa", "El Ornamento de Gampopa", "ancestral", "l", "D", "A", "lanzaastral", "gft",
     ["Gorro del Médico de Dakpo", "Vestidura del Monje", "Lanza de la Joya Preciosa", "Guantes del Que Une los Dos Ríos", "Zapatillas del Monasterio", "Fajín del Ornamento"],
     ("#c8a030", "#f0e0a0", "#ffffff"), ("gold", "yellow", "light")),
    ("sanandres", "El Mar de los Siete Colores", "", "c", "C", "L", "tridenteluna", "gft",
     ["Sombrero de Palma del Raizal", "Manto de los Siete Azules", "Tridente del Arrecife", "Brazales de Caracola", "Zapatos de Arena Blanca", "Cordón de la Hoyada"],
     ("#0e5a7a", "#3ad0e0", "#e0ffff"), ("silver", "sky", "light")),
    ("coronanegra", "La Corona Negra", "legendario", "f", "D", "S", "espadaastral", "sgf",
     ["Corona Negra de las Dakinis", "Coraza del Que Vuelve", "Espada de las Diecisiete Vidas", "Escudo del Linaje", "Guantes del Gran Sello", "Pezuñas de Tsurphu"],
     ("#0e0e12", "#d8a030", "#ffe8a0"), ("gold", "black", "dark")),
    ("malpelo", "La Roca de Malpelo", "", "c", "D", "S", "mangualsombra", "sgf",
     ["Yelmo del Acantilado", "Coraza de Roca Desnuda", "Mangual del Tiburón Martillo", "Escudo de la Isla Sola", "Guantes del Buzo", "Pezuñas de Basalto"],
     ("#1a2a3a", "#6a8aa8", "#d0e8ff"), ("iron", "navy", "iron")),
    ("nagarjuna", "Nagarjuna, la Vía del Medio", "ancestral", "l", "C", "A", "espadaastral", "gfa",
     ["Corona de las Siete Serpientes", "Vestidura del Vacío", "Espada de las Dos Verdades", "Guantes del Argumento", "Zapatillas de Nalanda", "Sello de los Nagas"],
     ("#2a5a5a", "#80e0d0", "#ffffff"), ("silver", "teal", "silver")),
    ("selva", "La Selva sin Orillas", "", "p", "D", "L", "arcoluna", "gft",
     ["Corona de Hojas de Platanillo", "Manto de la Lluvia Verde", "Arco de la Cerbatana", "Brazales de Liana", "Zapatos del Igapó", "Cordón de Semillas"],
     ("#1a4a1a", "#4ab03a", "#d0ffb0"), ("bronze", "forest", "medium")),
    ("vajrasattva", "Vajrasattva, el Espejo Limpio", "legendario", "c", "C", "A", "espadaastral", "sgf",
     ["Corona Blanca de Cien Sílabas", "Vestidura de Cristal", "Vajra de la Pureza", "Campana del Espejo", "Guantes del Rocío", "Zapatillas del Loto Blanco"],
     ("#d8e0ec", "#ffffff", "#e0f0ff"), ("silver", "white", "silver")),
    ("llorona", "El Lamento de la Llorona", "", "c", "D", "S", "varasombra", "gft",
     ["Velo de Lágrimas", "Coraza del Río de Noche", "Vara del Llanto", "Guantes Mojados", "Pezuñas de la Orilla", "Cinto de los Hijos Perdidos"],
     ("#2a2a3a", "#a8b8d0", "#ffffff"), ("silver", "lavender", "iron")),
    ("shantideva", "Shantideva, la Entrada en el Camino", "ancestral", "l", "D", "A", "lanzaastral", "gft",
     ["Gorro del Que Parecía Dormir", "Vestidura de Nalanda", "Lanza de la Paciencia", "Guantes de las Seis Perfecciones", "Zapatillas del Que se Elevó", "Fajín del Intercambio"],
     ("#8a6a1a", "#f0c860", "#fff8e0"), ("gold", "yellow", "gold")),
    ("mulatrespatas", "La Mula de Tres Patas", "", "f", "C", "S", "mangualsombra", "gft",
     ["Yelmo de Herradura", "Coraza de las Chispas", "Mangual del Galope Cojo", "Guantes de Herrero", "Pezuñas que Echan Fuego", "Cinto del Camino Real"],
     ("#2a1a14", "#e0401a", "#ffb060"), ("iron", "black", "red")),
    ("vajrayogini", "Vajrayogini, la Danzante Roja", "mitico", "f", "C", "A", "espadaastral", "sgft",
     ["Corona de Cinco Calaveras Secas", "Vestidura Roja de la Danza", "Cuchillo Curvo de la Dakini", "Cráneo Lleno de Néctar", "Guantes del Khatvanga", "Zapatillas sobre el Cadáver", "Fajín de Huesos Tallados"],
     ("#8a0e1a", "#ff3a2a", "#ffc0a0"), ("gold", "red", "red")),
    ("mahakala", "Mahakala, el Gran Protector", "legendario", "f", "D", "S", "mangualsombra", "sgf",
     ["Corona de Llamas Negras", "Coraza del Protector", "Mangual de la Ira Sabia", "Escudo del Dharma", "Guantes del Lazo", "Pezuñas del Cementerio"],
     ("#0e0e1a", "#3a5ad0", "#ff8a2a"), ("iron", "navy", "dark")),
    ("sayona", "La Sayona", "", "p", "C", "L", "sableluna", "gft",
     ["Velo de Viuda", "Manto Blanco del Camino", "Sable de la Venganza", "Brazales de la Noche Llanera", "Zapatos que no Suenan", "Cordón del Hombre Infiel"],
     ("#3a3a3a", "#f0f0f0", "#ffffff"), ("silver", "white", "iron")),
    ("amitabha", "Amitabha, la Luz Infinita", "mitico", "l", "C", "A", "arcoastral", "rgfa",
     ["Corona del Ocaso", "Vestidura Roja del Oeste", "Arco de la Luz sin Medida", "Anillo del Loto Rojo", "Guantes del Cuenco", "Zapatillas de la Tierra Pura", "Amuleto de las Cuarenta y Ocho Promesas"],
     ("#a01a1a", "#ff7a3a", "#fff0c0"), ("gold", "red", "gold")),
    ("prajna", "La Madre de los Budas", "legendario", "c", "D", "A", "espadaastral", "gfa",
     ["Corona del Más Allá", "Vestidura Dorada de la Perfección", "Espada del Sutra", "Guantes del Libro", "Zapatillas de la Otra Orilla", "Amuleto del Corazón del Sutra"],
     ("#c8a020", "#ffe080", "#ffffff"), ("gold", "yellow", "gold")),
    ("bardo", "El Bardo, el Entre-dos", "ancestral", "c", "D", "S", "varasombra", "gft",
     ["Yelmo de las Cuarenta y Nueve Noches", "Coraza de las Visiones", "Vara de la Luz que Llama", "Guantes del Viento Kármico", "Pezuñas del Paso", "Cinto del Renacer"],
     ("#1a1a3a", "#8a8ae0", "#e0e0ff"), ("silver", "purple", "silver")),
    ("samantabhadra", "Samantabhadra, el Buda Primordial", "mitico", "l", "D", "A", "espadaastral", "sgfa",
     ["Corona del Cielo Desnudo", "Vestidura del Azul sin Fondo", "Espada del Que Nunca se Movió", "Espejo de la Base", "Guantes de la Unión", "Zapatillas de la Primera Liberación", "Amuleto de la Plegaria de las Aspiraciones"],
     ("#0e1a5a", "#4a7ae8", "#ffffff"), ("gold", "navy", "gold")),
    ("cincobudas", "Los Cinco Budas", "mitico", "f", "C", "A", "espadaastral", "sgfta",
     ["Corona de las Cinco Familias", "Vestidura de los Cinco Colores", "Espada de las Cinco Sabidurías", "Escudo de los Cinco Puntos", "Guantes de los Cinco Gestos", "Zapatillas de las Cinco Direcciones", "Fajín de los Cinco Elementos", "Amuleto de las Cinco Joyas"],
     ("#a01a24", "#3ac08a", "#f0e040"), ("gold", "blue", "gold")),
    ("ruedadharma", "La Rueda del Dharma", "mitico", "l", "C", "A", "espadaastral", "sgfta",
     ["Corona de los Ocho Radios", "Vestidura del Primer Sermón", "Espada del Parque de los Ciervos", "Escudo de la Rueda", "Guantes del Que Gira", "Zapatillas del Noble Camino", "Fajín de las Cuatro Verdades", "Amuleto de los Dos Ciervos"],
     ("#c8a020", "#ffffff", "#ffe070"), ("gold", "white", "gold")),
]


def r10(v):
    return int(round(v / 10.0) * 10) if v >= 100 else int(round(v))


def slot_props(code, L, m, elem, listen, k):
    e, res = ELEM[elem]
    lv = LISTEN[listen]
    crit = min(20, 16 + (L - 200) // 50)
    dodge = min(21, 17 + (L - 200) // 50)
    if code == "h": return {"armorPct": r10(2.55 * L * m), "life": r10(1.7 * L * m), res: 50}
    if code == "b": return {"armorPct": r10(2.8 * L * m), "life": r10(2.5 * L * m), "resAll": 50}
    if code == "w": return {"dmgPct": r10(4 * L * m), e: r10(1.15 * L * m), "crit": crit, lv: r10(0.55 * L * m)}
    if code == "s": return {"armorPct": r10(2.55 * L * m), "block": 19, "resAll": 45}
    if code == "g": return {"armorPct": r10(2.15 * L * m), "dex": r10(0.3 * L * m)}
    if code == "f": return {"armorPct": r10(2.15 * L * m), "dodge": dodge}
    if code == "t": return {"life": r10(1.7 * L * m), "potion": 60}
    if code in "ar": return {"allStats": r10(0.16 * L * m), "resAll": 35}
    raise ValueError(code)


# one extra per piece, picked by slot and the set's place in the list, so neighbours differ
EXTRAS = {
    "h": ["hintCost", "mana", "allStats", "xp", "replayCost", "lifeRegen"],
    "b": ["allStats", "thorns", "ene", "mf", "lifeRegen", "vit"],
    "s": ["replayCost", "mana", "life", "thorns"],
    "g": ["leech", "manaLeech", "killHeal", "typoTol", "mf", "str"],
    "f": ["xp", "mf", "lifeRegen", "killHeal"],
    "t": ["mf", "mana", "leech", "str", "manaLeech"],
    "a": ["mf", "xp", "lifeRegen", "mana"],
    "r": ["mf", "xp", "leech"],
}


def extra(key, L, m):
    fixed = {"hintCost": 50, "replayCost": 45, "typoTol": 1, "leech": min(12, 9 + (L - 200) // 70), "manaLeech": min(12, 9 + (L - 200) // 70)}
    if key in fixed: return fixed[key]
    per = {"mana": 0.8, "allStats": 0.19, "xp": 0.11, "thorns": 1.1, "lifeRegen": 0.12, "killHeal": 0.3, "mf": 0.6, "ene": 0.2, "vit": 0.2, "str": 0.2, "life": 1.7}[key]
    return r10(per * L * (1 if key == "xp" else m))


def js(v):
    if v is True: return "true"
    return str(v)


def obj(d):
    return "{" + ", ".join(f"{k}: {js(v)}" for k, v in d.items()) + "}"


def main():
    data_p = os.path.join(ROOT, "public", "rpg", "data.js")
    data = open(data_p, encoding="utf-8").read()
    if 'id: "teyuna"' in data:
        raise SystemExit("already there")
    n = len(SETS)
    lines = ["  // levels 204-400 (2026-11-27, scripts/new_sets_400.py): Colombian places and legends, and the Buddhist lineages"]
    for i, (sid, name, tier, elem, listen, kit, weapon, slots, names, neck, lpc) in enumerate(SETS):
        L = round(204 + i * (400 - 204) / (n - 1))
        m = TIER[tier]
        codes = "hbw" + slots
        assert len(codes) == len(names), sid
        pieces = []
        for k, (code, pname) in enumerate(zip(codes, names)):
            base = weapon if code == "w" else JEWEL[code] if code in "ar" else KIT[kit][code]
            props = slot_props(code, L, m, elem, listen, k)
            if code != "w":
                key = EXTRAS[code][(i + k) % len(EXTRAS[code])]
                props[key] = props.get(key, 0) + extra(key, L, m) if key not in ("hintCost", "replayCost", "typoTol") else extra(key, L, m)
            pieces.append(f'{{name: "{pname}", base: "{base}", props: {obj(props)}}}')
        e, res = ELEM[elem]
        lv = LISTEN[listen]
        cs = min(13, 9 + (L - 200) // 50)
        last = {"nearExact": True, "comboKeep": True, "allStats": r10(0.3 * L * m), "xp": min(45, 33 + (L - 200) // 18)}
        if tier == "mitico":
            last["mf"] = r10(0.6 * L)
        bonus = {2: {res: 45, "life": r10(1.5 * L * m)}, 3: {lv: r10(0.55 * L * m), e: r10(1.0 * L * m)}, 4: {"replayCost": 55, "slowFree": True}}
        P = len(codes)
        if P == 5:
            bonus[5] = {"freeReplay": 1, "comboStart": cs, **last}
        else:
            bonus[5] = {"freeReplay": 1, "comboStart": cs}
            bonus[P] = last
            for extra_n in range(6, P):
                bonus[extra_n] = {"mf": r10(0.3 * L), "xp": 5}
        bonus = dict(sorted(bonus.items()))
        b = "{" + ", ".join(f"{k}: {obj(v)}" for k, v in bonus.items()) + "}"
        t = f'tier: "{tier}", ' if tier else ""
        lines.append(f'  {{id: "{sid}", {t}name: "{name}", pieces: [{", ".join(pieces)}], bonus: {b}, lvl: {L}}},')
    # after the last set (the end of the SETS list)
    a = data.index("export const SETS")
    end = data.index("\n];", a)
    data = data[:end] + "\n" + "\n".join(lines) + data[end:]
    open(data_p, "w", encoding="utf-8").write(data)

    # colours: build_lpc.py SETS
    lpc_p = os.path.join(ROOT, "scripts", "build_lpc.py")
    s = open(lpc_p, encoding="utf-8").read()
    a = s.index("SETS = {  # each set has its own colours")
    end = s.index("\n}", a)
    add = "".join(f'\n    "{sid}": {{"metal": "{lpc[0]}", "cloth": "{lpc[1]}", "wood": "{lpc[2]}"}},' for sid, *_, lpc in SETS)
    s = s[:end] + add + s[end:]
    open(lpc_p, "w", encoding="utf-8").write(s)

    # shirts: build_scenes.py NECKLACES and NECK_ORDER (by tier, each tier by level)
    sc_p = os.path.join(ROOT, "scripts", "build_scenes.py")
    s = open(sc_p, encoding="utf-8").read()
    a = s.index("NECKLACES = {")
    end = s.index("\n}", a)
    add = "".join(f'\n    "{sid}": ("{neck[0]}", "{neck[1]}", "{neck[2]}"),' for sid, *_, neck, lpc in SETS)
    s = s[:end] + add + s[end:]
    m = re.search(r"NECK_ORDER = \[(.*?)\]\n", s, re.S)
    order = re.findall(r'"(\w+)"', m.group(1))
    by_tier = {t: [x[0] for x in SETS if x[2] == t] for t in TIER}
    # insert each tier's new sets after the last old set of that tier
    tiers_old = {"": "canocristales", "ancestral": "huitaca", "legendario": "sombreron", "mitico": "dzogchen"}
    for t, after in tiers_old.items():
        j = order.index(after) + 1
        order[j:j] = by_tier[t]
    new = "NECK_ORDER = [" + ",\n              ".join(", ".join(f'"{x}"' for x in order[k:k + 12]) for k in range(0, len(order), 12)) + "]\n"
    s = s[:m.start()] + new + s[m.end():]
    open(sc_p, "w", encoding="utf-8").write(s)
    print(f"{n} sets, levels 204-400")


if __name__ == "__main__":
    main()
