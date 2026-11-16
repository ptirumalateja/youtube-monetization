// Nobody Claps at 6 AM - Slow Light stickman discipline reel, Silence Is Distance / 30 Friends dark look.
// Canvas 2D, design space 720x1280 scaled to the render size. Wordless, foley only.
// Payoff first: he breaks the tape in a roaring stadium -> hard cut to the same pose alone under a streetlight at 6 AM
// -> 5:58 alarm, laces, out the door -> DAY 1 / 47 (rain) / 112 (falls) / 203 (empty track) / 311 (steps at dawn)
// -> rehook: hands on knees, empty stands -> DAY 365 slams, the stands fill, he breaks the tape again -> close + CTA.
// window.renderAt(t, sub) -> JPEG data URL. window.events -> sound cues (mix.py). window.TL -> timeline.
'use strict';
const DW = 720, DH = 1280, DUR = 17.0;
const qs = new URLSearchParams(location.search);
const W = +(qs.get('w') || 1080), H = +(qs.get('h') || 1920), KK = W / DW;
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
function hash(i) { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }
function integ(fn, a, b, n = 48) { if (b <= a) return 0; const h = (b - a) / n; let s = 0; for (let i = 0; i < n; i++) s += fn(a + (i + 0.5) * h); return s * h; }
const rgba = (c, a) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;
const C = { gold: [255, 190, 92], goldHot: [255, 232, 180], cool: [150, 185, 255], figWarm: '#fff7ea', farWarm: '#a59d92' };

// ---------- timeline ----------
const T_CUT = 1.6, T_BED = 2.4, T_DOOR = 3.7, T_RUN1 = 4.7, T_RAIN = 6.5, T_FALL = 7.5, T_TRACK = 8.5, T_STEPS = 9.5,
  T_STOP = 10.5, T_365 = 12.0, T_TAPE2 = 13.7, T_CLOSE = 14.6, T_CTA = 15.6;
const TAPE1 = 0.12, SWITCH_OFF = 5.75, FALL_HIT = 7.95, FALL_SND = 7.5 + 0.18 + (FALL_HIT - 7.5 - 0.18) / 0.5;
const SHOTS = [[0, 'stadiumHook'], [T_CUT, 'road'], [T_BED, 'bedroom'], [T_DOOR, 'door'], [T_RUN1, 'street'], [T_RAIN, 'rain'],
  [T_FALL, 'fall'], [T_TRACK, 'track'], [T_STEPS, 'steps'], [T_STOP, 'rehook'], [T_365, 'finale'], [T_CLOSE, 'close']];
const DAYS = [[T_RUN1, 'DAY 1'], [T_RAIN, 'DAY 47'], [T_FALL, 'DAY 112'], [T_TRACK, 'DAY 203'], [T_STEPS, 'DAY 311'], [T_STOP, 'DAY 364'], [T_365 + 0.4, 'DAY 365']];

// ---------- rig (local px, facing +x, ground y = 0) - Silence stickman proportions ----------
const K = ['head', 'sh', 'hip', 'kn1', 'ft1', 'kn2', 'ft2', 'el1', 'hd1', 'el2', 'hd2'];
function mix(a, b, k) { const o = {}; for (const n of K) o[n] = [lerp(a[n][0], b[n][0], k), lerp(a[n][1], b[n][1], k)]; return o; }
const STAND = { head: [3, -150], sh: [0, -124], hip: [0, -66], kn1: [3, -33], ft1: [6, 0], kn2: [-3, -33], ft2: [-6, 0], el1: [4, -97], hd1: [6, -71], el2: [-4, -97], hd2: [-6, -71] };
const STANDDOWN = Object.assign({}, STAND, { head: [8, -146], sh: [3, -123] });
const KNEES = { head: [59, -110], sh: [37, -96], hip: [-8, -60], kn1: [8, -32], ft1: [2, 0], kn2: [-2, -32], ft2: [-10, 0], el1: [34, -70], hd1: [16, -44], el2: [28, -70], hd2: [10, -44] };
const CROUCH = { head: [58, -89], sh: [35, -78], hip: [-12, -44], kn1: [18, -40], ft1: [22, 0], kn2: [-4, -6], ft2: [-36, -2], el1: [44, -52], hd1: [30, -28], el2: [38, -52], hd2: [24, -28] };
const PRONE = { head: [84, -14], sh: [58, -12], hip: [0, -8], kn1: [-32, -6], ft1: [-64, -4], kn2: [-32, -9], ft2: [-64, -8], el1: [50, -30], hd1: [64, -4], el2: [44, -30], hd2: [56, -4] };
const FALLMID = { head: [83, -90], sh: [59, -81], hip: [10, -50], kn1: [20, -20], ft1: [0, -4], kn2: [-15, -35], ft2: [-40, -30], el1: [80, -70], hd1: [100, -56], el2: [74, -74], hd2: [96, -62] };
const SIT = { head: [-2, -92], sh: [-4, -66], hip: [0, -8], kn1: [32, -10], ft1: [66, -6], kn2: [32, -8], ft2: [66, -4], el1: [4, -40], hd1: [22, -30], el2: [0, -40], hd2: [18, -30] };
function rot(v, c, a) { const x = v[0] - c[0], y = v[1] - c[1]; return [c[0] + x * Math.cos(a) - y * Math.sin(a), c[1] + x * Math.sin(a) + y * Math.cos(a)]; }
function bedPose(k) { // k 0 = lying flat, 1 = sitting up
  const p = mix(SIT, SIT, 0), a = -Math.PI / 2 * (1 - eio(k));
  for (const n of ['head', 'sh', 'el1', 'hd1', 'el2', 'hd2']) p[n] = rot(SIT[n], SIT.hip, a);
  return p;
}
function runPose(ph, lean = 0.2, amp = 1) {
  const hip = [0, -64 - 3 * amp * Math.cos(2 * ph)];
  const sh = [hip[0] + 58 * Math.sin(lean), hip[1] - 58 * Math.cos(lean)];
  const head = [sh[0] + 26 * Math.sin(lean + 0.08), sh[1] - 26 * Math.cos(lean + 0.08)];
  const leg = q => { const a = 0.62 * amp * Math.sin(q), fl = 0.15 + 1.35 * amp * Math.pow(Math.max(0, Math.cos(q)), 1.2);
    const kn = [hip[0] + 32 * Math.sin(a), hip[1] + 32 * Math.cos(a)]; return [kn, [kn[0] + 34 * Math.sin(a - fl), kn[1] + 34 * Math.cos(a - fl)]]; };
  const arm = b => { const el = [sh[0] + 28 * Math.sin(b), sh[1] + 28 * Math.cos(b)]; return [el, [el[0] + 26 * Math.sin(b + 1.6), el[1] + 26 * Math.cos(b + 1.6)]]; };
  const [kn1, ft1] = leg(ph), [kn2, ft2] = leg(ph + Math.PI), [el1, hd1] = arm(-0.8 * amp * Math.sin(ph)), [el2, hd2] = arm(0.8 * amp * Math.sin(ph));
  return { head, sh, hip, kn1, ft1, kn2, ft2, el1, hd1, el2, hd2 };
}
function armsUp(p, k, wave = 0) { // victory V, blended by k
  const o = Object.assign({}, p), s = p.sh, w = Math.sin(wave) * 3;
  const up = { el1: [s[0] + 12, s[1] - 25], hd1: [s[0] + 26 + w, s[1] - 49], el2: [s[0] - 7, s[1] - 26], hd2: [s[0] - 14 - w, s[1] - 50] };
  for (const n in up) o[n] = [lerp(p[n][0], up[n][0], k), lerp(p[n][1], up[n][1], k)];
  o.head = [lerp(p.head[0], s[0] - 2, k * 0.7), lerp(p.head[1], s[1] - 25, k * 0.7)];
  return o;
}

// ---------- figure (Silence drawFig) ----------
function drawFig(g, pose, o) {
  const s = o.s || 1, d = o.dir ?? 1;
  if (o.breathe !== 0) { const b = Math.sin(T * (o.breathRate || 2.4)) * (o.breathe || 1.3); pose = Object.assign({}, pose);
    for (const n of ['head', 'sh']) pose[n] = [pose[n][0], pose[n][1] + b];
    for (const n of ['el1', 'el2']) pose[n] = [pose[n][0], pose[n][1] + b * 0.6]; }
  const X = p => o.x + p[0] * d * s, Y = p => o.y + p[1] * s * (o.reflect ? -0.55 : 1);
  const near = C.figWarm, far = C.farWarm;
  g.save(); g.globalAlpha = o.alpha ?? 1; g.lineCap = 'round'; g.lineJoin = 'round';
  const lw = 11.5 * s;
  const seg = (pts, col, w) => { g.strokeStyle = col; g.lineWidth = w; g.beginPath(); g.moveTo(X(pts[0]), Y(pts[0])); for (let i = 1; i < pts.length; i++) g.lineTo(X(pts[i]), Y(pts[i])); g.stroke(); };
  if (!o.reflect) { g.shadowColor = o.rim || 'rgba(255,214,160,0.45)'; g.shadowBlur = 10 * s * KK * (o.zoom || 1); }
  seg([pose.hip, pose.kn2, pose.ft2], far, lw);
  seg([pose.sh, pose.el2, pose.hd2], far, lw * 0.92);
  seg([pose.sh, pose.hip], near, lw * 1.05);
  seg([pose.hip, pose.kn1, pose.ft1], near, lw);
  seg([pose.sh, pose.el1, pose.hd1], near, lw * 0.92);
  g.fillStyle = near; g.beginPath(); g.arc(X(pose.head), Y(pose.head), 14.5 * s, 0, 7); g.fill();
  if (o.sweat && !o.reflect) { g.shadowBlur = 0; const hx = X(pose.head), hy = Y(pose.head);
    for (let i = 0; i < 2; i++) { const ph = (T * 0.8 + i * 0.5) % 1, a = Math.sin(ph * Math.PI); g.fillStyle = `rgba(170,210,255,${0.8 * a})`;
      g.beginPath(); g.arc(hx - (8 + 5 * i) * s * d, hy + (-4 + 20 * ph) * s, 2.2 * s, 0, 7); g.fill(); } }
  g.restore();
}
function fig(g, pose, x, y, o = {}) {
  if (o.refl !== false) drawFig(g, pose, Object.assign({ x, y: y + 10, reflect: true, alpha: o.reflA ?? 0.14 }, o));
  drawFig(g, pose, Object.assign({ x, y }, o));
}
function breath(g, x, y, t, a = 1) { // cold-morning breath puffs from the mouth
  for (let i = 0; i < 3; i++) { const ph = (t * 1.4 + i / 3) % 1; const al = 0.16 * Math.sin(ph * Math.PI) * a; if (al <= 0) continue;
    const gr = g.createRadialGradient(x + 30 * ph, y - 6 * ph, 0, x + 30 * ph, y - 6 * ph, 6 + 16 * ph); gr.addColorStop(0, `rgba(220,230,255,${al})`); gr.addColorStop(1, 'rgba(220,230,255,0)');
    g.fillStyle = gr; g.beginPath(); g.arc(x + 30 * ph, y - 6 * ph, 6 + 16 * ph, 0, 7); g.fill(); }
}

// ---------- camera + layers ----------
// world: ground at y = 0. cam {cx, cy, z}; screen = 360 + (x - cx) z, 640 + (y - cy) z (design px)
const gyOf = c => 640 - c.cy * c.z;
function camAt(cx, groundScreen, z, sh = 0) { return { cx: cx + sh, cy: -(groundScreen - 640) / z, z }; }
function setWorld(g, c) { g.setTransform(KK * c.z, 0, 0, KK * c.z, KK * (360 - c.cx * c.z), KK * (640 - c.cy * c.z)); }
function setLayer(g, c, p, lift = 0) { const s = c.z * p; g.setTransform(KK * s, 0, 0, KK * s, KK * (360 - c.cx * p * s), KK * (gyOf(c) - lift * c.z)); return s; }
function setScreen(g) { g.setTransform(KK, 0, 0, KK, 0, 0); }
function visRange(c, p) { const s = c.z * p; return [c.cx * p - 380 / s, c.cx * p + 380 / s]; }

// ---------- painters ----------
function sky(g, stops) { setScreen(g); const gr = g.createLinearGradient(0, 0, 0, DH); for (const [k, col] of stops) gr.addColorStop(k, col); g.fillStyle = gr; g.fillRect(0, 0, DW, DH); }
function stars(g, n, a, t) { setScreen(g); for (let i = 0; i < n; i++) { const x = hash(i + 1) * DW, y = hash(i + 50) * 700, tw = 0.6 + 0.4 * Math.sin(t * 2 + i);
  g.fillStyle = `rgba(220,230,255,${a * tw * (0.3 + 0.7 * hash(i + 9))})`; g.beginPath(); g.arc(x, y, 0.6 + 0.9 * hash(i + 3), 0, 7); g.fill(); } }
function dust(g, t, n = 40, col = '255,240,215', a0 = 0.12) { setScreen(g); for (let i = 0; i < n; i++) {
  const x = (hash(i) * DW + t * (4 + 8 * hash(i + 9))) % DW, y = 80 + hash(i + 3) * 1100 - t * (3 + 5 * hash(i + 5));
  g.fillStyle = `rgba(${col},${a0 + 0.15 * hash(i + 7)})`; g.beginPath(); g.arc(x, y, 0.6 + 1.1 * hash(i + 11), 0, 7); g.fill(); } }
function glowDot(g, x, y, r, a, col = C.gold, hot = C.goldHot) {
  g.save(); g.globalCompositeOperation = 'lighter';
  const gr = g.createRadialGradient(x, y, 0, x, y, r * 4); gr.addColorStop(0, rgba(hot, 0.9 * a)); gr.addColorStop(0.3, rgba(col, 0.45 * a)); gr.addColorStop(1, rgba(col, 0));
  g.fillStyle = gr; g.beginPath(); g.arc(x, y, r * 4, 0, 7); g.fill(); g.restore();
}
// ground plane from the ground line to the bottom edge (world coords; extends far)
function ground(g, c, kind, t) {
  setWorld(g, c); const x0 = c.cx - 400 / c.z, x1 = c.cx + 400 / c.z, yb = (DH - gyOf(c)) / c.z + 40;
  const pal = { road: ['#23252e', '#15161c', '#101116'], wet: ['#1f2433', '#131722', '#0e111a'], track: ['#4a2a24', '#2e1a17', '#1c1110'], concrete: ['#3a3640', '#25232b', '#18171d'], floor: ['#2a2830', '#1a191f', '#131217'] }[kind];
  let gr = g.createLinearGradient(0, 0, 0, yb); gr.addColorStop(0, pal[0]); gr.addColorStop(0.3, pal[1]); gr.addColorStop(1, pal[2]);
  g.fillStyle = gr; g.fillRect(x0, 0, x1 - x0, yb);
  g.fillStyle = 'rgba(255,240,220,0.32)'; g.fillRect(x0, -0.6, x1 - x0, 1.4);
  if (kind === 'road' || kind === 'wet') { // dashed centre line + curb
    g.fillStyle = 'rgba(240,230,200,0.22)'; for (let x = Math.floor(x0 / 90) * 90; x < x1; x += 90) g.fillRect(x, 52, 46, 4);
    g.fillStyle = 'rgba(255,255,255,0.05)'; g.fillRect(x0, 10, x1 - x0, 1.5);
  }
  if (kind === 'track') { for (const y of [14, 40, 76, 124, 190]) { g.fillStyle = 'rgba(255,240,230,0.2)'; g.fillRect(x0, y, x1 - x0, 1.6 + y * 0.012); } }
  if (kind === 'floor') { for (let x = Math.floor(x0 / 60) * 60; x < x1; x += 60) { g.fillStyle = 'rgba(255,240,220,0.035)'; g.fillRect(x, 0, 1.2, yb); } }
  for (let i = 1, d = 10; i < 9; i++, d *= 1.45) { g.fillStyle = `rgba(255,240,220,${0.035 - i * 0.003})`; g.fillRect(x0, d, x1 - x0, 1.1); }
}
function lightPool(g, c, x, w, col, a) { setWorld(g, c); g.save(); g.globalCompositeOperation = 'lighter'; g.translate(x, 6); g.scale(1, 0.18);
  const gr = g.createRadialGradient(0, 0, 0, 0, 0, w); gr.addColorStop(0, rgba(col, a)); gr.addColorStop(1, rgba(col, 0)); g.fillStyle = gr; g.beginPath(); g.arc(0, 0, w, 0, 7); g.fill(); g.restore(); }
function streetlight(g, c, x, h, col, a = 1, t = 0) {
  setWorld(g, c);
  g.strokeStyle = '#2c2e38'; g.lineWidth = 6; g.lineCap = 'round'; g.beginPath(); g.moveTo(x, 0); g.lineTo(x, -h); g.quadraticCurveTo(x, -h - 22, x + 34, -h - 22); g.stroke();
  g.strokeStyle = 'rgba(255,240,220,0.12)'; g.lineWidth = 1.4; g.beginPath(); g.moveTo(x + 2, 0); g.lineTo(x + 2, -h); g.stroke();
  g.fillStyle = '#3a3c48'; g.beginPath(); g.moveTo(x + 22, -h - 26); g.lineTo(x + 56, -h - 26); g.lineTo(x + 50, -h - 16); g.lineTo(x + 28, -h - 16); g.closePath(); g.fill();
  if (a <= 0) return;
  const lx = x + 39, ly = -h - 15;
  g.save(); g.globalCompositeOperation = 'lighter';
  for (let k = 0; k < 5; k++) { const w = 90 + k * 26, al = (0.06 - k * 0.01) * a; const gr = g.createLinearGradient(0, ly, 0, 0); gr.addColorStop(0, rgba(col, al * 1.8)); gr.addColorStop(1, rgba(col, al * 0.5));
    g.fillStyle = gr; g.beginPath(); g.moveTo(lx - 12 - k * 2, ly); g.lineTo(lx + 12 + k * 2, ly); g.lineTo(lx + w, 4); g.lineTo(lx - w, 4); g.closePath(); g.fill(); }
  g.restore();
  glowDot(g, lx, ly + 1, 7, 0.95 * a, col, [255, 245, 225]);
  lightPool(g, c, lx, 150, col, 0.35 * a);
}
function houses(g, c, p, t, warmA = 1) {
  const s = setLayer(g, c, p, 0); const [a, b] = visRange(c, p);
  for (let i = Math.floor(a / 170) - 1; i <= Math.floor(b / 170) + 1; i++) {
    const w = 120 + 60 * hash(i * 2.1), h = 120 + 120 * hash(i * 3.7), x = i * 170 + 20 * hash(i);
    g.fillStyle = '#141824'; g.fillRect(x, -h, w, h + 2); g.beginPath(); g.moveTo(x - 8, -h); g.lineTo(x + w / 2, -h - 46 - 20 * hash(i + 4)); g.lineTo(x + w + 8, -h); g.closePath(); g.fill();
    g.fillStyle = 'rgba(160,180,230,0.08)'; g.fillRect(x, -h, w, 1.5);
    for (let r = 0; r < 2; r++) for (let q = 0; q < 2; q++) {
      const wx = x + 18 + q * (w - 58), wy = -h + 24 + r * 54, id = i * 7 + r * 3 + q;
      let on = hash(id + 0.5) > 0.72 ? 1 : 0;
      if (i === 1 && r === 0 && q === 0) on = t < SWITCH_OFF ? 1 : 0; // the neighbour's light goes off
      g.fillStyle = on ? `rgba(255,196,120,${0.75 * warmA})` : 'rgba(40,48,70,0.9)'; g.fillRect(wx, wy, 22, 28);
      if (on) glowDot(g, wx + 11, wy + 14, 10, 0.25 * warmA);
    }
  }
}
function city(g, c, p, col, t) { // skyline silhouette near the horizon
  setLayer(g, c, p, 0); const [a, b] = visRange(c, p);
  for (let i = Math.floor(a / 60) - 1; i <= Math.floor(b / 60) + 1; i++) { const h = 60 + 200 * hash(i * 1.3) * hash(i * 2.9 + 1), w = 40 + 30 * hash(i + 7);
    g.fillStyle = col; g.fillRect(i * 60, -h, w, h + 2);
    for (let k = 0; k < 4; k++) if (hash(i * 11 + k) > 0.75) { g.fillStyle = 'rgba(255,200,130,0.5)'; g.fillRect(i * 60 + 8 + 10 * (k % 2), -h + 14 + 22 * k, 5, 7); } }
}
function rain(g, t, a = 1) {
  setScreen(g); g.save(); g.strokeStyle = `rgba(190,210,255,${0.32 * a})`; g.lineWidth = 1.3; g.beginPath();
  for (let i = 0; i < 260; i++) { const sp = 1500 + 700 * hash(i + 2), y = ((hash(i + 9) * 1500 + t * sp) % 1500) - 100, x = (hash(i) * 900 - 80 + y * 0.18);
    g.moveTo(x, y); g.lineTo(x + 7, y + 38); }
  g.stroke(); g.restore();
}
function splashes(g, c, t) { setWorld(g, c); for (let i = 0; i < 40; i++) { const ph = (t * 3 + hash(i)) % 1, x = c.cx + (hash(i + 4) * 2 - 1) * 380 / c.z, y = 4 + hash(i + 8) * 60;
  g.strokeStyle = `rgba(200,220,255,${0.4 * (1 - ph)})`; g.lineWidth = 1; g.beginPath(); g.ellipse(x, y, 2 + 9 * ph, (2 + 9 * ph) * 0.25, 0, 0, 7); g.stroke(); } }

// ---------- stadium ----------
const FANS = (() => { const f = []; for (let r = 0; r < 24; r++) for (let x = -1600; x < 2400; x += 19) { const i = f.length;
  f.push({ x: x + 8 * hash(i * 1.7) + (r % 2) * 9, y: -46 - r * 23 - 4 * hash(i), r, hue: hash(i * 3.3), ph: hash(i * 5.1) * 6.28, d: hash(i * 7.9), arms: hash(i * 9.3) }); } return f; })();
const fb = document.createElement('canvas'); fb.width = W; fb.height = H; const FB = fb.getContext('2d');
function stands(g, c, t, o) { // o: {fill 0..1 (fans present), lit 0..1, cheer 0..1, blur}
  const p = 0.5, s = setLayer(g, c, p, 0); const [a, b] = visRange(c, p);
  // tiers
  const top = -46 - 24 * 23;
  let gr = g.createLinearGradient(0, top, 0, 0); gr.addColorStop(0, lerp(0, 1, o.lit) > 0.5 ? '#2a2430' : '#141826'); gr.addColorStop(1, o.lit > 0.5 ? '#3a2e30' : '#1a1f2e');
  g.fillStyle = gr; g.fillRect(a - 40, top, b - a + 80, -top);
  g.fillStyle = '#1c1a24'; g.fillRect(a - 40, top - 14, b - a + 80, 14); g.fillStyle = `rgba(255,220,170,${0.1 + 0.25 * o.lit})`; g.fillRect(a - 40, top - 14, b - a + 80, 2);
  for (let r = 0; r < 24; r++) { g.fillStyle = `rgba(255,240,220,${0.03 + 0.05 * o.lit})`; g.fillRect(a - 40, -46 - r * 23 + 6, b - a + 80, 1.2); }
  // empty seats
  if (o.fill < 1) for (const f of FANS) { if (f.x < a - 20 || f.x > b + 20) continue; g.fillStyle = o.lit > 0.5 ? 'rgba(120,60,60,0.5)' : 'rgba(70,84,120,0.35)'; g.fillRect(f.x - 6, f.y - 3, 12, 6); }
  // fans
  const g0 = g; if (o.blur) { FB.setTransform(1, 0, 0, 1, 0, 0); FB.clearRect(0, 0, W, H); FB.setTransform(g0.getTransform()); g = FB; }
  for (const f of FANS) {
    if (f.x < a - 20 || f.x > b + 20) continue;
    const app = clamp((o.fill - f.d * 0.85) / 0.15); if (app <= 0) continue;
    const L = (0.35 + 0.4 * o.lit) * (1 - f.r * 0.015), warm = f.hue;
    const col = `rgba(${Math.round(lerp(150, 255, L * (0.7 + 0.3 * warm)))},${Math.round(lerp(130, 225, L * (0.6 + 0.3 * warm)))},${Math.round(lerp(120, 190, L * 0.7))},${app})`;
    const jump = o.cheer * Math.max(0, Math.sin(t * (7 + 3 * f.d) + f.ph)) * 3;
    g.fillStyle = col; g.beginPath(); g.ellipse(f.x, f.y - jump, 7.5, 6, 0, Math.PI, 0); g.fill();
    g.beginPath(); g.arc(f.x, f.y - 12 - jump, 4.8, 0, 7); g.fill();
    if (o.cheer > 0.1 && f.arms > 0.25) { g.strokeStyle = col; g.lineWidth = 2.6; g.lineCap = 'round'; const w = Math.sin(t * (9 + 4 * f.d) + f.ph) * 4 * o.cheer;
      g.beginPath(); g.moveTo(f.x - 5, f.y - 4 - jump); g.lineTo(f.x - 9 + w, f.y - 20 - jump); g.moveTo(f.x + 5, f.y - 4 - jump); g.lineTo(f.x + 9 + w, f.y - 20 - jump); g.stroke(); }
  }
  if (o.blur) { g = g0; g.save(); g.setTransform(1, 0, 0, 1, 0, 0); g.filter = `blur(${o.blur * KK}px)`; g.drawImage(fb, 0, 0); g.restore(); setLayer(g, c, p, 0); }
  // front wall with a lit band
  g.fillStyle = '#1b1a22'; g.fillRect(a - 40, -36, b - a + 80, 38);
  g.fillStyle = o.lit > 0.5 ? `rgba(255,190,110,${0.35 * o.lit})` : 'rgba(120,150,220,0.12)'; g.fillRect(a - 40, -30, b - a + 80, 3);
  return s;
}
function flashes(g, c, t, t0, t1, rate) { // camera flashes popping in the stands
  const p = 0.5; setLayer(g, c, p, 0); const [a, b] = visRange(c, p);
  for (let i = 0; i < rate * (t1 - t0); i++) { const tt = t0 + hash(i * 1.37 + 3) * (t1 - t0), dt = t - tt; if (dt < 0 || dt > 0.12) continue;
    const x = lerp(a, b, hash(i * 2.11)), y = -60 - hash(i * 4.7) * 700; const k = 1 - dt / 0.12;
    glowDot(g, x, y, 5 + 6 * hash(i), k, [255, 255, 255], [255, 255, 255]);
    g.save(); g.globalCompositeOperation = 'lighter'; g.strokeStyle = `rgba(255,255,255,${0.7 * k})`; g.lineWidth = 1.5; g.beginPath(); g.moveTo(x - 22 * k, y); g.lineTo(x + 22 * k, y); g.moveTo(x, y - 22 * k); g.lineTo(x, y + 22 * k); g.stroke(); g.restore(); }
}
function floodlights(g, t, on, cool = false) { // light banks along the top edge + their beams
  setScreen(g);
  const banks = [[90, 70], [360, 40], [630, 70]];
  banks.forEach(([x, y], i) => { const a = clamp(on * 3 - i);
    g.fillStyle = '#262632'; g.fillRect(x - 70, y - 22, 140, 36);
    for (let k = 0; k < 6; k++) { const lx = x - 55 + k * 22; g.fillStyle = a > 0 ? `rgba(255,248,230,${0.4 + 0.6 * a})` : 'rgba(90,96,120,0.6)'; g.beginPath(); g.arc(lx, y - 4, 7, 0, 7); g.fill(); if (a > 0) glowDot(g, lx, y - 4, 9, 0.5 * a, cool ? C.cool : [255, 230, 190], [255, 255, 245]); }
    if (a > 0) { g.save(); g.globalCompositeOperation = 'lighter'; const gr = g.createLinearGradient(0, y, 0, 900); gr.addColorStop(0, `rgba(255,236,200,${0.12 * a})`); gr.addColorStop(1, 'rgba(255,236,200,0)');
      g.fillStyle = gr; g.beginPath(); g.moveTo(x - 60, y); g.lineTo(x + 60, y); g.lineTo(x + 260 - i * 130, 900); g.lineTo(x - 140 - i * 130 + 260, 900); g.closePath(); g.fill(); g.restore(); }
  });
}
function confetti(g, t, t0, n = 160) { if (t < t0) return; setScreen(g); const dt = t - t0;
  for (let i = 0; i < n; i++) { const st = hash(i * 1.9) * 0.9; if (dt < st) continue; const u = dt - st;
    const x = hash(i * 3.1) * 760 - 20 + Math.sin(u * 3 + i) * 24, y = -30 + u * (220 + 160 * hash(i * 5.3)) + 60 * hash(i * 6.7);
    if (y > DH + 20) continue; const sp = u * (6 + 6 * hash(i)) + i;
    const cols = ['255,200,110', '255,240,220', '255,150,90', '200,220,255'];
    g.save(); g.translate(x, y); g.rotate(sp); g.scale(1, Math.abs(Math.cos(sp * 1.3)) + 0.15); g.fillStyle = `rgba(${cols[i % 4]},0.9)`; g.fillRect(-4, -2.2, 8, 4.4); g.restore(); }
}
function tape(g, c, x, t, tBreak) { // finish posts + tape at chest height; snaps and flutters away
  setWorld(g, c); const y = -104;
  g.strokeStyle = '#d8d2c6'; g.lineWidth = 4; for (const dx of [-10, 10]) { g.beginPath(); g.moveTo(x + dx, 0); g.lineTo(x + dx, y - 14); g.stroke(); }
  g.strokeStyle = 'rgba(255,255,255,0.9)'; g.lineWidth = 3;
  if (t < tBreak) { g.beginPath(); g.moveTo(x - 10, y); g.quadraticCurveTo(x, y + 4, x + 10, y); g.stroke(); return; }
  const k = clamp((t - tBreak) / 0.6);
  for (const sgn of [-1, 1]) { g.beginPath(); g.moveTo(x + 10 * sgn, y);
    for (let i = 1; i <= 8; i++) { const u = i / 8; g.lineTo(x + 10 * sgn - sgn * u * 10 + u * 40 * eout(k) * (sgn < 0 ? -0.3 : 1), y + u * 90 * eout(k) + Math.sin(u * 8 + t * 14) * 5 * k); }
    g.stroke(); }
}

// ---------- HUD (unzoomed; text inside y 300-1440 px = design 200-960) ----------
function fitFont(g, txt, weight, size, family, maxW) { g.font = `${weight} ${size}px "${family}"`; const w = g.measureText(txt).width; if (w > maxW) { size *= maxW / w; g.font = `${weight} ${size}px "${family}"`; } return size; }
function title(g, a, b, k, pop, shine = -1) {
  if (k <= 0) return; setScreen(g);
  g.save(); g.textAlign = 'center'; g.textBaseline = 'alphabetic'; g.letterSpacing = '0.5px'; g.globalAlpha *= k;
  g.translate(360, 260); g.scale(pop, pop); g.translate(-360, -260);
  const two = !!b;
  g.save(); g.fillStyle = 'rgba(12,13,18,0.58)'; g.shadowColor = 'rgba(0,0,0,0.45)'; g.shadowBlur = 18; g.beginPath(); g.roundRect(70, two ? 196 : 210, 580, two ? 118 : 92, 22); g.fill(); g.restore();
  g.shadowColor = 'rgba(0,0,0,0.6)'; g.shadowBlur = 12;
  fitFont(g, a, 900, 56, 'Inter Display', 530);
  let fs = 'rgba(255,200,110,1)';
  if (shine >= 0 && shine <= 1) { const x = lerp(40, 680, shine); const gr = g.createLinearGradient(x - 90, 0, x + 90, 0); gr.addColorStop(0, 'rgb(255,200,110)'); gr.addColorStop(0.5, 'rgb(255,250,230)'); gr.addColorStop(1, 'rgb(255,200,110)'); fs = gr; }
  g.fillStyle = fs; g.fillText(a, 360, two ? 252 : 275);
  if (two) { fitFont(g, b, 800, 40, 'Inter Display', 520); g.fillStyle = 'rgba(250,246,238,0.98)'; g.fillText(b, 360, 298); }
  g.restore();
}
function endTitle(g, k, pop, shine) { // v4: ~25% bigger close, punch line biggest
  if (k <= 0) return; setScreen(g); g.save(); g.globalAlpha *= k; g.textAlign = 'center'; g.translate(360, 300); g.scale(pop, pop); g.translate(-360, -300);
  g.save(); g.fillStyle = 'rgba(12,13,18,0.62)'; g.shadowColor = 'rgba(0,0,0,0.5)'; g.shadowBlur = 18; g.beginPath(); g.roundRect(80, 202, 560, 204, 24); g.fill(); g.restore();
  g.shadowColor = 'rgba(0,0,0,0.6)'; g.shadowBlur = 12; g.fillStyle = 'rgba(250,246,238,0.98)';
  fitFont(g, 'THEY CLAPPED', 850, 50, 'Inter Display', 520); g.fillText('THEY CLAPPED', 360, 254);
  fitFont(g, 'FOR THE FINISH.', 850, 50, 'Inter Display', 520); g.fillText('FOR THE FINISH.', 360, 306);
  fitFont(g, '6 AM BUILT IT.', 900, 74, 'Inter Display', 530);
  let fs = 'rgb(255,200,110)'; if (shine >= 0 && shine <= 1) { const x = lerp(40, 680, shine); const gr = g.createLinearGradient(x - 90, 0, x + 90, 0); gr.addColorStop(0, 'rgb(255,200,110)'); gr.addColorStop(0.5, 'rgb(255,250,230)'); gr.addColorStop(1, 'rgb(255,200,110)'); fs = gr; }
  g.fillStyle = fs; g.fillText('6 AM BUILT IT.', 360, 386); g.restore();
}
function dayPill(g, txt, t0, t, big = false) {
  const age = t - t0, pop = 1 + (big ? 0.6 : 0.3) * Math.exp(-age * 9), a = ss(0, 0.06, age);
  setScreen(g); g.save(); g.globalAlpha = a; const y = big ? 372 : 346; g.translate(360, y); g.scale(pop, pop);
  g.font = `800 ${big ? 46 : 26}px "JetBrains Mono"`; g.letterSpacing = '3px'; g.textAlign = 'center'; g.textBaseline = 'middle';
  const w = g.measureText(txt).width + (big ? 56 : 32), h = big ? 70 : 38;
  g.fillStyle = 'rgba(14,15,20,0.62)'; g.strokeStyle = big ? 'rgba(255,200,110,0.95)' : 'rgba(255,200,110,0.4)'; g.lineWidth = 2;
  g.beginPath(); g.roundRect(-w / 2, -h / 2, w, h, h / 2); g.fill(); g.stroke();
  g.shadowColor = rgba(C.gold, 0.7); g.shadowBlur = 10 * KK; g.fillStyle = 'rgba(255,214,150,1)'; g.fillText(txt, 0, 2);
  g.restore();
}
function caption(g, txt, a, age = 1) { // v2: gold pill + dark text so the run labels pop
  if (a <= 0) return; setScreen(g); g.save(); g.globalAlpha = a;
  const pop = 1 + 0.25 * Math.exp(-age * 12); g.translate(360, 400); g.scale(pop, pop);
  g.font = '900 42px "Inter Display"'; g.letterSpacing = '1px'; g.textAlign = 'center'; g.textBaseline = 'middle';
  const w = Math.min(560, g.measureText(txt).width + 56), h = 68;
  g.shadowColor = 'rgba(255,190,92,0.55)'; g.shadowBlur = 22 * KK; g.fillStyle = 'rgb(255,200,110)';
  g.beginPath(); g.roundRect(-w / 2, -h / 2, w, h, 16); g.fill();
  g.shadowBlur = 0; g.fillStyle = 'rgba(255,250,235,0.55)'; g.fillRect(-w / 2 + 14, -h / 2 + 3, w - 28, 2);
  g.fillStyle = '#16120c'; g.fillText(txt, 0, 3); g.restore(); }

// ---------- running helpers ----------
const STRIDE = 150; // design px per run cycle
function runner(t, t0, vfn) { const x = integ(vfn, t0, t), ph = 2 * Math.PI * x / STRIDE; return { x, ph, v: vfn(t) }; }
function runBlend(ph, v, vmax = 220) { const k = clamp(v / vmax); return mix(STAND, runPose(ph, lerp(0.05, 0.2, k), lerp(0.25, 1, k)), ss(0, 0.5, k) * 0.7 + 0.3 * k); }

// ---------- shots ----------
const S = {};
S.stadiumHook = (g, t) => {
  // payoff first: sprinting through the tape, packed stadium, flashes, confetti
  const v = tt => Math.max(0, 300 - 240 * Math.max(0, tt - 0.05)), r = runner(t, 0, v);
  const rx = -70 + r.x, FIN = -70 + integ(v, 0, TAPE1) + 22;
  const z = lerp(2.75, 2.5, eout(clamp(t / 1.6))), sh = t > TAPE1 && t < TAPE1 + 0.3 ? 3 * Math.sin(t * 70) * (1 - (t - TAPE1) / 0.3) : 0;
  const c = camAt(rx + 30, 870, z, sh);
  sky(g, [[0, '#1a1622'], [0.5, '#120f17'], [1, '#0d0b10']]);
  stands(g, c, t, { fill: 1, lit: 1, cheer: 1, blur: 1.2 });
  floodlights(g, t, 1);
  flashes(g, c, t, 0.1, 1.6, 34);
  ground(g, c, 'track', t);
  lightPool(g, c, rx + 20, 260, C.gold, 0.25);
  tape(g, c, FIN, t, TAPE1);
  const up = ss(0.22, 0.55, t), pose = armsUp(runPose(r.ph, lerp(0.22, 0.05, up), lerp(1, 0.55, clamp(t / 1.2))), up, t * 9);
  setWorld(g, c); fig(g, pose, rx, 0, { zoom: 1 });
  confetti(g, t, 0.14);
};
S.road = (g, t) => {
  // hard cut: same pose, alone under one streetlight at 6 AM
  const lt = t - T_CUT, k = ss(0.2, 0.75, lt);
  const c = camAt(30, 870, lerp(2.5, 2.2, eout(clamp(lt / 0.8))));
  sky(g, [[0, '#1a2440'], [0.55, '#0c1120'], [1, '#090b12']]);
  stars(g, 60, 0.6, t);
  houses(g, c, 0.42, t, 0.6);
  ground(g, c, 'road', t);
  streetlight(g, c, -70, 300, [255, 196, 120], 1, t);
  const base = runPose(1.2, 0.05, 0.55), pose = mix(armsUp(base, 1, 0), STANDDOWN, k);
  setWorld(g, c); fig(g, pose, 0, 0, { rim: 'rgba(255,214,160,0.4)' });
  setWorld(g, c); breath(g, 18, -150, t, 0.8);
  dust(g, t, 30, '200,215,255', 0.08);
};
S.bedroom = (g, t) => {
  const lt = t - T_BED, up = ss(0.3, 0.9, lt);
  const c = camAt(55, 900, lerp(2.0, 2.15, lt / 1.3));
  sky(g, [[0, '#0c1220'], [1, '#080a10']]);
  setWorld(g, c);
  // wall + window with deep blue pre-dawn light
  g.fillStyle = '#0e121c'; g.fillRect(-400, -600, 900, 600);
  g.fillStyle = '#16213a'; g.fillRect(-60, -300, 120, 130); g.strokeStyle = '#2a3348'; g.lineWidth = 5; g.strokeRect(-60, -300, 120, 130); g.beginPath(); g.moveTo(0, -300); g.lineTo(0, -170); g.moveTo(-60, -235); g.lineTo(60, -235); g.stroke();
  g.save(); g.globalCompositeOperation = 'lighter'; const wg = g.createLinearGradient(0, -170, 0, 0); wg.addColorStop(0, 'rgba(110,140,220,0.14)'); wg.addColorStop(1, 'rgba(110,140,220,0)'); g.fillStyle = wg;
  g.beginPath(); g.moveTo(-60, -170); g.lineTo(60, -170); g.lineTo(140, -40); g.lineTo(-40, -40); g.closePath(); g.fill(); g.restore();
  ground(g, c, 'floor', t);
  setWorld(g, c);
  // bed
  g.fillStyle = '#262a38'; g.fillRect(-60, -40, 200, 40); g.fillStyle = '#3a4058'; g.fillRect(-60, -44, 200, 8); g.fillStyle = '#2e3446'; g.fillRect(-72, -96, 12, 96);
  g.fillStyle = '#4a506a'; g.beginPath(); g.roundRect(-58, -58, 46, 16, 7); g.fill();
  // blanket over his legs
  fig(g, bedPose(up), 0, -44, { refl: false, breathe: 0.8 });
  setWorld(g, c); g.fillStyle = '#343b55'; g.beginPath(); g.roundRect(10, -58, 128, 18, 8); g.fill();
  // nightstand + alarm clock 5:58
  g.fillStyle = '#1e2230'; g.fillRect(160, -64, 70, 64);
  g.fillStyle = '#0b0c10'; g.beginPath(); g.roundRect(162, -104, 66, 40, 8); g.fill();
  const blink = (lt % 0.5) < 0.3;
  g.save(); g.font = '700 26px "JetBrains Mono"'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.shadowColor = 'rgba(255,90,60,0.9)'; g.shadowBlur = 14 * KK;
  g.fillStyle = 'rgba(255,110,80,1)'; g.fillText(blink ? '5:58' : '5 58', 195, -83); g.restore();
  glowDot(g, 195, -84, 22, 0.35, [255, 90, 60], [255, 150, 120]);
  dust(g, t, 25, '200,215,255', 0.06);
};
S.door = (g, t) => {
  const lt = t - T_DOOR, stand = ss(0.62, 0.95, lt), open = ss(0.7, 1.0, lt);
  const c = camAt(40, 900, lerp(2.7, 2.55, lt));
  sky(g, [[0, '#0d111b'], [1, '#090b10']]);
  setWorld(g, c);
  g.fillStyle = '#10141e'; g.fillRect(-400, -600, 900, 600);
  // door with cold dawn light through the gap
  const dx = 110; g.fillStyle = '#1a2032'; g.fillRect(dx, -230, 84, 230); g.strokeStyle = '#2b3246'; g.lineWidth = 6; g.strokeRect(dx - 3, -233, 90, 233);
  const gap = 4 + 40 * open;
  g.fillStyle = `rgba(150,180,240,${0.55 + 0.35 * open})`; g.fillRect(dx, -230, gap, 230);
  g.save(); g.globalCompositeOperation = 'lighter'; const lg = g.createLinearGradient(dx, 0, dx - 260, 0); lg.addColorStop(0, `rgba(130,160,230,${0.18 + 0.25 * open})`); lg.addColorStop(1, 'rgba(130,160,230,0)');
  g.fillStyle = lg; g.beginPath(); g.moveTo(dx, -230); g.lineTo(dx, 0); g.lineTo(dx - 260, 40); g.lineTo(dx - 260, -60); g.closePath(); g.fill(); g.restore();
  ground(g, c, 'floor', t);
  lightPool(g, c, dx - 40, 160, C.cool, 0.25 + 0.3 * open);
  const tug = Math.sin(lt * 22) * 3 * (1 - stand);
  const cr = Object.assign({}, CROUCH, { hd1: [CROUCH.hd1[0] + tug, CROUCH.hd1[1] - Math.abs(tug)], hd2: [CROUCH.hd2[0] - tug, CROUCH.hd2[1]] });
  setWorld(g, c); fig(g, mix(cr, STAND, stand), 0, 0, { rim: 'rgba(190,210,255,0.4)' });
  setWorld(g, c);
  if (stand < 0.5) { g.strokeStyle = 'rgba(255,240,220,0.9)'; g.lineWidth = 1.6; g.beginPath(); g.moveTo(22, -6); g.quadraticCurveTo(28 + tug, -20, 30 + tug, -28); g.stroke(); }
};
function runShot(g, t, t0, o) {
  const r = runner(t, t0, o.v), rx = (o.x0 || 0) + r.x;
  const gyFn = o.gy || (() => 0), gy = gyFn(rx);
  const c = camAt(rx + (typeof o.lead === 'function' ? -90 + 40 * (t - t0) : (o.lead ?? 40)), o.gs ?? 880, o.z(t - t0), 0); c.cy += gy;
  o.bg(c, rx);
  const pose = o.pose ? o.pose(t, r) : runBlend(r.ph, r.v);
  setWorld(g, c); fig(g, pose, rx, gy, { rim: o.rim, sweat: o.sweat, reflA: o.reflA, refl: o.refl });
  if (o.fg) o.fg(c, rx, r);
  return { c, rx, r };
}
S.street = (g, t) => {
  runShot(g, t, T_RUN1, { v: () => 220, z: lt => lerp(2.45, 2.3, lt / 1.8), rim: 'rgba(190,210,255,0.45)',
    bg: (c) => { sky(g, [[0, '#172038'], [0.6, '#0c1120'], [1, '#090b12']]); stars(g, 50, 0.5, t); houses(g, c, 0.45, t, 0.9); ground(g, c, 'road', t);
      for (let i = -1; i < 6; i++) streetlight(g, c, 120 + i * 330, 310, [255, 196, 120], 1, t); },
    fg: (c, rx) => { setWorld(g, c); breath(g, rx + 34, -148, t, 1); } });
  dust(g, t, 25, '200,215,255', 0.07);
};
S.rain = (g, t) => {
  runShot(g, t, T_RAIN, { v: () => 230, z: lt => lerp(3.15, 3.0, lt), gs: 1010, lead: 10, rim: 'rgba(190,210,255,0.5)', reflA: 0.25, x0: 400,
    bg: (c) => { sky(g, [[0, '#0f1626'], [0.6, '#0c111d'], [1, '#0a0d16']]); houses(g, c, 0.4, 99, 0.7); ground(g, c, 'wet', t);
      for (let i = -1; i < 6; i++) streetlight(g, c, 300 + i * 300, 300, [255, 180, 100], 1, t); splashes(g, c, t); },
    fg: () => rain(g, t, 1) });
};
S.fall = (g, tReal) => {
  const lw = tReal - T_FALL, t = T_FALL + (lw < 0.18 ? lw : lw < 0.78 ? 0.18 + (lw - 0.18) * 0.5 : 0.48 + (lw - 0.78) * 2.36);
  const tr = 7.72, v = tt => tt < tr ? 220 : tt < FALL_HIT ? 220 * (1 - (tt - tr) / (FALL_HIT - tr)) : tt < 8.32 ? 0 : 200 * ss(8.32, 8.5, tt);
  runShot(g, t, T_FALL, { v, z: lt => 2.45 + 0.55 * ss(0.15, 0.45, lt) * (1 - ss(0.5, 0.8, lt)), x0: 900, rim: 'rgba(190,210,255,0.45)',
    pose: (tt, r) => {
      const run = runBlend(r.ph, Math.max(r.v, tt < 8.3 ? 220 : r.v));
      if (tt < tr) return run;
      if (tt < 7.86) return mix(run, FALLMID, eio((tt - tr) / 0.14));
      if (tt < FALL_HIT) return mix(FALLMID, PRONE, eio((tt - 7.86) / (FALL_HIT - 7.86)));
      if (tt < 8.1) return PRONE;
      if (tt < 8.3) return mix(PRONE, CROUCH, eio((tt - 8.1) / 0.2));
      return mix(CROUCH, run, eio(clamp((tt - 8.3) / 0.16)));
    },
    bg: (c) => { sky(g, [[0, '#172038'], [0.6, '#0c1120'], [1, '#090b12']]); stars(g, 40, 0.4, t); city(g, c, 0.3, '#121827', t); ground(g, c, 'wet', t);
      for (let i = 0; i < 6; i++) streetlight(g, c, 760 + i * 340, 300, [255, 196, 120], 1, t); },
    fg: (c, rx) => { if (t > FALL_HIT && t < FALL_HIT + 0.35) { setWorld(g, c); const k = (t - FALL_HIT) / 0.35;
      for (let i = 0; i < 14; i++) { g.fillStyle = `rgba(200,220,255,${0.7 * (1 - k)})`; g.beginPath(); g.arc(rx + 50 + (hash(i) * 2 - 1) * 70 * k, -30 * Math.sin(k * 3) * hash(i + 3) - 2, 2, 0, 7); g.fill(); } } } });
};
S.track = (g, t) => {
  runShot(g, t, T_TRACK, { v: () => 240, z: lt => lerp(1.3, 1.45, lt), gs: 930, lead: lt => 0, rim: 'rgba(190,210,255,0.45)',
    bg: (c) => { sky(g, [[0, '#0b0f1a'], [1, '#08090e']]); stands(g, c, t, { fill: 0, lit: 0, cheer: 0 }); floodlights(g, t, 0.34, true); ground(g, c, 'track', t);
      lightPool(g, c, c.cx - 120, 300, C.cool, 0.2); } });
  dust(g, t, 30, '200,215,255', 0.08);
};
const STEP_W = 44, STEP_H = 18;
const stepY = x => x < 0 ? 0 : -STEP_H * Math.floor(x / STEP_W);
S.steps = (g, t) => {
  runShot(g, t, T_STEPS, { v: () => 190, z: lt => lerp(2.35, 2.5, lt), gs: 900, rim: 'rgba(255,200,150,0.5)', x0: 70, refl: false,
    gy: x => -STEP_H * (x / STEP_W) + 9,
    bg: (c) => {
      sky(g, [[0, '#18203a'], [0.35, '#2c2c4a'], [0.62, '#7a4a52'], [0.78, '#d88a58'], [1, '#2a1e22']]);
      setScreen(g); glowDot(g, 520, 760, 60, 0.6, [255, 170, 100], [255, 220, 170]);
      const c2 = Object.assign({}, c, { cy: c.cy + 160 }); city(g, c2, 0.25, '#2a2034', t);
      setWorld(g, c); const x0 = c.cx - 400 / c.z, x1 = c.cx + 400 / c.z, yb = c.cy + 700 / c.z;
      g.fillStyle = '#2a2530'; g.beginPath(); g.moveTo(x0, yb); g.lineTo(x0, stepY(x0));
      for (let x = Math.floor(Math.max(0, x0) / STEP_W) * STEP_W; x < x1 + STEP_W; x += STEP_W) { g.lineTo(x, stepY(x - 1)); g.lineTo(x, stepY(x)); g.lineTo(x + STEP_W, stepY(x)); }
      g.lineTo(x1 + STEP_W, yb); g.closePath(); g.fill();
      for (let x = Math.floor(Math.max(0, x0) / STEP_W) * STEP_W; x < x1 + STEP_W; x += STEP_W) { g.fillStyle = 'rgba(255,200,150,0.35)'; g.fillRect(x, stepY(x) - 1, STEP_W, 2); g.fillStyle = 'rgba(0,0,0,0.25)'; g.fillRect(x, stepY(x) + 1, 3, STEP_H); }
    } });
};
S.rehook = (g, t) => {
  const lt = t - T_STOP;
  const v = tt => 220 * (1 - ss(T_STOP, T_STOP + 0.4, tt));
  const r = runner(t, T_STOP, v), rx = r.x;
  const c = camAt(rx + 20, 880, lerp(2.2, 2.55, eio(clamp(lt / 1.5))));
  sky(g, [[0, '#0e1424'], [1, '#090b12']]); stands(g, c, t, { fill: 0, lit: 0, cheer: 0 }); floodlights(g, t, 0.34, true); ground(g, c, 'track', t);
  lightPool(g, c, rx, 240, C.cool, 0.22);
  const kk = ss(0.3, 0.6, lt), heave = Math.sin(lt * 9) * 3 * kk;
  const UP = Object.assign({}, STAND, { head: [-6, -150], sh: [-2, -124] }); const st = ss(1.0, 1.4, lt);
  let p = mix(mix(runBlend(r.ph, r.v), KNEES, kk), UP, st); p = Object.assign({}, p, { sh: [p.sh[0], p.sh[1] + heave], head: [p.head[0], p.head[1] + heave * 1.2] });
  setWorld(g, c); fig(g, p, rx, 0, { rim: 'rgba(190,210,255,0.45)', sweat: true, breathe: 0 });
  setWorld(g, c); breath(g, rx + 66, -108, t, 1.2);
  dust(g, t, 30, '200,215,255', 0.08);
};
S.finale = (g, t) => {
  const lt = t - T_365;
  const LO = T_365 + 0.4; // lights out until LO, then three banks slam on
  const v = tt => tt < T_TAPE2 ? 300 * ss(LO + 0.05, LO + 0.45, tt) : Math.max(0, 300 - 270 * (tt - T_TAPE2));
  const r = runner(t, T_365, v), rx = r.x, FIN = integ(v, T_365, T_TAPE2) + 22;
  const on = ((lt >= 0.4) + (lt >= 0.55) + (lt >= 0.7)) / 3, fill = ss(0.6, 1.3, lt), cheer = ss(0.7, 1.4, lt);
  const z = lt < 0.4 ? lerp(2.55, 2.65, lt / 0.4) : lerp(2.2, 2.6, eio(clamp((lt - 0.5) / 1.2)));
  const c = camAt(rx + 30, 870, z, t > T_TAPE2 && t < T_TAPE2 + 0.3 ? 3 * Math.sin(t * 70) : 0);
  sky(g, [[0, on > 0.5 ? '#1a1622' : on > 0 ? '#121420' : '#08090e'], [1, on > 0 ? '#0d0b10' : '#060608']]);
  stands(g, c, t, { fill, lit: on, cheer, blur: 1.2 });
  floodlights(g, t, on, on < 0.5);
  flashes(g, c, t, T_365 + 1.0, T_CLOSE, 30);
  ground(g, c, 'track', t);
  lightPool(g, c, rx + 20, 260, C.gold, 0.25 * on);
  tape(g, c, FIN, t, T_TAPE2);
  if (on === 0) { setScreen(g); g.fillStyle = 'rgba(4,5,8,0.6)'; g.fillRect(0, 0, DW, DH); }
  const up = ss(T_TAPE2 + 0.08, T_TAPE2 + 0.4, t);
  const UPL = Object.assign({}, STAND, { head: [-6, -150], sh: [-2, -124] }); const pose = armsUp(mix(UPL, runBlend(r.ph, Math.max(r.v, 120), 300), ss(LO, LO + 0.3, t)), up, t * 9);
  setWorld(g, c); fig(g, pose, rx, 0, { alpha: on > 0 ? 1 : 0.55 });
  confetti(g, t, T_TAPE2 + 0.02);
};
S.close = (g, t) => {
  const lt = t - T_CLOSE;
  const v = tt => Math.max(0, 290 - 260 * (tt - T_TAPE2));
  const rx = integ(v, T_365, T_CLOSE) + integ(v, T_CLOSE, t), r = runner(T_CLOSE, T_365, v);
  const turn = ss(0.5, 1.1, lt), dir = Math.cos(Math.PI * turn);
  const c = camAt(rx + lerp(30, -10, eio(clamp(lt / 2))), 900, lerp(2.6, 1.9, eio(clamp(lt / 1.2))));
  sky(g, [[0, '#1a1622'], [1, '#0d0b10']]);
  stands(g, c, t, { fill: 1, lit: lerp(1, 0.75, turn), cheer: lerp(1, 0.6, turn), blur: 2.2 }); floodlights(g, t, 1);
  setScreen(g); g.fillStyle = `rgba(8,9,14,${0.2 + 0.3 * turn})`; g.fillRect(0, 0, DW, DH);
  ground(g, c, 'track', t);
  lightPool(g, c, rx, 260, C.gold, 0.22);
  const down = ss(0.1, 0.6, lt), base = armsUp(runBlend(r.ph, 0, 290), 1, t * 9), pose = mix(base, STANDDOWN, down);
  setWorld(g, c); fig(g, pose, rx, 0, { dir: Math.abs(dir) < 0.12 ? 0.12 * Math.sign(dir || 1) : dir });
  confetti(g, t, T_TAPE2 + 0.02, 120);
};

function shotAt(t) { let s = SHOTS[0]; for (const x of SHOTS) if (t >= x[0]) s = x; return s; }
function frame(g, t) {
  T = t;
  const [t0, name] = shotAt(t);
  S[name](g, t);
  // vignette + grain (30 Friends finish, light enough that edges keep texture)
  setScreen(g);
  { const gr = g.createRadialGradient(360, 620, 280, 360, 640, 900); gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(1, 'rgba(0,0,0,0.38)'); g.fillStyle = gr; g.fillRect(0, 0, DW, DH);
    if (!window._grain) { window._grain = []; for (let n = 0; n < 4; n++) { const c = document.createElement('canvas'); c.width = c.height = 256; const x = c.getContext('2d'); const im = x.createImageData(256, 256);
      for (let p = 0; p < im.data.length; p += 4) { const v = Math.random() * 255; im.data[p] = im.data[p + 1] = im.data[p + 2] = v; im.data[p + 3] = 255; } x.putImageData(im, 0, 0); window._grain.push(c); } }
    g.save(); g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 0.05; g.globalCompositeOperation = 'overlay'; g.fillStyle = g.createPattern(window._grain[((Math.floor(t * 30) % 4) + 4) % 4], 'repeat'); g.fillRect(0, 0, W, H); g.restore(); setScreen(g); }
  // flash frame on the hard cuts that matter
  for (const [tc, a] of [[TAPE1, 0.35], [T_365 + 0.4, 0.4], [T_TAPE2, 0.3]]) if (t >= tc && t < tc + 0.12) { g.fillStyle = `rgba(255,240,220,${a * (1 - (t - tc) / 0.12)})`; g.fillRect(0, 0, DW, DH); }
  // titles
  const hp = (t0v) => 1 + 0.14 * Math.exp(-Math.max(0, t - t0v) * 9);
  if (t < T_CUT) title(g, 'EVERYONE CLAPS NOW.', '', 1, hp(0), (t - 0.1) / 0.7);
  else if (t < T_STOP) title(g, 'NOBODY CLAPPED', 'AT 6 AM.', 1, hp(T_CUT), t < T_CUT + 0.9 ? (t - T_CUT - 0.05) / 0.7 : -1);
  else if (t < T_365) title(g, 'JUST HIM.', 'EVERY DAY.', 1, hp(T_STOP), (t - T_STOP - 0.05) / 0.7);
  else if (t >= T_CLOSE) endTitle(g, ss(T_CLOSE, T_CLOSE + 0.15, t), hp(T_CLOSE), (t - T_CLOSE - 0.25) / 0.7);
  // day counter
  let day = null; for (const d of DAYS) if (t >= d[0]) day = d; if (t >= T_CLOSE) day = null;
  if (day && t >= T_RUN1) { let txt = day[1]; const i = DAYS.indexOf(day), age = t - day[0];
    if (i > 0 && age < 0.3 && i < DAYS.length - 1) { const a = +DAYS[i - 1][1].slice(4), b = +day[1].slice(4); txt = 'DAY ' + Math.round(lerp(a, b, eout(age / 0.3))); }
    if (!(t >= T_365 && t < T_365 + 0.4)) dayPill(g, txt, day[0], t, day[0] === T_365 + 0.4); }
  // small lock-in lines
  const cap = [[T_RUN1 + 0.25, T_RAIN, 'No crowd.'], [T_RAIN + 0.15, T_FALL, 'No likes.'], [T_FALL + 0.15, T_TRACK, 'No applause.'], [T_TRACK + 0.15, T_STEPS, 'No one watching.'], [T_STEPS + 0.12, T_STOP, 'Still showing up.']];
  for (const [a, b, txt] of cap) if (t >= a && t < b) caption(g, txt.toUpperCase(), ss(a, a + 0.08, t), t - a);
  if (t >= T_BED && t < T_RUN1) caption(g, '5:58 AM.', ss(T_BED + 0.1, T_BED + 0.18, t), t - T_BED - 0.1);
  const ca = ss(T_CTA, T_CTA + 0.3, t);
  if (ca > 0) { setScreen(g); g.save(); g.globalAlpha = ca; g.fillStyle = 'rgba(12,13,18,0.55)'; g.beginPath(); g.roundRect(110, 424, 500, 100, 20); g.fill();
    g.font = '800 38px "Inter"'; g.textAlign = 'center'; g.shadowColor = 'rgba(0,0,0,0.8)'; g.shadowBlur = 10; g.fillStyle = 'rgba(250,246,238,0.98)';
    g.fillText('Send this to someone', 360, 466); g.fillText('training in the dark 💛', 360, 510); g.restore(); }
  setScreen(g); g.save(); g.font = '600 11px "JetBrains Mono"'; g.letterSpacing = '5px'; g.textAlign = 'center'; g.fillStyle = 'rgba(242,238,230,0.28)'; g.fillText('SLOW LIGHT', 360, 1270); g.restore();
}

window.renderAt = (t, sub = 1) => {
  sub = Math.max(1, sub | 0);
  if (sub === 1) { frame(out, t); }
  else {
    out.setTransform(1, 0, 0, 1, 0, 0); out.fillStyle = '#000'; out.fillRect(0, 0, W, H);
    for (let i = 0; i < sub; i++) {
      // keep sub-frames inside the current shot so hard cuts stay hard
      let ts = t + (i / sub - 0.5) * (1 / 30) * 0.5; const st = shotAt(t)[0]; if (ts < st) ts = st;
      A.setTransform(1, 0, 0, 1, 0, 0); frame(A, ts);
      out.setTransform(1, 0, 0, 1, 0, 0); out.globalCompositeOperation = 'lighter'; out.globalAlpha = 1 / sub; out.drawImage(acc, 0, 0);
    }
    out.globalCompositeOperation = 'source-over'; out.globalAlpha = 1;
  }
  return cv.toDataURL('image/jpeg', 0.95);
};

// sound cues for mix.py (beds are built in mix.py from TL)
window.events = (() => {
  const e = [];
  e.push({ t: 0, s: 'roar', g: 1.0, pan: 0 }, { t: 0.0, s: 'slam', g: 0.55, pan: 0 }, { t: TAPE1 - 0.02, s: 'tape', g: 0.7, pan: 0.1 }, { t: 0.2, s: 'flash', g: 0.5, pan: -0.3 }, { t: 0.8, s: 'flash', g: 0.4, pan: 0.35 });
  e.push({ t: T_CUT + 0.35, s: 'alarm', g: 0.75, pan: 0.2 });
  e.push({ t: T_BED, s: 'alarm3', g: 0.7, pan: 0.35 }, { t: T_BED + 0.3, s: 'bed', g: 0.6, pan: 0 });
  e.push({ t: T_DOOR + 0.05, s: 'lace', g: 0.7, pan: 0 }, { t: T_DOOR + 0.7, s: 'door', g: 0.6, pan: 0.3 });
  e.push({ t: SWITCH_OFF - 0.02, s: 'switch', g: 0.5, pan: 0.25 });
  e.push({ t: FALL_SND - 0.04, s: 'fall', g: 1.0, pan: 0 });
  e.push({ t: T_STOP + 0.3, s: 'pant', g: 0.85, pan: 0 }, { t: T_STOP + 0.2, s: 'heart', g: 0.75, pan: 0 });
  e.push({ t: T_365 - 0.02, s: 'switch', g: 0.7, pan: 0 }); for (const k of [0, 0.15, 0.3]) e.push({ t: T_365 + 0.4 + k, s: 'slam', g: 0.8 + k, pan: 0 });
  e.push({ t: T_365 + 0.75, s: 'roar2', g: 0.55, pan: 0 }, { t: T_TAPE2 - 0.25, s: 'roar', g: 1.0, pan: 0 }, { t: T_TAPE2 - 0.02, s: 'tape', g: 0.7, pan: 0.1 }, { t: T_TAPE2, s: 'slam', g: 0.7, pan: 0 },
    { t: T_TAPE2 + 0.1, s: 'flash', g: 0.5, pan: 0.3 }, { t: T_TAPE2 + 0.7, s: 'flash', g: 0.4, pan: -0.3 }, { t: T_CLOSE - 0.3, s: 'roar2', g: 0.8, pan: 0 });
  return e.sort((a, b) => a.t - b.t);
})();
window.TL = { T_CUT, T_BED, T_DOOR, T_RUN1, T_RAIN, T_FALL, T_TRACK, T_STEPS, T_STOP, T_365, T_TAPE2, T_CLOSE, T_CTA, FALL_HIT, FALL_SND, DUR };
window.DUR = DUR;
document.fonts.load('600 20px "JetBrains Mono"').then(() => document.fonts.load('800 30px "JetBrains Mono"')).then(() => document.fonts.load('900 56px "Inter Display"')).then(() => document.fonts.load('700 34px "Inter"')).then(() => { window.ready = true; });
