// "Why do dreams feel real" v3: ONE continuous fall. The camera rides a red thread that is anchored on the dreamer's tick in every Meta world.
// Each world is a depth-displaced contour mesh (real parallax), sitting in a contour-line field that bends toward the thread; the thread, the field and the tunnel of frames never break between worlds.
import * as THREE from 'three';
const QP = new URLSearchParams(location.search); const W = +(QP.get('w') || 1080), H = +(QP.get('h') || 1920), DUR = 29.4;
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x)), sm = x => { x = clamp(x); return x * x * (3 - 2 * x); }, lerp = (a, b, t) => a + (b - a) * t;
const ease = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; }, easeOut = x => 1 - Math.pow(1 - clamp(x), 3);
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const renderer = new THREE.WebGLRenderer({antialias: true, preserveDrawingBuffer: true}); renderer.setPixelRatio(1); renderer.setSize(W, H); renderer.setClearColor(0x02050a, 1);
document.body.appendChild(renderer.domElement); document.body.style.width = W + 'px'; document.body.style.height = H + 'px';
const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(40, W / H, 0.1, 1400);
const M3 = await (await fetch('./assets/dreams/v3_meta.json')).json();
const loadImg = src => new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = src; });
const AXY = 0.9; // screen composition: worlds sit above the caption band

// ---------- stages ----------  (w = world width, R = rest distance, ds = depth strength, px/py = lateral pan of the look-at, roll0 = arrival roll that unwinds)
const S = 40, TR = 0.6;
const ST = [
  {k: 'bedfall', A: 0.0, w: 13, R: 21, ds: 3, px: 3.5, py: 0, nx: 0.0, ny: 0.3},
  {k: 'brain', A: 2.0, w: 12, R: 20, ds: 2.2, px: -3.5, py: 0, nx: 2.2, ny: -0.6},
  {k: 'head', A: 3.8, w: 22, R: 20, ds: 3, px: 3, py: 0, nx: -2.0, ny: 0.5},
  {k: 'island', A: 5.8, w: 12.5, R: 22, ds: 3.5, px: 0, py: 3.0, nx: 2.4, ny: -0.4},
  {k: 'stairs', A: 7.6, w: 30, R: 21, ds: 4, px: -7, py: 0, nx: -2.2, ny: 0.6, roll0: 1.2},
  {k: 'rem', A: 9.4, w: 24, R: 22, ds: 3, px: -4, py: 2, nx: 1.8, ny: -0.5},
  {k: 'ship', A: 11.2, w: 17, R: 21, ds: 3, px: -3, py: -9, nx: -1.8, ny: 0.4},
  {k: 'wave', A: 13.0, w: 14, R: 21, ds: 3, px: -5, py: 0, nx: 2.0, ny: -0.5},
  {k: 'corridor', A: 15.0, w: 36, R: 17, ds: 6, px: 4, py: 0, nx: -2.2, ny: 0.5},
  {k: 'ribbon', A: 17.0, w: 28, R: 22, ds: 3, px: 7, py: 0, nx: 2.0, ny: -0.4},
  {k: 'whalecity', A: 18.8, w: 36, R: 24, ds: 5, px: -15, py: 0, nx: -1.6, ny: 0.4},
  {k: 'web', A: 20.8, w: 30, R: 17, ds: 3, px: 3, py: 0, nx: 1.6, ny: -0.3},
  {k: 'morph', A: 22.6, w: 24, R: 22, ds: 3, px: -2, py: 0, nx: -1.4, ny: 0.3},
  {k: 'eye', A: 24.4, w: 11, R: 18, ds: 3, px: 0, py: 0, nx: 1.4, ny: -0.3},
  {k: 'lucid', A: 26.2, w: 22, R: 18, ds: 3, px: 0, py: 0, nx: -1.0, ny: 0.3},
  {k: 'loopcard', A: 27.8, w: 24, R: 22, ds: 3, px: 0, py: 0, nx: 0.0, ny: 0.0},
];

// backdrop plates: a second, related Meta world sits far behind each world (own depth, parallaxes against it); adjacent plates are visible ahead through the fall
const BD = {bedfall: ['portal', 14, -4, 3, -12, .5], brain: ['face', 16, 4, 1, -12, .35], head: ['brainteal', 22, -3, -2, -13, .3], island: ['moon', 26, -4, 4, -14, .6], stairs: ['vortex', 22, 5, 2, -14, .4],
  rem: ['throat', 28, 0, -2, -13, .4], ship: ['heart', 18, -3, 0, -13, .4], wave: ['clocks', 26, 0, 0, -13, .4], corridor: ['deja', 30, 0, 0, -12, .3], ribbon: ['collage', 40, 0, 0, -12, .4],
  whalecity: ['train', 22, 4, -3, -14, .4], web: ['city', 28, 0, 1, -13, .18], morph: ['brainc', 20, -4, 2, -13, .35], eye: ['stairsc', 24, 3, -1, -13, .3], lucid: ['heaven', 14, 0, -3, -12, .5], loopcard: ['bed', 22, 0, -2, -12, .4]};
const N = ST.length;
ST.forEach((s, i) => { s.i = i; s.z = -S * i; s.D = (i < N - 1 ? ST[i + 1].A : DUR) - s.A; s.node = V3(s.nx, s.ny + AXY, s.z); s.roll0 = s.roll0 || 0; });

// ---------- worlds: depth-displaced contour meshes ----------
const worldMat = (tex, dep, ds, d0) => new THREE.ShaderMaterial({
  uniforms: {uTex: {value: tex}, uDep: {value: dep}, uDS: {value: ds}, uD0: {value: d0}, uOp: {value: 1}, uRed: {value: 1}, uTeal: {value: 1}, uTexel: {value: new THREE.Vector2(1 / 1000, 1 / 400)}},
  transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
  vertexShader: `uniform sampler2D uDep; uniform float uDS,uD0; uniform vec2 uTexel; varying vec2 vUv; varying float vG;
    void main(){ vUv=uv; float d=texture2D(uDep,uv).r; vec3 p=position; p.z+=(d-uD0)*uDS;
      float gx=texture2D(uDep,uv+vec2(uTexel.x*3.0,0.0)).r-texture2D(uDep,uv-vec2(uTexel.x*3.0,0.0)).r, gy=texture2D(uDep,uv+vec2(0.0,uTexel.y*3.0)).r-texture2D(uDep,uv-vec2(0.0,uTexel.y*3.0)).r; vG=length(vec2(gx,gy));
      gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.0); }`,
  fragmentShader: `uniform sampler2D uTex; uniform float uOp,uRed,uTeal; varying vec2 vUv; varying float vG;
    void main(){ vec3 c=texture2D(uTex,vUv).rgb; float rm=clamp((c.r-0.55*c.g-0.04)*3.0,0.0,1.0); c*=mix(uTeal,uRed,rm);
      vec2 e=min(vUv,1.0-vUv); float f=smoothstep(0.0,0.09,min(e.x,e.y)); float st=1.0-0.8*smoothstep(0.06,0.2,vG); gl_FragColor=vec4(c*f*st*uOp,1.0); }`
});
const readDepthAt = (img, u, v) => { const c = document.createElement('canvas'); c.width = img.width; c.height = img.height; const x = c.getContext('2d'); x.drawImage(img, 0, 0);
  let s = 0, n = 0; for (let a = -2; a <= 2; a++) for (let b = -2; b <= 2; b++) { s += x.getImageData(clamp(Math.round(u * img.width) + a, 0, img.width - 1), clamp(Math.round(v * img.height) + b, 0, img.height - 1), 1, 1).data[0]; n++; } return s / n / 255; };
for (const s of ST) {
  const m = M3[s.k], [pw, ph] = m.size, h = s.w * ph / pw;
  const tex = await new THREE.TextureLoader().loadAsync(`./assets/dreams/v3_${s.k}.jpg`); tex.colorSpace = THREE.NoColorSpace; tex.anisotropy = 8;
  const dimg = await loadImg(`./assets/dreams/v3_${s.k}_d.png`); const dep = new THREE.Texture(dimg); dep.needsUpdate = true; dep.colorSpace = THREE.NoColorSpace; dep.minFilter = dep.magFilter = THREE.LinearFilter; dep.generateMipmaps = false;
  const d0 = readDepthAt(dimg, m.anchor[0], m.anchor[1]); const sx = Math.min(260, Math.round(s.w * 12)), sy = Math.max(8, Math.round(sx * h / s.w));
  s.h = h; s.mat = worldMat(tex, dep, s.ds, d0); s.mat.uniforms.uTexel.value.set(1 / dimg.width, 1 / dimg.height);
  s.mesh = new THREE.Mesh(new THREE.PlaneGeometry(s.w, h, sx, sy), s.mat); s.mesh.frustumCulled = false; s.mesh.renderOrder = 3; scene.add(s.mesh);
  s.mesh.position.set(s.node.x - (m.anchor[0] - 0.5) * s.w, s.node.y - (0.5 - m.anchor[1]) * h, s.z);
}

{ const MB = await (await fetch('./assets/dreams/v3b_meta.json')).json(); const gc = document.createElement('canvas'); gc.width = gc.height = 4; const gx = gc.getContext('2d'); gx.fillStyle = '#808080'; gx.fillRect(0, 0, 4, 4);
  const flat = new THREE.CanvasTexture(gc); flat.colorSpace = THREE.NoColorSpace;
  for (const s of ST) { const b = BD[s.k]; if (!b) continue; const [bk, bw, ox, oy, dz, op] = b, [pw, ph] = MB[bk]; const tex = await new THREE.TextureLoader().loadAsync(`./assets/dreams/v3b_${bk}.jpg`); tex.colorSpace = THREE.NoColorSpace; tex.anisotropy = 4;
    const mat = worldMat(tex, flat, 0, 0.5); mat.uniforms.uTexel.value.set(0.25, 0.25); const m = new THREE.Mesh(new THREE.PlaneGeometry(bw, bw * ph / pw, 2, 2), mat); m.frustumCulled = false; m.renderOrder = 2; scene.add(m);
    m.position.set(s.node.x + ox, s.node.y + oy, s.z + dz); s.bd = {m, op, dz, ox, oy}; } }
// paradox: the stairs loop into themselves (echo meshes shrinking down the same axis)
const stairs = ST.find(s => s.k === 'stairs'); const echoes = [0, 1, 2].map(n => { const e = new THREE.Mesh(stairs.mesh.geometry, stairs.mat.clone()); e.frustumCulled = false; e.renderOrder = 2; scene.add(e); return e; });

// ---------- contour-line field: teal lines in the art's own weight, bending toward the thread ----------
const fieldMats = [];
ST.forEach(s => {
  const mat = new THREE.ShaderMaterial({uniforms: {uA: {value: s.node.clone()}, uTime: {value: 0}, uOp: {value: 0}, uBend: {value: 0}}, transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending,
    vertexShader: `varying vec3 vW; void main(){ vec4 wp=modelMatrix*vec4(position,1.0); vW=wp.xyz; gl_Position=projectionMatrix*viewMatrix*wp; }`,
    fragmentShader: `uniform vec3 uA; uniform float uTime,uOp,uBend; varying vec3 vW;
      float lm(float v,float sp,float w){ float x=v/sp; float d=abs(fract(x-0.5)-0.5)/max(fwidth(x),1e-4); return 1.0-clamp(d-w,0.0,1.0); }
      void main(){ vec2 d=vW.xy-uA.xy; float r=length(d); float g=exp(-r*r/38.0); float y=vW.y-d.y*0.55*uBend*g+0.5*sin(vW.x*0.22+uTime*0.7)*(1.0-0.8*g)+0.25*sin(vW.x*0.7-uTime*1.3)*g;
        float l=lm(y,0.36,0.55); float ring=exp(-pow((r-fract(uTime*0.35)*14.0)/0.35,2.0))*0.6; float e=(0.10+0.22*g)*uOp*(1.0-smoothstep(10.0,26.0,r));
        gl_FragColor=vec4(vec3(0.10,0.80,0.68)*l*e+vec3(1.0,0.2,0.14)*ring*uOp*0.12,1.0); }`});
  const p = new THREE.Mesh(new THREE.PlaneGeometry(60, 80, 2, 2), mat); p.position.set(s.node.x, s.node.y, s.z - 6); p.renderOrder = 0; p.frustumCulled = false; scene.add(p); s.field = mat;
});

// ---------- the red thread: one continuous ribbon through every tick ----------
const pts = []; ST.forEach((s, i) => { pts.push(s.node.clone()); if (i < N - 1) { const n = ST[i + 1].node; pts.push(V3((s.node.x + n.x) / 2 + (i % 2 ? -3.2 : 3.2), (s.node.y + n.y) / 2 + (i % 3 - 1) * 1.6, (s.node.z + n.z) / 2)); } });
const curve = new THREE.CatmullRomCurve3(pts, false, 'centripetal'), TUBE = 2600;
const threadMat = new THREE.ShaderMaterial({uniforms: {uCamZ: {value: 0}, uTime: {value: 0}, uAmp: {value: 1}}, transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending,
  vertexShader: `uniform float uTime; varying vec2 vU; varying float vZ; void main(){ vU=uv; vec4 wp=modelMatrix*vec4(position,1.0); vZ=wp.z; gl_Position=projectionMatrix*viewMatrix*wp; }`,
  fragmentShader: `uniform float uCamZ,uTime,uAmp; varying vec2 vU; varying float vZ; void main(){ float d=uCamZ-vZ; float a=smoothstep(1.0,6.0,d)*(1.0-smoothstep(40.0,120.0,d)); float p=0.55+0.45*sin(vU.x*2600.0*0.35-uTime*16.0);
    float core=1.0-abs(vU.y*2.0-1.0); gl_FragColor=vec4(mix(vec3(1.0,0.14,0.10),vec3(1.0,0.75,0.65),core*core)*a*p*uAmp,1.0); }`});
const tube = new THREE.Mesh(new THREE.TubeGeometry(curve, TUBE, 0.03, 4, false), threadMat); tube.frustumCulled = false; tube.renderOrder = 5; scene.add(tube);
const glowTex = (() => { const c = document.createElement('canvas'); c.width = c.height = 128; const x = c.getContext('2d'), g = x.createRadialGradient(64, 64, 0, 64, 64, 64); g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(.22, 'rgba(255,70,50,.8)'); g.addColorStop(1, 'rgba(255,40,30,0)'); x.fillStyle = g; x.fillRect(0, 0, 128, 128); return new THREE.CanvasTexture(c); })();
const ticks = ST.map(s => { const sp = new THREE.Sprite(new THREE.SpriteMaterial({map: glowTex, blending: THREE.AdditiveBlending, depthTest: false, transparent: true, depthWrite: false})); sp.position.copy(s.node); sp.renderOrder = 6; scene.add(sp); return sp; });
// sample the thread by z for the camera rig
const SM = 4000, sampZ = [], sampP = []; for (let i = 0; i <= SM; i++) { const p = curve.getPoint(i / SM); sampZ.push(p.z); sampP.push(p); }
const threadAtZ = z => { let lo = 0, hi = SM; while (hi - lo > 1) { const m = (lo + hi) >> 1; if (sampZ[m] > z) lo = m; else hi = m; } const a = sampP[lo], b = sampP[hi], t = (a.z - z) / ((a.z - b.z) || 1); return V3(lerp(a.x, b.x, t), lerp(a.y, b.y, t), z); };

// ---------- tunnel of frames + speed streaks (the "fall" glue, strongest between worlds) ----------
const NF = 190, fp = [], faArr = []; const corners = [[-1, -1], [1, -1], [1, 1], [-1, 1]];
for (let i = 0; i < NF; i++) { const z = 40 - i * 3.1, size = 5.2 + 3.2 * ((i * 0.61803) % 1), red = i % 9 === 4 ? 1 : 0, ang = i * 0.21;
  for (let c = 0; c < 3; c++) { const s = size * (1 - c * 0.035); for (let e = 0; e < 4; e++) { const a = corners[e], b = corners[(e + 1) % 4]; fp.push(a[0] * s, a[1] * s, 0, b[0] * s, b[1] * s, 0); for (let q = 0; q < 2; q++) faArr.push(z, red, ang, 1 - c * 0.3); } } }
const fg = new THREE.BufferGeometry(); fg.setAttribute('position', new THREE.Float32BufferAttribute(fp, 3)); fg.setAttribute('aF', new THREE.Float32BufferAttribute(faArr, 4));
const fmat = new THREE.ShaderMaterial({uniforms: {uCamZ: {value: 0}, uTime: {value: 0}, uAmp: {value: 1}}, transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending,
  vertexShader: `attribute vec4 aF; uniform float uCamZ,uTime; varying float vA; varying float vR; void main(){ float a=aF.z+aF.x*0.045+uTime*0.10; mat2 m=mat2(cos(a),sin(a),-sin(a),cos(a)); vec2 p=m*position.xy; float d=uCamZ-aF.x;
    vA=smoothstep(3.0,12.0,d)*(1.0-smoothstep(18.0,70.0,d))*aF.w; vR=aF.y; gl_Position=projectionMatrix*viewMatrix*vec4(p.x,p.y+${AXY.toFixed(2)},aF.x,1.0); }`,
  fragmentShader: `uniform float uAmp; varying float vA; varying float vR; void main(){ vec3 c=mix(vec3(0.10,0.80,0.68)*0.55,vec3(1.0,0.16,0.12)*0.8,vR); gl_FragColor=vec4(c*vA*uAmp,1.0); }`});
const frames = new THREE.LineSegments(fg, fmat); frames.frustumCulled = false; frames.renderOrder = 1; scene.add(frames);
let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
const NS = 700, sp = [], sa = []; for (let i = 0; i < NS; i++) { const th = rnd() * 6.283, r = 2.0 + rnd() * 13, z = 40 - rnd() * 600; for (let e = 0; e < 2; e++) { sp.push(Math.cos(th) * r, Math.sin(th) * r, z); sa.push(e, rnd()); } }
const sg = new THREE.BufferGeometry(); sg.setAttribute('position', new THREE.Float32BufferAttribute(sp, 3)); sg.setAttribute('aS', new THREE.Float32BufferAttribute(sa, 2));
const smat = new THREE.ShaderMaterial({uniforms: {uCamZ: {value: 0}, uSpeed: {value: 0}}, transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending,
  vertexShader: `attribute vec2 aS; uniform float uCamZ,uSpeed; varying float vA; void main(){ vec3 p=position; p.y+=${AXY.toFixed(2)}; p.z+=aS.x*(0.8+18.0*uSpeed); float d=uCamZ-p.z; vA=smoothstep(1.0,6.0,d)*(1.0-smoothstep(20.0,70.0,d))*(0.08+0.9*uSpeed)*(0.5+0.5*aS.y)*(1.0-0.65*aS.x); gl_Position=projectionMatrix*viewMatrix*vec4(p,1.0); }`,
  fragmentShader: `varying float vA; void main(){ gl_FragColor=vec4(vec3(0.35,0.95,0.85)*vA,1.0); }`});
const streaks = new THREE.LineSegments(sg, smat); streaks.frustumCulled = false; streaks.renderOrder = 2; scene.add(streaks);

// ---------- captions ----------
const CAPS = [[0.1, 1.0, 'THIS IS A <em>DREAM.</em>'], [1.0, 2.0, 'AND IT FEELS <em>REAL.</em>'], [2.1, 3.7, 'SAME BRAIN.<br>DIFFERENT <em>STATE.</em>'], [3.9, 5.6, 'YOUR LOGIC CENTRE<br>SWITCHES <em>OFF.</em>'],
  [5.8, 7.4, 'NO REALITY CHECK.<br>NO <em>QUESTIONS.</em>'], [7.6, 9.2, 'IMPOSSIBLE PLACES<br>FEEL <em>BELIEVABLE.</em>'], [9.4, 11.0, 'YOUR BODY IS <em>LOCKED.</em><br>YOUR MIND ISN’T.'], [11.2, 14.8, 'THE FEAR, THE JOY,<br>THE LOSS: <em>ALL REAL.</em>'],
  [15.0, 20.6, 'BUILT FROM<br><em>YOUR MEMORIES.</em>'], [20.8, 24.2, 'YOUR BRAIN <em>WEAVES</em><br>IT ALL IN REAL TIME.'], [24.4, 26.0, 'NOT REAL.<br>BUT <em>FELT REAL.</em>'], [26.2, 27.6, 'AND SOMETIMES<br>YOU <em>REALISE.</em>'], [27.8, 29.4, 'YOU WAKE UP.<br>IT ALL <em>FELT REAL.</em>']];
const elCap = document.getElementById('cap'), elFlash = document.getElementById('flash'), elBar = document.getElementById('bar'), elTitle = document.getElementById('title');

// ---------- camera rig ----------
function rig(t) {
  let i = N - 1; for (let k = 0; k < N - 1; k++) if (t < ST[k + 1].A) { i = k; break; }
  const s = ST[i], nx = ST[Math.min(i + 1, N - 1)], D = s.D, tr = i < N - 1 ? TR : 0, pr = clamp((t - s.A) / (D - tr)), last = i === N - 1;
  const d0 = 0.8 * s.R, d1 = 0.62 * s.R; let dist = lerp(d0, s.R, easeOut(pr / 0.4)); if (pr > 0.4) dist = lerp(s.R, d1, ease((pr - 0.4) / 0.6)); if (last) dist = lerp(d0, s.R, easeOut((t - s.A) / 1.2));
  let camZ = s.z + dist, bump = 0, u = 0;
  if (!last && t > s.A + D - tr) { u = (t - (s.A + D - tr)) / tr; camZ = lerp(s.z + d1, nx.z + 0.8 * nx.R, ease(u)); bump = Math.sin(Math.PI * u); }
  const pan = Math.sin(Math.PI * pr);
  const rollIn = s.roll0 * (1 - ease(clamp((t - s.A) / 1.0)));
  return {i, s, camZ, dist, bump, u, panx: s.px * pan, pany: s.py * pan, rollIn, pr};
}
const beat = p => Math.exp(-p * 6.0);
window.renderAt = t => {
  t = clamp(t, 0, DUR); const r = rig(t), W0 = 2 * Math.PI / DUR; const th = threadAtZ(r.camZ - Math.max(r.dist, 6));
  const orb = Math.min(1, r.dist / 14); const ox = 2.4 * Math.sin(t * 0.95 + r.i) * orb, oy = 0.9 * Math.sin(t * 0.7 + 1) * orb;
  camera.fov = 40 + 10 * r.bump; camera.updateProjectionMatrix();
  camera.position.set(th.x + r.panx * 0.6 + ox, th.y + r.pany * 0.6 + oy, r.camZ);
  camera.up.set(0, 1, 0); camera.lookAt(th.x + r.panx, th.y + r.pany, r.camZ - Math.max(r.dist, 6)); camera.rotateZ(r.rollIn + 0.02 * Math.sin(t * 0.8) + (r.i % 2 ? 1 : -1) * 0.45 * r.bump);
  const cz = r.camZ; fmat.uniforms.uCamZ.value = cz; fmat.uniforms.uTime.value = t; fmat.uniforms.uAmp.value = 0.3 + 1.1 * r.bump; smat.uniforms.uCamZ.value = cz; smat.uniforms.uSpeed.value = r.bump;
  threadMat.uniforms.uCamZ.value = cz; threadMat.uniforms.uTime.value = t; threadMat.uniforms.uAmp.value = 0.8 + 0.6 * r.bump;
  let flash = 0;
  ST.forEach(s => {
    const d = cz - s.z, lt = t - s.A, op = sm((d - 1.2) / 4.5) * (1 - sm((d - 58) / 30)), pulse = (f, p = 0) => 0.5 + 0.5 * Math.sin(lt * f + p), u = s.mat.uniforms;
    let red = 1.0 + 1.3 * pulse(7), teal = 1.0;
    switch (s.k) { case 'bedfall': red = 1.3 + 1.6 * pulse(8); break; case 'brain': red = 1.0 + 1.6 * pulse(7, 1); break; case 'island': red = 1.0 + 2.2 * pulse(10); break; case 'stairs': red = 1 + 2.2 * pulse(6); break;
      case 'moon': red = 0.8 + 0.3 * pulse(5); break; case 'wave': red = 1.1 + 1.6 * beat((t * 1.9) % 1); break; case 'web': red = 1.0 + 1.8 * pulse(9); break; case 'eye': red = 1.0 + 1.6 * pulse(7); break; case 'head': red = 1.0 + 1.4 * pulse(5); break; case 'rem': red = 1.0 + 1.6 * pulse(4); break; case 'ribbon': red = 1.0 + 1.5 * pulse(6); break; case 'morph': red = 1.0 + 1.6 * pulse(8); break; case 'lucid': red = 1.2 + 1.8 * pulse(3); break; case 'loopcard': red = 1.2 + 1.2 * pulse(5); break; }
    u.uOp.value = op; u.uRed.value = red; u.uTeal.value = teal; s.mesh.visible = op > 0.004;
    s.mesh.rotation.z = (s.k === 'bedfall' ? 0.02 * Math.sin(lt * 2) : 0); // slight sway
    if (s.bd) { const dB = cz - (s.z + s.bd.dz), ob = sm((dB - 1.2) / 4.5) * (1 - sm((dB - 90) / 40)) * s.bd.op * 0.8, bu = s.bd.m.material.uniforms; bu.uOp.value = ob; bu.uRed.value = 0.9 + 0.7 * pulse(4, s.i); bu.uTeal.value = 0.9;
      s.bd.m.rotation.z = 0.05 * Math.sin(lt * 0.9 + s.i); s.bd.m.scale.setScalar(1 + 0.03 * lt); s.bd.m.visible = ob > 0.004; }
    const f = s.field.uniforms; f.uOp.value = op * 0.9; f.uTime.value = t; f.uBend.value = 0.5 + 0.5 * Math.sin(lt * 2.0);
    const tk = ticks[s.i]; tk.material.opacity = op * (0.55 + 0.35 * pulse(9)); tk.scale.setScalar(0.9 + 0.35 * pulse(9)); tk.visible = op > 0.01;
    if (s.k === 'loopcard') { const w = sm((t - 28.5) / 0.1) * (1 - sm((t - 28.65) / 0.5)); flash = Math.max(flash, 0.12 * w); }
  });
  { const op = stairs.mat.uniforms.uOp.value; echoes.forEach((e, n) => { const sc = Math.pow(0.55, n + 1), lt = t - stairs.A; e.position.copy(stairs.mesh.position).sub(stairs.node).multiplyScalar(sc).add(stairs.node).add(V3(0, 0, -7 * (n + 1))); e.scale.setScalar(sc); e.rotation.z = (n + 1) * 0.35 + lt * 0.25;
    const eu = e.material.uniforms; eu.uOp.value = op * 0.3 * Math.pow(0.6, n); eu.uRed.value = 1 + 1.5 * Math.sin(lt * 6 + n); e.visible = eu.uOp.value > 0.004; }); }
  renderer.render(scene, camera);
  elFlash.style.opacity = flash; elBar.style.width = (100 * t / DUR).toFixed(2) + '%';
  elTitle.innerHTML = 'WHY DO <em class="' + (t > 0.9 && t < 2.2 ? 'on' : '') + '">DREAMS</em> FEEL <em>REAL?</em>';
  let cs = ''; CAPS.forEach(([a, b, txt]) => { const k = sm((t - a) / 0.2) * (1 - sm((t - (b - 0.2)) / 0.2)); if (k > 0.01) cs += `<div style="opacity:${k.toFixed(3)};transform:translateY(${((1 - k) * 12).toFixed(1)}px)">${txt}</div>`; });
  elCap.innerHTML = cs;
};
window.ready = true; window.renderAt(0);
