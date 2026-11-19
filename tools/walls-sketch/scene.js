// "We build our own walls" remake: chalk-sketch look, drawn procedurally on canvas.
// World units: head radius = 1, ground y = 0, y up. render(t) -> canvas 1080x1920.
export const W = 1080, H = 1920, FPS = 30, DUR = 14.2;
export const out = document.createElement('canvas'); out.width = W; out.height = H;
const ctx = out.getContext('2d');
const WHITE = '#f3f1ec', BLACK = '#050505', TEAR = '#6fd3ff';

// ---------- helpers ----------
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a, b, k) => a + (b - a) * k;
const ease = k => k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
const sm = (a, b, t) => { const k = clamp((t - a) / (b - a)); return k * k * (3 - 2 * k); };
function mulberry(a) { return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
let rand = mulberry(1);
const jit = r => (rand() - .5) * 2 * r;
let SC = 100; // px per unit for current camera
const px = v => v / SC; // px -> units

function path(pts, closed) {
  ctx.beginPath();
  if (pts.length < 3 || (pts.length <= 9 && !path.smooth)) { ctx.moveTo(...pts[0]); for (const p of pts.slice(1)) ctx.lineTo(...p); if (closed) ctx.closePath(); return; }
  if (false) { ctx.moveTo(...pts[0]); for (const p of pts.slice(1)) ctx.lineTo(...p); return; }
  ctx.moveTo(pts[0][0], pts[0][1]);
  const n = pts.length;
  for (let i = 1; i < n - (closed ? 0 : 1); i++) {
    const p = pts[i], q = pts[(i + 1) % n];
    ctx.quadraticCurveTo(p[0], p[1], (p[0] + q[0]) / 2, (p[1] + q[1]) / 2);
  }
  if (!closed) ctx.lineTo(...pts[n - 1]); else ctx.closePath();
}
// sketchy stroke: several jittered passes
function sk(pts, wpx = 5, opt = {}) {
  const { col = WHITE, passes = 2, j = 2.2, closed = false, alpha = 1 } = opt;
  ctx.save(); ctx.strokeStyle = col; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.globalAlpha = alpha;
  for (let p = 0; p < passes; p++) {
    const jj = px(j * (p ? 1.4 : 1));
    const q = pts.map(([x, y]) => [x + jit(jj), y + jit(jj)]);
    if (closed) { q.push([q[0][0] + jit(jj * 2), q[0][1] + jit(jj * 2)]); }
    ctx.lineWidth = px(wpx * (p ? .55 : 1) * (.85 + rand() * .3));
    path(q, false); ctx.stroke();
  }
  ctx.restore();
}
function fill(pts, col = BLACK) { ctx.save(); ctx.fillStyle = col; path(pts, true); ctx.fill(); ctx.restore(); }
function ell(cx, cy, rx, ry, n = 22, rot = 0, a0 = 0, a1 = Math.PI * 2) {
  const o = []; for (let i = 0; i <= n; i++) { const a = a0 + (a1 - a0) * i / n; const x = Math.cos(a) * rx, y = Math.sin(a) * ry; o.push([cx + x * Math.cos(rot) - y * Math.sin(rot), cy + x * Math.sin(rot) + y * Math.cos(rot)]); } return o;
}
function hatch(clipPts, ang, gapPx, wpx = 2, alpha = .55, col = WHITE) {
  ctx.save(); path(clipPts, true); ctx.clip();
  let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9; for (const [x, y] of clipPts) { x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); }
  const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2, R = Math.hypot(x1 - x0, y1 - y0) / 2 + .1, g = px(gapPx);
  const c = Math.cos(ang), s = Math.sin(ang);
  ctx.strokeStyle = col; ctx.globalAlpha = alpha; ctx.lineCap = 'round';
  for (let d = -R; d <= R; d += g * (.8 + rand() * .4)) {
    if (rand() < .18) continue;
    const l0 = -R * (.6 + rand() * .4), l1 = R * (.6 + rand() * .4);
    ctx.lineWidth = px(wpx * (.6 + rand() * .7));
    ctx.beginPath(); ctx.moveTo(cx + c * l0 - s * d, cy + s * l0 + c * d); ctx.lineTo(cx + c * l1 - s * d + jit(px(2)), cy + s * l1 + c * d + jit(px(2))); ctx.stroke();
  }
  ctx.restore();
}
const LW = () => clamp(SC * .055, 3.2, 13); // main line width in px

// ---------- characters ----------
// pose: {x, lean, tilt, kneel, armL:[a,e], armR:[a,e], face:{mouth, brows, look:[x,y], eyes, tear, turn}}
function rot(p, o, a) { const c = Math.cos(a), s = Math.sin(a); const dx = p[0] - o[0], dy = p[1] - o[1]; return [o[0] + dx * c - dy * s, o[1] + dx * s + dy * c]; }

function ground(x, w) {
  ctx.save(); const pts = ell(x, 0, w, .35, 24);
  ctx.globalAlpha = 1; hatch(pts, -.35, 7, 2.2, .5);
  ctx.restore();
}
function shoe(x, y, dir) { const p = ell(x + dir * .12, y + .12, .42, .17, 14); fill(p, BLACK); sk(p, LW() * .8, { closed: true }); }

function drawKid(P, girl) {
  const lw = LW();
  const kneel = P.kneel || 0;
  const hipY = lerp(3.3, 1.35, kneel), hx = P.x;
  const lean = P.lean || 0;
  // legs
  const legs = [-1, 1].map(sd => {
    const hip = [hx + sd * .33, hipY];
    if (kneel < .01) return [hip, [hx + sd * .38, 1.65], [hx + sd * .42, .12]];
    const knee = [hx + sd * .3 + lerp(0, .9, kneel) * (sd > 0 ? 1 : .6), lerp(1.65, .25, kneel)];
    const foot = [hx + sd * .4 - lerp(0, 1.1, kneel), lerp(.12, .15, kneel)];
    return [hip, knee, foot];
  });
  ground(hx, girl ? 1.6 : 1.8);
  for (const [i, L] of legs.entries()) {
    if (girl) { sk(L, lw * .9, {}); shoe(L[2][0], 0, i ? 1 : -1); }
    else {
      // trousers: thick dark leg with outline + hatch
      const wdt = .32; const pts = [];
      const off = (a, b, s) => { const dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy); return [-dy / l * s, dx / l * s]; };
      for (let k = 0; k < L.length; k++) { const a = L[Math.max(0, k - 1)], b = L[Math.min(L.length - 1, k + 1)]; const o = off(a, b, wdt); pts.push([L[k][0] + o[0], L[k][1] + o[1]]); }
      for (let k = L.length - 1; k >= 0; k--) { const a = L[Math.max(0, k - 1)], b = L[Math.min(L.length - 1, k + 1)]; const o = off(a, b, -wdt * .9); pts.push([L[k][0] + o[0], L[k][1] + o[1]]); }
      fill(pts); hatch(pts, 1.25, 9, 2, .38); sk(pts, lw * .9, { closed: true });
      shoe(L[L.length - 1][0], 0, i ? 1 : -1);
    }
  }
  // torso (pivot at hips)
  ctx.save();
  ctx.translate(hx, hipY); ctx.rotate(-lean); ctx.translate(-hx, -hipY);
  const shY = hipY + 2.35;
  let body;
  if (girl) body = [[hx - .6, shY - .25], [hx - .35, shY + .02], [hx + .35, shY + .02], [hx + .6, shY - .25], [hx + 1.05, hipY - .55], [hx - 1.05, hipY - .55]];
  else body = [[hx - .82, shY - .3], [hx - .5, shY + .02], [hx + .5, shY + .02], [hx + .82, shY - .3], [hx + .7, hipY + .02], [hx - .7, hipY + .02]];
  // arms behind? draw arms after body
  fill(body); hatch(body, 1.1, 8, 2.2, .45); sk(body, lw, { closed: true });
  // neck
  sk([[hx, shY - .05], [hx + (P.tilt || 0) * .3, shY + .55]], lw * 1.05);
  // arms
  const arm = (sd, [a, e]) => {
    const s0 = [hx + sd * (girl ? .5 : .74), shY - .12];
    const u = [s0[0] + Math.sin(a) * sd * 1.25, s0[1] - Math.cos(a) * 1.25];
    const a2 = a + e;
    const h = [u[0] + Math.sin(a2) * sd * 1.15, u[1] - Math.cos(a2) * 1.15];
    if (!girl) { // sleeve
      const sl = [[s0[0] - sd * .15, s0[1] + .12], [s0[0] + Math.sin(a) * sd * .6 + .22 * Math.cos(a), s0[1] - Math.cos(a) * .6 + .22 * Math.sin(a) * sd], [s0[0] + Math.sin(a) * sd * .6 - .22 * Math.cos(a), s0[1] - Math.cos(a) * .6 - .22 * Math.sin(a) * sd], [s0[0] + sd * .1, s0[1] - .35]];
      fill(sl); sk(sl, lw * .8, { closed: true });
    }
    sk([s0, u, h], lw * .95);
    // hand: small scribbled fist / fingers
    sk(ell(h[0], h[1], .14, .14, 8), lw * .7, { closed: true });
    return h;
  };
  const hL = arm(-1, P.armL || [.15, .05]), hR = arm(1, P.armR || [.15, .05]);
  // head
  const hc = [hx + (P.tilt || 0) * .45, shY + .55 + .95 - (P.down || 0) * .25];
  ctx.save(); ctx.translate(hc[0], hc[1]); ctx.rotate(-(P.tilt || 0));
  drawHead(P.face || {}, girl);
  ctx.restore();
  ctx.restore();
  return { hL, hR, head: hc };
}

function drawHead(F, girl) {
  const lw = LW();
  const turn = F.turn || 0; // -1..1 face direction (+ = viewer's right)
  if (girl) { // back hair mass
    const back = []; for (let i = 0; i <= 20; i++) { const a = Math.PI * (i / 20); back.push([Math.cos(a) * 1.45 + jit(.06), Math.sin(a) * 1.25 + .1]); }
    back.push([-1.5, -.9], [-1.25, -1.35], [-.7, -1.1], [.7, -1.1], [1.25, -1.35], [1.5, -.9]);
    fill(back); sk(back, lw * .8, { closed: true });
    for (let i = 0; i < 16; i++) { const a = Math.PI * (.05 + .9 * i / 15); const s = [Math.cos(a) * .4, .9]; sk([s, [Math.cos(a) * 1.0, Math.sin(a) * .9 + .2], [Math.cos(a) * 1.5 + jit(.1), -.4 - rand() * .9]], lw * .32, { passes: 1, j: 2.5 }); }
  }
  const face = ell(0, 0, 1, 1, 26);
  fill(face, WHITE); sk(face, lw, { closed: true, col: WHITE });
  ctx.save(); ctx.strokeStyle = BLACK; // inner outline subtle shading
  hatch(ell(.15 - turn * .3, -.1, 1, 1, 20), .7, 6, 1.6, .18, BLACK);
  ctx.restore();
  const fx = turn * .28;
  // eyes
  const eyes = F.eyes || 'open', look = F.look || [0, 0];
  for (const sd of [-1, 1]) {
    const ex = fx + sd * .38 * (1 - Math.abs(turn) * .25 * (sd * turn > 0 ? 0 : 1)), ey = .02;
    const rx = girl ? .27 : .25, ry = girl ? .3 : .27;
    if (eyes === 'closed') { sk(ell(ex, ey - .05, rx, .1, 10, 0, Math.PI, 2 * Math.PI), lw * .55, { col: BLACK }); continue; }
    const half = eyes === 'half' ? .55 : 1;
    const e = ell(ex, ey, rx, ry * half, 18);
    fill(e, WHITE); sk(e, lw * .55, { closed: true, col: BLACK });
    const pr = (girl ? .14 : .13) * (eyes === 'small' ? .7 : 1);
    const pp = ell(ex + look[0] * .1, ey + look[1] * .1 * half, pr, pr * Math.min(1, half * 1.3), 10);
    fill(pp, BLACK);
    fill(ell(ex + look[0] * .1 + .05, ey + look[1] * .1 + .05, .035, .035, 6), WHITE);
    if (girl) for (let k = 0; k < 3; k++) sk([[ex + sd * (.12 + k * .08), ey + ry * half * .92], [ex + sd * (.18 + k * .11), ey + ry * half * 1.25]], lw * .3, { col: BLACK, passes: 1 });
  }
  // brows
  const br = F.brows || 'none';
  if (br !== 'none') for (const sd of [-1, 1]) {
    const bx = fx + sd * .38, by = .42;
    let inner = 0, outer = 0;
    if (br === 'angry') { inner = -.14; outer = .12; } else if (br === 'sad') { inner = .14; outer = -.08; } else if (br === 'worried') { inner = .1; outer = -.02; }
    sk([[bx - sd * .2, by + inner], [bx + sd * .22, by + outer]], lw * .75, { col: BLACK });
  }
  // nose hint
  sk([[fx + .05, -.18], [fx + .1, -.28]], lw * .3, { col: BLACK, passes: 1 });
  // mouth
  const m = F.mouth || 'flat', my = -.55, mx = fx;
  if (m === 'yell') { const o = ell(mx, my - .02, .24, .2, 14); fill(o, BLACK); sk(o, lw * .45, { closed: true, col: BLACK }); fill(ell(mx, my - .14, .1, .05, 8), '#b04040'); }
  else if (m === 'frown') sk(ell(mx, my - .2, .2, .12, 10, 0, .15 * Math.PI, .85 * Math.PI), lw * .6, { col: BLACK });
  else if (m === 'sad') sk(ell(mx, my - .14, .14, .07, 8, 0, .1 * Math.PI, .9 * Math.PI), lw * .5, { col: BLACK });
  else if (m === 'quiver') sk([[mx - .17, my], [mx - .06, my + .04], [mx + .05, my - .02], [mx + .17, my + .02]], lw * .5, { col: BLACK });
  else if (m === 'o') { const o = ell(mx, my, .08, .1, 10); fill(o, BLACK); }
  else sk([[mx - .13, my], [mx + .13, my - .01]], lw * .5, { col: BLACK });
  // tear
  if (F.tear > 0) for (const sd of [-1, 1]) {
    const k = F.tear, ex = fx + sd * .4;
    const y = .0 - k * .75;
    ctx.save(); ctx.globalAlpha = clamp(k * 4) * (1 - sm(.85, 1, k));
    fill(ell(ex - sd * .06, y - .15, .065, .1, 10), TEAR);
    sk([[ex - sd * .02, -.2], [ex - sd * .06, y - .1]], lw * .35, { col: TEAR, passes: 1 });
    ctx.restore();
  }
  // hair (front)
  drawHair(girl, lw);
}
function drawHair(girl, lw) {
  // messy mop: pointed tufts round the crown, locks swept across the forehead
  const H = [];
  const sideY = girl ? -1.3 : -.1;
  H.push([-1.15, sideY]);
  if (girl) H.push([-1.42, -.75], [-1.3, -.2]);
  else H.push([-1.32, .05], [-1.22, .2]);
  const N = 11;
  for (let i = 0; i <= N; i++) {
    const a = Math.PI * (.97 - .94 * i / N);
    const r = 1.2 + (girl ? .1 : 0);
    H.push([Math.cos(a) * r, Math.sin(a) * r * 1.02 + .1]);
    if (i < N) { const am = Math.PI * (.97 - .94 * (i + .5) / N); const rt = r + .2 + .08 * Math.sin(i * 2.7); H.push([Math.cos(am - .06) * rt, Math.sin(am - .06) * rt + .16]); }
  }
  if (girl) H.push([1.3, -.2], [1.42, -.75]);
  else H.push([1.25, .2], [1.32, .02]);
  H.push([1.15, sideY]);
  if (girl) H.push([.98, -.2], [.98, .25]);
  // fringe: locks sweep from right to left, tips pointing down-left
  const fr = girl ? [[.92, .5], [.6, .62], [.66, .32], [.3, .56], [.32, .25], [-.05, .5], [-.08, .22], [-.42, .46], [-.5, .2], [-.8, .4]]
                  : [[1.0, .35], [.72, .55], [.78, .18], [.4, .5], [.45, .1], [.05, .45], [.08, .05], [-.32, .42], [-.35, .08], [-.7, .38], [-.82, .1], [-1.05, .28]];
  H.push(...fr);
  if (girl) H.push([-.98, .2], [-1.0, -.3]);
  fill(H);
  ctx.save(); path(H, true); ctx.clip();
  // flow lines: shrunken copies of the outline, broken into pieces
  const c = [.15, .95];
  for (let k = 0; k < 7; k++) {
    const s = .3 + k * .1;
    const pts = H.map(p => [c[0] + (p[0] - c[0]) * s + jit(.04), c[1] + (p[1] - c[1]) * s + jit(.04)]);
    let i = Math.floor(rand() * 4);
    while (i < pts.length - 2) { const len = 2 + Math.floor(rand() * 3); sk(pts.slice(i, i + len + 1), lw * (.2 + rand() * .15), { passes: 1, j: 1.2, alpha: .8 }); i += len + 1 + Math.floor(rand() * 2); }
  }
  // locks: curved strokes from the crown into each fringe tip
  for (let i = 0; i < fr.length; i += 2) {
    const tip = fr[i];
    path.smooth = true; sk([[.5 + jit(.2), 1.25], [tip[0] + .35, (1.25 + tip[1]) / 2 + .1], tip], lw * .3, { passes: 1, j: 1.4 }); path.smooth = false;
  }
  ctx.restore();
  sk(H, lw * .7, { closed: true, j: 1.6, passes: 2 });
}
// ---------- wall ----------
const BW = 1.0, BH = .5, WALL_X0 = -1.3, WALL_COLS = 2.6, SIDE = .7, ROWS = 21;
function brickList() {
  const b = [];
  for (let r = 0; r < ROWS; r++) {
    const off = r % 2 ? BW / 2 : 0;
    for (let x = -off; x < WALL_COLS - 1e-6; x += BW) {
      const x0 = Math.max(0, x), x1 = Math.min(WALL_COLS, x + BW);
      if (x1 - x0 < .08) continue;
      b.push({ r, x0: WALL_X0 + x0, x1: WALL_X0 + x1, y0: r * BH, y1: (r + 1) * BH, seed: b.length });
    }
  }
  return b;
}
const BRICKS = brickList();
function brickShape(b, dx = 0, dy = 0, a = 0) {
  const cx = (b.x0 + b.x1) / 2, cy = (b.y0 + b.y1) / 2, hw = (b.x1 - b.x0) / 2, hh = BH / 2;
  return [[-hw, -hh], [hw, -hh], [hw, hh], [-hw, hh]].map(p => { const q = rot(p, [0, 0], a); return [cx + q[0] + dx, cy + q[1] + dy]; });
}
function drawBrick(pts, lw) {
  fill(pts); hatch(pts, .8, 9, 2, .45); sk(pts, lw, { closed: true, j: 1.6 });
}
// rows: number of rows visible (float: last row pops in); crack: 0..1 ; fallK: 0..1 collapse
function drawWall(rows, crack = 0, fall = -1, crackAt = [-1.3, 4.4]) {
  const lw = LW() * .95;
  const nR = Math.floor(rows), part = rows - nR;
  // side face (3/4 depth) for full rows
  const topY = Math.min(rows, ROWS) * BH;
  if (fall < 0 && topY > 0) {
    const side = [[WALL_X0 + WALL_COLS, 0], [WALL_X0 + WALL_COLS + SIDE, .35], [WALL_X0 + WALL_COLS + SIDE, topY + .35], [WALL_X0 + WALL_COLS, topY]];
    fill(side); hatch(side, -1.0, 8, 2, .3);
    for (let r = 1; r <= Math.min(nR, ROWS); r++) sk([[WALL_X0 + WALL_COLS, r * BH], [WALL_X0 + WALL_COLS + SIDE, r * BH + .35]], lw * .8, { j: 1.4, passes: 1 });
    sk(side, lw, { closed: true });
    const topf = [[WALL_X0, topY], [WALL_X0 + WALL_COLS, topY], [WALL_X0 + WALL_COLS + SIDE, topY + .35], [WALL_X0 + SIDE, topY + .35]];
    fill(topf); sk(topf, lw, { closed: true });
  }
  for (const b of BRICKS) {
    if (b.r > nR) continue;
    let s = 1, dy = 0;
    if (b.r === nR) { if (part <= 0) continue; s = part; dy = (1 - ease(part)) * .6; }
    let pts = brickShape(b, 0, dy);
    if (fall >= 0) {
      const R = mulberry(b.seed * 7 + 3);
      const delay = (ROWS - b.r) / ROWS * .35 + R() * .1;
      const k = clamp((fall - delay) / (1 - delay));
      const tgt = PILE[b.seed];
      const kk = k * k;
      const cx = (b.x0 + b.x1) / 2, cy = (b.y0 + b.y1) / 2;
      const x = lerp(cx, tgt[0], ease(k)), y = lerp(cy, tgt[1], kk) + Math.sin(k * Math.PI) * .3 * R();
      const a = lerp(0, tgt[2], k);
      pts = brickShape(b, x - cx, y - cy, a);
      if (k > .02 && k < .98) for (let i = 0; i < 2; i++) { const d = [x + jit(.6), y + jit(.4)]; sk([d, [d[0] + jit(.05), d[1] + jit(.05)]], 3, { passes: 1, alpha: .6 }); }
    }
    if (s < 1) { ctx.save(); ctx.globalAlpha = clamp(s * 2); drawBrick(pts, lw); ctx.restore(); }
    else drawBrick(pts, lw);
  }
  if (crack > 0 && fall < 0) {
    const R = mulberry(77); let p = crackAt.slice(); const segs = [];
    for (let i = 0; i < 18; i++) { const q = [p[0] + .15 + R() * .3, p[1] + (R() - .5) * .8]; segs.push([p, q]); if (R() < .35) segs.push([q, [q[0] + R() * .3, q[1] + (R() - .3) * .7]]); p = q; }
    const n = Math.floor(segs.length * crack);
    for (let i = 0; i < n; i++) sk(segs[i], LW() * .7, { col: '#ffffff', passes: 1 });
    // flying chips
    for (let i = 0; i < 6 * crack; i++) { const c = [crackAt[0] - .2 - R() * .8 * crack, crackAt[1] + (R() - .5) * 1.2]; fill(ell(c[0], c[1], .06, .05, 6), WHITE); }
  }
}
// rubble pile targets
const PILE = (() => {
  const R = mulberry(9); const out = [];
  const n = BRICKS.length;
  for (let i = 0; i < n; i++) {
    const layer = Math.floor(Math.pow(R(), .8) * 6);
    const spread = 2.4 - layer * .36;
    const x = .1 + (R() - .5) * 2 * spread;
    const y = .22 + layer * .4 + R() * .08;
    out[BRICKS[i].seed] = [x, Math.max(.2, y), (R() - .5) * 1.6];
  }
  return out;
})();
function drawRubble() { const lw = LW() * .95; const order = BRICKS.slice().sort((a, b) => PILE[a.seed][1] - PILE[b.seed][1]); for (const b of order) { const t = PILE[b.seed]; const cx = (b.x0 + b.x1) / 2, cy = (b.y0 + b.y1) / 2; drawBrick(brickShape(b, t[0] - cx, t[1] - cy, t[2]), lw); } }

// ---------- camera ----------
function cam(cx, cy, sc) { SC = sc; ctx.setTransform(sc, 0, 0, -sc, W / 2 - cx * sc, H / 2 + cy * sc); }

// ---------- poses ----------
const BOY_X = -3.4, GIRL_X = 3.3;
const yellArm = [.95, -.35];
function boyWide(t) {
  const beat = Math.floor(t / .5), ph = (t % .5) / .5;
  const yelling = Math.sin(t * 6.2) > -.3;
  return { x: BOY_X, lean: .07 + .04 * Math.sin(t * 6), tilt: -.05, armL: [.2, .1], armR: beat % 2 ? yellArm : [.55, .3],
    face: { turn: .6, look: [1, 0], brows: 'angry', mouth: yelling ? 'yell' : 'frown' } };
}
function girlWide(t) {
  const flinch = Math.max(0, Math.sin(t * 6.2)) * .05;
  return { x: GIRL_X, lean: -.06 - flinch, tilt: .08, armL: [.18, .05], armR: [.18, .05],
    face: { turn: -.5, look: t < 1.5 ? [-1, .1] : [-.6, -.8], brows: 'sad', mouth: t < 1.5 ? 'o' : 'sad', eyes: 'open' } };
}

// ---------- render ----------
export function render(t) {
  rand = mulberry(Math.floor(t * 12) * 131 + 7); // line boil at 12 fps
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = BLACK; ctx.fillRect(0, 0, W, H);
  if (t < 3.0) { // S1 wide: wall rises between them
    const k = t / 3.0; cam(0, 4.6, lerp(92, 104, k));
    const rows = 1 + 19.5 * Math.pow(clamp(t / 2.85), .9);
    drawKid(boyWide(t), false); drawKid(girlWide(t), true);
    drawWall(rows);
  } else if (t < 5.5) { // S2 girl beside the wall, starts to cry
    const k = (t - 3) / 2.5; cam(3.05, 4.3, lerp(196, 212, k));
    drawWall(ROWS);
    const cry = sm(3.9, 4.3, t);
    drawKid({ x: GIRL_X, lean: -.03, tilt: lerp(.05, -.12, cry), down: cry, armL: [.15, .1], armR: [.15, .1],
      face: { turn: -.35, look: cry > .5 ? [-.2, -1] : [-1, -.2], brows: 'sad', mouth: cry > .5 ? 'quiver' : 'sad', eyes: cry > .7 ? 'half' : 'open', tear: cry > 0 ? clamp((t - 4.1) / 1.3) : 0 } }, true);
  } else if (t < 7.5) { // S3 boy beside the wall, still yelling, then sulks
    const k = (t - 5.5) / 2; cam(-3.15, 4.3, lerp(196, 210, k));
    drawWall(ROWS);
    const yell = t < 6.4;
    drawKid({ x: BOY_X, lean: yell ? .08 : 0, tilt: yell ? -.04 : .03, armL: yell ? [.3, .2] : [.12, .1], armR: yell ? [.6, .4] : [.12, .1],
      face: { turn: .5, look: [1, yell ? .2 : -.1], brows: 'angry', mouth: yell && Math.sin(t * 9) > -.4 ? 'yell' : 'frown' } }, false);
  } else if (t < 9.0) { // S4 close-up: anger turns into doubt
    const k = (t - 7.5) / 1.5; cam(-2.95, 6.75, lerp(380, 400, k));
    drawWall(ROWS);
    const soft = sm(8.1, 8.6, t);
    drawKid({ x: BOY_X, tilt: lerp(.02, .06, soft), armL: [.12, .1], armR: [.12, .1],
      face: { turn: .45, look: soft > .5 ? [.8, -.5] : [1, 0], brows: soft > .5 ? 'sad' : 'angry', mouth: soft > .5 ? 'sad' : 'frown', eyes: soft > .5 ? 'open' : 'half' } }, false);
  } else if (t < 10.75) { // S5/S6 he pushes; the wall cracks and falls
    cam(-2.25, 4.4, 196);
    const crack = sm(9.35, 9.95, t), fall = t >= 10.0 ? clamp((t - 10.0) / .75) : -1;
    const step = sm(9.0, 9.35, t);
    const P = { x: lerp(BOY_X, -2.55, step), lean: .1 * step, armL: [.15, .1], armR: [lerp(.2, 1.55, step), lerp(.1, -.05, step)],
      face: { turn: .5, look: [1, -.2], brows: 'worried', mouth: fall >= 0 ? 'o' : 'quiver' } };
    drawWall(ROWS, crack, fall, [-1.3, 4.45]);
    drawKid(P, false);
  } else if (t < 12.0) { // S7 close-up: he looks at the rubble
    const k = (t - 10.75) / 1.25; cam(-2.65, 6.75, lerp(380, 405, k));
    drawKid({ x: -2.55, tilt: .1, down: .3, armL: [.12, .1], armR: [.12, .1],
      face: { turn: .5, look: [.6, -1], brows: 'sad', mouth: 'sad', tear: t > 11.2 ? clamp((t - 11.2) / 1.2) * .6 : 0 } }, false);
  } else { // S8 wide: alone by the rubble, sinks to his knees
    const k = (t - 12) / 2.2; cam(-.4, 3.9, lerp(118, 132, k));
    drawRubble();
    const kn = sm(12.5, 13.3, t);
    drawKid({ x: -2.2, kneel: kn, lean: .25 * kn, tilt: .15 * kn, down: kn, armL: [lerp(.12, .6, kn), lerp(.1, .5, kn)], armR: [lerp(.12, .7, kn), lerp(.1, .4, kn)],
      face: { turn: .4, look: [.5, -1], brows: 'sad', mouth: 'sad', eyes: kn > .6 ? 'closed' : 'open' } }, false);
  }
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  // chalk grain
  const g = mulberry(Math.floor(t * 12) + 99);
  ctx.fillStyle = 'rgba(0,0,0,.25)';
  for (let i = 0; i < 900; i++) ctx.fillRect(g() * W, g() * H, 2, 2);
  const fo = sm(13.85, 14.2, t); if (fo > 0) { ctx.fillStyle = `rgba(0,0,0,${fo})`; ctx.fillRect(0, 0, W, H); }
  return out;
}
