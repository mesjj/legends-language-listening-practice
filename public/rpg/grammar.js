// Forms of haber and the tenses around them. Runes are gone from the game: this now only names the
// tense of a word you missed ("pluscuamperfecto"), and its table converts an old save's haber runes.
const lc = (w) => w.toLowerCase().normalize("NFC").replace(/[^\p{L}]/gu, "");

// Irregular stems are listed out; regular verbs are rare enough in these tenses that a short list
// of common ones is enough, and a list never mistakes "para" or "cara" for a verb.
const COND_STEMS = ["habr", "ser", "podr", "tendr", "har", "dir", "deber", "querr", "sabr", "estar", "ir", "vendr", "pondr", "saldr", "valdr", "cabr",
  "gustar", "encantar", "importar", "molestar", "preferir", "parecer", "quedar", "pasar", "llegar", "dar", "ver", "creer", "hablar", "vivir", "volver"];
const COND = COND_STEMS.flatMap((s) => ["ía", "ías", "íamos", "íais", "ían"].map((e) => s + e));
const IMPSUBJ_STEMS = ["hubie", "tuvie", "pudie", "quisie", "hicie", "dije", "estuvie", "supie", "vinie", "pusie", "die", "vie", "anduvie", "traje", "cupie",
  "fue", "traduje", "conduje", "pidie", "sintie", "durmie", "murie", "siguie", "creye", "leye", "oye",
  "habla", "llega", "pasa", "deja", "termina", "necesita", "escucha", "toma", "trabaja", "lleva", "queda", "cambia", "pensa", "mira", "llama",
  "comie", "vivie", "volvie", "salie", "conocie", "entendie", "perdie", "escribie", "vendie", "compartie", "repitie", "atrevie"];
const IMPSUBJ = IMPSUBJ_STEMS.flatMap((s) => {
  const accented = s.slice(0, -1) + { a: "á", e: "é" }[s.at(-1)];
  return [s + "ra", s + "ras", accented + "ramos", s + "rais", s + "ran", s + "se", s + "ses", accented + "semos", s + "sen"];
}).filter((f) => !["fuera", "fueras"].includes(f)); // "fuera" is mostly "outside"
const PRESSUBJ = ["sea", "seas", "seamos", "sean", "esté", "estés", "estemos", "estén", "tenga", "tengas", "tengamos", "tengan", "pueda", "puedas", "podamos", "puedan",
  "haga", "hagas", "hagamos", "hagan", "diga", "digas", "digamos", "digan", "sepa", "sepas", "sepamos", "sepan", "quiera", "quieras", "queramos", "quieran",
  "vaya", "vayas", "vayamos", "vayan", "venga", "vengas", "vengamos", "vengan", "ponga", "pongas", "pongan", "salga", "salgas", "salgan", "conozca", "conozcas",
  "conozcan", "dé", "des", "den", "vea", "veas", "veamos", "vean", "oiga", "oigas", "traiga", "traigan", "entienda", "entiendas", "entiendan", "vuelva", "vuelvas", "vuelvan",
  "pase", "pases", "pasen", "llegue", "llegues", "lleguen", "sigas", "siga", "sigan", "pierda", "pierdas", "encuentre", "encuentres", "piense", "pienses", "sienta", "sientas"];
const FUT = ["ser", "podr", "tendr", "har", "dir", "sabr", "querr", "vendr", "pondr", "saldr", "valdr", "estar", "ir", "ver", "dar"]
  .flatMap((s) => ["á", "ás", "emos", "án", "é"].map((e) => s + e));

// Never dropped by monsters, only caught. lvl: the level a runeword with it asks for.
export const GRAMMAR_RUNES = [
  { id: "HA", lvl: 1, tense: "pretérito perfecto", core: ["he", "has", "ha", "hemos", "habéis", "han"], family: [], chance: 0.25,
    weapon: ["dmgPct", 20], armor: ["resAll", 6], off: ["block", 6], grammar: true },
  { id: "HABÍA", lvl: 6, tense: "pluscuamperfecto", core: ["había", "habías", "habíamos", "habíais", "habían"], family: [], chance: 1,
    weapon: ["dmgDictation", 15], armor: ["life", 25], off: ["armorPct", 30], grammar: true },
  { id: "HUBO", lvl: 12, tense: "pretérito de haber", core: ["hubo", "hube", "hubiste", "hubimos", "hubieron"], family: [], chance: 1,
    weapon: ["crit", 6], armor: ["xp", 5], off: ["dodge", 6], grammar: true },
  { id: "HAYA", lvl: 12, tense: "presente de subjuntivo", core: ["haya", "hayas", "hayamos", "hayáis", "hayan"], family: PRESSUBJ, chance: 0.2,
    weapon: ["dmgCloze", 15], armor: ["hintCost", 12], off: ["resAll", 12], grammar: true },
  { id: "HUBIERA", lvl: 18, tense: "imperfecto de subjuntivo", core: ["hubiera", "hubieras", "hubiéramos", "hubierais", "hubieran", "hubiese", "hubieses", "hubiésemos", "hubiesen"],
    family: IMPSUBJ, chance: 0.35, weapon: ["dmgPct", 40], armor: ["replayCost", 12], off: ["lifeRegen", 4], grammar: true },
  { id: "HABRÍA", lvl: 18, tense: "condicional", core: ["habría", "habrías", "habríamos", "habríais", "habrían"], family: COND, chance: 0.3,
    weapon: ["leech", 4], armor: ["mana", 25], off: ["resAll", 10], grammar: true },
  { id: "HABRÁ", lvl: 12, tense: "futuro", core: ["habrá", "habrás", "habré", "habremos", "habréis", "habrán"], family: FUT, chance: 0.3,
    weapon: ["killHeal", 6], armor: ["manaRegen", 2], off: ["mana", 20], grammar: true },
];
const CORE = new Map(), FAMILY = new Map();
for (const r of GRAMMAR_RUNES) {
  for (const f of r.core) CORE.set(f, r);
  for (const f of r.family) if (!CORE.has(f)) FAMILY.set(f, r);
}
// The rune a word belongs to, if any: { rune, core } (core = it's the haber form itself).
export function runeOf(word) {
  const k = lc(word);
  if (CORE.has(k)) return { rune: CORE.get(k), core: true };
  if (FAMILY.has(k)) return { rune: FAMILY.get(k), core: false };
  return null;
}
export const isGrammarWord = (w) => !!runeOf(w);
