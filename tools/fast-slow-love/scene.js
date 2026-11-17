// Fast love vs Slow love remake. Deterministic: render(t) draws frame at time t (s).
import * as THREE from 'three';
import { Reflector } from 'three/addons/objects/Reflector.js';

export const W = 1080, H = 1920, FPS = 30, DUR = 14.8;
const SS = 2; // supersample for panels
export const PANEL = { x: 28, w: 1024, h: 560, top: 432, bot: 1112 };
const PW = PANEL.w * SS, PH = PANEL.h * SS;

// ---------- helpers ----------
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a, b, k) => a + (b - a) * k;
const ease = k => k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
const smooth = (a, b, t) => { const k = clamp((t - a) / (b - a)); return k * k * (3 - 2 * k); };
let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
const n1 = (t, s) => Math.sin(t * 1.7 + s) * .5 + Math.sin(t * 3.1 + s * 2.3) * .3 + Math.sin(t * 5.3 + s * .7) * .2;

const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
renderer.setSize(PW, PH, false);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

// ---------- materials ----------
const skinMat = () => new THREE.MeshStandardMaterial({ color: 0xf3ede6, roughness: .5, metalness: 0, emissive: 0x2e2722 });
const blackMat = new THREE.MeshBasicMaterial({ color: 0x1a1414 });
const woodSide = new THREE.MeshStandardMaterial({ color: 0xb08a63, roughness: .85 });
const woodCap = (() => {
  const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d');
  g.fillStyle = '#e6d2b0'; g.fillRect(0, 0, 128, 128);
  g.strokeStyle = 'rgba(150,110,70,.55)'; g.lineWidth = 3;
  for (let r = 12; r < 64; r += 13) { g.beginPath(); g.arc(64, 64, r, 0, 7); g.stroke(); }
  g.strokeStyle = '#9b7550'; g.lineWidth = 8; g.beginPath(); g.arc(64, 64, 60, 0, 7); g.stroke();
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
  return new THREE.MeshStandardMaterial({ map: t, roughness: .8 });
})();
const charMat = new THREE.MeshStandardMaterial({ color: 0x2b211c, roughness: .95 });
const stoneMat = new THREE.MeshStandardMaterial({ color: 0x8f8a86, roughness: .9 });

function logMesh(r, len, axis) {
  const g = new THREE.CylinderGeometry(r, r, len, 28);
  const m = new THREE.Mesh(g, [woodSide, woodCap, woodCap]);
  if (axis === 'x') m.rotation.z = Math.PI / 2; else m.rotation.x = Math.PI / 2;
  m.castShadow = true;
  const grp = new THREE.Group(); grp.add(m); return grp;
}

// ---------- figure ----------
const LIMB = .036;
function limb(len, mat, r = LIMB) {
  const m = new THREE.Mesh(new THREE.CapsuleGeometry(r, len - 2 * r, 6, 14), mat);
  m.position.y = -len / 2; m.castShadow = true; return m;
}
class Figure {
  constructor() {
    this.mat = skinMat();
    const M = this.mat;
    this.root = new THREE.Group();
    this.spine = new THREE.Group(); this.root.add(this.spine);
    const torso = new THREE.Mesh(new THREE.CapsuleGeometry(.105, .36, 8, 18), M);
    torso.position.y = .28; torso.scale.set(1, 1, .82); torso.castShadow = true; this.spine.add(torso);
    this.neck = new THREE.Group(); this.neck.position.y = .54; this.spine.add(this.neck);
    const neckM = limb(.08, M, .03); neckM.position.y = .03; this.neck.add(neckM);
    this.head = new THREE.Mesh(new THREE.SphereGeometry(.175, 40, 30), M);
    this.head.position.y = .2; this.head.castShadow = true; this.neck.add(this.head);
    this.face = new THREE.Group(); this.head.add(this.face); this.buildFace();
    const arm = side => {
      const sh = new THREE.Group(); sh.position.set(side * .1, .47, 0); this.spine.add(sh);
      sh.add(limb(.31, M));
      const el = new THREE.Group(); el.position.y = -.31; sh.add(el);
      el.add(limb(.29, M, .032));
      const hand = new THREE.Mesh(new THREE.SphereGeometry(.045, 16, 12), M); hand.position.y = -.31; el.add(hand);
      return { sh, el, hand };
    };
    const leg = side => {
      const hp = new THREE.Group(); hp.position.set(side * .065, .02, 0); this.root.add(hp);
      hp.add(limb(.46, M, .04));
      const kn = new THREE.Group(); kn.position.y = -.46; hp.add(kn);
      kn.add(limb(.45, M, .036));
      const foot = new THREE.Mesh(new THREE.CapsuleGeometry(.035, .06, 4, 10), M);
      foot.rotation.x = Math.PI / 2; foot.position.set(0, -.46, .04); kn.add(foot);
      return { hp, kn };
    };
    this.la = arm(1); this.ra = arm(-1); this.ll = leg(1); this.rl = leg(-1);
    this.root.traverse(o => { if (o.isMesh && o.material === M) o.receiveShadow = false; });
  }
  feat(x, y, obj) {
    const r = .176, z = Math.sqrt(Math.max(0, r * r - x * x - y * y));
    obj.position.set(x, y, z);
    obj.lookAt(new THREE.Vector3(x, y, z).multiplyScalar(3));
    this.face.add(obj); return obj;
  }
  buildFace() {
    const dot = () => { const m = new THREE.Mesh(new THREE.SphereGeometry(.021, 14, 10), blackMat); m.scale.z = .35; return m; };
    const arc = (r, up) => {
      const m = new THREE.Mesh(new THREE.TorusGeometry(r, .0075, 6, 20, Math.PI), blackMat);
      const g = new THREE.Group(); g.add(m); m.rotation.z = up ? 0 : Math.PI; return g;
    };
    const brow = () => { const g = new THREE.Group(); const m = new THREE.Mesh(new THREE.CapsuleGeometry(.007, .045, 3, 6), blackMat); m.rotation.z = Math.PI / 2; g.add(m); return g; };
    this.F = {
      dotL: this.feat(.058, .025, dot()), dotR: this.feat(-.058, .025, dot()),
      hapL: this.feat(.058, .018, arc(.026, true)), hapR: this.feat(-.058, .018, arc(.026, true)),
      smile: this.feat(0, -.06, arc(.035, false)), frown: this.feat(0, -.085, arc(.03, true)),
      oh: this.feat(0, -.075, (() => { const m = new THREE.Mesh(new THREE.SphereGeometry(.026, 14, 10), blackMat); m.scale.set(.85, 1.15, .3); return m; })()),
      flat: this.feat(0, -.07, brow()),
      browL: this.feat(.06, .085, brow()), browR: this.feat(-.06, .085, brow()),
    };
  }
  setFace(f) {
    const F = this.F; Object.values(F).forEach(o => o.visible = false);
    const show = (...k) => k.forEach(n => F[n].visible = true);
    if (f === 'happy') show('hapL', 'hapR', 'smile');
    else if (f === 'content') show('hapL', 'hapR', 'smile');
    else if (f === 'smile') show('dotL', 'dotR', 'smile');
    else if (f === 'shock') { show('dotL', 'dotR', 'oh', 'browL', 'browR'); F.browL.children[0].rotation.z = Math.PI / 2; F.browR.children[0].rotation.z = Math.PI / 2; F.browL.position.y = .1; F.browR.position.y = .1; }
    else if (f === 'annoyed') { show('dotL', 'dotR', 'flat', 'browL', 'browR'); F.browL.children[0].rotation.z = Math.PI / 2 + .45; F.browR.children[0].rotation.z = Math.PI / 2 - .45; F.browL.position.y = .07; F.browR.position.y = .07; }
    else if (f === 'sad') { show('dotL', 'dotR', 'frown', 'browL', 'browR'); F.browL.children[0].rotation.z = Math.PI / 2 - .4; F.browR.children[0].rotation.z = Math.PI / 2 + .4; F.browL.position.y = .08; F.browR.position.y = .08; }
    else show('dotL', 'dotR');
  }
  apply(p) {
    this.root.position.set(p.x, p.y, p.z); this.root.rotation.set(0, p.ry, 0);
    this.spine.rotation.set(p.lean, 0, p.side);
    this.neck.rotation.set(p.hx, p.hy, p.hz);
    this.la.sh.rotation.set(-p.laf, -p.lat, p.laa); this.la.el.rotation.set(-p.lae, 0, 0);
    this.ra.sh.rotation.set(-p.raf, p.rat, -p.raa); this.ra.el.rotation.set(-p.rae, 0, 0);
    this.ll.hp.rotation.set(-p.llf, 0, p.lla); this.ll.kn.rotation.set(p.llk, 0, 0);
    this.rl.hp.rotation.set(-p.rlf, 0, -p.rla); this.rl.kn.rotation.set(p.rlk, 0, 0);
    this.setFace(p.face);
    const op = p.op ?? 1;
    this.mat.transparent = op < .999; this.mat.opacity = op; this.mat.depthWrite = op > .5;
    blackMatFade(this, op);
    this.root.visible = op > .01;
  }
}
function blackMatFade(fig, op) {
  if (!fig._bm) { fig._bm = new THREE.MeshBasicMaterial({ color: 0x1a1414, transparent: true }); fig.face.traverse(o => { if (o.isMesh) o.material = fig._bm; }); }
  fig._bm.opacity = op;
}

// ---------- poses ----------
const BASE = { x: 0, y: .93, z: 0, ry: 0, lean: 0, side: 0, hx: 0, hy: 0, hz: 0, laf: 0, laa: .12, lae: .1, raf: 0, raa: .12, rae: .1, llf: 0, lla: .03, llk: 0, rlf: 0, rla: .03, rlk: 0, op: 1, lat: 0, rat: 0 };
const SEAT_Y = .5;
const P = {
  stand: {},
  sit: { y: SEAT_Y, llf: 1.5, rlf: 1.5, llk: 1.42, rlk: 1.42, laf: .55, raf: .55, lae: .5, rae: .5, laa: .1, raa: .1, lean: .06 },
  bend: { lean: .95, y: .86, llf: .35, rlf: .35, llk: .5, rlk: .5, laf: 1.25, raf: 1.25, lae: .1, rae: .1, hx: -.3 },
  windup: { lean: -.1, raf: -.6, rae: .6, laf: .3 },
  release: { lean: .2, raf: 2.3, rae: .1, laf: .4, hx: -.1 },
  cheer: { laf: 0, raf: 0, laa: 2.75, raa: 2.75, lae: -.2, rae: -.2, hx: -.15 },
  crossed: { laf: .45, raf: .5, lae: 1.75, rae: 1.75, laa: .05, raa: .05, lat: 1.25, rat: 1.25, hx: .05 },
  hug: { y: .26, llf: 2.1, rlf: 2.1, llk: 2.5, rlk: 2.5, lla: .08, rla: .08, lean: .3, laf: .95, raf: .95, lae: .55, rae: .55, laa: .1, raa: .1, lat: .7, rat: .7, hx: .25 },
  lift: { lean: .75, y: .8, llf: .55, rlf: .55, llk: .9, rlk: .9, laf: 1.35, raf: 1.35, lae: 0, rae: 0, laa: .15, raa: .15 },
  carry: { lean: .08, laf: .55, raf: .55, lae: .25, rae: .25, laa: .1, raa: .1 },
  heave: { lean: -.05, laf: 2.1, raf: 2.1, lae: .1, rae: .1 },
};
const pose = (...parts) => Object.assign({}, BASE, ...parts);

class Track { // keyframes [{t, p}]; values eased between keys
  constructor() { this.k = []; }
  add(t, p, face) { this.k.push({ t, p, face }); return this; }
  at(t) {
    const k = this.k; let i = 0;
    while (i < k.length - 1 && k[i + 1].t <= t) i++;
    const a = k[i], b = k[Math.min(i + 1, k.length - 1)];
    const u = b.t > a.t ? ease(clamp((t - a.t) / (b.t - a.t))) : 0;
    const out = {};
    for (const key in BASE) out[key] = lerp(a.p[key], b.p[key], u);
    let face = 'neutral'; for (const kk of k) if (kk.face && kk.t <= t + 1e-6) face = kk.face; out.face = face;
    return out;
  }
}

// ---------- fire ----------
const FLAME_COLS = [0xd9361a, 0xf26b1d, 0xfba22a, 0xffd45a, 0xfff2c4];
class Fire {
  constructor(scene, x) {
    this.g = new THREE.Group(); this.g.position.set(x, 0, 0); scene.add(this.g);
    this.flames = new THREE.Group(); this.g.add(this.flames);
    this.mats = FLAME_COLS.map((c, i) => new THREE.MeshBasicMaterial({ color: c, transparent: true, opacity: [.78, .82, .85, .9, .95][i], depthWrite: false, toneMapped: false, side: THREE.DoubleSide }));
    // charred logs + stones
    for (let i = 0; i < 3; i++) { const l = new THREE.Mesh(new THREE.CylinderGeometry(.05, .05, .55, 10), charMat); l.rotation.set(Math.PI / 2, 0, (i - 1) * .9); l.position.y = .05; this.g.add(l); }
    for (let i = 0; i < 9; i++) { const a = i / 9 * Math.PI * 2; const s = new THREE.Mesh(new THREE.SphereGeometry(.07, 10, 8), stoneMat); s.scale.set(1.2, .6, 1); s.position.set(Math.cos(a) * .38, .03, Math.sin(a) * .2); this.g.add(s); }
    this.light = new THREE.PointLight(0xff8a3c, 0, 0, 1.6); this.light.position.set(0, .55, .25); this.light.castShadow = true;
    this.light.shadow.mapSize.set(1024, 1024); this.light.shadow.bias = -.002; this.g.add(this.light);
    // glow sprite
    const gc = document.createElement('canvas'); gc.width = gc.height = 256; const gg = gc.getContext('2d');
    const grd = gg.createRadialGradient(128, 128, 0, 128, 128, 128); grd.addColorStop(0, 'rgba(255,170,80,0.55)'); grd.addColorStop(.4, 'rgba(255,110,40,0.18)'); grd.addColorStop(1, 'rgba(255,90,30,0)');
    gg.fillStyle = grd; gg.fillRect(0, 0, 256, 256);
    this.glowTex = new THREE.CanvasTexture(gc);
    this.glow = new THREE.Sprite(new THREE.SpriteMaterial({ map: this.glowTex, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false }));
    this.glow.position.set(0, .45, -.1); this.g.add(this.glow);
    // embers
    this.emb = []; const eg = new THREE.SphereGeometry(.012, 6, 4);
    const em = new THREE.MeshBasicMaterial({ color: 0xffb35a, transparent: true, toneMapped: false, depthWrite: false, blending: THREE.AdditiveBlending });
    for (let i = 0; i < 40; i++) { const m = new THREE.Mesh(eg, em.clone()); this.g.add(m); this.emb.push({ m, ph: rnd() * 10, sx: (rnd() - .5) * .6, sp: .5 + rnd() * .8, dr: (rnd() - .5) * .4 }); }
    // smoke
    const sc = document.createElement('canvas'); sc.width = sc.height = 128; const sg = sc.getContext('2d');
    const sgr = sg.createRadialGradient(64, 64, 0, 64, 64, 64); sgr.addColorStop(0, 'rgba(200,200,200,.5)'); sgr.addColorStop(1, 'rgba(200,200,200,0)'); sg.fillStyle = sgr; sg.fillRect(0, 0, 128, 128);
    const st = new THREE.CanvasTexture(sc);
    this.smoke = []; for (let i = 0; i < 8; i++) { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: st, transparent: true, depthWrite: false })); this.g.add(s); this.smoke.push({ s, ph: i / 8 }); }
    this.tongues = 7; this.seeds = Array.from({ length: 40 }, () => rnd() * 100);
  }
  shape(w, h, tip) {
    const s = new THREE.Shape();
    s.moveTo(-w / 2, 0);
    s.bezierCurveTo(-w * .55, h * .4, tip - w * .12, h * .72, tip, h);
    s.bezierCurveTo(tip + w * .12, h * .72, w * .55, h * .4, w / 2, 0);
    s.quadraticCurveTo(0, -w * .18, -w / 2, 0);
    return new THREE.ShapeGeometry(s, 10);
  }
  update(t, size, smokeAmt = 0) {
    for (const c of [...this.flames.children]) { c.geometry.dispose(); this.flames.remove(c); }
    const S = Math.max(0, size);
    if (S > .01) {
      const N = this.tongues, Wd = .55 + .42 * Math.min(S, 1.8);
      for (let layer = 0; layer < 5; layer++) {
        const lk = [1, .82, .64, .45, .26][layer];
        for (let i = 0; i < N; i++) {
          const xn = i / (N - 1) - .5;
          const sd = this.seeds[i];
          const env = 1 - Math.pow(Math.abs(xn) * 2, 1.6) * .7;
          const flick = .72 + .28 * (n1(t * 2.2, sd) * .5 + .5);
          const h = S * .95 * env * flick * lk;
          if (h < .02) continue;
          const w = (.24 + .08 * S) * (0.7 + .5 * lk) * (layer === 4 ? 1.6 : 1);
          const tip = n1(t * 1.9, sd + 3) * .14 * h + xn * .12 * h;
          const m = new THREE.Mesh(this.shape(w, h, tip), this.mats[layer]);
          m.position.set(xn * Wd * (layer >= 3 ? .7 : 1), .02, .2 + layer * .002 + (i % 2) * .001);
          m.renderOrder = 10 + layer;
          this.flames.add(m);
        }
      }
    }
    const fl = .88 + .12 * n1(t * 4, 1.3);
    this.light.intensity = 4.2 * Math.pow(Math.min(S, 2), .9) * fl;
    this.glow.material.opacity = clamp(S * 1.1) * fl;
    const gs = 1.6 + 1.5 * S; this.glow.scale.set(gs * 1.3, gs, 1);
    this.glow.position.y = .35 + .3 * S;
    for (const e of this.emb) {
      const life = ((t * e.sp + e.ph) % 1.6) / 1.6;
      const on = S > .08 && (e.ph % 1) < .35 + .45 * Math.min(S, 1.5) / 1.5;
      e.m.visible = on;
      e.m.position.set(e.sx * (0.6 + S * .5) + Math.sin(life * 6 + e.ph) * e.dr * .3, .2 + life * (0.8 + S * 1.1), .25);
      e.m.material.opacity = (1 - life) * .9;
    }
    for (const sm of this.smoke) {
      const life = ((t * .35 + sm.ph) % 1);
      sm.s.visible = smokeAmt > .01;
      sm.s.position.set(Math.sin(life * 5 + sm.ph * 9) * .08, .1 + life * 1.0, .1);
      const sc = .15 + life * .35; sm.s.scale.set(sc, sc * 1.4, 1);
      sm.s.material.opacity = smokeAmt * Math.sin(life * Math.PI) * .45;
    }
  }
}

// ---------- pile ----------
class Pile {
  constructor(scene, x, z = .1) {
    this.g = new THREE.Group(); this.g.position.set(x, 0, z); scene.add(this.g);
    this.slots = []; const r = .085;
    const rows = [[-1, 0, 1], [-.5, .5], [0]];
    rows.forEach((row, ri) => row.forEach(cx => this.slots.push([cx * r * 2.02, r + ri * r * 1.74])));
    this.logs = this.slots.map(([sx, sy]) => { const l = logMesh(r, .5, 'z'); l.position.set(sx, sy, 0); this.g.add(l); return l; });
    this.order3 = [0, 1, 3]; // 3-log pyramid: two bottom (use slots 0,1 shifted) + top
  }
  set(n, pop = 1) { // n logs (0..6); pop scales the newest
    const order = n <= 3 ? [0, 1, 3] : [0, 1, 2, 3, 4, 5];
    const shift = n <= 3 ? .075 : 0;
    this.logs.forEach((l, i) => l.visible = false);
    const used = n <= 3 ? order.slice(0, n) : order.slice(0, n);
    used.forEach((si, j) => {
      const l = this.logs[si]; l.visible = true;
      l.position.x = this.slots[si][0] + (si === 3 && n <= 3 ? shift - .075 + .075 : shift) * (si === 3 ? 0 : 1);
      if (n <= 3 && si === 3) l.position.x = this.slots[0][0] + .075 + .075; // top centered over 0,1
      if (n <= 3 && si !== 3) l.position.x = this.slots[si][0] + .075;
      const s = j === used.length - 1 ? pop : 1; l.scale.setScalar(Math.max(.001, s));
    });
  }
}

// ---------- lane builder ----------
function makeLane(top) {
  const scene = new THREE.Scene();
  const bg = new THREE.Color(0x120d0b); scene.background = bg;
  const cam = new THREE.PerspectiveCamera(26, PANEL.w / PANEL.h, .1, 50);
  cam.position.set(.2, 1.2, 6.0); cam.lookAt(.2, 1.02, 0);
  const hemi = new THREE.HemisphereLight(0xd8dcea, 0x2a1d16, .9); scene.add(hemi);
  const key = new THREE.DirectionalLight(0xfff1e6, 1.5); key.position.set(-2, 3, 6); scene.add(key);
  // floor: reflector + dimming layer
  const refl = new Reflector(new THREE.PlaneGeometry(30, 12), { textureWidth: PW / 2, textureHeight: PH / 2, color: 0x777777 });
  refl.rotation.x = -Math.PI / 2; refl.position.y = -.001; scene.add(refl);
  const floorMat = new THREE.MeshStandardMaterial({ color: 0x1d1714, roughness: .55, transparent: true, opacity: .82 });
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(30, 12), floorMat); floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; scene.add(floor);
  // back wall
  const wallMat = new THREE.MeshStandardMaterial({ color: 0x1a1310, roughness: 1 });
  const wall = new THREE.Mesh(new THREE.PlaneGeometry(30, 10), wallMat); wall.position.set(0, 5, -3.2); wall.receiveShadow = true; scene.add(wall);
  const fire = new Fire(scene, 1.5);
  const seat = logMesh(.2, 1.15, 'x'); seat.position.set(-.08, .2, -.05); scene.add(seat);
  const A = new Figure(), B = new Figure(); scene.add(A.root, B.root);
  const pileL = new Pile(scene, -1.2), pileR = new Pile(scene, .78);
  return { scene, cam, hemi, key, fire, seat, A, B, pileL, pileR, wallMat, floorMat, bg };
}

const top = makeLane(true), bot = makeLane(false);
const flyLogs = [0, 1, 2, 3, 4, 5, 6, 7].map(() => { const l = logMesh(.07, .42, 'z'); top.scene.add(l); l.visible = false; return l; });
const flyLogsB = [0, 1, 2, 3].map(() => { const l = logMesh(.06, .36, 'z'); bot.scene.add(l); l.visible = false; return l; });

// ---------- TOP timeline ----------
const AX = -.36, BX = .22, STZ = .38;
const tA = new Track(), tB = new Track();
const sidePick = (fx, dir) => ({ x: fx, z: STZ, ry: dir * .75 }); // turn toward pile
const throwsA = [.15, .62, 1.08], throwsB = [.0, .45, .9]; // pick times
const topThrowEvents = [];
function addThrows(tr, x, picks, dir, who) {
  tr.add(0, pose(P.stand, { x, z: STZ, ry: dir * .5 }), 'happy');
  for (const t0 of picks) {
    tr.add(t0, pose(P.bend, sidePick(x, dir)));
    tr.add(t0 + .17, pose(P.windup, { x, z: STZ, ry: .55 }));
    tr.add(t0 + .3, pose(P.release, { x, z: STZ, ry: .65 }));
    topThrowEvents.push({ who, pick: t0 + .08, rel: t0 + .28, land: t0 + .62, from: dir < 0 ? 'L' : 'R' });
  }
}
addThrows(tA, AX, throwsA, -1, 'A');
addThrows(tB, BX, throwsB, 1, 'B');
// sit down on log
tA.add(1.5, pose(P.stand, { x: AX + .06, z: .2 }), 'happy'); tB.add(1.45, pose(P.stand, { x: BX - .04, z: .2 }), 'happy');
tA.add(1.78, pose(P.sit, { x: -.33, z: -.02 }), 'smile'); tB.add(1.78, pose(P.sit, { x: .15, z: -.02 }), 'smile');
// day 2 "I LOVE YOU!"  (A speaks, leaning together)
tA.add(2.0, pose(P.sit, { x: -.3, z: -.02, side: -.1, hz: -.18 }), 'happy'); tB.add(2.0, pose(P.sit, { x: .13, z: -.02, side: .08, hz: .2 }), 'happy');
tA.add(2.9, pose(P.sit, { x: -.3, z: -.02, side: -.1, hz: -.18 })); tB.add(2.9, pose(P.sit, { x: .13, z: -.02, side: .08, hz: .2 }));
// day 4 "MOVE IN WITH ME!"
tA.add(3.05, pose(P.sit, { x: -.29, z: -.02, laf: .9, lae: 1.1, hz: -.1 }), 'happy'); tB.add(3.05, pose(P.sit, { x: .12, z: -.02, hz: .12, raf: 1.0, rae: .8 }), 'smile');
tA.add(3.85, pose(P.sit, { x: -.29, z: -.02, hz: -.1 })); tB.add(3.85, pose(P.sit, { x: .12, z: -.02, hz: .12 }));
// stand, lift the seat log and heave it into the fire
tA.add(4.12, pose(P.stand, { x: -.32, z: .3 }), 'smile'); tB.add(4.12, pose(P.stand, { x: .16, z: .3 }), 'smile');
tA.add(4.35, pose(P.lift, { x: -.42, z: .3 })); tB.add(4.35, pose(P.lift, { x: .26, z: .3 }));
tA.add(4.6, pose(P.carry, { x: -.32, z: .3 })); tB.add(4.6, pose(P.carry, { x: .16, z: .3 }));
tA.add(4.85, pose(P.heave, { x: -.2, z: .3, ry: .35 })); tB.add(4.85, pose(P.heave, { x: .3, z: .3, ry: .45 }));
// flare -> shocked, then cheering at the huge fire (day 7)
tA.add(5.08, pose(P.stand, { x: -.24, z: .3, lean: -.12, hx: -.12 }), 'shock'); tB.add(5.08, pose(P.stand, { x: .26, z: .3, lean: -.12, hx: -.12 }), 'shock');
tA.add(5.32, pose(P.stand, { x: -.24, z: .3 })); tB.add(5.32, pose(P.stand, { x: .26, z: .3 }));
tA.add(5.5, pose(P.cheer, { x: -.24, z: .3 }), 'happy'); tB.add(5.5, pose(P.cheer, { x: .26, z: .3 }), 'happy');
tA.add(5.95, pose(P.cheer, { x: -.24, z: .3, laa: 2.6, raa: 2.85 })); tB.add(5.95, pose(P.cheer, { x: .26, z: .3, laa: 2.85, raa: 2.6 }));
tA.add(6.2, pose(P.stand, { x: -.24, z: .3 }), 'neutral'); tB.add(6.2, pose(P.stand, { x: .26, z: .3 }), 'neutral');
// day 15: arms crossed, drifting apart
tA.add(6.55, pose(P.crossed, { x: -.32, z: .3, ry: -.15 }), 'annoyed'); tB.add(6.55, pose(P.crossed, { x: .34, z: .3, ry: .15 }), 'annoyed');
tA.add(6.85, pose(P.crossed, { x: -.33, z: .3, ry: -.15 })); tB.add(6.85, pose(P.crossed, { x: .35, z: .3, ry: .15 }));
// day 27: hugging knees on the ground
tA.add(7.2, pose(P.hug, { x: -.2, z: .3 }), 'sad'); tB.add(7.2, pose(P.hug, { x: .2, z: .3 }), 'sad');
tA.add(7.6, pose(P.hug, { x: -.2, z: .3 })); tB.add(7.6, pose(P.hug, { x: .2, z: .3 }));
// day 30: turn away, back to back, "YOU'VE CHANGED."
tA.add(7.95, pose(P.hug, { x: -.17, z: .3, ry: -1.05 }), 'sad'); tB.add(7.95, pose(P.hug, { x: .17, z: .3, ry: 1.05 }), 'sad');
tA.add(9.3, pose(P.hug, { x: -.17, z: .3, ry: -1.05 })); tB.add(9.3, pose(P.hug, { x: .17, z: .3, ry: 1.05 }));
// fade away as days fly
tA.add(10.6, pose(P.hug, { x: -.2, z: .3, ry: -1.1, op: 0 })); tB.add(10.6, pose(P.hug, { x: .2, z: .3, ry: 1.1, op: 0 }));
tA.add(14, pose(P.hug, { op: 0 })); tB.add(14, pose(P.hug, { op: 0 }));

function topFire(t) {
  // grows with each landed log, flare at heave, then dies
  let s = .38;
  for (const e of topThrowEvents) s += .11 * smooth(e.land, e.land + .2, t);
  const flare = smooth(5.0, 5.35, t) * (1 - smooth(5.9, 6.6, t));
  s += .85 * flare;
  s *= 1 - smooth(6.1, 7.55, t) * .999;
  if (t > 7.55) s = 0;
  return s * (1 + .05 * n1(t * 3, 2));
}

// ---------- BOTTOM timeline ----------
const bA = new Track(), bB = new Track();
const BAX = -.33, BBX = .15;
const sitA = o => pose(P.sit, { x: BAX, z: -.02 }, o), sitB = o => pose(P.sit, { x: BBX, z: -.02 }, o);
const reachR = { ry: .55, lean: .55, raf: 1.0, rae: .1, hx: -.2 }; // B reaches to right pile
const tossR = { ry: .35, lean: .1, raf: 1.9, rae: .2 };
const reachL = { ry: -.55, lean: .55, laf: 1.0, lae: .1, hx: -.2 };
const lean = (k) => ({ side: -.17 * k, hz: -.42 * k, x: BAX + .08 * k }); // A rests head on B
const leanB = (k) => ({ hz: .15 * k, side: .04 * k });
const botToss = []; // {who, pick, rel, land, from}
function bTossB(t0, k) { bB.add(t0, sitB(leanB(k))); bB.add(t0 + .3, sitB({ ...reachR, ...leanB(k * .5) }), k > .5 ? 'content' : 'smile'); bB.add(t0 + .55, sitB({ ...tossR, ...leanB(k * .5) })); bB.add(t0 + .9, sitB(leanB(k))); botToss.push({ who: 'B', pick: t0 + .32, rel: t0 + .55, land: t0 + .85, from: 'R' }); }
function bTossA(t0) { bA.add(t0, sitA()); bA.add(t0 + .3, sitA(reachL)); bA.add(t0 + .55, sitA({ ry: .3, lean: .05, laf: 1.9, lae: .2 })); bA.add(t0 + .9, sitA()); botToss.push({ who: 'A', pick: t0 + .32, rel: t0 + .55, land: t0 + .95, from: 'L' }); }
bA.add(0, sitA(), 'smile'); bB.add(0, sitB(), 'smile');
bB.add(-.2, sitB());
bB.k = []; bB.add(0, sitB({ ...tossR }), 'smile'); bB.add(.35, sitB());
botToss.push({ who: 'B', pick: -1, rel: -.05, land: .3, from: 'R' });
bTossA(1.7);
bTossB(3.1, 0);
bTossA(4.3);
bA.add(5.6, sitA(), 'smile');
bTossB(5.8, 0);
// lean in from 6.9
bA.add(6.9, sitA(), 'smile'); bA.add(7.6, sitA(lean(1)), 'content');
bB.add(7.0, sitB()); bB.add(7.6, sitB(leanB(1)), 'content');
bTossB(8.6, 1);
bA.add(11.0, sitA(lean(1))); bA.add(11.5, sitA(lean(1.05)));
bTossB(10.2, 1);
bB.add(11.4, sitB(leanB(1)), 'content'); bB.add(12.0, sitB({ ...leanB(1.2), hx: .08 }), 'content');
bA.add(14, sitA(lean(1.05))); bB.add(14, sitB({ ...leanB(1.2), hx: .08 }));

function botFire(t) {
  let s = .66;
  for (const e of botToss) s += .12 * Math.exp(-Math.max(0, t - e.land) * 2.5) * smooth(e.land - .01, e.land + .12, t);
  s += .1 * smooth(4, 13, t);
  return s * (1 + .04 * n1(t * 3, 5));
}
function pileCountsTop(t) {
  const L = 3 - topThrowEvents.filter(e => e.from === 'L' && t >= e.pick).length;
  const R = 3 - topThrowEvents.filter(e => e.from === 'R' && t >= e.pick).length;
  return [L, R];
}
const botAdds = { L: [2.6, 6.2, 9.6, 11.3], R: [4.0, 7.2, 9.0, 11.8] };
function pileCountsBot(t) {
  const out = {};
  for (const side of ['L', 'R']) {
    const taken = botToss.filter(e => e.from === side && t >= e.pick).length;
    const adds = botAdds[side].filter(a => t >= a);
    const n = clamp(3 - taken + adds.length, 0, 6);
    const last = adds.length ? adds[adds.length - 1] : -9;
    out[side] = [n, t - last < .25 ? ease(clamp((t - last) / .25)) * 1.08 : 1];
  }
  return out;
}

const _v = new THREE.Vector3();
function flyLog(log, e, t, fig, fireX, startY) {
  if (t < e.pick || t > e.land) { log.visible = false; return; }
  log.visible = true;
  if (t < e.rel) { (fig.ra.hand).getWorldPosition(_v); log.position.copy(_v); log.rotation.set(0, 0, 0); return; }
  fig.ra.hand.getWorldPosition(_v);
  const k = (t - e.rel) / (e.land - e.rel);
  const sx = e._sx ?? (e._sx = _v.x), sy = e._sy ?? (e._sy = _v.y), sz = e._sz ?? (e._sz = _v.z);
  log.position.set(lerp(sx, fireX, k), lerp(sy, .15, k) + Math.sin(k * Math.PI) * .55, lerp(sz, .1, k));
  log.rotation.set(k * 4, 0, k * 3);
}

// ---------- 2D overlay ----------
export const out = document.createElement('canvas'); out.width = W; out.height = H;
const ctx = out.getContext('2d');
const FONT = '"JBM", monospace';
function rr(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
let BUB_MIN = 0;
function bubble(text, x, y, alpha, tailDir = 0, size = 34) {
  if (alpha <= 0) return;
  ctx.save(); ctx.globalAlpha = alpha;
  ctx.font = `800 ${size}px ${FONT}`; ctx.letterSpacing = '3px';
  const tw = ctx.measureText(text).width, padX = 26, bh = size + 30;
  const bw = tw + padX * 2;
  y = Math.max(y, BUB_MIN + bh + 22);
  const bx = Math.max(PANEL.x + 24, Math.min(PANEL.x + PANEL.w - 24 - bw, x - bw / 2 + tailDir * bw * .3)), by = y - bh - 22;
  const pop = 1;
  ctx.fillStyle = 'rgba(10,8,8,.82)'; ctx.strokeStyle = '#f4efe8'; ctx.lineWidth = 4;
  rr(bx, by, bw, bh, bh / 2); ctx.fill(); ctx.stroke();
  // tail
  ctx.beginPath(); ctx.moveTo(x - 12, by + bh - 2); ctx.lineTo(x, y - 4); ctx.lineTo(x + 12, by + bh - 2);
  ctx.fillStyle = 'rgba(10,8,8,1)'; ctx.fill(); ctx.stroke();
  ctx.fillRect(x - 10, by + bh - 6, 20, 5);
  ctx.fillStyle = '#f7f2ea'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(text, bx + bw / 2 + 1.5, by + bh / 2 + 2);
  ctx.restore();
}
function headScreen(lane, fig, py) {
  fig.head.getWorldPosition(_v); _v.y += .2; _v.project(lane.cam);
  return [PANEL.x + (_v.x * .5 + .5) * PANEL.w, py + (-_v.y * .5 + .5) * PANEL.h];
}
function dayAt(t) {
  const steps = [[0, 1], [1.9, 2], [2.95, 4], [5.25, 7], [6.4, 15], [6.95, 27], [7.45, 30]];
  if (t < 9.35) { let d = 1; for (const [a, v] of steps) if (t >= a) d = v; return d; }
  const k = clamp((t - 9.35) / 2.1);
  return Math.round(30 + (365 - 30) * (k * k * (1.4 - .4 * k)));
}
export function dayInfo(t) { return { day: dayAt(t), ff: t >= 9.35 && t < 11.45 }; }

function drawLane(lane, py, label, t, extra) {
  renderer.render(lane.scene, lane.cam);
  ctx.save(); rr(PANEL.x, py, PANEL.w, PANEL.h, 34); ctx.clip();
  ctx.drawImage(renderer.domElement, PANEL.x, py, PANEL.w, PANEL.h);
  if (extra) extra();
  // label
  ctx.font = `800 40px ${FONT}`; ctx.letterSpacing = '6px'; ctx.fillStyle = '#f6f1ea'; ctx.textAlign = 'left'; ctx.textBaseline = 'top';
  ctx.shadowColor = 'rgba(0,0,0,.6)'; ctx.shadowBlur = 8;
  ctx.fillText(label, PANEL.x + 40, py + 36);
  ctx.restore();
  ctx.save(); rr(PANEL.x, py, PANEL.w, PANEL.h, 34); ctx.strokeStyle = 'rgba(40,30,25,.35)'; ctx.lineWidth = 3; ctx.stroke(); ctx.restore();
}

export function render(t) {
  // ---- top lane state
  const pa = tA.at(t), pb = tB.at(t);
  const idle = Math.sin(t * 2.2) * .012;
  pa.hx += idle; pb.hx -= idle;
  top.A.apply(pa); top.B.apply(pb);
  top.A.root.updateMatrixWorld(true); top.B.root.updateMatrixWorld(true);
  const fs = topFire(t);
  top.fire.update(t, fs, smooth(7.4, 7.7, t) * (1 - smooth(9.6, 11, t)));
  const [nl, nr] = pileCountsTop(t); top.pileL.set(nl); top.pileR.set(nr);
  // seat log: lifted with hands 4.35-4.85, then flies into fire
  const seat = top.seat;
  if (t < 4.38) { seat.visible = true; seat.position.set(-.08, .2, -.05); seat.rotation.set(0, 0, 0); }
  else if (t < 4.86) {
    top.A.la.hand.getWorldPosition(_v); const ax = _v.x, ay = _v.y; top.B.ra.hand.getWorldPosition(_v);
    seat.position.set((ax + _v.x) / 2, (ay + _v.y) / 2 - .05, .3); seat.rotation.set(0, 0, 0);
  } else if (t < 5.1) {
    const k = (t - 4.86) / .24; seat.position.set(lerp(.05, 1.5, k), lerp(1.05, .2, k) + Math.sin(k * Math.PI) * .35, lerp(.3, .1, k)); seat.rotation.set(0, 0, -k * .6);
  } else seat.visible = false;
  topThrowEvents.forEach((e, i) => flyLog(flyLogs[i], e, t, e.who === 'A' ? top.A : top.B, 1.5));
  // lighting mood: darkness as the fire dies
  const warm = clamp(fs / 1.1);
  const life = 1 - smooth(6.3, 7.7, t);
  top.hemi.intensity = .32 + .58 * life; top.key.intensity = .45 + 1.05 * life;
  top.scene.background.setRGB(.022 + .03 * warm, .016 + .016 * warm, .014 + .008 * warm);
  // ---- bottom lane state
  const qa = bA.at(t), qb = bB.at(t);
  qa.hx += idle * .6; qb.hx -= idle * .6;
  bot.A.apply(qa); bot.B.apply(qb);
  bot.A.root.updateMatrixWorld(true); bot.B.root.updateMatrixWorld(true);
  bot.fire.update(t + 3.3, botFire(t));
  const pc = pileCountsBot(t); bot.pileL.set(pc.L[0], pc.L[1]); bot.pileR.set(pc.R[0], pc.R[1]);
  botToss.forEach((e, i) => { if (i < flyLogsB.length + 10) { const L = flyLogsB[i % flyLogsB.length]; if (t >= e.pick && t <= e.land) flyLog(L, e, t, e.who === 'A' ? bot.A : bot.B, 1.5); } });
  if (!botToss.some(e => t >= e.pick && t <= e.land)) flyLogsB.forEach(l => l.visible = false);
  // A tosses use left hand-less approximation: use right hand for both (fine at this scale)
  bot.scene.background.setRGB(.05, .033, .024);

  // ---- compose
  ctx.save();
  ctx.fillStyle = '#efe7da'; ctx.fillRect(0, 0, W, H);
  // paper grain
  ctx.restore();
  BUB_MIN = PANEL.top + 92;
  drawLane(top, PANEL.top, 'ALL AT ONCE', t, () => {
    const [ax, ay] = headScreen(top, top.A, PANEL.top), [bx, by] = headScreen(top, top.B, PANEL.top);
    const win = (a, b) => smooth(a, a + .12, t) * (1 - smooth(b - .12, b, t));
    bubble('I LOVE YOU!', ax, ay, win(2.05, 2.95), 0);
    bubble('MOVE IN WITH ME!', bx, by, win(3.08, 3.95), .25);
    bubble("YOU'VE CHANGED.", ax - 20, ay - 20, win(8.0, 9.45), -.3, 30);
    bubble("YOU'VE CHANGED.", bx + 20, by + 30, win(8.3, 9.45), .3, 30);
    // night falls: vignette deepening after fire dies
  });
  BUB_MIN = PANEL.bot + 92;
  drawLane(bot, PANEL.bot, 'A LITTLE EVERY DAY', t, () => {
    const [bx, by] = headScreen(bot, bot.B, PANEL.bot), [ax, ay] = headScreen(bot, bot.A, PANEL.bot);
    const k = smooth(11.95, 12.1, t);
    bubble('I LOVE YOU.', (ax + bx) / 2, Math.min(ay, by), k, 0);
  });
  // day counter
  const { day, ff } = dayInfo(t);
  const cy = (PANEL.top + PANEL.h + PANEL.bot) / 2 + 4;
  ctx.save();
  ctx.textBaseline = 'alphabetic'; ctx.fillStyle = '#2a201b';
  ctx.font = `800 40px ${FONT}`; ctx.letterSpacing = '8px';
  const dw = ctx.measureText('DAY').width;
  ctx.font = `800 104px ${FONT}`; ctx.letterSpacing = '0px';
  const nw = ctx.measureText(String(day)).width;
  const total = dw + 22 + nw; let x0 = W / 2 - total / 2;
  if (ff) { ctx.fillStyle = '#d8371f'; ctx.font = `800 40px ${FONT}`; ctx.fillText('▶▶', x0 - 96, cy + 22); }
  ctx.fillStyle = '#2a201b';
  ctx.font = `800 40px ${FONT}`; ctx.letterSpacing = '8px'; ctx.fillText('DAY', x0, cy + 22);
  ctx.font = `800 104px ${FONT}`; ctx.letterSpacing = '0px'; ctx.fillText(String(day), x0 + dw + 22, cy + 36);
  ctx.restore();
  // title
  ctx.save(); ctx.textBaseline = 'alphabetic'; ctx.textAlign = 'left';
  const parts = [['FAST LOVE', '#d8371f', 78], [' vs ', '#2a201b', 52], ['SLOW LOVE', '#2a201b', 78]];
  ctx.letterSpacing = '2px';
  let tw = 0; for (const [s, , z] of parts) { ctx.font = `800 ${z}px ${FONT}`; tw += ctx.measureText(s).width; }
  let tx = W / 2 - tw / 2;
  for (const [s, c, z] of parts) { ctx.font = `800 ${z}px ${FONT}`; ctx.fillStyle = c; ctx.fillText(s, tx, 392); tx += ctx.measureText(s).width; }
  ctx.restore();
  // end fade
  const f = smooth(13.15, 13.6, t);
  if (f > 0) { ctx.fillStyle = `rgba(239,231,218,${f})`; ctx.fillRect(0, 0, W, H); }
  // closing question card
  const q = smooth(13.45, 13.75, t);
  if (q > 0) {
    ctx.save(); ctx.globalAlpha = q; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
    const sc = .92 + .08 * ease(q); ctx.translate(W / 2, 900); ctx.scale(sc, sc);
    ctx.fillStyle = '#2a201b'; ctx.font = `800 76px ${FONT}`; ctx.letterSpacing = '2px';
    ctx.fillText('WHICH ONE', 0, -120); ctx.fillText('ARE YOU IN?', 0, -30);
    ctx.font = `800 64px ${FONT}`; ctx.textAlign = 'left';
    const segs = [['FAST', '#d8371f'], ['  or  ', '#2a201b'], ['SLOW', '#2a201b']];
    let w = 0; for (const [s] of segs) w += ctx.measureText(s).width; let x = -w / 2;
    for (const [s, c] of segs) { ctx.fillStyle = c; ctx.fillText(s, x, 100); x += ctx.measureText(s).width; }
    ctx.textAlign = 'center'; ctx.fillStyle = '#6b5a4f'; ctx.font = `800 40px ${FONT}`; ctx.letterSpacing = '6px';
    ctx.fillText('COMMENT BELOW \u2193', 0, 200);
    ctx.restore();
  }
  return out;
}
