// Oído: listening trainer client. Plain JS, no build step.
import { sourcesHtml } from "./sources.js";
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const audio = $("#audio");
const transcriptEl = $("#transcript");

const store = {
  get: (k, d) => { try { return JSON.parse(localStorage.getItem("oido:" + k)) ?? d; } catch { return d; } },
  set: (k, v) => localStorage.setItem("oido:" + k, JSON.stringify(v)),
};

const state = {
  ep: null,          // episode id
  T: null,           // transcript
  words: [],         // flat: { w, s, e, seg, el }
  segEls: [],
  segEnds: [],
  mode: store.get("mode", "hide"),
  revealed: new Set(),
  sel: null,         // { i, j, start, end, text, seg }
  loop: null,        // { start, end, count, waiting }
  playOnceEnd: null,
  pauseEach: store.get("pauseEach", false),
  pauseTarget: null,
  saved: [],
  curWord: -1,
  curSeg: -1,
  doneSegs: -1,
  userScrolledAt: 0,
  explainFor: null,  // { key, text }
};

// ---------- utils ----------
function fmt(s) {
  s = Math.max(0, Math.floor(s || 0));
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), x = s % 60;
  return h ? `${h}:${String(m).padStart(2, "0")}:${String(x).padStart(2, "0")}` : `${m}:${String(x).padStart(2, "0")}`;
}
function toast(msg, ms = 2600) {
  const t = $("#toast");
  t.textContent = msg;
  t.classList.add("show");
  clearTimeout(toast._t);
  toast._t = setTimeout(() => t.classList.remove("show"), ms);
}
async function api(path, opts = {}) {
  const r = await fetch(path, {
    ...opts,
    headers: opts.body ? { "Content-Type": "application/json" } : undefined,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(j.error || `Request failed (${r.status})`);
  return j;
}
function esc(s) {
  return s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
}
// Minimal Markdown: paragraphs, bullet/numbered lists, **bold**, *italic*.
function md(src) {
  const inline = (s) => esc(s).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/(^|[^*])\*([^*]+)\*/g, "$1<em>$2</em>");
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
// Binary search: last index with arr[i] <= t (arr of numbers via key fn).
function lastLE(n, key, t) {
  let lo = 0, hi = n - 1, ans = -1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    if (key(mid) <= t) { ans = mid; lo = mid + 1; } else hi = mid - 1;
  }
  return ans;
}

// ---------- rendering ----------
function render() {
  const { T } = state;
  state.words = [];
  state.segEls = [];
  state.segEnds = T.segments.map((s) => s.end);
  const hard = new Set(state.saved.filter((s) => s.kind === "hard").map((s) => s.seg));
  const frag = document.createDocumentFragment();
  T.segments.forEach((seg, si) => {
    const row = document.createElement("div");
    row.className = "seg" + (seg.edited ? " edited" : "") + (hard.has(si) ? " hard" : "") + (seg.flagged ? " flagged" : "");
    row.dataset.i = si;
    const ts = document.createElement("button");
    ts.className = "ts";
    ts.textContent = fmt(seg.start);
    ts.title = "Play from here";
    ts.tabIndex = -1;
    const txt = document.createElement("span");
    txt.className = "txt";
    seg.words.forEach((w, wi) => {
      const span = document.createElement("span");
      span.className = w.u ? "w u" : "w";
      span.textContent = w.w;
      if (w.u) span.title = "Not sure about this word. Check it by ear.";
      span.dataset.k = state.words.length;
      state.words.push({ ...w, seg: si, el: span });
      txt.append(span);
      if (wi < seg.words.length - 1) txt.append(" ");
    });
    row.append(ts, txt);
    state.segEls.push(row);
    frag.append(row);
  });
  transcriptEl.replaceChildren(frag);
  state.curWord = state.curSeg = state.doneSegs = -1;
  markSavedWords();
  updateMasks();
  paintLoop();
}

function isMasked(i) {
  if (state.revealed.has(i)) return false;
  if (state.mode === "show") return false;
  if (state.mode === "trail") return !(state.segEnds[i] <= audio.currentTime + 0.05);
  return true;
}
function updateMasks() {
  state.segEls.forEach((el, i) => el.classList.toggle("masked", isMasked(i)));
}
function setMode(m) {
  state.mode = m;
  store.set("mode", m);
  state.revealed.clear();
  $$(".modes button").forEach((b) => b.setAttribute("aria-checked", b.dataset.mode === m));
  updateMasks();
}
function reveal(i) {
  state.revealed.add(i);
  state.segEls[i]?.classList.remove("masked");
}

function markSavedWords() {
  $$(".w.saved", transcriptEl).forEach((el) => el.classList.remove("saved"));
  for (const s of state.saved) {
    if (s.kind !== "saved") continue;
    rangeWords(s.start, s.end).forEach((w) => w.el.classList.add("saved"));
  }
}
function rangeWords(start, end) {
  return state.words.filter((w) => w.s >= start - 0.05 && w.e <= end + 0.05);
}
function paintLoop() {
  $$(".w.inloop", transcriptEl).forEach((el) => el.classList.remove("inloop"));
  if (state.loop) rangeWords(state.loop.start, state.loop.end).forEach((w) => w.el.classList.add("inloop"));
}

// ---------- playback tick ----------
function tick() {
  const t = audio.currentTime;
  const { words } = state;

  // current word + line
  const wi = lastLE(words.length, (i) => words[i].s, t);
  const w = words[wi];
  const nowWord = w && t <= w.e + 0.25 ? wi : -1;
  if (nowWord !== state.curWord) {
    words[state.curWord]?.el.classList.remove("now");
    if (nowWord >= 0) words[nowWord].el.classList.add("now");
    state.curWord = nowWord;
  }
  const si = state.T ? lastLE(state.T.segments.length, (i) => state.T.segments[i].start, t) : -1;
  if (si !== state.curSeg) {
    state.segEls[state.curSeg]?.classList.remove("cur");
    state.segEls[si]?.classList.add("cur");
    state.curSeg = si;
    follow();
    if (!audio.paused && state.pauseEach && si >= 0) state.pauseTarget = state.T.segments[si].end;
  }
  // "after hearing" mode: unmask lines once they've finished
  const done = lastLE(state.segEnds.length, (i) => state.segEnds[i], t + 0.05);
  if (done !== state.doneSegs) {
    state.doneSegs = done;
    if (state.mode === "trail") updateMasks();
  }
  if (w) for (let k = Math.max(0, wi - 40); k <= wi; k++) words[k].el.classList.add("heard");

  // looping / play-once / pause after each line
  if (!audio.paused) {
    const L = state.loop;
    if (L && !L.waiting && t >= L.end) {
      L.count++;
      $("#loopLabel").textContent = loopLabel();
      if ($("#echo").checked) {
        audio.pause();
        L.waiting = true;
        const gap = ((L.end - L.start) / audio.playbackRate) * 1000 + 600;
        L.timer = setTimeout(() => {
          if (state.loop !== L) return;
          L.waiting = false;
          audio.currentTime = L.start;
          audio.play();
        }, gap);
      } else {
        audio.currentTime = L.start;
      }
    } else if (state.playOnceEnd != null && t >= state.playOnceEnd) {
      audio.pause();
      state.playOnceEnd = null;
    } else if (!L && state.pauseEach && state.pauseTarget != null && t >= state.pauseTarget) {
      audio.pause();
      state.pauseTarget = null;
    }
  }

  // transport
  $("#cur").textContent = fmt(t);
  if (!seekDragging && audio.duration) $("#seek").value = Math.round((t / audio.duration) * 1000);
  if (state.ep && Math.abs(t - (tick._saved || 0)) > 3) {
    store.set("pos:" + state.ep, t);
    tick._saved = t;
  }
  requestAnimationFrame(tick);
}

function follow() {
  if (Date.now() - state.userScrolledAt < 6000) return;
  const el = state.segEls[state.curSeg];
  if (!el) return;
  const box = transcriptEl.getBoundingClientRect();
  const r = el.getBoundingClientRect();
  const rel = (r.top - box.top) / box.height;
  if (rel < 0.15 || rel > 0.55) {
    const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
    transcriptEl.scrollTo({
      top: transcriptEl.scrollTop + (r.top - box.top) - box.height * 0.3,
      behavior: reduce ? "auto" : "smooth",
    });
  }
}
["wheel", "touchmove"].forEach((e) =>
  transcriptEl.addEventListener(e, () => (state.userScrolledAt = Date.now()), { passive: true }),
);

// ---------- transport ----------
function play() {
  if (state.pauseEach && !state.loop) {
    const segs = state.T.segments;
    let i = lastLE(segs.length, (k) => segs[k].start, audio.currentTime);
    if (i < 0) i = 0;
    if (audio.currentTime >= segs[i].end - 0.08 && i + 1 < segs.length) i++;
    state.pauseTarget = segs[i].end;
  }
  return audio.play();
}
function togglePlay() { audio.paused ? play() : audio.pause(); }
function jump(d) {
  audio.currentTime = Math.max(0, Math.min(audio.duration || 1e9, audio.currentTime + d));
  if (state.loop && (audio.currentTime < state.loop.start || audio.currentTime > state.loop.end)) clearLoop();
  state.userScrolledAt = 0;
}
function seekTo(t, andPlay = false) {
  audio.currentTime = t;
  state.userScrolledAt = 0;
  if (andPlay) play();
}
audio.addEventListener("play", () => $("#playIcon").setAttribute("d", "M6 4h4v16H6zM14 4h4v16h-4z"));
audio.addEventListener("pause", () => $("#playIcon").setAttribute("d", "M7 4l13 8-13 8z"));
audio.addEventListener("loadedmetadata", () => ($("#dur").textContent = fmt(audio.duration)));

let seekDragging = false;
$("#seek").addEventListener("input", (e) => {
  seekDragging = true;
  $("#cur").textContent = fmt((e.target.value / 1000) * audio.duration);
});
$("#seek").addEventListener("change", (e) => {
  seekDragging = false;
  seekTo((e.target.value / 1000) * audio.duration);
});
$("#playBtn").onclick = togglePlay;
$$("[data-jump]").forEach((b) => (b.onclick = () => jump(Number(b.dataset.jump))));
$("#speed").value = String(store.get("speed", 1));
audio.playbackRate = Number($("#speed").value);
$("#speed").onchange = (e) => {
  audio.playbackRate = Number(e.target.value);
  store.set("speed", audio.playbackRate);
};
function stepSpeed(dir) {
  const opts = [...$("#speed").options].map((o) => o.value);
  const i = Math.max(0, Math.min(opts.length - 1, opts.indexOf($("#speed").value) + dir));
  $("#speed").value = opts[i];
  $("#speed").onchange({ target: $("#speed") });
  toast(`Speed ${opts[i]}×`, 1200);
}
function setPauseEach(on) {
  state.pauseEach = on;
  store.set("pauseEach", on);
  $("#pauseEach").classList.toggle("on", on);
  state.pauseTarget = null;
}
$("#pauseEach").onclick = () => setPauseEach(!state.pauseEach);
$("#echo").checked = store.get("echo", false);
$("#echo").onchange = (e) => store.set("echo", e.target.checked);

// ---------- loops ----------
function loopLabel() {
  const L = state.loop;
  return `Looping ${fmt(L.start)}–${fmt(L.end)} · ${L.count} ${L.count === 1 ? "repeat" : "repeats"}`;
}
function setLoop(start, end) {
  clearLoop(false);
  state.loop = { start, end, count: 0, waiting: false };
  state.playOnceEnd = null;
  $("#loopbar").hidden = false;
  $("#loopLabel").textContent = loopLabel();
  $("#mineBtn").hidden = $("#compareBtn").hidden = !recording.url;
  paintLoop();
  seekTo(start, true);
}
function clearLoop(repaint = true) {
  if (state.loop?.timer) clearTimeout(state.loop.timer);
  state.loop = null;
  $("#loopbar").hidden = true;
  if (recording.url) { URL.revokeObjectURL(recording.url); recording.url = null; }
  if (repaint) paintLoop();
}
$("#loopStop").onclick = () => clearLoop();
function playOnce(start, end) {
  if (state.loop) clearLoop();
  state.playOnceEnd = end;
  seekTo(start, true);
}

// Repeat-and-record: play the clip once, then record you saying it.
const recording = { url: null, rec: null };
$("#recBtn").onclick = async () => {
  const L = state.loop;
  if (!L || recording.rec) return;
  let stream;
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  } catch {
    return toast("Microphone access was blocked. Allow it in the browser to record.");
  }
  const dur = (L.end - L.start) / audio.playbackRate;
  if (L.timer) clearTimeout(L.timer);
  L.waiting = true; // hold the loop while recording
  audio.currentTime = L.start;
  await audio.play();
  setTimeout(() => {
    audio.pause();
    const chunks = [];
    const rec = new MediaRecorder(stream);
    recording.rec = rec;
    rec.ondataavailable = (e) => chunks.push(e.data);
    rec.onstop = () => {
      stream.getTracks().forEach((tr) => tr.stop());
      if (recording.url) URL.revokeObjectURL(recording.url);
      recording.url = URL.createObjectURL(new Blob(chunks, { type: rec.mimeType }));
      recording.rec = null;
      $("#recBtn").classList.remove("recording");
      $("#recBtn").textContent = "Record me";
      $("#mineBtn").hidden = $("#compareBtn").hidden = false;
      toast("Recorded. Play it back or compare.");
    };
    rec.start();
    $("#recBtn").classList.add("recording");
    $("#recBtn").textContent = "Recording… say it";
    setTimeout(() => rec.state === "recording" && rec.stop(), dur * 1000 * 1.4 + 800);
  }, dur * 1000 + 100);
};
function playMine() {
  return new Promise((res) => {
    const a = new Audio(recording.url);
    a.onended = res;
    a.play();
  });
}
$("#mineBtn").onclick = () => { audio.pause(); playMine(); };
$("#compareBtn").onclick = () => {
  const L = state.loop;
  if (!L) return;
  L.waiting = true;
  if (L.timer) clearTimeout(L.timer);
  audio.currentTime = L.start;
  audio.play();
  setTimeout(async () => {
    audio.pause();
    await playMine();
  }, ((L.end - L.start) / audio.playbackRate) * 1000 + 150);
};

// ---------- selection ----------
function segContext(si) {
  const segs = state.T.segments;
  return segs.slice(Math.max(0, si - 3), si + 4).map((s) => s.text).join(" ");
}
function setSel(i, j) {
  const { words } = state;
  const a = words[i], b = words[j];
  state.sel = {
    i, j,
    start: a.s, end: b.e,
    text: words.slice(i, j + 1).map((w) => w.w).join(" "),
    seg: a.seg,
  };
  showSel();
}
function selFromSeg(si) {
  const first = state.words.findIndex((w) => w.seg === si);
  const n = state.T.segments[si].words.length;
  setSel(first, first + n - 1);
}
// Netflix / Whisper comparison for the selected line, filled when the box is open.
async function fillSources() {
  const s = state.sel, box = $("#srcBox");
  if (!s || !$("#srcDetails").open) return;
  const seg = state.T.segments[s.seg];
  const html = await sourcesHtml(state.ep, { start: seg.start, end: seg.end, text: seg.text }, "en");
  if (state.sel === s) box.innerHTML = html;
}
$("#srcDetails").addEventListener("toggle", fillSources);
function showSel() {
  const s = state.sel;
  showTab("study");
  $("#selEmpty").hidden = true;
  $("#selBox").hidden = false;
  $("#selText").textContent = s.text;
  $("#selTime").textContent = `${fmt(s.start)} – ${fmt(s.end)} · ${(s.end - s.start).toFixed(1)} s`;
  $("#fixText").value = state.T.segments[s.seg].text;
  const flagged = !!state.T.segments[s.seg].flagged;
  $("#flagToggle").textContent = flagged ? "Unflag (the text is fine)" : "Flag: text doesn't match audio";
  if (flagged) $(".fix").open = true;
  fillSources();
  const key = `${s.start}-${s.end}`;
  const out = $("#explainOut");
  if (state.explainFor?.key === key) {
    out.hidden = false;
    out.innerHTML = md(state.explainFor.text);
  } else {
    out.hidden = true;
  }
}

// A press that doesn't move is a click (seek / reveal), even if an old selection
// is still active. Buttons like the timestamps don't clear a selection on their
// own, so without this a leftover selection swallowed every later click.
let downAt = null;
transcriptEl.addEventListener("mousedown", (e) => (downAt = { x: e.clientX, y: e.clientY }));
transcriptEl.addEventListener("mouseup", onPointerUp);
transcriptEl.addEventListener("touchend", () => setTimeout(onPointerUp, 0));
function onPointerUp(e) {
  const sel = getSelection();
  const isClick =
    e?.type === "mouseup" && downAt && Math.hypot(e.clientX - downAt.x, e.clientY - downAt.y) < 4 && e.detail < 2;
  if (isClick) sel?.removeAllRanges();
  else if (sel && !sel.isCollapsed && transcriptEl.contains(sel.anchorNode)) {
    const segA = sel.anchorNode.parentElement?.closest(".seg");
    const segB = sel.focusNode.parentElement?.closest(".seg");
    if (!segA || !segB) return;
    const lo = Math.min(+segA.dataset.i, +segB.dataset.i);
    const hi = Math.max(+segA.dataset.i, +segB.dataset.i);
    const ks = [];
    for (let si = lo; si <= hi; si++) {
      for (const el of $$(".w", state.segEls[si])) if (sel.containsNode(el, true)) ks.push(+el.dataset.k);
    }
    if (ks.length) setSel(Math.min(...ks), Math.max(...ks));
    return;
  }
  if (!e || e.type !== "mouseup") return;
  const ts = e.target.closest(".ts");
  const row = e.target.closest(".seg");
  if (!row) return;
  const si = +row.dataset.i;
  if (ts) return seekTo(state.T.segments[si].start, true);
  if (row.classList.contains("masked")) {
    reveal(si);
    return;
  }
  const w = e.target.closest(".w");
  if (w) seekTo(state.words[+w.dataset.k].s);
}

$("#actPlay").onclick = () => state.sel && playOnce(state.sel.start, state.sel.end);
$("#actLoop").onclick = () => state.sel && setLoop(state.sel.start, state.sel.end);
$("#actSave").onclick = async () => {
  const s = state.sel;
  if (!s) return;
  const key = `${s.start}-${s.end}`;
  await saveItem({
    kind: "saved", start: s.start, end: s.end, text: s.text, seg: s.seg,
    explanation: state.explainFor?.key === key ? state.explainFor.text : "",
  });
  toast("Saved");
};
$("#actExplain").onclick = () => explainSel();
$("#askForm").onsubmit = (e) => {
  e.preventDefault();
  explainSel($("#askInput").value.trim());
};
async function explainSel(question = "", fresh = false) {
  const s = state.sel;
  if (!s) return;
  const out = $("#explainOut");
  out.hidden = false;
  out.classList.add("loading");
  out.textContent = "Asking Claude…";
  try {
    const { explanation, cached, at } = await api("api/explain", {
      method: "POST",
      body: { text: s.text, context: segContext(s.seg), question, fresh },
    });
    state.explainFor = { key: `${s.start}-${s.end}`, text: explanation };
    if (state.sel === s) {
      out.innerHTML = md(explanation) + (cached ? `<p class="cachednote">Saved look-up from ${new Date(at).toLocaleDateString()} · <button type="button" class="linkbtn" id="reask">Ask Claude again</button></p>` : "");
      $("#reask")?.addEventListener("click", () => explainSel(question, true));
    }
    // attach to an existing saved item for the same range
    const hit = state.saved.find((x) => Math.abs(x.start - s.start) < 0.01 && Math.abs(x.end - s.end) < 0.01);
    if (hit) {
      hit.explanation = explanation;
      await api(`api/saved/${hit.id}`, { method: "PATCH", body: { explanation } });
      renderSaved();
    }
  } catch (err) {
    out.textContent = err.message;
  } finally {
    out.classList.remove("loading");
  }
}
$("#actAnki").onclick = () => {
  const s = state.sel;
  if (!s) return;
  const key = `${s.start}-${s.end}`;
  makeAnki({ start: s.start, end: s.end, text: s.text, explanation: state.explainFor?.key === key ? state.explainFor.text : "" });
};
async function makeAnki(item) {
  const btns = $$("#actAnki, .row-actions [data-a=anki]");
  btns.forEach((b) => (b.disabled = true));
  toast(item.explanation ? "Adding to Anki…" : "Looking it up, then adding to Anki…", 15000);
  try {
    const { explanation } = await api("api/anki", {
      method: "POST",
      body: {
        episode: state.ep,
        start: item.start,
        end: item.end,
        text: item.text,
        context: segContext(segOfTime(item.start)),
        explanation: item.explanation || "",
      },
    });
    rememberExplanation(item.start, item.end, explanation);
    toast("Added to Anki (deck: Spanish Listening)");
  } catch (err) {
    toast(err.message, 6000);
  } finally {
    btns.forEach((b) => (b.disabled = false));
  }
}
// Keep a lookup: show it for the current selection and store it on a saved item.
async function rememberExplanation(start, end, explanation) {
  if (!explanation) return;
  const s = state.sel;
  if (s && Math.abs(s.start - start) < 0.01 && Math.abs(s.end - end) < 0.01) {
    state.explainFor = { key: `${s.start}-${s.end}`, text: explanation };
    showSel();
  }
  const hit = state.saved.find((x) => Math.abs(x.start - start) < 0.01 && Math.abs(x.end - end) < 0.01);
  if (hit && hit.explanation !== explanation) {
    hit.explanation = explanation;
    await api(`api/saved/${hit.id}`, { method: "PATCH", body: { explanation } });
    renderSaved();
  }
}
$("#fixSave").onclick = async () => {
  const s = state.sel;
  if (!s) return;
  const text = $("#fixText").value.trim();
  try {
    const seg = await api(`api/episodes/${state.ep}/segments/${s.seg}`, { method: "PUT", body: { text } });
    state.T.segments[s.seg] = seg;
    const top = transcriptEl.scrollTop;
    render();
    transcriptEl.scrollTop = top;
    reveal(s.seg);
    selFromSeg(s.seg);
    toast("Correction saved");
  } catch (err) {
    toast(err.message);
  }
};

$("#flagToggle").onclick = async () => {
  const s = state.sel;
  if (!s) return;
  const flagged = !state.T.segments[s.seg].flagged;
  try {
    const seg = await api(`api/episodes/${state.ep}/segments/${s.seg}/flag`, { method: "POST", body: { flagged } });
    state.T.segments[s.seg] = seg;
    const top = transcriptEl.scrollTop;
    render();
    transcriptEl.scrollTop = top;
    selFromSeg(s.seg);
    toast(flagged ? "Flagged: it's out of the games until fixed" : "Unflagged");
  } catch (err) {
    toast(err.message);
  }
};

// ---------- saved items ----------
async function saveItem(item) {
  const saved = await api("api/saved", { method: "POST", body: { ...item, episode: state.ep } });
  saved.seg = item.seg;
  state.saved.push(saved);
  markSavedWords();
  if (item.kind === "hard") state.segEls[item.seg]?.classList.add("hard");
  renderSaved();
  return saved;
}
function segOfTime(t) {
  return Math.max(0, lastLE(state.T.segments.length, (i) => state.T.segments[i].start, t + 0.01));
}
function renderSaved() {
  const list = $("#savedList");
  const showHard = $("#showHard").checked, showSaved = $("#showSaved").checked;
  const items = state.saved
    .filter((s) => (s.kind === "hard" ? showHard : showSaved))
    .sort((a, b) => a.start - b.start);
  $("#savedCount").textContent = state.saved.length ? `(${state.saved.length})` : "";
  if (!items.length) {
    list.innerHTML = `<li class="empty">Nothing here yet. Select words and press Save, or press X while listening to mark a line you didn't catch.</li>`;
    return;
  }
  list.replaceChildren(
    ...items.map((s) => {
      const li = document.createElement("li");
      li.className = "kind-" + s.kind;
      li.innerHTML = `
        <div class="t">${esc(s.text)}</div>
        <div class="meta">${fmt(s.start)} · ${s.kind === "hard" ? "missed line" : "saved phrase"}</div>
        ${s.explanation ? `<details class="note"><summary>Explanation</summary>${md(s.explanation)}</details>` : ""}
        <div class="row-actions">
          <button data-a="go">Go</button>
          <button data-a="loop">Loop</button>
          <button data-a="sel">Select</button>
          <button data-a="anki">Anki card</button>
          <button data-a="del">Delete</button>
        </div>`;
      li.querySelector(".row-actions").onclick = async (e) => {
        const a = e.target.dataset.a;
        if (a === "go") { reveal(segOfTime(s.start)); seekTo(s.start, true); }
        if (a === "loop") setLoop(s.start, s.end);
        if (a === "anki") makeAnki(s);
        if (a === "sel") {
          const ws = rangeWords(s.start, s.end);
          if (ws.length) {
            setSel(+ws[0].el.dataset.k, +ws.at(-1).el.dataset.k);
            if (s.explanation) { state.explainFor = { key: `${state.sel.start}-${state.sel.end}`, text: s.explanation }; showSel(); }
          }
        }
        if (a === "del") {
          await api(`api/saved/${s.id}`, { method: "DELETE" });
          state.saved = state.saved.filter((x) => x.id !== s.id);
          if (s.kind === "hard") state.segEls[segOfTime(s.start)]?.classList.remove("hard");
          markSavedWords();
          renderSaved();
        }
      };
      return li;
    }),
  );
}
$("#showHard").onchange = $("#showSaved").onchange = renderSaved;
$("#exportTsv").onclick = () => {
  const rows = state.saved
    .sort((a, b) => a.start - b.start)
    .map((s) => [s.text, (s.explanation || "").replace(/\s*\n\s*/g, "<br>"), `${state.T.title} @ ${fmt(s.start)}`]
      .map((f) => f.replace(/\t/g, " ")).join("\t"));
  const blob = new Blob([rows.join("\n")], { type: "text/tab-separated-values" });
  const a = Object.assign(document.createElement("a"), { href: URL.createObjectURL(blob), download: `${state.ep}-saved.tsv` });
  a.click();
  URL.revokeObjectURL(a.href);
};

// ---------- tabs ----------
function showTab(name) {
  $$(".tabs button").forEach((b) => b.classList.toggle("on", b.dataset.tab === name));
  $$(".tab").forEach((t) => (t.hidden = t.dataset.tab !== name));
}
$$(".tabs button").forEach((b) => (b.onclick = () => showTab(b.dataset.tab)));
$$(".modes button").forEach((b) => (b.onclick = () => setMode(b.dataset.mode)));

// ---------- keyboard ----------
// Don't leave focus on a mouse-clicked button, or Space would press it again
// instead of play/pause. (detail is 0 for keyboard activation, so tabbing still works.)
document.addEventListener("click", (e) => {
  const b = e.target.closest("button");
  if (b && e.detail) b.blur();
});
document.addEventListener("keydown", (e) => {
  if (e.target.closest("input, textarea, select") || e.metaKey || e.ctrlKey) return;
  const cur = state.curSeg >= 0 ? state.curSeg : 0;
  const seg = state.T?.segments[cur];
  switch (e.key) {
    case " ": e.preventDefault(); togglePlay(); break;
    case "ArrowLeft": e.preventDefault(); jump(e.altKey ? -20 : e.shiftKey ? -10 : -5); break;
    case "ArrowRight": e.preventDefault(); jump(5); break;
    case "r": case "R": if (seg) playOnce(seg.start, seg.end); break;
    case "t": case "T": reveal(cur); break;
    case "x": case "X":
      if (seg && !state.saved.some((s) => s.kind === "hard" && Math.abs(s.start - seg.start) < 0.01)) {
        saveItem({ kind: "hard", start: seg.start, end: seg.end, text: seg.text, seg: cur }).then(() => toast("Marked as missed"));
      }
      break;
    case "l": case "L":
      if (state.sel) setLoop(state.sel.start, state.sel.end);
      else if (seg) setLoop(seg.start, seg.end);
      break;
    case "p": case "P": setPauseEach(!state.pauseEach); toast(state.pauseEach ? "Pausing after every line" : "Continuous play", 1400); break;
    case "Escape": clearLoop(); break;
    case "[": stepSpeed(-1); break;
    case "]": stepSpeed(1); break;
    case "h": case "H": {
      const order = ["hide", "trail", "show"];
      setMode(order[(order.indexOf(state.mode) + 1) % 3]);
      break;
    }
  }
});

// ---------- boot ----------
async function loadEpisode(id) {
  state.ep = id;
  store.set("lastEp", id);
  const qs = new URLSearchParams(location.search);
  qs.set("ep", id);
  history.replaceState(null, "", "?" + qs);
  state.T = await (await fetch(`media/${encodeURIComponent(id)}/transcript.json`, { cache: "no-cache" })).json();
  state.saved = await api(`api/saved?episode=${encodeURIComponent(id)}`);
  state.saved.forEach((s) => (s.seg = segOfTime(s.start)));
  state.revealed.clear();
  state.sel = null;
  clearLoop(false);
  audio.src = `media/${encodeURIComponent(id)}/audio.mp3`;
  audio.currentTime = store.get("pos:" + id, 0);
  render();
  renderSaved();
  document.title = `Oído — ${state.T.title}`;
  $("#playLink").href = `play.html?ep=${encodeURIComponent(id)}`;
  $("#rpgLink").href = `rpg.html?ep=${encodeURIComponent(id)}`;
}

(async function boot() {
  setMode(state.mode);
  setPauseEach(state.pauseEach);
  const eps = await api("api/episodes");
  const sel = $("#episode");
  sel.replaceChildren(...eps.map((e) => new Option(e.title, e.id)));
  sel.onchange = () => loadEpisode(sel.value);
  if (!eps.length) {
    transcriptEl.innerHTML = `<p class="empty">No episodes yet. Run <code>scripts/add-episode.sh &lt;youtube-url&gt;</code> to add one.</p>`;
    return;
  }
  const want = new URLSearchParams(location.search).get("ep") || store.get("lastEp", null);
  const id = eps.some((e) => e.id === want) ? want : eps[0].id;
  sel.value = id;
  await loadEpisode(id);
  requestAnimationFrame(tick);
})();
