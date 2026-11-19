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
// ---------- 3D camera (perspective, like the ref's 3/4 views) ----------
const CAM = { pos: [0, 5, 20], r: [1, 0, 0], u: [0, 1, 0], f3: [0, 0, -1], f: 1500 };
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const crs = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const nrm = a => { const l = Math.hypot(...a); return [a[0] / l, a[1] / l, a[2] / l]; };
function cam3(pos, at, f) {
  const fw = nrm(sub(at, pos)), r = nrm(crs(fw, [0, 1, 0])), u = crs(r, fw);
  Object.assign(CAM, { pos, r, u, f3: fw, f });
}
function P3(p) { const d = sub(p, CAM.pos); const z = dot(d, CAM.f3); return [W / 2 + CAM.f * dot(d, CAM.r) / z, H / 2 - CAM.f * dot(d, CAM.u) / z, z]; }
function screen() { SC = 1; ctx.setTransform(1, 0, 0, 1, 0, 0); }
// stand a 2D character at ground point (x, 0, z), facing the camera
function placeKid(x, z, ay = 5) { const [sx, sy, dz] = P3([x, ay, z]); const s = CAM.f / dz; SC = s; ctx.setTransform(s, 0, 0, -s, sx - x * s, sy + ay * s); }
const lwAt = z => clamp(CAM.f / z * .05, 1.6, 12);

// ---------- wall: a long brick wall running away from the camera between them ----------
const BL = 1.0, BH = .5, ROWS = 21, WX0 = -1.3, WX1 = 1.3, WZ0 = -1.2, WZ1 = 1.6, DEPTH = .5;
// faces: E = near end (z = WZ1), L = boy side (x = WX0), R = girl side (x = WX1)
function faceBricks(face) {
  const len = face === 'E' ? WX1 - WX0 : WZ1 - WZ0, o = [];
  for (let r = 0; r < ROWS; r++) {
    const off = (r + (face === 'E' ? 1 : 0)) % 2 ? BL / 2 : 0;
    for (let u = -off; u < len - 1e-6; u += BL) {
      const u0 = Math.max(0, u), u1 = Math.min(len, u + BL);
      if (u1 - u0 < .08) continue;
      o.push({ face, r, u0, u1 });
    }
  }
  return o;
}
// face coords (u along the face, y up) -> world
function F3(face, u, y, inset = 0) {
  if (face === 'E') return [WX0 + u, y, WZ1 - inset];
  if (face === 'L') return [WX0 + inset, y, WZ1 - u];
  return [WX1 - inset, y, WZ1 - u];
}
const FACES = { E: faceBricks('E'), L: faceBricks('L'), R: faceBricks('R') };
const NORM = { E: [0, 0, 1], L: [-1, 0, 0], R: [1, 0, 0] };
function faceVisible(face) { const c = F3(face, .5, 3); return dot(NORM[face], sub(CAM.pos, c)) > 0; }
function quad(face, u0, u1, y0, y1) { return [F3(face, u0, y0), F3(face, u1, y0), F3(face, u1, y1), F3(face, u0, y1)].map(P3); }
function drawQuad(q, lw, hat = .45) { const p = q.map(v => [v[0], v[1]]); fill(p); if (hat) hatch(p, .8, 9, 2, hat); sk(p, lw, { closed: true, j: 1.4 }); }
// rows: visible rows (float, last one drops in); crack 0..1 at face-L point; fall 0..1 collapse
function drawWall(rows, crack = 0, fall = -1, crackAt = [3.6, 4.4]) {
  screen();
  const nR = Math.floor(rows), part = rows - nR, topY = Math.min(rows, ROWS) * BH;
  if (fall >= 0) { drawFalling(fall); return; }
  for (const face of ['L', 'R', 'E']) {
    if (!faceVisible(face)) continue;
    for (const b of FACES[face]) {
      if (b.r > nR) continue;
      let dy = 0, al = 1;
      if (b.r === nR) { if (part <= 0) continue; al = clamp(part * 2); dy = (1 - ease(part)) * .6; }
      const q = quad(face, b.u0, b.u1, b.r * BH + dy, (b.r + 1) * BH + dy);
      const z = q[0][2]; ctx.save(); ctx.globalAlpha = al; drawQuad(q, lwAt(z) * 1.1); ctx.restore();
    }
  }
  // top of the wall when the camera is above it
  if (CAM.pos[1] > topY && nR > 0) {
    const top = [[WX0, topY, WZ1], [WX1, topY, WZ1], [WX1, topY, WZ0], [WX0, topY, WZ0]].map(P3);
    const p = top.map(v => [v[0], v[1]]); fill(p); sk(p, lwAt(top[0][2]), { closed: true, j: 1.4 });
  }
  if (crack > 0) {
    const R = mulberry(77); let p = crackAt.slice(); const segs = [];
    for (let i = 0; i < 16; i++) { const q = [p[0] + (R() - .5) * .9, p[1] + (i % 2 ? .35 : -.35) + (R() - .5) * .5]; segs.push([p, q]); if (R() < .4) segs.push([q, [q[0] + (R() - .5) * .8, q[1] + (R() - .5) * .8]]); p = R() < .5 ? q : crackAt.map((v, k) => v + (R() - .5) * (k ? 1.4 : 1.2)); }
    const n = Math.floor(segs.length * crack);
    for (let i = 0; i < n; i++) { const a = P3(F3('L', segs[i][0][0], segs[i][0][1], -.01)), b = P3(F3('L', segs[i][1][0], segs[i][1][1], -.01)); sk([[a[0], a[1]], [b[0], b[1]]], lwAt(a[2]) * .9, { col: '#ffffff', passes: 1 }); }
    for (let i = 0; i < 8 * crack; i++) { const c = P3(F3('L', crackAt[0] + (R() - .5) * 1.4, crackAt[1] + (R() - .5) * 1.4, -.3 - R() * crack)); fill(ell(c[0], c[1], 4 + R() * 4, 3 + R() * 3, 6), WHITE); }
  }
}
// ---------- bricks as little 3D boxes (falling + rubble) ----------
function drawBox(c, yaw, roll, pitch = 0) {
  const hx = BL / 2, hy = BH / 2, hz = DEPTH / 2;
  const cy = Math.cos(yaw), sy = Math.sin(yaw), cr = Math.cos(roll), sr = Math.sin(roll), cp = Math.cos(pitch), sp = Math.sin(pitch);
  const T = ([x, y, z]) => { let a = [x * cr - y * sr, x * sr + y * cr, z]; a = [a[0], a[1] * cp - a[2] * sp, a[1] * sp + a[2] * cp]; return [a[0] * cy + a[2] * sy, a[1], -a[0] * sy + a[2] * cy]; };
  const V = []; for (const x of [-hx, hx]) for (const y of [-hy, hy]) for (const z of [-hz, hz]) { const q = T([x, y, z]); V.push([c[0] + q[0], c[1] + q[1], c[2] + q[2]]); }
  const F = [[0, 1, 3, 2, [-1, 0, 0]], [4, 6, 7, 5, [1, 0, 0]], [0, 4, 5, 1, [0, -1, 0]], [2, 3, 7, 6, [0, 1, 0]], [0, 2, 6, 4, [0, 0, -1]], [1, 5, 7, 3, [0, 0, 1]]];
  const lw = lwAt(dot(sub(c, CAM.pos), CAM.f3));
  for (const f of F) {
    const n = T(f[4]); const fc = [0, 1, 2, 3].map(i => V[f[i]]);
    const mid = fc.reduce((a, v) => [a[0] + v[0] / 4, a[1] + v[1] / 4, a[2] + v[2] / 4], [0, 0, 0]);
    if (dot(n, sub(CAM.pos, mid)) <= 0) continue;
    const p = fc.map(v => { const q = P3(v); return [q[0], q[1]]; });
    fill(p); if (Math.abs(n[1]) < .5) hatch(p, .8, 8, 1.8, .35); sk(p, lw, { closed: true, j: 1.2, passes: 1 });
  }
}
// falling bricks come from the faces the boy sees (L and E)
const FALLERS = [...FACES.L, ...FACES.E].map((b, i) => {
  const R = mulberry(i * 13 + 5);
  const c = F3(b.face, (b.u0 + b.u1) / 2, (b.r + .5) * BH, DEPTH / 2);
  const layer = Math.floor(Math.pow(R(), .7) * 5), spread = 1 - layer * .17;
  const ang = R() * Math.PI * 2, rad = Math.sqrt(R()) * spread;
  const tgt = [.6 + Math.cos(ang) * rad * 4.2, .25 + layer * .42 + R() * .05, .2 + Math.sin(ang) * rad * 2.6];
  return { b, c, yaw0: b.face === 'E' ? 0 : Math.PI / 2, tgt, yaw1: (R() - .5) * 3, roll1: (R() - .5) * .9, pitch1: (R() - .5) * .5, delay: (ROWS - b.r) / ROWS * .3 + R() * .12, spin: R() };
});
function fallState(f, k) {
  const kk = ease(k), x = lerp(f.c[0], f.tgt[0], kk), z = lerp(f.c[2], f.tgt[2], kk), y = lerp(f.c[1], f.tgt[1], k * k) + Math.sin(k * Math.PI) * .5 * f.spin;
  return [[x, y, z], lerp(f.yaw0, f.yaw0 + f.yaw1, k), f.roll1 * k + Math.sin(k * Math.PI) * f.spin * 1.2, f.pitch1 * k];
}
function drawFalling(fall) {
  screen();
  const st = FALLERS.map(f => fallState(f, clamp((fall - f.delay) / (1 - f.delay))));
  st.sort((a, b) => dot(sub(b[0], CAM.pos), CAM.f3) - dot(sub(a[0], CAM.pos), CAM.f3));
  for (const s of st) drawBox(...s);
  const R = mulberry(Math.floor(fall * 40));
  for (let i = 0; i < 26 * (1 - fall); i++) { const c = P3([WX0 - .2 - R() * 1.5, R() * 9, WZ1 - R() * 7]); fill(ell(c[0], c[1], 2 + R() * 4, 2 + R() * 3, 6), WHITE); }
}
function drawRubble() { drawFalling(1); }

// ---------- poses ----------
const BOY_X = -3.6, GIRL_X = 3.6;
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
  if (t < 3.0) { // S1 wide, slightly high: the wall rises between them
    const k = t / 3.0;
    cam3([-1.6, 7.5, lerp(27, 24, k)], [0, 5.6, 0], 1900);
    const rows = 1 + 19.5 * Math.pow(clamp(t / 2.85), .9);
    drawWall(rows);
    placeKid(BOY_X, 0); drawKid(boyWide(t), false);
    placeKid(GIRL_X, 0); drawKid(girlWide(t), true);
  } else if (t < 5.5) { // S2 her side: the wall fills the left of frame, she leans on it and cries
    const k = (t - 3) / 2.5;
    cam3([lerp(5.6, 5.3, k), 5.0, lerp(8.8, 8.2, k)], [2.0, 3.7, -.3], 1300);
    drawWall(ROWS);
    const cry = sm(3.9, 4.3, t), gx = 2.65;
    placeKid(gx, -.3);
    drawKid({ x: gx, lean: lerp(0, -.08, cry), tilt: lerp(0, -.26, cry), down: cry, armL: [.12, .1], armR: [.12, .1],
      face: { turn: -.15, look: cry > .5 ? [-.2, -1] : [-.8, -.1], brows: 'sad', mouth: cry > .5 ? 'quiver' : 'sad', eyes: cry > .7 ? 'half' : 'open', tear: cry > 0 ? clamp((t - 4.1) / 1.3) : 0 } }, true);
  } else if (t < 7.5) { // S3 his side: wall on the right, he shouts at it
    const k = (t - 5.5) / 2;
    cam3([lerp(-6.2, -5.9, k), 5.4, lerp(9.8, 9.2, k)], [-2.1, 3.7, -.3], 1500);
    drawWall(ROWS);
    const yell = t < 6.4;
    placeKid(-2.9, -.3);
    drawKid({ x: -2.9, lean: yell ? .06 : 0, tilt: yell ? .05 : .03, armL: yell ? [.3, .2] : [.12, .1], armR: yell ? [.35, .25] : [.12, .1],
      face: { turn: .45, look: [1, yell ? .5 : .2], brows: 'angry', mouth: yell && Math.sin(t * 9) > -.4 ? 'yell' : 'frown' } }, false);
  } else if (t < 9.0) { // S4 close-up: head fills the frame, wall at the right edge
    const k = (t - 7.5) / 1.5;
    cam3([lerp(-3.7, -3.6, k), 7.0, lerp(2.9, 2.6, k)], [-2.2, 6.3, -.3], 1100);
    drawWall(ROWS);
    const soft = sm(8.1, 8.6, t);
    placeKid(-2.5, -.3, 7);
    drawKid({ x: -2.5, tilt: lerp(.03, .07, soft), armL: [.12, .1], armR: [.12, .1],
      face: { turn: .35, look: soft > .5 ? [.8, -.5] : [1, .1], brows: soft > .5 ? 'sad' : 'angry', mouth: soft > .5 ? 'sad' : 'frown', eyes: soft > .5 ? 'open' : 'half' } }, false);
  } else if (t < 10.75) { // S5/S6 he pushes; the wall cracks and falls
    cam3([-6.4, 5.4, 10.4], [-1.9, 3.7, -.3], 1450);
    const crack = sm(9.35, 9.95, t), fall = t >= 10.0 ? clamp((t - 10.0) / .75) : -1;
    const step = sm(9.0, 9.35, t), bx = lerp(-2.9, -2.2, step);
    drawWall(ROWS, crack, fall, [1.9, 5.0]);
    placeKid(bx, -.3);
    drawKid({ x: bx, lean: .1 * step, armL: [.15, .1], armR: [lerp(.2, 1.5, step), lerp(.1, -.05, step)],
      face: { turn: .45, look: [1, -.2], brows: 'worried', mouth: fall >= 0 ? 'o' : 'quiver' } }, false);
  } else if (t < 12.0) { // S7 close-up: the wall is gone, he looks down at it
    const k = (t - 10.75) / 1.25;
    cam3([-2.9, 6.9, lerp(3.0, 2.7, k)], [-2.4, 6.2, -.3], 1100);
    placeKid(-2.2, -.3, 7);
    drawKid({ x: -2.2, tilt: .1, down: .3, armL: [.12, .1], armR: [.12, .1],
      face: { turn: .35, look: [.6, -1], brows: 'sad', mouth: 'sad', tear: t > 11.2 ? clamp((t - 11.2) / 1.2) * .6 : 0 } }, false);
  } else { // S8 far wide: alone by the rubble, sinks to his knees
    const k = (t - 12) / 2.2;
    cam3([-1.5, 6.5, lerp(20, 18.5, k)], [-.5, 4.3, 0], 1050);
    drawRubble();
    const kn = sm(12.5, 13.3, t), bx = -4.4;
    placeKid(bx, .4);
    drawKid({ x: bx, kneel: kn, lean: .25 * kn, tilt: .15 * kn, down: kn, armL: [lerp(.12, .6, kn), lerp(.1, .5, kn)], armR: [lerp(.12, .7, kn), lerp(.1, .4, kn)],
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
