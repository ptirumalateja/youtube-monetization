// Hall of Mirrors - Slow Light parable reel, paper-ink look (cream paper, black ink line art, one red accent).
// Canvas 2D, design space 720x1280 scaled to the render size. window.renderAt(t, sub) -> JPEG data URL.
'use strict';
const DW = 720, DH = 1280;
const qs = new URLSearchParams(location.search);
const W = +(qs.get('w') || 1080), H = +(qs.get('h') || 1920);
const LOOK = qs.get('look') || 'red';
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
const INK = '#1e1916', PAPER = '#ede6d6', FILL = '#fbf7ee', SHADE = '#ddd3c2', RED = '#c8282a', REDL = '#e05a4c';
// hand-drawn boil: tiny offsets that change 8x a second
const BOIL = () => Math.floor(T * 8);
function jit(x, y, a = 0.9) { const b = BOIL(); return [x + (hash(x * 0.13 + y * 0.71 + b * 3.3) - 0.5) * a * 2, y + (hash(x * 0.57 + y * 0.29 + b * 1.7) - 0.5) * a * 2]; }

// ---------- layout ----------
const FLOOR = 806;
const MIR = [[40, 236], [262, 458], [484, 680]];
const MTOP = 366, MBOT = FLOOR;

// ---------- dog rig (local px, facing +x, ground y = 0) ----------
const DK = ['chest', 'hip', 'head', 'f1e', 'f1p', 'f2e', 'f2p', 'r1k', 'r1h', 'r1p', 'r2k', 'r2h', 'r2p', 'tail'];
const STAND = { chest: [34, -60], hip: [-38, -62], head: [66, -96], f1e: [38, -30], f1p: [40, 0], f2e: [26, -30], f2p: [24, 0], r1k: [-28, -34], r1h: [-42, -14], r1p: [-36, 0], r2k: [-40, -34], r2h: [-54, -14], r2p: [-48, 0], tail: [-74, -92] };
const SNARL = { chest: [32, -52], hip: [-40, -58], head: [70, -70], f1e: [46, -26], f1p: [56, 0], f2e: [34, -26], f2p: [40, 0], r1k: [-24, -32], r1h: [-44, -12], r1p: [-34, 0], r2k: [-36, -32], r2h: [-56, -12], r2p: [-46, 0], tail: [-78, -78] };
const LUNGE = { chest: [46, -70], hip: [-26, -58], head: [88, -96], f1e: [76, -70], f1p: [98, -48], f2e: [66, -62], f2p: [88, -40], r1k: [-14, -30], r1h: [-38, -12], r1p: [-24, 0], r2k: [-26, -30], r2h: [-50, -12], r2p: [-38, 0], tail: [-70, -90] };
const DOWN = { chest: [36, -22], hip: [-38, -22], head: [76, -18], f1e: [58, -10], f1p: [80, -5], f2e: [52, -8], f2p: [72, -3], r1k: [-16, -12], r1h: [-42, -6], r1p: [-30, -3], r2k: [-24, -10], r2h: [-48, -5], r2p: [-36, -2], tail: [-86, -10] };
const HAPPY = { chest: [34, -60], hip: [-38, -62], head: [64, -102], f1e: [38, -30], f1p: [40, 0], f2e: [26, -30], f2p: [24, 0], r1k: [-28, -34], r1h: [-42, -14], r1p: [-36, 0], r2k: [-40, -34], r2h: [-54, -14], r2p: [-48, 0], tail: [-70, -108] };
function dmix(a, b, k) { const o = {}; for (const n of DK) o[n] = [lerp(a[n][0], b[n][0], k), lerp(a[n][1], b[n][1], k)]; return o; }

// primitives drawn twice: ink outline pass (wider) then paper fill pass -> one clean cartoon silhouette
function dogParts(P, o) {
  const sn = o.snarl || 0, wag = o.wag ? Math.sin(T * 20 + o.x * 0.01) * 20 * o.wag : 0;
  const near = [], far = [];
  far.push({ t: 'l', p: [P.chest, P.f2e, P.f2p], w: 11 }, { t: 'l', p: [P.hip, P.r2k, P.r2h, P.r2p], w: 11 });
  const tt = [P.tail[0] + wag * 0.4, P.tail[1] + wag];
  near.push({ t: 'q', p: [P.hip, [P.hip[0] - 26, P.hip[1] - 8], tt], w: 8 });
  near.push({ t: 'l', p: [P.hip, P.r1k, P.r1h, P.r1p], w: 12 }, { t: 'l', p: [P.chest, P.f1e, P.f1p], w: 12 });
  const mid = [(P.chest[0] + P.hip[0]) / 2, (P.chest[1] + P.hip[1]) / 2 - 3];
  near.push({ t: 'q', p: [P.chest, mid, P.hip], w: 40 });
  near.push({ t: 'e', c: [P.chest[0] + 4, P.chest[1] + 4], rx: 25, ry: 23 }, { t: 'e', c: [P.hip[0] - 2, P.hip[1] + 3], rx: 21, ry: 21 });
  near.push({ t: 'l', p: [[P.chest[0] + 6, P.chest[1] - 6], [P.head[0] - 10, P.head[1] + 8]], w: 22 });
  near.push({ t: 'e', c: P.head, rx: 23, ry: 20 });
  // snout + lower jaw (opens with the snarl)
  near.push({ t: 'r', c: [P.head[0] + 8, P.head[1] - 5], w: 32, h: 17, r: 8, rot: 0.08 });
  const ja = 0.12 + 0.55 * sn; near.push({ t: 'r', c: [P.head[0] + 8, P.head[1] + 6], w: 24, h: 8, r: 4, rot: ja });
  // ear: up and forward when snarling, floppy when happy
  const ea = o.happy ? -1.9 + 0.15 * Math.sin(T * 9) : lerp(-0.25, 0.35, sn);
  near.push({ t: 'ear', c: [P.head[0] - 8, P.head[1] - 12], a: ea });
  return { near, far, ja };
}
function prim(g, q, o, w, col) {
  const s = o.s, d = o.dir, X = p => o.x + p[0] * d * s, Y = p => o.y + p[1] * s;
  g.strokeStyle = col; g.fillStyle = col; g.lineCap = 'round'; g.lineJoin = 'round';
  if (q.t === 'l' || q.t === 'q') {
    g.lineWidth = (q.w + w) * s; g.beginPath(); const p0 = jit(X(q.p[0]), Y(q.p[0]), 0.6); g.moveTo(p0[0], p0[1]);
    if (q.t === 'q') { const c = jit(X(q.p[1]), Y(q.p[1]), 0.6), e = jit(X(q.p[2]), Y(q.p[2]), 0.6); g.quadraticCurveTo(c[0], c[1], e[0], e[1]); }
    else for (let i = 1; i < q.p.length; i++) { const p = jit(X(q.p[i]), Y(q.p[i]), 0.6); g.lineTo(p[0], p[1]); }
    g.stroke();
  } else if (q.t === 'e') { const c = jit(X(q.c), Y(q.c), 0.5); g.beginPath(); g.ellipse(c[0], c[1], (q.rx + w / 2) * s, (q.ry + w / 2) * s, 0, 0, 7); g.fill(); }
  else if (q.t === 'r') { g.save(); const c = jit(X(q.c), Y(q.c), 0.5); g.translate(c[0], c[1]); g.scale(d, 1); g.rotate(q.rot || 0); g.beginPath(); g.roundRect(-4 * s - w / 2 * s, -q.h / 2 * s - w / 2 * s, (q.w + w) * s, (q.h + w) * s, (q.r + w / 2) * s); g.fill(); g.restore(); }
  else if (q.t === 'ear') { g.save(); const c = jit(X(q.c), Y(q.c), 0.5); g.translate(c[0], c[1]); g.scale(d, 1); g.rotate(q.a); g.beginPath();
    const e = w / 2; g.moveTo(-9 * s - e * s, 4 * s + e * s); g.quadraticCurveTo(-6 * s, -14 * s, 2 * s, -26 * s - e * 1.6 * s); g.quadraticCurveTo(8 * s + e * s, -10 * s, 10 * s + e * s, 4 * s + e * s); g.closePath(); g.fill(); g.restore(); }
}
function drawDog(g, P, o) {
  const s = o.s, d = o.dir, X = p => o.x + p[0] * d * s, Y = p => o.y + p[1] * s;
  const { near, far, ja } = dogParts(P, o); const OW = 6.5, sn = o.snarl || 0;
  g.save(); g.globalAlpha = o.alpha ?? 1;
  for (const q of far) prim(g, q, o, OW, INK); for (const q of far) prim(g, q, o, 0, o.shade || SHADE);
  for (const q of near) prim(g, q, o, OW, INK); for (const q of near) prim(g, q, o, 0, o.fill || FILL);
  // details in ink
  const hx = X(P.head), hy = Y(P.head);
  g.save(); g.translate(hx, hy); g.scale(d, 1); g.strokeStyle = INK; g.fillStyle = INK; g.lineCap = 'round'; g.lineJoin = 'round';
  // nose
  g.beginPath(); g.ellipse(34 * s, -8 * s, 5 * s, 4 * s, 0, 0, 7); g.fill();
  // mouth: gums + teeth when snarling
  if (sn > 0.08) {
    g.save(); g.translate(4 * s, 6 * s); const L = 24 * s;
    g.fillStyle = RED; g.beginPath(); g.moveTo(0, -1 * s); g.lineTo(28 * s, -1 * s); g.lineTo(Math.cos(ja) * L, Math.sin(ja) * L + 2 * s); g.closePath(); g.fill();
    g.fillStyle = '#fff'; g.strokeStyle = INK; g.lineWidth = 1.4 * s;
    for (let i = 0; i < 4; i++) { const x0 = (6 + i * 5.5) * s; g.beginPath(); g.moveTo(x0, -1 * s); g.lineTo(x0 + 2.7 * s, (5 + (i === 0 ? 3 : 0)) * s * sn); g.lineTo(x0 + 5.4 * s, -1 * s); g.closePath(); g.fill(); g.stroke(); }
    g.restore();
  } else { g.lineWidth = 2.4 * s; g.beginPath(); g.moveTo(14 * s, 4 * s); g.quadraticCurveTo(22 * s, o.happy ? 10 * s : 6 * s, 30 * s, 2 * s); g.stroke(); if (o.happy) { g.fillStyle = REDL; g.beginPath(); g.ellipse(22 * s, 10 * s, 4 * s, 5 * s, 0.3, 0, 7); g.fill(); g.strokeStyle = INK; g.lineWidth = 1.6 * s; g.stroke(); } }
  // eye + brow
  if (sn > 0.3) { g.beginPath(); g.moveTo(-2 * s, -9 * s); g.lineTo(9 * s, -5 * s); g.lineTo(1 * s, -3 * s); g.closePath(); g.fill(); g.lineWidth = 3.2 * s; g.beginPath(); g.moveTo(-4 * s, -15 * s); g.lineTo(12 * s, -8 * s); g.stroke(); }
  else if (o.happy) { g.lineWidth = 2.8 * s; g.beginPath(); g.arc(3 * s, -6 * s, 4.5 * s, Math.PI * 1.1, Math.PI * 1.9); g.stroke(); }
  else { g.beginPath(); g.arc(3 * s, -6 * s, 3.2 * s, 0, 7); g.fill(); }
  g.restore();
  // hackles: ink zigzag along the back when snarling
  if (sn > 0.1 && !o.far) {
    g.save(); g.strokeStyle = INK; g.lineWidth = 2.6 * s; g.lineJoin = 'miter'; g.beginPath();
    for (let i = 0; i <= 10; i++) { const u = 0.08 + i * 0.075, bx = lerp(P.chest[0], P.hip[0], u), by = lerp(P.chest[1], P.hip[1], u) - 22 - 2 * Math.sin(u * Math.PI);
      const p = jit(X([bx, 0]), Y([0, by - (i % 2 ? 9 * sn : 0)]), 0.5); i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1]); }
    g.stroke(); g.restore();
  }
  // red anger marks + noise lines around a snarling head
  if (sn > 0.4 && !o.far) {
    g.save(); g.strokeStyle = RED; g.lineWidth = 3 * s; g.lineCap = 'round'; const ax = hx - 10 * s * d, ay = hy - 40 * s;
    for (let i = 0; i < 4; i++) { const a = i * Math.PI / 2 + 0.6; g.beginPath(); g.moveTo(ax + Math.cos(a) * 4 * s, ay + Math.sin(a) * 4 * s); g.quadraticCurveTo(ax + Math.cos(a + 0.5) * 9 * s, ay + Math.sin(a + 0.5) * 9 * s, ax + Math.cos(a) * 12 * s, ay + Math.sin(a) * 12 * s); g.stroke(); }
    g.strokeStyle = INK; g.lineWidth = 2.4 * s; const mx = hx + 46 * s * d, my = hy + 2 * s;
    for (let i = -1; i <= 1; i++) { const p0 = jit(mx, my + i * 12 * s), p1 = jit(mx + 14 * s * d, my + i * 16 * s); g.beginPath(); g.moveTo(p0[0], p0[1]); g.lineTo(p1[0], p1[1]); g.stroke(); }
    g.restore();
  }
  g.restore();
}

// ---------- paper hall ----------
function paper(g, t) {
  g.fillStyle = PAPER; g.fillRect(-200, -200, DW + 400, DH + 400);
  if (!window._paper) { const c = document.createElement('canvas'); c.width = c.height = 512; const x = c.getContext('2d'); const im = x.createImageData(512, 512);
    for (let p = 0; p < im.data.length; p += 4) { const v = 128 + (Math.random() - 0.5) * 60; im.data[p] = im.data[p + 1] = im.data[p + 2] = v; im.data[p + 3] = 255; } x.putImageData(im, 0, 0);
    x.globalAlpha = 0.08; for (let i = 0; i < 400; i++) { x.strokeStyle = Math.random() < 0.5 ? '#000' : '#fff'; x.lineWidth = 0.6; x.beginPath(); const a = Math.random() * 512, b = Math.random() * 512; x.moveTo(a, b); x.lineTo(a + (Math.random() - 0.5) * 30, b + (Math.random() - 0.5) * 30); x.stroke(); } window._paper = c; }
  g.save(); g.globalAlpha = 0.1; g.globalCompositeOperation = 'multiply'; g.fillStyle = g.createPattern(window._paper, 'repeat'); g.fillRect(-200, -200, DW + 400, DH + 400); g.restore();
}
function inkLine(g, pts, w, col = INK) { g.strokeStyle = col; g.lineWidth = w; g.lineCap = 'round'; g.lineJoin = 'round'; g.beginPath(); pts.forEach((p, i) => { const q = jit(p[0], p[1], 0.7); i ? g.lineTo(q[0], q[1]) : g.moveTo(q[0], q[1]); }); g.stroke(); }
function archPts(x0, x1, y0, y1, n = 26) { const r = (x1 - x0) / 2, p = [[x0, y1], [x0, y0 + r]]; for (let i = 0; i <= n; i++) { const a = Math.PI + i / n * Math.PI; p.push([x0 + r + Math.cos(a) * r, y0 + r + Math.sin(a) * r]); } p.push([x1, y1]); return p; }
function archPath(g, x0, x1, y0, y1) { const r = (x1 - x0) / 2; g.beginPath(); g.moveTo(x0, y1); g.lineTo(x0, y0 + r); g.arc(x0 + r, y0 + r, r, Math.PI, 0); g.lineTo(x1, y1); g.closePath(); }
function hall(g, t, mood) {
  paper(g, t);
  // back wall: a few hand-drawn stone courses and pillars, light so the paper stays bright
  for (let i = 0; i < 6; i++) inkLine(g, [[-20, 150 + i * 46], [740, 150 + i * 46 + (hash(i) - 0.5) * 3]], 1.1, 'rgba(30,25,22,0.18)');
  for (let i = 0; i < 18; i++) { const y = 150 + (i % 6) * 46, x = ((i * 97) % 700) + 10; inkLine(g, [[x, y], [x, y + 46]], 1, 'rgba(30,25,22,0.14)'); }
  // hanging lamp line
  inkLine(g, [[360, -10], [360, 70]], 2); inkLine(g, [[322, 70], [398, 70], [384, 98], [336, 98], [322, 70]], 3);
  // floor: one confident ink line + tile perspective strokes
  inkLine(g, [[-20, FLOOR + 1], [740, FLOOR - 1]], 3.5);
  for (let i = -6; i <= 6; i++) inkLine(g, [[360 + i * 70, FLOOR + 8], [360 + i * 70 * 2.6, DH + 30]], 1.2, 'rgba(30,25,22,0.22)');
  for (let i = 1, d = 34; i < 7; i++, d *= 1.45) inkLine(g, [[-20, FLOOR + d], [740, FLOOR + d]], 1.1, 'rgba(30,25,22,0.18)');
}
function mirror(g, t, m, dogFn, mood, crack) {
  const [x0, x1] = MIR[m], y0 = MTOP, y1 = MBOT, cx = (x0 + x1) / 2;
  // glass: pale grey-blue wash with a soft tint (red when hostile, warm when friendly)
  g.save(); archPath(g, x0, x1, y0, y1); g.clip();
  let gr = g.createLinearGradient(0, y0, 0, y1);
  gr.addColorStop(0, mood < 0.5 ? '#e6dcd8' : '#efe4cc'); gr.addColorStop(1, mood < 0.5 ? '#dacdc8' : '#e8d9b8'); g.fillStyle = gr; g.fillRect(x0, y0, x1 - x0, y1 - y0);
  const vy = y1 - 300;
  for (let k = 6; k >= 1; k--) { const sc = Math.pow(0.72, k);
    const ax0 = lerp(cx, x0, sc), ax1 = lerp(cx, x1, sc), ay0 = lerp(vy, y0, sc), ay1 = lerp(vy, y1, sc);
    inkLine(g, archPts(ax0, ax1, ay0, ay1), 1 + 1.2 * sc, `rgba(30,25,22,${0.25 + 0.3 * sc})`);
    inkLine(g, [[ax0, ay1], [ax1, ay1]], 1 + sc, `rgba(30,25,22,${0.2 + 0.3 * sc})`);
    if (k <= 3) dogFn(g, cx + (k % 2 ? 10 : -10) * sc, ay1, sc * 1.25, k, 1);
  }
  // sheen strokes
  g.strokeStyle = 'rgba(255,255,255,0.75)'; g.lineWidth = 5; g.lineCap = 'round'; g.beginPath(); g.moveTo(x0 + 26, y0 + 190); g.lineTo(x0 + 60, y0 + 140); g.moveTo(x0 + 26, y0 + 222); g.lineTo(x0 + 80, y0 + 150); g.stroke();
  if (crack > 0) { const px = cx + (hash(m) - 0.5) * 50, py = y0 + 260 + hash(m + 3) * 60;
    for (let i = 0; i < 8; i++) { const a = i / 8 * Math.PI * 2 + hash(i + m * 9); let x = px, y = py; const pts = [[x, y]]; for (let j = 0; j < 4; j++) { const l = 26 * crack * (0.6 + hash(i * 7 + j)); x += Math.cos(a + (hash(i + j * 3) - 0.5) * 0.7) * l; y += Math.sin(a + (hash(i * 2 + j) - 0.5) * 0.7) * l; pts.push([x, y]); } inkLine(g, pts, 1.6); } }
  g.restore();
  // frame: thick ink double line with a tan wood fill between
  g.save(); archPath(g, x0 - 7, x1 + 7, y0 - 7, y1); archPath(g, x0, x1, y0, y1); g.restore();
  g.save(); g.lineWidth = 14; g.strokeStyle = '#c9ae86'; archPath(g, x0 - 4, x1 + 4, y0 - 4, y1); g.stroke(); g.restore();
  inkLine(g, archPts(x0 - 11, x1 + 11, y0 - 11, y1), 3.4); inkLine(g, archPts(x0, x1, y0, y1), 2.6);
}

// ---------- look-test scenes ----------
const DUR = 4.0;
function heroPose(t) { const c = (t * 1.6) % 1; const k = c < 0.35 ? eout(c / 0.35) : 1 - eio((c - 0.35) / 0.65); return dmix(SNARL, LUNGE, k * 0.85); }
function scene(g, t) {
  const gold = LOOK === 'gold', mood = gold ? 1 : 0;
  hall(g, t, mood);
  const copy = (gg, x, y, sc, k, a) => gold
    ? drawDog(gg, HAPPY, { x, y, s: sc, dir: k % 2 ? -1 : 1, wag: 1, happy: 1, alpha: a, far: k > 1 })
    : drawDog(gg, heroPose(t - k * 0.04), { x, y, s: sc, dir: k % 2 ? -1 : 1, snarl: 1, alpha: a, far: k > 1 });
  for (let m = 0; m < 3; m++) mirror(g, t, m, copy, mood, gold ? 0 : (m === 2 ? 0.8 : m === 0 ? 0.5 : 0));
  // hero + soft ink shadow
  const o = gold ? { x: 340, y: FLOOR + 56, s: 1.8, dir: 1, wag: 1, happy: 1 } : { x: 330, y: FLOOR + 56, s: 1.8, dir: 1, snarl: 1 };
  g.save(); g.fillStyle = 'rgba(30,25,22,0.18)'; g.beginPath(); g.ellipse(o.x - 10, o.y + 4, 120, 10, 0, 0, 7); g.fill(); g.restore();
  drawDog(g, gold ? HAPPY : heroPose(t), o);
  if (gold) { // little red hearts float up from the reflections
    for (let i = 0; i < 6; i++) { const ph = (t * 0.5 + i / 6) % 1, x = 80 + i * 112, y = 760 - ph * 260; heart(g, x, y, 9, 1 - ph); } }
}
function heart(g, x, y, r, a) { g.save(); g.globalAlpha = a; g.fillStyle = RED; g.strokeStyle = INK; g.lineWidth = 2; g.beginPath(); g.moveTo(x, y + r); g.bezierCurveTo(x - r * 1.6, y - r * 0.2, x - r * 0.8, y - r * 1.4, x, y - r * 0.5); g.bezierCurveTo(x + r * 0.8, y - r * 1.4, x + r * 1.6, y - r * 0.2, x, y + r); g.fill(); g.stroke(); g.restore(); }

// ---------- text (handwritten small caps, key word in red; all inside design y 200-960) ----------
function fitFont(g, txt, size, family, maxW) { g.font = `${size}px "${family}"`; const w = g.measureText(txt).width; if (w > maxW) { size *= maxW / w; g.font = `${size}px "${family}"`; } return size; }
function words(g, parts, x, y, size, maxW) { // parts: [[text, color], ...] centered on one line
  const full = parts.map(p => p[0]).join(''); fitFont(g, full, size, 'Patrick Hand SC', maxW); let w = g.measureText(full).width, cx = x - w / 2;
  g.textAlign = 'left'; for (const [s, c] of parts) { g.fillStyle = c; g.fillText(s, cx, y); cx += g.measureText(s).width; }
}
function counter(g, label, val, col) {
  g.save(); const x = 240, y = 896, w = 240, h = 60;
  g.fillStyle = 'rgba(251,247,238,0.92)'; g.beginPath(); g.roundRect(x, y, w, h, 12); g.fill();
  inkLine(g, [[x, y + 6], [x, y + h - 6], [x + 6, y + h], [x + w - 6, y + h], [x + w, y + h - 6], [x + w, y + 6], [x + w - 6, y], [x + 6, y], [x, y + 6]], 3);
  g.font = '26px "Patrick Hand SC"'; g.textAlign = 'left'; g.fillStyle = INK; g.fillText(label, x + 18, y + 40);
  g.font = '38px "Permanent Marker"'; g.textAlign = 'right'; g.fillStyle = col; g.fillText(val, x + w - 16, y + 46); g.restore();
}
function frame(g, t) {
  T = t;
  const z = 1.0 + 0.04 * eout(clamp(t / 2.5)), sh = LOOK === 'gold' ? 0 : 2 * Math.exp(-((t * 1.6) % 1) * 8);
  g.setTransform(W / DW, 0, 0, H / DH, 0, 0); g.translate(360, 760); g.scale(z, z); g.translate(-360 + Math.sin(t * 61) * sh, -760 + Math.cos(t * 47) * sh);
  scene(g, t);
  g.setTransform(W / DW, 0, 0, H / DH, 0, 0);
  // soft warm paper vignette (light, never dark edges)
  const gr = g.createRadialGradient(360, 640, 380, 360, 640, 900); gr.addColorStop(0, 'rgba(120,95,60,0)'); gr.addColorStop(1, 'rgba(120,95,60,0.16)'); g.fillStyle = gr; g.fillRect(0, 0, DW, DH);
  g.textBaseline = 'alphabetic';
  if (LOOK === 'gold') { words(g, [['SAME ROOM. ', INK]], 360, 262, 66, 560); words(g, [['A THOUSAND ', INK], ['FRIENDS.', RED]], 360, 326, 58, 580); counter(g, 'FRIENDS', '1000', RED); }
  else { words(g, [['HE FOUGHT ', INK], ['1,000 DOGS.', RED]], 360, 262, 66, 580); words(g, [['ONLY ONE WAS REAL.', INK]], 360, 326, 54, 540); counter(g, 'ENEMIES', '1000', RED); }
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
document.fonts.load('40px "Patrick Hand SC"').then(() => document.fonts.load('40px "Permanent Marker"')).then(() => { window.ready = true; });
