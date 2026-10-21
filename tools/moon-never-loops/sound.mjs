// Original sound design, synthesised here (no samples, no licences). Reads timeline.json.
// Family "orbital glass": a spirograph warble whose vibrato is the loop rate of the myth path; as the
// Moon's orbit shrinks to true scale the vibrato depth collapses into one pure tone (the loops unwinding).
// The ride is a low pad with one glass ping per lunar month, climbing a scale (12 pings plus the start).
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
// the same eased year clock as the scene (ride 5.0 -> 15.6)
const RIDE0 = 5.0, RIDE1 = 15.6;
function rideDays(t) { const u = clamp((t - RIDE0) / (RIDE1 - RIDE0)), a = 0.12, b = 0.1, vmax = 1 / (1 - a / 2 - b / 2); let s;
  if (u < a) s = vmax * u * u / (2 * a); else if (u < 1 - b) s = vmax * (a / 2 + (u - a)); else s = 1 - vmax * (1 - u) * (1 - u) / (2 * b); return Y * clamp(s); }

// ---- spirograph warble: hook (full loops), unwinding during the morph, returning for the loop link ----
{ const loopRate = (Y / SYN) / 2.4; let ph = 0, vph = 0;
  for (let j = 0; j < L; j++) { const t = j / SR;
    let depth, g;
    if (t < 2.7) { depth = 1; g = 0.07 * (1 - 0.5 * smooth(1.45, 1.6, t) + 0.5 * smooth(2.0, 2.4, t)); }
    else if (t < 4.6) { depth = 1 - smooth(2.7, 4.6, t); g = 0.07; }
    else if (t < 5.4) { depth = 0; g = 0.07 * (1 - smooth(4.6, 5.4, t)); }
    else if (t < 19.7) { continue; }
    else { depth = smooth(19.7, 20.95, t); g = 0.07 * smooth(19.7, 20.3, t); }
    const rate = t < 4.6 || t >= 19.7 ? loopRate : loopRate * 0.4;
    vph += 2 * Math.PI * rate / SR; const f = 523.25 * Math.pow(2, depth * 0.55 * Math.sin(vph) / 1); ph += 2 * Math.PI * f / SR;
    const v = (Math.sin(ph) + 0.25 * Math.sin(2 * ph) + 0.1 * Math.sin(3 * ph)) * g; put(SFX, j, v, 0.55 * depth * Math.cos(vph)); put(SEND, j, v * 0.35, 0); } }
// ---- hook ----
hit(0, 0.7);
for (const [txt, t0, t1] of [["THE MOON'S PATH", 0, 0.5], ['AROUND THE SUN?', 0.5, 1.05], ['AT TRUE SCALE', 2.65, 3.1], ["THE MOON'S ORBIT IS 389X SMALLER", 3.1, 3.7],
  ['NO LOOPS.', 4.55, 4.85], ['THE SUN PULLS THE MOON', 8.0, 8.6], ['2.2X HARDER THAN EARTH.', 8.6, 9.2], ['SO ITS PATH ALWAYS', 11.5, 12.1], ['BENDS TOWARD THE SUN.', 12.1, 12.8],
  ['IT NEVER', 16.2, 16.55], ['GOES BACKWARDS.', 16.55, 17.2], ['12.4 GENTLE WAVES A YEAR ZERO LOOPS', 17.7, 18.5]])
  for (let k = 0; k < txt.length; k++) if (txt[k] !== ' ') noise(SFX, t0 + (t1 - t0) * k / txt.length, 0.022, 0.07, { hp: 2600, lp: 9000, d: 0.006, pan: rnd() * 0.3 });
// "THIS IS WRONG." stamp: dull detuned buzz + thud
tone(HIT, 1.45, 0.5, 150, 120, 0.35, { a: 0.002, d: 0.16, drive: 3 }); tone(SFX, 1.45, 0.35, 156, 128, 0.08, { d: 0.15, drive: 4, pan: 0.2 });
noise(SFX, 1.45, 0.06, 0.25, { lp: 3000, hp: 300, d: 0.02 });
// ---- the morph: a long falling whoosh as the orbit shrinks, a settled chime on NO LOOPS ----
noise(SFX, 2.6, 2.1, 0.16, { lp: 6000, lpEnd: 500, hp: 150, a: 0.3, d: 3, send: 0.3 });
tone(HIT, 2.62, 0.5, 170, 80, 0.3, { d: 0.18, drive: 1.5, send: 0.2 });
for (const [f, g] of [[523.25, 0.07], [784, 0.05], [1046.5, 0.03]]) tone(SFX, 4.55, 2.6, f, f, g, { a: 0.004, d: 1.1, send: 0.7 });
// ---- plunge to the chase camera ----
noise(SFX, 5.0, 2.0, 0.22, { lp: 7000, lpEnd: 350, hp: 120, a: 0.25, d: 3, send: 0.25 });
tone(SFX, 5.0, 2.0, 880, 140, 0.05, { a: 0.3, d: 3, curve: 0.6 });
// ---- the ride: pad, slow shimmer, one glass ping per lunar month (new Moon), rising ----
for (const [f, g, p] of [[146.83, 0.05, -0.3], [220, 0.04, 0.3], [293.66, 0.03, -0.1], [440, 0.012, 0.2]]) {
  const s0 = Math.round(5.6 * SR), s1 = Math.round(16.1 * SR); let ph = 0, ph2 = 0;
  for (let j = s0; j < s1; j++) { const t = j / SR, e = smooth(5.6, 7.0, t) * (1 - smooth(15.4, 15.95, t)); ph += 2 * Math.PI * f / SR; ph2 += 2 * Math.PI * f * 1.004 / SR;
    const v = (Math.sin(ph) + Math.sin(ph2)) * 0.5 * g * e * (0.8 + 0.2 * Math.sin(2 * Math.PI * 0.23 * t)); put(BED, j, v, p); put(SEND, j, v * 0.3, p); } }
{ const scale = [0, 2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19, 20]; // natural minor, climbing (one note per month)
  let k = 1; for (let s = 0; s < 1; s += 1 / (30 * 400)) { const t = RIDE0 + s * (RIDE1 - RIDE0); if (rideDays(t) >= k * SYN && k <= 12) {
      const f = 587.33 * Math.pow(2, scale[k] / 12); tone(SFX, t, 1.4, f, f, 0.065, { a: 0.003, d: 0.45, send: 0.6, pan: (k % 2 ? -0.35 : 0.35) });
      tone(SFX, t, 0.6, f * 2.76, f * 2.76, 0.015, { d: 0.12, send: 0.5 }); k++; } } }
for (let t = 6.0; t < 15.6; t += 1 / 15) noise(SFX, t, 0.01, 0.018, { hp: 4500, lp: 10000, d: 0.003, pan: 0.25 }); // counter chatter
// the two pulls: gold (sun) higher and longer, teal (earth) lower
tone(SFX, 8.9, 1.8, 392, 392, 0.06, { a: 0.02, d: 0.8, send: 0.5, pan: 0.4 }); tone(SFX, 8.9, 1.0, 196, 196, 0.05, { a: 0.02, d: 0.4, send: 0.4, pan: -0.4 });
tone(SFX, 11.5, 2.0, 293.66, 440, 0.03, { a: 0.4, d: 2, send: 0.5, curve: 0.5 });
// ---- held breath (15.6-16.2), then the twist ----
noise(SFX, 15.7, 0.5, 0.12, { lp: 300, lpEnd: 7000, hp: 200, rev: true, send: 0.3 });
hit(16.2, 1.0);
for (const [f, g, p] of [[146.83, 0.05, -0.4], [220, 0.045, 0.4], [293.66, 0.04, -0.2], [369.99, 0.03, 0.2], [440, 0.025, 0]])
  tone(SFX, 16.3, 3.4, f, f * 1.002, g, { a: 0.8, d: 6, send: 0.5, pan: p });
for (const [f, g] of [[1174.7, 0.04], [1760, 0.025]]) tone(SFX, 17.7, 2.2, f, f, g, { a: 0.01, d: 0.9, send: 0.7 });
// ---- loop link: rising sweep into frame 0 ----
noise(SFX, 19.7, 1.3, 0.14, { lp: 300, lpEnd: 6000, hp: 150, rev: true, send: 0.2 });
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
const duck = t => { let g = 1; for (const h of [0, 16.2]) { const dt = t - h; if (dt >= 0 && dt < 1.2) g = Math.min(g, 0.45 + 0.55 * dt / 1.2); if (dt > -0.05 && dt < 0) g = Math.min(g, 0.05); }
  if (t > 15.6 && t < 16.15) g = Math.min(g, 0.25); if (t > DUR - 0.05) g = Math.min(g, 0.05); return g; };
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
