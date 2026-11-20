// Writes scripts/lpc_items.json (which sets and uniques use each base item) for build_lpc.py.
import { writeFileSync } from "fs";
import { UNIQUES, SETS, BASE } from "../public/rpg/data.js";
const root = (b) => BASE[b]?.root || b; // reinforced and elite bases use their root's art
const sets = {}, uniques = {};
for (const s of SETS) for (const it of s.pieces) (sets[root(it.base)] ??= []).includes(s.id) || sets[root(it.base)].push(s.id);
for (const u of UNIQUES) (uniques[root(u.base)] ??= []).push(u.name);
writeFileSync(new URL("./lpc_items.json", import.meta.url), JSON.stringify({ sets, uniques }, null, 1));
console.log("sets", Object.keys(sets).length, "uniques", UNIQUES.length);
