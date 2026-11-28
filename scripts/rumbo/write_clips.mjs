// Write Rumbo's clip scripts with Claude: courses/rumbo/clips.json (the source of media/rumbo/).
//
// The facts come first, from code: a broadcast's prices are sampled from simulated sessions (so the
// bank covers the prices the game will need), a rumor's event and certainty, a contract's terms.
// Claude writes Spanish that states them (numbers in words, never digits). Then two checks, and a clip
// that fails either is thrown away and written again:
//   1. the numbers said in the text (listen-core's numbersIn) are exactly the facts' numbers;
//   2. a second Claude, who never sees the facts, reads the text as a player would and fills the same
//      answer form; its answers must equal the facts. A wrong answer key would teach wrong Spanish.
//
//   node scripts/rumbo/write_clips.mjs                         # up to the v1 targets (300 / 150 / 60)
//   node scripts/rumbo/write_clips.mjs --broadcast 10 --rumor 5 --contract 5   # smaller targets
// Uses the `claude` CLI (CLAUDE_BIN), like scripts/correct.mjs. Safe to stop and run again: it keeps
// what's written and only makes what's missing.
import fs from "fs";
import os from "os";
import path from "path";
import { spawn } from "child_process";
import { numbersIn } from "../../public/listen-core.js";
import { GOODS, GOOD_IDS, STATIONS, STATION_IDS, EVENTS, CERTAINTY, SPEAKERS, REGULARS, CLIENTS, CONTRACT_PAY, CONTRACT_DEADLINE, CONTRACT_QTY } from "../../public/rumbo/data.js";
import { simulate, rand, pick, basePrice } from "../../public/rumbo/economy.js";

const ROOT = new URL("../../", import.meta.url).pathname;
const OUT = path.join(ROOT, "courses/rumbo/clips.json");
const arg = (k, d) => { const i = process.argv.indexOf("--" + k); return i > 0 ? Number(process.argv[i + 1]) : d; };
const TARGET = { broadcast: arg("broadcast", 300), rumor: arg("rumor", 150), contract: arg("contract", 60) };
const BATCH = arg("batch", 10), PAR = arg("par", 4);
const MODEL = process.env.CLAUDE_MODEL || "claude-opus-5-5";

const bank = fs.existsSync(OUT) ? JSON.parse(fs.readFileSync(OUT, "utf8")) : { clips: [], rejected: [] };
const save = () => { fs.mkdirSync(path.dirname(OUT), { recursive: true }); fs.writeFileSync(OUT, JSON.stringify(bank, null, 1)); };

// ---------------------------------------------------------------- facts
const snaps = {}; // station -> price snapshots from 60 simulated sessions
for (let s = 0; s < 60; s++) for (const x of simulate("bank" + s)) (snaps[x.st] ||= []).push(x.prices);
const roundPrice = (p) => (p >= 1000 ? Math.round(p / 5) * 5 : Math.round(p));
const tierOf = (sp, id) => pick(SPEAKERS[sp].tiers, "tier", id);

function broadcastFacts(id, st) {
  const snap = pick(snaps[st], "snap", id);
  const r = rand("n", id), n = r < 0.4 ? 2 : r < 0.8 ? 3 : 4;
  const goods = [...GOOD_IDS].sort((a, b) => rand("g", id, a) - rand("g", id, b)).slice(0, n);
  const prices = {}, moves = {};
  for (const g of goods) {
    prices[g] = roundPrice(snap[g] * (0.98 + 0.04 * rand("p", id, g)));
    const rel = prices[g] / basePrice(st, g);
    moves[g] = rel > 1.04 ? "sube" : rel < 0.96 ? "baja" : "estable";
  }
  return { station: st, prices, moves };
}
const DEVICES = {
  1: ["dilo directo y claro", "dilo con una sola duda o atenuante, sin enredos"],
  2: ["usa subjuntivo después de una expresión de duda o de deseo", "usa una condicional con si", "menciona de pasada otra estación que no es la del suceso, dejando claro cuál sí es", "cuéntalo como algo que le dijo otra persona (estilo indirecto)"],
  3: ["usa una condicional irreal con pluscuamperfecto de subjuntivo cuyo sentido haya que deducir", "empieza diciendo un lugar o un suceso equivocado y corrígete", "mete una muletilla o una broma en medio", "usa una doble negación o un 'no es que… sino que…'", "habla en fragmentos, como en una conversación de cantina"],
};
function rumorFacts(id, sp, i) {
  const types = Object.keys(EVENTS), certs = Object.keys(CERTAINTY);
  const event = types[(i + Math.floor(rand("e0", sp) * types.length)) % types.length];
  const certainty = certs[(i + Math.floor(i / types.length)) % certs.length];
  const tier = tierOf(sp, id);
  return { event, station: EVENTS[event].station, certainty, tier, device: pick(DEVICES[tier], "dev", id) };
}
function contractFacts(id, sp) {
  const good = pick(GOOD_IDS, "cg", id), destination = pick(STATION_IDS, "cd", id), tier = tierOf(sp, id);
  // what a starting pilot can buy: at most about 4,000 credits of goods
  const most = Math.max(CONTRACT_QTY[0], Math.min(CONTRACT_QTY[1], Math.floor(4000 / basePrice(destination, good))));
  const qty = CONTRACT_QTY[0] + Math.floor(rand("cq", id) * (most - CONTRACT_QTY[0] + 1));
  const deadline = CONTRACT_DEADLINE[0] + Math.floor(rand("cl", id) * (CONTRACT_DEADLINE[1] - CONTRACT_DEADLINE[0] + 1));
  const value = qty * basePrice(destination, good);
  const pay = Math.round((value * CONTRACT_PAY[tier] * (0.95 + 0.1 * rand("cp", id))) / 50) * 50;
  const penalty = Math.round((pay * (0.25 + 0.3 * rand("cx", id))) / 50) * 50;
  return { good, qty, destination, deadline, pay, penalty, tier };
}
function planMissing() {
  const have = (pre) => bank.clips.filter((c) => c.id.startsWith(pre)).length;
  const todo = [];
  const used = new Set([...bank.clips, ...bank.rejected].map((c) => c.id));
  const nextId = (pre) => { let n = 0; while (used.has(`${pre}${String(n).padStart(3, "0")}`)) n++; const id = `${pre}${String(n).padStart(3, "0")}`; used.add(id); return [id, n]; };
  for (const st of STATION_IDS) {
    const pre = `b-${st}-`, want = Math.round(TARGET.broadcast / STATION_IDS.length);
    for (let k = have(pre); k < want; k++) {
      const [id] = nextId(pre), sp = STATIONS[st].announcer;
      const f = broadcastFacts(id, st);
      todo.push({ id, kind: "broadcast", speaker: sp, tier: tierOf(sp, id), facts: f });
    }
  }
  for (const sp of REGULARS) {
    const pre = `r-${sp}-`, want = Math.round(TARGET.rumor / REGULARS.length);
    for (let k = have(pre); k < want; k++) {
      const [id, n] = nextId(pre);
      const { tier, device, ...f } = rumorFacts(id, sp, n);
      todo.push({ id, kind: "rumor", speaker: sp, tier, device, facts: f });
    }
  }
  for (const sp of CLIENTS) {
    const pre = `c-${sp}-`, want = Math.round(TARGET.contract / CLIENTS.length);
    for (let k = have(pre); k < want; k++) {
      const [id] = nextId(pre);
      const { tier, ...f } = contractFacts(id, sp);
      todo.push({ id, kind: "contract", speaker: sp, tier, facts: f });
    }
  }
  return todo;
}

// ---------------------------------------------------------------- Claude
function claude(system, user, effort = "medium") {
  return new Promise((resolve, reject) => {
    const cp = spawn(process.env.CLAUDE_BIN || "claude", ["-p", "--output-format", "json", "--system-prompt", system, "--tools", "",
      "--strict-mcp-config", "--no-session-persistence", "--model", MODEL, "--effort", effort], { cwd: os.tmpdir(), stdio: ["pipe", "pipe", "pipe"] });
    let out = "", err = "";
    const timer = setTimeout(() => cp.kill(), 600000);
    cp.stdout.on("data", (c) => (out += c));
    cp.stderr.on("data", (c) => (err += c));
    cp.on("close", () => {
      clearTimeout(timer);
      try {
        const r = JSON.parse(out);
        if (r.is_error) return reject(new Error(r.result));
        const t = String(r.result).replace(/^```(json)?\s*|\s*```$/g, "");
        resolve(JSON.parse(t.slice(t.indexOf("["), t.lastIndexOf("]") + 1)));
      } catch (e) { reject(new Error(`claude: ${e.message} ${(err || out).slice(0, 300)}`)); }
    });
    cp.stdin.end(user);
  });
}

const WORLD = `Mundo: Rumbo, un juego de comercio espacial en una ruta de tres estaciones con nombres muiscas, habitadas por colombianos.
- Mina Tequendama ("la mina", "Tequendama"): luna minera, gente ruda. Produce mineral y hielo.
- Puerto Bachué ("el puerto", "Bachué"): el gran puerto de comercio.
- Huerta Iguaque ("la huerta", "el anillo", "Iguaque"): anillo agrícola. Produce comida.
Mercancías: mineral, hielo (agua congelada), comida (víveres), medicinas, maquinaria. La moneda son los créditos.
Los viajes entre estaciones se llaman saltos.`;

const WRITER = `Escribes los guiones de audio de un juego para aprender a escuchar español colombiano. Cada guion se convierte en voz con TTS y el jugador lo oye una vez; luego responde un formulario. Por eso:
- Español colombiano natural, del registro y el estilo del hablante que se indica. Nada de español de España.
- Los números SIEMPRE en palabras ("trescientos cuarenta y dos"), nunca en cifras. Ningún número aparte de los que se piden: ni horas, ni fechas, ni porcentajes, ni "un par", ni "dos o tres". No uses "uno" ni "una" como número.
- Todo dato pedido debe quedar dicho de forma inequívoca para un nativo atento. Nada inventado que contradiga los datos.
- Nada de acotaciones, efectos de sonido, emojis ni nombres de hablante: solo lo que se dice en voz alta.
- tier 1: claro, frases completas, 20 a 40 palabras. tier 2: natural, 30 a 55 palabras. tier 3: rápido y coloquial, con muletillas y giros, 35 a 65 palabras.

${WORLD}

Tipos de guion:
- broadcast: el boletín de precios de la radio de la estación indicada (el locutor puede saludar o nombrar la emisora). Di cada mercancía con su precio exacto en créditos. "moves" sugiere el verbo: sube → "sube a", baja → "baja a", "cae a"; estable → "se mantiene en", "sigue en", "está en". Solo esas mercancías.
- rumor: chisme en la cantina, de un parroquiano, sobre un suceso futuro en la estación indicada. Que se entienda qué va a pasar y dónde, sin decir cuándo exactamente ("en estos días", "pronto"). NO digas el efecto en los precios: el jugador lo deduce. La certeza debe oírse por la gramática y las expresiones del hablante: seguro (lo da por hecho: "ya es un hecho", "le juro que", "eso es fijo"), probable (cree que sí pero no lo garantiza: "parece que", "todo indica que", "yo creo que sí va a"), rumor (es solo un chisme que oyó, sin confirmar: "dizque", "dicen por ahí", "a lo mejor", "quién sabe"). Sigue el recurso gramatical ("device") pedido sin que la certeza deje de ser clara.
- contract: un cliente ofrece un contrato de entrega al piloto. Debe decir: la mercancía, la cantidad en unidades, la estación de destino, el plazo en saltos, el pago total en créditos y la multa en créditos si incumple. El cliente NO entrega la mercancía: el piloto la compra donde quiera y la lleva al destino ("consígame", "tráigame", "necesito que me entregue en…"). No nombres ninguna otra estación aparte del destino.

Responde SOLO un arreglo JSON: [{"id": "...", "text": "..."}], un elemento por guion, en el mismo orden.`;

const READER = `Eres un oyente nativo colombiano muy atento. Te doy transcripciones de audios de un juego; para cada una, llena el formulario que haría el jugador, solo con lo que el audio dice (sin suponer). Si algo no se dice o es ambiguo, pon null.

${WORLD}

Formularios:
- broadcast: {"prices": {mercancía: precio en número}} con las mercancías cuyo precio se dice (claves: mineral, hielo, comida, medicinas, maquinaria), y "station": la estación cuya radio habla (tequendama, bachue, iguaque) o null.
- rumor: {"event": uno de los sucesos de la lista, "station": tequendama | bachue | iguaque, "certainty": "seguro" | "probable" | "rumor"}. certainty: seguro = el hablante lo da por hecho; probable = cree que sí pasará pero no lo garantiza; rumor = solo repite un chisme sin confirmar, no se compromete. Sucesos:
${Object.entries(EVENTS).map(([k, e]) => `  ${k}: ${e.what} (en ${STATIONS[e.station].name})`).join("\n")}
- contract: {"good": mercancía, "qty": número, "destination": estación, "deadline": saltos, "pay": créditos, "penalty": créditos}.

Responde SOLO un arreglo JSON: [{"id": "...", ...formulario}], en el mismo orden.`;

const brief = (c) => {
  const S = SPEAKERS[c.speaker];
  const base = { id: c.id, kind: c.kind, tier: c.tier, speaker: S.name, style: S.style || "locutor de radio de la estación" };
  if (c.kind === "broadcast") return { ...base, station: STATIONS[c.facts.station].name, prices: c.facts.prices, moves: c.facts.moves };
  if (c.kind === "rumor") return { ...base, suceso: EVENTS[c.facts.event].what, station: STATIONS[c.facts.station].name, certainty: c.facts.certainty, device: c.device };
  return { ...base, good: GOODS[c.facts.good].name, qty: c.facts.qty, destination: STATIONS[c.facts.destination].name, deadline_saltos: c.facts.deadline, pay: c.facts.pay, penalty: c.facts.penalty };
};

// ---------------------------------------------------------------- checks
const sortN = (a) => [...a].sort((x, y) => x - y).join(",");
function numbersOk(c) {
  if (/\d/.test(c.text)) return "has digits";
  const said = numbersIn(c.text);
  const want = c.kind === "broadcast" ? Object.values(c.facts.prices) : c.kind === "contract" ? [c.facts.qty, c.facts.deadline, c.facts.pay, c.facts.penalty] : [];
  return sortN(said) === sortN(want) ? null : `numbers said ${sortN(said)} ≠ ${sortN(want)}`;
}
function readOk(c, r) {
  if (!r) return "reader gave nothing";
  const f = c.facts;
  if (c.kind === "broadcast") {
    const got = r.prices || {};
    const bad = [...new Set([...Object.keys(got), ...Object.keys(f.prices)])].filter((g) => Number(got[g]) !== f.prices[g]);
    if (r.station && r.station !== f.station) bad.push("station " + r.station);
    return bad.length ? "reader: " + bad.join(", ") : null;
  }
  if (c.kind === "rumor") {
    const bad = ["event", "station", "certainty"].filter((k) => r[k] !== f[k]).map((k) => `${k} ${r[k]}≠${f[k]}`);
    return bad.length ? "reader: " + bad.join(", ") : null;
  }
  const bad = ["good", "destination"].filter((k) => r[k] !== f[k]).concat(["qty", "deadline", "pay", "penalty"].filter((k) => Number(r[k]) !== f[k])).map((k) => `${k} ${r[k]}≠${f[k]}`);
  return bad.length ? "reader: " + bad.join(", ") : null;
}

async function runBatch(items) {
  let texts;
  try { texts = await claude(WRITER, JSON.stringify(items.map(brief), null, 1)); } catch (e) { console.error("  writer failed:", e.message); return; }
  const byId = Object.fromEntries(texts.map((t) => [t.id, String(t.text || "").replace(/\s+/g, " ").trim()]));
  const cand = [];
  for (const c of items) {
    c.text = byId[c.id];
    const why = !c.text ? "no text" : numbersOk(c);
    if (why) { bank.rejected.push({ ...c, why }); console.log(`  ✗ ${c.id}: ${why}`); } else cand.push(c);
  }
  if (!cand.length) return save();
  let reads;
  try { reads = await claude(READER, JSON.stringify(cand.map((c) => ({ id: c.id, kind: c.kind, text: c.text })), null, 1), "high"); } catch (e) { console.error("  reader failed:", e.message); return; }
  const rById = Object.fromEntries(reads.map((r) => [r.id, r]));
  for (const c of cand) {
    const why = readOk(c, rById[c.id]);
    if (why) { bank.rejected.push({ ...c, why, read: rById[c.id] }); console.log(`  ✗ ${c.id}: ${why}`); }
    else { delete c.device; bank.clips.push(c); console.log(`  ✓ ${c.id}`); }
  }
  save();
}

for (let round = 0; round < 4; round++) {
  const todo = planMissing();
  if (!todo.length) break;
  console.log(`round ${round + 1}: ${todo.length} clips to write`);
  // mix kinds in a batch only by kind order; batches of the same kind read better
  const batches = [];
  for (let i = 0; i < todo.length; i += BATCH) batches.push(todo.slice(i, i + BATCH));
  let next = 0;
  await Promise.all(Array.from({ length: PAR }, async () => { while (next < batches.length) { const b = batches[next++]; await runBatch(b); } }));
}
const by = (k) => bank.clips.filter((c) => c.kind === k).length;
console.log(`clips: ${by("broadcast")} broadcasts, ${by("rumor")} rumors, ${by("contract")} contracts; ${bank.rejected.length} rejected in all`);
