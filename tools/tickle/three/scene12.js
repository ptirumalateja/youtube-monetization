// "Why do dreams feel real" v4 (motion-first, first three worlds): the dreamer's red tick is a real moving object; the camera rides it; the red trail is where it has been.
// Each world is split into parts that animate on their own (figure peels out of the bed, nodes fire, logic lobe switches OFF); signals travel through the contour lines themselves.
import * as THREE from 'three';
const QP = new URLSearchParams(location.search); const W = +(QP.get('w') || 1080), H = +(QP.get('h') || 1920), DUR = +(QP.get('dur') || 8.2);
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x)), sm = x => { x = clamp(x); return x * x * (3 - 2 * x); }, lerp = (a, b, t) => a + (b - a) * t;
const ease = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; }, easeOut = x => 1 - Math.pow(1 - clamp(x), 3);
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const renderer = new THREE.WebGLRenderer({antialias: true, preserveDrawingBuffer: true}); renderer.setPixelRatio(1); renderer.setSize(W, H); renderer.setClearColor(0x02050a, 1);
document.body.appendChild(renderer.domElement); document.body.style.width = W + 'px'; document.body.style.height = H + 'px';
const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(40, W / H, 0.1, 1400);
const M3 = await (await fetch('./assets/dreams/v3_meta.json')).json();
const loadImg = src => new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = src; });
const AXY = 0.9, S = 34, TR = 0.55;

// ---------- part material: contour art with local gains, travelling pulse, radial reveal, sparkle ----------
const partMat = (tex, dep, ds, d0, asp) => new THREE.ShaderMaterial({
  uniforms: {uTex: {value: tex}, uDep: {value: dep}, uDS: {value: ds}, uD0: {value: d0}, uOp: {value: 1}, uRed: {value: 1}, uTeal: {value: 1}, uTexel: {value: new THREE.Vector2(1 / 1000, 1 / 600)}, uTime: {value: 0}, uAsp: {value: asp},
    uExcl: {value: [0, 0, 0, 0].map(() => new THREE.Vector4(2, 2, 2, 2))}, uReg: {value: new THREE.Vector4(2, 2, 2, 2)}, uRegG: {value: new THREE.Vector2(1, 1)}, uPulse: {value: new THREE.Vector4(0.5, 0.5, -1, 0)}, uRev: {value: new THREE.Vector3(0.5, 0.5, -1)}, uSpark: {value: 0}, uSplit: {value: new THREE.Vector3(2, 1, 1)}},
  transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
  vertexShader: `uniform sampler2D uDep; uniform float uDS,uD0; uniform vec2 uTexel; varying vec2 vUv; varying float vG;
    void main(){ vUv=uv; float d=texture2D(uDep,uv).r; vec3 p=position; p.z+=(d-uD0)*uDS;
      float gx=texture2D(uDep,uv+vec2(uTexel.x*3.0,0.0)).r-texture2D(uDep,uv-vec2(uTexel.x*3.0,0.0)).r, gy=texture2D(uDep,uv+vec2(0.0,uTexel.y*3.0)).r-texture2D(uDep,uv-vec2(0.0,uTexel.y*3.0)).r; vG=length(vec2(gx,gy));
      gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.0); }`,
  fragmentShader: `uniform sampler2D uTex; uniform float uOp,uRed,uTeal,uTime,uAsp,uSpark; uniform vec4 uExcl[4]; uniform vec4 uReg; uniform vec2 uRegG; uniform vec4 uPulse; uniform vec3 uRev; uniform vec3 uSplit; varying vec2 vUv; varying float vG;
    float box(vec2 p, vec4 b){ vec2 a=smoothstep(b.xy-0.004,b.xy+0.004,p), c=1.0-smoothstep(b.zw-0.004,b.zw+0.004,p); return a.x*a.y*c.x*c.y; }
    float hash(vec2 p){ return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
    void main(){ vec3 c=texture2D(uTex,vUv).rgb; float rm=clamp((c.r-0.55*c.g-0.04)*3.0,0.0,1.0);
      float side=step(vUv.x,uSplit.x); float tg=uTeal*mix(uSplit.z,uSplit.y,side), rg=uRed*mix(uSplit.z,uSplit.y,side);
      float inR=box(vUv,uReg); tg*=mix(1.0,uRegG.y,inR); rg*=mix(1.0,uRegG.x,inR);
      c*=mix(tg,rg,rm);
      float sp=1.0+uSpark*rm*(hash(floor(vUv*vec2(900.0,600.0)/3.0)+floor(uTime*14.0))-0.5)*2.2; c*=max(sp,0.15);
      if(uPulse.z>=0.0){ float d=length((vUv-uPulse.xy)*vec2(uAsp,1.0)); float ring=exp(-pow((d-uPulse.z)/0.05,2.0)); c*=1.0+uPulse.w*ring*3.0; c+=vec3(0.15,0.5,0.45)*ring*uPulse.w*0.0; }
      float a=1.0; if(uRev.z>=0.0){ float d=length((vUv-uRev.xy)*vec2(uAsp,1.0)); a=1.0-smoothstep(uRev.z-0.12,uRev.z,d); }
      for(int i=0;i<4;i++){ a*=1.0-box(vUv,uExcl[i]); }
      vec2 e=min(vUv,1.0-vUv); float f=smoothstep(0.0,0.03,min(e.x,e.y)); float st=1.0-0.8*smoothstep(0.06,0.2,vG);
      gl_FragColor=vec4(c*f*st*a*uOp,1.0); }`
});
const worlds = [];
const WD = [{k: 'bedfall', w: 14, A: 0.0, D: 3.0, ds: 3}, {k: 'brain', w: 13, A: 3.0, D: 2.6, ds: 2.2}, {k: 'head', w: 22, A: 5.6, D: 2.6, ds: 3}];
// part boxes in image coords (u0,v0,u1,v1; v down)
const PARTS = {
  bedfall: {fig: [0.365, 0.083, 0.575, 0.517], frames: [0.01, 0.125, 0.43, 0.842], bed: [0.45, 0.417, 0.85, 0.942]},
  brain: {fig: [0.545, 0.46, 0.64, 0.76]},
  head: {fig: [0.465, 0.43, 0.56, 0.66]},
};
const readDepthAt = (img, u, v) => { const c = document.createElement('canvas'); c.width = img.width; c.height = img.height; const x = c.getContext('2d'); x.drawImage(img, 0, 0); return x.getImageData(clamp(Math.round(u * img.width), 0, img.width - 1), clamp(Math.round(v * img.height), 0, img.height - 1), 1, 1).data[0] / 255; };
const toTex = b => [b[0], 1 - b[3], b[2], 1 - b[1]]; // image box (v down) -> texture-space box (v up)
function subGeom(w, h, b) { const g = new THREE.PlaneGeometry((b[2] - b[0]) * w, (b[3] - b[1]) * h, Math.max(2, Math.round((b[2] - b[0]) * w * 12)), Math.max(2, Math.round((b[3] - b[1]) * h * 12))); const uv = g.attributes.uv; for (let i = 0; i < uv.count; i++) { const ux = uv.getX(i), uy = uv.getY(i); uv.setXY(i, b[0] + (b[2] - b[0]) * ux, 1 - b[1] - (b[3] - b[1]) * (1 - uy)); } return g; }
for (let i = 0; i < WD.length; i++) {
  const s = WD[i], m = M3[s.k], [pw, ph] = m.size, h = s.w * ph / pw, asp = pw / ph;
  const tex = await new THREE.TextureLoader().loadAsync(`./assets/dreams/v3_${s.k}.jpg`); tex.colorSpace = THREE.NoColorSpace; tex.anisotropy = 8;
  const dimg = await loadImg(`./assets/dreams/v3_${s.k}_d.png`); const dep = new THREE.Texture(dimg); dep.needsUpdate = true; dep.colorSpace = THREE.NoColorSpace; dep.minFilter = dep.magFilter = THREE.LinearFilter; dep.generateMipmaps = false;
  Object.assign(s, {i, h, asp, z: -S * i, C: V3(0, AXY, -S * i), parts: {}}); const d0 = readDepthAt(dimg, m.anchor[0], m.anchor[1]);
  const mk = (geom, excl) => { const mat = partMat(tex, dep, s.ds, d0, asp); mat.uniforms.uTexel.value.set(1 / dimg.width, 1 / dimg.height); excl.forEach((b, j) => mat.uniforms.uExcl.value[j].set(...toTex(b))); const me = new THREE.Mesh(geom, mat); me.frustumCulled = false; me.renderOrder = 3; scene.add(me); return me; };
  const pb = PARTS[s.k], names = Object.keys(pb);
  s.base = mk(new THREE.PlaneGeometry(s.w, h, Math.min(260, Math.round(s.w * 12)), Math.max(8, Math.round(Math.min(260, s.w * 12) * h / s.w))), names.map(n => pb[n])); s.base.position.copy(s.C);
  names.forEach(n => { const b = pb[n], others = names.filter(o => o !== n && n !== 'fig' ? true : false).map(o => pb[o]); const ex = n === 'fig' ? [] : names.filter(o => o === 'fig').map(o => pb[o]);
    const me = mk(subGeom(s.w, h, b), ex); me.userData.rest = V3(s.C.x + ((b[0] + b[2]) / 2 - 0.5) * s.w, s.C.y + (0.5 - (b[1] + b[3]) / 2) * h, s.z); me.position.copy(me.userData.rest); me.material.uniforms.uDS.value = n === 'fig' ? 0.5 : n === 'frames' ? 1.2 : 2.0; s.parts[n] = me; });
  s.P = (u, v) => V3(s.C.x + (u - 0.5) * s.w, s.C.y + (0.5 - v) * h, s.z);
  worlds.push(s);
}
const [WB, WBr, WH] = worlds;

// ---------- the dreamer's red tick: a real path through the whole fall ----------
const startVec = WB.P(0.735, 0.47).sub(WB.P(0.545, 0.425));
function figOffset(i, tl) {
  if (i === 0) { const e = ease(tl / 1.4); return V3(startVec.x * (1 - e), startVec.y * (1 - e) - 0.4 * Math.max(0, tl - 1.4) + 0.4 * Math.sin(Math.PI * clamp(tl / 1.4)), 0); }
  if (i === 1) return V3(0.1 * Math.sin(tl * 2.2), -0.9 * tl - 0.12 * tl * tl, 0);
  return V3(0.05 * Math.sin(tl * 1.6), -0.38 * tl, 0);
}
function tickLocal(i, tl) { const o = figOffset(i, tl); const base = i === 0 ? WB.P(0.545, 0.425) : i === 1 ? WBr.P(0.59, 0.60) : WH.P(0.51, 0.53); return base.add(o).add(V3(0, i === 0 ? 0.95 : i === 1 ? 0.55 : 0.6, 0)); }
function tickAt(t) {
  let i = worlds.length - 1; for (let k = 0; k < worlds.length - 1; k++) if (t < worlds[k + 1].A) { i = k; break; }
  const s = worlds[i], tl = t - s.A, last = i === worlds.length - 1, td = s.D - TR;
  if (!last && tl > td) { const a = tickLocal(i, td), b = tickLocal(i + 1, 0), u = ease((tl - td) / TR); return V3(lerp(a.x, b.x, sm(u)), lerp(a.y, b.y, sm(u)), lerp(a.z, b.z, u)); }
  return tickLocal(i, tl);
}

// ---------- fields, frames, streaks (continuous fall glue) ----------
const fieldMats = worlds.map(s => { const mat = new THREE.ShaderMaterial({uniforms: {uA: {value: s.C.clone()}, uTime: {value: 0}, uOp: {value: 0}}, transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending,
  vertexShader: `varying vec3 vW; void main(){ vec4 wp=modelMatrix*vec4(position,1.0); vW=wp.xyz; gl_Position=projectionMatrix*viewMatrix*wp; }`,
  fragmentShader: `uniform vec3 uA; uniform float uTime,uOp; varying vec3 vW;
    float lm(float v,float sp,float w){ float x=v/sp; float d=abs(fract(x-0.5)-0.5)/max(fwidth(x),1e-4); return 1.0-clamp(d-w,0.0,1.0); }
    void main(){ vec2 d=vW.xy-uA.xy; float r=length(d); float g=exp(-r*r/38.0); float y=vW.y-d.y*0.4*g+0.5*sin(vW.x*0.22+uTime*0.7)*(1.0-0.8*g);
      float l=lm(y,0.36,0.55); float e=(0.08+0.18*g)*uOp*(1.0-smoothstep(10.0,26.0,r)); gl_FragColor=vec4(vec3(0.10,0.80,0.68)*l*e,1.0); }`});
  const p = new THREE.Mesh(new THREE.PlaneGeometry(60, 80, 2, 2), mat); p.position.set(s.C.x, s.C.y, s.z - 6); p.renderOrder = 0; p.frustumCulled = false; scene.add(p); return mat; });
const NF = 40, fp = [], faArr = []; const corners = [[-1, -1], [1, -1], [1, 1], [-1, 1]];
for (let i = 0; i < NF; i++) { const z = 40 - i * 3.1, size = 5.2 + 3.2 * ((i * 0.61803) % 1), red = i % 9 === 4 ? 1 : 0, ang = i * 0.21;
  for (let c = 0; c < 3; c++) { const s = size * (1 - c * 0.035); for (let e = 0; e < 4; e++) { const a = corners[e], b = corners[(e + 1) % 4]; fp.push(a[0] * s, a[1] * s, 0, b[0] * s, b[1] * s, 0); for (let q = 0; q < 2; q++) faArr.push(z, red, ang, 1 - c * 0.3); } } }
const fg = new THREE.BufferGeometry(); fg.setAttribute('position', new THREE.Float32BufferAttribute(fp, 3)); fg.setAttribute('aF', new THREE.Float32BufferAttribute(faArr, 4));
const fmat = new THREE.ShaderMaterial({uniforms: {uCamZ: {value: 0}, uTime: {value: 0}, uAmp: {value: 1}}, transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending,
  vertexShader: `attribute vec4 aF; uniform float uCamZ,uTime; varying float vA; varying float vR; void main(){ float a=aF.z+aF.x*0.045+uTime*0.10; mat2 m=mat2(cos(a),sin(a),-sin(a),cos(a)); vec2 p=m*position.xy; float d=uCamZ-aF.x;
    vA=smoothstep(3.0,12.0,d)*(1.0-smoothstep(18.0,70.0,d))*aF.w; vR=aF.y; gl_Position=projectionMatrix*viewMatrix*vec4(p.x,p.y+${AXY.toFixed(2)},aF.x,1.0); }`,
  fragmentShader: `uniform float uAmp; varying float vA; varying float vR; void main(){ vec3 c=mix(vec3(0.10,0.80,0.68)*0.55,vec3(1.0,0.16,0.12)*0.8,vR); gl_FragColor=vec4(c*vA*uAmp,1.0); }`});
const frames = new THREE.LineSegments(fg, fmat); frames.frustumCulled = false; frames.renderOrder = 1; scene.add(frames);
let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
const NS = 260, sp = [], sa = []; for (let i = 0; i < NS; i++) { const th = rnd() * 6.283, r = 2.0 + rnd() * 13, z = 40 - rnd() * 130; for (let e = 0; e < 2; e++) { sp.push(Math.cos(th) * r, Math.sin(th) * r, z); sa.push(e, rnd()); } }
const sg = new THREE.BufferGeometry(); sg.setAttribute('position', new THREE.Float32BufferAttribute(sp, 3)); sg.setAttribute('aS', new THREE.Float32BufferAttribute(sa, 2));
const smat = new THREE.ShaderMaterial({uniforms: {uCamZ: {value: 0}, uSpeed: {value: 0}}, transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending,
  vertexShader: `attribute vec2 aS; uniform float uCamZ,uSpeed; varying float vA; void main(){ vec3 p=position; p.y+=${AXY.toFixed(2)}; p.z+=aS.x*(0.8+18.0*uSpeed); float d=uCamZ-p.z; vA=smoothstep(1.0,6.0,d)*(1.0-smoothstep(20.0,70.0,d))*(0.04+0.9*uSpeed)*(0.5+0.5*aS.y)*(1.0-0.65*aS.x); gl_Position=projectionMatrix*viewMatrix*vec4(p,1.0); }`,
  fragmentShader: `varying float vA; void main(){ gl_FragColor=vec4(vec3(0.35,0.95,0.85)*vA,1.0); }`});
const streaks = new THREE.LineSegments(sg, smat); streaks.frustumCulled = false; streaks.renderOrder = 2; scene.add(streaks);

// ---------- tick glow + the trail (where the dreamer has been) ----------
const glowTex = (() => { const c = document.createElement('canvas'); c.width = c.height = 128; const x = c.getContext('2d'), g = x.createRadialGradient(64, 64, 0, 64, 64, 64); g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(.22, 'rgba(255,70,50,.8)'); g.addColorStop(1, 'rgba(255,40,30,0)'); x.fillStyle = g; x.fillRect(0, 0, 128, 128); return new THREE.CanvasTexture(c); })();
const tickSp = new THREE.Sprite(new THREE.SpriteMaterial({map: glowTex, blending: THREE.AdditiveBlending, depthTest: false, transparent: true, depthWrite: false})); tickSp.renderOrder = 7; scene.add(tickSp);
const NT = 90, trailPos = new Float32Array(NT * 2 * 3), trailA = new Float32Array(NT * 2); const tg = new THREE.BufferGeometry(); tg.setAttribute('position', new THREE.BufferAttribute(trailPos, 3)); tg.setAttribute('aA', new THREE.BufferAttribute(trailA, 1));
const idx = []; for (let i = 0; i < NT - 1; i++) idx.push(i * 2, i * 2 + 1, i * 2 + 2, i * 2 + 1, i * 2 + 3, i * 2 + 2); tg.setIndex(idx);
const trail = new THREE.Mesh(tg, new THREE.ShaderMaterial({transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, vertexShader: `attribute float aA; varying float vA; void main(){ vA=aA; gl_Position=projectionMatrix*viewMatrix*vec4(position,1.0); }`,
  fragmentShader: `varying float vA; void main(){ gl_FragColor=vec4(mix(vec3(1.0,0.14,0.10),vec3(1.0,0.7,0.6),vA*vA)*vA,1.0); }`})); trail.frustumCulled = false; trail.renderOrder = 6; scene.add(trail);

// ---------- the logic switch (world 3 focal object) ----------
const toggle = new THREE.Group(); { const pill = new THREE.Shape(); const rw = 0.9, rh = 0.42, rr = 0.42; pill.moveTo(-rw + rr, -rh); pill.lineTo(rw - rr, -rh); pill.absarc(rw - rr, 0, rh, -Math.PI / 2, Math.PI / 2); pill.lineTo(-rw + rr, rh); pill.absarc(-rw + rr, 0, rh, Math.PI / 2, 3 * Math.PI / 2);
  const pts = pill.getPoints(40).map(p => V3(p.x, p.y, 0)); const lm = new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({color: new THREE.Color(0.2, 0.95, 0.8), transparent: true, blending: THREE.AdditiveBlending, depthTest: false}));
  const inner = new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(pts.map(p => V3(p.x * 0.88, p.y * 0.8, 0))), lm.material.clone()); toggle.add(lm, inner);
  const knob = new THREE.Sprite(new THREE.SpriteMaterial({map: glowTex, blending: THREE.AdditiveBlending, depthTest: false, transparent: true, depthWrite: false})); knob.scale.setScalar(1.0); toggle.add(knob); toggle.userData = {lm, inner, knob}; }
toggle.renderOrder = 8; toggle.children.forEach(c => c.renderOrder = 8); scene.add(toggle);

// ---------- captions ----------
const CAPS = [[0.15, 1.4, 'THIS IS A <em>DREAM.</em>'], [1.5, 2.9, 'AND IT FEELS <em>REAL.</em>'], [3.1, 5.4, 'SAME BRAIN.<br>DIFFERENT <em>STATE.</em>'], [5.8, 8.2, 'YOUR LOGIC CENTRE<br>SWITCHES <em>OFF.</em>']];
const elCap = document.getElementById('cap'), elFlash = document.getElementById('flash'), elBar = document.getElementById('bar'), elTitle = document.getElementById('title');

// ---------- camera ----------
const keys = (arr, tl) => { for (let i = 0; i < arr.length - 1; i++) if (tl <= arr[i + 1][0]) return lerp(arr[i][1], arr[i + 1][1], sm((tl - arr[i][0]) / (arr[i + 1][0] - arr[i][0]))); return arr[arr.length - 1][1]; };
const DIST = [[[0, 12], [1.4, 16], [2.3, 19], [2.45, 18]], [[0, 22], [1.0, 22], [2.05, 16], [2.2, 15]], [[0, 25], [1.2, 22], [2.6, 16]]];
function frameAt(t) {
  let i = worlds.length - 1; for (let k = 0; k < worlds.length - 1; k++) if (t < worlds[k + 1].A) { i = k; break; }
  const s = worlds[i], tl = t - s.A, last = i === worlds.length - 1, td = s.D - TR, tick = tickAt(t); let bump = 0;
  const dist = keys(DIST[i], Math.min(tl, td)) + (!last && tl > td ? lerp(0, 3, sm((tl - td) / TR)) : 0); if (!last && tl > td) bump = Math.sin(Math.PI * (tl - td) / TR);
  let target = tick.clone();
  if (i === 1) target.lerp(WBr.P(0.5, 0.5), 0.55 * (1 - sm(tl / 1.6))); if (i === 2) target.lerp(WH.P(0.68, 0.23), 0.65 * sm((tl - 0.1) / 0.5) * (1 - sm((tl - 1.7) / 0.6)));
  return {i, s, tl, tick, target, dist, bump};
}
const beat = p => Math.exp(-p * 6.0);
window.renderAt = t => {
  t = clamp(t, 0, DUR); const f = frameAt(t), {s, tl, tick, bump} = f; const wob = f.i === 0 ? 1 : 1;
  // ---- parts ----
  const pr = (wi, name, o) => { const p = worlds[wi].parts[name]; p.position.copy(p.userData.rest).add(o.p || V3(0, 0, 0)); p.rotation.z = o.rz || 0; p.scale.setScalar(o.s || 1); return p; };
  worlds.forEach((w, wi) => {
    const d = f.target.z + f.dist - w.z, lt = t - w.A, op = sm((d - 1.2) / 4) * (1 - sm((d - 38) / 10));
    const U = w.base.material.uniforms; const all = [w.base, ...Object.values(w.parts)]; all.forEach(m => { const u = m.material.uniforms; u.uOp.value = op; u.uTime.value = t; m.visible = op > 0.004; u.uPulse.value.set(0.5, 0.5, -1, 0); u.uRev.value.set(0.5, 0.5, -1); u.uSpark.value = 0; u.uSplit.value.set(2, 1, 1); u.uReg.value.set(2, 2, 2, 2); u.uRegG.value.set(1, 1); u.uRed.value = 1; u.uTeal.value = 1; });
    const setAll = fn => all.forEach(m => fn(m.material.uniforms));
    if (wi === 0) {
      setAll(u => { u.uRed.value = 1.3 + 1.2 * (0.5 + 0.5 * Math.sin(lt * 8)); });
      WB.base.material.uniforms.uTeal.value = 0.12; WB.base.material.uniforms.uRed.value = 0.2; // drop the hatch panel; the action is in the parts
      WB.parts.fig.material.uniforms.uTeal.value = 1.7; WB.parts.frames.material.uniforms.uTeal.value = 1.4;
      const e = ease(lt / 1.4); pr(0, 'fig', {s: 1.25, p: figOffset(0, lt), rz: lerp(0.9, 0, e) + 0.06 * Math.sin(lt * 2.2)}); pr(0, 'frames', {p: V3(0.15 * lt, 0.7 * lt + 0.12 * Math.sin(lt * 1.7), 0), rz: -0.025 * lt}); pr(0, 'bed', {s: 1 + 0.008 * Math.sin(lt * 3), p: V3(0, 0, 0)});
      // the sleeper stays: breathing glow on the bed while the dream body leaves
      WB.parts.bed.material.uniforms.uTeal.value = 1.0 + 0.25 * Math.sin(lt * 3);
    } else if (wi === 1) {
      const U2 = w.base.material.uniforms; const sp = clamp((lt - 0.2) / 1.2);
      setAll(u => { u.uSplit.value.set(0.5, lerp(1.0, 1.9, sp), lerp(1.0, 0.7, sp)); u.uSpark.value = 0.9; const ph = (lt * 1.15) % 1; u.uPulse.value.set(0.5, 0.55, ph * 1.0, 0.55); });
      pr(1, 'fig', {p: figOffset(1, lt), rz: 0.25 * lt});
    } else {
      const rv = clamp(lt / 0.9), off = sm((lt - 0.9) / 0.8); // lobe switches OFF
      setAll(u => { u.uReg.value.set(...toTex([0.47, 0.06, 0.67, 0.40])); u.uRegG.value.set(lerp(2.6, 0.12, off), lerp(1.1, 0.25, off)); u.uRed.value = 1.0 + 0.5 * Math.sin(lt * 9) * (1 - off); u.uRev.value.set(0.575, 0.78, rv * 1.35); });
      pr(2, 'fig', {p: figOffset(2, lt), rz: 0.15 * Math.sin(lt * 1.4)});
    }
  });
  // ---- camera ----
  const orb = Math.min(1, f.dist / 14); const ox = 2.0 * Math.sin(t * 0.95) * orb, oy = 0.8 * Math.sin(t * 0.7 + 1) * orb;
  camera.fov = 40 + 10 * bump; camera.updateProjectionMatrix();
  camera.position.set(f.target.x + ox, f.target.y + oy, f.target.z + f.dist);
  camera.up.set(0, 1, 0); camera.lookAt(f.target.x, f.target.y, f.target.z); camera.rotateZ(0.02 * Math.sin(t * 0.8) + (f.i % 2 ? 1 : -1) * 0.4 * bump);
  const cz = camera.position.z; fmat.uniforms.uCamZ.value = cz; fmat.uniforms.uTime.value = t; fmat.uniforms.uAmp.value = 0.12 + 1.1 * bump; smat.uniforms.uCamZ.value = cz; smat.uniforms.uSpeed.value = bump;
  worlds.forEach((w, wi) => { const d = f.target.z + f.dist - w.z; fieldMats[wi].uniforms.uOp.value = sm((d - 1.2) / 4) * (1 - sm((d - 40) / 12)); fieldMats[wi].uniforms.uTime.value = t; });
  // ---- tick + trail ----
  tickSp.position.copy(tick); tickSp.scale.setScalar(0.55 + 0.25 * (0.5 + 0.5 * Math.sin(t * 10)));
  const camDir = V3(0, 0, -1); for (let i = 0; i < NT; i++) { const tau = i / (NT - 1) * 1.8, p = tickAt(Math.max(0, t - tau)), q = tickAt(Math.max(0, t - tau - 0.03)), tan = p.clone().sub(q); tan.z *= 0.2; const side = V3(-tan.y, tan.x, 0).normalize(); if (!isFinite(side.x)) side.set(1, 0, 0);
    const dc = p.distanceTo(camera.position), w = (0.0042 * dc) * (1 - tau / 1.8) + 0.004, a = Math.pow(1 - tau / 1.8, 1.4) * (t - tau > 0 ? 1 : 0) * 0.95 * sm((dc - 5) / 5); trailPos.set([p.x + side.x * w, p.y + side.y * w, p.z, p.x - side.x * w, p.y - side.y * w, p.z], i * 6); trailA[i * 2] = a; trailA[i * 2 + 1] = a; }
  tg.attributes.position.needsUpdate = true; tg.attributes.aA.needsUpdate = true;
  // ---- toggle ----
  { const tl3 = t - WH.A, on = tl3 > 0.3 && tl3 < 2.7, flip = sm((tl3 - 0.95) / 0.45); toggle.visible = on; const pos = WH.P(0.68, 0.23); toggle.position.set(pos.x, pos.y, pos.z + 0.4); toggle.scale.setScalar(1.15 * sm((tl3 - 0.3) / 0.3));
    const u = toggle.userData; u.knob.position.set(lerp(0.5, -0.5, flip), 0, 0.01); u.knob.material.color.setRGB(1, lerp(0.7, 1, flip) , lerp(0.7, 1, flip)); u.knob.material.opacity = lerp(1, 0.35, flip); u.lm.material.color.setRGB(lerp(1, 0.2, flip), lerp(0.2, 0.95, flip), lerp(0.15, 0.8, flip)); }
  renderer.render(scene, camera);
  elFlash.style.opacity = 0; elBar.style.width = (100 * t / 29.4).toFixed(2) + '%';
  elTitle.innerHTML = 'WHY DO <em class="' + (t > 0.9 && t < 2.2 ? 'on' : '') + '">DREAMS</em> FEEL <em>REAL?</em>';
  let cs = ''; CAPS.forEach(([a, b, txt]) => { const k = sm((t - a) / 0.2) * (1 - sm((t - (b - 0.2)) / 0.2)); if (k > 0.01) cs += `<div style="opacity:${k.toFixed(3)};transform:translateY(${((1 - k) * 12).toFixed(1)}px)">${txt}</div>`; });
  elCap.innerHTML = cs;
};
window.ready = true; window.renderAt(0);
