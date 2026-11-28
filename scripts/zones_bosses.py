"""The 72 bosses of the zones added on 2026-11-27 (scripts/zones_more.py), three per zone.

B(zone, id, name, title, icon, colour, hp, dmg, el, mods, minion, intro, special, p2, last, art)
special, by kind (the shapes the game already knows, see BOSSES in data.js):
  ("hit", name, every, mult, ready, hit, dodge)                     a heavy blow
  ("steal", name, every, mult, ready, hit, dodge)                   takes a potion or gold (hit: no full stop)
  ("tangle", name, every, mult, ready, hitlead, dodge, bound, warn, pron)   holds you 2 lines, heals
  ("burn", name, every, mult, ready, hitlead, dodge)                you burn 3 turns
  ("wail", name, every, mult, ready, hit, dodge, word)              its voice over the next line
p2: ("step"|"every"|"dmg", value, text) or ("summon", monster, text)
art: (kind, colours "main,second,accent,eye", options), drawn by build_bosses_kit.py.
The hells' bosses are guardians and afflictions, not deities: when they fall their karma runs out.
"""
BOSSES = []


def B(zone, id, name, title, icon, color, hp, dmg, el, mods, minion, intro, special, p2, last, art):
    BOSSES.append(dict(zone=zone, id=id, name=name, title=title, icon=icon, color=color, hp=hp, dmg=dmg, el=el, mods=mods,
                       minion=minion, intro=intro, special=special, p2=p2, last=last, art=art))


# ---------------------------------------------------------------- páramo
B("guatavita", "cacicaguatavita", "La Cacica de Guatavita", "La que se fue al fondo de la laguna", "floating-ghost", "#60e0d0", 1.3, 1.0, "cold", ["murmullo"], "animacacica",
  "Se arrojó a la laguna con su hija y nunca salió. Cuando baja la niebla, sube a mirar.",
  ("tangle", "El abrazo del agua", 4, 1.8, "El agua de la laguna sube por tus piernas.", "El agua te arrastra hacia el fondo", "Te sueltas y el agua vuelve a su sitio.", "La laguna no te suelta", "Hundido", "ella"),
  ("summon", "culebralaguna", "La Cacica llama a la serpiente de la laguna."), "La Cacica vuelve al fondo, despacio. La laguna se queda en calma.",
  ("floater", "#60e0d0,#2a6a6a,#e8c040,#e0ffff", dict(style="woman", hair=True, water=True)))
B("guatavita", "hombredorado", "El Hombre Dorado", "El que se bañaba en oro", "hooded-figure", "#ffd040", 1.25, 1.05, "light", ["ladron"], "ofrendero",
  "Cubierto de polvo de oro de la cabeza a los pies, de pie sobre una balsa de juncos. Quiere su ofrenda.",
  ("steal", "La ofrenda", 4, 1.8, "El Hombre Dorado extiende las manos: quiere tu ofrenda.", "Se lleva su ofrenda", "Retiras la mano a tiempo."),
  ("every", 3, "Lanza oro al agua y la laguna brilla. Ahora pide más a menudo."), "El oro se le cae de la piel y se hunde. Queda un hombre cansado sobre una balsa.",
  ("figure", "#d8a030,#8a5a20,#fff080,#ffffa0", dict(head="human", hat="crown", body="bare", held="staff", fx="gold", base="raft")))
B("guatavita", "serpientelaguna", "La Serpiente de la Laguna", "La que vive con la cacica", "cobra", "#5ac8a0", 1.4, 1.15, "cold", ["fuerte"], "culebralaguna",
  "Una cabeza sale del agua, y otra vuelta, y otra. La laguna entera es su cuerpo.",
  ("hit", "El golpe de cola", 5, 2.6, "La Serpiente levanta la cola fuera del agua.", "La cola te tira al barro.", "La cola golpea el agua y te salpica."),
  ("dmg", 1.3, "La Serpiente saca todo el cuerpo del agua."), "La Serpiente se enrosca en el fondo y cierra los ojos.",
  ("serpent", "#3a8a6a,#1e4a3a,#e8c040,#f0e060", dict(water=True, crest=True)))
B("cocuy", "senornevado", "El Señor del Nevado", "El que duerme en el hielo", "ogre", "#c8f0ff", 1.4, 1.05, "cold", ["piedra", "gelido"], "golemhielo",
  "Una figura de hielo alta como el glaciar. Cuando abre los ojos, el viento se detiene.",
  ("tangle", "La helada", 4, 1.8, "El Señor del Nevado sopla y el aire se congela.", "Te cubre de hielo", "El hielo se rompe a tus pies.", "El hielo no te deja", "Congelado", "él"),
  ("summon", "grietaviva", "El glaciar se abre y salen grietas vivas."), "El Señor del Nevado se duerme otra vez. El hielo cruje y se calla.",
  ("figure", "#a0d8f0,#4a80b0,#ffffff,#2a80ff", dict(head="ice", hat="crown", body="armor", held="spear", fx="ice", big=True)))
B("cocuy", "avalancha", "La Avalancha", "La que baja sin avisar", "rock-golem", "#f0f8ff", 1.6, 1.2, "cold", ["fuerte", "piedra"], "caminantenieve",
  "Un estruendo arriba. La nieve baja, y tiene brazos.",
  ("hit", "El alud", 5, 2.8, "Toda la ladera tiembla.", "La nieve te entierra.", "Saltas a una roca y la nieve pasa por debajo."),
  ("dmg", 1.3, "La Avalancha se lleva media montaña con ella."), "La nieve se queda quieta. Por fin, silencio.",
  ("colossus", "#e8f0f8,#a8b8d0,#ffffff,#2a80ff", dict(material="snow")))
B("cocuy", "loboventisca", "El Lobo de la Ventisca", "El que aúlla con el viento", "wolf-head", "#e0f0ff", 1.3, 1.2, "cold", ["veloz", "rapido"], "loboblanco",
  "Primero oyes el aullido, después el viento. Cuando ves al lobo, ya es tarde.",
  ("wail", "El aullido", 3, 2.1, "El Lobo levanta el hocico al cielo.", "Su aullido te hiela los huesos.", "Oyes la frase por encima del aullido.", "bramido"),
  ("summon", "loboblanco", "La manada sale de la ventisca."), "El Lobo se pierde en la nieve. Su aullido se oye cada vez más lejos.",
  ("beast", "#e8f0f8,#a8b8c8,#ffffff,#40a0ff", dict(head="wolf", fx="snow")))
B("niebla", "guardianpalmas", "El Guardián de las Palmas", "El más viejo del bosque", "tree-face", "#80c060", 1.5, 1.0, "poison", ["regenera"], "helechogigante",
  "Una palma de cera alta como una torre, con cara. Cuida el bosque desde antes de que hubiera gente.",
  ("tangle", "Las raíces", 4, 1.8, "Las raíces se mueven bajo tus pies.", "Las raíces te atan", "Las raíces agarran la tierra donde estabas.", "Las raíces no te sueltan", "Atado", "él"),
  ("summon", "musgoso", "Del musgo de su tronco caen musgosos."), "El Guardián se queda quieto, una palma más en la niebla.",
  ("tree", "#8a8470,#4a6a3a,#c8d8b0,#f0e040", dict(style="palm", fx="fog")))
B("niebla", "viudaniebla", "La Viuda de la Niebla", "La que espera en el sendero", "floating-ghost", "#c8d8d0", 1.35, 1.05, "cold", ["eco", "murmullo"], "sombrarboles",
  "Una mujer de luto en el sendero, que pregunta por su marido. No tiene pies.",
  ("wail", "El llanto", 3, 2.1, "La Viuda se cubre la cara.", "Su llanto te parte el corazón.", "Oyes la frase debajo del llanto.", "llanto"),
  ("every", 2, "La Viuda grita el nombre de su marido. La niebla se cierra."), "La Viuda se va por el sendero, por fin sola, sin llorar.",
  ("floater", "#2a2a30,#c8d8d0,#ffffff,#a0e0ff", dict(style="woman", veil=True, fx="fog")))
B("niebla", "osoviejo", "El Oso Viejo", "El dueño del bosque", "bear-head", "#e8c080", 1.5, 1.25, None, ["fuerte"], "osoanteojos",
  "Un oso de anteojos enorme, con el pelo blanco en la cara. Ha visto pasar a muchos cazadores.",
  ("hit", "El zarpazo", 4, 2.5, "El Oso Viejo se pone de pie.", "El zarpazo te tumba.", "Te agachas y la zarpa pasa por encima."),
  ("step", 2, "El Oso ruge y todo el bosque se calla."), "El Oso Viejo se va bosque adentro, despacio.",
  ("beast", "#2a2220,#1a1410,#e8d0a0,#ff4020", dict(head="bear", spectacles=True, stand=True)))
B("azufre", "viejovolcan", "El Viejo del Volcán", "El que atiza el fuego de abajo", "hooded-figure", "#ffa040", 1.4, 1.1, "fire", ["igneo"], "espiritucrater",
  "Un viejo sentado al borde del cráter, con una pipa que echa azufre. Dicen que él enciende el volcán.",
  ("burn", "La pipa", 4, 2.0, "El Viejo da una chupada larga a su pipa.", "Te echa el humo encima", "El humo amarillo pasa a tu lado."),
  ("every", 3, "El Viejo golpea el suelo con el bastón. El cráter escupe fuego."), "El Viejo apaga la pipa y se mete en el cráter.",
  ("figure", "#8a6048,#6a5a3a,#e8d040,#ff8020", dict(head="human", beard=True, hat="wide", body="ruana", held="staff", fx="smoke", pipe=True)))
B("azufre", "nubeamarilla", "La Nube Amarilla", "La que quema la garganta", "ghost", "#f0e060", 1.35, 1.05, "poison", ["ladron", "murmullo"], "fumarolaviva",
  "Una nube de azufre que se mueve contra el viento. Dentro, algo respira.",
  ("steal", "El ahogo", 4, 1.8, "La Nube Amarilla te envuelve.", "Te ahoga", "Contienes el aire y sales de la nube."),
  ("summon", "fumarolaviva", "La tierra se abre y salen más fumarolas."), "El viento se lleva la Nube Amarilla. Se puede respirar.",
  ("floater", "#d8d060,#f8f4c0,#8a8030,#ff8020", dict(style="cloud")))
B("azufre", "gigantelava", "El Gigante de Lava", "El que sale del cráter", "rock-golem", "#ff6a1a", 1.6, 1.2, "fire", ["piedra", "fuerte"], "piedrahirviente",
  "Una roca negra con grietas de fuego se levanta del cráter. Cada paso derrite la nieve.",
  ("hit", "El puño de lava", 5, 2.7, "El Gigante levanta un puño que gotea fuego.", "El puño de lava te alcanza.", "El puño se hunde en la nieve, que hierve."),
  ("dmg", 1.3, "Al Gigante se le abren todas las grietas."), "El Gigante se enfría y queda como una roca más.",
  ("colossus", "#3a2420,#1e1210,#ff6a1a,#ffe060", dict(material="lava")))

# ---------------------------------------------------------------- ciénaga
B("manglar", "madredeagua", "La Madre de Agua", "La dueña de los esteros", "floating-ghost", "#60c8e0", 1.35, 1.0, "cold", ["regenera", "eco"], "mareaviva",
  "Una mujer joven con el pelo de oro y los pies al revés, sentada en una raíz del manglar.",
  ("tangle", "Los brazos del estero", 4, 1.8, "El agua del estero gira a tu alrededor.", "El agua te enreda", "Saltas a una raíz y el agua pasa.", "El estero no te suelta", "Atrapado", "ella"),
  ("summon", "mareaviva", "Sube la marea, y con ella sus hijas."), "La Madre de Agua se hunde entre las raíces. La marea baja.",
  ("floater", "#60c8e0,#2a6a8a,#f0c040,#e0ffff", dict(style="woman", hair=True, water=True, goldhair=True)))
B("manglar", "bambero", "El Bambero", "El dueño de los animales del monte", "hooded-figure", "#a0e060", 1.3, 1.1, None, ["ladron", "veloz"], "cangrejoazul",
  "Un hombrecito que silba en el manglar. Protege a los animales, y castiga al que caza de más.",
  ("steal", "El silbido", 4, 1.8, "El Bambero silba y el manglar se llena de ruidos.", "Te esconde las cosas", "No le haces caso, y se calla."),
  ("every", 3, "El Bambero llama a todos los animales del manglar."), "El Bambero se ríe y desaparece entre las raíces.",
  ("figure", "#6a4a34,#4a6a3a,#c8e080,#f0ff80", dict(head="human", hat="wide", body="tunic", held="staff", fx="leaves", small=True, animals=True)))
B("manglar", "pulpogigante", "El Pulpo Gigante", "El que vive bajo las raíces", "slime", "#e06a7a", 1.45, 1.15, "cold", ["piedra"], "pulpomanglar",
  "Ocho brazos salen del agua entre las raíces. El agua se pone negra.",
  ("tangle", "Los ocho brazos", 4, 1.9, "Los brazos del Pulpo se acercan por el agua.", "Los brazos te agarran", "Los brazos se cierran sobre el agua.", "El Pulpo no te suelta", "Agarrado", "él"),
  ("every", 3, "El Pulpo echa tinta y el agua se pone negra."), "El Pulpo se esconde bajo las raíces.",
  ("octopus", "#a04a5a,#6a2a3a,#e8a0a8,#f0e040", dict()))
B("magdalena", "champanfantasma", "El Champán Fantasma", "El que baja el río sin bogas", "ghost", "#a0c8ff", 1.4, 1.05, "cold", ["ladron", "eco"], "bogafantasma",
  "Un champán viejo baja por el río, con su techo de palma y su farol. Los remos se mueven solos.",
  ("steal", "Los remos", 4, 1.8, "El champán se acerca a la orilla y los remos se levantan.", "Te cobran el pasaje", "Te apartas de la orilla a tiempo."),
  ("summon", "bogafantasma", "Los bogas del champán saltan a la orilla."), "El champán sigue río abajo y se pierde en la noche.",
  ("object", "#5a4a3a,#a0c8ff,#e8d080,#e0f0ff", dict(style="boat")))
B("magdalena", "bagreviejo", "El Bagre Viejo", "El que se traga las canoas", "croc-jaws", "#c8c8a0", 1.5, 1.2, "cold", ["fuerte", "piedra"], "bagregigante",
  "Un bagre tan grande como un champán, con bigotes como sogas. Los pescadores le dejan la mitad de lo que sacan.",
  ("hit", "El coletazo", 4, 2.5, "El Bagre Viejo se hunde y el río se queda quieto.", "El coletazo te tira al agua.", "La cola pasa a tu lado."),
  ("dmg", 1.3, "El Bagre Viejo abre la boca: cabe una canoa."), "El Bagre se hunde al fondo del río.",
  ("fish", "#6a6a5a,#a8a890,#3a3a30,#e8c040", dict(style="catfish")))
B("magdalena", "damario", "La Dama del Río", "La que canta en las noches de luna", "floating-ghost", "#e0e8ff", 1.35, 1.05, "cold", ["murmullo", "eco"], "remolinorio",
  "Una mujer vestida de blanco camina sobre el agua y canta. Los que la siguen no vuelven.",
  ("wail", "La canción", 3, 2.0, "La Dama del Río empieza a cantar.", "Su canción te arrastra al agua.", "Oyes la frase por encima de la canción.", "llanto"),
  ("every", 2, "La Dama canta más fuerte. El río se levanta."), "La Dama del Río se hunde cantando. Su voz se apaga.",
  ("floater", "#e8e8f0,#a0b0d0,#ffffff,#a0e0ff", dict(style="woman", water=True, hair=True)))
B("atrato", "guando", "El Guando", "Los que cargan al muerto", "floating-ghost", "#d8d0c0", 1.4, 1.1, "cold", ["eco", "maldito"], "pescadordelta",
  "Una procesión de sombras carga una camilla por la selva. Si te cruzas con ellos, te dan la camilla.",
  ("steal", "La camilla", 4, 1.8, "El Guando se acerca y te ofrece la camilla.", "Te pasan la camilla", "Te apartas y la procesión sigue."),
  ("summon", "pescadordelta", "Más sombras se unen a la procesión."), "La procesión se aleja entre los árboles, cantando bajito.",
  ("object", "#3a3a40,#d8d0c0,#e8d080,#ffffa0", dict(style="procession")))
B("atrato", "anacondamadre", "La Anaconda Madre", "La que duerme en el fondo del delta", "cobra", "#8ac040", 1.6, 1.15, None, ["piedra", "regenera"], "anacondadelta",
  "El tronco atravesado en el caño respira. Tiene ojos.",
  ("tangle", "El abrazo", 4, 1.9, "La Anaconda se desenrolla despacio.", "Te aprieta entre sus anillos", "Te deslizas fuera de sus anillos.", "La Anaconda no te suelta", "Apretado", "ella"),
  ("summon", "anacondadelta", "Sus hijas salen del agua."), "La Anaconda Madre se hunde en el caño. El agua se queda lisa.",
  ("serpent", "#4a6a2a,#2a3a18,#1a2010,#f0c030", dict(spots=True, water=True)))
B("atrato", "senorlluvia", "El Señor de la Lluvia", "El que nunca deja de llover", "ghost", "#a0b8d0", 1.4, 1.1, "light", ["electrico", "murmullo"], "nubelluvia",
  "Una nube negra con forma de hombre, sentada sobre el delta. Llueve desde que llegó.",
  ("hit", "El rayo", 4, 2.4, "El Señor de la Lluvia levanta el brazo y retumba el trueno.", "El rayo cae a tu lado y te tumba.", "El rayo cae en el agua."),
  ("every", 3, "La lluvia se vuelve tormenta."), "La nube se deshace. Por primera vez en meses, sale el sol.",
  ("floater", "#4a5460,#a0b0c0,#f0f080,#ffffff", dict(style="storm")))
B("canocristales", "macarenia", "La Macarenia", "La planta que pinta el río", "evil-tree", "#ff4a6a", 1.45, 1.05, "poison", ["regenera"], "algaroja",
  "Una planta roja gigante se levanta del río, con hojas como banderas.",
  ("tangle", "Las algas", 4, 1.8, "Las algas rojas suben por tus piernas.", "Las algas te atan al fondo", "Te sueltas de las algas.", "Las algas no te sueltan", "Enredado", "ella"),
  ("summon", "algaroja", "El río entero se pone rojo."), "La Macarenia se tiende en el agua y el río vuelve a brillar.",
  ("tree", "#d0304a,#8a1a2a,#f08aa0,#f0e040", dict(style="weed", water=True)))
B("canocristales", "arcoirisagua", "El Arcoíris del Agua", "La serpiente de los cinco colores", "cobra", "#f0c040", 1.4, 1.1, "light", ["veloz", "electrico"], "espiritucano",
  "Una serpiente con los cinco colores del río sale del agua como un arcoíris.",
  ("hit", "El resplandor", 4, 2.4, "La serpiente brilla con todos sus colores.", "El resplandor te ciega y te tumba.", "Cierras los ojos y te apartas."),
  ("step", 2, "Sus colores giran cada vez más rápido."), "El Arcoíris se disuelve en el agua del caño.",
  ("serpent", "#d0304a,#f0c040,#40a060,#ffffff", dict(rainbow=True, water=True)))
B("canocristales", "guardiansierra", "El Guardián de la Sierra", "El que cuida las rocas", "rock-golem", "#c8b8a0", 1.6, 1.15, None, ["piedra", "fuerte"], "piedrapulida",
  "Las rocas del lecho del río se juntan y se levantan. Tienen musgo de colores.",
  ("hit", "El aplastón", 5, 2.7, "El Guardián levanta los dos brazos.", "El aplastón hace temblar el río.", "Las rocas caen en el agua."),
  ("dmg", 1.3, "El Guardián se cubre de algas rojas y crece."), "El Guardián se desarma y vuelve a ser el lecho del río.",
  ("colossus", "#8a7a6a,#5a4e44,#d0304a,#40e0ff", dict(material="stone", moss=True)))

# ---------------------------------------------------------------- selva
B("amazonas", "yacumama", "La Yacumama", "La madre del agua", "cobra", "#60c080", 1.6, 1.15, "poison", ["piedra", "regenera"], "anacondaverde",
  "La serpiente más grande del río, larga como una isla. Se traga lo que pasa cerca.",
  ("tangle", "La corriente", 4, 1.9, "La Yacumama abre la boca y el agua corre hacia ella.", "La corriente te arrastra hacia su boca", "Te agarras a una raíz.", "La corriente no te suelta", "Arrastrado", "ella"),
  ("summon", "anacondaverde", "La Yacumama llama a sus hijas."), "La Yacumama vuelve a dormir en el fondo.",
  ("serpent", "#4a7a2a,#2a4a18,#e8d040,#f0c030", dict(spots=True, water=True, big=True)))
B("amazonas", "chullachaqui", "El Chullachaqui", "El del pie torcido", "goblin", "#c0e060", 1.35, 1.1, None, ["ladron", "veloz"], "monoarana",
  "Se parece a un amigo tuyo, pero tiene un pie de palo. Quiere llevarte selva adentro.",
  ("steal", "El engaño", 4, 1.8, "El Chullachaqui te llama con la voz de un amigo.", "Te engaña", "Le miras los pies y no le sigues."),
  ("every", 3, "El Chullachaqui cambia de cara una y otra vez."), "El Chullachaqui se ríe y se pierde entre los árboles.",
  ("figure", "#8a6048,#5a6a3a,#c8e060,#c8ff60", dict(head="human", hat="wide", body="tunic", held="staff", pegleg=True, fx="leaves")))
B("amazonas", "madreceiba", "La Madre Ceiba", "El árbol que sostiene el cielo", "tree-face", "#a0e060", 1.7, 1.1, "poison", ["regenera", "piedra"], "hongoluz",
  "Una ceiba tan alta que sus raíces son paredes. Tiene una cara en el tronco, y está enfadada.",
  ("hit", "Las raíces", 5, 2.6, "La tierra se levanta: son las raíces de la Ceiba.", "Las raíces te lanzan lejos.", "Saltas por encima de una raíz."),
  ("summon", "hongoluz", "La Ceiba llena el suelo de hongos que brillan."), "La Ceiba cierra los ojos. Sigue sosteniendo el cielo.",
  ("tree", "#8a8070,#3a6a24,#a0e060,#f0e040", dict(style="ceiba")))
B("chiribiquete", "jaguarpintura", "El Jaguar de la Pintura", "El que salió de la roca", "wolf-head", "#ff8a3a", 1.45, 1.25, None, ["veloz", "fuerte"], "jaguarpintado",
  "Uno de los jaguares pintados en la meseta se despega de la roca y baja.",
  ("hit", "El salto", 4, 2.5, "El Jaguar se agacha sobre la roca.", "Te cae encima.", "Salta y cae donde no estás."),
  ("step", 2, "Las manchas rojas del Jaguar brillan."), "El Jaguar vuelve a subir a la roca y se queda quieto, pintado.",
  ("beast", "#c87a30,#8a4a1a,#a8301a,#f0e040", dict(head="cat", spots=True, painted=True)))
B("chiribiquete", "duenoanimales", "El Dueño de los Animales", "El que cuida la selva", "tribal-mask", "#e0c060", 1.4, 1.1, None, ["ladron", "eco"], "hombrepintado",
  "Un hombre con una máscara de jaguar, rodeado de pájaros. Cuida la selva y no le gustan los extraños.",
  ("steal", "La máscara", 4, 1.8, "El Dueño se pone la máscara de jaguar.", "Te quita lo que trajiste", "Bajas la mirada, y te deja pasar."),
  ("summon", "guacamayaroja", "El Dueño silba y bajan las guacamayas."), "El Dueño se quita la máscara y te deja seguir.",
  ("figure", "#8a5a3a,#c8a040,#e0302a,#ffe060", dict(head="jaguar", hat="feathers", body="bare", held="staff", fx="birds")))
B("chiribiquete", "cascadaviva", "La Cascada Viva", "La que cae desde la meseta", "floating-ghost", "#a0e8ff", 1.4, 1.1, "cold", ["murmullo", "regenera"], "lianacascada",
  "Una cascada que cae de la meseta tiene cara y brazos. El ruido no te deja oír.",
  ("tangle", "El chorro", 4, 1.8, "La Cascada abre los brazos.", "El agua te aplasta contra la roca", "Te pegas a la pared y el agua pasa.", "El agua no te deja", "Empapado", "ella"),
  ("every", 3, "La Cascada crece con la lluvia."), "La Cascada vuelve a caer, tranquila.",
  ("floater", "#3a8ab8,#a0e8ff,#ffffff,#e0ffff", dict(style="waterfall")))
B("guacharos", "reyguacharos", "El Rey de los Guácharos", "El que grita en la oscuridad", "evil-bat", "#ff8a4a", 1.4, 1.1, None, ["eco", "veloz"], "guacharo",
  "Un guácharo grande como un hombre, con los ojos rojos. Grita, y la cueva entera grita con él.",
  ("wail", "El grito", 3, 2.1, "El Rey abre el pico.", "Su grito te tumba.", "Oyes la frase por debajo del grito.", "grito"),
  ("summon", "guacharo", "Miles de guácharos levantan el vuelo."), "El Rey de los Guácharos vuelve a su nido en lo alto.",
  ("bird", "#8a5a3a,#c8a070,#ffffff,#ff6020", dict(style="guacharo", crown=True)))
B("guacharos", "bocacueva", "La Boca de la Cueva", "La que se cierra", "rock-golem", "#a0a090", 1.6, 1.2, None, ["piedra", "fuerte"], "estalagmita",
  "La entrada de la cueva tiene dientes. Y se están cerrando.",
  ("hit", "El mordisco", 5, 2.8, "Las estalactitas bajan como dientes.", "Las estalactitas te alcanzan.", "Corres y los dientes se cierran detrás de ti."),
  ("dmg", 1.3, "La cueva entera tiembla."), "La Boca de la Cueva se abre y te deja salir.",
  ("object", "#5a5a54,#3a3a36,#a8a090,#ff6020", dict(style="mouth")))
B("guacharos", "aranamadre", "La Araña Madre", "La que teje en el techo", "hanging-spider", "#c8c0b0", 1.45, 1.15, "poison", ["vampirico"], "aranacueva",
  "Del techo cuelga una araña blanca del tamaño de una vaca. Toda la cueva es su tela.",
  ("tangle", "La tela", 4, 1.8, "La Araña Madre baja por un hilo.", "Te envuelve en su tela", "La tela cae a tu lado.", "La tela no te deja", "Envuelto", "ella"),
  ("summon", "aranacueva", "Sus crías bajan del techo."), "La Araña Madre sube a su tela y se esconde.",
  ("spider", "#d8d0c0,#8a8478,#c04040,#ff3020", dict()))
B("darien", "hombresincamino", "El Hombre sin Camino", "El que se perdió en el Darién", "shambling-zombie", "#c8d8a0", 1.4, 1.1, None, ["ladron", "eco"], "caminantesinrumbo",
  "Un hombre con la ropa hecha jirones pregunta por el camino. Si le contestas, te pierdes con él.",
  ("steal", "La pregunta", 4, 1.8, "El Hombre sin Camino te pregunta: ¿por dónde se sale?", "Te hace perder el rumbo", "No contestas, y sigue su camino."),
  ("every", 3, "El Hombre sin Camino da vueltas a tu alrededor."), "El Hombre encuentra el camino y se va, sin mirar atrás.",
  ("figure", "#8a8070,#4a5a3a,#c8b080,#e0ff80", dict(head="human", beard=True, hat="cap", body="rags", held="machete", fx="ghost", pack=True)))
B("darien", "tigredarien", "El Tigre del Darién", "El que caza entre dos mares", "wolf-head", "#ffc040", 1.5, 1.25, None, ["fuerte", "veloz"], "tigrillosalvaje",
  "Un jaguar viejo y enorme, lleno de cicatrices. Conoce todos los caminos que no existen.",
  ("hit", "El zarpazo", 4, 2.5, "El Tigre desaparece entre las hojas.", "Sale de las hojas y te tumba.", "Le ves venir y te apartas."),
  ("step", 2, "El Tigre ruge y la selva entera se calla."), "El Tigre se va hacia el mar, despacio.",
  ("beast", "#d0902a,#a8701e,#3a2a14,#c8ff40", dict(head="cat", spots=True, scars=True)))
B("darien", "cienagatraga", "La Ciénaga que Traga", "El barro que tiene hambre", "slime", "#8a8a4a", 1.55, 1.05, "poison", ["regenera", "piedra"], "plantased",
  "El suelo parece firme, pero se mueve. Tiene una boca.",
  ("tangle", "El barro", 4, 1.8, "El barro sube hasta tus rodillas.", "El barro te traga hasta la cintura", "Saltas a un tronco.", "El barro no te suelta", "Hundido", "ella"),
  ("summon", "plantased", "Del barro salen plantas de la sed."), "La Ciénaga se queda quieta, y es solo barro.",
  ("blob", "#5a5a30,#3a3a1e,#8a8a4a,#f0e040", dict(style="mud")))

# ---------------------------------------------------------------- llano
B("tatacoa", "gliptodonte", "El Gliptodonte", "El armadillo de antes de la gente", "boar", "#e0c8a0", 1.7, 1.2, None, ["piedra", "fuerte"], "armadillofosil",
  "Un armadillo grande como una casa, de los que vivían aquí hace miles de años. Sus huesos se levantaron.",
  ("hit", "El coletazo", 5, 2.7, "El Gliptodonte levanta la cola de púas.", "La cola de púas te alcanza.", "La cola golpea la tierra roja."),
  ("dmg", 1.3, "Al Gliptodonte se le cae la tierra de encima: es todo hueso."), "El Gliptodonte se tiende y vuelve a ser fósil.",
  ("beast", "#a8704a,#6a4028,#e0d8c0,#ff6020", dict(head="glypto")))
B("tatacoa", "espantotatacoa", "El Espanto de la Tatacoa", "El que aúlla de noche", "ghost", "#ff8a5a", 1.35, 1.1, "fire", ["eco", "ladron"], "polvorojo",
  "De noche se oye un aullido en los laberintos rojos. Es un espanto de polvo con ojos de fuego.",
  ("steal", "El remolino", 4, 1.8, "El Espanto da vueltas y levanta el polvo.", "Te arrebata", "Te tapas la cara y el polvo pasa."),
  ("summon", "polvorojo", "El desierto se llena de remolinos."), "El Espanto se deshace en polvo rojo.",
  ("floater", "#d06a3a,#f0a070,#8a3a1a,#ffe060", dict(style="dust")))
B("tatacoa", "estrellacaida", "La Estrella Caída", "La que bajó del cielo", "burning-skull", "#fff080", 1.4, 1.2, "fire", ["igneo", "electrico"], "buscadorestrellas",
  "Una noche cayó una estrella en el desierto. No se apagó: se levantó.",
  ("burn", "La luz", 4, 2.1, "La Estrella brilla tanto que no ves nada.", "Su luz te quema", "Cierras los ojos y te apartas."),
  ("every", 3, "La Estrella se enciende como un sol pequeño."), "La Estrella vuelve a subir al cielo y se queda con las otras.",
  ("floater", "#fff080,#ffd040,#ff8020,#ffffff", dict(style="meteor")))
B("guajira", "vientohabla", "El Viento que Habla", "El que dice tu nombre", "shouting", "#f0e0b0", 1.4, 1.1, None, ["murmullo", "eco"], "remolinoarena",
  "En la Guajira el viento no para. Este, además, habla, y sabe tu nombre.",
  ("wail", "La voz del viento", 3, 2.1, "El viento toma aire.", "El viento te tumba en la arena.", "Oyes la frase por encima del viento.", "grito"),
  ("every", 2, "El viento sopla desde todas partes."), "El viento se calma. Solo se oye el mar.",
  ("floater", "#d8c090,#f8ecd0,#a07a40,#ffffff", dict(style="wind")))
B("guajira", "piratacabo", "El Pirata del Cabo", "El que enterró el tesoro", "skeleton", "#e0d8c0", 1.4, 1.15, None, ["ladron", "fuerte"], "piratahogado",
  "Un pirata de barba blanca, con un garfio y una pala. Busca su tesoro en la arena, y cree que lo tienes tú.",
  ("steal", "El garfio", 4, 1.9, "El Pirata levanta el garfio.", "Te registra los bolsillos", "El garfio se clava en la arena."),
  ("summon", "piratahogado", "Su tripulación sale del mar."), "El Pirata encuentra su cofre, vacío, y se sienta a mirar el mar.",
  ("figure", "#c8906a,#2a3a6a,#e8c040,#40e0c0", dict(head="human", beard=True, hat="tricorn", body="coat", held="saber", hook=True)))
B("guajira", "toroarena", "El Toro de Arena", "El que corre con el viento", "charging-bull", "#e0b070", 1.5, 1.25, None, ["rapido", "fuerte"], "chivosalvaje",
  "Un toro hecho de arena corre por las dunas. Donde pisa, la arena vuela.",
  ("hit", "La embestida", 4, 2.5, "El Toro de Arena escarba en la duna.", "La embestida te entierra en la arena.", "Te apartas, y el toro se deshace y se vuelve a hacer."),
  ("step", 2, "El Toro corre más rápido que el viento."), "El Toro de Arena se deshace en la duna.",
  ("beast", "#d8b070,#a07a40,#f0e0b0,#ff6020", dict(head="bull", fx="sand")))
B("canon", "hormigareina", "La Hormiga Reina", "La madre de todas las culonas", "wasp-sting", "#c84a2a", 1.5, 1.15, "poison", ["regenera", "vampirico"], "hormigaculona",
  "Una hormiga del tamaño de una vaca, con alas, en un hormiguero alto como un cerro.",
  ("tangle", "Las mandíbulas", 4, 1.9, "La Reina abre las mandíbulas.", "Te sujeta con las mandíbulas", "Las mandíbulas se cierran en el aire.", "La Reina no te suelta", "Sujetado", "ella"),
  ("summon", "hormigaculona", "Sale todo el hormiguero."), "La Reina vuelve a su hormiguero. Las hormigas la siguen.",
  ("ant", "#6a2a14,#3a1408,#c84a2a,#ff3020", dict()))
B("canon", "diablocanon", "El Diablo del Cañón", "El que sopla el calor", "devil-mask", "#ff5a2a", 1.45, 1.2, "fire", ["igneo", "maldito"], "vientocaliente",
  "Al fondo del cañón vive un diablo que sopla el calor hacia arriba. Por eso el cañón quema.",
  ("burn", "El soplo", 4, 2.1, "El Diablo toma aire.", "Te sopla fuego", "El soplo sube por la pared."),
  ("every", 3, "El Diablo se ríe y el cañón entero se calienta."), "El Diablo se mete en una grieta, y por fin corre una brisa.",
  ("figure", "#a8301a,#5a1a10,#e8c040,#ffd040", dict(head="demon", body="bare", held="trident", fx="flame", tail=True)))
B("canon", "condorviejo", "El Cóndor Viejo", "El que vigila el cañón", "vulture", "#e8e0d0", 1.4, 1.15, None, ["veloz", "eco"], "condorcanon",
  "Un cóndor de alas inmensas, con el collar blanco ya gris de viejo. Vuela en círculos sobre ti.",
  ("wail", "El chillido", 3, 2.0, "El Cóndor Viejo baja en picada.", "Su chillido te tumba.", "Oyes la frase por encima del chillido.", "grito"),
  ("summon", "condorcanon", "Otros cóndores bajan con él."), "El Cóndor Viejo sube con el aire caliente y se pierde.",
  ("bird", "#2a2420,#d8d0c0,#c88060,#ff6020", dict(style="condor")))
B("volcan", "senorvolcan", "El Señor del Volcán", "El que duerme bajo la montaña", "rock-golem", "#ff4a1a", 1.6, 1.2, "fire", ["igneo", "piedra"], "rocafundida",
  "La montaña entera se mueve. Tiene una cara de roca negra y una boca de lava.",
  ("burn", "La lava", 4, 2.2, "El Señor del Volcán abre la boca.", "La lava te alcanza", "La lava pasa a tu lado y se enfría."),
  ("summon", "rocafundida", "El volcán escupe rocas."), "El Señor del Volcán cierra la boca y se duerme.",
  ("colossus", "#2a1a14,#140a08,#ff6a1a,#ffe060", dict(material="lava", mouth=True, peak=True)))
B("volcan", "serpientefuego", "La Serpiente de Fuego", "La que nada en la lava", "cobra", "#ff8a1a", 1.45, 1.2, "fire", ["veloz", "igneo"], "salamandralava",
  "Una serpiente de fuego sale del río de lava y se enrosca.",
  ("burn", "La mordida", 4, 2.1, "La Serpiente levanta la cabeza.", "Te muerde con colmillos de fuego", "La Serpiente muerde el aire."),
  ("step", 2, "La Serpiente se enciende entera."), "La Serpiente de Fuego vuelve a la lava.",
  ("serpent", "#e05a1a,#8a2a0a,#ffd040,#ffffff", dict(fire=True, hood=True)))
B("volcan", "pajarolava", "El Pájaro de Lava", "El que nace de la ceniza", "raven", "#ffb040", 1.4, 1.25, "fire", ["rapido", "regenera"], "pajaroceniza",
  "Un pájaro de fuego con alas de ceniza. Cuando cae, vuelve a nacer.",
  ("hit", "La caída", 4, 2.5, "El Pájaro de Lava sube muy alto.", "Cae sobre ti como una piedra ardiente.", "Se estrella donde estabas."),
  ("every", 3, "El Pájaro de Lava arde más fuerte."), "El Pájaro se deshace en ceniza. Nadie sabe si volverá a nacer.",
  ("bird", "#ff8a1a,#ffd040,#6a6460,#ffffff", dict(style="phoenix")))

# ---------------------------------------------------------------- ruinas
B("tierradentro", "duenotumba", "El Dueño de la Tumba", "El que duerme pintado", "tribal-mask", "#ff6a3a", 1.45, 1.15, "light", ["maldito", "eco"], "sombrapintada",
  "Al fondo del hipogeo, una figura con una máscara pintada se levanta de su lecho de piedra.",
  ("tangle", "La maldición", 4, 1.8, "El Dueño de la Tumba levanta las manos.", "La maldición te ata", "La maldición se deshace en el aire.", "La maldición no te deja", "Maldito", "él"),
  ("summon", "sombrapintada", "Las figuras pintadas salen de las paredes."), "El Dueño se vuelve a acostar y se queda quieto, pintado.",
  ("figure", "#c8a880,#1a1410,#a8301a,#ffe060", dict(head="mask", body="robe", held="staff", fx="painted")))
B("tierradentro", "granurna", "La Gran Urna", "La que guarda los huesos", "rock-golem", "#e0a060", 1.6, 1.2, None, ["piedra", "fuerte"], "urnaviva",
  "Una urna de barro más alta que tú, con una cara pintada. Se mueve.",
  ("hit", "El golpe", 5, 2.7, "La Gran Urna se inclina hacia ti.", "La Urna te cae encima.", "La Urna golpea el suelo y suena hueca."),
  ("dmg", 1.3, "La Urna se raja y por la grieta sale una luz."), "La Gran Urna se queda quieta, rajada, en su rincón.",
  ("object", "#a86a3a,#6a3a1a,#2a1a10,#ffb040", dict(style="urn")))
B("tierradentro", "serpientepintada", "La Serpiente Pintada", "La de la escalera", "cobra", "#e03a2a", 1.45, 1.15, "poison", ["veloz"], "serpienteescalera",
  "La serpiente roja y negra pintada en la escalera se despega de la pared.",
  ("hit", "La mordida", 4, 2.4, "La Serpiente levanta la cabeza.", "Te muerde.", "Muerde la pared."),
  ("summon", "serpienteescalera", "Más serpientes bajan por la escalera."), "La Serpiente vuelve a la pared y se queda pintada.",
  ("serpent", "#a8301a,#1a1410,#f0e8d8,#ffe060", dict(bands=True)))
B("murallas", "corsario", "El Corsario de la Bahía", "El que atacó la ciudad", "skeleton", "#ffd060", 1.45, 1.15, None, ["ladron", "fuerte"], "piratesqueleto",
  "Un corsario de casaca roja salta la muralla, con el sable entre los dientes. Viene por el oro.",
  ("steal", "El saqueo", 4, 1.9, "El Corsario levanta el sable.", "Te saquea", "El sable choca contra la piedra."),
  ("summon", "piratesqueleto", "Su tripulación sube por la muralla."), "El Corsario salta al mar y nada hacia su barco.",
  ("figure", "#c8906a,#a82a2a,#e8c040,#ffe060", dict(head="human", beard=True, hat="tricorn", body="coat", held="saber")))
B("murallas", "castillovivo", "El Castillo Vivo", "El que no se rinde", "rock-golem", "#c8b890", 1.7, 1.2, None, ["piedra", "fuerte"], "canonvivo",
  "Las piedras del castillo se levantan. Tiene garitas por hombros y cañones por brazos.",
  ("hit", "El cañonazo", 5, 2.8, "El Castillo apunta sus cañones.", "El cañonazo te alcanza.", "La bala pasa silbando."),
  ("dmg", 1.3, "El Castillo dispara todos sus cañones a la vez."), "El Castillo se vuelve a sentar sobre la colina.",
  ("colossus", "#c8b890,#8a7a60,#3a3a3a,#ff8020", dict(material="castle")))
B("murallas", "galeonhundido", "El Galeón Hundido", "El que se llevó el oro al fondo", "ghost", "#a0e0e0", 1.45, 1.1, "cold", ["eco", "murmullo"], "espiritufoso",
  "Un galeón cubierto de algas sale del agua en la bahía, con las velas rotas. Se oyen campanas.",
  ("wail", "Las campanas", 3, 2.1, "Las campanas del Galeón empiezan a sonar.", "Las campanas te tumban.", "Oyes la frase por encima de las campanas.", "bramido"),
  ("every", 2, "El Galeón sube del todo, y se abren sus cañones."), "El Galeón se hunde otra vez, con su oro.",
  ("object", "#3a4a4a,#a0e0e0,#4a7a3a,#e0ffff", dict(style="galleon")))
B("mompox", "noviamompox", "La Novia de Mompox", "La que espera en el balcón", "floating-ghost", "#f0e8ff", 1.4, 1.1, "cold", ["eco", "murmullo"], "noviabalcon",
  "Una novia con un vestido de hace cien años espera en un balcón. El novio no llegó nunca.",
  ("wail", "El llanto", 3, 2.1, "La Novia mira a la calle vacía.", "Su llanto te hiela.", "Oyes la frase por encima del llanto.", "llanto"),
  ("every", 2, "La Novia baja del balcón y te sigue."), "La Novia se quita el velo y se va hacia el río.",
  ("floater", "#f0ecf4,#c8c0d8,#ffffff,#a080ff", dict(style="woman", veil=True, dress=True)))
B("mompox", "orfebreplata", "El Orfebre de Plata", "El que hace la filigrana", "hooded-figure", "#e0e8ff", 1.4, 1.15, "light", ["ladron", "electrico"], "orfebre",
  "Un viejo orfebre trabaja la plata en hilos finos como el pelo. Lo que te quita, lo vuelve filigrana.",
  ("steal", "La filigrana", 4, 1.8, "El Orfebre tiende hilos de plata a tu alrededor.", "Te enreda en filigrana", "Los hilos se cierran en el aire."),
  ("every", 3, "El Orfebre trabaja cada vez más rápido."), "El Orfebre guarda sus herramientas y apaga la lámpara.",
  ("figure", "#8a6048,#3a3a4a,#e8e8f0,#a0e8ff", dict(head="human", beard=True, body="coat", held="hammer", fx="silver")))
B("mompox", "relojplaza", "El Reloj de la Plaza", "El que se paró a medianoche", "rock-golem", "#f0d080", 1.6, 1.2, None, ["piedra", "maldito"], "relojparado",
  "El reloj de la torre se paró hace cien años. Esta noche da las doce.",
  ("hit", "Las doce campanadas", 5, 2.7, "Las agujas del Reloj se juntan en las doce.", "Las campanadas te tumban.", "Te tapas los oídos y te apartas."),
  ("step", 2, "Las agujas del Reloj giran hacia atrás."), "El Reloj se vuelve a parar, ahora a la una.",
  ("object", "#e8e0d0,#a89a80,#3a2a1a,#ffe060", dict(style="clock")))
B("minassal", "gigantesal", "El Gigante de Sal", "El que sostiene la montaña", "rock-golem", "#f0f0ff", 1.7, 1.2, None, ["piedra", "fuerte"], "golemsal",
  "Un gigante blanco de sal, tallado por los mineros sin querer. Sostiene el techo con la espalda.",
  ("hit", "El derrumbe", 5, 2.8, "El Gigante se endereza y el techo cruje.", "Te cae el techo encima.", "Corres y el techo cae detrás de ti."),
  ("dmg", 1.3, "El Gigante suelta el techo para pelear con las dos manos."), "El Gigante vuelve a sostener la montaña, quieto.",
  ("colossus", "#e8e8f0,#a8a8c0,#ffffff,#6060ff", dict(material="salt")))
B("minassal", "vetaviva", "La Veta Viva", "La serpiente de cristal", "cobra", "#c8c8ff", 1.45, 1.15, "light", ["electrico", "regenera"], "cristalsal",
  "La veta de sal de la pared se mueve: es una serpiente de cristal violeta.",
  ("tangle", "Los cristales", 4, 1.8, "La Veta Viva brilla y los cristales crecen.", "Los cristales te encierran", "Rompes los cristales antes de que se cierren.", "Los cristales no te dejan", "Encerrado", "ella"),
  ("summon", "cristalsal", "Las paredes se llenan de cristales vivos."), "La Veta vuelve a la pared.",
  ("serpent", "#8a8ae0,#5a5ab0,#e0e0ff,#ffffff", dict(crystal=True)))
B("minassal", "capataz", "El Capataz de la Mina", "El que no deja salir a nadie", "hooded-figure", "#f0c060", 1.45, 1.15, None, ["ladron", "fuerte"], "minerosal",
  "Un hombre con casco y látigo. Cobra a los mineros cada piedra que sacan.",
  ("steal", "El cobro", 4, 1.8, "El Capataz levanta el látigo.", "Te cobra la sal", "El látigo suena en el aire."),
  ("summon", "minerosal", "El Capataz llama a sus mineros."), "El Capataz suelta el látigo. Los mineros salen a la luz.",
  ("figure", "#8a6048,#4a4a5a,#e8c040,#ff6020", dict(head="human", hat="helm", body="coat", held="whip", lamp=True)))

# ---------------------------------------------------------------- the hells
B("infiernoscalientes", "guardianlinea", "El Guardián de la Línea Negra", "El que marca a los condenados", "minotaur", "#ff4a1a", 1.8, 1.25, "fire", ["fuerte", "maldito", "igneo"], "cabezatoro",
  "Un guardián con cabeza de toro marca líneas negras sobre los cuerpos, y luego corta por ellas.",
  ("tangle", "Las líneas", 4, 2.0, "El Guardián estira un cordel negro.", "Te marca con el cordel", "El cordel se queda en el aire.", "Las líneas negras no te dejan", "Marcado", "él"),
  ("summon", "cabezatoro", "Llegan más guardianes."), "El karma del Guardián se agota. Su forma se deshace y renace en otro lugar.",
  ("figure", "#8a2a1a,#2a1410,#1a1a1a,#ffd040", dict(head="ox", body="armor", held="chain", fx="flame", big=True)))
B("infiernoscalientes", "ira", "La Ira", "La que enciende los infiernos", "devil-mask", "#ff2a1a", 1.85, 1.3, "fire", ["igneo", "rapido", "fuerte"], "llamahambrienta",
  "Los infiernos calientes nacen de la ira. Aquí la ira tiene cara, y arde.",
  ("burn", "El fuego de la ira", 4, 2.3, "La Ira grita y todo se enciende.", "Su fuego te alcanza", "Respiras hondo y el fuego pasa."),
  ("every", 3, "La Ira crece con cada golpe."), "La Ira se consume en su propio fuego y se apaga. Ya no queda nada que quemar.",
  ("figure", "#c81a0a,#5a0a04,#ffb040,#ffffff", dict(head="demon", hair="flame", body="bare", held="sword", arms=4, fx="flame", big=True)))
B("infiernoscalientes", "montanasaplastan", "Las Montañas que Aplastan", "Las que se juntan", "rock-golem", "#c86a3a", 1.9, 1.3, None, ["piedra", "fuerte"], "rocaaplastadora",
  "Dos montañas con cabeza de animal se acercan una a otra, y todo lo que queda en medio queda aplastado.",
  ("hit", "El aplastamiento", 5, 2.9, "Las Montañas empiezan a juntarse.", "Las Montañas te aplastan.", "Sales de en medio a tiempo."),
  ("dmg", 1.3, "Las Montañas se juntan más rápido."), "Las Montañas se separan y se quedan quietas. Su karma se ha agotado.",
  ("colossus", "#5a3a30,#2a1410,#ff6a1a,#ffd040", dict(material="stone", big=True)))
B("infiernosfrios", "carcelerofrio", "El Carcelero del Hielo", "El que cierra las celdas", "hooded-figure", "#80c8ff", 1.8, 1.25, "cold", ["gelido", "piedra"], "carcelerohielo",
  "Un carcelero de hielo con un manojo de llaves heladas. En los infiernos fríos no hay puertas, pero él las cierra.",
  ("tangle", "Las cadenas de hielo", 4, 2.0, "El Carcelero hace sonar sus cadenas.", "Te encadena al hielo", "Las cadenas caen en la nieve.", "Las cadenas no te dejan", "Encadenado", "él"),
  ("summon", "carcelerohielo", "Más carceleros salen de la oscuridad."), "El Carcelero suelta las llaves. Su karma se agota, y el hielo se derrite un poco.",
  ("figure", "#8ab0d8,#3a5a8a,#e0f4ff,#80e0ff", dict(head="helm", body="armor", held="chain", fx="ice", keys=True, big=True)))
B("infiernosfrios", "granloto", "El Gran Loto Partido", "El último de los infiernos fríos", "evil-tree", "#ff6a8a", 1.85, 1.3, "cold", ["eco", "regenera"], "lotorojo",
  "Aquí el frío es tanto que la carne se abre como los pétalos de un loto. Un loto enorme, rojo y azul, se abre en la nieve.",
  ("wail", "El lamento", 3, 2.2, "El Gran Loto se abre y deja salir un lamento.", "Su lamento te hiela por dentro.", "Oyes la frase debajo del lamento.", "llanto"),
  ("every", 2, "Los pétalos del Gran Loto se abren todos a la vez."), "El Gran Loto se cierra. Su karma se agota, y renace en un lugar más cálido.",
  ("floater", "#c83a4a,#3a6ac8,#ffa0a8,#ffffff", dict(style="lotus")))
B("infiernosfrios", "ventiscaeterna", "La Ventisca Eterna", "La que nunca para", "ghost", "#e0f0ff", 1.8, 1.25, "cold", ["ladron", "murmullo", "gelido"], "vientocorta",
  "Una tormenta de nieve con forma de mujer, que sopla desde el principio del tiempo.",
  ("steal", "El viento", 4, 1.9, "La Ventisca abre los brazos.", "Te arranca lo que llevas", "Te agachas y el viento pasa por encima."),
  ("summon", "vientocorta", "Del viento salen más vientos."), "La Ventisca se calma. Por un momento, en el infierno frío no sopla nada.",
  ("floater", "#a0c0e8,#e8f4ff,#ffffff,#2a60c0", dict(style="woman", hair=True, fx="snow")))
B("infiernosvecinos", "shalmali", "El Árbol Shalmali", "El de las hojas de hierro", "evil-tree", "#c8c8d8", 1.9, 1.3, None, ["piedra", "fuerte", "vampirico"], "arbolespadas",
  "Un árbol de hierro con espinas como espadas. Arriba alguien te llama por tu nombre; si subes, las espinas apuntan hacia abajo.",
  ("tangle", "Las espinas", 4, 2.0, "Las ramas de hierro se mueven hacia ti.", "Las espinas te atrapan", "Las espinas se clavan en el suelo.", "Las espinas no te dejan", "Atrapado", "él"),
  ("summon", "cuervohierro", "Los cuervos de hierro bajan de sus ramas."), "Las espinas se doblan. El karma del árbol se agota, y se vuelve un árbol cualquiera.",
  ("tree", "#4a4448,#a8a8b8,#e8e8f0,#ff3020", dict(style="shalmali")))
B("infiernosvecinos", "barquerorio", "El Barquero del Río de Ceniza", "El que cobra por cruzar", "hooded-figure", "#e0d0e0", 1.8, 1.25, None, ["ladron", "eco"], "barqueroceniza",
  "Un barquero encapuchado en un río de ceniza caliente. Cobra por cruzar, pero la otra orilla no existe.",
  ("steal", "El pasaje", 4, 1.9, "El Barquero tiende la mano.", "Te cobra el pasaje", "Te apartas de la orilla."),
  ("summon", "sombrario", "Las sombras del río suben a la barca."), "El Barquero deja el remo. Su karma se agota, y el río de ceniza se enfría.",
  ("figure", "#8a8288,#4a4448,#e8e0e8,#ff8020", dict(head="hood", body="robe", held="oar", fx="ash", base="boat")))
B("infiernosvecinos", "cuervomayor", "El Gran Cuervo de Hierro", "El que arranca los ojos", "raven", "#a8a8b8", 1.8, 1.3, None, ["rapido", "fuerte"], "cuervohierro",
  "Un cuervo de hierro del tamaño de un caballo, con el pico afilado como un cuchillo.",
  ("hit", "El picotazo", 4, 2.6, "El Gran Cuervo abre las alas de hierro.", "El picotazo te tumba.", "El pico se clava en la tierra."),
  ("step", 2, "Las alas del Gran Cuervo suenan como espadas."), "El Gran Cuervo se posa y se queda quieto. Su karma se agota.",
  ("bird", "#5a5a64,#3a3a44,#c8c8d8,#ff3020", dict(style="raven", metal=True)))
B("infiernosefimeros", "puertaviva", "El que Vive en la Puerta", "El que siente cada portazo", "rock-golem", "#e0a060", 1.8, 1.25, None, ["piedra", "eco"], "puertagime",
  "Una puerta vieja con una cara en la madera. Siente cada vez que la abren y la cierran.",
  ("hit", "El portazo", 5, 2.8, "La puerta se abre de par en par.", "El portazo te tumba.", "La puerta se cierra en el aire."),
  ("summon", "puertagime", "Se abren más puertas a tu alrededor."), "La puerta se abre despacio. Su karma se agota, y lo que vivía en ella sale libre.",
  ("object", "#6a4a30,#3a2a1a,#a8a8b0,#ffe060", dict(style="door")))
B("infiernosefimeros", "fogoneterno", "El Fogón Eterno", "El que arde sin descanso", "small-fire", "#ff8a2a", 1.85, 1.25, "fire", ["igneo", "regenera"], "fogonllora",
  "Un fogón de piedra que nunca se apaga. Dentro, algo siente el fuego de cada comida.",
  ("burn", "Las brasas", 4, 2.2, "El Fogón escupe brasas.", "Las brasas te queman", "Las brasas caen a tus pies."),
  ("summon", "ollahirviendo", "Las ollas del Fogón empiezan a hervir."), "El Fogón se apaga por primera vez. Su karma se agota, y queda ceniza tibia.",
  ("object", "#5a4a40,#3a2e28,#ff6a1a,#ffd040", dict(style="stove")))
B("infiernosefimeros", "piedrarecuerda", "La Piedra que Recuerda", "La que siente cada paso", "rock-golem", "#a0c8ff", 1.9, 1.25, None, ["piedra", "maldito"], "piedracamino",
  "Una piedra en medio del camino, pisada por todos. Recuerda cada paso, y no olvida.",
  ("tangle", "El peso", 4, 2.0, "La Piedra que Recuerda se hace pesada.", "Te aplasta con todo su peso", "Te apartas de su sombra.", "El peso no te deja", "Aplastado", "ella"),
  ("every", 3, "La Piedra recuerda todos los pasos a la vez."), "La Piedra se parte en dos. Su karma se agota, y lo que vivía en ella se va.",
  ("colossus", "#7a7468,#4a4640,#a8a090,#80c0ff", dict(material="stone", sad=True)))
