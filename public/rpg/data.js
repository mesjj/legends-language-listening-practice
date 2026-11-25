import { GRAMMAR_RUNES } from "./grammar.js";

// Leyendas: static game content. Every name, item and monster here is original to this app.
// Icons: game-icons.net (CC BY 3.0), see icons/CREDITS.txt.

// ---------- rarity ----------
export const RARITY = {
  low:    { name: "Gastado",  color: "#8d8a84" },
  normal: { name: "Normal",   color: "#e4dfd2" },
  magic:  { name: "Mágico",   color: "#7f95ff" },
  rare:   { name: "Raro",     color: "#f0d25c" },
  set:    { name: "De conjunto", color: "#4ccf55" },
  unique: { name: "Único",    color: "#cf9f55" },
  crafted: { name: "Artesanal", color: "#e8873a" },
  runeword: { name: "Palabra rúnica", color: "#d8c08a" }, // only items from before runes were removed
  // above unique, each about a third as common as the one below it
  ancestral:  { name: "Ancestral",  color: "#e0679e" },
  legendario: { name: "Legendario", color: "#ff5a4a" },
  mitico:     { name: "Mítico",     color: "#6fe6ff" },
  tunjo:      { name: "Del arcoíris", color: "#ffb6f0" }, // only from Doña Remedios' tunjo: one of each, never sold
  relic:  { name: "Reliquia", color: "#ff9cf2" },
  gem:    { name: "Gema",     color: "#e4dfd2" },
  runa:   { name: "Runa",     color: "#b9b2a2" },
  potion: { name: "Poción",   color: "#e4dfd2" },
};

// ---------- equipment slots ----------
export const SLOTS = {
  head:   "Cabeza",
  body:   "Torso",
  hands:  "Manos",
  feet:   "Pies",
  belt:   "Cintura",
  neck:   "Cuello",
  shirt:  "Camiseta",
  ring:   "Anillo",
  weapon: "Arma",
  off:    "Mano izquierda",
};
// Where an item kind can go when equipped (ring -> ring1/ring2, weapon -> weapon1/weapon2).
export const EQUIP_SLOTS = ["head", "neck", "shirt", "body", "weapon1", "off1", "weapon2", "off2", "hands", "ring1", "ring2", "belt", "feet"];

// ---------- properties ----------
// fmt: how a value reads on an item. {v} is replaced by the value.
export const PROPS = {
  dmgPct:      { fmt: "+{v}% de daño", order: 1 },
  dmgMin:      { fmt: "+{v} al daño mínimo", order: 2 },
  dmgMax:      { fmt: "+{v} al daño máximo", order: 3 },
  dmgDictation:{ fmt: "+{v}% de daño en dictado", order: 4 },
  dmgCloze:    { fmt: "+{v}% de daño en huecos", order: 5 },
  fire:        { fmt: "+{v} de daño de fuego", order: 6 },
  cold:        { fmt: "+{v} de daño de frío", order: 7 },
  light:       { fmt: "+{v} de daño de rayo", order: 8 },
  poison:      { fmt: "+{v} de daño de veneno", order: 9 },
  crit:        { fmt: "+{v}% de probabilidad de golpe crítico", order: 10 },
  leech:       { fmt: "{v}% del daño se convierte en vida", order: 11 },
  manaLeech:   { fmt: "{v}% del daño se convierte en maná", order: 12 },
  armor:       { fmt: "+{v} de defensa", order: 13 },
  armorPct:    { fmt: "+{v}% de defensa", order: 14 },
  block:       { fmt: "+{v}% de probabilidad de bloquear", order: 15 },
  dodge:       { fmt: "+{v}% de probabilidad de esquivar", order: 16 },
  str:         { fmt: "+{v} de fuerza", order: 20 },
  dex:         { fmt: "+{v} de destreza", order: 21 },
  vit:         { fmt: "+{v} de vitalidad", order: 22 },
  ene:         { fmt: "+{v} de energía", order: 23 },
  allStats:    { fmt: "+{v} a todos los atributos", order: 19 },
  life:        { fmt: "+{v} de vida", order: 24 },
  mana:        { fmt: "+{v} de maná", order: 25 },
  lifeRegen:   { fmt: "Regeneras {v} de vida por turno", order: 26 },
  manaRegen:   { fmt: "Regeneras {v} de maná por turno", order: 27 },
  killHeal:    { fmt: "+{v} de vida por cada enemigo abatido", order: 28 },
  resFire:     { fmt: "Resistencia al fuego +{v}%", order: 30 },
  resCold:     { fmt: "Resistencia al frío +{v}%", order: 31 },
  resLight:    { fmt: "Resistencia al rayo +{v}%", order: 32 },
  resPoison:   { fmt: "Resistencia al veneno +{v}%", order: 33 },
  resAll:      { fmt: "Todas las resistencias +{v}%", order: 29 },
  thorns:      { fmt: "Devuelves {v} de daño a quien te golpea", order: 34 },
  replayCost:  { fmt: "Repetir cuesta {v}% menos maná", order: 40 },
  hintCost:    { fmt: "Las pistas cuestan {v}% menos maná", order: 41 },
  freeReplay:  { fmt: "+{v} repetición gratis por frase", order: 42 },
  slowFree:    { fmt: "Escuchar despacio no cuesta maná", order: 43, flag: true },
  typoTol:     { fmt: "Se perdona {v} letra más por palabra", order: 44 },
  nearExact:   { fmt: "En el combate, las tildes que faltan no restan", order: 45, flag: true },
  comboStart:  { fmt: "Empiezas cada combate con racha de al menos {v}", order: 46 },
  comboKeep:   { fmt: "Un error leve no rompe tu racha", order: 47, flag: true },
  potion:      { fmt: "Las pociones curan {v}% más", order: 50 },
  beltSlots:   { fmt: "+{v} espacios para pociones", order: 51 },
  mf:          { fmt: "+{v}% de probabilidad de objetos mágicos", order: 60 },
  gf:          { fmt: "+{v}% de oro de los enemigos", order: 61 },
  xp:          { fmt: "+{v}% de experiencia", order: 62 },
  spellDmg:    { fmt: "+{v}% de daño de los hechizos", order: 63 },
};

// ---------- item bases ----------
// kind "melee": your attack is a full dictation. kind "ranged": fill the gaps (faster, less damage).
// g: grammatical gender of the noun, so magic names agree ("Espada Afilada", "Machete Afilado").
const W = (id, name, g, icon, lvl, dmg, o = {}) => ({ id, name, g, icon, lvl, slot: "weapon", dmg, kind: "melee", sockets: 2, ...o });
export const BASES = [
  // melee weapons
  W("daga", "Daga", "f", "plain-dagger", 1, [2, 4], { req: { dex: 0 }, sockets: 1 }),
  W("garrote", "Garrote", "m", "spiked-mace", 3, [2, 7], { req: { str: 14 } }),
  W("lanza", "Lanza", "f", "barbed-spear", 7, [3, 10], { req: { str: 16, dex: 14 } }),
  W("machete", "Machete", "m", "machete", 2, [2, 6], { req: { str: 12 } }),
  W("garras", "Garras", "f", "claws", 4, [3, 6], { req: { dex: 18 }, sockets: 2 }),
  W("espada", "Espada", "f", "pointy-sword", 6, [4, 9], { req: { str: 18, dex: 12 } }),
  W("latigo", "Látigo", "m", "whip", 8, [3, 12], { req: { dex: 25 } }),
  W("estoque", "Estoque", "m", "pointy-sword", 12, [5, 12], { req: { dex: 34 } }),
  W("hacha", "Hacha", "f", "battle-axe", 10, [6, 12], { req: { str: 28 } }),
  W("maza", "Maza", "f", "spiked-mace", 13, [7, 15], { req: { str: 34 }, sockets: 2 }),
  W("mangual", "Mangual", "m", "flail", 16, [5, 22], { req: { str: 40, dex: 20 } }),
  W("pico", "Pico", "m", "war-axe", 18, [8, 18], { req: { str: 46 } }),
  W("espadon", "Espada ancha", "f", "broadsword", 20, [11, 20], { req: { str: 50, dex: 30 }, sockets: 3 }),
  W("lanzalarga", "Lanza larga", "f", "barbed-spear", 22, [14, 30], { req: { str: 50, dex: 45 }, twoHanded: true, sockets: 4 }),
  W("mandoble", "Mandoble", "m", "two-handed-sword", 24, [18, 34], { req: { str: 64, dex: 30 }, twoHanded: true, sockets: 4 }),
  W("martillo", "Martillo de guerra", "m", "warhammer", 27, [22, 38], { req: { str: 80 }, twoHanded: true, sockets: 4 }),
  W("alabarda", "Alabarda", "f", "halberd", 31, [20, 46], { req: { str: 75, dex: 45 }, twoHanded: true, sockets: 4 }),
  W("tridente", "Tridente", "m", "trident", 35, [24, 40], { req: { str: 70, dex: 60 }, sockets: 3 }),
  W("guadana", "Guadaña", "f", "scythe", 40, [30, 60], { req: { str: 95, dex: 60 }, twoHanded: true, sockets: 5 }),
  W("hachagrande", "Hacha de guerra", "f", "war-axe", 46, [26, 48], { req: { str: 110 }, sockets: 4 }),
  W("lanzadentada", "Lanza dentada", "f", "barbed-spear", 43, [28, 52], { req: { str: 90, dex: 80 }, twoHanded: true, sockets: 5 }),
  // ranged / caster weapons: fill-the-gaps attacks
  W("honda", "Honda", "f", "sling", 1, [1, 4], { kind: "ranged", req: {}, sockets: 1 }),
  W("varita", "Varita", "f", "crystal-wand", 5, [2, 6], { kind: "ranged", magic: true, req: { dex: 10 }, sockets: 1 }),
  W("arco", "Arco", "m", "bow-arrow", 9, [4, 9], { kind: "ranged", req: { dex: 28 }, twoHanded: true, sockets: 3 }),
  W("bumeran", "Bumerán", "m", "sling", 12, [4, 11], { kind: "ranged", req: { dex: 30 }, sockets: 2 }),
  W("baston", "Bastón", "m", "wizard-staff", 14, [5, 13], { kind: "ranged", magic: true, req: { str: 15, dex: 25 }, twoHanded: true, sockets: 3 }),
  W("cetro", "Cetro", "m", "crystal-wand", 18, [7, 16], { kind: "ranged", magic: true, req: { str: 10, dex: 35 }, sockets: 2 }),
  W("ballesta", "Ballesta", "f", "crossbow", 21, [10, 22], { kind: "ranged", req: { str: 40, dex: 45 }, twoHanded: true, sockets: 4 }),
  W("arcocurvo", "Arco recurvo", "m", "bow-arrow", 26, [11, 26], { kind: "ranged", req: { dex: 65 }, twoHanded: true, sockets: 4 }),
  W("arcolargo", "Arco largo", "m", "bow-arrow", 30, [13, 30], { kind: "ranged", req: { dex: 80 }, twoHanded: true, sockets: 4 }),
  W("varaanillada", "Vara anillada", "f", "wizard-staff", 33, [14, 30], { kind: "ranged", magic: true, req: { str: 25, dex: 70 }, twoHanded: true, sockets: 4 }),
  W("bastonruna", "Bastón de los páramos", "m", "wizard-staff", 38, [16, 34], { kind: "ranged", magic: true, req: { str: 30, dex: 70 }, twoHanded: true, sockets: 5 }),

  // off hand
  { id: "rodela", name: "Rodela", g: "f", icon: "viking-shield", lvl: 1, slot: "off", def: [3, 6], block: 15, req: { str: 10 }, sockets: 2 },
  { id: "escudomadera", name: "Escudo de madera", g: "m", icon: "round-shield", lvl: 4, slot: "off", def: [5, 9], block: 17, req: { str: 15 }, sockets: 2 },
  { id: "escudo", name: "Escudo", g: "m", icon: "round-shield", lvl: 8, def: [8, 14], slot: "off", block: 20, req: { str: 25 }, sockets: 3 },
  { id: "orbe", name: "Orbe", g: "m", icon: "crystal-ball", lvl: 10, def: [2, 5], slot: "off", block: 0, req: {}, sockets: 2, props: { mana: 10 } },
  { id: "escudotribal", name: "Escudo tribal", g: "m", icon: "tribal-shield", lvl: 18, def: [16, 26], slot: "off", block: 24, req: { str: 45 }, sockets: 3 },
  { id: "escudolargo", name: "Escudo largo", g: "m", icon: "bordered-shield", lvl: 24, def: [22, 34], slot: "off", block: 26, req: { str: 60 }, sockets: 3 },
  { id: "pavés", name: "Pavés", g: "m", icon: "bordered-shield", lvl: 30, def: [30, 46], slot: "off", block: 30, req: { str: 80 }, sockets: 4 },
  { id: "escudocruz", name: "Escudo cruzado", g: "m", icon: "bordered-shield", lvl: 40, def: [38, 56], slot: "off", block: 32, req: { str: 95 }, sockets: 4 },

  // head
  { id: "capucha", name: "Capucha", g: "f", icon: "hood", lvl: 1, slot: "head", def: [2, 4], req: {}, sockets: 2 },
  { id: "panoleta", name: "Pañoleta", g: "f", icon: "hood", lvl: 2, slot: "head", def: [2, 5], req: {}, sockets: 1 },
  { id: "sombrero", name: "Sombrero", g: "m", icon: "western-hat", lvl: 4, slot: "head", def: [4, 8], req: { str: 10 }, sockets: 2 },
  { id: "casco", name: "Casco", g: "m", icon: "light-helm", lvl: 10, slot: "head", def: [10, 16], req: { str: 26 }, sockets: 2 },
  { id: "tricornio", name: "Tricornio", g: "m", icon: "western-hat", lvl: 13, slot: "head", def: [10, 15], req: { str: 22 }, sockets: 2 },
  { id: "sombrerobrujo", name: "Sombrero de brujo", g: "m", icon: "western-hat", lvl: 20, slot: "head", def: [12, 18], req: {}, sockets: 2, props: { mana: 8 } },
  { id: "cascobarbaro", name: "Casco bárbaro", g: "m", icon: "light-helm", lvl: 22, slot: "head", def: [18, 28], req: { str: 48 }, sockets: 2 },
  { id: "mascara", name: "Máscara", g: "f", icon: "tribal-mask", lvl: 17, slot: "head", def: [14, 22], req: { str: 30 }, sockets: 3 },
  { id: "yelmo", name: "Yelmo", g: "m", icon: "heavy-helm", lvl: 26, slot: "head", def: [24, 36], req: { str: 60 }, sockets: 3 },
  { id: "yelmocornudo", name: "Yelmo cornudo", g: "m", icon: "heavy-helm", lvl: 32, slot: "head", def: [28, 40], req: { str: 70 }, sockets: 3 },
  { id: "corona", name: "Corona", g: "f", icon: "jewel-crown", lvl: 36, slot: "head", def: [30, 44], req: { str: 70 }, sockets: 3 },
  { id: "almete", name: "Almete", g: "m", icon: "heavy-helm", lvl: 42, slot: "head", def: [36, 52], req: { str: 90 }, sockets: 3 },

  // body
  { id: "tunica", name: "Túnica", g: "f", icon: "robe", lvl: 1, slot: "body", def: [3, 7], req: {}, sockets: 2 },
  { id: "ruana", name: "Ruana", g: "f", icon: "cloak", lvl: 3, slot: "body", def: [6, 11], req: { str: 10 }, sockets: 2 },
  { id: "chaqueta", name: "Chaqueta", g: "f", icon: "leather-vest", lvl: 5, slot: "body", def: [9, 15], req: { str: 14 }, sockets: 2 },
  { id: "jubon", name: "Jubón de cuero", g: "m", icon: "leather-vest", lvl: 9, slot: "body", def: [14, 22], req: { str: 22 }, sockets: 3 },
  { id: "gaban", name: "Gabán", g: "m", icon: "cloak", lvl: 13, slot: "body", def: [18, 28], req: { str: 30 }, sockets: 3 },
  { id: "cota", name: "Cota de malla", g: "f", icon: "chest-armor", lvl: 18, slot: "body", def: [28, 42], req: { str: 45 }, sockets: 3 },
  { id: "tabardo", name: "Tabardo", g: "m", icon: "robe", lvl: 23, slot: "body", def: [34, 50], req: { str: 55 }, sockets: 3 },
  { id: "coraza", name: "Coraza de púas", g: "f", icon: "spiked-armor", lvl: 30, slot: "body", def: [48, 70], req: { str: 80 }, sockets: 4 },
  { id: "lorica", name: "Lórica", g: "f", icon: "chest-armor", lvl: 38, slot: "body", def: [58, 84], req: { str: 95 }, sockets: 4 },

  // hands
  { id: "guantes", name: "Guantes", g: "m", icon: "gloves", lvl: 1, slot: "hands", def: [1, 3], req: {}, sockets: 0 },
  { id: "munequeras", name: "Muñequeras", g: "f", icon: "bracers", lvl: 6, slot: "hands", def: [3, 6], req: { str: 15 }, sockets: 0 },
  { id: "brazales", name: "Brazales", g: "m", icon: "bracers", lvl: 12, slot: "hands", def: [5, 9], req: { str: 25 }, sockets: 0 },
  { id: "guantescetrero", name: "Guantes de cetrero", g: "m", icon: "gloves", lvl: 18, slot: "hands", def: [7, 12], req: { str: 35 }, sockets: 0 },
  { id: "guanteletes", name: "Guanteletes", g: "m", icon: "gauntlet", lvl: 25, slot: "hands", def: [10, 16], req: { str: 55 }, sockets: 0 },

  // feet
  { id: "alpargatas", name: "Alpargatas", g: "f", icon: "sandal", lvl: 1, slot: "feet", def: [1, 3], req: {}, sockets: 0 },
  { id: "zapatos", name: "Zapatos", g: "m", icon: "leather-boot", lvl: 4, slot: "feet", def: [2, 5], req: { str: 10 }, sockets: 0 },
  { id: "botas", name: "Botas", g: "f", icon: "leather-boot", lvl: 8, slot: "feet", def: [4, 8], req: { str: 18 }, sockets: 0 },
  { id: "botasviaje", name: "Botas de viaje", g: "f", icon: "boots", lvl: 16, slot: "feet", def: [7, 12], req: { str: 30 }, sockets: 0 },
  { id: "botasmontar", name: "Botas de montar", g: "f", icon: "boots", lvl: 21, slot: "feet", def: [9, 14], req: { str: 40 }, sockets: 0 },
  { id: "grebas", name: "Botas de hierro", g: "f", icon: "metal-boot", lvl: 28, slot: "feet", def: [12, 18], req: { str: 60 }, sockets: 0 },
  { id: "botaspunta", name: "Botas de punta de hierro", g: "f", icon: "metal-boot", lvl: 38, slot: "feet", def: [16, 24], req: { str: 80 }, sockets: 0 },

  // belt
  { id: "faja", name: "Faja", g: "f", icon: "belt", lvl: 1, slot: "belt", def: [1, 2], req: {}, sockets: 0, props: { beltSlots: 2 } },
  { id: "cordon", name: "Cordón", g: "m", icon: "belt", lvl: 6, slot: "belt", def: [2, 4], req: { str: 12 }, sockets: 0, props: { beltSlots: 3 } },
  { id: "cinturon", name: "Cinturón", g: "m", icon: "belt", lvl: 12, slot: "belt", def: [3, 6], req: { str: 25 }, sockets: 0, props: { beltSlots: 4 } },
  { id: "fajin", name: "Fajín", g: "m", icon: "belt", lvl: 19, slot: "belt", def: [5, 9], req: { str: 35 }, sockets: 0, props: { beltSlots: 5 } },
  { id: "cinturonplacas", name: "Cinturón de placas", g: "m", icon: "belt-armor", lvl: 26, slot: "belt", def: [8, 12], req: { str: 50 }, sockets: 0, props: { beltSlots: 6 } },
  { id: "cinto", name: "Cinto de hebilla", g: "m", icon: "belt", lvl: 36, slot: "belt", def: [11, 16], req: { str: 70 }, sockets: 0, props: { beltSlots: 6 } },

  // jewellery: no defence, always at least magic
  { id: "collar", name: "Collar", g: "m", icon: "necklace", lvl: 1, slot: "neck", req: {}, sockets: 0, jewel: true },
  { id: "amuleto", name: "Amuleto", g: "m", icon: "gem-pendant", lvl: 1, slot: "neck", req: {}, sockets: 0, jewel: true },
  { id: "medallon", name: "Medallón", g: "m", icon: "gem-pendant", lvl: 1, slot: "neck", req: {}, sockets: 0, jewel: true },
  { id: "cadena", name: "Cadena", g: "f", icon: "necklace", lvl: 1, slot: "neck", req: {}, sockets: 0, jewel: true },
  { id: "anillo", name: "Anillo", g: "m", icon: "power-ring", lvl: 1, slot: "ring", req: {}, sockets: 0, jewel: true },
  { id: "sortija", name: "Sortija", g: "f", icon: "diamond-ring", lvl: 1, slot: "ring", req: {}, sockets: 0, jewel: true },
];
// Every base (but jewellery) also comes in a reinforced and an ancestral version: higher level,
// much better damage or defence, higher requirements, one more socket at the top.
export const TIERS = { 2: { name: "Excepcional", word: "reforzad@", lvl: 18 }, 3: { name: "De élite", word: "ancestral", lvl: 36 } };
for (const b of BASES.filter((x) => !x.jewel && !x.tier)) {
  for (const t of [2, 3]) {
    const k = t === 2 ? [1.7, 2, 1.8, 3, 1.3, 10] : [2.6, 5, 2.7, 8, 1.6, 25]; // dmg×, +dmg, def×, +def, req×, +req
    const req = Object.fromEntries(Object.entries(b.req || {}).map(([s, v]) => [s, Math.round(v * k[4] + (v || t === 3 ? k[5] : 0))]));
    BASES.push({
      ...b, id: `${b.id}_${t}`, root: b.id, tier: t,
      name: `${b.name} ${TIERS[t].word.replace(/@/g, b.g === "f" ? "a" : "o")}`,
      lvl: b.lvl + TIERS[t].lvl,
      dmg: b.dmg && [Math.round(b.dmg[0] * k[0] + k[1]), Math.round(b.dmg[1] * k[0] + k[1] + 1)],
      def: b.def && [Math.round(b.def[0] * k[2] + k[3]), Math.round(b.def[1] * k[2] + k[3])],
      block: b.block ? b.block + t * 2 : b.block,
      sockets: b.sockets ? Math.min(6, b.sockets + (t === 3 ? 1 : 0)) : 0,
      req,
    });
  }
}
// ---------- the high bands: new designs from level 50 to 130 ----------
// Every ten levels from 50, a material of its own, and a full kit in it: three weapons (one hand, two
// hands, bow or staff), a shield, helmet, armour, gloves, boots and belt. Each piece has a shape the
// ordinary bases don't use and is drawn wholly in its band's material (scripts/build_lpc.py: BAND_LOOKS,
// BAND_STOPS); rarity shows in the name and the glow. They have no reinforced or ancestral versions:
// the next band is the next step up. Their stats follow the best ordinary bases' curve, a little above.
export const BANDS = [
  { id: "obsidiana", lvl: 50, name: "Obsidiana", desc: "Vidrio de volcán, negro, con brasas en los filos." },
  { id: "hueso", lvl: 60, name: "Hueso", desc: "Tallado en los huesos de lo que vivía en el Abismo." },
  { id: "esmeralda", lvl: 70, name: "Esmeralda", desc: "Piedra verde de las minas de Muzo." },
  { id: "tumbaga", lvl: 80, name: "Tumbaga", desc: "Oro y cobre fundidos como los fundían los orfebres antiguos." },
  { id: "catatumbo", lvl: 90, name: "Catatumbo", desc: "Forjado bajo el relámpago que nunca para." },
  { id: "luna", lvl: 100, name: "Luna", desc: "Plata pálida que brilla de noche." },
  { id: "sombra", lvl: 110, name: "Sombra", desc: "Hecho de lo que hay en el fondo del Abismo." },
  { id: "astral", lvl: 120, name: "Astral", desc: "Polvo de estrellas, el último metal." },
];
{
  // average damage or defence per level, by kind of piece (the best ordinary bases, a little above)
  const PER = { melee1: 1.2, melee2: 1.68, ranged1: 0.68, ranged2: 1, off: 1.84, head: 1.68, body: 2.84, hands: 0.74, feet: 0.9, belt: 0.65 };
  const SOCK_OF = { melee1: 4, melee2: 6, ranged1: 4, ranged2: 5, off: 5, head: 4, body: 5 };
  const ICON = { off: "bordered-shield", head: "heavy-helm", body: "chest-armor", hands: "gauntlet", feet: "metal-boot", belt: "belt-armor" };
  // [band, kind, id, name, gender, icon, level within the band, extra]
  const K = (k, id, name, g, icon, at = 0, o = {}) => ({ k, id, name, g, icon, at, o });
  const KITS = {
    obsidiana: [K("melee1", "macana", "Macana", "f", "broadsword", 0), K("melee2", "hachaobsidiana", "Hacha de obsidiana", "f", "battle-axe", 4),
      K("ranged2", "arcoobsidiana", "Arco de obsidiana", "m", "bow-arrow", 2), K("off", "escudoobsidiana", "Escudo de obsidiana", "m", null, 3),
      K("head", "yelmoobsidiana", "Yelmo de obsidiana", "m", null, 1), K("body", "corazaobsidiana", "Coraza de obsidiana", "f", null, 5),
      K("hands", "guantesobsidiana", "Guanteletes de obsidiana", "m", null, 2), K("feet", "grebasobsidiana", "Grebas de obsidiana", "f", null, 3),
      K("belt", "cintoobsidiana", "Cinto de obsidiana", "m", null, 6)],
    hueso: [K("melee1", "sablehueso", "Sable de hueso", "m", "machete", 0), K("melee2", "guadanahueso", "Guadaña de hueso", "f", "scythe", 4),
      K("ranged1", "varahueso", "Vara de hueso", "f", "crystal-wand", 2, { magic: true }), K("off", "escudohueso", "Escudo de hueso", "m", null, 3),
      K("head", "yelmohueso", "Yelmo de hueso", "m", null, 1), K("body", "petohueso", "Peto de hueso", "m", null, 5),
      K("hands", "brazaleshueso", "Brazales de hueso", "m", null, 2), K("feet", "botashueso", "Botas de hueso", "f", null, 3),
      K("belt", "cinturonhueso", "Cinturón de hueso", "m", null, 6)],
    esmeralda: [K("melee1", "estoqueesmeralda", "Estoque de esmeralda", "m", "pointy-sword", 0, { dexy: true }), K("melee2", "alabardaesmeralda", "Alabarda de esmeralda", "f", "halberd", 4),
      K("ranged1", "cetroesmeralda", "Cetro de esmeralda", "m", "crystal-wand", 2, { magic: true }), K("off", "escudoesmeralda", "Escudo de esmeralda", "m", null, 3),
      K("head", "yelmoesmeralda", "Yelmo de esmeralda", "m", null, 1), K("body", "cotaesmeralda", "Cota de esmeralda", "f", null, 5),
      K("hands", "guantesesmeralda", "Guantes de esmeralda", "m", null, 2), K("feet", "zapatosesmeralda", "Zapatos de esmeralda", "m", null, 3),
      K("belt", "fajaesmeralda", "Faja de esmeralda", "f", null, 6)],
    tumbaga: [K("melee1", "mazatumbaga", "Maza de tumbaga", "f", "spiked-mace", 0), K("melee2", "lanzatumbaga", "Lanza de tumbaga", "f", "barbed-spear", 4),
      K("ranged2", "baculotumbaga", "Báculo de tumbaga", "m", "wizard-staff", 2, { magic: true }), K("off", "rodelatumbaga", "Rodela de tumbaga", "f", null, 3),
      K("head", "yelmotumbaga", "Yelmo de tumbaga", "m", null, 1), K("body", "corazatumbaga", "Coraza de tumbaga", "f", null, 5),
      K("hands", "guantestumbaga", "Guanteletes de tumbaga", "m", null, 2), K("feet", "grebastumbaga", "Grebas de tumbaga", "f", null, 3),
      K("belt", "cintotumbaga", "Cinto de tumbaga", "m", null, 6)],
    catatumbo: [K("melee1", "espadacatatumbo", "Espada del Catatumbo", "f", "pointy-sword", 0), K("melee2", "martillocatatumbo", "Martillo del Catatumbo", "m", "warhammer", 4),
      K("ranged2", "ballestacatatumbo", "Ballesta del Catatumbo", "f", "crossbow", 2), K("off", "escudocatatumbo", "Escudo del Catatumbo", "m", null, 3),
      K("head", "yelmocatatumbo", "Yelmo del Catatumbo", "m", null, 1), K("body", "corazacatatumbo", "Coraza del Catatumbo", "f", null, 5),
      K("hands", "guantescatatumbo", "Guantes del Catatumbo", "m", null, 2), K("feet", "botascatatumbo", "Botas del Catatumbo", "f", null, 3),
      K("belt", "cintocatatumbo", "Cinto del Catatumbo", "m", null, 6)],
    luna: [K("melee1", "sableluna", "Sable de luna", "m", "machete", 0, { dexy: true }), K("melee2", "tridenteluna", "Tridente de luna", "m", "trident", 4),
      K("ranged2", "arcoluna", "Arco de luna", "m", "bow-arrow", 2), K("off", "rodelaluna", "Rodela de luna", "f", null, 3),
      K("head", "yelmoluna", "Yelmo de luna", "m", null, 1), K("body", "mantoluna", "Manto de luna", "m", null, 5),
      K("hands", "brazalesluna", "Brazales de luna", "m", null, 2), K("feet", "zapatosluna", "Zapatos de luna", "m", null, 3),
      K("belt", "cordonluna", "Cordón de luna", "m", null, 6)],
    sombra: [K("melee1", "mangualsombra", "Mangual de sombra", "m", "flail", 0), K("melee2", "mandoblesombra", "Mandoble de sombra", "m", "two-handed-sword", 4),
      K("ranged2", "varasombra", "Vara de sombra", "f", "wizard-staff", 2, { magic: true }), K("off", "escudosombra", "Escudo de sombra", "m", null, 3),
      K("head", "yelmosombra", "Yelmo de sombra", "m", null, 1), K("body", "corazasombra", "Coraza de sombra", "f", null, 5),
      K("hands", "guantessombra", "Guanteletes de sombra", "m", null, 2), K("feet", "pezunassombra", "Pezuñas de sombra", "f", null, 3),
      K("belt", "cintosombra", "Cinto de sombra", "m", null, 6)],
    astral: [K("melee1", "espadaastral", "Espada astral", "f", "broadsword", 0), K("melee2", "lanzaastral", "Lanza astral", "f", "barbed-spear", 4),
      K("ranged2", "arcoastral", "Arco astral", "m", "bow-arrow", 2), K("off", "escudoastral", "Escudo astral", "m", null, 3),
      K("head", "capiroteastral", "Capirote astral", "m", null, 1, { mana: true }), K("body", "vestiduraastral", "Vestidura astral", "f", null, 5),
      K("hands", "guantesastral", "Guantes astrales", "m", null, 2), K("feet", "zapatillasastral", "Zapatillas astrales", "f", null, 3),
      K("belt", "fajinastral", "Fajín astral", "m", null, 6)],
  };
  BANDS.forEach((band, bi) => {
    for (const p of KITS[band.id]) {
      const L = band.lvl + p.at, avg = PER[p.k] * L;
      const r = (x) => Math.max(1, Math.round(x));
      const strReq = r(1.9 * L + 30);
      const b = { id: p.id, name: p.name, g: p.g, icon: p.icon || ICON[p.k], lvl: L, band: band.id, sockets: SOCK_OF[p.k] || 0 };
      if (p.k.startsWith("melee") || p.k.startsWith("ranged")) {
        Object.assign(b, { slot: "weapon", kind: p.k.startsWith("melee") ? "melee" : "ranged", dmg: [r(avg * 0.65), r(avg * 1.35)] });
        if (p.k.endsWith("2")) b.twoHanded = true;
        if (p.o.magic) Object.assign(b, { magic: true, req: { str: r(0.3 * strReq), dex: r(0.85 * strReq) } });
        else if (p.k.startsWith("ranged") || p.o.dexy) b.req = { dex: strReq };
        else b.req = { str: strReq, dex: r(0.55 * strReq) };
      } else {
        Object.assign(b, { slot: p.k, def: [r(avg * 0.85), r(avg * 1.15)], req: { str: r(strReq * (p.k === "body" || p.k === "off" ? 1 : 0.85)) } });
        if (p.k === "off") b.block = Math.min(40, 34 + Math.floor(bi / 2));
        if (p.k === "belt") b.props = { beltSlots: 6 };
        if (p.o.mana) { b.props = { mana: 10 + 2 * bi }; b.req = { str: r(strReq * 0.5) }; }
      }
      BASES.push(b);
    }
  });
}
export const BASE = Object.fromEntries(BASES.map((b) => [b.id, b]));
// A set's magic undershirt (melted from the whole set at the alembic): its own slot, never dropped,
// sold or made any other way, so it's kept out of BASES.
BASE.camiseta = { id: "camiseta", name: "Camiseta encantada", g: "f", icon: "leather-vest", lvl: 1, slot: "shirt", req: {}, sockets: 0, jewel: true };

// ---------- affixes ----------
// pre: adjective after the noun, with "@" for the gendered ending ("Afilad@" -> Afilado/Afilada).
// suf: "del Toro" etc. Tiers: [minLevel, min, max]. slots: where it can roll ("armor" = head/body/hands/feet/belt/off).
const ARMOR = ["head", "body", "hands", "feet", "belt", "off"];
const JEWEL = ["neck", "ring"];
const ALL = ["weapon", ...ARMOR, ...JEWEL];
export const PREFIXES = [
  { name: "Afilad@", prop: "dmgPct", slots: ["weapon"], tiers: [[1, 10, 20], [9, 21, 40], [20, 41, 65], [34, 66, 100]] },
  { name: "Cruel", prop: "dmgMax", slots: ["weapon", "ring", "hands"], tiers: [[1, 1, 3], [12, 4, 8], [26, 9, 15]] },
  { name: "Pesad@", prop: "dmgMin", slots: ["weapon", "ring"], tiers: [[3, 1, 2], [14, 3, 6], [28, 7, 10]] },
  { name: "Ardiente", prop: "fire", slots: ["weapon", "ring", "hands"], tiers: [[2, 1, 4], [12, 5, 10], [25, 11, 22]] },
  { name: "Helad@", prop: "cold", slots: ["weapon", "ring", "hands"], tiers: [[2, 1, 4], [12, 5, 10], [25, 11, 22]] },
  { name: "Chispeante", prop: "light", slots: ["weapon", "ring", "neck"], tiers: [[4, 1, 6], [14, 4, 14], [28, 8, 28]] },
  { name: "Venenos@", prop: "poison", slots: ["weapon", "hands"], tiers: [[4, 2, 5], [14, 6, 12], [28, 13, 24]] },
  { name: "Erudit@", prop: "dmgDictation", slots: ["weapon", "head", "neck"], tiers: [[5, 10, 20], [18, 21, 35], [32, 36, 50]] },
  { name: "Certer@", prop: "dmgCloze", slots: ["weapon", "hands", "neck"], tiers: [[5, 10, 20], [18, 21, 35], [32, 36, 50]] },
  { name: "Implacable", prop: "crit", slots: ["weapon", "hands", "ring"], tiers: [[6, 2, 4], [20, 5, 8]] },
  { name: "Resistente", prop: "armorPct", slots: ARMOR, tiers: [[1, 10, 20], [10, 21, 40], [22, 41, 65], [36, 66, 90]] },
  { name: "Reforzad@", prop: "armor", slots: ARMOR, tiers: [[1, 2, 6], [12, 7, 15], [26, 16, 30]] },
  { name: "Azulad@", prop: "mana", slots: ["head", "off", "neck", "ring", "weapon"], tiers: [[1, 5, 10], [10, 11, 20], [24, 21, 35]] },
  { name: "Ignífug@", prop: "resFire", slots: [...ARMOR, ...JEWEL], tiers: [[2, 8, 15], [14, 16, 25], [28, 26, 35]] },
  { name: "Abrigad@", prop: "resCold", slots: [...ARMOR, ...JEWEL], tiers: [[2, 8, 15], [14, 16, 25], [28, 26, 35]] },
  { name: "Aislad@", prop: "resLight", slots: [...ARMOR, ...JEWEL], tiers: [[2, 8, 15], [14, 16, 25], [28, 26, 35]] },
  { name: "Purificad@", prop: "resPoison", slots: [...ARMOR, ...JEWEL], tiers: [[2, 8, 15], [14, 16, 25], [28, 26, 35]] },
  { name: "Prismátic@", prop: "resAll", slots: ["off", "neck", "ring", "body"], tiers: [[12, 5, 10], [26, 11, 20]] },
  { name: "Afortunad@", prop: "mf", slots: ["head", "neck", "ring", "feet", "hands"], tiers: [[3, 5, 12], [16, 13, 25]] },
  { name: "Atent@", prop: "replayCost", slots: ["head", "neck", "ring"], tiers: [[3, 10, 20], [16, 21, 35], [30, 36, 50]] },
  { name: "Sabi@", prop: "hintCost", slots: ["head", "neck", "off"], tiers: [[3, 15, 30], [18, 31, 50]] },
  { name: "Firme", prop: "block", slots: ["off"], tiers: [[4, 4, 8], [20, 9, 14]] },
];
export const SUFFIXES = [
  { name: "del Toro", prop: "str", slots: ALL, tiers: [[1, 1, 3], [8, 4, 7], [18, 8, 12], [32, 13, 20]] },
  { name: "del Colibrí", prop: "dex", slots: ALL, tiers: [[1, 1, 3], [8, 4, 7], [18, 8, 12], [32, 13, 20]] },
  { name: "de la Ceiba", prop: "vit", slots: ALL, tiers: [[1, 1, 3], [8, 4, 7], [18, 8, 12], [32, 13, 20]] },
  { name: "del Búho", prop: "ene", slots: ALL, tiers: [[1, 1, 3], [8, 4, 7], [18, 8, 12], [32, 13, 20]] },
  { name: "del Oso", prop: "life", slots: [...ARMOR, ...JEWEL], tiers: [[1, 4, 10], [10, 11, 25], [24, 26, 45], [38, 46, 70]] },
  { name: "del Manantial", prop: "lifeRegen", slots: [...ARMOR, ...JEWEL], tiers: [[4, 1, 2], [18, 3, 5]] },
  { name: "de la Lluvia", prop: "manaRegen", slots: [...ARMOR, ...JEWEL, "weapon"], tiers: [[4, 1, 2], [18, 3, 4]] },
  { name: "del Murciélago", prop: "leech", slots: ["weapon", "ring", "neck", "hands"], tiers: [[6, 2, 4], [20, 5, 8]] },
  { name: "de la Polilla", prop: "manaLeech", slots: ["weapon", "ring", "neck", "hands"], tiers: [[6, 2, 4], [20, 5, 7]] },
  { name: "de la Guaca", prop: "gf", slots: [...ARMOR, ...JEWEL], tiers: [[1, 15, 40], [16, 41, 80]] },
  { name: "de la Suerte", prop: "mf", slots: [...ARMOR, ...JEWEL], tiers: [[4, 5, 12], [18, 13, 22]] },
  { name: "del Maestro", prop: "xp", slots: ["neck", "ring", "head"], tiers: [[8, 3, 6], [24, 7, 10]] },
  { name: "del Cactus", prop: "thorns", slots: ["body", "off", "hands"], tiers: [[2, 1, 4], [14, 5, 12], [28, 13, 25]] },
  { name: "del Venado", prop: "dodge", slots: ["feet", "body", "hands"], tiers: [[5, 2, 4], [20, 5, 8]] },
  { name: "del Chamán", prop: "killHeal", slots: ["weapon", "hands", "head"], tiers: [[3, 1, 4], [16, 5, 10], [30, 11, 18]] },
  { name: "del Herbolario", prop: "potion", slots: ["belt", "neck", "body"], tiers: [[2, 10, 25], [16, 26, 50]] },
  { name: "del Eco", prop: "freeReplay", slots: ["head", "neck"], tiers: [[12, 1, 1]] },
  { name: "de la Tormenta", prop: "crit", slots: ["weapon", "neck"], tiers: [[10, 2, 4], [26, 5, 7]] },
];

// Rare names: "<noun> <phrase>", e.g. "Colmillo de Ceniza".
export const RARE_A = ["Colmillo", "Grito", "Susurro", "Furia", "Sombra", "Raíz", "Llama", "Lamento", "Garra", "Pluma", "Ojo", "Mordida", "Promesa", "Plegaria", "Ruina", "Eco", "Espina", "Brasa", "Tormenta", "Ceniza", "Niebla", "Herida", "Canto", "Hueso"];
export const RARE_B = ["de Ceniza", "del Páramo", "de la Ciénaga", "del Llano", "de Obsidiana", "del Abismo", "de Niebla", "del Cóndor", "de la Luna", "del Jaguar", "de Sangre", "del Trueno", "de la Selva", "de Cuarzo", "del Río", "de Fuego", "de Hielo", "del Olvido", "de la Montaña", "del Ocaso"];

// ---------- uniques ----------
// Fixed properties; [min,max] values roll when found.
export const UNIQUES = [
  { name: "Mordisco de Tigrillo", base: "daga", lvl: 3, props: { dmgPct: [40, 60], dex: 5, crit: 5, leech: 4 }, flavor: "Pequeña, rápida y con mal genio." },
  { name: "El Desyerbador", base: "machete", lvl: 4, props: { dmgPct: [50, 80], str: 6, killHeal: 4, dmgDictation: 15 }, flavor: "Abrió trochas donde no había camino." },
  { name: "Honda de Pastorcito", base: "honda", lvl: 3, props: { dmgPct: [50, 70], dmgCloze: 25, mf: 15 }, flavor: "Para espantar al lobo, y a veces al cura." },
  { name: "Capucha del Monaguillo", base: "capucha", lvl: 5, props: { armorPct: [60, 90], replayCost: 30, mana: 15, xp: 5 }, flavor: "Escuchaba la misa entera sin perder palabra." },
  { name: "Ruana de la Abuela", base: "ruana", lvl: 6, props: { armorPct: [80, 110], life: 25, resCold: 30, lifeRegen: 2 }, flavor: "Huele a tinto y a leña." },
  { name: "Alpargatas del Peregrino", base: "alpargatas", lvl: 7, props: { armorPct: [40, 60], dodge: 6, vit: 6, gf: 40 }, flavor: "Llegaron caminando a Monserrate tres veces." },
  { name: "Varita de Guadua", base: "varita", lvl: 8, props: { dmgPct: [60, 90], dmgCloze: 30, manaRegen: 2, hintCost: 40 }, flavor: "Crece medio metro por noche." },
  { name: "Faja del Trapiche", base: "faja", lvl: 9, props: { beltSlots: 2, potion: 40, str: 6, life: 15 }, flavor: "Huele a panela." },
  { name: "Sombrero de Doce Vueltas", base: "sombrero", lvl: 10, props: { armorPct: [70, 100], freeReplay: 1, resAll: 10, dex: 8 }, flavor: "Cada vuelta, una historia que alguien escuchó bien." },
  { name: "Anillo del Guaquero", base: "anillo", lvl: 11, props: { mf: [25, 40], gf: [60, 100], allStats: 3 }, flavor: "Siempre sabe dónde está enterrado el oro." },
  { name: "Látigo del Arriero Bravo", base: "latigo", lvl: 12, props: { dmgPct: [80, 120], light: 12, str: 8, comboStart: 2 }, flavor: "Restalla como trueno en la loma." },
  { name: "Guantes del Escribano", base: "guantes", lvl: 13, props: { armorPct: [50, 80], dmgDictation: 30, typoTol: 1, dex: 6 }, flavor: "Sus dedos corrían más que la lengua del notario." },
  { name: "Hacha del Leñador Sordo", base: "hacha", lvl: 14, props: { dmgPct: [100, 140], dmgMax: 10, crit: 6, mana: -10 }, flavor: "No oía nada, así que golpeaba más fuerte." },
  { name: "Arco de la Cazadora", base: "arco", lvl: 15, props: { dmgPct: [90, 130], dmgCloze: 35, dex: 12, crit: 5 }, flavor: "Nunca falló un blanco que no quisiera fallar." },
  { name: "Collar de Chaquiras", base: "collar", lvl: 16, props: { resAll: [15, 25], mana: 25, manaRegen: 2, hintCost: 30 }, flavor: "Cada cuenta, una palabra aprendida." },
  { name: "Máscara del Carnaval", base: "mascara", lvl: 18, props: { armorPct: [90, 130], allStats: 6, dodge: 6, comboKeep: true }, flavor: "Detrás de ella, nadie se ríe de tus errores." },
  { name: "Maza del Cacique", base: "maza", lvl: 19, props: { dmgPct: [110, 150], fire: 18, killHeal: 8, str: 10 }, flavor: "Pesa lo que pesa la palabra dada." },
  { name: "Botas del Cartero", base: "botasviaje", lvl: 20, props: { armorPct: [60, 90], dodge: 8, freeReplay: 1, gf: 50 }, flavor: "Ninguna carta se quedó sin entregar." },
  { name: "Jubón del Contrabandista", base: "jubon", lvl: 21, props: { armorPct: [100, 140], dodge: 8, mf: 25, thorns: 10 }, flavor: "Tiene más bolsillos de los que se ven." },
  { name: "Orbe del Oráculo", base: "orbe", lvl: 22, props: { mana: [30, 45], replayCost: 40, slowFree: true, ene: 10 }, flavor: "Lo escucha todo dos veces, y la segunda más despacio." },
  { name: "Mandoble del Juramento", base: "mandoble", lvl: 26, props: { dmgPct: [150, 200], dmgDictation: 40, leech: 6, vit: 12 }, flavor: "Lo que se dice frente a él, se cumple." },
  { name: "Oído de la Montaña", base: "casco", lvl: 27, props: { armorPct: [100, 140], nearExact: true, life: 30, resAll: 15 }, flavor: "Oye el río aunque el río susurre." },
  { name: "Sortija de la Novia Triste", base: "sortija", lvl: 28, props: { life: [30, 45], manaLeech: 5, resCold: 30, xp: 8 }, flavor: "Fría como la noche en que la dejaron esperando." },
  { name: "Ballesta del Centinela", base: "ballesta", lvl: 30, props: { dmgPct: [140, 190], dmgCloze: 40, cold: 20, crit: 8 }, flavor: "No dormía. No parpadeaba. No fallaba." },
  { name: "Pavés de la Muralla", base: "pavés", lvl: 32, props: { armorPct: [130, 170], block: 15, resAll: 25, thorns: 25 }, flavor: "Cartagena aguantó. Este escudo también." },
  { name: "Coraza del Volcán", base: "coraza", lvl: 34, props: { armorPct: [140, 190], resFire: 50, fire: 20, life: 60, str: 15 }, flavor: "Todavía está tibia." },
  { name: "Guadaña de la Llorona", base: "guadana", lvl: 40, props: { dmgPct: [180, 240], cold: 40, leech: 8, freeReplay: 1, comboStart: 3 }, flavor: "Corta el silencio en dos." },
  { name: "La Mocha", base: "espada", lvl: 9, props: { dmgPct: [70, 100], crit: 6, dex: 6, dmgDictation: 15 }, flavor: "Le falta la punta. No le falta nada más." },
  { name: "Uñas del Mohán", base: "garras", lvl: 12, props: { dmgPct: [80, 110], poison: 12, leech: 5, dodge: 5 }, flavor: "Las encontraron en la orilla, todavía mojadas." },
  { name: "Campanario de Mompox", base: "mangual", lvl: 20, props: { dmgPct: [110, 150], light: 20, thorns: 10, comboStart: 2 }, flavor: "Suena a las seis aunque nadie lo toque." },
  { name: "Espada del Libertador Cansado", base: "espadon", lvl: 23, props: { dmgPct: [120, 160], allStats: 5, resAll: 10, dmgDictation: 25 }, flavor: "Cruzó los Andes. Ahora quiere dormir." },
  { name: "Mazo del Trapiche", base: "martillo", lvl: 29, props: { dmgPct: [140, 180], str: 12, killHeal: 10, potion: 30 }, flavor: "Muele caña, muele huesos." },
  { name: "Guardia del Virrey", base: "alabarda", lvl: 33, props: { dmgPct: [140, 190], armorPct: 30, block: 8, resAll: 15 }, flavor: "Defendió a quien no lo merecía." },
  { name: "Arpón de Taganga", base: "tridente", lvl: 36, props: { dmgPct: [150, 200], cold: 25, dex: 12, dmgCloze: 30 }, flavor: "Nunca sale del agua con las manos vacías." },
  { name: "Hacha del Pirata Ciego", base: "hachagrande", lvl: 47, props: { dmgPct: [180, 240], dmgMax: 20, leech: 7, crit: 8 }, flavor: "Saqueó Cartagena. Dos veces." },
  { name: "Bastón del Taita", base: "baston", lvl: 16, props: { dmgPct: [80, 120], mana: 30, manaRegen: 3, hintCost: 30, dmgCloze: 20 }, flavor: "Huele a yagé y a madrugada." },
  { name: "Arco del Último Muisca", base: "arcolargo", lvl: 32, props: { dmgPct: [150, 200], dmgCloze: 40, crit: 10, gf: 60 }, flavor: "Apunta siempre hacia la laguna." },
  // bows for the long road: reinforced and elite bases, so they keep up with the Abismo
  { name: "Arco del Pescador de Luna", base: "arco_2", lvl: 27, props: { dmgPct: [120, 160], cold: 20, dmgCloze: 35, mf: [15, 25] }, flavor: "Pescaba reflejos en el Magdalena, y nunca volvió sin uno." },
  { name: "Arco de la Madremonte", base: "arcocurvo", lvl: 29, props: { dmgPct: [150, 200], poison: 25, dmgCloze: 40, dodge: 8, leech: 5 }, flavor: "El monte entero apunta contigo." },
  { name: "Arco de Bochica", base: "arcocurvo_2", lvl: 44, props: { dmgPct: [190, 250], light: 45, crit: 12, dmgCloze: 50, comboStart: 3 }, flavor: "Abrió el Tequendama de un flechazo, y el agua le dio las gracias." },
  { name: "Arco de las Siete Lunas", base: "arco_3", lvl: 46, props: { dmgPct: [190, 240], cold: 25, fire: 25, light: 25, dmgCloze: 45, mf: [25, 40] }, flavor: "Una luna por cada noche que la cazadora no durmió." },
  { name: "El Vigía del Páramo", base: "arcolargo_2", lvl: 49, props: { dmgPct: [200, 260], cold: 40, crit: 12, nearExact: true, freeReplay: 1 }, flavor: "Ve venir la niebla tres días antes." },
  { name: "La Flecha que Vuelve", base: "arcocurvo_3", lvl: 62, props: { dmgPct: [230, 300], dmgCloze: 65, leech: 8, comboKeep: true, allStats: [8, 12] }, flavor: "Siempre regresa a la mano que la entendió." },
  { name: "Báculo del Páramo Eterno", base: "bastonruna", lvl: 41, props: { dmgPct: [170, 220], cold: 35, freeReplay: 1, replayCost: 30, ene: 15 }, flavor: "Ahí arriba el tiempo se congela." },
  { name: "Rodela del Cimarrón", base: "rodela", lvl: 6, props: { armorPct: [60, 90], block: 8, dodge: 5, life: 20 }, flavor: "Hecha a escondidas, de noche." },
  { name: "Escudo de San Jorge", base: "escudo", lvl: 15, props: { armorPct: [80, 110], resFire: 40, thorns: 12, vit: 8 }, flavor: "El dragón no lo cuenta." },
  { name: "Caparazón de Morrocoy", base: "escudotribal", lvl: 24, props: { armorPct: [100, 140], block: 10, resAll: 15, lifeRegen: 3 }, flavor: "Lento pero llega." },
  { name: "Yelmo del Conquistador Perdido", base: "yelmo", lvl: 30, props: { armorPct: [110, 150], mf: 30, str: 10, resLight: 30 }, flavor: "Buscaba El Dorado. Encontró la ciénaga." },
  { name: "Túnica de la Monja Alférez", base: "tunica", lvl: 8, props: { armorPct: [60, 90], dex: 8, dodge: 6, comboStart: 1 }, flavor: "Nadie sospechó nada en veinte años." },
  { name: "Cota del Fraile Guerrero", base: "cota", lvl: 22, props: { armorPct: [100, 140], life: 40, resAll: 15, xp: 5 }, flavor: "Rezaba con una mano." },
  { name: "Brazales de la Tejedora", base: "brazales", lvl: 17, props: { armorPct: [60, 90], dex: 8, typoTol: 1, dmgDictation: 15 }, flavor: "Ni una puntada torcida." },
  { name: "Guanteletes del Capataz", base: "guanteletes", lvl: 28, props: { armorPct: [90, 120], str: 12, crit: 5, killHeal: 6 }, flavor: "Se los quitaron entre todos." },
  { name: "Botas de Siete Leguas", base: "botas", lvl: 11, props: { armorPct: [50, 80], dodge: 10, dex: 6, freeReplay: 1 }, flavor: "Llegas antes de salir." },
  { name: "Grebas del Puente de Boyacá", base: "grebas", lvl: 31, props: { armorPct: [100, 140], vit: 12, resAll: 15, block: 5 }, flavor: "Nadie pasó por encima de ellas." },
  { name: "Cinturón del Contrabando", base: "cinturon", lvl: 14, props: { beltSlots: 2, gf: 60, mf: 15, dex: 5 }, flavor: "Lleva más de lo que declara." },
  { name: "Cincha del Caballo de Bolívar", base: "cinturonplacas", lvl: 30, props: { beltSlots: 2, str: 12, life: 40, potion: 40 }, flavor: "Blanco, como en la pregunta." },
  { name: "Amuleto de la Lechuza", base: "amuleto", lvl: 19, props: { allStats: 6, nearExact: true, resAll: 15, xp: 6 }, flavor: "Ve de noche lo que tú no oyes de día." },
  { name: "Corona del Dorado", base: "corona", lvl: 44, props: { armorPct: [120, 160], allStats: 15, mf: 50, gf: 120, freeReplay: 1 }, flavor: "La laguna nunca la devolvió. Hasta ahora." },
];

// ---------- crafting (alembic): magic item + gem + any potion -> artesanal ----------
// The gem decides the family; its grade, how strong the fixed properties are.
export const CRAFT = {
  rubi:      { name: "de sangre",   props: { leech: [[2, 3], [3, 5], [5, 7]], life: [[10, 20], [20, 35], [35, 55]] } },
  zafiro:    { name: "de brujo",    props: { mana: [[10, 20], [20, 35], [35, 55]], manaRegen: [[1, 1], [1, 2], [2, 3]] } },
  esmeralda: { name: "de guardián", props: { resAll: [[5, 8], [8, 12], [12, 18]], armorPct: [[15, 30], [30, 50], [50, 80]] } },
  amatista:  { name: "de golpe",    props: { dmgPct: [[15, 30], [30, 50], [50, 80]], crit: [[2, 3], [3, 4], [4, 6]] } },
  topacio:   { name: "de fortuna",  props: { mf: [[10, 20], [20, 30], [30, 45]], gf: [[20, 40], [40, 70], [70, 100]] } },
  diamante:  { name: "de oído",     props: { replayCost: [[8, 12], [12, 18], [18, 25]], hintCost: [[8, 15], [15, 25], [25, 35]] } },
};

// ---------- runas (the new runes) ----------
// Stones cut with Muisca words: numbers for the common ones, the land for the middle ones, its gods for the
// high ones. One goes in a socket like a gem (kind "runa", in it.gems as { runa: id }) and gives what it
// gives in that kind of item: w in a weapon, a in armour (head, torso, hands, feet, belt), o in a shield.
// A runa asks for its level: the item needs at least that level to be worn.
// tier: comun / media / alta. They drop rarely (RUNA_CHANCE in engine.js), the high ones very rarely, and
// 3 of the same in the alembic make the next one up (never into the last).
export const RUNA_TIERS = {
  comun: { name: "Runa común", color: "#c9c0ad", weight: 1 },
  media: { name: "Runa media", color: "#e0a640", weight: 0.15 },
  alta:  { name: "Runa alta",  color: "#a98bff", weight: 0.004 },
};
const RN = (id, name, tier, lvl, w, a, o, gloss) => ({ id, name, tier, lvl, w, a, o, gloss });
export const RUNAS = [
  RN("ata", "Ata", "comun", 1, ["dmgMax", 3], ["armor", 8], ["block", 3], "uno"),
  RN("bosa", "Bosa", "comun", 3, ["dmgMin", 2], ["life", 12], ["armor", 12], "dos"),
  RN("mica", "Mica", "comun", 6, ["fire", 6], ["resFire", 12], ["resFire", 15], "tres"),
  RN("muyhica", "Muyhica", "comun", 9, ["cold", 6], ["resCold", 12], ["resCold", 15], "cuatro"),
  RN("hisca", "Hisca", "comun", 12, ["light", 8], ["resLight", 12], ["resLight", 15], "cinco"),
  RN("ta", "Ta", "comun", 15, ["poison", 8], ["resPoison", 12], ["resPoison", 15], "seis"),
  RN("cuhupcua", "Cuhupcua", "media", 20, ["dmgPct", 25], ["armorPct", 25], ["armorPct", 30], "siete"),
  RN("suhuza", "Suhuza", "media", 24, ["crit", 3], ["dex", 7], ["dodge", 3], "ocho"),
  RN("aca", "Aca", "media", 28, ["leech", 3], ["vit", 7], ["life", 30], "nueve"),
  RN("ubchihica", "Ubchihica", "media", 32, ["manaLeech", 3], ["ene", 7], ["mana", 30], "diez"),
  RN("sie", "Sie", "media", 35, ["cold", 16], ["manaRegen", 2], ["resCold", 25], "agua"),
  RN("fiba", "Fiba", "media", 38, ["dmgCloze", 20], ["dodge", 3], ["block", 6], "aire"),
  RN("gata", "Gata", "media", 41, ["fire", 18], ["lifeRegen", 3], ["resFire", 25], "fuego"),
  RN("hyca", "Hyca", "media", 44, ["dmgDictation", 20], ["str", 7], ["thorns", 12], "piedra"),
  RN("quyca", "Quyca", "media", 47, ["killHeal", 6], ["gf", 40], ["resAll", 8], "tierra"),
  RN("zipa", "Zipa", "media", 50, ["dmgPct", 40], ["mf", 15], ["armorPct", 45], "el señor de Bacatá"),
  RN("sue", "Sué", "alta", 55, ["dmgPct", 60], ["armorPct", 60], ["armorPct", 70], "el sol"),
  RN("chia", "Chía", "alta", 58, ["crit", 5], ["manaRegen", 4], ["mana", 60], "la luna"),
  RN("bachue", "Bachué", "alta", 61, ["leech", 6], ["life", 60], ["life", 75], "la madre que salió de la laguna"),
  RN("bochica", "Bochica", "alta", 64, ["dmgDictation", 35], ["replayCost", 25], ["hintCost", 30], "el que enseñó a hilar"),
  RN("nencatacoa", "Nencatacoa", "alta", 67, ["dmgCloze", 35], ["allStats", 6], ["allStats", 8], "el de las fiestas"),
  RN("huitaca", "Huitaca", "alta", 70, ["manaLeech", 6], ["mf", 30], ["dodge", 6], "la rebelde"),
  RN("chibchacum", "Chibchacum", "alta", 74, ["dmgMin", 12], ["str", 15], ["block", 12], "el que carga la tierra"),
  RN("guahaioque", "Guahaioque", "alta", 78, ["killHeal", 15], ["resAll", 18], ["resAll", 22], "el de la muerte"),
  RN("chaquen", "Chaquén", "alta", 83, ["crit", 8], ["dex", 15], ["thorns", 30], "el guardián de los linderos"),
  RN("chiminigagua", "Chiminigagua", "alta", 90, ["dmgPct", 100], ["allStats", 10], ["allStats", 12], "la luz del principio"),
];
export const RUNA = Object.fromEntries(RUNAS.map((r) => [r.id, r]));
// Rune sets: every one of a set's runes in the sockets of one plain item (white: normal, superior or worn),
// in any order, and the item gets the set's bonus besides what each rune gives. Each set fits some kinds of
// item (w weapon, a armour, o shield); bonus by kind. With the high ones, a plain item of 5 or 6 sockets can
// be better than a legendary: few will ever see one.
export const RUNA_SETS = [
  { id: "cuenta", name: "La cuenta", runas: ["ata", "bosa", "mica"], kinds: ["w", "a", "o"],
    bonus: { w: { dmgPct: 30, allStats: 4 }, a: { armorPct: 30, allStats: 4, life: 20 }, o: { armorPct: 35, allStats: 4, block: 5 } } },
  { id: "laguna", name: "Laguna de Guatavita", runas: ["sie", "muyhica", "ta"], kinds: ["a", "o"],
    bonus: { a: { resCold: 25, resPoison: 25, manaRegen: 3, replayCost: 20 }, o: { resAll: 15, mana: 40, replayCost: 20 } } },
  { id: "fogon", name: "Fogón de la tribu", runas: ["gata", "mica", "cuhupcua", "hisca"], kinds: ["w"],
    bonus: { w: { fire: 35, light: 25, dmgPct: 35, crit: 3 } } },
  { id: "cercado", name: "Cercado del Zipa", runas: ["zipa", "quyca", "hyca", "cuhupcua"], kinds: ["a", "o"],
    bonus: { a: { armorPct: 80, resAll: 15, life: 60, thorns: 20 }, o: { armorPct: 90, resAll: 20, block: 10, thorns: 25 } } },
  { id: "camino", name: "Camino de Bochica", runas: ["bochica", "fiba", "sie", "suhuza", "aca"], kinds: ["w", "a"],
    bonus: { w: { dmgDictation: 40, dmgCloze: 40, dmgPct: 80, typoTol: 1, allStats: 8 }, a: { armorPct: 100, freeReplay: 1, typoTol: 1, allStats: 10, resAll: 15 } } },
  { id: "bachue", name: "Hijos de Bachué", runas: ["bachue", "aca", "ubchihica", "gata", "sie"], kinds: ["a"],
    bonus: { a: { armorPct: 120, life: 120, lifeRegen: 6, resAll: 25, allStats: 10 } } },
  { id: "solyluna", name: "El sol y la luna", runas: ["sue", "chia", "huitaca", "nencatacoa", "ubchihica"], kinds: ["w"],
    bonus: { w: { dmgPct: 150, crit: 6, leech: 6, allStats: 12, resAll: 15 } } },
  { id: "aliento", name: "Aliento de Chiminigagua", runas: ["chiminigagua", "sue", "chia", "bochica", "chibchacum", "chaquen"], kinds: ["w", "a"],
    bonus: { w: { dmgPct: 160, crit: 8, leech: 8, allStats: 20, resAll: 30, freeReplay: 1 }, a: { armorPct: 160, life: 150, allStats: 20, resAll: 35, freeReplay: 1, typoTol: 1 } } },
];

// ---------- runes (removed) ----------
// Runes and runewords are gone from the game. Their table stays only so an old save can be converted
// (main.js dropRunes: loose and socketed runes sold, a runeword's rune effects kept in its properties).
export const RUNES = [
  { id: "CA",  lvl: 1,  weapon: ["dmgMax", 2],    armor: ["armor", 6],    off: ["block", 3] },
  { id: "SA",  lvl: 2,  weapon: ["dmgMin", 1],    armor: ["life", 8],     off: ["armor", 8] },
  { id: "LU",  lvl: 4,  weapon: ["light", 5],     armor: ["mana", 8],     off: ["resLight", 12] },
  { id: "NA",  lvl: 5,  weapon: ["cold", 4],      armor: ["manaRegen", 1], off: ["resCold", 12] },
  { id: "TI",  lvl: 7,  weapon: ["crit", 2],      armor: ["dex", 3],      off: ["dodge", 2] },
  { id: "GRE", lvl: 9,  weapon: ["dmgPct", 15],   armor: ["str", 3],      off: ["thorns", 4] },
  { id: "PA",  lvl: 11, weapon: ["dmgCloze", 8],  armor: ["replayCost", 6], off: ["resPoison", 15] },
  { id: "LO",  lvl: 13, weapon: ["poison", 8],    armor: ["resAll", 4],   off: ["resAll", 6] },
  { id: "MA",  lvl: 15, weapon: ["leech", 2],     armor: ["vit", 4],      off: ["life", 15] },
  { id: "FE",  lvl: 18, weapon: ["fire", 10],     armor: ["resFire", 15], off: ["resFire", 20] },
  { id: "LI",  lvl: 21, weapon: ["manaLeech", 2], armor: ["ene", 5],      off: ["mana", 15] },
  { id: "RI",  lvl: 24, weapon: ["dmgDictation", 10], armor: ["hintCost", 8], off: ["block", 5] },
  { id: "PO",  lvl: 27, weapon: ["killHeal", 4],  armor: ["lifeRegen", 2], off: ["lifeRegen", 3] },
  { id: "SOL", lvl: 31, weapon: ["fire", 18],     armor: ["allStats", 3], off: ["resAll", 10] },
  { id: "DA",  lvl: 35, weapon: ["dmgPct", 30],   armor: ["armorPct", 20], off: ["armorPct", 25] },
  { id: "DO",  lvl: 40, weapon: ["crit", 5],      armor: ["xp", 4],       off: ["dodge", 5] },
];
RUNES.push(...GRAMMAR_RUNES); // forms of haber: caught by ear, never dropped (see grammar.js)
export const RUNE = Object.fromEntries(RUNES.map((r) => [r.id, r]));
// kinds: "melee" / "ranged" weapons, or a slot (head, body, off).

// ---------- random uniques ----------
// Most uniques are written by hand (below). Past those, the game invents one: base + a namesake.
export const UNIQUE_OWNERS = [
  "de Don Ramiro el Sordo", "de la Viuda de Cumbal", "de Mamá Pancha", "del Cura sin Sombra", "de Tío Conejo", "de la Niña Úrsula",
  "del Arriero Celestino", "de Doña Bárbara Peña", "del Sastre de Mompox", "de la Hermana Clotilde", "del Cartero de Barichara",
  "de la Partera de Guapi", "del Alcalde Mudo", "de Misiá Gertrudis", "del Boga del Magdalena", "de la Cantora de Tumaco",
  "del Herrero Tuerto", "de Don Abundio", "de la Comadre Rosalba", "del Último Muisca", "de Mono Jaramillo", "del Teniente Ospina",
  "de la Señorita Inés", "del Pescador de Taganga", "de Doña Eduviges", "del Profesor Lozano", "de la Abuela Saturia",
  "del Gallero de Sahagún", "de la Lavandera del Cauca", "del Telegrafista de Honda", "de los Siete Hermanos", "de la Monja Alférez",
];
export const UNIQUE_TITLES = { // stand-alone names, by gender of the base
  m: ["El Madrugador", "El Último Tinto", "El Desvelo", "El Aguacero", "El Pregón", "El Juramento Roto", "El Silbo Largo", "El Recado"],
  f: ["La Desvelada", "La Promesa", "La Callada", "La Serenata", "La Trasnochada", "La Remolona", "La Advertencia", "La Primera Lluvia"],
};
// Names for the three top rarities: the base, then one of these.
export const TOP_NAMES = {
  ancestral: ["de los Abuelos", "de la Primera Gente", "del Templo Hundido", "de la Laguna Sagrada", "del Camino Viejo", "de los que Ya No Están",
    "de la Piedra Pintada", "del Pueblo Dormido", "de la Ceiba Madre", "del Fuego Guardado"],
  legendario: ["que Partió el Río", "del Último Cacique", "de las Siete Lunas", "que Cantaba Sola", "de la Guerra Larga", "del Cóndor Blanco",
    "que Nadie Pudo Cargar", "de la Noche sin Fin", "del Juramento", "que Volvió del Páramo"],
  mitico: ["del Primer Sonido", "de Antes de la Palabra", "del Eco Eterno", "de la Voz Primera", "del Silencio Roto", "del Origen",
    "que Oye lo No Dicho", "del Nombre Verdadero"],
};
export const TOP_FLAVORS = {
  ancestral: "Lo hicieron manos que ya nadie recuerda.",
  legendario: "De esto se habla en las veredas, y casi nadie lo ha visto.",
  mitico: "Dicen que existía antes que la gente aprendiera a hablar.",
};
export const UNIQUE_FLAVORS = [
  "Nadie recuerda quién la hizo, pero todos recuerdan a quién se la quitaron.", "Huele a café y a pólvora.",
  "La heredó el que menos la merecía.", "Pasó por tres guerras y dos matrimonios.", "Dicen que todavía oye a su dueño.",
  "La encontraron en un baúl, debajo de cartas sin abrir.", "Vino por el río, sola.", "Nunca se la presta a nadie.",
  "Brilla un poquito cuando alguien miente.", "La bendijeron dos veces, por si acaso.", "Pesa más los domingos.",
  "Tiene un nombre grabado que nadie sabe leer.", "Se la ganaron a los dados en Mompox.", "Siempre vuelve a la misma casa.",
];

// ---------- sets ----------
export const SETS = [
  {
    id: "arriero", name: "Avíos del Arriero",
    pieces: [
      { name: "Sombrero del Arriero", base: "sombrero", props: { armorPct: 60, vit: 8, replayCost: 15 } },
      { name: "Ruana del Arriero", base: "ruana", props: { armorPct: 70, life: 25, resCold: 20 } },
      { name: "Carriel del Arriero", base: "faja", props: { beltSlots: 2, gf: 50, potion: 25 } },
      { name: "Alpargatas del Arriero", base: "alpargatas", props: { armorPct: 50, dodge: 5, dex: 6 } },
    ],
    bonus: { 2: { life: 30 }, 3: { replayCost: 25, mf: 20 }, 4: { freeReplay: 1, allStats: 8, resAll: 15 } },
    lvl: 8,
  },
  {
    id: "cacique", name: "Herencia del Cacique",
    pieces: [
      { name: "Diadema del Cacique", base: "mascara", props: { armorPct: 80, mana: 25, hintCost: 25 } },
      { name: "Pectoral del Cacique", base: "amuleto", props: { resAll: 15, ene: 10, manaRegen: 2 } },
      { name: "Bastón del Cacique", base: "baston", props: { dmgPct: 100, dmgCloze: 25, fire: 10 } },
      { name: "Brazaletes del Cacique", base: "brazales", props: { armorPct: 60, crit: 4, manaLeech: 3 } },
    ],
    bonus: { 2: { mana: 30 }, 3: { dmgCloze: 30, hintCost: 30 }, 4: { slowFree: true, mf: 40, allStats: 10 } },
    lvl: 18,
  },
  {
    id: "centinela", name: "Hierro del Centinela",
    pieces: [
      { name: "Yelmo del Centinela", base: "yelmo", props: { armorPct: 90, life: 30, resLight: 25 } },
      { name: "Cota del Centinela", base: "cota", props: { armorPct: 100, vit: 15, thorns: 12 } },
      { name: "Escudo del Centinela", base: "escudotribal", props: { armorPct: 90, block: 10, resAll: 15 } },
      { name: "Guanteletes del Centinela", base: "guanteletes", props: { armorPct: 70, str: 12, dmgDictation: 20 } },
      { name: "Botas del Centinela", base: "grebas", props: { armorPct: 70, dodge: 5, lifeRegen: 3 } },
    ],
    bonus: { 2: { armorPct: 50 }, 3: { life: 60, resAll: 15 }, 4: { dmgDictation: 40 }, 5: { comboKeep: true, nearExact: true } },
    lvl: 28,
  },
  {
    id: "patasola", name: "Andanzas de la Patasola",
    pieces: [
      { name: "Garras de la Patasola", base: "garras", props: { dmgPct: 120, leech: 6, poison: 15 } },
      { name: "Velo de la Patasola", base: "capucha", props: { armorPct: 80, dodge: 6, crit: 4 } },
      { name: "Sortija de la Patasola", base: "sortija", props: { dex: 12, mf: 20, resPoison: 30 } },
      { name: "Bota de la Patasola", base: "botas", props: { armorPct: 70, dodge: 8, killHeal: 6 } },
    ],
    bonus: { 2: { crit: 6 }, 3: { leech: 5, dex: 15 }, 4: { comboStart: 3, typoTol: 1, xp: 10 } },
    lvl: 22,
  },
  {
    id: "jaguar", name: "Rastro del Jaguar",
    pieces: [
      { name: "Arco del Jaguar", base: "arcocurvo_2", props: { dmgPct: 170, dmgCloze: 40, crit: 8, leech: 4 } },
      { name: "Piel del Jaguar", base: "jubon_2", props: { armorPct: 110, dodge: 8, dex: 12 } },
      { name: "Capucha del Jaguar", base: "capucha_2", props: { armorPct: 90, crit: 5, replayCost: 20 } },
      { name: "Garras del Jaguar", base: "guantes_2", props: { armorPct: 80, dex: 10, dmgCloze: 20 } },
      { name: "Huellas del Jaguar", base: "botas_2", props: { armorPct: 80, dodge: 6, killHeal: 6 } },
    ],
    bonus: { 2: { dex: 15 }, 3: { crit: 8, dmgPct: 50 }, 4: { dmgCloze: 40, leech: 5 }, 5: { comboKeep: true, comboStart: 3, allStats: 12 } },
    lvl: 42,
  },
  // The second eight, higher up: four elements, two from Tibetan Buddhism, a river spirit, the sun.
  // Each has its own colours (a gradient map in build_lpc.py) and its own ornament (custom_art.py).
  {
    id: "cienaga", name: "Hálito de la Ciénaga",
    pieces: [
      { name: "Capucha de la Ciénaga", base: "capucha_2", props: { armorPct: 90, resPoison: 30, dodge: 6 } },
      { name: "Gabán de la Ciénaga", base: "gaban_2", props: { armorPct: 100, life: 60, thorns: 15 } },
      { name: "Garras de la Ciénaga", base: "garras_2", props: { dmgPct: 150, poison: 35, leech: 5 } },
      { name: "Botas de la Ciénaga", base: "botas_2", props: { armorPct: 80, dodge: 6, killHeal: 8 } },
    ],
    bonus: { 2: { poison: 20 }, 3: { resPoison: 30, leech: 4 }, 4: { typoTol: 1, life: 80, crit: 6 } },
    lvl: 34,
  },
  {
    id: "mohan", name: "Embrujo del Mohán",
    pieces: [
      { name: "Sombrero del Mohán", base: "sombrero_2", props: { armorPct: 90, mana: 40, hintCost: 25 } },
      { name: "Ruana del Mohán", base: "ruana_2", props: { armorPct: 110, life: 70, resCold: 30 } },
      { name: "Tridente del Mohán", base: "tridente", props: { dmgPct: 160, cold: 30, dmgDictation: 30 } },
      { name: "Brazaletes del Mohán", base: "brazales_2", props: { armorPct: 80, manaLeech: 4, crit: 5 } },
      { name: "Alpargatas del Mohán", base: "alpargatas_2", props: { armorPct: 80, dodge: 7, lifeRegen: 4 } },
    ],
    bonus: { 2: { resCold: 20 }, 3: { cold: 25, mana: 40 }, 4: { replayCost: 30, mf: 30 }, 5: { slowFree: true, allStats: 12 } },
    lvl: 36,
  },
  {
    id: "yogui", name: "Senda del Yogui de las Nieves",
    pieces: [
      { name: "Turbante del Yogui", base: "panoleta_3", props: { armorPct: 90, hintCost: 35, nearExact: true } },
      { name: "Túnica de algodón del Yogui", base: "tunica_3", props: { armorPct: 100, resCold: 40, life: 70 } },
      { name: "Mala de ciento ocho cuentas", base: "amuleto", props: { replayCost: 30, freeReplay: 1, ene: 15 } },
      { name: "Cinta de meditación", base: "cordon_2", props: { manaRegen: 4, mana: 40, beltSlots: 1 } },
      { name: "Sandalias del Yogui", base: "alpargatas_3", props: { armorPct: 80, dodge: 8, lifeRegen: 5 } },
    ],
    bonus: { 2: { manaRegen: 3 }, 3: { slowFree: true, resAll: 20 }, 4: { typoTol: 1, mana: 60 }, 5: { freeReplay: 1, allStats: 15, xp: 10 } },
    lvl: 40,
  },
  {
    id: "vajra", name: "Rayo Diamantino",
    pieces: [
      { name: "Vajra de cristal", base: "cetro_2", props: { dmgPct: 170, light: 40, spellDmg: 25, crit: 8 } },
      { name: "Corona de las Cinco Sabidurías", base: "corona", props: { armorPct: 110, allStats: 10, hintCost: 30 } },
      { name: "Manto azafrán", base: "jubon_3", props: { armorPct: 120, life: 80, resAll: 15 } },
      { name: "Cadena del Diamante", base: "cadena", props: { resLight: 35, mana: 50, manaRegen: 3 } },
      { name: "Guantes del Ritual", base: "guantes_3", props: { armorPct: 90, crit: 6, manaLeech: 4 } },
    ],
    bonus: { 2: { spellDmg: 15 }, 3: { light: 30, resLight: 25 }, 4: { crit: 8, dmgPct: 50 }, 5: { comboKeep: true, nearExact: true, spellDmg: 25 } },
    lvl: 44,
  },
  {
    id: "averno", name: "Pacto del Averno",
    pieces: [
      { name: "Cuernos del Pacto", base: "yelmocornudo", props: { armorPct: 120, resFire: 40, str: 15 } },
      { name: "Coraza del Averno", base: "coraza_2", props: { armorPct: 140, life: 100, thorns: 25 } },
      { name: "Hoja del Averno", base: "mandoble_2", props: { dmgPct: 210, fire: 60, leech: 7, dmgDictation: 30 } },
      { name: "Garras del Pacto", base: "guanteletes_2", props: { armorPct: 100, fire: 20, crit: 6 } },
      { name: "Pezuñas del Averno", base: "grebas_2", props: { armorPct: 100, resFire: 30, killHeal: 10 } },
      { name: "Cadenas del Pacto", base: "cinturonplacas_2", props: { life: 60, str: 12, potion: 30 } },
    ],
    bonus: { 2: { fire: 25 }, 3: { resFire: 30, leech: 5 }, 4: { dmgPct: 60, thorns: 30 }, 5: { life: 120, crit: 8 }, 6: { comboStart: 3, allStats: 15, fire: 50 } },
    lvl: 48,
  },
  {
    id: "trueno", name: "Cólera del Trueno",
    pieces: [
      { name: "Lanza del Trueno", base: "lanzalarga_2", props: { dmgPct: 220, light: 70, crit: 10 } },
      { name: "Yelmo de la Tormenta", base: "yelmo_2", props: { armorPct: 130, resLight: 45, dodge: 6 } },
      { name: "Loriga del Trueno", base: "lorica", props: { armorPct: 150, life: 110, resAll: 15 } },
      { name: "Muñequeras del Relámpago", base: "munequeras_3", props: { armorPct: 100, dex: 15, light: 20 } },
      { name: "Botas del Vendaval", base: "botasmontar_2", props: { armorPct: 100, dodge: 10, xp: 8 } },
    ],
    bonus: { 2: { light: 30 }, 3: { resLight: 30, crit: 6 }, 4: { dmgPct: 70, dodge: 6 }, 5: { comboKeep: true, light: 60, allStats: 15 } },
    lvl: 52,
  },
  {
    id: "sol", name: "Custodia del Sol",
    pieces: [
      { name: "Almete del Sol", base: "almete", props: { armorPct: 140, life: 80, resFire: 30 } },
      { name: "Peto del Sol", base: "lorica_2", props: { armorPct: 170, life: 140, resAll: 20 } },
      { name: "Espada del Mediodía", base: "espada_3", props: { dmgPct: 230, fire: 40, light: 40, crit: 8 } },
      { name: "Escudo de Inti", base: "escudocruz", props: { armorPct: 140, block: 12, resAll: 20 } },
      { name: "Botas del Alba", base: "botaspunta_2", props: { armorPct: 120, dodge: 8, lifeRegen: 8 } },
    ],
    bonus: { 2: { life: 100 }, 3: { resAll: 25, block: 6 }, 4: { dmgPct: 70, lifeRegen: 8 }, 5: { nearExact: true, comboKeep: true, allStats: 20, xp: 10 } },
    lvl: 56,
  },
  {
    id: "guardian", name: "Ira del Protector",
    pieces: [
      { name: "Diadema de cinco calaveras", base: "cascobarbaro_2", props: { armorPct: 150, str: 20, resAll: 20 } },
      { name: "Hacha del Protector", base: "hacha_3", props: { dmgPct: 260, fire: 60, leech: 8, dmgDictation: 40 } },
      { name: "Piel del Protector", base: "tabardo_2", props: { armorPct: 170, life: 160, thorns: 40 } },
      { name: "Brazaletes de serpiente", base: "brazales_3", props: { armorPct: 130, poison: 40, crit: 8 } },
      { name: "Botas del Protector", base: "grebas_2", props: { armorPct: 130, dodge: 8, killHeal: 14 } },
      { name: "Cinto del Protector", base: "cinto_2", props: { life: 80, potion: 40, resFire: 30 } },
    ],
    bonus: { 2: { thorns: 30 }, 3: { life: 150, resAll: 20 }, 4: { dmgDictation: 50, leech: 6 }, 5: { comboStart: 4, crit: 10 }, 6: { comboKeep: true, nearExact: true, allStats: 25 } },
    lvl: 60,
  },
  // One set for each rarity above unique: its pieces only ever drop in that rarity (see TOP_SETS).
  {
    id: "laguna", tier: "ancestral", name: "Ofrendas de la Laguna",
    pieces: [
      { name: "Máscara de la Laguna", base: "mascara", props: { armorPct: 120, mana: 40, hintCost: 30, resAll: 10 } },
      { name: "Pectoral de la Laguna", base: "amuleto", props: { allStats: 8, resAll: 20, xp: 6 } },
      { name: "Manto de la Laguna", base: "ruana", props: { armorPct: 140, life: 60, replayCost: 25 } },
      { name: "Brazaletes de la Laguna", base: "brazales", props: { armorPct: 110, crit: 6, manaLeech: 4 } },
      { name: "Arco de la Ofrenda", base: "arco", props: { dmgPct: 200, dmgCloze: 45, crit: 8, gf: 60 } },
    ],
    bonus: { 2: { resAll: 15 }, 3: { replayCost: 25, mf: 40 }, 4: { freeReplay: 1, allStats: 12, life: 80 }, 5: { dmgCloze: 40, crit: 8, xp: 8 } },
    lvl: 18,
  },
  {
    id: "condor", tier: "legendario", name: "Gesta del Cóndor",
    pieces: [
      { name: "Yelmo del Cóndor", base: "yelmo", props: { armorPct: 160, life: 70, resLight: 30, dodge: 6 } },
      { name: "Alas del Cóndor", base: "coraza", props: { armorPct: 180, life: 90, resAll: 20 } },
      { name: "Garra del Cóndor", base: "espadon", props: { dmgPct: 220, crit: 10, leech: 6, dmgDictation: 35 } },
      { name: "Guanteletes del Cóndor", base: "guanteletes", props: { armorPct: 140, str: 15, dmgPct: 30 } },
      { name: "Grebas del Cóndor", base: "grebas", props: { armorPct: 140, dodge: 8, lifeRegen: 5 } },
    ],
    bonus: { 2: { life: 80 }, 3: { dmgPct: 60, resAll: 20 }, 4: { comboStart: 3, crit: 8 }, 5: { comboKeep: true, nearExact: true, allStats: 15 } },
    lvl: 30,
  },
  {
    id: "origen", tier: "mitico", name: "La Voz del Origen",
    pieces: [
      { name: "Corona del Primer Sonido", base: "corona", props: { armorPct: 200, allStats: 12, hintCost: 40 } },
      { name: "Arco del Eco Eterno", base: "arcolargo", props: { dmgPct: 280, dmgCloze: 60, freeReplay: 1, crit: 10 } },
      { name: "Túnica del Silencio Roto", base: "tunica", props: { armorPct: 220, life: 120, resAll: 30 } },
      { name: "Sortija de la Voz Primera", base: "sortija", props: { mf: 60, xp: 10, replayCost: 30 } },
      { name: "Botas de Antes de la Palabra", base: "botasviaje", props: { armorPct: 180, dodge: 10, dex: 20 } },
      { name: "Pectoral del Origen", base: "amuleto", props: { resAll: 25, ene: 25, manaRegen: 4 } },
    ],
    bonus: { 2: { resAll: 20 }, 3: { replayCost: 40, slowFree: true }, 4: { dmgCloze: 50, typoTol: 1 }, 5: { freeReplay: 1, allStats: 20 }, 6: { nearExact: true, comboKeep: true, xp: 15 } },
    lvl: 38,
  },
  // the second three: two more of each tier, for the long road down the Abismo
  {
    id: "bachue", tier: "ancestral", name: "Regreso de Bachué",
    pieces: [
      { name: "Velo de Iguaque", base: "capucha_3", props: { armorPct: 170, mana: 60, resPoison: 30, hintCost: 35 } },
      { name: "Túnica de las Aguas", base: "tunica_3", props: { armorPct: 190, life: 130, resAll: 25, lifeRegen: 8 } },
      { name: "Báculo de la Serpiente", base: "baston_3", props: { dmgPct: 280, poison: 70, spellDmg: 30, manaLeech: 6 } },
      { name: "Pectoral de la Madre", base: "amuleto", props: { allStats: 14, resAll: 20, xp: 8 } },
      { name: "Sandalias de la Orilla", base: "alpargatas_3", props: { armorPct: 150, dodge: 10, replayCost: 30 } },
    ],
    bonus: { 2: { resPoison: 30, life: 90 }, 3: { poison: 60, mf: 50 }, 4: { freeReplay: 1, allStats: 15 }, 5: { slowFree: true, dmgCloze: 50, xp: 10 } },
    lvl: 50,
  },
  {
    id: "nevado", tier: "ancestral", name: "Silencio del Nevado",
    pieces: [
      { name: "Yelmo de la Cumbre Blanca", base: "yelmo_3", props: { armorPct: 200, life: 110, resCold: 45 } },
      { name: "Loriga de Escarcha", base: "cota_3", props: { armorPct: 220, life: 160, resAll: 30, thorns: 30 } },
      { name: "Hoja del Glaciar", base: "espadon_3", props: { dmgPct: 310, cold: 90, crit: 12, dmgDictation: 40 } },
      { name: "Guanteletes del Hielo Eterno", base: "guanteletes_3", props: { armorPct: 170, str: 22, cold: 30 } },
      { name: "Botas de la Ventisca", base: "botasmontar_3", props: { armorPct: 170, dodge: 12, resCold: 30 } },
    ],
    bonus: { 2: { resCold: 40, armorPct: 60 }, 3: { cold: 80, life: 120 }, 4: { comboStart: 4, block: 8 }, 5: { comboKeep: true, nearExact: true, allStats: 20 } },
    lvl: 64,
  },
  {
    id: "vientos", tier: "legendario", name: "Señor de los Vientos",
    pieces: [
      { name: "Pañoleta del Vendaval", base: "panoleta_3", props: { armorPct: 170, dex: 25, dodge: 10 } },
      { name: "Gabán de las Corrientes", base: "gaban_3", props: { armorPct: 200, life: 130, resAll: 25, dodge: 8 } },
      { name: "Sable del Siroco", base: "espada_3", props: { dmgPct: 320, light: 60, crit: 14, leech: 6 } },
      { name: "Guantes del Halconero", base: "guantescetrero_3", props: { armorPct: 160, dex: 20, crit: 8 } },
      { name: "Botas del Remolino", base: "botasviaje_3", props: { armorPct: 160, dodge: 12, xp: 10 } },
      { name: "Fajín de las Cuatro Brisas", base: "fajin_3", props: { life: 100, potion: 50, resLight: 30 } },
    ],
    bonus: { 2: { dodge: 10 }, 3: { dex: 30, dmgPct: 70 }, 4: { replayCost: 40, slowFree: true }, 5: { comboStart: 4, crit: 10 }, 6: { comboKeep: true, freeReplay: 1, allStats: 25 } },
    lvl: 58,
  },
  {
    id: "montana", tier: "legendario", name: "Corazón de la Montaña",
    pieces: [
      { name: "Yelmo de Piedra Viva", base: "yelmocornudo_3", props: { armorPct: 230, life: 150, resAll: 25 } },
      { name: "Coraza de la Roca Madre", base: "coraza_3", props: { armorPct: 260, life: 220, thorns: 60 } },
      { name: "Martillo del Volcán Dormido", base: "mangual_3", props: { dmgPct: 340, fire: 80, crit: 10, killHeal: 20 } },
      { name: "Muro de la Cordillera", base: "pavés_3", props: { armorPct: 220, block: 16, resAll: 30 } },
      { name: "Grebas del Basalto", base: "grebas_3", props: { armorPct: 200, vit: 30, lifeRegen: 10 } },
      { name: "Cinto de las Vetas", base: "cinturonplacas_3", props: { life: 130, beltSlots: 4, gf: 60 } },
    ],
    bonus: { 2: { armorPct: 80, life: 120 }, 3: { block: 10, resFire: 40 }, 4: { thorns: 60, vit: 30 }, 5: { dmgDictation: 60, leech: 8 }, 6: { nearExact: true, comboKeep: true, allStats: 30 } },
    lvl: 72,
  },
  {
    id: "kalachakra", tier: "mitico", name: "La Rueda del Tiempo",
    pieces: [
      { name: "Corona de las Diez Potencias", base: "corona_2", props: { armorPct: 240, allStats: 18, hintCost: 45 } },
      { name: "Manto de los Siete Planetas", base: "jubon_3", props: { armorPct: 250, life: 180, resAll: 35 } },
      { name: "La Rueda", base: "cetro_3", props: { dmgPct: 360, spellDmg: 50, light: 60, freeReplay: 1 } },
      { name: "Medallón del Instante", base: "medallon", props: { resAll: 30, ene: 35, manaRegen: 6 } },
      { name: "Sortija del Ciclo", base: "sortija", props: { mf: 80, xp: 14, replayCost: 35 } },
      { name: "Zapatillas del Mandala", base: "zapatos_3", props: { armorPct: 200, dodge: 12, dex: 25 } },
    ],
    bonus: { 2: { resAll: 25 }, 3: { replayCost: 45, slowFree: true }, 4: { dmgCloze: 60, typoTol: 1 }, 5: { freeReplay: 1, allStats: 25 }, 6: { nearExact: true, comboKeep: true, xp: 20 } },
    lvl: 68,
  },
  {
    id: "luzclara", tier: "mitico", name: "La Luz Clara",
    pieces: [
      { name: "Moño del Yogui", base: "panoleta_3", props: { armorPct: 220, ene: 30, hintCost: 50, mana: 80 } },
      { name: "Manto Blanco del Arcoíris", base: "tunica_3", props: { armorPct: 280, life: 220, resAll: 40 } },
      { name: "Cristal de la Mente Natural", base: "bastonruna_3", props: { dmgPct: 400, dmgCloze: 70, spellDmg: 60, crit: 12 } },
      { name: "Espejo del Corazón", base: "amuleto", props: { allStats: 22, resAll: 30, xp: 15 } },
      { name: "Anillo de la Gota de Luz", base: "anillo", props: { mf: 90, manaLeech: 8, freeReplay: 1 } },
      { name: "Pasos sin Huella", base: "botaspunta_3", props: { armorPct: 220, dodge: 15, lifeRegen: 12 } },
    ],
    bonus: { 2: { resAll: 30, mana: 80 }, 3: { replayCost: 50, slowFree: true, typoTol: 1 }, 4: { dmgCloze: 70, comboStart: 5 }, 5: { freeReplay: 1, allStats: 30 }, 6: { nearExact: true, comboKeep: true, xp: 25, mf: 60 } },
    lvl: 80,
  },
  // the high bands' sets (levels 68 to 126): built on the band pieces, each in colours of its own, with an ornament
  {
    id: "osario", tier: "ancestral", name: "Danza del Osario",
    pieces: [
      { name: "Calavera Alegre", base: "yelmohueso", props: { armorPct: 210, life: 120, resAll: 25, mf: 30 } },
      { name: "Peto de las Costillas", base: "petohueso", props: { armorPct: 240, life: 180, thorns: 50, resCold: 35 } },
      { name: "Guadaña del Último Baile", base: "guadanahueso", props: { dmgPct: 340, cold: 90, killHeal: 24, crit: 10 } },
      { name: "Brazaletes de Falanges", base: "brazaleshueso", props: { armorPct: 180, crit: 9, leech: 7 } },
      { name: "Botas del Cortejo", base: "botashueso", props: { armorPct: 180, dodge: 12, lifeRegen: 10 } },
    ],
    bonus: { 2: { life: 120, resCold: 30 }, 3: { killHeal: 20, mf: 50 }, 4: { comboStart: 4, thorns: 50 }, 5: { comboKeep: true, nearExact: true, allStats: 22 } },
    lvl: 68,
  },
  {
    id: "tairona", name: "Legado Tairona",
    pieces: [
      { name: "Yelmo del Mamo", base: "yelmoesmeralda", props: { armorPct: 190, life: 120, resAll: 20 } },
      { name: "Manta de la Sierra", base: "cotaesmeralda", props: { armorPct: 210, life: 170, vit: 25 } },
      { name: "Estoque de la Ciudad Perdida", base: "estoqueesmeralda", props: { dmgPct: 300, crit: 10, dex: 25, dmgDictation: 40 } },
      { name: "Guantes de la Escalinata", base: "guantesesmeralda", props: { armorPct: 160, crit: 8, leech: 6 } },
      { name: "Faja de los Caminos de Piedra", base: "fajaesmeralda", props: { life: 110, potion: 40, dodge: 8 } },
    ],
    bonus: { 2: { life: 120 }, 3: { resAll: 25, dex: 25 }, 4: { dmgPct: 80, crit: 8 }, 5: { comboKeep: true, nearExact: true, allStats: 25 } },
    lvl: 72,
  },
  {
    id: "dorado", name: "La Balsa de El Dorado",
    pieces: [
      { name: "Diadema del Zipa", base: "yelmotumbaga", props: { armorPct: 220, mana: 90, hintCost: 40, resAll: 20 } },
      { name: "Coraza de Polvo de Oro", base: "corazatumbaga", props: { armorPct: 250, life: 200, gf: 80 } },
      { name: "Báculo de la Ofrenda", base: "baculotumbaga", props: { dmgPct: 360, spellDmg: 50, fire: 70, manaLeech: 7 } },
      { name: "Pectoral de la Balsa", base: "amuleto", props: { allStats: 18, resAll: 25, xp: 10 } },
      { name: "Grebas del Cacique Dorado", base: "grebastumbaga", props: { armorPct: 200, dodge: 10, ene: 25 } },
      { name: "Cinto de las Esmeraldas", base: "cintotumbaga", props: { life: 130, potion: 50, mf: 50 } },
    ],
    bonus: { 2: { gf: 60, mana: 80 }, 3: { spellDmg: 40, replayCost: 40 }, 4: { mf: 80, resAll: 25 }, 5: { freeReplay: 1, slowFree: true }, 6: { nearExact: true, comboKeep: true, allStats: 30 } },
    lvl: 84,
  },
  {
    id: "madreagua", tier: "ancestral", name: "La Madre del Agua",
    pieces: [
      { name: "Corona del Río", base: "yelmotumbaga", props: { armorPct: 280, life: 160, resCold: 45, mana: 80 } },
      { name: "Coraza de Escamas", base: "corazacatatumbo", props: { armorPct: 310, life: 250, resAll: 35 } },
      { name: "Lanza del Remolino", base: "lanzatumbaga", props: { dmgPct: 440, cold: 140, crit: 12, dmgCloze: 50 } },
      { name: "Guanteletes de la Corriente", base: "guantestumbaga", props: { armorPct: 230, dex: 30, manaLeech: 8 } },
      { name: "Botas del Vado", base: "botascatatumbo", props: { armorPct: 230, dodge: 14, lifeRegen: 12 } },
      { name: "Sortija de la Orilla", base: "sortija", props: { mf: 70, xp: 12, replayCost: 35 } },
    ],
    bonus: { 2: { resCold: 40, life: 150 }, 3: { cold: 110, mana: 100 }, 4: { replayCost: 45, slowFree: true }, 5: { comboStart: 5, dodge: 10 }, 6: { comboKeep: true, nearExact: true, allStats: 30 } },
    lvl: 96,
  },
  {
    id: "relampago", name: "El Relámpago Eterno",
    pieces: [
      { name: "Yelmo del Rayo", base: "yelmocatatumbo", props: { armorPct: 250, life: 150, resLight: 45 } },
      { name: "Coraza de la Tormenta", base: "corazacatatumbo", props: { armorPct: 280, life: 230, resAll: 30 } },
      { name: "Martillo del Trueno sin Fin", base: "martillocatatumbo", props: { dmgPct: 400, light: 130, crit: 12, dmgDictation: 50 } },
      { name: "Guantes de Chispa", base: "guantescatatumbo", props: { armorPct: 210, str: 30, light: 40 } },
      { name: "Botas del Lago de Maracaibo", base: "botascatatumbo", props: { armorPct: 210, dodge: 12, lifeRegen: 12 } },
    ],
    bonus: { 2: { resLight: 40, life: 150 }, 3: { light: 100, crit: 8 }, 4: { comboStart: 5, dmgPct: 90 }, 5: { comboKeep: true, nearExact: true, allStats: 30 } },
    lvl: 96,
  },
  {
    id: "vigilia", name: "Vigilia de la Luna",
    pieces: [
      { name: "Yelmo de la Vigía", base: "yelmoluna", props: { armorPct: 280, life: 170, resCold: 40, dodge: 8 } },
      { name: "Manto de Medianoche", base: "mantoluna", props: { armorPct: 310, life: 260, resAll: 35 } },
      { name: "Arco de la Luna Nueva", base: "arcoluna", props: { dmgPct: 450, cold: 120, dmgCloze: 70, crit: 12 } },
      { name: "Cordón de Plata", base: "cordonluna", props: { armorPct: 240, life: 150, resAll: 30 } },  // was a buckler, which a two-handed bow can't wear with
      { name: "Brazales de Rocío", base: "brazalesluna", props: { armorPct: 230, dex: 35, manaLeech: 8 } },
      { name: "Zapatos sin Ruido", base: "zapatosluna", props: { armorPct: 230, dodge: 15, replayCost: 40 } },
    ],
    bonus: { 2: { dodge: 10, resCold: 40 }, 3: { dmgCloze: 60, dex: 35 }, 4: { replayCost: 50, slowFree: true }, 5: { freeReplay: 1, comboStart: 5 }, 6: { nearExact: true, comboKeep: true, allStats: 35, xp: 15 } },
    lvl: 108,
  },
  {
    // the Arhuaco of the Sierra Nevada de Santa Marta: white cotton, the tutusoma (its point is the snowy
    // peaks), the mochila woven slowly, a thought in every turn of its spiral; a walking stick for the paths
    id: "arhuaco", tier: "legendario", name: "El Tejido de la Sierra",
    pieces: [
      { name: "Tutusoma de las Nieves", base: "yelmocatatumbo", props: { armorPct: 280, life: 170, resCold: 45, hintCost: 40 } },
      { name: "Manta Blanca de Nabusímake", base: "corazacatatumbo", props: { armorPct: 320, life: 260, resAll: 30, lifeRegen: 12 } },
      { name: "Bastón del Caminante", base: "baculotumbaga", props: { dmgPct: 420, dmgDictation: 55, cold: 110, manaLeech: 7 } },
      { name: "Mochila del Pensamiento", base: "cintocatatumbo", props: { life: 160, mf: 60, replayCost: 40 } },
      { name: "Collar de la Madre Tierra", base: "amuleto", props: { allStats: 20, resAll: 25, xp: 12 } },
    ],
    bonus: { 2: { resCold: 40, life: 150 }, 3: { replayCost: 40, mana: 120 }, 4: { slowFree: true, dmgDictation: 60 }, 5: { freeReplay: 1, nearExact: true, allStats: 32 } },
    lvl: 94,
  },
  {
    id: "pacto", tier: "legendario", name: "El Pacto de la Sombra",
    pieces: [
      { name: "Yelmo del Pacto", base: "yelmosombra", props: { armorPct: 360, life: 220, resAll: 35, str: 30 } },
      { name: "Coraza del Contrato", base: "corazasombra", props: { armorPct: 400, life: 320, thorns: 120, resFire: 50 } },
      { name: "Mandoble sin Alma", base: "mandoblesombra", props: { dmgPct: 560, fire: 180, leech: 10, crit: 14 } },
      { name: "Guanteletes de la Firma", base: "guantessombra", props: { armorPct: 300, crit: 12, killHeal: 30 } },
      { name: "Pezuñas del Diablo", base: "pezunassombra", props: { armorPct: 300, dodge: 15, dmgDictation: 60 } },
      { name: "Cinto de las Almas", base: "cintosombra", props: { life: 200, potion: 60, leech: 6 } },
    ],
    bonus: { 2: { life: 200, resFire: 40 }, 3: { fire: 150, thorns: 80 }, 4: { dmgDictation: 70, leech: 8 }, 5: { comboStart: 6, crit: 12 }, 6: { comboKeep: true, nearExact: true, allStats: 40 } },
    lvl: 116,
  },
  {
    id: "caiman", tier: "ancestral", name: "El Hombre Caimán",
    pieces: [
      { name: "Yelmo de las Fauces", base: "yelmosombra", props: { armorPct: 340, life: 210, resPoison: 45, str: 30 } },
      { name: "Piel de Escamas", base: "corazasombra", props: { armorPct: 380, life: 300, thorns: 100, resAll: 35 } },
      { name: "Mangual de la Cola", base: "mangualsombra", props: { dmgPct: 520, poison: 170, leech: 9, crit: 13 } },
      { name: "Escudo del Magdalena", base: "escudoastral", props: { armorPct: 330, block: 16, resAll: 35 } },
      { name: "Garras del Caimán", base: "guantessombra", props: { armorPct: 290, crit: 11, killHeal: 28 } },
      { name: "Patas del Pantano", base: "pezunassombra", props: { armorPct: 290, dodge: 14, lifeRegen: 16 } },
    ],
    bonus: { 2: { resPoison: 40, life: 180 }, 3: { poison: 140, thorns: 70 }, 4: { dmgDictation: 60, leech: 7 }, 5: { comboStart: 6, crit: 10 }, 6: { comboKeep: true, nearExact: true, allStats: 36 } },
    lvl: 121,
  },
  {
    id: "firmamento", tier: "mitico", name: "El Primer Cielo",
    pieces: [
      { name: "Capirote de las Constelaciones", base: "capiroteastral", props: { armorPct: 440, allStats: 30, hintCost: 55, mana: 140 } },
      { name: "Vestidura del Firmamento", base: "vestiduraastral", props: { armorPct: 480, life: 380, resAll: 50 } },
      { name: "Espada de la Estrella Fugaz", base: "espadaastral", props: { dmgPct: 680, light: 160, cold: 160, crit: 16 } },
      { name: "Escudo de la Vía Láctea", base: "escudoastral", props: { armorPct: 400, block: 18, resAll: 40 } },
      { name: "Guantes del Cartógrafo Celeste", base: "guantesastral", props: { armorPct: 360, dex: 45, mf: 90 } },
      { name: "Zapatillas del Cometa", base: "zapatillasastral", props: { armorPct: 360, dodge: 18, xp: 20 } },
    ],
    bonus: { 2: { resAll: 40, mana: 120 }, 3: { replayCost: 60, slowFree: true, typoTol: 1 }, 4: { dmgPct: 120, comboStart: 6 }, 5: { freeReplay: 1, allStats: 40 }, 6: { nearExact: true, comboKeep: true, xp: 30, mf: 80 } },
    lvl: 126,
  },
  {
    id: "andes", name: "Cumbre de los Andes",
    pieces: [
      { name: "Gorro del Páramo", base: "capiroteastral", props: { armorPct: 330, life: 220, resCold: 50, mana: 100 } },
      { name: "Ruana de los Andes", base: "vestiduraastral", props: { armorPct: 360, life: 330, resAll: 40, vit: 35 } },
      { name: "Arco del Cóndor", base: "arcoastral", props: { dmgPct: 520, cold: 150, dmgCloze: 80, crit: 13 } },
      { name: "Guantes de Lana de Alpaca", base: "guantesastral", props: { armorPct: 280, dex: 40, manaLeech: 8 } },
      { name: "Abarcas del Camino Real", base: "zapatillasastral", props: { armorPct: 280, dodge: 16, xp: 15 } },
      { name: "Chumbe de Siete Colores", base: "fajinastral", props: { life: 220, potion: 60, mf: 60 } },
    ],
    bonus: { 2: { resCold: 45, life: 200 }, 3: { dmgCloze: 70, dex: 40 }, 4: { replayCost: 55, slowFree: true }, 5: { freeReplay: 1, comboStart: 6 }, 6: { nearExact: true, comboKeep: true, allStats: 40, xp: 20 } },
    lvl: 130,
  },
  // From 138 to 200, at the same spacing as below: a green set about every 12 levels, a pink one about
  // every 25, a red one about every 22, a blue one about every 25. All on Luna, Sombra and Astral pieces
  // (there's no band above Astral), so their props carry on the top sets' curve per level and tier
  // (scratchpad generator: armour ~2.5–2.8 × level, damage 4 × level, × 1.08 / 1.15 / 1.3 for pink / red / blue).
  {id: "galeon", tier: "legendario", name: "El Galeón Hundido", pieces: [{name: "Yelmo del Capitán Ahogado", base: "yelmosombra", props: {armorPct: 400, life: 270, resCold: 50, mana: 130}}, {name: "Coraza de Coral", base: "corazasombra", props: {armorPct: 440, life: 400, resAll: 40, thorns: 140}}, {name: "Sable del Abordaje", base: "sableluna", props: {dmgPct: 630, cold: 180, crit: 14, leech: 7}}, {name: "Rodela del Cofre", base: "rodelaluna", props: {armorPct: 380, block: 17, resAll: 35, mf: 70}}, {name: "Guanteletes de Doblones", base: "guantessombra", props: {armorPct: 340, dex: 40, mf: 70}}, {name: "Cinto del Ancla", base: "cintosombra", props: {life: 270, potion: 60, vit: 35}}], bonus: {2: {resCold: 45, life: 240}, 3: {dmgDictation: 90, cold: 160}, 4: {replayCost: 55, slowFree: true}, 5: {freeReplay: 1, comboStart: 6}, 6: {nearExact: true, comboKeep: true, allStats: 48, xp: 23}}, lvl: 138},
  {id: "frailejon", name: "Niebla del Páramo", pieces: [{name: "Capucha de Niebla", base: "capiroteastral", props: {armorPct: 360, life: 240, resCold: 50, mana: 110}}, {name: "Manto de Frailejón", base: "vestiduraastral", props: {armorPct: 400, life: 360, resAll: 45, lifeRegen: 17}}, {name: "Vara del Nacimiento del Agua", base: "varasombra", props: {dmgPct: 570, cold: 160, crit: 14, dmgCloze: 80}}, {name: "Guantes de Musgo", base: "guantesastral", props: {armorPct: 310, dex: 45, manaLeech: 7}}, {name: "Botas de la Turbera", base: "zapatillasastral", props: {armorPct: 310, dodge: 15, xp: 16}}, {name: "Fajín de Rocío", base: "fajinastral", props: {life: 240, potion: 60, mf: 60}}], bonus: {2: {resCold: 45, life: 210}, 3: {dmgCloze: 80, cold: 140}, 4: {replayCost: 55, slowFree: true}, 5: {freeReplay: 1, comboStart: 6}, 6: {nearExact: true, comboKeep: true, allStats: 43, xp: 24}}, lvl: 142},
  {id: "bochica", tier: "ancestral", name: "La Senda de Bochica", pieces: [{name: "Capucha del Anciano", base: "capiroteastral", props: {armorPct: 400, life: 270, resLight: 50, hintCost: 50}}, {name: "Manto del Tejedor", base: "vestiduraastral", props: {armorPct: 440, life: 390, resAll: 45, ene: 35}}, {name: "Báculo del Tequendama", base: "varasombra", props: {dmgPct: 630, light: 180, crit: 14, dmgCloze: 90}}, {name: "Guantes del Telar", base: "guantesastral", props: {armorPct: 340, dex: 45, replayCost: 45}}, {name: "Sandalias del Peregrino", base: "zapatillasastral", props: {armorPct: 340, dodge: 15, xp: 16}}, {name: "Anillo de Chuchaviva", base: "anillo", props: {allStats: 24, resAll: 30, mf: 70}}], bonus: {2: {resLight: 45, life: 240}, 3: {dmgCloze: 90, light: 160}, 4: {replayCost: 55, slowFree: true}, 5: {freeReplay: 1, comboStart: 7}, 6: {nearExact: true, comboKeep: true, allStats: 47, xp: 24}}, lvl: 146},
  {id: "bufeo", tier: "mitico", name: "El Bufeo Colorado", pieces: [{name: "Sombrero del Forastero", base: "capiroteastral", props: {armorPct: 500, life: 330, resCold: 50, allStats: 29}}, {name: "Traje Blanco de la Fiesta", base: "vestiduraastral", props: {armorPct: 550, life: 490, resAll: 45, mana: 160}}, {name: "Lanza del Amazonas", base: "lanzaastral", props: {dmgPct: 780, cold: 220, crit: 14, dmgCloze: 110}}, {name: "Fajín de Agua Negra", base: "fajinastral", props: {life: 330, potion: 60, manaLeech: 8}}, {name: "Guantes del Río Abajo", base: "guantesastral", props: {armorPct: 420, dex: 45, mf: 90}}, {name: "Zapatillas de la Orilla", base: "zapatillasastral", props: {armorPct: 420, dodge: 15, xp: 17}}], bonus: {2: {resCold: 45, life: 290}, 3: {dmgCloze: 110, cold: 200}, 4: {replayCost: 55, slowFree: true}, 5: {freeReplay: 1, comboStart: 7}, 6: {nearExact: true, comboKeep: true, allStats: 58, xp: 25, mf: 90}}, lvl: 150},
  {id: "llanero", name: "Coplas del Llano", pieces: [{name: "Sombrero de Pelo de Guama", base: "yelmoluna", props: {armorPct: 390, life: 260, resFire: 50, vit: 40}}, {name: "Liquiliqui del Coplero", base: "mantoluna", props: {armorPct: 430, life: 380, resAll: 45, dmgDictation: 80}}, {name: "Lanza del Vaquero", base: "tridenteluna", props: {dmgPct: 620, fire: 180, crit: 14, leech: 8}}, {name: "Brazales del Arreo", base: "brazalesluna", props: {armorPct: 330, dex: 45, str: 45}}, {name: "Cotizas del Joropo", base: "zapatosluna", props: {armorPct: 330, dodge: 15, comboStart: 7}}, {name: "Soga de Enlazar", base: "cordonluna", props: {life: 260, potion: 60, killHeal: 35}}], bonus: {2: {resFire: 45, life: 230}, 3: {dmgDictation: 80, fire: 150}, 4: {replayCost: 55, slowFree: true}, 5: {freeReplay: 1, comboStart: 7}, 6: {nearExact: true, comboKeep: true, allStats: 46, xp: 26}}, lvl: 154},
  {id: "madremonte", tier: "legendario", name: "La Madremonte", pieces: [{name: "Tocado de Musgo", base: "yelmoluna", props: {armorPct: 470, life: 310, resPoison: 50, lifeRegen: 22}}, {name: "Manto de Hojas", base: "mantoluna", props: {armorPct: 520, life: 460, resAll: 45, thorns: 170}}, {name: "Vara de la Selva", base: "varasombra", props: {dmgPct: 740, poison: 210, crit: 14, manaLeech: 8}}, {name: "Brazales de Bejuco", base: "brazalesluna", props: {armorPct: 400, dex: 50, thorns: 170}}, {name: "Zapatos de Raíz", base: "zapatosluna", props: {armorPct: 400, dodge: 15, vit: 40}}, {name: "Cordón de Lianas", base: "cordonluna", props: {life: 310, potion: 60, lifeRegen: 22}}], bonus: {2: {resPoison: 45, life: 280}, 3: {dmgDictation: 100, poison: 180}, 4: {replayCost: 55, slowFree: true}, 5: {freeReplay: 1, comboStart: 7}, 6: {nearExact: true, comboKeep: true, allStats: 55, xp: 27}}, lvl: 160},
  {id: "silbon", name: "El Silbido del Silbón", pieces: [{name: "Sombrero del Silbón", base: "yelmosombra", props: {armorPct: 420, life: 280, resCold: 50, replayCost: 45}}, {name: "Harapos del Errante", base: "corazasombra", props: {armorPct: 460, life: 420, resAll: 45, dodge: 16}}, {name: "Mangual del Costal", base: "mangualsombra", props: {dmgPct: 660, cold: 190, crit: 15, dmgDictation: 90}}, {name: "Guanteletes de Hueso Seco", base: "guantessombra", props: {armorPct: 360, dex: 50, killHeal: 40}}, {name: "Pezuñas del Camino Largo", base: "pezunassombra", props: {armorPct: 360, dodge: 16, freeReplay: 1}}, {name: "Cinto del Costal", base: "cintosombra", props: {life: 280, potion: 60, mf: 70}}], bonus: {2: {resCold: 45, life: 250}, 3: {dmgDictation: 90, cold: 170}, 4: {replayCost: 55, slowFree: true}, 5: {freeReplay: 1, comboStart: 8}, 6: {nearExact: true, comboKeep: true, allStats: 50, xp: 28}}, lvl: 166},
  {id: "tunda", tier: "ancestral", name: "La Tunda", pieces: [{name: "Velo del Manglar", base: "yelmoluna", props: {armorPct: 470, life: 310, resPoison: 50, manaLeech: 9}}, {name: "Manto de Raíces", base: "mantoluna", props: {armorPct: 520, life: 460, resAll: 45, lifeRegen: 22}}, {name: "Tridente del Estero", base: "tridenteluna", props: {dmgPct: 740, poison: 210, crit: 15, dmgCloze: 100}}, {name: "Cordón del Manglar", base: "cordonluna", props: {life: 310, potion: 60, thorns: 170}}, {name: "Brazales del Camarón", base: "brazalesluna", props: {armorPct: 400, dex: 50, leech: 9}}, {name: "Pata de Molinillo", base: "zapatosluna", props: {armorPct: 400, dodge: 32}}], bonus: {2: {resPoison: 45, life: 280}, 3: {dmgCloze: 100, poison: 180}, 4: {replayCost: 55, slowFree: true}, 5: {freeReplay: 1, comboStart: 8}, 6: {nearExact: true, comboKeep: true, allStats: 55, xp: 28}}, lvl: 171},
  {id: "mahamudra", tier: "mitico", name: "El Gran Sello", pieces: [{name: "Moño del Cielo Abierto", base: "capiroteastral", props: {armorPct: 580, life: 390, resLight: 50, hintCost: 50}}, {name: "Manto del Espacio", base: "vestiduraastral", props: {armorPct: 640, life: 570, resAll: 45, ene: 45}}, {name: "Arco sin Blanco", base: "arcoastral", props: {dmgPct: 910, light: 260, crit: 15, dmgCloze: 130}}, {name: "Fajín del Silencio", base: "fajinastral", props: {life: 390, potion: 60, replayCost: 45}}, {name: "Guantes del Sello", base: "guantesastral", props: {armorPct: 490, dex: 50, typoTol: 1}}, {name: "Zapatillas del Camino Natural", base: "zapatillasastral", props: {armorPct: 490, dodge: 16, xp: 19}}], bonus: {2: {resLight: 45, life: 340}, 3: {dmgCloze: 130, light: 230}, 4: {replayCost: 55, slowFree: true}, 5: {freeReplay: 1, comboStart: 8}, 6: {nearExact: true, comboKeep: true, allStats: 68, xp: 29, mf: 100}}, lvl: 175},
  {id: "candileja", name: "La Candileja", pieces: [{name: "Capirote de Candela", base: "capiroteastral", props: {armorPct: 450, life: 300, resFire: 50, mana: 140}}, {name: "Vestidura Chamuscada", base: "vestiduraastral", props: {armorPct: 500, life: 440, resAll: 45, thorns: 160}}, {name: "Espada de la Bola de Fuego", base: "espadaastral", props: {dmgPct: 710, fire: 200, crit: 15, dmgDictation: 100}}, {name: "Escudo del Fuego Fatuo", base: "escudoastral", props: {armorPct: 430, block: 18, resAll: 40, killHeal: 45}}, {name: "Guantes de Ceniza", base: "guantesastral", props: {armorPct: 380, dex: 55, leech: 9}}, {name: "Zapatillas del Pajonal", base: "zapatillasastral", props: {armorPct: 380, dodge: 16, comboStart: 8}}], bonus: {2: {resFire: 45, life: 270}, 3: {dmgDictation: 100, fire: 180}, 4: {replayCost: 55, slowFree: true}, 5: {freeReplay: 1, comboStart: 8}, 6: {nearExact: true, comboKeep: true, allStats: 53, xp: 30}}, lvl: 178},
  {id: "sombreron", tier: "legendario", name: "El Sombrerón", pieces: [{name: "El Gran Sombrero", base: "capiroteastral", props: {armorPct: 530, life: 360, resFire: 50, allStats: 31}}, {name: "Capa de la Noche de Feria", base: "vestiduraastral", props: {armorPct: 590, life: 520, resAll: 50, dodge: 16}}, {name: "Mandoble del Jinete", base: "mandoblesombra", props: {dmgPct: 840, fire: 240, crit: 15, dmgDictation: 120}}, {name: "Guantes de las Cadenas", base: "guantesastral", props: {armorPct: 450, dex: 55, leech: 9}}, {name: "Botas de Estribo", base: "zapatillasastral", props: {armorPct: 450, dodge: 16, comboStart: 8}}, {name: "Cinto de los Perros Negros", base: "cintosombra", props: {life: 360, potion: 60, killHeal: 50}}], bonus: {2: {resFire: 45, life: 310}, 3: {dmgDictation: 120, fire: 210}, 4: {replayCost: 55, slowFree: true}, 5: {freeReplay: 1, comboStart: 8}, 6: {nearExact: true, comboKeep: true, allStats: 63, xp: 30}}, lvl: 182},
  {id: "marimba", name: "Marimba del Pacífico", pieces: [{name: "Turbante de la Cantadora", base: "capiroteastral", props: {armorPct: 480, life: 320, resLight: 50, xp: 21}}, {name: "Vestidura del Currulao", base: "vestiduraastral", props: {armorPct: 530, life: 480, resAll: 50, dmgCloze: 100}}, {name: "Arco de Chonta", base: "arcoastral", props: {dmgPct: 760, light: 220, crit: 16, manaLeech: 10}}, {name: "Guantes del Marimbero", base: "guantesastral", props: {armorPct: 410, dex: 55, replayCost: 45}}, {name: "Zapatillas de Arena Negra", base: "zapatillasastral", props: {armorPct: 410, dodge: 32}}, {name: "Fajín del Bombo", base: "fajinastral", props: {life: 320, potion: 60, mana: 150}}], bonus: {2: {resLight: 45, life: 280}, 3: {dmgCloze: 100, light: 190}, 4: {replayCost: 55, slowFree: true}, 5: {freeReplay: 1, comboStart: 9}, 6: {nearExact: true, comboKeep: true, allStats: 57, xp: 32}}, lvl: 190},
  {id: "huitaca", tier: "ancestral", name: "La Fiesta de Huitaca", pieces: [{name: "Corona de Flores", base: "capiroteastral", props: {armorPct: 540, life: 360, resLight: 50, xp: 22}}, {name: "Vestidura de la Fiesta", base: "vestiduraastral", props: {armorPct: 590, life: 530, resAll: 50, mf: 100}}, {name: "Espada del Baile", base: "espadaastral", props: {dmgPct: 850, light: 240, crit: 16, comboStart: 9}}, {name: "Escudo de la Luna Llena", base: "escudoastral", props: {armorPct: 510, block: 19, resAll: 45, mana: 170}}, {name: "Guantes de Plumas de Búho", base: "guantesastral", props: {armorPct: 460, dex: 60, allStats: 32}}, {name: "Zapatillas de la Ronda", base: "zapatillasastral", props: {armorPct: 460, dodge: 17, dmgDictation: 120}}], bonus: {2: {resLight: 45, life: 320}, 3: {dmgDictation: 120, light: 210}, 4: {replayCost: 55, slowFree: true}, 5: {freeReplay: 1, comboStart: 9}, 6: {nearExact: true, comboKeep: true, allStats: 64, xp: 33}}, lvl: 196},
  {id: "canocristales", name: "El Río de los Cinco Colores", pieces: [{name: "Yelmo de Macarenia", base: "yelmosombra", props: {armorPct: 510, life: 340, resCold: 50, lifeRegen: 24}}, {name: "Coraza del Lecho de Piedra", base: "corazasombra", props: {armorPct: 560, life: 500, resAll: 50, thorns: 180}}, {name: "Lanza de la Corriente Clara", base: "lanzaastral", props: {dmgPct: 800, cold: 230, crit: 16, dmgCloze: 110}}, {name: "Cinto de las Piedras de Colores", base: "cintosombra", props: {life: 340, potion: 60, mana: 160}}, {name: "Guantes del Agua Transparente", base: "guantesastral", props: {armorPct: 430, dex: 60, manaLeech: 10}}, {name: "Botas de los Pozos", base: "zapatillasastral", props: {armorPct: 430, dodge: 17, xp: 22}}], bonus: {2: {resCold: 45, life: 300}, 3: {dmgCloze: 110, cold: 200}, 4: {replayCost: 55, slowFree: true}, 5: {freeReplay: 1, comboStart: 9}, 6: {nearExact: true, comboKeep: true, allStats: 60, xp: 33}}, lvl: 200},
  {id: "dzogchen", tier: "mitico", name: "La Gran Perfección", pieces: [{name: "Corona del Espacio Primordial", base: "capiroteastral", props: {armorPct: 660, life: 440, resLight: 50, hintCost: 50}}, {name: "Manto de las Cinco Luces", base: "vestiduraastral", props: {armorPct: 730, life: 650, resAll: 50, allStats: 39}}, {name: "Espada del Instante Presente", base: "espadaastral", props: {dmgPct: 1040, light: 300, crit: 16, dmgCloze: 140}}, {name: "Espejo del Estado Natural", base: "escudoastral", props: {armorPct: 620, block: 19, resAll: 45, replayCost: 45}}, {name: "Guantes de la Presencia", base: "guantesastral", props: {armorPct: 560, dex: 60, typoTol: 1}}, {name: "Zapatillas sin Esfuerzo", base: "zapatillasastral", props: {armorPct: 560, dodge: 17, mf: 120}}], bonus: {2: {resLight: 45, life: 390}, 3: {dmgCloze: 140, light: 260}, 4: {replayCost: 55, slowFree: true}, 5: {freeReplay: 1, comboStart: 9}, 6: {nearExact: true, comboKeep: true, allStats: 78, xp: 33, mf: 120}}, lvl: 200},
  // the three ways of the bodhisattva (the shepherd crosses last, the boatman with everyone, the king first to open the way)
  // and the eight manifestations of Guru Rinpoche
  {id: "pastor", name: "El Bodisatva Pastor", pieces: [{name: "Capucha del Pastor", base: "yelmotumbaga", props: {armorPct: 220, life: 150, resLight: 50, hintCost: 50}}, {name: "Manto de Lana del Rebaño", base: "corazatumbaga", props: {armorPct: 250, life: 220, resAll: 35, lifeRegen: 11}}, {name: "Cayado que Va Detrás", base: "baculotumbaga", props: {dmgPct: 350, light: 100, crit: 12, killHeal: 20}}, {name: "Cinto del que Espera", base: "cintotumbaga", props: {life: 150, potion: 60, mf: 40}}, {name: "Sandalias del Último en Cruzar", base: "grebastumbaga", props: {armorPct: 190, dodge: 13, xp: 10}}], bonus: {2: {resLight: 45, life: 130}, 3: {dmgDictation: 50, light: 90}, 4: {replayCost: 55, slowFree: true}, 5: {freeReplay: 1, comboStart: 4, nearExact: true, comboKeep: true, allStats: 26, xp: 15}}, lvl: 88},
  {id: "barquero", tier: "ancestral", name: "El Bodisatva Barquero", pieces: [{name: "Sombrero de Paja del Barquero", base: "yelmoluna", props: {armorPct: 280, life: 180, resCold: 50, replayCost: 45}}, {name: "Ropa de la Travesía", base: "mantoluna", props: {armorPct: 300, life: 270, resAll: 40, vit: 25}}, {name: "Pértiga de la Otra Orilla", base: "tridenteluna", props: {dmgPct: 430, cold: 120, crit: 12, dmgCloze: 60}}, {name: "Faja de la Barca", base: "cordonluna", props: {life: 180, potion: 60, mana: 90}}, {name: "Pies Mojados del Río", base: "zapatosluna", props: {armorPct: 230, dodge: 13, xp: 11}}], bonus: {2: {resCold: 45, life: 160}, 3: {dmgCloze: 60, cold: 110}, 4: {replayCost: 55, slowFree: true}, 5: {freeReplay: 1, comboStart: 5, nearExact: true, comboKeep: true, allStats: 32, xp: 17}}, lvl: 100},
  {id: "rey", tier: "legendario", name: "El Bodisatva Rey", pieces: [{name: "Corona del que Abre Camino", base: "yelmosombra", props: {armorPct: 330, life: 220, resLight: 50, allStats: 19}}, {name: "Armadura del Reino", base: "corazasombra", props: {armorPct: 360, life: 320, resAll: 40, thorns: 120}}, {name: "Espada del Buen Gobierno", base: "mandoblesombra", props: {dmgPct: 520, light: 150, crit: 12, leech: 6}}, {name: "Escudo del Pueblo", base: "escudosombra", props: {armorPct: 310, block: 16, resAll: 35, life: 150}}, {name: "Guantes de la Mano Abierta", base: "guantessombra", props: {armorPct: 280, dex: 35, mf: 60}}, {name: "Cinto del Rey", base: "cintosombra", props: {life: 220, potion: 60, str: 35}}], bonus: {2: {resLight: 45, life: 190}, 3: {dmgDictation: 70, light: 130}, 4: {replayCost: 55, slowFree: true}, 5: {freeReplay: 1, comboStart: 5}, 6: {nearExact: true, comboKeep: true, allStats: 39, xp: 19}}, lvl: 112},
  {id: "shakya", name: "Shakya Senge, el León de los Shakya", pieces: [{name: "Hábito Azafrán", base: "corazasombra", props: {armorPct: 330, life: 300, resAll: 40, ene: 30}}, {name: "Bastón del Monje", base: "varasombra", props: {dmgPct: 470, light: 140, crit: 13, dmgCloze: 60}}, {name: "Cinto de la Renuncia", base: "cintosombra", props: {life: 200, potion: 60, manaLeech: 6}}, {name: "Pies Descalzos del Camino", base: "pezunassombra", props: {armorPct: 250, dodge: 14, xp: 13}}, {name: "Cuenco de Limosna", base: "amuleto", props: {allStats: 18, resAll: 30, mf: 50}}], bonus: {2: {resLight: 45, life: 180}, 3: {dmgCloze: 60, light: 120}, 4: {replayCost: 55, slowFree: true}, 5: {freeReplay: 1, comboStart: 5, nearExact: true, comboKeep: true, allStats: 35, xp: 20}}, lvl: 118},
  {id: "tsokye", tier: "ancestral", name: "Tsokye Dorje, el Vajra Nacido del Lago", pieces: [{name: "Corona del Niño del Lago", base: "capiroteastral", props: {armorPct: 350, life: 240, resCold: 50, mana: 110}}, {name: "Manto Azul del Loto", base: "vestiduraastral", props: {armorPct: 390, life: 350, resAll: 40, lifeRegen: 17}}, {name: "Vajra del Lago", base: "espadaastral", props: {dmgPct: 550, cold: 160, crit: 13, dmgDictation: 80}}, {name: "Guantes de la Flor Abierta", base: "guantesastral", props: {armorPct: 300, dex: 65}}, {name: "Zapatillas sobre el Agua", base: "zapatillasastral", props: {armorPct: 300, dodge: 18}}, {name: "Fajín del Tallo", base: "fajinastral", props: {life: 240, potion: 60, mf: 60}}], bonus: {2: {resCold: 45, life: 210}, 3: {dmgDictation: 80, cold: 140}, 4: {replayCost: 55, slowFree: true}, 5: {freeReplay: 1, comboStart: 6}, 6: {nearExact: true, comboKeep: true, allStats: 41, xp: 21}}, lvl: 128},
  {id: "loden", name: "Loden Chokse, el que Busca el Saber", pieces: [{name: "Diadema del Príncipe Sabio", base: "capiroteastral", props: {armorPct: 340, life: 230, resLight: 50, hintCost: 50}}, {name: "Túnica Blanca del Estudio", base: "vestiduraastral", props: {armorPct: 380, life: 340, resAll: 40, ene: 35}}, {name: "Cetro del Saber Supremo", base: "espadaastral", props: {dmgPct: 540, light: 150, crit: 13, dmgCloze: 70}}, {name: "Guantes del Copista", base: "guantesastral", props: {armorPct: 290, dex: 40, replayCost: 45}}, {name: "Zapatillas del Peregrino Sabio", base: "zapatillasastral", props: {armorPct: 290, dodge: 14, xp: 15}}, {name: "Fajín de los Textos", base: "fajinastral", props: {life: 230, potion: 60, mana: 110}}], bonus: {2: {resLight: 45, life: 200}, 3: {dmgCloze: 70, light: 130}, 4: {replayCost: 55, slowFree: true}, 5: {freeReplay: 1, comboStart: 6}, 6: {nearExact: true, comboKeep: true, allStats: 40, xp: 22}}, lvl: 134},
  {id: "pemagyalpo", tier: "legendario", name: "Pema Gyalpo, el Rey Loto", pieces: [{name: "Corona del Rey Loto", base: "capiroteastral", props: {armorPct: 420, life: 280, resFire: 50, allStats: 25}}, {name: "Manto Real de Oddiyana", base: "vestiduraastral", props: {armorPct: 460, life: 410, resAll: 45, mf: 70}}, {name: "Cetro del Rey Loto", base: "espadaastral", props: {dmgPct: 660, fire: 190, crit: 14, dmgDictation: 90}}, {name: "Espejo del Rey Loto", base: "escudoastral", props: {armorPct: 400, block: 17, resAll: 40, mana: 130}}, {name: "Guantes de Seda Real", base: "guantesastral", props: {armorPct: 360, dex: 45, leech: 7}}, {name: "Zapatillas del Palacio", base: "zapatillasastral", props: {armorPct: 360, dodge: 15, xp: 16}}], bonus: {2: {resFire: 45, life: 250}, 3: {dmgDictation: 90, fire: 170}, 4: {replayCost: 55, slowFree: true}, 5: {freeReplay: 1, comboStart: 7}, 6: {nearExact: true, comboKeep: true, allStats: 50, xp: 24}}, lvl: 144},
  {id: "pandita", tier: "ancestral", name: "Padmasambhava, el Pandita Nacido del Loto", pieces: [{name: "Gorro de Pandita", base: "capiroteastral", props: {armorPct: 430, life: 290, resLight: 50, hintCost: 50}}, {name: "Manto del Maestro", base: "vestiduraastral", props: {armorPct: 470, life: 420, resAll: 45, ene: 40}}, {name: "Khatvanga del Pandita", base: "lanzaastral", props: {dmgPct: 670, light: 190, crit: 14, dmgCloze: 90}}, {name: "Guantes del Debate", base: "guantesastral", props: {armorPct: 360, dex: 45, typoTol: 1}}, {name: "Zapatillas de Nalanda", base: "zapatillasastral", props: {armorPct: 360, dodge: 15, xp: 17}}, {name: "Fajín del Comentario", base: "fajinastral", props: {life: 290, potion: 60, replayCost: 45}}], bonus: {2: {resLight: 45, life: 250}, 3: {dmgCloze: 90, light: 170}, 4: {replayCost: 55, slowFree: true}, 5: {freeReplay: 1, comboStart: 7}, 6: {nearExact: true, comboKeep: true, allStats: 51, xp: 26}}, lvl: 156},
  {id: "nyima", tier: "legendario", name: "Nyima Özer, Rayos de Sol", pieces: [{name: "Moño del Yogui del Sol", base: "capiroteastral", props: {armorPct: 490, life: 330, resFire: 50, mana: 150}}, {name: "Falda de Piel de Tigre", base: "vestiduraastral", props: {armorPct: 540, life: 480, resAll: 45, vit: 40}}, {name: "Khatvanga que Detiene el Sol", base: "lanzaastral", props: {dmgPct: 770, fire: 220, crit: 15, dmgDictation: 110}}, {name: "Brazaletes de Hueso", base: "guantesastral", props: {armorPct: 420, dex: 50, killHeal: 45}}, {name: "Pies del Cementerio", base: "zapatillasastral", props: {armorPct: 420, dodge: 20}}, {name: "Fajín de Rayos", base: "fajinastral", props: {life: 330, potion: 60, lifeRegen: 23}}], bonus: {2: {resFire: 45, life: 290}, 3: {dmgDictation: 110, fire: 190}, 4: {replayCost: 55, slowFree: true}, 5: {freeReplay: 1, comboStart: 8}, 6: {nearExact: true, comboKeep: true, allStats: 58, xp: 28}}, lvl: 168},
  {id: "sengedradrok", tier: "mitico", name: "Senge Dradrok, el Rugido del León", pieces: [{name: "Corona de Cinco Calaveras", base: "capiroteastral", props: {armorPct: 620, life: 410, resFire: 50, allStats: 36}}, {name: "Manto de Llamas", base: "vestiduraastral", props: {armorPct: 680, life: 600, resAll: 50, thorns: 220}}, {name: "Vajra del Rugido", base: "espadaastral", props: {dmgPct: 970, fire: 280, crit: 15, dmgDictation: 130}}, {name: "Mano del Escorpión", base: "guantesastral", props: {armorPct: 520, dex: 55, leech: 9}}, {name: "Pies que Pisan el Orgullo", base: "zapatillasastral", props: {armorPct: 520, dodge: 16, mf: 110}}, {name: "Fajín del León", base: "fajinastral", props: {life: 410, potion: 60, str: 55}}], bonus: {2: {resFire: 45, life: 360}, 3: {dmgDictation: 130, fire: 240}, 4: {replayCost: 55, slowFree: true}, 5: {freeReplay: 1, comboStart: 8}, 6: {nearExact: true, comboKeep: true, allStats: 73, xp: 31, mf: 110}}, lvl: 186},
  {id: "drollo", tier: "mitico", name: "Dorje Drolö, el de la Tigresa", pieces: [{name: "Corona Iracunda", base: "capiroteastral", props: {armorPct: 660, life: 440, resFire: 50, allStats: 39}}, {name: "Piel de Tigre en Llamas", base: "vestiduraastral", props: {armorPct: 720, life: 640, resAll: 50, thorns: 230}}, {name: "Purba del Tigre", base: "espadaastral", props: {dmgPct: 1030, fire: 300, crit: 16, dmgDictation: 140}}, {name: "Mano del Vajra", base: "guantesastral", props: {armorPct: 550, dex: 60, killHeal: 60}}, {name: "Pies sobre la Tigresa", base: "zapatillasastral", props: {armorPct: 550, dodge: 21}}, {name: "Fajín de Piel de Tigre", base: "fajinastral", props: {life: 440, potion: 60, leech: 10}}], bonus: {2: {resFire: 45, life: 390}, 3: {dmgDictation: 140, fire: 260}, 4: {replayCost: 55, slowFree: true}, 5: {freeReplay: 1, comboStart: 9}, 6: {nearExact: true, comboKeep: true, allStats: 77, xp: 33, mf: 120}}, lvl: 198},
];

// ---------- gems ----------
// Socketed effect depends on where the gem sits: weapon / armour (head, body) / shield.
export const GEM_GRADES = ["Fragmento de", "", "perfecto"];
// shades: one colour per grade (fragment, plain, perfect), darker to brighter, to tell them apart
export const GEMS = {
  rubi:      { name: "rubí", fname: "Rubí", color: "#e0464e", shades: ["#a3303a", "#e0464e", "#ff9196"], weapon: ["fire", [3, 7, 14]], armor: ["life", [8, 16, 30]], off: ["resFire", [12, 20, 30]] },
  zafiro:    { name: "zafiro", fname: "Zafiro", color: "#4a7bff", shades: ["#2c4aa6", "#4a7bff", "#a3bfff"], weapon: ["cold", [3, 7, 14]], armor: ["mana", [8, 16, 30]], off: ["resCold", [12, 20, 30]] },
  topacio:   { name: "topacio", fname: "Topacio", color: "#f2c230", shades: ["#a8821a", "#f2c230", "#ffea8a"], weapon: ["light", [4, 9, 18]], armor: ["mf", [8, 15, 25]], off: ["resLight", [12, 20, 30]] },
  esmeralda: { name: "esmeralda", fname: "Esmeralda", color: "#2fbf6a", shades: ["#1d7a44", "#2fbf6a", "#86f0b0"], weapon: ["poison", [4, 9, 18]], armor: ["dex", [3, 6, 10]], off: ["resPoison", [12, 20, 30]] },
  amatista:  { name: "amatista", fname: "Amatista", color: "#a65fe0", shades: ["#6a3a96", "#a65fe0", "#d9adff"], weapon: ["dmgPct", [10, 20, 35]], armor: ["str", [3, 6, 10]], off: ["armor", [8, 16, 30]] },
  diamante:  { name: "diamante", fname: "Diamante", color: "#e8f2ff", shades: ["#929eae", "#e8f2ff", "#a6f2ff"], weapon: ["crit", [2, 4, 6]], armor: ["replayCost", [8, 15, 25]], off: ["resAll", [6, 10, 15]] },
};

// ---------- potions ----------
export const POTIONS = {
  life:  { name: "Poción de vida", short: "Vida", icon: "health-potion", color: "#d23a3a", heal: [30, 80, 200], price: [25, 75, 200] },
  mana:  { name: "Poción de maná", short: "Maná", icon: "round-potion", color: "#3a64d2", mana: [25, 60, 150], price: [25, 75, 200] },
  rejuv: { name: "Poción de rejuvenecimiento", short: "Rejuv.", icon: "standing-potion", color: "#9d4ad6", pct: 0.4, price: [300, 300, 300] },
};
export const POTION_TIER_NAMES = ["menor", "", "mayor"];

// ---------- classes ----------
export const CLASSES = {
  cazadora: {
    name: "Cazadora", icon: "bow-arrow",
    blurb: "Rápida y certera. Sus ataques a distancia son ejercicios de huecos, y hacen más daño.",
    stats: { str: 15, dex: 25, vit: 15, ene: 10 }, passive: { dmgCloze: 25, crit: 3 }, start: ["honda", "capucha"],
  },
  guerrero: {
    name: "Guerrero", icon: "machete",
    blurb: "Aguanta golpes y dicta frases enteras. Su daño en dictado es mayor.",
    stats: { str: 25, dex: 15, vit: 25, ene: 5 }, passive: { dmgDictation: 20, life: 10 }, start: ["machete", "rodela"],
  },
  chaman: {
    name: "Chamán", icon: "wizard-staff",
    blurb: "Mucho maná para repetir y pedir pistas, que además le cuestan menos.",
    stats: { str: 10, dex: 15, vit: 15, ene: 30 }, passive: { replayCost: 20, hintCost: 25, manaRegen: 1 }, start: ["varita", "tunica"],
  },
  brujo: {
    name: "Brujo", icon: "crystal-ball",
    blurb: "Lanza hechizos con varitas y bastones: fuego, escarcha, rayo y un escudo. Cada hechizo cuesta maná y lo potencia tu acierto en la frase.",
    stats: { str: 10, dex: 15, vit: 10, ene: 35 }, passive: { spellDmg: 10, manaRegen: 1 }, start: ["varita", "tunica"], spells: true,
  },
};

// ---------- class abilities ----------
// One per class, used in a fight with F (Alt+F while typing) or its button. Costs `cost` of your maximum
// mana. arm: waits for your next hit that lands (a hit with no word right doesn't use it up).
// volley: that hit lands whole on every monster. double: that hit does twice the damage.
// roar: for `turns` monster turns, the damage you take is halved. heal: that share of your maximum life,
// now, and it puts out a boss's fire.
export const POWERS = {
  cazadora: { id: "lluvia", name: "Lluvia de flechas", icon: "arrow-cluster", color: "#9fd66b", cost: 0.4, arm: true, volley: true,
    desc: "Tu próximo golpe cae entero sobre todos los monstruos, no solo sobre el objetivo." },
  guerrero: { id: "grito", name: "Grito de guerra", icon: "shouting", color: "#e8884a", cost: 0.4, roar: true, turns: 3,
    desc: "Los monstruos se encogen: durante sus próximos 3 turnos te hacen la mitad de daño." },
  chaman: { id: "sanar", name: "Sanación", icon: "healing", color: "#6fd0a8", cost: 0.4, heal: 0.4,
    desc: "Recuperas al momento el 40% de tu vida máxima, y se apaga el fuego que te quema." },
  brujo: { id: "sobrecarga", name: "Sobrecarga", icon: "magic-swirl", color: "#c48cff", cost: 0.4, arm: true, double: true,
    desc: "Tu próximo golpe, con hechizo o sin él, hace el doble de daño." },
};

// ---------- the brujo's spells ----------
// One is kept prepared and goes off with every attack, while there's mana for it; the line's accuracy
// sets its strength, like any hit. They need a magic weapon (varita, bastón, cetro, vara: `magic: true`),
// and their damage grows with energía instead of destreza. cost: × the replay price at your level.
// mult: the weapon's hit turned into the element. splash: that share of it to every other monster.
// all: the whole of it to every monster. freeze: turns the target skips its attacks (from 60% accuracy).
// shield: absorbs damage for the rest of the fight: accuracy × (6 + 2.5 per level) × spell power; recast, it
// adds up to your maximum life at most.
export const SPELLS = [
  { id: "fuego", key: "q", name: "Bola de fuego", icon: "small-fire", color: "#f0743a", el: "fire", lvl: 1, cost: 2.5, mult: 1.25, splash: 0.35,
    desc: "Daño de fuego al objetivo; un 35% salpica a todos los demás." },
  { id: "escarcha", key: "w", name: "Escarcha", icon: "snowflake-2", color: "#7fb8ff", el: "cold", lvl: 6, cost: 2, mult: 1, freeze: 2,
    desc: "Daño de frío; con un 60% de acierto o más, congela al objetivo: no ataca ni ahora ni en el turno siguiente." },
  { id: "rayo", key: "e", name: "Rayo", icon: "lightning-helix", color: "#f2d43c", el: "light", lvl: 12, cost: 3.5, mult: 0.65, all: true,
    desc: "Daño de rayo a todos los monstruos a la vez." },
  { id: "escudo", key: "r", name: "Escudo arcano", icon: "crystal-ball", color: "#b48cff", lvl: 18, cost: 3, shield: 1,
    desc: "Tu golpe de siempre, y un escudo que absorbe daño hasta el final del combate (más con más acierto y energía; como mucho, tu vida máxima)." },
];

// ---------- pets and mounts ----------
// Won by finishing a whole episode (20 minutes or more) with every line perfect both ways (all the gaps,
// every sentence written whole): on Normal or harder, a pet; on Difícil, a mount. One of each per episode,
// a coat you don't have yet while there is one. The one you take along (Personaje → Compañeros) is shown
// next to you, and adds its props like gear does. Art: scripts/build_companions.py.
export const PETS = {
  canela:   { name: "Canela", coat: "rojizo", props: { gf: 30 }, desc: "Olfatea el oro: los enemigos sueltan más." },
  azabache: { name: "Azabache", coat: "negro", props: { dodge: 6 }, desc: "Ladra a tiempo: esquivas más." },
  copito:   { name: "Copito", coat: "blanco", props: { typoTol: 1 }, desc: "Oído fino: se te perdona una letra más por palabra." },
  humo:     { name: "Humo", coat: "gris", props: { mf: 25 }, desc: "Escarba entre los restos: más objetos mágicos." },
  cacao:    { name: "Cacao", coat: "chocolate", props: { freeReplay: 1 }, desc: "Te la repite: una escucha más gratis por frase." },
};
export const PET_KIND = "perro criollo";
export const MOUNTS = {
  noche:    { name: "Noche", coat: "negro" },
  castano:  { name: "Castaño", coat: "castaño" },
  palomino: { name: "Palomino", coat: "dorado" },
  tordo:    { name: "Tordo", coat: "tordo" },
  lucero:   { name: "Lucero", coat: "blanco" },
};
export const MOUNT_PROPS = { xp: 10, gf: 10 }; // every horse: you get further, faster
export const COMPANION_MIN_SECONDS = 20 * 60;

// ---------- monsters ----------
// hp/dmg are multipliers on the level curve. el: element of its attacks.
export const MONSTERS = {
  espanto:   { name: "Espanto de niebla", icon: "ghost", color: "#b9c6cf", hp: 0.8, dmg: 1.0, el: "cold" },
  cuervo:    { name: "Cuervo del páramo", icon: "raven", color: "#6f7480", hp: 0.6, dmg: 0.9 },
  frailejon: { name: "Frailejón maldito", icon: "evil-tree", color: "#a7b06a", hp: 1.4, dmg: 0.7 },
  lobo:      { name: "Lobo de niebla", icon: "wolf-head", color: "#9aa2a8", hp: 1.0, dmg: 1.2 },
  sapo:      { name: "Sapo de ciénaga", icon: "frog", color: "#7fae5a", hp: 0.9, dmg: 0.9, el: "poison" },
  caiman:    { name: "Caimán negro", icon: "croc-jaws", color: "#5e7a55", hp: 1.5, dmg: 1.3 },
  sanguijuela: { name: "Sanguijuela gigante", icon: "leeching-worm", color: "#a0525a", hp: 0.7, dmg: 0.8, vamp: true },
  ahogado:   { name: "Pescador ahogado", icon: "shambling-zombie", color: "#7d9b9a", hp: 1.3, dmg: 1.0, el: "cold" },
  arana:     { name: "Araña tejedora", icon: "hanging-spider", color: "#7b6a8c", hp: 0.9, dmg: 1.1, el: "poison" },
  coral:     { name: "Serpiente coral", icon: "cobra", color: "#d0603e", hp: 0.8, dmg: 1.3, el: "poison" },
  mico:      { name: "Rata de monte", icon: "rat", color: "#a07a52", hp: 1.0, dmg: 1.0 },
  avispa:    { name: "Avispa de fuego", icon: "wasp-sting", color: "#e09a30", hp: 0.6, dmg: 1.2, el: "fire" },
  toro:      { name: "Toro negro", icon: "charging-bull", color: "#55504a", hp: 1.6, dmg: 1.4 },
  jinete:    { name: "Cimarrón del llano", icon: "cloaked-figure-on-horseback", color: "#8a8fb0", hp: 1.2, dmg: 1.2, el: "light" },
  alacran:   { name: "Ciempiés del llano", icon: "centipede", color: "#c09050", hp: 0.9, dmg: 1.2, el: "poison" },
  chulo:     { name: "Chulo carroñero", icon: "vulture", color: "#6a5f58", hp: 0.8, dmg: 1.0 },
  guardian:  { name: "Guardián de piedra", icon: "rock-golem", color: "#9a9184", hp: 2.0, dmg: 1.1 },
  osamenta:  { name: "Osamenta", icon: "skeleton", color: "#d8d2c0", hp: 0.9, dmg: 1.1 },
  momia:     { name: "Momia del cerro", icon: "mummy-head", color: "#b8a77c", hp: 1.4, dmg: 1.0, el: "poison" },
  vampiro:   { name: "Murciélago vampiro", icon: "evil-bat", color: "#7a4a6a", hp: 0.7, dmg: 1.0, vamp: true },
  duende:    { name: "Duende travieso", icon: "goblin", color: "#8cab6a", hp: 0.8, dmg: 1.0 },
  diablillo: { name: "Diablillo", icon: "imp", color: "#c0503a", hp: 0.9, dmg: 1.3, el: "fire" },
  baba:      { name: "Baba del pantano", icon: "slime", color: "#7fbf8f", hp: 1.4, dmg: 0.8, el: "poison" },
  zaino:     { name: "Zaíno salvaje", icon: "boar", color: "#7a5a48", hp: 1.3, dmg: 1.2 },
  oso:       { name: "Oso de anteojos", icon: "bear-head", color: "#4a4038", hp: 1.8, dmg: 1.3 },
};

// Easy-mode creatures: smaller, slower cousins.
export const EASY_MONSTERS = {
  babosa:      { name: "Babosa", icon: "slime", color: "#9fc7a3", hp: 0.6, dmg: 0.6 },
  sapito:      { name: "Sapito", icon: "frog", color: "#9cc47a", hp: 0.6, dmg: 0.6 },
  culebrita:   { name: "Culebrita", icon: "snake", color: "#b9a46a", hp: 0.55, dmg: 0.7 },
  duendecillo: { name: "Duendecillo", icon: "goblin", color: "#a7c48a", hp: 0.65, dmg: 0.6 },
  cuervito:    { name: "Cuervito", icon: "raven", color: "#8a8f99", hp: 0.5, dmg: 0.6 },
  murcieguito: { name: "Murcieguito", icon: "evil-bat", color: "#9a7a8a", hp: 0.5, dmg: 0.6 },
  jabato:      { name: "Jabato", icon: "boar", color: "#9a7a62", hp: 0.7, dmg: 0.6 },
  conejo:      { name: "Conejo travieso", icon: "rabbit", color: "#e8e2d8", hp: 0.6, dmg: 0.5 },
};
Object.assign(MONSTERS, EASY_MONSTERS);
export const EASY_ROSTER = {
  paramo: ["cuervito", "babosa", "duendecillo"],
  cienaga: ["sapito", "babosa", "culebrita"],
  selva: ["culebrita", "conejo", "duendecillo"],
  llano: ["jabato", "cuervito", "culebrita"],
  ruinas: ["murcieguito", "babosa", "duendecillo"],
  abismo: Object.keys(EASY_MONSTERS),
};

// Difficulty. Easy: short chunks of each line, gentle monsters, worse rewards.
// maxWords: longest chunk you hear per attack. safeAcc: at or above this accuracy, nothing hits you.
export const DIFFICULTY = {
  facil:   { name: "Fácil", maxWords: 4, cloze: 1, dmgTaken: 0.3, safeAcc: 0.7, hp: 0.8, xp: 0.7, gold: 0.6, loot: 0.5, mf: -40, elite: 0.4, noTop: true, rareKeep: 0.35, costMul: 0.5, paidListens: 2, freeReward: 0.35,
             desc: "Frases cortas (hasta 4 palabras), enemigos débiles, ayudas a mitad de precio y escuchas ilimitadas (con menos recompensa). Menos experiencia y oro; no caen objetos únicos ni de conjunto, y pocos raros." },
  medio:   { name: "Normal", maxWords: 8, cloze: 2, dmgTaken: 0.65, safeAcc: 0.9, hp: 1, xp: 1, gold: 1, loot: 1, mf: 0, elite: 1,
             desc: "Trozos de hasta 8 palabras. Los enemigos pegan menos." },
  dificil: { name: "Difícil", maxWords: 99, cloze: 4, dmgTaken: 1, safeAcc: 1, hp: 1, xp: 1.25, gold: 1.3, loot: 1.5, mf: 50, elite: 1.6,
             desc: "La frase entera. Solo la perfección te protege. Más experiencia y mejor botín." },
};
// Monster modifiers that make the audio itself harder; easy-mode bosses don't use them.
export const LISTENING_MODS = ["murmullo", "veloz", "eco", "maldito"];

// Bosses: fixed, one per zone. mods are drawn from MONSTER_MODS. Each has its own art (rpg/bosses, drawn by
// scripts/build_bosses.py), an entrance, a signature attack and a second phase from half its life:
//   special: every `every` turns it gets ready (you see it coming: a meter on its bar), and on the next line it
//     lets go: only a perfect line gets you out of the way (on Fácil, a line good enough to dodge). mult: how
//     hard it hits, times a normal blow. Plus what it does: steal (a potion, or gold), tangle (n lines without
//     Despacio or Pista, and it heals), burn (n turns of fire, put out by a perfect line), wail (its cry plays
//     over the line it's about to hit you on).
//   p2: what changes at half life: step (the meter fills faster), every, summon [kind, n], dmg, deal.
//   last: its last words.
export const BOSSES = {
  silbon:     { name: "El Silbón", title: "El que silba en el páramo", icon: "hooded-figure", color: "#9fe8ff", hp: 1.2, dmg: 1.0, el: "cold", mods: ["murmullo"], minions: "espanto",
                intro: "Si lo oyes cerca, está lejos. Si lo oyes lejos… ya lo tienes encima.",
                special: { name: "El silbido", every: 7, mult: 2.6, notes: ["do", "re", "mi", "fa", "sol", "la", "si"],
                  ready: "El Silbón llega al <b>si</b>. Ya casi no se oye: lo tienes encima. <b>Solo una frase perfecta</b> te salva.",
                  hit: "El silbido se apaga y el Silbón te alcanza.", dodge: "Escribes la frase entera: el silbido vuelve a sonar lejos." },
                p2: { step: 2, text: "El Silbón crece hasta las copas de los frailejones. Ahora silba más rápido." },
                last: "El saco cae al suelo. Los huesos, por fin, se quedan quietos." },
  mohan:      { name: "El Mohán", title: "El señor del río", icon: "ogre", color: "#ffc83a", hp: 1.4, dmg: 1.0, el: "cold", mods: ["piedra", "vampirico"], minions: "ahogado",
                intro: "Lo que cae al río es suyo. Y tú estás con el agua hasta las rodillas.",
                special: { name: "Al fondo del río", every: 4, mult: 2, steal: true,
                  ready: "El Mohán te agarra del tobillo. <b>Solo una frase perfecta</b> te suelta.",
                  hit: "Te arrastra al agua", dodge: "Te sueltas de un tirón antes de que te hunda." },
                p2: { summon: ["ahogado", 2], text: "El Mohán se levanta del agua. Los ahogados salen con él." },
                last: "El Mohán se hunde en el río. El agua devuelve lo que te quitó." },
  madremonte: { name: "La Madremonte", title: "La dueña de la selva", icon: "tree-face", color: "#c8ff3a", hp: 1.5, dmg: 1.1, el: "poison", mods: ["veloz", "regenera"], minions: "arana",
                intro: "No se le ve la cara. La selva entera es su cuerpo, y la selva no te quiere aquí.",
                special: { name: "Enredadera", every: 4, mult: 1.6, tangle: 2, heal: 0.08,
                  ready: "Las raíces se mueven bajo tus pies. <b>Solo una frase perfecta</b> te deja saltar a tiempo.",
                  hit: "Las enredaderas te atrapan: <b>2 frases sin Despacio ni Pista</b>, y ella se cura.", dodge: "Saltas: las raíces se cierran en el aire." },
                p2: { summon: ["arana", 2], text: "La selva despierta: las arañas bajan de los árboles." },
                last: "La Madremonte se deshace en hojas secas. La lluvia para un momento." },
  bolafuego:  { name: "La Bola de Fuego", title: "La que cruza el llano ardiendo", icon: "burning-skull", color: "#ff8a1a", hp: 1.3, dmg: 1.2, el: "fire", mods: ["rapido"], minions: "diablillo",
                intro: "Cruza el llano de noche, rodando y rugiendo. Lo que toca, arde.",
                special: { name: "Embestida", every: 3, mult: 2.2, burn: 3,
                  ready: "La Bola de Fuego toma impulso. <b>Solo una frase perfecta</b> te aparta a tiempo.",
                  hit: "Te embiste: <b>ardes</b> durante 3 turnos. Una frase perfecta apaga el fuego.", dodge: "Te apartas y pasa rugiendo a tu lado." },
                p2: { every: 2, text: "La Bola de Fuego arde azul: más caliente, más rápida." },
                last: "El fuego se apaga. Queda una calavera humeando en el pasto." },
  llorona:    { name: "La Llorona", title: "La que llora junto al río", icon: "floating-ghost", color: "#cfeeff", hp: 1.6, dmg: 1.2, el: "cold", mods: ["eco", "ladron"], minions: "osamenta",
                intro: "«¡Ay, mis hijos!». Su llanto lo tapa todo. Escucha por encima de él.",
                special: { name: "El llanto", every: 3, mult: 2, wail: true,
                  ready: "La Llorona va a llorar. <b>Su llanto sonará encima de la próxima frase</b>: solo una frase perfecta te protege.",
                  hit: "Su llanto te hiela la sangre.", dodge: "Oyes la frase por encima del llanto." },
                p2: { every: 2, scream: true, text: "La Llorona se vuelve. Por fin le ves la cara." },
                last: "«¡Ay, mis hijos!»… y el llanto se apaga en el río." },
  mandingas:  { name: "El Mandingas", title: "El que hace tratos", icon: "devil-mask", color: "#ff4a2a", hp: 1.8, dmg: 1.3, el: "fire", mods: ["veloz", "fuerte", "maldito"], minions: "diablillo",
                intro: "Muy elegante, muy amable. Hace tratos con quien no escucha bien. No firmes nada.",
                special: { name: "Fuego del infierno", every: 4, mult: 2.6,
                  ready: "El Mandingas aviva la llama de su mano. <b>Solo una frase perfecta</b> te aparta.",
                  hit: "Te lanza el fuego del infierno.", dodge: "La llama revienta donde estabas hace un segundo." },
                p2: { deal: true, text: "El Mandingas baja la llama y sonríe: «Hablemos de negocios»." },
                last: "El Mandingas se hunde en el suelo, riéndose: «Nos volveremos a ver»." },
};

// Champion / unique monster modifiers. Some change the listening itself.
// What monsters shrug off and what hurts them more, against the fire / cold / lightning / poison
// part of your damage (physical damage is never resisted). 100 = immune, 50 = half, -50 = 1.5×.
export const MONSTER_RES = {
  espanto:     { cold: 100, poison: 100, fire: -50 },
  cuervo:      { light: -50 },
  frailejon:   { fire: -75, poison: 50 },
  lobo:        { cold: 50, fire: -25 },
  sapo:        { poison: 75, cold: -50 },
  caiman:      { poison: 50, cold: -50 },
  sanguijuela: { poison: 50, light: -50 },
  ahogado:     { cold: 100, poison: 100, light: -50, fire: -25 },
  arana:       { poison: 100, fire: -50 },
  coral:       { poison: 100, cold: -50 },
  mico:        { poison: 50 },
  avispa:      { fire: 100, cold: -50 },
  toro:        { fire: 25, light: -25 },
  jinete:      { light: 100, poison: -50 },
  alacran:     { poison: 100, cold: -25 },
  chulo:       { poison: 75, light: -50 },
  guardian:    { poison: 100, light: 50, cold: -50 },
  osamenta:    { poison: 100, cold: 50, light: -50 },
  momia:       { poison: 100, fire: -100 },
  vampiro:     { poison: 50, fire: -50 },
  duende:      { light: -25 },
  diablillo:   { fire: 100, cold: -75 },
  baba:        { poison: 100, fire: -50, light: -25 },
  zaino:       { poison: 25, cold: -25 },
  oso:         { cold: 75, fire: -25 },
  // easy
  babosa:      { poison: 100, fire: -50 },
  sapito:      { poison: 50 },
  culebrita:   { poison: 75 },
  cuervito:    { light: -50 },
  murcieguito: { fire: -50 },
  // bosses
  silbon:      { cold: 100, poison: 100, fire: -50 },
  mohan:       { cold: 100, light: -50 },
  madremonte:  { poison: 100, cold: 50, fire: -50 },
  bolafuego:   { fire: 100, cold: -75 },
  llorona:     { cold: 100, poison: 100, light: -50, fire: -25 },
  mandingas:   { fire: 100, poison: 50, cold: -50 },
};

export const MONSTER_MODS = {
  fuerte:    { name: "Fuerte", desc: "Golpea un 50% más fuerte" },
  rapido:    { name: "Rápido", desc: "Ataca dos veces por turno" },
  piedra:    { name: "Piel de piedra", desc: "Recibe un 35% menos de daño" },
  vampirico: { name: "Vampírico", desc: "Se cura con el daño que hace" },
  regenera:  { name: "Regenerador", desc: "Recupera un poco de vida cada turno, salvo si aciertas la frase entera" },
  ladron:    { name: "Ladrón de maná", desc: "Cada golpe te quita maná" },
  maldito:   { name: "Maldito", desc: "Tus pistas cuestan el doble" },
  murmullo:  { name: "Murmullo", desc: "Las frases se oyen más bajo" },
  veloz:     { name: "Parlanchín", desc: "Las frases suenan un 15% más rápido" },
  eco:       { name: "Eco", desc: "No puedes escuchar despacio" },
  igneo:     { name: "Ígneo", desc: "Sus golpes queman", el: "fire" },
  gelido:    { name: "Gélido", desc: "Sus golpes congelan", el: "cold" },
  electrico: { name: "Eléctrico", desc: "Sus golpes electrizan", el: "light" },
};
export const RANDOM_MODS = ["fuerte", "rapido", "piedra", "vampirico", "regenera", "ladron", "maldito", "murmullo", "veloz", "eco", "igneo", "gelido", "electrico"];
export const UNIQUE_MONSTER_NAMES = [
  "Uñanegra", "Ojo de Niebla", "Rasgacielos", "Doña Penumbra", "El Tuerto Malaclase", "Colmillo Viejo", "La Comadre Sombría",
  "Pataepalo", "El Sin Nombre", "Lenguadeplata", "Malagüero", "Don Ceniza", "La Viuda del Monte", "Quiebrahuesos", "El Mudo",
];

// ---------- zones ----------
export const ZONES = [
  { id: "paramo", name: "Páramo de la Niebla", lvl: [1, 5], monsters: ["espanto", "cuervo", "frailejon", "lobo"], boss: "silbon", packs: 6,
    blurb: "Frailejones, frío y una niebla en la que se oye un silbido." },
  { id: "cienaga", name: "Ciénaga del Mohán", lvl: [6, 11], monsters: ["sapo", "caiman", "sanguijuela", "ahogado", "baba"], boss: "mohan", packs: 7,
    blurb: "Agua quieta, caimanes y pescadores que nunca volvieron." },
  { id: "selva", name: "Selva del Chocó", lvl: [12, 18], monsters: ["arana", "coral", "mico", "avispa", "duende"], boss: "madremonte", packs: 7,
    blurb: "Llueve siempre. Algo se mueve entre las hojas." },
  { id: "llano", name: "Llanos en Llamas", lvl: [19, 26], monsters: ["toro", "jinete", "alacran", "chulo", "zaino"], boss: "bolafuego", packs: 8,
    blurb: "La sabana arde de noche y nadie sabe por qué." },
  { id: "ruinas", name: "Ruinas de Piedra", lvl: [27, 34], monsters: ["guardian", "osamenta", "momia", "vampiro", "oso"], boss: "llorona", packs: 8,
    blurb: "Estatuas antiguas que vigilan, y un llanto junto al río." },
  { id: "abismo", name: "El Abismo", lvl: [35, 99], monsters: Object.keys(MONSTERS), boss: "mandingas", packs: 8, endless: true,
    blurb: "Sin fondo. Cada descenso es más duro, y el botín, mejor." },
];

// ---------- the rainbow items: only from Doña Remedios' tunjo ----------
// One sentence, one try, at most once a day and at a price (main.js). Each is one of a kind: a
// collection of twelve, kept in the village (Colección). `look` is the base whose shape it wears,
// redrawn in rainbow (scripts/tunjo_art.py, which also draws its icon); `family` the bases its damage
// or defence come from, the best one for your level when it falls (a slot name: any base of that slot).
// `props` are its own; on top it gets a mítico's worth of properties for its level.
const SWORDS = ["espada", "estoque", "espadon", "mandoble", "sablehueso", "estoqueesmeralda", "espadacatatumbo", "sableluna", "mandoblesombra", "espadaastral"];
export const TUNJO_ITEMS = [
  { id: "filo", name: "Filo de Cuchavira", look: "espada", family: SWORDS, props: { dmgDictation: 60, comboKeep: 1, crit: 12 },
    flavor: "Cuchavira tendió su arco sobre el agua y lo cortó con esto. Cada tajo deja siete colores en el aire." },
  { id: "arco", name: "Arco de las Siete Aguas", look: "arcolargo", family: ["arco", "arcocurvo", "arcolargo", "arcoobsidiana", "arcoluna", "arcoastral"],
    props: { dmgCloze: 60, comboStart: 5, dex: 30 }, flavor: "Sus flechas caen como la lluvia cuando hace sol." },
  { id: "vara", name: "Vara de la Lluvia con Sol", look: "bastonruna", family: ["varita", "baston", "cetro", "varaanillada", "bastonruna", "varahueso", "cetroesmeralda", "baculotumbaga", "varasombra"],
    props: { spellDmg: 60, slowFree: 1, manaRegen: 12 }, flavor: "Donde la apoyas, el páramo se pinta de colores un momento." },
  { id: "rodela", name: "Rodela del Aguacero", look: "escudo", family: "off", props: { block: 15, thorns: 250, resAll: 15 },
    flavor: "El agua que la golpea sale de colores." },
  { id: "corona", name: "Corona del Arco Alto", look: "corona", family: "head", props: { xp: 25, typoTol: 1, allStats: 10 },
    flavor: "Quien la lleva oye primero el trueno y después la luz." },
  { id: "manto", name: "Manto de Cuchavira", look: "tunica", family: "body", props: { life: 450, nearExact: 1, armorPct: 120 },
    flavor: "Tejido con el borde del arcoíris, por donde se deshilacha." },
  { id: "manos", name: "Manos del Tejedor de Colores", look: "guantes", family: "hands", props: { hintCost: 60, typoTol: 1, leech: 8 },
    flavor: "Separan una palabra de otra como quien separa hilos." },
  { id: "pasos", name: "Pasos sobre el Arcoíris", look: "botas", family: "feet", props: { dodge: 15, potion: 50, gf: 80 },
    flavor: "Para cruzar de un cerro a otro sin tocar el valle." },
  { id: "faja", name: "Faja de los Siete Hilos", look: "faja", family: "belt", props: { beltSlots: 2, life: 250, lifeRegen: 25 },
    flavor: "Un hilo por color, y ninguno se anuda con otro." },
  { id: "oyente", name: "El Tunjo que Escucha", look: "amuleto", family: ["amuleto"], props: { dmgDictation: 30, dmgCloze: 30, xp: 15, comboStart: 3 },
    flavor: "Una figurita de oro con la oreja pegada al pecho de quien la lleva." },
  { id: "gota", name: "La Gota Partida", look: "anillo", family: ["anillo"], props: { mf: 70, gf: 70, allStats: 6 },
    flavor: "Una gota de lluvia que se partió en colores y no se volvió a juntar." },
  { id: "eco", name: "Anillo del Eco", look: "sortija", family: ["sortija"], props: { freeReplay: 2, replayCost: 40, manaLeech: 6 },
    flavor: "Repite lo último que oíste, más bajito, hasta que lo entiendes." },
];
