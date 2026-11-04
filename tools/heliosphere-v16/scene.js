// Heliosphere v16, opening act (0-7 s). One continuous camera: Earth close-up -> rip back to the whole heliosphere
// (Sun in front, planets on their true stretched waves) -> zoom out until the Sun's bubble is a speck orbiting a huge galaxy.
// window.renderAt(t) draws reel second t; window.ready flips true once textures are in.
import * as THREE from "three";

const W = 1080, H = 1920; let EARTH_ROT = 2.4; window.setEarthRot = (v) => { EARTH_ROT = v; };
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const seg = (t, a, b) => clamp((t - a) / (b - a));
const sm = (x) => { x = clamp(x); return x * x * (3 - 2 * x); };
const eio = (x) => { x = clamp(x); return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const lerp = (a, b, k) => a + (b - a) * k;
const v3 = (x, y, z) => new THREE.Vector3(x, y, z);
function rng(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

const NOISE = `
float h1(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float n2(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h1(i),h1(i+vec2(1,0)),f.x),mix(h1(i+vec2(0,1)),h1(i+vec2(1,1)),f.x),f.y);}
float fbm(vec2 p){float s=0.,a=.5;for(int i=0;i<6;i++){s+=a*n2(p);p=mat2(1.6,1.2,-1.2,1.6)*p;a*=.5;}return s;}
float h3(vec3 p){return fract(sin(dot(p,vec3(127.1,311.7,74.7)))*43758.5453);}
float n3(vec3 p){vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
 return mix(mix(mix(h3(i),h3(i+vec3(1,0,0)),f.x),mix(h3(i+vec3(0,1,0)),h3(i+vec3(1,1,0)),f.x),f.y),
            mix(mix(h3(i+vec3(0,0,1)),h3(i+vec3(1,0,1)),f.x),mix(h3(i+vec3(0,1,1)),h3(i+vec3(1,1,1)),f.x),f.y),f.z);}
float fbm3(vec3 p){float s=0.,a=.5;for(int i=0;i<5;i++){s+=a*n3(p);p=p*2.03+vec3(1.7,9.2,3.1);a*=.5;}return s;}
`;

// ---------- motion model (display units) ----------
const V = 12;                                   // Sun's speed, units per second (planets' waves stretch along +Z)
const sunAt = (t) => v3(0, 0, V * t);
const NE = v3(0.1, 0.49, 0.866).normalize();     // ecliptic normal: ~60 deg to the galactic plane (Y), ~30 deg to the motion (Z)
const EU = new THREE.Vector3().crossVectors(NE, v3(1, 0, 0)).normalize(), EW = new THREE.Vector3().crossVectors(NE, EU).normalize();
const PL = [ // name, a (AU), display radius of the body, texture, phase
  ["Mercury", 0.387, 0.30, "mercury.jpg", 4.4], ["Venus", 0.723, 0.46, "venus.jpg", 0.2], ["Earth", 1.0, 0.52, null, 1.75],
  ["Mars", 1.524, 0.38, "mars.jpg", 6.2], ["Jupiter", 5.203, 1.55, "jupiter.jpg", 0.6], ["Saturn", 9.555, 1.3, "saturn.jpg", 0.9],
  ["Uranus", 19.22, 0.85, "uranus.jpg", 5.5], ["Neptune", 30.11, 0.82, "neptune.jpg", 5.3]];
const orbitR = (a) => 6 * Math.sqrt(a), period = (a) => 2.2 * Math.pow(a, 0.75); // compressed distances, exaggerated speeds
function planetAt(i, t, o = new THREE.Vector3()) { const [, a, , , ph] = PL[i], th = ph + 6.2832 * t / period(a), r = orbitR(a);
  return o.copy(sunAt(t)).addScaledVector(EU, r * Math.cos(th)).addScaledVector(EW, r * Math.sin(th)); }

// ---------- galaxy placement ----------
const GR = 20000, GS = GR / 70;                  // Sun at 70 shader units from the centre (about 0.53 of the disc)
const GC = v3(GR, 0, 0);

function glowTex(stops) { const c = document.createElement("canvas"); c.width = c.height = 256; const g = c.getContext("2d"), r = g.createRadialGradient(128, 128, 0, 128, 128, 128);
  stops.forEach(([k, col]) => r.addColorStop(k, col)); g.fillStyle = r; g.fillRect(0, 0, 256, 256); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; }
function raysTex() { const c = document.createElement("canvas"); c.width = c.height = 512; const g = c.getContext("2d"), r = rng(31); g.translate(256, 256);
  for (let i = 0; i < 90; i++) { const a = r() * 6.2832, L = 120 + r() * 136, w = 0.004 + r() * 0.012; const gr = g.createLinearGradient(0, 0, Math.cos(a) * L, Math.sin(a) * L);
    gr.addColorStop(0, "rgba(255,230,180,.55)"); gr.addColorStop(1, "rgba(255,180,90,0)"); g.fillStyle = gr; g.beginPath(); g.moveTo(0, 0); g.arc(0, 0, L, a - w, a + w); g.closePath(); g.fill(); }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; }

const canvas = document.getElementById("gl");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, logarithmicDepthBuffer: true, preserveDrawingBuffer: true });
renderer.setSize(W, H, false); renderer.setPixelRatio(1); renderer.outputColorSpace = THREE.SRGBColorSpace; renderer.toneMapping = THREE.NoToneMapping;
const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(40, W / H, 0.01, 4e6);
const manager = new THREE.LoadingManager(); let loaded = false; manager.onLoad = () => { loaded = true; };
const TL = new THREE.TextureLoader(manager), tex = (f, srgb = true) => { const t = TL.load("assets/" + f); if (srgb) t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; };
const U = { t: { value: 0 }, gal: { value: 0 }, galT: { value: 0 } };

const skyU = { uOut: { value: 0 } };
// ---------- sky: soft grey-blue full-bleed, nebula wash, Milky Way band (fades once we leave the disc), sparse soft stars ----------
const sky = new THREE.Mesh(new THREE.SphereGeometry(1, 64, 32), new THREE.ShaderMaterial({ side: THREE.BackSide, depthWrite: false, depthTest: false,
  uniforms: skyU,
  vertexShader: `varying vec3 vD; void main(){ vD=normalize(position); vec4 p=projectionMatrix*modelViewMatrix*vec4(position,1.); gl_Position=p.xyww; }`,
  fragmentShader: NOISE + `uniform float uOut; varying vec3 vD;
void main(){ vec3 d=normalize(vD);
 vec3 lo=vec3(.235,.255,.31), hi=vec3(.33,.355,.42); vec3 c=mix(lo,hi,.5+.5*d.y);
 float neb=fbm3(d*2.2+vec3(3.,1.,7.)); float neb2=fbm3(d*5.+vec3(9.,2.,4.));
 c+=vec3(.07,.10,.14)*smoothstep(.45,.8,neb)+vec3(.09,.05,.10)*smoothstep(.55,.85,neb2)*.8;
 float b=exp(-pow(d.y/.17,2.)); float lane=smoothstep(.45,.75,fbm3(d*7.+vec3(2.,5.,1.)))*exp(-pow(d.y/.05,2.));
 float band=b*(.55+.9*fbm3(d*4.+vec3(5.,5.,5.)));
 vec3 bc=mix(vec3(.55,.62,.80),vec3(1.,.82,.58),pow(max(0.,dot(d,vec3(1,0,0))),3.));
 c+= (1.-uOut)*(bc*band*.42 - vec3(.16,.14,.12)*lane);
 vec3 g=d*420.; vec3 cell=floor(g); float s=h3(cell); vec3 f=fract(g)-.5; float st=step(.9935,s)*exp(-dot(f,f)*26.)*(.5+.5*h3(cell+3.));
 c+=vec3(.9,.95,1.)*st*.7;
 gl_FragColor=vec4(c,1.); }` }));
sky.frustumCulled = false; sky.renderOrder = -10; scene.add(sky);

// ---------- light ----------
const sunLight = new THREE.PointLight(0xfff1dc, 3.2, 0, 0); scene.add(sunLight); scene.add(new THREE.AmbientLight(0x8fa4c8, 0.07));

// ---------- the Sun: boiling granulation, sunspots, limb darkening, corona, rays ----------
const SUNR = 2.0;
const sunMat = new THREE.ShaderMaterial({ uniforms: { uT: U.t },
  vertexShader: `varying vec3 vN, vP, vV; void main(){ vP=position; vN=normalize(normalMatrix*normal); vec4 mv=modelViewMatrix*vec4(position,1.); vV=normalize(-mv.xyz); gl_Position=projectionMatrix*mv; }`,
  fragmentShader: NOISE + `uniform float uT; varying vec3 vN, vP, vV;
void main(){ vec3 p=normalize(vP);
 float g=fbm3(p*9.+vec3(0.,uT*.35,0.)); float g2=fbm3(p*26.-vec3(uT*.6,0.,0.));
 float cells=smoothstep(.35,.75,g*.65+g2*.45);
 float spots=smoothstep(.72,.8,fbm3(p*3.1+vec3(7.,1.,3.)))*smoothstep(.62,.25,abs(p.y));
 float limb=pow(max(dot(vN,vV),0.),.42);
 vec3 c=mix(vec3(.95,.36,.05),vec3(1.,.86,.48),cells); c=mix(c,vec3(.35,.08,.02),spots*.85);
 c*=.55+.75*limb; c+=vec3(1.,.55,.18)*pow(1.-limb,3.)*.6;
 gl_FragColor=vec4(c*1.15,1.); }` });
const sunG = new THREE.Group(); scene.add(sunG);
const sunBody = new THREE.Mesh(new THREE.SphereGeometry(SUNR, 96, 64), sunMat); sunG.add(sunBody);
const spr = (map, s, op) => { const m = new THREE.Sprite(new THREE.SpriteMaterial({ map, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, opacity: op })); m.scale.setScalar(s); return m; };
const corona1 = spr(glowTex([[0, "rgba(255,240,200,1)"], [0.12, "rgba(255,200,110,.85)"], [0.35, "rgba(255,150,60,.25)"], [1, "rgba(255,120,40,0)"]]), SUNR * 7, 0.9); sunG.add(corona1);
const corona2 = spr(glowTex([[0, "rgba(255,210,150,.5)"], [0.4, "rgba(255,160,80,.12)"], [1, "rgba(255,120,40,0)"]]), SUNR * 26, 0.7); sunG.add(corona2);
const rays = spr(raysTex(), SUNR * 16, 0.55); sunG.add(rays);

// ---------- planets ----------
const SOL = new THREE.Group(); scene.add(SOL);
const bodies = [];
const earthMat = new THREE.ShaderMaterial({ uniforms: { day: { value: tex("earth_day.jpg") }, night: { value: tex("earth_night.jpg") }, water: { value: tex("earth_water.jpg", false) }, uSun: { value: v3(0, 0, 0) } },
  vertexShader: `varying vec2 vUv; varying vec3 vWN, vWP; void main(){ vUv=uv; vWN=normalize(mat3(modelMatrix)*normal); vec4 w=modelMatrix*vec4(position,1.); vWP=w.xyz; gl_Position=projectionMatrix*viewMatrix*w; }`,
  fragmentShader: `uniform sampler2D day, night, water; uniform vec3 uSun; varying vec2 vUv; varying vec3 vWN, vWP;
void main(){ vec3 N=normalize(vWN), L=normalize(uSun-vWP), V=normalize(cameraPosition-vWP); float d=dot(N,L);
 vec3 dc=texture2D(day,vUv).rgb, nc=texture2D(night,vUv).rgb; float wm=texture2D(water,vUv).r;
 float lit=smoothstep(-.08,.25,d);
 vec3 c=dc*(.06+1.15*max(d,0.)) ;
 vec3 R=reflect(-L,N); c+=vec3(1.,.92,.8)*pow(max(dot(R,V),0.),38.)*wm*.75*lit;
 float city=smoothstep(.18,.6,dot(nc,vec3(.62,.33,.05))); c+=vec3(1.,.74,.38)*city*1.8*(1.-lit);
 c+=vec3(1.,.48,.2)*exp(-pow(d/.05,2.))*.07;
 gl_FragColor=vec4(c,1.);
 #include <colorspace_fragment>
 }` });
PL.forEach(([name, a, R, file], i) => {
  const g = new THREE.Group(); SOL.add(g);
  const mat = name === "Earth" ? earthMat : new THREE.MeshStandardMaterial({ map: tex(file), roughness: 1, metalness: 0 });
  const m = new THREE.Mesh(new THREE.SphereGeometry(R, 96, 64), mat); g.add(m);
  const b = { name, a, R, g, m, tilt: new THREE.Group() };
  if (name === "Earth") {
    const cl = new THREE.Mesh(new THREE.SphereGeometry(R * 1.012, 96, 64), new THREE.MeshStandardMaterial({ color: 0xffffff, alphaMap: tex("earth_clouds.jpg", false), transparent: true, depthWrite: false, roughness: 1 })); g.add(cl); b.clouds = cl;
    const atm = new THREE.Mesh(new THREE.SphereGeometry(R * 1.07, 64, 48), new THREE.ShaderMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.BackSide, uniforms: { uSun: earthMat.uniforms.uSun },
      vertexShader: `varying vec3 vWN, vWP; void main(){ vWN=normalize(mat3(modelMatrix)*normal); vec4 w=modelMatrix*vec4(position,1.); vWP=w.xyz; gl_Position=projectionMatrix*viewMatrix*w; }`,
      fragmentShader: `uniform vec3 uSun; varying vec3 vWN, vWP; void main(){ vec3 N=normalize(vWN), V=normalize(cameraPosition-vWP), L=normalize(uSun-vWP);
        float rim=pow(1.-abs(dot(N,V)),2.2); float l=.15+1.1*max(dot(N,L),0.); gl_FragColor=vec4(vec3(.35,.62,1.)*rim*l*1.4,rim); }` })); g.add(atm);
    const moon = new THREE.Mesh(new THREE.SphereGeometry(R * 0.27, 64, 48), new THREE.MeshStandardMaterial({ map: tex("moon.jpg"), roughness: 1 })); SOL.add(moon); b.moon = moon;
  }
  if (name === "Saturn") {
    const rin = R * 1.24, rout = R * 2.3, rg = new THREE.RingGeometry(rin, rout, 256, 1);
    const rm = new THREE.ShaderMaterial({ transparent: true, side: THREE.DoubleSide, depthWrite: false, uniforms: { rt: { value: tex("saturn_rings.png") }, rin: { value: rin }, rout: { value: rout } },
      vertexShader: `varying vec3 vP; void main(){ vP=position; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
      fragmentShader: `uniform sampler2D rt; uniform float rin, rout; varying vec3 vP; void main(){ float u=(length(vP.xy)-rin)/(rout-rin); vec4 c=texture2D(rt,vec2(u,.5)); gl_FragColor=vec4(c.rgb*1.05,c.a*.95);
 #include <colorspace_fragment>
 }` });
    const ring = new THREE.Mesh(rg, rm); ring.rotation.x = Math.PI / 2; m.add(ring);
  }
  m.rotation.z = name === "Uranus" ? 1.7 : name === "Saturn" ? 0.47 : name === "Earth" ? 0.41 : 0.1;
  bodies.push(b);
});

// asteroid belt: small lit rocks between Mars and Jupiter
const belt = (() => { const N = 1400, r = rng(77), pos = new Float32Array(N * 3), dat = []; for (let i = 0; i < N; i++) dat.push([orbitR(2.2 + r() * 1.1), r() * 6.2832, (r() - 0.5) * 0.6, 0.6 + r() * 1.4]);
  const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  const p = new THREE.Points(g, new THREE.PointsMaterial({ color: 0xcdb8a0, size: 2.2, sizeAttenuation: false, transparent: true, opacity: 0.7, depthWrite: false })); p.frustumCulled = false; SOL.add(p); return { p, pos, dat }; })();

// trails: dense soft glowing beads along each planet's true path (and a wake behind the Sun)
const TRN = 420;
const trailMat = new THREE.ShaderMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, vertexColors: true,
  vertexShader: `attribute float aA; attribute float aS; varying vec3 vC; varying float vA; void main(){ vC=color; vA=aA; vec4 mv=modelViewMatrix*vec4(position,1.); gl_PointSize=clamp(aS*2600./-mv.z,1.6,8.); gl_Position=projectionMatrix*mv; }`,
  fragmentShader: `varying vec3 vC; varying float vA; void main(){ vec2 d=gl_PointCoord-.5; float k=dot(d,d)*4.; if(k>1.) discard; gl_FragColor=vec4(vC,vA*exp(-k*3.)); }` });
const TCOL = [[0.75, 0.72, 0.68], [1, 0.85, 0.6], [0.45, 0.75, 1], [1, 0.5, 0.35], [1, 0.8, 0.55], [1, 0.9, 0.65], [0.6, 0.95, 1], [0.45, 0.6, 1], [1, 0.8, 0.45]];
const trails = TCOL.map((c, i) => { const g = new THREE.BufferGeometry(), pos = new Float32Array(TRN * 3), col = new Float32Array(TRN * 3), aA = new Float32Array(TRN), aS = new Float32Array(TRN);
  for (let k = 0; k < TRN; k++) { col.set(c, k * 3); } g.setAttribute("position", new THREE.BufferAttribute(pos, 3)); g.setAttribute("color", new THREE.BufferAttribute(col, 3));
  g.setAttribute("aA", new THREE.BufferAttribute(aA, 1)); g.setAttribute("aS", new THREE.BufferAttribute(aS, 1)); const p = new THREE.Points(g, trailMat); p.frustumCulled = false; SOL.add(p); return { g, pos, aA, aS, sun: i === 8 }; });

// solar wind: particles streaming out from the Sun and slowing at the termination shock
const wind = (() => { const N = 1800, r = rng(5), pos = new Float32Array(N * 3), dat = []; for (let i = 0; i < N; i++) { const z = r() * 2 - 1, a = r() * 6.2832, s = Math.sqrt(1 - z * z); dat.push([v3(s * Math.cos(a), s * Math.sin(a), z), r()]); }
  const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(pos, 3)); const aA = new Float32Array(N); g.setAttribute("aA", new THREE.BufferAttribute(aA, 1));
  const m = new THREE.ShaderMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    vertexShader: `attribute float aA; varying float vA; void main(){ vA=aA; vec4 mv=modelViewMatrix*vec4(position,1.); gl_PointSize=clamp(260./-mv.z,1.2,4.); gl_Position=projectionMatrix*mv; }`,
    fragmentShader: `varying float vA; void main(){ vec2 d=gl_PointCoord-.5; float k=dot(d,d)*4.; if(k>1.) discard; gl_FragColor=vec4(1.,.9,.72,vA*exp(-k*2.5)); }` });
  const p = new THREE.Points(g, m); p.frustumCulled = false; SOL.add(p); return { pos, aA, dat, g }; })();

// ---------- the bubbles: heliosphere (nose along the motion, long tail) and Earth's magnetosphere ----------
function shellGeo(sx, nose, tail) { const g = new THREE.IcosahedronGeometry(1, 7), p = g.attributes.position;
  for (let i = 0; i < p.count; i++) { const x = p.getX(i), y = p.getY(i), z = p.getZ(i), c = z, s = sx * (1 - (1 - nose) * Math.max(0, c) + (tail - 1) * Math.pow(Math.max(0, -c), 2.0));
    p.setXYZ(i, x * sx * (1 + 0.04 * Math.sin(5 * Math.atan2(y, x))), y * sx, z * s); } g.computeVertexNormals(); return g; }
function shellMat(pal, strength, flow) {
  return new THREE.ShaderMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
    uniforms: { uT: U.t, uS: { value: strength }, uF: { value: flow }, cN: { value: new THREE.Color(pal[0]) }, cF: { value: new THREE.Color(pal[1]) }, cT: { value: new THREE.Color(pal[2]) }, uK: { value: 1 } },
    vertexShader: `varying vec3 vP, vWN, vWP; void main(){ vP=position; vWN=normalize(mat3(modelMatrix)*normal); vec4 w=modelMatrix*vec4(position,1.); vWP=w.xyz; gl_Position=projectionMatrix*viewMatrix*w; }`,
    fragmentShader: NOISE + `uniform float uT,uS,uF,uK; uniform vec3 cN,cF,cT; varying vec3 vP, vWN, vWP;
void main(){ vec3 N=normalize(vWN), V=normalize(cameraPosition-vWP); float f=1.-abs(dot(N,V)); float fr=pow(f,2.4);
 vec3 q=normalize(vP); float c=q.z; float ang=atan(q.y,q.x);
 float along=vP.z/length(vP+1e-4)*0.+vP.z;
 float fl=fbm(vec2(ang*4.,along*uF*.06+uT*.45)); float fil=pow(1.-abs(2.*fbm(vec2(ang*9.+1.7,along*uF*.14+uT*.8))-1.),4.);
 vec3 col=mix(cF,cN,smoothstep(.1,.9,c)); col=mix(col,cT,smoothstep(-.2,-.9,c));
 col+=vec3(.25,.1,.3)*pow(f,5.);           // iridescent edge
 float a=(fr*(.55+.9*fl)+fil*.35*fr+.035*(.5+fl))*uS*uK;
 gl_FragColor=vec4(col*a*1.3,a); }` }); }
const HELI = new THREE.Group(); SOL.add(HELI);
const helioMat = shellMat([0xff7a4a, 0x4f8dff, 0x9a6bff], 0.95, 1.0), tsMat = shellMat([0xffd2a0, 0x7fc8ff, 0x8f9dff], 0.42, 1.6);
HELI.add(new THREE.Mesh(shellGeo(66, 0.86, 2.4), helioMat)); HELI.add(new THREE.Mesh(shellGeo(45, 0.8, 1.8), tsMat));
const MAG = new THREE.Group(); SOL.add(MAG);
const magMat = shellMat([0xffa060, 0x4fd0ff, 0x6f8bff], 0.9, 18.0), magMat2 = shellMat([0xff8a50, 0x80e0ff, 0x8090ff], 0.45, 26.0);
MAG.add(new THREE.Mesh(shellGeo(1.45, 0.72, 4.2), magMat)); MAG.add(new THREE.Mesh(shellGeo(1.9, 0.78, 3.0), magMat2));
// dipole field lines, squeezed on the dayside, stretched into the tail
{ const lm = new THREE.LineBasicMaterial({ color: 0x9fe6ff, transparent: true, opacity: 0.32, blending: THREE.AdditiveBlending, depthWrite: false });
  for (const L of [0.85, 1.1, 1.4, 1.8]) for (let k = 0; k < 8; k++) { const ph = k / 8 * 6.2832, pts = [];
    for (let j = 0; j <= 80; j++) { const lat = -1.45 + 2.9 * j / 80, r = L * Math.cos(lat) ** 2 + 0.52; const x = r * Math.cos(lat) * Math.cos(ph), y = r * Math.sin(lat), z = r * Math.cos(lat) * Math.sin(ph);
      const sq = z > 0 ? 0.72 : 1 + 1.3 * Math.pow(-z / (L + 0.5), 1.4); pts.push(v3(x, y, z * sq)); }
    MAG.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), lm)); } }
MAG.userData.lines = MAG.children.filter((c) => c.isLine);

// ---------- the galaxy: volumetric shader disc (26 stacked layers), dust lanes, differential rotation, soft stars ----------
const GAL = new THREE.Group(); GAL.position.copy(GC); GAL.rotation.x = -Math.PI / 2; GAL.scale.setScalar(GS); scene.add(GAL);
{ const L = 26, TH = 4;
  for (let i = 0; i < L; i++) { const zf = i / (L - 1) - 0.5;
    const m = new THREE.ShaderMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, uniforms: { uT: U.galT, uI: U.gal, uZ: { value: zf }, uL: { value: L } },
      vertexShader: `varying vec2 vP; void main(){ vP=position.xy; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
      fragmentShader: NOISE + `uniform float uT,uI,uZ,uL; varying vec2 vP;
void main(){ float r=length(vP); if(r>150.) discard; float a=atan(vP.y,vP.x);
 float aa=a-uT*.10/(.35+r/45.); float sp=aa+2.35*log(max(r,3.)/10.);
 float arm=pow(.5+.5*cos(2.*sp+.35*(fbm(vP*.04)-.5)),5.); float arm2=pow(.5+.5*cos(2.*sp+1.9),6.)*.45;
 vec2 q=vec2(cos(aa),sin(aa))*r; float cl=fbm(q*.055+uZ*1.7), cl2=fbm(q*.16+7.3);
 float dust=smoothstep(.45,.75,fbm(q*.09+3.1))*pow(.5+.5*cos(2.*sp+.55),4.);
 float bul=.6*exp(-r*r/(2.*11.*11.)), bar=.7*exp(-pow(q.x*cos(.5)+q.y*sin(.5),2.)/(2.*18.*18.)-pow(-q.x*sin(.5)+q.y*cos(.5),2.)/(2.*6.*6.));
 float disc=exp(-r/48.)*smoothstep(150.,90.,r); float sig=.16+.34*max(bul,bar*.7); float lay=exp(-uZ*uZ/(2.*sig*sig));
 float it=(bul*.55+bar*.35+disc*(arm*2.6+arm2*1.2+.12)*pow(.25+1.2*cl,1.6))*(1.-.85*dust)*lay;
 vec3 core=vec3(1.,.66,.32), armc=vec3(.38,.58,1.), pink=vec3(1.,.32,.55);
 vec3 col=mix(armc,core,clamp(max(bul,bar)*1.6+exp(-r/16.),0.,1.)); col=mix(col,pink,smoothstep(.72,.9,cl2)*arm*disc*1.4);
 gl_FragColor=vec4(col*uI, min(.8,it*2.2/uL)*uI); }` });
    const pl = new THREE.Mesh(new THREE.PlaneGeometry(310, 310), m); pl.position.z = zf * TH * 2; GAL.add(pl); }
  const dm = new THREE.ShaderMaterial({ transparent: true, depthWrite: false, side: THREE.DoubleSide, uniforms: { uT: U.galT, uI: U.gal },
    vertexShader: `varying vec2 vP; void main(){ vP=position.xy; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader: NOISE + `uniform float uT,uI; varying vec2 vP; void main(){ float r=length(vP); if(r>150.) discard; float a=atan(vP.y,vP.x)-uT*.10/(.35+r/45.); float sp=a+2.35*log(max(r,3.)/10.);
 vec2 q=vec2(cos(a),sin(a))*r; float lane=pow(.5+.5*cos(2.*sp+.6),7.); float d=smoothstep(.35,.8,fbm(q*.07+3.1))*lane*smoothstep(6.,22.,r)*smoothstep(150.,80.,r);
 gl_FragColor=vec4(vec3(.06,.045,.035),d*.75*uI); }` });
  const dp = new THREE.Mesh(new THREE.PlaneGeometry(310, 310), dm); dp.position.z = 0.6; dp.renderOrder = 2; GAL.add(dp);
  const N = 1600, pos = new Float32Array(N * 3), col = new Float32Array(N * 3), sz = new Float32Array(N), gs = rng(909); let n = 0, g0 = 0;
  while (n < N && g0++ < N * 40) { const r = 6 + Math.pow(gs(), 0.9) * 110, ph = gs() * 6.2832, sp = ph + 2.35 * Math.log(r / 10), arm = Math.pow(0.5 + 0.5 * Math.cos(2 * sp), 3);
    if (gs() > 0.12 + 0.88 * arm) continue; const big = gs() < 0.06; pos.set([Math.cos(ph) * r, Math.sin(ph) * r, (gs() + gs() - 1) * (1.5 + 3 * Math.exp(-r / 15))], n * 3);
    const warm = gs() < Math.exp(-r / 30); col.set(warm ? [1, 0.86, 0.62] : [0.72, 0.84, 1], n * 3); sz[n] = big ? 2.2 + gs() * 1.6 : 0.6 + gs() * 0.9; n++; }
  const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(pos, 3)); g.setAttribute("color", new THREE.BufferAttribute(col, 3)); g.setAttribute("sz", new THREE.BufferAttribute(sz, 1));
  const sm2 = new THREE.ShaderMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, vertexColors: true, uniforms: { uT: U.galT, uI: U.gal },
    vertexShader: `attribute float sz; uniform float uT; varying vec3 vC; void main(){ vC=color; float r=length(position.xy), a=atan(position.y,position.x)-uT*.10/(.35+r/45.);
      vec3 p=vec3(cos(a)*r,sin(a)*r,position.z); vec4 mv=modelViewMatrix*vec4(p,1.); gl_PointSize=clamp(sz*${(GS * 2400).toFixed(1)}/-mv.z,1.2,6.); gl_Position=projectionMatrix*mv; }`,
    fragmentShader: `uniform float uI; varying vec3 vC; void main(){ vec2 d=gl_PointCoord-.5; float k=dot(d,d)*4.; if(k>1.) discard; float f=exp(-k*5.)+.25*exp(-k*1.2); gl_FragColor=vec4(vC*uI,f*.5*uI); }` });
  const pts = new THREE.Points(g, sm2); pts.frustumCulled = false; GAL.add(pts); }
// the Sun's orbit (gold) and a marker that stands in for the bubble once it is too small to see
const orbit = new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(Array.from({ length: 721 }, (_, i) => { const a = i / 720 * 6.2832; return v3(GC.x - GR * Math.cos(a), 0, GR * Math.sin(a)); })),
  new THREE.LineBasicMaterial({ color: 0xffd27a, transparent: true, opacity: 0, depthWrite: false })); scene.add(orbit);
const marker = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex([[0, "rgba(255,255,255,1)"], [0.15, "rgba(255,220,150,.9)"], [0.5, "rgba(255,170,80,.25)"], [1, "rgba(255,150,60,0)"]]), blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, sizeAttenuation: false, opacity: 0 }));
marker.scale.setScalar(0.05); scene.add(marker);

// ---------- camera path ----------
const tmp = new THREE.Vector3(), tmp2 = new THREE.Vector3();
function cameraAt(t) {
  const S = sunAt(t), E = planetAt(2, t);
  const toSun = tmp.copy(S).sub(E).normalize();
  const side = new THREE.Vector3().crossVectors(toSun, NE).normalize();
  const dE = toSun.clone().multiplyScalar(0.5).addScaledVector(side, 0.82).addScaledVector(NE, 0.3).normalize();
  const dW = v3(0.82, 0.42, -0.2).normalize(), dG = v3(-0.42, 0.72, -0.55).normalize();
  const kT = sm(seg(t, 0.2, 1.7)), k1 = eio(seg(t, 0.25, 2.6)), k3 = eio(seg(t, 2.5, 3.5)), k2 = eio(seg(t, 3.5, 6.8));
  const target = E.clone().lerp(S.clone().addScaledVector(v3(0, 0, 1), -6), kT).lerp(S.clone().addScaledVector(v3(0, 0, 1), -45), k3).lerp(S.clone().lerp(GC, 0.42), Math.pow(k2, 3));
  const d = Math.exp(lerp(lerp(lerp(Math.log(3.4), Math.log(150), k1), Math.log(380), k3), Math.log(36000), k2));
  const dir = dE.clone().lerp(dW, k1).lerp(dG, k2).normalize();
  camera.position.copy(target).addScaledVector(dir, d);
  const up = NE.clone().lerp(v3(0, 0, 1), k1).lerp(v3(1, 0, 0), k2).normalize(); camera.up.copy(up);
  camera.lookAt(target);
  if (k1 < 1) { camera.updateMatrixWorld(); const offY = (1 - kT) * 0.6; camera.position.addScaledVector(new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 1), -offY); camera.lookAt(target.clone().addScaledVector(new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 1), -offY)); }
  camera.updateMatrixWorld(true); return d;
}

// ---------- frame ----------
const proj = (p) => { const v = p.clone().project(camera); return [(v.x * 0.5 + 0.5) * W, (-v.y * 0.5 + 0.5) * H, v.z]; };
const $ = (id) => document.getElementById(id);
const fade = (t, a, b, f = 0.25) => sm(seg(t, a, a + f)) * (1 - sm(seg(t, b - f, b)));
function renderAt(t) {
  U.t.value = t;
  const S = sunAt(t); sunG.position.copy(S); sunLight.position.copy(S); earthMat.uniforms.uSun.value.copy(S);
  sunBody.rotation.y = t * 0.15; rays.material.rotation = t * 0.05;
  bodies.forEach((b, i) => { planetAt(i, t, b.g.position); b.m.rotation.y = t * (b.name === "Earth" ? 0.9 : 0.5) + (b.name === "Earth" ? EARTH_ROT : 0); const dc = b.g.position.distanceTo(camera.position); b.g.visible = b.name === "Earth" || dc > 30; if (b.clouds) b.clouds.rotation.y = t * 1.0; });
  { const E = bodies[2].g.position, mth = 1.1 + t * 2.4; bodies[2].moon.position.copy(E).addScaledVector(EU, Math.cos(mth) * 1.6).addScaledVector(EW, Math.sin(mth) * 1.6); }
  // magnetosphere: nose to the Sun, tail away
  { const E = bodies[2].g.position; MAG.position.copy(E); MAG.lookAt(S); }
  HELI.position.copy(S); HELI.rotation.set(0, 0, 0);
  // trails
  trails.forEach((tr, i) => { const isSun = tr.sun, P = isSun ? 4 : period(PL[i][1]), Tt = Math.min(isSun ? 6 : 1.6 * P, 9);
    for (let k = 0; k < TRN; k++) { const tau = Tt * k / (TRN - 1), tt = t - tau; (isSun ? tmp.copy(sunAt(tt)) : planetAt(i, tt, tmp)); tr.pos.set([tmp.x, tmp.y, tmp.z], k * 3);
      const f = 1 - k / (TRN - 1); tr.aA[k] = Math.pow(f, 1.4) * (isSun ? 0.5 : 0.85); tr.aS[k] = isSun ? 0.9 : 0.16 + 0.14 * f; }
    tr.g.attributes.position.needsUpdate = tr.g.attributes.aA.needsUpdate = tr.g.attributes.aS.needsUpdate = true; });
  // asteroid belt
  belt.dat.forEach(([r, ph, z, s], k) => { const th = ph + 6.2832 * t / period(Math.pow(r / 6, 2)); tmp.copy(S).addScaledVector(EU, r * Math.cos(th)).addScaledVector(EW, r * Math.sin(th)).addScaledVector(NE, z); belt.pos.set([tmp.x, tmp.y, tmp.z], k * 3); });
  belt.p.geometry.attributes.position.needsUpdate = true;
  // solar wind: out to the termination shock, slowing and fading
  wind.dat.forEach(([d, ph], k) => { const u = (ph + t * 0.22) % 1, r = 2.2 + 40 * Math.pow(u, 0.75); tmp.copy(S).addScaledVector(d, r * (d.z > 0 ? 0.8 : 1.15)); wind.pos.set([tmp.x, tmp.y, tmp.z], k * 3);
    wind.aA[k] = Math.sin(Math.PI * u) * 0.5; });
  wind.g.attributes.position.needsUpdate = wind.g.attributes.aA.needsUpdate = true;

  const d = cameraAt(t);
  { const ds = camera.position.distanceTo(S); const k = sm(seg(ds, 25, 90)); corona2.material.opacity = 0.7 * k; rays.material.opacity = 0.55 * k; corona1.material.opacity = 0.35 + 0.55 * k; }
  sky.position.copy(camera.position); sky.scale.setScalar(1e5); skyU.uOut.value = sm(seg(Math.abs(camera.position.y), 1200, 4000));
  // what is visible at each scale
  const close = 1 - sm(seg(d, 5, 30));
  MAG.children.forEach((c) => { if (c.material.uniforms) c.material.uniforms.uK.value = close; else c.material.opacity = 0.16 * close; });
  MAG.visible = close > 0.01;
  const g = sm(seg(Math.log(d), Math.log(450), Math.log(4000))); U.gal.value = g; U.galT.value = t * 1.2;
  SOL.visible = d < 9000; sunG.visible = d < 20000;
  helioMat.uniforms.uK.value = 1 - sm(seg(Math.log(d), Math.log(1500), Math.log(6000)));
  tsMat.uniforms.uK.value = helioMat.uniforms.uK.value * sm(seg(d, 30, 120));
  orbit.material.opacity = 0.6 * sm(seg(Math.log(d), Math.log(2000), Math.log(12000)));
  marker.position.copy(S); marker.material.opacity = sm(seg(Math.log(d), Math.log(700), Math.log(2500))); marker.scale.setScalar(0.045);
  renderer.render(scene, camera);
  // captions
  $("big").style.opacity = fade(t, -1, 2.65, 0.2);
  $("l1").style.opacity = fade(t, 2.7, 3.7, 0.18);
  $("l2").style.opacity = fade(t, 4.4, 99, 0.25);
  const lab = $("lab"), lo = sm(seg(t, 5.2, 5.6)); lab.style.opacity = lo; if (lo > 0) { const [x, y] = proj(S); lab.style.left = (x + 26) + "px"; lab.style.top = (y - 11) + "px"; }
  $("note").style.opacity = 0.8;
}
window.renderAt = renderAt;
const wait = () => { if (loaded) { renderAt(0); window.ready = true; } else setTimeout(wait, 100); }; wait();
