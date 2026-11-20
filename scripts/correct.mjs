// Claude correction pass over review chunks (see review_chunks.py).
//   python3 -I scripts/review_chunks.py prepare media/<id> --chunks 6
//   node scripts/correct.mjs media/<id> [--prompt scripts/correction-prompt-subtitles.md]
// Uses the API if ANTHROPIC_API_KEY is set, otherwise the Claude Code CLI (`claude -p`,
// i.e. whatever account Claude Code is logged in with).
//   python3 -I scripts/review_chunks.py apply media/<id> media/<id>/review/out*.json
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";
import os from "node:os";
import Anthropic from "@anthropic-ai/sdk";

const here = path.dirname(fileURLToPath(import.meta.url));
const dir = process.argv[2];
if (!dir) {
  console.error("usage: node scripts/correct.mjs media/<id>");
  process.exit(1);
}
const reviewDir = path.join(dir, "review");
const pi = process.argv.indexOf("--prompt");
const promptFile = pi > 0 ? process.argv[pi + 1] : path.join(here, "correction-prompt.md");
const system = fs.readFileSync(promptFile, "utf8");
const useApi = !!(process.env.ANTHROPIC_API_KEY || process.env.ANTHROPIC_AUTH_TOKEN);
const chunks = fs.readdirSync(reviewDir).filter((f) => /^chunk\d+\.txt$/.test(f)).sort();
const client = useApi ? new Anthropic() : null;

function parseJson(text) {
  const m = text.match(/\{[\s\S]*\}/);
  if (!m) throw new Error("no JSON object in reply");
  return JSON.parse(m[0]);
}

function viaClaudeCode(input) {
  return new Promise((resolve, reject) => {
    const args = ["-p", "--output-format", "json", "--system-prompt", system, "--tools", "",
      "--strict-mcp-config", "--no-session-persistence", "--model", "claude-opus-5-5", "--effort", "high"];
    const p = spawn(process.env.CLAUDE_BIN || "claude", args, { cwd: os.tmpdir(), stdio: ["pipe", "pipe", "pipe"] });
    let out = "", err = "";
    const timer = setTimeout(() => p.kill(), 30 * 60 * 1000);
    p.stdout.on("data", (d) => (out += d));
    p.stderr.on("data", (d) => (err += d));
    p.on("error", reject);
    p.on("close", (code) => {
      clearTimeout(timer);
      try {
        const r = JSON.parse(out);
        if (r.is_error) return reject(new Error(r.result || "claude -p failed"));
        resolve(r.result);
      } catch {
        reject(new Error(`claude -p exited ${code}: ${(err || out).slice(0, 300)}`));
      }
    });
    p.stdin.end(input);
  });
}

async function correct(file) {
  const out = path.join(reviewDir, file.replace("chunk", "out").replace(".txt", ".json"));
  if (fs.existsSync(out)) return console.log(`${file}: already done`);
  const input = fs.readFileSync(path.join(reviewDir, file), "utf8");
  if (!useApi) {
    const fixes = parseJson(await viaClaudeCode(input));
    fs.writeFileSync(out, JSON.stringify(fixes, null, 1));
    return console.log(`${file}: ${Object.keys(fixes).length} corrections`);
  }
  const stream = client.beta.messages.stream({
    model: "claude-opus-5-5",
    max_tokens: 64000,
    thinking: { type: "adaptive" },
    output_config: { effort: "high" },
    betas: ["server-side-fallback-2026-07-01"],
    fallbacks: "default",
    system,
    messages: [{ role: "user", content: input }],
  });
  const msg = await stream.finalMessage();
  if (msg.stop_reason === "refusal") throw new Error(`${file}: Claude declined`);
  if (msg.stop_reason === "max_tokens") throw new Error(`${file}: reply was cut off`);
  const text = msg.content.filter((b) => b.type === "text").map((b) => b.text).join("");
  const fixes = parseJson(text);
  fs.writeFileSync(out, JSON.stringify(fixes, null, 1));
  console.log(`${file}: ${Object.keys(fixes).length} corrections`);
}

// a few at a time
const queue = [...chunks];
let failed = 0;
await Promise.all(Array.from({ length: 4 }, async () => {
  for (let f; (f = queue.shift()); ) {
    try { await correct(f); } catch (e) { failed++; console.error(`${f}: ${e.message}`); }
  }
}));
if (failed) process.exit(1);
