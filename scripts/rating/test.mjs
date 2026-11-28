// Unit tests for public/rpg/rating.js:  node --test scripts/rating/
import test from "node:test";
import assert from "node:assert/strict";
import * as R from "../../public/rpg/rating.js";
const Rr = R;
const R0 = () => ({ r: R.newRating(), model: R.newModel() });

test("syllables", () => {
  const cases = { y: 1, hoy: 1, muy: 1, que: 1, qué: 1, guitarra: 3, pingüino: 3, día: 2, leo: 2, ciudad: 2, cuidado: 3,
    murciélago: 4, oído: 3, aeropuerto: 5, países: 3, crees: 2, bueno: 2, averiguar: 4, estáis: 2, "¿Qué?": 1, "15": 3 };
  for (const [w, n] of Object.entries(cases)) assert.equal(R.syllables(w), n, w);
});

const W = (text, t0 = 0, per = 0.25) => text.split(" ").map((w, i) => ({ w, s: t0 + i * per, e: t0 + (i + 1) * per }));

test("features: speed, length, sounds and names left out", () => {
  const f = R.lineFeatures(W("Ah, Kramer dice que no viene"), { names: ["Kramer"] });
  assert.equal(f.len, +Math.log(1 + 4).toFixed(3)); // dice que no viene
  // 1 (dice: 2) + que 1 + no 1 + vie-ne 2 = 6 syllables; Kramer is a name but it's still spoken: 2 more
  assert.equal(f.rate, +(8 / 1.5).toFixed(3));
  assert.equal(R.lineFeatures(W("Ah, mm"), {}), null);
  assert.equal(R.lineFeatures(W("Kramer"), { names: ["Kramer"] }), null);
  assert.equal(R.lineFeatures(W("sí, señor"), {}).accents, 1);
  assert.equal(R.lineFeatures(W("Dice que no viene"), { playRate: 1.15 }).rate, +((6 / 1) * 1.15).toFixed(3));
});

test("features: rarity and the player's word history", () => {
  const freq = { counts: { que: 99, raro: 0 }, total: 100 };
  const f = R.lineFeatures(W("que raro"), { freq, words: { que: { seen: 5, hit: 4, miss: 1 } } });
  assert.ok(Math.abs(f.rarity - (-Math.log(1) - Math.log(1 / 100)) / 2) < 0.002);
  assert.ok(Math.abs(f.maxRarity - Math.log(100)) < 0.002);
  assert.equal(f.unseen, 0.5);
  assert.equal(f.missRate, +(((1 + 1) / (5 + 2) + 1 / 2) / 2).toFixed(3));
});

test("heard audio: overlapping parts aren't fresh", () => {
  let h = R.addHeard(undefined, 0, 4, 10);
  assert.ok(R.overlaps(h, 3, 6));
  assert.ok(!R.overlaps(h, 4, 8));
  h = R.addHeard(h, 4, 8, 10);
  assert.deepEqual(h, [[0, 8]]);
  h = R.addHeard(h, 8, 10, 10);
  assert.equal(h, 1);
  assert.ok(R.overlaps(1, 0, 1));
  assert.ok(!R.overlaps(undefined, 0, 1));
  assert.deepEqual(R.parseExKey("12"), { si: 12, a: 0, b: null });
  assert.deepEqual(R.parseExKey("12:3-7#2"), { si: 12, a: 3, b: 7 });
});

test("answer score", () => {
  assert.equal(R.answerScore({ strict: 1, plays: 1 }), 1);
  assert.equal(R.answerScore({ strict: 1, plays: 2 }), 0.75);
  assert.equal(R.answerScore({ strict: 1, plays: 5 }), 0.6);
  assert.equal(R.answerScore({ strict: 0.5, plays: 2, slows: 1, hinted: true }), +(0.5 * 0.75 * 0.8 * 0.6).toFixed(3));
  assert.equal(R.answerScore({ strict: null }), null);
});

test("word history", () => {
  const H = {};
  R.addWord(H, "¿Qué?", true); R.addWord(H, "que", false); R.addWord(H, "mm", true); R.addWord(H, "y", true);
  assert.deepEqual(H, { que: { seen: 2, hit: 1, miss: 1 } });
});

test("corpus stats: both kinds, standardized", () => {
  const T = [{ segments: [{ words: W("esto es una frase normal") }, { words: W("otra frase bastante parecida aquí") }] }];
  const freq = R.countWords(T);
  const st = R.featureStats(T, freq);
  assert.ok(st.dict.rate.n === 2 && st.cloze.len.n === 2);
  const x = R.standardize(R.lineFeatures(T[0].segments[0].words, { freq }), st.dict);
  assert.ok(Object.values(x).every(Number.isFinite));
});

test("model: update signs", () => {
  const x = { rate: 1, len: 0.5, rarity: 0, maxRarity: 0, accents: 0, quiet: 0 };
  let R = R0(), M = R.model;
  const up = Rr.rateUpdate(R.r, M, x, 1, "2026-11-27");
  assert.ok(up.th1 > up.th0, "better than expected raises θ");
  assert.equal(M.w.rate, Rr.RATING.w0.rate - Rr.RATING.eta * (1 - up.E) * 1); // and makes such lines count as easier
  R = R0(); M = R.model;
  const down = Rr.rateUpdate(R.r, M, x, 0, "2026-11-27");
  assert.ok(down.th1 < down.th0, "worse than expected lowers θ");
  assert.ok(M.w.rate > Rr.RATING.w0.rate && M.w.len > Rr.RATING.w0.len, "and moves w along x");
  assert.equal(M.w.rarity, Rr.RATING.w0.rarity); // features at 0 don't move
  assert.deepEqual(R.r.hist, [["2026-11-27", R.r.th]]);
  Rr.rateUpdate(R.r, M, x, 0, "2026-11-27");
  assert.equal(R.r.hist.length, 1, "one entry per day");
  assert.equal(Rr.shown(0), 1500);
  assert.equal(Rr.predict({}, Rr.RATING.w0, 0), 0.5);
  assert.ok(Rr.kTheta(0) === 0.5 && Rr.kTheta(1e6) === 0.08);
  assert.equal(Rr.tagOf(0.8), "fácil"); assert.equal(Rr.tagOf(0.1), "brutal");
});
