// El Bestiario: catch and raise creatures; every move is a listening exercise on a line of the episode.
import { $, esc, store, api, CFG, playable, chooseBlanks, scoreDictation, scoreCloze, isSound } from "../listen-core.js";
import { TYPES, FORMS, SPECIES, STARTERS, AREAS, ITEMS, BALLS, TEAM_SIZE, typeMult } from "./data.js";
import * as E from "./engine.js";
import { sfx, isMuted, setMuted, setBusy, hush, quiet } from "../rpg/sfx.js";

const audio = $("#audio");
setBusy(() => !audio.paused);
const screen = $("#screen");
let G = store.get("bestiario", null); // the saved game
const S = { ep: null, T: null, lines: [], view: "start", B: null, area: null, recent: [] };
const save = () => store.set("bestiario", G);
const h = (html) => { const t = document.createElement("template"); t.innerHTML = html.trim(); return t.content.firstElementChild; };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// ---------- toast ----------
let toastT = null;
function toast(msg, ms = 2600) {
  const t = $("#toast");
  t.textContent = msg; t.classList.add("on");
  clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove("on"), ms);
}

// ---------- sprites: the Leyendas monsters, drawn big and crisp ----------
let ATLAS = null;
async function loadAtlas() { ATLAS = (await (await fetch("rpg/lpc/atlas.json")).json()).monsters; }
function sprite(sp, { px = 3, flip = false, shiny = false, cls = "", max = 220 } = {}) {
  const s = SPECIES[sp], r = ATLAS?.[s.sprite];
  if (!r) return `<span class="sprite missing">${esc(s.name)}</span>`;
  const [x, y, w, hh, k = 1] = r;
  const scale = Math.min(px * k * s.size, max / Math.max(w, hh));
  return `<svg class="sprite ${flip ? "flip" : ""} ${shiny ? "shiny" : ""} ${cls}" width="${Math.round(w * scale)}" height="${Math.round(hh * scale)}" viewBox="${x} ${y} ${w} ${hh}" aria-label="${esc(s.name)}" role="img"><image href="rpg/lpc/monsters.png" width="1024" height="120"/></svg>`;
}
const typeChip = (t) => `<span class="type" style="--t:${TYPES[t].color}">${TYPES[t].name}</span>`;
const typesOf = (sp) => SPECIES[sp].types.map(typeChip).join("");
const hpPct = (c) => Math.max(0, Math.round((c.hp / E.stats(c).maxHp) * 100));
const hpClass = (c) => { const p = hpPct(c); return p > 50 ? "" : p > 20 ? "mid" : "low"; };
const display = (c) => `${E.nameOf(c)}${c.shiny ? ' <span class="shinytag" title="Brillante: una entre cien">✦</span>' : ""}`;

// ---------- the episode: lines to hear ----------
async function loadEpisode(id) {
  S.ep = id;
  store.set("lastEp", id);
  S.T = await (await fetch(`media/${encodeURIComponent(id)}/transcript.json`, { cache: "no-cache" })).json();
  S.lines = S.T.segments.map((s, i) => (playable(s) ? i : -1)).filter((i) => i >= 0);
  audio.src = `media/${encodeURIComponent(id)}/audio.mp3`;
}
let stopAt = null;
function playRange(start, end, rate = 1) {
  audio.playbackRate = rate;
  audio.currentTime = Math.max(0, start - 0.12);
  stopAt = end + 0.2;
  hush();
  audio.play().catch(() => {});
}
setInterval(() => { if (stopAt != null && !audio.paused && audio.currentTime >= stopAt) { audio.pause(); stopAt = null; } }, 30);
const segClip = (si) => { const s = S.T.segments[si], w = s.words; return { start: w[0].s ?? s.start, end: w[w.length - 1].e ?? s.end }; };

// Which line a move asks for. Longer lines further from home. A line you got wrong rests 5 minutes,
// then comes back before new ones.
const REST_MS = 5 * 60 * 1000;
const LEN = { hueco: [4, 9], huecos: [6, 11], dictado: [3, 5], catch: [3, 4] };
const missed = () => ((G.missed ||= {})[S.ep] ||= {});
function pickLine(form) {
  const tier = S.area?.tier || 0, [lo, hi0] = LEN[form], hi = hi0 + (form === "catch" ? tier : tier * 2);
  const fits = (si) => { const n = S.T.segments[si].words.filter((w) => !isSound(w.w)).length; return n >= lo && n <= hi; };
  const M = missed(), now = Date.now();
  const due = Object.keys(M).map(Number).filter((si) => now - M[si] >= REST_MS && S.lines.includes(si) && fits(si));
  if (due.length) return due[0];
  let pool = S.lines.filter((si) => fits(si) && !S.recent.includes(si) && !(M[si] && now - M[si] < REST_MS));
  if (!pool.length) pool = S.lines.filter(fits);
  if (!pool.length) pool = S.lines;
  return E.pick(pool);
}
function noteLine(si, acc) {
  S.recent = [si, ...S.recent.filter((x) => x !== si)].slice(0, 40);
  if (acc < 1) missed()[si] = Date.now(); else delete missed()[si];
  G.stats.lines++; if (acc >= 1) G.stats.perfect++;
}

// ---------- screens ----------
function show(view) {
  S.view = view;
  hush(); audio.pause();
  ({ start: renderStart, town: renderTown, area: renderArea, battle: renderBattle, shop: renderShop, corral: renderCorral, dex: renderDex })[view]();
  $("#pesos").textContent = G ? `$${G.pesos.toLocaleString("es-CO")}` : "";
  window.scrollTo(0, 0);
}

function renderStart() {
  screen.innerHTML = `
    <section class="start">
      <h2>Elige tu primera criatura</h2>
      <p class="lede">En el Bestiario cada golpe es una frase del episodio: la oyes, la escribes, y según lo bien que la escribas, pega. Para atrapar criaturas les lanzas una totuma… y escribes lo que oyes.</p>
      <div class="starters">${STARTERS.map((sp) => `
        <button class="starter" data-sp="${sp}">
          <div class="stage">${sprite(sp, { px: 4, max: 150 })}</div>
          <b>${SPECIES[sp].name}</b><div>${typesOf(sp)}</div>
          <p>${esc(SPECIES[sp].blurb)}</p>
        </button>`).join("")}</div>
      <p class="dim small">Agua le gana a Fuego, Fuego a Planta, Planta a Agua.</p>
    </section>`;
  screen.querySelectorAll("[data-sp]").forEach((b) => (b.onclick = () => {
    G = E.newSave(CFG.user?.name || "", b.dataset.sp);
    save(); sfx.levelup();
    toast(`${SPECIES[b.dataset.sp].name} se viene contigo.`);
    show("town");
  }));
}

function teamCard(c, i, { actions = "" } = {}) {
  const st = E.stats(c), next = E.xpFor(c.lvl + 1), prev = E.xpFor(c.lvl);
  return `<div class="ccard${c.hp <= 0 ? " fainted" : ""}">
    <div class="cstage">${sprite(c.sp, { px: 2.5, max: 90, shiny: c.shiny })}</div>
    <div class="cinfo">
      <div class="cname">${display(c)} <span class="lvl">Nv ${c.lvl}</span></div>
      <div>${typesOf(c.sp)}</div>
      <div class="hpbar ${hpClass(c)}"><i style="width:${hpPct(c)}%"></i></div>
      <div class="dim small">${Math.max(0, c.hp)}/${st.maxHp} de vida · exp ${Math.round(((c.xp - prev) / (next - prev)) * 100)}%</div>
      ${actions}
    </div></div>`;
}

function renderTown() {
  const hurt = G.team.some((c) => c.hp < E.stats(c).maxHp);
  screen.innerHTML = `
    <section class="town">
      <div class="townhead">
        <div><h2>El pueblo</h2><p class="dim">La plaza, la iglesia, la tienda de Doña Rosa y un perro dormido al sol.</p></div>
        <div class="medals" title="Guardianes vencidos">${AREAS.map((a) => `<span class="medal ${G.beaten[a.id] ? "on" : ""}" title="${esc(a.guardian.name)}">${G.beaten[a.id] ? "★" : "☆"}</span>`).join("")}</div>
      </div>
      <h3>Tu equipo <span class="dim">${G.team.length}/${TEAM_SIZE}</span></h3>
      <div class="team">${G.team.map((c, i) => teamCard(c, i, { actions: i ? `<button class="mini" data-lead="${i}">Al frente</button>` : `<span class="dim small">va al frente</span>` })).join("")}</div>
      <div class="townacts">
        <button id="heal" ${hurt ? "" : "disabled"}>Donde Doña Rosa: curar a todos</button>
        <button id="toShop">La tienda</button>
        <button id="toCorral">El corral <span class="dim">${G.corral.length}</span></button>
        <button id="toDex">El cuaderno <span class="dim">${Object.keys(G.dex.caught).length}/${Object.keys(SPECIES).length}</span></button>
      </div>
      <h3>Salir</h3>
      <ol class="areas">${AREAS.map((a, i) => {
        const open = E.areaOpen(G, i);
        return `<li class="${open ? "" : "locked"}" style="--sky1:${a.sky[0]};--sky2:${a.sky[1]};--ground:${a.ground}">
          <div class="abg"></div>
          <div class="atext"><b>${esc(a.name)}</b> <span class="dim">nivel ${a.lvl[0]}–${a.lvl[1]}</span>${G.beaten[a.id] ? ' <span class="beat">★ guardián vencido</span>' : ""}
          <p>${open ? esc(a.blurb) : `Cerrado: primero vence a ${esc(AREAS[i - 1].guardian.name)} en ${esc(AREAS[i - 1].name)}.`}</p></div>
          ${open ? `<button class="primary" data-area="${a.id}">Ir</button>` : ""}</li>`;
      }).join("")}</ol>
    </section>`;
  $("#heal").onclick = () => { E.healAll(G); save(); sfx.levelup(); toast("Doña Rosa les da caldo y una cobija. Todos como nuevos."); renderTown(); };
  $("#toShop").onclick = () => show("shop");
  $("#toCorral").onclick = () => show("corral");
  $("#toDex").onclick = () => show("dex");
  screen.querySelectorAll("[data-lead]").forEach((b) => (b.onclick = () => { const [c] = G.team.splice(+b.dataset.lead, 1); G.team.unshift(c); save(); renderTown(); }));
  screen.querySelectorAll("[data-area]").forEach((b) => (b.onclick = () => { S.area = E.areaById(b.dataset.area); show("area"); }));
}

function renderArea() {
  const a = S.area, g = a.guardian, alive = G.team.some((c) => c.hp > 0);
  const seen = a.wild.map(([sp]) => sp).concat(a.legend ? [a.legend] : [], a.legend2 ? [a.legend2] : []);
  screen.innerHTML = `
    <section class="area" style="--sky1:${a.sky[0]};--sky2:${a.sky[1]};--ground:${a.ground}">
      <div class="areahero"><div class="abg"></div><div><h2>${esc(a.name)}</h2><p>${esc(a.blurb)}</p></div></div>
      <div class="areaacts">
        <button class="primary big" id="explore" ${alive ? "" : "disabled"}>Buscar en el monte <kbd>Enter</kbd></button>
        <button class="big" id="guardian" ${alive ? "" : "disabled"}>${G.beaten[a.id] ? "Volver a retar a" : "Retar a"} ${esc(g.name)}, ${esc(g.title)}</button>
        <button id="back">Volver al pueblo</button>
      </div>
      ${alive ? "" : `<p class="warn">Tu equipo está desmayado. Vuelve al pueblo: Doña Rosa los cura.</p>`}
      <h3>Lo que vive aquí</h3>
      <div class="roster">${seen.map((sp) => {
        const known = G.dex.seen[sp], caught = G.dex.caught[sp];
        return `<div class="rmon ${known ? "" : "unknown"}" title="${known ? esc(SPECIES[sp].name) : "Sin ver todavía"}">${sprite(sp, { px: 2, max: 56 })}<span>${known ? esc(SPECIES[sp].name) : "¿?"}${caught ? " ●" : ""}</span></div>`;
      }).join("")}</div>
      <h3>Tu equipo</h3>
      <div class="team small">${G.team.map((c, i) => teamCard(c, i)).join("")}</div>
    </section>`;
  $("#explore").onclick = () => startBattle({ wild: E.wildFor(a) });
  $("#guardian").onclick = () => startBattle({ trainer: g });
  $("#back").onclick = () => show("town");
  $("#explore").focus();
}

function renderShop() {
  screen.innerHTML = `
    <section class="shop">
      <h2>La tienda <span class="dim">de Doña Rosa</span></h2>
      <p class="dim">Tienes $${G.pesos.toLocaleString("es-CO")}.</p>
      <table class="shoptable">${Object.entries(ITEMS).map(([id, it]) => `
        <tr><td><b>${esc(it.name)}</b><div class="dim small">${esc(it.desc)}</div></td>
        <td class="num">$${it.price.toLocaleString("es-CO")}</td><td class="num dim">tienes ${G.bag[id] || 0}</td>
        <td><button data-buy="${id}" ${G.pesos < it.price ? "disabled" : ""}>Comprar</button> <button data-buy5="${id}" ${G.pesos < it.price * 5 ? "disabled" : ""}>×5</button></td></tr>`).join("")}</table>
      <button id="back">Volver al pueblo</button>
    </section>`;
  const buy = (id, n) => { const cost = ITEMS[id].price * n; if (G.pesos < cost) return; G.pesos -= cost; G.bag[id] = (G.bag[id] || 0) + n; save(); sfx.coin(); show("shop"); };
  screen.querySelectorAll("[data-buy]").forEach((b) => (b.onclick = () => buy(b.dataset.buy, 1)));
  screen.querySelectorAll("[data-buy5]").forEach((b) => (b.onclick = () => buy(b.dataset.buy5, 5)));
  $("#back").onclick = () => show("town");
}

function renderCorral() {
  screen.innerHTML = `
    <section class="corral">
      <h2>El corral</h2>
      <p class="dim">Las criaturas que no caben en tu equipo esperan aquí, comiendo y durmiendo. Tu equipo lleva hasta ${TEAM_SIZE}.</p>
      <h3>Tu equipo</h3>
      <div class="team">${G.team.map((c, i) => teamCard(c, i, { actions: G.team.length > 1 ? `<button class="mini" data-down="${i}">Al corral</button>` : "" })).join("")}</div>
      <h3>En el corral <span class="dim">${G.corral.length}</span></h3>
      ${G.corral.length ? `<div class="team">${G.corral.map((c, i) => teamCard(c, i, { actions: `<button class="mini" data-up="${i}" ${G.team.length >= TEAM_SIZE ? "disabled" : ""}>Al equipo</button> <button class="mini ghost" data-free="${i}">Soltar</button>` })).join("")}</div>` : `<p class="dim">Vacío. Lo que atrapes con el equipo lleno vendrá aquí.</p>`}
      <button id="back">Volver al pueblo</button>
    </section>`;
  screen.querySelectorAll("[data-down]").forEach((b) => (b.onclick = () => { G.corral.push(...G.team.splice(+b.dataset.down, 1)); save(); renderCorral(); }));
  screen.querySelectorAll("[data-up]").forEach((b) => (b.onclick = () => { if (G.team.length < TEAM_SIZE) { G.team.push(...G.corral.splice(+b.dataset.up, 1)); save(); renderCorral(); } }));
  screen.querySelectorAll("[data-free]").forEach((b) => (b.onclick = () => {
    const c = G.corral[+b.dataset.free];
    if (!confirm(`¿Soltar a ${E.nameOf(c)} (nivel ${c.lvl}) en el monte? No vuelve.`)) return;
    G.corral.splice(+b.dataset.free, 1); save(); renderCorral();
  }));
  $("#back").onclick = () => show("town");
}

function renderDex() {
  const all = Object.values(SPECIES);
  screen.innerHTML = `
    <section class="dex">
      <h2>El cuaderno</h2>
      <p class="dim">Vistas ${Object.keys(G.dex.seen).length} · atrapadas ${Object.keys(G.dex.caught).length} · de ${all.length}. Una frase perfecta cuenta igual que una mala para el cuaderno; para atraparlas, no.</p>
      <div class="dexgrid">${all.map((s, i) => {
        const seen = G.dex.seen[s.id], caught = G.dex.caught[s.id];
        return `<div class="dexcard ${seen ? "" : "unknown"} ${s.legend ? "legend" : ""}">
          <span class="dexn">${String(i + 1).padStart(2, "0")}</span>
          <div class="dstage">${sprite(s.id, { px: 2.5, max: 80 })}</div>
          <b>${seen ? esc(s.name) : "¿?"}</b>${caught ? ' <span class="caught" title="Atrapada">●</span>' : ""}
          ${seen ? `<div>${typesOf(s.id)}</div><p>${esc(s.blurb)}</p>${s.evo ? `<p class="dim small">Cambia al nivel ${s.evo[1]}.</p>` : ""}` : ""}
        </div>`;
      }).join("")}</div>
      <button id="back">Volver al pueblo</button>
    </section>`;
  $("#back").onclick = () => show("town");
}

// ---------- battle ----------
// B = { wild | trainer, foes: [creature], fi, me (team index), phase, ex, seenMe: Set of uids that fought }
function startBattle({ wild, trainer }) {
  const foes = wild ? [wild] : trainer.team.map(([sp, lvl]) => E.makeCreature(sp, lvl, { shiny: false }));
  const me = G.team.findIndex((c) => c.hp > 0);
  if (me < 0) return toast("Tu equipo está desmayado");
  S.B = { wild: !!wild, trainer, foes, fi: 0, me, phase: "menu", fought: new Set([G.team[me].uid]), log: [] };
  for (const f of foes.slice(0, 1)) G.dex.seen[f.sp] = 1;
  G.stats.battles++;
  save();
  show("battle");
  const f = foes[0];
  say(wild ? (SPECIES[f.sp].legend ? `¡${E.nameOf(f)}! Una de las viejas historias, aquí, de verdad.` : `¡Sale un${f.shiny ? " brillante" : ""} ${E.nameOf(f)} de entre la maleza!`) : `${trainer.name}: «${trainer.hi}»`);
}
const foe = () => S.B.foes[S.B.fi];
const mine = () => G.team[S.B.me];

function plate(c, side) {
  const st = E.stats(c), next = E.xpFor(c.lvl + 1), prev = E.xpFor(c.lvl);
  return `<div class="plate ${side}">
    <div class="pname">${display(c)} <span class="lvl">Nv ${c.lvl}</span></div>
    <div class="ptypes">${typesOf(c.sp)}${side === "foe" && G.dex.caught[c.sp] ? ' <span class="caught" title="Ya tienes una">●</span>' : ""}</div>
    ${side === "foe" && S.B?.trainer ? `<div class="trainer">de ${esc(S.B.trainer.name)} ${S.B.foes.map((f) => `<i class="ball ${f.hp <= 0 ? "out" : ""}"></i>`).join("")}</div>` : ""}
    <div class="hpbar ${hpClass(c)}"><i style="width:${hpPct(c)}%"></i></div>
    ${side === "me" ? `<div class="hpnum">${Math.max(0, c.hp)} / ${st.maxHp}</div><div class="xpbar"><i style="width:${Math.round(((c.xp - prev) / (next - prev)) * 100)}%"></i></div>` : ""}
  </div>`;
}
function renderBattle() {
  const B = S.B, a = S.area;
  screen.innerHTML = `
    <section class="battle">
      <div class="scene" style="--sky1:${a.sky[0]};--sky2:${a.sky[1]};--ground:${a.ground}">
        <div class="abg"></div>
        <div class="side foe" id="foeSide">${plate(foe(), "foe")}<div class="mon" id="foeMon"><div class="pad"></div>${sprite(foe().sp, { px: 4, shiny: foe().shiny, max: 190 })}</div></div>
        <div class="side me" id="meSide"><div class="mon" id="meMon"><div class="pad"></div>${sprite(mine().sp, { px: 4.5, flip: true, shiny: mine().shiny, max: 210 })}</div>${plate(mine(), "me")}</div>
      </div>
      <div class="panel">
        <div class="msg" id="msg" aria-live="polite"></div>
        <div class="acts" id="acts"></div>
      </div>
    </section>`;
  renderActs();
}
function refreshPlates() {
  const fs = $("#foeSide .plate"), ms = $("#meSide .plate");
  if (fs) fs.outerHTML = plate(foe(), "foe");
  if (ms) ms.outerHTML = plate(mine(), "me");
}
function say(text) { const m = $("#msg"); if (m) m.innerHTML = text; }
async function sayWait(text, ms = 900) { say(text); await sleep(ms); }

function renderActs() {
  const B = S.B, acts = $("#acts");
  if (!acts) return;
  B.phase = "menu";
  const balls = BALLS.reduce((n, b) => n + (G.bag[b] || 0), 0);
  acts.innerHTML = `<div class="menu4">
    <button class="primary" id="aFight">Luchar <kbd>1</kbd></button>
    <button id="aBall" ${B.wild && balls ? "" : "disabled"} title="${B.wild ? "" : "A las criaturas de otra persona no se les tira totuma"}">Totuma <span class="dim">${balls}</span> <kbd>2</kbd></button>
    <button id="aBag">Mochila <kbd>3</kbd></button>
    <button id="aTeam">Equipo <kbd>4</kbd></button>
    ${B.wild ? `<button id="aRun" class="ghost">Huir <kbd>5</kbd></button>` : ""}
  </div>`;
  $("#aFight").onclick = renderMoves;
  $("#aBall").onclick = renderBalls;
  $("#aBag").onclick = renderBag;
  $("#aTeam").onclick = () => renderSwitch(false);
  $("#aRun") && ($("#aRun").onclick = run);
  $("#aFight").focus();
}
function backBtn() { return `<button class="ghost back" id="aBack">Atrás <kbd>Esc</kbd></button>`; }
function renderMoves() {
  const acts = $("#acts"), f = foe();
  S.B.phase = "moves";
  acts.innerHTML = `<div class="moves">${E.movesOf(mine()).map((m, i) => {
    const eff = typeMult(m.type, SPECIES[f.sp].types);
    return `<button class="move" data-move="${m.id}" style="--t:${TYPES[m.type].color}">
      <b>${esc(m.name)}</b> <kbd>${i + 1}</kbd>
      <span class="mform">${FORMS[m.form].name} · fuerza ${m.power}</span>
      <span class="mtype">${TYPES[m.type].name}${G.dex.seen[f.sp] && eff !== 1 ? ` · <em class="${eff > 1 ? "good" : "bad"}">${eff > 1 ? "le duele" : "le hace poco"}</em>` : ""}</span>
    </button>`;
  }).join("")}</div>${backBtn()}`;
  acts.querySelectorAll("[data-move]").forEach((b) => (b.onclick = () => exercise({ kind: "move", move: E.movesOf(mine()).find((m) => m.id === b.dataset.move) })));
  $("#aBack").onclick = renderActs;
  acts.querySelector("[data-move]")?.focus();
}
function renderBalls() {
  const acts = $("#acts");
  S.B.phase = "balls";
  acts.innerHTML = `<p class="dim small">Le lanzas la totuma y escribes una frase corta. Cuanto más débil esté, y mejor la escribas, más fácil.</p>
    <div class="moves">${BALLS.filter((b) => G.bag[b]).map((b, i) => `<button class="move" data-ball="${b}"><b>${esc(ITEMS[b].name)}</b> <kbd>${i + 1}</kbd><span class="mform">tienes ${G.bag[b]}</span><span class="mtype">${esc(ITEMS[b].desc)}</span></button>`).join("")}</div>${backBtn()}`;
  acts.querySelectorAll("[data-ball]").forEach((b) => (b.onclick = () => exercise({ kind: "ball", ball: b.dataset.ball })));
  $("#aBack").onclick = renderActs;
  acts.querySelector("[data-ball]")?.focus();
}
function renderBag() {
  const acts = $("#acts"), items = ["panela", "sancocho", "tinto"].filter((k) => G.bag[k]);
  S.B.phase = "bag";
  acts.innerHTML = items.length ? `<div class="moves">${items.map((k, i) => `<button class="move" data-item="${k}"><b>${esc(ITEMS[k].name)}</b> <kbd>${i + 1}</kbd><span class="mform">tienes ${G.bag[k]}</span><span class="mtype">${esc(ITEMS[k].desc)}</span></button>`).join("")}</div>${backBtn()}`
    : `<p class="dim">La mochila no tiene nada para curar. En la tienda del pueblo hay agua de panela.</p>${backBtn()}`;
  acts.querySelectorAll("[data-item]").forEach((b) => (b.onclick = () => pickTarget(b.dataset.item)));
  $("#aBack").onclick = renderActs;
  acts.querySelector("[data-item]")?.focus();
}
function pickTarget(item) {
  const acts = $("#acts"), it = ITEMS[item];
  const ok = (c) => (it.revive ? c.hp <= 0 : c.hp > 0 && c.hp < E.stats(c).maxHp);
  acts.innerHTML = `<p class="dim small">¿A quién le das ${esc(it.name.toLowerCase())}?</p><div class="moves">${G.team.map((c, i) => `<button class="move" data-t="${i}" ${ok(c) ? "" : "disabled"}><b>${display(c)}</b><span class="mform">Nv ${c.lvl} · ${Math.max(0, c.hp)}/${E.stats(c).maxHp}</span></button>`).join("")}</div>${backBtn()}`;
  acts.querySelectorAll("[data-t]").forEach((b) => (b.onclick = async () => {
    const c = G.team[+b.dataset.t], max = E.stats(c).maxHp;
    G.bag[item]--;
    if (it.revive) c.hp = Math.round(max * it.revive); else c.hp = Math.min(max, c.hp + it.heal);
    save(); sfx.levelup(); refreshPlates();
    acts.innerHTML = "";
    await sayWait(`${E.nameOf(c)} ${it.revive ? "se despierta con el tinto" : "se toma el " + it.name.toLowerCase() + " y se siente mejor"}.`);
    await foeTurn();
    if (S.B && !S.B.over) renderActs();
  }));
  $("#aBack").onclick = renderBag;
}
function renderSwitch(forced) {
  const acts = $("#acts");
  S.B.phase = forced ? "forced" : "switch";
  acts.innerHTML = `<p class="dim small">${forced ? "¿Quién sale ahora?" : "Cambiar gasta tu turno."}</p><div class="moves">${G.team.map((c, i) => `<button class="move" data-sw="${i}" ${c.hp > 0 && i !== S.B.me ? "" : "disabled"}><b>${display(c)}</b><span class="mform">Nv ${c.lvl} · ${Math.max(0, c.hp)}/${E.stats(c).maxHp}</span><span class="mtype">${SPECIES[c.sp].types.map((t) => TYPES[t].name).join(" / ")}</span></button>`).join("")}</div>${forced ? "" : backBtn()}`;
  acts.querySelectorAll("[data-sw]").forEach((b) => (b.onclick = async () => {
    S.B.me = +b.dataset.sw; S.B.fought.add(mine().uid);
    renderBattle(); $("#acts").innerHTML = "";
    await sayWait(`¡Adelante, ${E.nameOf(mine())}!`);
    if (!forced) await foeTurn();
    if (S.B && !S.B.over) renderActs();
  }));
  if (!forced) $("#aBack").onclick = renderActs;
  acts.querySelector("[data-sw]:not([disabled])")?.focus();
}
async function run() {
  $("#acts").innerHTML = "";
  await sayWait("Te escabulles entre la maleza.", 800);
  endBattle("run");
}

// ---------- the exercise: hear a line, write it ----------
function exercise(action) {
  const B = S.B, acts = $("#acts");
  const form = action.kind === "ball" ? "catch" : action.move.form;
  const si = pickLine(form);
  const words = S.T.segments[si].words;
  const blanks = form === "hueco" ? chooseBlanks(S.T.segments, si, 1) : form === "huecos" ? chooseBlanks(S.T.segments, si, 3) : null;
  B.ex = { action, si, words, blanks, form, plays: 0 };
  B.phase = "exercise";
  const clip = segClip(si);
  const play = (slow) => { B.ex.plays++; playRange(clip.start, clip.end, slow ? 0.75 : 1); };
  const title = action.kind === "ball" ? `${esc(ITEMS[action.ball].name)} · escribe la frase` : `${esc(action.move.name)} · ${FORMS[form].desc.toLowerCase()}`;
  acts.innerHTML = `<div class="ex">
    <div class="exhead"><b>${title}</b>
      <button class="play" id="exPlay" title="Oír otra vez (Tab en la última casilla, o aquí)">▶ Oír</button>
      <button class="ghost" id="exSlow" title="Más despacio">Despacio</button></div>
    ${blanks ? `<div class="cloze" id="cloze">${words.map((w, i) => blanks.includes(i)
      ? `<input data-i="${i}" autocomplete="off" autocapitalize="off" spellcheck="false" size="${Math.max(3, w.w.replace(/[^\p{L}]/gu, "").length)}" aria-label="Palabra que falta">`
      : `<span>${esc(w.w)}</span>`).join(" ")}</div>`
      : `<textarea id="exAnswer" rows="2" placeholder="Escribe lo que oyes y pulsa Enter" autocomplete="off" autocapitalize="off" spellcheck="false"></textarea>`}
    <div class="exfoot"><button class="primary" id="exGo">${action.kind === "ball" ? "Lanzar" : "Atacar"} <kbd>Enter</kbd></button>${backBtn()}</div>
  </div>`;
  $("#exPlay").onclick = () => { play(false); focusEx(); };
  $("#exSlow").onclick = () => { play(true); focusEx(); };
  $("#exGo").onclick = submit;
  $("#aBack").onclick = () => { audio.pause(); action.kind === "ball" ? renderBalls() : renderMoves(); };
  const inputs = [...acts.querySelectorAll("#cloze input")];
  acts.querySelector(".ex").addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && e.target.matches("input, textarea")) { e.preventDefault(); submit(); }
    // Tab moves to the next gap; on the last one (or in a dictation) it plays the line again
    if (e.key === "Tab" && e.target.matches("input, textarea")) {
      const k = inputs.indexOf(e.target);
      if (!e.shiftKey && k >= 0 && k < inputs.length - 1) return; // the browser moves on
      if (e.shiftKey && k > 0) return;
      e.preventDefault(); play(e.shiftKey);
    }
  });
  focusEx();
  quiet().then(() => { if (S.B?.ex?.si === si && B.phase === "exercise") play(false); });
}
const focusEx = () => ($("#cloze input") || $("#exAnswer"))?.focus();
function submit() {
  const B = S.B, ex = B.ex;
  if (B.phase !== "exercise") return;
  let r;
  if (ex.blanks) {
    const typed = Object.fromEntries([...document.querySelectorAll("#cloze input")].map((x) => [x.dataset.i, x.value.trim()]));
    if (!Object.values(typed).some(Boolean)) return toast("Escribe lo que falta");
    r = scoreCloze(ex.words, ex.blanks, typed);
  } else {
    const v = $("#exAnswer").value;
    if (!v.trim()) return toast("Escribe lo que oíste");
    r = scoreDictation(ex.words, v);
  }
  B.phase = "resolving";
  noteLine(ex.si, r.acc);
  save();
  if (r.acc >= 1) sfx.correct(0, ex.plays <= 1); else if (r.acc >= 0.5) sfx.partial(); else sfx.miss();
  // the answer stays in view, and you hear the line again now that it's done
  const pct = Math.min(r.acc >= 1 ? 100 : 99, Math.round(r.acc * 100));
  $("#acts").innerHTML = `<div class="exres"><div class="diff">${r.html}</div><div class="verdict ${r.acc >= 1 ? "good" : r.acc >= 0.5 ? "" : "bad"}"><b>${pct}%</b>${r.acc < 0.5 ? " · no alcanza" : r.acc >= 1 ? " · perfecto" : ""}</div></div>`;
  quiet().then(() => { const c = segClip(ex.si); playRange(c.start, c.end, 1); });
  (ex.action.kind === "ball" ? throwBall(ex.action.ball, r.acc) : myTurn(ex.action.move, r.acc)).catch((e) => { console.error(e); toast(e.message); });
}

// ---------- turns ----------
function shake(id, cls = "hit") { const el = $(id); if (!el) return; el.classList.remove(cls); void el.offsetWidth; el.classList.add(cls); }
const effText = (eff) => (eff >= 2 ? " <b>¡Le duele de verdad!</b>" : eff > 1 ? " Le duele." : eff <= 0.5 ? " Apenas le hace cosquillas." : "");
// "el Conejo salvaje", "el Jabato de Doña Ofelia", "La Madremonte"
function foeName(c, cap = true) {
  const n = E.nameOf(c), own = /^(El|La) /.test(n);
  const out = own ? n : `${cap ? "El" : "el"} ${n}${S.B.wild ? " salvaje" : ` de ${S.B.trainer.name}`}`;
  return out;
}
async function attack(att, def, move, acc, mineAttacks) {
  const r = E.damage(att, def, move, acc);
  const who = mineAttacks ? E.nameOf(att) : foeName(att);
  if (r.miss) { sfx.miss(); await sayWait(`${who} intenta ${esc(move.name)}… y falla. ${mineAttacks ? "No entendiste lo suficiente." : ""}`, 1100); return r; }
  const dmg = mineAttacks ? r.dmg : Math.max(1, Math.round(r.dmg * E.FOE_SOFTEN));
  def.hp = Math.max(0, def.hp - dmg);
  sfx.hit(r.perfect);
  shake(mineAttacks ? "#foeMon" : "#meMon");
  refreshPlates();
  await sayWait(`${who} usa <b>${esc(move.name)}</b>${r.perfect && mineAttacks ? " con una frase perfecta" : ""}: ${dmg} de daño.${effText(r.eff)}`, 1200);
  return r;
}
async function myTurn(move, acc) {
  const B = S.B, me = mine(), f = foe();
  const meFirst = E.stats(me).spd >= E.stats(f).spd;
  await sleep(500);
  if (meFirst) {
    await attack(me, f, move, acc, true);
    if (f.hp <= 0) return foeFainted();
    await foeTurn();
  } else {
    await foeTurn();
    if (B.over || mine() !== me || me.hp <= 0) return;
    await attack(me, f, move, acc, true);
    if (f.hp <= 0) return foeFainted();
  }
  if (!B.over && B.phase !== "forced") renderActs();
}
async function foeTurn() {
  const B = S.B, f = foe(), me = mine();
  if (B.over || f.hp <= 0) return;
  await attack(f, me, E.foeMove(f, me), null, false);
  if (me.hp <= 0) await meFainted();
}
async function meFainted() {
  const B = S.B;
  sfx.kill(); shake("#meMon", "faint");
  await sayWait(`${E.nameOf(mine())} se desmaya.`, 1100);
  save();
  if (!G.team.some((c) => c.hp > 0)) {
    B.over = true;
    const lost = Math.round(G.pesos * 0.15);
    G.pesos -= lost;
    E.healAll(G); save();
    await sayWait(`No te queda nadie en pie. Pierdes $${lost.toLocaleString("es-CO")} y despiertas donde Doña Rosa, que ya los curó a todos.`, 2600);
    return endBattle("lost");
  }
  renderSwitch(true);
}
async function foeFainted() {
  const B = S.B, f = foe();
  sfx.kill(); shake("#foeMon", "faint");
  await sayWait(`${E.nameOf(f)} se desmaya.`, 1000);
  await shareXp(f);
  if (B.trainer && B.fi < B.foes.length - 1) {
    B.fi++;
    G.dex.seen[foe().sp] = 1; save();
    renderBattle(); $("#acts").innerHTML = "";
    await sayWait(`${B.trainer.name} saca a ${E.nameOf(foe())}.`, 1100);
    return renderActs();
  }
  B.over = true;
  if (B.trainer) {
    const first = !G.beaten[S.area.id];
    const pesos = first ? B.trainer.pesos : Math.round(B.trainer.pesos / 3);
    G.pesos += pesos; G.beaten[S.area.id] = true; save(); sfx.coin();
    await sayWait(`${B.trainer.name}: «${B.trainer.bye}»<br>Te da $${pesos.toLocaleString("es-CO")}.${first && AREAS.indexOf(S.area) < AREAS.length - 1 ? ` <b>Se abre ${esc(AREAS[AREAS.indexOf(S.area) + 1].name)}.</b>` : ""}`, 3200);
  } else {
    const pesos = 4 * f.lvl + E.rnd(0, f.lvl);
    G.pesos += pesos; save(); sfx.coin();
    await sayWait(`Encuentras $${pesos.toLocaleString("es-CO")} entre la hierba.`, 900);
  }
  endBattle("won");
}
// xp to everyone who fought and is still standing; the one out front gets it all, the others half
async function shareXp(f) {
  const B = S.B, base = E.xpGain(f, !!B.trainer);
  for (const c of G.team.filter((c) => B.fought.has(c.uid) && c.hp > 0)) {
    const xp = c === mine() ? base : Math.round(base / 2);
    const res = E.addXp(c, xp);
    refreshPlates();
    await sayWait(`${E.nameOf(c)} gana ${xp} de experiencia.`, 700);
    for (const L of res.levels) {
      sfx.levelup();
      await sayWait(`<b>${E.nameOf(c)} sube al nivel ${L.lvl}.</b>${L.learned.length ? ` Aprende ${L.learned.map((m) => `<b>${esc(m.name)}</b> (${FORMS[m.form].name})`).join(" y ")}.` : ""}`, 1400);
    }
    if (res.evolve) await evolveScene(c, res.evolve);
  }
  save();
}
async function evolveScene(c, into) {
  const from = E.nameOf(c);
  const mon = c === mine() ? $("#meMon") : null;
  mon?.classList.add("evolving");
  await sayWait(`¿Qué le pasa a ${from}? Está cambiando…`, 1800);
  E.evolve(c, into);
  G.dex.seen[into] = 1; G.dex.caught[into] = 1;
  save(); sfx.identify();
  if (mon) { renderBattle(); $("#acts").innerHTML = ""; }
  await sayWait(`<b>¡${from} ahora es ${E.nameOf(c)}!</b>`, 2000);
}
async function throwBall(ball, acc) {
  const B = S.B, f = foe();
  G.bag[ball]--; save();
  await sleep(400);
  const p = E.catchChance(f, ball, acc);
  const caught = Math.random() < p;
  const mon = $("#foeMon");
  mon.classList.add("inball");
  await sayWait(`Le lanzas la ${ITEMS[ball].name.toLowerCase()}…`, 900);
  if (acc < 0.6) {
    mon.classList.remove("inball"); sfx.miss();
    await sayWait("La frase se te enredó y la totuma sale torcida. Se rompe contra una piedra.", 1500);
  } else {
    // up to three wobbles; the odds decide how many before it breaks free
    const wobbles = caught ? 3 : Math.min(2, Math.floor(p * 4));
    for (let k = 0; k < wobbles; k++) { shake("#foeMon", "wobble"); sfx.partial(); await sleep(700); }
    if (caught) {
      sfx.levelup();
      G.dex.caught[f.sp] = 1; G.stats.caught++;
      const toTeam = G.team.length < TEAM_SIZE;
      f.uid = E.uid();
      (toTeam ? G.team : G.corral).push(f);
      B.over = true; save();
      await sayWait(`<b>¡Atrapaste a ${E.nameOf(f)}!</b> ${toTeam ? "Se une a tu equipo." : "Tu equipo está lleno: va al corral del pueblo."}`, 2200);
      return endBattle("caught");
    }
    mon.classList.remove("inball"); sfx.miss();
    await sayWait(["¡Se escapó!", "¡Casi! Se sale de la totuma.", "Uy, por poco."][Math.min(2, wobbles)], 1100);
  }
  await foeTurn();
  if (!B.over) renderActs();
}
function endBattle(how) {
  const B = S.B;
  B.over = true;
  save();
  const acts = $("#acts");
  if (!acts) return;
  if (how === "lost") { S.B = null; return show("town"); }
  acts.innerHTML = `<div class="menu4"><button class="primary" id="aAgain">Seguir buscando <kbd>Enter</kbd></button><button id="aOut">Salir de ${esc(S.area.name)}</button></div>`;
  $("#aAgain").onclick = () => { S.B = null; if (G.team.some((c) => c.hp > 0)) startBattle({ wild: E.wildFor(S.area) }); else show("area"); };
  $("#aOut").onclick = () => { S.B = null; show("area"); };
  $("#aAgain").focus();
}

// ---------- keys ----------
document.addEventListener("keydown", (e) => {
  if (e.target.matches("input, textarea, select")) return;
  if (S.view === "battle" && S.B) {
    const ph = S.B.phase;
    if (e.key === "Escape" && $("#aBack")) { e.preventDefault(); $("#aBack").click(); return; }
    if (/^[1-5]$/.test(e.key)) {
      const sel = ph === "menu" ? ["#aFight", "#aBall", "#aBag", "#aTeam", "#aRun"][+e.key - 1] : null;
      const btn = sel ? $(sel) : [...document.querySelectorAll("#acts .move")][+e.key - 1];
      if (btn && !btn.disabled) { e.preventDefault(); btn.click(); }
    }
  }
  if (S.view === "area" && e.key === "Enter" && document.activeElement === document.body) $("#explore")?.click();
  if (e.key === "m" || e.key === "M") toggleMute();
});
function toggleMute() { setMuted(!isMuted()); $("#muteBtn").textContent = isMuted() ? "Sonido: no" : "Sonido: sí"; }

// ---------- start ----------
(async function boot() {
  $("#muteBtn").textContent = isMuted() ? "Sonido: no" : "Sonido: sí";
  $("#muteBtn").onclick = toggleMute;
  await loadAtlas();
  const eps = await api("api/episodes");
  const sel = $("#episode");
  sel.replaceChildren(...eps.map((e) => new Option(e.title, e.id)));
  const want = new URLSearchParams(location.search).get("ep") || store.get("lastEp", null);
  const id = eps.some((e) => e.id === want) ? want : eps[0]?.id;
  if (!id) { screen.innerHTML = `<p class="empty">Todavía no hay episodios.</p>`; return; }
  sel.value = id;
  await loadEpisode(id);
  sel.onchange = async () => { await loadEpisode(sel.value); toast("Las frases vendrán de este episodio"); };
  show(G ? "town" : "start");
})();

// for debugging and tests
window.bestiario = { S, get G() { return G; }, set G(v) { G = v; }, E, save };
