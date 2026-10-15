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

// ---------- FULL CUT v3: opening grammar (time-offset ghost, depth stack, orbiting camera) applied to every beat ----------
const LEADT = 0.6, OFFv = V3(0.6, 0.8, -3.2);
const eP = (s, p) => { const u = clamp((s - p.t0) / p.dur); return u * u * (3 - 2 * u); };
const pathAt = (s, p) => { const e = eP(s, p); return V3(lerp(p.from.x, p.to.x, e), lerp(p.from.y, p.to.y, e) + p.arc * Math.sin(Math.PI * e) * (1 - e), 0); };
const slopeOf = (s, p) => { const q = Math.min(s, p.t0 + p.dur * 0.96), a = pathAt(q - 0.04, p), b = pathAt(q + 0.04, p); return Math.atan2(b.y - a.y, b.x - a.x) * 0.7; };
const TGT = V3(33.15, 2.0, 0);
const P0 = {t0: 0.15, dur: 2.1, from: V3(-6, -7, 0), to: TGT, arc: 3.2};
const P1 = {t0: 4.4, dur: 1.8, from: V3(70, -6, 0), to: V3(99.3, -0.8, 0), arc: 2.5};
function drawApproach(E, p, am, sc) {
  const conv = sm((E - (p.t0 + p.dur - 0.15)) / 0.45), bob = 0.01 * Math.sin(E * 2);
  put(hand.real, pathAt(E, p), am, E, {scale: sc, rz: slopeOf(E, p) + bob});
  const s1 = E + LEADT; put(hand.ghost, pathAt(s1, p).add(OFFv.clone().multiplyScalar(1 - eP(s1, p))), 0.95 * sm((E - (p.t0 - 0.05)) / 0.4) * (1 - 0.9 * conv) * am, E, {scale: sc, rz: slopeOf(s1, p) + bob});
  for (let k = 0; k < 4; k++) { const f = (k + 1) / 5, s2 = E + LEADT * f; put(hand.tr[k], pathAt(s2, p).add(OFFv.clone().multiplyScalar(1 - eP(s2, p))), 1.7 * sm((E - (p.t0 + 0.05)) / 0.4) * (1 - conv) * (1 - f * 0.5) * am, E, {scale: sc, rz: slopeOf(s2, p), cut: 0.5}); }
}
// depth layers for stage k: background flow field, faint foreground lines, glass layers behind the hand
const mkFlow = (x, z, off) => { const f = flow.clone(); f.material = flow.material.clone(); f.material.uniforms.uOff.value = off; f.position.set(x, 2, z); scene.add(f); return f; };
const flowF0 = mkFlow(30, 10, 0), flowP = mkFlow(100, -7, 70), flowPF = mkFlow(100, 10, 70);
stages[0].planes.forEach((p, i) => p.position.set(24 + i * 4.5, 1.5, -6 - i * 2));
stages[1].planes.forEach((p, i) => p.position.set(104 + i * 4.5, 0.5, -6 - i * 2));
function layers(E, S, fl, fF, tgt, pull, pinch, flare, fadeP, am) {
  fl.material.uniforms.uT.value.copy(tgt); fF.material.uniforms.uT.value.copy(tgt); fl.material.uniforms.uPull.value = pull; fF.material.uniforms.uPull.value = pull; fl.material.uniforms.uTime.value = E; fF.material.uniforms.uTime.value = E + 3; fl.material.uniforms.uAmp.value = am; fF.material.uniforms.uAmp.value = 0.3 * am;
  S.planes.forEach(p => { p.material.uniforms.uPinch.value = pinch; p.material.uniforms.uTime.value = E; p.material.uniforms.uFade.value = fadeP; });
  S.field.material.uniforms.uPinch.value = pinch; S.field.material.uniforms.uFlare.value = flare; S.field.material.uniforms.uTime.value = E;
}
function drawOpening(Eo, am) {
  const S = stages[0], fl1 = Math.exp(-Math.max(0, Eo - 1.65) / 0.3) * (Eo > 1.65 ? 1 : 0) * 0.5, fl2 = Math.exp(-Math.max(0, Eo - 2.25) / 0.25) * (Eo > 2.25 ? 1 : 0);
  const fade = (0.35 + 0.65 * sm(Eo / 0.3)) * am, pull = sm((Eo - 0.5) / 1.3), pinch = sm((Eo - 1.0) / 1.0) * (1 - 0.25 * sm((Eo - 3.0) / 0.6));
  drawApproach(Eo, P0, fade, 0.78);
  layers(Eo, S, flow, flowF0, V3(33.5, 2.2, 0), pull, pinch, fl1 + fl2, 0.5 * sm((Eo - 0.4) / 0.5) * (1 - sm((Eo - 2.4) / 0.6)) * am, fade);
  cores[0].scale.setScalar(0.9 + (1 + 3.5 * (fl1 + fl2) + 0.8 * pinch) * 0.55); cores[0].material.opacity = (0.15 + 0.5 * pinch + 0.3 * (fl1 + fl2)) * sm((Eo - 0.4) / 0.4) * am;
  updateRipples(V3(33.5, 2.2, 0.5), Eo - 2.25, 0.8 * (Eo > 2.25 ? 1 : 0) * am, 6, 0.5);
}
function openingCam(Eo, drift) { const th = lerp(-0.3, 0.24, sm(Eo / 3.8)) + (drift || 0), push = sm((Eo - 3.0) / 1.0), R = lerp(55, 47, sm(Eo / 3.8)) - 22 * push, cx = lerp(26, 33, push); return [0, cx + R * Math.sin(th), 3 + 1.2 * Math.sin(Eo * 0.6), R * Math.cos(th), cx + 1 + 5 * push, 2, 0, 41 - 6 * push]; }
function palmCam(E) { const th = lerp(-0.28, 0.22, sm((E - 3.9) / 3.0)), push = sm((E - 6.2) / 0.7), R = lerp(52, 40, sm((E - 3.9) / 2.3)) - 14 * push; return [0, 100 + R * Math.sin(th), 2.5, R * Math.cos(th), 100, -1, 0, 40 - 3 * push]; }
const curveRev = new THREE.CatmullRomCurve3(curveBr.getPoints(60).reverse());
const mkTubeC = (curve, r, col, op) => { const m = new THREE.Mesh(new THREE.TubeGeometry(curve, 220, r, 6, false), new THREE.MeshBasicMaterial({color: col, transparent: true, opacity: op, blending: THREE.AdditiveBlending, depthTest: false})); m.renderOrder = 6; m.frustumCulled = false; scene.add(m); return m; };
const tubeRet = mkTubeC(curveRev, 0.1, 0x30f0c8, 0.9), tubeRetGlow = mkTubeC(curveRev, 0.45, 0xf1ead8, 0.14), sRet = stream(curveRev, 0x30f0c8);
function setTube(core, glow, head, vis, col, glowCol) { core.visible = glow.visible = vis > 0.01; for (const m of [core, glow]) m.geometry.setDrawRange(0, Math.floor(sm(head) * 220) * 36); core.material.color.setHex(col); glow.material.color.setHex(glowCol); core.material.opacity = 0.9 * vis; glow.material.opacity = 0.16 * vis; }
const CAM = [[7.4, 198, 1, 62, 200, 0, 0, 42], [8.8, 198, 1, 62, 200, 0, 0, 42], [10.2, 200, 0, 56, 200, -2, 0, 40], [11.4, 206, -4, 52, 208, -8, 0, 40], [12.0, 206, -4, 52, 208, -8, 0, 40],
  [12.05, 100, -0.5, 40, 100, -1.2, 0, 38], [14.0, 100, -0.5, 36, 100, -1.2, 0, 36], [15.2, 101, -0.5, 33, 103, 0.5, 0, 34], [16.5, 100, -0.5, 36, 100, -1.2, 0, 36], [16.55, 198, 1, 60, 200, 0, 0, 42], [20.3, 200, 1, 58, 200, 0, 0, 42]];
function camAt(t) { let i = 0; while (i < CAM.length - 2 && t > CAM[i + 1][0]) i++; const a = CAM[i], b = CAM[i + 1], u = sm((t - a[0]) / (b[0] - a[0])); return a.map((v, k) => lerp(v, b[k], u)); }
function follow(curve, u, dir) { const p = curve.getPoint(clamp(u)); return [0, p.x - 8 * dir, p.y + 2, 48, p.x + 10 * dir, p.y, 0, 40]; }
const LINES = [[2.3, 3.9, 'big', 'YOUR BRAIN<br><em>CHEATS.</em>'], [4.3, 6.0, 'sm', 'TRY TO TICKLE YOURSELF.'], [6.2, 7.2, 'sm', 'EXPECTED TOUCH.<br>WEAKER RESPONSE.'], [8.9, 11.6, 'sm', 'MOVEMENT. PREDICTION. TOUCH.'],
  [13.4, 14.6, 'sm', 'THE TOUCH IS PREDICTED.'], [14.7, 16.4, 'sm', 'SOMEONE ELSE.<br><em>NO PREDICTION.</em>'], [18.3, 20.0, 'sm', 'THAT’S WHY IT <em>TICKLES.</em>'], [20.5, 23.2, 'sm', 'BUT YOU CAN’T MAKE IT A <em>SURPRISE.</em>']];
const wf = document.getElementById('wf');
function waveSVG(t, mode, tin, tout) {
  const a = sm((t - tin) / 0.4) * (1 - sm((t - tout) / 0.4)); if (a <= 0.01) return '';
  const wave = (y0, amp, col, decay) => { let d = ''; for (let x = 0; x <= 420; x += 4) { const u = x / 420, y = y0 - amp * Math.sin(x * 0.22) * Math.exp(-u * decay) * clamp((t - tin) / 0.6) * Math.min(1, u * 14); d += (x ? 'L' : 'M') + x + ',' + y.toFixed(1); } return `<path d="${d}" stroke="${col}" stroke-width="3" fill="none"/>`; };
  const lab = (x, y, s, c) => `<text x="${x}" y="${y}" font-family="Liberation Sans Narrow,sans-serif" font-weight="700" font-size="26" letter-spacing="4" fill="${c}">${s}</text>`;
  let g = `<g transform="translate(60,0)">${lab(0, 24, 'EXPECTED TOUCH', '#3ef0c8')}${wave(86, 18, '#3ef0c8', 2.2)}${lab(0, 130, 'WEAKER RESPONSE', '#e8e4d0')}</g>`;
  if (mode === 'both') g += `<g transform="translate(580,0)">${lab(0, 24, 'UNEXPECTED TOUCH', '#ff3a2c')}${wave(86, 58, '#ff3a2c', 0.7)}${lab(0, 130, 'STRONGER RESPONSE', '#e8e4d0')}</g>`;
  return `<g opacity="${a}">${g}</g>`;
}
const flashEl = document.getElementById('flash');
const C1 = V3(100, -1, 0), C2 = V3(104.5, 2.0, 0.4), BRN = V3(201, 7.6, 0), EC = 15.3;
window.renderAt = async (E) => {
  // ---- camera ----
  let c = E < 4.0 ? openingCam(E) : E < 7.4 ? palmCam(E) : E >= 20.2 ? openingCam(3.0, (E - 20.2) * 0.02) : camAt(E);
  const wins = [[sm((E - 6.9) / 0.3) * (1 - sm((E - 8.8) / 0.5)), curveBr, sm((E - 7.0) / 1.8), 1], [sm((E - 11.6) / 0.3) * (1 - sm((E - 13.3) / 0.4)), curveRev, sm((E - 11.9) / 1.5), -1], [sm((E - 15.9) / 0.3) * (1 - sm((E - 17.9) / 0.4)), curveBr, sm((E - 16.4) / 1.3), 1]];
  for (const [w, cv, u, dir] of wins) if (w > 0) { const f = follow(cv, u, dir); c = c.map((v, k) => lerp(v, f[k], w)); }
  const shk = E > EC && E < EC + 1.5 ? Math.exp(-(E - EC) * 8) * 0.5 : 0, dr = (E >= 7.4 && E < 20.2) ? 1 : 0;
  camera.position.set(c[1] + dr * 2.5 * Math.sin(E * 0.45) + shk * Math.sin(E * 90), c[2] + dr * 0.8 * Math.cos(E * 0.37) + shk * 0.7 * Math.cos(E * 70), c[3]); camera.fov = c[7]; camera.updateProjectionMatrix(); camera.lookAt(c[4], c[5], c[6]);
  // ---- reset ----
  [flow, flowF0, flowP, flowPF, flow2].forEach(f => f.material.uniforms.uAmp.value = 0);
  stages.forEach(s => { s.planes.forEach(p => { p.material.uniforms.uFade.value = 0; p.material.uniforms.uPinch.value = 0; }); s.field.material.uniforms.uPinch.value = 0; s.field.material.uniforms.uFlare.value = 0; s.field.material.uniforms.uTime.value = E; s.field.material.uniforms.uAmp.value = 1; });
  cores.forEach(c0 => c0.material.opacity = 0); cores[1].position.copy(STAGE_T[1]); cores[2].position.copy(STAGE_T[2]);
  [hand.real, hand.ghost, ...hand.tr, palm, macro, brain, other, own].forEach(o => o.visible = false); rings.forEach(o => o.visible = false); updateBurst(V3(0, 0, 0), -1, 0);
  updateStream(sCmd, -1, 0); updateStream(sPrd, -1, 0); updateStream(sBr, -1, 0); updateStream(sRet, -1, 0); tubeCore.visible = tubeGlow.visible = tubeRet.visible = tubeRetGlow.visible = false;
  let wfh = '';
  // ===== OPENING (and loop close) =====
  if (E < 4.05) drawOpening(E, 1 - sm((E - 3.85) / 0.2));
  if (E >= 19.9) drawOpening(3.0, sm((E - 19.9) / 0.5));
  // ===== PALM 1: the ghost finger leads in time and lands on the contact first; macro push; damped ripple =====
  if (E >= 3.9 && E < 8.6) {
    const S = stages[1], pf = 1 - sm((E - 8.0) / 0.5), appear = sm((E - 3.95) / 0.4) * pf, ghostArr = P1.t0 + P1.dur - LEADT, realArr = P1.t0 + P1.dur;
    put(palm, C1, appear, E, {reveal: clamp((E - 4.0) / 0.9)});
    drawApproach(E, P1, appear, 0.78);
    const pull = sm((E - 4.6) / 1.2), pinch = sm((E - ghostArr + 0.4) / 0.8) * (1 - 0.5 * sm((E - 7.4) / 0.6)), fl = Math.exp(-Math.max(0, E - realArr) / 0.3) * (E > realArr ? 1 : 0);
    layers(E, S, flowP, flowPF, V3(100, -1, 0), pull, pinch * 0.6, fl * 0.6 + 0.4 * Math.exp(-Math.max(0, E - ghostArr) / 0.3) * (E > ghostArr ? 1 : 0), 0.8 * sm((E - 4.3) / 0.5) * (1 - sm((E - 6.1) / 0.4)), 0.8 * appear);
    S.field.material.uniforms.uAmp.value = 0.7;
    put(macro, V3(100, -1.1, 3), sm((E - 6.3) / 0.4) * (1 - sm((E - 7.8) / 0.5)) * 0.65 * appear, E, {scale: 0.3});
    updateRipples(V3(100, -1.1, 3.5), E - realArr, 0.8 * appear, 4.5, 0.5);
    cores[1].scale.setScalar(1.2 + 1.0 * sm((E - ghostArr) / 0.8) + 2.0 * Math.exp(-Math.max(0, E - realArr) / 0.3)); cores[1].material.opacity = clamp((E - ghostArr + 0.4) / 0.6) * 0.95 * (1 - sm((E - 7.8) / 0.6)) * pf;
  }
  // ===== BRIDGE 1 =====
  { const hb = clamp((E - 7.0) / 1.8), bv = sm((E - 6.9) / 0.3) * (1 - sm((E - 8.8) / 0.5)); setTube(tubeCore, tubeGlow, hb, bv, 0xf1ead8, 0x30f0c8); updateStream(sBr, hb, bv);
    const p = curveBr.getPoint(sm(hb)); flow2.material.uniforms.uAmp.value = bv; flow2.material.uniforms.uPull.value = 0.9; flow2.material.uniforms.uTime.value = E; flow2.material.uniforms.uT.value.set(p.x, p.y, 0); }
  // ===== BRAIN: command and prediction race; the prediction arrives first =====
  const a1 = sm((E - 7.9) / 0.7) * (1 - sm((E - 12.5) / 0.4)), a2 = sm((E - 17.2) / 0.5) * (1 - sm((E - 20.1) / 0.3)), flareB = sm((E - 17.9) / 0.3) * (1 - sm((E - 19.6) / 0.5));
  if (a1 > 0.002 || a2 > 0.002) {
    put(brain, V3(200, 0.5, 0), a1 + a2, E, {reveal: E < 14 ? clamp((E - 7.9) / 0.9) : 1, red: 0.85 * flareB});
    if (a1 > 0.002) {
      updateStream(sCmd, (E - 8.8) / 2.4, a1); updateStream(sPrd, (E - 9.5) / 0.9, a1);
      const arrive = sm((E - 10.4) / 0.25) * (1 - sm((E - 11.8) / 0.6)), arriveC = sm((E - 11.2) / 0.25) * (1 - sm((E - 12.0) / 0.5));
      cores[2].scale.setScalar(1.2 + 1.8 * arrive + 1.2 * arriveC); cores[2].material.opacity = clamp((E - 8.9) / 0.5) * (0.35 + 0.4 * arrive + 0.2 * arriveC) * a1;
      stages[2].planes.forEach(p => { p.material.uniforms.uPinch.value = 0.4; p.material.uniforms.uTime.value = E; p.material.uniforms.uFade.value = 0.35 * a1; });
      wfh += waveSVG(E, 'exp', 10.6, 12.4);
    }
    if (a2 > 0.002) { cores[2].position.copy(BRN); cores[2].scale.setScalar(4 + 6 * flareB); cores[2].material.opacity = 0.6 * flareB; updateBurst(BRN, E - 17.9, 0.9 * (E > 17.9 ? 1 : 0)); wfh += waveSVG(E, 'both', 18.4, 20.0); }
  }
  // ===== RETURN: a teal prediction line carries us back to the same palm =====
  { const hr = clamp((E - 11.9) / 1.5), rv = sm((E - 11.8) / 0.3) * (1 - sm((E - 13.9) / 0.4)); setTube(tubeRet, tubeRetGlow, hr, rv, 0x30f0c8, 0xf1ead8); updateStream(sRet, hr, rv);
    if (rv > 0.01) { const p = curveRev.getPoint(sm(hr)); flow2.material.uniforms.uAmp.value = Math.max(flow2.material.uniforms.uAmp.value, rv); flow2.material.uniforms.uPull.value = 0.9; flow2.material.uniforms.uTime.value = E; flow2.material.uniforms.uT.value.set(p.x, p.y, 0); } }
  // ===== PALM 2: predicted + dampened, then someone else strikes somewhere unpredicted =====
  if (E >= 12.8 && E < 16.9) {
    const pa = sm((E - 12.9) / 0.5) * (1 - sm((E - 16.5) / 0.4)), S = stages[1], flash = E >= EC ? Math.exp(-(E - EC) / 0.6) : 0, pre = E < EC ? 1 : 0;
    put(palm, C1, pa, E, {reveal: clamp((E - 12.9) / 0.8), red: 0.7 * flash, wave: 1.4 * flash});
    put(hand.real, V3(99.3, -0.8, 1.5), 0.65 * sm((E - 13.4) / 0.4) * (1 - sm((E - 15.4) / 0.3)) * pa, E, {});
    put(hand.ghost, V3(99.3, -0.5, 0.8), 0.8 * sm((E - 13.3) / 0.4) * (1 - sm((E - 15.0) / 0.3)) * pa, E, {cut: 0.4});
    const u = clamp((E - 14.1) / 1.2), e = Math.pow(u, 2.2), off = V3(24, 20, 4).multiplyScalar(1 - e); off.x += -7 * Math.sin(Math.PI * u) * (1 - u);
    put(other, C2.clone().add(off), pa * sm((E - 14.1) / 0.3), E, {scale: 0.9, red: 0.5 * flash});
    if (pre) updateRipples(V3(100, -1.1, 3.5), E - 13.8, 0.35, 4.5, 0.5); else { updateBurst(C2, E - EC, 1); updateRipples(C2.clone().add(V3(0, 0, 0.6)), E - EC, 1, 14, 0.38); }
    cores[1].position.copy(pre ? C1 : C2); cores[1].scale.setScalar(pre ? 1.8 : 2 + 7 * Math.exp(-(E - EC) / 0.25)); cores[1].material.opacity = pre ? 0.4 * sm((E - 13.2) / 0.4) * pa : (0.4 + 0.6 * Math.exp(-(E - EC) / 0.6)) * pa;
    const pn = sm((E - 14.4) / 0.9) * (E >= EC ? 1.5 * Math.exp(-(E - EC) / 1.5) + 0.5 : 0.5);
    layers(E, S, flowP, flowPF, E >= EC ? C2 : C1, 0.7 * sm((E - 13.0) / 0.6), pn, 1.2 * flash, 0.8 * sm((E - 14.2) / 0.5) * (1 - sm((E - 16.2) / 0.5)), 0.7 * pa);
  }
  // ===== RED BRIDGE: the surprise travels to the brain =====
  { const h3 = clamp((E - 16.4) / 1.3), v3 = sm((E - 16.3) / 0.3) * (1 - sm((E - 18.2) / 0.5)); if (v3 > 0.01) { setTube(tubeCore, tubeGlow, h3, v3, 0xff3a2c, 0xff3a2c); updateStream(sBr, h3, v3); const p = curveBr.getPoint(sm(h3)); flow2.material.uniforms.uAmp.value = v3; flow2.material.uniforms.uPull.value = 0.9; flow2.material.uniforms.uT.value.set(p.x, p.y, 0); } }
  // ===== overlays =====
  wf.innerHTML = '<svg width="1080" height="160" viewBox="0 0 1080 160">' + wfh + '</svg>';
  flashEl.style.opacity = String(E >= EC && E < EC + 0.12 ? 0.12 * (1 - (E - EC) / 0.12) : 0);
  dust.position.x = camera.position.x - 2 - E * 0.5;
  const L = LINES.find(l => E >= l[0] && E < l[1]); const tt = document.getElementById('title');
  if (L) { const n = clamp((E - L[0]) / 0.35) * (1 - sm((E - (L[1] - 0.25)) / 0.25)); tt.className = L[2]; tt.innerHTML = `<div style="opacity:${n}">${L[3]}</div>`; } else tt.innerHTML = '';
  renderer.domElement.style.opacity = String(1 - 0.85 * clamp(1 - Math.abs(E - 4.0) / 0.12));
  renderer.render(scene, camera); return true;
};
window.ready = true;
