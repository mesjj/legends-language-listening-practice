// The game's interface in English. The game is written in Spanish; with English chosen, the page is
// translated as it's drawn: every text node and tooltip is looked up in rpg/i18n/en.json, made by
// scripts/i18n (extract.mjs pulls every Spanish text out of the source, translate.mjs has Claude
// translate the new ones). {0}, {1}… in an entry stand for values filled in at runtime; those values
// are translated too when they have an entry (a monster's name, a zone). Item names are put together
// from their parts in English order. What you're learning is never translated: the episode's lines,
// your answers, Anki cards and Claude's explanations (SKIP). en.manual.json holds hand-written entries
// for text the code builds out of pieces (they win over en.json).
import { store } from "../listen-core.js";

export const LANGS = { es: "Español", en: "English" };
export const lang = () => (store.get("uiLang", "es") in LANGS ? store.get("uiLang", "es") : "es");
export function setLang(l) { store.set("uiLang", l); location.reload(); }

const SKIP = ".diff, .you .typed, .nearmiss b, .nearmiss s, .gtag, .cardfront, .cardback, #explainOut, .explain-out, .gtext, .wchips, .cloze, .skeleton, .lsent, .lq, #answer, .tunjoline, [translate=no], textarea, input, script, style, svg";
const ATTRS = ["title", "placeholder", "aria-label", "alt"];
let exact = null, buckets = null, adjectives = null;
const cache = new Map();
// what was left in Spanish, to find what's missing: leyendasI18nMisses() in the console
const misses = new Set(), SPANISH = /[áéíóúñ¿¡]|(^|\s)(de|la|el|los|las|que|con|por|para|una|del|tus?|sin|más|cada|frase|y|se|te|al)(\s|$)/i;
globalThis.leyendasI18nMisses = () => [...misses];
const done = new WeakMap(); // node -> the text we put there

// words that come after the noun in Spanish and before it in English (Poción de vida menor → Minor Life Potion)
const ADJ = ["superior", "menor", "mayor", "perfecto", "perfecta"];
function compile(dict) {
  exact = new Map(); buckets = new Map(); adjectives = new Set(ADJ);
  const put = (es, en, derived = false) => {
    if (es === en) return;
    // a value at an edge is often markup or an optional ending: the rest works on its own too
    const e = /^\{(\d+)\}\s*([\s\S]+)$/.exec(es) || /^([\s\S]+?)\s*\{(\d+)\}$/.exec(es);
    if (e) {
      const n = /^\{/.test(es) ? e[1] : e[2], rest = /^\{/.test(es) ? e[2] : e[1];
      if (en.includes(`{${n}}`) && /\p{L}/u.test(rest)) put(rest.trim(), en.replace(`{${n}}`, "").replace(/\s+/g, " ").trim(), true);
    }
    // a value glued to a word (dominad{0}: an ending chosen at runtime) can't be matched reliably
    if (/\p{L}\{\d+\}|\}\p{L}/u.test(es)) return;
    if (!/\{\d+\}/.test(es)) { if (!derived || !exact.has(es)) exact.set(es, en); return; }
    const order = [];
    const src = es.replace(/[.*+?^$()[\]\\|]/g, "\\$&").replace(/\{(\d+)\}/g, (_, n) => { order.push(+n); return "(.+?)"; });
    const lit = es.split(/\{\d+\}/)[0], key = lit.length >= 2 ? lit.slice(0, 2).toLowerCase() : "";
    if (!buckets.has(key)) buckets.set(key, []);
    buckets.get(key).push({ re: new RegExp(`^${src}$`, "s"), order, en });
  };
  for (const [es, en] of Object.entries(dict)) {
    // item prefixes are written Afilad@: Afilado, Afilada (and plurals)
    if (es.includes("@")) {
      for (const v of ["o", "a", "os", "as"]) { const w = es.replace(/@/g, v); put(w, en); adjectives.add(w); }
      continue;
    }
    put(es, en);
  }
  // longer, more specific patterns first
  for (const list of buckets.values()) list.sort((a, b) => b.re.source.length - a.re.source.length);
}

// item names and other short names made of known parts ("Espada Afilada del Cóndor")
function byParts(t) {
  const tok = t.split(" ");
  if (tok.length < 2 || tok.length > 7) return null;
  const best = Array(tok.length + 1).fill(null);
  best[0] = [];
  for (let i = 0; i < tok.length; i++) {
    if (!best[i]) continue;
    for (let j = Math.min(tok.length, i + 4); j > i; j--) {
      const es = tok.slice(i, j).join(" ");
      const en = exact.get(es);
      if (en && (!best[j] || best[j].length > best[i].length + 1)) best[j] = [...best[i], { es, en }];
    }
  }
  const parts = best[tok.length];
  if (!parts || parts.length < 2) return null;
  // adjectives go before the noun in English
  const adj = parts.filter((p) => adjectives.has(p.es)), rest = parts.filter((p) => !adjectives.has(p.es));
  return [...adj, ...rest].map((p) => p.en).join(" ");
}

export function tr(s, depth = 0) {
  if (!exact || !s || !/\p{L}/u.test(s)) return s;
  const m = /^([\s·,:;–—-]*)([\s\S]*?)(\s*)$/.exec(s);
  const core = m[2].replace(/\s+/g, " ");
  if (!core) return s;
  let out = cache.get(core);
  if (out === undefined) {
    out = exact.get(core) ?? null;
    if (out == null) {
      for (const list of [buckets.get(core.slice(0, 2).toLowerCase()), buckets.get("")]) {
        for (const p of list || []) {
          const g = p.re.exec(core);
          if (!g) continue;
          out = p.en.replace(/\{(\d+)\}/g, (_, n, at) => { const v = g[p.order.indexOf(+n) + 1] ?? ""; const t = depth < 2 ? tr(v, depth + 1) : v; return at > 0 && /^The /.test(t) ? "t" + t.slice(1) : t; });
          break;
        }
        if (out != null) break;
      }
    }
    if (out == null) out = byParts(core);
    if (out == null && depth < 2) {
      const pieces = core.split(/( · | \+ |, |: |\(|\))/);
      if (pieces.length > 1) { const t = pieces.map((x) => (/\p{L}/u.test(x) ? tr(x, depth + 1) : x)).join(""); if (t !== core) out = t; }
    }
    if (out == null) { out = core; if (depth === 0 && SPANISH.test(core)) misses.add(core); }
    if (cache.size > 20000) cache.clear();
    cache.set(core, out);
  }
  return out === core ? s : m[1] + out + m[3];
}

const skipped = (el) => !!el?.closest?.(SKIP);
function doText(n) {
  if (done.get(n) === n.data) return;
  const p = n.parentElement;
  if (!p || skipped(p)) return;
  const t = tr(n.data);
  done.set(n, t);
  if (t !== n.data) n.data = t;
}
function doAttrs(el) {
  if (skipped(el) && !el.matches?.("textarea, input")) return;
  for (const a of ATTRS) {
    const v = el.getAttribute?.(a);
    if (!v) continue;
    const t = tr(v);
    if (t !== v) el.setAttribute(a, t);
  }
}
function walk(root) {
  if (root.nodeType === 3) return doText(root);
  if (root.nodeType !== 1 || skipped(root)) return;
  doAttrs(root);
  const it = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT, {
    acceptNode: (n) => (n.nodeType === 1 && n.matches(SKIP) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT),
  });
  for (let n = it.nextNode(); n; n = it.nextNode()) n.nodeType === 3 ? doText(n) : doAttrs(n);
}

export async function startI18n() {
  document.documentElement.lang = lang();
  if (lang() === "es") return;
  try {
    const [auto, manual] = await Promise.all([`rpg/i18n/${lang()}.json`, `rpg/i18n/${lang()}.manual.json`].map((u) => fetch(u).then((r) => (r.ok ? r.json() : {}))));
    compile({ ...auto, ...manual });
  } catch { return; }
  document.title = tr(document.title);
  walk(document.body);
  new MutationObserver((muts) => {
    for (const m of muts) {
      if (m.type === "characterData") doText(m.target);
      else if (m.type === "attributes") doAttrs(m.target);
      else m.addedNodes.forEach(walk);
    }
  }).observe(document.body, { subtree: true, childList: true, characterData: true, attributes: true, attributeFilter: ATTRS });
}
