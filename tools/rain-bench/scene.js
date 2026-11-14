// Sit In The Rain - Slow Light remake of the "sit beside you until it passes" rain-bench stickman reel.
// Same look as Silence Is Distance (tools/silence-distance): dark glossy gradient, cream/gold warmth vs cool grey.
// Canvas 2D in the ref's 720x1280 design space. window.renderAt(t, sub) -> JPEG; window.events -> sound cues.
'use strict';
const DW = 720, DH = 1280, DUR = 10.0;
const qs = new URLSearchParams(location.search);
const W = +(qs.get('w') || 1080), H = +(qs.get('h') || 1920);
const cv = document.createElement('canvas'); cv.width = W; cv.height = H; document.body.appendChild(cv);
const out = cv.getContext('2d');
const acc = document.createElement('canvas'); acc.width = W; acc.height = H;
const A = acc.getContext('2d');

const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, k) => a + (b - a) * k;
const ss = (a, b, x) => { const k = clamp((x - a) / (b - a)); return k * k * (3 - 2 * k); };
const eio = k => k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
const eout = k => 1 - Math.pow(1 - k, 3);
function hash(i) { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }
const rgba = (c, a) => `rgba(${c[0] | 0},${c[1] | 0},${c[2] | 0},${a})`;
const mixc = (a, b, k) => [lerp(a[0], b[0], k), lerp(a[1], b[1], k), lerp(a[2], b[2], k)];
const GOLD = [255, 190, 92], GOLDH = [255, 232, 180];
const CREAM = [255, 247, 234], CREAMF = [165, 157, 146], GREY = [146, 154, 168], GREYF = [96, 103, 116];

// ---------- layout (design px) ----------
const GY = 930, S = 2.0;           // ground line, figure scale (ref figures are ~2x the Silence ones)
const SEAT = GY - 50 * S;          // bench seat top
const SADX = 300, FRX = 420;       // seated x of the sad one and the friend
const CL = { x0: 125, x1: 595, y: 455 }; // cloud

// ---------- poses (front view unless noted; units at S=1, ground y=0) ----------
const K = ['head', 'sh', 'hip', 'kn1', 'ft1', 'kn2', 'ft2', 'el1', 'hd1', 'el2', 'hd2'];
const mix = (a, b, k) => { const o = {}; for (const n of K) o[n] = [lerp(a[n][0], b[n][0], k), lerp(a[n][1], b[n][1], k)]; return o; };
const LEGS = { hip: [0, -52], kn1: [16, -47], ft1: [16, -6], kn2: [-16, -47], ft2: [-16, -6] };
const FSTAND = { head: [0, -161], sh: [0, -137], hip: [0, -81], kn1: [7, -42], ft1: [9, -6], kn2: [-7, -42], ft2: [-9, -6], el1: [13, -109], hd1: [15, -83], el2: [-13, -109], hd2: [-15, -83] };
const FSIT = Object.assign({ head: [0, -130], sh: [0, -106], el1: [17, -80], hd1: [12, -54], el2: [-17, -80], hd2: [-12, -54] }, LEGS);
const SAD = Object.assign({ head: [0, -100], sh: [0, -93], el1: [12, -50], hd1: [6, -92], el2: [-12, -50], hd2: [-6, -92] }, LEGS);
const SADUP = Object.assign({ head: [3, -116], sh: [1, -100], el1: [13, -68], hd1: [8, -54], el2: [-13, -68], hd2: [-8, -54] }, LEGS);
const SADLEAN = Object.assign({ head: [27, -115], sh: [10, -100], el1: [24, -74], hd1: [26, -54], el2: [-8, -72], hd2: [2, -54] }, LEGS);
const ARM = Object.assign({ head: [-7, -129], sh: [0, -106], el1: [16, -80], hd1: [11, -54], el2: [-30, -104], hd2: [-68, -94] }, LEGS);
const ARMTILT = Object.assign({}, ARM, { head: [-12, -137] });
function walk(ph) { // profile walk facing +x
  const o = {};
  const leg = (p) => { const a = 0.42 * Math.sin(p); const bend = 0.75 * clamp(Math.sin(p - 1.1), 0, 1);
    const kn = [40 * Math.sin(a), 40 * Math.cos(a)]; const b = a - bend; return [kn, [kn[0] + 36 * Math.sin(b), kn[1] + 36 * Math.cos(b)]]; };
  const [k1, f1] = leg(ph), [k2, f2] = leg(ph + Math.PI); const hy = -Math.max(f1[1], f2[1]) - 6;
  o.hip = [0, hy]; o.sh = [2, hy - 56]; o.head = [3, hy - 80];
  o.kn1 = [k1[0], hy + k1[1]]; o.ft1 = [f1[0], hy + f1[1]]; o.kn2 = [k2[0], hy + k2[1]]; o.ft2 = [f2[0], hy + f2[1]];
  const arm = (p) => { const a = -0.38 * Math.sin(p); const el = [2 + 27 * Math.sin(a), hy - 56 + 27 * Math.cos(a)]; const b = a + 0.35 + 0.2 * Math.max(0, -Math.sin(p)); return [el, [el[0] + 25 * Math.sin(b), el[1] + 25 * Math.cos(b)]]; };
  const [e1, h1] = arm(ph), [e2, h2] = arm(ph + Math.PI); o.el1 = e1; o.hd1 = h1; o.el2 = e2; o.hd2 = h2;
  return o;
}

let T = 0;
function drawFig(g, pose, o) { // o: x, y, dir, s, near, far (rgb), glow (rgba string), alpha, reflect
  const s = o.s, d = o.dir;
  const b = (o.breath ?? 1) * Math.sin(T * 2.2 + o.x * 0.05) * 1.2; pose = Object.assign({}, pose);
  for (const n of ['head', 'sh']) pose[n] = [pose[n][0] + (o.shiver || 0) * Math.sin(T * 47 + n.length), pose[n][1] + b];
  for (const n of ['el1', 'el2', 'hd1', 'hd2']) pose[n] = [pose[n][0], pose[n][1] + b * 0.5];
  const X = p => o.x + p[0] * d * s, Y = p => o.y + p[1] * s * (o.reflect ? -0.5 : 1);
  g.save(); g.globalAlpha = o.alpha ?? 1; g.lineCap = 'round'; g.lineJoin = 'round';
  const lw = 11.5 * s, near = rgba(o.near, 1), far = rgba(o.far, 1);
  const seg = (pts, col, w) => { g.strokeStyle = col; g.lineWidth = w; g.beginPath(); g.moveTo(X(pts[0]), Y(pts[0])); for (let i = 1; i < pts.length; i++) g.lineTo(X(pts[i]), Y(pts[i])); g.stroke(); };
  if (!o.reflect) { g.shadowColor = o.glow; g.shadowBlur = 10 * s * (W / DW); }
  seg([pose.hip, pose.kn2, pose.ft2], far, lw);
  if (!o.armFront) seg([pose.sh, pose.el2, pose.hd2], far, lw * 0.92);
  seg([pose.sh, pose.hip], near, lw * 1.05);
  seg([pose.hip, pose.kn1, pose.ft1], near, lw);
  seg([pose.sh, pose.el1, pose.hd1], near, lw * 0.92);
  g.fillStyle = near; g.beginPath(); g.arc(X(pose.head), Y(pose.head), 14.5 * s, 0, 7); g.fill();
  g.restore();
  return { X, Y, pose };
}
function drawArm(g, pose, o) { // the arm around the shoulders, drawn over the other person
  const s = o.s, d = o.dir, X = p => o.x + p[0] * d * s, Y = p => o.y + p[1] * s;
  g.save(); g.lineCap = 'round'; g.lineJoin = 'round'; g.shadowColor = o.glow; g.shadowBlur = 10 * s * (W / DW);
  g.strokeStyle = rgba(o.near, 1); g.lineWidth = 11.5 * s * 0.92; g.beginPath(); g.moveTo(X(pose.sh), Y(pose.sh)); g.lineTo(X(pose.el2), Y(pose.el2)); g.lineTo(X(pose.hd2), Y(pose.hd2)); g.stroke();
  g.restore();
}

// ---------- timeline ----------
const WALK0 = 0, WALK1 = 1.55, TURN1 = 1.85, SIT0 = 1.95, SIT1 = 2.65, ARM0 = 3.7, ARM1 = 4.5, UP0 = 4.7, UP1 = 5.2, LEAN0 = 5.6, LEAN1 = 6.5, TXT2 = 6.9;
const FR_START = 655, FR_STOP = 478;
function friendAt(t) {
  if (t < WALK1) { const k = t / WALK1; const x = lerp(FR_START, FR_STOP, k * (1.15 - 0.15 * k)); const amp = 1 - ss(0.8, 1, k);
    return { pose: mix(FSTAND, walk(t * 10.5), amp * 0.999 + 0.001), x, dir: -1 }; }
  if (t < SIT0) return { pose: FSTAND, x: FR_STOP, dir: -1 };
  if (t < SIT1) { const k = eio(clamp((t - SIT0) / (SIT1 - SIT0))); return { pose: mix(FSTAND, FSIT, k), x: lerp(FR_STOP, FRX, k), dir: 1 }; }
  if (t < ARM0) return { pose: FSIT, x: FRX, dir: 1 };
  if (t < LEAN0) return { pose: mix(FSIT, ARM, eio(clamp((t - ARM0) / (ARM1 - ARM0)))), x: FRX, dir: 1, arm: true };
  return { pose: mix(ARM, ARMTILT, eio(clamp((t - LEAN0 - 0.3) / 0.8))), x: FRX, dir: 1, arm: true };
}
function sadAt(t) {
  let p = SAD;
  if (t >= UP0) p = mix(SAD, SADUP, eio(clamp((t - UP0) / (UP1 - UP0))));
  if (t >= LEAN0) p = mix(SADUP, SADLEAN, eio(clamp((t - LEAN0) / (LEAN1 - LEAN0))));
  return p;
}
const warmth = t => ss(4.4, 7.2, t); // how much colour the sad one has got back

// ---------- scene pieces ----------
function background(g, t, flash) {
  let gr = g.createLinearGradient(0, 0, 0, DH);
  gr.addColorStop(0, '#191b24'); gr.addColorStop(0.5, '#111219'); gr.addColorStop(1, '#16171f');
  g.fillStyle = gr; g.fillRect(0, 0, DW, DH);
  gr = g.createRadialGradient(360, 720, 10, 360, 720, 520); gr.addColorStop(0, 'rgba(120,150,210,0.07)'); gr.addColorStop(1, 'rgba(120,150,210,0)');
  g.fillStyle = gr; g.fillRect(0, 0, DW, DH);
  gr = g.createLinearGradient(0, 0, DW, DH * 0.6);
  gr.addColorStop(0.25, 'rgba(255,255,255,0)'); gr.addColorStop(0.42, 'rgba(255,255,255,0.025)'); gr.addColorStop(0.6, 'rgba(255,255,255,0)');
  g.fillStyle = gr; g.fillRect(0, 0, DW, DH);
  if (flash > 0) { g.fillStyle = `rgba(200,215,255,${0.10 * flash})`; g.fillRect(0, 0, DW, DH); }
}
function cloud(g, t, flash) {
  const bob = Math.sin(t * 1.1) * 3; const cy = CL.y + bob;
  g.save(); g.translate(360, cy); g.scale(1.25, 1.0); g.translate(-360, -cy);
  const puffs = [[200, 18, 40], [245, -8, 52], [300, -30, 62], [360, -40, 70], [420, -26, 60], [475, -6, 52], [520, 16, 40], [270, 22, 46], [450, 22, 46], [360, 18, 52]];
  g.save();
  g.shadowColor = 'rgba(0,0,0,0.55)'; g.shadowBlur = 24 * W / DW; g.shadowOffsetY = 10 * W / DW;
  const gr = g.createLinearGradient(0, cy - 110, 0, cy + 70);
  gr.addColorStop(0, `rgb(${92 + 90 * flash},${96 + 92 * flash},${108 + 100 * flash})`); gr.addColorStop(0.55, `rgb(${58 + 70 * flash},${61 + 72 * flash},${71 + 80 * flash})`); gr.addColorStop(1, '#2d2f37');
  g.fillStyle = gr; g.beginPath();
  for (const [x, y, r] of puffs) { g.moveTo(x + r, cy + y); g.arc(x, cy + y, r, 0, 7); }
  g.roundRect(CL.x0 + 10, cy + 10, CL.x1 - CL.x0 - 20, 54, 27); g.fill();
  g.restore();
  // glossy top highlights
  g.save(); g.globalCompositeOperation = 'lighter';
  for (const [x, y, r] of puffs.slice(0, 7)) { const hg = g.createRadialGradient(x - r * 0.25, cy + y - r * 0.55, 0, x - r * 0.25, cy + y - r * 0.55, r * 0.7); hg.addColorStop(0, `rgba(210,220,240,${0.10 + 0.25 * flash})`); hg.addColorStop(1, 'rgba(210,220,240,0)'); g.fillStyle = hg; g.fillRect(x - r, cy + y - r, 2 * r, 2 * r); }
  if (flash > 0) { const fg = g.createRadialGradient(330, cy, 0, 330, cy, 220); fg.addColorStop(0, `rgba(220,230,255,${0.55 * flash})`); fg.addColorStop(1, 'rgba(220,230,255,0)'); g.fillStyle = fg; g.fillRect(100, cy - 220, 500, 440); }
  g.restore(); g.restore();
  return cy;
}
function bench(g, front) {
  const x0 = 190, x1 = 530;
  g.save();
  const plank = (y, h, a) => { const gr = g.createLinearGradient(0, y, 0, y + h); gr.addColorStop(0, `rgba(118,112,104,${a})`); gr.addColorStop(0.4, `rgba(74,70,66,${a})`); gr.addColorStop(1, `rgba(40,38,38,${a})`);
    g.fillStyle = gr; g.beginPath(); g.roundRect(x0, y, x1 - x0, h, 4); g.fill(); g.fillStyle = `rgba(255,240,220,${0.28 * a})`; g.fillRect(x0 + 4, y + 1, x1 - x0 - 8, 1.6); };
  if (!front) { // back legs, backrest
    g.fillStyle = '#2a2a2f'; for (const x of [x0 + 16, x1 - 22]) g.fillRect(x, SEAT - 96, 7, 96 + (GY - SEAT));
    plank(SEAT - 96, 20, 1); plank(SEAT - 66, 20, 1); plank(SEAT - 2, 16, 1);
  } else { // seat and front legs over the hips
    g.fillStyle = '#34343a'; for (const x of [x0 + 26, x1 - 32]) g.fillRect(x, SEAT + 10, 8, GY - SEAT - 10);
    g.fillStyle = 'rgba(255,240,220,0.18)'; g.fillRect(x0 + 4, SEAT + 13, x1 - x0 - 8, 1.4);
  }
  g.restore();
}
function ground(g) {
  let gr = g.createLinearGradient(0, GY - 6, 0, GY + 150);
  gr.addColorStop(0, 'rgba(70,74,86,0.85)'); gr.addColorStop(0.12, 'rgba(40,43,52,0.75)'); gr.addColorStop(1, 'rgba(22,23,31,0)');
  g.fillStyle = gr; g.fillRect(0, GY - 6, DW, 160);
  g.fillStyle = 'rgba(220,230,255,0.22)'; g.fillRect(0, GY - 6, DW, 1.2);
}
// rain: drops fall from the cloud to the ground. layer 0 behind the figures, 1 in front.
function rain(g, t, cy, layer, warmX, warmK) {
  g.save(); g.lineCap = 'round';
  const N = 150, top = cy + 50;
  for (let i = layer; i < N; i += 2) {
    const x = CL.x0 + 22 + hash(i) * (CL.x1 - CL.x0 - 44), sp = 760 + 260 * hash(i + 3), len = 18 + 18 * hash(i + 5);
    const span = GY - top + 40; const y = top + ((t * sp + hash(i + 7) * span) % span);
    if (y > GY) continue;
    const near = Math.max(0, 1 - Math.abs(x - warmX) / 95) * warmK;
    const c = mixc([170, 185, 215], GOLD, near), a = (layer ? 0.55 : 0.32) * ss(top, top + 30, y);
    g.strokeStyle = rgba(c, a + 0.25 * near); g.lineWidth = layer ? 1.6 : 1.2;
    g.beginPath(); g.moveTo(x - 2, y - len); g.lineTo(x, y); g.stroke();
  }
  // splashes on the ground
  for (let i = layer; i < 40; i += 2) {
    const x = CL.x0 + 10 + hash(i + 40) * (CL.x1 - CL.x0 - 20), ph = (t * 1.7 + hash(i + 50)) % 1;
    g.strokeStyle = `rgba(190,205,235,${0.35 * (1 - ph)})`; g.lineWidth = 1;
    g.beginPath(); g.ellipse(x, GY + 6 + hash(i + 60) * 30, 3 + 16 * ph, (3 + 16 * ph) * 0.25, 0, 0, 7); g.stroke();
  }
  g.restore();
}
function motes(g, t) {
  for (let i = 0; i < 40; i++) {
    const x = (hash(i) * DW + t * (4 + 8 * hash(i + 9))) % DW, y = 140 + hash(i + 3) * 1000 - t * (3 + 5 * hash(i + 5));
    g.fillStyle = `rgba(255,240,215,${0.08 + 0.14 * hash(i + 7)})`; g.beginPath(); g.arc(x, y, 0.6 + 1.1 * hash(i + 11), 0, 7); g.fill();
  }
}
function fitText(g, txt, maxW, size, weight) { let s = size; g.font = `${weight} ${s}px "Inter Display"`; while (g.measureText(txt).width > maxW && s > 12) { s -= 1; g.font = `${weight} ${s}px "Inter Display"`; } return s; }
function titles(g, t) {
  const a1 = 1 - ss(TXT2 - 0.25, TXT2, t), a2 = ss(TXT2, TXT2 + 0.35, t);
  const line = (txt, y, size, weight, col, a) => { if (a <= 0.01) return; g.save(); g.textAlign = 'center'; g.textBaseline = 'alphabetic';
    fitText(g, txt, 560, size, weight); g.letterSpacing = '0.5px'; g.shadowColor = 'rgba(0,0,0,0.55)'; g.shadowBlur = 10; g.fillStyle = col; g.globalAlpha = a; g.fillText(txt, 360, y); g.restore(); };
  line("THEY CAN'T STOP YOUR RAIN.", 236, 46, 900, 'rgb(255,200,110)', a1);
  line("BUT THEY'LL SIT IN IT WITH YOU.", 286, 34, 800, 'rgba(250,246,238,0.98)', a1);
  line('TAG THE ONE WHO', 236, 34, 800, 'rgba(250,246,238,0.98)', a2);
  line('SAT IN YOUR RAIN 💛', 288, 48, 900, 'rgb(255,200,110)', a2);
  g.save(); g.textAlign = 'center'; g.font = '600 11px "JetBrains Mono"'; g.letterSpacing = '5px'; g.fillStyle = 'rgba(242,238,230,0.26)'; g.fillText('SLOW LIGHT', 360, 1010); g.restore();
}

// ---------- frame ----------
function frame(g, t) {
  T = t; const k = W / DW;
  const flash = Math.exp(-Math.pow((t - 0.16) / 0.06, 2)) + 0.5 * Math.exp(-Math.pow((t - 0.34) / 0.05, 2));
  g.setTransform(k, 0, 0, k, 0, 0);
  background(g, t, flash);
  // slow push-in about the bench, plus a small punch on the lightning
  const Z = 1 + 0.07 * eout(clamp(t / DUR)) + 0.012 * flash, PX = 360, PY = 760;
  g.setTransform(k * Z, 0, 0, k * Z, k * (PX - PX * Z), k * (PY - PY * Z));
  motes(g, t);
  const cy = cloud(g, t, flash);
  const fr = friendAt(t), sp = sadAt(t), wk = warmth(t);
  const sadNear = mixc(GREY, CREAM, wk), sadFar = mixc(GREYF, CREAMF, wk);
  const sadO = { x: SADX, y: GY, dir: 1, s: S, near: sadNear, far: sadFar, glow: wk > 0.3 ? `rgba(255,214,160,${0.42 * wk})` : 'rgba(190,210,255,0.25)', shiver: 1.4 * (1 - ss(4.0, 5.2, t)), breath: 1.6 };
  const frO = { x: fr.x, y: GY, dir: fr.dir, s: S, near: CREAM, far: CREAMF, glow: 'rgba(255,214,160,0.45)', armFront: fr.arm };
  // warm light gathering around the friend once seated
  const warmK = ss(SIT1, SIT1 + 0.8, t);
  if (warmK > 0) { g.save(); g.globalCompositeOperation = 'lighter'; const cx = lerp(FRX, (FRX + SADX) / 2, wk), r = 150 + 90 * wk;
    const gr = g.createRadialGradient(cx, GY - 130, 0, cx, GY - 130, r); gr.addColorStop(0, rgba(GOLD, 0.16 * warmK)); gr.addColorStop(1, rgba(GOLD, 0)); g.fillStyle = gr; g.fillRect(cx - r, GY - 130 - r, 2 * r, 2 * r); g.restore(); }
  ground(g);
  // reflections on the wet ground
  g.save(); g.beginPath(); g.rect(0, GY - 4, DW, 140); g.clip();
  drawFig(g, sp, Object.assign({}, sadO, { reflect: true, alpha: 0.07, y: GY + 4 })); drawFig(g, fr.pose, Object.assign({}, frO, { reflect: true, alpha: 0.07, y: GY + 4 }));
  g.restore();
  rain(g, t, cy, 0, FRX, warmK);
  bench(g, false);
  if (fr.arm) drawArm(g, fr.pose, frO); // around his back, behind his head
  drawFig(g, sp, sadO);
  drawFig(g, fr.pose, frO);
  bench(g, true);
  rain(g, t, cy, 1, FRX, warmK);
  g.setTransform(k, 0, 0, k, 0, 0);
  titles(g, t);
}

window.renderAt = (t, sub = 1) => {
  sub = Math.max(1, sub | 0);
  if (sub === 1) frame(out, t);
  else {
    out.setTransform(1, 0, 0, 1, 0, 0); out.fillStyle = '#000'; out.fillRect(0, 0, W, H);
    for (let i = 0; i < sub; i++) { frame(A, t + (i / sub - 0.5) / 60); out.setTransform(1, 0, 0, 1, 0, 0); out.globalCompositeOperation = 'lighter'; out.globalAlpha = 1 / sub; out.drawImage(acc, 0, 0); }
    out.globalCompositeOperation = 'source-over'; out.globalAlpha = 1;
  }
  return cv.toDataURL('image/jpeg', 0.95);
};
window.events = (() => {
  const e = [{ t: 0.0, s: 'thunder', g: 0.9, pan: 0 }];
  for (let i = 0; i < 6; i++) { const ts = 0.12 + i * (Math.PI / 10.5) * 0.98; if (ts < WALK1) e.push({ t: ts, s: 'wetstep', g: 0.5, pan: 0.6 - i * 0.08 }); }
  e.push({ t: SIT0 + 0.45, s: 'creak', g: 0.7, pan: 0.15 }, { t: ARM0 + 0.1, s: 'lean', g: 0.7, pan: 0 }, { t: UP0 + 0.1, s: 'exhale', g: 0.55, pan: -0.15 }, { t: LEAN0 + 0.2, s: 'swell', g: 0.55, pan: 0 });
  return e;
})();
window.DUR = DUR;
document.fonts.load('900 40px "Inter Display"').then(() => document.fonts.load('600 20px "JetBrains Mono"')).then(() => { window.ready = true; });
