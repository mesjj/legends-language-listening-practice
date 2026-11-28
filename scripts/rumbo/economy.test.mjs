// Rumbo's economy: node --test scripts/rumbo/
import test from "node:test";
import assert from "node:assert/strict";
import { newWorld, advance, price, prices, bindBroadcast, trade, quote, addEvent, eventMult, pickBroadcast, tellRumor, truthChance, leadFor, netWorth } from "../../public/rumbo/economy.js";
import { STATION_IDS, GOOD_IDS } from "../../public/rumbo/data.js";
import { numbersIn, parseNumber } from "../../public/listen-core.js";

const run = (seed, n) => { const W = newWorld(seed); for (let i = 0; i < n; i++) advance(W); return W; };

test("the same seed gives the same prices", () => {
  const a = run("s1", 8), b = run("s1", 8), c = run("s2", 8);
  for (const st of STATION_IDS) assert.deepEqual(prices(a, st), prices(b, st));
  assert.notDeepEqual(STATION_IDS.map((st) => prices(a, st)), STATION_IDS.map((st) => prices(c, st)));
  assert.deepEqual(a.events, b.events);
});

test("a broadcast binds the true prices to the spoken ones", () => {
  const W = run("s3", 3);
  addEvent(W, { type: "huelga", start: W.turn, source: "test" });
  bindBroadcast(W, "tequendama", { mineral: 342, hielo: 18 });
  assert.equal(price(W, "tequendama", "mineral"), 342);
  assert.equal(price(W, "tequendama", "hielo"), 18);
});

test("an event moves its price by its stated size, only while it lasts", () => {
  const W = newWorld("s4", 0, { background: 0 });
  const before = W.anchor.iguaque.comida;
  const e = addEvent(W, { type: "plaga", start: 1, source: "test" });
  assert.ok(e.size >= 0.3 && e.size <= 0.8);
  W.turn = 1;
  assert.equal(eventMult(W, "iguaque", "comida"), 1 + e.size);
  assert.equal(price(W, "iguaque", "comida"), Math.round(before * (1 + e.size)));
  assert.equal(eventMult(W, "iguaque", "mineral"), 1);
  W.turn = 1 + e.dur;
  assert.equal(eventMult(W, "iguaque", "comida"), 1);
});

test("trades move the price 1% a unit, and the quote matches the fill", () => {
  const W = newWorld("s5");
  const p0 = price(W, "bachue", "medicinas");
  const q = quote(p0, 10), r = trade(W, "bachue", "medicinas", 10);
  assert.equal(r.total, q);
  assert.ok(price(W, "bachue", "medicinas") > p0);
  const p1 = price(W, "bachue", "medicinas"), s = trade(W, "bachue", "medicinas", -10);
  assert.equal(s.total, quote(p1, -10));
  assert.ok(s.total < r.total, "a round trip loses");
});

test("pickBroadcast takes a fitting clip and skips used ones", () => {
  const W = newWorld("s6");
  const p = prices(W, "bachue");
  const clips = [
    { id: "far", kind: "broadcast", facts: { station: "bachue", prices: { mineral: p.mineral * 3 } } },
    { id: "near", kind: "broadcast", facts: { station: "bachue", prices: { mineral: p.mineral + 2 } } },
    { id: "other", kind: "broadcast", facts: { station: "iguaque", prices: { mineral: 1 } } },
  ];
  assert.equal(pickBroadcast(clips, W, "bachue").id, "near");
  assert.equal(pickBroadcast(clips, W, "bachue", new Set(["near"])).id, "far");
});

test("rumors: hedging and liars lower the chance, harder clips warn earlier", () => {
  assert.ok(truthChance("rocio", "seguro") > truthChance("rocio", "rumor"));
  assert.ok(truthChance("rocio", "seguro") > truthChance("chato", "seguro"));
  assert.deepEqual([leadFor(0.1), leadFor(0.5), leadFor(0.9)], [1, 2, 3]);
  let trues = 0;
  for (let i = 0; i < 400; i++) {
    const W = newWorld("r" + i, 0, { background: 0 });
    const r = tellRumor(W, { id: "x" + i, speaker: "rocio", facts: { event: "huelga", certainty: "seguro" } }, 0.9, i);
    if (r.truth) { trues++; assert.equal(r.event.start, 3); assert.equal(W.events.length, 1); } else assert.equal(W.events.length, 0);
  }
  assert.ok(trues > 320 && trues < 390, `rocio seguro true ${trues}/400`);
});

test("net worth counts credits and cargo at the hub", () => {
  const W = newWorld("s7");
  assert.equal(netWorth({ credits: 100, cargo: { mineral: { qty: 2, cost: 0 } } }, W), 100 + 2 * price(W, "bachue", "mineral"));
});

test("Spanish numbers, in words or digits", () => {
  assert.deepEqual(numbersIn("el mineral sube a trescientos cuarenta y dos créditos, el agua baja a dieciocho"), [342, 18]);
  assert.deepEqual(numbersIn("seiscientos noventa y un créditos y una multa de mil doscientos"), [691, 1200]);
  assert.deepEqual(numbersIn("un cargamento de dos mil quinientos"), [2500]);
  for (const [s, n] of [["342", 342], ["1.342", 1342], ["trescientos cuarenta y dos", 342], ["mil", 1000], ["hola", null], ["", null]]) assert.equal(parseNumber(s), n);
});
