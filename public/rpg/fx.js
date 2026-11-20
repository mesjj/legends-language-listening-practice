// Fight effects drawn over the stage: swings, thrusts, arrows, spell bolts, bursts and shakes.
// All short (well under a second) and skipped when the system asks for reduced motion.
export const reduced = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
export const wait = (ms) => new Promise((r) => setTimeout(r, reduced() ? 0 : ms));

export function layerOf(stage) { return layer(stage); }
function layer(stage) {
  let L = stage.querySelector(":scope > .fxlayer");
  if (!L) { L = document.createElement("div"); L.className = "fxlayer"; stage.append(L); }
  return L;
}
// a point on an element, in stage coordinates (fx, fy: fractions of its box)
export function pointOn(el, stage, fx = 0.5, fy = 0.45) {
  const a = el.getBoundingClientRect(), s = stage.getBoundingClientRect();
  return { x: a.left - s.left + a.width * fx, y: a.top - s.top + a.height * fy };
}
function put(stage, html, { x, y }) {
  const d = document.createElement("div");
  d.className = "fx";
  d.style.left = `${x}px`; d.style.top = `${y}px`;
  d.innerHTML = html;
  layer(stage).append(d);
  return d;
}
const gone = (el, ms) => setTimeout(() => el.remove(), ms);

// A sword's arc across the target.
export function slash(stage, at, color = "#fff", big = false) {
  if (reduced()) return;
  const s = big ? 1.35 : 1;
  const d = put(stage, `<svg class="fx-slash" width="${120 * s}" height="${120 * s}" viewBox="-60 -60 120 120">
      <path d="M -40 -38 Q 18 -18 34 42" pathLength="100" stroke="${color}" stroke-width="7" fill="none" stroke-linecap="round"/>
      <path d="M -40 -38 Q 18 -18 34 42" pathLength="100" stroke="#fff" stroke-width="2.5" fill="none" stroke-linecap="round"/></svg>`, at);
  gone(d, 420);
}
// A spear's jab: a streak driving into the target from the left.
export function thrust(stage, at, color = "#fff", big = false) {
  if (reduced()) return;
  const d = put(stage, `<i class="fx-thrust" style="--c:${color};--w:${big ? 130 : 96}px"></i>`, at);
  gone(d, 380);
}
// Something flying from a to b: an arrow, a sling stone or a spell bolt. Resolves on arrival.
export async function projectile(stage, a, b, kind = "arrow", color = "#fff", ms = 220) {
  if (reduced()) return;
  const ang = Math.atan2(b.y - a.y, b.x - a.x);
  const html = kind === "bolt" ? `<i class="fx-bolt" style="--c:${color}"></i>`
    : kind === "stone" ? `<i class="fx-stone"></i>` : `<i class="fx-arrow" style="--c:${color}"></i>`;
  const d = put(stage, html, a);
  const tr = (p) => `translate(${p.x - a.x}px, ${p.y - a.y}px) rotate(${ang}rad)`;
  await d.animate([{ transform: tr(a) }, { transform: tr(b) }], { duration: ms, easing: "cubic-bezier(.3,.1,.8,.6)" }).finished.catch(() => {});
  d.remove();
}
// A burst of the hit's colour on impact; bigger, with sparks, on a critical.
export function burst(stage, at, color = "#fff", big = false) {
  if (reduced()) return;
  const sparks = big ? Array.from({ length: 8 }, (_, i) => `<b style="--a:${i * 45 + 10}deg"></b>`).join("") : "";
  const d = put(stage, `<span class="fx-burst ${big ? "big" : ""}" style="--c:${color}">${sparks}</span>`, at);
  gone(d, 600);
}
// The whole stage jolts, with a white flash, for a critical or perfect hit.
export function shake(stage) {
  if (reduced()) return;
  stage.classList.remove("shake"); void stage.offsetWidth; stage.classList.add("shake");
  const f = document.createElement("div");
  f.className = "fx-flash";
  layer(stage).append(f);
  gone(f, 380);
  setTimeout(() => stage.classList.remove("shake"), 400);
}
// Restart a CSS animation class on an element.
export function pulse(el, cls, ms = 600) {
  if (!el || reduced()) return;
  el.classList.remove(cls); void el.offsetWidth; el.classList.add(cls);
  setTimeout(() => el.classList.remove(cls), ms);
}
// A column of light where something good fell (or over you, for a caught rune).
export function beam(stage, at, color = "#f0d25c", ms = 1600) {
  const d = put(stage, `<i class="fx-beam" style="--c:${color};--ms:${reduced() ? 1 : ms}ms"></i>`, at);
  gone(d, reduced() ? 900 : ms);
}
