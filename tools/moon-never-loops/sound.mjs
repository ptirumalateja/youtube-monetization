// Original sound design, synthesised here (no samples, no licences). Reads timeline.json.
// Family "orbital glass": a spirograph warble whose vibrato is the loop rate of the myth path; as the
// Moon's orbit shrinks to true scale the vibrato depth collapses into one pure tone (the loops unwinding).
// The ride is a low pad with one glass ping per completed lunar month, climbing a scale; a throbbing gold drone for the Sun's pull.
// Every write wraps modulo the loop length, so the file loops seamlessly.
import fs from 'node:fs';
import { execFileSync } from 'node:child_process';
const spec = JSON.parse(fs.readFileSync(new URL('./timeline.json', import.meta.url)));
const SR = 48000, DUR = spec.duration, L = Math.round(SR * DUR), F = spec.facts;
const Y = F.year_days, SYN = F.synodic_month_days;
const bus = () => [new Float32Array(L), new Float32Array(L)];
const HIT = bus(), SFX = bus(), BED = bus(), SEND = bus();
let seed = 4242; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647 * 2 - 1;
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
function noise(b, at, len, g, { lp = 8000, hp = 0, a = 0.002, d = 0.2, pan = 0, rev = false, send = 0, lpEnd = null } = {}) {
  const n = Math.round(len * SR), s = Math.round(at * SR); let y = 0, x1 = 0, h = 0;
  for (let j = 0; j < n; j++) { const t = j / SR, cut = lpEnd ? lp + (lpEnd - lp) * (j / n) : lp, al = 1 - Math.exp(-2 * Math.PI * cut / SR);
    const x = rnd(); y += al * (x - y); let v = y;
    if (hp) { const ah = Math.exp(-2 * Math.PI * hp / SR); h = ah * (h + v - x1); x1 = v; v = h; }
    const e = rev ? Math.pow(t / len, 2.2) * Math.min(1, (len - t) / 0.004) : env(t, a, d, len);
    put(b, s + j, v * g * e, pan); if (send) put(SEND, s + j, v * g * e * send, pan); }
}
function hit(at, size) {
  noise(HIT, at - 0.5 * size, 0.5 * size - 0.05, 0.3 * size, { lp: 400, lpEnd: 6000, rev: true });
  noise(HIT, at, 0.08, 0.8 * size, { lp: 12000, hp: 2400, a: 0.0005, d: 0.022, send: 0.4 });
  tone(HIT, at, 0.9, 300, 92, 0.85 * size, { a: 0.002, d: 0.3, drive: 2.2, send: 0.3, curve: 0.45 });
  for (const [m, gg, dd] of [[1, 0.26, 1.8], [2.76, 0.18, 1.2], [5.4, 0.1, 0.7]])                 // bowl-like partials (glass, not gong)
    tone(HIT, at, 3, 196 * m, 196 * m * 0.997, gg * size, { a: 0.003, d: dd, send: 0.7, pan: (m > 2 ? 0.25 : -0.25) });
  tone(HIT, at, 1.6, 55, 40, 0.55 * size, { a: 0.004, d: 0.55 });
}
// the same clock as the scene: base rate plus a ride window, integrating to exactly 12 synodic months
const CL = spec.clock, D_TOT = CL.months * SYN;
const rideW = t => smooth(CL.ride[0], CL.ride[1], t) * (1 - smooth(CL.ride[2], CL.ride[3], t));
const STEP = 1 / 600, NT = Math.round(DUR / STEP); let wsum = 0; for (let i = 0; i < NT; i++) wsum += rideW((i + 0.5) * STEP) * STEP;
const RATE_A = (D_TOT - CL.base_days_per_s * DUR) / wsum;
const monthTimes = []; { let d = 0; for (let i = 0; i < NT; i++) { const t = (i + 0.5) * STEP, nd = d + (CL.base_days_per_s + RATE_A * rideW(t)) * STEP;
  if (Math.floor(nd / SYN + 1e-6) > Math.floor(d / SYN + 1e-6)) monthTimes.push(t); d = nd; } }

// ---- frame 0: a soft hit and a warm space drone under the close-up ----
hit(0, 0.6);
for (const [f, g, p] of [[110, 0.05, -0.3], [164.8, 0.035, 0.3], [220, 0.02, 0]]) tone(BED, 0, 2.6, f, f * 1.003, g, { a: 0.05, d: 3, send: 0.3, pan: p });
// ---- pull back: rising air whoosh into the wide view ----
noise(SFX, 0.9, 1.5, 0.2, { lp: 400, lpEnd: 7000, hp: 150, rev: true, send: 0.3 });
tone(SFX, 1.0, 1.4, 180, 620, 0.04, { a: 0.4, d: 2, curve: 1.6 });
// ---- spirograph warble: audible while the usual drawing is on screen, then it unwinds into one pure tone ----
{ let ph = 0, vph = 0;
  for (let j = 0; j < L; j++) { const t = j / SR; if (t < 1.7 || t > 5.4) continue;
    const depth = 1 - smooth(2.9, 4.7, t), g = 0.065 * smooth(1.7, 2.1, t) * (1 - smooth(4.7, 5.4, t)) * (1 - 0.45 * smooth(2.2, 2.3, t) * (1 - smooth(2.5, 2.9, t)));
    vph += 2 * Math.PI * 5.1 * (1 - 0.6 * smooth(2.9, 4.7, t)) / SR; const f = 523.25 * Math.pow(2, depth * 0.55 * Math.sin(vph)); ph += 2 * Math.PI * f / SR;
    const v = (Math.sin(ph) + 0.25 * Math.sin(2 * ph) + 0.1 * Math.sin(3 * ph)) * g; put(SFX, j, v, 0.55 * depth * Math.cos(vph)); put(SEND, j, v * 0.35, 0); } }
for (const [txt, t0, t1] of [["THE MOON'S PATH", 0, 0.5], ['AROUND THE SUN', 0.5, 1.0], ['AT REAL SCALE', 2.95, 3.35], ['NO LOOPS.', 4.7, 5.0],
  ['THE SUN PULLS THE MOON', 8.4, 9.0], ['HARDER THAN EARTH DOES.', 9.0, 9.6], ['SO ITS PATH ALWAYS', 12.2, 12.8], ['CURVES TOWARD THE SUN.', 12.8, 13.5],
  ['IT NEVER', 15.2, 15.55], ['GOES BACKWARDS.', 15.55, 16.2]])
  for (let k = 0; k < txt.length; k++) if (txt[k] !== ' ') noise(SFX, t0 + (t1 - t0) * k / txt.length, 0.022, 0.07, { hp: 2600, lp: 9000, d: 0.006, pan: rnd() * 0.3 });
// "NOT LIKE THIS." stamp
tone(HIT, 2.2, 0.5, 150, 120, 0.35, { a: 0.002, d: 0.16, drive: 3 }); tone(SFX, 2.2, 0.35, 156, 128, 0.08, { d: 0.15, drive: 4, pan: 0.2 });
noise(SFX, 2.2, 0.06, 0.25, { lp: 3000, hp: 300, d: 0.02 });
// ---- the unwinding: a long falling whoosh, then a settled chime on NO LOOPS ----
noise(SFX, 2.9, 1.9, 0.14, { lp: 6000, lpEnd: 500, hp: 150, a: 0.3, d: 3, send: 0.3 });
for (const [f, g] of [[523.25, 0.07], [784, 0.05], [1046.5, 0.03]]) tone(SFX, 4.7, 2.6, f, f, g, { a: 0.004, d: 1.1, send: 0.7 });
// ---- dive to fly beside Earth and the Moon ----
noise(SFX, 5.0, 2.0, 0.22, { lp: 7000, lpEnd: 350, hp: 120, a: 0.25, d: 3, send: 0.25 });
tone(SFX, 5.0, 2.0, 880, 140, 0.05, { a: 0.3, d: 3, curve: 0.6 });
tone(HIT, 6.9, 0.7, 160, 70, 0.25, { d: 0.25, drive: 1.5, send: 0.3 });
// ---- the ride: pad, slow shimmer, one glass ping per completed lunar month, rising ----
for (const [f, g, p] of [[146.83, 0.05, -0.3], [220, 0.04, 0.3], [293.66, 0.03, -0.1], [440, 0.012, 0.2]]) {
  const s0 = Math.round(6.2 * SR), s1 = Math.round(15.3 * SR); let ph = 0, ph2 = 0;
  for (let j = s0; j < s1; j++) { const t = j / SR, e = smooth(6.2, 7.4, t) * (1 - smooth(14.6, 15.15, t)); ph += 2 * Math.PI * f / SR; ph2 += 2 * Math.PI * f * 1.004 / SR;
    const v = (Math.sin(ph) + Math.sin(ph2)) * 0.5 * g * e * (0.8 + 0.2 * Math.sin(2 * Math.PI * 0.23 * t)); put(BED, j, v, p); put(SEND, j, v * 0.3, p); } }
{ const scale = [0, 2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19, 20];
  monthTimes.forEach((t, i) => { if (t > 15.1) return; const f = 587.33 * Math.pow(2, scale[i + 1] / 12);
    tone(SFX, t, 1.4, f, f, 0.065, { a: 0.003, d: 0.45, send: 0.6, pan: (i % 2 ? -0.35 : 0.35) }); tone(SFX, t, 0.6, f * 2.76, f * 2.76, 0.015, { d: 0.12, send: 0.5 }); }); }
// the pull: a heavy gold drone that throbs toward the Sun, a thin teal tone for Earth
{ const s0 = Math.round(9.0 * SR), s1 = Math.round(11.9 * SR); let ph = 0, ph2 = 0;
  for (let j = s0; j < s1; j++) { const t = j / SR, e = smooth(9.0, 9.4, t) * (1 - smooth(11.5, 11.9, t)); ph += 2 * Math.PI * 98 / SR; ph2 += 2 * Math.PI * 392 / SR;
    const thr = 0.6 + 0.4 * Math.sin(2 * Math.PI * 3.4 * t);
    put(SFX, j, (Math.tanh(2 * Math.sin(ph)) * 0.05 * thr + Math.sin(2 * ph) * 0.02) * e, 0.3); put(SFX, j, Math.sin(ph2) * 0.012 * e, -0.4); put(SEND, j, Math.sin(ph2) * 0.01 * e, 0); } }
// ---- crane up: a slow swell, held breath, then the twist ----
tone(SFX, 11.8, 3.0, 293.66, 440, 0.03, { a: 1.2, d: 3, send: 0.5, curve: 0.5 });
noise(SFX, 11.8, 2.9, 0.1, { lp: 300, lpEnd: 4000, hp: 150, a: 1.5, d: 4, send: 0.3 });
noise(SFX, 14.75, 0.45, 0.12, { lp: 300, lpEnd: 7000, hp: 200, rev: true, send: 0.3 });
hit(15.2, 1.0);
for (const [f, g, p] of [[146.83, 0.05, -0.4], [220, 0.045, 0.4], [293.66, 0.04, -0.2], [369.99, 0.03, 0.2], [440, 0.025, 0]])
  tone(SFX, 15.3, 3.2, f, f * 1.002, g, { a: 0.8, d: 6, send: 0.5, pan: p });
for (const [f, g] of [[1174.7, 0.04], [1760, 0.025]]) tone(SFX, 16.2, 2.2, f, f, g, { a: 0.01, d: 0.9, send: 0.7 });
// ---- dive home: falling whoosh, then a rising tone into frame 0 ----
noise(SFX, 18.4, 2.4, 0.2, { lp: 7000, lpEnd: 400, hp: 120, a: 0.4, d: 3, send: 0.25 });
noise(SFX, 19.9, 1.05, 0.14, { lp: 300, lpEnd: 6000, hp: 150, rev: true, send: 0.2 });
tone(SFX, 19.9, 1.1, 220, 440, 0.03, { a: 0.8, d: 3, curve: 1.5 });

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
const duck = t => { let g = 1; for (const h of [0, 15.2]) { const dt = t - h; if (dt >= 0 && dt < 1.2) g = Math.min(g, 0.45 + 0.55 * dt / 1.2); if (dt > -0.05 && dt < 0) g = Math.min(g, 0.05); }
  if (t > 14.7 && t < 15.15) g = Math.min(g, 0.25); if (t > DUR - 0.05) g = Math.min(g, 0.05); return g; };
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
