import * as T from 'three';
// Proton laps Earth. One second, slowed 10x: an LHC-speed proton circles the equator 7.48 times,
// leaving a coil. Then a log plunge from Earth scale to metres: light is 2.85 m ahead.
// Two scenes (Earth units: radius 10; finish line: metres) cross-fade during the plunge.
const spec = await fetch('./timeline.json').then(r => r.json());
window.filmSpec = spec;
const F = spec.facts, DUR = spec.duration, S0 = spec.slowStart, SF = spec.slowFactor, LAPS = F.laps_per_s;
const params = new URLSearchParams(location.search), W = +(params.get('w') || 720), H = Math.round(W * 16 / 9);
const film = document.querySelector('#film');
const renderer = new T.WebGLRenderer({ canvas: film, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H, false); renderer.autoClear = true;
const FOV = 50, PX = H / (2 * Math.tan(FOV * Math.PI / 360));
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const smooth = (a, b, x) => { const s = clamp((x - a) / (b - a)); return s * s * (3 - 2 * s); };
const mixv = (a, b, s) => a + (b - a) * s;

// ===================== Earth scene =====================
const RE = 10, KM = RE / 6371; // world units per km
const earth = new T.Scene(); earth.background = new T.Color('#060b13');
const camE = new T.PerspectiveCamera(FOV, 9 / 16, 0.0005, 2000); camE.up.set(0, 0, 1);
const U = { uTime: { value: 0 }, uLaps: { value: 0 }, uHook: { value: 0 }, uPX: { value: PX }, uFade: { value: 1 }, uNear: { value: 1 } };
{
  const globe = new T.Mesh(new T.SphereGeometry(RE, 128, 96), new T.MeshStandardMaterial({ color: '#0c2236', roughness: 0.85, metalness: 0 }));
  earth.add(globe);
  const sun = new T.DirectionalLight('#ffe9cc', 1.7); sun.position.set(-30, -12, 18); earth.add(sun);
  earth.add(new T.HemisphereLight('#3a6274', '#05080d', 0.55));
  // fresnel rim
  const rim = new T.Mesh(new T.SphereGeometry(RE * 1.035, 96, 64), new T.ShaderMaterial({ transparent: true, depthWrite: false, blending: T.AdditiveBlending, side: T.BackSide,
    vertexShader: `varying vec3 vN; varying vec3 vV; void main(){ vec4 mv = modelViewMatrix*vec4(position,1.); vN = normalize(normalMatrix*normal); vV = normalize(-mv.xyz); gl_Position = projectionMatrix*mv; }`,
    fragmentShader: `varying vec3 vN; varying vec3 vV; void main(){ float f = pow(1. - abs(dot(vN, vV)), 3.); gl_FragColor = vec4(vec3(.25,.72,.78)*f*0.9, 1.); }` }));
  rim.material.customProgramCacheKey = () => 'rim'; earth.add(rim);
  // dotted parallels and meridians (dots, never wire lines)
  const pos = [];
  for (let lat = -75; lat <= 75; lat += 15) { if (lat === 0) continue; const n = Math.round(260 * Math.cos(lat * Math.PI / 180));
    for (let k = 0; k < n; k++) { const a = 2 * Math.PI * k / n, c = Math.cos(lat * Math.PI / 180); pos.push(RE * 1.003 * c * Math.cos(a), RE * 1.003 * c * Math.sin(a), RE * 1.003 * Math.sin(lat * Math.PI / 180)); } }
  for (let lon = 0; lon < 360; lon += 20) for (let k = 0; k < 120; k++) { const lat = -84 + 168 * k / 119, c = Math.cos(lat * Math.PI / 180), a = lon * Math.PI / 180;
    pos.push(RE * 1.003 * c * Math.cos(a), RE * 1.003 * c * Math.sin(a), RE * 1.003 * Math.sin(lat * Math.PI / 180)); }
  const g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute(pos, 3));
  const m = new T.ShaderMaterial({ uniforms: U, transparent: true, depthWrite: false, blending: T.AdditiveBlending,
    vertexShader: `uniform float uPX; varying float vL; void main(){ vec4 mv = modelViewMatrix*vec4(position,1.); gl_Position = projectionMatrix*mv; gl_PointSize = max(1.3, 0.07*uPX/-mv.z);
      vec3 n = normalize(position); vL = 0.25 + 0.75*clamp(dot(n, normalize(vec3(-30.,-12.,18.)))*0.8+0.4, 0., 1.); }`,
    fragmentShader: `uniform float uFade; varying float vL; void main(){ vec2 c=gl_PointCoord*2.-1.; if(dot(c,c)>1.) discard; gl_FragColor = vec4(vec3(.45,.66,.72)*0.42*vL*uFade, 1.); }` });
  m.customProgramCacheKey = () => 'grid';
  const dots = new T.Points(g, m); earth.add(dots);
  // gold equator with a tick every 1,000 km (40 ticks), long ticks every 10,000 km
  const tp = [], tb = [];
  for (let k = 0; k < 40; k++) { const big = k % 10 === 0, a = -Math.PI / 2 + 2 * Math.PI * k / 40.075, r0 = RE * 1.006, r1 = RE * (big ? 1.075 : 1.035), w = big ? 0.06 : 0.035;
    const c = Math.cos(a), s = Math.sin(a), tx = -s * w, ty = c * w; const q = [[r0 * c - tx, r0 * s - ty], [r0 * c + tx, r0 * s + ty], [r1 * c + tx, r1 * s + ty], [r1 * c - tx, r1 * s - ty]];
    for (const i of [0, 1, 2, 0, 2, 3]) { tp.push(q[i][0], q[i][1], 0); tb.push(big ? 1 : 0.5); } }
  const tg = new T.BufferGeometry(); tg.setAttribute('position', new T.Float32BufferAttribute(tp, 3)); tg.setAttribute('aB', new T.Float32BufferAttribute(tb, 1));
  const tm = new T.ShaderMaterial({ uniforms: U, transparent: true, depthWrite: false, blending: T.AdditiveBlending,
    vertexShader: `attribute float aB; varying float vB; void main(){ vB=aB; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader: `uniform float uFade; varying float vB; void main(){ gl_FragColor = vec4(vec3(.9,.72,.38)*vB*uFade, 1.); }` });
  tm.customProgramCacheKey = () => 'eqticks'; earth.add(new T.Mesh(tg, tm));
  const eq = new T.Mesh(new T.TorusGeometry(RE * 1.004, 0.035, 8, 400), new T.MeshBasicMaterial({ color: '#c99a4c', transparent: true, opacity: 0.8, blending: T.AdditiveBlending, depthWrite: false }));
  earth.add(eq);
}
// the coil: proton path spirals outward a little each lap so the laps stay countable
const PHI0 = -Math.PI / 2 - 2 * Math.PI * (LAPS % 1); // chosen so the last lap ends at the front (angle -90deg)
const coilR = L => RE * 1.04 + 0.3 * L;
const coilP = L => { const a = PHI0 + 2 * Math.PI * L, r = coilR(L); return new T.Vector3(r * Math.cos(a), r * Math.sin(a), 0); };
const FIN = coilP(LAPS), TAN = new T.Vector3(-Math.sin(PHI0 + 2 * Math.PI * LAPS), Math.cos(PHI0 + 2 * Math.PI * LAPS), 0);
{
  const pts = []; for (let k = 0; k <= 3000; k++) pts.push(coilP(LAPS * k / 3000));
  const g = new T.TubeGeometry(new T.CatmullRomCurve3(pts), 3000, 0.07, 6, false);
  const m = new T.ShaderMaterial({ uniforms: U, transparent: true, depthWrite: false, blending: T.AdditiveBlending,
    vertexShader: `varying float vL; void main(){ vL = uv.x * ${LAPS.toFixed(5)}; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader: `uniform float uLaps; uniform float uFade; uniform float uNear; varying float vL;
      void main(){ float d = uLaps - vL; if (d < 0.) discard; float head = exp(-d*9.); float lap = floor(vL);
        vec3 col = mix(vec3(.25,.75,.78), vec3(1.,.86,.55), head); float a = 0.42 + 0.06*mod(lap,2.) + 2.2*head;
        gl_FragColor = vec4(col*a*uFade*uNear, 1.); }` });
  m.customProgramCacheKey = () => 'coil'; earth.add(new T.Mesh(g, m));
}
// real-speed blur ring for the hook: a comet that lags a quarter lap per frame
{
  const g = new T.TorusGeometry(coilR(0), 0.09, 8, 600);
  const m = new T.ShaderMaterial({ uniforms: U, transparent: true, depthWrite: false, blending: T.AdditiveBlending,
    vertexShader: `varying float vA; void main(){ vA = atan(position.y, position.x); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader: `uniform float uTime; uniform float uHook; uniform float uNear; varying float vA;
      void main(){ float head = fract(${(LAPS).toFixed(4)}*uTime); float a = fract((vA + 1.5707963)/6.2831853);
        float d = fract(head - a); float comet = exp(-d*5.); gl_FragColor = vec4(mix(vec3(.3,.8,.82), vec3(1.,.9,.65), comet*comet)*(0.25+1.6*comet)*uHook*uNear, 1.); }` });
  m.customProgramCacheKey = () => 'hookring'; earth.add(new T.Mesh(g, m));
}
// proton head
const headMat = new T.ShaderMaterial({ uniforms: { ...U, uSize: { value: 0.9 }, uA: { value: 1 } }, transparent: true, depthWrite: false, blending: T.AdditiveBlending,
  vertexShader: `uniform float uPX; uniform float uSize; void main(){ vec4 mv = modelViewMatrix*vec4(position,1.); gl_Position = projectionMatrix*mv; gl_PointSize = clamp(uSize*uPX/-mv.z, 7., 120.); }`,
  fragmentShader: `uniform float uA; void main(){ vec2 c=gl_PointCoord*2.-1.; float r=length(c); if(r>1.)discard; float core=smoothstep(.25,.1,r); float halo=exp(-r*r*6.);
    gl_FragColor = vec4((vec3(1.,.82,.5)*halo + vec3(1.)*core)*uA, 1.); }` });
headMat.customProgramCacheKey = () => 'head';
const headGeo = new T.BufferGeometry(); headGeo.setAttribute('position', new T.Float32BufferAttribute([0, 0, 0], 3));
const head = new T.Points(headGeo, headMat); head.frustumCulled = false; earth.add(head);
// space dust for parallax
function dust(sceneRef, n, spread, z0, z1, key, size = 0.16) {
  let s = 11; const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647; const pos = [];
  for (let i = 0; i < n; i++) pos.push((rnd() - .5) * spread, (rnd() - .5) * spread, z0 + rnd() * (z1 - z0));
  const g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute(pos, 3));
  const m = new T.ShaderMaterial({ uniforms: { ...U, uS: { value: size } }, transparent: true, depthWrite: false, blending: T.AdditiveBlending,
    vertexShader: `uniform float uPX; uniform float uS; void main(){ vec4 mv = modelViewMatrix*vec4(position,1.); gl_Position = projectionMatrix*mv; gl_PointSize = clamp(uS*uPX/-mv.z, 1.2, 6.); }`,
    fragmentShader: `void main(){ vec2 c=gl_PointCoord*2.-1.; float r=dot(c,c); if(r>1.)discard; gl_FragColor=vec4(vec3(.6,.7,.8)*.28*(1.-r),1.); }` });
  m.customProgramCacheKey = () => key; const p = new T.Points(g, m); p.frustumCulled = false; sceneRef.add(p);
}
dust(earth, 2500, 160, -60, 60, 'dustE');

// ===================== finish-line scene (metres) =====================
// x: direction of travel, lanes at y=0 (proton) and y=1.1 (light); z up. Camera sits at y<0.
const fin = new T.Scene(); fin.background = new T.Color('#060b13');
const camF = new T.PerspectiveCamera(FOV, 9 / 16, 0.05, 4e6); camF.up.set(0, 0, 1);
const GAP = F.gap_m, LANE = 1.1;
{
  // scale-free ground dots: layers at 1 m .. 100 km spacing, each fades by camera distance
  const layers = [1, 10, 100, 1000, 10000, 100000];
  layers.forEach((sp, li) => {
    const pos = []; const n = 40; for (let i = -n; i <= n; i++) for (let j = -n; j <= n; j++) pos.push(i * sp + GAP / 2, j * sp + LANE / 2, -0.02);
    const g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute(pos, 3));
    const m = new T.ShaderMaterial({ uniforms: { ...U, uSp: { value: sp }, uD: { value: 10 } }, transparent: true, depthWrite: false, blending: T.AdditiveBlending,
      vertexShader: `uniform float uSp; uniform float uD; varying float vA; void main(){ vec4 mv = modelViewMatrix*vec4(position,1.); gl_Position = projectionMatrix*mv; gl_PointSize = 2.2;
        float k = log(uD/uSp)/2.302585; vA = smoothstep(-0.2, 0.4, k) * (1. - smoothstep(1.6, 2.2, k)); }`,
      fragmentShader: `uniform float uFade; varying float vA; void main(){ vec2 c=gl_PointCoord*2.-1.; if(dot(c,c)>1.)discard; gl_FragColor = vec4(vec3(.42,.6,.66)*.85*vA*uFade,1.); }` });
    m.customProgramCacheKey = () => 'gd' + li; const p = new T.Points(g, m); p.frustumCulled = false; p.userData.mat = m; fin.add(p);
  });
  // lanes: gold metre ticks across both lanes, from -40 m to +12 m
  const tp = [];
  for (let x = -40; x <= 12; x++) { const w = x % 5 === 0 ? 0.05 : 0.025; tp.push(x - w, -0.45, 0, x + w, -0.45, 0, x + w, LANE + 0.45, 0, x - w, -0.45, 0, x + w, LANE + 0.45, 0, x - w, LANE + 0.45, 0); }
  const tg = new T.BufferGeometry(); tg.setAttribute('position', new T.Float32BufferAttribute(tp, 3));
  fin.add(new T.Mesh(tg, new T.MeshBasicMaterial({ color: '#8a6a34', transparent: true, opacity: 0.55, depthWrite: false, blending: T.AdditiveBlending })));
  // trails (long tapered streaks) and heads
  const streak = (y, len, col, key, wid) => { const g = new T.PlaneGeometry(len, wid, 64, 1); g.translate(-len / 2, y, 0.25);
    const m = new T.ShaderMaterial({ uniforms: U, transparent: true, depthWrite: false, blending: T.AdditiveBlending,
      vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
      fragmentShader: `uniform float uFade; varying vec2 vUv; void main(){ float a = pow(vUv.x, 2.2) * (1. - pow(abs(vUv.y*2.-1.), 2.)); gl_FragColor = vec4(vec3(${col})*a*1.2*uFade, 1.); }` });
    m.customProgramCacheKey = () => key; const s = new T.Mesh(g, m); s.rotation.x = 0; fin.add(s); return s; };
  const ls = streak(LANE, 60, '1.,.97,.9', 'sl', 0.22); ls.position.x = GAP;
  streak(0, 60, '1.,.78,.42', 'sp', 0.18);
  const hp = new T.BufferGeometry(); hp.setAttribute('position', new T.Float32BufferAttribute([0, 0, 0.25], 3));
  const pm = headMat.clone(); pm.uniforms = { ...U, uSize: { value: 0.6 }, uA: { value: 1 } }; pm.customProgramCacheKey = () => 'phead';
  const p1 = new T.Points(hp, pm); p1.frustumCulled = false; fin.add(p1);
  const lm = new T.ShaderMaterial({ uniforms: { ...U, uSize: { value: 0.8 } }, transparent: true, depthWrite: false, blending: T.AdditiveBlending, vertexShader: headMat.vertexShader,
    fragmentShader: `void main(){ vec2 c=gl_PointCoord*2.-1.; float r=length(c); if(r>1.)discard; float core=smoothstep(.3,.1,r); float halo=exp(-r*r*4.); gl_FragColor = vec4(vec3(.85,.93,1.)*halo*1.2 + vec3(1.)*core, 1.); }` });
  lm.customProgramCacheKey = () => 'lhead';
  const lg = new T.BufferGeometry(); lg.setAttribute('position', new T.Float32BufferAttribute([GAP, LANE, 0.25], 3));
  const l1 = new T.Points(lg, lm); l1.frustumCulled = false; fin.add(l1);
  // long 1px beam lines so the finish point can be followed down from 1,000 km
  { const g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute([-4e5, 0, 0.25, 0, 0, 0.25, -4e5, LANE, 0.25, GAP, LANE, 0.25], 3));
    g.setAttribute('color', new T.Float32BufferAttribute([0.3, 0.22, 0.1, 1, 0.8, 0.45, 0.3, 0.32, 0.36, 1, 1, 1], 3));
    fin.add(new T.LineSegments(g, new T.LineBasicMaterial({ vertexColors: true, transparent: true, blending: T.AdditiveBlending, depthWrite: false }))); }
  // a person for scale (1.75 m), standing beyond the lanes midway along the gap
  const body = new T.MeshStandardMaterial({ color: '#cdbf9f', roughness: 0.8 });
  const man = new T.Group(); man.position.set(GAP / 2, LANE + 1.3, 0); fin.add(man);
  const cap = (r, len, x, z, rx = 0) => { const o = new T.Mesh(new T.CapsuleGeometry(r, len, 6, 12), body); o.rotation.x = Math.PI / 2; o.position.set(x, 0, z); o.rotation.y = rx; man.add(o); return o; };
  cap(0.075, 0.72, -0.1, 0.44); cap(0.075, 0.72, 0.1, 0.44); cap(0.17, 0.42, 0, 1.12); cap(0.055, 0.55, -0.27, 1.12, 0.08); cap(0.055, 0.55, 0.27, 1.12, -0.08);
  const hd = new T.Mesh(new T.SphereGeometry(0.12, 20, 14), body); hd.position.set(0, 0, 1.62); man.add(hd);
  fin.add(new T.HemisphereLight('#9cbcc8', '#0a0f16', 1.1)); const key = new T.DirectionalLight('#ffe0b0', 1.6); key.position.set(-3, -4, 6); fin.add(key);
  const glow = new T.PointLight('#e8f0ff', 3, 6); glow.position.set(GAP, LANE, 0.6); fin.add(glow);
}
dust(fin, 1500, 30, 0.2, 8, 'dustF', 0.03);

// ===================== cameras =====================
const CK = [[-1.5, 54, 40, 12], [0, 50, 34, -10], [2.4, 56, 50, -4], [5, 56, 58, 0], [8, 57, 60, 4], [12.4, 56, 56, 10], [14.8, 54, 52, 12], [22.5, 50, 34, -10], [24.9, 56, 50, -4]];
function camKeys(t) {
  let k = 1; while (k < CK.length - 2 && t > CK[k + 1][0]) k++;
  const [a, b, c, d] = [CK[k - 1], CK[k], CK[k + 1], CK[k + 2]], u = clamp((t - b[0]) / (c[0] - b[0])), out = [];
  for (let j = 1; j < 4; j++) { const m1 = (c[j] - a[j]) / (c[0] - a[0]) * (c[0] - b[0]), m2 = (d[j] - b[j]) / (d[0] - b[0]) * (c[0] - b[0]), u2 = u * u, u3 = u2 * u;
    out.push((2 * u3 - 3 * u2 + 1) * b[j] + (u3 - 2 * u2 + u) * m1 + (-2 * u3 + 3 * u2) * c[j] + (u3 - u2) * m2); }
  return out;
}
const orbitPos = (t) => { const [D, el, az] = camKeys(t), e = el * Math.PI / 180, z = az * Math.PI / 180, r = D * Math.cos(e); return new T.Vector3(r * Math.sin(z), -r * Math.cos(z), D * Math.sin(e)); };
// finish-line camera in metres, relative to the gap centre; same direction expressed in Earth axes
const LOCAL_DIR = new T.Vector3(-0.35, -1, 0.42).normalize();          // local (x travel, y lanes, z up)
const OUT = FIN.clone().setZ(0).normalize();                             // radial outward at the finish (= local -y)
const toEarth = v => TAN.clone().multiplyScalar(v.x).addScaledVector(OUT, -v.y).add(new T.Vector3(0, 0, v.z));
const LOCAL_TOP = new T.Vector3(0, -0.35, 1).normalize(), DIR_E = toEarth(LOCAL_TOP).normalize();
const M_PER_UNIT = 1 / KM * 1000, NEAR_M = 7.2;
const P0 = orbitPos(14.8), D0 = P0.distanceTo(FIN), DIR0 = P0.clone().sub(FIN).normalize();
// plunge (14.8-16.6) and its mirror pull-back (21.0-22.5): returns distance (Earth units) and blend of directions
function plunge(t) {
  let s = -1, back = false;
  if (t >= 14.8 && t < 16.6) s = smooth(14.8, 16.6, t);
  else if (t >= 16.6 && t < 21.0) s = 1;
  else if (t >= 21.0) { s = 1 - smooth(21.0, 22.5, t); back = true; }
  if (s < 0) return null;
  const dEnd = NEAR_M / M_PER_UNIT, logd = mixv(Math.log(D0), Math.log(dEnd), Math.pow(s, 0.85));
  return { s, d: Math.exp(logd), back };
}
const lookF = new T.Vector3(GAP / 2, LANE / 2, 0.6);
function placeCameras(t) {
  const pl = plunge(t);
  let dist = null;
  if (!pl) { U.uNear.value = 1; camE.position.copy(orbitPos(t)); camE.lookAt(0, 0, 0); return { earthA: 1, finA: 0 }; }
  // pull-back returns toward the loop pose rather than the 14.8 pose
  const Pstart = pl.back ? orbitPos(22.5) : P0, dir0 = Pstart.clone().sub(FIN).normalize(), d0 = Pstart.distanceTo(FIN);
  const ds = clamp(Math.log(d0 / pl.d) / Math.log(d0 / (NEAR_M / M_PER_UNIT)));
  const dir = dir0.clone().lerp(DIR_E, smooth(0, 0.7, ds)).normalize();
  dist = Math.exp(mixv(Math.log(d0), Math.log(NEAR_M / M_PER_UNIT), ds));
  const look = new T.Vector3(0, 0, 0).lerp(FIN, smooth(0, 0.35, ds));
  camE.position.copy(FIN).addScaledVector(dir, dist); camE.lookAt(look);
  const dm = dist * M_PER_UNIT; // same view in metres
  const lookLocal = lookF.clone(); const ldir = LOCAL_TOP.clone().lerp(LOCAL_DIR, smooth(Math.log(2e5), Math.log(25), Math.log(dm))).normalize();
  camF.position.copy(lookLocal).addScaledVector(ldir, dm); camF.lookAt(lookLocal.clone().lerp(new T.Vector3(GAP / 2, LANE / 2, 0), 0));
  if (t > 16.6 && t < 21.0) { const u = (t - 16.6) / 4.4; camF.position.x += 0.9 * u - 0.4; camF.lookAt(lookF.x + 0.2 * u, lookF.y, lookF.z); }
  fin.children.forEach(c => { if (c.userData.mat) c.userData.mat.uniforms.uD.value = dm; });
  U.uNear.value = smooth(3, 10, dist);
  const finA = smooth(4, 1.2, dist);
  return { earthA: 1 - smooth(2.2, 0.7, dist), finA };
}

// ===================== state, overlay =====================
const sim = t => clamp((t - S0) / SF, 0, 1);
function state(t) { const s = t < 21.0 ? sim(t) : 1; return { time: s, laps: s * LAPS, km: s * F.c_km_s }; }
window.stateAt = state;
const out = document.querySelector('#out'), ctx = out.getContext('2d');
const FONT = 'Menlo, "Liberation Mono", monospace', C_CREAM = '#f4e6c8', C_TEAL = '#57d0cc', C_RED = 'rgb(214,62,48)', C_GOLD = '#e8bd68';
const typed = (s, t0, t1, t) => { if (t < t0) return ''; const n = Math.max(1, Math.ceil(s.length * clamp((t - t0) / (t1 - t0)))); return s.slice(0, n); };
function text(s, x, y, size, color, { align = 'center', alpha = 1, spacing = 0, stroke = true } = {}) {
  if (!s || alpha <= 0) return; ctx.save(); ctx.globalAlpha = alpha; ctx.font = `bold ${size}px ${FONT}`; ctx.textAlign = align; ctx.textBaseline = 'middle'; ctx.letterSpacing = spacing + 'px';
  if (stroke) { ctx.lineWidth = Math.max(4, size * 0.11); ctx.strokeStyle = '#05080e'; ctx.lineJoin = 'round'; ctx.strokeText(s, x, y); }
  ctx.fillStyle = color; ctx.fillText(s, x, y); ctx.restore();
}
function chip(s, x, y, size, alpha = 1) {
  if (!s || alpha <= 0) return; ctx.save(); ctx.globalAlpha = alpha; ctx.font = `bold ${size}px ${FONT}`; const w = ctx.measureText(s).width, px = size * 0.45, h = size * 1.42;
  ctx.fillStyle = C_RED; ctx.beginPath(); ctx.roundRect(x - w / 2 - px, y - h / 2, w + 2 * px, h, size * 0.22); ctx.fill();
  ctx.fillStyle = '#fff3e0'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(s, x, y + size * 0.04); ctx.restore();
}
const proj = (v, cam) => { const q = v.clone().project(cam); return [(q.x + 1) / 2 * 1080, (1 - q.y) / 2 * 1920]; };
const grain = [...Array(6)].map((_, k) => { const c = document.createElement('canvas'); c.width = 270; c.height = 480; const x = c.getContext('2d'); const im = x.createImageData(270, 480); let s = 99 + k * 7;
  for (let i = 0; i < im.data.length; i += 4) { s = (s * 16807) % 2147483647; const v = s % 255; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; } x.putImageData(im, 0, 0); return c; });

function overlay(t, st, finA) {
  text('THOUGHT EXPERIMENT · NOT TO SCALE', 540, 168, 23, C_CREAM, { alpha: 0.62 * (1 - smooth(21.0, 21.4, t)) + 0.62 * smooth(22.1, 22.5, t) * 0, spacing: 2, stroke: false });
  const hk = 1 - smooth(2.3, 2.6, t);
  if (hk > 0) {
    text(typed('THIS PROTON', 0, 0.45, t), 540, 300, 96, C_CREAM, { alpha: hk });
    text(typed('CIRCLES EARTH 7.5×', 0.5, 1.15, t), 540, 404, 56, C_CREAM, { alpha: hk });
    text(typed('IN ONE SECOND.', 1.15, 1.7, t), 540, 474, 56, C_GOLD, { alpha: hk });
  }
  const sA = smooth(2.4, 2.7, t) * (1 - smooth(12.2, 12.5, t));
  text('1 SECOND, SLOWED DOWN 10×', 540, 262, 34, C_CREAM, { alpha: sA, spacing: 2 });
  text('99.999999% OF LIGHT SPEED', 540, 316, 26, C_TEAL, { alpha: sA * 0.9 * smooth(3.0, 3.4, t), spacing: 2, stroke: false });
  // counters
  const cA = smooth(2.4, 2.7, t) * (1 - smooth(14.4, 14.9, t));
  const by = 1452;
  [['TIME', st.time.toFixed(3) + ' s', 200, C_CREAM], ['LAPS', st.laps.toFixed(2), 540, C_GOLD], ['KM', Math.floor(st.km).toLocaleString('en-US'), 880, C_TEAL]].forEach(([l, v, x, c]) => {
    text(l, x, by, 27, c, { alpha: 0.8 * cA, spacing: 4, stroke: false }); text(v, x, by + 62, 60, c, { alpha: cA }); });
  // 7.5 laps
  const lA = smooth(12.45, 12.6, t) * (1 - smooth(14.25, 14.45, t));
  if (lA > 0) {
    text(typed('7.5 LAPS IN 1 SECOND.', 12.45, 13.0, t), 540, 270, 56, C_CREAM, { alpha: lA });
    chip(t > 13.1 ? 'REAL PROTONS · CERN LHC' : '', 540, 352, 38, lA * smooth(13.1, 13.2, t));
    text(typed("ITS 27 KM RING: 11,245 LAPS A SECOND", 13.3, 13.9, t), 540, 428, 26, C_CREAM, { alpha: lA * 0.9, stroke: false });
  }
  // the twist
  const wA = smooth(14.45, 14.6, t) * (1 - smooth(16.4, 16.7, t));
  text(typed('AND LIGHT STILL WINS.', 14.45, 15.0, t), 540, 300, 62, C_GOLD, { alpha: wA });
  // finish line
  const fA = smooth(16.7, 16.9, t) * (1 - smooth(19.45, 19.65, t));
  if (fA > 0) {
    text(typed('BY 2.85 METRES.', 16.8, 17.3, t), 540, 290, 78, C_GOLD, { alpha: fA });
    text(typed('AFTER 299,792 KM.', 17.5, 18.0, t), 540, 378, 44, C_CREAM, { alpha: fA });
  }
  const tagA = finA * (1 - smooth(20.9, 21.3, t)) * smooth(16.3, 16.7, t);
  if (tagA > 0) {
    const [lx, ly] = proj(new T.Vector3(GAP, LANE, 0.25), camF), [px, py] = proj(new T.Vector3(0, 0, 0.25), camF);
    text('LIGHT', lx, ly - 70, 34, '#eef4ff', { alpha: tagA }); text('PROTON', px, py - 70, 34, C_GOLD, { alpha: tagA });
    const [ax, ay] = proj(new T.Vector3(0, -0.55, 0.02), camF), [bx, bby] = proj(new T.Vector3(GAP, -0.55, 0.02), camF);
    ctx.save(); ctx.globalAlpha = tagA; ctx.strokeStyle = C_RED; ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(ax, ay - 16); ctx.lineTo(ax, ay); ctx.lineTo(bx, bby); ctx.lineTo(bx, bby - 16); ctx.stroke(); ctx.restore();
    chip('2.85 M', (ax + bx) / 2, (ay + bby) / 2 + 48, 34, tagA);
  }
  const nA = smooth(19.65, 19.8, t) * (1 - smooth(20.9, 21.2, t));
  text(typed('NOTHING WITH MASS', 19.65, 20.1, t), 540, 290, 66, C_CREAM, { alpha: nA });
  text(typed('CATCHES LIGHT.', 20.15, 20.55, t), 540, 372, 66, C_GOLD, { alpha: nA });
  const fl = t >= 16.6 ? 0.12 * Math.exp(-(t - 16.6) * 12) : 0;
  if (fl > 0.005) { ctx.save(); ctx.fillStyle = `rgba(255,240,220,${fl})`; ctx.fillRect(0, 0, 1080, 1920); ctx.restore(); }
}

function drawFilm(alpha) { if (alpha <= 0.001) return; ctx.save(); ctx.globalAlpha = alpha; ctx.drawImage(film, 0, 0, 1080, 1920);
  ctx.globalCompositeOperation = 'lighter'; ctx.filter = 'blur(14px)'; ctx.globalAlpha = 0.5 * alpha; ctx.drawImage(film, 0, 0, 1080, 1920);
  ctx.filter = 'blur(40px)'; ctx.globalAlpha = 0.3 * alpha; ctx.drawImage(film, 0, 0, 1080, 1920); ctx.restore(); }

window.renderAt = function (t, frame = Math.round(t * 30)) {
  t = ((t % DUR) + DUR) % DUR;
  const st = state(t);
  U.uTime.value = t;
  U.uLaps.value = t < S0 ? 0 : t < 21.0 ? st.laps : LAPS * (1 - smooth(21.6, 22.2, t));
  U.uHook.value = (1 - smooth(2.2, 2.45, t)) + smooth(21.9, 22.5, t);
  const showHead = t >= 2.3 && t < 21.7;
  const { earthA, finA } = placeCameras(t);
  const hp = coilP(U.uLaps.value > 0 ? U.uLaps.value : 0); head.position.copy(hp); head.visible = showHead;
  headMat.uniforms.uA.value = showHead ? U.uNear.value : 0;
  ctx.fillStyle = '#060b13'; ctx.fillRect(0, 0, 1080, 1920);
  if (earthA > 0.001) { renderer.render(earth, camE); drawFilm(earthA); }
  if (finA > 0.001) { renderer.render(fin, camF); drawFilm(finA); }
  ctx.save(); const v = ctx.createRadialGradient(540, 960, 380, 540, 960, 1150); v.addColorStop(0, 'rgba(4,8,14,0)'); v.addColorStop(1, 'rgba(4,8,14,0.72)'); ctx.fillStyle = v; ctx.fillRect(0, 0, 1080, 1920);
  ctx.globalAlpha = 0.045; ctx.globalCompositeOperation = 'overlay'; ctx.drawImage(grain[frame % 6], 0, 0, 1080, 1920); ctx.restore();
  overlay(t, st, finA);
  return st;
};
window.captureFrame = (t, frame) => { window.renderAt(t, frame); return out.toDataURL('image/jpeg', 0.95).split(',')[1]; };
window.renderAt(0.01);
window.ready = true;
