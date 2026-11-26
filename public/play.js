// Oído: dictation game. Hear a line, type it, get scored word by word.
import { $, fmt, esc, store, api, md, playable, flagLine, chooseBlanks as pickBlanks, scoreDictation, scoreCloze } from "./listen-core.js";
const audio = $("#audio");
const GOAL = 20; // lines per day


const G = store.get("game", { xp: 0, combo: 0, bestCombo: 0, day: "", todayCount: 0, streak: 0, lastGoalDay: "" });
const st = {
  ep: null, T: null,
  lines: [],      // indices of playable segments
  li: 0,          // position in lines
  prog: null,     // { pos, r: { segIdx: bestAccuracy } }
  mode: store.get("gameMode", "dictation"),
  plays: 0, slows: 0, hinted: false, checked: false,
  blanks: [],     // cloze: word indices to fill
};

// ---------- helpers ----------
function toast(msg, cls = "", ms = 2200) {
  const t = $("#toast");
  t.textContent = msg;
  t.className = "toast show " + cls;
  clearTimeout(toast._t);
  toast._t = setTimeout(() => (t.className = "toast"), ms);
}
const dayStr = (d = new Date()) => d.toLocaleDateString("en-CA");
const yesterday = () => dayStr(new Date(Date.now() - 864e5));

// ---------- level / stats ----------
function levelOf(xp) {
  let level = 1, rem = xp;
  while (rem >= 100 * level) { rem -= 100 * level; level++; }
  return { level, rem, need: 100 * level };
}
function rollDay() {
  const today = dayStr();
  if (G.day !== today) { G.day = today; G.todayCount = 0; }
  if (G.lastGoalDay !== today && G.lastGoalDay !== yesterday()) G.streak = 0;
}
function renderStats(pop = []) {
  const L = levelOf(G.xp);
  $("#lvl").textContent = L.level;
  $("#xpfill").style.width = `${(L.rem / L.need) * 100}%`;
  $("#xptxt").textContent = `${L.rem} / ${L.need}`;
  $("#combo").textContent = `×${comboMult().toFixed(1)}`;
  $("#today").textContent = `${G.todayCount}/${GOAL}`;
  $("#streak").textContent = G.streak;
  for (const id of pop) {
    const el = $("#" + id).closest(".stat");
    el.classList.remove("pop"); void el.offsetWidth; el.classList.add("pop");
  }
}
const comboMult = () => 1 + 0.1 * Math.min(G.combo, 10);

// ---------- episode map ----------
function renderMap() {
  const map = $("#map");
  map.replaceChildren(...st.lines.map((si, k) => {
    const i = document.createElement("i");
    const r = st.prog.r[si];
    if (r != null) i.className = r >= 1 ? "perfect" : r >= 0.7 ? "good" : "rough";
    if (k === st.li) i.classList.add("cur");
    return i;
  }));
  const done = st.lines.filter((si) => st.prog.r[si] != null).length;
  const perfect = st.lines.filter((si) => st.prog.r[si] >= 1).length;
  $("#mapTxt").textContent = `${done} of ${st.lines.length} lines played · ${perfect} perfect`;
}
$("#map").addEventListener("click", (e) => {
  const r = $("#map").getBoundingClientRect();
  goTo(Math.floor(((e.clientX - r.left) / r.width) * st.lines.length));
});

// ---------- audio ----------
let stopAt = null;
function playLine(rate = 1) {
  const s = st.T.segments[st.lines[st.li]];
  audio.playbackRate = rate;
  audio.currentTime = Math.max(0, s.start - 0.12);
  stopAt = s.end + 0.2;
  audio.play();
  $("#playLine").classList.add("playing");
}
// checked every frame, and on the audio's own progress events: frames stop in a background tab
function checkStop() {
  if (stopAt != null && !audio.paused && audio.currentTime >= stopAt) {
    audio.pause();
    stopAt = null;
  }
}
(function watch() { checkStop(); requestAnimationFrame(watch); })();
audio.addEventListener("timeupdate", checkStop);
audio.addEventListener("pause", () => $("#playLine").classList.remove("playing"));

// Penalties: first listen is free; each extra listen −10%, slow −15%, hint −30%.
function multiplier() {
  return Math.max(0.3, 1 - 0.1 * Math.max(0, st.plays - 1) - 0.15 * st.slows - (st.hinted ? 0.3 : 0));
}
function renderCost() {
  const m = multiplier();
  $("#cost").textContent = `${Math.round(m * 100)}% points`;
  $("#cost").classList.toggle("down", m < 1);
}
function doPlay(slow = false) {
  if (!st.checked) {
    if (slow) st.slows++; else st.plays++;
    renderCost();
  }
  playLine(slow ? 0.7 : 1);
}

// ---------- rounds ----------
function chooseBlanks(si) { return pickBlanks(st.T.segments, si); }
function goTo(k, autoplay = true) {
  st.li = Math.max(0, Math.min(st.lines.length - 1, k));
  st.prog.pos = st.li;
  store.set("game:" + st.ep, st.prog);
  const si = st.lines[st.li];
  const seg = st.T.segments[si];
  st.plays = 0; st.slows = 0; st.hinted = false; st.checked = false; st.explanation = ""; st.undo = null;
  document.querySelectorAll(".flagBtn").forEach((b) => (b.disabled = false));
  $("#when").textContent = `Line ${st.li + 1} of ${st.lines.length} · ${fmt(seg.start)} · ${seg.words.length} words`;
  $("#result").hidden = true;
  $("#explainOut").hidden = true;
  $("#ankiBtn").textContent = "Anki card";
  $("#skeleton").hidden = true;
  $("#checkBtn").disabled = false;
  $("#hintBtn").disabled = false;
  $("#answer").value = "";
  if (st.mode === "cloze") {
    st.blanks = chooseBlanks(si);
    const box = $("#clozeLine");
    box.replaceChildren();
    seg.words.forEach((w, i) => {
      if (st.blanks.includes(i)) {
        const inp = document.createElement("input");
        inp.dataset.i = i;
        inp.size = Math.max(10, w.w.length); // the same width for every word up to 10 letters, so the gap gives nothing away
        inp.autocomplete = "off"; inp.spellcheck = false; inp.setAttribute("autocapitalize", "off");
        box.append(inp);
      } else box.append(w.w);
      box.append(" ");
    });
    box.hidden = false;
    $("#answer").hidden = true;
  } else {
    $("#clozeLine").hidden = true;
    $("#answer").hidden = false;
  }
  renderCost();
  renderMap();
  focusInput();
  if (autoplay) doPlay();
}
function focusInput() {
  const el = st.mode === "cloze" ? $("#clozeLine input") : $("#answer");
  el?.focus();
}
function next() {
  // next line you haven't got perfect yet
  for (let k = st.li + 1; k < st.lines.length; k++) {
    if ((st.prog.r[st.lines[k]] ?? 0) < 1) return goTo(k);
  }
  toast("You've reached the end of the episode. ¡Bravo!", "levelup", 4000);
}

$("#hintBtn").onclick = () => {
  if (st.checked || st.hinted) return;
  st.hinted = true;
  $("#hintBtn").disabled = true;
  renderCost();
  const words = st.T.segments[st.lines[st.li]].words;
  if (st.mode === "cloze") {
    for (const inp of document.querySelectorAll("#clozeLine input")) {
      if (!inp.value) inp.placeholder = words[+inp.dataset.i].w.replace(/^[¿¡]/, "")[0] + "…";
    }
  } else {
    const sk = $("#skeleton");
    sk.innerHTML = words
      .map((w) => {
        const bare = w.w.replace(/[^\p{L}']/gu, "");
        return `<span>${esc(bare[0] || "")}${"_".repeat(Math.max(0, bare.length - 1))}</span>`;
      })
      .join("");
    sk.hidden = false;
  }
  focusInput();
};


function check() {
  if (st.checked) return;
  if (st.plays + st.slows === 0) return toast("Listen first: press Play or Tab");
  const si = st.lines[st.li];
  const words = st.T.segments[si].words;
  let html, pts, acc, accentMiss;
  if (st.mode === "cloze") {
    const typed = Object.fromEntries([...document.querySelectorAll("#clozeLine input")].map((x) => [x.dataset.i, x.value.trim()]));
    const r = scoreCloze(words, st.blanks, typed, { names: st.T?.names });
    ({ html, acc, accentMiss } = r);
    pts = r.exact * 15 + r.near * 7 - r.accentMiss * 3;
  } else {
    const r = scoreDictation(words, $("#answer").value, { names: st.T?.names });
    ({ acc, accentMiss } = r);
    pts = r.exact * 10 + r.near * 5 - r.accentMiss * 2;
    html = r.html + `<span class="you">You typed: ${esc(r.typed || "(nothing)")}</span>`;
  }

  st.checked = true;
  // so "text doesn't match audio" can undo this line's effects
  st.undo = { G: { ...G }, r: st.prog.r[si] };
  const perfect = acc >= 1;
  const mult = multiplier() * comboMult();
  const gain = Math.round(pts * mult);
  const before = levelOf(G.xp).level;
  rollDay();
  G.xp += gain;
  G.todayCount++;
  if (G.todayCount === GOAL) {
    G.streak = G.lastGoalDay === yesterday() ? G.streak + 1 : 1;
    G.lastGoalDay = dayStr();
    setTimeout(() => toast(`Daily goal reached. Streak: ${G.streak} ${G.streak === 1 ? "day" : "days"}`, "levelup", 3500), 900);
  }
  if (perfect && st.plays + st.slows === 1 && !st.hinted) G.combo++;
  else if (acc < 0.8) G.combo = 0;
  G.bestCombo = Math.max(G.bestCombo, G.combo);
  store.set("game", G);
  st.prog.r[si] = Math.max(st.prog.r[si] ?? 0, acc);
  store.set("game:" + st.ep, st.prog);

  $("#diff").innerHTML = html;
  $("#gain").textContent = `+${gain}`;
  $("#verdict").textContent =
    perfect ? (st.plays + st.slows === 1 && !st.hinted ? "¡Perfecto! First listen, combo up." : "¡Perfecto!")
    : accentMiss && acc >= 0.9 ? `Casi: every word right, but ${accentMiss === 1 ? "an accent is" : accentMiss + " accents are"} off (dotted words).`
    : acc >= 0.8 ? "Casi. Check the orange and red words."
    : acc >= 0.5 ? "Bien. Hear it again and listen for the red words."
    : "Hard one. Hear it a few times, then add it to your missed lines.";
  $("#result").classList.toggle("perfect", perfect);
  $("#result").hidden = false;
  $("#checkBtn").disabled = true;
  $("#hintBtn").disabled = true;
  $("#missBtn").disabled = false;
  $("#explainBtn").disabled = false;
  $("#ankiBtn").disabled = false;
  renderStats(["xptxt", "combo", "today"]);
  renderMap();
  if (levelOf(G.xp).level > before) setTimeout(() => toast(`Level ${levelOf(G.xp).level}!`, "levelup", 3000), 400);
  $("#nextBtn").focus();
}

// The transcript is wrong for this line: flag it, undo any score, drop it from the game.
async function flagCurrent() {
  const li = st.li, si = st.lines[li];
  document.querySelectorAll(".flagBtn").forEach((b) => (b.disabled = true));
  try {
    await flagLine(st.ep, si);
  } catch (e) {
    document.querySelectorAll(".flagBtn").forEach((b) => (b.disabled = false));
    return toast(e.message);
  }
  audio.pause();
  if (st.checked && st.undo) {
    Object.assign(G, st.undo.G);
    store.set("game", G);
    if (st.undo.r == null) delete st.prog.r[si]; else st.prog.r[si] = st.undo.r;
  }
  st.T.segments[si].flagged = true;
  st.lines.splice(li, 1);
  store.set("game:" + st.ep, st.prog);
  renderStats();
  toast("Flagged. It's out of the games, and marked ⚑ in Listen so you can fix it.", "", 3500);
  goTo(Math.min(li, st.lines.length - 1));
}
document.querySelectorAll(".flagBtn").forEach((b) => (b.onclick = flagCurrent));

$("#checkBtn").onclick = check;
$("#nextBtn").onclick = next;
$("#skipBtn").onclick = () => { audio.pause(); next(); };
$("#playLine").onclick = () => { doPlay(false); focusInput(); };
$("#slowLine").onclick = () => { doPlay(true); focusInput(); };
$("#againBtn").onclick = () => playLine(1);
$("#missBtn").onclick = async () => {
  const si = st.lines[st.li], s = st.T.segments[si];
  try {
    await api("api/saved", { method: "POST", body: { episode: st.ep, kind: "hard", start: s.start, end: s.end, text: s.text } });
    $("#missBtn").disabled = true;
    toast("Added to missed lines (see Saved in Listen)");
  } catch (e) { toast(e.message); }
};
const contextOf = (si) => st.T.segments.slice(Math.max(0, si - 3), si + 4).map((s) => s.text).join(" ");
function showExplanation(text) {
  st.explanation = text;
  $("#explainOut").hidden = false;
  $("#explainOut").innerHTML = md(text);
  $("#explainBtn").disabled = true;
}
$("#explainBtn").onclick = async () => {
  const li = st.li, si = st.lines[li];
  const out = $("#explainOut");
  out.hidden = false;
  out.textContent = "Asking Claude…";
  $("#explainBtn").disabled = true;
  try {
    const { explanation } = await api("api/explain", { method: "POST", body: { text: st.T.segments[si].text, context: contextOf(si) } });
    if (st.li === li) showExplanation(explanation);
  } catch (e) { out.textContent = e.message; $("#explainBtn").disabled = false; }
};
// Anki card: audio of the line on the front; text + Claude's explanation on the back
// (the server looks it up if we don't have one yet).
$("#ankiBtn").onclick = async () => {
  const li = st.li, si = st.lines[li], s = st.T.segments[si];
  const btn = $("#ankiBtn");
  btn.disabled = true;
  if (!st.explanation) toast("Looking it up, then adding to Anki…", "", 15000);
  try {
    const { explanation } = await api("api/anki", {
      method: "POST",
      body: { episode: st.ep, start: s.start, end: s.end, text: s.text, context: contextOf(si), explanation: st.explanation },
    });
    if (st.li === li) {
      if (explanation && !st.explanation) showExplanation(explanation);
      btn.textContent = "Added to Anki";
    }
    toast("Added to Anki");
  } catch (e) {
    toast(e.message, "", 4000);
    if (st.li === li) btn.disabled = false;
  }
};

for (const b of document.querySelectorAll(".modes button")) {
  b.onclick = () => {
    st.mode = b.dataset.mode;
    store.set("gameMode", st.mode);
    document.querySelectorAll(".modes button").forEach((x) => x.setAttribute("aria-checked", x === b));
    goTo(st.li, false);
  };
}

document.addEventListener("keydown", (e) => {
  if (e.key === "Tab") {
    e.preventDefault();
    // in the blanks, Tab goes to the next one (Shift+Tab back); past the last one it plays the line again
    if (e.target.matches("#clozeLine input")) {
      const ins = [...document.querySelectorAll("#clozeLine input")], k = ins.indexOf(e.target) + (e.shiftKey ? -1 : 1);
      if (ins[k]) return ins[k].focus();
    }
    doPlay(e.shiftKey);
    return;
  }
  if (e.key === "Enter" && !e.shiftKey) {
    if (e.target.closest("button")) return; // let the focused button handle it
    e.preventDefault();
    if (!st.checked) {
      // in cloze, Enter moves to the next gap before checking
      if (st.mode === "cloze" && e.target.matches("#clozeLine input")) {
        const ins = [...document.querySelectorAll("#clozeLine input")];
        const k = ins.indexOf(e.target);
        if (k < ins.length - 1) return ins[k + 1].focus();
      }
      check();
    } else next();
  }
});

// ---------- boot ----------
(async function boot() {
  rollDay();
  renderStats();
  const eps = await api("api/episodes");
  if (!eps.length) return toast("No episodes yet");
  const want = new URLSearchParams(location.search).get("ep") || store.get("lastEp", null);
  st.ep = eps.some((e) => e.id === want) ? want : eps[0].id;
  store.set("lastEp", st.ep);
  $("#listenLink").href = `./?ep=${encodeURIComponent(st.ep)}`;
  $("#rpgLink").href = `rpg.html?ep=${encodeURIComponent(st.ep)}`;
  st.T = await (await fetch(`media/${encodeURIComponent(st.ep)}/transcript.json`, { cache: "no-cache" })).json();
  audio.src = `media/${encodeURIComponent(st.ep)}/audio.mp3`;
  st.lines = st.T.segments.map((s, i) => (playable(s) ? i : -1)).filter((i) => i >= 0);
  st.prog = store.get("game:" + st.ep, { pos: 0, r: {} });
  document.querySelectorAll(".modes button").forEach((x) => x.setAttribute("aria-checked", x.dataset.mode === st.mode));
  goTo(st.prog.pos || 0, false);
})();
