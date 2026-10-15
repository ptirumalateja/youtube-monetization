// Full animatic: 5 stages along x (0 hook, 100 palm, 200 brain, 300 other hand), one continuous camera flight.
// Master style: teal contour-line art (Meta) as layered sprites; bone white = real movement; teal = prediction; red = contact/surprise only.
import * as THREE from 'three';
const QP = new URLSearchParams(location.search); const W = +(QP.get('w') || 1080), H = +(QP.get('h') || 1350), DUR = 23.7, LEAD = 0.5;
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

// ---------- timeline ----------
const T1 = 3.2, F12 = [3.2, 3.9], T2 = [3.9, 8.2], F23 = [8.2, 8.9], T3 = [8.9, 13.0], F34 = [13.0, 13.7], T4 = [13.7, 17.0], FB = [17.0, 17.5], T3b = [17.5, 18.6], F51 = [18.6, 19.2];
const KX = [[0, -4], [0.5, 6], [0.62, 6.4], [1.1, 18], [1.22, 18.4], [1.65, 28], [1.8, 28.6], [2.35, 33.15]];
const tipX1 = t => { if (t <= KX[0][0]) return KX[0][1]; for (let i = 1; i < KX.length; i++) if (t <= KX[i][0]) return lerp(KX[i - 1][1], KX[i][1], sm((t - KX[i - 1][0]) / (KX[i][0] - KX[i - 1][0]))); return KX[KX.length - 1][1]; };
const CAM = [[0, 25, 3, 52, 26, 2.2, 0, 42], [0.9, 25.4, 3, 51, 26, 2.2, 0, 41], [1.6, 25.8, 3, 50, 26.3, 2.2, 0, 40], [2.3, 26, 3, 49, 26.5, 2.2, 0, 39], [2.8, 26, 3.2, 49, 26.6, 2.3, 0, 39], [3.2, 26, 3.5, 50, 27, 2.4, 0, 40],
  [3.9, 96, 3, 56, 100, -1, 0, 42], [5.2, 97, 2.5, 48, 100, -1, 0, 40], [6.0, 98, 1, 40, 100, -1.5, 0, 38], [6.5, 100, -0.5, 30, 100, -1.2, 0, 32], [7.4, 100, -0.5, 32, 100, -1.2, 0, 34], [8.2, 100, 1, 44, 100, -1, 0, 40],
  [8.25, 198, 1, 62, 200, 0, 0, 42], [8.9, 198, 1, 62, 200, 0, 0, 42], [10.6, 200, 0, 56, 200, -2, 0, 40], [12.2, 206, -4, 52, 208, -8, 0, 40], [13.0, 208, -4, 52, 210, -8, 0, 42],
  [13.7, 298, 2, 66, 300, -2, 0, 42], [14.8, 298, 0, 58, 299, -3, 0, 40], [15.3, 298, -3, 38, 297, -5, 0, 34], [16.2, 298, -3, 34, 297, -5, 0, 34], [17.0, 300, 0, 60, 300, -2, 0, 40],
  [17.5, 198, 1, 58, 200, 0, 0, 40], [18.6, 200, 1, 62, 200, 0, 0, 42], [19.2, 22, 4, 46, 24, 2.4, 0, 42], [21.8, 20, 4, 44, 22, 2.4, 0, 40]];
function camAt(t) { let i = 0; while (i < CAM.length - 2 && t > CAM[i + 1][0]) i++; const a = CAM[i], b = CAM[i + 1], u = sm((t - a[0]) / (b[0] - a[0])); return a.map((v, k) => lerp(v, b[k], u)); }
const LINES = [[1.8, 3.3, 'big', 'YOUR BRAIN<br><em>CHEATS.</em>'], [4.1, 6.1, 'sm', 'TRY TO TICKLE YOURSELF.'], [6.5, 8.1, 'sm', 'EXPECTED TOUCH.<br>WEAKER RESPONSE.'], [9.1, 11.2, 'sm', 'MOVEMENT. PREDICTION. TOUCH.'],
  [13.9, 15.2, 'sm', 'SOMEONE ELSE.'], [15.4, 17.0, 'sm', 'LESS PREDICTABLE.<br><em>MORE SURPRISING.</em>'], [17.6, 18.6, 'sm', 'THAT’S WHY IT <em>TICKLES.</em>'], [19.5, 21.8, 'sm', 'BUT YOU CAN’T MAKE IT A <em>SURPRISE.</em>']];
const wf = document.getElementById('wf');
function waveSVG(t, strengthUn, tin, tout) {
  const a = sm((t - tin) / 0.4) * (1 - sm((t - tout) / 0.4)); if (a <= 0.01) return '';
  const wave = (y0, amp, col, decay) => { let d = ''; for (let x = 0; x <= 420; x += 4) { const u = x / 420, y = y0 - amp * Math.sin(x * 0.22) * Math.exp(-u * decay) * clamp((t - tin) / 0.6) * Math.min(1, u * 14); d += (x ? 'L' : 'M') + x + ',' + y.toFixed(1); } return `<path d="${d}" stroke="${col}" stroke-width="3" fill="none"/>`; };
  const lab = (x, y, s, c) => `<text x="${x}" y="${y}" font-family="Liberation Sans Narrow,sans-serif" font-weight="700" font-size="26" letter-spacing="4" fill="${c}">${s}</text>`;
  return `<g opacity="${a}"><g transform="translate(60,0)">${lab(0, 24, 'EXPECTED TOUCH', '#3ef0c8')}${wave(86, 18, '#3ef0c8', 2.2)}${lab(0, 130, 'WEAKER RESPONSE', '#e8e4d0')}</g>` +
    `<g transform="translate(580,0)">${lab(0, 24, 'UNEXPECTED TOUCH', '#ff3a2c')}${wave(86, 18 + 40 * strengthUn, '#ff3a2c', 0.7)}${lab(0, 130, 'STRONGER RESPONSE', '#e8e4d0')}</g></g>`;
}
const flashEl = document.getElementById('flash');
window.renderAt = async (tReal) => {
  const BR0 = 8.2, BR = 1.9, inBr2 = tReal >= 9.0 && tReal < BR0 + BR + 0.4; const t = tReal < BR0 ? tReal : Math.max(BR0, tReal - BR);
  let c = camAt(Math.min(t, DUR)); { const w = sm((tReal - 7.8) / 0.6) * (1 - sm((tReal - 10.4) / 0.7)); if (w > 0) { const p = curveBr.getPoint(sm((tReal - 8.0) / 2.2)); const f = [0, p.x - 8, p.y + 2, 48, p.x + 10, p.y, 0, 40]; c = c.map((v, k) => lerp(v, f[k], w)); } }
  const shk = Math.exp(-Math.max(0, t - 15.3) * 8) * (t > 15.3 ? 1 : 0) * 0.5;
  camera.position.set(c[1] + shk * Math.sin(t * 90), c[2] + shk * 0.7 * Math.cos(t * 70), c[3]); camera.fov = c[7]; camera.updateProjectionMatrix(); camera.lookAt(c[4], c[5], c[6]);
  flow.material.uniforms.uAmp.value = 0; flow2.material.uniforms.uAmp.value = 0;
  { const hd = clamp((tReal - 8.0) / 2.2), vis = sm((tReal - 7.9) / 0.4) * (1 - sm((tReal - 10.4) / 0.6)), p = curveBr.getPoint(sm((tReal - 8.0) / 2.2));
    for (const m of [tubeCore, tubeGlow]) { m.visible = vis > 0.01; m.geometry.setDrawRange(0, Math.floor(sm(hd) * 220) * 36); }
    tubeCore.material.opacity = 0.9 * vis; tubeGlow.material.opacity = 0.16 * vis;
    flow2.material.uniforms.uAmp.value = vis; flow2.material.uniforms.uPull.value = 0.9; flow2.material.uniforms.uTime.value = tReal; flow2.material.uniforms.uT.value.set(p.x, p.y, 0); }
  stages.forEach(s => { s.planes.forEach(p => { p.material.uniforms.uFade.value = 0; p.material.uniforms.uPinch.value = 0; }); s.field.material.uniforms.uPinch.value = 0; s.field.material.uniforms.uFlare.value = 0; s.field.material.uniforms.uTime.value = t; s.field.material.uniforms.uAmp.value = 1; });
  cores.forEach(c0 => c0.material.opacity = 0);
  const hide = o => (o.visible = false); [hand.real, hand.ghost, ...hand.tr, palm, macro, brain, other, own].forEach(hide); rings.forEach(hide); sparkGeo.attributes.position.array.fill(0); updateBurst(V3(0, 0, 0), -1, 0);
  updateStream(sCmd, -1, 0); updateStream(sPrd, -1, 0); updateStream(sBr, clamp((tReal - 8.0) / 2.2), 1 - sm((tReal - 10.4) / 0.6));
  // ===== stage 1 (hook, and loop return): static camera, ghost already at the target, stepping stones, one smooth approach =====
  const hookT = t < T1 + 0.2 ? t : (t >= F51[0] ? Math.max(0.05, 0.5 + (t - F51[1]) * 0.9) : -1);
  if (hookT >= 0) {
    const S = stages[0], u = hookT, e = sm((u - 0.2) / 2.1), realX = lerp(4, 33.15, e), yAt = x => lerp(0.6, 2.0, (x - 4) / 29.15), conv = sm((u - 2.15) / 0.45), fadeAll = t < 0.3 ? 0.35 + 0.65 * sm(t / 0.25) : 1, bob = 0.008 * Math.sin(u * 2.0), SC0 = 0.78;
    put(hand.real, V3(realX, yAt(realX), 0), fadeAll, u, {rz: bob, scale: SC0});
    put(hand.ghost, V3(33.15, 2.0, 0), 1.0 * sm((u - 0.3) / 0.5) * (1 - conv) * fadeAll, u, {rz: bob, scale: SC0, cut: 0.4});
    [15.5, 22, 28].forEach((sx, i) => { const pass = sm((realX - sx + 4) / 3.5); put(hand.tr[i], V3(sx, yAt(sx), 0), 2.3 * sm((u - (0.4 + 0.2 * i)) / 0.25) * (1 - pass), u, {rz: bob, scale: SC0, cut: 0.52}); });
    flow.material.uniforms.uPull.value = sm((u - 0.5) / 1.3); flow.material.uniforms.uTime.value = u; flow.material.uniforms.uAmp.value = fadeAll * (1 - sm((u - 2.8) / 0.6));
    const pinch = sm((u - 0.7) / 1.0) * (1 - 0.25 * sm((u - 2.8) / 0.6)), flare = Math.exp(-Math.max(0, u - 2.3) / 0.25) * (u > 2.3 ? 1 : 0);
    S.field.material.uniforms.uPinch.value = pinch; S.field.material.uniforms.uFlare.value = flare; S.field.material.uniforms.uTime.value = u;
    const ps = 1 + 3.5 * flare + 0.8 * pinch; cores[0].scale.setScalar(0.9 + ps * 0.55); cores[0].material.opacity = (0.15 + 0.5 * pinch + 0.3 * flare) * sm((u - 0.5) / 0.4);
  }
  // ===== stage 2 (palm, predicted path, damped contact) =====
  if (t >= F12[0] + 0.3 && t < F23[1]) {
    const S = stages[1], u = t - T2[0], contact = 6.4, appear = sm((t - 3.75) / 0.5) * (1 - sm((t - 8.4) / 0.5));
    put(palm, V3(100, -1, 0), appear * (1 - 0.0), t, {reveal: clamp((t - 3.85) / 0.9)});
    const tipP = lerp(76, 99.3, 1 - Math.pow(1 - clamp((t - 4.4) / 2.0), 2.2)), fin = t > 4.3 ? appear : 0;
    put(hand.real, V3(tipP, -0.8, 1.5), fin * (1 - 0.7 * sm((t - 6.9) / 0.5)), t, {rz: 0.02 * Math.sin(t * 2)});
    const tipG = lerp(76, 99.3, 1 - Math.pow(1 - clamp((t + 0.5 - 4.4) / 2.0), 2.2)); put(hand.ghost, V3(tipG, -0.5, 0.8), (t > 4.3 ? appear : 0) * 0.8 * (1 - sm((t - 6.6) / 0.4)), t, {});
    for (let k = 0; k < 4; k++) put(hand.tr[k], V3(Math.min(99.3, tipP + 4.2 * (k + 1)), -0.8 + 0.5 * (k + 1) * 0.3, -0.4 * (k + 1)), fin * 0.9 * (1 - k * 0.2) * (1 - sm((t - contact) / 0.4)), t, {});
    const tp = sm((t - 5.0) / 1.2) * (1 - 0.5 * sm((t - 7.4) / 0.6)); S.planes.forEach(p => { p.material.uniforms.uPinch.value = tp * 0.6; p.material.uniforms.uTime.value = t; p.material.uniforms.uFade.value = 0.8 * sm((t - 4.4) / 0.6) * (1 - sm((t - 6.0) / 0.4)); });
    S.field.material.uniforms.uPinch.value = tp * 0.5; S.field.material.uniforms.uAmp.value = 0.7;
    const mAlpha = sm((t - 6.1) / 0.4) * (1 - sm((t - 7.8) / 0.5)); put(macro, V3(100, -1.1, 3), mAlpha * 0.65, t, {scale: 0.3});
    updateRipples(V3(100, -1.1, 3.5), t - contact, 0.8, 4.5, 0.5); cores[1].scale.setScalar(1.2 + 1.0 * sm((t - 5.4) / 0.8) + 2.0 * Math.exp(-Math.max(0, t - contact) / 0.3)); cores[1].material.opacity = clamp((t - 4.9) / 0.6) * 0.95 * (1 - sm((t - 7.8) / 0.6));
  }
  // ===== stage 3 (brain, two signals, waveform) =====
  const brainOn = (t >= F23[0] + 0.3 && t < F34[1]) || (t >= FB[0] && t < F51[1]) || inBr2;
  if (brainOn) {
    const S = stages[2], flareB = t >= FB[0] ? sm((t - 17.55) / 0.3) * (1 - sm((t - 18.5) / 0.4)) : 0;
    const a = t < F34[1] ? sm((tReal - 9.2) / 0.7) * (1 - sm((t - 13.1) / 0.5)) : sm((t - 17.3) / 0.3) * (1 - sm((t - 18.7) / 0.4));
    put(brain, V3(200, 0.5, 0), a, t, {reveal: t < F34[1] ? clamp((tReal - 9.2) / 0.9) : 1, red: 0.85 * flareB});
    const sc = t < F34[1];
    const hc = sc ? (t - 9.0) / 3.0 : 0, hp = sc ? (t - 9.9) / 1.1 : 0;   // command slow (arrives ~12.0), prediction fast (arrives first ~11.0)
    updateStream(sCmd, hc, a); updateStream(sPrd, hp, a);
    const arrive = sm((t - 11.0) / 0.25) * (1 - sm((t - 12.4) / 0.6)), arriveC = sm((t - 12.0) / 0.25) * (1 - sm((t - 12.8) / 0.5));
    cores[2].scale.setScalar(1.2 + 1.8 * arrive + 1.2 * arriveC); cores[2].material.opacity = sc ? clamp((t - 9.4) / 0.5) * (0.35 + 0.4 * arrive + 0.2 * arriveC) * a : 0.6 * flareB;
    if (!sc) { cores[2].position.set(201, 7.6, 0); cores[2].scale.setScalar(4 + 6 * flareB); updateBurst(V3(201, 7.6, 0), t - 17.55, 0.9); } else cores[2].position.copy(STAGE_T[2]);
    S.planes.forEach(p => { p.material.uniforms.uPinch.value = 0.4; p.material.uniforms.uTime.value = t; p.material.uniforms.uFade.value = 0.35 * a; });
  }
  // ===== stage 4 (someone else, unexpected touch) =====
  if (t >= F34[0] + 0.3 && t < FB[1]) {
    const S = stages[3], a = sm((t - 13.6) / 0.5) * (1 - sm((t - 17.1) / 0.4)), contact = 15.2, C = V3(294, -6.2, 0);
    put(own, V3(294, -6.2, 0), a, t, {reveal: clamp((t - 13.7) / 0.8)});
    const u = clamp((t - 13.9) / 1.3), e = Math.pow(u, 2.2), off = V3(18, 12, 3).multiplyScalar(1 - e); off.y += 2.5 * Math.sin(Math.PI * u) * (1 - u);
    put(other, C.clone().add(off), a * sm((t - 13.9) / 0.4), t, {red: 0.25 * Math.exp(-Math.max(0, t - contact) / 0.5) * (t > contact ? 1 : 0)});
    const un = t - contact, boom = un > 0 ? 1 : 0;
    updateBurst(V3(294, -6.2, 0), un, boom); updateRipples(V3(294, -6.2, 0.6), un, 1.0 * boom, 14, 0.38);
    cores[3].scale.setScalar(2 + 7 * Math.exp(-Math.max(0, un) / 0.25) * boom); cores[3].material.opacity = clamp((t - 14.8) / 0.4) * (0.4 + 0.6 * Math.exp(-Math.max(0, un) / 0.6)) * a;
    const pn = sm((t - 14.2) / 1.0) * (0.5 + 1.0 * boom * Math.exp(-Math.max(0, un) / 1.5)); S.planes.forEach(p => { p.material.uniforms.uPinch.value = pn; p.material.uniforms.uTime.value = t; p.material.uniforms.uFade.value = 0.8 * sm((t - 14.0) / 0.5) * (1 - sm((t - 16.2) / 0.5)); });
    S.field.material.uniforms.uPinch.value = pn; S.field.material.uniforms.uFlare.value = 1.2 * Math.exp(-Math.max(0, un) / 0.3) * boom; S.field.material.uniforms.uAmp.value = 1.0;
  }
  // overlays: waveform + flash + typography
  const unS = t >= 17.4 ? 1.0 : 0.0;
  wf.innerHTML = '<svg width="1080" height="160" viewBox="0 0 1080 160">' + waveSVG(t, 1.0, 11.8, 13.0) + waveSVG(t, 1.2, 17.7, 18.6) + '</svg>';
  const fl = (t >= 15.2 && t < 15.32) ? 0.12 * (1 - (t - 15.2) / 0.12) : 0; flashEl.style.opacity = String(fl);
  dust.position.x = camera.position.x - 2 - tReal * 0.5;
  const L = LINES.find(l => t >= l[0] && t < l[1]); const tt = document.getElementById('title');
  if (L) { const n = clamp((t - L[0]) / 0.35) * (1 - sm((t - (L[1] - 0.25)) / 0.25)); tt.className = L[2]; tt.innerHTML = `<div style="opacity:${n}">${L[3]}</div>`; } else tt.innerHTML = '';
  renderer.domElement.style.opacity = String(WAN && tReal < 3.4 ? 0 : (t < 0.3 ? 0.25 + 0.75 * sm(t / 0.25) : 1));
  if (WAN) { const wa = tReal < 3.5 ? 1 : 1 - sm((tReal - 3.5) / 0.5); wanImg.style.opacity = String(wa); if (wa > 0.001) { const idx = Math.min(124, Math.floor(tReal * 30) + 1); if (idx !== wanIdx) { wanImg.src = './assets/wan/w' + String(idx).padStart(5, '0') + '.jpg'; try { await wanImg.decode(); } catch (e) {} wanIdx = idx; } } }
  renderer.render(scene, camera); return true;
};
window.ready = true;
