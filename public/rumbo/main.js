// Rumbo: a turn-based space-trading game where prices, rumors and contracts arrive only as audio.
// Screens: station (price board, the three sources, contracts, notes), clip (listen and answer),
// market, map, end of session. The rules live in economy.js; this file is the flow and the screens.
// See README.md (Rumbo) and data/ for the spec.
import { $, esc, store, CFG, parseNumber, nameSet } from "../listen-core.js";
import { startI18n, lang, setLang } from "../rpg/i18n.js";
import { lineFeatures, LINE_FEATURES, featureVector, difficulty, predict, sigmoid, rateUpdate, newRating, newModel, answerScore, shown, provisional, tagOf, RATING } from "../rpg/rating.js";
import * as E from "./economy.js";
import { GOODS, GOOD_IDS, STATIONS, STATION_IDS, EVENTS, CERTAINTY, SPEAKERS, REGULARS, CLIENTS, SESSION_TURNS, START, HOLD_UPGRADE, COST, SLOW_RATE, SOURCE_NOISE, fuel } from "./data.js";
import { playClip, stop } from "./audio.js";

const audioEl = $("#audio");
const screen = $("#screen");
const KEY = "rumbo";

// ---------------------------------------------------------------- the clip bank and its difficulty
const BANK = await fetch("media/rumbo/bank.json").then((r) => (r.ok ? r.json() : { clips: [] })).catch(() => ({ clips: [] }));
const CLIPS = BANK.clips.filter((c) => !c.bad);
const BY_ID = Object.fromEntries(CLIPS.map((c) => [c.id, c]));
const FREQ = await fetch("api/wordfreq").then((r) => (r.ok ? r.json() : null)).catch(() => null);
const NAMES = nameSet(["Tequendama", "Bachué", "Iguaque", "Rocío", "Efraín", "Yesenia", "Cárdenas", "Gustavo", "Rengifo", "Barrios", "Chato", "Mono", "Huerta", "Puerto", "Mina"]);
// how much radio noise a clip is played with, where it's heard
const levelOf = (c, st) => (c.kind === "broadcast" ? STATIONS[c.facts.station].noise : SOURCE_NOISE[c.kind] + 0.3 * STATIONS[st].noise);
const FEAT = Object.fromEntries(CLIPS.map((c) => [c.id, lineFeatures(c.words || [], { freq: FREQ, names: NAMES })]));
const STATS = (() => {
  const out = {};
  for (const k of LINE_FEATURES) {
    const xs = CLIPS.map((c) => FEAT[c.id]?.[k]).filter((v) => v != null && isFinite(v));
    if (xs.length < 2) continue;
    const mean = xs.reduce((a, b) => a + b, 0) / xs.length;
    const sd = Math.sqrt(xs.reduce((a, b) => a + (b - mean) ** 2, 0) / xs.length) || 1;
    out[k] = { mean, sd };
  }
  return out;
})();
const clipX = (c, st) => featureVector({ ...(FEAT[c.id] || {}), quiet: levelOf(c, st) }, STATS);
// the market's difficulty of a clip, 0 to 1, the same for every player: it sets the edge it gives
const diffOf = (c, st) => sigmoid(difficulty(clipX(c, st), RATING.w0));

// ---------------------------------------------------------------- the saved game
function fresh() {
  return {
    v: 1, turn: 0,
    ship: { credits: START.credits, hold: START.hold, at: START.station, cargo: {} },
    board: {}, heard: {}, speakers: {}, history: [], session: null,
    rating: newRating(), model: newModel(),
  };
}
let G = store.get(KEY, null) || fresh();
const save = () => store.set(KEY, G);
const S = { view: "station", clip: null, msg: null, market: {} }; // what's on screen (not saved)
const ses = () => G.session;
const W = () => G.session?.world;
const here = () => G.ship.at;
const turnsLeft = () => SESSION_TURNS - (W().turn - W().start);

// ---------------------------------------------------------------- formatting
const nf = new Intl.NumberFormat("es-CO");
const cr = (n) => `${nf.format(Math.round(n))} cr`;
const goodName = (g) => GOODS[g].name;
const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);
const ageText = (t) => { const a = G.turn - t; return a <= 0 ? "este turno" : a === 1 ? "hace 1 turno" : `hace ${a} turnos`; };
const cargoN = () => E.cargoCount(G.ship);
// net worth on screen: credits plus cargo at what it cost (true prices stay hidden until the end)
const worthAtCost = () => G.ship.credits + Object.values(G.ship.cargo).reduce((a, c) => a + c.cost, 0);
function toast(msg) {
  const t = $("#toast");
  t.textContent = msg;
  t.classList.add("on");
  clearTimeout(toast.t);
  toast.t = setTimeout(() => t.classList.remove("on"), 3200);
}

// ---------------------------------------------------------------- the event log (api/lines, as Leyendas)
const pending = [];
function logEv(e) {
  pending.push({ ...e, game: "rumbo", t: Date.now() });
  clearTimeout(logEv.t);
  logEv.t = setTimeout(flushLog, 2000);
}
function flushLog(beacon = false) {
  if (!pending.length) return;
  const body = JSON.stringify({ events: pending.splice(0) });
  if (beacon && navigator.sendBeacon) { navigator.sendBeacon("api/lines", new Blob([body], { type: "application/json" })); return; }
  fetch("api/lines", { method: "POST", headers: { "Content-Type": "application/json" }, body, keepalive: true }).catch(() => {});
}
addEventListener("pagehide", () => flushLog(true));

// ---------------------------------------------------------------- sessions and turns
function boardSet(st, g, entry) { (G.board[st] ||= {})[g] = entry; }
function startSession() {
  const seed = String(Date.now());
  const eventTypes = [...new Set(CLIPS.filter((c) => c.kind === "rumor").map((c) => c.facts.event))];
  const world = E.newWorld(seed, G.turn, { eventTypes, turns: SESSION_TURNS });
  G.session = { n: G.history.length + 1, seed, world, used: [], log: [], trades: [], rumors: [], contracts: [], notes: [], visit: null, worth0: E.netWorth(G.ship, world), credits0: G.ship.credits };
  arrive();
  save();
  logEv({ ev: "rumboTurn", session: G.session.n, turn: 0, at: here(), worth: G.session.worth0, credits: G.ship.credits });
}
function note(text, kind = "") { ses().notes.unshift({ turn: W().turn - W().start, text, kind }); ses().notes.length = Math.min(ses().notes.length, 40); }

// what happens on arriving at a station: the turn's consequences, then the station's broadcast,
// who's at the cantina and which contract is on offer
function arrive() {
  const s = ses(), w = W(), st = here();
  for (const r of s.rumors) {
    if (r.resolved || w.turn < r.start) continue;
    r.resolved = true;
    const rec = (G.speakers[r.speaker] ||= { right: 0, wrong: 0 });
    r.truth ? rec.right++ : rec.wrong++;
    note(`${SPEAKERS[r.speaker].name}: ${r.truth ? "lo que contó pasó" : "lo que contó no pasó"} (${EVENTS[r.type].what}, ${STATIONS[EVENTS[r.type].station].name}).`, r.truth ? "good" : "bad");
  }
  for (const k of s.contracts) {
    if (k.status !== "open" || w.turn <= k.due) continue;
    k.status = "failed";
    G.ship.credits -= k.terms.penalty;
    note(`Contrato vencido con ${SPEAKERS[k.client].name}: pagaste la multa de ${cr(k.terms.penalty)}.`, "bad");
    logEv({ ev: "rumboContract", clip: k.clip, status: "failed", penalty: k.terms.penalty });
  }
  const used = new Set(s.used);
  const b = E.pickBroadcast(CLIPS, w, st, used, G.heard);
  if (b) { E.bindBroadcast(w, st, b.facts.prices); s.used.push(b.id); }
  // an easy public broadcast is already priced in: the dock talks of it before you listen
  if (b && diffOf(b, st) < 0.35)
    for (const [g, p] of Object.entries(b.facts.prices)) {
      const cur = G.board[st]?.[g];
      if (!cur || cur.t < G.turn) boardSet(st, g, { p: Math.round(p / 10) * 10, t: G.turn, src: "público" });
    }
  const offers = CLIPS.filter((c) => c.kind === "contract" && c.facts.destination !== st && !used.has(c.id));
  const oldest = Math.min(Infinity, ...offers.map((c) => G.heard[c.id] || 0));
  const offer = E.pick(offers.filter((c) => (G.heard[c.id] || 0) === oldest), w.seed, "offer", w.turn, st) || null;
  if (offer) s.used.push(offer.id);
  s.visit = { turn: w.turn, st, broadcast: b?.id || null, answered: {}, regs: E.regularsAt(w, st, REGULARS), drinks: {}, offer: offer?.id || null };
}

function jump(to) {
  const f = fuel(here(), to);
  if (turnsLeft() <= 0) return;
  G.ship.credits -= f;
  G.ship.at = to;
  G.turn++;
  E.advance(W());
  arrive();
  save();
  logEv({ ev: "rumboTurn", session: ses().n, turn: W().turn - W().start, at: to, fuel: f, worth: E.netWorth(G.ship, W()), credits: G.ship.credits });
  S.view = "station";
  render();
}

function endSession() {
  const s = ses(), w = W();
  const worth1 = E.netWorth(G.ship, w);
  for (const k of s.contracts) if (k.status === "open") k.status = "cancelled";
  const best = s.trades.filter((t) => t.profit != null).sort((a, b) => b.profit - a.profit)[0] || null;
  const day = new Date().toISOString().slice(0, 10);
  G.history.push({ n: s.n, date: day, turns: w.turn - w.start, worth0: s.worth0, worth1, perTurn: Math.round((worth1 - s.worth0) / Math.max(1, w.turn - w.start)) });
  G.last = { n: s.n, worth0: s.worth0, worth1, best, log: s.log.filter((x) => x.strict < 1), cancelled: s.contracts.filter((k) => k.status === "cancelled").length, turns: w.turn - w.start, rating0: s.rating0 ?? null };
  logEv({ ev: "rumboTurn", session: s.n, end: true, turn: w.turn - w.start, worth: worth1, worth0: s.worth0 });
  G.session = null;
  save();
  flushLog();
  S.view = "end";
  render();
}

// ---------------------------------------------------------------- listening
function openClip(c, src) {
  stop(audioEl);
  S.clip = { c, src, plays: 0, slows: 0, fresh: !G.heard[c.id], playing: false, E: predict(clipX(c, here()), G.model.w, G.rating.th) };
  S.view = "clip";
  render();
}
async function play(slow = false) {
  const C = S.clip;
  if (!C || C.playing) return;
  const cost = C.plays === 0 && !slow ? 0 : slow ? COST.slow : COST.replay;
  if (cost && G.ship.credits < cost) return toast("No te alcanza para oírlo otra vez.");
  G.ship.credits -= cost;
  C.plays++;
  if (slow) C.slows++;
  G.heard[C.c.id] = Date.now();
  save();
  renderStatus();
  // update the screen in place: a redraw would wipe what's typed in the form
  const sync = () => {
    if (S.view !== "clip" || S.clip !== C) return;
    $("#clipPlay")?.classList.toggle("on", C.playing);
    document.querySelectorAll(".clipbtns button").forEach((x) => (x.disabled = C.playing));
    document.querySelectorAll("#answer button").forEach((x) => (x.disabled = false));
    const l = $("#clipPlay .plabel"); if (l) l.textContent = C.playing ? "Sonando…" : "Escuchado";
    const n = $("#playCount"); if (n) n.textContent = `Lo oíste ${C.plays} ${C.plays === 1 ? "vez" : "veces"}.`;
  };
  await playClip(audioEl, `media/rumbo/${C.c.file}`, {
    rate: slow ? SLOW_RATE : 1, level: levelOf(C.c, here()),
    onState: (on) => { C.playing = on; sync(); },
  });
  sync();
}

// score and record an answer; strict: share of fields right
function recordAnswer(C, answer, right, total) {
  const strict = total ? right / total : 0;
  const entry = { id: C.c.id, kind: C.c.kind, answer, strict: +strict.toFixed(3), plays: C.plays, slows: C.slows, turn: W().turn - W().start, st: here() };
  ses().log.push(entry);
  let rated = null;
  if (C.fresh) {
    const score = answerScore({ strict, plays: C.plays, slows: C.slows });
    if (ses().rating0 == null) ses().rating0 = G.rating.th;
    rated = rateUpdate(G.rating, G.model, clipX(C.c, here()), score, new Date().toISOString().slice(0, 10));
  }
  logEv({ ev: "rumboClip", clip: C.c.id, src: C.c.kind, plays: C.plays, slows: C.slows, answer, truth: C.c.facts, strict: entry.strict, fresh: C.fresh, E: rated?.E ?? null, th: rated ? G.rating.th : null });
  return entry;
}

function submitBroadcast(form) {
  const C = S.clip, facts = C.c.facts.prices, st = here();
  const typed = {};
  for (const g of GOOD_IDS) { const v = form.elements[g].value.trim(); if (v) typed[g] = parseNumber(v); }
  if (Object.values(typed).some((v) => v == null)) return toast("Escribe cada precio como un número (342) o en palabras (trescientos cuarenta y dos).");
  if (!Object.keys(typed).length) return toast("Anota al menos un precio.");
  const all = new Set([...Object.keys(facts), ...Object.keys(typed)]);
  const right = [...all].filter((g) => typed[g] === facts[g]).length;
  const entry = recordAnswer(C, typed, right, all.size);
  entry.truth = facts;
  for (const [g, p] of Object.entries(typed)) boardSet(st, g, { p, t: G.turn, src: "oído", clip: C.c.id });
  ses().visit.answered.broadcast = true;
  save();
  toast(`Anotaste ${Object.keys(typed).length} precio${Object.keys(typed).length === 1 ? "" : "s"} en el tablero.`);
  S.view = "station";
  render();
}

function rumorOptions(c) {
  const f = c.facts, ev = EVENTS[f.event];
  const others = Object.keys(EVENTS).filter((k) => k !== f.event);
  // distractors: the same station's other events first, then the same good elsewhere
  const near = others.filter((k) => EVENTS[k].station === ev.station || EVENTS[k].good === ev.good);
  const ordered = [...near.sort((a, b) => E.rand(c.id, a) - E.rand(c.id, b)), ...others.filter((k) => !near.includes(k)).sort((a, b) => E.rand(c.id, a) - E.rand(c.id, b))];
  return [f.event, ...ordered.slice(0, 3)].sort((a, b) => E.rand(c.id, "o", a) - E.rand(c.id, "o", b));
}
function submitRumor(form) {
  const C = S.clip, f = C.c.facts;
  const a = { event: form.elements.event.value, station: form.elements.station.value, certainty: form.elements.certainty.value };
  if (!a.event || !a.station || !a.certainty) return toast("Contesta las tres preguntas.");
  const right = ["event", "station", "certainty"].filter((k) => a[k] === f[k]).length;
  const entry = recordAnswer(C, a, right, 3);
  entry.truth = { event: f.event, station: f.station, certainty: f.certainty };
  const r = ses().rumors.find((x) => x.clip === C.c.id);
  if (r) r.notes = a;
  save();
  toast("Anotado en tu libreta.");
  S.view = "station";
  render();
}
function submitContract(form, accept) {
  const C = S.clip, f = C.c.facts;
  const num = (k) => parseNumber(form.elements[k].value);
  const a = { good: form.elements.good.value, qty: num("qty"), destination: form.elements.destination.value, deadline: num("deadline"), pay: num("pay"), penalty: num("penalty") };
  if (accept && Object.values(a).some((v) => v == null || v === "")) return toast("Llena los seis campos antes de firmar.");
  const right = Object.keys(a).filter((k) => a[k] === f[k]).length;
  const entry = recordAnswer(C, a, right, 6);
  entry.truth = { good: f.good, qty: f.qty, destination: f.destination, deadline: f.deadline, pay: f.pay, penalty: f.penalty };
  entry.accepted = accept;
  ses().visit.answered.contract = true;
  if (accept) {
    ses().contracts.push({ clip: C.c.id, client: C.c.speaker, terms: entry.truth, notes: a, accepted: W().turn, due: W().turn + f.deadline, status: "open" });
    note(`Firmaste con ${SPEAKERS[C.c.speaker].name}: según tus notas, ${a.qty} de ${goodName(a.good)} a ${STATIONS[a.destination].name} en ${a.deadline} saltos, por ${cr(a.pay)}.`);
  }
  logEv({ ev: "rumboContract", clip: C.c.id, status: accept ? "accepted" : "declined" });
  save();
  toast(accept ? "Contrato firmado. Los términos que valen son los que dijo el cliente." : "Rechazaste el contrato.");
  S.view = "station";
  render();
}

function buyDrink(reg) {
  const v = ses().visit;
  if (v.drinks[reg]) return openClip(BY_ID[v.drinks[reg]], "rumor");
  if (G.ship.credits < COST.drink) return toast("No te alcanza para el trago.");
  const c = E.pickRumor(CLIPS, reg, new Set(ses().used), G.heard, `${W().seed}|${W().turn}`);
  if (!c) return toast(`${SPEAKERS[reg].name} no tiene nada nuevo que contar.`);
  G.ship.credits -= COST.drink;
  ses().used.push(c.id);
  v.drinks[reg] = c.id;
  const r = E.tellRumor(W(), c, diffOf(c, here()), `${W().turn}${reg}`);
  ses().rumors.push({ clip: c.id, speaker: reg, type: c.facts.event, truth: r.truth, start: r.event ? r.event.start : W().turn + r.lead, told: W().turn, resolved: false, notes: null });
  save();
  openClip(c, "rumor");
}

// ---------------------------------------------------------------- trading
function doTrade(g, qty) {
  const st = here(), w = W(), s = ses();
  if (!qty) return;
  const c = (G.ship.cargo[g] ||= { qty: 0, cost: 0 });
  if (qty > 0) {
    if (cargoN() + qty > G.ship.hold) return toast(`Tu bodega solo tiene ${G.ship.hold - cargoN()} espacios libres.`);
    // buy what the credits cover, at the true price
    let n = qty;
    while (n > 0 && E.quote(E.price(w, st, g), n) > G.ship.credits) n--;
    if (!n) return toast("No te alcanzan los créditos.");
    qty = n;
  } else if (-qty > c.qty) return toast(`Solo llevas ${c.qty} de ${goodName(g)}.`);
  const heard = G.board[st]?.[g];
  const r = E.trade(w, st, g, qty);
  let profit = null;
  if (qty > 0) { G.ship.credits -= r.total; c.qty += qty; c.cost += r.total; }
  else {
    const basis = c.qty ? (c.cost * -qty) / c.qty : 0;
    profit = Math.round(r.total - basis);
    G.ship.credits += r.total; c.cost -= basis; c.qty += qty;
    if (!c.qty) delete G.ship.cargo[g];
  }
  // the fill shows the true price: a price you heard wrong shows its true value now
  let msg = `${qty > 0 ? "Compraste" : "Vendiste"} ${Math.abs(qty)} de ${goodName(g)} por ${cr(r.total)} (${cr(r.avg)} cada uno).`;
  if (heard && heard.t === G.turn && heard.src === "oído" && heard.p !== r.first) {
    msg += ` Ojo: anotaste ${nf.format(heard.p)}, pero el precio era ${nf.format(r.first)}.`;
    const entry = s.log.find((x) => x.id === heard.clip);
    if (entry) (entry.revealed ||= {})[g] = r.first;
  }
  boardSet(st, g, { p: r.after, t: G.turn, src: "recibo", was: heard && heard.t === G.turn && heard.src === "oído" && heard.p !== r.first ? heard.p : undefined });
  s.trades.push({ g, st, qty, total: r.total, profit, turn: w.turn - w.start });
  logEv({ ev: "rumboTrade", st, g, qty, total: r.total, first: r.first, heard: heard?.t === G.turn ? heard.p : null, profit, credits: G.ship.credits });
  S.msg = msg;
  save();
  render();
}
function deliver(k) {
  const c = G.ship.cargo[k.terms.good];
  if (!c || c.qty < k.terms.qty) return toast(`Te faltan ${k.terms.qty - (c?.qty || 0)} de ${goodName(k.terms.good)}.`);
  const basis = (c.cost * k.terms.qty) / c.qty;
  c.qty -= k.terms.qty; c.cost -= basis;
  if (!c.qty) delete G.ship.cargo[k.terms.good];
  G.ship.credits += k.terms.pay;
  k.status = "done";
  ses().trades.push({ g: k.terms.good, st: here(), qty: -k.terms.qty, total: k.terms.pay, profit: Math.round(k.terms.pay - basis), turn: W().turn - W().start, contract: true });
  note(`Entregaste a ${SPEAKERS[k.client].name}: ${k.terms.qty} de ${goodName(k.terms.good)}. Te pagó ${cr(k.terms.pay)}.`, "good");
  logEv({ ev: "rumboContract", clip: k.clip, status: "done", pay: k.terms.pay });
  save();
  render();
}

// ---------------------------------------------------------------- art
const STARS = Array.from({ length: 40 }, (_, i) => `<circle cx="${(E.rand("sx", i) * 320).toFixed(0)}" cy="${(E.rand("sy", i) * 140).toFixed(0)}" r="${(0.4 + E.rand("sr", i) * 1.1).toFixed(1)}" opacity="${(0.3 + E.rand("so", i) * 0.7).toFixed(2)}"/>`).join("");
function art(st, small = false) {
  const body = {
    tequendama: `<defs><radialGradient id="mt" cx="35%" cy="35%"><stop offset="0" stop-color="#b9b2a6"/><stop offset="1" stop-color="#4a4540"/></radialGradient></defs>
      <circle cx="170" cy="74" r="52" fill="url(#mt)"/>
      <circle cx="150" cy="60" r="9" fill="#00000030"/><circle cx="190" cy="92" r="13" fill="#00000028"/><circle cx="185" cy="52" r="5" fill="#00000030"/><circle cx="140" cy="96" r="6" fill="#00000025"/>
      <path d="M200 30 l14 -18 l6 4 l-12 20z" fill="#f2b84b"/><rect x="211" y="8" width="3" height="16" fill="#cfc6b8"/>
      <circle cx="212" cy="7" r="2.4" fill="#ff6b3d"><animate attributeName="opacity" values="1;.2;1" dur="1.6s" repeatCount="indefinite"/></circle>`,
    bachue: `<g transform="translate(170 74)">
      <ellipse rx="86" ry="22" fill="none" stroke="#7fd1c7" stroke-width="3" opacity=".8"/>
      <rect x="-14" y="-46" width="28" height="92" rx="6" fill="#d8e2e6"/><rect x="-30" y="-12" width="60" height="24" rx="5" fill="#9fb4bd"/>
      ${[-70, -40, 40, 70].map((x) => `<rect x="${x - 6}" y="-5" width="12" height="10" rx="2" fill="#f2b84b"/>`).join("")}
      ${[-30, -14, 2, 18].map((y, i) => `<circle cx="0" cy="${y}" r="2.2" fill="#ffe9a8"><animate attributeName="opacity" values="1;.3;1" dur="${1.2 + i * 0.3}s" repeatCount="indefinite"/></circle>`).join("")}</g>`,
    iguaque: `<g transform="translate(170 74)">
      <ellipse rx="92" ry="34" fill="none" stroke="#4d8f4a" stroke-width="16"/>
      <ellipse rx="92" ry="34" fill="none" stroke="#8fd16f" stroke-width="5" stroke-dasharray="10 7"/>
      <ellipse rx="92" ry="34" fill="none" stroke="#2c5a2b" stroke-width="16" stroke-dasharray="0 140 120 400" opacity=".6"/>
      <circle r="13" fill="#d8e2e6"/><line x1="-80" y1="0" x2="80" y2="0" stroke="#d8e2e6" stroke-width="2"/></g>`,
  }[st];
  return `<svg class="art${small ? " small" : ""}" viewBox="0 0 320 140" role="img" aria-label="${esc(STATIONS[st].name)}"><rect width="320" height="140" fill="#0b1020"/><g fill="#fff">${STARS}</g>${body}</svg>`;
}

// ---------------------------------------------------------------- screens
function renderStatus() {
  const el = $("#status");
  if (!G.session) { el.innerHTML = ""; return; }
  const R = G.rating;
  el.innerHTML = `
    <span title="Créditos"><b>${cr(G.ship.credits)}</b></span>
    <span title="Bodega: unidades que llevas y capacidad">Bodega <b>${cargoN()}/${G.ship.hold}</b></span>
    <span title="Turnos de la sesión">Turno <b>${W().turn - W().start}/${SESSION_TURNS}</b></span>
    <span title="Índice de oído en Rumbo: sube cuando entiendes clips nuevos mejor de lo esperado">Índice <b>${shown(R.th)}${provisional(R) ? "?" : ""}</b></span>`;
}

function render() {
  renderStatus();
  if (!CLIPS.length) { screen.innerHTML = `<section class="card"><h2>Falta el banco de clips</h2><p>No encontré <code>media/rumbo/bank.json</code>. Constrúyelo con <code>scripts/rumbo/</code> (ver el README).</p></section>`; return; }
  if (S.view === "end") return renderEnd();
  if (!G.session) return renderIntro();
  if (S.view === "clip" && S.clip) return renderClip();
  if (S.view === "market") return renderMarket();
  if (S.view === "map") return renderMap();
  renderStation();
}

function renderIntro() {
  const h = G.history[G.history.length - 1];
  screen.innerHTML = `<section class="card intro">
    ${art("bachue")}
    <h2>${h ? "Otra sesión de comercio" : "Rumbo"}</h2>
    <p>Comercias entre tres estaciones. Los precios, los chismes y los contratos solo llegan por audio: quien entiende primero y bien, gana.</p>
    <ul>
      <li><b>Radio de la estación</b> (gratis): los precios de hoy, dichos rápido. Anótalos en el tablero.</li>
      <li><b>Cantina</b> (un trago, ${cr(COST.drink)}): un chisme sobre algo que va a pasar. Ojo con qué tan seguro está quien lo cuenta.</li>
      <li><b>Contratos</b>: un cliente dice qué quiere, cuánto, adónde, en cuántos saltos, cuánto paga y la multa.</li>
    </ul>
    <p>Cada clip se oye una vez gratis; otra vez cuesta ${cr(COST.replay)}, despacio ${cr(COST.slow)}. Compras y vendes al precio real, no al que creíste oír. Una sesión dura ${SESSION_TURNS} saltos.</p>
    ${h ? `<p class="dim">Llevas ${cr(G.ship.credits)} y estás en ${STATIONS[here()].name}. Última sesión: ${cr(h.worth0)} → ${cr(h.worth1)}.</p>` : ""}
    <button class="primary" id="startBtn">Empezar sesión</button>
  </section>`;
}

function boardRows(st, interactive = false) {
  const b = G.board[st] || {};
  return GOOD_IDS.map((g) => {
    const e = b[g];
    const p = !e ? "—" : `${e.src === "público" ? "≈ " : ""}${nf.format(e.p)}`;
    const was = e?.was != null ? `<span class="was" title="Lo que anotaste">${nf.format(e.was)}</span> ` : "";
    const src = !e ? "" : e.src === "público" ? "se comenta en el muelle" : e.src === "recibo" ? "de tu recibo" : "lo que oíste";
    return `<tr class="${e && G.turn - e.t > 0 ? "old" : ""}"><td>${cap(goodName(g))}</td><td class="num">${was}${p}</td><td class="age">${e ? `${ageText(e.t)} · ${src}` : "sin dato"}</td>${interactive ? `<td>${G.ship.cargo[g]?.qty || ""}</td>` : ""}</tr>`;
  }).join("");
}
function recordOf(sp) {
  const r = G.speakers[sp];
  return r && r.right + r.wrong ? `acertó ${r.right} de ${r.right + r.wrong}` : "sin historial";
}

function renderStation() {
  const st = here(), s = ses(), v = s.visit, w = W();
  const b = v.broadcast && BY_ID[v.broadcast], offer = v.offer && BY_ID[v.offer];
  const tag = (c) => `<span class="tag t-${tagOf(predict(clipX(c, st), G.model.w, G.rating.th)).replace("í", "i").replace("á", "a")}" title="Qué tan difícil es para ti, según tu índice">${tagOf(predict(clipX(c, st), G.model.w, G.rating.th))}</span>`;
  const due = s.contracts.filter((k) => k.status === "open" && k.terms.destination === st);
  const open = s.contracts.filter((k) => k.status === "open");
  const cargo = Object.entries(G.ship.cargo).filter(([, c]) => c.qty);
  screen.innerHTML = `
  <section class="station">
    <div class="sthead">
      ${art(st)}
      <div><h2>${STATIONS[st].name}</h2><p class="kind">${STATIONS[st].kind}</p><p class="dim">${STATIONS[st].blurb}</p></div>
    </div>
    ${due.map((k) => `<div class="card deliver"><b>${SPEAKERS[k.client].name}</b> te espera aquí: ${k.terms.qty} de ${goodName(k.terms.good)}. <button class="primary" data-deliver="${k.clip}">Entregar</button></div>`).join("")}
    <div class="grid">
      <div class="card">
        <h3>Tablero de precios</h3>
        <table class="board"><thead><tr><th>Mercancía</th><th>Precio</th><th>Visto</th></tr></thead><tbody>${boardRows(st)}</tbody></table>
        <p class="dim small">El tablero solo muestra lo que tú confirmaste. Los precios nuevos están en el audio.</p>
      </div>
      <div class="card sources">
        <h3>Escuchar</h3>
        <button class="source" data-src="broadcast" ${b ? "" : "disabled"}>
          <span class="sname">${STATIONS[st].radio} ${b ? tag(b) : ""}</span>
          <span class="sdesc">${!b ? "Hoy no hay boletín." : v.answered.broadcast ? "Ya anotaste los precios de este turno." : "Gratis · los precios de hoy"}</span>
        </button>
        ${v.regs.map((r) => `<button class="source" data-drink="${r}">
          <span class="sname">Cantina: ${SPEAKERS[r].name} ${v.drinks[r] ? tag(BY_ID[v.drinks[r]]) : ""}</span>
          <span class="sdesc">${v.drinks[r] ? (s.rumors.find((x) => x.clip === v.drinks[r])?.notes ? "Ya anotaste su chisme." : "Te está contando algo.") : `Invitarle un trago: ${cr(COST.drink)}`} · ${recordOf(r)}</span>
        </button>`).join("")}
        <button class="source" data-src="contract" ${offer && !v.answered.contract ? "" : "disabled"}>
          <span class="sname">Contrato${offer ? `: ${SPEAKERS[offer.speaker].name} ${tag(offer)}` : ""}</span>
          <span class="sdesc">${!offer ? "Nadie ofrece contratos hoy." : v.answered.contract ? "Ya respondiste esta oferta." : "Gratis · una oferta de entrega"}</span>
        </button>
      </div>
      <div class="card">
        <h3>Tu nave</h3>
        <p>${cr(G.ship.credits)} · bodega ${cargoN()}/${G.ship.hold}</p>
        ${cargo.length ? `<ul class="cargo">${cargo.map(([g, c]) => `<li>${c.qty} de ${goodName(g)} <span class="dim">(te costó ${cr(c.cost)})</span></li>`).join("")}</ul>` : `<p class="dim">La bodega va vacía.</p>`}
        ${open.length ? `<h4>Contratos (según tus notas)</h4><ul class="contracts">${open.map((k) => `<li><b>${SPEAKERS[k.client].name}</b>: ${k.notes.qty ?? "?"} de ${k.notes.good ? goodName(k.notes.good) : "?"} a ${k.notes.destination ? STATIONS[k.notes.destination].name : "?"}, en ${k.notes.deadline ?? "?"} saltos desde el turno ${k.accepted - w.start}. Pago ${k.notes.pay != null ? cr(k.notes.pay) : "?"}, multa ${k.notes.penalty != null ? cr(k.notes.penalty) : "?"}.</li>`).join("")}</ul>` : ""}
      </div>
      <div class="card">
        <h3>Libreta</h3>
        ${s.rumors.filter((r) => r.notes).map((r) => `<p class="rnote ${r.resolved ? (r.truth ? "good" : "bad") : ""}"><b>${SPEAKERS[r.speaker].name}</b> (turno ${r.told - w.start}): ${EVENTS[r.notes.event].what}, en ${STATIONS[r.notes.station].name}. Dijo: ${CERTAINTY[r.notes.certainty].label.toLowerCase()}.${r.resolved ? (r.truth ? " Pasó." : " No pasó.") : ""}</p>`).join("") || `<p class="dim">Lo que te cuenten en la cantina queda aquí, con lo que anotaste.</p>`}
        ${s.notes.slice(0, 8).map((n) => `<p class="note ${n.kind}"><span class="dim">Turno ${n.turn}:</span> ${n.text}</p>`).join("")}
      </div>
    </div>
    <div class="actions">
      <button class="primary" data-go="market">Mercado</button>
      <button class="primary" data-go="map">${turnsLeft() > 0 ? "Saltar a otra estación" : "Ver el mapa"}</button>
      <button class="ghost" id="endBtn">Terminar la sesión</button>
    </div>
  </section>`;
}

function renderClip() {
  const C = S.clip, c = C.c, st = here(), sp = SPEAKERS[c.speaker];
  const lvl = levelOf(c, st);
  const kindName = { broadcast: STATIONS[st].radio, rumor: "Cantina", contract: "Oferta de contrato" }[c.kind];
  const E0 = tagOf(C.E);
  const form = {
    broadcast: () => `<form id="answer" class="prices" autocomplete="off">
        <p class="dim small">Anota cada precio que oigas, en cifras o en palabras. Deja vacío lo que no dijeron.</p>
        ${GOOD_IDS.map((g) => `<label><span>${cap(goodName(g))}</span><input name="${g}" inputmode="text" placeholder="—"></label>`).join("")}
        <button class="primary" ${C.plays ? "" : "disabled"}>Anotar en el tablero</button></form>`,
    rumor: () => {
      const opts = rumorOptions(c);
      return `<form id="answer" class="mc" autocomplete="off">
        <fieldset><legend>¿Qué va a pasar?</legend>${opts.map((k) => `<label><input type="radio" name="event" value="${k}"> ${cap(EVENTS[k].what)}</label>`).join("")}</fieldset>
        <fieldset><legend>¿Dónde?</legend>${STATION_IDS.map((k) => `<label><input type="radio" name="station" value="${k}"> ${STATIONS[k].name}</label>`).join("")}</fieldset>
        <fieldset><legend>¿Qué tan seguro está?</legend>${Object.entries(CERTAINTY).map(([k, x]) => `<label><input type="radio" name="certainty" value="${k}"> ${x.label}</label>`).join("")}</fieldset>
        <button class="primary" ${C.plays ? "" : "disabled"}>Anotar en la libreta</button></form>`;
    },
    contract: () => `<form id="answer" class="terms" autocomplete="off">
        <label><span>Mercancía</span><select name="good"><option value="">—</option>${GOOD_IDS.map((g) => `<option value="${g}">${cap(goodName(g))}</option>`).join("")}</select></label>
        <label><span>Cantidad</span><input name="qty" placeholder="unidades"></label>
        <label><span>Destino</span><select name="destination"><option value="">—</option>${STATION_IDS.map((k) => `<option value="${k}">${STATIONS[k].name}</option>`).join("")}</select></label>
        <label><span>Plazo</span><input name="deadline" placeholder="saltos"></label>
        <label><span>Pago</span><input name="pay" placeholder="créditos"></label>
        <label><span>Multa</span><input name="penalty" placeholder="créditos"></label>
        <div class="row"><button class="primary" name="accept" value="1" ${C.plays ? "" : "disabled"}>Aceptar</button><button class="ghost" name="accept" value="0" ${C.plays ? "" : "disabled"}>Rechazar</button></div></form>`,
  }[c.kind];
  screen.innerHTML = `<section class="card clip">
    <button class="ghost back" data-go="station">← Volver a la estación</button>
    <h2>${kindName}</h2>
    <p class="who">${sp.name} · <span class="tag t-${E0.replace("í", "i").replace("á", "a")}">${E0}</span> ${lvl > 0.4 ? "· señal con mucha estática" : lvl > 0.15 ? "· algo de estática" : "· señal limpia"}${C.fresh ? "" : " · ya lo oíste antes"}</p>
    <div class="player">
      <button id="clipPlay" class="play ${C.playing ? "on" : ""}" aria-label="Escuchar">
        <span class="bars"><i></i><i></i><i></i><i></i><i></i></span>
        <span class="plabel">${C.plays ? "Escuchado" : "Escuchar (gratis)"}</span>
      </button>
      <div class="clipbtns">
        <button class="ghost" id="replayBtn" ${C.plays ? "" : "disabled"}>Otra vez · ${cr(COST.replay)}</button>
        <button class="ghost" id="slowBtn" ${C.plays ? "" : "disabled"}>Despacio · ${cr(COST.slow)}</button>
      </div>
      <p class="dim small" id="playCount">${C.plays ? `Lo oíste ${C.plays} ${C.plays === 1 ? "vez" : "veces"}.` : "Se oye una vez gratis. No hay respuestas correctas a la vista: lo sabrás por lo que pase."}</p>
    </div>
    ${form()}
  </section>`;
}

function renderMarket() {
  const st = here(), w = W(), b = G.board[st] || {};
  const rows = GOOD_IDS.map((g) => {
    const e = b[g], q = S.market[g] || "";
    const have = G.ship.cargo[g]?.qty || 0;
    const n = parseInt(q, 10) || 0;
    const est = e && n ? `≈ ${cr(E.quote(e.p, n))} según tu precio` : n ? "sin precio anotado: a ciegas" : "";
    return `<tr><td>${cap(goodName(g))}</td><td class="num">${e ? `${e.src === "público" ? "≈ " : ""}${nf.format(e.p)}` : "—"}<span class="age">${e ? ageText(e.t) : ""}</span></td><td>${have || ""}</td>
      <td><input class="qty" data-qty="${g}" value="${esc(q)}" inputmode="numeric" placeholder="0"><span class="est">${est}</span></td>
      <td class="tbtns"><button data-buy="${g}" ${n ? "" : "disabled"}>Comprar</button><button data-sell="${g}" ${n && have ? "" : "disabled"}>Vender</button></td></tr>`;
  }).join("");
  screen.innerHTML = `<section class="card market">
    <button class="ghost back" data-go="station">← Volver a la estación</button>
    <h2>Mercado de ${STATIONS[st].name}</h2>
    <p class="dim small">Las cuentas se hacen con lo que tú anotaste. La compra o la venta se cierra al precio real, y cada unidad lo mueve un 1%.</p>
    ${S.msg ? `<p class="msg">${esc(S.msg)}</p>` : ""}
    <table class="mkt"><thead><tr><th>Mercancía</th><th>Tu precio</th><th>Llevas</th><th>Cantidad</th><th></th></tr></thead><tbody>${rows}</tbody></table>
    <p>Créditos: <b>${cr(G.ship.credits)}</b> · Bodega: <b>${cargoN()}/${G.ship.hold}</b></p>
    ${st === HOLD_UPGRADE.at && G.ship.hold < HOLD_UPGRADE.hold ? `<p><button id="upgradeBtn">Ampliar la bodega a ${HOLD_UPGRADE.hold} unidades · ${cr(HOLD_UPGRADE.cost)}</button></p>` : ""}
  </section>`;
  S.msg = null;
  void w;
}

function renderMap() {
  const st = here(), pos = { tequendama: [70, 150], bachue: [190, 60], iguaque: [310, 150] };
  const left = turnsLeft();
  const line = (a, b) => `<line x1="${pos[a][0]}" y1="${pos[a][1]}" x2="${pos[b][0]}" y2="${pos[b][1]}"/><text x="${(pos[a][0] + pos[b][0]) / 2}" y="${(pos[a][1] + pos[b][1]) / 2 - 6}">${fuel(a, b)} cr</text>`;
  screen.innerHTML = `<section class="card map">
    <button class="ghost back" data-go="station">← Volver a la estación</button>
    <h2>Mapa de la ruta</h2>
    <p>${left > 0 ? `Te quedan <b>${left}</b> ${left === 1 ? "salto" : "saltos"} en esta sesión. Cada salto es un turno: los precios se mueven.` : "Se acabaron los saltos de esta sesión."}</p>
    <svg viewBox="0 0 380 200" class="route">${line("tequendama", "bachue")}${line("bachue", "iguaque")}${line("tequendama", "iguaque")}
      ${STATION_IDS.map((k) => `<g class="node ${k === st ? "here" : ""}"><circle cx="${pos[k][0]}" cy="${pos[k][1]}" r="${k === st ? 14 : 10}"/><text x="${pos[k][0]}" y="${pos[k][1] + 30}">${STATIONS[k].name}</text></g>`).join("")}</svg>
    <div class="grid three">${STATION_IDS.map((k) => `<div class="card mini">
      <h3>${STATIONS[k].name}</h3>
      <table class="board">${boardRows(k)}</table>
      ${k === st ? `<p class="dim">Estás aquí.</p>` : `<button class="primary" data-jump="${k}" ${left > 0 && G.ship.credits >= fuel(st, k) ? "" : "disabled"}>Saltar · ${cr(fuel(st, k))}</button>`}
    </div>`).join("")}</div>
    ${left <= 0 ? `<p><button class="primary" id="endBtn">Cerrar la sesión</button></p>` : ""}
  </section>`;
}

function answerText(e) {
  const a = e.answer, t = e.truth || {};
  if (e.kind === "broadcast") return GOOD_IDS.filter((g) => g in a || g in t).map((g) => `${goodName(g)}: ${a[g] != null ? nf.format(a[g]) : "—"}${a[g] !== t[g] ? ` → <b>${t[g] != null ? nf.format(t[g]) : "no lo dijeron"}</b>` : " ✓"}`).join(" · ");
  if (e.kind === "rumor") return [["event", (k) => EVENTS[k]?.what], ["station", (k) => STATIONS[k]?.name], ["certainty", (k) => CERTAINTY[k]?.label]].map(([k, f]) => `${a[k] ? f(a[k]) : "—"}${a[k] !== t[k] ? ` → <b>${f(t[k])}</b>` : " ✓"}`).join(" · ");
  const F = { good: goodName, destination: (k) => STATIONS[k]?.name, qty: String, deadline: (n) => `${n} saltos`, pay: cr, penalty: cr };
  return Object.keys(F).map((k) => `${a[k] != null && a[k] !== "" ? F[k](a[k]) : "—"}${a[k] !== t[k] ? ` → <b>${F[k](t[k])}</b>` : " ✓"}`).join(" · ");
}
function renderEnd() {
  const L = G.last;
  if (!L) { S.view = "station"; return render(); }
  const d = L.worth1 - L.worth0;
  const hist = G.history.slice(-6);
  screen.innerHTML = `<section class="card end">
    <h2>Fin de la sesión ${L.n}</h2>
    <p class="big">${cr(L.worth0)} → <b>${cr(L.worth1)}</b> <span class="${d >= 0 ? "good" : "bad"}">${d >= 0 ? "+" : ""}${cr(d)}</span></p>
    <p class="dim">El patrimonio cuenta tus créditos y la carga al precio real del puerto. ${L.turns} ${L.turns === 1 ? "turno" : "turnos"}${L.cancelled ? `; ${L.cancelled} contrato${L.cancelled === 1 ? " quedó cancelado" : "s quedaron cancelados"} sin multa` : ""}.</p>
    ${L.best ? `<p>Mejor negocio: ${L.best.contract ? "un contrato de" : "vender"} ${Math.abs(L.best.qty)} de ${goodName(L.best.g)} en ${STATIONS[L.best.st].name}, ganancia ${cr(L.best.profit)}.</p>` : ""}
    <p>Índice de oído en Rumbo: ${L.rating0 != null ? `${shown(L.rating0)} → ` : ""}<b>${shown(G.rating.th)}</b>${provisional(G.rating) ? " (provisional)" : ""}.</p>
    ${hist.length > 1 ? `<p class="dim small">Ganancia por turno en tus últimas sesiones: ${hist.map((h) => `${h.perTurn >= 0 ? "+" : ""}${nf.format(h.perTurn)}`).join(" · ")}</p>` : ""}
    <h3>${L.log.length ? "Lo que se te escapó" : "No se te escapó nada"}</h3>
    ${L.log.map((e, i) => { const c = BY_ID[e.id]; return c ? `<div class="lesson">
      <button class="ghost" data-replay="${e.id}">▶</button>
      <div><p class="dim small">${{ broadcast: "Radio", rumor: "Cantina", contract: "Contrato" }[e.kind]} · ${SPEAKERS[c.speaker].name}</p>
      <p class="transcript" translate="no">${esc(c.text)}</p>
      <p class="small">${answerText(e)}</p></div></div>` : ""; }).join("")}
    <p><button class="primary" id="startBtn">Nueva sesión</button></p>
  </section>`;
}

// ---------------------------------------------------------------- input
screen.addEventListener("click", (e) => {
  const t = e.target.closest("button");
  if (!t || t.disabled) return;
  if (t.id === "startBtn") { startSession(); S.view = "station"; return render(); }
  if (t.dataset.go) { stop(audioEl); S.view = t.dataset.go; S.clip = t.dataset.go === "station" ? null : S.clip; return render(); }
  if (t.id === "endBtn") { if (turnsLeft() > 0 && !confirm("¿Terminar la sesión ahora?")) return; return endSession(); }
  if (t.dataset.src === "broadcast") return openClip(BY_ID[ses().visit.broadcast], "broadcast");
  if (t.dataset.src === "contract") return openClip(BY_ID[ses().visit.offer], "contract");
  if (t.dataset.drink) return buyDrink(t.dataset.drink);
  if (t.id === "clipPlay") return play(false);
  if (t.id === "replayBtn") return play(false);
  if (t.id === "slowBtn") return play(true);
  if (t.dataset.jump) return jump(t.dataset.jump);
  if (t.dataset.deliver) return deliver(ses().contracts.find((k) => k.clip === t.dataset.deliver));
  if (t.dataset.buy || t.dataset.sell) {
    const g = t.dataset.buy || t.dataset.sell, n = parseInt(S.market[g], 10) || 0;
    S.market[g] = "";
    return doTrade(g, t.dataset.buy ? n : -n);
  }
  if (t.id === "upgradeBtn") {
    if (G.ship.credits < HOLD_UPGRADE.cost) return toast("No te alcanzan los créditos.");
    G.ship.credits -= HOLD_UPGRADE.cost; G.ship.hold = HOLD_UPGRADE.hold;
    S.msg = `Tu bodega ahora carga ${HOLD_UPGRADE.hold} unidades.`;
    save();
    return render();
  }
  if (t.dataset.replay) { const c = BY_ID[t.dataset.replay]; return playClip(audioEl, `media/rumbo/${c.file}`, { level: 0 }); }
});
screen.addEventListener("submit", (e) => {
  e.preventDefault();
  const f = e.target;
  if (!S.clip) return;
  const kind = S.clip.c.kind;
  if (kind === "broadcast") return submitBroadcast(f);
  if (kind === "rumor") return submitRumor(f);
  if (kind === "contract") return submitContract(f, e.submitter?.value === "1");
});
screen.addEventListener("input", (e) => {
  const g = e.target.dataset?.qty;
  if (!g) return;
  S.market[g] = e.target.value.replace(/\D/g, "");
  // only the row's estimate and buttons change, so typing keeps focus
  const row = e.target.closest("tr"), n = parseInt(S.market[g], 10) || 0, p = G.board[here()]?.[g];
  row.querySelector(".est").textContent = p && n ? `≈ ${cr(E.quote(p.p, n))} según tu precio` : n ? "sin precio anotado: a ciegas" : "";
  row.querySelector("[data-buy]").disabled = !n;
  row.querySelector("[data-sell]").disabled = !n || !(G.ship.cargo[g]?.qty);
});
$("#langBtn").textContent = lang() === "es" ? "English" : "Español";
$("#langBtn").onclick = () => setLang(lang() === "es" ? "en" : "es");
if (CFG.online) { $("#listenLink").hidden = true; $("#epLink").hidden = true; }

// debugging, as window.leyendas: S, G, E and the renderers
window.rumbo = { S, get G() { return G; }, E, W, render, BY_ID, CLIPS, diffOf, reset: () => { G = fresh(); save(); render(); } };
await startI18n();
render();
