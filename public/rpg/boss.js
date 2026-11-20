// How the bosses look: their animated art (rpg/bosses, drawn by scripts/build_bosses.py), the bar across the
// top of the stage (name, life, the meter of its signature attack), the entrance, and the big words that
// cross the stage when something happens. The rules are in main.js (bossTurn, bossPhase2).
import { esc } from "../listen-core.js";
import { BOSSES } from "./data.js";
import { reduced } from "./fx.js";

let ART = null;
export async function loadBossArt() {
  if (ART) return ART;
  try { ART = await (await fetch("rpg/bosses/bosses.json")).json(); } catch { ART = {}; }
  return ART;
}
export const hasBossArt = (kind) => !!ART?.[kind];

// The boss standing on the stage: an 8-frame loop, the second row once it has changed.
export function bossSprite(kind, phase2 = false) {
  const a = ART?.[kind];
  if (!a) return "";
  const [w, h, n] = a;
  return `<span class="bsprite b-${kind}" style="--w:${w};--h:${h};--n:${n};--row:${phase2 ? 1 : 0};background-image:url(rpg/bosses/${kind}.png)"></span>`;
}

// The meter of its signature attack: one mark per turn until it lets go (the Silbón's are the notes of his scale).
export function specialMeter(kind, B, every) {
  const sp = BOSSES[kind].special;
  const marks = Array.from({ length: every }, (_, i) => `<i class="${i < B.charge ? "on" : ""}">${sp.notes ? sp.notes[Math.round((i * (sp.notes.length - 1)) / Math.max(1, every - 1))] : ""}</i>`).join("");
  return `<span class="bb-special${B.armed ? " armed" : ""}${sp.notes ? " notes" : ""}">
    <span class="bb-sname">${esc(sp.name)}</span><span class="bb-marks">${marks}</span>
    ${B.armed ? `<span class="bb-warn">¡Ahora! Solo una frase perfecta</span>` : ""}</span>`;
}

// The entrance: the stage goes dark around the boss, its name lands, a line about it. Click, a key or
// a few seconds to start. Resolves when it's gone.
export function bossIntro(stage, kind, onSound) {
  const def = BOSSES[kind];
  return new Promise((done) => {
    if (!stage) return done();
    const foe = stage.querySelector(".foe.t-boss .foeart"), s = stage.getBoundingClientRect();
    const r = foe?.getBoundingClientRect();
    const x = r ? r.left - s.left + r.width / 2 : s.width * 0.6, y = r ? r.top - s.top + r.height * 0.45 : s.height * 0.5;
    const el = document.createElement("div");
    el.className = "bossintro";
    // the words go in the room to the left of the boss
    const room = r ? Math.max(200, r.left - s.left - s.width * 0.05 - 24) : s.width * 0.48;
    el.style.cssText = `--bc:${def.color};--x:${x}px;--y:${y}px;--room:${Math.round(room)}px`;
    el.innerHTML = `<div class="bi-text"><p class="bi-title">${esc(def.title)}</p><h2 class="bi-name">${esc(def.name)}</h2>
      <p class="bi-line">${esc(def.intro)}</p><p class="bi-go">Pulsa cualquier tecla para luchar</p></div>`;
    stage.append(el);
    stage.classList.add("intro-on");
    onSound?.();
    let over = false;
    const end = () => {
      if (over) return;
      over = true;
      removeEventListener("keydown", key, true);
      el.classList.add("out");
      stage.classList.remove("intro-on");
      setTimeout(() => el.remove(), reduced() ? 0 : 450);
      done();
    };
    const key = (e) => { if (["Shift", "Control", "Alt", "Meta"].includes(e.key)) return; e.preventDefault(); e.stopPropagation(); end(); };
    el.addEventListener("click", end);
    addEventListener("keydown", key, true);
    setTimeout(end, reduced() ? 2600 : 4200);
  });
}

// Big words across the stage: the special coming, landing or missed; the second phase.
export function bossShout(stage, html, cls = "", color = "#fff", ms = 1800) {
  if (!stage) return;
  stage.querySelectorAll(".bshout").forEach((n) => n.remove());
  const el = document.createElement("div");
  el.className = `bshout ${cls}`;
  el.style.setProperty("--bc", color);
  el.style.setProperty("--ms", `${ms}ms`);
  el.innerHTML = html;
  stage.append(el);
  setTimeout(() => el.remove(), ms);
}
