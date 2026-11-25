// Same Size, 3D version. Two renders from one page:
//   ?mode=corridor   a long dark concrete corridor, glossy tiled floor, warm ceiling lights fading into haze, a gold
//                    glow at the far end. window.info gives the screen position of two floor spots (near, far) and how
//                    many pixels a 1.8 m person would be at each, so the compositor can place the figures.
//   ?mode=figure     one Slow Light stickman (series rig), standing, turned toward the camera, on a transparent background.
// The figure is pasted twice at exactly the same pixel size by ../same_size_3d.py: that is the illusion.
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { Reflector } from 'three/addons/objects/Reflector.js';
import * as SLD from './sld.js';
const { V, rng, PAL } = SLD;

const q = new URLSearchParams(location.search); const W = +q.get('w') || 1080, H = +q.get('h') || 1350, MODE = q.get('mode') || 'corridor';
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: MODE === 'figure', preserveDrawingBuffer: true });
renderer.setSize(W, H, false); renderer.setPixelRatio(1); renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.0;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene();
const cam = new THREE.PerspectiveCamera(52, W / H, 0.1, 200);

function tileTex() {   // dark polished tiles with thin grout lines
  const c = document.createElement('canvas'); c.width = c.height = 512; const g = c.getContext('2d'); const R = rng(4);
  for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) { const v = 58 + R() * 14; g.fillStyle = `rgb(${v},${v * 0.98},${v * 0.95})`; g.fillRect(i * 128, j * 128, 128, 128); }
  for (let k = 0; k < 2500; k++) { const v = 40 + R() * 30; g.fillStyle = `rgba(${v},${v},${v},0.25)`; g.fillRect(R() * 512, R() * 512, 2, 2); }
  g.strokeStyle = 'rgb(14,13,12)'; g.lineWidth = 7; for (let i = 0; i <= 4; i++) { g.beginPath(); g.moveTo(i * 128, 0); g.lineTo(i * 128, 512); g.stroke(); g.beginPath(); g.moveTo(0, i * 128); g.lineTo(512, i * 128); g.stroke(); }
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; }
function concreteTex() {
  const c = document.createElement('canvas'); c.width = c.height = 512; const g = c.getContext('2d'); const R = rng(8);
  g.fillStyle = 'rgb(70,68,64)'; g.fillRect(0, 0, 512, 512);
  for (let k = 0; k < 9000; k++) { const v = 50 + R() * 50; g.fillStyle = `rgba(${v},${v * 0.98},${v * 0.94},0.18)`; g.fillRect(R() * 512, R() * 512, 1 + R() * 4, 1 + R() * 4); }
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; return t; }

if (MODE === 'corridor') {
  const HAZE = new THREE.Color(0x1a1612); scene.background = HAZE; scene.fog = new THREE.FogExp2(HAZE, 0.02);
  cam.position.set(0, 1.55, 4); cam.lookAt(0, 1.75, -40);
  const CW = 4.2, CH = 4.6, LEN = 90;                                            // corridor width, height, length
  const tiles = tileTex(); tiles.repeat.set(CW / 1.2, LEN / 1.2);
  const mirror = new Reflector(new THREE.PlaneGeometry(CW, LEN), { textureWidth: W, textureHeight: H, color: 0x7a7470 });
  mirror.rotation.x = -Math.PI / 2; mirror.position.set(0, -0.002, -LEN / 2 + 5); scene.add(mirror);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(CW, LEN), new THREE.MeshStandardMaterial({ map: tiles, roughness: 0.35, metalness: 0.1, color: 0xd8d2c8, transparent: true, opacity: 0.8 }));
  floor.rotation.x = -Math.PI / 2; floor.position.set(0, 0, -LEN / 2 + 5); floor.receiveShadow = true; scene.add(floor);
  const ct = concreteTex(); ct.repeat.set(LEN / 4, 1.2);
  const wallMat = new THREE.MeshStandardMaterial({ map: ct, roughness: 0.92, color: 0x9a9690 });
  for (const s of [-1, 1]) { const w = new THREE.Mesh(new THREE.PlaneGeometry(LEN, CH), wallMat); w.rotation.y = -s * Math.PI / 2; w.position.set(s * CW / 2, CH / 2, -LEN / 2 + 5); w.receiveShadow = true; scene.add(w); }
  const ceil = new THREE.Mesh(new THREE.PlaneGeometry(CW, LEN), new THREE.MeshStandardMaterial({ color: 0x3a3834, roughness: 0.95 })); ceil.rotation.x = Math.PI / 2; ceil.position.set(0, CH, -LEN / 2 + 5); scene.add(ceil);
  // ribs every 3 m (a frame around the corridor), and a warm ceiling light in every other bay
  const ribMat = new THREE.MeshStandardMaterial({ color: 0x55524c, roughness: 0.8 });
  const lampMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(0xffd9a0).multiplyScalar(1.6) });
  for (let z = 2; z > -LEN + 5; z -= 3) {
    for (const s of [-1, 1]) { const p = new THREE.Mesh(new THREE.BoxGeometry(0.3, CH, 0.35), ribMat); p.position.set(s * (CW / 2 - 0.15), CH / 2, z); p.castShadow = p.receiveShadow = true; scene.add(p); }
    const b = new THREE.Mesh(new THREE.BoxGeometry(CW, 0.3, 0.35), ribMat); b.position.set(0, CH - 0.15, z); scene.add(b);
    if (((z - 2) / 3) % 2 === 0) { const l = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.05, 0.22), lampMat); l.position.set(0, CH - 0.03, z - 1.5); scene.add(l);
      if (z > -40) { const pl = new THREE.PointLight(0xffc98a, 16, 11, 1.5); pl.position.set(0, CH - 0.4, z - 1.5); scene.add(pl); } } }
  // the far end: an open doorway full of gold light
  const end = new THREE.Mesh(new THREE.PlaneGeometry(CW, CH), new THREE.MeshBasicMaterial({ color: new THREE.Color(0xffc670).multiplyScalar(2.2), fog: false })); end.position.set(0, CH / 2, -LEN + 5); scene.add(end);
  const endL = new THREE.SpotLight(0xffc26a, 400, 70, 0.5, 0.9, 1.2); endL.position.set(0, 2.2, -LEN + 6); endL.target.position.set(0, 0, 0); scene.add(endL, endL.target);
  scene.add(new THREE.HemisphereLight(0x8a7a66, 0x1a1612, 0.5));
  window.spots = { near: [-0.75, -1.6], far: [0.35, -19] };   // floor spots (x, z) for the two figures
} else {
  const R = SLD.createRig(scene);
  const hero = R.makeFig(PAL.CREAM, 'hero', { rim: 0.3, rimCol: 0xffd9a0, lift: 0.06 });
  const P = { ...R.P0, p: 0.03, tilt: -0.05, sL: 0.18, sR: 0.12, eL: 0.25, eR: 0.3, aL: 0.06, aR: -0.08, kL: 0.04, kR: 0.08 };
  const J = R.skel(P, V(0, 0, 0), -1.4); R.poseFig(hero, J);
  // lit like the corridor: warm from above and slightly in front, gold rim from the far end behind
  const k = new THREE.DirectionalLight(0xffd6a0, 2.4); k.position.set(0.5, 4, 3); scene.add(k);
  const r = new THREE.DirectionalLight(0xffb85a, 3.2); r.position.set(0, 1.5, -5); scene.add(r);
  scene.add(new THREE.HemisphereLight(0x8a7a66, 0x1a1612, 0.6));
  cam.fov = 18; cam.position.set(0, 1.0, 7.4); cam.lookAt(0, 0.92, 0); cam.updateProjectionMatrix();
  // report the feet and head in screen space, so the sprite can be cropped tight and scaled by its true height
  window.figBox = () => { const pr = v => { const p = v.clone().project(cam); return [(p.x * 0.5 + 0.5) * W, (0.5 - p.y * 0.5) * H]; };
    return { foot: pr(V(0, 0, 0)), head: pr(J.head.clone().add(V(0, 0.15, 0))) }; };
}
cam.updateProjectionMatrix(); cam.updateMatrixWorld();
const composer = new EffectComposer(renderer); composer.setSize(W, H); composer.addPass(new RenderPass(scene, cam));
if (MODE === 'corridor') composer.addPass(new UnrealBloomPass(new THREE.Vector2(W, H), 0.55, 0.7, 0.85));
composer.addPass(new OutputPass());
window.info = () => { if (!window.spots) return window.figBox ? window.figBox() : null; const o = {};
  for (const [k, [x, z]] of Object.entries(window.spots)) { const f = V(x, 0, z).project(cam), h = V(x, 1.8, z).project(cam);
    o[k] = { foot: [(f.x * 0.5 + 0.5) * W, (0.5 - f.y * 0.5) * H], h18: (h.y - f.y) * 0.5 * H }; } return o; };
window.render = () => { (MODE === 'figure' ? renderer.render(scene, cam) : composer.render()); return renderer.domElement.toDataURL('image/png'); };
window.ready = true;
