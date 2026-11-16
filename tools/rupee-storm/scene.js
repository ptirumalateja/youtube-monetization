// ₹1 Crore or ₹1 Doubled? — "Notification Storm" on riso-print paper. Wordless, 9:16, 20.6 s.
// Frame 0: phone A holds ₹1 crore, phone B holds ₹1. A collapses into the finish flag of a race bar (the open loop),
// B takes centre and "credited" cards pile in every ~0.4 s. Day 24 the bar smashes the flag (OVERTAKEN), the bar
// rescales and keeps stretching to 107×, B cracks under the load, day 30 slams +₹53.7 crore, the phone shatters into the
// payoff chart, whose bars morph into the two comment buttons.
// window.renderAt(t, sub) -> JPEG. window.events -> sound cues. window.TL -> timeline.
'use strict';
const DW = 720, DH = 1280, DUR = 20.75;
const qs = new URLSearchParams(location.search);
const W = +(qs.get('w') || 1080), H = +(qs.get('h') || 1920), KK = W / DW, NOTEXT = qs.get('notext') === '1';
const cv = document.createElement('canvas'); cv.width = W; cv.height = H; document.body.appendChild(cv);
const out = cv.getContext('2d');
const acc = document.createElement('canvas'); acc.width = W; acc.height = H; const A = acc.getContext('2d');
let T = 0;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, k) => a + (b - a) * k;
const ss = (a, b, x) => { const k = clamp((x - a) / (b - a)); return k * k * (3 - 2 * k); };
const eout = k => 1 - Math.pow(1 - clamp(k), 3);
const ein = k => Math.pow(clamp(k), 3);
const spr = x => x <= 0 ? 0 : 1 - Math.exp(-x * 13) * Math.cos(x * 24);
function hash(i) { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }
const inr = n => '₹' + Math.round(n).toLocaleString('en-IN');
const short = n => n >= 1e7 ? '₹' + (n / 1e7).toFixed(n >= 1e8 ? 0 : 1) + ' CR' : n >= 1e5 ? '₹' + (n / 1e5).toFixed(1).replace(/\.0$/, '') + ' L' : inr(n);
const CREAM = '#F4ECDD', INK = '#1B1F3B', GREEN = '#12B76A', SAFF = '#FF8A1F', INDIGO = '#3D4BE0', RED = '#F04438', YEL = '#FFD23F', PINK = '#FF5C8A';

// ---------- timeline ----------
const TD = [null, 0];
for (let d = 2; d <= 30; d++) TD.push(
  d <= 10 ? 0.25 + (d - 2) * 0.4 :
  d <= 19 ? 4.35 + (d - 11) * 0.42 :
  d === 20 ? 8.2 :
  d <= 23 ? 9.0 + (d - 21) * 0.6 :
  d === 24 ? 10.9 :
  d <= 29 ? 12.25 + (d - 25) * 0.55 : 15.2);
const T_FOLD = 1.25, T_FLIP = TD[24], T_SLAM = TD[30], T_SHAT = 15.65, T_PAY = 16.0, T_CHART = 17.35, T_CTA = 18.75, T_END = T_PAY;
const dayAt = t => { let d = 0; for (let i = 1; i <= 30; i++) if (t >= TD[i]) d = i; return d; };
const val = d => Math.pow(2, d) - 1;
const liveVal = t => { const d = dayAt(t); if (d <= 1) return 1; return lerp(val(d - 1), val(d), eout((t - TD[d]) / 0.07)); };
const PX = 360, PY = 780; // B phone centre once it owns the screen

// ---------- textures ----------
const halftone = (() => { const c = document.createElement('canvas'); c.width = c.height = 10; const g = c.getContext('2d'); g.fillStyle = INK; g.beginPath(); g.arc(5, 5, 2.3, 0, 7); g.fill(); return c; })();
const grain = (() => { const c = document.createElement('canvas'); c.width = c.height = 256; const g = c.getContext('2d'); const im = g.createImageData(256, 256);
  for (let i = 0; i < 256 * 256; i++) { const v = hash(i * 1.37) * 255; im.data[i * 4] = im.data[i * 4 + 1] = im.data[i * 4 + 2] = v; im.data[i * 4 + 3] = 255; } g.putImageData(im, 0, 0); return c; })();
// static riso background (paper, halftone colour fields, kolam dots) rendered once; rings rotate live
const BG = document.createElement('canvas'); BG.width = W; BG.height = H;
(() => { const g = BG.getContext('2d'); g.setTransform(KK, 0, 0, KK, 0, 0); g.fillStyle = CREAM; g.fillRect(0, 0, DW, DH);
  const rg = g.createRadialGradient(360, 600, 60, 360, 640, 900); rg.addColorStop(0, 'rgba(255,250,238,0.9)'); rg.addColorStop(1, 'rgba(226,212,188,0.5)'); g.fillStyle = rg; g.fillRect(0, 0, DW, DH);
  const field = (cx, cy, R, col, off, step) => { g.fillStyle = col; for (let y = cy - R; y < cy + R; y += step) for (let x = cx - R + ((Math.round((y - cy) / step)) % 2) * step / 2; x < cx + R; x += step) { const dd = Math.hypot(x - cx, y - cy) / R; if (dd >= 1) continue; const r = step * 0.48 * Math.pow(1 - dd, 0.7); g.beginPath(); g.arc(x + off, y + off, r, 0, 7); g.fill(); } };
  field(30, 150, 330, 'rgba(255,92,138,0.22)', 0, 16); field(30, 150, 330, 'rgba(0,120,191,0.10)', 3, 16);
  field(700, 1180, 380, 'rgba(255,138,31,0.24)', 0, 16); field(700, 1180, 380, 'rgba(61,75,224,0.10)', -3, 16);
  field(720, 420, 200, 'rgba(255,210,63,0.35)', 0, 14);
  g.fillStyle = 'rgba(27,31,59,0.12)'; for (let y = 20; y < DH; y += 40) for (let x = 20 + ((y / 40) % 2) * 20; x < DW; x += 40) { g.beginPath(); g.arc(x, y, 1.7, 0, 7); g.fill(); } })();
let HT = null, GR = null;
const CRACKS = (() => { const L = []; const pts = [[60, -40], [-70, 120], [40, 230], [-40, -150], [90, 60], [-90, -40], [0, 40]];
  pts.forEach(([x0, y0], k) => { const br = []; for (let b = 0; b < 7; b++) { let x = x0, y = y0, a = (b / 7) * 6.283 + hash(k * 9 + b) * 0.8; const p = [[x, y]];
      for (let s = 0; s < 9; s++) { a += (hash(k * 99 + b * 13 + s) - 0.5) * 0.9; const len = 14 + 22 * hash(k * 7 + b * 3 + s * 5); x += Math.cos(a) * len; y += Math.sin(a) * len; p.push([x, y]); } br.push(p); } L.push(br); });
  return L; })();
const SHARDS = (() => { const S = []; const nx = 4, ny = 7, w = 300 / nx, h = 620 / ny; const J = (i, j) => [(-150 + i * w) + (i > 0 && i < nx ? (hash(i * 31 + j * 7) - 0.5) * w * 0.6 : 0), (-310 + j * h) + (j > 0 && j < ny ? (hash(i * 17 + j * 53) - 0.5) * h * 0.6 : 0)];
  for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) { const a = J(i, j), b = J(i + 1, j), c = J(i + 1, j + 1), d = J(i, j + 1); S.push([a, b, c]); S.push([a, c, d]); }
  return S.map((p, k) => { const cx = (p[0][0] + p[1][0] + p[2][0]) / 3, cy = (p[0][1] + p[1][1] + p[2][1]) / 3; return { p, cx, cy, vx: cx * 3.2 + (hash(k) - 0.5) * 300, vy: cy * 2.2 - 260 - hash(k + 5) * 300, rot: (hash(k + 9) - 0.5) * 9 }; }); })();
const PH = document.createElement('canvas'); PH.width = Math.ceil(320 * KK * 1.4); PH.height = Math.ceil(640 * KK * 1.4); const PG = PH.getContext('2d');

// ---------- helpers ----------
function fitFont(g, txt, weight, size, family, maxW) { g.font = `${weight} ${size}px "${family}"`; const w = g.measureText(txt).width; if (w > maxW) { size *= maxW / w; g.font = `${weight} ${size}px "${family}"`; } return size; }
function rr(g, x, y, w, h, r) { g.beginPath(); g.roundRect(x, y, w, h, r); }
function riso(g, txt, x, y, col, off = 4, sh = PINK) { g.fillStyle = sh; g.fillText(txt, x + off, y + off); g.fillStyle = col; g.fillText(txt, x, y); }
function background(g, t) {
  g.setTransform(1, 0, 0, 1, 0, 0); g.drawImage(BG, 0, 0); g.setTransform(KK, 0, 0, KK, 0, 0);
  const ring = (cx, cy, r, col, ph) => { g.save(); g.translate(cx, cy); g.rotate(t * 0.25 + ph); g.strokeStyle = col; g.lineWidth = 2.2;
    for (let k = 0; k < 12; k++) { g.rotate(Math.PI / 6); g.beginPath(); g.ellipse(r * 0.55, 0, r * 0.45, r * 0.18, 0, 0, 7); g.stroke(); } g.beginPath(); g.arc(0, 0, r * 1.02, 0, 7); g.stroke(); g.restore(); };
  ring(40, 120, 150, 'rgba(255,92,138,0.30)', 0); ring(690, 1200, 170, 'rgba(255,138,31,0.30)', 1); ring(20, 1180, 100, 'rgba(61,75,224,0.18)', 3);
}
function grainPass(g, t) { g.setTransform(1, 0, 0, 1, 0, 0); g.save(); g.globalAlpha = 0.07; g.globalCompositeOperation = 'multiply'; if (!GR) GR = g.createPattern(grain, 'repeat');
  const f = Math.floor(t * 30); g.translate(hash(f) * 256, hash(f + 7) * 256); g.fillStyle = GR; g.fillRect(-256, -256, W + 512, H + 512); g.restore(); }
function card(g, x, y, w, h, title, sub, big = false, col = GREEN) {
  g.save(); g.fillStyle = 'rgba(27,31,59,0.16)'; rr(g, x + 3, y + 4, w, h, 14); g.fill();
  g.fillStyle = '#FFFFFF'; rr(g, x, y, w, h, 14); g.fill();
  const r = big ? 34 : 17, cx = x + 12 + r, cy = y + h / 2; g.fillStyle = col; g.beginPath(); g.arc(cx, cy, r, 0, 7); g.fill();
  g.strokeStyle = '#fff'; g.lineWidth = big ? 8 : 3.8; g.lineCap = 'round'; g.lineJoin = 'round'; g.beginPath(); g.moveTo(cx - r * 0.42, cy + 0.02 * r); g.lineTo(cx - r * 0.1, cy + r * 0.32); g.lineTo(cx + r * 0.45, cy - r * 0.3); g.stroke();
  if (!NOTEXT) { g.textAlign = 'left'; g.fillStyle = INK; fitFont(g, title, 900, big ? 64 : 24, 'Inter Display', w - (2 * r + 38)); g.fillText(title, cx + r + 12, cy + (big ? 6 : 2));
    g.font = `800 ${big ? 22 : 18}px "JetBrains Mono"`; g.fillStyle = 'rgba(27,31,59,0.6)'; g.fillText(sub, cx + r + 12, cy + (big ? 40 : 24)); }
  g.restore();
}
function phone(g, who, t, o = {}) {
  const hdr = who === 'A' ? INDIGO : SAFF, d = dayAt(t);
  g.save(); if (!HT) HT = g.createPattern(halftone, 'repeat'); g.globalAlpha = 0.42; g.fillStyle = HT; rr(g, -134, -290, 300, 620, 44); g.fill(); g.restore();
  g.fillStyle = who === 'A' ? 'rgba(255,92,138,0.9)' : 'rgba(61,75,224,0.85)'; rr(g, -146, -306, 300, 620, 44); g.fill(); // riso misregistration
  g.fillStyle = INK; rr(g, -150, -310, 300, 620, 44); g.fill();
  g.save(); rr(g, -140, -300, 280, 600, 34); g.clip();
  g.fillStyle = '#F3F4FA'; g.fillRect(-140, -300, 280, 600);
  g.fillStyle = hdr; g.fillRect(-140, -300, 280, 196);
  g.fillStyle = 'rgba(255,255,255,0.10)'; for (let i = 0; i < 6; i += 2) { g.beginPath(); g.arc(110 - i * 12, -280 + i * 8, 70 + i * 22, 0, 7); g.fill(); }
  if (!NOTEXT) {
    g.fillStyle = 'rgba(255,255,255,0.9)'; g.font = '700 12px "JetBrains Mono"'; g.textAlign = 'left'; g.fillText('9:41', -118, -278); g.textAlign = 'right'; g.fillText('▮▮▮ 92%', 118, -278);
    g.textAlign = 'center'; g.font = '800 15px "JetBrains Mono"'; g.letterSpacing = '1px'; g.fillStyle = 'rgba(255,255,255,0.92)';
    g.fillText(who === 'A' ? '₹1 CRORE · TODAY' : '₹1 · DOUBLED DAILY', 0, -238); g.letterSpacing = '0px';
    const bal = who === 'A' ? 1e7 : (o.bal ?? liveVal(t)); const pop = o.pop || 0;
    g.save(); g.translate(0, -186); g.scale(1 + 0.06 * pop, 1 + 0.06 * pop); g.fillStyle = '#fff'; fitFont(g, inr(bal), 900, 50, 'Inter Display', 236); g.fillText(inr(bal), 0, 17); g.restore();
    g.font = '800 13px "JetBrains Mono"'; g.fillStyle = 'rgba(255,255,255,0.85)'; g.fillText('BALANCE', 0, -128);
  }
  if (who === 'A') card(g, -130, -90, 260, 78, '₹1,00,00,000', 'CREDITED · TODAY');
  else if (d > 0) {
    const e = d === 1 ? 1 : spr((t - TD[d]) * 1.3);
    for (let k = 0; k < 7; k++) { const j = d - k; if (j < 1) break; const y = -90 + (k - (1 - e)) * 86; if (y > 300) break;
      g.save(); if (k === 0 && d > 1) { const s = lerp(0.85, 1, e); g.translate(0, y + 39); g.scale(s, s); g.translate(0, -(y + 39)); g.globalAlpha = clamp(e * 2); }
      card(g, -130, y, 260, 78, '+' + inr(Math.pow(2, j - 1)), `DAY ${j} · CREDITED`); g.restore(); }
  }
  if (o.cracks > 0) { g.lineCap = 'round'; for (let c = 0; c < Math.min(CRACKS.length, Math.ceil(o.cracks)); c++) { const grow = clamp(o.cracks - c); for (const br of CRACKS[c]) { const n = Math.max(1, Math.floor((br.length - 1) * grow));
        g.strokeStyle = 'rgba(27,31,59,0.11)'; g.lineWidth = 2; g.beginPath(); g.moveTo(br[0][0] + 1, br[0][1] + 1); for (let i = 1; i <= n; i++) g.lineTo(br[i][0] + 1, br[i][1] + 1); g.stroke();
        g.strokeStyle = 'rgba(255,255,255,0.35)'; g.lineWidth = 1.2; g.beginPath(); g.moveTo(br[0][0], br[0][1]); for (let i = 1; i <= n; i++) g.lineTo(br[i][0], br[i][1]); g.stroke(); } } }
  const gl = g.createLinearGradient(-140, -300, 140, 300); gl.addColorStop(0, 'rgba(255,255,255,0.10)'); gl.addColorStop(0.45, 'rgba(255,255,255,0)'); g.fillStyle = gl; g.fillRect(-140, -300, 280, 600);
  g.restore();
  g.fillStyle = INK; rr(g, -40, -298, 80, 18, 9); g.fill();
}
// stamp in screen space. Default zone is the title band above the race bar.
function stamp(g, lines, k, o = {}) {
  if (k <= 0 || NOTEXT) return; const y = o.y ?? 262, size = o.size ?? 40, size2 = o.size2 ?? size * 0.78, bg = o.bg ?? '#fff', fg = o.fg ?? INK, rot = o.rot ?? -0.02, pop = o.pop ?? 0;
  g.setTransform(KK, 0, 0, KK, 0, 0); g.save(); g.translate(o.x ?? 360, y); g.rotate(rot); const sc = 1 + pop * 0.12; g.scale(sc, sc); g.globalAlpha = clamp(k * 3);
  const ws = lines.map((l, i) => { const s = fitFont(g, l, 900, i ? size2 : size, 'Inter Display', o.maxW ?? 540); return { s, w: g.measureText(l).width }; });
  const w = Math.max(...ws.map(q => q.w)) + 44, h = ws.reduce((a, q) => a + q.s * 1.06, 0) + 24;
  g.fillStyle = o.shadow ?? PINK; rr(g, -w / 2 + 6, -h / 2 + 6, w, h, 10); g.fill();
  g.fillStyle = bg; rr(g, -w / 2, -h / 2, w, h, 10); g.fill();
  g.textAlign = 'center'; let yy = -h / 2 + 12;
  lines.forEach((l, i) => { g.font = `900 ${ws[i].s}px "Inter Display"`; yy += ws[i].s * 0.88; g.fillStyle = i && o.fg2 ? o.fg2 : fg; if (!(i && o.l2at && T < o.l2at)) { g.save(); if (i && o.l2at) { const q = popAt(T, o.l2at); g.translate(0, yy - ws[i].s * 0.3); g.scale(1 + q * 0.08, 1 + q * 0.08); g.translate(0, -(yy - ws[i].s * 0.3)); } g.fillText(l, 0, yy); g.restore(); } yy += ws[i].s * 0.18; });
  g.restore();
}
const win = (t, a, b, f = 0.034) => t < a || t > b ? 0 : Math.min(1, (t - a) / f, (b - t) / f);
const popAt = (t, a) => t < a ? 0 : Math.max(0, 1 - (t - a) / 0.12);

// ---------- camera ----------
function camAt(t) {
  const d = dayAt(t); const punch = d >= 2 && t < T_SLAM + 0.5 ? 0.035 * Math.exp(-(t - TD[d]) * 9) : 0;
  let cx = 360, cy = 640, z = 1;
  if (t >= TD[10] && t < TD[11]) { cx = PX; cy = PY - 186 * 1.08 - 10; z = 1.55; }                       // hard cut in on the ₹1,023
  else if (t >= TD[20] && t < TD[20] + 0.8) { cx = PX; cy = PY - 186 * 1.08 - 10; z = 1.5 + 0.08 * (t - TD[20]); } // hard cut in on ₹10 lakh
  else if (t >= T_FOLD && t < T_FLIP) z = 1 + 0.07 * ss(TD[21], T_FLIP, t);
  else if (t >= T_FLIP && t < T_SLAM) z = 1 + 0.06 * ss(TD[25], T_SLAM, t);
  else if (t >= T_SLAM) z = 1.06 + 0.04 * ss(T_SLAM, T_SHAT, t) - 0.2 * eout((t - T_SHAT) / 0.5);
  return { cx, cy, z: z + punch };
}
function shakeAt(t) {
  let s = 0; const d = dayAt(t);
  if (t >= TD[20] && t < TD[20] + 0.25) s += 6 * (1 - (t - TD[20]) / 0.25);
  if (t >= T_FLIP && t < T_FLIP + 0.45) s += 12 * (1 - (t - T_FLIP) / 0.45);
  if (d >= 25 && d < 30) s += (2 + (d - 25) * 1.5) * Math.exp(-(t - TD[d]) * 5) + (d - 24) * 0.5;
  if (t >= T_SLAM && t < T_SHAT + 0.3) s += 10 * Math.exp(-(t - T_SLAM) * 3);
  return [s * Math.sin(t * 91.7), s * Math.cos(t * 77.3)];
}

// ---------- race bar (open loop, frame 0 -> CTA) ----------
const BX = 84, BW = 552, BYY = 352, BH = 40;
function flagX(v) { return BX + BW * Math.min(1, 1e7 / Math.max(v, 1e7)); }
function raceBar(g, t, d, v) {
  if (NOTEXT) return; g.setTransform(KK, 0, 0, KK, 0, 0); const pp = d > 0 ? Math.exp(-(t - TD[d]) * 9) : 0;
  const [sx, sy] = t >= T_FLIP && t < T_FLIP + 0.45 ? shakeAt(t) : [0, 0]; g.save(); g.translate(sx, sy);
  g.fillStyle = 'rgba(27,31,59,0.12)'; rr(g, BX, BYY, BW, BH, 20); g.fill();
  const fill = v >= 1e7 ? BW : Math.max(BH, BW * v / 1e7);
  g.fillStyle = INDIGO; rr(g, BX + 4, BYY + 4, fill, BH, 20); g.fill();   // riso offset
  g.fillStyle = SAFF; rr(g, BX, BYY, fill, BH, 20); g.fill();
  g.save(); rr(g, BX, BYY, fill, BH, 20); g.clip(); g.fillStyle = 'rgba(255,255,255,0.22)'; for (let x = BX - 60 + (t * 120) % 30; x < BX + fill; x += 30) { g.beginPath(); g.moveTo(x, BYY + BH); g.lineTo(x + 14, BYY + BH); g.lineTo(x + 34, BYY); g.lineTo(x + 20, BYY); g.fill(); } g.restore();
  g.strokeStyle = INK; g.lineWidth = 3; rr(g, BX, BYY, BW, BH, 20); g.stroke();
  const fx = flagX(v);
  const badge = () => { g.fillStyle = PINK; g.beginPath(); g.arc(3, 3, 34, 0, 7); g.fill(); g.fillStyle = INDIGO; g.beginPath(); g.arc(0, 0, 34, 0, 7); g.fill();
    g.fillStyle = '#fff'; g.textAlign = 'center'; g.font = '900 17px "Inter Display"'; g.fillText('₹1', 0, -3); g.font = '900 13px "Inter Display"'; g.fillText('CRORE', 0, 13); };
  if (t < T_FLIP) { const k = t < T_FOLD + 0.3 ? 1 + 0.25 * popAt(t, 0) : 1 + 0.35 * Math.max(0, 1 - (t - T_FOLD - 0.3) / 0.15); g.save(); g.translate(BX + BW, BYY + BH / 2); g.scale(k, k); badge(); g.restore(); }
  if (t >= T_FLIP) {
    const k = t - T_FLIP; if (k < 1.2) { g.save(); g.translate(BX + BW - 330 * k, BYY + BH / 2 - 120 * k + 1300 * k * k); g.scale(1 + k, 1 + k); g.rotate(-k * 7); badge(); g.restore(); }
    g.fillStyle = INDIGO; g.fillRect(fx - 2.5, BYY - 10, 5, BH + 20);
    
  }
  const dd = Math.max(1, d); g.save(); g.translate(BX, BYY + BH + 38); g.scale(1 + 0.1 * pp, 1 + 0.1 * pp);
  g.fillStyle = d >= 28 ? RED : INK; rr(g, -2, -32, 160, 46, 23); g.fill(); g.fillStyle = '#fff'; g.font = '800 29px "JetBrains Mono"'; g.textAlign = 'center'; g.fillText(`DAY ${String(dd).padStart(2, '0')}`, 78, 1); g.restore();
  g.textAlign = 'right'; g.font = '900 30px "Inter Display"';
  if (v < 1e7) { const gap = 1e7 - v; g.fillStyle = RED; g.fillText(`${inr(gap)} BEHIND`, BX + BW, BYY + BH + 40); }
  else { const m = v / 1e7; g.save(); g.translate(BX + BW, BYY + BH + 46); g.scale(1 + 0.07 * pp, 1 + 0.07 * pp); g.textAlign = 'right'; g.font = '900 44px "Inter Display"'; riso(g, `${m < 10 ? m.toFixed(1) : Math.round(m)}× ₹1 CRORE`, 0, 0, '#0A8A4E', 3, YEL); g.restore(); }
  g.restore();
}

// ---------- frame ----------
function frame(g, t) {
  T = t;
  const d = dayAt(t), v = liveVal(t), pop = d > 1 ? Math.exp(-(t - TD[d]) * 9) : 0;
  background(g, t);
  const c = camAt(t), [sx, sy] = shakeAt(t);
  const world = () => g.setTransform(KK * c.z, 0, 0, KK * c.z, KK * (360 - c.cx * c.z + sx), KK * (640 - c.cy * c.z + sy));
  if (t < T_SHAT) {
    const f = eout((t - T_FOLD) / 0.35);
    const bx = lerp(530, PX, f), by = lerp(PY + 40, PY, f), bs = lerp(1.04, 1.08, f);
    world(); g.save(); g.translate(bx, by); g.scale(bs, bs); if (d >= 25) g.rotate(Math.sin(t * 60) * 0.004 * (d - 24));
    phone(g, 'B', t, { pop, cracks: d >= 25 ? (d - 25) + clamp((t - TD[d]) / 0.2) + (t >= T_SLAM ? 2 * clamp((t - T_SLAM) / 0.3) : 0) : 0 }); g.restore();
    if (t < T_FOLD + 0.35) {
      const k = ein((t - T_FOLD) / 0.35); const ax = lerp(190, BX + BW, k), ay = lerp(PY + 40, BYY + BH / 2, k), as = lerp(1.04, 0.06, k);
      world(); g.save(); g.translate(ax, ay); g.scale(as, as); g.rotate(k * 0.6); phone(g, 'A', t); g.restore(); }
  } else if (t < T_SHAT + 1.4) {
    const bs = 1.08, sc = KK * 1.4; PG.setTransform(1, 0, 0, 1, 0, 0); PG.clearRect(0, 0, PH.width, PH.height); PG.setTransform(sc, 0, 0, sc, PH.width / 2, PH.height / 2);
    phone(PG, 'B', T_SHAT - 0.001, { bal: val(30), cracks: 7 });
    const k = t - T_SHAT; world();
    for (const s of SHARDS) { g.save(); g.translate(PX + (s.cx + s.vx * k) * bs, PY + (s.cy + s.vy * k + 900 * k * k) * bs); g.rotate(s.rot * k); g.scale(bs, bs); g.translate(-s.cx, -s.cy);
      g.beginPath(); g.moveTo(...s.p[0]); g.lineTo(...s.p[1]); g.lineTo(...s.p[2]); g.closePath(); g.clip(); g.globalAlpha = clamp(1.4 - k);
      g.drawImage(PH, -PH.width / 2 / sc, -PH.height / 2 / sc, PH.width / sc, PH.height / sc); g.restore(); }
  }
  if (t >= T_SLAM && t < T_SHAT + 0.9) { g.setTransform(KK, 0, 0, KK, 0, 0); const k = clamp((t - T_SLAM) / 0.12), sc = lerp(2.2, 1, eout(k)); const fly = Math.max(0, t - T_SHAT);
    g.save(); g.translate(360 + sx, 700 - 900 * fly * fly - 200 * fly + sy); g.rotate(-0.05 + fly * 0.8); g.scale(sc, sc); g.globalAlpha = clamp(k * 3) * clamp(1.4 - fly * 2);
    card(g, -285, -95, 570, 190, '+₹53,68,70,912', 'DAY 30 · ONE DAY', true); g.restore(); }
  if (t >= T_PAY - 0.05 && t < T_CTA) payoff(g, t);
  if (t < T_CTA) raceBar(g, t, d, v);
  if (t < T_FOLD + 0.15 && !NOTEXT) { g.setTransform(KK, 0, 0, KK, 0, 0); const up = ein((t - T_FOLD + 0.1) / 0.25);
    g.save(); g.translate(0, -200 * up); g.textAlign = 'center'; const p2 = popAt(t, 0.4);
    fitFont(g, '₹1 CRORE NOW…', 900, 74, 'Inter Display', 560); riso(g, '₹1 CRORE NOW…', 360, 262, INDIGO, 4);
    g.save(); g.translate(360, 330); g.scale(1 + p2 * 0.25, 1 + p2 * 0.25); fitFont(g, 'OR ₹1 DOUBLED 30 DAYS?', 900, 66, 'Inter Display', 570); riso(g, 'OR ₹1 DOUBLED 30 DAYS?', 0, 0, SAFF, 4, INK); g.restore();
    g.restore(); }
  stamp(g, ['WHICH ONE', 'DO YOU TAKE?'], win(t, T_FOLD + 0.15, TD[6] + 0.1), { size: 44, size2: 40, pop: popAt(t, T_FOLD + 0.15), bg: YEL });
  stamp(g, ['₹1 DOUBLES', 'EVERY DAY. 30 DAYS.'], win(t, TD[6] + 0.12, TD[10] - 0.02), { size: 40, size2: 34, pop: popAt(t, TD[6] + 0.12), shadow: SAFF });
  stamp(g, ['DAY 10: ₹1,023.', 'LOOKS STUPID, RIGHT?'], win(t, TD[10], TD[11] - 0.02), { size: 44, size2: 36, l2at: TD[10] + 0.38, pop: popAt(t, TD[10]), bg: YEL, shadow: INDIGO });
  stamp(g, [`DAY ${d}: ${inr(val(d))}.`, 'NOT EVEN 0.1%.'], win(t, TD[11], TD[14] - 0.02), { size: 44, size2: 38, pop: popAt(t, TD[11]), shadow: SAFF });
  stamp(g, [`DAY ${d}: ${inr(val(d))}.`, 'THAT\'S IT?'], win(t, TD[14], TD[17] - 0.02), { size: 44, size2: 38, pop: popAt(t, TD[14]), bg: YEL, shadow: PINK });
  stamp(g, [`DAY ${d}: ${inr(val(d))}.`, `STILL ${Math.floor((1 - val(d) / 1e7) * 100)}% BEHIND.`], win(t, TD[17], TD[20] - 0.02), { size: 44, size2: 38, pop: popAt(t, TD[d]) * 0.6, shadow: RED });
  stamp(g, ['DAY 20: ₹10 LAKH.', 'STILL ₹89 LAKH BEHIND.'], win(t, TD[20], TD[21] - 0.02), { size: 44, size2: 34, l2at: TD[20] + 0.4, pop: popAt(t, TD[20]), bg: YEL, shadow: RED });
  stamp(g, [`ONLY ${30 - d} DAYS LEFT…`], win(t, TD[21], TD[23] - 0.02), { size: 40, pop: popAt(t, TD[d]) * 0.6, shadow: PINK });
  stamp(g, ['DAY 23: SO CLOSE.'], win(t, TD[23], T_FLIP - 0.02), { size: 46, pop: popAt(t, TD[23]), shadow: RED });
  stamp(g, ['OVERTAKEN.'], win(t, T_FLIP + 0.02, T_FLIP + 0.85, 0.03), { y: 700, size: 104, pop: popAt(t, T_FLIP + 0.02), bg: RED, fg: '#fff', shadow: INK, rot: -0.08, maxW: 500 });
  stamp(g, ['DAY 24. AND 6 DAYS', 'ARE STILL LEFT…'], win(t, T_FLIP + 0.85, TD[25] - 0.02), { size: 40, size2: 40, pop: popAt(t, T_FLIP + 0.85), bg: GREEN, fg: '#fff', shadow: INK });
  stamp(g, ['EACH DAY ADDS MORE', 'THAN ALL DAYS BEFORE.'], win(t, TD[25], TD[27] - 0.02), { size: 36, size2: 36, pop: popAt(t, TD[25]), shadow: SAFF });
  stamp(g, ['HOW HIGH', 'DOES IT GO?'], win(t, TD[27], TD[29] - 0.02), { size: 46, size2: 46, pop: popAt(t, TD[27]), bg: YEL, shadow: INDIGO });
  stamp(g, ['1 DAY LEFT…', 'HOW MUCH WILL IT ADD?'], win(t, TD[29], T_SLAM - 0.02), { size: 54, size2: 34, l2at: TD[29] + 0.38, pop: popAt(t, TD[29]), bg: RED, fg: '#fff', shadow: INK, rot: 0.03 });
  for (const [a, s] of [[T_FLIP, 0.55], [T_SLAM, 0.35], [T_SHAT, 0.6]]) if (t >= a && t < a + 0.1) { g.setTransform(1, 0, 0, 1, 0, 0); g.fillStyle = `rgba(255,255,255,${s * (1 - (t - a) / 0.1)})`; g.fillRect(0, 0, W, H); }
  if (t >= T_CTA) cta(g, t);
  if (t >= T_CTA - 0.13 && t < T_CTA + 0.16) { g.setTransform(KK, 0, 0, KK, 0, 0); const q = t < T_CTA ? eout((t - T_CTA + 0.13) / 0.13) : 1 - ein((t - T_CTA) / 0.16); const r = 26 * q; g.fillStyle = YEL;
    for (let y = 0; y < DH + 40; y += 34) for (let x = (Math.round(y / 34) % 2) * 17; x < DW + 40; x += 34) { g.beginPath(); g.arc(x, y, r * (0.75 + 0.25 * hash(x * 7 + y)), 0, 7); g.fill(); } }
  grainPass(g, t);
}
function confetti(g, t, t0, n, a = 0.85) { for (let i = 0; i < n; i++) { const s = 0.5 + hash(i) * 0.9, x = hash(i + 3) * 760 - 20 + Math.sin(t * 2 + i) * 20, y = -60 + ((t - t0 + 0.3) * (260 + 200 * hash(i + 7)) + hash(i + 11) * 1300) % 1400;
  g.save(); g.translate(x, y); g.rotate(t * (2 + hash(i) * 4) + i); g.fillStyle = [SAFF, INDIGO, PINK, YEL, GREEN][i % 5]; g.globalAlpha = a; g.fillRect(-7 * s, -3.5 * s, 14 * s, 7 * s); g.restore(); } }
const BASE = 960, CSC = 222 / 236;
const BARS = [{ x: 150, m: 2.2, col: INDIGO, lab: '₹1 CRORE', lab2: '2.2 m' }, { x: 360, m: 182, col: null, lab: 'STATUE OF', lab3: 'UNITY', lab2: '182 m' }, { x: 570, m: 236, col: SAFF, lab: 'DAY 30', lab2: '236 m' }];
function payoff(g, t) {
  g.setTransform(KK, 0, 0, KK, 0, 0); const k = t - T_PAY;
  confetti(g, t, T_PAY, 70);
  if (NOTEXT) return;
  const n = lerp(val(29), val(30), eout(k / 0.5)); g.textAlign = 'center';
  const p = popAt(t, T_PAY); g.save(); g.translate(360, 568); g.scale(1 + p * 0.2, 1 + p * 0.2); g.rotate(-0.03);
  fitFont(g, '₹107 CRORE', 900, 112, 'Inter Display', 520); riso(g, '₹107 CRORE', 0, 0, INDIGO, 5); g.restore();
  if (k > 0.5) { g.font = '800 34px "JetBrains Mono"'; g.fillStyle = INK; g.fillText(inr(val(30)), 360, 618); }
  stamp(g, ['HALF OF IT CAME', 'ON THE LAST DAY.'], win(t, T_PAY + 0.2, T_CHART - 0.02), { y: 740, size: 50, pop: popAt(t, T_PAY + 0.2), bg: YEL, shadow: PINK });
  const a = eout((t - T_CHART) / 0.55); if (a > 0) {
    g.globalAlpha = clamp(a * 2); g.font = '800 26px "JetBrains Mono"'; g.fillStyle = INK; g.fillText('STACKED IN ₹500 NOTES', 360, 660); g.globalAlpha = 1;
    g.fillStyle = INK; g.fillRect(80, BASE, 560, 4);
    for (const b of BARS) { const h = Math.max(4, b.m * CSC * a);
      if (!b.col) { statue(g, b.x + 4, BASE, h, PINK); statue(g, b.x, BASE, h, INK); }
      else { g.fillStyle = b.col; g.fillRect(b.x - 50, BASE - h, 100, h); g.fillStyle = 'rgba(27,31,59,0.18)'; for (let yy = BASE - 7; yy > BASE - h; yy -= 9) g.fillRect(b.x - 50, yy, 100, 1.6); }
      g.globalAlpha = clamp(a * 2); g.fillStyle = INK; g.font = '900 26px "Inter Display"'; const top = BASE - h;
      if (b.lab3) { g.fillText(b.lab, b.x, top - 60); g.fillText(b.lab3, b.x, top - 34); } else g.fillText(b.lab, b.x, top - 34);
      g.font = '800 22px "JetBrains Mono"'; g.fillStyle = b.col === SAFF ? '#C25A00' : INK; g.fillText(b.lab2, b.x, top - 10); g.globalAlpha = 1; }
    stamp(g, ['1.3× STATUE', 'OF UNITY'], win(t, T_CHART + 0.6, T_CTA), { x: 170, y: 820, size: 30, size2: 30, pop: popAt(t, T_CHART + 0.6), bg: YEL, shadow: INK, rot: -0.1, maxW: 260 });
  }
}
function statue(g, x, base, h, col) { // riso silhouette: pedestal + standing figure with shawl, head ~ top
  const ped = h * 0.3, fh = h - ped, w = fh * 0.32; g.fillStyle = col; g.beginPath();
  g.moveTo(x - 46, base); g.lineTo(x + 46, base); g.lineTo(x + 40, base - ped * 0.55); g.lineTo(x + 30, base - ped * 0.6); g.lineTo(x + 26, base - ped); g.lineTo(x - 26, base - ped); g.lineTo(x - 30, base - ped * 0.6); g.lineTo(x - 40, base - ped * 0.55); g.closePath(); g.fill();
  const y0 = base - ped; g.beginPath(); g.moveTo(x - w * 0.55, y0); g.lineTo(x + w * 0.55, y0); g.lineTo(x + w * 0.62, y0 - fh * 0.55); g.lineTo(x + w * 0.5, y0 - fh * 0.82); g.lineTo(x + w * 0.2, y0 - fh * 0.88); g.lineTo(x - w * 0.2, y0 - fh * 0.88); g.lineTo(x - w * 0.5, y0 - fh * 0.82); g.lineTo(x - w * 0.62, y0 - fh * 0.55); g.closePath(); g.fill();
  g.beginPath(); g.ellipse(x, y0 - fh * 0.93, w * 0.17, fh * 0.07, 0, 0, 7); g.fill(); }
function cta(g, t) {
  background(g, t); g.setTransform(KK, 0, 0, KK, 0, 0); confetti(g, t, T_CTA, 40, 0.7);
  const k = eout((t - T_CTA) / 0.32);
  const btn = (b, tx, num, l1, l2, col, on) => { const h0 = Math.max(4, b.m * CSC);
    const x = lerp(b.x - 50, tx - 125, k), y = lerp(BASE - h0, 640, k), w = lerp(100, 250, k), h = lerp(h0, 150, k), r = lerp(0, 24, k);
    g.save(); if (on && k >= 1) { g.translate(tx, 715); g.scale(1.06, 1.06); g.translate(-tx, -715); }
    g.fillStyle = INK; rr(g, x + 6, y + 6, w, h, r); g.fill(); g.fillStyle = col; rr(g, x, y, w, h, r); g.fill();
    if (on && k >= 1) { g.strokeStyle = YEL; g.lineWidth = 8; rr(g, x - 9, y - 9, w + 18, h + 18, r + 6); g.stroke(); }
    if (!NOTEXT) { g.globalAlpha = clamp((k - 0.6) * 3); g.fillStyle = '#fff'; g.textAlign = 'center'; g.font = '900 44px "Inter Display"'; g.fillText(num, tx, y + 52); fitFont(g, l1, 900, 30, 'Inter Display', 220); g.fillText(l1, tx, y + 94); g.font = '800 17px "JetBrains Mono"'; g.fillText(l2, tx, y + 124); g.globalAlpha = 1; }
    g.restore(); };
  const sel = Math.floor((t - T_CTA - 0.35) / 0.45) % 2;
  btn(BARS[0], 215, '1', 'TAKE ₹1 CRORE', 'SAFE. TODAY.', INDIGO, sel === 0); btn(BARS[2], 505, '2', 'HOLD 30 DAYS', 'TRUST THE DOUBLING', SAFF, sel === 1);
  if (NOTEXT) return;
  const p = popAt(t, T_CTA); g.textAlign = 'center';
  g.save(); g.translate(360, 380); g.scale(1 + p * 0.4, 1 + p * 0.4); fitFont(g, 'DAY 17: STILL 98% BEHIND.', 900, 50, 'Inter Display', 560); riso(g, 'DAY 17: STILL 98% BEHIND.', 0, 0, INK, 3);
  fitFont(g, 'WOULD YOU HOLD?', 900, 78, 'Inter Display', 560); riso(g, 'WOULD YOU HOLD?', 0, 92, SAFF, 5, INK); g.restore();
  g.globalAlpha = clamp((t - T_CTA - 0.35) / 0.15); const pc = popAt(t, T_CTA + 0.35); g.save(); g.translate(330, 920); g.scale(1 + pc * 0.4, 1 + pc * 0.4); fitFont(g, 'COMMENT 1 OR 2', 900, 60, 'Inter Display', 480); riso(g, 'COMMENT 1 OR 2', 0, 0, INK, 4, YEL); g.restore();
  const bob = Math.abs(Math.sin((t - T_CTA) * 7)) * 12; g.font = '60px "Noto Color Emoji"'; g.textAlign = 'left'; g.fillText('👇', 590, 915 + bob); g.globalAlpha = 1;
}

window.renderAt = (t, sub = 1) => {
  sub = Math.max(1, sub | 0);
  if (sub === 1) frame(out, t);
  else { out.setTransform(1, 0, 0, 1, 0, 0); out.fillStyle = '#000'; out.fillRect(0, 0, W, H);
    for (let i = 0; i < sub; i++) { A.setTransform(1, 0, 0, 1, 0, 0); frame(A, Math.max(0, t + (i / sub - 0.5) / 90)); out.setTransform(1, 0, 0, 1, 0, 0); out.globalCompositeOperation = 'lighter'; out.globalAlpha = 1 / sub; out.drawImage(acc, 0, 0); }
    out.globalCompositeOperation = 'source-over'; out.globalAlpha = 1; }
  return cv.toDataURL('image/jpeg', 0.95);
};
window.events = (() => {
  const e = [{ t: 0.0, s: 'chime', g: 1.0, pan: -0.2 }, { t: 0.0, s: 'stamp', g: 0.9 }, { t: T_FOLD, s: 'whoosh', g: 0.9 }, { t: T_FOLD + 0.3, s: 'stamp', g: 0.8 }];
  for (let d = 2; d <= 29; d++) {
    if (d === 24) continue;
    e.push({ t: TD[d], s: 'ping', g: d <= 10 ? 0.8 : 0.85, pan: 0.2, rate: Math.min(1.7, 1 + (d - 2) * 0.026) });
    if (d >= 3) e.push({ t: TD[d] + 0.02, s: 'buzz', g: d < 11 ? 0.45 : lerp(0.5, 0.85, (d - 11) / 18), pan: 0.1 });
    if (d >= 3 && d <= 10) e.push({ t: TD[d], s: 'coin', g: 0.5, pan: -0.2, rate: 1 + d * 0.04 });
    if (d >= 25) e.push({ t: TD[d] + 0.03, s: 'crack', g: lerp(0.5, 0.9, (d - 25) / 4), rate: lerp(1.1, 0.9, (d - 25) / 4) });
  }
  e.push({ t: TD[6] + 0.12, s: 'stamp', g: 0.6 }, { t: TD[10], s: 'stamp', g: 1.0 }, { t: TD[10], s: 'whoosh', g: 0.5 }, { t: TD[11], s: 'whoosh', g: 0.6 });
  e.push({ t: TD[20], s: 'scratch', g: 0.8 }, { t: TD[20], s: 'stamp', g: 1.0 }, { t: TD[21], s: 'stamp', g: 0.6 });
  e.push({ t: TD[21] - 0.1, s: 'heart', g: 0.9 }, { t: TD[23], s: 'stamp', g: 0.8 }, { t: T_FLIP - 0.6, s: 'rise', g: 0.6 });
  e.push({ t: T_FLIP, s: 'boom', g: 1.0 }, { t: T_FLIP, s: 'crack', g: 1.0, rate: 0.9 }, { t: T_FLIP + 0.02, s: 'stamp', g: 1.0 }, { t: T_FLIP + 0.1, s: 'ooh', g: 0.7 }, { t: T_FLIP + 0.5, s: 'stamp', g: 0.8 }, { t: T_FLIP + 0.5, s: 'cash', g: 0.7 });
  e.push({ t: T_FLIP + 0.85, s: 'stamp', g: 0.8 }, { t: TD[27], s: 'stamp', g: 0.7 }, { t: TD[11], s: 'stamp', g: 0.6 }, { t: TD[14], s: 'stamp', g: 0.6 }, { t: TD[17], s: 'stamp', g: 0.6 }, { t: 1.6, s: 'rise', g: 0.5 }, { t: TD[25] + 0.01, s: 'stamp', g: 0.5 }, { t: TD[29], s: 'stamp', g: 0.8 }, { t: T_SLAM - 0.7, s: 'rise', g: 0.8 });
  e.push({ t: T_SLAM, s: 'boom', g: 1.0, rate: 0.85 }, { t: T_SLAM, s: 'stamp', g: 1.0 }, { t: T_SLAM + 0.02, s: 'ping', g: 1.0, rate: 0.8 });
  e.push({ t: T_SHAT, s: 'shatter', g: 1.0 }, { t: T_SHAT, s: 'boom', g: 0.8, rate: 1.1 }, { t: T_PAY, s: 'chime', g: 1.0 }, { t: T_PAY, s: 'cash', g: 0.7 }, { t: T_PAY + 0.2, s: 'stamp', g: 0.9 }, { t: T_CHART - 0.4, s: 'rise', g: 0.6 }, { t: T_CHART, s: 'bundle', g: 0.9 });
  e.push({ t: T_CHART + 0.6, s: 'stamp', g: 1.0 }, { t: TD[10] + 0.38, s: 'stamp', g: 0.7 }, { t: TD[20] + 0.4, s: 'stamp', g: 0.7 }, { t: TD[29] + 0.38, s: 'stamp', g: 0.7 });
  e.push({ t: T_CTA, s: 'whoosh', g: 0.9 }, { t: T_CTA, s: 'stamp', g: 1.0 });
  for (let k = 0; k < 4; k++) e.push({ t: T_CTA + 0.35 + k * 0.45, s: 'ping', g: 0.45, pan: k % 2 ? 0.4 : -0.4, rate: k % 2 ? 1.25 : 1.0 });
  return e.map(x => ({ pan: 0, ...x })).sort((a, b) => a.t - b.t);
})();
window.TL = { TD, T_FLIP, T_END, T_CTA, T_SLAM, T_SHAT, T_PAY, DUR };
window.DUR = DUR;
document.fonts.load('700 17px "JetBrains Mono"').then(() => document.fonts.load('800 17px "JetBrains Mono"')).then(() => document.fonts.load('900 56px "Inter Display"')).then(() => document.fonts.load('800 34px "Inter Display"')).then(() => { window.ready = true; });
