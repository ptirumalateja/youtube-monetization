// Scene 2: smooth skinned wire-mesh hand (bone white), predicted ghost (teal), deformable planes of predicted space,
// red contact point that bends the space. Opening 01A-01D of the storyboard.
import * as THREE from 'three';
const QP = new URLSearchParams(location.search); const W = +(QP.get('w') || 1080), H = +(QP.get('h') || 1920), LEAD = 0.5;
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x)), sm = x => { x = clamp(x); return x * x * (3 - 2 * x); }, lerp = (a, b, t) => a + (b - a) * t;
const WHITE = new THREE.Color(1.25, 1.18, 1.02), TEAL = new THREE.Color(0.12, 0.9, 0.78), RED = new THREE.Color(1.0, 0.16, 0.12);

const renderer = new THREE.WebGLRenderer({antialias: true, preserveDrawingBuffer: true});
renderer.setPixelRatio(1); renderer.setSize(W, H); renderer.setClearColor(0x02050a, 1);
document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(38, W / H, 0.1, 400);

// ---------- hand data ----------
const data = await (await fetch('../hand/hand.json')).json();
const NV = data.v.length / 3, V0 = new Float32Array(data.v), IDX = new Uint32Array(data.f), BI = new Uint16Array(data.bi), BW = new Float32Array(data.bw);
const FJ = data.fingerJoints, TH = data.thumb;
const T = p => new THREE.Matrix4().makeTranslation(p[0], p[1], p[2]);
const Rz = a => new THREE.Matrix4().makeRotationZ(a), Ry = a => new THREE.Matrix4().makeRotationY(a);
const pivot = (P, R) => T(P).multiply(R).multiply(T([-P[0], -P[1], -P[2]]));
const POINT = {flex: [[0.0, 0.04, 0.0], [1.25, 1.4, 0.9], [1.35, 1.45, 0.9], [1.4, 1.4, 0.8]], spread: [0.03, -0.02, -0.1, -0.2], th: {abd: -0.55, f: [0.55, 0.5]}};
function boneMats(p) {
  const M = []; for (let i = 0; i < 17; i++) M.push(new THREE.Matrix4());
  for (let f = 0; f < 4; f++) {
    const A0 = pivot(FJ[f][0], Ry(p.spread[f]).multiply(Rz(-p.flex[f][0])));
    const A1 = A0.clone().multiply(pivot(FJ[f][1], Rz(-p.flex[f][1])));
    const A2 = A1.clone().multiply(pivot(FJ[f][2], Rz(-p.flex[f][2])));
    M[2 + 3 * f] = A0; M[3 + 3 * f] = A1; M[4 + 3 * f] = A2;
  }
  const B0 = pivot(TH[0], Ry(p.th.abd)); const B1 = B0.clone().multiply(pivot(TH[1], Rz(-p.th.f[0]))); const B2 = B1.clone().multiply(pivot(TH[2], Rz(-p.th.f[1])));
  M[14] = B0; M[15] = B1; M[16] = B2;
  return M;
}
const tipNeutral = new THREE.Vector3(FJ[0][3][0] + 0.55, FJ[0][3][1], FJ[0][3][2]);
const ARR = new Float32Array(17 * 16);
function skin(posArr, M) {
  M.forEach((m, i) => ARR.set(m.elements, i * 16));
  for (let v = 0; v < NV; v++) {
    const x = V0[3 * v], y = V0[3 * v + 1], z = V0[3 * v + 2]; let ox = 0, oy = 0, oz = 0;
    for (let k = 0; k < 4; k++) {
      const w = BW[4 * v + k]; if (w === 0) continue; const o = BI[4 * v + k] * 16;
      ox += w * (ARR[o] * x + ARR[o + 4] * y + ARR[o + 8] * z + ARR[o + 12]);
      oy += w * (ARR[o + 1] * x + ARR[o + 5] * y + ARR[o + 9] * z + ARR[o + 13]);
      oz += w * (ARR[o + 2] * x + ARR[o + 6] * y + ARR[o + 10] * z + ARR[o + 14]);
    }
    posArr[3 * v] = ox; posArr[3 * v + 1] = oy; posArr[3 * v + 2] = oz;
  }
}
const lineMat = c => new THREE.ShaderMaterial({
  uniforms: {uColor: {value: c}, uAlpha: {value: 1}}, transparent: true, depthTest: true, depthWrite: false, blending: THREE.AdditiveBlending,
  vertexShader: `attribute vec3 aN; varying vec3 vN; varying vec3 vV; varying vec3 vA;
    void main(){ vA=aN; vec4 mv=modelViewMatrix*vec4(position,1.0); vN=normalize(normalMatrix*normal); vV=normalize(-mv.xyz); gl_Position=projectionMatrix*mv; }`,
  fragmentShader: `uniform vec3 uColor; uniform float uAlpha; varying vec3 vN; varying vec3 vV; varying vec3 vA;
    float lm(float v,float sp,float w){ float x=v/sp; float d=abs(fract(x-0.5)-0.5)/max(fwidth(x),1e-4); return 1.0-clamp(d-w,0.0,1.0); }
    void main(){
      float ndv=abs(dot(normalize(vN),normalize(vV))); float rim=pow(1.0-ndv,2.2);
      float l1=lm(vA.x,0.30,0.45), l2=lm(vA.z,0.55,0.35)*0.6, l3=lm(vA.y,0.55,0.35)*0.45;
      float lines=max(l1,max(l2,l3)); float arm=smoothstep(-13.0,-2.5,vA.x);
      float a=(lines*(0.38+1.5*rim)+rim*0.42+0.025)*arm*uAlpha;
      gl_FragColor=vec4(uColor*a,1.0); }`
});
function makeHand(color) {
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(V0), 3)); g.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(NV * 3), 3));
  g.setAttribute('aN', new THREE.BufferAttribute(V0, 3)); g.setIndex(new THREE.BufferAttribute(IDX, 1));
  const pre = new THREE.Mesh(g, new THREE.MeshBasicMaterial({colorWrite: false})), ln = new THREE.Mesh(g, lineMat(color));
  for (const m of [pre, ln]) { m.matrixAutoUpdate = false; m.frustumCulled = false; scene.add(m); } pre.renderOrder = 0; ln.renderOrder = 3;
  return {g, pre, ln};
}
const real = makeHand(WHITE), ghost = makeHand(TEAL), trail1 = makeHand(TEAL), trail2 = makeHand(TEAL);
function placeHand(h, tipTarget, pose, roll, alpha) {
  const M = boneMats(pose); skin(h.g.attributes.position.array, M); h.g.attributes.position.needsUpdate = true; h.g.computeVertexNormals();
  const R = new THREE.Matrix4().makeRotationFromEuler(new THREE.Euler(roll, 0.05, 0.03, 'XYZ'));
  const tip = tipNeutral.clone().applyMatrix4(M[4]).applyMatrix4(R); const pos = tipTarget.clone().sub(tip);
  const mat = R.clone().setPosition(pos); h.pre.matrix.copy(mat); h.ln.matrix.copy(mat); h.ln.material.uniforms.uAlpha.value = alpha;
  h.pre.visible = h.ln.visible = alpha > 0.002;
}
// ---------- planes of predicted space (deformable), field plane, target ----------
const TARGET = new THREE.Vector3(33.5, 2.2, 0);
const planeMat = (tint, base) => new THREE.ShaderMaterial({
  uniforms: {uT: {value: TARGET}, uPinch: {value: 0}, uTime: {value: 0}, uTint: {value: tint}, uBase: {value: base}, uFade: {value: 1}, uSize: {value: new THREE.Vector2(18, 28)}},
  transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
  vertexShader: `uniform vec3 uT; uniform float uPinch; uniform float uTime; varying vec2 vUv; varying float vG; varying float vD;
    void main(){ vUv=uv; vec4 wp=modelMatrix*vec4(position,1.0); vec3 n=normalize((modelMatrix*vec4(0.,0.,1.,0.)).xyz);
      vec3 d=wp.xyz-uT; float r=length(d); float g=exp(-(r*r)/110.0); vG=g;
      wp.xyz-=d*0.42*uPinch*g; wp.xyz+=n*(5.5*uPinch*g + 0.35*sin(r*0.6-uTime*3.0)*g*uPinch);
      vD=r; gl_Position=projectionMatrix*viewMatrix*wp; }`,
  fragmentShader: `uniform vec3 uTint; uniform float uBase; uniform float uFade; uniform vec2 uSize; uniform float uPinch; varying vec2 vUv; varying float vG; varying float vD;
    float lm(float v,float sp,float w){ float x=v/sp; float d=abs(fract(x-0.5)-0.5)/max(fwidth(x),1e-4); return 1.0-clamp(d-w,0.0,1.0); }
    void main(){ vec2 p=vUv*uSize; float gl=max(lm(p.x,1.6,0.5),lm(p.y,1.6,0.5));
      vec2 e=min(vUv,1.0-vUv); float edge=1.0-smoothstep(0.0,0.025,min(e.x,e.y));
      float a=(uBase*(0.55+0.45*vG*uPinch)+gl*0.16*(1.0+2.2*vG*uPinch)+edge*0.45)*uFade;
      gl_FragColor=vec4(uTint*a,1.0); }`
});
const planes = [];
[[14, 0.28, 0.9], [21, -0.16, 0.8], [27, 0.22, 1.0]].forEach(([x, ry, s], i) => {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(18, 28, 46, 70), planeMat(TEAL.clone().multiplyScalar(0.9), 0.045)); m.position.set(x, 1.5 - i * 0.3, -1.2 + i * 0.6); m.rotation.y = Math.PI / 2 + ry; m.rotation.x = 0.04 * (i - 1);
  m.renderOrder = 2; scene.add(m); planes.push(m);
});
const field = new THREE.Mesh(new THREE.PlaneGeometry(34, 44, 90, 110), new THREE.ShaderMaterial({
  uniforms: {uT: {value: TARGET}, uPinch: {value: 0}, uTime: {value: 0}, uFlare: {value: 0}}, transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
  vertexShader: `varying vec2 vUv; varying vec3 vW; void main(){ vUv=uv; vec4 wp=modelMatrix*vec4(position,1.0); vW=wp.xyz; gl_Position=projectionMatrix*viewMatrix*wp; }`,
  fragmentShader: `uniform vec3 uT; uniform float uPinch; uniform float uTime; uniform float uFlare; varying vec2 vUv; varying vec3 vW;
    float lm(float v,float sp,float w){ float x=v/sp; float d=abs(fract(x-0.5)-0.5)/max(fwidth(x),1e-4); return 1.0-clamp(d-w,0.0,1.0); }
    void main(){ vec3 d=vW-uT; float r=length(d.yz+vec2(0.0,d.x*0.0)); float rr=length(d); float g=exp(-(rr*rr)/7.0);
      float y=vW.y+ (vW.y-uT.y)*(-0.9*uPinch*g) ; float flow=lm(y+0.35*sin(vW.z*0.35+uTime)*g*uPinch,0.62,0.45);
      float ring=0.0; for(int i=0;i<5;i++){ float ph=fract(uTime*0.45+float(i)/5.0); float rad=ph*6.5; ring+=exp(-pow((rr-rad)/0.1,2.0))*(1.0-ph)*(0.18+0.55*uPinch); }
      float edge=exp(-rr/30.0);
      vec3 teal=vec3(0.12,0.9,0.78)*flow*0.4*edge*(0.35+0.8*uPinch); vec3 red=vec3(1.0,0.18,0.12)*(ring*0.85+ g*0.35*uPinch + uFlare*exp(-rr*1.4)*1.1);
      gl_FragColor=vec4(teal+red,1.0); }`
}));
field.position.copy(TARGET).add(new THREE.Vector3(0.3, 0, 0)); field.rotation.y = -1.05; field.renderOrder = 1; scene.add(field);
const glowTex = (() => { const c = document.createElement('canvas'); c.width = c.height = 128; const x = c.getContext('2d'), g = x.createRadialGradient(64, 64, 0, 64, 64, 64); g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(0.2, 'rgba(255,90,70,0.8)'); g.addColorStop(1, 'rgba(255,40,30,0)'); x.fillStyle = g; x.fillRect(0, 0, 128, 128); return new THREE.CanvasTexture(c); })();
const core = new THREE.Sprite(new THREE.SpriteMaterial({map: glowTex, blending: THREE.AdditiveBlending, depthTest: false, transparent: true})); core.position.copy(TARGET).add(new THREE.Vector3(-0.4, 0, 0.2)); core.renderOrder = 5; scene.add(core);
// dust
const pg = new THREE.BufferGeometry(), pp = new Float32Array(900 * 3); for (let i = 0; i < 900; i++) { pp[3 * i] = lerp(-10, 48, Math.random()); pp[3 * i + 1] = lerp(-14, 18, Math.random()); pp[3 * i + 2] = lerp(-14, 10, Math.random()); }
pg.setAttribute('position', new THREE.BufferAttribute(pp, 3));
const dust = new THREE.Points(pg, new THREE.PointsMaterial({size: 2.2, sizeAttenuation: false, color: 0x4de8d0, transparent: true, opacity: 0.55, blending: THREE.AdditiveBlending, depthWrite: false, depthTest: false})); dust.renderOrder = 4; scene.add(dust);

// ---------- timeline ----------
const tipX = t => { const u = clamp((t - 0.05) / 2.0); return lerp(8.0, TARGET.x - 0.35, 1 - Math.pow(1 - u, 3)); };
const CAM = [[0, 9, 3.0, 50, 10, 2.0, 0, 42], [0.6, 14, 4.0, 46, 17, 2.2, 0, 40], [1.1, 24, 3.5, 34, 28, 2.2, 0, 36], [1.6, 27, 3.0, 26, 31.5, 2.2, 0, 32], [2.4, 24, 4.0, 36, 26, 2.4, 0, 38], [3.2, 20, 5, 46, 22, 2.5, 0, 42]];
function camAt(t) { let i = 0; while (i < CAM.length - 2 && t > CAM[i + 1][0]) i++; const a = CAM[i], b = CAM[i + 1], u = sm((t - a[0]) / (b[0] - a[0])); return a.map((v, k) => lerp(v, b[k], u)); }
window.renderAt = async (t) => {
  const c = camAt(Math.min(t, 3.2)); camera.position.set(c[1], c[2], c[3]); camera.fov = c[7]; camera.updateProjectionMatrix(); camera.lookAt(c[4], c[5], c[6]);
  const roll = -0.3, lead = tipX(t + LEAD), cur = tipX(t);
  const pinch = sm((t - 0.35) / 1.15) * (1 - 0.25 * sm((t - 2.6) / 0.6)), flare = Math.exp(-Math.max(0, t - 1.5) / 0.22) * (t > 1.5 ? 1 : 0) * 0.8 + Math.exp(-Math.max(0, t - 2.0) / 0.3) * (t > 2.0 ? 1 : 0);
  const conv = sm((t - 1.75) / 0.5);
  placeHand(real, new THREE.Vector3(cur, TARGET.y, 0), POINT, roll, 1.0);
  const sep = 1 - conv; placeHand(ghost, new THREE.Vector3(lead, TARGET.y + 3.4 * sep, -3.2 * sep), POINT, roll, 0.8 * (1 - 0.75 * conv));
  placeHand(trail1, new THREE.Vector3(tipX(t + LEAD + 0.18), TARGET.y + 3.4 * sep, -3.2 * sep), POINT, roll, 0.22 * (1 - conv));
  placeHand(trail2, new THREE.Vector3(tipX(t + LEAD + 0.36), TARGET.y + 3.4 * sep, -3.2 * sep), POINT, roll, 0.12 * (1 - conv));
  planes.forEach((p, i) => { p.material.uniforms.uPinch.value = pinch; p.material.uniforms.uTime.value = t; p.material.uniforms.uFade.value = sm((t - 0.35) / 0.5) * (1 - 0.92 * sm((t - 1.15) / 0.5)); });
  field.material.uniforms.uPinch.value = pinch; field.material.uniforms.uTime.value = t; field.material.uniforms.uFlare.value = flare;
  const ps = 1.0 + 3.5 * flare + 0.8 * pinch; core.scale.setScalar(0.9 + ps * 0.55); core.material.opacity = 0.3 + 0.35 * pinch + 0.25 * flare;
  dust.position.x = -t * 0.8; renderer.domElement.style.opacity = String(0.25 + 0.75 * sm(t / 0.25));
  const tt = document.getElementById('title'); const n = clamp((t - 1.55) / 0.35); tt.innerHTML = n > 0 ? `<div style="opacity:${n}">YOUR BRAIN<br><em>CHEATS.</em></div>` : '';
  renderer.render(scene, camera); return true;
};
// ---- isolated hand debug: window.renderHand(poseName, yaw, pitch) ----
const OPEN = {flex: [[0.1, 0.18, 0.08], [0.06, 0.14, 0.06], [0.1, 0.2, 0.08], [0.16, 0.24, 0.1]], spread: [0.3, 0.05, -0.2, -0.42], th: {abd: 0.5, f: [0.12, 0.08]}};
const POSES = {point: POINT, open: OPEN};
window.renderHand = async (poseName, yaw, pitch, dist = 46) => {
  [...planes, field, core, dust, ghost.pre, ghost.ln, trail1.pre, trail1.ln, trail2.pre, trail2.ln].forEach(o => o.visible = false);
  renderer.domElement.style.opacity = '1'; document.getElementById('title').innerHTML = '';
  const M = boneMats(POSES[poseName]); skin(real.g.attributes.position.array, M); real.g.attributes.position.needsUpdate = true; real.g.computeVertexNormals();
  real.pre.matrix.identity(); real.ln.matrix.identity(); real.ln.material.uniforms.uAlpha.value = 1; real.pre.visible = real.ln.visible = true;
  const cx = 2, cy = 0, cz = 2; camera.fov = 30; camera.updateProjectionMatrix();
  camera.position.set(cx + dist * Math.sin(yaw) * Math.cos(pitch), cy + dist * Math.sin(pitch), cz + dist * Math.cos(yaw) * Math.cos(pitch)); camera.lookAt(cx, cy, cz);
  renderer.render(scene, camera); return true;
};
window.ready = true;
