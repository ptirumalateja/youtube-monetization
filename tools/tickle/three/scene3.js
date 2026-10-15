// Scene 2: smooth skinned wire-mesh hand (bone white), predicted ghost (teal), deformable planes of predicted space,
// red contact point that bends the space. Opening 01A-01D of the storyboard.
import * as THREE from 'three';
const QP = new URLSearchParams(location.search); const W = +(QP.get('w') || 1080), H = +(QP.get('h') || 1920), LEAD = 0.5;
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x)), sm = x => { x = clamp(x); return x * x * (3 - 2 * x); }, lerp = (a, b, t) => a + (b - a) * t;
const WHITE = new THREE.Color(1.25, 1.18, 1.02), TEAL = new THREE.Color(0.12, 0.9, 0.78), RED = new THREE.Color(1.0, 0.16, 0.12);

const renderer = new THREE.WebGLRenderer({antialias: true, preserveDrawingBuffer: true});
renderer.setPixelRatio(1); renderer.setSize(W, H); renderer.setClearColor(0x02050a, 1);
document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(38, W / H, 0.1, 400);

// ---------- hand art: Meta AI contour-line hand, extracted to alpha (assets/hand_point_side.png), layered for depth ----------
const tex = await new THREE.TextureLoader().loadAsync('./assets/hand_point_side.png'); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8; tex.minFilter = THREE.LinearMipmapLinearFilter;
const PW = 40, PH = 20, TIPLOC = new THREE.Vector3((1318 / 2000 - 0.5) * PW, (0.5 - 415 / 1000) * PH, 0);   // fingertip in plane-local units
const handMat = (tint, op) => new THREE.ShaderMaterial({
  uniforms: {uTex: {value: tex}, uTint: {value: tint}, uOp: {value: op}, uTime: {value: 0}, uWave: {value: 0}, uBend: {value: 0}},
  transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
  vertexShader: `uniform float uTime; uniform float uWave; uniform float uBend; varying vec2 vUv;
    void main(){ vUv=uv; vec3 p=position; float f=smoothstep(0.45,1.0,uv.x);
      p.y+= uBend*f*f*4.0 + uWave*0.5*sin(uv.x*16.0-uTime*4.0)*f; gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.0); }`,
  fragmentShader: `uniform sampler2D uTex; uniform vec3 uTint; uniform float uOp; varying vec2 vUv;
    void main(){ float a=texture2D(uTex,vUv).a*smoothstep(0.0,0.16,vUv.x); gl_FragColor=vec4(uTint*a*uOp,1.0); }`
});
function makeSpriteHand(layers) {
  const g = new THREE.Group(); g.layers_ = [];
  layers.forEach(([z, tint, op]) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(PW, PH, 60, 30), handMat(tint, op)); m.position.z = z; m.renderOrder = 3; m.frustumCulled = false; g.add(m); g.layers_.push(m); });
  scene.add(g); return g;
}
const BONE = new THREE.Color(1.3, 1.22, 1.05), TL = new THREE.Color(0.14, 0.95, 0.8);
const real = makeSpriteHand([[0.0, BONE, 1.0], [-0.5, TL, 0.42], [-1.0, TL, 0.26]]);
const ghost = makeSpriteHand([[0.0, TL, 0.8], [-0.6, TL, 0.36]]);
const trail1 = makeSpriteHand([[0, TL, 0.3]]), trail2 = makeSpriteHand([[0, TL, 0.16]]);
function placeHand(h, tip, alpha, t, wave, bend, rz) {
  h.position.set(tip.x - TIPLOC.x, tip.y - TIPLOC.y, tip.z - TIPLOC.z); h.rotation.set(0, 0, rz || 0); h.visible = alpha > 0.003;
  h.layers_.forEach((m, i) => { m.material.uniforms.uTime.value = t; m.material.uniforms.uWave.value = wave; m.material.uniforms.uBend.value = bend; m.material.uniforms.uOp.value = (m.userData.base ??= m.material.uniforms.uOp.value) * alpha; });
}
// ---------- planes of predicted space (deformable), field plane, target ----------
const TARGET = new THREE.Vector3(33.5, 2.2, 0);
const planeMat = (tint, base) => new THREE.ShaderMaterial({
  uniforms: {uT: {value: TARGET}, uPinch: {value: 0}, uTime: {value: 0}, uTint: {value: tint}, uBase: {value: base}, uFade: {value: 1}, uSize: {value: new THREE.Vector2(18, 28)}},
  transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
  vertexShader: `uniform vec3 uT; uniform float uPinch; uniform float uTime; varying vec2 vUv; varying float vG; varying float vD;
    void main(){ vUv=uv; vec4 wp=modelMatrix*vec4(position,1.0); vec3 n=normalize((modelMatrix*vec4(0.,0.,1.,0.)).xyz);
      vec3 d=wp.xyz-uT; float r=length(d); float g=exp(-(r*r)/110.0); vG=g;
      wp.xyz-=d*0.42*uPinch*g; wp.xyz+=n*(5.5*uPinch*g + 0.35*sin(r*0.6-uTime*3.0)*g*uPinch);
      vD=r; gl_Position=projectionMatrix*viewMatrix*wp; }`,
  fragmentShader: `uniform vec3 uTint; uniform float uBase; uniform float uFade; uniform vec2 uSize; uniform float uPinch; varying vec2 vUv; varying float vG; varying float vD;
    float lm(float v,float sp,float w){ float x=v/sp; float d=abs(fract(x-0.5)-0.5)/max(fwidth(x),1e-4); return 1.0-clamp(d-w,0.0,1.0); }
    void main(){ vec2 p=vUv*uSize; float gl=max(lm(p.x,1.6,0.5),lm(p.y,1.6,0.5));
      vec2 e=min(vUv,1.0-vUv); float edge=1.0-smoothstep(0.0,0.025,min(e.x,e.y));
      float a=(uBase*(0.55+0.45*vG*uPinch)+gl*0.16*(1.0+2.2*vG*uPinch)+edge*0.45)*uFade;
      gl_FragColor=vec4(uTint*a,1.0); }`
});
const planes = [];
[[14, 0.28, 0.9], [21, -0.16, 0.8], [27, 0.22, 1.0]].forEach(([x, ry, s], i) => {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(18, 28, 46, 70), planeMat(TEAL.clone().multiplyScalar(0.9), 0.045)); m.position.set(x, 1.5 - i * 0.3, -1.2 + i * 0.6); m.rotation.y = Math.PI / 2 + ry; m.rotation.x = 0.04 * (i - 1);
  m.renderOrder = 2; scene.add(m); planes.push(m);
});
const field = new THREE.Mesh(new THREE.PlaneGeometry(34, 44, 90, 110), new THREE.ShaderMaterial({
  uniforms: {uT: {value: TARGET}, uPinch: {value: 0}, uTime: {value: 0}, uFlare: {value: 0}}, transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
  vertexShader: `varying vec2 vUv; varying vec3 vW; void main(){ vUv=uv; vec4 wp=modelMatrix*vec4(position,1.0); vW=wp.xyz; gl_Position=projectionMatrix*viewMatrix*wp; }`,
  fragmentShader: `uniform vec3 uT; uniform float uPinch; uniform float uTime; uniform float uFlare; varying vec2 vUv; varying vec3 vW;
    float lm(float v,float sp,float w){ float x=v/sp; float d=abs(fract(x-0.5)-0.5)/max(fwidth(x),1e-4); return 1.0-clamp(d-w,0.0,1.0); }
    void main(){ vec3 d=vW-uT; float r=length(d.yz+vec2(0.0,d.x*0.0)); float rr=length(d); float g=exp(-(rr*rr)/7.0);
      float y=vW.y+ (vW.y-uT.y)*(-0.9*uPinch*g) ; float flow=lm(y+0.35*sin(vW.z*0.35+uTime)*g*uPinch,0.62,0.45);
      float ring=0.0; for(int i=0;i<5;i++){ float ph=fract(uTime*0.45+float(i)/5.0); float rad=ph*6.5; ring+=exp(-pow((rr-rad)/0.1,2.0))*(1.0-ph)*(0.18+0.55*uPinch); }
      float edge=exp(-rr/30.0);
      vec3 teal=vec3(0.12,0.9,0.78)*flow*0.4*edge*(0.35+0.8*uPinch); vec3 red=vec3(1.0,0.18,0.12)*(ring*0.85+ g*0.35*uPinch + uFlare*exp(-rr*1.4)*1.1);
      gl_FragColor=vec4(teal+red,1.0); }`
}));
field.position.copy(TARGET).add(new THREE.Vector3(0.3, 0, 0)); field.rotation.y = -1.05; field.renderOrder = 1; scene.add(field);
const glowTex = (() => { const c = document.createElement('canvas'); c.width = c.height = 128; const x = c.getContext('2d'), g = x.createRadialGradient(64, 64, 0, 64, 64, 64); g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(0.2, 'rgba(255,90,70,0.8)'); g.addColorStop(1, 'rgba(255,40,30,0)'); x.fillStyle = g; x.fillRect(0, 0, 128, 128); return new THREE.CanvasTexture(c); })();
const core = new THREE.Sprite(new THREE.SpriteMaterial({map: glowTex, blending: THREE.AdditiveBlending, depthTest: false, transparent: true})); core.position.copy(TARGET).add(new THREE.Vector3(-0.4, 0, 0.2)); core.renderOrder = 5; scene.add(core);
// dust
const pg = new THREE.BufferGeometry(), pp = new Float32Array(900 * 3); for (let i = 0; i < 900; i++) { pp[3 * i] = lerp(-10, 48, Math.random()); pp[3 * i + 1] = lerp(-14, 18, Math.random()); pp[3 * i + 2] = lerp(-14, 10, Math.random()); }
pg.setAttribute('position', new THREE.BufferAttribute(pp, 3));
const dust = new THREE.Points(pg, new THREE.PointsMaterial({size: 2.2, sizeAttenuation: false, color: 0x4de8d0, transparent: true, opacity: 0.55, blending: THREE.AdditiveBlending, depthWrite: false, depthTest: false})); dust.renderOrder = 4; scene.add(dust);

// ---------- timeline ----------
const tipX = t => { const u = clamp((t - 0.05) / 2.0); return lerp(8.0, TARGET.x - 0.35, 1 - Math.pow(1 - u, 3)); };
const CAM = [[0, 9, 3.0, 50, 10, 2.0, 0, 42], [0.6, 14, 4.0, 46, 17, 2.2, 0, 40], [1.1, 24, 3.5, 34, 28, 2.2, 0, 36], [1.6, 27, 3.0, 26, 31.5, 2.2, 0, 32], [2.4, 24, 4.0, 36, 26, 2.4, 0, 38], [3.2, 20, 5, 46, 22, 2.5, 0, 42]];
function camAt(t) { let i = 0; while (i < CAM.length - 2 && t > CAM[i + 1][0]) i++; const a = CAM[i], b = CAM[i + 1], u = sm((t - a[0]) / (b[0] - a[0])); return a.map((v, k) => lerp(v, b[k], u)); }
window.renderAt = async (t) => {
  const c = camAt(Math.min(t, 3.2)); camera.position.set(c[1], c[2], c[3]); camera.fov = c[7]; camera.updateProjectionMatrix(); camera.lookAt(c[4], c[5], c[6]);
  const lead = tipX(t + LEAD), cur = tipX(t), conv = sm((t - 1.75) / 0.5), sep = 1 - conv;
  const pinch = sm((t - 0.35) / 1.15) * (1 - 0.25 * sm((t - 2.6) / 0.6)), flare = Math.exp(-Math.max(0, t - 1.5) / 0.22) * (t > 1.5 ? 1 : 0) * 0.8 + Math.exp(-Math.max(0, t - 2.0) / 0.3) * (t > 2.0 ? 1 : 0);
  const wave = 0.5 * Math.exp(-Math.pow((t - 0.9) / 0.6, 2)), bob = 0.012 * Math.sin(t * 2.2);
  placeHand(real, new THREE.Vector3(cur, TARGET.y - 0.3, 0), 1.0, t, wave, 0.0, bob);
  placeHand(ghost, new THREE.Vector3(lead, TARGET.y + 3.4 * sep, -3.2 * sep), 0.85 * (1 - 0.75 * conv), t, wave * 1.2, 0.0, bob);
  placeHand(trail1, new THREE.Vector3(tipX(t + LEAD + 0.18), TARGET.y + 3.4 * sep, -3.2 * sep), 0.8 * (1 - conv), t, wave, 0, bob);
  placeHand(trail2, new THREE.Vector3(tipX(t + LEAD + 0.36), TARGET.y + 3.4 * sep, -3.2 * sep), 0.7 * (1 - conv), t, wave, 0, bob);
  planes.forEach((p, i) => { p.material.uniforms.uPinch.value = pinch; p.material.uniforms.uTime.value = t; p.material.uniforms.uFade.value = sm((t - 0.35) / 0.5) * (1 - 0.92 * sm((t - 1.15) / 0.5)); });
  field.material.uniforms.uPinch.value = pinch; field.material.uniforms.uTime.value = t; field.material.uniforms.uFlare.value = flare;
  const ps = 1.0 + 3.5 * flare + 0.8 * pinch; core.scale.setScalar(0.9 + ps * 0.55); core.material.opacity = 0.3 + 0.35 * pinch + 0.25 * flare;
  dust.position.x = -t * 0.8; renderer.domElement.style.opacity = String(0.25 + 0.75 * sm(t / 0.25));
  const tt = document.getElementById('title'); const n = clamp((t - 1.55) / 0.35); tt.innerHTML = n > 0 ? `<div style="opacity:${n}">YOUR BRAIN<br><em>CHEATS.</em></div>` : '';
  renderer.render(scene, camera); return true;
};
window.ready = true;
