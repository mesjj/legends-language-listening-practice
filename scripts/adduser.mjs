// Add a player to the online version, or give one a new password.
//   DATA_DIR=/var/lib/leyendas node scripts/adduser.mjs <username> "Shown name" [password]
// Without a password it makes one up and prints it.
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { hashPass, validName } from "../auth.js";

const [username, name, given] = process.argv.slice(2);
const dir = process.env.DATA_DIR;
if (!dir || !username) {
  console.error('usage: DATA_DIR=<dir> node scripts/adduser.mjs <username> "Shown name" [password]');
  process.exit(1);
}
const u = username.toLowerCase();
if (!validName(u)) { console.error("username: 2-32 of a-z 0-9 _ -"); process.exit(1); }
const file = path.join(dir, "users.json");
let users = {};
try { users = JSON.parse(fs.readFileSync(file, "utf8")); } catch { /* first user */ }
// easy to type on a phone: three short words' worth of lowercase letters and digits
const pass = given || Array.from(crypto.randomBytes(12), (b) => "abcdefghjkmnpqrstuvwxyz23456789"[b % 31]).join("").replace(/(.{4})(?!$)/g, "$1-");
const salt = crypto.randomBytes(16).toString("hex");
users[u] = { name: name || users[u]?.name || username, salt, hash: hashPass(pass, salt) };
fs.mkdirSync(dir, { recursive: true });
fs.writeFileSync(file + ".tmp", JSON.stringify(users, null, 1), { mode: 0o600 });
fs.renameSync(file + ".tmp", file);
console.log(`${u} (${users[u].name})  password: ${pass}`);
