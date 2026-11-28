// Background music, synthesized (WebAudio, no files): one piece per place, the village and each zone's
// scene. Off unless you turn it on (remembered on this device). The Spanish always wins: while a line
// plays, the music drops almost to nothing and comes back after.
//
// Each piece is a few parameters (tempo, metre, key, chords, which instruments play which steps) and a
// melody made once from a fixed seed, so it is the same piece every time. 32 bars, then it loops:
// 4 bars without the tune, then the tune in A A B A, then 4 bars of rest.

let ctx = null, out = null, duck = null, echo = null, echoIn = null;
let on = localStorage.getItem("rpgMusic") === "1";
let busy = () => false;
let place = null, cur = null, timer = null;
const VOL = 0.22, DUCKED = 0.07;

export const isOn = () => on;
export function setBusy(fn) { busy = fn; }
export function setOn(v) {
  on = v; localStorage.setItem("rpgMusic", v ? "1" : "0");
  if (v) start(place); else stopAll();
}
// where you are: "aldea" or a scene id; null for silence. Changing place crossfades.
export function setPlace(p) {
  if (p === place && (cur || !on)) return;
  place = p;
  if (on) start(p);
}

function init() {
  if (ctx) return ctx;
  const C = window.AudioContext || window.webkitAudioContext;
  if (!C) return null;
  ctx = new C();
  out = ctx.createGain(); out.gain.value = VOL;
  duck = ctx.createGain(); duck.gain.value = 1;
  out.connect(duck); duck.connect(ctx.destination);
  // one echo for the pieces that want space (a stone room, a cold valley)
  echoIn = ctx.createGain(); echoIn.gain.value = 0;
  echo = ctx.createDelay(1.5); echo.delayTime.value = 0.42;
  const fb = ctx.createGain(); fb.gain.value = 0.38;
  const lp = ctx.createBiquadFilter(); lp.type = "lowpass"; lp.frequency.value = 2200;
  echoIn.connect(echo); echo.connect(lp); lp.connect(fb); fb.connect(echo); lp.connect(out);
  // browsers start audio only after a click: resume on the next one
  const wake = () => { if (ctx.state === "suspended") ctx.resume(); };
  addEventListener("pointerdown", wake); addEventListener("keydown", wake);
  return ctx;
}

// ---------- instruments ----------
const hz = (m) => 440 * 2 ** ((m - 69) / 12);
function env(g, t, a, peak, len, rel = 0.08) {
  g.gain.setValueAtTime(0.0001, t);
  g.gain.exponentialRampToValueAtTime(peak, t + a);
  g.gain.setTargetAtTime(0.0001, t + Math.max(a, len), rel);
}
function osc(type, f, t, stop, dest, detune = 0) {
  const o = ctx.createOscillator(); o.type = type; o.frequency.value = f; o.detune.value = detune;
  o.connect(dest); o.start(t); o.stop(stop); return o;
}
function voice(dest, vol, send) {
  const g = ctx.createGain(); g.connect(dest);
  if (send) { const s = ctx.createGain(); s.gain.value = send; g.connect(s); s.connect(echoIn); }
  return g;
}
const INST = {
  // plucked string (tiple, harp, bandola): a bright wave through a closing filter
  pluck(dest, m, t, len, vol, o = {}) {
    const g = voice(dest, vol, o.send), f = ctx.createBiquadFilter();
    f.type = "lowpass"; f.Q.value = 2;
    f.frequency.setValueAtTime(o.bright || 3200, t); f.frequency.exponentialRampToValueAtTime(400, t + 0.35);
    f.connect(g); env(g, t, 0.004, vol, 0.02, o.decay || 0.18);
    osc(o.wave || "triangle", hz(m), t, t + 1.5, f); osc("square", hz(m), t, t + 1.5, f, 7).frequency.value = hz(m);
  },
  // marimba (chonta): a sine and its fourth partial, the partial gone at once
  marimba(dest, m, t, len, vol, o = {}) {
    const g = voice(dest, vol, o.send); env(g, t, 0.003, vol, 0.01, o.decay || 0.16);
    osc("sine", hz(m), t, t + 1.2, g);
    const g2 = voice(dest, vol * 0.35); env(g2, t, 0.002, vol * 0.35, 0.005, 0.03); osc("sine", hz(m) * 3.98, t, t + 0.3, g2);
  },
  // flute / ocarina / sung line: soft attack, a little vibrato, a breath of noise
  flute(dest, m, t, len, vol, o = {}) {
    const g = voice(dest, vol, o.send); env(g, t, o.attack || 0.06, vol, len * 0.9, 0.12);
    const v = ctx.createOscillator(), vg = ctx.createGain(); v.frequency.value = 5.2; vg.gain.value = hz(m) * 0.006;
    v.connect(vg); const main = osc(o.wave || "sine", hz(m), t, t + len + 0.8, g); vg.connect(main.frequency); v.start(t); v.stop(t + len + 0.8);
    if (o.breath) { const n = noiseSrc(t, len), nf = ctx.createBiquadFilter(), ng = voice(dest, vol * o.breath); nf.type = "bandpass"; nf.frequency.value = hz(m) * 2; nf.Q.value = 4; n.connect(nf); nf.connect(ng); env(ng, t, 0.03, vol * o.breath, len * 0.5, 0.1); }
  },
  // a reed (clarinet-ish): a square, darkened
  reed(dest, m, t, len, vol, o = {}) {
    const g = voice(dest, vol, o.send), f = ctx.createBiquadFilter(); f.type = "lowpass"; f.frequency.value = 1100; f.connect(g);
    env(g, t, 0.05, vol, len * 0.85, 0.1); osc("square", hz(m), t, t + len + 0.6, f);
  },
  bass(dest, m, t, len, vol, o = {}) {
    const g = voice(dest, vol); env(g, t, 0.01, vol, Math.min(len, 0.4), o.decay || 0.15); osc(o.wave || "triangle", hz(m), t, t + len + 0.8, g);
  },
  // a held chord: two detuned saws, filtered soft, slow in and out
  pad(dest, ms, t, len, vol, o = {}) {
    const f = ctx.createBiquadFilter(); f.type = "lowpass"; f.frequency.value = o.cut || 900;
    const g = voice(dest, vol, o.send); f.connect(g);
    g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(vol, t + len * 0.35); g.gain.setTargetAtTime(0.0001, t + len * 0.8, len * 0.15);
    for (const m of ms) { osc(o.wave || "sawtooth", hz(m), t, t + len + 1, f, -6); osc(o.wave || "sawtooth", hz(m), t, t + len + 1, f, 6); }
  },
  // a bell (the abyss): inharmonic partials, a long ring
  bell(dest, m, t, len, vol, o = {}) {
    for (const [r, k] of [[1, 1], [2.76, 0.5], [5.4, 0.25]]) { const g = voice(dest, vol * k, o.send); env(g, t, 0.004, vol * k, 0.01, 0.9 / r); osc("sine", hz(m) * r, t, t + 4, g); }
  },
  kick(dest, t, vol) { const g = voice(dest, vol); env(g, t, 0.003, vol, 0.02, 0.12); const o = osc("sine", 110, t, t + 0.5, g); o.frequency.setValueAtTime(110, t); o.frequency.exponentialRampToValueAtTime(42, t + 0.18); },
  tom(dest, t, vol, f0 = 190) { const g = voice(dest, vol); env(g, t, 0.003, vol, 0.01, 0.09); const o = osc("sine", f0, t, t + 0.4, g); o.frequency.exponentialRampToValueAtTime(f0 * 0.6, t + 0.15); },
  shaker(dest, t, vol) { const n = noiseSrc(t, 0.08), f = ctx.createBiquadFilter(), g = voice(dest, vol); f.type = "highpass"; f.frequency.value = 6000; n.connect(f); f.connect(g); env(g, t, 0.004, vol, 0.01, 0.025); },
};
let noiseBuf = null;
function noiseSrc(t, len) {
  if (!noiseBuf) { noiseBuf = ctx.createBuffer(1, ctx.sampleRate, ctx.sampleRate); const d = noiseBuf.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1; }
  const s = ctx.createBufferSource(); s.buffer = noiseBuf; s.loop = true; s.start(t); s.stop(t + len + 0.5); return s;
}
// sounds of the place, now and then
const FX = {
  wind(dest, t) { const n = noiseSrc(t, 6), f = ctx.createBiquadFilter(), g = voice(dest, 0.05); f.type = "bandpass"; f.Q.value = 1.2; f.frequency.setValueAtTime(400, t); f.frequency.linearRampToValueAtTime(900, t + 3); f.frequency.linearRampToValueAtTime(350, t + 6); n.connect(f); f.connect(g); g.gain.setValueAtTime(0.0001, t); g.gain.linearRampToValueAtTime(0.05, t + 2.5); g.gain.linearRampToValueAtTime(0.0001, t + 6); },
  bubbles(dest, t) { for (let i = 0; i < 3; i++) { const s = t + i * 0.13 + Math.random() * 0.05, g = voice(dest, 0.05); env(g, s, 0.005, 0.05, 0.02, 0.04); const o = osc("sine", 300, s, s + 0.2, g); o.frequency.exponentialRampToValueAtTime(700 + Math.random() * 400, s + 0.08); } },
  birds(dest, t) { const n = 2 + Math.floor(Math.random() * 3), f0 = 2600 + Math.random() * 1400; for (let i = 0; i < n; i++) { const s = t + i * 0.14, g = voice(dest, 0.03); env(g, s, 0.005, 0.03, 0.04, 0.03); const o = osc("sine", f0, s, s + 0.15, g); o.frequency.exponentialRampToValueAtTime(f0 * 1.4, s + 0.07); } },
  fire(dest, t) { for (let i = 0; i < 6; i++) { const s = t + Math.random() * 1.5, n = noiseSrc(s, 0.03), f = ctx.createBiquadFilter(), g = voice(dest, 0.06); f.type = "highpass"; f.frequency.value = 2500; n.connect(f); f.connect(g); env(g, s, 0.002, 0.06, 0.005, 0.01); } },
  drip(dest, t) { const g = voice(dest, 0.05, 0.6); env(g, t, 0.003, 0.05, 0.01, 0.05); const o = osc("sine", 1400, t, t + 0.2, g); o.frequency.exponentialRampToValueAtTime(2400, t + 0.05); },
};

// ---------- the pieces ----------
// step: seconds per step; bar: steps per bar; scale: semitones from the root; prog: chord degrees, one per bar;
// parts: [instrument, steps it plays on, options]. lead: the tune's instrument and its rhythms (step, length).
const MAJ = [0, 2, 4, 5, 7, 9, 11], MIN = [0, 2, 3, 5, 7, 8, 10], DOR = [0, 2, 3, 5, 7, 9, 10], PHR = [0, 1, 3, 5, 7, 8, 10], HARM = [0, 2, 3, 5, 7, 8, 11], LOC = [0, 1, 3, 5, 6, 8, 10];
const TRACKS = {
  // the village: a bambuco's lilt in 6/8, a tiple strumming, a flute
  aldea: { step: 0.115, bar: 12, root: 55, scale: MAJ, prog: [0, 3, 4, 0, 5, 3, 4, 0], seed: 11,
    pad: { vol: 0.05, cut: 700 }, bass: [[0, 6, 9], 0.16],
    arp: ["pluck", [0, 2, 3, 5, 6, 8, 9, 11], { vol: 0.07, bright: 2600, oct: 0 }],
    perc: [["shaker", [0, 2, 3, 5, 6, 8, 9, 11], 0.05], ["kick", [0, 6], 0.12]],
    lead: ["flute", { vol: 0.1, breath: 0.25, oct: 12 }, [[[0, 3], [3, 3], [6, 2], [8, 4]], [[0, 2], [2, 1], [3, 3], [6, 6]], [[0, 6], [6, 3], [9, 3]], [[0, 3], [3, 2], [5, 1], [6, 6]]]] },
  // the páramo: slow and misty, a drone, a lonely flute with an echo, the wind
  paramo: { step: 0.2, bar: 16, root: 50, scale: DOR, prog: [0, 0, 6, 0, 3, 3, 6, 4], seed: 23,
    drone: [38, 45], pad: { vol: 0.06, cut: 600, send: 0.3 }, bass: null,
    arp: ["pluck", [0, 6, 10], { vol: 0.04, bright: 1600, oct: 0, send: 0.5, decay: 0.5 }], perc: [],
    lead: ["flute", { vol: 0.1, breath: 0.4, oct: 12, send: 0.45, attack: 0.15 }, [[[0, 8], [8, 8]], [[0, 6], [6, 2], [8, 8]], [[0, 16]], [[4, 4], [8, 8]]]],
    fx: ["wind", 0.12] },
  // the ciénaga: murky, a low marimba, a reed, bubbles
  cienaga: { step: 0.15, bar: 16, root: 45, scale: PHR, prog: [0, 0, 1, 0, 5, 6, 1, 0], seed: 37,
    pad: { vol: 0.045, cut: 500 }, bass: [[0, 10], 0.18, "sine"],
    arp: ["marimba", [0, 3, 6, 10, 12], { vol: 0.1, oct: -12, decay: 0.25 }],
    perc: [["tom", [0, 6, 8], 0.08, 120]],
    lead: ["reed", { vol: 0.055, oct: 12 }, [[[0, 4], [6, 2], [8, 6]], [[2, 2], [4, 4], [10, 6]], [[0, 12]], [[0, 2], [3, 3], [8, 8]]]],
    fx: ["bubbles", 0.3] },
  // the Chocó: a currulao: chonta marimba, bombo, cununo, guasá, birds
  selva: { step: 0.085, bar: 12, root: 52, scale: MIN, prog: [0, 0, 4, 4, 3, 3, 4, 0], seed: 41,
    pad: null, bass: [[0, 6], 0.16, "sine"],
    arp: ["marimba", [0, 2, 3, 5, 6, 8, 9, 11], { vol: 0.09, oct: 12 }],
    perc: [["kick", [0, 6], 0.16], ["tom", [3, 9, 10], 0.09, 220], ["shaker", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 0.035]],
    lead: ["flute", { vol: 0.08, wave: "triangle", oct: 12 }, [[[0, 3], [3, 3], [6, 6]], [[0, 2], [2, 1], [3, 3], [6, 3], [9, 3]], [[0, 6], [6, 6]], [[3, 3], [6, 2], [8, 4]]]],
    fx: ["birds", 0.25] },
  // the llanos: a joropo, fast, harp runs, maracas, a bandola; fire crackling
  llano: { step: 0.072, bar: 12, root: 50, scale: HARM, prog: [0, 0, 4, 4, 0, 0, 3, 4], seed: 53,
    pad: null, bass: [[0, 4, 8], 0.15],
    arp: ["pluck", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], { vol: 0.055, bright: 3600, oct: 12, run: true }],
    perc: [["shaker", [0, 2, 3, 4, 6, 8, 9, 10], 0.05]],
    lead: ["pluck", { vol: 0.09, wave: "sawtooth", bright: 2400, oct: 12, decay: 0.12 }, [[[0, 2], [2, 2], [4, 2], [6, 2], [8, 4]], [[0, 4], [4, 2], [6, 2], [8, 2], [10, 2]], [[0, 6], [6, 6]], [[0, 2], [2, 2], [4, 4], [8, 4]]]],
    fx: ["fire", 0.3] },
  // the ruins: an ocarina, a hollow pad, stone echoes, a slow drum
  ruinas: { step: 0.17, bar: 16, root: 48, scale: MIN, prog: [0, 5, 3, 4, 0, 5, 6, 4], seed: 67,
    pad: { vol: 0.055, cut: 800, wave: "triangle", send: 0.3 }, bass: [[0], 0.14, "sine"],
    arp: null, perc: [["tom", [0, 10], 0.1, 90]],
    lead: ["flute", { vol: 0.1, oct: 12, send: 0.5, attack: 0.04 }, [[[0, 4], [4, 4], [8, 8]], [[0, 2], [2, 2], [4, 8], [12, 4]], [[0, 16]], [[4, 4], [8, 4], [12, 4]]]],
    fx: ["drip", 0.2] },
  // the abyss: drones a tritone apart, a heartbeat, far bells, almost no tune
  abismo: { step: 0.22, bar: 16, root: 47, scale: LOC, prog: [0, 0, 1, 0, 4, 0, 1, 0], seed: 79,
    drone: [35, 41], pad: { vol: 0.04, cut: 400, send: 0.3 }, bass: null,
    arp: ["bell", [0], { vol: 0.05, oct: 0, send: 0.6, sparse: 0.5 }],
    perc: [["kick", [0, 2], 0.11]],
    lead: ["reed", { vol: 0.035, oct: 0, send: 0.5 }, [[[0, 16]], [[8, 8]], [[0, 8]], [[4, 12]]]],
    fx: ["drip", 0.15] },
  // a boss: driving and dark, a low ostinato, war drums, a drone, a reed crying over it
  jefe: { step: 0.105, bar: 16, root: 45, scale: HARM, prog: [0, 0, 5, 4, 0, 0, 1, 4], seed: 97,
    drone: [33, 40], pad: { vol: 0.035, cut: 500, send: 0.2 }, bass: [[0, 3, 6, 8, 11, 14], 0.17, "sawtooth"],
    arp: ["marimba", [0, 2, 4, 6, 8, 10, 12, 14], { vol: 0.07, oct: -12, decay: 0.12 }],
    perc: [["kick", [0, 6, 8], 0.15], ["tom", [12, 13, 14, 15], 0.07, 150], ["tom", [4], 0.08, 95]],
    lead: ["reed", { vol: 0.05, oct: 12, send: 0.35 }, [[[0, 6], [6, 2], [8, 8]], [[0, 4], [4, 4], [8, 4], [12, 4]], [[0, 16]], [[2, 2], [4, 6], [10, 6]]]],
    fx: null },
};

// a small seeded random, so a piece's tune is always the same
function rng(seed) { return () => { seed |= 0; seed = (seed + 0x6d2b79f5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const note = (T, deg, oct = 0) => T.root + oct + T.scale[((deg % 7) + 7) % 7] + 12 * Math.floor(deg / 7);
const chord = (T, d) => [note(T, d), note(T, d + 2), note(T, d + 4)];
// the tune: phrase A and phrase B, 4 bars each; each note near the last, landing on chord tones
function makeTune(T) {
  const R = rng(T.seed), rh = T.lead[2], phrase = (startDeg) => {
    let deg = startDeg; const bars = [];
    for (let b = 0; b < 4; b++) {
      const c = T.prog[b % T.prog.length], notes = [];
      for (const [s, len] of rh[Math.floor(R() * rh.length)]) {
        const tones = [c, c + 2, c + 4].map((x) => x + 7 * Math.round((deg - x) / 7));
        deg = s === 0 || R() < 0.45 ? tones.reduce((a, x) => (Math.abs(x - deg) < Math.abs(a - deg) ? x : a)) : deg + (R() < 0.5 ? -1 : 1) * (R() < 0.8 ? 1 : 2);
        deg = Math.max(-2, Math.min(9, deg));
        notes.push([s, len, deg]);
      }
      bars.push(notes);
    }
    return bars;
  };
  return { A: phrase(2), B: phrase(4) };
}

// ---------- playing ----------
function start(p) {
  if (!init()) return;
  if (cur?.id === p) return;
  if (cur) fadeOut(cur);
  cur = null;
  if (!p || !TRACKS[p]) return;
  const T = TRACKS[p], g = ctx.createGain();
  g.gain.setValueAtTime(0.0001, ctx.currentTime); g.gain.exponentialRampToValueAtTime(1, ctx.currentTime + 2.5); g.connect(out);
  echoIn.gain.setTargetAtTime(1, ctx.currentTime, 0.5);
  cur = { id: p, T, g, tune: makeTune(T), step: 0, at: ctx.currentTime + 0.15, drones: [] };
  if (T.drone) for (const m of T.drone) { const dg = voice(g, 0.035, 0.3); dg.gain.setValueAtTime(0.0001, ctx.currentTime); dg.gain.exponentialRampToValueAtTime(0.035, ctx.currentTime + 4); cur.drones.push(osc("sawtooth", hz(m), ctx.currentTime, ctx.currentTime + 36000, (() => { const f = ctx.createBiquadFilter(); f.type = "lowpass"; f.frequency.value = 300; f.connect(dg); return f; })())); }
  if (!timer) timer = setInterval(tick, 60);
}
function fadeOut(c) {
  const t = ctx.currentTime;
  c.g.gain.cancelScheduledValues(t); c.g.gain.setValueAtTime(Math.max(0.0001, c.g.gain.value), t); c.g.gain.exponentialRampToValueAtTime(0.0001, t + 1.5);
  for (const d of c.drones) d.stop(t + 1.6);
  setTimeout(() => c.g.disconnect(), 1800);
}
function stopAll() {
  if (cur && ctx) fadeOut(cur);
  if (echoIn) echoIn.gain.setTargetAtTime(0, ctx.currentTime, 0.3); // what was sent to the echo goes too
  cur = null;
  clearInterval(timer); timer = null;
}
function tick() {
  if (!ctx || !cur) return;
  duck.gain.setTargetAtTime(busy() ? DUCKED : 1, ctx.currentTime, 0.25);
  if (ctx.state !== "running") { cur.at = ctx.currentTime + 0.15; return; }
  while (cur.at < ctx.currentTime + 0.25) { play(cur, cur.step, cur.at); cur.step++; cur.at += cur.T.step; }
}
const LOOP_BARS = 32;
function play(c, n, t) {
  const T = c.T, s = n % T.bar, barN = Math.floor(n / T.bar) % LOOP_BARS, deg = T.prog[barN % T.prog.length], ch = chord(T, deg), dest = c.g;
  const barLen = T.step * T.bar;
  if (s === 0 && T.pad) INST.pad(dest, ch.map((m) => m - 12), t, barLen, T.pad.vol, T.pad);
  if (T.bass && T.bass[0].includes(s)) INST.bass(dest, (s === T.bass[0][0] ? ch[0] : T.bass[0].indexOf(s) % 2 ? ch[2] : ch[0]) - 24, t, T.step * 3, T.bass[1], { wave: T.bass[2] });
  if (T.arp && T.arp[1].includes(s)) {
    const o = T.arp[2], i = T.arp[1].indexOf(s);
    if (!o.sparse || Math.random() < o.sparse) {
      const m = o.run ? note(T, deg + [0, 2, 4, 7, 9, 11, 14, 11, 9, 7, 4, 2][i % 12], o.oct) : ch[i % 3] + (o.oct || 0) + (i >= 3 ? 12 : 0);
      INST[T.arp[0]](dest, m, t, T.step, o.vol, o);
    }
  }
  for (const [k, steps, vol, f] of T.perc) if (steps.includes(s)) INST[k](dest, t, vol * (s === 0 ? 1 : 0.8), f);
  // the tune: bars 4–19 A A B A, then rest until the loop comes round
  const sec = barN - 4;
  if (sec >= 0 && sec < 16) {
    const ph = [c.tune.A, c.tune.A, c.tune.B, c.tune.A][Math.floor(sec / 4)][sec % 4], o = T.lead[1];
    for (const [st, len, dg] of ph) if (st === s) INST[T.lead[0]](dest, note(T, dg, o.oct), t, len * T.step, o.vol, o);
  }
  if (T.fx && s === 0 && Math.random() < T.fx[1]) FX[T.fx[0]](dest, t + Math.random() * barLen * 0.5);
}
// A zone added on 2026-11-27 (data.js ZONE_VARIANTS) plays a piece built on one of these: the same band, its own
// seed (another tune), and its own key, mode and tempo.
const SCALES = { MAJ, MIN, DOR, PHR, HARM, LOC };
export function addTrack(id, { base, seed, root, scale, tempo = 1 }) {
  const T = TRACKS[base];
  if (!T || TRACKS[id]) return;
  TRACKS[id] = { ...T, seed, root: root ?? T.root, scale: SCALES[scale] || T.scale, step: T.step * tempo };
}
export const PLACES = Object.keys(TRACKS);
export const nowPlaying = () => cur?.id || null;
