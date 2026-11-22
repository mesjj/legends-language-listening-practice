// Little synthesized sounds (WebAudio, no files): hits, the chime of a right answer that climbs
// with your streak, loot by rarity. Muted with M; the choice is remembered.
let ctx = null, master = null;
let muted = localStorage.getItem("rpgMuted") === "1";
// The Spanish audio always wins: no effect starts while it's playing (busy), a manual play cuts the
// effects off (hush), and the next line waits for them to finish, plus a short gap (quiet).
let busy = () => false, endsAt = 0;
export function setBusy(fn) { busy = fn; }
export function hush() {
  if (!ctx || !master) return;
  master.disconnect();
  master = ctx.createGain();
  master.gain.value = 0.32;
  master.connect(ctx.destination);
  endsAt = 0;
}
export function quiet(gap = 250) {
  const left = ctx ? Math.max(0, endsAt - ctx.currentTime) * 1000 : 0;
  return new Promise((r) => setTimeout(r, left ? left + gap : 0));
}
export const isMuted = () => muted;
export function setMuted(v) { muted = v; localStorage.setItem("rpgMuted", v ? "1" : "0"); }

function ac() {
  if (muted || busy()) return null;
  return openCtx();
}
function openCtx() {
  if (!ctx) {
    const C = window.AudioContext || window.webkitAudioContext;
    if (!C) return null;
    ctx = new C();
    master = ctx.createGain();
    master.gain.value = 0.32;
    master.connect(ctx.destination);
  }
  if (ctx.state === "suspended") ctx.resume();
  return ctx;
}
// one note: type, frequency (or [from, to] glide), start offset, length, volume
function tone(type, f, at = 0, len = 0.15, vol = 0.5, { attack = 0.005 } = {}) {
  const c = ac();
  if (!c) return;
  const t = c.currentTime + at;
  const o = c.createOscillator(), g = c.createGain();
  o.type = type;
  const [f0, f1] = Array.isArray(f) ? f : [f, f];
  o.frequency.setValueAtTime(f0, t);
  if (f1 !== f0) o.frequency.exponentialRampToValueAtTime(f1, t + len);
  g.gain.setValueAtTime(0.0001, t);
  g.gain.exponentialRampToValueAtTime(vol, t + attack);
  g.gain.exponentialRampToValueAtTime(0.0001, t + len);
  o.connect(g).connect(master);
  o.start(t);
  o.stop(t + len + 0.02);
  endsAt = Math.max(endsAt, t + len);
}
function noise(at = 0, len = 0.12, vol = 0.4, freq = 1200, q = 0.8) {
  const c = ac();
  if (!c) return;
  const t = c.currentTime + at;
  const buf = c.createBuffer(1, Math.ceil(c.sampleRate * len), c.sampleRate);
  const d = buf.getChannelData(0);
  for (let i = 0; i < d.length; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / d.length);
  const s = c.createBufferSource(), f = c.createBiquadFilter(), g = c.createGain();
  s.buffer = buf;
  f.type = "bandpass"; f.frequency.value = freq; f.Q.value = q;
  g.gain.value = vol;
  s.connect(f).connect(g).connect(master);
  s.start(t);
  endsAt = Math.max(endsAt, t + len);
}
// a held, shaped voice: oscillator (glide from f0 to f1 over len), vibrato, through a band-pass (a vowel)
function voice(type, f0, f1, at, len, vol, { vib = 0, vibHz = 5.5, band = 0, q = 3, dest = null, attack = 0.04 } = {}) {
  const c = dest ? ctx : ac();
  if (!c) return;
  const t = c.currentTime + at;
  const o = c.createOscillator(), g = c.createGain();
  o.type = type;
  o.frequency.setValueAtTime(f0, t);
  o.frequency.exponentialRampToValueAtTime(f1, t + len);
  if (vib) {
    const l = c.createOscillator(), lg = c.createGain();
    l.frequency.value = vibHz; lg.gain.value = vib;
    l.connect(lg).connect(o.frequency); l.start(t); l.stop(t + len + 0.05);
  }
  g.gain.setValueAtTime(0.0001, t);
  g.gain.exponentialRampToValueAtTime(vol, t + attack);
  g.gain.setValueAtTime(vol, t + Math.max(attack, len - 0.15));
  g.gain.exponentialRampToValueAtTime(0.0001, t + len);
  let node = o;
  if (band) { const f = c.createBiquadFilter(); f.type = "bandpass"; f.frequency.value = band; f.Q.value = q; o.connect(f); node = f; }
  node.connect(g).connect(dest || master);
  o.start(t); o.stop(t + len + 0.05);
  if (!dest) endsAt = Math.max(endsAt, t + len);
}
function rumble(at, len, vol, f0 = 120, f1 = 40) {
  const c = ac();
  if (!c) return;
  const t = c.currentTime + at;
  const buf = c.createBuffer(1, Math.ceil(c.sampleRate * len), c.sampleRate), d = buf.getChannelData(0);
  for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
  const s = c.createBufferSource(), f = c.createBiquadFilter(), g = c.createGain();
  s.buffer = buf; f.type = "lowpass"; f.Q.value = 4;
  f.frequency.setValueAtTime(f0, t); f.frequency.exponentialRampToValueAtTime(f1, t + len);
  g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(vol, t + 0.08); g.gain.exponentialRampToValueAtTime(0.0001, t + len);
  s.connect(f).connect(g).connect(master); s.start(t);
  endsAt = Math.max(endsAt, t + len);
}
// the Silbón's scale: do re mi fa sol la si
const SCALE = [1046.5, 1174.7, 1318.5, 1396.9, 1568, 1760, 1975.5];
// what each boss sounds like when it appears, and when it lets go
const BOSS_SOUND = {
  // the whistle climbing the scale, each note fainter: the nearer he is, the further away it sounds
  silbon: () => SCALE.forEach((f, i) => { voice("sine", f * 0.99, f, i * 0.3, 0.32, 0.3 * (1 - i / 8.5), { vib: 9, vibHz: 6 }); noise(i * 0.3, 0.3, 0.04 * (1 - i / 8), 5000, 1); }),
  // a heavy splash, a growl from under the water
  mohan: () => { noise(0, 0.7, 0.6, 700, 0.6); rumble(0.1, 1.4, 0.7, 260, 50); voice("sawtooth", 72, 58, 0.35, 1.2, 0.16, { vib: 6, vibHz: 9, band: 300, q: 2 }); },
  // leaves thrashing, a branch creaking
  madremonte: () => { for (let i = 0; i < 9; i++) noise(i * 0.09 + Math.random() * 0.05, 0.12, 0.25, 3200 + Math.random() * 1500, 1.5); voice("sawtooth", 140, 92, 0.5, 1.1, 0.12, { vib: 14, vibHz: 13, band: 600, q: 6 }); },
  // a roar of fire rushing past
  bolafuego: () => { rumble(0, 1.5, 0.9, 300, 1800); noise(0.05, 1.3, 0.35, 900, 0.5); for (let i = 0; i < 10; i++) noise(0.2 + Math.random() * 1.1, 0.03, 0.3, 4000, 1); },
  // «¡ay!»: a long falling wail
  llorona: () => { voice("triangle", 760, 470, 0, 1.5, 0.3, { vib: 22, vibHz: 5, band: 900, q: 2.5 }); voice("sine", 1140, 700, 0.04, 1.45, 0.08, { vib: 30, vibHz: 5 }); },
  // a low laugh: ja, ja, ja
  mandingas: () => { [0, 0.2, 0.4, 0.62].forEach((t, i) => voice("sawtooth", 118 - i * 6, 96 - i * 6, t, 0.17, 0.34, { band: 650, q: 3, attack: 0.02 })); rumble(0.8, 1, 0.5, 90, 40); },
};
// pentatonic steps, so a long streak keeps climbing without sounding wrong
const STEP = [0, 2, 4, 7, 9, 12, 14, 16, 19, 21, 24];
const note = (base, k) => base * Math.pow(2, STEP[Math.min(k, STEP.length - 1)] / 12);

export const sfx = {
  // a right answer: two notes that climb with the streak; perfect adds a sparkle
  correct(streak = 0, perfect = false) {
    const k = Math.min(streak, 10), b = 523.25;
    tone("triangle", note(b, k), 0, 0.16, 0.42);
    tone("triangle", note(b, k + 2), 0.07, 0.22, 0.38);
    if (perfect) { tone("sine", note(b * 2, k + 4), 0.14, 0.3, 0.22); tone("sine", note(b * 2, k + 6), 0.2, 0.35, 0.16); }
  },
  // getting a lost streak back: each of the 3 answers has its own sound, climbing like a lock giving way:
  // 1 a low bell, 2 a higher bell with an echo, 3 the streak comes back (a rising run and a shimmer)
  regain(k) {
    if (k <= 1) { tone("sine", 392, 0, 0.7, 0.3); tone("triangle", 784, 0.01, 0.35, 0.14); noise(0, 0.05, 0.12, 3000, 3); }
    else if (k === 2) { tone("sine", 587.3, 0, 0.7, 0.3); tone("sine", 880, 0.09, 0.8, 0.22); tone("triangle", 1174.7, 0.09, 0.3, 0.1); noise(0, 0.05, 0.14, 3800, 3); }
    else {
      [0, 4, 7, 12, 16, 19, 24].forEach((s, i) => tone("triangle", 392 * Math.pow(2, s / 12), i * 0.055, 0.45, 0.26));
      [0, 7, 12].forEach((s) => tone("sine", 784 * Math.pow(2, s / 12), 0.4, 1.3, 0.12));
      noise(0.38, 0.8, 0.16, 6500, 2);
    }
  },
  partial() { tone("triangle", 392, 0, 0.14, 0.3); tone("triangle", 440, 0.07, 0.16, 0.22); },
  miss() { tone("sine", [220, 140], 0, 0.22, 0.35); },
  hit(crit = false) { noise(0, 0.09, crit ? 0.7 : 0.45, crit ? 2400 : 1600); tone("square", [crit ? 180 : 140, 60], 0, 0.1, crit ? 0.3 : 0.18); },
  hurt() { noise(0, 0.14, 0.35, 500); tone("sawtooth", [160, 90], 0, 0.16, 0.15); },
  kill() { tone("square", [300, 80], 0, 0.22, 0.14); noise(0.02, 0.2, 0.25, 900); },
  // loot, by how good it is
  drop(rarity) {
    const top = { ancestral: 1, legendario: 2, mitico: 3, relic: 3 }[rarity];
    if (top) {
      // a longer run, higher each tier, and a bell over it
      const run = [0, 4, 7, 12, 16, 19, 24].slice(0, 4 + top);
      run.forEach((s, i) => tone("triangle", 330 * Math.pow(2, (s + top * 2) / 12), i * 0.08, 0.6, 0.3));
      tone("sine", 1760 * (1 + top * 0.12), run.length * 0.08, 1 + top * 0.3, 0.16);
      if (top === 3) noise(run.length * 0.08, 0.6, 0.15, 5000, 2);
    } else if (rarity === "unique" || rarity === "set") { [0, 4, 7, 12, 16].forEach((s, i) => tone("triangle", 392 * Math.pow(2, s / 12), i * 0.07, 0.5, 0.3)); tone("sine", 1568, 0.36, 0.7, 0.14); }
    else if (rarity === "rare") { [0, 7, 12].forEach((s, i) => tone("triangle", 523 * Math.pow(2, s / 12), i * 0.06, 0.32, 0.28)); }
    else tone("triangle", 660, 0, 0.12, 0.2);
  },
  identify() { [0, 4, 7, 11, 14].forEach((s, i) => tone("sine", 587 * Math.pow(2, s / 12), i * 0.05, 0.4, 0.22)); },
  spell(score = 1) { tone("sawtooth", [200, 200 + 900 * score], 0, 0.45, 0.12); tone("sine", [400, 400 + 1200 * score], 0.05, 0.5, 0.2); noise(0.3, 0.3, 0.3 * score, 3000, 2); },
  // a zone fully mastered: a little brass fanfare, then a bright chord
  fanfare() {
    [[0, 0], [4, 0.12], [7, 0.24], [12, 0.36], [7, 0.52], [12, 0.62]].forEach(([n, t]) => tone("square", 392 * Math.pow(2, n / 12), t, t > 0.5 ? 0.6 : 0.16, 0.11));
    [0, 4, 7, 12, 16].forEach((n) => tone("triangle", 392 * Math.pow(2, n / 12), 0.62, 1.1, 0.12));
    noise(0.62, 0.5, 0.18, 6000, 2);
  },
  levelup() { [0, 4, 7, 12].forEach((s, i) => tone("square", 392 * Math.pow(2, s / 12), i * 0.1, 0.3, 0.12)); },
  // bosses: their entrance, the note the Silbón has reached (fainter as it climbs), their big blow
  bossIntro(kind) { BOSS_SOUND[kind]?.(); },
  whistle(k) { const f = SCALE[Math.min(6, k)]; voice("sine", f * 0.99, f, 0, 0.5, 0.3 * (1 - k / 8.5), { vib: 9, vibHz: 6 }); noise(0, 0.4, 0.04, 5000, 1); },
  armed() { voice("sawtooth", 110, 220, 0, 0.6, 0.12, { band: 500, q: 4 }); noise(0.5, 0.2, 0.2, 400); },
  bossBlow(kind) { rumble(0, 0.6, 0.9, 400, 60); noise(0, 0.25, 0.7, 900, 0.7); tone("square", [90, 40], 0, 0.3, 0.3); BOSS_SOUND[kind] && kind !== "silbon" && kind !== "llorona" && kind !== "mohan" && noise(0.05, 0.4, 0.3, 2400); },
  scream() { voice("sawtooth", 1250, 880, 0, 1.2, 0.18, { vib: 40, vibHz: 7, band: 1400, q: 2 }); voice("triangle", 1900, 1300, 0.05, 1.1, 0.08, { vib: 50, vibHz: 7 }); noise(0, 1.1, 0.12, 3000, 0.8); },
  bossDeath() { rumble(0, 2.2, 0.8, 500, 35); tone("sawtooth", [220, 40], 0.1, 1.8, 0.12); noise(0.3, 1.4, 0.2, 1200, 0.5); },
  // dice clattering on wood; a win: a bright little run
  dice() { for (let i = 0; i < 7; i++) { const t = i * 0.07 + Math.random() * 0.04; noise(t, 0.025, 0.35 * (1 - i / 9), 2600 + Math.random() * 1800, 4); tone("square", 900 + Math.random() * 500, t, 0.02, 0.04); } },
  diceWin() { [0, 4, 7, 12].forEach((s, i) => tone("triangle", 659 * Math.pow(2, s / 12), i * 0.06, 0.3, 0.26)); },
  coin() { tone("square", 1318, 0, 0.06, 0.12); tone("square", 1760, 0.05, 0.12, 0.12); },
};

// The Llorona's cry, under the line she's about to hit you with: it plays alongside the Spanish (which
// silences every other effect), quieter than the voice, falling «ay»s for as long as the line lasts.
export function wailOver(seconds) {
  if (muted || !openCtx()) return;
  const out = ctx.createGain();
  out.gain.value = 0.16;
  out.connect(ctx.destination);
  for (let t = 0; t < seconds; t += 1.1) {
    const f = 620 + Math.random() * 120;
    voice("triangle", f, f * 0.68, t, 1.2, 0.5, { vib: 20, vibHz: 5, band: 900, q: 2, dest: out });
    voice("sine", f * 1.5, f, t + 0.05, 1.1, 0.15, { vib: 26, vibHz: 5, dest: out });
  }
  setTimeout(() => out.disconnect(), (seconds + 1.5) * 1000);
}
