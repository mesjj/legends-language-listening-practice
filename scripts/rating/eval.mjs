#!/usr/bin/env node
// Índice de oído: how good are the predictions?
//
//   node scripts/rating/eval.mjs [data/rating-replay.json] [--exact]
//
// Reads what scripts/rating/backfill.mjs wrote (run that first). For each rating (dictation, gaps):
//  - the game's own predictions, where the log has them (`pred`, since phase 2);
//  - a replay: the model run from scratch (θ = 0, w = w0) over every fresh answer in order, each line
//    predicted before it updates the model, as the game does. --exact leaves out the approximate answers
//    (from before the game decided freshness).
// Prints the log loss (lower is better; predicting the average score every time is the bar to beat) and a
// calibration table: predictions bucketed by tenths, and the mean actual score in each. The model is working
// when the two columns are close.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as R from "../../public/rpg/rating.js";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const args = process.argv.slice(2), exact = args.includes("--exact");
const file = args.find((a) => !a.startsWith("--")) || path.join(ROOT, "data", "rating-replay.json");
const D = JSON.parse(fs.readFileSync(file, "utf8"));
const f2 = (v) => (Number.isFinite(v) ? v.toFixed(2) : "  – ");
const mean = (a) => a.reduce((x, y) => x + y, 0) / a.length;

function report(title, pairs) {
  if (!pairs.length) return console.log(`  ${title}: none`);
  const ll = mean(pairs.map(([E, S]) => R.logLoss(E, S)));
  const base = mean(pairs.map(([, S]) => S)), llBase = mean(pairs.map(([, S]) => R.logLoss(base, S)));
  console.log(`  ${title}: ${pairs.length} lines, log loss ${ll.toFixed(3)} (always ${f2(base)}: ${llBase.toFixed(3)})`);
  console.log("    predicted   lines   mean predicted   mean actual");
  for (let b = 0; b < 10; b++) {
    const P = pairs.filter(([E]) => Math.min(9, Math.floor(E * 10)) === b);
    if (P.length) console.log(`    ${(b / 10).toFixed(1)}–${((b + 1) / 10).toFixed(1)}    ${String(P.length).padStart(5)}   ${f2(mean(P.map((p) => p[0]))).padStart(14)}   ${f2(mean(P.map((p) => p[1]))).padStart(11)}`);
  }
}

for (const kind of ["dict", "cloze"]) {
  const A = D.answers.filter((a) => a.kind === kind && a.rs != null && (!exact || !a.approx));
  if (!A.length) continue;
  console.log(`\n${kind === "dict" ? "Dictation" : "Gaps"} (${A.length} fresh answers, ${A.filter((a) => a.approx).length} approximate)`);
  report("the game's predictions", A.filter((a) => a.pred != null).map((a) => [a.pred, a.rs]));
  const rating = R.newRating(), model = R.newModel(), pairs = [];
  for (const a of A) {
    const x = R.featureVector(a.feat, D.stats[kind]);
    pairs.push([R.predict(x, model.w, rating.th), a.rs]);
    R.rateUpdate(rating, model, x, a.rs);
  }
  report("replay from scratch", pairs);
  console.log(`  rating after the replay: ${R.shown(rating.th)} (θ ${rating.th.toFixed(3)})`);
  console.log("  weights (start → learned):", Object.keys(R.RATING.w0).map((k) => `${k} ${R.RATING.w0[k]}→${model.w[k].toFixed(2)}`).join(", "));
}
