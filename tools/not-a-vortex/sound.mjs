// Original sound design, synthesised here (no samples, no licences). Reads timeline.json.
// Family "orbital machinery": the myth is a swirling, tremolo vortex drone that tape-stops when it is called wrong;
// each planet in the flyby gets a pass-by whoosh and a bell tuned lower the farther out it is; the true motion is a
// rising rush of wind with a steady low engine; the core is a slow heartbeat drone with the S2 whip; the black hole
// reveal takes the biggest hit after a held breath. Every write wraps modulo the loop length, so the file loops.
import fs from 'node:fs';
import { execFileSync } from 'node:child_process';
const spec = JSON.parse(fs.readFileSync(new URL('./timeline.json', import.meta.url)));
const SR = 48000, DUR = spec.duration, L = Math.round(SR * DUR);
const bus = () => [new Float32Array(L), new Float32Array(L)];
const HIT = bus(), SFX = bus(), BED = bus(), SEND = bus();
let seed = 777; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647 * 2 - 1;
const put = (b, i, v, pan) => { const k = ((i % L) + L) % L; b[0][k] += v * Math.sqrt((1 - pan) / 2); b[1][k] += v * Math.sqrt((1 + pan) / 2); };
const env = (t, a, d, len) => Math.min(1, t / a) * Math.exp(-t / d) * Math.min(1, (len - t) / 0.01);
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const smooth = (a, b, x) => { const s = clamp((x - a) / (b - a)); return s * s * (3 - 2 * s); };

function tone(b, at, len, f0, f1, g, { a = 0.004, d = 1, pan = 0, drive = 0, send = 0, curve = 1 } = {}) {
  let ph = 0; const n = Math.round(len * SR), s = Math.round(at * SR);
  for (let j = 0; j < n; j++) { const t = j / SR, u = j / n, f = f0 + (f1 - f0) * Math.pow(u, curve); ph += 2 * Math.PI * f / SR;
    let v = Math.sin(ph); if (drive) v = Math.tanh(v * (1 + drive)) / Math.tanh(1 + drive);
    v *= g * env(t, a, d, len); put(b, s + j, v, pan); if (send) put(SEND, s + j, v * send, pan); }
}
function noise(b, at, len, g, { lp = 8000, hp = 0, a = 0.002, d = 0.2, pan = 0, rev = false, send = 0, lpEnd = null, panEnd = null } = {}) {
  const n = Math.round(len * SR), s = Math.round(at * SR); let y = 0, x1 = 0, h = 0;
  for (let j = 0; j < n; j++) { const t = j / SR, cut = lpEnd ? lp + (lpEnd - lp) * (j / n) : lp, al = 1 - Math.exp(-2 * Math.PI * cut / SR);
    const x = rnd(); y += al * (x - y); let v = y;
    if (hp) { const ah = Math.exp(-2 * Math.PI * hp / SR); h = ah * (h + v - x1); x1 = v; v = h; }
    const e = rev ? Math.pow(t / len, 2.2) * Math.min(1, (len - t) / 0.004) : env(t, a, d, len);
    const p = panEnd === null ? pan : pan + (panEnd - pan) * (j / n);
    put(b, s + j, v * g * e, p); if (send) put(SEND, s + j, v * g * e * send, p); }
}
function hit(at, size, root = 98) {
  noise(HIT, at - 0.5 * size, 0.5 * size - 0.05, 0.3 * size, { lp: 400, lpEnd: 6000, rev: true });
  noise(HIT, at, 0.09, 0.85 * size, { lp: 12000, hp: 2200, a: 0.0005, d: 0.024, send: 0.4 });
  tone(HIT, at, 1.0, root * 3.2, root, 0.9 * size, { a: 0.002, d: 0.34, drive: 2.4, send: 0.3, curve: 0.45 });
  for (const [m, gg, dd] of [[1, 0.22, 2.2], [1.5, 0.12, 1.6], [2.01, 0.12, 1.4], [3.0, 0.07, 0.9]])   // brass-free "orbital" partials (fifths)
    tone(HIT, at, 3.2, root * 2 * m, root * 2 * m * 0.996, gg * size, { a: 0.004, d: dd, send: 0.7, pan: (m > 1.6 ? 0.3 : -0.3) });
  tone(HIT, at, 1.8, 52, 38, 0.6 * size, { a: 0.004, d: 0.6 });
}
const type = (txt, t0, t1, g = 0.06) => { for (let k = 0; k < txt.length; k++) if (txt[k] !== ' ') noise(SFX, t0 + (t1 - t0) * k / txt.length, 0.02, g, { hp: 2800, lp: 9000, d: 0.005, pan: rnd() * 0.3 }); };

// ---- 0.0-2.6 the myth vortex: swirling drone (pan circles at the coil rate), tape-stop on IT'S WRONG ----
hit(0, 0.7, 110);
{ let ph = [0, 0, 0], pos = 0;
  for (let j = 0; j < L; j++) { const t = j / SR; const tm = t > 28.4 ? t - DUR : t; if (tm < -0.6 || tm > 2.6) continue;
    const stop = smooth(1.5, 2.3, tm), rate = 1 - 0.92 * stop, g = 0.06 * smooth(-0.6, 0.1, tm) * (1 - smooth(2.2, 2.6, tm));
    pos += 2 * Math.PI * 1.3 * rate / SR; const pan = 0.7 * Math.sin(pos);
    let v = 0; [[146.8, 1], [220, 0.6], [293.7, 0.35]].forEach(([f, a], k) => { ph[k] += 2 * Math.PI * f * rate * (1 + 0.004 * Math.sin(pos * 3)) / SR; v += a * Math.sin(ph[k] + 0.3 * Math.sin(ph[k] * 2)); });
    v *= g * (0.75 + 0.25 * Math.sin(pos * 4)); put(SFX, j, v, pan); put(SEND, j, v * 0.3, pan); } }
noise(SFX, -0.6, 3.0, 0.07, { lp: 1800, hp: 200, a: 0.4, d: 9, send: 0.2, pan: -0.5, panEnd: 0.5 });
type("YOU'VE SEEN THIS.", 0.03, 0.5);
tone(HIT, 1.25, 0.5, 150, 118, 0.42, { a: 0.002, d: 0.17, drive: 3 }); noise(SFX, 1.25, 0.06, 0.28, { lp: 3000, hp: 300, d: 0.02 });   // stamp
tone(SFX, 1.5, 0.9, 420, 40, 0.06, { a: 0.01, d: 2, curve: 1.8, drive: 1 });                                                          // tape stop
// ---- 2.6 the Sun: a deep fire roar and crackle, then the flyby ----
noise(SFX, 2.45, 0.35, 0.16, { lp: 300, lpEnd: 6000, hp: 120, rev: true, send: 0.2 });
hit(2.6, 0.45, 82);
noise(SFX, 2.6, 0.9, 0.16, { lp: 900, hp: 100, a: 0.05, d: 0.6, send: 0.2 });
for (let k = 0; k < 40; k++) noise(SFX, 2.6 + Math.random() * 0.75, 0.012, 0.05, { hp: 1800, lp: 7000, d: 0.004, pan: rnd() * 0.6 });
type('THE SUN', 2.65, 2.9);
const T0 = 3.3, TS = 0.9625;
const BELL = [1046.5, 880, 784, 659.3, 523.3, 440, 392, 329.6];        // farther out = lower
for (let i = 0; i < 8; i++) { const at = T0 + TS * i, pan = i % 2 ? 0.45 : -0.45;
  noise(SFX, at - 0.42, 0.5, 0.16, { lp: 500, lpEnd: 7000, hp: 150, rev: true, send: 0.2, pan: -pan, panEnd: pan });     // pass-by whoosh into the planet
  tone(SFX, at - 0.05, 2.0, BELL[i], BELL[i], 0.055, { a: 0.003, d: 0.55, send: 0.6, pan });
  tone(SFX, at - 0.05, 1.2, BELL[i] * 2.76, BELL[i] * 2.76, 0.012, { d: 0.18, send: 0.5, pan });
  tone(SFX, at - 0.05, 0.9, BELL[i] / 4, BELL[i] / 4.2, 0.05, { a: 0.01, d: 0.3, send: 0.2 });
  type(spec.planets[i].name, at - 0.12, at + 0.1, 0.05); }
// warm pad under the tour (D major-ish), swelling into the wide shot
for (const [f, g, p] of [[146.83, 0.04, -0.3], [220, 0.03, 0.3], [293.66, 0.022, -0.1], [369.99, 0.014, 0.2]]) {
  const s0 = Math.round(2.6 * SR), s1 = Math.round(13.1 * SR); let ph = 0, ph2 = 0;
  for (let j = s0; j < s1; j++) { const t = j / SR, e = smooth(2.6, 3.6, t) * (1 - smooth(12.8, 13.05, t)) * (1 + 0.8 * smooth(10.8, 12.6, t)); ph += 2 * Math.PI * f / SR; ph2 += 2 * Math.PI * f * 1.005 / SR;
    const v = (Math.sin(ph) + Math.sin(ph2)) * 0.5 * g * e; put(BED, j, v, p); put(SEND, j, v * 0.3, p); } }
// ---- 11-13.6 the wide shot: a long rising swell, then the held breath ----
noise(SFX, 10.75, 1.7, 0.12, { lp: 7000, lpEnd: 600, hp: 120, a: 0.3, d: 3, send: 0.3 });
type('THE WHOLE SYSTEM IS TILTED', 11.3, 11.8, 0.04); type('60° TO THE GALAXY', 11.8, 12.2, 0.04); type('NOW LET THE SUN MOVE.', 12.85, 13.35, 0.05);
tone(SFX, 12.0, 1.5, 220, 440, 0.03, { a: 1.0, d: 3, send: 0.5, curve: 1.4 });
noise(SFX, 13.1, 0.48, 0.14, { lp: 300, lpEnd: 8000, hp: 200, rev: true, send: 0.3 });
// ---- 13.6 the Sun moves: big hit, steady engine, rising rush of wind (true motion) ----
hit(13.6, 0.95, 92);
{ const s0 = Math.round(13.6 * SR), s1 = Math.round(20.2 * SR); let ph = 0, ph2 = 0, y = 0;
  for (let j = s0; j < s1; j++) { const t = j / SR, e = smooth(13.6, 14.4, t) * (1 - smooth(19.6, 20.2, t));
    ph += 2 * Math.PI * 98 / SR; ph2 += 2 * Math.PI * 147 * (1 + 0.002 * Math.sin(t * 3)) / SR;
    const eng = (Math.tanh(1.8 * Math.sin(ph)) * 0.035 + Math.sin(ph2) * 0.018) * e * (0.85 + 0.15 * Math.sin(2 * Math.PI * 0.6 * t));
    const cut = 400 + 3000 * smooth(13.6, 19.4, t); const al = 1 - Math.exp(-2 * Math.PI * cut / SR); y += al * (rnd() - y);
    put(SFX, j, eng, 0); put(SFX, j, y * 0.09 * e, 0.3 * Math.sin(t * 0.7)); put(SEND, j, y * 0.03 * e, 0); } }
for (const [txt, a, b] of [['230 KM/S', 13.75, 14.0], ["EARTH'S REAL PATH:", 15.0, 15.4], ['A STRETCHED WAVE.', 15.4, 15.8], ["PLANETS DON'T TRAIL BEHIND.", 16.45, 16.95],
  ['HALF THE TIME, THEY LEAD.', 16.95, 17.4], ["NEPTUNE'S PATH:", 17.85, 18.15], ['ALMOST STRAIGHT.', 18.15, 18.5], ['NOT A VORTEX.', 18.95, 19.25]]) type(txt, a, b, 0.045);
// a soft glass ping on each line (Earth teal, lead gold, Neptune blue)
for (const [at, f] of [[15.4, 659.3], [16.95, 784], [18.15, 523.3]]) tone(SFX, at, 1.6, f, f, 0.04, { a: 0.003, d: 0.5, send: 0.6 });
hit(18.95, 0.55, 110);
// ---- 19.8-23.4 pull out to the galaxy: long airy rise, a choir-like pad, low gong on the centre ----
noise(SFX, 19.6, 2.6, 0.14, { lp: 300, lpEnd: 5000, hp: 150, a: 1.0, d: 4, send: 0.4 });
for (const [f, g, p] of [[110, 0.03, -0.4], [164.8, 0.028, 0.4], [220, 0.024, -0.2], [277.2, 0.018, 0.2], [329.6, 0.014, 0]]) {
  const s0 = Math.round(20.0 * SR), s1 = Math.round(24.0 * SR); let ph = 0, ph2 = 0, ph3 = 0;
  for (let j = s0; j < s1; j++) { const t = j / SR, e = smooth(20.0, 21.4, t) * (1 - smooth(23.3, 23.9, t));
    ph += 2 * Math.PI * f / SR; ph2 += 2 * Math.PI * f * 1.006 / SR; ph3 += 2 * Math.PI * f * 0.994 / SR;
    const v = (Math.sin(ph) + 0.6 * Math.sin(ph2) + 0.6 * Math.sin(ph3) + 0.2 * Math.sin(3 * ph)) * g * e * 0.5; put(BED, j, v, p); put(SEND, j, v * 0.5, p); } }
tone(HIT, 21.4, 3.5, 98, 97, 0.12, { a: 0.01, d: 1.4, send: 0.6 }); tone(HIT, 21.4, 3.0, 147, 146.5, 0.07, { a: 0.01, d: 1.2, send: 0.6 });
type('ALL OF IT ORBITS', 21.4, 21.8, 0.04); type("THE GALAXY'S CENTRE", 21.8, 22.25, 0.04);
// ---- 23.4-24.6 dive into the core ----
noise(SFX, 23.3, 1.4, 0.2, { lp: 7000, lpEnd: 300, hp: 100, a: 0.4, d: 3, send: 0.3 });
tone(SFX, 23.3, 1.4, 900, 120, 0.045, { a: 0.3, d: 3, curve: 0.6 });
// ---- 24.4-27.6 the core: slow heartbeat drone, S2 whip at pericentre, held breath, the biggest hit on Sagittarius A* ----
{ const s0 = Math.round(24.4 * SR), s1 = Math.round(27.9 * SR); let ph = 0;
  for (let j = s0; j < s1; j++) { const t = j / SR, e = smooth(24.4, 25.0, t) * (1 - smooth(27.4, 27.9, t)) * (1 - 0.85 * smooth(25.75, 25.95, t) * (1 - smooth(26.1, 26.3, t)));
    ph += 2 * Math.PI * 110 / SR; const beat = Math.exp(-((t * 1.1) % 1) * 7) + 0.6 * Math.exp(-(((t * 1.1) + 0.72) % 1) * 9);
    const v = (Math.tanh(2.2 * Math.sin(ph)) * 0.05 + Math.sin(ph * 0.5) * 0.04) * e * (0.35 + 0.65 * beat); put(SFX, j, v, 0); put(SEND, j, v * 0.2, 0); } }
// S2 pericentre passage (2018.4 in the scene clock lands at 25.59 s): a fast doppler zing
{ const at = 25.59; tone(SFX, at - 0.35, 0.7, 700, 1900, 0.05, { a: 0.3, d: 0.4, curve: 2, pan: -0.6, send: 0.4 }); tone(SFX, at, 0.6, 1900, 500, 0.05, { a: 0.003, d: 0.25, curve: 0.5, pan: 0.6, send: 0.4 });
  noise(SFX, at - 0.3, 0.6, 0.1, { lp: 2000, lpEnd: 9000, hp: 600, a: 0.25, d: 0.2, pan: -0.6, panEnd: 0.6 }); }
type('THESE STARS ORBIT', 24.9, 25.3, 0.04); type('SOMETHING INVISIBLE.', 25.3, 25.8, 0.04);
noise(SFX, 25.62, 0.46, 0.13, { lp: 300, lpEnd: 7000, hp: 200, rev: true, send: 0.3 });
hit(26.1, 1.25, 73.4);
for (const [f, g, p] of [[73.4, 0.04, 0], [110, 0.04, -0.4], [146.8, 0.035, 0.4], [220, 0.022, -0.2]]) tone(SFX, 26.2, 1.6, f, f * 1.001, g, { a: 0.4, d: 4, send: 0.5, pan: p });
type('A BLACK HOLE · 4 MILLION SUNS', 26.35, 26.8, 0.035);
// ---- 27.6 NOW YOU KNOW, plunge home, rising tone and the vortex swirl returning into frame 0 ----
type('NOW YOU KNOW.', 27.6, 27.9, 0.06);
noise(SFX, 27.6, 1.0, 0.18, { lp: 6000, lpEnd: 500, hp: 120, a: 0.2, d: 3, send: 0.25 });
noise(SFX, 28.1, 0.88, 0.16, { lp: 300, lpEnd: 7000, hp: 150, rev: true, send: 0.2 });
tone(SFX, 28.0, 1.0, 220, 440, 0.03, { a: 0.6, d: 3, curve: 1.5 });

// ---- reverb on the send (Schroeder, run over two loops so the tail wraps) ----
function reverb([l, r]) {
  const out = [new Float32Array(L), new Float32Array(L)];
  [l, r].forEach((x, c) => { const combs = [1687, 1601, 2053, 2251].map(d => ({ d: d + c * 31, buf: new Float32Array(d + c * 31), i: 0 }));
    const aps = [347, 113].map(d => ({ buf: new Float32Array(d), i: 0 }));
    for (let k = 0; k < 2 * L; k++) { const inp = x[k % L]; let s = 0;
      for (const cb of combs) { const y = cb.buf[cb.i]; cb.buf[cb.i] = inp + y * 0.86; cb.i = (cb.i + 1) % cb.d; s += y; }
      s *= 0.25; for (const ap of aps) { const y = ap.buf[ap.i]; const v = -s + y; ap.buf[ap.i] = s + y * 0.5; ap.i = (ap.i + 1) % ap.buf.length; s = v; }
      if (k >= L) out[c][k - L] = s; } });
  return out;
}
const VERB = reverb(SEND);
const hp90 = ([l, r]) => [l, r].forEach(x => { const a = Math.exp(-2 * Math.PI * 90 / SR); let y = 0, p = 0; for (let k = 0; k < 2 * L; k++) { const v = x[k % L]; y = a * (y + v - p); p = v; if (k >= L) x[k - L] = y; } });
hp90(SFX); hp90(BED); hp90(VERB);
const HITS = [0, 2.6, 13.6, 18.95, 26.1];
const duck = t => { let g = 1; for (const h of HITS) { const dt = t - h; if (dt >= 0 && dt < 1.2) g = Math.min(g, 0.45 + 0.55 * dt / 1.2); if (dt > -0.05 && dt < 0) g = Math.min(g, 0.05); }
  if (t > 13.1 && t < 13.55) g = Math.min(g, 0.2); if (t > 25.75 && t < 26.05) g = Math.min(g, 0.12); return g; };
const mix = [new Float32Array(L), new Float32Array(L)];
for (let c = 0; c < 2; c++) for (let k = 0; k < L; k++) { const d = duck(k / SR); mix[c][k] = HIT[c][k] + (SFX[c][k] * 1.7 + BED[c][k] * 1.7) * d + VERB[c][k] * 0.5; }
let peak = 0; for (const x of mix) for (const v of x) peak = Math.max(peak, Math.abs(v));
const buf = Buffer.alloc(44 + L * 4);
buf.write('RIFF', 0); buf.writeUInt32LE(36 + L * 4, 4); buf.write('WAVEfmt ', 8); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(2, 22);
buf.writeUInt32LE(SR, 24); buf.writeUInt32LE(SR * 4, 28); buf.writeUInt16LE(4, 32); buf.writeUInt16LE(16, 34); buf.write('data', 36); buf.writeUInt32LE(L * 4, 40);
for (let k = 0; k < L; k++) for (let c = 0; c < 2; c++) { const v = Math.tanh(1.3 * mix[c][k] / peak) / Math.tanh(1.3); buf.writeInt16LE(Math.round(v * 0.89 * 32767), 44 + k * 4 + c * 2); }
fs.mkdirSync(new URL('./output/', import.meta.url), { recursive: true });
const raw = new URL('./output/sound_raw.wav', import.meta.url).pathname, fin = new URL('./output/sound.wav', import.meta.url).pathname;
fs.writeFileSync(raw, buf);
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', raw, '-af', 'loudnorm=I=-15:TP=-3:LRA=9,alimiter=limit=0.66:level=false', '-ar', '48000', fin]);
console.log('sound.wav written; raw peak', peak.toFixed(3));
