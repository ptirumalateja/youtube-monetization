// Lobster photo post (Slow Light): a lobster just out of its old shell on a dark seabed, the empty shell behind it,
// one warm gold light from above. Procedural geometry only. Rendered to a still by still.cjs (window.render()).
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const q = new URLSearchParams(location.search); const W = +q.get('w') || 1080, H = +q.get('h') || 1350;
const V = (x, y, z) => new THREE.Vector3(x, y, z);
const rng = s => () => { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; };

const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setSize(W, H, false); renderer.setPixelRatio(1);
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene();
const WATER = new THREE.Color(0x0b1a22);                         // deep teal-navy, never pure black (no "black border" reads)
scene.background = WATER; scene.fog = new THREE.FogExp2(WATER, 0.085);
const cam = new THREE.PerspectiveCamera(32, W / H, 0.1, 80);
cam.position.set(1.2, 2.7, 6.6); cam.lookAt(-0.35, 0.3, -0.1);

// ---- light: one warm key from above (the light through the water), a cold dim fill, a rim from behind
const key = new THREE.SpotLight(0xffc77a, 120, 18, 0.27, 0.8, 1.3); key.position.set(0.2, 7.2, 1.2); key.target.position.set(-0.45, 0, -0.1);
key.castShadow = true; key.shadow.mapSize.set(2048, 2048); key.shadow.bias = -0.0004; key.shadow.radius = 4; scene.add(key, key.target);
scene.add(new THREE.HemisphereLight(0x3d6a80, 0x0a0806, 0.3));
const rim = new THREE.DirectionalLight(0x9fc4d8, 0.9); rim.position.set(-3, 2.5, -4); scene.add(rim);

// ---- textures
function noiseTex(size, seed, base, amp, scale) {
  const c = document.createElement('canvas'); c.width = c.height = size; const x = c.getContext('2d'); const R = rng(seed);
  x.fillStyle = `rgb(${base},${base},${base})`; x.fillRect(0, 0, size, size);
  for (let i = 0; i < size * size / scale; i++) { const v = base + (R() - 0.5) * amp; x.fillStyle = `rgba(${v},${v * 0.97},${v * 0.9},0.35)`; x.fillRect(R() * size, R() * size, 1 + R() * 3, 1 + R() * 3); }
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; return t; }

// ---- seabed: gentle sand ripples, a few rocks, a dark shelf of rock behind (where he hid to molt)
{ const g = new THREE.PlaneGeometry(40, 40, 260, 260); g.rotateX(-Math.PI / 2); const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) { const x = p.getX(i), z = p.getZ(i); p.setY(i, 0.035 * Math.sin(x * 3.1 + z * 0.8) + 0.02 * Math.sin(x * 7.3 - z * 2.1) + 0.12 * Math.sin(x * 0.35) * Math.cos(z * 0.4)); }
  g.computeVertexNormals(); const t = noiseTex(512, 3, 120, 90, 6); t.repeat.set(10, 10);
  const m = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color: 0x5f5a50, map: t, roughness: 0.95 })); m.receiveShadow = true; scene.add(m); }
const groundY = (x, z) => 0.035 * Math.sin(x * 3.1 + z * 0.8) + 0.02 * Math.sin(x * 7.3 - z * 2.1) + 0.12 * Math.sin(x * 0.35) * Math.cos(z * 0.4);
const rockMat = new THREE.MeshStandardMaterial({ color: 0x3a3a38, roughness: 0.9, map: noiseTex(256, 9, 110, 120, 4) });
function rock(x, z, s, seed, sy = 0.7) { const g = new THREE.IcosahedronGeometry(1, 3); const p = g.attributes.position; const R = rng(seed);
  const k = [...Array(6)].map(() => [R() * 6, R() * 6, R() * 6, 0.1 + 0.15 * R()]);
  for (let i = 0; i < p.count; i++) { const v = V(p.getX(i), p.getY(i), p.getZ(i)); let d = 1; for (const [a, b, c, w] of k) d += w * Math.sin(v.x * a + v.y * b + v.z * c); v.multiplyScalar(d); p.setXYZ(i, v.x, v.y * sy, v.z); }
  g.computeVertexNormals(); const m = new THREE.Mesh(g, rockMat); m.scale.setScalar(s); m.position.set(x, groundY(x, z) + s * 0.25, z); m.castShadow = m.receiveShadow = true; scene.add(m); return m; }
rock(-3.2, -2.4, 1.6, 11, 0.8); rock(-1.6, -3.4, 1.2, 12); rock(2.9, -2.6, 1.0, 13); rock(1.9, 0.9, 0.22, 14); rock(-1.9, 1.1, 0.16, 15); rock(0.7, -1.4, 0.3, 16);

// ---- the lobster: built from simple solids along its body
function lobster(mat, opts = {}) {
  const G = new THREE.Group(); const add = (geo, pos, scl, rot) => { const m = new THREE.Mesh(geo, mat); m.position.copy(pos); if (scl) m.scale.copy(scl); if (rot) m.rotation.set(...rot); m.castShadow = true; m.receiveShadow = true; G.add(m); return m; };
  const sph = new THREE.SphereGeometry(1, 40, 24), cyl = new THREE.CylinderGeometry(1, 1, 1, 14), cone = new THREE.ConeGeometry(1, 1, 14);
  const body = new THREE.Group(); G.add(body);
  const acc = opts.accent || mat;   // legs, antennae, joints: the orange-red of a live lobster
  const lathe = (pts, len) => { const g = new THREE.LatheGeometry(pts.map(([r, y]) => new THREE.Vector2(r, y * len)), 40); g.rotateZ(-Math.PI / 2); return g; };   // profile along +x
  // carapace (head and thorax): a lathed shell, pointed at the front, with the rostrum spike
  const cara = new THREE.Group(); body.add(cara);
  { const g = lathe([[0.02, 0], [0.16, 0.03], [0.215, 0.15], [0.225, 0.45], [0.2, 0.7], [0.13, 0.88], [0.06, 0.97], [0.0, 1.0]], 0.98);
    const m = new THREE.Mesh(g, mat); m.scale.set(1, 0.88, 1.0); m.position.set(-0.2, 0.32, 0); m.castShadow = m.receiveShadow = true; cara.add(m);
    const r = new THREE.Mesh(cone, mat); r.scale.set(0.03, 0.2, 0.03); r.rotation.z = -Math.PI / 2 - 0.1; r.position.set(0.86, 0.35, 0); cara.add(r);
    if (opts.lift) { cara.position.set(0.0, 0.02, 0); cara.rotation.z = opts.lift; } }
  // tail: six overlapping segments drooping a little, then the fan
  const tail = new THREE.Group(); body.add(tail); if (opts.tailShift) tail.position.x -= opts.tailShift;
  let x = -0.2, y = 0.31;
  for (let i = 0; i < 6; i++) { const s = 1 - i * 0.085; const m = new THREE.Mesh(sph, mat); m.scale.set(0.12, 0.13 * s, 0.19 * s); m.position.set(x, y, 0); m.castShadow = m.receiveShadow = true; tail.add(m); x -= 0.17 * s; y -= 0.02 + i * 0.006; }
  for (let i = -2; i <= 2; i++) { const m = new THREE.Mesh(sph, acc); m.scale.set(0.16, 0.016, 0.07); m.position.set(x - 0.08, y - 0.02, i * 0.065); m.rotation.y = i * 0.3; m.castShadow = true; tail.add(m); }
  // claws: arm forward, then a big claw: a lathed palm and two curved fingers, slightly open. One crusher, one cutter.
  for (const side of [1, -1]) {
    const big = side > 0 ? 1.15 : 0.95; const a0 = V(0.6, 0.27, 0.14 * side), a1 = V(0.86, 0.3, 0.36 * side), a2 = V(1.12, 0.27, 0.42 * side);
    for (const [p, q2, r] of [[a0, a1, 0.045], [a1, a2, 0.05]]) { const d = q2.clone().sub(p); const m = new THREE.Mesh(cyl, mat); m.scale.set(r, d.length(), r);
      m.position.copy(p).add(q2).multiplyScalar(0.5); m.quaternion.setFromUnitVectors(V(0, 1, 0), d.normalize()); m.castShadow = true; G.add(m); }
    for (const j of [a1, a2]) { const k = new THREE.Mesh(sph, acc); k.scale.setScalar(0.058); k.position.copy(j); G.add(k); }
    const claw = new THREE.Group(); claw.position.copy(a2); claw.rotation.y = -0.22 * side; claw.rotation.z = -0.06; claw.scale.setScalar(big); G.add(claw);
    const palm = new THREE.Mesh(lathe([[0.045, 0], [0.09, 0.07], [0.15, 0.22], [0.155, 0.34], [0.12, 0.46], [0.085, 0.5]], 1), mat); palm.scale.set(1, 0.62, 1); palm.castShadow = true; claw.add(palm);
    const fingerG = lathe([[0.075, 0], [0.068, 0.1], [0.05, 0.24], [0.022, 0.35], [0.0, 0.38]], 1);
    const f1 = new THREE.Mesh(fingerG, mat); f1.scale.set(1, 0.55, side > 0 ? 1.15 : 0.8); f1.position.set(0.47, 0.03, 0); f1.rotation.z = 0.2; f1.castShadow = true; claw.add(f1);
    const f2 = new THREE.Mesh(fingerG, mat); f2.scale.set(0.92, 0.55, side > 0 ? 1.15 : 0.8); f2.position.set(0.47, -0.035, 0); f2.rotation.z = -0.08; f2.castShadow = true; claw.add(f2);
    const tip = new THREE.Mesh(sph, acc); tip.scale.setScalar(0.02); tip.position.set(0.47 + 0.36 * Math.cos(0.2), 0.03 + 0.36 * Math.sin(0.2), 0); claw.add(tip); }
  // four pairs of walking legs, bent down to the sand
  for (const side of [1, -1]) for (let i = 0; i < 4; i++) {
    const r0 = V(0.45 - i * 0.13, 0.2, 0.12 * side), r1 = V(0.42 - i * 0.16, 0.24, (0.34 + 0.02 * i) * side), r2 = V(0.36 - i * 0.2, 0.0, (0.46 + 0.04 * i) * side);
    for (const [p, q2] of [[r0, r1], [r1, r2]]) { const d = q2.clone().sub(p); const m = new THREE.Mesh(cyl, acc); m.scale.set(0.016, d.length(), 0.016);
      m.position.copy(p).add(q2).multiplyScalar(0.5); m.quaternion.setFromUnitVectors(V(0, 1, 0), d.normalize()); m.castShadow = true; G.add(m); } }
  // eyes on short stalks, two long antennae sweeping back, two short antennules
  for (const side of [1, -1]) {
    if (!opts.empty) { const e = new THREE.Mesh(sph, new THREE.MeshStandardMaterial({ color: 0x050505, roughness: 0.2 })); e.scale.setScalar(0.03); e.position.set(0.74, 0.42, 0.06 * side); G.add(e); }
    const pts = [V(0.76, 0.38, 0.05 * side), V(1.1, 0.62, 0.22 * side), V(1.25, 0.9, 0.55 * side), V(0.9, 1.05, 1.0 * side), V(0.2, 0.95, 1.35 * side)];
    const t = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 60, 0.009, 6), acc); t.castShadow = true; G.add(t);
    const pts2 = [V(0.78, 0.38, 0.03 * side), V(0.98, 0.5, 0.08 * side), V(1.12, 0.52, 0.14 * side)];
    G.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts2), 16, 0.006, 5), acc)); }
  return G; }

// the new lobster: dark wet shell, warm gold where the light hits, cool rim
const shellTex = noiseTex(256, 21, 150, 110, 3);
const shellMat = new THREE.MeshPhysicalMaterial({ color: 0x3d3324, map: shellTex, roughness: 0.48, clearcoat: 0.45, clearcoatRoughness: 0.35, sheen: 0.4, sheenColor: new THREE.Color(0x4f7f95) });
const accMat = new THREE.MeshPhysicalMaterial({ color: 0xa8482a, roughness: 0.5, clearcoat: 0.3 });
const L = lobster(shellMat, { accent: accMat }); L.rotation.y = -0.85; L.position.set(0.05, 0.02, 0.35); scene.add(L);
// the old shell: pale, empty, the carapace lifted open where he climbed out
const oldMat = new THREE.MeshStandardMaterial({ color: 0xe6dccb, roughness: 0.8, transparent: true, opacity: 0.42, side: THREE.DoubleSide, emissive: 0x6a5a48, emissiveIntensity: 0.2, depthWrite: false });
const O = lobster(oldMat, { empty: true, lift: 0.35, tailShift: 0.06 }); O.rotation.y = 0.15; O.scale.setScalar(0.92); O.position.set(-1.35, 0.0, -0.95); scene.add(O);

// ---- light through the water: a soft gold shaft, and marine snow drifting in it
{ const g = new THREE.CylinderGeometry(0.4, 2.0, 7.5, 48, 1, true); g.translate(0, 3.75, 0);
  const m = new THREE.Mesh(g, new THREE.ShaderMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, fog: false,
    vertexShader: 'varying vec2 vU; varying vec3 vN, vV; void main(){ vU=uv; vec4 mv=modelViewMatrix*vec4(position,1.0); vN=normalize(normalMatrix*normal); vV=normalize(-mv.xyz); gl_Position=projectionMatrix*mv; }',
    fragmentShader: 'varying vec2 vU; varying vec3 vN, vV; void main(){ float e=pow(abs(dot(vN,vV)),2.0); float a=e*smoothstep(0.0,0.35,vU.y)*(1.0-smoothstep(0.7,1.0,vU.y)); gl_FragColor=vec4(vec3(1.0,0.78,0.45)*a*0.09,1.0); }' }));
  m.position.set(0.25, -0.05, 0.4); m.rotation.z = -0.06; scene.add(m); }
{ const R = rng(5), N = 1400, pos = new Float32Array(N * 3), sz = new Float32Array(N);
  for (let i = 0; i < N; i++) { pos.set([-5 + 10 * R(), 0.1 + 5 * R(), -5 + 8 * R()], i * 3); sz[i] = 0.4 + R(); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('sz', new THREE.BufferAttribute(sz, 1));
  scene.add(new THREE.Points(g, new THREE.ShaderMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false, uniforms: { uH: { value: H } },
    vertexShader: 'attribute float sz; uniform float uH; varying float vA; void main(){ vec4 mv=modelViewMatrix*vec4(position,1.0); vec3 w=(modelMatrix*vec4(position,1.0)).xyz; float inBeam=exp(-pow(length(w.xz-vec2(0.3,0.4))/1.4,2.0)); vA=(0.25+0.75*inBeam)*sz*exp(-max(0.0,-mv.z-3.0)*0.12); gl_Position=projectionMatrix*mv; gl_PointSize=clamp(0.012*uH/(-mv.z)*sz,1.0,8.0); }',
    fragmentShader: 'varying float vA; void main(){ float d=length(gl_PointCoord-0.5); gl_FragColor=vec4(vec3(1.0,0.9,0.75)*smoothstep(0.5,0.0,d)*vA*0.5,1.0); }' }))); }

const composer = new EffectComposer(renderer); composer.setSize(W, H);
composer.addPass(new RenderPass(scene, cam)); composer.addPass(new UnrealBloomPass(new THREE.Vector2(W, H), 0.35, 0.6, 0.82)); composer.addPass(new OutputPass());
window.render = () => { composer.render(); return renderer.domElement.toDataURL('image/png'); };
window.ready = true;
