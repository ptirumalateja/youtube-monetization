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
function glass(mood, b) { // mood 0 red (hostile) .. 0.5 neutral .. 1 warm (friendly)
  const R = b ? [218, 200, 196] : [232, 214, 210], N = b ? [214, 218, 216] : [228, 231, 229], Wm = b ? [232, 217, 184] : [240, 228, 204];
  const c = mood < 0.5 ? R.map((v, i) => lerp(v, N[i], mood * 2)) : N.map((v, i) => lerp(v, Wm[i], mood * 2 - 1)); return `rgb(${c.map(Math.round).join(',')})`; }
function mirror(g, t, m, dogFn, mood, crack) {
  const [x0, x1] = MIR[m], y0 = MTOP, y1 = MBOT, cx = (x0 + x1) / 2;
  // glass: pale grey-blue wash with a soft tint (red when hostile, warm when friendly)
  g.save(); archPath(g, x0, x1, y0, y1); g.clip();
  let gr = g.createLinearGradient(0, y0, 0, y1);
  gr.addColorStop(0, glass(mood, 0)); gr.addColorStop(1, glass(mood, 1)); g.fillStyle = gr; g.fillRect(x0, y0, x1 - x0, y1 - y0);
  const vy = y1 - 300;
  for (let k = 6; k >= 1; k--) { const sc = Math.pow(0.72, k);
    const ax0 = lerp(cx, x0, sc), ax1 = lerp(cx, x1, sc), ay0 = lerp(vy, y0, sc), ay1 = lerp(vy, y1, sc);
    inkLine(g, archPts(ax0, ax1, ay0, ay1), 1 + 1.2 * sc, `rgba(30,25,22,${0.25 + 0.3 * sc})`);
    inkLine(g, [[ax0, ay1], [ax1, ay1]], 1 + sc, `rgba(30,25,22,${0.2 + 0.3 * sc})`);
    if (k <= 3 && dogFn) dogFn(g, cx + (k % 2 ? 10 : -10) * sc, ay1, sc * 1.25, k, m);
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


function heart(g, x, y, r, a) { if (a <= 0) return; g.save(); g.globalAlpha = a; g.fillStyle = RED; g.strokeStyle = INK; g.lineWidth = 2; g.beginPath(); g.moveTo(x, y + r); g.bezierCurveTo(x - r * 1.6, y - r * 0.2, x - r * 0.8, y - r * 1.4, x, y - r * 0.5); g.bezierCurveTo(x + r * 0.8, y - r * 1.4, x + r * 1.6, y - r * 0.2, x, y + r); g.fill(); g.stroke(); g.restore(); }
function fitFont(g, txt, size, family, maxW) { g.font = `${size}px "${family}"`; const w = g.measureText(txt).width; if (w > maxW) { size *= maxW / w; g.font = `${size}px "${family}"`; } return size; }
function words(g, parts, x, y, size, maxW) { const full = parts.map(p => p[0]).join(''); fitFont(g, full, size, 'Patrick Hand SC', maxW); let w = g.measureText(full).width, cx = x - w / 2;
  g.textAlign = 'left'; for (const [s, c] of parts) { g.fillStyle = c; g.fillText(s, cx, y); cx += g.measureText(s).width; } }

// ======================= timeline (VO line [start, end] from vo/vo.json, atempo 1.08) =======================
const VO = [[0.1, 3.904], [4.286, 8.066], [8.278, 11.832], [12.087, 14.369], [14.624, 17.669], [17.924, 20.873], [21.128, 22.71], [23.305, 26.715], [26.927, 28.713], [29.053, 33.09], [33.6, 38.932], [39.357, 40.164], [40.377, 45.056], [45.353, 48.787], [49.169, 51.859], [52.199, 56.619], [57.086, 59.169]];
const DUR = 60.6;
// key word times
const K = {
  wipe1: 4.0, story: 4.3, mirrorsWord: 6.85, reveal: 7.55, enter: 8.3, surround: 10.42, growl: 12.0, growlBack: 12.85, teeth: 14.62, thousandMouths: 15.66,
  attack: 18.06, back: 19.12, night: 21.13, dropped: 22.3, wipe2: 22.85, morning: 23.3, wag: 25.95, tails: 26.95,
  same: 29.05, world: 31.73, name: 33.6, bias: 36.0, seeing: 37.28, wipe3: 39.05, everyday: 39.36, friend: 40.38, cold: 42.66, theyCold: 43.76,
  boss: 45.35, walkIn: 46.6, getOne: 48.21, most: 49.17, mirrorW: 52.2, barking: 54.0, barksBack: 54.88, cta: 57.0,
};
const win = (t, a, b) => t >= a && t < b;

// ======================= dog poses over time =======================
function walkPose(base, ph, amp = 1) { // simple trot: diagonal pairs swing
  const P = JSON.parse(JSON.stringify(base)); const a = Math.sin(ph), b = Math.sin(ph + Math.PI);
  const sw = (j, k, dx, lift) => { P[j] = [P[j][0] + dx * 0.5, P[j][1] - lift * 0.5]; P[k] = [P[k][0] + dx, P[k][1] - lift]; };
  sw('f1e', 'f1p', 13 * a * amp, Math.max(0, a) * 10 * amp); sw('r2k', 'r2p', 13 * a * amp, Math.max(0, a) * 9 * amp);
  sw('f2e', 'f2p', 13 * b * amp, Math.max(0, b) * 10 * amp); sw('r1k', 'r1p', 13 * b * amp, Math.max(0, b) * 9 * amp);
  const bob = Math.abs(Math.sin(ph)) * 3 * amp; for (const n of ['chest', 'hip', 'head', 'tail']) P[n] = [P[n][0], P[n][1] - bob];
  return P;
}
function lungeCycle(t, rate) { const c = (t * rate) % 1; const k = c < 0.3 ? eout(c / 0.3) : 1 - eio((c - 0.3) / 0.7); return dmix(SNARL, LUNGE, k * 0.9); }
// the first dog: returns {P, o}
function heroState(t) {
  let P = STAND, x = 330, sn = 0, alpha = 1, sh = 0;
  if (t < K.wipe1) { P = lungeCycle(t + 0.12, 1.5); sn = 1; }
  else if (t < K.enter) { alpha = 0; }
  else if (t < K.surround) { const k = clamp((t - K.enter) / (K.surround - K.enter - 0.3)); x = lerp(-120, 330, eout(k)); P = k < 1 ? walkPose(STAND, t * 11) : STAND; }
  else if (t < K.growl) { const j = Math.exp(-(t - K.surround) * 7); P = dmix(STAND, SNARL, 0.15 * (1 - j)); sh = j; P = JSON.parse(JSON.stringify(P)); for (const n of DK) P[n] = [P[n][0], P[n][1] - 14 * j * (n === 'f1p' || n === 'f2p' || n === 'r1p' || n === 'r2p' ? 0.4 : 1)]; sn = 0.1; }
  else if (t < K.attack) { sn = ss(K.growl, K.growl + 0.3, t) * 0.7 + 0.3 * ss(K.teeth, K.teeth + 0.3, t); P = dmix(STAND, SNARL, sn); }
  else if (t < K.dropped - 0.25) { const fast = t > K.night ? 2.6 : 1.5; P = lungeCycle(t - K.attack, fast); sn = 1; }
  else { const k = ss(K.dropped - 0.25, K.dropped + 0.25, t); P = dmix(SNARL, DOWN, eio(k)); sn = 1 - k; }
  return { P, o: { x, y: FLOOR + 56, s: 1.8, dir: 1, snarl: sn, alpha } };
}
function sheState(t) { // the second dog: walks in, wags
  const k = clamp((t - K.morning) / 1.9); const x = lerp(-130, 330, eout(k));
  const P = k < 1 ? walkPose(STAND, t * 10) : STAND; const wag = ss(K.wag - 0.1, K.wag + 0.2, t);
  return { P: wag > 0 ? dmix(STAND, HAPPY, wag) : P, o: { x, y: FLOOR + 56, s: 1.8, dir: 1, wag, happy: wag > 0.5 ? 1 : 0, collar: 1 } };
}
// ======================= hall scenes =======================
function moodAt(t) { // 0 red .. 0.5 neutral .. 1 warm
  if (t < K.wipe1) return 0;
  if (t < K.growl) return 0.5;
  if (t < K.wipe2) return lerp(0.5, 0, ss(K.growl, K.growlBack + 0.4, t));
  if (t < K.wag) return 0.5;
  return lerp(0.5, 1, ss(K.wag, K.tails + 0.5, t));
}
function hallScene(g, t) {
  const morning = t >= K.wipe2 + 0.075, night = t >= K.wipe1 && !morning;
  const mood = moodAt(t);
  hall(g, t, mood);
  // window light: moon at night, sun shaft in the morning
  if (morning) sunShaft(g, t);
  // reflections
  let dogFn = null; const crack = t < K.wipe1 ? 0.7 : t < K.attack ? 0 : t < K.wipe2 ? clamp(ss(K.attack, K.attack + 0.3, t) * 0.5 + ss(K.back, K.dropped, t) * 0.6, 0, 1.1) : 0.12;
  if (!morning) {
    const pop = t < K.wipe1 ? 1 : ss(K.surround, K.surround + 0.25, t);
    if (pop > 0) dogFn = (gg, x, y, sc, k, m) => {
      const hs = heroState(t - (t > K.growl && t < K.growlBack ? 0 : 0.04 * k));
      // in the growl beat the reflections answer ~0.8 s late (the dog growls first, the hall growls back)
      let P = hs.P, sn = hs.o.snarl;
      if (t >= K.growl && t < K.growlBack + 0.3) { const k2 = ss(K.growlBack - 0.1, K.growlBack + 0.2, t); P = dmix(STAND, SNARL, 0.7 * k2); sn = 0.7 * k2; }
      if (t >= K.surround && t < K.growl) { P = STAND; sn = 0; }
      const pk = clamp(pop * 1.2 - (k - 1) * 0.1);
      drawDog(gg, P, { x, y, s: sc * (0.6 + 0.4 * eout(pk)), dir: (k + m) % 2 ? -1 : 1, snarl: sn, alpha: pk, far: k > 1 });
    };
  } else {
    const pop = ss(K.morning + 1.2, K.morning + 1.6, t);
    if (pop > 0) dogFn = (gg, x, y, sc, k, m) => { const s2 = sheState(t - 0.05 * k); drawDog(gg, s2.P, { x, y, s: sc, dir: (k + m) % 2 ? -1 : 1, wag: s2.o.wag, happy: s2.o.happy, collar: 1, alpha: pop, far: k > 1 }); };
  }
  for (let m = 0; m < 3; m++) mirror(g, t, m, dogFn, mood, crack * (m === 1 ? 0.7 : 1) * (m === 0 ? 0.8 : 1));
  if (night) nightWash(g, t);
  // hero / her + shadow
  const st = morning ? sheState(t) : heroState(t);
  if (st.o.alpha !== 0) {
    g.save(); g.fillStyle = 'rgba(30,25,22,0.18)'; g.beginPath(); g.ellipse(st.o.x - 10, st.o.y + 4, 120, 10, 0, 0, 7); g.fill(); g.restore();
    drawDog(g, st.P, st.o);
    if (st.o.collar) collar(g, st.P, st.o);
  }
  // fallen hero stays faint in the morning hall? no - the morning is a new day; keep the cracks as the only trace
  if (morning) { for (let i = 0; i < 6; i++) { const ph = ((t - K.tails) * 0.45 + i / 6) % 1; if (t > K.tails) heart(g, 80 + i * 112 + Math.sin(t * 2 + i) * 10, 740 - ph * 300, 9, Math.sin(ph * Math.PI)); } }
  // surprise mark when the hall fills
  if (win(t, K.surround, K.surround + 0.9)) { const k = ss(K.surround, K.surround + 0.15, t) * (1 - ss(K.surround + 0.7, K.surround + 0.9, t)); g.save(); g.globalAlpha = k; g.font = '64px "Permanent Marker"'; g.fillStyle = RED; g.textAlign = 'center'; g.fillText('!', 470, 650); g.restore(); }
  // impact flashes on each attack
  if (t >= K.attack && t < K.dropped) { const c = ((t - K.attack) * (t > K.night ? 2.6 : 1.5)) % 1; if (c > 0.22 && c < 0.42) impact(g, 520, 700, (c - 0.22) / 0.2); }
}
function collar(g, P, o) { const s = o.s, X = p => o.x + p[0] * o.dir * s, Y = p => o.y + p[1] * s; const a = [P.chest[0] + 6, P.chest[1] - 6], b = [P.head[0] - 10, P.head[1] + 8];
  const c = [lerp(a[0], b[0], 0.55), lerp(a[1], b[1], 0.55)]; g.save(); g.translate(X(c), Y(c)); g.rotate(-0.9 * o.dir); g.fillStyle = RED; g.strokeStyle = INK; g.lineWidth = 2.6; g.beginPath(); g.roundRect(-22 * s * 0.5, -5 * s * 0.5, 44 * s * 0.5, 10 * s * 0.5, 3); g.fill(); g.stroke();
  g.fillStyle = '#e8b84a'; g.beginPath(); g.arc(0, 8 * s * 0.5, 4.5 * s * 0.5, 0, 7); g.fill(); g.stroke(); g.restore(); }
function impact(g, x, y, k) { g.save(); g.globalAlpha = 1 - k; g.strokeStyle = RED; g.lineWidth = 4; g.lineCap = 'round'; for (let i = 0; i < 9; i++) { const a = i / 9 * Math.PI * 2, r0 = 20 + 40 * k, r1 = r0 + 26; g.beginPath(); g.moveTo(x + Math.cos(a) * r0, y + Math.sin(a) * r0); g.lineTo(x + Math.cos(a) * r1, y + Math.sin(a) * r1); g.stroke(); } g.restore(); }
function nightWash(g, t) { // the night: a cool grey-blue wash over the paper, still light (no dark edges)
  const k = ss(K.wipe1, K.wipe1 + 0.2, t) * (t > K.night ? 1 : 0.55);
  g.save(); g.globalCompositeOperation = 'multiply'; g.fillStyle = `rgba(190,198,214,${0.55 * k})`; g.fillRect(-200, -200, DW + 400, DH + 400); g.restore();
  // moon in the top window
  g.save(); g.globalAlpha = k; g.fillStyle = '#f7f1e2'; g.strokeStyle = INK; g.lineWidth = 3; g.beginPath(); g.arc(600, 120, 30, 0, 7); g.fill(); g.stroke(); g.fillStyle = 'rgba(30,25,22,0.12)'; g.beginPath(); g.arc(590, 112, 6, 0, 7); g.arc(610, 130, 4, 0, 7); g.fill(); g.restore();
  // night clock: hand spins during "all night"
  if (t > K.night - 0.2) { const k2 = ss(K.night - 0.2, K.night, t) * (1 - ss(K.dropped + 0.2, K.dropped + 0.5, t)); const a = (t - K.night) * 9; g.save(); g.globalAlpha = k2; g.translate(120, 120); g.fillStyle = FILL; g.beginPath(); g.arc(0, 0, 34, 0, 7); g.fill(); inkLine(g, archPts(-34, 34, -34, 0, 20).slice(2), 3); g.strokeStyle = INK; g.lineWidth = 3; g.beginPath(); g.arc(0, 0, 34, 0, 7); g.stroke(); g.lineWidth = 3.5; g.lineCap = 'round'; g.beginPath(); g.moveTo(0, 0); g.lineTo(Math.sin(a) * 24, -Math.cos(a) * 24); g.moveTo(0, 0); g.lineTo(Math.sin(a / 12) * 15, -Math.cos(a / 12) * 15); g.stroke(); g.restore(); }
}
function sunShaft(g, t) { const k = ss(K.wipe2 + 0.3, K.morning + 0.6, t); g.save(); g.globalAlpha = 0.5 * k; g.fillStyle = '#fff6d8'; g.beginPath(); g.moveTo(520, -20); g.lineTo(640, -20); g.lineTo(420, DH); g.lineTo(180, DH); g.closePath(); g.fill(); g.restore();
  g.save(); g.globalAlpha = k; g.strokeStyle = INK; g.lineWidth = 3; g.fillStyle = '#f3d36a'; g.beginPath(); g.arc(600, 110, 28, 0, 7); g.fill(); g.stroke(); for (let i = 0; i < 10; i++) { const a = i / 10 * Math.PI * 2 + t * 0.4; g.beginPath(); g.moveTo(600 + Math.cos(a) * 38, 110 + Math.sin(a) * 38); g.lineTo(600 + Math.cos(a) * 50, 110 + Math.sin(a) * 50); g.stroke(); } g.restore(); }


// ======================= story intro: fly through the endless mirror tunnel =======================
function tunnelScene(g, t) {
  paper(g, t);
  for (let i = 0; i < 26; i++) inkLine(g, [[-20, 20 + i * 50], [740, 20 + i * 50]], 1.1, 'rgba(30,25,22,0.14)');
  const u = Math.max(0, t - K.wipe1), f = 1.25 * u + 0.22 * u * u; // levels travelled, accelerating
  const fr = f % 1, cx = 360, cy = 720, rot = 0.035 * Math.sin(u * 1.3);
  g.save(); g.translate(cx, cy); g.rotate(rot); g.translate(-cx, -cy);
  for (let j = 0; j < 13; j++) {
    const sc = Math.pow(0.72, j - fr) * 1.05; const w = 640 * sc, h = 1180 * sc; const x0 = cx - w / 2, x1 = cx + w / 2, y1 = cy + h * 0.5, y0 = y1 - h;
    const a = j > 9 ? clamp(1 - (j - 9 - fr) / 3) : 1; if (a <= 0) continue;
    g.save(); g.globalAlpha = a;
    // glass
    archPath(g, x0, x1, y0, y1); const gr = g.createLinearGradient(0, y0, 0, y1); gr.addColorStop(0, glass(0.5, 0)); gr.addColorStop(1, glass(0.5, 1)); g.fillStyle = gr; g.fill();
    // floor line inside this mirror
    inkLine(g, [[x0, y1 - 1], [x1, y1 - 1]], Math.max(1, 2.4 * sc), INK);
    // gilded frame
    g.lineWidth = Math.max(2, 14 * sc); g.strokeStyle = '#c9ae86'; archPath(g, x0 - 4 * sc, x1 + 4 * sc, y0 - 4 * sc, y1); g.stroke();
    inkLine(g, archPts(x0 - 11 * sc, x1 + 11 * sc, y0 - 11 * sc, y1, 20), Math.max(1, 3.4 * sc)); inkLine(g, archPts(x0, x1, y0, y1, 20), Math.max(0.8, 2.6 * sc));
    // two little candles at the foot of every frame
    for (const sx of [-1, 1]) { const px = cx + sx * (w / 2 + 34 * sc), py = y1 - 6 * sc, fl = 0.85 + 0.15 * Math.sin(t * 17 + j * 2 + sx);
      g.fillStyle = FILL; g.strokeStyle = INK; g.lineWidth = Math.max(0.8, 2.4 * sc); g.beginPath(); g.rect(px - 7 * sc, py - 40 * sc, 14 * sc, 40 * sc); g.fill(); g.stroke();
      g.fillStyle = '#f0a43a'; g.beginPath(); g.moveTo(px, py - 66 * sc * fl); g.quadraticCurveTo(px + 8 * sc, py - 48 * sc, px, py - 42 * sc); g.quadraticCurveTo(px - 8 * sc, py - 48 * sc, px, py - 66 * sc * fl); g.fill(); g.stroke(); }
    g.restore();
  }
  { const gr = g.createRadialGradient(cx, cy + 40, 0, cx, cy + 40, 360); gr.addColorStop(0, 'rgba(255,196,120,0.35)'); gr.addColorStop(1, 'rgba(255,196,120,0)'); g.fillStyle = gr; g.fillRect(cx - 400, cy - 400, 800, 800); }
  // a lone silhouette deep in the tunnel: the stray, far away, getting closer (foreshadow)
  const ds = 0.32 + 0.1 * u; g.save(); g.fillStyle = 'rgba(30,25,22,0.15)'; g.beginPath(); g.ellipse(cx, cy + 70, 60 * ds, 6 * ds, 0, 0, 7); g.fill(); g.restore(); drawDog(g, walkPose(STAND, t * 9), { x: cx, y: cy + 70, s: ds, dir: 1, alpha: 0.95 });
  g.restore();
  // sheen sweep on "mirrors"
  const sk = clamp((t - K.mirrorsWord + 0.1) / 0.5); if (sk > 0 && sk < 1) { const x = lerp(-300, 1000, sk); g.save(); g.globalAlpha = 0.55 * Math.sin(sk * Math.PI); g.fillStyle = '#ffffff'; g.beginPath(); g.moveTo(x, -50); g.lineTo(x + 90, -50); g.lineTo(x - 210, DH + 50); g.lineTo(x - 300, DH + 50); g.closePath(); g.fill(); g.restore(); }
}

// ======================= split: same room, different world =======================
function splitScene(g, t) {
  const k = eio(ss(K.same, K.same + 0.5, t));
  // left: red hall + snarling dog; right: warm hall + happy dog. Each half is the hall drawn at 0.5 scale... drawn full and clipped.
  for (const side of [0, 1]) {
    g.save(); g.beginPath(); side ? g.rect(360, -50, 420, DH + 100) : g.rect(-60, -50, 420, DH + 100); g.clip();
    g.translate(side ? 180 : -180, 0); g.translate(360, 640); g.scale(lerp(1, 1, k), 1); g.translate(-360, -640);
    const mood = side ? 1 : 0; hall(g, t, mood);
    const fn = side ? (gg, x, y, sc, kk, m) => drawDog(gg, HAPPY, { x, y, s: sc, dir: (kk + m) % 2 ? -1 : 1, wag: 1, happy: 1, collar: 1, far: kk > 1 })
      : (gg, x, y, sc, kk, m) => drawDog(gg, lungeCycle(t - 0.05 * kk, 1.4), { x, y, s: sc, dir: (kk + m) % 2 ? -1 : 1, snarl: 1, far: kk > 1 });
    mirror(g, t, 1, fn, mood, side ? 0 : 0.6);
    g.save(); g.fillStyle = 'rgba(30,25,22,0.18)'; g.beginPath(); g.ellipse(330, FLOOR + 60, 110, 9, 0, 0, 7); g.fill(); g.restore();
    if (side) { const o = { x: 360, y: FLOOR + 56, s: 1.6, dir: 1, wag: 1, happy: 1, collar: 1 }; drawDog(g, HAPPY, o); collar(g, HAPPY, o); }
    else drawDog(g, lungeCycle(t, 1.4), { x: 330, y: FLOOR + 56, s: 1.6, dir: 1, snarl: 1 });
    g.restore();
  }
  // torn-paper divider
  const pts = []; for (let y = -20; y <= DH + 20; y += 26) pts.push([360 + (hash(y) - 0.5) * 10, y]); inkLine(g, pts, 5);
}

// ======================= concept card: hostile attribution bias =======================
function conceptScene(g, t) {
  paper(g, t);
  // one mirror, a calm reflection; the dog sees a snarling one in his thought bubble
  const x0 = 330, x1 = 640, y0 = 400, y1 = 806;
  g.save(); archPath(g, x0, x1, y0, y1); g.clip(); g.fillStyle = glass(0.5, 0); g.fillRect(x0, y0, x1 - x0, y1 - y0);
  drawDog(g, STAND, { x: 500, y: y1 - 6, s: 1.5, dir: -1, far: false, alpha: 0.95 }); g.restore();
  g.save(); g.lineWidth = 14; g.strokeStyle = '#c9ae86'; archPath(g, x0 - 4, x1 + 4, y0 - 4, y1); g.stroke(); g.restore();
  inkLine(g, archPts(x0 - 11, x1 + 11, y0 - 11, y1), 3.4); inkLine(g, archPts(x0, x1, y0, y1), 2.6);
  inkLine(g, [[-20, FLOOR + 1], [740, FLOOR - 1]], 3.5);
  const sn = ss(K.name + 0.3, K.name + 0.8, t);
  drawDog(g, dmix(STAND, SNARL, sn), { x: 170, y: FLOOR + 56, s: 1.7, dir: 1, snarl: sn });
  // thought bubble with the snarling version (what he THINKS he sees)
  const b = ss(K.seeing - 0.1, K.seeing + 0.3, t);
  if (b > 0) { g.save(); g.globalAlpha = b; const bx = 250, by = 520;
    for (const [x, y, r] of [[230, 680, 7], [215, 645, 11]]) { g.fillStyle = FILL; g.strokeStyle = INK; g.lineWidth = 3; g.beginPath(); g.arc(x + 0, y, r, 0, 7); g.fill(); g.stroke(); }
    g.fillStyle = FILL; g.beginPath(); g.ellipse(bx - 30, by + 20, 110, 80, 0, 0, 7); g.fill(); inkLine(g, Array.from({ length: 41 }, (_, i) => { const a = i / 40 * Math.PI * 2; return [bx - 30 + Math.cos(a) * (110 + 6 * Math.sin(a * 9)), by + 20 + Math.sin(a) * (80 + 6 * Math.sin(a * 9))]; }), 3);
    drawDog(g, SNARL, { x: bx - 40, y: by + 70, s: 0.85, dir: 1, snarl: 1 }); g.restore(); }
  // title card like a chapter heading
  const tk = ss(K.bias - 0.1, K.bias + 0.25, t);
  g.save(); g.globalAlpha = tk; g.textAlign = 'center'; g.font = '56px "Permanent Marker"'; g.fillStyle = INK; const tw = Math.min(600, g.measureText('HOSTILE ATTRIBUTION BIAS').width);
  fitFont(g, 'HOSTILE ATTRIBUTION BIAS', 50, 'Permanent Marker', 600); g.fillText('HOSTILE ATTRIBUTION BIAS', 360, 318);
  const ul = ss(K.bias + 0.1, K.bias + 0.6, t); inkLine(g, [[90, 336], [lerp(90, 630, ul), 333]], 5, RED); g.restore();
}

// ======================= people (ink style, round heads like the dog) =======================
// pose: {x, y(ground), s, dir, face:'calm'|'frown'|'angry'|'smile'|'shout', arms:'down'|'phone'|'fists'|'point', turn: 0..1 (1 = back to us), walk ph}
function person(g, o) {
  const s = o.s, d = o.dir; const X = v => o.x + v * d * s, Y = v => o.y + v * s; const ph = o.walk || 0, wa = o.walk != null ? 1 : 0;
  const parts = []; // [type, data]
  const hip = [0, -80], sh = [0, -158], head = [0, -200];
  const legs = [[[hip[0] - 8, hip[1]], [-8 + 14 * Math.sin(ph) * wa, -40], [-10 + 22 * Math.sin(ph) * wa, 0]], [[hip[0] + 8, hip[1]], [8 - 14 * Math.sin(ph) * wa, -40], [10 - 22 * Math.sin(ph) * wa, 0]]];
  let arms;
  if (o.arms === 'phone') arms = [[[ -14, -150], [-22, -110], [14, -112]], [[14, -150], [26, -112], [20, -112]]];
  else if (o.arms === 'fists') arms = [[[-14, -150], [-4, -122], [26, -136]], [[14, -150], [34, -126], [46, -146]]];
  else if (o.arms === 'open') arms = [[[-14, -150], [-40, -128], [-58, -146]], [[14, -150], [40, -128], [58, -146]]];
  else arms = [[[-14, -150], [-22 - 6 * Math.sin(ph) * wa, -112], [-20 - 14 * Math.sin(ph) * wa, -76]], [[14, -150], [22 + 6 * Math.sin(ph) * wa, -112], [20 + 14 * Math.sin(ph) * wa, -76]]];
  const L = (pts, w) => ({ t: 'l', p: pts, w });
  const body = [L(legs[0], 15), L(legs[1], 15), { t: 'r', c: [0, -118], w: 56, h: 84, r: 22 }, L(arms[0], 13), L(arms[1], 13), { t: 'e', c: head, rx: 36, ry: 36 }];
  const oo = { x: o.x, y: o.y, s, dir: d };
  g.save(); g.globalAlpha = o.alpha ?? 1;
  const draw = (q, w, col) => { if (q.t === 'r') { g.fillStyle = col; const c = jit(X(q.c[0]) - (q.w + w) * s / 2 * 1, Y(q.c[1]) - (q.h + w) * s / 2, 0.5); g.beginPath(); g.roundRect(c[0], c[1], (q.w + w) * s, (q.h + w) * s, (q.r + w / 2) * s); g.fill(); } else prim(g, q, oo, w, col); };
  for (const q of body) draw(q, 6.5, INK); for (const q of body) draw(q, 0, o.fill || FILL);
  // hands as fists / phone
  for (const a of arms) { const h = a[2]; g.fillStyle = FILL; g.strokeStyle = INK; g.lineWidth = 3 * s; g.beginPath(); g.arc(X(h[0]), Y(h[1]), (o.arms === 'fists' ? 10 : 8) * s, 0, 7); g.fill(); g.stroke(); }
  if (o.arms === 'phone') { g.save(); g.translate(X(16), Y(-128)); g.rotate(-0.15 * d); g.fillStyle = INK; g.beginPath(); g.roundRect(-11 * s, -20 * s, 22 * s, 36 * s, 4 * s); g.fill(); g.fillStyle = o.screen || '#cfe0e6'; g.fillRect(-8 * s, -16 * s, 16 * s, 26 * s); g.restore(); }
  // face (hidden when turned away)
  if ((o.turn || 0) < 0.5) {
    const hx = X(head[0]) + 6 * d * s, hy = Y(head[1]); g.strokeStyle = INK; g.fillStyle = INK; g.lineCap = 'round'; g.lineWidth = 3.2 * s; const f = o.face || 'calm';
    const ex = [-12, 12];
    for (const e of ex) { const x = hx + e * s, y = hy - 4 * s;
      if (f === 'smile') { g.beginPath(); g.arc(x, y + 2 * s, 5 * s, Math.PI * 1.1, Math.PI * 1.9); g.stroke(); }
      else { g.beginPath(); g.arc(x, y, 3.4 * s, 0, 7); g.fill(); }
      if (f === 'angry' || f === 'shout' || f === 'frown') { const tilt = f === 'frown' ? 0.4 : 1; g.beginPath(); g.moveTo(x - 7 * s * Math.sign(e), y - 12 * s + (e < 0 ? -1 : 1) * 0 - 4 * s * tilt); g.lineTo(x + 7 * s * Math.sign(e), y - 9 * s + 3 * s * tilt); g.stroke(); } }
    g.beginPath();
    if (f === 'smile') { g.arc(hx, hy + 8 * s, 10 * s, 0.15 * Math.PI, 0.85 * Math.PI); g.stroke(); }
    else if (f === 'frown' || f === 'angry') { g.arc(hx, hy + 22 * s, 9 * s, 1.2 * Math.PI, 1.8 * Math.PI); g.stroke(); }
    else if (f === 'shout') { g.fillStyle = RED; g.ellipse(hx, hy + 14 * s, 9 * s, 7 * s, 0, 0, 7); g.fill(); g.stroke(); }
    else { g.moveTo(hx - 7 * s, hy + 13 * s); g.lineTo(hx + 7 * s, hy + 13 * s); g.stroke(); }
    if (f === 'angry' || f === 'shout') { g.fillStyle = 'rgba(224,90,76,0.35)'; for (const e of ex) { g.beginPath(); g.ellipse(hx + e * 1.3 * s, hy + 8 * s, 6 * s, 3.5 * s, 0, 0, 7); g.fill(); } }
  }
  if (o.mad) { g.save(); g.strokeStyle = RED; g.lineWidth = 3.2 * s; g.lineCap = 'round'; const ax = X(head[0]) - 26 * d * s, ay = Y(head[1]) - 40 * s; for (let i = 0; i < 4; i++) { const a = i * Math.PI / 2 + 0.6; g.beginPath(); g.moveTo(ax + Math.cos(a) * 4 * s, ay + Math.sin(a) * 4 * s); g.quadraticCurveTo(ax + Math.cos(a + 0.5) * 9 * s, ay + Math.sin(a + 0.5) * 9 * s, ax + Math.cos(a) * 12 * s, ay + Math.sin(a) * 12 * s); g.stroke(); } g.restore(); }
  g.restore();
}
function bubble(g, x, y, w, h, txt, k, tailDir = -1, col = FILL, txtCol = INK, size = 28) {
  if (k <= 0) return; g.save(); g.globalAlpha = Math.min(1, k * 1.5); g.translate(x, y); const sc = 0.7 + 0.3 * eout(clamp(k)); g.scale(sc, sc);
  g.fillStyle = col; g.strokeStyle = INK; g.lineWidth = 3; g.beginPath(); g.roundRect(-w / 2, -h / 2, w, h, 16); g.fill(); g.stroke();
  g.beginPath(); g.moveTo(tailDir * w * 0.25 - 10, h / 2 - 1.5); g.lineTo(tailDir * w * 0.25 + tailDir * 6, h / 2 + 18); g.lineTo(tailDir * w * 0.25 + 12, h / 2 - 1.5); g.fill(); g.stroke();
  g.fillStyle = col; g.fillRect(tailDir * w * 0.25 - 9, h / 2 - 5, 20, 6);
  g.fillStyle = txtCol; g.textAlign = 'center'; g.textBaseline = 'middle'; fitFont(g, txt, size + 6, 'Patrick Hand SC', w - 26); g.fillText(txt, 0, 2); g.textBaseline = 'alphabetic'; g.restore();
}
// big wall mirror behind the person (a "person hall"): his reflection copies him
function bigMirror(g, t, mood, reflFn) {
  const x0 = 120, x1 = 600, y0 = 300, y1 = 820;
  g.save(); archPath(g, x0, x1, y0, y1); g.clip(); let gr = g.createLinearGradient(0, y0, 0, y1); gr.addColorStop(0, glass(mood, 0)); gr.addColorStop(1, glass(mood, 1)); g.fillStyle = gr; g.fillRect(x0, y0, x1 - x0, y1 - y0);
  const cx = 360, vy = y1 - 330; for (let k = 5; k >= 1; k--) { const sc = Math.pow(0.74, k); const ax0 = lerp(cx, x0, sc), ax1 = lerp(cx, x1, sc), ay0 = lerp(vy, y0, sc), ay1 = lerp(vy, y1, sc);
    inkLine(g, archPts(ax0, ax1, ay0, ay1), 1 + 1.2 * sc, `rgba(30,25,22,${0.22 + 0.3 * sc})`); if (k <= 3 && reflFn) reflFn(g, cx + (k % 2 ? 60 : -60) * sc, ay1, sc * 1.25, k); }
  g.strokeStyle = 'rgba(255,255,255,0.75)'; g.lineWidth = 6; g.lineCap = 'round'; g.beginPath(); g.moveTo(x0 + 40, y0 + 260); g.lineTo(x0 + 100, y0 + 180); g.moveTo(x0 + 40, y0 + 300); g.lineTo(x0 + 130, y0 + 190); g.stroke(); g.restore();
  g.save(); g.lineWidth = 16; g.strokeStyle = '#c9ae86'; archPath(g, x0 - 5, x1 + 5, y0 - 5, y1); g.stroke(); g.restore();
  inkLine(g, archPts(x0 - 13, x1 + 13, y0 - 13, y1), 3.6); inkLine(g, archPts(x0, x1, y0, y1), 2.8);
}
function peopleScene(g, t) {
  paper(g, t);
  for (let i = 0; i < 6; i++) inkLine(g, [[-20, 150 + i * 46], [740, 150 + i * 46]], 1.1, 'rgba(30,25,22,0.16)');
  inkLine(g, [[-20, FLOOR + 1], [740, FLOOR - 1]], 3.5); for (let i = -6; i <= 6; i++) inkLine(g, [[360 + i * 70, FLOOR + 8], [360 + i * 70 * 2.6, DH + 30]], 1.2, 'rgba(30,25,22,0.2)');
  const Y0 = FLOOR + 60;
  if (t < K.boss) { // friend doesn't reply
    const coldK = ss(K.cold - 0.2, K.cold + 0.3, t), theyK = ss(K.theyCold - 0.2, K.theyCold + 0.3, t);
    const mood = lerp(0.5, 0.15, coldK);
    bigMirror(g, t, mood, (gg, x, y, sc, k) => person(gg, { x, y, s: sc * 0.9, dir: -1, face: coldK > 0.5 ? 'frown' : 'calm', arms: 'phone', alpha: 0.85, turn: coldK }));
    // him (left), facing right, phone
    person(g, { x: 200, y: Y0, s: 1.6, dir: coldK > 0.5 ? -1 : 1, face: t > K.friend + 1.0 ? 'frown' : 'calm', arms: 'phone', mad: coldK > 0.5 });
    // the friend (right), small at first, turns away when "now they go cold too"
    person(g, { x: 535, y: Y0, s: 1.4, dir: theyK > 0.5 ? 1 : -1, face: theyK > 0.5 ? 'frown' : 'smile', arms: 'phone', fill: '#f4eadb' });
    // chat bubbles
    const b1 = ss(K.friend, K.friend + 0.25, t); bubble(g, 230, 330, 270, 66, 'hey. you free?', b1, 1);
    const seen = ss(K.friend + 0.5, K.friend + 0.7, t); if (seen > 0) { g.save(); g.globalAlpha = seen; g.font = '22px "Patrick Hand SC"'; g.fillStyle = 'rgba(30,25,22,0.7)'; g.textAlign = 'right'; g.fillText('seen 11:42 pm', 350, 392); g.restore(); }
    const think = ss(K.friend + 1.0, K.friend + 1.3, t); bubble(g, 230, 440, 330, 64, '"they\'re ignoring me."', think, -1, FILL, RED, 32);
    // cold: frost marks between them
    if (coldK > 0) { g.save(); g.globalAlpha = coldK; g.strokeStyle = '#6a8ca0'; g.lineWidth = 3; for (let i = 0; i < 5; i++) { const x = 330 + i * 18, y = 700 + (i % 2) * 20; g.beginPath(); for (let a = 0; a < 3; a++) { const an = a * Math.PI / 3; g.moveTo(x - Math.cos(an) * 10, y - Math.sin(an) * 10); g.lineTo(x + Math.cos(an) * 10, y + Math.sin(an) * 10); } g.stroke(); } g.restore(); }
  } else if (t < K.most) { // boss sounds short
    const walkK = clamp((t - K.walkIn) / 1.0), getK = ss(K.getOne - 0.15, K.getOne + 0.15, t);
    const mood = lerp(0.5, 0, ss(K.walkIn, K.getOne, t));
    bigMirror(g, t, mood, (gg, x, y, sc, k) => person(gg, { x, y, s: sc * 0.9, dir: -1, face: walkK > 0 ? 'angry' : 'calm', arms: walkK > 0 ? 'fists' : 'down', alpha: 0.85 }));
    const bossFace = getK > 0.5 ? 'shout' : 'calm';
    person(g, { x: 550, y: Y0, s: 1.6, dir: -1, face: bossFace, arms: getK > 0.5 ? 'fists' : 'down', fill: '#efe3cf', mad: getK > 0.5 });
    const hx = lerp(60, 230, eout(walkK)); person(g, { x: hx, y: Y0, s: 1.6, dir: 1, face: walkK > 0 ? 'angry' : 'frown', arms: walkK > 0 ? 'fists' : 'down', walk: walkK > 0 && walkK < 1 ? t * 10 : null, mad: walkK > 0 });
    bubble(g, 520, 340, 290, 66, 'my office. now.', ss(K.boss, K.boss + 0.25, t), 1);
    if (getK > 0) { const k = clamp((t - K.getOne) / 0.5); impactBig(g, 400, 640, k); }
  } else { // most enemies are our own reflection -> the world is a mirror
    const smileK = ss(K.mirrorW + 0.35, K.mirrorW + 0.8, t), dogK = ss(K.barking, K.barking + 1.0, t);
    const mood = smileK > 0 ? lerp(0, 1, smileK) : 0;
    bigMirror(g, t, mood, (gg, x, y, sc, k) => person(gg, { x, y, s: sc * 0.9, dir: -1, face: smileK > 0.5 ? 'smile' : 'angry', arms: smileK > 0.5 ? 'open' : 'fists', alpha: 0.9, mad: smileK < 0.5 }));
    person(g, { x: 290, y: Y0, s: 1.7, dir: 1, face: smileK > 0.5 ? 'smile' : 'angry', arms: smileK > 0.5 ? 'open' : 'fists', mad: smileK < 0.5 });
    if (dogK > 0) { const x = lerp(-120, 490, eout(dogK)); const o = { x, y: Y0, s: 1.35, dir: 1, wag: 1, happy: 1, collar: 1 }; drawDog(g, dogK < 1 ? walkPose(STAND, t * 10) : HAPPY, o); collar(g, HAPPY, o); }
    if (smileK > 0) for (let i = 0; i < 5; i++) { const ph = ((t - K.mirrorW) * 0.4 + i / 5) % 1; heart(g, 150 + i * 105, 700 - ph * 260, 8, Math.sin(ph * Math.PI) * smileK); }
  }
}
function impactBig(g, x, y, k) { g.save(); g.globalAlpha = 1 - k * 0.6; const r = 40 + 70 * eout(k); g.fillStyle = RED; g.strokeStyle = INK; g.lineWidth = 3; g.beginPath();
  for (let i = 0; i <= 24; i++) { const a = i / 24 * Math.PI * 2, rr = r * (i % 2 ? 0.55 : 1) * (0.9 + 0.2 * hash(i)); g.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr); } g.closePath(); g.fill(); g.stroke();
  g.fillStyle = FILL; g.textAlign = 'center'; g.font = `${28 + 10 * eout(k)}px "Permanent Marker"`; g.fillText('FIGHT!', x, y + 10); g.restore(); }

// ======================= CTA =======================
function ctaScene(g, t) {
  paper(g, t); inkLine(g, [[-20, FLOOR + 1], [740, FLOOR - 1]], 3.5);
  const o = { x: 330, y: FLOOR + 60, s: 1.7, dir: 1, wag: 1, happy: 1, collar: 1 }; drawDog(g, HAPPY, o); collar(g, HAPPY, o);
  // share arrow
  const k = ss(K.cta, K.cta + 0.4, t); g.save(); g.globalAlpha = k; g.translate(360, 360); g.scale(0.8 + 0.2 * eout(k), 0.8 + 0.2 * eout(k));
  g.fillStyle = FILL; g.strokeStyle = INK; g.lineWidth = 5; g.lineJoin = 'round'; g.beginPath(); g.moveTo(-70, 40); g.quadraticCurveTo(-60, -30, 20, -30); g.lineTo(20, -60); g.lineTo(80, -10); g.lineTo(20, 40); g.lineTo(20, 10); g.quadraticCurveTo(-30, 10, -70, 40); g.closePath(); g.fill(); g.stroke(); g.restore();
}

// ======================= transitions =======================
function inkWipe(g, k) { // black torn edge sweeps right -> left, covers, then uncovers
  if (k <= 0 || k >= 1) return; const e = k < 0.5 ? lerp(DW + 60, -60, eio(k * 2)) : -60, e2 = k < 0.5 ? DW + 60 : lerp(DW + 60, -60, eio((k - 0.5) * 2));
  // band = between the two edges: draw as clip of region x in [e, e2]
  g.save(); g.beginPath(); g.moveTo(e, -40); for (let y = -40; y <= DH + 40; y += 24) g.lineTo(e + (hash(y * 0.7 + 3) - 0.5) * 50, y); for (let y = DH + 40; y >= -40; y -= 30) g.lineTo(Math.min(e2, DW + 60) + (hash(y * 0.3) - 0.5) * 40, y); g.closePath();
  g.fillStyle = '#16120f'; g.fill(); for (let i = 0; i < 14; i++) { const y = hash(i * 5) * DH, x = e - 20 - hash(i * 3) * 40; g.beginPath(); g.arc(x, y, 3 + 6 * hash(i), 0, 7); g.fill(); } g.restore();
}
const WIPES = [[K.wipe1 - 0.25, 0.5], [K.wipe2 - 0.2, 0.55], [K.wipe3 - 0.15, 0.5], [K.cta - 0.4, 0.5]];

// ======================= text =======================
const CAPS = [ // [t0, t1, line]  one short punchy line per beat, timed to the VO
  [K.story + 0.2, K.reveal, [['A HALL OF ', INK], ['MIRRORS.', RED]]],
  [K.enter, K.surround, [['ONE STRAY DOG.', INK]]],
  [K.surround, K.growl, [['SURROUNDED.', RED]]],
  [K.growl, K.growlBack, [['HE GROWLED.', INK]]],
  [K.growlBack, K.teeth, [['THEY ', INK], ['GROWLED BACK.', RED]]],
  [K.teeth, K.thousandMouths, [['TEETH.', INK]]],
  [K.thousandMouths, K.attack, [['1,000 MOUTHS.', RED]]],
  [K.attack, K.back, [['HE ATTACKED.', INK]]],
  [K.back, K.night, [['THEY ', INK], ['ATTACKED BACK.', RED]]],
  [K.night, K.dropped - 0.05, [['ALL NIGHT.', INK]]],
  [K.dropped - 0.05, K.wipe2 - 0.3, [['UNTIL HE ', INK], ['DROPPED.', RED]]],
  [K.morning, K.wag, [['NEXT MORNING...', INK]]],
  [K.wag, K.tails, [['SHE ', INK], ['WAGGED.', RED]]],
  [K.tails, K.same, [['1,000 TAILS ', RED], ['WAGGED BACK.', INK]]],
  [K.same, K.world, [['SAME ROOM.', INK]]],
  [K.world, K.name - 0.1, [['DIFFERENT ', INK], ['WORLD.', RED]]],
  [K.name, K.bias - 0.1, [['IT HAS A NAME:', INK]]],
  [K.seeing, K.wipe3 - 0.1, [['SEEING ATTACKS ', RED], ['THAT AREN\'T THERE.', INK]]],
  [K.everyday, K.friend, [['WE DO IT ', INK], ['TOO.', RED]]],
  [K.friend, K.cold - 0.1, [['NO REPLY?', INK]]],
  [K.cold - 0.1, K.theyCold - 0.1, [['YOU GO ', INK], ['COLD.', RED]]],
  [K.theyCold - 0.1, K.boss, [['THEY GO ', INK], ['COLD TOO.', RED]]],
  [K.boss, K.walkIn, [['SHORT TONE?', INK]]],
  [K.walkIn, K.getOne - 0.05, [['YOU WALK IN ', INK], ['READY TO FIGHT.', RED]]],
  [K.getOne - 0.05, K.most, [['YOU ', INK], ['GET ONE.', RED]]],
  [K.most, K.mirrorW, [['THE ENEMY? ', INK], ['YOUR REFLECTION.', RED]]],
];
function caption(g, t) {
  for (const [t0, t1, a] of CAPS) { if (t < t0 || t >= t1) continue; const k = ss(t0, t0 + 0.1, t), pop = 1 + 0.1 * Math.exp(-(t - t0) * 12);
    g.save(); g.globalAlpha = k * (1 - ss(t1 - 0.06, t1, t)); g.translate(360, 912); g.scale(pop, pop); g.translate(-360, -912);
    g.fillStyle = 'rgba(237,230,214,0.88)'; g.beginPath(); g.roundRect(60, 876, 600, 70, 14); g.fill();
    words(g, a, 360, 926, 54, 570); g.restore(); }
}
function counterBox(g, t) {
  let label = null, val = '', col = RED;
  if (t < K.wipe1) { label = 'ENEMIES'; val = '1000'; }
  else if (t >= K.surround && t < K.growlBack) { label = 'DOGS'; val = String(Math.round(1000 * eout(clamp((t - K.surround) / 0.7)))); col = INK; }
  else if (t >= K.growlBack && t < K.wipe2) { label = 'ENEMIES'; val = '1000'; }
  else if (t >= K.tails && t < K.same) { label = 'FRIENDS'; val = String(Math.round(1000 * eout(clamp((t - K.tails) / 0.7)))); }
  if (!label) return;
  const flash = t >= K.growlBack && t < K.growlBack + 0.4 ? 1 : 0;
  g.save(); const x = 240, y = 208, w = 240, h = 58; g.translate(360, y + h / 2); const p = 1 + 0.1 * flash; g.scale(p, p); g.translate(-360, -(y + h / 2));
  g.fillStyle = 'rgba(251,247,238,0.95)'; g.beginPath(); g.roundRect(x, y, w, h, 12); g.fill();
  inkLine(g, [[x, y + 6], [x, y + h - 6], [x + 6, y + h], [x + w - 6, y + h], [x + w, y + h - 6], [x + w, y + 6], [x + w - 6, y], [x + 6, y], [x, y + 6]], 3);
  g.font = '26px "Patrick Hand SC"'; g.textAlign = 'left'; g.fillStyle = INK; g.fillText(label, x + 18, y + 38);
  g.font = '36px "Permanent Marker"'; g.textAlign = 'right'; g.fillStyle = col; g.fillText(val, x + w - 16, y + 44); g.restore();
}
function bigLines(g, t) { // hook title, rule, CTA
  g.textBaseline = 'alphabetic';
  if (t < K.wipe1 - 0.05) { const p = 1 + 0.12 * Math.exp(-t * 8); g.save(); g.translate(360, 300); g.scale(p, p); g.translate(-360, -300);
    g.fillStyle = 'rgba(237,230,214,0.88)'; g.beginPath(); g.roundRect(60, 262, 600, 118, 16); g.fill();
    words(g, [['HE FOUGHT ', INK], ['1,000 DOGS.', RED]], 360, 318, 64, 580);
    const k2 = ss(2.55, 2.75, t); if (k2 > 0) { g.globalAlpha = k2; words(g, [['ONLY ONE WAS ', INK], ['REAL.', RED]], 360, 368, 50, 540); } g.restore(); }
  if (t >= K.mirrorW && t < K.cta - 0.2) { const k1 = ss(K.mirrorW, K.mirrorW + 0.2, t), k2 = ss(K.barking, K.barking + 0.2, t);
    g.save(); g.fillStyle = 'rgba(237,230,214,0.9)'; g.beginPath(); g.roundRect(56, 868, 608, 106, 14); g.fill(); g.globalAlpha = k1; words(g, [['THE WORLD IS A ', INK], ['MIRROR.', RED]], 360, 910, 50, 580);
    g.globalAlpha = k2; words(g, [['WALK IN BARKING, ', INK], ['IT BARKS BACK.', RED]], 360, 960, 44, 580); g.restore(); }
  if (t >= K.cta) { const k = ss(K.cta + 0.1, K.cta + 0.4, t); g.save(); g.globalAlpha = k;
    words(g, [['SEND THIS TO SOMEONE', INK]], 360, 500, 54, 580); words(g, [['ALWAYS ', INK], ['READY FOR A FIGHT.', RED]], 360, 562, 54, 580); g.restore(); }
}

// ======================= camera =======================
function cam(t) { // [zoom, cx, cy, shake]  punch-ins, whips and hard cuts for variety
  const HEAD = [470, 690];
  if (t < K.wipe1) {
    // frame 0: tight on the snarling face, whip out to the hall by 0.6 s; 1.55-2.4 s hard cut to a snarling reflection; back wide
    if (t < 0.6) { const k = eio(clamp(t / 0.6)); return [lerp(2.7, 1.14, k), lerp(HEAD[0], 360, k), lerp(HEAD[1], 700, k), 4 * (1 - k)]; }
    if (t >= 1.55 && t < 2.45) { const k = clamp((t - 1.55) / 0.9); return [lerp(1.9, 2.1, k), 582, 640, 2 * Math.exp(-(t - 1.55) * 8)]; }
    return [1.14 + 0.04 * eout(clamp((t - 0.6) / 3)), 360, 700, 3 * Math.exp(-((t + 0.12) * 1.5 % 1) * 9)];
  }
  if (t < K.reveal) return [1, 360, 640, 0];
  if (t < K.enter) { const k = eout(clamp((t - K.reveal) / 0.6)); return [lerp(2.6, 1.05, k), 360, lerp(600, 680, k), 0]; }
  if (t < K.surround) { const hx = heroState(t).o.x; return [1.35, clamp(hx + 60, 240, 480), 720, 0]; } // tracking the stray as he walks in
  if (t < K.growl) { const k = eout(clamp((t - K.surround) / 0.35)); return [lerp(1.35, 1.05, k), lerp(390, 360, k), lerp(720, 680, k), 5 * Math.exp(-(t - K.surround) * 7)]; }
  if (t < K.growlBack) { const k = eout(clamp((t - K.growl) / 0.3)); return [lerp(1.05, 1.5, k), lerp(360, 430, k), lerp(680, 700, k), 0]; } // punch in on his growl
  if (t < K.teeth) { const k = eout(clamp((t - K.growlBack) / 0.25)); return [lerp(1.9, 1.08, k), 360, 650, 4 * Math.exp(-(t - K.growlBack) * 6)]; } // whip out: the hall answers
  if (t < K.thousandMouths) { const k = eio(ss(K.teeth, K.teeth + 0.4, t)); return [lerp(1.13, 2.3, k), lerp(360, 480, k), lerp(700, 690, k), 0]; }
  if (t < K.attack) { const k = eio(ss(K.thousandMouths, K.thousandMouths + 0.35, t)); return [lerp(2.3, 1.0, k), lerp(480, 360, k), lerp(690, 640, k), 0]; }
  if (t < K.wipe2) { // fight: a hard cut to a new angle on every lunge, shake on impact
    const fast = t > K.night ? 2.6 : 1.5, ph = (t - K.attack) * fast, n = Math.floor(ph), c = ph % 1;
    const A = [[1.1, 360, 680], [1.75, 560, 640], [1.5, 430, 700], [1.3, 250, 660]][n % 4];
    if (t >= K.dropped - 0.3) { const k = eout(clamp((t - K.dropped + 0.3) / 0.8)); return [lerp(1.1, 1.3, k), 360, lerp(680, 760, k), 0]; }
    return [A[0] + 0.05 * (c > 0.25 ? Math.exp(-(c - 0.25) * 6) : 0), A[1], A[2], c > 0.22 && c < 0.5 ? 7 : 0];
  }
  if (t < K.wag) { const sx = sheState(t).o.x; return [1.3, clamp(sx + 40, 240, 480), 720, 0]; }
  if (t < K.tails) { const k = eout(clamp((t - K.wag) / 0.4)); return [lerp(1.3, 1.5, k), lerp(370, 420, k), 700, 0]; }
  if (t < K.same) { const k = eout(clamp((t - K.tails) / 0.35)); return [lerp(1.5, 1.04, k), lerp(420, 360, k), lerp(700, 660, k), 3 * Math.exp(-(t - K.tails) * 7)]; }
  if (t < K.world) return [lerp(1.0, 1.06, ss(K.same, K.world, t)), 360, 640, 0];
  if (t < K.name) { const k = eout(clamp((t - K.world) / 0.3)); return [lerp(1.06, 1.18, k), 360, 640, 0]; }
  if (t < K.seeing) return [1.0 + 0.05 * ss(K.name, K.seeing, t), 300, 660, 0];
  if (t < K.wipe3) { const k = eout(clamp((t - K.seeing) / 0.3)); return [lerp(1.05, 1.3, k), lerp(300, 250, k), lerp(660, 600, k), 0]; }
  if (t < K.cold) return [1.0 + 0.04 * ss(K.everyday, K.cold, t), 360, 640, 0];
  if (t < K.theyCold) { const k = eout(clamp((t - K.cold) / 0.3)); return [lerp(1.04, 1.4, k), lerp(360, 230, k), lerp(640, 620, k), 0]; }
  if (t < K.boss) { const k = eout(clamp((t - K.theyCold) / 0.3)); return [lerp(1.4, 1.3, k), lerp(230, 500, k), 620, 0]; }
  if (t < K.walkIn) return [1.0, 360, 640, 0];
  if (t < K.getOne) return [1.0 + 0.2 * ss(K.walkIn, K.getOne, t), 380, 640, 0];
  if (t < K.most) { const k = eout(clamp((t - K.getOne) / 0.3)); return [lerp(1.45, 1.05, k), 400, 640, 7 * Math.exp(-(t - K.getOne) * 5)]; }
  if (t < K.mirrorW) return [1.0 + 0.1 * ss(K.most, K.mirrorW, t), 360, 600, 0];
  if (t < K.cta) { const k = eout(clamp((t - K.mirrorW) / 0.5)); return [lerp(1.1, 1.0, k), 360, 640, 0]; }
  return [1, 360, 640, 0];
}
function scene(g, t) {
  if (t >= K.wipe1 && t < K.reveal) return tunnelScene(g, t);
  if (t < K.same) return hallScene(g, t);
  if (t < K.name) return splitScene(g, t);
  if (t < K.wipe3 + 0.1) return conceptScene(g, t);
  if (t < K.cta - 0.15) return peopleScene(g, t);
  return ctaScene(g, t);
}
function frame(g, t) {
  T = t;
  const [z, cx, cy, sh] = cam(t);
  g.setTransform(W / DW, 0, 0, H / DH, 0, 0); g.translate(360, 640); g.scale(z, z); g.translate(-cx + Math.sin(t * 61) * sh, -cy + Math.cos(t * 47) * sh);
  scene(g, t);
  g.setTransform(W / DW, 0, 0, H / DH, 0, 0);
  // red pulse at the frame edges during the fight (light red, never a dark border)
  const hostile = t < K.wipe1 ? 1 : (t >= K.growlBack && t < K.dropped) ? 1 : 0;
  if (hostile) { const p = 0.5 + 0.5 * Math.sin(t * 9); const gr = g.createRadialGradient(360, 640, 420, 360, 640, 900); gr.addColorStop(0, 'rgba(200,40,42,0)'); gr.addColorStop(1, `rgba(200,40,42,${0.1 + 0.1 * p})`); g.fillStyle = gr; g.fillRect(0, 0, DW, DH); }
  const gr = g.createRadialGradient(360, 640, 380, 360, 640, 900); gr.addColorStop(0, 'rgba(120,95,60,0)'); gr.addColorStop(1, 'rgba(120,95,60,0.14)'); g.fillStyle = gr; g.fillRect(0, 0, DW, DH);
  if (t >= K.reveal && t < K.reveal + 0.18) { g.fillStyle = `rgba(255,252,244,${0.85 * (1 - (t - K.reveal) / 0.18)})`; g.fillRect(0, 0, DW, DH); }
  counterBox(g, t); caption(g, t); bigLines(g, t);
  for (const [w0, d] of WIPES) inkWipe(g, (t - w0) / d);
}
window.renderAt = (t, sub = 1) => {
  sub = Math.max(1, sub | 0);
  if (sub === 1) frame(out, t);
  else { out.setTransform(1, 0, 0, 1, 0, 0); out.fillStyle = '#000'; out.fillRect(0, 0, W, H);
    for (let i = 0; i < sub; i++) { A.setTransform(1, 0, 0, 1, 0, 0); frame(A, t + (i / sub - 0.5) * (1 / 30) * 0.5); out.setTransform(1, 0, 0, 1, 0, 0); out.globalCompositeOperation = 'lighter'; out.globalAlpha = 1 / sub; out.drawImage(acc, 0, 0); }
    out.globalCompositeOperation = 'source-over'; out.globalAlpha = 1; }
  return cv.toDataURL('image/jpeg', 0.92);
};
// ======================= sound cues (no SFX in the hook 0-3 s or after the rule line) =======================
window.events = (() => { const e = [];
  e.push({ t: K.wipe1 - 0.15, s: 'swipe', g: 0.5, pan: 0 });
  e.push({ t: K.mirrorsWord - 0.1, s: 'pop', g: 0.45, pan: 0 }, { t: K.reveal - 0.1, s: 'swipe', g: 0.45, pan: 0, rate: 0.8 });
  for (let i = 0; i < 4; i++) e.push({ t: K.enter + 0.2 + i * 0.29, s: 'paws', g: 0.35, pan: -0.3 + i * 0.1 });
  e.push({ t: K.surround - 0.05, s: 'pop', g: 0.7, pan: 0 });
  e.push({ t: K.growl, s: 'growl', g: 0.8, pan: 0 }, { t: K.growlBack - 0.05, s: 'growls', g: 0.9, pan: 0 });
  e.push({ t: K.thousandMouths - 0.05, s: 'snarls', g: 0.9, pan: 0 });
  for (let tt = K.attack; tt < K.dropped - 0.3; ) { const fast = tt > K.night ? 2.6 : 1.5; e.push({ t: tt + 0.22 / fast, s: 'glass', g: 0.75, pan: 0.3, rate: 0.95 + 0.1 * hash(tt) }, { t: tt + 0.05, s: 'bark', g: 0.65, pan: -0.1, rate: 0.95 + 0.1 * hash(tt * 3) }); tt += 1 / fast; }
  e.push({ t: K.night - 0.1, s: 'clock', g: 0.45, pan: -0.4 });
  e.push({ t: K.dropped, s: 'thud', g: 0.8, pan: 0 }, { t: K.dropped + 0.1, s: 'whimper', g: 0.5, pan: 0 });
  e.push({ t: K.wipe2 - 0.1, s: 'swipe', g: 0.5, pan: 0 }, { t: K.morning + 0.1, s: 'birds', g: 0.35, pan: 0.3 });
  for (let i = 0; i < 4; i++) e.push({ t: K.morning + 0.3 + i * 0.3, s: 'paws', g: 0.3, pan: -0.3 + i * 0.1 });
  e.push({ t: K.wag, s: 'wag', g: 0.5, pan: 0 }, { t: K.tails, s: 'chime', g: 0.6, pan: 0 });
  e.push({ t: K.bias - 0.1, s: 'marker', g: 0.5, pan: 0 });
  e.push({ t: K.wipe3 - 0.1, s: 'swipe', g: 0.5, pan: 0 });
  e.push({ t: K.friend, s: 'ding', g: 0.55, pan: 0.2 }, { t: K.cold, s: 'frost', g: 0.45, pan: 0 });
  e.push({ t: K.boss, s: 'ding', g: 0.5, pan: 0.3, rate: 0.85 }, { t: K.getOne, s: 'boom', g: 0.7, pan: 0 });
  return e.sort((a, b) => a.t - b.t); })();
window.TL = K; window.DUR = DUR;
document.fonts.load('40px "Patrick Hand SC"').then(() => document.fonts.load('40px "Permanent Marker"')).then(() => { window.ready = true; });
