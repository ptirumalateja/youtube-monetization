// Articulated silhouette footballer: real adult proportions (about 7.6 heads), tapered limbs,
// football shorts and short sleeves, so the outline reads as a person from any angle.
// Local frame: the figure faces +z, y up, its LEFT is +x. Angles in degrees.
import * as THREE from 'three';

const D = Math.PI / 180;

function lathe(L, prof, flat = 0.88, seg = 14) {
  // prof: [[u, r], ...] with u 0 (joint) -> 1 (end); limb hangs along -y
  const pts = [];
  pts.push(new THREE.Vector2(0.0001, 0));
  for (const [u, r] of prof) pts.push(new THREE.Vector2(r, -u * L));
  pts.push(new THREE.Vector2(0.0001, -L));
  const g = new THREE.LatheGeometry(pts.reverse(), seg);
  g.scale(1, 1, flat);
  return g;
}
function ell(rx, ry, rz, seg = 16) { const g = new THREE.SphereGeometry(1, seg, Math.round(seg * 0.75)); g.scale(rx, ry, rz); return g; }

export class Human {
  constructor(mat, opt = {}) {
    const s = opt.height ? opt.height / 1.83 : 1;
    this.s = s;
    this.root = new THREE.Group();          // ground point under the pelvis, world placed
    this.body = new THREE.Group();          // pelvis (y set by grounding)
    this.root.add(this.body);
    const M = (g, parent, x = 0, y = 0, z = 0) => { const m = new THREE.Mesh(g, mat); m.position.set(x, y, z); parent.add(m); m.frustumCulled = false; return m; };
    const G = (parent, x = 0, y = 0, z = 0) => { const g = new THREE.Group(); g.position.set(x * s, y * s, z * s); parent.add(g); return g; };
    const L = (v) => v * s;
    this.keeper = !!opt.keeper;
    // torso: two elliptical lathes (pelvis->waist, waist->shoulders) so the outline is a smooth V
    const torsoLow = lathe(L(0.3), [[0, 0.11], [0.2, 0.152], [0.4, 0.163], [0.7, 0.146], [1, 0.13]].map(([u, r]) => [u, L(r)]), 0.66, 20);
    torsoLow.rotateX(Math.PI); torsoLow.translate(0, L(-0.1), 0);         // spans y -0.1 (crotch) .. +0.2 (waist)
    M(torsoLow, this.body, 0, 0, L(-0.01));
    M(ell(L(0.12), L(0.07), L(0.1)), this.body, 0, L(-0.07), L(-0.03));     // seat
    this.spine = G(this.body, 0, 0.12, 0);
    const torsoUp = lathe(L(0.46), [[0, 0.13], [0.25, 0.138], [0.55, 0.162], [0.74, 0.17], [0.88, 0.152], [0.96, 0.12], [1, 0.07]].map(([u, r]) => [u, L(r)]), 0.62, 20);
    torsoUp.rotateX(Math.PI);                                               // spans y 0 .. 0.46 above the waist
    M(torsoUp, this.spine, 0, L(-0.02), L(-0.005));
    this.chest = G(this.spine, 0, 0.2, 0);
    this.neck = G(this.chest, 0, 0.24, -0.01);
    M(new THREE.CylinderGeometry(L(0.05), L(0.058), L(0.14), 12), this.neck, 0, L(0.03), 0);
    M(ell(L(0.13), L(0.04), L(0.07)), this.neck, 0, L(-0.035), 0);          // trapezius slope
    this.head = G(this.neck, 0, 0.08, 0.005);
    M(ell(L(0.088), L(0.112), L(0.1)), this.head, 0, L(0.11), L(-0.005));
    M(ell(L(0.075), L(0.06), L(0.08)), this.head, 0, L(0.05), L(0.025));      // jaw
    M(ell(L(0.016), L(0.026), L(0.03)), this.head, 0, L(0.085), L(0.095));     // nose
    // arms
    const armProf = [[0, 0.052], [0.15, 0.054], [0.55, 0.046], [0.9, 0.04], [1, 0.037]].map(([u, r]) => [u, L(r)]);
    const foreProf = [[0, 0.04], [0.2, 0.044], [0.6, 0.034], [1, 0.027]].map(([u, r]) => [u, L(r)]);
    this.sh = {}; this.el = {}; this.wr = {};
    for (const side of ['L', 'R']) {
      const sx = side === 'L' ? 1 : -1;
      const sh = G(this.chest, 0.168 * sx, 0.185, -0.01);
      M(ell(L(0.056), L(0.064), L(0.058)), sh, 0, L(-0.015), 0);
      M(lathe(L(0.29), armProf), sh);
      M(lathe(L(0.15), [[0, 0.035], [0.12, 0.056], [0.6, 0.057], [1, 0.053]].map(([u, r]) => [u, L(r)])), sh); // sleeve
      if (this.keeper) M(lathe(L(0.29), armProf.map(([u, r]) => [u, r * 1.25])), sh);
      const el = G(sh, 0, -0.29, 0);
      M(ell(L(0.039), L(0.04), L(0.039)), el);
      M(lathe(L(0.26), foreProf), el);
      if (this.keeper) M(lathe(L(0.26), foreProf.map(([u, r]) => [u, r * 1.2])), el);
      const wr = G(el, 0, -0.26, 0);
      // hand: palm + fingers block, thumb
      const kg = this.keeper ? 1.45 : 1;
      M(ell(L(0.016) * kg, L(0.058) * kg, L(0.034) * kg), wr, 0, L(-0.055), 0);
      M(ell(L(0.012), L(0.032), L(0.012)), wr, 0, L(-0.035), L(0.035));
      this.sh[side] = sh; this.el[side] = el; this.wr[side] = wr;
    }
    // legs
    const thighProf = [[0, 0.088], [0.12, 0.09], [0.45, 0.075], [0.85, 0.055], [1, 0.05]].map(([u, r]) => [u, L(r)]);
    const shinProf = [[0, 0.05], [0.18, 0.062], [0.35, 0.058], [0.7, 0.04], [0.92, 0.034], [1, 0.034]].map(([u, r]) => [u, L(r)]);
    this.hip = {}; this.kn = {}; this.an = {}; this.toe = {}; this.heel = {};
    for (const side of ['L', 'R']) {
      const sx = side === 'L' ? 1 : -1;
      const hip = G(this.body, 0.092 * sx, -0.045, 0);
      M(lathe(L(0.44), thighProf), hip);
      M(lathe(L(0.25), [[0, 0.06], [0.12, 0.092], [0.5, 0.093], [1, 0.088]].map(([u, r]) => [u, L(r)]), 0.9), hip, sx * L(0.008), L(0.02), 0); // shorts
      const kn = G(hip, 0, -0.44, 0);
      M(ell(L(0.052), L(0.055), L(0.055)), kn);
      M(lathe(L(0.43), shinProf), kn);
      const an = G(kn, 0, -0.43, 0);
      M(ell(L(0.042), L(0.045), L(0.05)), an, 0, L(-0.01), 0);
      // boot: heel back 0.06, toe forward 0.2
      M(ell(L(0.045), L(0.042), L(0.135)), an, 0, L(-0.05), L(0.07));
      M(ell(L(0.04), L(0.03), L(0.06)), an, 0, L(-0.06), L(0.17));
      const toe = new THREE.Object3D(); toe.position.set(0, L(-0.085), L(0.215)); an.add(toe);
      const heel = new THREE.Object3D(); heel.position.set(0, L(-0.085), L(-0.055)); an.add(heel);
      this.hip[side] = hip; this.kn[side] = kn; this.an[side] = an; this.toe[side] = toe; this.heel[side] = heel;
    }
    this.hipH = L(0.98);
    this.body.position.y = this.hipH;
    this._v = new THREE.Vector3();
  }
  // p: pose object (missing fields = 0)
  pose(p) {
    const g = (k, d = 0) => (p[k] === undefined ? d : p[k]);
    this.body.rotation.set(g('pTilt') * D, g('pTwist') * D, g('pSide') * D, 'YXZ');
    this.spine.rotation.set(g('lean') * D, g('twist') * D, g('side') * D, 'YXZ');
    this.chest.rotation.set(g('lean2') * D, g('twist2') * D, g('side2') * D, 'YXZ');
    this.neck.rotation.set(g('neck') * D, g('headY') * 0.4 * D, 0, 'YXZ');
    this.head.rotation.set(g('headX') * D, g('headY') * 0.6 * D, g('headZ') * D, 'YXZ');
    for (const side of ['L', 'R']) {
      const sx = side === 'L' ? 1 : -1;
      const h = g('hip' + side, [0, 0, 0]);
      this.hip[side].rotation.set(-h[0] * D, sx * (h[2] || 0) * D, sx * (h[1] || 0) * D, 'ZXY');
      this.kn[side].rotation.set(g('knee' + side) * D, 0, 0);
      this.an[side].rotation.set(g('ankle' + side) * D, sx * g('toeOut' + side) * D, 0, 'YXZ');
      const a = g('sh' + side, [0, 0, 0]);
      this.sh[side].rotation.set(-a[0] * D, sx * (a[2] || 0) * D, sx * (a[1] || 0) * D, 'ZXY');
      this.el[side].rotation.set(-g('elb' + side) * D, 0, 0);
      this.wr[side].rotation.set(-g('wrist' + side, 0) * D, 0, 0);
    }
  }
  // put the lowest foot point on the ground (plus lift), after root x/z/heading are set
  ground(lift = 0) {
    this.body.position.y = this.hipH;
    this.root.updateMatrixWorld(true);
    let mn = 1e9;
    for (const side of ['L', 'R']) for (const o of [this.toe[side], this.heel[side]]) { o.getWorldPosition(this._v); mn = Math.min(mn, this._v.y); }
    this.body.position.y += -(mn - this.root.position.y) + lift;
    this.root.updateMatrixWorld(true);
  }
  footWorld(side, out) { return this.toe[side].getWorldPosition(out); }
}

// ---------------------------------------------------------------- pose library
export const P = {
  stand: { hipL: [2, 4, 0], hipR: [2, 4, 0], kneeL: 4, kneeR: 4, shL: [4, 8, 0], shR: [4, 8, 0], elbL: 12, elbR: 12, lean: 2 },
  ready: { hipL: [30, 10, 0], hipR: [30, 10, 0], kneeL: 38, kneeR: 38, ankleL: -12, ankleR: -12, lean: 22, lean2: 6, neck: -14, headX: -14,
           shL: [28, 34, 0], shR: [28, 34, 0], elbL: 35, elbR: 35, wristL: 10, wristR: 10 },
  wall: { hipL: [3, 2, 0], hipR: [3, 2, 0], kneeL: 6, kneeR: 6, lean: 1, shL: [22, -12, 0], shR: [22, -12, 0], elbL: 62, elbR: 62, wristL: 0, wristR: 0 },
  crouch: { hipL: [105, 14, 0], hipR: [105, 14, 0], kneeL: 128, kneeR: 128, ankleL: -24, ankleR: -24, lean: 18, lean2: 8, neck: -10, headX: -12,
            shL: [40, 20, 0], shR: [40, 20, 0], elbL: 40, elbR: 40 },
  duck: { hipL: [118, 16, 0], hipR: [118, 16, 0], kneeL: 140, kneeR: 140, ankleL: -26, ankleR: -26, lean: 42, lean2: 20, neck: 20, headX: 25,
          shL: [150, 30, 0], shR: [150, 30, 0], elbL: 120, elbR: 120 },
};

export function lerpPose(a, b, u) {
  const out = {};
  const keys = new Set([...Object.keys(a), ...Object.keys(b)]);
  for (const k of keys) {
    const va = a[k], vb = b[k];
    if (Array.isArray(va) || Array.isArray(vb)) {
      const A = va || [0, 0, 0], B = vb || [0, 0, 0];
      out[k] = [0, 1, 2].map((i) => (A[i] || 0) + ((B[i] || 0) - (A[i] || 0)) * u);
    } else out[k] = (va || 0) + ((vb || 0) - (va || 0)) * u;
  }
  return out;
}
export const smooth = (x) => { x = Math.min(1, Math.max(0, x)); return x * x * (3 - 2 * x); };
// keyframe track: [[t, pose], ...] sorted; smooth between keys
export function track(keys, t) {
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 0; i < keys.length - 1; i++) {
    const [t0, p0] = keys[i], [t1, p1] = keys[i + 1];
    if (t <= t1) return lerpPose(p0, p1, smooth((t - t0) / (t1 - t0)));
  }
  return keys[keys.length - 1][1];
}
// running gait, phase in cycles; f = 0..1 effort
export function run(phase, f = 1) {
  const th = phase * 2 * Math.PI;
  const leg = (o) => {
    const a = th + o;
    const hip = 18 + 40 * Math.sin(a);
    const knee = 22 + 85 * Math.pow(Math.max(0, Math.cos(a + Math.PI / 4)), 2) + 12 * Math.max(0, -Math.sin(a));
    const ankle = 8 * Math.sin(a - 0.6);
    return [hip, knee, ankle];
  };
  const [hL, kL, aL] = leg(0), [hR, kR, aR] = leg(Math.PI);
  const p = { hipL: [hL * f, 4, 0], hipR: [hR * f, 4, 0], kneeL: kL * f + 5, kneeR: kR * f + 5, ankleL: aL, ankleR: aR,
    lean: 10 * f + 2, neck: -6, headX: -4, twist: 6 * Math.sin(th) * f,
    shL: [-42 * Math.sin(th) * f - 8, 10, 0], shR: [42 * Math.sin(th) * f - 8, 10, 0], elbL: 78 + 14 * Math.sin(th), elbR: 78 - 14 * Math.sin(th) };
  return p;
}
