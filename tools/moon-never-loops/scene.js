import * as T from 'three';
// The Moon Never Loops. Open on the loopy Moon path everyone draws, shrink the Moon's orbit to true
// scale (the loops unwind into Earth's circle), then ride one year behind Earth: the Moon weaves
// across Earth's track 12.4 times but its path always bends toward the Sun. Never a loop.
// Units: 1 world unit = 1 million km. Distances are true; Sun, Earth and Moon discs are enlarged.
const spec = await fetch('./timeline.json').then(r => r.json());
window.filmSpec = spec;
const F = spec.facts, DUR = spec.duration;
const Y = F.year_days, MS = F.sidereal_month_days, SYN = F.synodic_month_days;
const R = F.earth_sun_km / 1e6, RM = F.earth_moon_km / 1e6, RMYTH = spec.myth_r_over_R * R;
const WE = 2 * Math.PI / Y, WM = 2 * Math.PI / MS, PHI = Math.PI; // day 0: new Moon, between Earth and Sun
const params = new URLSearchParams(location.search), W = +(params.get('w') || 720), H = Math.round(W * 16 / 9);
const film = document.querySelector('#film');
const renderer = new T.WebGLRenderer({ canvas: film, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H, false);
const FOV = 50, PX = H / (2 * Math.tan(FOV * Math.PI / 360));
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const smooth = (a, b, x) => { const s = clamp((x - a) / (b - a)); return s * s * (3 - 2 * s); };
const mixv = (a, b, s) => a + (b - a) * s;

const earthAt = d => new T.Vector3(R * Math.cos(WE * d), R * Math.sin(WE * d), 0);
const moonAt = (d, r) => earthAt(d).add(new T.Vector3(r * Math.cos(WM * d + PHI), r * Math.sin(WM * d + PHI), 0));

const scene = new T.Scene(); scene.background = new T.Color('#050a12');
const cam = new T.PerspectiveCamera(FOV, 9 / 16, 0.01, 8000); cam.up.set(0, 0, 1);
const U = { uPX: { value: PX }, uH: { value: H }, uAspect: { value: 9 / 16 }, uTime: { value: 0 } };

// ---------- stars (far shell) and orbit dust (parallax while riding) ----------
function points(pos, col, key, vs, fs, extra = {}) {
  const g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute(pos, 3)); if (col) g.setAttribute('aC', new T.Float32BufferAttribute(col, 1));
  const m = new T.ShaderMaterial({ uniforms: { ...U, ...extra }, transparent: true, depthWrite: false, blending: T.AdditiveBlending, vertexShader: vs, fragmentShader: fs });
  m.customProgramCacheKey = () => key; const p = new T.Points(g, m); p.frustumCulled = false; scene.add(p); return m;
}
let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
{
  const pos = [], col = [];
  for (let i = 0; i < 5000; i++) { const u = rnd() * 2 - 1, a = rnd() * 2 * Math.PI, s = Math.sqrt(1 - u * u); pos.push(4000 * s * Math.cos(a), 4000 * s * Math.sin(a), 4000 * u); col.push(Math.pow(rnd(), 3)); }
  points(pos, col, 'stars', `attribute float aC; varying float vC; void main(){ vC = aC; vec4 mv = modelViewMatrix*vec4(position,1.); gl_Position = projectionMatrix*mv; gl_PointSize = 1.2 + 2.4*aC; }`,
    `varying float vC; void main(){ vec2 c=gl_PointCoord*2.-1.; float r=dot(c,c); if(r>1.)discard; vec3 col = mix(vec3(.62,.72,.85), vec3(1.,.9,.72), step(.7, fract(vC*37.)));
      gl_FragColor = vec4(col*(0.25+0.75*vC)*(1.-r), 1.); }`);
}
const dustMat = (() => {
  const pos = [], col = [];
  for (let i = 0; i < 60000; i++) { const a = rnd() * 2 * Math.PI, rr = R + (rnd() - .5) * 30, z = (rnd() - .5) * 12; pos.push(rr * Math.cos(a), rr * Math.sin(a), z); col.push(rnd()); }
  return points(pos, col, 'dust', `uniform float uPX; attribute float aC; varying float vA; void main(){ vec4 mv = modelViewMatrix*vec4(position,1.); gl_Position = projectionMatrix*mv;
      float d = -mv.z; gl_PointSize = clamp(0.06*uPX/d, 1.0, 5.); vA = (0.3+0.7*aC) * smoothstep(60., 6., d) * smoothstep(0.3, 1.5, d); }`,
    `uniform float uDust; varying float vA; void main(){ vec2 c=gl_PointCoord*2.-1.; float r=dot(c,c); if(r>1.)discard; gl_FragColor = vec4(vec3(.55,.68,.78)*.5*vA*uDust*(1.-r),1.); }`,
    { uDust: { value: 0 } });
})();

// ---------- the Sun: a dotted globe (latitude rings of gold dots) inside a soft corona ----------
const SUN_R = 12; // enlarged (true radius 0.7 units)
const sunMat = (() => {
  const pos = [], col = [];
  for (let lat = -84; lat <= 84; lat += 4) { const c = Math.cos(lat * Math.PI / 180), n = Math.max(6, Math.round(150 * c));
    for (let k = 0; k < n; k++) { const a = 2 * Math.PI * (k + 0.5 * (lat / 4 % 2)) / n; pos.push(SUN_R * c * Math.cos(a), SUN_R * c * Math.sin(a), SUN_R * Math.sin(lat * Math.PI / 180)); col.push(rnd()); } }
  return points(pos, col, 'sundots', `uniform float uPX; uniform float uTime; attribute float aC; varying float vL; varying float vC; void main(){ vec4 mv = modelViewMatrix*vec4(position,1.);
      gl_Position = projectionMatrix*mv; gl_PointSize = clamp(0.32*uPX/-mv.z, 1.4, 7.); vec3 n = normalize(normalMatrix*normalize(position)); vL = pow(clamp(n.z,0.,1.), 0.6);
      vC = aC; }`,
    `uniform float uTime; varying float vL; varying float vC; void main(){ vec2 c=gl_PointCoord*2.-1.; float r=dot(c,c); if(r>1.)discard;
      float fl = 0.75 + 0.25*sin(uTime*2.3 + vC*40.); vec3 col = mix(vec3(.95,.55,.2), vec3(1.,.92,.7), vL);
      gl_FragColor = vec4(col*(0.25+0.9*vL)*fl*(1.-r), 1.); }`);
})();
const glowSprite = (size, col, key, power) => {
  const m = new T.ShaderMaterial({ uniforms: { ...U, uA: { value: 1 } }, transparent: true, depthWrite: false, blending: T.AdditiveBlending,
    vertexShader: `varying vec2 vUv; void main(){ vUv = uv*2.-1.; gl_Position = projectionMatrix*(modelViewMatrix*vec4(0.,0.,0.,1.) + vec4(position.xy, 0., 0.)); }`,
    fragmentShader: `uniform float uA; varying vec2 vUv; void main(){ float r = length(vUv); float g = pow(max(0., 1.-r), ${power.toFixed(1)}); gl_FragColor = vec4(vec3(${col})*g*uA, 1.); }` });
  m.customProgramCacheKey = () => key; const s = new T.Mesh(new T.PlaneGeometry(size, size), m); s.frustumCulled = false; scene.add(s); return s;
};
const sunCore = new T.Mesh(new T.SphereGeometry(SUN_R * 0.97, 64, 48), new T.MeshBasicMaterial({ color: '#2a1406' })); scene.add(sunCore);
const corona = glowSprite(SUN_R * 9, '1.,.72,.38', 'corona', 3.2); corona.material.uniforms.uA.value = 0.55;

// ---------- the two paths: screen-space ribbons evaluated in the vertex shader ----------
// mode 0 = Earth (teal), 1 = Moon (gold). uR is the Moon's orbit radius (morphs from myth to true).
const NSEG = 12000;
function pathRibbon(mode, key) {
  const tau = [], side = [], idx = [];
  for (let i = 0; i <= NSEG; i++) { const d = Y * i / NSEG; tau.push(d, d); side.push(-1, 1); if (i < NSEG) { const a = 2 * i; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); } }
  const g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute(new Array(tau.length * 3).fill(0), 3));
  g.setAttribute('aTau', new T.Float32BufferAttribute(tau, 1)); g.setAttribute('aSide', new T.Float32BufferAttribute(side, 1)); g.setIndex(idx);
  const m = new T.ShaderMaterial({ uniforms: { ...U, uR: { value: RMYTH }, uNow: { value: 0 }, uWidth: { value: 3 }, uFuture: { value: 1 }, uHead: { value: 20 }, uA: { value: 1 }, uBase: { value: 0.8 } },
    transparent: true, depthWrite: false, depthTest: false, blending: T.AdditiveBlending, side: T.DoubleSide,
    vertexShader: `uniform float uR; uniform float uWidth; uniform float uH; uniform float uAspect; attribute float aTau; attribute float aSide; varying float vTau; varying float vSide;
      vec3 P(float d){ float e = ${WE.toFixed(9)}*d, m = ${WM.toFixed(9)}*d + ${PHI.toFixed(6)}; return vec3(${R.toFixed(4)}*cos(e), ${R.toFixed(4)}*sin(e), 0.) + ${mode.toFixed(1)}*uR*vec3(cos(m), sin(m), 0.); }
      void main(){ vTau = aTau; vSide = aSide; float dt = ${(Y / NSEG).toFixed(6)};
        vec4 p0 = projectionMatrix*modelViewMatrix*vec4(P(aTau),1.), p1 = projectionMatrix*modelViewMatrix*vec4(P(aTau+dt),1.), pm = projectionMatrix*modelViewMatrix*vec4(P(aTau-dt),1.);
        vec2 s0 = p0.xy/max(p0.w,1e-4), s1 = p1.xy/max(p1.w,1e-4), sm = pm.xy/max(pm.w,1e-4);
        vec2 dir = (s1 - sm)*vec2(uAspect,1.); dir = length(dir) > 1e-7 ? normalize(dir) : vec2(1.,0.);
        vec2 n = vec2(-dir.y, dir.x)/vec2(uAspect,1.);
        gl_Position = p0 + vec4(n*aSide*uWidth/uH*p0.w, 0., 0.); if (p0.w < 0.02) gl_Position = vec4(0.,0.,-2.,1.); }`,
    fragmentShader: `uniform float uNow; uniform float uFuture; uniform float uHead; uniform float uA; uniform float uBase; varying float vTau; varying float vSide;
      void main(){ float edge = 1. - vSide*vSide; float d = uNow - vTau; float past = step(0., d);
        float head = past*exp(-max(d, 0.)/uHead); float b = mix(uFuture, 1., past)*uBase + 1.6*head;
        vec3 col = ${mode ? 'mix(vec3(.95,.72,.32), vec3(1.,.95,.8), head)' : 'mix(vec3(.2,.62,.66), vec3(.6,.95,.95), head)'};
        gl_FragColor = vec4(col*b*edge*uA, 1.); }` });
  m.customProgramCacheKey = () => key; const mesh = new T.Mesh(g, m); mesh.frustumCulled = false; mesh.renderOrder = 2 + mode; scene.add(mesh); return m;
}
const earthPath = pathRibbon(0, 'pathE'), moonPath = pathRibbon(1, 'pathM');

// ---------- Earth and Moon: lit sphere sprites (enlarged, clamped to a minimum screen size) ----------
function body(key, base, size, minPx) {
  const g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute([0, 0, 0], 3));
  const m = new T.ShaderMaterial({ uniforms: { ...U, uSize: { value: size }, uMin: { value: minPx }, uSun: { value: new T.Vector3() }, uA: { value: 1 } }, transparent: true, depthWrite: false, depthTest: false,
    vertexShader: `uniform float uPX; uniform float uSize; uniform float uMin; void main(){ vec4 mv = modelViewMatrix*vec4(position,1.); gl_Position = projectionMatrix*mv; gl_PointSize = max(uMin, uSize*uPX/-mv.z); }`,
    fragmentShader: `uniform vec3 uSun; uniform float uA; void main(){ vec2 c = gl_PointCoord*2.-1.; c.y = -c.y; float r2 = dot(c,c);
      vec2 cc = c*1.45; float rr = dot(cc,cc); vec3 col = vec3(0.);
      if (rr < 1.) { vec3 n = vec3(cc, sqrt(1.-rr)); float l = clamp(dot(n, normalize(uSun)), 0., 1.); col = vec3(${base})*(0.06 + 1.15*pow(l,0.8)) + vec3(.9,.95,1.)*pow(1.-n.z,4.)*0.25*l; }
      float halo = exp(-r2*5.)*0.35; if (r2 > 1.) discard; gl_FragColor = vec4((col + vec3(${base})*halo)*uA, rr < 1. ? 1. : halo*uA); }` });
  m.customProgramCacheKey = () => key; const p = new T.Points(g, m); p.frustumCulled = false; p.renderOrder = 10; scene.add(p); return p;
}
const earth = body('earth', '.35,.62,.95', 0.06, 15), moon = body('moon', '1.,.98,.92', 0.03, 10);
moon.renderOrder = 11;

// ---------- timeline ----------
// day: the clock that moves Earth and the Moon. Hook: one myth year in 2.4 s. Ride: one true year, 5.0 -> 15.6.
const RIDE0 = 5.0, RIDE1 = 15.6;
// eased ramp: accelerate over the first 12%, glide, decelerate over the last 10% (ends at exactly one year)
function rideDays(t) { const u = clamp((t - RIDE0) / (RIDE1 - RIDE0)), a = 0.12, b = 0.1, vmax = 1 / (1 - a / 2 - b / 2); let s;
  if (u < a) s = vmax * u * u / (2 * a); else if (u < 1 - b) s = vmax * (a / 2 + (u - a)); else s = 1 - vmax * (1 - u) * (1 - u) / (2 * b);
  return Y * clamp(s); }
const dayAt = t => t < 2.4 ? Y * (t / 2.4) % Y : t < RIDE0 ? 0 : rideDays(t);
function moonR(t) { // log morph myth -> true (2.7-4.6) and back (19.7-20.95)
  const l0 = Math.log(RMYTH), l1 = Math.log(RM);
  if (t < 2.7) return RMYTH; if (t < 4.6) return Math.exp(mixv(l0, l1, smooth(2.7, 4.6, t)));
  if (t < 19.7) return RM; return Math.exp(mixv(l1, l0, smooth(19.7, 20.95, t)));
}
function state(t) { const d = t >= RIDE0 ? rideDays(t) : 0; return { days: d, months: d / SYN }; }
window.stateAt = state;

// ---------- cameras ----------
const sph = (focus, dist, el, az) => { const e = el * Math.PI / 180, z = az * Math.PI / 180, r = dist * Math.cos(e);
  return { pos: focus.clone().add(new T.Vector3(r * Math.sin(z), -r * Math.cos(z), dist * Math.sin(e))), look: focus.clone() }; };
const TOP = (t) => sph(new T.Vector3(0, -8, 0), 800, 68, -4 + 6 * Math.sin(t * 0.4));
const FINAL = (t) => sph(new T.Vector3(R * 0.1, 0, 0), 720, 42, 62 - 3 * (t - 16.2));
function chase(d) { // ahead of Earth and a little outside the orbit, looking back down the track
  const e = WE * d, E = earthAt(d), Tg = new T.Vector3(-Math.sin(e), Math.cos(e), 0), N = new T.Vector3(Math.cos(e), Math.sin(e), 0);
  const pos = E.clone().addScaledVector(Tg, 1.5).addScaledVector(N, 0.3).add(new T.Vector3(0, 0, 0.32));
  const look = E.clone().addScaledVector(Tg, -3.0).addScaledVector(N, -0.25).add(new T.Vector3(0, 0, -0.02));
  return { pos, look };
}
function blendPose(a, b, s, l0 = 0, l1 = 0.4) { // log-distance blend between two poses; the look point moves during [l0, l1]
  const look = a.look.clone().lerp(b.look, smooth(l0, l1, s));
  const da = a.pos.distanceTo(a.look), db = b.pos.distanceTo(b.look);
  const dir = a.pos.clone().sub(a.look).normalize().lerp(b.pos.clone().sub(b.look).normalize(), smooth(0.05, 0.85, s)).normalize();
  return { pos: look.clone().addScaledVector(dir, Math.exp(mixv(Math.log(da), Math.log(db), s))), look };
}
function pose(t) {
  if (t < 5.0) return TOP(t);
  if (t < 7.0) { const s = smooth(5.0, 7.0, t); return blendPose(TOP(t), chase(dayAt(t)), Math.pow(s, 0.9)); }
  if (t < 16.2) return chase(dayAt(t));
  if (t < 18.6) return blendPose(chase(Y), FINAL(t), smooth(16.2, 18.6, t), 0.45, 1);
  if (t < 19.7) return FINAL(t);
  return blendPose(FINAL(t), TOP(t), smooth(19.7, 20.95, t));
}

// ---------- overlay ----------
const out = document.querySelector('#out'), ctx = out.getContext('2d');
const FONT = '"Liberation Mono", Menlo, monospace', C_CREAM = '#f4e6c8', C_TEAL = '#57d0cc', C_RED = 'rgb(214,62,48)', C_GOLD = '#e8bd68';
const typed = (s, t0, t1, t) => { if (t < t0) return ''; const n = Math.max(1, Math.ceil(s.length * clamp((t - t0) / (t1 - t0)))); return s.slice(0, n); };
function text(s, x, y, size, color, { align = 'center', alpha = 1, spacing = 0, stroke = true } = {}) {
  if (!s || alpha <= 0) return; ctx.save(); ctx.globalAlpha = alpha; ctx.font = `bold ${size}px ${FONT}`; ctx.textAlign = align; ctx.textBaseline = 'middle'; ctx.letterSpacing = spacing + 'px';
  if (stroke) { ctx.lineWidth = Math.max(4, size * 0.11); ctx.strokeStyle = '#04070d'; ctx.lineJoin = 'round'; ctx.strokeText(s, x, y); }
  ctx.fillStyle = color; ctx.fillText(s, x, y); ctx.restore();
}
function chip(s, x, y, size, alpha = 1) {
  if (!s || alpha <= 0) return; ctx.save(); ctx.globalAlpha = alpha; ctx.font = `bold ${size}px ${FONT}`; const w = ctx.measureText(s).width, px = size * 0.45, h = size * 1.42;
  ctx.fillStyle = C_RED; ctx.beginPath(); ctx.roundRect(x - w / 2 - px, y - h / 2, w + 2 * px, h, size * 0.22); ctx.fill();
  ctx.fillStyle = '#fff3e0'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(s, x, y + size * 0.04); ctx.restore();
}
const proj = v => { const q = v.clone().project(cam); return [(q.x + 1) / 2 * 1080, (1 - q.y) / 2 * 1920, q.z < 1]; };
function arrow(x0, y0, ang, len, col, alpha, label) {
  const x1 = x0 + Math.cos(ang) * len, y1 = y0 + Math.sin(ang) * len; ctx.save(); ctx.globalAlpha = alpha; ctx.lineCap = 'round';
  for (const [w, c] of [[11, '#04070d'], [5, col]]) { ctx.strokeStyle = c; ctx.fillStyle = c; ctx.lineWidth = w; ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke();
    const hx = Math.cos(ang), hy = Math.sin(ang), s = w === 11 ? 26 : 20; ctx.beginPath(); ctx.moveTo(x1 + hx * s * 0.6, y1 + hy * s * 0.6);
    ctx.lineTo(x1 - hx * s * 0.6 - hy * s * 0.55, y1 - hy * s * 0.6 + hx * s * 0.55); ctx.lineTo(x1 - hx * s * 0.6 + hy * s * 0.55, y1 - hy * s * 0.6 - hx * s * 0.55); ctx.fill(); }
  ctx.restore(); if (label) text(label, x1 + Math.cos(ang) * 44, y1 + Math.sin(ang) * 44 + (Math.abs(Math.sin(ang)) < 0.5 ? -28 : 0), 30, col, { alpha });
}
const grain = [...Array(6)].map((_, k) => { const c = document.createElement('canvas'); c.width = 270; c.height = 480; const x = c.getContext('2d'); const im = x.createImageData(270, 480); let s = 99 + k * 7;
  for (let i = 0; i < im.data.length; i += 4) { s = (s * 16807) % 2147483647; const v = s % 255; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; } x.putImageData(im, 0, 0); return c; });

function overlay(t, st, d, r) {
  // top tag
  const tagMyth = 1 - smooth(2.5, 2.8, t) + smooth(20.4, 20.9, t);
  text('THE USUAL DRAWING', 540, 168, 23, C_CREAM, { alpha: 0.62 * clamp(tagMyth), spacing: 3, stroke: false });
  text('DISTANCES TO SCALE · SUN, EARTH, MOON ENLARGED', 540, 168, 22, C_CREAM, { alpha: 0.62 * smooth(4.4, 4.8, t) * (1 - smooth(19.6, 20.0, t)), spacing: 1, stroke: false });
  // hook
  const hk = 1 - smooth(2.3, 2.6, t) + smooth(20.6, 20.95, t) * 0;
  if (hk > 0) {
    text(typed("THE MOON'S PATH", 0, 0.5, t), 540, 300, 84, C_CREAM, { alpha: hk });
    text(typed('AROUND THE SUN?', 0.5, 1.05, t), 540, 392, 64, C_GOLD, { alpha: hk });
    chip(t >= 1.45 ? 'THIS IS WRONG.' : '', 540, 1500, 52, hk * smooth(1.45, 1.52, t));
  }
  // true scale
  const ts = smooth(2.6, 2.75, t) * (1 - smooth(5.6, 6.0, t));
  if (ts > 0) {
    text(typed('AT TRUE SCALE', 2.65, 3.1, t), 540, 300, 68, C_CREAM, { alpha: ts });
    text(typed("THE MOON'S ORBIT IS 389× SMALLER", 3.1, 3.7, t), 540, 372, 28, C_CREAM, { alpha: ts * 0.9, spacing: 1, stroke: false });
    text(typed('NO LOOPS.', 4.55, 4.85, t), 540, 1500, 84, C_GOLD, { alpha: ts });
  }
  // counters
  const cA = smooth(5.9, 6.3, t) * (1 - smooth(16.0, 16.4, t)), by = 1452;
  [['DAYS', Math.floor(st.days).toString(), 300, C_CREAM], ['LUNAR MONTHS', st.months.toFixed(1), 780, C_GOLD]].forEach(([l, v, x, c]) => {
    text(l, x, by, 27, c, { alpha: 0.8 * cA, spacing: 4, stroke: false }); text(v, x, by + 64, 64, c, { alpha: cA }); });
  // body labels during the ride
  const lA = smooth(6.6, 7.0, t) * (1 - smooth(15.8, 16.2, t)), lB = lA * (1 - smooth(8.7, 8.9, t) + smooth(11.2, 11.45, t));
  if (lA > 0) {
    const [ex, ey] = proj(earthAt(d)), [mx, my] = proj(moonAt(d, r));
    text('EARTH', ex, ey + 58, 28, C_TEAL, { alpha: lB * 0.95, spacing: 2 });
    text('MOON', mx, my - 46, 26, '#dcdcd6', { alpha: lB * 0.95, spacing: 2 });
    // Sun direction marker on the frame edge
    const [sx, sy, front] = proj(new T.Vector3(0, 0, 0)); let ang = Math.atan2(sy - ey, sx - ex); if (!front) ang += Math.PI;
    const ex2 = 540 + Math.cos(ang) * 1000, ey2 = 960 + Math.sin(ang) * 1000, k = Math.min(440 / Math.abs(ex2 - 540 || 1), 600 / Math.abs(ey2 - 960 || 1), 1);
    const ax = 540 + (ex2 - 540) * k, ay = 960 + (ey2 - 960) * k;
    ctx.save(); ctx.globalAlpha = lA; ctx.fillStyle = C_GOLD; ctx.translate(ax, ay); ctx.rotate(ang); ctx.beginPath(); ctx.moveTo(30, 0); ctx.lineTo(-8, -18); ctx.lineTo(-8, 18); ctx.fill(); ctx.restore();
    text('SUN', ax - Math.cos(ang) * 64, ay - Math.sin(ang) * 40, 28, C_GOLD, { alpha: lA, spacing: 2 });
  }
  // why: two pulls on the Moon
  const pA = smooth(8.0, 8.2, t) * (1 - smooth(11.2, 11.45, t));
  if (pA > 0) {
    text(typed('THE SUN PULLS THE MOON', 8.0, 8.6, t), 540, 290, 50, C_CREAM, { alpha: pA });
    text(typed('2.2× HARDER THAN EARTH.', 8.6, 9.2, t), 540, 360, 50, C_GOLD, { alpha: pA });
    const [ex, ey] = proj(earthAt(d)), [mx, my] = proj(moonAt(d, r)), M = moonAt(d, r);
    const [sx, sy] = proj(M.clone().add(M.clone().negate().normalize().multiplyScalar(0.5)));
    const aS = Math.atan2(sy - my, sx - mx), aE = Math.atan2(ey - my, ex - mx), aA = pA * smooth(8.9, 9.3, t);
    arrow(mx, my, aS, 2.2 * 95, C_GOLD, aA, 'SUN 2.2×'); arrow(mx, my, aE, 95, C_TEAL, aA, 'EARTH 1×');
  }
  const bA = smooth(11.5, 11.7, t) * (1 - smooth(15.4, 15.6, t));
  text(typed('SO ITS PATH ALWAYS', 11.5, 12.1, t), 540, 290, 50, C_CREAM, { alpha: bA });
  text(typed('BENDS TOWARD THE SUN.', 12.1, 12.8, t), 540, 360, 50, C_GOLD, { alpha: bA });
  // twist
  const nA = smooth(16.2, 16.3, t) * (1 - smooth(19.4, 19.7, t));
  text(typed('IT NEVER', 16.2, 16.55, t), 540, 300, 96, C_CREAM, { alpha: nA });
  text(typed('GOES BACKWARDS.', 16.55, 17.2, t), 540, 404, 74, C_GOLD, { alpha: nA });
  text(typed('12.4 GENTLE WAVES A YEAR · ZERO LOOPS', 17.7, 18.5, t), 540, 1500, 29, C_CREAM, { alpha: nA * 0.95, spacing: 1 });
  const fl = t >= 16.2 ? 0.12 * Math.exp(-(t - 16.2) * 12) : 0;
  if (fl > 0.005) { ctx.save(); ctx.fillStyle = `rgba(255,240,220,${fl})`; ctx.fillRect(0, 0, 1080, 1920); ctx.restore(); }
}

function drawFilm() { ctx.drawImage(film, 0, 0, 1080, 1920); ctx.save();
  ctx.globalCompositeOperation = 'lighter'; ctx.filter = 'blur(14px)'; ctx.globalAlpha = 0.5; ctx.drawImage(film, 0, 0, 1080, 1920);
  ctx.filter = 'blur(40px)'; ctx.globalAlpha = 0.3; ctx.drawImage(film, 0, 0, 1080, 1920); ctx.restore(); }

window.renderAt = function (t, frame = Math.round(t * 30)) {
  t = ((t % DUR) + DUR) % DUR;
  const st = state(t), d = dayAt(t), r = moonR(t);
  U.uTime.value = t;
  const p = pose(t); cam.position.copy(p.pos); cam.lookAt(p.look);
  const camDist = p.pos.distanceTo(p.look);
  cam.near = Math.max(0.01, camDist * 0.004); cam.updateProjectionMatrix();
  // paths: whole path lit in the overview shots, past bright / future dim while riding
  const ride = smooth(5.0, 6.2, t) * (1 - smooth(16.2, 17.4, t));
  for (const m of [earthPath, moonPath]) { const u = m.uniforms; u.uR.value = r; u.uNow.value = t < RIDE0 ? (t < 2.4 ? d : -1) : d;
    u.uFuture.value = mixv(1, 0.2, ride); u.uHead.value = t < 2.4 ? 22 : 1.2; }
  if (t >= 16.2) { earthPath.uniforms.uNow.value = moonPath.uniforms.uNow.value = Y + 1; }
  moonPath.uniforms.uWidth.value = mixv(3.2, 2.6, ride); earthPath.uniforms.uWidth.value = mixv(2.0, 1.8, ride);
  earthPath.uniforms.uBase.value = mixv(0.55, 0.75, ride); moonPath.uniforms.uBase.value = 0.85;
  moonPath.uniforms.uHead.value = t < 2.4 ? 22 : 1.2; earthPath.uniforms.uHead.value = t < 2.4 ? 0.001 : 1.2;
  earth.position.copy(earthAt(d)); moon.position.copy(moonAt(d, r));
  for (const b of [earth, moon]) b.material.uniforms.uSun.value.copy(b.position.clone().negate().normalize()).transformDirection(cam.matrixWorldInverse);
  moon.material.uniforms.uMin.value = mixv(9, 13, ride); earth.material.uniforms.uMin.value = mixv(14, 22, ride);
  dustMat.uniforms.uDust.value = ride;
  ctx.fillStyle = '#050a12'; ctx.fillRect(0, 0, 1080, 1920);
  renderer.render(scene, cam); drawFilm();
  ctx.save(); const v = ctx.createRadialGradient(540, 960, 380, 540, 960, 1150); v.addColorStop(0, 'rgba(4,8,14,0)'); v.addColorStop(1, 'rgba(4,8,14,0.72)'); ctx.fillStyle = v; ctx.fillRect(0, 0, 1080, 1920);
  ctx.globalAlpha = 0.045; ctx.globalCompositeOperation = 'overlay'; ctx.drawImage(grain[frame % 6], 0, 0, 1080, 1920); ctx.restore();
  overlay(t, st, d, r);
  return st;
};
// fact check: the true heliocentric Moon path must curve toward the Sun everywhere (curvature > 0)
window.convexCheck = () => { let min = Infinity; const h = 0.01; for (let d = 0; d < Y; d += 0.05) {
  const a = moonAt(d - h, RM), b = moonAt(d, RM), c = moonAt(d + h, RM); const vx = (c.x - a.x) / 2 / h, vy = (c.y - a.y) / 2 / h, ax = (c.x - 2 * b.x + a.x) / h / h, ay = (c.y - 2 * b.y + a.y) / h / h;
  min = Math.min(min, (vx * ay - vy * ax) / Math.pow(Math.hypot(vx, vy), 3) * R); } return min; };
window.captureFrame = (t, frame) => { window.renderAt(t, frame); return out.toDataURL('image/jpeg', 0.95).split(',')[1]; };
window.renderAt(0.01);
window.ready = true;
