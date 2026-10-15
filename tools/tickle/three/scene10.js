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
const AX = 1.1; // axis height (world) so worlds sit above the caption band

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

// ---------- stops (v2: the dreamer is in every world) ----------
const S = 34, R = 24, TR = 0.6, CREEP = 0.9;
const HS = [{k: 'sleeper', w: 8.6, A: 0}, {k: 'bedfall', w: 8.2, A: 1.2}, {k: 'brain', w: 10.4, A: 2.5}, {k: 'island', w: 6.9, A: 4.4}, {k: 'stairs', w: 20, A: 6.0}, {k: 'moon', w: 20, A: 7.8},
  {k: 'heart', w: 8.6, A: 9.4}, {k: 'boat', w: 7.4, A: 11.3}, {k: 'corridor', w: 8.2, A: 13.4}, {k: 'collage', w: 8.2, A: 15.0}, {k: 'whalecity', w: 8.2, A: 16.6}, {k: 'web', w: 8.2, A: 18.2},
  {k: 'heaven', w: 6.9, A: 19.8}, {k: 'eye', w: 8.6, A: 21.6}, {k: 'bed', w: 9.6, A: 23.4}];
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
const NF = 150, fr = [], fp = [], faArr = []; const corners = [[-1, -1], [1, -1], [1, 1], [-1, 1]];
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
const NS = 560, sp = [], sa = []; let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
for (let i = 0; i < NS; i++) { const th = rnd() * 6.283, r = 2.2 + rnd() * 12, z = 40 - rnd() * 560; for (let e = 0; e < 2; e++) { sp.push(Math.cos(th) * r, Math.sin(th) * r, z); sa.push(e, rnd()); } }
const sg = new THREE.BufferGeometry(); sg.setAttribute('position', new THREE.Float32BufferAttribute(sp, 3)); sg.setAttribute('aS', new THREE.Float32BufferAttribute(sa, 2));
const smat = new THREE.ShaderMaterial({uniforms: {uCamZ: {value: 0}, uSpeed: {value: 0}}, transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending,
  vertexShader: `attribute vec2 aS; uniform float uCamZ,uSpeed; varying float vA; void main(){ vec3 p=position; p.y+=${AX.toFixed(2)}; p.z+=aS.x*(0.8+16.0*uSpeed); float d=uCamZ-p.z; vA=smoothstep(1.0,6.0,d)*(1.0-smoothstep(20.0,70.0,d))*(0.10+0.9*uSpeed)*(0.5+0.5*aS.y)*(1.0-0.65*aS.x); gl_Position=projectionMatrix*viewMatrix*vec4(p,1.0); }`,
  fragmentShader: `varying float vA; void main(){ gl_FragColor=vec4(vec3(0.35,0.95,0.85)*vA,1.0); }`});
const streaks = new THREE.LineSegments(sg, smat); streaks.frustumCulled = false; streaks.renderOrder = 2; scene.add(streaks);

// ---------- extras ----------
const redLine = o => new THREE.LineBasicMaterial({color: new THREE.Color(1.0, 0.2, 0.14), transparent: true, opacity: o, blending: THREE.AdditiveBlending, depthTest: false, depthWrite: false});
const circPts = Array.from({length: 129}, (_, i) => new THREE.Vector3(Math.cos(i / 128 * 6.2832), Math.sin(i / 128 * 6.2832), 0));
const rings = Array.from({length: 4}, () => { const m = new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(circPts), redLine(0)); m.renderOrder = 4; m.frustumCulled = false; scene.add(m); return m; });
const faller = mkSprite('faller', 4.2), waveBack = mkSprite('wave', 11.4);

// ---------- captions (title stays up the whole time) ----------
const CAPS = [[0.1, 1.2, 'THIS IS A <em>DREAM.</em>'], [1.15, 2.4, 'AND IT FEELS <em>REAL.</em>'], [2.55, 4.3, 'SAME BRAIN.<br>DIFFERENT <em>STATE.</em>'], [4.5, 7.7, 'THE REALITY CHECK<br>IS <em>SWITCHED OFF.</em>'],
  [7.9, 9.3, 'IMPOSSIBLE PLACES<br>FEEL <em>BELIEVABLE.</em>'], [9.5, 13.3, 'THE EMOTIONS<br>ARE <em>REAL.</em>'], [13.5, 18.1, 'BUILT FROM<br><em>YOUR MEMORIES.</em>'], [18.3, 21.5, 'YOUR BRAIN <em>WEAVES</em><br>IT ALL IN REAL TIME.'],
  [21.7, 23.3, 'NOT REAL.<br>BUT <em>FELT REAL.</em>'], [23.5, 25.0, 'YOU WAKE UP.<br>IT ALL <em>FELT REAL.</em>']];
const elCap = document.getElementById('cap'), elFlash = document.getElementById('flash'), elBar = document.getElementById('bar'), elTitle = document.getElementById('title');
const beat = p => Math.exp(-p * 6.0);
window.renderAt = t => {
  t = Math.min(Math.max(t, 0), DUR); const cz = camZ(t), tr = trans(t), bump = tr.u >= 0 ? Math.sin(Math.PI * tr.u) : 0, W0 = 2 * Math.PI / DUR;
  camera.fov = 40 + 11 * bump; camera.updateProjectionMatrix();
  camera.position.set(0.42 * Math.sin(W0 * 2 * t), 0.22 * Math.cos(W0 * 3 * t), cz);
  camera.up.set(0, 1, 0); camera.lookAt(0, 0, cz - 10); camera.rotateZ(0.025 * Math.sin(W0 * 2 * t + 1) + (tr.i >= 0 ? (tr.i % 2 ? 1 : -1) * 0.5 * bump : 0));
  fmat.uniforms.uCamZ.value = cz; fmat.uniforms.uTime.value = t; smat.uniforms.uCamZ.value = cz; smat.uniforms.uSpeed.value = bump;
  let flash = 0; const at = k => HS.findIndex(h => h.k === k);
  waveBack.visible = faller.visible = false;
  HS.forEach((h, i) => {
    const d = cz - h.z, lt = t - h.A; const op = sm((d - 1.5) / 5.5) * (1 - sm((d - 36) / 16)); const o = {op, rz: 0, s: 1, red: 1, teal: 1}; let x = 0, y = 0; const pulse = (f, p = 0) => 0.5 + 0.5 * Math.sin(lt * f + p);
    switch (h.k) {
      case 'sleeper': { const z = sm(lt / 1.1); o.s = 1 + 0.45 * z; y = -1.1 * z; o.red = 1.2 + 2.4 * pulse(9); o.rz = 0.01 * Math.sin(W0 * 3 * t); break; }
      case 'bedfall': o.rz = 0.03 * Math.sin(lt * 2.5); o.red = 1.3 + 1.6 * pulse(8); o.s = 1 + 0.05 * lt; break;
      case 'brain': o.red = 1.0 + 1.4 * pulse(7, 1); o.s = 1 + 0.03 * lt; break;
      case 'island': o.red = 1.0 + 2.2 * pulse(10); y = 0.5 * lt; o.rz = 0.02 * Math.sin(lt * 9); break;
      case 'stairs': x = lerp(4.0, -4.4, ease(lt / 1.7)); o.red = 1 + 1.6 * pulse(6); break;
      case 'moon': x = lerp(4.2, -1.4, ease(lt / 1.7)); o.red = 0.85 + 0.35 * pulse(5); break;
      case 'heart': { const p = (lt * 1.9) % 1; o.s = 1 + 0.06 * beat(p); o.red = 1.0 + 2.2 * beat(p); break; }
      case 'boat': { y = -2.0 + 0.25 * Math.sin(lt * 3.2); o.rz = 0.05 * Math.sin(lt * 2.6); o.red = 1.3 + 1.2 * pulse(7); break; }
      case 'corridor': o.s = 1 + 0.04 * lt; o.red = 1.2 + 1.4 * pulse(6); break;
      case 'collage': o.rz = 0.025 * lt; o.s = 1 + 0.03 * lt; o.red = 1.2 + 1.2 * pulse(6); break;
      case 'whalecity': o.s = 1 + 0.045 * lt; x = -0.15 * lt; o.red = 1.3 + 1.2 * pulse(6); break;
      case 'web': o.s = 1 + 0.04 * lt; o.rz = 0.02 * Math.sin(lt * 2); o.red = 1.0 + 1.6 * pulse(8); break;
      case 'heaven': o.s = 1 + 0.04 * lt; o.red = 1.0 + 1.0 * pulse(6); break;
      case 'eye': o.s = 1 + 0.04 * lt; o.red = 1.0 + 1.5 * pulse(7); break;
      case 'bed': { o.s = 1 + 0.012 * Math.sin(W0 * 9 * t); o.red = 1.2 + 0.5 * Math.sin(W0 * 8 * t); const w = sm((t - 24.1) / 0.1) * (1 - sm((t - 24.25) / 0.5)); flash = Math.max(flash, 0.12 * w); break; }
    }
    setSp(h.sp, x, y, h.z, o); h.op = op; h.lt = lt;
    if (h.k === 'boat') { setSp(waveBack, 0, lerp(-6.2, 0.1, sm(lt / 1.6)) , h.z - 0.6, {op: op * 0.95, red: 1.1 + 1.6 * beat((t * 1.9) % 1), s: 1}); waveBack.visible = op > 0.004; }
    if (h.k === 'heart') { setSp(faller, 0, -0.3, h.z + 0.4, {op: op * 0.85, rz: -0.6 + 0.25 * Math.sin(lt * 2), s: 0.55 + 0.05 * Math.sin(lt * 3), red: 1.6}); faller.visible = op > 0.004; }
  });
  { const hh = HS[at('heart')], ww = HS[at('boat')], on = Math.max(hh.op, ww.op * 0.8), zb = hh.op >= ww.op ? hh.z : ww.z; rings.forEach((r, n) => { const p = ((t * 1.9) + n * 0.25) % 1; r.position.set(0, AX - 0.2, zb + 0.5); r.scale.setScalar(1.0 + p * 7.5); r.material.opacity = 0.75 * (1 - p) * on; r.visible = r.material.opacity > 0.01; }); }
  renderer.render(scene, camera);
  elFlash.style.opacity = flash; elBar.style.width = (100 * t / DUR).toFixed(2) + '%';
  const tw = t > 0.9 && t < 2.2 ? 1 : 0, tr2 = t > 21.4 && t < 24.9 ? 1 : 0; elTitle.innerHTML = 'WHY DO <em class="' + (tw ? 'on' : '') + '">DREAMS</em> FEEL <em>REAL?</em>';
  let cs = ''; CAPS.forEach(([a, b, txt]) => { const k = sm((t - a) / 0.2) * (1 - sm((t - (b - 0.2)) / 0.2)); if (k > 0.01) cs += `<div style="opacity:${k.toFixed(3)};transform:translateY(${((1 - k) * 12).toFixed(1)}px)">${txt}</div>`; });
  elCap.innerHTML = cs;
};
window.ready = true; window.renderAt(0);
