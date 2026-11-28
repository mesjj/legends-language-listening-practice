"""One-off (2026-11-27): 66 more monsters (10 per zone, 16 for easy mode) and 18 more bosses (three more per
zone), written into public/rpg/data.js. Their art: scripts/build_monsters.py and scripts/build_bosses_more.py.
usage: python3 scripts/new_foes.py   (refuses if they're already there)
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# zone: [(id, name, icon, color, hp, dmg, extra, res)]
MON = {
    "paramo": [
        ("ventisca", "Ventisca viva", "ghost", "#d8ecff", 0.8, 1.0, {"el": "cold"}, {"cold": 100, "fire": -75}),
        ("curi", "Curí de la escarcha", "rat", "#c8b8a0", 0.7, 0.9, {}, {"cold": 50}),
        ("aguila", "Águila del páramo", "vulture", "#8a7a68", 0.8, 1.2, {}, {"light": -50}),
        ("frailejonero", "Guardián del frailejón", "evil-tree", "#b8c098", 1.6, 0.8, {}, {"poison": 50, "fire": -75}),
        ("lagartija", "Lagartija de hielo", "snake", "#a0d0e0", 0.9, 1.0, {"el": "cold"}, {"cold": 75, "fire": -50}),
        ("pastorhelado", "Pastor helado", "shambling-zombie", "#b0c0d0", 1.3, 1.0, {"el": "cold"}, {"cold": 100, "poison": 100, "fire": -50}),
        ("venadoespectral", "Venado espectral", "ghost", "#c8d8e8", 1.0, 1.1, {}, {"cold": 50, "light": -50}),
        ("piedrarueda", "Piedra que rueda", "rock-golem", "#8a8a8a", 2.0, 0.9, {}, {"poison": 100, "cold": 25, "light": 25}),
        ("barbamusgo", "Barbas de musgo", "slime", "#7a9a5a", 1.3, 0.8, {"el": "poison"}, {"poison": 75, "fire": -75}),
        ("colibrihelado", "Colibrí de escarcha", "raven", "#80d0e0", 0.5, 1.1, {}, {"cold": 50, "light": -25}),
    ],
    "cienaga": [
        ("bocachico", "Bocachico mordedor", "frog", "#a0a8a0", 0.8, 1.1, {}, {"cold": 25, "light": -50}),
        ("garzanegra", "Garza negra", "vulture", "#3a3a40", 0.8, 1.1, {}, {"poison": 25, "light": -25}),
        ("anguila", "Anguila eléctrica", "snake", "#5a6a5a", 1.0, 1.3, {"el": "light"}, {"light": 100, "cold": -25}),
        ("tortugamordedora", "Tortuga mordedora", "croc-jaws", "#5a5a3a", 1.8, 1.0, {}, {"poison": 50, "fire": 25, "cold": -50}),
        ("zancudos", "Nube de zancudos", "wasp-sting", "#5a4a4a", 0.6, 0.9, {"vamp": True}, {"poison": 75, "fire": -75}),
        ("raya", "Raya de río", "frog", "#8a7a5a", 1.0, 1.2, {"el": "poison"}, {"poison": 75, "light": -50}),
        ("ranatoro", "Rana toro", "frog", "#6a8a3a", 1.4, 1.0, {}, {"poison": 50, "cold": -50}),
        ("hombrelodo", "Hombre de lodo", "slime", "#6a5038", 1.7, 1.0, {}, {"poison": 100, "cold": -25, "fire": -25}),
        ("chiguirorabioso", "Chigüiro rabioso", "boar", "#8a6040", 1.2, 1.1, {}, {"poison": 25, "cold": -25}),
        ("liriocarnivoro", "Lirio carnívoro", "evil-tree", "#c070a0", 1.1, 1.1, {"el": "poison"}, {"poison": 100, "fire": -75}),
    ],
    "selva": [
        ("jaguarsombra", "Jaguar de sombra", "wolf-head", "#3a3440", 1.3, 1.4, {}, {"cold": 25, "light": -50}),
        ("conga", "Hormiga conga", "wasp-sting", "#2a1e18", 0.7, 1.3, {"el": "poison"}, {"poison": 100, "fire": -50}),
        ("tarantula", "Tarántula pollera", "hanging-spider", "#6a4a3a", 1.0, 1.1, {"el": "poison"}, {"poison": 100, "fire": -50}),
        ("escorpion", "Escorpión negro", "centipede", "#2a2428", 0.9, 1.3, {"el": "poison"}, {"poison": 100, "cold": -50}),
        ("boa", "Boa constrictora", "cobra", "#8a7a4a", 1.6, 1.1, {}, {"poison": 50, "cold": -50}),
        ("maicero", "Mono maicero", "goblin", "#6a5038", 0.9, 1.0, {}, {"poison": 25, "light": -25}),
        ("ranaveneno", "Rana venenosa", "frog", "#e0c020", 0.6, 1.3, {"el": "poison"}, {"poison": 100, "fire": -50}),
        ("guacharaca", "Guacharaca furiosa", "raven", "#8a6a4a", 0.7, 1.0, {}, {"light": -50}),
        ("liana", "Liana estranguladora", "evil-tree", "#4a7a3a", 1.5, 0.9, {}, {"poison": 75, "fire": -100}),
        ("chamanperdido", "Chamán perdido", "hooded-figure", "#7a5a8a", 1.1, 1.2, {"el": "poison"}, {"poison": 75, "light": -25}),
    ],
    "llano": [
        ("torocandela", "Toro de candela", "charging-bull", "#a03a1a", 1.6, 1.4, {"el": "fire"}, {"fire": 100, "cold": -50}),
        ("garrapata", "Garrapata gigante", "centipede", "#6a3a3a", 0.8, 0.9, {"vamp": True}, {"poison": 50, "fire": -50}),
        ("cimarron", "Caballo cimarrón", "charging-bull", "#6a4a30", 1.3, 1.2, {}, {"poison": 25, "light": -25}),
        ("halconfuego", "Halcón de fuego", "vulture", "#d06a2a", 0.8, 1.3, {"el": "fire"}, {"fire": 100, "cold": -50}),
        ("espantosabana", "Espanto de la sabana", "ghost", "#d8c8a0", 1.0, 1.2, {"el": "cold"}, {"cold": 100, "poison": 100, "light": -50}),
        ("iguanafuego", "Iguana de fuego", "snake", "#c0501a", 1.1, 1.2, {"el": "fire"}, {"fire": 100, "cold": -75}),
        ("remolino", "Remolino de polvo", "ghost", "#c8a870", 1.0, 1.1, {}, {"poison": 100, "light": 50, "cold": -25}),
        ("coplero", "Coplero maldito", "shambling-zombie", "#8a6a8a", 1.2, 1.1, {"el": "light"}, {"light": 75, "poison": -25}),
        ("armadillobrasa", "Armadillo de brasa", "boar", "#8a4a2a", 1.8, 1.0, {"el": "fire"}, {"fire": 100, "cold": -50}),
        ("cascabel", "Serpiente cascabel", "cobra", "#a08a5a", 0.9, 1.4, {"el": "poison"}, {"poison": 100, "cold": -50}),
    ],
    "ruinas": [
        ("gargola", "Gárgola de piedra", "evil-bat", "#7a7a80", 1.6, 1.1, {}, {"poison": 100, "light": 25, "cold": -25}),
        ("calavera", "Calavera rodante", "skeleton", "#e0d8c0", 0.8, 1.2, {}, {"poison": 100, "cold": 50, "light": -50}),
        ("idolo", "Ídolo vivo", "rock-golem", "#9a8a6a", 2.0, 1.0, {}, {"poison": 100, "fire": 25, "light": -25}),
        ("tunjomaldito", "Tunjo maldito", "imp", "#d0a030", 1.0, 1.3, {"el": "light"}, {"light": 100, "poison": 100, "cold": -50}),
        ("sacerdotehueso", "Sacerdote de hueso", "skeleton", "#c8c0a8", 1.1, 1.3, {"el": "cold"}, {"poison": 100, "cold": 75, "fire": -50}),
        ("serpientepiedra", "Serpiente de piedra", "cobra", "#8a8478", 1.5, 1.1, {}, {"poison": 100, "cold": 25, "light": -25}),
        ("aranatumba", "Araña de las tumbas", "hanging-spider", "#4a4450", 1.0, 1.2, {"el": "poison"}, {"poison": 100, "fire": -50}),
        ("guerreroespectro", "Guerrero espectral", "shambling-zombie", "#8ab0c0", 1.3, 1.3, {"el": "cold"}, {"cold": 100, "poison": 100, "light": -50}),
        ("ratatumba", "Rata de las tumbas", "rat", "#6a6058", 0.7, 1.0, {"vamp": True}, {"poison": 75, "fire": -25}),
        ("ojocripta", "Ojo de la cripta", "ghost", "#b04a6a", 0.9, 1.3, {"el": "light"}, {"light": 75, "poison": 50, "fire": -50}),
    ],
}
EASY = {
    "paramo": ["mariquita", "polilla", "pajarito"],
    "cienaga": ["caracol", "cangrejito", "pececito"],
    "selva": ["gusanito", "abejita", "hongo"],
    "llano": ["grillo", "lagartijita", "pollito"],
    "ruinas": ["ratoncito", "erizo", "hormiguita", "tortuguita"],
}
EASY_DEF = {
    "mariquita": ("Mariquita", "wasp-sting", "#e04030", 0.5, 0.5),
    "polilla": ("Polilla", "wasp-sting", "#c8b898", 0.45, 0.6),
    "pajarito": ("Pajarito", "raven", "#d8a050", 0.5, 0.6),
    "caracol": ("Caracol", "slime", "#c09060", 0.7, 0.45),
    "cangrejito": ("Cangrejito", "frog", "#e07040", 0.6, 0.6),
    "pececito": ("Pececito", "frog", "#f0a030", 0.5, 0.55),
    "gusanito": ("Gusanito", "leeching-worm", "#a0c060", 0.55, 0.5),
    "abejita": ("Abejita", "wasp-sting", "#f0c030", 0.45, 0.65),
    "hongo": ("Hongo saltarín", "slime", "#d04a3a", 0.65, 0.5),
    "grillo": ("Grillo", "centipede", "#6a8a3a", 0.5, 0.6),
    "lagartijita": ("Lagartijita", "snake", "#80b050", 0.55, 0.6),
    "pollito": ("Pollito", "raven", "#f8e060", 0.45, 0.5),
    "ratoncito": ("Ratoncito", "rat", "#a09080", 0.5, 0.55),
    "erizo": ("Erizo", "boar", "#8a7060", 0.7, 0.5),
    "hormiguita": ("Hormiguita", "wasp-sting", "#5a2a20", 0.45, 0.6),
    "tortuguita": ("Tortuguita", "frog", "#6a9a5a", 0.8, 0.4),
}
B = '''  // three more per zone (2026-11-27, scripts/new_foes.py; art: scripts/build_bosses_more.py)
  venadonegro: { name: "El Venado Negro", title: "El de los ojos de candela", icon: "charging-bull", color: "#ff6a4a", hp: 1.2, dmg: 1.05, el: "cold", mods: ["veloz"], minions: "venadoespectral",
                intro: "Un venado negro en la niebla, quieto, mirándote. Los cazadores que lo siguieron no volvieron.",
                special: { name: "La cornada", every: 5, mult: 2.4,
                  ready: "El Venado Negro baja la cornamenta. <b>Solo una frase perfecta</b> te aparta.",
                  hit: "La cornada te levanta del suelo.", dodge: "Pasa a tu lado como una sombra y se pierde en la niebla." },
                p2: { step: 2, text: "Los ojos del Venado se encienden como brasas. Ahora embiste más a menudo." },
                last: "El Venado se deshace en niebla. Solo quedan dos brasas que se apagan." },
  condorhielo: { name: "El Cóndor de Hielo", title: "El que trae la helada", icon: "vulture", color: "#a0e8ff", hp: 1.3, dmg: 1.0, el: "cold", mods: ["murmullo"], minions: "colibrihelado",
                intro: "Cuando pasa por encima, se hiela el agua de las lagunas. Su sombra es fría.",
                special: { name: "La helada", every: 4, mult: 1.8, tangle: 2, heal: 0.06, bound: "El hielo no te deja", boundWarn: "Helado",
                  ready: "El Cóndor abre las alas y el aire se hiela. <b>Solo una frase perfecta</b> te deja moverte.",
                  hit: "El hielo te atrapa: <b>2 frases sin Despacio ni Pista</b>, y él se recupera.", dodge: "La escarcha cubre la piedra donde estabas." },
                p2: { summon: ["ventisca", 2], text: "El Cóndor bate las alas y se levanta la ventisca." },
                last: "El Cóndor cae despacio y se rompe como un témpano." },
  arrierofantasma: { name: "El Arriero Fantasma", title: "El que nunca llegó al pueblo", icon: "cloaked-figure-on-horseback", color: "#e8d8a0", hp: 1.25, dmg: 1.0, el: "cold", mods: ["ladron"], minions: "pastorhelado",
                intro: "Se oyen las mulas y el silbido del arriero, pero el camino está vacío. Cobra el paso.",
                special: { name: "El cobro", every: 4, mult: 1.8, steal: true,
                  ready: "El Arriero estira la mano: quiere su paga. <b>Solo una frase perfecta</b> te deja pasar sin pagar.",
                  hit: "Te cobra el paso", dodge: "Pasas de largo y su mano se cierra en la niebla." },
                p2: { every: 3, text: "El Arriero hace sonar el zurriago. Las mulas fantasma te rodean." },
                last: "El Arriero se quita el sombrero, por fin llegó. Se va camino abajo." },
  mohana:     { name: "La Mohana", title: "La que peina su pelo en el río", icon: "floating-ghost", color: "#7ae8c8", hp: 1.4, dmg: 1.0, el: "cold", mods: ["eco", "regenera"], minions: "bocachico",
                intro: "Una mujer peinándose sentada en una piedra del río. El pelo le llega al agua, y sigue bajando.",
                special: { name: "El pelo", every: 4, mult: 1.7, tangle: 2, heal: 0.08, bound: "Su pelo no te deja", boundWarn: "Enredado",
                  ready: "El pelo de la Mohana se mueve en el agua hacia ti. <b>Solo una frase perfecta</b> te deja salir.",
                  hit: "El pelo te enreda: <b>2 frases sin Despacio ni Pista</b>, y ella se cura.", dodge: "El pelo se cierra sobre el agua vacía." },
                p2: { summon: ["anguila", 2], text: "La Mohana se mete al río. El agua se llena de anguilas." },
                last: "La Mohana se hunde con su peine de oro. El río se queda quieto." },
  bufeoencantado: { name: "El Bufeo Encantado", title: "El que baila en las fiestas del río", icon: "ghost", color: "#ff9ab8", hp: 1.35, dmg: 1.05, el: "cold", mods: ["ladron", "veloz"], minions: "raya",
                intro: "Un hombre de sombrero blanco que baila mejor que nadie. Nunca se quita el sombrero.",
                special: { name: "El baile", every: 4, mult: 1.9, steal: true,
                  ready: "El Bufeo te saca a bailar. <b>Solo una frase perfecta</b> te deja decirle que no.",
                  hit: "Te lleva bailando", dodge: "Le dices que no. Se va a buscar otra pareja." },
                p2: { every: 3, text: "Se le cae el sombrero: debajo, un espiráculo. El Bufeo vuelve al agua." },
                last: "Un delfín rosado se aleja río abajo, y el sombrero blanco flota." },
  tarumama:   { name: "La Tarumama", title: "La vieja del río", icon: "hooded-figure", color: "#c8d88a", hp: 1.45, dmg: 1.05, el: "poison", mods: ["murmullo", "piedra"], minions: "hombrelodo",
                intro: "Una vieja con los pies al revés, en la orilla. Grita para que los niños no se acerquen al agua.",
                special: { name: "El grito del río", every: 4, mult: 2.1, wail: "grito",
                  ready: "La Tarumama toma aire. <b>Su grito sonará encima de la próxima frase</b>: solo una frase perfecta te protege.",
                  hit: "Su grito te tumba en el barro.", dodge: "Oyes la frase por debajo del grito." },
                p2: { summon: ["hombrelodo", 2], text: "La Tarumama golpea el barro y el barro se levanta." },
                last: "La Tarumama se mete al agua de espaldas, caminando hacia adelante." },
  pollomaligno: { name: "El Pollo Maligno", title: "El que se come a los perdidos", icon: "raven", color: "#ff5a2a", hp: 1.4, dmg: 1.15, el: "poison", mods: ["fuerte"], minions: "guacharaca",
                intro: "Un pollo enorme en la selva del Pacífico. Canta como un hombre perdido, y quien lo sigue, se pierde.",
                special: { name: "El picotazo", every: 4, mult: 2.6,
                  ready: "El Pollo Maligno levanta el pico. <b>Solo una frase perfecta</b> te aparta.",
                  hit: "El picotazo te tumba.", dodge: "El pico se clava en el barro donde estabas." },
                p2: { dmg: 1.3, text: "El Pollo Maligno se esponja: ahora es el doble de grande." },
                last: "El Pollo Maligno sale corriendo selva adentro, cacareando." },
  boraro:     { name: "El Boraro", title: "El de los pies al revés", icon: "ogre", color: "#ff8a4a", hp: 1.55, dmg: 1.1, el: "poison", mods: ["piedra", "vampirico"], minions: "jaguarsombra",
                intro: "Grande, peludo, con las orejas largas y los pies al revés. Sus huellas te llevan al lado contrario.",
                special: { name: "El abrazo", every: 4, mult: 1.8, tangle: 2, heal: 0.08, bound: "El Boraro no te suelta", boundWarn: "Apretado",
                  ready: "El Boraro abre los brazos. <b>Solo una frase perfecta</b> te libra.",
                  hit: "Te aprieta entre los brazos: <b>2 frases sin Despacio ni Pista</b>, y él se cura.", dodge: "Abraza un tronco: tú ya no estás." },
                p2: { summon: ["jaguarsombra", 2], text: "El Boraro silba. Los jaguares de sombra salen de la selva." },
                last: "El Boraro se va, y sus huellas dicen que viene." },
  hojarasquin: { name: "El Hojarasquín", title: "El guardián del monte", icon: "tree-face", color: "#a8e040", hp: 1.5, dmg: 1.05, el: "poison", mods: ["regenera", "eco"], minions: "liana",
                intro: "Un montón de hojas secas que se levanta y camina. Cuida el monte de quien lo daña.",
                special: { name: "La hojarasca", every: 4, mult: 1.8, steal: true,
                  ready: "El Hojarasquín sopla y las hojas se levantan. <b>Solo una frase perfecta</b> te deja ver.",
                  hit: "La hojarasca te tapa", dodge: "Las hojas caen. Sigues en tu sitio." },
                p2: { summon: ["liana", 2], text: "El monte entero se mueve con él." },
                last: "Las hojas caen al suelo, quietas. El monte vuelve a respirar." },
  mulatrespatas: { name: "La Mula de Tres Patas", title: "La que galopa echando chispas", icon: "charging-bull", color: "#ff7a1a", hp: 1.35, dmg: 1.2, el: "fire", mods: ["rapido"], minions: "torocandela",
                intro: "Se oye galopar en tres tiempos. Echa chispas por los cascos y fuego por los ojos.",
                special: { name: "El galope", every: 3, mult: 2.1, burn: 3,
                  ready: "La Mula escarba con su única pata delantera. <b>Solo una frase perfecta</b> te aparta.",
                  hit: "Te arrolla: <b>ardes</b> durante 3 turnos. Una frase perfecta apaga el fuego.", dodge: "Pasa a tu lado echando chispas." },
                p2: { every: 2, text: "La Mula echa fuego por la boca. Ya no para de galopar." },
                last: "La Mula se apaga como una brasa. Quedan tres huellas quemadas." },
  juanmachete: { name: "Juan Machete", title: "El que le vendió el alma al diablo", icon: "hooded-figure", color: "#ffd04a", hp: 1.45, dmg: 1.15, el: "fire", mods: ["ladron", "fuerte"], minions: "cimarron",
                intro: "Tenía el hato más grande del llano. Pagó por él con lo que no se paga, y ahora cobra a los demás.",
                special: { name: "El machete", every: 4, mult: 2.0, steal: true,
                  ready: "Juan Machete afila el machete en una piedra. <b>Solo una frase perfecta</b> te aparta.",
                  hit: "Te corta la bolsa", dodge: "El machete corta el aire." },
                p2: { summon: ["cimarron", 2], text: "Juan Machete silba: su ganado sale del monte." },
                last: "Juan Machete se hunde en la tierra con su oro. El llano queda en paz." },
  tigremariposo: { name: "El Tigre Mariposo", title: "El jaguar más grande del llano", icon: "wolf-head", color: "#ffb84a", hp: 1.5, dmg: 1.25, mods: ["veloz", "fuerte"], minions: "halconfuego",
                intro: "Las manchas le dan vueltas como alas de mariposa. Del morichal sale un rugido que hace temblar el agua.",
                special: { name: "El zarpazo", every: 4, mult: 2.5,
                  ready: "El Tigre se agazapa en el pasto. <b>Solo una frase perfecta</b> te aparta.",
                  hit: "El zarpazo te tumba.", dodge: "Salta por encima de ti y cae en el pasto." },
                p2: { step: 2, text: "El Tigre ruge. Las manchas le dan vueltas más rápido." },
                last: "El Tigre Mariposo se va despacio hacia el morichal." },
  poira:      { name: "El Poira", title: "El que enseña los conjuros", icon: "imp", color: "#c89aff", hp: 1.5, dmg: 1.15, el: "light", mods: ["maldito", "eco"], minions: "ojocripta",
                intro: "Pequeño, con un sombrero enorme y los pies al revés. Enseña conjuros a cambio de lo que más quieres.",
                special: { name: "El conjuro", every: 4, mult: 1.8, tangle: 2, heal: 0.08, bound: "El conjuro no te deja", boundWarn: "Embrujado",
                  ready: "El Poira murmura un conjuro. <b>Solo una frase perfecta</b> lo rompe.",
                  hit: "El conjuro te ata: <b>2 frases sin Despacio ni Pista</b>, y él se cura.", dodge: "El conjuro se deshace en el aire." },
                p2: { summon: ["ojocripta", 2], text: "El Poira se ríe. Se abren ojos en todas las piedras." },
                last: "El Poira se mete en el río y su sombrero sigue flotando." },
  duendemayor: { name: "El Duende Mayor", title: "El que esconde las cosas", icon: "goblin", color: "#9aff6a", hp: 1.45, dmg: 1.1, mods: ["ladron", "rapido"], minions: "ratatumba",
                intro: "Un duende viejo con sombrero de ala ancha. Tira piedras desde el tejado y esconde todo lo que pierdes.",
                special: { name: "Las piedras", every: 4, mult: 2.2,
                  ready: "El Duende junta piedras en el sombrero. <b>Solo una frase perfecta</b> te aparta.",
                  hit: "Te llueven piedras.", dodge: "Las piedras rebotan donde estabas." },
                p2: { every: 3, text: "El Duende se ríe y desaparece. Las piedras vienen de todas partes." },
                last: "El Duende se esconde en una grieta. Devuelve lo que no era suyo." },
  centinela:  { name: "El Centinela Dormido", title: "La estatua que despierta", icon: "rock-golem", color: "#e0c87a", hp: 1.8, dmg: 1.2, mods: ["piedra", "fuerte"], minions: "idolo",
                intro: "Una estatua de piedra con colmillos, tallada hace mil años. Abre los ojos cuando oye pasos.",
                special: { name: "El golpe de piedra", every: 5, mult: 2.8,
                  ready: "El Centinela levanta su maza de piedra. <b>Solo una frase perfecta</b> te aparta.",
                  hit: "El golpe hace temblar las ruinas.", dodge: "La maza parte la losa donde estabas." },
                p2: { dmg: 1.3, text: "Al Centinela se le cae la piedra de la cara. Debajo, otra cara más vieja." },
                last: "El Centinela cierra los ojos. Vuelve a dormir otros mil años." },
  chibchacum: { name: "Chibchacum", title: "El que inundó la sabana", icon: "ogre", color: "#5ac8ff", hp: 1.8, dmg: 1.25, el: "cold", mods: ["piedra", "regenera", "murmullo"], minions: "anguila",
                intro: "Castigó a los muiscas con el agua. Ahora carga la tierra en los hombros, y cuando se cansa, tiembla.",
                special: { name: "La inundación", every: 4, mult: 2, tangle: 2, heal: 0.08, bound: "El agua no te deja", boundWarn: "Inundado",
                  ready: "El agua sube hasta tus rodillas. <b>Solo una frase perfecta</b> te saca.",
                  hit: "El agua te arrastra: <b>2 frases sin Despacio ni Pista</b>, y él se cura.", dodge: "Saltas a una piedra y el agua pasa." },
                p2: { every: 3, text: "Chibchacum cambia la tierra de hombro. Todo tiembla." },
                last: "Chibchacum se queda quieto con la tierra a cuestas. El agua baja." },
  buziraco:   { name: "Buziraco", title: "El del cerro de la Popa", icon: "devil-mask", color: "#ff3a1a", hp: 1.85, dmg: 1.3, el: "fire", mods: ["fuerte", "veloz", "maldito"], minions: "diablillo",
                intro: "Un macho cabrío de fuego en lo alto del cerro. Lo echaron de allí hace siglos, y quiere volver.",
                special: { name: "El fuego del cerro", every: 4, mult: 2.3, burn: 3,
                  ready: "Buziraco agacha los cuernos y le arden. <b>Solo una frase perfecta</b> te aparta.",
                  hit: "La cornada de fuego te alcanza: <b>ardes</b> durante 3 turnos. Una frase perfecta apaga el fuego.", dodge: "El fuego pasa a tu lado y quema la hierba." },
                p2: { summon: ["diablillo", 2], text: "Buziraco bala y el cerro se abre. Salen diablillos." },
                last: "Buziraco cae rodando cerro abajo y se apaga en el mar." },
  madreespantos: { name: "La Madre de los Espantos", title: "La que los llama a todos", icon: "floating-ghost", color: "#e0a0ff", hp: 1.9, dmg: 1.3, el: "cold", mods: ["eco", "ladron", "regenera"], minions: "espanto",
                intro: "Todos los espantos tienen madre. Es alta como la noche, y los llama con un llanto que se oye en todo el abismo.",
                special: { name: "El llanto de todos", every: 3, mult: 2.1, wail: "llanto",
                  ready: "La Madre de los Espantos va a llorar. <b>Su llanto sonará encima de la próxima frase</b>: solo una frase perfecta te protege.",
                  hit: "Su llanto te hiela.", dodge: "Oyes la frase por encima del llanto." },
                p2: { summon: ["espantosabana", 2], every: 2, text: "La Madre abre los brazos. Sus hijos vienen de todos los rincones." },
                last: "La Madre de los Espantos se recoge en la oscuridad. Por fin, silencio." },
'''
NEW_BOSSES = {"paramo": ["venadonegro", "condorhielo", "arrierofantasma"], "cienaga": ["mohana", "bufeoencantado", "tarumama"],
              "selva": ["pollomaligno", "boraro", "hojarasquin"], "llano": ["mulatrespatas", "juanmachete", "tigremariposo"],
              "ruinas": ["poira", "duendemayor", "centinela"], "abismo": ["chibchacum", "buziraco", "madreespantos"]}
BOSS_RES = {"venadonegro": {"cold": 75, "fire": -50}, "condorhielo": {"cold": 100, "fire": -75}, "arrierofantasma": {"cold": 100, "poison": 100, "light": -50},
            "mohana": {"cold": 75, "poison": 50, "light": -50}, "bufeoencantado": {"cold": 50, "light": -50}, "tarumama": {"poison": 75, "fire": -50},
            "pollomaligno": {"poison": 75, "light": -50}, "boraro": {"poison": 75, "fire": -50}, "hojarasquin": {"poison": 100, "fire": -75},
            "mulatrespatas": {"fire": 100, "cold": -50}, "juanmachete": {"fire": 75, "light": -50}, "tigremariposo": {"poison": 25, "cold": -25},
            "poira": {"light": 100, "poison": 50, "fire": -50}, "duendemayor": {"light": -25, "poison": 25}, "centinela": {"poison": 100, "cold": 25, "light": -50},
            "chibchacum": {"cold": 100, "light": -50}, "buziraco": {"fire": 100, "poison": 50, "cold": -50}, "madreespantos": {"cold": 100, "poison": 100, "light": -50, "fire": -25}}


def js(v):
    return "true" if v is True else f'"{v}"' if isinstance(v, str) else str(v)


def obj(d):
    return "{ " + ", ".join(f"{k}: {js(v)}" for k, v in d.items()) + " }"


def main():
    p = os.path.join(ROOT, "public", "rpg", "data.js")
    s = open(p, encoding="utf-8").read()
    if "ventisca:" in s:
        raise SystemExit("already there")

    def ins_before(anchor_start, end_mark, text):
        nonlocal s
        i = s.index(anchor_start)
        j = s.index(end_mark, i)
        s = s[:j] + text + s[j:]

    lines = ["  // ten more per zone (2026-11-27, scripts/new_foes.py; drawn in scripts/build_monsters.py)"]
    for z, mons in MON.items():
        for mid, name, icon, col, hp, dmg, extra, res in mons:
            d = {"name": name, "icon": icon, "color": col, "hp": hp, "dmg": dmg, **extra}
            lines.append(f"  {mid}: {obj(d)},")
    ins_before("export const MONSTERS = {", "\n};", "\n" + "\n".join(lines))
    lines = ["  // more (2026-11-27)"] + [f'  {k}: {obj({"name": n, "icon": i, "color": c, "hp": hp, "dmg": dm})},' for k, (n, i, c, hp, dm) in EASY_DEF.items()]
    ins_before("export const EASY_MONSTERS = {", "\n};", "\n" + "\n".join(lines))
    for z, ids in EASY.items():
        a = f"  {z}: ["
        i = s.index(a, s.index("export const EASY_ROSTER"))
        j = s.index("]", i)
        s = s[:j] + ", " + ", ".join(f'"{x}"' for x in ids) + s[j:]
    # resistances
    res = [f"  {mid}: {obj(r)}," for z in MON.values() for mid, *_, r in z]
    res += [f"  {k}: {obj(v)}," for k, v in BOSS_RES.items()]
    res += ["  mariquita: { poison: 50 },", "  caracol: { poison: 75, fire: -50 },", "  hongo: { poison: 100, fire: -50 },", "  erizo: { poison: 25 },"]
    ins_before("export const MONSTER_RES = {", "\n};", "\n  // 2026-11-27\n" + "\n".join(res))
    # bosses
    ins_before("export const BOSSES = {", "\n};", "\n" + B.rstrip("\n"))
    # zones: monsters and bosses
    for z, mons in MON.items():
        i = s.index(f'{{ id: "{z}",', s.index("export const ZONES"))
        a = s.index("monsters: [", i)
        b = s.index("]", a)
        s = s[:b] + ", " + ", ".join(f'"{m[0]}"' for m in mons) + s[b:]
    for z, ids in NEW_BOSSES.items():
        i = s.index(f'{{ id: "{z}",', s.index("export const ZONES"))
        a = s.index("bosses: [", i)
        b = s.index("]", a)
        s = s[:b] + ", " + ", ".join(f'"{x}"' for x in ids) + s[b:]
    open(p, "w", encoding="utf-8").write(s)
    print("ok")


if __name__ == "__main__":
    main()
