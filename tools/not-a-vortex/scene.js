import * as T from 'three';
// Not a Vortex. Open on the viral "solar system is a vortex" picture and call it wrong, then one continuous move:
// the real solar system (today's planet positions, every planet orbiting and spinning) in front of the Milky Way,
// the Sun starts moving at its real 230 km/s and the orbits become long stretched waves, the camera pulls back
// until the whole spiral and Sagittarius A* at its centre are in view, and the Sun runs one full lap (loops).
// Two scenes drawn into one frame, both in galactic axes (x to the Galactic Centre, z to the north pole):
//   galaxy: 1 unit = 1 light year, the Sun starts at the origin, Galactic Centre at (+26,700, 0, 0)
//   solar:  an enlarged inset of the solar system at the Sun's position, on a compressed map (radius = 2.2 sqrt(a AU)),
//           drawn with a camera that is the galaxy camera's offset from the Sun scaled by K, so the two line up exactly
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
// y: years since J2000.0 (orbits). The orrery opens on today's positions (2026.8), then runs at RATE years per video second.
const RATE = [[0, 0.1], [2.6, 0.1], [5.6, 0.26], [12.6, 0.26], [15, 0.5], [22.6, 0.5], [24.4, 0.26], [26, 0.26]];
const rateAt = t => { for (let k = 1; k < RATE.length; k++) if (t <= RATE[k][0]) { const [t0, r0] = RATE[k - 1], [t1, r1] = RATE[k]; return mixv(r0, r1, smooth(t0, t1, t)); } return RATE.at(-1)[1]; };
const STEP = 1 / 600, NT = Math.round(DUR / STEP), YR = new Float64Array(NT + 1);
for (let i = 0; i < NT; i++) YR[i + 1] = YR[i] + rateAt((i + 0.5) * STEP) * STEP;
const rawYear = t => { const x = clamp(t / STEP, 0, NT), i = Math.min(NT - 1, Math.floor(x)); return mixv(YR[i], YR[i + 1], x - i); };
const Y_TODAY = 26.8, yearAt = t => Y_TODAY + rawYear(t) - rawYear(2.6);
const T_MOVE = 6.2, Y_MOVE = yearAt(T_MOVE);
const spinHours = t => t * 4;                                    // planet rotation runs at 4 hours per video second

// ---------- planets: J2000 Kepler elements (mean longitude L0 at J2000), on a compressed map ----------
// each orbit is scaled by k = 2.2 / sqrt(a), which keeps its shape and the Sun at its focus; sizes enlarged as R^0.5
const DS = 2.2;
PL.forEach(p => { p.n = 2 * Math.PI / p.P; p.M0 = (p.L0 - p.peri) * RAD; p.k = DS / Math.sqrt(p.a); p.R = 0.2 * Math.pow(p.R_km / 6371, 0.5); });
const VD = VSUN * DS;                                            // the Sun's speed on the map: Earth's wave keeps its true stretch (48.5 radii per orbit)
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

// ---------- the myth: the viral vortex (tight coils, orbital planes square to the motion, planets trailing in a cone) ----------
const MYTH = PL.map((p, i) => ({ r: 0.55 * Math.sqrt(p.a) + 0.15, w: 2 * Math.PI * 0.55 / Math.pow(p.P, 0.35), lag: 0.9 * Math.sqrt(p.a) + 0.2 * i, ph: i * 2.1 }));
const MYTHR = [0.2, 0.28, 0.3, 0.24, 0.55, 0.42, 0.36, 0.36];           // enlarged planet radii in the hook, so each shows its surface
const MYTH_V = 2.2, MYTH_AX = V3(0.25, 0.35, 1).normalize();     // myth-world units per video second; screen-up-ish axis
const mythE1 = V3(1, 0, 0).cross(MYTH_AX).normalize(), mythE2 = MYTH_AX.clone().cross(mythE1).normalize();
const mythPos = (i, s) => { const m = MYTH[i], a = m.w * s + m.ph; return mythE1.clone().multiplyScalar(m.r * Math.cos(a)).addScaledVector(mythE2, m.r * Math.sin(a)).addScaledVector(MYTH_AX, MYTH_V * s - m.lag); };

// ---------- scenes and cameras ----------
const sSolar = new T.Scene(), sGal = new T.Scene();
const camS = new T.PerspectiveCamera(FOV, 9 / 16, 1e-3, 1e9), camG = new T.PerspectiveCamera(FOV, 9 / 16, 1, 1e8);
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


// ================= SOLAR SCENE (map units, Sun at origin) =================
// sky for the myth: stars plus the Milky Way band, laid along the true galactic plane (so it crosses the ecliptic at 60 deg)
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

// tilt each planet: IAU north poles (RA, Dec, J2000) turned into ecliptic axes. Venus and Uranus spin backwards, so
// their spin axes are the IAU south poles (tilts of 177 and 98 deg)
const POLES = [[281.01, 61.41], [272.76, 67.16], [0, 90], [317.68, 52.89], [268.06, 64.50], [40.59, 83.54], [257.31, -15.18], [299.36, 43.46]];
const EPS = 23.4393 * RAD;
bodies.forEach((b, i) => { const [ra, de] = POLES[i].map(x => x * RAD), x = Math.cos(de) * Math.cos(ra), y = Math.cos(de) * Math.sin(ra), z = Math.sin(de);
  const pole = V3(x, y * Math.cos(EPS) + z * Math.sin(EPS), -y * Math.sin(EPS) + z * Math.cos(EPS)); if (i === 1 || i === 6) pole.negate();
  b.pole = pole; b.tiltQ = new T.Quaternion().setFromUnitVectors(V3(0, 1, 0), pole); });
ringMesh.quaternion.setFromUnitVectors(V3(0, 0, 1), V3(0, 1, 0)); uRing.quaternion.copy(ringMesh.quaternion);
// rings and atmospheres must tilt with the planet but not spin: put them under a tilt group
bodies.forEach(b => { const tg = new T.Group(); tg.quaternion.copy(b.tiltQ); b.group.add(tg); b.spin.removeFromParent(); tg.add(b.spin); b.tilt = tg; });
bodies[5].group.remove(ringMesh); bodies[5].tilt.add(ringMesh); bodies[6].group.remove(uRing); bodies[6].tilt.add(uRing);

// moons: the Moon, the Galilean moons, Titan, Triton. Sizes and distances on the enlarged map (distance in host radii), periods slowed
const MOONS = [ // planet, texture, radius km, period days, distance (host radii on the map), phase
  [2, 'moon', 1737, 27.32, 2.6, 2.5], [4, 'io', 1822, 1.769, 1.6, 0.6], [4, 'europa', 1561, 3.551, 2.0, 2.4], [4, 'ganymede', 2634, 7.155, 2.5, 4.1],
  [4, 'callisto', 2410, 16.69, 3.2, 5.5], [5, 'titan', 2575, 15.95, 3.1, 3.9], [7, 'triton', 1353, -5.877, 2.3, 1.0]];
const moonBodies = MOONS.map(([pi, n, rk, per, k, ph]) => { const m = planetMat('moon_' + n, T_[n], n === 'moon' ? { nrm: T_.moon_n, gain: 1.35 } : { gain: 1.3 });
  const mesh = new T.Mesh(new T.SphereGeometry(PL[pi].R * Math.pow(rk / PL[pi].R_km, 0.6), 48, 36), m); ecl.add(mesh); return { mesh, pi, d: k * PL[pi].R, per, ph, mat: m }; });
const posD = (i, y) => kepler(PL[i], y).multiplyScalar(PL[i].k);  // Sun-relative, ecliptic axes, map units
function moonPos(mb, t, y) { const hp = posD(mb.pi, y), a = 2 * Math.PI * t / (0.6 * Math.pow(Math.abs(mb.per), 0.4)) * Math.sign(mb.per) + mb.ph;
  const eq = bodies[mb.pi].pole, u = V3(1, 0, 0).cross(eq).normalize(), v = eq.clone().cross(u).normalize();
  return hp.addScaledVector(u, mb.d * Math.cos(a)).addScaledVector(v, mb.d * Math.sin(a)); }

// asteroid belt and Kuiper belt (points in the ecliptic, Keplerian shear at their true radii, drawn on the map)
function belt(n, r0, r1, thick, key, rgb, size) {
  const pos = [], a = []; for (let i = 0; i < n; i++) { const r = r0 + (r1 - r0) * Math.pow(rnd(), 0.8); pos.push(r, rnd() * 2 * Math.PI, gauss() * thick); a.push(rnd()); }
  const m = pointsMat(key, `${LOGV[0]} uniform float uY; attribute float aR; varying float vR; void main(){ vR = aR; float r = position.x, th = position.y + 6.2832*uY/pow(r, 1.5), rd = ${DS.toFixed(2)}*sqrt(r);
      vec4 mv = modelViewMatrix*vec4(rd*cos(th), rd*sin(th), position.z*rd, 1.); gl_Position = projectionMatrix*mv; gl_PointSize = clamp(${size.toFixed(1)}*uH/1280.*(0.6+0.8*aR), 1., 4.); ${LOGV[1]} }`,
    `${LOGF[0]} uniform float uA; varying float vR; void main(){ ${LOGF[1]} vec2 q = gl_PointCoord*2.-1.; float r = dot(q,q); if (r > 1.) discard; gl_FragColor = vec4(vec3(${rgb.join(',')})*(0.4+0.6*vR)*(1.-r)*uA, 1.); }`,
    { uY: { value: 0 } });
  return pointCloud(ecl, pos, { aR: [a, 1] }, m);
}
const astBelt = belt(9000, 2.1, 3.3, 0.04, 'ast', [0.85, 0.78, 0.66], 1.6), kuiper = belt(9000, 30, 50, 0.06, 'kuiper', [0.6, 0.7, 0.85], 1.5);

// glow markers so planets stay findable when they are sub-pixel (wide shots); sized in pixels
const glowMat = (key, rgb) => pointsMat(key, `${LOGV[0]} uniform float uPx; void main(){ gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); gl_PointSize = uPx*uH/1280.; ${LOGV[1]} }`,
  `${LOGF[0]} uniform float uA; void main(){ ${LOGF[1]} vec2 q = gl_PointCoord*2.-1.; float r = dot(q,q); if (r > 1.) discard; gl_FragColor = vec4(vec3(${rgb.join(',')})*(exp(-r*6.)*1.3 + 0.15*(1.-r))*uA, 1.); }`, { uPx: { value: 14 } });
const PCOL = [[0.8, 0.78, 0.74], [1, 0.9, 0.7], [0.5, 0.8, 1], [1, 0.6, 0.4], [1, 0.85, 0.65], [1, 0.9, 0.7], [0.65, 0.9, 0.95], [0.5, 0.7, 1]];
const moonGlows = MOONS.map((m, k) => { const pc = pointCloud(ecl, [0, 0, 0], {}, glowMat('mg' + k, [1, 0.96, 0.9])); pc.renderOrder = 8; return pc; });
const glows = PL.map((p, i) => { const pc = pointCloud(ecl, [0, 0, 0], {}, glowMat('pg' + i, PCOL[i])); pc.renderOrder = 8; return pc; });

// ---------- paths: screen-space ribbons evaluated in the vertex shader ----------
// P(y) is a GLSL function of the ribbon's parameter, drawn from uStart to uNow; the newest end is widest and brightest.
function ribbonMesh(parent, key, nseg, pfn, rgb, { base = 0.18, pw = 1.6, dash = 0 } = {}) {
  const tau = [], side = [], idx = [];
  for (let k = 0; k <= nseg; k++) { tau.push(k / nseg, k / nseg); side.push(-1, 1); if (k < nseg) { const a = 2 * k; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); } }
  const g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute(new Array(tau.length * 3).fill(0), 3));
  g.setAttribute('aU', new T.Float32BufferAttribute(tau, 1)); g.setAttribute('aSide', new T.Float32BufferAttribute(side, 1)); g.setIndex(idx);
  const mat = new T.ShaderMaterial({ uniforms: { ...U, uNow: { value: 0 }, uStart: { value: 0 }, uWidth: { value: 3 }, uA: { value: 0 }, uHead: { value: 0.1 } },
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
      void main(){ ${LOGF[1]} ${dash ? `if (fract(vU*${dash.toFixed(1)}) > 0.5) discard;` : ''} float edge = 1. - vSide*vSide; float head = exp(-vAge/uHead);
        float b = ${base.toFixed(3)} + ${(1 - base).toFixed(3)}*pow(vU, ${pw.toFixed(2)}) + 1.2*head;
        gl_FragColor = vec4(vec3(${rgb.join(',')})*b*edge*uA, 1.); }` });
  mat.customProgramCacheKey = () => 'rib_' + key;
  const mesh = new T.Mesh(g, mat); mesh.frustumCulled = false; mesh.renderOrder = 6; parent.add(mesh); return mat;
}
const f6 = x => x.toFixed(6), v3s = v => `vec3(${v.toArray().map(f6).join(',')})`;
const TRAIL_COL = [[0.85, 0.82, 0.78], [1, 0.85, 0.55], [0.35, 0.85, 0.95], [1, 0.5, 0.32], [1, 0.75, 0.45], [1, 0.88, 0.6], [0.55, 0.9, 0.95], [0.45, 0.65, 1]];
// true paths in the galaxy's frame, relative to the Sun now:  P(y) = V*(y - now) + k*orbit(y)
const trails = PL.map((p, i) => ribbonMesh(ecl, 'trail' + i, 2400, keplerGLSL(p, 'orb') + `vec3 P(float y){ return ${v3s(VE.clone().multiplyScalar(VD))}*(y - uNow) + ${f6(p.k)}*orb(y); }`, TRAIL_COL[i]));
// the orbits themselves (Sun at rest), brightest just behind each planet
const rings = PL.map((p, i) => ribbonMesh(ecl, 'ring' + i, 720, keplerGLSL(p, 'orb') + `vec3 P(float y){ return ${f6(p.k)}*orb(y); }`, TRAIL_COL[i], { base: 0.22, pw: 3 }));
// the myth: tight coils trailing in a cone, relative to the myth Sun now
const mythTrails = PL.map((p, i) => { const m = MYTH[i];
  return ribbonMesh(sSolar, 'myth' + i, 2400, `vec3 P(float s){ float a = ${m.w.toFixed(5)}*s + ${m.ph.toFixed(4)}; return ${v3s(mythE1)}*${m.r.toFixed(4)}*cos(a) + ${v3s(mythE2)}*${m.r.toFixed(4)}*sin(a)
         + ${v3s(MYTH_AX)}*(${MYTH_V.toFixed(4)}*(s - uNow) - ${m.lag.toFixed(4)}); }`, TRAIL_COL[i]); });
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
  { uS: { value: 0 }, uV: { value: VE.clone().multiplyScalar(VD) }, uBox: { value: 40 } });
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

// ================= GALAXY SCENE (light years; the Sun starts at the origin, the Galactic Centre at +26,700 ly on x) =================
const GC = V3(GC_LY, 0, 0);
// the disc turns with the Sun: the Sun sits close to the spiral pattern's corotation radius, so the arms keep pace with it
const galaxy = new T.Group(); galaxy.position.copy(GC); sGal.add(galaxy);
T_.plate = await tex('assets/galaxy_plate.jpg');
const plateMat = new T.ShaderMaterial({ uniforms: { uMap: { value: T_.plate }, uA: { value: 1 } }, transparent: true, depthWrite: false, blending: T.AdditiveBlending, side: T.DoubleSide,
  vertexShader: `${LOGV[0]} varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); ${LOGV[1]} }`,
  fragmentShader: `${LOGF[0]} uniform sampler2D uMap; uniform float uA; varying vec2 vUv; void main(){ ${LOGF[1]} vec3 c = texture2D(uMap, vUv).rgb; gl_FragColor = vec4(pow(c, vec3(1.25))*uA, 1.); }` });
plateMat.customProgramCacheKey = () => 'plate';
galaxy.add(new T.Mesh(new T.PlaneGeometry(110000, 110000), plateMat));
// stars drawn from the plate's own light (so they trace the arms, bar and bulge), with a thin disc and a thick bulge
const galStars = await (async () => {
  const img = await new Promise(res => { const im = new Image(); im.onload = () => res(im); im.src = 'assets/galaxy_plate.jpg'; });
  const S = 768, cv = document.createElement('canvas'); cv.width = cv.height = S; const cx = cv.getContext('2d'); cx.drawImage(img, 0, 0, S, S); const px = cx.getImageData(0, 0, S, S).data;
  const pos = [], c3 = [], c2 = [];
  for (let n = 0; n < 260000;) { const ix = Math.floor(rnd() * S), iy = Math.floor(rnd() * S), o = (iy * S + ix) * 4, r = px[o] / 255, g = px[o + 1] / 255, b = px[o + 2] / 255, l = (r + g + b) / 3;
    if (rnd() > Math.pow(l, 1.2) * 1.8) continue; n++;
    const x = ((ix + rnd()) / S - 0.5) * 110000, y = (0.5 - (iy + rnd()) / S) * 110000, R = Math.hypot(x, y);
    pos.push(x, y, gauss() * (220 + 1900 * Math.exp(-R / 3000)));
    const blue = R > 9000 && rnd() < 0.22, m = Math.max(r, g, b, 0.05);
    if (blue) c3.push(0.68, 0.8, 1); else c3.push(r / m, g / m, b / m);
    c2.push((0.35 + 0.65 * rnd()) * (0.5 + l), blue ? 1 : 0); }
  const m = pointsMat('galstars', `${LOGV[0]} attribute vec3 aCol; attribute vec2 aB; varying vec3 vC; varying float vB; void main(){ vC = aCol; vB = aB.x;
      vec4 mv = modelViewMatrix*vec4(position,1.); vB *= 0.25 + 0.75*smoothstep(2000., 14000., -mv.z); gl_Position = projectionMatrix*mv; gl_PointSize = clamp((1.3 + 1.1*aB.y + 0.6*aB.x)*uH/1280.*mix(1., 40000./max(-mv.z, 1.), 0.25), 1., 4.); ${LOGV[1]} }`,
    `${LOGF[0]} uniform float uA; varying vec3 vC; varying float vB; void main(){ ${LOGF[1]} vec2 q = gl_PointCoord*2.-1.; float r = dot(q,q); if (r > 1.) discard; gl_FragColor = vec4(vC*vB*exp(-r*3.)*0.75*uA, 1.); }`);
  return pointCloud(galaxy, pos, { aCol: [c3, 3], aB: [c2, 2] }, m); })();
// our part of the Orion Spur (within ~5,000 ly of the Sun), with a few pink star-forming nebulae: sharp detail behind the solar system
const neighbourhood = (() => { const pos = [], c = [];
  for (let i = 0; i < 50000; i++) { const r = 5000 * Math.pow(rnd(), 0.75), a = rnd() * 6.283; pos.push(-GC_LY + r * Math.cos(a) + gauss() * 200, r * Math.sin(a) * 0.8, gauss() * (120 + r * 0.04)); c.push(0.25 + 0.75 * Math.pow(rnd(), 3), rnd()); }
  const neb = [[1344, 209, -19], [1600, 263, 0], [2600, 15, -1], [4100, 287, -0.6], [3300, 80, 1.5], [2200, 130, 2]];
  for (const [d, l, b] of neb) for (let j = 0; j < 500; j++) pos.push(-GC_LY + d * Math.cos(l * RAD) + gauss() * 45, d * Math.sin(l * RAD) + gauss() * 45, d * Math.sin(b * RAD) + gauss() * 25), c.push(0.6 + 0.6 * rnd(), -1);
  const m = pointsMat('neigh', `${LOGV[0]} attribute vec2 aC; varying vec2 vC; void main(){ vC = aC; vec4 mv = modelViewMatrix*vec4(position,1.); gl_Position = projectionMatrix*mv;
      gl_PointSize = clamp((aC.y < 0. ? 2.2 : 1.1 + 1.6*aC.x)*uH/1280., 1., 4.); ${LOGV[1]} }`,
    `${LOGF[0]} uniform float uA; varying vec2 vC; void main(){ ${LOGF[1]} vec2 q = gl_PointCoord*2.-1.; float r = dot(q,q); if (r > 1.) discard;
      vec3 col = vC.y < 0. ? vec3(1.,.42,.55) : vC.y < .3 ? vec3(1.,.72,.5) : vC.y < .75 ? vec3(1.,.95,.88) : vec3(.62,.75,1.); gl_FragColor = vec4(col*exp(-r*3.5)*vC.x*uA*(vC.y < 0. ? 0.35 : 1.), 1.); }`);
  return pointCloud(galaxy, pos, { aC: [c, 2] }, m); })();
// distant stars all round (follows the camera)
const galSky = new T.Group(); sGal.add(galSky);
{ const pos = [], c = []; for (let i = 0; i < 9000; i++) { const u = rnd() * 2 - 1, a = rnd() * 6.283, s = Math.sqrt(1 - u * u); pos.push(4e6 * s * Math.cos(a), 4e6 * s * Math.sin(a), 4e6 * u); c.push(Math.pow(rnd(), 4), rnd()); }
  const m = pointsMat('galsky', `${LOGV[0]} attribute vec2 aC; varying vec2 vC; void main(){ vC = aC; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); gl_PointSize = (1.1 + 2.4*aC.x)*uH/1280.; ${LOGV[1]} }`,
    `${LOGF[0]} uniform float uA; varying vec2 vC; void main(){ ${LOGF[1]} vec2 q = gl_PointCoord*2.-1.; float r = dot(q,q); if (r > 1.) discard; vec3 col = vC.y < .2 ? vec3(.62,.72,1.) : vC.y < .7 ? vec3(1.,.96,.9) : vec3(1.,.8,.6);
      gl_FragColor = vec4(col*(.2 + .9*vC.x)*(1.-r)*uA, 1.); }`);
  pointCloud(galSky, pos, { aC: [c, 2] }, m); }
// the bulge's soft glow (gives the flat plate some volume)
const bulge = sprite(sGal, 1, 'bulge', `uniform float uA; varying vec2 vUv; void main(){ float r = length(vUv); gl_FragColor = vec4(vec3(1.,.8,.55)*(exp(-r*9.)*0.9 + exp(-r*3.5)*0.18)*uA, 1.); }`);
bulge.position.copy(GC);
// Sagittarius A*: a dark shadow inside a glowing orange ring, the look of the Event Horizon Telescope image. Shown hugely enlarged.
const bh = sprite(sGal, 1, 'bh', `uniform float uA; uniform float uTime; varying vec2 vUv; ${NOISE}
  void main(){ float r = length(vUv)*2.2; float ang = atan(vUv.y, vUv.x);
    float ring = exp(-pow((r - 1.0)/0.16, 2.)); float knots = 0.65 + 0.35*sin(ang*3. + 0.8 + uTime*0.4) + 0.15*n3(vec3(cos(ang)*3., sin(ang)*3., uTime*0.3));
    float bright = 0.75 + 0.45*cos(ang - 1.9);                         // Doppler beaming: one side brighter
    float halo = exp(-max(r - 1., 0.)*2.5)*0.25;
    vec3 col = vec3(1., .55, .18)*ring*knots*bright*1.5 + vec3(1., .45, .12)*halo;
    float shadow = smoothstep(0.62, 0.78, r);
    gl_FragColor = vec4(col*shadow, uA*max(1. - smoothstep(1.3, 2.2, r), 0.)); }`);
bh.material.blending = T.NormalBlending; bh.renderOrder = 10; bh.position.copy(GC);
// the Sun's orbit around the centre: the lap so far (gold) and the whole circle (dashed); the Sun itself as a gold point
const orbitP = `vec3 P(float y){ float a = 3.14159265 - y; return vec3(${GC_LY.toFixed(1)} + ${GC_LY.toFixed(1)}*cos(a), ${GC_LY.toFixed(1)}*sin(a), 0.); }`;
const lapTrail = ribbonMesh(sGal, 'lap', 1440, orbitP, [1, 0.8, 0.45], { base: 0.25, pw: 1.5 });
const lapCircle = ribbonMesh(sGal, 'lapc', 1440, orbitP, [0.98, 0.9, 0.72], { base: 1, pw: 1, dash: 120 });
// a soft dark patch behind the solar system so its planets stand out against the bright arms
const sunVeil = sprite(sGal, 1, 'veil', `uniform float uA; varying vec2 vUv; void main(){ float r = length(vUv); gl_FragColor = vec4(vec3(0.004,0.006,0.012), uA*(1.-smoothstep(0.3, 0.75, r))*0.85); }`);
sunVeil.material.blending = T.NormalBlending; sunVeil.renderOrder = 7;
const galSun = pointCloud(sGal, [0, 0, 0], {}, glowMat('galsun', [1, 0.85, 0.55])); galSun.renderOrder = 9;

// ================= CAMERA =================
// One move from 2.6 s to the end, built in galaxy light years. The solar inset's camera is the galaxy camera's offset
// from the Sun times K = dS / dG (same orientation), with dS following its own curve: early on the solar system fills
// the frame in front of the galaxy, later it shrinks to the gold point that runs the lap.
const P = (pos, look, up) => ({ pos, look, up: up.clone() });
const slerpDir = (a, b, s) => a.clone().lerp(b, s).normalize();
function blendPose(a, b, s, l0 = 0, l1 = 1) {           // log-distance blend around a moving look point
  const look = a.look.clone().lerp(b.look, smooth(l0, l1, s));
  const da = a.pos.distanceTo(a.look), db = b.pos.distanceTo(b.look);
  const dir = slerpDir(a.pos.clone().sub(a.look).normalize(), b.pos.clone().sub(b.look).normalize(), smooth(0.05, 0.95, s));
  return { pos: look.clone().addScaledVector(dir, Math.exp(mixv(Math.log(da), Math.log(db), s))), look, up: slerpDir(a.up, b.up, s) };
}
function curve(K) { // cubic Hermite through (t, value) keys in log space
  const L = K.map(([t, v]) => [t, Math.log(v)]);
  const m = L.map((k, i) => i === 0 || i === L.length - 1 ? 0 : ((L[i + 1][1] - L[i][1]) / (L[i + 1][0] - L[i][0]) + (L[i][1] - L[i - 1][1]) / (L[i][0] - L[i - 1][0])) / 2);
  return t => { if (t <= L[0][0]) return Math.exp(L[0][1]);
    for (let i = 1; i < L.length; i++) if (t <= L[i][0]) { const h = L[i][0] - L[i - 1][0], s = (t - L[i - 1][0]) / h, s2 = s * s, s3 = s2 * s;
      return Math.exp((2 * s3 - 3 * s2 + 1) * L[i - 1][1] + (s3 - 2 * s2 + s) * h * m[i - 1] + (-2 * s3 + 3 * s2) * L[i][1] + (s3 - s2) * h * m[i]); }
    return Math.exp(L.at(-1)[1]); };
}
const dSAt = curve([[2.6, 13], [6.2, 19], [9.0, 25], [12.6, 60], [14.6, 100], [16.6, 150], [24.4, 150], [25.95, 30]]);
// orrery: 55 deg above the ecliptic, turned so the Sun's in-plane motion runs UP the frame (the same way it runs in the
// moving shots, so there is no sideways swing); slow orbit about the ecliptic pole that settles to zero when the Sun sets off
const UP_IN = VG.clone().addScaledVector(ECL_N, -VG.dot(ECL_N)).normalize();
function orrery(t, free = false) { const ang = free ? (t - 6.2) * 0.05 : (Math.min(t, 6.2) - 6.2) * 0.045;
  const up = UP_IN.clone().applyQuaternion(new T.Quaternion().setFromAxisAngle(ECL_N, ang)), h = ECL_N.clone().cross(up).normalize();
  return { dir: ECL_N.clone().multiplyScalar(Math.cos(35 * RAD)).addScaledVector(h, Math.sin(35 * RAD)).normalize(), up }; }
// the inset's own view of the solar system once the galaxy takes over: the orrery again, orbiting slowly, easing to the opening view for the loop
function orreryLate(t) { if (t < 24.4) return orrery(t, true); const a = orrery(24.4, true), b = orrery(3), s = Math.pow(smooth(24.4, 25.95, t), 1.4);
  return { dir: a.dir.clone().lerp(b.dir, s).normalize(), up: a.up.clone().lerp(b.up, s).normalize() }; }
// moving: ahead of the Sun and off to the far side from the centre, 50 deg from its line of motion, looking back along the paths
// (the Sun near the top of the frame, its path running down and away)
const SIDE = (() => { const d = V3(-Math.cos(18 * RAD), 0, Math.sin(18 * RAD)); return d.addScaledVector(VG, -d.dot(VG)).normalize(); })();
const RIDE_DIR = SIDE.clone().multiplyScalar(Math.sin(50 * RAD)).addScaledVector(VG, Math.cos(50 * RAD)), RIDE_UP = VG.clone().multiplyScalar(Math.sin(50 * RAD)).addScaledVector(SIDE, -Math.cos(50 * RAD));
function poseA(t) { const o = orrery(t), s = smooth(6.0, 10.4, t), dS = dSAt(t), dG = 22000;
  const dir = slerpDir(o.dir, RIDE_DIR, s), up = slerpDir(o.up, RIDE_UP, smooth(6.0, 8.2, t));
  const lookS = o.up.clone().multiplyScalar(1.3 * (1 - s)).addScaledVector(VG, -0.3 * dS * s);     // solar units
  return P(dir.multiplyScalar(dG), lookS.multiplyScalar(dG / dS), up); }
// the whole galaxy: from 34 deg above the disc on the far side from the centre, the disc's long axis up the frame; slow orbit
function poseB(t) { const q = new T.Quaternion().setFromAxisAngle(V3(0, 0, 1), 0.03 * (t - 12.6));
  return P(GC.clone().addScaledVector(V3(-Math.cos(34 * RAD), 0, Math.sin(34 * RAD)).applyQuaternion(q), 165000), GC.clone(), V3(0, 1, 0).applyQuaternion(q)); }
// home: down onto the Sun (back at its start after the lap), ending on the orrery's opening view
function poseC(t) { const o = orrery(3); return P(o.dir.multiplyScalar(4000), V3(), o.up); }
function galPoseAt(t) {
  if (t < 12.6) return poseA(t);
  if (t < 17.6) return blendPose(poseA(t), poseB(t), smooth(12.6, 17.6, t), 0.05, 0.85);
  if (t < 24.4) return poseB(t);
  return blendPose(poseB(t), poseC(t), Math.pow(smooth(24.4, 25.95, t), 1.4), 0, 0.6);
}
// the lap: one full orbit of the Galactic Centre between 17.6 and 22.6 s (eased), 230 million years
const T_LAP0 = 17.6, T_LAP1 = 22.6;
const lapPhase = t => { const s = clamp((t - T_LAP0) / (T_LAP1 - T_LAP0)); return 2 * Math.PI * (s - Math.sin(2 * Math.PI * s) / (2 * Math.PI)); };
const sunGal = t => { const a = Math.PI - lapPhase(t); return V3(GC_LY + GC_LY * Math.cos(a), GC_LY * Math.sin(a), 0); };
// the myth: side chase of the vortex
const MYTH_CAM = t => { const side = mythE1.clone().multiplyScalar(-1).addScaledVector(mythE2, 0.55).normalize();
  return P(side.multiplyScalar(13.5).addScaledVector(MYTH_AX, 1.2), MYTH_AX.clone().multiplyScalar(-3.6), MYTH_AX.clone()); };

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
function state(t) { return { myr: F.galactic_year_myr * lapPhase(t) / (2 * Math.PI) }; }
window.stateAt = state;

function overlay(t, st) {
  // hook
  const hk = 1 - smooth(2.2, 2.5, t);
  text(typed("YOU'VE SEEN THIS.", 0.03, 0.5, t), 540, 290, 76, C_CREAM, { alpha: hk });
  chip(t >= 1.25 ? "IT'S WRONG." : '', 540, 1470, 60, hk * smooth(1.25, 1.31, t));
  // the real one
  const rA = smooth(2.8, 2.95, t) * (1 - smooth(5.6, 5.85, t));
  text(typed("HERE'S THE REAL ONE.", 2.8, 3.3, t), 540, 290, 62, C_GOLD, { alpha: rA });
  const lA = smooth(3.0, 3.4, t) * (1 - smooth(6.6, 7.2, t));
  if (lA > 0) PL.forEach((p, i) => { const [x, y, f] = projWith(camS, e2g(posD(i, yearAt(t)))); if (!f || x < 30 || x > 1050 || y < 420 || y > 1650) return;
    const r = PL[i].R / camS.position.length() * 1920 / (2 * Math.tan(FOV * RAD / 2)) * (i === 5 ? 2.4 : 1);
    text(p.name, x + r + 14, y, 22, C_CREAM, { align: 'left', alpha: lA * 0.85, spacing: 2 }); });
  // moving
  const mA = smooth(6.0, 6.15, t) * (1 - smooth(8.3, 8.5, t));
  text(typed('THE SUN IS MOVING', 6.0, 6.4, t), 540, 280, 50, C_CREAM, { alpha: mA }); text(typed('230 KM/S', 6.4, 6.7, t), 540, 360, 84, C_GOLD, { alpha: mA });
  const wA = smooth(8.5, 8.65, t) * (1 - smooth(10.45, 10.6, t));
  text(typed('THE PLANETS FOLLOW', 8.5, 8.9, t), 540, 280, 50, C_CREAM, { alpha: wA }); text(typed('IN STRETCHED WAVES', 8.9, 9.3, t), 540, 350, 54, C_TEAL, { alpha: wA });
  const aA = smooth(10.6, 10.75, t) * (1 - smooth(12.45, 12.6, t));
  text(typed('HALF THE TIME', 10.6, 10.9, t), 540, 280, 50, C_CREAM, { alpha: aA }); text(typed("THEY'RE AHEAD OF THE SUN", 10.9, 11.4, t), 540, 350, 50, C_GOLD, { alpha: aA });
  const vA = smooth(12.7, 12.8, t) * (1 - smooth(14.1, 14.3, t));
  text(typed('NOT A VORTEX.', 12.7, 13.0, t), 540, 320, 92, C_CREAM, { alpha: vA });
  // the galaxy and its centre
  const bA = smooth(14.8, 15.0, t) * (1 - smooth(17.3, 17.5, t));
  text(typed('ALL OF IT ORBITS', 14.8, 15.2, t), 540, 280, 54, C_CREAM, { alpha: bA });
  if (t > 15.0 && t < 17.6) { const [x, y, f] = projWith(camG, GC); const a = smooth(15.2, 15.35, t) * (1 - smooth(17.3, 17.5, t)) * (f ? 1 : 0);
    chip(t >= 15.25 ? 'SAGITTARIUS A*' : '', 540, 370, 50, a); text(typed('A BLACK HOLE · 4 MILLION SUNS', 15.55, 16.0, t), 540, 446, 30, C_CREAM, { alpha: a, spacing: 1 }); }
  // the Sun's place, and the lap
  if (t > 14.9 && t < 24.4) { const [x, y, f] = projWith(camG, sunGal(t)); const a = smooth(14.9, 15.3, t) * (1 - smooth(24.1, 24.4, t));
    const rr = 12.8 * 1920 / (2 * Math.tan(FOV * RAD / 2) * dSAt(t)) + 16;      // a ring round the whole solar system
    if (f) { ringMark(x, y, rr, a * 0.55); text('THE SUN + 8 PLANETS', x, y + rr + 36, 24, C_CREAM, { alpha: a * (y < 1280 ? 1 : 0), spacing: 3 }); } }
  const pA = smooth(17.6, 17.8, t) * (1 - smooth(23.6, 23.8, t));
  text(typed('ONE LAP AROUND THE GALAXY', 17.6, 18.1, t), 540, 280, 44, C_CREAM, { alpha: pA });
  if (pA > 0) { text(`${Math.round(st.myr)}`, 540, 1520, 120, C_GOLD, { alpha: pA }); text('MILLION YEARS', 540, 1610, 36, C_CREAM, { alpha: pA, spacing: 4 }); }
  // home
  const yA = smooth(23.8, 23.95, t) * (1 - smooth(25.1, 25.3, t));
  text(typed('NOW YOU KNOW.', 23.8, 24.1, t), 540, 320, 88, C_CREAM, { alpha: yA });
  text('DISTANCES COMPRESSED · SIZES ENLARGED · NOT TO SCALE', 540, 1760, 20, C_CREAM, { alpha: 0.45 * smooth(2.8, 3.2, t) * (1 - smooth(25.0, 25.3, t)), spacing: 1, stroke: false });
  // flashes: the hit on IT'S WRONG, the Sun setting off, the black hole; and the loop point (white at the seam)
  const fl = Math.max(t >= 1.25 ? 0.1 * Math.exp(-(t - 1.25) * 12) : 0, t >= 2.6 ? 0.25 * Math.exp(-(t - 2.6) * 8) : 0, t >= T_MOVE ? 0.08 * Math.exp(-(t - T_MOVE) * 10) : 0,
    t >= 15.25 ? 0.07 * Math.exp(-(t - 15.25) * 10) : 0, Math.pow(smooth(25.55, 26.0, t), 2) * 0.85, 0.85 * Math.exp(-t * 14));
  if (fl > 0.005) { ctx.save(); ctx.fillStyle = `rgba(255,240,220,${fl})`; ctx.fillRect(0, 0, 1080, 1920); ctx.restore(); }
}
function drawFilm() { ctx.drawImage(film, 0, 0, 1080, 1920); ctx.save();
  ctx.globalCompositeOperation = 'lighter'; ctx.filter = 'blur(10px) brightness(0.85)'; ctx.globalAlpha = 0.38; ctx.drawImage(film, 0, 0, 1080, 1920);
  ctx.filter = 'blur(40px)'; ctx.globalAlpha = 0.28; ctx.drawImage(film, 0, 0, 1080, 1920); ctx.restore(); }


// ================= FRAME =================
const R_SUN_D = 0.6;                                            // the Sun's radius on the map
function setCam(cam, pose, near) { cam.position.copy(pose.pos); cam.up.copy(pose.up); cam.lookAt(pose.look); cam.near = near; cam.updateProjectionMatrix(); cam.updateMatrixWorld(); }
window.renderAt = function (t, frame = Math.round(t * 30)) {
  t = ((t % DUR) + DUR) % DUR;
  const st = state(t), y = yearAt(t), myth = t < 2.6;
  U.uTime.value = t;
  renderer.setClearColor('#02040a', 1); renderer.clear();
  let poseS, sunNdc = null;
  // ---- galaxy layer ----
  if (!myth) {
    const g = galPoseAt(t), sun = sunGal(t);
    setCam(camG, g, Math.max(1e-3, g.pos.distanceTo(g.look) * 1e-4));
    galSky.position.copy(camG.position);
    const phi = lapPhase(t), reveal = smooth(12.6, 16, t); galaxy.rotation.z = -phi;
    const home = 1 - 0.7 * smooth(24.9, 25.45, t);
    plateMat.uniforms.uA.value = (0.55 + 0.45 * reveal) * home; galStars.material.uniforms.uA.value = (0.6 + 0.4 * reveal) * home;
    neighbourhood.material.uniforms.uA.value = 0.22 * (1 - smooth(14, 18, t)) + 0.2 * smooth(24.8, 25.7, t);
    bulge.scale.setScalar(26000); bulge.material.uniforms.uA.value = 0.35;
    bh.scale.setScalar(6000); bh.material.uniforms.uA.value = 1;
    lapTrail.uniforms.uStart.value = 0; lapTrail.uniforms.uNow.value = Math.max(phi, 1e-4); lapTrail.uniforms.uWidth.value = 5; lapTrail.uniforms.uHead.value = 0.04;
    lapTrail.uniforms.uA.value = (phi > 1e-3 ? 1 : 0) * (1 - smooth(24.4, 25.0, t));
    lapCircle.uniforms.uStart.value = 0; lapCircle.uniforms.uNow.value = 2 * Math.PI; lapCircle.uniforms.uWidth.value = 2.4; lapCircle.uniforms.uHead.value = 1e-6;
    lapCircle.uniforms.uA.value = 0.4 * smooth(16.4, 17.4, t) * (1 - smooth(24.2, 24.8, t));
    galSun.position.copy(sun); galSun.material.uniforms.uA.value = smooth(13.8, 14.6, t) * (1 - smooth(15.0, 16.0, t)); galSun.material.uniforms.uPx.value = 22;
    // the inset's camera: the galaxy camera's offset from the Sun times K, so the two line up exactly; once the galaxy takes over it
    // eases into its own orrery view, with the Sun kept on the screen point where the galaxy shows it
    const rel = g.pos.clone().sub(sun), dSv = dSAt(t), K = dSv / rel.length(), w = smooth(12.6, 17.0, t), o2 = orreryLate(t);
    const look = g.look.clone().sub(sun).multiplyScalar(K * (1 - w));
    poseS = P(slerpDir(rel, o2.dir, w).multiplyScalar(dSv), look, slerpDir(g.up, o2.up, w));
    sunNdc = sun.clone().project(camG);
    sunVeil.position.copy(sun); sunVeil.scale.setScalar(2 * 13 * 1.9 / K); sunVeil.material.uniforms.uA.value = smooth(15.5, 17.2, t) * (1 - smooth(24.2, 24.9, t));
    renderer.render(sGal, camG); renderer.clearDepth();
  } else poseS = MYTH_CAM(t);
  // ---- solar layer (an enlarged inset at the Sun) ----
  const dS = poseS.pos.length(), showSolar = myth ? 0 : 1 - smooth(600, 5000, dS);
  setCam(camS, poseS, myth ? 0.01 : Math.max(1e-3, dS * 2e-3));
  if (sunNdc) { const so = V3().project(camS); camS.projectionMatrix.elements[8] += so.x - sunNdc.x; camS.projectionMatrix.elements[9] += so.y - sunNdc.y; }
  sky.visible = myth; sky.position.copy(camS.position);
  const lapW = smooth(15.5, 17.2, t) * (1 - smooth(24.2, 24.9, t));
  const mythW = PL.map((p, i) => mythPos(i, t).addScaledVector(MYTH_AX, -MYTH_V * t)), mScale = PL.map((p, i) => myth ? MYTHR[i] / p.R : 1);
  bodies.forEach((b, i) => { const pe = myth ? g2e(mythW[i]) : posD(i, y); b.group.position.copy(pe); b.group.scale.setScalar(mScale[i]);
    b.spin.rotation.y = (myth ? t * 30 : spinHours(t)) / Math.abs(PL[i].day_h) * 2 * Math.PI * Math.sign(PL[i].day_h) + i * 1.3; b.group.visible = myth || showSolar > 0.01;
    glows[i].position.copy(pe); glows[i].material.uniforms.uA.value = showSolar * smooth(30, 160, dS) * 0.9; glows[i].material.uniforms.uPx.value = 9 + 1.5 * Math.sqrt(i) + 8 * lapW; });
  for (const m of [...mats, ringMat, uRingMat, ...moonBodies.map(mb => mb.mat)]) m.uniforms.uSunPos.value.set(0, 0, 0);
  mats[5].uniforms.uCtr.value.copy(myth ? mythW[5] : e2g(posD(5, y))); mats[5].uniforms.uRad.value = PL[5].R * mScale[5]; mats[5].uniforms.uRingN.value.copy(e2g(bodies[5].pole));
  ringU.uCtr.value.copy(mats[5].uniforms.uCtr.value); ringU.uRad.value = PL[5].R * mScale[5];
  uRingMat.uniforms.uCtr.value.copy(myth ? mythW[6] : e2g(posD(6, y))); uRingMat.uniforms.uRad.value = PL[6].R * mScale[6];
  EU.uCloudShift.value = t * 0.003;
  moonBodies.forEach((mb, k) => { mb.mesh.position.copy(moonPos(mb, t, y)); mb.mesh.visible = showSolar > 0.01 && dS < 100; moonGlows[k].material.uniforms.uA.value = 0; });
  // the Sun
  const sunS = (myth ? 0.5 : R_SUN_D) / R_SUN; sunMesh.scale.setScalar(sunS); corona.scale.setScalar(sunS);
  sunMesh.visible = myth || showSolar > 0.01; corona.visible = sunMesh.visible && dS < 90; corona.material.uniforms.uA.value = 0.8;
  sunGlare.visible = true; sunGlare.scale.setScalar(myth ? 3.4 : Math.max(R_SUN_D * 7, dS * 0.06)); sunGlare.material.uniforms.uA.value = myth ? 0.5 * (1 - smooth(1.9, 2.55, t)) : showSolar * 0.55;
  // belts and orbits (Sun at rest), then the true paths (Sun moving)
  astBelt.material.uniforms.uY.value = kuiper.material.uniforms.uY.value = y;
  const lapA = smooth(15.5, 17.2, t) * (1 - smooth(24.2, 24.9, t)), restA = myth ? 0 : smooth(2.6, 3.2, t) * (1 - smooth(T_MOVE, T_MOVE + 0.8, t)) + smooth(25.1, 25.6, t) + lapA;
  astBelt.material.uniforms.uA.value = (restA - lapA) * 0.35; kuiper.material.uniforms.uA.value = (restA - lapA) * 0.3;
  rings.forEach((m, i) => { m.uniforms.uNow.value = y; m.uniforms.uStart.value = y - PL[i].P * 0.995; m.uniforms.uA.value = restA * 0.8; m.uniforms.uWidth.value = 2.2 + 1.8 * lapA; m.uniforms.uHead.value = 0.02; });
  const moveA = myth ? 0 : smooth(T_MOVE, T_MOVE + 0.4, t) * (1 - smooth(14.5, 16.5, t)) * showSolar;
  trails.forEach((m, i) => { m.uniforms.uNow.value = y; m.uniforms.uStart.value = Y_MOVE; m.uniforms.uA.value = moveA * (i === 2 ? 1.25 : 1);
    m.uniforms.uWidth.value = i === 2 ? 4 : 3; m.uniforms.uHead.value = 0.04; });
  sunTrailMat.uniforms.uLen.value = Math.max(0, y - Y_MOVE) * VD; sunTrailMat.uniforms.uA.value = moveA * 0.9;
  dustMat.uniforms.uS.value = y - Y_MOVE; dustMat.uniforms.uA.value = myth ? 0 : smooth(6.2, 6.8, t) * (1 - smooth(9, 10.5, t)) * 0.5;
  // the myth
  const mA = myth ? 1 - smooth(1.9, 2.55, t) : 0;
  mythTrails.forEach(m => { m.uniforms.uNow.value = t; m.uniforms.uStart.value = t - 6; m.uniforms.uA.value = mA * (1 - smooth(1.6, 2.3, t)); m.uniforms.uWidth.value = 3.2; m.uniforms.uHead.value = 0.15; });
  mythBeads.forEach(b => { b.visible = false; });
  mythSun.position.set(0, 0, 0); mythSun.material.uniforms.uA.value = mA * 0.3; mythSun.visible = myth; mythTail.uniforms.uA.value = mA;
  renderer.render(sSolar, camS);
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
  return { motionAboveEclipticDeg: beta, eclipticToGalacticPlaneDeg: tilt, earthAheadFraction: ahead / 1000, auPerYear: VSUN,
    axialTiltsDeg: bodies.map(b => +(Math.acos(b.pole.z) / RAD).toFixed(1)), lapMyr: state(T_LAP1).myr }; };
window.renderAt(3.0);
window.ready = true;
