// Original sound design, synthesised here (no samples, no licences). Reads timeline.json.
// Family "orbital machinery": the myth is a swirling, tremolo vortex drone that tape-stops when it is called wrong;
// the real solar system arrives on a warm pad with a bell per planet, tuned lower the farther out it is; the true motion
// is a rising rush of wind with a steady low engine; the galaxy gets a choir-like pad and a low gong on Sagittarius A*;
// the lap ticks once per 10 million years and closes on a chime. Every write wraps modulo the loop length, so the file loops.
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
  for (let j = 0; j < L; j++) { const t = j / SR; const tm = t > DUR - 0.6 ? t - DUR : t; if (tm < -0.6 || tm > 2.6) continue;
    const stop = smooth(1.5, 2.3, tm), rate = 1 - 0.92 * stop, g = 0.06 * smooth(-0.6, 0.1, tm) * (1 - smooth(2.2, 2.6, tm));
    pos += 2 * Math.PI * 1.3 * rate / SR; const pan = 0.7 * Math.sin(pos);
    let v = 0; [[146.8, 1], [220, 0.6], [293.7, 0.35]].forEach(([f, a], k) => { ph[k] += 2 * Math.PI * f * rate * (1 + 0.004 * Math.sin(pos * 3)) / SR; v += a * Math.sin(ph[k] + 0.3 * Math.sin(ph[k] * 2)); });
    v *= g * (0.75 + 0.25 * Math.sin(pos * 4)); put(SFX, j, v, pan); put(SEND, j, v * 0.3, pan); } }
noise(SFX, -0.6, 3.0, 0.07, { lp: 1800, hp: 200, a: 0.4, d: 9, send: 0.2, pan: -0.5, panEnd: 0.5 });
type("YOU'VE SEEN THIS.", 0.03, 0.5);
tone(HIT, 1.25, 0.5, 150, 118, 0.42, { a: 0.002, d: 0.17, drive: 3 }); noise(SFX, 1.25, 0.06, 0.28, { lp: 3000, hp: 300, d: 0.02 });   // stamp
tone(SFX, 1.5, 0.9, 420, 40, 0.06, { a: 0.01, d: 2, curve: 1.8, drive: 1 });                                                          // tape stop
// ---- 2.6 the real solar system: reveal hit, warm pad, a small chime as each planet is named ----
noise(SFX, 2.3, 0.3, 0.16, { lp: 300, lpEnd: 6000, hp: 120, rev: true, send: 0.2 });
hit(2.6, 0.5, 82);
type("HERE'S THE REAL ONE.", 2.8, 3.3, 0.05);
const BELL = [1046.5, 880, 784, 659.3, 523.3, 440, 392, 329.6];        // farther out = lower
for (let i = 0; i < 8; i++) { const at = 3.15 + 0.11 * i, pan = (i / 7 - 0.5) * 0.9;
  tone(SFX, at, 1.6, BELL[i], BELL[i], 0.03, { a: 0.003, d: 0.45, send: 0.6, pan }); tone(SFX, at, 0.8, BELL[i] * 2.76, BELL[i] * 2.76, 0.007, { d: 0.15, send: 0.5, pan }); }
for (const [f, g, p] of [[146.83, 0.04, -0.3], [220, 0.03, 0.3], [293.66, 0.022, -0.1], [369.99, 0.014, 0.2]]) {
  const s0 = Math.round(2.6 * SR), s1 = Math.round(6.3 * SR); let ph = 0, ph2 = 0;
  for (let j = s0; j < s1; j++) { const t = j / SR, e = smooth(2.6, 3.4, t) * (1 - smooth(5.9, 6.15, t)) * (1 + 0.6 * smooth(4.8, 5.9, t)); ph += 2 * Math.PI * f / SR; ph2 += 2 * Math.PI * f * 1.005 / SR;
    const v = (Math.sin(ph) + Math.sin(ph2)) * 0.5 * g * e; put(BED, j, v, p); put(SEND, j, v * 0.3, p); } }
tone(SFX, 4.6, 1.5, 220, 440, 0.025, { a: 1.0, d: 3, send: 0.5, curve: 1.4 });
noise(SFX, 5.72, 0.48, 0.14, { lp: 300, lpEnd: 8000, hp: 200, rev: true, send: 0.3 });
// ---- 6.2 the Sun moves: big hit, steady engine, rising rush of wind (true motion) ----
hit(6.2, 0.95, 92);
{ const s0 = Math.round(6.2 * SR), s1 = Math.round(15.4 * SR); let ph = 0, ph2 = 0, y = 0;
  for (let j = s0; j < s1; j++) { const t = j / SR, e = smooth(6.2, 7.0, t) * (1 - smooth(14.2, 15.4, t));
    ph += 2 * Math.PI * 98 / SR; ph2 += 2 * Math.PI * 147 * (1 + 0.002 * Math.sin(t * 3)) / SR;
    const eng = (Math.tanh(1.8 * Math.sin(ph)) * 0.035 + Math.sin(ph2) * 0.018) * e * (0.85 + 0.15 * Math.sin(2 * Math.PI * 0.6 * t));
    const cut = 400 + 3000 * smooth(6.2, 12.6, t); const al = 1 - Math.exp(-2 * Math.PI * cut / SR); y += al * (rnd() - y);
    put(SFX, j, eng, 0); put(SFX, j, y * 0.09 * e, 0.3 * Math.sin(t * 0.7)); put(SEND, j, y * 0.03 * e, 0); } }
for (const [txt, a, b] of [['THE SUN IS MOVING', 6.0, 6.4], ['230 KM/S', 6.4, 6.7], ['THE PLANETS FOLLOW', 8.5, 8.9], ['IN STRETCHED WAVES', 8.9, 9.3],
  ['HALF THE TIME', 10.6, 10.9], ["THEY'RE AHEAD OF THE SUN", 10.9, 11.4], ['NOT A VORTEX.', 12.7, 13.0]]) type(txt, a, b, 0.045);
// a soft glass ping on each line (waves teal, ahead gold)
for (const [at, f] of [[8.9, 659.3], [10.9, 784]]) tone(SFX, at, 1.6, f, f, 0.04, { a: 0.003, d: 0.5, send: 0.6 });
hit(12.7, 0.55, 110);
// ---- 13-17.6 pull back to the whole galaxy: long airy rise, a choir-like pad, low gong on Sagittarius A* ----
noise(SFX, 13.0, 2.4, 0.14, { lp: 300, lpEnd: 5000, hp: 150, a: 1.0, d: 4, send: 0.4 });
for (const [f, g, p] of [[110, 0.03, -0.4], [164.8, 0.028, 0.4], [220, 0.024, -0.2], [277.2, 0.018, 0.2], [329.6, 0.014, 0]]) {
  const s0 = Math.round(13.6 * SR), s1 = Math.round(25.2 * SR); let ph = 0, ph2 = 0, ph3 = 0;
  for (let j = s0; j < s1; j++) { const t = j / SR, e = smooth(13.6, 15.2, t) * (1 - smooth(24.4, 25.2, t)) * (1 + 0.5 * smooth(17.6, 22.6, t));
    ph += 2 * Math.PI * f / SR; ph2 += 2 * Math.PI * f * 1.006 / SR; ph3 += 2 * Math.PI * f * 0.994 / SR;
    const v = (Math.sin(ph) + 0.6 * Math.sin(ph2) + 0.6 * Math.sin(ph3) + 0.2 * Math.sin(3 * ph)) * g * e * 0.5; put(BED, j, v, p); put(SEND, j, v * 0.5, p); } }
noise(SFX, 14.8, 0.45, 0.12, { lp: 300, lpEnd: 7000, hp: 200, rev: true, send: 0.3 });
hit(15.25, 0.9, 73.4);
tone(HIT, 15.25, 3.5, 73.4, 73, 0.12, { a: 0.01, d: 1.6, send: 0.6 }); tone(HIT, 15.25, 3.0, 110, 109.6, 0.07, { a: 0.01, d: 1.3, send: 0.6 });
type('ALL OF IT ORBITS', 14.8, 15.2, 0.04); type('A BLACK HOLE · 4 MILLION SUNS', 15.55, 16.0, 0.035);
// ---- 17.6-22.6 one lap: a tick every 10 million years on the counter, a rising orbit tone, a chime when the lap closes ----
type('ONE LAP AROUND THE GALAXY', 17.6, 18.1, 0.04);
{ const lap = t => { const s = clamp((t - 17.6) / 5); return 230 * (s - Math.sin(2 * Math.PI * s) / (2 * Math.PI)); }; let last = 0;
  for (let t = 17.6; t <= 22.6; t += 1 / 1000) { const m = Math.floor(lap(t) / 10); if (m > last) { last = m; noise(SFX, t, 0.018, 0.07, { hp: 2500, lp: 9000, d: 0.006, pan: 0.4 * Math.sin(m) });
      tone(SFX, t, 0.12, 1760, 1760, 0.012, { d: 0.04, send: 0.3 }); } } }
tone(SFX, 17.6, 5.0, 196, 392, 0.03, { a: 2.0, d: 9, send: 0.5, curve: 1.6 });
hit(22.6, 0.6, 98);
for (const [f, g] of [[784, 0.04], [1174.7, 0.025], [1568, 0.015]]) tone(SFX, 22.6, 2.4, f, f, g, { a: 0.003, d: 0.8, send: 0.7 });
// ---- 23.8 NOW YOU KNOW, plunge home into the white seam and the vortex of frame 0 ----
type('NOW YOU KNOW.', 23.8, 24.1, 0.06);
noise(SFX, 24.4, 1.6, 0.18, { lp: 300, lpEnd: 8000, hp: 150, rev: true, send: 0.25 });
tone(SFX, 24.6, 1.4, 220, 660, 0.03, { a: 0.8, d: 3, curve: 1.5 });

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
const HITS = [0, 2.6, 6.2, 12.7, 15.25, 22.6];
const duck = t => { let g = 1; for (const h of HITS) { const dt = t - h; if (dt >= 0 && dt < 1.2) g = Math.min(g, 0.45 + 0.55 * dt / 1.2); if (dt > -0.05 && dt < 0) g = Math.min(g, 0.05); }
  if (t > 5.75 && t < 6.15) g = Math.min(g, 0.25); return g; };
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
