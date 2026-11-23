// Don't Tell Your Dreams, in the Silence Is Distance (v8) look: Canvas 2D, design space 720x1280 scaled to the render
// size, navy gradient with a warm wash and drifting motes, glowing cream stickmen, gold light. A shot-for-shot restaging
// of the owner's reference reel; every cut, beat and lyric time is in timeline.json (measured at 30 fps).
// Story: a small hero holds a glowing star (his dream) among four tall smiling friends. They turn: knives behind their
// backs, hands reaching for the star. He hugs it, closes his eyes, takes it into his chest, opens them determined,
// grows tall; the light bursts out of him and throws them to the floor.
// window.renderAt(t, sub) -> JPEG data URL (sub = motion-blur samples, never across a cut). window.metaAt(t) -> {shot}.
'use strict';
const DW = 720, DH = 1280;
const qs = new URLSearchParams(location.search);
const W = +(qs.get('w') || 1080), H = +(qs.get('h') || 1920);
const cv = document.createElement('canvas'); cv.width = W; cv.height = H; document.body.appendChild(cv);
const out = cv.getContext('2d');
const acc = document.createElement('canvas'); acc.width = W; acc.height = H; const A = acc.getContext('2d');
let TL, DUR, T = 0;

// ---------- helpers ----------
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, k) => a + (b - a) * k;
const ss = (a, b, x) => { const k = clamp((x - a) / (b - a)); return k * k * (3 - 2 * k); };
const eout = k => 1 - Math.pow(1 - k, 3);
const bump = (t, a, d) => { const x = (t - a) / d; return x <= 0 || x >= 1 ? 0 : Math.sin(Math.PI * x) ** 2; };
const L2 = (a, b, k) => [lerp(a[0], b[0], k), lerp(a[1], b[1], k)];
function hash(i) { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }

// ---------- palette (Silence) ----------
const C = { bgTop: '#191b24', bgMid: '#111219', bgBot: '#16171f', fig: '#fff7ea', figBack: '#cfc8bd', ink: '#1b1d27', gold: [255, 190, 92], goldHot: [255, 232, 180] };
const rgba = (c, a) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;

// ---------- shots and cameras ----------
// camera: world x -> 360 + (x - cx) * z ; world y (floor = 0, up negative) -> fy + y * z  (fy = floor's screen y)
let SHOTS = [];
const shotAt = t => SHOTS.filter(s => t >= s.t0).pop();
function camFor(sh, t) {
  const u = clamp((t - sh.t0) / (sh.t1 - sh.t0));
  switch (sh.name) {
    case 'A': { const p = ss(TL.A.turn0, sh.t1, t); return { cx: -40 * p, z: 1.0 + 0.05 * u, fy: 1290 }; }
    case 'B': { const z = 1.3 + 0.07 * u; return { cx: 0, z, fy: 415 + 810 * z }; }
    case 'C': return { cx: -30, z: 1.1 + 0.04 * u, fy: 330 + 810 * 1.1 };
    case 'D': { const z = 1.22 + 0.12 * eout(u); return { cx: 0, z, fy: 430 + 800 * z }; }
    case 'E': { const p = ss(TL.E.push0, sh.t1, t); const z = 2.7 + 0.08 * u + 0.45 * p; return { cx: 0, z, fy: lerp(420, 380, p) + 805 * z }; }
    case 'F': { const k = t >= TL.F.burst ? Math.exp(-(t - TL.F.burst) * 6) : 0; return { cx: 8 * k * Math.sin(t * 80), z: 0.62 - 0.02 * u, fy: 1080 + 7 * k * Math.sin(t * 67) }; }
  }
}
let CAM;
const SX = x => 360 + (x - CAM.cx) * CAM.z, SY = y => CAM.fy + y * CAM.z;

// ---------- background (Silence) ----------
function background(g, t) {
  let gr = g.createLinearGradient(0, 0, 0, DH);
  gr.addColorStop(0, C.bgTop); gr.addColorStop(0.5, C.bgMid); gr.addColorStop(1, C.bgBot);
  g.fillStyle = gr; g.fillRect(0, 0, DW, DH);
  gr = g.createRadialGradient(360, 560, 10, 360, 560, 520); gr.addColorStop(0, 'rgba(255,190,110,0.10)'); gr.addColorStop(1, 'rgba(255,190,110,0)');
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
// the floor: one glossy ledge across the frame (the Silence ledge, full width)
function floor(g) {
  const y0 = SY(0); if (y0 > DH + 40) return; const z = CAM.z, top = 21 * z, front = 24 * z, depth = 160 * z, tone = [62, 60, 64];
  let gr = g.createLinearGradient(0, y0 - top, 0, y0 + front);
  gr.addColorStop(0, `rgba(${tone[0] + 26},${tone[1] + 26},${tone[2] + 28},1)`); gr.addColorStop(0.45, `rgba(${tone[0]},${tone[1]},${tone[2]},1)`); gr.addColorStop(1, `rgba(${tone[0] - 22},${tone[1] - 22},${tone[2] - 20},1)`);
  g.fillStyle = gr; g.fillRect(-50, y0 - top, DW + 100, top + front);
  gr = g.createLinearGradient(0, y0 + front, 0, y0 + front + depth);
  gr.addColorStop(0, `rgba(${tone[0] - 30},${tone[1] - 30},${tone[2] - 26},1)`); gr.addColorStop(1, `rgba(${tone[0] - 30},${tone[1] - 30},${tone[2] - 26},0)`);
  g.fillStyle = gr; g.fillRect(-50, y0 + front, DW + 100, depth);
  g.fillStyle = 'rgba(255,236,205,0.55)'; g.fillRect(-50, y0 + front - 1.2 * z, DW + 100, 1.6 * z);
  g.fillStyle = 'rgba(255,255,255,0.10)'; g.fillRect(-50, y0 - top, DW + 100, 1.2 * z);
}
function shadow(g, x, w, a = 0.45) { const y = SY(-6); g.save(); g.fillStyle = `rgba(0,0,0,${a})`; g.beginPath(); g.ellipse(SX(x), y, w * CAM.z, 9 * CAM.z, 0, 0, 7); g.fill(); g.restore(); }

// ---------- the rig: front view, world px; the hero is 860 tall at s = 1 ----------
function ik(sh, tg, a, b, bend) {
  const dx = tg[0] - sh[0], dy = tg[1] - sh[1]; const d = Math.hypot(dx, dy); const dd = clamp(d, 1e-3, a + b - 0.5);
  const ux = dx / (d || 1), uy = dy / (d || 1); const x = (a * a - b * b + dd * dd) / (2 * dd), h = Math.sqrt(Math.max(0, a * a - x * x));
  const el = [sh[0] + ux * x - uy * h * bend, sh[1] + uy * x + ux * h * bend]; return { el, hd: [sh[0] + ux * dd, sh[1] + uy * dd] };
}
function joints(b) {
  const s = b.s, hip = [b.x, b.y - 470 * s], lean = b.lean || 0, hunch = b.hunch || 0;
  const sh = [hip[0] + lean, hip[1] - 280 * s * (1 - 0.15 * hunch)];
  const head = [sh[0] + lean * 0.35 + (b.look || 0) * 10 * s, sh[1] - (40 + b.hr) * s + hunch * 30 * s];
  const lg = b.legs || [0.1, -0.1], kn = (side, a) => [hip[0] + side * 20 * s + Math.sin(a) * 235 * s, hip[1] + Math.cos(a) * 235 * s];
  const knL = kn(-1, -Math.abs(lg[0]) * 0.6), knR = kn(1, Math.abs(lg[1]) * 0.6);
  const ftL = [knL[0] - Math.abs(lg[0]) * 60 * s - 10 * s, b.y], ftR = [knR[0] + Math.abs(lg[1]) * 60 * s + 10 * s, b.y];
  const J = { hip, sh, head, knL, knR, ftL, ftR };
  for (const side of ['L', 'R']) { const arm = b.arms[side], sgn = side === 'L' ? -1 : 1; const so = [sh[0] + sgn * 14 * s, sh[1] + 10 * s];
    const r = arm.el ? { el: arm.el, hd: arm.h } : ik(so, arm.h, 150 * s, 140 * s, arm.bend ?? sgn); J['so' + side] = so; J['el' + side] = r.el; J['hd' + side] = r.hd; }   // arm.el: a hand-placed elbow (the hug)
  if (b.rot || b.moveHip) { const c = Math.cos(b.rot || 0), sn = Math.sin(b.rot || 0), p = J.hip.slice(), to = b.moveHip || p;
    for (const k in J) { const v = J[k], dx = v[0] - p[0], dy = v[1] - p[1]; J[k] = [to[0] + dx * c - dy * sn, to[1] + dx * sn + dy * c]; } }
  return J;
}
function drawBody(g, b, J) {
  const z = CAM.z, s = b.s, lw = 12 * s * z, P = p => [SX(p[0]), SY(p[1])];
  g.save(); g.globalAlpha = b.alpha ?? 1; g.lineCap = 'round'; g.lineJoin = 'round';
  g.shadowColor = 'rgba(255,214,160,0.42)'; g.shadowBlur = 9 * z * Math.min(2, s) * (W / DW);
  const seg = (pts, col, w) => { g.strokeStyle = col; g.lineWidth = w; g.beginPath(); const p0 = P(pts[0]); g.moveTo(p0[0], p0[1]); for (let i = 1; i < pts.length; i++) { const p = P(pts[i]); g.lineTo(p[0], p[1]); } g.stroke(); };
  const col = b.dim ? C.figBack : C.fig;
  for (const side of ['L', 'R']) { const kn = b.arms[side].knife; if (kn && kn.behind) knife(g, J['hd' + side], kn.ang, s, kn.a ?? 1); }   // behind the body
  seg([J.hip, J.knL, J.ftL], col, lw); seg([J.hip, J.knR, J.ftR], col, lw);
  seg([J.sh, J.hip], col, lw * 1.05);
  for (const side of ['L', 'R']) { seg([J.sh, J['so' + side], J['el' + side], J['hd' + side]], col, lw * 0.92); if (b.arms[side].claw) claw(g, J['el' + side], J['hd' + side], s, col); }
  const hc = P(J.head), hr = b.hr * s * z; g.fillStyle = col; g.beginPath(); g.arc(hc[0], hc[1], hr, 0, 7); g.fill();
  g.shadowBlur = 0; if (b.hair) hair(g, hc, hr, b.rot || 0); face(g, hc, hr, b.face, b.look || 0, b.rot || 0);
  for (const side of ['L', 'R']) { const kn = b.arms[side].knife; if (kn && !kn.behind) knife(g, J['hd' + side], kn.ang, s, kn.a ?? 1); }
  g.restore();
}
function claw(g, el, hd, s, col) { // three curled fingers off the hand, pointing along the forearm
  const z = CAM.z, a = Math.atan2(hd[1] - el[1], hd[0] - el[0]); g.save(); g.strokeStyle = col; g.lineWidth = 6 * s * z; g.lineCap = 'round';
  for (let i = -1; i <= 1; i++) { const aa = a + i * 0.45, x0 = SX(hd[0]), y0 = SY(hd[1]), l = 26 * s * z;
    const x1 = x0 + Math.cos(aa) * l, y1 = y0 + Math.sin(aa) * l; g.beginPath(); g.moveTo(x0, y0); g.quadraticCurveTo(x1, y1, x1 + Math.cos(aa + 1.4) * l * 0.45, y1 + Math.sin(aa + 1.4) * l * 0.45); g.stroke(); }
  g.restore(); }
function hair(g, hc, hr, rot) { g.save(); g.translate(hc[0], hc[1]); g.rotate(rot); g.strokeStyle = C.fig; g.lineWidth = hr * 0.11; g.lineCap = 'round';
  [[-0.32, -0.5], [-0.08, -0.12], [0.18, 0.25], [0.4, 0.55]].forEach(([x, a]) => { const bx = x * hr, by = -Math.sqrt(1 - x * x) * hr * 0.96; g.beginPath(); g.moveTo(bx, by); g.quadraticCurveTo(bx + Math.sin(a) * hr * 0.2, by - hr * 0.3, bx + Math.sin(a) * hr * 0.42, by - hr * 0.42); g.stroke(); });
  g.restore(); }
function knife(g, hd, ang, s, a) { if (a <= 0.01) return; const z = CAM.z, x = SX(hd[0]), y = SY(hd[1]); g.save(); g.globalAlpha *= a; g.translate(x, y); g.rotate(ang); g.scale(s * z, s * z); g.shadowBlur = 0;
  g.fillStyle = '#4a3324'; g.beginPath(); g.roundRect(-7, -6, 14, 40, 5); g.fill();
  const gr = g.createLinearGradient(-10, 0, 10, 0); gr.addColorStop(0, '#9aa3b2'); gr.addColorStop(0.5, '#eef2f8'); gr.addColorStop(1, '#b8c0cc');
  g.fillStyle = gr; g.beginPath(); g.moveTo(-9, -6); g.lineTo(9, -6); g.lineTo(7, -70); g.quadraticCurveTo(0, -96, -9, -104); g.closePath(); g.fill();
  g.strokeStyle = 'rgba(255,255,255,0.55)'; g.lineWidth = 1.5; g.beginPath(); g.moveTo(5, -10); g.lineTo(4, -70); g.stroke();
  g.restore(); }

// ---------- faces (ink on the cream disc); look shifts the features toward a side ----------
function face(g, hc, r, kind, look, rot) {
  g.save(); g.translate(hc[0], hc[1]); g.rotate(rot); g.translate(look * r * 0.32, r * 0.04); g.scale(r / 100, r / 100);
  g.strokeStyle = g.fillStyle = C.ink; g.lineCap = 'round'; g.lineJoin = 'round'; g.lineWidth = 9;
  const dot = (x, y, rx = 8, ry = 11) => { g.beginPath(); g.ellipse(x, y, rx, ry, 0, 0, 7); g.fill(); };
  const line = (...p) => { g.beginPath(); g.moveTo(p[0], p[1]); for (let i = 2; i < p.length; i += 2) g.lineTo(p[i], p[i + 1]); g.stroke(); };
  const arc = (x, y, rr, a0, a1) => { g.beginPath(); g.arc(x, y, rr, a0, a1); g.stroke(); };
  const P = Math.PI;
  ({
    smile: () => { dot(-30, -14); dot(30, -14); arc(0, 2, 34, 0.2 * P, 0.8 * P); },
    grin: () => { dot(-30, -18); dot(30, -18); g.lineWidth = 8; arc(0, -6, 44, 0.14 * P, 0.86 * P); },
    neutral: () => { dot(-30, -12); dot(30, -12); line(-18, 36, 18, 36); },
    angry: () => { g.lineWidth = 10; line(-52, -46, -14, -28); line(52, -46, 14, -28); dot(-28, -10, 8, 9); dot(28, -10, 8, 9); g.lineWidth = 9; arc(0, 66, 30, 1.22 * P, 1.78 * P); },
    worried: () => { g.lineWidth = 7; line(-50, -40, -16, -52); line(50, -40, 16, -52); dot(-28, -14, 9, 12); dot(28, -14, 9, 12); g.beginPath(); g.ellipse(0, 40, 12, 15, 0, 0, 7); g.fill(); },
    scared: () => { g.lineWidth = 7; line(-52, -46, -16, -60); line(52, -46, 16, -60); g.lineWidth = 6; g.beginPath(); g.ellipse(-28, -14, 15, 18, 0, 0, 7); g.stroke(); g.beginPath(); g.ellipse(28, -14, 15, 18, 0, 0, 7); g.stroke(); dot(-28, -10, 6, 7); dot(28, -10, 6, 7);
      g.beginPath(); g.moveTo(-22, 54); g.quadraticCurveTo(0, 20, 22, 54); g.closePath(); g.fill(); },
    closed: () => { g.lineWidth = 7; arc(-28, -26, 20, 0.2 * P, 0.8 * P); arc(28, -26, 20, 0.2 * P, 0.8 * P); line(-44, 0, -14, 0); line(14, 0, 44, 0); g.lineWidth = 8; arc(0, 66, 22, 1.25 * P, 1.75 * P); },
    determined: () => { g.lineWidth = 12; line(-56, -34, -12, -24); line(56, -34, 12, -24); g.beginPath(); g.ellipse(-28, -6, 9, 8, 0, 0, 7); g.fill(); g.beginPath(); g.ellipse(28, -6, 9, 8, 0, 0, 7); g.fill(); g.lineWidth = 8; arc(0, 68, 22, 1.25 * P, 1.75 * P); },
    sad: () => { g.lineWidth = 7; line(-50, -36, -16, -48); line(50, -36, 16, -48); dot(-28, -12, 8, 10); dot(28, -12, 8, 10); g.lineWidth = 8; arc(0, 70, 28, 1.22 * P, 1.78 * P); },
    dazed: () => { g.lineWidth = 7; line(-40, -26, -16, -2); line(-16, -26, -40, -2); line(16, -26, 40, -2); line(40, -26, 16, -2); g.beginPath(); g.moveTo(-24, 40); g.quadraticCurveTo(-12, 30, 0, 40); g.quadraticCurveTo(12, 50, 24, 40); g.stroke(); },
  })[kind]();
  g.restore();
}

// ---------- the star and the light ----------
function starPath(g, x, y, R) { g.beginPath(); for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, r = i % 2 ? R * 0.42 : R; const px = x + Math.cos(a) * r, py = y + Math.sin(a) * r; i ? g.lineTo(px, py) : g.moveTo(px, py); } g.closePath(); }
function glow(g, x, y, r, a, col = C.gold) { if (a <= 0) return; g.save(); g.globalCompositeOperation = 'lighter'; const gr = g.createRadialGradient(x, y, 0, x, y, r);
  gr.addColorStop(0, rgba(C.goldHot, 0.9 * a)); gr.addColorStop(0.25, rgba(col, 0.45 * a)); gr.addColorStop(1, rgba(col, 0)); g.fillStyle = gr; g.beginPath(); g.arc(x, y, r, 0, 7); g.fill(); g.restore(); }
function drawStar(g, p, size, a, rot = 0) { if (a <= 0.01) return; const x = SX(p[0]), y = SY(p[1]), R = size * CAM.z;
  glow(g, x, y, R * 4.2, 0.75 * a);
  g.save(); g.globalAlpha = a; g.translate(x, y); g.rotate(rot); g.translate(-x, -y);
  starPath(g, x, y, R); const gr = g.createRadialGradient(x, y - R * 0.2, 0, x, y, R); gr.addColorStop(0, '#fff6dc'); gr.addColorStop(0.6, '#ffd57e'); gr.addColorStop(1, '#f2a93c');
  g.fillStyle = gr; g.shadowColor = 'rgba(255,200,110,0.9)'; g.shadowBlur = 18 * (W / DW); g.fill();
  g.lineWidth = 2.5 * CAM.z; g.strokeStyle = 'rgba(255,248,225,0.9)'; g.stroke(); g.restore(); }

// ---------- who does what ----------
const HOME = { L2: [-275, -40], L1: [-158, -20], R1: [158, -20], R2: [275, -40] };
const FRIENDS = ['L2', 'R2', 'L1', 'R1'];   // back to front
function heroAt(t, sh) {
  const b = { x: 0, y: 0, s: 1, hr: 50, hair: true, face: 'smile', look: 0, lean: 0, hunch: 0, arms: {}, legs: [0.12, -0.12] };
  const breath = 3 * Math.sin(t * 2.4);
  const star = { p: [0, -650 + breath], size: 44, a: 1, rot: 0.05 * Math.sin(t * 1.7) }; let hold = 'both', chest = 0;
  if (sh.name === 'A') { const tr = ss(TL.A.turn0, TL.A.turn1, t); b.look = -0.9 * tr; b.lean = -12 * tr;
    if (tr > 0) { hold = 'offer'; star.p = L2(star.p, [-205, -700 + breath], tr); } }
  if (sh.name === 'C') { const C_ = TL.C, pull = ss(C_.pull0, TL.D_t0, t); b.look = lerp(-0.9, 0, pull); b.lean = lerp(-14, 0, pull); hold = pull < 0.8 ? 'offer' : 'both';
    star.p = L2([-210, -700 + breath], [0, -650 + breath], pull); b.face = t < C_.worried ? 'smile' : 'worried'; star.size = 44 * (1 - 0.25 * ss(C_.worried, C_.worried + 0.4, t)); }
  if (sh.name === 'D') { b.face = 'scared'; hold = 'hug'; b.hunch = 0.35; b.x = 2 * Math.sin(t * 38); star.size = 36; star.p = [0, -640]; }
  if (sh.name === 'E') { const E = TL.E; hold = 'hug'; star.size = 36; star.p = [0, -640];
    b.face = t < E.close ? 'scared' : (t < E.open ? 'closed' : 'determined'); b.hunch = t < E.close ? 0.3 : lerp(0.3, 0, ss(E.close, E.close + 0.6, t));
    const ab = ss(E.absorb0, E.absorb1, t); star.size = 36 * (1 - 0.75 * ab); star.a = 1 - ss(E.absorb1 - 0.4, E.absorb1, t); chest = ss(E.absorb0 + 0.4, E.absorb1, t);
    const lw = ss(E.lower0, E.lower1, t); if (lw > 0) hold = { lower: lw }; }
  if (sh.name === 'F') { const F = TL.F; b.face = 'determined'; hold = 'fists'; star.a = 0; chest = 1; b.s = 1.3;
    const st = ss(F.step0, F.step1, t); b.y = 30 * st; b.legs = [0.12 + 0.25 * bump(t, F.step0, F.step1 - F.step0), -0.12]; }
  const sp = star.p;
  if (hold === 'both') { b.arms.L = { h: [sp[0] - 46, sp[1] + 30], bend: -1 }; b.arms.R = { h: [sp[0] + 46, sp[1] + 30], bend: 1 }; }
  else if (hold === 'offer') { b.arms.L = { h: [sp[0] + 10, sp[1] + 38], bend: 1 }; b.arms.R = { h: [60, -470], bend: 1 }; }
  else if (hold === 'hug' || (hold && hold.lower !== undefined)) { const lw = hold.lower || 0;
    // the hug: forearms crossed flat over the chest, elbows out at the sides; lowering slides into arms at the sides
    const hy = b.hunch * 30;
    const hug = { L: [[-98, -628 + hy], [58, -676 + hy]], R: [[98, -624 + hy], [-58, -668 + hy]] }, down = { L: [[-60, -600], [-72, -460]], R: [[60, -600], [72, -460]] };
    b.arms.L = { el: L2(hug.L[0], down.L[0], lw), h: L2(hug.L[1], down.L[1], lw) }; b.arms.R = { el: L2(hug.R[0], down.R[0], lw), h: L2(hug.R[1], down.R[1], lw) }; }
  else { b.arms.L = { h: [-78 * b.s, -470 * b.s + b.y], bend: -1 }; b.arms.R = { h: [78 * b.s, -470 * b.s + b.y], bend: 1 }; }
  return { b, star, chest };
}
function friendAt(id, t, sh) {
  const [hx, hy] = HOME[id], side = Math.sign(hx), inner = side < 0 ? 'R' : 'L', outer = side < 0 ? 'L' : 'R';
  const b = { x: hx, y: hy, s: 1.24, hr: 46, face: 'grin', look: -side * 0.35, lean: -side * 26, hunch: 0.1, arms: {}, legs: [0.1, -0.1], dim: Math.abs(hx) > 160 };
  const idle = 5 * Math.sin(t * 2.2 + hx);
  const knifeBack = { h: [hx + side * 52, hy - 520 + idle * 0.3], bend: side, knife: { ang: side * 0.35, behind: true, a: 0 } };
  b.arms[outer] = knifeBack; b.arms[inner] = { h: [hx - side * 50, hy - 560], bend: -side };
  const n = sh.name, B = TL.B;
  if (n === 'A') { if (id === 'R1') knifeBack.knife.a = ss(TL.A.knifeIn, TL.A.knifeIn + 0.15, t);
    if (id === 'L1') { const k = ss(TL.A.turn1, TL.A.turn1 + 0.4, t); b.lean += 30 * k; b.hunch += 0.25 * k; b.look = 0.6; } }
  if (n === 'B') { if (id === 'R1') knifeBack.knife.a = 1;
    if (id === 'R1' && t > B.r1Angry) b.face = t < B.r1Angry + 0.1 ? 'neutral' : 'angry';
    if (id === 'L1' && t > B.l1Angry) b.face = 'angry';
    if ((id === 'L2' || id === 'R2') && t > B.l1Angry + 0.2) b.face = 'angry';
    if (id === 'R1') { const r = ss(B.reach0, B.reach1, t); b.arms[inner] = { h: L2([hx - 50, hy - 560], [40, -665 + 6 * Math.sin(t * 9)], r), bend: 1, claw: r > 0.3 }; } }
  if (n === 'C' || n === 'D') { b.face = 'angry'; if (id === 'R1' || id === 'L1') knifeBack.knife.a = 1;
    if (id === 'R1') b.arms[inner] = { h: [n === 'C' ? -60 : 38, n === 'C' ? -690 : -630 + 6 * Math.sin(t * 9)], bend: 1, claw: true };
    if (n === 'C' && id === 'L1') { b.lean = 60; b.hunch = 0.55; b.look = 0.4; }
    if (n === 'D') { b.x = hx * 1.15; b.s = 1.36; b.hunch = 0.45; b.lean = -side * 40; } }
  if (n === 'F') { const F = TL.F; b.s = 1.0; b.dim = false; b.x = { L2: -340, L1: -180, R1: 180, R2: 340 }[id]; b.y = { L2: -30, L1: -10, R1: -10, R2: -30 }[id];
    const back = ss(F.back0, F.back1, t); b.x += side * 25 * back; b.hunch = 0.35 + 0.25 * back; b.lean = side * 20 * back; b.look = -side * 0.4;
    b.face = back > 0.3 ? 'worried' : 'sad';
    b.arms[outer] = { h: [b.x + side * 70, b.y - 450], bend: side, knife: { ang: side * 0.25, behind: false, a: 1 } }; b.arms[inner] = { h: [b.x - side * 62, b.y - 460], bend: -side };
    if (t >= F.burst) blast(b, id, t, side); }
  return b;
}
// the burst: thrown outward, a cartwheel in the air, then flat on the floor in the foreground, dazed
const LAND = { L2: [-430, 150], L1: [-250, 250], R1: [250, 250], R2: [430, 150] };
function blast(b, id, t, side) {
  const F = TL.F, u = t - F.burst, T_ = F.land - F.burst + 0.05 * (Math.abs(LAND[id][0]) > 400), k = clamp(u / T_);
  const p0 = [b.x, b.y - 470], p1 = [LAND[id][0], LAND[id][1] - 60];
  b.moveHip = [lerp(p0[0], p1[0], eout(k) * 0.7 + k * 0.3), lerp(p0[1], p1[1], k) - 900 * k * (1 - k)];
  b.rot = side * Math.PI * 2.5 * k;                                         // a cartwheel outward, ending flat, head outward
  b.s = lerp(1.0, 0.72, eout(k));                                             // and they land further off: smaller
  const fl = k < 1 ? Math.sin(u * 22) : 0;
  b.face = k < 1 ? 'scared' : 'dazed'; b.hunch = 0; b.lean = 0; b.look = 0;
  const hp = [b.x, b.y - 470];   // targets in the pre-rotation frame: arms thrown up while flying, along the sides when flat
  b.arms.L = k < 1 ? { h: [hp[0] - 150, hp[1] - 440 - 40 * fl], bend: -1 } : { h: [hp[0] - 70, hp[1] + 20], bend: -1 };
  b.arms.R = k < 1 ? { h: [hp[0] + 150, hp[1] - 440 + 40 * fl], bend: 1 } : { h: [hp[0] + 70, hp[1] + 20], bend: 1 };
  b.legs = k < 1 ? [0.35 + 0.15 * fl, -0.35 + 0.15 * fl] : [0.12, -0.12];
  b.flying = { k, u };
}
function thrownKnife(g, id, t, side) { // the knives fly up spinning and stick in the floor in front of them
  const F = TL.F, u = t - F.burst, T_ = 0.8, k = clamp(u / T_); const x0 = { L2: -410, L1: -250, R1: 250, R2: 410 }[id], land = [x0 * 1.3 + side * 40, 120 + 40 * hash(x0)];
  const p = [lerp(x0, land[0], k), lerp(-450, land[1], k) - 1100 * k * (1 - k)];
  knife(g, p, k < 1 ? u * 16 * side : Math.PI + side * 0.35, 1.0, 1);
}

// ---------- overlays: speed lines, lyrics ----------
function speedLines(g, t) {
  const a = ss(TL.D.lines0, TL.D.lines0 + 0.15, t); const fr = Math.floor(t * 12); g.save(); g.lineCap = 'round';
  for (let i = 0; i < 64; i++) { const ang = hash(i + fr * 101) * Math.PI * 2, r0 = 300 + 140 * hash(i * 3 + fr), w = 1 + 3 * hash(i * 7 + fr);
    g.strokeStyle = `rgba(237,230,214,${0.22 * a * (0.4 + 0.6 * hash(i * 5 + fr))})`; g.lineWidth = w; g.beginPath();
    g.moveTo(360 + Math.cos(ang) * r0, 560 + Math.sin(ang) * r0); g.lineTo(360 + Math.cos(ang) * 1200, 560 + Math.sin(ang) * 1200); g.stroke(); }
  g.restore(); }
function lyrics(g, t) {
  for (const [t0, t1, lines] of TL.lyrics) { if (t < t0 || t >= t1) continue;
    g.save(); g.textAlign = 'center'; g.textBaseline = 'alphabetic'; g.font = '600 31px "Inter"'; g.letterSpacing = '0.2px';
    g.shadowColor = 'rgba(0,0,0,0.75)'; g.shadowBlur = 10; g.fillStyle = 'rgba(250,246,238,0.97)';
    lines.forEach((l, i) => g.fillText(l, 360, 1002 + i * 40)); g.restore(); } }

// ---------- one frame ----------
function frame(g, t) {
  T = t; const sh = shotAt(t); CAM = camFor(sh, t);
  g.setTransform(W / DW, 0, 0, H / DH, 0, 0);
  background(g, t);
  if (sh.name === 'D') speedLines(g, t);
  floor(g);
  const h = heroAt(t, sh);
  const vis = { A: FRIENDS, B: FRIENDS, C: ['R2', 'L1', 'R1'], D: FRIENDS, E: [], F: FRIENDS }[sh.name];
  const fb = vis.map(id => [id, friendAt(id, t, sh)]);
  shadow(g, 0, 70 * h.b.s); for (const [, b] of fb) if (!b.flying) shadow(g, b.x, 70 * b.s, 0.35);
  const draw = b => drawBody(g, b, joints(b));
  for (const [, b] of fb) if (!b.flying) draw(b);
  const Jh = joints(h.b); drawBody(g, h.b, Jh);
  const chestP = L2(Jh.sh, Jh.hip, 0.28), F = TL.F;
  const charge = sh.name === 'F' ? ss(F.charge0, F.burst, t) : 0, post = sh.name === 'F' && t >= F.burst ? Math.exp(-(t - F.burst) * 2.5) : 0;
  if (h.chest > 0) { glow(g, SX(chestP[0]), SY(chestP[1]), (90 + 160 * charge + 120 * post) * h.b.s * CAM.z, h.chest * (0.75 + 0.25 * charge));
    glow(g, SX(chestP[0]), SY(chestP[1]), 26 * h.b.s * CAM.z, h.chest); }
  drawStar(g, h.star.p, h.star.size, h.star.a, h.star.rot);
  if (sh.name === 'D' || sh.name === 'E') { // the hugging arms go over the star
    g.save(); g.lineCap = 'round'; g.lineJoin = 'round'; g.strokeStyle = C.fig; g.lineWidth = 12 * CAM.z * 0.92; g.shadowColor = 'rgba(255,214,160,0.42)'; g.shadowBlur = 9 * CAM.z * (W / DW);
    for (const s of ['L', 'R']) { g.beginPath(); const p = [Jh.sh, Jh['so' + s], Jh['el' + s], Jh['hd' + s]].map(q => [SX(q[0]), SY(q[1])]); g.moveTo(...p[0]); for (let i = 1; i < p.length; i++) g.lineTo(...p[i]); g.stroke(); }
    g.restore(); }
  if (sh.name === 'F') { for (const [, b] of fb) if (b.flying) draw(b); if (t >= F.burst) for (const [id] of fb) thrownKnife(g, id, t, Math.sign(HOME[id][0])); }
  if (sh.name === 'F') { const fl = bump(t, F.burst - 0.06, 0.32); if (fl > 0) { glow(g, SX(chestP[0]), SY(chestP[1]), 200 + 900 * ss(F.burst - 0.06, F.burst + 0.2, t), fl);
      g.save(); g.fillStyle = `rgba(255,246,226,${0.85 * fl})`; g.fillRect(0, 0, DW, DH); g.restore(); }
    const rk = t >= F.burst ? clamp((t - F.burst) / 0.6) : 0; if (rk > 0 && rk < 1) { g.save(); g.globalCompositeOperation = 'lighter'; g.strokeStyle = rgba(C.goldHot, 0.7 * (1 - rk)); g.lineWidth = 10 * (1 - rk) + 2;
      g.beginPath(); g.ellipse(SX(0), SY(0), 40 + 520 * eout(rk), 10 + 70 * eout(rk), 0, 0, 7); g.stroke(); g.restore(); } }
  lyrics(g, t);
  g.save(); g.font = '600 11px "JetBrains Mono"'; g.letterSpacing = '5px'; g.textAlign = 'center'; g.fillStyle = 'rgba(242,238,230,0.28)'; g.fillText('SLOW LIGHT', 360, 1270); g.restore();
}

window.renderAt = (t, sub = 1) => {
  sub = Math.max(1, sub | 0); const sh = shotAt(t);
  if (sub === 1) frame(out, t);
  else { out.setTransform(1, 0, 0, 1, 0, 0); out.fillStyle = '#000'; out.fillRect(0, 0, W, H);
    for (let i = 0; i < sub; i++) { const ti = Math.max(sh.t0, t + (i / sub - 0.5) * (1 / 30) * 0.5);
      A.setTransform(1, 0, 0, 1, 0, 0); frame(A, ti); out.setTransform(1, 0, 0, 1, 0, 0); out.globalCompositeOperation = 'lighter'; out.globalAlpha = 1 / sub; out.drawImage(acc, 0, 0); }
    out.globalCompositeOperation = 'source-over'; out.globalAlpha = 1; }
  return cv.toDataURL('image/jpeg', 0.95);
};
window.metaAt = t => ({ shot: shotAt(t).name });
(async () => {
  TL = await (await fetch('./timeline.json')).json(); DUR = TL.duration; window.DUR = DUR; window.events = TL;
  SHOTS = TL.shots.map(([t0, name], i) => ({ t0, t1: i + 1 < TL.shots.length ? TL.shots[i + 1][0] : DUR, name })); TL.D_t0 = TL.shots[3][0];
  await document.fonts.load('600 31px "Inter"'); await document.fonts.load('600 11px "JetBrains Mono"');
  window.ready = true;
})();
