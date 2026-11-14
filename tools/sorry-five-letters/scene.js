// Sorry Is 5 Letters - Slow Light stickman reel in the Silence Is Distance (v8) look.
// Two people stand back to back after a fight. The unsaid word SORRY hangs over them as five gold blocks
// that get heavier every day, until he finally types it and the giant letters shrink into one small message.
// Canvas 2D, design space 720x1280 scaled to the render size (same as tools/silence-distance).
// window.renderAt(t, sub) -> JPEG data URL. window.events -> sound cue list (mix.py).
'use strict';
const DW = 720, DH = 1280, DUR = 13.6;
const qs = new URLSearchParams(location.search);
const W = +(qs.get('w') || 1080), H = +(qs.get('h') || 1920);
const cv = document.createElement('canvas'); cv.width = W; cv.height = H; document.body.appendChild(cv);
const out = cv.getContext('2d');
const acc = document.createElement('canvas'); acc.width = W; acc.height = H;
const A = acc.getContext('2d');

// ---------- helpers ----------
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, k) => a + (b - a) * k;
const ss = (a, b, x) => { const k = clamp((x - a) / (b - a)); return k * k * (3 - 2 * k); };
const eio = k => k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
const eout = k => 1 - Math.pow(1 - k, 3);
const pw = (t, keys) => {
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) if (t <= keys[i][0]) { const [t0, v0] = keys[i - 1], [t1, v1] = keys[i]; return lerp(v0, v1, (t - t0) / (t1 - t0)); }
  return keys[keys.length - 1][1];
};
function hash(i) { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }
const mixC = (a, b, k) => a.map((v, i) => Math.round(lerp(v, b[i], k)));
const rgb = c => `rgb(${c[0]},${c[1]},${c[2]})`;
const rgba = (c, a) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;

// ---------- palette (Slow Light, as Silence Is Distance) ----------
const C = {
  bgTop: '#33333d', bgMid: '#22232c', bgBot: '#2a2b34',
  gold: [255, 190, 92], goldHot: [255, 232, 180],
  figWarm: [255, 247, 234], farWarm: [165, 157, 146],
  figCool: [223, 228, 238], farCool: [138, 144, 156],
};

// ---------- timeline (output seconds) ----------
// 0.00 frame 0 = DAY 30, the word crushing them. 0.25 SLAM (hit). 1.35-1.75 rewind to DAY 1.
// 1.75-7.6 each day the word drops a notch (thuds), they type sorry and delete it.
// 8.3 he lifts his phone; 8.75-9.45 the giant letters fly into his message; 9.55 sent; 10.0 she gets it.
// 9.5-10.1 they stand; 10.2-10.65 they turn around; 10.7 hold hands; 10.3+ end line; 11.0+ CTA.
const THUDS = [[0.25, 1.0, 30], [3.35, 0.2, 2], [4.95, 0.42, 5], [5.85, 0.6, 9], [6.7, 0.8, 16], [7.55, 1.0, 30]];
const REW0 = 1.35, REW1 = 1.75, FLY0 = 8.75, FLY_ST = 0.14, FLY_D = 0.42, SEND = 9.55;
function heavy(t) { // letter weight 0..1
  if (t < REW0) return lerp(0.9, 1.0, clamp((t - 0.15) / 0.1) ** 2);
  if (t < REW1) return 1 - eio((t - REW0) / (REW1 - REW0));
  let h = 0;
  for (const [tt, v] of THUDS.slice(1)) if (t >= tt - 0.1) h = lerp(h, v, clamp((t - tt + 0.1) / 0.1) ** 2); // accelerating fall, impact at tt
  return h;
}
function dayAt(t) {
  if (t < REW0) return 30;
  if (t < REW1) return Math.max(1, Math.round(30 - 29 * eio((t - REW0) / (REW1 - REW0))));
  let d = 1; for (const [tt, , dd] of THUDS.slice(1)) if (t >= tt) d = dd; return d;
}
// how bowed the bodies are (follows the letters, then lifts as the letters leave)
// impact impulse: knees buckle past the pose, then settle
const impK = (t, tt) => { const k = t - tt; return k > 0 ? Math.exp(-k * 9) * (1 - Math.exp(-k * 60)) : 0; };
const impulse = t => t < REW0 ? impK(t, 0.25) : t < REW1 ? 0 : THUDS.slice(1).reduce((m, [tt, v]) => m + v * impK(t, tt), 0);
const bodyHeavy = t => t < FLY0 ? heavy(t) + 0.16 * impulse(t) : 1 - ss(FLY0 + 0.3, SEND + 0.45, t);
// letters: lift before the slam (anticipation), then a small bounce after it
function dropY(t) {
  if (t < REW0) { const up = ss(0.03, 0.15, t) * (1 - clamp((t - 0.15) / 0.1) ** 2); return -38 * up + bounce(t, 0.25, 1); }
  if (t < REW1) return 0;
  let y = 0; for (const [tt, v] of THUDS.slice(1)) { y += -26 * v * ss(tt - 0.3, tt - 0.12, t) * (1 - clamp((t - tt + 0.1) / 0.1) ** 2) * (t < tt + 0.05 ? 1 : 0); y += bounce(t, tt, v); }
  return y;
}
function bounce(t, tt, v) { const k = t - tt; return k > 0 && k < 0.6 ? -9 * v * Math.exp(-k * 10) * Math.abs(Math.sin(k * 22)) : 0; }
// squash on impact
function squash(t) { if (t < REW0) { const k = t - 0.25; return k > 0 ? 0.14 * Math.exp(-k * 14) : 0; } if (t < REW1) return 0; return THUDS.slice(1).reduce((m, [tt, v]) => { const k = t - tt; return m + (k > 0 ? 0.13 * v * Math.exp(-k * 14) : 0); }, 0); }
const hitList = t => t < REW0 ? [[0.25, 1.25]] : t < REW1 ? [] : THUDS.slice(1);
function shakeAt(t) {
  let s = 0; for (const [tt, v] of THUDS) { const k = t - tt; if (k > 0 && k < 0.6) s += (tt < 1 ? 17 : 3 + 13 * v) * Math.exp(-k * 8) * Math.sin(k * 75); }
  return s;
}

// ---------- poses (local px, facing +x, ground y = 0) ----------
const K = ['head', 'sh', 'hip', 'kn1', 'ft1', 'kn2', 'ft2', 'el1', 'hd1', 'el2', 'hd2'];
const STAND = { head: [0, -161], sh: [0, -137], hip: [0, -81], kn1: [2, -42], ft1: [3, -6], kn2: [-2, -42], ft2: [-3, -6], el1: [4, -109], hd1: [6, -83], el2: [-4, -109], hd2: [-6, -83] };
const SAG = { head: [7, -150], sh: [2, -128], hip: [-2, -77], kn1: [5, -40], ft1: [4, -6], kn2: [1, -40], ft2: [-2, -6], el1: [7, -101], hd1: [9, -76], el2: [2, -101], hd2: [3, -76] };
const BOW = { head: [17, -112], sh: [6, -93], hip: [-13, -50], kn1: [17, -44], ft1: [11, -6], kn2: [13, -43], ft2: [6, -6], el1: [20, -66], hd1: [23, -46], el2: [16, -66], hd2: [19, -45] };
const HOLD = { head: [1, -161], sh: [0, -137], hip: [0, -81], kn1: [2, -42], ft1: [3, -6], kn2: [-2, -42], ft2: [-3, -6], el1: [14, -113], hd1: [27, -97], el2: [11, -111], hd2: [25, -95] };
// phone arms (hands in front of the chest / face), per body state
const ARM_STAND = { el1: [9, -108], hd1: [21, -119], el2: [5, -108], hd2: [18, -118] };
const ARM_SAG = { el1: [11, -100], hd1: [22, -109], el2: [7, -100], hd2: [19, -108] };
const ARM_BOW = { el1: [24, -70], hd1: [33, -86], el2: [20, -70], hd2: [30, -85] };
function mix(a, b, k) { const o = {}; for (const n of K) o[n] = [lerp(a[n][0], b[n][0], k), lerp(a[n][1], b[n][1], k)]; return o; }
function bodyPose(h, phone) {
  let p = h < 0.5 ? mix(STAND, SAG, eio(h / 0.5)) : mix(SAG, BOW, eio((h - 0.5) / 0.5));
  if (phone > 0) {
    const arm = h < 0.5 ? mix(Object.assign({}, STAND, ARM_STAND), Object.assign({}, SAG, ARM_SAG), h / 0.5) : mix(Object.assign({}, SAG, ARM_SAG), Object.assign({}, BOW, ARM_BOW), (h - 0.5) / 0.5);
    for (const n of ['el1', 'hd1', 'el2', 'hd2']) p[n] = [lerp(p[n][0], arm[n][0], phone), lerp(p[n][1], arm[n][1], phone)];
  }
  return p;
}

// ---------- figure ----------
let T = 0;
function drawFig(g, pose, o) {
  // o: x, y (ground), dir (-1..1), s, wk (0 cool..1 warm), pony, phone (0..1 glow), alpha, reflect
  const s = o.s, d = o.dir;
  { const b = Math.sin(T * 2.4 + o.x * 0.05) * 1.3 * (1 - 0.7 * (o.still || 0)), ty = Math.sin(T * 14 + o.x) * 0.8; pose = Object.assign({}, pose);
    for (const n of ['head', 'sh']) pose[n] = [pose[n][0], pose[n][1] + b];
    for (const n of ['el1', 'el2']) pose[n] = [pose[n][0], pose[n][1] + b * 0.6];
    for (const n of ['hd1', 'hd2']) pose[n] = [pose[n][0], pose[n][1] + b * 0.5 + (o.typing ? ty : 0)]; }
  const X = p => o.x + p[0] * d * s, Y = p => o.y + p[1] * s * (o.reflect ? -0.55 : 1);
  const near = rgb(mixC(C.figCool, C.figWarm, o.wk)), far = rgb(mixC(C.farCool, C.farWarm, o.wk));
  g.save(); g.globalAlpha = o.alpha ?? 1; g.lineCap = 'round'; g.lineJoin = 'round';
  const lw = 11.5 * s;
  const seg = (pts, col, w) => { g.strokeStyle = col; g.lineWidth = w; g.beginPath(); g.moveTo(X(pts[0]), Y(pts[0])); for (let i = 1; i < pts.length; i++) g.lineTo(X(pts[i]), Y(pts[i])); g.stroke(); };
  if (!o.reflect) { g.shadowColor = rgba(mixC([190, 210, 255], [255, 214, 160], o.wk), 0.35 + 0.07 * o.wk); g.shadowBlur = 9 * s * (W / DW); }
  seg([pose.hip, pose.kn2, pose.ft2], far, lw);
  seg([pose.sh, pose.el2, pose.hd2], far, lw * 0.92);
  seg([pose.sh, pose.hip], near, lw * 1.05);
  seg([pose.hip, pose.kn1, pose.ft1], near, lw);
  if (o.phone > 0 && !o.reflect) {
    const hx = (X(pose.hd1) + X(pose.hd2)) / 2, hy = (Y(pose.hd1) + Y(pose.hd2)) / 2;
    g.save(); g.shadowBlur = 0; g.translate(hx, hy); g.rotate(-0.5 * Math.sign(d || 1));
    g.fillStyle = '#2a2a30'; g.beginPath(); g.roundRect(-5 * s, -8 * s, 10 * s, 16 * s, 2.5 * s); g.fill();
    g.fillStyle = rgba(C.goldHot, 0.35 + 0.65 * o.phone); g.beginPath(); g.roundRect(-3.6 * s, -6.6 * s, 7.2 * s, 13.2 * s, 1.5 * s); g.fill();
    g.restore();
  }
  seg([pose.sh, pose.el1, pose.hd1], near, lw * 0.92);
  g.fillStyle = near; g.beginPath(); g.arc(X(pose.head), Y(pose.head), 14.5 * s, 0, 7); g.fill();
  if (o.pony) {
    const hx = X(pose.head), hy = Y(pose.head), dd = Math.sign(d || 1) * Math.max(0.35, Math.abs(d)); g.shadowBlur = 0;
    g.strokeStyle = near; g.lineWidth = 5 * s; g.beginPath();
    g.moveTo(hx - 9 * dd * s, hy - 11 * s); g.quadraticCurveTo(hx - 21 * dd * s, hy - 15 * s, hx - 19 * dd * s, hy + 4 * s); g.stroke();
    g.fillStyle = near; g.beginPath(); g.ellipse(hx - 11 * dd * s, hy - 12 * s, 4 * s, 3 * s, 0, 0, 7); g.fill();
  }
  if (o.phone > 0 && !o.reflect) {
    const hx = (X(pose.hd1) + X(pose.hd2)) / 2, hy = (Y(pose.hd1) + Y(pose.hd2)) / 2;
    g.shadowBlur = 0; g.globalCompositeOperation = 'lighter';
    const r = 48 * s; const gr = g.createRadialGradient(hx, hy - 6 * s, 0, hx, hy - 6 * s, r);
    gr.addColorStop(0, rgba(C.gold, 0.30 * o.phone)); gr.addColorStop(1, rgba(C.gold, 0));
    g.fillStyle = gr; g.beginPath(); g.arc(hx, hy - 6 * s, r, 0, 7); g.fill();
  }
  g.restore();
}
const phonePos = (pose, o) => [o.x + (pose.hd1[0] + pose.hd2[0]) / 2 * o.dir * o.s, o.y + (pose.hd1[1] + pose.hd2[1]) / 2 * o.s];

// ---------- set ----------
const GY = 870, FS = 2.4, HIM_X = 297, HER_X = 423;
function background(g, t) {
  let gr = g.createLinearGradient(0, 0, 0, DH);
  gr.addColorStop(0, C.bgTop); gr.addColorStop(0.5, C.bgMid); gr.addColorStop(1, C.bgBot);
  g.fillStyle = gr; g.fillRect(0, 0, DW, DH);
  gr = g.createRadialGradient(360, 560, 10, 360, 560, 520); gr.addColorStop(0, 'rgba(255,190,110,0.10)'); gr.addColorStop(1, 'rgba(255,190,110,0)');
  g.fillStyle = gr; g.fillRect(0, 0, DW, DH);
  gr = g.createRadialGradient(360, 980, 10, 360, 980, 420); gr.addColorStop(0, 'rgba(120,150,210,0.07)'); gr.addColorStop(1, 'rgba(120,150,210,0)');
  g.fillStyle = gr; g.fillRect(0, 0, DW, DH);
  gr = g.createLinearGradient(0, 0, DW, DH * 0.6);
  gr.addColorStop(0.25, 'rgba(255,255,255,0)'); gr.addColorStop(0.42, 'rgba(255,255,255,0.025)'); gr.addColorStop(0.6, 'rgba(255,255,255,0)');
  g.fillStyle = gr; g.fillRect(0, 0, DW, DH);
  // soft light pools reaching the very edges (top and bottom) so no edge band is flat
  for (const [x, y, r, c, a] of [[90, 40, 380, '255,200,140', 0.24], [640, 90, 360, '170,190,240', 0.2], [360, -40, 420, '255,215,170', 0.12], [120, 1250, 420, '255,205,150', 0.24], [620, 1210, 400, '160,180,230', 0.2], [360, 1320, 460, '255,220,180', 0.06]]) {
    const gp = g.createRadialGradient(x, y, 0, x, y, r); gp.addColorStop(0, `rgba(${c},${a})`); gp.addColorStop(1, `rgba(${c},0)`); g.fillStyle = gp; g.fillRect(0, 0, DW, DH);
  }
  for (let i = 0; i < 46; i++) {
    const x = (hash(i) * DW + t * (4 + 8 * hash(i + 9))) % DW, y = ((hash(i + 3) * 1280 - t * (3 + 5 * hash(i + 5))) % 1280 + 1280) % 1280;
    const a = 0.10 + 0.18 * hash(i + 7) * (0.6 + 0.4 * Math.sin(t * 1.3 + i));
    g.fillStyle = `rgba(255,240,215,${a})`; g.beginPath(); g.arc(x, y, 0.6 + 1.1 * hash(i + 11), 0, 7); g.fill();
  }
}
const LTOP = 32, LFRONT = 36, LDEPTH = 420;
function ledge(g, crack) {
  const y0 = GY, tone = [60, 59, 64];
  let gr = g.createLinearGradient(0, y0 - LTOP, 0, y0 + LFRONT);
  gr.addColorStop(0, `rgb(${tone[0] + 26},${tone[1] + 26},${tone[2] + 28})`);
  gr.addColorStop(0.45, `rgb(${tone[0]},${tone[1]},${tone[2]})`);
  gr.addColorStop(1, `rgb(${tone[0] - 22},${tone[1] - 22},${tone[2] - 20})`);
  g.fillStyle = gr; g.fillRect(-60, y0 - LTOP, DW + 120, LTOP + LFRONT);
  gr = g.createLinearGradient(0, y0 + LFRONT, 0, y0 + LFRONT + LDEPTH);
  gr.addColorStop(0, `rgba(${tone[0] - 30},${tone[1] - 30},${tone[2] - 26},1)`); gr.addColorStop(0.45, 'rgba(52,53,62,1)'); gr.addColorStop(1, 'rgba(66,66,76,1)');
  g.fillStyle = gr; g.fillRect(-60, y0 + LFRONT, DW + 120, LDEPTH);
  // glossy floor: warm reflection under them + soft pools out to the frame edges (no flat bottom band)
  for (const [x, y, r, c, al] of [[360, y0 + 120, 330, '255,205,150', 0.16], [70, y0 + 420, 380, '255,200,145', 0.2], [660, y0 + 380, 360, '165,185,235', 0.18], [360, y0 + 470, 300, '230,215,200', 0.08]]) {
    const gp = g.createRadialGradient(x, y, 0, x, y, r); gp.addColorStop(0, `rgba(${c},${al})`); gp.addColorStop(1, `rgba(${c},0)`);
    g.fillStyle = gp; g.fillRect(-60, y0 + LFRONT, DW + 120, LDEPTH);
  }
  g.fillStyle = 'rgba(255,236,205,0.5)'; g.fillRect(-60, y0 + LFRONT - 1.8, DW + 120, 2.2);
  g.fillStyle = 'rgba(255,255,255,0.10)'; g.fillRect(-60, y0 - LTOP, DW + 120, 1.6);
  // cracks under their feet, growing with the weight
  if (crack > 0.01) {
    g.save(); g.lineCap = 'round'; g.lineJoin = 'round';
    for (let c = 0; c < 7; c++) {
      const sx = lerp(250, 470, hash(c * 3.1)), dir = hash(c * 5.7) < 0.5 ? -1 : 1; let x = sx, y = y0 - 6;
      const len = Math.round(9 * crack * (0.6 + 0.4 * hash(c * 2.3)));
      g.beginPath(); g.moveTo(x, y);
      for (let i = 0; i < len; i++) { x += dir * (6 + 9 * hash(c * 13 + i)) ; y += (hash(c * 7 + i * 1.7) - 0.25) * 9; y = Math.min(y, y0 + LFRONT + 40); g.lineTo(x, y); }
      g.strokeStyle = 'rgba(8,8,12,0.85)'; g.lineWidth = 2.2; g.stroke();
      g.strokeStyle = 'rgba(255,214,160,0.12)'; g.lineWidth = 0.8; g.translate(0, 1.4); g.stroke(); g.translate(0, -1.4);
    }
    g.restore();
  }
}

// ---------- the word ----------
const WORD = 'SORRY';
const blockSize = h => lerp(48, 100, h);
function wordLayout(t, h, restY) { // returns 5 slots {x, y (top), b}
  const b = blockSize(h), gap = 0.1 * b, total = 5 * b + 4 * gap;
  const sT = GY - 176 * FS, floatBottom = pw(h, [[0, sT - 30], [0.45, sT + 8], [1, sT + 260]]);
  const bob = (1 - ss(0.2, 0.45, h)) * Math.sin(t * 2.2) * 4;
  const bottom = Math.min(floatBottom + bob, restY) + dropY(t);
  return [...WORD].map((ch, i) => ({ ch, x: 360 - total / 2 + i * (b + gap), y: bottom - b, b, i }));
}
function letterBlock(g, x, y, b, ch, h, flash, alpha = 1, glyphOnly = 0) {
  // h: 0 light glowing gold .. 1 heavy dark bronze
  g.save(); g.globalAlpha *= alpha;
  const top = mixC([255, 216, 146], [138, 104, 62], h), mid = mixC([242, 168, 62], [96, 70, 40], h), bot = mixC([168, 98, 26], [44, 31, 20], h);
  if (glyphOnly < 1) {
    g.save(); g.globalAlpha *= 1 - glyphOnly;
    const gr = g.createLinearGradient(0, y, 0, y + b); gr.addColorStop(0, rgb(top)); gr.addColorStop(0.45, rgb(mid)); gr.addColorStop(1, rgb(bot));
    g.shadowColor = rgba(C.gold, 0.85 * (1 - 0.8 * h)); g.shadowBlur = (8 + 22 * (1 - h) + 18 * flash) * W / DW * (b / 80);
    g.fillStyle = gr; g.beginPath(); g.roundRect(x, y, b, b, b * 0.1); g.fill();
    g.shadowBlur = 0;
    // glossy top highlight + darker lower edge (weight)
    g.fillStyle = `rgba(255,250,235,${0.5 - 0.3 * h})`; g.fillRect(x + b * 0.07, y + b * 0.05, b * 0.86, Math.max(1.5, b * 0.035));
    g.fillStyle = `rgba(0,0,0,${0.15 + 0.3 * h})`; g.fillRect(x + b * 0.04, y + b * 0.9, b * 0.92, b * 0.08);
    // chips/scratches when heavy
    if (h > 0.5) { g.strokeStyle = `rgba(20,14,8,${(h - 0.5) * 0.9})`; g.lineWidth = Math.max(1, b * 0.015); for (let k = 0; k < 3; k++) { const a = hash(ch.charCodeAt(0) + k * 9 + x * 0.01); g.beginPath(); g.moveTo(x + b * (0.15 + 0.7 * a), y + b * 0.08); g.lineTo(x + b * (0.1 + 0.8 * hash(a * 91)), y + b * (0.2 + 0.2 * a)); g.stroke(); } }
    if (flash > 0.02) { g.globalCompositeOperation = 'lighter'; g.fillStyle = rgba(C.goldHot, 0.55 * flash); g.beginPath(); g.roundRect(x, y, b, b, b * 0.1); g.fill(); g.globalCompositeOperation = 'source-over'; }
    g.restore();
  }
  // the letter: engraved dark on gold, becomes bubble text color when glyphOnly
  g.font = `900 ${b * 0.72}px "Inter Display"`; g.textAlign = 'center'; g.textBaseline = 'middle';
  if (glyphOnly < 1) { g.fillStyle = `rgba(255,240,210,${(0.35 - 0.2 * h) * (1 - glyphOnly)})`; g.fillText(ch, x + b / 2, y + b * 0.54 + Math.max(1, b * 0.02)); }
  g.fillStyle = h > 0.5 ? `rgb(${Math.round(lerp(35, 22, h))},${Math.round(lerp(29, 16, h))},${Math.round(lerp(21, 10, h))})` : '#231d15';
  g.fillText(ch, x + b / 2, y + b * 0.52);
  g.restore();
}

// ---------- chat bubbles ----------
function bubble(g, x, y, txt, style, align, a, k, size) {
  // style 'draft' grey / 'gold' sent; align 'r' = bubble ends at x, 'l' = starts at x. returns layout
  g.save(); g.globalAlpha *= a; g.font = `600 ${size}px "Inter"`;
  const tw = g.measureText(txt).width, w = Math.max(tw + size * 1.4, size * 2.2), h = size * 1.85;
  const x0 = align === 'r' ? x - w : x; const ax = align === 'r' ? x : x;
  g.translate(ax, y); g.scale(0.7 + 0.3 * eout(k), 0.7 + 0.3 * eout(k)); g.translate(-ax, 0);
  g.shadowColor = style === 'gold' ? 'rgba(255,190,92,0.55)' : 'rgba(0,0,0,0.4)'; g.shadowBlur = 10;
  g.fillStyle = style === 'gold' ? '#f6b04a' : 'rgba(92,98,112,0.95)';
  g.beginPath(); g.roundRect(x0, -h / 2, w, h, h / 2); g.fill(); g.shadowBlur = 0;
  g.fillStyle = style === 'gold' ? '#231d15' : 'rgba(230,234,242,0.95)'; g.textBaseline = 'middle'; g.fillText(txt, x0 + size * 0.7, 0.5);
  g.restore(); return { x0, w, h };
}
function draftText(t, txt, t0, t1, t2, t3) {
  if (t < t0 || t > t3 + 0.1) return null;
  const n = t < t1 ? Math.round(txt.length * (t - t0) / (t1 - t0)) : t < t2 ? txt.length : Math.round(txt.length * (1 - (t - t2) / (t3 - t2)));
  return txt.slice(0, Math.max(0, n));
}
const cursor = t => (Math.floor(t * 3) % 2 ? '|' : ' ');

function glowDot(g, x, y, r, a) {
  g.save(); g.globalCompositeOperation = 'lighter';
  const gr = g.createRadialGradient(x, y, 0, x, y, r * 4); gr.addColorStop(0, rgba(C.goldHot, 0.9 * a)); gr.addColorStop(0.3, rgba(C.gold, 0.45 * a)); gr.addColorStop(1, rgba(C.gold, 0));
  g.fillStyle = gr; g.beginPath(); g.arc(x, y, r * 4, 0, 7); g.fill(); g.restore();
}

// ---------- the scene ----------
const BUB_SIZE = 30;
function scene(g, t) {
  const h = heavy(t), hb = bodyHeavy(t);
  // phones: he types 1.9-3.3, she types 3.55-4.85, he lifts it again at 8.3 for the real one, she gets it at 10.0
  const phM = ss(1.85, 2.0, t) * (1 - ss(3.2, 3.35, t)) + ss(8.25, 8.5, t) * (1 - ss(9.95, 10.2, t));
  const phF = ss(3.5, 3.65, t) * (1 - ss(4.8, 4.95, t)) + ss(9.95, 10.05, t) * (1 - ss(10.2, 10.4, t));
  // turning around (dir) and holding hands
  const tm = eio(clamp((t - 10.2) / 0.38)), tf = eio(clamp((t - 10.3) / 0.38));
  const dM = lerp(-1, 1, tm), dF = lerp(1, -1, tf);
  const hold = eio(clamp((t - 10.62) / 0.35));
  let pM = bodyPose(hb, phM), pF = bodyPose(hb, phF);
  if (hold > 0) { pM = mix(pM, HOLD, hold); pF = mix(pF, HOLD, hold); }
  const warmK = ss(9.4, 10.4, t);
  const oM = { x: HIM_X, y: GY, dir: dM, s: FS, wk: warmK, pony: false, phone: phM * (t > 8 ? 1 : 0.85), typing: phM > 0.5, still: hb };
  const oF = { x: HER_X, y: GY, dir: dF, s: FS, wk: warmK, pony: true, phone: phF, typing: phF > 0.5, still: hb };
  // ledge + reflections
  ledge(g, t < FLY0 ? ss(0.6, 1, h) : 1 - ss(SEND, SEND + 0.6, t));
  g.save(); g.beginPath(); g.rect(-60, GY - LTOP, DW + 120, LTOP + LFRONT); g.clip();
  const mk = o => Object.assign({}, o, { reflect: true, alpha: 0.13, y: GY + 12 });
  drawFig(g, pM, mk(oM)); drawFig(g, pF, mk(oF)); g.restore();
  // where the word rests: the higher of the two heads
  const headTop = (p, o) => o.y + p.head[1] * o.s - 14.5 * o.s;
  const restY = Math.min(headTop(pM, oM), headTop(pF, oF)) + 2;
  const slots = wordLayout(t, Math.min(h, 1), restY);
  // the light under the word (warm), dims as it gets heavy
  {
    const cx = 360, cy = slots[0].y + slots[0].b / 2; const a = lerp(0.16, 0.05, h) * (t < FLY0 ? 1 : 1 - ss(FLY0, SEND, t));
    g.save(); g.globalCompositeOperation = 'lighter'; const gr = g.createRadialGradient(cx, cy, 0, cx, cy, 300);
    gr.addColorStop(0, rgba(C.gold, a)); gr.addColorStop(1, rgba(C.gold, 0)); g.fillStyle = gr; g.fillRect(cx - 320, cy - 320, 640, 640); g.restore();
  }
  // figures
  drawFig(g, pF, oF); drawFig(g, pM, oM);
  // impact: shockwave along the floor, flying chips off the ledge, a dark flash in the cracks
  for (const [tt, v] of hitList(t)) {
    const k = (t - tt) / 0.55; if (k <= 0 || k >= 1) continue; const e = eout(k);
    g.save(); g.globalCompositeOperation = 'lighter';
    for (const [r0, a0] of [[1, 1], [0.6, 0.6]]) {
      g.strokeStyle = rgba(C.goldHot, 0.55 * a0 * (1 - k) * Math.min(1, v)); g.lineWidth = 4 * (1 - k) + 1;
      g.beginPath(); g.ellipse(360, GY - LTOP / 2, 30 + 420 * e * r0 * Math.min(1, v + 0.2), (6 + 40 * e * r0) * Math.min(1, v + 0.2), 0, 0, 7); g.stroke();
    }
    g.restore();
    if (v >= 0.55) for (let i = 0; i < 16; i++) { // chips knocked off the ledge front
      const sx = lerp(200, 520, hash(i * 2.9 + tt)), vx = (hash(i * 5.1) - 0.5) * 220 * v, vy = -(80 + 160 * hash(i * 3.7)) * v, kt = t - tt;
      const x = sx + vx * kt, y = GY - LTOP + vy * kt + 0.5 * 1400 * kt * kt; if (y > GY + 300) continue;
      g.save(); g.translate(x, y); g.rotate(kt * 12 * (hash(i) - 0.5)); g.fillStyle = `rgba(${70 + 40 * hash(i)},${66 + 36 * hash(i)},${66 + 30 * hash(i)},${1 - k})`;
      const r = 2 + 4 * hash(i * 6.3); g.fillRect(-r, -r * 0.7, r * 2, r * 1.4); g.restore();
    }
  }
  // dust on each thud
  for (const [tt, v] of THUDS) {
    const k = (t - tt) / 0.7; if (k <= 0 || k >= 1) continue;
    for (let i = 0; i < 26; i++) {
      const side = i % 2 ? 1 : -1, fx = (i < 13 ? (side < 0 ? HIM_X : HER_X) : lerp(slots[0].x, slots[4].x + slots[4].b, hash(i * 3.3)));
      const fy = i < 13 ? GY - LTOP + 4 : restY;
      const sp = (20 + 50 * hash(i + tt)) * (0.5 + v), e = eout(k);
      const x = fx + side * sp * e * (0.5 + hash(i * 1.9)), y = fy - (8 + 26 * hash(i * 2.7)) * Math.sin(e * Math.PI * 0.8);
      g.fillStyle = `rgba(210,200,185,${0.35 * (1 - k) * (0.4 + v)})`; g.beginPath(); g.arc(x, y, 1 + 1.6 * hash(i * 4.1), 0, 7); g.fill();
    }
  }
  // drafts: he types "I'm sorry" and deletes it; she types "sorry." and deletes it
  const bubY = (p, o) => o.y + (p.sh[1] + 6) * o.s;
  const dm = draftText(t, "I'm sorry", 2.0, 2.55, 2.85, 3.15);
  if (dm !== null) bubble(g, HIM_X - 40, bubY(pM, oM), dm + cursor(t), 'draft', 'r', 1, ss(2.0, 2.12, t), BUB_SIZE);
  const df = draftText(t, 'sorry…', 3.65, 4.1, 4.4, 4.7);
  if (df !== null) bubble(g, HER_X + 40, bubY(pF, oF), df + cursor(t), 'draft', 'l', 1, ss(3.65, 3.77, t), BUB_SIZE);
  // the real one: his message bubble; the five giant letters fly into it
  let bubLay = null; const bx = HIM_X - 75, by = GY - 215;
  const flyK = i => clamp((t - (FLY0 + i * FLY_ST)) / FLY_D);
  const sendK = clamp((t - SEND) / 0.5);
  if (t >= 8.55 && sendK < 1) {
    const typed = WORD.split('').filter((_, i) => flyK(i) >= 1).length;
    const txt = 'sorry'.slice(0, typed);
    // bubble flies over to her phone once sent
    const tgt = phonePos(pF, oF);
    const e = eio(sendK), x = lerp(bx, tgt[0] + 40, e), y = lerp(by, tgt[1] - 10, e) - Math.sin(e * Math.PI) * 60;
    const sc = lerp(1, 0.25, e), a = 1 - ss(0.75, 1, sendK);
    g.save(); g.translate(x, y); g.scale(sc, sc);
    bubLay = bubble(g, 0, 0, txt + (typed < 5 ? cursor(t) : ''), 'gold', 'r', a, ss(8.55, 8.7, t), BUB_SIZE + 3);
    g.restore();
    if (sendK > 0 && sendK < 1) glowDot(g, x, y, 4, 1 - sendK * 0.5);
  }
  // giant letters (with the flight into the bubble)
  const fullBub = (() => { g.save(); g.font = `600 ${BUB_SIZE + 3}px "Inter"`; const w = g.measureText('sorry').width + (BUB_SIZE + 3) * 1.4; const cw = [...'sorry'].map((c, i) => g.measureText('sorry'.slice(0, i)).width); const cwi = [...'sorry'].map(c => g.measureText(c).width); g.restore(); return { w, cw, cwi }; })();
  for (const sl of slots) {
    const k = t < FLY0 ? 0 : flyK(sl.i); if (k >= 1) continue;
    const thudFlash = THUDS.reduce((m, [tt]) => Math.max(m, t > tt ? Math.exp(-(t - tt) * 7) : 0), 0) * 0.22;
    if (k <= 0) { const sq = squash(t), cx = sl.x + sl.b / 2, by0 = sl.y + sl.b; g.save(); g.translate(cx, by0); g.scale(1 + sq * 0.7, 1 - sq); g.translate(-cx, -by0); letterBlock(g, sl.x, sl.y, sl.b, sl.ch, h, thudFlash); g.restore(); continue; }
    // target: the glyph slot in his bubble (bubble right edge at bx)
    const s = BUB_SIZE + 3, tx = bx - fullBub.w + s * 0.7 + fullBub.cw[sl.i] + fullBub.cwi[sl.i] / 2, ty = by;
    const e = eio(k), b = lerp(sl.b, s * 1.05, e);
    const cx = lerp(sl.x + sl.b / 2, tx, e), cy = lerp(sl.y + sl.b / 2, ty, e) + Math.sin(e * Math.PI) * 30;
    const hh = lerp(h, 0, ss(0, 0.5, k)); // brightens as it leaves
    letterBlock(g, cx - b / 2, cy - b / 2, b, sl.ch, hh, 0.6 * (1 - k), 1 - ss(0.85, 1, k), ss(0.55, 0.95, k));
  }
  // the meeting: warm bloom between their hands
  const bloom = ss(10.75, 11.6, t);
  if (bloom > 0) {
    const hx = 360, hy = GY - 97 * FS; const pulse = 0.85 + 0.15 * Math.sin((t - 10.7) * 3.2);
    g.save(); g.globalCompositeOperation = 'lighter';
    const gr = g.createRadialGradient(hx, hy, 0, hx, hy, 260); gr.addColorStop(0, rgba(C.gold, 0.22 * bloom * pulse)); gr.addColorStop(0.35, rgba(C.gold, 0.1 * bloom * pulse)); gr.addColorStop(1, rgba(C.gold, 0));
    g.fillStyle = gr; g.fillRect(hx - 280, hy - 280, 560, 560);
    glowDot(g, hx, hy, 4.5, 0.9 * bloom * pulse); g.restore();
  }
}

function label(g, txt, x, y, size, alpha, spacing, weight = 600, align = 'left', col = '242,238,230') {
  g.save(); g.font = `${weight} ${size}px "JetBrains Mono"`; g.letterSpacing = spacing + 'px'; g.textAlign = align; g.textBaseline = 'alphabetic';
  g.fillStyle = `rgba(${col},${alpha})`; g.fillText(txt, x, y); g.restore();
}
function headline(g, l1, l2, a) {
  if (a <= 0.01) return;
  g.save(); g.globalAlpha *= a; g.textAlign = 'center'; g.textBaseline = 'alphabetic'; g.shadowColor = 'rgba(0,0,0,0.5)'; g.shadowBlur = 10;
  g.font = '900 50px "Inter Display"'; g.letterSpacing = '0.5px'; g.fillStyle = 'rgba(255,200,110,1)'; g.fillText(l1, 360, 262);
  g.font = '800 32px "Inter Display"'; g.fillStyle = 'rgba(250,246,238,0.98)'; g.fillText(l2, 360, 306); g.restore();
}

// ---------- compose ----------
const zoomAt = t => lerp(1.0, 1.06, eout(clamp(t / 2.0))) + 0.03 * clamp((t - 2) / 11);
function frame(g, t) {
  T = t;
  g.setTransform(W / DW, 0, 0, H / DH, 0, 0);
  background(g, t);
  const punch = hitList(t).reduce((m, [tt, v]) => { const kk = t - tt; return m + (kk > 0 ? 0.045 * Math.min(1.2, v) * Math.exp(-kk * 9) : 0); }, 0);
  const Z = zoomAt(t) + punch, sh = shakeAt(t), k = W / DW, ZY = 700;
  g.setTransform(k * Z, 0, 0, k * Z, k * (360 - 360 * Z) + k * sh * 0.4, k * (ZY - ZY * Z) + k * sh);
  scene(g, t);
  // impact flash
  { const f = hitList(t).reduce((m, [tt, v]) => { const kk = t - tt; return m + (kk > 0 ? 0.09 * Math.min(1, v) * Math.exp(-kk * 18) : 0); }, 0);
    if (f > 0.005) { g.save(); g.setTransform(1, 0, 0, 1, 0, 0); g.globalCompositeOperation = 'lighter'; g.fillStyle = `rgba(255,220,170,${f})`; g.fillRect(0, 0, W, H); g.restore(); } }
  // rewind flicker (1.35-1.75)
  if (t > REW0 - 0.02 && t < REW1 + 0.05) {
    const a = Math.sin(clamp((t - REW0) / (REW1 - REW0 + 0.05)) * Math.PI);
    g.save(); g.setTransform(W / DW, 0, 0, H / DH, 0, 0); g.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 9; i++) { const y = (hash(i + Math.floor(t * 30) * 13) * DH); g.fillStyle = `rgba(200,210,255,${0.06 * a})`; g.fillRect(0, y, DW, 2 + 5 * hash(i * 7)); }
    g.restore();
  }
  // HUD (not zoomed)
  g.setTransform(W / DW, 0, 0, H / DH, 0, 0);
  const endK = ss(10.1, 10.45, t);
  headline(g, 'SORRY IS 5 LETTERS.', 'SO WHY IS IT SO HEAVY?', 1 - endK);
  headline(g, 'JUST 5 LETTERS.', 'SAY IT BEFORE IT GETS HEAVY.', endK);
  // DAY counter + rehook (below the ledge, inside the safe zone)
  const day = dayAt(t), cA = 1 - ss(9.6, 9.9, t);
  if (cA > 0.01) {
    const txt = day >= 5 ? `DAY ${day}  ·  STILL 5 LETTERS` : `DAY ${day}`;
    const lastHit = hitList(t).filter(([tt]) => t >= tt).pop(); const pop = lastHit ? 1 + 0.35 * Math.exp(-(t - lastHit[0]) * 10) : 1;
    g.save(); g.globalAlpha = cA; g.translate(360, 955); g.scale(pop, pop); g.translate(-360, -955); g.font = '700 22px "JetBrains Mono"'; g.letterSpacing = '3px'; g.textAlign = 'center';
    g.fillStyle = day >= 30 ? 'rgba(255,214,150,0.98)' : 'rgba(246,242,234,0.92)'; g.fillText(txt, 360, 962); g.restore();
  }
  // CTA
  const ctaA = ss(11.0, 11.4, t);
  if (ctaA > 0.01) {
    g.save(); g.globalAlpha = ctaA; g.textAlign = 'center'; g.font = '700 26px "Inter"'; g.fillStyle = 'rgba(250,246,238,0.96)';
    g.fillText('Send this to the one who needs it 💛', 360, 960); g.restore();
  }
  label(g, 'SLOW LIGHT', 360, 1270, 11, 0.28, 5, 600, 'center');
}

window.renderAt = (t, sub = 1) => {
  sub = Math.max(1, sub | 0);
  if (sub === 1) frame(out, t);
  else {
    out.setTransform(1, 0, 0, 1, 0, 0); out.fillStyle = '#000'; out.fillRect(0, 0, W, H);
    for (let i = 0; i < sub; i++) {
      frame(A, clamp(t + (i / sub - 0.5) * (1 / 30) * 0.5, 0, DUR));
      out.setTransform(1, 0, 0, 1, 0, 0); out.globalCompositeOperation = 'lighter'; out.globalAlpha = 1 / sub; out.drawImage(acc, 0, 0);
    }
    out.globalCompositeOperation = 'source-over'; out.globalAlpha = 1;
  }
  return cv.toDataURL('image/jpeg', 0.95);
};

window.events = (() => {
  const e = [];
  e.push({ t: 0.0, s: 'creak', g: 0.5, pan: 0 });
  e.push({ t: 0.25, s: 'slam', g: 1.0, pan: 0 }, { t: 0.27, s: 'crack', g: 0.8, pan: 0 });
  e.push({ t: REW0 - 0.05, s: 'rewind', g: 0.7, pan: 0 });
  e.push({ t: 0.25, s: 'sub', g: 1.0, pan: 0 });
  for (const [tt, v] of THUDS.slice(1)) { e.push({ t: tt, s: 'thud', g: 0.45 + 0.55 * v, pan: 0, rate: 1.1 - 0.3 * v }, { t: tt, s: 'sub', g: 0.3 + 0.7 * v, pan: 0 }); if (v >= 0.4) e.push({ t: tt, s: 'slam', g: 0.35 + 0.6 * v, pan: 0, rate: 1.1 - 0.15 * v }); if (v >= 0.8) e.push({ t: tt + 0.02, s: 'crack', g: 0.4 + 0.4 * v, pan: 0 }); }
  e.push({ t: 2.0, s: 'type', g: 0.45, pan: -0.35 }, { t: 2.85, s: 'erase', g: 0.45, pan: -0.35 });
  e.push({ t: 3.65, s: 'type', g: 0.42, pan: 0.35 }, { t: 4.4, s: 'erase', g: 0.42, pan: 0.35 });
  for (let i = 0; i < 5; i++) e.push({ t: FLY0 + i * FLY_ST + FLY_D - 0.02, s: 'brick1', g: 0.5, pan: -0.3, rate: 1 + 0.05 * i });
  e.push({ t: FLY0 - 0.05, s: 'release', g: 0.6, pan: 0 });
  e.push({ t: SEND, s: 'send', g: 0.85, pan: -0.2 }, { t: SEND + 0.5, s: 'ping', g: 0.8, pan: 0.35 });
  e.push({ t: 9.55, s: 'rise', g: 0.5, pan: -0.3 }, { t: 9.6, s: 'rise', g: 0.45, pan: 0.3 });
  e.push({ t: 10.75, s: 'swell', g: 0.85, pan: 0 });
  return e.sort((a, b) => a.t - b.t);
})();
window.DUR = DUR;
document.fonts.load('600 20px "JetBrains Mono"').then(() => document.fonts.load('900 60px "Inter Display"')).then(() => document.fonts.load('600 20px "Inter"')).then(() => { window.ready = true; });
