// Vault B: key stills. Three.js r170 in headless Chromium (swiftshader).
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { BokehPass } from 'three/addons/postprocessing/BokehPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { Reflector } from 'three/addons/objects/Reflector.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

const q = new URLSearchParams(location.search);
const W = +(q.get('w') || 1080), H = +(q.get('h') || 1920);
const renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H);
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.0;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// ---------- seeded random ----------
let seed = 7; const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
const rr = (a, b) => a + (b - a) * rnd();
const setSeed = s => { seed = s; };

// ---------- procedural textures ----------
function canvasTex(w, h, draw, srgb = true, rep = [1, 1]) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d'); draw(g, w, h);
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rep[0], rep[1]);
  if (srgb) t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t;
}
// value noise
function makeNoise(n = 256, sd = 1) {
  setSeed(sd); const a = new Float32Array(n * n); for (let i = 0; i < a.length; i++) a[i] = rnd();
  const s = (x, y) => a[((y % n + n) % n) * n + ((x % n + n) % n)];
  return (x, y) => { const xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi; const u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf);
    return (s(xi, yi) * (1 - u) + s(xi + 1, yi) * u) * (1 - v) + (s(xi, yi + 1) * (1 - u) + s(xi + 1, yi + 1) * u) * v; };
}
const N1 = makeNoise(256, 3), N2 = makeNoise(256, 11);
function fbm(x, y, oct = 5, N = N1) { let f = 0, a = 0.5, s = 1; for (let i = 0; i < oct; i++) { f += a * N(x * s, y * s); s *= 2.03; a *= 0.5; } return f; }

function stoneTextures(size, base, var1, speck, sd) {
  // returns {map, bump, rough}
  const img = new ImageData(size, size), bmp = new ImageData(size, size);
  setSeed(sd);
  for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) {
    const i = (y * size + x) * 4;
    const nx = x / size * 8, ny = y / size * 8;
    let f = fbm(nx + sd, ny, 6); const g = fbm(nx * 3 + 9, ny * 3, 3, N2);
    let sp = rnd() < speck ? rr(-0.35, 0.25) : 0;
    const v = 0.75 + (f - 0.5) * var1 + (g - 0.5) * 0.25 + sp;
    img.data[i] = Math.min(255, base[0] * v); img.data[i + 1] = Math.min(255, base[1] * v); img.data[i + 2] = Math.min(255, base[2] * v); img.data[i + 3] = 255;
    const b = Math.max(0, Math.min(255, (f * 0.7 + g * 0.3) * 255 + sp * 120)); bmp.data[i] = bmp.data[i + 1] = bmp.data[i + 2] = b; bmp.data[i + 3] = 255;
  }
  const mk = (d, srgb) => canvasTex(size, size, g => g.putImageData(d, 0, 0), srgb);
  return { map: mk(img, true), bump: mk(bmp, false) };
}

// ---------- materials ----------
const GOLD = new THREE.Color().setRGB(1.0, 0.72, 0.30);
const goldMat = (rough = 0.22, tint = GOLD) => new THREE.MeshPhysicalMaterial({ color: tint, metalness: 1, roughness: rough });
let coinBump;
function coinFaceTex() {
  return canvasTex(256, 256, (g, w, h) => {
    g.fillStyle = '#808080'; g.fillRect(0, 0, w, h);
    g.strokeStyle = '#d8d8d8'; g.lineWidth = 10; g.beginPath(); g.arc(128, 128, 112, 0, 7); g.stroke();
    g.strokeStyle = '#b0b0b0'; g.lineWidth = 4; g.beginPath(); g.arc(128, 128, 92, 0, 7); g.stroke();
    // dotted ring
    g.fillStyle = '#c8c8c8'; for (let i = 0; i < 40; i++) { const a = i / 40 * Math.PI * 2; g.beginPath(); g.arc(128 + Math.cos(a) * 102, 128 + Math.sin(a) * 102, 3, 0, 7); g.fill(); }
    // conch-like motif (Travancore coins carry a conch)
    g.fillStyle = '#d0d0d0'; g.beginPath(); g.ellipse(128, 132, 34, 52, 0.3, 0, 7); g.fill();
    g.fillStyle = '#909090'; g.beginPath(); g.ellipse(134, 128, 14, 32, 0.3, 0, 7); g.fill();
    g.fillStyle = '#d0d0d0'; g.beginPath(); g.moveTo(100, 180); g.lineTo(156, 180); g.lineTo(128, 200); g.fill();
  }, false);
}

// ---------- geometry builders ----------
function coinGeo() {
  // lathe profile with raised rim
  const p = [[0, 0.03], [0.40, 0.03], [0.44, 0.042], [0.5, 0.04], [0.505, 0], [0.5, -0.04], [0.44, -0.042], [0.40, -0.03], [0, -0.03]].map(([x, y]) => new THREE.Vector2(x, y));
  const g = new THREE.LatheGeometry(p, 40);
  // planar uv for faces
  const pos = g.attributes.position, uv = g.attributes.uv;
  for (let i = 0; i < pos.count; i++) uv.setXY(i, pos.getX(i) + 0.5, pos.getZ(i) + 0.5);
  return g;
}
function addCoinHeap(group, { cx = 0, cz = 0, R = 3, Hh = 1.6, n = 5000, scale = 0.12, rough = 0.2, sd = 1, under = true }) {
  setSeed(sd);
  const h = (x, z) => { const r2 = ((x - cx) ** 2 + (z - cz) ** 2) / (R * R); return Hh * Math.exp(-r2 * 2.2) * (1 + 0.12 * (N2(x * 2 + 5, z * 2) - 0.5)); };
  if (under) { // gold mound so gaps are gold, not black
    const mg = new THREE.PlaneGeometry(R * 3.2, R * 3.2, 120, 120); mg.rotateX(-Math.PI / 2);
    const p = mg.attributes.position; for (let i = 0; i < p.count; i++) { const x = p.getX(i) + cx, z = p.getZ(i) + cz; p.setXYZ(i, x, h(x, z) - scale * 0.25, z); }
    mg.computeVertexNormals(); const m = new THREE.Mesh(mg, goldMat(0.45, new THREE.Color().setRGB(0.8, 0.52, 0.18))); m.receiveShadow = true; group.add(m);
  }
  const geo = coinGeo(); const mat = goldMat(rough); mat.bumpMap = coinBump; mat.bumpScale = 1.2;
  const im = new THREE.InstancedMesh(geo, mat, n); im.castShadow = true; im.receiveShadow = true;
  const M = new THREE.Matrix4(), Q = new THREE.Quaternion(), E = new THREE.Euler(), up = new THREE.Vector3(0, 1, 0), nrm = new THREE.Vector3();
  const col = new THREE.Color();
  for (let i = 0; i < n; i++) {
    const a = rnd() * Math.PI * 2, r = R * 1.25 * Math.sqrt(rnd()); const x = cx + Math.cos(a) * r, z = cz + Math.sin(a) * r;
    const e = 0.02; nrm.set(h(x - e, z) - h(x + e, z), 2 * e, h(x, z - e) - h(x, z + e)).normalize();
    Q.setFromUnitVectors(up, nrm); const tilt = new THREE.Quaternion().setFromEuler(E.set(rr(-0.7, 0.7), rr(0, 6.28), rr(-0.7, 0.7))); Q.multiply(tilt);
    const s = scale * rr(0.85, 1.15);
    M.compose(new THREE.Vector3(x, h(x, z) + rr(-0.02, 0.05) * Hh * 0.2, z), Q, new THREE.Vector3(s, s * rr(0.9, 1.2), s));
    im.setMatrixAt(i, M); const k = rr(0.82, 1.05); col.setRGB(k, k * rr(0.95, 1.02), k * rr(0.85, 1.0)); im.setColorAt(i, col);
  }
  group.add(im); return h;
}
function latheObj(profile, mat, seg = 48) { const g = new THREE.LatheGeometry(profile.map(([x, y]) => new THREE.Vector2(x, y)), seg); const m = new THREE.Mesh(g, mat); m.castShadow = m.receiveShadow = true; return m; }
function kalasam(mat) { // pot-shaped finial
  return latheObj([[0, 0], [0.32, 0.02], [0.36, 0.1], [0.2, 0.18], [0.22, 0.24], [0.42, 0.42], [0.46, 0.62], [0.38, 0.82], [0.2, 0.92], [0.24, 0.98], [0.14, 1.04], [0.1, 1.2], [0.16, 1.32], [0.08, 1.48], [0.03, 1.7], [0, 1.78]], mat);
}
function goldPot(mat) { return latheObj([[0, 0], [0.28, 0], [0.3, 0.05], [0.52, 0.3], [0.58, 0.55], [0.5, 0.8], [0.3, 0.95], [0.26, 1.02], [0.34, 1.1], [0.36, 1.14], [0, 1.14]], mat); }
function crown(mat, gemMats) {
  const g = new THREE.Group();
  const band = latheObj([[0.5, 0], [0.52, 0.02], [0.53, 0.25], [0.56, 0.3], [0.56, 0.34], [0.5, 0.34], [0.49, 0.02]], mat, 64); g.add(band);
  for (let i = 0; i < 10; i++) {
    const a = i / 10 * Math.PI * 2;
    const sp = latheObj([[0, 0], [0.09, 0.0], [0.07, 0.12], [0.11, 0.2], [0.05, 0.36], [0.02, 0.5], [0, 0.56]], mat, 16);
    sp.position.set(Math.cos(a) * 0.52, 0.32, Math.sin(a) * 0.52); sp.rotation.z = -Math.cos(a) * 0.15; sp.rotation.x = Math.sin(a) * 0.15; g.add(sp);
    const gem = new THREE.Mesh(new THREE.SphereGeometry(0.055, 16, 12), gemMats[i % gemMats.length]); gem.scale.set(0.6,0.78,0.36); gem.position.set(Math.cos(a + 0.31) * 0.555, 0.16, Math.sin(a + 0.31) * 0.555); gem.lookAt(0, 0.16, 0); g.add(gem);
  }
  const top = latheObj([[0, 0], [0.18, 0], [0.12, 0.25], [0.16, 0.4], [0.06, 0.55], [0, 0.7]], mat, 32); top.position.y = 0.45; g.add(top);
  // dome arches
  for (let i = 0; i < 4; i++) { const t = new THREE.Mesh(new THREE.TorusGeometry(0.5, 0.025, 8, 40, Math.PI), mat); t.rotation.y = i * Math.PI / 4; t.position.y = 0.32; t.scale.y = 0.7; g.add(t); }
  return g;
}
function chain(mat, curve, linkR = 0.06, n = 80) {
  const g = new THREE.Group(); const geo = new THREE.TorusGeometry(linkR, linkR * 0.28, 8, 20); geo.scale(1.5, 1, 1);
  const im = new THREE.InstancedMesh(geo, mat, n); im.castShadow = true;
  const M = new THREE.Matrix4(), up = new THREE.Vector3(1, 0, 0);
  for (let i = 0; i < n; i++) { const t = i / (n - 1); const p = curve.getPointAt(t), d = curve.getTangentAt(t);
    const Q = new THREE.Quaternion().setFromUnitVectors(up, d); Q.multiply(new THREE.Quaternion().setFromAxisAngle(up, i % 2 ? Math.PI / 2 : 0)); M.compose(p, Q, new THREE.Vector3(1, 1, 1)); im.setMatrixAt(i, M); }
  g.add(im); return g;
}
function gemMaterials() {
  return [new THREE.MeshPhysicalMaterial({ color: 0xb00018, roughness: 0.05, metalness: 0.0, clearcoat: 1, emissive: 0x300004, sheen: 0 }),
    new THREE.MeshPhysicalMaterial({ color: 0x0a7a32, roughness: 0.05, clearcoat: 1, emissive: 0x01200a }),
    new THREE.MeshPhysicalMaterial({ color: 0xffffff, roughness: 0.0, clearcoat: 1, emissive: 0x222222 })];
}

// ---------- lamp (Kerala nilavilakku) ----------
function nilavilakku(mat) {
  const g = new THREE.Group();
  g.add(latheObj([[0, 0], [0.5, 0], [0.52, 0.04], [0.42, 0.08], [0.3, 0.12], [0.12, 0.2], [0.1, 0.3], [0.14, 0.34], [0.08, 0.4], [0.07, 1.2], [0.11, 1.24], [0.07, 1.3], [0.06, 1.5], [0.1, 1.55], [0, 1.56]], mat));
  const dish = latheObj([[0, 0], [0.12, 0], [0.42, 0.08], [0.46, 0.14], [0.44, 0.16], [0.1, 0.06], [0, 0.06]], mat); dish.position.y = 1.5; g.add(dish);
  const fin = latheObj([[0, 0], [0.08, 0], [0.12, 0.1], [0.06, 0.25], [0.02, 0.4], [0, 0.45]], mat, 24); fin.position.y = 1.6; g.add(fin);
  return g;
}
function flameMesh(lean = 0) {
  const g = new THREE.Group();
  const prof = []; for (let i = 0; i <= 20; i++) { const t = i / 20; prof.push(new THREE.Vector2(0.055 * Math.sin(Math.PI * Math.pow(t, 0.55)) * (1 - t * 0.3), t * 0.32)); }
  const geo = new THREE.LatheGeometry(prof, 24); const p = geo.attributes.position;
  for (let i = 0; i < p.count; i++) { const y = p.getY(i); p.setX(i, p.getX(i) + lean * y * y * 3.2); p.setY(i, y * (1 - Math.abs(lean) * 0.25)); }
  geo.computeVertexNormals();
  const core = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: new THREE.Color().setRGB(6, 3.2, 0.9), transparent: true, opacity: 0.95, blending: THREE.AdditiveBlending, depthWrite: false }));
  const outer = new THREE.Mesh(geo.clone().scale(1.6, 1.25, 1.6), new THREE.MeshBasicMaterial({ color: new THREE.Color().setRGB(2.2, 0.7, 0.08), transparent: true, opacity: 0.35, blending: THREE.AdditiveBlending, depthWrite: false }));
  const blue = new THREE.Mesh(new THREE.SphereGeometry(0.03, 12, 8), new THREE.MeshBasicMaterial({ color: new THREE.Color().setRGB(0.3, 0.5, 2), transparent: true, opacity: 0.4, blending: THREE.AdditiveBlending, depthWrite: false }));
  blue.position.y = 0.01; g.add(outer, core, blue); return g;
}
function glowSprite(color, size, opacity = 1) {
  if (!glowSprite.tex) glowSprite.tex = canvasTex(128, 128, (g) => { const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.25, 'rgba(255,255,255,0.45)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, 128, 128); }, true);
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowSprite.tex, color, transparent: true, opacity, blending: THREE.AdditiveBlending, depthWrite: false })); s.scale.set(size, size, 1); return s;
}
function lampLight(scene, pos, intensity = 30, dist = 30, shadow = true, lean = 0, withLamp = true, lampMat) {
  const grp = new THREE.Group(); grp.position.copy(pos);
  if (withLamp) { const l = nilavilakku(lampMat); grp.add(l); }
  const f = flameMesh(lean); f.position.y = withLamp ? 1.62 : 0; f.position.x = withLamp ? 0.36 : 0; grp.add(f);
  const s = glowSprite(new THREE.Color(1, 0.6, 0.25), 0.9, 0.55); s.position.copy(f.position).add(new THREE.Vector3(lean * 0.1, 0.12, 0)); grp.add(s);
  const L = new THREE.PointLight(new THREE.Color(1, 0.62, 0.3), intensity, dist, 1.6); L.position.copy(f.position).add(new THREE.Vector3(0, 0.15, 0));
  if (shadow) { L.castShadow = true; L.shadow.mapSize.set(1024, 1024); L.shadow.radius = 6; L.shadow.bias = -0.002; L.shadow.camera.near = 0.05; }
  grp.add(L); scene.add(grp); return grp;
}
// dust motes
function dust(scene, center, size, n = 1500, color = new THREE.Color(1, 0.75, 0.45), ps = 0.03, op = 0.6) {
  const g = new THREE.BufferGeometry(); const a = new Float32Array(n * 3); for (let i = 0; i < n; i++) { a[i * 3] = center.x + rr(-1, 1) * size.x; a[i * 3 + 1] = center.y + rr(-1, 1) * size.y; a[i * 3 + 2] = center.z + rr(-1, 1) * size.z; }
  g.setAttribute('position', new THREE.BufferAttribute(a, 3));
  if (!dust.tex) dust.tex = canvasTex(64, 64, (c) => { const gr = c.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); c.fillStyle = gr; c.fillRect(0, 0, 64, 64); });
  const p = new THREE.Points(g, new THREE.PointsMaterial({ size: ps, map: dust.tex, color, transparent: true, opacity: op, blending: THREE.AdditiveBlending, depthWrite: false, sizeAttenuation: true }));
  scene.add(p); return p;
}
// volumetric light shaft (additive cone with soft falloff)
function shaft(scene, from, to, r0, r1, color, op = 0.25) {
  const len = from.distanceTo(to); const geo = new THREE.CylinderGeometry(r0, r1, len, 48, 1, true); geo.translate(0, -len / 2, 0);
  const mat = new THREE.ShaderMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
    uniforms: { c: { value: color }, op: { value: op } },
    vertexShader: 'varying vec3 vN; varying vec3 vV; varying float vY; void main(){ vec4 mv = modelViewMatrix*vec4(position,1.); vN = normalize(normalMatrix*normal); vV = normalize(-mv.xyz); vY = uv.y; gl_Position = projectionMatrix*mv; }',
    fragmentShader: 'uniform vec3 c; uniform float op; varying vec3 vN; varying vec3 vV; varying float vY; void main(){ float f = pow(abs(dot(vN,vV)),2.0); gl_FragColor = vec4(c*f*op*smoothstep(0.0,0.35,vY)*(0.35+0.65*vY),1.); }' });
  const m = new THREE.Mesh(geo, mat); m.position.copy(from); m.lookAt(to); m.rotateX(-Math.PI / 2); scene.add(m); return m;
}

// ---------- environment (warm vault reflections) ----------
function warmEnv(intensity = 1, sky = false) {
  const s = new THREE.Scene();
  s.background = sky ? new THREE.Color(0.5, 0.45, 0.5) : new THREE.Color(0.05, 0.03, 0.02);
  const add = (pos, r, c) => { const m = new THREE.Mesh(new THREE.SphereGeometry(r, 16, 12), new THREE.MeshBasicMaterial({ color: c })); m.position.copy(pos); s.add(m); };
  const warm = new THREE.Color(1, 0.6, 0.28).multiplyScalar(14 * intensity), dim = new THREE.Color(0.9, 0.5, 0.2).multiplyScalar(2.5 * intensity);
  add(new THREE.Vector3(3, 2, 2), 0.6, warm); add(new THREE.Vector3(-4, 1.5, -1), 0.5, warm); add(new THREE.Vector3(0.5, 3, -4), 0.45, warm); add(new THREE.Vector3(-1, 4, 3), 0.8, dim);
  add(new THREE.Vector3(2, -0.5, -3), 1.2, dim); add(new THREE.Vector3(-3, 0, 3.5), 1.0, dim);
  // floor/wall bounce: large dim warm shell
  const shell = new THREE.Mesh(new THREE.SphereGeometry(9, 24, 16), new THREE.MeshBasicMaterial({ color: new THREE.Color(0.35, 0.2, 0.1).multiplyScalar(intensity), side: THREE.BackSide })); s.add(shell);
  const pm = new THREE.PMREMGenerator(renderer); const rt = pm.fromScene(s, 0.02); return rt.texture;
}

// ---------- corridor + door ----------
let stone, iron;
function initMats() {
  coinBump = coinFaceTex();
  const st = stoneTextures(512, [150, 122, 96], 0.6, 0.015, 4); // laterite/granite warm
  stone = new THREE.MeshStandardMaterial({ map: st.map, bumpMap: st.bump, bumpScale: 3, roughness: 0.88, color: 0xffffff });
  const ir = (() => { const size = 512; const img = new ImageData(size, size), bmp = new ImageData(size, size); setSeed(9);
    for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) { const i = (y * size + x) * 4; const f = fbm(x / 48, y / 48, 6), g = fbm(x / 9 + 3, y / 9, 3, N2); const rust = Math.max(0, f - 0.55) * 3;
      img.data[i] = 30 + rust * 55 + g * 14; img.data[i + 1] = 27 + rust * 26 + g * 11; img.data[i + 2] = 25 + rust * 10 + g * 9; img.data[i + 3] = 255; const b = (f * 0.5 + g * 0.5) * 255; bmp.data[i] = bmp.data[i + 1] = bmp.data[i + 2] = b; bmp.data[i + 3] = 255; }
    return { map: canvasTex(size, size, c => c.putImageData(img, 0, 0)), bump: canvasTex(size, size, c => c.putImageData(bmp, 0, 0), false) }; })();
  iron = new THREE.MeshStandardMaterial({ map: ir.map, bumpMap: ir.bump, bumpScale: 2, metalness: 0.75, roughness: 0.48 });
}
function stoneBlocks(scene, x0, x1, y0, y1, z, normal, bw = 1.1, bh = 0.55, depth = 0.3, sd = 1) {
  // a wall of slightly irregular blocks in plane; normal: 'z' wall facing +z at z, 'x+' facing +x etc
  setSeed(sd); const geos = [];
  for (let y = y0, row = 0; y < y1; y += bh, row++) {
    const off = (row % 2) * bw * 0.5;
    for (let x = x0 - off; x < x1; x += bw) {
      const xa = Math.max(x, x0), xb = Math.min(x + bw, x1); if (xb - xa < 0.08) continue;
      const w = xb - xa - 0.03, h = bh - 0.03; const g = new THREE.BoxGeometry(w, h, depth * rr(0.8, 1.2));
      const uv = g.attributes.uv; const ox = rnd(), oy = rnd(); for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * 0.35 * w / bw + ox, uv.getY(i) * 0.2 + oy);
      g.translate((xa + xb) / 2, y + bh / 2, rr(-0.02, 0.02)); geos.push(g);
    }
  }
  const m = new THREE.Mesh(mergeGeometries(geos), stone); m.castShadow = m.receiveShadow = true;
  if (normal === 'z') m.position.z = z; if (normal === 'x+') { m.rotation.y = Math.PI / 2; m.position.x = z; } if (normal === 'x-') { m.rotation.y = -Math.PI / 2; m.position.x = z; }
  scene.add(m); return m;
}
function floor(scene, x0, x1, z0, z1, y = 0, s = 1.2) {
  setSeed(21); const geos = [];
  for (let x = x0; x < x1; x += s) for (let z = z0; z < z1; z += s) { const g = new THREE.BoxGeometry(s - 0.03, 0.2, s - 0.03); const uv = g.attributes.uv; const ox = rnd(), oy = rnd(); for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * 0.4 + ox, uv.getY(i) * 0.4 + oy); g.translate(x + s / 2, y - 0.1 + rr(-0.01, 0.01), z + s / 2); geos.push(g); }
  const m = new THREE.Mesh(mergeGeometries(geos), stone); m.receiveShadow = true; scene.add(m); return m;
}
function cobra(mat, flip = 1) {
  // relief cobra: coiled tail, rising body, spread hood, head
  const g = new THREE.Group();
  const pts = []; // coil at base then S-rise
  for (let i = 0; i <= 40; i++) { const t = i / 40; const a = t * Math.PI * 3.2; pts.push(new THREE.Vector3(Math.cos(a) * (0.38 - t * 0.12) * flip, -1.35 + Math.sin(a) * 0.12 + t * 0.08, 0.04 + 0.03 * Math.sin(a))); }
  for (let i = 1; i <= 30; i++) { const t = i / 30; pts.push(new THREE.Vector3((0.26 * Math.cos(t * Math.PI * 1.5) - 0.05) * flip, -1.25 + t * 1.45, 0.06 + t * 0.05)); }
  const curve = new THREE.CatmullRomCurve3(pts);
  const tube = new THREE.TubeGeometry(curve, 300, 0.1, 16, false);
  // taper the tail
  const p = tube.attributes.position; const cnt = 301 * 17;
  for (let i = 0; i < p.count; i++) { const seg = Math.floor(i / 17) / 300; if (seg < 0.25) { const c = curve.getPointAt(seg); const k = 0.25 + 0.75 * (seg / 0.25); p.setXYZ(i, c.x + (p.getX(i) - c.x) * k, c.y + (p.getY(i) - c.y) * k, c.z + (p.getZ(i) - c.z) * k); } }
  tube.computeVertexNormals(); const body = new THREE.Mesh(tube, mat); body.castShadow = body.receiveShadow = true; g.add(body);
  // hood: wide cobra hood, narrow at the neck, widest at 60%, with ventral scale bands
  const hs = new THREE.Shape(); hs.moveTo(-0.1, -0.12); hs.bezierCurveTo(-0.2, 0.08, -0.44, 0.2, -0.4, 0.46); hs.bezierCurveTo(-0.37, 0.66, -0.2, 0.76, 0, 0.76);
  hs.bezierCurveTo(0.2, 0.76, 0.37, 0.66, 0.4, 0.46); hs.bezierCurveTo(0.44, 0.2, 0.2, 0.08, 0.1, -0.12); hs.lineTo(-0.1, -0.12);
  if (!cobra.bump) cobra.bump = canvasTex(512, 512, (c, w, h) => { c.fillStyle = '#606060'; c.fillRect(0, 0, w, h);
    const sx = 18, sy = 13; for (let r = 0; r < h / sy + 2; r++) for (let k = 0; k < w / sx + 2; k++) { const x = k * sx + (r % 2) * sx / 2, y = r * sy;
      const gr = c.createRadialGradient(x, y - 3, 1, x, y, sx * 0.62); gr.addColorStop(0, '#d8d8d8'); gr.addColorStop(0.7, '#8a8a8a'); gr.addColorStop(1, '#3a3a3a');
      c.fillStyle = gr; c.beginPath(); c.ellipse(x, y, sx * 0.55, sy * 0.75, 0, 0, Math.PI * 2); c.fill(); }
    // belly scutes down the middle of the hood front
    for (let y = 0; y < h; y += 22) { const gr = c.createLinearGradient(0, y, 0, y + 20); gr.addColorStop(0, '#e0e0e0'); gr.addColorStop(0.8, '#909090'); gr.addColorStop(1, '#303030'); c.fillStyle = gr; c.fillRect(w * 0.42, y, w * 0.16, 20); } }, false);
  cobra.bump.wrapS = cobra.bump.wrapT = THREE.ClampToEdgeWrapping;
  const hm = mat.clone(); hm.bumpMap = cobra.bump; hm.bumpScale = 1.6;
  const hg = new THREE.ExtrudeGeometry(hs, { depth: 0.05, bevelEnabled: true, bevelThickness: 0.07, bevelSize: 0.05, bevelSegments: 6, curveSegments: 40 });
  { const uv = hg.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * 1.15 + 0.5, (uv.getY(i) + 0.12) * 1.1); }
  // bulge the hood forward in the middle
  { const p = hg.attributes.position; for (let i = 0; i < p.count; i++) { const x = p.getX(i), y = p.getY(i); if (p.getZ(i) > 0.03) p.setZ(i, p.getZ(i) + 0.08 * Math.max(0, 1 - (x * x) / 0.16) * Math.sin(Math.min(1, Math.max(0, (y + 0.12) / 0.88)) * Math.PI)); } hg.computeVertexNormals(); }
  const hood = new THREE.Mesh(hg, hm); hood.position.set(-0.05 * flip, 0.12, 0.06); hood.castShadow = hood.receiveShadow = true; g.add(hood);
  // head: broad flat skull tapering to a snout pointing out of the door
  // head in profile, snout pointing at the other cobra
  const hgeo = new THREE.CapsuleGeometry(0.068, 0.13, 10, 24); hgeo.rotateZ(Math.PI / 2);
  { const p = hgeo.attributes.position; for (let i = 0; i < p.count; i++) { let x = p.getX(i), y = p.getY(i), z = p.getZ(i); const f = Math.max(0, (flip * x) / 0.135);
      y *= 0.72 - 0.3 * f; z *= 0.9 - 0.35 * f; if (y > 0) y *= 0.85; p.setXYZ(i, x, y, z); } hgeo.computeVertexNormals(); }
  const hmat = mat.clone(); hmat.bumpMap = cobra.bump; hmat.bumpScale = 0.5;
  const hx = -0.05 * flip + flip * 0.04; const head = new THREE.Mesh(hgeo, hmat); head.rotation.z = -flip * 0.12; head.position.set(hx, 0.9, 0.27); head.scale.setScalar(1.25); head.castShadow = true; g.add(head);
  const eyeM = new THREE.MeshPhysicalMaterial({ color: 0x5a0008, roughness: 0.02, clearcoat: 1, emissive: new THREE.Color(0.4, 0.0, 0.02) });
  const ex = hx + flip * 0.065; const e = new THREE.Mesh(new THREE.SphereGeometry(0.017, 16, 12), eyeM); e.position.set(ex + flip * 0.02, 0.93, 0.335); g.add(e);
  const brow = new THREE.Mesh(new THREE.SphereGeometry(0.026, 12, 8), hmat); brow.scale.set(1.3, 0.45, 0.8); brow.position.set(ex + flip * 0.02, 0.952, 0.325); g.add(brow);
  g.userData.eyes = [new THREE.Vector3(ex + flip * 0.02, 0.93, 0.335), new THREE.Vector3(ex + flip * 0.02, 0.93, 0.335)];
  return g;
}
function vaultDoor(scene, { x = 0, z = 0, w = 2.0, h = 3.0 } = {}) {
  const g = new THREE.Group(); g.position.set(x, 0, z);
  // stone frame
  const fr = new THREE.Mesh(new THREE.BoxGeometry(w + 0.8, 0.5, 0.6), stone); fr.position.set(0, h + 0.25, 0.05); fr.castShadow = fr.receiveShadow = true; g.add(fr);
  for (const s of [-1, 1]) { const j = new THREE.Mesh(new THREE.BoxGeometry(0.4, h, 0.6), stone); j.position.set(s * (w / 2 + 0.2), h / 2, 0.05); j.castShadow = j.receiveShadow = true; g.add(j); }
  // iron leaf
  const leaf = new THREE.Mesh(new THREE.BoxGeometry(w, h, 0.18), iron); leaf.position.set(0, h / 2, -0.05); leaf.castShadow = leaf.receiveShadow = true; g.add(leaf);
  // horizontal bands
  const bandM = iron.clone(); bandM.roughness = 0.38;
  for (const y of [0.35, h * 0.5 - 0.6, h - 0.35]) { const b = new THREE.Mesh(new THREE.BoxGeometry(w, 0.16, 0.06), bandM); b.position.set(0, y, 0.07); b.castShadow = true; g.add(b); }
  // rivets
  const rv = new THREE.InstancedMesh(new THREE.SphereGeometry(0.035, 12, 8), bandM, 400); let k = 0; const M = new THREE.Matrix4();
  for (const y of [0.35, h * 0.5 - 0.6, h - 0.35]) for (let i = 0; i < 14; i++) { M.makeTranslation(-w / 2 + 0.1 + i * (w - 0.2) / 13, y, 0.1); rv.setMatrixAt(k++, M); }
  for (let j = 0; j < 22; j++) for (const s of [-1, 1]) { M.makeTranslation(s * (w / 2 - 0.08), 0.15 + j * (h - 0.3) / 21, 0.04); rv.setMatrixAt(k++, M); }
  rv.count = k; rv.castShadow = true; g.add(rv);
  // two cobras facing each other
  const cobM = new THREE.MeshStandardMaterial({ map: iron.map, bumpMap: iron.bumpMap, bumpScale: 1, metalness: 0.9, roughness: 0.3, color: new THREE.Color(1.6, 1.3, 1.0) });
  const cL = cobra(cobM, 1); cL.position.set(-0.42, h * 0.62, 0.03); cL.rotation.z = -0.08; g.add(cL);
  const cR = cobra(cobM, -1); cR.position.set(0.42, h * 0.62, 0.03); cR.rotation.z = 0.08; g.add(cR);
  // no handle, no lock: a smooth seam down the middle
  const seam = new THREE.Mesh(new THREE.BoxGeometry(0.02, h - 0.1, 0.02), new THREE.MeshStandardMaterial({ color: 0x060504, roughness: 1 })); seam.position.set(0, h / 2, 0.045); g.add(seam);
  scene.add(g); g.userData = { cL, cR, h }; return g;
}

// ---------- gopuram ----------
function gopuram(scene) {
  const g = new THREE.Group();
  const lime = new THREE.MeshStandardMaterial({ color: new THREE.Color(0.86, 0.72, 0.55), roughness: 0.85, bumpMap: stone.bumpMap, bumpScale: 1.5 });
  const shade = new THREE.MeshStandardMaterial({ color: new THREE.Color(0.42, 0.34, 0.27), roughness: 0.9 });
  const gm = goldMat(0.18);
  // base: two plain storeys of granite with gate
  const baseW = 18, baseD = 9;
  const base = new THREE.Mesh(new THREE.BoxGeometry(baseW, 7, baseD), stone); base.position.y = 3.5; base.castShadow = base.receiveShadow = true; g.add(base);
  const gate = new THREE.Mesh(new THREE.BoxGeometry(3.6, 5.6, 0.4), new THREE.MeshStandardMaterial({ color: 0x1a120c, roughness: 0.9 })); gate.position.set(0, 2.8, baseD / 2 + 0.01); g.add(gate);
  for (const s of [-1, 1]) for (let i = 0; i < 4; i++) { const pil = new THREE.Mesh(new THREE.BoxGeometry(0.6, 6.6, 0.5), stone); pil.position.set(s * (2.4 + i * 1.9), 3.3, baseD / 2 + 0.2); pil.castShadow = true; g.add(pil); }
  const corn = new THREE.Mesh(new THREE.BoxGeometry(baseW + 1, 0.5, baseD + 1), lime); corn.position.y = 7.25; corn.castShadow = true; g.add(corn);
  // 7 tapering tiers
  let y = 7.5, w = baseW - 0.6, d = baseD - 0.4; const th = 3.4;
  setSeed(5);
  for (let t = 0; t < 7; t++) {
    const tier = new THREE.Group();
    const body = new THREE.Mesh(new THREE.BoxGeometry(w, th, d), shade); body.position.y = th / 2; tier.add(body);
    // pilaster pavilions along front and sides with tiny roofs, figures in niches
    const nF = Math.max(3, Math.round(w / 1.7));
    for (let i = 0; i < nF; i++) {
      const px = -w / 2 + (i + 0.5) * w / nF; const pw = w / nF * 0.78;
      for (const side of [1, -1]) {
        const pav = new THREE.Mesh(new THREE.BoxGeometry(pw, th * 0.72, 0.45), lime); pav.position.set(px, th * 0.42, side * (d / 2 + 0.2)); pav.castShadow = pav.receiveShadow = true; tier.add(pav);
        const roof = new THREE.Mesh(new THREE.CylinderGeometry(pw * 0.35, pw * 0.55, 0.45, 4, 1), lime); roof.rotation.y = Math.PI / 4; roof.position.set(px, th * 0.88, side * (d / 2 + 0.2)); roof.castShadow = true; tier.add(roof);
        if (i % 2 === 0) { const fig = new THREE.Mesh(new THREE.CapsuleGeometry(pw * 0.14, th * 0.32, 4, 8), lime); fig.position.set(px, th * 0.42, side * (d / 2 + 0.5)); fig.castShadow = true; tier.add(fig);
          const niche = new THREE.Mesh(new THREE.BoxGeometry(pw * 0.5, th * 0.5, 0.05), shade); niche.position.set(px, th * 0.42, side * (d / 2 + 0.43)); tier.add(niche); }
      }
    }
    const nS = Math.max(2, Math.round(d / 1.8));
    for (let i = 0; i < nS; i++) { const pz = -d / 2 + (i + 0.5) * d / nS; for (const side of [1, -1]) { const pav = new THREE.Mesh(new THREE.BoxGeometry(0.45, th * 0.72, d / nS * 0.78), lime); pav.position.set(side * (w / 2 + 0.2), th * 0.42, pz); pav.castShadow = pav.receiveShadow = true; tier.add(pav); } }
    const c = new THREE.Mesh(new THREE.BoxGeometry(w + 0.9, 0.35, d + 0.9), lime); c.position.y = th + 0.05; c.castShadow = c.receiveShadow = true; tier.add(c);
    const nk = Math.round((w + 0.9) / 0.7); for (let i = 0; i < nk; i++) { const kx = -(w + 0.9) / 2 + (i + 0.5) * (w + 0.9) / nk; for (const side of [1, -1]) {
      const ku = new THREE.Mesh(new THREE.TorusGeometry(0.2, 0.07, 6, 12, Math.PI), lime); ku.position.set(kx, th + 0.22, side * (d / 2 + 0.46)); ku.castShadow = true; tier.add(ku);
      const kb = new THREE.Mesh(new THREE.SphereGeometry(0.1, 8, 6), lime); kb.position.set(kx, th + 0.25, side * (d / 2 + 0.45)); tier.add(kb); } }
    tier.position.y = y; g.add(tier);
    y += th + 0.2; w -= 1.85; d -= 0.75;
  }
  // barrel (shala) roof
  const bar = new THREE.Mesh(new THREE.CylinderGeometry(d * 0.62, d * 0.62, w + 1.2, 32, 1, false, 0, Math.PI), lime); bar.rotation.z = Math.PI / 2; bar.rotation.y = 0; bar.position.y = y; bar.rotation.x = 0;
  bar.rotation.set(0, 0, Math.PI / 2); bar.geometry.rotateY(-Math.PI / 2); bar.castShadow = true; g.add(bar);
  for (let i = 0; i < 7; i++) { const k = kalasam(gm); k.scale.setScalar(1.6); k.position.set(-(w + 0.4) / 2 + i * (w + 0.4) / 6, y + d * 0.6 - 0.05, 0); g.add(k); }
  scene.add(g); return g;
}
function palm(scene, x, z, h, lean, mat) {
  const pts = []; for (let i = 0; i <= 10; i++) { const t = i / 10; pts.push(new THREE.Vector3(x + lean * t * t * h * 0.3, t * h, z)); }
  const c = new THREE.CatmullRomCurve3(pts); const tr = new THREE.Mesh(new THREE.TubeGeometry(c, 30, h * 0.018, 8), mat); tr.castShadow = true; scene.add(tr);
  const top = c.getPointAt(1);
  for (let i = 0; i < 14; i++) { const a = i / 14 * Math.PI * 2; const fp = [];
    for (let j = 0; j <= 8; j++) { const t = j / 8; fp.push(new THREE.Vector3(top.x + Math.cos(a) * t * h * 0.28, top.y + Math.sin(t * Math.PI * 0.7) * h * 0.06 - t * t * h * 0.12, top.z + Math.sin(a) * t * h * 0.28)); }
    const fc = new THREE.CatmullRomCurve3(fp); const fr = new THREE.Mesh(new THREE.TubeGeometry(fc, 16, h * 0.012, 4), mat); fr.scale.set(1, 1, 1); scene.add(fr);
    // leaflets as thin quads
    for (let j = 1; j < 16; j++) { const t = j / 16; const p = fc.getPointAt(t), tg = fc.getTangentAt(t); for (const s of [-1, 1]) { const l = new THREE.Mesh(new THREE.PlaneGeometry(h * 0.012, h * 0.09 * Math.sin(t * Math.PI) + 0.05), mat); l.position.copy(p); l.lookAt(p.clone().add(new THREE.Vector3(0, 1, 0))); l.rotateZ(s * 1.1); l.translateY(-h * 0.04); scene.add(l); } }
  }
}

// ---------- composer ----------
function compose(scene, cam, { bloom = [0.9, 0.6, 0.82], dof = null, grade = {} } = {}) {
  const comp = new EffectComposer(renderer, new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, samples: 0 }));
  comp.setPixelRatio(1); comp.setSize(W, H);
  comp.addPass(new RenderPass(scene, cam));
  if (dof) comp.addPass(new BokehPass(scene, cam, { focus: dof.focus, aperture: dof.aperture, maxblur: dof.maxblur || 0.012 }));
  comp.addPass(new UnrealBloomPass(new THREE.Vector2(W, H), bloom[0], bloom[1], bloom[2]));
  comp.addPass(new OutputPass());
  // grade: lift edges (no near-black borders), warm, mild vignette, grain
  comp.addPass(new ShaderPass({ uniforms: { tDiffuse: { value: null }, vig: { value: grade.vig ?? 0.18 }, lift: { value: grade.lift ?? 0.035 }, warm: { value: grade.warm ?? 0.04 }, seed: { value: 1.3 } },
    vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }',
    fragmentShader: `uniform sampler2D tDiffuse; uniform float vig, lift, warm, seed; varying vec2 vUv;
      float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233))+seed)*43758.5453); }
      void main(){ vec3 c = texture2D(tDiffuse, vUv).rgb; vec2 d = vUv-0.5; d.x *= 0.75; float v = 1.0 - vig*smoothstep(0.2, 0.75, length(d));
        c *= v; c = c + lift*vec3(1.0,0.8,0.6)*(1.0-c); c.r += warm*c.r*(1.0-c.r); c.b -= warm*0.6*c.b*(1.0-c.b);
        c += (h(vUv*1000.0)-0.5)*0.025; gl_FragColor = vec4(c,1.); }` }));
  return comp;
}

// ---------- shots ----------
const SHOTS = {
  gold() {
    const scene = new THREE.Scene(); scene.environment = warmEnv(1.0); scene.environmentIntensity = 0.35;
    scene.background = new THREE.Color(0.10, 0.055, 0.025); scene.fog = new THREE.FogExp2(new THREE.Color(0.16, 0.08, 0.03), 0.06);
    const grp = new THREE.Group(); scene.add(grp);
    addCoinHeap(grp, { cx: 0, cz: 0, R: 2.6, Hh: 1.5, n: 7000, scale: 0.13, sd: 2 });
    addCoinHeap(grp, { cx: -3.2, cz: -3, R: 2.4, Hh: 2.2, n: 4000, scale: 0.13, sd: 3 });
    addCoinHeap(grp, { cx: 3.4, cz: -4, R: 2.8, Hh: 2.6, n: 4000, scale: 0.13, sd: 4 });
    const gm = goldMat(0.16), gems = gemMaterials();
    const cr = crown(gm, gems); cr.position.set(1.0, 1.15, -0.9); cr.rotation.set(0.2, 0.4, -0.2); cr.scale.setScalar(0.5); grp.add(cr);
    const p1 = goldPot(gm); p1.position.set(-1.25, 0.9, -0.7); p1.rotation.z = 0.12; p1.scale.setScalar(0.8); grp.add(p1);
    const p2 = goldPot(goldMat(0.3)); p2.position.set(2.2, 1.0, -2.4); p2.rotation.z = -0.5; p2.scale.setScalar(0.9); grp.add(p2);
    const k1 = kalasam(gm); k1.position.set(-2.8, 1.9, -3.4); k1.scale.setScalar(0.9); grp.add(k1);
    const curve = new THREE.CatmullRomCurve3([new THREE.Vector3(-0.6, 1.35, 1.3), new THREE.Vector3(-0.2, 1.4, 0.7), new THREE.Vector3(0.4, 1.28, 0.2), new THREE.Vector3(1.3, 0.95, 0.4), new THREE.Vector3(2.0, 0.55, 1.2)]);
    grp.add(chain(gm, curve, 0.05, 120));
    // loose coins tumbling (frozen mid-air)
    setSeed(77); const cg = coinGeo(); const cm = goldMat(0.15); cm.bumpMap = coinBump; cm.bumpScale = 1.2;
    for (let i = 0; i < 26; i++) { const c = new THREE.Mesh(cg, cm); c.scale.setScalar(0.13); c.position.set(rr(-1.5, 1.8), rr(1.6, 3.2), rr(-1.5, 1.6)); c.rotation.set(rr(0, 6), rr(0, 6), rr(0, 6)); c.castShadow = true; grp.add(c); }
    // lamps (out of frame + background glints)
    lampLight(scene, new THREE.Vector3(2.4, 0.3, 2.2), 9, 14, true, 0, false);
    lampLight(scene, new THREE.Vector3(-2.6, 0.4, 1.0), 5, 12, true, 0, false);
    for (const [x, y, z] of [[-1.5, 2.5, -6], [1.8, 2.6, -7.5], [4.5, 2.0, -6], [-4.5, 2.0, -5.5]]) { lampLight(scene, new THREE.Vector3(x, y, z), 4, 9, false, 0, false); }
    const key = new THREE.SpotLight(new THREE.Color(1, 0.8, 0.55), 22, 20, 0.5, 0.6, 1.4); key.position.set(-1.5, 6, 3.5); key.target.position.set(0, 1, 0); key.castShadow = true; key.shadow.mapSize.set(2048, 2048); scene.add(key, key.target);
    dust(scene, new THREE.Vector3(0, 2.5, 0), new THREE.Vector3(4, 2, 4), 2500, undefined, 0.025, 0.5);
    const cam = new THREE.PerspectiveCamera(34, W / H, 0.05, 80); cam.position.set(0.1, 1.5, 3.0); cam.lookAt(0.4, 1.35, -1.0);
    return compose(scene, cam, { bloom: [0.45, 0.45, 0.93], dof: { focus: 2.75, aperture: 0.0022, maxblur: 0.01 } });
  },
  door() {
    const scene = buildCorridor(); const { door } = scene.userData;
    const cam = new THREE.PerspectiveCamera(42, W / H, 0.05, 80); cam.position.set(0.2, 0.9, 8.6); cam.lookAt(0, 1.75, 0);
    return compose(scene, cam, { bloom: [0.5, 0.5, 0.9], dof: { focus: 8.0, aperture: 0.0006 } });
  },
};
function buildCorridor({ lampLean = 0, lampPos = new THREE.Vector3(1.35, 0, 1.0), extraLight = true, lampRotY = 0 } = {}) {
  const scene = new THREE.Scene(); scene.environment = warmEnv(0.45); scene.environmentIntensity = 0.5;
  scene.background = new THREE.Color(0.12, 0.07, 0.04); scene.fog = new THREE.FogExp2(new THREE.Color(0.2, 0.11, 0.05), 0.05);
  floor(scene, -3, 3, -1, 12);
  stoneBlocks(scene, -3, 3, 0, 5.5, -0.35, 'z', 1.1, 0.55, 0.3, 3); // back wall around door (door covers middle)
  stoneBlocks(scene, -1, 12, 0, 5.5, -2.1, 'x+', 1.2, 0.55, 0.3, 4);
  stoneBlocks(scene, -1, 12, 0, 5.5, 2.1, 'x-', 1.2, 0.55, 0.3, 5);
  const ceil = new THREE.Mesh(new THREE.BoxGeometry(4.6, 0.3, 14), stone); ceil.position.set(0, 4.25, 5.5); ceil.receiveShadow = true; scene.add(ceil);
  // back wall plane behind blocks fills gaps
  const door = vaultDoor(scene, { x: 0, z: 0.02, w: 2.1, h: 3.2 });
  const bm = new THREE.MeshStandardMaterial({ color: 0xb08a5a, metalness: 1, roughness: 0.25 });
  const lamp = lampLight(scene, lampPos, 14, 14, true, lampLean, true, bm); lamp.rotation.y = lampRotY;
  if (extraLight) { const l2 = lampLight(scene, new THREE.Vector3(-1.35, 0, 1.0), 10, 12, false, 0, true, bm); }
  // warm fill from behind camera (stairwell glow) to keep frame edges lifted
  const fill = new THREE.PointLight(new THREE.Color(1, 0.7, 0.42), 14, 24, 1.2); fill.position.set(0, 3.6, 11); scene.add(fill);
  dust(scene, new THREE.Vector3(0, 2, 3), new THREE.Vector3(1.6, 1.6, 2.5), 900, undefined, 0.018, 0.35);
  scene.userData = { door, lamp }; return scene;
}


// ---------- extra shots ----------
function skyDome(scene, top, mid, horizon, sunDir, sunCol) {
  const m = new THREE.ShaderMaterial({ side: THREE.BackSide, depthWrite: false, uniforms: { top: { value: top }, mid: { value: mid }, hor: { value: horizon }, sd: { value: sunDir.clone().normalize() }, sc: { value: sunCol } },
    vertexShader: 'varying vec3 vD; void main(){ vD = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }',
    fragmentShader: 'uniform vec3 top, mid, hor, sd, sc; varying vec3 vD; void main(){ float y = vD.y; vec3 c = y>0.18 ? mix(mid, top, smoothstep(0.18,0.8,y)) : mix(hor, mid, smoothstep(-0.05,0.18,y)); float s = max(dot(normalize(vD), sd),0.); c += sc*(pow(s,600.)*8. + pow(s,12.)*0.6 + pow(s,3.)*0.15); gl_FragColor = vec4(c,1.); }' });
  const d = new THREE.Mesh(new THREE.SphereGeometry(400, 32, 16), m); scene.add(d); return d;
}
SHOTS.tower = () => {
  const scene = new THREE.Scene(); scene.fog = new THREE.Fog(new THREE.Color(0.95, 0.72, 0.6), 90, 400);
  const sunDir = new THREE.Vector3(-0.8, 0.12, -0.5);
  skyDome(scene, new THREE.Color(0.28, 0.42, 0.78), new THREE.Color(0.95, 0.62, 0.55), new THREE.Color(1.3, 0.78, 0.45), sunDir, new THREE.Color(1.6, 0.9, 0.5));
  const pm = new THREE.PMREMGenerator(renderer); scene.environment = pm.fromScene(scene, 0.04).texture; scene.environmentIntensity = 0.6;
  const g = gopuram(scene); g.position.set(0, 0.6, -30); g.scale.set(1, 1.15, 1);
  const sun = new THREE.DirectionalLight(new THREE.Color(1, 0.72, 0.48), 3.2); sun.position.copy(sunDir).multiplyScalar(80).add(new THREE.Vector3(0, 10, -30)); sun.target.position.set(0, 15, -30);
  sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, { left: -30, right: 30, top: 50, bottom: -10, near: 1, far: 200 }); scene.add(sun, sun.target);
  scene.add(new THREE.HemisphereLight(new THREE.Color(0.7, 0.6, 0.8), new THREE.Color(0.5, 0.35, 0.25), 0.9));
  const gm = stone.clone(); gm.map = stone.map.clone(); gm.map.repeat.set(40, 40); gm.map.needsUpdate = true;
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(300, 150), gm); ground.rotation.x = -Math.PI / 2; ground.position.set(0, 0.6, -91); ground.receiveShadow = true; scene.add(ground);
  for (let i = 0; i < 5; i++) { const st = new THREE.Mesh(new THREE.BoxGeometry(80, 0.2, 0.8), stone); st.position.set(0, 0.5 - i * 0.16, -15.5 + i * 0.8); st.receiveShadow = true; scene.add(st); }
  const pond = new Reflector(new THREE.PlaneGeometry(160, 60), { textureWidth: W, textureHeight: H, color: 0x707068 }); pond.rotation.x = -Math.PI / 2; pond.position.set(0, -0.2, 16); scene.add(pond);
  const tint = new THREE.Mesh(new THREE.PlaneGeometry(80, 26), new THREE.MeshBasicMaterial({ color: new THREE.Color(0.2, 0.17, 0.14), transparent: true, opacity: 0.3 })); tint.rotation.x = -Math.PI / 2; tint.position.set(0, -0.18, 16); tint.scale.set(2, 2.31, 1); scene.add(tint);
  const palmM = new THREE.MeshStandardMaterial({ color: new THREE.Color(0.12, 0.13, 0.07), roughness: 0.9, side: THREE.DoubleSide });
  palm(scene, -24, -20, 18, 0.8, palmM); palm(scene, 25, -18, 16, -0.6, palmM); palm(scene, -30, -10, 14, 1.2, palmM); palm(scene, 31, -8, 15, -1.0, palmM);
  for (const sx of [-1, 1]) { const wall = new THREE.Mesh(new THREE.BoxGeometry(60, 4.5, 1.2), new THREE.MeshStandardMaterial({ color: new THREE.Color(0.82, 0.74, 0.62), roughness: 0.9 })); wall.position.set(sx * 39, 2.8, -26); wall.castShadow = wall.receiveShadow = true; scene.add(wall);
    const roof = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 2.2, 1.6, 4, 1), new THREE.MeshStandardMaterial({ color: new THREE.Color(0.45, 0.2, 0.12), roughness: 0.8 })); roof.scale.set(19, 1, 1); roof.rotation.y = Math.PI / 4; roof.scale.set(1, 1, 1); const rf = new THREE.Mesh(new THREE.BoxGeometry(60, 0.5, 2.6), roof.material); rf.position.set(sx * 39, 5.2, -26); rf.rotation.x = 0.0; rf.castShadow = true; scene.add(rf); }
  dust(scene, new THREE.Vector3(0, 8, -12), new THREE.Vector3(20, 8, 12), 1500, new THREE.Color(1, 0.8, 0.6), 0.08, 0.35);
  const cam = new THREE.PerspectiveCamera(56, W / H, 0.5, 900); cam.position.set(0.8, 1.2, 36); cam.lookAt(0, 11, -30);
  return compose(scene, cam, { bloom: [0.5, 0.6, 0.85], grade: { vig: 0.12, lift: 0.02 } });
};
function stoneBlocksZ(scene, x, z0, z1, sd) {
  if (z1 - z0 < 0.3) return; const m = stoneBlocks(scene, 0, z1 - z0, 0, 5.5, 0, 'none', 1.2, 0.55, 0.3, sd);
  m.rotation.y = x < 0 ? Math.PI / 2 : -Math.PI / 2; m.position.set(x, 0, x < 0 ? z1 : z0);
}
function openVaultRow(scene) {
  floor(scene, -3, 3, -32, 6);
  const ceil = new THREE.Mesh(new THREE.BoxGeometry(4.6, 0.3, 40), stone); ceil.position.set(0, 4.4, -13); ceil.receiveShadow = true; scene.add(ceil);
  const zs = [-2, -8, -14, -20, -26];
  for (const side of [-1, 1]) { let prev = 6, k = 0;
    for (const zc of zs) { stoneBlocksZ(scene, side * 2.1, zc + 1.0, prev, 30 + k++ + (side > 0 ? 10 : 0)); prev = zc - 1.0; }
    stoneBlocksZ(scene, side * 2.1, -32, prev, 60 + (side > 0 ? 5 : 0)); }
  zs.forEach((zc, i) => { for (const sd of [-1, 1]) {
    const lin = new THREE.Mesh(new THREE.BoxGeometry(0.5, 1.2, 2.2), stone); lin.position.set(sd * 2.1, 3.7, zc); lin.castShadow = lin.receiveShadow = true; scene.add(lin);
    const leaf = new THREE.Mesh(new THREE.BoxGeometry(0.12, 3.0, 1.9), iron); leaf.position.set(sd * 1.7, 1.5, zc - 1.75); leaf.rotation.y = -sd * 0.55; leaf.castShadow = true; scene.add(leaf);
    const room = new THREE.Group(); room.position.set(sd * 3.6, 0, zc); scene.add(room);
    const back = new THREE.Mesh(new THREE.PlaneGeometry(2.4, 3.1), new THREE.MeshBasicMaterial({ color: new THREE.Color(1.4, 0.8, 0.3) })); back.position.set(sd * 1.3, 1.55, 0); back.rotation.y = -sd * Math.PI / 2; room.add(back);
    addCoinHeap(room, { cx: 0, cz: 0, R: 1.0, Hh: 1.2, n: 700, scale: 0.12, sd: 10 + i, under: true });
    const L = new THREE.PointLight(new THREE.Color(1, 0.68, 0.3), 40, 12, 1.4); L.position.set(sd * 2.7, 2.4, zc); scene.add(L);
    shaft(scene, new THREE.Vector3(sd * 2.4, 2.9, zc), new THREE.Vector3(-sd * 0.6, 0, zc + 0.6), 0.8, 1.6, new THREE.Color(1, 0.62, 0.25), 0.08);
  } });
  const door = vaultDoor(scene, { x: 0, z: -31.6, w: 2.1, h: 3.2 });
  stoneBlocks(scene, -3, 3, 0, 5.5, -31.95, 'z', 1.1, 0.55, 0.3, 77);
  return door;
}
SHOTS.vaults = () => {
  const scene = new THREE.Scene(); scene.environment = warmEnv(0.5); scene.environmentIntensity = 0.5;
  scene.background = new THREE.Color(0.12, 0.07, 0.04); scene.fog = new THREE.FogExp2(new THREE.Color(0.2, 0.11, 0.05), 0.028);
  openVaultRow(scene);
  const bm = new THREE.MeshStandardMaterial({ color: 0xb08a5a, metalness: 1, roughness: 0.25 });
  const dl = new THREE.SpotLight(new THREE.Color(1, 0.7, 0.45), 8, 30, 0.2, 0.8, 1); dl.position.set(0, 3.5, -18); dl.target.position.set(0, 1.6, -31.6); scene.add(dl, dl.target);
  dust(scene, new THREE.Vector3(0, 2, -12), new THREE.Vector3(1.8, 2, 14), 3000, undefined, 0.025, 0.4);
  const cam = new THREE.PerspectiveCamera(50, W / H, 0.05, 80); cam.position.set(-0.6, 1.2, 3); cam.lookAt(0.25, 1.7, -30);
  return compose(scene, cam, { bloom: [0.6, 0.6, 0.85], dof: { focus: 12, aperture: 0.0003 } });
};
SHOTS.lamp = () => {
  const scene = buildCorridor({ lampLean: -0.3, lampPos: new THREE.Vector3(1.35, 0, 1.0), extraLight: false });
  const bm = new THREE.MeshStandardMaterial({ color: 0xb08a5a, metalness: 1, roughness: 0.25 });
  lampLight(scene, new THREE.Vector3(-1.35, 0, 1.0), 10, 12, false, 0.3, true, bm).rotation.y = Math.PI;
  const cam = new THREE.PerspectiveCamera(38, W / H, 0.05, 80); cam.position.set(0.15, 1.75, 4.8); cam.lookAt(0.85, 1.7, 0.9);
  return compose(scene, cam, { bloom: [0.6, 0.5, 0.88], dof: { focus: 3.9, aperture: 0.002, maxblur: 0.01 } });
};
SHOTS.macro = () => {
  const scene = buildCorridor({ lampPos: new THREE.Vector3(-1.2, 0, 0.9), extraLight: false });
  const { door } = scene.userData; const c = door.userData.cL; c.updateMatrixWorld(true); const wp = new THREE.Vector3(); c.getWorldPosition(wp);
  const cam = new THREE.PerspectiveCamera(30, W / H, 0.02, 40); cam.position.set(wp.x + 0.9, wp.y + 0.25, 2.1); cam.lookAt(wp.x - 0.05, wp.y + 0.35, 0.1);
  return compose(scene, cam, { bloom: [0.6, 0.5, 0.85], dof: { focus: 2.0, aperture: 0.0015, maxblur: 0.008 } });
};
SHOTS.hand = () => {
  const scene = buildCorridor({ lampPos: new THREE.Vector3(-1.5, 0.15, 3.0), extraLight: false });
  // open hand, fingers up and slightly spread (silhouette for the shadow)
  const s = new THREE.Shape();
  const fing = [[-0.27, 0.62, -0.18], [-0.09, 0.74, -0.05], [0.09, 0.70, 0.06], [0.25, 0.56, 0.18]]; // x, length, tilt
  s.moveTo(-0.22, -0.9); s.lineTo(-0.3, -0.15); s.lineTo(-0.36, 0.05);
  for (const [x, L, t] of fing) { const w = 0.075; const bx = x, by = 0.08; const tx = bx + Math.sin(t) * L, ty = by + Math.cos(t) * L * 0.75 + 0.1;
    s.lineTo(bx - w, by); s.lineTo(tx - w * 0.85, ty); s.quadraticCurveTo(tx, ty + 0.09, tx + w * 0.85, ty); s.lineTo(bx + w, by); }
  s.lineTo(0.36, -0.02); s.bezierCurveTo(0.5, -0.05, 0.62, 0.0, 0.7, 0.12); s.quadraticCurveTo(0.74, 0.2, 0.66, 0.2); s.bezierCurveTo(0.55, 0.12, 0.44, -0.2, 0.3, -0.3); s.lineTo(0.22, -0.9); s.lineTo(-0.22, -0.9);
  const hand = new THREE.Mesh(new THREE.ExtrudeGeometry(s, { depth: 0.05, bevelEnabled: true, bevelThickness: 0.02, bevelSize: 0.015, bevelSegments: 2, curveSegments: 12 }), new THREE.MeshStandardMaterial({ color: 0x3a2a20 }));
  hand.castShadow = true; hand.rotation.z = -0.5; hand.rotation.y = 0.35; hand.position.set(-0.9, 1.95, 2.0); hand.scale.setScalar(0.2); scene.add(hand);
  const cam = new THREE.PerspectiveCamera(36, W / H, 0.05, 80); cam.position.set(0.7, 1.95, 3.6); cam.lookAt(-0.3, 2.05, 0);
  return compose(scene, cam, { bloom: [0.55, 0.5, 0.88], dof: { focus: 3.7, aperture: 0.0012 } });
};
SHOTS.eyes = () => {
  const scene = buildCorridor({ lampPos: new THREE.Vector3(0.0, 0, 1.3), extraLight: false });
  const { door } = scene.userData; door.updateMatrixWorld(true);
  const e = new THREE.Vector3(); door.userData.cL.localToWorld(e.copy(door.userData.cL.userData.eyes[1])); const e2 = new THREE.Vector3(); door.userData.cR.localToWorld(e2.copy(door.userData.cR.userData.eyes[0]));
  const m = e.clone().add(e2).multiplyScalar(0.5);
  const cam = new THREE.PerspectiveCamera(40, W / H, 0.01, 40); cam.position.set(m.x + 0.08, m.y - 0.55, m.z + 2.7); cam.lookAt(m.x, m.y - 0.62, m.z);
  for (const p of [e, e2]) { const sp = glowSprite(new THREE.Color(1, 0.18, 0.1), 0.1, 0.9); sp.position.copy(p).add(new THREE.Vector3(0, 0, 0.02)); scene.add(sp); }
  return compose(scene, cam, { bloom: [0.8, 0.4, 0.82], dof: { focus: 2.75, aperture: 0.0015, maxblur: 0.01 } });
};

window.renderShot = async (name) => {
  initMats.done || (initMats(), initMats.done = true);
  const comp = SHOTS[name](); comp.render(); await new Promise(r => setTimeout(r, 10));
  return renderer.domElement.toDataURL('image/png');
};
window.ready = true;
