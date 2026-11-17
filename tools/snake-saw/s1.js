// The Snake and the Saw - Slow Light parable reel, paper-ink look (cream paper, black ink line art, one red accent).
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
const INK = '#1e1916', PAPER = '#ede6d6', FILL = '#fbf7ee', SHADE = '#ddd3c2', RED = '#c8282a', REDL = '#e05a4c';
const SNAKE = '#e6cf8f', SNAKE_D = '#cdb06a', STEEL = '#dfe3e2', WOOD = '#c9ae86', WOOD_D = '#a98a62';
const BOIL = () => Math.floor(T * 8);
function jit(x, y, a = 0.9) { const b = BOIL(); return [x + (hash(x * 0.13 + y * 0.71 + b * 3.3) - 0.5) * a * 2, y + (hash(x * 0.57 + y * 0.29 + b * 1.7) - 0.5) * a * 2]; }

// ---------- paper + ink ----------
function paper(g) {
  g.fillStyle = PAPER; g.fillRect(-400, -400, DW + 800, DH + 800);
  if (!window._paper) { const c = document.createElement('canvas'); c.width = c.height = 512; const x = c.getContext('2d'); const im = x.createImageData(512, 512);
    for (let p = 0; p < im.data.length; p += 4) { const v = 128 + (Math.random() - 0.5) * 60; im.data[p] = im.data[p + 1] = im.data[p + 2] = v; im.data[p + 3] = 255; } x.putImageData(im, 0, 0);
    x.globalAlpha = 0.08; for (let i = 0; i < 400; i++) { x.strokeStyle = Math.random() < 0.5 ? '#000' : '#fff'; x.lineWidth = 0.6; x.beginPath(); const a = Math.random() * 512, b = Math.random() * 512; x.moveTo(a, b); x.lineTo(a + (Math.random() - 0.5) * 30, b + (Math.random() - 0.5) * 30); x.stroke(); } window._paper = c; }
  g.save(); g.globalAlpha = 0.1; g.globalCompositeOperation = 'multiply'; g.fillStyle = g.createPattern(window._paper, 'repeat'); g.fillRect(-400, -400, DW + 800, DH + 800); g.restore();
}
function inkLine(g, pts, w, col = INK) { g.strokeStyle = col; g.lineWidth = w; g.lineCap = 'round'; g.lineJoin = 'round'; g.beginPath(); pts.forEach((p, i) => { const q = jit(p[0], p[1], 0.7); i ? g.lineTo(q[0], q[1]) : g.moveTo(q[0], q[1]); }); g.stroke(); }
function inkShape(g, pts, fill, w = 3) { g.beginPath(); pts.forEach((p, i) => { const q = jit(p[0], p[1], 0.6); i ? g.lineTo(q[0], q[1]) : g.moveTo(q[0], q[1]); }); g.closePath(); if (fill) { g.fillStyle = fill; g.fill(); } g.strokeStyle = INK; g.lineWidth = w; g.lineJoin = 'round'; g.stroke(); }
function blob(g, x, y, rx, ry, fill, w = 3, rot = 0) { const c = jit(x, y, 0.5); g.beginPath(); g.ellipse(c[0], c[1], rx, ry, rot, 0, 7); if (fill) { g.fillStyle = fill; g.fill(); } if (w) { g.strokeStyle = INK; g.lineWidth = w; g.stroke(); } }

// ---------- workshop ----------
const FLOOR = 880;
const SAW = { tip: 250, heel: 575, topTip: 752, botTip: 800, topHeel: 726, botHeel: 814 };
const sawTop = x => lerp(SAW.topTip, SAW.topHeel, clamp((x - SAW.tip) / (SAW.heel - SAW.tip)));
const sawBot = x => lerp(SAW.botTip, SAW.botHeel, clamp((x - SAW.tip) / (SAW.heel - SAW.tip)));
function workshop(g, opt = {}) {
  paper(g);
  // plank wall
  for (let i = 0; i < 12; i++) { const x = -40 + i * 74 + (hash(i) - 0.5) * 8; inkLine(g, [[x, -60], [x + 2, FLOOR - 4]], 1.1, 'rgba(30,25,22,0.16)'); }
  for (let i = 0; i < 9; i++) { const x = hash(i * 3) * 720, y = 120 + hash(i * 7) * 600; blob(g, x, y, 3, 2, 'rgba(30,25,22,0.14)', 0); }
  if (!opt.bare) {
    // pegboard tools (very light)
    g.save(); g.globalAlpha = 0.42;
    inkLine(g, [[60, 380], [660, 380]], 2.4); for (const x of [120, 260, 420, 560]) inkLine(g, [[x, 372], [x, 392]], 3);
    inkShape(g, [[108, 392], [132, 392], [132, 520], [108, 520]], WOOD, 2.4); inkShape(g, [[84, 392], [156, 392], [156, 420], [84, 420]], STEEL, 2.4); // hammer
    inkLine(g, [[260, 392], [260, 540]], 5); blob(g, 260, 548, 13, 13, STEEL, 2.4); // wrench-ish
    inkShape(g, [[410, 392], [430, 392], [436, 470], [404, 470]], WOOD, 2.4); inkShape(g, [[412, 470], [428, 470], [424, 540], [416, 540]], STEEL, 2.2); // chisel
    g.beginPath(); g.arc(560, 452, 46, Math.PI * 1.15, Math.PI * 1.85); g.strokeStyle = INK; g.lineWidth = 4; g.stroke(); inkLine(g, [[528, 418], [528, 470]], 3); // coil of rope / clamp
    g.restore();
  }
  // floor
  inkLine(g, [[-60, FLOOR + 1], [780, FLOOR - 1]], 3.5);
  for (let i = 1, d = 30; i < 7; i++, d *= 1.45) inkLine(g, [[-60, FLOOR + d], [780, FLOOR + d]], 1.1, 'rgba(30,25,22,0.18)');
  // wood shavings
  for (let i = 0; i < 7; i++) { const x = 40 + hash(i * 11) * 640, y = FLOOR + 24 + hash(i * 5) * 140; g.save(); g.strokeStyle = 'rgba(30,25,22,0.45)'; g.lineWidth = 2; g.beginPath(); g.arc(x, y, 8 + hash(i) * 6, 0.3, 4.6); g.stroke(); g.restore(); }
}
function stump(g) { // the handle rests on a stump at the right
  const x0 = 545, x1 = 705, top = 822;
  inkShape(g, [[x0 + 6, top], [x0, FLOOR + 2], [x1, FLOOR + 2], [x1 - 6, top]], WOOD, 3.2);
  for (let i = 0; i < 4; i++) inkLine(g, [[x0 + 30 + i * 32, top + 14], [x0 + 26 + i * 33, FLOOR - 6]], 1.4, 'rgba(30,25,22,0.4)');
  blob(g, (x0 + x1) / 2, top, (x1 - x0) / 2 - 4, 14, '#dcc39b', 3.2);
  g.save(); g.strokeStyle = 'rgba(30,25,22,0.45)'; g.lineWidth = 1.4; for (const r of [0.25, 0.5, 0.75]) { g.beginPath(); g.ellipse((x0 + x1) / 2, top, ((x1 - x0) / 2 - 4) * r, 14 * r, 0, 0, 7); g.stroke(); } g.restore();
}
function drawSaw(g, opt = {}) {
  const { tip, heel, topTip, botTip, topHeel, botHeel } = SAW;
  // blade
  const pts = [[tip, topTip], [heel, topHeel]];
  pts.push([heel, botHeel]);
  const n = 30; for (let i = 0; i <= n; i++) { const x = lerp(heel, tip, i / n), y = sawBot(x); pts.push([x, y + (i % 2 ? 0 : 8)]); }
  inkShape(g, pts, STEEL, 3);
  // sheen + steel line
  g.save(); g.strokeStyle = 'rgba(255,255,255,0.9)'; g.lineWidth = 5; g.lineCap = 'round'; g.beginPath(); g.moveTo(tip + 40, topTip + 12); g.lineTo(heel - 60, topHeel + 12); g.stroke(); g.restore();
  inkLine(g, [[tip + 14, topTip + 32], [heel - 20, topHeel + 52]], 1.2, 'rgba(30,25,22,0.35)');
  // handle
  const hx = heel - 6;
  inkShape(g, [[hx, topHeel - 10], [hx + 60, topHeel - 30], [hx + 118, topHeel - 18], [hx + 132, topHeel + 30], [hx + 110, botHeel + 6], [hx + 40, botHeel + 12], [hx, botHeel + 4]], WOOD, 3.4);
  inkShape(g, [[hx + 40, topHeel + 6], [hx + 92, topHeel - 4], [hx + 104, topHeel + 28], [hx + 82, botHeel - 16], [hx + 46, botHeel - 12]], PAPER, 2.8);
  for (const [x, y] of [[hx + 18, topHeel + 10], [hx + 20, botHeel - 16]]) blob(g, x, y, 5, 5, '#e8b84a', 2);
  if (opt.label) { /* none */ }
}
// red nick spots on the blade (blood on the teeth)
function sawBlood(g, k) { if (k <= 0) return; g.save(); g.fillStyle = RED; for (let i = 0; i < 12; i++) { const x = lerp(SAW.tip + 20, SAW.heel - 40, hash(i * 3.7)); if (hash(i * 9) > k) continue; const y = sawBot(x) + 2; g.beginPath(); g.ellipse(x, y, 4, 6, 0, 0, 7); g.fill(); } g.restore(); }

// ---------- snake ----------
const SN = 64;
function sRad(i) { const u = i / (SN - 1); return 17 * (0.78 + 0.22 * Math.sin(Math.min(u * 4, 1) * Math.PI / 2)) * (1 - 0.86 * ss(0.45, 1, u)); }
function nrm(pts, i) { const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)]; const dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1; return [-dy / l, dx / l, dx / l, dy / l]; }
// draw spine range [i0,i1] as one chunk: ink pass then fill pass then markings
function snakeChunk(g, pts, i0, i1, o) {
  const sc = o.s || 1; g.lineCap = 'round'; g.lineJoin = 'round';
  for (const pass of [0, 1]) {
    g.strokeStyle = pass ? (o.fill || SNAKE) : INK;
    for (let i = i0; i < i1; i++) { const r = sRad(i) * sc; g.lineWidth = pass ? r * 2 : r * 2 + 7 * sc; g.beginPath(); g.moveTo(pts[i][0], pts[i][1]); g.lineTo(pts[i + 1][0], pts[i + 1][1]); g.stroke(); }
  }
  // belly stripe (lighter) on the lower side + chevron bands
  for (let i = Math.max(i0, 3); i < i1; i += 3) {
    const [nx, ny, dx, dy] = nrm(pts, i), r = sRad(i) * sc, p = pts[i]; const f = ny < 0 ? -1 : 1; // f: normal pointing down-ish
    g.strokeStyle = SNAKE_D; g.lineWidth = 3.4 * sc; g.beginPath(); g.moveTo(p[0] - nx * r * 0.75 * f + dx * 3, p[1] - ny * r * 0.75 * f + dy * 3); g.lineTo(p[0] - dx * 5 * sc, p[1] - dy * 5 * sc); g.lineTo(p[0] + nx * r * 0.75 * f + dx * 3, p[1] + ny * r * 0.75 * f + dy * 3); g.stroke();
    if (i % 6 === 0) { g.strokeStyle = 'rgba(30,25,22,0.55)'; g.lineWidth = 1.8 * sc; g.beginPath(); g.moveTo(p[0] - nx * r * 0.8 * f + dx * 3, p[1] - ny * r * 0.8 * f + dy * 3); g.lineTo(p[0] - dx * 5 * sc, p[1] - dy * 5 * sc); g.lineTo(p[0] + nx * r * 0.8 * f + dx * 3, p[1] + ny * r * 0.8 * f + dy * 3); g.stroke(); }
  }
  // cuts
  if (o.cuts) for (const c of o.cuts) { if (c.i < i0 || c.i >= i1) continue; const [nx, ny, dx, dy] = nrm(pts, c.i), r = sRad(c.i) * sc, p = pts[c.i];
    const L = r * 0.9 * c.k; g.strokeStyle = RED; g.lineWidth = 3.6 * sc; g.beginPath(); g.moveTo(p[0] - nx * L + dx * 4, p[1] - ny * L + dy * 4); g.lineTo(p[0] + nx * L - dx * 4, p[1] + ny * L - dy * 4); g.stroke();
    if (c.drip) { g.fillStyle = RED; const by = p[1] + Math.abs(ny) * r; g.beginPath(); g.ellipse(p[0] + 2, by + 4 + 4 * c.drip, 2.6 * sc, 4 * sc, 0, 0, 7); g.fill(); } }
}
// head: o.mood 'calm'|'alert'|'angry'|'dead', o.mouth 0..1, o.tongue 0..1, o.bite (teeth closed on something)
function snakeHead(g, pts, o) {
  const sc = (o.s || 1) * (o.headS || 1), p = pts[0], q = pts[3]; let a = Math.atan2(p[1] - q[1], p[0] - q[0]); if (o.headA != null) a = o.headA;
  const flip = Math.cos(a) < 0 ? -1 : 1;
  g.save(); const c = jit(p[0], p[1], 0.5); g.translate(c[0], c[1]); g.rotate(a); g.scale(sc, sc * flip);
  const m = o.mouth || 0, ja = m * 0.75;
  // tongue
  if ((o.tongue || 0) > 0 && m < 0.3) { const L = 26 * o.tongue, w = Math.sin(T * 30) * 3; g.strokeStyle = RED; g.lineWidth = 3; g.lineCap = 'round'; g.beginPath(); g.moveTo(30, 6); g.lineTo(30 + L, 6 + w); g.lineTo(38 + L, 1 + w); g.moveTo(30 + L, 6 + w); g.lineTo(38 + L, 11 + w); g.stroke(); }
  // lower jaw (behind)
  g.save(); g.translate(-12, 6); g.rotate(ja); g.fillStyle = INK; g.beginPath(); g.ellipse(22, 3, 28, 9.5, 0.04, 0, 7); g.fill(); g.fillStyle = o.fill || SNAKE; g.beginPath(); g.ellipse(22, 3, 24.5, 6, 0.04, 0, 7); g.fill();
  if (m > 0.1) { g.fillStyle = '#fff'; g.strokeStyle = INK; g.lineWidth = 1.4; for (const x of [40]) { g.beginPath(); g.moveTo(x - 4, -2); g.lineTo(x, -11 * m); g.lineTo(x + 3, -2); g.closePath(); g.fill(); g.stroke(); } }
  g.restore();
  // mouth inside
  if (m > 0.05) { g.fillStyle = RED; g.beginPath(); g.moveTo(-10, 4); g.lineTo(44, 2); g.lineTo(-12 + Math.cos(ja) * 54, 6 + Math.sin(ja) * 54); g.closePath(); g.fill(); g.strokeStyle = INK; g.lineWidth = 2; g.stroke(); }
  // head
  g.fillStyle = INK; g.beginPath(); g.ellipse(8, -2, 34, 21, 0, 0, 7); g.fill();
  g.fillStyle = o.fill || SNAKE; g.beginPath(); g.ellipse(8, -2, 30.5, 17.5, 0, 0, 7); g.fill();
  g.fillStyle = SNAKE_D; g.beginPath(); g.ellipse(4, -10, 18, 6, -0.1, 0, 7); g.fill();
  // fangs (upper)
  if (m > 0.1) { g.fillStyle = '#fff'; g.strokeStyle = INK; g.lineWidth = 1.6; for (const x of [28, 18]) { g.beginPath(); g.moveTo(x - 4, 12); g.lineTo(x, 12 + 15 * m); g.lineTo(x + 4, 12); g.closePath(); g.fill(); g.stroke(); } }
  // nostril
  g.fillStyle = INK; g.beginPath(); g.ellipse(34, -6, 2.4, 1.8, 0, 0, 7); g.fill();
  // eye
  const mood = o.mood || 'calm';
  if (mood === 'dead') { g.strokeStyle = INK; g.lineWidth = 3.2; g.lineCap = 'round'; g.beginPath(); g.moveTo(6, -14); g.lineTo(16, -4); g.moveTo(16, -14); g.lineTo(6, -4); g.stroke(); }
  else {
    const er = mood === 'alert' ? 8 : 7; g.fillStyle = '#fff'; g.strokeStyle = INK; g.lineWidth = 2.4; g.beginPath(); g.arc(11, -9, er, 0, 7); g.fill(); g.stroke();
    g.fillStyle = mood === 'angry' ? RED : INK; g.beginPath(); g.ellipse(13, -9, mood === 'alert' ? 2.4 : 1.8, 5, 0, 0, 7); g.fill();
    if (mood === 'angry') { g.strokeStyle = INK; g.lineWidth = 4.2; g.lineCap = 'round'; g.beginPath(); g.moveTo(0, -22); g.lineTo(22, -12); g.stroke(); }
  }
  g.restore();
}
// slither spine: head at (hx, hy-ish) moving +x along the floor, body trailing to the left, hump wave
function groundSpine(hx, t, o = {}) {
  const P = [], seg = 9.2, A = o.amp ?? 9, lift = o.lift ?? 26, w = o.wave ?? 9, base = o.base ?? FLOOR;
  for (let i = 0; i < SN; i++) {
    const s = i * seg; const env = clamp(i / 7);
    let x = hx - s * 0.985, y = base - sRad(i) - 2 - A * env * (0.5 + 0.5 * Math.sin(s * 0.055 - t * w));
    if (i < 9) { const k = (1 - i / 9); y -= lift * k * k; x += (o.rear || 0) * k * k * -30; y -= (o.rear || 0) * k * k * 70; }
    P.push([x, y]);
  }
  return P;
}
// coil spine around the saw blade: head above the tip, helix from x0 to x1, tail down to the floor going left
function coilSpine(t, R, o = {}) {
  const P = [], x0 = 312, x1 = 520, turns = 3, nNeck = 9, nHel = 40, nTail = SN - nNeck - nHel;
  const head = o.head || [238, 690];
  const hs = [];
  for (let j = 0; j < nHel; j++) { const u = j / (nHel - 1), phi = u * turns * Math.PI * 2 + 0.2; const x = lerp(x0, x1, u), cy = (sawTop(x) + sawBot(x)) / 2; const shiver = (o.shiver || 0) * Math.sin(t * 40 + j) * 1.5;
    hs.push([x - 0.28 * R * Math.sin(phi), cy - (R + shiver) * Math.cos(phi), Math.sin(phi)]); }
  const h0 = hs[0];
  for (let i = 0; i < nNeck; i++) { const k = i / nNeck; const e = eio(k); P.push([lerp(head[0], h0[0], e) + Math.sin(k * Math.PI) * -20, lerp(head[1], h0[1], k) - Math.sin(k * Math.PI) * 26]); }
  for (const p of hs) P.push([p[0], p[1]]);
  const hl = hs[hs.length - 1];
  for (let i = 1; i <= nTail; i++) { const k = i / nTail; P.push([lerp(hl[0], 300, eio(k)) + Math.sin(k * 3) * 10, lerp(hl[1], FLOOR - 8, ss(0, 0.35, k)) - 2 * Math.sin(k * 9)]); }
  P.depth = hs.map(p => p[2]); P.nNeck = nNeck; P.nHel = nHel;
  return P;
}
function lerpSpine(a, b, k) { const P = a.map((p, i) => [lerp(p[0], b[i][0], k), lerp(p[1], b[i][1], k)]); P.depth = b.depth; P.nNeck = b.nNeck; P.nHel = b.nHel; return P; }
// draw a coiled snake + saw in the right order: back strands, blade, front strands, head
function coilDraw(g, P, o, sawFn) {
  const n0 = P.nNeck, d = P.depth; const chunks = []; let s = n0, cur = d[0] > 0;
  for (let j = 1; j < d.length; j++) { const f = d[j] > 0; if (f !== cur) { chunks.push([s, n0 + j, cur]); s = n0 + j; cur = f; } }
  chunks.push([s, n0 + d.length - 1, cur]);
  // tail (behind blade? it hangs down at the back-right then lies on floor in front) -> draw first
  snakeChunk(g, P, n0 + d.length - 1, SN - 1, o);
  for (const c of chunks) if (!c[2]) snakeChunk(g, P, Math.max(0, c[0] - 1), c[1], o);
  sawFn();
  for (const c of chunks) if (c[2]) snakeChunk(g, P, c[0], Math.min(SN - 1, c[1] + 1), o);
  snakeChunk(g, P, 0, n0 + 1, o);
  snakeHead(g, P, o);
}

// ---------- horse + bat ----------
// gallop rig, local px facing +x, ground y = 0
function horseLegs(ph, mode, k) { // returns 4 legs [shoulder, knee, hoof], order: farBack, farFront, nearBack, nearFront
  const L = [];
  const base = [[-62, 0.0], [58, 0.55], [-48, 0.12], [72, 0.68]];
  for (const [bx, off] of base) {
    const sh = [bx, -128]; let hoof, knee;
    if (mode === 'down') { knee = [bx + 42, -90]; hoof = [bx + 88, -80]; }
    else { const a = (ph + off) * Math.PI * 2, run = k; const hx = bx + Math.cos(a) * 46 * run, lift = Math.max(0, Math.sin(a)) * 40 * run; hoof = [hx, -lift]; const front = bx > 0 ? 1 : -1; knee = [(sh[0] + hoof[0]) / 2 + front * (8 + 18 * Math.max(0, Math.sin(a)) * run) * (bx > 0 ? 1 : -1) * -1, (sh[1] + hoof[1]) / 2 - 4]; }
    L.push([sh, knee, hoof]);
  }
  return L;
}
function drawHorse(g, o) { // o: x, y, s, ph (gallop phase), run 0..1, mode 'stand'|'run'|'rear'|'down', panic 0..1
  const s = o.s; g.save(); const c = jit(o.x, o.y, 0.4); g.translate(c[0], c[1]); g.scale(s * (o.dir || 1), s);
  let rot = 0, lift = 0; const mode = o.mode || 'stand';
  if (mode === 'run') { lift = Math.abs(Math.sin(o.ph * Math.PI * 2)) * 10 * o.run; rot = Math.sin(o.ph * Math.PI * 2) * 0.05 * o.run; }
  if (mode === 'rear') { rot = -0.42 * o.rear; }
  if (mode === 'down') { lift = -74 * o.down; rot = 0.06 * o.down; }
  g.translate(-60, -lift); g.rotate(rot); g.translate(60, 0);
  const legs = horseLegs(o.ph || 0, mode === 'down' ? 'down' : 'gallop', mode === 'run' ? o.run : mode === 'rear' ? 0.6 : 0);
  if (mode === 'down') { const st = horseLegs(0, 'gallop', 0); for (let i = 0; i < 4; i++) for (let j = 0; j < 3; j++) legs[i][j] = [lerp(st[i][j][0], legs[i][j][0], o.down), lerp(st[i][j][1], legs[i][j][1] - (j === 2 ? 74 * (1 - o.down) * 0 : 0), o.down)]; }
  if (mode === 'rear') { for (const i of [1, 3]) { const L = legs[i]; L[1] = [L[0][0] + 34, L[0][1] + 26 + Math.sin(T * 18 + i) * 8]; L[2] = [L[0][0] + 22, L[0][1] + 66 + Math.sin(T * 18 + i) * 10]; } }
  const fillH = '#ecd9b4', shadeH = '#d9c193';
  const leg = (L, col) => { for (const pass of [0, 1]) { g.strokeStyle = pass ? col : INK; g.lineCap = 'round'; g.lineJoin = 'round'; g.lineWidth = pass ? 15 : 22; g.beginPath(); g.moveTo(L[0][0], L[0][1]); g.lineTo(L[1][0], L[1][1]); g.lineTo(L[2][0], L[2][1]); g.stroke(); } g.fillStyle = INK; g.beginPath(); g.roundRect(L[2][0] - 10, L[2][1] - 9, 20, 11, 3); g.fill(); };
  leg(legs[0], shadeH); leg(legs[1], shadeH);
  // tail
  const tw = Math.sin(T * 14) * 10 * (o.run || 0.2);
  for (let i = 0; i < 5; i++) inkLine(g, [[-96, -150], [-130 - i * 4, -120 + tw * 0.5], [-142 - i * 6 + tw, -60 + i * 6]], 4, INK);
  // body
  g.fillStyle = INK; g.beginPath(); g.ellipse(0, -150, 102, 52, 0, 0, 7); g.fill(); g.fillStyle = fillH; g.beginPath(); g.ellipse(0, -150, 97, 47, 0, 0, 7); g.fill();
  leg(legs[2], fillH); leg(legs[3], fillH);
  g.fillStyle = INK; g.beginPath(); g.ellipse(0, -150, 102, 52, 0, 0, 7); g.globalAlpha = 0; g.fill(); g.globalAlpha = 1;
  // re-cover body top over near legs' tops
  g.fillStyle = fillH; g.beginPath(); g.ellipse(0, -156, 94, 40, 0, 0, 7); g.fill();
  // neck + head (one group that pivots at the withers)
  const hr = mode === 'rear' ? -0.35 * o.rear : mode === 'down' ? 0.85 * o.down : mode === 'run' ? 0.08 * Math.sin(o.ph * Math.PI * 2) : 0;
  g.save(); g.translate(60, -170); g.rotate(hr); g.translate(-60, 170);
  for (const pass of [0, 1]) { const e = pass ? 0 : 7; const col = pass ? fillH : INK; g.strokeStyle = col; g.fillStyle = col; g.lineCap = 'round';
    g.lineWidth = 48 + e; g.beginPath(); g.moveTo(52, -168); g.lineTo(112, -258); g.stroke();
    g.lineWidth = 34 + e; g.beginPath(); g.moveTo(122, -258); g.lineTo(166, -214); g.stroke();
    g.beginPath(); g.ellipse(126, -256, 26 + e / 2, 22 + e / 2, 0.6, 0, 7); g.fill(); g.beginPath(); g.ellipse(166, -212, 19 + e / 2, 16 + e / 2, 0.6, 0, 7); g.fill(); }
  // ear
  g.fillStyle = INK; g.beginPath(); g.moveTo(108, -272); g.lineTo(104, -306); g.lineTo(122, -276); g.closePath(); g.fill();
  g.fillStyle = INK; g.beginPath(); g.ellipse(174, -212, 3, 4, 0.6, 0, 7); g.fill(); // nostril
  inkLine(g, [[156, -198], [170, -196]], 2.4); // mouth
  const pn = o.panic || 0;
  if (mode === 'down' && o.down > 0.8) { g.strokeStyle = INK; g.lineWidth = 3; g.lineCap = 'round'; g.beginPath(); g.moveTo(126, -266); g.lineTo(138, -254); g.moveTo(138, -266); g.lineTo(126, -254); g.stroke(); }
  else { g.fillStyle = '#fff'; g.strokeStyle = INK; g.lineWidth = 2.4; g.beginPath(); g.arc(132, -260, 6 + 3 * pn, 0, 7); g.fill(); g.stroke(); g.fillStyle = pn > 0.5 ? RED : INK; g.beginPath(); g.arc(133 + 2 * pn, -260, 2.8, 0, 7); g.fill(); }
  // mane along the back of the neck
  for (let i = 0; i < 7; i++) { const u = i / 6, x = lerp(30, 100, u), y = lerp(-178, -282, u), fl = Math.sin(T * 16 + i) * 6 * (o.run || 0.2); inkLine(g, [[x + 8, y + 6], [x - 14 - fl, y - 4], [x - 24 - fl * 1.5, y + 8]], 4); }
  g.restore();
  g.restore();
}
function drawBat(g, x, y, s, ph) {
  g.save(); g.translate(x, y); g.scale(s, s); const f = Math.sin(ph * Math.PI * 2);
  g.fillStyle = INK; for (const d of [-1, 1]) { g.beginPath(); g.moveTo(0, 0); g.quadraticCurveTo(d * 20, -24 * f - 6, d * 44, -18 * f); g.lineTo(d * 36, -2 * f + 4); g.lineTo(d * 26, -4 * f + 10); g.lineTo(d * 16, 6); g.closePath(); g.fill(); }
  g.beginPath(); g.ellipse(0, 4, 9, 12, 0, 0, 7); g.fill(); g.beginPath(); g.moveTo(-6, -4); g.lineTo(-8, -16); g.lineTo(-1, -7); g.moveTo(6, -4); g.lineTo(8, -16); g.lineTo(1, -7); g.fill();
  g.fillStyle = '#fff'; g.beginPath(); g.arc(-3.5, 1, 1.8, 0, 7); g.arc(3.5, 1, 1.8, 0, 7); g.fill(); g.restore();
}
