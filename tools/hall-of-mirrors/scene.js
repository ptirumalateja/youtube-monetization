// Hall of Mirrors - Slow Light parable reel: a dog fights 1,000 reflections; a happy dog sees 1,000 friends.
// Canvas 2D, design space 720x1280 scaled to the render size. window.renderAt(t, sub) -> JPEG data URL.
'use strict';
const DW = 720, DH = 1280;
const qs = new URLSearchParams(location.search);
const W = +(qs.get('w') || 1080), H = +(qs.get('h') || 1920);
const cv = document.createElement('canvas'); cv.width = W; cv.height = H; document.body.appendChild(cv);
const out = cv.getContext('2d');
const acc = document.createElement('canvas'); acc.width = W; acc.height = H;
const A = acc.getContext('2d');
let T = 0;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, k) => a + (b - a) * k;
const ss = (a, b, x) => { const k = clamp((x - a) / (b - a)); return k * k * (3 - 2 * k); };
const eio = k => k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
const eout = k => 1 - Math.pow(1 - k, 3);
function hash(i) { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }
const rgba = (c, a) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;
const C = { gold: [255, 190, 92], goldHot: [255, 232, 180], red: [255, 70, 52], redHot: [255, 150, 120], dog: '#fff4e4', dogFar: '#b9ab98' };

// ---------- layout ----------
const FLOOR = 872;
const MIR = [[34, 236], [260, 460], [484, 686]];   // mirror x ranges (back wall)
const MTOP = 372, MBOT = FLOOR - 6;                  // arch spring line ~ MTOP+70

// ---------- dog rig (local px, facing +x, ground y = 0) ----------
const DK = ['chest', 'hip', 'head', 'f1e', 'f1p', 'f2e', 'f2p', 'r1k', 'r1h', 'r1p', 'r2k', 'r2h', 'r2p', 'tail'];
const STAND = { chest: [42, -74], hip: [-46, -76], head: [82, -116], f1e: [46, -38], f1p: [48, 0], f2e: [34, -38], f2p: [32, 0], r1k: [-34, -44], r1h: [-52, -20], r1p: [-46, 0], r2k: [-46, -44], r2h: [-62, -20], r2p: [-58, 0], tail: [-92, -112] };
const SNARL = { chest: [38, -64], hip: [-48, -70], head: [84, -84], f1e: [56, -34], f1p: [66, 0], f2e: [42, -32], f2p: [48, 0], r1k: [-28, -40], r1h: [-52, -18], r1p: [-42, 0], r2k: [-40, -40], r2h: [-64, -18], r2p: [-56, 0], tail: [-96, -96] };
const LUNGE = { chest: [56, -86], hip: [-30, -70], head: [106, -116], f1e: [90, -84], f1p: [116, -58], f2e: [80, -76], f2p: [104, -48], r1k: [-18, -38], r1h: [-46, -18], r1p: [-30, 0], r2k: [-30, -38], r2h: [-58, -18], r2p: [-46, 0], tail: [-84, -110] };
const DOWN = { chest: [44, -26], hip: [-46, -28], head: [92, -24], f1e: [70, -12], f1p: [96, -6], f2e: [64, -10], f2p: [88, -4], r1k: [-20, -14], r1h: [-50, -8], r1p: [-36, -4], r2k: [-28, -12], r2h: [-58, -6], r2p: [-44, -3], tail: [-104, -14] };
const HAPPY = { chest: [42, -76], hip: [-46, -76], head: [80, -110], f1e: [46, -38], f1p: [48, 0], f2e: [34, -38], f2p: [32, 0], r1k: [-34, -44], r1h: [-52, -20], r1p: [-46, 0], r2k: [-46, -44], r2h: [-62, -20], r2p: [-58, 0], tail: [-88, -132] };
for (const P of [STAND, SNARL, LUNGE, HAPPY]) { for (const n of ['f1e','f2e','r1k','r2k','r1h','r2h']) P[n] = [P[n][0], P[n][1] * 0.9 - 6]; for (const n of ['chest','hip','head','tail']) P[n] = [P[n][0], P[n][1] + 8]; }
function dmix(a, b, k) { const o = {}; for (const n of DK) o[n] = [lerp(a[n][0], b[n][0], k), lerp(a[n][1], b[n][1], k)]; return o; }

// o: {x, y, s, dir, snarl 0..1, wag 0..1, mood 0 red .. 1 gold, alpha, far(bool, cheaper), glow}
function drawDog(g, P, o) {
  const s = o.s, d = o.dir;
  const X = p => o.x + p[0] * d * s, Y = p => o.y + p[1] * s;
  const near = o.col || C.dog, far = o.colFar || C.dogFar;
  g.save(); g.globalAlpha = o.alpha ?? 1; g.lineCap = 'round'; g.lineJoin = 'round';
  const lw = 12.5 * s;
  const seg = (pts, col, w) => { g.strokeStyle = col; g.lineWidth = w; g.beginPath(); g.moveTo(X(pts[0]), Y(pts[0])); for (let i = 1; i < pts.length; i++) g.lineTo(X(pts[i]), Y(pts[i])); g.stroke(); };
  if (!o.far) { const gc = o.mood < 0.5 ? rgba(C.red, 0.45 * (1 - o.mood * 2)) : rgba(C.gold, 0.45 * (o.mood * 2 - 1)); g.shadowColor = gc; g.shadowBlur = 14 * s * (W / DW); }
  // far legs
  seg([P.chest, P.f2e, P.f2p], far, lw * 0.78); seg([P.hip, P.r2k, P.r2h, P.r2p], far, lw * 0.78);
  // tail (wag swings the tip)
  const wag = o.wag ? Math.sin(T * 22 + o.x * 0.01) * 22 * o.wag : 0;
  const tb = P.hip, tt = [P.tail[0] + wag * 0.4, P.tail[1] + wag];
  g.strokeStyle = near; g.lineWidth = lw * 0.62; g.beginPath(); g.moveTo(X(tb), Y(tb)); g.quadraticCurveTo(X([tb[0] - 30, tb[1] - 6]), Y([tb[0] - 30, tb[1] - 6]), X(tt), Y(tt)); g.stroke();
  // body: thick arched barrel
  const mid = [(P.chest[0] + P.hip[0]) / 2, (P.chest[1] + P.hip[1]) / 2 - 6];
  g.strokeStyle = near; g.lineWidth = lw * 2.5; g.beginPath(); g.moveTo(X(P.chest), Y(P.chest)); g.quadraticCurveTo(X(mid), Y(mid), X(P.hip), Y(P.hip)); g.stroke();
  g.fillStyle = near; g.beginPath(); g.ellipse(X([P.chest[0] + 4, 0]), Y([0, P.chest[1] + 5]), 27 * s, 24 * s, 0, 0, 7); g.fill();
  g.beginPath(); g.ellipse(X([P.hip[0] - 2, 0]), Y([0, P.hip[1] + 3]), 22 * s, 21 * s, 0, 0, 7); g.fill();
  // hackles: spikes along the back when snarling
  if (o.snarl > 0.05 && !o.far) {
    g.save(); g.shadowBlur = 0; g.fillStyle = near;
    for (let i = 0; i < 9; i++) { const u = 0.15 + i * 0.09; const bx = lerp(P.chest[0], P.hip[0], u), by = lerp(P.chest[1], P.hip[1], u) - 13 - 4 * Math.sin(u * Math.PI);
      const h = (8 + 7 * Math.sin(u * Math.PI)) * o.snarl;
      g.beginPath(); g.moveTo(X([bx - 6, by + 2]), Y([bx - 6, by + 2])); g.lineTo(X([bx - 2, by - h]), Y([bx - 2, by - h])); g.lineTo(X([bx + 5, by + 2]), Y([bx + 5, by + 2])); g.fill(); }
    g.restore();
  }
  // near legs
  seg([P.hip, P.r1k, P.r1h, P.r1p], near, lw * 0.82); seg([P.chest, P.f1e, P.f1p], near, lw * 0.82);
  // neck
  const nb = [P.chest[0] + 6, P.chest[1] - 8];
  seg([nb, [P.head[0] - 12, P.head[1] + 6]], near, lw * 1.9);
  // head: skull + snout + ear
  const hx = X(P.head), hy = Y(P.head), sn = o.snarl || 0;
  g.fillStyle = near; g.beginPath(); g.ellipse(hx, hy, 24 * s, 21 * s, 0, 0, 7); g.fill();
  // snout (upper jaw) and lower jaw that opens with the snarl
  const jaw = 0.18 + 0.5 * sn;
  g.save(); g.translate(hx, hy); g.scale(d * 1.3, 1.3);
  g.fillStyle = near; g.beginPath(); g.roundRect(4 * s, -6 * s, 30 * s, 13 * s, 6 * s); g.fill();
  g.save(); g.translate(8 * s, 6 * s); g.rotate(jaw * 0.9); g.beginPath(); g.roundRect(-2 * s, -3 * s, 26 * s, 8 * s, 4 * s); g.fill(); g.restore();
  if (sn > 0.08 && !o.far) { // gums + teeth
    g.shadowBlur = 0; g.fillStyle = `rgba(150,24,30,${0.95 * sn})`; g.beginPath(); g.moveTo(8 * s, 6 * s); g.lineTo(34 * s, 6 * s); g.lineTo(8 * s + Math.cos(jaw * 0.9) * 26 * s, 6 * s + Math.sin(jaw * 0.9) * 26 * s); g.closePath(); g.fill();
    g.fillStyle = `rgba(255,255,255,${sn})`;
    for (let i = 0; i < 5; i++) { const x0 = (11 + i * 4.6) * s; g.beginPath(); g.moveTo(x0, 6 * s); g.lineTo(x0 + 2.2 * s, (6 + 5 + (i === 0 ? 3 : 0)) * s); g.lineTo(x0 + 4.4 * s, 6 * s); g.fill(); }
  }
  // nose
  g.fillStyle = '#2a2224'; g.beginPath(); g.arc(33 * s, -2 * s, 3.6 * s, 0, 7); g.fill();
  // ear: pricked forward when snarling, soft back when happy
  g.fillStyle = near; g.beginPath(); const ea = lerp(-0.6, 0.15, sn) - 0.5 * (o.mood || 0) * (1 - sn);
  g.save(); g.translate(-6 * s, -12 * s); g.rotate(ea); g.moveTo(-7 * s, 2 * s); g.lineTo(0, -24 * s); g.lineTo(9 * s, 2 * s); g.closePath(); g.fill(); g.restore();
  // eye
  if (!o.far) {
    const red = sn > 0.3 && (o.mood ?? 0) < 0.5;
    g.fillStyle = red ? 'rgba(255,60,40,1)' : '#2a2224'; if (red) { g.shadowColor = 'rgba(255,40,20,1)'; g.shadowBlur = 8 * s * W / DW; }
    g.beginPath(); if (sn > 0.3) { g.moveTo(-1 * s, -6 * s); g.lineTo(9 * s, -3 * s); g.lineTo(0, -1 * s); g.closePath(); } else g.arc(4 * s, -4 * s, 2.8 * s, 0, 7); g.fill();
    // brow furrow
    if (sn > 0.3) { g.shadowBlur = 0; g.strokeStyle = '#2a2224'; g.lineWidth = 2.2 * s; g.beginPath(); g.moveTo(-3 * s, -10 * s); g.lineTo(10 * s, -5 * s); g.stroke(); }
  } else if (sn > 0.3 && (o.mood ?? 0) < 0.5) { g.fillStyle = 'rgba(255,70,40,0.9)'; g.beginPath(); g.arc(4 * s, -4 * s, 2.6 * s, 0, 7); g.fill(); }
  g.restore();
  g.restore();
}

// ---------- the hall ----------
function archPath(g, x0, x1, y0, y1) { const r = (x1 - x0) / 2; g.beginPath(); g.moveTo(x0, y1); g.lineTo(x0, y0 + r); g.arc(x0 + r, y0 + r, r, Math.PI, 0); g.lineTo(x1, y1); g.closePath(); }
function wall(g, t, mood) {
  // warm dark wood/stone wall, lit by candles; tones shift red (hostile) -> gold (friendly)
  const red = 1 - mood;
  let gr = g.createLinearGradient(0, 0, 0, FLOOR);
  gr.addColorStop(0, `rgb(${24 + 10 * red},${19},${22})`); gr.addColorStop(0.55, `rgb(${40 + 16 * red},${28 + 6 * mood},${26})`); gr.addColorStop(1, `rgb(${30 + 10 * red},${22},${22})`);
  g.fillStyle = gr; g.fillRect(-200, -200, DW + 400, FLOOR + 200);
  // panel seams + carved pilasters between mirrors
  for (let i = 0; i < 14; i++) { g.fillStyle = 'rgba(255,220,180,0.035)'; g.fillRect(-200, 40 + i * 64, DW + 400, 1.2); }
  for (const x of [0, 248, 472, 720]) {
    gr = g.createLinearGradient(x - 14, 0, x + 14, 0); gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(0.5, 'rgba(255,210,150,0.10)'); gr.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = gr; g.fillRect(x - 14, 0, 28, FLOOR);
  }
  // ceiling beams fade into the top edge (no flat dark band)
  for (let i = 0; i < 3; i++) { g.fillStyle = `rgba(255,200,140,${0.05 - i * 0.012})`; g.fillRect(-200, 120 + i * 70, DW + 400, 10); }
  // a candelabra glow hangs from the top edge so the top never reads as a flat dark band
  g.save(); g.globalCompositeOperation = 'lighter'; const fl = 0.9 + 0.1 * Math.sin(t * 11);
  gr = g.createRadialGradient(360, 60, 0, 360, 60, 420 * fl); gr.addColorStop(0, rgba(red > 0.5 ? [255, 120, 70] : [255, 190, 110], 0.22)); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = gr; g.fillRect(-200, -200, DW + 400, 700); g.restore();
  g.strokeStyle = 'rgba(120,90,60,0.6)'; g.lineWidth = 2; g.beginPath(); g.moveTo(360, -10); g.lineTo(360, 70); g.stroke();
  g.strokeStyle = 'rgba(170,130,80,0.8)'; g.lineWidth = 3; g.beginPath(); g.moveTo(300, 92); g.quadraticCurveTo(360, 118, 420, 92); g.stroke();
}
function candle(g, x, y, t, k, i, mood) {
  const fl = 0.8 + 0.2 * Math.sin(t * 17 + i * 3.1) * Math.sin(t * 7.3 + i), col = mood < 0.5 ? [255, 140, 80] : [255, 200, 120];
  g.save(); g.globalCompositeOperation = 'lighter';
  let gr = g.createRadialGradient(x, y - 10, 0, x, y - 10, 170 * fl); gr.addColorStop(0, rgba(col, 0.32 * k)); gr.addColorStop(1, rgba(col, 0)); g.fillStyle = gr; g.beginPath(); g.arc(x, y - 10, 170 * fl, 0, 7); g.fill();
  g.restore();
  g.fillStyle = '#e9dcc4'; g.fillRect(x - 5, y, 10, 26); g.fillStyle = '#6a5038'; g.fillRect(x - 10, y + 26, 20, 5);
  g.save(); g.globalCompositeOperation = 'lighter'; g.fillStyle = rgba([255, 230, 170], 0.95 * k);
  g.beginPath(); g.moveTo(x, y - 18 * fl); g.quadraticCurveTo(x + 5, y - 4, x, y); g.quadraticCurveTo(x - 5, y - 4, x, y - 18 * fl); g.fill(); g.restore();
}
// one mirror: nested arches (mirror-in-mirror tunnel) with shrinking dog copies
function mirror(g, t, m, dogFn, mood, crack) {
  const [x0, x1] = MIR[m], y0 = MTOP, y1 = MBOT, cx = (x0 + x1) / 2;
  g.save(); archPath(g, x0, x1, y0, y1); g.clip();
  // glass: dark, tinted by mood, brighter toward the infinite centre
  let gr = g.createLinearGradient(0, y0, 0, y1); const red = 1 - mood;
  gr.addColorStop(0, `rgb(${lerp(46, 60, red)},${lerp(36, 24, red)},${lerp(26, 30, red)})`); gr.addColorStop(1, `rgb(${lerp(70, 74, red)},${lerp(52, 30, red)},${lerp(32, 32, red)})`);
  g.fillStyle = gr; g.fillRect(x0, y0, x1 - x0, y1 - y0);
  const vy = y1 - 300; // vanishing point inside the mirror
  for (let k = 7; k >= 1; k--) { // nested frames + copies, far -> near
    const sc = Math.pow(0.7, k);
    const ax0 = lerp(cx, x0, sc), ax1 = lerp(cx, x1, sc), ay0 = lerp(vy, y0, sc), ay1 = lerp(vy, y1, sc);
    g.save(); archPath(g, ax0, ax1, ay0, ay1); g.strokeStyle = rgba(mood < 0.5 ? [255, 150, 110] : [255, 205, 140], 0.20 + 0.25 * sc); g.lineWidth = 3 * sc + 0.6; g.stroke(); g.restore();
    // floor line in the reflection
    g.fillStyle = `rgba(255,220,180,${0.05 + 0.1 * sc})`; g.fillRect(ax0, ay1 - 1, ax1 - ax0, 1.2);
    if (k <= 4) dogFn(g, cx + (k % 2 ? 12 : -12) * sc, ay1 - 2, sc * 1.12, k, 1 - k * 0.12);
  }
  // sheen
  gr = g.createLinearGradient(x0, y0, x1, y1); gr.addColorStop(0.2, 'rgba(255,255,255,0)'); gr.addColorStop(0.35, 'rgba(255,255,255,0.07)'); gr.addColorStop(0.42, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(x0, y0, x1 - x0, y1 - y0);
  // cracks spread from impact points
  if (crack > 0) { g.strokeStyle = `rgba(255,235,220,${0.55 * crack})`; g.lineWidth = 1.2; const px = cx + (hash(m) - 0.5) * 60, py = y0 + 230 + hash(m + 3) * 100;
    for (let i = 0; i < 9; i++) { const a = i / 9 * Math.PI * 2 + hash(i + m * 9); let x = px, y = py; g.beginPath(); g.moveTo(x, y); for (let j = 0; j < 5; j++) { const l = 30 * crack * (0.6 + hash(i * 7 + j)); x += Math.cos(a + (hash(i + j * 3) - 0.5) * 0.6) * l; y += Math.sin(a + (hash(i * 2 + j) - 0.5) * 0.6) * l; g.lineTo(x, y); } g.stroke(); } }
  g.restore();
  // gilded frame
  g.save(); archPath(g, x0, x1, y0, y1); g.lineWidth = 9; g.strokeStyle = '#5a4126'; g.stroke(); g.lineWidth = 3; g.strokeStyle = rgba(mood < 0.5 ? [230, 150, 90] : [240, 196, 120], 0.85); g.stroke(); g.restore();
}
function floor(g, mood) {
  const y0 = FLOOR; let gr = g.createLinearGradient(0, y0, 0, DH);
  gr.addColorStop(0, `rgb(${46 + 14 * (1 - mood)},${34},${30})`); gr.addColorStop(0.3, 'rgb(30,24,24)'); gr.addColorStop(1, 'rgb(26,21,22)');
  g.fillStyle = gr; g.fillRect(-200, y0, DW + 400, DH - y0 + 200);
  for (let i = 1, d = 10; i < 12; i++, d *= 1.38) { g.fillStyle = `rgba(255,225,190,${0.06 - i * 0.004})`; g.fillRect(-200, y0 + d, DW + 400, 1.3); }
  for (let i = -9; i <= 9; i++) { g.strokeStyle = 'rgba(255,225,190,0.035)'; g.lineWidth = 1.2; g.beginPath(); g.moveTo(360 + i * 46, y0); g.lineTo(360 + i * 46 * 3.4, DH + 40); g.stroke(); }
  g.fillStyle = 'rgba(255,225,190,0.35)'; g.fillRect(-200, y0, DW + 400, 1.5);
}

// ---------- timeline (hook look test; full timeline after VO) ----------
const DUR = 4.0;
function heroPose(t) { // frame 0: lunging snarl, recoil, lunge again
  const c = (t * 1.6) % 1; const k = c < 0.35 ? eout(c / 0.35) : 1 - eio((c - 0.35) / 0.65);
  return dmix(SNARL, LUNGE, k * 0.85);
}
const LOOK = qs.get('look') || 'red';
function scene(g, t) {
  const mood = LOOK === 'gold' ? 1 : 0; if (mood) return sceneGold(g, t);
  wall(g, t, mood);
  const P = heroPose(t), sn = 1;
  const copy = (gg, x, y, sc, k, a) => { // reflections: a pair facing each other (infinite feel), red-eyed
    const dP = heroPose(t - k * 0.03);
    drawDog(gg, dP, { x, y, s: sc * 1.15, dir: k % 2 ? -1 : 1, snarl: sn, mood, alpha: a, far: k > 2, col: k > 2 ? '#d8c6b0' : C.dog });
  };
  for (let m = 0; m < 3; m++) mirror(g, t, m, copy, mood, m === 2 ? 0.4 : m === 0 ? 0.25 : 0);
  candle(g, 248, 520, t, 1, 1, mood); candle(g, 472, 520, t, 1, 2, mood);
  floor(g, mood);
  candle(g, 70, 1000, t, 1, 3, mood); candle(g, 650, 1000, t, 1, 4, mood); for (const [x, i] of [[300, 5], [360, 6], [420, 7]]) candle(g, x, 56 + 36, t, 0.8, i, mood);
  // hero + glossy reflection
  const o = { x: 330, y: FLOOR + 4, s: 1.38, dir: 1, snarl: sn, mood };
  { const gr = g.createRadialGradient(o.x, FLOOR + 6, 0, o.x, FLOOR + 6, 130); gr.addColorStop(0, 'rgba(0,0,0,0.45)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.save(); g.translate(0, FLOOR + 6); g.scale(1, 0.12); g.translate(0, -(FLOOR + 6)); g.fillStyle = gr; g.beginPath(); g.arc(o.x, FLOOR + 6, 130, 0, 7); g.fill(); g.restore(); }
  drawDog(g, P, o);
}

function sceneGold(g, t) {
  const mood = 1; wall(g, t, mood);
  const copy = (gg, x, y, sc, k, a) => drawDog(gg, HAPPY, { x, y, s: sc * 1.15, dir: k % 2 ? -1 : 1, snarl: 0, wag: 1, mood, alpha: a, far: k > 2, col: k > 2 ? '#e8d6b8' : C.dog });
  for (let m = 0; m < 3; m++) mirror(g, t, m, copy, mood, 0);
  candle(g, 248, 520, t, 1, 1, mood); candle(g, 472, 520, t, 1, 2, mood);
  floor(g, mood);
  candle(g, 70, 1000, t, 1, 3, mood); candle(g, 650, 1000, t, 1, 4, mood); for (const [x, i] of [[300, 5], [360, 6], [420, 7]]) candle(g, x, 92, t, 0.8, i, mood);
  drawDog(g, HAPPY, { x: 330, y: FLOOR + 4, s: 1.38, dir: 1, snarl: 0, wag: 1, mood });
}
// ---------- HUD ----------
function fitFont(g, txt, weight, size, family, maxW) { g.font = `${weight} ${size}px "${family}"`; const w = g.measureText(txt).width; if (w > maxW) { size *= maxW / w; g.font = `${weight} ${size}px "${family}"`; } return size; }
function title(g, a, b, k, pop, col) {
  g.save(); g.textAlign = 'center'; g.textBaseline = 'alphabetic'; g.globalAlpha *= k;
  g.translate(360, 262); g.scale(pop, pop); g.translate(-360, -262);
  g.save(); g.fillStyle = 'rgba(18,12,14,0.6)'; g.shadowColor = 'rgba(0,0,0,0.45)'; g.shadowBlur = 18; g.beginPath(); g.roundRect(74, 198, 572, 122, 22); g.fill(); g.restore();
  g.shadowColor = 'rgba(0,0,0,0.6)'; g.shadowBlur = 12;
  fitFont(g, a, 900, 60, 'Inter Display', 520); g.fillStyle = col; g.fillText(a, 360, 256);
  fitFont(g, b, 800, 42, 'Inter Display', 500); g.fillStyle = 'rgba(250,246,238,0.98)'; g.fillText(b, 360, 304);
  g.restore();
}
function counter(g, label, val, col, pop) {
  g.save(); g.textAlign = 'center'; g.translate(360, 952); g.scale(pop, pop);
  g.font = '700 15px "JetBrains Mono"'; g.letterSpacing = '4px'; g.fillStyle = 'rgba(242,232,220,0.85)'; g.fillText(label, 0, -30);
  g.font = '800 40px "JetBrains Mono"'; g.letterSpacing = '1px'; g.shadowColor = col; g.shadowBlur = 14 * W / DW; g.fillStyle = col; g.fillText(val, 0, 8);
  g.restore();
}
function camTf(t) { const z = 1.06 + 0.05 * eout(clamp(t / 2.5)) + 0.02 * Math.exp(-((t * 1.6) % 1) * 6); const sh = 2.5 * Math.exp(-((t * 1.6) % 1) * 8);
  const cx = 360, cy = 700; return [z, cx + Math.sin(t * 61) * sh, cy + Math.cos(t * 47) * sh]; }
function frame(g, t) {
  T = t;
  const [z, cx, cy] = camTf(t);
  g.setTransform(W / DW * z, 0, 0, H / DH * z, (W / DW) * (360 - cx * z), (H / DH) * (700 - cy * z) + 0);
  g.setTransform(W / DW, 0, 0, H / DH, 0, 0); g.translate(360, 700); g.scale(z, z); g.translate(-cx, -cy);
  scene(g, t);
  g.setTransform(W / DW, 0, 0, H / DH, 0, 0);
  // finish: light vignette (edges keep candle light, never flat black) + grain
  const gr = g.createRadialGradient(360, 660, 300, 360, 660, 900); gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(1, 'rgba(0,0,0,0.3)'); g.fillStyle = gr; g.fillRect(0, 0, DW, DH);
  if (!window._grain) { window._grain = []; for (let n = 0; n < 4; n++) { const c = document.createElement('canvas'); c.width = c.height = 256; const x = c.getContext('2d'); const im = x.createImageData(256, 256);
    for (let p = 0; p < im.data.length; p += 4) { const v = Math.random() * 255; im.data[p] = im.data[p + 1] = im.data[p + 2] = v; im.data[p + 3] = 255; } x.putImageData(im, 0, 0); window._grain.push(c); } }
  g.save(); g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 0.05; g.globalCompositeOperation = 'overlay'; g.fillStyle = g.createPattern(window._grain[((Math.floor(t * 30) % 4) + 4) % 4], 'repeat'); g.fillRect(0, 0, W, H); g.restore();
  g.setTransform(W / DW, 0, 0, H / DH, 0, 0);
  if (LOOK === 'gold') { title(g, 'SAME ROOM.', 'A THOUSAND FRIENDS.', 1, 1, 'rgb(255,200,110)'); counter(g, 'FRIENDS', '1,000', 'rgb(255,200,110)', 1); }
  else { title(g, 'HE FOUGHT 1,000 DOGS.', 'ONLY ONE WAS REAL.', 1, 1 + 0.1 * Math.exp(-t * 8), 'rgb(255,120,96)'); counter(g, 'ENEMIES', '1,000', 'rgb(255,110,90)', 1); }
  g.save(); g.font = '600 11px "JetBrains Mono"'; g.letterSpacing = '5px'; g.textAlign = 'center'; g.fillStyle = 'rgba(242,238,230,0.28)'; g.fillText('SLOW LIGHT', 360, 1270); g.restore();
}
window.renderAt = (t, sub = 1) => {
  sub = Math.max(1, sub | 0);
  if (sub === 1) frame(out, t);
  else { out.setTransform(1, 0, 0, 1, 0, 0); out.fillStyle = '#000'; out.fillRect(0, 0, W, H);
    for (let i = 0; i < sub; i++) { A.setTransform(1, 0, 0, 1, 0, 0); frame(A, t + (i / sub - 0.5) * (1 / 30) * 0.5); out.setTransform(1, 0, 0, 1, 0, 0); out.globalCompositeOperation = 'lighter'; out.globalAlpha = 1 / sub; out.drawImage(acc, 0, 0); }
    out.globalCompositeOperation = 'source-over'; out.globalAlpha = 1; }
  return cv.toDataURL('image/jpeg', 0.92);
};
window.events = []; window.TL = {}; window.DUR = DUR;
document.fonts.load('700 15px "JetBrains Mono"').then(() => document.fonts.load('800 40px "JetBrains Mono"')).then(() => document.fonts.load('900 56px "Inter Display"')).then(() => { window.ready = true; });
