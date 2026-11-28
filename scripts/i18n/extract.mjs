// Pull every piece of Spanish UI text out of the game's source: string and template literals, split
// at HTML tags, with ${…} as a wildcard (\u0001); attribute texts (title, placeholder, aria-label) too.
import fs from "fs";
import * as acorn from "acorn";
import { simple } from "acorn-walk";
// usage: node scripts/i18n/extract.mjs  (writes scripts/i18n/strings.json)
const ROOT = new URL("../../", import.meta.url).pathname;
const files = process.argv.length > 2 ? process.argv.slice(2) : ["rpg/main.js", "rpg/data.js", "rpg/engine.js", "rpg/boss.js", "rpg/figure.js", "rpg/look.js", "listen-core.js", "sources.js", "rpg.html", "rpg/lpc/look.json", "rumbo/main.js", "rumbo/data.js", "rumbo.html"].map((f) => ROOT + "public/" + f);
const ENT = { "&nbsp;": " ", "&middot;": "·", "&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"', "&#39;": "'", "&times;": "×", "&mdash;": "—", "&ndash;": "–", "&hellip;": "…", "&rarr;": "→", "&larr;": "←" };
const dec = (t) => t.replace(/&[a-z#0-9]+;/g, (m) => ENT[m] ?? m);
const out = new Map();
const looksUI = (t) => {
  const lit = t.replace(/\u0001/g, " ");
  if (!/\p{L}{3}/u.test(lit)) return false;
  if (/^[\w$.-]+$/.test(lit.trim()) && !/^\p{Lu}\p{Ll}+$/u.test(lit.trim())) return false; // identifiers, class names
  if (/^(https?:|\.\/|rpg\/|media\/|api\/|#|\.|data:|var\(|rgba?\(|url\()/.test(lit.trim())) return false;
  if (/[{};]\s*$|^\s*[.#][\w-]+\s*\{|=>|\bfunction\b|\bconst\b/.test(lit)) return false;
  if (/^[\w-]+(\s+[\w-]+)*$/.test(lit.trim()) && !/\s/.test(lit.trim()) && !/[áéíóúñ]/.test(lit)) return /^\p{Lu}/u.test(lit.trim());
  if (/^[a-z0-9_-]+( [a-z0-9_-]+)+$/.test(lit.trim()) && /\b(on|hidden|got|here|far|primary|ghost|dim|small|locked|cleared|leech)\b/.test(lit)) return false;
  return true;
};
function add(raw, where) {
  let t = dec(raw).replace(/\s+/g, " ").trim();
  t = t.replace(/^[\s\u0001·,:;–—-]+|[\s\u0001]+$/g, (m) => (m.includes("\u0001") && m.trim() !== "" ? m : "")).trim();
  if (!t || !looksUI(t)) return;
  if (!out.has(t)) out.set(t, where);
}
function harvest(text, where) {
  // attribute texts inside tags
  for (const a of text.matchAll(/\b(?:title|placeholder|aria-label|alt)=(?:"([^"]*)"|'([^']*)')/g)) add(a[1] ?? a[2], where);
  for (const seg of text.split(/<[^>]*>/)) add(seg, where);
}
for (const f of files) {
  const src = fs.readFileSync(f, "utf8");
  if (f.endsWith(".json")) { JSON.stringify(JSON.parse(src), (k, v) => { if (typeof v === "string" && /^\p{Lu}[\p{L} ]+$/u.test(v)) add(v, f.split("/").pop()); return v; }); continue; }
  if (f.endsWith(".html")) { harvest(src.replace(/<(script|style)[\s\S]*?<\/\1>/g, ""), f.split("/").pop()); continue; }
  const ast = acorn.parse(src, { ecmaVersion: "latest", sourceType: "module", locations: true });
  simple(ast, {
    Literal(n) { if (typeof n.value === "string") harvest(n.value, `${f.split("/").pop()}:${n.loc.start.line}`); },
    TemplateLiteral(n) { harvest(n.quasis.map((q) => q.value.cooked ?? q.value.raw).join("\u0001"), `${f.split("/").pop()}:${n.loc.start.line}`); },
  });
}
const arr = [...out].map(([k, w]) => ({ es: k, at: w }));
fs.writeFileSync(process.env.OUT || ROOT + "scripts/i18n/strings.json", JSON.stringify(arr, null, 1));
console.log(arr.length, "strings");
