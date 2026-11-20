// Convert whisper.cpp full JSON (-ojf) into the app's transcript.json:
//   { title, source, duration, segments: [{ start, end, text, words: [{ w, s, e }] }] }
// Words carry approximate per-word timing; segments are sentence-sized.
//
// usage: node scripts/build-transcript.mjs <whisper.json> <out transcript.json> \
//          --title "..." --source "https://..." --duration 5145
import fs from "node:fs";

const [, , inFile, outFile, ...rest] = process.argv;
if (!inFile || !outFile) {
  console.error("usage: build-transcript.mjs whisper.json transcript.json [--title T] [--source URL] [--duration S]");
  process.exit(1);
}
const opts = {};
for (let i = 0; i < rest.length; i += 2) opts[rest[i].replace(/^--/, "")] = rest[i + 1];

const data = JSON.parse(fs.readFileSync(inFile, "utf8"));

// 1. tokens -> words with absolute times.
// With VAD on, whisper.cpp reports token offsets relative to the segment, so map
// token times linearly into the segment's own [from, to] span.
const words = [];
for (const seg of data.transcription) {
  const from = seg.offsets.from / 1000;
  const to = seg.offsets.to / 1000;
  const toks = seg.tokens.filter((t) => !/^\[_|^\[/.test(t.text) && t.text !== "");
  if (!toks.length) continue;
  const tmin = toks[0].offsets.from;
  const tmax = Math.max(...toks.map((t) => t.offsets.to));
  const span = tmax - tmin || 1;
  const map = (t) => from + ((t - tmin) / span) * (to - from);
  let cur = null;
  for (const t of toks) {
    const startsWord = /^\s/.test(t.text) || !cur;
    const piece = t.text.replace(/^\s+/, "");
    if (!piece) continue;
    const isPunct = /^[.,;:!?…»)\]"]+$/.test(piece);
    if (startsWord && !(isPunct && cur)) {
      cur = { w: piece, s: map(t.offsets.from), e: map(t.offsets.to), segEnd: false };
      words.push(cur);
    } else {
      cur.w += piece;
      cur.e = map(t.offsets.to);
    }
  }
  if (cur) cur.segEnd = true;
}

// 2. group words into sentence-sized segments.
const MAX_WORDS = 28;
const segments = [];
let buf = [];
const flush = () => {
  if (!buf.length) return;
  segments.push({
    start: +buf[0].s.toFixed(2),
    end: +buf[buf.length - 1].e.toFixed(2),
    text: buf.map((w) => w.w).join(" "),
    words: buf.map((w) => ({ w: w.w, s: +w.s.toFixed(2), e: +w.e.toFixed(2) })),
  });
  buf = [];
};
for (let i = 0; i < words.length; i++) {
  const w = words[i];
  const next = words[i + 1];
  buf.push(w);
  const endsSentence = /[.?!…]["»]?$/.test(w.w);
  const gap = next ? next.s - w.e : 99;
  if (
    (endsSentence && buf.length >= 3) ||
    gap > 1.5 ||
    buf.length >= MAX_WORDS ||
    (buf.length >= 16 && /,$/.test(w.w))
  ) {
    flush();
  }
}
flush();

// Merge tiny fragments ("¿Qué?") into the previous segment when they're close.
const merged = [];
for (const s of segments) {
  const prev = merged[merged.length - 1];
  if (prev && s.words.length <= 2 && prev.words.length < 14 && s.start - prev.end < 0.6) {
    prev.end = s.end;
    prev.text += " " + s.text;
    prev.words.push(...s.words);
  } else merged.push(s);
}

const out = {
  title: opts.title || "Untitled",
  source: opts.source || "",
  duration: Number(opts.duration) || merged.at(-1)?.end || 0,
  segments: merged,
};
fs.writeFileSync(outFile, JSON.stringify(out));
console.log(`${words.length} words -> ${merged.length} segments -> ${outFile}`);
