// Translate the strings extract.mjs found that public/rpg/i18n/en.json lacks, with the claude CLI, in
// batches, and merge them into en.json ({ spanish pattern: english }; wildcards are {0},{1}… in both).
// usage: node scripts/i18n/extract.mjs && node scripts/i18n/translate.mjs
import fs from "fs";
import { execFileSync } from "child_process";
const ROOT = new URL("../../", import.meta.url).pathname, EN = ROOT + "public/rpg/i18n/en.json";
const all = JSON.parse(fs.readFileSync(ROOT + "scripts/i18n/strings.json", "utf8"));
const done = fs.existsSync(EN) ? JSON.parse(fs.readFileSync(EN, "utf8")) : {};
const num = (t) => { let i = 0; return t.replace(/\u0001/g, () => `{${i++}}`); };
const todo = all.filter((x) => !(num(x.es) in done));
const B = +(process.env.BATCH || 120), start = +(process.argv[2] || 0), step = +(process.argv[3] || 1);
const GLOSS = `Glossary (use consistently): frase = line; dictado = dictation; huecos / rellenar huecos = gaps / fill the gaps; racha = streak; jefe = boss; descenso = descent; aldea = village; alijo = stash; bolsa = bag; botín = loot; zona = zone; grupo = group; combate = fight; dominar / dominada = master / mastered; punto débil = weak spot; sanguijuela (Anki leech) = leech; tunjo = tunjo; casete = cassette; runa = rune; palabra rúnica = runeword; hueco (in items) = socket; engarzar = socket; joya = gem; collar = necklace; conjunto = set; mítico = mythic; legendario = legendary; ancestral = ancestral; raro = rare; mágico = magic; único = unique; sin identificar = unidentified; identificar = identify; alambique = alembic; maná = mana; vida = life; aguante = stamina; Escucha primero = Listen first; Despacio = Slow; Pista = Hint; Repaso = Review; cripta = crypt; Encrucijada = Crossroads; El Remolino = The Whirlpool; El Abismo = The Abyss; Páramo de la Niebla = Misty Páramo; Ciénaga del Mohán = Mohán's Swamp; Selva del Chocó = Chocó Jungle; Llanos en Llamas = Burning Plains; Ruinas de Piedra = Stone Ruins; dados = dice; premio = prize; nivel = level; Fácil/Normal/Difícil = Easy/Normal/Hard.`;
for (let b = start; b * B < todo.length; b += step) {
  const batch = todo.slice(b * B, (b + 1) * B);
  const items = Object.fromEntries(batch.map((x, i) => [i, num(x.es)]));
  const prompt = `You are translating the interface of an original browser RPG for Spanish listening practice from Spanish into natural, concise English. It is set in Colombian folklore. The strings below were extracted from its source code in order; neighbours give context. {0}, {1}… are values filled in at runtime (numbers, names, words): keep every one exactly once, reorder them if English needs it. Many are fragments of a sentence split by HTML tags: translate the fragment so it reads naturally in place, keeping leading/trailing words such as "de", "a", "y" translated in a way that joins the same pieces. Keep proper names of folklore beings and people (el Mohán → the Mohán, la Llorona, el Silbón, la Madremonte, el Mandingas, la Patasola, Doña Remedios, Don Eusebio…) and Colombian place/culture words (páramo, tunjo, guadua, ceiba, Chocó, Tairona, tumbaga). Translate item and set names into evocative English (Botas del Alba → Boots of the Dawn; "del Cóndor" → "of the Condor"; "Rodela" → "Buckler"). If a string is not human-readable text (CSS, code, class names, a file name) or is a Spanish example sentence/word the player must hear or write, return it unchanged. Keep «» quotes as “”. Keep HTML entities and punctuation style; keep keyboard key names. Spanish second person (tú) → "you".
${GLOSS}
Reply with only a JSON object mapping each id to its English text, nothing else.
${JSON.stringify(items, null, 0)}`;
  let res;
  for (let tries = 0; tries < 3; tries++) {
    try {
      const txt = execFileSync("claude", ["-p", "--model", "sonnet"], { input: prompt, encoding: "utf8", maxBuffer: 1 << 26, timeout: 600000 });
      res = JSON.parse(txt.slice(txt.indexOf("{"), txt.lastIndexOf("}") + 1));
      break;
    } catch (e) { console.error(`batch ${b} try ${tries}: ${e.message.slice(0, 200)}`); }
  }
  if (!res) continue;
  const part = {};
  batch.forEach((x, i) => {
    const es = num(x.es), en = res[i];
    if (typeof en !== "string") return;
    const want = (es.match(/\{\d+\}/g) || []).sort().join(), got = (en.match(/\{\d+\}/g) || []).sort().join();
    if (want !== got) { console.error("placeholders differ:", es, "→", en); return; }
    part[es] = en;
  });
  const cur = fs.existsSync(EN) ? JSON.parse(fs.readFileSync(EN, "utf8")) : {};
  fs.writeFileSync(EN, JSON.stringify({ ...cur, ...part }, null, 0).replace(/","/g, '",\n"'));
  console.log(`batch ${b}: ${Object.keys(part).length}/${batch.length}`);
}
