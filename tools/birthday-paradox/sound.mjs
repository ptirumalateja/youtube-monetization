// Original sound design, synthesised here (no samples, no licences). Reads timeline.json.
// Family: music-box plucks (each month is a note, so two people with one birthday ring in unison),
// a tightening drone + heartbeat, sparkle ticks for threads, one big "same day" hit, a soft landing hit at 70.
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
const PENTA = [0, 2, 4, 7, 9]; // D major pentatonic
const noteHz = k => 293.66 * Math.pow(2, (12 * Math.floor(k / 5) + PENTA[k % 5]) / 12);
const MONTH0 = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
const month = d => MONTH0.filter(m => m <= d).length - 1;
const panOf = d => 0.55 * Math.cos(Math.PI / 2 - 2 * Math.PI * d / 365);

function pluck(at, f, g, pan) { // music box: inharmonic tine partials
  tone(SFX, at, 1.6, f, f, g, { a: 0.002, d: 0.55, pan, send: 0.35 });
  tone(SFX, at, 0.5, f * 2.76, f * 2.76, g * 0.32, { a: 0.001, d: 0.12, pan, send: 0.3 });
  tone(SFX, at, 0.2, f * 5.4, f * 5.4, g * 0.12, { a: 0.001, d: 0.04, pan });
}
function hit(at, size) {
  noise(HIT, at - 0.55 * size, 0.55 * size - 0.05, 0.35 * size, { lp: 400, lpEnd: 6000, rev: true });       // reverse suck
  noise(HIT, at, 0.09, 0.9 * size, { lp: 12000, hp: 2200, a: 0.0005, d: 0.025, send: 0.4 });                // crack
  tone(HIT, at, 0.9, 320, 88, 0.85 * size, { a: 0.002, d: 0.28, drive: 2.5, send: 0.3, curve: 0.45 });        // body
  for (const [m, gg, dd] of [[1, 0.28, 1.6], [2.32, 0.2, 1.1], [3.17, 0.14, 0.8], [4.53, 0.09, 0.5]])       // gong partials
    tone(HIT, at, 3, 146.8 * m, 146.8 * m * 0.995, gg * size, { a: 0.003, d: dd, send: 0.6, pan: (m % 2 ? -0.2 : 0.2) });
  tone(HIT, at, 1.8, 52, 38, 0.6 * size, { a: 0.004, d: 0.6 });                                              // small real sub
}

// ---- frame 0 (its pre-swell wraps to the end of the file, leading the loop back in) ----
hit(0, 0.6);
// hook ring sweep: a soft glass glissando
for (let k = 0; k < 8; k++) pluck(0.05 + k * 0.1, noteHz(k + 3), 0.05, -0.6 + k * 0.17);

// ---- people: drop whiff, landing pluck (month = note), thread sparkle ----
people.forEach((p, i) => {
  const fast = p.n > 23, pan = panOf(p.day), f = noteHz(month(p.day) + 2);
  noise(SFX, p.t - p.drop, p.drop, fast ? 0.035 : 0.07, { lp: 2500, lpEnd: 7000, hp: 300, rev: true, pan });
  if (p.n === 23) return;
  pluck(p.t, f, fast ? 0.11 : 0.2, pan);
  const ticks = Math.min(i, fast ? 6 : 22);
  for (let k = 0; k < ticks; k++) { const tt = p.t + (fast ? 0.2 : 0.3) * (k / Math.max(1, ticks)); noise(SFX, tt, 0.03, 0.05, { hp: 5000, lp: 11000, d: 0.008, pan: rnd() * 0.8, send: 0.5 }); }
  if (p.stack > 0) { tone(SFX, p.t, 1.2, f * 1.004, f * 1.004, 0.1, { d: 0.5, pan, send: 0.4 }); noise(HIT, p.t, 0.12, 0.18, { lp: 9000, hp: 1500, d: 0.03 }); tone(HIT, p.t, 0.5, 180, 90, 0.18, { d: 0.18, drive: 1.5 }); }
});

// ---- tension: drone that tightens with the odds, and a heartbeat that speeds up ----
const P = n => { let q = 1; for (let k = 0; k < n; k++) q *= (365 - k) / 365; return 1 - q; };
{
  const ph = [0, 0, 0, 0];
  for (let j = 0; j < L; j++) { const t = j / SR; let n = 0; while (n < people.length && people[n].t <= t) n++;
    const p = P(n), on = Math.min(1, Math.max(0, (t - 2.2) / 1.5)) * (t < 11.0 ? 1 : t < 11.75 ? 0.04 : t < 20.2 ? 1 : Math.max(0, 1 - (t - 20.2) / 0.6));
    const fr = [110, 110.6, 164.8, 220 + 30 * p]; let v = 0;
    for (let k = 0; k < 4; k++) { ph[k] += 2 * Math.PI * fr[k] / SR; v += Math.sin(ph[k]) + 0.3 * Math.sin(2 * ph[k]) * p + 0.18 * Math.sin(3 * ph[k]) * p; }
    v *= 0.022 * (0.35 + p) * on; BED[0][j] += v; BED[1][j] += v * 0.97; }
  let t = 2.4; while (t < 10.95) { const iv = 0.85 - 0.43 * (t - 2.4) / 8.5;
    tone(BED, t, 0.25, 140, 70, 0.22, { d: 0.07, drive: 1 }); tone(BED, t + 0.16, 0.22, 120, 65, 0.13, { d: 0.06, drive: 1 }); t += iv; }
}

// ---- type-on ticks for every typed line, and a reverse whoosh into the snap ----
for (const [txt, t0, t1] of [['23 PEOPLE.', 0, 0.45], ['50% CHANCE TWO', 0.5, 1.15], ['SHARE A BIRTHDAY.', 1.1, 1.75], ['23 PEOPLE', 11.85, 12.15],
  ['253 PAIRS', 12.45, 12.75], ['EVERY PAIR IS A CHANCE TO MATCH.', 13.0, 13.7], ['COUNT THE PAIRS,', 18.2, 18.85], ['NOT THE PEOPLE.', 18.95, 19.6]])
  for (let k = 0; k < txt.length; k++) if (txt[k] !== ' ') noise(SFX, t0 + (t1 - t0) * k / txt.length, 0.025, 0.09, { hp: 2500, lp: 9000, d: 0.006, pan: rnd() * 0.3 });
noise(SFX, 1.75, 0.6, 0.2, { lp: 500, lpEnd: 7000, hp: 150, rev: true, send: 0.3 });
tone(HIT, 2.35, 0.5, 200, 90, 0.35, { d: 0.12, drive: 2, send: 0.3 });
noise(HIT, 2.35, 0.06, 0.4, { hp: 2500, lp: 12000, d: 0.02 });

// ---- held breath (11.0-11.75) then the match ----
tone(SFX, 11.05, 0.7, 1760, 1900, 0.025, { a: 0.4, d: 2 });           // thin glass whine, barely there
{ const f = noteHz(month(spec.matchDay) + 2), pn = panOf(spec.matchDay); // the twins: same note, twice, beating
  pluck(11.75, f, 0.22, pn); tone(SFX, 11.75, 2.5, f * 1.006, f * 1.006, 0.14, { d: 1.2, pan: -pn, send: 0.6 }); tone(SFX, 11.75, 2.5, f * 2, f * 2, 0.06, { d: 0.9, send: 0.6 }); }
hit(11.75, 1.0);
// bowed-glass pad under the reveal and the thesis (D, F#, A, E)
for (const [f, g] of [[293.66, 0.05], [369.99, 0.04], [440, 0.035], [659.25, 0.02]]) {
  tone(SFX, 12.0, 3.3, f, f, g, { a: 1.0, d: 6, send: 0.5 }); tone(SFX, 18.0, 2.6, f * 2, f * 2, g * 0.7, { a: 0.4, d: 3, send: 0.6 });
}
// ---- fill to 70: riser, then a smaller landing hit ----
noise(SFX, 15.2, 2.8, 0.14, { lp: 600, lpEnd: 9000, hp: 200, rev: true, send: 0.2 });
tone(SFX, 15.2, 2.8, 220, 880, 0.05, { a: 1.5, d: 9, curve: 2 });
hit(18.0, 0.6);
// ---- implosion and loop link ----
noise(SFX, 20.2, 0.8, 0.16, { lp: 300, lpEnd: 5000, rev: true });
tone(SFX, 20.2, 0.8, 180, 720, 0.06, { a: 0.6, d: 9, curve: 2 });
pluck(21.0, noteHz(2), 0.08, 0);

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
const duck = t => { let g = 1; for (const h of [0, 11.75, 18.0]) { const dt = t - h; if (dt >= 0 && dt < 1.2) g = Math.min(g, 0.45 + 0.55 * dt / 1.2); if (dt > -0.05 && dt < 0) g = Math.min(g, 0.05); }
  if (t > 11.0 && t < 11.7) g = Math.min(g, 0.25); if (t > DUR - 0.05) g = Math.min(g, 0.05); return g; };
const mix = [new Float32Array(L), new Float32Array(L)];
for (let c = 0; c < 2; c++) for (let k = 0; k < L; k++) {
  const d = duck(k / SR); mix[c][k] = HIT[c][k] + (SFX[c][k] * 0.9 + BED[c][k]) * d + VERB[c][k] * 0.55;
}
let peak = 0; for (const x of mix) for (const v of x) peak = Math.max(peak, Math.abs(v));
const buf = Buffer.alloc(44 + L * 4);
buf.write('RIFF', 0); buf.writeUInt32LE(36 + L * 4, 4); buf.write('WAVEfmt ', 8); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(2, 22);
buf.writeUInt32LE(SR, 24); buf.writeUInt32LE(SR * 4, 28); buf.writeUInt16LE(4, 32); buf.writeUInt16LE(16, 34); buf.write('data', 36); buf.writeUInt32LE(L * 4, 40);
for (let k = 0; k < L; k++) for (let c = 0; c < 2; c++) { const v = Math.tanh(1.3 * mix[c][k] / peak) / Math.tanh(1.3); buf.writeInt16LE(Math.round(v * 0.89 * 32767), 44 + k * 4 + c * 2); }
fs.mkdirSync(new URL('./output/', import.meta.url), { recursive: true });
const raw = new URL('./output/sound_raw.wav', import.meta.url).pathname, fin = new URL('./output/sound.wav', import.meta.url).pathname;
fs.writeFileSync(raw, buf);
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', raw, '-af', 'loudnorm=I=-15:TP=-2:LRA=9,alimiter=limit=0.79:level=false', '-ar', '48000', fin]);
console.log('sound.wav written; raw peak', peak.toFixed(3));
