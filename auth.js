// Accounts for the online version: a users file, login sessions, and each player's saved game.
//   DATA_DIR/users.json     { username: { name, salt, hash } }   (scrypt; made by scripts/adduser.mjs)
//   DATA_DIR/sessions.json  { token: { u, exp } }
//   DATA_DIR/state/<username>.json   the game's saved keys
import fs from "node:fs";
import fsp from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";

const DAY = 864e5, SESSION_DAYS = 180;
export const COOKIE = "ley_s";

export function hashPass(pass, salt) {
  return crypto.scryptSync(String(pass), salt, 32).toString("hex");
}
export const validName = (u) => /^[a-z0-9_-]{2,32}$/.test(u);

async function writeJson(file, obj) {
  const tmp = file + ".tmp";
  await fsp.writeFile(tmp, JSON.stringify(obj));
  await fsp.rename(tmp, file);
}

export function makeAuth(dataDir) {
  const USERS = path.join(dataDir, "users.json");
  const SESSIONS = path.join(dataDir, "sessions.json");
  const STATE = path.join(dataDir, "state");
  fs.mkdirSync(STATE, { recursive: true });
  const users = () => { try { return JSON.parse(fs.readFileSync(USERS, "utf8")); } catch { return {}; } };
  let sessions = {};
  try { sessions = JSON.parse(fs.readFileSync(SESSIONS, "utf8")); } catch { /* none yet */ }
  const now = Date.now();
  for (const [t, s] of Object.entries(sessions)) if (s.exp < now) delete sessions[t];

  // a few wrong passwords from one address, then a pause
  const tries = new Map();
  const limited = (ip) => {
    const t = tries.get(ip);
    return t && t.n >= 8 && Date.now() - t.at < 15 * 60e3;
  };
  const failed = (ip) => {
    const t = tries.get(ip);
    tries.set(ip, { n: t && Date.now() - t.at < 15 * 60e3 ? t.n + 1 : 1, at: Date.now() });
  };

  return {
    login(username, pass, ip) {
      if (limited(ip)) return { error: "Demasiados intentos. Prueba de nuevo dentro de un rato.", status: 429 };
      const u = String(username || "").trim().toLowerCase();
      const rec = users()[u];
      const ok = rec && crypto.timingSafeEqual(Buffer.from(hashPass(pass, rec.salt), "hex"), Buffer.from(rec.hash, "hex"));
      if (!ok) { failed(ip); return { error: "Usuario o contraseña incorrectos.", status: 401 }; }
      tries.delete(ip);
      const token = crypto.randomBytes(32).toString("base64url");
      sessions[token] = { u, exp: Date.now() + SESSION_DAYS * DAY };
      writeJson(SESSIONS, sessions).catch(console.error);
      return { token, user: { id: u, name: rec.name || u } };
    },
    logout(token) {
      if (sessions[token]) { delete sessions[token]; writeJson(SESSIONS, sessions).catch(console.error); }
    },
    // the logged-in user for a request, or null
    user(req) {
      const token = cookie(req, COOKIE);
      const s = token && sessions[token];
      if (!s || s.exp < Date.now()) return null;
      const rec = users()[s.u];
      return rec ? { id: s.u, name: rec.name || s.u, token } : null;
    },
    async getState(u) {
      try { return JSON.parse(await fsp.readFile(path.join(STATE, `${u}.json`), "utf8")); } catch { return {}; }
    },
    async putState(u, state) {
      await writeJson(path.join(STATE, `${u}.json`), state);
    },
  };
}

export function cookie(req, name) {
  for (const part of String(req.headers.cookie || "").split(/;\s*/)) {
    const i = part.indexOf("=");
    if (i > 0 && part.slice(0, i) === name) return decodeURIComponent(part.slice(i + 1));
  }
  return null;
}
