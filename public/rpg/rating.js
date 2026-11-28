// Índice de oído: a listening rating, like a chess rating, measured only on lines heard for the first time
// (see the README). This module is pure (no DOM): the game, the server (api/wordfreq) and the scripts in
// scripts/rating/ all use it. Phase 1 collects the data: which audio you've heard, your history with every
// word, the features of each fresh line and its score. Phase 2: the model that predicts a fresh line's score
// and moves the rating by the surprise.
import { norm, isSound, isNameWord, nameSet, playable, chooseBlanks } from "../listen-core.js";

// ---------------------------------------------------------------- tuning, in one place
export const RATING = {
  listen: [1, 1, 0.75, 0.6], // the score's factor by listens before answering: 1 → 1.0, 2 → 0.75, 3+ → 0.6
  slow: 0.8, // any slow listen
  hint: 0.6, // a hint
  fast: 1.15, // the Parlanchín (veloz) plays lines this much faster
  // starting weights of the difficulty model (phase 2). Only the line's own features count toward the
  // rating; your history with its words (unseen, missRate) is kept apart (phase 3: "Qué te cuesta").
  w0: { rate: 0.8, len: 0.3, rarity: 0.3, maxRarity: 0.2, accents: 0.1, quiet: 0.4 },
};
// the line's own features: the same for everyone, standardized over the whole corpus
export const LINE_FEATURES = ["rate", "len", "rarity", "maxRarity", "accents"];

// ---------------------------------------------------------------- syllables
const STRONG = "aeoáéó", WEAK = "iuü", ACCWEAK = "íú";
const isV = (c) => STRONG.includes(c) || WEAK.includes(c) || ACCWEAK.includes(c);
// Spanish syllables by vowel groups: two strong vowels split (le-o), an accented í/ú splits (dí-a),
// a weak and any other vowel join (cie-lo, cui-da). The silent u of que/qui/gue/gui doesn't count,
// a final y after a vowel joins it (hoy, muy), y alone is a syllable. Digits: about two a number.
export function syllables(word) {
  let w = String(word).toLowerCase().normalize("NFC").replace(/[^a-záéíóúüñ0-9]/g, "");
  if (!w) return 0;
  if (/^\d+$/.test(w)) return Math.max(1, Math.min(6, w.length + 1));
  w = w.replace(/\d+/g, "").replace(/([qg])u(?=[eiéí])/g, "$1").replace(/y$/, "i"); // hoy, muy, rey: a closing vowel; y alone: one syllable
  let n = 0, prev = "";
  for (const c of w) {
    if (!isV(c)) { prev = ""; continue; }
    if (!prev) n++;
    else if ((STRONG.includes(prev) && STRONG.includes(c)) || ACCWEAK.includes(prev) || ACCWEAK.includes(c)) n++;
    prev = c;
  }
  return Math.max(1, n);
}

// ---------------------------------------------------------------- which words count
// The words of a line that are listened for: not sounds (ah, mm, jaja), not the episode's foreign names.
export function counted(words, names) {
  const N = nameSet(names);
  return words.filter((x) => norm(x.w).length && !isSound(x.w) && !isNameWord(N, x.w));
}
const hasAccent = (w) => /[áéíóúüñ]/i.test(w);

// ---------------------------------------------------------------- corpus word frequency
// counts: { word: n } over every Spanish transcript; total: the sum. Rarity = -log((n + 1) / total).
export function countWords(transcripts) {
  const counts = {};
  let total = 0;
  for (const t of transcripts) {
    for (const s of t.segments || []) for (const x of counted(s.words || [], t.names)) {
      const k = norm(x.w);
      counts[k] = (counts[k] || 0) + 1;
      total++;
    }
  }
  return { counts, total };
}
export const rarityOf = (freq, k) => (freq?.total ? -Math.log(((freq.counts[k] || 0) + 1) / freq.total) : null);

// ---------------------------------------------------------------- features of a line
// words: the exercise's words ({w, s, e}); ctx: { names, freq, words (the player's ch.words), playRate, quiet }.
// Returns raw (unstandardized) values, or null when nothing in the line is listened for.
export function lineFeatures(words, ctx = {}) {
  const ws = counted(words, ctx.names);
  if (!ws.length) return null;
  const s0 = words.find((x) => x.s != null)?.s, e1 = [...words].reverse().find((x) => x.e != null)?.e;
  const dur = s0 != null && e1 != null ? Math.max(0.3, e1 - s0) : null;
  const syl = words.reduce((a, x) => a + (isSound(x.w) ? 0 : syllables(x.w)), 0);
  const keys = ws.map((x) => norm(x.w));
  const rar = ctx.freq ? keys.map((k) => rarityOf(ctx.freq, k)) : null;
  const hist = ctx.words ? keys.map((k) => ctx.words[k] || { seen: 0, hit: 0, miss: 0 }) : null;
  const r3 = (v) => (v == null ? null : Math.round(v * 1000) / 1000);
  return {
    rate: dur ? r3((syl / dur) * (ctx.playRate || 1)) : null,
    len: r3(Math.log(1 + ws.length)),
    rarity: rar ? r3(rar.reduce((a, b) => a + b, 0) / rar.length) : null,
    maxRarity: rar ? r3(Math.max(...rar)) : null,
    accents: r3(ws.filter((x) => hasAccent(x.w)).length / ws.length),
    quiet: ctx.quiet ? 1 : 0,
    // the player's history with these words: for "what makes lines hard for you", not for the rating
    unseen: hist ? r3(hist.filter((h) => !h.seen).length / hist.length) : null,
    missRate: hist ? r3(hist.reduce((a, h) => a + (h.miss + 1) / (h.hit + h.miss + 2), 0) / hist.length) : null,
  };
}

// Mean and SD of the line's own features over every line the game can ask (playable), computed once
// (api/wordfreq, rebuilt when an episode is added), never as a running average, so ratings don't drift.
// Two sets: dictation (the whole line) and gaps (the gapped words, picked as the game picks them;
// the speed is still the whole line's).
export function featureStats(transcripts, freq) {
  const acc = { dict: {}, cloze: {} };
  for (const K of Object.values(acc)) for (const k of LINE_FEATURES) K[k] = [];
  const put = (K, f) => { if (f) for (const k of LINE_FEATURES) if (f[k] != null && isFinite(f[k])) K[k].push(f[k]); };
  for (const t of transcripts) (t.segments || []).forEach((s, si) => {
    if (!playable(s)) return;
    const ctx = { names: t.names, freq }, whole = lineFeatures(s.words, ctx);
    put(acc.dict, whole);
    const gaps = lineFeatures(chooseBlanks(t.segments, si).map((i) => s.words[i]), ctx);
    if (gaps && whole) gaps.rate = whole.rate;
    put(acc.cloze, gaps);
  });
  const out = {};
  for (const [kind, K] of Object.entries(acc)) {
    out[kind] = {};
    for (const [k, v] of Object.entries(K)) {
      const m = v.reduce((a, b) => a + b, 0) / (v.length || 1);
      const sd = Math.sqrt(v.reduce((a, b) => a + (b - m) ** 2, 0) / (v.length || 1)) || 1;
      out[kind][k] = { mean: +m.toFixed(4), sd: +sd.toFixed(4), n: v.length };
    }
  }
  return out;
}
// stats: one kind's (stats.dict or stats.cloze)
export function standardize(feat, stats) {
  const x = {};
  for (const k of LINE_FEATURES) x[k] = feat?.[k] == null || !stats?.[k] ? 0 : (feat[k] - stats[k].mean) / stats[k].sd;
  x.quiet = feat?.quiet || 0;
  return x;
}

// ---------------------------------------------------------------- what audio has been heard
// Per line (segment index): 1 = all of it, or a list of [a, b) word ranges. A part of a line is fresh
// only if none of its words' audio was played before (a part of a line already heard whole isn't).
export function overlaps(rec, a, b) {
  if (!rec) return false;
  if (rec === 1) return true;
  return rec.some(([x, y]) => x < b && a < y);
}
export function addHeard(rec, a, b, n) {
  if (rec === 1) return 1;
  if (a <= 0 && b >= n) return 1;
  const all = [...(rec || []), [a, b]].sort((p, q) => p[0] - q[0]);
  const out = [];
  for (const r of all) { const last = out[out.length - 1]; if (last && r[0] <= last[1]) last[1] = Math.max(last[1], r[1]); else out.push([...r]); }
  return out.length === 1 && out[0][0] <= 0 && out[0][1] >= n ? 1 : out;
}
// An exercise key ("12", "12:0-6", "12#2") → { si, a, b } (b null: to the end of the line)
export function parseExKey(key) {
  const m = /^(\d+)(?::(\d+)-(\d+))?/.exec(String(key));
  return m ? { si: +m[1], a: m[2] != null ? +m[2] : 0, b: m[3] != null ? +m[3] : null } : null;
}

// ---------------------------------------------------------------- the score of an answer (S, 0 to 1)
// strict accuracy (accents count; the gear's forgiveness doesn't), less for listening again or for help.
// Answers with help still count: dropping them would leave only the easy lines.
export function answerScore({ strict, plays = 1, slows = 0, hinted = false }) {
  if (strict == null) return null;
  const f = RATING.listen[Math.min(RATING.listen.length - 1, Math.max(1, plays))];
  return Math.round(Math.max(0, Math.min(1, strict)) * f * (slows ? RATING.slow : 1) * (hinted ? RATING.hint : 1) * 1000) / 1000;
}

// ---------------------------------------------------------------- the player's history with words
// ch.words: { word: { seen, hit, miss } } over every episode, from every scored word.
export function addWord(W, w, ok) {
  const k = norm(w);
  if (k.length < 2 || isSound(w)) return;
  const e = (W[k] ||= { seen: 0, hit: 0, miss: 0 });
  e.seen++;
  if (ok) e.hit++; else e.miss++;
}

// ---------------------------------------------------------------- the model (phase 2)
// D = w · x (x: the line's standardized features; no intercept, so θ = 0 is "50/50 on an average line"),
// E = sigmoid(θ − D) is the predicted score. After each fresh answer with score S:
//   θ ← θ + Kθ (S − E),  Kθ = max(0.08, 0.5 / sqrt(1 + n/20))
//   w ← w − η (S − E) x − λ (w − w0)
// Doing worse than predicted (S < E) moves w toward x: lines like this one count as harder from then on.
Object.assign(RATING, { kMin: 0.08, k0: 0.5, kN: 20, eta: 0.01, lambda: 0.001, clip: 3, provisional: 50, base: 1500, scale: 200 });
export const sigmoid = (z) => 1 / (1 + Math.exp(-z));
// standardized features, cut at ±3 SD so one odd line (a two-word shout) can't swing the weights
export function featureVector(feat, stats) {
  const x = standardize(feat, stats), c = RATING.clip;
  for (const k of Object.keys(x)) x[k] = Math.max(-c, Math.min(c, x[k]));
  return x;
}
export const newRating = () => ({ th: 0, n: 0, hist: [] });
export const newModel = () => ({ w: { ...RATING.w0 } });
export const difficulty = (x, w) => Object.keys(RATING.w0).reduce((a, k) => a + (w[k] ?? RATING.w0[k]) * (x[k] || 0), 0);
export const predict = (x, w, th) => sigmoid(th - difficulty(x, w));
export const kTheta = (n) => Math.max(RATING.kMin, RATING.k0 / Math.sqrt(1 + n / RATING.kN));
// R: one rating ({ th, n, hist }), M: its model ({ w }); both changed in place. day: "2026-11-27" for hist.
export function rateUpdate(R, M, x, S, day) {
  const E = predict(x, M.w, R.th), th0 = R.th, d = S - E;
  R.th = th0 + kTheta(R.n) * d;
  R.n++;
  for (const k of Object.keys(RATING.w0)) {
    const w = M.w[k] ?? RATING.w0[k];
    M.w[k] = +(w - RATING.eta * d * (x[k] || 0) - RATING.lambda * (w - RATING.w0[k])).toFixed(5);
  }
  R.th = +R.th.toFixed(5);
  if (day) { const last = R.hist[R.hist.length - 1]; if (last?.[0] === day) last[1] = R.th; else R.hist.push([day, R.th]); }
  return { E: +E.toFixed(3), th0, th1: R.th };
}
export const shown = (th) => Math.round(RATING.base + RATING.scale * th);
export const provisional = (R) => (R?.n || 0) < RATING.provisional;
// the tag before answering, from E: fácil / media / difícil / brutal
export const tagOf = (E) => (E >= 0.75 ? "fácil" : E >= 0.5 ? "media" : E >= 0.25 ? "difícil" : "brutal");
// log loss of a predicted score E for an actual score S (S between 0 and 1)
export const logLoss = (E, S) => { const e = Math.min(1 - 1e-6, Math.max(1e-6, E)); return -(S * Math.log(e) + (1 - S) * Math.log(1 - e)); };
