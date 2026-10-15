// "Temporal sculpture" opening: a hand built from ring slices (contour language), its predicted ghost arriving first,
// a teal wire grid that bends around the red touch point. Palette (PDF): bone white = movement, teal = form/prediction,
// red = touch/surprise only, near-black = space.
import * as THREE from 'three';
import {LineSegments2} from 'three/addons/lines/LineSegments2.js';
import {LineSegmentsGeometry} from 'three/addons/lines/LineSegmentsGeometry.js';
import {LineMaterial} from 'three/addons/lines/LineMaterial.js';

const W = 1080, H = 1920, DUR = 4.0, LEAD = 0.55;
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const sm = x => { x = clamp(x); return x * x * (3 - 2 * x); };
const lerp = (a, b, t) => a + (b - a) * t;
const WHITE = [0.91, 0.89, 0.82], TEAL = [0.16, 0.95, 0.80], RED = [1.0, 0.24, 0.19];

const renderer = new THREE.WebGLRenderer({antialias: true, preserveDrawingBuffer: true});
renderer.setPixelRatio(1); renderer.setSize(W, H); renderer.setClearColor(0x04070a, 1);
document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(38, W / H, 0.1, 500);
const res = new THREE.Vector2(W, H);

function lineLayer(width, opacity) {
  const g = new LineSegmentsGeometry();
  const m = new LineMaterial({linewidth: width, vertexColors: true, transparent: true, opacity, depthTest: false, depthWrite: false, blending: THREE.AdditiveBlending, resolution: res});
  const o = new LineSegments2(g, m); o.frustumCulled = false; scene.add(o); return o;
}
const glow = {hand: lineLayer(5, 0.16), ghost: lineLayer(6, 0.2), trail: lineLayer(4, 0.14), grid: lineLayer(3, 0.4)};
const core = {hand: lineLayer(1.5, 1), ghost: lineLayer(1.4, 0.95), trail: lineLayer(1.1, 0.7), grid: lineLayer(1.2, 0.85), path: lineLayer(1.8, 0.9)};
function setLines(layers, pos, col) { for (const l of layers) { l.geometry.setPositions(pos); l.geometry.setColors(col); } }

// ---- target (flat red ellipse, tilted so it reads as a spatial marker, not a portal) ----
const TARGET = new THREE.Vector3(7, 12, 0);
const tgt = new THREE.Group(); tgt.position.copy(TARGET); tgt.rotation.y = -0.75; scene.add(tgt);
const mk = (geo, op) => new THREE.Mesh(geo, new THREE.MeshBasicMaterial({color: 0xff3d30, transparent: true, opacity: op, depthTest: false, blending: THREE.AdditiveBlending}));
const tRing = mk(new THREE.RingGeometry(1.9, 2.35, 64), 1), tCore = mk(new THREE.CircleGeometry(0.8, 48), 1), tHalo = mk(new THREE.RingGeometry(2.5, 3.6, 64), 0.08);
tgt.add(tRing, tCore, tHalo);

// ---- hand skeleton -> ring slices ----
const AX = new THREE.Vector3(1, 0, 0), Zl = new THREE.Vector3(0, 0, 1);
function ringsAlong(out, p, d, L, rU0, rU1, rV0, rV1, U, spacing, fadeFn) {
  const n = Math.max(2, Math.round(L / spacing)), V = new THREE.Vector3().crossVectors(d, U).normalize();
  const rings = [];
  for (let k = 0; k <= n; k++) {
    const s = k / n, c = p.clone().addScaledVector(d, L * s), rU = lerp(rU0, rU1, s), rV = lerp(rV0, rV1, s);
    out.push({c, rU, rV, U, V, f: fadeFn ? fadeFn(s) : 1});
  }
}
function buildHand(t) {
  const s = sm((t - 0.1) / 2.6);              // openness grows as the hand reaches
  const rings = [];
  const sp = 0.2;
  // forearm (x from -62 to 0), then palm (0..9.5)
  ringsAlong(rings, new THREE.Vector3(-24, 0, 0), AX, 24, 3.6, 2.7, 2.6, 2.0, Zl, 0.3, u => 0.0 + 1.0 * Math.pow(u, 1.3));
  ringsAlong(rings, new THREE.Vector3(0, 0, 0), AX, 9.5, 2.7, 3.7, 2.0, 1.7, Zl, 0.22, null);
  // fingers: base z offsets, lengths, radii, spread, flex profile
  const F = [
    {z: 3.1, len: [4.0, 2.5, 2.0], r: 0.95, sp: 0.16, k: 0.9},
    {z: 1.05, len: [4.5, 2.9, 2.2], r: 1.0, sp: 0.02, k: 1.0},
    {z: -1.05, len: [4.2, 2.7, 2.1], r: 0.95, sp: -0.14, k: 1.1},
    {z: -3.0, len: [3.3, 2.0, 1.8], r: 0.8, sp: -0.32, k: 1.25}];
  F.forEach((f, i) => {
    const open = 0.25 + 0.75 * s, ph = Math.sin(t * 3.2 + i * 0.9) * 0.05;
    const flex = [lerp(0.55, 0.06, open) * f.k + ph, lerp(0.85, 0.12, open) * f.k + ph, lerp(0.55, 0.08, open) * f.k];
    let p = new THREE.Vector3(9.4, 0.0, f.z), d = new THREE.Vector3(Math.cos(f.sp), 0, Math.sin(f.sp)).normalize();
    const lat = new THREE.Vector3(-Math.sin(f.sp), 0, Math.cos(f.sp));
    let r0 = f.r;
    f.len.forEach((L, j) => {
      d.applyAxisAngle(lat, -flex[j]);
      const U = lat.clone().sub(d.clone().multiplyScalar(lat.dot(d))).normalize(), r1 = r0 * 0.86;
      ringsAlong(rings, p, d, L, r0, r1, r0 * 0.92, r1 * 0.92, U, sp, null);
      if (j === 2) for (const u of [0.35, 0.62, 0.82, 0.94]) { const c = p.clone().addScaledVector(d, L + r1 * 0.6 * u); const rr = r1 * Math.sqrt(1 - u * u); rings.push({c, rU: rr, rV: rr * 0.92, U, V: new THREE.Vector3().crossVectors(d, U).normalize(), f: 1}); }
      p = p.clone().addScaledVector(d, L); r0 = r1;
    });
  });
  // thumb (abducted toward +z, below the index)
  {
    const open = 0.2 + 0.8 * s, flex = [lerp(0.2, -0.1, open), lerp(0.5, 0.1, open), lerp(0.4, 0.05, open)];
    let p = new THREE.Vector3(1.6, -1.2, 2.2), d = new THREE.Vector3(Math.cos(0.42), -0.22, Math.sin(0.42)).normalize(), r0 = 1.3;
    const lat = new THREE.Vector3(-Math.sin(0.42), 0, Math.cos(0.42));
    [3.0, 2.6, 2.1].forEach((L, j) => {
      d.applyAxisAngle(lat, -flex[j]);
      const U = lat.clone().sub(d.clone().multiplyScalar(lat.dot(d))).normalize(), r1 = r0 * 0.86;
      ringsAlong(rings, p, d, L, r0, r1, r0 * 0.9, r1 * 0.9, U, sp, null);
      p = p.clone().addScaledVector(d, L); r0 = r1;
    });
  }
  return rings;
}
// wrist path: slides along its own axis toward the target and eases to a stop just before contact
const ALPHA = 1.08, DIR = new THREE.Vector3(Math.cos(ALPHA), Math.sin(ALPHA), 0);
const TIPOFF = 15.8;
const WEND = TARGET.clone().addScaledVector(DIR, -TIPOFF), WSTART = WEND.clone().addScaledVector(DIR, -44);
function wristAt(tau) {
  const u = clamp((tau - 0.1) / 2.6), e = 1 - Math.pow(1 - u, 3);
  const p = WSTART.clone().lerp(WEND, e); p.x += 2.2 * Math.sin(Math.PI * e) * 0.9; return p;
}
function handMatrix(tau) {
  const m = new THREE.Matrix4(), q = new THREE.Quaternion().setFromEuler(new THREE.Euler(-0.95, -0.18, ALPHA, 'ZYX'));
  m.compose(wristAt(tau), q, new THREE.Vector3(1, 1, 1)); return m;
}
function emit(out, rings, M, color, intensity, camPos, M_SEG = 22, backDim = 0.10) {
  const nm = new THREE.Matrix3().setFromMatrix4(M), P = out.pos, C = out.col;
  for (const r of rings) {
    let prev = null, prevVis = 1;
    for (let k = 0; k <= M_SEG; k++) {
      const a = k / M_SEG * Math.PI * 2, ca = Math.cos(a), sa = Math.sin(a);
      const n = r.U.clone().multiplyScalar(ca * r.rV).addScaledVector(r.V, sa * r.rU).normalize().applyMatrix3(nm);
      const v = r.c.clone().addScaledVector(r.U, ca * r.rU).addScaledVector(r.V, sa * r.rV).applyMatrix4(M);
      const vis = n.dot(camPos.clone().sub(v).normalize()) > -0.05 ? 1 : backDim;
      if (prev) { P.push(prev.x, prev.y, prev.z, v.x, v.y, v.z); const i1 = intensity * r.f * prevVis, i2 = intensity * r.f * vis; C.push(color[0] * i1, color[1] * i1, color[2] * i1, color[0] * i2, color[1] * i2, color[2] * i2); }
      prev = v; prevVis = vis;
    }
  }
}
// ---- wire grid backdrop that bends around the touch point ----
const GZ = -34, GN = {x: 21, y: 31}, GSP = 5.2, SUB = 10;
function buildGrid(t) {
  const P = [], C = [], pinch = sm((t - 0.9) / 1.2) * (1 - 0.55 * sm((t - 2.7) / 0.6));
  const t0 = 2.7, damp = Math.exp(-Math.max(0, t - t0) / 0.55) * (t > t0 ? 1 : 0);
  const warp = (x, y) => {
    const dx = x - TARGET.x, dy = y - TARGET.y, r = Math.hypot(dx, dy), g = Math.exp(-(r * r) / 260);
    const k = -0.55 * pinch * g;                          // lines are pulled toward the touch point
    let z = GZ + 7 * pinch * g;
    const rw = Math.max(0, t - t0) * 26; z += 2.2 * damp * Math.sin((r - rw) * 0.55) * Math.exp(-r / 22);   // damped (expected) ripple
    return [x + dx * k, y + dy * k, z, g];
  };
  const seg = (a, b) => {
    const pa = warp(a[0], a[1]), pb = warp(b[0], b[1]);
    const ia = 0.16 + 0.55 * pa[3] * (0.3 + pinch), ib = 0.16 + 0.55 * pb[3] * (0.3 + pinch);
    P.push(pa[0], pa[1], pa[2], pb[0], pb[1], pb[2]); C.push(TEAL[0] * ia, TEAL[1] * ia, TEAL[2] * ia, TEAL[0] * ib, TEAL[1] * ib, TEAL[2] * ib);
  };
  for (let i = -GN.x; i <= GN.x; i++) for (let j = -GN.y * SUB; j < GN.y * SUB; j++) seg([i * GSP, j * GSP / SUB], [i * GSP, (j + 1) * GSP / SUB]);
  for (let j = -GN.y; j <= GN.y; j++) for (let i = -GN.x * SUB; i < GN.x * SUB; i++) seg([i * GSP / SUB, j * GSP], [(i + 1) * GSP / SUB, j * GSP]);
  return {P, C};
}
function pathLine(t) { // the shadow's route: ghost fingertip positions for the next second
  const P = [], C = []; let prev = null;
  for (let k = 0; k <= 30; k++) { const tau = t + LEAD + k * 0.04, w = wristAt(tau), m = handMatrix(tau), tip = new THREE.Vector3(TIPOFF, 0, 0).applyMatrix4(m.clone().setPosition(w));
    if (prev) { const a = 0.25 + 0.75 * (1 - k / 30); P.push(prev.x, prev.y, prev.z, tip.x, tip.y, tip.z); C.push(...TEAL.map(v => v * a), ...TEAL.map(v => v * a)); } prev = tip; }
  return {P, C};
}

window.renderAt = (t) => {
  const T = Math.min(t, DUR);
  // camera: slow push between layers with a gentle drift
  camera.position.set(1 + 5 * Math.sin(T * 0.45), -4 + 1.8 * T, 112 - 9 * T); camera.lookAt(0, 2 + 0.9 * T, 0); camera.updateMatrixWorld();
  const cp = camera.position.clone();
  // real hand (bone white)
  const hand = {pos: [], col: []}; emit(hand, buildHand(T), handMatrix(T), WHITE, 0.95, cp);
  setLines([glow.hand, core.hand], hand.pos, hand.col);
  // predicted ghost (teal) leads by LEAD; fades into the real hand as they converge
  const conv = sm((T - 2.45) / 0.55);
  const gh = {pos: [], col: []}; emit(gh, buildHand(T + LEAD), handMatrix(T + LEAD), TEAL, 0.9 * (1 - 0.85 * conv), cp);
  setLines([glow.ghost, core.ghost], gh.pos, gh.col);
  // offset wire positions of the fingertip's future path
  const tr = {pos: [], col: []}; for (let k = 1; k <= 2; k++) emit(tr, buildHand(T + LEAD + 0.2 * k).filter((_, i) => i % 6 === 0), handMatrix(T + LEAD + 0.2 * k), TEAL, (0.55 - 0.18 * k) * (1 - conv), cp, 14, 0.04);
  setLines([glow.trail, core.trail], tr.pos, tr.col);
  const g = buildGrid(T); setLines([glow.grid, core.grid], g.P, g.C);
  const pl = pathLine(T); core.path.geometry.setPositions(pl.P); core.path.geometry.setColors(pl.C);
  // red target: pulses harder when the ghost arrives, flares at contact
  const ghostArrive = sm((T - 1.6) / 0.35), contact = Math.exp(-Math.max(0, T - 2.7) / 0.25) * (T > 2.7 ? 1 : 0);
  const pulse = 1 + 0.08 * Math.sin(T * 9) + 0.5 * ghostArrive * (1 - sm((T - 2.7) / 0.8)) + 0.9 * contact;
  tgt.scale.setScalar(pulse); tRing.material.opacity = 0.55 + 0.45 * ghostArrive; tHalo.material.opacity = 0.05 + 0.12 * ghostArrive + 0.25 * contact;
  // opening is almost black: fade the whole scene up
  const fade = sm((T - 0.05) / 0.5); scene.children.forEach(c => { if (c.material && c.isLineSegments2) c.visible = true; });
  renderer.domElement.style.opacity = String(fade);
  // sparse integrated line (typed), red only on the key word
  const full = ['YOUR SHADOW ', '<em>ARRIVES</em>', ' FIRST.'], plain = 'YOUR SHADOW ARRIVES FIRST.', n = Math.max(1, Math.floor(plain.length * clamp((T - 0.7) / 1.3)));
  let html = '', used = 0; for (const part of full) { const text = part.replace(/<[^>]+>/g, ''); const take = Math.max(0, Math.min(text.length, n - used)); used += text.length; if (take <= 0) continue; html += part.startsWith('<em>') ? `<em>${text.slice(0, take)}</em>` : text.slice(0, take); }
  document.getElementById('line').innerHTML = T > 0.7 ? html : '';
  renderer.render(scene, camera);
  return true;
};
window.ready = true;
