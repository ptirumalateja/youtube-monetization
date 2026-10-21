// Original sound design, synthesised here (no samples, no licences). Reads timeline.json.
// Family "accelerator": electric whine that rises with speed, a doppler pass-by every time the proton
// crosses the front of Earth, a digital tick on every completed lap, counter chatter, held breath,
// a long falling plunge whoosh, and a clean bright "zing" for light at the finish.
// Every write wraps modulo the loop length, so the file loops seamlessly.
import fs from 'node:fs';
import { execFileSync } from 'node:child_process';
const spec = JSON.parse(fs.readFileSync(new URL('./timeline.json', import.meta.url)));
const SR = 48000, DUR = spec.duration, L = Math.round(SR * DUR), people = spec.people;
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
const S0 = spec.slowStart, SF = spec.slowFactor, LAPS = spec.facts.laps_per_s;
// ---- hook: real-speed whirr (7.48 rev/s buzz) under the frame-0 hit ----
hit(0, 0.75);
{ const n = Math.round(2.35 * SR); let ph = 0, ph2 = 0;
  for (let j = 0; j < n; j++) { const t = j / SR; ph += 2 * Math.PI * 330 / SR; ph2 += 2 * Math.PI * 7.4808 / SR;
    const am = 0.55 + 0.45 * Math.cos(ph2), e = Math.min(1, t / 0.02) * (1 - Math.max(0, (t - 1.9) / 0.45));
    const v = (Math.sin(ph) + 0.4 * Math.sin(2.01 * ph) + 0.2 * Math.sin(3.03 * ph)) * am * 0.06 * e; put(SFX, j, v, 0.5 * Math.sin(ph2)); } }
for (const [txt, t0, t1] of [['THIS PROTON', 0, 0.45], ['CIRCLES EARTH 7.5X', 0.5, 1.15], ['IN ONE SECOND.', 1.15, 1.7], ['7.5 LAPS IN 1 SECOND.', 12.45, 13.0],
  ['ITS 27 KM RING: 11,245 LAPS A SECOND', 13.3, 13.9], ['AND LIGHT STILL WINS.', 14.45, 15.0], ['BY 2.85 METRES.', 16.8, 17.3], ['AFTER 299,792 KM.', 17.5, 18.0],
  ['NOTHING WITH MASS', 19.65, 20.1], ['CATCHES LIGHT.', 20.15, 20.55]])
  for (let k = 0; k < txt.length; k++) if (txt[k] !== ' ') noise(SFX, t0 + (t1 - t0) * k / txt.length, 0.025, 0.08, { hp: 2500, lp: 9000, d: 0.006, pan: rnd() * 0.3 });
// ---- the snap into slow motion: tape-stop down, then a soft thud ----
tone(SFX, 2.1, 0.32, 660, 90, 0.12, { d: 0.5, drive: 1, curve: 0.5 });
noise(SFX, 1.85, 0.5, 0.18, { lp: 400, lpEnd: 6000, hp: 150, rev: true, send: 0.3 });
tone(HIT, 2.42, 0.6, 180, 70, 0.4, { d: 0.18, drive: 2, send: 0.3 });
// ---- the slowed second: whine, pass-bys, lap ticks ----
{ let ph = 0; const a = Math.round(S0 * SR), b = Math.round((S0 + SF) * SR);
  for (let j = a; j < b; j++) { const t = j / SR, u = (t - S0) / SF; ph += 2 * Math.PI * (140 + 160 * u) / SR;
    const e = Math.min(1, (t - S0) / 0.6) * Math.min(1, (S0 + SF - t) / 0.08);
    const v = (Math.sin(ph) + 0.5 * Math.sin(2 * ph) + 0.25 * Math.sin(3 * ph) + 0.12 * Math.sin(5 * ph)) * 0.07 * (0.6 + 0.6 * u) * e; put(BED, j, v, 0); } }
for (let k = 0; k <= 7; k++) { // pass the front of the globe at laps = k + frac
  const t = S0 + SF * ((LAPS % 1) + k - 1 + 1) / LAPS; if (t > S0 + SF) break;
  noise(SFX, t - 0.45, 0.45, 0.22, { lp: 900, lpEnd: 5000, hp: 200, rev: true, pan: -0.6 });
  noise(SFX, t, 0.5, 0.22, { lp: 5000, lpEnd: 700, hp: 200, d: 0.2, pan: 0.6 });
  tone(SFX, t - 0.2, 0.55, 520 + 30 * k, 300 + 20 * k, 0.08, { d: 0.3, curve: 0.5 }); }
for (let k = 1; k <= 7; k++) { const t = S0 + SF * k / LAPS; // lap completed: digital tick + small sub pulse, pitch climbs
  tone(SFX, t, 0.35, 880 * Math.pow(2, k / 12), 880 * Math.pow(2, k / 12), 0.1, { d: 0.12, send: 0.4 });
  tone(SFX, t, 0.1, 2640 * Math.pow(2, k / 12), 2640 * Math.pow(2, k / 12), 0.03, { d: 0.03 });
  tone(HIT, t, 0.4, 110, 60, 0.07 + 0.01 * k, { d: 0.1, drive: 1.5 }); }
for (let t = S0 + 0.05; t < S0 + SF; t += 0.0667) noise(SFX, t, 0.012, 0.025, { hp: 4000, lp: 10000, d: 0.004, pan: 0.2 }); // counter chatter
// ---- the second ends: a stop chime ----
{ const t = S0 + SF; tone(SFX, t, 2.2, 587.3, 587.3, 0.1, { d: 0.9, send: 0.6 }); tone(SFX, t, 2.2, 880, 880, 0.06, { d: 0.8, send: 0.6 }); tone(HIT, t, 0.6, 150, 70, 0.15, { d: 0.2, drive: 1.5 }); }
for (const [f, g] of [[146.8, 0.04], [220, 0.03]]) tone(SFX, 12.5, 2.3, f, f, g, { a: 0.6, d: 5, send: 0.4 });
// LHC chip
tone(SFX, 13.1, 0.4, 1320, 1320, 0.05, { d: 0.12, send: 0.4 });
// ---- held breath, then the plunge ----
tone(SFX, 14.45, 0.4, 2200, 2400, 0.02, { a: 0.2, d: 2 });
noise(SFX, 14.8, 1.8, 0.24, { lp: 7000, lpEnd: 300, hp: 120, a: 0.15, d: 3, send: 0.25 });
tone(SFX, 14.8, 1.8, 900, 120, 0.06, { a: 0.2, d: 3, curve: 0.6 });
// ---- the finish: light zing (bright, pure) over the hit ----
hit(16.6, 1.0);
for (const [f, g] of [[1174.7, 0.07], [1760, 0.05], [2349.3, 0.03], [3520, 0.015]]) tone(SFX, 16.6, 2.8, f, f, g, { a: 0.005, d: 1.4, send: 0.7 });
for (const [f, g] of [[146.8, 0.05], [220, 0.04], [293.7, 0.03]]) tone(SFX, 17.0, 4.0, f, f, g, { a: 1.2, d: 6, send: 0.4 }); // low pad under the result
tone(SFX, 19.65, 1.4, 587.3, 587.3, 0.05, { a: 0.3, d: 2, send: 0.6 });
// ---- pull back and loop link: reverse plunge rising into frame 0 ----
noise(SFX, 21.0, 1.5, 0.2, { lp: 300, lpEnd: 7000, hp: 120, rev: true, send: 0.2 });
tone(SFX, 21.0, 1.5, 120, 900, 0.05, { a: 0.6, d: 9, curve: 2 });
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
const duck = t => { let g = 1; for (const h of [0, 16.6]) { const dt = t - h; if (dt >= 0 && dt < 1.2) g = Math.min(g, 0.45 + 0.55 * dt / 1.2); if (dt > -0.05 && dt < 0) g = Math.min(g, 0.05); }
  if (t > 14.45 && t < 14.8) g = Math.min(g, 0.3); if (t > DUR - 0.05) g = Math.min(g, 0.05); return g; };
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
