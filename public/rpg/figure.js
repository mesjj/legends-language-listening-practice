// The player's figure and the item icons, from the LPC pixel art built by scripts/build_lpc.py.
// The figure is the class's body plus one layer stack per equipped item, drawn in z order;
// each item's look depends on its rarity (or its set, or which unique it is).
// Set and unique pieces glow, uniques shimmer, and the three top rarities (ancestral, legendario, mítico) have looks of their own and glow brighter.
import { RARITY, BASE, SETS } from "./data.js";
import { lookLayers, fixLook } from "./look.js";

// the character's look (body, skin, hair ...; see look.js), made valid; old characters get their class's
export const lookOfChar = (ch) => fixLook(ch.look, ch.cls);
const SLOTS = ["head", "body", "hands", "feet", "belt", "neck"];
let A = null, W = 0, H = 0, IW = 0, IH = 0, MW = 0, MH = 0;
// The sheets are read once and kept in memory (blob URLs) for as long as the page is open: if new
// art is published while you play, the page goes on drawing from the sheets that match its index,
// instead of fetching the new ones and cutting them up with the old rectangles (blank items).
const SRC = { atlas: "rpg/lpc/atlas.png", icons: "rpg/lpc/icons.png", monsters: "rpg/lpc/monsters.png" };
async function keep(url) {
  try { const r = await fetch(url, { cache: "no-cache" }); if (r.ok) return URL.createObjectURL(await r.blob()); } catch {}
  return url;
}

export async function loadFigure() {
  if (A) return;
  A = await (await fetch("rpg/lpc/atlas.json", { cache: "no-cache" })).json();
  const [a, i, m] = await Promise.all([keep(SRC.atlas), keep(SRC.icons), keep(SRC.monsters)]);
  SRC.atlas = a; SRC.icons = i; SRC.monsters = m;
  const size = (src) => new Promise((ok) => { const im = new Image(); im.onload = () => ok([im.naturalWidth, im.naturalHeight]); im.onerror = () => ok([0, 0]); im.src = src; });
  [[W, H], [IW, IH], [MW, MH]] = await Promise.all([size(SRC.atlas), size(SRC.icons), size(SRC.monsters)]);
}

// the look for an item: its unique, then its set, then its rarity, then plain
function styles(it) {
  const s = [];
  if (it.set || it.setShirt) s.push(it.set || it.setShirt); // a set piece's own art (and a set undershirt's icon, in the set's colours), where it has some (the top-tier sets' icons are drawn by hand)
  if (it.tunjo) s.push(`t:${it.tunjo}`, "tunjo", "mitico"); // the tunjo's rainbow items: drawn each (scripts/tunjo_art.py)
  if (TOP_GLOW[it.rarity]) s.push(it.rarity, "unique"); // the three top rarities: their own look, always
  if (it.rarity === "unique") s.push(`u:${it.name}`, "unique");
  // crafted and runeword items borrow the rare look; reinforced/ancestral bases use their root's art
  s.push(["set", "crafted", "runeword"].includes(it.rarity) ? "rare" : it.rarity, "normal");
  return s;
}
const root = (it) => it.look || BASE[it.base]?.root || it.base; // a rainbow item wears its own shape, whatever base its stats are on
// The slots the figure draws, and the set's piece for each (rings aren't drawn).
export const SHOW_SLOTS = ["head", "body", "hands", "feet", "belt", "neck", "weapon", "off"];
export function setPieceFor(set, sl) {
  const p = set?.pieces.find((q) => BASE[q.base]?.slot === sl);
  return p && { base: p.base, rarity: set.tier || "set", set: set.id, name: p.name };
}
// With a set's undershirt on, what each slot shows: "set" (the set's piece), "real" (what's really
// worn there) or "none" (nothing), chosen on the shirt (it.show, by slot). By default the set's piece
// where the set has one, and what's really worn elsewhere. (it.hide, older: set pieces unticked by name.)
export function shirtChoice(shirt, set, sl) {
  const piece = setPieceFor(set, sl);
  const c = shirt?.show?.[sl] ?? (piece && shirt?.hide?.includes(piece.name) ? "real" : piece ? "set" : "real");
  return c === "set" && !piece ? "real" : c;
}
// What the figure wears, as [slot, item]. A two-handed weapon and a shield that can't go together:
// the set's piece wins, and between two real ones (which can't happen) the weapon.
export function shownGear(ch) {
  const w = `weapon${ch.swap}`, o = `off${ch.swap}`;
  const g = Object.fromEntries([...SLOTS.filter((k) => k !== "shirt"), w, o].map((k) => [k, ch.equip[k]]));
  const shirt = ch.equip.shirt, set = shirt?.setShirt && SETS.find((x) => x.id === shirt.setShirt);
  if (set) {
    const keyOf = { weapon: w, off: o }, from = {};
    for (const sl of SHOW_SLOTS) {
      const k = keyOf[sl] || sl, c = shirtChoice(shirt, set, sl);
      from[sl] = c;
      if (c === "none") g[k] = null;
      else if (c === "set") g[k] = setPieceFor(set, sl);
    }
    const two = g[w] && BASE[g[w].base]?.twoHanded;
    if (two && g[o]) {
      if (from.off === "set" && from.weapon !== "set") g[w] = null;
      else g[o] = null;
    }
  }
  return Object.entries(g);
}
// which glow an item gets: set and unique as before; the top rarities brighter, the mythic one pulsing
const TOP_GLOW = { ancestral: 1, legendario: 1, mitico: 1, tunjo: 1 };
const glowOf = (it) => (it.rarity === "unique" || it.rarity === "set" || TOP_GLOW[it.rarity] ? `lpc-${it.rarity}` : "");
function lookOf(it, body) {
  for (const st of styles(it)) {
    const L = A.looks[`item:${root(it)}:${st}:${body}`];
    if (L?.length) return L;
  }
  return null;
}
// The ornaments of the three top-tier sets (original art, scripts/custom_art.py): the Laguna's gold dust, the Cóndor's wings,
// the Origen's rings of sound. Worn with any piece of the set; fuller with the whole set on.
const ORNAMENTS = { laguna: 1, condor: 1, origen: 1, cienaga: 1, mohan: 1, yogui: 1, vajra: 1, averno: 1, trueno: 1, sol: 1, guardian: 1, bachue: 1, nevado: 1, vientos: 1, montana: 1, kalachakra: 1, luzclara: 1, osario: 1, tairona: 1, dorado: 1, relampago: 1, vigilia: 1, pacto: 1, firmamento: 1, madreagua: 1, caiman: 1, andes: 1, arhuaco: 1, galeon: 1, frailejon: 1, bochica: 1, bufeo: 1, llanero: 1, madremonte: 1, silbon: 1, tunda: 1, mahamudra: 1, candileja: 1, sombreron: 1, marimba: 1, huitaca: 1, canocristales: 1, dzogchen: 1 };
function ornamentKeys(ch) {
  const worn = shownGear(ch).map(([, it]) => it).filter(Boolean);
  const out = [];
  for (const s of SETS) {
    if (!ORNAMENTS[s.id]) continue;
    const n = worn.filter((it) => it.set === s.id).length;
    if (n) out.push(`orn:${s.id}:${n >= s.pieces.length ? "full" : "part"}`);
  }
  return out;
}

// atlas cells are 128px with the 64px character in the middle, so a cell is drawn at (-32,-32)
const frame = ([f]) => {
  const c = A.frame, x = (f % A.cols) * c, y = Math.floor(f / A.cols) * c, o = (64 - c) / 2;
  return `<svg x="${o}" y="${o}" width="${c}" height="${c}" viewBox="${x} ${y} ${c} ${c}"><image href="${SRC.atlas}" width="${W}" height="${H}"/></svg>`;
};
const reduced = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
function defs() {
  const glow = (id, color, anim, strong) => `<filter id="${id}" x="-30%" y="-30%" width="160%" height="160%">
    <feDropShadow dx="0" dy="0" stdDeviation="${strong ? 1 : 0.7}" flood-color="${color}" flood-opacity=".95">
      ${anim && !reduced() ? `<animate attributeName="stdDeviation" values="${strong ? "0.6;2;0.6" : "0.5;1.3;0.5"}" dur="${strong ? "1.8s" : "2.6s"}" repeatCount="indefinite"/>` : ""}
    </feDropShadow></filter>`;
  // The glow filters live once, in a tiny svg on the page that is never hidden. (Every picture used to
  // carry its own copies under the same ids: the browser takes the first copy in the page, and when
  // that one sat in a closed panel, every glowing item drew as nothing, though its tooltip still worked.)
  if (typeof document !== "undefined" && !document.getElementById("lpc-glows")) {
    const box = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    box.id = "lpc-glows";
    box.setAttribute("aria-hidden", "true");
    box.setAttribute("style", "position:absolute;width:0;height:0;overflow:hidden;pointer-events:none");
    box.innerHTML = `<defs>${glow("lpc-set", RARITY.set.color)}${glow("lpc-unique", RARITY.unique.color, true)}${glow("lpc-ancestral", RARITY.ancestral.color, true)}${glow("lpc-legendario", RARITY.legendario.color, true)}${glow("lpc-mitico", RARITY.mitico.color, true, true)}${glow("lpc-tunjo", "#fff2c4", true, true)}</defs>`;
    document.body.prepend(box);
  }
  return "";
}

// still: no glows (their animated filters are costly where many figures share a page, as on the Camisetas shelf)
export function figureSvg(ch, { cls = "", still = false } = {}) {
  if (!A) return `<div class="portrait ${cls}"></div>`;
  const look = lookOfChar(ch), body = look.body;
  const mine = lookLayers(look);
  // the look's parts, from their recoloured sheets (standing frame); without them, the class's old figure
  const parts = mine.length ? mine.filter((p) => p.rows.idle).map((p) => ({ z: p.z, html: () => {
    const [y, fs] = p.rows.idle, o = (64 - fs) / 2;
    return `<svg x="${o}" y="${o}" width="${fs}" height="${fs}" viewBox="0 ${y} ${fs} ${fs}"><image href="${p.url()}" width="${p.canvas.width}" height="${p.canvas.height}"/></svg>`;
  } })) : (A.looks[`class:${ch.cls}`] || []).map((l) => ({ z: l[1], html: () => frame(l) }));
  for (const [, it] of shownGear(ch)) {
    if (!it) continue;
    const L = lookOf(it, body);
    const glow = still ? "" : glowOf(it);
    if (L) for (const l of L) parts.push({ z: l[1], html: () => frame(l), glow });
  }
  for (const k of ornamentKeys(ch)) for (const l of A.looks[k] || []) parts.push({ z: l[1], html: () => frame(l) });
  parts.sort((a, b) => a.z - b.z);
  const layers = parts.map(({ html, glow }) => (glow ? `<g filter="url(#${glow})">${html()}</g>` : html())).join("");
  return `<svg class="portrait lpc ${cls}" viewBox="8 6 48 58" overflow="hidden" role="img" aria-label="${ch.name}" shape-rendering="crispEdges">
    ${defs()}<ellipse cx="32" cy="61.5" rx="12" ry="2.2" fill="rgba(0,0,0,.45)"/>${layers}</svg>`;
}

// An item's icon, cropped from its own layers, or null when there's none (potions, gems, some bases).
export function itemIconSvg(it, cls = "", { still = false } = {}) {
  if (!A || !it.base) return null;
  for (const st of styles(it)) {
    const r = A.icons[`item:${root(it)}:${st}`];
    if (!r) continue;
    const [x, y, w, h] = r;
    const glow = !still && glowOf(it) ? ` filter="url(#${glowOf(it)})"` : "";
    // the inner svg crops the icon sheet to exactly this icon; the outer one scales it to the box
    const m = 1.5;
    return `<svg class="ico px ${cls}" viewBox="${-m} ${-m} ${w + 2 * m} ${h + 2 * m}" aria-hidden="true">${glow ? defs() : ""}<g${glow}>
      <svg width="${w}" height="${h}" viewBox="${x} ${y} ${w} ${h}"><image href="${SRC.icons}" width="${IW}" height="${IH}"/></svg></g></svg>`;
  }
  return null;
}

// A monster's picture, or null if it has none. Drawn at a fixed pixel scale (px per art pixel) so a
// bat stays smaller than a bear; `box` caps the size. Easy-mode cousins carry their own extra scale.
export function monsterSvg(kind, { px = 2, box = 96, cls = "" } = {}) {
  const r = A?.monsters?.[kind];
  if (!r) return null;
  const [x, y, w, h, k = 1] = r;
  const s = Math.min(px * k, box / Math.max(w, h));
  return `<svg class="mon px ${cls}" width="${Math.round(w * s)}" height="${Math.round(h * s)}" viewBox="${x} ${y} ${w} ${h}" aria-hidden="true">
    <image href="${SRC.monsters}" width="${MW}" height="${MH}"/></svg>`;
}

// ---------- the fighting figure ----------
// A canvas of the same layers in motion: built from rpg/lpc/anim.json, one sheet per look with a
// row per animation (idle facing you, side facing the monsters, slash, thrust, shoot, spellcast, hurt).
let AN = null;
const sheetCache = {};
export async function loadAnims() {
  if (AN) return AN;
  try { AN = await (await fetch("rpg/lpc/anim.json")).json(); } catch { AN = null; }
  return AN;
}
const sheet = (f) => (sheetCache[f] ||= new Promise((ok) => {
  const im = new Image(); im.onload = () => ok(im); im.onerror = () => ok(null); im.src = `rpg/lpc/anim/${f}.png`;
}));
function animKey(it, body) {
  for (const st of styles(it)) { const k = `item:${root(it)}:${st}:${body}`; if (AN.looks[k]) return k; }
  return null;
}
// What the figure attacks with: a weapon's own move (bows shoot, spears thrust, wands cast), else a swing.
export function attackAnim(ch) {
  const w = Object.fromEntries(shownGear(ch))[`weapon${ch.swap}`];
  return (w && AN?.attack[root(w)]) || "slash";
}
// the part of the 64px frame that's drawn: room in front for swings and behind for nothing much
const VX0 = 8, VY0 = -14, VW0 = 104, VH0 = 78;
// On horseback: the horse (64×61) stands at (HX, HY) in frame pixels, the rider sits on it in the
// generator's "ride" frame. Moves are drawn standing above the waist (CUT), nudged RDX forward to the
// seated torso, over the seated legs; a layer with no seated frame (most weapons) is drawn whole.
const HX = 6, HY = 30, CUT = 45, RDX = 3;
const RIDE_VIEW = { fight: [4, 2, 104, 90], doll: [2, 6, 72, 86] };
export const ridingMount = (ch) => (AN?.anims?.ride && ch.mount && ch.mounts?.includes(ch.mount) ? ch.mount : null);
const GLOW = { tunjo: RARITY.tunjo.color, unique: RARITY.unique.color, set: RARITY.set.color, ancestral: RARITY.ancestral.color, legendario: RARITY.legendario.color, mitico: RARITY.mitico.color };

export function fightFigure(ch, { scale = 2.5, centered = false } = {}) {
  if (!AN) return null;
  // centered: the body in the middle of the canvas (the inventory), instead of room in front for swings
  const mount = ridingMount(ch);
  const [VX, VY, VW, VH] = mount ? RIDE_VIEW[centered ? "doll" : "fight"] : centered ? [5, 6, 54, 58] : [VX0, VY0, VW0, VH0];
  const look = lookOfChar(ch), body = look.body;
  const mine = lookLayers(look);
  const keys = mine.length ? [] : [{ k: `class:${ch.cls}` }];
  for (const [slot, it] of shownGear(ch)) {
    const k = it && animKey(it, body);
    if (k) keys.push({ k, glow: GLOW[it.rarity], held: !SLOTS.includes(slot) });
  }
  for (const k of ornamentKeys(ch)) if (AN.looks[k]) keys.push({ k });
  const cv = document.createElement("canvas");
  cv.width = VW; cv.height = VH;
  cv.className = "fightfig";
  cv.style.width = `${VW * scale}px`;
  cv.setAttribute("role", "img");
  cv.setAttribute("aria-label", ch.name);
  const g = cv.getContext("2d");
  let layers = [], anim = "idle", frame = 0, timer = null, done = null, horse = null;
  const put = (L, a, f, dx = 0, clip = null) => {
    const [y, fs, n] = L.rows[a], o = (64 - fs) / 2;
    f = Math.min(f, n - 1);
    g.shadowColor = L.glow || "transparent"; g.shadowBlur = L.glow ? 1.4 : 0;
    if (clip) { g.save(); g.beginPath(); g.rect(0, clip[0] - VY, VW, clip[1] - clip[0]); g.clip(); }
    g.drawImage(L.img, f * fs, y, fs, fs, o - VX + dx, o - VY, fs, fs);
    if (clip) g.restore();
  };
  const drawRiding = () => {
    g.fillStyle = "rgba(0,0,0,.45)";
    g.beginPath(); g.ellipse(HX + 32 - VX, HY + 59.5 - VY, 26, 2.6, 0, 0, 7); g.fill();
    if (horse) g.drawImage(horse, HX - VX, HY - VY);
    // hurt (falling over) and the turn to the side don't apply up there: just sit
    const move = anim !== "idle" && anim !== "side" && anim !== "hurt" ? anim : null;
    for (const L of layers) {
      if (!L.img) continue;
      const seat = L.rows.ride, act = move && L.rows[move];
      // weapons and shields are drawn whole; clothes with no seated frame only above the waist
      const upper = L.held ? null : [-999, CUT];
      if (move && act && L.held) put(L, move, frame, RDX);
      else if (move && act) {
        if (seat) put(L, "ride", 0, 0, [CUT, 999]);
        put(L, move, frame, RDX, [-999, CUT]);
      } else if (seat) put(L, "ride", 0);
      else if (L.rows.side) put(L, "side", 0, RDX, upper);
    }
  };
  const draw = () => {
    g.clearRect(0, 0, VW, VH);
    if (mount) return drawRiding();
    g.fillStyle = "rgba(0,0,0,.45)";
    g.beginPath(); g.ellipse(32 - VX, 61.5 - VY, 12, 2.2, 0, 0, 7); g.fill();
    for (const L of layers) {
      const r = L.rows[anim];
      if (!r || !L.img) continue;
      const [y, fs, n] = r, f = Math.min(frame, n - 1), o = (64 - fs) / 2;
      g.shadowColor = L.glow || "transparent"; g.shadowBlur = L.glow ? 1.4 : 0; // blur ≈ 2σ: the same 0.7 glow as the portrait (figureSvg)
      g.drawImage(L.img, f * fs, y, fs, fs, o - VX, o - VY, fs, fs);
    }
  };
  const horseReady = mount ? new Promise((ok) => { const im = new Image(); im.onload = () => { horse = im; ok(); }; im.onerror = () => ok(); im.src = `rpg/lpc/companions/mount-${mount}.png`; }) : null;
  const ready = Promise.all([...keys.map(async ({ k, glow, held }) => {
    const look = AN.looks[k];
    const img = await sheet(look.f);
    return look.l.map(([z, rows]) => ({ z, rows, img, glow, held }));
  }), horseReady]).then(([...ls]) => { ls = ls.filter(Boolean); layers = [...mine.map((p) => ({ z: p.z, rows: p.rows, img: p.canvas })), ...ls.flat()].sort((a, b) => a.z - b.z); draw(); });
  const stop = () => { clearInterval(timer); timer = null; done?.(); done = null; };
  return {
    el: cv, ready, riding: mount, vw: VW,
    // play an animation; resolves when it ends. hold: stay on the last frame (dying).
    // Attacks turn side-on first and stay side-on a moment after, then face the viewer again.
    play(name, { ms = 75, hold = false, frames } = {}) {
      stop();
      const n = frames ?? AN.anims[name] ?? 1;
      if (matchMedia("(prefers-reduced-motion: reduce)").matches) { if (hold) { anim = name; frame = n - 1; draw(); } return Promise.resolve(); }
      const turn = name !== "hurt" && name !== "idle" && AN.anims.side;
      const seq = [...(turn ? [["side", 0]] : []), ...Array.from({ length: n }, (_, i) => [name, i]), ...(turn && !hold ? [["side", 0], ["side", 0]] : [])];
      let k = 0;
      [anim, frame] = seq[0]; draw();
      return new Promise((ok) => {
        done = ok;
        timer = setInterval(() => {
          k++;
          if (k >= seq.length) {
            if (!hold) { anim = "idle"; frame = 0; }
            draw(); stop(); return;
          }
          [anim, frame] = seq[k]; draw();
        }, ms);
      });
    },
    idle() { stop(); anim = "idle"; frame = 0; draw(); },
    // step through [anim, frame] pairs, ms apart, and stay on the last one
    steps(seq, ms = 140) {
      stop();
      let k = 0;
      [anim, frame] = seq[0]; draw();
      return new Promise((ok) => {
        done = ok;
        timer = setInterval(() => {
          if (++k >= seq.length) return stop();
          [anim, frame] = seq[k]; draw();
        }, ms);
      });
    },
    stop,
  };
}

// The inventory figure, alive: it holds a stance for a few seconds, then moves slowly into the next:
// facing you, turned to one side or the other, the weapon raised ready (from its attack's frames).
// Returns a function that stops it.
const READY = { slash: 2, thrust: 3, shoot: 8, spellcast: 3 }; // the frame of each attack that reads as "ready"
export function stanceLoop(fig, ch) {
  if (!fig || !AN || matchMedia("(prefers-reduced-motion: reduce)").matches) return () => {};
  const atk = attackAnim(ch), k = Math.min(READY[atk] ?? 2, (AN.anims[atk] || 1) - 1);
  const up = Array.from({ length: k + 1 }, (_, i) => [atk, i]);
  const flip = (on) => { fig.el.style.transform = on ? "scaleX(-1)" : ""; };
  const stances = [
    async () => { flip(false); await fig.steps([["idle", 0]]); },
    async () => { flip(false); await fig.steps([["side", 0]]); },
    async () => { flip(false); await fig.steps([["side", 0], ...up], 160); },
    async () => { flip(true); await fig.steps([["side", 0]]); },
    async () => { flip(true); await fig.steps([["side", 0], ...up], 160); },
  ];
  let alive = true, last = 0, t = null;
  const next = async () => {
    if (!alive) return;
    if (fig.el.isConnected && fig.el.offsetParent) {
      // back to facing you between two side stances half the time, so it doesn't spin around
      let i;
      do i = Math.floor(Math.random() * stances.length); while (i === last);
      if (last && i && Math.random() < 0.5) { await stances[0](); await new Promise((r) => (t = setTimeout(r, 900))); }
      if (!alive) return;
      last = i;
      await stances[i]();
    }
    t = setTimeout(next, 2600 + Math.random() * 2400);
  };
  t = setTimeout(next, 2200);
  return () => { alive = false; clearTimeout(t); fig.stop(); };
}
