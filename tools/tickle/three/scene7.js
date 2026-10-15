// Full animatic: 5 stages along x (0 hook, 100 palm, 200 brain, 300 other hand), one continuous camera flight.
// Master style: teal contour-line art (Meta) as layered sprites; bone white = real movement; teal = prediction; red = contact/surprise only.
import * as THREE from 'three';
const QP = new URLSearchParams(location.search); const W = +(QP.get('w') || 1080), H = +(QP.get('h') || 1350), DUR = 23.2, LEAD = 0.5;
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x)), sm = x => { x = clamp(x); return x * x * (3 - 2 * x); }, lerp = (a, b, t) => a + (b - a) * t;
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const renderer = new THREE.WebGLRenderer({antialias: true, preserveDrawingBuffer: true}); renderer.setPixelRatio(1); renderer.setSize(W, H); renderer.setClearColor(0x02050a, 1);
document.body.appendChild(renderer.domElement);
document.body.style.width = W + 'px'; document.body.style.height = H + 'px';
const WAN = QP.get('wan') === '1'; let wanImg = null, wanIdx = -1;
if (WAN) { wanImg = document.createElement('img'); wanImg.style.cssText = `position:absolute;left:0;top:0;width:${W}px;height:${H}px;z-index:1`; document.body.appendChild(wanImg); renderer.domElement.style.zIndex = 0; }
const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(40, W / H, 0.1, 600);
const BONE = new THREE.Color(1.3, 1.22, 1.05), TL = new THREE.Color(0.14, 0.95, 0.8), RD = new THREE.Color(1.0, 0.16, 0.12);
const loadTex = async n => { const t = await new THREE.TextureLoader().loadAsync('./assets/' + n); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; };
const TX = {hand: await loadTex('hand_point_side.png'), palm: await loadTex('palm.png'), other: await loadTex('other_hand.png'), own: await loadTex('own_palm.png'), brain: await loadTex('brain.png'), macro: await loadTex('macro.png')};

// ---------- sprite factory (contour art) ----------
const spriteMat = (tex, tint, op) => new THREE.ShaderMaterial({
  uniforms: {uTex: {value: tex}, uTint: {value: tint.clone()}, uOp: {value: op}, uTime: {value: 0}, uWave: {value: 0}, uReveal: {value: 1}, uRed: {value: 0}, uEdgeL: {value: 0}, uRad: {value: 0}, uCut: {value: 0}},
  transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
  vertexShader: `uniform float uTime; uniform float uWave; varying vec2 vUv;
    void main(){ vUv=uv; vec3 p=position; float f=smoothstep(0.45,1.0,uv.x); p.y+=uWave*0.5*sin(uv.x*16.0-uTime*4.0)*f; gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.0); }`,
  fragmentShader: `uniform sampler2D uTex; uniform vec3 uTint; uniform float uOp; uniform float uReveal; uniform float uRed; uniform float uEdgeL; uniform float uRad; uniform float uCut; varying vec2 vUv;
    void main(){ float a=texture2D(uTex,vUv).a; float front=uReveal*1.3-0.1; a*=1.0-smoothstep(front-0.12,front,vUv.x);
      a*=mix(1.0,smoothstep(0.0,0.16,vUv.x),uEdgeL); a*=uCut>0.0?smoothstep(uCut-0.02,uCut+0.06,vUv.x):1.0; a*=mix(1.0,1.0-smoothstep(0.30,0.5,length((vUv-0.5)*vec2(1.0,1.25))),uRad); vec3 c=mix(uTint,vec3(1.0,0.2,0.14),uRed); gl_FragColor=vec4(c*a*uOp,1.0); }`
});
function mkSprite(tex, px, py, ppu, anchor, layers, edgeL = 0) {
  const w = px / ppu, h = py / ppu, g = new THREE.Group(); g.layers_ = []; g.anchorLocal = V3((anchor[0] / px - 0.5) * w, (0.5 - anchor[1] / py) * h, 0);
  layers.forEach(([z, tint, op]) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h, 50, 30), spriteMat(tex, tint, op)); m.material.uniforms.uEdgeL.value = edgeL; m.position.z = z; m.userData.base = op; m.renderOrder = 3; m.frustumCulled = false; g.add(m); g.layers_.push(m); });
  scene.add(g); return g;
}
function put(sp, anchorWorld, alpha, t, o = {}) {
  const s = o.scale || 1, rz = o.rz || 0, a = sp.anchorLocal.clone().multiplyScalar(s).applyAxisAngle(V3(0, 0, 1), rz);
  sp.scale.setScalar(s); sp.rotation.z = rz; sp.position.copy(anchorWorld).sub(a); sp.visible = alpha > 0.003;
  sp.layers_.forEach(m => { const u = m.material.uniforms; u.uOp.value = m.userData.base * alpha; u.uTime.value = t; u.uWave.value = o.wave || 0; u.uReveal.value = o.reveal ?? 1; u.uRed.value = o.red || 0; u.uCut.value = o.cut || 0; });
}
const hand = {real: mkSprite(TX.hand, 2000, 1000, 50, [1318, 415], [[0, BONE, 1.0], [-0.5, TL, 0.42], [-1.0, TL, 0.26]], 1),
  ghost: mkSprite(TX.hand, 2000, 1000, 50, [1318, 415], [[0, TL, 0.8], [-0.6, TL, 0.36]], 1),
  tr: [0, 1, 2, 3].map(() => mkSprite(TX.hand, 2000, 1000, 50, [1318, 415], [[0, TL, 0.3]], 1))};
const palm = mkSprite(TX.palm, 2000, 1125, 50, [1010, 790], [[0, TL, 0.95], [-0.7, TL, 0.3]]);
const macro = mkSprite(TX.macro, 1760, 1408, 50, [880, 700], [[0, TL, 1.0], [-0.5, TL, 0.3]]); macro.layers_.forEach(m => m.material.uniforms.uRad.value = 1);
const brain = mkSprite(TX.brain, 2000, 1125, 50, [1000, 560], [[0, TL, 0.95], [-0.9, TL, 0.3]]);
const other = mkSprite(TX.other, 2000, 1125, 50, [905, 590], [[0, TL, 1.0], [-0.6, TL, 0.3]]);
const own = mkSprite(TX.own, 2000, 1125, 50, [700, 870], [[0, TL, 0.95], [-0.6, TL, 0.3]]);

// ---------- planes of predicted space, flow field, targets ----------
const planeMat = () => new THREE.ShaderMaterial({
  uniforms: {uT: {value: V3(0, 0, 0)}, uPinch: {value: 0}, uTime: {value: 0}, uFade: {value: 0}},
  transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
  vertexShader: `uniform vec3 uT; uniform float uPinch; uniform float uTime; varying vec2 vUv; varying float vG;
    void main(){ vUv=uv; vec4 wp=modelMatrix*vec4(position,1.0); vec3 n=normalize((modelMatrix*vec4(0.,0.,1.,0.)).xyz); vec3 d=wp.xyz-uT; float r=length(d); float g=exp(-(r*r)/110.0); vG=g;
      wp.xyz-=d*0.42*uPinch*g; wp.xyz+=n*(5.5*uPinch*g+0.35*sin(r*0.6-uTime*3.0)*g*uPinch); gl_Position=projectionMatrix*viewMatrix*wp; }`,
  fragmentShader: `uniform float uFade; uniform float uPinch; varying vec2 vUv; varying float vG;
    float lm(float v,float sp,float w){ float x=v/sp; float d=abs(fract(x-0.5)-0.5)/max(fwidth(x),1e-4); return 1.0-clamp(d-w,0.0,1.0); }
    void main(){ vec2 p=vUv*vec2(18.0,28.0); float gl=max(lm(p.x,1.6,0.5),lm(p.y,1.6,0.5)); vec2 e=min(vUv,1.0-vUv); float edge=1.0-smoothstep(0.0,0.025,min(e.x,e.y));
      float a=(0.04*(0.55+0.45*vG*uPinch)+gl*0.16*(1.0+2.2*vG*uPinch)+edge*0.45)*uFade; gl_FragColor=vec4(vec3(0.11,0.81,0.7)*a,1.0); }`
});
const stages = [0, 1, 2, 3].map(k => ({x: 100 * k, planes: [], field: null}));
const STAGE_T = [V3(33.5, 2.2, 0), V3(100, -1, 0), V3(218, -12, 0), V3(294, -6.2, 0)];
stages.forEach((s, k) => {
  [[14, 0.28], [21, -0.16], [27, 0.22]].forEach(([dx, ry], i) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(18, 28, 46, 70), planeMat()); m.position.set(s.x + dx + (k ? 4 : 0), 1.5 - i * 0.3, -1.2 + i * 0.6); m.rotation.y = Math.PI / 2 + ry; m.renderOrder = 2; m.material.uniforms.uT.value = STAGE_T[k]; scene.add(m); s.planes.push(m); });
  const f = new THREE.Mesh(new THREE.PlaneGeometry(34, 44, 90, 110), new THREE.ShaderMaterial({
    uniforms: {uT: {value: STAGE_T[k]}, uPinch: {value: 0}, uTime: {value: 0}, uFlare: {value: 0}, uAmp: {value: 1}, uEdge: {value: k === 0 ? 30 : 8}}, transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
    vertexShader: `varying vec3 vW; void main(){ vec4 wp=modelMatrix*vec4(position,1.0); vW=wp.xyz; gl_Position=projectionMatrix*viewMatrix*wp; }`,
    fragmentShader: `uniform vec3 uT; uniform float uPinch; uniform float uTime; uniform float uFlare; uniform float uAmp; uniform float uEdge; varying vec3 vW;
      float lm(float v,float sp,float w){ float x=v/sp; float d=abs(fract(x-0.5)-0.5)/max(fwidth(x),1e-4); return 1.0-clamp(d-w,0.0,1.0); }
      void main(){ vec3 d=vW-uT; float rr=length(d); float g=exp(-(rr*rr)/7.0);
        float y=vW.y+(vW.y-uT.y)*(-0.9*uPinch*g); float flow=lm(y+0.35*sin(vW.z*0.35+uTime)*g*uPinch,0.62,0.45);
        float ring=0.0; for(int i=0;i<5;i++){ float ph=fract(uTime*0.45+float(i)/5.0); float rad=ph*6.5; ring+=exp(-pow((rr-rad)/0.1,2.0))*(1.0-ph)*(0.18+0.55*uPinch); }
        float edge=exp(-rr/uEdge)*(1.0-smoothstep(7.0,15.0,rr)); vec3 teal=vec3(0.12,0.9,0.78)*flow*0.4*edge*(0.35+0.8*uPinch); vec3 red=vec3(1.0,0.18,0.12)*(ring*0.85+g*0.35*uPinch+uFlare*exp(-rr*1.4)*1.1);
        gl_FragColor=vec4((teal+red)*uAmp,1.0); }`})); 
  f.position.copy(STAGE_T[k]).add(V3(0.3, 0, k === 0 ? 0 : -4)); f.rotation.y = k === 0 ? -1.05 : 0; f.renderOrder = 1; scene.add(f); s.field = f;
});
const flow = new THREE.Mesh(new THREE.PlaneGeometry(160, 56, 2, 2), new THREE.ShaderMaterial({
  uniforms: {uT: {value: V3(33.5, 2.2, 0)}, uPull: {value: 0}, uTime: {value: 0}, uAmp: {value: 0}, uOff: {value: 0}}, transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending,
  vertexShader: `varying vec3 vW; void main(){ vec4 wp=modelMatrix*vec4(position,1.0); vW=wp.xyz; gl_Position=projectionMatrix*viewMatrix*wp; }`,
  fragmentShader: `uniform vec3 uT; uniform float uPull; uniform float uTime; uniform float uAmp; uniform float uOff; varying vec3 vW;
    float lm(float v,float sp,float w){ float x=v/sp; float d=abs(fract(x-0.5)-0.5)/max(fwidth(x),1e-4); return 1.0-clamp(d-w,0.0,1.0); }
    void main(){ float dx=(vW.x-uT.x)/26.0; float g=exp(-dx*dx); float dy=vW.y-uT.y; float yw=vW.y-dy*0.62*uPull*g; yw+=0.35*sin(vW.x*0.12+uTime*0.5+vW.y*0.08)*(1.0-0.7*uPull*g);
      float l=lm(yw,0.8,0.42); float near=exp(-length(vec2(dx*26.0,dy))/22.0); float xo=vW.x-uOff; float edge=smoothstep(-30.0,-6.0,xo)*(1.0-smoothstep(52.0,70.0,xo));
      vec3 c=mix(vec3(0.1,0.8,0.7),vec3(1.0,0.2,0.14),near*uPull*0.55); gl_FragColor=vec4(c*l*(0.16+0.5*near*uPull)*edge*uAmp,1.0); }`}));
flow.position.set(30, 2, -7); flow.renderOrder = 0; scene.add(flow);
const flow2 = flow.clone(); flow2.material = flow.material.clone(); flow2.material.uniforms.uOff.value = 128; flow2.position.set(150, 2, -7); scene.add(flow2);
const glowTex = (() => { const c = document.createElement('canvas'); c.width = c.height = 128; const x = c.getContext('2d'), g = x.createRadialGradient(64, 64, 0, 64, 64, 64); g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(0.2, 'rgba(255,90,70,0.8)'); g.addColorStop(1, 'rgba(255,40,30,0)'); x.fillStyle = g; x.fillRect(0, 0, 128, 128); return new THREE.CanvasTexture(c); })();
const glow = k => { const s = new THREE.Sprite(new THREE.SpriteMaterial({map: glowTex, blending: THREE.AdditiveBlending, depthTest: false, transparent: true})); s.position.copy(STAGE_T[k]); s.renderOrder = 6; scene.add(s); return s; };
const cores = [0, 1, 2, 3].map(glow);
// dust
const pg = new THREE.BufferGeometry(), pp = new Float32Array(900 * 3); for (let i = 0; i < 900; i++) { pp[3 * i] = lerp(-30, 30, Math.random()); pp[3 * i + 1] = lerp(-16, 18, Math.random()); pp[3 * i + 2] = lerp(-14, 10, Math.random()); }
pg.setAttribute('position', new THREE.BufferAttribute(pp, 3));
const dust = new THREE.Points(pg, new THREE.PointsMaterial({size: 2.2, sizeAttenuation: false, color: 0x4de8d0, transparent: true, opacity: 0.5, blending: THREE.AdditiveBlending, depthWrite: false, depthTest: false})); dust.renderOrder = 4; scene.add(dust);

// ---------- contact burst (stage 4), ripples, signal streams ----------
const NSP = 110, spark = {ang: [], len: [], spd: []}; for (let i = 0; i < NSP; i++) { spark.ang.push(Math.random() * Math.PI * 2); spark.len.push(0.6 + Math.random() * 2.4); spark.spd.push(7 + Math.random() * 16); }
const sparkGeo = new THREE.BufferGeometry(); sparkGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(NSP * 6), 3)); sparkGeo.setAttribute('color', new THREE.BufferAttribute(new Float32Array(NSP * 6), 3));
const sparks = new THREE.LineSegments(sparkGeo, new THREE.LineBasicMaterial({vertexColors: true, transparent: true, blending: THREE.AdditiveBlending, depthTest: false})); sparks.renderOrder = 7; sparks.frustumCulled = false; scene.add(sparks);
const dropGeo = new THREE.BufferGeometry(); dropGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(NSP * 3), 3));
const drops = new THREE.Points(dropGeo, new THREE.PointsMaterial({size: 4, sizeAttenuation: false, color: 0xff3a2c, transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending, depthTest: false})); drops.renderOrder = 7; drops.frustumCulled = false; scene.add(drops);
function updateBurst(center, u, strength) { // u seconds since contact
  const P = sparkGeo.attributes.position.array, C = sparkGeo.attributes.color.array, D = dropGeo.attributes.position.array;
  for (let i = 0; i < NSP; i++) {
    const r0 = Math.max(0, u) * spark.spd[i] * (1 - 0.5 * clamp(u / 1.4)), r1 = r0 + spark.len[i] * clamp(u * 6) * (1 - clamp(u / 1.2)), fade = (u < 0 ? 0 : 1 - clamp(u / 1.3)) * strength, ca = Math.cos(spark.ang[i]), sa = Math.sin(spark.ang[i]);
    P.set([center.x + ca * r0, center.y + sa * r0 * 0.75, center.z + 1, center.x + ca * r1, center.y + sa * r1 * 0.75, center.z + 1], i * 6); C.set([fade, fade * 0.16, fade * 0.1, fade, fade * 0.16, fade * 0.1], i * 6);
    D.set([center.x + ca * (r1 + 0.3), center.y + sa * (r1 + 0.3) * 0.75, center.z + 1.2], i * 3);
  }
  sparkGeo.attributes.position.needsUpdate = sparkGeo.attributes.color.needsUpdate = dropGeo.attributes.position.needsUpdate = true; drops.material.opacity = 0.9 * (u < 0 ? 0 : 1 - clamp(u / 1.5)) * strength;
}
const rings = []; for (let i = 0; i < 8; i++) { const m = new THREE.Mesh(new THREE.RingGeometry(0.97, 1.0, 96), new THREE.MeshBasicMaterial({color: 0xff2e22, transparent: true, depthTest: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide})); m.renderOrder = 6; scene.add(m); rings.push(m); }
function updateRipples(center, u, amp, maxR, flat) { rings.forEach((m, i) => { const a = u - i * 0.12, r = Math.max(0.01, a * 7), life = a < 0 ? 0 : Math.exp(-a / (0.9 * amp + 0.15)); m.position.set(center.x, center.y, center.z + 0.5); m.scale.set(Math.min(r, maxR), Math.min(r, maxR) * flat, 1); m.material.opacity = life * amp * (1 - i / 10); m.visible = m.material.opacity > 0.01; }); }
// signal streams (stage 3)
const curveCmd = new THREE.CatmullRomCurve3([V3(201, 7.6, 1), V3(196, 3, 1), V3(193, -4, 1), V3(198, -11, 1), V3(206, -13.5, 1), V3(214, -12.5, 1), V3(218, -12, 1)]);
const curvePrd = new THREE.CatmullRomCurve3([V3(207, -4.6, 1), V3(210, -8, 1), V3(214, -10.8, 1), V3(218, -12, 1)]);
function stream(curve, color) {
  const N = 150, g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(N * 3), 3)); g.setAttribute('color', new THREE.BufferAttribute(new Float32Array(N * 3), 3));
  const p = new THREE.Points(g, new THREE.PointsMaterial({size: 4.5, sizeAttenuation: false, vertexColors: true, transparent: true, blending: THREE.AdditiveBlending, depthTest: false})); p.renderOrder = 7; p.frustumCulled = false; scene.add(p);
  const ln = new THREE.Line(new THREE.BufferGeometry().setFromPoints(curve.getPoints(80)), new THREE.LineBasicMaterial({color, transparent: true, opacity: 0.35, blending: THREE.AdditiveBlending, depthTest: false})); ln.renderOrder = 5; scene.add(ln);
  return {g, p, ln, N, curve, color};
}
const curveBr = new THREE.CatmullRomCurve3([V3(100, -1, 2), V3(110, 7, 2), V3(126, 13, 1), V3(146, 7, 1), V3(168, 11, 1), V3(188, 13, 1), V3(201, 7.6, 1)]);
const mkTube = (r, col, op) => { const m = new THREE.Mesh(new THREE.TubeGeometry(curveBr, 220, r, 6, false), new THREE.MeshBasicMaterial({color: col, transparent: true, opacity: op, blending: THREE.AdditiveBlending, depthTest: false})); m.renderOrder = 6; m.frustumCulled = false; scene.add(m); return m; };
const tubeCore = mkTube(0.1, 0xf1ead8, 0.9), tubeGlow = mkTube(0.45, 0x30f0c8, 0.16);
const sCmd = stream(curveCmd, 0xf1ead8), sPrd = stream(curvePrd, 0x30f0c8), sBr = stream(curveBr, 0xf1ead8);
function updateStream(s, head, vis) {
  const P = s.g.attributes.position.array, C = s.g.attributes.color.array, col = new THREE.Color(s.color);
  for (let i = 0; i < s.N; i++) { const u = clamp(head - i * 0.006), p = s.curve.getPoint(u), f = (1 - i / s.N) * vis * (head > 0 ? 1 : 0) * (u > 0 ? 1 : 0); P.set([p.x + (Math.random() - 0.5) * 0.25, p.y + (Math.random() - 0.5) * 0.25, p.z], i * 3); C.set([col.r * f, col.g * f, col.b * f], i * 3); }
  s.g.attributes.position.needsUpdate = s.g.attributes.color.needsUpdate = true; s.ln.geometry.setDrawRange(0, Math.max(0, Math.floor(clamp(head) * 81))); s.ln.material.opacity = 0.3 * vis;
}

// ---------- OPENING v3: time-offset ghost, time ribbon, layered depth, orbiting camera ----------
const TGT = V3(33.15, 2.0, 0), LEADT = 0.6, SC0 = 0.78;
const tipPath = s => { const u = clamp((s - 0.15) / 2.1), e = u * u * (3 - 2 * u); return V3(lerp(-6, TGT.x, e), lerp(-7, TGT.y, e) + 3.2 * Math.sin(Math.PI * e) * (1 - e), 0); };
const slope = s => { const q = Math.min(s, 2.2), a = tipPath(q - 0.04), b = tipPath(q + 0.04); return Math.atan2(b.y - a.y, b.x - a.x) * 0.7; };   // hold the last real heading once the path ends (no snap to 0)
const eP = s => { const u = clamp((s - 0.15) / 2.1); return u * u * (3 - 2 * u); }, OFFv = V3(0.6, 0.8, -3.2);   // ghost depth/height offset is part of its approach: it lands exactly on the contact point and never moves after
const NR = 30, NS = 41, ribbons = [];
for (let i = 0; i < NR; i++) { const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(NS * 3), 3)); g.setAttribute('color', new THREE.BufferAttribute(new Float32Array(NS * 3), 3)); const l = new THREE.Line(g, new THREE.LineBasicMaterial({vertexColors: true, transparent: true, blending: THREE.AdditiveBlending, depthTest: false})); l.renderOrder = 5; l.frustumCulled = false; scene.add(l); ribbons.push(l); }
const flowF = flow.clone(); flowF.material = flow.material.clone(); flowF.position.set(30, 2, 10); scene.add(flowF);
stages[0].planes.forEach((p, i) => { p.position.set(24 + i * 4.5, 1.5, -6 - i * 2); });
const LINES = [[2.3, 4.2, 'big', 'YOUR BRAIN<br><em>CHEATS.</em>']];
const flashEl = document.getElementById('flash');
window.renderAt = async (E) => {
  const th = lerp(-0.3, 0.24, sm(E / 3.8)), R = lerp(55, 47, sm(E / 3.8)), Tc = V3(26, 2, 0);
  camera.position.set(Tc.x + R * Math.sin(th), 3 + 1.2 * Math.sin(E * 0.6), Tc.z + R * Math.cos(th)); camera.fov = 41; camera.updateProjectionMatrix(); camera.lookAt(Tc.x + 1, 2, 0);
  [hand.real, hand.ghost, ...hand.tr, palm, macro, brain, other, own].forEach(o => o.visible = false); rings.forEach(o => o.visible = false); updateBurst(V3(0, 0, 0), -1, 0);
  cores.forEach(c0 => c0.material.opacity = 0); stages.forEach(s => { s.planes.forEach(p => p.material.uniforms.uFade.value = 0); s.field.material.uniforms.uPinch.value = 0; s.field.material.uniforms.uFlare.value = 0; s.field.material.uniforms.uAmp.value = 1; });
  const conv = sm((E - 2.1) / 0.45), sep = 1 - conv, fade = 0.35 + 0.65 * sm(E / 0.3), bob = 0.01 * Math.sin(E * 2);
  put(hand.real, tipPath(E), fade, E, {scale: SC0, rz: slope(E) + bob});
  const gP = tipPath(E + LEADT).add(OFFv.clone().multiplyScalar(1 - eP(E + LEADT)));
  put(hand.ghost, gP, 0.95 * sm((E - 0.1) / 0.4) * (1 - 0.9 * conv), E, {scale: SC0, rz: slope(E + LEADT) + bob});
  for (let k = 0; k < 4; k++) { const f = (k + 1) / 5, s2 = E + LEADT * f, p = tipPath(s2).add(OFFv.clone().multiplyScalar(1 - eP(s2))); put(hand.tr[k], p, 1.7 * sm((E - 0.2) / 0.4) * (1 - conv) * (1 - f * 0.5), E, {scale: SC0, rz: slope(E + LEADT * f), cut: 0.5}); }
  // time ribbon: thin lines stretch from the real fingertip to the ghost fingertip, collapse when they meet
  const rv = (QP.get('rib') === '0' ? 0 : 1) * sm((E - 0.2) / 0.4) * (1 - 0.9 * sm((E - 2.2) / 0.4));
  ribbons.forEach((l, i) => { const P = l.geometry.attributes.position.array, C = l.geometry.attributes.color.array, m = i / (NR - 1) - 0.5;
    for (let j = 0; j < NS; j++) { const f = j / (NS - 1), p = tipPath(E + LEADT * f), w = Math.pow(Math.sin(Math.PI * f), 0.8), sf = 1 - eP(E + LEADT * f);
      P.set([p.x + 0.6 * sf, p.y + 0.8 * sf + m * 2.8 * w * (0.4 + 0.6 * sf), -3.2 * sf + m * 1.6 * w * sf], j * 3);
      const a = rv * w * (0.18 + 0.5 * (1 - Math.abs(m) * 2)); C.set([0.12 * a, 0.95 * a, 0.8 * a], j * 3); }
    l.geometry.attributes.position.needsUpdate = l.geometry.attributes.color.needsUpdate = true; });
  // depth layers: background field, foreground fine lines, faint glass layers behind the hand
  const S = stages[0], pull = sm((E - 0.5) / 1.3), pinch = sm((E - 1.0) / 1.0) * (1 - 0.25 * sm((E - 3.0) / 0.6)), fl2 = Math.exp(-Math.max(0, E - 2.25) / 0.25) * (E > 2.25 ? 1 : 0), fl1 = Math.exp(-Math.max(0, E - 1.65) / 0.3) * (E > 1.65 ? 1 : 0) * 0.5;
  flow.material.uniforms.uPull.value = pull; flow.material.uniforms.uTime.value = E; flow.material.uniforms.uAmp.value = fade; flowF.material.uniforms.uPull.value = pull; flowF.material.uniforms.uTime.value = E + 3; flowF.material.uniforms.uAmp.value = 0.3 * fade; flow.material.uniforms.uOff.value = 0; flowF.material.uniforms.uOff.value = 0;
  S.planes.forEach(p => { p.material.uniforms.uPinch.value = pinch; p.material.uniforms.uTime.value = E; p.material.uniforms.uFade.value = 0.5 * sm((E - 0.4) / 0.5) * (1 - sm((E - 2.4) / 0.6)); });
  S.field.material.uniforms.uPinch.value = pinch; S.field.material.uniforms.uFlare.value = fl1 + fl2; S.field.material.uniforms.uTime.value = E;
  cores[0].scale.setScalar(0.9 + (1 + 3.5 * (fl1 + fl2) + 0.8 * pinch) * 0.55); cores[0].material.opacity = (0.15 + 0.5 * pinch + 0.3 * (fl1 + fl2)) * sm((E - 0.4) / 0.4);
  updateRipples(V3(33.5, 2.2, 0.5), E - 2.25, 0.8 * (E > 2.25 ? 1 : 0), 6, 0.5);
  dust.position.x = camera.position.x - 2 - E * 0.5;
  const L = LINES.find(l => E >= l[0] && E < l[1]); const tt = document.getElementById('title');
  if (L) { const n = clamp((E - L[0]) / 0.35); tt.className = L[2]; tt.innerHTML = `<div style="opacity:${n}">${L[3]}</div>`; } else tt.innerHTML = '';
  document.getElementById('wf').innerHTML = ''; flashEl.style.opacity = '0';
  renderer.render(scene, camera); return true;
};
window.ready = true;
