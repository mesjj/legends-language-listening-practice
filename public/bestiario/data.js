// El Bestiario: creatures, types, moves, places and people. All original to this game; the sprites
// are the Leyendas monsters (rpg/lpc/monsters.png, LPC art, see rpg/lpc/CREDITS.txt).

// ---------- types ----------
// mult[attacker][defender]: 2 = hurts a lot, 0.5 = barely. Anything not listed is 1.
export const TYPES = {
  agua:   { name: "Agua",   color: "#3f8fd8" },
  fuego:  { name: "Fuego",  color: "#e2572e" },
  planta: { name: "Planta", color: "#4fa648" },
  tierra: { name: "Tierra", color: "#a8773f" },
  aire:   { name: "Aire",   color: "#7fb8c9" },
  veneno: { name: "Veneno", color: "#9a52b8" },
  sombra: { name: "Sombra", color: "#4b4470" },
  monte:  { name: "Monte",  color: "#8f8a78" },
};
const CHART = {
  agua:   { fuego: 2, tierra: 2, agua: 0.5, planta: 0.5 },
  fuego:  { planta: 2, veneno: 2, fuego: 0.5, agua: 0.5, tierra: 0.5 },
  planta: { agua: 2, tierra: 2, planta: 0.5, fuego: 0.5, aire: 0.5, veneno: 0.5 },
  tierra: { fuego: 2, veneno: 2, planta: 0.5, aire: 0.5 },
  aire:   { planta: 2, veneno: 2, tierra: 0.5 },
  veneno: { planta: 2, monte: 2, veneno: 0.5, tierra: 0.5, sombra: 0.5 },
  sombra: { sombra: 2, monte: 2, veneno: 0.5 },
  monte:  { sombra: 0.5 },
};
export const typeMult = (atk, defTypes) => defTypes.reduce((m, d) => m * (CHART[atk]?.[d] ?? 1), 1);

// ---------- moves ----------
// Every move is a listening exercise. form: "hueco" (fill one gap), "huecos" (two or three gaps),
// "dictado" (write the whole line). The harder the form, the harder it hits; how well you wrote it
// decides how much of that lands.
export const FORMS = {
  hueco:   { name: "1 hueco", power: 40, desc: "Escribe una palabra que falta" },
  huecos:  { name: "huecos", power: 65, desc: "Escribe las 2 o 3 palabras que faltan" },
  dictado: { name: "dictado", power: 95, desc: "Escribe la frase entera" },
};
// per type: [quick, strong, total]
const MOVE_NAMES = {
  monte:  ["Arañazo", "Embestida", "Estampida"],
  agua:   ["Salpicón", "Chorro", "Aguacero"],
  fuego:  ["Chispazo", "Llamarada", "Candela"],
  planta: ["Hojazo", "Bejucazo", "Selva viva"],
  tierra: ["Terronazo", "Derrumbe", "Temblor"],
  aire:   ["Picotazo", "Ventarrón", "Remolino"],
  veneno: ["Picadura", "Ponzoña", "Plaga"],
  sombra: ["Susto", "Mal de ojo", "Espanto"],
};
export const MOVES = {};
for (const [type, names] of Object.entries(MOVE_NAMES))
  ["hueco", "huecos", "dictado"].forEach((form, i) => (MOVES[`${type}-${form}`] = { id: `${type}-${form}`, name: names[i], type, form, power: FORMS[form].power }));

// ---------- creatures ----------
// sprite: key in rpg/lpc/atlas.json "monsters"; size: extra scale on top of the atlas's own.
// base: [hp, attack, defence, speed]. rate: how easy to catch (255 easy, 3 very hard).
// evo: [into, at level]. legend: one of the old stories of the land; rare and hard to catch.
const C = (id, name, sprite, types, base, rate, o = {}) => ({ id, name, sprite, types, base, rate, size: 1, ...o });
export const SPECIES = Object.fromEntries([
  C("sapito", "Sapito", "sapito", ["agua"], [45, 49, 47, 46], 45, { evo: ["sapo", 16], blurb: "Canta de noche en los charcos. Si lo coges, se infla para parecer más grande." }),
  C("sapo", "Sapo Bocón", "sapo", ["agua"], [72, 72, 68, 60], 45, { blurb: "Se traga lo que le cabe en la boca, y le cabe casi todo." }),
  C("chispita", "Chispita", "bolafuego", ["fuego"], [40, 56, 40, 62], 45, { size: 0.55, evo: ["bolafuego", 16], blurb: "Una brasa que se escapó de un fogón y no quiso apagarse." }),
  C("bolafuego", "Bolafuego", "bolafuego", ["fuego"], [64, 86, 56, 82], 45, { blurb: "Cruza los potreros rodando de noche. Los arrieros le rezan para que pase de largo." }),
  C("frailejoncito", "Frailejoncito", "frailejon", ["planta"], [50, 46, 56, 40], 45, { size: 0.5, evo: ["frailejon", 16], blurb: "Crece un centímetro al año, y lo dice con orgullo." }),
  C("frailejon", "Frailejón", "frailejon", ["planta"], [82, 66, 86, 50], 45, { blurb: "Guarda el agua de la niebla en sus hojas peludas y la suelta en los ríos." }),
  C("cuervito", "Cuervito", "cuervito", ["aire"], [40, 46, 36, 60], 200, { evo: ["cuervo", 14], blurb: "Roba lo que brilla, aunque no sepa para qué." }),
  C("cuervo", "Cuervo", "cuervo", ["aire", "sombra"], [62, 72, 52, 86], 90, { blurb: "Se acuerda de las caras. Y de quién le tiró una piedra." }),
  C("chulo", "Chulo", "chulo", ["aire"], [56, 56, 46, 56], 150, { blurb: "Da vueltas en el cielo esperando. Es paciente." }),
  C("jabato", "Jabato", "jabato", ["tierra"], [50, 56, 50, 40], 190, { evo: ["zaino", 18], blurb: "Hoza la tierra buscando raíces, y a veces monedas." }),
  C("zaino", "Zaíno", "zaino", ["tierra"], [86, 86, 76, 56], 75, { blurb: "Anda en manada por el monte. Se oye antes de verse." }),
  C("conejo", "Conejo", "conejo", ["monte"], [40, 42, 36, 76], 255, { blurb: "Si lo ves quieto, es que ya te vio primero." }),
  C("mico", "Mico", "mico", ["monte"], [46, 52, 40, 82], 200, { blurb: "Se lleva el sombrero de los turistas y lo devuelve lleno de mangos." }),
  C("culebrita", "Culebrita", "culebrita", ["veneno"], [40, 52, 40, 60], 170, { evo: ["coral", 18], blurb: "Se esconde entre las hojas secas del camino. Mira dónde pisas." }),
  C("coral", "Coral", "coral", ["veneno"], [66, 82, 62, 80], 60, { size: 1.4, blurb: "Rojo, negro y amarillo: el monte avisa con colores." }),
  C("avispa", "Avispa Quitacalzón", "avispa", ["veneno", "aire"], [40, 62, 36, 86], 160, { blurb: "Su nombre lo dice todo. Corre." }),
  C("arana", "Araña Peluda", "arana", ["veneno"], [56, 66, 56, 40], 140, { blurb: "Teje de noche; por la mañana la tela está llena de rocío." }),
  C("alacran", "Alacrán", "alacran", ["veneno", "tierra"], [66, 82, 82, 46], 90, { size: 0.7, blurb: "Duerme dentro de las botas. Sacúdelas siempre." }),
  C("babosa", "Babosa", "babosa", ["agua"], [56, 36, 56, 26], 190, { evo: ["baba", 15], blurb: "Deja un camino que brilla con la luna." }),
  C("baba", "Baba", "baba", ["agua", "veneno"], [86, 56, 82, 30], 75, { blurb: "Nadie sabe qué tiene por dentro. Mejor así." }),
  C("murcieguito", "Murcieguito", "murcieguito", ["sombra", "aire"], [40, 46, 36, 72], 190, { evo: ["vampiro", 20], blurb: "Se cuelga de las vigas de las casas viejas." }),
  C("vampiro", "Vampiro", "vampiro", ["sombra", "aire"], [72, 82, 62, 92], 75, { size: 1.3, blurb: "Visita a las vacas de noche. Ellas no se quejan, pero amanecen cansadas." }),
  C("babilla", "Babilla", "caiman", ["agua", "tierra"], [76, 86, 72, 46], 90, { size: 0.8, blurb: "Flota como un tronco. Los troncos no parpadean." }),
  C("lobo", "Lobo de Monte", "lobo", ["sombra"], [66, 82, 56, 76], 100, { size: 0.8, blurb: "Aúlla a la luna llena, y la luna nunca contesta." }),
  C("oso", "Oso de Anteojos", "oso", ["tierra", "monte"], [92, 86, 72, 40], 60, { size: 0.8, blurb: "Tímido, goloso, y más fuerte de lo que parece." }),
  C("toro", "Toro Cimarrón", "toro", ["tierra"], [86, 92, 72, 56], 60, { size: 0.8, blurb: "Nunca tuvo dueño y no piensa tenerlo." }),
  C("diablillo", "Diablillo", "diablillo", ["fuego", "sombra"], [50, 66, 46, 76], 120, { blurb: "Esconde las llaves, apaga las velas y se ríe bajito." }),
  C("sanguijuela", "Sanguijuela", "sanguijuela", ["agua", "veneno"], [56, 56, 52, 46], 150, { size: 0.8, blurb: "Se pega y no suelta. Un poco como el subjuntivo." }),
  C("duendecillo", "Duendecillo", "duendecillo", ["sombra"], [46, 56, 46, 66], 120, { evo: ["duende", 22], blurb: "Les trenza el pelo a los caballos mientras duermen." }),
  C("duende", "Duende", "duende", ["sombra", "monte"], [72, 82, 66, 82], 60, { blurb: "Se enamora de las muchachas que tocan guitarra, y no las deja en paz." }),
  // the legends
  C("madremonte", "La Madremonte", "madremonte", ["planta", "sombra"], [96, 96, 96, 86], 6, { legend: true, blurb: "Cuida el monte. A quien lo tala, lo pierde en él para siempre." }),
  C("llorona", "La Llorona", "llorona", ["agua", "sombra"], [96, 92, 86, 100], 6, { legend: true, blurb: "Se oye llorar junto al río. Si suena lejos, está cerca." }),
  C("silbon", "El Silbón", "silbon", ["sombra", "aire"], [92, 104, 82, 96], 6, { legend: true, blurb: "Silba do, re, mi, fa, sol, la, si. Si el silbido suena cerca, está lejos." }),
  C("mohan", "El Mohán", "mohan", ["agua", "monte"], [106, 96, 96, 76], 6, { legend: true, blurb: "Vive en las cuevas del río, fuma tabaco y toca el tiple. No le gusta que lo molesten." }),
  C("mandingas", "Mandingas", "mandingas", ["fuego", "sombra"], [92, 110, 82, 92], 6, { legend: true, blurb: "Apuesta con quien se deje, y nunca pierde." }),
].map((s) => [s.id, s]));
export const STARTERS = ["sapito", "chispita", "frailejoncito"];

// ---------- places ----------
// tier: how long the lines get. wild: [species, weight]. legend: one rare old story per place.
export const AREAS = [
  { id: "vereda", name: "La vereda", lvl: [2, 5], tier: 0, sky: ["#bfe3ef", "#e9f3d9"], ground: "#8cbc5a",
    blurb: "Potreros, cercas de alambre y un camino de barro. Aquí empieza todo.",
    wild: [["conejo", 30], ["cuervito", 25], ["jabato", 20], ["babosa", 15], ["mico", 10], ["culebrita", 6]],
    guardian: { name: "Doña Ofelia", title: "la de la tienda", team: [["jabato", 5], ["cuervito", 6]], pesos: 600,
      hi: "¿Usted no es de por aquí, cierto? A ver si sabe oír, que aquí la gente habla rapidito.", bye: "Bueno, bueno. Siga, pues, que el páramo la espera." } },
  { id: "paramo", name: "El páramo", lvl: [6, 10], tier: 1, sky: ["#cdd6dc", "#e6e3d3"], ground: "#7f9663",
    blurb: "Niebla, frailejones y un frío que se mete en los huesos.",
    wild: [["chulo", 25], ["conejo", 15], ["avispa", 20], ["arana", 18], ["frailejoncito", 6], ["oso", 8], ["cuervito", 8]],
    legend: "madremonte",
    guardian: { name: "Don Aurelio", title: "el arriero", team: [["chulo", 9], ["avispa", 9], ["oso", 11]], pesos: 1200,
      hi: "Llevo cuarenta años subiendo mulas por aquí. Usted no me va a ganar en una tarde.", bye: "Caramba. Baje a la ciénaga, que allá la cosa se pone fea." } },
  { id: "cienaga", name: "La ciénaga", lvl: [11, 16], tier: 2, sky: ["#b9d1c4", "#d9e2c9"], ground: "#4f7a64",
    blurb: "Agua quieta, mosquitos y troncos que a veces no son troncos.",
    wild: [["babosa", 20], ["sanguijuela", 20], ["sapito", 10], ["babilla", 12], ["culebrita", 15], ["coral", 5], ["baba", 6]],
    legend: "llorona",
    guardian: { name: "Mercedes", title: "la pescadora", team: [["sanguijuela", 14], ["baba", 15], ["babilla", 17]], pesos: 2000,
      hi: "Usted no es de por aquí. Se le nota en cómo mira el agua.", bye: "Váyase antes de que oscurezca. El monte de noche no es para cualquiera." } },
  { id: "monte", name: "El monte oscuro", lvl: [17, 23], tier: 3, sky: ["#4c5876", "#8b7f8c"], ground: "#3a4a3a",
    blurb: "Árboles tan altos que no se ve el cielo. Algo silba entre las ramas.",
    wild: [["murcieguito", 20], ["lobo", 18], ["duendecillo", 16], ["diablillo", 14], ["cuervo", 14], ["alacran", 10], ["chispita", 4]],
    legend: "silbon",
    guardian: { name: "Doña Tránsito", title: "la rezandera", team: [["duende", 21], ["vampiro", 22], ["lobo", 23]], pesos: 3200,
      hi: "Yo a esas criaturas las conozco desde niña. A usted todavía no.", bye: "Dios la acompañe. A la cueva del río no entra cualquiera." } },
  { id: "cueva", name: "La cueva del río", lvl: [24, 32], tier: 4, sky: ["#2e3346", "#56506a"], ground: "#45403b",
    blurb: "Humo de tabaco, música de tiple y el río que suena por dentro de la piedra.",
    wild: [["vampiro", 18], ["zaino", 16], ["toro", 14], ["alacran", 16], ["bolafuego", 10], ["coral", 12], ["duende", 14]],
    legend: "mohan", legend2: "mandingas",
    guardian: { name: "El Mohán", title: "el dueño del río", team: [["coral", 30], ["bolafuego", 31], ["mohan", 34]], pesos: 8000,
      hi: "¿Quién toca a mi puerta? Si sabe escuchar, entre. Si no, el río se la lleva.", bye: "Usted oye bien. Quédese con el río; yo me quedo con la música." } },
];

// ---------- things to carry ----------
export const ITEMS = {
  totuma:  { name: "Totuma", price: 200, ball: 1, desc: "Una totuma de calabazo. Para atrapar criaturas." },
  pintada: { name: "Totuma pintada", price: 600, ball: 1.6, desc: "Pintada a mano: atrapa mejor." },
  oro:     { name: "Totuma de oro", price: 1500, ball: 2.5, desc: "La mejor. Hasta una leyenda lo pensaría dos veces." },
  panela:  { name: "Agua de panela", price: 300, heal: 30, desc: "Cura 30 de vida." },
  sancocho:{ name: "Sancocho", price: 800, heal: 120, desc: "Cura 120 de vida." },
  tinto:   { name: "Tinto", price: 1000, revive: 0.5, desc: "Despierta a una criatura desmayada, con media vida." },
};
export const BALLS = ["totuma", "pintada", "oro"];
export const TEAM_SIZE = 6;
