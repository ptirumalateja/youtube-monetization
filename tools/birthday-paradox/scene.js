import * as T from 'three';
// The Birthday Paradox. A 365-day ring seen from above; people drop in as dots and every
// new dot threads itself to every earlier one. window.renderAt(t) is deterministic.
const spec = await fetch('./timeline.json').then(r => r.json());
window.filmSpec = spec;
const people = spec.people, N = people.length, DUR = spec.duration;
const params = new URLSearchParams(location.search), W = +(params.get('w') || 720), H = Math.round(W * 16 / 9);

const film = document.querySelector('#film');
const renderer = new T.WebGLRenderer({ canvas: film, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H, false);
const scene = new T.Scene(); scene.background = new T.Color('#060b13');
const FOV = 50, camera = new T.PerspectiveCamera(FOV, 9 / 16, 0.1, 400);
camera.up.set(0, 0, 1);
const PX = H / (2 * Math.tan(FOV * Math.PI / 360)); // world-size -> pixel factor for points

const R = 10, GOLD = new T.Color('#e0b25a'), TEAL = new T.Color('#3fc4c4'), CREAM = new T.Color('#f4e6c8'), RED = new T.Color('#d63e30');
const ang = day => Math.PI / 2 - 2 * Math.PI * (day + 0.5) / 365; // JAN at the top, clockwise
const MONTH0 = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
const MONTHS = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];

const U = { uTime: { value: 0 }, uImp: { value: 0 }, uPX: { value: PX }, uGlow: { value: 0 }, uThreadA: { value: 0.5 }, uP: { value: 0 }, uFade: { value: 1 } };
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const smooth = (a, b, x) => { const s = clamp((x - a) / (b - a)); return s * s * (3 - 2 * s); };

// ---------- the 365-day ring: one tick per day, longer gold ticks at month starts ----------
{
  const pos = [], bright = [], angA = [];
  for (let d = 0; d < 365; d++) {
    const m = MONTH0.includes(d), a = Math.PI / 2 - 2 * Math.PI * d / 365, r0 = R + 0.22, r1 = R + (m ? 1.25 : 0.6), w = m ? 0.05 : 0.026;
    const c = Math.cos(a), s = Math.sin(a), tx = -s * w, ty = c * w;
    const q = [[r0 * c - tx, r0 * s - ty], [r0 * c + tx, r0 * s + ty], [r1 * c + tx, r1 * s + ty], [r1 * c - tx, r1 * s - ty]];
    for (const k of [0, 1, 2, 0, 2, 3]) { pos.push(q[k][0], q[k][1], 0); bright.push(m ? 1 : 0.42); angA.push(d / 365); }
  }
  const g = new T.BufferGeometry();
  g.setAttribute('position', new T.Float32BufferAttribute(pos, 3));
  g.setAttribute('aB', new T.Float32BufferAttribute(bright, 1));
  g.setAttribute('aA', new T.Float32BufferAttribute(angA, 1));
  const m = new T.ShaderMaterial({ uniforms: U, transparent: true, depthWrite: false, blending: T.AdditiveBlending,
    vertexShader: `attribute float aB; attribute float aA; varying float vB; varying float vA; void main(){ vB=aB; vA=aA; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader: `uniform float uGlow; uniform float uTime; uniform float uFade; varying float vB; varying float vA;
      void main(){ float sweep = fract(uTime/0.9); float dA = abs(fract(vA - sweep + .5) - .5);
        float pulse = uGlow * (0.55 + 1.4*exp(-dA*dA*400.));
        vec3 col = mix(vec3(.88,.70,.36), vec3(1.,.93,.78), clamp(pulse,0.,1.));
        gl_FragColor = vec4(col*(vB*0.85 + pulse*0.9)*uFade, 1.); }` });
  m.customProgramCacheKey = () => 'ticks';
  scene.add(new T.Mesh(g, m));
  const base = new T.Mesh(new T.RingGeometry(R + 0.12, R + 0.2, 512), new T.MeshBasicMaterial({ color: GOLD, transparent: true, opacity: 0.55, blending: T.AdditiveBlending, depthWrite: false }));
  scene.add(base);
}
// month names, flat on the floor, upright toward the top of the frame
{
  for (let i = 0; i < 12; i++) {
    const c = document.createElement('canvas'); c.width = 256; c.height = 96; const x = c.getContext('2d');
    x.font = 'bold 64px Menlo, monospace'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillStyle = '#f1dcae'; x.fillText(MONTHS[i], 128, 50);
    const tex = new T.CanvasTexture(c); tex.anisotropy = 8;
    const mesh = new T.Mesh(new T.PlaneGeometry(2.1, 0.79), new T.MeshBasicMaterial({ map: tex, transparent: true, opacity: 0.62, depthWrite: false }));
    const a = ang(MONTH0[i] + 15), r = R + 2.35; mesh.position.set(r * Math.cos(a), r * Math.sin(a), 0); scene.add(mesh);
  }
}
// probability gauge just inside the ring, with a red tick at 50%
{
  const g = new T.RingGeometry(R - 0.98, R - 0.84, 512, 1);
  const m = new T.ShaderMaterial({ uniforms: U, transparent: true, depthWrite: false, blending: T.AdditiveBlending,
    vertexShader: `varying vec2 vP; void main(){ vP=position.xy; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader: `uniform float uP; uniform float uFade; varying vec2 vP;
      void main(){ float f = fract(atan(vP.x, vP.y)/6.2831853 + 1.); float on = step(f, uP);
        vec3 c = mix(vec3(.10,.16,.20)*.6, vec3(.25,.77,.77)*.62, on); gl_FragColor = vec4(c*uFade, 1.); }` });
  m.customProgramCacheKey = () => 'gauge';
  scene.add(new T.Mesh(g, m));
  const tick = new T.Mesh(new T.PlaneGeometry(0.14, 0.9), new T.MeshBasicMaterial({ color: RED, transparent: true, opacity: 0.95, depthWrite: false }));
  tick.position.set(0, -(R - 0.91), 0.01); scene.add(tick);
  window._halfTick = tick;
}

// ---------- people ----------
const slot = p => { const a = ang(p.day), r = R - 0.15 - p.stack * 0.62; return new T.Vector3(r * Math.cos(a), r * Math.sin(a), 0); };
const P3 = people.map(slot);
const BIG = 1e6;
function pointsLayer(kind) {
  const g = new T.BufferGeometry(), pos = [], tl = [], dr = [], tr = [];
  people.forEach((p, i) => { pos.push(P3[i].x, P3[i].y, 0); tl.push(p.t); dr.push(p.drop); tr.push(p.tRed ?? BIG); });
  g.setAttribute('position', new T.Float32BufferAttribute(pos, 3));
  g.setAttribute('aT', new T.Float32BufferAttribute(tl, 1));
  g.setAttribute('aD', new T.Float32BufferAttribute(dr, 1));
  g.setAttribute('aR', new T.Float32BufferAttribute(tr, 1));
  const dots = kind === 'dots';
  const m = new T.ShaderMaterial({ uniforms: U, transparent: true, depthWrite: false, blending: T.AdditiveBlending,
    vertexShader: `uniform float uTime; uniform float uImp; uniform float uPX; attribute float aT; attribute float aD; attribute float aR;
      varying float vA; varying float vRed; varying float vK;
      void main(){ vec3 p = position; float t = uTime;
        ${dots ? `
        float s = clamp((t - (aT - aD)) / aD, 0., 1.); float fall = (1.-s)*(1.-s);
        p.z += 30. * fall; vA = step(aT - aD, t) * (0.35 + 0.65*s);
        float land = exp(-max(t-aT,0.)*7.) * step(aT, t);
        float size = 0.62 + 0.9*land + 0.5*fall;
        vRed = smoothstep(aR, aR+0.08, t); vK = land;` : `
        float age = t - aT; vA = step(0., age) * exp(-age*4.) * 0.7; float size = 0.6 + 2.6*(1.-exp(-age*4.));
        vRed = smoothstep(aR, aR+0.05, t); vK = 0.;`}
        p = mix(p, vec3(0.,0.,1.5), uImp); vA *= 1. - uImp*uImp;
        vec4 mv = modelViewMatrix * vec4(p, 1.); gl_Position = projectionMatrix * mv; gl_PointSize = min(size * uPX / -mv.z, 46.); }`,
    fragmentShader: `uniform float uFade; varying float vA; varying float vRed; varying float vK;
      void main(){ vec2 c = gl_PointCoord*2.-1.; float r = length(c); if (r > 1.) discard;
        vec3 base = mix(vec3(1.,.90,.68), vec3(.86,.25,.19), vRed);
        ${dots ? `float core = smoothstep(.42,.30,r); float halo = exp(-r*r*5.)*.55; vec3 col = base*(halo+core) + vec3(1.)*core*(.25+vK*.6)*(1.-vRed*.6);`
               : `float ring = smoothstep(.09,0.,abs(r-.86)); vec3 col = base*ring*.8;`}
        gl_FragColor = vec4(col*vA*uFade, 1.); }` });
  m.customProgramCacheKey = () => kind;
  const pts = new T.Points(g, m); pts.frustumCulled = false; scene.add(pts);
}
pointsLayer('ripples'); pointsLayer('dots');

// ---------- threads: one arc per pair, grown from the newcomer to the earlier dot ----------
const SEG = 18, pairs = [];
for (let j = 1; j < N; j++) for (let i = 0; i < j; i++) {
  const pj = people[j], grow = j < 22 ? 0.32 : j === 22 ? 0.42 : 0.2;
  const born = pj.t + (j === 22 ? 0.0 : 0.2) * (i / j) + (j === 22 && people[i].day !== pj.day ? 0.12 + 0.35 * (i / j) : 0);
  pairs.push({ i, j, born, grow, red: people[i].day === pj.day });
}
window._pairs = pairs;
function arc(a, b, k) {
  const mid = a.clone().add(b).multiplyScalar(0.5), chord = a.distanceTo(b);
  const c = mid.multiplyScalar(0.95 - 0.63 * Math.min(1, chord / (2 * R))); c.z = 0.16 * chord;
  const u = k / SEG, v = 1 - u; // quadratic bezier from b (newcomer) to a
  return new T.Vector3().addScaledVector(b, v * v).addScaledVector(c, 2 * u * v).addScaledVector(a, u * u);
}
{
  const pos = [], uu = [], bb = [], gg = [], rr = [];
  for (const pr of pairs) {
    const a = P3[pr.i], b = P3[pr.j];
    for (let k = 0; k < SEG; k++) for (const kk of [k, k + 1]) { const v = arc(a, b, kk); pos.push(v.x, v.y, v.z); uu.push(kk / SEG); bb.push(pr.born); gg.push(pr.grow); rr.push(pr.red ? 1 : 0); }
  }
  const g = new T.BufferGeometry();
  g.setAttribute('position', new T.Float32BufferAttribute(pos, 3));
  g.setAttribute('aU', new T.Float32BufferAttribute(uu, 1));
  g.setAttribute('aB', new T.Float32BufferAttribute(bb, 1));
  g.setAttribute('aG', new T.Float32BufferAttribute(gg, 1));
  g.setAttribute('aRed', new T.Float32BufferAttribute(rr, 1));
  const m = new T.ShaderMaterial({ uniforms: U, transparent: true, depthWrite: false, blending: T.AdditiveBlending,
    vertexShader: `uniform float uTime; uniform float uImp; attribute float aU; attribute float aB; attribute float aG; attribute float aRed;
      varying float vA; varying float vRed;
      void main(){ float prog = (uTime - aB) / aG; vA = step(aU, prog); float head = exp(-max(prog-aU,0.)*6.);
        vA *= 0.75 + 1.6*head*step(prog,1.6); vRed = aRed;
        vec3 p = mix(position, vec3(0.,0.,1.5), uImp); vA *= 1. - uImp;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.); }`,
    fragmentShader: `uniform float uThreadA; uniform float uFade; varying float vA; varying float vRed;
      void main(){ vec3 c = mix(vec3(.25,.77,.78), vec3(.84,.24,.19), vRed); float a = mix(uThreadA, 1., vRed);
        gl_FragColor = vec4(c*vA*a*uFade, 1.); }` });
  m.customProgramCacheKey = () => 'threads';
  const ls = new T.LineSegments(g, m); ls.frustumCulled = false; scene.add(ls);
}
// the red "same birthday" links also get a thick tube so they read at phone size
for (const pr of pairs.filter(p => p.red)) {
  const a = P3[pr.i], b = P3[pr.j]; const pts = []; for (let k = 0; k <= SEG; k++) pts.push(arc(a, b, k));
  const curve = new T.CatmullRomCurve3(pts);
  const g = new T.TubeGeometry(curve, 48, pr.j === 22 ? 0.11 : 0.07, 8, false);
  const m = new T.ShaderMaterial({ uniforms: { ...U, aB: { value: pr.born }, aG: { value: pr.grow } }, transparent: true, depthWrite: false, blending: T.AdditiveBlending,
    vertexShader: `uniform float uImp; varying float vU; void main(){ vU = uv.x; vec3 p = mix(position, vec3(0.,0.,1.5), uImp); gl_Position = projectionMatrix*modelViewMatrix*vec4(p,1.); }`,
    fragmentShader: `uniform float uTime; uniform float aB; uniform float aG; uniform float uImp; uniform float uFade; varying float vU;
      void main(){ float prog = (uTime - aB)/aG; if (vU > prog) discard; float head = exp(-max(prog-vU,0.)*5.)*step(prog,1.5);
        gl_FragColor = vec4(vec3(.86,.26,.2)*(0.8+1.2*head)*(1.-uImp)*uFade, 1.); }` });
  m.customProgramCacheKey = () => 'tube' + pr.j;
  scene.add(new T.Mesh(g, m));
}

// ---------- parallax dust ----------
{
  let s = 7; const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
  const pos = [], ph = [];
  for (let i = 0; i < 2600; i++) { pos.push((rnd() - .5) * 70, (rnd() - .5) * 70, -14 + rnd() * 34); ph.push(rnd() * 6.28); }
  const g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute(pos, 3)); g.setAttribute('aPh', new T.Float32BufferAttribute(ph, 1));
  const m = new T.ShaderMaterial({ uniforms: U, transparent: true, depthWrite: false, blending: T.AdditiveBlending,
    vertexShader: `uniform float uTime; uniform float uPX; attribute float aPh; varying float vA;
      void main(){ vec3 p = position; p.z += 0.6*sin(uTime*0.35 + aPh); p.x += 0.4*sin(uTime*0.21 + aPh*1.7);
        vec4 mv = modelViewMatrix*vec4(p,1.); gl_Position = projectionMatrix*mv; gl_PointSize = max(1.2, 0.16*uPX/-mv.z);
        vA = 0.18 + 0.14*sin(aPh*3.); }`,
    fragmentShader: `uniform float uFade; varying float vA; void main(){ vec2 c=gl_PointCoord*2.-1.; float r=dot(c,c); if(r>1.)discard; gl_FragColor=vec4(vec3(.62,.72,.80)*vA*(1.-r)*mix(.6,1.,uFade),1.); }` });
  m.customProgramCacheKey = () => 'dust';
  const d = new T.Points(g, m); d.frustumCulled = false; scene.add(d);
}

// ---------- camera: Catmull-Rom through keys [t, distance, elevation deg, azimuth deg] ----------
const CK = [[-1.3, 49, 60, 22], [0, 44, 84, -8], [2.05, 49, 78, -3], [2.6, 47, 61, 3], [7, 47, 59, 8], [11.0, 46, 58, 13], [11.75, 43.5, 60, 14],
  [13.5, 43, 63, 16], [15.2, 45, 62, 18], [18.0, 49, 57, 22], [20.2, 49, 60, 22], [21.5, 44, 84, -8], [23.55, 49, 78, -3]];
function camAt(t) {
  let k = 1; while (k < CK.length - 2 && t > CK[k + 1][0]) k++;
  const [a, b, c, d] = [CK[k - 1], CK[k], CK[k + 1], CK[k + 2]], u = clamp((t - b[0]) / (c[0] - b[0]));
  const out = [];
  for (let j = 1; j < 4; j++) { // non-uniform Catmull-Rom (tangents scaled by interval)
    const m1 = (c[j] - a[j]) / (c[0] - a[0]) * (c[0] - b[0]), m2 = (d[j] - b[j]) / (d[0] - b[0]) * (c[0] - b[0]);
    const u2 = u * u, u3 = u2 * u; out.push((2 * u3 - 3 * u2 + 1) * b[j] + (u3 - 2 * u2 + u) * m1 + (-2 * u3 + 3 * u2) * c[j] + (u3 - u2) * m2);
  }
  return out;
}
const look = new T.Vector3(0, -1.4, 0);
function placeCamera(t) {
  const [D, el, az] = camAt(t), e = el * Math.PI / 180, z = az * Math.PI / 180, r = D * Math.cos(e);
  camera.position.set(r * Math.sin(z), -r * Math.cos(z), D * Math.sin(e));
  camera.lookAt(look);
}

// ---------- state as a pure function of t ----------
const Pn = n => { let q = 1; for (let k = 0; k < n; k++) q *= (365 - k) / 365; return 1 - q; };
function state(t) {
  let n = 0; while (n < N && people[n].t <= t) n++;
  const last = n ? people[n - 1].t : 0, tw = smooth(last, last + 0.22, t);
  const p = n ? Pn(n - 1) + (Pn(n) - Pn(n - 1)) * tw : 0;
  return { n, pairs: n * (n - 1) / 2, p };
}
window.stateAt = state;

// ---------- overlay ----------
const out = document.querySelector('#out'), ctx = out.getContext('2d');
const FONT = 'Menlo, "Liberation Mono", monospace';
const C_CREAM = '#f4e6c8', C_TEAL = '#57d0cc', C_RED = 'rgb(214,62,48)', C_GOLD = '#e8bd68';
const typed = (s, t0, t1, t) => { if (t < t0) return ''; const n = Math.max(1, Math.ceil(s.length * clamp((t - t0) / (t1 - t0)))); return s.slice(0, n); };
function text(s, x, y, size, color, { align = 'center', alpha = 1, spacing = 0, weight = 'bold', stroke = true } = {}) {
  if (!s || alpha <= 0) return;
  ctx.save(); ctx.globalAlpha = alpha; ctx.font = `${weight} ${size}px ${FONT}`; ctx.textAlign = align; ctx.textBaseline = 'middle';
  ctx.letterSpacing = spacing + 'px';
  if (stroke) { ctx.lineWidth = Math.max(4, size * 0.11); ctx.strokeStyle = '#05080e'; ctx.lineJoin = 'round'; ctx.strokeText(s, x, y); }
  ctx.fillStyle = color; ctx.fillText(s, x, y); ctx.restore();
}
function chip(s, x, y, size, alpha = 1) {
  if (!s || alpha <= 0) return;
  ctx.save(); ctx.globalAlpha = alpha; ctx.font = `bold ${size}px ${FONT}`; const w = ctx.measureText(s).width, padX = size * 0.45, h = size * 1.42;
  ctx.fillStyle = C_RED; ctx.beginPath(); ctx.roundRect(x - w / 2 - padX, y - h / 2, w + 2 * padX, h, size * 0.22); ctx.fill();
  ctx.fillStyle = '#fff3e0'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(s, x, y + size * 0.04); ctx.restore();
}
const fmt = n => n.toLocaleString('en-US');
const pct = p => (p * 100).toFixed(1) + '%';
function project(v) { const q = v.clone().project(camera); return [(q.x + 1) / 2 * 1080, (1 - q.y) / 2 * 1920]; }
// fixed grain tiles
const grain = [...Array(6)].map((_, k) => { const c = document.createElement('canvas'); c.width = 270; c.height = 480; const x = c.getContext('2d'); const im = x.createImageData(270, 480); let s = 99 + k * 7;
  for (let i = 0; i < im.data.length; i += 4) { s = (s * 16807) % 2147483647; const v = s % 255; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; } x.putImageData(im, 0, 0); return c; });

function drawOverlay(t, st) {
  const fadeAll = 1 - smooth(20.15, 20.6, t);
  // tag
  text('THOUGHT EXPERIMENT · ONE SIMULATED ROOM', 540, 168, 23, C_CREAM, { alpha: 0.62 * (t < 20.6 ? 1 : 1 - smooth(20.6, 21.0, t)), spacing: 2, stroke: false });
  // hook
  const hookA = 1 - smooth(2.25, 2.6, t);
  if (hookA > 0) {
    text(typed('23 PEOPLE.', 0, 0.45, t), 540, 318, 96, C_CREAM, { alpha: hookA });
    text(typed('50% CHANCE TWO', 0.5, 1.15, t), 540, 422, 56, C_CREAM, { alpha: hookA });
    text(typed('SHARE A BIRTHDAY.', 1.1, 1.75, t), 540, 492, 56, C_GOLD, { alpha: hookA });
  }
  // centre counter, pinned to the projected ring centre
  const [cx, cy] = project(new T.Vector3(0, 0, 0));
  const cA = smooth(2.2, 2.6, t) * fadeAll;
  text('CHANCE OF A', cx, cy - 96, 25, C_CREAM, { alpha: 0.8 * cA, spacing: 3, stroke: false });
  text('SHARED BIRTHDAY', cx, cy - 64, 25, C_CREAM, { alpha: 0.8 * cA, spacing: 3, stroke: false });
  const hot = t > 11.75 && t < 15.2 ? 1 : 0;
  text(pct(st.p), cx, cy + 12, 104, st.p >= 0.5 ? C_GOLD : C_CREAM, { alpha: cA });
  // people / pairs below the ring
  const bA = cA, by = 1452;
  text('PEOPLE', 330, by, 27, C_CREAM, { alpha: 0.75 * bA, spacing: 4, stroke: false });
  text('PAIRS', 750, by, 27, C_TEAL, { alpha: 0.85 * bA, spacing: 4, stroke: false });
  text(String(st.n), 330, by + 62, 70, C_CREAM, { alpha: bA });
  text(fmt(st.pairs), 750, by + 62, 70, C_TEAL, { alpha: bA });
  // the reveal
  const rA = smooth(11.85, 12.05, t) * (1 - smooth(15.0, 15.35, t));
  if (rA > 0) {
    text(typed('23 PEOPLE', 11.85, 12.15, t), 540, 262, 58, C_CREAM, { alpha: rA });
    text(t > 12.25 ? 'MEANS' : '', 540, 322, 30, C_CREAM, { alpha: rA * 0.8, spacing: 4, stroke: false });
    chip(t > 12.45 ? typed('253 PAIRS', 12.45, 12.75, t) : '', 540, 392, 66, rA);
    text(typed('EVERY PAIR IS A CHANCE TO MATCH.', 13.0, 13.7, t), 540, 472, 30, C_CREAM, { alpha: rA });
  }
  // mark the twins on the ring: red circle on the slot, chip just inside the ring
  const mA = smooth(11.75, 11.85, t) * (1 - smooth(14.8, 15.2, t));
  if (mA > 0) {
    const mid = P3[7].clone().add(P3[22]).multiplyScalar(0.5), [sx, sy] = project(mid), pulse = 1 + 0.5 * Math.exp(-(t - 11.75) * 5);
    ctx.save(); ctx.globalAlpha = mA; ctx.strokeStyle = C_RED; ctx.lineWidth = 6; ctx.beginPath(); ctx.arc(sx, sy, 34 * pulse, 0, Math.PI * 2); ctx.stroke(); ctx.restore();
    const [kx, ky] = project(mid.clone().multiplyScalar(0.62));
    chip(t > 11.9 ? 'BOTH MAR 14' : '', Math.min(kx, 1080 - 150), ky - 70, 32, mA * smooth(11.9, 12.0, t));
  }
  // thesis
  const eA = smooth(18.15, 18.3, t) * fadeAll;
  if (eA > 0) {
    text(typed('COUNT THE PAIRS,', 18.2, 18.85, t), 540, 304, 72, C_CREAM, { alpha: eA });
    text(typed('NOT THE PEOPLE.', 18.95, 19.6, t), 540, 392, 72, C_GOLD, { alpha: eA });
  }
  // flash on the reveal, capped at 14%
  const fl = t >= 11.75 ? 0.14 * Math.exp(-(t - 11.75) * 14) : 0;
  if (fl > 0.005) { ctx.save(); ctx.fillStyle = `rgba(255,236,210,${fl})`; ctx.fillRect(0, 0, 1080, 1920); ctx.restore(); }
}

window.renderAt = function (t, frame = Math.round(t * 30)) {
  t = ((t % DUR) + DUR) % DUR;
  U.uTime.value = t;
  U.uImp.value = Math.pow(smooth(20.2, 21.0, t), 1.6);
  U.uGlow.value = Math.exp(-t / 0.55) + Math.pow(smooth(20.7, DUR, t), 2) + 0.9 * Math.exp(-Math.max(0, t - 11.75) * 2.2) * (t >= 11.75 ? 1 : 0) + 0.4 * Math.exp(-Math.max(0, t - 18.0) * 3) * (t >= 18 ? 1 : 0);
  const st = state(t);
  U.uP.value = st.p * (1 - smooth(20.2, 20.9, t));
  U.uThreadA.value = 0.6 * Math.min(1, 6 / Math.sqrt(Math.max(1, st.pairs)));
  placeCamera(t);
  renderer.render(scene, camera);
  // composite: base, soft bloom, vignette, grain, overlay
  ctx.save(); ctx.globalCompositeOperation = 'source-over'; ctx.fillStyle = '#060b13'; ctx.fillRect(0, 0, 1080, 1920);
  ctx.drawImage(film, 0, 0, 1080, 1920);
  ctx.globalCompositeOperation = 'lighter'; ctx.filter = 'blur(14px)'; ctx.globalAlpha = 0.55; ctx.drawImage(film, 0, 0, 1080, 1920);
  ctx.filter = 'blur(40px)'; ctx.globalAlpha = 0.35; ctx.drawImage(film, 0, 0, 1080, 1920); ctx.restore();
  ctx.save(); const v = ctx.createRadialGradient(540, 960, 380, 540, 960, 1150); v.addColorStop(0, 'rgba(4,8,14,0)'); v.addColorStop(1, 'rgba(4,8,14,0.72)'); ctx.fillStyle = v; ctx.fillRect(0, 0, 1080, 1920);
  ctx.globalAlpha = 0.045; ctx.globalCompositeOperation = 'overlay'; ctx.drawImage(grain[frame % 6], 0, 0, 1080, 1920); ctx.restore();
  drawOverlay(t, st);
  return st;
};
window.captureFrame = (t, frame) => { window.renderAt(t, frame); return out.toDataURL('image/jpeg', 0.95).split(',')[1]; };
window.renderAt(0.01);
window.ready = true;
