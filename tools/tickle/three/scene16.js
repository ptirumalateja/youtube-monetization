// "Why does time fly when you're having fun?" (Time Flies rebuild, 22 s, 9:16). Same engine as the dreams reel: depth-displaced Meta contour frames, one red time thread (the figure's tick) carried through every world,
// worlds aligned on the tick and dissolved in place; one signature motion per scene (rotating clock faces, polaroids lighting along the detour, dolly into the Droste photo).
import * as THREE from 'three';
const QP = new URLSearchParams(location.search); const W = +(QP.get('w') || 1080), H = +(QP.get('h') || 1920), DUR = +(QP.get('dur') || 22.0);
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x)), sm = x => { x = clamp(x); return x * x * (3 - 2 * x); }, lerp = (a, b, t) => a + (b - a) * t;
const ease = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; }, easeOut = x => 1 - Math.pow(1 - clamp(x), 3);
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const renderer = new THREE.WebGLRenderer({antialias: true, preserveDrawingBuffer: true}); renderer.setPixelRatio(1); renderer.setSize(W, H); renderer.setClearColor(0x02050a, 1);
document.body.appendChild(renderer.domElement); document.body.style.width = W + 'px'; document.body.style.height = H + 'px';
const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(40, W / H, 0.1, 1400);
const MT = await (await fetch('./assets/dreams/tf_meta.json')).json();
const loadImg = src => new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = src; });
const AXY = 0.9, S = 10, TR = 0.55;

const partMat = (tex, dep, ds, d0, asp) => new THREE.ShaderMaterial({
  uniforms: {uTex: {value: tex}, uDep: {value: dep}, uDS: {value: ds}, uD0: {value: d0}, uOp: {value: 1}, uRed: {value: 1}, uTeal: {value: 1}, uTexel: {value: new THREE.Vector2(1 / 1000, 1 / 600)}, uTime: {value: 0}, uAsp: {value: asp},
    uExcl: {value: [0, 0, 0, 0].map(() => new THREE.Vector4(2, 2, 2, 2))}, uReg: {value: new THREE.Vector4(2, 2, 2, 2)}, uRegG: {value: new THREE.Vector2(1, 1)}, uPulse: {value: new THREE.Vector4(0.5, 0.5, -1, 0)}, uRev: {value: new THREE.Vector3(0.5, 0.5, -1)}, uSpark: {value: 0}},
  transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
  vertexShader: `uniform sampler2D uDep; uniform float uDS,uD0; uniform vec2 uTexel; varying vec2 vUv; varying float vG;
    void main(){ vUv=uv; float d=texture2D(uDep,uv).r; vec3 p=position; p.z+=(d-uD0)*uDS;
      float gx=texture2D(uDep,uv+vec2(uTexel.x*3.0,0.0)).r-texture2D(uDep,uv-vec2(uTexel.x*3.0,0.0)).r, gy=texture2D(uDep,uv+vec2(0.0,uTexel.y*3.0)).r-texture2D(uDep,uv-vec2(0.0,uTexel.y*3.0)).r; vG=length(vec2(gx,gy));
      gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.0); }`,
  fragmentShader: `uniform sampler2D uTex; uniform float uOp,uRed,uTeal,uTime,uAsp,uSpark; uniform vec4 uExcl[4]; uniform vec4 uReg; uniform vec2 uRegG; uniform vec4 uPulse; uniform vec3 uRev; varying vec2 vUv; varying float vG;
    float box(vec2 p, vec4 b){ vec2 a=smoothstep(b.xy-0.004,b.xy+0.004,p), c=1.0-smoothstep(b.zw-0.004,b.zw+0.004,p); return a.x*a.y*c.x*c.y; }
    float hash(vec2 p){ return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
    void main(){ vec3 c=texture2D(uTex,vUv).rgb; float rm=clamp((c.r-0.55*c.g-0.04)*3.0,0.0,1.0);
      float inR=box(vUv,uReg); float tg=uTeal*mix(1.0,uRegG.y,inR), rg=uRed*mix(1.0,uRegG.x,inR); c*=mix(tg,rg,rm);
      float sp=1.0+uSpark*rm*(hash(floor(vUv*vec2(900.0,600.0)/3.0)+floor(uTime*14.0))-0.5)*2.2; c*=max(sp,0.15);
      if(uPulse.z>=0.0){ float d=length((vUv-uPulse.xy)*vec2(uAsp,1.0)); float ring=exp(-pow((d-uPulse.z)/0.05,2.0)); c*=1.0+uPulse.w*ring*3.0; }
      float a=1.0; if(uRev.z>=0.0){ float d=length((vUv-uRev.xy)*vec2(uAsp,1.0)); a=1.0-smoothstep(uRev.z-0.12,uRev.z,d); }
      for(int i=0;i<4;i++){ a*=1.0-box(vUv,uExcl[i]); }
      vec2 e=min(vUv,1.0-vUv); float f=smoothstep(0.0,0.03,min(e.x,e.y)); float st=1.0-0.8*smoothstep(0.06,0.2,vG);
      gl_FragColor=vec4(c*f*st*a*uOp,1.0); }`
});
const worlds = [];
// k = frame key (assets/dreams/tf_<k>), A = start (s), D = duration, w = world width
const WD = [{k: 'phone', w: 15, A: 0.0, D: 2.9, ds: 3}, {k: 'runner', w: 14, A: 2.9, D: 1.6, ds: 3}, {k: 'brain', w: 14, A: 4.5, D: 1.7, ds: 2.5}, {k: 'fly', w: 15, A: 6.2, D: 2.1, ds: 3}, {k: 'swirl', w: 14, A: 8.3, D: 1.7, ds: 3},
  {k: 'strip', w: 14, A: 10.0, D: 1.6, ds: 3}, {k: 'ribbon', w: 15, A: 11.6, D: 2.3, ds: 3}, {k: 'geo', w: 15, A: 13.9, D: 3.3, ds: 2}, {k: 'droste', w: 14, A: 17.2, D: 1.5, ds: 3}, {k: 'gear', w: 14, A: 18.7, D: 1.5, ds: 3}, {k: 'eye', w: 14, A: 20.2, D: 1.8, ds: 3}];
// image-space boxes (u0,v0,u1,v1; v down) for parts that move on their own
const PARTS = {
  runner: {runner: [0.30, 0.04, 0.76, 0.97], icons: [0.0, 0.12, 0.30, 0.80]}, fly: {dust: [0.0, 0.08, 0.50, 0.70], clocks: [0.60, 0.10, 0.90, 0.40]}, swirl: {swirl: [0.12, 0.10, 0.88, 1.0]}, gear: {dial: [0.33, 0.24, 0.67, 0.80]}, eye: {dial: [0.33, 0.25, 0.67, 0.80]},
  phone: {top: [0.36, 0.24, 0.52, 0.58]},
};
const readDepthAt = (img, u, v) => { const c = document.createElement('canvas'); c.width = img.width; c.height = img.height; const x = c.getContext('2d'); x.drawImage(img, 0, 0); return x.getImageData(clamp(Math.round(u * img.width), 0, img.width - 1), clamp(Math.round(v * img.height), 0, img.height - 1), 1, 1).data[0] / 255; };
const toTex = b => [b[0], 1 - b[3], b[2], 1 - b[1]];
function subGeom(w, h, b) { const g = new THREE.PlaneGeometry((b[2] - b[0]) * w, (b[3] - b[1]) * h, Math.max(2, Math.round((b[2] - b[0]) * w * 12)), Math.max(2, Math.round((b[3] - b[1]) * h * 12))); const uv = g.attributes.uv; for (let i = 0; i < uv.count; i++) { const ux = uv.getX(i), uy = uv.getY(i); uv.setXY(i, b[0] + (b[2] - b[0]) * ux, 1 - b[1] - (b[3] - b[1]) * (1 - uy)); } return g; }
// figure / tick anchor per frame (u, v) in the frame
const ANC = {phone: [0.547, 0.69], runner: [0.5, 0.45], brain: [0.516, 0.69], fly: [0.586, 0.52], swirl: [0.5, 0.62], strip: [0.55, 0.61], ribbon: [0.61, 0.33], geo: [0.60, 0.84], droste: [0.5, 0.54], gear: [0.5, 0.5], eye: [0.5, 0.52]};
for (let i = 0; i < WD.length; i++) {
  const s = WD[i], m = MT[s.k], [pw, ph] = m.size, h = s.w * ph / pw, asp = pw / ph;
  const tex = await new THREE.TextureLoader().loadAsync(`./assets/dreams/tf_${s.k}.jpg`); tex.colorSpace = THREE.NoColorSpace; tex.anisotropy = 8;
  const dimg = await loadImg(`./assets/dreams/tf_${s.k}_d.png`); const dep = new THREE.Texture(dimg); dep.needsUpdate = true; dep.colorSpace = THREE.NoColorSpace; dep.minFilter = dep.magFilter = THREE.LinearFilter; dep.generateMipmaps = false;
  Object.assign(s, {i, h, asp, z: -S * i, C: V3(0, AXY, -S * i), parts: {}}); const d0 = readDepthAt(dimg, ANC[s.k][0], ANC[s.k][1]);
  const mk = (geom, excl) => { const mat = partMat(tex, dep, s.ds, d0, asp); mat.uniforms.uTexel.value.set(1 / dimg.width, 1 / dimg.height); excl.forEach((b, j) => mat.uniforms.uExcl.value[j].set(...toTex(b))); const me = new THREE.Mesh(geom, mat); me.frustumCulled = false; me.renderOrder = 3; scene.add(me); return me; };
  const pb = PARTS[s.k] || {}, names = Object.keys(pb);
  s.base = mk(new THREE.PlaneGeometry(s.w, h, Math.min(260, Math.round(s.w * 12)), Math.max(8, Math.round(Math.min(260, s.w * 12) * h / s.w))), names.map(n => pb[n])); s.base.position.copy(s.C);
  names.forEach(n => { const b = pb[n]; const me = mk(subGeom(s.w, h, b), []); me.userData.rest = V3(s.C.x + ((b[0] + b[2]) / 2 - 0.5) * s.w, s.C.y + (0.5 - (b[1] + b[3]) / 2) * h, s.z); me.position.copy(me.userData.rest); me.material.uniforms.uDS.value = 1.0; s.parts[n] = me; });
  s.P = (u, v) => V3(s.C.x + (u - 0.5) * s.w, s.C.y + (0.5 - v) * h, s.z);
  worlds.push(s);
}
const WK = {}; worlds.forEach(w => WK[w.k] = w);

// ---------- per-world choreography: tick path (uv + height), camera distance, focus, signature motion ----------
const SPEC = {};
const kf = (arr, tl) => { if (tl <= arr[0][0]) return arr[0].slice(1); for (let i = 0; i < arr.length - 1; i++) if (tl <= arr[i + 1][0]) { const k = sm((tl - arr[i][0]) / (arr[i + 1][0] - arr[i][0])); return arr[i].slice(1).map((v, j) => lerp(v, arr[i + 1][j + 1], k)); } return arr[arr.length - 1].slice(1); };
const keys = (arr, tl) => { for (let i = 0; i < arr.length - 1; i++) if (tl <= arr[i + 1][0]) return lerp(arr[i][1], arr[i + 1][1], sm((tl - arr[i][0]) / (arr[i + 1][0] - arr[i][0]))); return arr[arr.length - 1][1]; };
const frameBoxes = (pts, wv = 0.085, hv = 0.15) => pts.map(([u, v]) => [u - wv, v - hv, u + wv, v + hv]);
const GEO_FR = frameBoxes([[0.22, 0.54], [0.35, 0.64], [0.50, 0.72], [0.64, 0.66], [0.78, 0.52]], 0.075, 0.13), RIB_FR = frameBoxes([[0.125, 0.78], [0.27, 0.53], [0.50, 0.50], [0.68, 0.61], [0.73, 0.23], [0.90, 0.33]], 0.085, 0.15);
SPEC.phone = {tick: [[0, 0.49, 0.45, 0.2], [1.4, 0.547, 0.66, 0.3], [2.9, 0.547, 0.66, 0.3]], dist: [[0, 27], [1.5, 21], [2.9, 19]], focus: {uv: [0.5, 0.45], w: [[0, 0.5], [1.5, 0.25], [2.9, 0.2]]},
  fx: (w, lt, op, H) => { H.setAll(u => { u.uRed.value = 1 + 1.6 * H.pulse(5); u.uPulse.value.set(0.49, 0.57, ((lt * 0.8) % 1) * 0.7, 0.7); }); H.pr('top', {p: V3(0.08 * Math.sin(lt * 1.6), 0.12 * Math.sin(lt * 1.9), 0), rz: 0.03 * Math.sin(lt * 1.3)}); }};
SPEC.runner = {tick: [[0, 0.5, 0.835, 0.5], [1.6, 0.52, 0.83, 0.5]], dist: [[0, 18], [1.6, 21]], focus: {uv: [0.5, 0.5], w: [[0, 0.6], [1.6, 0.6]]},
  fx: (w, lt, op, H) => { H.setAll(u => { u.uRed.value = 1 + 1.4 * H.pulse(7); u.uSpark.value = 0.5; }); H.pr('runner', {p: V3(0.25 * lt, 0.18 * lt, 0), rz: -0.02 * lt}); H.pr('icons', {p: V3(-0.5 * lt, 0.1 * Math.sin(lt * 3), 0)}); }};
SPEC.brain = {tick: [[0, 0.516, 0.69, 0.4], [0.9, 0.50, 0.50, 0.3], [1.7, 0.49, 0.28, 0.3]], dist: [[0, 19], [1.7, 15]], focus: {uv: [0.5, 0.35], w: [[0, 0.8], [1.7, 0.8]]},
  fx: (w, lt, op, H) => { H.setAll(u => { u.uRed.value = 1 + 2.2 * H.pulse(8); u.uSpark.value = 0.9; u.uPulse.value.set(0.5, 0.23, ((lt * 0.9) % 1) * 0.5, 0.6); }); }};
SPEC.fly = {tick: [[0, 0.586, 0.52, 0.5], [1.4, 0.80, 0.50, 0.5], [2.1, 0.86, 0.46, 0.5]], dist: [[0, 18], [2.1, 22]], focus: {uv: [0.55, 0.5], w: [[0, 0.6], [2.1, 0.4]]},
  fx: (w, lt, op, H) => { H.setAll(u => { u.uRed.value = 1 + 1.8 * H.pulse(6); u.uSpark.value = 0.4; }); H.pr('dust', {p: V3(-1.6 * lt, 0.15 * Math.sin(lt * 2), 0)}); H.pr('clocks', {p: V3(0.2 * lt, 0.25 * lt, 0)}); }};
SPEC.swirl = {tick: [[0, 0.5, 0.60, 0.5], [1.7, 0.5, 0.60, 0.5]], dist: [[0, 21], [1.7, 14]], focus: {uv: [0.5, 0.5], w: [[0, 0.5], [1.7, 0.7]]},
  fx: (w, lt, op, H) => { H.setAll(u => { u.uRed.value = 1 + 1.8 * H.pulse(7); u.uPulse.value.set(0.5, 0.52, ((lt * 0.9) % 1) * 0.6, 0.8); }); H.pr('swirl', {rz: 0.45 * lt}); }};
SPEC.strip = {tick: [[0, 0.55, 0.61, 0.4], [1.6, 0.72, 0.70, 0.4]], dist: [[0, 15], [1.6, 20]], focus: {uv: [0.5, 0.5], w: [[0, 0.7], [1.6, 0.4]]},
  fx: (w, lt, op, H) => { H.setAll(u => { u.uRed.value = 1 + 1.6 * H.pulse(6); u.uPulse.value.set(0.55, 0.6, ((lt * 0.8) % 1) * 0.7, 0.6); }); w.base.rotation.z = 0.04 * Math.sin(lt * 1.4); }};
SPEC.ribbon = {tick: [[0, 0.125, 0.70, 0.3], [0.5, 0.27, 0.46, 0.3], [1.0, 0.50, 0.43, 0.3], [1.5, 0.68, 0.54, 0.3], [1.9, 0.73, 0.17, 0.3], [2.3, 0.90, 0.26, 0.3]], dist: [[0, 21], [2.3, 19]], focus: {uv: [0.5, 0.5], w: [[0, 0.5], [2.3, 0.5]]},
  fx: (w, lt, op, H) => { const i = Math.min(5, Math.floor(lt / 0.4)), b = RIB_FR[i]; H.setAll(u => { u.uReg.value.set(...toTex(b)); u.uRegG.value.set(2.8, 2.2); u.uRed.value = 1 + 1.2 * H.pulse(6); }); }};
SPEC.geo = {tick: [[0, 0.22, 0.54, 0.3], [0.5, 0.22, 0.54, 0.3], [1.0, 0.35, 0.64, 0.3], [1.5, 0.50, 0.72, 0.3], [2.0, 0.64, 0.66, 0.3], [2.6, 0.78, 0.52, 0.3], [3.3, 0.88, 0.37, 0.3]], dist: [[0, 20], [1.0, 19], [3.3, 20]], focus: {uv: [0.5, 0.5], w: [[0, 0.4], [3.3, 0.4]]},
  fx: (w, lt, op, H) => { const i = Math.min(4, Math.max(0, Math.floor((lt - 0.4) / 0.6))); H.setAll(u => { u.uReg.value.set(...toTex(GEO_FR[i])); u.uRegG.value.set(2.6, 2.4); u.uRed.value = 1 + 1.4 * H.pulse(6); u.uPulse.value.set(0.5, 0.145, ((lt * 0.7) % 1) * 0.55, 0.5); }); }};
SPEC.droste = {tick: [[0, 0.5, 0.54, 0.3], [1.5, 0.5, 0.73, 0.2]], dist: [[0, 20], [1.0, 14], [1.5, 6]], focus: {uv: [0.5, 0.6], w: [[0, 0.2], [1.5, 0.95]]},
  fx: (w, lt, op, H) => { H.setAll(u => { u.uRed.value = 1 + 2 * H.pulse(6); u.uPulse.value.set(0.5, 0.73, ((lt * 0.9) % 1) * 0.5, 0.8); }); }};
SPEC.gear = {tick: [[0, 0.5, 0.50, 0.4], [1.5, 0.5, 0.50, 0.4]], dist: [[0, 16], [1.5, 20]], focus: {uv: [0.5, 0.5], w: [[0, 0.8], [1.5, 0.8]]},
  fx: (w, lt, op, H) => { H.setAll(u => { u.uRed.value = 1 + 1.8 * H.pulse(7); u.uPulse.value.set(0.5, 0.5, ((lt * 0.8) % 1) * 0.5, 0.7); }); H.pr('dial', {rz: 0.9 * lt}); w.base.rotation.z = -0.03 * lt; }};
SPEC.eye = {tick: [[0, 0.503, 0.52, 0.3], [1.8, 0.503, 0.52, 0.3]], dist: [[0, 19], [1.8, 15]], focus: {uv: [0.5, 0.5], w: [[0, 0.8], [1.8, 0.8]]},
  fx: (w, lt, op, H) => { H.setAll(u => { u.uRed.value = 1 + 1.5 * H.pulse(7); }); H.pr('dial', {rz: 0.6 * lt}); }};

// ---------- the tick: one red thread through the whole film ----------
function tickLocal(i, tl) { const [u, v, dy] = kf(SPEC[worlds[i].k].tick, tl); return worlds[i].P(u, v).add(V3(0, dy, 0)); }
function figOffset(i, tl) { return tickLocal(i, tl).sub(tickLocal(i, 0)); }
const fieldMats = worlds.map(s => { const mat = new THREE.ShaderMaterial({uniforms: {uA: {value: s.C.clone()}, uTime: {value: 0}, uOp: {value: 0}}, transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending,
  vertexShader: `varying vec3 vW; void main(){ vec4 wp=modelMatrix*vec4(position,1.0); vW=wp.xyz; gl_Position=projectionMatrix*viewMatrix*wp; }`,
  fragmentShader: `uniform vec3 uA; uniform float uTime,uOp; varying vec3 vW;
    float lm(float v,float sp,float w){ float x=v/sp; float d=abs(fract(x-0.5)-0.5)/max(fwidth(x),1e-4); return 1.0-clamp(d-w,0.0,1.0); }
    void main(){ vec2 d=vW.xy-uA.xy; float r=length(d); float g=exp(-r*r/38.0); float y=vW.y-d.y*0.4*g+0.5*sin(vW.x*0.22+uTime*0.7)*(1.0-0.8*g);
      float l=lm(y,0.36,0.55); float e=(0.08+0.18*g)*uOp*(1.0-smoothstep(10.0,26.0,r)); gl_FragColor=vec4(vec3(0.10,0.80,0.68)*l*e,1.0); }`});
  const p = new THREE.Mesh(new THREE.PlaneGeometry(60, 80, 2, 2), mat); p.position.set(s.C.x, s.C.y, s.z - 6); p.renderOrder = 0; p.frustumCulled = false; scene.add(p); mat.userData.plane = p; return mat; });
const alignWorlds = () => { for (let k = 1; k < worlds.length; k++) { const a = tickLocal(k - 1, worlds[k - 1].D - TR), b = tickLocal(k, 0), dx = a.x - b.x, dy = a.y - b.y, w = worlds[k];
  w.C.x += dx; w.C.y += dy; w.base.position.x += dx; w.base.position.y += dy; Object.values(w.parts).forEach(p => { p.userData.rest.x += dx; p.userData.rest.y += dy; p.position.copy(p.userData.rest); });
  const pl = fieldMats[k].userData.plane; pl.position.x += dx; pl.position.y += dy; fieldMats[k].uniforms.uA.value.x += dx; fieldMats[k].uniforms.uA.value.y += dy; } };
function tickAt(t) {
  let i = worlds.length - 1; for (let k = 0; k < worlds.length - 1; k++) if (t < worlds[k + 1].A) { i = k; break; }
  const s = worlds[i], tl = t - s.A, last = i === worlds.length - 1, td = s.D - TR;
  if (!last && tl > td) { const a = tickLocal(i, td), b = tickLocal(i + 1, 0), u = ease((tl - td) / TR); return V3(lerp(a.x, b.x, sm(u)), lerp(a.y, b.y, sm(u)), lerp(a.z, b.z, u)); }
  return tickLocal(i, tl);
}
// tunnel of frames + speed streaks
const NF = 90, fp = [], faArr = []; const corners = [[-1, -1], [1, -1], [1, 1], [-1, 1]];
for (let i = 0; i < NF; i++) { const z = 40 - i * 3.1, size = 5.2 + 3.2 * ((i * 0.61803) % 1), red = i % 9 === 4 ? 1 : 0, ang = i * 0.21;
  for (let c = 0; c < 3; c++) { const s = size * (1 - c * 0.035); for (let e = 0; e < 4; e++) { const a = corners[e], b = corners[(e + 1) % 4]; fp.push(a[0] * s, a[1] * s, 0, b[0] * s, b[1] * s, 0); for (let q = 0; q < 2; q++) faArr.push(z, red, ang, 1 - c * 0.3); } } }
const fg = new THREE.BufferGeometry(); fg.setAttribute('position', new THREE.Float32BufferAttribute(fp, 3)); fg.setAttribute('aF', new THREE.Float32BufferAttribute(faArr, 4));
const fmat = new THREE.ShaderMaterial({uniforms: {uCamZ: {value: 0}, uTime: {value: 0}, uAmp: {value: 1}}, transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending,
  vertexShader: `attribute vec4 aF; uniform float uCamZ,uTime; varying float vA; varying float vR; void main(){ float a=aF.z+aF.x*0.045+uTime*0.10; mat2 m=mat2(cos(a),sin(a),-sin(a),cos(a)); vec2 p=m*position.xy; float d=uCamZ-aF.x;
    vA=smoothstep(3.0,12.0,d)*(1.0-smoothstep(18.0,70.0,d))*aF.w; vR=aF.y; gl_Position=projectionMatrix*viewMatrix*vec4(p.x,p.y+${AXY.toFixed(2)},aF.x,1.0); }`,
  fragmentShader: `uniform float uAmp; varying float vA; varying float vR; void main(){ vec3 c=mix(vec3(0.10,0.80,0.68)*0.55,vec3(1.0,0.16,0.12)*0.8,vR); gl_FragColor=vec4(c*vA*uAmp,1.0); }`});
const frames = new THREE.LineSegments(fg, fmat); frames.frustumCulled = false; frames.renderOrder = 1; scene.add(frames);
let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
const NS = 300, sp = [], sa = []; for (let i = 0; i < NS; i++) { const th = rnd() * 6.283, r = 2.0 + rnd() * 13, z = 40 - rnd() * 130; for (let e = 0; e < 2; e++) { sp.push(Math.cos(th) * r, Math.sin(th) * r, z); sa.push(e, rnd()); } }
const sg = new THREE.BufferGeometry(); sg.setAttribute('position', new THREE.Float32BufferAttribute(sp, 3)); sg.setAttribute('aS', new THREE.Float32BufferAttribute(sa, 2));
const smat = new THREE.ShaderMaterial({uniforms: {uCamZ: {value: 0}, uSpeed: {value: 0}}, transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending,
  vertexShader: `attribute vec2 aS; uniform float uCamZ,uSpeed; varying float vA; void main(){ vec3 p=position; p.y+=${AXY.toFixed(2)}; p.z+=aS.x*(0.8+18.0*uSpeed); float d=uCamZ-p.z; vA=smoothstep(1.0,6.0,d)*(1.0-smoothstep(20.0,70.0,d))*(0.04+0.9*uSpeed)*(0.5+0.5*aS.y)*(1.0-0.65*aS.x); gl_Position=projectionMatrix*viewMatrix*vec4(p,1.0); }`,
  fragmentShader: `varying float vA; void main(){ gl_FragColor=vec4(vec3(0.35,0.95,0.85)*vA,1.0); }`});
const streaks = new THREE.LineSegments(sg, smat); streaks.frustumCulled = false; streaks.renderOrder = 2; scene.add(streaks);
const glowTex = (() => { const c = document.createElement('canvas'); c.width = c.height = 128; const x = c.getContext('2d'), g = x.createRadialGradient(64, 64, 0, 64, 64, 64); g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(.22, 'rgba(255,70,50,.8)'); g.addColorStop(1, 'rgba(255,40,30,0)'); x.fillStyle = g; x.fillRect(0, 0, 128, 128); return new THREE.CanvasTexture(c); })();
const tickSp = new THREE.Sprite(new THREE.SpriteMaterial({map: glowTex, blending: THREE.AdditiveBlending, depthTest: false, transparent: true, depthWrite: false})); tickSp.renderOrder = 7; scene.add(tickSp);
const NT = 90, trailPos = new Float32Array(NT * 2 * 3), trailA = new Float32Array(NT * 2); const tg = new THREE.BufferGeometry(); tg.setAttribute('position', new THREE.BufferAttribute(trailPos, 3)); tg.setAttribute('aA', new THREE.BufferAttribute(trailA, 1));
const idx = []; for (let i = 0; i < NT - 1; i++) idx.push(i * 2, i * 2 + 1, i * 2 + 2, i * 2 + 1, i * 2 + 3, i * 2 + 2); tg.setIndex(idx);
const trail = new THREE.Mesh(tg, new THREE.ShaderMaterial({transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, vertexShader: `attribute float aA; varying float vA; void main(){ vA=aA; gl_Position=projectionMatrix*viewMatrix*vec4(position,1.0); }`,
  fragmentShader: `varying float vA; void main(){ gl_FragColor=vec4(mix(vec3(1.0,0.14,0.10),vec3(1.0,0.7,0.6),vA*vA)*vA,1.0); }`})); trail.frustumCulled = false; trail.renderOrder = 6; scene.add(trail);

// ---------- captions (voice-matched) ----------
const CAPS = [[0.15, 2.7, 'WHERE DID THE LAST<br>THREE <em>HOURS</em> GO?'], [2.95, 4.45, 'WHEN YOU’RE<br><em>ABSORBED,</em>'], [4.55, 6.1, 'YOU PAY LESS<br>ATTENTION TO <em>TIME.</em>'], [6.25, 8.2, 'SO IN THE MOMENT,<br>IT <em>FLIES.</em>'],
  [8.35, 11.5, 'BUT LATER, YOUR BRAIN<br>COUNTS THE <em>MEMORIES</em><br>IT STORED.'], [11.7, 13.8, 'MORE NEW MOMENTS,<br>MORE <em>MEMORIES.</em>'], [14.0, 17.1, 'THE SAME HOURS<br>CAN FEEL <em>LONGER</em><br>LOOKING BACK.'], [17.3, 20.1, 'SAME CLOCK.<br>A DIFFERENT<br><em>EXPERIENCE.</em>'], [20.4, 22.0, 'WHERE DID THE LAST<br>THREE <em>HOURS</em> GO?']];
const elCap = document.getElementById('cap'), elBar = document.getElementById('bar');
function distAt(i, tl) { return keys(SPEC[worlds[i].k].dist, tl); }
function targetFor(i, tl, tick) { const sp = SPEC[worlds[i].k], tg2 = tick.clone(); if (sp.focus) tg2.lerp(worlds[i].P(sp.focus.uv[0], sp.focus.uv[1]), keys(sp.focus.w, tl)); return tg2; }
function frameAt(t) {
  let i = worlds.length - 1; for (let k = 0; k < worlds.length - 1; k++) if (t < worlds[k + 1].A) { i = k; break; }
  const s = worlds[i], tl = t - s.A, last = i === worlds.length - 1, td = s.D - TR, tick = tickAt(t); let bump = 0, dist, target;
  if (!last && tl > td) { const u = ease((tl - td) / TR); bump = Math.sin(Math.PI * (tl - td) / TR); dist = lerp(distAt(i, td), distAt(i + 1, 0), u); target = targetFor(i, td, tick).lerp(targetFor(i + 1, 0, tick), u); }
  else { dist = distAt(i, tl); target = targetFor(i, tl, tick); }
  return {i, s, tl, tick, target, dist, bump};
}
alignWorlds();
window.renderAt = t => {
  t = clamp(t, 0, DUR); const f = frameAt(t), {tick, bump} = f;
  const pr = (wi, name, o) => { const p = worlds[wi].parts[name]; if (!p) return; p.position.copy(p.userData.rest).add(o.p || V3(0, 0, 0)); p.rotation.z = o.rz || 0; p.scale.setScalar(o.s || 1); return p; };
  worlds.forEach((w, wi) => {
    const d = f.target.z + f.dist - w.z, lt = t - w.A, op = sm((d - 1.2) / 4) * sm((t - (w.A - 0.55)) / 0.5) * (wi < worlds.length - 1 ? 1 - sm((t - (w.A + w.D - 0.15)) / 0.45) : 1);
    const all = [w.base, ...Object.values(w.parts)]; all.forEach(m => { const u = m.material.uniforms; u.uOp.value = op; u.uTime.value = t; m.visible = op > 0.004; u.uPulse.value.set(0.5, 0.5, -1, 0); u.uRev.value.set(0.5, 0.5, -1); u.uSpark.value = 0; u.uReg.value.set(2, 2, 2, 2); u.uRegG.value.set(1, 1); u.uRed.value = 1; u.uTeal.value = 1.15; });
    w.base.rotation.z = 0; Object.values(w.parts).forEach(p => { p.rotation.z = 0; p.position.copy(p.userData.rest); p.scale.setScalar(1); });
    if (op > 0.004) SPEC[w.k].fx(w, lt, op, {setAll: fn => all.forEach(m => fn(m.material.uniforms)), pr: (name, o) => pr(wi, name, o), pulse: (fq, p = 0) => 0.5 + 0.5 * Math.sin(lt * fq + p)});
  });
  const orb = Math.min(1, f.dist / 14); const ox = 1.6 * Math.sin(t * 0.95) * orb, oy = 0.6 * Math.sin(t * 0.7 + 1) * orb;
  camera.fov = 40 + 10 * bump; camera.updateProjectionMatrix();
  camera.position.set(f.target.x + ox, f.target.y + oy, f.target.z + f.dist);
  camera.up.set(0, 1, 0); camera.lookAt(f.target.x, f.target.y, f.target.z); camera.rotateZ(0.02 * Math.sin(t * 0.8) + (f.i % 2 ? 1 : -1) * 0.35 * bump);
  const cz = camera.position.z; fmat.uniforms.uCamZ.value = cz; fmat.uniforms.uTime.value = t; fmat.uniforms.uAmp.value = 0.12 + 1.1 * bump; smat.uniforms.uCamZ.value = cz; smat.uniforms.uSpeed.value = bump;
  worlds.forEach((w, wi) => { const d = f.target.z + f.dist - w.z; fieldMats[wi].uniforms.uOp.value = sm((d - 1.2) / 4) * sm((t - (w.A - 0.55)) / 0.5) * (wi < worlds.length - 1 ? 1 - sm((t - (w.A + w.D - 0.15)) / 0.45) : 1); fieldMats[wi].uniforms.uTime.value = t; });
  tickSp.position.copy(tick); tickSp.scale.setScalar(0.55 + 0.25 * (0.5 + 0.5 * Math.sin(t * 10)));
  for (let i = 0; i < NT; i++) { const tau = i / (NT - 1) * 1.8, p = tickAt(Math.max(0, t - tau)), q = tickAt(Math.max(0, t - tau - 0.03)), tan = p.clone().sub(q); tan.z *= 0.2; const side = V3(-tan.y, tan.x, 0).normalize(); if (!isFinite(side.x)) side.set(1, 0, 0);
    const dc = p.distanceTo(camera.position), wd = (0.0042 * dc) * (1 - tau / 1.8) + 0.004, a = Math.pow(1 - tau / 1.8, 1.4) * (t - tau > 0 ? 1 : 0) * 0.95 * sm((dc - 5) / 5); trailPos.set([p.x + side.x * wd, p.y + side.y * wd, p.z, p.x - side.x * wd, p.y - side.y * wd, p.z], i * 6); trailA[i * 2] = a; trailA[i * 2 + 1] = a; }
  tg.attributes.position.needsUpdate = true; tg.attributes.aA.needsUpdate = true;
  renderer.render(scene, camera);
  elBar.style.width = (100 * t / DUR).toFixed(2) + '%';
  let cs = ''; CAPS.forEach(([a, b, txt]) => { const k = sm((t - a) / 0.2) * (1 - sm((t - (b - 0.2)) / 0.2)); if (k > 0.01) cs += `<div style="opacity:${k.toFixed(3)};transform:translateY(${((1 - k) * 12).toFixed(1)}px)">${txt}</div>`; });
  elCap.innerHTML = cs;
};
window.ready = true; window.renderAt(0);
