// Rumbo's economy: pure functions (no DOM, no Math.random), so the same seed always gives the same
// prices and the tests in scripts/rumbo/ can run it in Node. A world is a plain object, saved as is.
//
// Every price is an anchor times the events active on it. Each turn the anchor takes a random step
// (±3%) and reverts a little toward the station's base; trades push it 1% a unit. A broadcast clip
// sets the anchor so the price is exactly what was said: the bank decides, the economy follows.
import { GOODS, GOOD_IDS, STATIONS, STATION_IDS, EVENTS, EVENT_SIZE, EVENT_DUR, CERTAINTY, SPEAKERS } from "./data.js";

export const ECON = {
  drift: 0.03, // the random step per turn, either way
  revert: 0.12, // share of the gap to the base closed each turn
  impact: 0.01, // each unit bought raises the price this much (sold: lowers)
  fit: 0.12, // a broadcast fits if its prices are within about this (log) distance of the true ones
  background: 3, // unannounced events per session
};

// ---------------------------------------------------------------- deterministic randomness
// a float in [0, 1) from any list of keys: the same keys, the same number
export function rand(...keys) {
  let h = 2166136261 >>> 0;
  const s = keys.join("|");
  for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
  h ^= h >>> 16; h = Math.imul(h, 0x85ebca6b); h ^= h >>> 13; h = Math.imul(h, 0xc2b2ae35); h ^= h >>> 16;
  return (h >>> 0) / 4294967296;
}
export const pick = (arr, ...keys) => arr[Math.floor(rand(...keys) * arr.length)];
const between = ([a, b], ...keys) => a + rand(...keys) * (b - a);
const intBetween = ([a, b], ...keys) => a + Math.floor(rand(...keys) * (b - a + 1));

// ---------------------------------------------------------------- prices
export const basePrice = (st, g) => GOODS[g].base * STATIONS[st].factor[g];

export function newWorld(seed, turn = 0, { eventTypes = Object.keys(EVENTS), background = ECON.background, turns = 12 } = {}) {
  const W = { seed: String(seed), turn, start: turn, anchor: {}, events: [] };
  for (const st of STATION_IDS) {
    W.anchor[st] = {};
    for (const g of GOOD_IDS) W.anchor[st][g] = basePrice(st, g) * (0.9 + 0.2 * rand(W.seed, "init", st, g));
  }
  // events nobody announced: the broadcasts are how you find out
  for (let i = 0; i < background && eventTypes.length; i++) {
    const type = pick(eventTypes, W.seed, "bg", i);
    const start = turn + 2 + Math.floor(rand(W.seed, "bgt", i) * Math.max(1, turns - 3));
    addEvent(W, { type, start, source: "bg" }, `bg${i}`);
  }
  return W;
}

export function addEvent(W, { type, start, source, clip = null }, key = W.events.length) {
  const E = EVENTS[type];
  // the same event already planned at that time is the same event
  const same = W.events.find((e) => e.type === type && e.start <= start + 1 && start <= e.start + e.dur);
  if (same) return same;
  const e = {
    type, station: E.station, good: E.good, start, source, clip,
    dur: intBetween(EVENT_DUR, W.seed, "dur", type, key),
    size: E.dir * +between(EVENT_SIZE, W.seed, "size", type, key).toFixed(3),
  };
  W.events.push(e);
  return e;
}
export const active = (e, turn) => turn >= e.start && turn < e.start + e.dur;
export function eventMult(W, st, g, turn = W.turn) {
  let m = 1;
  for (const e of W.events) if (e.station === st && e.good === g && active(e, turn)) m *= 1 + e.size;
  return m;
}
export const price = (W, st, g) => Math.max(1, Math.round(W.anchor[st][g] * eventMult(W, st, g)));
export const prices = (W, st) => Object.fromEntries(GOOD_IDS.map((g) => [g, price(W, st, g)]));

// one turn passes: every anchor takes its step
export function advance(W) {
  W.turn++;
  for (const st of STATION_IDS)
    for (const g of GOOD_IDS) {
      let a = W.anchor[st][g] * (1 + ECON.drift * (2 * rand(W.seed, "drift", W.turn, st, g) - 1));
      a += (basePrice(st, g) - a) * ECON.revert;
      W.anchor[st][g] = a;
    }
  return W;
}

// Buy (qty > 0) or sell (qty < 0) at the true price, unit by unit: each unit moves the price 1%.
// A unit bought is paid, then raises the price; a unit sold lowers it, then is paid. So buying and
// selling straight back always loses a little.
export function trade(W, st, g, qty) {
  const n = Math.abs(qty), buy = qty > 0;
  let total = 0;
  const first = price(W, st, g);
  for (let i = 0; i < n; i++) {
    if (buy) { total += price(W, st, g); W.anchor[st][g] *= 1 + ECON.impact; }
    else { W.anchor[st][g] *= 1 - ECON.impact; total += price(W, st, g); }
  }
  return { total, first, avg: n ? total / n : 0, after: price(W, st, g) };
}
// what a trade would cost at a given price, with its own impact, without doing it (the estimate)
export function quote(p, qty) {
  const n = Math.abs(qty), f = qty > 0 ? 1 + ECON.impact : 1 - ECON.impact;
  let total = 0, x = p;
  for (let i = 0; i < n; i++) {
    if (qty < 0) x *= f;
    total += Math.max(1, Math.round(x));
    if (qty > 0) x *= f;
  }
  return total;
}

// ---------------------------------------------------------------- broadcasts bind the prices
// facts: { good: price } as spoken. Afterwards price(W, st, g) is exactly the spoken price.
export function bindBroadcast(W, st, facts) {
  for (const [g, p] of Object.entries(facts)) W.anchor[st][g] = p / eventMult(W, st, g);
}
export function fitCost(W, st, facts) {
  const ds = Object.entries(facts).map(([g, p]) => Math.log(p / price(W, st, g)) ** 2);
  return ds.length ? Math.sqrt(ds.reduce((a, b) => a + b, 0) / ds.length) : Infinity;
}
// The broadcast for this station this turn: among clips not heard this session, those that fit the
// true prices; of those the least recently heard (across sessions), then the closest. heard: { id: time }.
export function pickBroadcast(clips, W, st, usedNow = new Set(), heard = {}) {
  const cand = clips.filter((c) => c.kind === "broadcast" && c.facts.station === st && !usedNow.has(c.id));
  if (!cand.length) return null;
  const scored = cand.map((c) => ({ c, cost: fitCost(W, st, c.facts.prices), last: heard[c.id] || 0 }));
  const fits = scored.filter((x) => x.cost <= ECON.fit);
  const pool = fits.length ? fits : scored.sort((a, b) => a.cost - b.cost).slice(0, 3);
  pool.sort((a, b) => a.last - b.last || a.cost - b.cost || (a.c.id < b.c.id ? -1 : 1));
  return pool[0].c;
}

// ---------------------------------------------------------------- rumors
// How likely what the speaker says comes true: their reliability, less when they hedge.
export const truthChance = (speaker, certainty) => (SPEAKERS[speaker]?.reliability ?? 0.5) * (CERTAINTY[certainty]?.trust ?? 0.5);
// A harder clip announces its event earlier (more turns to act on it).
export const leadFor = (d) => (d < 0.35 ? 1 : d < 0.65 ? 2 : 3);
// Tell a rumor: decide whether it's true; if so, its event is scheduled `lead` turns from now.
// Returns { truth, event }. A real event of that type already planned in the window makes it true too.
export function tellRumor(W, clip, d, key) {
  const lead = leadFor(d), start = W.turn + lead;
  const planned = W.events.find((e) => e.type === clip.facts.event && e.start > W.turn && e.start <= W.turn + 3);
  if (planned) { planned.told = true; return { truth: true, event: planned, lead: planned.start - W.turn }; }
  const truth = rand(W.seed, "truth", clip.id, key) < truthChance(clip.speaker, clip.facts.certainty);
  if (!truth) return { truth: false, event: null, lead, start };
  const event = addEvent(W, { type: clip.facts.event, start, source: "rumor", clip: clip.id }, `r${key}`);
  event.told = true;
  return { truth: true, event, lead };
}
// a rumor clip to tell now: one of the speaker's, not heard this session, least recently heard first
export function pickRumor(clips, speaker, usedNow = new Set(), heard = {}, key = "") {
  const cand = clips.filter((c) => c.kind === "rumor" && c.speaker === speaker && !usedNow.has(c.id));
  if (!cand.length) return null;
  const oldest = Math.min(...cand.map((c) => heard[c.id] || 0));
  const pool = cand.filter((c) => (heard[c.id] || 0) === oldest);
  return pick(pool, "rumor", speaker, key);
}
// who's drinking at a station this turn: two regulars
export function regularsAt(W, st, regulars) {
  const order = [...regulars].sort((a, b) => rand(W.seed, "bar", W.turn, st, a) - rand(W.seed, "bar", W.turn, st, b));
  return order.slice(0, 2);
}

// ---------------------------------------------------------------- the ship
export function cargoCount(ship) { return Object.values(ship.cargo).reduce((a, c) => a + c.qty, 0); }
// net worth: credits plus the cargo at the hub's true price (it buys everything)
export function netWorth(ship, W) {
  let v = ship.credits;
  for (const [g, c] of Object.entries(ship.cargo)) if (c.qty) v += c.qty * price(W, "bachue", g);
  return Math.round(v);
}

// ---------------------------------------------------------------- simulation (the clip pipeline samples prices from it)
// Price snapshots of whole sessions, events included, so broadcast clips cover what the game will need.
export function simulate(seed, turns = 12) {
  const W = newWorld(seed, 0, { background: 4, turns });
  const snaps = [];
  for (let t = 0; t <= turns; t++) {
    for (const st of STATION_IDS) snaps.push({ st, turn: t, prices: prices(W, st) });
    advance(W);
  }
  return snaps;
}
