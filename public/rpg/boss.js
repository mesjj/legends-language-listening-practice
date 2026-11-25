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

// ---------- the boss leaping out of the screen, and the final blow (like the streak dice's show) ----------
// Both copy the boss's picture off the stage into a layer over the whole page, blow it up to most of
// the screen and play it there; the layer lets clicks and keys through and removes itself.
function bossCopy(stage) { return artCopy(stage?.querySelector(".foe.t-boss .foeart")); }
function artCopy(art, fit = 1) {
  if (!art) return null;
  const r = art.getBoundingClientRect();
  if (!r.width || !r.height) return null;
  const k = Math.min((innerWidth * 0.82 * fit) / r.width, (innerHeight * 0.7 * fit) / r.height, 6);
  const dx = innerWidth / 2 - (r.left + r.width / 2), dy = innerHeight / 2 - (r.top + r.height / 2);
  const box = document.createElement("div");
  box.className = "bl-boss";
  box.style.cssText = `left:${r.left}px;top:${r.top}px;width:${r.width}px;height:${r.height}px`;
  box.innerHTML = art.innerHTML;
  return { box, k, dx, dy };
}
function layer(cls, color) {
  const el = document.createElement("div");
  el.className = `bossleap ${cls}`;
  el.style.setProperty("--bc", color);
  el.setAttribute("aria-hidden", "true");
  document.body.append(el);
  return el;
}
const shakeFrames = (k, dx, dy) => [0, 1, 2, 3, 4, 5].map((i) => ({ transform: `translate(${dx + (i % 2 ? 9 : -9) * (1 - i / 6)}px, ${dy + (i % 3 - 1) * 6}px) scale(${k})` }));

// It hits you: it leaps at you, huge, and falls back. `big` for its signature attack, with the name.
export function bossLeap(stage, { color = "#e04030", name = "", big = false } = {}) {
  if (reduced()) return Promise.resolve();
  const c = bossCopy(stage);
  if (!c) return Promise.resolve();
  const L = layer(`leap${big ? " big" : ""}`, color);
  L.append(c.box);
  if (name) L.insertAdjacentHTML("beforeend", `<div class="bl-name">${esc(name)}</div>`);
  const ms = big ? 1700 : 1000, k = c.k * (big ? 1 : 0.85);
  L.animate([{ opacity: 0 }, { opacity: 1, offset: 0.2 }, { opacity: 1, offset: 0.75 }, { opacity: 0 }], { duration: ms, fill: "forwards" });
  c.box.animate([
    { transform: "translate(0, 0) scale(1)", filter: "brightness(1)" },
    { transform: `translate(${c.dx}px, ${c.dy}px) scale(${k * 1.18})`, filter: "brightness(1.6)", offset: 0.28 },
    { transform: `translate(${c.dx}px, ${c.dy}px) scale(${k})`, filter: "brightness(1)", offset: 0.4 },
    { transform: `translate(${c.dx}px, ${c.dy}px) scale(${k})`, offset: 0.7 },
    { transform: "translate(0, 0) scale(1)", opacity: 0 },
  ], { duration: ms, easing: "cubic-bezier(.3, .7, .3, 1)", fill: "forwards" });
  setTimeout(() => {
    if (!L.isConnected) return;
    L.insertAdjacentHTML("beforeend", `<i class="bl-flash"></i><i class="bl-crack"></i>`);
    L.animate([{ transform: "translate(0,0)" }, { transform: "translate(-14px, 8px)" }, { transform: "translate(12px, -8px)" }, { transform: "translate(-8px, 5px)" }, { transform: "translate(0,0)" }], { duration: 380 });
  }, ms * 0.28);
  return new Promise((ok) => setTimeout(() => { L.remove(); ok(); }, ms + 50));
}

// The killing blow on a boss: it's brought up huge, two great cuts cross the screen in your hit's colour,
// it flashes white and shakes, and splits along the cut while shards fly; the halves fall away.
export function bossFinisher(stage, { color = "#fff", bossColor = "#e04030" } = {}) {
  if (reduced()) return Promise.resolve();
  const c = bossCopy(stage);
  if (!c) return Promise.resolve();
  const L = layer("finish", bossColor);
  L.style.setProperty("--hc", color);
  L.append(c.box);
  L.insertAdjacentHTML("beforeend", `<div class="bl-name final">¡Golpe final!</div>`);
  const at = `translate(${c.dx}px, ${c.dy}px) scale(${c.k})`;
  L.animate([{ opacity: 0 }, { opacity: 1, offset: 0.12 }, { opacity: 1, offset: 0.85 }, { opacity: 0 }], { duration: 2700, fill: "forwards" });
  c.box.animate([{ transform: "translate(0, 0) scale(1)" }, { transform: at }], { duration: 450, easing: "cubic-bezier(.2, 1.3, .4, 1)", fill: "forwards" });
  // the two cuts
  setTimeout(() => {
    if (!L.isConnected) return;
    L.insertAdjacentHTML("beforeend", `<i class="bl-cut a"></i><i class="bl-cut b"></i>`);
  }, 650);
  // the flash, the shake, white-hot
  setTimeout(() => {
    if (!L.isConnected) return;
    L.insertAdjacentHTML("beforeend", `<i class="bl-flash white"></i>`);
    c.box.animate([...shakeFrames(c.k, c.dx, c.dy).map((f, i) => ({ ...f, filter: `brightness(${i % 2 ? 4 : 1.5}) saturate(${i % 2 ? 0 : 1})` })), { transform: at, filter: "brightness(3) saturate(0)" }], { duration: 450, fill: "forwards" });
  }, 900);
  // the split: two copies of the boss, each clipped to one side of the cut, falling apart
  setTimeout(() => {
    if (!L.isConnected) return;
    const halves = [["polygon(0 0, 100% 0, 100% 38%, 0 62%)", -1, [160, -110]], ["polygon(0 62%, 100% 38%, 100% 100%, 0 100%)", 1, [-150, 200]]];
    for (const [clip, s, [mx, my]] of halves) {
      const h = c.box.cloneNode(true);
      h.getAnimations?.().forEach((a) => a.cancel());
      h.style.clipPath = clip;
      L.append(h);
      h.animate([{ transform: at, filter: "brightness(2.5)", opacity: 1 },
        { transform: `translate(${c.dx + mx * 0.35}px, ${c.dy + my * 0.35}px) scale(${c.k}) rotate(${s * -4}deg)`, filter: "brightness(1.6)", opacity: 1, offset: 0.25 },
        { transform: `translate(${c.dx + mx}px, ${c.dy + my + 120}px) scale(${c.k}) rotate(${s * -16}deg)`, filter: "brightness(.8)", opacity: 0 }],
        { duration: 1250, easing: "cubic-bezier(.2, .6, .6, 1)", fill: "forwards" });
    }
    c.box.remove();
    for (let i = 0; i < 70; i++) {
      const p = document.createElement("i");
      const a = Math.random() * Math.PI * 2, d = 160 + Math.random() * Math.max(innerWidth, innerHeight) * 0.45;
      p.className = `bl-shard${i % 3 ? "" : " hot"}`;
      p.style.cssText = `--dx:${Math.cos(a) * d}px;--dy:${Math.sin(a) * d}px;--r:${Math.random() * 720}deg;animation-delay:${Math.random() * 0.12}s`;
      L.append(p);
    }
  }, 1350);
  return new Promise((ok) => setTimeout(() => { L.remove(); ok(); }, 2750));
}

// A critical hit or a huge one (yours): the monster you hit blown up mid-screen, a cut of light across it in
// the hit's colour, a flash and a jolt, and the damage in giant numbers under the word.
export function bigHit(art, { color = "#fff", label = "¡Crítico!", num = 0 } = {}) {
  if (reduced()) return Promise.resolve();
  const c = artCopy(art, 0.85);
  if (!c) return Promise.resolve();
  const L = layer("crit", color);
  L.style.setProperty("--hc", color);
  L.append(c.box);
  L.insertAdjacentHTML("beforeend", `<div class="bl-name crit">${esc(label)}</div><div class="bl-num">${num}</div><i class="bl-cut a"></i><i class="bl-flash white"></i>`);
  const at = `translate(${c.dx}px, ${c.dy}px) scale(${c.k})`;
  L.animate([{ opacity: 0 }, { opacity: 1, offset: 0.12 }, { opacity: 1, offset: 0.75 }, { opacity: 0 }], { duration: 1150, fill: "forwards" });
  c.box.animate([{ transform: "translate(0, 0) scale(1)" }, { transform: at, offset: 0.25, filter: "brightness(3) saturate(0)" },
    ...shakeFrames(c.k, c.dx, c.dy).map((f, i) => ({ ...f, offset: 0.3 + i * 0.05, filter: `brightness(${i % 2 ? 2 : 1})`, opacity: 1 })),
    { transform: at, opacity: 1, offset: 0.78 },
    { transform: `translate(${c.dx + 60}px, ${c.dy}px) scale(${c.k * 0.9}) rotate(8deg)`, opacity: 0 }], { duration: 1150, fill: "forwards" });
  L.animate([{ transform: "translate(0,0)" }, { transform: "translate(-12px, 6px)" }, { transform: "translate(10px, -6px)" }, { transform: "translate(-6px, 4px)" }, { transform: "translate(0,0)" }], { duration: 360, delay: 200 });
  return new Promise((ok) => setTimeout(() => { L.remove(); ok(); }, 1180));
}
// A heavy blow on you: the screen goes red, cracks across it like glass, and the damage shakes there huge.
export function bigHurt({ num = 0, color = "#e02a1a" } = {}) {
  if (reduced()) return Promise.resolve();
  const L = layer("hurt", color);
  const cracks = Array.from({ length: 9 }, (_, i) => {
    const a = i * 40 + Math.random() * 25;
    return `<i class="bl-glass" style="--a:${a}deg;--l:${30 + Math.random() * 45}vmax"></i>`;
  }).join("");
  L.innerHTML = `${cracks}<div class="bl-num hurt">−${num}</div><i class="bl-flash"></i>`;
  L.animate([{ opacity: 0 }, { opacity: 1, offset: 0.08 }, { opacity: 1, offset: 0.7 }, { opacity: 0 }], { duration: 1100, fill: "forwards" });
  L.animate([{ transform: "translate(0,0)" }, { transform: "translate(16px, -10px)" }, { transform: "translate(-14px, 9px)" }, { transform: "translate(9px, -5px)" }, { transform: "translate(-4px, 2px)" }, { transform: "translate(0,0)" }], { duration: 450 });
  return new Promise((ok) => setTimeout(() => { L.remove(); ok(); }, 1120));
}
