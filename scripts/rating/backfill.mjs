#!/usr/bin/env node
// Índice de oído, phase 1: replay the line log and rebuild what the rating needs from it.
//
//   node scripts/rating/backfill.mjs [data/lines.jsonl] [--out data/rating-replay.json]
//
// Goes through every `answer` event in time order. It rebuilds which audio was heard (per episode, per
// line, by word range) and the word history (seen / hit / miss), works out each answer's line features
// and score S (public/rpg/rating.js), and writes them all to --out for the model and eval scripts.
//
// Freshness: answers logged since the rating data started carry `fresh` (decided in the game, which knows
// everything the character had already answered). Older answers don't: for those, "fresh" means only the
// first time in the log, which overcounts (the log starts long after the character did), so they're
// marked `approx` and kept apart in the summary.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as R from "../../public/rpg/rating.js";
import { norm } from "../../public/listen-core.js";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args.splice(i, 2)[1] : d; };
const OUT = opt("--out", path.join(ROOT, "data", "rating-replay.json"));
const MEDIA = process.env.MEDIA_DIR || path.join(ROOT, "media");
const LOG = args[0] || path.join(ROOT, "data", "lines.jsonl");

const events = fs.readFileSync(LOG, "utf8").split("\n").filter(Boolean).map((l) => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
events.sort((a, b) => a.t - b.t);
const shows = new Map(events.filter((e) => e.ev === "show").map((e) => [e.id, e]));

// the corpus: the server's cache if it's there, else counted here the same way
const TS = {};
const transcript = (ep) => {
  if (!(ep in TS)) { try { TS[ep] = JSON.parse(fs.readFileSync(path.join(MEDIA, ep, "transcript.json"), "utf8")); } catch { TS[ep] = null; } }
  return TS[ep];
};
const rated = (ep, T) => T && !T.zones && T.source !== "course" && (!T.lang || T.lang === "es") && !/-en$/.test(ep);
let wf = null;
try { wf = JSON.parse(fs.readFileSync(path.join(ROOT, "data", "wordfreq.json"), "utf8")); if (!wf.stats?.dict) wf = null; } catch { /* count below */ }
if (!wf) {
  const ts = fs.readdirSync(MEDIA).map((ep) => [ep, transcript(ep)]).filter(([ep, T]) => rated(ep, T)).map(([, T]) => T);
  const f = R.countWords(ts);
  wf = { ...f, stats: R.featureStats(ts, f) };
}

// an answer's word range: from its exercise key, or (older events) from its show's start and end times
function range(e, T) {
  const seg = T.segments[e.si];
  if (!seg) return null;
  if (e.ex) { const k = R.parseExKey(e.ex); return k && { a: k.a, b: k.b ?? seg.words.length, cloze2: /#2$/.test(e.ex) }; }
  const sh = shows.get(e.id);
  if (sh?.start == null) return { a: 0, b: seg.words.length };
  const idx = seg.words.map((w, i) => (w.s >= sh.start - 0.02 && w.e <= sh.end + 0.02 ? i : -1)).filter((i) => i >= 0);
  return idx.length ? { a: idx[0], b: idx[idx.length - 1] + 1 } : { a: 0, b: seg.words.length };
}

const heard = {}, words = {}, out = [];
const tally = { answers: 0, skipped: 0, fresh: 0, approx: 0, seen: 0 };
for (const e of events) {
  if (e.ev !== "answer" || e.si == null || !e.ep) continue;
  tally.answers++;
  const T = transcript(e.ep), sh = shows.get(e.id) || {};
  const rg = T && range(e, T);
  if (!rg || sh.review || sh.card || e.kind === "recall" || sh.mode === "recall") { tally.skipped++; continue; }
  const seg = T.segments[e.si], n = seg.words.length, H = (heard[e.ep] ||= {});
  const firstInLog = !R.overlaps(H[e.si], rg.a, rg.b);
  const fresh = e.fresh != null ? e.fresh : firstInLog && rated(e.ep, T) && !seg.flagged;
  const approx = e.fresh == null;
  const kind = e.rk || (sh.mode === "cloze" ? "cloze" : "dict");
  let feat = e.feat || null;
  if (fresh && !feat) {
    const ws = seg.words.slice(rg.a, rg.b);
    // the gaps of an old cloze answer: the words it scored (a cloze answer's `w` lists only its gaps)
    const asked = kind === "cloze" ? ws.filter((w) => (e.w || []).some((x) => x[0] === w.w)) : ws;
    feat = R.lineFeatures(asked.length ? asked : ws, { names: T.names, freq: wf, words });
    if (feat && kind === "cloze") feat.rate = R.lineFeatures(ws, { names: T.names, freq: wf })?.rate ?? feat.rate;
  }
  const rs = e.rs ?? R.answerScore({ strict: e.strict ?? e.acc, plays: (e.plays || 0) + (e.slows || 0), slows: e.slows, hinted: e.hinted });
  if (fresh && feat) { tally.fresh++; if (approx) tally.approx++; out.push({ t: e.t, ep: e.ep, si: e.si, a: rg.a, b: rg.b, kind, approx, feat, rs, pred: e.pred ?? null }); }
  else tally.seen++;
  H[e.si] = R.addHeard(H[e.si], rg.a, rg.b, n);
  for (const [w, , c] of e.w || []) if (c !== "n") R.addWord(words, w, c === 2);
}

fs.writeFileSync(OUT, JSON.stringify({ made: new Date().toISOString(), log: LOG, stats: wf.stats, heard, words, answers: out }));

const mean = (a) => (a.length ? a.reduce((x, y) => x + y, 0) / a.length : NaN);
const f2 = (v) => (Number.isFinite(v) ? v.toFixed(2) : "–");
console.log(`answers ${tally.answers}: fresh ${tally.fresh} (${tally.approx} only first-in-log, approximate), already heard ${tally.seen}, not rateable ${tally.skipped}`);
for (const k of ["dict", "cloze"]) {
  const A = out.filter((x) => x.kind === k), exact = A.filter((x) => !x.approx);
  if (!A.length) continue;
  console.log(`\n${k}: ${A.length} fresh (${exact.length} decided by the game), mean S ${f2(mean(A.map((x) => x.rs)))}`);
  for (const f of [...R.LINE_FEATURES, "quiet", "unseen", "missRate"]) {
    const v = A.map((x) => x.feat[f]).filter((x) => x != null);
    if (v.length) console.log(`  ${f.padEnd(10)} mean ${f2(mean(v))}  corpus ${wf.stats[k]?.[f] ? f2(wf.stats[k][f].mean) : "–"}`);
  }
}
console.log(`\nwords with a history: ${Object.keys(words).length}; written to ${path.relative(process.cwd(), OUT)}`);
