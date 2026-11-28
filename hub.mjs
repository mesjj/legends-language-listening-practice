// The general server: both games on one port, each live from its own folder (git worktree).
//   /leyendas/  → ../leyendas (Leyendas and the listening pages), its own server.js on an inner port
//   /rumbo/     → ../rumbo (Rumbo), its own server.js on another inner port
//   /           → a page linking both
// One origin, so the browser's saves are shared: Rumbo's transmissions read the Leyendas save.
// Both servers use this folder's data/ (DATA_DIR) and their own media/ (episodes are symlinks to this
// folder's media/). Old links (/rpg.html, /rumbo.html, /media/…) redirect to the right game.
//
//   node hub.mjs            PORT (8790), LEYENDAS_DIR, RUMBO_DIR, DATA_DIR to override
import http from "node:http";
import path from "node:path";
import fs from "node:fs";
import { spawn } from "node:child_process";

const HERE = path.dirname(new URL(import.meta.url).pathname);
const PORT = Number(process.env.PORT || 8790), HOST = "127.0.0.1";
const DATA_DIR = process.env.DATA_DIR || path.join(HERE, "data");
const GAMES = {
  leyendas: { dir: process.env.LEYENDAS_DIR || path.resolve(HERE, "../leyendas"), port: PORT + 3, name: "Leyendas", home: "rpg.html" },
  rumbo: { dir: process.env.RUMBO_DIR || path.resolve(HERE, "../rumbo"), port: PORT + 4, name: "Rumbo", home: "rumbo.html" },
};

// ---------------------------------------------------------------- the two game servers
const kids = [];
for (const [id, g] of Object.entries(GAMES)) {
  if (!fs.existsSync(path.join(g.dir, "server.js"))) { console.error(`${id}: no server.js in ${g.dir}`); process.exit(1); }
  const start = () => {
    const env = { ...process.env, PORT: String(g.port), HOST, DATA_DIR, BASE_PATH: `/${id}/` };
    delete env.MEDIA_DIR;
    const k = spawn(process.execPath, ["server.js"], { cwd: g.dir, env, stdio: ["ignore", "pipe", "pipe"] });
    const tag = (s) => s.toString().split("\n").filter(Boolean).map((l) => `[${id}] ${l}`).join("\n");
    k.stdout.on("data", (d) => console.log(tag(d)));
    k.stderr.on("data", (d) => console.error(tag(d)));
    // a crash (or a syntax error mid-edit) restarts it a moment later
    k.on("exit", (code) => { if (!stopping) { console.error(`[${id}] exited (${code}); restarting`); setTimeout(start, 1500); } });
    g.proc = k;
    kids.push(k);
  };
  start();
}
let stopping = false;
const stopAll = () => { stopping = true; for (const k of kids) k.kill(); process.exit(0); };
process.on("SIGINT", stopAll);
process.on("SIGTERM", stopAll);

// ---------------------------------------------------------------- routing
// Which game a path belongs to when it comes without a prefix, or with the other game's: Rumbo owns its
// page, its code and its clips; every other page (Leyendas, the listening pages) is Leyendas'.
const rumboOwns = (p) => p === "/rumbo.html" || p.startsWith("/rumbo/") || p.startsWith("/media/rumbo/");
const isPage = (p) => p === "/" || p.endsWith(".html");

const HOME = `<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Oído</title><link rel="icon" type="image/png" href="leyendas/favicon.png">
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#0b0f1a;color:#e6ebf5;font:16px/1.5 system-ui,sans-serif}
main{width:min(92vw,560px)}h1{margin:0 0 .2em}p{color:#8c98b3}a.g{display:block;padding:1.1em 1.3em;margin:.8em 0;border:1px solid #26324d;border-radius:12px;background:#101728;color:inherit;text-decoration:none}
a.g:hover{border-color:#7fd1c7}a.g b{font-size:1.3em;display:block}a.g span{color:#8c98b3}nav a{color:#7fd1c7;margin-right:1em}</style></head>
<body><main><h1>Oído</h1><p>Dos juegos para entrenar el oído en español.</p>
<a class="g" href="leyendas/rpg.html"><b>Leyendas</b><span>Un juego de rol: cada ataque es una frase del episodio que escuchas.</span></a>
<a class="g" href="rumbo/rumbo.html"><b>Rumbo</b><span>Comercio espacial: los precios, los chismes y los contratos solo llegan por audio.</span></a>
<nav><a href="leyendas/">Escuchar</a><a href="leyendas/play.html">Dictado</a><a href="leyendas/episodes.html">Episodios</a></nav></main></body></html>`;

function redirect(res, to) { res.writeHead(302, { Location: to }); res.end(); }

function proxy(req, res, id, rest) {
  const g = GAMES[id];
  const headers = { ...req.headers, host: `${HOST}:${g.port}` };
  const up = http.request({ host: HOST, port: g.port, method: req.method, path: rest, headers }, (r) => {
    res.writeHead(r.statusCode, r.headers);
    r.pipe(res);
  });
  up.on("error", () => { if (!res.headersSent) { res.writeHead(502, { "Content-Type": "text/plain; charset=utf-8" }); res.end(`${g.name} is starting or stopped (${g.dir}); try again in a moment.`); } else res.end(); });
  req.pipe(up);
}

http.createServer((req, res) => {
  const url = new URL(req.url, "http://x");
  const p = url.pathname, q = url.search;
  if (p === "/" || p === "/index.html") { res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" }); return res.end(HOME); }
  const m = p.match(/^\/(leyendas|rumbo)(\/.*)?$/);
  if (!m) return redirect(res, (rumboOwns(p) ? "/rumbo" : "/leyendas") + p + q); // an old link
  const [, id, rest = "/"] = m;
  if (rest === "/" && !p.endsWith("/")) return redirect(res, p + "/" + q);
  // a page of the other game: send it there, so each game always runs from its own folder
  if (id === "rumbo" && isPage(rest) && rest !== "/rumbo.html") return redirect(res, rest === "/" ? "/rumbo/rumbo.html" : "/leyendas" + rest + q);
  if (id === "leyendas" && rest === "/rumbo.html") return redirect(res, "/rumbo/rumbo.html" + q);
  proxy(req, res, id, rest + q);
}).listen(PORT, HOST, () => {
  console.log(`hub on http://${HOST}:${PORT}/`);
  for (const [id, g] of Object.entries(GAMES)) console.log(`  /${id}/ → ${g.dir} (port ${g.port})`);
});
