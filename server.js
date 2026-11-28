// Spanish listening trainer: tiny dependency-light server.
//   - serves public/ and media/ (with HTTP Range so the audio can seek)
//   - /api/episodes            list of transcribed episodes
//   - /api/saved               saved highlights (JSON file in data/)
//   - /api/explain             Claude explanation of a selected phrase
//   - /api/clip                mp3 clip of a time range (ffmpeg)
//   - /api/anki                add a card to Anki through AnkiConnect
//   - /api/shadow              transcribe a short recording of your voice (local whisper.cpp)
import http from "node:http";
import fs from "node:fs";
import fsp from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import { makeAuth, COOKIE } from "./auth.js";

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const PORT = Number(process.env.PORT || 8790);
const HOST = process.env.HOST || "127.0.0.1";
const MEDIA_DIR = process.env.MEDIA_DIR || path.join(ROOT, "media");
const DATA_DIR = process.env.DATA_DIR || path.join(ROOT, "data");
const PUBLIC_DIR = path.join(ROOT, "public");
const ANKI_URL = process.env.ANKI_URL || "http://127.0.0.1:8765";
const ANKI_DECK = process.env.ANKI_DECK || "Spanish Listening";
const MODEL = process.env.CLAUDE_MODEL || "claude-opus-5-5";
const CLAUDE_BIN = process.env.CLAUDE_BIN || "claude";
// ONLINE=1: the hosted version for other learners. Everyone logs in, their game is saved on
// the server, and only the game is served: nothing that needs Anki, whisper.cpp or Claude.
const ONLINE = process.env.ONLINE === "1";
const BASE_PATH = process.env.BASE_PATH || "/"; // where nginx mounts the app, for the cookie
const LANG = process.env.LEARN_LANG || "es"; // the language being learned
// offline there is one player, the owner of this copy (and of everything in media/)
const LOCAL_USER = process.env.LOCAL_USER || "jbro";

fs.mkdirSync(DATA_DIR, { recursive: true });
const SAVED_FILE = path.join(DATA_DIR, "saved.json");
const LOOKUPS_FILE = path.join(DATA_DIR, "explanations.json");
const auth = ONLINE ? makeAuth(DATA_DIR) : null;
// online, the only API the game may use; the rest needs things that live on the owner's computer
const ONLINE_API = new Set(["/api/episodes", "/api/config", "/api/state", "/api/login", "/api/logout", "/api/lines", "/api/wordfreq"]);
// pages anyone may load before logging in
const OPEN_FILES = new Set(["/login.html", "/favicon.png", "/apple-touch-icon.png"]);

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".mp3": "audio/mpeg",
  ".m4a": "audio/mp4",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".txt": "text/plain; charset=utf-8",
};

// ---------- helpers ----------
function send(res, status, body, headers = {}) {
  const isObj = typeof body === "object" && !Buffer.isBuffer(body);
  res.writeHead(status, {
    "Content-Type": isObj ? MIME[".json"] : "text/plain; charset=utf-8",
    ...headers,
  });
  res.end(isObj ? JSON.stringify(body) : body);
}

async function readBody(req, limit = 1e6) {
  let size = 0;
  const chunks = [];
  for await (const c of req) {
    size += c.length;
    if (size > limit) throw Object.assign(new Error("body too large"), { status: 413 });
    chunks.push(c);
  }
  const raw = Buffer.concat(chunks).toString("utf8");
  return raw ? JSON.parse(raw) : {};
}

// The line log (rpg main.js lineLog): every line the game shows and every answer to it, one JSON object
// per line of data/lines.jsonl (online: data/lines/<user>.jsonl). POST appends a batch; GET downloads it.
const linesFile = (user) => (user ? path.join(DATA_DIR, "lines", `${String(user).replace(/[^\w-]/g, "_")}.jsonl`) : path.join(DATA_DIR, "lines.jsonl"));
async function handleLines(req, res, user) {
  const file = linesFile(user);
  if (req.method === "GET") {
    const body = await fsp.readFile(file, "utf8").catch(() => "");
    return send(res, 200, body, { "Content-Type": "application/x-ndjson; charset=utf-8", "Content-Disposition": `attachment; filename="leyendas-frases.jsonl"` });
  }
  if (req.method !== "POST") return send(res, 405, { error: "GET or POST" });
  const b = await readBody(req, 2e6);
  const events = Array.isArray(b?.events) ? b.events.slice(0, 2000) : null;
  if (!events) return send(res, 400, { error: "events required" });
  const lines = events.filter((e) => e && typeof e === "object" && !Array.isArray(e)).map((e) => JSON.stringify(e)).filter((l) => l.length < 8000);
  await fsp.mkdir(path.dirname(file), { recursive: true });
  if (lines.length) await fsp.appendFile(file, lines.join("\n") + "\n");
  return send(res, 200, { ok: true, n: lines.length });
}

// Resolve a path inside a base directory, refusing traversal.
function safeJoin(base, rel) {
  const p = path.resolve(base, "." + path.sep + rel);
  return p === base || p.startsWith(base + path.sep) ? p : null;
}

async function serveFile(req, res, file) {
  let st;
  try {
    st = await fsp.stat(file);
    if (!st.isFile()) throw new Error();
  } catch {
    return send(res, 404, "not found");
  }
  const type = MIME[path.extname(file)] || "application/octet-stream";
  const range = req.headers.range && /^bytes=(\d*)-(\d*)$/.exec(req.headers.range);
  if (range) {
    let start = range[1] ? Number(range[1]) : st.size - Number(range[2]);
    let end = range[1] && range[2] ? Number(range[2]) : st.size - 1;
    end = Math.min(end, st.size - 1);
    if (start > end || start < 0) {
      return send(res, 416, "bad range", { "Content-Range": `bytes */${st.size}` });
    }
    res.writeHead(206, {
      "Content-Type": type,
      "Content-Length": end - start + 1,
      "Content-Range": `bytes ${start}-${end}/${st.size}`,
      "Accept-Ranges": "bytes",
    });
    return fs.createReadStream(file, { start, end }).pipe(res);
  }
  res.writeHead(200, {
    "Content-Type": type,
    "Content-Length": st.size,
    "Accept-Ranges": "bytes",
    "Cache-Control": type.startsWith("audio") ? "private, max-age=86400" : "no-cache",
  });
  fs.createReadStream(file).pipe(res);
}

// ---------- word frequency, for the listening rating (public/rpg/rating.js) ----------
// Every word of every Spanish transcript, counted, and the mean and SD of each line feature over all their
// lines, computed once and cached in data/wordfreq.json until an episode is added or changed.
// Not counted: English transcripts (an id ending -en, or a lang other than es) and generated courses.
const RATING_MOD = import("./public/rpg/rating.js");
let wordfreqMem = null;
async function wordfreq() {
  const R = await RATING_MOD;
  const ts = [], sig = [];
  for (const id of (await fsp.readdir(MEDIA_DIR).catch(() => [])).sort()) {
    const f = path.join(MEDIA_DIR, id, "transcript.json");
    const st = await fsp.stat(f).catch(() => null);
    if (!st) continue;
    sig.push(`${id}:${Math.round(st.mtimeMs)}`);
    if (/-en$/.test(id)) continue;
    try {
      const t = JSON.parse(await fsp.readFile(f, "utf8"));
      if (t.source === "course" || (t.lang && t.lang !== "es")) continue;
      ts.push({ id, segments: t.segments, names: t.names });
    } catch { /* not readable yet */ }
  }
  const key = sig.join("|");
  if (wordfreqMem?.sig === key) return wordfreqMem;
  const file = path.join(DATA_DIR, "wordfreq.json");
  const cached = JSON.parse(await fsp.readFile(file, "utf8").catch(() => "null"));
  if (cached?.sig === key) return (wordfreqMem = cached);
  const freq = R.countWords(ts);
  const out = { sig: key, eps: ts.map((t) => t.id), total: freq.total, counts: freq.counts, stats: R.featureStats(ts, freq) };
  await fsp.mkdir(DATA_DIR, { recursive: true });
  await fsp.writeFile(file, JSON.stringify(out));
  return (wordfreqMem = out);
}

// ---------- episodes ----------
async function listEpisodes() {
  const out = [];
  for (const id of await fsp.readdir(MEDIA_DIR).catch(() => [])) {
    const f = path.join(MEDIA_DIR, id, "transcript.json");
    try {
      const t = JSON.parse(await fsp.readFile(f, "utf8"));
      out.push({ id, title: t.title, show: t.show || "", duration: t.duration, source: t.source, lines: t.segments.length });
    } catch {
      /* not transcribed yet */
    }
  }
  return out;
}

// ---------- stored look-ups ----------
// Every explanation Claude gives is kept in data/explanations.json, keyed by the phrase (and the
// question, if any), so looking the same phrase up again is instant and free. `fresh` asks again.
let lookups = null;
let lookupsWrite = Promise.resolve();
const normKey = (s) => String(s || "").toLowerCase().normalize("NFC").replace(/[«»"“”.,;:!?¡¿…—-]+/g, " ").replace(/\s+/g, " ").trim();
const lookupKey = (text, question) => normKey(text) + (question ? " ?? " + normKey(question) : "");
async function loadLookups() {
  if (lookups) return lookups;
  try {
    lookups = JSON.parse(await fsp.readFile(LOOKUPS_FILE, "utf8"));
  } catch {
    // first run: start from the explanations already attached to saved highlights
    lookups = {};
    for (const it of await loadSaved()) {
      if (it.text && it.explanation) lookups[lookupKey(it.text)] = { text: it.text, explanation: it.explanation, at: it.created || Date.now() };
    }
    await writeLookups();
  }
  return lookups;
}
function writeLookups() {
  lookupsWrite = lookupsWrite.then(async () => {
    const tmp = LOOKUPS_FILE + ".tmp";
    await fsp.writeFile(tmp, JSON.stringify(lookups, null, 1));
    await fsp.rename(tmp, LOOKUPS_FILE);
  });
  return lookupsWrite;
}
async function explainStored({ text, context, question, fresh }) {
  const all = await loadLookups();
  const key = lookupKey(text, question);
  if (!fresh && all[key]) return { explanation: all[key].explanation, cached: true, at: all[key].at };
  const explanation = await explain({ text, context, question });
  all[key] = { text, question: question || undefined, context, explanation, at: Date.now() };
  await writeLookups();
  return { explanation, cached: false };
}

// ---------- saved items ----------
async function loadSaved() {
  try {
    return JSON.parse(await fsp.readFile(SAVED_FILE, "utf8"));
  } catch {
    return [];
  }
}
async function writeSaved(items) {
  const tmp = SAVED_FILE + ".tmp";
  await fsp.writeFile(tmp, JSON.stringify(items, null, 2));
  await fsp.rename(tmp, SAVED_FILE);
}

// ---------- audio clips ----------
function clipMp3(episode, start, end) {
  return new Promise((resolve, reject) => {
    const src = safeJoin(MEDIA_DIR, path.join(episode, "audio.mp3"));
    if (!src || !fs.existsSync(src)) return reject(new Error("no such episode"));
    const s = Math.max(0, Number(start) - 0.15);
    const dur = Math.min(60, Number(end) - s + 0.3);
    if (!(dur > 0)) return reject(new Error("bad range"));
    const ff = spawn("ffmpeg", [
      "-loglevel", "error", "-ss", s.toFixed(2), "-t", dur.toFixed(2), "-i", src,
      "-ac", "1", "-b:a", "64k", "-f", "mp3", "pipe:1",
    ]);
    const chunks = [];
    ff.stdout.on("data", (c) => chunks.push(c));
    ff.on("error", reject);
    ff.on("close", (code) =>
      code === 0 ? resolve(Buffer.concat(chunks)) : reject(new Error("ffmpeg failed")),
    );
  });
}

// ---------- Anki (AnkiConnect add-on, code 2055492159) ----------
function escHtml(s) {
  return s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
}
// Minimal Markdown for the card back: paragraphs, lists, **bold**, *italic*.
function mdToHtml(src) {
  const inline = (s) =>
    escHtml(s).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").replace(/(^|[^*])\*([^*]+)\*/g, "$1<i>$2</i>");
  const out = [];
  let list = null;
  for (const raw of src.split("\n")) {
    const line = raw.trim();
    const m = /^([-*]|\d+\.)\s+(.*)$/.exec(line);
    if (m) {
      const tag = /\d/.test(m[1]) ? "ol" : "ul";
      if (list !== tag) { if (list) out.push(`</${list}>`); out.push(`<${tag}>`); list = tag; }
      out.push(`<li>${inline(m[2])}</li>`);
      continue;
    }
    if (list) { out.push(`</${list}>`); list = null; }
    if (line) out.push(`<p>${inline(line.replace(/^#+\s*/, ""))}</p>`);
  }
  if (list) out.push(`</${list}>`);
  return out.join("");
}

async function anki(action, params = {}) {
  const r = await fetch(ANKI_URL, {
    method: "POST",
    body: JSON.stringify({ action, version: 6, params }),
    signal: AbortSignal.timeout(8000),
  });
  const j = await r.json();
  if (j.error) throw new Error(j.error);
  return j.result;
}

// ---------- Anki review (the game's Repaso) ----------
// The only decks the game may read or answer: data/review-decks.json if there is one (a list like the
// default below; kind "dictation" cards are dictated, "recall" cards are recalled and self-graded, with
// "script": "latin" for cards not in Tibetan script), else just Spanish Listening. Only the review
// schedule changes; note text is never touched.
const DEFAULT_DECKS = [
  { id: "spanish", name: "Spanish Listening", deck: "Spanish Listening", kind: "dictation", query: '"deck:Spanish Listening" tag:listening' },
];
const REVIEW_DECKS = (() => {
  try { return JSON.parse(fs.readFileSync(path.join(DATA_DIR, "review-decks.json"), "utf8")); } catch { return DEFAULT_DECKS; }
})();
const ALL_REVIEW = "(" + REVIEW_DECKS.map((d) => `(${d.query})`).join(" OR ") + ")";
const soundOf = (html) => /\[sound:([^\]]+)\]/.exec(html || "")?.[1] || null;
const stripTags = (html) => String(html || "").replace(/<br\s*\/?>/gi, " ").replace(/<[^>]+>/g, " ").replace(/&nbsp;/g, " ")
  .replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/\s+/g, " ").trim();

// Anki's own three numbers for each deck (new today within its limit, learning, to review),
// as on Anki's deck list.
async function deckStats() {
  const st = Object.values(await anki("getDeckStats", { decks: REVIEW_DECKS.map((d) => d.deck) }));
  return Object.fromEntries(REVIEW_DECKS.map((d) => {
    const x = st.find((s) => s.name === d.deck.split("::").pop()) || {};
    return [d.id, { new: x.new_count || 0, learn: x.learn_count || 0, review: x.review_count || 0 }];
  }));
}
async function reviewDecks() {
  const counts = await deckStats();
  return REVIEW_DECKS.map((d) => ({ id: d.id, name: d.name, kind: d.kind, counts: counts[d.id], due: counts[d.id].new + counts[d.id].learn + counts[d.id].review }));
}
// Anki's own next intervals for Again/Hard/Good/Easy ("<10m", "1d", ...), as on its answer buttons
const nextOf = (c) => (c?.nextReviews || []).map((x) => String(x).replace(/[\u2066-\u2069]/g, ""));
// what a card counts as right now: learning (queue 1, or 3 = learning across days), review, or new
const catOf = (c) => (c.queue === 1 || c.queue === 3 ? "learn" : c.queue === 2 ? "review" : "new");
// Due cards of the chosen decks, one entry per note (its twin cards are answered together).
async function reviewCards(ids) {
  const out = [];
  const counts = await deckStats();
  for (const d of REVIEW_DECKS.filter((x) => ids.includes(x.id))) {
    // due learning and review cards, plus today's new cards (as many as the deck's daily limit leaves)
    const due = await anki("findCards", { query: `${d.query} is:due` });
    const dueInfo = due.length ? await anki("cardsInfo", { cards: due }) : [];
    let newInfo = [];
    if (counts[d.id].new) {
      const fresh = await anki("findCards", { query: `${d.query} is:new -is:suspended -is:buried` });
      if (fresh.length) newInfo = (await anki("cardsInfo", { cards: fresh })).sort((a, b) => a.due - b.due).slice(0, counts[d.id].new);
    }
    const info = [...dueInfo, ...newInfo];
    if (!info.length) continue;
    const notes = [...new Set(info.map((c) => c.note))];
    // all cards of those notes that belong to this deck, so twins get the same answer
    const twins = await anki("findCards", { query: `${d.query} nid:${notes.join(",")}` });
    const twinInfo = await anki("cardsInfo", { cards: twins });
    for (const nid of notes) {
      const c = info.find((x) => x.note === nid), f = c.fields;
      const mine = twinInfo.filter((x) => x.note === nid);
      // lapses: how often you've forgotten it (the worst of the twins); the game makes leeches into named monsters
      // n: how many of its cards are in today's study, by kind, so the counts match Anki's
      const n = { new: 0, learn: 0, review: 0 };
      for (const x of info.filter((x) => x.note === nid)) n[catOf(x)]++;
      const card = { deck: d.id, deckName: d.name, kind: d.kind, note: nid, cards: mine.map((x) => x.cardId), lapses: Math.max(0, ...mine.map((x) => x.lapses || 0)),
        n, cat: n.learn ? "learn" : n.review ? "review" : "new", next: nextOf(c) };
      if (d.kind === "dictation") {
        const back = f.Back?.value || "";
        const [head, ...rest] = back.split(/<hr\s*\/?>/i);
        Object.assign(card, { audio: soundOf(f.Front?.value) || soundOf(back), text: stripTags(head), back: rest.join("<hr>") });
      } else if (f.Pregunta) {
        Object.assign(card, { script: d.script, front: f.Pregunta.value, back: f.Respuesta?.value || "", notes: f.Extra?.value || "" });
      } else if (f.Texto) {
        // cloze: every gap hidden on the front (a note's cards are answered together), shown in blue on the back
        const t = f.Texto.value, CL = /\{\{c\d+::(.*?)(?:::(.*?))?\}\}/g;
        Object.assign(card, { script: d.script, front: t.replace(CL, (_, a, hint) => `<b>[${hint || "…"}]</b>`),
          back: t.replace(CL, (_, a) => `<span style="color:blue">${a}</span>`), notes: f.Extra?.value || "" });
      } else {
        Object.assign(card, { script: d.script, audio: soundOf(f.Audio?.value), front: f.Expression?.value || "", back: f.Definitions?.value || "", notes: f.Notes?.value || "" });
      }
      if (card.audio || d.kind === "recall") out.push(card);
    }
  }
  return out;
}
async function reviewAnswer(cards, ease) {
  cards = [...new Set((cards || []).map(Number))].filter(Number.isInteger);
  ease = Number(ease);
  if (!cards.length || ![1, 2, 3, 4].includes(ease)) throw Object.assign(new Error("cards and ease 1-4 required"), { status: 400 });
  // refuse anything outside the review decks
  const ok = await anki("findCards", { query: `cid:${cards.join(",")} ${ALL_REVIEW}` });
  if (ok.length !== cards.length) throw Object.assign(new Error("those cards aren't in the review decks"), { status: 403 });
  const result = await anki("answerCards", { answers: cards.map((cardId) => ({ cardId, ease })) });
  // where Anki put them: still in today's learning steps (queue 1, due in epoch seconds) means the
  // card comes back this session, as in Anki (Again on a review: 10 min, then Good: graduates)
  const after = await anki("cardsInfo", { cards });
  const learning = after.filter((c) => c.queue === 1);
  const first = learning.reduce((a, c) => (!a || c.due < a.due ? c : a), null);
  return { result, again: first ? { due: first.due * 1000, n: learning.length, next: nextOf(first) } : null };
}

// ---------- shadowing: your voice -> text, with a local whisper.cpp server ----------
// whisper-server keeps the model loaded, so a few seconds of speech come back in well under a second.
// Started on the first request; nothing leaves the machine.
const WHISPER_BIN = process.env.WHISPER_SERVER_BIN || "whisper-server";
const WHISPER_MODEL = process.env.WHISPER_MODEL || path.join(ROOT, "models", "ggml-large-v3.bin");
const WHISPER_PORT = Number(process.env.WHISPER_PORT || 8791);
let whisperProc = null, whisperReady = null;
function whisperUp() {
  if (whisperReady) return whisperReady;
  if (!fs.existsSync(WHISPER_MODEL)) return Promise.reject(Object.assign(new Error(`No whisper model at ${WHISPER_MODEL}`), { status: 503 }));
  whisperProc = spawn(WHISPER_BIN, ["-m", WHISPER_MODEL, "-l", "es", "-nt", "--host", "127.0.0.1", "--port", String(WHISPER_PORT)], { stdio: "ignore" });
  whisperProc.on("exit", () => { whisperProc = null; whisperReady = null; });
  whisperProc.on("error", () => { whisperProc = null; whisperReady = null; });
  whisperReady = (async () => {
    for (let i = 0; i < 120; i++) {
      try { await fetch(`http://127.0.0.1:${WHISPER_PORT}/`); return; } catch {}
      if (!whisperProc) break;
      await new Promise((r) => setTimeout(r, 500));
    }
    whisperReady = null;
    throw Object.assign(new Error("The speech recogniser (whisper-server) didn't start."), { status: 503 });
  })();
  return whisperReady;
}
for (const sig of ["exit", "SIGINT", "SIGTERM"]) process.on(sig, () => { whisperProc?.kill(); if (sig !== "exit") process.exit(0); });

async function readRaw(req, limit) {
  let size = 0;
  const chunks = [];
  for await (const c of req) {
    size += c.length;
    if (size > limit) throw Object.assign(new Error("recording too long"), { status: 413 });
    chunks.push(c);
  }
  return Buffer.concat(chunks);
}
// Browser recording (webm/ogg/mp4) -> 16 kHz mono wav, through ffmpeg's pipes.
function toWav(buf) {
  return new Promise((resolve, reject) => {
    const ff = spawn("ffmpeg", ["-loglevel", "error", "-i", "pipe:0", "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", "-f", "wav", "pipe:1"]);
    const out = [];
    let err = "";
    ff.stdout.on("data", (d) => out.push(d));
    ff.stderr.on("data", (d) => (err += d));
    ff.on("error", reject);
    ff.on("close", (code) => (code === 0 ? resolve(Buffer.concat(out)) : reject(new Error(`ffmpeg: ${err.trim() || code}`))));
    ff.stdin.on("error", () => {});
    ff.stdin.end(buf);
  });
}
async function transcribeVoice(buf) {
  await whisperUp();
  const wav = await toWav(buf);
  const form = new FormData();
  form.append("file", new Blob([wav], { type: "audio/wav" }), "voice.wav");
  form.append("response_format", "json");
  form.append("temperature", "0");
  const r = await fetch(`http://127.0.0.1:${WHISPER_PORT}/inference`, { method: "POST", body: form });
  if (!r.ok) throw new Error(`whisper-server: ${r.status}`);
  const j = await r.json();
  // whisper marks silence and noise as [música], (risas), etc.
  return String(j.text || "").replace(/\[[^\]]*\]|\([^)]*\)/g, " ").replace(/\s+/g, " ").trim();
}

// ---------- Claude ----------
let client = null;
async function claude() {
  // loaded on first use, so the online version runs without the SDK installed
  if (!client) { const { default: Anthropic } = await import("@anthropic-ai/sdk"); client = new Anthropic(); } // ANTHROPIC_API_KEY from the environment
  return client;
}

const EXPLAIN_SYSTEM = `You help an advanced learner of Spanish who already knows most vocabulary and grammar and is training listening comprehension with native-speed, informal Colombian audio (talk shows, interviews, podcasts, TV series).

The learner highlights a phrase from a transcript and you get it with surrounding context. Your answer also goes on the back of a flashcard. Reply in English, in Markdown, in exactly this shape:

- *spanish part* — **short meaning** · detail
- *next part* — **short meaning** · detail

*Whole thing:* a natural English rendering of the highlighted phrase as used here.

Rules:
- Split the phrase into its meaningful parts, in order: single words, or chunks that work as a unit (idioms, set phrases, verb + clitics, "pa' que"). Skip parts that need no explanation for an advanced learner (articles, "y", "que" used plainly) unless they're part of a chunk; a short phrase may be just one part.
- **short meaning** is one word or a couple of words, bold, giving what the part means in this sentence (not the dictionary's first sense).
- After " · ", the detail: register and region (say if Colombian/regional or slang), literal vs. idiomatic sense, non-obvious grammar, or how it sounds in fast speech (dropped s/d, "pa'", run-together words). One short sentence; leave the " · detail" off if there's nothing worth adding.
- Leave out the *Whole thing:* line when there's only one part and its short meaning already says it.
- If the transcript looks like a mis-transcription, add a last line: *Maybe misheard:* what was likely said.

If the message includes "My question:", answer that question directly and briefly instead of using the shape above.

No preamble, no headings. Keep it under ~150 words unless the phrase genuinely needs more.`;

// Without an API key, go through the local Claude Code CLI in non-interactive
// mode, which uses whoever is logged in to Claude Code (e.g. a Pro/Max plan).
function explainViaClaudeCode(user, system = EXPLAIN_SYSTEM) {
  return new Promise((resolve, reject) => {
    const cp = spawn(
      CLAUDE_BIN,
      [
        "-p", "--output-format", "json",
        "--system-prompt", system,
        "--tools", "", "--strict-mcp-config", "--no-session-persistence",
        "--model", MODEL, "--effort", "low",
      ],
      { cwd: os.tmpdir(), stdio: ["pipe", "pipe", "pipe"] },
    );
    let out = "", err = "";
    const timer = setTimeout(() => cp.kill(), 120000);
    cp.stdout.on("data", (c) => (out += c));
    cp.stderr.on("data", (c) => (err += c));
    cp.on("error", (e) =>
      reject(new Error(e.code === "ENOENT" ? "Claude Code isn't installed, and no ANTHROPIC_API_KEY is set." : e.message)),
    );
    cp.on("close", () => {
      clearTimeout(timer);
      try {
        const r = JSON.parse(out);
        if (r.is_error) return reject(new Error(r.result || "Claude Code returned an error. Is it logged in?"));
        resolve(String(r.result || "").trim());
      } catch {
        reject(new Error((err || out).trim().slice(0, 300) || "Claude Code gave no answer. Run `claude` once to log in."));
      }
    });
    cp.stdin.end(user);
  });
}

async function explain({ text, context, question }) {
  const user =
    `Context (transcript excerpt):\n"""\n${context || text}\n"""\n\n` +
    `Highlighted phrase: «${text}»` +
    (question ? `\n\nMy question: ${question}` : "");
  return askClaude(EXPLAIN_SYSTEM, user);
}

// La encrucijada: Claude's second opinion on a translation, mood first.
const SUBJ_SYSTEM = `You check a translation exercise for an advanced learner of Spanish (Colombian Spanish is the target; "plata", "tú" or "usted" are all fine). The learner got an English sentence and wrote it in Spanish; the point of the exercise is choosing subjunctive or indicative in the subordinate clause.

Reply in Spanish, in Markdown, briefly (under ~90 words), in exactly this shape:
- **Modo:** whether their mood choice is right, and the reason in one short sentence (what triggers it).
- **Tu frase:** whether it is correct and natural. If not, the corrected sentence in *italics*, and what was wrong (spelling, accents, word choice, other grammar), one short sentence.
- Only if useful, one line **Ojo:** with a nuance (e.g. both moods possible, with the difference in meaning).

No preamble. Don't repeat the English. Accept any natural translation, not just the reference.`;
async function subjReview({ en, es, typed, mood }) {
  const user = `English: ${en}\nReference translation (${mood === "s" ? "subjunctive" : "indicative"}): ${es}\nLearner wrote: ${typed}`;
  return askClaude(SUBJ_SYSTEM, user);
}

async function askClaude(system, user) {
  if (!process.env.ANTHROPIC_API_KEY && !process.env.ANTHROPIC_AUTH_TOKEN) {
    return explainViaClaudeCode(user, system);
  }
  const resp = await (await claude()).beta.messages.create({
    model: MODEL,
    max_tokens: 4000,
    thinking: { type: "adaptive" },
    output_config: { effort: "low" },
    betas: ["server-side-fallback-2026-07-01"],
    fallbacks: "default",
    system,
    messages: [{ role: "user", content: user }],
  });
  if (resp.stop_reason === "refusal") {
    throw new Error("Claude declined to answer this one.");
  }
  return resp.content
    .filter((b) => b.type === "text")
    .map((b) => b.text)
    .join("\n")
    .trim();
}

// ---------- router ----------
const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, "http://x");
  let p = decodeURIComponent(url.pathname);
  try {
    if (p === "/api/config" && req.method === "GET") {
      const u = ONLINE ? auth.user(req) : { id: LOCAL_USER, name: LOCAL_USER };
      return send(res, 200, { online: ONLINE, lang: LANG, user: u ? { id: u.id, name: u.name } : null });
    }
    if (ONLINE) {
      if (p === "/api/login" && req.method === "POST") {
        const b = await readBody(req, 4000);
        const ip = req.headers["x-real-ip"] || req.socket.remoteAddress;
        const r = auth.login(b.user, b.pass, ip);
        if (r.error) return send(res, r.status, { error: r.error });
        return send(res, 200, { user: r.user }, {
          "Set-Cookie": `${COOKIE}=${r.token}; Path=${BASE_PATH}; Max-Age=${180 * 86400}; HttpOnly; Secure; SameSite=Lax`,
        });
      }
      if (OPEN_FILES.has(p)) return serveFile(req, res, path.join(PUBLIC_DIR, p.slice(1)));
      const user = auth.user(req);
      if (!user) {
        if (p.startsWith("/api/")) return send(res, 401, { error: "Inicia sesión" });
        if (p === "/" || p.endsWith(".html")) return send(res, 302, "", { Location: "login.html" });
        return send(res, 401, "log in first");
      }
      if (p === "/api/logout" && req.method === "POST") {
        auth.logout(user.token);
        return send(res, 200, { ok: true }, { "Set-Cookie": `${COOKIE}=; Path=${BASE_PATH}; Max-Age=0; HttpOnly; Secure; SameSite=Lax` });
      }
      if (p === "/api/state") {
        if (req.method === "GET") return send(res, 200, await auth.getState(user.id));
        if (req.method === "PUT") {
          const b = await readBody(req, 5e6);
          if (!b || typeof b !== "object" || Array.isArray(b)) return send(res, 400, { error: "bad state" });
          await auth.putState(user.id, b);
          return send(res, 200, { ok: true });
        }
      }
      if (p === "/api/lines") return handleLines(req, res, user.id);
      if (p.startsWith("/api/") && !ONLINE_API.has(p)) return send(res, 404, { error: "No disponible en la versión en línea" });
      // only the game: the listening and dictation pages need the owner's tools
      if (p === "/" || (p.endsWith(".html") && p !== "/rpg.html")) return send(res, 302, "", { Location: "rpg.html" });
    }
    if (p === "/api/lines") return handleLines(req, res, null);
    if (p === "/api/wordfreq" && req.method === "GET") return send(res, 200, await wordfreq());
    if (p === "/api/episodes" && req.method === "GET") {
      return send(res, 200, await listEpisodes());
    }

    // Fix a transcript line: replace its text, spread word timings by length.
    const segEdit = /^\/api\/episodes\/([\w-]+)\/segments\/(\d+)$/.exec(p);
    if (segEdit && req.method === "PUT") {
      const file = safeJoin(MEDIA_DIR, path.join(segEdit[1], "transcript.json"));
      const t = JSON.parse(await fsp.readFile(file, "utf8"));
      const seg = t.segments[Number(segEdit[2])];
      if (!seg) return send(res, 404, { error: "no such segment" });
      const text = String((await readBody(req)).text || "").replace(/\s+/g, " ").trim();
      if (!text) return send(res, 400, { error: "text required" });
      const toks = text.split(" ");
      const total = toks.reduce((n, w) => n + w.length + 1, 0);
      let at = seg.start;
      seg.words = toks.map((w) => {
        const d = ((w.length + 1) / total) * (seg.end - seg.start);
        const word = { w, s: +at.toFixed(2), e: +(at + d).toFixed(2) };
        at += d;
        return word;
      });
      seg.text = text;
      seg.edited = true;
      delete seg.flagged; // fixed
      const backup = file.replace(/\.json$/, ".orig.json");
      if (!fs.existsSync(backup)) await fsp.copyFile(file, backup);
      await fsp.writeFile(file + ".tmp", JSON.stringify(t));
      await fsp.rename(file + ".tmp", file);
      return send(res, 200, seg);
    }

    // Flag a line whose text doesn't match the audio (wrong words or wrong timing).
    // Flagged lines are left out of the games until someone fixes them.
    const segFlag = /^\/api\/episodes\/([\w-]+)\/segments\/(\d+)\/flag$/.exec(p);
    if (segFlag && req.method === "POST") {
      const file = safeJoin(MEDIA_DIR, path.join(segFlag[1], "transcript.json"));
      const t = JSON.parse(await fsp.readFile(file, "utf8"));
      const seg = t.segments[Number(segFlag[2])];
      if (!seg) return send(res, 404, { error: "no such segment" });
      const b = await readBody(req);
      if (b.flagged === false) delete seg.flagged;
      else seg.flagged = true;
      const backup = file.replace(/\.json$/, ".orig.json");
      if (!fs.existsSync(backup)) await fsp.copyFile(file, backup);
      await fsp.writeFile(file + ".tmp", JSON.stringify(t));
      await fsp.rename(file + ".tmp", file);
      return send(res, 200, seg);
    }

    if (p === "/api/saved") {
      if (req.method === "GET") {
        const ep = url.searchParams.get("episode");
        const all = await loadSaved();
        return send(res, 200, ep ? all.filter((s) => s.episode === ep) : all);
      }
      if (req.method === "POST") {
        const b = await readBody(req);
        const all = await loadSaved();
        const item = {
          id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
          episode: String(b.episode || ""),
          start: Number(b.start),
          end: Number(b.end),
          text: String(b.text || "").slice(0, 2000),
          note: String(b.note || "").slice(0, 5000),
          explanation: String(b.explanation || "").slice(0, 10000),
          kind: b.kind === "hard" ? "hard" : "saved",
          created: new Date().toISOString(),
        };
        all.push(item);
        await writeSaved(all);
        return send(res, 200, item);
      }
    }
    const savedMatch = /^\/api\/saved\/([\w-]+)$/.exec(p);
    if (savedMatch) {
      const all = await loadSaved();
      const i = all.findIndex((s) => s.id === savedMatch[1]);
      if (i < 0) return send(res, 404, { error: "not found" });
      if (req.method === "DELETE") {
        all.splice(i, 1);
        await writeSaved(all);
        return send(res, 200, { ok: true });
      }
      if (req.method === "PATCH") {
        const b = await readBody(req);
        for (const k of ["note", "explanation", "ankiNoteId"]) if (k in b) all[i][k] = b[k];
        await writeSaved(all);
        return send(res, 200, all[i]);
      }
    }

    if (p === "/api/explain" && req.method === "POST") {
      const b = await readBody(req);
      if (!b.text) return send(res, 400, { error: "text required" });
      return send(res, 200, await explainStored(b));
    }

    if (p === "/api/clip" && req.method === "GET") {
      const q = url.searchParams;
      const buf = await clipMp3(q.get("episode"), q.get("start"), q.get("end"));
      return send(res, 200, buf, {
        "Content-Type": "audio/mpeg",
        "Content-Disposition": `attachment; filename="clip.mp3"`,
      });
    }

    if (p === "/api/review/decks" && req.method === "GET") {
      return send(res, 200, await reviewDecks());
    }
    if (p === "/api/review/cards" && req.method === "GET") {
      return send(res, 200, await reviewCards(String(url.searchParams.get("decks") || "").split(",")));
    }
    if (p === "/api/review/media" && req.method === "GET") {
      const file = String(url.searchParams.get("file") || "");
      if (!/^[^/\\]+\.(mp3|ogg|wav|m4a|png|jpe?g|gif|webp)$/i.test(file)) return send(res, 400, { error: "bad file" });
      const b64 = await anki("retrieveMediaFile", { filename: file });
      if (!b64) return send(res, 404, { error: "not in Anki's media" });
      const type = { mp3: "audio/mpeg", ogg: "audio/ogg", wav: "audio/wav", m4a: "audio/mp4", png: "image/png", jpg: "image/jpeg", jpeg: "image/jpeg", gif: "image/gif", webp: "image/webp" }[file.split(".").pop().toLowerCase()];
      return send(res, 200, Buffer.from(b64, "base64"), { "Content-Type": type, "Cache-Control": "private, max-age=86400" });
    }
    if (p === "/api/review/answer" && req.method === "POST") {
      const b = await readBody(req);
      return send(res, 200, await reviewAnswer(b.cards, b.ease));
    }

    if (p === "/api/subj/review" && req.method === "POST") {
      const b = await readBody(req);
      const f = (k) => String(b[k] || "").slice(0, 400).trim();
      if (!f("en") || !f("typed")) return send(res, 400, { error: "en and typed required" });
      return send(res, 200, { review: await subjReview({ en: f("en"), es: f("es"), typed: f("typed"), mood: f("mood") }) });
    }
    if (p === "/api/shadow/warm" && req.method === "POST") {
      whisperUp().catch((e) => console.error(e.message));
      return send(res, 200, { ok: true });
    }
    if (p === "/api/shadow" && req.method === "POST") {
      const buf = await readRaw(req, 8e6);
      if (buf.length < 200) return send(res, 400, { error: "empty recording" });
      return send(res, 200, { text: await transcribeVoice(buf) });
    }

    if (p === "/api/anki" && req.method === "POST") {
      // Every card gets a lookup: reuse the one the client already has, or ask now.
      const b = await readBody(req);
      const text = String(b.text || "").trim();
      if (!text) return send(res, 400, { error: "text required" });
      await anki("version"); // fail fast if Anki is closed, before spending a lookup
      const audio = await clipMp3(b.episode, b.start, b.end);
      // reuse the client's lookup if it's in the card format (a list of parts), otherwise ask again
      const given = String(b.explanation || "").trim();
      const explanation = /^[-*]\s+\*[^*\s]/.test(given) ? given : (await explainStored({ text, context: b.context })).explanation;
      const filename = `sll_${b.episode}_${Math.round(b.start * 1000)}.mp3`;
      await anki("createDeck", { deck: ANKI_DECK });
      const noteId = await anki("addNote", {
        note: {
          deckName: ANKI_DECK,
          modelName: "Basic",
          fields: {
            Front: "",
            Back: `<div style="font-size:1.3em">${escHtml(text)}</div><hr>${mdToHtml(explanation)}`,
          },
          options: { allowDuplicate: false },
          tags: ["listening", b.episode],
          audio: [{ data: audio.toString("base64"), filename, fields: ["Front"] }],
        },
      });
      return send(res, 200, { noteId, explanation });
    }

    // static: media and public
    if (p.startsWith("/media/")) {
      const f = safeJoin(MEDIA_DIR, p.slice("/media/".length));
      return f ? serveFile(req, res, f) : send(res, 404, "not found");
    }
    const f = safeJoin(PUBLIC_DIR, p === "/" ? "index.html" : p.slice(1));
    return f ? serveFile(req, res, f) : send(res, 404, "not found");
  } catch (err) {
    console.error(err);
    const msg =
      err.cause?.code === "ECONNREFUSED" || /fetch failed/.test(err.message)
        ? "Couldn't reach Anki. Is Anki open with the AnkiConnect add-on installed?"
        : err.message;
    return send(res, err.status || 500, { error: msg });
  }
});

server.listen(PORT, HOST, () => console.log(`listening on http://${HOST}:${PORT}/`));
