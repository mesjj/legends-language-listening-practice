// Which words of an episode are parts of non-Spanish proper names (Jerry, Kramer, Puddy, Play Now...):
// a learner can't be expected to spell those from hearing them, so the games don't count them when
// they're wrong (listen-core.js scoreWords, `names`). Spanish names and words (Holanda, María, Dios)
// still count. Writes the list to transcript.json as `names` (tokens as written in the transcript).
//   node scripts/find_names.mjs media/<id> [--force]
// Uses the API if ANTHROPIC_API_KEY is set, otherwise the Claude Code CLI (`claude -p`), like correct.mjs.
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { spawn } from "node:child_process";
import Anthropic from "@anthropic-ai/sdk";

const dir = process.argv[2];
if (!dir) { console.error("usage: node scripts/find_names.mjs media/<id> [--force]"); process.exit(1); }
const file = path.join(dir, "transcript.json");
const T = JSON.parse(fs.readFileSync(file, "utf8"));
if (T.names && !process.argv.includes("--force")) { console.log(`${dir}: already has ${T.names.length} names`); process.exit(0); }

// every capitalised word, with how often it comes and a line or two it comes in
const strip = (w) => w.replace(/^[^\p{L}]+|[^\p{L}]+$/gu, "");
const cand = new Map();
for (const s of T.segments) for (const w of s.words || []) {
  const t = strip(w.w);
  if (!t || !/^\p{Lu}/u.test(t)) continue;
  const c = cand.get(t) || { n: 0, ex: [] };
  c.n++;
  if (c.ex.length < 2 && !c.ex.includes(s.text)) c.ex.push(s.text);
  cand.set(t, c);
}
if (!cand.size) { T.names = []; fs.writeFileSync(file, JSON.stringify(T)); console.log(`${dir}: no candidates`); process.exit(0); }

const system = `You help a Spanish listening trainer. The learner hears a line of a Spanish-language episode and types it. Some words are parts of proper names that are not Spanish (English or other foreign names of people, places, brands, shows: Jerry, Kramer, Puddy, Newman, Play Now, The Wiz, Pottery Barn). A learner can't be expected to spell those from hearing them, so they won't count when wrong.

You get the capitalised words of one episode, each with how often it appears and example lines. Return the ones that are (part of) such a non-Spanish proper name.

Leave out:
- ordinary Spanish words that are only capitalised because they start a sentence (Hola, Bueno, Claro, Qué...)
- Spanish names and Spanish-spelled names a Spanish speaker would write the same way (María, Carlos, José, Dios, Holanda, Bélgica, Nueva York, Señor, Sr)
- foreign words that aren't names

Reply with only a JSON object: {"names": ["Jerry", "Kramer", ...]}, each exactly as written in the list.`;
const input = [...cand].sort((a, b) => b[1].n - a[1].n).map(([w, c]) => `${w} (${c.n}): ${c.ex.join(" | ")}`).join("\n");

function viaCli() {
  return new Promise((resolve, reject) => {
    const args = ["-p", "--output-format", "json", "--system-prompt", system, "--tools", "",
      "--strict-mcp-config", "--no-session-persistence", "--model", "claude-opus-5-5", "--effort", "medium"];
    const p = spawn(process.env.CLAUDE_BIN || "claude", args, { cwd: os.tmpdir(), stdio: ["pipe", "pipe", "pipe"] });
    let out = "", err = "";
    p.stdout.on("data", (d) => (out += d));
    p.stderr.on("data", (d) => (err += d));
    p.on("error", reject);
    p.on("close", (code) => {
      try { const r = JSON.parse(out); if (r.is_error) return reject(new Error(r.result)); resolve(r.result); }
      catch { reject(new Error(`claude -p exited ${code}: ${(err || out).slice(0, 300)}`)); }
    });
    p.stdin.end(input);
  });
}
async function viaApi() {
  const msg = await new Anthropic().messages.stream({
    model: "claude-opus-5-5", max_tokens: 16000, thinking: { type: "adaptive" }, output_config: { effort: "medium" },
    system, messages: [{ role: "user", content: input }],
  }).finalMessage();
  if (msg.stop_reason === "refusal") throw new Error("Claude declined");
  return msg.content.filter((b) => b.type === "text").map((b) => b.text).join("");
}

const text = process.env.ANTHROPIC_API_KEY ? await viaApi() : await viaCli();
const m = text.match(/\{[\s\S]*\}/);
if (!m) throw new Error("no JSON in reply");
const names = [...new Set(JSON.parse(m[0]).names || [])].filter((w) => cand.has(w)).sort();
T.names = names;
fs.writeFileSync(file, JSON.stringify(T));
console.log(`${dir}: ${names.length} names: ${names.join(", ")}`);
