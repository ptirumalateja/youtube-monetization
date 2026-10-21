import * as T from 'three';
// Proton laps Earth for one full minute. A real Earth (NASA Blue Marble day, Black Marble night lights),
// an LHC-speed proton at 7.48 laps a second. 60 s of laps play in 20 s (playback ramps x1 -> x5):
// every lap leaves a ring, so 448 laps build a Saturn-like disc. Then a pull-back to the Moon: 46 trips.
const spec = await fetch('./timeline.json').then(r => r.json());
window.filmSpec = spec;
const F = spec.facts, DUR = spec.duration, M0 = spec.minuteStart, ML = spec.minuteLen, B = spec.rampB, LAPS = F.laps_per_s;
const params = new URLSearchParams(location.search), W = +(params.get('w') || 1080), H = Math.round(W * 16 / 9);
const film = document.querySelector('#film');
const renderer = new T.WebGLRenderer({ canvas: film, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H, false);
const FOV = 50, PX = H / (2 * Math.tan(FOV * Math.PI / 360));
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const smooth = (a, b, x) => { const s = clamp((x - a) / (b - a)); return s * s * (3 - 2 * s); };
const mixv = (a, b, s) => a + (b - a) * s;

// ===================== time map =====================
// clip time u in [0, ML] -> real seconds s = u + B u^2 (x1 at the start, x5 at the end, 60 s at u = 20)
const realS = t => { if (t < M0) return 0; const u = Math.min(t - M0, ML); return u + B * u * u; };
const rate = t => (t < M0 || t > M0 + ML) ? 1 : 1 + 2 * B * (t - M0);
const clipAt = s => (-1 + Math.sqrt(1 + 4 * B * s)) / (2 * B) + M0; // inverse of realS
window.clipAt = clipAt;
function state(t) { const s = t < M0 + ML ? realS(t) : F.minute_s; return { time: s, laps: s * LAPS, km: s * F.c_km_s }; }
window.stateAt = state;

// ===================== scene =====================
const RE = 10, KM = RE / 6371;
const scene = new T.Scene(); scene.background = new T.Color('#03060b');
const cam = new T.PerspectiveCamera(FOV, 9 / 16, 0.05, 8000); cam.up.set(0, 0, 1);
const SUN = new T.Vector3(-1, -0.14, 0.28).normalize();
const U = { uTime: { value: 0 }, uLaps: { value: 0 }, uHook: { value: 0 }, uPX: { value: PX }, uTrail: { value: 0.3 }, uRecent: { value: 3 }, uSun: { value: SUN }, uGlow: { value: 0 } };
const loader = new T.TextureLoader();
const tex = (f) => new Promise(r => loader.load('./tex/' + f, t => { t.colorSpace = T.NoColorSpace; t.anisotropy = renderer.capabilities.getMaxAnisotropy(); t.wrapS = T.RepeatWrapping; r(t); }));
const [tDay, tNight, tWater, tClouds] = await Promise.all(['earth-blue-marble.jpg', 'earth-night.jpg', 'earth-water.png', 'clouds.png'].map(tex));

// ---- Earth ----
const earthGeo = new T.SphereGeometry(RE, 256, 160); earthGeo.rotateX(Math.PI / 2); // north pole on +z
const earthMat = new T.ShaderMaterial({
  uniforms: { ...U, uDay: { value: tDay }, uNight: { value: tNight }, uWater: { value: tWater }, uClouds: { value: tClouds }, uSpin: { value: 0 }, uCloudSpin: { value: 0 } },
  vertexShader: `varying vec2 vUv; varying vec3 vN; varying vec3 vP;
    void main(){ vUv = uv; vN = normalize(mat3(modelMatrix)*normal); vec4 w = modelMatrix*vec4(position,1.); vP = w.xyz; gl_Position = projectionMatrix*viewMatrix*w; }`,
  fragmentShader: `uniform sampler2D uDay; uniform sampler2D uNight; uniform sampler2D uWater; uniform sampler2D uClouds; uniform vec3 uSun; uniform float uCloudSpin; uniform float uGlow;
    varying vec2 vUv; varying vec3 vN; varying vec3 vP;
    void main(){
      if (uGlow > .5) { gl_FragColor = vec4(0.,0.,0.,1.); return; }
      vec3 N = normalize(vN), V = normalize(cameraPosition - vP), L = uSun;
      float ndl = dot(N, L);
      vec3 day = pow(texture2D(uDay, vUv).rgb, vec3(2.2));
      vec3 night = pow(texture2D(uNight, vUv).rgb, vec3(2.2));
      float water = texture2D(uWater, vUv).r;
      float cl = texture2D(uClouds, vUv + vec2(uCloudSpin, 0.)).r;
      float clSh = texture2D(uClouds, vUv + vec2(uCloudSpin + 0.002, -0.001)).r;
      float dif = clamp(ndl * 1.05 + 0.04, 0., 1.);
      float dayAmt = smoothstep(-0.12, 0.18, ndl);
      vec3 H = normalize(L + V);
      float spec = 0.0 * pow(max(dot(N, H), 0.), 400.) * water * 0.55 * (1. - cl) * step(0., ndl);
      vec3 col = day * dif * 1.5 * (1. - 0.45 * clSh);
      col += vec3(1., .93, .8) * spec;
      col = mix(col, vec3(.96, .97, 1.) * (dif * 1.15 + 0.01), cl * 0.85);
      col += night * vec3(1., .78, .5) * 2.4 * (1. - dayAmt) * (1. - 0.75 * cl);
      float fres = pow(1. - max(dot(N, V), 0.), 4.);
      col += vec3(.28, .52, 1.) * fres * (0.01 + 0.25 * smoothstep(-0.25, 0.5, ndl));
      col = col / (1. + col * 0.35);
      gl_FragColor = vec4(pow(col, vec3(1. / 2.2)), 1.);
    }` });
const globe = new T.Mesh(earthGeo, earthMat); scene.add(globe);
// atmosphere shell (outer limb glow, brighter on the day side)
const atmo = new T.Mesh(new T.SphereGeometry(RE * 1.035, 128, 80), new T.ShaderMaterial({ uniforms: U, transparent: true, depthWrite: false, blending: T.AdditiveBlending, side: T.BackSide,
  vertexShader: `varying vec3 vN; varying vec3 vP; void main(){ vN = normalize(mat3(modelMatrix)*normal); vec4 w = modelMatrix*vec4(position,1.); vP = w.xyz; gl_Position = projectionMatrix*viewMatrix*w; }`,
  fragmentShader: `uniform vec3 uSun; uniform float uGlow; varying vec3 vN; varying vec3 vP; void main(){ vec3 V = normalize(cameraPosition - vP);
    float f = pow(clamp(1. - abs(dot(normalize(vN), V)), 0., 1.), 5.); float sunSide = smoothstep(-0.35, 0.6, dot(normalize(vN), uSun));
    gl_FragColor = vec4(vec3(.3,.58,1.) * f * (0.05 + 1.0 * sunSide) * (1. - uGlow * 0.6), 1.); }` }));
scene.add(atmo);

// ---- the lap disc: proton spirals outward DR per lap, each lap stays as a ring ----
const R0 = RE * 1.05, DR = 0.022, PHI0 = -Math.PI / 2;
const spiral = L => { const a = PHI0 + 2 * Math.PI * L, r = R0 + DR * Math.max(L, 0); return new T.Vector3(r * Math.cos(a), r * Math.sin(a), 0); };
{
  const g = new T.RingGeometry(R0 - 0.2, R0 + DR * 450 + 0.4, 720, 1);
  const m = new T.ShaderMaterial({ uniforms: U, transparent: true, depthWrite: false, blending: T.AdditiveBlending, side: T.DoubleSide,
    vertexShader: `varying vec2 vP; void main(){ vP = position.xy; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader: `uniform float uLaps; uniform float uTrail; uniform float uRecent; varying vec2 vP;
      void main(){
        float r = length(vP); float a = fract((atan(vP.y, vP.x) - (${PHI0.toFixed(6)})) / 6.2831853);
        float q = (r - ${R0.toFixed(4)}) / ${DR.toFixed(4)};
        float fw = fwidth(q);
        float k = floor(q - a + 0.5); float Ls = k + a; float d = q - Ls;
        if (Ls < 0. || Ls > uLaps + 0.02 || uLaps <= 0.) discard;
        float w = 0.12, sg = max(w, fw * 0.6);
        float line = exp(-0.5 * d * d / (sg * sg)) * (w / sg);
        line = mix(line, w * 2.5, smoothstep(0.6, 1.4, fw));
        float age = uLaps - Ls;
        float dec = mod(floor(Ls / ${(LAPS * 10).toFixed(4)}), 2.);
        vec3 col = mix(vec3(.25,.78,.85), vec3(.95,.72,.36), dec);
        float recent = exp(-age / uRecent);
        float trail = exp(-age / uTrail);
        vec3 c = col * line * (0.4 + 1.1 * recent) + vec3(1., .9, .7) * trail * (line * 2.2 + 0.25 * exp(-d * d * 8.));
        gl_FragColor = vec4(c, 1.); }` });
  m.extensions = { derivatives: true }; m.customProgramCacheKey = () => 'disc';
  scene.add(new T.Mesh(g, m));
}
// real-speed comet ring for the hook (sits on the first lap radius)
{
  const g = new T.TorusGeometry(R0, 0.06, 8, 720);
  const m = new T.ShaderMaterial({ uniforms: U, transparent: true, depthWrite: false, blending: T.AdditiveBlending,
    vertexShader: `varying float vA; void main(){ vA = atan(position.y, position.x); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader: `uniform float uTime; uniform float uHook; varying float vA;
      void main(){ float head = fract(${LAPS.toFixed(5)} * (uTime - ${M0.toFixed(2)})); float a = fract((vA - (${PHI0.toFixed(6)})) / 6.2831853);
        float d = fract(head - a); float comet = exp(-d * 4.); gl_FragColor = vec4(mix(vec3(.3,.8,.85), vec3(1.,.9,.65), comet*comet) * (0.22 + 1.7 * comet) * uHook, 1.); }` });
  m.customProgramCacheKey = () => 'hookring'; scene.add(new T.Mesh(g, m));
}
// proton head
const headMat = new T.ShaderMaterial({ uniforms: { ...U, uSize: { value: 0.75 }, uA: { value: 1 } }, transparent: true, depthWrite: false, blending: T.AdditiveBlending,
  vertexShader: `uniform float uPX; uniform float uSize; void main(){ vec4 mv = modelViewMatrix*vec4(position,1.); gl_Position = projectionMatrix*mv; gl_PointSize = clamp(uSize*uPX/-mv.z, 10., 90.); }`,
  fragmentShader: `uniform float uA; void main(){ vec2 c=gl_PointCoord*2.-1.; float r=length(c); if(r>1.)discard; float core=smoothstep(.25,.1,r); float halo=exp(-r*r*6.);
    gl_FragColor = vec4((vec3(1.,.82,.5)*halo + vec3(1.)*core)*uA, 1.); }` });
headMat.customProgramCacheKey = () => 'head';
const headGeo = new T.BufferGeometry(); headGeo.setAttribute('position', new T.Float32BufferAttribute([0, 0, 0], 3));
const head = new T.Points(headGeo, headMat); head.frustumCulled = false; scene.add(head);

// ---- the Moon, at its real mean distance (384,400 km) ----
const MOON_D = F.moon_km * KM, MOON_R = 1737.4 * KM;
const moonMat = new T.ShaderMaterial({ uniforms: U,
  vertexShader: `varying vec3 vN; varying vec3 vO; void main(){ vO = normal; vN = normalize(mat3(modelMatrix)*normal); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
  fragmentShader: `uniform vec3 uSun; uniform float uGlow; varying vec3 vN; varying vec3 vO;
    float h(vec3 p){ return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453); }
    float n3(vec3 p){ vec3 i = floor(p), f = fract(p); f = f*f*(3.-2.*f);
      return mix(mix(mix(h(i), h(i+vec3(1,0,0)), f.x), mix(h(i+vec3(0,1,0)), h(i+vec3(1,1,0)), f.x), f.y),
                 mix(mix(h(i+vec3(0,0,1)), h(i+vec3(1,0,1)), f.x), mix(h(i+vec3(0,1,1)), h(i+vec3(1,1,1)), f.x), f.y), f.z); }
    void main(){ if (uGlow > .5) { gl_FragColor = vec4(0.,0.,0.,1.); return; }
      float n = 0.5*n3(vO*2.5) + 0.3*n3(vO*6.) + 0.2*n3(vO*14.); float alb = mix(0.42, 0.78, smoothstep(0.42, 0.6, n));
      float d = clamp(dot(normalize(vN), uSun), 0., 1.); gl_FragColor = vec4(vec3(pow(alb * d * 1.1 + 0.015, 1./2.2)), 1.); }` });
const moon = new T.Mesh(new T.SphereGeometry(MOON_R, 64, 40), moonMat); scene.add(moon);
// stars: sparse, dim, far
{
  let s = 5; const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647; const pos = [], br = [];
  for (let i = 0; i < 2600; i++) { const z = rnd() * 2 - 1, a = rnd() * 6.2831853, r = Math.sqrt(1 - z * z); pos.push(5000 * r * Math.cos(a), 5000 * r * Math.sin(a), 5000 * z); br.push(Math.pow(rnd(), 3)); }
  const g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute(pos, 3)); g.setAttribute('aB', new T.Float32BufferAttribute(br, 1));
  const m = new T.ShaderMaterial({ uniforms: U, transparent: true, depthWrite: false, blending: T.AdditiveBlending,
    vertexShader: `attribute float aB; varying float vB; void main(){ vB = aB; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); gl_PointSize = 1.4 + 1.6*aB; }`,
    fragmentShader: `uniform float uGlow; varying float vB; void main(){ vec2 c=gl_PointCoord*2.-1.; float r=dot(c,c); if(r>1.)discard; gl_FragColor=vec4(vec3(.8,.85,1.)*(0.12+0.6*vB)*(1.-r)*(1.-uGlow),1.); }` });
  m.customProgramCacheKey = () => 'stars'; const p = new T.Points(g, m); p.frustumCulled = false; scene.add(p);
}

// ===================== cameras =====================
// orbit keys: [t, distance, elevation deg, azimuth deg]; t=30 repeats t=0 so the loop closes
const CK = [[-3, 44, 18, -14], [0, 44, 18, -10], [3, 46, 20, -6], [8, 52, 23, 0], [13, 62, 25, 6], [18, 76, 27, 11], [23, 93, 28, 15], [25.2, 97, 28, 17], [30, 44, 18, -10], [33, 46, 20, -6]];
function camKeys(t) {
  let k = 1; while (k < CK.length - 2 && t > CK[k + 1][0]) k++;
  const [a, b, c, d] = [CK[k - 1], CK[k], CK[k + 1], CK[k + 2]], u = clamp((t - b[0]) / (c[0] - b[0])), out = [];
  for (let j = 1; j < 4; j++) { const m1 = (c[j] - a[j]) / (c[0] - a[0]) * (c[0] - b[0]), m2 = (d[j] - b[j]) / (d[0] - b[0]) * (c[0] - b[0]), u2 = u * u, u3 = u2 * u;
    out.push((2 * u3 - 3 * u2 + 1) * b[j] + (u3 - 2 * u2 + u) * m1 + (-2 * u3 + 3 * u2) * c[j] + (u3 - u2) * m2); }
  return out;
}
const orbit = t => { const [D, el, az] = camKeys(t), e = el * Math.PI / 180, z = az * Math.PI / 180;
  return { target: new T.Vector3(0, 0, 0.06 * D), dir: new T.Vector3(Math.cos(e) * Math.sin(z), -Math.cos(e) * Math.cos(z), Math.sin(e)), D }; };
// the Moon sits straight behind Earth as seen from the 25.2 s pose, a little to the side so the line reads
const AZM = 17 * Math.PI / 180;
const MHAT = new T.Vector3(-Math.sin(AZM), Math.cos(AZM), 0).applyAxisAngle(new T.Vector3(0, 0, 1), 0.10);
moon.position.copy(MHAT).multiplyScalar(MOON_D);
const MOONVIEW = (t) => { const e = 56 * Math.PI / 180, side = new T.Vector3(0, 0, 1).cross(MHAT).normalize();
  const dir = MHAT.clone().multiplyScalar(-Math.cos(e)).addScaledVector(new T.Vector3(0, 0, 1), Math.sin(e)).addScaledVector(side, 0.06).normalize();
  return { target: MHAT.clone().multiplyScalar(MOON_D * 0.5), dir, D: 1140 * (1 + 0.035 * clamp((t - 26.6) / 2.3)) }; };
const blendPose = (A, Bp, s, sD = s) => ({ target: A.target.clone().lerp(Bp.target, s), dir: A.dir.clone().lerp(Bp.dir, s).normalize(), D: Math.exp(mixv(Math.log(A.D), Math.log(Bp.D), sD)) });
function pose(t) {
  if (t < 25.2) return orbit(t);
  if (t < 26.7) { const A = orbit(25.2), Bp = MOONVIEW(t), sT = smooth(25.7, 26.7, t), sD = smooth(25.2, 26.5, t);
    return { target: A.target.clone().lerp(Bp.target, sT), dir: A.dir.clone().lerp(Bp.dir, smooth(25.2, 26.7, t)).normalize(), D: Math.exp(mixv(Math.log(A.D), Math.log(Bp.D), sD)) }; }
  if (t < 28.9) return MOONVIEW(t);
  const A = MOONVIEW(28.9), Bp = orbit(DUR), u = clamp((t - 28.9) / (DUR - 28.9));
  return { target: A.target.clone().lerp(Bp.target, smooth(0, 0.45, u)), dir: A.dir.clone().lerp(Bp.dir, smooth(0, 1, u)).normalize(), D: Math.exp(mixv(Math.log(A.D), Math.log(Bp.D), smooth(0, 1, u))) };
}
function placeCamera(t) { const p = pose(t); cam.position.copy(p.target).addScaledVector(p.dir, p.D); cam.lookAt(p.target); return p; }

// ===================== overlay =====================
const out = document.querySelector('#out'), ctx = out.getContext('2d');
const FONT = '"JetBrains Mono", Menlo, "Liberation Mono", monospace', C_CREAM = '#f4e6c8', C_TEAL = '#57d0cc', C_RED = 'rgb(214,62,48)', C_GOLD = '#e8bd68';
const typed = (s, t0, t1, t) => { if (t < t0) return ''; const n = Math.max(1, Math.ceil(s.length * clamp((t - t0) / (t1 - t0)))); return s.slice(0, n); };
function text(s, x, y, size, color, { align = 'center', alpha = 1, spacing = 0, stroke = true, weight = 800 } = {}) {
  if (!s || alpha <= 0) return; ctx.save(); ctx.globalAlpha = alpha; ctx.font = `${weight} ${size}px ${FONT}`; ctx.textAlign = align; ctx.textBaseline = 'middle'; ctx.letterSpacing = spacing + 'px';
  if (stroke) { ctx.lineWidth = Math.max(4, size * 0.12); ctx.strokeStyle = '#03060b'; ctx.lineJoin = 'round'; ctx.strokeText(s, x, y); }
  ctx.fillStyle = color; ctx.fillText(s, x, y); ctx.restore();
}
function chip(s, x, y, size, alpha = 1, fill = C_RED) {
  if (!s || alpha <= 0) return; ctx.save(); ctx.globalAlpha = alpha; ctx.font = `800 ${size}px ${FONT}`; const w = ctx.measureText(s).width, px = size * 0.5, h = size * 1.45;
  ctx.fillStyle = fill; ctx.beginPath(); ctx.roundRect(x - w / 2 - px, y - h / 2, w + 2 * px, h, size * 0.22); ctx.fill();
  ctx.fillStyle = '#fff3e0'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(s, x, y + size * 0.04); ctx.restore();
}
const proj = v => { const q = v.clone().project(cam); return [(q.x + 1) / 2 * 1080, (1 - q.y) / 2 * 1920, q.z]; };
const grain = [...Array(6)].map((_, k) => { const c = document.createElement('canvas'); c.width = 270; c.height = 480; const x = c.getContext('2d'); const im = x.createImageData(270, 480); let s = 99 + k * 7;
  for (let i = 0; i < im.data.length; i += 4) { s = (s * 16807) % 2147483647; const v = s % 255; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; } x.putImageData(im, 0, 0); return c; });
const MILESTONES = [10, 20, 30, 40, 50].map(s => ({ s, t: clipAt(s), laps: Math.floor(s * LAPS) }));
window.milestones = MILESTONES;
const fmt = n => Math.floor(n).toLocaleString('en-US');
const tripsAt = t => { const p = clamp((t - 26.55) / 1.45); return Math.min(F.moon_trips, Math.floor(F.moon_trips * Math.pow(p, 1.25) + 1e-9)); };
window.tripsAt = tripsAt;

function overlay(t, st) {
  text('THOUGHT EXPERIMENT', 540, 150, 22, C_CREAM, { alpha: 0.55 * (1 - smooth(29.2, 29.5, t)) + 0.55 * smooth(29.85, 30, t), spacing: 3, stroke: false, weight: 600 });
  // hook
  const hk = 1 - smooth(2.75, 3.0, t);
  if (hk > 0) {
    text(typed('THIS PROTON', 0, 0.4, t), 540, 290, 96, C_CREAM, { alpha: hk });
    text(typed('LAPS EARTH 7.5×', 0.45, 1.0, t), 540, 395, 66, C_CREAM, { alpha: hk });
    text(typed('EVERY SECOND.', 1.05, 1.5, t), 540, 475, 66, C_GOLD, { alpha: hk });
  }
  const qA = smooth(2.9, 3.05, t) * (1 - smooth(5.6, 5.9, t));
  text(typed('HOW MANY LAPS', 2.95, 3.35, t), 540, 290, 70, C_CREAM, { alpha: qA });
  text(typed('IN ONE MINUTE?', 3.4, 3.8, t), 540, 375, 70, C_GOLD, { alpha: qA });
  // during the minute
  const mA = smooth(5.7, 6.0, t) * (1 - smooth(22.9, 23.1, t));
  text('1 MINUTE IN 20 SECONDS', 540, 250, 38, C_CREAM, { alpha: mA, spacing: 1 });
  text(`PLAYBACK ×${rate(t).toFixed(1)}`, 540, 304, 28, C_TEAL, { alpha: mA * 0.95, spacing: 3, stroke: false, weight: 700 });
  for (const m of MILESTONES) { const a = smooth(m.t, m.t + 0.08, t) * (1 - smooth(m.t + 1.3, m.t + 1.5, t));
    if (a > 0) { const pop = 1 + 0.25 * Math.exp(-(t - m.t) * 14); chip(`${m.s} S · ${m.laps} LAPS`, 540, 392, 40 * pop, a); } }
  // counters
  const cA = smooth(2.95, 3.2, t) * (1 - smooth(25.2, 25.6, t)), by = 1530;
  const done = t >= M0 + ML;
  [['TIME', st.time.toFixed(1) + ' s', 190, C_CREAM], ['LAPS', fmt(st.laps), 540, C_GOLD], ['KM', fmt(st.km), 870, C_TEAL]].forEach(([l, v, x, c], i) => {
    const big = done && i === 1 ? 1 + 0.35 * Math.exp(-(t - M0 - ML) * 10) : 1;
    text(l, x, by, 27, c, { alpha: 0.8 * cA, spacing: 4, stroke: false, weight: 600 }); text(v, x, by + 64, (i === 2 ? 50 : 62) * big, c, { alpha: cA }); });
  // 448 laps
  const rA = smooth(23.0, 23.1, t) * (1 - smooth(25.1, 25.35, t));
  if (rA > 0) {
    text(typed('448 LAPS.', 23.05, 23.4, t), 540, 290, 116, C_GOLD, { alpha: rA });
    text(typed('IN 60 SECONDS.', 23.55, 23.95, t), 540, 404, 54, C_CREAM, { alpha: rA });
    text(typed('17,987,547 KM', 24.1, 24.5, t), 540, 480, 44, C_TEAL, { alpha: rA });
  }
  // the Moon
  const oA = smooth(25.35, 25.5, t) * (1 - smooth(28.0, 28.2, t));
  if (oA > 0) {
    text(typed("THAT'S 46 TRIPS", 25.4, 25.85, t), 540, 250, 76, C_CREAM, { alpha: oA });
    text(typed('TO THE MOON.', 25.9, 26.3, t), 540, 340, 76, C_GOLD, { alpha: oA });
  }
  const tA = smooth(26.35, 26.6, t) * (1 - smooth(29.0, 29.25, t));
  if (tA > 0) {
    const [ex, ey] = proj(new T.Vector3(0, 0, 0)), [mx, my] = proj(moon.position);
    const n = tripsAt(t), len = Math.hypot(mx - ex, my - ey), nx = -(my - ey) / len, ny = (mx - ex) / len;
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let k = 0; k < n; k++) { const off = ((k % 2 ? 1 : -1) * Math.ceil(k / 2) / 23) * 0.2 * len, fresh = Math.exp(-(n - 1 - k) / 2.5);
      const cx = (ex + mx) / 2 + nx * off, cy = (ey + my) / 2 + ny * off;
      ctx.strokeStyle = k % 2 ? `rgba(232,189,104,${(0.22 + 0.7 * fresh) * tA})` : `rgba(87,208,204,${(0.22 + 0.7 * fresh) * tA})`; ctx.lineWidth = 2 + 2.5 * fresh;
      ctx.beginPath(); ctx.moveTo(ex, ey); ctx.quadraticCurveTo(cx, cy, mx, my); ctx.stroke(); }
    ctx.restore();
    text('EARTH', ex, ey + 110, 28, C_CREAM, { alpha: tA * 0.9, spacing: 3, weight: 700 });
    text('MOON', mx, my - 46, 28, C_CREAM, { alpha: tA * 0.9, spacing: 3, weight: 700 });
    text('384,400 KM', 600, 1040, 26, C_CREAM, { align: 'left', alpha: tA * 0.8, spacing: 2, weight: 700 }); text('TO SCALE', 600, 1078, 22, C_CREAM, { align: 'left', alpha: tA * 0.6, spacing: 3, stroke: false, weight: 600 });
    text('TRIPS', 540, 1690, 27, C_TEAL, { alpha: tA * 0.85, spacing: 4, stroke: false, weight: 600 });
    text(String(n), 540, 1762, 78 * (1 + 0.12 * Math.exp(-Math.max(0, t - 28.0) * 8) * (n === 46 ? 1 : 0)), n === 46 ? C_GOLD : C_CREAM, { alpha: tA });
  }
  const eA = smooth(28.05, 28.2, t) * (1 - smooth(29.1, 29.35, t));
  if (eA > 0) {
    text(typed('IN ONE MINUTE.', 28.05, 28.45, t), 540, 290, 80, C_GOLD, { alpha: eA });
    chip(t > 28.5 ? 'REAL PROTONS · CERN LHC' : '', 540, 392, 36, eA * smooth(28.5, 28.6, t));
    text(typed('99.999999% OF LIGHT SPEED', 28.6, 28.9, t), 540, 466, 28, C_CREAM, { alpha: eA * 0.9, stroke: false, weight: 700 });
  }
  const fl = (t >= M0 + ML ? 0.16 * Math.exp(-(t - M0 - ML) * 10) : 0) + (t < 0.4 ? 0.12 * Math.exp(-t * 12) : 0);
  if (fl > 0.005) { ctx.save(); ctx.fillStyle = `rgba(255,240,220,${fl})`; ctx.fillRect(0, 0, 1080, 1920); ctx.restore(); }
}

function drawFilm(alpha, glow) { ctx.save(); ctx.globalAlpha = alpha;
  if (!glow) ctx.drawImage(film, 0, 0, 1080, 1920);
  else { ctx.globalCompositeOperation = 'lighter'; ctx.filter = 'blur(10px)'; ctx.globalAlpha = 0.6; ctx.drawImage(film, 0, 0, 1080, 1920);
    ctx.filter = 'blur(36px)'; ctx.globalAlpha = 0.45; ctx.drawImage(film, 0, 0, 1080, 1920); }
  ctx.restore(); }

window.renderAt = function (t, frame = Math.round(t * 30)) {
  t = ((t % DUR) + DUR) % DUR;
  const st = state(t);
  U.uTime.value = t;
  // laps drawn: live during the minute, held through the Moon, unwound into the loop
  const lapsVis = t < M0 ? 0 : t < 29.3 ? st.laps : F.laps_in_minute * (1 - smooth(29.3, 29.85, t));
  U.uLaps.value = lapsVis;
  const lpf = LAPS * rate(t) / 30; // laps per frame: the trail is the shutter smear
  U.uTrail.value = t < 29.3 ? Math.max(0.12, 1.1 * lpf) : 0.12;
  U.uRecent.value = 2 + 2.5 * rate(t);
  U.uHook.value = (1 - smooth(2.9, 3.15, t)) + smooth(29.75, 30, t);
  const showHead = t < 23.4 || t > 29.75;
  if (t < M0 || t > 29.75) { const a = PHI0 + 2 * Math.PI * LAPS * ((t > 29.75 ? t - DUR : t) - M0); head.position.set(R0 * Math.cos(a), R0 * Math.sin(a), 0); }
  else head.position.copy(spiral(lapsVis));
  headMat.uniforms.uA.value = showHead ? 1 : smooth(23.9, 23.4, t);
  const spin = 0.12 * Math.sin(2 * Math.PI * t / DUR); globe.rotation.z = spin; earthMat.uniforms.uCloudSpin.value = 0.004 * Math.sin(2 * Math.PI * t / DUR);
  placeCamera(t);
  ctx.fillStyle = '#03060b'; ctx.fillRect(0, 0, 1080, 1920);
  U.uGlow.value = 0; renderer.render(scene, cam); drawFilm(1, false);
  U.uGlow.value = 1; renderer.render(scene, cam); drawFilm(1, true); U.uGlow.value = 0;
  ctx.save(); const v = ctx.createRadialGradient(540, 960, 420, 540, 960, 1180); v.addColorStop(0, 'rgba(3,6,11,0)'); v.addColorStop(1, 'rgba(3,6,11,0.7)'); ctx.fillStyle = v; ctx.fillRect(0, 0, 1080, 1920);
  ctx.globalAlpha = 0.04; ctx.globalCompositeOperation = 'overlay'; ctx.drawImage(grain[frame % 6], 0, 0, 1080, 1920); ctx.restore();
  overlay(t, st);
  return st;
};
window.captureFrame = (t, frame) => { window.renderAt(t, frame); return out.toDataURL('image/jpeg', 0.95).split(',')[1]; };
await document.fonts.load('800 40px "JetBrains Mono"').catch(() => {});
window.renderAt(0.01);
window.ready = true;
