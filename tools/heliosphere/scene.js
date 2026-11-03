import * as THREE from "three";

export const T = { end: 34, earthIn: 22.6, earthOut: 27.4 };
const W = 1080, H = 1920, R0 = 10, E = 600; // E = x-offset of the Earth cutaway location
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const seg = (t, a, b) => clamp((t - a) / (b - a));
const sm = (x) => { x = clamp(x); return x * x * (3 - 2 * x); };
const eo3 = (x) => 1 - Math.pow(1 - clamp(x), 3);
const eio = (x) => { x = clamp(x); return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const lerp = (a, b, k) => a + (b - a) * k;
function rng(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
// comet-like heliosphere: nose toward +x, long tail toward -x
function shape(x, y, z) { const l = Math.hypot(x, y, z) || 1, c = x / l; return 1 - 0.1 * c + 0.62 * Math.pow(Math.max(0, -c), 2.2); }
const rbDir = (x, y, z) => R0 * shape(x, y, z);

function glowTex(inner, mid) {
  const c = document.createElement("canvas"); c.width = c.height = 256; const g = c.getContext("2d"), r = g.createRadialGradient(128, 128, 0, 128, 128, 128);
  r.addColorStop(0, inner); r.addColorStop(0.16, mid); r.addColorStop(0.5, "rgba(255,150,40,.10)"); r.addColorStop(1, "rgba(0,0,0,0)"); g.fillStyle = r; g.fillRect(0, 0, 256, 256); return new THREE.CanvasTexture(c);
}
function planetTex(base, seed, bands) {
  const c = document.createElement("canvas"); c.width = 256; c.height = 128; const g = c.getContext("2d"), r = rng(seed);
  g.fillStyle = base; g.fillRect(0, 0, 256, 128);
  for (let i = 0; i < 40; i++) { g.fillStyle = `rgba(${bands},${0.08 + r() * 0.18})`; if (i % 2) g.fillRect(0, r() * 128, 256, 3 + r() * 10); else { g.beginPath(); g.ellipse(r() * 256, r() * 128, 8 + r() * 30, 4 + r() * 12, 0, 0, 7); g.fill(); } }
  return new THREE.CanvasTexture(c);
}
function earthTex() {
  const c = document.createElement("canvas"); c.width = 512; c.height = 256; const g = c.getContext("2d"), r = rng(9);
  g.fillStyle = "#14407f"; g.fillRect(0, 0, 512, 256);
  for (let i = 0; i < 26; i++) { g.fillStyle = `rgba(${60 + r() * 40},${120 + r() * 50},${60 + r() * 30},.95)`; g.beginPath(); g.ellipse(r() * 512, 40 + r() * 176, 14 + r() * 50, 8 + r() * 26, r() * 3, 0, 7); g.fill(); }
  g.fillStyle = "rgba(240,248,255,.9)"; g.fillRect(0, 0, 512, 16); g.fillRect(0, 240, 512, 16);
  for (let i = 0; i < 40; i++) { g.fillStyle = "rgba(255,255,255,.28)"; g.beginPath(); g.ellipse(r() * 512, r() * 256, 10 + r() * 40, 3 + r() * 8, 0, 0, 7); g.fill(); }
  return new THREE.CanvasTexture(c);
}

// fresnel shell; colour blends orange nose -> blue flanks/tail using the object-space x of the normal
function bubbleShell(k, strength, power, opts) {
  const g = new THREE.IcosahedronGeometry(1, 6), p = g.attributes.position, n0 = g.attributes.normal;
  for (let i = 0; i < p.count; i++) { const x = p.getX(i), y = p.getY(i), z = p.getZ(i), s = R0 * k * shape(x, y, z); p.setXYZ(i, x * s, y * s, z * s); n0.setXYZ(i, x, y, z); }
  const m = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
    uniforms: { uS: { value: strength }, uP: { value: power }, uNose: { value: opts.nose }, uA: { value: new THREE.Color(opts.a) }, uB: { value: new THREE.Color(opts.b) } },
    vertexShader: "varying vec3 vN; varying vec3 vV; varying vec3 vO; void main(){ vec4 mv=modelViewMatrix*vec4(position,1.); vN=normalize(normalMatrix*normal); vV=normalize(-mv.xyz); vO=normalize(normal); gl_Position=projectionMatrix*mv; }",
    fragmentShader: "uniform float uS; uniform float uP; uniform float uNose; uniform vec3 uA; uniform vec3 uB; varying vec3 vN; varying vec3 vV; varying vec3 vO; void main(){ float f=1.-abs(dot(normalize(vN),normalize(vV))); float a=pow(f,uP); float nose=smoothstep(0.15,0.85,vO.x); vec3 col=mix(uB,uA,nose*uNose); float k=a*uS*(1.+0.9*nose*uNose)+0.02+0.05*nose*uNose; gl_FragColor=vec4(col*k,1.); }"
  });
  return new THREE.Mesh(g, m);
}
function latLong(k, color, opacity) {
  const pts = [], N = 96, P = (th, ph) => { const x = Math.cos(th), y = Math.sin(th) * Math.cos(ph), z = Math.sin(th) * Math.sin(ph), s = R0 * k * shape(x, y, z); return [x * s, y * s, z * s]; };
  for (let a = 1; a < 12; a++) { const th = a * Math.PI / 12; for (let i = 0; i < N; i++) pts.push(...P(th, i / N * 6.2832), ...P(th, (i + 1) / N * 6.2832)); }
  for (let a = 0; a < 24; a++) { const ph = a * Math.PI / 12; for (let i = 0; i < 48; i++) pts.push(...P(i / 48 * Math.PI, ph), ...P((i + 1) / 48 * Math.PI, ph)); }
  const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.Float32BufferAttribute(pts, 3));
  return new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color, transparent: true, opacity, depthWrite: false, blending: THREE.AdditiveBlending }));
}
function equatorTicks(k) { // degree ticks around the equatorial rim
  const pts = [];
  for (let i = 0; i < 180; i++) { const a = i / 180 * 6.2832, x = Math.cos(a), z = Math.sin(a), s = R0 * k * shape(x, 0, z), len = i % 5 === 0 ? 0.55 : 0.28; pts.push(x * s, 0, z * s, x * (s + len), 0, z * (s + len)); }
  const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.Float32BufferAttribute(pts, 3));
  return new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color: 0xcfe4ff, transparent: true, opacity: 0.55, depthWrite: false, blending: THREE.AdditiveBlending }));
}
function ringLine(r, color, opacity, y = 0, cx = 0) { const pts = []; for (let i = 0; i <= 160; i++) { const a = i / 160 * 6.2832; pts.push(new THREE.Vector3(cx + Math.cos(a) * r, y, Math.sin(a) * r)); } return new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({ color, transparent: true, opacity, depthWrite: false, blending: THREE.AdditiveBlending })); }

// streamlines of potential flow around a sphere of radius a, flow travelling toward -x
function streamlines(n, a, X0, X1, seed, bMin, bMax) {
  const r = rng(seed), out = [];
  for (let i = 0; i < n; i++) {
    const b = a * (bMin + (bMax - bMin) * Math.sqrt(r())), ang = r() * 6.2832; let p = [X0, b * Math.cos(ang), b * Math.sin(ang)]; const pts = [p.slice()], cum = [0];
    for (let s = 0; s < 1400; s++) {
      const rr = Math.hypot(...p), a3 = a * a * a, x = p[0];
      let v = [(1 + a3 / (2 * rr ** 3)) - 3 * a3 * x * x / (2 * rr ** 5), -3 * a3 * x * p[1] / (2 * rr ** 5), -3 * a3 * x * p[2] / (2 * rr ** 5)].map((c) => -c);
      const vl = Math.hypot(...v); v = v.map((c) => c / vl); p = p.map((c, j) => c + v[j] * 0.3);
      if (Math.hypot(...p) < a * 0.98) break; pts.push(p.slice()); cum.push(cum[cum.length - 1] + 0.3); if (p[0] < -X1) break;
    }
    out.push({ pts, cum, L: cum[cum.length - 1], off: r(), rate: 0.5 + r() * 0.35, kind: 0 });
  }
  return out;
}
function pathAt(sl, s, out, o) { // sample polyline by arclength
  const n = sl.pts.length - 1, f = clamp(s / sl.L) * n, i = Math.min(n - 1, Math.floor(f)), k = f - i, a = sl.pts[i], b = sl.pts[i + 1];
  out[o] = a[0] + (b[0] - a[0]) * k; out[o + 1] = a[1] + (b[1] - a[1]) * k; out[o + 2] = a[2] + (b[2] - a[2]) * k;
}
function streakSystem(list, color) {
  const N = list.length, pos = new Float32Array(N * 6), col = new Float32Array(N * 6), g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(pos, 3)); g.setAttribute("color", new THREE.BufferAttribute(col, 3));
  const m = new THREE.LineSegments(g, new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false })); m.frustumCulled = false;
  return { m, pos, col, g, N, color };
}

export function createScene(host) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
  renderer.setSize(W, H); renderer.setPixelRatio(1); renderer.toneMapping = THREE.NoToneMapping; renderer.outputColorSpace = THREE.SRGBColorSpace; renderer.setClearColor(0x020307, 1);
  host.appendChild(renderer.domElement);
  const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(38, W / H, 0.1, 12000);
  camera.setViewOffset(W, H, 0, 300, W, H);

  // stars
  let starPts; { const r = rng(7), n = 7000, pos = new Float32Array(n * 3), col = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) { const z = r() * 2 - 1, a = r() * 6.2832, q = Math.sqrt(1 - z * z), d = 4000; pos.set([q * Math.cos(a) * d, z * d, q * Math.sin(a) * d], i * 3); const b = 0.15 + Math.pow(r(), 2.2) * 0.8, k = r(); col.set(k < 0.2 ? [b * 0.8, b * 0.9, b] : k < 0.35 ? [b, b * 0.85, b * 0.6] : [b, b, b * 0.95], i * 3); }
    const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(pos, 3)); g.setAttribute("color", new THREE.BufferAttribute(col, 3));
    starPts = new THREE.Points(g, new THREE.PointsMaterial({ size: 2, sizeAttenuation: false, vertexColors: true, transparent: true, opacity: 0.9, depthWrite: false })); scene.add(starPts); }

  // ================= HELIOSPHERE LOCATION =================
  const helio = new THREE.Group(); scene.add(helio);
  const hp = bubbleShell(1.0, 0.85, 3.4, { nose: 1, a: 0xff8a2a, b: 0x2a6bff }), hpOuter = bubbleShell(1.035, 0.5, 5, { nose: 1, a: 0xffc26a, b: 0x6fb6ff });
  const ts = bubbleShell(0.74, 0.32, 3.6, { nose: 1, a: 0xffb454, b: 0x5aa9ff }), hw = bubbleShell(1.13, 0.0, 4, { nose: 1, a: 0xffa640, b: 0x2b4fa0 });
  const hpGrid = latLong(1.0, 0x7db4ff, 0.2), tsGrid = latLong(0.74, 0xffc47a, 0.08), ticks = equatorTicks(1.0);
  // hydrogen wall: a compressed glowing cap just ahead of the nose
  const wall = new THREE.Mesh(new THREE.SphereGeometry(R0 * 1.13, 64, 32, -0.0, 6.2832, 0, 0.62), new THREE.ShaderMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
    vertexShader: "varying vec3 vN; varying vec3 vV; varying float vA; void main(){ vec4 mv=modelViewMatrix*vec4(position,1.); vN=normalize(normalMatrix*normal); vV=normalize(-mv.xyz); vA=position.y; gl_Position=projectionMatrix*mv; }",
    fragmentShader: "varying vec3 vN; varying vec3 vV; varying float vA; void main(){ float f=1.-abs(dot(normalize(vN),normalize(vV))); float e=smoothstep(10.,0.,length(vec2(vA,0.))); gl_FragColor=vec4(vec3(1.,.6,.2)*(0.12+0.5*pow(f,2.))*0.9,1.); }" }));
  wall.rotation.z = -Math.PI / 2; wall.scale.set(1, 1, 1); wall.position.x = -R0 * 0.1; // cap centred on +x, squashed toward the nose
  helio.add(hp, ts, hpGrid, tsGrid, ticks);
  for (const k of [0.25, 0.5, 0.75]) helio.add(ringLine(R0 * k, 0x8fb8ff, 0.1));

  // sun: granulated shader photosphere, corona rays, prominences, anamorphic flare
  const NZ = `float h3(vec3 p){return fract(sin(dot(p,vec3(127.1,311.7,74.7)))*43758.5453);}
float n3(vec3 p){vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(mix(h3(i),h3(i+vec3(1,0,0)),f.x),mix(h3(i+vec3(0,1,0)),h3(i+vec3(1,1,0)),f.x),f.y),mix(mix(h3(i+vec3(0,0,1)),h3(i+vec3(1,0,1)),f.x),mix(h3(i+vec3(0,1,1)),h3(i+vec3(1,1,1)),f.x),f.y),f.z);}
float f3(vec3 p){float s=0.,a=.5;for(int i=0;i<5;i++){s+=a*n3(p);p=p*2.03+vec3(1.7,9.2,3.1);a*=.5;}return s;}`;
  const sunR = 0.62;
  const sunMat = new THREE.ShaderMaterial({ uniforms: { uT: { value: 0 } },
    vertexShader: `varying vec3 vP; varying vec3 vN; varying vec3 vV; void main(){ vec4 mv=modelViewMatrix*vec4(position,1.); vP=normalize(position); vN=normalize(normalMatrix*normal); vV=normalize(-mv.xyz); gl_Position=projectionMatrix*mv; }`,
    fragmentShader: `uniform float uT; varying vec3 vP; varying vec3 vN; varying vec3 vV; ${NZ}
void main(){ float mu=clamp(dot(normalize(vN),normalize(vV)),0.,1.); vec3 p=vP;
 float g1=f3(p*5.5+vec3(0.,uT*.18,0.)); float g2=f3(p*16.+vec3(uT*.35,0.,uT*.2));
 float cell=smoothstep(.30,.78,g1)*.55+g2*.45;
 float spot=smoothstep(.64,.74,n3(p*1.7+vec3(3.1,1.,uT*.02)))*smoothstep(.0,.6,1.-abs(p.y)*1.1);
 vec3 c1=vec3(.92,.30,.03), c2=vec3(1.,.66,.14), c3=vec3(1.,.96,.72);
 vec3 col=mix(c1,c2,cell); col=mix(col,c3,pow(cell,2.6)*.85); col=mix(col,vec3(.25,.07,.01),spot*.8);
 col*=(.38+.8*pow(mu,.5))*1.25; col+=vec3(.35,.1,.0)*pow(1.-mu,3.)*.6; gl_FragColor=vec4(col,1.); }` });
  const sunCore = new THREE.Mesh(new THREE.SphereGeometry(sunR, 64, 48), sunMat); scene.add(sunCore);
  const proms = []; for (let k = 0; k < 5; k++) { const pr = rng(60 + k), d = new THREE.Vector3(pr() * 2 - 1, (pr() * 2 - 1) * 0.6, pr() * 2 - 1).normalize(), sz = 0.55 + pr() * 0.9;
    const arc = new THREE.Mesh(new THREE.TorusGeometry(sunR * 0.2 * sz, sunR * 0.018, 8, 32, Math.PI), new THREE.MeshBasicMaterial({ color: 0xff7a1c, transparent: true, opacity: 0.8, blending: THREE.AdditiveBlending, depthWrite: false }));
    arc.position.copy(d).multiplyScalar(sunR * 0.99); arc.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), d); arc.rotateY(pr() * 6.28); sunCore.add(arc); proms.push(arc); }
  const sunGlow = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex("rgba(255,255,240,.9)", "rgba(255,200,100,.55)"), blending: THREE.AdditiveBlending, depthWrite: false, transparent: true })); scene.add(sunGlow);
  const rayTex = (seed, n) => { const c = document.createElement("canvas"); c.width = c.height = 512; const g = c.getContext("2d"), r = rng(seed); g.translate(256, 256); g.globalCompositeOperation = "lighter";
    for (let i = 0; i < n; i++) { const a = r() * 6.2832, len = 110 + r() * 146, wd = 0.015 + r() * 0.04, gr = g.createLinearGradient(0, 0, Math.cos(a) * len, Math.sin(a) * len); gr.addColorStop(0, "rgba(255,232,170,.8)"); gr.addColorStop(1, "rgba(255,150,40,0)");
      g.fillStyle = gr; g.beginPath(); g.moveTo(Math.cos(a - wd) * 24, Math.sin(a - wd) * 24); g.lineTo(Math.cos(a) * len, Math.sin(a) * len); g.lineTo(Math.cos(a + wd) * 24, Math.sin(a + wd) * 24); g.closePath(); g.fill(); }
    return new THREE.CanvasTexture(c); };
  const raysA = new THREE.Sprite(new THREE.SpriteMaterial({ map: rayTex(81, 64), blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, opacity: 0.85 })), raysB = new THREE.Sprite(new THREE.SpriteMaterial({ map: rayTex(82, 40), blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, opacity: 0.55 })); scene.add(raysA, raysB);
  const flareTex = (() => { const c = document.createElement("canvas"); c.width = 512; c.height = 64; const g = c.getContext("2d"); g.translate(256, 32); g.scale(1, 0.125); const gr = g.createRadialGradient(0, 0, 0, 0, 0, 256); gr.addColorStop(0, "rgba(255,240,210,.9)"); gr.addColorStop(0.2, "rgba(255,190,110,.35)"); gr.addColorStop(1, "rgba(255,150,60,0)"); g.fillStyle = gr; g.fillRect(-256, -256, 512, 512); return new THREE.CanvasTexture(c); })();
  const sunFlare = new THREE.Sprite(new THREE.SpriteMaterial({ map: flareTex, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, opacity: 0.6 })); scene.add(sunFlare);
  const sunLight = new THREE.PointLight(0xfff0c8, 3.2, 0, 0); scene.add(sunLight); scene.add(new THREE.AmbientLight(0x5a6a9a, 2.2));
  // planets
  const PN = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"], AU = [0.39, 0.72, 1, 1.52, 5.2, 9.5, 19.2, 30], PR = [1.25, 1.75, 2.3, 2.95, 3.9, 4.85, 5.7, 6.5];
  const PS = [0.14, 0.24, 0.3, 0.19, 0.6, 0.52, 0.36, 0.36], PC = [["#8d8780", 1, "70,64,60"], ["#d9c08a", 2, "180,150,100"], ["#2c6ab6", 3, "255,255,255"], ["#b5573a", 4, "120,50,30"], ["#c9a778", 5, "120,80,50"], ["#d8c08a", 6, "150,120,80"], ["#7fd0d6", 7, "60,150,160"], ["#3f63d8", 8, "20,40,140"]];
  const anchors = {}, v3 = (x, y, z) => new THREE.Vector3(x, y, z);
  const sys = new THREE.Group(); sys.rotation.z = 1.05; scene.add(sys); const SE = new THREE.Euler(0, 0, 1.05);
  const TL = new THREE.TextureLoader(), tex = (f) => { const t = TL.load("./assets/planets/" + f); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t; };
  const MAPS = ["mercurymap.jpg", "venusmap.jpg", "earth_atmos_2048.jpg", "marsmap1k.jpg", "jupitermap.jpg", "saturnmap.jpg", "uranusmap.jpg", "neptunemap.jpg"];
  const TILT = [0.0, 3.09, 0.41, 0.44, 0.05, 0.47, 1.71, 0.49], RSP = [0.4, -0.3, 1.8, 1.7, 3.2, 3.0, 2.2, 2.2];
  const planets = PN.map((n, i) => { const m = new THREE.Mesh(new THREE.SphereGeometry(PS[i], 64, 48), new THREE.MeshStandardMaterial({ map: tex(MAPS[i]), roughness: 1, metalness: 0, emissive: 0x080a12 })); m.rotation.order = "ZXY"; m.rotation.z = TILT[i]; sys.add(m); return m; });
  const RIMC = [0x000000, 0xffd9a0, 0x6fb0ff, 0xff9a6a, 0xe6c898, 0xf2e2b4, 0x8fe8f0, 0x5f8fff], RIMI = [0, 0.9, 1.5, 0.5, 0.7, 0.7, 1.0, 1.2];
  planets.forEach((m, i) => { if (!RIMI[i]) return; m.add(new THREE.Mesh(new THREE.SphereGeometry(PS[i] * 1.07, 48, 32), new THREE.ShaderMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, uniforms: { uC: { value: new THREE.Color(RIMC[i]) }, uI: { value: RIMI[i] } },
    vertexShader: "varying vec3 vN; varying vec3 vV; void main(){ vec4 mv=modelViewMatrix*vec4(position,1.); vN=normalize(normalMatrix*normal); vV=normalize(-mv.xyz); gl_Position=projectionMatrix*mv; }",
    fragmentShader: "uniform vec3 uC; uniform float uI; varying vec3 vN; varying vec3 vV; void main(){ float f=pow(1.-clamp(dot(normalize(vN),normalize(vV)),0.,1.),2.4); gl_FragColor=vec4(uC,f*uI); }" }))); });
  { const g = new THREE.RingGeometry(PS[5] * 1.35, PS[5] * 2.4, 96, 1), p = g.attributes.position, uv = g.attributes.uv; for (let i = 0; i < p.count; i++) { const r = Math.hypot(p.getX(i), p.getY(i)); uv.setXY(i, (r - PS[5] * 1.35) / (PS[5] * 1.05), 0.5); }
    const ring = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ map: tex("saturnringcolor.jpg"), alphaMap: tex("saturnringpattern.gif"), transparent: true, side: THREE.DoubleSide, depthWrite: false })); ring.rotation.x = Math.PI / 2; planets[5].add(ring); }
  // Earth gets a thin cloud layer
  { const cl = new THREE.Mesh(new THREE.SphereGeometry(PS[2] * 1.02, 48, 32), new THREE.MeshStandardMaterial({ color: 0xffffff, alphaMap: tex("earthcloudmaptrans.jpg"), transparent: true, opacity: 0.4, depthWrite: false, roughness: 1 })); planets[2].add(cl); }
  const orbitG = new THREE.Group(); sys.add(orbitG); PR.forEach((r) => orbitG.add(ringLine(r, 0xdbe8ff, 0.75)));
  // helical trails behind each planet (planets move through space with the Sun)
  const TRN = 420, TRLEN = [8, 8, 8, 8, 8, 8, 8, 8], trails = PN.map((n, i) => { const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(TRN * 3), 3)); g.setAttribute("color", new THREE.BufferAttribute(new Float32Array(TRN * 3), 3));
    const l = new THREE.Line(g, new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false })); l.frustumCulled = false; scene.add(l); return l; });
  const OM = AU.map((a) => 3.8 / Math.sqrt(a)), ang = (i, t) => i * 1.9 + t * OM[i];
  const trailPts = trails.map((l) => { const p = new THREE.Points(l.geometry, new THREE.PointsMaterial({ size: 2.6, sizeAttenuation: false, vertexColors: true, transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending, depthWrite: false })); p.frustumCulled = false; scene.add(p); return p; });
  // comet-tail wakes along each orbit, the Moon and Jupiter's four big moons
  const ARCN = 80, ARCC = [[0.8, 0.78, 0.72], [1, 0.85, 0.55], [0.45, 0.7, 1], [1, 0.55, 0.35], [1, 0.8, 0.55], [1, 0.9, 0.6], [0.5, 0.95, 1], [0.4, 0.55, 1]];
  const arcs = PN.map(() => { const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(ARCN * 3), 3)); g.setAttribute("color", new THREE.BufferAttribute(new Float32Array(ARCN * 3), 3));
    const l = new THREE.Line(g, new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false })); l.frustumCulled = false; sys.add(l); return l; });
  const moon = new THREE.Mesh(new THREE.SphereGeometry(0.075, 32, 24), new THREE.MeshStandardMaterial({ map: tex("moon_1024.jpg"), roughness: 1 })); sys.add(moon);
  // the Sun's own straight path: it leads, the planets weave along beside it in stretched waves
  const sunTrail = (() => { const n = 80, pos = new Float32Array(n * 3), col = new Float32Array(n * 3); for (let i = 0; i < n; i++) { const u = i / (n - 1); pos.set([-u * 15, 0, 0], i * 3); const f = Math.pow(1 - u, 1.4); col.set([1 * f, 0.82 * f, 0.4 * f], i * 3); }
    const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(pos, 3)); g.setAttribute("color", new THREE.BufferAttribute(col, 3));
    const l = new THREE.Line(g, new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false })); l.frustumCulled = false; scene.add(l); return l; })();
  const JM = [[0.8, 0.045, 7.0, 0xd8c26a], [1.05, 0.04, 4.6, 0xd2cabb], [1.38, 0.065, 3.1, 0x8f8578], [1.8, 0.055, 1.9, 0x6b6359]].map(([or, rd, sp, c]) => { const m = new THREE.Mesh(new THREE.SphereGeometry(rd, 20, 14), new THREE.MeshStandardMaterial({ color: c, roughness: 1 })); sys.add(m); return { m, or, sp }; });
  // Sun's motion arrow
  const arrow = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, R0 * 1.3, 8), new THREE.MeshBasicMaterial({ color: 0xffe9a0, transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending, depthWrite: false })); arrow.rotation.z = -Math.PI / 2; arrow.position.set(0.6 + R0 * 0.65, 0, 0); scene.add(arrow);
  const head = new THREE.Mesh(new THREE.ConeGeometry(0.26, 0.8, 16), new THREE.MeshBasicMaterial({ color: 0xffe9a0 })); head.rotation.z = -Math.PI / 2; head.position.set(R0 * 1.3 + 0.75, 0, 0); scene.add(head);

  // solar wind
  const NW = 520, wr = rng(21), wdir = [], wph = [], wsp = [];
  for (let i = 0; i < NW; i++) { const z = wr() * 2 - 1, a = wr() * 6.2832, q = Math.sqrt(1 - z * z); wdir.push([q * Math.cos(a), z, q * Math.sin(a)]); wph.push(wr()); wsp.push(0.18 + wr() * 0.12); }
  const wind = streakSystem(new Array(NW), [1, 0.78, 0.35]); scene.add(wind.m);
  // cosmic rays deflected around the bubble (potential-flow streamlines) + a few that get through
  const RAYS = streamlines(280, R0 * 1.06, R0 * 2.6, R0 * 3.4, 55, 0.25, 1.5);
  { const r = rng(88); for (let i = 0; i < 22; i++) { const a = r() * 6.2832, b = r() * R0 * 0.8, y = b * Math.cos(a), z = b * Math.sin(a), pts = [[R0 * 2.6, y, z], [R0 * 0.3, y * 0.4, z * 0.4]]; RAYS.push({ pts, cum: [0, 24], L: 24, off: r(), rate: 0.4 + r() * 0.25, kind: 1 }); } }



  // ---- Sagittarius A* + Milky Way backdrop (camera-attached; opens on a hero close-up, then pulls back to reveal the whole galaxy)
  const bh = new THREE.Group(); scene.add(bh); const bhBill = new THREE.Group(); bh.add(bhBill);
  const BHR = 30, DIN = BHR * 1.12, DOUT = BHR * 1.9;
  bh.add(new THREE.Mesh(new THREE.SphereGeometry(BHR, 64, 48), new THREE.MeshBasicMaterial({ color: 0x000000 })));
  const NA = 3200, ar = rng(404), aR = [], aP = [], aT = [];
  for (let i = 0; i < NA; i++) { const u = ar(); aR.push(DIN + Math.pow(u, 1.2) * (DOUT - DIN)); aP.push(ar() * 6.2832); aT.push((ar() - 0.5) * 0.9); }
  const aPos = new Float32Array(NA * 3), aCol = new Float32Array(NA * 3), aG = new THREE.BufferGeometry(); aG.setAttribute("position", new THREE.BufferAttribute(aPos, 3)); aG.setAttribute("color", new THREE.BufferAttribute(aCol, 3));
  const disk = new THREE.Points(aG, new THREE.PointsMaterial({ size: 1.9, sizeAttenuation: false, vertexColors: true, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false })); disk.frustumCulled = false;
  const diskG = new THREE.Group(); diskG.rotation.set(Math.PI / 2 + 0.3, 0, 0.12); diskG.add(disk); bh.add(diskG);
  const diskMat = new THREE.ShaderMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, uniforms: { uT: { value: 0 }, uIn: { value: DIN }, uOut: { value: DOUT }, uI: { value: 0.95 } },
    vertexShader: `varying vec2 vP; void main(){ vP=position.xy; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader: `uniform float uT,uIn,uOut,uI; varying vec2 vP;
float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float n2(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y);}
float f2(vec2 p){float s=0.,a=.5;for(int i=0;i<5;i++){s+=a*n2(p);p*=2.03;a*=.5;}return s;}
void main(){ float r=length(vP); float rn=(r-uIn)/(uOut-uIn); if(rn<0.||rn>1.) discard; float a=atan(vP.y,vP.x);
 float om=2.4*pow(1.-rn*.8,1.5); float aa=a+uT*om*.45;
 float n=f2(vec2(aa*3.3,rn*24.))*.6+f2(vec2(aa*9.+3.,rn*64.))*.4;
 float fil=smoothstep(.22,.86,n);
 float dop=.22+1.4*pow(.5+.5*cos(a),1.7);
 float it=pow(1.-rn,1.6)*(.3+1.6*fil)*dop*smoothstep(0.,.05,rn);
 vec3 hot=vec3(1.,.94,.8), mid=vec3(1.,.55,.16), cold=vec3(.5,.14,.05);
 vec3 col=mix(hot,mid,smoothstep(0.,.35,rn)); col=mix(col,cold,smoothstep(.3,.95,rn));
 gl_FragColor=vec4(col*uI,it); }` });
  const diskMesh = new THREE.Mesh(new THREE.RingGeometry(DIN, DOUT, 192, 6), diskMat); diskMesh.rotation.x = -Math.PI / 2; diskG.add(diskMesh);
  // gravitationally lensed image of the far side of the disk, arching over and under the shadow
  const lensMat = new THREE.ShaderMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, uniforms: { uT: { value: 0 }, uR: { value: BHR } },
    vertexShader: `varying vec2 vP; void main(){ vP=position.xy; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader: `uniform float uT,uR; varying vec2 vP;
float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float n2(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y);}
void main(){ float r=length(vP)/uR; if(r<1.||r>2.6) discard; float a=atan(vP.y,vP.x);
 float top=pow(.5+.5*cos(a-1.15),2.0), bot=.28*pow(.5+.5*cos(a-1.15-3.1416),3.);
 float n=.55+.75*n2(vec2(a*6.+uT*.5,r*34.));
 float it=exp(-(r-1.)*5.2)*(top+bot+.06)*n*smoothstep(1.,1.012,r);
 vec3 col=mix(vec3(1.,.96,.84),vec3(1.,.5,.14),clamp((r-1.)*1.6,0.,1.));
 gl_FragColor=vec4(col*0.9,it*0.75); }` });
  const lens = new THREE.Mesh(new THREE.RingGeometry(BHR * 0.99, BHR * 2.65, 192, 4), lensMat); bhBill.add(lens);
  const photon = new THREE.Mesh(new THREE.RingGeometry(BHR * 1.0, BHR * 1.018, 160), new THREE.MeshBasicMaterial({ color: 0xffe9bd, transparent: true, opacity: 0.95, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide })); bhBill.add(photon);
  const bhGlow = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex("rgba(255,200,120,.0)", "rgba(255,170,70,.26)"), blending: THREE.AdditiveBlending, depthWrite: false, transparent: true })); bhGlow.scale.setScalar(BHR * 6); bh.add(bhGlow);
  const bhFlare = new THREE.Sprite(new THREE.SpriteMaterial({ map: flareTex, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, opacity: 0.4 })); bhFlare.scale.set(BHR * 18, BHR * 0.8, 1); bhBill.add(bhFlare);
  // ---- the Milky Way, fixed in the world: a golden disc of concentric rings, Sagittarius A* at its heart, the Sun's galactic path through it
  const gs = rng(909), XH = new THREE.Vector3(1, 0, 0), GPv = new THREE.Vector3(0, 0.09, -0.99).normalize(), GNv = new THREE.Vector3().crossVectors(XH, GPv).normalize();
  const GC = new THREE.Vector3(-8, 0, 0).addScaledVector(GPv, 62), GQ = new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().makeBasis(XH, GPv, GNv));
  const galW = new THREE.Group(); galW.position.copy(GC); galW.quaternion.copy(GQ); scene.add(galW); bh.position.copy(GC); bh.quaternion.copy(GQ);
  const galSpin = new THREE.Group(); galW.add(galSpin); const SPN = -Math.sign(GNv.clone().cross(GC.clone().negate()).x) || 1, DGv = GNv.clone().multiplyScalar(0.77).addScaledVector(GPv, -0.64).normalize();
  const coreGlow = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex("rgba(255,214,140,.0)", "rgba(255,190,100,.55)"), blending: THREE.AdditiveBlending, depthWrite: false, transparent: true })); coreGlow.scale.setScalar(150); galW.add(coreGlow);
  { const N = 70000, pos = new Float32Array(N * 3), col = new Float32Array(N * 3); let n = 0, guard = 0;
    while (n < N && guard++ < N * 20) { const r = 10 + Math.pow(gs(), 1.2) * 100, ring = 0.5 + 0.5 * Math.cos(r * 1.1), arm0 = 0.5 + 0.5 * Math.cos(2 * (Math.atan2(0, 1) + 0)); if (gs() > 0.55 + 0.45 * ring) continue;
      const ph = gs() * 6.2832, zz2 = (gs() + gs() - 1) * (0.5 + r * 0.012), cl = 0.12 + 0.88 * Math.pow(0.5 + 0.5 * Math.cos(2 * (ph - 2.2 * Math.log(r / 10))), 2.2), b = Math.min(1, (0.75 + 0.25 * ring) * cl * (1.25 - r / 125) * 1.15), k = Math.min(1, (r - 10) / 100);
      pos.set([Math.cos(ph) * r, Math.sin(ph) * r, zz2], n * 3); col.set([b, b * (0.84 - 0.2 * k), b * (0.55 - 0.3 * k)], n * 3); n++; }
    const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(pos, 3)); g.setAttribute("color", new THREE.BufferAttribute(col, 3));
    galSpin.add(new THREE.Points(g, new THREE.PointsMaterial({ size: 1.5, sizeAttenuation: false, vertexColors: true, transparent: true, opacity: 0.95, blending: THREE.AdditiveBlending, depthWrite: false }))); }
  const SR = GC.length(), tu1 = GC.clone().negate().normalize(), tu2 = new THREE.Vector3().crossVectors(GNv, tu1); if (tu2.x < 0) tu2.negate();
  const trkP = (al, o) => o.copy(GC).addScaledVector(tu1, SR * Math.cos(al)).addScaledVector(tu2, SR * Math.sin(al));
  const TA0 = -1.2, TSP = 2.8;
  const trackG = (() => { const n = 260, pos = new Float32Array(n * 3), col = new Float32Array(n * 3), v = new THREE.Vector3(); for (let i = 0; i < n; i++) { const al = TA0 + i / (n - 1) * TSP; trkP(al, v); pos.set([v.x, v.y, v.z], i * 3); const f = Math.pow(Math.max(0, 1 - Math.abs(al - 0.1) / 1.5), 1.1); col.set([1.0 * f, 0.8 * f, 0.38 * f], i * 3); }
    const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(pos, 3)); g.setAttribute("color", new THREE.BufferAttribute(col, 3));
    const l = new THREE.Line(g, new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false })); l.frustumCulled = false; scene.add(l); return l; })();
  const beadTex = glowTex("rgba(255,244,210,1)", "rgba(255,200,100,.7)"), beads = Array.from({ length: 14 }, () => { const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: beadTex, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true })); scene.add(sp); return sp; });
  // the Sun's wavy path: a hatched ribbon through the Sun
  const RIBN = 72, mkG = (n) => { const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(n * 3), 3)); return g; };
  const ribHatch = new THREE.LineSegments(mkG(RIBN * 2), new THREE.LineBasicMaterial({ color: 0xc8501e, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false })), ribCurve = new THREE.Line(mkG(160), new THREE.LineBasicMaterial({ color: 0xff8a3c, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false }));
  ribHatch.frustumCulled = ribCurve.frustumCulled = false; scene.add(ribHatch); scene.add(ribCurve);
  const _wp = new THREE.Vector3();
  const heliDot = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex("rgba(255,250,225,1)", "rgba(255,214,110,.85)"), blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, depthTest: false })); heliDot.visible = false; scene.add(heliDot);
  // Parker-spiral arms of the Sun's magnetic field
  const spiral = new THREE.Group(); scene.add(spiral);
  for (let k = 0; k < 6; k++) { const pts = [], n = 200; for (let i = 0; i < n; i++) { const r = 0.85 + i / (n - 1) * R0 * 0.72, ph = k * 1.0472 + r * 0.8, y = 0.45 * Math.sin(2 * ph) * (r / 7); pts.push(new THREE.Vector3(Math.cos(ph) * r, y, Math.sin(ph) * r)); }
    spiral.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({ color: 0x66e0d0, transparent: true, opacity: 0.5, blending: THREE.AdditiveBlending, depthWrite: false }))); }
  // distant stars streaming past (the Sun's motion)
  { const r = rng(777); for (let i = 0; i < 170; i++) { const a = r() * 6.2832, d = 22 + r() * 90, y = Math.cos(a) * d * 0.7, z = Math.sin(a) * d; RAYS.push({ pts: [[160, y, z], [-160, y, z]], cum: [0, 320], L: 320, off: r(), rate: 0.5 + r() * 0.5, kind: 2 }); } }

  const rays = streakSystem(RAYS, [0.42, 0.55, 0.65]); scene.add(rays.m);

  // ================= EARTH LOCATION =================
  const earthG = new THREE.Group(); scene.add(earthG);
  const earth = new THREE.Mesh(new THREE.SphereGeometry(1.6, 48, 32), new THREE.MeshStandardMaterial({ map: tex('earth_atmos_2048.jpg'), roughness: 0.9, emissive: 0x0b1a33, emissiveIntensity: 1 })); earthG.add(earth);
  earthG.add(new THREE.Mesh(new THREE.SphereGeometry(1.63, 48, 32), new THREE.MeshStandardMaterial({ color: 0xffffff, alphaMap: tex('earthcloudmaptrans.jpg'), transparent: true, opacity: 0.4, depthWrite: false })));
  { const L = new THREE.PointLight(0xfff0d0, 3.4, 0, 0); L.position.set(30, 2, 12); earthG.add(L); L.intensity = 1.4; }
  // magnetopause + bow shock shells (lathe about the Sun-Earth axis)
  const lathe = (r0, tail, ex) => { const pts = []; for (let i = 0; i <= 90; i++) { const th = i / 90 * 2.45, r = Math.min(tail, r0 * Math.pow(2 / (1 + Math.cos(th)), ex)); pts.push(new THREE.Vector2(r * Math.sin(th), r * Math.cos(th))); } return new THREE.LatheGeometry(pts, 72); };
  const fres = (c1, c2, s, p) => new THREE.ShaderMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, uniforms: { a: { value: new THREE.Color(c1) }, b: { value: new THREE.Color(c2) } },
    vertexShader: "varying vec3 vN; varying vec3 vV; varying float vX; void main(){ vec4 mv=modelViewMatrix*vec4(position,1.); vN=normalize(normalMatrix*normal); vV=normalize(-mv.xyz); vX=position.y; gl_Position=projectionMatrix*mv; }",
    fragmentShader: `uniform vec3 a; uniform vec3 b; varying vec3 vN; varying vec3 vV; varying float vX; void main(){ float f=1.-abs(dot(normalize(vN),normalize(vV))); float k=pow(f,${p.toFixed(1)})*${s.toFixed(2)}+0.03; gl_FragColor=vec4(mix(b,a,smoothstep(-8.,10.,vX))*k,1.); }` });
  const mpause = new THREE.Mesh(lathe(9.7, 42, 0.55), fres(0x7ad0ff, 0x2f6dff, 1.5, 3.6)); mpause.rotation.z = -Math.PI / 2; earthG.add(mpause);
  const bow = new THREE.Mesh(lathe(13.4, 52, 0.62), fres(0xffb040, 0xff7a20, 1.3, 4.2)); bow.rotation.z = -Math.PI / 2; earthG.add(bow);
  // dipole field loops (axis tilted ~11 deg)
  { const pts = [], tilt = 11 * Math.PI / 180;
    for (const L of [1.7, 2.4, 3.3, 4.6, 6.2]) for (let a = 0; a < 14; a++) { const az = a / 14 * 6.2832; let prev = null; for (let i = 0; i <= 40; i++) { const lam = -1.45 + i / 40 * 2.9, r = L * Math.cos(lam) ** 2, cx = r * Math.cos(lam), cy = r * Math.sin(lam);
        let x = cx * Math.cos(az), z = cx * Math.sin(az), y = cy; const x2 = x * Math.cos(tilt) - y * Math.sin(tilt), y2 = x * Math.sin(tilt) + y * Math.cos(tilt); const q = [x2, y2, z]; if (prev) pts.push(...prev, ...q); prev = q; } }
    const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.Float32BufferAttribute(pts, 3)); earthG.add(new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color: 0x66c8ff, transparent: true, opacity: 0.4, blending: THREE.AdditiveBlending, depthWrite: false }))); }
  const eHalo = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex('rgba(120,190,255,.9)', 'rgba(60,130,255,.35)'), blending: THREE.AdditiveBlending, depthWrite: false, transparent: true })); eHalo.scale.setScalar(7); earthG.add(eHalo);
  const EW = streamlines(380, 11.0, 24, 40, 303, 0.05, 2.4), ewind = streakSystem(EW, [1, 0.62, 0.2]); earthG.add(ewind.m);

  // ================= camera =================
  const keys = [ // t, az, el, d, tx, ty, tz
    [0, 92, 14, 62, -4, 0, 0], [6, 80, 18, 58, -4, 0, 0], [14, 106, 12, 54, -5, 0, 0], [18, 118, 20, 54, -3, 0, 0], [21, 100, 26, 50, 3, 0, 0], [26, 70, 30, 34, 1, 0, 0], [29.5, 40, 22, 13, 0, 0, 0], [34, 90, 18, 64, -4, 0, 0], [34.01, 90, 18, 64, -4, 0, 0]];
  const cr = (p0, p1, p2, p3, u) => 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u * u * u);
  function helioCam(t) {
    let i = 0; while (i < keys.length - 3 && t >= keys[i + 1][0]) i++;
    const k0 = keys[Math.max(0, i - 1)], k1 = keys[i], k2 = keys[i + 1], k3 = keys[Math.min(keys.length - 1, i + 2)], u = clamp((t - k1[0]) / (k2[0] - k1[0]));
    return [1, 2, 3, 4, 5, 6].map((j) => cr(k0[j], k1[j], k2[j], k3[j], u));
  }
  const wE = (t) => sm(seg(t, 19.2, 22.8)) * (1 - sm(seg(t, 27.2, 29.6)));
  const NE = new THREE.Vector3(0, 1, 0).applyEuler(SE), tB = new THREE.Vector3(), dB = new THREE.Vector3(), tmpV = new THREE.Vector3();
  const MSC = 0.03, DE = 2.1;
  function cam(t, w, EP, sunDir, zz = 0) {
    const c = helioCam(t), a = c[0] * Math.PI / 180, e = c[1] * Math.PI / 180;
    tB.set(c[3], c[4], c[5]); dB.set(Math.cos(e) * Math.cos(a), Math.sin(e), Math.cos(e) * Math.sin(a));
    tmpV.copy(tB).lerp(EP, w).lerp(GC, Math.pow(zz, 1.8)); const dir = dB.clone().lerp(NE, w).lerp(DGv, zz).normalize(), d = Math.exp(lerp(lerp(Math.log(c[2]), Math.log(DE), w), Math.log(520), zz));
    camera.up.set(0, 1, 0).lerp(sunDir, w).normalize();
    camera.position.copy(tmpV).addScaledVector(dir, d); camera.lookAt(tmpV);
  }

  // ================= render =================
  
  function render(t) {
    const inEarth = false, w = wE(t);
    const aE = ang(2, t), EPv = v3(Math.cos(aE) * PR[2], 0, Math.sin(aE) * PR[2]).applyEuler(SE), sunDirV = EPv.clone().multiplyScalar(-1).normalize();
    const zz = 1 - sm(seg(t, 3.0, 8.0)); cam(t, w, EPv, sunDirV, zz); camera.rotateZ(0.012 * Math.sin(t * 0.55)); camera.updateMatrixWorld(true);
    const hf = (1 - sm(seg(w, 0.15, 0.6))); helio.visible = hf > 0.01; hp.material.uniforms.uS.value = 0.85 * hf; ts.material.uniforms.uS.value = 0.32 * hf; hpGrid.material.opacity = 0.2 * hf; tsGrid.material.opacity = 0.08 * hf; ticks.material.opacity = 0.55 * hf;
    const msc = MSC * sm(seg(w, 0.35, 0.9)); earthG.visible = msc > 0.0004; ewind.m.visible = earthG.visible;
    { const X = sunDirV.clone(), Z = NE.clone(), Y = new THREE.Vector3().crossVectors(Z, X).normalize(); earthG.position.copy(EPv); earthG.setRotationFromMatrix(new THREE.Matrix4().makeBasis(X, Y, Z)); earthG.scale.setScalar(Math.max(msc, 1e-4));
      const M = (lx, ly) => EPv.clone().addScaledVector(X, lx * msc).addScaledVector(Y, ly * msc);
      anchors["Bow shock"] = M(11.6, -8.2); anchors.Magnetopause = M(5.7, 9.9); anchors.Magnetotail = M(-16, 0); anchors.Earth = EPv.clone(); anchors["Sun "] = M(17, 0); }
    const wf = 1 - w;
    const infl = 1 + 0.004 * Math.sin(t * 1.3); helio.scale.setScalar(infl);
    const pu = 1 + 0.04 * Math.sin(t * 2.4);
    sunGlow.scale.setScalar(lerp(4.6, 1.2, w) * pu); sunCore.scale.setScalar(lerp(1, 0.2, w)); sunMat.uniforms.uT.value = t;
    raysA.scale.setScalar(lerp(8.2, 1.4, w) * (1 + 0.03 * Math.sin(t * 1.7))); raysA.material.rotation = t * 0.06; raysB.scale.setScalar(lerp(6.2, 1.1, w)); raysB.material.rotation = -t * 0.09 + 1;
    sunFlare.scale.set(lerp(15, 3, w), lerp(0.9, 0.2, w), 1); sunFlare.material.opacity = 0.5 + 0.12 * Math.sin(t * 3.1);
    proms.forEach((a, k) => { a.material.opacity = 0.55 + 0.35 * Math.sin(t * 1.3 + k * 1.7); });
    // planets + trails
    const TS_ = 2.2; // how fast the Sun travels in the trail (units per unit of trail age)
    planets.forEach((m, i) => { const a = ang(i, t), r = PR[i], om = OM[i]; m.position.set(Math.cos(a) * r, 0, Math.sin(a) * r); m.rotation.y = t * RSP[i]; if (i !== 2) { m.scale.setScalar(Math.max(0.001, 1 - sm(seg(w, 0.05, 0.6)))); m.visible = w < 0.62; } if (i === 2) { const sh = lerp(1, 0.048 / PS[2], sm(seg(w, 0.3, 0.8))); m.scale.setScalar(sh); m.visible = w < 0.85; } anchors[PN[i]] = m.position.clone().applyEuler(SE);
      const pa = trails[i].geometry.attributes.position, ca = trails[i].geometry.attributes.color, Lt = TRLEN[i], tf = sm(seg(t, 0.2, 2.0)) * (t < 27 ? 1 : 1 - 0.5 * sm(seg(t, 27, 30)));
      for (let j = 0; j < TRN; j++) { const age = j / (TRN - 1) * Lt, aa = a - age * om, q = v3(Math.cos(aa) * r, 0, Math.sin(aa) * r).applyEuler(SE), f = Math.pow(1 - j / TRN, 0.7) * tf; pa.setXYZ(j, q.x - age * TS_, q.y, q.z); ca.setXYZ(j, 1.0 * f, 0.78 * f, 0.38 * f); }
      pa.needsUpdate = true; ca.needsUpdate = true; });
    orbitG.visible = w < 0.5;
    { const vis = w < 0.3, af = sm(seg(t, 0.3, 2.2)) * (1 - sm(seg(w, 0.02, 0.3)));
      arcs.forEach((l, i) => { l.visible = vis; if (!vis) return; const a = ang(i, t), r = PR[i], ap = l.geometry.attributes.position, ac = l.geometry.attributes.color, cc = ARCC[i];
        for (let j = 0; j < ARCN; j++) { const u = j / (ARCN - 1), aa = a - u * 1.3, f = Math.pow(1 - u, 1.6) * af; ap.setXYZ(j, Math.cos(aa) * r, 0, Math.sin(aa) * r); ac.setXYZ(j, cc[0] * f, cc[1] * f, cc[2] * f); } ap.needsUpdate = true; ac.needsUpdate = true; });
      const pe = planets[2].position, ma2 = t * 2.6; moon.position.set(pe.x + Math.cos(ma2) * 0.5, 0.03 * Math.sin(ma2 * 2), pe.z + Math.sin(ma2) * 0.5); moon.rotation.y = ma2; moon.visible = vis;
      const pj = planets[4].position; JM.forEach((o, k) => { const a2 = t * o.sp + k * 1.7; o.m.position.set(pj.x + Math.cos(a2) * o.or, 0.02 * Math.sin(a2), pj.z + Math.sin(a2) * o.or); o.m.visible = vis; }); } arrow.visible = head.visible = w < 0.3 && !(t > 26.5 && t < 31.5); trails.forEach((l) => (l.visible = w < 0.3)); trailPts.forEach((l) => (l.visible = w < 0.3)); sunTrail.visible = false;
    { const tv = w < 0.3, tf = sm(seg(t, 0.3, 1.8)) * (1 - sm(seg(w, 0.02, 0.3))); trackG.visible = tv; trackG.material.opacity = tf; const q = new THREE.Vector3();
      beads.forEach((b, i) => { b.visible = tv; if (!tv) return; let al = ((i / beads.length) * TSP - 0.7 * t) % TSP; if (al < 0) al += TSP; al += TA0; trkP(al, q); b.position.copy(q); const f = Math.pow(Math.max(0, 1 - Math.abs(al - 0.1) / 1.5), 1.1) * tf; b.material.opacity = f; b.scale.setScalar(2.2 * (0.5 + 0.5 * f) * (1 + 3.5 * zz)); });
      ribHatch.visible = ribCurve.visible = tv; const ro = 0.5 * tf; ribHatch.material.opacity = ro * 0.8; ribCurve.material.opacity = ro; const rA = 2.2, rk = 0.32, rv = 3.2, hp_ = ribHatch.geometry.attributes.position, cp_ = ribCurve.geometry.attributes.position, off = Math.sin(rk * rv * t);
      for (let i = 0; i < RIBN; i++) { const x = -15 + 17 * i / (RIBN - 1), y = rA * (Math.sin(rk * (x + rv * t)) - off); hp_.setXYZ(i * 2, x, 0, 0); hp_.setXYZ(i * 2 + 1, x, y, 0); }
      for (let i = 0; i < 160; i++) { const x = -15 + 17 * i / 159, y = rA * (Math.sin(rk * (x + rv * t)) - off); cp_.setXYZ(i, x, y, 0); } hp_.needsUpdate = cp_.needsUpdate = true; }
    arrow.material.opacity = 0.7 + 0.25 * Math.sin(t * 4);
    // solar wind
    const wI = sm(seg(t, 0, 0.5)) * (1 - w);
    for (let i = 0; i < NW; i++) {
      const d = wdir[i], Rb = rbDir(d[0], d[1], d[2]) * 0.98, ph = (wph[i] + t * wsp[i]) % 1, rh = 0.85 + ph * (Rb - 0.85), far = rh > Rb * 0.74, len = far ? 0.45 : 1.3, rt = Math.max(0.8, rh - len);
      const f = wI * (1 - sm((ph - 0.85) / 0.15)) * (far ? 0.4 : 0.7) * (0.5 + 0.5 * sm(ph / 0.12)), o = i * 6, w = wind.pos, c = wind.col;
      w[o] = d[0] * rh; w[o + 1] = d[1] * rh; w[o + 2] = d[2] * rh; w[o + 3] = d[0] * rt; w[o + 4] = d[1] * rt; w[o + 5] = d[2] * rt;
      c[o] = 1 * f; c[o + 1] = 0.78 * f; c[o + 2] = 0.35 * f; c[o + 3] = c[o + 4] = c[o + 5] = 0;
    }
    wind.g.attributes.position.needsUpdate = true; wind.g.attributes.color.needsUpdate = true;
    // cosmic rays (helio)
    const rI = sm(seg(t, 0, 0.8)) * (1 - w);
    for (let i = 0; i < rays.N; i++) {
      const r = RAYS[i], o = i * 6, ph = (r.off + t * r.rate * 0.12) % 1, s = ph * r.L;
      pathAt(r, s, rays.pos, o); pathAt(r, s - (r.kind === 2 ? 14 : 2.6), rays.pos, o + 3);
      const f = rI * (r.kind === 2 ? 0.55 : r.kind ? 0.6 * (1 - sm((s - 14) / 8)) : 1.5) * (r.kind === 2 ? 1 : sm(s / 3)) * (1 - sm((ph - 0.9) / 0.1));
      rays.col[o] = rays.color[0] * f; rays.col[o + 1] = rays.color[1] * f; rays.col[o + 2] = rays.color[2] * f; rays.col[o + 3] = rays.col[o + 4] = rays.col[o + 5] = 0;
    }
    rays.g.attributes.position.needsUpdate = true; rays.g.attributes.color.needsUpdate = true;
    // earth wind
    if (w > 0.02) {
      earth.rotation.y = t * 0.7;
      for (let i = 0; i < ewind.N; i++) { const r = EW[i], o = i * 6, ph = (r.off + t * r.rate * 0.14) % 1, s = ph * r.L; pathAt(r, s, ewind.pos, o); pathAt(r, s - 2.0, ewind.pos, o + 3);
        const f = 0.95 * sm(s / 4) * (1 - sm((ph - 0.9) / 0.1)); ewind.col[o] = f; ewind.col[o + 1] = 0.62 * f; ewind.col[o + 2] = 0.2 * f; ewind.col[o + 3] = ewind.col[o + 4] = ewind.col[o + 5] = 0; }
      ewind.g.attributes.position.needsUpdate = true; ewind.g.attributes.color.needsUpdate = true;
    }
    // Sagittarius A* + Milky Way
    { const hc = helioCam(t), fwd = new THREE.Vector3(), rt = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 0), upc = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 1); camera.getWorldDirection(fwd);
      const gv = w < 0.85; galW.visible = bh.visible = gv; bh.scale.setScalar(Math.max(0.001, 0.2 * (1 + 0.8 * zz) * (1 - sm(w)))); coreGlow.material.opacity = 0.55 + 0.45 * zz; heliDot.visible = false; heliDot.material.opacity = Math.min(1, zz * 1.6); heliDot.scale.setScalar(camera.position.length() * 0.016 * (0.85 + 0.15 * Math.sin(t * 4)));
      diskMat.uniforms.uT.value = t; lensMat.uniforms.uT.value = t; galSpin.rotation.z = SPN * t * 0.3; bhBill.quaternion.copy(GQ).invert().multiply(camera.quaternion);
      photon.material.opacity = 0.4 + 0.05 * Math.sin(t * 2.1); bhFlare.material.opacity = 0.34 + 0.08 * Math.sin(t * 1.3);
      for (let i = 0; i < NA; i++) { const r = aR[i], k = (r - DIN) / (DOUT - DIN), ph = aP[i] + t * 2.6 / Math.pow(r / BHR, 1.5) * 1.6, c = Math.cos(ph), sn = Math.sin(ph), dop = 0.35 + Math.pow(0.5 + 0.5 * c, 1.5), b = Math.pow(1 - k, 0.9) * dop * 1.1;
        aPos[i * 3] = c * r; aPos[i * 3 + 1] = aT[i] * (1 + k * 2.4); aPos[i * 3 + 2] = sn * r; aCol[i * 3] = Math.min(1, b); aCol[i * 3 + 1] = Math.min(1, b * (0.5 + 0.45 * (1 - k))); aCol[i * 3 + 2] = Math.min(1, b * (0.15 + 0.6 * Math.pow(1 - k, 3))); }
      aG.attributes.position.needsUpdate = true; aG.attributes.color.needsUpdate = true;
      galW.updateMatrixWorld(true); anchors["Sagittarius A*"] = GC.clone(); anchors.SunOrbit = trkP(0.95, new THREE.Vector3()); anchors.MilkyWay = galW.localToWorld(new THREE.Vector3(26, -30, 0)); }
    starPts.material.opacity = 0.85; anchors.SunDot = v3(0, 0, 0);
    spiral.rotation.y = t * 0.9; spiral.visible = !inEarth; sunCore.rotation.y = t * 0.55;
    // anchors for labels
    anchors.Sun = v3(0, 0, 0);
    const hpA = (dx, dy, dz) => { const l = Math.hypot(dx, dy, dz), x = dx / l, y = dy / l, z = dz / l, s = rbDir(x, y, z); return v3(x * s, y * s, z * s); };
    anchors.Heliopause = hpA(0.45, 0.5, 0.75); anchors["Termination shock"] = hpA(-0.2, 0.45, 0.85).multiplyScalar(0.74); anchors["Hydrogen wall"] = hpA(1, 0.34, 0.12).multiplyScalar(1.13);
    anchors.Arrow = v3(R0 * 0.78, 0, 0); anchors.Heliotail = hpA(-1, 0.1, 0.25).multiplyScalar(0.9);
    { const sc = SYSG.scale.x; SYSG.scale.setScalar(1 + 2.8 * zz); const sc2 = SYSG.scale.x; for (const k of Object.keys(anchors)) { if (["Sagittarius A*", "SunOrbit", "MilkyWay", "SunDot"].includes(k)) continue; anchors[k] = anchors[k].clone().multiplyScalar(sc2); } }
    renderer.render(scene, camera);
  }
  const SYSG = new THREE.Group(); { const keep = new Set([galW, bh, starPts, trackG, heliDot, ...beads]); scene.children.slice().forEach((o) => { if (!keep.has(o) && !o.isLight) SYSG.add(o); }); scene.add(SYSG); }
  const pv = new THREE.Vector3();
  function proj(v) { pv.copy(v); pv.project(camera); return [(pv.x * 0.5 + 0.5) * W, (-pv.y * 0.5 + 0.5) * H, pv.z < 1]; }
  return { render, proj, anchors, renderer, camera };
}
