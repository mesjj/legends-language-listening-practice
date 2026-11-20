// El Bestiario: the rules. No DOM here, so it can be tested with node.
import { SPECIES, MOVES, AREAS, ITEMS, typeMult } from "./data.js";

export const rnd = (a, b) => a + Math.floor(Math.random() * (b - a + 1));
export const pick = (a) => a[Math.floor(Math.random() * a.length)];
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
let n = 0;
export const uid = () => `${Date.now().toString(36)}${(n++).toString(36)}${Math.random().toString(36).slice(2, 6)}`;

// ---------- creatures ----------
export const xpFor = (lvl) => Math.round(lvl ** 3 * 0.8); // total xp to reach lvl
export function stats(c) {
  const [hp, atk, def, spd] = SPECIES[c.sp].base, L = c.lvl;
  return { maxHp: Math.floor((2 * hp * L) / 100) + L + 10, atk: Math.floor((2 * atk * L) / 100) + 5, def: Math.floor((2 * def * L) / 100) + 5, spd: Math.floor((2 * spd * L) / 100) + 5 };
}
export function makeCreature(sp, lvl, { shiny } = {}) {
  const c = { uid: uid(), sp, lvl, xp: xpFor(lvl), shiny: shiny ?? Math.random() < 1 / 100 };
  c.hp = stats(c).maxHp;
  return c;
}
export const nameOf = (c) => SPECIES[c.sp].name;
// What it knows at its level: the quick move of Monte and of each of its types from the start,
// its first type's strong move at 8 and total at 18, its second type's strong at 12. At most 4, newest kept.
export function movesOf(c) {
  const [t1, t2] = SPECIES[c.sp].types, L = c.lvl, out = [];
  out.push(t1 === "monte" ? "monte-hueco" : `${t1}-hueco`);
  if (t1 !== "monte") out.unshift("monte-hueco");
  if (t2) out.push(`${t2}-hueco`);
  if (L >= 8) out.push(`${t1}-huecos`);
  if (t2 && L >= 12) out.push(`${t2}-huecos`);
  if (L >= 18) out.push(`${t1}-dictado`);
  return [...new Set(out)].slice(-4).map((id) => MOVES[id]);
}
export function learnedAt(c, lvl) {
  const before = new Set(movesOf({ ...c, lvl: lvl - 1 }).map((m) => m.id));
  return movesOf({ ...c, lvl }).filter((m) => !before.has(m.id));
}

// ---------- fighting ----------
// acc: how well the exercise was written (0..1). Under half, it misses; perfect hits a bit harder.
export function accFactor(acc) {
  if (acc == null) return 1; // the foe doesn't write
  if (acc < 0.5) return 0;
  return acc >= 1 ? 1.2 : 0.4 + 0.6 * acc;
}
export function damage(att, def, move, acc) {
  const A = stats(att), D = stats(def), f = accFactor(acc);
  if (!f) return { dmg: 0, miss: true, eff: 1 };
  const stab = SPECIES[att.sp].types.includes(move.type) ? 1.25 : 1;
  const eff = typeMult(move.type, SPECIES[def.sp].types);
  const base = ((((2 * att.lvl) / 5 + 2) * move.power * A.atk) / D.def) / 50 + 2;
  const dmg = Math.max(1, Math.round(base * stab * eff * f * (0.85 + Math.random() * 0.15)));
  return { dmg, eff, perfect: acc >= 1 };
}
// The foe's turn: its best-looking move, now and then a random one.
export function foeMove(foe, target) {
  const ms = movesOf(foe);
  if (Math.random() < 0.3) return pick(ms);
  return ms.map((m) => [m, m.power * typeMult(m.type, SPECIES[target.sp].types) * (SPECIES[foe.sp].types.includes(m.type) ? 1.25 : 1)]).sort((a, b) => b[1] - a[1])[0][0];
}
export const FOE_SOFTEN = 0.8; // the foe doesn't have to listen: it hits a little softer

// Catching: weaker and rarer helps, so does a better totuma and a better answer.
export function catchChance(c, ball, acc) {
  if (acc < 0.6) return 0;
  const S = stats(c), sp = SPECIES[c.sp];
  const hpPart = (3 * S.maxHp - 2 * c.hp) / (3 * S.maxHp);
  const p = (hpPart * sp.rate * ITEMS[ball].ball) / 255 * (acc >= 1 ? 1.25 : 0.6 + 0.4 * acc);
  return clamp(p + (sp.legend ? 0 : 0.03), 0, 1);
}

// ---------- growing ----------
export function xpGain(foe, trainer) {
  const b = SPECIES[foe.sp].base.reduce((a, x) => a + x, 0);
  return Math.round(((b / 4) * foe.lvl) / 5 * 1.5 * (trainer ? 1.5 : 1));
}
// Adds xp; returns the levels gained (each with any new moves) and an evolution, if due.
export function addXp(c, xp) {
  const out = { levels: [], evolve: null };
  c.xp += xp;
  while (c.lvl < 100 && c.xp >= xpFor(c.lvl + 1)) {
    const before = stats(c).maxHp;
    c.lvl++;
    c.hp += stats(c).maxHp - before; // what it grows, it heals
    out.levels.push({ lvl: c.lvl, learned: learnedAt(c, c.lvl) });
  }
  const evo = SPECIES[c.sp].evo;
  if (evo && c.lvl >= evo[1]) out.evolve = evo[0];
  return out;
}
export function evolve(c, into) {
  const before = stats(c).maxHp;
  c.sp = into;
  c.hp = clamp(c.hp + stats(c).maxHp - before, 1, stats(c).maxHp);
}

// ---------- the wild ----------
export function wildFor(area) {
  // the old stories of a place come out about once in 60 encounters, a little above the place's best
  if (area.legend && Math.random() < 1 / 60) {
    const sp = area.legend2 && Math.random() < 0.5 ? area.legend2 : area.legend;
    return makeCreature(sp, area.lvl[1] + 3);
  }
  const tot = area.wild.reduce((a, [, w]) => a + w, 0);
  let r = Math.random() * tot, sp = area.wild[0][0];
  for (const [s, w] of area.wild) { if ((r -= w) < 0) { sp = s; break; } }
  return makeCreature(sp, rnd(area.lvl[0], area.lvl[1]));
}
export const areaById = (id) => AREAS.find((a) => a.id === id);
// A place is open once the guardian of the one before has been beaten.
export const areaOpen = (save, i) => i === 0 || !!save.beaten[AREAS[i - 1].id];

export function newSave(name, starter) {
  const first = makeCreature(starter, 5, { shiny: false });
  return { v: 1, name, pesos: 1500, team: [first], corral: [], bag: { totuma: 5, panela: 3 },
    dex: { seen: { [starter]: 1 }, caught: { [starter]: 1 } }, beaten: {}, created: Date.now(), stats: { battles: 0, caught: 1, lines: 0, perfect: 0 } };
}
export const healAll = (save) => { for (const c of [...save.team, ...save.corral]) c.hp = stats(c).maxHp; };
