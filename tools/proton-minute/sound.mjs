// Original sound design, synthesised here (no samples, no licences). Reads timeline.json.
// Family "accelerator": a tick on every one of the 448 laps (it starts as countable clicks and
// accelerates into a buzz as playback ramps x1 -> x5), an engine whine whose flutter is the lap rate,
// a kick on every real second, milestone hits every 10 s, a big stop hit at 448, a pull-back whoosh,
// one plink per Moon trip, and a reverse rise into frame 0.
// Every write wraps modulo the loop length, so the file loops seamlessly.
import fs from 'node:fs';
import { execFileSync } from 'node:child_process';
const spec = JSON.parse(fs.readFileSync(new URL('./timeline.json', import.meta.url)));
const SR = 48000, DUR = spec.duration, L = Math.round(SR * DUR);
const bus = () => [new Float32Array(L), new Float32Array(L)];
const HIT = bus(), SFX = bus(), BED = bus(), SEND = bus();
let seed = 12345; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647 * 2 - 1;
const put = (b, i, v, pan) => { const k = ((i % L) + L) % L; b[0][k] += v * Math.sqrt((1 - pan) / 2); b[1][k] += v * Math.sqrt((1 + pan) / 2); };
const env = (t, a, d, len) => Math.min(1, t / a) * Math.exp(-t / d) * Math.min(1, (len - t) / 0.01);

function tone(b, at, len, f0, f1, g, { a = 0.004, d = 1, pan = 0, drive = 0, send = 0, curve = 1 } = {}) {
  let ph = 0; const n = Math.round(len * SR), s = Math.round(at * SR);
  for (let j = 0; j < n; j++) { const t = j / SR, u = j / n, f = f0 + (f1 - f0) * Math.pow(u, curve); ph += 2 * Math.PI * f / SR;
    let v = Math.sin(ph); if (drive) v = Math.tanh(v * (1 + drive)) / Math.tanh(1 + drive);
    v *= g * env(t, a, d, len); put(b, s + j, v, pan); if (send) put(SEND, s + j, v * send, pan); }
}
// one-pole filtered noise; lp/hp in Hz, swelling (reverse) or decaying
function noise(b, at, len, g, { lp = 8000, hp = 0, a = 0.002, d = 0.2, pan = 0, rev = false, send = 0, lpEnd = null } = {}) {
  const n = Math.round(len * SR), s = Math.round(at * SR); let y = 0, x1 = 0, h = 0;
  for (let j = 0; j < n; j++) { const t = j / SR, cut = lpEnd ? lp + (lpEnd - lp) * (j / n) : lp, al = 1 - Math.exp(-2 * Math.PI * cut / SR);
    const x = rnd(); y += al * (x - y); let v = y;
    if (hp) { const ah = Math.exp(-2 * Math.PI * hp / SR); h = ah * (h + v - x1); x1 = v; v = h; }
    const e = rev ? Math.pow(t / len, 2.2) * Math.min(1, (len - t) / 0.004) : env(t, a, d, len);
    put(b, s + j, v * g * e, pan); if (send) put(SEND, s + j, v * g * e * send, pan); }
}
function hit(at, size) {
  noise(HIT, at - 0.55 * size, 0.55 * size - 0.05, 0.35 * size, { lp: 400, lpEnd: 6000, rev: true });       // reverse suck
  noise(HIT, at, 0.09, 0.9 * size, { lp: 12000, hp: 2200, a: 0.0005, d: 0.025, send: 0.4 });                // crack
  tone(HIT, at, 0.9, 320, 88, 0.85 * size, { a: 0.002, d: 0.28, drive: 2.5, send: 0.3, curve: 0.45 });        // body
  for (const [m, gg, dd] of [[1, 0.28, 1.6], [2.32, 0.2, 1.1], [3.17, 0.14, 0.8], [4.53, 0.09, 0.5]])       // gong partials
    tone(HIT, at, 3, 146.8 * m, 146.8 * m * 0.995, gg * size, { a: 0.003, d: dd, send: 0.6, pan: (m % 2 ? -0.2 : 0.2) });
  tone(HIT, at, 1.8, 52, 38, 0.6 * size, { a: 0.004, d: 0.6 });                                              // small real sub
}
const F = spec.facts, M0 = spec.minuteStart, ML = spec.minuteLen, B = spec.rampB, LAPS = F.laps_per_s, END = M0 + ML;
const clipAt = s => (-1 + Math.sqrt(1 + 4 * B * s)) / (2 * B) + M0;
const rate = t => (t < M0 || t > END) ? 1 : 1 + 2 * B * (t - M0);
// ---- hook: real-speed whirr (7.48 rev/s flutter) ----
hit(0, 0.75);
{ const n = Math.round(M0 * SR); let ph = 0, ph2 = 0;
  for (let j = 0; j < n; j++) { const t = j / SR; ph += 2 * Math.PI * 330 / SR; ph2 += 2 * Math.PI * LAPS / SR;
    const am = 0.55 + 0.45 * Math.cos(ph2), e = Math.min(1, t / 0.02);
    const v = (Math.sin(ph) + 0.4 * Math.sin(2.01 * ph) + 0.2 * Math.sin(3.03 * ph)) * am * 0.06 * e; put(SFX, j, v, 0.5 * Math.sin(ph2)); } }
for (const [txt, t0, t1] of [['HOW MANY LAPS', 2.95, 3.35], ['IN ONE MINUTE?', 3.4, 3.8],
  ['448 LAPS.', 23.05, 23.4], ['IN 60 SECONDS.', 23.55, 23.95], ['17,987,547 KM', 24.1, 24.5], ["THAT'S 46 TRIPS", 25.4, 25.85], ['TO THE MOON.', 25.9, 26.3],
  ['IN ONE MINUTE.', 29.0, 29.4], ['99.999999% OF LIGHT SPEED', 29.55, 29.85]])
  for (let k = 0; k < txt.length; k++) if (txt[k] !== ' ') noise(SFX, t0 + (t1 - t0) * k / txt.length, 0.025, 0.07, { hp: 2500, lp: 9000, d: 0.006, pan: rnd() * 0.3 });
// ---- the minute starts: suck-in and a thud ----
noise(SFX, M0 - 0.5, 0.5, 0.2, { lp: 400, lpEnd: 6000, hp: 150, rev: true, send: 0.3 });
tone(HIT, M0, 0.6, 180, 70, 0.45, { d: 0.18, drive: 2, send: 0.3 });
// ---- engine: whine rises with playback speed, flutters at the lap rate ----
{ let ph = 0, pf = 0; const a = Math.round(M0 * SR), b = Math.round(END * SR);
  for (let j = a; j < b; j++) { const t = j / SR, u = (t - M0) / ML, r = rate(t); ph += 2 * Math.PI * (110 + 330 * u * u + 40 * u) / SR; pf += 2 * Math.PI * LAPS * r / SR;
    const e = Math.min(1, (t - M0) / 0.8) * Math.min(1, (END - t) / 0.03), fl = 0.6 + 0.4 * Math.cos(pf);
    const v = (Math.sin(ph) + 0.5 * Math.sin(2 * ph) + 0.3 * Math.sin(3 * ph) + 0.15 * Math.sin(5 * ph)) * 0.06 * (0.5 + 0.9 * u) * fl * e; put(BED, j, v, 0.25 * Math.sin(pf)); } }
noise(BED, M0, ML, 0.05, { lp: 600, lpEnd: 5000, hp: 200, a: 3, d: 100 }); // rising air
// ---- a tick on every lap (448 of them) ----
for (let k = 1; k <= F.full_laps; k++) { const t = clipAt(k / LAPS), u = (t - M0) / ML, f = 1200 * Math.pow(2, u);
  tone(SFX, t, 0.05, f, f, 0.05 * (1 - 0.5 * u), { a: 0.0005, d: 0.012, pan: (k % 2 ? -0.3 : 0.3) }); }
// doppler pass-bys while the laps are still countable
for (let k = 0; k < 14; k++) { const t = clipAt((k + 0.5) / LAPS), g = 0.16 * (1 - k / 14);
  noise(SFX, t - 0.12, 0.12, g, { lp: 900, lpEnd: 5000, hp: 200, rev: true, pan: -0.6 }); noise(SFX, t, 0.15, g, { lp: 5000, lpEnd: 700, hp: 200, d: 0.08, pan: 0.6 }); }
// ---- a kick on every real second: 60 BPM accelerating to 300 BPM ----
for (let s = 1; s < 60; s++) { const t = clipAt(s), u = (t - M0) / ML; tone(HIT, t, 0.25, 140, 48, 0.32 + 0.12 * u, { a: 0.001, d: 0.09, drive: 1.5 }); noise(SFX, t, 0.04, 0.05 + 0.05 * u, { hp: 5000, lp: 12000, d: 0.01 }); }
// ---- milestones every 10 s ----
for (const s of [10, 20, 30, 40, 50]) { const t = clipAt(s), k = s / 10;
  tone(HIT, t, 0.9, 260, 80, 0.4, { d: 0.25, drive: 2, send: 0.3, curve: 0.45 });
  tone(SFX, t, 1.0, 880 * Math.pow(2, k / 6), 880 * Math.pow(2, k / 6), 0.07, { d: 0.35, send: 0.6 }); noise(SFX, t, 0.08, 0.3, { hp: 2200, lp: 12000, d: 0.02, send: 0.3 }); }
// ---- 448: the stop ----
noise(SFX, END - 0.6, 0.6, 0.25, { lp: 500, lpEnd: 8000, rev: true, hp: 150 });
hit(END, 1.0);
for (const [f, g] of [[587.3, 0.08], [880, 0.06], [1174.7, 0.04]]) tone(SFX, END, 2.4, f, f, g, { d: 1.0, send: 0.7 });
for (const [f, g] of [[146.8, 0.05], [220, 0.04], [293.7, 0.03]]) tone(SFX, END + 0.2, 2.2, f, f, g, { a: 0.6, d: 4, send: 0.4 });
// ---- pull back to the Moon ----
noise(SFX, 25.2, 1.6, 0.26, { lp: 7000, lpEnd: 300, hp: 120, a: 0.2, d: 3, send: 0.25 });
tone(SFX, 25.2, 1.6, 700, 110, 0.06, { a: 0.2, d: 3, curve: 0.6 });
for (const [f, g] of [[110, 0.05], [164.8, 0.04], [220, 0.03]]) tone(SFX, 26.0, 3.0, f, f, g, { a: 0.8, d: 6, send: 0.5 });
// ---- one plink per trip to the Moon (same easing as the on-screen counter) ----
const PENTA = [0, 2, 4, 7, 9];
for (let n = 1; n <= F.moon_trips; n++) { const t = 26.5 + 2.4 * Math.sqrt(n / F.moon_trips), st = PENTA[(n - 1) % 5] + 12 * Math.floor((n - 1) / 5) / 3;
  const f = 659.3 * Math.pow(2, Math.round(st) / 12); tone(SFX, t, 0.3, f, f, 0.05, { a: 0.001, d: 0.08, send: 0.5, pan: (n % 2 ? -0.35 : 0.35) }); }
for (let n = 1; n <= 4; n++) { const t0 = 26.5 + 2.4 * Math.sqrt((n - 1) / F.moon_trips), t1 = 26.5 + 2.4 * Math.sqrt(n / F.moon_trips);
  noise(SFX, t0, t1 - t0, 0.12, { lp: 800, lpEnd: 6000, hp: 300, rev: true, pan: n % 2 ? 0.4 : -0.4 }); }
hit(28.9, 0.8);
for (const [f, g] of [[440, 0.06], [659.3, 0.05], [880, 0.035]]) tone(SFX, 28.9, 2.0, f, f, g, { a: 0.01, d: 0.9, send: 0.7 });
tone(SFX, 29.45, 0.4, 1320, 1320, 0.05, { d: 0.12, send: 0.4 }); // LHC chip
// ---- snap back into frame 0 ----
noise(SFX, 29.9, 1.1, 0.24, { lp: 300, lpEnd: 8000, hp: 120, rev: true, send: 0.2 });
tone(SFX, 29.9, 1.1, 120, 900, 0.05, { a: 0.5, d: 9, curve: 2 });
// ---- reverb on the send (Schroeder, run over two loops so the tail wraps) ----
function reverb([l, r]) {
  const out = [new Float32Array(L), new Float32Array(L)];
  [l, r].forEach((x, c) => { const combs = [1557, 1617, 1491, 1422].map(d => ({ d: d + c * 23, buf: new Float32Array(d + c * 23), i: 0 }));
    const aps = [225, 556].map(d => ({ buf: new Float32Array(d), i: 0 }));
    for (let k = 0; k < 2 * L; k++) { const inp = x[k % L]; let s = 0;
      for (const cb of combs) { const y = cb.buf[cb.i]; cb.buf[cb.i] = inp + y * 0.84; cb.i = (cb.i + 1) % cb.d; s += y; }
      s *= 0.25; for (const ap of aps) { const y = ap.buf[ap.i]; const v = -s + y; ap.buf[ap.i] = s + y * 0.5; ap.i = (ap.i + 1) % ap.buf.length; s = v; }
      if (k >= L) out[c][k - L] = s; } });
  return out;
}
const VERB = reverb(SEND);
// high-pass everything but the hit bus at 90 Hz (phones), duck under hits, sum
const hp90 = ([l, r]) => [l, r].forEach(x => { const a = Math.exp(-2 * Math.PI * 90 / SR); let y = 0, p = 0; for (let k = 0; k < 2 * L; k++) { const v = x[k % L]; y = a * (y + v - p); p = v; if (k >= L) x[k - L] = y; } });
hp90(SFX); hp90(BED); hp90(VERB);
const duck = t => { let g = 1; for (const h of [0, END, 28.9]) { const dt = t - h; if (dt >= 0 && dt < 1.2) g = Math.min(g, 0.45 + 0.55 * dt / 1.2); if (dt > -0.05 && dt < 0) g = Math.min(g, 0.05); }
  if (t > DUR - 0.05) g = Math.min(g, 0.05); return g; };
const mix = [new Float32Array(L), new Float32Array(L)];
for (let c = 0; c < 2; c++) for (let k = 0; k < L; k++) {
  const d = duck(k / SR); mix[c][k] = HIT[c][k] + (SFX[c][k] * 1.7 + BED[c][k] * 1.7) * d + VERB[c][k] * 0.55;
}
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
