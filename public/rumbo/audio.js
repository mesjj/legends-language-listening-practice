// Rumbo's clip player: the radio filter is added live with WebAudio. Its level (0 to 1) comes from the
// station and the source: a band-pass at about 300 to 3,400 Hz, static under the voice and short
// dropouts. Level 0 plays the clip clean. Nothing else (music, effects) ever plays over a clip.
let ctx = null, chain = null;

function noiseBuffer(c) {
  // two seconds of pink-ish noise, looped
  const n = c.sampleRate * 2, b = c.createBuffer(1, n, c.sampleRate), d = b.getChannelData(0);
  let b0 = 0, b1 = 0, b2 = 0;
  for (let i = 0; i < n; i++) {
    const w = Math.random() * 2 - 1;
    b0 = 0.997 * b0 + w * 0.03; b1 = 0.985 * b1 + w * 0.03; b2 = 0.95 * b2 + w * 0.05;
    d[i] = (b0 + b1 + b2 + w * 0.08) * 0.5;
  }
  return b;
}

function setup(el) {
  ctx = new (window.AudioContext || window.webkitAudioContext)();
  const src = ctx.createMediaElementSource(el);
  const hp = ctx.createBiquadFilter(); hp.type = "highpass";
  const lp = ctx.createBiquadFilter(); lp.type = "lowpass";
  const mid = ctx.createBiquadFilter(); mid.type = "peaking"; mid.frequency.value = 1800; mid.Q.value = 0.8;
  const voice = ctx.createGain(); // dropouts dip this
  const hiss = ctx.createGain(); hiss.gain.value = 0;
  const hissBand = ctx.createBiquadFilter(); hissBand.type = "bandpass"; hissBand.frequency.value = 2500; hissBand.Q.value = 0.5;
  src.connect(hp).connect(lp).connect(mid).connect(voice).connect(ctx.destination);
  hissBand.connect(hiss).connect(ctx.destination);
  chain = { hp, lp, mid, voice, hiss, hissBand, noise: noiseBuffer(ctx), hissSrc: null, timer: null };
}

function setLevel(level) {
  const t = ctx.currentTime, on = level > 0;
  chain.hp.frequency.setValueAtTime(on ? 250 + 150 * level : 20, t);
  chain.lp.frequency.setValueAtTime(on ? 3800 - 900 * level : 20000, t);
  chain.mid.gain.setValueAtTime(on ? 4 * level : 0, t);
  chain.voice.gain.setValueAtTime(1, t);
}

function startStatic(level) {
  stopStatic();
  if (level <= 0) return;
  const s = ctx.createBufferSource();
  s.buffer = chain.noise; s.loop = true;
  s.connect(chain.hissBand);
  s.start();
  chain.hissSrc = s;
  chain.hiss.gain.setValueAtTime(0.05 + 0.22 * level, ctx.currentTime);
  // dropouts: the voice fades out for a moment and the static swells, more often on a worse band
  const tick = () => {
    const wait = (6 - 4.5 * level) * (0.6 + Math.random() * 0.8) * 1000;
    chain.timer = setTimeout(() => {
      if (!chain.hissSrc) return;
      const t = ctx.currentTime, len = 0.06 + 0.2 * level * Math.random();
      chain.voice.gain.setTargetAtTime(0.08, t, 0.01);
      chain.voice.gain.setTargetAtTime(1, t + len, 0.02);
      chain.hiss.gain.setTargetAtTime(0.1 + 0.4 * level, t, 0.01);
      chain.hiss.gain.setTargetAtTime(0.05 + 0.22 * level, t + len, 0.03);
      tick();
    }, wait);
  };
  tick();
}
function stopStatic() {
  clearTimeout(chain?.timer);
  if (chain?.hissSrc) { try { chain.hissSrc.stop(); } catch { /* already stopped */ } chain.hissSrc = null; }
  if (chain) chain.hiss.gain.setValueAtTime(0, ctx.currentTime);
}

// Play a clip through the radio. Resolves when it ends (or is stopped). onState(true/false) for the
// play indicator.
export async function playClip(el, url, { rate = 1, level = 0, onState = () => {} } = {}) {
  if (!ctx) setup(el);
  if (ctx.state === "suspended") await ctx.resume();
  stop(el);
  el.src = url;
  el.playbackRate = rate;
  el.preservesPitch = el.mozPreservesPitch = el.webkitPreservesPitch = true;
  setLevel(level);
  return new Promise((resolve) => {
    const done = () => { el.onended = el.onpause = el.onerror = null; stopStatic(); onState(false); resolve(); };
    el.onended = done; el.onpause = done; el.onerror = done;
    el.play().then(() => { startStatic(level); onState(true); }).catch(done);
  });
}
export function stop(el) {
  if (!el.paused) el.pause();
  if (chain) stopStatic();
}
