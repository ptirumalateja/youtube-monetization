import * as T from 'three';
// The Moon Never Loops (v2, cinematic). Close on a real-looking Earth and Moon, pull back to the loopy
// drawing everyone has seen, unwind it to the real path, then fly beside Earth and the Moon for a year:
// the Moon's trail weaves around Earth's and always curves toward the Sun. Never a loop.
// Units: 1 world unit = 1 million km. Orbits and paths are true; the Sun, Earth and Moon are enlarged.
const spec = await fetch('./timeline.json').then(r => r.json());
window.filmSpec = spec;
const F = spec.facts, DUR = spec.duration, CL = spec.clock;
const Y = F.year_days, MS = F.sidereal_month_days, SYN = F.synodic_month_days;
const R = F.earth_sun_km / 1e6, RM = F.earth_moon_km / 1e6, RMYTH = spec.myth_r_over_R * R;
const D_TOT = CL.months * SYN;                 // whole months, so the Moon's phase matches at the loop point
const WE = 2 * Math.PI / Y, WM = 2 * Math.PI / MS;
const RE_D = 0.05, RMO_D = 0.022, RS_D = 5.0;  // display radii (Earth ~8x, Moon ~13x, Sun ~7x real)
const params = new URLSearchParams(location.search), W = +(params.get('w') || 720), H = Math.round(W * 16 / 9);
const film = document.querySelector('#film');
const renderer = new T.WebGLRenderer({ canvas: film, antialias: true, preserveDrawingBuffer: true, logarithmicDepthBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H, false); renderer.outputColorSpace = T.SRGBColorSpace;
const FOV = 50, PX = H / (2 * Math.tan(FOV * Math.PI / 360));
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const smooth = (a, b, x) => { const s = clamp((x - a) / (b - a)); return s * s * (3 - 2 * s); };
const mixv = (a, b, s) => a + (b - a) * s;

// ---------- the clock: slow in the close-ups, fast while riding; integrates to exactly 12 synodic months ----------
const rideW = t => smooth(CL.ride[0], CL.ride[1], t) * (1 - smooth(CL.ride[2], CL.ride[3], t));
const STEP = 1 / 600, NT = Math.round(DUR / STEP);
let wsum = 0; for (let i = 0; i < NT; i++) wsum += rideW((i + 0.5) * STEP) * STEP;
const RATE_A = (D_TOT - CL.base_days_per_s * DUR) / wsum;
const DAY = new Float64Array(NT + 1); for (let i = 0; i < NT; i++) DAY[i + 1] = DAY[i] + (CL.base_days_per_s + RATE_A * rideW((i + 0.5) * STEP)) * STEP;
const dayAt = t => { const x = clamp(t / STEP, 0, NT), i = Math.min(NT - 1, Math.floor(x)); return mixv(DAY[i], DAY[i + 1], x - i); };

// local frame that turns with Earth: N points away from the Sun, Tg along the motion, Z up
const frameAt = d => { const e = WE * d; return { N: new T.Vector3(Math.cos(e), Math.sin(e), 0), Tg: new T.Vector3(-Math.sin(e), Math.cos(e), 0), Z: new T.Vector3(0, 0, 1) }; };
const local = (d, n, tg, z) => { const f = frameAt(d); return f.N.clone().multiplyScalar(n).addScaledVector(f.Tg, tg).addScaledVector(f.Z, z); };
const earthAt = d => new T.Vector3(R * Math.cos(WE * d), R * Math.sin(WE * d), 0);
// close-up camera direction (day side, a little ahead); the Moon starts behind Earth, off to one side
const C0_DIR = new T.Vector3(-0.5, 0.8, 0.3).normalize();
const PHI = Math.atan2(C0_DIR.y, C0_DIR.x) + (params.has('phi') ? +params.get('phi') : spec.moon_phase_offset);
const moonVec = (d, r) => new T.Vector3(r * Math.cos(WM * d + PHI), r * Math.sin(WM * d + PHI), 0);
const moonAt = (d, r = RM) => earthAt(d).add(moonVec(d, r));

const scene = new T.Scene(); scene.background = new T.Color('#03060c');
const cam = new T.PerspectiveCamera(FOV, 9 / 16, 0.0005, 9000); cam.up.set(0, 0, 1);
const U = { uPX: { value: PX }, uH: { value: H }, uAspect: { value: 9 / 16 }, uTime: { value: 0 } };
// shaders work on the raw texture values (no sRGB decode), since ShaderMaterial output is not re-encoded
const tex = url => new Promise(res => new T.TextureLoader().load(url, t => { t.colorSpace = T.NoColorSpace; t.anisotropy = 8; res(t); }));
const [tDay, tNight, tClouds, tWater, tMoon, tMoonN] = await Promise.all([tex('assets/earth_day.jpg'), tex('assets/earth_night.jpg'), tex('assets/earth_clouds.jpg'),
  tex('assets/earth_water.jpg'), tex('assets/moon_albedo.jpg'), tex('assets/moon_normal.png')]);

let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
function points(pos, col, key, vs, fs, extra = {}) {
  const g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute(pos, 3)); if (col) g.setAttribute('aC', new T.Float32BufferAttribute(col, 1));
  const m = new T.ShaderMaterial({ uniforms: { ...U, ...extra }, transparent: true, depthWrite: false, blending: T.AdditiveBlending, vertexShader: vs, fragmentShader: fs });
  m.customProgramCacheKey = () => key; const p = new T.Points(g, m); p.frustumCulled = false; return { m, p };
}
// ---------- sky: stars plus a soft procedural Milky Way band (follows the camera, infinitely far) ----------
const sky = new T.Group(); scene.add(sky);
{
  const pos = [], col = [];
  for (let i = 0; i < 9000; i++) { const u = rnd() * 2 - 1, a = rnd() * 2 * Math.PI, s = Math.sqrt(1 - u * u); pos.push(4000 * s * Math.cos(a), 4000 * s * Math.sin(a), 4000 * u); col.push(Math.pow(rnd(), 4)); }
  // band: tilted great circle, gaussian thickness, dust lane carved out of the middle
  const tilt = new T.Matrix4().makeRotationX(1.05).multiply(new T.Matrix4().makeRotationZ(0.4));
  for (let i = 0; i < 70000; i++) { const a = rnd() * 2 * Math.PI, g = (rnd() + rnd() + rnd() - 1.5) * 0.16;
    if (Math.abs(g + 0.03 * Math.sin(a * 5)) < 0.018 && rnd() < 0.85) continue;
    const v = new T.Vector3(Math.cos(a) * Math.cos(g), Math.sin(a) * Math.cos(g), Math.sin(g)).applyMatrix4(tilt).multiplyScalar(4000);
    pos.push(v.x, v.y, v.z); col.push(-0.05 - 0.25 * rnd() * (0.6 + 0.4 * Math.cos(a))); }
  const st = points(pos, col, 'sky', `attribute float aC; varying float vC; void main(){ vC = aC; vec4 mv = modelViewMatrix*vec4(position,1.); gl_Position = projectionMatrix*mv;
      gl_PointSize = aC >= 0. ? 1.1 + 2.6*aC : 1.6; }`,
    `varying float vC; void main(){ vec2 c=gl_PointCoord*2.-1.; float r=dot(c,c); if(r>1.)discard;
      vec3 col; float b; if (vC >= 0.) { col = mix(vec3(.65,.75,.92), vec3(1.,.88,.72), step(.7, fract(vC*37.))); b = 0.3+0.9*vC; }
      else { col = mix(vec3(.55,.62,.85), vec3(.95,.82,.65), fract(-vC*13.)); b = -vC*0.55; }
      gl_FragColor = vec4(col*b*(1.-r), 1.); }`);
  sky.add(st.p);
}

// ---------- the Sun: animated granulation, limb darkening, corona and streamers ----------
const NOISE = `vec3 h3(vec3 p){ p = vec3(dot(p,vec3(127.1,311.7,74.7)), dot(p,vec3(269.5,183.3,246.1)), dot(p,vec3(113.5,271.9,124.6))); return -1.+2.*fract(sin(p)*43758.5453); }
  float n3(vec3 p){ vec3 i=floor(p), f=fract(p), u=f*f*(3.-2.*f);
    return mix(mix(mix(dot(h3(i),f), dot(h3(i+vec3(1,0,0)),f-vec3(1,0,0)),u.x), mix(dot(h3(i+vec3(0,1,0)),f-vec3(0,1,0)), dot(h3(i+vec3(1,1,0)),f-vec3(1,1,0)),u.x),u.y),
               mix(mix(dot(h3(i+vec3(0,0,1)),f-vec3(0,0,1)), dot(h3(i+vec3(1,0,1)),f-vec3(1,0,1)),u.x), mix(dot(h3(i+vec3(0,1,1)),f-vec3(0,1,1)), dot(h3(i+vec3(1,1,1)),f-vec3(1,1,1)),u.x),u.y),u.z); }`;
const LOGV = ['#include <common>\n#include <logdepthbuf_pars_vertex>\n', '\n#include <logdepthbuf_vertex>\n'];
const LOGF = ['#include <logdepthbuf_pars_fragment>\n', '\n#include <logdepthbuf_fragment>\n'];
const sun = new T.Mesh(new T.SphereGeometry(RS_D, 96, 64), new T.ShaderMaterial({ uniforms: U,
  vertexShader: `${LOGV[0]} varying vec3 vP; varying vec3 vN; varying vec3 vV; void main(){ vP = position; vec4 mv = modelViewMatrix*vec4(position,1.); vN = normalize(normalMatrix*normal); vV = normalize(-mv.xyz);
    gl_Position = projectionMatrix*mv; ${LOGV[1]} }`,
  fragmentShader: `${LOGF[0]} uniform float uTime; varying vec3 vP; varying vec3 vN; varying vec3 vV; ${NOISE}
    void main(){ ${LOGF[1]} vec3 p = normalize(vP); float g = 0.; float a = 0.5; vec3 q = p*7. + vec3(0., 0., uTime*0.12);
      for (int i=0;i<4;i++){ g += a*abs(n3(q)); q *= 2.3; a *= 0.5; }
      float spots = smoothstep(0.42, 0.55, n3(p*2.2 + 3.1))*smoothstep(0.62, 0.3, abs(p.z));
      float mu = clamp(dot(vN, vV), 0., 1.); float limb = 0.38 + 0.62*pow(mu, 0.55);
      vec3 col = mix(vec3(1.,.55,.16), vec3(1.,.93,.75), clamp(1.15 - 1.6*g, 0., 1.)) * limb * (1. - 0.75*spots);
      gl_FragColor = vec4(col*vec3(.78,.7,.6), 1.); }` }));
sun.material.customProgramCacheKey = () => 'sun'; scene.add(sun);
function sprite(size, key, frag, extra = {}) {
  const m = new T.ShaderMaterial({ uniforms: { ...U, uA: { value: 1 }, ...extra }, transparent: true, depthWrite: false, depthTest: false, blending: T.AdditiveBlending,
    vertexShader: `varying vec2 vUv; void main(){ vUv = uv*2.-1.; gl_Position = projectionMatrix*(modelViewMatrix*vec4(0.,0.,0.,1.) + vec4(position.xy, 0., 0.)); }`, fragmentShader: frag });
  m.customProgramCacheKey = () => key; const s = new T.Mesh(new T.PlaneGeometry(size, size), m); s.frustumCulled = false; s.renderOrder = -1; scene.add(s); return s;
}
const corona = sprite(RS_D * 16, 'corona', `uniform float uA; uniform float uTime; varying vec2 vUv; ${NOISE}
  void main(){ float r = length(vUv)*8.; float ang = atan(vUv.y, vUv.x);
    float glow = 0.9*exp(-(r-1.)*2.6) + 0.35*exp(-(r-1.)*0.7);
    float streak = pow(0.5+0.5*n3(vec3(cos(ang)*3., sin(ang)*3., uTime*0.05)), 3.)*exp(-(r-1.)*0.9)*1.1;
    float a = r < 0.98 ? 0. : (glow + streak)*smoothstep(8., 2., r);
    gl_FragColor = vec4(vec3(1.,.72,.4)*a*uA, 1.); }`);

// ---------- Earth: Blue Marble day, city lights at night, clouds, ocean glint, atmosphere ----------
const earthGroup = new T.Group(); scene.add(earthGroup);
const earthSpin = new T.Group(); earthSpin.rotation.x = Math.PI / 2; earthGroup.add(earthSpin); // sphere poles (y) -> world z
const EU = { ...U, uDay: { value: tDay }, uNight: { value: tNight }, uClouds: { value: tClouds }, uWater: { value: tWater }, uSunDir: { value: new T.Vector3(1, 0, 0) }, uCloudShift: { value: 0 } };
const earthMesh = new T.Mesh(new T.SphereGeometry(RE_D, 160, 120), new T.ShaderMaterial({ uniforms: EU,
  vertexShader: `${LOGV[0]} varying vec2 vUv; varying vec3 vNw; varying vec3 vPw; void main(){ vUv = uv; vNw = normalize(mat3(modelMatrix)*normal); vec4 w = modelMatrix*vec4(position,1.); vPw = w.xyz;
    gl_Position = projectionMatrix*viewMatrix*w; ${LOGV[1]} }`,
  fragmentShader: `${LOGF[0]} uniform sampler2D uDay; uniform sampler2D uNight; uniform sampler2D uClouds; uniform sampler2D uWater; uniform vec3 uSunDir; uniform float uCloudShift;
    varying vec2 vUv; varying vec3 vNw; varying vec3 vPw;
    void main(){ ${LOGF[1]} vec3 n = normalize(vNw), L = normalize(uSunDir), V = normalize(cameraPosition - vPw); float l = dot(n, L);
      vec3 day = texture2D(uDay, vUv).rgb; float cl = texture2D(uClouds, vUv + vec2(uCloudShift, 0.)).r; float water = texture2D(uWater, vUv).r;
      float lit = smoothstep(-0.08, 0.25, l);
      day = mix(day, vec3(dot(day, vec3(.3,.5,.2))), 0.18); vec3 col = day*(0.05 + 1.3*max(l, 0.));
      col = mix(col, vec3(1.)*(0.04 + 1.15*max(l,0.)), cl*0.85);
      vec3 Hh = normalize(L + V); col += water*(1.-cl)*vec3(1.,.9,.75)*pow(max(dot(n, Hh), 0.), 60.)*0.9*lit;
      vec3 night = texture2D(uNight, vUv).rgb; col += night*night*vec3(1.4,1.05,0.65)*(1.-lit)*(1.-cl*0.8)*1.8;
      float fr = pow(1. - max(dot(n, V), 0.), 2.6); col += vec3(.35,.6,1.)*fr*smoothstep(-0.25, 0.4, l)*0.9;
      col += vec3(.45,.2,.06)*exp(-pow((l-0.02)/0.035, 2.))*0.12*(1.-cl);
      gl_FragColor = vec4(col, 1.); }` }));
earthMesh.material.customProgramCacheKey = () => 'earth'; earthSpin.add(earthMesh);
const atmo = new T.Mesh(new T.SphereGeometry(RE_D * 1.06, 96, 64), new T.ShaderMaterial({ uniforms: EU, transparent: true, depthWrite: false, blending: T.AdditiveBlending, side: T.BackSide,
  vertexShader: `${LOGV[0]} varying vec3 vNw; varying vec3 vPw; void main(){ vNw = normalize(mat3(modelMatrix)*normal); vec4 w = modelMatrix*vec4(position,1.); vPw = w.xyz; gl_Position = projectionMatrix*viewMatrix*w; ${LOGV[1]} }`,
  fragmentShader: `${LOGF[0]} uniform vec3 uSunDir; varying vec3 vNw; varying vec3 vPw; void main(){ ${LOGF[1]} vec3 n = normalize(vNw), V = normalize(cameraPosition - vPw);
    float rim = clamp(1. - abs(dot(n, V)), 0., 1.); float side = smoothstep(-0.35, 0.5, dot(n, normalize(uSunDir)));
    float a = pow(rim, 5.)*1.6; gl_FragColor = vec4(vec3(.32,.58,1.)*a*side, 1.); }` }));
atmo.material.customProgramCacheKey = () => 'atmo'; earthGroup.add(atmo);

// ---------- Moon: procedural albedo and object-space normals, tidally locked ----------
const moonGroup = new T.Group(); scene.add(moonGroup);
const moonSpin = new T.Group(); moonSpin.rotation.x = Math.PI / 2; moonGroup.add(moonSpin);
const moonMesh = new T.Mesh(new T.SphereGeometry(RMO_D, 128, 96), new T.ShaderMaterial({ uniforms: { ...U, uAlb: { value: tMoon }, uNrm: { value: tMoonN }, uSunDir: { value: new T.Vector3(1, 0, 0) } },
  vertexShader: `${LOGV[0]} varying vec2 vUv; varying vec3 vPw; varying vec3 vM0; varying vec3 vM1; varying vec3 vM2; void main(){ vUv = uv; vM0 = modelMatrix[0].xyz; vM1 = modelMatrix[1].xyz; vM2 = modelMatrix[2].xyz;
    vec4 w = modelMatrix*vec4(position,1.); vPw = w.xyz; gl_Position = projectionMatrix*viewMatrix*w; ${LOGV[1]} }`,
  fragmentShader: `${LOGF[0]} varying vec3 vM0; varying vec3 vM1; varying vec3 vM2; uniform sampler2D uAlb; uniform sampler2D uNrm; uniform vec3 uSunDir; varying vec2 vUv; varying vec3 vPw;
    void main(){ ${LOGF[1]} vec3 no = texture2D(uNrm, vUv).xyz*2.-1.;
      // texture space (x lon0, y lon90, z north) -> three sphere local (x, z north -> y, y -> -z)
      vec3 nObj = vec3(no.x, no.z, -no.y); vec3 n = normalize(mat3(vM0, vM1, vM2)*nObj); float l = dot(n, normalize(uSunDir));
      vec3 alb = texture2D(uAlb, vUv).rgb; vec3 col = alb*vec3(1.,.98,.94)*(0.05 + 1.35*max(l, 0.));
      gl_FragColor = vec4(col, 1.); }` }));
moonMesh.material.customProgramCacheKey = () => 'moon'; moonSpin.add(moonMesh);

function marker(rgb, px, key) {
  const g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute([0, 0, 0], 3));
  const m = new T.ShaderMaterial({ uniforms: { uA: { value: 0 } }, transparent: true, depthWrite: false, depthTest: false, blending: T.AdditiveBlending,
    vertexShader: `void main(){ gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); gl_PointSize = ${px.toFixed(1)}; }`,
    fragmentShader: `uniform float uA; void main(){ vec2 c=gl_PointCoord*2.-1.; float r=dot(c,c); if(r>1.)discard; gl_FragColor = vec4(vec3(${rgb})*(exp(-r*7.)*1.4 + 0.25*(1.-r))*uA, 1.); }` });
  m.customProgramCacheKey = () => key; const p = new T.Points(g, m); p.frustumCulled = false; p.renderOrder = 20; scene.add(p); return p;
}
const earthGlow = marker('.45,.75,1.', 26, 'eglow'), moonGlow = marker('1.,.97,.9', 18, 'mglow');

// ---------- paths: screen-space ribbons evaluated in the vertex shader ----------
// kind 0 = Earth (teal), 1 = Moon's real path (gold), 2 = the usual drawing (cream dashes, radius morphs)
function ribbon(kind, d0, d1, nseg, key) {
  const tau = [], side = [], idx = [];
  for (let i = 0; i <= nseg; i++) { const d = d0 + (d1 - d0) * i / nseg; tau.push(d, d); side.push(-1, 1); if (i < nseg) { const a = 2 * i; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); } }
  const g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute(new Array(tau.length * 3).fill(0), 3));
  g.setAttribute('aTau', new T.Float32BufferAttribute(tau, 1)); g.setAttribute('aSide', new T.Float32BufferAttribute(side, 1)); g.setIndex(idx);
  const colExpr = kind === 0 ? 'mix(vec3(.18,.55,.62), vec3(.6,.95,.95), head)' : kind === 1 ? 'mix(vec3(1.,.7,.28), vec3(1.,.96,.82), head)' : 'vec3(1.,.93,.8)';
  const m = new T.ShaderMaterial({ uniforms: { ...U, uR: { value: kind ? RM : 0 }, uNow: { value: 0 }, uWidth: { value: 3 }, uFuture: { value: 0.2 }, uHead: { value: 3 }, uA: { value: 1 } },
    transparent: true, depthWrite: false, depthTest: true, blending: T.AdditiveBlending, side: T.DoubleSide,
    vertexShader: `${LOGV[0]}
      uniform float uR; uniform float uWidth; uniform float uH; uniform float uAspect; attribute float aTau; attribute float aSide; varying float vTau; varying float vSide;
      vec3 P(float d){ float e = ${WE.toFixed(10)}*d, m = ${WM.toFixed(10)}*d + ${PHI.toFixed(6)}; return vec3(${R.toFixed(4)}*cos(e), ${R.toFixed(4)}*sin(e), 0.) + uR*vec3(cos(m), sin(m), 0.); }
      void main(){ vTau = aTau; vSide = aSide; float dt = ${((d1 - d0) / nseg).toFixed(6)};
        vec4 p0 = projectionMatrix*viewMatrix*vec4(P(aTau),1.), p1 = projectionMatrix*viewMatrix*vec4(P(aTau+dt),1.), pm = projectionMatrix*viewMatrix*vec4(P(aTau-dt),1.);
        vec2 s1 = p1.xy/max(p1.w,1e-5), sm = pm.xy/max(pm.w,1e-5);
        vec2 dir = (s1 - sm)*vec2(uAspect,1.); dir = length(dir) > 1e-9 ? normalize(dir) : vec2(1.,0.);
        vec2 n = vec2(-dir.y, dir.x)/vec2(uAspect,1.);
        gl_Position = p0 + vec4(n*aSide*uWidth/uH*p0.w, 0., 0.);
        ${LOGV[1]}
        if (p0.w < 1e-4 || p1.w < 1e-4 || pm.w < 1e-4) gl_Position = vec4(0.,0.,-2.,1.);
      }`,
    fragmentShader: `${LOGF[0]}
      uniform float uNow; uniform float uFuture; uniform float uHead; uniform float uA; varying float vTau; varying float vSide;
      void main(){ ${LOGF[1]}
        float edge = 1. - vSide*vSide; float d = uNow - vTau; float past = step(0., d);
        float head = past*exp(-max(d, 0.)/uHead);
        float b = ${kind === 2 ? 'step(0.42, fract(vTau*0.9))' : 'mix(uFuture, 0.75, past) + 1.7*head'};
        vec3 col = ${colExpr};
        gl_FragColor = vec4(col*b*edge*uA, 1.); }` });
  m.customProgramCacheKey = () => key; const mesh = new T.Mesh(g, m); mesh.frustumCulled = false; mesh.renderOrder = 5 + kind; scene.add(mesh); return m;
}
const earthPath = ribbon(0, -2, D_TOT + 2, 14000, 'pathE'), moonPath = ribbon(1, -2, D_TOT + 2, 26000, 'pathM'), sketch = ribbon(2, 0, Y, 12000, 'sketch');

// ---------- timeline helpers ----------
function sketchR(t) { const l0 = Math.log(RMYTH), l1 = Math.log(RM); return t < 2.9 ? RMYTH : Math.exp(mixv(l0, l1, smooth(2.9, 4.7, t))); }
function state(t) { const d = dayAt(t); return { days: d, months: Math.floor(d / SYN + 1e-6) }; }
window.stateAt = state;

// ---------- cameras ----------
const sph = (focus, dist, el, az) => { const e = el * Math.PI / 180, z = az * Math.PI / 180, r = dist * Math.cos(e);
  return { pos: focus.clone().add(new T.Vector3(r * Math.sin(z), -r * Math.cos(z), dist * Math.sin(e))), look: focus.clone() }; };
const C0 = (d, t) => { const E = earthAt(d), f = frameAt(d), dir = f.N.clone().multiplyScalar(C0_DIR.x).addScaledVector(f.Tg, C0_DIR.y).addScaledVector(f.Z, C0_DIR.z);
  const drift = 0.012 * Math.sin(t * 0.9); return { pos: E.clone().addScaledVector(dir, 0.6 + drift), look: E.clone().add(local(d, 0.03, -0.05, 0.0)) }; };
const WIDE = (t) => sph(new T.Vector3(0, -6, 0), 780, 66, -8 + 4 * Math.sin(t * 0.3));
const HERO = (t) => sph(new T.Vector3(10, 6, 0), 540, 32, 118 + 3 * (t - 15.2));
// riding: A looks sunward past Earth (trails arc toward the Sun), B swings to the day side
// riding: look sunward past Earth and the Moon, so the Sun, both bodies and the trails share the frame
const RA = d => { const E = earthAt(d), M = moonAt(d), mid = E.clone().lerp(M, 0.5), pos = mid.clone().add(local(d, 1.4, 0.36, 0.28));
  const dir = mid.clone().sub(pos).normalize().multiplyScalar(0.56).add(pos.clone().negate().normalize().multiplyScalar(0.44)); return { pos, look: pos.clone().add(dir) }; };
// crane: rise from the ride to the hero view, keeping Earth and then the Sun in frame
function crane(d, t, s) { const a = RA(d), h = HERO(t), E = earthAt(d);
  const look = E.clone().lerp(h.look, smooth(0.4, 1, s));
  const dir = a.pos.clone().sub(a.look).normalize().lerp(h.pos.clone().sub(h.look).normalize(), smooth(0, 0.8, s)).normalize();
  const dist = Math.exp(mixv(Math.log(a.pos.distanceTo(a.look)), Math.log(h.pos.distanceTo(h.look)), Math.pow(s, 0.75)));
  return { pos: look.clone().addScaledVector(dir, dist), look }; }
function blendPose(a, b, s, l0 = 0, l1 = 1) {
  const look = a.look.clone().lerp(b.look, smooth(l0, l1, s));
  const da = a.pos.distanceTo(a.look), db = b.pos.distanceTo(b.look);
  const dir = a.pos.clone().sub(a.look).normalize().lerp(b.pos.clone().sub(b.look).normalize(), smooth(0.05, 0.9, s)).normalize();
  return { pos: look.clone().addScaledVector(dir, Math.exp(mixv(Math.log(da), Math.log(db), s))), look };
}
const lerpPose = (a, b, s) => ({ pos: a.pos.clone().lerp(b.pos, s), look: a.look.clone().lerp(b.look, s) });
function pose(t, d) {
  if (t < 1.0) return C0(d, t);
  if (t < 2.4) return blendPose(C0(d, t), WIDE(t), smooth(1.0, 2.4, t), 0.35, 1);
  if (t < 5.0) return WIDE(t);
  if (t < 7.0) return blendPose(WIDE(t), RA(d), smooth(5.0, 7.0, t), 0, 0.45);
  if (t < 11.8) return RA(d);
  if (t < 15.2) return crane(d, t, smooth(11.8, 15.2, t));
  if (t < 18.4) return HERO(t);
  return blendPose(HERO(t), C0(d, t), Math.pow(smooth(18.4, 21.0, t), 1.25), 0, 0.3);
}

// ---------- overlay ----------
const out = document.querySelector('#out'), ctx = out.getContext('2d');
const FONT = '"Liberation Mono", Menlo, monospace', C_CREAM = '#f4e6c8', C_TEAL = '#57d0cc', C_RED = 'rgb(214,62,48)', C_GOLD = '#e8bd68';
const typed = (s, t0, t1, t) => { if (t < t0) return ''; const n = Math.max(1, Math.ceil(s.length * clamp((t - t0) / (t1 - t0)))); return s.slice(0, n); };
function text(s, x, y, size, color, { align = 'center', alpha = 1, spacing = 0, stroke = true } = {}) {
  if (!s || alpha <= 0) return; ctx.save(); ctx.globalAlpha = alpha; ctx.font = `bold ${size}px ${FONT}`; ctx.textAlign = align; ctx.textBaseline = 'middle'; ctx.letterSpacing = spacing + 'px';
  if (stroke) { ctx.lineWidth = Math.max(4, size * 0.12); ctx.strokeStyle = 'rgba(3,6,12,.92)'; ctx.lineJoin = 'round'; ctx.strokeText(s, x, y); }
  ctx.shadowColor = 'rgba(0,0,0,.6)'; ctx.shadowBlur = 18; ctx.fillStyle = color; ctx.fillText(s, x, y); ctx.restore();
}
function chip(s, x, y, size, alpha = 1) {
  if (!s || alpha <= 0) return; ctx.save(); ctx.globalAlpha = alpha; ctx.font = `bold ${size}px ${FONT}`; const w = ctx.measureText(s).width, px = size * 0.45, h = size * 1.42;
  ctx.fillStyle = C_RED; ctx.beginPath(); ctx.roundRect(x - w / 2 - px, y - h / 2, w + 2 * px, h, size * 0.22); ctx.fill();
  ctx.fillStyle = '#fff3e0'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(s, x, y + size * 0.04); ctx.restore();
}
const proj = v => { const q = v.clone().project(cam); const p = v.clone().applyMatrix4(cam.matrixWorldInverse); return [(q.x + 1) / 2 * 1080, (1 - q.y) / 2 * 1920, p.z < 0]; };
// a glowing pull beam from the Moon toward a body, with particles flowing along it
function beam(x0, y0, x1, y1, width, rgb, alpha, t, len) {
  const dx = x1 - x0, dy = y1 - y0, L = Math.hypot(dx, dy) || 1, ux = dx / L, uy = dy / L, ex = x0 + ux * len, ey = y0 + uy * len;
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.lineCap = 'round';
  const g = ctx.createLinearGradient(x0, y0, ex, ey); g.addColorStop(0, `rgba(${rgb},${0.9 * alpha})`); g.addColorStop(1, `rgba(${rgb},0)`);
  for (const [w, a] of [[width * 3.2, 0.25], [width, 1]]) { ctx.globalAlpha = a; ctx.strokeStyle = g; ctx.lineWidth = w; ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(ex, ey); ctx.stroke(); }
  ctx.globalAlpha = 1; ctx.fillStyle = `rgba(255,248,230,${0.85 * alpha})`;
  const n = Math.max(2, Math.round(len / 46)); for (let k = 0; k < n; k++) { const s = (((k / n) - (t * 0.55)) % 1 + 1) % 1, px = x0 + ux * len * s, py = y0 + uy * len * s, fade = 1 - s;
    ctx.beginPath(); ctx.arc(px, py, width * 0.42 * fade + 1, 0, 7); ctx.fill(); }
  ctx.restore();
}
function phaseIcon(x, y, r, frac, lit) { // frac 0..1 through a lunation (0 = new); lit side drawn as a crescent/gibbous shape
  ctx.save(); ctx.translate(x, y); ctx.globalAlpha = lit ? 1 : 0.35;
  ctx.fillStyle = 'rgba(30,36,48,.9)'; ctx.beginPath(); ctx.arc(0, 0, r, 0, 7); ctx.fill();
  const k = Math.cos(frac * 2 * Math.PI), waxing = frac < 0.5; ctx.fillStyle = lit ? '#efe6d2' : '#7f8794';
  ctx.beginPath(); ctx.arc(0, 0, r, -Math.PI / 2, Math.PI / 2, !waxing);
  ctx.ellipse(0, 0, r * Math.abs(k), r, 0, Math.PI / 2, -Math.PI / 2, waxing ? k < 0 : k > 0); ctx.fill();
  ctx.strokeStyle = lit ? 'rgba(232,189,104,.9)' : 'rgba(150,160,175,.5)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(0, 0, r, 0, 7); ctx.stroke(); ctx.restore();
}
const grain = [...Array(6)].map((_, k) => { const c = document.createElement('canvas'); c.width = 270; c.height = 480; const x = c.getContext('2d'); const im = x.createImageData(270, 480); let s = 99 + k * 7;
  for (let i = 0; i < im.data.length; i += 4) { s = (s * 16807) % 2147483647; const v = s % 255; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; } x.putImageData(im, 0, 0); return c; });

function overlay(t, st, d) {
  text('SIZES ENLARGED · ORBITS AND PATH TO SCALE', 540, 168, 22, C_CREAM, { alpha: 0.6 * smooth(2.9, 3.3, t) * (1 - smooth(18.4, 18.9, t)), spacing: 1, stroke: false });
  const hk = 1 - smooth(2.75, 3.0, t);
  if (hk > 0) {
    text(typed("THE MOON'S PATH", 0, 0.5, t), 540, 300, 84, C_CREAM, { alpha: hk });
    text(typed('AROUND THE SUN', 0.5, 1.0, t), 540, 392, 64, C_GOLD, { alpha: hk });
    chip(t >= 2.2 ? 'NOT LIKE THIS.' : '', 540, 1520, 54, hk * smooth(2.2, 2.27, t));
  }
  const ts = smooth(2.95, 3.1, t) * (1 - smooth(5.4, 5.8, t));
  text(typed('AT REAL SCALE', 2.95, 3.35, t), 540, 300, 64, C_CREAM, { alpha: ts });
  text(typed('NO LOOPS.', 4.7, 5.0, t), 540, 1520, 92, C_GOLD, { alpha: ts });
  // the pull beams
  const pA = smooth(8.4, 8.6, t) * (1 - smooth(11.6, 11.9, t));
  if (pA > 0) {
    text(typed('THE SUN PULLS THE MOON', 8.4, 9.0, t), 540, 290, 50, C_CREAM, { alpha: pA });
    text(typed('HARDER THAN EARTH DOES.', 9.0, 9.6, t), 540, 360, 50, C_GOLD, { alpha: pA });
    const [mx, my] = proj(moonAt(d)), [ex, ey] = proj(earthAt(d)), [sx, sy] = proj(new T.Vector3(0, 0, 0));
    const bA = pA * smooth(9.0, 9.5, t);
    beam(mx, my, sx, sy, 16, '255,196,96', bA, t, Math.min(560, Math.hypot(sx - mx, sy - my)));
    beam(mx, my, ex, ey, 6, '87,208,204', bA, t, Math.hypot(ex - mx, ey - my) * 0.9);
  }
  const cA = smooth(12.2, 12.4, t) * (1 - smooth(14.4, 14.6, t));
  text(typed('SO ITS PATH ALWAYS', 12.2, 12.8, t), 540, 290, 52, C_CREAM, { alpha: cA });
  text(typed('CURVES TOWARD THE SUN.', 12.8, 13.5, t), 540, 362, 52, C_GOLD, { alpha: cA });
  // labels while riding
  const lA = smooth(7.0, 7.4, t) * (1 - smooth(14.6, 15.0, t)) * (1 - pA);
  if (lA > 0) { const [ex, ey, ef] = proj(earthAt(d)), [mx, my, mf] = proj(moonAt(d));
    if (ef) text('EARTH', ex, ey + 70, 28, C_TEAL, { alpha: lA, spacing: 3 }); if (mf) text('MOON', mx, my - 52, 26, '#e6e0d2', { alpha: lA, spacing: 3 }); }
  // month row: one phase icon per lunar month, lit as each month completes
  const mA = smooth(6.6, 7.0, t) * (1 - smooth(15.0, 15.4, t));
  if (mA > 0) { ctx.save(); ctx.globalAlpha = mA; for (let k = 0; k < 12; k++) phaseIcon(540 + (k - 5.5) * 74, 1530, 24, (k + 0.5) / 12, st.months > k); ctx.restore();
    text(`${st.months} / 12 MONTHS`, 540, 1600, 26, C_CREAM, { alpha: mA * 0.85, spacing: 3, stroke: false }); }
  // twist
  const nA = smooth(15.2, 15.3, t) * (1 - smooth(18.2, 18.5, t));
  text(typed('IT NEVER', 15.2, 15.55, t), 540, 300, 100, C_CREAM, { alpha: nA });
  text(typed('GOES BACKWARDS.', 15.55, 16.2, t), 540, 408, 76, C_GOLD, { alpha: nA });
  const fl = t >= 15.2 ? 0.1 * Math.exp(-(t - 15.2) * 12) : 0;
  if (fl > 0.005) { ctx.save(); ctx.fillStyle = `rgba(255,240,220,${fl})`; ctx.fillRect(0, 0, 1080, 1920); ctx.restore(); }
}
function flare() { // a few soft ghosts along the line through the frame centre when the Sun is on screen
  const [sx, sy, front] = proj(new T.Vector3(0, 0, 0)); if (!front) return; const on = clamp(1.4 - Math.max(Math.abs(sx - 540) / 700, Math.abs(sy - 960) / 1100)); if (on <= 0) return;
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  for (const [k, r, a, c] of [[0.35, 60, 0.05, '255,190,120'], [0.7, 26, 0.07, '120,200,255'], [1.25, 90, 0.035, '255,160,90'], [1.6, 40, 0.05, '180,255,220']]) {
    const x = sx + (540 - sx) * 2 * k, y = sy + (960 - sy) * 2 * k, g = ctx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, `rgba(${c},${a * on})`); g.addColorStop(0.7, `rgba(${c},${a * on * 0.5})`); g.addColorStop(1, `rgba(${c},0)`); ctx.fillStyle = g; ctx.fillRect(x - r, y - r, 2 * r, 2 * r); }
  ctx.restore();
}
function drawFilm() { ctx.drawImage(film, 0, 0, 1080, 1920); ctx.save();
  ctx.globalCompositeOperation = 'lighter'; ctx.filter = 'blur(12px) brightness(0.9)'; ctx.globalAlpha = 0.45; ctx.drawImage(film, 0, 0, 1080, 1920);
  ctx.filter = 'blur(42px)'; ctx.globalAlpha = 0.32; ctx.drawImage(film, 0, 0, 1080, 1920); ctx.restore(); }

window.renderAt = function (t, frame = Math.round(t * 30)) {
  t = ((t % DUR) + DUR) % DUR;
  const st = state(t), d = st.days;
  U.uTime.value = t;
  const E = earthAt(d), M = moonAt(d);
  earthGroup.position.copy(E); moonGroup.position.copy(M);
  earthSpin.rotation.y = 2.2 + t * 0.55 + d * 0.004; EU.uCloudShift.value = t * 0.004;
  EU.uSunDir.value.copy(E).negate().normalize(); moonMesh.material.uniforms.uSunDir.value.copy(M).negate().normalize();
  // tidal lock: texture longitude 0 faces Earth
  const toE = E.clone().sub(M); moonSpin.rotation.y = Math.atan2(toE.y, toE.x);
  const p = pose(t, d); cam.position.copy(p.pos); cam.lookAt(p.look);
  const camDist = p.pos.distanceTo(p.look); cam.near = Math.max(0.0005, camDist * 0.002); cam.updateProjectionMatrix();
  sky.position.copy(cam.position);
  const sunScale = clamp(p.pos.length() / 110, 1, 4.5); sun.scale.setScalar(sunScale); corona.scale.setScalar(sunScale); corona.material.uniforms.uA.value = mixv(1, 0.6, clamp((sunScale - 1) / 2));
  // far away, Earth and Moon keep a small glowing marker so they stay findable
  for (const [g, P] of [[earthGlow, E], [moonGlow, M]]) { g.position.copy(P); g.material.uniforms.uA.value = smooth(2.5, 8, P.distanceTo(cam.position)); }
  // paths
  const ride = smooth(5.0, 6.5, t) * (1 - smooth(18.4, 19.4, t));
  moonPath.uniforms.uNow.value = earthPath.uniforms.uNow.value = d;
  moonPath.uniforms.uFuture.value = 0.12 * smooth(4.2, 5.0, t) * (1 - smooth(18.4, 19.4, t));
  moonPath.uniforms.uA.value = smooth(4.0, 5.0, t) * (1 - smooth(19.6, 20.6, t)); earthPath.uniforms.uA.value = 0.65 * moonPath.uniforms.uA.value;
  earthPath.uniforms.uFuture.value = 0.0;
  moonPath.uniforms.uWidth.value = mixv(3.4, 3.0, ride); earthPath.uniforms.uWidth.value = 2.0;
  moonPath.uniforms.uHead.value = earthPath.uniforms.uHead.value = mixv(10, 2.0, ride);
  sketch.uniforms.uR.value = sketchR(t); sketch.uniforms.uA.value = 0.75 * smooth(1.6, 2.1, t) * (1 - smooth(4.4, 5.0, t)); sketch.uniforms.uWidth.value = 2.6;
  ctx.fillStyle = '#03060c'; ctx.fillRect(0, 0, 1080, 1920);
  renderer.render(scene, cam); drawFilm(); flare();
  ctx.save(); const v = ctx.createRadialGradient(540, 960, 420, 540, 960, 1180); v.addColorStop(0, 'rgba(3,6,12,0)'); v.addColorStop(1, 'rgba(3,6,12,0.7)'); ctx.fillStyle = v; ctx.fillRect(0, 0, 1080, 1920);
  ctx.globalAlpha = 0.04; ctx.globalCompositeOperation = 'overlay'; ctx.drawImage(grain[frame % 6], 0, 0, 1080, 1920); ctx.restore();
  overlay(t, st, d);
  return st;
};
// fact check: the true heliocentric Moon path must curve toward the Sun everywhere (curvature > 0)
window.convexCheck = () => { let min = Infinity; const h = 0.01; for (let d = 0; d < Y; d += 0.05) {
  const a = moonAt(d - h), b = moonAt(d), c = moonAt(d + h); const vx = (c.x - a.x) / 2 / h, vy = (c.y - a.y) / 2 / h, ax = (c.x - 2 * b.x + a.x) / h / h, ay = (c.y - 2 * b.y + a.y) / h / h;
  min = Math.min(min, (vx * ay - vy * ax) / Math.pow(Math.hypot(vx, vy), 3) * R); } return min; };
window.captureFrame = (t, frame) => { window.renderAt(t, frame); return out.toDataURL('image/jpeg', 0.95).split(',')[1]; };
window.renderAt(0.01);
window.ready = true;
