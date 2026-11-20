// The two sources a transcript line was made from, for comparison: the official (Netflix)
// subtitles aligned to the audio, and Whisper's raw transcription. Read straight from the
// episode folder (media/<id>/transcript.subs.json and transcript.whisper.json); episodes
// transcribed without subtitles only have Whisper.
const cache = {};
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const fmt = (t) => `${Math.floor(t / 60)}:${String(Math.floor(t % 60)).padStart(2, "0")}`;

async function getJson(url) {
  try {
    const r = await fetch(url);
    return r.ok ? await r.json() : null;
  } catch { return null; }
}
export function loadSources(ep) {
  if (!cache[ep]) {
    cache[ep] = Promise.all([getJson(`media/${ep}/transcript.subs.json`), getJson(`media/${ep}/transcript.whisper.json`)])
      .then(([subs, whisper]) => ({ subs, whisper }));
  }
  return cache[ep];
}

// The source's lines that overlap [start, end] (with a little slack), words outside the range dimmed.
function linesFor(T, start, end) {
  if (!T) return null;
  const pad = 0.35;
  const inside = (w) => { const mid = (w.s + w.e) / 2; return mid >= start - 0.15 && mid <= end + 0.15; };
  return T.segments.filter((s) => s.end > start - pad && s.start < end + pad && (!s.words?.length || s.words.some(inside))).map((s) => {
    const words = s.words?.length ? s.words.map((w) => {
      return inside(w) ? esc(w.w) : `<span class="out">${esc(w.w)}</span>`;
    }).join(" ") : esc(s.text);
    return `<div class="srcline"><span class="t">${fmt(s.start)}</span> ${words}</div>`;
  });
}

// HTML comparing the line (start..end, text) with both sources.
const L = {
  es: { none: "No disponible para este episodio.", empty: "Nada en este momento del audio.", cur: "Transcripción",
    subs: "subtítulos oficiales, alineados al audio; suelen resumir", whisper: "transcripción automática del audio, sin corregir",
    help: "En gris: palabras de la misma línea que caen fuera de este fragmento." },
  en: { none: "Not available for this episode.", empty: "Nothing at this point in the audio.", cur: "Transcript",
    subs: "official subtitles, aligned to the audio; often condensed", whisper: "automatic transcription of the audio, uncorrected",
    help: "Greyed out: words of the same line that fall outside this stretch." },
};
export async function sourcesHtml(ep, { start, end, text }, lang = "es") {
  const { subs, whisper } = await loadSources(ep);
  const t = L[lang];
  const block = (title, note, lines) => `<section class="src">
      <h4>${title} <span class="note">${note}</span></h4>
      ${lines == null ? `<p class="none">${t.none}</p>` : lines.length ? lines.join("") : `<p class="none">${t.empty}</p>`}
    </section>`;
  return `<section class="src cur"><h4>${t.cur} <span class="note">${fmt(start)}–${fmt(end)}</span></h4><div class="srcline">${esc(text)}</div></section>`
    + block("Netflix", t.subs, linesFor(subs, start, end))
    + block("Whisper", t.whisper, linesFor(whisper, start, end))
    + `<p class="srchelp">${t.help}</p>`;
}
