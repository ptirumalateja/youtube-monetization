import * as T from 'three';
// Not a Vortex. Open on the viral "solar system is a vortex" picture, call it wrong, fly past all eight
// planets (true sizes, tilts and spins), then let the Sun move at its real speed through the galaxy:
// the paths are long stretched waves and the planets take turns leading the Sun. Pull out to the whole
// Milky Way, dive to its centre where stars whip around Sagittarius A*, and plunge home (loops).
// Three scenes at three scales, all in galactic axes (x to the Galactic Centre, z to the north pole):
//   solar:  1 unit = 1 AU, Sun at the origin (the planets live in an ecliptic group rotated into galactic axes)
//   galaxy: 1 unit = 1 light year, Sun at the origin, Galactic Centre at (+26,700, 0, 0)
//   core:   1 unit = 1 AU, Sagittarius A* at the origin
const spec = await fetch('./timeline.json').then(r => r.json());
const F = spec.facts, DUR = spec.duration, PL = spec.planets;
const AU = F.au_km, LY_AU = 63241.08, GC_LY = F.sun_to_galactic_centre_ly;
const VSUN = F.sun_speed_kms * F.year_s / AU;                 // AU per year (about 48.5)
const params = new URLSearchParams(location.search), W = +(params.get('w') || 720), H = Math.round(W * 16 / 9);
const film = document.querySelector('#film');
const renderer = new T.WebGLRenderer({ canvas: film, antialias: true, preserveDrawingBuffer: true, logarithmicDepthBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H, false); renderer.outputColorSpace = T.SRGBColorSpace; renderer.autoClear = false;
const FOV = 50;
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const smooth = (a, b, x) => { const s = clamp((x - a) / (b - a)); return s * s * (3 - 2 * s); };
const mixv = (a, b, s) => a + (b - a) * s;
const V3 = (x = 0, y = 0, z = 0) => new T.Vector3(x, y, z);
const RAD = Math.PI / 180;

// ---------- ecliptic -> galactic (J2000 rotation, verified: ecliptic pole 60.2 deg from the galactic pole) ----------
const M_EG = new T.Matrix4().set(-0.054876, -0.993821, -0.096476, 0, 0.494109, -0.110991, 0.862286, 0, -0.867666, -0.000352, 0.497147, 0, 0, 0, 0, 1);
const Q_EG = new T.Quaternion().setFromRotationMatrix(M_EG);
const e2g = v => v.clone().applyQuaternion(Q_EG);
const g2e = v => v.clone().applyQuaternion(Q_EG.clone().invert());
const VG = V3(...F.sun_velocity_galactic_kms).normalize();     // direction of the Sun's motion (galactic axes)
const VE = g2e(VG);                                              // same, ecliptic axes: 60.6 deg out of the ecliptic plane
const ECL_N = e2g(V3(0, 0, 1));                                  // ecliptic north in galactic axes

// ---------- clocks ----------
// Y: years of solar-system time (orbits). Rate keys (video s -> years per video s).
const RATE = [[0, 0.002], [11.0, 0.002], [12.6, 0.3], [13.6, 0.55], [17.4, 0.55], [19.8, 2.6], [29, 2.6]];
const rateAt = t => { for (let k = 1; k < RATE.length; k++) if (t <= RATE[k][0]) { const [t0, r0] = RATE[k - 1], [t1, r1] = RATE[k]; return mixv(r0, r1, smooth(t0, t1, t)); } return RATE.at(-1)[1]; };
const STEP = 1 / 600, NT = Math.round(DUR / STEP), YR = new Float64Array(NT + 1);
for (let i = 0; i < NT; i++) YR[i + 1] = YR[i] + rateAt((i + 0.5) * STEP) * STEP;
const yearAt = t => { const x = clamp(t / STEP, 0, NT), i = Math.min(NT - 1, Math.floor(x)); return mixv(YR[i], YR[i + 1], x - i); };
const T_MOVE = 13.6, Y_MOVE = yearAt(T_MOVE);
const spinHours = t => t * 3.2;                                  // planet rotation runs at 3.2 hours per video second

// ---------- planets: Kepler orbits (J2000 elements); staged so the flyby meets them one after another ----------
const T_TOUR0 = 3.3, T_STOP = 0.9625;                            // first planet at 3.3 s, then one every 0.96 s
const stopTime = i => T_TOUR0 + T_STOP * i;
const STAGE0 = 205;                                              // ecliptic longitude of Mercury at its stop (deg)
PL.forEach((p, i) => { p.R = p.R_km / AU; p.n = 2 * Math.PI / p.P; p.theta = (STAGE0 + 21 * i) * RAD;
  p.M0 = p.theta - p.peri * RAD - p.n * yearAt(stopTime(i)); });
function kepler(p, y) {
  const M = p.M0 + p.n * y; let E = M; for (let k = 0; k < 6; k++) E -= (E - p.e * Math.sin(E) - M) / (1 - p.e * Math.cos(E));
  const xv = p.a * (Math.cos(E) - p.e), yv = p.a * Math.sqrt(1 - p.e * p.e) * Math.sin(E);
  const w = (p.peri - p.node) * RAD, O = p.node * RAD, I = p.i * RAD;
  const cw = Math.cos(w), sw = Math.sin(w), cO = Math.cos(O), sO = Math.sin(O), cI = Math.cos(I), sI = Math.sin(I);
  return V3((cO * cw - sO * sw * cI) * xv + (-cO * sw - sO * cw * cI) * yv, (sO * cw + cO * sw * cI) * xv + (-sO * sw + cO * cw * cI) * yv, (sw * sI) * xv + (cw * sI) * yv);
}
// GLSL version with the same constants, baked per planet
const keplerGLSL = (p, fn) => { const w = (p.peri - p.node) * RAD, O = p.node * RAD, I = p.i * RAD, f = x => x.toFixed(8);
  const cw = Math.cos(w), sw = Math.sin(w), cO = Math.cos(O), sO = Math.sin(O), cI = Math.cos(I), sI = Math.sin(I);
  return `vec3 ${fn}(float y){ float M = ${f(p.M0)} + ${f(p.n)}*y; float E = M; for (int k=0;k<5;k++) E -= (E - ${f(p.e)}*sin(E) - M)/(1. - ${f(p.e)}*cos(E));
    float xv = ${f(p.a)}*(cos(E) - ${f(p.e)}), yv = ${f(p.a * Math.sqrt(1 - p.e * p.e))}*sin(E);
    return vec3(${f(cO * cw - sO * sw * cI)}*xv + ${f(-cO * sw - sO * cw * cI)}*yv, ${f(sO * cw + cO * sw * cI)}*xv + ${f(-sO * sw + cO * cw * cI)}*yv, ${f(sw * sI)}*xv + ${f(cw * sI)}*yv); }`; };
const posEcl = (i, y) => kepler(PL[i], y);                        // Sun-relative, ecliptic axes, AU
const posGal = (i, y) => e2g(posEcl(i, y));

// ---------- the myth: the viral vortex (tight coils, orbital planes square to the motion, planets trailing in a cone) ----------
const MYTH = PL.map((p, i) => ({ r: 0.55 * Math.sqrt(p.a) + 0.15, w: 2 * Math.PI * 0.55 / Math.pow(p.P, 0.35), lag: 0.9 * Math.sqrt(p.a) + 0.2 * i, ph: i * 2.1 }));
const MYTH_V = 2.2, MYTH_AX = V3(0.25, 0.35, 1).normalize();     // myth-world units per video second; screen-up-ish axis
const mythE1 = V3(1, 0, 0).cross(MYTH_AX).normalize(), mythE2 = MYTH_AX.clone().cross(mythE1).normalize();
const mythPos = (i, s) => { const m = MYTH[i], a = m.w * s + m.ph; return mythE1.clone().multiplyScalar(m.r * Math.cos(a)).addScaledVector(mythE2, m.r * Math.sin(a)).addScaledVector(MYTH_AX, MYTH_V * s - m.lag); };

// ---------- scenes and cameras ----------
const sSolar = new T.Scene(), sGal = new T.Scene(), sCore = new T.Scene();
const camS = new T.PerspectiveCamera(FOV, 9 / 16, 1e-7, 1e8), camG = new T.PerspectiveCamera(FOV, 9 / 16, 0.01, 1e7), camC = new T.PerspectiveCamera(FOV, 9 / 16, 0.01, 1e7);
const U = { uH: { value: H }, uAspect: { value: 9 / 16 }, uTime: { value: 0 } };
const tex = (url, srgb = false) => new Promise(res => new T.TextureLoader().load(url, t => { t.colorSpace = T.NoColorSpace; t.anisotropy = 8; t.generateMipmaps = true; res(t); }));
const LOGV = ['#include <common>\n#include <logdepthbuf_pars_vertex>\nuniform float uH; uniform float uAspect;\n', '\n#include <logdepthbuf_vertex>\n'];
const LOGF = ['#include <logdepthbuf_pars_fragment>\n', '\n#include <logdepthbuf_fragment>\n'];
let seed = 11; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
const gauss = () => { let u = 0; for (let k = 0; k < 6; k++) u += rnd(); return u - 3; };
const NOISE = `vec3 h3(vec3 p){ p = vec3(dot(p,vec3(127.1,311.7,74.7)), dot(p,vec3(269.5,183.3,246.1)), dot(p,vec3(113.5,271.9,124.6))); return -1.+2.*fract(sin(p)*43758.5453); }
  float n3(vec3 p){ vec3 i=floor(p), f=fract(p), u=f*f*(3.-2.*f);
    return mix(mix(mix(dot(h3(i),f), dot(h3(i+vec3(1,0,0)),f-vec3(1,0,0)),u.x), mix(dot(h3(i+vec3(0,1,0)),f-vec3(0,1,0)), dot(h3(i+vec3(1,1,0)),f-vec3(1,1,0)),u.x),u.y),
               mix(mix(dot(h3(i+vec3(0,0,1)),f-vec3(0,0,1)), dot(h3(i+vec3(1,0,1)),f-vec3(1,0,1)),u.x), mix(dot(h3(i+vec3(0,1,1)),f-vec3(0,1,1)), dot(h3(i+vec3(1,1,1)),f-vec3(1,1,1)),u.x),u.y),u.z); }
  vec3 cell(vec3 p){ vec3 i = floor(p), f = fract(p); float d1 = 9., d2 = 9.; for (int x=-1;x<=1;x++) for (int y=-1;y<=1;y++) for (int z=-1;z<=1;z++){ vec3 g = vec3(x,y,z);
      vec3 o = 0.5 + 0.5*h3(i+g); vec3 r = g + o - f; float d = dot(r,r); if (d < d1){ d2 = d1; d1 = d; } else if (d < d2) d2 = d; } return vec3(sqrt(d1), sqrt(d2), 0.); }`;
function pointsMat(key, vs, fs, extra = {}, blending = T.AdditiveBlending) {
  const m = new T.ShaderMaterial({ uniforms: { ...U, uA: { value: 1 }, ...extra }, transparent: true, depthWrite: false, blending, vertexShader: vs, fragmentShader: fs });
  m.customProgramCacheKey = () => key; return m;
}
function pointCloud(scene, pos, attrs, mat) {
  const g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute(pos, 3));
  for (const [k, [arr, n]] of Object.entries(attrs)) g.setAttribute(k, new T.Float32BufferAttribute(arr, n));
  const p = new T.Points(g, mat); p.frustumCulled = false; scene.add(p); return p;
}
function sprite(scene, size, key, frag, extra = {}) {   // camera-facing quad, additive
  const m = new T.ShaderMaterial({ uniforms: { ...U, uA: { value: 1 }, ...extra }, transparent: true, depthWrite: false, depthTest: false, blending: T.AdditiveBlending,
    vertexShader: `varying vec2 vUv; void main(){ vUv = uv*2.-1.; float sc = length(modelMatrix[0].xyz); gl_Position = projectionMatrix*(modelViewMatrix*vec4(0.,0.,0.,1.) + vec4(position.xy*sc, 0., 0.)); }`, fragmentShader: frag });
  m.customProgramCacheKey = () => key; const s = new T.Mesh(new T.PlaneGeometry(size, size), m); s.frustumCulled = false; s.renderOrder = -1; scene.add(s); return s;
}

// ================= SOLAR SCENE =================
// sky: stars plus the Milky Way band, laid along the true galactic plane (so it crosses the ecliptic at 60 deg)
const sky = new T.Group(); sSolar.add(sky);
{
  const pos = [], c = [];
  for (let i = 0; i < 16000; i++) { const u = rnd() * 2 - 1, a = rnd() * 2 * Math.PI, s = Math.sqrt(1 - u * u); pos.push(9e4 * s * Math.cos(a), 9e4 * s * Math.sin(a), 9e4 * u); c.push(Math.pow(rnd(), 5), rnd()); }
  for (let i = 0; i < 110000; i++) { // band: thicker and brighter toward the Galactic Centre (+x), with the Great Rift dust lane
    const l = (rnd() * 2 - 1) * Math.PI, toward = 0.5 + 0.5 * Math.cos(l), b = gauss() * (0.05 + 0.09 * toward);
    const rift = Math.abs(b - 0.012 * Math.sin(l * 3)) < 0.016 * (0.4 + toward) && Math.abs(l) < 1.6;
    if (rift && rnd() < 0.85) continue; if (rnd() > 0.35 + 0.65 * toward) continue;
    pos.push(9e4 * Math.cos(b) * Math.cos(l), 9e4 * Math.cos(b) * Math.sin(l), 9e4 * Math.sin(b)); c.push(-(0.15 + 0.85 * rnd()) * (0.35 + 0.65 * toward), rnd()); }
  const m = pointsMat('sky', `uniform float uH; attribute vec2 aC; varying vec2 vC; void main(){ vC = aC; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.);
      gl_PointSize = aC.x >= 0. ? (1.2 + 3.2*aC.x)*uH/1280. : 1.7*uH/1280.; }`,
    `uniform float uA; varying vec2 vC; void main(){ vec2 q = gl_PointCoord*2.-1.; float r = dot(q,q); if (r > 1.) discard;
      vec3 col; float b; if (vC.x >= 0.) { col = vC.y < .2 ? vec3(.62,.72,1.) : vC.y < .7 ? vec3(1.,.96,.9) : vec3(1.,.8,.6); b = .28 + 1.1*vC.x; }
      else { col = mix(vec3(.62,.66,.86), vec3(1.,.85,.68), vC.y); b = -vC.x*.42; }
      gl_FragColor = vec4(col*b*(1.-r)*uA, 1.); }`);
  pointCloud(sky, pos, { aC: [c, 2] }, m);
}

// ecliptic group: everything that orbits lives here, in ecliptic axes, rotated into galactic axes
const ecl = new T.Group(); ecl.quaternion.copy(Q_EG); sSolar.add(ecl);
const SU = { ...U, uSunPos: { value: V3() } };

// ---------- the Sun: white-gold photosphere, granulation cells, sunspot groups, faculae, limb prominences ----------
const R_SUN = 696000 / AU;
const sunMesh = new T.Mesh(new T.SphereGeometry(R_SUN, 128, 96), new T.ShaderMaterial({ uniforms: U,
  vertexShader: `${LOGV[0]} varying vec3 vP; varying vec3 vN; varying vec3 vV; void main(){ vP = position/${R_SUN.toFixed(9)}; vec4 mv = modelViewMatrix*vec4(position,1.); vN = normalize(normalMatrix*normal); vV = normalize(-mv.xyz);
    gl_Position = projectionMatrix*mv; ${LOGV[1]} }`,
  fragmentShader: `${LOGF[0]} uniform float uTime; varying vec3 vP; varying vec3 vN; varying vec3 vV; ${NOISE}
    void main(){ ${LOGF[1]} vec3 p = normalize(vP);
      vec3 c1 = cell(p*110. + vec3(0., 0., uTime*0.08)); float gran = smoothstep(0.0, 0.3, c1.y - c1.x)*(0.7 + 0.6*n3(p*30.));       // bright cells, dark lanes
      vec3 c2 = cell(p*9. + 4.); float sup = smoothstep(0.0, 0.25, c2.y - c2.x);
      float mu = clamp(dot(vN, vV), 0., 1.);
      // sunspot groups in the activity belts (15-30 deg), umbra + penumbra
      float spot = 0., pen = 0.; float lat = asin(clamp(p.y, -1., 1.));
      for (int k = 0; k < 7; k++){ float fk = float(k); vec3 cdir = normalize(vec3(cos(fk*2.3+0.4), (mod(fk,2.)*2.-1.)*(0.28+0.14*fract(fk*0.37)), sin(fk*2.3+0.4)));
        float d = acos(clamp(dot(p, cdir), -1., 1.)) / (0.018 + 0.016*fract(fk*0.71));
        d += 0.35*n3(p*60. + fk); spot = max(spot, 1. - smoothstep(0.45, 0.6, d)); pen = max(pen, 1. - smoothstep(0.9, 1.25, d)); }
      float limb = 0.32 + 0.68*pow(mu, 0.6);
      vec3 hot = vec3(1., .97, .9), warm = vec3(1., .78, .46), deep = vec3(.95, .45, .15);
      vec3 col = mix(warm, hot, 0.35 + 0.65*gran*(0.75 + 0.25*sup)) * mix(vec3(1.), deep/warm*0.9, pow(1.-mu, 2.2));
      float fac = (1.-sup)*pow(1.-mu, 1.5)*0.35*smoothstep(0.1, 0.5, abs(lat));                              // faculae, bright near the limb
      col *= limb*(1. + fac);
      col *= 1. - 0.55*pen; col = mix(col, vec3(.22,.08,.03), 0.85*spot);
      gl_FragColor = vec4(col*0.62, 1.); }` }));
sunMesh.material.customProgramCacheKey = () => 'sun'; sSolar.add(sunMesh);
const corona = sprite(sSolar, R_SUN * 9, 'corona', `uniform float uA; uniform float uTime; varying vec2 vUv; ${NOISE}
  void main(){ float r = length(vUv)*4.5; float ang = atan(vUv.y, vUv.x); if (r < 0.985) discard;
    float glow = 0.8*exp(-(r-1.)*5.5) + 0.25*exp(-(r-1.)*1.3);
    float streak = pow(0.5+0.5*n3(vec3(cos(ang)*2.6, sin(ang)*2.6, 0.3)), 4.)*exp(-(r-1.)*1.1)*0.9;
    // prominences: arcs of hot plasma standing on the limb (H-alpha pink-red)
    float pr = 0.; for (int k=0;k<5;k++){ float fk = float(k); float a0 = fk*1.31 + 0.6; float da = mod(ang - a0 + 3.14159, 6.28318) - 3.14159;
      float h = 0.06 + 0.05*fract(fk*0.77); float arc = exp(-pow((r - 1. - h*sin(clamp(da/0.09, -1., 1.)*1.5708 + 1.5708))/0.008, 2.)) * step(abs(da), 0.09);
      pr += arc*(0.6 + 0.4*n3(vec3(ang*40., r*30., uTime*0.2 + fk))); }
    vec3 c = vec3(1.,.82,.55)*(glow + streak) + vec3(1., .35, .3)*pr*1.4;
    gl_FragColor = vec4(c*uA*smoothstep(4.5, 1.5, r), 1.); }`);
const sunGlare = sprite(sSolar, 1, 'glare', `uniform float uA; varying vec2 vUv; void main(){ float r = length(vUv); float a = exp(-r*7.)*1.2 + exp(-r*2.5)*0.25;
  float rays = pow(abs(cos(atan(vUv.y, vUv.x)*3.)), 40.)*exp(-r*3.)*0.35; gl_FragColor = vec4(vec3(1.,.9,.72)*(a + rays)*(1.-smoothstep(.8,1.,r))*uA, 1.); }`);

// ---------- planets ----------
const T_ = {};
for (const n of ['mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'moon', 'io', 'europa', 'ganymede', 'callisto', 'titan', 'triton', 'earth_day', 'earth_night', 'earth_clouds', 'earth_water'])
  T_[n] = await tex(`assets/${n}.jpg`);
T_.mercury_n = await tex('assets/mercury_normal.png'); T_.moon_n = await tex('assets/moon_normal.png'); T_.rings = await tex('assets/saturn_rings.png');
T_.rings.wrapS = T.ClampToEdgeWrapping; T_.rings.generateMipmaps = false; T_.rings.minFilter = T.LinearFilter;
const RING_IN = 66900 / 58232, RING_OUT = 141000 / 58232;          // in Saturn radii (texture span)

// one generic surface shader: albedo map, optional normal map, limb darkening, atmosphere rim, Saturn ring shadow
function planetMat(key, map, { nrm = null, rim = [0, 0, 0], rimPow = 3, limbK = 0, ringShadow = false, gain = 1.25, amb = 0.015 } = {}) {
  const u = { ...SU, uMap: { value: map }, uNrm: { value: nrm }, uRing: { value: T_.rings }, uRingN: { value: V3(0, 1, 0) }, uCtr: { value: V3() }, uRad: { value: 1 } };
  const m = new T.ShaderMaterial({ uniforms: u,
    vertexShader: `${LOGV[0]} varying vec2 vUv; varying vec3 vNw; varying vec3 vPw; varying vec3 vM0; varying vec3 vM1; varying vec3 vM2;
      void main(){ vUv = uv; vM0 = normalize(modelMatrix[0].xyz); vM1 = normalize(modelMatrix[1].xyz); vM2 = normalize(modelMatrix[2].xyz);
        vNw = normalize(mat3(modelMatrix)*normal); vec4 w = modelMatrix*vec4(position,1.); vPw = w.xyz; gl_Position = projectionMatrix*viewMatrix*w; ${LOGV[1]} }`,
    fragmentShader: `${LOGF[0]} uniform sampler2D uMap; uniform sampler2D uNrm; uniform sampler2D uRing; uniform vec3 uSunPos; uniform vec3 uRingN; uniform vec3 uCtr; uniform float uRad;
      varying vec2 vUv; varying vec3 vNw; varying vec3 vPw; varying vec3 vM0; varying vec3 vM1; varying vec3 vM2;
      void main(){ ${LOGF[1]} vec3 n = normalize(vNw);
        ${nrm ? `vec3 no = texture2D(uNrm, vUv).xyz*2.-1.; vec3 nObj = vec3(no.x, no.z, -no.y); n = normalize(mat3(vM0, vM1, vM2)*nObj);` : ''}
        vec3 L = normalize(uSunPos - vPw), V = normalize(cameraPosition - vPw); float l = dot(n, L), mu = max(dot(normalize(vNw), V), 0.);
        vec3 alb = texture2D(uMap, vUv).rgb;
        float lit = max(l, 0.); ${limbK > 0 ? `lit *= pow(max(dot(normalize(vNw), L), 0.), ${limbK.toFixed(2)}) ; lit = mix(lit, max(l,0.), 0.4);` : ''}
        vec3 col = alb*(${amb.toFixed(3)} + ${gain.toFixed(2)}*lit);
        ${ringShadow ? `{ vec3 p = vPw - uCtr; float dn = dot(L, uRingN); if (abs(dn) > 1e-4) { float tt = -dot(p, uRingN)/dn; if (tt > 0.) { float r = length(p + L*tt)/uRad;
            float a = texture2D(uRing, vec2((r - ${RING_IN.toFixed(5)})/${(RING_OUT - RING_IN).toFixed(5)}, 0.5)).a; if (r > ${RING_IN.toFixed(5)} && r < ${RING_OUT.toFixed(5)}) col *= 1. - 0.88*a; } } }` : ''}
        float fr = pow(1. - mu, ${rimPow.toFixed(1)}); col += vec3(${rim.join(',')})*fr*smoothstep(-0.3, 0.5, dot(normalize(vNw), L));
        gl_FragColor = vec4(col, 1.); }` });
  m.customProgramCacheKey = () => key; return m;
}
const bodies = [];   // { group, spin, mesh, R, i, mat }
function makeBody(i, mat, R, segs = 160) {
  const g = new T.Group(), spin = new T.Group(); g.add(spin); ecl.add(g);
  const mesh = new T.Mesh(new T.SphereGeometry(R, segs, Math.round(segs * 0.75)), mat); spin.add(mesh);
  return { group: g, spin, mesh, R, i, mat };
}
const mats = [
  planetMat('mercury', T_.mercury, { nrm: T_.mercury_n, gain: 1.1, amb: 0.01 }),
  planetMat('venus', T_.venus, { rim: [0.9, 0.75, 0.45], rimPow: 2.5, limbK: 0.6, gain: 0.95 }),
  null,
  planetMat('mars', T_.mars, { rim: [0.7, 0.42, 0.3], rimPow: 4, gain: 1.35 }),
  planetMat('jupiter', T_.jupiter, { rim: [0.35, 0.32, 0.3], rimPow: 3, limbK: 0.45, gain: 1.3 }),
  planetMat('saturn', T_.saturn, { rim: [0.3, 0.28, 0.22], rimPow: 3, limbK: 0.45, ringShadow: true, gain: 1.3 }),
  planetMat('uranus', T_.uranus, { rim: [0.35, 0.5, 0.55], rimPow: 2.5, limbK: 0.7, gain: 0.95 }),
  planetMat('neptune', T_.neptune, { rim: [0.25, 0.4, 0.7], rimPow: 2.5, limbK: 0.5, gain: 1.35 })];
// Earth: Blue Marble day, city lights, clouds, ocean glint, atmosphere (as in The Moon Never Loops, re-lit)
const EU = { ...SU, uDay: { value: T_.earth_day }, uNight: { value: T_.earth_night }, uClouds: { value: T_.earth_clouds }, uWater: { value: T_.earth_water }, uCloudShift: { value: 0 } };
mats[2] = new T.ShaderMaterial({ uniforms: EU,
  vertexShader: `${LOGV[0]} varying vec2 vUv; varying vec3 vNw; varying vec3 vPw; void main(){ vUv = uv; vNw = normalize(mat3(modelMatrix)*normal); vec4 w = modelMatrix*vec4(position,1.); vPw = w.xyz;
    gl_Position = projectionMatrix*viewMatrix*w; ${LOGV[1]} }`,
  fragmentShader: `${LOGF[0]} uniform sampler2D uDay; uniform sampler2D uNight; uniform sampler2D uClouds; uniform sampler2D uWater; uniform vec3 uSunPos; uniform float uCloudShift;
    varying vec2 vUv; varying vec3 vNw; varying vec3 vPw;
    void main(){ ${LOGF[1]} vec3 n = normalize(vNw), L = normalize(uSunPos - vPw), V = normalize(cameraPosition - vPw); float l = dot(n, L);
      vec3 day = texture2D(uDay, vUv).rgb; float cl = texture2D(uClouds, vUv + vec2(uCloudShift, 0.)).r; float water = texture2D(uWater, vUv).r;
      float lit = smoothstep(-0.08, 0.25, l);
      day = mix(day, vec3(dot(day, vec3(.3,.5,.2))), 0.15); vec3 col = day*(0.03 + 1.3*max(l, 0.));
      col = mix(col, vec3(1.)*(0.02 + 1.15*max(l,0.)), cl*0.85);
      vec3 Hh = normalize(L + V); col += water*(1.-cl)*vec3(1.,.9,.75)*pow(max(dot(n, Hh), 0.), 60.)*0.9*lit;
      vec3 night = texture2D(uNight, vUv).rgb; col += night*night*vec3(1.4,1.05,0.65)*(1.-lit)*(1.-cl*0.8)*1.8;
      float fr = pow(1. - max(dot(n, V), 0.), 2.6); col += vec3(.35,.6,1.)*fr*smoothstep(-0.25, 0.4, l)*0.9;
      gl_FragColor = vec4(col, 1.); }` });
mats[2].customProgramCacheKey = () => 'earth';
PL.forEach((p, i) => bodies.push(makeBody(i, mats[i], p.R, i >= 4 ? 200 : 160)));
// atmosphere shells (additive, back faces): Earth blue, Venus haze, Mars thin dust, giants faint
const atmoMat = (key, rgb, k) => { const m = new T.ShaderMaterial({ uniforms: SU, transparent: true, depthWrite: false, blending: T.AdditiveBlending, side: T.BackSide,
  vertexShader: `${LOGV[0]} varying vec3 vNw; varying vec3 vPw; void main(){ vNw = normalize(mat3(modelMatrix)*normal); vec4 w = modelMatrix*vec4(position,1.); vPw = w.xyz; gl_Position = projectionMatrix*viewMatrix*w; ${LOGV[1]} }`,
  fragmentShader: `${LOGF[0]} uniform vec3 uSunPos; varying vec3 vNw; varying vec3 vPw; void main(){ ${LOGF[1]} vec3 n = normalize(vNw), V = normalize(cameraPosition - vPw);
    float rim = clamp(1. - abs(dot(n, V)), 0., 1.); float side = smoothstep(-0.35, 0.5, dot(n, normalize(uSunPos - vPw)));
    gl_FragColor = vec4(vec3(${rgb.join(',')})*pow(rim, 5.)*${k.toFixed(2)}*side, 1.); }` }); m.customProgramCacheKey = () => key; return m; };
for (const [i, rgb, k, s] of [[1, [1.0, 0.85, 0.55], 1.2, 1.04], [2, [0.32, 0.58, 1.0], 1.6, 1.06], [3, [0.85, 0.55, 0.4], 0.7, 1.03], [4, [0.6, 0.55, 0.5], 0.5, 1.02], [5, [0.6, 0.55, 0.4], 0.5, 1.02], [6, [0.5, 0.8, 0.9], 0.8, 1.03], [7, [0.4, 0.6, 1.0], 0.9, 1.03]])
  bodies[i].group.add(new T.Mesh(new T.SphereGeometry(PL[i].R * s, 96, 64), atmoMat('atmo' + i, rgb, k)));
// Saturn's rings: measured radii (D to F ring), forward-scattering when back-lit, Saturn's shadow across them
const ringU = { ...SU, uRing: { value: T_.rings }, uCtr: { value: V3() }, uRad: { value: PL[5].R } };
const ringMat = new T.ShaderMaterial({ uniforms: ringU, transparent: true, depthWrite: false, side: T.DoubleSide,
  vertexShader: `${LOGV[0]} varying vec3 vPw; varying vec3 vNw; void main(){ vec4 w = modelMatrix*vec4(position,1.); vPw = w.xyz; vNw = normalize(mat3(modelMatrix)*vec3(0.,0.,1.)); gl_Position = projectionMatrix*viewMatrix*w; ${LOGV[1]} }`,
  fragmentShader: `${LOGF[0]} uniform sampler2D uRing; uniform vec3 uSunPos; uniform vec3 uCtr; uniform float uRad; varying vec3 vPw; varying vec3 vNw;
    void main(){ ${LOGF[1]} vec3 p = vPw - uCtr; float r = length(p)/uRad; float u = (r - ${RING_IN.toFixed(5)})/${(RING_OUT - RING_IN).toFixed(5)}; if (u < 0. || u > 1.) discard;
      vec4 s = texture2D(uRing, vec2(u, 0.5)); vec3 L = normalize(uSunPos - vPw), V = normalize(cameraPosition - vPw);
      float sameSide = sign(dot(L, vNw))*sign(dot(V, vNw));                     // lit face vs unlit face
      float lit = sameSide > 0. ? 0.12 + 0.75*sqrt(abs(dot(L, vNw))) : (1. - s.a)*1.2*sqrt(abs(dot(L, vNw)));   // unlit face: light leaks through the thin parts
      lit = clamp(lit, 0., 1.4);
      float dl = dot(p, L); vec3 perp = p - L*dl; float sh = (dl < 0. && length(perp) < uRad) ? 0.06 : 1.;  // Saturn's shadow on the rings
      gl_FragColor = vec4(s.rgb*lit*sh*1.05, s.a*0.97); }` });
ringMat.customProgramCacheKey = () => 'rings';
const ringMesh = new T.Mesh(new T.RingGeometry(PL[5].R * RING_IN, PL[5].R * RING_OUT, 512, 4), ringMat); ringMesh.renderOrder = 3;
bodies[5].group.add(ringMesh);   // ring lies in the planet's equator: oriented with the tilt group below
// Uranus: thin dark rings (epsilon brightest) seen against the planet and the sky
const uRingMat = new T.ShaderMaterial({ uniforms: { ...SU, uCtr: { value: V3() }, uRad: { value: PL[6].R } }, transparent: true, depthWrite: false, side: T.DoubleSide,
  vertexShader: `${LOGV[0]} varying vec3 vPw; void main(){ vec4 w = modelMatrix*vec4(position,1.); vPw = w.xyz; gl_Position = projectionMatrix*viewMatrix*w; ${LOGV[1]} }`,
  fragmentShader: `${LOGF[0]} uniform vec3 uCtr; uniform float uRad; varying vec3 vPw; void main(){ ${LOGF[1]} float r = length(vPw - uCtr)/uRad;
    float a = 0.; for (int k=0;k<9;k++){ float rk = 1.64 + 0.045*float(k) + (k==8 ? 0.07 : 0.); a += exp(-pow((r - rk)/(k==8 ? 0.006 : 0.0025), 2.))*(k==8 ? 0.9 : 0.35); }
    gl_FragColor = vec4(vec3(.62,.66,.7)*a*0.5, a*0.6); }` });
uRingMat.customProgramCacheKey = () => 'uring';
const uRing = new T.Mesh(new T.RingGeometry(PL[6].R * 1.6, PL[6].R * 2.1, 256, 2), uRingMat); bodies[6].group.add(uRing);

// tilt each planet: pole leans from ecliptic north by the true obliquity, in a direction staged for the camera
const POLE_AZ = [0, 90, 200, 30, 0, 150, 180, 40];                 // relative to the planet's staged longitude (deg)
bodies.forEach((b, i) => { const p = PL[i], az = p.theta + POLE_AZ[i] * RAD, tl = p.tilt * RAD;
  const pole = V3(Math.sin(tl) * Math.cos(az), Math.sin(tl) * Math.sin(az), Math.cos(tl));
  b.pole = pole; b.tiltQ = new T.Quaternion().setFromUnitVectors(V3(0, 1, 0), pole); });
ringMesh.quaternion.setFromUnitVectors(V3(0, 0, 1), V3(0, 1, 0)); uRing.quaternion.copy(ringMesh.quaternion);
// rings and atmospheres must tilt with the planet but not spin: put them under a tilt group
bodies.forEach(b => { const tg = new T.Group(); tg.quaternion.copy(b.tiltQ); b.group.add(tg); b.spin.removeFromParent(); tg.add(b.spin); b.tilt = tg; });
bodies[5].group.remove(ringMesh); bodies[5].tilt.add(ringMesh); bodies[6].group.remove(uRing); bodies[6].tilt.add(uRing);

// moons (true distances and sizes): the Moon, the Galilean moons, Titan, Triton
const MOONS = [ // planet, texture, radius km, distance km, period days, phase
  [2, 'moon', 1737, 384400, 27.32, 2.5], [4, 'io', 1822, 421700, 1.769, 0.6], [4, 'europa', 1561, 671000, 3.551, 2.4], [4, 'ganymede', 2634, 1070400, 7.155, 4.1],
  [4, 'callisto', 2410, 1882700, 16.69, 5.5], [5, 'titan', 2575, 1221870, 15.95, 3.9], [7, 'triton', 1353, 354759, -5.877, 1.0]];
const moonBodies = MOONS.map(([pi, n, rk, dk, per, ph]) => { const m = planetMat('moon_' + n, T_[n], n === 'moon' ? { nrm: T_.moon_n, gain: 1.35 } : { gain: 1.3 });
  const mesh = new T.Mesh(new T.SphereGeometry(rk / AU, 64, 48), m); ecl.add(mesh); return { mesh, pi, d: dk / AU, per, ph, mat: m }; });

// asteroid belt and Kuiper belt (points, in the ecliptic, slow Keplerian shear)
function belt(n, r0, r1, thick, key, rgb, size) {
  const pos = [], a = []; for (let i = 0; i < n; i++) { const r = r0 + (r1 - r0) * Math.pow(rnd(), 0.8); pos.push(r, rnd() * 2 * Math.PI, gauss() * thick * r); a.push(rnd()); }
  const m = pointsMat(key, `${LOGV[0]} uniform float uY; attribute float aR; varying float vR; void main(){ vR = aR; float r = position.x, th = position.y + 6.2832*uY/pow(r, 1.5);
      vec4 mv = modelViewMatrix*vec4(r*cos(th), r*sin(th), position.z, 1.); gl_Position = projectionMatrix*mv; gl_PointSize = clamp(${size.toFixed(1)}*uH/1280.*(0.6+0.8*aR), 1., 4.); ${LOGV[1]} }`,
    `${LOGF[0]} uniform float uA; varying float vR; void main(){ ${LOGF[1]} vec2 q = gl_PointCoord*2.-1.; float r = dot(q,q); if (r > 1.) discard; gl_FragColor = vec4(vec3(${rgb.join(',')})*(0.4+0.6*vR)*(1.-r)*uA, 1.); }`,
    { uY: { value: 0 } });
  return pointCloud(ecl, pos, { aR: [a, 1] }, m);
}
const astBelt = belt(26000, 2.1, 3.3, 0.06, 'ast', [0.85, 0.78, 0.66], 1.8), kuiper = belt(22000, 30, 50, 0.08, 'kuiper', [0.6, 0.7, 0.85], 1.6);

// orbit lines (true ellipses), faint cream
const orbitLines = PL.map((p, i) => { const pts = []; for (let k = 0; k <= 720; k++) pts.push(kepler(p, -p.M0 / p.n + (k / 720) * p.P));
  const g = new T.BufferGeometry().setFromPoints(pts); const m = new T.ShaderMaterial({ uniforms: { uA: { value: 0 } }, transparent: true, depthWrite: false, blending: T.AdditiveBlending,
    vertexShader: `${LOGV[0]} void main(){ gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); ${LOGV[1]} }`,
    fragmentShader: `${LOGF[0]} uniform float uA; void main(){ ${LOGF[1]} gl_FragColor = vec4(vec3(.95,.86,.68)*uA, 1.); }` });
  m.customProgramCacheKey = () => 'orb' + i; const l = new T.Line(g, m); l.frustumCulled = false; ecl.add(l); return m; });

// glow markers so planets stay findable when they are sub-pixel (wide shots); sized in pixels
const glowMat = (key, rgb) => pointsMat(key, `${LOGV[0]} uniform float uPx; void main(){ gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); gl_PointSize = uPx*uH/1280.; ${LOGV[1]} }`,
  `${LOGF[0]} uniform float uA; void main(){ ${LOGF[1]} vec2 q = gl_PointCoord*2.-1.; float r = dot(q,q); if (r > 1.) discard; gl_FragColor = vec4(vec3(${rgb.join(',')})*(exp(-r*6.)*1.3 + 0.15*(1.-r))*uA, 1.); }`, { uPx: { value: 14 } });
const PCOL = [[0.8, 0.78, 0.74], [1, 0.9, 0.7], [0.5, 0.8, 1], [1, 0.6, 0.4], [1, 0.85, 0.65], [1, 0.9, 0.7], [0.65, 0.9, 0.95], [0.5, 0.7, 1]];
const moonGlows = MOONS.map((m, k) => { const pc = pointCloud(ecl, [0, 0, 0], {}, glowMat('mg' + k, [1, 0.96, 0.9])); pc.renderOrder = 8; return pc; });
const glows = PL.map((p, i) => { const pc = pointCloud(ecl, [0, 0, 0], {}, glowMat('pg' + i, PCOL[i])); pc.renderOrder = 8; return pc; });

// ---------- paths: screen-space ribbons evaluated in the vertex shader ----------
// mode 0: the true path in the galaxy's frame, relative to the Sun now:  P(tau) = V*(tau - now) + orbit(tau)
// mode 1: the myth path (tight coil, trailing cone), relative to the myth Sun now
function ribbon(i, mode, span, nseg, rgb) {
  const tau = [], side = [], idx = [];
  for (let k = 0; k <= nseg; k++) { tau.push(k / nseg, k / nseg); side.push(-1, 1); if (k < nseg) { const a = 2 * k; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); } }
  const g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute(new Array(tau.length * 3).fill(0), 3));
  g.setAttribute('aU', new T.Float32BufferAttribute(tau, 1)); g.setAttribute('aSide', new T.Float32BufferAttribute(side, 1)); g.setIndex(idx);
  const m = mode === 0 ? MYTH[i] : null;
  const pfn = mode === 0 ? keplerGLSL(PL[i], 'orb') + `vec3 P(float y){ return ${VE.x.toFixed(6)}*vec3(1.,0.,0.)*${VSUN.toFixed(4)}*(y - uNow) + vec3(0., ${VE.y.toFixed(6)}*${VSUN.toFixed(4)}*(y - uNow), ${VE.z.toFixed(6)}*${VSUN.toFixed(4)}*(y - uNow)) + orb(y); }`
    : `vec3 P(float s){ float a = ${MYTH[i].w.toFixed(5)}*s + ${MYTH[i].ph.toFixed(4)}; return vec3(${mythE1.toArray().map(x => x.toFixed(5))})*${MYTH[i].r.toFixed(4)}*cos(a) + vec3(${mythE2.toArray().map(x => x.toFixed(5))})*${MYTH[i].r.toFixed(4)}*sin(a)
         + vec3(${MYTH_AX.toArray().map(x => x.toFixed(5))})*(${MYTH_V.toFixed(4)}*(s - uNow) - ${MYTH[i].lag.toFixed(4)}); }`;
  const mat = new T.ShaderMaterial({ uniforms: { ...U, uNow: { value: 0 }, uStart: { value: 0 }, uWidth: { value: 3 }, uA: { value: 1 }, uHead: { value: 0.1 } },
    transparent: true, depthWrite: false, depthTest: true, blending: T.AdditiveBlending, side: T.DoubleSide,
    vertexShader: `${LOGV[0]} uniform float uNow; uniform float uStart; uniform float uWidth; attribute float aU; attribute float aSide; varying float vU; varying float vSide; varying float vAge;
      ${pfn}
      void main(){ float y = mix(uStart, uNow, aU); float dt = max((uNow - uStart)/${nseg}., 1e-6); vU = aU; vSide = aSide; vAge = uNow - y;
        mat4 MV = projectionMatrix*viewMatrix*modelMatrix; vec4 p0 = MV*vec4(P(y),1.), p1 = MV*vec4(P(y+dt),1.), pm = MV*vec4(P(y-dt),1.);
        vec2 s1 = p1.xy/max(p1.w,1e-6), sm = pm.xy/max(pm.w,1e-6);
        vec2 dir = (s1 - sm)*vec2(uAspect,1.); dir = length(dir) > 1e-9 ? normalize(dir) : vec2(1.,0.);
        vec2 n = vec2(-dir.y, dir.x)/vec2(uAspect,1.);
        float w = uWidth*(0.35 + 0.65*aU);
        gl_Position = p0 + vec4(n*aSide*w/uH*p0.w, 0., 0.); ${LOGV[1]}
        if (p0.w < 1e-6 || p1.w < 1e-6 || pm.w < 1e-6) gl_Position = vec4(0.,0.,-2.,1.); }`,
    fragmentShader: `${LOGF[0]} uniform float uA; uniform float uHead; varying float vU; varying float vSide; varying float vAge;
      void main(){ ${LOGF[1]} float edge = 1. - vSide*vSide; float head = exp(-vAge/uHead);
        float b = (0.18 + 0.82*pow(vU, 1.6)) + 1.2*head;
        gl_FragColor = vec4(vec3(${rgb.join(',')})*b*edge*uA, 1.); }` });
  mat.customProgramCacheKey = () => `rib${mode}_${i}`;
  const mesh = new T.Mesh(g, mat); mesh.frustumCulled = false; mesh.renderOrder = 6;
  (mode === 0 ? ecl : sSolar).add(mesh); return mat;
}
const TRAIL_COL = [[0.85, 0.82, 0.78], [1, 0.85, 0.55], [0.35, 0.85, 0.95], [1, 0.5, 0.32], [1, 0.75, 0.45], [1, 0.88, 0.6], [0.55, 0.9, 0.95], [0.45, 0.65, 1]];
const trails = PL.map((p, i) => ribbon(i, 0, 0, i < 4 ? 9000 : 3000, TRAIL_COL[i]));
const mythTrails = PL.map((p, i) => ribbon(i, 1, 0, 2400, TRAIL_COL[i]));
// the Sun's own path (galaxy frame): a straight gold line behind it; the myth Sun gets a comet tail
const sunTrailMat = new T.ShaderMaterial({ uniforms: { ...U, uLen: { value: 0 }, uA: { value: 0 }, uDir: { value: VE.clone() }, uWidth: { value: 5 } }, transparent: true, depthWrite: false, blending: T.AdditiveBlending, side: T.DoubleSide,
  vertexShader: `${LOGV[0]} uniform float uLen; uniform vec3 uDir; uniform float uWidth; attribute float aU; attribute float aSide; varying float vU; varying float vSide;
    void main(){ vU = aU; vSide = aSide; vec3 P0 = -uDir*uLen*(1.-aU); mat4 MV = projectionMatrix*viewMatrix*modelMatrix; vec4 p0 = MV*vec4(P0,1.), p1 = MV*vec4(P0 + uDir*0.01*uLen + uDir*1e-4,1.);
      vec2 dir = (p1.xy/max(p1.w,1e-6) - p0.xy/max(p0.w,1e-6))*vec2(uAspect,1.); dir = length(dir) > 1e-9 ? normalize(dir) : vec2(1.,0.); vec2 n = vec2(-dir.y, dir.x)/vec2(uAspect,1.);
      gl_Position = p0 + vec4(n*aSide*uWidth*(0.3+0.7*aU)/uH*p0.w, 0., 0.); ${LOGV[1]} if (p0.w < 1e-6) gl_Position = vec4(0.,0.,-2.,1.); }`,
  fragmentShader: `${LOGF[0]} uniform float uA; varying float vU; varying float vSide; void main(){ ${LOGF[1]} float e = 1. - vSide*vSide; gl_FragColor = vec4(vec3(1.,.82,.5)*e*(0.15 + 0.85*pow(vU, 2.))*uA, 1.); }` });
sunTrailMat.customProgramCacheKey = () => 'suntrail';
{ const tau = [], side = [], idx = []; for (let k = 0; k <= 400; k++) { tau.push(k / 400, k / 400); side.push(-1, 1); if (k < 400) { const a = 2 * k; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); } }
  const g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute(new Array(tau.length * 3).fill(0), 3)); g.setAttribute('aU', new T.Float32BufferAttribute(tau, 1)); g.setAttribute('aSide', new T.Float32BufferAttribute(side, 1)); g.setIndex(idx);
  const ms = new T.Mesh(g, sunTrailMat); ms.frustumCulled = false; ms.renderOrder = 6; ecl.add(ms); }

// interstellar dust streaming past at the Sun's speed (galaxy frame seen from the Sun): sells the motion
const dustMat = pointsMat('dust', `${LOGV[0]} uniform float uS; uniform vec3 uV; uniform float uBox; attribute float aR; varying float vR;
    void main(){ vR = aR; vec3 p = mod(position - uV*uS + uBox*0.5, uBox) - uBox*0.5; vec4 mv = modelViewMatrix*vec4(p, 1.); gl_Position = projectionMatrix*mv;
      gl_PointSize = clamp((1.2 + 2.0*aR)*uH/1280.*6./max(-mv.z, 0.5), 0.8, 5.); ${LOGV[1]} }`,
  `${LOGF[0]} uniform float uA; varying float vR; void main(){ ${LOGF[1]} vec2 q = gl_PointCoord*2.-1.; float r = dot(q,q); if (r > 1.) discard; gl_FragColor = vec4(vec3(.75,.85,1.)*(0.3+0.7*vR)*(1.-r)*uA, 1.); }`,
  { uS: { value: 0 }, uV: { value: VE.clone().multiplyScalar(VSUN) }, uBox: { value: 120 } });
{ const pos = [], a = []; for (let i = 0; i < 9000; i++) { pos.push((rnd() - 0.5) * 120, (rnd() - 0.5) * 120, (rnd() - 0.5) * 120); a.push(rnd()); } pointCloud(ecl, pos, { aR: [a, 1] }, dustMat); }

// myth Sun (a comet-like glowing ball with a tail) and myth planets (glowing beads)
const mythSun = sprite(sSolar, 1.6, 'mythsun', `uniform float uA; varying vec2 vUv; void main(){ float r = length(vUv); float a = smoothstep(0.32, 0.27, r)*1.2 + exp(-r*5.)*0.9;
  gl_FragColor = vec4(vec3(1.,.86,.55)*a*uA, 1.); }`);
const mythBeads = PL.map((p, i) => sprite(sSolar, 0.32 + 0.06 * Math.sqrt(i), 'mb' + i, `uniform float uA; varying vec2 vUv; void main(){ float r = length(vUv); float a = smoothstep(0.42, 0.34, r)*1.1 + exp(-r*6.)*0.6;
  gl_FragColor = vec4(vec3(${TRAIL_COL[i].join(',')})*a*uA, 1.); }`));
const mythTail = new T.ShaderMaterial({ uniforms: { ...U, uA: { value: 0 } }, transparent: true, depthWrite: false, blending: T.AdditiveBlending, side: T.DoubleSide,
  vertexShader: `uniform float uA; uniform float uH; uniform float uAspect; attribute float aU; attribute float aSide; varying float vU; varying float vSide; void main(){ vU = aU; vSide = aSide;
    vec3 ax = vec3(${MYTH_AX.toArray().map(x => x.toFixed(5))}); vec3 P0 = -ax*14.*(1.-aU);
    vec4 p0 = projectionMatrix*viewMatrix*vec4(P0,1.), p1 = projectionMatrix*viewMatrix*vec4(P0 + ax*0.05,1.);
    vec2 dir = normalize((p1.xy/p1.w - p0.xy/p0.w)*vec2(uAspect,1.)); vec2 n = vec2(-dir.y, dir.x)/vec2(uAspect,1.);
    gl_Position = p0 + vec4(n*aSide*(6. + 40.*aU*aU)/uH*p0.w, 0., 0.); }`,
  fragmentShader: `uniform float uA; varying float vU; varying float vSide; void main(){ float e = exp(-vSide*vSide*3.); gl_FragColor = vec4(vec3(1.,.8,.45)*e*pow(vU, 2.5)*0.9*uA, 1.); }` });
mythTail.customProgramCacheKey = () => 'mythtail';
{ const tau = [], side = [], idx = []; for (let k = 0; k <= 200; k++) { tau.push(k / 200, k / 200); side.push(-1, 1); if (k < 200) { const a = 2 * k; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); } }
  const g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute(new Array(tau.length * 3).fill(0), 3)); g.setAttribute('aU', new T.Float32BufferAttribute(tau, 1)); g.setAttribute('aSide', new T.Float32BufferAttribute(side, 1)); g.setIndex(idx);
  const ms = new T.Mesh(g, mythTail); ms.frustumCulled = false; ms.renderOrder = 4; sSolar.add(ms); }

// galactic plane through the Sun (shown in the wide shot): a faint teal disc, 60 deg to the planets' plane
const gPlaneMat = new T.ShaderMaterial({ uniforms: { uA: { value: 0 } }, transparent: true, depthWrite: false, blending: T.AdditiveBlending, side: T.DoubleSide,
  vertexShader: `${LOGV[0]} varying vec2 vP; void main(){ vP = position.xy; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); ${LOGV[1]} }`,
  fragmentShader: `${LOGF[0]} uniform float uA; varying vec2 vP; void main(){ ${LOGF[1]} float r = length(vP)/70.; if (r > 1.) discard;
    vec2 g = abs(fract(vP/7.) - 0.5); float line = smoothstep(0.47, 0.5, max(g.x, g.y));
    gl_FragColor = vec4(vec3(.34,.82,.8)*(0.05 + 0.25*line)*(1.-r)*uA, 1.); }` });
gPlaneMat.customProgramCacheKey = () => 'gplane';
const gPlane = new T.Mesh(new T.CircleGeometry(70, 128), gPlaneMat); sSolar.add(gPlane);   // galactic axes: the disc is the x-y plane

// ================= GALAXY SCENE (light years, Sun at origin) =================
const GC = V3(GC_LY, 0, 0);
const galaxy = new T.Group(); galaxy.position.copy(GC); sGal.add(galaxy);
{
  // barred spiral: bar 27 deg from the Sun-centre line, four major log-spiral arms (pitch 12 deg), trailing for clockwise rotation (seen from the north)
  const pos = [], col = [], dpos = [], dcol = [];
  const PHI_SUN = Math.PI;                                         // the Sun sits at angle 180 deg from the centre (x = -26,700)
  const BAR = 27 * RAD + Math.PI, pitch = 12 * RAD, k = 1 / Math.tan(pitch);
  const add = (x, y, z, c) => { pos.push(x, y, z); col.push(...c); };
  for (let i = 0; i < 60000; i++) { // bar + bulge (warm), boxy
    const a = gauss() * 14000 * (rnd() < 0.5 ? 0.5 : 0.25), b = gauss() * 3800, c = gauss() * 1500 * (0.4 + rnd());
    add(a * Math.cos(BAR) - b * Math.sin(BAR), a * Math.sin(BAR) + b * Math.cos(BAR), c, [1.0, 0.78 + 0.1 * rnd(), 0.52, 0.22 + 0.25 * rnd(), 0]); }
  for (let i = 0; i < 30000; i++) { const r = Math.abs(gauss()) * 2200, th = rnd() * 6.283, z = gauss() * 1200; add(r * Math.cos(th), r * Math.sin(th), z * (1 - r / 9000), [1, 0.86, 0.66, 0.3 + 0.2 * rnd(), 0]); }
  const arms = [0, 0.5 * Math.PI, Math.PI, 1.5 * Math.PI];
  const armR0 = 11000;
  for (let ai = 0; ai < 4; ai++) {
    for (let i = 0; i < 55000; i++) { // stars along the arm
      const r = armR0 + Math.pow(rnd(), 0.9) * 48000, th = BAR + arms[ai] + Math.log(r / armR0) * k * 0.62;
      const w = 900 + r * 0.035, off = gauss() * w, z = gauss() * (250 + r * 0.004);
      const x = (r + off) * Math.cos(th), y = (r + off) * Math.sin(th);
      const young = rnd() < 0.55; add(x, y, z, young ? [0.55, 0.7, 1.0, 0.8 + 0.9 * rnd(), 0] : [1, 0.93, 0.84, 0.45 + 0.5 * rnd(), 0]);
      if (rnd() < 0.015) { // H II regions: pink knots clustered on the arm
        for (let j = 0; j < 6; j++) add(x + gauss() * 160, y + gauss() * 160, z + gauss() * 60, [1, 0.55, 0.65, 0.7 + 0.5 * rnd(), 1]); }
      if (rnd() < 0.5) { // dust lane on the inner (concave) edge of the arm
        const ro = r + off - w * 0.9 - Math.abs(gauss()) * 300; dpos.push(ro * Math.cos(th - 0.01), ro * Math.sin(th - 0.01), gauss() * 120); dcol.push(0.5 + 0.5 * rnd()); }
    }
  }
  // Orion Spur: the short arm segment where the Sun lives, between the Sagittarius and Perseus arms
  for (let i = 0; i < 14000; i++) { const s = (rnd() - 0.5) * 16000, th = PHI_SUN + s / 26700 * 1.0, r = 26700 + s * 0.45 + gauss() * 700;
    add(r * Math.cos(th), r * Math.sin(th), gauss() * 300, rnd() < 0.6 ? [0.65, 0.78, 1, 0.45 + 0.5 * rnd(), 0] : [1, 0.94, 0.86, 0.35 + 0.3 * rnd(), 0]); }
  for (let i = 0; i < 90000; i++) { // smooth exponential disc between the arms
    const r = -Math.log(1 - rnd() * 0.995) * 11000 + 1500, th = rnd() * 6.283; add(r * Math.cos(th), r * Math.sin(th), gauss() * 450, [1, 0.9, 0.78, 0.18 + 0.25 * rnd(), 0]); }
  const m = pointsMat('gal', `${LOGV[0]} attribute vec3 aCol; attribute vec2 aB; varying vec3 vC; varying float vB; void main(){ vC = aCol; vB = aB.x;
      vec4 mv = modelViewMatrix*vec4(position,1.); gl_Position = projectionMatrix*mv; float d = -mv.z;
      gl_PointSize = clamp((aB.y > 0.5 ? 2.6 : 1.7)*uH/1280.*mix(1., 60000./max(d, 1.), 0.15), 1., 4.); vB *= clamp(d/120., 0.15, 1.); ${LOGV[1]} }`,
    `${LOGF[0]} uniform float uA; varying vec3 vC; varying float vB; void main(){ ${LOGF[1]} vec2 q = gl_PointCoord*2.-1.; float r = dot(q,q); if (r > 1.) discard; gl_FragColor = vec4(vC*vB*(1.-r)*0.55*uA, 1.); }`);
  const c3 = [], c2 = []; for (let i = 0; i < col.length; i += 5) { c3.push(col[i], col[i + 1], col[i + 2]); c2.push(col[i + 3], col[i + 4]); }
  galaxy.userData.stars = pointCloud(galaxy, pos, { aCol: [c3, 3], aB: [c2, 2] }, m);
  const dm = pointsMat('galdust', `${LOGV[0]} attribute float aD; varying float vD; void main(){ vD = aD; vec4 mv = modelViewMatrix*vec4(position,1.); gl_Position = projectionMatrix*mv;
      gl_PointSize = clamp(3.2*uH/1280.*60000./max(-mv.z, 1.), 1.5, 9.); ${LOGV[1]} }`,
    `${LOGF[0]} uniform float uA; varying float vD; void main(){ ${LOGF[1]} vec2 q = gl_PointCoord*2.-1.; float r = dot(q,q); if (r > 1.) discard; gl_FragColor = vec4(vec3(0.02,0.015,0.01), (1.-r)*0.22*vD*uA); }`,
    {}, T.NormalBlending);
  galaxy.userData.dust = pointCloud(galaxy, dpos, { aD: [dcol, 1] }, dm);
  // soft glows: the bulge and the disc
  galaxy.userData.glow = sprite(sGal, 1, 'galglow', `uniform float uA; varying vec2 vUv; void main(){ float r = length(vUv); gl_FragColor = vec4(vec3(1.,.8,.55)*(exp(-r*9.)*1.1 + exp(-r*3.5)*0.2)*uA, 1.); }`);
}
// the Sun's orbit around the centre (dashed cream) and the Sun marker
const sunOrbitMat = new T.ShaderMaterial({ uniforms: { uA: { value: 0 } }, transparent: true, depthWrite: false, blending: T.AdditiveBlending,
  vertexShader: `${LOGV[0]} attribute float aK; varying float vK; void main(){ vK = aK; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); ${LOGV[1]} }`,
  fragmentShader: `${LOGF[0]} uniform float uA; varying float vK; void main(){ ${LOGF[1]} if (fract(vK*90.) > 0.55) discard; gl_FragColor = vec4(vec3(.98,.9,.72)*0.8*uA, 1.); }` });
sunOrbitMat.customProgramCacheKey = () => 'sunorbit';
{ const pts = [], k = []; for (let i = 0; i <= 1440; i++) { const a = Math.PI + i / 1440 * 2 * Math.PI; pts.push(V3(GC_LY * Math.cos(a), GC_LY * Math.sin(a), 0)); k.push(i / 1440); }
  const g = new T.BufferGeometry().setFromPoints(pts); g.setAttribute('aK', new T.Float32BufferAttribute(k, 1)); const l = new T.Line(g, sunOrbitMat); l.frustumCulled = false; galaxy.add(l); }
// local stars near the Sun (within ~60 ly), including Alpha Centauri, Sirius and Barnard's star in their real directions
const localStars = (() => { const pos = [], c = [];
  const real = [[4.37, 315.7, -0.68, 1.4], [8.6, 227.2, -8.9, 2.2], [5.96, 31.0, 14.1, 0.5], [10.5, 195.8, -48.0, 0.6], [11.4, 78.3, -19.1, 0.6]]; // d ly, l, b, brightness
  for (const [d, l, b, br] of real) { pos.push(d * Math.cos(b * RAD) * Math.cos(l * RAD), d * Math.cos(b * RAD) * Math.sin(l * RAD), d * Math.sin(b * RAD)); c.push(br, 0.3); }
  for (let i = 0; i < 4000; i++) { const r = 60 * Math.cbrt(rnd()), u = rnd() * 2 - 1, a = rnd() * 6.283, s = Math.sqrt(1 - u * u); pos.push(r * s * Math.cos(a), r * s * Math.sin(a), r * u); c.push(0.2 + 0.6 * Math.pow(rnd(), 3), rnd()); }
  const m = pointsMat('local', `${LOGV[0]} attribute vec2 aC; varying vec2 vC; void main(){ vC = aC; vec4 mv = modelViewMatrix*vec4(position,1.); gl_Position = projectionMatrix*mv;
      gl_PointSize = clamp((1.5 + 5.*aC.x)*uH/1280., 1., 9.); ${LOGV[1]} }`,
    `${LOGF[0]} uniform float uA; varying vec2 vC; void main(){ ${LOGF[1]} vec2 q = gl_PointCoord*2.-1.; float r = dot(q,q); if (r > 1.) discard;
      vec3 col = vC.y < .25 ? vec3(1.,.7,.5) : vC.y < .8 ? vec3(1.,.95,.88) : vec3(.7,.8,1.); gl_FragColor = vec4(col*(exp(-r*5.)*1.2)*vC.x*uA, 1.); }`);
  return pointCloud(sGal, pos, { aC: [c, 2] }, m); })();
// our neighbourhood of the Orion Spur (within ~5,000 ly): fills the zoom between the nearest stars and the whole galaxy,
// with the Orion Nebula (1,344 ly, l = 209) and the Carina Nebula (7,500 ly is too far; use the closer Lagoon-like knots) as pink glows
const neighbourhood = (() => { const pos = [], c = [];
  for (let i = 0; i < 70000; i++) { const r = 5000 * Math.pow(rnd(), 0.75), a = rnd() * 6.283; pos.push(r * Math.cos(a) + gauss() * 200, r * Math.sin(a) * 0.8, gauss() * (120 + r * 0.04)); c.push(0.25 + 0.75 * Math.pow(rnd(), 3), rnd()); }
  const neb = [[1344, 209, -19], [1600, 263, 0], [2600, 15, -1], [4100, 287, -0.6], [3300, 80, 1.5], [2200, 130, 2]];
  for (const [d, l, b] of neb) for (let j = 0; j < 500; j++) { const x = d * Math.cos(l * RAD), y = d * Math.sin(l * RAD), z = d * Math.sin(b * RAD); pos.push(x + gauss() * 45, y + gauss() * 45, z + gauss() * 25); c.push(0.6 + 0.6 * rnd(), -1); }
  const m = pointsMat('neigh', `${LOGV[0]} attribute vec2 aC; varying vec2 vC; void main(){ vC = aC; vec4 mv = modelViewMatrix*vec4(position,1.); gl_Position = projectionMatrix*mv;
      gl_PointSize = clamp((aC.y < 0. ? 3.5 : 1.3 + 2.2*aC.x)*uH/1280., 1., 6.); ${LOGV[1]} }`,
    `${LOGF[0]} uniform float uA; varying vec2 vC; void main(){ ${LOGF[1]} vec2 q = gl_PointCoord*2.-1.; float r = dot(q,q); if (r > 1.) discard;
      vec3 col = vC.y < 0. ? vec3(1.,.42,.55) : vC.y < .3 ? vec3(1.,.72,.5) : vC.y < .75 ? vec3(1.,.95,.88) : vec3(.62,.75,1.); gl_FragColor = vec4(col*exp(-r*3.5)*vC.x*uA*(vC.y < 0. ? 0.5 : 1.), 1.); }`);
  return pointCloud(sGal, pos, { aC: [c, 2] }, m); })();
// the crowded heart of the galaxy (within ~400 ly of the centre): fills the dive toward Sagittarius A*
const coreCluster = (() => { const pos = [], c = [];
  for (let i = 0; i < 60000; i++) { const r = 400 * Math.pow(rnd(), 2.2) + 0.3, u = rnd() * 2 - 1, a = rnd() * 6.283, s = Math.sqrt(1 - u * u); pos.push(GC_LY + r * s * Math.cos(a), r * s * Math.sin(a), r * u * 0.6); c.push(0.25 + 0.75 * Math.pow(rnd(), 2.5), rnd()); }
  const m = pointsMat('gcore', `${LOGV[0]} attribute vec2 aC; varying vec2 vC; void main(){ vC = aC; vec4 mv = modelViewMatrix*vec4(position,1.); gl_Position = projectionMatrix*mv; gl_PointSize = clamp((1.2 + 2.6*aC.x)*uH/1280., 1., 5.); ${LOGV[1]} }`,
    `${LOGF[0]} uniform float uA; varying vec2 vC; void main(){ ${LOGF[1]} vec2 q = gl_PointCoord*2.-1.; float r = dot(q,q); if (r > 1.) discard; vec3 col = vC.y < .7 ? vec3(1.,.7,.45) : vec3(.75,.82,1.); gl_FragColor = vec4(col*exp(-r*4.)*vC.x*uA, 1.); }`);
  return pointCloud(sGal, pos, { aC: [c, 2] }, m); })();
const galSunMark = pointCloud(sGal, [0, 0, 0], {}, glowMat('galsun', [1, 0.85, 0.55])); galSunMark.renderOrder = 9;

// ================= CORE SCENE (AU, Sagittarius A* at origin) =================
// S-star orbits (Gillessen et al. 2017 elements; a in arcsec at 8.28 kpc -> AU), drawn as Kepler ribbons around the central mass
const ARC_AU = 8280 * 206264.806 / 206264.806 * 1;   // 1 arcsec at 8.28 kpc = 8,280 AU
const SSTARS = [ // name, a(arcsec), e, i, Omega, omega, P(yr), tp(yr, epoch offset), colour
  ['S2', 0.1255, 0.8839, 134.18, 226.94, 65.51, 16.0, 2018.38, [0.7, 0.8, 1.0]], ['S38', 0.1416, 0.8201, 171.1, 101.06, 17.99, 19.2, 2003.19, [0.75, 0.82, 1.0]],
  ['S55', 0.1078, 0.7209, 150.1, 325.5, 331.5, 12.8, 2009.31, [0.75, 0.85, 1.0]], ['S14', 0.2863, 0.9761, 100.59, 226.38, 334.59, 55.3, 2000.12, [0.8, 0.85, 1.0]],
  ['S1', 0.595, 0.556, 119.14, 342.04, 122.3, 166, 2001.8, [0.85, 0.88, 1.0]], ['S4', 0.357, 0.3905, 80.33, 258.84, 290.8, 77.0, 1957.4, [0.8, 0.86, 1.0]],
  ['S9', 0.2724, 0.644, 82.41, 156.6, 150.6, 51.3, 1976.7, [0.85, 0.9, 1.0]], ['S12', 0.2987, 0.8883, 33.56, 230.1, 317.9, 58.9, 1995.59, [0.8, 0.86, 1.0]],
  ['S13', 0.2641, 0.425, 24.7, 74.5, 245.2, 49.0, 2004.86, [0.85, 0.9, 1.0]], ['S8', 0.4047, 0.8031, 74.37, 315.43, 346.7, 92.9, 1983.64, [0.8, 0.86, 1.0]],
  ['S29', 0.428, 0.728, 105.8, 161.96, 346.1, 101, 2021.4, [0.85, 0.88, 1.0]]].map(([n, a, e, i, O, w, P, tp, c]) => ({ name: n, a: a * ARC_AU, e, i, node: O, peri: O + w, P, tp, c }));
SSTARS.forEach(s => { s.n = 2 * Math.PI / s.P; s.M0 = -s.n * (s.tp - 2000); });   // y measured in years from 2000.0
const coreRibbons = SSTARS.map((s, i) => { const kg = { ...s, a: s.a };
  const tau = [], side = [], idx = []; const nseg = 1500; for (let k = 0; k <= nseg; k++) { tau.push(k / nseg, k / nseg); side.push(-1, 1); if (k < nseg) { const a = 2 * k; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); } }
  const g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute(new Array(tau.length * 3).fill(0), 3)); g.setAttribute('aU', new T.Float32BufferAttribute(tau, 1)); g.setAttribute('aSide', new T.Float32BufferAttribute(side, 1)); g.setIndex(idx);
  const mat = new T.ShaderMaterial({ uniforms: { ...U, uNow: { value: 0 }, uSpan: { value: s.P }, uA: { value: 0 }, uWidth: { value: 3 } }, transparent: true, depthWrite: false, blending: T.AdditiveBlending, side: T.DoubleSide,
    vertexShader: `${LOGV[0]} uniform float uNow; uniform float uSpan; uniform float uWidth; attribute float aU; attribute float aSide; varying float vU; varying float vSide; ${keplerGLSL(kg, 'P')}
      void main(){ float y = uNow - uSpan*(1. - aU); float dt = uSpan/${nseg}.; vU = aU; vSide = aSide;
        vec4 p0 = projectionMatrix*viewMatrix*vec4(P(y),1.), p1 = projectionMatrix*viewMatrix*vec4(P(y+dt),1.), pm = projectionMatrix*viewMatrix*vec4(P(y-dt),1.);
        vec2 dir = (p1.xy/max(p1.w,1e-6) - pm.xy/max(pm.w,1e-6))*vec2(uAspect,1.); dir = length(dir) > 1e-9 ? normalize(dir) : vec2(1.,0.); vec2 n = vec2(-dir.y, dir.x)/vec2(uAspect,1.);
        gl_Position = p0 + vec4(n*aSide*uWidth*(0.3+0.7*aU)/uH*p0.w, 0., 0.); ${LOGV[1]} if (p0.w < 1e-6) gl_Position = vec4(0.,0.,-2.,1.); }`,
    fragmentShader: `${LOGF[0]} uniform float uA; varying float vU; varying float vSide; void main(){ ${LOGF[1]} float e = 1. - vSide*vSide; gl_FragColor = vec4(vec3(${s.c.join(',')})*e*(0.08 + 0.92*pow(vU, 3.))*uA, 1.); }` });
  mat.customProgramCacheKey = () => 'core' + i; const ms = new T.Mesh(g, mat); ms.frustumCulled = false; sCore.add(ms); return mat; });
const coreStars = SSTARS.map((s, i) => sprite(sCore, 1, 'cs' + i, `uniform float uA; varying vec2 vUv; void main(){ float r = length(vUv); float a = smoothstep(0.2, 0.12, r) + exp(-r*7.)*0.9 + pow(abs(cos(atan(vUv.y,vUv.x)*2.)), 60.)*exp(-r*3.)*0.4;
  gl_FragColor = vec4(vec3(${s.c.join(',')})*a*uA, 1.); }`));
// the nuclear star cluster around them (red giants and blue stars), and Sagittarius A* itself:
// a dark shadow with a glowing orange ring (the look of the Event Horizon Telescope image). Shown enlarged.
const nsc = (() => { const pos = [], c = []; for (let i = 0; i < 9000; i++) { const r = 400 + 30000 * Math.pow(rnd(), 1.8), u = rnd() * 2 - 1, a = rnd() * 6.283, s = Math.sqrt(1 - u * u);
    pos.push(r * s * Math.cos(a), r * s * Math.sin(a), r * u * 0.8); c.push(0.2 + 0.8 * Math.pow(rnd(), 2.5), rnd()); }
  const m = pointsMat('nsc', `${LOGV[0]} attribute vec2 aC; varying vec2 vC; void main(){ vC = aC; vec4 mv = modelViewMatrix*vec4(position,1.); gl_Position = projectionMatrix*mv; gl_PointSize = clamp((1.2 + 3.5*aC.x)*uH/1280., 1., 6.); ${LOGV[1]} }`,
    `${LOGF[0]} uniform float uA; varying vec2 vC; void main(){ ${LOGF[1]} vec2 q = gl_PointCoord*2.-1.; float r = dot(q,q); if (r > 1.) discard; vec3 col = vC.y < .55 ? vec3(1.,.66,.42) : vec3(.75,.82,1.); gl_FragColor = vec4(col*exp(-r*4.)*vC.x*uA, 1.); }`);
  return pointCloud(sCore, pos, { aC: [c, 2] }, m); })();
const bh = sprite(sCore, 1, 'bh', `uniform float uA; uniform float uTime; varying vec2 vUv; ${NOISE}
  void main(){ float r = length(vUv)*2.2; float ang = atan(vUv.y, vUv.x);
    float ring = exp(-pow((r - 1.0)/0.16, 2.)); float knots = 0.65 + 0.35*sin(ang*3. + 0.8) + 0.15*n3(vec3(cos(ang)*3., sin(ang)*3., uTime*0.3));
    float bright = 0.75 + 0.45*cos(ang - 1.9);                         // Doppler beaming: one side brighter
    float halo = exp(-max(r - 1., 0.)*2.5)*0.25;
    vec3 col = vec3(1., .55, .18)*ring*knots*bright*1.4 + vec3(1., .45, .12)*halo;
    float shadow = smoothstep(0.62, 0.78, r);
    gl_FragColor = vec4(col*shadow*uA, 1.); }`);
bh.material.blending = T.NormalBlending; bh.material.transparent = true;
bh.material.fragmentShader = bh.material.fragmentShader.replace('gl_FragColor = vec4(col*shadow*uA, 1.);', 'gl_FragColor = vec4(col*shadow, uA*max(1. - smoothstep(1.3, 2.2, r), 0.));');

function moonEcl(mb, t, y, big = 1, ph = mb.ph) { const hp = posEcl(mb.pi, y), a = 2 * Math.PI * (y * 365.25 + spinHours(t) / 24) / mb.per + ph;
  const eq = bodies[mb.pi].pole.clone(), u = V3(1, 0, 0).cross(eq).normalize(), v = eq.clone().cross(u).normalize();
  return hp.addScaledVector(u, mb.d * Math.cos(a) * big).addScaledVector(v, mb.d * Math.sin(a) * big); }
// ================= CAMERA CHOREOGRAPHY =================
// a pose: { pos, look, up } in the solar scene's units (AU, galactic axes, Sun at origin)
const P = (pos, look, up = ECL_N) => ({ pos, look, up: up.clone() });
const slerpDir = (a, b, s) => a.clone().lerp(b, s).normalize();
function blendPose(a, b, s, l0 = 0, l1 = 1) {           // log-distance blend around a moving look point
  const look = a.look.clone().lerp(b.look, smooth(l0, l1, s));
  const da = a.pos.distanceTo(a.look), db = b.pos.distanceTo(b.look);
  const dir = slerpDir(a.pos.clone().sub(a.look).normalize(), b.pos.clone().sub(b.look).normalize(), smooth(0.05, 0.95, s));
  return { pos: look.clone().addScaledVector(dir, Math.exp(mixv(Math.log(da), Math.log(db), s))), look, up: slerpDir(a.up, b.up, s) };
}
const gpos = (i, t) => posGal(i, yearAt(t));
// the view of planet i at its stop: on the sunward side, offset sideways so the terminator shows; slow drift
const VIEW = [ // [distance in radii, side angle deg, elevation deg, screen offset (radii, along up) ]
  [5.2, 72, 10], [5.0, 76, 12], [4.4, 62, 16], [4.8, 70, 12], [5.8, 66, 10], [7.6, 58, 30], [5.6, 70, 14], [5.2, 72, 10]];
function stopPose(i, t) {
  const p = gpos(i, t), R = PL[i].R, [k, side, el] = VIEW[i], drift = (t - stopTime(i)) * 5;
  const sunward = p.clone().negate().normalize(), n = ECL_N, tang = n.clone().cross(sunward).normalize();
  const a = (side + drift) * RAD, e = el * RAD;
  const dir = sunward.clone().multiplyScalar(Math.cos(a) * Math.cos(e)).addScaledVector(tang, Math.sin(a) * Math.cos(e)).addScaledVector(n, Math.sin(e)).normalize();
  const look = p.clone().addScaledVector(n, -R * 0.35);                 // planet sits a little above centre (labels go low)
  return P(p.clone().addScaledVector(dir, k * R), look);
}
function sunPose(t) { const d = R_SUN * 3.4, a = (40 + (t - 2.6) * 8) * RAD;
  const dir = V3(Math.cos(a), Math.sin(a), 0.25).normalize(); return P(dir.multiplyScalar(d), V3(0, 0, 0).addScaledVector(ECL_N, -R_SUN * 0.3)); }
function tourPose(t) {
  if (t < T_TOUR0) return sunPose(t);
  const k = Math.min(7, Math.floor((t - T_TOUR0) / T_STOP)), s = (t - stopTime(k)) / T_STOP;
  if (k === 7 || s < 0.55) return stopPose(k, t);
  return blendPose(stopPose(k, t), stopPose(k + 1, t), smooth(0.55, 1.0, s), 0.0, 0.45);
}
function tourEntry(t) { return blendPose(sunPose(t), stopPose(0, t), smooth(2.95, T_TOUR0, t), 0, 0.5); }
// wide view of the whole system, from above the ecliptic, galactic plane visible
const WIDE = t => { const look = V3(), az = (215 + (t - 11) * 4) * RAD, el = 38 * RAD, d = 128;
  const n = ECL_N, x = e2g(V3(Math.cos(az), Math.sin(az), 0));
  return P(x.multiplyScalar(d * Math.cos(el)).addScaledVector(n, d * Math.sin(el)), look); };
// riding with the Sun in the galaxy's frame: the camera sits ahead and to the side, looking back along the trails
const sideAx = VG.clone().cross(ECL_N).normalize();
const upAx = sideAx.clone().cross(VG).normalize();
const RIDE = (t, d) => { // d = how far ahead of the Sun the camera rides; the Sun sits high in frame, the trails run down to their vanishing point
  const look = VG.clone().multiplyScalar(-d);
  const pos = VG.clone().multiplyScalar(d).addScaledVector(sideAx, d * 0.14).addScaledVector(upAx, -d * 0.5);
  return P(pos, look, upAx.clone()); };
// myth: side chase of the vortex
const MYTH_CAM = t => { const s = t * 1.0; const sunNow = V3(0, 0, 0); // the myth world is drawn relative to its Sun
  const side = mythE1.clone().multiplyScalar(-1).addScaledVector(mythE2, 0.55).normalize();
  return P(side.multiplyScalar(13.5).addScaledVector(MYTH_AX, 1.2), MYTH_AX.clone().multiplyScalar(-3.6), MYTH_AX.clone().addScaledVector(side, 0).normalize()); };

// galaxy section: camera in light years (Sun at origin); converted for the solar scene by x LY_AU
const GAL_UP = V3(0, 0, 1);
function galPullPose(t) { // 19.8 -> 22.4: rise out of the disc and back until the whole galaxy fits, then drift while the centre is named
  const s = smooth(19.8, 22.4, t), drift = Math.max(0, t - 22.4);
  const dLy = Math.exp(mixv(Math.log(75 / LY_AU), Math.log(150000), Math.pow(s, 0.8)));
  const dirOut = slerpDir(sideAx.clone().multiplyScalar(0.8).addScaledVector(VG, 0.55).add(V3(0, 0, 0.35)).normalize(), V3(-0.42, -0.30, 0.86).normalize(), smooth(0.25, 0.8, s));
  const look = GC.clone().multiplyScalar(smooth(Math.log(3000), Math.log(110000), Math.log(dLy)));
  const q = new T.Quaternion().setFromAxisAngle(V3(0, 0, 1), drift * 0.05);
  return { pos: look.clone().addScaledVector(dirOut.applyQuaternion(q), dLy * (1 - 0.06 * drift)), look, up: slerpDir(V3(0, 0, 1), V3(1, 0, 0.2).normalize(), smooth(0.45, 0.95, s)) };
}
function galDivePose(t) { // 23.4 -> 24.6: dive to the Galactic Centre (ends ~0.03 ly away, handing over to the core scene)
  const a = galPullPose(23.4), s = smooth(23.4, 24.6, t);
  const dirA = a.pos.clone().sub(GC).normalize(), dirB = V3(-0.35, -0.55, 0.75).normalize();
  const d = Math.exp(mixv(Math.log(a.pos.distanceTo(GC)), Math.log(0.03), Math.pow(s, 0.85)));
  return { pos: GC.clone().addScaledVector(slerpDir(dirA, dirB, smooth(0, 0.7, s)), d), look: GC.clone(), up: slerpDir(a.up, V3(0, 0, 1), s) };
}
// core: orbit the S-star cluster (AU); hand-over distance 0.03 ly = 1,900 AU
const CORE_DIR = V3(-0.35, -0.55, 0.75).normalize();
function corePose(t) { const s = smooth(24.3, 27.6, t), d = Math.exp(mixv(Math.log(1900), Math.log(2600), s));
  const q = new T.Quaternion().setFromAxisAngle(V3(0, 0, 1), (t - 24.3) * 0.12); const dir = CORE_DIR.clone().applyQuaternion(q);
  return { pos: dir.multiplyScalar(d), look: V3(0, 0, 0), up: V3(0, 0, 1) }; }
// plunge home: 27.6 -> 29.0, out of the core, across the galaxy, down to the Sun, into the myth framing
function plungeGal(t) { // galaxy-ly coordinates: out of the core to the overview, then down onto the Sun
  const over = galPullPose(23.0);
  if (t < 28.0) { const s = smooth(27.6, 28.0, t); const d = Math.exp(mixv(Math.log(0.04), Math.log(over.pos.distanceTo(GC)), Math.pow(s, 0.6)));
    return { pos: GC.clone().addScaledVector(slerpDir(CORE_DIR, over.pos.clone().sub(GC).normalize(), smooth(0.3, 1, s)), d), look: GC.clone(), up: slerpDir(V3(0, 0, 1), over.up, s) }; }
  const s = smooth(28.0, 28.5, t), m0 = MYTH_CAM(0), dirE = m0.pos.clone().normalize();
  const d = Math.exp(mixv(Math.log(over.pos.length()), Math.log(m0.pos.length() / LY_AU), Math.pow(s, 0.7)));
  const dir = slerpDir(over.pos.clone().normalize(), dirE, smooth(0.2, 0.95, s));
  return { pos: dir.multiplyScalar(d), look: GC.clone().multiplyScalar(1 - smooth(0.0, 0.7, s)).add(m0.look.clone().multiplyScalar(smooth(0.6, 1, s) / LY_AU)), up: slerpDir(over.up, m0.up, s) };
}

// ================= OVERLAY =================
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
function ringMark(x, y, r, alpha) { if (alpha <= 0) return; ctx.save(); ctx.globalAlpha = alpha; ctx.strokeStyle = C_RED; ctx.lineWidth = 5; ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.stroke(); ctx.restore(); }
const projWith = (cam, v) => { const q = v.clone().project(cam); const p = v.clone().applyMatrix4(cam.matrixWorldInverse); return [(q.x + 1) / 2 * 1080, (1 - q.y) / 2 * 1920, p.z < 0]; };
const grain = [...Array(6)].map((_, k) => { const c = document.createElement('canvas'); c.width = 270; c.height = 480; const x = c.getContext('2d'); const im = x.createImageData(270, 480); let s = 99 + k * 7;
  for (let i = 0; i < im.data.length; i += 4) { s = (s * 16807) % 2147483647; const v = s % 255; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; } x.putImageData(im, 0, 0); return c; });
const fmtKm = km => km < 1e9 ? `${Math.round(km / 1e6).toLocaleString('en-US')} MILLION KM` : `${(km / 1e9).toFixed(1)} BILLION KM`;
function state(t) { const moving = t >= T_MOVE && t < 19.8; const y = yearAt(Math.min(t, 19.8)) - Y_MOVE; return { km: t >= T_MOVE ? Math.max(0, y) * F.year_s * F.sun_speed_kms : 0, moving }; }
window.stateAt = state;

function overlay(t, st) {
  // hook
  const hk = 1 - smooth(2.2, 2.5, t);
  text(typed("YOU'VE SEEN THIS.", 0.03, 0.5, t), 540, 290, 76, C_CREAM, { alpha: hk });
  chip(t >= 1.25 ? "IT'S WRONG." : '', 540, 1470, 60, hk * smooth(1.25, 1.31, t));
  // tour
  text('PLANET SIZES TRUE · DISTANCES TRUE · TIME SPED UP', 540, 176, 21, C_CREAM, { alpha: 0.55 * smooth(2.7, 3.1, t) * (1 - smooth(10.8, 11.2, t)), spacing: 1, stroke: false });
  text(typed('THE SUN', 2.65, 2.9, t), 540, 1380, 56, C_GOLD, { alpha: smooth(2.6, 2.7, t) * (1 - smooth(3.15, 3.35, t)), spacing: 4 });
  for (let i = 0; i < 8; i++) {
    const t0 = stopTime(i) - 0.12, t1 = stopTime(i) + T_STOP * 0.62;
    const a = smooth(t0, t0 + 0.12, t) * (1 - smooth(t1, t1 + 0.12, t)); if (a <= 0) continue;
    text(typed(PL[i].name, t0, t0 + 0.22, t), 540, 1360, 60, C_GOLD, { alpha: a, spacing: 6 });
    text(PL[i].fact, 540, 1438, 30, C_CREAM, { alpha: a * smooth(t0 + 0.18, t0 + 0.3, t), spacing: 1 });
  }
  // wide
  const wA = smooth(11.3, 11.5, t) * (1 - smooth(12.75, 12.95, t));
  text(typed('THE WHOLE SYSTEM IS TILTED', 11.3, 11.8, t), 540, 300, 44, C_CREAM, { alpha: wA });
  text(typed('60° TO THE GALAXY', 11.8, 12.2, t), 540, 364, 56, C_TEAL, { alpha: wA });
  const nA = smooth(12.85, 13.0, t) * (1 - smooth(13.9, 14.1, t));
  text(typed('NOW LET THE SUN MOVE.', 12.85, 13.35, t), 540, 320, 54, C_GOLD, { alpha: nA });
  // motion
  const mA = smooth(13.7, 13.9, t) * (1 - smooth(19.6, 19.8, t));
  if (mA > 0) { text('THE SUN HAS MOVED', 540, 1560, 26, C_CREAM, { alpha: mA * 0.9, spacing: 3, stroke: false }); text(fmtKm(Math.max(st.km, 1e6)), 540, 1612, 46, C_GOLD, { alpha: mA }); }
  const sA = smooth(13.75, 13.95, t) * (1 - smooth(14.9, 15.1, t));
  text(typed('230 KM/S', 13.75, 14.0, t), 540, 300, 70, C_GOLD, { alpha: sA }); text('AROUND THE GALAXY', 540, 370, 30, C_CREAM, { alpha: sA * smooth(13.95, 14.1, t), spacing: 3 });
  const eA = smooth(15.0, 15.15, t) * (1 - smooth(16.35, 16.5, t));
  text(typed("EARTH'S REAL PATH:", 15.0, 15.4, t), 540, 290, 46, C_CREAM, { alpha: eA }); text(typed('A STRETCHED WAVE.', 15.4, 15.8, t), 540, 356, 54, C_TEAL, { alpha: eA });
  const lA = smooth(16.45, 16.6, t) * (1 - smooth(17.75, 17.9, t));
  text(typed("PLANETS DON'T TRAIL BEHIND.", 16.45, 16.95, t), 540, 290, 42, C_CREAM, { alpha: lA }); text(typed('HALF THE TIME, THEY LEAD.', 16.95, 17.4, t), 540, 352, 46, C_GOLD, { alpha: lA });
  const oA = smooth(17.85, 18.0, t) * (1 - smooth(18.8, 18.95, t));
  text(typed("NEPTUNE'S PATH:", 17.85, 18.15, t), 540, 290, 46, C_CREAM, { alpha: oA }); text(typed('ALMOST STRAIGHT.', 18.15, 18.5, t), 540, 356, 54, '#8fb4ff', { alpha: oA });
  const vA = smooth(18.95, 19.05, t) * (1 - smooth(19.7, 19.85, t));
  text(typed('NOT A VORTEX.', 18.95, 19.25, t), 540, 330, 92, C_CREAM, { alpha: vA });
  // galaxy
  const gA = smooth(21.4, 21.6, t) * (1 - smooth(23.4, 23.6, t));
  text(typed('ALL OF IT ORBITS', 21.4, 21.8, t), 540, 290, 54, C_CREAM, { alpha: gA }); text(typed("THE GALAXY'S CENTRE", 21.8, 22.25, t), 540, 360, 50, C_GOLD, { alpha: gA });
  text('ONE LAP: 230 MILLION YEARS', 540, 1560, 32, C_CREAM, { alpha: smooth(22.3, 22.5, t) * (1 - smooth(23.4, 23.6, t)), spacing: 2 });
  if (t > 20.6 && t < 23.6) { const [x, y, f] = projWith(camG, V3()); const a = smooth(20.6, 20.9, t) * (1 - smooth(23.3, 23.5, t)); if (f) { ringMark(x, y, 22, a); text('THE SUN', x, y + 52, 26, C_CREAM, { alpha: a, spacing: 3 }); } }
  // core
  const cA = smooth(24.9, 25.05, t) * (1 - smooth(27.4, 27.6, t));
  text(typed('THESE STARS ORBIT', 24.9, 25.3, t), 540, 290, 50, C_CREAM, { alpha: cA * (1 - smooth(26.0, 26.15, t)) }); text(typed('SOMETHING INVISIBLE.', 25.3, 25.8, t), 540, 356, 50, C_GOLD, { alpha: cA * (1 - smooth(26.0, 26.15, t)) });
  if (t > 26.1 && t < 27.6) { const [x, y] = projWith(camC, V3()); const a = smooth(26.1, 26.25, t) * (1 - smooth(27.4, 27.6, t));
    ringMark(x, y, 70 + 8 * Math.sin(t * 6), a); chip(t >= 26.2 ? 'SAGITTARIUS A*' : '', 540, 300, 50, a); text(typed('A BLACK HOLE · 4 MILLION SUNS', 26.35, 26.8, t), 540, 380, 32, C_CREAM, { alpha: a, spacing: 1 });
    text('S2 · 16 YEARS PER LAP · UP TO 7,650 KM/S', 540, 1560, 26, C_CREAM, { alpha: a * smooth(26.6, 26.8, t) * 0.85, spacing: 1, stroke: false }); }
  const yA = smooth(27.6, 27.7, t) * (1 - smooth(28.55, 28.75, t));
  text(typed('NOW YOU KNOW.', 27.6, 27.9, t), 540, 330, 88, C_CREAM, { alpha: yA });
  text('THOUGHT EXPERIMENT · SIZES ENLARGED IN WIDE SHOTS', 540, 1700, 20, C_CREAM, { alpha: 0.45 * (smooth(11, 11.4, t) * (1 - smooth(28.5, 28.8, t))), spacing: 1, stroke: false });
  const fl = Math.max(t >= 1.25 ? 0.1 * Math.exp(-(t - 1.25) * 12) : 0, t >= 13.6 ? 0.08 * Math.exp(-(t - 13.6) * 10) : 0, t >= 26.1 ? 0.1 * Math.exp(-(t - 26.1) * 10) : 0);
  if (fl > 0.005) { ctx.save(); ctx.fillStyle = `rgba(255,240,220,${fl})`; ctx.fillRect(0, 0, 1080, 1920); ctx.restore(); }
}
function drawFilm() { ctx.drawImage(film, 0, 0, 1080, 1920); ctx.save();
  ctx.globalCompositeOperation = 'lighter'; ctx.filter = 'blur(10px) brightness(0.85)'; ctx.globalAlpha = 0.38; ctx.drawImage(film, 0, 0, 1080, 1920);
  ctx.filter = 'blur(40px)'; ctx.globalAlpha = 0.28; ctx.drawImage(film, 0, 0, 1080, 1920); ctx.restore(); }

// ================= FRAME =================
function setCam(cam, pose, near) { cam.position.copy(pose.pos); cam.up.copy(pose.up); cam.lookAt(pose.look); cam.near = near; cam.updateProjectionMatrix(); cam.updateMatrixWorld(); }
function solarPose(t) {
  if (t < 2.6) return null;
  if (t < T_TOUR0) return blendPose(sunPose(t), stopPose(0, T_TOUR0), smooth(2.95, T_TOUR0, t), 0, 0.5);
  if (t < 10.75) return tourPose(t);
  if (t < 12.4) return blendPose(stopPose(7, t), WIDE(t), Math.pow(smooth(10.75, 12.4, t), 0.8), 0, 0.6);
  if (t < 13.6) return WIDE(t);
  if (t < 15.0) return blendPose(WIDE(t), RIDE(t, 3.2), smooth(13.6, 15.0, t), 0, 0.8);
  if (t < 17.6) return RIDE(t, 3.2 - (t - 15) * 0.2);
  if (t < 19.8) return blendPose(RIDE(t, 2.68), RIDE(t, 60), smooth(17.6, 19.3, t), 0, 1);
  return null;
}
// stage the spins: turn signature features toward the camera at each stop (Great Red Spot, Tharsis and Valles Marineris, Great Dark Spot)
{ const FEAT = { 3: [-95, -5], 4: [25, -22.5], 7: [-40, -20], 2: [80, 20] };
  for (const [ks, [lon, lat]] of Object.entries(FEAT)) { const i = +ks, b = bodies[i], tt = stopTime(i) + 0.3, y = yearAt(tt), pose = stopPose(i, tt);
    const ph = (lon + 180) / 360 * 2 * Math.PI, th = (90 - lat) * RAD, loc = V3(-Math.cos(ph) * Math.sin(th), Math.cos(th), Math.sin(ph) * Math.sin(th));
    const toCam = pose.pos.clone().sub(posGal(i, y)).normalize(); let best = -2, bo = 0;
    for (let a = 0; a < 360; a++) { const ang = spinHours(tt) / PL[i].day_h * 2 * Math.PI + a * RAD;
      const w = loc.clone().applyAxisAngle(V3(0, 1, 0), ang).applyQuaternion(b.tiltQ).applyQuaternion(Q_EG); const d = w.dot(toCam.clone().lerp(posGal(i, y).clone().negate().normalize(), 0.35).normalize()); if (d > best) { best = d; bo = a * RAD; } }
    b.spin0 = bo; } }
// stage the moons: pick each moon's orbital phase so it sits in frame (in front of the sky, not behind its planet) during its planet's stop
{ const tmp = new T.PerspectiveCamera(FOV, 9 / 16, 1e-8, 1e3); const TARGET = { moon: [0.18, 0.62], io: [0.8, 0.3], europa: [0.16, 0.36], ganymede: [0.9, 0.62], callisto: [0.5, 0.12], titan: [0.86, 0.22], triton: [0.22, 0.25] };
  moonBodies.forEach((mb, k) => { const name = MOONS[k][1], tt = stopTime(mb.pi) + 0.35, y = yearAt(tt), pose = stopPose(mb.pi, tt); tmp.position.copy(pose.pos); tmp.up.copy(pose.up); tmp.lookAt(pose.look); tmp.updateMatrixWorld();
    let best = 1e9, bp = mb.ph; const [tx, ty] = TARGET[name];
    for (let a = 0; a < 360; a += 1) { const w = e2g(moonEcl(mb, tt, y, 1, a * RAD)); const q = w.clone().project(tmp); const behind = w.distanceTo(tmp.position) > posGal(mb.pi, y).distanceTo(tmp.position);
      if (q.z > 1 || behind && Math.hypot(q.x, q.y) < 0.5) continue; const sx = (q.x + 1) / 2, sy = (1 - q.y) / 2; const e = Math.hypot(sx - tx, (sy - ty) * 1.2); if (e < best) { best = e; bp = a * RAD; } }
    mb.ph = bp; }); }
window.renderAt = function (t, frame = Math.round(t * 30)) {
  t = ((t % DUR) + DUR) % DUR;
  const st = state(t), y = yearAt(t);
  U.uTime.value = t;
  renderer.setClearColor('#02040a', 1); renderer.clear();
  // ---- which scale? ----
  let pose = solarPose(t), galPose = null, corePoseV = null, myth = t < 2.6 || t >= 28.5;
  if (t >= 19.8 && t < 23.4) galPose = galPullPose(t);
  else if (t >= 23.4 && t < 24.6) galPose = galDivePose(t);
  if (t >= 24.3 && t < 27.9) corePoseV = corePose(t);
  if (t >= 27.6 && t < 28.5) galPose = plungeGal(t);
  if (galPose && !pose) pose = { pos: galPose.pos.clone().multiplyScalar(LY_AU), look: galPose.look.clone().multiplyScalar(LY_AU), up: galPose.up };
  if (myth) pose = MYTH_CAM(t);
  // ---- galaxy layer ----
  const camDistLy = pose ? pose.pos.length() / LY_AU : 0;
  const galA = galPose ? smooth(0.02, 3, galPose.pos.length()) * smooth(120, 1500, galPose.pos.distanceTo(GC)) * (t > 28.0 ? 1 - smooth(0.05, 0.002, galPose.pos.length()) : 1) : 0;
  if (galPose) {
    setCam(camG, galPose, Math.max(1e-4, galPose.pos.distanceTo(galPose.look) * 1e-4));
    galaxy.userData.stars.material.uniforms.uA.value = galA; galaxy.userData.dust.material.uniforms.uA.value = galA;
    galaxy.userData.glow.position.copy(GC); const gd = galPose.pos.distanceTo(GC); galaxy.userData.glow.scale.setScalar(Math.max(gd * 0.5, 30));
    galaxy.userData.glow.material.uniforms.uA.value = galA * 0.3 * smooth(3000, 30000, gd);
    sunOrbitMat.uniforms.uA.value = smooth(20.9, 21.5, t) * (1 - smooth(23.0, 23.5, t)) * (t < 27 ? 1 : 0);
    localStars.material.uniforms.uA.value = smooth(0.3, 3, galPose.pos.length()) * (1 - smooth(800, 6000, galPose.pos.length()));
    const dS = galPose.pos.length(), dC = galPose.pos.distanceTo(GC);
    neighbourhood.material.uniforms.uA.value = smooth(15, 300, dS) * (1 - smooth(9000, 40000, dS)) * 0.9;
    coreCluster.material.uniforms.uA.value = smooth(0.08, 2, dC) * (1 - smooth(1500, 6000, dC));
    galSunMark.material.uniforms.uA.value = (t < 23.6 ? smooth(20.4, 20.8, t) * (1 - smooth(23.2, 23.5, t)) : 0) + (t > 28.1 ? smooth(28.1, 28.4, t) : 0);
    galSunMark.material.uniforms.uPx.value = 18;
    renderer.render(sGal, camG); renderer.clearDepth();
  }
  // ---- core layer ----
  if (corePoseV) {
    const cA = smooth(24.3, 24.7, t) * (1 - smooth(27.55, 27.85, t));
    setCam(camC, corePoseV, 1);
    const yc = 2010 - 2000 + (t - 24.3) * 6.5;   // years since 2000: S2 whips through pericentre (2018.4) on screen
    coreRibbons.forEach((m, i) => { m.uniforms.uNow.value = yc; m.uniforms.uSpan.value = Math.min(SSTARS[i].P * 0.98, 4 + (t - 24.3) * 6.5); m.uniforms.uA.value = cA * 0.9; m.uniforms.uWidth.value = i === 0 ? 4.5 : 3; });
    coreStars.forEach((s, i) => { const p = kepler(SSTARS[i], yc); s.position.copy(p); const d = camC.position.distanceTo(p); s.scale.setScalar(d * 0.035 * (i === 0 ? 1.4 : 1)); s.material.uniforms.uA.value = cA; });
    nsc.material.uniforms.uA.value = cA * 0.8;
    const bA = smooth(26.1, 26.5, t) * cA; bh.scale.setScalar(camC.position.length() * 0.16 * (1 + 0.25 * smooth(26.1, 27.4, t))); bh.material.uniforms.uA.value = bA;
    renderer.render(sCore, camC); renderer.clearDepth();
  }
  // ---- solar layer ----
  if (pose) {
    const showSolar = myth ? 1 : 1 - smooth(1500, 60000, pose.pos.length());
    const nearSurf = Math.max(1e-8, Math.min(...bodies.map((b, i) => posGal(i, y).distanceTo(pose.pos) - b.R * 3), pose.pos.length() - R_SUN * 2) * 0.3);
    setCam(camS, pose, Math.max(1e-8, nearSurf));
    sky.position.copy(camS.position); sky.children[0].material.uniforms.uA.value = galPose ? 1 - galA : 1;
    // planets and moons
    bodies.forEach((b, i) => { const pe = posEcl(i, y); b.group.position.copy(pe);
      const turns = spinHours(t) / PL[i].day_h; b.spin.rotation.y = turns * 2 * Math.PI + (b.spin0 ?? i * 1.3);
      b.group.visible = !myth && showSolar > 0.01 && t < 27.5;
      const pg = e2g(pe), dist = pg.distanceTo(camS.position);
      // in wide shots, enlarge the planet so it stays visible (tagged on screen); never during the flyby
      const big = t > 10.9 ? Math.max(1, dist * mixv(0.0032, 0.006, smooth(13.6, 14.6, t)) * Math.pow(PL[i].R / PL[2].R, 0.35) / PL[i].R) : 1; b.group.scale.setScalar(big);
      glows[i].position.copy(pe); glows[i].material.uniforms.uA.value = (myth || t > 27.5 ? 0 : 1) * smooth(80, 600, dist / PL[i].R / big) * showSolar * (t > 10.5 ? 1 : 0.6);
      glows[i].material.uniforms.uPx.value = 10 + 2 * Math.sqrt(i); });
    for (const m of [...mats, ringMat, uRingMat, ...moonBodies.map(mb => mb.mat)]) { m.uniforms.uSunPos.value.set(0, 0, 0); }
    mats[5].uniforms.uCtr.value.copy(e2g(posEcl(5, y))); mats[5].uniforms.uRad.value = PL[5].R * bodies[5].group.scale.x;
    mats[5].uniforms.uRingN.value.copy(e2g(bodies[5].pole));
    ringU.uCtr.value.copy(mats[5].uniforms.uCtr.value); ringU.uRad.value = mats[5].uniforms.uRad.value;
    uRingMat.uniforms.uCtr.value.copy(e2g(posEcl(6, y))); uRingMat.uniforms.uRad.value = PL[6].R * bodies[6].group.scale.x;
    EU.uCloudShift.value = t * 0.003;
    moonBodies.forEach(mb => { const host = bodies[mb.pi], big = host.group.scale.x;
      mb.mesh.position.copy(moonEcl(mb, t, y, big)); mb.mesh.scale.setScalar(big); mb.mesh.visible = host.group.visible;
      const mg = moonGlows[moonBodies.indexOf(mb)]; mg.position.copy(mb.mesh.position); const st = stopTime(mb.pi); mg.material.uniforms.uPx.value = 7;
      mg.material.uniforms.uA.value = host.group.visible ? smooth(st - 0.45, st - 0.2, t) * (1 - smooth(st + 0.5, st + 0.7, t)) * 0.55 : 0; });
    // Sun
    const sd = camS.position.length(); sunMesh.visible = !myth; corona.visible = !myth && sd < 0.3;
    corona.material.uniforms.uA.value = 1;
    const sunBig = t > 10.9 ? Math.max(1, sd * 0.006 / R_SUN) : 1; sunMesh.scale.setScalar(sunBig); corona.scale.setScalar(sunBig);
    sunGlare.visible = !myth; sunGlare.scale.setScalar(sd * 0.045); sunGlare.material.uniforms.uA.value = smooth(0.05, 2, sd) * 0.6 * showSolar * (1 - 0.5 * smooth(10.9, 12, t) * (1 - smooth(13.4, 14, t)));
    // belts and orbits
    astBelt.material.uniforms.uY.value = kuiper.material.uniforms.uY.value = y;
    const wideA = smooth(10.9, 11.8, t) * (1 - smooth(14.0, 14.8, t));
    astBelt.material.uniforms.uA.value = (myth ? 0 : 1) * Math.max(wideA * 0.012, 0.5 * smooth(4.5, 5.6, t) * (1 - smooth(6.8, 7.2, t))) * 0.8;
    kuiper.material.uniforms.uA.value = (myth ? 0 : 1) * wideA * 0.6;
    orbitLines.forEach(m => m.uniforms.uA.value = (myth ? 0 : 1) * wideA * 0.35);
    gPlaneMat.uniforms.uA.value = (myth ? 0 : 1) * smooth(11.9, 12.4, t) * (1 - smooth(13.2, 13.8, t));
    // true paths (galaxy frame)
    const moveA = myth ? 0 : smooth(13.6, 13.9, t) * (1 - smooth(19.6, 20.6, t));
    trails.forEach((m, i) => { m.uniforms.uNow.value = y; m.uniforms.uStart.value = Math.max(Y_MOVE, y - (i < 4 ? 6 : 40)); m.uniforms.uA.value = moveA * (i === 2 ? 1.25 : 1);
      m.uniforms.uWidth.value = i === 2 ? 4.2 : 3.2; m.uniforms.uHead.value = 0.05; });
    sunTrailMat.uniforms.uLen.value = (y - Y_MOVE) * VSUN; sunTrailMat.uniforms.uA.value = moveA * 0.9;
    dustMat.uniforms.uS.value = y - Y_MOVE; dustMat.uniforms.uA.value = myth ? 0 : smooth(13.6, 14.2, t) * (1 - smooth(18.0, 19.0, t)) * 0.7;
    // myth
    const ms = t >= 28.5 ? (t - 29.0) : t;                   // the loop: myth time runs continuously through frame 0
    const mA = myth ? (t >= 28.5 ? smooth(28.5, 28.95, t) : (1 - smooth(1.9, 2.55, t))) : 0;
    mythTrails.forEach((m, i) => { m.uniforms.uNow.value = ms; m.uniforms.uStart.value = ms - 6; m.uniforms.uA.value = mA * (t < 1.6 || t >= 28.5 ? 1 : 1 - smooth(1.6, 2.3, t)); m.uniforms.uWidth.value = 3.2; m.uniforms.uHead.value = 0.15; });
    mythBeads.forEach((b, i) => { b.position.copy(mythPos(i, ms)).addScaledVector(MYTH_AX, -MYTH_V * ms); b.material.uniforms.uA.value = mA; b.visible = myth; });
    mythSun.position.set(0, 0, 0); mythSun.material.uniforms.uA.value = mA; mythSun.visible = myth; mythTail.uniforms.uA.value = mA;
    sSolar.visible = true;
    renderer.render(sSolar, camS);
  }
  drawFilm();
  ctx.save(); const v = ctx.createRadialGradient(540, 960, 420, 540, 960, 1180); v.addColorStop(0, 'rgba(2,4,10,0)'); v.addColorStop(1, 'rgba(2,4,10,0.65)'); ctx.fillStyle = v; ctx.fillRect(0, 0, 1080, 1920);
  ctx.globalAlpha = 0.04; ctx.globalCompositeOperation = 'overlay'; ctx.drawImage(grain[frame % 6], 0, 0, 1080, 1920); ctx.restore();
  overlay(t, st);
  return st;
};
window.captureFrame = (t, frame) => { window.renderAt(t, frame); return out.toDataURL('image/jpeg', 0.93).split(',')[1]; };
// fact check helpers for render.cjs
window.factCheck = () => { const beta = Math.asin(VE.z) / RAD; const tilt = Math.acos(ECL_N.z) / RAD;
  // fraction of Earth's orbit spent ahead of the Sun along the direction of motion
  let ahead = 0; for (let k = 0; k < 1000; k++) if (posEcl(2, k / 1000).dot(VE) > 0) ahead++;
  return { motionAboveEclipticDeg: beta, eclipticToGalacticPlaneDeg: tilt, earthAheadFraction: ahead / 1000, auPerYear: VSUN }; };
window.renderAt(0.05);
window.ready = true;
