// The player's look: body, skin, face, hair, beard and clothes, chosen in the character editor.
// The parts come from rpg/lpc/look.json (built by scripts/build_looks.py) in LPC's base colours,
// and are recoloured here with the LPC palettes: one canvas per part and colour, kept for reuse.

let L = null;
export async function loadLook() {
  if (L) return L;
  try { L = await (await fetch("rpg/lpc/look.json")).json(); } catch { L = null; }
  return L;
}
export const lookData = () => L;

// what each class looked like before there was a choice
const DEFAULTS = {
  guerrero: { body: "male", skin: "light", head: "human_male", face: "neutral", eyes: "blue", brows: null, nose: null, ears: null, wrinkles: null,
    hair: "plain", beard: "beard", stache: null, hairColor: "dark_brown", shirt: "longsleeve", shirtColor: "white", legs: "pants", legsColor: "brown" },
  cazadora: { body: "female", skin: "olive", head: "human_female", face: "neutral", eyes: "blue", brows: null, nose: null, ears: null, wrinkles: null,
    hair: "ponytail", beard: null, stache: null, hairColor: "black", shirt: "longsleeve", shirtColor: "tan", legs: "pants", legsColor: "forest" },
  chaman: { body: "male", skin: "brown", head: "human_male", face: "neutral", eyes: "blue", brows: null, nose: null, ears: null, wrinkles: null,
    hair: "long", beard: null, stache: null, hairColor: "black", shirt: "sleeveless", shirtColor: "white", legs: "pants", legsColor: "tan" },
  brujo: { body: "male", skin: "light", head: "human_male", face: "neutral", eyes: "blue", brows: null, nose: null, ears: null, wrinkles: null,
    hair: "long", beard: "beard", stache: null, hairColor: "gray", shirt: "longsleeve", shirtColor: "purple", legs: "pants", legsColor: "charcoal" },
};
export const defaultLook = (cls) => ({ ...(DEFAULTS[cls] || DEFAULTS.guerrero) });
// the colour each part takes: skin for the body and head, hair colour for hair, beard and brows ...
const COLOR_OF = { body: "skin", eye: "eyes" };

export const slot = (id) => L?.slots.find((s) => s.id === id);
export const opt = (sid, id) => slot(sid)?.opts.find((o) => o.id === id);
const headKind = (look) => opt("head", look.head)?.kind || "male";
// which sheet an option uses for this look (faces follow the head's shape, the rest the body)
export const variantOf = (sid, look) => (sid === "face" ? headKind(look) : look.body);
export const fits = (sid, o, look) => sid === "body" || !!o.k[variantOf(sid, look)];

// a look with every choice valid for its body (a blouse on a male body becomes a shirt, and so on)
export function fixLook(look, cls) {
  const d = defaultLook(cls), out = { ...d, ...(look || {}) };
  if (!L) return out;
  for (const S of L.slots) {
    const cur = S.opts.find((o) => o.id === out[S.id]);
    if (out[S.id] == null && S.none) continue;
    if (!cur || !fits(S.id, cur, out)) out[S.id] = S.opts.find((o) => o.id === d[S.id] && fits(S.id, o, out))?.id ?? (S.none ? null : S.opts.find((o) => fits(S.id, o, out))?.id);
  }
  for (const [mat, key] of [["body", "skin"], ["eye", "eyes"], ["hair", "hairColor"], ["cloth", "shirtColor"], ["cloth", "legsColor"]])
    if (!L.pal[mat].c[out[key]]) out[key] = d[key];
  return out;
}

// colour maps: LPC base ramp -> chosen ramp, with off-by-one neighbours as in the build's recolor()
const rgb = (h) => { const n = parseInt(h.replace("#", ""), 16); return [n >> 16, (n >> 8) & 255, n & 255]; };
function rampMap(mat, name, m = new Map(), from = null) {
  const P = L.pal[mat], to = P.c[name];
  if (!to) return m;
  (from || P.base).forEach((src, i) => {
    const [r, g, b] = rgb(src), d = rgb(to[i]);
    for (let dr = -1; dr <= 1; dr++) for (let dg = -1; dg <= 1; dg++) for (let db = -1; db <= 1; db++) {
      const k = ((r + dr) << 16) | ((g + dg) << 8) | (b + db);
      if (!m.has(k)) m.set(k, d);
    }
  });
  return m;
}

const imgCache = {}, tinted = new Map();
const loadImg = (f) => (imgCache[f] ||= new Promise((ok) => {
  const im = new Image(); im.onload = () => ok(im); im.onerror = () => ok(null); im.src = `rpg/lpc/look/${f}.png`;
}));
function tint(im, colors) {
  const cv = document.createElement("canvas");
  cv.width = im.naturalWidth; cv.height = im.naturalHeight;
  const g = cv.getContext("2d");
  g.drawImage(im, 0, 0);
  let m = new Map();
  for (const [mat, name, from] of colors) m = rampMap(mat, name, m, from);
  if (m.size) {
    const d = g.getImageData(0, 0, cv.width, cv.height), p = d.data;
    for (let i = 0; i < p.length; i += 4) {
      if (!p[i + 3]) continue;
      const t = m.get((p[i] << 16) | (p[i + 1] << 8) | p[i + 2]);
      if (t) { p[i] = t[0]; p[i + 1] = t[1]; p[i + 2] = t[2]; }
    }
    g.putImageData(d, 0, 0);
  }
  return cv;
}

// The layers of a look: [{ key, z, rows, colors }] (before loading)
function plan(look) {
  const out = [];
  for (const S of L.slots) {
    const o = S.opts.find((x) => x.id === look[S.id]);
    if (!o) continue;
    // items that come in ready-made colours (blouse, tunic ...) aren't recoloured: take the colour's own sheet
    const ready = o.v && (o.v[look[S.color]] || o.v.white || Object.values(o.v)[0]);
    const k = (ready || o.k)[variantOf(S.id, look)];
    const part = k && L.looks[k];
    if (!part) continue;
    const colors = ready ? [] : S.mats.map((mat) => [mat, look[S.color || COLOR_OF[mat]], o.src?.[mat]]);
    for (const [z, rows] of part.l) out.push({ f: part.f, z, rows, colors, id: `${part.f}|${colors.flat().join(",")}` });
  }
  return out;
}
// Load and recolour what a look needs; afterwards lookLayers() has it all.
export async function prepareLook(look) {
  if (!L) return;
  await Promise.all(plan(look).map(async (p) => {
    if (tinted.has(p.id)) return;
    const im = await loadImg(p.f);
    if (im && !tinted.has(p.id)) { const cv = tint(im, p.colors); tinted.set(p.id, { cv, url: null }); }
  }));
}
// [{ z, rows, canvas, url() }] for the parts that are ready (all of them after prepareLook)
export function lookLayers(look) {
  if (!L) return [];
  return plan(look).filter((p) => tinted.has(p.id)).map((p) => {
    const t = tinted.get(p.id);
    return { z: p.z, rows: p.rows, canvas: t.cv, url: () => (t.url ||= t.cv.toDataURL()) };
  });
}
export function randomLook(cls) {
  const pick = (a) => a[Math.floor(Math.random() * a.length)];
  const look = { body: pick(["male", "female"]) };
  look.head = pick(slot("head").opts.filter((o) => o.kind !== "elderly" || Math.random() < 0.3)).id;
  const chance = { nose: 0.35, ears: 0.12, wrinkles: 0.1, brows: 0.5, beard: look.body === "male" ? 0.45 : 0.03, stache: look.body === "male" ? 0.3 : 0.02, shirt: 0.95, hair: 0.92 };
  for (const S of L.slots) {
    if (S.id === "head" || S.id === "body") continue;
    const ok = S.opts.filter((o) => fits(S.id, o, look));
    look[S.id] = S.none && Math.random() > (chance[S.id] ?? 1) ? null : S.id === "face" && Math.random() < 0.6 ? "neutral" : pick(ok).id;
  }
  const human = ["light", "amber", "olive", "taupe", "bronze", "brown", "black"];
  look.skin = pick(human);
  look.eyes = pick(["brown", "brown", "brown", "blue", "green", "gray"]);
  look.hairColor = pick(["black", "raven", "dark_brown", "chestnut", "light_brown", "sandy", "blonde", "gray", "white", "ginger", "redhead"]);
  const cloth = Object.keys(L.pal.cloth.c);
  look.shirtColor = pick(cloth); look.legsColor = pick(cloth);
  return fixLook(look, cls);
}
