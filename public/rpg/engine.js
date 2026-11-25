// Leyendas: rules. Item generation, character stats, monsters, combat maths, saving.
import {
  RARITY, PROPS, BASES, BASE, BANDS, PREFIXES, SUFFIXES, RARE_A, RARE_B, UNIQUES, SETS, GEMS, GEM_GRADES,
  POTIONS, POTION_TIER_NAMES, CLASSES, MONSTERS, BOSSES, MONSTER_MODS, RANDOM_MODS, UNIQUE_MONSTER_NAMES, ZONES,
  DIFFICULTY, EASY_ROSTER, LISTENING_MODS, MONSTER_RES, CRAFT, RUNE, UNIQUE_OWNERS, UNIQUE_TITLES, UNIQUE_FLAVORS, TOP_NAMES, TOP_FLAVORS, TIERS, SPELLS, PETS, MOUNTS, MOUNT_PROPS, POWERS, RUNAS, RUNA, RUNA_TIERS, RUNA_SETS,
} from "./data.js";
export { DIFFICULTY };
export const diffOf = (ch) => DIFFICULTY[ch.difficulty || "medio"];

export const rnd = (a, b) => a + Math.floor(Math.random() * (b - a + 1));
export const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];
const chance = (p) => Math.random() < p;
const uid = () => Math.random().toString(36).slice(2, 10);
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

// ---------- items ----------
const gendered = (name, g) => name.replace(/@/g, g === "f" ? "a" : "o");
function slotGroup(base) { return base.slot === "ring" || base.slot === "neck" ? base.slot : base.slot; }

function rollAffix(list, base, ilvl, taken) {
  const ok = list.filter((a) => a.slots.includes(slotGroup(base)) && a.tiers[0][0] <= ilvl && !taken.has(a.prop));
  if (!ok.length) return null;
  const a = pick(ok);
  const tiers = a.tiers.filter((t) => t[0] <= ilvl);
  // usually the best tier you qualify for, sometimes one lower
  const t = tiers.length > 1 && chance(0.35) ? tiers[tiers.length - 2] : tiers[tiers.length - 1];
  taken.add(a.prop);
  return { name: a.name, prop: a.prop, value: rnd(t[1], t[2]) };
}

function basesFor(ilvl, slot) {
  return BASES.filter((b) => b.lvl <= ilvl && (!slot || b.slot === slot));
}
// Prefer bases near the item level so drops keep up with you.
// How often each slot drops when none is asked for: the shares from when every slot had its first
// bases, so adding more kinds of boots doesn't make rings rarer.
const SLOT_SHARE = { weapon: 23, off: 5, head: 6, body: 5, hands: 3, feet: 4, belt: 3, neck: 2, ring: 2 };
export const RETIRE_AT = 60; // item level from which only the high bands' designs drop
function pickBase(ilvl, slot) {
  if (!slot) {
    const open = Object.keys(SLOT_SHARE).filter((s) => basesFor(Math.max(1, ilvl), s).length);
    slot = pick(open.flatMap((s) => Array(SLOT_SHARE[s]).fill(s)));
  }
  let list = basesFor(Math.max(1, ilvl), slot);
  // From RETIRE_AT the ordinary designs (and their reinforced and ancestral versions) stop dropping:
  // only the high bands' (and jewellery, which has none). Below it, from the first band, they're half as likely.
  if (ilvl >= RETIRE_AT && list.some((b) => b.band)) list = list.filter((b) => b.band || b.jewel);
  const old = ilvl >= BANDS[0].lvl ? 0.5 : 1;
  // bases far below the item level (30+) fade to a fifth, so the high bands' designs show up past 50
  // (and the bands' own pieces count double: fewer kinds of them)
  const w = list.map((b) => Math.max(ilvl - b.lvl >= 30 ? 0.2 : 1, 6 - Math.floor((ilvl - b.lvl) / 6)) * (b.band ? 2 : b.jewel ? 1 : old));
  let x = Math.random() * w.reduce((a, b) => a + b, 0);
  for (let i = 0; i < list.length; i++) if ((x -= w[i]) < 0) return list[i];
  return list[list.length - 1];
}

function rollRange(v) { return Array.isArray(v) ? rnd(v[0], v[1]) : v; }

// Sockets above plain: [chance of any, fewest, most to start, chance of each one more]. Up to 5 (and
// the base's own most) in every tier, each extra socket rarer the higher the tier: a 5-socket mythic is
// about one in a thousand of the mythics that could hold five.
const SOCK = {
  magic: [0.25, 1, 1, 0.4], rare: [0.15, 1, 1, 0.3], unique: [0.15, 1, 1, 0.25], set: [0.15, 1, 1, 0.25],
  ancestral: [0.5, 1, 1, 0.25], legendario: [1, 1, 1, 0.2], mitico: [1, 1, 2, 0.12],
};
// A plain (white) item's sockets: from 1 to its base's most; at that most, now and then one more, and
// rarely two (never past 6): a base of 4 gets 5 about 3% and 6 about 0.4% of the time, a base of 5 gets 6 about 2%.
export function plainSockets(base) {
  const cap = base.sockets || 0;
  if (!cap) return 0;
  let n = rnd(1, cap);
  if (n === cap && cap >= 4 && n < 6 && chance(0.12)) { n++; if (n < 6 && chance(0.12)) n++; }
  return n;
}
function sockRoll(rarity, base) {
  const S = SOCK[rarity], cap = Math.min(5, base.sockets || 0);
  if (!S || !cap || !chance(S[0])) return 0;
  let n = rnd(S[1], S[2]);
  while (n < cap && chance(S[3])) n++;
  return Math.min(n, cap);
}
export function makeItem(baseId, rarity, ilvl, extra = {}, { fullRare = false } = {}) {
  const base = BASE[baseId];
  const it = { id: uid(), base: baseId, rarity, ilvl, props: {}, sockets: 0, gems: [], ...extra };
  if (base.def) it.def = rnd(base.def[0], base.def[1]);
  if (base.props) for (const [k, v] of Object.entries(base.props)) it.props[k] = v;
  if (rarity === "low") it.quality = -25;
  if (rarity === "normal" && chance(0.18)) it.quality = rnd(10, 25); // superior
  // sockets: plain items often, magic ones sometimes, rares rarely
  if (base.sockets) {
    if ((rarity === "normal" || rarity === "low") && chance(0.5)) it.sockets = plainSockets(base);
    else it.sockets = sockRoll(rarity, base);
  }
  if (rarity === "magic") {
    const taken = new Set();
    const p = chance(0.7) ? rollAffix(PREFIXES, base, ilvl, taken) : null;
    const s = !p || chance(0.6) ? rollAffix(SUFFIXES, base, ilvl, taken) : null;
    for (const a of [p, s]) if (a) it.props[a.prop] = (it.props[a.prop] || 0) + a.value;
    it.pre = p?.name; it.suf = s?.name;
  }
  if (rarity === "rare") {
    const taken = new Set();
    const most = ilvl >= 20 ? 6 : 5, n = fullRare ? most : rnd(3, most);
    for (let i = 0; i < n; i++) {
      const a = rollAffix(chance(0.5) ? PREFIXES : SUFFIXES, base, ilvl, taken) || rollAffix(PREFIXES, base, ilvl, taken) || rollAffix(SUFFIXES, base, ilvl, taken);
      if (a) it.props[a.prop] = (it.props[a.prop] || 0) + a.value;
    }
    it.name = `${pick(RARE_A)} ${pick(RARE_B)}`;
  }
  return it;
}

export function makeUnique(u, ilvl) {
  const it = makeItem(u.base, "unique", ilvl);
  it.name = u.name;
  for (const [k, v] of Object.entries(u.props)) it.props[k] = (it.props[k] || 0) + (typeof v === "boolean" ? v : rollRange(v));
  it.flavor = u.flavor;
  return it;
}
// A unique nobody wrote: a random base, a namesake, and more and stronger properties than a rare.
export function makeRandomUnique(ilvl, slot = null) {
  const base = pickBase(ilvl, slot);
  const it = makeItem(base.id, "unique", ilvl);
  it.name = chance(0.75) ? `${BASE[base.root || base.id].name} ${pick(UNIQUE_OWNERS)}` : pick(UNIQUE_TITLES[base.g] || UNIQUE_TITLES.m);
  const taken = new Set();
  const n = rnd(4, ilvl >= 25 ? 6 : 5);
  for (let i = 0; i < n; i++) {
    const a = rollAffix(chance(0.5) ? PREFIXES : SUFFIXES, base, ilvl + 6, taken) || rollAffix(PREFIXES, base, ilvl + 6, taken) || rollAffix(SUFFIXES, base, ilvl + 6, taken);
    if (a) it.props[a.prop] = (it.props[a.prop] || 0) + a.value;
  }
  // one listening property, and the item itself is better made
  const listen = pick(base.slot === "weapon" ? [["dmgDictation", 15, 30], ["dmgCloze", 15, 30], ["comboStart", 1, 2]] : [["replayCost", 10, 25], ["hintCost", 10, 30], ["xp", 3, 8], ["freeReplay", 1, 1]]);
  it.props[listen[0]] = (it.props[listen[0]] || 0) + rnd(listen[1], listen[2]);
  if (base.dmg) it.props.dmgPct = (it.props.dmgPct || 0) + rnd(40, 80);
  if (base.def) it.props.armorPct = (it.props.armorPct || 0) + rnd(40, 80);
  it.flavor = pick(UNIQUE_FLAVORS);
  it.lreq = Math.max(base.lvl, Math.round(ilvl * 0.85));
  return it;
}
// The three rarities above unique: more properties, from deeper tiers, worth more each, and
// better made. Always better than a random unique of the same level.
export const TOP = {
  ancestral:  { n: [5, 6], up: 8,  boost: 1.15, pct: [70, 110],  listen: 1, res: null,     all: null },
  legendario: { n: [6, 7], up: 14, boost: 1.3,  pct: [100, 150], listen: 2, res: [8, 15],  all: null },
  mitico:     { n: [7, 8], up: 20, boost: 1.5,  pct: [150, 210], listen: 2, res: [15, 25], all: [5, 10] },
};
export function makeTopItem(rarity, ilvl, slot = null) {
  // about a third of the time, a piece of the tier's own set, once you're near its level
  const sets = SETS.filter((s) => s.tier === rarity && s.lvl <= ilvl + 4).flatMap((s) => s.pieces.filter((p) => !slot || BASE[p.base].slot === slot).map((p) => [s, p]));
  if (sets.length && chance(0.35)) {
    const [set, piece] = pick(sets);
    // the best-made version of its base you could find at this level, and some of the tier's extras
    const better = BASES.filter((b) => (b.root || b.id) === piece.base && b.lvl <= ilvl).sort((a, b) => b.lvl - a.lvl)[0];
    const it = makeSetItem(set, { ...piece, base: better?.id || piece.base }, ilvl);
    it.rarity = rarity;
    const T = TOP[rarity], base = BASE[it.base], taken = new Set(Object.keys(it.props)), L = ilvl + T.up;
    for (let i = 0, n = T.n[0] - 3; i < n; i++) {
      const a = rollAffix(chance(0.5) ? PREFIXES : SUFFIXES, base, L, taken) || rollAffix(PREFIXES, base, L, taken);
      if (a) it.props[a.prop] = (it.props[a.prop] || 0) + Math.max(1, Math.round(a.value * T.boost));
    }
    if (T.res) it.props.resAll = (it.props.resAll || 0) + rnd(...T.res);
    it.sockets = sockRoll(rarity, base);
    it.flavor = TOP_FLAVORS[rarity];
    return it;
  }
  const T = TOP[rarity], base = pickBase(ilvl, slot);
  const it = makeItem(base.id, rarity, ilvl);
  it.name = `${BASE[base.root || base.id].name} ${pick(TOP_NAMES[rarity])}`;
  const taken = new Set(), L = ilvl + T.up, add = (k, v) => (it.props[k] = (it.props[k] || 0) + v);
  for (let i = 0, n = rnd(...T.n); i < n; i++) {
    const a = rollAffix(chance(0.5) ? PREFIXES : SUFFIXES, base, L, taken) || rollAffix(PREFIXES, base, L, taken) || rollAffix(SUFFIXES, base, L, taken);
    if (a) add(a.prop, Math.max(1, Math.round(a.value * T.boost)));
  }
  const listen = base.slot === "weapon" ? [["dmgDictation", 20, 40], ["dmgCloze", 20, 40], ["comboStart", 1, 3]] : [["replayCost", 15, 30], ["hintCost", 15, 35], ["xp", 5, 10], ["freeReplay", 1, 1]];
  for (const [k, a, b] of listen.sort(() => Math.random() - 0.5).slice(0, T.listen)) add(k, rnd(a, b));
  if (base.dmg) add("dmgPct", rnd(...T.pct));
  if (base.def) add("armorPct", rnd(...T.pct));
  if (T.res) add("resAll", rnd(...T.res));
  if (T.all) add("allStats", rnd(...T.all));
  it.sockets = sockRoll(rarity, base);
  it.flavor = TOP_FLAVORS[rarity];
  it.lreq = Math.max(base.lvl, Math.round(ilvl * 0.85));
  return it;
}
// Alembic: magic item + gem + potion. The gem picks the family, its grade the strength.
function makeCrafted(src, gem) {
  const base = BASE[src.base];
  const it = makeItem(base.id, "crafted", src.ilvl);
  const fam = CRAFT[gem.gem];
  for (const [k, grades] of Object.entries(fam.props)) it.props[k] = (it.props[k] || 0) + rnd(...grades[gem.grade]);
  const taken = new Set(Object.keys(it.props));
  const n = rnd(1, 3);
  for (let i = 0; i < n; i++) {
    const a = rollAffix(chance(0.5) ? PREFIXES : SUFFIXES, base, src.ilvl, taken) || rollAffix(PREFIXES, base, src.ilvl, taken);
    if (a) it.props[a.prop] = (it.props[a.prop] || 0) + a.value;
  }
  it.craft = gem.gem;
  it.name = `${pick(RARE_A)} ${pick(RARE_B)}`;
  return it;
}
export function makeSetItem(set, piece, ilvl) {
  const it = makeItem(piece.base, "set", ilvl);
  it.name = piece.name; it.set = set.id;
  for (const [k, v] of Object.entries(piece.props)) it.props[k] = (it.props[k] || 0) + v;
  return it;
}
export function makeGem(type, grade) {
  return { id: uid(), kind: "gem", gem: type, grade, rarity: "gem" };
}
// The Montón transformer: very rare, used up at the Montón (every 250 perfect gems there: a mythic, a pet or a mount)
export function makeRelic() {
  return { id: uid(), kind: "relic", relic: "transformador", rarity: "relic" };
}
// Gems: how often each kind of monster drops one, and what a drop at a level is worth in perfect gems
// (3 make the next grade: a chip is 1/9 of a perfect, a gem 1/3). The transformer falls about as often as
// 100 perfect gems' worth: in the time the gems for 100 perfects fall, one transformer does.
export const GEM_CHANCE = { normal: 0.04, minion: 0.02, champion: 0.15, unique: 0.3, boss: 0.8 };
const gemGrade = (lvl) => (lvl >= 28 && chance(0.3) ? 2 : lvl >= 12 && chance(0.5) ? 1 : 0);
export const perfectWorth = (lvl) => (lvl >= 28 ? 0.3 + 0.35 / 3 + 0.35 / 9 : lvl >= 12 ? 0.5 / 3 + 0.5 / 9 : 1 / 9);
export const relicChance = (m) => ((GEM_CHANCE[m.tier] || 0) * perfectWorth(m.lvl)) / 100;
export function makePotion(type, tier) {
  return { id: uid(), kind: "potion", potion: type, tier, rarity: "potion" };
}

// Roll the rarity of a drop. mf has diminishing returns for the best tiers.
// good: multiplier on the chance of rare, set and unique (2 for a perfect line with perfect accents)
export function rollRarity(mf, bonus = 1, D = null, good = 1, luck = 1) {
  const r0 = rollRarityRaw(mf, bonus, good, luck);
  // what easy mode holds back falls as plain or magic, in the same proportions as the rest
  if (D?.noTop && (r0 === "unique" || r0 === "set" || TOP[r0])) return plainRoll(mf, bonus);
  if (D?.rareKeep != null && r0 === "rare" && Math.random() > D.rareKeep) return plainRoll(mf, bonus);
  return r0;
}
// Rare, set, unique and the three tiers above grow with the monster, magic find and perfect accents,
// softly (rare + set + unique never past half of a roll). Everything else is plain or magic, and there
// the order is worn (grey) > normal (white) > magic (blue) from an ordinary monster: champions,
// uniques and bosses, a harder difficulty and magic find lean it toward blue.
// luck: a long streak's bonus (streakLuck), multiplying the chance of rare and everything above it.
function rollRarityRaw(mf, bonus, good = 1, luck = 1) {
  // the good roll happens on this share of drops (the rest were always plain), as before
  if (Math.random() >= 0.36 / Math.min(2, Math.max(1, bonus) ** 0.35)) {
    const g = goodRoll(mf, bonus, good, luck);
    if (g) return g;
  }
  return plainRoll(mf, bonus);
}
// The exact chance (in %) of each of the three top tiers per piece of gear, for showing: too rare to simulate.
export function topOdds(mf, bonus = 1, D = null, good = 1) {
  if (D?.noTop) return { mitico: 0, legendario: 0, ancestral: 0 };
  const share = 1 - 0.36 / Math.min(2, Math.max(1, bonus) ** 0.35);
  const eff = (cap) => (mf * cap) / (mf + cap), m = Math.max(0.5, bonus) ** 0.5 * Math.sqrt(good);
  const pa = 0.006 * m * (1 + eff(150) / 100), pl = pa * 0.3, pm = pl * 0.3;
  return { mitico: share * pm * 100, legendario: share * pl * 100, ancestral: share * pa * 100 };
}
function goodRoll(mf, bonus, good, luck) {
  const eff = (cap) => (mf * cap) / (mf + cap);
  const m = Math.max(0.5, bonus) ** 0.5 * Math.sqrt(good);
  let pu = 0.018 * m * (1 + eff(250) / 100);
  let ps = 0.03 * m * (1 + eff(500) / 100);
  let pr = 0.13 * m * (1 + eff(600) / 100);
  const top = pu + ps + pr;
  if (top > 0.5) { const k = 0.5 / top; pu *= k; ps *= k; pr *= k; }
  pu *= luck; ps *= luck; pr *= luck; // the streak's bonus on top, past the cap
  // above unique, each tier about a third of the one below it, and magic find helps them less
  // (a roll of their own, so they don't take anything from the others)
  const pa = 0.006 * m * (1 + eff(150) / 100) * luck, pl = pa * 0.3, pm = pl * 0.3;
  const t = Math.random();
  if (t < pm) return "mitico";
  if (t < pm + pl) return "legendario";
  if (t < pm + pl + pa) return "ancestral";
  const r = Math.random();
  if (r < pu) return "unique";
  if (r < pu + ps) return "set";
  if (r < pu + ps + pr) return "rare";
  return null;
}
// grey : white : blue = 1.55 : 1.2 : 0.95 from an ordinary monster with no magic find (about 37/28/23%
// of all drops); the better the monster, the fewer grey and white; magic find moves some to blue.
function plainRoll(mf, bonus) {
  const b = Math.max(1, bonus), find = mf / (mf + 300); // 0 → 1, a half at 300%
  const w = { low: (1.55 / b ** 0.8) * (1 - 0.3 * find), normal: (1.2 / b ** 0.4) * (1 - 0.1 * find), magic: 0.95 * (1 + 0.35 * find) };
  let r = Math.random() * (w.low + w.normal + w.magic);
  if ((r -= w.low) < 0) return "low";
  if ((r -= w.normal) < 0) return "normal";
  return "magic";
}

export function randomItem(ilvl, mf = 0, bonus = 1, slot = null, D = null, good = 1, force = null, luck = 1) {
  let rarity = force || rollRarity(mf, bonus, D, good, luck);
  if (TOP[rarity]) return makeTopItem(rarity, ilvl, slot);
  if (rarity === "unique") {
    // the hand-written ones first; past those, or one time in three, an invented one
    const list = UNIQUES.filter((u) => u.lvl <= ilvl + 2 && (!slot || BASE[u.base].slot === slot));
    if (list.length && chance(0.66)) return makeUnique(pick(list), ilvl);
    return makeRandomUnique(ilvl, slot);
  }
  if (rarity === "set") {
    const list = SETS.filter((s) => !s.tier && s.lvl <= ilvl + 2).flatMap((s) => s.pieces.filter((p) => !slot || BASE[p.base].slot === slot).map((p) => [s, p]));
    if (list.length) { const [s, p] = pick(list); return makeSetItem(s, p, ilvl); }
    rarity = "rare";
  }
  const base = pickBase(ilvl, slot);
  if (base.jewel && (rarity === "normal" || rarity === "low")) rarity = "magic"; // plain rings aren't a thing
  return makeItem(base.id, rarity, ilvl);
}

// ---------- item display ----------
export function itemName(it) {
  if (it.kind === "runa") return `Runa ${RUNA[it.runa].name}`;
  if (it.kind === "gem") {
    const g = GEMS[it.gem];
    return it.grade === 0 ? `${GEM_GRADES[0]} ${g.name}` : it.grade === 1 ? g.fname : `${g.fname} ${["esmeralda", "amatista"].includes(it.gem) ? "perfecta" : "perfecto"}`;
  }
  if (it.kind === "potion") {
    const p = POTIONS[it.potion];
    return it.potion === "rejuv" ? p.name : `${p.name}${POTION_TIER_NAMES[it.tier] ? " " + POTION_TIER_NAMES[it.tier] : ""}`;
  }
  if (it.kind === "relic") return "Transformador del montón";
  const base = BASE[it.base];
  if (it.unid) return base.name; // its colour still says what it might be
  if (it.name) return it.name;
  if (it.rarity === "magic") return [base.name, it.pre && gendered(it.pre, base.g), it.suf].filter(Boolean).join(" ");
  if (it.quality > 0) return `${base.name} superior`;
  if (it.quality < 0) return `${base.name} ${base.g === "f" ? "gastada" : "gastado"}`;
  return base.name;
}
export function itemColor(it) {
  if (it.kind === "runa") return RUNA_TIERS[RUNA[it.runa].tier].color;
  if (it.kind === "gem") return GEMS[it.gem].shades?.[it.grade] || GEMS[it.gem].color;
  if (it.kind === "potion") return POTIONS[it.potion].color;
  return RARITY[it.rarity].color;
}
export function itemIcon(it) {
  if (it.kind === "gem") return "cut-diamond";
  if (it.kind === "runa") return "rune-stone";
  if (it.kind === "relic") return "crystal-growth";
  if (it.kind === "potion") return POTIONS[it.potion].icon;
  return BASE[it.base].icon;
}
// What one socketed gem gives in an item of this slot (or a rune, in an old save being converted).
export const runaKind = (slot) => (slot === "weapon" ? "w" : slot === "off" ? "o" : "a");
export function socketEffect(s, slot) {
  if (s.runa) { const [prop, value] = RUNA[s.runa][runaKind(slot)]; return { prop, value }; }
  if (s.rune) {
    const r = RUNE[s.rune];
    const [prop, value] = r[slot === "weapon" ? "weapon" : slot === "off" ? "off" : "armor"];
    return { prop, value };
  }
  return gemEffect(s.gem, s.grade, slot);
}
export function gemEffect(gem, grade, slot) {
  const g = GEMS[gem];
  const where = slot === "weapon" ? "weapon" : slot === "off" ? "off" : "armor";
  const [prop, vals] = g[where];
  return { prop, value: vals[grade] };
}
export const PROP_ORDER = (k) => PROPS[k]?.order ?? 99;
export function propText(prop, v) {
  const p = PROPS[prop];
  if (!p) return `${prop}: ${v}`;
  if (p.flag) return p.fmt;
  return p.fmt.replace("{v}", v).replace("+-", "−");
}
// All of an item's properties, including socketed gems, merged.
export function itemProps(it) {
  const out = { ...it.props };
  const slot = BASE[it.base]?.slot;
  for (const g of it.gems || []) {
    const e = socketEffect(g, slot);
    out[e.prop] = (out[e.prop] || 0) + e.value;
  }
  const rs = runaSetOf(it);
  if (rs) for (const [k, v] of Object.entries(rs.bonus[runaKind(slot)])) out[k] = (out[k] || 0) + v;
  return out;
}
// Plain items (white) are the ones a rune set wakes up in.
export const isPlain = (it) => !it.kind && (it.rarity === "normal" || it.rarity === "low");
// The rune set complete in this item's sockets, if any (every rune of it, in any order, in a plain item of a kind it fits).
export function runaSetOf(it) {
  if (!isPlain(it) || !it.gems?.length) return null;
  const kind = runaKind(BASE[it.base]?.slot), have = it.gems.filter((g) => g.runa).map((g) => g.runa);
  if (have.length < 2) return null;
  let best = null;
  for (const rs of RUNA_SETS) {
    if (!rs.kinds.includes(kind)) continue;
    const left = [...have];
    if (rs.runas.every((r) => { const i = left.indexOf(r); if (i < 0) return false; left.splice(i, 1); return true; }) && (!best || rs.runas.length > best.runas.length)) best = rs;
  }
  return best;
}
export function makeRuna(id) {
  return { id: uid(), kind: "runa", runa: id, rarity: "runa" };
}
// Runes from monsters: rarely, and which one weighed by tier (RUNA_TIERS.weight), only up to a little above
// the monster's level. A specific high rune is about one in hundreds of thousands of kills.
export const RUNA_CHANCE = { normal: 0.004, minion: 0.002, champion: 0.02, unique: 0.05, boss: 0.35 };
export function pickRuna(lvl) {
  const pool = RUNAS.filter((r) => r.lvl <= lvl + 5);
  let t = Math.random() * pool.reduce((a, r) => a + RUNA_TIERS[r.tier].weight, 0);
  for (const r of pool) if ((t -= RUNA_TIERS[r.tier].weight) <= 0) return r.id;
  return pool[0].id;
}
// Weapon damage and defence after the item's own quality and +% rolls.
export function itemDamage(it) {
  const base = BASE[it.base];
  if (!base.dmg) return null;
  const p = itemProps(it);
  const m = 1 + ((it.quality || 0) + (p.dmgPct || 0)) / 100;
  return [Math.round(base.dmg[0] * m + (p.dmgMin || 0)), Math.round(base.dmg[1] * m + (p.dmgMax || 0))];
}
export function itemDefense(it) {
  if (!it.def) return 0;
  const p = itemProps(it);
  return Math.round(it.def * (1 + ((it.quality || 0) + (p.armorPct || 0)) / 100) + (p.armor || 0));
}
export function itemValue(it) {
  if (it.kind === "gem") return [20, 80, 300][it.grade];
  if (it.kind === "runa") { const r = RUNA[it.runa]; return { comun: 40, media: 400, alta: 4000 }[r.tier] + r.lvl * 10; }
  if (it.kind === "potion") return 5;
  if (it.kind === "relic") return 0; // not for sale
  // (runes are gone: only to sell an old save's)
  if (it.kind === "rune") return !RUNE[it.rune] ? 0 : RUNE[it.rune].grammar ? 250 + RUNE[it.rune].lvl * 20 : 30 + RUNE[it.rune].lvl * 12;
  if (it.rarity === "tunjo") return 1; // the tunjo's rainbow items: worth everything, sold for nothing
  const mult = { low: 0.4, normal: 1, magic: 3, rare: 7, crafted: 8, set: 12, unique: 15, runeword: 14, ancestral: 25, legendario: 40, mitico: 70 }[it.rarity];
  // uniques and set pieces have a level of their own: they're worth that, not where they happened to drop
  const lvl = it.rarity === "unique" || it.set || it.setShirt ? itemLevelReq(it) : it.ilvl;
  return Math.round((10 + lvl * 6) * mult);
}
export function canEquip(ch, it) {
  if (it.kind) return false;
  const base = BASE[it.base];
  const st = charStats(ch);
  const req = it.rarity === "tunjo" ? {} : base.req || {}; // the rainbow items ask nothing
  const lvlReq = itemLevelReq(it);
  return ch.level >= lvlReq && st.str >= (req.str || 0) && st.dex >= (req.dex || 0);
}
// an item asks at least the level of each rune set in it
export function itemLevelReq(it) {
  const own = itemLevelReq0(it);
  let r = 0;
  for (const g of it.gems || []) if (g.runa) r = Math.max(r, RUNA[g.runa].lvl);
  return Math.max(own, r);
}
function itemLevelReq0(it) {
  if (it.lreq) return it.lreq;
  if (it.rarity === "unique") return UNIQUES.find((u) => u.name === it.name)?.lvl ?? it.ilvl;
  if (it.rarity === "runeword") return BASE[it.base].lvl; // from an old save (runes are gone)
  if (it.set) return Math.max(BASE[it.base].lvl, SETS.find((s) => s.id === it.set)?.lvl ?? it.ilvl);
  const base = BASE[it.base];
  if (it.rarity === "rare" || it.rarity === "crafted") return Math.max(base.lvl, Math.min(it.ilvl, Math.round(it.ilvl * 0.8)));
  if (it.rarity === "magic") return Math.max(base.lvl, Math.round(it.ilvl * 0.6));
  return base.lvl;
}

// ---------- character ----------
export function newCharacter(name, cls) {
  const c = CLASSES[cls];
  const ch = {
    v: 1, name, cls, level: 1, xp: 0, gold: 50, points: 0,
    base: { ...c.stats },
    equip: {}, swap: 1, inv: [], stash: [],
    belt: [], // potions
    life: 0, mana: 0,
    zones: { paramo: { pack: 0, cleared: false, depth: 0 } },
    stats: { kills: 0, lines: 0, perfect: 0, deaths: 0, bestCombo: 0 },
    created: Date.now(),
  };
  for (const id of c.start) {
    const it = makeItem(id, "normal", 1);
    const slot = BASE[id].slot;
    ch.equip[slot === "weapon" ? "weapon1" : slot === "off" ? "off1" : slot] = it;
  }
  ch.belt = [makePotion("life", 0), makePotion("life", 0), makePotion("mana", 0), makePotion("mana", 0)];
  const s = charStats(ch);
  ch.life = s.maxLife; ch.mana = s.maxMana;
  return ch;
}

// Experience for the next level. Up to level 40 a level is about 50 kills of monsters your level (with
// main.js's XP_RATE); past it, the curve steepens (× levelSlope), more with every level (see README).
export const levelSlope = (lvl) => (lvl <= 40 ? 1 : 1 + 1.5 * Math.pow((lvl - 40) / 50, 3));
export const xpToNext = (lvl) => Math.round(40 * Math.pow(lvl, 1.8) * levelSlope(lvl));

export function activeSlots(ch) {
  return ["head", "neck", "shirt", "body", `weapon${ch.swap}`, `off${ch.swap}`, "hands", "ring1", "ring2", "belt", "feet"];
}
export function equippedItems(ch) {
  return activeSlots(ch).map((s) => ch.equip[s]).filter(Boolean);
}
export function setCounts(ch) {
  const n = {};
  for (const it of equippedItems(ch)) if (it.set) n[it.set] = (n[it.set] || 0) + 1;
  return n;
}

// Everything derived from attributes + gear + set bonuses + class passive.
export function charStats(ch) {
  const P = {};
  const add = (props) => { for (const [k, v] of Object.entries(props)) P[k] = typeof v === "boolean" ? (P[k] || v) : (P[k] || 0) + v; };
  add(CLASSES[ch.cls].passive);
  for (const it of equippedItems(ch)) add(itemProps(it));
  const shirtSet = setShirtOf(ch);
  if (shirtSet) for (const b of Object.values(shirtSet.bonus)) add(b);
  for (const [sid, n] of Object.entries(setCounts(ch))) {
    if (sid === shirtSet?.id) continue;
    const set = SETS.find((s) => s.id === sid);
    for (const [k, b] of Object.entries(set.bonus)) if (n >= +k) add(b);
  }
  // the pet and the horse you take along
  if (PETS[ch.pet] && ch.pets?.includes(ch.pet)) add(PETS[ch.pet].props);
  if (MOUNTS[ch.mount] && ch.mounts?.includes(ch.mount)) add(MOUNT_PROPS);
  const all = P.allStats || 0;
  const str = ch.base.str + (P.str || 0) + all, dex = ch.base.dex + (P.dex || 0) + all;
  const vit = ch.base.vit + (P.vit || 0) + all, ene = ch.base.ene + (P.ene || 0) + all;

  const weapon = ch.equip[`weapon${ch.swap}`];
  const kind = weapon ? BASE[weapon.base].kind : "melee";
  let dmg = weapon ? itemDamage(weapon) : [1, 3];
  // the weapon's own +% is already in itemDamage; other gear's +% applies on top
  const weaponProps = weapon ? itemProps(weapon) : {};
  const otherPct = (P.dmgPct || 0) - (weaponProps.dmgPct || 0);
  const otherMin = (P.dmgMin || 0) - (weaponProps.dmgMin || 0), otherMax = (P.dmgMax || 0) - (weaponProps.dmgMax || 0);
  const statBonus = kind === "ranged" ? dex : str;
  const m = (1 + otherPct / 100) * (1 + statBonus / 100);
  dmg = [Math.max(1, Math.round((dmg[0] + otherMin) * m)), Math.max(1, Math.round((dmg[1] + otherMax) * m))];
  const elem = { fire: P.fire || 0, cold: P.cold || 0, light: P.light || 0, poison: P.poison || 0 };

  let armor = Math.round(dex / 4);
  for (const it of equippedItems(ch)) armor += itemDefense(it);
  const off = ch.equip[`off${ch.swap}`];
  const block = off && BASE[off.base].block ? clamp(BASE[off.base].block + (P.block || 0) + Math.floor(dex / 10), 0, 60) : 0;

  const res = (k) => clamp((P[k] || 0) + (P.resAll || 0), -100, 75);
  const beltSlots = 4 + (P.beltSlots || 0);
  return {
    str, dex, vit, ene, kind, dmg, elem, armor, block, otherPct, statPct: statBonus, otherFlat: [otherMin, otherMax],
    maxLife: Math.round(10 + vit * 2 + ch.level * 4 + (P.life || 0)),
    maxMana: Math.round(5 + ene * 1.6 + ch.level * 1.5 + (P.mana || 0)),
    crit: clamp(5 + dex * 0.08 + (P.crit || 0), 0, 50),
    dodge: clamp((P.dodge || 0) + dex * 0.03, 0, 40),
    resFire: res("resFire"), resCold: res("resCold"), resLight: res("resLight"), resPoison: res("resPoison"),
    leech: P.leech || 0, manaLeech: P.manaLeech || 0, lifeRegen: 1 + (P.lifeRegen || 0), manaRegen: 2 + Math.floor(ene / 15) + (P.manaRegen || 0),
    killHeal: P.killHeal || 0, thorns: P.thorns || 0,
    dmgDictation: P.dmgDictation || 0, dmgCloze: P.dmgCloze || 0,
    replayCost: clamp(P.replayCost || 0, 0, 80), hintCost: clamp(P.hintCost || 0, 0, 90),
    freeReplay: P.freeReplay || 0, slowFree: !!P.slowFree, typoTol: P.typoTol || 0, nearExact: !!P.nearExact,
    comboStart: P.comboStart || 0, comboKeep: !!P.comboKeep,
    potion: P.potion || 0, beltSlots, mf: P.mf || 0, gf: P.gf || 0, xp: P.xp || 0,
    spellDmg: P.spellDmg || 0, magicWeapon: !!(weapon && BASE[weapon.base].magic),
  };
}

// Mana costs scale with level so replays always matter.
export function costs(ch, st, maldito = false) {
  const base = (2 + ch.level * 0.45) * (diffOf(ch).costMul ?? 1);
  return {
    replay: Math.max(1, Math.round(base * (1 - st.replayCost / 100))),
    slow: st.slowFree ? 0 : Math.max(1, Math.round(base * 1.5 * (1 - st.replayCost / 100))),
    // a hint is meant to hurt: 8 replays
    hint: Math.max(1, Math.round(base * 8 * (1 - st.hintCost / 100) * (maldito ? 2 : 1))),
  };
}

// ---------- spells (the brujo) ----------
export const powerOf = (ch) => POWERS[ch.cls] || null;
export const powerCost = (ch, st) => Math.max(1, Math.round(st.maxMana * (powerOf(ch)?.cost || 0)));
export const canCast = (ch, st) => !!CLASSES[ch.cls]?.spells && st.magicWeapon;
export const spellsFor = (ch) => (CLASSES[ch.cls]?.spells ? SPELLS : []);
export function spellCost(ch, sp) {
  return Math.max(1, Math.round((2 + ch.level * 0.45) * (diffOf(ch).costMul ?? 1) * sp.cost));
}
// The prepared spell, applied to a hit already made: its parts turned into the spell's element (energía
// instead of destreza, plus spell damage), and what else it does. A hit of 0 (no word right) fizzles.
export function castSpell(ch, st, sp, hit, acc) {
  const out = { parts: { ...hit.parts }, splash: sp.splash || 0, all: !!sp.all, freeze: 0, shield: 0 };
  if (!hit.dmg) return out;
  const power = ((1 + st.ene / 100) / (1 + st.statPct / 100)) * (1 + st.spellDmg / 100);
  if (sp.el) {
    const phys = out.parts.phys || 0;
    delete out.parts.phys;
    out.parts[sp.el] = Math.round((out.parts[sp.el] || 0) + phys * sp.mult * power);
  }
  if (sp.freeze && acc >= 0.6) out.freeze = sp.freeze;
  if (sp.shield) out.shield = Math.round(acc * (6 + 2.5 * ch.level) * power * sp.shield);
  return out;
}

// ---------- monsters ----------
const hpCurve = (l) => 8 + l * 3.2 + Math.pow(l, 1.45);
const dmgCurve = (l) => 5 + l * 2.4 + Math.pow(l, 1.25) * 0.4;
export const xpFor = (l) => Math.round(5 + 5 * Math.pow(l, 1.5));

function monster(kind, lvl, tier, extra = {}, D = DIFFICULTY.medio) {
  const def = kind in BOSSES && tier === "boss" ? BOSSES[kind] : MONSTERS[kind];
  const T = { normal: [1, 1, 1], minion: [0.8, 0.9, 0.6], champion: [2, 1.4, 3], unique: [3, 1.6, 5], boss: [9, 2.3, 18] }[tier]; // bosses: 9× the life, 2.3× the blow
  const hp = Math.max(1, Math.round(hpCurve(lvl) * def.hp * T[0] * D.hp * (0.88 + Math.random() * 0.24)));
  let mods = extra.mods || def.mods || [];
  if (D === DIFFICULTY.facil) mods = mods.filter((m) => !LISTENING_MODS.includes(m));
  const el = mods.map((m) => MONSTER_MODS[m].el).find(Boolean) || def.el || null;
  // resistances: the kind's own, and Ígneo / Gélido / Eléctrico monsters resist their element at least 75%
  const res = { ...(MONSTER_RES[kind] || {}) };
  for (const m of mods) { const e = MONSTER_MODS[m].el; if (e) res[e] = Math.max(res[e] || 0, 75); }
  return {
    uid: uid(), kind, tier, lvl, name: extra.name || def.name, icon: def.icon, color: def.color,
    hp, maxHp: hp, dmg: dmgCurve(lvl) * def.dmg * T[1] * (mods.includes("fuerte") ? 1.5 : 1),
    el, res, mods, vamp: def.vamp || mods.includes("vampirico"), xp: Math.round(xpFor(lvl) * T[2]),
  };
}

// One monster, for encounters built outside makeEncounter (weak spots, Anki leeches).
export const makeFoe = (kind, lvl, tier, extra = {}, D = DIFFICULTY.medio) => monster(kind, lvl, tier, extra, D);

// A pack for zone `zone` at progress `pack` (0..packs-1), or the boss when pack === packs.
export function makeEncounter(zone, pack, depth = 0, D = DIFFICULTY.medio) {
  const easy = D === DIFFICULTY.facil;
  const roster = easy ? (zone.easy || EASY_ROSTER[zone.id]) : zone.monsters;
  const M = (kind, lvl, tier, extra) => monster(kind, lvl, tier, extra, D);
  const span = zone.lvl[1] - zone.lvl[0];
  const lvl = zone.flat ? zone.lvl[0] : zone.endless ? zone.lvl[0] + depth * 2 + Math.floor(pack / 3) : zone.lvl[0] + (zone.packs ? Math.round((span * pack) / zone.packs) : span);
  if (pack >= zone.packs) {
    const b = BOSSES[zone.boss];
    const boss = M(zone.boss, lvl + 1, "boss");
    const minion = easy ? pick(roster) : b.minions;
    return { lvl, boss: true, intro: b.intro, monsters: [boss, M(minion, lvl, "minion"), ...(easy ? [] : [M(minion, lvl, "minion")])] };
  }
  const r = Math.random();
  if (!easy && r < 0.1 * D.elite && pack > 0) {
    const kind = pick(roster);
    const mods = [...RANDOM_MODS].sort(() => Math.random() - 0.5).slice(0, (lvl > 15 ? 3 : 2) + (D === DIFFICULTY.dificil ? 1 : 0));
    const u = M(kind, lvl + 1, "unique", { mods, name: pick(UNIQUE_MONSTER_NAMES) });
    return { lvl, monsters: [u, ...Array.from({ length: rnd(2, 3) }, () => M(kind, lvl, "minion"))] };
  }
  if (r < 0.1 * D.elite + 0.22 * D.elite) {
    const kind = pick(roster);
    const mods = [pick(easy ? RANDOM_MODS.filter((m) => !LISTENING_MODS.includes(m)) : RANDOM_MODS)];
    return { lvl, monsters: Array.from({ length: rnd(2, 3) }, () => M(kind, lvl, "champion", { mods })) };
  }
  const n = rnd(1, Math.min(easy ? 2 : 4, 2 + Math.floor(pack / 2)));
  return { lvl, monsters: Array.from({ length: n }, () => M(pick(roster), lvl, "normal")) };
}

// ---------- combat ----------
// Your attack for one exercise. acc is 0..1, mode "dictation"|"cloze".
export function playerAttack(ch, st, acc, mode, { perfectFirst, combo }) {
  if (acc <= 0) return { dmg: 0, crit: false, parts: {} };
  const crit = perfectFirst || Math.random() * 100 < st.crit;
  const base = rnd(st.dmg[0], st.dmg[1]);
  const modeMult = mode === "cloze" ? 0.7 * (1 + st.dmgCloze / 100) : 1 + st.dmgDictation / 100;
  const comboMult = 1 + 0.1 * Math.min(combo, 10);
  const phys = base * modeMult * comboMult * acc * (crit ? 2 : 1);
  const parts = { phys: Math.round(phys) };
  for (const [k, v] of Object.entries(st.elem)) if (v) parts[k] = Math.round(v * acc * comboMult * (crit ? 1.5 : 1));
  const dmg = Object.values(parts).reduce((a, b) => a + b, 0);
  return { dmg: Math.max(1, dmg), crit, parts };
}

// Your attack's parts against one monster: elemental parts scaled by its resistances, physical untouched.
export function damageAgainst(parts, m) {
  let total = 0;
  const notes = { immune: [], resist: [], weak: [] }, by = {};
  const stone = m.mods?.includes("piedra") ? 0.65 : 1;
  for (const [k, v] of Object.entries(parts)) {
    if (!v) continue;
    const r = k === "phys" ? 0 : (m.res?.[k] || 0);
    total += v * (1 - r / 100);
    by[k] = Math.max(0, v * (1 - r / 100) * stone); // what each kind of damage really did
    if (r >= 100) notes.immune.push(k); else if (r > 0) notes.resist.push(k); else if (r < 0) notes.weak.push(k);
  }
  total *= stone;
  return { dmg: Math.max(0, Math.round(total)), notes, by };
}

// One monster's attack on you after an exercise. A perfect line means you dodge everything.
export function monsterAttack(ch, st, m, acc, level, D = DIFFICULTY.medio) {
  if (acc >= D.safeAcc) return { dodged: true, dmg: 0 };
  if (Math.random() * 100 < st.dodge) return { dodged: true, dmg: 0 };
  if (st.block && Math.random() * 100 < st.block) return { blocked: true, dmg: 0 };
  const raw = m.dmg * D.dmgTaken * (1 - 0.75 * acc) * (0.85 + Math.random() * 0.3);
  const dr = Math.min(0.75, st.armor / (st.armor + 25 + 12 * m.lvl));
  // half of an elemental monster's hit is its element, which your resistance reduces; the rest your armour
  const phys = m.el ? raw * 0.5 * (1 - dr) : raw * (1 - dr);
  const elDmg = m.el ? raw * 0.5 * (1 - st[`res${cap(m.el)}`] / 100) : 0;
  return { dmg: Math.max(1, Math.round(phys + elDmg)), phys, el: m.el || null, elDmg };
}
const cap = (s) => s[0].toUpperCase() + s.slice(1);
// A boss's signature blow: like a normal one (armour, resistance; what you got right still softens it),
// times its weight, with no dodge or block by chance: only the line itself gets you out of the way. It
// never takes more than BLOW_CAP of your life at once.
export const BLOW_CAP = 0.65;
export function heavyBlow(st, m, acc, mult, D = DIFFICULTY.medio) {
  const raw = m.dmg * D.dmgTaken * (1 - 0.5 * acc) * mult * (0.9 + Math.random() * 0.2);
  const dr = Math.min(0.75, st.armor / (st.armor + 25 + 12 * m.lvl));
  let phys = m.el ? raw * 0.5 * (1 - dr) : raw * (1 - dr);
  let elDmg = m.el ? raw * 0.5 * (1 - st[`res${cap(m.el)}`] / 100) : 0;
  const cap50 = st.maxLife * BLOW_CAP, total = phys + elDmg;
  if (total > cap50) { phys *= cap50 / total; elDmg *= cap50 / total; }
  return { dmg: Math.max(1, Math.round(phys + elDmg)), phys, el: m.el || null, elDmg };
}

// What a dead monster drops.
// Past 10 in a row, each answer more makes rare-or-better drops 1% likelier than normal (11: +1%, 12: +2%...).
export const streakLuck = () => 1; // (a streak used to raise the odds of rare loot; now it rolls the streak dice below)

// ---------- the streak dice ----------
// From a streak of DICE_FROM, each perfect line rolls percentile dice (1–100): a win if the roll is at most
// the streak's chance, 1% at 5 and one point more every 2 lines, at most 15% (10: 3%, 20: 8%, 30: 13%).
// A win rolls the prize die, a d20 plus one per 10 of the streak (at most +4): the higher, the better the
// prize. Over a streak from 5 to 30 that's about 2 wins; an ancestral about 1 long streak in 7, a legendary
// about 1 in 20, a mythic only from a natural 20 on a streak of 40 or more.
export const DICE_FROM = 5;
export const diceChance = (n) => (n < DICE_FROM ? 0 : Math.min(15, 1 + Math.floor((n - DICE_FROM) / 2))); // whole numbers: one more every 2 lines
export const prizeBonus = (n) => Math.min(4, Math.floor(n / 10));
export const PRIZES = [ // [lowest total, kind, what it's called]
  [24, "mitico", "un objeto mítico"], [22, "legendario", "un objeto legendario"], [20, "ancestral", "un objeto ancestral"],
  [16, "item", "un objeto raro o mejor"], [11, "gem", "una gema"], [1, "gold", "una bolsa de oro"],
];
export function streakRoll(n, lvl, st, D = DIFFICULTY.medio, easy = false) {
  const need = diceChance(n);
  if (!need) return null;
  const roll = 1 + Math.floor(Math.random() * 100);
  const out = { n, need, roll, win: roll <= need };
  if (!out.win) return out;
  const face = 1 + Math.floor(Math.random() * 20), bonus = prizeBonus(n), total = face + bonus;
  let [, kind, label] = PRIZES.find(([min]) => total >= min);
  // Fácil never gives the three top tiers: they become a unique
  if (easy && ["mitico", "legendario", "ancestral"].includes(kind)) [kind, label] = ["item", "un objeto único"];
  Object.assign(out, { face, bonus, total, kind, label });
  if (kind === "gold") out.gold = Math.round(D.gold * (20 + lvl * 6) * (1 + n / 10) * (0.8 + Math.random() * 0.4) * (1 + (st.gf || 0) / 100));
  else if (kind === "gem") out.item = makeGem(pick(Object.keys(GEMS)), Math.min(2, gemGrade(lvl) + 1));
  else if (kind === "item") out.item = randomItem(lvl + 2, st.mf || 0, 5, null, D, 1, easy && label.includes("único") ? "unique" : chance(0.25) ? "unique" : chance(0.2) ? "set" : "rare");
  else out.item = randomItem(lvl + 2, st.mf || 0, 5, null, D, 1, kind);
  return out;
}
export function lootFor(m, ch, st, D = DIFFICULTY.medio, good = 1, luck = 1) {
  const out = [];
  st = { ...st, mf: Math.max(0, st.mf + D.mf) };
  const gold = Math.round(D.gold * (3 + m.lvl * 2.5) * (0.5 + Math.random()) * (1 + st.gf / 100) * ({ normal: 1, minion: 0.6, champion: 2.5, unique: 4, boss: 10 }[m.tier]));
  const L = D.loot;
  const n = { normal: chance(0.2 * L) ? 1 : 0, minion: chance(0.12 * L) ? 1 : 0, champion: chance(Math.min(1, 0.65 * L)) ? 1 : 0, unique: 2, boss: Math.max(1, Math.round(4 * L)) }[m.tier];
  const bonus = { normal: 1, minion: 1, champion: 1.8, unique: 3, boss: 5 }[m.tier] * L;
  for (let i = 0; i < n; i++) out.push(randomItem(m.lvl, st.mf, bonus, null, D, good, null, luck));
  if (chance(relicChance(m))) out.push(makeRelic());
  if (chance({ normal: 0.12, minion: 0.06, champion: 0.3, unique: 0.5, boss: 1 }[m.tier])) {
    const tier = m.lvl >= 24 ? 2 : m.lvl >= 10 ? 1 : 0;
    out.push(makePotion(chance(0.08) ? "rejuv" : chance(0.55) ? "life" : "mana", tier));
  }
  if (chance(GEM_CHANCE[m.tier])) {
    out.push(makeGem(pick(Object.keys(GEMS)), gemGrade(m.lvl)));
  }
  if (chance(RUNA_CHANCE[m.tier])) out.push(makeRuna(pickRuna(m.lvl)));
  return { gold: chance(0.7) || m.tier !== "normal" ? gold : 0, items: out };
}

export function zoneById(id) { return ZONES.find((z) => z.id === id); }
export function nextZone(id) { const i = ZONES.findIndex((z) => z.id === id); return ZONES[i + 1]; }

// ---------- alembic (crafting) ----------
// 3 identical gems -> next grade. 3 perfect gems + a magic item -> a rare item of the same type.
// A whole set, one of each piece and nothing else: it melts into the set's magic undershirt (see makeSetShirt).
// Props that only shape the piece itself (its armour, its damage) don't carry over.
const LOCAL_PROPS = new Set(["armorPct", "armor", "dmgPct", "dmgMin", "dmgMax", "block"]);
export function makeSetShirt(set, pieces) {
  const sum = {};
  for (const it of pieces) for (const [k, v0] of Object.entries(it.props || {})) {
    // what the base itself does (a belt's pockets, an orb's mana) stays with the base
    const v = typeof v0 === "number" ? v0 - (BASE[it.base]?.props?.[k] || 0) : v0;
    if (LOCAL_PROPS.has(k) || !v) continue;
    sum[k] = typeof v === "boolean" ? (sum[k] || v) : (sum[k] || 0) + v;
  }
  // half of what the pieces gave, rounded; never less than 1 of something they had
  const props = {};
  for (const [k, v] of Object.entries(sum)) props[k] = typeof v === "boolean" ? v : v > 0 ? Math.max(1, Math.round(v / 2)) : Math.round(v / 2);
  return { id: uid(), base: "camiseta", rarity: set.tier || "set", ilvl: set.lvl, lreq: set.lvl, props, sockets: 0, gems: [], setShirt: set.id, name: `Camiseta de «${set.name}»` };
}
// a worn set undershirt (its own slot): every bonus of its set, all tiers
export const setShirtOf = (ch) => { const n = ch.equip?.shirt; return n?.setShirt ? SETS.find((s) => s.id === n.setShirt) : null; };
function setMelt(items) {
  const id = items[0]?.set, set = id && SETS.find((s) => s.id === id);
  if (!set || items.some((i) => i.kind || i.set !== id)) return null;
  const have = new Set(items.map((i) => i.name)).size;
  if (have !== items.length) return { result: null, text: "Hace falta una pieza de cada, sin repetir." };
  if (have < set.pieces.length) return { result: null, text: `A ${set.name} le faltan piezas: tienes ${have} de ${set.pieces.length}.` };
  const neck = makeSetShirt(set, items);
  return { result: neck, shirt: neck, setId: set.id, set: set.name, text: `${set.name} se funde en una camiseta encantada.` };
}
export function alembic(items) {
  // a whole set melts; a partial one only says what's missing if no other recipe takes the pieces
  const melt = setMelt(items);
  if (melt?.result) return melt;
  return alembicRecipe(items) || melt;
}
function alembicRecipe(items) {
  // 3 of the same rune: the next one up (not into the last, Chiminigagua: that one only falls)
  const runas = items.filter((i) => i.kind === "runa");
  if (items.length === 3 && runas.length === 3 && runas.every((r) => r.runa === runas[0].runa)) {
    const k = RUNAS.findIndex((r) => r.id === runas[0].runa), next = RUNAS[k + 1];
    if (!next || k + 1 === RUNAS.length - 1) return { result: null, text: "Esas runas ya no suben más: la última solo cae de los monstruos." };
    return { result: makeRuna(next.id), text: `Las tres runas se funden en una runa ${next.name}.` };
  }
  const gems = items.filter((i) => i.kind === "gem");
  if (items.length === 3 && gems.length === 3 && gems.every((g) => g.gem === gems[0].gem && g.grade === gems[0].grade) && gems[0].grade < 2) {
    return { result: makeGem(gems[0].gem, gems[0].grade + 1), text: "Las gemas se funden en una mejor." };
  }
  const mag = items.filter((i) => !i.kind && i.rarity === "magic");
  if (items.length === 4 && mag.length === 1 && gems.length === 3 && gems.every((g) => g.grade === 2)) {
    const base = BASE[mag[0].base];
    const it = makeItem(base.id, "rare", Math.max(mag[0].ilvl, 10));
    return { result: it, text: "El objeto mágico renace como raro." };
  }
  // a plain item with nothing in it + any 3 gems: new sockets, a different number when it can be
  const plain = items.filter((i) => !i.kind && (i.rarity === "normal" || i.rarity === "low"));
  if (items.length === 4 && plain.length === 1 && gems.length === 3) {
    const it = plain[0], max = BASE[it.base].sockets || 0;
    if (!max) return { result: null, text: "Ese objeto no admite engastes." };
    if (it.gems.length) return { result: null, text: "Solo sirve con un objeto que no tenga nada engastado." };
    let n = plainSockets(BASE[it.base]);
    while (max > 1 && n === it.sockets) n = plainSockets(BASE[it.base]);
    return { result: { ...it, sockets: n, gems: [], runeword: undefined }, text: `${n === 1 ? "Se abre un engaste" : `Se abren ${n} engastes`} en el objeto.` };
  }
  const potions = items.filter((i) => i.kind === "potion");
  if (items.length === 3 && mag.length === 1 && gems.length === 1 && potions.length === 1) {
    const it = makeCrafted(mag[0], gems[0]);
    return { result: it, text: `El objeto sale del alambique como artesanal ${CRAFT[gems[0].gem].name}.` };
  }
  if (items.length === 3 && items.every((i) => !i.kind && i.rarity === "rare")) {
    // worth more than what goes in: above the best of the three, and half the time a unique or set piece
    const lvl = Math.max(...items.map((i) => i.ilvl)) + 3, r = Math.random();
    const it = r < 0.25 ? randomItem(lvl, 0, 1, null, null, 1, "unique") : r < 0.5 ? randomItem(lvl, 0, 1, null, null, 1, "set")
      : makeItem(pickBase(lvl).id, "rare", lvl, {}, { fullRare: true });
    return { result: it, text: "Tres raros se convierten en algo nuevo." };
  }
  // the same for the top tiers: above the best of the three, half the time one tier up (mythic has none above: a new mythic)
  const TOP_UP = { ancestral: ["legendario", "Tres ancestrales"], legendario: ["mitico", "Tres legendarios"], mitico: ["mitico", "Tres míticos"] };
  const top = items[0] && TOP_UP[items[0].rarity];
  if (top && items.length === 3 && items.every((i) => !i.kind && i.rarity === items[0].rarity)) {
    const lvl = Math.max(...items.map((i) => i.ilvl)) + 3;
    const it = makeTopItem(Math.random() < 0.5 ? top[0] : items[0].rarity, lvl);
    return { result: it, text: `${top[1]} se convierten en algo nuevo.` };
  }
  return null;
}
export const RECIPES = [
  "Un conjunto completo (una pieza de cada, nada más) → la camiseta encantada del conjunto: todas las bonificaciones del conjunto y la mitad de las propiedades de sus piezas (sin su defensa ni su daño; las gemas engastadas se pierden). Se lleva debajo de todo, en un sitio propio; mientras la llevas, se te ve con el conjunto entero (tú eliges qué piezas). Va a tus camisetas, una por conjunto",
  "3 gemas iguales → la gema del grado siguiente",
  "3 runas iguales → la runa siguiente (Ata → Bosa → … ; la última, Chiminigagua, solo cae)",
  "3 gemas perfectas + 1 objeto mágico → objeto raro del mismo tipo",
  "3 objetos raros → un objeto de nivel más alto que el mejor de los tres: único o de conjunto la mitad de las veces; si no, un raro con el máximo de propiedades",
  "3 objetos ancestrales (rosas) → un objeto de nivel más alto que el mejor de los tres: legendario la mitad de las veces; si no, otro ancestral",
  "3 objetos legendarios (rojos) → un objeto de nivel más alto que el mejor de los tres: mítico la mitad de las veces; si no, otro legendario",
  "3 objetos míticos (celestes) → un mítico nuevo de nivel más alto que el mejor de los tres",
  "1 objeto blanco sin nada engastado + 3 gemas cualesquiera → el mismo objeto con engastes nuevos (de 1 al máximo de su tipo; otro número si ya tenía)",
  "1 objeto mágico + 1 gema + 1 poción → objeto artesanal (naranja). La gema decide la familia: rubí de sangre, zafiro de brujo, esmeralda de guardián, amatista de golpe, topacio de fortuna, diamante de oído; su grado, la fuerza",
];

// A reward of a chosen rarity (casetes): "unique" may come out as a set piece.
// One of Doña Remedios' rainbow items (data.js TUNJO_ITEMS), for this level: on the best base of its
// family, its own properties, and a mítico's worth more, a little stronger.
// seed: the item's own, so made again at another level it keeps its character (main.js attuneTunjo).
// No attribute requirements, and its level is always yours: it can always be worn.
export function makeTunjoItem(def, ilvl, seed = Math.floor(Math.random() * 2 ** 31)) {
  const real = Math.random;
  let a = seed >>> 0;
  Math.random = () => { a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  try { return Object.assign(tunjoItem(def, ilvl), { seed }); } finally { Math.random = real; }
}
function tunjoItem(def, ilvl) {
  const fam = (typeof def.family === "string" ? BASES.filter((b) => b.slot === def.family && !b.root) : def.family.map((id) => BASE[id]))
    .filter((b) => b && b.lvl <= Math.max(ilvl, 1)).sort((a, b) => b.lvl - a.lvl);
  const base = fam[0] || BASE[[def.family].flat()[0]] || BASE[def.look];
  const it = makeItem(base.id, "tunjo", ilvl);
  Object.assign(it, { name: def.name, tunjo: def.id, look: def.look, flavor: def.flavor });
  const T = TOP.mitico, taken = new Set(Object.keys(def.props)), L = ilvl + T.up + 6, add = (k, v) => (it.props[k] = (it.props[k] || 0) + v);
  for (let i = 0; i < 7; i++) {
    const a = rollAffix(chance(0.5) ? PREFIXES : SUFFIXES, base, L, taken) || rollAffix(PREFIXES, base, L, taken) || rollAffix(SUFFIXES, base, L, taken);
    if (a) add(a.prop, Math.max(1, Math.round(a.value * 1.6)));
  }
  for (const [k, v] of Object.entries(def.props)) add(k, v);
  if (base.dmg) add("dmgPct", rnd(190, 250));
  if (base.def) add("armorPct", rnd(190, 250));
  add("resAll", rnd(20, 30));
  add("allStats", rnd(8, 14));
  it.sockets = sockRoll("mitico", base);
  it.lreq = 1;
  // and better than any rare or magic item of its slot could be, up to 4 levels above: by at least
  // a tenth in damage or defence, attributes (all four, all-attributes counted four times) and
  // resistances (likewise), whatever base and rolls that item got
  const R = rivalBest(base.slot, ilvl + 4), P = it.props, need = 1.1;
  const avg = () => { const d = itemDamage(it); return d ? (d[0] + d[1]) / 2 : 0; };
  if (base.dmg) while (avg() < R.dmg * need) P.dmgPct = (P.dmgPct || 0) + 10;
  if (it.def) while (itemDefense(it) < R.def * need) P.armorPct = (P.armorPct || 0) + 10;
  const stat = ATTRS.reduce((t, k) => t + (P[k] || 0), 0) + 4 * (P.allStats || 0);
  if (stat < R.stat * need) P.allStats = (P.allStats || 0) + Math.ceil((R.stat * need - stat) / 4);
  const res = RESISTS.reduce((t, k) => t + (P[k] || 0), 0) + 4 * (P.resAll || 0);
  if (res < R.res * need) P.resAll = (P.resAll || 0) + Math.ceil((R.res * need - res) / 4);
  return it;
}
const ATTRS = ["str", "dex", "vit", "ene"], RESISTS = ["resFire", "resCold", "resLight", "resPoison"];
// The most a rare or magic item of this slot could have at this level, per measure, over every base.
function affixMax(prop, base, L) {
  let v = 0;
  for (const list of [PREFIXES, SUFFIXES]) {
    let m = 0;
    for (const a of list) if (a.prop === prop && a.slots.includes(slotGroup(base))) for (const t of a.tiers) if (t[0] <= L) m = Math.max(m, t[2]);
    v += m;
  }
  const own = base.props?.[prop];
  return v + (typeof own === "number" ? own : 0);
}
function rivalBest(slot, L) {
  const R = { dmg: 0, def: 0, stat: 0, res: 0 };
  for (const b of BASES) {
    if (b.slot !== slot || b.lvl > L) continue;
    const top = (k) => affixMax(k, b, L);
    if (b.dmg) { const m = 1 + top("dmgPct") / 100; R.dmg = Math.max(R.dmg, (b.dmg[0] * m + top("dmgMin") + b.dmg[1] * m + top("dmgMax")) / 2); }
    if (b.def) R.def = Math.max(R.def, b.def[1] * (1 + top("armorPct") / 100) + top("armor"));
    R.stat = Math.max(R.stat, ATTRS.reduce((t, k) => t + top(k), 0) + 4 * top("allStats"));
    R.res = Math.max(R.res, RESISTS.reduce((t, k) => t + top(k), 0) + 4 * top("resAll"));
  }
  return R;
}
export function rewardItem(ilvl, rarity, slot = null) {
  if (rarity === "unique") return randomItem(ilvl, 99999, 99, slot);
  return makeItem(pickBase(ilvl, slot).id, rarity, ilvl);
}

