// Shared listening-exercise logic: scoring typed answers against a transcript line.
// Used by the dictation game (play.js) and the RPG (rpg/main.js).

export const $ = (s, el = document) => el.querySelector(s);
export const fmt = (s) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`;
export const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

// What this server offers: { online, lang (being learned), user }. Online, everyone logs in and
// their game lives on the server (see auth.js); offline it's all in this browser.
export const CFG = await fetch("api/config").then((r) => r.json()).catch(() => ({ online: false, lang: "es", user: null }));

const PRE = "oido:";
export const store = {
  get: (k, d) => { try { return JSON.parse(localStorage.getItem(PRE + k)) ?? d; } catch { return d; } },
  set: (k, v) => { localStorage.setItem(PRE + k, JSON.stringify(v)); if (CFG.online) dirty(); },
};

// ---------- online: the saved game goes to the server ----------
// Every change is kept here at once and sent a moment later. Each copy carries the time of its
// last change, so a save that never reached the server (no signal) wins over the server's older one.
let pushTimer = null;
function localState() {
  const out = {};
  for (let i = 0; i < localStorage.length; i++) {
    const k = localStorage.key(i);
    if (k.startsWith(PRE)) try { out[k.slice(PRE.length)] = JSON.parse(localStorage.getItem(k)); } catch { /* skip */ }
  }
  return out;
}
function dirty() {
  localStorage.setItem(PRE + "_t", String(Date.now()));
  localStorage.setItem(PRE + "_user", JSON.stringify(CFG.user?.id));
  clearTimeout(pushTimer);
  pushTimer = setTimeout(push, 1200);
}
async function push() {
  clearTimeout(pushTimer); pushTimer = null;
  try {
    const r = await fetch("api/state", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(localState()) });
    if (r.status === 401) location.replace("login.html");
  } catch { /* offline: it goes with the next change, or on the next visit */ }
}
if (CFG.online) {
  const r = await fetch("api/state");
  if (r.status === 401) { location.replace("login.html"); await new Promise(() => {}); }
  const server = await r.json();
  const mine = store.get("_user", null) === CFG.user?.id;
  if (mine && Number(store.get("_t", 0)) > Number(server._t || 0)) push(); // this device is ahead
  else {
    for (const k of Object.keys(localStorage)) if (k.startsWith(PRE)) localStorage.removeItem(k);
    for (const [k, v] of Object.entries(server)) localStorage.setItem(PRE + k, JSON.stringify(v));
    localStorage.setItem(PRE + "_user", JSON.stringify(CFG.user?.id));
  }
  // leaving the page or switching apps: send what's pending now
  const flush = () => { if (pushTimer) push(); };
  addEventListener("pagehide", flush);
  document.addEventListener("visibilitychange", () => document.visibilityState === "hidden" && flush());
}
export async function logout() {
  if (pushTimer) await push();
  await fetch("api/logout", { method: "POST" }).catch(() => {});
  for (const k of Object.keys(localStorage)) if (k.startsWith(PRE)) localStorage.removeItem(k);
  location.replace("login.html");
}

export async function api(path, opts = {}) {
  const r = await fetch(path, {
    ...opts,
    headers: opts.body ? { "Content-Type": "application/json" } : undefined,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(j.error || `Request failed (${r.status})`);
  return j;
}

export function hash(n) { n = ((n >>> 16) ^ n) * 0x45d9f3b; n = ((n >>> 16) ^ n) * 0x45d9f3b; return ((n >>> 16) ^ n) >>> 0; }

export function norm(w) {
  // lenient: accents (and ñ vs n) don't count against you
  // apostrophes don't count either: phones type ’ for ', and "dont" is close enough to "don't"
  return w.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9]/g, "");
}
// A word that's right except for its accents (or ñ) costs this much of the line's score,
// so nothing is 100% without every accent.
export const ACCENT_PENALTY = 0.01;
// strict: case and punctuation don't matter, but accents and ñ do
const hasAccent = (w) => /[áéíóúüñ]/i.test(w);
export const accentKey = (w) => w.toLowerCase().normalize("NFC").replace(/[^\p{L}0-9']/gu, "");
function lev(a, b) {
  const d = Array.from({ length: a.length + 1 }, (_, i) => [i]);
  for (let j = 1; j <= b.length; j++) d[0][j] = j;
  for (let i = 1; i <= a.length; i++)
    for (let j = 1; j <= b.length; j++)
      d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
  return d[a.length][b.length];
}
// 2 = exact (ignoring accents/punctuation), 1 = a typo away, 0 = different.
// extraTol widens the typo allowance (an RPG item can grant it).
export function sim(target, typed, extraTol = 0) {
  if (!typed) return 0;
  if (target === typed) return 2;
  const tol = (target.length >= 8 ? 2 : target.length >= 4 ? 1 : 0) + (target.length >= 3 ? extraTol : 0);
  return tol && lev(target, typed) <= tol ? 1 : 0;
}

export function md(src) {
  const inline = (s) => esc(s).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/(^|[^*])\*([^*]+)\*/g, "$1<em>$2</em>");
  let html = "", list = false;
  for (const raw of src.split("\n")) {
    const l = raw.trim(), m = /^[-*]\s+(.*)$/.exec(l);
    if (m) { if (!list) { html += "<ul>"; list = true; } html += `<li>${inline(m[1])}</li>`; continue; }
    if (list) { html += "</ul>"; list = false; }
    if (l) html += `<p>${inline(l.replace(/^#+\s*/, ""))}</p>`;
  }
  return html + (list ? "</ul>" : "");
}

// Lines worth playing: 3–24 words, nothing uncertain, no digits (numbers can be written many ways),
// and not flagged as not matching the audio.
export function playable(seg) {
  const n = seg.words.length;
  return n >= 3 && n <= 24 && !seg.flagged && !seg.words.some((w) => w.u) && !/\d/.test(seg.text);
}

// Which words to blank in "fill the gaps": ordinary words of 4+ letters, not names.
// avoid: words to leave out if there are others to pick (a second pass over the same line).
export function chooseBlanks(segments, si, maxK = 4, avoid = []) {
  const words = segments[si].words;
  const isName = (i) => i > 0 && /^[¿¡«"]?\p{Lu}/u.test(words[i].w) && !/[.?!…]$/.test(words[i - 1].w);
  let cand = words.map((w, i) => i).filter((i) => norm(words[i].w).length >= 4 && !isName(i) && !isSound(words[i].w));
  if (avoid.length) { const rest = cand.filter((i) => !avoid.includes(i)); if (rest.length) cand = rest; else return avoid.slice(); }
  if (!cand.length) {
    // short line like "Por fin, ¿no?": gap its longest word
    const real = words.map((w, i) => i).filter((i) => !isSound(words[i].w));
    cand = (real.length ? real : words.map((w, i) => i)).sort((a, b) => norm(words[b].w).length - norm(words[a].w).length).slice(0, 1);
  }
  const k = Math.max(1, Math.min(maxK, Math.round(words.length * 0.25), cand.length));
  return cand.map((i) => [hash(si * 131 + i), i]).sort((a, b) => a[0] - b[0]).slice(0, k).map((x) => x[1]).sort((a, b) => a - b);
}

// Weighted LCS between target words and typed words: exact matches 2, near matches 1.
export function alignWords(target, typed, extraTol = 0) {
  const n = target.length, m = typed.length;
  const D = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(0));
  for (let i = 1; i <= n; i++)
    for (let j = 1; j <= m; j++) {
      const s = sim(target[i - 1], typed[j - 1], extraTol);
      D[i][j] = Math.max(D[i - 1][j], D[i][j - 1], s ? D[i - 1][j - 1] + s : -1);
    }
  const ops = [];
  let i = n, j = m;
  while (i > 0 || j > 0) {
    const s = i && j ? sim(target[i - 1], typed[j - 1], extraTol) : 0;
    if (i && j && s && D[i][j] === D[i - 1][j - 1] + s) { ops.push({ t: i - 1, y: j - 1, s }); i--; j--; }
    else if (i && (!j || D[i][j] === D[i - 1][j])) { ops.push({ t: i - 1, s: 0 }); i--; }
    else { ops.push({ y: j - 1, extra: true }); j--; }
  }
  return ops.reverse();
}

// Score a dictation answer. Returns { acc, html, exact, near, missed } where acc is 0..1.
// Sounds rather than words (ah, ay, eh, oh, mm, hum, ujum, uf, jaja ...): they don't count in a dictation,
// written or not.
const SOUND = /^(a+h+|a+y+|a+h+a+|e+h+|e+y+|o+h+|o+y+|u+h+|h*u+h*m+|e+h*m+|u+j+u+m+|m+j+m+|m+|h+m+|m+h+m+|u+f+|p+u+f+|b+a+h+|(ja)+j?|(je)+j?|(ji)+j?|(jo)+j?|h?u+y+|s+h+|p+s+t+|a+j+a+|o+h+o+)$/;
export const isSound = (w) => SOUND.test(norm(w));

export function scoreDictation(allWords, typedText, opts = {}) {
  // score without the sounds (unless the line is nothing but sounds), then put them back, greyed
  const keep = allWords.map((w, i) => i).filter((i) => !isSound(allWords[i].w));
  if (!keep.length || keep.length === allWords.length) return scoreWords(allWords, typedText, opts);
  const typed = typedText.trim().split(/\s+/).filter((t) => t && !isSound(t)).join(" ");
  const r = scoreWords(keep.map((i) => allWords[i]), typed, opts);
  r.words.forEach((x) => (x.i = keep[x.i]));
  // re-thread the html: each scored word's span is followed by the sounds before the next one
  const spans = r.html.match(/<span[^>]*>.*?<\/span> /g) || [];
  let html = "", k = 0;
  const sound = (i) => `<span class="sound" title="Un sonido, no cuenta">${esc(allWords[i].w)}</span> `;
  for (const sp of spans) {
    if (!/class="(edge|extra)/.test(sp)) while (k < allWords.length && isSound(allWords[k].w)) html += sound(k++);
    html += sp;
    if (!/class="(edge|extra)/.test(sp)) k++;
  }
  while (k < allWords.length) html += isSound(allWords[k].w) ? sound(k++) : (k++, "");
  r.html = html;
  r.typed = typedText.trim();
  return r;
}
function scoreWords(words, typedText, { extraTol = 0, nearIsExact = false } = {}) {
  const typedRaw = typedText.trim().split(/\s+/).filter(Boolean);
  const ops = alignWords(words.map((w) => norm(w.w)), typedRaw.map(norm), extraTol);
  let got = 0, strict = 0, exact = 0, near = 0, html = "", accents = true, accentMiss = 0;
  // Extra words before the first or after the last word of the line are fine: the clip often
  // catches a fragment of the line before or after. Only extras in the middle count as wrong.
  const firstHit = ops.findIndex((o) => !o.extra), lastHit = ops.length - 1 - [...ops].reverse().findIndex((o) => !o.extra);
  ops.forEach((op, k) => { if (op.extra && (firstHit < 0 || k < firstHit || k > lastHit)) op.edge = true; });
  // per word of the line: { i, w, typed, ok, near, accent }. A missed word takes the stray typed
  // word(s) sitting in its gap, so "you wrote X, it was Y" can be shown.
  const per = [];
  let gap = [];
  for (const op of ops) {
    if (op.edge) continue;
    if (op.extra) { gap.push(typedRaw[op.y]); continue; }
    if (op.s) { gap = []; continue; }
    per.push({ t: op.t, gap });
  }
  const strays = new Map(per.map((x) => [x.t, x.gap]));
  const used = new Set();
  const perWord = [];
  for (const op of ops) {
    if (op.edge) { html += `<span class="edge" title="Not part of this line (the clip can catch a bit of the line before or after). Doesn't count against you.">${esc(typedRaw[op.y])}</span> `; continue; }
    if (op.extra) { html += `<span class="extra">${esc(typedRaw[op.y])}</span> `; accents = false; continue; }
    const w = words[op.t].w;
    const badAccent = op.s === 2 && accentKey(w) !== accentKey(typedRaw[op.y] || "");
    let typedW = op.y != null ? typedRaw[op.y] : null;
    if (!op.s) { const g = strays.get(op.t) || []; typedW = g.find((x) => !used.has(x)) ?? null; if (typedW) used.add(typedW); }
    perWord.push({ i: op.t, w, typed: typedW, ok: op.s === 2 && !badAccent, near: op.s === 1, accent: badAccent });
    if (op.s !== 2 || badAccent) accents = false;
    if (badAccent) accentMiss++;
    const s = op.s;
    if (s === 2) exact++; else if (s === 1) near++;
    got += s === 2 ? 1 : s === 1 ? 0.5 : 0;
    strict += op.s === 2 ? 1 : op.s === 1 ? 0.5 : 0;
    const title = op.s === 1 ? ` title="You typed: ${esc(typedRaw[op.y])}"` : badAccent ? ` title="Accent: you typed ${esc(typedRaw[op.y])}"` : "";
    html += `<span class="${s === 2 ? "ok" : s === 1 ? "close" : "miss"}${badAccent ? " accent" : ""}"${title}>${esc(w)}</span> `;
  }
  // accentsPerfect: every word right, spelled exactly, accents and ñ included
  // nearIsExact (an item's help in a fight): a missing accent costs nothing. strictAcc is what you
  // really wrote, accents counted, for mastery
  return { acc: Math.max(0, got / words.length - (nearIsExact ? 0 : ACCENT_PENALTY * accentMiss)), strictAcc: Math.max(0, strict / words.length - ACCENT_PENALTY * accentMiss), html, exact, near, accentMiss,
    missed: words.length - exact - near, typed: typedRaw.join(" "), words: perWord,
    // only counts when there was an accent (or ñ) to get right
    accentsPerfect: accents && got === words.length && words.some((w) => hasAccent(w.w)) };
}

// Score "fill the gaps" inputs ({wordIndex: typed}). Same return shape.
export function scoreCloze(words, blanks, typed, { extraTol = 0, nearIsExact = false } = {}) {
  let got = 0, strict = 0, exact = 0, near = 0, html = "", accents = true, accentMiss = 0;
  const perWord = [];
  words.forEach((w, i) => {
    if (!blanks.includes(i)) { html += esc(w.w) + " "; return; }
    let s = sim(norm(w.w), norm(typed[i] || ""), extraTol);
    const badAccent = s === 2 && accentKey(w.w) !== accentKey(typed[i] || "");
    perWord.push({ i, w: w.w, typed: typed[i] || null, ok: s === 2 && !badAccent, near: s === 1, accent: badAccent });
    if (s !== 2 || badAccent) accents = false;
    if (badAccent) accentMiss++;
    strict += s === 2 ? 1 : s === 1 ? 0.5 : 0;
    if (s === 2) exact++; else if (s === 1) near++;
    got += s === 2 ? 1 : s === 1 ? 0.5 : 0;
    const title = badAccent ? "Accent: you typed " + esc(typed[i]) : s === 2 ? "" : "You typed: " + esc(typed[i] || "(nothing)");
    html += `<span class="${s === 2 ? "ok" : s === 1 ? "close" : "miss"}${badAccent ? " accent" : ""}" title="${title}">${esc(w.w)}</span> `;
  });
  return { acc: Math.max(0, got / blanks.length - (nearIsExact ? 0 : ACCENT_PENALTY * accentMiss)), strictAcc: Math.max(0, strict / blanks.length - ACCENT_PENALTY * accentMiss), html, exact, near, accentMiss,
    missed: blanks.length - exact - near, words: perWord, accentsPerfect: accents && got === blanks.length && blanks.some((i) => hasAccent(words[i].w)) };
}

// Mark a line as "text doesn't match the audio". It drops out of the games until fixed.
export function flagLine(ep, si, flagged = true) {
  return api(`api/episodes/${encodeURIComponent(ep)}/segments/${si}/flag`, { method: "POST", body: { flagged } });
}
