// Profit Pipe - Slow Light remake of the "hard work fills the pipe" stickman reel, in the Silence Is Distance (v8) look.
// Canvas 2D, design space 720x1280 scaled to the render size. Stickman, palette, glossy ledges and labels are the Silence ones.
// Story: the employee's laptop feeds a hose -> the PROFIT pipe -> pours gold into MANAGEMENT's mouth. He overflows, coins pile up.
// A leak marked SALARY drips one coin to the employee. Counters: YOU 1, 2 vs THEM racing into the thousands.
// window.renderAt(t, sub) -> JPEG data URL. window.events -> sound cue list (used by mix.py).
'use strict';
const DW = 720, DH = 1280, DUR = 12.0;
const qs = new URLSearchParams(location.search);
const W = +(qs.get('w') || 1080), H = +(qs.get('h') || 1920);
const cv = document.createElement('canvas'); cv.width = W; cv.height = H; document.body.appendChild(cv);
const out = cv.getContext('2d');
const acc = document.createElement('canvas'); acc.width = W; acc.height = H;
const A = acc.getContext('2d');
let T = 0;

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

// ---------- palette (Slow Light, same as Silence) ----------
const C = {
  bgTop: '#191b24', bgMid: '#111219', bgBot: '#16171f',
  gold: [255, 190, 92], goldHot: [255, 232, 180],
  figWarm: '#fff7ea', farWarm: '#a59d92',
  figCool: '#dfe4ee', farCool: '#8a909c',
};
const rgba = (c, a) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;

// ---------- timeline ----------
const VALVE = 0.3;           // valve snaps wider, the pour doubles
const OVER = 4.4;            // he can't swallow any more
const FLAIL1 = 6.0;          // flailing ends, he slumps back stuffed
const DRIPS = [6.85, 9.45];  // salary coin lands in his hands
const DRIP_FALL = 0.5;
const SALARY_ON = 5.5;
const END_TXT = 9.75, CTA_ON = 10.5;

// ---------- layout (design px) ----------
const FLOOR = 834;
const EX = 262;                         // employee hip x (faces right)
const MX = 476, SEAT = 734, MS = 1.15;  // manager hip x (faces left), box top, scale
const BOX = { x0: 424, x1: 590 };
const PIPE_Y = 452, PIPE_R = 11, NOZ = { x: 514, y: 522 };
const HX = 200;                         // the hose rises into the pipe here
const LEAK_X = 286;

// ---------- poses (local px, facing +x, ground y = 0) - the Silence rig ----------
const K = ['head', 'sh', 'hip', 'kn1', 'ft1', 'kn2', 'ft2', 'el1', 'hd1', 'el2', 'hd2'];
const SIT = { head: [0, -88], sh: [-9, -64], hip: [-16, -9], kn1: [14, -40], ft1: [27, -6], kn2: [10, -38], ft2: [22, -6], el1: [4, -40], hd1: [16, -50], el2: [1, -39], hd2: [13, -49] };
const SLUMP = { head: [10, -72], sh: [-3, -56], hip: [-16, -9], kn1: [14, -40], ft1: [27, -6], kn2: [10, -38], ft2: [22, -6], el1: [8, -34], hd1: [18, -44], el2: [5, -33], hd2: [15, -43] };
const TYPE = { head: [6, -84], sh: [-6, -62], hip: [-16, -9], kn1: [14, -40], ft1: [27, -6], kn2: [10, -38], ft2: [22, -6], el1: [6, -40], hd1: [20, -47], el2: [3, -39], hd2: [17, -46] };
const CUP = { head: [-4, -90], sh: [-12, -66], hip: [-16, -9], kn1: [14, -40], ft1: [27, -6], kn2: [10, -38], ft2: [22, -6], el1: [10, -50], hd1: [22, -60], el2: [7, -50], hd2: [19, -59] };
// manager sits on the box edge (ground = seat), legs hang to the floor; faces left (dir -1)
const LEG = { kn1: [30, -6], ft1: [36, 92], kn2: [25, -5], ft2: [29, 92] };
const MSIT = Object.assign({ head: [-38, -86], sh: [-26, -60], hip: [-4, -6], el1: [-2, -36], hd1: [12, -24], el2: [-6, -35], hd2: [8, -23] }, LEG);
const MFLAIL = Object.assign({ head: [-14, -88], sh: [-12, -62], hip: [-4, -6], el1: [8, -84], hd1: [30, -108], el2: [-36, -80], hd2: [-58, -100] }, LEG);
const MSTUFF = Object.assign({ head: [-42, -80], sh: [-30, -56], hip: [-4, -6], el1: [-24, -30], hd1: [-16, -6], el2: [-30, -30], hd2: [-24, -6] }, LEG);
function mix(a, b, k) { const o = {}; for (const n of K) o[n] = [lerp(a[n][0], b[n][0], k), lerp(a[n][1], b[n][1], k)]; return o; }

// ---------- figure (Silence drawFig + mouth / tie / belly for the manager) ----------
function drawFig(g, pose, o) {
  const s = o.s, d = o.dir;
  { const b = Math.sin(T * 2.4 + o.x * 0.05) * 1.3, ty = Math.sin(T * 14 + o.x) * 0.8; pose = Object.assign({}, pose);
    for (const n of ['head', 'sh']) pose[n] = [pose[n][0], pose[n][1] + b];
    for (const n of ['el1', 'el2']) pose[n] = [pose[n][0], pose[n][1] + b * 0.6];
    for (const n of ['hd1', 'hd2']) pose[n] = [pose[n][0], pose[n][1] + b * 0.5 + (o.typing ? ty : 0)]; }
  const X = p => o.x + p[0] * d * s, Y = p => o.y + p[1] * s * (o.reflect ? -0.55 : 1);
  const near = o.warm ? C.figWarm : C.figCool, far = o.warm ? C.farWarm : C.farCool;
  g.save(); g.globalAlpha = o.alpha ?? 1; g.lineCap = 'round'; g.lineJoin = 'round';
  const lw = 11.5 * s;
  const seg = (pts, col, w) => { g.strokeStyle = col; g.lineWidth = w; g.beginPath(); g.moveTo(X(pts[0]), Y(pts[0])); for (let i = 1; i < pts.length; i++) g.lineTo(X(pts[i]), Y(pts[i])); g.stroke(); };
  if (!o.reflect) { g.shadowColor = o.warm ? 'rgba(255,214,160,0.42)' : 'rgba(190,210,255,0.35)'; g.shadowBlur = 9 * s * (W / DW); }
  seg([pose.hip, pose.kn2, pose.ft2], far, lw);
  seg([pose.sh, pose.el2, pose.hd2], far, lw * 0.92);
  if (o.belly) { // torso bows forward as he fills up
    const mx = (pose.sh[0] + pose.hip[0]) / 2, my = (pose.sh[1] + pose.hip[1]) / 2; const dx = pose.hip[0] - pose.sh[0], dy = pose.hip[1] - pose.sh[1], l = Math.hypot(dx, dy);
    const nx = -dy / l, ny = dx / l, b = o.belly * 26; const cx = mx + nx * b * (nx > 0 ? 1 : -1), cy = my + ny * b * (nx > 0 ? 1 : -1);
    g.strokeStyle = near; g.lineWidth = lw * (1.05 + o.belly * 0.9); g.beginPath(); g.moveTo(X(pose.sh), Y(pose.sh)); g.quadraticCurveTo(X([cx, cy]), Y([cx, cy]), X(pose.hip), Y(pose.hip)); g.stroke();
  } else seg([pose.sh, pose.hip], near, lw * 1.05);
  if (o.tie && !o.reflect) { // small tie hanging from the collar along the chest
    const a = pose.sh, b = [lerp(pose.sh[0], pose.hip[0], 0.42) + 5, lerp(pose.sh[1], pose.hip[1], 0.42)];
    g.save(); g.shadowBlur = 0; g.strokeStyle = '#c9453a'; g.lineWidth = 5.5 * s; g.beginPath(); g.moveTo(X([a[0] + 4, a[1] + 3]), Y([a[0] + 4, a[1] + 3])); g.lineTo(X(b), Y(b)); g.stroke(); g.restore();
  }
  seg([pose.hip, pose.kn1, pose.ft1], near, lw);
  if (o.laptop && !o.reflect) laptop(g, pose, o, X, Y);
  seg([pose.sh, pose.el1, pose.hd1], near, lw * 0.92);
  g.fillStyle = near; g.beginPath();
  if (o.mouth > 0.02 && !o.reflect) { // open mouth: a wedge cut out of the head, facing up-front
    const hx = X(pose.head), hy = Y(pose.head), ang = -Math.PI / 2 + 0.55 * d, w = 0.62 * o.mouth;
    g.moveTo(hx, hy); g.arc(hx, hy, 14.5 * s, ang + w, ang - w + Math.PI * 2); g.closePath();
  } else g.arc(X(pose.head), Y(pose.head), 14.5 * s, 0, 7);
  g.fill();
  if (o.glow > 0 && !o.reflect) { // laptop light on the face
    const hx = X(pose.hd1), hy = Y(pose.hd1);
    g.shadowBlur = 0; g.globalCompositeOperation = 'lighter';
    const r = 50 * s; const gr = g.createRadialGradient(hx, hy - 8 * s, 0, hx, hy - 8 * s, r);
    gr.addColorStop(0, rgba(C.gold, 0.28 * o.glow)); gr.addColorStop(1, rgba(C.gold, 0));
    g.fillStyle = gr; g.beginPath(); g.arc(hx, hy - 8 * s, r, 0, 7); g.fill();
  }
  g.restore();
}
function laptop(g, pose, o, X, Y) {
  // base on the knees, lid hinged at the far end, screen faces him
  const b0 = [pose.kn1[0] - 14, pose.kn1[1] - 7], b1 = [pose.kn1[0] + 24, pose.kn1[1] - 10], lid = [b1[0] + 9, b1[1] - 30];
  g.save(); g.shadowBlur = 0; g.lineCap = 'round'; g.lineJoin = 'round';
  // glowing screen face (a thin quad on the inside of the lid)
  g.globalCompositeOperation = 'lighter';
  const sc = g.createRadialGradient(X([b1[0] - 6, b1[1] - 14]), Y([0, b1[1] - 14]), 0, X([b1[0] - 6, 0]), Y([0, b1[1] - 14]), 34 * o.s);
  sc.addColorStop(0, rgba(C.gold, 0.35 * o.glow + 0.1)); sc.addColorStop(1, rgba(C.gold, 0)); g.fillStyle = sc; g.beginPath(); g.arc(X([b1[0] - 6, 0]), Y([0, b1[1] - 14]), 34 * o.s, 0, 7); g.fill();
  g.globalCompositeOperation = 'source-over';
  g.strokeStyle = '#30313a'; g.lineWidth = 6 * o.s; g.beginPath(); g.moveTo(X(b0), Y(b0)); g.lineTo(X(b1), Y(b1)); g.lineTo(X(lid), Y(lid)); g.stroke();
  g.strokeStyle = rgba(C.goldHot, 0.6 + 0.4 * o.glow); g.lineWidth = 3 * o.s; g.beginPath(); g.moveTo(X([b1[0] - 3, b1[1] - 4]), Y([b1[0] - 3, b1[1] - 4])); g.lineTo(X([lid[0] - 3, lid[1] + 2]), Y([lid[0] - 3, lid[1] + 2])); g.stroke();
  g.restore();
}

// ---------- background (Silence) ----------
function bgPipe(g, x0, y0, x1, y1, r, a) {
  g.save(); g.globalAlpha = a; g.lineCap = 'butt';
  for (const [w, col, dy] of [[r * 2 + 3, '#262833', 0], [r * 2, '#3b3e4b', 0], [r * 0.8, '#555968', -r * 0.35], [1.6, 'rgba(230,234,250,0.35)', -r * 0.55]]) {
    g.strokeStyle = col; g.lineWidth = w; g.beginPath(); g.moveTo(x0, y0 + dy); g.lineTo(x1, y1 + dy); g.stroke(); }
  g.restore();
}
function background(g, t) {
  let gr = g.createLinearGradient(0, 0, 0, DH);
  gr.addColorStop(0, '#2a2c37'); gr.addColorStop(0.45, '#1c1e27'); gr.addColorStop(1, '#22232c');
  g.fillStyle = gr; g.fillRect(-200, -200, DW + 400, DH + 400);
  // wall panels: vertical seams edge to edge + a rail
  for (let x = -20; x < DW + 60; x += 96) { g.fillStyle = 'rgba(255,255,255,0.035)'; g.fillRect(x, -200, 1.5, DH); g.fillStyle = 'rgba(0,0,0,0.12)'; g.fillRect(x + 1.5, -200, 2, DH); }
  g.fillStyle = 'rgba(255,255,255,0.05)'; g.fillRect(-200, 300, DW + 400, 2);
  // out-of-focus factory pipes along the top and down both sides
  bgPipe(g, -200, 28, DW + 200, 28, 16, 0.9); bgPipe(g, -200, 92, DW + 200, 92, 9, 0.7);
  for (let x = 40; x < DW; x += 150) { g.fillStyle = 'rgba(110,114,130,0.7)'; g.fillRect(x, 10, 7, 36); }
  // a warm work lamp above the scene
  gr = g.createRadialGradient(400, 0, 10, 400, 0, 620); gr.addColorStop(0, 'rgba(255,200,130,0.16)'); gr.addColorStop(1, 'rgba(255,200,130,0)');
  g.fillStyle = gr; g.fillRect(-200, -200, DW + 400, DH);
  gr = g.createRadialGradient(560, 600, 10, 560, 600, 470); gr.addColorStop(0, `rgba(255,190,110,${0.11 + 0.05 * ss(OVER, 6, t)})`); gr.addColorStop(1, 'rgba(255,190,110,0)');
  g.fillStyle = gr; g.fillRect(0, 0, DW, DH);
  gr = g.createRadialGradient(180, 720, 10, 180, 720, 380); gr.addColorStop(0, 'rgba(120,150,210,0.08)'); gr.addColorStop(1, 'rgba(120,150,210,0)');
  g.fillStyle = gr; g.fillRect(0, 0, DW, DH);
  gr = g.createLinearGradient(0, 0, DW, DH * 0.6);
  gr.addColorStop(0.25, 'rgba(255,255,255,0)'); gr.addColorStop(0.42, 'rgba(255,255,255,0.025)'); gr.addColorStop(0.6, 'rgba(255,255,255,0)');
  g.fillStyle = gr; g.fillRect(0, 0, DW, DH);
  for (let i = 0; i < 46; i++) {
    const x = (hash(i) * DW + t * (4 + 8 * hash(i + 9))) % DW, y = 120 + hash(i + 3) * 960 - t * (3 + 5 * hash(i + 5));
    const a = 0.10 + 0.18 * hash(i + 7) * (0.6 + 0.4 * Math.sin(t * 1.3 + i));
    g.fillStyle = `rgba(255,240,215,${a})`; g.beginPath(); g.arc(x, y, 0.6 + 1.1 * hash(i + 11), 0, 7); g.fill();
  }
}
function label(g, txt, x, y, size, alpha, spacing, weight = 600, align = 'left', col = '242,238,230') {
  g.save(); g.font = `${weight} ${size}px "JetBrains Mono"`; g.letterSpacing = spacing + 'px'; g.textAlign = align; g.textBaseline = 'alphabetic';
  g.fillStyle = `rgba(${col},${alpha})`; g.fillText(txt, x, y); g.restore();
}
function glowDot(g, x, y, r, a) {
  g.save(); g.globalCompositeOperation = 'lighter';
  const gr = g.createRadialGradient(x, y, 0, x, y, r * 4); gr.addColorStop(0, rgba(C.goldHot, 0.9 * a)); gr.addColorStop(0.3, rgba(C.gold, 0.45 * a)); gr.addColorStop(1, rgba(C.gold, 0));
  g.fillStyle = gr; g.beginPath(); g.arc(x, y, r * 4, 0, 7); g.fill(); g.restore();
}

// ---------- glossy floor + seat box (Silence ledge material) ----------
function floor(g) {
  const y0 = FLOOR, top = 21, front = 24, depth = 140, tone = [56, 57, 66];
  let gr = g.createLinearGradient(0, y0 - top, 0, y0 + front);
  gr.addColorStop(0, `rgba(${tone[0] + 26},${tone[1] + 26},${tone[2] + 28},1)`); gr.addColorStop(0.45, `rgba(${tone[0]},${tone[1]},${tone[2]},1)`); gr.addColorStop(1, `rgba(${tone[0] - 22},${tone[1] - 22},${tone[2] - 20},1)`);
  g.fillStyle = gr; g.fillRect(-60, y0 - top, DW + 120, top + front);
  // v4 (no borders): the glossy floor continues to the bottom edge, lit warm toward the pile, with receding seams
  gr = g.createLinearGradient(0, y0 + front, 0, y0 + 420);
  gr.addColorStop(0, 'rgb(40,41,50)'); gr.addColorStop(0.5, 'rgb(46,46,56)'); gr.addColorStop(1, 'rgb(54,52,60)');
  g.fillStyle = gr; g.fillRect(-200, y0 + front, DW + 400, 420);
  gr = g.createRadialGradient(400, y0 + 40, 10, 400, y0 + 40, 420); gr.addColorStop(0, 'rgba(255,190,110,0.22)'); gr.addColorStop(1, 'rgba(255,190,110,0)');
  g.fillStyle = gr; g.fillRect(-200, y0 + front, DW + 400, 420);
  for (let i = 1, d = 14; i < 12; i++, d *= 1.42) { g.fillStyle = `rgba(255,240,220,${0.10 - i * 0.004})`; g.fillRect(-200, y0 + front + d, DW + 400, 1.3); }
  for (let i = -8; i <= 8; i++) { g.strokeStyle = 'rgba(255,240,220,0.045)'; g.lineWidth = 1.2; g.beginPath(); g.moveTo(384 + i * 60, y0 + front); g.lineTo(384 + i * 60 * 3.2, y0 + 420); g.stroke(); }
  g.fillStyle = 'rgba(255,236,205,0.45)'; g.fillRect(-60, y0 + front - 1.2, DW + 120, 1.6);
  g.fillStyle = 'rgba(255,255,255,0.10)'; g.fillRect(-60, y0 - top, DW + 120, 1.2);
}
function seatBox(g, t) {
  const { x0, x1 } = BOX, y0 = SEAT, y1 = FLOOR - 4;
  let gr = g.createLinearGradient(x0, 0, x1, 0);
  gr.addColorStop(0, '#4a4a54'); gr.addColorStop(0.5, '#383944'); gr.addColorStop(1, '#2a2b33');
  g.fillStyle = gr; g.beginPath(); g.roundRect(x0, y0, x1 - x0, y1 - y0, 4); g.fill();
  gr = g.createLinearGradient(0, y0 - 14, 0, y0 + 2); gr.addColorStop(0, '#6a6a76'); gr.addColorStop(1, '#4c4c58');
  g.fillStyle = gr; g.beginPath(); g.moveTo(x0, y0); g.lineTo(x0 + 16, y0 - 14); g.lineTo(x1 + 16, y0 - 14); g.lineTo(x1, y0); g.closePath(); g.fill();
  g.fillStyle = 'rgba(255,236,205,0.5)'; g.fillRect(x0, y0 - 0.6, x1 - x0, 1.4);
  // warm gold light from the pile on the box front
  const k = ss(OVER, 7, t); gr = g.createLinearGradient(0, y1, 0, y0); gr.addColorStop(0, rgba(C.gold, 0.22 * k)); gr.addColorStop(1, rgba(C.gold, 0));
  g.fillStyle = gr; g.fillRect(x0, y0, x1 - x0, y1 - y0);
}

// ---------- the pipe + hose ----------
const CPL = PIPE_Y + 64;
function pipePath(g) { g.beginPath(); g.moveTo(HX, CPL); g.lineTo(HX, PIPE_Y + 28); g.quadraticCurveTo(HX, PIPE_Y, HX + 28, PIPE_Y); g.lineTo(NOZ.x - 28, PIPE_Y); g.quadraticCurveTo(NOZ.x, PIPE_Y, NOZ.x, PIPE_Y + 28); g.lineTo(NOZ.x, NOZ.y - 6); }
const PIPE_PTS = (() => { // polyline along the pipe from the hose coupling to the nozzle, for pulses
  const p = []; for (let y = CPL; y >= PIPE_Y + 28; y -= 4) p.push([HX, y]);
  for (let a = 0; a <= 1; a += 0.1) p.push([HX + 28 * (1 - Math.cos(a * Math.PI / 2)), PIPE_Y + 28 - 28 * Math.sin(a * Math.PI / 2)]);
  for (let x = HX + 28; x <= NOZ.x - 28; x += 4) p.push([x, PIPE_Y]);
  for (let a = 0; a <= 1; a += 0.1) p.push([NOZ.x - 28 + 28 * Math.sin(a * Math.PI / 2), PIPE_Y + 28 - 28 * Math.cos(a * Math.PI / 2)]);
  for (let y = PIPE_Y + 28; y <= NOZ.y; y += 4) p.push([NOZ.x, y]);
  return p;
})();
function hosePts() { // laptop -> floor -> up into the pipe coupling
  const lid = [EX + 50, 778]; const a = lid, b = [EX + 64, 812], c = [EX + 50, 832], d = [EX + 20, 832];
  const p = []; for (let u = 0; u <= 1; u += 0.05) { const v = 1 - u; p.push([v * v * v * a[0] + 3 * v * v * u * b[0] + 3 * v * u * u * c[0] + u * u * u * d[0], v * v * v * a[1] + 3 * v * v * u * b[1] + 3 * v * u * u * c[1] + u * u * u * d[1]]); }
  for (let x = EX + 20; x >= HX + 24; x -= 4) p.push([x, 832]);
  for (let u = 0; u <= 1; u += 0.1) p.push([HX + 24 - 24 * Math.sin(u * Math.PI / 2), 832 - 24 * (1 - Math.cos(u * Math.PI / 2))]);
  for (let y = 808; y >= CPL; y -= 4) p.push([HX, y]);
  return p;
}
const HOSE_PTS = hosePts();
const FLOW = HOSE_PTS.concat(PIPE_PTS);
const FLOW_LEN = (() => { const l = [0]; for (let i = 1; i < FLOW.length; i++) l.push(l[i - 1] + Math.hypot(FLOW[i][0] - FLOW[i - 1][0], FLOW[i][1] - FLOW[i - 1][1])); return l; })();
function flowAt(d) { // point at distance d along hose+pipe
  const L = FLOW_LEN; if (d <= 0) return FLOW[0]; if (d >= L[L.length - 1]) return FLOW[FLOW.length - 1];
  let i = 1; while (L[i] < d) i++; const k = (d - L[i - 1]) / (L[i] - L[i - 1]); return [lerp(FLOW[i - 1][0], FLOW[i][0], k), lerp(FLOW[i - 1][1], FLOW[i][1], k)];
}
const HOSE_LEN = (() => { let l = 0; for (let i = 1; i < HOSE_PTS.length; i++) l += Math.hypot(HOSE_PTS[i][0] - HOSE_PTS[i - 1][0], HOSE_PTS[i][1] - HOSE_PTS[i - 1][1]); return l; })();
function hose(g, t) {
  g.save(); g.lineCap = 'round'; g.lineJoin = 'round';
  g.strokeStyle = '#3a3b46'; g.lineWidth = 10; g.beginPath(); HOSE_PTS.forEach((p, i) => i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); g.stroke();
  g.strokeStyle = 'rgba(255,200,120,0.45)'; g.lineWidth = 3; g.shadowColor = rgba(C.gold, 0.9); g.shadowBlur = 8 * W / DW; g.stroke();
  g.restore();
}
function pipe(g, t) {
  g.save(); g.lineCap = 'butt'; g.lineJoin = 'round';
  pipePath(g); g.strokeStyle = '#2e3039'; g.lineWidth = PIPE_R * 2 + 3; g.stroke();
  pipePath(g); g.strokeStyle = '#5b5e6c'; g.lineWidth = PIPE_R * 2; g.stroke();
  g.translate(0, -4); pipePath(g); g.strokeStyle = '#8a8d9c'; g.lineWidth = PIPE_R * 0.9; g.stroke();
  g.translate(0, -2.5); pipePath(g); g.strokeStyle = 'rgba(235,238,250,0.55)'; g.lineWidth = 2; g.stroke();
  g.restore();
  // collars
  for (const [x, y, vert] of [[HX, CPL, 1], [NOZ.x, NOZ.y - 4, 1], [250, PIPE_Y, 0], [440, PIPE_Y, 0]]) {
    g.fillStyle = '#6d7080'; if (vert) g.fillRect(x - PIPE_R - 3, y - 5, PIPE_R * 2 + 6, 9); else g.fillRect(x - 4, y - PIPE_R - 3, 8, PIPE_R * 2 + 6);
    g.fillStyle = 'rgba(240,242,255,0.35)'; if (vert) g.fillRect(x - PIPE_R - 3, y - 5, PIPE_R * 2 + 6, 1.5); else g.fillRect(x - 4, y - PIPE_R - 3, 1.5, PIPE_R * 2 + 6);
  }
  // valve wheel on top, spins open at VALVE
  const vx = 345, vy = PIPE_Y - 30, rot = 2.6 * eio(clamp((t + 0.25 - VALVE) / 0.35)) + 0.15 * t;
  g.fillStyle = '#5b5e6c'; g.fillRect(vx - 3, vy, 6, 18);
  g.save(); g.translate(vx, vy); g.rotate(rot); g.strokeStyle = '#9a9dac'; g.lineWidth = 3; g.beginPath(); g.arc(0, 0, 12, 0, 7); g.stroke();
  for (let i = 0; i < 4; i++) { g.rotate(Math.PI / 4 * 2); g.beginPath(); g.moveTo(0, 0); g.lineTo(12, 0); g.stroke(); } g.fillStyle = '#c9cbd6'; g.beginPath(); g.arc(0, 0, 3, 0, 7); g.fill(); g.restore();
  // leak crack
  const lk = ss(SALARY_ON - 0.2, SALARY_ON + 0.2, t);
  if (lk > 0) { g.strokeStyle = `rgba(20,20,26,${0.9 * lk})`; g.lineWidth = 1.6; g.beginPath(); g.moveTo(LEAK_X - 6, PIPE_Y + 5); g.lineTo(LEAK_X - 1, PIPE_Y + 9); g.lineTo(LEAK_X + 3, PIPE_Y + 7); g.lineTo(LEAK_X + 1, PIPE_Y + PIPE_R); g.stroke(); }
}
function pulses(g, t) {
  // gold pulses born at each typing burst, run the hose and the pipe, feed the pour
  const total = FLOW_LEN[FLOW_LEN.length - 1], speed = 900;
  g.save(); g.globalCompositeOperation = 'lighter';
  for (let i = -12; i < 60; i++) {
    const tb = i * 0.2; const d = (t - tb) * speed; if (d < 0 || d > total) continue;
    const [x, y] = flowAt(d); const inPipe = d > HOSE_LEN; const a = (inPipe ? 0.6 : 1) * (0.7 + 0.3 * hash(i + 40));
    const r = inPipe ? 9 : 6.5; const gr = g.createRadialGradient(x, y, 0, x, y, r * 2.2);
    gr.addColorStop(0, rgba(C.goldHot, a)); gr.addColorStop(0.4, rgba(C.gold, a * 0.5)); gr.addColorStop(1, rgba(C.gold, 0));
    g.fillStyle = gr; g.beginPath(); g.arc(x, y, r * 2.2, 0, 7); g.fill();
  }
  // the pipe's gold seam glows stronger after the valve opens
  g.globalAlpha = 0.20 + 0.18 * ss(VALVE, VALVE + 0.3, t); g.translate(0, 0); pipePath(g); g.strokeStyle = rgba(C.gold, 0.5); g.lineWidth = 2.5; g.shadowColor = rgba(C.gold, 1); g.shadowBlur = 10 * W / DW; g.stroke();
  g.restore();
}

// ---------- coins ----------
const RATE = t => t < VALVE ? 34 : t < OVER ? 64 : 82;
const SPAWN = (() => { const s = []; let t = -1.2; while (t < DUR + 0.5) { s.push(t); t += 1 / RATE(Math.max(0, t)); } return s; })();
const G = 1500, V0 = 260;
function mouthPos(t) { const [p, o] = managerPose(t); const a = -Math.PI / 2 + 0.55 * o.dir; const x = o.x + p.head[0] * o.dir * o.s + Math.cos(a) * 8 * o.s, y = o.y + p.head[1] * o.s + Math.sin(a) * 8 * o.s; return [x, y]; }
function fallTime(h) { return (-V0 + Math.sqrt(V0 * V0 + 2 * G * h)) / G; }
const coinCache = new Map();
function coinPlan(i) { // where coin i goes: swallowed, or bounces and lands on the pile
  if (coinCache.has(i)) return coinCache.get(i);
  const ts = SPAWN[i], jx = (hash(i * 3.1) - 0.5) * 9;
  const mt = mouthPos(Math.max(0, ts + 0.13)); const h = mt[1] - NOZ.y; const th = ts + fallTime(h);
  const plan = { ts, jx, th, hitY: mt[1], hitX: mt[0], swallow: th < OVER + 0.05 && h > 20 };
  if (!plan.swallow) {
    const side = hash(i * 7.7) < 0.7 ? 1 : -1; plan.vx = side > 0 ? -(40 + 150 * hash(i * 5.3)) : 30 + 110 * hash(i * 5.3); plan.vy = -(120 + 260 * hash(i * 2.9));
    const yLand = FLOOR - 6 - 4 * hash(i); const dy = yLand - plan.hitY; plan.tl = (-plan.vy + Math.sqrt(plan.vy * plan.vy + 2 * G * dy)) / G;
    plan.xl = plan.hitX + plan.vx * plan.tl; plan.land = th + plan.tl;
  }
  coinCache.set(i, plan); return plan;
}
function coin(g, x, y, r, spin, a = 1) {
  const w = Math.max(0.25, Math.abs(Math.cos(spin)));
  g.save(); g.globalAlpha *= a; g.translate(x, y);
  const gr = g.createLinearGradient(0, -r, 0, r); gr.addColorStop(0, '#ffe2a0'); gr.addColorStop(0.5, '#f4b046'); gr.addColorStop(1, '#a8661c');
  g.fillStyle = gr; g.beginPath(); g.ellipse(0, 0, r * w, r, 0, 0, 7); g.fill();
  g.fillStyle = 'rgba(255,250,232,0.7)'; g.beginPath(); g.ellipse(-r * 0.25 * w, -r * 0.3, r * 0.35 * w, r * 0.22, 0, 0, 7); g.fill();
  g.restore();
}
function pileCount(t) { let n = 0; for (let i = 0; i < SPAWN.length; i++) { if (SPAWN[i] > t) break; const p = coinPlan(i); if (!p.swallow && p.land <= t) n++; } return n; }
const PILE_CX = 382;
function pileShape(n) { const k = Math.sqrt(n); return { w: Math.min(84, 12 + k * 5.2), h: Math.min(46, 4 + k * 2.4) }; }
function pile(g, t, refl = false) {
  const n = pileCount(t); if (n < 1) return;
  const { w, h } = pileShape(n);
  g.save();
  if (refl) { g.translate(0, 2 * FLOOR + 6); g.scale(1, -0.5); g.translate(0, -FLOOR); g.globalAlpha = 0.22; }
  // glow under the pile
  if (!refl) { g.save(); g.globalCompositeOperation = 'lighter'; const gr = g.createRadialGradient(PILE_CX, FLOOR - h * 0.3, 0, PILE_CX, FLOOR - h * 0.3, w * 1.5); gr.addColorStop(0, rgba(C.gold, 0.30)); gr.addColorStop(1, rgba(C.gold, 0)); g.fillStyle = gr; g.beginPath(); g.arc(PILE_CX, FLOOR - h * 0.3, w * 1.5, 0, 7); g.fill(); g.restore(); }
  const m = Math.min(n, 320);
  for (let k = 0; k < m; k++) {
    const u = (hash(k * 1.7) * 2 - 1), v = Math.sqrt(hash(k * 2.3)); const x = PILE_CX + u * w; const top = h * Math.pow(1 - u * u, 0.8); const y = FLOOR - 5 - top * v;
    const r = 6.2; g.save(); g.translate(x, y); g.scale(1, 0.45 + 0.25 * hash(k * 9.1)); coin(g, 0, 0, r, 0.3 * hash(k), 1); g.restore();
  }
  g.restore();
}
function coins(g, t) {
  g.save();
  const nozzleGlow = 0.6 + 0.4 * ss(VALVE, VALVE + 0.2, t);
  for (let i = 0; i < SPAWN.length; i++) {
    const ts = SPAWN[i]; if (ts > t) break; const p = coinPlan(i); const dt = t - ts; const spin = dt * (9 + 6 * hash(i)) + i;
    if (t < p.th) { const y = NOZ.y + V0 * dt + 0.5 * G * dt * dt; const x = NOZ.x + p.jx * (0.4 + dt * 3) + (p.hitX - NOZ.x) * clamp(dt / (p.th - p.ts)); coin(g, x, y, 5.8, spin); continue; }
    if (p.swallow) continue;
    if (t < p.land) { const d = t - p.th; coin(g, p.hitX + p.vx * d, p.hitY + p.vy * d + 0.5 * G * d * d, 5.8, spin * 1.6); }
  }
  glowDot(g, NOZ.x, NOZ.y + 6, 7, nozzleGlow);
  g.restore();
}

// ---------- the salary drip ----------
function drip(g, t) {
  for (let j = 0; j < DRIPS.length; j++) {
    const land = DRIPS[j], t0 = land - DRIP_FALL - 0.55, tf = land - DRIP_FALL;
    if (t < t0 || t > land + 0.02) continue;
    if (t < tf) { const k = (t - t0) / (tf - t0); coin(g, LEAK_X, PIPE_Y + PIPE_R + 3 + 3 * eio(k), 2 + 3.8 * eout(k), 1.2 + t * 2); glowDot(g, LEAK_X, PIPE_Y + PIPE_R + 5, 3, 0.4 * k); }
    else { const k = (t - tf) / DRIP_FALL, [hx, hy] = handPos(land); const x = lerp(LEAK_X, hx, k), y = lerp(PIPE_Y + PIPE_R + 6, hy - 6, k * k); coin(g, x, y, 5.8, t * 9); glowDot(g, x, y, 3.5, 0.7); }
  }
}
// employee pose: types; looks up and cups his hands for each drip; holds the coin, sets it down beside him
function empPose(t) {
  let p = TYPE, look = 0, hold = -1;
  for (let j = 0; j < DRIPS.length; j++) { const l = DRIPS[j]; const k = ss(l - 0.95, l - 0.55, t) * (1 - ss(l + 0.75, l + 1.1, t)); if (k > 0) { p = mix(TYPE, CUP, eio(k)); look = k; } if (t >= l && t < l + 0.95) hold = j; }
  return { p, look, hold };
}
function empO(t) { return { x: EX, y: FLOOR, dir: 1, s: 1, warm: false, typing: empPose(t).look < 0.2, laptop: true, glow: 0.55 + 0.35 * Math.max(0, Math.sin(t * 7)) * (1 - empPose(t).look) }; }
function handPos(t) { const { p } = empPose(t); const o = empO(t); return [o.x + (p.hd1[0] + p.hd2[0]) / 2 * o.s, o.y + (p.hd1[1] + p.hd2[1]) / 2 * o.s]; }
function salaryCount(t) { return DRIPS.filter(l => t >= l).length; }

// ---------- manager ----------
function managerPose(t) {
  // v3: he grows from frame 0. Same size as the employee at t=0, each gulp puffs him up a step, ~1.5x by 3 s.
  const tg = Math.max(0, t), gN = Math.floor(tg * 1.9), gF = (tg * 1.9) % 1, step = k => 0.72 * (1 - Math.exp(-k / 4));
  const grow = t < OVER ? lerp(step(gN), step(gN + 1), eout(clamp(gF / 0.35))) : step(Math.floor(OVER * 1.9) + 1) + 0.06 * ss(OVER, 6, t);
  const sM = 1.0 + grow;
  const o = { x: 521 - 38 * sM, y: SEAT, dir: -1, s: sM, warm: true, tie: true };
  // gulps: head bobs, mouth snaps
  const gph = (t * 1.9) % 1, gulp = t < OVER ? Math.exp(-gph * 7) : 0;
  let p = MSIT;
  const fk = ss(OVER, OVER + 0.25, t) * (1 - ss(FLAIL1 - 0.35, FLAIL1, t));
  if (fk > 0) {
    const fl = Object.assign({}, MFLAIL); const w = Math.sin((t - OVER) * 17), w2 = Math.sin((t - OVER) * 13 + 1);
    fl.hd1 = [fl.hd1[0] + 18 * w, fl.hd1[1] + 10 * w2]; fl.el1 = [fl.el1[0] + 8 * w, fl.el1[1] + 5 * w2];
    fl.hd2 = [fl.hd2[0] - 16 * w2, fl.hd2[1] + 12 * w]; fl.el2 = [fl.el2[0] - 6 * w2, fl.el2[1] + 5 * w];
    fl.head = [fl.head[0] + 6 * w2, fl.head[1]]; fl.sh = [fl.sh[0] + 4 * w2, fl.sh[1]];
    p = mix(MSIT, fl, eio(fk));
  }
  const sk = ss(FLAIL1 - 0.35, FLAIL1 + 0.2, t); if (sk > 0) p = mix(p, MSTUFF, sk);
  if (gulp > 0) { p = Object.assign({}, p); p.head = [p.head[0] + 2 * gulp, p.head[1] + 4 * gulp]; }
  o.mouth = t < OVER ? 0.75 + 0.25 * (1 - gulp) : lerp(0.35, 0.9, 0.5 + 0.5 * Math.sin(t * 11));
  o.belly = clamp(0.1 + 0.9 * grow / 0.5) * (1 + 0.15 * ss(OVER, 6, t));
  p = Object.assign({}, p); const fy = (FLOOR - SEAT - 4) / sM; p.ft1 = [p.ft1[0], fy]; p.ft2 = [p.ft2[0], fy];
  return [p, o];
}

// ---------- camera ----------
// slow push-in on the whole scene; for each salary drip it leans toward the employee and back.
function cam(t) {
  // floor lands at design y ~1000 (1500 px), pipe at ~385; push in slowly from frame 0
  let z = lerp(1.56, 1.64, eout(clamp(t / DUR))), cx = 384, cy = 610;
  for (const l of DRIPS) { const k = ss(l - 1.0, l - 0.35, t) * (1 - ss(l + 0.5, l + 1.2, t)); z = lerp(z, 1.68, k); cx = lerp(cx, 362, k); cy = lerp(cy, 604, k); }
  const shake = (t > OVER && t < FLAIL1) ? 1.6 * Math.sin(t * 41) : 0;
  return { z, cx: cx + shake, cy };
}
function sceneTf(t) { const k = W / DW, c = cam(t); return [k * c.z, 0, 0, k * c.z, k * (360 - c.cx * c.z), k * (640 - c.cy * c.z)]; }

function drawScene(g, t) {
  floor(g);
  // reflections on the glossy floor
  g.save(); g.beginPath(); g.rect(-60, FLOOR - 21, DW + 120, 60); g.clip();
  const [mp, mo] = managerPose(t), ep = empPose(t), eo = empO(t);
  drawFig(g, ep.p, Object.assign({}, eo, { reflect: true, alpha: 0.13, y: FLOOR + 10 }));
  pile(g, t, true);
  g.restore();
  hose(g, t);
  seatBox(g, t);
  pipe(g, t);
  pulses(g, t);
  drawFig(g, mp, mo);
  coins(g, t);
  pile(g, t);
  // the coins he has been paid sit beside him on the floor
  const n = salaryCount(t);
  for (let j = 0; j < n; j++) { const set = DRIPS[j] + 0.95; if (t < set) continue; coin(g, EX + 58 + j * 3, FLOOR - 7 - j * 4, 5.8, 0.15); glowDot(g, EX + 58, FLOOR - 9, 3, 0.35); }
  drawFig(g, ep.p, eo);
  if (ep.hold >= 0) { const [hx, hy] = handPos(t); coin(g, hx, hy - 6, 5.8, t * 3); glowDot(g, hx, hy - 6, 4.5, 0.9 * (0.75 + 0.25 * Math.sin(t * 8))); }
  drip(g, t);
  // labels in the scene (JetBrains, like WAITS / TEXTS FIRST)
  label(g, 'PROFIT', 262, PIPE_Y - 21, 12, 0.9 * (1 - ss(CTA_ON - 0.2, CTA_ON + 0.1, t)), 3, 700, 'center');
    sceneCounters(g, t);
  const lA = 1 - ss(CTA_ON - 0.2, CTA_ON + 0.1, t);
  const sa = ss(SALARY_ON, SALARY_ON + 0.3, t);
  if (sa > 0) { label(g, 'SALARY', LEAK_X + 16, PIPE_Y + 40, 12, 0.92 * sa, 3.5, 700, 'left', '214,224,244'); g.save(); g.globalAlpha = sa * 0.6; g.strokeStyle = 'rgba(214,224,244,0.8)'; g.lineWidth = 1.2; g.beginPath(); g.moveTo(LEAK_X + 15, PIPE_Y + 38); g.lineTo(LEAK_X + 4, PIPE_Y + 20); g.stroke(); g.restore(); }
}

// ---------- HUD (unzoomed, inside y 300-1440 at 1080x1920 = design 200-960) ----------
function fitFont(g, txt, weight, size, family, maxW) { g.font = `${weight} ${size}px "${family}"`; const w = g.measureText(txt).width; if (w > maxW) { size *= maxW / w; g.font = `${weight} ${size}px "${family}"`; } return size; }
function title(g, a, b, k, pop) {
  g.save(); g.textAlign = 'center'; g.textBaseline = 'alphabetic'; g.letterSpacing = '0.5px'; g.globalAlpha *= k;
  g.shadowColor = 'rgba(0,0,0,0.5)'; g.shadowBlur = 10;
  g.translate(360, 250); g.scale(pop, pop); g.translate(-360, -250);
  fitFont(g, a, 900, 56, 'Inter Display', 560); g.fillStyle = 'rgba(255,200,110,1)'; g.fillText(a, 360, 246);
  fitFont(g, b, 800, 36, 'Inter Display', 540); g.fillStyle = 'rgba(250,246,238,0.98)'; g.fillText(b, 360, 292);
  g.restore();
}
function fmt(n) { return n.toLocaleString('en-US'); }
function sceneCounters(g, t) {
  const you = salaryCount(t), them = 4180 + Math.round(SPAWN.filter(x => x <= t && x >= 0).length * 37);
  let b = 0; for (const l of DRIPS) if (t >= l) b = Math.max(b, Math.exp(-(t - l) * 5));
  // YOU GOT n, above the employee
  label(g, 'EMPLOYEE', EX + 6, 684, 13, 0.95, 2.5, 700, 'center', '214,224,244');
  g.save(); g.translate(EX + 6, 712); g.scale(1 + 0.45 * b, 1 + 0.45 * b); g.font = '700 26px "JetBrains Mono"'; g.textAlign = 'center'; g.fillStyle = b > 0.05 ? 'rgba(255,214,150,0.98)' : 'rgba(214,224,244,0.98)'; g.fillText(fmt(you), 0, 0); g.restore();
  // THEY GOT n, on the front of his seat
  label(g, 'MANAGEMENT', (BOX.x0 + BOX.x1) / 2 + 10, 776, 13, 0.95, 2.5, 700, 'center');
  g.save(); g.font = '700 26px "JetBrains Mono"'; g.textAlign = 'center'; g.shadowColor = rgba(C.gold, 0.7); g.shadowBlur = 8 * W / DW; g.fillStyle = 'rgba(255,214,150,0.98)'; g.fillText(fmt(them), (BOX.x0 + BOX.x1) / 2 + 10, 803); g.restore();
}
function frame(g, t) {
  T = t;
  g.setTransform(W / DW, 0, 0, H / DH, 0, 0); background(g, t);
  g.setTransform(...sceneTf(t));
  drawScene(g, t);
  g.setTransform(W / DW, 0, 0, H / DH, 0, 0);
  // hook -> end lines
  const swap = ss(END_TXT - 0.15, END_TXT, t), pop = 1 + 0.12 * Math.exp(-Math.max(0, t - END_TXT) * 9) * (t >= END_TXT ? 1 : 0);
  if (swap < 1) title(g, 'YOU FILL THE PIPE.', 'GUESS WHO DRINKS FROM IT?', 1 - swap, 1);
  if (swap > 0) title(g, 'YOU GET THE DRIPS.', 'THEY GET THE FLOOD.', swap, pop);
  const ca = ss(CTA_ON, CTA_ON + 0.3, t);
  if (ca > 0) { g.save(); g.globalAlpha = ca; g.font = '700 26px "Inter"'; g.textAlign = 'center'; g.fillStyle = 'rgba(250,246,238,0.95)'; g.fillText('Send this to the coworker', 300, 540); g.fillText('who fills the pipe 💛', 300, 576); g.restore(); }
  label(g, 'SLOW LIGHT', 360, 1270, 11, 0.28, 5, 600, 'center');
}

window.renderAt = (t, sub = 1) => {
  sub = Math.max(1, sub | 0);
  if (sub === 1) { frame(out, t); }
  else {
    out.setTransform(1, 0, 0, 1, 0, 0); out.fillStyle = '#000'; out.fillRect(0, 0, W, H);
    for (let i = 0; i < sub; i++) {
      A.setTransform(1, 0, 0, 1, 0, 0); frame(A, t + (i / sub - 0.5) * (1 / 30) * 0.5);
      out.setTransform(1, 0, 0, 1, 0, 0); out.globalCompositeOperation = 'lighter'; out.globalAlpha = 1 / sub; out.drawImage(acc, 0, 0);
    }
    out.globalCompositeOperation = 'source-over'; out.globalAlpha = 1;
  }
  return cv.toDataURL('image/jpeg', 0.95);
};

// sound cues for mix.py (beds are built in mix.py from the same timeline)
window.events = (() => {
  const e = [];
  e.push({ t: VALVE - 0.05, s: 'clunk', g: 0.8, pan: 0.05 });
  for (let tg = 0.0; tg < OVER; tg += 1 / 1.9) e.push({ t: tg + 0.02, s: 'gulp', g: 0.42, pan: 0.45, rate: 0.95 + 0.1 * hash(tg * 10) });
  e.push({ t: OVER, s: 'choke', g: 0.85, pan: 0.45 });
  e.push({ t: OVER + 0.25, s: 'pile', g: 0.6, pan: 0.4 }, { t: OVER + 3.5, s: 'pile', g: 0.5, pan: 0.45, rate: 0.95 });
  for (const l of DRIPS) e.push({ t: l, s: 'tink', g: 0.95, pan: -0.45 });
  e.push({ t: END_TXT - 0.1, s: 'swell', g: 0.6, pan: 0 });
  return e.sort((a, b) => a.t - b.t);
})();
window.TL = { VALVE, OVER, FLAIL1, DRIPS, END_TXT, DUR };
window.DUR = DUR;
document.fonts.load('600 20px "JetBrains Mono"').then(() => document.fonts.load('700 26px "JetBrains Mono"')).then(() => document.fonts.load('900 56px "Inter Display"')).then(() => { window.ready = true; });
