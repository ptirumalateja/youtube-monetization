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

function fitFont(g, txt, size, family, maxW) { g.font = `${size}px "${family}"`; const w = g.measureText(txt).width; if (w > maxW) { size *= maxW / w; g.font = `${size}px "${family}"`; } return size; }
function words(g, parts, x, y, size, maxW, fam = 'Patrick Hand SC') { const full = parts.map(p => p[0]).join(''); fitFont(g, full, size, fam, maxW); let w = g.measureText(full).width, cx = x - w / 2;
  g.textAlign = 'left'; for (const [s, c] of parts) { g.fillStyle = c; g.fillText(s, cx, y); cx += g.measureText(s).width; } }
function heart(g, x, y, r, a, col = RED) { if (a <= 0) return; g.save(); g.globalAlpha = a; g.fillStyle = col; g.strokeStyle = INK; g.lineWidth = 3; g.beginPath(); g.moveTo(x, y + r); g.bezierCurveTo(x - r * 1.6, y - r * 0.2, x - r * 0.8, y - r * 1.4, x, y - r * 0.5); g.bezierCurveTo(x + r * 0.8, y - r * 1.4, x + r * 1.6, y - r * 0.2, x, y + r); g.fill(); g.stroke(); g.restore(); }

// ======================= timeline (vo/vo.json, atempo 1.08) =======================
const DUR = 57.27;
const K = {
  wipe1: 2.62, start: 2.75, cut: 3.63, sting: 4.78, decided: 5.54, attacking: 6.34, struck: 8.63, bit: 10.09, cutMouth: 10.83,
  furious: 11.88, wrapped: 12.4, crush: 13.8, tighter: 14.5, deeper: 15.52, teeth: 15.98, until: 16.87, gone: 17.35,
  wipe2: 18.05, sawOne: 18.39, his: 19.61, reaction: 19.82, rest: 20.5, name: 21.35, horseFx: 22.39, bat: 23.61, bites: 24.11, nothing: 25.21,
  but: 26.43, panics: 26.71, runs: 27.33, collapses: 28.55, wipe3: 30.32, small: 30.6, big: 31.46, hurts: 32.88, wipe4: 34.05, everyday: 34.27,
  rude: 36.56, fire: 37.74, replay: 38.36, argument: 39.96, turn: 41.16, war: 41.74, time: 42.37, sleep: 42.95, peace: 43.73, gone2: 44.59,
  something: 45.47, two: 46.62, wipe5: 47.55, next: 47.77, cuts: 48.47, remember: 49.01, letGo: 50.41, rule: 52.4, worth: 53.16, cta: 54.6,
};
const win = (t, a, b) => t >= a && t < b;

// ======================= the snake's story =======================
function storyCuts(t) {
  const c = [];
  if (t >= K.cut) c.push({ i: 4, k: ss(K.cut, K.cut + 0.12, t) });
  return c;
}
function coilCuts(P, n, t) { const c = []; if (!P.depth) return c; const n0 = P.nNeck; const front = [];
  for (let j = 0; j < P.depth.length; j++) if (P.depth[j] > 0.15) front.push(n0 + j);
  const order = front.map(i => [hash(i * 1.37), i]).sort((a, b) => a[0] - b[0]).map(x => x[1]);
  for (let k = 0; k < Math.min(n, order.length); k++) c.push({ i: order[k], k: 1, drip: ((t * 1.3 + hash(k)) % 1) });
  return c; }
function cutCount(t) { // the counter: CUTS
  if (t < K.wipe1) return Math.round(lerp(28, 41, ss(0, 2.4, t)));
  if (t < K.cut) return 0; if (t < K.bit) return 1; if (t < K.cutMouth) return 2; if (t < K.tighter) return 3 + Math.round(4 * ss(K.wrapped, K.tighter, t));
  return 7 + Math.round(34 * ss(K.tighter, K.until, t));
}
function coilState(t, R, shiver) { return coilSpine(t, R, { shiver, head: [252, 708] }); }
function storyState(t) { // {P, o, coil}
  const o = { mood: 'calm', mouth: 0, tongue: 0, cuts: [] };
  if (t < K.wipe1) { // hook: squeezing hard, near the end
    const P = coilState(t, 49 + 1.5 * Math.sin(t * 9), 1); o.mood = 'angry'; o.mouth = 0.55 + 0.35 * Math.abs(Math.sin(t * 5)); o.headA = 0.42 + 0.06 * Math.sin(t * 11); o.cuts = coilCuts(P, 20, t); return { P, o, coil: true };
  }
  if (t < K.wrapped) {
    let hx, lift = 22, rear = 0, ha = null;
    if (t < K.cut) { const k = (t - K.start) / (K.cut - K.start); hx = lerp(-90, 286, eout(clamp(k))); lift = lerp(22, 46, ss(0.6, 1, k)); o.tongue = (Math.sin(t * 7) > 0.3) ? 1 : 0; }
    else if (t < K.sting) { hx = lerp(286, 300, ss(K.cut, K.sting, t)); lift = 46 - 8 * ss(K.cut, K.cut + 0.3, t); o.mood = 'alert'; }
    else {
      // recoil + rear up facing the blade tip
      const r = ss(K.sting, K.sting + 0.35, t); hx = lerp(300, 205, eout(r)); rear = r; ha = -0.12; o.mood = t > K.decided ? 'angry' : 'alert';
      o.mouth = t > K.attacking ? 0.75 + 0.15 * Math.sin(t * 20) : t > K.sting && t < K.sting + 0.5 ? 0.6 : 0; o.tongue = t < K.attacking ? 1 : 0;
      // strike 1: lunge at the tip
      if (t >= K.struck - 0.1 && t < K.bit - 0.2) { const c = t - (K.struck - 0.1); const k = c < 0.22 ? eout(c / 0.22) : 1 - eio(clamp((c - 0.5) / 0.5)); hx = lerp(205, 262, k); rear = lerp(1, 0.55, k); o.mouth = lerp(1, 0.9, k); ha = lerp(-0.12, 0.35, k); }
      // bite: grabs the blade and holds
      if (t >= K.bit - 0.2 && t < K.furious) { const k = eout(ss(K.bit - 0.2, K.bit + 0.05, t)); hx = lerp(205, 262, k); rear = lerp(1, 0.55, k); ha = lerp(-0.12, 0.35, k) + 0.05 * Math.sin(t * 30) * (t > K.bit ? 1 : 0); o.mouth = t > K.bit ? 0.32 : 1; }
      if (t >= K.furious) { const k = ss(K.furious, K.furious + 0.3, t); hx = lerp(262, 215, k); rear = lerp(0.55, 1, k); ha = -0.12 + 0.12 * Math.sin(t * 26); o.mouth = 0.9; o.mood = 'angry'; }
    }
    const P = groundSpine(hx, t, { lift, rear, amp: 9 });
    if (ha != null) o.headA = ha;
    o.cuts = storyCuts(t);
    return { P, o, coil: false };
  }
  // wrap: morph the slither into the coil, then squeeze, then die
  const R = t < K.tighter ? 60 : lerp(60, 49, ss(K.tighter, K.until, t));
  const dead = ss(K.until, K.gone + 0.1, t);
  const C = coilSpine(t, lerp(R, 55, dead), { shiver: t > K.tighter && t < K.until ? 1 : 0, head: [lerp(252, 280, dead), lerp(708, 846, eio(dead))] });
  const G = groundSpine(215, t, { lift: 26, rear: 1, amp: 9 });
  const m = eio(ss(K.wrapped, K.wrapped + 1.4, t));
  const P = m < 1 ? lerpSpine(G, C, m) : C;
  o.mood = t > K.gone - 0.05 ? 'dead' : 'angry'; o.mouth = dead > 0.5 ? 0.25 : 0.55 + 0.35 * Math.abs(Math.sin(t * 6)); o.headA = lerp(lerp(-0.12, 0.42, m), 0.15, dead);
  const n = Math.round(lerp(3, 7, ss(K.wrapped + 0.6, K.tighter, t)) + 14 * ss(K.tighter, K.until, t));
  o.cuts = coilCuts(P, n, t); if (dead > 0.5) for (const c of o.cuts) c.drip = 0.4;
  if (dead > 0) o.fill = mixCol(SNAKE, '#d9d2bf', dead);
  return { P, o, coil: true };
}
function mixCol(a, b, k) { const pa = a.match(/\w\w/g).map(h => parseInt(h, 16)), pb = b.match(/\w\w/g).map(h => parseInt(h, 16)); return `rgb(${pa.map((v, i) => Math.round(lerp(v, pb[i], k))).join(',')})`; }
function bloodPool(g, k, x = 410) { if (k <= 0) return; g.save(); g.fillStyle = RED; g.globalAlpha = 0.9; g.beginPath(); g.ellipse(x, FLOOR + 4, 20 + 90 * k, 5 + 9 * k, 0, 0, 7); g.fill(); g.restore(); }
function drips(g, t, k) { if (k <= 0) return; g.save(); g.fillStyle = RED; for (let i = 0; i < 6; i++) { const x = 330 + hash(i * 4.1) * 170, ph = (t * 1.1 + hash(i * 2.3)) % 1, y0 = sawBot(x) + 30; const y = lerp(y0, FLOOR, ph * ph); if (hash(i * 7) > k) continue; g.beginPath(); g.ellipse(x, y, 3.4, 5.5, 0, 0, 7); g.fill(); } g.restore(); }
function mouthBlood(g, t, k) { if (k <= 0) return; g.save(); g.fillStyle = RED; for (let i = 0; i < 3; i++) { const ph = (t * 1.4 + i / 3) % 1; g.beginPath(); g.ellipse(292 + i * 7, lerp(806, FLOOR, ph * ph), 3.2, 5, 0, 0, 7); g.fill(); } g.restore(); bloodPool(g, 0.25 * k, 300); }
function anger(g, x, y, k, s = 1) { if (k <= 0) return; g.save(); g.globalAlpha = k; g.strokeStyle = RED; g.lineWidth = 4 * s; g.lineCap = 'round'; for (let i = 0; i < 4; i++) { const a = i * Math.PI / 2 + 0.6; g.beginPath(); g.moveTo(x + Math.cos(a) * 5 * s, y + Math.sin(a) * 5 * s); g.quadraticCurveTo(x + Math.cos(a + 0.5) * 12 * s, y + Math.sin(a + 0.5) * 12 * s, x + Math.cos(a) * 16 * s, y + Math.sin(a) * 16 * s); g.stroke(); } g.restore(); }
function spark(g, x, y, k, r = 34) { if (k <= 0 || k >= 1) return; g.save(); g.globalAlpha = 1 - k; g.strokeStyle = RED; g.lineWidth = 4; g.lineCap = 'round'; for (let i = 0; i < 8; i++) { const a = i / 8 * Math.PI * 2 + 0.3, r0 = 8 + r * k, r1 = r0 + 16; g.beginPath(); g.moveTo(x + Math.cos(a) * r0, y + Math.sin(a) * r0); g.lineTo(x + Math.cos(a) * r1, y + Math.sin(a) * r1); g.stroke(); } g.restore(); }
function thought(g, x, y, w, h, k, tailTo) { if (k <= 0) return; g.save(); g.globalAlpha = Math.min(1, k * 1.4); const sc = 0.7 + 0.3 * eout(clamp(k));
  if (tailTo) for (const [f, r] of [[0.25, 7], [0.5, 11]]) blob(g, lerp(tailTo[0], x, f), lerp(tailTo[1], y + h * 0.45, f), r, r, FILL, 3);
  g.translate(x, y); g.scale(sc, sc); g.fillStyle = FILL; g.beginPath(); g.ellipse(0, 0, w / 2, h / 2, 0, 0, 7); g.fill();
  inkLine(g, Array.from({ length: 49 }, (_, i) => { const a = i / 48 * Math.PI * 2; return [Math.cos(a) * (w / 2 + 5 * Math.sin(a * 11)), Math.sin(a) * (h / 2 + 5 * Math.sin(a * 11))]; }), 3); g.restore(); }
// the saw as the snake imagines it: eyes + a toothy grin
function evilSaw(g, x, y, s, k, red) { g.save(); g.translate(x, y); g.scale(s, s); g.translate(-450, -770); drawSaw(g);
  g.fillStyle = '#fff'; g.strokeStyle = INK; g.lineWidth = 3; for (const ex of [330, 390]) { g.beginPath(); g.arc(ex, 768, 13, 0, 7); g.fill(); g.stroke(); g.fillStyle = red ? RED : INK; g.beginPath(); g.arc(ex + 3, 770, 5, 0, 7); g.fill(); g.fillStyle = '#fff'; }
  g.lineWidth = 5; g.lineCap = 'round'; g.beginPath(); g.moveTo(312, 745 - 4 * k); g.lineTo(346, 756); g.moveTo(406, 745 - 4 * k); g.lineTo(374, 756); g.stroke();
  if (red) { g.globalAlpha = 0.25; g.fillStyle = RED; g.fillRect(240, 700, 480, 140); } g.restore(); }

function workshopScene(g, t) {
  workshop(g); stump(g);
  const st = storyState(t);
  const sawShake = 0; // the saw never moves
  // blood on the floor
  if (st.coil) { const k = t < K.wipe1 ? 0.85 : ss(K.tighter, K.gone + 0.6, t); bloodPool(g, k); }
  if (t >= K.cutMouth && t < K.wrapped + 0.6) mouthBlood(g, t, ss(K.cutMouth, K.cutMouth + 0.3, t));
  // shadow
  g.save(); g.fillStyle = 'rgba(30,25,22,0.16)'; g.beginPath(); g.ellipse(st.coil ? 410 : st.P[20][0], FLOOR + 3, 200, 9, 0, 0, 7); g.fill(); g.restore();
  if (st.coil) { coilDraw(g, st.P, st.o, () => { drawSaw(g); sawBlood(g, t < K.wipe1 ? 1 : ss(K.wrapped, K.until, t)); }); drips(g, t, t < K.wipe1 ? 1 : ss(K.tighter, K.until, t) * (1 - ss(K.gone, K.gone + 1.2, t))); }
  else {
    drawSaw(g); if (t >= K.bit) sawBlood(g, 0.25);
    // body passes in front of the blade
    snakeChunk(g, st.P, 0, SN - 1, st.o); snakeHead(g, st.P, st.o);
  }
  // sting spark at the nick + the "!"
  if (t >= K.cut && t < K.cut + 0.5) spark(g, 290, 806, (t - K.cut) / 0.5, 26);
  if (win(t, K.sting, K.sting + 0.8)) { const k = ss(K.sting, K.sting + 0.12, t) * (1 - ss(K.sting + 0.6, K.sting + 0.8, t)); g.save(); g.globalAlpha = k; g.font = '80px "Permanent Marker"'; g.fillStyle = RED; g.textAlign = 'center'; g.fillText('!', 180, 690); g.restore(); }
  if (t >= K.struck && t < K.struck + 0.6) spark(g, 300, 784, (t - K.struck - 0.12) / 0.45, 40);
  if (t >= K.bit && t < K.bit + 0.5) spark(g, 300, 790, (t - K.bit) / 0.5, 40);
  // anger marks
  if (!st.coil && t > K.decided) anger(g, st.P[0][0] - 20, st.P[0][1] - 56, 1, 1.4);
  if (st.coil && st.o.mood === 'angry') anger(g, st.P[0][0] - 30, st.P[0][1] - 52, 1, 1.4);
  // what he thinks: the saw is attacking him
  if (t >= K.decided - 0.1 && t < K.struck) { const k = ss(K.decided - 0.1, K.decided + 0.25, t) * (1 - ss(K.struck - 0.25, K.struck, t));
    thought(g, 300, 520, 340, 210, k, [215, 720]); if (k > 0.3) { g.save(); g.globalAlpha = clamp(k * 1.5 - 0.4); const red = t > K.attacking; const lun = red ? Math.sin(t * 16) * 6 : 0; evilSaw(g, 300 + lun, 528, 0.62, red ? 1 : 0, red); g.restore(); } }
}

// ======================= scoreboard: one cut vs the rest =======================
function scoreScene(g, t) {
  paper(g);
  const pts = []; for (let y = -40; y <= DH + 40; y += 26) pts.push([360 + (hash(y) - 0.5) * 10, y]);
  // left: the saw alone
  g.save(); g.translate(180, 760); g.scale(0.62, 0.62); g.translate(-470, -790); drawSaw(g); sawBlood(g, 0.3); g.restore();
  // right: the saw with the snake (dead)
  g.save(); g.translate(540, 760); g.scale(0.62, 0.62); g.translate(-470, -800); const P = coilSpine(17.5, 55, { head: [280, 846] }); const cut = coilCuts(P, 18, 17.5); for (const c of cut) c.drip = 0.4; bloodPool(g, 1);
  coilDraw(g, P, { mood: 'dead', mouth: 0.25, headA: 0.15, cuts: cut, fill: '#d9d2bf' }, () => { drawSaw(g); sawBlood(g, 1); }); g.restore();
  inkLine(g, pts, 5);
  g.textAlign = 'center';
  const k1 = ss(K.sawOne, K.sawOne + 0.2, t), k2 = ss(K.his, K.his + 0.2, t);
  g.save(); g.globalAlpha = k1; g.font = '40px "Patrick Hand SC"'; g.fillStyle = INK; g.fillText('THE SAW', 180, 420); g.font = '150px "Permanent Marker"'; const p1 = 1 + 0.25 * Math.exp(-(t - K.sawOne - 0.43) * 9) * (t > K.sawOne + 0.43 ? 1 : 0); g.translate(180, 560); g.scale(p1, p1); g.fillText('1', 0, 0); g.restore();
  g.save(); g.globalAlpha = k1; g.font = '30px "Patrick Hand SC"'; g.fillStyle = INK; g.fillText('CUT', 180, 610); g.restore();
  const n = Math.round(lerp(1, 40, eout(ss(K.reaction, K.rest + 0.2, t))));
  g.save(); g.globalAlpha = k2; g.font = '40px "Patrick Hand SC"'; g.fillStyle = INK; g.fillText('HIS REACTION', 540, 420); g.font = '150px "Permanent Marker"'; g.fillStyle = RED; const p2 = 1 + 0.12 * Math.abs(Math.sin(t * 14)) * (t < K.rest + 0.2 ? 1 : 0); g.translate(540, 560); g.scale(p2, p2); g.fillText(String(n), 0, 0); g.restore();
  g.save(); g.globalAlpha = k2; g.font = '30px "Patrick Hand SC"'; g.fillStyle = INK; g.fillText('CUTS', 540, 610); g.restore();
}

// ======================= the wild horse effect =======================
function plain(g, scroll) {
  paper(g); const GY = 900;
  // far hills (slow), near grass (fast)
  const h = []; for (let x = -60; x <= 780; x += 30) { const u = x + scroll * 0.15; h.push([x, 640 - 40 * Math.sin(u * 0.008) - 20 * Math.sin(u * 0.021 + 1)]); } inkLine(g, h, 2.2, 'rgba(30,25,22,0.45)');
  const h2 = []; for (let x = -60; x <= 780; x += 30) { const u = x + scroll * 0.4; h2.push([x, 760 - 26 * Math.sin(u * 0.012 + 2) - 12 * Math.sin(u * 0.03)]); } inkLine(g, h2, 2.4, 'rgba(30,25,22,0.6)');
  inkLine(g, [[-60, GY + 1], [780, GY - 1]], 3.5);
  for (let i = 0; i < 22; i++) { const x = ((i * 67 - scroll) % 840 + 840) % 840 - 60, y = GY + 20 + hash(i) * 180; inkLine(g, [[x - 8, y], [x - 4, y - 14]], 2, 'rgba(30,25,22,0.5)'); inkLine(g, [[x, y], [x + 2, y - 18]], 2, 'rgba(30,25,22,0.5)'); inkLine(g, [[x + 8, y], [x + 6, y - 13]], 2, 'rgba(30,25,22,0.5)'); }
  for (let i = 0; i < 6; i++) { const x = ((i * 151 - scroll) % 840 + 840) % 840 - 60; inkLine(g, [[x - 6, GY], [x - 3, GY - 12]], 2); inkLine(g, [[x + 2, GY], [x + 4, GY - 15]], 2); }
}
function horseX(t) { return 380; }
function horseScroll(t) { // distance travelled (px) - accelerates on "runs", stops on collapse
  if (t < K.runs - 0.2) return 0; const a = t - (K.runs - 0.2), stop = K.collapses + 0.5; const v = 1400;
  if (t < stop) return v * a * a / (a + 0.4); const a2 = stop - (K.runs - 0.2); const d0 = v * a2 * a2 / (a2 + 0.4); const dt = t - stop; return d0 + v * 0.35 * (1 - Math.exp(-dt * 3)); }
function horseScene(g, t) {
  const sc = horseScroll(t); plain(g, sc);
  const GY = 900; const run = ss(K.runs - 0.3, K.runs + 0.1, t) * (1 - ss(K.collapses, K.collapses + 0.3, t));
  let mode = 'stand', rear = 0, down = 0; if (t >= K.panics - 0.1 && t < K.runs - 0.2) { mode = 'rear'; rear = Math.sin(clamp((t - K.panics + 0.1) / (K.runs - K.panics)) * Math.PI); }
  if (run > 0) mode = 'run'; if (t >= K.collapses) { mode = 'down'; down = eout(ss(K.collapses, K.collapses + 0.5, t)); }
  const panic = ss(K.panics - 0.1, K.panics + 0.1, t);
  const hx = horseX(t);
  g.save(); g.fillStyle = 'rgba(30,25,22,0.16)'; g.beginPath(); g.ellipse(hx, GY + 3, 170, 9, 0, 0, 7); g.fill(); g.restore();
  // speed lines + dust while running
  if (run > 0.2) { g.save(); g.globalAlpha = run; for (let i = 0; i < 8; i++) { const y = 560 + hash(i) * 330, x = ((hash(i * 3) * 900 - t * 2600) % 900 + 900) % 900 - 90; inkLine(g, [[x, y], [x + 90 + 60 * hash(i * 5), y]], 2.2, 'rgba(30,25,22,0.5)'); } g.restore(); }
  for (let i = 0; i < 5; i++) { const ph = ((t * 2.2) + i / 5) % 1; if (run < 0.2 && !(t >= K.collapses && t < K.collapses + 1.2)) break; const big = t >= K.collapses ? 1.8 : 1; blob(g, hx - 150 - ph * 160, GY - 14 - ph * 24, (10 + 20 * ph) * big, (8 + 14 * ph) * big, `rgba(237,230,214,${1 - ph})`, 2 * (1 - ph)); }
  drawHorse(g, { x: hx, y: GY, s: 1.45, ph: t * 2.6, run, mode, rear, down, panic });
  // the bite dot on the near front leg
  const legP = [hx + (72 + 20) * 1.45 - 60 * 1.45 * 0, GY - 58];
  if (t >= K.bites && t < K.collapses) { g.save(); g.fillStyle = RED; g.beginPath(); g.arc(hx + 92, GY - 64 + (mode === 'run' ? -20 * Math.abs(Math.sin(t * 2.6 * Math.PI * 2)) : 0), 3.4, 0, 7); g.fill(); g.restore(); }
  // bat: flies in, bites, flies off
  if (t >= K.bat - 0.1 && t < K.but) { let bx, by; const a = clamp((t - K.bat + 0.1) / 0.6), b = clamp((t - K.bites - 0.3) / 0.9);
    bx = lerp(780, hx + 108, eout(a)); by = lerp(420, GY - 80, eout(a)); if (b > 0) { bx = lerp(hx + 108, 820, eio(b)); by = lerp(GY - 80, 300, eio(b)); }
    drawBat(g, bx, by, 1.3, t * 7); }
  if (t >= K.bites && t < K.bites + 0.5) spark(g, hx + 92, GY - 64, (t - K.bites) / 0.5, 18);
  // "the bite is nothing": a tiny label
  if (win(t, K.nothing - 0.2, K.but)) { const k = ss(K.nothing - 0.2, K.nothing, t); g.save(); g.globalAlpha = k; inkLine(g, [[hx + 50, GY - 170], [hx + 84, GY - 74]], 3, RED); inkLine(g, [[hx + 72, GY - 90], [hx + 84, GY - 74], [hx + 90, GY - 94]], 3, RED); g.font = '34px "Patrick Hand SC"'; g.fillStyle = RED; g.textAlign = 'center'; g.fillText('TINY BITE', hx + 40, GY - 180); g.restore(); }
  if (t >= K.panics - 0.05 && t < K.runs) { const k = ss(K.panics - 0.05, K.panics + 0.1, t); g.save(); g.globalAlpha = k; g.font = '80px "Permanent Marker"'; g.fillStyle = RED; g.textAlign = 'center'; g.fillText('!!', hx + 150, 540); g.restore(); }
  // title
  const tk = ss(K.horseFx - 0.1, K.horseFx + 0.2, t) * (1 - ss(K.bat + 0.2, K.bat + 0.5, t));
  if (tk > 0) { g.save(); g.globalAlpha = tk; const p = 1 + 0.15 * Math.exp(-(t - K.horseFx) * 8); g.translate(360, 380); g.scale(p, p); g.translate(-360, -380); g.textAlign = 'center';
    fitFont(g, 'THE WILD HORSE', 76, 'Permanent Marker', 600); g.fillStyle = INK; g.fillText('THE WILD HORSE', 360, 360); g.font = '76px "Permanent Marker"'; g.fillStyle = RED; g.fillText('EFFECT', 360, 446);
    const ul = ss(K.horseFx + 0.2, K.horseFx + 0.7, t); inkLine(g, [[200, 470], [lerp(200, 520, ul), 466]], 6, RED); g.restore(); }
}

// ======================= small wound + big reaction = real damage =======================
function bandage(g, x, y, s) { g.save(); g.translate(x, y); g.rotate(-0.4); g.scale(s, s); inkShape(g, [[-44, -14], [44, -14], [44, 14], [-44, 14]], '#f0d6b4', 3); inkShape(g, [[-14, -14], [14, -14], [14, 14], [-14, 14]], '#e7c49c', 2); g.strokeStyle = RED; g.lineWidth = 3; g.beginPath(); g.moveTo(-6, 0); g.lineTo(6, 0); g.stroke(); g.restore(); }
function burst(g, x, y, r, spin = 0, label = null) { g.save(); g.fillStyle = RED; g.strokeStyle = INK; g.lineWidth = 3.5; g.beginPath();
  for (let i = 0; i <= 24; i++) { const a = i / 24 * Math.PI * 2 + spin, rr = r * (i % 2 ? 0.55 : 1) * (0.9 + 0.2 * hash(i + Math.floor(T * 8))); g.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr); } g.closePath(); g.fill(); g.stroke();
  if (label) { g.fillStyle = FILL; g.textAlign = 'center'; g.font = `${r * 0.42}px "Permanent Marker"`; g.fillText(label, x, y + r * 0.15); } g.restore(); }
function brokenHeart(g, x, y, r, k) { heart(g, x - 6 * k, y, r, 1); g.save(); g.strokeStyle = PAPER; g.lineWidth = 8; g.beginPath(); g.moveTo(x - 2, y - r * 0.5); g.lineTo(x + 8, y - r * 0.1); g.lineTo(x - 6, y + r * 0.25); g.lineTo(x + 4, y + r * 0.7); g.stroke(); g.strokeStyle = INK; g.lineWidth = 3; g.stroke(); g.restore(); }
function equationScene(g, t) {
  paper(g);
  const rows = [[K.small, 360], [K.big, 600], [K.hurts, 840]];
  const k1 = ss(K.small, K.small + 0.2, t), k2 = ss(K.big, K.big + 0.2, t), k3 = ss(K.hurts, K.hurts + 0.2, t);
  g.textAlign = 'left';
  // row 1
  if (k1 > 0) { g.save(); g.globalAlpha = k1; bandage(g, 150, 330, 0.8 + 0.2 * eout(k1)); g.font = '58px "Permanent Marker"'; g.fillStyle = INK; g.fillText('SMALL WOUND', 250, 352); g.restore(); }
  if (k2 > 0) { g.save(); g.globalAlpha = k2; g.font = '70px "Permanent Marker"'; g.fillStyle = INK; g.textAlign = 'center'; g.fillText('+', 360, 470); const r = 66 * (0.6 + 0.4 * eout(k2)) * (1 + 0.06 * Math.sin(t * 22)); burst(g, 150, 580, r, t * 0.5); g.textAlign = 'left'; g.font = '58px "Permanent Marker"'; g.fillStyle = RED; g.fillText('BIG REACTION', 250, 602); g.restore(); }
  if (k3 > 0) { g.save(); g.globalAlpha = k3; g.font = '70px "Permanent Marker"'; g.fillStyle = INK; g.textAlign = 'center'; g.fillText('=', 360, 718); brokenHeart(g, 150, 818, 44 * (0.7 + 0.3 * eout(k3)), ss(K.hurts + 0.2, K.hurts + 0.5, t)); g.textAlign = 'left'; g.font = '58px "Permanent Marker"'; g.fillStyle = INK; g.fillText('REAL DAMAGE', 250, 842); inkLine(g, [[250, 862], [lerp(250, 640, ss(K.hurts + 0.2, K.hurts + 0.7, t)), 858]], 6, RED); g.restore(); }
}

// ======================= people (ink, round heads) =======================
function prim(g, q, o, w, col) {
  const s = o.s, d = o.dir, X = p => o.x + p[0] * d * s, Y = p => o.y + p[1] * s;
  g.strokeStyle = col; g.fillStyle = col; g.lineCap = 'round'; g.lineJoin = 'round';
  if (q.t === 'l') { g.lineWidth = (q.w + w) * s; g.beginPath(); const p0 = jit(X(q.p[0]), Y(q.p[0]), 0.6); g.moveTo(p0[0], p0[1]); for (let i = 1; i < q.p.length; i++) { const p = jit(X(q.p[i]), Y(q.p[i]), 0.6); g.lineTo(p[0], p[1]); } g.stroke(); }
  else if (q.t === 'e') { const c = jit(X(q.c), Y(q.c), 0.5); g.beginPath(); g.ellipse(c[0], c[1], (q.rx + w / 2) * s, (q.ry + w / 2) * s, 0, 0, 7); g.fill(); }
}
function person(g, o) {
  const s = o.s, d = o.dir; const X = v => o.x + v * d * s, Y = v => o.y + v * s; const ph = o.walk || 0, wa = o.walk != null ? 1 : 0;
  const head = [0, -200];
  const legs = [[[-8, -80], [-8 + 14 * Math.sin(ph) * wa, -40], [-10 + 22 * Math.sin(ph) * wa, 0]], [[8, -80], [8 - 14 * Math.sin(ph) * wa, -40], [10 - 22 * Math.sin(ph) * wa, 0]]];
  let arms;
  if (o.arms === 'phone') arms = [[[-14, -150], [-22, -110], [14, -112]], [[14, -150], [26, -112], [20, -112]]];
  else if (o.arms === 'type') { const a = Math.sin(T * 40) * 4; arms = [[[-14, -150], [-22, -110], [10, -116 + a]], [[14, -150], [26, -112], [22, -114 - a]]]; }
  else if (o.arms === 'fists') arms = [[[-14, -150], [-4, -122], [26, -136]], [[14, -150], [34, -126], [46, -146]]];
  else if (o.arms === 'point') arms = [[[-14, -150], [-22, -112], [-20, -76]], [[14, -150], [50, -150], [80, -160]]];
  else arms = [[[-14, -150], [-22 - 6 * Math.sin(ph) * wa, -112], [-20 - 14 * Math.sin(ph) * wa, -76]], [[14, -150], [22 + 6 * Math.sin(ph) * wa, -112], [20 + 14 * Math.sin(ph) * wa, -76]]];
  const L = (pts, w) => ({ t: 'l', p: pts, w });
  const body = [L(legs[0], 15), L(legs[1], 15), L([[0, -150], [0, -90]], 50), L(arms[0], 13), L(arms[1], 13), { t: 'e', c: head, rx: 36, ry: 36 }];
  const oo = { x: o.x, y: o.y, s, dir: d };
  g.save(); g.globalAlpha = o.alpha ?? 1;
  for (const q of body) prim(g, q, oo, 6.5, INK); for (const q of body) prim(g, q, oo, 0, o.fill || FILL);
  for (const a of arms) { const h = a[2]; g.fillStyle = FILL; g.strokeStyle = INK; g.lineWidth = 3 * s; g.beginPath(); g.arc(X(h[0]), Y(h[1]), (o.arms === 'fists' ? 10 : 8) * s, 0, 7); g.fill(); g.stroke(); }
  if (o.arms === 'phone' || o.arms === 'type') { g.save(); g.translate(X(16), Y(-128)); g.rotate(-0.15 * d); g.fillStyle = INK; g.beginPath(); g.roundRect(-11 * s, -20 * s, 22 * s, 36 * s, 4 * s); g.fill(); g.fillStyle = o.screen || '#cfe0e6'; g.fillRect(-8 * s, -16 * s, 16 * s, 26 * s); g.restore(); }
  const hx = X(head[0]) + 6 * d * s, hy = Y(head[1]); g.strokeStyle = INK; g.fillStyle = INK; g.lineCap = 'round'; g.lineWidth = 3.2 * s; const f = o.face || 'calm';
  for (const e of [-12, 12]) { const x = hx + e * s, y = hy - 4 * s;
    if (f === 'smile') { g.beginPath(); g.arc(x, y + 2 * s, 5 * s, Math.PI * 1.1, Math.PI * 1.9); g.stroke(); }
    else if (f === 'wide') { g.fillStyle = '#fff'; g.beginPath(); g.arc(x, y, 7 * s, 0, 7); g.fill(); g.stroke(); g.fillStyle = INK; g.beginPath(); g.arc(x, y, 2.6 * s, 0, 7); g.fill(); }
    else { g.beginPath(); g.arc(x, y, 3.4 * s, 0, 7); g.fill(); }
    if (f === 'angry' || f === 'shout' || f === 'frown') { const tilt = f === 'frown' ? 0.4 : 1; g.beginPath(); g.moveTo(x - 7 * s * Math.sign(e), y - 16 * s * tilt); g.lineTo(x + 7 * s * Math.sign(e), y - 9 * s + 3 * s * tilt); g.stroke(); } }
  g.beginPath();
  if (f === 'smile') { g.arc(hx, hy + 8 * s, 10 * s, 0.15 * Math.PI, 0.85 * Math.PI); g.stroke(); }
  else if (f === 'frown' || f === 'angry') { g.arc(hx, hy + 22 * s, 9 * s, 1.2 * Math.PI, 1.8 * Math.PI); g.stroke(); }
  else if (f === 'shout') { g.fillStyle = RED; g.ellipse(hx, hy + 14 * s, 9 * s, 7 * s, 0, 0, 7); g.fill(); g.stroke(); }
  else if (f === 'wide') { g.moveTo(hx - 5 * s, hy + 15 * s); g.lineTo(hx + 5 * s, hy + 15 * s); g.stroke(); }
  else { g.moveTo(hx - 7 * s, hy + 13 * s); g.lineTo(hx + 7 * s, hy + 13 * s); g.stroke(); }
  if (o.mad) anger(g, X(head[0]) - 26 * d * s, Y(head[1]) - 40 * s, 1, s);
  g.restore();
}
function bubble(g, x, y, w, h, txt, k, tailDir = -1, col = FILL, txtCol = INK, size = 28) {
  if (k <= 0) return; g.save(); g.globalAlpha = Math.min(1, k * 1.5); g.translate(x, y); const sc = 0.7 + 0.3 * eout(clamp(k)); g.scale(sc, sc);
  g.fillStyle = col; g.strokeStyle = INK; g.lineWidth = 3; g.beginPath(); g.roundRect(-w / 2, -h / 2, w, h, 16); g.fill(); g.stroke();
  g.beginPath(); g.moveTo(tailDir * w * 0.25 - 10, h / 2 - 1.5); g.lineTo(tailDir * w * 0.25 + tailDir * 6, h / 2 + 18); g.lineTo(tailDir * w * 0.25 + 12, h / 2 - 1.5); g.fill(); g.stroke();
  g.fillStyle = col; g.fillRect(tailDir * w * 0.25 - 9, h / 2 - 5, 20, 6);
  g.fillStyle = txtCol; g.textAlign = 'center'; g.textBaseline = 'middle'; fitFont(g, txt, size + 6, 'Patrick Hand SC', w - 26); g.fillText(txt, 0, 2); g.textBaseline = 'alphabetic'; g.restore();
}
function impactBig(g, x, y, k, label) { g.save(); g.globalAlpha = 1 - k * 0.4; const r = 50 + 80 * eout(k); burst(g, x, y, r, 0, label); g.restore(); }
function room(g, night) {
  paper(g); for (let i = 0; i < 12; i++) { const x = -40 + i * 74; inkLine(g, [[x, -60], [x + 2, FLOOR - 4]], 1, 'rgba(30,25,22,0.12)'); }
  inkLine(g, [[-60, FLOOR + 1], [780, FLOOR - 1]], 3.5); for (let i = 1, d = 30; i < 7; i++, d *= 1.45) inkLine(g, [[-60, FLOOR + d], [780, FLOOR + d]], 1.1, 'rgba(30,25,22,0.16)');
}
function phoneBig(g, x, y, s, k, lines) { if (k <= 0) return; g.save(); g.globalAlpha = Math.min(1, k * 1.5); g.translate(x, y); g.scale(s * (0.85 + 0.15 * eout(k)), s * (0.85 + 0.15 * eout(k)));
  g.fillStyle = INK; g.beginPath(); g.roundRect(-150, -250, 300, 500, 36); g.fill(); g.fillStyle = FILL; g.beginPath(); g.roundRect(-136, -224, 272, 450, 22); g.fill();
  g.fillStyle = INK; g.beginPath(); g.roundRect(-30, -240, 60, 10, 5); g.fill();
  for (const ln of lines) ln(g); g.restore(); }
function comment(g, y, name, txt, col, a = 1) { g.save(); g.globalAlpha *= a; blob(g, -100, y, 20, 20, '#d8cbb5', 2.5); g.textAlign = 'left'; g.font = '22px "Patrick Hand SC"'; g.fillStyle = 'rgba(30,25,22,0.6)'; g.fillText(name, -70, y - 6); g.font = '30px "Patrick Hand SC"'; g.fillStyle = col; fitFont(g, txt, 30, 'Patrick Hand SC', 190); g.fillText(txt, -70, y + 22); g.restore(); }
function battery(g, x, y, w, h, lvl, label, k) { g.save(); g.globalAlpha = k;
  inkShape(g, [[x, y], [x + w, y], [x + w, y + h], [x, y + h]], FILL, 4); inkShape(g, [[x + w, y + h * 0.3], [x + w + 14, y + h * 0.3], [x + w + 14, y + h * 0.7], [x + w, y + h * 0.7]], INK, 3);
  const col = lvl > 0.35 ? '#8fae6e' : RED; const segs = 5; for (let i = 0; i < segs; i++) { const on = lvl * segs > i + 0.05; if (!on) continue; g.fillStyle = col; g.fillRect(x + 8 + i * (w - 16) / segs + 2, y + 8, (w - 16) / segs - 6, h - 16); }
  g.font = '40px "Permanent Marker"'; g.textAlign = 'right'; g.fillStyle = INK; g.fillText(label, x - 18, y + h * 0.68);
  g.font = '30px "Patrick Hand SC"'; g.textAlign = 'center'; g.fillStyle = lvl < 0.05 ? RED : INK; g.fillText(Math.round(lvl * 100) + '%', x + w / 2, y + h + 34); g.restore(); }
function stopwatch(g, x, y, r, sec, k) { if (k <= 0) return; g.save(); g.globalAlpha = k; g.translate(x, y); const sc = 0.8 + 0.2 * eout(k); g.scale(sc, sc);
  inkShape(g, [[-14, -r - 26], [14, -r - 26], [14, -r - 4], [-14, -r - 4]], WOOD, 3); blob(g, 0, 0, r, r, FILL, 5);
  for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; inkLine(g, [[Math.sin(a) * r * 0.82, -Math.cos(a) * r * 0.82], [Math.sin(a) * r * 0.92, -Math.cos(a) * r * 0.92]], 3); }
  const a = sec / 60 * Math.PI * 2 * 5; g.fillStyle = 'rgba(200,40,42,0.25)'; g.beginPath(); g.moveTo(0, 0); g.arc(0, 0, r * 0.78, -Math.PI / 2, -Math.PI / 2 + a); g.closePath(); g.fill();
  inkLine(g, [[0, 0], [Math.sin(a) * r * 0.75, -Math.cos(a) * r * 0.75]], 6, RED); blob(g, 0, 0, 8, 8, INK, 0);
  g.font = '64px "Permanent Marker"'; g.textAlign = 'center'; g.fillStyle = INK; g.fillText('0:0' + Math.min(2, Math.floor(sec)), 0, r * 0.55); g.restore(); }
function nightWash(g, k) { if (k <= 0) return; g.save(); g.globalCompositeOperation = 'multiply'; g.fillStyle = `rgba(200,210,230,${0.45 * k})`; g.fillRect(-400, -400, DW + 800, DH + 800); g.restore(); }
function lifeScene(g, t) {
  const Y0 = FLOOR + 60;
  if (t < K.rude) { // we do it every day: walking, calendar flipping
    room(g); const day = Math.floor(clamp((t - K.everyday) / 0.45, 0, 6)); const days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];
    g.save(); g.translate(360, 360); inkShape(g, [[-90, -70], [90, -70], [90, 90], [-90, 90]], FILL, 4); g.fillStyle = RED; g.fillRect(-88, -68, 176, 44); g.font = '30px "Permanent Marker"'; g.textAlign = 'center'; g.fillStyle = FILL; g.fillText('EVERY DAY', 0, -36); g.fillStyle = INK; g.font = '76px "Permanent Marker"'; g.fillText(days[day], 0, 60); g.restore();
    person(g, { x: 360, y: Y0, s: 1.7, dir: 1, face: 'frown', arms: 'phone', walk: t * 9 });
    return;
  }
  if (t < K.fire) { // one rude comment
    room(g); const k = ss(K.rude, K.rude + 0.2, t);
    phoneBig(g, 360, 600, 1.1, 1, [g2 => { comment(g2, -150, '@you', 'new post!', INK); g2.save(); const kk = ss(K.rude + 0.15, K.rude + 0.35, t); g2.globalAlpha = kk; g2.fillStyle = 'rgba(200,40,42,0.12)'; g2.fillRect(-132, -40, 264, 90); comment(g2, 0, '@someone', 'nobody asked.', RED); g2.restore(); }]);
    return;
  }
  if (t < K.replay) { // you fire back
    room(g); person(g, { x: 230, y: Y0, s: 1.8, dir: 1, face: 'angry', arms: 'type', mad: true });
    const msgs = ['EXCUSE ME??', 'WHO ASKED YOU?', 'SAY THAT AGAIN', '!!!']; for (let i = 0; i < 4; i++) { const t0 = K.fire + i * 0.13; const k = ss(t0, t0 + 0.12, t); bubble(g, 470 + (i % 2) * 40, 680 - i * 110, 250, 64, msgs[i], k, -1, FILL, RED, 30); }
    return;
  }
  if (t < K.argument) { // replay it all night
    room(g); nightWash(g, 1);
    g.save(); g.translate(560, 300); blob(g, 0, 0, 44, 44, '#f7f1e2', 3); g.restore();
    g.save(); g.font = '46px "Permanent Marker"'; g.textAlign = 'center'; g.fillStyle = INK; const mins = 2 * 60 + 12 + Math.floor((t - K.replay) * 40); g.fillText(`${Math.floor(mins / 60) + 1}:${String(mins % 60).padStart(2, '0')} AM`, 200, 310); g.restore();
    person(g, { x: 360, y: Y0, s: 2.1, dir: 1, face: 'wide', arms: 'phone' });
    const loop = ((t - K.replay) * 2.2) % 1; bubble(g, 360, 600, 300, 76, '"nobody asked."', 0.4 + 0.6 * eout(loop), -1, FILL, RED, 36);
    g.save(); g.translate(560, 600); g.rotate(-t * 8); g.strokeStyle = RED; g.lineWidth = 5; g.beginPath(); g.arc(0, 0, 26, 0.3, 5.6); g.stroke(); g.fillStyle = RED; g.beginPath(); g.moveTo(26 * Math.cos(0.3) - 9, 26 * Math.sin(0.3) - 2); g.lineTo(26 * Math.cos(0.3) + 9, 26 * Math.sin(0.3) - 2); g.lineTo(26 * Math.cos(0.3), 26 * Math.sin(0.3) + 12); g.fill(); g.restore();
    return;
  }
  if (t < K.time) { // a small argument becomes a war
    room(g); const warK = ss(K.turn, K.war, t);
    person(g, { x: 190, y: Y0, s: 1.6, dir: 1, face: warK > 0.3 ? 'shout' : 'frown', arms: warK > 0.3 ? 'fists' : 'down', mad: warK > 0.3 });
    person(g, { x: 530, y: Y0, s: 1.6, dir: -1, face: warK > 0.5 ? 'shout' : 'calm', arms: warK > 0.5 ? 'fists' : 'down', fill: '#f4eadb', mad: warK > 0.5 });
    bubble(g, 230, 520, 250, 62, 'you forgot. again.', ss(K.argument + 0.1, K.argument + 0.3, t), -1);
    if (t > K.turn) { const n = Math.floor((t - K.turn) / 0.09); const ws = ['ALWAYS!', 'NEVER!', 'YOU!', 'ME?!', 'WHY?!', 'ENOUGH!']; for (let i = 0; i < Math.min(n, 6); i++) bubble(g, 120 + hash(i * 3) * 480, 380 + hash(i * 7) * 300, 150, 54, ws[i], 1, i % 2 ? 1 : -1, FILL, RED, 30); }
    if (t > K.war - 0.05) impactBig(g, 360, 650, clamp((t - K.war + 0.05) / 0.6), 'WAR!');
    return;
  }
  if (t < K.wipe5) { // batteries drain, then: 2 seconds
    room(g);
    const lv = tt => 1 - eio(ss(tt, tt + 0.55, t));
    const out = ss(K.something - 0.1, K.something + 0.3, t);
    g.save(); g.translate(0, -120 * out); g.globalAlpha = 1 - out;
    battery(g, 300, 330, 260, 96, lv(K.time + 0.05), 'TIME', ss(K.time - 0.1, K.time + 0.1, t));
    battery(g, 300, 500, 260, 96, lv(K.sleep + 0.05), 'SLEEP', ss(K.sleep - 0.1, K.sleep + 0.1, t));
    battery(g, 300, 670, 260, 96, lv(K.peace + 0.05), 'PEACE', ss(K.peace - 0.1, K.peace + 0.1, t));
    g.restore();
    if (t >= K.gone2 && t < K.something) { const k = (0.5 + 0.5 * Math.sin(t * 20)) * (1 - out); g.save(); g.globalAlpha = k; g.strokeStyle = RED; g.lineWidth = 6; for (const y of [330, 500, 670]) { g.beginPath(); g.roundRect(292, y - 8, 276, 112, 10); g.stroke(); } g.restore(); }
    stopwatch(g, 360, 560, 190, clamp((t - K.something - 0.3) / (K.two + 0.15 - K.something - 0.3)) * 2, out);
    return;
  }
}

// ======================= ending: a new snake lets go =======================
function endScene(g, t) {
  workshop(g); stump(g); drawSaw(g); sawBlood(g, 0.15);
  const o = { mood: 'calm', mouth: 0, tongue: 0, cuts: [] };
  let hx, lift = 22;
  if (t < K.cuts) { hx = lerp(-90, 288, eout(clamp((t - K.wipe5) / (K.cuts - K.wipe5)))); lift = lerp(22, 46, ss(K.cuts - 0.4, K.cuts, t)); o.tongue = Math.sin(t * 7) > 0.3 ? 1 : 0; }
  else if (t < K.letGo) { hx = 288 + 4 * ss(K.cuts, K.cuts + 0.3, t); lift = 46 - 8 * ss(K.cuts, K.cuts + 0.3, t); o.mood = t < K.remember ? 'alert' : 'calm'; o.cuts = [{ i: 4, k: 1 }]; o.tongue = t > K.remember + 0.6 ? 1 : 0; }
  else { const k = clamp((t - K.letGo - 0.25) / 4.6); hx = lerp(292, 1180, k * (0.6 + 0.4 * k)); lift = lerp(38, 22, ss(K.letGo, K.letGo + 0.4, t)); o.cuts = [{ i: 4, k: 1 }]; o.tongue = Math.sin(t * 7) > 0.3 ? 1 : 0; }
  const P = groundSpine(hx, t, { lift, amp: 9 });
  g.save(); g.fillStyle = 'rgba(30,25,22,0.16)'; g.beginPath(); g.ellipse(P[20][0], FLOOR + 3, 200, 9, 0, 0, 7); g.fill(); g.restore();
  snakeChunk(g, P, 0, SN - 1, o); snakeHead(g, P, o);
  if (t >= K.cuts && t < K.cuts + 0.45) spark(g, 290, 806, (t - K.cuts) / 0.45, 22);
  // remember the snake: thought bubble with the first snake on the saw
  if (t >= K.remember - 0.1 && t < K.letGo + 0.3) { const k = ss(K.remember - 0.1, K.remember + 0.2, t) * (1 - ss(K.letGo, K.letGo + 0.3, t)); thought(g, 300, 540, 380, 250, k, [270, 760]);
    if (k > 0.3) { g.save(); g.globalAlpha = clamp(k * 1.5 - 0.4); g.beginPath(); g.ellipse(300, 540, 170, 105, 0, 0, 7); g.clip(); g.translate(300, 548); g.scale(0.44, 0.44); g.translate(-450, -790);
      const Pc = coilSpine(17.5, 55, { head: [280, 846] }); const cut = coilCuts(Pc, 18, 17.5); bloodPool(g, 1); coilDraw(g, Pc, { mood: 'dead', mouth: 0.25, headA: 0.15, cuts: cut, fill: '#d9d2bf' }, () => { drawSaw(g); sawBlood(g, 1); }); g.restore(); } }
}
function ctaScene(g, t) { endScene(g, t); }

// ======================= transitions =======================
function inkWipe(g, k) {
  if (k <= 0 || k >= 1) return; const e = k < 0.5 ? lerp(DW + 60, -60, eio(k * 2)) : -60, e2 = k < 0.5 ? DW + 60 : lerp(DW + 60, -60, eio((k - 0.5) * 2));
  g.save(); g.beginPath(); g.moveTo(e, -40); for (let y = -40; y <= DH + 40; y += 24) g.lineTo(e + (hash(y * 0.7 + 3) - 0.5) * 50, y); for (let y = DH + 40; y >= -40; y -= 30) g.lineTo(Math.min(e2, DW + 60) + (hash(y * 0.3) - 0.5) * 40, y); g.closePath();
  g.fillStyle = '#16120f'; g.fill(); g.restore();
}
const WIPES = [[K.wipe1 - 0.2, 0.42], [K.wipe2 - 0.22, 0.5], [K.wipe3 - 0.2, 0.45], [K.wipe4 - 0.2, 0.45], [K.wipe5 - 0.2, 0.45]];

// ======================= text =======================
const CAPS = [
  [K.start, K.sting - 0.05, [['ONE ', INK], ['TINY ', RED], ['CUT.', INK]]],
  [K.sting - 0.05, K.decided, [['HE FELT THE ', INK], ['STING.', RED]]],
  [K.decided, K.attacking, [['AND DECIDED...', INK]]],
  [K.attacking, K.struck - 0.1, [['THE SAW WAS ', INK], ['ATTACKING.', RED]]],
  [K.struck - 0.1, K.bit - 0.1, [['SO HE ', INK], ['STRUCK BACK.', RED]]],
  [K.bit - 0.1, K.cutMouth, [['HE BIT THE BLADE.', INK]]],
  [K.cutMouth, K.furious, [['AND CUT ', INK], ['HIS OWN MOUTH.', RED]]],
  [K.furious, K.wrapped, [['FURIOUS.', RED]]],
  [K.wrapped, K.crush, [['HE WRAPPED AROUND IT...', INK]]],
  [K.crush, K.tighter, [['TO ', INK], ['CRUSH IT.', RED]]],
  [K.tighter, K.deeper, [['TIGHTER...', INK]]],
  [K.deeper, K.until, [['DEEPER.', RED]]],
  [K.until, K.wipe2 - 0.3, [['UNTIL HE WAS ', INK], ['GONE.', RED]]],
  [K.name, K.horseFx - 0.1, [['THERE\'S A NAME FOR THIS.', INK]]],
  [K.bat, K.nothing - 0.15, [['A TINY BAT ', INK], ['BITES.', RED]]],
  [K.nothing - 0.15, K.but, [['THE BITE IS ', INK], ['NOTHING.', RED]]],
  [K.but, K.runs, [['BUT THE HORSE ', INK], ['PANICS.', RED]]],
  [K.runs, K.collapses, [['AND RUNS. AND RUNS.', INK]]],
  [K.collapses, K.wipe3 - 0.25, [['UNTIL IT ', INK], ['COLLAPSES.', RED]]],
  [K.hurts, K.wipe4 - 0.2, [['THAT\'S WHAT ', INK], ['HURTS YOU.', RED]]],
  [K.everyday, K.rude, [['WE DO IT ', INK], ['EVERY DAY.', RED]]],
  [K.rude, K.fire, [['ONE ', INK], ['RUDE COMMENT.', RED]]],
  [K.fire, K.replay, [['YOU ', INK], ['FIRE BACK.', RED]]],
  [K.replay, K.argument, [['REPLAY IT ', INK], ['ALL NIGHT.', RED]]],
  [K.argument, K.turn, [['ONE SMALL ARGUMENT...', INK]]],
  [K.turn, K.time, [['TURNED INTO A ', INK], ['WAR.', RED]]],
  [K.gone2, K.something, [['GONE.', RED]]],
  [K.something, K.wipe5 - 0.2, [['OVER A ', INK], ['2-SECOND ', RED], ['THING.', INK]]],
  [K.next, K.remember, [['NEXT TIME SOMETHING ', INK], ['CUTS YOU,', RED]]],
  [K.remember, K.letGo, [['REMEMBER ', INK], ['THE SNAKE.', RED]]],
  [K.letGo, K.rule - 0.05, [['LET GO ', RED], ['OF THE SAW.', INK]]],
];
function caption(g, t) {
  for (const [t0, t1, a] of CAPS) { if (t < t0 || t >= t1) continue; const k = ss(t0, t0 + 0.1, t), pop = 1 + 0.1 * Math.exp(-(t - t0) * 12);
    g.save(); g.globalAlpha = k * (1 - ss(t1 - 0.06, t1, t)); g.translate(360, 922); g.scale(pop, pop); g.translate(-360, -922);
    g.fillStyle = 'rgba(237,230,214,0.9)'; g.beginPath(); g.roundRect(60, 888, 600, 68, 14); g.fill();
    words(g, a, 360, 938, 54, 570); g.restore(); }
}
function counterBox(g, t) {
  let label = null, val = '', col = RED;
  if (t < K.wipe1 || (t >= K.cut && t < K.wipe2 - 0.2)) { label = 'CUTS'; val = String(cutCount(t)); }
  else if (t >= K.runs && t < K.wipe3) { label = 'KM RUN'; val = (horseScroll(t) / 260).toFixed(1); col = INK; }
  else if (t >= K.replay && t < K.argument) { label = 'REPLAYS'; val = String(1 + Math.floor((t - K.replay) * 2.2 * 6)); }
  if (!label) return;
  const flash = t >= K.cut && t < K.cut + 0.3 ? 1 : 0;
  g.save(); const x = 230, y = 208, w = 260, h = 58; g.translate(360, y + h / 2); const p = 1 + 0.12 * flash; g.scale(p, p); g.translate(-360, -(y + h / 2));
  g.fillStyle = 'rgba(251,247,238,0.95)'; g.beginPath(); g.roundRect(x, y, w, h, 12); g.fill();
  inkLine(g, [[x, y + 6], [x, y + h - 6], [x + 6, y + h], [x + w - 6, y + h], [x + w, y + h - 6], [x + w, y + 6], [x + w - 6, y], [x + 6, y], [x, y + 6]], 3);
  g.font = '26px "Patrick Hand SC"'; g.textAlign = 'left'; g.fillStyle = INK; g.fillText(label, x + 18, y + 38);
  g.font = '36px "Permanent Marker"'; g.textAlign = 'right'; g.fillStyle = col; g.fillText(val, x + w - 16, y + 44); g.restore();
}
function plate(g, y0, h) { g.fillStyle = 'rgba(237,230,214,0.9)'; g.beginPath(); g.roundRect(56, y0, 608, h, 16); g.fill(); }
function bigLines(g, t) {
  g.textBaseline = 'alphabetic';
  if (t < K.wipe1 - 0.02) { const p = 1 + 0.12 * Math.exp(-t * 8); g.save(); g.translate(360, 320); g.scale(p, p); g.translate(-360, -320);
    plate(g, 280, 128); words(g, [['HE KILLED ', INK], ['HIMSELF.', RED]], 360, 338, 66, 580);
    const k2 = ss(1.3, 1.45, t); if (k2 > 0) { g.globalAlpha = k2; words(g, [['THE SAW ', INK], ['NEVER MOVED.', RED]], 360, 394, 50, 540); } g.restore(); }
  if (t >= K.rule && t < K.cta) { const k1 = ss(K.rule, K.rule + 0.2, t), k2 = ss(K.worth - 0.2, K.worth, t);
    g.save(); plate(g, 440, 140); g.globalAlpha = k1; words(g, [['NOT EVERY BATTLE', INK]], 360, 502, 64, 580, 'Permanent Marker'); g.globalAlpha = k2; words(g, [['IS ', INK], ['WORTH FIGHTING.', RED]], 360, 562, 54, 580, 'Permanent Marker'); g.restore(); }
  if (t >= K.cta) { const k = ss(K.cta, K.cta + 0.25, t); g.save(); g.globalAlpha = k; plate(g, 440, 140);
    words(g, [['SEND THIS TO SOMEONE', INK]], 360, 502, 58, 580, 'Permanent Marker'); words(g, [['WHO ', INK], ['NEEDS IT.', RED]], 360, 562, 58, 580, 'Permanent Marker'); g.restore(); }
}

// ======================= camera [zoom, cx, cy, shake] =======================
function cam(t) {
  const HEAD = [262, 712];
  if (t < K.wipe1) {
    if (t < 0.6) { const k = eio(clamp(t / 0.6)); return [lerp(2.7, 1.5, k), lerp(HEAD[0] + 20, 395, k), lerp(HEAD[1], 770, k), 4 * (1 - k)]; }
    if (t >= 1.5 && t < 2.32) { const k = clamp((t - 1.5) / 0.82); return [lerp(2.0, 2.15, k), 600, 790, 0]; } // the saw handle: perfectly still
    return [1.5 + 0.08 * ss(0.6, 2.6, t), 395, 770, 3 * Math.abs(Math.sin(t * 9))];
  }
  if (t < K.cut) { const hx = storyState(t).P[0][0]; return [1.75, clamp(hx - 40, 200, 470), 800, 0]; }
  if (t < K.sting) { const k = eout(clamp((t - K.cut) / 0.25)); return [lerp(1.75, 2.3, k), lerp(270, 285, k), lerp(780, 800, k), 0]; }
  if (t < K.decided) { const k = eout(clamp((t - K.sting) / 0.3)); return [lerp(2.3, 1.5, k), lerp(285, 300, k), lerp(800, 740, k), 6 * Math.exp(-(t - K.sting) * 6)]; }
  if (t < K.attacking) return [1.5 + 0.08 * ss(K.decided, K.attacking, t), 300, 660, 0];
  if (t < K.struck - 0.1) { const k = eout(clamp((t - K.attacking) / 0.25)); return [lerp(1.58, 1.8, k), 300, lerp(660, 580, k), 2 * Math.sin(t * 30) * k]; }
  if (t < K.bit - 0.2) { return [1.6, 300, 770, (t > K.struck + 0.1 && t < K.struck + 0.5) ? 7 : 0]; }
  if (t < K.cutMouth) { const k = eout(clamp((t - K.bit + 0.2) / 0.25)); return [lerp(1.6, 2.3, k), 290, 790, t > K.bit && t < K.bit + 0.4 ? 6 : 1.5]; }
  if (t < K.furious) return [2.6, 300, 820, 1]; // close: blood drips from the mouth
  if (t < K.wrapped) { const k = eout(clamp((t - K.furious) / 0.3)); return [lerp(2.6, 1.6, k), lerp(300, 250, k), lerp(820, 740, k), 4]; }
  if (t < K.tighter) { const k = eio(clamp((t - K.wrapped) / 1.0)); return [lerp(1.6, 1.4, k), lerp(250, 395, k), lerp(740, 770, k), 0]; }
  if (t < K.deeper) { const k = eout(clamp((t - K.tighter) / 0.3)); return [lerp(1.4, 1.75, k), lerp(395, 330, k), 740, 3]; }
  if (t < K.until) { const k = eout(clamp((t - K.deeper) / 0.25)); return [lerp(2.3, 2.5, k), 420, 820, 4]; }
  if (t < K.wipe2) { const k = eio(clamp((t - K.until) / 1.0)); return [lerp(1.8, 1.45, k), lerp(330, 395, k), lerp(780, 780, k), 0]; }
  if (t < K.name) { if (t < K.his) return [1.0 + 0.25 * ss(K.sawOne, K.sawOne + 0.4, t), 260, 600, 0]; if (t < K.rest) { const k = eout(clamp((t - K.his) / 0.25)); return [lerp(1.25, 1.35, k), lerp(260, 460, k), 600, 0]; } const k = eout(clamp((t - K.rest) / 0.4)); return [lerp(1.35, 1.0, k), lerp(460, 360, k), lerp(600, 640, k), 0]; }
  if (t < K.bat) return [1.0 + 0.06 * ss(K.name, K.bat, t), 360, 640, 0];
  if (t < K.bites) return [1.1, 420, 700, 0];
  if (t < K.nothing - 0.15) { const k = eout(clamp((t - K.bites) / 0.25)); return [lerp(1.1, 2.0, k), lerp(420, 470, k), lerp(700, 820, k), 0]; }
  if (t < K.but) return [2.4 + 0.2 * ss(K.nothing, K.but, t), 480, 830, 0];
  if (t < K.runs) { const k = eout(clamp((t - K.but) / 0.3)); return [lerp(2.4, 1.05, k), lerp(480, 380, k), lerp(830, 720, k), t > K.panics ? 5 : 0]; }
  if (t < K.collapses) return [1.05 + 0.08 * ss(K.runs, K.collapses, t), 360, 720, 3];
  if (t < K.wipe3) { const k = eout(clamp((t - K.collapses) / 0.4)); return [lerp(1.1, 1.25, k), lerp(360, 430, k), lerp(720, 800, k), 8 * Math.exp(-(t - K.collapses - 0.3) * 4) * (t > K.collapses + 0.3 ? 1 : 0)]; }
  if (t < K.wipe4) { if (t < K.big) return [1.1, 360, 400, 0]; if (t < K.hurts) { const k = eout(clamp((t - K.big) / 0.25)); return [1.1, 360, lerp(400, 600, k), 4 * Math.exp(-(t - K.big) * 4)]; } const k = eout(clamp((t - K.hurts) / 0.3)); return [lerp(1.1, 1.0, k), 360, lerp(600, 640, k), 0]; }
  if (t < K.rude) return [1.35 + 0.08 * ss(K.everyday, K.rude, t), 360, 640, 0];
  if (t < K.fire) { const k = eout(clamp((t - K.rude - 0.15) / 0.25)); return [lerp(1.0, 1.45, k), 360, lerp(600, 600, k), 0]; }
  if (t < K.replay) return [1.1, 360, 620, 4];
  if (t < K.argument) return [1.0 + 0.12 * ss(K.replay, K.argument, t), 360, 600, 0];
  if (t < K.time) { if (t < K.turn) return [1.15, 360, 680, 0]; return [1.05 + 0.15 * ss(K.turn, K.war, t), 360, 640, t > K.war ? 9 * Math.exp(-(t - K.war) * 3) : 3]; }
  if (t < K.wipe5) { if (t < K.something) return [1.12, 360, 560, t > K.gone2 && t < K.gone2 + 0.4 ? 6 : 0]; return [1.0 + 0.12 * ss(K.something, K.wipe5, t), 360, 600, 0]; }
  if (t < K.cuts) { const hx = endSnakeX(t); return [1.7, clamp(hx - 40, 200, 470), 800, 0]; }
  if (t < K.remember) { const k = eout(clamp((t - K.cuts) / 0.25)); return [lerp(1.7, 1.9, k), 290, 800, 0]; }
  if (t < K.letGo) { const k = eout(clamp((t - K.remember) / 0.35)); return [lerp(1.9, 1.3, k), lerp(290, 320, k), lerp(800, 680, k), 0]; }
  if (t < K.rule) { const k = eio(clamp((t - K.letGo) / 1.4)); return [lerp(1.3, 1.15, k), lerp(320, 420, k), lerp(680, 700, k), 0]; }
  return [1.15 + 0.08 * ss(K.rule, DUR, t), 440, 700, 0];
}
function endSnakeX(t) { return lerp(-90, 288, eout(clamp((t - K.wipe5) / (K.cuts - K.wipe5)))); }
function scene(g, t) {
  if (t < K.wipe2) return workshopScene(g, t);
  if (t < K.name) return scoreScene(g, t);
  if (t < K.wipe3) return horseScene(g, t);
  if (t < K.wipe4) return equationScene(g, t);
  if (t < K.wipe5) return lifeScene(g, t);
  return endScene(g, t);
}
function frame(g, t) {
  T = t;
  const [z, cx, cy, sh] = cam(t);
  g.setTransform(W / DW, 0, 0, H / DH, 0, 0); g.translate(360, 640); g.scale(z, z); g.translate(-cx + Math.sin(t * 61) * sh, -cy + Math.cos(t * 47) * sh);
  scene(g, t);
  g.setTransform(W / DW, 0, 0, H / DH, 0, 0);
  const hostile = t < K.wipe1 || (t >= K.attacking && t < K.gone) || (t >= K.panics && t < K.collapses) || (t >= K.turn && t < K.time);
  if (hostile) { const p = 0.5 + 0.5 * Math.sin(t * 9); const gr = g.createRadialGradient(360, 640, 420, 360, 640, 900); gr.addColorStop(0, 'rgba(200,40,42,0)'); gr.addColorStop(1, `rgba(200,40,42,${0.1 + 0.1 * p})`); g.fillStyle = gr; g.fillRect(0, 0, DW, DH); }
  const gr = g.createRadialGradient(360, 640, 380, 360, 640, 900); gr.addColorStop(0, 'rgba(120,95,60,0)'); gr.addColorStop(1, 'rgba(120,95,60,0.12)'); g.fillStyle = gr; g.fillRect(0, 0, DW, DH);
  for (const tf of [K.name, K.rude, K.fire, K.replay, K.argument, K.time]) if (t >= tf && t < tf + 0.12) { g.fillStyle = `rgba(255,252,244,${0.7 * (1 - (t - tf) / 0.12)})`; g.fillRect(0, 0, DW, DH); }
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
// ======================= sound cues (no SFX in the hook 0-3.5 s or the rule + CTA) =======================
window.events = (() => { const e = [];
  e.push({ t: K.wipe1 - 0.15, s: 'swipe', g: 0.5, pan: 0 });
  for (let i = 0; i < 3; i++) e.push({ t: K.start + 0.8 + i * 0.5, s: 'slither', g: 0.35, pan: -0.3 + i * 0.2 });
  e.push({ t: K.sting - 0.05, s: 'hiss', g: 0.7, pan: 0 });
  e.push({ t: K.attacking, s: 'hiss', g: 0.8, pan: 0, rate: 0.9 });
  e.push({ t: K.struck + 0.1, s: 'clang', g: 0.75, pan: 0.1 });
  e.push({ t: K.bit, s: 'clang', g: 0.7, pan: 0, rate: 0.9 }, { t: K.bit + 0.05, s: 'scrape', g: 0.5, pan: 0 });
  e.push({ t: K.cutMouth, s: 'drip', g: 0.45, pan: 0 });
  e.push({ t: K.wrapped, s: 'slither', g: 0.55, pan: 0.2, rate: 0.9 });
  e.push({ t: K.crush, s: 'creak', g: 0.55, pan: 0 });
  e.push({ t: K.tighter, s: 'scrape', g: 0.6, pan: 0 }, { t: K.deeper, s: 'scrape', g: 0.65, pan: 0.2, rate: 0.9 });
  e.push({ t: K.until + 0.2, s: 'heart', g: 0.5, pan: 0 });
  e.push({ t: K.gone, s: 'thud', g: 0.6, pan: 0 });
  e.push({ t: K.wipe2 - 0.15, s: 'swipe', g: 0.5, pan: 0 });
  e.push({ t: K.sawOne + 0.43, s: 'marker', g: 0.45, pan: -0.3 }, { t: K.reaction, s: 'tick', g: 0.5, pan: 0.3 });
  e.push({ t: K.name - 0.05, s: 'swipe', g: 0.4, pan: 0, rate: 1.2 }, { t: K.name, s: 'wind', g: 0.35, pan: 0 });
  e.push({ t: K.horseFx, s: 'marker', g: 0.5, pan: 0 });
  e.push({ t: K.bat - 0.05, s: 'flap', g: 0.55, pan: 0.4 }, { t: K.bites, s: 'nip', g: 0.5, pan: 0.2 });
  e.push({ t: K.panics - 0.05, s: 'neigh', g: 0.7, pan: 0 });
  e.push({ t: K.runs - 0.1, s: 'gallop', g: 0.7, pan: 0 });
  e.push({ t: K.collapses + 0.3, s: 'thud', g: 0.8, pan: 0, rate: 0.8 });
  e.push({ t: K.wipe3 - 0.15, s: 'swipe', g: 0.5, pan: 0 });
  e.push({ t: K.small, s: 'marker', g: 0.45, pan: -0.2 }, { t: K.big, s: 'boom', g: 0.6, pan: 0 }, { t: K.hurts, s: 'crack', g: 0.55, pan: 0 });
  e.push({ t: K.wipe4 - 0.15, s: 'swipe', g: 0.5, pan: 0 });
  e.push({ t: K.rude + 0.15, s: 'ding', g: 0.55, pan: 0.2 }, { t: K.fire, s: 'typing', g: 0.6, pan: 0 });
  e.push({ t: K.replay, s: 'clock', g: 0.45, pan: -0.3 });
  e.push({ t: K.war - 0.05, s: 'boom', g: 0.75, pan: 0 });
  e.push({ t: K.time + 0.05, s: 'drain', g: 0.45, pan: -0.2 }, { t: K.sleep + 0.05, s: 'drain', g: 0.45, pan: 0, rate: 0.9 }, { t: K.peace + 0.05, s: 'drain', g: 0.45, pan: 0.2, rate: 0.8 });
  e.push({ t: K.something + 0.3, s: 'tick', g: 0.5, pan: 0 });
  e.push({ t: K.wipe5 - 0.15, s: 'swipe', g: 0.5, pan: 0 });
  e.push({ t: K.next + 0.2, s: 'slither', g: 0.3, pan: -0.3 });
  e.push({ t: K.letGo + 0.3, s: 'slither', g: 0.35, pan: 0.3 });
  return e.sort((a, b) => a.t - b.t); })();
window.TL = K; window.DUR = DUR;
document.fonts.load('40px "Patrick Hand SC"').then(() => document.fonts.load('40px "Permanent Marker"')).then(() => { window.ready = true; });
