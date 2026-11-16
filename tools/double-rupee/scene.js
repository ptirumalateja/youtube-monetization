// ₹1 Crore Today vs ₹1 Doubled for 30 Days - Slow Light dark-warm, wordless.
// Two true-scale stacks of ₹500 notes (0.11 mm each): A = ₹1 crore (2.2 m), B = running total of ₹1 doubled daily (2^d - 1).
// A person (1.7 m) stands between them for scale; from day 24 the camera scale drops and landmarks appear.
// window.renderAt(t, sub) -> JPEG. window.events -> sound cues. window.TL -> timeline.
'use strict';
const DW = 720, DH = 1280, DUR = 21.0;
const qs = new URLSearchParams(location.search);
const W = +(qs.get('w') || 1080), H = +(qs.get('h') || 1920), KK = W / DW;
const cv = document.createElement('canvas'); cv.width = W; cv.height = H; document.body.appendChild(cv);
const out = cv.getContext('2d');
const acc = document.createElement('canvas'); acc.width = W; acc.height = H; const A = acc.getContext('2d');
let T = 0;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, k) => a + (b - a) * k;
const ss = (a, b, x) => { const k = clamp((x - a) / (b - a)); return k * k * (3 - 2 * k); };
const eout = k => 1 - Math.pow(1 - k, 3);
function hash(i) { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }
const rgba = (c, a) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;
const GOLD = [255, 200, 110], HOT = [255, 236, 190], SILVER = [190, 205, 235];
const inr = n => '₹' + Math.round(n).toLocaleString('en-IN');
const crore = n => (n / 1e7).toFixed(n >= 1e8 ? 0 : 1).replace(/\.0$/, '') + ' CRORE';
const lakh = n => (n / 1e5).toFixed(1).replace(/\.0$/, '') + ' LAKH';

// ---------- timeline ----------
const TD = [null];
for (let d = 1; d <= 30; d++) TD.push(d <= 9 ? 1.6 + (d - 1) * 0.33 : d === 10 ? 4.6 : d <= 20 ? 5.6 + (d - 11) * 0.5 : d <= 23 ? 10.6 + (d - 21) * 0.65 : d === 24 ? 12.6 : 13.4 + (d - 25) * 0.75);
const T_FLIP = TD[24], T_END = 17.9, T_CTA = 19.0;
const dayAt = t => { let d = 0; for (let i = 1; i <= 30; i++) if (t >= TD[i]) d = i; return d; };
const val = d => Math.pow(2, d) - 1;
function liveVal(t) { const d = dayAt(t); if (d === 0) return 0; return lerp(val(d - 1), val(d), eout(clamp((t - TD[d]) / 0.15))); }
const CRORE = 1e7, NOTE_M = 0.00011;
const hM = v => v / 500 * NOTE_M; // metres of ₹500 notes
// ---------- scale (px per metre) ----------
const S0 = 230, ROOM = 505;
function scaleAt(t) {
  const d = dayAt(t); const tgt = dd => dd < 24 ? S0 : Math.min(S0, ROOM / hM(val(dd)));
  if (d < 24) return S0;
  const k = eout(clamp((t - TD[d]) / 0.45));
  return Math.exp(lerp(Math.log(tgt(d - 1)), Math.log(tgt(d)), k));
}
const G = 1000; // ground line (design px)
const AX = 210, BX = 490, SW = 128;

// ---------- person (Silence stickman, 1.7 m) ----------
const STAND = { head: [3, -150], sh: [0, -124], hip: [0, -66], kn1: [3, -33], ft1: [6, 0], kn2: [-3, -33], ft2: [-6, 0], el1: [4, -97], hd1: [6, -71], el2: [-4, -97], hd2: [-6, -71] };
const LOOKUP = Object.assign({}, STAND, { head: [8, -152] });
function drawFig(g, pose, x, y, s, alpha = 1, refl = false) {
  const X = p => x + p[0] * s, Y = p => y + p[1] * s * (refl ? -0.5 : 1);
  g.save(); g.globalAlpha = alpha; g.lineCap = 'round'; g.lineJoin = 'round'; const lw = Math.max(1.2, 11.5 * s);
  if (!refl) { g.shadowColor = 'rgba(255,214,160,0.45)'; g.shadowBlur = 10 * s * KK; }
  const seg = (pts, col, w) => { g.strokeStyle = col; g.lineWidth = w; g.beginPath(); g.moveTo(X(pts[0]), Y(pts[0])); for (let i = 1; i < pts.length; i++) g.lineTo(X(pts[i]), Y(pts[i])); g.stroke(); };
  seg([pose.hip, pose.kn2, pose.ft2], '#a59d92', lw); seg([pose.sh, pose.el2, pose.hd2], '#a59d92', lw * 0.92);
  seg([pose.sh, pose.hip], '#fff7ea', lw * 1.05); seg([pose.hip, pose.kn1, pose.ft1], '#fff7ea', lw); seg([pose.sh, pose.el1, pose.hd1], '#fff7ea', lw * 0.92);
  g.fillStyle = '#fff7ea'; g.beginPath(); g.arc(X(pose.head), Y(pose.head), Math.max(1.5, 14.5 * s), 0, 7); g.fill(); g.restore();
}
function glow(g, x, y, r, a, col = GOLD, hot = HOT) { g.save(); g.globalCompositeOperation = 'lighter'; const gr = g.createRadialGradient(x, y, 0, x, y, r);
  gr.addColorStop(0, rgba(hot, 0.85 * a)); gr.addColorStop(0.35, rgba(col, 0.35 * a)); gr.addColorStop(1, rgba(col, 0)); g.fillStyle = gr; g.beginPath(); g.arc(x, y, r, 0, 7); g.fill(); g.restore(); }

// ---------- stacks ----------
function noteStack(g, x, hpx, col, S, a = 1, pop = 0) {
  if (hpx <= 0.3) return;
  const w = SW, x0 = x - w / 2, y0 = G - hpx, dep = 16;
  g.save(); g.globalAlpha = a;
  let gr = g.createLinearGradient(x0, 0, x0 + w, 0); gr.addColorStop(0, rgba(col.map(c => c * 0.55), 1)); gr.addColorStop(0.5, rgba(col.map(c => c * 0.85), 1)); gr.addColorStop(1, rgba(col.map(c => c * 0.4), 1));
  g.fillStyle = gr; g.fillRect(x0, y0, w, hpx);
  // bundles of 100 notes = 1.1 cm; draw straps when bundles are at least 5 px apart, else fine texture
  const bpx = 0.011 * S;
  if (bpx >= 5) { for (let y = G - bpx; y > y0; y -= bpx) { g.fillStyle = 'rgba(30,20,10,0.35)'; g.fillRect(x0, y, w, 1.2); g.fillStyle = 'rgba(255,245,220,0.22)'; g.fillRect(x0 + w * 0.42, y + 1.5, w * 0.16, Math.max(1, bpx - 3)); } }
  else { for (let i = 0; i < hpx; i += 3) { g.fillStyle = `rgba(255,240,210,${0.04 + 0.05 * hash(i)})`; g.fillRect(x0, G - i, w, 1); } }
  // top face
  g.fillStyle = rgba(col.map(c => Math.min(255, c * 1.05)), 1); g.beginPath(); g.moveTo(x0, y0); g.lineTo(x0 + dep, y0 - dep * 0.55); g.lineTo(x0 + w + dep, y0 - dep * 0.55); g.lineTo(x0 + w, y0); g.closePath(); g.fill();
  // side face
  g.fillStyle = rgba(col.map(c => c * 0.3), 1); g.beginPath(); g.moveTo(x0 + w, y0); g.lineTo(x0 + w + dep, y0 - dep * 0.55); g.lineTo(x0 + w + dep, G - dep * 0.55); g.lineTo(x0 + w, G); g.closePath(); g.fill();
  g.fillStyle = 'rgba(255,250,235,0.5)'; g.fillRect(x0, y0, w, 1.5);
  g.restore();
  glow(g, x + 8, y0, 70 + 60 * pop, (0.35 + 0.6 * pop) * a, col, HOT);
}
function coinPile(g, x, v, pop) { // first days: real coins, one per rupee (max 511), piled in a mound
  const n = Math.min(120, Math.round(v)); if (n <= 0) return 0;
  const cols = Math.min(9, Math.ceil(Math.sqrt(n))); let i = 0, top = G;
  g.save();
  for (let row = 0; i < n; row++) { const per = Math.max(1, cols - Math.floor(row / 3)); for (let c = 0; c < per && i < n; c++, i++) {
    const cx = x + (c - (per - 1) / 2) * 13 + (hash(i) - 0.5) * 3, cy = G - 4 - row * 4.2; top = Math.min(top, cy);
    g.fillStyle = '#7a5a26'; g.beginPath(); g.ellipse(cx, cy + 1.5, 7, 2.6, 0, 0, 7); g.fill();
    g.fillStyle = `rgb(${230 + 20 * hash(i + 3)},${185 + 20 * hash(i + 5)},${100})`; g.beginPath(); g.ellipse(cx, cy, 7, 2.6, 0, 0, 7); g.fill(); } }
  g.restore(); glow(g, x, top, 60 + 50 * pop, 0.4 + 0.6 * pop); return G - top;
}
// ---------- landmarks (silhouettes, metres) ----------
const LM = [
  [25, 'house', 6], [26, 'b5', 15], [27, 'b10', 30], [28, 'charminar', 56], [29, 'qutub', 72.5], [30, 'unity', 182],
];
function landmark(g, kind, x, S, a) {
  if (a <= 0) return; g.save(); g.globalAlpha = a; g.fillStyle = '#232634'; g.strokeStyle = 'rgba(190,205,240,0.35)'; g.lineWidth = 1.5;
  const m = v => v * S; const P = (pts) => { g.beginPath(); g.moveTo(x + m(pts[0][0]), G - m(pts[0][1])); for (const p of pts.slice(1)) g.lineTo(x + m(p[0]), G - m(p[1])); g.closePath(); g.fill(); g.stroke(); };
  const win = (x0, y0, w, h, nx, ny) => { for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) if (hash(i * 7 + j * 13 + x0) > 0.45) { g.fillStyle = 'rgba(255,196,120,0.55)'; g.fillRect(x + m(x0 + (i + 0.3) * w / nx), G - m(y0 + (j + 0.7) * h / ny), m(w / nx * 0.4), m(h / ny * 0.4)); } g.fillStyle = '#232634'; };
  if (kind === 'house') { P([[-5, 0], [-5, 4], [0, 6.5], [5, 4], [5, 0]]); win(-4, 0, 8, 4, 3, 1); }
  if (kind === 'b5') { P([[-7, 0], [-7, 15], [7, 15], [7, 0]]); win(-7, 0, 14, 15, 4, 5); }
  if (kind === 'b10') { P([[-9, 0], [-9, 30], [9, 30], [9, 0]]); win(-9, 0, 18, 30, 5, 10); }
  if (kind === 'charminar') { P([[-16, 0], [-16, 34], [16, 34], [16, 0], [7, 0], [7, 18], [0, 24], [-7, 18], [-7, 0]]);
    for (const sx of [-15, 15]) { P([[sx - 2, 0], [sx - 2, 50], [sx, 56], [sx + 2, 50], [sx + 2, 0]]); } }
  if (kind === 'qutub') { P([[-7, 0], [-3.5, 70], [0, 72.5], [3.5, 70], [7, 0]]); g.strokeStyle = 'rgba(190,205,240,0.25)'; for (const h of [20, 38, 52, 62]) { const hw = lerp(7, 3.5, h / 70); g.beginPath(); g.moveTo(x + m(-hw - 1.2), G - m(h)); g.lineTo(x + m(hw + 1.2), G - m(h)); g.stroke(); } }
  if (kind === 'unity') { // pedestal + standing figure, 182 m statue on a 58 m base (base drawn lower)
    P([[-22, 0], [-18, 25], [18, 25], [22, 0]]);
    const b = 25, fs = 182 / 165; const p = (u, v) => [u * fs * 0.9, b + v * fs];
    P([p(-14, 0), p(-16, 60), p(-22, 120), p(-12, 150), p(-6, 158), p(-6, 165), p(6, 165), p(6, 158), p(12, 150), p(20, 120), p(16, 60), p(14, 0)]); }
  g.restore();
}

// ---------- background ----------
function background(g, t) {
  g.setTransform(KK, 0, 0, KK, 0, 0);
  let gr = g.createLinearGradient(0, 0, 0, DH); gr.addColorStop(0, '#2e2836'); gr.addColorStop(0.55, '#221e28'); gr.addColorStop(1, '#1d1a22');
  g.fillStyle = gr; g.fillRect(0, 0, DW, DH);
  // warm spot from above (reaches the top edge so FB sees light, not a border)
  g.save(); g.globalCompositeOperation = 'lighter';
  for (let k = 0; k < 5; k++) { const a = 0.045 - k * 0.007; const g2 = g.createLinearGradient(0, -40, 0, G); g2.addColorStop(0, rgba(GOLD, a * 1.5)); g2.addColorStop(1, rgba(GOLD, a * 0.6));
    g.fillStyle = g2; g.beginPath(); g.moveTo(330 - 30 - k * 8, -40); g.lineTo(390 + 30 + k * 8, -40); g.lineTo(650 + k * 40, G); g.lineTo(70 - k * 40, G); g.closePath(); g.fill(); }
  g.restore();
  for (let i = 0; i < 60; i++) { const x = (hash(i) * DW + t * (4 + 8 * hash(i + 9))) % DW, y = 60 + hash(i + 3) * 1000 - t * (3 + 5 * hash(i + 5));
    g.fillStyle = `rgba(255,236,200,${0.1 + 0.18 * hash(i + 7)})`; g.beginPath(); g.arc(x, y, 0.6 + 1.1 * hash(i + 11), 0, 7); g.fill(); }
  // glossy floor to the bottom edge
  gr = g.createLinearGradient(0, G, 0, DH); gr.addColorStop(0, '#3c3542'); gr.addColorStop(0.25, '#28232d'); gr.addColorStop(1, '#221e27'); g.fillStyle = gr; g.fillRect(0, G, DW, DH - G);
  g.fillStyle = 'rgba(255,236,205,0.4)'; g.fillRect(0, G - 0.5, DW, 1.4);
  for (let i = 1, d = 10; i < 9; i++, d *= 1.45) { g.fillStyle = `rgba(255,240,220,${0.04 - i * 0.004})`; g.fillRect(0, G + d, DW, 1.1); }
  g.save(); g.globalCompositeOperation = 'lighter'; g.translate(360, G + 10); g.scale(1, 0.16); const pg = g.createRadialGradient(0, 0, 0, 0, 0, 380); pg.addColorStop(0, rgba(GOLD, 0.22)); pg.addColorStop(1, rgba(GOLD, 0)); g.fillStyle = pg; g.beginPath(); g.arc(0, 0, 380, 0, 7); g.fill(); g.restore();
}

// ---------- HUD ----------
function fitFont(g, txt, weight, size, family, maxW) { g.font = `${weight} ${size}px "${family}"`; const w = g.measureText(txt).width; if (w > maxW) { size *= maxW / w; g.font = `${weight} ${size}px "${family}"`; } return size; }
function title(g, a, b, k, pop, big = false, gold2 = false) {
  if (k <= 0) return; g.setTransform(KK, 0, 0, KK, 0, 0); g.save(); g.globalAlpha *= k; g.textAlign = 'center';
  g.translate(360, 250); g.scale(pop, pop); g.translate(-360, -250);
  const fa = big ? 58 : 48, fb = big ? 42 : 36;
  g.font = `900 ${fa}px "Inter Display"`; let wa = Math.min(560, g.measureText(a).width); g.font = `800 ${fb}px "Inter Display"`; const wb = b ? Math.min(560, g.measureText(b).width) : 0;
  const w = Math.max(wa, wb) + 64, h = b ? (big ? 126 : 110) : 76;
  g.save(); g.fillStyle = 'rgba(12,13,18,0.6)'; g.shadowColor = 'rgba(0,0,0,0.45)'; g.shadowBlur = 16; g.beginPath(); g.roundRect(360 - w / 2, 204, w, h, 18); g.fill(); g.restore();
  g.shadowColor = 'rgba(0,0,0,0.6)'; g.shadowBlur = 10;
  fitFont(g, a, 900, fa, 'Inter Display', 560); g.fillStyle = 'rgb(255,200,110)'; g.fillText(a, 360, 204 + fa + 4);
  if (b) { fitFont(g, b, 800, fb, 'Inter Display', 560); g.fillStyle = gold2 ? 'rgb(255,200,110)' : 'rgba(250,246,238,0.98)'; g.fillText(b, 360, 204 + h - 20); }
  g.restore();
}
function card(g, x, y, w, label, value, lead, leadK, col) {
  g.save(); g.fillStyle = 'rgba(12,13,18,0.68)'; g.strokeStyle = lead ? rgba(GOLD, 0.95) : 'rgba(200,210,235,0.25)'; g.lineWidth = lead ? 3 : 1.5;
  if (lead) { g.shadowColor = rgba(GOLD, 0.6); g.shadowBlur = 16 * KK * leadK; }
  g.beginPath(); g.roundRect(x, y, w, 92, 16); g.fill(); g.stroke(); g.shadowBlur = 0;
  g.font = '700 17px "JetBrains Mono"'; g.letterSpacing = '2px'; g.textAlign = 'left'; g.fillStyle = rgba(col, 0.9); g.fillText(label, x + 16, y + 28);
  g.letterSpacing = '0px'; fitFont(g, value, 900, 34, 'Inter Display', w - 30); g.fillStyle = 'rgba(250,246,238,1)'; g.fillText(value, x + 16, y + 72);
  if (lead) { const cw = 104; g.fillStyle = rgb(GOLD); g.beginPath(); g.roundRect(x + w - cw - 14, y - 14, cw, 28, 14); g.fill(); g.font = '900 15px "Inter Display"'; g.letterSpacing = '1px'; g.fillStyle = '#16120c'; g.textAlign = 'center'; g.fillText('WINNING', x + w - cw / 2 - 14, y + 5.5); }
  g.restore();
}
const rgb = c => `rgb(${c[0]},${c[1]},${c[2]})`;

function frame(g, t) {
  T = t;
  const d = dayAt(t), v = liveVal(t), S = scaleAt(t), pop = d > 0 ? Math.exp(-(t - TD[d]) * 7) : 0;
  // camera: slight push + shake on the flip / landmark days
  let shake = 0; if (d >= 24 && t - TD[d] < 0.3) shake = (d === 24 ? 6 : 3.5) * Math.sin(t * 80) * (1 - (t - TD[d]) / 0.3);
  const z = 1 + 0.03 * Math.sin(t * 0.4) + (t < 1.6 ? 0.06 * (1 - t / 1.6) : 0);
  background(g, t);
  g.setTransform(KK * z, 0, 0, KK * z, KK * (360 - 360 * z + shake), KK * (G - G * z));
  // landmarks (behind)
  for (const [day, kind, hm] of LM) { if (d < day) continue; const a = day === d ? ss(TD[day], TD[day] + 0.25, t) : (day === d - 1 ? 0.45 : 0.18) * (day >= 28 || d < 30 ? 1 : 0.5);
    landmark(g, kind, 620, S, d >= 30 && day < 28 ? 0 : a); }
  // A: ₹1 crore (drops in at frame 0)
  const drop = 0;
  g.save(); g.translate(0, -drop); noteStack(g, AX, hM(CRORE) * S, SILVER, S, 1, t < 0.5 ? Math.exp(-t * 6) : 0); g.restore();
  // B: running total
  let bTop;
  if (v < 512) bTop = coinPile(g, BX, v, pop);
  else { const hp = Math.max(hM(v) * S, 5 * Math.log2(v + 1)); noteStack(g, BX, hp, GOLD, S, 1, pop); bTop = hp; }
  if (d === 0 && t > 0.25) { const k = eout(clamp((t - 0.25) / 0.2)); coinPile(g, BX, k >= 1 ? 1 : 0, 0); if (k < 1) { g.fillStyle = 'rgb(240,200,100)'; g.beginPath(); g.ellipse(BX, lerp(560, G - 4, k), 7, 2.6, 0, 0, 7); g.fill(); } }
  // height tag on B (true metres) from day 20
  if (d >= 21) { const hm = hM(v); const txt = hm < 1 ? Math.round(hm * 100) + ' cm' : hm < 10 ? hm.toFixed(1) + ' m' : Math.round(hm) + ' m';
    g.save(); g.font = '700 18px "JetBrains Mono"'; g.textAlign = 'left'; g.fillStyle = 'rgba(255,214,150,0.95)'; g.fillText(txt, BX + SW / 2 + 22, G - bTop + 6); g.restore(); }
  // person, 1.7 m, between the stacks, looks up as B grows
  const ps = 1.7 * S / 165, pose = d >= 21 ? LOOKUP : STAND;
  drawFig(g, pose, 352, G + 6, ps, 0.16, true); drawFig(g, pose, 352, G, ps);
  // reflections of the stacks
  g.save(); g.globalAlpha = 0.12; g.translate(0, 2 * G); g.scale(1, -0.35); g.translate(0, -G * (1 / 0.35 - 1) * 0); g.restore();
  // ---- HUD (screen space) ----
  g.setTransform(KK, 0, 0, KK, 0, 0);
  // vignette + grain
  { const gr = g.createRadialGradient(360, 640, 300, 360, 640, 900); gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(1, 'rgba(0,0,0,0.12)'); g.fillStyle = gr; g.fillRect(0, 0, DW, DH); }
  if (d === 24 && t - TD[24] < 0.14) { g.fillStyle = `rgba(255,236,200,${0.45 * (1 - (t - TD[24]) / 0.14)})`; g.fillRect(0, 0, DW, DH); }
  const bLead = v > CRORE;
  card(g, 64, 350, 288, 'TODAY', '₹1 CRORE', !bLead, 1, SILVER);
  card(g, 368, 350, 288, d ? `DOUBLED · DAY ${d}` : 'DOUBLED · 30 DAYS', inr(Math.max(v, 1)), bLead, 1 + pop, GOLD);
  // titles
  const tp = t0 => 1 + 0.14 * Math.exp(-Math.max(0, t - t0) * 9);
  if (t < 1.6) title(g, 'WHICH ONE', 'DO YOU TAKE?', 1, tp(0), true);
  else if (t < 4.6) title(g, '₹1, DOUBLED', 'EVERY DAY FOR 30 DAYS', 1, tp(1.6));
  else if (t < 5.6) title(g, 'DAY 10: ₹1,023.', 'LOOKS STUPID, RIGHT?', 1, tp(4.6));
  else if (t < TD[20]) title(g, 'STILL LOSING.', 'BEHIND BY ' + inr(CRORE - v), 1, tp(5.6));
  else if (t < TD[21]) title(g, 'DAY 20: ₹10 LAKH.', 'STILL WAY BEHIND.', 1, tp(TD[20]));
  else if (t < T_FLIP) title(g, "IT'S CATCHING UP…", 'BEHIND BY ' + inr(Math.max(0, CRORE - v)), 1, tp(TD[21]));
  else if (t < TD[25]) title(g, 'DAY 24.', 'IT WINS.', 1, tp(T_FLIP), true, true);
  else if (t < T_END) { const lines = { 25: 'TALLER THAN A HOUSE.', 26: '5 FLOORS HIGH.', 27: '10 FLOORS HIGH.', 28: 'PAST CHARMINAR.', 29: 'PAST QUTUB MINAR.', 30: 'PAST THE STATUE OF UNITY.' };
    title(g, lines[d], '₹' + crore(v), 1, tp(TD[d]), false, false); }
  else title(g, 'SLOW FOR 23 DAYS.', 'UNSTOPPABLE AFTER.', ss(T_END, T_END + 0.12, t), tp(T_END), true, true);
  const ca = ss(T_CTA, T_CTA + 0.3, t);
  if (ca > 0) { g.save(); g.globalAlpha = ca; g.fillStyle = 'rgba(12,13,18,0.7)'; g.beginPath(); g.roundRect(100, 1040, 520, 96, 20); g.fill();
    g.font = '800 34px "Inter"'; g.textAlign = 'center'; g.fillStyle = 'rgba(250,246,238,0.98)'; g.fillText('Which one did you pick?', 360, 1080); g.fillText('Be honest 👇', 360, 1120); g.restore(); }
  g.save(); g.font = '600 11px "JetBrains Mono"'; g.letterSpacing = '5px'; g.textAlign = 'center'; g.fillStyle = 'rgba(242,238,230,0.28)'; g.fillText('SLOW LIGHT', 360, 1270); g.restore();
  // grain
  if (!window._grain) { window._grain = []; for (let n = 0; n < 4; n++) { const c = document.createElement('canvas'); c.width = c.height = 256; const x = c.getContext('2d'); const im = x.createImageData(256, 256);
    for (let p = 0; p < im.data.length; p += 4) { const q = Math.random() * 255; im.data[p] = im.data[p + 1] = im.data[p + 2] = q; im.data[p + 3] = 255; } x.putImageData(im, 0, 0); window._grain.push(c); } }
  g.save(); g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 0.05; g.globalCompositeOperation = 'overlay'; g.fillStyle = g.createPattern(window._grain[Math.floor(t * 30) % 4], 'repeat'); g.fillRect(0, 0, W, H); g.restore();
}

window.renderAt = (t, sub = 1) => {
  sub = Math.max(1, sub | 0);
  if (sub === 1) frame(out, t);
  else { out.setTransform(1, 0, 0, 1, 0, 0); out.fillStyle = '#000'; out.fillRect(0, 0, W, H);
    for (let i = 0; i < sub; i++) { A.setTransform(1, 0, 0, 1, 0, 0); frame(A, Math.max(0, t + (i / sub - 0.5) / 60)); out.setTransform(1, 0, 0, 1, 0, 0); out.globalCompositeOperation = 'lighter'; out.globalAlpha = 1 / sub; out.drawImage(acc, 0, 0); }
    out.globalCompositeOperation = 'source-over'; out.globalAlpha = 1; }
  return cv.toDataURL('image/jpeg', 0.95);
};
window.events = (() => {
  const e = [{ t: 0.02, s: 'cash', g: 1.0, pan: -0.3 }, { t: 0.42, s: 'coin', g: 0.9, pan: 0.3 }];
  for (let d = 1; d <= 30; d++) {
    if (d <= 9) e.push({ t: TD[d], s: 'coin', g: 0.8, pan: 0.3, rate: 1 + d * 0.06 });
    else if (d <= 23) { e.push({ t: TD[d], s: 'bundle', g: lerp(0.6, 1.0, (d - 10) / 13), pan: 0.3, rate: lerp(1.1, 0.85, (d - 10) / 13) }); if (d % 3 === 0) e.push({ t: TD[d] + 0.05, s: 'riffle', g: 0.4, pan: 0.35 }); }
    else if (d === 24) e.push({ t: TD[d], s: 'boom', g: 1.0, pan: 0 }, { t: TD[d], s: 'cash', g: 0.9, pan: 0.2 });
    else e.push({ t: TD[d] - 0.55, s: 'rise', g: 0.45, pan: 0 }, { t: TD[d], s: 'boom', g: lerp(0.6, 1.0, (d - 25) / 5), pan: 0, rate: lerp(1.1, 0.8, (d - 25) / 5) });
  }
  e.push({ t: TD[21] - 0.1, s: 'heart', g: 0.8, pan: 0 });
  return e.sort((a, b) => a.t - b.t);
})();
window.TL = { TD, T_FLIP, T_END, T_CTA, DUR };
window.DUR = DUR;
document.fonts.load('700 17px "JetBrains Mono"').then(() => document.fonts.load('900 56px "Inter Display"')).then(() => document.fonts.load('800 34px "Inter"')).then(() => { window.ready = true; });
