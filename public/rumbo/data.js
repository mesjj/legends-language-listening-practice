// Rumbo's content: stations, goods, events, the people you hear. Pure data, no DOM: the game, the
// economy's tests and the clip pipeline (scripts/rumbo/) all import it.

export const SESSION_TURNS = 12;
export const START = { credits: 1500, hold: 20, station: "bachue" };
export const HOLD_UPGRADE = { hold: 40, cost: 2500, at: "bachue" };
export const COST = { drink: 20, replay: 5, slow: 10 };
export const SLOW_RATE = 0.75;

// base price in credits; each station multiplies it (producers ~0.6, buyers ~1.4)
export const GOODS = {
  mineral: { name: "mineral", art: "el mineral", base: 300 },
  hielo: { name: "hielo", art: "el hielo", base: 60 },
  comida: { name: "comida", art: "la comida", base: 140 },
  medicinas: { name: "medicinas", art: "las medicinas", base: 520 },
  maquinaria: { name: "maquinaria", art: "la maquinaria", base: 900 },
};
export const GOOD_IDS = Object.keys(GOODS);

export const STATIONS = {
  tequendama: {
    name: "Mina Tequendama", short: "la mina", radio: "Radio de la mina", kind: "Luna minera",
    blurb: "Una luna de roca y polvo. Mineros curtidos, acentos fuertes, radio con estática.",
    factor: { mineral: 0.6, hielo: 0.6, comida: 1.4, medicinas: 1.4, maquinaria: 1.0 },
    noise: 0.55, announcer: "locutor_mina",
  },
  bachue: {
    name: "Puerto Bachué", short: "el puerto", radio: "Radio del puerto", kind: "Puerto de comercio",
    blurb: "El gran mercado de la ruta. Locutores claros, compra de todo a precio justo.",
    factor: { mineral: 1.15, hielo: 1.15, comida: 1.15, medicinas: 1.15, maquinaria: 1.15 },
    noise: 0, announcer: "locutora_puerto",
  },
  iguaque: {
    name: "Huerta Iguaque", short: "la huerta", radio: "Radio de la huerta", kind: "Anillo agrícola",
    blurb: "Un anillo de cultivos que gira despacio. Necesita mineral y máquinas.",
    factor: { mineral: 1.4, hielo: 1.0, comida: 0.6, medicinas: 1.0, maquinaria: 1.4 },
    noise: 0.25, announcer: "locutora_huerta",
  },
};
export const STATION_IDS = Object.keys(STATIONS);
// fuel in credits for a jump between two stations; each jump is one turn
export const FUEL = { "bachue-tequendama": 40, "bachue-iguaque": 40, "iguaque-tequendama": 70 };
export const fuel = (a, b) => (a === b ? 0 : FUEL[[a, b].sort().join("-")]);

// noise of the radio filter by source (the broadcast's comes from its station)
export const SOURCE_NOISE = { rumor: 0.3, contract: 0.1 };

// Events: planned price shocks. A rumor clip describes one of these; the game schedules it (or not).
export const EVENTS = {
  huelga: { station: "tequendama", good: "mineral", dir: 1, what: "una huelga de los mineros" },
  veta: { station: "tequendama", good: "mineral", dir: -1, what: "una veta nueva y muy rica de mineral" },
  derrumbe: { station: "tequendama", good: "medicinas", dir: 1, what: "un derrumbe en los túneles con heridos" },
  cometa: { station: "tequendama", good: "hielo", dir: -1, what: "un cometa capturado lleno de hielo" },
  bloqueo: { station: "tequendama", good: "comida", dir: 1, what: "los convoyes de comida no llegan a la mina" },
  plaga: { station: "iguaque", good: "comida", dir: 1, what: "una plaga en los cultivos" },
  cosecha: { station: "iguaque", good: "comida", dir: -1, what: "una cosecha récord" },
  riego: { station: "iguaque", good: "maquinaria", dir: 1, what: "el sistema de riego se dañó" },
  obras: { station: "iguaque", good: "mineral", dir: 1, what: "van a construir un anillo nuevo y necesitan mineral" },
  fiebre: { station: "iguaque", good: "medicinas", dir: 1, what: "una fiebre que se está regando entre los cultivadores" },
  cargamento: { station: "bachue", good: "medicinas", dir: -1, what: "llega un cargamento grande de medicinas" },
  feria: { station: "bachue", good: "maquinaria", dir: -1, what: "una feria de maquinaria con remates" },
  fuga: { station: "bachue", good: "hielo", dir: 1, what: "una fuga en los tanques de agua del puerto" },
  banquete: { station: "bachue", good: "comida", dir: 1, what: "las fiestas del puerto, con banquetes" },
};
export const EVENT_SIZE = [0.3, 0.8]; // |shock| as a fraction of the price
export const EVENT_DUR = [2, 4]; // turns

// how sure the speaker says they are; the truth is set by the speaker's reliability times this
export const CERTAINTY = {
  seguro: { label: "Seguro", trust: 1 },
  probable: { label: "Probable", trust: 0.75 },
  rumor: { label: "Solo un rumor", trust: 0.5 },
};

// Voices (Fish Audio reference ids). Every recurring speaker keeps one voice.
// tier: how they speak (1 clear and a bit slow, 2 natural, 3 fast and colloquial)
export const SPEAKERS = {
  locutora_puerto: { name: "Locutora del puerto", role: "announcer", voice: "e296306da5d449999f6e35c2b9f60aea", tiers: [1, 1, 2], station: "bachue" },
  locutora_huerta: { name: "Locutora de la huerta", role: "announcer", voice: "84a980d0ef3d4f8ea185951bd920afbe", tiers: [1, 2, 2, 3], station: "iguaque" },
  locutor_mina: { name: "Locutor de la mina", role: "announcer", voice: "138af509e91b409aa23e50ddb3b8e069", tiers: [2, 3, 3], station: "tequendama" },
  rocio: { name: "La capitana Rocío", role: "regular", voice: "08ecaf85075041fc9aa66698ae430dc4", tiers: [1, 2], reliability: 0.9,
    style: "piloto veterana, habla claro y con calma, frases completas" },
  efrain: { name: "Don Efraín", role: "regular", voice: "da13e1b3f87c4f40b8090d0fd6454921", tiers: [1, 2, 3], reliability: 0.75,
    style: "señor mayor, pausado, usa dichos y rodeos, a veces se va por las ramas" },
  mono: { name: "El Mono", role: "regular", voice: "b46654f2e3ef4f48b5f7c9d22ae3f921", tiers: [2, 3], reliability: 0.6,
    style: "mecánico joven, rápido, muy coloquial: parce, marica, qué nota, de una" },
  yesenia: { name: "Yesenia", role: "regular", voice: "d0a094ffceca4b718676b9404bd16c65", tiers: [2, 3], reliability: 0.45,
    style: "costeña, cantinera, habla rápido y se come las eses: ajá, mi vida, eche" },
  chato: { name: "El Chato", role: "regular", voice: "bc93fd919a214c2eae9fe16492a47489", tiers: [2, 3], reliability: 0.3,
    style: "paisa chismoso, exagera todo: pues, vea, oiga, ave maría, hágale" },
  marcela: { name: "La ingeniera Cárdenas", role: "client", voice: "e8ffb4ccb56a4eb0b1d85b57f2f45a47", tiers: [1, 2],
    style: "ingeniera, precisa y formal, usted" },
  gustavo: { name: "Don Gustavo Rengifo", role: "client", voice: "c943469bcc194734ac1a09d083cb1062", tiers: [2, 3],
    style: "comerciante relajado, conversador, mete detalles de más" },
  barrios: { name: "El señor Barrios", role: "client", voice: "83d3adfc726043c2b6c3c3845b008829", tiers: [2, 3],
    style: "costeño de Barranquilla, rápido, con humor" },
};
export const REGULARS = Object.keys(SPEAKERS).filter((k) => SPEAKERS[k].role === "regular");
export const CLIENTS = Object.keys(SPEAKERS).filter((k) => SPEAKERS[k].role === "client");

// contracts: the pay over the goods' value at the destination grows with how hard the client is to follow
export const CONTRACT_PAY = { 1: 1.2, 2: 1.4, 3: 1.7 };
export const CONTRACT_DEADLINE = [2, 5]; // jumps
export const CONTRACT_QTY = [3, 20];

// Fish Audio speed per tier
export const TIER_SPEED = { 1: 0.9, 2: 1.0, 3: 1.12 };
