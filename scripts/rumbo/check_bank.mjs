// Check Rumbo's clip bank (media/rumbo/bank.json) and mark the clips the game must not use.
//   1. Each clip's text states its facts: the numbers in the text are the facts' numbers.
//   2. Whisper heard those numbers too (a voice that misreads a price would teach a wrong answer):
//      a clip whose heard numbers differ is marked "bad" and the game skips it.
//   3. Every event type has rumor clips, at more than one certainty, so any event can be announced
//      and any can be a false rumor.
//   node scripts/rumbo/check_bank.mjs          # report, and write the marks into bank.json
import fs from "fs";
import { numbersIn, norm, parseNumber } from "../../public/listen-core.js";
import { EVENTS } from "../../public/rumbo/data.js";

const FILE = new URL("../../media/rumbo/bank.json", import.meta.url).pathname;
const bank = JSON.parse(fs.readFileSync(FILE, "utf8"));
const sortN = (a) => [...a].sort((x, y) => x - y).join(",");
const want = (c) => (c.kind === "broadcast" ? Object.values(c.facts.prices) : c.kind === "contract" ? [c.facts.qty, c.facts.deadline, c.facts.pay, c.facts.penalty] : []);
// share of the text's words Whisper heard (in order)
function heardShare(text, heard) {
  // numbers are checked apart (Whisper writes digits for "mil trescientos"): compare the other words
  const toks = (s) => s.split(/\s+/).map(norm).filter((w) => w && !/^\d/.test(w) && parseNumber(w) == null && w !== "y");
  const a = toks(text), b = toks(heard || "");
  const d = Array.from({ length: a.length + 1 }, () => new Array(b.length + 1).fill(0));
  for (let i = 1; i <= a.length; i++) for (let j = 1; j <= b.length; j++) d[i][j] = a[i - 1] === b[j - 1] ? d[i - 1][j - 1] + 1 : Math.max(d[i - 1][j], d[i][j - 1]);
  return a.length ? d[a.length][b.length] / a.length : 1;
}
let bad = 0, low = 0;
for (const c of bank.clips) {
  delete c.bad;
  const said = numbersIn(c.text), heard = numbersIn(c.heard || "");
  if (sortN(said) !== sortN(want(c))) c.bad = `text says ${sortN(said)}, facts ${sortN(want(c))}`;
  else if (sortN(heard) !== sortN(want(c))) c.bad = `Whisper heard ${sortN(heard)}, facts ${sortN(want(c))}`;
  const share = heardShare(c.text, c.heard);
  if (c.bad) { bad++; console.log(`✗ ${c.id}: ${c.bad}\n    text:  ${c.text}\n    heard: ${c.heard}`); }
  else if (share < 0.75) { low++; console.log(`? ${c.id}: Whisper matched only ${Math.round(share * 100)}% of the words\n    text:  ${c.text}\n    heard: ${c.heard}`); }
}
const rumors = bank.clips.filter((c) => c.kind === "rumor" && !c.bad);
const missing = Object.keys(EVENTS).filter((e) => new Set(rumors.filter((c) => c.facts.event === e).map((c) => c.facts.certainty)).size < 2);
if (missing.length) console.log(`events with rumors at fewer than two certainties: ${missing.join(", ")}`);
fs.writeFileSync(FILE, JSON.stringify(bank));
const n = (k) => bank.clips.filter((c) => c.kind === k && !c.bad).length;
console.log(`${bank.clips.length} clips: ${bad} marked bad, ${low} to listen to; usable ${n("broadcast")} broadcasts, ${n("rumor")} rumors, ${n("contract")} contracts`);
process.exitCode = bad || missing.length ? 1 : 0;
