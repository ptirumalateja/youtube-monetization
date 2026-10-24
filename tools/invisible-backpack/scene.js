// The Invisible Backpack (Part 1 of 2): a white stickman walks bent under a weight nobody can see. An X-ray cut shows a
// giant transparent backpack full of glowing labelled rocks. He takes it off, sits, then stacks the rocks one by one
// into a staircase and climbs it while the blue crowd that walked past him stops below and looks up.
// renderAt(t) is pure (no state carried between frames), so frames can be rendered in any order by parallel workers.
// World units are metres. The path runs along +x (he faces +x), the stair rises along +x, the side camera lives on +z.
import * as THREE from 'three';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {UnrealBloomPass} from 'three/addons/postprocessing/UnrealBloomPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';
import {ShaderPass} from 'three/addons/postprocessing/ShaderPass.js';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';

const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960;
const TL=await (await fetch('timeline.json')).json(); const DUR=TL.duration;
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true}); renderer.setPixelRatio(1); renderer.setSize(W,H);
renderer.shadowMap.enabled=true; renderer.shadowMap.type=THREE.PCFSoftShadowMap; document.body.appendChild(renderer.domElement);
const scene=new THREE.Scene(); const FOGC=new THREE.Color(0x0c1422); scene.fog=new THREE.FogExp2(FOGC,0.011);
const cam=new THREE.PerspectiveCamera(40,W/H,0.05,3000);

const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x)); const sstep=(a,b,x)=>{const t=clamp((x-a)/(b-a));return t*t*(3-2*t)}; const lerp=(a,b,t)=>a+(b-a)*t;
const ease=u=>u<0.5?4*u*u*u:1-Math.pow(-2*u+2,3)/2; const V=(x,y,z)=>new THREE.Vector3(x,y,z);
function rng(seed){ let s=seed>>>0; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; }
const yawTo=(a,b)=>Math.atan2(-(b.z-a.z),b.x-a.x);
const rotY=(v,y)=>V(v.x*Math.cos(y)+v.z*Math.sin(y),v.y,-v.x*Math.sin(y)+v.z*Math.cos(y));

// ---------------------------------------------------------------- stage constants
const HX=0;                         // where he stops walking
const SX=0.45, T=0.55, R=0.45, NR=7; // stair: rock k spans x [SX+(k-1)T, SX+(k+1)T], y [(k-1)R, kR]; he stands on its near half
const BAG_G=V(-0.8,0,-0.05);        // where the backpack is set down: behind him, at the foot of the future stair
const BAG_W=0.78, BAG_H=1.05, BAG_D=0.5;
const L={thigh:0.46,shin:0.46,torso:0.56,neck:0.07,head:0.125,upper:0.31,fore:0.29};
const standX=k=>k<=0?HX:SX+(k-0.5)*T, standY=k=>k*R;
const TOPX=SX+6.95*T, TOPY=7*R;

// build cycles: rock k is lifted out of the bag, carried, set down (it grows into step k) and stepped on
const CY=TL.cycles.map(([s,c])=>{ const g1=s+0.33*c, p0=g1+0.07*c, p1=p0+0.18*c, s0=p1+0.1*c, s1=s0+0.32*c; return {g0:s,g1,p0,p1,s0,s1,c}; });
const FOCUS=[...Array(NR)].map((_,i)=>TL.focus0+i*TL.focus_dt);

// ---------------------------------------------------------------- walking: he slows to a stop just after the flash
const V_HERO=0.48, V_CROWD=0.72;
const vHero=t=>V_HERO*(1-sstep(1.85,2.35,t)), vCrowd=t=>V_CROWD*(1-sstep(9.45,9.85,t));
function integ(f,t){ const n=Math.max(1,Math.ceil(t*200)); let s=0; const h=t/n; for(let i=0;i<n;i++) s+=f((i+0.5)*h)*h; return s; }
const DH_TAB=[], DC_TAB=[]; for(let i=0;i<=DUR*100;i++){ DH_TAB.push(integ(vHero,i/100)); DC_TAB.push(integ(vCrowd,i/100)); }
const tab=(A,t)=>{ const x=clamp(t,0,DUR)*100, i=Math.min(A.length-2,Math.floor(x)); return lerp(A[i],A[i+1],x-i); };
const DH=t=>tab(DH_TAB,t), DC=t=>tab(DC_TAB,t);
const HX0=HX-DH(DUR);
const STEP_H=[]; { for(let n=0;n<40;n++){ const d=0.9*(0.25+0.5*n); if(d>DH(DUR)) break; let a=0,b=4; for(let i=0;i<40;i++){ const m=(a+b)/2; if(DH(m)>=d) b=m; else a=m; } STEP_H.push(b); } }

// ---------------------------------------------------------------- sky: dusk over a dust plain, gold afterglow ahead (+x), crescent moon
const SUN_DIR=V(1,0.0,-0.28).normalize(), MOON_DIR=V(-0.66,0.5,-0.56).normalize();
const skyU={uGlow:{value:1}};
const sky=new THREE.Mesh(new THREE.SphereGeometry(1500,48,24),new THREE.ShaderMaterial({side:THREE.BackSide,depthWrite:false,fog:false,uniforms:{...skyU,uSun:{value:SUN_DIR},uMoon:{value:MOON_DIR}},
  vertexShader:`varying vec3 vD; void main(){ vD=normalize(position); gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
  fragmentShader:`varying vec3 vD; uniform vec3 uSun,uMoon; uniform float uGlow;
    float h(vec3 p){ return fract(sin(dot(p,vec3(12.9898,78.233,37.719)))*43758.5453); }
    void main(){ vec3 d=normalize(vD); float y=d.y;
      vec3 c=mix(vec3(0.060,0.105,0.150),vec3(0.018,0.030,0.068),smoothstep(0.0,0.42,y)); c=mix(c,vec3(0.006,0.010,0.026),smoothstep(0.35,0.95,y));
      c=mix(c,vec3(0.030,0.040,0.060),smoothstep(0.0,-0.2,y));
      c+=vec3(0.08,0.22,0.24)*exp(-abs(y-0.05)*16.0)*0.55;                                    // teal band
      float s=max(dot(normalize(vec3(d.x,0.0,d.z)),normalize(vec3(uSun.x,0.0,uSun.z))),0.0);
      c+=vec3(1.0,0.56,0.24)*exp(-max(y,0.0)*11.0)*pow(s,5.0)*0.75*uGlow;                       // gold afterglow on the horizon ahead
      c+=vec3(0.9,0.42,0.2)*exp(-max(y,0.0)*30.0)*pow(s,14.0)*0.6*uGlow;
      vec3 g=floor(d*380.0); float st=step(0.9965,h(g)); float tw=0.5+0.5*h(g+3.1);
      c+=vec3(0.85,0.9,1.0)*st*tw*smoothstep(0.12,0.45,y)*0.95;                                  // stars
      float m=dot(d,uMoon); float md=acos(clamp(m,-1.0,1.0));
      vec3 off=normalize(uMoon+vec3(0.022,0.012,0.012)); float md2=acos(clamp(dot(d,off),-1.0,1.0));
      float disc=smoothstep(0.030,0.027,md)*smoothstep(0.024,0.028,md2);                       // thin crescent
      c+=vec3(1.0,0.95,0.82)*disc*1.6 + vec3(0.5,0.6,0.75)*exp(-md*24.0)*0.10;
      gl_FragColor=vec4(c,1.0);} `}));
scene.add(sky);
// low dunes (soft rolling silhouettes, two rings for parallax)
function dunes(r,hgt,seed,col){ const Rn=rng(seed),seg=400,pos=[],idx=[]; const ph=[Rn()*6,Rn()*6,Rn()*6];
  for(let i=0;i<=seg;i++){ const a=i/seg*Math.PI*2; const y=hgt*(0.55+0.3*Math.sin(a*4+ph[0])+0.15*Math.sin(a*9+ph[1])+0.05*Math.sin(a*17+ph[2]));
    pos.push(Math.cos(a)*r,-3,Math.sin(a)*r, Math.cos(a)*r,y,Math.sin(a)*r); }
  for(let i=0;i<seg;i++){ const k=i*2; idx.push(k,k+1,k+2,k+1,k+3,k+2); }
  const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3)); g.setIndex(idx);
  return new THREE.Mesh(g,new THREE.MeshBasicMaterial({color:col,side:THREE.DoubleSide,fog:false})); }
scene.add(dunes(700,16,3,0x0f1826)); scene.add(dunes(420,7,9,0x0b121d));

// ground: dust plain with a packed path
function noiseTex(size,seed,base,amp,blobs){ const c=document.createElement('canvas'); c.width=c.height=size; const g=c.getContext('2d'); const Rn=rng(seed);
  const im=g.createImageData(size,size); for(let i=0;i<size*size;i++){ const v=clamp(base+(Rn()-0.5)*amp,0,255); im.data[i*4]=im.data[i*4+1]=im.data[i*4+2]=v; im.data[i*4+3]=255; }
  g.putImageData(im,0,0); g.globalAlpha=0.25; for(let k=0;k<blobs;k++){ g.fillStyle=Rn()<0.5?'#000':'#fff'; g.beginPath(); g.arc(Rn()*size,Rn()*size,Rn()*size*0.1,0,7); g.fill(); }
  const t=new THREE.CanvasTexture(c); t.wrapS=t.wrapT=THREE.RepeatWrapping; return t; }
const gTex=noiseTex(256,5,128,70,50); gTex.repeat.set(220,220);
const ground=new THREE.Mesh(new THREE.PlaneGeometry(1600,1600),new THREE.MeshStandardMaterial({color:0x2f3442,roughness:1,map:gTex,bumpMap:gTex,bumpScale:0.5}));
ground.rotation.x=-Math.PI/2; ground.receiveShadow=true; scene.add(ground);
{ const pt=noiseTex(256,8,150,50,30); pt.repeat.set(60,1);
  const path=new THREE.Mesh(new THREE.PlaneGeometry(80,1.9),new THREE.MeshStandardMaterial({color:0x3d4150,roughness:1,map:pt,transparent:true,opacity:0.55}));
  path.rotation.x=-Math.PI/2; path.position.set(10,0.003,-0.45); path.receiveShadow=true; scene.add(path); }
// scattered pebbles for scale and parallax
{ const Rn=rng(12); const geo=new THREE.DodecahedronGeometry(1,0); const m=new THREE.MeshStandardMaterial({color:0x3a3c46,roughness:1,flatShading:true});
  const N=420, im=new THREE.InstancedMesh(geo,m,N); const M=new THREE.Matrix4(), Q=new THREE.Quaternion(), E=new THREE.Euler();
  for(let i=0;i<N;i++){ let x,z; do{ x=-14+Rn()*34; z=-12+Rn()*16; }while(Math.abs(z+0.45)<1.1 || (x>-0.6&&x<5.4&&Math.abs(z)<0.9));
    const s=0.02+Math.pow(Rn(),3)*0.12; M.compose(V(x,s*0.3,z),Q.setFromEuler(E.set(Rn()*6,Rn()*6,Rn()*6)),V(s,s*0.6,s)); im.setMatrixAt(i,M); }
  im.receiveShadow=true; im.castShadow=true; scene.add(im); }

// ---------------------------------------------------------------- lights
const hemi=new THREE.HemisphereLight(0x5a70a0,0x15171e,0.95); scene.add(hemi);
const key=new THREE.DirectionalLight(0xa9bce6,0.95); key.castShadow=true; key.shadow.mapSize.set(2048,2048);
Object.assign(key.shadow.camera,{left:-6,right:6,top:6,bottom:-6,near:1,far:60}); key.shadow.bias=-0.0005; key.shadow.normalBias=0.02; scene.add(key,key.target);
const rim=new THREE.DirectionalLight(0xffb470,0.55); scene.add(rim,rim.target);

// ---------------------------------------------------------------- glow sprites
function glowTex(){ const c=document.createElement('canvas'); c.width=c.height=128; const g=c.getContext('2d'); const r=g.createRadialGradient(64,64,0,64,64,64);
  r.addColorStop(0,'rgba(255,255,255,1)'); r.addColorStop(0.2,'rgba(255,255,255,0.5)'); r.addColorStop(0.5,'rgba(255,255,255,0.12)'); r.addColorStop(1,'rgba(255,255,255,0)'); g.fillStyle=r; g.fillRect(0,0,128,128);
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; return t; }
const GLOW=glowTex();
const glow=(col,s,op)=>{ const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:GLOW,color:col,transparent:true,opacity:op,depthWrite:false,blending:THREE.AdditiveBlending,fog:false})); sp.scale.set(s,s,1); scene.add(sp); return sp; };

// ---------------------------------------------------------------- rocks: rough faceted basalt with glowing amber cracks
function crackTex(seed){ const c=document.createElement('canvas'); c.width=512; c.height=256; const g=c.getContext('2d'); const Rn=rng(seed);
  g.fillStyle='#120600'; g.fillRect(0,0,512,256);
  const line=(w,col,blur)=>{ g.strokeStyle=col; g.lineWidth=w; g.shadowColor=col; g.shadowBlur=blur; };
  const paths=[]; for(let k=0;k<11;k++){ let x=Rn()*512, y=Rn()*256, a=Rn()*6.28; const p=[[x,y]]; const n=6+Math.floor(Rn()*10);
    for(let i=0;i<n;i++){ a+=(Rn()-0.5)*1.4; const l=10+Rn()*26; x+=Math.cos(a)*l; y+=Math.sin(a)*l*0.6; p.push([x,y]); } paths.push(p); }
  for(const [w,col,b] of [[7,'rgba(255,120,30,0.35)',14],[3,'rgba(255,170,70,0.9)',6],[1.2,'rgba(255,236,190,1)',2]]){ line(w,col,b);
    for(const p of paths){ g.beginPath(); p.forEach(([x,y],i)=>i?g.lineTo(x,y):g.moveTo(x,y)); g.stroke(); } }
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; t.wrapS=THREE.RepeatWrapping; return t; }
const ROCK_COL=noiseTex(256,31,120,90,40);
function rockGeo(seed){
  const g=new THREE.IcosahedronGeometry(1,3); const p=g.attributes.position; const Rn=rng(seed);
  const waves=[]; for(let i=0;i<10;i++){ waves.push([V(Rn()*2-1,Rn()*2-1,Rn()*2-1).normalize(),1.4+Rn()*5,Rn()*6.28,0.12/(1+i*0.5)]); }
  const v=new THREE.Vector3(); let lo=V(9,9,9), hi=V(-9,-9,-9);
  for(let i=0;i<p.count;i++){ v.set(p.getX(i),p.getY(i),p.getZ(i));
    const n=2.4; const s=Math.pow(Math.pow(Math.abs(v.x),n)+Math.pow(Math.abs(v.y),n)+Math.pow(Math.abs(v.z),n),1/n); v.multiplyScalar(1/s);
    let d=0; for(const [dir,f,ph,a] of waves) d+=a*Math.sin(v.dot(dir)*f+ph); v.multiplyScalar(1+d);
    if(v.y>0.62) v.y=0.62+(v.y-0.62)*0.18; if(v.y<-0.72) v.y=-0.72+(v.y+0.72)*0.2;     // flat-ish top (a tread) and a seat underneath
    p.setXYZ(i,v.x,v.y,v.z); lo.min(v); hi.max(v); }
  const c=lo.clone().add(hi).multiplyScalar(0.5), s=hi.clone().sub(lo);
  for(let i=0;i<p.count;i++) p.setXYZ(i,(p.getX(i)-c.x)/s.x,(p.getY(i)-c.y)/s.y,(p.getZ(i)-c.z)/s.z);   // unit box, centred
  g.computeVertexNormals(); return g; }
const ROCKS=[]; { const Rn=rng(404);
  // slots inside the bag (bag-local, unscaled): rock 1 is on top, the bottom pair comes out last
  const SLOT=[[0.0,0.33,0.0],[-0.18,0.11,0.03],[0.18,0.12,-0.03],[-0.17,-0.11,-0.02],[0.18,-0.12,0.03],[-0.17,-0.34,0.02],[0.18,-0.35,-0.02]];
  for(let i=0;i<NR;i++){ const mat=new THREE.MeshStandardMaterial({color:0x5a4e46,roughness:0.92,metalness:0,map:ROCK_COL,flatShading:true,emissive:0xffa24a,emissiveMap:crackTex(70+i*13),emissiveIntensity:1});
    const m=new THREE.Mesh(rockGeo(900+i*77),mat); m.castShadow=true; m.receiveShadow=true; m.matrixAutoUpdate=false; m.frustumCulled=false; scene.add(m);
    const gl=glow(0xff9a40,1,0); const pl=new THREE.PointLight(0xff9a48,0,2.6,2); scene.add(pl);
    ROCKS.push({m,mat,gl,pl,slot:V(...SLOT[i]),sb:V(0.33+Rn()*0.04,0.18+Rn()*0.03,0.27+Rn()*0.04),ss:V(1.16+Rn()*0.06,0.47+Rn()*0.02,0.9+Rn()*0.08),
      yawB:(Rn()-0.5)*0.6,yawS:(Rn()-0.5)*0.16,zS:(Rn()-0.5)*0.06,tilt:(Rn()-0.5)*0.05}); } }

// ---------------------------------------------------------------- the backpack: x-ray glass (fresnel rim, ~30% average opacity, warm inner glow)
const bagU={uVis:{value:0},uX:{value:0},uFill:{value:1}};
const bagOuter=new THREE.ShaderMaterial({transparent:true,depthWrite:false,side:THREE.FrontSide,uniforms:bagU,
  vertexShader:`varying vec3 vN,vV; void main(){ vec4 mv=modelViewMatrix*vec4(position,1.0); vN=normalize(normalMatrix*normal); vV=normalize(-mv.xyz); gl_Position=projectionMatrix*mv; }`,
  fragmentShader:`varying vec3 vN,vV; uniform float uVis,uX,uFill; void main(){ float f=1.0-abs(dot(normalize(vN),normalize(vV))); f=pow(f,1.8);
    vec3 rimC=mix(vec3(0.80,0.93,0.92),vec3(0.55,0.95,1.0),uX); vec3 body=vec3(1.0,0.62,0.28)*(0.22+0.25*uFill);
    vec3 c=mix(body,rimC*(1.1+0.5*uX),f); float a=uVis*(0.12+0.62*f)*(1.0+0.25*uX); gl_FragColor=vec4(c,clamp(a,0.0,1.0)); }`});
const bagInner=new THREE.ShaderMaterial({transparent:true,depthWrite:false,side:THREE.BackSide,blending:THREE.AdditiveBlending,uniforms:bagU,
  vertexShader:`varying vec3 vN,vV; void main(){ vec4 mv=modelViewMatrix*vec4(position,1.0); vN=normalize(normalMatrix*normal); vV=normalize(-mv.xyz); gl_Position=projectionMatrix*mv; }`,
  fragmentShader:`varying vec3 vN,vV; uniform float uVis,uX,uFill; void main(){ float f=abs(dot(normalize(vN),normalize(vV)));
    gl_FragColor=vec4(vec3(1.0,0.55,0.22)*pow(f,2.0)*0.16*uVis*(0.25+0.75*uFill)+vec3(0.3,0.7,0.8)*0.05*uX*uVis,1.0); }`});
const bag=new THREE.Group(); bag.matrixAutoUpdate=false; scene.add(bag);
function bagPart(geo,x,y,z,rx=0){ for(const mat of [bagInner,bagOuter]){ const m=new THREE.Mesh(geo,mat); m.position.set(x,y,z); m.rotation.x=rx; m.renderOrder=mat===bagOuter?12:11; m.frustumCulled=false; bag.add(m); } }
function taper(g,hh){ const p=g.attributes.position; for(let i=0;i<p.count;i++){ const yn=p.getY(i)/hh, u=Math.max(0,yn);
  p.setX(i,p.getX(i)*(1-0.17*u*u)*(1+0.04*Math.max(0,-yn))); p.setZ(i,p.getZ(i)*(1-0.12*u*u)); } g.computeVertexNormals(); return g; }
bagPart(taper(new RoundedBoxGeometry(BAG_W,BAG_H,BAG_D,6,0.2),BAG_H/2),0,0,0);
for(const s of [-1,1]){                                                                             // shoulder straps (towards +z, the wearer)
  const c=new THREE.CatmullRomCurve3([V(s*0.21,0.28,0.24),V(s*0.15,0.2,0.33),V(s*0.12,0.06,0.37),V(s*0.14,-0.16,0.35),V(s*0.2,-0.34,0.25)]);
  bagPart(new THREE.TubeGeometry(c,24,0.036,8,false),0,0,0); }
bagPart(new THREE.TorusGeometry(0.09,0.018,8,20,Math.PI),0,BAG_H*0.57,0);                           // grab handle
const bagGlow=glow(0xffa050,1.4,0); const bagLight=new THREE.PointLight(0xffa050,0,3.2,2); scene.add(bagLight);

// ---------------------------------------------------------------- lamp (kindles on the top step)
const lamp=new THREE.Group(); scene.add(lamp);
{ const metal=new THREE.MeshStandardMaterial({color:0x1d1f26,roughness:0.5,metalness:0.7});
  const base=new THREE.Mesh(new THREE.CylinderGeometry(0.075,0.09,0.05,20),metal); base.position.y=0.025; base.castShadow=true; lamp.add(base);
  const cap=new THREE.Mesh(new THREE.ConeGeometry(0.085,0.07,20),metal); cap.position.y=0.25; lamp.add(cap);
  for(let i=0;i<4;i++){ const b=new THREE.Mesh(new THREE.CylinderGeometry(0.007,0.007,0.17,6),metal); const a=i*Math.PI/2+0.4; b.position.set(Math.cos(a)*0.066,0.135,Math.sin(a)*0.066); lamp.add(b); }
  const ring=new THREE.Mesh(new THREE.TorusGeometry(0.035,0.006,6,16),metal); ring.position.y=0.3; lamp.add(ring); }
const lampFlame=new THREE.Mesh(new THREE.SphereGeometry(0.045,16,12),new THREE.MeshBasicMaterial({color:0xffe0a8,transparent:true})); lamp.add(lampFlame); lampFlame.position.y=0.13;
const lampGlow=glow(0xffc070,0.8,0); const lampLight=new THREE.PointLight(0xffc27a,0,7,2); scene.add(lampLight);

// ---------------------------------------------------------------- dust: drifting motes (world-fixed, camera-wrapped) and puffs
const moteU={camPos:{value:V(0,0,0)},box:{value:12},wx:{value:0},t:{value:0},pxs:{value:H/1920},op:{value:1}};
{ const n=3200,Rn=rng(91),p=[],s=[]; for(let i=0;i<n;i++){ p.push(Rn(),Rn(),Rn()); s.push(Rn()); }
  const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(p,3)); g.setAttribute('seed',new THREE.Float32BufferAttribute(s,1));
  const pts=new THREE.Points(g,new THREE.ShaderMaterial({transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,fog:false,uniforms:moteU,
    vertexShader:`uniform vec3 camPos; uniform float box,wx,t,pxs; attribute float seed; varying float vA;
      void main(){ vec3 p=position*box; p.x+=wx*(0.7+0.6*seed); p.y+=sin(t*0.5+seed*6.0)*0.25; p.z+=cos(t*0.3+seed*5.0)*0.2;
        vec3 rel=mod(p-camPos+box*0.5,box)-box*0.5; vec3 w=camPos+rel; w.y=abs(w.y);
        vec4 mv=modelViewMatrix*vec4(w,1.0); float d=-mv.z; vA=smoothstep(0.3,1.5,d)*(1.0-smoothstep(box*0.3,box*0.5,length(rel)))*(0.3+0.7*seed)*(1.0-smoothstep(1.0,5.0,w.y)*0.6);
        gl_PointSize=clamp(30.0/d,1.0,5.0)*pxs*1.8; gl_Position=projectionMatrix*mv; }`,
    fragmentShader:`uniform float op; varying float vA; void main(){ float a=smoothstep(0.5,0.0,length(gl_PointCoord-0.5)); gl_FragColor=vec4(vec3(1.0,0.86,0.66)*a*vA*0.42*op,1.0);} `}));
  pts.frustumCulled=false; scene.add(pts); }
const WIND=t=>0.12+1.0*sstep(14.6,15.6,t); const WX_TAB=[]; for(let i=0;i<=DUR*100;i++) WX_TAB.push(integ(WIND,i/100));
function puffTex(){ const c=document.createElement('canvas'); c.width=c.height=128; const g=c.getContext('2d'); const Rn=rng(7);
  for(let k=0;k<18;k++){ const x=34+Rn()*60,y=34+Rn()*60,r=16+Rn()*28; const gr=g.createRadialGradient(x,y,0,x,y,r); gr.addColorStop(0,'rgba(255,255,255,0.3)'); gr.addColorStop(1,'rgba(255,255,255,0)'); g.fillStyle=gr; g.fillRect(0,0,128,128); }
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; return t; }
const PUFF=puffTex(); const puffPool=[]; for(let i=0;i<160;i++){ const s=new THREE.Sprite(new THREE.SpriteMaterial({map:PUFF,color:0x8f8577,transparent:true,opacity:0,depthWrite:false,fog:true})); s.visible=false; s.renderOrder=8; scene.add(s); puffPool.push(s); }
const PUFFS=[];   // {t0, p, size, n, spread}, filled once the motion is defined below

// ---------------------------------------------------------------- stickman rig (tube limbs, sphere head and a small nose so the look direction reads)
function makeFig(color,emis,r){
  const mat=new THREE.MeshStandardMaterial({color,roughness:0.55,metalness:0,emissive:new THREE.Color(emis),emissiveIntensity:1});
  const cyl=new THREE.CylinderGeometry(1,1,1,12,1,true), sph=new THREE.SphereGeometry(1,16,12);
  const mk=g=>{ const m=new THREE.Mesh(g,mat); m.castShadow=true; m.frustumCulled=false; scene.add(m); return m; };
  const F={mat,r,bones:[...Array(9)].map(()=>mk(cyl)),joints:[...Array(12)].map(()=>mk(sph)),head:mk(sph),nose:mk(sph)}; return F; }
const UPV=V(0,1,0), _q=new THREE.Quaternion();
function bone(m,a,b,r){ const d=b.clone().sub(a); const len=Math.max(d.length(),1e-4); m.position.copy(a).add(b).multiplyScalar(0.5); m.scale.set(r,len,r); m.quaternion.setFromUnitVectors(UPV,d.multiplyScalar(1/len)); }
function ball(m,p,r){ m.position.copy(p); m.scale.setScalar(r); }
function ik(S,Tg,pole){ const d=Tg.clone().sub(S); const dist=Math.min(Math.max(d.length(),0.05),L.upper+L.fore-0.003); const dn=d.normalize();
  const a=(L.upper*L.upper-L.fore*L.fore+dist*dist)/(2*dist); const h=Math.sqrt(Math.max(0,L.upper*L.upper-a*a));
  const p=pole.clone().addScaledVector(dn,-pole.dot(dn)); if(p.lengthSq()<1e-6) p.set(0,-1,0); p.normalize();
  return {E:S.clone().addScaledVector(dn,a).addScaledVector(p,h), Hd:S.clone().addScaledVector(dn,dist)}; }
// pose: p torso pitch forward, tilt head pitch (negative looks up), hy head yaw, aL/aR thigh angle, kL/kR knee bend, sL/sR arm angle,
// eL/eR elbow flex, dy hip offset; tL/tR optional world hand targets with weights wL/wR. All angles in radians.
const P0={p:0.05,tilt:0,hy:0,aL:0.05,aR:-0.05,kL:0.05,kR:0.05,sL:0.12,sR:-0.05,eL:0.2,eR:0.2,dy:0};
const POSES={
  stand:{...P0},
  heavy:{...P0,p:0.6,tilt:0.24,aL:0.12,aR:0.12,kL:0.28,kR:0.28,sL:0.12,sR:0.18,eL:0.25,eR:0.2},
  crouch:{...P0,p:1.0,tilt:-0.3,aL:1.2,aR:1.0,kL:1.95,kR:1.75,sL:0.6,sR:0.7,eL:0.1,eR:0.1},
  carry:{...P0,p:0.14,tilt:0.12,aL:0.1,aR:-0.08,kL:0.15,kR:0.12,sL:0.6,sR:0.6,eL:1.2,eR:1.2},
  place:{...P0,p:0.75,tilt:-0.05,aL:0.75,aR:0.2,kL:0.95,kR:0.35,sL:1.1,sR:1.1,eL:0.35,eR:0.35},
  sit:{...P0,p:0.32,tilt:0.18,aL:2.05,aR:1.85,kL:2.5,kR:2.3,sL:0.95,sR:0.85,eL:0.35,eR:0.4,dy:-0.12},
  tall:{...P0,p:-0.03,tilt:-0.16,aL:0.06,aR:-0.06,kL:0.02,kR:0.02,sL:0.1,sR:-0.08,eL:0.12,eR:0.1},
};
const blend=(a,b,u)=>{ const o={}; for(const k in P0) o[k]=lerp(a[k]??P0[k],b[k]??P0[k],u); for(const s of ['L','R']){ const ta=a['t'+s], tb=b['t'+s]; const wa=a['w'+s]||0, wb=b['w'+s]||0;
  if(ta||tb){ o['t'+s]=(ta&&tb)?ta.clone().lerp(tb,u):(ta||tb).clone(); o['w'+s]=lerp(wa,wb,u); o['p'+s]=(b['p'+s]||a['p'+s]); } } return o; };
// world-space skeleton for a figure standing at root (feet level), facing yaw
function skel(P,root,yaw){
  const leg=(a,k)=>{ const kn=[Math.sin(a)*L.thigh,-Math.cos(a)*L.thigh]; const b=a-k; return [kn,[kn[0]+Math.sin(b)*L.shin,kn[1]-Math.cos(b)*L.shin]]; };
  const [kl,fl]=leg(P.aL,P.kL), [kr,fr]=leg(P.aR,P.kR);
  const hipY=-Math.min(fl[1],fr[1])+0.035+P.dy, hipX=-(fl[0]+fr[0])*0.5*0.6;
  const W_=(x,y,z)=>rotY(V(x,y,z),yaw).add(root);
  const J={}; J.hip=W_(hipX,hipY,0); J.hipL=W_(hipX,hipY,0.06); J.hipR=W_(hipX,hipY,-0.06);
  J.kL=W_(hipX+kl[0],hipY+kl[1],0.07); J.fL=W_(hipX+fl[0],hipY+fl[1],0.07); J.kR=W_(hipX+kr[0],hipY+kr[1],-0.07); J.fR=W_(hipX+fr[0],hipY+fr[1],-0.07);
  const nx=hipX+Math.sin(P.p)*L.torso, ny=hipY+Math.cos(P.p)*L.torso; J.neck=W_(nx,ny,0);
  const hd=P.p+P.tilt; J.head=W_(nx+Math.sin(hd)*(L.neck+L.head),ny+Math.cos(hd)*(L.neck+L.head),0);
  J.face=rotY(rotY(V(Math.cos(hd),-Math.sin(hd),0),P.hy),yaw);
  const shx=nx-Math.sin(P.p)*0.05, shy=ny-Math.cos(P.p)*0.05;
  for(const [s,z] of [['L',0.035],['R',-0.035]]){ const S=W_(shx,shy,z); const sa=P['s'+s], ea=P['e'+s];
    const E=W_(shx+Math.sin(sa)*L.upper,shy-Math.cos(sa)*L.upper,z*2.4); const Hd=W_(shx+Math.sin(sa)*L.upper+Math.sin(sa+ea)*L.fore,shy-Math.cos(sa)*L.upper-Math.cos(sa+ea)*L.fore,z*3);
    let E2=E,H2=Hd; const w=P['w'+s]||0;
    if(w>0&&P['t'+s]){ const tg=Hd.clone().lerp(P['t'+s],w); const pole=P['p'+s]?P['p'+s].clone():E.clone().sub(S.clone().add(Hd).multiplyScalar(0.5)); const r=ik(S,tg,pole); E2=r.E; H2=r.Hd; }
    J['sh'+s]=S; J['el'+s]=E2; J['h'+s]=H2; }
  J.fwd=rotY(V(1,0,0),yaw); J.up=J.neck.clone().sub(J.hip).normalize(); return J; }
function poseFig(F,J){ const B=F.bones, r=F.r;
  bone(B[0],J.hip,J.neck,r); bone(B[1],J.hipL,J.kL,r); bone(B[2],J.kL,J.fL,r); bone(B[3],J.hipR,J.kR,r); bone(B[4],J.kR,J.fR,r);
  bone(B[5],J.shL,J.elL,r); bone(B[6],J.elL,J.hL,r); bone(B[7],J.shR,J.elR,r); bone(B[8],J.elR,J.hR,r);
  [J.hipL,J.hipR,J.kL,J.kR,J.fL,J.fR,J.shL,J.shR,J.elL,J.elR,J.hL,J.hR].forEach((p,i)=>ball(F.joints[i],p,r*(i>=10?1.35:1.05)));
  ball(F.head,J.head,L.head); ball(F.nose,J.head.clone().addScaledVector(J.face,L.head*0.92),0.032); }
// gait: phase ph (radians), amplitude a 0..1
function gait(P,ph,a,A=0.3,K=0.55,arm=0.15){ const s=Math.sin(ph), c=Math.cos(ph);
  return {...P,aL:P.aL+A*a*s,aR:P.aR-A*a*s,kL:P.kL+K*a*Math.max(0,c),kR:P.kR+K*a*Math.max(0,-c),sL:P.sL-arm*a*s,sR:P.sR+arm*a*s}; }

const hero=makeFig('#efe6d4','#2a241a',0.045);
const CROWD=[[1.8,-0.9,0.1,5.15,-0.85],[3.0,-1.6,1.7,5.65,-1.6],[4.2,-2.3,3.3,6.2,-1.05]].map(([x0,z,ph,tx,tz],i)=>({x0:HX0+x0,z,ph,tx,tz,i,f:makeFig('#5872ad','#121d3c',0.04)}));

// ---------------------------------------------------------------- the backpack's motion: on his back, lifted off and set down, emptied
function bagBasisOnBack(J){ const u=J.up.clone(), back=J.fwd.clone().addScaledVector(u,-J.fwd.dot(u)).normalize().negate();
  const zA=back.clone().negate(), xA=u.clone().cross(zA).normalize(); const m=new THREE.Matrix4().makeBasis(xA,u,zA);
  const c=J.hip.clone().add(J.neck).multiplyScalar(0.5).addScaledVector(u,0.1).addScaledVector(back,BAG_D*0.5+0.055);
  return {p:c,q:new THREE.Quaternion().setFromRotationMatrix(m)}; }
const removedAt=t=>{ let n=0; for(const c of CY) n+=sstep(c.g0,c.g1,t); return n; };
function bagGround(t){ const rm=removedAt(t)/NR; const sy=1-0.3*rm; const q=new THREE.Quaternion().setFromEuler(new THREE.Euler(-0.1*rm,1.45,0.06*rm));
  return {p:V(BAG_G.x,BAG_H*0.5*sy+0.002,BAG_G.z),q,sy}; }
const LIFT0=7.6, LIFT1=8.0;   // the bag comes off his back and lands at TL.thud

// ---------------------------------------------------------------- hero motion
function cycPose(k,t,c){                 // pose while working on rock k (1-based) during cycle c
  const k0=k-1, root0=V(standX(k0),standY(k0),0), root1=V(standX(k),standY(k),0);
  let P, root=root0.clone(), yaw=0;
  const bagTop=V(BAG_G.x,BAG_H*0.9,BAG_G.z); let toBag=yawTo(root0,bagTop); if(toBag>0) toBag-=2*Math.PI;
  if(t<c.g1){ const u=(t-c.g0)/(c.g1-c.g0);
    if(k===1){ yaw=lerp(SIT_YAW,toBag,sstep(0,0.45,u)); P=blend(POSES.stand,POSES.crouch,sstep(0.05,0.55,u)*(1-0.6*sstep(0.7,1,u))); }
    else { yaw=lerp(0,toBag*0.55,sstep(0,0.4,u))*(1-sstep(0.75,1,u)); P=blend(POSES.stand,{...POSES.place,p:0.4,kL:0.4,kR:0.3,aL:0.3},sstep(0,0.5,u)*(1-sstep(0.7,1,u))); } }
  else if(t<c.p0){ yaw=lerp(k===1?toBag:0,0,sstep(c.g1,c.p0,t)); P=blend(POSES.carry,POSES.carry,0); }
  else if(t<c.p1){ P=blend(POSES.carry,POSES.place,sstep(c.p0,c.p1,t)); }
  else if(t<c.s0){ P=blend(POSES.place,POSES.stand,sstep(c.p1,c.s0,t)); }
  else { const u=sstep(c.s0,c.s1,t), b=Math.sin(Math.PI*clamp((t-c.s0)/(c.s1-c.s0)));
    root=V(lerp(root0.x,root1.x,u),lerp(root0.y,root1.y,sstep(0.15,0.8,clamp((t-c.s0)/(c.s1-c.s0)))),0);
    P={...POSES.stand,p:0.05+0.32*b,aL:0.05+0.95*b,kL:0.05+1.25*b,aR:-0.05-0.15*b,sL:0.12-0.35*b,sR:-0.05+0.4*b}; }
  return {P,root,yaw}; }
const RELIEF={...POSES.stand,p:0.06,hy:0.3};
const SIT_YAW=-Math.PI/2;   // he sits turned toward the side (+z), the bag at his right
const SIT=(()=>{ const J=skel(POSES.sit,V(HX,0,0),SIT_YAW); return {...POSES.sit,tL:J.kL.clone().add(rotY(V(0.03,0.05,0.04),SIT_YAW)),tR:J.kR.clone().add(rotY(V(0.03,0.05,-0.04),SIT_YAW)),wL:1,wR:1,pL:rotY(V(0,-1,0.5),SIT_YAW),pR:rotY(V(0,-1,-0.5),SIT_YAW)}; })();
const sitBlend=t=>blend(RELIEF,SIT,sstep(8.2,8.65,t)*(1-sstep(9.05,9.35,t)));
function heroAt(t,bare=false){           // bare: no hand targets (used by the bag and rock paths, which only need the torso)
  let P, root=V(HX,0,0), yaw=0;
  const breath=Math.sin(2*Math.PI*0.62*t);
  if(t<2.4){ const d=DH(t), a=vHero(t)/V_HERO, ph=d/0.9*2*Math.PI; root=V(HX0+d,0,0); P=gait({...POSES.heavy,p:POSES.heavy.p+0.025*Math.sin(2*ph)*a+0.035*breath*(1-a)},ph,a,0.3,0.5,0.12); }
  else if(t<7.42){ const u=sstep(7.0,7.4,t); P=blend({...POSES.heavy,p:0.6+0.035*breath,tilt:0.24+0.03*breath},{...POSES.heavy,p:0.4,tilt:-0.62,kL:0.2,kR:0.2},u); }
  else if(t<9.15){
    if(t<LIFT1+0.12){ const reach=sstep(7.42,7.6,t), carry=sstep(LIFT0,LIFT1,t);
      const base=blend({...POSES.heavy,p:0.4,tilt:-0.62,kL:0.2,kR:0.2},{...POSES.stand,p:0.42,tilt:0.25,hy:0.5,kL:0.35,kR:0.45,aR:0.2},carry);
      if(bare) P=base; else { const B=bagAt(t); const tl=B.p.clone().add(V(0.21,0.28,0.24).applyQuaternion(B.q)), tr=B.p.clone().add(V(-0.21,0.28,0.24).applyQuaternion(B.q));
        const top=B.p.clone().add(V(0,BAG_H*0.55*B.sy,0).applyQuaternion(B.q)); const w=reach*(1-sstep(7.8,7.92,t));
        P={...base,tL:tl.clone().lerp(top.clone().add(V(0,0.02,0.06)),carry),tR:tr.clone().lerp(top.clone().add(V(0,0.02,-0.06)),carry),wL:w,wR:w,pL:V(-0.3,0.2,0.6),pR:V(-0.3,0.2,-0.6)}; } }
    else if(t<8.2) P=blend({...POSES.stand,p:0.42,tilt:0.25,hy:0.5,kL:0.35,kR:0.45,aR:0.2},RELIEF,sstep(LIFT1+0.12,8.2,t));
    else { P=sitBlend(t); yaw=SIT_YAW*sstep(8.1,8.45,t)*(1-sstep(9.15,9.35,t)); } }
  else { let k=1; while(k<NR&&t>=CY[k].g0) k++; const c=CY[k-1];
    const r=cycPose(k,t,c); P=r.P; root=r.root; yaw=r.yaw;
    if(k===1&&t<9.35){ P=blend(sitBlend(t),P,sstep(9.2,9.35,t)); }
    if(!bare){ const rk=rockAt(k-1,t);                               // hands on the rock while it is held
      const hold0=k===1?c.g0+0.2*(c.g1-c.g0):c.g1-0.12;
      if(t>hold0 && t<c.p1+0.04){ const side=rotY(V(0,0,1),rk.yaw); const half=rk.size.z*0.5+0.02;
        const w=(k===1?sstep(hold0,c.g0+0.5*(c.g1-c.g0),t):sstep(hold0,c.g1,t))*(1-sstep(c.p1,c.p1+0.04,t));
        P={...P,tL:rk.pos.clone().addScaledVector(side,half),tR:rk.pos.clone().addScaledVector(side,-half),wL:w,wR:w,pL:V(0,-0.6,1),pR:V(0,-0.6,-1)}; }
      else if(k>1&&t>=c.g0&&t<c.g1){ const w=sstep(c.g0,c.g0+0.15,t)*0.55;            // reaches toward the rock rising out of the bag
        P={...P,tL:rk.pos.clone().add(V(0,0,0.15)),tR:rk.pos.clone().add(V(0,0,-0.15)),wL:w,wR:w}; } }
    if(t>=CY[NR-1].s1){ const u=sstep(CY[NR-1].s1,CY[NR-1].s1+0.55,t); root=V(lerp(standX(NR),TOPX,u),TOPY,0);
      P=blend(gait(POSES.stand,u*Math.PI*2,Math.sin(Math.PI*u),0.25,0.45,0.1),POSES.tall,sstep(0.4,1,u));
      P={...P,p:P.p+0.008*Math.sin(2*Math.PI*0.25*t)}; } }
  return {P,root,yaw}; }

// ---------------------------------------------------------------- bag transform over time
function bagAt(t){
  if(t<LIFT0){ const h=heroAt(Math.min(t,LIFT0-1e-4),true); const J=skel(h.P,h.root,h.yaw); const b=bagBasisOnBack(J); return {...b,sy:1}; }
  const g=bagGround(t); if(t>=LIFT1) return g;
  const h=heroAt(LIFT0-1e-4,true); const b=bagBasisOnBack(skel(h.P,h.root,h.yaw)); const u=ease(sstep(LIFT0,LIFT1,t));
  const mid=b.p.clone().lerp(g.p,0.5).add(V(-0.1,0.15,0)); const p=b.p.clone().multiplyScalar((1-u)*(1-u)).addScaledVector(mid,2*u*(1-u)).addScaledVector(g.p,u*u);
  return {p,q:b.q.clone().slerp(g.q,u),sy:1}; }

// ---------------------------------------------------------------- rock transform over time
const carryPoint=(J)=>J.neck.clone().addScaledVector(J.fwd,0.36).add(V(0,-0.36,0));
function rockAt(i,t){
  const Rk=ROCKS[i], c=CY[i], k=i+1;
  const B=bagAt(Math.min(t,c.g0)); const slot=Rk.slot.clone().multiply(V(1,B.sy,1)); const qs=new THREE.Quaternion().setFromEuler(new THREE.Euler(0,Rk.yawB+spinAt(i,t),0));
  const inBag={pos:B.p.clone().add(slot.applyQuaternion(B.q)),q:B.q.clone().multiply(qs),size:Rk.sb.clone()};
  const final={pos:V(SX+k*T,(k-1)*R+Rk.ss.y*0.5-0.012,Rk.zS),q:new THREE.Quaternion().setFromEuler(new THREE.Euler(0,Rk.yawS,Rk.tilt)),size:Rk.ss.clone()};
  const yawOf=q=>new THREE.Euler().setFromQuaternion(q,'YXZ').y;
  if(t<c.g0) return {...inBag,yaw:yawOf(inBag.q),state:0};
  if(t>=c.p1){ const u=clamp((t-c.p1)/0.2); const e=1+0.08*Math.sin(Math.PI*u)*(1-u);             // grows into the step with a small pop
    const g=sstep(0,1,u); const size=Rk.sb.clone().lerp(Rk.ss,g).multiplyScalar(e); const pos=final.pos.clone(); pos.y=(k-1)*R+size.y*0.5-0.012;
    return {pos,q:final.q,size,yaw:Rk.yawS,state:2,grow:u}; }
  const h=heroAt(t,true), J=skel(h.P,h.root,h.yaw); const cp=carryPoint(J); const qC=new THREE.Quaternion().setFromEuler(new THREE.Euler(0,h.yaw,0));
  const land=V(final.pos.x-0.05,(k-1)*R+Rk.sb.y*0.5,Rk.zS);
  if(t<c.g1){ const u=clamp((t-c.g0)/(c.g1-c.g0));
    if(k===1){ const a=sstep(0.45,1,u); const top=inBag.pos.clone().add(V(0,0.3,0)); const p=inBag.pos.clone().lerp(top,sstep(0.45,0.7,u)).lerp(cp,sstep(0.65,1,u));
      return {pos:a>0?p:inBag.pos,q:inBag.q.clone().slerp(qC,a),size:Rk.sb.clone(),yaw:h.yaw,state:1}; }
    const e=ease(u); const peak=inBag.pos.clone().lerp(cp,0.5).add(V(0,0.55+0.1*k,0));                  // floats up out of the bag to his hands
    const p=inBag.pos.clone().multiplyScalar((1-e)*(1-e)).addScaledVector(peak,2*e*(1-e)).addScaledVector(cp,e*e);
    return {pos:p,q:inBag.q.clone().slerp(qC,e),size:Rk.sb.clone(),yaw:h.yaw,state:1,float:Math.sin(Math.PI*u)}; }
  if(t<c.p0) return {pos:cp,q:qC,size:Rk.sb.clone(),yaw:h.yaw,state:1};
  const u=ease(clamp((t-c.p0)/(c.p1-c.p0))); const p=cp.clone().lerp(land,u); p.y+=0.08*Math.sin(Math.PI*u);
  return {pos:p,q:qC.clone().slerp(final.q,u),size:Rk.sb.clone(),yaw:h.yaw,state:1}; }
function spinAt(i,t){ const f=FOCUS[i]; return 0.9*ease(clamp((t-(f-0.25))/0.45)); }
function focusGlow(i,t){ const f=FOCUS[i]; return t<f-0.2?0:(t<f+0.15?sstep(f-0.2,f,t)*(1+0.8*Math.exp(-Math.pow((t-f)/0.12,2))):1+0.8*Math.exp(-Math.pow((t-f)/0.12,2))); }

// ---------------------------------------------------------------- crowd motion
function crowdAt(m,t,heroHead,heroRoot){
  const dt=0.12*m.i, T0=9.75+dt, T1=10.2+dt, T2=11.75+dt;            // turn, walk back toward the stair, stop
  const x1=m.x0+DC(DUR), A=V(x1,0,m.z), Bt=V(m.tx,0,m.tz), back=yawTo(A,Bt);
  let root, yaw=0, P;
  if(t<T0){ const d=DC(t), a=vCrowd(t)/V_CROWD; root=V(m.x0+d,0,m.z); P=gait({...POSES.stand,p:0.06,tilt:-0.02},d/1.3*2*Math.PI+m.ph,a,0.36,0.6,0.32); }
  else if(t<T1){ const u=sstep(T0,T1,t); root=A.clone(); yaw=back*u; P=gait({...POSES.stand,p:0.05},u*Math.PI*2,Math.sin(Math.PI*u)*0.7,0.22,0.45,0.1); }
  else { const u=clamp((t-T1)/(T2-T1)), e=ease(u); root=A.clone().lerp(Bt,e); const dist=A.distanceTo(Bt)*e; const a=Math.sin(Math.PI*u)*1.0;
    const face=yawTo(root,heroRoot); const wf=sstep(0.75,1,u); yaw=lerp(back,face+((back-face)>Math.PI?2*Math.PI:((face-back)>Math.PI?-2*Math.PI:0)),wf);
    P=gait({...POSES.stand,p:0.06},dist/1.2*2*Math.PI+m.ph,Math.min(1,a*1.3),0.34,0.55,0.28); }
  // glance back at him as they walk on (8.4-9.2 s), then watch him climb
  const gl=[[8.4,9.05],[8.5,9.2],[8.62,9.3]][m.i]; const g=sstep(gl[0],gl[0]+0.22,t)*(1-sstep(gl[1]-0.22,gl[1],t));
  const neck=root.clone().add(V(0,1.45,0)); const lookY=yawTo(root,heroHead);
  let rel=((lookY-yaw+Math.PI*3)%(Math.PI*2))-Math.PI; rel=clamp(rel,-1.6,1.6);
  const watch=sstep(T2-0.3,T2+0.4,t); const hy=lerp(0,rel,Math.max(g*0.95,watch));
  const up=Math.atan2(heroHead.y-neck.y,Math.hypot(heroHead.x-root.x,heroHead.z-root.z));
  P={...P,hy,tilt:lerp(P.tilt,-clamp(up,0,1.0)*0.9,watch)};
  return {P,root,yaw}; }

// ---------------------------------------------------------------- dust puffs (footsteps, the thud, every rock set down)
for(const ts of STEP_H){ if(ts>2.4) continue; const d=DH(ts); PUFFS.push({t0:ts,p:V(HX0+d+0.12,0.03,(PUFFS.length%2?0.07:-0.07)),size:0.32,n:4,spread:0.18}); }
PUFFS.push({t0:TL.thud,p:BAG_G.clone().add(V(0,0.04,0)),size:0.75,n:22,spread:0.7});
CY.forEach((c,i)=>{ const k=i+1; PUFFS.push({t0:c.p1+0.02,p:V(SX+k*T,(k-1)*R+0.03,0),size:0.5,n:9,spread:0.55}); });
function drawPuffs(t){ let n=0; const Rn=rng(5150);
  for(const e of PUFFS){ const a=t-e.t0; for(let j=0;j<e.n;j++){ const ang=Rn()*6.283, sp=0.4+Rn()*0.8, rise=0.2+Rn()*0.5, sz=0.6+Rn()*0.8;
      if(a<0||a>1.6||n>=puffPool.length) continue; const s=puffPool[n++]; const u=1-Math.exp(-a*3.2);
      s.visible=true; s.position.copy(e.p).add(V(Math.cos(ang)*e.spread*sp*u+0.12*a,rise*u*e.size,Math.sin(ang)*e.spread*sp*u));
      const sc=e.size*sz*(0.35+0.9*u); s.scale.set(sc,sc,1); s.material.opacity=0.42*Math.min(1,a*12)*Math.pow(1-a/1.6,1.6); } }
  for(let i=n;i<puffPool.length;i++) puffPool[i].visible=false; }

// ---------------------------------------------------------------- camera
const CUTS=TL.cuts.concat([1e9]); const shotOf=t=>{ let i=0; while(t>=CUTS[i+1]) i++; return i; };
const heroX=t=>t<2.4?HX0+DH(t):HX;
function camShot(i,t){
  switch(i){
    case 0:{ const hx=heroX(Math.min(t,TL.flash)); const r=sstep(2.05,2.7,t); const p=V(hx-2.5-0.35*r,0.45+0.1*r,3.3+0.35*r), l=V(hx+1.0-0.6*r,1.05+0.1*r,-0.6); p.lerp(l,0.08*sstep(2.7,4.0,t)); return {p,l,fov:40}; }   // walk, then reveal (eases left so the whole bag is in frame)   // walk, then reveal
    case 1:{ const u=clamp((t-4)/3); const c=bagAt(4.0).p; const th=lerp(Math.PI-1.05,Math.PI+0.28,ease(u)); const r=lerp(2.9,2.5,u);                          // inventory orbit
      return {p:V(c.x+r*Math.cos(th),c.y+0.3-0.15*u,c.z+r*Math.sin(th)),l:c.clone(),fov:38}; }
    case 2:{ const u=clamp((t-7)/1.45); return {p:V(HX+3.4-0.3*u,0.28,0.55),l:V(HX,1.0-0.12*sstep(7.7,8.3,t),-0.3),fov:40}; }                                  // front low
    case 3:{ return {p:V(HX-3.6,0.45,1.6),l:V(HX+3.0,0.75,-1.2),fov:44}; }                                                                                     // reverse low
    case 4:{ return {p:V(0.1,0.95,4.4),l:V(-0.15,0.75,-0.3),fov:42}; }                                                                                            // side
    case 5:{ const c=V(SX+1.0*T,0.55,-0.35); return {p:c.clone().add(V(-0.9,3.5,2.5)),l:c,fov:42}; }                                              // top
    case 6:{ return {p:V(SX+2.0*T,1.45,4.4),l:V(SX+1.9*T,1.15,-0.3),fov:42}; }                                                                                   // side
    case 7:{ const c=V(SX+2.1*T,1.1,-0.35); return {p:c.clone().add(V(-1.2,4.3,3.2)),l:c,fov:42}; }                                               // top
    case 8:{ const u=1-Math.pow(1-clamp((t-12.0)/0.85),3); const a={p:V(SX+3.2*T,1.9,4.0),l:V(SX+3.0*T,1.5,0)}, b={p:V(12.5,1.5,10.5),l:V(3.2,1.7,-1.4)};   // rise: fast pull-back
      const p=a.p.clone().lerp(b.p,u), l=a.l.clone().lerp(b.l,u); const d=sstep(12.85,15.0,t); p.add(V(0.3*d,0.45*d,0.3*d)); l.add(V(0,0.5*d,0)); return {p,l,fov:lerp(42,52,u)}; }
    default:{ const u=ease(clamp((t-15.0)/(TL.hold-15.0))); return {p:V(8.9,0.28,6.9).lerp(V(8.6,0.32,6.65),u),l:V(2.45,2.55,-0.7),fov:lerp(62,60,u)}; }                 // hero shot
  } }
const SHAKES=[[TL.thud,0.35]].concat(CY.map(c=>[c.p1,0.2]));
function shakeAt(t){ let s=0; for(const [te,a] of SHAKES){ const d=t-te; if(d>=0&&d<0.4) s+=a*Math.exp(-d/0.11); } return s; }

// ---------------------------------------------------------------- post
const composer=new EffectComposer(renderer); composer.setSize(W,H);
composer.addPass(new RenderPass(scene,cam));
const bloom=new UnrealBloomPass(new THREE.Vector2(W,H),0.5,0.55,0.8); composer.addPass(bloom);
const gradeU={tDiffuse:{value:null},uT:{value:0},uFlash:{value:0},uAsp:{value:W/H},uX:{value:0},uH:{value:H}};
const gradePass=new ShaderPass({uniforms:gradeU,vertexShader:`varying vec2 vU; void main(){ vU=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
 fragmentShader:`varying vec2 vU; uniform sampler2D tDiffuse; uniform float uT,uFlash,uAsp,uX,uH;
  float h(vec2 p){ return fract(sin(dot(p,vec2(12.9898,78.233))+uT*37.0)*43758.5453); }
  void main(){ vec2 c=vU-0.5; float r2=dot(c*vec2(uAsp,1.0),c*vec2(uAsp,1.0)); vec2 off=c*0.0016*(1.0+r2*4.0);
   vec3 col=vec3(texture2D(tDiffuse,vU+off).r,texture2D(tDiffuse,vU).g,texture2D(tDiffuse,vU-off).b);
   col=vec3(1.0)-exp(-1.25*col);
   float l=dot(col,vec3(0.299,0.587,0.114)); col=mix(col*vec3(0.86,1.0,1.08),col*vec3(1.06,1.0,0.9),smoothstep(0.15,0.7,l));
   vec3 xr=vec3(0.45,0.9,1.0)*pow(smoothstep(0.04,0.75,l),0.7)*1.35+vec3(0.0,0.025,0.045); xr*=0.92+0.08*sin(vU.y*uH*1.6); col=mix(col,xr,uX);   // x-ray cut
   float vig=1.0-smoothstep(0.12,0.5,r2)*0.7; col*=vig; col+=(h(vU*vec2(uAsp,1.0)*900.0)-0.5)*0.028; col+=uFlash*vec3(1.0,0.97,0.92);
   gl_FragColor=vec4(max(col,0.0),1.0);} `});
composer.addPass(gradePass); const GU=gradePass.uniforms;   // ShaderPass clones its uniforms: always write to GU
composer.addPass(new OutputPass());

// ---------------------------------------------------------------- one sub-frame
const _M=new THREE.Matrix4();
function setT(t){
  const h=heroAt(t); const Jh=skel(h.P,h.root,h.yaw); poseFig(hero,Jh);
  for(const m of CROWD){ const c=crowdAt(m,t,Jh.head,h.root); const Jc=skel(c.P,c.root,c.yaw); poseFig(m.f,Jc); m.J=Jc; }
  // backpack
  const vis=sstep(TL.flash,TL.flash+0.05,t); const X=t<TL.flash?0:1-sstep(TL.flash+0.45,TL.flash+0.95,t);   // x-ray look holds ~0.5 s, then dissolves to colour
  const B=bagAt(t); _M.compose(B.p,B.q,V(1,B.sy,1)); bag.matrix.copy(_M); bag.matrixWorldNeedsUpdate=true; bag.visible=vis>0.001;
  const fill=1-removedAt(t)/NR; bagU.uVis.value=vis; bagU.uX.value=X; bagU.uFill.value=fill;
  bagGlow.position.copy(B.p); bagGlow.material.opacity=vis*(0.2+0.1*X)*(0.3+0.7*fill); bagGlow.scale.setScalar(1.5);
  bagLight.position.copy(B.p); bagLight.intensity=vis*2.2*(0.15+0.85*fill);
  // rocks
  for(let i=0;i<NR;i++){ const Rk=ROCKS[i], r=rockAt(i,t); const show=vis>0.001;
    _M.compose(r.pos,r.q,r.size); Rk.m.matrix.copy(_M); Rk.m.matrixWorld.copy(_M); Rk.m.visible=show;
    const placed=r.state===2; const pulse=placed?Math.exp(-Math.max(0,t-CY[i].p1)/0.35):0;
    let e=placed?0.55+1.6*pulse+0.15*sstep(15.0,15.8,t):(0.75+0.6*focusGlow(i,t)*sstep(4.0,4.2,t)+(r.float||0)*0.8);
    e*=(1+0.3*X);
    Rk.mat.emissiveIntensity=e; Rk.gl.position.copy(r.pos); Rk.gl.material.opacity=show?(placed?0.18+0.4*pulse:0.22+0.25*focusGlow(i,t)*sstep(4,4.2,t))*Math.min(1,e):0;
    Rk.gl.scale.setScalar(placed?1.3:0.6); Rk.pl.position.copy(r.pos).add(V(0.15,0.05,placed?0.75:0)); Rk.pl.intensity=show?(placed?0.35+1.0*pulse:0.0):0; }
  // lamp on the top step
  const lk=sstep(TL.chord-0.05,TL.chord+0.5,t); lamp.position.set(SX+7.75*T,TOPY+0.0,0.24); lamp.visible=t>=TL.chord-0.3;
  const flick=0.92+0.08*Math.sin(t*17.0)*Math.sin(t*5.3); lampFlame.material.opacity=lk; lampFlame.scale.setScalar(0.4+0.6*lk);
  lampGlow.position.copy(lamp.position).add(V(0,0.13,0)); lampGlow.material.opacity=0.5*lk*flick; lampGlow.scale.setScalar(0.6);
  lampLight.position.copy(lampGlow.position); lampLight.intensity=1.5*lk*flick;
  // camera
  const s=shotOf(t); const c=camShot(s,t); cam.up.copy(c.up||UPV); cam.position.copy(c.p); cam.lookAt(c.l); cam.fov=c.fov; cam.updateProjectionMatrix();
  const sh=shakeAt(t); if(sh>0){ cam.rotateX(0.035*sh*Math.sin(t*131.0)); cam.rotateY(0.035*sh*Math.sin(t*97.0+1.3)); }
  // light rigs follow the action
  const focus=s<=3?V(HX,0.8,0):V(SX+3*T,1.5,0); key.position.copy(focus).add(V(-5,11,8)); key.target.position.copy(focus); key.target.updateMatrixWorld();
  rim.position.copy(focus).add(SUN_DIR.clone().multiplyScalar(20)).add(V(0,3,0)); rim.target.position.copy(focus); rim.target.updateMatrixWorld();
  rim.intensity=0.5+0.35*sstep(14.5,15.5,t);
  moteU.camPos.value.copy(cam.position); moteU.t.value=t; moteU.wx.value=tab(WX_TAB,t); moteU.box.value=s>=8?16:9; moteU.op.value=1;
  drawPuffs(t);
  GU.uT.value=t; GU.uX.value=X*0.92; const df=t-TL.flash; GU.uFlash.value=(df>=0&&df<0.18)?0.16*(1-df/0.18):0;
  bloom.strength=0.5+0.1*X;
  return {Jh,B}; }
const acc=document.createElement('canvas'); acc.width=W; acc.height=H; const actx=acc.getContext('2d');
window.renderAt=function(t,Ksub=3){
  const s=shotOf(t), t0=CUTS[s], t1=CUTS[s+1]-1e-4;          // never blur across a cut
  actx.globalAlpha=1; actx.clearRect(0,0,W,H); const shutter=1/60;
  for(let k=0;k<Ksub;k++){ const tt=clamp(t+(Ksub>1?(k/(Ksub-1)-0.5)*shutter:0),Math.max(0,t0),Math.min(DUR,t1)); setT(tt); composer.render(); actx.globalAlpha=1/(k+1); actx.drawImage(renderer.domElement,0,0); }
  return acc.toDataURL('image/jpeg',0.95); };
// screen positions and numbers for the overlay and the sound
const proj=v=>{ const p=v.clone().project(cam); return [p.x*0.5+0.5,0.5-p.y*0.5,p.z<1?1:0]; };
const counterAt=t=>{ let n=0; for(const c of CY) if(t>=c.p1) n++; return n; };
window.metaAt=function(t){ const S=setT(t); cam.updateMatrixWorld();
  return {t,shot:shotOf(t),counter:counterAt(t),rocks:ROCKS.map((_,i)=>proj(rockAt(i,t).pos)),hero:proj(S.Jh.head),bag:proj(S.B.p),top:proj(V(TOPX,TOPY+2.2,0)),crowd:CROWD.map(m=>proj(m.J.head))}; };
window.events={flash:TL.flash,focus:FOCUS,thud:TL.thud,cycles:CY,steps:STEP_H,chord:TL.chord,cuts:TL.cuts,hit:CY[4].s1};
window.ready=true;
