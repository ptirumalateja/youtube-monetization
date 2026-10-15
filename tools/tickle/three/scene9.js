// "Why do dreams feel real" (25 s, 9:16). One continuous dive down a tunnel of frames; each world is a Meta contour-art sprite on the axis.
// Grammar (Format B): teal contour = the world, red = the dream signal only (portal glow, nodes, heart core, crest, cubes, pupil); camera flies THROUGH each world into the next (match-move on its centre).
import * as THREE from 'three';
const QP = new URLSearchParams(location.search); const W = +(QP.get('w') || 1080), H = +(QP.get('h') || 1920), DUR = 25;
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x)), sm = x => { x = clamp(x); return x * x * (3 - 2 * x); }, lerp = (a, b, t) => a + (b - a) * t;
const ease = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const renderer = new THREE.WebGLRenderer({antialias: true, preserveDrawingBuffer: true}); renderer.setPixelRatio(1); renderer.setSize(W, H); renderer.setClearColor(0x02050a, 1);
document.body.appendChild(renderer.domElement); document.body.style.width = W + 'px'; document.body.style.height = H + 'px';
const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(40, W / H, 0.1, 900);
const META = await (await fetch('./assets/dreams/meta.json')).json();
const TX = {};
for (const k of Object.keys(META)) { const t = await new THREE.TextureLoader().loadAsync(`./assets/dreams/${k}.jpg`); t.colorSpace = THREE.NoColorSpace; t.anisotropy = 8; TX[k] = t; }
const AX = 1.4; // axis height (world) so worlds sit above the caption band

// ---------- sprite (colour-preserving, additive) ----------
const spriteMat = tex => new THREE.ShaderMaterial({
  uniforms: {uTex: {value: tex}, uOp: {value: 1}, uRed: {value: 1}, uTeal: {value: 1}, uFlash: {value: 0}},
  transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
  vertexShader: `varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
  fragmentShader: `uniform sampler2D uTex; uniform float uOp,uRed,uTeal,uFlash; varying vec2 vUv;
    void main(){ vec3 c=texture2D(uTex,vUv).rgb; float rm=clamp((c.r-0.55*c.g-0.04)*3.0,0.0,1.0);
      c*=mix(uTeal,uRed,rm); vec2 e=min(vUv,1.0-vUv); float f=smoothstep(0.0,0.07,min(e.x,e.y));
      gl_FragColor=vec4(c*f*uOp+vec3(uFlash),1.0); }`
});
const mkSprite = (k, w) => { const [pw, ph] = META[k], m = new THREE.Mesh(new THREE.PlaneGeometry(w, w * ph / pw), spriteMat(TX[k])); m.frustumCulled = false; m.renderOrder = 3; scene.add(m); return m; };
const setSp = (m, x, y, z, o = {}) => { m.position.set(x, y + AX, z); m.rotation.z = o.rz || 0; m.scale.setScalar(o.s || 1); const u = m.material.uniforms; u.uOp.value = o.op ?? 1; u.uRed.value = o.red ?? 1; u.uTeal.value = o.teal ?? 1; m.visible = u.uOp.value > 0.004; };

// ---------- stops ----------
const S = 34, R = 24, TR = 0.85, CREEP = 1.0;
const HS = [{k: 'bed', w: 9.4, A: 0}, {k: 'portal', w: 9.8, A: 1.4}, {k: 'brain', w: 9.8, A: 2.5}, {k: 'face', w: 10.4, A: 5.0}, {k: 'stairs', w: 11, A: 7.0}, {k: 'heart', w: 9.4, A: 9.2},
  {k: 'wave', w: 11.4, A: 11.6}, {k: 'city', w: 11.4, A: 14.0}, {k: 'eye', w: 10.2, A: 17.2}, {k: 'vortex', w: 10.2, A: 19.4}, {k: 'bed', w: 9.4, A: 22.0}];
const N = HS.length; HS.forEach((h, i) => { h.z = -S * i; h.sp = mkSprite(h.k, h.w); });
function camZ(t) {
  for (let i = 0; i < N; i++) {
    const A = HS[i].A, nxt = i < N - 1 ? HS[i + 1].A : 1e9, D = nxt - TR;
    if (t < nxt) { const zi = HS[i].z, cr = i === N - 1 ? 0 : CREEP; if (t < D || i === N - 1) return zi + R - cr * (t - A);
      const e0 = zi + R - cr * (D - A), e1 = HS[i + 1].z + R; return lerp(e0, e1, ease((t - D) / TR)); }
  } return HS[N - 1].z + R;
}
function trans(t) { for (let i = 0; i < N - 1; i++) { const D = HS[i + 1].A - TR; if (t >= D && t < HS[i + 1].A) return {u: (t - D) / TR, i}; } return {u: -1, i: -1}; }

// ---------- tunnel of frames ----------
const NF = 100, fr = [], fp = [], faArr = []; const corners = [[-1, -1], [1, -1], [1, 1], [-1, 1]];
for (let i = 0; i < NF; i++) {
  const z = 40 - i * 4.2, size = 5.2 + 3.2 * ((i * 0.61803) % 1), red = i % 9 === 4 ? 1 : 0, ang = i * 0.21;
  for (let c = 0; c < 3; c++) { const s = size * (1 - c * 0.035); for (let e = 0; e < 4; e++) { const a = corners[e], b = corners[(e + 1) % 4]; fp.push(a[0] * s, a[1] * s, 0, b[0] * s, b[1] * s, 0); for (let q = 0; q < 2; q++) faArr.push(z, red, ang, 1 - c * 0.3); } }
}
const fg = new THREE.BufferGeometry(); fg.setAttribute('position', new THREE.Float32BufferAttribute(fp, 3)); fg.setAttribute('aF', new THREE.Float32BufferAttribute(faArr, 4));
const fmat = new THREE.ShaderMaterial({uniforms: {uCamZ: {value: 0}, uTime: {value: 0}, uAmp: {value: 1}, uRedAmp: {value: 1}}, transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending,
  vertexShader: `attribute vec4 aF; uniform float uCamZ,uTime; varying float vA; varying float vR;
    void main(){ float a=aF.z+aF.x*0.045+uTime*0.10; mat2 m=mat2(cos(a),sin(a),-sin(a),cos(a)); vec2 p=m*position.xy; float d=uCamZ-aF.x;
      vA=smoothstep(3.0,12.0,d)*(1.0-smoothstep(18.0,60.0,d))*aF.w*0.6; vR=aF.y; gl_Position=projectionMatrix*viewMatrix*vec4(p.x,p.y+${AX.toFixed(2)},aF.x,1.0); }`,
  fragmentShader: `uniform float uAmp,uRedAmp; varying float vA; varying float vR; void main(){ vec3 c=mix(vec3(0.10,0.80,0.68)*0.55,vec3(1.0,0.16,0.12)*0.8*uRedAmp,vR); gl_FragColor=vec4(c*vA*uAmp,1.0); }`});
const frames = new THREE.LineSegments(fg, fmat); frames.frustumCulled = false; frames.renderOrder = 1; scene.add(frames);

// ---------- speed streaks + dust ----------
const NS = 420, sp = [], sa = []; let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
for (let i = 0; i < NS; i++) { const th = rnd() * 6.283, r = 2.2 + rnd() * 12, z = 40 - rnd() * 420; for (let e = 0; e < 2; e++) { sp.push(Math.cos(th) * r, Math.sin(th) * r, z); sa.push(e, rnd()); } }
const sg = new THREE.BufferGeometry(); sg.setAttribute('position', new THREE.Float32BufferAttribute(sp, 3)); sg.setAttribute('aS', new THREE.Float32BufferAttribute(sa, 2));
const smat = new THREE.ShaderMaterial({uniforms: {uCamZ: {value: 0}, uSpeed: {value: 0}}, transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending,
  vertexShader: `attribute vec2 aS; uniform float uCamZ,uSpeed; varying float vA; void main(){ vec3 p=position; p.y+=${AX.toFixed(2)}; p.z+=aS.x*(0.8+16.0*uSpeed); float d=uCamZ-p.z; vA=smoothstep(1.0,6.0,d)*(1.0-smoothstep(20.0,70.0,d))*(0.10+0.9*uSpeed)*(0.5+0.5*aS.y)*(1.0-0.65*aS.x); gl_Position=projectionMatrix*viewMatrix*vec4(p,1.0); }`,
  fragmentShader: `varying float vA; void main(){ gl_FragColor=vec4(vec3(0.35,0.95,0.85)*vA,1.0); }`});
const streaks = new THREE.LineSegments(sg, smat); streaks.frustumCulled = false; streaks.renderOrder = 2; scene.add(streaks);

// ---------- extras ----------
const redLine = o => new THREE.LineBasicMaterial({color: new THREE.Color(1.0, 0.2, 0.14), transparent: true, opacity: o, blending: THREE.AdditiveBlending, depthTest: false, depthWrite: false});
const cubeGeo = new THREE.EdgesGeometry(new THREE.BoxGeometry(1, 1, 1));
const cubes = Array.from({length: 44}, (_, i) => { const m = new THREE.LineSegments(cubeGeo, redLine(0.9)); m.renderOrder = 4; m.frustumCulled = false; m.userData = {s: 0.25 + rnd() * 0.65, y: lerp(-3.5, 4.0, rnd()), v: 0.6 + rnd() * 0.9, ph: i / 44, r: rnd() * 6, rv: 0.4 + rnd() * 1.2, z: rnd() * 5 - 1}; scene.add(m); return m; });
const circPts = Array.from({length: 129}, (_, i) => new THREE.Vector3(Math.cos(i / 128 * 6.2832), Math.sin(i / 128 * 6.2832), 0));
const rings = Array.from({length: 4}, () => { const m = new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(circPts), redLine(0)); m.renderOrder = 4; m.frustumCulled = false; scene.add(m); return m; });
const whale = mkSprite('whale', 9.0), train = mkSprite('train', 8.0), stairsEcho = [mkSprite('stairs', 11), mkSprite('stairs', 11), mkSprite('stairs', 11)];
const portalGlow = (() => { const c = document.createElement('canvas'); c.width = c.height = 128; const x = c.getContext('2d'), g = x.createRadialGradient(64, 64, 0, 64, 64, 64); g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(.25, 'rgba(255,70,50,.75)'); g.addColorStop(1, 'rgba(255,40,30,0)'); x.fillStyle = g; x.fillRect(0, 0, 128, 128);
  const s = new THREE.Sprite(new THREE.SpriteMaterial({map: new THREE.CanvasTexture(c), blending: THREE.AdditiveBlending, depthTest: false, transparent: true, depthWrite: false})); s.renderOrder = 5; scene.add(s); return s; })();

// ---------- captions ----------
const CAPS = [[0.15, 1.2, 'head', 'THIS IS A <em>DREAM.</em>'], [1.1, 2.3, 'head', 'AND IT FEELS <em>REAL.</em>'], [2.6, 4.9, 'cap', 'SAME BRAIN.<br>DIFFERENT <em>STATE.</em>'], [5.1, 8.9, 'cap', 'THE REALITY CHECK<br>IS <em>SWITCHED OFF.</em>'],
  [9.3, 13.9, 'cap', 'THE EMOTIONS ARE <em>REAL.</em><br>THE WORLD ISN’T.'], [14.1, 19.2, 'cap', 'BUILT FROM <em>YOUR MEMORIES.</em>'], [19.5, 21.9, 'cap', 'AND YOU BELIEVE<br><em>ALL OF IT.</em>'], [22.1, 25.0, 'cap', 'UNTIL YOU <em>WAKE UP.</em>']];
const elHead = document.getElementById('head'), elCap = document.getElementById('cap'), elFlash = document.getElementById('flash');

const beat = p => Math.exp(-p * 6.0);
window.renderAt = t => {
  t = Math.min(Math.max(t, 0), DUR); const cz = camZ(t), tr = trans(t), bump = tr.u >= 0 ? Math.sin(Math.PI * tr.u) : 0;
  const W0 = 2 * Math.PI / DUR;
  camera.fov = 40 + 11 * bump; camera.updateProjectionMatrix();
  camera.position.set(0.42 * Math.sin(W0 * 2 * t), 0.22 * Math.cos(W0 * 3 * t), cz);
  camera.up.set(0, 1, 0); camera.lookAt(0.0, AX * 0.0, cz - 10); camera.rotateZ(0.025 * Math.sin(W0 * 2 * t + 1) + (tr.i >= 0 ? (tr.i % 2 ? 1 : -1) * 0.5 * bump : 0));
  fmat.uniforms.uCamZ.value = cz; fmat.uniforms.uTime.value = t; smat.uniforms.uCamZ.value = cz; smat.uniforms.uSpeed.value = bump;
  let flash = 0;
  HS.forEach((h, i) => {
    const d = cz - h.z, lt = t - h.A; let op = sm((d - 1.5) / 5.5) * (1 - sm((d - 36) / 16)); const o = {op, rz: 0, s: 1, red: 1, teal: 1}; let x = 0, y = 0;
    switch (h.k) {
      case 'bed': o.s = 1 + 0.012 * Math.sin(W0 * 9 * t); o.red = 1.3 + 0.6 * Math.sin(W0 * 8 * t); o.rz = 0.015 * Math.sin(W0 * 3 * t); break;
      case 'portal': o.rz = 0.05 * Math.sin(lt * 3); o.red = 1.5 + 0.8 * Math.sin(lt * 9); y = -0.2 * lt; break;
      case 'brain': o.red = 1.0 + 1.6 * (0.5 + 0.5 * Math.sin(lt * 7 + 1)) ; o.teal = 0.8; o.s = 1 + 0.015 * Math.sin(lt * 7); break;
      case 'face': o.rz = -0.04 + 0.03 * lt; break;
      case 'stairs': o.red = 0.8 + 3.0 * (0.5 + 0.5 * Math.sin(lt * 6)); o.rz = 0.04 * Math.sin(lt * 1.5); break;
      case 'heart': { const p = (lt * 1.8) % 1; o.s = 1 + 0.07 * beat(p); o.red = 1.0 + 2.2 * beat(p); break; }
      case 'wave': { y = lerp(-6.0, 0.2, sm(lt / 2.2)); const p = (t * 1.8) % 1; o.red = 1.1 + 1.6 * beat(p); o.s = 1 + 0.02 * beat(p); break; }
      case 'city': o.red = 0.62 + 0.12 * Math.sin(lt * 5); o.s = 1.0 + 0.012 * lt; break;
      case 'eye': { o.red = 1.0 + 1.8 * (0.5 + 0.5 * Math.sin(lt * 5)); o.s = 1 + 0.05 * sm(lt / 2.5); break; }
      case 'vortex': o.rz = lt * 0.9; o.red = 1.0 + 1.0 * Math.sin(lt * 6); break;
    }
    if (i === N - 1) { const w = sm((t - 23.8) / 0.12) * (1 - sm((t - 23.95) / 0.5)); flash = Math.max(flash, 0.12 * w); }
    h.sp.material.uniforms.uFlash.value = 0; setSp(h.sp, x, y, h.z, o);
    h.op = op; h.lt = lt;
  });
  const at = k => HS.findIndex(h => h.k === k);
  // red wire cubes streaming off the stone face
  { const h = HS[at('face')], v = h.op; cubes.forEach(c => { const u = c.userData, p = (h.lt * 0.22 * u.v + u.ph) % 1, x = 0.8 + p * 6.4, vis = Math.sin(Math.PI * p) * v * (h.lt > -2 ? 1 : 0);
    c.position.set(x, u.y * (0.55 + p * 0.5) + AX, h.z + u.z); c.rotation.set(u.r + h.lt * u.rv, u.r * 0.7 + h.lt * u.rv * 0.8, 0); c.scale.setScalar(u.s * (0.7 + p * 0.5)); c.material.opacity = 0.9 * vis; c.visible = vis > 0.01; }); }
  // stair echoes (the loop that never ends)
  { const h = HS[at('stairs')]; stairsEcho.forEach((m, n) => { const sc = Math.pow(0.58, n + 1), pu = (h.lt * 0.35 + n * 0.33) % 1; setSp(m, 0, 0, h.z - 1 - n * 0.6, {s: sc * (1 + 0.1 * pu), rz: (n + 1) * 0.28 + h.lt * 0.25, op: h.op * Math.pow(0.55, n + 1) * 1.1, red: 1 + 1.5 * Math.sin(h.lt * 6 + n)}); }); }
  // heart ripples (also carry into the wave world)
  { const hh = HS[at('heart')], ww = HS[at('wave')], on = Math.max(hh.op, ww.op * 0.8), zb = hh.op >= ww.op ? hh.z : ww.z; rings.forEach((r, n) => { const p = ((t * 1.8) / 1 + n * 0.25) % 1, k = p * (n % 2 ? 1 : 1); r.position.set(0, AX - 0.2, zb + 0.5); r.scale.setScalar(1.0 + p * 7.5); r.material.opacity = 0.75 * (1 - p) * on; r.visible = r.material.opacity > 0.01; }); }
  // memory collage: whale + train cross the floating city at different depths (parallax)
  { const h = HS[at('city')], v = h.op; setSp(whale, lerp(-11, 11, clamp((h.lt + 0.2) / 4.2)), 1.2 + 0.9 * Math.sin(h.lt * 1.4), h.z + 6, {op: 0.95 * v * sm((h.lt + 0.2) / 0.5), s: 1, red: 1, rz: 0.06 * Math.sin(h.lt * 1.4)});
    setSp(train, lerp(13, -13, clamp((h.lt - 0.6) / 3.0)), -3.2, h.z + 10.5, {op: 0.95 * v * sm((h.lt - 0.5) / 0.4) * (1 - sm((h.lt - 3.8) / 0.4)), s: 1.0}); }
  // red portal glow (hook transition)
  { const h = HS[at('portal')], g = h.op; portalGlow.position.set(0, AX + 1.4, h.z + 0.3); portalGlow.scale.setScalar(5.0 + 1.2 * Math.sin(h.lt * 9)); portalGlow.material.opacity = 0.55 * g; portalGlow.visible = g > 0.01; }
  renderer.render(scene, camera);
  elFlash.style.opacity = flash;
  let hs = '', cs = ''; CAPS.forEach(([a, b, w, txt]) => { const k = sm((t - a) / 0.22) * (1 - sm((t - (b - 0.22)) / 0.22)); if (k > 0.01) { const s = `<div style="opacity:${k.toFixed(3)};transform:translateY(${((1 - k) * 12).toFixed(1)}px)">${txt}</div>`; if (w === 'head') hs += s; else cs += s; } });
  elHead.innerHTML = hs; elCap.innerHTML = cs;
};
window.ready = true; window.renderAt(0);
