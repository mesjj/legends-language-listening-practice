// Leyendas: a listening RPG. Every attack is a listening exercise on a line of the episode.
import { $, esc, store, api, md, CFG, logout, playable, chooseBlanks, isSound, scoreDictation, scoreCloze, flagLine, norm, hash, accentKey } from "../listen-core.js";
import { RARITY, SLOTS, BASE, CLASSES, ZONES, BOSSES, EASY_ROSTER, MONSTER_MODS, POTIONS, SETS, GEMS, RUNE, CRAFT, TIERS, BANDS, SPELLS, PETS, PET_KIND, MOUNTS, MOUNT_PROPS, COMPANION_MIN_SECONDS, PROPS, TUNJO_ITEMS, POWERS, RUNAS, RUNA, RUNA_TIERS, RUNA_SETS } from "./data.js";
import * as E from "./engine.js";
import { figureSvg, itemIconSvg, monsterSvg, loadFigure, loadAnims, fightFigure, attackAnim, lookOfChar, stanceLoop, SHOW_SLOTS, setPieceFor, shirtChoice } from "./figure.js";
import { loadLook, lookData, prepareLook, defaultLook, randomLook, fixLook, fits } from "./look.js";
import * as FX from "./fx.js";
import { sourcesHtml } from "../sources.js";
import { runeOf as runeOfEs } from "./grammar.js";
import { SUBJ, SUBJ_CATS } from "./subjuntivo.js";
import { startI18n, lang, setLang, LANGS } from "./i18n.js";
import { sfx, isMuted, setMuted, setBusy, hush, quiet, wailOver } from "./sfx.js";
import { loadBossArt, hasBossArt, bossSprite, specialMeter, bossIntro, bossShout, bossLeap, bossFinisher, bigHit, bigHurt } from "./boss.js";
import * as MUSIC from "./music.js";

const audio = $("#audio");
const cardAudio = new Audio(); // Anki clips in the Repaso
const stopAll = () => { audio.pause(); cardAudio.pause(); };
setBusy(() => !audio.paused || !cardAudio.paused); // no effect sounds over the Spanish
MUSIC.setBusy(() => !audio.paused || !cardAudio.paused); // and the music drops while it plays
const screen = $("#screen");
const INV_SIZE = 56, STASH_SIZE = 500; // the bag: 7 rows of 8
// forms of haber (and the tenses near them) get their tense named when you miss one; Spanish only
const runeOf = (w) => (CFG.lang === "es" ? runeOfEs(w) : null);
// online: no Anki, no Claude, no voice (they need the owner's computer); see .online in rpg.css
if (CFG.online) document.body.classList.add("online");
// phones: note when a text box has the keyboard up (rpg.css hides the HUD then)
document.addEventListener("focusin", (e) => { if (e.target.matches("textarea, input:not([type=checkbox]):not([type=radio])")) document.body.classList.add("typing"); });
document.addEventListener("focusout", () => document.body.classList.remove("typing"));

let ch = store.get("rpg", null);
const S = { ep: null, T: null, lines: [], view: "town", F: null, alembic: [], loot: null };

const save = () => store.set("rpg", ch);
const stats = () => E.charStats(ch);

// ---------- small helpers ----------
function toast(msg, cls = "", ms = 2400) {
  const t = $("#toast");
  t.textContent = msg;
  t.className = "toast show " + cls;
  clearTimeout(toast._t);
  toast._t = setTimeout(() => (t.className = "toast"), ms);
}
const icon = (name, color, cls = "") =>
  `<i class="ico ${cls}" style="-webkit-mask-image:url(rpg/icons/${name}.svg);mask-image:url(rpg/icons/${name}.svg);background:${color}"></i>`;
// still: without the glow filter (for long lists, where many filters make scrolling stutter)
const itemIco = (it, still = false) => (it.kind === "relic" ? `<span class="ico relic-ico" aria-hidden="true"><i></i></span>` : itemIconSvg(it, "", { still }) || icon(E.itemIcon(it), E.itemColor(it)));
// what fills a socket: a gem or a runa
const sockColor = (g) => (g.runa ? RUNA_TIERS[RUNA[g.runa].tier].color : GEMS[g.gem].shades?.[g.grade] || GEMS[g.gem].color);
const socketLine = (g, slot) => {
  const e = E.socketEffect(g, slot);
  return `<div class="tgem" style="color:${sockColor(g)}">${g.runa ? `ᚱ <b>${esc(RUNA[g.runa].name)}</b>:` : "◆"} ${esc(E.propText(e.prop, e.value))}</div>`;
};
const RUNA_KINDS = [["w", "En un arma"], ["a", "En armadura (casco, torso, manos, pies, cinturón)"], ["o", "En un escudo"]];
const runaKindName = { w: "armas", a: "armaduras", o: "escudos" };
// A rune set's lines: its runes (the ones in this item lit), what it gives, and in what
function runaSetHtml(rs, have = [], on = false, kind = null) {
  const left = [...have];
  const runes = rs.runas.map((r) => { const i = left.indexOf(r), got = i >= 0; if (got) left.splice(i, 1); return `<span class="${got ? "" : "dim"}" style="${got ? `color:${RUNA_TIERS[RUNA[r].tier].color}` : ""}">${esc(RUNA[r].name)}</span>`; }).join(" · ");
  const kinds = kind ? [kind] : rs.kinds;
  return `<div class="trunaset${on ? " on" : ""}"><div><b>${esc(rs.name)}</b> <span class="dim">(${rs.runas.length} runas, en ${rs.kinds.map((k) => runaKindName[k]).join(", ")})</span></div><div>${runes}</div>` +
    kinds.map((k) => `<div class="${on ? "" : "dim"}">${kind ? "" : `<span class="dim">En ${runaKindName[k]}:</span> `}${Object.entries(rs.bonus[k]).map(([p, v]) => esc(E.propText(p, v))).join(", ")}</div>`).join("") + `</div>`;
}
const h = (html) => { const d = document.createElement("div"); d.innerHTML = html.trim(); return d.firstElementChild; };
const findItem = (id) => {
  for (const [where, list] of [["inv", ch.inv], ["stash", ch.stash], ["belt", ch.belt]]) {
    const i = list.findIndex((x) => x.id === id);
    if (i >= 0) return { it: list[i], where, list, i };
  }
  for (const [slot, it] of Object.entries(ch.equip)) if (it?.id === id) return { it, where: "equip", slot };
  for (const [sid, it] of Object.entries(ch.shirts || {})) if (it?.id === id) return { it, where: "shirts", sid };
  return null;
};

// ---------- episode / lines ----------
// A course (an episode built by scripts/build_course.py) brings its own zones: each one lends the
// monsters and boss of one of the game's zones, and lists its fights line by line.
const GAME_ZONES = ZONES.slice();
function installZones(T) {
  const course = (T.zones || []).map((z) => {
    const t = GAME_ZONES.find((q) => q.id === z.template) || GAME_ZONES[0];
    const zone = { ...t, id: z.id, scene: t.id, name: z.name, blurb: z.blurb, lvl: z.lvl, endless: false, easy: t.easy || EASY_ROSTER[t.id] };
    // four ways to study a zone, each its own run of fights, any of them at any time; the last fight is the boss
    zone.fightsOf = (m) => z.fights.filter((f) => f.mode === m);
    Object.defineProperty(zone, "fights", { get: () => zone.fightsOf(modeOf(zone.id)), enumerable: true });
    zone.modes = MODES.filter((m) => z.fights.some((f) => f.mode === m));
    Object.defineProperty(zone, "packs", { get: () => zone.fights.length - 1, enumerable: true });
    return zone;
  });
  ZONES.splice(0, ZONES.length, ...(course.length ? course : GAME_ZONES));
}
const lessonOf = (si) => S.T?.segments[si]?.lesson || null;
const LEVEL_NAME = { verb: "El verbo", word: "Palabra por palabra", gap: "Escribe el verbo", vocab: "Toda la frase" };
const MODE_DESC = { verb: "¿qué significa el verbo?", word: "una palabra de la frase cada vez", gap: "escribe el verbo que falta", vocab: "¿qué significa la frase entera?" };
const MODES = ["verb", "word", "gap", "vocab"];
const modeOf = (zid) => ch.zones[zid]?.mode || "verb";
// Saves from before the modes had one place along verb → word → gap: carry it over to that mode.
// Which drops fall unidentified: set (green), ancestral (pink), legendary (red) and mythic (light blue).
// Rare and unique pieces come identified; any left unidentified from before are identified on load.
const UNID = new Set(["set", "ancestral", "legendario", "mitico"]);
function identifyOld() {
  for (const it of [...ch.inv, ...(ch.stash || [])]) if (it?.unid && !UNID.has(it.rarity)) delete it.unid;
}
// Runes were taken out of the game. In an older save, loose ones are sold at their price, socketed
// ones come out (refunded the same, so the socket is free again), and a runeword keeps everything it
// gave, the runes' own effects included, with its sockets closed. Then it's an ordinary item.
function dropRunes() {
  if (!ch) return;
  const all = () => [...Object.values(ch.equip || {}), ...ch.inv, ...(ch.stash || [])].filter(Boolean);
  if (!all().some((it) => it.kind === "rune" || it.runeword || it.gems?.some((g) => g.rune))) return;
  let gold = 0, n = 0, words = 0;
  const price = (id) => E.itemValue({ kind: "rune", rune: id });
  const loose = (list) => list.filter((it) => { if (it?.kind !== "rune") return true; gold += price(it.rune); n++; return false; });
  ch.inv = loose(ch.inv);
  if (ch.stash) ch.stash = loose(ch.stash);
  for (const it of all()) {
    if (it.kind || !(it.runeword || it.gems?.some((g) => g.rune))) continue;
    const slot = BASE[it.base].slot;
    if (it.runeword) {
      for (const g of it.gems) if (g.rune && RUNE[g.rune]) { const e = E.socketEffect(g, slot); it.props[e.prop] = typeof e.value === "boolean" ? e.value : (it.props[e.prop] || 0) + e.value; }
      it.gems = []; it.sockets = 0; words++;
    } else {
      for (const g of it.gems) if (g.rune) { gold += RUNE[g.rune] ? price(g.rune) : 0; n++; }
      it.gems = it.gems.filter((g) => !g.rune);
    }
    delete it.runeword; delete it.rwProps;
  }
  ch.gold += gold;
  save();
  const parts = [n ? `${n} ${n === 1 ? "runa vendida" : "runas vendidas"} por ${gold} de oro` : "", words === 1 ? "tu palabra rúnica se queda con todo lo que daba" : words ? `tus ${words} palabras rúnicas se quedan con todo lo que daban` : ""].filter(Boolean);
  setTimeout(() => toast(`Las runas ya no existen: ${parts.join("; ")}.`, "levelup", 6000), 400);
}
// Set necklaces became magic undershirts, worn in a slot of their own: an older save's necklaces
// (the collection, and the one on the neck) turn into the set's undershirt, the worn one onto the new slot.
function necklacesToShirts() {
  if (!ch) return;
  const conv = (it) => {
    if (!it?.setNeck) return it;
    const set = SETS.find((s) => s.id === it.setNeck);
    const out = { ...it, base: "camiseta", setShirt: it.setNeck, name: `Camiseta de «${set?.name || it.setNeck}»` };
    delete out.setNeck;
    return out;
  };
  let n = 0;
  if (ch.necklaces) { for (const [sid, it] of Object.entries(ch.necklaces)) { (ch.shirts ||= {})[sid] = conv(it); n++; } delete ch.necklaces; }
  if (ch.equip?.neck?.setNeck) {
    const it = conv(ch.equip.neck); delete ch.equip.neck; n++;
    if (ch.equip.shirt) (ch.shirts ||= {})[it.setShirt] = it; else ch.equip.shirt = it;
  }
  for (const list of [ch.inv, ch.stash || []]) list.forEach((it, i) => { if (it?.setNeck) { list[i] = conv(it); n++; } });
  if (!n) return;
  save();
  setTimeout(() => toast(`Tus collares de conjunto son ahora camisetas encantadas (${n}): se llevan debajo de todo, en un sitio propio, y el cuello queda libre para un collar.`, "levelup", 7000), 900);
}
function migrateModes() {
  for (const z of ZONES) {
    const zp = z.modes && ch.zones[z.id];
    if (!zp || zp.mode) continue;
    let p = zp.pack || 0;
    zp.mode = "verb";
    for (const m of ["verb", "word", "gap"]) { const n = z.fightsOf(m).length; if (p < n || m === "gap") { zp.mode = m; zp.pack = Math.min(p, n - 1); break; } p -= n; }
    if (zp.cleared) (zp.done ||= {}).gap = true;
  }
}
// switch a course zone to another mode; each mode keeps its own place
function setMode(zid, m) {
  const zp = (ch.zones[zid] ||= { pack: 0, cleared: false, depth: 0 });
  (zp.byMode ||= {})[modeOf(zid)] = zp.pack;
  zp.mode = m; zp.pack = zp.byMode[m] || 0;
}
const courseFight = (z, pack) => z.fights[Math.min(pack, z.fights.length - 1)];
// Progress through the zones is kept per episode (ch.zonesByEp; ch.zones is the current one's). A new
// episode starts at the first zone with every zone's levels shifted so it begins at your level then
// (ch.epShift, fixed for the episode). The progress from before this belongs to the episode in play
// when it arrived, unshifted.
function useEpisodeZones() {
  if (!ch || !S.ep) return;
  const by = (ch.zonesByEp ||= {}), shift = (ch.epShift ||= {});
  if (!by[S.ep]) {
    const first = !ch.zonesEp; // the first time: what there is so far is this episode's
    by[S.ep] = first && ch.zones ? ch.zones : { paramo: { pack: 0, cleared: false, depth: 0 } };
    shift[S.ep] = first ? 0 : Math.max(0, (ch.level || 1) - 1);
  }
  ch.zonesEp = S.ep;
  ch.zones = by[S.ep];
}
const epShift = () => ch?.epShift?.[S.ep] || 0;
// the button on the map: this episode's zones as if opening it for the first time, at your level now
function restartEpisode() {
  ch.zonesByEp[S.ep] = { paramo: { pack: 0, cleared: false, depth: 0 } };
  ch.epShift[S.ep] = Math.max(0, (ch.level || 1) - 1);
  ch.zones = ch.zonesByEp[S.ep];
  save();
}
// a zone with this episode's levels (the review zones keep their own)
const atLevel = (z) => (!z?.lvl || !epShift() || !ZONES.includes(z) ? z : { ...z, lvl: [z.lvl[0] + epShift(), z.lvl[1] + epShift()] });
async function loadEpisode(id) {
  S.ep = id;
  store.set("lastEp", id);
  S.T = await (await fetch(`media/${encodeURIComponent(id)}/transcript.json`, { cache: "no-cache" })).json();
  installZones(S.T);
  S.lines = S.T.segments.map((s, i) => (playable(s) ? i : -1)).filter((i) => i >= 0);
  // every line that could be played if it weren't flagged: zones are cut from this,
  // so flagging a line removes just that line instead of shifting every zone
  S.base = S.T.segments.map((s, i) => (playable({ ...s, flagged: undefined }) ? i : -1)).filter((i) => i >= 0);
  useEpisodeZones(); save();
  audio.src = `media/${encodeURIComponent(id)}/audio.mp3`;
  $("#listenLink").href = `./?ep=${encodeURIComponent(id)}`;
  $("#dictLink").href = `play.html?ep=${encodeURIComponent(id)}`;
}
// ---------- fixed passages ----------
// Each zone is a fixed stretch of the episode: every group has the same 6 lines and the boss
// the same 12, in order, every time. Replaying a zone means hearing the same audio again.
const PER_PACK = 6, PER_BOSS = 12;
const zoneSize = (z) => z.packs * PER_PACK + PER_BOSS;
function zoneStart(z) {
  let off = 0;
  for (const q of ZONES) { if (q === z) break; off += zoneSize(q); }
  return off;
}
function zoneOffset(z, depth = 0) {
  const off = zoneStart(z) + (z.endless ? depth * zoneSize(z) : 0);
  // the Abismo's last descent ends where the episode ends (overlapping the one before), instead of running on into its start
  if (z.endless && depth === descentsOf(z) - 1 && S.base?.length) return Math.max(zoneStart(z), Math.min(off, S.base.length - zoneSize(z)));
  return off;
}
// A zone's boss waits until you've mastered half its lines. Until then every line of its stretch
// (the boss's old ones too) is shared out among the normal groups, and once you've beaten them all
// more groups come, the ones you know least first. The boss brings what's left: the lines you've
// never heard and the ones that have cost you most. Courses and El Remolino keep their own rules.
const BOSS_GATE = 0.5;
const gated = (z) => !z.fights && !z.dynamic && !z.review;
const zoneDone = (z, depth = 0) => { const zl = zoneLines(z, depth); return { n: zl.length, m: zl.filter((si) => lineMastered(si, "dict") || lineMastered(si, "cloze")).length }; };
const bossReady = (z, depth = 0) => { const { n, m } = zoneDone(z, depth); return m >= Math.ceil(n * BOSS_GATE); };
const bossNeed = (z, depth = 0) => { const { n, m } = zoneDone(z, depth); return `${m}/${Math.ceil(n * BOSS_GATE)}`; };
// past the last group with the boss not ready: the group whose lines you know least (ties: the next in turn)
function extraGroup(z, zp) {
  const k = zp.extra || 0, known = (p) => groupLines(z, p, zp.depth || 0).filter((si) => lineMastered(si)).length / Math.max(1, groupLines(z, p, zp.depth || 0).length);
  let best = k % z.packs;
  for (let j = 1; j < z.packs; j++) { const p = (k + j) % z.packs; if (known(p) < known(best)) best = p; }
  return best;
}
function groupLines(z, pack, depth = 0) {
  if (z.fights) return courseFight(z, pack).lines.filter((si) => !S.T.segments[si].flagged);
  if (z.dynamic) { const L = (ch.zones[z.id]?.lines || []).filter((si) => !S.T.segments[si]?.flagged), head = L.length - PER_BOSS; return pack >= z.packs ? L.slice(Math.max(0, head)) : L.slice(pack * PER_PACK, Math.min(head, (pack + 1) * PER_PACK)); }
  if (pack >= z.packs) return []; // the boss's lines are chosen when you meet it (bossLines)
  const N = zoneSize(z), a = Math.floor((pack * N) / z.packs), b = Math.floor(((pack + 1) * N) / z.packs);
  const off = zoneOffset(z, depth) + a, n = b - a;
  const ok = (si) => !S.T.segments[si].flagged;
  const out = [];
  for (let k = 0; k < n; k++) out.push(S.base[(off + k) % S.base.length]);
  const lines = out.filter(ok);
  // everything here was flagged: borrow the next good lines
  for (let k = n; !lines.length && k < S.base.length; k++) { const si = S.base[(off + k) % S.base.length]; if (ok(si)) lines.push(si); }
  return lines;
}
function zoneLines(z, depth = 0) {
  const out = [];
  for (let p = 0; p < z.packs + (gated(z) ? 0 : 1); p++) out.push(...groupLines(z, p, depth));
  return out;
}
// The Abismo goes on where the other zones stop: each descent is the next stretch of the episode,
// as many descents as it takes to reach its end (deeper still, the episode starts over).
const descentsOf = (z) => Math.max(1, Math.ceil((S.base.length - zoneStart(z)) / zoneSize(z)));
const deepest = (zp) => Math.max(zp?.maxDepth || 0, zp?.depth || 0);

// ---------- El Remolino: the episode's last level, made of what you struggled with ----------
// Opens once every line of the episode (the five zones and every descent of the Abismo) is mastered,
// by dictation or by filling the gaps. Each time you start it, it's built again from what has cost
// you most: the lines you've missed worst (ch.struggle) and the ones holding your weak words, the
// very worst kept for its boss. Getting a line perfect here halves its weight, so it changes as you go.
const REMOLINO = "remolino", REM_MAX = 36;
function episodeLines() {
  if (S.T?.zones) return [];
  const out = new Set(), ab = GAME_ZONES.find((z) => z.endless);
  for (const z of ZONES) if (!z.endless) zoneLines(z).forEach((si) => out.add(si));
  for (let d = 0; d < descentsOf(ab); d++) zoneLines(ab, d).forEach((si) => out.add(si));
  return [...out];
}
const lineDone = (si) => lineMastered(si, "dict") || lineMastered(si, "cloze");
const episodeDone = () => { const L = episodeLines(); return L.length > 0 && L.every(lineDone); };
// how much each line has cost you, hardest first
function struggleRank() {
  const L = ch.struggle?.[S.ep] || {}, weak = new Map(weakList().map((x) => [x.k, x.score]));
  const score = (si) => (L[si] || 0) + 0.3 * S.T.segments[si].words.reduce((t, w) => t + (weak.get(norm(w.w)) || 0), 0);
  const speed = (si) => { const s = S.T.segments[si]; return s.words.length / Math.max(0.5, s.end - s.start); };
  // past what you've missed, the fastest speech fills the rest
  return S.lines.filter((si) => S.T.segments[si].words.length >= 3).map((si) => ({ si, v: score(si), f: speed(si) }))
    .sort((a, b) => b.v - a.v || b.f - a.f);
}
function buildRemolino(zp) {
  const top = struggleRank().slice(0, REM_MAX);
  // groups climb towards the worst; the boss gets the very worst 12
  zp.lines = top.map((x) => x.si).reverse();
  zp.missed = top.filter((x) => x.v > 0).length;
}
function remolinoZone() {
  const ab = GAME_ZONES.find((z) => z.endless), zp = ch.zones[REMOLINO] ||= { pack: 0, cleared: false, depth: 0 };
  const n = (zp.lines || []).length;
  // its boss is the one of the stretch your worst line comes from
  const worst = zp.lines?.at(-1), home = worst == null ? ab : ZONES.find((z) => !z.endless && zoneLines(z).includes(worst)) || ab;
  const lvl = Math.max(ch.level, atLevel(ab).lvl[0] + 2 * descentsOf(ab));
  return { ...ab, id: REMOLINO, scene: "abismo", dynamic: true, endless: false, name: "El Remolino", boss: home.boss, lvl: [lvl, lvl + 4],
    packs: Math.max(0, Math.ceil((n - PER_BOSS) / PER_PACK)), blurb: "Todo lo que te ha costado de este episodio, girando junto." };
}
function remolinoCard() {
  if (S.T?.zones) return "";
  const L = episodeLines(), done = L.filter(lineDone).length, open = done === L.length && L.length > 0;
  const zp = ch.zones[REMOLINO], z = remolinoZone(), W = weakList().slice(0, 8);
  const prog = !open ? `Se abre cuando domines todas las frases del episodio (al dictado o con huecos): llevas ${done} de ${L.length}.`
    : zp?.lines && zp.pack > 0 ? `Grupo ${zp.pack + 1} de ${z.packs + 1}: ${z.packs ? `luego ${esc(BOSSNAME(z))}` : "el jefe"}`
    : zp?.wins ? `Superado ${zp.wins} ${zp.wins === 1 ? "vez" : "veces"}. Al entrar se rehace con lo que más te cuesta ahora.` : "Se arma al entrar con lo que más te ha costado.";
  return `<li class="remolino ${open ? "" : "locked"}" style="--scene:url('${new URL("rpg/scenes/abismo.png", location.href).href}')">
    <div><b>El Remolino</b> <span class="dim">nivel ${z.lvl[0]}–${z.lvl[1]}</span><p>Lo que más te ha costado de este episodio, todo junto: las frases que peor te han salido y las que llevan tus puntos débiles. Las peores, para el jefe. Cada frase que bordas aquí pesa la mitad la próxima vez.</p>
      <span class="prog">${prog}</span>
      ${!open ? `<div class="zmastery"><span class="zbar"><i style="width:${(done / Math.max(1, L.length)) * 100}%"></i></span>Episodio dominado: ${done}/${L.length} frases</div>` : ""}
      ${open && W.length ? `<div class="wchips">${W.map((x) => `<span class="wchip ${x.leech ? "leech" : ""}">${esc(x.w)}</span>`).join("")}</div>` : ""}
      ${open ? `<div class="zmastery"><span class="zprize ${zp?.wins ? "got" : ""}">${zp?.wins ? "la primera vez: mítico (recibido); ahora: legendario" : "premio: un objeto mítico la primera vez, legendario después"}</span></div>` : ""}</div>
    ${open ? `<button data-zone="${REMOLINO}" class="primary">${zp?.lines && zp.pack > 0 ? "Seguir" : "Entrar"}</button>` : ""}</li>`;
}
// Mastery is kept twice in an episode: by dictation (melee, every word) and by filling the gaps
// (ranged), so a line mastered one way can still be mastered the other. Which counts goes with the
// weapon in your hand. A course keeps one, its modes decide the exercise.
const scoreKind = () => (S.T?.zones || stats().kind !== "ranged" ? "dict" : "cloze");
const mastery = (kind = scoreKind()) => { const k = kind === "cloze" ? "masteryCloze" : "mastery"; return ((ch[k] ||= {})[S.ep] ||= {}); };

// Easier difficulties split a line into short chunks (always the same ones), each its own attack.
function chunks(si, max) {
  const w = S.T.segments[si].words, n = w.length;
  if (n <= max) return [{ si, a: 0, b: n }];
  const out = [];
  let a = 0;
  while (a < n) {
    let b = Math.min(n, a + max);
    if (b < n) for (let k = b; k > a + 1; k--) if (/[,.;:?!…]$/.test(w[k - 1].w)) { b = k; break; } // end at a pause
    if (n - b === 1) b = b - a < max ? n : b - 1; // don't leave one word on its own
    out.push({ si, a, b });
    a = b;
  }
  return out;
}
const exKey = (e) => (e.a === 0 && e.b === S.T.segments[e.si].words.length ? `${e.si}` : `${e.si}:${e.a}-${e.b}`) + (e.v ? "#2" : "");
// Filling the gaps, every line (or chunk) comes twice: the second time with other words missing.
function clozeBlanks(e, words) {
  const key = e.si * 64 + e.a, segs = { [key]: { words } }, n = E.diffOf(ch).cloze;
  const first = chooseBlanks(segs, key, n);
  return e.v ? chooseBlanks(segs, key, n, first) : first;
}
const hasSecond = (e) => { const w = S.T.segments[e.si].words.slice(e.a, e.b); return clozeBlanks({ ...e, v: 1 }, w).join() !== clozeBlanks(e, w).join(); };
const exMastered = (e, kind, M = mastery(kind)) => (M[exKey(e)] ?? 0) >= 1;
// a line counts as mastered if you got it all perfect, whole or chunk by chunk
// (filling the gaps: both passes, where the line has a second one)
const passes = (e, kind, M) => exMastered(e, kind, M) && ((kind ?? scoreKind()) !== "cloze" || !hasSecond(e) || exMastered({ ...e, v: 1 }, kind, M));
const lineMastered = (si, kind, M) => passes({ si, a: 0, b: S.T.segments[si].words.length }, kind, M) || [4, 8].some((mx) => { const c = chunks(si, mx); return c.length > 1 && c.every((e) => passes(e, kind, M)); });
const mastered = (lines, kind) => lines.filter((si) => lineMastered(si, kind)).length;
function buildQueue(slot = {}) {
  const zp = ch.zones[S.zone.id];
  if (slot.boss && gated(S.zone)) return bossQueue(S.zone, zp.depth || 0);
  const lines = groupLines(S.zone, slot.group ?? zp.pack, zp.depth || 0);
  // a course's sentences are short and asked whole
  const fight = S.zone.fights && courseFight(S.zone, zp.pack);
  const all = fight?.items ? fight.items.filter((it) => lines.includes(it.si)).map((it) => ({ ...it }))
    : fight ? lines.map((si) => ({ si, a: 0, b: S.T.segments[si].words.length })) : lines.flatMap((si) => chunks(si, E.diffOf(ch).maxWords));
  // lines you've never heard come first, then the ones you've missed, then the mastered ones
  // (each in story order): a fight that ends quickly would otherwise keep giving you the same
  // opening lines while the later ones go unheard
  const M = mastery();
  const rank = (e) => (exMastered(e) || lineMastered(e.si) ? 2 : M[exKey(e)] != null ? 1 : 0);
  if (fight || scoreKind() !== "cloze") return bossMix([0, 1, 2].flatMap((r) => all.filter((e) => rank(e) === r)), fight);
  // filling the gaps: each one's second pass, other words missing, two exercises after its first
  const both = [];
  all.forEach((e, k) => { both.push(e); if (k >= 2 && hasSecond(all[k - 2])) both.push({ ...all[k - 2], v: 1 }); });
  for (const e of all.slice(-2)) if (hasSecond(e)) both.push({ ...e, v: 1 });
  return bossMix([0, 1, 2].flatMap((r) => both.filter((e) => rank(e) === r)), fight);
}
// A zone's boss brings the lines of its stretch you haven't mastered: the ones you've never heard
// (in story order) taking turns with the ones that have cost you most (weighted by how much they've
// cost, how badly you did and how recently you missed them, with a little chance so no two fights
// are the same). Later bosses bring more; Difícil and deeper descents add more, Fácil fewer. A few
// lines you already know wait at the very end, in case the fight outlasts the rest.
function bossQueue(z, depth) {
  const zi = Math.max(0, ZONES.indexOf(z)), diff = ch.difficulty || "medio";
  const want = PER_BOSS + Math.max(2, Math.min(18, 3 + 2 * zi + (diff === "dificil" ? 3 : diff === "facil" ? -2 : 0) + Math.min(6, depth)));
  const M = mastery(), A = missAt(), cost = ch.struggle?.[S.ep] || {}, cloze = scoreKind() === "cloze";
  const exs = (si) => chunks(si, E.diffOf(ch).maxWords).flatMap((c) => (cloze && hasSecond(c) ? [c, { ...c, v: 1 }] : [c]));
  const fresh = [], hard = [], known = [];
  for (const si of zoneLines(z, depth)) {
    if (S.T.segments[si].flagged) continue;
    if (lineMastered(si)) { known.push(...exs(si)); continue; }
    const open = exs(si).filter((e) => !((M[exKey(e)] ?? 0) >= 1));
    if (!open.length) continue;
    if (open.every((e) => M[exKey(e)] == null) && !cost[si]) { fresh.push(open); continue; }
    const tried = open.filter((e) => M[exKey(e)] != null);
    const worst = tried.length ? Math.min(...tried.map((e) => M[exKey(e)])) : 0;
    const last = Math.max(0, ...open.map((e) => A[exKey(e)] || 0)), ago = last ? (Date.now() - last) / 864e5 : 30;
    hard.push({ open, w: ((cost[si] || 0) + (1 - worst) * 2 + 1 / (1 + ago)) * (0.75 + Math.random() * 0.5) });
  }
  hard.sort((a, b) => b.w - a.w);
  const out = [];
  let nf = 0, nh = 0;
  while (out.length < want && (nf < fresh.length || nh < hard.length)) {
    if (nh < hard.length) out.push(...hard[nh++].open.map((e) => ({ ...e, back: true })));
    if (out.length < want && nf < fresh.length) out.push(...fresh[nf++]);
  }
  out.push(...known.sort(() => Math.random() - 0.5).slice(0, 6));
  out.misses = nh; out.fresh = nf;
  return out;
}
// El Remolino's boss knows what you've missed. Besides its own lines it brings back phrases you've heard
// and not yet got to 100%, drawn at random but weighted to the worst and the most recently missed,
// so no two boss fights are the same. Its own lines you already know are swapped for more of these.
function bossMix(own, course) {
  const zp = ch.zones[S.zone.id], depth = zp.depth || 0;
  if (course || S.zone.review || gated(S.zone) || zp.pack < S.zone.packs) return own;
  const zi = Math.max(0, ZONES.indexOf(S.zone)), diff = ch.difficulty || "medio";
  const want = Math.max(2, Math.min(18, 3 + 2 * zi + (diff === "dificil" ? 3 : diff === "facil" ? -2 : 0) + Math.min(6, depth)));
  const from = new Set(zoneLines(S.zone, depth));
  const mine = new Set(own.map((e) => e.si)), M = mastery(), A = missAt(), cloze = scoreKind() === "cloze";
  const pool = [];
  for (const si of from) {
    if (mine.has(si) || S.T.segments[si].flagged || lineMastered(si)) continue;
    for (const c of chunks(si, E.diffOf(ch).maxWords)) for (const e of cloze && hasSecond(c) ? [c, { ...c, v: 1 }] : [c]) {
      const best = M[exKey(e)];
      if (best >= 1) continue; // already right
      // never heard: a little chance; missed: more the worse it went and the more recently
      if (best == null) { pool.push({ e, w: 0.4 }); continue; }
      const ago = A[exKey(e)] ? (Date.now() - A[exKey(e)]) / 864e5 : 30; // days since you last missed it
      pool.push({ e, w: 0.6 + (1 - best) * 2 + 1 / (1 + ago) });
    }
  }
  // the boss's own lines you already know give their place to ones you don't (if there are any);
  // they only come at the very end, in case the fight outlasts everything else
  const known = (e) => exMastered(e) || lineMastered(e.si);
  const ownOpen = own.filter((e) => !known(e)), ownDone = own.filter(known);
  const picked = [];
  while (picked.length < want + ownDone.length && pool.length) {
    let r = Math.random() * pool.reduce((t, p) => t + p.w, 0), k = 0;
    while (k < pool.length - 1 && (r -= pool[k].w) > 0) k++;
    picked.push({ ...pool.splice(k, 1)[0].e, back: true });
  }
  // one you've missed, then one of the boss's own you don't know yet, until they run out
  const out = [];
  for (let k = 0; k < Math.max(picked.length, ownOpen.length); k++) { if (picked[k]) out.push(picked[k]); if (ownOpen[k]) out.push(ownOpen[k]); }
  out.push(...ownDone);
  out.misses = picked.length;
  return out;
}
// When each line (or chunk, or card) was last missed: it rests a while before coming back.
const REST_MS = 5 * 60 * 1000;
const missAt = () => ((ch.missAt ||= {})[S.ep] ||= {});
const resting = (e) => Date.now() - (missAt()[exKey(e)] || 0) < REST_MS;
const exWords = () => (S.F.ex.card ? S.F.ex.card.words : S.T.segments[S.F.si].words.slice(S.F.ex.a, S.F.ex.b));
const exText = () => exWords().map((w) => w.w).join(" ");

// ---------- audio ----------
let stopAt = null;
function playSeg(si, rate = 1) {
  const F = S.F;
  if (F?.ex?.card) return playCard(F.ex.card, rate);
  cardAudio.pause();
  let s = S.T.segments[si];
  // an exercise that's part of a line plays only its part; a course's word card plays its whole sentence
  if (F?.ex && F.ex.si === si && F.ex.k == null) { const w = exWords(); s = { start: w[0].s, end: w[w.length - 1].e }; }
  const fast = F && alive(F).some((m) => m.mods.includes("veloz"));
  const quiet = F && alive(F).some((m) => m.mods.includes("murmullo"));
  audio.playbackRate = rate * (fast ? 1.15 : 1);
  audio.volume = quiet ? 0.4 : 1;
  audio.currentTime = Math.max(0, s.start - 0.12);
  stopAt = s.end + 0.2;
  hush();
  audio.play();
  const b = bossOf(F);
  if (b && bossRules(F) && F.boss.armed && !F.checked && BOSSES[b.kind].special.wail && !isEasy()) wailOver((s.end - s.start + 0.4) / audio.playbackRate);
}
// Any stretch of the episode (trials, casetes, the grimoire), with no monster effects.
function playRange(start, end, rate = 1) {
  cardAudio.pause();
  audio.playbackRate = rate;
  audio.volume = 1;
  audio.currentTime = Math.max(0, start - 0.12);
  stopAt = end + 0.2;
  hush();
  audio.play();
}
function playCard(card, rate = 1) {
  if (!card.audio) return toast("Esta tarjeta no tiene audio");
  audio.pause();
  const src = `api/review/media?file=${encodeURIComponent(card.audio)}`;
  if (!cardAudio.src.endsWith(src)) cardAudio.src = src;
  cardAudio.playbackRate = rate;
  cardAudio.currentTime = 0;
  hush();
  cardAudio.play().catch(() => {});
}
// checked every frame, and on the audio's own progress events: frames stop in a background tab,
// where without them a line would play on into the rest of the episode
function checkStop() { if (stopAt != null && !audio.paused && audio.currentTime >= stopAt) { audio.pause(); stopAt = null; } }
(function watch() { checkStop(); requestAnimationFrame(watch); })();
audio.addEventListener("timeupdate", checkStop);

// ---------- HUD ----------
function renderHud() {
  if (!ch) return;
  const st = stats();
  ch.life = Math.min(ch.life, st.maxLife);
  ch.mana = Math.min(ch.mana, st.maxMana);
  const orb = (el, v, max) => {
    el.querySelector(".fill").style.height = `${Math.max(0, (v / max) * 100)}%`;
    el.querySelector("span").textContent = `${Math.max(0, Math.round(v))}/${max}`;
  };
  orb($("#lifeOrb"), ch.life, st.maxLife);
  orb($("#manaOrb"), ch.mana, st.maxMana);
  const need = E.xpToNext(ch.level);
  $("#xpFill").style.width = `${(ch.xp / need) * 100}%`;
  $("#xpTxt").textContent = `Nivel ${ch.level} · ${ch.xp}/${need} exp`;
  const belt = $("#belt");
  belt.replaceChildren();
  for (let i = 0; i < st.beltSlots; i++) {
    const p = ch.belt[i];
    const b = h(`<button class="slot pot" ${p ? `data-id="${p.id}"` : "disabled"}>${p ? itemIco(p) : ""}<kbd>${i < 9 ? i + 1 : ""}</kbd></button>`);
    if (p) b.onclick = () => drink(p.id);
    belt.append(b);
  }
  renderSpells(st);
  const w = ch.equip[`weapon${ch.swap}`];
  $("#swapBtn").innerHTML = `<span class="set">${ch.swap === 1 ? "I" : "II"}</span>${w ? itemIco(w) : icon("crossed-swords", "#777")}<span class="mode">${st.kind === "ranged" ? "Huecos" : "Dictado"}</span>`;
}

// The brujo's spells: one kept prepared (ch.spell), cast with every attack while there's mana.
function renderSpells(st = stats()) {
  const bar = $("#spells");
  const list = E.spellsFor(ch), pw = E.powerOf(ch);
  bar.hidden = !list.length && !pw;
  if (bar.hidden) return;
  const can = E.canCast(ch, st);
  bar.innerHTML = powerButton(st) + list.map((sp) => {
    const locked = ch.level < sp.lvl, cost = E.spellCost(ch, sp), on = ch.spell === sp.id && !locked;
    const why = locked ? `Se aprende en el nivel ${sp.lvl}.` : !can ? "Necesitas una varita, un cetro o un bastón." : on ? "Preparado: sale con cada ataque. Clic para guardarlo." : "Clic para prepararlo.";
    return `<button class="spell${on ? " on" : ""}${locked ? " locked" : ""}" data-spell="${sp.id}" style="--sc:${sp.color}" ${locked ? "disabled" : ""}
      title="${esc(`${sp.name} (${cost} de maná): ${sp.desc} ${why}`)}">${icon(sp.icon, locked ? "#666" : sp.color)}<span class="sn">${locked ? `nv ${sp.lvl}` : cost}</span><kbd>${sp.key.toUpperCase()}</kbd></button>`;
  }).join("");
  bar.classList.toggle("nowand", !can);
  bar.querySelectorAll("[data-spell]").forEach((b) => (b.onclick = () => prepSpell(b.dataset.spell)));
  bar.querySelector("[data-power]")?.addEventListener("click", usePower);
  $("#powBtn")?.classList.toggle("on", S.view === "fight" && powerOn());
}
// The runes and their sets, in the Alambique tab: what each set asks and gives, and which runes you have.
function runaGuide() {
  const have = {};
  for (const it of [...ch.inv, ...(ch.stash || [])]) if (it.kind === "runa") have[it.runa] = (have[it.runa] || 0) + 1;
  const tiers = Object.entries(RUNA_TIERS).map(([t, T]) => `<div class="runarow"><b style="color:${T.color}">${T.name.replace("Runa ", "")}:</b> ${RUNAS.filter((r) => r.tier === t).map((r) => `<span class="${have[r.id] ? "" : "dim"}" title="${esc(`«${r.gloss}» · nivel ${r.lvl} · arma: ${E.propText(...r.w)} · armadura: ${E.propText(...r.a)} · escudo: ${E.propText(...r.o)}`)}">${esc(r.name)}${have[r.id] ? ` <span class="small">×${have[r.id]}</span>` : ""}</span>`).join(" · ")}</div>`).join("");
  return `<section class="runaguide"><h3>Runas y conjuntos rúnicos</h3>
    <p class="dim small">Las runas caen muy de vez en cuando (las medias, raras; las altas, casi nunca) y se engastan como las gemas: cada una da lo suyo según dónde esté. Si todas las runas de un conjunto están en un mismo objeto blanco, en cualquier orden, despierta y da además su bonificación. Un objeto blanco de 5 o 6 engastes con un conjunto alto puede valer más que un legendario. Aquí, en el alambique, 3 runas iguales hacen la siguiente. Las que tienes en la bolsa o el alijo, sin atenuar.</p>
    ${tiers}
    <div class="runasets">${RUNA_SETS.map((rs) => runaSetHtml(rs, Object.keys(have))).join("")}</div></section>`;
}
// The keyboard shortcuts, listed in the village's Mercader tab (keep in step with the keydown handler).
function keysCard() {
  const alt = /Mac|iPhone|iPad/.test(navigator.platform) ? "Opción" : "Alt", pw = E.powerOf(ch);
  const k = (...ks) => ks.map((x) => `<kbd>${x}</kbd>`).join(" + ");
  const group = (title, rows) => `<div class="keysgroup"><h4>${title}</h4><dl>${rows.map(([keys, what]) => `<dt>${keys}</dt><dd>${what}</dd>`).join("")}</dl></div>`;
  return `<section class="keyscard"><h3>Atajos de teclado</h3>
    <p class="dim small">Con ${alt} funcionan también mientras escribes la respuesta.</p>
    <div class="keysgrid">
    ${group("Pociones", [
      [`${k("1")} … ${k("9")}`, "Bebe la poción de ese hueco del cinturón"],
      [k(alt, "1"), "Una poción de vida"], [k(alt, "2"), "Una de maná"], [k(alt, "3"), "Una de rejuvenecimiento"],
    ])}
    ${group("En combate", [
      [k("Enter"), "Ataca con lo que escribiste; después, sigue"],
      [k("Tab"), "Vuelve a oír la frase (en los huecos, pasa al siguiente)"],
      [k("Mayús", "Tab"), "La oyes despacio"],
      [k(alt, "H"), "Pista"],
      ...(pw ? [[`${k("F")} o ${k(alt, "F")}`, `${esc(pw.name)}, tu habilidad de clase`]] : []),
      ...(E.spellsFor(ch).length ? [[`${k("Q")} ${k("W")} ${k("E")} ${k("R")}`, `Prepara un hechizo (o ${alt} con la letra)`]] : []),
      [k("V"), "Tras la frase: conjura repitiéndola en voz alta (otra vez V para parar)"],
      [k("G"), "Tras la frase: abre el grimorio, si lo tienes"],
      [`${k("Espacio")} y ${k("1")}–${k("4")}`, "En las tarjetas: muestra la respuesta y califícala"],
    ])}
    ${group("En todas partes", [
      [k(alt, "S"), "Cambia de armas (I y II)"],
      [k("C"), "Personaje"], [k("I"), "Inventario"], [k("M"), "Sonido sí / no"],
      [k("Esc"), "Cierra paneles y ventanas"],
    ])}
    </div></section>`;
}
// The class ability (POWERS): one per class, for a fight, paid with a share of your maximum mana.
const powerOn = (F = S.F) => !!(F && (F.power || F.roar > 0));
function powerButton(st) {
  const pw = E.powerOf(ch);
  if (!pw) return "";
  const cost = E.powerCost(ch, st), F = S.F, on = S.view === "fight" && powerOn(F);
  const state = on ? (F.power ? "Preparada: sale con tu próximo golpe." : `Activa: ${F.roar === 1 ? "queda 1 turno" : `quedan ${F.roar} turnos`}.`) : "Úsala en un combate (F, o Alt+F mientras escribes).";
  return `<button class="spell power${on ? " on" : ""}" data-power style="--sc:${pw.color}" title="${esc(`${pw.name} (${cost} de maná): ${pw.desc} ${state}`)}">${icon(pw.icon, pw.color)}<span class="sn">${cost}</span><kbd>F</kbd></button>`;
}
function usePower() {
  const pw = E.powerOf(ch), F = S.F, st = stats();
  if (!pw) return;
  if (S.view !== "fight" || !F || F.over || !alive(F).length) return toast(`${pw.name}: solo en un combate`);
  if (powerOn(F)) return toast(F.power ? `${pw.name} ya está preparada: sale con tu próximo golpe` : `${pw.name} sigue activa (${F.roar} ${F.roar === 1 ? "turno" : "turnos"} más)`);
  if (pw.heal && ch.life >= st.maxLife && !F.boss?.burn) return toast("Tienes la vida entera: no hay nada que sanar");
  const cost = E.powerCost(ch, st);
  if (!spend(cost)) return;
  if (pw.arm) { F.power = pw.id; addLog(`<b style="color:${pw.color}">${esc(pw.name)}</b> <span class="dim">(−${cost} de maná)</span>: sale con tu próximo golpe.`, "good"); }
  if (pw.roar) { F.roar = pw.turns; addLog(`<b style="color:${pw.color}">¡${esc(pw.name)}!</b> <span class="dim">(−${cost} de maná)</span> Los monstruos se encogen: durante ${pw.turns} turnos te hacen la mitad de daño.`, "good"); }
  if (pw.heal) {
    const before = ch.life;
    ch.life = Math.min(st.maxLife, ch.life + Math.round(st.maxLife * pw.heal));
    const burnt = F.boss?.burn > 0; if (burnt) F.boss.burn = 0;
    addLog(`<b style="color:${pw.color}">${esc(pw.name)}</b> <span class="dim">(−${cost} de maná)</span>: recuperas <b>${Math.round(ch.life - before)}</b> de vida${burnt ? " y se apaga el fuego" : ""}.`, "good");
    flashOrb("#lifeOrb", "heal");
  }
  sfx.spell(1);
  save(); renderHud();
}
function prepSpell(id) {
  const sp = E.spellsFor(ch).find((x) => x.id === id);
  if (!sp) return;
  if (ch.level < sp.lvl) return toast(`${sp.name} se aprende en el nivel ${sp.lvl}`);
  ch.spell = ch.spell === id ? null : id;
  save(); renderSpells();
  if (!ch.spell) return toast(`Guardas ${sp.name}: atacas sin hechizo`);
  toast(E.canCast(ch, stats()) ? `${sp.name} preparado: sale con cada ataque (${E.spellCost(ch, sp)} de maná)` : `${sp.name} preparado, pero necesitas una varita, un cetro o un bastón`);
}

function drink(id) {
  const i = ch.belt.findIndex((p) => p.id === id);
  if (i < 0) return;
  const p = ch.belt[i], st = stats(), P = POTIONS[p.potion];
  const boost = 1 + st.potion / 100;
  if (p.potion === "life") ch.life = Math.min(st.maxLife, ch.life + Math.round(P.heal[p.tier] * boost));
  if (p.potion === "mana") ch.mana = Math.min(st.maxMana, ch.mana + Math.round(P.mana[p.tier] * boost));
  if (p.potion === "rejuv") { ch.life = Math.min(st.maxLife, ch.life + st.maxLife * P.pct); ch.mana = Math.min(st.maxMana, ch.mana + st.maxMana * P.pct); }
  ch.belt.splice(i, 1);
  save(); renderHud(); flashOrb(p.potion === "mana" ? "#manaOrb" : "#lifeOrb", "heal");
}
function drinkType(type) {
  const p = ch.belt.find((x) => x.potion === type);
  if (p) drink(p.id); else toast(`No te quedan pociones de ${type === "life" ? "vida" : type === "mana" ? "maná" : "rejuvenecimiento"}`);
}
function flashOrb(sel, cls) {
  const el = $(sel);
  el.classList.remove("hit", "heal"); void el.offsetWidth; el.classList.add(cls);
}

function swapWeapons() {
  ch.swap = ch.swap === 1 ? 2 : 1;
  save(); renderHud(); renderPanels(); renderMe();
  if (S.F && !S.F.checked && S.F.si != null) setupExercise(true);
  if (S.F && !S.F.review) renderGroupMastery();
  toast(`Armas ${ch.swap === 1 ? "I" : "II"}: ${stats().kind === "ranged" ? "atacas rellenando huecos" : "atacas dictando"}`);
}
$("#swapBtn").onclick = swapWeapons;

// ---------- tooltips & item menu ----------
function tooltipHtml(it, compare = true) {
  const color = E.itemColor(it);
  let out = `<div class="tname${it.rarity === "tunjo" ? " rainbow" : ""}" style="color:${color}">${esc(E.itemName(it))}</div>`;
  if (it.kind === "gem") {
    const g = GEMS[it.gem];
    out += `<div class="tsub">Gema</div>`;
    for (const [where, label] of [["weapon", "En un arma"], ["armor", "En casco o torso"], ["off", "En un escudo"]]) {
      const e = E.gemEffect(it.gem, it.grade, where === "armor" ? "head" : where);
      out += `<div class="tline"><span class="dim">${label}:</span> ${esc(E.propText(e.prop, e.value))}</div>`;
    }
    return out + `<div class="tsub">Valor: ${E.itemValue(it)} de oro</div>`;
  }
  if (it.kind === "runa") {
    const r = RUNA[it.runa], sets = RUNA_SETS.filter((x) => x.runas.includes(r.id));
    out += `<div class="tsub" style="color:${color}">${RUNA_TIERS[r.tier].name} · «${esc(r.gloss)}» en muisca</div>`;
    for (const [k, label] of RUNA_KINDS) out += `<div class="tline"><span class="dim">${label}:</span> ${esc(E.propText(...r[k]))}</div>`;
    if (r.lvl > 1) out += `<div class="tline dim">El objeto en que la engastes pide nivel ${r.lvl}.</div>`;
    if (sets.length) out += `<div class="tline dim">Forma parte de:</div>` + sets.map((x) => runaSetHtml(x)).join("");
    out += `<div class="tline dim">Un conjunto rúnico despierta cuando todas sus runas están en un mismo objeto blanco (normal, superior o gastado), en cualquier orden.</div>`;
    return out + `<div class="tsub">Valor: ${E.itemValue(it)} de oro</div>`;
  }
  if (it.kind === "relic") return out + `<div class="tsub" style="color:${color}">Reliquia · muy rara</div><div class="tline">En la aldea, en el Montón: por cada ${MOUND_STEP} gemas perfectas del montón, un objeto mítico, una mascota o una montura. Se gasta al usarlo; las gemas que sobren se quedan.</div><div class="tsub">No se vende</div>`;
  if (it.kind === "potion") {
    const P = POTIONS[it.potion];
    const txt = it.potion === "life" ? `Recupera ${P.heal[it.tier]} de vida` : it.potion === "mana" ? `Recupera ${P.mana[it.tier]} de maná` : "Recupera el 40% de vida y maná";
    return out + `<div class="tline">${txt}</div>`;
  }
  const base = BASE[it.base];
  if (["rare", "unique", "set", "crafted", "runeword", "ancestral", "legendario", "mitico", "tunjo"].includes(it.rarity)) out += `<div class="tsub" style="color:${color}">${esc(base.name)}</div>`;
  const kindName = it.rarity === "crafted" && it.craft ? `Artesanal ${CRAFT[it.craft].name}` : RARITY[it.rarity].name;
  out += `<div class="tsub">${kindName}${base.tier ? ` · ${TIERS[base.tier].name}` : ""}${base.band ? ` · <span class="band" title="${esc(BANDS.find((b) => b.id === base.band).desc)}">${esc(BANDS.find((b) => b.id === base.band).name)}</span>` : ""} · ${SLOTS[base.slot]}${base.twoHanded ? " · a dos manos" : base.slot === "weapon" ? " · a una mano" : ""}</div>`;
  if (it.unid) return out + `<div class="tline unid">Sin identificar</div><div class="tline dim">Clic → Identificar: oyes una frase corta y la escribes. Don Eusebio te ayuda, por oro.</div><div class="tsub">Valor: ${E.itemValue(it)} de oro</div>`;
  if (base.dmg) {
    const d = E.itemDamage(it), w = weaponTotals(it);
    out += `<div class="tline">Daño: <b>${d[0]}–${d[1]}</b>${w.ownPct ? ` <span class="dim">(base ${base.dmg[0]}–${base.dmg[1]}, ${w.ownPct > 0 ? "+" : ""}${w.ownPct}%)</span>` : ""}</div>`;
    if (w.extra) out += `<div class="tline">Con lo elemental: <b>${d[0] + w.extra}–${d[1] + w.extra}</b> <span class="dim">(${w.elems})</span></div>`;
    out += `<div class="tline">Por golpe con tu personaje: <b>${w.you[0]}–${w.you[1]}</b>${w.why.length ? ` <span class="dim">(${w.why.join(", ")})</span>` : ""}</div>`;
    out += `<div class="tline dim">${base.kind === "ranged" ? "A distancia: atacas rellenando huecos" : "Cuerpo a cuerpo: atacas dictando la frase"}</div>`;
    if (base.magic) out += `<div class="tline" style="color:#b48cff">Arma mágica: con ella, el brujo lanza hechizos</div>`;
  }
  if (it.def) {
    const a = armorTotals(it), why = [`base ${it.def}`];
    if (a.ownPct) why.push(`${a.ownPct > 0 ? "+" : ""}${a.ownPct}%`);
    if (a.flat) why.push(`+${a.flat}`);
    out += `<div class="tline">Defensa: <b>${E.itemDefense(it)}</b>${why.length > 1 ? ` <span class="dim">(${why.join(", ")})</span>` : ""}</div>`;
    out += `<div class="tline">Tu defensa con esto puesto: <b>${a.you}</b>${a.you !== a.now ? ` <span class="dim">(ahora ${a.now})</span>` : ""} <span class="dim">· frena el ${a.dr}% del daño físico de un monstruo de tu nivel</span></div>`;
  }
  if (base.block) { const a = armorTotals(it); out += `<div class="tline">Bloqueo: ${base.block}%${a.block !== base.block ? ` <span class="dim">(con tu destreza${E.itemProps(it).block ? " y el escudo" : ""}: <b>${a.block}%</b>)</span>` : ""}</div>`; }
  const req = it.rarity === "tunjo" ? {} : base.req || {}, st = stats(), lreq = E.itemLevelReq(it);
  const reqs = [];
  if (lreq > 1) reqs.push(`<span class="${ch.level < lreq ? "bad" : ""}">Nivel ${lreq}</span>`);
  if (req.str) reqs.push(`<span class="${st.str < req.str ? "bad" : ""}">Fuerza ${req.str}</span>`);
  if (req.dex) reqs.push(`<span class="${st.dex < req.dex ? "bad" : ""}">Destreza ${req.dex}</span>`);
  if (reqs.length) out += `<div class="tline dim">Requiere: ${reqs.join(", ")}</div>`;
  if (it.rarity === "tunjo" && it.band) out += `<div class="tline rainbow">Crece contigo del nivel ${it.band[0]} al ${it.band[1]}: cada vez que subes se rehace a tu nivel, siempre mejor que cualquier objeto mágico o raro de ese nivel. Después del ${it.band[1]} se queda como está. No pide nada para llevarlo.</div>`;
  const sortP = (o) => Object.entries(o).sort((a, b) => (E.PROP_ORDER(a[0]) - E.PROP_ORDER(b[0])));
  const plist = (o) => sortP(o).map(([k, v]) => `<div>${esc(E.propText(k, v))}</div>`).join("");
  {
    const props = sortP(it.props);
    if (props.length) out += `<div class="tprops">` + props.map(([k, v]) => `<div>${esc(E.propText(k, v))}</div>`).join("") + `</div>`;
  }
  if (it.sockets) {
    out += `<div class="tline dim">Engastes: ${it.gems.length}/${it.sockets}</div>`;
    for (const g of it.gems) out += socketLine(g, base.slot);
    const rs = E.runaSetOf(it), have = it.gems.filter((g) => g.runa).map((g) => g.runa), kind = E.runaKind(base.slot);
    if (rs) out += `<div class="tline" style="color:${RUNA_TIERS.alta.color}">Conjunto rúnico despierto (sus bonificaciones ya están sumadas arriba de lo que da cada runa):</div>` + runaSetHtml(rs, have, true, kind);
    else if (have.length && E.isPlain(it)) {
      const near = RUNA_SETS.filter((x) => x.kinds.includes(kind) && x.runas.length <= it.sockets && have.every((r) => x.runas.includes(r)));
      if (near.length) out += `<div class="tline dim">Con sus runas va camino de:</div>` + near.map((x) => runaSetHtml(x, have, false, kind)).join("");
    } else if (have.length) out += `<div class="tline dim">Los conjuntos rúnicos solo despiertan en objetos blancos.</div>`;
  }
  if (it.setShirt) {
    const set = SETS.find((s) => s.id === it.setShirt), c = RARITY[set.tier || "set"].color;
    out += `<div class="tset"><div style="color:${c}">Todas las bonificaciones de ${esc(set.name)}</div>` +
      Object.entries(set.bonus).map(([n, b]) => `<div>(${n} piezas) ${Object.entries(b).map(([k, v]) => esc(E.propText(k, v))).join(", ")}</div>`).join("") +
      `<div class="dim">Más arriba, la mitad de las propiedades de sus piezas: ${set.pieces.map((p) => esc(p.name)).join(", ")}.</div>` +
      `<div class="dim">Se lleva debajo de todo, en su propio sitio. Con ella puesta se te ve con el conjunto entero, lleves lo que lleves encima (lo de encima sigue dando lo suyo); ${touch() ? "tócala" : "haz clic en ella"} puesta para elegir qué piezas se ven. Solo se guarda en tus camisetas: no se vende ni va al alijo.</div></div>`;
  }
  if (it.set) {
    const set = SETS.find((s) => s.id === it.set), have = E.setCounts(ch)[it.set] || 0;
    const owned = new Set(E.equippedItems(ch).filter((x) => x.set === it.set).map((x) => x.name));
    out += `<div class="tset"${set.tier ? ` style="color:${RARITY[set.tier].color}"` : ""}><div style="color:${RARITY[set.tier || "set"].color}">${esc(set.name)}${set.tier ? ` <span class="dim">· conjunto ${RARITY[set.tier].name.toLowerCase()}</span>` : ""}</div>` +
      // each piece: worn (bright), or a mark when it's in your bag or the stash (identified: an unidentified one doesn't count yet)
      (!it.unid && hasShirt(it.set) ? `<div class="sethave on">✓ Ya tienes su camiseta${ch.equip.shirt?.setShirt === it.set ? " (la llevas puesta)" : ""}: este conjunto no te hace falta para fundirla.</div>` : "") +
      set.pieces.map((p) => { const where = owned.has(p.name) ? "puesta" : ch.inv.some((x) => !x.unid && x.set === it.set && x.name === p.name) ? "en la bolsa" : (ch.stash || []).some((x) => !x.unid && x.set === it.set && x.name === p.name) ? "en el alijo" : "";
        return `<div class="${owned.has(p.name) ? "" : "dim"}">${esc(p.name)}${where ? ` <span class="sethave${owned.has(p.name) ? " on" : ""}">✓ ${where}</span>` : ""}</div>`; }).join("") +
      Object.entries(set.bonus).map(([n, b]) => `<div class="${have >= +n ? "" : "dim"}">(${n} piezas) ${Object.entries(b).map(([k, v]) => esc(E.propText(k, v))).join(", ")}</div>`).join("") + `</div>`;
  }
  if (it.flavor) out += `<div class="tflavor">${esc(it.flavor)}</div>`;
  if (compare) {
    const slots = equipTargets(it);
    const cur = slots.map((s) => ch.equip[s]).filter((x) => x && x.id !== it.id);
    if (cur.length && findItem(it.id)?.where !== "equip") out += `<div class="tcompare"><div class="dim">Llevas puesto:</div>${cur.map((c) => `<div class="tcmp">${tooltipHtml(c, false)}</div>`).join("")}</div>`;
  }
  return out;
}
function equipTargets(it) {
  if (it.kind) return [];
  const slot = BASE[it.base].slot;
  if (slot === "weapon") return [`weapon${ch.swap}`];
  if (slot === "off") return [`off${ch.swap}`];
  if (slot === "ring") return ["ring1", "ring2"];
  return [slot];
}
const ALEM_SIZE = 6; // the alembic: room for the biggest set (6 pieces)
const tip = $("#tip");
document.addEventListener("mouseover", (e) => {
  const el = e.target.closest("[data-id]");
  if (!el || !$("#menu").hidden) return;
  const f = findItem(el.dataset.id) || (S.loot && S.loot.items.find((x) => x.id === el.dataset.id) && { it: S.loot.items.find((x) => x.id === el.dataset.id) });
  if (!f) return;
  tip.innerHTML = tooltipHtml(f.it);
  tip.hidden = false;
  placeTip(el);
});
document.addEventListener("mouseout", (e) => { if (e.target.closest("[data-id], [data-pip]")) tip.hidden = true; });
// the progress circles over a fight: what each one is, at once (a native title is slow on something this small)
document.addEventListener("mouseover", (e) => {
  const el = e.target.closest("[data-pip]");
  if (!el) return;
  tip.innerHTML = `<div class="tline">${esc(el.dataset.pip)}</div>`;
  tip.hidden = false;
  placeTip(el);
});
function placeTip(el) {
  const r = el.getBoundingClientRect();
  const w = tip.offsetWidth, hh = tip.offsetHeight;
  let x = r.right + 10, y = r.top;
  if (x + w > innerWidth - 8) x = r.left - w - 10;
  if (x < 8) x = 8;
  if (y + hh > innerHeight - 8) y = innerHeight - hh - 8;
  tip.style.left = `${x}px`; tip.style.top = `${Math.max(8, y)}px`;
}

function openMenu(el, actions) {
  tip.hidden = true;
  const m = $("#menu");
  m.replaceChildren(...actions.map(([label, fn, dis]) => {
    const b = h(`<button ${dis ? "disabled" : ""}>${esc(label)}</button>`);
    b.onclick = () => { closeMenu(); fn(); };
    return b;
  }));
  m.hidden = false;
  const r = el.getBoundingClientRect();
  m.style.left = `${Math.min(innerWidth - m.offsetWidth - 8, r.left)}px`;
  m.style.top = `${Math.min(innerHeight - m.offsetHeight - 8, r.bottom + 4)}px`;
  m.querySelector("button:not([disabled])")?.focus();
}
function closeMenu() { $("#menu").hidden = true; }
document.addEventListener("pointerdown", (e) => { if (!e.target.closest("#menu") && !e.target.closest("[data-id]")) closeMenu(); });

function itemActions(id) {
  const f = findItem(id);
  if (!f) return [];
  const { it, where } = f;
  const inTown = S.view === "town";
  const A = [];
  if (where === "equip") {
    if (it.setShirt) A.push(["Qué piezas se ven…", () => shirtDisplay()]);
    A.push([it.setShirt ? "Quitártela (vuelve a tus camisetas)" : "Quitar", () => unequip(f.slot)]);
    return A;
  }
  if (where === "shirts") {
    const ok = E.canEquip(ch, it);
    A.push([ok ? "Ponértela" : `Ponértela (nivel ${E.itemLevelReq(it)})`, () => wearShirt(f.sid), !ok]);
    return A;
  }
  if (it.kind === "potion") {
    if (where !== "belt") A.push(["Al cinturón", () => toBelt(it.id), ch.belt.length >= stats().beltSlots]);
    if (where === "belt") A.push(["Beber", () => drink(it.id)]);
  } else if (it.kind === "gem" || it.kind === "runa") {
    const hosts = [...Object.values(ch.equip).filter(Boolean), ...ch.inv].filter((x) => !x.kind && !x.unid && x.sockets > x.gems.length);
    for (const host of hosts.slice(0, 8)) A.push([`Engastar en ${E.itemName(host)}`, () => socket(it.id, host.id)]);
    if (!hosts.length) A.push(["No tienes objetos con engastes libres", () => {}, true]);
  } else if (it.kind === "relic") {
    if (inTown) A.push(["Ir al Montón", () => { S.townTab = "monton"; renderTown(); renderPanels(); }]);
  } else if (it.unid && (where === "inv" || where === "stash")) {
    A.push(["Identificar", () => identify(it.id)]);
    A.push(["Equipar (identifícalo primero)", () => {}, true]);
  } else if (where === "inv") {
    const ok = E.canEquip(ch, it);
    const slot = BASE[it.base].slot;
    if (slot === "ring") { A.push(["Ponerse (anillo 1)", () => equip(it.id, "ring1"), !ok]); A.push(["Ponerse (anillo 2)", () => equip(it.id, "ring2"), !ok]); }
    else if (slot === "weapon" || slot === "off") {
      A.push([`Equipar en armas I`, () => equip(it.id, `${slot}1`), !ok]);
      A.push([`Equipar en armas II`, () => equip(it.id, `${slot}2`), !ok]);
    } else A.push([ok ? "Equipar" : "Equipar (no cumples los requisitos)", () => equip(it.id, slot), !ok]);
  }
  if (where === "inv" && S.view === "town" && S.townTab === "alembic") A.push(["Al alambique", () => toAlembic(it.id), S.alembic.length >= ALEM_SIZE]);
  if (where === "inv" && inTown) A.push(["Guardar en el alijo", () => move(it.id, ch.stash, STASH_SIZE, "El alijo está lleno")]);
  if (where === "stash") A.push(["Sacar al inventario", () => move(it.id, ch.inv, INV_SIZE, "El inventario está lleno")]);
  if (where === "belt") A.push(["Al inventario", () => move(it.id, ch.inv, INV_SIZE, "El inventario está lleno")]);
  if (inTown && where !== "belt" && it.kind !== "relic") A.push([`Vender (${E.itemValue(it)} de oro)`, () => sell(it.id)]);
  // throwing away is for good, so it asks once more
  if (!inTown && where === "inv") A.push(["Tirar…", () => setTimeout(() => openMenu(document.querySelector(`[data-id="${it.id}"]`) || $("#invPanel"), [
    [`Sí, tirar ${E.itemName(it)} para siempre`, () => { remove(it.id); save(); renderPanels(); toast(`Tiraste ${E.itemName(it)}`); }],
    ["No, quedármelo", () => {}],
  ]))]);
  return A;
}
document.addEventListener("click", (e) => {
  const el = e.target.closest("[data-id]");
  if (!el || el.closest("#belt") || el.closest(".ground")) return;
  e.preventDefault();
  // with the stash open, a click moves the item straight across (the menu is on right-click)
  // at the alembic, anything in the bag goes straight in (and comes back out with a click on it there)
  const g = S.view === "town" && S.townTab === "alembic" && findItem(el.dataset.id);
  if (g?.where === "inv") return S.alembic.length >= ALEM_SIZE ? toast("El alambique está lleno") : toAlembic(g.it.id);
  // at the Vender tab, a click on something in the bag sells it
  const v = S.view === "town" && S.townTab === "sell" && findItem(el.dataset.id);
  if (v?.where === "inv") return sell(v.it.id);
  // at the Montón, a click on a perfect gem in the bag throws it on the pile
  const mg = S.view === "town" && S.townTab === "monton" && findItem(el.dataset.id);
  if (mg?.where === "inv" && mg.it.kind === "gem" && mg.it.grade === 2) return throwGems(mg.it.gem, 1, mg.it.id);
  const f = S.view === "town" && S.townTab === "stash" && findItem(el.dataset.id);
  if (f?.where === "inv") return move(f.it.id, ch.stash, STASH_SIZE, "El alijo está lleno");
  if (f?.where === "stash") return move(f.it.id, ch.inv, INV_SIZE, "El inventario está lleno");
  // a potion in the bag goes straight onto the belt (the menu, to drop it etc., is on right-click)
  const pot = findItem(el.dataset.id);
  if (pot?.where === "inv" && pot.it.kind === "potion") { tip.hidden = true; return toBelt(pot.it.id); }
  // the worn undershirt: straight to choosing which pieces show (its menu is on right-click)
  if (pot?.where === "equip" && pot.it.setShirt) { tip.hidden = true; return shirtDisplay(); }
  openMenu(el, itemActions(el.dataset.id));
});
document.addEventListener("contextmenu", (e) => {
  const el = e.target.closest("[data-id]");
  if (!el || el.closest("#belt") || el.closest(".ground")) return;
  e.preventDefault();
  openMenu(el, itemActions(el.dataset.id));
});

function remove(id) {
  const f = findItem(id);
  if (!f) return null;
  if (f.where === "equip") { delete ch.equip[f.slot]; return f.it; }
  f.list.splice(f.i, 1);
  return f.it;
}
function move(id, to, cap, full) {
  if (to.length >= cap) return toast(full);
  const it = remove(id);
  to.push(it);
  save(); renderPanels(); renderHud(); if (S.view === "town") renderTown();
}
function toBelt(id) {
  if (ch.belt.length >= stats().beltSlots) return toast("El cinturón está lleno");
  move(id, ch.belt, 99, "");
}
function equip(id, slot) {
  const f = findItem(id);
  if (!f || !E.canEquip(ch, f.it)) return toast("No cumples los requisitos");
  const base = BASE[f.it.base];
  const set = slot.slice(-1);
  const freed = [];
  // whatever comes off must fit in the bag
  const off = [ch.equip[slot], base.twoHanded && ch.equip[`off${set}`], base.slot === "off" && ch.equip[`weapon${set}`] && BASE[ch.equip[`weapon${set}`].base].twoHanded && ch.equip[`weapon${set}`]].filter(Boolean);
  if (ch.inv.length - (f.list === ch.inv ? 1 : 0) + off.filter((x) => !x.setShirt).length > INV_SIZE) return toast("No cabe en el inventario lo que te quitarías: haz sitio primero");
  f.list.splice(f.i, 1);
  if (ch.equip[slot]) freed.push(ch.equip[slot]);
  ch.equip[slot] = f.it;
  // two-handed weapons need the off hand free, and vice versa
  if (base.twoHanded && ch.equip[`off${set}`]) { freed.push(ch.equip[`off${set}`]); delete ch.equip[`off${set}`]; }
  if (base.slot === "off" && ch.equip[`weapon${set}`] && BASE[ch.equip[`weapon${set}`].base].twoHanded) { freed.push(ch.equip[`weapon${set}`]); delete ch.equip[`weapon${set}`]; }
  for (const x of freed) if (x.setShirt) (ch.shirts ||= {})[x.setShirt] = x; else ch.inv.push(x);
  afterGearChange();
  // the other weapon set isn't shown on the doll: say where it went
  if (/^(weapon|off)\d$/.test(slot) && +set !== ch.swap) toast(`${E.itemName(f.it)} va a las armas ${set === "1" ? "I" : "II"}, en reserva. Cámbialas con Alt+S o el botón «Armas».`, "", 4000);
}
function unequip(slot) {
  const it = ch.equip[slot];
  if (it?.setShirt) { (ch.shirts ||= {})[it.setShirt] = it; delete ch.equip[slot]; return afterGearChange(); }
  if (ch.inv.length >= INV_SIZE) return toast("El inventario está lleno");
  ch.inv.push(ch.equip[slot]);
  delete ch.equip[slot];
  afterGearChange();
}
// A set's magic undershirt from the collection onto its own slot; the one you had on goes back
function wearShirt(sid) {
  const it = ch.shirts?.[sid];
  if (!it || !E.canEquip(ch, it)) return toast("No cumples los requisitos");
  const old = ch.equip.shirt;
  delete ch.shirts[sid];
  ch.equip.shirt = it;
  if (old) ch.shirts[old.setShirt] = old;
  afterGearChange();
  toast(`Te pones la ${E.itemName(it)}`, "r-set");
}
// The worn undershirt: which of its set's pieces show over what you really wear (all, unless unticked).
// it.hide: the names of the pieces not shown; in their place the figure shows what's on that slot.
// The undershirt's picker: per slot, the set's piece, what you really wear there, or nothing. Where
// both exist, a choice between them ("o"); where only one, show it or not. Looks only: stats don't change.
function shirtDisplay() {
  const it = ch.equip.shirt, set = it && SETS.find((s) => s.id === it.setShirt);
  if (!set) return;
  const color = RARITY[set.tier || "set"].color;
  const realOf = (sl) => (sl === "weapon" ? ch.equip[`weapon${ch.swap}`] : sl === "off" ? ch.equip[`off${ch.swap}`] : ch.equip[sl]);
  const opt = (sl, v, item, label) => `<button type="button" class="shopt" data-sl="${sl}" data-v="${v}" title="${esc(label)}">${item ? itemIco(item) : ""}<span style="${item ? `color:${E.itemColor(item)}` : ""}">${esc(label)}</span></button>`;
  const row = (sl) => {
    const piece = setPieceFor(set, sl), real = realOf(sl);
    if (!piece && !real) return "";
    const opts = [piece && opt(sl, "set", piece, piece.name), real && opt(sl, "real", real, E.itemName(real)), opt(sl, "none", null, "Nada")].filter(Boolean);
    return `<div class="shirtpick" data-row="${sl}"><span class="dim small shslot">${esc(SLOTS[sl])}</span><div class="shopts">${opts.join(`<i class="or">o</i>`)}</div></div>`;
  };
  const d = dialog(`<h3 style="color:${color}">${esc(E.itemName(it))}</h3>
    <p class="dim">Elige qué se ve en cada sitio: la pieza del conjunto, lo que llevas puesto o nada. Lo que da cada cosa no cambia: solo cómo te ves.</p>
    <div class="shirtfig">${figureSvg(ch)}</div>
    <div class="shirtpicks">${SHOW_SLOTS.map(row).join("")}</div>
    <div class="row"><button id="shirtAll" class="ghost">Todo el conjunto</button><button id="shirtReal" class="ghost">Lo que llevo</button><span style="flex:1"></span><button id="shirtOff">Quitártela</button><button id="shirtDone" class="primary">Listo</button></div>`, { cls: "shirtdlg" });
  const mark = () => d.querySelectorAll(".shopt").forEach((b) => b.classList.toggle("on", shirtChoice(it, set, b.dataset.sl) === b.dataset.v));
  const apply = () => {
    delete it.hide;
    // keep only what differs from the default
    for (const sl of Object.keys(it.show || {})) if (it.show[sl] === (setPieceFor(set, sl) ? "set" : "real")) delete it.show[sl];
    if (it.show && !Object.keys(it.show).length) delete it.show;
    save(); renderMe(); renderPanels();
    d.querySelector(".shirtfig").innerHTML = figureSvg(ch);
    mark();
  };
  const choose = (sl, v) => { it.show = { ...(it.show || {}), [sl]: v }; };
  // a two-handed weapon and the other hand can't both show: picking one clears the other
  const shownIn = (sl) => { const c = shirtChoice(it, set, sl); return c === "set" ? setPieceFor(set, sl) : c === "real" ? realOf(sl) : null; };
  const twoH = (x) => !!(x && BASE[x.base]?.twoHanded);
  const pick = (sl, v) => {
    choose(sl, v);
    if (sl === "weapon" && twoH(shownIn("weapon")) && shownIn("off")) choose("off", "none");
    if (sl === "off" && v !== "none" && twoH(shownIn("weapon"))) choose("weapon", "none");
  };
  // carry an older choice (pieces unticked by name) over before anything changes
  if (it.hide) { for (const sl of SHOW_SLOTS) { const c = shirtChoice(it, set, sl); if (c !== "set" && setPieceFor(set, sl)) choose(sl, c); } }
  d.querySelectorAll(".shopt").forEach((b) => (b.onclick = () => { pick(b.dataset.sl, b.dataset.v); apply(); }));
  d.querySelector("#shirtAll").onclick = () => { for (const sl of SHOW_SLOTS) if (setPieceFor(set, sl)) choose(sl, "set"); apply(); };
  d.querySelector("#shirtReal").onclick = () => { for (const sl of SHOW_SLOTS) choose(sl, "real"); apply(); };
  d.querySelector("#shirtOff").onclick = () => { closeDialog(); unequip("shirt"); };
  d.querySelector("#shirtDone").onclick = closeDialog;
  mark();
}
function afterGearChange() {
  renderMe();
  const st = stats();
  // extra potions fall out of a smaller belt into the bag
  while (ch.belt.length > st.beltSlots) ch.inv.push(ch.belt.pop());
  save(); renderPanels(); renderHud();
  // the town shows the stash (and, on a phone, the bag) itself: a gem socketed from there must vanish there too
  if (S.view === "town") renderTown();
  if (S.F && !S.F.checked && S.F.si != null) setupExercise(true);
}
function socket(gemId, hostId) {
  const host = findItem(hostId)?.it;
  if (!host || host.gems.length >= host.sockets) return;
  const gem = remove(gemId);
  host.gems.push(gem.kind === "runa" ? { runa: gem.runa } : { gem: gem.gem, grade: gem.grade });
  const rs = gem.kind === "runa" && E.runaSetOf(host);
  toast(rs ? `¡${RUNA_SETS.find((x) => x.id === rs.id).name}! El conjunto rúnico despierta en ${E.itemName(host)}` : `Engastaste ${E.itemName(gem)}`, rs ? "levelup" : "", rs ? 4000 : undefined);
  afterGearChange();
}
// The stash in order: gear (best rarity first, then by slot, higher level first), gems
// (by type, best grade first), potions.
const RARITY_RANK = ["tunjo", "mitico", "legendario", "ancestral", "unique", "set", "runeword", "crafted", "rare", "magic", "normal", "low"];
const SLOT_RANK = ["weapon", "off", "head", "body", "hands", "feet", "belt", "neck", "ring"];
const GEM_RANK = Object.keys(GEMS);
// [numbers..., name]: compared number by number, then by name (sortCompare)
function sortKey(it) {
  if (it.kind === "gem") return [2, GEM_RANK.indexOf(it.gem), -it.grade, 0, 0, ""];
  if (it.kind === "runa") return [2, 50, -RUNAS.findIndex((r) => r.id === it.runa), 0, 0, ""];
  if (it.kind === "potion") return [3, ["life", "mana", "rejuv"].indexOf(it.potion), -(it.tier || 0), 0, 0, ""];
  if (it.kind) return [4, 0, 0, 0, 0, E.itemName(it)];
  // a set's pieces together, in the set's own order, after the rest of their rarity's sets... by set
  // (identified only: an unidentified piece doesn't say which set it is, so it goes with the others by slot)
  const si = it.set && !it.unid ? SETS.findIndex((x) => x.id === it.set) : -1;
  if (si >= 0) {
    const pi = SETS[si].pieces.findIndex((pc) => pc.name === it.name);
    return [0, RARITY_RANK.indexOf(it.rarity), si, pi < 0 ? 99 : pi, -(it.ilvl || 0), E.itemName(it)];
  }
  return [0, RARITY_RANK.indexOf(it.rarity), SETS.length + SLOT_RANK.indexOf(BASE[it.base]?.slot), 0, -(it.ilvl || 0), E.itemName(it)];
}
function sortCompare(a, b) {
  const x = sortKey(a), y = sortKey(b), n = x.length - 1;
  for (let i = 0; i < n; i++) if (x[i] !== y[i]) return x[i] - y[i];
  return x[n].localeCompare(y[n]);
}
// The stash holds STASH_SIZE, but shows 8 rows and grows a row at a time, always one row free.
// Rows run the page's width, as wide as the village picture: 10 slots on a phone, 16 on a computer,
// each slot about as big as the bag's.
let stashColsShown = 0;
const stashCols = () => Math.max(10, Math.min(24, Math.floor((screen.clientWidth - 40 + 3) / 57)));
const stashShown = (cols = stashCols()) => Math.min(STASH_SIZE, Math.max(cols * 8, (Math.ceil(ch.stash.length / cols) + 1) * cols));
new ResizeObserver(() => { if (S.view === "town" && S.townTab === "stash" && stashCols() !== stashColsShown) renderTown(); }).observe(screen);
function sortStash() { sortList(ch.stash); }
function sortBag() { sortList(ch.inv); toast("Bolsa ordenada"); }
function sortList(list) {
  list.sort(sortCompare);
  save(); if (S.view === "town") renderTown(); renderPanels();
}
function sell(id) {
  if (findItem(id)?.it.kind === "relic") return toast("El transformador no se vende");
  const it = remove(id);
  ch.gold += E.itemValue(it);
  // the last few sales can be bought back at the same price, in case of a slip
  (S.sold ||= []).unshift(it); S.sold.length = Math.min(S.sold.length, 8);
  toast(`Vendido por ${E.itemValue(it)} de oro`);
  save(); renderPanels(); renderHud(); renderTown();
}

// ---------- the item list: bag, stash and what you wear as a table, everything in plain sight ----------
const LIST_TABS = [["inv", "Bolsa"], ["stash", "Alijo"], ["equip", "Puesto"]];
const SLOT_NAMES = { weapon1: "Arma I", off1: "Escudo I", weapon2: "Arma II", off2: "Escudo II", head: "Cabeza", neck: "Cuello", body: "Torso", hands: "Manos", ring1: "Anillo 1", ring2: "Anillo 2", belt: "Cintura", feet: "Pies" };
function listRows(tab) {
  if (tab === "equip") return Object.entries(ch.equip).filter(([, it]) => it).map(([slot, it]) => ({ it, slot }));
  return (tab === "inv" ? ch.inv : ch.stash).map((it) => ({ it }));
}
// What it is, in a few words: rarity and kind of item
function listKind(it) {
  if (it.kind === "gem") return "Gema";
  if (it.kind === "runa") return RUNA_TIERS[RUNA[it.runa].tier].name;
  if (it.kind === "relic") return "Reliquia";
  if (it.kind === "potion") return "Poción";
  const base = BASE[it.base];
  const rar = it.rarity === "crafted" && it.craft ? `Artesanal ${CRAFT[it.craft].name}` : RARITY[it.rarity].name;
  return `${rar} · ${SLOTS[base.slot]}${base.twoHanded ? " a dos manos" : base.slot === "weapon" ? " a una mano" : ""}${["rare", "unique", "set", "crafted", "runeword", "ancestral", "legendario", "mitico", "tunjo"].includes(it.rarity) && base.name !== SLOTS[base.slot] ? ` · ${base.name}` : ""}`;
}
// A weapon's own elemental damage (props and gems), and what one hit would do with it in your hand:
// your other gear, strength or dexterity and every elemental bonus included.
function weaponTotals(it) {
  const P = E.itemProps(it), els = ["fire", "cold", "light", "poison"].filter((k) => P[k]);
  const extra = els.reduce((a, k) => a + P[k], 0);
  const elems = els.map((k) => `+${P[k]} ${ELEMENTS[k].res}`).join(", ");
  const st = E.charStats({ ...ch, equip: { ...ch.equip, [`weapon${ch.swap}`]: it } });
  const allEl = Object.values(st.elem).reduce((a, v) => a + v, 0);
  const ownPct = (it.quality || 0) + (P.dmgPct || 0);
  const statName = st.kind === "ranged" ? "destreza" : "fuerza", why = [];
  if (st.otherPct) why.push(`${st.otherPct > 0 ? "+" : ""}${st.otherPct}% de tu otro equipo`);
  if (st.otherFlat[0] || st.otherFlat[1]) why.push(`+${st.otherFlat[0]}–${st.otherFlat[1]} de tu otro equipo`);
  if (st.statPct) why.push(`+${st.statPct}% por tu ${statName}`);
  if (allEl - extra) why.push(`+${allEl - extra} elemental de tu otro equipo`);
  if (extra) why.push(`+${extra} elemental del arma`);
  return { extra, elems, ownPct, why, you: [st.dmg[0] + allEl, st.dmg[1] + allEl] };
}
// A piece of armour's own defence rolls, and your whole defence with it on (it replaces what's in its slot).
function armorTotals(it) {
  const slot = BASE[it.base].slot, key = slot === "off" ? `off${ch.swap}` : slot === "weapon" ? `weapon${ch.swap}` : slot;
  const P = E.itemProps(it), st = E.charStats({ ...ch, equip: { ...ch.equip, [key]: it } });
  const dr = Math.round(Math.min(0.75, st.armor / (st.armor + 25 + 12 * ch.level)) * 100);
  return { ownPct: (it.quality || 0) + (P.armorPct || 0), flat: P.armor || 0, you: st.armor, now: stats().armor, dr, block: st.block };
}
// Damage or defence, the number you compare first
function listMain(it) {
  if (it.kind) return "";
  const base = BASE[it.base];
  if (base.dmg) {
    const d = E.itemDamage(it), w = weaponTotals(it);
    return `Daño <b>${d[0]}–${d[1]}</b>${w.extra ? ` <span class="dim">(${d[0] + w.extra}–${d[1] + w.extra} con ${w.elems})</span>` : ""}<div class="dim">${base.kind === "ranged" ? "a distancia" : "cuerpo a cuerpo"} · contigo ${w.you[0]}–${w.you[1]} por golpe</div>`;
  }
  if (it.def) { const a = armorTotals(it); return `Defensa <b>${E.itemDefense(it)}</b><div class="dim">contigo ${a.you}${a.you !== a.now ? ` (ahora ${a.now})` : ""} · frena el ${a.dr}%${base.block ? ` · bloqueo ${a.block}%` : ""}</div>`; }
  return "";
}
function listProps(it) {
  if (it.kind === "gem") {
    const eff = (where) => E.gemEffect(it.gem, it.grade, where);
    return [["weapon", "Arma"], ["head", "Armadura"], ["off", "Escudo"]].map(([w, l]) => { const e = eff(w); return `<div><span class="dim">${l}:</span> ${esc(E.propText(e.prop, e.value))}</div>`; }).join("");
  }
  if (it.kind === "potion") {
    const P = POTIONS[it.potion];
    return it.potion === "life" ? `Recupera ${P.heal[it.tier]} de vida` : it.potion === "mana" ? `Recupera ${P.mana[it.tier]} de maná` : "Recupera el 40% de vida y maná";
  }
  if (it.kind === "runa") return [["w", "Arma"], ["a", "Armadura"], ["o", "Escudo"]].map(([k, l]) => `<div><span class="dim">${l}:</span> ${esc(E.propText(...RUNA[it.runa][k]))}</div>`).join("");
  if (it.kind === "relic") return `En el Montón: cada ${MOUND_STEP} gemas perfectas, un mítico, una mascota o una montura`;
  if (it.unid) return `<span class="unid">Sin identificar</span>`;
  let out = Object.entries(it.props).sort((a, b) => E.PROP_ORDER(a[0]) - E.PROP_ORDER(b[0])).map(([k, v]) => `<div>${esc(E.propText(k, v))}</div>`).join("");
  if (it.set) { const st = SETS.find((x) => x.id === it.set); out += `<div style="color:${RARITY[st.tier || "set"].color}">${esc(st.name)}</div>`; }
  return out || `<span class="dim">—</span>`;
}
function listReq(it) {
  if (it.kind) return "";
  const req = BASE[it.base].req || {}, st = stats(), lreq = E.itemLevelReq(it), out = [];
  if (lreq > 1) out.push(`<span class="${ch.level < lreq ? "bad" : ""}">Nivel ${lreq}</span>`);
  if (req.str) out.push(`<span class="${st.str < req.str ? "bad" : ""}">Fue ${req.str}</span>`);
  if (req.dex) out.push(`<span class="${st.dex < req.dex ? "bad" : ""}">Des ${req.dex}</span>`);
  return out.join("<br>") || `<span class="dim">—</span>`;
}
function listSockets(it) {
  if (!it.sockets) return `<span class="dim">—</span>`;
  const used = it.gems.map((g) => `<span style="color:${sockColor(g)}">${g.runa ? "ᚱ" : "◆"}</span>`).join(" ");
  return `${it.gems.length}/${it.sockets}${used ? `<div>${used}</div>` : ""}`;
}
function listActions(it, tab, slot) {
  const town = S.view === "town", A = [];
  if (tab === "equip") A.push(`<button data-la="unequip" data-slot="${slot}">Quitar</button>`);
  if (tab === "inv" && !it.kind && !it.unid) {
    const sl = BASE[it.base].slot;
    const target = sl === "ring" ? (!ch.equip.ring1 ? "ring1" : !ch.equip.ring2 ? "ring2" : "ring1") : sl === "weapon" || sl === "off" ? `${sl}${ch.swap}` : sl;
    A.push(`<button data-la="equip" data-slot="${target}" ${E.canEquip(ch, it) ? "" : "disabled title=\"No cumples los requisitos\""}>Equipar</button>`);
  }
  if (it.unid && tab !== "equip") A.push(`<button data-la="identify">Identificar</button>`);
  if (town && tab === "inv") A.push(`<button data-la="tostash">Al alijo</button>`);
  if (town && tab === "stash") A.push(`<button data-la="toinv">A la bolsa</button>`);
  if (town && tab !== "equip" && it.kind !== "relic") A.push(`<button data-la="sell" class="sellbtn">Vender <b>${E.itemValue(it)}</b></button>`);
  // only from the bag; it's for good, so the first click asks
  if (tab === "inv") A.push(`<button data-la="toss" class="tossbtn">Tirar</button>`);
  return A.join("");
}
const LIST_SORTS = {
  name: (a, b) => sortCompare(a.it, b.it),
  level: (a, b) => (b.it.kind ? -1 : E.itemLevelReq(b.it)) - (a.it.kind ? -1 : E.itemLevelReq(a.it)),
  value: (a, b) => E.itemValue(b.it) - E.itemValue(a.it),
};
function openItemList(tab = S.listTab || "inv") {
  S.listTab = tab;
  const box = dialog(`<div id="itemList"></div>`, { cls: "itemlist" });
  renderItemList(box);
}
function renderItemList(box = $(".dialog.itemlist")) {
  if (!box) return;
  const tab = S.listTab, sortBy = S.listSort || "", town = S.view === "town";
  const rows = listRows(tab);
  if (sortBy) rows.sort(LIST_SORTS[sortBy]);
  const count = tab === "inv" ? `${ch.inv.length}/${INV_SIZE}` : tab === "stash" ? `${ch.stash.length}/${STASH_SIZE}` : `armas ${ch.swap === 1 ? "I" : "II"} en uso`;
  const th = (key, label) => key ? `<th><button class="lsort${sortBy === key ? " on" : ""}" data-lsort="${key}">${label}</button></th>` : `<th>${label}</th>`;
  box.querySelector("#itemList").innerHTML = `
    <div class="ltop">
      <h3>Tus objetos</h3>
      <div class="ltabs" role="tablist">${LIST_TABS.map(([k, l]) => `<button role="tab" aria-selected="${k === tab}" class="${k === tab ? "on" : ""}" data-ltab="${k}">${l}</button>`).join("")}</div>
      <span class="dim">${count} · ${ch.gold} de oro</span>
      <button class="x" id="listClose" aria-label="Cerrar">×</button>
    </div>
    ${!town && tab !== "equip" ? `<p class="dim small">Vender y usar el alijo: en la aldea.</p>` : ""}
    ${rows.length ? `<div class="ltable-wrap"><table class="ltable">
      <thead><tr>${th("name", "Objeto")}${th("level", "Requiere")}<th>Daño / defensa</th><th>Propiedades</th><th>Engastes</th>${th("value", "Valor")}<th></th></tr></thead>
      <tbody>${rows.map(({ it, slot }) => `<tr data-lid="${it.id}">
        <td class="lname"><div style="color:${E.itemColor(it)}">${itemIco(it)} ${esc(E.itemName(it))}</div><div class="dim">${slot ? `<b>${SLOT_NAMES[slot] || slot}</b> · ` : ""}${esc(listKind(it))}</div></td>
        <td class="lreq">${listReq(it)}</td>
        <td class="lmain">${listMain(it)}</td>
        <td class="lprops">${listProps(it)}</td>
        <td class="lsock" data-l="Engastes">${it.kind ? "" : listSockets(it)}</td>
        <td class="lval" data-l="Valor">${E.itemValue(it)}</td>
        <td class="lact">${listActions(it, tab, slot)}</td></tr>`).join("")}</tbody></table></div>`
      : `<p class="dim">${tab === "inv" ? "La bolsa está vacía." : tab === "stash" ? "El alijo está vacío." : "No llevas nada puesto."}</p>`}`;
  box.querySelector("#listClose").onclick = closeDialog;
  box.querySelectorAll("[data-ltab]").forEach((b) => (b.onclick = () => { S.listTab = b.dataset.ltab; renderItemList(box); }));
  box.querySelectorAll("[data-lsort]").forEach((b) => (b.onclick = () => { S.listSort = S.listSort === b.dataset.lsort ? "" : b.dataset.lsort; renderItemList(box); }));
  box.querySelectorAll("[data-la]").forEach((b) => (b.onclick = () => {
    const id = b.closest("tr").dataset.lid, a = b.dataset.la;
    if (a === "toss" && !b.classList.contains("sure")) {
      box.querySelectorAll(".tossbtn.sure").forEach((x) => { x.classList.remove("sure"); x.textContent = "Tirar"; });
      b.classList.add("sure"); b.textContent = "¿Seguro? Tirar";
      return;
    }
    if (a === "toss") { const it = findItem(id)?.it; if (!it) return; remove(id); save(); renderPanels(); toast(`Tiraste ${E.itemName(it)}`); }
    else if (a === "sell") sell(id);
    else if (a === "equip") equip(id, b.dataset.slot);
    else if (a === "unequip") unequip(b.dataset.slot);
    else if (a === "tostash") move(id, ch.stash, STASH_SIZE, "El alijo está lleno");
    else if (a === "toinv") move(id, ch.inv, INV_SIZE, "El inventario está lleno");
    else if (a === "identify") { closeDialog(); return identify(id); }
    renderItemList(box);
  }));
}

// ---------- panels: character & inventory ----------
// On wide screens the page makes room for open drawers instead of hiding under them.
// Side panel: the Netflix subtitles and Whisper's raw transcription for the line you just checked
// (or the one you died on). Shares the right side with the inventory. Empty while you're still
// answering, so it can't give the line away.
function srcPhrase() {
  if (S.view === "dead" && S.death && !S.death.card) return S.death;
  if (S.F?.checked && S.F.ex && !S.F.review) return currentPhrase();
  return null;
}
async function refreshSources() {
  const panel = $("#srcPanel");
  if (panel.hidden) return;
  const P = srcPhrase(), body = $("#srcBody");
  if (!P) { body.innerHTML = `<p class="dim">Aparece cuando compruebes la frase, para no revelártela antes.</p>`; return; }
  body.innerHTML = `<p class="dim">Cargando…</p>`;
  const html = await sourcesHtml(S.ep, { start: P.start, end: P.end, text: P.text });
  if (srcPhrase()?.start === P.start) body.innerHTML = html;
}
function toggleSources() {
  const panel = $("#srcPanel");
  panel.hidden = !panel.hidden;
  if (!panel.hidden) $("#invPanel").hidden = true;
  syncDrawers(); refreshSources();
}
$("#srcClose").onclick = toggleSources;
function syncDrawers() {
  document.body.classList.toggle("char-open", !$("#charPanel").hidden);
  document.body.classList.toggle("inv-open", !$("#invPanel").hidden || !$("#srcPanel").hidden);
}
function renderPanels() {
  syncDrawers();
  if (!ch) return;
  if (!$("#charPanel").hidden) renderChar();
  if (!$("#invPanel").hidden) renderInv();
}
function togglePanel(sel) {
  const p = $(sel);
  p.hidden = !p.hidden;
  // on a phone each panel takes the whole width: one at a time
  if (!p.hidden && narrow()) for (const o of ["#charPanel", "#invPanel", "#srcPanel"]) if (o !== sel) $(o).hidden = true;
  renderPanels();
}
$("#charBtn").onclick = () => togglePanel("#charPanel");
$("#invBtn").onclick = () => { $("#srcPanel").hidden = true; togglePanel("#invPanel"); };

function companionsPanel() {
  const block = (type) => {
    const C = COMPANION[type], own = ch[C.own] || [];
    const how = type === "pet" ? "Domina un episodio entero (20 minutos o más): todas sus frases al 100%, con huecos y al dictado, en Normal o Difícil."
      : "Domina un episodio entero así en Difícil.";
    if (!own.length) return `<p class="dim small">${type === "pet" ? "Mascota" : "Montura"}: ninguna aún. ${how}</p>`;
    return `<div class="comps">${Object.keys(C.list).map((id) => {
      const has = own.includes(id), on = ch[C.on] === id;
      return `<button class="compbtn${on ? " on" : ""}" ${has ? `data-comp="${type}:${id}"` : "disabled"} title="${has ? esc(`${C.list[id].name}: ${companionLine(type, id)}${on ? " Va contigo: clic para dejarlo en la aldea." : " Clic para llevarlo."}`) : "Aún no lo tienes"}">
        ${has ? `<img class="${type}" src="${compImg(type, id)}" alt="">` : `<span class="q">?</span>`}<span>${has ? esc(C.list[id].name) : "—"}</span></button>`;
    }).join("")}</div>${ch[C.on] && own.includes(ch[C.on]) ? `<p class="dim small">${esc(C.list[ch[C.on]].name)}: ${esc(companionLine(type, ch[C.on]))}</p>` : ""}`;
  };
  return `<h3>Compañeros</h3>${block("pet")}${block("mount")}`;
}
function renderChar() {
  const st = stats(), c = CLASSES[ch.cls];
  const attr = (k, label, help, now) => `<div class="attr"><div class="aname">${label}<small>${esc(help)}</small><small class="anow">${esc(now)}</small></div><b>${st[k]}</b>${ch.points ? `<button data-attr="${k}" title="Asignar un punto a ${label}">+</button>` : ""}</div>`;
  const n1 = (v) => v.toLocaleString("es", { maximumFractionDigits: 1 });
  const row = (label, v, cls = "") => `<div class="srow ${cls}"><span>${label}</span><b>${v}</b></div>`;
  const C = E.costs(ch, st);
  $("#charPanel").innerHTML = `
    <div class="ptitle"><div>${esc(ch.name)}</div><span>${c.name} · nivel ${ch.level}</span><button class="x" data-close="#charPanel" aria-label="Cerrar">×</button></div>
    <div class="charport" id="charPort"></div>
    <button id="lookBtn" class="lookbtn">${figureSvg(ch, { cls: "tiny" })}Cambiar aspecto</button>
    <button id="classBtn" class="ghost">Cambiar de clase o empezar de cero</button>${CFG.online ? `<button id="logoutBtn" class="ghost logout">Cerrar sesión</button>` : ""}
    ${ch.points ? `<div class="points">Tienes ${ch.points} ${ch.points === 1 ? "punto" : "puntos"} por asignar</div>` : ""}
    <div class="attrs">
      ${attr("str", "Fuerza", "Cada punto: +1% de daño con armas cuerpo a cuerpo (dictado). Algunas armas y armaduras la exigen.",
        st.kind === "ranged" ? `Ahora: no cuenta para tu arma a distancia` : `Ahora: +${st.str}% de daño`)}
      ${attr("dex", "Destreza", "Cada punto: +1% de daño a distancia (huecos), +0,08% de crítico, +0,03% de esquiva y +¼ de defensa. Algunas armas la exigen.",
        `Ahora: ${st.kind === "ranged" ? `+${st.dex}% de daño, ` : ""}+${n1(st.dex * 0.08)}% de crítico, +${n1(st.dex * 0.03)}% de esquiva, +${Math.round(st.dex / 4)} de defensa`)}
      ${attr("vit", "Vitalidad", "Cada punto: +2 de vida.", `Ahora: +${st.vit * 2} de vida`)}
      ${attr("ene", "Energía", `Cada punto: +1,6 de maná. Cada 15 puntos: +1 de maná recuperado tras cada ataque.${E.spellsFor(ch).length ? " Para el brujo: +1% de daño de los hechizos." : ""}`,
        `Ahora: +${Math.round(st.ene * 1.6)} de maná, +${Math.floor(st.ene / 15)} por ataque`)}
    </div>
    <h3>Ataque</h3>
    ${(() => {
      const els = Object.entries(st.elem).filter(([, v]) => v), extra = els.reduce((a, [, v]) => a + v, 0);
      if (!extra) return row("Daño por golpe", `${st.dmg[0]}–${st.dmg[1]}`);
      return row("Daño por golpe", `${st.dmg[0] + extra}–${st.dmg[1] + extra}`)
        + row("&nbsp;&nbsp;del arma", `${st.dmg[0]}–${st.dmg[1]}`, "sub")
        + els.map(([k, v]) => row(`&nbsp;&nbsp;+ ${ELEMENTS[k].name.toLowerCase()}`, `+${v}`, "sub")).join("")
        + `<p class="dim small">Todo se suma en cada golpe. Una frase a medias hace la parte proporcional, y un monstruo que resiste un elemento recibe menos de esa parte.</p>`;
    })()}
    ${row("Tipo de ataque", st.kind === "ranged" ? "Rellenar huecos" : "Dictado")}
    ${E.spellsFor(ch).length ? `<h3>Hechizos</h3>
      <p class="dim small">${E.canCast(ch, st) ? "Prepara uno (Q, W, E, R, o Alt con la letra mientras escribes) y sale con cada ataque mientras te alcance el maná. Tu acierto en la frase decide su fuerza; la energía, no la destreza, sube su daño." : "<b>Necesitas una varita, un cetro o un bastón</b> para lanzarlos."}${st.spellDmg ? ` Daño de hechizos +${st.spellDmg}%.` : ""}</p>
      ${E.spellsFor(ch).map((sp) => `<div class="srow spellrow${ch.level < sp.lvl ? " dim" : ""}"><span>${icon(sp.icon, sp.color)} <b>${esc(sp.name)}</b> <kbd>${sp.key.toUpperCase()}</kbd><small>${esc(sp.desc)}</small></span><b>${ch.level < sp.lvl ? `nivel ${sp.lvl}` : `${E.spellCost(ch, sp)} maná`}</b></div>`).join("")}` : ""}
    ${row("Crítico", `${st.crit.toFixed(1)}%`)}
    ${st.dmgDictation ? row("Daño en dictado", `+${st.dmgDictation}%`) : ""}
    ${st.dmgCloze ? row("Daño en huecos", `+${st.dmgCloze}%`) : ""}
    ${st.leech ? row("Robo de vida", `${st.leech}%`) : ""}
    ${E.powerOf(ch) ? `<h3>Habilidad de ${esc(CLASSES[ch.cls].name.toLowerCase())}</h3>
      <div class="srow spellrow"><span>${icon(E.powerOf(ch).icon, E.powerOf(ch).color)} <b>${esc(E.powerOf(ch).name)}</b> <kbd>F</kbd><small>${esc(E.powerOf(ch).desc)} En un combate: F, o Alt+F mientras escribes.</small></span><b>${E.powerCost(ch, st)} maná</b></div>` : ""}
    ${companionsPanel()}
    <h3>Defensa</h3>
    ${row("Vida", `${Math.round(ch.life)}/${st.maxLife}`)}
    ${row("Maná", `${Math.round(ch.mana)}/${st.maxMana}`)}
    ${row("Defensa", st.armor)}
    ${st.block ? row("Bloqueo", `${st.block}%`) : ""}
    ${row("Esquiva", `${st.dodge.toFixed(1)}%`)}
    ${row("Res. fuego", `${st.resFire}%`, "fire")}${row("Res. frío", `${st.resCold}%`, "cold")}${row("Res. rayo", `${st.resLight}%`, "light")}${row("Res. veneno", `${st.resPoison}%`, "poison")}
    <h3>Escucha</h3>
    ${row("Repetir", `${C.replay} de maná`)}
    ${row("Escuchar despacio", C.slow ? `${C.slow} de maná` : "gratis")}
    ${row("Pista", `${C.hint} de maná`)}
    ${row("Escuchas gratis por frase", 1 + st.freeReplay)}
    ${st.typoTol ? row("Tolerancia a errores", `+${st.typoTol} letra`) : ""}
    ${st.nearExact ? row("Casi correcto", "cuenta como correcto") : ""}
    <h3>Botín</h3>
    ${row("Objetos mágicos", `+${st.mf}%`)}${row("Oro", `+${st.gf}%`)}${st.xp ? row("Experiencia", `+${st.xp}%`) : ""}
    <h3>Historial</h3>
    ${row("Frases", ch.stats.lines)}${row("Perfectas", ch.stats.perfect)}${row("Enemigos abatidos", ch.stats.kills)}${row("Mejor racha", ch.stats.bestCombo)}${row("Muertes", ch.stats.deaths)}
    ${dropTally()}
    <div class="row"><button id="debugExport" class="ghost" title="Descarga un archivo con tu personaje, tus estadísticas, las probabilidades de botín y los últimos objetos y errores, para revisar qué pasa">Exportar datos de depuración</button></div>`;
  // with a pet or a horse along, the character stands here with them
  const port = $("#charPort"), fig = companionsHtml() && fightFigure(ch, { centered: true });
  port.hidden = !fig;
  if (fig) { fig.el.classList.add("dollfig"); port.append(withCompanions(fig, "doll")); }
}
function dropTally() {
  const d = ch.stats.drops || {}, n = Object.values(d).reduce((a, b) => a + b, 0);
  if (!n) return `<p class="dim small">Desde ahora se cuenta el equipo que te cae, por rareza.</p>`;
  // every rarity, even the ones that haven't dropped yet (a mítico you've never seen still shows, at 0),
  // and the chance of each per piece of gear from an ordinary monster right now (simulated, with your magic find)
  const order = ["low", "normal", "magic", "rare", "set", "unique", "ancestral", "legendario", "mitico"];
  const st = stats(), D = E.diffOf(ch), odds = { ...lootOdds(st, D, 6000).normal, ...E.topOdds(Math.max(0, st.mf + D.mf), D.loot, D) };
  const per = (r) => { const p = odds[r] || 0; return p >= 1 ? `${p.toFixed(1)}%` : p > 0 ? `1 de cada ${Math.round(100 / p).toLocaleString("es")}` : "muy raro"; };
  return `<h3>Equipo que te ha caído <span class="dim">(${n})</span></h3><p class="dim small">Cuántas piezas de cada rareza te han caído, y la probabilidad de cada una ahora por pieza de un monstruo normal.</p>` + order.map((r) =>
    `<div class="srow${d[r] ? "" : " none"}" title="Ahora, por pieza de un monstruo normal: ${per(r)}"><span style="color:${RARITY[r].color}">${RARITY[r].name}</span><b>${d[r] || 0} <span class="dim">· ${(((d[r] || 0) / n) * 100).toFixed(1)}% · ahora ${per(r)}</span></b></div>`).join("");
}
// ---------- debug export ----------
// One JSON file to look at what's going on: the character and its computed stats, what the loot odds
// are for you right now (simulated), the last drops, and the last errors in this page.
const recentErrors = [];
addEventListener("error", (e) => { recentErrors.push({ t: Date.now(), msg: String(e.message), at: `${e.filename}:${e.lineno}:${e.colno}`, stack: e.error?.stack?.slice(0, 1500) }); if (recentErrors.length > 30) recentErrors.shift(); });
addEventListener("unhandledrejection", (e) => { recentErrors.push({ t: Date.now(), msg: String(e.reason?.message || e.reason), stack: e.reason?.stack?.slice(0, 1500) }); if (recentErrors.length > 30) recentErrors.shift(); });
function lootOdds(st, D, N0 = 20000) {
  // per piece of gear from an ordinary monster / a champion / a boss, with your magic find and difficulty
  const out = {};
  for (const [tier, bonus] of [["normal", 1], ["champion", 1.8], ["boss", 5]]) {
    const c = {}, N = N0, mf = Math.max(0, st.mf + D.mf);
    for (let i = 0; i < N; i++) { const r = E.rollRarity(mf, bonus * D.loot, D, 1); c[r] = (c[r] || 0) + 1; }
    out[tier] = Object.fromEntries(Object.entries(c).sort((a, b) => b[1] - a[1]).map(([k, v]) => [k, +((v / N) * 100).toFixed(2)]));
  }
  return out;
}
function exportDebug() {
  const st = stats(), D = E.diffOf(ch);
  const brief = (it) => it && { name: E.itemName(it), rarity: it.rarity, base: it.base, ilvl: it.ilvl, unid: !!it.unid, sockets: it.sockets, gems: (it.gems || []).map((g) => `${g.gem}:${g.grade}`), set: it.set, props: it.props };
  const data = {
    exported: new Date().toISOString(),
    page: { url: location.pathname + location.search, ua: navigator.userAgent, viewport: [innerWidth, innerHeight], dpr: devicePixelRatio, reducedMotion: matchMedia("(prefers-reduced-motion: reduce)").matches },
    episode: S.T ? { id: S.ep, segments: S.T.segments.length, course: !!S.T.zones } : null,
    view: S.view, zone: S.zone?.id, fight: S.F ? { monsters: S.F.monsters.map((m) => ({ name: m.name, tier: m.tier, lvl: m.lvl, hp: m.hp, maxHp: m.maxHp, dmg: m.dmg, el: m.el, res: m.res, mods: m.mods })), combo: S.F.combo } : null,
    character: { name: ch.name, cls: ch.cls, level: ch.level, xp: ch.xp, gold: ch.gold, difficulty: D.name, streak: ch.streak, base: ch.base, points: ch.points, stats: st },
    equipped: Object.fromEntries(Object.entries(ch.equip).filter(([, v]) => v).map(([k, v]) => [k, brief(v)])),
    inventory: ch.inv.map(brief), stashCount: ch.stash.length, belt: ch.belt.map((p) => p.potion),
    drops: { counts: ch.stats.drops || {}, last: ch.dropLog || [] },
    lootOdds: lootOdds(st, D),
    history: ch.stats, zones: ch.zones, zoneRewards: ch.zoneRewards,
    errors: recentErrors,
  };
  const blob = new Blob([JSON.stringify(data, null, 1)], { type: "application/json" });
  const a = document.createElement("a"), d = new Date(), pad = (n) => String(n).padStart(2, "0");
  a.href = URL.createObjectURL(blob);
  a.download = `leyendas-debug-${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-${pad(d.getHours())}${pad(d.getMinutes())}.json`;
  document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 2000);
  toast("Datos de depuración descargados");
}
$("#charPanel").addEventListener("click", (e) => {
  if (e.target.closest("#lookBtn")) return openLookDialog();
  if (e.target.closest("#classBtn")) return openClassDialog();
  if (e.target.closest("#logoutBtn")) return logout();
  if (e.target.closest("#debugExport")) return exportDebug();
  const cb = e.target.closest("[data-comp]");
  if (cb) {
    const [type, id] = cb.dataset.comp.split(":"), on = COMPANION[type].on;
    ch[on] = ch[on] === id ? null : id;
    save(); renderPanels(); renderHud(); renderMe();
    return toast(ch[on] ? `${COMPANION[type].list[id].name} va contigo` : `${COMPANION[type].list[id].name} se queda en la aldea`);
  }
  const b = e.target.closest("[data-attr]");
  if (b && ch.points > 0) {
    ch.base[b.dataset.attr]++; ch.points--;
    save(); renderPanels(); renderHud();
  }
  const x = e.target.closest("[data-close]");
  if (x) { $(x.dataset.close).hidden = true; syncDrawers(); }
});
$("#invPanel").addEventListener("click", (e) => {
  const x = e.target.closest("[data-close]");
  if (x) { $(x.dataset.close).hidden = true; syncDrawers(); }
});

function slotCell(slot, label, cls = "") {
  const it = ch.equip[slot];
  return `<div class="doll-slot ${cls}" title="${label}">${it ? `<button class="item r-${it.rarity}" data-id="${it.id}">${itemIco(it)}${it.sockets ? `<span class="sock">${it.gems.length}/${it.sockets}</span>` : ""}</button>` : `<span class="empty">${label}</span>`}</div>`;
}
// you already have this set's undershirt (on the shelf or on you): a little shirt in the item's corner
// (not while the item is unidentified)
const hasShirt = (sid) => !!(sid && (ch.shirts?.[sid] || ch.equip.shirt?.setShirt === sid));
const shirtMark = (it) => (it.set && !it.unid && hasShirt(it.set) ? `<span class="hasshirt" title="Ya tienes la camiseta de este conjunto">${icon("leather-vest", "#8fd18a")}</span>` : "");
function grid(list, size) {
  let out = "";
  // never hide anything: a bag that somehow holds more than it should shows the extra too
  for (let i = 0; i < Math.max(size, list.length); i++) {
    const it = list[i];
    out += it ? `<button class="cell item r-${it.rarity}" data-id="${it.id}">${itemIco(it)}${shirtMark(it)}${it.sockets ? `<span class="sock">${it.gems.length}/${it.sockets}</span>` : ""}${!it.kind && !E.canEquip(ch, it) ? `<span class="noreq"></span>` : ""}</button>` : `<span class="cell"></span>`;
  }
  return out;
}
// The figure on the paper doll moves between stances (stanceLoop). It's kept across re-renders while
// what you wear doesn't change, so it doesn't jump back to the start every time the bag changes.
let doll = { sig: null, fig: null, stop: () => {}, svg: "" };
function dollFigure(box) {
  const svg = figureSvg(ch), sig = svg + `|${ch.pet}|${ch.mount}`;
  if (sig !== doll.sig) {
    doll.stop();
    const fig = fightFigure(ch, { centered: true });
    doll = { sig, fig, stop: fig ? stanceLoop(fig, ch) : () => {}, svg };
    if (fig) fig.el.classList.add("dollfig");
  }
  if (doll.fig) box.prepend(withCompanions(doll.fig, "doll"));
  else box.insertAdjacentHTML("afterbegin", doll.svg);
}
// One place per set for its magic undershirt (made at the alembic from the whole set); the one you wear shows here too
// you, as you'd look with this set's undershirt on, every piece shown (the shelf: in colour if you have it, a shadow if not)
// the shelf shows you in the set alone: no other gear, no horse
const dressedIn = (set) => ({ ...ch, mount: null, equip: { shirt: { base: "camiseta", rarity: set.tier || "set", setShirt: set.id } } });
// the shelf in tiers: plain sets, then ancestral, legendary and mythic, each by level (as the shirts hang)
const TIER_RANK = { ancestral: 1, legendario: 2, mitico: 3, tunjo: 4 };
const SETS_BY_TIER = SETS.map((s, i) => [s, i]).sort(([a, i], [b, j]) => (TIER_RANK[a.tier] || 0) - (TIER_RANK[b.tier] || 0) || a.lvl - b.lvl || i - j).map(([s]) => s);
function shirtShelf() {
  const worn = ch.equip.shirt?.setShirt, have = Object.keys(ch.shirts || {}).length + (worn ? 1 : 0);
  return `<p class="dim">Funde un conjunto entero en el alambique (una pieza de cada, nada más) y se convierte en su camiseta encantada: todas sus bonificaciones y la mitad de las propiedades de sus piezas. Se lleva debajo de todo, en un sitio propio, así que el cuello queda libre para un collar. Con ella puesta se te ve con el conjunto entero, lleves lo que lleves encima, y lo de encima sigue dando lo suyo; puesta, un clic en ella para elegir qué piezas se ven. Una por conjunto. Tienes ${have} de ${SETS.length}.</p>
  <div class="necks">${SETS_BY_TIER.map((set) => {
    const it = ch.shirts?.[set.id] || (worn === set.id ? ch.equip.shirt : null), color = RARITY[set.tier || "set"].color;
    const sub = set.tier ? `Conjunto ${RARITY[set.tier].name.toLowerCase()} · ` : "";
    return `<div class="neckcard${it ? "" : " missing"}${worn === set.id ? " worn" : ""}" style="--nc:${color}">
      <div class="neckfig" ${it ? `title="Así te ves con ${esc(set.name)}"` : `aria-hidden="true"`}>${figureSvg(dressedIn(set), { still: true })}</div>
      <b style="color:${color}">${esc(set.name)}</b>
      <span class="dim small">${sub}nivel ${set.lvl} · ${set.pieces.length} piezas</span>
      <div class="neckfoot">${it ? `<button class="cell item r-${it.rarity}" data-id="${it.id}" title="${esc(E.itemName(it))}">${itemIco(it, true)}</button>` : `<span class="cell neckempty">${icon("leather-vest", color)}</span>`}
        <span class="small">${worn === set.id ? "La llevas puesta" : it ? `${touch() ? "Toca" : "Haz clic en"} la camiseta para ponértela` : "Aún no la tienes"}</span></div>
    </div>`;
  }).join("")}</div>`;
}
function renderInv() {
  const s = ch.swap;
  $("#invPanel").innerHTML = `
    <div class="ptitle"><div>Inventario</div><span class="goldamt" title="Oro">${icon("coins-pile", "#e2b84a")}${ch.gold} de oro</span><button id="invSort" class="ghost small" ${ch.inv.length > 1 ? "" : "disabled"} title="Ordena la bolsa: equipo (de mejor a peor rareza, por tipo, de más nivel a menos), gemas, pociones">Ordenar</button><button id="invList" class="ghost small" title="Todo en una tabla, sin pasar el ratón por encima">Ver como lista</button><button class="x" data-close="#invPanel" aria-label="Cerrar">×</button></div>
    <div class="doll">
      <div class="doll-portrait" id="dollFig"><span class="dolllvl" title="Nivel ${ch.level}">${ch.level}</span></div>
      ${slotCell(`weapon${s}`, "Arma", "w")}
      ${slotCell("head", "Cabeza", "head")}
      ${slotCell(`off${s}`, "Escudo", "o")}
      ${slotCell("neck", "Cuello", "neck")}
      ${slotCell("body", "Torso", "body")}
      ${slotCell("hands", "Manos", "hands")}
      ${slotCell("ring1", "Anillo", "r1")}
      ${slotCell("belt", "Cintura", "belt")}
      ${slotCell("ring2", "Anillo", "r2")}
      ${slotCell("feet", "Pies", "feet")}
      ${slotCell("shirt", "Camiseta", "shirt")}
    </div>
    <div class="swaprow"><button id="invSwap">Armas ${s === 1 ? "I" : "II"} <span class="dim">(cambiar: Alt+S)</span></button>
      <span class="dim">En reserva: ${[ch.equip[`weapon${3 - s}`], ch.equip[`off${3 - s}`]].filter(Boolean).map((x) => esc(E.itemName(x))).join(", ") || "nada"}</span></div>
    <div class="grid">${grid(ch.inv, INV_SIZE)}</div>
    <p class="dim small">Haz clic en un objeto para equiparlo, venderlo o engastar gemas.${Object.keys(ch.shirts || {}).length ? " Tus camisetas de conjunto están en la aldea, pestaña Camisetas." : ""}</p>`;
  dollFigure($("#dollFig"));
  $("#invSwap").onclick = swapWeapons;
  $("#invList").onclick = () => openItemList("inv");
  $("#invSort").onclick = sortBag;
}

// ---------- screens ----------
function show(view) {
  // a phone's panels cover the whole screen: going somewhere closes them
  if (view !== S.view && narrow()) { for (const o of ["#charPanel", "#invPanel", "#srcPanel"]) $(o).hidden = true; syncDrawers(); }
  S.view = view;
  // the streak lasts through the village too: it ends only when you miss or fall
  closeMenu(); tip.hidden = true;
  $("#hud").hidden = !ch || view === "create";
  ({ create: renderCreate, town: renderTown, map: renderMap, fight: renderFight, dead: renderDead })[view]();
  renderHud();
  placeMusic();
}
// the village's piece in the village (and while making a character), each zone's own in its fights; the
// map keeps what was playing; falling is silent
function placeMusic() {
  const v = S.view;
  if (v === "map") return;
  MUSIC.setPlace(v === "town" || v === "create" ? "aldea" : v === "fight" ? (S.F?.enc?.boss ? "jefe" : sceneOf(S.zone) || "aldea") : null);
}
function syncMusicBtn() {
  const b = $("#musicBtn");
  if (b) { b.textContent = MUSIC.isOn() ? "Música: sí" : "Música: no"; b.setAttribute("aria-pressed", String(MUSIC.isOn())); }
}

// ---------- the look editor ----------
// A preview and one row per choice: arrows through the options of a part (hair, beard ...) and
// swatches for colours. Options that don't exist for the body (a corset on the male body) are skipped.
const NONE = { nose: "Normal", ears: "Normales", wrinkles: "Sin arrugas", brows: "Sin cejas", hair: "Calvo", beard: "Sin barba", stache: "Sin bigote", shirt: "Sin camisa" };
const SWATCH_ROWS = [["skin", "body", "Piel"], ["eyes", "eye", "Ojos"], ["hairColor", "hair", "Color del pelo"], ["shirtColor", "cloth", "Color de la camisa"], ["legsColor", "cloth", "Color de las piernas"]];
// where each colour row goes: after the part it colours
const SWATCH_AFTER = { body: "skin", face: "eyes", stache: "hairColor", shirt: "shirtColor", legs: "legsColor" };
function lookEditor(el, start, cls, onChange, { withGear = null } = {}) {
  const LD = lookData();
  if (!LD) { el.innerHTML = `<p class="dim">No se pudo cargar el editor de aspecto.</p>`; return; }
  let look = fixLook(start, cls), gear = !!withGear;
  const preview = () => figureSvg({ ...(gear ? withGear : { cls, equip: {}, swap: 1 }), name: "Vista previa", look }, { cls: "big" });
  const swatches = ([key, mat, label]) => {
    const P = LD.pal[mat];
    // a top that only comes in some colours offers just those
    const part = { shirtColor: "shirt", legsColor: "legs" }[key], o = part && LD.slots.find((x) => x.id === part).opts.find((x) => x.id === look[part]);
    const list = Object.keys(P.c).filter((c) => !o?.v || o.v[c]);
    return `<div class="lrow"><span class="llabel">${label}</span><div class="swatches" role="radiogroup" aria-label="${label}">${list.map((c) =>
      `<button class="sw${look[key] === c ? " on" : ""}" role="radio" aria-checked="${look[key] === c}" data-sw="${key}" data-v="${c}" title="${esc(P.names[c])}" aria-label="${esc(P.names[c])}"
        style="background:linear-gradient(135deg, ${P.c[c][Math.min(4, P.c[c].length - 1)]} 0 50%, ${P.c[c][Math.max(0, P.c[c].length - 3)]} 50%)"></button>`).join("")}</div>
      <span class="lval">${esc(P.names[look[key]] || "")}</span></div>`;
  };
  const choices = (S2) => [...(S2.none ? [null] : []), ...S2.opts.filter((o) => fits(S2.id, o, look)).map((o) => o.id)];
  const row = (S2) => {
    const o = S2.opts.find((x) => x.id === look[S2.id]);
    const n = choices(S2).length, i = choices(S2).indexOf(look[S2.id]) + 1;
    return `<div class="lrow"><span class="llabel">${S2.label}</span>
      <button class="larr" data-step="-1" data-slot="${S2.id}" aria-label="${S2.label}: anterior">‹</button>
      <span class="lval">${esc(o ? o.label : NONE[S2.id] || "Ninguno")}<small>${i}/${n}</small></span>
      <button class="larr" data-step="1" data-slot="${S2.id}" aria-label="${S2.label}: siguiente">›</button></div>`;
  };
  const draw = () => {
    const rows = LD.slots.map((S2) => row(S2) + (SWATCH_AFTER[S2.id] ? swatches(SWATCH_ROWS.find((r) => r[0] === SWATCH_AFTER[S2.id])) : "")).join("");
    el.innerHTML = `<div class="looked">
      <div class="lookprev">${preview()}
        ${withGear ? `<label class="small"><input type="checkbox" id="lookGear" ${gear ? "checked" : ""}> Con el equipo</label>` : ""}
        <div class="lookbtns"><button id="lookRand">Al azar</button><button id="lookDef">El de la clase</button></div></div>
      <div class="lookrows">${rows}</div></div>`;
    el.querySelectorAll("[data-step]").forEach((b) => (b.onclick = () => {
      const S2 = LD.slots.find((x) => x.id === b.dataset.slot), c = choices(S2);
      const v = c[(c.indexOf(look[S2.id]) + +b.dataset.step + c.length) % c.length], change = { [S2.id]: v };
      // a new body brings its usual face shape, and a woman starts without the beard (both can be put back)
      if (S2.id === "body") {
        const other = { male: "human_female", female: "human_male" }[v];
        if (look.head === other) change.head = v === "female" ? "human_female" : "human_male";
        if (v === "female") Object.assign(change, { beard: null, stache: null });
      }
      set(change, `[data-slot="${S2.id}"][data-step="${b.dataset.step}"]`);
    }));
    el.querySelectorAll("[data-sw]").forEach((b) => (b.onclick = () => set({ [b.dataset.sw]: b.dataset.v }, `[data-sw="${b.dataset.sw}"][data-v="${b.dataset.v}"]`)));
    $("#lookRand", el).onclick = () => set(randomLook(cls), "#lookRand");
    $("#lookDef", el).onclick = () => set(defaultLook(cls), "#lookDef");
    if ($("#lookGear", el)) $("#lookGear", el).onchange = (e) => { gear = e.target.checked; draw(); };
  };
  // change, recolour what's new, redraw, and keep the focus on the control you used
  const set = async (change, focusSel) => {
    look = fixLook({ ...look, ...change }, cls);
    await prepareLook(look).catch(() => {});
    draw();
    el.querySelector(focusSel)?.focus();
    onChange(look);
  };
  prepareLook(look).then(draw, draw);
  return { get look() { return look; } };
}
function openLookDialog() {
  const before = ch.look;
  dialog(`<h3>Aspecto de ${esc(ch.name)}</h3><div id="lookEdD"></div>
    <div class="row"><button id="lookSave" class="primary">Guardar</button><button id="lookCancel" class="ghost">Cancelar</button></div>`, { cls: "lookdlg" });
  const ed = lookEditor($("#lookEdD"), lookOfChar(ch), ch.cls, () => {}, { withGear: ch });
  $("#lookSave").onclick = async () => {
    ch.look = ed.look;
    await prepareLook(ch.look).catch(() => {});
    save(); closeDialog(); renderPanels(); renderHud();
    if (S.view === "fight") renderMe(); else if (S.view !== "create") show(S.view);
    toast("Aspecto guardado");
  };
  $("#lookCancel").onclick = () => { ch.look = before; closeDialog(); };
}

// Two ways out of a class: change it and keep everything (the attribute points you placed come back
// to place again), or start a new character from nothing.
function openClassDialog() {
  const fighting = S.view === "fight";
  const d = dialog(`<h3>Cambiar de clase</h3>
    <p class="dim">Te quedas con todo: nivel, experiencia, equipo, oro, alijo, frases dominadas, mascotas y monturas, y tu aspecto. Tus atributos vuelven a los de la nueva clase y te devuelvo los puntos que habías asignado (${spentPoints()}), para que los repartas otra vez. La nueva clase trae sus propias ventajas${CLASSES.brujo ? "; el brujo, además, sus hechizos (con varita o bastón)" : ""}.</p>
    ${fighting ? `<p class="warn">Termina o abandona el combate para cambiar de clase.</p>` : ""}
    <div class="classes">${Object.entries(CLASSES).map(([id, c]) => `<button class="cls" data-newcls="${id}" ${id === ch.cls || fighting ? "disabled" : ""}>${icon(c.icon, "#d8c49a", "big")}<b>${c.name}${id === ch.cls ? " (la tuya)" : ""}</b><span>${esc(c.blurb)}</span></button>`).join("")}</div>
    <h3>Empezar de cero</h3>
    <p class="dim">Un personaje nuevo de nivel 1: se pierde todo lo de ${esc(ch.name)} (equipo, oro, alijo, progreso en las zonas y en los episodios, mascotas y monturas). Tus mazos de Anki no cambian. Hasta que crees el nuevo, si recargas la página sigues teniendo a ${esc(ch.name)}.</p>
    ${(ch.pets?.length || ch.mounts?.length) ? `<p class="dim">O empieza de cero quedándote con tus ${[ch.pets?.length && `mascotas (${ch.pets.length})`, ch.mounts?.length && `monturas (${ch.mounts.length})`].filter(Boolean).join(" y ")}: todo lo demás se pierde igual.</p>` : ""}
    <div class="row"><button id="wipeBtn" class="danger" ${fighting ? "disabled" : ""}>Empezar de cero…</button>${(ch.pets?.length || ch.mounts?.length) ? `<button id="wipeKeepBtn" class="danger" ${fighting ? "disabled" : ""}>Empezar de cero, con mascotas y monturas…</button>` : ""}<button id="classCancel" class="ghost">Cancelar</button></div>`, { cls: "classdlg" });
  d.querySelectorAll("[data-newcls]").forEach((b) => (b.onclick = () => changeClass(b.dataset.newcls)));
  d.querySelector("#classCancel").onclick = () => closeDialog();
  const twoClicks = (btn, sure, go) => btn && (btn.onclick = () => {
    if (!btn.dataset.sure) { btn.dataset.sure = 1; btn.textContent = sure; return; }
    go();
  });
  twoClicks(d.querySelector("#wipeBtn"), `Sí, borrar a ${ch.name} y empezar de cero`, () => startOver(false));
  twoClicks(d.querySelector("#wipeKeepBtn"), `Sí, borrar a ${ch.name} (menos mascotas y monturas)`, () => startOver(true));
}
const spentPoints = () => Object.entries(ch.base).reduce((n, [k, v]) => n + Math.max(0, v - (CLASSES[ch.cls].stats[k] ?? 0)), 0);
function changeClass(cls) {
  const back = spentPoints(), was = CLASSES[ch.cls].name;
  ch.look = lookOfChar(ch); // keep the face you had, even if it was the old class's own
  ch.cls = cls;
  ch.base = { ...CLASSES[cls].stats };
  ch.points = (ch.points || 0) + back;
  ch.spell = null;
  const st = stats();
  ch.life = Math.min(ch.life, st.maxLife); ch.mana = Math.min(ch.mana, st.maxMana);
  save(); closeDialog(); renderPanels(); renderHud(); if (S.view === "town") renderTown();
  toast(`Ahora eres ${CLASSES[cls].name.toLowerCase()} (antes, ${was.toLowerCase()}). ${ch.points ? `Tienes ${ch.points} puntos por asignar.` : ""}`, "levelup", 4500);
}
function startOver(keepCompanions) {
  S.newLook = lookOfChar(ch);
  // carried into the next character made (not saved anywhere until then)
  S.carry = keepCompanions ? { pets: [...(ch.pets || [])], mounts: [...(ch.mounts || [])], pet: ch.pet || null, mount: ch.mount || null } : null;
  const name = ch.name;
  closeDialog();
  for (const id of ["#charPanel", "#invPanel"]) { const el = $(id); if (el) el.hidden = true; }
  syncDrawers();
  ch = null;
  show("create");
  const n = $("#cname"); if (n) n.value = name;
}
function renderCreate() {
  screen.innerHTML = `
    <section class="create">
      <h2>Una nueva leyenda</h2>
      <p class="lead">Cada golpe es una frase que escuchas. Si la entiendes bien, golpeas fuerte y esquivas. Si no, te golpean a ti.</p>
      <label class="name">Nombre <input id="cname" maxlength="20" value="Viajero" autocomplete="off"></label>
      <div class="lookbox"><h3>Aspecto</h3>
        <p class="dim small" id="lookNote">${S.newLook ? "Este aspecto será el de tu personaje, elijas la clase que elijas." : "Si no lo cambias, cada clase trae el suyo."}</p>
        <div id="lookEd"></div></div>
      <h3>Clase</h3>
      <div class="classes">
        ${Object.entries(CLASSES).map(([id, c]) => `
          <button class="cls" data-cls="${id}">${icon(c.icon, "#d8c49a", "big")}<b>${c.name}</b><span>${esc(c.blurb)}</span>${POWERS[id] ? `<span class="clspow" style="color:${POWERS[id].color}">${esc(POWERS[id].name)}: <span class="dim">${esc(POWERS[id].desc)}</span></span>` : ""}</button>`).join("")}
      </div>
    </section>`;
  // the look you pick here is kept whatever the class; untouched, each class brings its own
  lookEditor($("#lookEd"), S.newLook || defaultLook("guerrero"), "guerrero", (look) => {
    S.newLook = look;
    $("#lookNote").textContent = "Este aspecto será el de tu personaje, elijas la clase que elijas.";
  });
  screen.querySelectorAll(".cls").forEach((b) => (b.onclick = async () => {
    ch = E.newCharacter($("#cname").value.trim() || "Viajero", b.dataset.cls);
    ch.look = fixLook(S.newLook || defaultLook(b.dataset.cls), b.dataset.cls);
    S.newLook = null;
    if (S.carry) { Object.assign(ch, S.carry); S.carry = null; }
    useEpisodeZones();
    await prepareLook(ch.look).catch(() => {});
    save();
    toast("Bienvenido a la aldea");
    show("town");
  }));
}

const narrow = () => innerWidth < 760;
const touch = () => matchMedia("(hover: none)").matches;
// on a phone the inventory panel would cover the stash or the alembic: show the bag right here instead
const invInline = () => (narrow() ? `<h3 class="rwtitle">Tu inventario <span class="dim">${ch.inv.length}/${INV_SIZE}</span></h3><div class="grid">${grid(ch.inv, INV_SIZE)}</div>` : "");
// Town: merchant (potions), stash, alembic, and the road out.
// Each village tab has its own scene (scripts/build_scenes.py, v-<tab>.png) and what moves in it,
// placed in % of the picture: [kind, x, y, count or size, spread].
const TOWN_FX = {
  merchant: [["glow", 25, 80, 70, "255,150,60"], ["flame", 25, 82, 1], ["ember", 25, 78, 10, 3], ["smoke", 25, 70, 3, 2], ["glow", 62, 50, 120, "255,210,150"]],
  casetes: [["pulse", 52.5, 50, 70, "255,210,110"], ["ring", 52.5, 42, 3], ["sparkle", 52.5, 50, 4, 2], ["sparkle", 36, 64, 5, 7], ["sparkle", 80.6, 38, 3, 4], ["sparkle", 19.4, 62, 3, 2], ["glow", 45.7, 56, 70, "255,190,100"], ["flame", 45.7, 57, 1], ["glow", 25.2, 56, 70, "255,190,100"], ["flame", 25.2, 57, 1], ["glow", 83, 33, 120, "255,160,80"], ["flame", 77.5, 33, 1], ["flame", 80, 33, 1], ["flame", 88.6, 33, 1], ["flame", 90.7, 33, 1], ["dust", 50, 30, 8, 14]],
  sell: [["sparkle", 37, 52, 4, 3], ["sparkle", 63.5, 54, 3, 2], ["shaft", 49, 30, 1], ["dust", 49, 40, 10, 8]],
  stash: [["flame", 32.6, 40, 1], ["flame", 68, 40, 1], ["glow", 32.6, 30, 110, "255,160,70"], ["glow", 68, 30, 110, "255,160,70"], ["dust", 50, 50, 12, 40]],
  alembic: [["bubble", 55.8, 56, 4, 1], ["bubble", 59.2, 56, 4, 1], ["bubble", 62.5, 56, 4, 1], ["steam", 35.4, 34, 4, 1.5], ["steam", 86, 30, 3, 1], ["flame", 35.4, 66, 1], ["glow", 35.4, 66, 60, "255,140,50"], ["glow", 86.7, 86, 50, "255,120,40"]],
};
// Camisetas: the room is drawn with empty pegs; the undershirts you have hang on them
// (scripts/build_scenes.py writes their strip and where each one goes)
let NECKS = null;
fetch("rpg/scenes/v-camisetas-shirts.json").then((r) => r.json()).then((j) => { NECKS = j; if (S.view === "town" && S.townTab === "camisetas") renderTown(); }).catch(() => {});
function hungShirts() {
  if (!NECKS) return "";
  const [cw, ch_] = NECKS.cell, [W, H] = NECKS.scene, n = NECKS.n;
  const have = new Set([...Object.keys(ch.shirts || {}), ch.equip.shirt?.setShirt].filter(Boolean));
  const url = new URL("rpg/scenes/v-camisetas-shirts.png", location.href).href;
  return Object.entries(NECKS.at).filter(([sid]) => have.has(sid)).map(([sid, [x, y, i]]) => {
    const set = SETS.find((s) => s.id === sid);
    return `<b class="hungneck${ch.equip.shirt?.setShirt === sid ? " worn" : ""}" title="${esc(set?.name || sid)}" style="left:${x}%;top:${y}%;width:${(cw / W) * 100}%;height:${(ch_ / H) * 100}%;background-image:url('${url}');background-size:${n * 100}% 100%;background-position:${(i / (n - 1)) * 100}% 0"></b>`;
  }).join("");
}
// ---------- the Montón: perfect gems thrown on a pile, for nothing but the pile ----------
// Where the k-th gem lies: the pile is always a pyramid (rows b, b-1 … 1) being finished. Going from
// base b-1 to b adds one gem to every row, bottom first so each rests on two below, on the right for
// odd b and the left for even, so the heap grows evenly. x in gem widths, r the row from the ground.
function moundCells(n) {
  const cells = []; let lo = 0;
  for (let b = 1; cells.length < n; b++) {
    const left = b % 2 === 0;
    if (left) lo -= 1;
    for (let r = 0; r < b && cells.length < n; r++) cells.push([left ? lo + r / 2 : lo + r / 2 + (b - 1 - r), r]);
  }
  return cells;
}
const moundRand = (k, i) => { const x = Math.sin(k * 127.1 + i * 311.7) * 43758.5453; return x - Math.floor(x); };
function moundScene() {
  const M = ch.mound || [], cells = moundCells(M.length);
  const xs = cells.map(([x]) => x), lo = Math.min(0, ...xs), hi = Math.max(0, ...xs), rows = Math.max(1, ...cells.map(([, r]) => r + 1));
  // the scene is 3 times as wide as tall: one gem's width in % of the width, and its height (rows overlap)
  // as big as fits both ways: the width of the base, and the rows plus the top gem's height under the top edge
  const u = Math.min(9, 92 / Math.max(hi - lo + 1, 6), 86 / (3 * (0.74 * (rows - 1) + 0.86))), rowH = u * 3 * 0.74, mid = (lo + hi) / 2;
  const gems = M.map((g, k) => {
    const [x, r] = cells[k], sh = GEMS[g].shades || [GEMS[g].color, GEMS[g].color, GEMS[g].color];
    const jx = (moundRand(k, 1) - 0.5) * 0.16, rot = Math.round((moundRand(k, 2) - 0.5) * 30), tw = moundRand(k, 3) < 0.08;
    return `<i class="mgem${tw ? " tw" : ""}${k === M.length - 1 && S.moundDrop ? " drop" : ""}" style="left:${(50 + (x - mid + jx - 0.5) * u).toFixed(2)}%;bottom:${(8 + r * rowH).toFixed(2)}%;width:${u.toFixed(2)}%;--rot:${rot}deg;--a:${sh[2]};--b:${sh[1]};--c:${sh[0]};--tw:${(moundRand(k, 4) * 6).toFixed(1)}s"></i>`;
  }).join("");
  S.moundDrop = false;
  return `<div class="townscene moundscene" aria-hidden="true"><i class="moundglow"></i>${gems}</div>`;
}
const perfectGems = () => [...ch.inv.map((it) => [it, "inv"]), ...(ch.stash || []).map((it) => [it, "stash"])].filter(([it]) => it.kind === "gem" && it.grade === 2);
function moundPanel() {
  const M = ch.mound || [], have = perfectGems();
  const count = (list, g) => list.filter((x) => x === g).length;
  const types = Object.keys(GEMS);
  const relics = [...ch.inv, ...(ch.stash || [])].filter((x) => x.kind === "relic"), k = Math.floor(M.length / MOUND_STEP);
  const transform = `<div class="moundrelic${relics.length ? " have" : ""}">${itemIco(E.makeRelic())}<div><b style="color:${RARITY.relic.color}">Transformador del montón</b>
    <span class="dim">${relics.length ? `Tienes ${relics.length}. ` : "Cae muy rara vez, sobre todo de los jefes. "}Por cada ${MOUND_STEP} gemas perfectas del montón: un objeto mítico, una mascota o una montura. Se gasta al usarlo.${k ? ` Ahora daría ${k} ${k === 1 ? "premio" : "premios"}${M.length % MOUND_STEP ? ` y quedarían ${M.length % MOUND_STEP} gemas` : ""}.` : ` Te faltan ${MOUND_STEP - (M.length % MOUND_STEP)} gemas para el primero.`}</span></div>
    <button id="moundGo" class="primary" ${relics.length && k ? "" : "disabled"}>Transformar el montón</button></div>`;
  return `${transform}<div class="row">${massGemButton()}</div><p class="dim">Al montón se echan gemas perfectas. Solas no dan nada: se quedan ahí, una encima de otra. ${touch() ? "Toca" : "Clic en"} una gema perfecta de la bolsa para echarla, o usa los botones.</p>
    <h3 class="rwtitle">${M.length ? `${M.length} ${M.length === 1 ? "gema perfecta" : "gemas perfectas"} en el montón` : "El montón está vacío"}</h3>
    ${M.length ? `<p class="moundcount">${types.filter((g) => M.includes(g)).map((g) => `<span style="color:${GEMS[g].color}">◆ ${esc(GEMS[g].name)} ${count(M, g)}</span>`).join(" ")}</p>` : ""}
    <div class="shop">${types.map((g) => { const n = have.filter(([it]) => it.gem === g).length, tmp = E.makeGem(g, 2);
      return `<div class="ware">${itemIco(tmp)}<div><b style="color:${E.itemColor(tmp)}">${esc(E.itemName(tmp))}</b><span class="dim">${n ? `tienes ${n}` : "no tienes"}</span></div><button data-throw="${g}" ${n ? "" : "disabled"}>Echar una</button>${n > 1 ? `<button data-throw="${g}" data-all="1">Echar las ${n}</button>` : ""}</div>`; }).join("")}</div>`;
}
// The transformer: every MOUND_STEP gems (the last thrown first, so the heap shrinks from the top) become
// one prize: a mythic, a pet or a mount, a third each (only kinds you can still get: a pet or mount you don't have)
const MOUND_STEP = 100;
function transformMound() {
  const M = ch.mound || [], k = Math.floor(M.length / MOUND_STEP);
  const relic = ch.inv.find((x) => x.kind === "relic") || (ch.stash || []).find((x) => x.kind === "relic");
  if (!relic || !k) return;
  const from = ch.inv.includes(relic) ? ch.inv : ch.stash;
  from.splice(from.indexOf(relic), 1);
  M.splice(M.length - k * MOUND_STEP);
  for (let i = 0; i < k; i++) {
    const kinds = ["item", ...["pet", "mount"].filter((t) => Object.keys(COMPANION[t].list).some((id) => !(ch[COMPANION[t].own] || []).includes(id)))];
    const kind = kinds[Math.floor(Math.random() * kinds.length)];
    if (kind === "item") {
      const it = E.makeTopItem("mitico", ch.level + 2);
      const where = stow(it) || (ch.inv.push(it), "a tu bolsa");
      celebrate({ mound: true, it, where, i, n: k });
    } else {
      const C = COMPANION[kind], own = (ch[C.own] ||= []), fresh = Object.keys(C.list).filter((id) => !own.includes(id));
      const id = fresh[Math.floor(Math.random() * fresh.length)];
      own.push(id); if (!ch[C.on]) ch[C.on] = id;
      celebrate({ mound: true, companion: kind, id, i, n: k });
    }
  }
  save(); renderTown(); renderPanels(); renderMe(); renderHud();
}
// Every gem in the bag and the stash, 3 of a kind and grade at a time, into the next grade, all at once and
// on up: chips into gems, then those gems (old and new) into perfect ones. Leftovers (1 or 2 of a kind) stay.
function gemMerges() {
  const pool = {};
  for (const where of [ch.inv, ch.stash || []]) for (const it of where) if (it.kind === "gem" && it.grade < 2) ((pool[it.gem] ||= [0, 0])[it.grade]++);
  let merges = 0, perfect = 0;
  for (const [a, b] of Object.values(pool)) { const up = Math.floor(a / 3); merges += up; const p = Math.floor((b + up) / 3); merges += p; perfect += p; }
  return { merges, perfect };
}
function massGemButton() {
  const { merges, perfect } = gemMerges();
  return `<button id="massGems" ${merges ? "" : "disabled"} title="Todas las gemas de la bolsa y del alijo, de 3 en 3 (mismo tipo y grado), a la siguiente; y las nuevas también, hasta perfectas. Las que sobren se quedan.">Fundir todas las gemas${merges ? ` (${merges} ${merges === 1 ? "fusión" : "fusiones"}${perfect ? `, ${perfect} ${perfect === 1 ? "perfecta" : "perfectas"}` : ""})` : ""}</button>`;
}
function massGems() {
  const refs = {}; // gem type → grade → [[item, its list]]
  for (const where of [ch.inv, ch.stash || []]) for (const it of where) if (it.kind === "gem" && it.grade < 2) (((refs[it.gem] ||= [[], [], []])[it.grade]).push([it, where]));
  const made = [0, 0, 0];
  for (const [g, grades] of Object.entries(refs)) for (const grade of [0, 1]) {
    const list = grades[grade];
    while (list.length >= 3) {
      const used = list.splice(-3);
      for (const [it, where] of used) where.splice(where.indexOf(it), 1);
      // the new one goes where the first of the three was: there's room, three just left it
      const home = used[0][1], gem = E.makeGem(g, grade + 1);
      home.push(gem); made[grade + 1]++;
      if (grade + 1 < 2) grades[grade + 1].push([gem, home]);
    }
  }
  if (!made[1] && !made[2]) return toast("No hay 3 gemas iguales para fundir");
  toast(`Fundidas: ${[made[1] && `${made[1]} ${made[1] === 1 ? "gema" : "gemas"}`, made[2] && `${made[2]} ${made[2] === 1 ? "perfecta" : "perfectas"}`].filter(Boolean).join(" y ")}`, "levelup", 3500);
  sfx.coin?.();
  save(); renderTown(); renderPanels();
}
// throw up to n perfect gems of a type (a given one first, if clicked), from the bag, then the stash
function throwGems(g, n, id = null) {
  const list = perfectGems().filter(([it]) => it.gem === g).sort(([a], [b]) => (b.id === id) - (a.id === id));
  let k = 0;
  for (const [it, where] of list) {
    if (k >= n) break;
    const arr = where === "inv" ? ch.inv : ch.stash, i = arr.indexOf(it);
    if (i < 0) continue;
    arr.splice(i, 1); (ch.mound ||= []).push(g); k++;
  }
  if (!k) return;
  S.moundDrop = true;
  sfx.coin?.();
  save(); renderTown(); renderPanels();
}
function townScene(tab) {
  const r = (a, b) => (a + Math.random() * (b - a)).toFixed(2);
  const fx = (TOWN_FX[tab] || []).flatMap(([k, x, y, n, spread = 0]) => {
    if (k === "ring") return Array.from({ length: n }, (_, i) => `<i class="tfx-ring" style="left:${x}%;top:${y}%;animation-delay:${(i * 1.4).toFixed(1)}s"></i>`);
    if (k === "pulse") return [`<i class="tfx-glow tfx-pulse" style="left:${x}%;top:${y}%;--r:${n}px;--c:${spread}"></i>`];
    if (k === "glow") return [`<i class="tfx-glow" style="left:${x}%;top:${y}%;--r:${n}px;--c:${spread}"></i>`];
    if (k === "eq") return Array.from({ length: n }, (_, i) => `<i class="tfx-eq" style="left:calc(${x}% + ${i * 4}px);top:${y}%;--d:${r(0.35, 0.8)}"></i>`);
    if (k === "flame" || k === "shaft") return [`<i class="tfx-${k}" style="left:${x}%;top:${y}%"></i>`];
    return Array.from({ length: n }, () => `<i class="tfx-${k}" style="left:${(x + (Math.random() * 2 - 1) * spread).toFixed(2)}%;top:${y}%;--d:${r(0.7, 1.4)};--t:${r(-1, 0)};--k:${Math.random() < 0.5 ? -1 : 1}"></i>`);
  }).join("");
  if (tab === "monton") return moundScene();
  return `<div class="townscene" style="background-image:url('${new URL(`rpg/scenes/v-${tab}.png`, location.href).href}')" aria-hidden="true">${fx}${tab === "camisetas" ? hungShirts() : ""}</div>`;
}
function renderTown() {
  dropRunes(); necklacesToShirts(); attuneTunjo();
  const st = stats();
  ch.life = st.maxLife; ch.mana = st.maxMana; // rest in town
  S.townTab = S.townTab === "collares" ? "camisetas" : S.townTab === "gamble" || S.townTab === "coleccion" ? "merchant" : S.townTab || "merchant"; // (Apuestas and Colección are gone)
  const tierNow = ch.level >= 24 ? 2 : ch.level >= 10 ? 1 : 0;
  const tabs = [["merchant", "Mercader"], ["casetes", "Tunjos"], ["sell", "Vender"], ["stash", "Alijo"], ["alembic", "Alambique"], ["camisetas", "Camisetas"], ["monton", "Montón"]];
  let body = "";
  if (S.townTab === "merchant") {
    body = `<p class="dim">Pociones para el camino. Para vender, la pestaña Vender.</p><div class="shop">` +
      ["life", "mana", "rejuv"].map((type) => {
        const P = POTIONS[type], tier = type === "rejuv" ? 0 : tierNow, price = P.price[tier];
        const tmp = E.makePotion(type, tier);
        return `<div class="ware">${itemIco(tmp)}<div><b>${esc(E.itemName(tmp))}</b><span class="dim">${price} de oro</span></div><button data-buy="${type}" ${ch.gold < price ? "disabled" : ""}>Comprar</button></div>`;
      }).join("") + `</div><button id="fillBelt">Llenar el cinturón</button>${touch() ? "" : keysCard()}`;
  } else if (S.townTab === "casetes") {
    const p = tunjoPrice(), wait = tunjoWait(), G = ch.grimoire || [];
    const short = Math.max(0, p - ch.gold);
    body = `<p class="dim">Doña Remedios guarda tunjos que hablan: figuritas de oro que alguien ofrendó a la laguna y que todavía repiten lo que les dijeron al oído. Le queda uno al día, y no lo regala. Dice una frase entera del episodio y tú tienes una sola respuesta: si la entiendes palabra por palabra, a sus pies cae un objeto del arcoíris, de los que no salen en ningún otro sitio.</p>
      <div class="shop"><div class="ware tunjoware">${icon("tunjo", "#d8b84a")}<div><b class="rainbow">Tunjo que habla</b><span class="dim">${p.toLocaleString("es")} de oro</span></div>
        <button id="buyTunjo" ${wait || short ? "disabled" : ""}>Comprar y oír</button></div></div>
      <p class="dim small">${wait ? `El próximo tunjo, en ${hoursLeft(wait)}.` : short ? `Te faltan ${short.toLocaleString("es")} de oro.` : "Hoy tienes uno."} Si la frase no coincide con su audio (No coincide), te devuelve el oro y puedes comprar otro.</p>
      ${tunjoPrizes()}
      ${CFG.online ? "" : `<h3 class="rwtitle">Grimorio</h3>`}
      ${CFG.online ? "" : G.length ? `<ol class="grimoire">${G.map((g, i) => `<li><b>${esc(g.name)}</b><p class="gtext">${esc(g.text)}</p>${g.ep === S.ep ? `<button data-gplay="${i}">▶ Oír</button>` : ""}</li>`).join("")}</ol>
        <p class="dim">En combate, después de una frase: Grimorio (G), y lees el pasaje en voz alta.</p>`
      : `<p class="dim">Vacío. La frase de un tunjo que entiendas queda aquí como conjuro.</p>`}`;
  } else if (S.townTab === "sell") {
    const back = S.sold || [];
    body = `<p class="dim">${touch() ? "Toca" : "Clic en"} un objeto del inventario y se vende al momento. Lo equipado y el cinturón no se venden así.</p>${invInline()}
      ${back.length ? `<h3 class="rwtitle">Vendido hace poco</h3><div class="shop">${back.map((it, i) => `<div class="ware">${itemIco(it)}<div><b style="color:${E.itemColor(it)}">${esc(E.itemName(it))}</b><span class="dim">${E.itemValue(it)} de oro</span></div><button data-buyback="${i}" ${ch.gold < E.itemValue(it) ? "disabled" : ""}>Recomprar</button></div>`).join("")}</div>` : ""}`;
  } else if (S.townTab === "camisetas") {
    body = shirtShelf();
  } else if (S.townTab === "monton") {
    body = moundPanel();
  } else if (S.townTab === "stash") {
    body = `<p class="dim">Lo que guardes aquí no ocupa el inventario. ${touch() ? "Toca un objeto del inventario para guardarlo, y uno del alijo para sacarlo." : "Clic en un objeto del inventario para guardarlo, y en uno del alijo para sacarlo. Clic derecho para más opciones."}</p>${invInline()}<h3 class="rwtitle">El alijo <span class="dim">${ch.stash.length}/${STASH_SIZE}</span></h3><div class="grid stash" style="--scols:${(stashColsShown = stashCols())}">${grid(ch.stash, stashShown(stashColsShown))}</div><div class="row"><button id="sortStash" ${ch.stash.length > 1 ? "" : "disabled"} title="Equipo (de mejor a peor, cada conjunto junto), gemas, pociones">Ordenar el alijo</button><button id="stashList" title="El alijo en una tabla, sin pasar el ratón por encima">Ver como lista</button></div>${unidCount() ? `<button id="idAll" class="idall">Identificar uno tras otro <span class="dim">(${unidCount()} sin identificar, en la bolsa y el alijo)</span></button>` : ""}`;
  } else {
    body = `<p class="dim">Pon objetos del inventario en el alambique y transmuta. ${touch() ? "Toca" : "Clic en"} un objeto del inventario para meterlo, y en el alambique para sacarlo.${touch() ? "" : " Clic derecho para más opciones."}</p>
      <div class="alembic">${[...Array(ALEM_SIZE).keys()].map((i) => { const it = S.alembic[i]; return it ? `<button class="cell item r-${it.rarity}" data-alem="${i}" title="${esc(E.itemName(it))}">${itemIco(it)}</button>` : `<span class="cell"></span>`; }).join("")}</div>
      <div class="row"><button id="transmute" class="primary" ${S.alembic.length ? "" : "disabled"}>Transmutar</button><button id="emptyAlem" ${S.alembic.length ? "" : "disabled"}>Vaciar</button>${massGemButton()}</div>
      ${invInline()}
      <ul class="recipes">${E.RECIPES.map((r) => `<li>${esc(r)}</li>`).join("")}</ul>
      ${runaGuide()}`;
  }
  screen.innerHTML = `
    <section class="town">
      <div class="townhead">${icon("village", "#d8c49a", "big")}<div><h2>La aldea</h2><p class="dim">Descansas junto al fogón: vida y maná al máximo.</p></div>
        <button id="toMap" class="primary">Salir al camino</button></div>
      <div class="tabs">${tabs.map(([id, l]) => `<button data-tab="${id}" class="${S.townTab === id ? "on" : ""}">${l}</button>`).join("")}</div>
      ${townScene(S.townTab)}
      <div class="townbody">${body}</div>
    </section>`;
  screen.querySelectorAll("[data-tab]").forEach((b) => (b.onclick = () => {
    S.townTab = b.dataset.tab;
    // the stash works by clicking items in the inventory, so open it alongside
    if ((S.townTab === "stash" || S.townTab === "sell") && $("#invPanel").hidden && !narrow()) { $("#srcPanel").hidden = true; $("#invPanel").hidden = false; syncDrawers(); }
    renderTown(); renderPanels();
  }));
  $("#toMap").onclick = () => show("map");
  $("#moundGo")?.addEventListener("click", transformMound);
  screen.querySelectorAll("[data-throw]").forEach((b) => (b.onclick = () => throwGems(b.dataset.throw, b.dataset.all ? Infinity : 1)));
  $("#buyTunjo")?.addEventListener("click", buyTunjo);
  screen.querySelectorAll("[data-tback]").forEach((b) => (b.onclick = () => tunjoBack(b.dataset.tback)));
  $("#sortStash")?.addEventListener("click", sortStash);
  $("#idAll")?.addEventListener("click", () => { const n = nextUnid(); if (n) identify(n.id, true); });
  $("#stashList")?.addEventListener("click", () => openItemList("stash"));
  screen.querySelectorAll("[data-gplay]").forEach((b) => (b.onclick = () => { const g = ch.grimoire[+b.dataset.gplay]; playRange(g.start, g.end); }));
  screen.querySelectorAll("[data-buy]").forEach((b) => (b.onclick = () => buyPotion(b.dataset.buy)));
  screen.querySelectorAll("[data-buyback]").forEach((b) => (b.onclick = () => {
    const it = S.sold[+b.dataset.buyback], price = E.itemValue(it);
    if (ch.inv.length >= INV_SIZE) return toast("El inventario está lleno");
    if (ch.gold < price) return toast("No te alcanza el oro");
    ch.gold -= price; ch.inv.push(it); S.sold.splice(+b.dataset.buyback, 1);
    save(); renderHud(); renderPanels(); renderTown();
  }));
  $("#fillBelt")?.addEventListener("click", () => { while (ch.belt.length < stats().beltSlots && buyPotion("life", true) && ch.belt.length < stats().beltSlots && buyPotion("mana", true)); renderTown(); });
  screen.querySelectorAll("[data-alem]").forEach((b) => (b.onclick = () => { ch.inv.push(S.alembic.splice(+b.dataset.alem, 1)[0]); save(); renderTown(); renderPanels(); }));
  $("#massGems")?.addEventListener("click", massGems);
  $("#emptyAlem")?.addEventListener("click", () => { ch.inv.push(...S.alembic); S.alembic = []; save(); renderTown(); renderPanels(); });
  $("#transmute")?.addEventListener("click", () => {
    const r = E.alembic(S.alembic);
    if (!r) return toast("Esa combinación no hace nada");
    if (!r.result) return toast(r.text); // a recipe that can't apply to these: nothing is used up
    if (r.shirt && (ch.shirts?.[r.setId] || ch.equip.shirt?.setShirt === r.setId)) return toast(`Ya tienes la camiseta de ${r.set}: solo hay una por conjunto.`, "", 4000);
    S.alembic = [];
    if (r.shirt) {
      (ch.shirts ||= {})[r.setId] = r.shirt;
      save(); renderTown(); renderPanels();
      return celebrate({ it: r.shirt, melt: r.set, neck: true, where: "a tus camisetas (pestaña Camisetas)" });
    }
    if (r.results) { // a whole set melted: its own celebration, the prizes into the bag (or the stash)
      // the pieces came out of the bag, so there's room for what comes back; the stash or the bag over its size otherwise
      r.results.forEach((it, i) => celebrate({ it, where: stow(it) || (ch.inv.push(it), "a tu bolsa"), melt: r.set, i, n: r.results.length }));
      save(); renderTown(); renderPanels();
      return;
    }
    ch.inv.push(r.result);
    toast(`${r.text} ${E.itemName(r.result)}`, `r-${r.result.rarity}`, 3500);
    save(); renderTown(); renderPanels();
  });
}
function buyPotion(type, quiet) {
  const tier = type === "rejuv" ? 0 : ch.level >= 24 ? 2 : ch.level >= 10 ? 1 : 0;
  const price = POTIONS[type].price[tier];
  if (ch.gold < price) { if (!quiet) toast("No te alcanza el oro"); return false; }
  const p = E.makePotion(type, tier);
  if (ch.belt.length < stats().beltSlots) ch.belt.push(p);
  else if (ch.inv.length < INV_SIZE) ch.inv.push(p);
  else { toast("No te cabe nada más"); return false; }
  ch.gold -= price;
  save(); renderHud(); renderPanels();
  if (!quiet) renderTown();
  return true;
}
function toAlembic(id) {
  if (S.alembic.length >= ALEM_SIZE) return;
  S.alembic.push(remove(id));
  save(); renderTown(); renderPanels();
}

// A course zone's four ways in, each with how far along it you are.
function modeButtons(z) {
  const zp = ch.zones[z.id] || {};
  return `<div class="modes">${z.modes.map((m) => {
    const n = z.fightsOf(m).length;
    const pack = m === modeOf(z.id) ? zp.pack || 0 : zp.byMode?.[m] || 0;
    const st = pack >= n - 1 ? "jefe" : `combate ${pack + 1} de ${n - 1}, luego el jefe`;
    return `<button data-zone="${z.id}" data-mode="${m}" class="mode${zp.done?.[m] ? " done" : ""}"><b>${zp.done?.[m] ? "✓ " : ""}${LEVEL_NAME[m]}</b><span>${MODE_DESC[m]}</span><span class="dim">${st}</span></button>`;
  }).join("")}</div>`;
}
// Map: zones unlock one after another.
// how far this episode is from a pet (Normal) and a horse (Difícil)
function companionProgressHtml() {
  if (!companionEpisode()) return "";
  const got = ch.companionEps?.[S.ep] || {};
  const part = (type, label) => {
    const C = COMPANION[type], p = epPerfect(C.diff), won = got[type];
    if (won) return `<div class="cprog done"><b>${label}</b> ${won === "all" ? "ganada (ya tenías todos: fue un objeto legendario)" : `ganada: <img class="${type}" src="${compImg(type, won)}" alt=""> ${esc(C.list[won].name)}`}</div>`;
    const bar = (k, name) => `<span class="cbar" title="${name}: ${p[k]} de ${p.n} frases perfectas"><i style="width:${(p[k] / p.n) * 100}%"></i></span><span class="dim">${name} ${p[k]}/${p.n}</span>`;
    return `<div class="cprog"><b>${label}</b> ${bar("cloze", "huecos")} ${bar("dict", "dictado")}</div>`;
  };
  return `<section class="companions-prog"><p class="dim small">Domina el episodio entero, todas sus frases al 100% con huecos y al dictado: en Normal ganas un ${PET_KIND} y en Difícil un caballo, de un color que aún no tengas.</p>
    ${part("pet", "Mascota (Normal o Difícil)")}${part("mount", "Montura (Difícil)")}</section>`;
}
// The Abismo on the map: one row per descent until the episode ends, each its own stretch, level and
// mastery, enterable once you've got that deep; past the end, one row for going on deeper.
function descentList(z, zp) {
  const n = descentsOf(z), deep = deepest(zp), cur = zp.depth || 0;
  const bar = (lines, k) => { const m = mastered(lines, k); return `<span class="dbar" title="${k === "dict" ? "Dictado" : "Huecos"}: ${m}/${lines.length} frases al 100%"><i style="width:${(m / lines.length) * 100}%"></i></span><span class="dcount">${k === "dict" ? "dictado" : "huecos"} ${m}/${lines.length}</span>`; };
  const row = (d, label, span) => {
    const lines = zoneLines(z, d), reach = d <= deep, here = d === cur;
    const prize = ["dict", "cloze"].map((k) => zoneRewardGot(z, d, k) ? "✓" : "").join("");
    return `<li class="descent${here ? " here" : ""}${reach ? "" : " far"}">
      <span class="dname"><b>${label}</b> <span class="dim">nivel ${atLevel(z).lvl[0] + d * 2}${span ? ` · ${span}` : ""}</span>${here ? ` <span class="dhere">${zp.pack >= z.packs ? (bossReady(z, d) ? "jefe" : `grupos extra: ${bossNeed(z, d)} para el jefe`) : `grupo ${zp.pack + 1}`}</span>` : ""}</span>
      <span class="dmast">${bar(lines, "dict")}${bar(lines, "cloze")}${prize ? `<span class="dprize" title="Premios recibidos: dictado y huecos al 100%">${prize}</span>` : ""}</span>
      ${reach ? `<button data-zone="${z.id}" data-depth="${d}" class="${here ? "primary" : ""}">${here ? "Seguir" : "Entrar"}</button>` : `<span class="dim small">Llega desde el descenso ${d}</span>`}</li>`;
  };
  const rows = [];
  for (let d = 0; d < n; d++) {
    const zl = zoneLines(z, d);
    rows.push(row(d, `Descenso ${d + 1}`, `${fmtTime(S.T.segments[zl[0]].start)}–${fmtTime(S.T.segments[zl[zl.length - 1]].end)}`));
  }
  if (deep >= n) rows.push(row(deep === cur ? cur : deep, `Descenso ${(deep === cur ? cur : deep) + 1}`, "el episodio vuelve a empezar"));
  return `<p class="dim small">${n} descensos hasta el final del episodio; cada uno es el tramo siguiente. Más hondo, el episodio vuelve a empezar, más duro.</p><ol class="descents">${rows.join("")}</ol>`;
}
function renderMap() {
  useEpisodeZones(); migrateModes(); identifyOld(); dropRunes(); necklacesToShirts(); attuneTunjo();
  // prizes for zones finished before there were prizes (or when the bag was full)
  if (S.T) for (const z of ZONES) zoneRewards(z);
  const unlocked = (i) => i === 0 || ch.zones[ZONES[i - 1].id]?.cleared;
  screen.innerHTML = `
    <section class="map">
      <div class="maphead"><div><h2>El camino</h2><p class="dim">${S.T.zones ? "Cada zona es un grupo de verbos. Elige cómo estudiarlo: el verbo, palabra por palabra, escribir el verbo o la frase entera. Cada forma tiene sus combates y su jefe, y puedes cambiar cuando quieras." : "Cada zona es siempre el mismo tramo del episodio: repítela hasta dominar todas sus frases."}${epShift() ? ` Cada episodio lleva su propio avance: este lo empezaste en el nivel ${epShift() + 1}, y sus zonas empiezan ahí.` : ""}</p></div><button id="toTown">Volver a la aldea</button></div>
      <div class="diffpick" role="radiogroup" aria-label="Dificultad">
        ${Object.entries(E.DIFFICULTY).map(([id, d]) => `<button role="radio" aria-checked="${(ch.difficulty || "medio") === id}" data-diff="${id}"><b>${d.name}</b><span>${esc(d.desc)}</span></button>`).join("")}
      </div>
      ${companionProgressHtml()}
      <section class="repaso" id="repaso"><p class="dim">Buscando tus mazos de Anki…</p></section>
      <section class="repaso encruc" id="encruc"></section>
      ${weakSpotsHtml()}
      <ol class="zones">
        ${ZONES.map((z, i) => {
          const zp = ch.zones[z.id] || { pack: 0 };
          const open = unlocked(i);
          const prog = z.endless ? `Descenso ${(zp.depth || 0) + 1} · ${zp.pack < z.packs ? `grupo ${zp.pack + 1}` : bossReady(z, zp.depth || 0) ? `te espera ${BOSSNAME(z)}` : `${BOSSNAME(z)} aparece cuando domines la mitad de las frases (${bossNeed(z, zp.depth || 0)})`}`
            : zp.cleared ? `Liberada. Puedes volver a por botín.`
            : zp.pack >= z.packs && !bossReady(z) ? `${BOSSNAME(z)} aparece cuando domines la mitad de las frases (${bossNeed(z)})`
            : zp.pack >= z.packs ? `Te espera ${BOSSNAME(z)}`
            : `Grupo ${zp.pack + 1} de ${z.packs}, luego ${BOSSNAME(z)}`;
          const zl = zoneLines(z, zp.depth || 0);
          const sc = open && sceneOf(z);
          return `<li class="${open ? "" : "locked"} ${zp.cleared ? "cleared" : ""} ${sc ? "hasscene" : ""}"${sc ? ` style="--scene:url('${new URL(`rpg/scenes/${sc}.png`, location.href).href}')"` : ""}>
            <div><b>${esc(z.name)}</b> <span class="dim">nivel ${atLevel(z).lvl[0]}${z.endless ? "+" : "–" + atLevel(z).lvl[1]}</span><p>${esc(z.blurb)}</p><span class="prog">${!open ? "Derrota al jefe anterior para llegar aquí" : z.modes ? (zp.cleared ? "Liberada. Elige una forma de estudiarla:" : "Elige una forma de estudiarla:") : prog}</span>
              ${z.endless && open ? descentList(z, zp) : (z.fights ? [["dict", "Dominio"]] : [["dict", "Dictado"], ["cloze", "Huecos"]]).map(([k, label]) => { const zm = mastered(zl, k); return `<div class="zmastery" title="${k === "cloze" ? "Frases que has completado al 100% con un arma a distancia (rellenando huecos), las dos veces: cada frase vuelve con otras palabras ocultas" : z.fights ? "Frases que has acertado al 100% al menos una vez" : "Frases que has escrito enteras al 100% con un arma cuerpo a cuerpo (dictado)"}"><span class="zbar"><i style="width:${(zm / zl.length) * 100}%"></i></span>${label}: ${zm}/${zl.length} frases <span class="zprize ${zoneRewardGot(z, zp.depth, k) ? "got" : ""}" title="Todas al 100%: ${k === "dict" ? "un objeto mítico" : "un objeto legendario o mítico"}, una vez">${zoneRewardGot(z, zp.depth, k) ? "premio recibido" : `premio: ${k === "dict" ? "mítico" : "legendario o mítico"}`}</span></div>`; }).join("")}${z.fights || (z.endless && open) ? "" : `<div class="zmastery">${fmtTime(S.T.segments[zl[0]].start)}–${fmtTime(S.T.segments[zl[zl.length - 1]].end)} del episodio</div>`}</div>
            ${open && !z.endless ? (z.modes ? modeButtons(z) : `<button data-zone="${z.id}" class="primary">Entrar</button>`) : ""}
          </li>`;
        }).join("")}
        ${remolinoCard()}
      </ol>
      ${S.T.zones ? "" : `<p class="restartep"><button id="restartEp">Empezar este episodio de nuevo</button> <span class="dim">Vuelve al Páramo con las zonas a tu nivel (${ch.level}), como la primera vez. Lo que has dominado y tus puntos débiles se quedan.</span></p>`}
    </section>`;
  $("#toTown").onclick = () => show("town");
  const re = $("#restartEp");
  if (re) re.onclick = () => {
    const d = dialog(`<h3>¿Empezar este episodio de nuevo?</h3><p>Las zonas vuelven a cerrarse y empiezan en tu nivel actual (${ch.level}): el Páramo será nivel ${ch.level}–${ch.level + 4}. Pierdes el avance por las zonas y los descensos de este episodio; las frases dominadas, los premios ya recibidos y tus puntos débiles se quedan.</p>
      <p class="row"><button class="primary" id="reYes">Empezar de nuevo</button> <button id="reNo">Cancelar</button></p>`);
    d.querySelector("#reNo").onclick = closeDialog;
    d.querySelector("#reYes").onclick = () => { restartEpisode(); closeDialog(); renderMap(); toast("El episodio empieza de nuevo a tu nivel"); };
  };
  screen.querySelectorAll("[data-zone]").forEach((b) => (b.onclick = () => enterZone(b.dataset.zone, b.dataset.mode, b.dataset.depth)));
  screen.querySelectorAll("[data-diff]").forEach((b) => (b.onclick = () => { ch.difficulty = b.dataset.diff; save(); renderMap(); }));
  if (!CFG.online) { renderRepasoEntry(); renderEncrucijadaEntry(); }
}

// ---------- Repaso: your due Anki cards as a fight ----------
// Spanish Listening cards are dictated like a line; the Tibetan ones are recalled and graded.
// Every answer goes straight to Anki (both cards of a note get it).
const EASE = { 1: "Otra vez", 2: "Difícil", 3: "Bien", 4: "Fácil" };
const EASE_EN = { 1: "Again", 2: "Hard", 3: "Good", 4: "Easy" };
const GRADE_ACC = { 1: 0, 2: 0.6, 3: 0.9, 4: 1 };
async function renderRepasoEntry() {
  const el = $("#repaso");
  if (!el) return;
  let decks;
  try { decks = await api("api/review/decks"); }
  catch (e) { el.innerHTML = `<div><b>La cripta del repaso</b><p class="dim">Abre Anki para repasar tus tarjetas aquí. (${esc(e.message)})</p></div>`; return; }
  if (!$("#repaso")) return;
  const chosen = new Set(ch.reviewDecks || decks.map((d) => d.id));
  // a deck added since you last chose starts ticked
  const seen = ch.reviewSeen || decks.map((d) => d.id);
  if (ch.reviewDecks) for (const d of decks) if (!seen.includes(d.id)) chosen.add(d.id);
  ch.reviewSeen = decks.map((d) => d.id); ch.reviewDecks = ch.reviewDecks && [...chosen];
  const total = () => decks.filter((d) => chosen.has(d.id)).reduce((a, d) => a + d.due, 0);
  el.innerHTML = `<div class="rhead"><div><b>La cripta del repaso</b> <span class="dim">tus tarjetas de Anki pendientes; cada respuesta se guarda en Anki</span></div>
      <button id="enterRepaso" class="primary"></button></div>
    <div class="rdecks">${decks.map((d) => `<label class="${d.due ? "" : "none"}"><input type="checkbox" data-deck="${d.id}" ${chosen.has(d.id) ? "checked" : ""}>
      ${esc(d.name)} ${ankiCounts(d.counts)} <span class="dim">${d.kind === "dictation" ? "dictado" : "recordar y puntuar"}</span></label>`).join("")}</div>
    <p class="dim small ankikey">${ankiCounts({ new: "Nuevas", learn: "Aprendiendo", review: "Para repasar" }, null, true)}</p>`;
  const btn = $("#enterRepaso");
  const sync = () => { const n = total(); btn.textContent = n ? "Entrar" : "Nada pendiente"; btn.disabled = !n; };
  el.querySelectorAll("[data-deck]").forEach((c) => (c.onchange = () => {
    c.checked ? chosen.add(c.dataset.deck) : chosen.delete(c.dataset.deck);
    ch.reviewDecks = [...chosen]; save(); sync();
  }));
  btn.onclick = () => enterRepaso([...chosen]);
  sync();
}
// Anki's three numbers, in Anki's colours: new, learning, to review. cur: the kind of the card in front of you.
function ankiCounts(n, cur = null, legend = false) {
  return `<span class="ankicounts${legend ? " legend" : ""}">${["new", "learn", "review"].map((k) =>
    `<span class="ac-${k}${cur === k ? " cur" : ""}" title="${{ new: "Nuevas", learn: "Aprendiendo", review: "Para repasar" }[k]}">${n?.[k] ?? 0}</span>`).join("")}</span>`;
}
// What's left of a deck in this session, counted in cards the way Anki counts them.
function sessionCounts(deck) {
  const R = S.review, F = S.F;
  const left = R.cards.slice(F?.checked ? R.i : Math.max(0, R.i - 1)).filter((c) => c.deck === deck);
  const out = { new: 0, learn: 0, review: 0 };
  for (const c of left) for (const k in out) out[k] += c.n?.[k] || 0;
  return out;
}
async function enterRepaso(deckIds) {
  const btn = $("#enterRepaso");
  if (btn) { btn.disabled = true; btn.textContent = "Cargando tarjetas…"; }
  let cards;
  try { cards = await api(`api/review/cards?decks=${deckIds.join(",")}`); }
  catch (e) { toast(e.message, "", 4000); return renderRepasoEntry(); }
  if (!cards.length) { toast("No hay tarjetas pendientes"); return renderRepasoEntry(); }
  for (const c of cards) if (c.kind === "dictation") c.words = c.text.split(/\s+/).filter(Boolean).map((w) => ({ w }));
  // as Anki does: learning cards first, then reviews, then new ones; the decks mixed within each
  for (let i = cards.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [cards[i], cards[j]] = [cards[j], cards[i]]; }
  const ORDER = { learn: 0, review: 1, new: 2 };
  cards.sort((a, b) => (ORDER[a.cat] ?? 1) - (ORDER[b.cat] ?? 1));
  S.review = { cards, i: 0, counts: { 1: 0, 2: 0, 3: 0, 4: 0 }, failed: 0, source: "anki" };
  cardFight("La cripta del repaso");
}
// A fight of cards (Anki's, or La encrucijada's sentences): monsters from the furthest zone you've
// reached, at your level.
function cardFight(name) {
  const reached = ZONES.filter((z, i) => !z.endless && (i === 0 || ch.zones[ZONES[i - 1].id]?.cleared));
  const home = reached[reached.length - 1] || ZONES[0];
  const lvl = Math.max(home.lvl[0], Math.min(ch.level, home.lvl[1]));
  // flat: it stays at this level however many cards you do (a long review shouldn't get deadlier)
  S.zone = { id: "repaso", name, review: true, lvl: [lvl, lvl], monsters: home.monsters, easy: EASY_ROSTER[home.id], boss: home.boss, packs: 9999, endless: true, flat: true };
  ch.zones.repaso = { pack: 0, cleared: false, depth: 0 };
  try { startEncounter(); }
  catch (e) { console.error(e); S.F = null; S.review = null; show("map"); toast(`No se pudo abrir el repaso: ${e.message}`, "", 5000); }
}
// La encrucijada never runs out: when its sentences are used up, another round of them is dealt
const cardsLeft = () => {
  const R = S.review;
  if (!R) return 0;
  if (R.source === "subj" && R.cards.length - R.i <= 0) R.cards.push(...subjSession(R.cats).map((x) => ({ ...x, kind: "subj", deck: "subj", deckName: SUBJ_CATS[x.cat] })));
  return R.cards.length - R.i;
};
async function answerCard(card, ease) {
  S.review.counts[ease]++;
  if (card.kind === "subj") return subjProgress(card, ease >= 3);
  let r;
  const R = S.review, req = api("api/review/answer", { method: "POST", body: { cards: card.cards, ease } });
  R.pending = req.catch(() => null);
  try { r = await req; }
  catch (e) { S.review.failed++; return toast(`Anki no guardó la respuesta: ${e.message}`, "", 5000); }
  // still in Anki's learning steps (Again, or a new card's first step): it comes back this session
  // when it's due, and the next answer moves it on (Good after Again: see it in a day)
  if (r?.again && S.review === R) R.cards.push({ ...card, cat: "learn", n: { new: 0, learn: r.again.n, review: 0 }, dueAt: r.again.due, back2: true, next: r.again.next || [] });
}
// While the last answer is on its way to Anki, hold off (a failed card may be coming back), then
// run fn once, however many times Enter was pressed. true: held off.
function afterAnswer(fn) {
  const R = S.review, F = S.F;
  if (!R?.pending) return false;
  if (!R.waiting) {
    R.waiting = true;
    R.pending.then(() => { R.pending = null; R.waiting = false; if (S.F === F && S.review === R) fn(); });
  }
  return true;
}
// The next card, as Anki picks it: a learning card that's come due first, then the rest in order;
// with nothing else left, learning cards still waiting are shown early (Anki's "learn ahead").
function pickCard() {
  const R = S.review, rest = R.cards.slice(R.i), now = Date.now();
  let k = rest.findIndex((c) => c.back2 && c.dueAt <= now);
  if (k < 0) k = rest.findIndex((c) => !c.back2);
  if (k < 0) k = rest.reduce((b, c, j) => (c.dueAt < rest[b].dueAt ? j : b), 0);
  const [c] = R.cards.splice(R.i + k, 1);
  R.cards.splice(R.i, 0, c);
  return R.cards[R.i++];
}
// Out of cards: whatever is left runs off, and you keep what's on the ground.
// Flash cards go on with no screen between groups: the gold goes straight into your purse and the next
// group comes, until the cards run out.
function reviewNextPack() {
  const F = S.F, gold = F.ground.gold;
  stopAll();
  ch.gold += gold;
  if (S.review) S.review.gold = (S.review.gold || 0) + gold;
  ch.zones.repaso.pack++;
  save();
  if (gold) sfx.coin();
  startEncounter();
  addLog(`Grupo derrotado${gold ? `: <b class="gold">+${gold} de oro</b>` : ""}. Llegan más.`, "good");
  renderHud(); renderPanels();
}
function repasoDone() {
  const F = S.F, R = S.review;
  stopAll();
  F.over = true;
  ch.gold += F.ground.gold;
  S.loot = { gold: F.ground.gold + (R.gold || 0), items: [] };
  save();
  const n = Object.values(R.counts).reduce((x, y) => x + y, 0);
  $("#arena").innerHTML = `
    <div class="victory">
      ${R.source === "subj" ? `<h3>Encrucijada superada</h3>
      <p>${n} ${n === 1 ? "frase" : "frases"}: ${R.counts[3] + R.counts[4]} con el modo bien${R.counts[2] ? `, ${R.counts[2]} a medias` : ""}${R.counts[1] ? `, ${R.counts[1]} con el modo mal` : ""}. <span class="dim">Las que fallaste vuelven primero la próxima vez.</span></p>` : `
      <h3>Repaso terminado</h3>
      <p>${n} ${n === 1 ? "nota" : "notas"}: ${[4, 3, 2, 1].filter((k) => R.counts[k]).map((k) => `${R.counts[k]} ${EASE[k].toLowerCase()}`).join(" · ")}.
        ${R.failed ? `<span class="bad">${R.failed} no se guardaron en Anki.</span>` : `<span class="dim">Todo guardado en Anki.</span>`}</p>`}
      ${alive(F).length ? `<p class="dim">Sin más ${R.source === "subj" ? "frases" : "tarjetas"}, los monstruos que quedaban huyen.</p>` : ""}
      ${S.loot.gold ? `<p class="gold">${icon("coins-pile", "#e2b84a")} +${S.loot.gold} de oro</p>` : ""}
      <div class="row"><button id="goMain" class="primary">Volver a la aldea</button></div>
    </div>`;
  if (S.loot.gold) sfx.coin();
  $("#goMain").onclick = () => { S.F = null; S.review = null; show("town"); };
  $("#goMain").focus();
}
function setupCardExercise() {
  const F = S.F, card = F.ex.card, st = stats(), C = E.costs(ch, st);
  $("#arena").innerHTML = `
    <div class="ex">
      <div class="excontrols">${card.audio ? `
        <button id="playBtn" class="playbtn" title="Escuchar (Tab)"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></button>
        <button id="slowBtn" title="Escuchar despacio (Mayús+Tab)">Despacio <span class="cost">${C.slow ? C.slow + " maná" : "gratis"}</span></button>` : ""}
        <span class="dim exinfo" id="exinfo"></span>
        <span class="deckname">${esc(card.deckName)}</span>
      </div>
      <div class="cardfront ${card.script === "latin" ? "latin" : "tib"}">${cleanHtml(card.front)}</div>
      <div class="cardback" id="cardBack" hidden>${cleanHtml(card.back)}${card.notes ? `<div class="cardnotes">${cleanHtml(card.notes)}</div>` : ""}</div>
      <div class="exactions">
        <button id="revealBtn" class="primary">Mostrar <kbd>Espacio</kbd></button>
        <div class="grades" id="grades" hidden>${[1, 2, 3, 4].map((k) => `<button data-ease="${k}" class="g${k}">${card.next?.[k - 1] ? `<span class="ivl">${esc(card.next[k - 1])}</span>` : ""}${EASE[k]} <kbd title="tecla">${k}</kbd></button>`).join("")}</div>
      </div>
      <div class="result" id="result" hidden></div>
    </div>`;
  if (card.audio) { $("#playBtn").onclick = () => doPlay(false); $("#slowBtn").onclick = () => doPlay(true); }
  $("#revealBtn").onclick = revealCard;
  document.querySelectorAll("#grades [data-ease]").forEach((b) => (b.onclick = () => gradeCard(+b.dataset.ease)));
  updateExInfo();
  focusInput();
}
function revealCard() {
  const F = S.F;
  if (!F || F.checked || F.revealed) return;
  F.revealed = true;
  $("#cardBack").hidden = false;
  $("#revealBtn").hidden = true;
  $("#grades").hidden = false;
  $("#grades [data-ease='3']").focus();
}
// Tibetan cards: your own grade is the attack. Otra vez misses, Fácil is a perfect hit.
function gradeCard(ease) {
  const F = S.F;
  if (!F || F.checked || !F.revealed) return;
  F.ease = ease;
  if (F.ex.card) answerCard(F.ex.card, ease);
  const acc = F.lesson ? LESSON_ACC[ease] : GRADE_ACC[ease];
  resolveAttack({ acc, html: "", typed: "", missed: 0 }, acc, ease === 4 && F.slows === 0);
}
// Anki's own HTML, keeping only harmless formatting (the blue highlight, bold, line breaks).
function cleanHtml(html) {
  const doc = new DOMParser().parseFromString(`<div>${html || ""}</div>`, "text/html");
  const ok = new Set(["DIV", "SPAN", "FONT", "B", "I", "U", "STRONG", "EM", "BR", "P", "UL", "OL", "LI", "HR", "SUB", "SUP"]);
  const walk = (el) => {
    for (const n of [...el.childNodes]) {
      if (n.nodeType === 3) continue;
      if (n.nodeType === 1 && n.tagName === "IMG") {
        // a figure from Anki's media folder, through the server
        const f = n.getAttribute("src") || "";
        const img = doc.createElement("img");
        if (/^[^/\\:]+\.(png|jpe?g|gif|webp)$/i.test(f)) { img.src = `api/review/media?file=${encodeURIComponent(f)}`; img.alt = ""; n.replaceWith(img); }
        else n.remove();
        continue;
      }
      if (n.nodeType !== 1 || !ok.has(n.tagName)) { n.replaceWith(...(n.nodeType === 1 && !["SCRIPT", "STYLE"].includes(n.tagName) ? n.childNodes : [])); continue; }
      const hi = (n.getAttribute("color") || n.getAttribute("style") || "").match(/blue|rgb\(0,\s*0,\s*255\)|#00f/i);
      for (const a of [...n.attributes]) n.removeAttribute(a.name);
      if (hi) n.className = "hl";
      walk(n);
    }
  };
  const root = doc.body.firstElementChild;
  walk(root);
  return root.innerHTML.replace(/\[sound:[^\]]+\]/g, "");
}
// ---------- La encrucijada: subjunctive or not ----------
// An English sentence; you write it in Spanish. The attack is whether the key verb is in the right
// mood (accents count: llegué is not llegue). The rest of your wording is yours: it isn't graded,
// you see one translation to compare, and Claude can review the whole sentence.
// Progress per sentence in ch.subj: the ones you got wrong come back first.
const MOOD = { s: "subjuntivo", i: "indicativo" };
function renderEncrucijadaEntry() {
  const el = $("#encruc");
  if (!el) return;
  const cats = new Set(ch.subjCats || Object.keys(SUBJ_CATS));
  const P = ch.subj || {};
  const seen = SUBJ.filter((x) => P[x.id]).length, missed = SUBJ.filter((x) => P[x.id] && !P[x.id].streak).length;
  el.innerHTML = `<div class="rhead"><div><b>La encrucijada</b> <span class="dim">una frase en inglés: escríbela en español, con subjuntivo o sin él</span></div>
      <button id="enterEncruc" class="primary">Entrar</button></div>
    <div class="rdecks">${Object.entries(SUBJ_CATS).map(([id, name]) => `<label><input type="checkbox" data-scat="${id}" ${cats.has(id) ? "checked" : ""}> ${esc(name)}
      <span class="dim">${SUBJ.filter((x) => x.cat === id).length}</span></label>`).join("")}</div>
    <p class="dim small ankikey">${SUBJ.length} frases · has visto ${seen}${missed ? ` · <span class="bad">${missed} por repetir</span>` : ""}</p>`;
  const btn = $("#enterEncruc");
  const sync = () => { btn.disabled = !cats.size; };
  el.querySelectorAll("[data-scat]").forEach((c) => (c.onchange = () => {
    c.checked ? cats.add(c.dataset.scat) : cats.delete(c.dataset.scat);
    ch.subjCats = [...cats]; save(); sync();
  }));
  btn.onclick = () => enterEncrucijada(cats);
  sync();
}
const shuffle = (a) => { for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
// 16 sentences: missed ones first, then ones you haven't seen, then the ones you know least well,
// with both moods in the mix.
function subjSession(cats, n = 16) {
  const P = ch.subj || {};
  const pri = (x) => { const p = P[x.id]; return !p ? 1 : !p.streak ? 0 : 1 + p.streak; };
  const pool = shuffle(SUBJ.filter((x) => cats.has(x.cat))).sort((a, b) => pri(a) - pri(b));
  const take = pool.slice(0, n);
  for (const mood of ["s", "i"]) {
    if (take.length > 3 && take.filter((x) => x.mood === mood).length < 4) {
      const extra = pool.slice(n).filter((x) => x.mood === mood).slice(0, 4);
      take.splice(take.length - extra.length, extra.length, ...extra);
    }
  }
  return shuffle(take);
}
function enterEncrucijada(cats) {
  const cards = subjSession(cats).map((x) => ({ ...x, kind: "subj", deck: "subj", deckName: SUBJ_CATS[x.cat] }));
  if (!cards.length) return toast("Elige al menos un tipo de frase");
  S.review = { cards, i: 0, counts: { 1: 0, 2: 0, 3: 0, 4: 0 }, failed: 0, source: "subj", cats: new Set(cats) };
  try { cardFight("La encrucijada"); }
  catch (e) { console.error(e); S.F = null; S.review = null; show("map"); toast(`No se pudo abrir la encrucijada: ${e.message}`, "", 5000); }
}
function subjProgress(card, right) {
  const P = (ch.subj = ch.subj || {});
  const p = (P[card.id] = P[card.id] || { n: 0, ok: 0, streak: 0 });
  p.n++;
  if (right) { p.ok++; p.streak++; } else p.streak = 0;
  p.last = Date.now();
  save();
}
const subjToks = (text) => text.split(/\s+/).filter(Boolean);
// The reference with its key verb as a gap: the hint (it doesn't say which mood).
function subjFrame(card) {
  return subjToks(card.es).map((t) => (card.ok.some((f) => accentKey(f) === accentKey(t)) ? `<span class="gap">______</span>` : esc(t))).join(" ");
}
// Find the key verb in what you wrote. The last match wins (the subordinate clause comes after
// the trigger: "Está claro que esté…" is the second verb). kind: ok, accent (right mood, missing
// accent), amb (only the accent tells the moods apart, and it's missing), bad, or none.
function gradeSubj(card, text) {
  let found = null;
  subjToks(text).forEach((t) => {
    const a = accentKey(t), n = norm(t);
    if (!n) return;
    const okE = card.ok.find((f) => accentKey(f) === a), badE = card.bad.find((f) => accentKey(f) === a);
    if (okE) return (found = { kind: "ok", form: okE, typed: t });
    if (badE) return (found = { kind: "bad", form: badE, typed: t });
    const okL = card.ok.find((f) => norm(f) === n), badL = card.bad.find((f) => norm(f) === n);
    if (okL && badL) found = { kind: "amb", form: okL, other: badL, typed: t };
    else if (okL) found = { kind: "accent", form: okL, typed: t };
    else if (badL) found = { kind: "bad", form: badL, typed: t };
  });
  const kind = found?.kind || "none";
  // the right form to show: the one in the same position as what you wrote (tú/usted…)
  const want = kind === "bad" ? card.ok[Math.min(card.bad.indexOf(found.form), card.ok.length - 1)] || card.ok[0] : found?.form || card.ok[0];
  const acc = { ok: 1, accent: 0.9, amb: 0.5, bad: 0, none: 0.35 }[kind];
  return { acc, kind, found, want, typed: text.trim(), html: "" };
}
function setupSubjExercise() {
  const F = S.F, card = F.ex.card, C = E.costs(ch, stats());
  $("#arena").innerHTML = `
    <div class="ex">
      <div class="excontrols">
        <button id="hintBtn" title="La frase en español con el verbo en blanco (Alt+H)">Pista <span class="cost">${C.hint} maná</span></button>
        <span class="dim exinfo" id="exinfo">Escríbela en español: ¿subjuntivo o indicativo?</span>
        <span class="deckname">${esc(card.deckName)}</span>
      </div>
      <p class="subjen">${esc(card.en)}</p>
      <div class="skeleton" id="skeleton" hidden></div>
      <textarea id="answer" rows="2" placeholder="Escribe la frase en español y pulsa Enter" autocomplete="off" autocapitalize="off" spellcheck="false"></textarea>
      <div class="exactions"><button id="attackBtn" class="primary">Atacar <kbd>Enter</kbd></button></div>
      <div class="result" id="result" hidden></div>
    </div>`;
  $("#hintBtn").onclick = () => hint();
  $("#attackBtn").onclick = attack;
  focusInput();
}
function attackSubj() {
  const F = S.F, card = F.ex.card, text = $("#answer").value;
  if (!text.trim()) return toast("Escribe la frase en español");
  const r = gradeSubj(card, text);
  F.subj = r;
  F.ease = { ok: F.hinted ? 3 : 4, accent: 3, amb: 2, bad: 1, none: 1 }[r.kind];
  answerCard(card, F.ease);
  resolveAttack(r, r.acc, r.kind === "ok" && !F.hinted);
}
// Your sentence with the key verb marked, the verdict and the rule, and one translation.
function subjVerdictHtml(card, r) {
  const mark = (text, form, cls) => subjToks(text).map((t) => (form && accentKey(t) === accentKey(form) ? `<span class="${cls}">${esc(t)}</span>` : esc(t))).join(" ");
  const f = r.found, m = MOOD[card.mood];
  const verdict = {
    ok: `<b class="good">Bien:</b> <b>${esc(f?.typed || "")}</b>, ${m}.`,
    accent: `<b class="good">Bien el modo</b>, pero la tilde: <b>${esc(r.want)}</b>, no ${esc(f?.typed || "")}.`,
    amb: `<b class="bad">Ojo con la tilde:</b> <b>${esc(r.want)}</b> (${m}) y <b>${esc(f?.other || "")}</b> (${MOOD[card.mood === "s" ? "i" : "s"]}) solo se distinguen por ella.`,
    bad: `<b class="bad">Escribiste <s>${esc(f?.typed || "")}</s></b> (${MOOD[card.mood === "s" ? "i" : "s"]}); hacía falta <b>${esc(r.want)}</b> (${m}).`,
    none: `<b class="bad">No encuentro el verbo clave</b> (aquí, <b>${esc(r.want)}</b>, ${m}). Si usaste otro verbo, compara con la traducción o pide la revisión.`,
  }[r.kind];
  return `<div class="subjres k-${r.kind}">
    <div class="you">Escribiste: <span class="typed">${f ? mark(r.typed, f.typed, r.kind === "ok" || r.kind === "accent" ? "kok" : "kbad") : esc(r.typed)}</span></div>
    <div class="verdict subjverdict"><span class="moodtag m-${card.mood}">${m}</span> ${verdict}</div>
    <p class="why">${esc(card.why)}</p>
    <div class="ref"><span class="dim">Una traducción:</span> ${mark(card.es, card.ok.find((o) => subjToks(card.es).some((t) => accentKey(t) === accentKey(o))), "kok")}</div>
  </div>`;
}
function showSubjResult(r) {
  const F = S.F, card = F.ex.card, res = $("#result");
  res.innerHTML = `${subjVerdictHtml(card, r)}
    <div class="row">
      <button id="reviewBtn" title="Claude revisa tu frase entera: el modo, y si es correcta y natural">Que lo revise Claude</button>
      <button id="nextBtn" class="primary">${!cardsLeft() ? "Terminar" : alive(F).length ? "Siguiente frase" : "Siguiente grupo"} <kbd>Enter</kbd></button>
    </div>
    <div class="explain" id="explainOut" hidden></div>`;
  res.hidden = false;
  $("#attackBtn").hidden = true;
  $("#hintBtn").disabled = true;
  $("#answer").disabled = true;
  $("#nextBtn").onclick = afterResult;
  $("#reviewBtn").onclick = async () => {
    const b = $("#reviewBtn"), out = $("#explainOut");
    b.disabled = true; b.textContent = "Claude está leyendo…";
    try {
      const { review } = await api("api/subj/review", { method: "POST", body: { en: card.en, es: card.es, typed: r.typed, mood: card.mood } });
      if (S.F !== F || F.ex.card !== card) return;
      out.innerHTML = md(review); out.hidden = false; b.textContent = "Revisado";
    } catch (e) { b.disabled = false; b.textContent = "Que lo revise Claude"; toast(e.message, "", 4000); }
    $("#nextBtn")?.focus();
  };
  renderGroupMastery();
  $("#nextBtn").focus();
}

const BOSSNAME = (z) => BOSSES[z.boss].name;
const fmtTime = (t) => `${Math.floor(t / 60)}:${String(Math.floor(t % 60)).padStart(2, "0")}`;

// ---------- fighting ----------
const alive = (F) => F.monsters.filter((m) => m.hp > 0);
function enterZone(id, mode, depth) {
  useEpisodeZones();
  ch.zones[id] = ch.zones[id] || { pack: 0, cleared: false, depth: 0 };
  if (depth != null) {
    const zp = ch.zones[id], d = Math.min(+depth, deepest(zp));
    if (d !== (zp.depth || 0)) { zp.maxDepth = deepest(zp); zp.depth = d; zp.pack = 0; }
  }
  migrateModes();
  if (mode) setMode(id, mode);
  if (id === REMOLINO) {
    if (!episodeDone()) return toast("El Remolino se abre cuando domines todo el episodio");
    const zp = ch.zones[REMOLINO];
    if (!zp.lines || !zp.pack) buildRemolino(zp);
    save();
  }
  S.zone = id === REMOLINO ? remolinoZone() : E.zoneById(id);
  startEncounter();
}
// load the speech recogniser in the background, so the first spell doesn't wait for it
let warmed = false;
function warmVoice() { if (!warmed && voiceOk()) { warmed = true; fetch("api/shadow/warm", { method: "POST" }).catch(() => {}); } }
function startEncounter() {
  endCelebration();
  warmVoice();
  const zp = ch.zones[S.zone.id], z = S.zone;
  // past the last group, a gated zone's boss only comes once you've mastered half its lines
  const late = zp.pack >= z.packs, held = late && gated(z) && !bossReady(z, zp.depth || 0);
  const slot = { boss: late && !held, group: held ? extraGroup(z, zp) : null };
  const enc = E.makeEncounter(atLevel(z), held ? z.packs - 1 : zp.pack, zp.depth || 0, E.diffOf(ch));
  const queue = S.zone.review ? [] : buildQueue(slot);
  S.F = { enc, monsters: enc.monsters, target: 0, combo: Math.max(stats().comboStart, ch.streak || 0), ear: ch.earStreak || 0, log: [], si: null, ground: { gold: 0, items: [] }, queue, qi: 0, review: !!S.zone.review };
  if (held) S.F.extra = true;
  if (enc.boss) S.F.boss = { charge: 0, armed: false, p2: false, stolen: [], deal: null, burn: 0, tangle: 0 };
  S.loot = null;
  const foe = S.zone.review ? leechFoe(enc) : weakFoe(enc, queue);
  if (foe) enc.monsters.unshift(foe);
  show("fight");
  if (enc.intro) addLog(enc.intro, "intro");
  if (foe) addLog(foe.lore, "weak");
  if ((ch.streak || 0) >= 2 && !S.F.review) addLog(`Sigues con tu racha de <b>${ch.streak}</b> (×${(1 + 0.1 * Math.min(ch.streak, 10)).toFixed(1)}).`, "good");
  if (held) addLog(`${esc(BOSSES[z.boss].name)} no aparece hasta que domines la mitad de las frases de esta zona (llevas ${bossNeed(z, zp.depth || 0)}). Otro grupo, con las frases que menos dominas.`, "intro");
  if (enc.boss && gated(z)) addLog(`<b>${esc(BOSSES[z.boss].name)}</b> trae ${queue.fresh === 1 ? "1 frase nueva" : `${queue.fresh} frases nuevas`} y ${queue.misses === 1 ? "1 de las que más te cuestan" : `${queue.misses} de las que más te cuestan`}. Y lo que falles aquí te lo devuelve enseguida.`, "intro");
  else if (queue.misses) addLog(`<b>${esc(BOSSES[S.zone.boss].name)}</b> conoce tus fallos: trae ${queue.misses} ${queue.misses === 1 ? "frase que aún no dominas" : "frases que aún no dominas"}. Y lo que falles aquí te lo devuelve enseguida.`, "intro");
  const boss = bossOf(S.F);
  if (boss && hasBossArt(boss.kind)) {
    if (bossRules(S.F)) addLog(`<b>${esc(BOSSES[boss.kind].special.name)}</b>: lo verás venir en su barra. Cuando se llene, <b>solo una frase perfecta</b> lo esquiva. A la mitad de su vida, cambia.`, "boss");
    const F = S.F;
    bossIntro($(".stage"), boss.kind, () => sfx.bossIntro(boss.kind)).then(() => { if (S.F === F) nextExercise(); });
  } else nextExercise();
}

// ---------- bosses ----------
// Each boss has its own art, an entrance, a signature attack it charges where you can see it (only a perfect
// line gets you out of the way) and a second phase from half its life (data.js BOSSES). The signature
// attacks and phases belong to the zones' bosses: not in a course or a review.
const bossOf = (F) => F?.monsters?.find((m) => m.tier === "boss" && m.kind in BOSSES) || null;
const bossRules = (F) => !!(F?.boss && !F.review && !S.zone?.fights);
const isEasy = () => (ch.difficulty || "medio") === "facil";
// the signature attack: one turn sooner than its card says (never more often than every 2 turns), except on Fácil
const bossEvery = (F, m) => { const n = (F.boss.p2 && BOSSES[m.kind].p2.every) || BOSSES[m.kind].special.every; return isEasy() ? n : Math.max(2, n - 1); };
const PRICE = 0.15; // the Mandingas's deal: what each line short of perfect costs, of your life
// Its turn: let go of the signature attack if it was ready (it hits instead of its normal blow), or charge it.
function bossTurn(F, m, acc, st, D, unleash, wasFrozen) {
  const B = F.boss, def = BOSSES[m.kind], sp = def.special, ev = { kind: m.kind };
  if (unleash) {
    B.armed = false; B.charge = 0;
    if (acc >= (isEasy() ? D.safeAcc : 1)) { ev.dodged = true; addLog(`<b>${esc(sp.name)}</b>: ${sp.dodge}`, "good"); return ev; }
    const a = E.heavyBlow(st, m, acc, sp.mult * (isEasy() ? 0.6 : 1), D);
    ev.hit = a;
    let what = sp.hit;
    if (sp.steal) {
      const p = ch.belt.length ? ch.belt.pop() : null;
      const gold = p ? 0 : Math.min(ch.gold, Math.round(ch.gold * 0.1 + 5 * m.lvl));
      if (p) { B.stolen.push({ item: p }); what += ` y se lleva tu <b>${esc(POTIONS[p.potion]?.name?.toLowerCase() || "poción")}</b>. La recuperas si lo vences`; }
      else if (gold > 0) { ch.gold -= gold; B.stolen.push({ gold }); what += ` y se lleva <b>${gold}</b> de oro. Lo recuperas si lo vences`; }
    }
    if (sp.tangle) { B.tangle = sp.tangle + 1; m.hp = Math.min(m.maxHp, m.hp + Math.round(m.maxHp * sp.heal)); }
    if (sp.burn) B.burn = sp.burn;
    addLog(`<b>${esc(sp.name)}</b>: ${what.replace(/\.$/, "")} <b class="taken">(−${a.dmg})</b>.`, "bad");
    return ev;
  }
  if (wasFrozen) return ev;
  const every = bossEvery(F, m);
  B.charge = Math.min(every, B.charge + ((B.p2 && def.p2.step) || 1));
  ev.charged = B.charge;
  if (B.charge >= every) { B.armed = true; ev.ready = true; addLog(sp.ready, "boss"); }
  return ev;
}
// At half its life it changes, once: faster, or with help, or with an offer.
function bossPhase2(F, m) {
  const B = F.boss, def = BOSSES[m.kind], p2 = def.p2;
  B.p2 = true;
  addLog(`<b>${esc(def.name)}</b>: ${p2.text}`, "boss");
  if (p2.summon && !isEasy()) { const [kind, n] = p2.summon; for (let i = 0; i < n; i++) F.monsters.push(E.makeFoe(kind, F.enc.lvl, "minion", {}, E.diffOf(ch))); }
  if (p2.dmg) m.dmg *= p2.dmg;
  if (p2.deal) B.dealPending = true;
}
// The Mandingas's offer: everything back now, and twice the loot, for a price on every line short of perfect.
function offerDeal(F) {
  const m = bossOf(F), B = F.boss;
  if (!m || m.hp <= 0 || S.F !== F || !B.dealPending) return;
  B.dealPending = false;
  let chosen = false;
  const stage = () => $(".stage");
  const choose = (yes) => {
    if (chosen) return;
    chosen = true;
    const st = stats();
    if (yes) {
      B.deal = "signed";
      ch.life = st.maxLife; ch.mana = st.maxMana;
      addLog(`Firmas. <b>Vida y maná al máximo</b>, y si lo vences, el doble de botín. Pero cada frase que no sea perfecta te cuesta un ${PRICE * 100}% de tu vida.`, "boss");
      bossShout(stage(), "Trato hecho", "deal", BOSSES.mandingas.color);
    } else {
      B.deal = "refused";
      m.dmg *= 1.2;
      addLog("«Usted se lo pierde». El Mandingas se enfurece: <b>pega un 20% más fuerte</b>.", "boss");
      bossShout(stage(), "«Usted se lo pierde»", "deal", BOSSES.mandingas.color);
    }
    sfx.bossIntro("mandingas");
    save(); renderHud(); renderFoes(); renderBossWarn();
  };
  addLog(`<b>El Mandingas</b>: «Hagamos un trato. Le devuelvo toda la vida y todo el maná, ahora mismo. Y si me gana, le doy el doble de botín. A cambio, cada frase que no escriba perfecta, me la cobro: un ${PRICE * 100}% de su vida.»`, "boss");
  const d = dialog(`<div class="deal" style="--bc:${BOSSES.mandingas.color}">
      <p class="deal-kicker">El Mandingas</p>
      <h3>«Hagamos un trato»</h3>
      <p>«Le devuelvo toda la vida y todo el maná, ahora mismo. Y si me gana, le doy el <b>doble de botín</b>.»</p>
      <p>«A cambio, cada frase que no escriba perfecta, me la cobro: <b>un ${PRICE * 100}% de su vida</b>.»</p>
      <div class="row"><button class="primary" id="dealYes">Firmar</button><button id="dealNo">No firmar</button></div>
    </div>`, { cls: "dealbox", onClose: () => choose(false) });
  d.querySelector("#dealYes").onclick = () => { choose(true); closeDialog(); };
  d.querySelector("#dealNo").onclick = () => { choose(false); closeDialog(); };
  setTimeout(() => d.querySelector("#dealNo")?.focus(), 50);
}
// What it took comes back when it falls.
function giveBack(x) {
  if (x.gold) ch.gold += x.gold;
  else if (x.item) (ch.belt.length < stats().beltSlots ? ch.belt : ch.inv).push(x.item);
}
function bossFalls(F, m) {
  const B = F.boss, def = BOSSES[m.kind];
  addLog(`<i>${esc(def.last)}</i>`, "boss");
  if (B.stolen.length) {
    B.stolen.forEach(giveBack);
    const gold = B.stolen.reduce((a, x) => a + (x.gold || 0), 0), pots = B.stolen.filter((x) => x.item).length;
    addLog(`Recuperas ${[pots ? `${pots} ${pots === 1 ? "poción" : "pociones"}` : "", gold ? `${gold} de oro` : ""].filter(Boolean).join(" y ")}.`, "good");
    B.stolen = [];
  }
  B.armed = false; B.burn = 0; B.tangle = 0;
}
// Over the line you're answering: what the boss has ready for it, and what it has done to you.
function renderBossWarn() {
  const F = S.F, ex = $("#arena .ex");
  if (!ex) return;
  ex.querySelector(".bosswarns")?.remove();
  const m = bossOf(F);
  if (!bossRules(F) || !m || m.hp <= 0) return;
  const B = F.boss, sp = BOSSES[m.kind].special, out = [];
  if (B.armed) out.push(`<div class="bosswarn armed"><b>${esc(sp.name)}</b> ${sp.wail && !isEasy() ? "Su llanto suena encima de esta frase." : "Viene con esta frase."} ${isEasy() ? "Entiéndela bien" : "Solo una frase <b>perfecta</b>"} para esquivarlo.</div>`);
  if (B.tangle > 0) out.push(`<div class="bosswarn tangle">Enredado: sin Despacio ni Pista${B.tangle > 1 ? " en esta frase y la siguiente" : " en esta frase"}.</div>`);
  if (B.burn > 0) out.push(`<div class="bosswarn burn">Ardes: una frase perfecta apaga el fuego.</div>`);
  if (B.deal === "signed") out.push(`<div class="bosswarn deal">El trato: si no es perfecta, te cuesta un ${PRICE * 100}% de tu vida.</div>`);
  if (out.length) ex.prepend(h(`<div class="bosswarns" style="--bc:${BOSSES[m.kind].color}">${out.join("")}</div>`));
}

// ---------- weak spots: the words you keep missing come back as monsters ----------
// Every word you get wrong is written down (per episode); getting it right later pays the debt off.
// A word missed often enough, and not yet made up for, can turn up in a fight, and its line comes first.
// The worst ones (leeches) are named uniques. Writing its word right hits it twice as hard.
const EPITHETS = ["el Inquebrantable", "el Escurridizo", "el Que Siempre Vuelve", "el Terco", "el Sordo", "el Eterno", "el Implacable",
  "el Huidizo", "el Tozudo", "el Susurrante", "el Olvidadizo", "el Atravesado", "el Mal Oído", "el Tramposo"];
const weakBook = () => ((ch.weak = ch.weak || {})[S.ep] = ch.weak[S.ep] || {});
const weakScore = (e) => e.miss - e.hit / 2;
const isWeak = (e) => e.miss >= 2 && weakScore(e) >= 1.5;
const isLeech = (e) => e.miss >= 5 && weakScore(e) >= 3;
const capWord = (w) => w.charAt(0).toUpperCase() + w.slice(1);
const bare = (w) => w.replace(/[^\p{L}'’-]/gu, "");
// Filling gaps: how fresh the right answers were. A word you've got right in a gap before counts as
// known a fifth more each time (fully from the 5th), across episodes; a miss counts as fresh.
// Returns the multiplier on the odds of rare and better loot from this attack's kills: 1 down to
// 0.15 when every gap was a word you know cold. Then counts this answer's right words.
function gapFreshness(r) {
  const K = (ch.gapKnown ||= {}), per = (r.words || []).filter((x) => !isSound(x.w));
  if (!per.length) { S.F.gapStale = null; return 1; }
  let stale = 0; const known = [];
  for (const x of per) {
    const k = norm(x.w), n = K[k] || 0;
    if (x.ok && n) { stale += Math.min(1, n / 5); if (n >= 2) known.push(bare(x.w).toLowerCase()); }
  }
  for (const x of per) if (x.ok) { const k = norm(x.w); K[k] = (K[k] || 0) + 1; }
  const mult = Math.max(0.15, 1 - 0.85 * (stale / per.length));
  S.F.gapStale = mult < 0.95 ? { mult, words: known } : null;
  return mult;
}
function trackWords(r) {
  const F = S.F;
  if (F.review || !r.words) return;
  const W = weakBook();
  for (const x of r.words) {
    const k = norm(x.w);
    if (k.length < 2 || isSound(x.w)) continue;
    if (x.ok) { if (W[k]) W[k].hit++; continue; }
    const e = (W[k] = W[k] || { w: bare(x.w).toLowerCase(), miss: 0, hit: 0, si: [] });
    e.miss++;
    if (!e.si.includes(F.si)) e.si = [...e.si, F.si].slice(-6);
  }
  // how much each line has cost you: the tunjos' unique clips are cut from the worst stretch
  const L = ((ch.struggle = ch.struggle || {})[S.ep] = ch.struggle[S.ep] || {});
  if (r.acc < 1) L[F.si] = Math.round(((L[F.si] || 0) + 1 - r.acc) * 100) / 100;
  else if (S.zone?.dynamic && L[F.si]) L[F.si] = Math.round(L[F.si] * 50) / 100;
}
function weakList(ep = S.ep) {
  const W = ch.weak?.[ep] || {};
  return Object.entries(W).filter(([k, e]) => isWeak(e) && !isSound(k)).map(([k, e]) => ({ k, ...e, score: weakScore(e), leech: isLeech(e) })).sort((a, b) => b.score - a.score);
}
function weakFoe(enc, queue) {
  if (enc.boss || S.zone.fights) return null;
  const ok = (si) => S.T.segments[si] && !S.T.segments[si].flagged && S.lines.includes(si);
  const cand = weakList().filter((x) => x.si.some(ok));
  if (!cand.length || Math.random() > 0.55) return null;
  const tot = cand.reduce((a, x) => a + x.score, 0);
  let r = Math.random() * tot, w = cand[0];
  for (const x of cand) { r -= x.score; if (r <= 0) { w = x; break; } }
  const D = E.diffOf(ch), lvl = enc.lvl;
  const kind = enc.monsters[0].kind in BOSSES ? "espanto" : enc.monsters[0].kind;
  const name = w.leech ? `${capWord(w.w)} ${EPITHETS[hash(w.k.length * 7919 + [...w.k].reduce((a, c) => a + c.charCodeAt(0), 0)) % EPITHETS.length]}` : capWord(w.w);
  const m = E.makeFoe(kind, lvl + (w.leech ? 1 : 0), w.leech ? "unique" : "champion", { name, mods: w.leech ? ["fuerte"] : [] }, D);
  m.weak = w.k; m.word = w.w;
  // its name would give the word away: it stays masked until you've answered its line
  m.mask = w.leech ? `Punto débil ${name.slice(capWord(w.w).length + 1)}` : "Punto débil";
  m.lore = `${w.leech ? "Tu peor punto débil" : "Un punto débil"} vuelve: una palabra de la primera frase que has fallado ${w.miss} ${w.miss === 1 ? "vez" : "veces"}${w.hit ? ` y acertado ${w.hit}` : ""}. Escríbela bien y le das el doble.`;
  // its line (or the chunk of it with the word) goes to the front of the queue
  const si = w.si.filter(ok).at(-1);
  const exs = chunks(si, D.maxWords);
  const ex = exs.find((e) => S.T.segments[si].words.slice(e.a, e.b).some((x) => norm(x.w) === w.k)) || exs[0];
  queue.unshift(ex);
  return m;
}
// In the crypt: a card you've forgotten again and again (4+ lapses) shows up as a named unique.
function leechFoe(enc) {
  const R = S.review;
  if (!R) return null;
  const c = R.cards.slice(R.i).find((x) => x.lapses >= 4 && !x.leechShown && !x.back2);
  if (!c) return null;
  c.leechShown = true;
  // bring that card to the front of what's left
  R.cards.splice(R.cards.indexOf(c), 1);
  R.cards.splice(R.i, 0, c);
  const label = (c.kind === "recall" ? cleanHtml(c.front).replace(/<[^>]+>/g, "") : c.text.split(/\s+/).slice(0, 3).join(" ")).trim().slice(0, 28);
  const m = E.makeFoe(enc.monsters[0].kind, enc.lvl + 1, "unique", { name: `${label} ${EPITHETS[c.note % EPITHETS.length]}`, mods: ["fuerte"] }, E.diffOf(ch));
  m.leechCard = c.note;
  if (c.kind === "dictation") m.mask = `Sanguijuela ${EPITHETS[c.note % EPITHETS.length]}`; // its words are the answer
  m.lore = `Una sanguijuela de Anki: has olvidado esta tarjeta ${c.lapses} veces. Va primero.`;
  return m;
}
function addLog(text, cls = "") {
  S.F.log.unshift({ text, cls });
  S.F.log = S.F.log.slice(0, 12);
  const el = $("#log");
  if (el) el.innerHTML = S.F.log.map((l) => `<li class="${l.cls}">${l.text}</li>`).join("");
}

function renderFight() {
  const F = S.F, zp = ch.zones[S.zone.id];
  screen.innerHTML = `
    <section class="fight">
      <div class="fighthead">
        <div><b>${esc(S.zone.name)}</b> <span class="dim">${F.review ? `${S.review?.source === "subj" ? "Subjuntivo o no" : "Repaso de Anki"} · grupo ${zp.pack + 1}` : S.zone.fights ? `${LEVEL_NAME[courseFight(S.zone, zp.pack).mode]}${F.enc.boss ? " · jefe" : ` · combate ${zp.pack + 1} de ${S.zone.packs}`}` : F.enc.boss ? "Jefe" : F.extra ? `${S.zone.endless ? `Descenso ${(zp.depth || 0) + 1} · ` : ""}grupo extra · ${bossNeed(S.zone, zp.depth || 0)} frases para el jefe` : S.zone.endless ? `Descenso ${(zp.depth || 0) + 1} · grupo ${zp.pack + 1}` : `Grupo ${zp.pack + 1} de ${S.zone.packs}`} · nivel ${F.enc.lvl} · ${E.diffOf(ch).name}</span>
          <div class="dim small" id="groupMastery"></div></div>
        <div class="combo" id="combo"></div>
        <button id="portal" class="ghost" title="${F.review ? "Vuelves a la aldea con el oro que llevas ganado." : "Vuelves a la aldea. El grupo actual se reinicia."}">Volver a la aldea</button>
      </div>
      <div class="stage${sceneOf(S.zone) ? ` scene scene-${sceneOf(S.zone)}` : ""}${bossOf(F) && hasBossArt(bossOf(F).kind) ? ` bossfight bf-${bossOf(F).kind}` : ""}">
        ${sceneOf(S.zone) ? sceneFx(sceneOf(S.zone)) : ""}
        <div class="bossbar" id="bossbar" hidden></div>
        <div class="me" id="me"></div>
        <div class="foes" id="foes"></div>
      </div>
      <div class="arena" id="arena"></div>
      <details class="logbox" id="logbox"${localStorage.getItem("rpgLogOpen") === "1" ? " open" : ""}><summary>Registro del combate</summary><ul class="log" id="log"></ul></details>
    </section>`;
  // the log is folded away unless you open it (remembered on this device)
  $("#logbox").ontoggle = (e) => localStorage.setItem("rpgLogOpen", e.target.open ? "1" : "0");
  // a card fight has no end of its own (La encrucijada) or none you must reach: leaving keeps the gold of
  // what you've already beaten in this group
  $("#portal").onclick = () => { stopAll(); if (F.review && !F.over) { ch.gold += F.ground.gold; F.ground.gold = 0; S.review = null; save(); } S.F = null; show("town"); };
  renderMe(); renderFoes(); renderCombo(); addLog("", "");
  S.F.log = S.F.log.filter((l) => l.text);
  $("#log").innerHTML = S.F.log.map((l) => `<li class="${l.cls}">${l.text}</li>`).join("");
}
function renderGroupMastery() {
  const F = S.F, el = $("#groupMastery");
  if (!el || !F) return;
  if (F.review && S.review.source === "subj") {
    const R = S.review, done = R.i - (F.checked ? 0 : 1), good = R.counts[3] + R.counts[4];
    el.innerHTML = `<b class="ankideck">${esc(F.ex?.card?.deckName || "")}</b> · frase ${R.i} · ${good}/${done} con el modo bien`;
    return;
  }
  if (F.review) {
    const R = S.review, done = R.i - (F.checked ? 0 : 1), c = F.ex?.card;
    el.innerHTML = `${c ? `<b class="ankideck">${esc(c.deckName)}</b> ${ankiCounts(sessionCounts(c.deck), F.checked ? null : c.cat)} · ` : ""}nota ${Math.min(R.i, R.cards.length)} de ${R.cards.length} · ${done} respondidas`;
    return;
  }
  // an exercise counts as done if you got it 100%, or its whole line is mastered some other way
  // (whole, or in other-sized chunks from another difficulty)
  const done = (e) => exMastered(e) || lineMastered(e.si);
  const n = F.queue.length, m = F.queue.filter(done).length;
  const lines = new Set(F.queue.map((e) => e.si)).size;
  const M = mastery();
  const twice = F.queue.some((e) => e.v);
  el.innerHTML = `${lines} ${lines === 1 ? "frase" : "frases"}${twice ? `, dos veces con otros huecos: ${n} ejercicios` : n > lines ? ` en ${n} trozos` : ""} · dominad${n > lines ? "os" : "as"}${S.T.zones ? "" : scoreKind() === "cloze" ? " con huecos" : " al dictado"} ${m}/${n} ` +
    F.queue.map((e) => `<i class="pip ${done(e) ? "on" : M[exKey(e)] != null ? "seen" : ""} ${e === F.ex ? "cur" : ""}" data-pip="${done(e) ? "Dominada" : M[exKey(e)] != null ? `Tu mejor: ${Math.round(M[exKey(e)] * 100)}%` : "Aún no la has oído"}${e.v ? " (segunda vez, otros huecos)" : ""}${e.back ? " · traída por el jefe" : ""}"></i>`).join("");
}
function renderMe() {
  const el = $("#me");
  if (!el) return;
  // the moving figure when the animation sheets are there, the still one otherwise
  S.fig = fightFigure(ch);
  el.innerHTML = `${S.fig ? "" : figureSvg(ch, { cls: "small" })}<span class="mename">${esc(ch.name)}</span>`;
  if (S.fig) {
    el.prepend(withCompanions(S.fig));
  }
}
// The hero's canvas with the horse behind and the dog at the feet. "fight": the wide fight canvas;
// "doll": the centred one of the inventory and the character panel (sized to its box).
function withCompanions(fig, kind = "fight") {
  // riding: the horse is in the figure's own canvas
  const wrap = h(`<div class="figwrap ${kind}${fig.riding ? " riding" : ""}" style="--vw:${fig.vw}">${companionsHtml(!!fig.riding)}</div>`);
  wrap.append(fig.el);
  // drawn at the hero's scale: their own pixel width × --px
  wrap.querySelectorAll("img.comp").forEach((img) => { const set = () => img.style.setProperty("--w", img.naturalWidth); if (img.complete) set(); else img.onload = set; });
  return wrap;
}
function companionsHtml(riding = false) {
  const out = [];
  if (!riding && MOUNTS[ch.mount] && ch.mounts?.includes(ch.mount)) out.push(`<img class="comp mount" src="${compImg("mount", ch.mount)}" alt="" title="${esc(MOUNTS[ch.mount].name)}">`);
  if (PETS[ch.pet] && ch.pets?.includes(ch.pet)) out.push(`<img class="comp pet" src="${compImg("pet", ch.pet)}" alt="" title="${esc(PETS[ch.pet].name)}">`);
  return out.join("");
}
const REGAIN = 3; // perfect lines in a row that bring a broken streak back
const REGAIN_FROM = 10; // only a streak at least this long can be got back
// ---------- the streak dice (E.streakRoll) ----------
// Rolled when the line is answered; the prize goes straight to you (gold to your purse, the thing to your
// bag, or the stash, or the ground); the dice play out over the stage a moment later.
// Two streaks roll their own dice: the streak (perfect lines) and the ear streak (perfect lines heard only once).
const DICE_KIND = { racha: { name: "Dados de la racha", n: (F) => F.combo }, oido: { name: "Dados de oído", n: (F) => F.ear } };
function streakDice(F, kind = "racha") {
  const K = DICE_KIND[kind];
  const r = E.streakRoll(K.n(F), F.enc?.lvl || ch.level, stats(), E.diffOf(ch), isEasy());
  if (!r) return null;
  r.kind2 = kind;
  ch.stats.diceRolls = (ch.stats.diceRolls || 0) + 1;
  if (!r.win) return addLog(`${dieIco(kind)} ${K.name}: sale <b>${r.roll}</b>; ganabas con ${r.need === 1 ? "un 1" : `1 a ${r.need}`} (${r.need}% de probabilidad). Sin premio.`, "dice"), r;
  ch.stats.diceWins = (ch.stats.diceWins || 0) + 1;
  let where = "";
  if (r.gold) ch.gold += r.gold;
  else {
    if (!r.item.kind && UNID.has(r.item.rarity)) r.item.unid = true;
    where = stow(r.item) || (F.ground.items.push(r.item), "al suelo");
    logDrops([r.item], { tier: "racha", lvl: F.enc?.lvl || ch.level });
  }
  r.where = where;
  const what = r.gold ? `<b>${r.gold} de oro</b>` : `<b style="color:${E.itemColor(r.item)}">${esc(r.item.unid ? `${RARITY[r.item.rarity]?.name || ""} sin identificar` : E.itemName(r.item))}</b>`;
  addLog(`${dieIco(kind)} <b>¡${K.name}!</b> Sale ${r.roll}, y ganabas con ${r.need === 1 ? "un 1" : `1 a ${r.need}`}. Dado de premio: ${r.face}${r.bonus ? ` + ${r.bonus}` : ""} = <b>${r.total}</b>: ${what}${where ? ` <span class="dim">(va ${where})</span>` : ""}.`, "good");
  save();
  return r;
}
// coins and sparks raining over a whole-screen layer (the dice and the victory celebration)
function coinRain(layer, color, n, delay = 0.8) {
  if (FX.reduced()) return;
  for (let i = 0; i < n; i++) {
    const c = h(`<i class="dice-rain${i % 3 ? "" : " spark"}"></i>`), t = 1.2 + Math.random() * 1.2;
    c.style.cssText = `left:${Math.random() * 100}%;--dx:${Math.random() * 120 - 60}px;--r:${Math.random() * 900 - 450}deg;--c:${color};--t:${t}s;animation-delay:${Math.random() * delay}s`;
    layer.append(c);
    setTimeout(() => c.remove(), (t + delay + 0.2) * 1000);
  }
}
// A group (or a boss) beaten: a celebration over the whole screen, like the dice's, with what dropped.
// It lets clicks and keys through, so the loot buttons underneath work at once; it fades by itself,
// and goes as soon as you move on.
function endCelebration() { document.querySelector(".wincel")?.remove(); }
function celebrateWin({ boss, title, sub, gold, items }) {
  endCelebration();
  const top = items.filter((it) => BEAM_RANK[it.rarity]);
  const best = top.length ? E.itemColor(top.sort((a, b) => BEAM_RANK[b.rarity] - BEAM_RANK[a.rarity])[0]) : "#f0d25c";
  const shown = items.slice(0, 8);
  const layer = h(`<div class="diceshow wincel won${boss ? " boss" : ""}" aria-hidden="true" style="--pc:${best}"><div class="dice-rays"></div>
    <div class="dicebox win wincard"><i class="dice-bulbs"></i>
      <div class="dice-banner">${boss ? "¡Victoria!" : "¡Grupo derrotado!"}</div>
      <div class="win-title">${esc(title)}</div>${sub ? `<div class="win-sub">${sub}</div>` : ""}
      ${gold ? `<div class="win-gold">${icon("coins-pile", "#f0d25c")} +<b data-to="${gold}">0</b> de oro</div>` : ""}
      ${shown.length ? `<div class="win-items">${shown.map((it, i) => `<div class="win-item${BEAM_RANK[it.rarity] ? " top" : ""}" style="--c:${E.itemColor(it)};animation-delay:${0.5 + i * 0.18}s">${itemIco(it)}<span>${esc(it.unid ? `${RARITY[it.rarity]?.name || ""} sin identificar` : E.itemName(it))}</span></div>`).join("")}${items.length > shown.length ? `<div class="win-more">y ${items.length - shown.length} más</div>` : ""}</div>`
        : gold ? "" : `<div class="win-sub">Nada en el suelo esta vez.</div>`}
    </div></div>`);
  document.body.append(layer);
  sfx.groupWin(boss);
  if (!FX.reduced()) { const fl = h(`<i class="dice-flash"></i>`); layer.append(fl); setTimeout(() => fl.remove(), 600); }
  coinRain(layer, "#f0d25c", boss ? 70 : 34);
  if (top.length || boss) setTimeout(() => layer.isConnected && coinRain(layer, best, boss ? 60 : 30, 0.6), boss ? 2300 : 700);
  const g = layer.querySelector(".win-gold b");
  if (g) {
    const to = +g.dataset.to, t0 = performance.now(), ms = FX.reduced() ? 0 : 900;
    const step = () => { const k = ms ? Math.min(1, (performance.now() - t0) / ms) : 1; g.textContent = Math.round(to * (1 - Math.pow(1 - k, 3))); if (k < 1 && g.isConnected) requestAnimationFrame(step); };
    setTimeout(step, 350);
  }
  const stay = (boss ? 4800 : 2600) + Math.min(8, items.length) * 180;
  setTimeout(() => layer.classList.add("out"), stay);
  setTimeout(() => layer.remove(), stay + 500);
}
const dieIco = (kind = "racha") => `<i class="die-ico${kind === "oido" ? " ear" : ""}" aria-hidden="true"></i>`;
// Two percentile dice tumble and land; on a win, the gold prize die (a d20) rolls too, and the prize shows.
function showDice(r) {
  const stage = $(".stage");
  if (!stage) return;
  // the dice take over the screen (a layer over everything that lets clicks and typing through);
  // both streaks can roll on the same line: their boxes sit side by side, the ear's dice in blue
  const kind = r.kind2 || "racha";
  let show = document.querySelector(".diceshow");
  if (!show) document.body.append((show = h(`<div class="diceshow quiet" aria-live="polite"><div class="dice-rays"></div><div class="dicestack"></div></div>`)));
  const stack = show.querySelector(".dicestack");
  stack.querySelectorAll(`.dicebox[data-kind="${kind}"]`).forEach((n) => n.remove());
  show.classList.remove("out");
  const done = (box) => { box.remove(); if (!stack.children.length) show.remove(); };
  const tens = (v) => String(Math.floor((v % 100) / 10)) + "0", ones = (v) => String(v % 10);
  const box = h(`<div class="dicebox${kind === "oido" ? " ear" : ""}" data-kind="${kind}"><i class="dice-bulbs" aria-hidden="true"></i>
      <div class="dice-kind">${kind === "oido" ? "Dados de oído" : "Dados de la racha"}</div>
      <div class="dice-row"><span class="die d10" data-v="${tens(r.roll)}">${tens(r.roll)}</span><span class="die d10" data-v="${ones(r.roll)}">${ones(r.roll)}</span></div>
      <div class="dice-need">gana con ${r.need === 1 ? "un 1" : `1 a ${r.need}`}</div>
      <div class="dice-res"></div></div>`);
  kind === "oido" ? stack.append(box) : stack.prepend(box);
  const rain = (color, n) => coinRain(show, color, n);
  // a burst of coins and sparkles out of the box
  const burst = (color, n) => {
    if (FX.reduced()) return;
    for (let i = 0; i < n; i++) {
      const a = Math.random() * Math.PI * 2, d = 140 + Math.random() * 320;
      const c = h(`<i class="dice-coin${i % 3 ? "" : " spark"}"></i>`);
      c.style.cssText = `--dx:${Math.cos(a) * d}px;--dy:${Math.sin(a) * d - 120}px;--r:${Math.random() * 720 - 360}deg;--c:${color};animation-delay:${Math.random() * 0.25}s`;
      box.append(c);
      setTimeout(() => c.remove(), 1700);
    }
  };
  const tumble = (el, faces, ms) => new Promise((ok) => {
    if (FX.reduced()) return ok();
    const final = el.textContent, t0 = performance.now();
    el.classList.add("rolling");
    const tick = () => {
      if (performance.now() - t0 >= ms) { el.textContent = final; el.classList.remove("rolling"); el.classList.add("landed"); return ok(); }
      el.textContent = faces[Math.floor(Math.random() * faces.length)];
      setTimeout(tick, 55);
    };
    tick();
  });
  const res = box.querySelector(".dice-res");
  sfx.dice();
  setTimeout(() => sfx.dice(), 380);
  const [a, b] = box.querySelectorAll(".d10");
  Promise.all([tumble(a, ["00", "10", "20", "30", "40", "50", "60", "70", "80", "90"], 850), tumble(b, "0123456789".split(""), 1050)]).then(async () => {
    if (!box.isConnected) return;
    sfx.diceLand();
    if (!r.win) {
      res.innerHTML = `Sacas <b>${r.roll}</b>`;
      box.classList.add("lost");
      sfx.diceLose();
      setTimeout(() => { box.classList.add("out"); if (stack.children.length === 1) show.classList.add("out"); }, 700);
      setTimeout(() => done(box), 1050);
      return;
    }
    res.innerHTML = `<b>¡${r.roll}!</b> Premio…`;
    box.classList.add("win", "landwin");
    show.classList.remove("quiet");
    show.classList.add("won");
    if (!FX.reduced()) { const fl = h(`<i class="dice-flash"></i>`); show.append(fl); setTimeout(() => fl.remove(), 600); }
    rain("#f0d25c", 40);
    box.insertAdjacentHTML("afterbegin", `<div class="dice-banner">¡Premio!</div>`);
    burst("#f0d25c", 18);
    sfx.diceWin();
    const d20 = h(`<span class="die d20">${r.face}</span>`);
    box.querySelector(".dice-need").after(h(`<div class="dice-row prize"></div>`));
    const row = box.querySelector(".dice-row.prize");
    row.append(d20);
    if (r.bonus) row.append(h(`<span class="dice-bonus">+${r.bonus} <small>${kind === "oido" ? "oído" : "racha"}</small></span>`));
    sfx.dice();
    await tumble(d20, Array.from({ length: 20 }, (_, i) => String(i + 1)), 900);
    if (!box.isConnected) return;
    const top = r.kind === "mitico" || r.kind === "legendario" || r.kind === "ancestral";
    const color = r.gold ? "#f0d25c" : E.itemColor(r.item);
    res.innerHTML = `<b class="dice-total">${r.total}</b> <span style="color:${color}">${r.gold ? `${r.gold} de oro` : esc(r.label.replace(/^un[a]? /, "").replace(/^./, (c) => c.toUpperCase()))}</span>`;
    box.classList.add(top ? "jackpot" : "prized");
    box.style.setProperty("--pc", color);
    show.style.setProperty("--pc", color);
    if (top) { show.classList.add("jackpot"); box.querySelector(".dice-banner").textContent = "¡Jackpot!"; }
    burst(color, top ? 60 : 30);
    rain(color, top ? 90 : 45);
    if (top) setTimeout(() => box.isConnected && burst("#f0d25c", 40), 500);
    if (r.gold) sfx.coin(); else sfx.drop(r.item.rarity);
    sfx.jackpot(top);
    const me = $("#me");
    if (me && (top || r.kind === "item")) FX.beam(stage, FX.pointOn(me, stage, 0.5, 0.9), color, top ? 2600 : 1600);
    if (top) FX.shake(stage);
    renderHud(); renderPanels();
    setTimeout(() => { box.classList.add("out"); if (stack.children.length === 1) show.classList.add("out"); }, top ? 4200 : 3000);
    setTimeout(() => done(box), top ? 4700 : 3500);
  });
}
function renderCombo() {
  const c = S.F.combo, L = ch.streakLost;
  // a broken streak on its way back: a glowing badge, a dot per perfect line (the newest pops, the next blinks)
  const got = Math.min(c, REGAIN), popped = got > (S.F.regainShown || 0);
  S.F.regainShown = L ? got : 0;
  const dots = Array.from({ length: REGAIN }, (_, i) => `<i class="rdot${i < got ? " on" : i === got ? " next" : ""}${popped && i === got - 1 ? " pop" : ""}"></i>`).join("");
  const back = L ? ` <span class="regain" title="Fallaste con una racha de ${L}. ${REGAIN} aciertos seguidos la recuperan (más esos ${REGAIN}); otro fallo y se pierde."><span class="rlabel">Recupera tu racha de <b>${L}</b></span><span class="rdots">${dots}</span><b class="rcount">${got}/${REGAIN}</b></span>` : "";
  const el = $("#combo");
  // just got it back: a burst over the counter
  el.classList.toggle("regained", !!S.F.regainedAt && Date.now() - S.F.regainedAt < 2500);
  if (L) return void (el.innerHTML = (c ? `Racha <b>×${(1 + 0.1 * Math.min(c, 10)).toFixed(1)}</b> <span class="dim">(${c})</span>` : "") + back + earBadge());
  el.innerHTML = S.F.regainedAt && Date.now() - S.F.regainedAt < 2500 ? `<span class="rback">¡Racha recuperada!</span> ` : "";
  const next = E.diceChance(c + 1);
  el.innerHTML += c ? `Racha <b>×${(1 + 0.1 * Math.min(c, 10)).toFixed(1)}</b> <span class="dim">(${c})</span>${next ? ` <span class="luck" title="Los dados de la racha: la próxima frase perfecta tira un número del 1 al 100 y gana un premio con ${next === 1 ? "un 1" : `1 a ${next}`}, un ${next}% de probabilidad (dado de premio +${E.prizeBonus(c + 1)}).">${dieIco()} ${next}%</span>` : ""}` : "";
  el.innerHTML += earBadge();
}
// the ear streak: perfect lines in a row heard only once (no replay, no slow play, no hint)
function earBadge() {
  const e = S.F.ear || 0;
  if (!e) return "";
  const next = E.diceChance(e + 1);
  return ` <span class="earstreak" title="Racha de oído: frases perfectas seguidas escuchándolas una sola vez (sin repetir, sin cámara lenta, sin pistas). Desde ${E.DICE_FROM} tira sus propios dados${next ? `: la próxima gana con ${next === 1 ? "un 1" : `1 a ${next}`}, un ${next}% (dado de premio +${E.prizeBonus(e + 1)})` : ""}.">Oído <b>${e}</b>${next ? ` ${dieIco("oido")} ${next}%` : ""}</span>`;
}
// Element badges on monsters: what half of their hits are made of, and which resistance helps.
const ELEMENTS = {
  fire:   { name: "Fuego",  icon: "small-fire",      color: "#f0743a", res: "fuego" },
  cold:   { name: "Frío",   icon: "snowflake-2",     color: "#7fb8ff", res: "frío" },
  light:  { name: "Rayo",   icon: "lightning-helix", color: "#f2d43c", res: "rayo" },
  poison: { name: "Veneno", icon: "poison-bottle",   color: "#6fd06a", res: "veneno" },
};
const elemBadge = (el) => {
  const e = ELEMENTS[el];
  return e ? `<span class="elem" style="--ec:${e.color}" title="La mitad de su daño es de ${e.name.toLowerCase()}: tu resistencia al ${e.res} la reduce.">${icon(e.icon, e.color)}${e.name}</span>` : "";
};
// Weaknesses and immunities on a monster card: icon + word, details on hover.
const resChips = (res) => {
  const ks = Object.entries(res || {}).filter(([, v]) => v).sort((a, b) => b[1] - a[1]);
  if (!ks.length) return "";
  return `<span class="reses">${ks.map(([k, v]) => {
    const e = ELEMENTS[k], kind = v >= 100 ? "imm" : v > 0 ? "res" : "weak";
    const word = { imm: "inmune", res: "resiste", weak: "débil" }[kind];
    const tip = v >= 100 ? `Inmune al ${e.res}: tu daño de ${e.res} no le hace nada.` : v > 0 ? `Resiste el ${e.res}: tu daño de ${e.res} le hace un ${100 - v}%.` : `Débil al ${e.res}: tu daño de ${e.res} le hace un ${100 - v}%.`;
    return `<span class="rchip ${kind}" style="--ec:${e.color}" title="${tip}">${icon(e.icon, e.color)}${word}</span>`;
  }).join("")}</span>`;
};
function renderFoes() {
  const F = S.F;
  const t = currentTarget();
  if ($(".stage.scene")) return renderUnits(F, t);
  $("#foes").innerHTML = F.monsters.map((m, i) => `
    <button class="foe t-${m.tier} ${m.hp <= 0 ? "dead" : ""} ${m.fallen ? "fallen" : ""} ${t === m ? "target" : ""}" data-foe="${i}" ${m.hp <= 0 ? "disabled" : ""}>
      ${elemBadge(m.el)}
      <span class="foeart">${(m.tier === "boss" && bossSprite(m.kind, F.boss?.p2)) || monsterSvg(m.kind, { px: m.tier === "boss" ? 2.8 : 2, box: m.tier === "boss" ? 136 : 92 }) || icon(m.icon, m.color, "foeico")}</span>
      <span class="fname">${esc(m.mask || m.name)}</span>
      ${resChips(m.res)}
      ${m.mods.length ? `<span class="mods">${m.mods.map((k) => `<span title="${esc(MONSTER_MODS[k].desc)}">${MONSTER_MODS[k].name}</span>`).join(" · ")}</span>` : ""}
      <span class="hp"><i style="width:${(Math.max(0, m.hp) / m.maxHp) * 100}%"></i></span>
      <span class="hpnum">${Math.max(0, m.hp)}/${m.maxHp}</span>
    </button>`).join("");
  $("#foes").querySelectorAll("[data-foe]").forEach((b) => (b.onclick = () => { F.target = +b.dataset.foe; renderFoes(); focusInput(); }));
  $("#foes").querySelectorAll("[title]").forEach((n) => n.removeAttribute("title")); // the hover tooltip (foeTip) says it all
  renderBossBar(F);
}
// In a scene the monsters stand on the ground like in a 3D RPG: no card, a plate floating over the head
// (element, name, health, traits), a ring at the feet of the one you aim at, every other one a step back.
function renderUnits(F, t) {
  $("#foes").innerHTML = F.monsters.map((m, i) => { const big = m.tier === "boss" && hasBossArt(m.kind); return `
    <button class="foe unit t-${m.tier} ${m.hp <= 0 ? "dead" : ""} ${m.fallen ? "fallen" : ""} ${t === m ? "target" : ""} ${i % 2 && !big ? "back" : ""}${big ? ` bossunit${F.boss?.armed && bossRules(F) ? " armed" : ""}${F.boss?.p2 ? " p2" : ""}` : ""}" data-foe="${i}" ${m.hp <= 0 ? "disabled" : ""}
      ${big ? `style="--bc:${BOSSES[m.kind].color}"` : ""} aria-label="${esc(m.mask || m.name)}, ${Math.max(0, m.hp)} de ${m.maxHp} de vida${t === m ? ", objetivo" : ""}">
      ${big ? "" : `<span class="plate">
        <span class="pname">${m.el ? `<span class="pel" style="--ec:${ELEMENTS[m.el].color}" title="${esc(ELEMENTS[m.el].name)}: la mitad de su daño es de ${ELEMENTS[m.el].res}; tu resistencia al ${ELEMENTS[m.el].res} la reduce.">${icon(ELEMENTS[m.el].icon, ELEMENTS[m.el].color)}</span>` : ""}<span class="fname">${esc(m.mask || m.name)}</span></span>
        <span class="hp"><i style="width:${(Math.max(0, m.hp) / m.maxHp) * 100}%"></i><b class="hpnum">${Math.max(0, m.hp)}/${m.maxHp}</b></span>
        ${m.mods.length ? `<span class="mods">${m.mods.map((k) => `<span title="${esc(MONSTER_MODS[k].desc)}">${MONSTER_MODS[k].name}</span>`).join(" · ")}</span>` : ""}
        ${resChips(m.res)}
      </span>`}
      <span class="foeart">${big ? bossSprite(m.kind, F.boss?.p2) : monsterSvg(m.kind, { px: m.tier === "boss" ? 2.8 : 2.2, box: m.tier === "boss" ? 140 : 100 }) || icon(m.icon, m.color, "foeico")}</span>
    </button>`; }).join("");
  $("#foes").querySelectorAll("[data-foe]").forEach((b) => (b.onclick = () => { F.target = +b.dataset.foe; renderFoes(); focusInput(); }));
  $("#foes").querySelectorAll("[title]").forEach((n) => n.removeAttribute("title")); // the hover tooltip (foeTip) says it all
  renderBossBar(F);
}
// The boss's bar across the top of the stage: its title and name, its life (a mark at half, where it
// changes), its traits, and the meter of its signature attack.
function renderBossBar(F) {
  const el = $("#bossbar");
  if (!el) return;
  const m = bossOf(F);
  if (!m || !hasBossArt(m.kind) || !$(".stage.scene")) { el.hidden = true; return; }
  const def = BOSSES[m.kind], B = F.boss, hp = Math.max(0, m.hp), rules = bossRules(F);
  el.hidden = false;
  el.className = `bossbar${B?.armed && rules ? " armed" : ""}${B?.p2 ? " p2" : ""}${hp <= 0 ? " dead" : ""}${currentTarget() === m ? " target" : ""}`;
  el.style.setProperty("--bc", def.color);
  el.innerHTML = `
    <div class="bb-head"><span class="bb-title">${esc(def.title)}</span>
      <b class="bb-name">${m.el ? `<span class="pel" style="--ec:${ELEMENTS[m.el].color}">${icon(ELEMENTS[m.el].icon, ELEMENTS[m.el].color)}</span>` : ""}${esc(m.name)}</b></div>
    <div class="bb-hp"><i style="width:${(hp / m.maxHp) * 100}%"></i>${B && !B.p2 && rules ? `<span class="bb-half"></span>` : ""}<b>${hp}/${m.maxHp}</b></div>
    <div class="bb-info">${m.mods.length ? `<span class="mods">${m.mods.map((k) => MONSTER_MODS[k].name).join(" · ")}</span>` : ""}${resChips(m.res)}</div>
    ${rules && hp > 0 ? specialMeter(m.kind, B, bossEvery(F, m)) : ""}`;
  el.onclick = () => { F.target = F.monsters.indexOf(m); renderFoes(); focusInput(); };
}
// Hovering a monster: what it is, how hard it hits you (after your armour and resistances), what it
// shrugs off, its traits, and what clicking does.
const TIER_NAME = { normal: "", minion: "Esbirro", champion: "Campeón", unique: "Único", boss: "Jefe" };
function foeTip(m) {
  const st = stats(), D = E.diffOf(ch), t = currentTarget() === m;
  const raw = m.dmg * D.dmgTaken * 1.15, dr = Math.min(0.75, st.armor / (st.armor + 25 + 12 * m.lvl));
  const res = m.el ? st[`res${m.el[0].toUpperCase()}${m.el.slice(1)}`] || 0 : 0;
  const phys = m.el ? raw * 0.5 * (1 - dr) : raw * (1 - dr), elD = m.el ? raw * 0.5 * (1 - res / 100) : 0;
  const hit = Math.max(1, Math.round(phys + elD)), twice = m.mods.includes("rapido");
  const color = m.tier === "champion" ? "var(--r-magic)" : m.tier === "unique" || m.tier === "boss" ? "var(--r-unique)" : "var(--ink, #e4dfd2)";
  const E2 = m.el && ELEMENTS[m.el];
  const reses = Object.entries(m.res || {}).filter(([, v]) => v).sort((a, b) => b[1] - a[1]).map(([k, v]) => {
    const e = ELEMENTS[k];
    return `<div style="color:${e.color}">${v >= 100 ? `Inmune al ${e.res}: tu daño de ${e.res} no le hace nada` : v > 0 ? `Resiste el ${e.res}: tu daño de ${e.res} le hace un ${100 - v}%` : `Débil al ${e.res}: tu daño de ${e.res} le hace un ${100 - v}%`}</div>`;
  }).join("");
  return `<div class="tname" style="color:${color}">${esc(m.mask || m.name)}</div>
    <div class="tsub">${[TIER_NAME[m.tier], `nivel ${m.lvl}`].filter(Boolean).join(" · ")}</div>
    ${m.lore ? `<div class="tline dim">${esc(m.lore)}</div>` : ""}
    <div class="tline">Vida: <b>${Math.max(0, m.hp)}</b> de ${m.maxHp}</div>
    <div class="tline">Te pega hasta <b>${hit}</b>${twice ? " <b>dos veces</b> por turno" : " por turno"} <span class="dim">(con tu armadura${m.el ? ` y tu resistencia al ${E2.res}` : ""}, si fallas la frase entera)</span></div>
    ${E2 ? `<div class="tline" style="color:${E2.color}">${E2.name}: la mitad de su golpe es de ${E2.res}; te protege tu resistencia (${res}%)</div>` : ""}
    <div class="tline dim">Cuanto más aciertes, menos te pega; con la frase al ${Math.round(D.safeAcc * 100)}% o más, no te toca.</div>
    ${reses ? `<div class="tprops">${reses}</div>` : ""}
    ${m.mods.length ? `<div class="tprops">${m.mods.map((k) => `<div><b>${esc(MONSTER_MODS[k].name)}:</b> ${esc(MONSTER_MODS[k].desc)}</div>`).join("")}</div>` : ""}
    <div class="tline dim">${m.hp <= 0 ? "Derrotado" : t ? "Es tu objetivo" : "Clic para apuntarle"}</div>`;
}
document.addEventListener("mouseover", (e) => {
  const el = e.target.closest("[data-foe]");
  if (!el || !S.F || !$("#menu").hidden) return;
  const m = S.F.monsters[+el.dataset.foe];
  if (!m) return;
  tip.innerHTML = foeTip(m);
  tip.hidden = false;
  placeTip(el.querySelector(".foeart") || el);
});
document.addEventListener("mouseout", (e) => { const el = e.target.closest("[data-foe]"); if (el && !el.contains(e.relatedTarget)) tip.hidden = true; });
function currentTarget() {
  const F = S.F;
  if (F.monsters[F.target]?.hp > 0) return F.monsters[F.target];
  const a = alive(F)[0];
  F.target = F.monsters.indexOf(a);
  return a;
}
// The big number between you and them: the whole hit, coloured by your streak, with what the
// streak adds. Streak tiers: 3 (gold), 5 (fire), 7 (crimson), 10 (the cap: electric blue).
const STREAK = [[10, "max", "¡Racha máxima!"], [7, "t3", "¡Imparable!"], [5, "t2", "¡En llamas!"], [3, "t1", "¡Racha!"], [0, "t0", ""]];
// Zone backdrops behind the fight (scripts/build_scenes.py). ?scene=<id> in the address tries one in every zone.
const SCENES = new Set(["paramo", "cienaga", "selva", "llano", "ruinas", "abismo"]);
// What moves in each scene: [kind, how many]. Each particle gets a random place, size, speed and
// delay (CSS custom properties); the motion itself is in rpg.css (.sfx-<kind>).
const SCENE_FX = {
  paramo: [["fog", 6], ["drizzle", 26]],
  cienaga: [["firefly", 16], ["mist", 5]],
  selva: [["rain", 46], ["mote", 10], ["drip", 6]],
  llano: [["ember", 26], ["heat", 1], ["smoke", 4]],
  ruinas: [["shaft", 3], ["dust", 22], ["mist", 3]],
  abismo: [["spark", 26], ["glow", 1], ["ash", 14]],
};
function sceneFx(id) {
  const r = (a, b) => (a + Math.random() * (b - a)).toFixed(2);
  return `<div class="scenefx" aria-hidden="true">${(SCENE_FX[id] || []).flatMap(([k, n]) => Array.from({ length: n }, (_, i) =>
    `<i class="sfx-${k}" style="--x:${r(0, 100)}%;--y:${r(0, 100)}%;--s:${r(0.6, 1.4)};--d:${r(0.7, 1.5)};--t:${r(-1, 0)};--k:${i % 2 ? 1 : -1}"></i>`)).join("")}</div>`;
}
const sceneOf = (z) => { const q = new URLSearchParams(location.search).get("scene"); const id = z?.scene || z?.id; return SCENES.has(q) ? q : SCENES.has(id) ? id : null; };
function hitBanner(stage, me, tEl, hit, combo) {
  if (!stage || !tEl) return;
  const a = FX.pointOn(me, stage, 0.5, 0.35), b = FX.pointOn(tEl.querySelector(".foeart") || tEl, stage, 0.5, 0.35);
  let html;
  if (!hit.dmg) {
    if (!hit.broke) return;
    html = `<div class="hb t-broke"><span class="hb-tag">Racha rota</span><span class="hb-sub">${hit.broke} seguidas${ch.streakLost ? ` · <b class="hb-regain">${REGAIN} aciertos seguidos la recuperan</b>` : ""}</span></div>`;
  } else {
    const used = Math.min(hit.combo || 0, 10), [, tier, name] = STREAK.find(([n]) => combo >= n);
    const shown = hit.onTarget ?? hit.dmg; // what reached the one you aimed at, after its resistances
    const sub = [used ? `+${used * 10}% por racha` : "", E.diceChance(combo) ? `dados ${E.diceChance(combo)}%` : "", hit.crit ? "crítico ×2" : "", shown !== hit.dmg ? `${hit.dmg} antes de sus resistencias` : ""].filter(Boolean).join(" · ");
    html = `<div class="hb ${tier}${hit.crit ? " crit" : ""}">
      ${name || hit.crit ? `<span class="hb-tag">${name || "¡Crítico!"}</span>` : ""}
      <span class="hb-num">${shown}</span>
      ${combo >= 2 ? `<span class="hb-streak">${combo} seguidas</span>` : ""}
      ${typeChips(hit.landed || hit.parts, "out", hit.notes, shown)}
      ${sub ? `<span class="hb-sub">${sub}</span>` : ""}
      ${ch.streakLost ? `<span class="hb-regain">Recuperando ${ch.streakLost} · ${Math.min(combo, REGAIN)}/${REGAIN}</span>` : S.F?.regainedAt && Date.now() - S.F.regainedAt < 1500 ? `<span class="hb-regain done">¡Racha recuperada!</span>` : ""}</div>`;
  }
  stage.querySelectorAll(".hbwrap.out").forEach((n) => n.remove());
  const n = h(`<div class="hbwrap out">${html}</div>`);
  n.style.left = `${(a.x + b.x) / 2}px`; n.style.top = `${Math.max(75, stage.clientHeight * 0.48)}px`;
  FX.layerOf(stage).append(n);
  setTimeout(() => n.remove(), 1700);
}
// Little chips with each kind of damage in a hit: physical and the elements, with their icons.
// Yours say when the monster is immune, resists or is weak to an element.
const PHYS = { out: { name: "físico", icon: "broadsword", color: "#e8dcc0" }, in: { name: "físico", icon: "claws", color: "#e8dcc0" } };
// whole numbers that add up to the total shown (largest remainders get the leftover points)
function roundTo(by, total) {
  const e = Object.entries(by || {}).filter(([, v]) => v > 0), sum = e.reduce((t, [, v]) => t + v, 0);
  if (!sum || total == null) return by;
  const r = e.map(([k, v]) => { const x = (v * total) / sum; return [k, Math.floor(x), x - Math.floor(x)]; });
  let left = total - r.reduce((t, [, f]) => t + f, 0);
  r.sort((a, b) => b[2] - a[2]).forEach((x) => { if (left > 0) { x[1]++; left--; } });
  return { ...by, ...Object.fromEntries(r.map(([k, f]) => [k, f])) };
}
function typeChips(by, side, notes, total) {
  by = roundTo(by, total);
  const chips = Object.entries(by || {}).filter(([k, v]) => v >= 1 || notes?.immune.includes(k)).sort(([a], [b]) => (a === "phys" ? -1 : b === "phys" ? 1 : 0)).map(([k, v]) => {
    const T = k === "phys" ? PHYS[side] : { name: ELEMENTS[k].res, icon: ELEMENTS[k].icon, color: ELEMENTS[k].color };
    const state = notes?.immune.includes(k) ? "immune" : notes?.weak.includes(k) ? "weak" : notes?.resist.includes(k) ? "resist" : "";
    const tag = { immune: "inmune", weak: "débil", resist: "resiste" }[state];
    return `<span class="hb-chip ${state}" style="--ec:${T.color}">${icon(T.icon, T.color)}<b>${state === "immune" ? 0 : Math.round(v)}</b> ${T.name}${tag ? ` <i>${tag}</i>` : ""}</span>`;
  });
  return chips.length ? `<span class="hb-chips">${chips.join("")}</span>` : "";
}
// The same over you, for what the monsters did back: the total, each kind, and what you avoided.
function hurtBanner(stage, me, taken, inc, safe) {
  if (!stage || !me) return;
  const p = FX.pointOn(me, stage, 0.5, 0.3);
  let html;
  if (!taken) {
    if (!safe && !inc?.dodged && !inc?.blocked) return;
    const what = safe ? "Esquivas todo" : inc.blocked && !inc.dodged ? "Bloqueas" : "Esquivas";
    html = `<div class="hb t-dodge"><span class="hb-tag">${what}</span>${safe ? `<span class="hb-sub">entendiste la frase</span>` : ""}</div>`;
  } else {
    const avoided = [inc.dodged ? `${inc.dodged} esquivado${inc.dodged > 1 ? "s" : ""}` : "", inc.blocked ? `${inc.blocked} bloqueado${inc.blocked > 1 ? "s" : ""}` : ""].filter(Boolean).join(" · ");
    html = `<div class="hb t-hurt"><span class="hb-num">−${taken}</span>
      ${typeChips(inc.by, "in", null, taken)}
      <span class="hb-sub">${inc.hits} ${inc.hits === 1 ? "golpe" : "golpes"}${avoided ? ` · ${avoided}` : ""}</span></div>`;
  }
  stage.querySelectorAll(".hbwrap.in").forEach((n) => n.remove());
  const n = h(`<div class="hbwrap in">${html}</div>`);
  n.style.left = `${Math.max(70, p.x)}px`; n.style.top = `${Math.max(60, p.y)}px`;
  FX.layerOf(stage).append(n);
  setTimeout(() => n.remove(), 1700);
}
function floatNum(i, text, cls, pop = 1) {
  // over a monster: on the effects layer, so it doesn't fade along with a monster that falls
  const foe = i >= 0 && $(`#foes [data-foe="${i}"] .foeart`), stage = $(".stage");
  if (foe && stage) {
    const { x, y } = FX.pointOn(foe, stage, 0.5, 0.25);
    const n = h(`<span class="fx"><span class="float ${cls}" style="--pop:${pop}">${text}</span></span>`);
    n.style.left = `${x}px`; n.style.top = `${y}px`;
    FX.layerOf(stage).append(n);
    return setTimeout(() => n.remove(), 1200);
  }
  const el = $(`#foes [data-foe="${i}"]`) || $("#lifeOrb");
  const n = h(`<span class="float ${cls}">${text}</span>`);
  el.append(n);
  setTimeout(() => n.remove(), 1200);
}

function nextExercise() {
  const F = S.F;
  if (F.review) {
    // wait for the last answer to reach Anki: a failed card may be coming back
    if (afterAnswer(nextExercise)) return;
    if (!cardsLeft()) return repasoDone();
    F.ex = { card: pickCard() };
    F.si = null;
  } else {
    if (!F.queue.length) F.queue = buildQueue();
    // One you got right doesn't come back this fight. One you missed rests for 5 minutes, then
    // comes first. If everything left is resting, the one that has rested longest.
    const n = F.queue.length, open = (e) => !F.known?.includes(exKey(e)), A = missAt();
    // a boss throws a phrase you just missed straight back, three phrases later (once each)
    F.turn = (F.turn || 0) + 1;
    const back = F.enc.boss && (F.comeback || []).find((c) => c.at <= F.turn && open(c.e));
    if (back) { F.comeback.splice(F.comeback.indexOf(back), 1); addLog(`<b>${esc(BOSSES[S.zone.boss]?.name || "El jefe")}</b> te devuelve una frase que fallaste.`, "weak"); }
    const due = back ? back.e : F.queue.find((e) => open(e) && A[exKey(e)] && !resting(e));
    let pick = due;
    // in a boss fight, what you already know waits until nothing else is left, resting or not
    const fresh = (e) => !F.enc.boss || !(exMastered(e) || lineMastered(e.si));
    for (let k = 0; !pick && k < n; k++) { const e = F.queue[(F.qi + k) % n]; if (open(e) && !resting(e) && fresh(e)) { pick = e; F.qi += k + 1; } }
    if (!pick && F.enc.boss) pick = F.queue.filter((e) => open(e) && fresh(e)).sort((a, b) => A[exKey(a)] - A[exKey(b)])[0];
    for (let k = 0; !pick && k < n; k++) { const e = F.queue[(F.qi + k) % n]; if (open(e) && !resting(e)) { pick = e; F.qi += k + 1; } }
    if (!pick) pick = F.queue.filter(open).sort((a, b) => A[exKey(a)] - A[exKey(b)])[0];
    if (!pick) pick = F.queue[F.qi++ % n];
    F.ex = pick;
    F.si = F.ex.si;
  }
  F.revealed = false; F.ease = null;
  if (F.boss?.tangle > 0) F.boss.tangle--;
  F.plays = 0; F.slows = 0; F.paid = 0; F.paidCount = 0; F.freeListening = false; F.hinted = false; F.checked = false; F.explanation = "";
  // how things stood before this line, in case it gets flagged as not matching the audio
  F.before = { life: ch.life, mana: ch.mana, combo: F.combo, ear: F.ear || 0, streakLost: ch.streakLost || 0, lines: ch.stats.lines, perfect: ch.stats.perfect, boss: F.boss ? JSON.parse(JSON.stringify(F.boss)) : null };
  save();
  setupExercise(false);
  renderBossWarn();
  renderGroupMastery();
  // let the last round's sounds finish first, so the line isn't heard over them
  const ex = F.ex;
  quiet().then(() => { if (S.F === F && F.ex === ex && !F.plays && !F.slows && !F.checked && !earOnlyAfter()) doPlay(false); });
}
// a course's "write the verb": the clip says the verb, so it's heard only once you've answered
const earOnlyAfter = () => S.F?.lesson?.mode === "gap" && !S.F.checked;
function setupExercise(keep) {
  const F = S.F, st = stats();
  queueMicrotask(refreshSources);
  if (F.ex.card?.kind === "recall") { F.mode = "recall"; return setupCardExercise(); }
  if (F.ex.card?.kind === "subj") { F.mode = "subj"; return setupSubjExercise(); }
  F.lesson = F.ex.card ? null : lessonOf(F.si);
  if (F.lesson && F.ex.k != null) F.lesson = { ...F.lesson, mode: "word", word: F.lesson.gloss[F.ex.k] };
  if (F.lesson && F.lesson.mode !== "gap") { F.mode = "recall"; return setupLessonRecall(F.lesson); }
  F.mode = F.lesson ? "cloze" : st.kind === "ranged" ? "cloze" : "dictation";
  const words = exWords();
  const C = E.costs(ch, st, alive(F).some((m) => m.mods.includes("maldito")));
  const eco = alive(F).some((m) => m.mods.includes("eco"));
  const typed = keep ? ($("#answer")?.value || "") : "";
  $("#arena").innerHTML = `
    <div class="ex">
      <div class="excontrols">
        <button id="playBtn" class="playbtn" title="Escuchar (Tab)"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></button>
        <button id="slowBtn" ${eco ? "disabled title='El eco no te deja escuchar despacio'" : F.boss?.tangle > 0 ? "disabled title='Las enredaderas no te dejan'" : `title="Escuchar despacio (Mayús+Tab)"`}>Despacio <span class="cost">${C.slow ? C.slow + " maná" : "gratis"}</span></button>
        <button id="hintBtn" ${F.boss?.tangle > 0 ? "disabled title='Las enredaderas no te dejan'" : `title="Primera letra de cada palabra (Alt+H)"`}>Pista <span class="cost">${C.hint} maná</span></button>${E.powerOf(ch) ? `<button id="powBtn" class="powbtn${powerOn(F) ? " on" : ""}" style="--sc:${E.powerOf(ch).color}" title="${esc(E.powerOf(ch).desc)}">${icon(E.powerOf(ch).icon, E.powerOf(ch).color)} ${esc(E.powerOf(ch).name)} <span class="cost">${E.powerCost(ch, stats())} maná</span></button>` : ""}
        <span class="dim exinfo" id="exinfo"></span>
        ${F.review ? `<span class="deckname">${esc(F.ex.card.deckName)}</span>` : `<button class="flagBtn ghost" title="El texto no coincide con el audio (palabras equivocadas o el corte suena mal). Quita la frase de los juegos y deshace sus efectos.">No coincide</button>`}
      </div>
      ${F.mode === "cloze" ? `<div class="cloze" id="cloze"></div>` : `<div class="skeleton" id="skeleton" hidden></div><textarea id="answer" rows="2" placeholder="Escribe lo que oíste y pulsa Enter para atacar" autocomplete="off" autocapitalize="off" spellcheck="false"></textarea>`}
      <div class="exactions"><button id="attackBtn" class="primary">Atacar <kbd>Enter</kbd></button></div>
      <div class="result" id="result" hidden></div>
    </div>`;
  if (F.mode === "cloze") {
    F.blanks = F.lesson ? F.lesson.at.slice() : F.ex.card ? chooseBlanks({ 0: { words } }, 0, E.diffOf(ch).cloze) : clozeBlanks(F.ex, words);
    // the word of a weak spot you're fighting is always among the gaps
    const must = F.ex.card || F.lesson ? [] : words.map((w, i) => i).filter((i) => !isSound(words[i].w) && alive(F).some((m) => m.weak && m.weak === norm(words[i].w)));
    // (a second pass keeps its own gaps as well, so it doesn't come out the same as the first)
    if (must.length) F.blanks = [...new Set([...must, ...F.blanks])].slice(0, F.ex.v ? Infinity : Math.max(F.blanks.length, must.length)).sort((a, b) => a - b);
    const box = $("#cloze");
    words.forEach((w, i) => {
      if (F.blanks.includes(i)) {
        const inp = h(`<input data-i="${i}" size="${Math.max(10, w.w.length)}" autocomplete="off" spellcheck="false" autocapitalize="off">`);
        box.append(inp);
        // a course's gap: after the verb, what it is in Spanish
        if (F.lesson && i === F.lesson.at[F.lesson.at.length - 1]) box.append(" ", h(`<span class="gaphint" title="En español">(${esc(F.lesson.hint)})</span>`));
      } else box.append(w.w);
      box.append(" ");
    });
  } else if (keep) $("#answer").value = typed;
  $("#playBtn").onclick = () => { doPlay(false); focusInput(); };
  $("#slowBtn").onclick = () => { doPlay(true); focusInput(); };
  if (earOnlyAfter()) for (const b of ["#playBtn", "#slowBtn"]) { $(b).disabled = true; $(b).title = "La frase suena después de responder"; }
  $("#powBtn")?.addEventListener("click", usePower);
  $("#hintBtn").onclick = () => hint(); // not `= hint`: the click event would arrive as `free`
  $("#attackBtn").onclick = attack;
  bindFlag();
  if (F.hinted) { F.hinted = false; hint(true); }
  updateExInfo();
  focusInput();
}
// Course modes (the verb, word by word, the whole sentence): hear and read the sentence, think what it means, look, and say how it went.
const LESSON_EASE = { 1: "No lo sabía", 2: "Más o menos", 3: "Lo sabía", 4: "Fácil" };
const LESSON_ACC = { 1: 0, 2: 0.6, 3: 1, 4: 1 };
const verbWords = (L, seg) => L.at.map((i) => seg.words[i].w.replace(/[^\p{L}'’-]/gu, "")).join(" ");
function lessonBack(L, seg) {
  if (L.mode === "word") return `<div class="lverbans"><b lang="en">${esc(L.word[0])}</b> = <b>${esc(L.word[1])}</b></div>
    <div class="lt">${esc(L.t)}</div>`;
  return `<div class="lverbans"><b lang="en">${esc(verbWords(L, seg))}</b> = <b>${esc(L.hint)}</b>
      <span class="lforms"><span lang="en">${esc(L.v)} · ${esc(L.past)} · ${esc(L.pp)}</span>: ${esc(L.es)}</span></div>
    <div class="lt">${esc(L.t)}</div>
    ${L.gloss?.length ? `<ul class="lgloss">${L.gloss.map(([en, es]) => `<li><b lang="en">${esc(en)}</b> ${esc(es)}</li>`).join("")}</ul>` : ""}`;
}
function setupLessonRecall(L) {
  const F = S.F, C = E.costs(ch, stats()), seg = S.T.segments[F.si];
  const mark = (i) => (L.mode === "verb" ? L.at.includes(i) : L.mode === "word" && i >= F.ex.a && i < F.ex.b);
  const sent = seg.words.map((w, i) => (mark(i) ? `<b class="lverb">${esc(w.w)}</b>` : esc(w.w))).join(" ");
  $("#arena").innerHTML = `
    <div class="ex lesson">
      <div class="excontrols">
        <button id="playBtn" class="playbtn" title="Escuchar (Tab)"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></button>
        <button id="slowBtn" title="Escuchar despacio (Mayús+Tab)">Despacio <span class="cost">${C.slow ? C.slow + " maná" : "gratis"}</span></button>
        <span class="dim exinfo" id="exinfo"></span>
      </div>
      <p class="lq">${L.mode === "verb" ? `¿Qué significa <b lang="en">${esc(verbWords(L, seg))}</b>?` : L.mode === "word" ? `¿Qué significa <b lang="en">${esc(L.word[0])}</b> aquí?` : "¿Qué significa la frase? Cada palabra."}</p>
      <div class="lsent" lang="en">${sent}</div>
      <div class="cardback lback" id="cardBack" hidden>${lessonBack(L, seg)}</div>
      <div class="exactions">
        <button id="revealBtn" class="primary">Mostrar <kbd>Espacio</kbd></button>
        <div class="grades" id="grades" hidden>${[1, 2, 3, 4].map((k) => `<button data-ease="${k}" class="g${k}">${LESSON_EASE[k]} <kbd title="tecla">${k}</kbd></button>`).join("")}</div>
      </div>
      <div class="result" id="result" hidden></div>
    </div>`;
  $("#playBtn").onclick = () => doPlay(false);
  $("#slowBtn").onclick = () => doPlay(true);
  $("#revealBtn").onclick = revealCard;
  document.querySelectorAll("#grades [data-ease]").forEach((b) => (b.onclick = () => gradeCard(+b.dataset.ease)));
  updateExInfo();
  focusInput();
}
function showLessonResult(acc) {
  const F = S.F, res = $("#result");
  res.innerHTML = `
    <div class="verdict">${acc >= 1 ? "¡Bien!" : acc > 0 ? "A medias." : "La próxima vez."}
      <span class="dim">${F.prevBest == null ? "Primera vez." : `Antes: ${F.prevBest >= 1 ? "la sabías" : "no la sabías"}.`}</span>
      ${F.masteredNow ? `<span class="mastered">¡${F.lesson?.mode === "word" ? "Palabra" : "Frase"} dominada! +${F.masteredNow} exp</span>` : ""}</div>
    <div class="row"><button id="againBtn">Volver a oír</button>
      <button id="nextBtn" class="primary">${alive(F).length ? "Siguiente frase" : "Recoger el botín"} <kbd>Enter</kbd></button></div>`;
  res.hidden = false;
  $("#grades").hidden = true;
  renderGroupMastery();
  $("#againBtn").onclick = () => playSeg(F.si, 1);
  $("#nextBtn").onclick = afterResult;
  $("#nextBtn").focus();
}
function updateExInfo() {
  const F = S.F, st = stats();
  const free = Math.max(0, 1 + st.freeReplay - F.plays);
  const C = E.costs(ch, st), D = E.diffOf(ch);
  const left = D.paidListens != null ? D.paidListens - F.paidCount : null;
  const what = F.freeListening ? `escuchas libres · recompensa ×${D.freeReward}`
    : left != null && left <= 0 ? `repetir: gratis, pero la frase dará ×${D.freeReward}`
    : free ? `${free} ${free === 1 ? "escucha gratis" : "escuchas gratis"}`
    : `repetir: ${C.replay} maná${left != null ? ` (${left} más, luego gratis con menos recompensa)` : ""}`;
  $("#exinfo").textContent = F.lesson ? `${LEVEL_NAME[F.lesson.mode]} · ${what}`
    : F.mode === "recall" && !F.ex.card?.audio ? "Recuerda la respuesta"
    : `${F.mode === "cloze" ? "Rellena los huecos" : F.mode === "recall" ? "Recuerda el significado" : "Dictado"} · ${what}`;
  $("#exinfo").classList.toggle("freeListen", !!F.freeListening);
}
function focusInput() {
  if (!S.F || S.F.checked) return;
  (S.F.mode === "cloze" ? $("#cloze input") : S.F.mode === "recall" ? $("#revealBtn") : $("#answer"))?.focus();
}
function spend(n) {
  if (ch.mana < n) { toast(n > stats().maxMana ? `Cuesta ${n} de maná y tu barra solo llega a ${stats().maxMana}: necesitas más maná máximo (equipo, energía).` : "No tienes suficiente maná. Bebe una poción (Alt+2)."); flashOrb("#manaOrb", "hit"); return false; }
  ch.mana -= n; renderHud(); return true;
}
const unlimitedNow = () => { const D = E.diffOf(ch); return D.paidListens != null && S.F.paidCount >= D.paidListens; };
function enterFreeListening() {
  const F = S.F;
  if (F.freeListening) return;
  F.freeListening = true;
  addLog(`Escuchas libres: esta frase da solo el ${Math.round(E.diffOf(ch).freeReward * 100)}% de daño, experiencia y botín.`, "bad");
}
const rewardMul = () => (S.F?.freeListening ? E.diffOf(ch).freeReward : 1);
function doPlay(slow) {
  const F = S.F;
  if (!F || (F.si == null && !F.ex?.card) || F.ex?.card?.kind === "subj") return;
  if (F.ex?.card && F.ex.card.kind === "recall" && !F.ex.card.audio) return;   // a card with nothing to hear
  const st = stats(), C = E.costs(ch, st);
  if (F.checked) return playSeg(F.si, slow ? 0.75 : 1);
  if (earOnlyAfter()) return toast("La frase suena después de responder");
  const unlimited = unlimitedNow();
  // Fácil: once the paid listens are bought, listening is free but the line pays less.
  // Without the mana to buy them, there are no more listens.
  const pay = (n) => {
    if (!n) return true;
    if (unlimited) { enterFreeListening(); return true; }
    if (!spend(n)) return false;
    F.paidCount++;
    return true;
  };
  if (slow) {
    if (alive(F).some((m) => m.mods.includes("eco"))) return toast("El eco no te deja escuchar despacio");
    if (F.boss?.tangle > 0) return toast("Las enredaderas no te dejan: sin Despacio");
    if (!pay(C.slow)) return;
    F.slows++;
  } else {
    if (F.plays >= 1 + st.freeReplay && !pay(C.replay)) return;
    F.plays++;
  }
  playSeg(F.si, slow ? 0.75 : 1);
  updateExInfo();
}
function hint(free) {
  const F = S.F;
  if (F.mode === "recall" || F.checked || (F.hinted && !free)) return;
  if (F.mode === "subj") {
    if (!free) { const C = E.costs(ch, stats()); if (!spend(C.hint)) return; }
    F.hinted = true;
    $("#hintBtn").disabled = true;
    $("#skeleton").innerHTML = subjFrame(F.ex.card);
    $("#skeleton").hidden = false;
    return focusInput();
  }
  if (!free && F.boss?.tangle > 0) return toast("Las enredaderas no te dejan: sin Pista");
  if (!free) {
    const C = E.costs(ch, stats(), alive(F).some((m) => m.mods.includes("maldito")));
    if (!spend(C.hint)) return;
  }
  F.hinted = true;
  $("#hintBtn").disabled = true;
  const words = exWords();
  if (F.mode === "cloze") {
    for (const inp of document.querySelectorAll("#cloze input")) if (!inp.value) inp.placeholder = words[+inp.dataset.i].w.replace(/^[¿¡]/, "")[0] + "…";
  } else {
    const sk = $("#skeleton");
    sk.innerHTML = words.map((w) => { const b = w.w.replace(/[^\p{L}']/gu, ""); return `<span>${esc(b[0] || "")}${"_".repeat(Math.max(0, b.length - 1))}</span>`; }).join("");
    sk.hidden = false;
  }
  focusInput();
}

function attack() {
  const F = S.F;
  if (!F || F.checked) return;
  if (F.mode === "recall") return F.revealed ? null : revealCard();
  if (F.mode === "subj") return attackSubj();
  const after = earOnlyAfter();
  if (F.plays + F.slows === 0 && !after) return toast("Escucha primero (Tab)");
  const st = stats(), D = E.diffOf(ch), words = exWords();
  const opts = { extraTol: st.typoTol, nearIsExact: st.nearExact };
  let r;
  if (F.mode === "cloze") {
    const typed = Object.fromEntries([...document.querySelectorAll("#cloze input")].map((x) => [x.dataset.i, x.value.trim()]));
    r = scoreCloze(words, F.blanks, typed, opts);
  } else r = scoreDictation(words, $("#answer").value, opts);
  const perfect = r.acc >= 1 && F.plays + F.slows <= 1 && !F.hinted;
  if (F.review) {
    // dictated Anki card: perfect first listen = Fácil, right = Bien, close = Difícil, else Otra vez
    F.ease = r.acc >= 1 ? (perfect ? 4 : 3) : r.acc >= 0.8 ? 2 : 1;
    answerCard(F.ex.card, F.ease);
  }
  resolveAttack(r, r.acc, perfect);
  // now that it's answered, hear it (once the hit's sounds are done)
  if (after) quiet().then(() => { if (S.F === F && F.checked) playSeg(F.si, 1); });
}
function resolveAttack(r, acc, perfectFirst) {
  const F = S.F, st = stats(), D = E.diffOf(ch), words = F.lesson || !(F.mode === "recall" || F.mode === "subj") ? exWords() : [];
  F.checked = true;
  // every word right with every accent: kills from this attack roll good loot at double the odds
  F.goodLoot = r.accentsPerfect ? 2 : 1;
  // gaps filled with words you've already got right in a gap again and again: less rare loot
  F.freshLoot = F.mode === "cloze" && !F.review && !F.lesson ? gapFreshness(r) : ((F.gapStale = null), 1);
  // the streak counting this answer (kills land before the streak is updated below): its loot luck
  F.luckCombo = acc >= 1 ? F.combo + 1 : st.comboKeep && acc >= 0.85 ? F.combo : 0;
  ch.stats.lines++;
  // an item that counts near misses as right helps in the fight (damage, streak, dodging), but what
  // you really wrote is what counts for mastery and your record
  const wrote = r.strictAcc ?? acc;
  if (wrote >= 1) ch.stats.perfect++;
  if (F.review) F.masteredNow = 0;
  else { masteryUpdate(wrote, words, D); trackWords(r); if (F.masteredNow) zoneRewards(S.zone); }
  const caught = []; // (runes caught by ear used to rise over you here)
  if (acc >= 1 && ch.streakLost) sfx.regain(F.combo + 1); else if (acc >= 1) sfx.correct(F.combo, perfectFirst); else if (acc >= 0.8) sfx.partial();
  const said = new Set((r.words || []).map((x) => norm(x.w))), right = new Set((r.words || []).filter((x) => x.ok).map((x) => norm(x.w)));
  // masked weak spots show their name once their line has been answered
  for (const m of F.monsters) if (m.mask && ((m.weak && said.has(m.weak)) || (m.leechCard && F.ex.card?.note === m.leechCard))) {
    delete m.mask;
    addLog(`El punto débil era «<b>${esc(m.weak ? m.word : m.name)}</b>».`, "weak");
  }


  // a course fight ends when she knows every one of its lines, no sooner and no later
  const course = !F.review && S.zone?.fights;
  if (!F.review && acc >= 1) (F.known ||= []).includes(exKey(F.ex)) || F.known.push(exKey(F.ex));
  if (!F.review) { if (acc < 1) missAt()[exKey(F.ex)] = Date.now(); else delete missAt()[exKey(F.ex)]; }
  if (!F.review && !course && F.enc.boss && acc < 1 && !(F.thrown ||= []).includes(exKey(F.ex))) { F.thrown.push(exKey(F.ex)); (F.comeback ||= []).push({ e: F.ex, at: (F.turn || 0) + 4 }); }
  const left = course ? F.queue.filter((e) => !F.known?.includes(exKey(e))).length : 0;

  // your attack
  const target = currentTarget();
  // in a course the weapon decides the kind of damage, whatever the mode asks
  const hitMode = F.lesson ? (st.kind === "ranged" ? "cloze" : "dictation") : F.mode === "recall" || F.mode === "subj" ? "dictation" : F.mode;
  const hit = E.playerAttack(ch, st, acc, hitMode, { perfectFirst, combo: F.combo });
  hit.combo = F.combo; // the streak this hit was made with (its bonus)
  if (F.freeListening) {
    hit.dmg = Math.round(hit.dmg * rewardMul());
    for (const k in hit.parts) hit.parts[k] *= rewardMul();
  }
  // the prepared spell goes off with the hit, if there's mana for it
  let spell = null, cast = null;
  const prepared = E.canCast(ch, st) && SPELLS.find((x) => x.id === ch.spell && ch.level >= x.lvl);
  if (prepared) {
    const cost = E.spellCost(ch, prepared);
    if (ch.mana < cost) addLog(`No te alcanza el maná para <b>${esc(prepared.name)}</b> (${cost}): golpe sin hechizo.`, "bad");
    else {
      ch.mana -= cost; spell = prepared;
      cast = E.castSpell(ch, st, spell, hit, acc);
      hit.parts = cast.parts;
      if (hit.dmg) hit.dmg = Math.max(1, Math.round(Object.values(hit.parts).reduce((a, b) => a + b, 0)));
      hit.spell = spell;
      addLog(hit.dmg ? `Lanzas <b style="color:${spell.color}">${esc(spell.name)}</b> <span class="dim">(−${cost} de maná)</span>.` : `<b>${esc(spell.name)}</b> se deshace en el aire: no acertaste ninguna palabra <span class="dim">(−${cost} de maná)</span>.`, hit.dmg ? "" : "bad");
    }
  }
  // the class ability waiting for this hit (a hit with no word right keeps it for the next)
  const armed = F.power && hit.dmg ? POWERS[ch.cls] : null;
  if (armed) {
    F.power = null;
    if (armed.double) { for (const k in hit.parts) hit.parts[k] *= 2; hit.dmg *= 2; }
    addLog(`<b style="color:${armed.color}">${esc(armed.name)}</b>${armed.volley ? ": el golpe cae sobre todos" : ": el doble de daño"}.`, "good");
  }
  const volley = !!armed?.volley;
  // overkill carries over to the next monster, as the same share of each part of the hit
  let share = hit.dmg ? 1 : 0, totalDealt = 0, remaining = hit.dmg;
  const order = [target, ...alive(F).filter((m) => m !== target)];
  const elemNotes = [], fxHits = [];
  let bonus = hit.crit || F.combo >= 5; // the log shows the number bigger and bold
  for (const m of order) {
    if (share <= 0) break;
    // a weak spot: its own word, written right, hits it twice as hard; missed again, half
    const wm = m.weak && said.has(m.weak) ? (right.has(m.weak) ? 2 : 0.5) : 1;
    if (wm > 1 && hit.dmg) bonus = true;
    if (m.weak && wm !== 1 && hit.dmg) addLog(wm > 1 ? `Escribes bien «<b>${esc(m.word)}</b>»: <b>${esc(m.name)}</b> recibe el doble.` : `Se te vuelve a escapar «${esc(m.word)}»: <b>${esc(m.name)}</b> se ríe y recibe la mitad.`, wm > 1 ? "good" : "bad");
    const parts = Object.fromEntries(Object.entries(hit.parts).map(([k, v]) => [k, v * share * wm]));
    const { dmg, notes, by } = E.damageAgainst(parts, m);
    if (m === target) { hit.landed = by; hit.notes = notes; hit.onTarget = dmg; }
    if (m === target && notes.weak.length) bonus = true;
    if (m === target) elemNotes.push(...notes.immune.map((k) => `<b>${esc(m.mask || m.name)}</b> es inmune al ${ELEMENTS[k].res}.`),
      ...notes.weak.map((k) => `<b>${esc(m.mask || m.name)}</b> es débil al ${ELEMENTS[k].res}: más daño.`));
    const dealt = Math.min(m.hp, dmg);
    m.hp -= dmg;
    // the last one holds on while there are lines she doesn't know yet
    if (course && left && m.hp <= 0 && !alive(F).some((x) => x !== m)) m.hp = 1;
    totalDealt += dealt;
    fxHits.push({ i: F.monsters.indexOf(m), text: (hit.crit && m === target ? "¡" : "") + dmg + (hit.crit && m === target ? "!" : ""), cls: hit.crit ? "crit" : "dmg", killed: m.hp <= 0, m });
    // a spell that hits everyone hits each one whole; otherwise only overkill carries on
    share = (cast?.all || volley) && hit.dmg ? 1 : m.hp < 0 && dmg ? share * (-m.hp / dmg) : 0;
    if (m.hp <= 0) kill(m);
  }
  // a fireball splashes onto every other monster still standing
  if (cast?.splash && hit.dmg) for (const m of alive(F).filter((x) => x !== target)) {
    const { dmg } = E.damageAgainst(Object.fromEntries(Object.entries(hit.parts).map(([k, v]) => [k, v * cast.splash])), m);
    if (!dmg) continue;
    m.hp -= dmg; totalDealt += Math.min(dmg, m.hp + dmg);
    fxHits.push({ i: F.monsters.indexOf(m), text: String(dmg), cls: "dmg", killed: m.hp <= 0, m });
    if (m.hp <= 0) kill(m);
  }
  if (cast?.freeze && target.hp > 0) {
    target.frozen = cast.freeze;
    addLog(`<b>${esc(target.mask || target.name)}</b> queda congelado: no ataca ni ahora ni en el turno siguiente.`, "good");
  }
  if (cast?.shield) {
    F.shield = Math.min(st.maxLife, (F.shield || 0) + cast.shield);
    addLog(`Un <b style="color:${spell.color}">escudo arcano</b> te rodea: absorbe <b>${F.shield}</b> de daño.`, "good");
  }
  remaining = Math.round(hit.dmg * share);
  if (hit.dmg === 0) addLog(F.mode === "subj" ? "Fallas el golpe: el modo no era ese." : F.lesson && F.mode === "recall" ? "Fallas el golpe: no lo sabías." : "Fallas el golpe: no acertaste ninguna palabra.", "bad");
  else addLog(`${hit.crit ? (perfectFirst ? "<b>¡Golpe perfecto!</b> " : "<b>¡Crítico!</b> ") : ""}Golpeas por <b class="dmg${bonus ? " big" : ""}">${hit.dmg}</b>${Object.keys(hit.parts).length > 1 ? ` <span class="dim">(${Object.entries(hit.parts).filter(([, v]) => v).map(([k, v]) => k === "phys" ? `${Math.round(v)} del arma` : `${Math.round(v)} de ${ELEMENTS[k].res}`).join(" + ")})</span>` : ""}${F.combo >= 5 ? ` <span class="combotag">racha ×${F.combo}</span>` : ""}.`, hit.crit ? "good" : "");
  for (const n of elemNotes) addLog(n, n.includes("débil") ? "good" : "bad");
  if (course && !left && alive(F).length) {
    addLog("Ya sabes todas las frases de este combate: <b>los que quedan caen</b>.", "good");
    for (const m of alive(F)) { fxHits.push({ i: F.monsters.indexOf(m), text: "✓", cls: "dmg", killed: true, m }); kill(m); }
  }
  if (st.leech && totalDealt) ch.life = Math.min(st.maxLife, ch.life + Math.round((totalDealt * st.leech) / 100));
  if (st.manaLeech && totalDealt) ch.mana = Math.min(st.maxMana, ch.mana + Math.round((totalDealt * st.manaLeech) / 100));

  // a boss at half its life changes
  const boss = bossRules(F) ? bossOf(F) : null;
  let p2Now = false;
  if (boss && boss.hp > 0 && !F.boss.p2 && boss.hp <= boss.maxHp / 2) { bossPhase2(F, boss); p2Now = true; }

  // streak
  // a miss: the streak you had waits (ch.streakLost); 3 perfect in a row bring it back, plus those 3.
  // A miss on the way back loses it for good.
  hit.broke = 0;
  if (acc >= 1) {
    F.combo++;
    const L = ch.streakLost;
    if (L && F.combo >= REGAIN) {
      F.combo = L + F.combo; ch.streakLost = 0; F.regainedAt = Date.now();
      setTimeout(() => { if (S.F === F) renderCombo(); }, 2600);
      addLog(`<b>¡Recuperas tu racha!</b> ${REGAIN} seguidas: vuelves a <b>${F.combo}</b>.`, "good");
    } else if (L) addLog(`Recuperando tu racha de ${L}: <b>${F.combo}/${REGAIN}</b>.`, "good");
  } else if (!(st.comboKeep && acc >= 0.85)) {
    if (ch.streakLost) addLog(`Se pierde tu racha de ${ch.streakLost}.`, "bad");
    // only a streak worth getting back waits: 10 or more (REGAIN_FROM)
    const keep = F.combo >= REGAIN_FROM ? F.combo : 0;
    if (F.combo >= 3) { addLog(`Se rompe tu racha de ${F.combo}.${keep ? ` <b>${REGAIN} seguidas</b> la recuperan.` : ""}`, "bad"); hit.broke = F.combo; }
    ch.streakLost = keep; F.combo = 0;
  }
  ch.stats.bestCombo = Math.max(ch.stats.bestCombo, F.combo);
  ch.streak = F.combo; // the streak goes on into the next group, until you miss or fall
  // the streak dice: from a streak of 5, every perfect line rolls for a prize
  const dice = acc >= 1 && !F.review ? streakDice(F) : null;
  // the ear streak: only lines you listen to count; heard once and perfect, it grows; anything else ends it
  let earDice = null;
  if (!(F.mode === "recall" || F.mode === "subj")) {
    if (acc >= 1 && perfectFirst) {
      F.ear = (F.ear || 0) + 1;
      ch.stats.bestEar = Math.max(ch.stats.bestEar || 0, F.ear);
      if (!F.review) earDice = streakDice(F, "oido");
      if (F.ear === E.DICE_FROM && !F.review) addLog(`<b>¡Racha de oído de ${E.DICE_FROM}!</b> ${E.DICE_FROM} frases perfectas seguidas escuchándolas una sola vez. Desde ahora esta racha tira sus propios dados, los azules, igual que la otra.`, "good");
    } else {
      if (F.ear >= 3) addLog(`Se acaba tu racha de oído de ${F.ear}.`, "bad");
      F.ear = 0;
    }
    ch.earStreak = F.ear;
  }
  if (F.combo === E.DICE_FROM && acc >= 1 && !F.review) addLog(`<b>¡Racha de ${E.DICE_FROM}!</b> Desde ahora cada frase perfecta tira los dados: sale un número del 1 al 100, y si es igual o menor que tu probabilidad de premio, ganas algo. Ahora es un ${E.diceChance(E.DICE_FROM)}% (solo gana un 1); sube 1 punto cada 2 frases perfectas, hasta un 15%, y con la racha mejora también el premio.`, "good");

  // their turn
  let taken = 0;
  const attackers = [], incoming = { by: {}, hits: 0, dodged: 0, blocked: 0 };
  const frozenNow = [];
  // a boss with its signature attack ready lets go of it instead of its normal blow
  const unleash = !!(boss && boss.hp > 0 && F.boss.armed), bossFrozen = !!(boss && boss.frozen > 0);
  for (const m of alive(F)) {
    if (m.frozen > 0) { m.frozen--; frozenNow.push(m.mask || m.name); continue; }
    if (m === boss && unleash) continue;
    attackers.push(F.monsters.indexOf(m));
    const swings = m.mods.includes("rapido") ? 2 : 1;
    for (let k = 0; k < swings; k++) {
      const a = E.monsterAttack(ch, st, m, acc, ch.level, D);
      if (a.dodged || a.blocked) { incoming[a.blocked ? "blocked" : "dodged"]++; continue; }
      taken += a.dmg;
      incoming.hits++;
      incoming.by.phys = (incoming.by.phys || 0) + a.phys;
      if (a.el) incoming.by[a.el] = (incoming.by[a.el] || 0) + a.elDmg;
      if (m.vamp) m.hp = Math.min(m.maxHp, m.hp + Math.round(a.dmg * 0.5));
      if (m.mods.includes("ladron")) ch.mana = Math.max(0, ch.mana - Math.round(3 + m.lvl / 3));
      if (st.thorns) { m.hp -= st.thorns; if (m.hp <= 0) { kill(m); break; } }
    }
    // a perfect line doesn't give it time to heal
    if (m.mods.includes("regenera") && m.hp > 0 && acc < 1) m.hp = Math.min(m.maxHp, m.hp + Math.round(m.maxHp * 0.02));
  }
  // the boss: burning, its signature attack, the price of the Mandingas's deal
  let bossEv = null;
  if (boss && boss.hp > 0) {
    const B = F.boss;
    if (B.burn > 0) {
      if (acc >= 1) { B.burn = 0; addLog("Una frase perfecta: <b>apagas el fuego</b>.", "good"); }
      else {
        const d = Math.max(1, Math.round(st.maxLife * 0.05 * (1 - (st.resFire || 0) / 100)));
        B.burn--; taken += d; incoming.by.fire = (incoming.by.fire || 0) + d;
        addLog(`Ardes: <b class="taken">−${d}</b>${B.burn ? ` <span class="dim">(${B.burn} ${B.burn === 1 ? "turno" : "turnos"} más)</span>` : ""}.`, "bad");
      }
    }
    bossEv = bossTurn(F, boss, acc, st, D, unleash, bossFrozen);
    if (bossEv.hit) {
      const a = bossEv.hit;
      taken += a.dmg; incoming.hits++;
      incoming.by.phys = (incoming.by.phys || 0) + a.phys;
      if (a.el) incoming.by[a.el] = (incoming.by[a.el] || 0) + a.elDmg;
    }
    if (B.deal === "signed" && acc < 1) {
      const d = Math.max(1, Math.round(st.maxLife * PRICE));
      taken += d; incoming.by.phys = (incoming.by.phys || 0) + d;
      addLog(`El trato se cobra su parte: <b class="taken">−${d}</b>.`, "bad");
    }
    bossEv.p2Now = p2Now;
  } else if (p2Now) bossEv = { kind: boss.kind, p2Now };
  // a forgotten card is memory, not a fight lost: one card costs at most a little of your life
  const REVIEW_CAP = 0.12;
  if (F.review && taken > st.maxLife * REVIEW_CAP) {
    const capped = Math.max(1, Math.round(st.maxLife * REVIEW_CAP));
    for (const k in incoming.by) incoming.by[k] *= capped / taken;
    taken = capped;
  }
  if (acc >= D.safeAcc && alive(F).length && !taken) addLog(acc >= 1 ? "Entendiste todo: <b>esquivas todos los ataques</b>." : "Entendiste lo suficiente: <b>esquivas todos los ataques</b>.", "good");
  else if (taken) {
    const kinds = Object.entries(roundTo(incoming.by, taken)).filter(([, v]) => v >= 1).map(([k, v]) => `${Math.round(v)} ${k === "phys" ? "físico" : `de ${ELEMENTS[k].res}`}`);
    addLog(`Te golpean por <b class="taken">${taken}</b>${kinds.length > 1 ? ` <span class="dim">(${kinds.join(" + ")})</span>` : ""}.`, "bad");
  }
  if (frozenNow.length && !(acc >= D.safeAcc)) addLog(`${frozenNow.map((n) => `<b>${esc(n)}</b>`).join(", ")} no ${frozenNow.length > 1 ? "pueden" : "puede"} moverse: ${frozenNow.length > 1 ? "están congelados" : "está congelado"}.`, "good");
  if (F.roar > 0) {
    if (taken) { const cut = Math.floor(taken / 2); taken -= cut; addLog(`El grito de guerra les quita fuerza: <b>${cut}</b> de daño menos.`, "good"); }
    if (--F.roar === 0) addLog("Se apaga el efecto del grito de guerra.", "dim");
  }
  if (F.shield && taken) {
    const soak = Math.min(F.shield, taken);
    F.shield -= soak; taken -= soak;
    addLog(`El escudo arcano absorbe <b>${soak}</b>${F.shield ? ` <span class="dim">(le quedan ${F.shield})</span>` : ": <b>se rompe</b>"}.`, "good");
  }
  ch.life -= taken;
  ch.life = Math.min(st.maxLife, ch.life + st.lifeRegen);
  ch.mana = Math.min(st.maxMana, ch.mana + st.manaRegen);

  save();
  renderCombo(); renderHud(); renderPanels();
  const round = playRound(F, { hits: fxHits, target: F.monsters.indexOf(target), attackers, taken, incoming, hit, safe: acc >= D.safeAcc && !taken, dying: ch.life <= 0, caught, combo: F.combo, boss: bossEv });
  if (ch.life <= 0) {
    // the fall plays out first; nothing else can happen meanwhile
    F.over = true;
    if ($("#portal")) $("#portal").disabled = true;
    return round.then(() => { if (S.F === F) die(r, acc); });
  }
  F.goodLoot = 1; F.freshLoot = 1;
  if (dice) setTimeout(() => { if (S.F === F) showDice(dice); }, FX.reduced() ? 0 : 700);
  if (earDice) setTimeout(() => { if (S.F === F) showDice(earDice); }, FX.reduced() ? 0 : dice ? 1000 : 700);
  if (F.boss?.dealPending) round.then(() => setTimeout(() => offerDeal(F), 300));
  showResult(r, acc, hit);
}

// Best score per exercise of the episode; a first 100% pays a bonus.
function masteryUpdate(acc, words, D) {
  const F = S.F, M = mastery(), key = exKey(F.ex), prevBest = M[key];
  F.prevBest = prevBest;
  M[key] = Math.max(prevBest ?? 0, acc);
  F.before.mastery = prevBest;
  if (acc >= 1) { recordPerfect(F.ex, scoreKind()); checkCompanions(); }
  if (acc >= 1 && !(prevBest >= 1)) {
    const share = words.length / S.T.segments[F.si].words.length;
    const bonus = Math.max(1, Math.round(E.xpFor(ch.level) * 0.6 * share * D.xp * rewardMul() * XP_RATE));
    gainXp(bonus);
    F.masteredNow = bonus;
  } else F.masteredNow = 0;
}
// Every phrase of a zone at 100% pays once (per episode, zone, descent and way of playing):
// all the gaps filled, a legendary or mythic item; every sentence written whole, a mythic one.
const zoneRewardKey = (z, depth, kind) => `${S.ep}|${z.id}|${z.endless ? depth || 0 : 0}|${kind}`;
const zoneRewardGot = (z, depth, kind) => !!ch.zoneRewards?.[zoneRewardKey(z, depth, kind)];
function zoneRewards(z) {
  if (!S.T || !z || z.id === "repaso" || z.dynamic) return;
  const zp = ch.zones[z.id];
  for (const depth of z.endless ? Array.from({ length: Math.min(deepest(zp), descentsOf(z) - 1) + 1 }, (_, d) => d) : [zp?.depth || 0]) zoneRewardsAt(z, depth);
}
function zoneRewardsAt(z, depth) {
  const lines = zoneLines(z, depth);
  if (!lines.length) return;
  for (const kind of z.fights ? ["dict"] : ["dict", "cloze"]) {
    const key = zoneRewardKey(z, depth, kind);
    if (ch.zoneRewards?.[key] || mastered(lines, kind) < lines.length) continue;
    const rarity = kind === "dict" || Math.random() < 0.3 ? "mitico" : "legendario";
    const it = E.randomItem(Math.max(ch.level, atLevel(z).lvl?.[0] || 1) + 2, 0, 1, null, null, 1, rarity);
    it.unid = true;
    const where = stow(it);
    if (!where && S.F?.ground) S.F.ground.items.push(it);
    else if (!where) continue; // nowhere to put it: try again later
    (ch.zoneRewards ||= {})[key] = true;
    save();
    const what = kind === "dict" ? "todas las frases escritas enteras" : "todos los huecos rellenados";
    const zname = z.endless ? `${z.name}, descenso ${depth + 1}` : z.name;
    if (S.F) addLog(`<b>¡${esc(zname)} dominada!</b> ${what} al 100%. Premio: un objeto <span style="color:${E.itemColor(it)}">${RARITY[rarity].name.toLowerCase()}</span> (${where || "en el suelo"}).`, "good");
    celebrate({ z, kind, n: lines.length, it, where: where || "al suelo: recógelo al terminar el combate" });
  }
}
// The celebration: one screen per prize, one after another if several arrive at once.
const cheers = [];
// ---------- pets and mounts ----------
// Perfect lines are also kept per difficulty (a perfect on Difícil counts for Normal too), so that
// finishing a whole episode both ways can be told apart by where it was done.
const PERFECT_COUNTS = { medio: ["medio"], dificil: ["medio", "dificil"] };
const COMPANION = { pet: { diff: "medio", list: PETS, own: "pets", on: "pet" }, mount: { diff: "dificil", list: MOUNTS, own: "mounts", on: "mount" } };
const perfectMap = (diff, kind) => ((((ch.perfectBy ||= {})[diff] ||= {})[S.ep] ||= {})[kind] ||= {});
function recordPerfect(e, kind) { for (const d of PERFECT_COUNTS[ch.difficulty || "medio"] || []) perfectMap(d, kind)[exKey(e)] = 1; }
const companionEpisode = () => !!S.T && !S.T.zones && (S.T.duration || 0) >= COMPANION_MIN_SECONDS;
// how many of the episode's lines are perfect, each way, on a difficulty
function epPerfect(diff) {
  const n = S.lines.length, out = { n };
  for (const kind of ["cloze", "dict"]) {
    const M = perfectMap(diff, kind);
    out[kind] = S.lines.filter((si) => lineMastered(si, kind, M)).length;
  }
  return out;
}
function checkCompanions() {
  if (!companionEpisode()) return;
  for (const [type, C] of Object.entries(COMPANION)) {
    if (ch.companionEps?.[S.ep]?.[type]) continue;
    if (!PERFECT_COUNTS[ch.difficulty || "medio"]?.includes(C.diff)) continue;
    const n = S.lines.length;
    if (Object.keys(perfectMap(C.diff, "cloze")).length < n || Object.keys(perfectMap(C.diff, "dict")).length < n) continue;
    const p = epPerfect(C.diff);
    if (p.cloze < n || p.dict < n) continue;
    awardCompanion(type);
  }
}
function awardCompanion(type) {
  const C = COMPANION[type], own = (ch[C.own] ||= []);
  const fresh = Object.keys(C.list).filter((id) => !own.includes(id));
  const id = fresh.length ? fresh[Math.floor(Math.random() * fresh.length)] : null;
  ((ch.companionEps ||= {})[S.ep] ||= {})[type] = id || "all";
  let it = null, where = null;
  if (id) { own.push(id); if (!ch[C.on]) ch[C.on] = id; }
  else { // every coat already: a legendary instead
    it = E.randomItem(ch.level + 2, 0, 1, null, null, 1, "legendario"); it.unid = true;
    where = stow(it);
    if (!where && S.F?.ground) S.F.ground.items.push(it);
  }
  save(); renderMe(); renderHud();
  if (S.F) addLog(`<b>¡Episodio dominado${type === "mount" ? " en Difícil" : ""}!</b> ${id ? `${type === "pet" ? "Un perro" : "Un caballo"} se une a ti: <b>${esc(C.list[id].name)}</b>.` : "Ya tenías todos: te llevas un objeto legendario."}`, "good");
  celebrate({ companion: type, id, it, where: where || "al suelo: recógelo al terminar el combate" });
}
const compImg = (type, id) => `rpg/lpc/companions/${type}-${id}.png`;
const companionLine = (type, id) => type === "pet"
  ? `${PETS[id].desc} ${Object.entries(PETS[id].props).map(([k, v]) => PROPS[k].fmt.replace("{v}", v)).join(", ")}.`
  : `${Object.entries(MOUNT_PROPS).map(([k, v]) => PROPS[k].fmt.replace("{v}", v)).join(", ")}.`;

function celebrate(c) {
  cheers.push(c);
  if (cheers.length === 1) showCheer();
}
function showCheer() {
  const c = cheers[0];
  if (!c) return;
  if (c.mound) return showMoundCheer(c);
  if (c.companion && c.id) return showCompanionCheer(c);
  const color = E.itemColor(c.it), R = RARITY[c.it.rarity].name;
  const sparks = Array.from({ length: 28 }, (_, i) => `<i style="--a:${(i * 360) / 28 + (i % 3) * 7}deg;--d:${0.9 + (i % 5) * 0.25}s;--r:${110 + (i % 4) * 45}px"></i>`).join("");
  const d = dialog(`<div class="cheer" style="--c:${color}">
      <div class="sparks" aria-hidden="true">${sparks}</div>
      ${c.melt ? `<p class="cheer-kicker">${esc(c.melt)}</p>
      <h3>${c.neck ? "¡Camiseta del conjunto!" : "¡Conjunto transmutado!"}</h3>
      <p class="cheer-what">${c.neck ? "Fundiste el conjunto entero en una camiseta encantada: todas sus bonificaciones y la mitad de las propiedades de sus piezas. Se lleva debajo de todo, en su propio sitio; con ella puesta se te ve con el conjunto entero, lleves lo que lleves encima." : `Fundiste el conjunto entero en el alambique.${c.n > 1 ? ` Premio ${c.i + 1} de ${c.n}.` : ""}`}</p>
      <div class="cheer-prize">${itemIco(c.it)}<div><b style="color:${color}">${esc(E.itemName(c.it))}</b><span class="dim">${R} · va ${esc(c.where)}</span></div></div>`
      : `<p class="cheer-kicker">${esc(c.z.name)}</p>
      <h3>¡Zona dominada!</h3>
      <p class="cheer-what">${c.kind === "dict" ? `Escribiste enteras las ${c.n} frases` : `Rellenaste todos los huecos de las ${c.n} frases, las dos veces`}, cada una al 100%.</p>
      <div class="cheer-prize">${itemIco(c.it)}<div><b style="color:${color}">Objeto ${R.toLowerCase()}</b><span class="dim">Sin identificar · va ${esc(c.where)}</span></div></div>`}
      <button class="primary" id="cheerOk">${cheers.length > 1 ? "Siguiente premio" : "¡Seguir!"}</button>
    </div>`, { cls: "cheerbox", onClose: () => { cheers.shift(); if (cheers.length) setTimeout(showCheer, 250); } });
  d.querySelector("#cheerOk").onclick = () => closeDialog();
  setTimeout(() => d.querySelector("#cheerOk")?.focus(), 50);
  sfx.fanfare();
  setTimeout(() => sfx.drop(c.it.rarity), 900);
}
function showMoundCheer(c) {
  const sparks = Array.from({ length: 36 }, (_, i) => `<i style="--a:${(i * 360) / 36}deg;--d:${0.9 + (i % 5) * 0.25}s;--r:${120 + (i % 4) * 45}px"></i>`).join("");
  let prize, color = RARITY.relic.color;
  if (c.companion) {
    const C = COMPANION[c.companion], x = C.list[c.id], pet = c.companion === "pet";
    prize = `<div class="cheer-comp"><img class="${c.companion}" src="${compImg(c.companion, c.id)}" alt=""><div><b>${esc(x.name)}</b><span class="dim">${pet ? `Un ${PET_KIND} ${x.coat}` : `Un caballo ${x.coat}`} · ${esc(companionLine(c.companion, c.id))}</span>
      <span class="dim small">${ch[C.on] === c.id ? "Va contigo." : "Llévalo contigo desde Personaje → Compañeros."}</span></div></div>`;
  } else {
    color = E.itemColor(c.it);
    prize = `<div class="cheer-prize">${itemIco(c.it)}<div><b style="color:${color}">${esc(E.itemName(c.it))}</b><span class="dim">${RARITY[c.it.rarity].name} · va ${esc(c.where)}</span></div></div>`;
  }
  const d = dialog(`<div class="cheer" style="--c:${color}">
      <div class="sparks" aria-hidden="true">${sparks}</div>
      <p class="cheer-kicker">El Montón${c.n > 1 ? ` · premio ${c.i + 1} de ${c.n}` : ""}</p>
      <h3>¡El montón se transforma!</h3>
      <p class="cheer-what">${MOUND_STEP} gemas perfectas se funden en ${c.companion ? (c.companion === "pet" ? "una mascota" : "una montura") : "un objeto mítico"}.</p>
      ${prize}
      <button class="primary" id="cheerOk">${cheers.length > 1 || c.i + 1 < c.n ? "Siguiente premio" : "¡Seguir!"}</button>
    </div>`, { cls: "cheerbox", onClose: () => { cheers.shift(); if (cheers.length) setTimeout(showCheer, 250); } });
  d.querySelector("#cheerOk").onclick = () => closeDialog();
  setTimeout(() => d.querySelector("#cheerOk")?.focus(), 50);
  sfx.fanfare();
  setTimeout(() => sfx.drop("mitico"), 900);
}
function showCompanionCheer(c) {
  const C = COMPANION[c.companion], x = C.list[c.id], pet = c.companion === "pet";
  const sparks = Array.from({ length: 28 }, (_, i) => `<i style="--a:${(i * 360) / 28 + (i % 3) * 7}deg;--d:${0.9 + (i % 5) * 0.25}s;--r:${110 + (i % 4) * 45}px"></i>`).join("");
  const d = dialog(`<div class="cheer" style="--c:#f2d27a">
      <div class="sparks" aria-hidden="true">${sparks}</div>
      <p class="cheer-kicker">${esc(S.T.title)}</p>
      <h3>¡Episodio dominado${pet ? "" : " en Difícil"}!</h3>
      <p class="cheer-what">Todas las frases, con huecos y al dictado, al 100%${pet ? "" : " en Difícil"}.</p>
      <div class="cheer-comp"><img class="${c.companion}" src="${compImg(c.companion, c.id)}" alt=""><div><b>${esc(x.name)}</b><span class="dim">${pet ? `Un ${PET_KIND} ${x.coat}` : `Un caballo ${x.coat}`} · ${esc(companionLine(c.companion, c.id))}</span>
        <span class="dim small">${ch[C.on] === c.id ? "Va contigo." : "Llévalo contigo desde Personaje → Compañeros."}</span></div></div>
      <button class="primary" id="cheerOk">${cheers.length > 1 ? "Siguiente premio" : "¡Seguir!"}</button>
    </div>`, { cls: "cheerbox", onClose: () => { cheers.shift(); if (cheers.length) setTimeout(showCheer, 250); } });
  d.querySelector("#cheerOk").onclick = () => closeDialog();
  setTimeout(() => d.querySelector("#cheerOk")?.focus(), 50);
  sfx.fanfare();
}
// "You wrote X, it was Y": the words you got wrong, one by one. Grammar forms say their tense.
function nearMissHtml(r, max = 5) {
  const wrong = (r?.words || []).filter((x) => !x.ok);
  if (!wrong.length) return "";
  const items = wrong.slice(0, max).map((x) => {
    const want = esc(bare(x.w)), got = x.typed ? esc(bare(x.typed) || x.typed) : "";
    const g = runeOf(x.w);
    const tag = g ? ` <span class="gtag" title="Tiempo verbal">${esc(g.rune.tense)}</span>` : "";
    if (x.accent) return `<li>Tilde: era <b>${want}</b>, no <s>${got}</s>${tag}</li>`;
    if (got) return `<li>Escribiste <s>${got}</s>; era <b>${want}</b>${tag}</li>`;
    return `<li>Se te pasó <b>${want}</b>${tag}</li>`;
  });
  if (wrong.length > max) items.push(`<li class="dim">y ${wrong.length - max} más</li>`);
  return `<ul class="nearmiss">${items.join("")}</ul>`;
}

// ---------- the round, animated ----------
// Your figure attacks with its weapon's move; at the moment of impact the foes update (numbers,
// flinches, falls) with a swing, jab, arrow or bolt in the colour of the hit's strongest element.
// Then whoever is still standing lunges at you.
const MOVE = { slash: [70, 3], thrust: [55, 5], shoot: [45, 8], spellcast: [65, 4] }; // ms per frame, frame of impact/release
const foeEl = (i) => $(`#foes [data-foe="${i}"]`);
function hitColor(parts) {
  let best = null, v = 0;
  for (const [k, x] of Object.entries(parts || {})) if (k !== "phys" && ELEMENTS[k] && x > v) { best = k; v = x; }
  return best && v >= (parts.phys || 0) * 0.25 ? ELEMENTS[best].color : "#f4ead2";
}
async function playRound(F, { hits, target, attackers, taken, incoming, hit, safe, dying, caught = [], combo = 0, boss: bev = null }) {
  const stage = $(".stage"), fig = S.fig, me = $("#me");
  const move = attackAnim(ch), [ms, at] = MOVE[move] || MOVE.slash;
  const color = hitColor(hit.parts), big = hit.crit;
  const live = () => S.F === F && $(".stage") === stage;
  fig?.play(move, { ms });
  await FX.wait(ms * (at + 1)); // +1: the turn to face them
  if (!live()) return;
  const tEl = foeEl(target);
  if (tEl && (move === "shoot" || move === "spellcast")) {
    const from = FX.pointOn(fig?.el || me, stage, 0.45, 0.5), to = FX.pointOn(tEl.querySelector(".foeart") || tEl, stage);
    const w = ch.equip[`weapon${ch.swap}`];
    const kind = move === "spellcast" ? "bolt" : (w?.base || "").startsWith("honda") ? "stone" : "arrow";
    await FX.projectile(stage, from, to, kind, move === "spellcast" && color === "#f4ead2" ? "#b28cff" : color);
    if (!live()) return;
  }
  // impact: numbers grow with your streak
  renderFoes();
  hitBanner(stage, fig?.el || me, foeEl(target), hit, combo);
  const pop = Math.min(1.9, 1 + 0.09 * Math.min(combo, 10));
  if (hit.dmg) sfx.hit(big);
  for (const h of hits) {
    const el = foeEl(h.i);
    if (!el) continue;
    floatNum(h.i, h.text, `${h.cls}${combo >= 5 ? " hot" : ""}`, pop);
    if (h.killed && h.m?.tier === "boss") {
      // the final blow: the boss brought up huge and cut in two, then it falls on the stage
      sfx.finisher();
      bossFinisher(stage, { color, bossColor: BOSSES[h.m.kind]?.color || "#e04030" }).then(() => { el.classList.add("dying"); sfx.bossDeath(); lootBeam(F, stage, h); });
      if (FX.reduced()) { el.classList.add("dying"); sfx.bossDeath(); lootBeam(F, stage, h); }
    } else if (h.killed) { el.classList.add("dying"); setTimeout(() => sfx.kill(), 120); lootBeam(F, stage, h); }
    else FX.pulse(el, "flinch", 360);
  }
  const tNow = foeEl(target);
  if (tNow) {
    const p = FX.pointOn(tNow.querySelector(".foeart") || tNow, stage);
    if (!hit.dmg) { floatNum(target, "Fallas", "miss"); sfx.miss(); }
    else {
      if (move === "slash") FX.slash(stage, p, color, big);
      else if (move === "thrust") FX.thrust(stage, p, color, big);
      FX.burst(stage, p, color, big);
      if (big) FX.shake(stage);
    }
  }
  // a critical hit, or one that takes 40% of a monster's life or more: blown up over the whole screen
  // (not the blow that kills a boss: that has its own finisher)
  const tm = F.monsters[target], bossKill = hits.some((h) => h.killed && h.m?.tier === "boss");
  if (hit.dmg && tm && !bossKill && (big || hit.dmg >= 0.4 * tm.maxHp)) {
    const art = foeEl(target)?.querySelector(".foeart");
    if (art) {
      sfx.bigHit();
      await bigHit(art, { color: color === "#f4ead2" ? "#ffe68a" : color, label: big ? "¡Crítico!" : "¡Golpe brutal!", num: hit.dmg });
      if (!live()) return;
    }
  }
  // a boss at half its life: it changes before your eyes
  if (bev?.p2Now) {
    const d = BOSSES[bev.kind];
    setTimeout(() => {
      if (!live()) return;
      bossShout(stage, `<small>${esc(d.name)}</small>${esc(d.p2.text.split(".")[0])}`, "phase", d.color, 2600);
      if (d.p2.scream) { sfx.scream(); FX.shake(stage); } else sfx.bossIntro(bev.kind);
      FX.pulse(stage.querySelector(".bossunit"), "transform", 900);
    }, 450);
  }
  // their turn
  const blow = bev && (bev.hit || bev.dodged);
  if (!attackers.length && !blow && !bev?.charged && !taken) return;
  await FX.wait(300);
  if (!live()) return;
  attackers.forEach((i, k) => setTimeout(() => FX.pulse(foeEl(i), "lunge", 360), FX.reduced() ? 0 : k * 90));
  // the boss hitting you: it leaps out of the screen at you, huge (its signature blow bigger, with its name)
  const bossHits = taken && attackers.some((i) => F.monsters[i]?.tier === "boss");
  if (bev?.hit || bossHits) {
    const d = BOSSES[F.monsters.find((m) => m.tier === "boss")?.kind];
    if (d) {
      sfx.bossLunge(!!bev?.hit);
      await bossLeap(stage, { color: d.color, big: !!bev?.hit, name: bev?.hit ? d.special.name : "" });
      if (!live()) return;
    }
  }
  if (blow) {
    const d = BOSSES[bev.kind], bu = stage.querySelector(".bossunit");
    FX.pulse(bu, "unleash", 700);
    if (bev.hit) {
      bossShout(stage, esc(d.special.name), "blow", d.color);
      sfx.bossBlow(bev.kind);
      FX.shake(stage);
      FX.burst(stage, FX.pointOn(me, stage, 0.5, 0.45), d.color, true);
    } else bossShout(stage, `¡Esquivado!<small>${esc(d.special.name)}</small>`, "dodged", "#9fe8a0");
  }
  await FX.wait(170);
  if (!live()) return;
  // a heavy blow on you (a quarter of your life or more), unless the boss has just leapt at you for it
  if (taken && !dying && !(bev?.hit || bossHits) && taken >= 0.25 * stats().maxLife) { sfx.bigHurt(); bigHurt({ num: taken }); }
  if (attackers.length || taken) hurtBanner(stage, fig?.el || me, taken, incoming, safe);
  if (taken) {
    sfx.hurt();
    flashOrb("#lifeOrb", "hit");
    FX.pulse(me, "hit", 380);
    if (dying) {
      me.classList.add("dying");
      await fig?.play("hurt", { ms: 110, hold: true });
      await FX.wait(650);
    } else fig?.play("hurt", { ms: 70, frames: 3 });
  }
  // the boss charging its signature attack: the Silbón climbs his scale; full, it's coming
  if (bev?.charged && !dying) {
    await FX.wait(blow ? 900 : 450);
    if (!live()) return;
    if (bev.kind === "silbon") sfx.whistle(bev.charged - 1);
    if (bev.ready) {
      const d = BOSSES[bev.kind];
      setTimeout(() => { if (live()) { bossShout(stage, `${esc(d.special.name)}<small>Viene con la próxima frase</small>`, "ready", d.color, 2200); if (bev.kind !== "silbon") sfx.armed(); } }, bev.kind === "silbon" ? 350 : 0);
    }
  }
}

// The best thing a fallen monster dropped, if it's worth a column of light.
const BEAM_RANK = { relic: 9, tunjo: 8, mitico: 7, legendario: 6, ancestral: 5, unique: 4, set: 4, rare: 3 };
function lootBeam(F, stage, h) {
  const best = (h.m?.drops || []).map((it) => ({ it, r: it.kind === "relic" ? "relic" : it.rarity })).filter((x) => BEAM_RANK[x.r]).sort((a, b) => BEAM_RANK[b.r] - BEAM_RANK[a.r])[0];
  if (!best) return;
  const el = foeEl(h.i);
  if (!el) return;
  const p = FX.pointOn(el.querySelector(".foeart") || el, stage, 0.5, 0.95);
  setTimeout(() => {
    if (S.F !== F) return;
    FX.beam(stage, p, E.itemColor(best.it), BEAM_RANK[best.r] >= 5 ? 1800 + 600 * (BEAM_RANK[best.r] - 4) : best.r === "unique" || best.r === "set" ? 2400 : 1600);
    sfx.drop(best.r);
  }, 520);
}
// Every piece of gear that falls, by rarity (what you saw, after a review's reduced rewards): the
// character panel shows the tally, the debug export the last ones in detail.
function logDrops(items, m) {
  for (const it of items.filter((x) => x.kind === "runa")) {
    const r = RUNA[it.runa];
    addLog(`<b style="color:${E.itemColor(it)}">¡Una runa ${esc(r.name)}!</b> <span class="dim">(${RUNA_TIERS[r.tier].name.toLowerCase()})</span>`, "good");
    if (r.tier !== "comun") toast(`¡Runa ${r.name}!`, "levelup", 3500);
  }
  const gear = items.filter((it) => !it.kind);
  if (!gear.length) return;
  ch.stats.drops ||= {};
  ch.dropLog ||= [];
  for (const it of gear) {
    ch.stats.drops[it.rarity] = (ch.stats.drops[it.rarity] || 0) + 1;
    ch.dropLog.push({ t: Date.now(), zone: S.zone?.id, tier: m.tier, mlvl: m.lvl, rarity: it.rarity, base: it.base, ilvl: it.ilvl, luck: S.F?.luckCombo || 0, good: S.F?.goodLoot || 1 });
  }
  if (ch.dropLog.length > 300) ch.dropLog.splice(0, ch.dropLog.length - 300);
}
function kill(m) {
  const F = S.F, st = stats();
  m.hp = 0;
  ch.stats.kills++;
  m.fallen = true;
  const pen = m.lvl < ch.level - 6 ? 0.3 : 1;
  const D = E.diffOf(ch);
  const mul = rewardMul();
  gainXp(Math.round(m.xp * pen * D.xp * mul * (1 + st.xp / 100) * XP_RATE));
  if (st.killHeal) ch.life = Math.min(st.maxLife, ch.life + st.killHeal);
  const loot = E.lootFor(m, ch, st, D, F.goodLoot || 1, E.streakLuck(F.luckCombo || 0) * (F.freshLoot ?? 1));
  // the Mandingas pays what he promised
  if (m.tier === "boss" && F.boss?.deal === "signed") { const more = E.lootFor(m, ch, st, D, F.goodLoot || 1, E.streakLuck(F.luckCombo || 0) * (F.freshLoot ?? 1)); loot.gold += more.gold; loot.items.push(...more.items); }
  F.ground.gold += Math.round(loot.gold * mul);
  // flash cards (Anki's, La encrucijada's) pay gold only: nothing falls to pick up
  const items = F.review ? [] : mul < 1 ? loot.items.filter(() => Math.random() < mul) : loot.items;
  // good things fall unidentified: you find out what they are by ear (Identificar)
  for (const it of items) if (!it.kind && UNID.has(it.rarity)) it.unid = true;
  m.drops = items;
  logDrops(items, m);
  if (items.some((it) => it.kind === "relic")) addLog(`<b style="color:${RARITY.relic.color}">¡Un Transformador del montón!</b> Cae muy rara vez: en la aldea, en el Montón, convierte cada ${MOUND_STEP} gemas perfectas en un mítico, una mascota o una montura.`, "good");
  F.ground.items.push(...items);
  addLog(`Derrotas a <span class="n-${m.tier}">${esc(m.mask || m.name)}</span>.`, "kill");
  if (m.tier === "boss" && F.boss && m.kind in BOSSES) bossFalls(F, m);
  if (m.weak && !m.mask) addLog(`Vences a tu punto débil «<b>${esc(m.word)}</b>». Sigue acertándola y no volverá.`, "good");
}
// all experience, kills and mastered lines, at this rate (0.5: levels take twice the play they used to)
const XP_RATE = 0.5;
function gainXp(n) {
  ch.xp += n;
  while (ch.xp >= E.xpToNext(ch.level)) {
    ch.xp -= E.xpToNext(ch.level);
    ch.level++;
    attuneTunjo();
    ch.points += 5;
    const st = stats();
    ch.life = st.maxLife; ch.mana = st.maxMana;
    setTimeout(() => { toast(`¡Nivel ${ch.level}! Tienes ${ch.points} puntos por asignar (C).`, "levelup", 3500); sfx.levelup(); }, 300);
  }
}

function showCardResult(r, acc) {
  const F = S.F, card = F.ex.card, res = $("#result");
  // graded cards: you've already seen the back, so go straight on
  if (card.kind === "recall") { renderGroupMastery(); return afterResult(); }
  const anki = `<span class="ankigrade g${F.ease}">Anki: ${EASE[F.ease]} <span class="dim">(${EASE_EN[F.ease]})</span></span>`;
  res.innerHTML = card.kind === "recall" ? `<div class="verdict">${anki}</div>` : `
    <div class="diff">${r.html}</div>
    ${F.mode === "dictation" ? `<div class="you">Escribiste: <span class="typed">${esc(r.typed || "(nada)")}</span></div>` : ""}
    ${nearMissHtml(r)}
    <div class="verdict"><b>${acc < 1 ? Math.min(99, Math.round(acc * 100)) : 100}%</b> ${anki}</div>
    <div class="cardback">${cleanHtml(card.back)}</div>`;
  res.innerHTML += `<div class="row"><button id="againBtn">Volver a oír</button>
    <button id="nextBtn" class="primary">${!cardsLeft() ? "Terminar el repaso" : alive(F).length ? "Siguiente tarjeta" : "Siguiente grupo"} <kbd>Enter</kbd></button></div>`;
  res.hidden = false;
  $("#grades") && ($("#grades").hidden = true);
  $("#attackBtn") && ($("#attackBtn").hidden = true);
  $("#hintBtn") && ($("#hintBtn").disabled = true);
  $("#againBtn").onclick = () => playCard(card, 1);
  $("#nextBtn").onclick = afterResult;
  renderGroupMastery();
  $("#nextBtn").focus();
}
function showResult(r, acc, hit) {
  const F = S.F;
  if (F.review && F.mode === "subj") return showSubjResult(r);
  if (F.review) return showCardResult(r, acc);
  if (F.lesson && F.mode === "recall") return showLessonResult(acc);
  const res = $("#result");
  const pct = acc < 1 ? Math.min(99, Math.round(acc * 100)) : 100;
  const C = E.costs(ch, stats());
  res.innerHTML = `
    <div class="diff">${r.html}</div>
    ${F.mode === "dictation" ? `<div class="you">Escribiste: <span class="typed">${esc(r.typed || "(nada)")}</span></div>` : ""}
    ${nearMissHtml(r)}
    <div class="verdict"><b>${pct}%</b> ${acc >= 1 && (r.strictAcc ?? 1) < 1 ? `En el combate cuenta como perfecta: a tu equipo no le importan las tildes que faltan. Lo que escribiste: <b>${Math.min(99, Math.round(r.strictAcc * 100))}%</b>, así que no cuenta para dominarla.` : acc >= 1 ? "Perfecto." : r.accentMiss && acc >= 0.9 ? `Casi: ${r.accentMiss === 1 ? "falta una tilde" : `fallan ${r.accentMiss} tildes`} (palabras subrayadas).` : acc >= 0.8 ? "Casi." : acc >= 0.5 ? "A medias." : "Se te escapó."}
      <span class="dim">${F.prevBest == null ? "Primera vez que la oyes." : `Tu mejor antes: ${Math.round(F.prevBest * 100)}%.`}</span>
      ${F.masteredNow ? `<span class="mastered">¡Frase dominada! +${F.masteredNow} exp</span>` : ""}
      ${F.lesson ? "" : r.accentsPerfect ? `<span class="accents" title="Todas las palabras bien escritas, con tildes y eñes: el botín de este golpe tiene el doble de probabilidad de ser raro, de conjunto o único.">Tildes perfectas: botín ×2</span>` : ""}
      ${F.mode === "cloze" && F.gapStale ? `<span class="stale" title="Los huecos eran palabras que ya has acertado en huecos muchas veces (${esc(F.gapStale.words.join(", "))}): el botín de este golpe tiene menos probabilidad de ser raro o mejor. Cuanto más repetidas, menos.">Huecos ya sabidos: botín raro ×${F.gapStale.mult.toFixed(2).replace(".", ",")}</span>` : ""}</div>
    ${F.lesson ? `<div class="cardback lback">${lessonBack(F.lesson, S.T.segments[F.si])}</div>` : ""}
    <div class="row">
      <button id="againBtn">Volver a oír</button>
      ${alive(F).length && voiceOk() ? `<button id="castBtn" class="cast" title="Repite la frase en voz alta, imitando cómo suena: cuanto más se parezca, más daño hace el hechizo (V)">Conjurar <span class="cost">${spellCost()} maná</span></button>` : ""}
      ${alive(F).length && voiceOk() && ch.grimoire?.length ? `<button id="grimBtn" class="cast" title="Tus conjuros: pasajes de los tunjos únicos (G)">Grimorio</button>` : ""}
      <button id="explainBtn">Explicar</button>
      <button id="ankiBtn">Tarjeta Anki</button>
      <button class="srcBtn" title="Ver los subtítulos de Netflix y la transcripción de Whisper de esta frase">Netflix / Whisper</button>
      <button class="flagBtn ghost" title="El texto no coincide con el audio. Quita la frase de los juegos y te devuelve la vida y la racha que perdiste en ella.">No coincide</button>
      <button id="nextBtn" class="primary">${alive(F).length ? "Siguiente frase" : "Recoger el botín"} <kbd>Enter</kbd></button>
    </div>
    <div class="explain" id="explainOut" hidden></div>`;
  res.hidden = false;
  renderGroupMastery();
  $("#attackBtn").hidden = true;
  $("#hintBtn").disabled = true;
  $("#slowBtn").disabled = false;
  $("#againBtn").onclick = () => playSeg(F.si, 1);
  $("#nextBtn").onclick = afterResult;
  $("#explainBtn").onclick = explain;
  $("#ankiBtn").onclick = anki;
  $("#castBtn")?.addEventListener("click", castShadow);
  $("#grimBtn")?.addEventListener("click", openGrimoire);
  bindFlag();
  document.querySelectorAll(".srcBtn").forEach((b) => (b.onclick = toggleSources));
  refreshSources();
  $("#nextBtn").focus();
}
function afterResult() {
  const F = S.F;
  if (!F || F.over) return;
  if (F.review && afterAnswer(afterResult)) return;
  if (F.review && !cardsLeft()) return repasoDone();
  if (alive(F).length) return nextExercise();
  if (F.review) return reviewNextPack();
  victory();
}
// The transcript is wrong for this line: flag it, give back what it cost you, move on.
function bindFlag() { document.querySelectorAll(".flagBtn").forEach((b) => (b.onclick = flagCurrent)); }
async function flagCurrent() {
  const F = S.F, si = F.si;
  document.querySelectorAll(".flagBtn").forEach((b) => (b.disabled = true));
  try { await flagLine(S.ep, si); }
  catch (e) { document.querySelectorAll(".flagBtn").forEach((b) => (b.disabled = false)); return toast(e.message); }
  stopAll();
  const b = F.before, st = stats();
  ch.life = Math.min(st.maxLife, Math.max(ch.life, b.life));
  ch.mana = Math.min(st.maxMana, Math.max(ch.mana, b.mana));
  F.combo = Math.max(F.combo, b.combo); ch.streak = F.combo;
  F.ear = Math.max(F.ear || 0, b.ear || 0); ch.earStreak = F.ear;
  if (b.combo >= F.combo) ch.streakLost = b.streakLost; // a flagged line didn't break anything
  ch.stats.lines = b.lines; ch.stats.perfect = b.perfect;
  if (b.boss && F.boss) {
    const now = F.boss, kept = b.boss.stolen.length;
    now.stolen.slice(kept).forEach(giveBack);
    F.boss = { ...b.boss, stolen: now.stolen.slice(0, kept), p2: now.p2, deal: now.deal, dealPending: now.dealPending };
  }
  S.T.segments[si].flagged = true;
  const k = S.lines.indexOf(si);
  if (k >= 0) S.lines.splice(k, 1);
  const cur = F.queue.indexOf(F.ex);
  if (F.checked) { const key = exKey(F.ex); if (b.mastery == null) delete mastery()[key]; else mastery()[key] = b.mastery; }
  F.qi = F.queue.slice(0, Math.max(0, cur)).filter((e) => e.si !== si).length;
  F.queue = F.queue.filter((e) => e.si !== si);
  save(); renderHud(); renderCombo(); renderPanels();
  toast("Frase marcada: no volverá a salir. Puedes corregirla en Escuchar (⚑).", "", 3500);
  if (alive(F).length) nextExercise(); else victory();
}
const contextOf = (si) => S.T.segments.slice(Math.max(0, si - 3), si + 4).map((s) => s.text).join(" ");
// The phrase being worked on (the current exercise): what Explicar, Anki and the death screen use.
// P = { si, text, start, end, explanation } — explanation is filled in once Claude answers.
function currentPhrase() {
  const F = S.F, w = exWords();
  return { si: F.si, text: exText(), start: w[0].s, end: w[w.length - 1].e, get explanation() { return F.explanation; }, set explanation(v) { F.explanation = v; } };
}
// root: where its button and output live (the page, or a dialog over it)
async function explainPhrase(P, still = () => true, fresh = false, root = document) {
  const out = $("#explainOut", root);
  out.hidden = false; out.textContent = "Preguntándole a Claude…";
  $("#explainBtn", root).disabled = true;
  try {
    const { explanation, cached, at } = await api("api/explain", { method: "POST", body: { text: P.text, context: contextOf(P.si), fresh } });
    if (still()) {
      P.explanation = explanation;
      out.innerHTML = md(explanation) + (cached ? `<p class="cachednote">Consulta guardada del ${new Date(at).toLocaleDateString("es")} · <button type="button" class="linkbtn" id="reask">Preguntar de nuevo a Claude</button></p>` : "");
      $("#reask", root)?.addEventListener("click", () => explainPhrase(P, still, true, root));
    }
  } catch (e) { out.textContent = e.message; $("#explainBtn", root).disabled = false; }
}
async function ankiPhrase(P, still = () => true, root = document) {
  const btn = $("#ankiBtn", root);
  btn.disabled = true;
  if (!P.explanation) toast("Buscando la explicación y creando la tarjeta…", "", 15000);
  try {
    const { explanation } = await api("api/anki", { method: "POST", body: { episode: S.ep, start: P.start, end: P.end, text: P.text, context: contextOf(P.si), explanation: P.explanation } });
    if (still()) {
      if (explanation && !P.explanation) { P.explanation = explanation; $("#explainOut", root).hidden = false; $("#explainOut", root).innerHTML = md(explanation); }
      btn.textContent = "Añadida a Anki";
    }
    toast("Añadida a Anki");
  } catch (e) { toast(e.message, "", 4000); btn.disabled = false; }
}
function playPhrase(P, rate = 1) {
  audio.playbackRate = rate; audio.volume = 1;
  audio.currentTime = Math.max(0, P.start - 0.12);
  stopAt = P.end + 0.2;
  audio.play();
}
function explain() { const F = S.F, P = currentPhrase(); explainPhrase(P, () => S.F === F && F.si === P.si); }
function anki() { const F = S.F, P = currentPhrase(); ankiPhrase(P, () => S.F === F && F.si === P.si); }

// All foes down: loot on the ground, then onwards.
function victory() {
  const F = S.F, zp = ch.zones[S.zone.id];
  stopAll();
  F.over = true;
  const wasBoss = F.enc.boss;
  if (wasBoss) {
    if (S.zone.dynamic) {
      const rarity = zp.wins ? "legendario" : "mitico";
      const it = E.randomItem(S.zone.lvl[0] + 2, 0, 1, null, null, 1, rarity);
      it.unid = true;
      const where = stow(it);
      if (!where) F.ground.items.push(it);
      addLog(`<b>¡El Remolino, superado!</b> Lo que más te costaba de este episodio, vencido. Premio: un objeto <span style="color:${E.itemColor(it)}">${RARITY[rarity].name.toLowerCase()}</span> (${where || "en el suelo"}). La próxima vez se arma con lo que te cueste entonces.`, "good");
      zp.wins = (zp.wins || 0) + 1; zp.cleared = true; zp.pack = 0; zp.lines = null;
    } else if (S.zone.endless) { zp.depth = (zp.depth || 0) + 1; zp.maxDepth = Math.max(zp.maxDepth || 0, zp.depth); zp.pack = 0; }
    else { zp.cleared = true; zp.pack = 0; if (S.zone.fights) (zp.done ||= {})[modeOf(S.zone.id)] = true; const nz = E.nextZone(S.zone.id); if (nz) ch.zones[nz.id] = ch.zones[nz.id] || { pack: 0, cleared: false, depth: 0 }; }
  } else if (F.extra) zp.extra = (zp.extra || 0) + 1;
  else zp.pack++;
  ch.gold += F.ground.gold;
  S.loot = { gold: F.ground.gold, items: F.ground.items };
  save();
  const nz = E.nextZone(S.zone.id);
  $("#arena").innerHTML = `
    <div class="victory">
      <h3>${wasBoss ? `${esc(BOSSES[S.zone.boss].name)} ha caído.` : "Grupo derrotado."}</h3>
      ${wasBoss && !S.zone.endless && nz ? `<p>Se abre el camino a <b>${esc(nz.name)}</b>.</p>` : ""}
      ${S.loot.gold ? `<p class="gold">${icon("coins-pile", "#e2b84a")} +${S.loot.gold} de oro</p>` : ""}
      <div class="ground" id="ground"></div>
      <div class="row">
        ${wasBoss && !S.zone.endless
          ? `<button id="goMain" class="primary" data-go="Volver a la aldea"></button><button id="goSkip" class="ghost">Volver sin recoger</button>`
          : `<button id="goMain" class="primary" data-go="Seguir adelante"></button><button id="goSkip" class="ghost">Seguir sin recoger</button><button id="goTown" title="Recoge lo que quepa y vuelve">Volver a la aldea</button>`}
      </div>
    </div>`;
  renderGround();
  celebrateWin({ boss: wasBoss, title: wasBoss ? `${BOSSES[S.zone.boss].name} ha caído.` : S.zone.name,
    sub: wasBoss && !S.zone.endless && nz ? `Se abre el camino a <b>${esc(nz.name)}</b>.` : "", gold: S.loot.gold, items: S.loot.items });
  const home = () => { endCelebration(); S.F = null; show("town"); };
  const next = wasBoss && !S.zone.endless ? home : startEncounter;
  $("#goMain").onclick = () => { endCelebration(); collectThen(next); };
  $("#goSkip").onclick = () => { endCelebration(); next(); };
  $("#goTown")?.addEventListener("click", () => collectThen(home));
  $("#goMain").focus();
}
// What the main button picks up (Opciones): every kind of thing that can be on the ground has a box.
// Each item belongs to exactly one box (pickKey); anything without a box is always picked up, so a new
// kind of loot is never left behind by accident. Unticked boxes are kept in ch.pickup as false.
const PICKUP = [
  { title: "Equipo", hint: "por rareza (sin identificar también: su color ya dice cuál es)", keys: ["low", "normal", "magic", "rare", "set", "unique", "ancestral", "legendario", "mitico", "crafted"].map((k) => [k, RARITY[k].name, RARITY[k].color]) },
  { title: "Pociones", keys: Object.entries(POTIONS).map(([k, p]) => [`p:${k}`, p.name, p.color]) },
  { title: "Gemas", keys: [["g:0", "Fragmentos de gema"], ["g:1", "Gemas"], ["g:2", "Gemas perfectas"]].map(([k, n]) => [k, n, "#e4dfd2"]) },
  { title: "Runas", keys: [["comun", "Runas comunes"], ["media", "Runas medias"], ["alta", "Runas altas"]].map(([k, n]) => [`r:${k}`, n, RUNA_TIERS[k].color]) },
];
const PICKUP_KEYS = new Set(PICKUP.flatMap((g) => g.keys.map(([k]) => k)));
function pickKey(it) {
  if (it.kind === "potion") return `p:${it.potion}`;
  if (it.kind === "gem") return `g:${it.grade}`;
  if (it.kind === "runa") return `r:${RUNA[it.runa].tier}`;
  return it.rarity;
}
// Extra rules for equipment (off unless ticked): picked up if they match, whatever the rarity box says.
const SOCKET_RULES = [1, 2, 3, 4, 5, 6];
// "better than the best you have": where to look for what you have (any of these ticked turns it on)
const BETTER_THAN = [["better", "lo que llevas puesto"], ["better:inv", "lo que llevas en la bolsa"], ["better:stash", "lo que tienes en el alijo"]];
const ruleOn = (k) => ch.pickup?.[k] === true;
// the socket rule is "at least this many": the smallest number chosen (older saves may have several)
const sockMin = () => SOCKET_RULES.find((n) => ruleOn(`s:${n}`)) || 0;
function wanted(it) {
  const k = pickKey(it);
  if (!PICKUP_KEYS.has(k) || ch.pickup?.[k] !== false) return true;
  if (it.kind) return false;
  const least = sockMin();
  if (least && it.sockets >= least) return true;
  return BETTER_THAN.some(([k]) => ruleOn(k)) && isUpgrade(it);
}
// How strong you are, as one number: the hit you deal (with elements and crits) times how much you can
// take (life, armour, dodge, resistances), with a little for the listening help and the finds.
function power(st) {
  const hit = ((st.dmg[0] + st.dmg[1]) / 2 + Object.values(st.elem).reduce((a, v) => a + v, 0)) * (1 + st.crit / 100) * (1 + st.spellDmg / 200);
  const dr = Math.min(0.75, st.armor / (st.armor + 25 + 12 * ch.level));
  const res = (st.resFire + st.resCold + st.resLight + st.resPoison) / 400;
  const tough = st.maxLife / (1 - dr) / (1 - st.dodge / 100) / (1 - st.block / 200) * (1 + res / 2);
  const help = 1 + (st.dmgDictation + st.dmgCloze) / 400 + (st.replayCost + st.hintCost) / 400 + (st.freeReplay + st.typoTol + st.comboStart) / 20 + (st.nearExact + st.comboKeep + st.slowFree) / 10 + (st.leech + st.manaLeech + st.lifeRegen + st.killHeal) / 100;
  return Math.sqrt(hit * tough) * help;
}
// Better than what you wear: you can put it on now, and wearing it (in place of the weaker of the two
// rings) makes you stronger. An empty slot: anything you can wear is better. Unidentified items don't
// count: nobody knows yet what they do.
// The swap is imagined the way equipping really works: a shield takes off a two-handed weapon and a
// two-handed weapon takes off the shield (so, with a bow in your hands, a shield is not "for an empty slot").
function powerWith(it) {
  const base = BASE[it.base], set = ch.swap;
  let best = 0;
  for (const slot of equipTargets(it)) {
    const eq = { ...ch.equip }, w = eq[`weapon${set}`];
    if (base.twoHanded && eq[`off${set}`]) delete eq[`off${set}`];
    if (base.slot === "off" && w && BASE[w.base].twoHanded) delete eq[`weapon${set}`];
    eq[slot] = it;
    best = Math.max(best, power(E.charStats({ ...ch, equip: eq })));
  }
  return best;
}
// Better than the best you have, looking where the ticked boxes say: what you wear (as you are now),
// and anything of the same slot in your bag or your stash that you could put on. With nothing to
// compare against there (an empty slot, no shield in the stash), anything you can wear is better.
// Only what you can put on now counts, on both sides; unidentified items don't (nobody knows yet).
function isUpgrade(it) {
  if (it.kind || it.unid || !E.canEquip(ch, it)) return false;
  // weapons only against weapons of the same kind: a sword against swords and axes (you attack by
  // dictation), a bow against bows and staves (you fill in gaps), since your two sets are often one of each
  const slot = BASE[it.base].slot, kind = BASE[it.base].kind;
  const same = (x) => x && x.id !== it.id && !x.kind && !x.unid && BASE[x.base]?.slot === slot && (slot !== "weapon" || BASE[x.base].kind === kind) && E.canEquip(ch, x);
  let best = 0;
  if (ruleOn("better")) {
    // both weapon sets count as worn: each one's weapon or shield, tried in your hands. An empty slot is
    // empty even with a two-handed weapon in your hands: a shield for later is worth having.
    if (slot === "weapon" || slot === "off") for (const n of [1, 2]) { const x = ch.equip[`${slot}${n}`]; if (same(x)) best = Math.max(best, powerWith(x)); }
    else if (equipTargets(it).every((s) => ch.equip[s])) best = power(stats());
  }
  if (ruleOn("better:inv")) for (const x of ch.inv.filter(same)) best = Math.max(best, powerWith(x));
  if (ruleOn("better:stash")) for (const x of (ch.stash || []).filter(same)) best = Math.max(best, powerWith(x));
  return !best || powerWith(it) > best * 1.001;
}
const pickingAll = () => [...PICKUP_KEYS].every((k) => ch.pickup?.[k] !== false);


function openOptions() {
  const box = ([k, name, col]) => `<label class="pickopt"><input type="checkbox" data-pick="${k}" ${ch.pickup?.[k] === false ? "" : "checked"}><span style="color:${col}">${esc(name)}</span></label>`;
  const d = dialog(`<h3>Opciones</h3>
    <h4>Idioma del juego</h4>
    <p class="langpick" translate="no">${Object.entries(LANGS).map(([k, n]) => `<button data-lang="${k}" class="${lang() === k ? "primary" : "ghost"}">${n}</button>`).join("")}</p>
    <p class="dim">Los menús, los textos y los objetos cambian de idioma; las frases del episodio y lo que escribes, no.</p>
    <h4>Qué recoge el botón de recoger</h4>
    <p class="dim">Al acabar un combate, el botón principal recoge solo lo que marques aquí; lo demás se queda en el suelo, y siempre puedes recogerlo a mano con un clic.</p>
    ${PICKUP.map((g) => `<fieldset class="pickgroup"><legend>${g.title}${g.hint ? ` <span class="dim">· ${g.hint}</span>` : ""}</legend>${g.keys.map(box).join("")}</fieldset>`).join("")}
    <fieldset class="pickgroup rules"><legend>Además, equipo de cualquier rareza que… <span class="dim">· se recoge aunque su rareza no esté marcada</span></legend>
      <div class="pickrule"><span>tenga al menos estos huecos:</span>${[0, ...SOCKET_RULES].map((n) => `<label class="pickopt"><input type="radio" name="sockmin" data-sock="${n}" ${sockMin() === n ? "checked" : ""}><span>${n || "da igual"}</span></label>`).join("")}</div>
      <div class="pickrule"><span>sea mejor que lo mejor que tengas en:</span>${BETTER_THAN.map(([k, name]) => `<label class="pickopt"><input type="checkbox" data-rule="${k}" ${ruleOn(k) ? "checked" : ""}><span>${name}</span></label>`).join("")}</div>
      <p class="dim pickhint">Mejor quiere decir que te lo puedes poner ya y, puesto, te hace más fuerte (daño y aguante, y un poco las ayudas para escuchar). Con varias casillas, tiene que ganarle a todo lo de esos sitios. Lo puesto incluye tus dos juegos de armas (I y II), y un arma solo se compara con las de su clase: cuerpo a cuerpo con cuerpo a cuerpo, a distancia con a distancia. Lo que está sin identificar no cuenta: aún no se sabe qué hace.</p>
    </fieldset>
    <div class="row"><button id="pickAll" class="ghost">Marcarlo todo</button><button id="pickNone" class="ghost">No marcar nada</button><button id="optClose" class="primary">Listo</button></div>`, { cls: "optdlg" });
  d.querySelectorAll("[data-lang]").forEach((b) => (b.onclick = () => { if (b.dataset.lang !== lang()) setLang(b.dataset.lang); }));
  const sync = () => { save(); renderGround(); };
  d.querySelectorAll("[data-pick]").forEach((c) => (c.onchange = () => {
    ch.pickup ||= {};
    if (c.checked) delete ch.pickup[c.dataset.pick]; else ch.pickup[c.dataset.pick] = false;
    sync();
  }));
  d.querySelectorAll("[data-sock]").forEach((c) => (c.onchange = () => {
    ch.pickup ||= {};
    for (const n of SOCKET_RULES) delete ch.pickup[`s:${n}`];
    if (+c.dataset.sock) ch.pickup[`s:${c.dataset.sock}`] = true;
    sync();
  }));
  d.querySelectorAll("[data-rule]").forEach((c) => (c.onchange = () => {
    ch.pickup ||= {};
    if (c.checked) ch.pickup[c.dataset.rule] = true; else delete ch.pickup[c.dataset.rule];
    sync();
  }));
  const rules = () => Object.fromEntries(Object.entries(ch.pickup || {}).filter(([, v]) => v === true));
  const all = (on) => { d.querySelectorAll("[data-pick]").forEach((c) => { c.checked = on; }); ch.pickup = { ...rules(), ...(on ? {} : Object.fromEntries([...PICKUP_KEYS].map((k) => [k, false]))) }; sync(); };
  d.querySelector("#pickAll").onclick = () => all(true);
  d.querySelector("#pickNone").onclick = () => all(false);
  d.querySelector("#optClose").onclick = () => closeDialog();
}

// The main button after a fight: pick up what you chose (Opciones), then go on. If something you
// wanted doesn't fit, say so and stay; pressing again goes on and leaves it.
function collectThen(go) {
  if (S.loot.items.some(wanted) && !S.loot.warned) {
    for (const it of S.loot.items.filter(wanted)) pickUp(it.id, true);
    if (S.loot.items.some(wanted)) S.loot.warned = true;
    renderGround();
    if (S.loot.warned) {
      toast("El inventario está lleno: algo se quedó en el suelo. Pulsa otra vez para seguir sin ello.", "", 4000);
      return;
    }
  }
  go();
}
function renderGround() {
  const g = $("#ground");
  if (!g) return;
  g.innerHTML = S.loot.items.length
    ? S.loot.items.map((it) => `<button class="drop r-${it.rarity}${BEAM_RANK[it.rarity] ? " beam" : ""}${wanted(it) ? "" : " unwanted"}" data-id="${it.id}" ${wanted(it) ? "" : `title="No lo recoge el botón (Opciones). Clic para recogerlo."`} style="color:${E.itemColor(it)};--c:${E.itemColor(it)}">${itemIco(it)} ${esc(E.itemName(it))}${it.unid ? ` <span class="unidtag">sin identificar</span>` : ""}${wanted(it) ? "" : ` <span class="skiptag">no se recoge</span>`}</button>`).join("")
    : `<span class="dim">${S.loot.gold ? "No hay nada más en el suelo." : "Nada en el suelo."}</span>`;
  g.querySelectorAll(".drop").forEach((b) => (b.onclick = () => { pickUp(b.dataset.id); renderGround(); }));
  // the main button says whether it picks things up; the skip button only matters while there's loot
  const main = $("#goMain"), want = S.loot.items.filter(wanted).length, left = want > 0;
  const what = want === S.loot.items.length && pickingAll() ? "Recogerlo todo" : "Recoger lo elegido";
  if (main) main.innerHTML = `${left && !S.loot.warned ? `${what} y ${main.dataset.go.toLowerCase()}` : main.dataset.go} <kbd>Enter</kbd>`;
  if ($("#goSkip")) $("#goSkip").hidden = !left || !!S.loot.warned;
  main?.classList.toggle("hasloot", left && !S.loot.warned);
  // a way to the options from the loot itself
  if (main && !$("#pickOpts")) main.parentElement.insertAdjacentHTML("beforeend", `<button id="pickOpts" class="linkbtn" title="Elegir qué recoge el botón">Qué recoger…</button>`);
  $("#pickOpts") && ($("#pickOpts").onclick = openOptions);
}
function pickUp(id, quiet) {
  const i = S.loot.items.findIndex((x) => x.id === id);
  const it = S.loot.items[i];
  if (it.kind === "potion" && ch.belt.length < stats().beltSlots) ch.belt.push(it);
  else if (ch.inv.length < INV_SIZE) ch.inv.push(it);
  else { if (!quiet) toast("El inventario está lleno"); return; }
  S.loot.items.splice(i, 1);
  tip.hidden = true;
  if (["unique", "set", "ancestral", "legendario", "mitico", "tunjo"].includes(it.rarity) && !it.unid) toast(`¡${E.itemName(it)}!`, `r-${it.rarity}`, 3000);
  save(); renderHud(); renderPanels();
}

function die(r, acc) {
  ch.streak = 0; ch.streakLost = 0; ch.earStreak = 0;
  stopAll();
  // keep the phrase that finished you off, to look at on the death screen
  const F = S.F;
  if (F.review) {
    const c = F.ex.card;
    S.death = { card: c, r, acc, mode: F.mode, ease: F.ease, killers: [...new Set(alive(F).map((m) => m.mask || m.name))] };
    S.review = null;
  } else {
  const P = currentPhrase();
  S.death = { si: P.si, text: P.text, start: P.start, end: P.end, explanation: F.explanation, r, acc, mode: F.mode,
    full: S.T.segments[F.si].text, killers: [...new Set(alive(F).map((m) => m.mask || m.name))] };
  }
  const lost = Math.round(ch.gold * 0.1);
  ch.gold -= lost;
  ch.stats.deaths++;
  const st = stats();
  ch.life = st.maxLife; ch.mana = st.maxMana;
  S.deathGold = lost;
  save();
  show("dead");
}
function deathPhraseHtml(P) {
  if (!P) return "";
  if (P.card?.kind === "subj") {
    const c = P.card;
    return `<div class="deathphrase">
      <h3>La frase que te venció${P.killers.length ? ` <span class="dim">· ${esc(P.killers.join(", "))}</span>` : ""}</h3>
      <p class="subjen">${esc(c.en)}</p>${subjVerdictHtml(c, P.r)}
    </div>`;
  }
  if (P.card) {
    const c = P.card;
    return `<div class="deathphrase">
      <h3>La tarjeta que te venció${P.killers.length ? ` <span class="dim">· ${esc(P.killers.join(", "))}</span>` : ""}</h3>
      ${c.kind === "recall" ? `<div class="cardfront ${c.script === "latin" ? "latin" : "tib"}">${cleanHtml(c.front)}</div>` : `<div class="diff">${P.r.html}</div>${P.mode === "dictation" ? `<div class="you">Escribiste: <span class="typed">${esc(P.r.typed || "(nada)")}</span></div>` : ""}${nearMissHtml(P.r)}`}
      <div class="cardback">${cleanHtml(c.back)}</div>
      <p class="dim">Anki: ${EASE[P.ease]} (guardado). El resto de tarjetas te espera en la cripta.</p>
      <div class="row"><button id="deathPlay">▶ Oír</button><button id="deathSlow">Despacio</button></div>
    </div>`;
  }
  const pct = P.acc < 1 ? Math.min(99, Math.round(P.acc * 100)) : 100;
  return `<div class="deathphrase">
    <h3>La frase que te venció${P.killers.length ? ` <span class="dim">· ${esc(P.killers.join(", "))}</span>` : ""}</h3>
    <div class="diff">${P.r.html}</div>
    ${P.mode === "dictation" ? `<div class="you">Escribiste: <span class="typed">${esc(P.r.typed || "(nada)")}</span></div>` : ""}
    ${nearMissHtml(P.r)}
    <div class="verdict"><b>${pct}%</b>${P.r.missed ? ` <span class="dim">${P.r.missed} ${P.r.missed === 1 ? "palabra se te escapó" : "palabras se te escaparon"}</span>` : ""}</div>
    ${P.full && P.full.trim() !== P.text.trim() ? `<div class="ans full"><span class="dim">La línea completa:</span> ${esc(P.full)}</div>` : ""}
    <div class="row">
      <button id="deathPlay">▶ Oír</button>
      <button id="deathSlow">Despacio</button>
      <button id="explainBtn">Explicar</button>
      <button id="ankiBtn">Tarjeta Anki</button>
      <button class="srcBtn" title="Ver los subtítulos de Netflix y la transcripción de Whisper de esta frase">Netflix / Whisper</button>
    </div>
    <div class="explain" id="explainOut" hidden></div>
  </div>`;
}
function renderDead() {
  screen.innerHTML = `
    <section class="dead">
      ${icon("death-skull", "#a33", "huge")}
      <h2>Has caído</h2>
      <p>Pierdes ${S.deathGold} de oro. Tu equipo sigue contigo, y el grupo te espera donde lo dejaste.</p>
      ${deathPhraseHtml(S.death)}
      <button id="revive" class="primary">Despertar en la aldea <kbd>Enter</kbd></button>
    </section>`;
  S.F = null;
  const P = S.death;
  if (P?.card?.kind === "subj") { /* nothing to play */ }
  else if (P?.card) {
    $("#deathPlay").onclick = () => { playCard(P.card, 1); $("#revive").focus(); };
    $("#deathSlow").onclick = () => { playCard(P.card, 0.75); $("#revive").focus(); };
  } else if (P) {
    $("#deathPlay").onclick = () => { playPhrase(P, 1); $("#revive").focus(); };
    $("#deathSlow").onclick = () => { playPhrase(P, 0.7); $("#revive").focus(); };
    $("#explainBtn").onclick = () => explainPhrase(P, () => S.death === P);
    $("#ankiBtn").onclick = () => ankiPhrase(P, () => S.death === P);
    if (P.explanation) { $("#explainOut").hidden = false; $("#explainOut").innerHTML = md(P.explanation); }
    document.querySelectorAll(".srcBtn").forEach((b) => (b.onclick = () => { toggleSources(); $("#revive").focus(); }));
    refreshSources();
  }
  $("#revive").onclick = () => show("town");
  $("#revive").focus();
}

// The words you keep missing in this episode: they turn up as monsters.
function weakSpotsHtml() {
  const L = weakList().slice(0, 14);
  if (!L.length) return "";
  return `<section class="weakspots"><h3>Tus puntos débiles</h3><p class="dim">Palabras que fallas más de lo que aciertas. Aparecen como monstruos con su nombre; las peores, como únicos.</p>
    <div class="wchips">${L.map((x) => `<span class="wchip ${x.leech ? "leech" : ""}" title="Fallada ${x.miss}, acertada ${x.hit}">${esc(x.w)} <i>${x.miss}/${x.hit}</i></span>`).join("")}</div></section>`;
}

// ---------- dialogs ----------
function dialog(html, { cls = "", onClose } = {}) {
  closeDialog();
  const d = h(`<div class="modal"><div class="dialog ${cls}" role="dialog" aria-modal="true">${html}</div></div>`);
  document.body.append(d);
  S.dialog = { el: d, onClose };
  d.addEventListener("mousedown", (e) => { if (e.target === d) closeDialog(); });
  return d.firstElementChild;
}
function closeDialog() {
  if (!S.dialog) return;
  const { el, onClose } = S.dialog;
  S.dialog = null;
  stopRecording();
  el.remove();
  stopAll();
  onClose?.();
  focusInput();
}
function pay(n) {
  if (ch.gold < n) { toast("No te alcanza el oro"); return false; }
  ch.gold -= n;
  sfx.coin();
  save(); renderHud();
  if (S.view === "town") renderTown();
  return true;
}
// A bag with room: the inventory, else the stash.
function stow(it) {
  const bag = ch.inv.length < INV_SIZE ? ch.inv : ch.stash.length < STASH_SIZE ? ch.stash : null;
  if (!bag) return null;
  bag.push(it);
  save(); renderPanels();
  return bag === ch.inv ? "a tu bolsa" : "al alijo";
}

// ---------- trials: hear a clip, write it ----------
// For identifying items and for the casetes. clip: { start, end, words, rate }.
// onResult(r) returns HTML for what happened, and optionally { again } for a retry button.
const segClip = (si) => { const s = S.T.segments[si], w = s.words; return { si, start: w[0].s ?? s.start, end: w[w.length - 1].e ?? s.end, words: w }; };
function pickLine(minW, maxW, list = S.lines) {
  const ok = list.filter((si) => { const n = S.T.segments[si].words.length; return n >= minW && n <= maxW; });
  return E.pick(ok.length ? ok : list);
}
// onFlag(): the line was marked as not matching its audio (single-line clips only)
// maxPlays: how many times the clip may be heard before answering (the first, automatic, counts); after, freely
function trial({ title, sub = "", clip, buttons = [], onResult, onFlag, maxPlays = 0 }) {
  const box = dialog(`
    <h3>${title}</h3>${sub ? `<p class="dim">${sub}</p>` : ""}
    <div class="excontrols">
      <button class="playbtn" id="tPlay" title="Escuchar (Tab)"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></button>
      <button id="tSlow" title="Escuchar despacio (Mayús+Tab)">Despacio</button>${maxPlays ? `<span class="dim" id="tLeft">Puedes escucharla ${maxPlays} veces</span>` : ""}
      ${buttons.map((b, i) => `<button data-tb="${i}" title="${esc(b.title || "")}">${b.label}${b.cost != null ? ` <span class="cost">${b.cost} de oro</span>` : ""}</button>`).join("")}
    </div>
    <div class="skeleton" id="tSkel" hidden></div>
    <textarea id="tAnswer" rows="2" placeholder="Escribe lo que oíste y pulsa Enter" autocomplete="off" autocapitalize="off" spellcheck="false"></textarea>
    <div class="row" id="tRow"><button id="tCheck" class="primary">Comprobar <kbd>Enter</kbd></button><button id="tClose" class="ghost">Cerrar</button></div>
    <div class="result" id="tRes" hidden></div>`, { cls: "trial" });
  const T = { done: false, hinted: false };
  let plays = 0;
  const left = () => box.querySelector("#tLeft");
  const play = (slow) => {
    if (maxPlays && !T.done) {
      if (plays >= maxPlays) return toast("Ya no quedan escuchas: escribe lo que oíste");
      plays++;
      const n = maxPlays - plays;
      if (left()) left().textContent = n === 1 ? "Te queda 1 escucha" : n ? `Te quedan ${n} escuchas` : "No quedan escuchas";
      if (!n) box.querySelectorAll("#tPlay, #tSlow").forEach((x) => (x.disabled = true));
    }
    playRange(clip.start, clip.end, (clip.rate || 1) * (slow ? 0.75 : 1));
  };
  const ans = box.querySelector("#tAnswer");
  T.skeleton = () => {
    T.hinted = true;
    const sk = box.querySelector("#tSkel");
    sk.innerHTML = clip.words.map((w) => { const b = bare(w.w); return `<span>${esc(b[0] || "")}${"_".repeat(Math.max(0, b.length - 1))}</span>`; }).join("");
    sk.hidden = false;
    ans.focus();
  };
  // end the trial with a message instead of a check (e.g. Don Eusebio did it for you)
  T.finish = (html) => {
    T.done = true;
    ans.disabled = true;
    box.querySelectorAll("[data-tb]").forEach((b) => (b.disabled = true));
    box.querySelector("#tCheck").remove();
    const res = box.querySelector("#tRes");
    res.innerHTML = html;
    res.hidden = false;
    box.querySelectorAll("#tPlay, #tSlow").forEach((x) => (x.disabled = false));
    if (left()) left().textContent = "";
    box.querySelector("#tClose").textContent = "Cerrar";
    box.querySelector("#tClose").className = "primary";
    box.querySelector("#tClose").focus();
  };
  const check = () => {
    if (T.done) return;
    if (!ans.value.trim()) return toast("Escribe lo que oíste");
    const r = scoreDictation(clip.words, ans.value, { extraTol: stats().typoTol });
    const out = onResult(r, T);
    const pct = r.acc < 1 ? Math.min(99, Math.round(r.acc * 100)) : 100;
    const html = typeof out === "string" ? out : out.html;
    T.finish(`<div class="diff">${r.html}</div><div class="you">Escribiste: <span class="typed">${esc(r.typed || "(nada)")}</span></div>${nearMissHtml(r)}
      <div class="verdict"><b>${pct}%</b></div>${html}`);
    // what the phrase means, a card for it, or "this isn't what's said", now that it's been answered
    if (clip.si != null && S.T?.segments[clip.si]) {
      const P = { si: clip.si, text: clip.words.map((w) => w.w).join(" "), start: clip.start, end: clip.end, explanation: null };
      const row = box.querySelector("#tRow"), still = () => box.isConnected;
      const back = () => (box.querySelector("#tAgain") || box.querySelector("#tClose")).focus(); // Enter keeps going to the retry
      const ex = h(`<button id="explainBtn">Explicar</button>`), an = h(`<button id="ankiBtn">Tarjeta Anki</button>`);
      row.append(ex, an);
      box.querySelector("#tRes").append(h(`<div class="explain" id="explainOut" hidden></div>`));
      ex.onclick = () => { explainPhrase(P, still, false, box); back(); };
      an.onclick = () => { ankiPhrase(P, still, box); back(); };
      // one line only: in a stretch of several there's no telling which one is off
      if (clip.words === S.T.segments[clip.si].words) {
        const fl = h(`<button class="flagBtn ghost" title="El texto no coincide con el audio. Quita la frase de los juegos.">No coincide</button>`);
        row.append(fl);
        fl.onclick = async () => {
          fl.disabled = true;
          try { await flagLine(S.ep, clip.si); } catch (e) { fl.disabled = false; return toast(e.message); }
          S.T.segments[clip.si].flagged = true;
          const k = S.lines.indexOf(clip.si);
          if (k >= 0) S.lines.splice(k, 1);
          save();
          toast("Frase marcada: no volverá a salir. Puedes corregirla en Escuchar (⚑).", "", 3500);
          onFlag?.(r);
        };
      }
    }
    if (out.again) {
      // a retry is what you usually want next, so Enter goes there; Cerrar steps back
      const b = h(`<button id="tAgain" class="primary">${out.againLabel || "Otra frase"} <kbd>Enter</kbd></button>`);
      box.querySelector("#tRow").prepend(b);
      b.onclick = out.again;
      box.querySelector("#tClose").className = "ghost";
      b.focus();
    }
  };
  box.querySelector("#tPlay").onclick = () => { play(false); ans.focus(); };
  box.querySelector("#tSlow").onclick = () => { play(true); ans.focus(); };
  box.querySelector("#tCheck").onclick = check;
  box.querySelector("#tClose").onclick = closeDialog;
  buttons.forEach((b, i) => (box.querySelector(`[data-tb="${i}"]`).onclick = () => { if (!T.done) b.run(T); }));
  box.addEventListener("keydown", (e) => {
    if (e.key === "Tab") { e.preventDefault(); play(e.shiftKey); return; }
    if (e.key === "Enter" && !e.shiftKey && e.target === ans) { e.preventDefault(); check(); }
  });
  ans.focus();
  quiet().then(() => { if (!T.done && box.isConnected && audio.paused) play(false); });
  return T;
}

// ---------- identifying: good drops come unidentified ----------
// Each one carries a short line; write it (90%+) and you learn what the item is. Don Eusebio, the
// village's old know-it-all, gives you the first letters for gold; nobody identifies it for you.
const ID_WORDS = { rare: [4, 8], set: [6, 11], unique: [8, 15], ancestral: [9, 16], legendario: [10, 18], mitico: [12, 22] };
function revealItem(it) {
  delete it.unid; delete it.idLine;
  ch.stats.identified = (ch.stats.identified || 0) + 1;
  save(); renderPanels(); if (S.view === "town" && S.townTab === "stash") renderTown(); // the stash shows the identify button's count
  sfx.identify();
  setTimeout(() => sfx.drop(it.rarity), 350);
  return `<div class="idreveal" style="--c:${E.itemColor(it)}">${tooltipHtml(it, false)}</div>`;
}
// Identifying one after another (the inventory's button, in the village): the bag first, then the stash.
const unidList = () => [...ch.inv, ...ch.stash].filter((x) => x.unid);
const unidCount = () => unidList().length;
const nextUnid = () => unidList()[0] || null;
// chain: after one is right, Siguiente (Enter) opens the next
function identify(id, chain = false) {
  const f = findItem(id);
  if (!f?.it.unid) return;
  closeMenu();
  const it = f.it;
  if (!it.idLine || it.idLine.ep !== S.ep || !S.lines.includes(it.idLine.si)) { it.idLine = { ep: S.ep, si: pickLine(...(ID_WORDS[it.rarity] || [4, 9])) }; save(); }
  const hintPrice = 15 + it.ilvl * 4;
  trial({
    title: `Identificar <span style="color:${E.itemColor(it)}">${esc(E.itemName(it))}</span>`,
    sub: "Escribe la frase que oyes (90% o más) y sabrás qué es. Puedes oírla las veces que quieras.",
    clip: segClip(it.idLine.si),
    buttons: [
      { label: "Pista de Don Eusebio", cost: hintPrice, title: "Te dice la primera letra de cada palabra",
        run: (T) => { if (!T.hinted && pay(hintPrice)) T.skeleton(); } },
    ],
    onFlag: (r) => { it.idLine = null; save(); if (r.acc < 0.9) identify(id); },
    onResult: (r) => {
      if (r.acc >= 0.9) {
        const html = `<p class="good">Lo entendiste: ya sabes qué es.</p>${revealItem(it)}`, next = chain && nextUnid();
        if (!next) return html;
        const n = unidCount();
        return { html: html + `<p class="dim">${n === 1 ? "Te queda 1 sin identificar." : `Te quedan ${n} sin identificar.`}</p>`, again: () => identify(next.id, true), againLabel: "Siguiente" };
      }
      it.idLine = null; save(); // the next try is a different line
      return { html: `<p>No basta para saber qué es (hace falta un 90%). La próxima vez, otra frase.</p>`, again: () => identify(id, chain) };
    },
  });
}

// ---------- the tunjo: Doña Remedios' one sentence a day ----------
// A tunjo que habla costs about eight hours of play (its price follows your level, as your gold does)
// and there's one a day: after you buy one, the next is 24 hours away. It says one whole sentence from
// anywhere in the episode, and you get one answer. Every word right (a slip of spelling or an accent
// is forgiven) and a rainbow item falls that comes from nowhere else, one you don't have yet
// (data.js TUNJO_ITEMS; listed under the buy button). Wrong, and the gold and the day are gone.
const TUNJO_WAIT = 24 * 3600 * 1000;
const tunjoPrice = () => Math.round(((10 + 6 * ch.level) * 4000) / 1000) * 1000;
const tunjoWait = () => Math.max(0, (ch.tunjoNext || 0) - Date.now());
const hoursLeft = (ms) => { const m = Math.ceil(ms / 60000), h = Math.floor(m / 60); return h ? `${h} h ${m % 60} min` : `${m} min`; };
// a whole sentence: starts like one, ends like one, and is long enough to be worth a day
function tunjoLine() {
  const seg = (si) => S.T.segments[si];
  const whole = (si) => { const t = seg(si).text.trim(), n = seg(si).words.length; return n >= 6 && n <= 24 && /^[¿¡"«]?[A-ZÁÉÍÓÚÑ]/.test(t) && /[.?!…]["»]?$/.test(t); };
  const ok = S.lines.filter(whole);
  const long = S.lines.filter((si) => seg(si).words.length >= 6);
  return E.pick(ok.length ? ok : long.length ? long : S.lines);
}
// what you've won so far, by item id: a copy of each (Recuperar gives it back if it's sold, lost or tossed)
const tunjoBook = () => (ch.tunjoBook ||= {});
const ownsNow = (id) => [...ch.inv, ...ch.stash, ...Object.values(ch.equip)].some((x) => x?.tunjo === id);
function tunjoPrize() {
  const book = tunjoBook(), band = bandOf(ch.level), left = tunjoLeft();
  // all twelve still growing: one of them again, with other properties, its thirty levels from now (the collection keeps it)
  const def = E.pick(left.length ? left : TUNJO_ITEMS), it = E.makeTunjoItem(def, ch.level + 2);
  it.band = band;
  const old = book[def.id];
  if (!old || !old.band || old.band[1] <= band[1]) book[def.id] = JSON.parse(JSON.stringify(it));
  return { it, again: !!old && (old.band?.[1] ?? 0) >= ch.level };
}
// what the tunjo can still give you
// (the ones you don't have, and the ones whose thirty levels you've already left behind)
const tunjoLeft = () => { const book = tunjoBook(); return TUNJO_ITEMS.filter((d) => !book[d.id] || (book[d.id].band?.[1] ?? 0) < ch.level); };
function buyTunjo() {
  const price = tunjoPrice();
  if (tunjoWait()) return toast(`El próximo tunjo, en ${hoursLeft(tunjoWait())}`);
  if (ch.inv.length >= INV_SIZE && ch.stash.length >= STASH_SIZE) return toast("No te cabe nada más");
  if (!S.lines.length) return toast("Este episodio no tiene frases para el tunjo");
  if (!pay(price)) return;
  ch.tunjoNext = Date.now() + TUNJO_WAIT;
  ch.stats.casetes = (ch.stats.casetes || 0) + 1;
  save(); renderHud();
  const clip = segClip(tunjoLine());
  sfx.drop("mitico");
  let gave = false;
  trial({
    title: `<span class="rainbow">Tunjo que habla</span>`,
    sub: "Una frase entera: la oyes tres veces como mucho (despacio también cuenta) y tienes una sola respuesta. Cada palabra bien (una letra o una tilde se perdonan) y cae un objeto del arcoíris.",
    clip, maxPlays: 3,
    // the line didn't match its audio: the gold back, and the tunjo can be bought again now
    onFlag: () => { if (!gave) { ch.gold += price; ch.tunjoNext = 0; save(); renderHud(); renderPanels(); if (S.view === "town") renderTown(); toast(`Doña Remedios te devuelve ${price.toLocaleString("es")} de oro, y puedes probar otro tunjo.`, "", 4000); } },
    onResult: (r) => {
      const right = r.missed === 0 && !/class="extra"/.test(r.html);
      if (S.view === "town") setTimeout(renderTown, 0);
      if (!right) return `<p>El tunjo se calla. Mañana Doña Remedios tendrá otro.</p>`;
      gave = true;
      const { it, again } = tunjoPrize(), where = stow(it), spell = CFG.online ? null : learnSpell(clip);
      setTimeout(() => sfx.drop("mitico"), 300);
      return `<p class="good">¡Lo entendiste entero! Al tunjo le salen colores, y a sus pies:</p>
        <div class="idreveal tunjo" style="--c:${RARITY.tunjo.color}">${tooltipHtml(it, false)}</div>
        <p class="dim">${again ? "Ya lo tenías: este sale con otras propiedades y sus treinta niveles desde ahora. " : `Nuevo, para los ${bandText(it.band)}. `}Va ${where || "a la Colección (no te cabía)"}.${spell ? ` Y la frase queda en tu grimorio: <b>${esc(spell.name)}</b>.` : ""}</p>`;
    },
  });
}
// Under the tunjo's buy button: what it can give. One of the twelve you don't have yet (all twelve once you
// have them all, made again for your level).
function tunjoPrizes() {
  const book = tunjoBook(), band = bandOf(ch.level), left = new Set(tunjoLeft().map((d) => d.id)), all = !left.size;
  return `<h3 class="rwtitle">El premio: uno de estos</h3>
    <p class="dim">Un objeto del arcoíris crece contigo durante treinta niveles desde el que tienes al ganarlo, y luego se queda como está: el que ganes ahora, ${bandText(band)}. ${all ? "Todos los tuyos siguen creciendo: el tunjo te da uno de los doce otra vez, con otras propiedades y sus treinta niveles desde ahora." : left.size === 1 ? "Solo te falta uno (o uno de los tuyos ya dejó de crecer): si aciertas, es ese." : `Si aciertas, te toca al azar uno de estos ${left.size}: los que no tienes y los que ya dejaron de crecer.`}</p>
    <div class="tprizes">${TUNJO_ITEMS.map((d) => {
      const it = book[d.id], can = all || left.has(d.id), show = it || { base: d.look, rarity: "tunjo", tunjo: d.id, look: d.look, name: d.name };
      const note = can ? (it?.band ? `puede tocarte (el tuyo dejó de crecer en el ${it.band[1]})` : "puede tocarte") : `ya lo tienes (${it.band[0]}–${it.band[1]})`;
      const back = it && !ownsNow(d.id) ? `<button class="small" data-tback="${d.id}" title="Lo vendiste, lo tiraste o lo perdiste: te lo devuelve">Recuperar</button>` : "";
      return `<div class="tprize${can ? " can" : " have"}" title="${esc(d.name)} · ${note}">${itemIco(show)}<b class="${can ? "rainbow" : ""}">${esc(d.name)}</b><span class="dim small">${esc(SLOTS[BASE[d.look].slot])} · ${note}</span>${back}</div>`;
    }).join("")}</div>`;
}
// A rainbow item's band: thirty levels from the one you won it at (at 51: 51–80). It grows with you
// through them, then stays as it was at the last. (Bands were fifty levels once: those are cut to thirty.)
const BAND = 30;
const bandOf = (L) => [L, L + BAND - 1];
const bandText = (b) => `niveles ${b[0]}–${b[1]}`;
// The rainbow items grow with you inside their band: each is made again at your level (or its band's
// last, once you're past it; its seed keeps its character), keeping its place, its sockets and the
// gems in them. On load and on every level up.
function attuneTunjo() {
  const all = [...Object.values(ch.equip), ...ch.inv, ...ch.stash, ...Object.values(ch.tunjoBook || {})];
  let changed = false;
  for (const it of all) {
    if (it?.rarity !== "tunjo") continue;
    if (it.band && it.band[1] - it.band[0] >= BAND) it.band = [it.band[0], it.band[0] + BAND - 1];
    const band = it.band || bandOf(ch.level), lvl = Math.min(Math.max(ch.level, band[0]), band[1]) + 2;
    if (it.ilvl === lvl && it.seed != null && it.lreq === 1 && it.band) continue;
    const def = TUNJO_ITEMS.find((d) => d.id === it.tunjo);
    if (!def) continue;
    if (it.seed == null) it.seed = [...String(it.id)].reduce((h, c) => (Math.imul(h, 31) + c.charCodeAt(0)) | 0, 7) >>> 0;
    const fresh = E.makeTunjoItem(def, lvl, it.seed), keep = { id: it.id, band, gems: it.gems || [], sockets: Math.max(it.sockets || 0, (it.gems || []).length) };
    for (const k of Object.keys(it)) delete it[k];
    Object.assign(it, fresh, keep);
    changed = true;
  }
  if (changed) save();
  return changed;
}
function tunjoBack(id) {
  const it = tunjoBook()[id];
  if (!it || ownsNow(id)) return;
  const copy = JSON.parse(JSON.stringify(it));
  copy.id = Math.random().toString(36).slice(2, 10);
  if (!stow(copy)) return toast("No te cabe: haz sitio en la bolsa o el alijo");
  toast(`${it.name}, de vuelta contigo`, "r-tunjo", 2500);
  renderTown();
}

// ---------- shadowing as spellcasting ----------
// After a line, say it out loud the way it sounds. Your voice is transcribed on this computer
// (whisper.cpp) and compared with the line: the closer, the harder the spell hits. No retaliation:
// the monsters are too busy listening. Once per line.
const voiceOk = () => !CFG.online && !!(navigator.mediaDevices?.getUserMedia && window.MediaRecorder);
const spellCost = () => Math.round(6 + ch.level * 0.8);
const grimCost = () => Math.round(15 + ch.level * 1.5);
let rec = null;
function stopRecording() { rec?.stop(); }
async function recordVoice(maxSec) {
  stopAll();
  const stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } });
  const mr = new MediaRecorder(stream);
  const parts = [];
  mr.ondataavailable = (e) => e.data.size && parts.push(e.data);
  const done = new Promise((res) => (mr.onstop = () => { stream.getTracks().forEach((t) => t.stop()); res(new Blob(parts, { type: mr.mimeType })); }));
  mr.start();
  rec = { stop: () => mr.state !== "inactive" && mr.stop() };
  const timer = setTimeout(() => rec?.stop(), maxSec * 1000);
  const blob = await done;
  clearTimeout(timer);
  rec = null;
  return blob;
}
async function transcribeVoice(blob) {
  const r = await fetch("api/shadow", { method: "POST", body: blob, headers: { "Content-Type": blob.type || "application/octet-stream" } });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(j.error || `Error ${r.status}`);
  return j.text || "";
}
// Record, transcribe, score. btn shows what's happening. Returns { r, text } or null.
async function shadow(words, btn, { maxSec }) {
  const label = btn.innerHTML;
  btn.classList.add("rec");
  btn.innerHTML = `<i class="recdot"></i> Habla ahora… <kbd>V</kbd> para terminar`;
  let blob;
  try { blob = await recordVoice(maxSec); }
  catch (e) { btn.classList.remove("rec"); btn.innerHTML = label; toast(`No puedo usar el micrófono (${e.message})`); return null; }
  btn.classList.remove("rec");
  btn.innerHTML = "Escuchando tu voz…";
  btn.disabled = true;
  try {
    const text = await transcribeVoice(blob);
    return { text, r: scoreDictation(words, text, { extraTol: 1 }) };
  } catch (e) {
    toast(e.message);
    btn.disabled = false; btn.innerHTML = label;
    return null;
  }
}
// The spell itself: weapon damage boosted by energy and streak, times how close your voice was.
// Below 40% it fizzles; 98%+ is a critical.
async function spellHit(F, score, { all = false, mult = 1 } = {}) {
  const st = stats();
  const q = Math.max(0, (score - 0.4) / 0.6);
  const crit = score >= 0.98;
  const power = ((st.dmg[0] + st.dmg[1]) / 2) * (1.1 + st.ene / 60) * (1 + 0.1 * Math.min(F.combo, 10)) * mult;
  const dmg = Math.round(power * q * q * (crit ? 1.5 : 1));
  const targets = all ? alive(F) : [currentTarget()];
  const hits = [];
  if (dmg > 0) for (const m of targets) {
    const d = Math.max(1, Math.round(dmg * (m.mods.includes("piedra") ? 0.65 : 1)));
    m.hp -= d;
    hits.push({ i: F.monsters.indexOf(m), text: crit ? `¡${d}!` : `${d}`, killed: m.hp <= 0, m });
    if (m.hp <= 0) kill(m);
  }
  ch.stats.spells = (ch.stats.spells || 0) + 1;
  addLog(dmg > 0 ? `${crit ? "<b>¡Conjuro perfecto!</b> " : ""}Tu voz golpea por <b class="dmg spelldmg${crit ? " big" : ""}">${dmg}</b>${targets.length > 1 ? " a todos" : ""}.` : "El conjuro se deshace en el aire: no se pareció lo bastante.", dmg > 0 ? "good" : "bad");
  save(); renderHud(); renderPanels();
  // the animation
  const stage = $(".stage"), me = $("#me"), live = () => S.F === F && $(".stage") === stage;
  if (!stage) return dmg;
  S.fig?.play("spellcast", { ms: 65 });
  await FX.wait(65 * 5);
  sfx.spell(q);
  if (!live()) return dmg;
  const color = "#b28cff";
  await Promise.all(targets.map((m) => {
    const el = foeEl(F.monsters.indexOf(m));
    return el ? FX.projectile(stage, FX.pointOn(S.fig?.el || me, stage, 0.45, 0.5), FX.pointOn(el.querySelector(".foeart") || el, stage), "bolt", color, 260) : null;
  }));
  if (!live()) return dmg;
  renderFoes();
  if (!hits.length) { floatNum(F.monsters.indexOf(targets[0]), "Se deshace", "miss"); sfx.miss(); }
  for (const x of hits) {
    const el = foeEl(x.i);
    if (!el) continue;
    floatNum(x.i, x.text, `spell${crit ? " crit" : ""}`, 1 + q * 0.5);
    FX.burst(stage, FX.pointOn(el.querySelector(".foeart") || el, stage), color, crit);
    if (x.killed) { el.classList.add("dying"); setTimeout(() => sfx.kill(), 120); lootBeam(F, stage, x); }
    else FX.pulse(el, "flinch", 360);
  }
  if (crit) FX.shake(stage);
  return dmg;
}
function afterSpell(F) {
  if (S.F !== F) return;
  const nb = $("#nextBtn");
  if (nb && !alive(F).length) nb.innerHTML = `${!F.review ? "Recoger el botín" : cardsLeft() ? "Siguiente grupo" : "Terminar el repaso"} <kbd>Enter</kbd>`;
  nb?.focus();
}
async function castShadow() {
  const F = S.F, btn = $("#castBtn");
  if (!F || !F.checked || F.cast || F.casting || F.over || !alive(F).length || !btn) return;
  if (!spend(spellCost())) return;
  F.casting = true;
  const words = exWords();
  const res = await shadow(words, btn, { maxSec: Math.max(3, (words.at(-1).e - words[0].s) * 1.8 + 1.5) });
  F.casting = false;
  if (S.F !== F) return;
  if (!res) { ch.mana = Math.min(stats().maxMana, ch.mana + spellCost()); renderHud(); return; }
  F.cast = true;
  btn.remove();
  const out = h(`<div class="castout"><div class="you">Dijiste: ${esc(res.text || "(nada)")}</div><div class="diff">${res.r.html}</div>${nearMissHtml(res.r)}
    <div class="verdict"><b>${Math.round(res.r.acc * 100)}%</b> <span class="dim">de parecido</span></div></div>`);
  $("#result .row").before(out);
  await spellHit(F, res.r.acc);
  afterSpell(F);
}

// ---------- the grimoire: passages from unique casetes, cast at every monster ----------
function learnSpell(clip) {
  ch.grimoire = ch.grimoire || [];
  const text = clip.words.map((w) => w.w).join(" ");
  const old = ch.grimoire.find((g) => g.ep === S.ep && Math.abs(g.start - clip.start) < 0.5);
  if (old) return old;
  const first = clip.words.slice(0, 4).map((w) => bare(w.w)).join(" ");
  const spell = { id: E.rnd(1, 1e9), ep: S.ep, start: clip.start, end: clip.end, words: clip.words.map((w) => w.w), name: `«${capWord(first)}…»`, text };
  ch.grimoire.push(spell);
  save();
  return spell;
}
function openGrimoire() {
  const F = S.F;
  if (!F || F.over || !alive(F).length) return;
  F.grimUsed = F.grimUsed || [];
  const list = (ch.grimoire || []);
  const box = dialog(`
    <h3>Grimorio</h3>
    <p class="dim">Lee el pasaje en voz alta, como suena. Cada conjuro golpea a todos los monstruos, una vez por combate. Cuesta ${grimCost()} de maná.</p>
    <ol class="grimoire">${list.map((g, i) => {
      const here = g.ep === S.ep, used = F.grimUsed.includes(g.id);
      return `<li><b>${esc(g.name)}</b><p class="gtext">${esc(g.text)}</p>
        <div class="row">${here ? `<button data-gplay="${i}">▶ Oír</button>` : `<span class="dim">De otro episodio: no se puede oír aquí.</span>`}
        <button class="cast" data-gcast="${i}" ${used || ch.mana < grimCost() ? "disabled" : ""}>${used ? "Ya lo usaste" : "Conjurar"}</button></div><div class="gout" data-gout="${i}"></div></li>`;
    }).join("")}</ol>
    <div class="row"><button id="gClose" class="ghost">Cerrar</button></div>`, { cls: "grim" });
  box.querySelector("#gClose").onclick = closeDialog;
  box.querySelectorAll("[data-gplay]").forEach((b) => (b.onclick = () => { const g = list[+b.dataset.gplay]; playRange(g.start, g.end); }));
  box.querySelectorAll("[data-gcast]").forEach((b) => (b.onclick = async () => {
    const g = list[+b.dataset.gcast];
    if (F.casting || F.grimUsed.includes(g.id) || !spend(grimCost())) return;
    F.casting = true;
    const res = await shadow(g.words.map((w) => ({ w })), b, { maxSec: Math.max(6, (g.end - g.start) * 1.6 + 2) });
    F.casting = false;
    if (S.F !== F) return;
    if (!res) { ch.mana = Math.min(stats().maxMana, ch.mana + grimCost()); renderHud(); return; }
    F.grimUsed.push(g.id);
    const out = box.querySelector(`[data-gout="${b.dataset.gcast}"]`);
    if (out) out.innerHTML = `<div class="diff">${res.r.html}</div>${nearMissHtml(res.r)}<div class="verdict"><b>${Math.round(res.r.acc * 100)}%</b></div>`;
    b.textContent = "Lanzado";
    await FX.wait(500);
    closeDialog();
    await spellHit(F, res.r.acc, { all: true, mult: 2.2 });
    afterSpell(F);
  }));
}

// ---------- keys ----------
document.addEventListener("keydown", (e) => {
  if (!ch) return;
  if (S.dialog) {
    if (e.key === "Escape") closeDialog();
    else if ((e.key === "v" || e.key === "V") && rec) { e.preventDefault(); stopRecording(); }
    return;
  }
  const typing = e.target.matches("input, textarea, select");
  if ((e.key === "v" || e.key === "V") && rec) { e.preventDefault(); return stopRecording(); }
  if (e.key === "Escape") { closeMenu(); $("#charPanel").hidden = true; $("#invPanel").hidden = true; $("#srcPanel").hidden = true; syncDrawers(); return; }
  if (e.altKey && ["Digit1", "Digit2", "Digit3"].includes(e.code)) { e.preventDefault(); drinkType(["life", "mana", "rejuv"][+e.code.slice(-1) - 1]); return; }
  if (e.altKey && e.code === "KeyS") { e.preventDefault(); swapWeapons(); return; }
  // spells: Alt+Q/W/E/R anywhere (even while typing), Q/W/E/R otherwise
  const spKey = E.spellsFor(ch).find((sp) => e.code === `Key${sp.key.toUpperCase()}`);
  if (spKey && (e.altKey || (!e.target.matches("input, textarea, select") && !e.ctrlKey && !e.metaKey))) { e.preventDefault(); return prepSpell(spKey.id); }
  if (e.altKey && e.code === "KeyH") { e.preventDefault(); if (S.F) hint(); return; }
  if (e.code === "KeyF" && S.view === "fight" && (e.altKey || (!typing && !e.ctrlKey && !e.metaKey))) { e.preventDefault(); return usePower(); }
  if (S.view === "fight" && S.F) {
    if (e.key === "Tab") {
      e.preventDefault();
      // in the blanks, Tab goes to the next one (Shift+Tab back); past the last one it plays the line again
      if (e.target.matches("#cloze input")) {
        const ins = [...document.querySelectorAll("#cloze input")], k = ins.indexOf(e.target) + (e.shiftKey ? -1 : 1);
        if (ins[k]) return ins[k].focus();
      }
      doPlay(e.shiftKey); return;
    }
    // Tibetan cards: Space shows the answer, 1-4 grade it
    if (S.F.mode === "recall" && !S.F.checked && !S.F.over && !typing) {
      if ((e.key === " " || e.key === "Enter") && !S.F.revealed) { e.preventDefault(); return revealCard(); }
      if (S.F.revealed && /^[1-4]$/.test(e.key)) { e.preventDefault(); return gradeCard(+e.key); }
    }
    if (e.key === "Enter" && !e.shiftKey) {
      if (e.target.closest("button")) return;
      e.preventDefault();
      if (S.F.over) return ($("#goMain") || $("#goTown"))?.click();
      if (S.F.checked) return afterResult();
      if (S.F.mode === "cloze" && e.target.matches("#cloze input")) {
        const ins = [...document.querySelectorAll("#cloze input")];
        const k = ins.indexOf(e.target);
        if (k < ins.length - 1) return ins[k + 1].focus();
      }
      return attack();
    }
  }
  if (typing) return;
  if (S.view === "fight" && S.F?.checked && (e.key === "v" || e.key === "V")) { e.preventDefault(); return castShadow(); }
  if (S.view === "fight" && S.F?.checked && (e.key === "g" || e.key === "G") && $("#grimBtn")) { e.preventDefault(); return openGrimoire(); }
  if (e.key === "m" || e.key === "M") return toggleMute();
  if (e.key === "c" || e.key === "C") togglePanel("#charPanel");
  if (e.key === "i" || e.key === "I") togglePanel("#invPanel");
  if (/^[1-9]$/.test(e.key)) { const p = ch.belt[+e.key - 1]; if (p) drink(p.id); }
});
// clicking a button with the mouse shouldn't leave it focused (Enter would re-trigger it)
document.addEventListener("click", (e) => { const b = e.target.closest("button"); if (b && e.detail) b.blur(); });

// ---------- boot ----------
// drawers open below the header, so its buttons stay reachable
const setTopH = () => document.documentElement.style.setProperty("--top-h", `${$(".top").offsetHeight}px`);
addEventListener("resize", setTopH);
new ResizeObserver(setTopH).observe($(".top")); // the header wraps on a phone, and fonts arrive late
function toggleMute() {
  setMuted(!isMuted());
  const b = $("#muteBtn");
  if (b) { b.textContent = isMuted() ? "Sonido: no" : "Sonido: sí"; b.setAttribute("aria-pressed", String(!isMuted())); }
  if (!isMuted()) sfx.coin();
}
(async function boot() {
  await startI18n();
  $("#langBtn").textContent = lang() === "es" ? "English" : "Español";
  $("#langBtn").onclick = () => setLang(lang() === "es" ? "en" : "es");
  setTopH();
  $("#muteBtn").textContent = isMuted() ? "Sonido: no" : "Sonido: sí";
  $("#muteBtn").onclick = toggleMute;
  $("#optBtn").onclick = openOptions;
  syncMusicBtn();
  $("#musicBtn").onclick = () => { MUSIC.setOn(!MUSIC.isOn()); syncMusicBtn(); placeMusic(); };
  await Promise.all([loadFigure(), loadAnims(), loadLook(), loadBossArt()]).catch(() => {}); // the figure falls back to empty if the art is missing
  if (ch) await prepareLook(lookOfChar(ch)).catch(() => {});
  const eps = await api("api/episodes");
  const sel = $("#episode");
  sel.replaceChildren(...eps.map((e) => new Option(e.title, e.id)));
  const want = new URLSearchParams(location.search).get("ep") || store.get("lastEp", null);
  const id = eps.some((e) => e.id === want) ? want : eps[0]?.id;
  if (!id) { screen.innerHTML = `<p class="empty">Todavía no hay episodios.</p>`; return; }
  sel.value = id;
  await loadEpisode(id);
  // another episode: its own zones and progress, so redraw where you are (a fight in progress belongs to the
  // old one's lines: it ends, and you go to the map)
  sel.onchange = async () => {
    stopAll();
    await loadEpisode(sel.value);
    if (S.view === "dead") return toast("Las frases vendrán de este episodio");
    if (S.F) S.F = null;
    if (ch) show(S.view === "fight" ? "map" : S.view || "town");
    toast("Las frases vendrán de este episodio");
  };
  // online, a new player starts straight away with a random heroine (she can change her look later)
  if (!ch && CFG.online) await quickStart();
  show(ch ? "town" : "create");
})();
async function quickStart() {
  const cls = Object.keys(CLASSES)[Math.floor(Math.random() * Object.keys(CLASSES).length)];
  const pick = (a) => a[Math.floor(Math.random() * a.length)];
  let look = randomLook(cls);
  for (let i = 0; i < 30 && look.body !== "female"; i++) look = randomLook(cls);
  // a young heroine with a full head of hair; the rest (skin, eyes, colours, clothes) as it came
  const hair = ["pixie", "bangs", "bob", "lob", "long", "long_straight", "wavy", "loose", "xlong", "xlong_wavy", "ponytail", "high_ponytail",
    "braid", "pigtails", "bun", "bangs_bun", "half_up", "curly_short", "curly_long", "curls_large", "afro", "natural", "twists"];
  ch = E.newCharacter((CFG.user?.name || "Viajera").slice(0, 20), cls);
  useEpisodeZones();
  ch.look = fixLook({ ...look, body: "female", head: "human_female", hair: pick(hair), face: pick(["neutral", "neutral", "happy"]),
    hairColor: look.hairColor === "gray" || look.hairColor === "white" ? "chestnut" : look.hairColor, wrinkles: null, beard: null, stache: null }, cls);
  await prepareLook(ch.look).catch(() => {});
  save();
  setTimeout(() => toast(`Bienvenida a la aldea, ${ch.name}. En «Personaje» puedes cambiar tu aspecto.`, "", 5000), 300);
}

// for debugging in the console
window.leyendas = { S, get ch() { return ch; }, E, socket, toAlembic, tooltipHtml2: (it) => tooltipHtml(it), showDice, streakDice, tooltipHtml, zoneLines, exKey, chunks, renderMap, perfectMap, checkCompanions, epPerfect, renderMe, renderTown, wanted, isUpgrade, victory, powerWith, stats };
