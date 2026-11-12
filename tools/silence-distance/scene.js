// Silence Is Distance - Slow Light remake of the "texts first / waits" split-screen stickman reel.
// Canvas 2D. Design space is the reference's 720x1280; everything is scaled to the render size.
// window.renderAt(t, sub) -> JPEG data URL. window.events -> sound cue list (used by mix.py).
'use strict';
const DW = 720, DH = 1280, DUR = 12.1;
// v2 hook: output time -> scene time. Starts mid-typing and plays the opening 1.3x, so the first text fires at 0.15 s.
const WARP = [[0, 0.3], [1.3, 2.0], [11.4, 12.1]];
const warp = t => pw(t, WARP), unwarp = s => pw(s, WARP.map(([a, b]) => [b, a]));
const OUT_DUR = 11.4;
// v3: everything below the background moves down so the hook clears the Reels account-name bar.
const SHIFT = 110;
// v4: tighter crop + a slow push-in from frame 0. Content scales about (360, ZP) in design px.
const ZP = 180; let ZC = 1.13, T = 0;
const zoomAt = to => lerp(1.08, 1.16, eout(clamp(to / 2.2)));
const contentTf = () => { const k = W / DW, Z = ZC; return [k * Z, 0, 0, k * Z, k * (360 - 360 * Z), k * (ZP + (SHIFT - ZP) * Z)]; };
const qs = new URLSearchParams(location.search);
const W = +(qs.get('w') || 1080), H = +(qs.get('h') || 1920);
const cv = document.createElement('canvas'); cv.width = W; cv.height = H; document.body.appendChild(cv);
const out = cv.getContext('2d');
const layer = document.createElement('canvas'); layer.width = W; layer.height = H;
const L = layer.getContext('2d');
const acc = document.createElement('canvas'); acc.width = W; acc.height = H;
const A = acc.getContext('2d');

// ---------- helpers ----------
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, k) => a + (b - a) * k;
const ss = (a, b, x) => { const k = clamp((x - a) / (b - a)); return k * k * (3 - 2 * k); };
const eio = k => k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
const eout = k => 1 - Math.pow(1 - k, 3);
const pw = (t, keys) => { // piecewise linear [[t,v]...]
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) if (t <= keys[i][0]) { const [t0, v0] = keys[i - 1], [t1, v1] = keys[i]; return lerp(v0, v1, (t - t0) / (t1 - t0)); }
  return keys[keys.length - 1][1];
};
function hash(i) { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }

// ---------- palette (Slow Light) ----------
const C = {
  bgTop: '#191b24', bgMid: '#111219', bgBot: '#16171f',
  gold: [255, 190, 92], goldHot: [255, 232, 180],
  figWarm: '#fff7ea', farWarm: '#a59d92',
  figCool: '#dfe4ee', farCool: '#8a909c',
};
const rgba = (c, a) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;

// ---------- poses (local px, facing +x, ground y = 0) ----------
const K = ['head', 'sh', 'hip', 'kn1', 'ft1', 'kn2', 'ft2', 'el1', 'hd1', 'el2', 'hd2'];
const P = (o) => o;
const SIT = P({ head: [0, -88], sh: [-9, -64], hip: [-16, -9], kn1: [14, -40], ft1: [27, -6], kn2: [10, -38], ft2: [22, -6], el1: [4, -40], hd1: [16, -50], el2: [1, -39], hd2: [13, -49] });
const SLUMP = P({ head: [10, -72], sh: [-3, -56], hip: [-16, -9], kn1: [14, -40], ft1: [27, -6], kn2: [10, -38], ft2: [22, -6], el1: [8, -34], hd1: [18, -44], el2: [5, -33], hd2: [15, -43] });
const CROUCH = P({ head: [12, -122], sh: [5, -98], hip: [-13, -46], kn1: [17, -44], ft1: [11, -6], kn2: [13, -43], ft2: [6, -6], el1: [22, -80], hd1: [36, -74], el2: [18, -80], hd2: [32, -73] });
const STAND = P({ head: [0, -161], sh: [0, -137], hip: [0, -81], kn1: [2, -42], ft1: [3, -6], kn2: [-2, -42], ft2: [-3, -6], el1: [4, -109], hd1: [6, -83], el2: [-4, -109], hd2: [-6, -83] });
const HOLD = P({ head: [1, -161], sh: [0, -137], hip: [0, -81], kn1: [2, -42], ft1: [3, -6], kn2: [-2, -42], ft2: [-3, -6], el1: [14, -113], hd1: [27, -97], el2: [11, -111], hd2: [25, -95] });
function mix(a, b, k) { const o = {}; for (const n of K) o[n] = [lerp(a[n][0], b[n][0], k), lerp(a[n][1], b[n][1], k)]; return o; }
function walk(ph) { // procedural walk, ph in radians
  const o = {}; const s = Math.sin(ph);
  const leg = (p) => { const a = 0.42 * Math.sin(p); const bend = 0.75 * clamp(Math.sin(p - 1.1), 0, 1);
    const kn = [40 * Math.sin(a), 40 * Math.cos(a)]; const b = a - bend; const ft = [kn[0] + 36 * Math.sin(b), kn[1] + 36 * Math.cos(b)]; return [kn, ft]; };
  const [k1, f1] = leg(ph), [k2, f2] = leg(ph + Math.PI);
  const drop = Math.max(f1[1], f2[1]); const hy = -drop - 6; // lowest foot touches ground
  o.hip = [0, hy]; o.sh = [2, hy - 56]; o.head = [3, hy - 80];
  o.kn1 = [k1[0], hy + k1[1]]; o.ft1 = [f1[0], hy + f1[1]]; o.kn2 = [k2[0], hy + k2[1]]; o.ft2 = [f2[0], hy + f2[1]];
  const arm = (p) => { const a = -0.38 * Math.sin(p); const el = [2 + 27 * Math.sin(a), hy - 56 + 27 * Math.cos(a)]; const b = a + 0.35 + 0.2 * Math.max(0, -Math.sin(p)); return [el, [el[0] + 25 * Math.sin(b), el[1] + 25 * Math.cos(b)]]; };
  const [e1, h1] = arm(ph), [e2, h2] = arm(ph + Math.PI); o.el1 = e1; o.hd1 = h1; o.el2 = e2; o.hd2 = h2;
  return o;
}

// ---------- figure ----------
function drawFig(g, pose, o) {
  // o: x, y (ground), dir, s (scale), warm(bool), pony(bool), phone (0..1 glow), alpha, reflect(bool)
  const s = o.s, d = o.dir;
  { const b = Math.sin(T * 2.4 + o.x * 0.05) * 1.3, ty = Math.sin(T * 14 + o.x) * 0.8; pose = Object.assign({}, pose);
    for (const n of ['head', 'sh']) pose[n] = [pose[n][0], pose[n][1] + b];
    for (const n of ['el1', 'el2']) pose[n] = [pose[n][0], pose[n][1] + b * 0.6];
    for (const n of ['hd1', 'hd2']) pose[n] = [pose[n][0], pose[n][1] + b * 0.5 + (o.phone > 0 ? ty : 0)]; }
  const X = p => o.x + p[0] * d * s, Y = p => o.y + p[1] * s * (o.reflect ? -0.55 : 1);
  const near = o.warm ? C.figWarm : C.figCool, far = o.warm ? C.farWarm : C.farCool;
  g.save(); g.globalAlpha = o.alpha ?? 1; g.lineCap = 'round'; g.lineJoin = 'round';
  const lw = 11.5 * s;
  const seg = (pts, col, w) => { g.strokeStyle = col; g.lineWidth = w; g.beginPath(); g.moveTo(X(pts[0]), Y(pts[0])); for (let i = 1; i < pts.length; i++) g.lineTo(X(pts[i]), Y(pts[i])); g.stroke(); };
  if (!o.reflect) { g.shadowColor = o.warm ? 'rgba(255,214,160,0.42)' : 'rgba(190,210,255,0.35)'; g.shadowBlur = 9 * s * (W / DW); }
  seg([pose.hip, pose.kn2, pose.ft2], far, lw);
  seg([pose.sh, pose.el2, pose.hd2], far, lw * 0.92);
  seg([pose.sh, pose.hip], near, lw * 1.05);
  seg([pose.hip, pose.kn1, pose.ft1], near, lw);
  // phone between the hands
  if (o.phone > 0 && !o.reflect) {
    const hx = (X(pose.hd1) + X(pose.hd2)) / 2, hy = (Y(pose.hd1) + Y(pose.hd2)) / 2;
    g.save(); g.shadowBlur = 0; g.translate(hx, hy); g.rotate(-0.5 * d);
    g.fillStyle = '#2a2a30'; g.beginPath(); g.roundRect(-5 * s, -8 * s, 10 * s, 16 * s, 2.5 * s); g.fill();
    g.fillStyle = rgba(C.goldHot, 0.35 + 0.65 * o.phone); g.beginPath(); g.roundRect(-3.6 * s, -6.6 * s, 7.2 * s, 13.2 * s, 1.5 * s); g.fill();
    g.restore();
  }
  seg([pose.sh, pose.el1, pose.hd1], near, lw * 0.92);
  // head
  g.fillStyle = near; g.beginPath(); g.arc(X(pose.head), Y(pose.head), 14.5 * s, 0, 7); g.fill();
  if (o.pony) { // ponytail on the back of the head
    const hx = X(pose.head), hy = Y(pose.head); g.shadowBlur = 0;
    g.strokeStyle = near; g.lineWidth = 5 * s; g.beginPath();
    g.moveTo(hx - 9 * d * s, hy - 11 * s); g.quadraticCurveTo(hx - 21 * d * s, hy - 15 * s, hx - 19 * d * s, hy + 4 * s); g.stroke();
    g.fillStyle = near; g.beginPath(); g.ellipse(hx - 11 * d * s, hy - 12 * s, 4 * s, 3 * s, 0, 0, 7); g.fill();
  }
  // phone light on the face
  if (o.phone > 0 && !o.reflect) {
    const hx = (X(pose.hd1) + X(pose.hd2)) / 2, hy = (Y(pose.hd1) + Y(pose.hd2)) / 2;
    g.shadowBlur = 0; g.globalCompositeOperation = 'lighter';
    const r = 48 * s; const gr = g.createRadialGradient(hx, hy - 6 * s, 0, hx, hy - 6 * s, r);
    gr.addColorStop(0, rgba(C.gold, 0.30 * o.phone)); gr.addColorStop(1, rgba(C.gold, 0));
    g.fillStyle = gr; g.beginPath(); g.arc(hx, hy - 6 * s, r, 0, 7); g.fill();
  }
  g.restore();
}
function phonePos(pose, o) { return [o.x + (pose.hd1[0] + pose.hd2[0]) / 2 * o.dir * o.s, o.y + (pose.hd1[1] + pose.hd2[1]) / 2 * o.s]; }

function bubble(g, x, y, s, k, t, warm) { // typing bubble, k = 0..1 visibility
  if (k <= 0.01) return;
  g.save(); g.translate(x, y); g.scale(s * (0.6 + 0.4 * eout(k)), s * (0.6 + 0.4 * eout(k))); g.globalAlpha = k;
  g.fillStyle = warm ? 'rgba(78,74,70,0.95)' : 'rgba(70,74,84,0.95)';
  g.beginPath(); g.roundRect(-16, -10, 32, 20, 9); g.fill();
  g.beginPath(); g.moveTo(-6, 9); g.lineTo(-11, 15); g.lineTo(-1, 9); g.fill();
  for (let i = 0; i < 3; i++) { const b = 0.55 + 0.45 * Math.max(0, Math.sin(t * 9 - i * 0.9)); g.fillStyle = `rgba(235,235,240,${b})`; g.beginPath(); g.arc(-8 + i * 8, -1 - 1.5 * Math.max(0, Math.sin(t * 9 - i * 0.9)), 2.6, 0, 7); g.fill(); }
  g.restore();
}

// ---------- ledges (glossy) ----------
function ledges(g, cam, gy, eL, eR, warm, drawRefl) {
  // cam: {z, cx, sx, sy}: world x -> sx + (x - cx) * z ; world y (rel ground) -> sy + y * z
  const z = cam.z; const sxL = cam.sx + (eL - cam.cx) * z, sxR = cam.sx + (eR - cam.cx) * z, y0 = cam.sy;
  const top = 21 * z, front = 24 * z, depth = 120 * z;
  const tone = warm ? [62, 60, 64] : [52, 57, 68];
  for (const side of [-1, 1]) {
    const x0 = side < 0 ? -50 : sxR, x1 = side < 0 ? sxL : DW + 50;
    // top face: glossy gradient, brighter toward the back edge
    let gr = g.createLinearGradient(0, y0 - top, 0, y0 + front);
    gr.addColorStop(0, `rgba(${tone[0] + 26},${tone[1] + 26},${tone[2] + 28},1)`);
    gr.addColorStop(0.45, `rgba(${tone[0]},${tone[1]},${tone[2]},1)`);
    gr.addColorStop(1, `rgba(${tone[0] - 22},${tone[1] - 22},${tone[2] - 20},1)`);
    g.fillStyle = gr; g.fillRect(x0, y0 - top, x1 - x0, top + front);
    // front face fading into the background
    gr = g.createLinearGradient(0, y0 + front, 0, y0 + front + depth);
    gr.addColorStop(0, `rgba(${tone[0] - 30},${tone[1] - 30},${tone[2] - 26},1)`);
    gr.addColorStop(1, `rgba(${tone[0] - 30},${tone[1] - 30},${tone[2] - 26},0)`);
    g.fillStyle = gr; g.fillRect(x0, y0 + front, x1 - x0, depth);
    // specular lip
    g.fillStyle = warm ? 'rgba(255,236,205,0.55)' : 'rgba(215,228,255,0.45)';
    g.fillRect(x0, y0 + front - 1.2 * z, x1 - x0, 1.6 * z);
    g.fillStyle = 'rgba(255,255,255,0.10)'; g.fillRect(x0, y0 - top, x1 - x0, 1.2 * z);
    // inner cliff edge highlight
    const ex = side < 0 ? sxL : sxR;
    gr = g.createLinearGradient(0, y0 - top, 0, y0 + front + depth * 0.8);
    gr.addColorStop(0, warm ? 'rgba(255,225,180,0.45)' : 'rgba(200,215,240,0.35)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.fillRect(ex - (side < 0 ? 1.4 * z : 0), y0 - top, 1.4 * z, top + front + depth * 0.8);
  }
}

// ---------- background ----------
function background(g, t) {
  let gr = g.createLinearGradient(0, 0, 0, DH);
  gr.addColorStop(0, C.bgTop); gr.addColorStop(0.5, C.bgMid); gr.addColorStop(1, C.bgBot);
  g.fillStyle = gr; g.fillRect(0, 0, DW, DH);
  // warm wash behind the top story, cool wash behind the bottom one
  gr = g.createRadialGradient(360, 380, 10, 360, 380, 460); gr.addColorStop(0, 'rgba(255,190,110,0.10)'); gr.addColorStop(1, 'rgba(255,190,110,0)');
  g.fillStyle = gr; g.fillRect(0, 0, DW, DH);
  gr = g.createRadialGradient(360, 830, 10, 360, 830, 440); gr.addColorStop(0, 'rgba(120,150,210,0.08)'); gr.addColorStop(1, 'rgba(120,150,210,0)');
  g.fillStyle = gr; g.fillRect(0, 0, DW, DH);
  // gloss sheen: a soft diagonal highlight band
  gr = g.createLinearGradient(0, 0, DW, DH * 0.6);
  gr.addColorStop(0.25, 'rgba(255,255,255,0)'); gr.addColorStop(0.42, 'rgba(255,255,255,0.025)'); gr.addColorStop(0.6, 'rgba(255,255,255,0)');
  g.fillStyle = gr; g.fillRect(0, 0, DW, DH);
  // drifting dust motes
  for (let i = 0; i < 46; i++) {
    const x = (hash(i) * DW + t * (4 + 8 * hash(i + 9))) % DW, y = 120 + hash(i + 3) * 960 - t * (3 + 5 * hash(i + 5));
    const a = 0.10 + 0.18 * hash(i + 7) * (0.6 + 0.4 * Math.sin(t * 1.3 + i));
    g.fillStyle = `rgba(255,240,215,${a})`; g.beginPath(); g.arc(x, y, 0.6 + 1.1 * hash(i + 11), 0, 7); g.fill();
  }
}

function label(g, txt, x, y, size, alpha, spacing, weight = 600, align = 'left') {
  g.save(); g.font = `${weight} ${size}px "JetBrains Mono"`; g.letterSpacing = spacing + 'px'; g.textAlign = align; g.textBaseline = 'alphabetic';
  g.fillStyle = `rgba(242,238,230,${alpha})`; g.fillText(txt, x, y); g.restore();
}

// ---------- the top story: TEXTS FIRST ----------
const TOP = { gy: 432, eL: 216, eR: 504, nb: 15 };
const BW = (TOP.eR - TOP.eL) / TOP.nb;
const brickOrder = []; for (let i = 0, l = 0, r = TOP.nb - 1; i < TOP.nb; i++) brickOrder.push(i % 2 === 0 ? l++ : r--);
const BR0 = 1.85, BRD = 0.1; // first brick time, spacing
const brickT = idx => BR0 + brickOrder.indexOf(idx) * BRD;
const DAYS = [[0, 1], [1.5, 1], [1.6, 4], [1.8, 12], [2.0, 24], [2.2, 37], [2.4, 50], [2.6, 67], [2.8, 86], [3.0, 104], [3.2, 118], [3.4, 126], [3.6, 131], [3.8, 133], [4.0, 135], [4.2, 137], [4.4, 139], [4.6, 141], [4.8, 147], [5.0, 160], [5.2, 189], [5.4, 227], [5.6, 263], [5.8, 301], [6.0, 339], [6.2, 365]];
const HIS_X = 175, HER_X = 545, MEET_HIM = 332, MEET_HER = 388, WALK0 = 4.2, WALK1 = 5.45;

function topPose(t, who) { // who: 0 him (faces right), 1 her (faces left)
  const home = who ? HER_X : HIS_X, meet = who ? MEET_HER : MEET_HIM;
  if (t < 3.5) return [SIT, home];
  if (t < 3.8) return [mix(SIT, CROUCH, eio((t - 3.5) / 0.3)), home];
  if (t < 4.15) return [mix(CROUCH, STAND, eio((t - 3.8) / 0.35)), home];
  if (t < WALK0) return [STAND, home];
  if (t < WALK1) {
    const k = (t - WALK0) / (WALK1 - WALK0); const x = lerp(home, meet, k * k * (1.6 - 0.6 * k) / 1.0);
    const amp = ss(0, 0.12, k) * (1 - ss(0.85, 1, k)); const ph = (t - WALK0) * 11.5 + (who ? 0.6 : 0);
    return [mix(STAND, walk(ph), amp), x];
  }
  const k = eio(clamp((t - WALK1) / 0.35));
  return [mix(STAND, HOLD, k), meet];
}

function drawTop(g, t) {
  const cam = { z: 1, cx: 0, sx: 0, sy: TOP.gy };
  ledges(g, cam, TOP.gy, TOP.eL, TOP.eR, true);
  const [pm, xm] = topPose(t, 0), [pf, xf] = topPose(t, 1);
  const oM = { x: xm, y: TOP.gy, dir: 1, s: 1, warm: true, pony: false };
  const oF = { x: xf, y: TOP.gy, dir: -1, s: 1, warm: true, pony: true };
  const phoneK = 1 - ss(3.45, 3.65, t);
  const herLit = ss(0.9, 1.05, t);
  oM.phone = phoneK * (0.55 + 0.45 * (ss(0.0, 0.1, t))); oF.phone = phoneK * (0.25 + 0.75 * herLit);
  const pM = phonePos(pm, oM), pF = phonePos(pf, oF);
  // reflections on the glossy ledge / bridge
  g.save(); g.beginPath(); g.rect(0, TOP.gy - 21, DW, 45); g.clip();
  const mk = (o) => Object.assign({}, o, { reflect: true, alpha: 0.13, y: TOP.gy + 10 });
  drawFig(g, pm, mk(oM)); drawFig(g, pf, mk(oF)); g.restore();
  // message line
  const lineOn = ss(0.5, 0.52, t) * (1 - ss(3.3, 3.55, t));
  if (lineOn > 0) {
    const k = eout(clamp((t - 0.5) / 0.45)); const x1 = lerp(pM[0], pF[0], k), y1 = lerp(pM[1], pF[1], k);
    g.save(); g.globalCompositeOperation = 'lighter'; g.lineCap = 'round';
    g.strokeStyle = rgba(C.gold, 0.85 * lineOn); g.lineWidth = 1.8; g.shadowColor = rgba(C.gold, 1); g.shadowBlur = 10 * W / DW;
    g.beginPath(); g.moveTo(pM[0], pM[1]); g.lineTo(x1, y1); g.stroke();
    if (k < 1) glowDot(g, x1, y1, 5, 1);
    // reply back 1.6-2.0
    const rk = clamp((t - 1.58) / 0.32); if (rk > 0 && rk < 1) glowDot(g, lerp(pF[0], pM[0], eout(rk)), lerp(pF[1], pM[1], eout(rk)), 4.5, 1);
    // sparks flying both ways while the bridge builds
    for (let i = 0; i < 18; i++) {
      const ts = 1.95 + i * 0.085, kk = (t - ts) / 0.28; if (kk <= 0 || kk >= 1) continue;
      const fwd = i % 2 === 0; const e = eout(kk); const a = fwd ? pM : pF, b = fwd ? pF : pM;
      glowDot(g, lerp(a[0], b[0], e), lerp(a[1], b[1], e) - Math.sin(e * Math.PI) * 10, 3.2, 1 - kk * 0.3);
    }
    g.restore();
  }
  // bricks
  for (let i = 0; i < TOP.nb; i++) {
    const tb = brickT(i); if (t < tb) continue;
    const k = clamp((t - tb) / 0.14); const x = TOP.eL + i * BW, drop = (1 - eout(k)) * -26;
    const flash = Math.exp(-(t - tb - 0.1) * 6) * (t > tb + 0.1 ? 1 : k);
    brick(g, x, TOP.gy - 8 + drop, BW, 21, flash, t);
  }
  // figures
  drawFig(g, pf, oF); drawFig(g, pm, oM);
  // typing bubbles
  const hb = ss(0.0, 0.08, t) * (1 - ss(0.4, 0.5, t));
  bubble(g, xm + pm.head[0] + 12, TOP.gy + pm.head[1] - 30, 1, hb, t, true);
  const fb = ss(1.25, 1.33, t) * (1 - ss(1.52, 1.6, t));
  bubble(g, xf - pf.head[0] - 12, TOP.gy + pf.head[1] - 30, 1, fb, t, true);
  // the meeting: warm light blooms from their hands
  const bloom = ss(5.65, 6.6, t);
  if (bloom > 0) {
    const hx = (MEET_HIM + MEET_HER) / 2, hy = TOP.gy - 96; const pulse = 0.85 + 0.15 * Math.sin((t - 5.6) * 3.2);
    g.save(); g.globalCompositeOperation = 'lighter';
    let gr = g.createRadialGradient(hx, hy, 0, hx, hy, 150); gr.addColorStop(0, rgba(C.gold, 0.2 * bloom * pulse)); gr.addColorStop(0.35, rgba(C.gold, 0.10 * bloom * pulse)); gr.addColorStop(1, rgba(C.gold, 0));
    g.fillStyle = gr; g.fillRect(hx - 160, hy - 160, 320, 320);
    glowDot(g, hx, hy, 3.5, 0.9 * bloom * pulse);
    g.restore();
  }
}
function glowDot(g, x, y, r, a) {
  g.save(); g.globalCompositeOperation = 'lighter';
  let gr = g.createRadialGradient(x, y, 0, x, y, r * 4); gr.addColorStop(0, rgba(C.goldHot, 0.9 * a)); gr.addColorStop(0.3, rgba(C.gold, 0.45 * a)); gr.addColorStop(1, rgba(C.gold, 0));
  g.fillStyle = gr; g.beginPath(); g.arc(x, y, r * 4, 0, 7); g.fill(); g.restore();
}
function brick(g, x, y, w, h, flash, t) {
  g.save();
  const gr = g.createLinearGradient(0, y, 0, y + h);
  gr.addColorStop(0, '#ffd892'); gr.addColorStop(0.45, '#f2a83e'); gr.addColorStop(1, '#a8621a');
  g.shadowColor = rgba(C.gold, 0.8); g.shadowBlur = (6 + 14 * flash) * W / DW;
  g.fillStyle = gr; g.beginPath(); g.roundRect(x + 1.2, y, w - 2.4, h, 2.6); g.fill();
  g.shadowBlur = 0; g.fillStyle = 'rgba(255,250,235,0.55)'; g.fillRect(x + 3, y + 2, w - 6, 2); // glossy top highlight
  if (flash > 0.02) { g.globalCompositeOperation = 'lighter'; g.fillStyle = rgba(C.goldHot, 0.6 * flash); g.beginPath(); g.roundRect(x + 1.2, y, w - 2.4, h, 2.6); g.fill(); }
  g.restore();
}

// ---------- the bottom story: WAITS ----------
const BOT = { gy: 860 };
function botCam(t) { // returns {z, cx, sx, sy}
  const wide = (tt) => ({ z: pw(tt, [[0, 1], [6.2, 0.72], [8.3, 0.58], [12.1, 0.5]]), cx: 360, sx: 360, sy: BOT.gy });
  const herX = 360 + halfGap(t) + 42;
  const close = (tt) => ({ z: lerp(1.9, 2.04, clamp((tt - 6.6) / 1.7)), cx: herX - 8, sx: 380, sy: 940 });
  if (t < 6.22 || t >= 8.3) return wide(t);
  const a = wide(6.22), b = close(t); const k = eio(clamp((t - 6.22) / 0.4));
  return { z: Math.exp(lerp(Math.log(a.z), Math.log(b.z), k)), cx: lerp(a.cx, b.cx, k), sx: lerp(a.sx, b.sx, k), sy: lerp(a.sy, b.sy, k) };
}
const halfGap = t => pw(t, [[0, 144], [6.2, 257], [8.3, 300], [12.1, 380]]);

function drawBot(g, t) {
  const cam = botCam(t), z = cam.z, hg = halfGap(t);
  const eL = 360 - hg, eR = 360 + hg;
  ledges(g, cam, cam.sy, eL, eR, false);
  const S = (wx) => cam.sx + (wx - cam.cx) * z;
  const xm = S(eL - 41), xf = S(eR + 42);
  // poses: slump over time, him sits up to finally send, she sits up when it lands
  const slumpM = ss(0.7, 6.0, t) * (1 - ss(9.0, 9.3, t)) * 0.95;
  const slumpF = ss(1.5, 6.0, t) * 0.8 * (1 - ss(10.35, 10.75, t));
  const pm = mix(SIT, SLUMP, slumpM), pf = mix(SIT, SLUMP, slumpF);
  const oM = { x: xm, y: cam.sy, dir: 1, s: z, warm: false, pony: false, phone: 0.45 + 0.4 * (ss(9.15, 9.3, t)) };
  const oF = { x: xf, y: cam.sy, dir: -1, s: z, warm: false, pony: true, phone: 0.35 + 0.65 * ss(10.35, 10.45, t) * (1 - 0.3 * ss(10.6, 11, t)) };
  g.save(); g.beginPath(); g.rect(0, cam.sy - 21 * z, DW, 45 * z); g.clip();
  const mk = (o) => Object.assign({}, o, { reflect: true, alpha: 0.11, y: cam.sy + 10 * z });
  drawFig(g, pm, mk(oM)); drawFig(g, pf, mk(oF)); g.restore();
  // the late message: a slow line across the long gap
  if (t > 9.5) {
    const pM = phonePos(pm, oM), pF = phonePos(pf, oF); const k = clamp((t - 9.5) / 0.85);
    const x1 = lerp(pM[0], pF[0], k), y1 = lerp(pM[1], pF[1], k);
    g.save(); g.globalCompositeOperation = 'lighter'; g.lineCap = 'round';
    g.strokeStyle = rgba(C.gold, 0.6); g.lineWidth = 1.3; g.shadowColor = rgba(C.gold, 0.9); g.shadowBlur = 7 * W / DW;
    g.beginPath(); g.moveTo(pM[0], pM[1]); g.lineTo(x1, y1); g.stroke();
    if (k < 1) glowDot(g, x1, y1, 3.6, 0.9);
    g.restore();
  }
  drawFig(g, pf, oF); drawFig(g, pm, oM);
  // bubbles: he types and deletes, she types and deletes, close-up: she almost sends, the end: she starts typing back
  const bm = ss(0.0, 0.08, t) * (1 - ss(0.5, 0.62, t)) + ss(9.12, 9.2, t) * (1 - ss(9.42, 9.5, t));
  bubble(g, xm + (pm.head[0] + 12) * z, cam.sy + (pm.head[1] - 30) * z, z, bm, t, false);
  const bf = ss(2.35, 2.43, t) * (1 - ss(2.68, 2.78, t)) + ss(6.95, 7.03, t) * (1 - ss(7.55, 7.68, t)) + ss(10.95, 11.05, t);
  bubble(g, xf - (pf.head[0] + 12) * z, cam.sy + (pf.head[1] - 30) * z, z, bf, t, false);
}

// ---------- compose one frame (design space) ----------
function panel(g, t, fn, y0, y1, fade) {
  L.setTransform(1, 0, 0, 1, 0, 0); L.clearRect(0, 0, W, H); L.setTransform(...contentTf());
  fn(L, t);
  // soft mask at the panel edges
  L.globalCompositeOperation = 'destination-in';
  const gr = L.createLinearGradient(0, y0, 0, y1);
  gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(fade / (y1 - y0), 'rgba(0,0,0,1)'); gr.addColorStop(1 - fade / (y1 - y0), 'rgba(0,0,0,1)'); gr.addColorStop(1, 'rgba(0,0,0,0)');
  L.fillStyle = gr; L.fillRect(0, 0, DW, DH); L.globalCompositeOperation = 'source-over';
  g.setTransform(1, 0, 0, 1, 0, 0); g.drawImage(layer, 0, 0); g.setTransform(...contentTf());
}
function frame(g, t) {
  T = t; ZC = zoomAt(unwarp(t));
  g.setTransform(W / DW, 0, 0, H / DH, 0, 0);
  background(g, t);
  const endFade = 1 - 0.75 * ss(11.45, 12.05, t);
  g.globalAlpha = endFade;
  panel(g, t, drawTop, 150, 585, 26);
  panel(g, t, drawBot, 625, 1010, 26);
  g.setTransform(...contentTf());
  // HUD
  // hook line, on screen from frame 0
  g.save(); g.textAlign = 'center'; g.textBaseline = 'alphabetic'; g.font = '800 46px "Inter Display"'; g.letterSpacing = '0.5px';
  g.shadowColor = 'rgba(0,0,0,0.5)'; g.shadowBlur = 10;
  g.fillStyle = 'rgba(250,246,238,0.98)'; g.fillText('AFTER A FIGHT,', 360, 104);
  g.fillStyle = 'rgba(255,200,110,1)'; g.fillText('WHO TEXTS FIRST?', 360, 160); g.restore();
  label(g, 'TEXTS FIRST', 80, 237, 25, 0.95, 4, 700);
  label(g, 'WAITS', 80, 663, 25, 0.85, 4, 700);
  const day = Math.round(pw(t, DAYS));
  g.save(); g.font = '600 15px "JetBrains Mono"'; g.letterSpacing = '3px'; g.textBaseline = 'alphabetic'; const w1 = g.measureText('DAY ').width;
  g.font = '700 26px "JetBrains Mono"'; g.letterSpacing = '1px'; const w2 = g.measureText(String(day)).width; const x0 = 360 - (w1 + w2) / 2;
  g.restore();
  label(g, 'DAY', x0, 607, 15, 0.7, 3);
  g.save(); g.font = '700 26px "JetBrains Mono"'; g.letterSpacing = '1px'; g.fillStyle = day === 365 ? 'rgba(255,214,150,0.98)' : 'rgba(246,242,234,0.96)'; g.fillText(String(day), x0 + w1, 609); g.restore();
  // thin divider lines around the counter
  g.fillStyle = 'rgba(255,255,255,0.05)'; g.fillRect(0, 574, DW, 1); g.fillRect(0, 627, DW, 1);
  g.setTransform(W / DW, 0, 0, H / DH, 0, 0);
  label(g, 'SLOW LIGHT', 360, 1248, 11, 0.28, 5, 600, 'center');
  g.globalAlpha = 1;
}

window.renderAt = (t, sub = 1) => {
  sub = Math.max(1, sub | 0);
  t = warp(t);
  if (sub === 1) { frame(out, t); }
  else {
    out.setTransform(1, 0, 0, 1, 0, 0); out.fillStyle = '#000'; out.fillRect(0, 0, W, H);
    for (let i = 0; i < sub; i++) {
      frame(A, t + (i / sub - 0.5) * (1 / 30) * 0.5);
      out.setTransform(1, 0, 0, 1, 0, 0); out.globalCompositeOperation = 'lighter'; out.globalAlpha = 1 / sub; out.drawImage(acc, 0, 0);
    }
    out.globalCompositeOperation = 'source-over'; out.globalAlpha = 1;
  }
  return cv.toDataURL('image/jpeg', 0.95);
};

// sound cues for mix.py
window.events = (() => {
  const e = [];
  e.push({ t: 0.02, s: 'type', g: 0.5, pan: -0.35, panel: 'top' }, { t: 0.02, s: 'type', g: 0.3, pan: -0.35, panel: 'bot' });
  e.push({ t: 0.5, s: 'send', g: 0.8, pan: -0.2 }, { t: 0.95, s: 'ping', g: 0.75, pan: 0.35 });
  e.push({ t: 0.5, s: 'erase', g: 0.35, pan: -0.35, panel: 'bot' });
  e.push({ t: 1.27, s: 'type', g: 0.4, pan: 0.35 }, { t: 1.58, s: 'send', g: 0.55, pan: 0.2 }, { t: 1.9, s: 'ping', g: 0.5, pan: -0.35 });
  for (let i = 0; i < TOP.nb; i++) { const x = TOP.eL + i * BW; e.push({ t: brickT(i) + 0.12, s: i % 2 ? 'brick1' : 'brick2', g: 0.55, pan: (x - 360) / 300, rate: 1 + 0.03 * brickOrder.indexOf(i) }); }
  e.push({ t: 2.36, s: 'type', g: 0.22, pan: 0.4, panel: 'bot' }, { t: 2.68, s: 'erase', g: 0.2, pan: 0.4, panel: 'bot' });
  e.push({ t: 3.55, s: 'rise', g: 0.5, pan: -0.3 }, { t: 3.6, s: 'rise', g: 0.45, pan: 0.3 });
  // footsteps: lowest-foot changes during the walk
  for (let i = 0; i < 9; i++) { const ts = WALK0 + 0.1 + i * (Math.PI / 11.5); if (ts < WALK1 - 0.05) { e.push({ t: ts, s: 'step', g: 0.4, pan: -0.25 }); e.push({ t: ts + 0.05, s: 'step', g: 0.35, pan: 0.25 }); } }
  e.push({ t: 5.7, s: 'swell', g: 0.8, pan: 0 });
  e.push({ t: 6.22, s: 'whoosh', g: 0.55, pan: 0.2 }, { t: 6.97, s: 'type', g: 0.35, pan: 0.15 }, { t: 7.56, s: 'erase', g: 0.3, pan: 0.15 });
  e.push({ t: 8.3, s: 'pullback', g: 0.45, pan: 0 });
  e.push({ t: 9.12, s: 'type', g: 0.35, pan: -0.4 }, { t: 9.5, s: 'send', g: 0.5, pan: -0.4 }, { t: 10.35, s: 'ping', g: 0.45, pan: 0.45 }, { t: 10.97, s: 'type', g: 0.3, pan: 0.45 });
  for (const x of e) x.t = Math.max(0, unwarp(x.t));
  return e.sort((a, b) => a.t - b.t);
})();
window.DUR = OUT_DUR;
document.fonts.load('600 20px "JetBrains Mono"').then(() => document.fonts.load('700 26px "JetBrains Mono"')).then(() => { window.ready = true; });
