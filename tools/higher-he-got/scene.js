// The Higher He Got: two stickmen share a bench under a street lamp. Every coin that lands under him lifts him higher
// and turns him a little more to gold, until he reaches down and cannot touch her hand. renderAt(t) is pure (no state
// carried between frames), so frames can be rendered in any order by parallel workers.
import * as THREE from 'three';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {UnrealBloomPass} from 'three/addons/postprocessing/UnrealBloomPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';
import {ShaderPass} from 'three/addons/postprocessing/ShaderPass.js';

const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960;
const TL=await (await fetch('timeline.json')).json();
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true}); renderer.setPixelRatio(1); renderer.setSize(W,H);
renderer.shadowMap.enabled=true; renderer.shadowMap.type=THREE.PCFSoftShadowMap; document.body.appendChild(renderer.domElement);
const scene=new THREE.Scene(); scene.fog=new THREE.FogExp2(0x070d19,0.0055);
const cam=new THREE.PerspectiveCamera(40,W/H,0.05,2000);

const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x)); const sstep=(a,b,x)=>{const t=clamp((x-a)/(b-a));return t*t*(3-2*t)}; const lerp=(a,b,t)=>a+(b-a)*t;
const V=(x,y,z)=>new THREE.Vector3(x,y,z);
function rng(seed){ let s=seed>>>0; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; }

// ---------------------------------------------------------------- the money curve (compounding: height grows exponentially)
const TH=TL.coin_th, K=TL.growth_k, H0=TL.h0, [RE0,RE1]=TL.rise_ease;
function sClock(t){ if(t<=RE0) return t; if(t>=RE1) return RE0+0.5*(RE1-RE0); const u=(t-RE0)/(RE1-RE0); return RE0+0.5*(RE1-RE0)*(2*u-u*u); }
const hSmooth=t=>H0*Math.exp(K*sClock(t));
const HF=hSmooth(99); const NC=Math.floor(HF/TH+1e-6);
const LAND=[]; for(let i=0;i<NC;i++){ const target=(i+1)*TH; let a=-1,b=20; for(let it=0;it<50;it++){ const m=(a+b)/2; if(hSmooth(m)>=target) b=m; else a=m; } LAND.push(b); }
const FLYI=LAND.map(t=>lerp(0.6,0.28,clamp(t/10)));    // seconds a coin spends spiralling in (shorter once they pour in)
function landed(t){ let lo=0,hi=NC; while(lo<hi){ const m=(lo+hi)>>1; if(LAND[m]<=t) lo=m+1; else hi=m; } return lo; }
function seatH(t){ const n=landed(t); if(n===0) return 0; const e=sstep(0,0.08,t-LAND[n-1]); return TH*(n-1+e); }
const worthAt=t=>{ const w=TL.worth_final*clamp((hSmooth(t)-H0)/(HF-H0)); return Math.round(w/1000)*1000; };

// ---------------------------------------------------------------- stage constants
const SB=0.47;                                        // bench seat height
const XHER=-0.32, XHIM=0.32, COIN_R=0.2;
const L_T=0.5, L_UP=0.3, L_FORE=0.28, L_TH=0.45, L_SH=0.44, HEAD_R=0.12, BR=0.032;
const LAMP=V(-0.85,3.3,-0.45);

// ---------------------------------------------------------------- environment map for the metals (warm top, navy below)
function makeEnv(){
  const s=new THREE.Scene();
  const m=new THREE.ShaderMaterial({side:THREE.BackSide,uniforms:{},vertexShader:`varying vec3 vD; void main(){ vD=normalize(position); gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
    fragmentShader:`varying vec3 vD; void main(){ float y=vD.y; vec3 c=mix(vec3(0.02,0.035,0.07),vec3(0.10,0.12,0.18),smoothstep(-0.4,0.1,y));
      c+=vec3(1.6,1.15,0.6)*pow(max(y,0.0),3.0)*1.4; c+=vec3(1.4,0.9,0.45)*exp(-pow((y-0.05)*9.0,2.0))*smoothstep(0.2,0.9,vD.x*0.5+0.5)*0.9;
      c+=vec3(0.25,0.55,0.6)*exp(-pow((y+0.05)*7.0,2.0))*smoothstep(0.3,1.0,-vD.x*0.5+0.5)*0.5; gl_FragColor=vec4(c,1.0);} `});
  s.add(new THREE.Mesh(new THREE.SphereGeometry(10,32,16),m));
  const pm=new THREE.PMREMGenerator(renderer); const rt=pm.fromScene(s,0.02); pm.dispose(); return rt.texture;
}
const ENV=makeEnv();

// ---------------------------------------------------------------- sky, stars, city, park
const skyU={uGold:{value:0},uCamY:{value:0}};
const sky=new THREE.Mesh(new THREE.SphereGeometry(1500,48,24),new THREE.ShaderMaterial({side:THREE.BackSide,depthWrite:false,fog:false,uniforms:skyU,
  vertexShader:`varying vec3 vD; void main(){ vD=normalize(position); gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
  fragmentShader:`varying vec3 vD; uniform float uGold,uCamY; void main(){ float y=vD.y;
    vec3 c=mix(vec3(0.02,0.032,0.062),vec3(0.004,0.007,0.016),smoothstep(-0.02,0.5,y));
    c+=vec3(0.35,0.22,0.12)*exp(-pow(y*14.0,2.0))*0.18;                                  // city glow on the horizon
    float g=max(dot(vD,normalize(vec3(0.05,1.0,-0.25))),0.0);
    c+=uGold*(vec3(1.0,0.72,0.32)*pow(g,7.0)*0.9+vec3(0.55,0.36,0.16)*pow(g,2.2)*0.28);   // the light he climbs toward
    gl_FragColor=vec4(c,1.0);} `}));
scene.add(sky);
{ const R=rng(7); const n=2600, p=new Float32Array(n*3), a=new Float32Array(n);
  for(let i=0;i<n;i++){ let x,y,z; do{ x=R()*2-1; y=R(); z=R()*2-1; }while(x*x+y*y+z*z>1||y<0.06); const l=Math.hypot(x,y,z); p.set([x/l*1300,y/l*1300,z/l*1300],i*3); a[i]=Math.pow(R(),3); }
  const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.BufferAttribute(p,3)); g.setAttribute('aB',new THREE.BufferAttribute(a,1));
  const st=new THREE.Points(g,new THREE.ShaderMaterial({transparent:true,depthWrite:false,fog:false,blending:THREE.AdditiveBlending,uniforms:{uS:{value:H/1920}},
    vertexShader:`attribute float aB; varying float vB; uniform float uS; void main(){ vB=aB; gl_PointSize=(1.4+aB*2.6)*uS*1.6; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
    fragmentShader:`varying float vB; void main(){ float r=length(gl_PointCoord-0.5)*2.0; float a=smoothstep(1.0,0.0,r); gl_FragColor=vec4(vec3(0.85,0.9,1.0)*a*(0.25+0.9*vB),1.0);} `}));
  st.frustumCulled=false; scene.add(st); }
// distant city: dark blocks with lit windows (fogged by hand in the point shader)
{ const R=rng(21); const bMat=new THREE.MeshStandardMaterial({color:0x0c1424,roughness:0.92,metalness:0});
  const box=new THREE.BoxGeometry(1,1,1); const N=260; const im=new THREE.InstancedMesh(box,bMat,N); const m=new THREE.Matrix4();
  const wp=[], wc=[]; const warm=[1.0,0.78,0.48], teal=[0.5,0.85,0.82];
  for(let i=0;i<N;i++){ const x=(R()*2-1)*160, z=-55-R()*170, w=5+R()*11, d=5+R()*10; let h=3.5+Math.pow(R(),1.8)*10; if(R()<0.07) h+=9+R()*8;
    m.compose(V(x,h/2,z),new THREE.Quaternion(),V(w,h,d)); im.setMatrixAt(i,m);
    for(let yy=2.2;yy<h-1.2;yy+=2.3) for(let xx=-w/2+1.0;xx<w/2-0.6;xx+=1.55){ if(R()<0.27){ wp.push(x+xx,yy,z+d/2+0.05); wc.push(...(R()<0.78?warm:teal), 0.5+R()*0.5); } } }
  scene.add(im);
  const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(wp,3)); g.setAttribute('aC',new THREE.Float32BufferAttribute(wc,4));
  const pts=new THREE.Points(g,new THREE.ShaderMaterial({transparent:true,depthWrite:false,fog:false,blending:THREE.AdditiveBlending,uniforms:{uK:{value:H/2/Math.tan(20*Math.PI/180)}},
    vertexShader:`attribute vec4 aC; varying vec4 vC; uniform float uK; void main(){ vec4 mv=modelViewMatrix*vec4(position,1.0); float d=-mv.z; float f=exp(-pow(0.0055*d,2.0));
      vC=vec4(aC.rgb,aC.a*(0.25+0.75*f)); gl_PointSize=clamp(uK*0.55/d,1.2,7.0); gl_Position=projectionMatrix*mv; }`,
    fragmentShader:`varying vec4 vC; void main(){ vec2 c=abs(gl_PointCoord-0.5)*2.0; float a=(1.0-smoothstep(0.55,1.0,max(c.x,c.y*0.8))); gl_FragColor=vec4(vC.rgb*a*vC.a*0.85,1.0);} `}));
  pts.frustumCulled=false; scene.add(pts); }
const ground=new THREE.Mesh(new THREE.PlaneGeometry(600,600),new THREE.MeshStandardMaterial({color:0x0b111c,roughness:0.96,metalness:0}));
ground.rotation.x=-Math.PI/2; ground.receiveShadow=true; scene.add(ground);
const path=new THREE.Mesh(new THREE.PlaneGeometry(60,1.6),new THREE.MeshStandardMaterial({color:0x1d2534,roughness:0.9}));
path.rotation.x=-Math.PI/2; path.position.set(0,0.004,1.55); path.receiveShadow=true; scene.add(path);
// bushes behind the bench for depth
{ const R=rng(5); const bm=new THREE.MeshStandardMaterial({color:0x0b1a1c,roughness:1}); const sg=new THREE.SphereGeometry(1,18,12);
  for(let i=0;i<14;i++){ const b=new THREE.Mesh(sg,bm); const s=0.5+R()*0.7; b.scale.set(s*1.3,s,s); b.position.set((R()*2-1)*6,s*0.55,-2.6-R()*3.5); b.receiveShadow=true; scene.add(b); } }
// bench
const wood=new THREE.MeshStandardMaterial({color:0x4a3628,roughness:0.75}); const iron=new THREE.MeshStandardMaterial({color:0x1b1f27,roughness:0.5,metalness:0.6});
const bench=new THREE.Group(); scene.add(bench);
for(const [w,h,d,x,y,z,m] of [[1.7,0.05,0.14,0,SB-0.025,0.14,wood],[1.7,0.05,0.14,0,SB-0.025,-0.02,wood],[1.7,0.05,0.12,0,SB-0.025,-0.17,wood],
  [1.7,0.1,0.04,0,0.78,-0.27,wood],[1.7,0.1,0.04,0,0.93,-0.28,wood],
  [0.05,SB,0.05,-0.75,SB/2,0.15,iron],[0.05,SB,0.05,0.75,SB/2,0.15,iron],[0.05,0.98,0.05,-0.75,0.49,-0.25,iron],[0.05,0.98,0.05,0.75,0.49,-0.25,iron]]){
  const b=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m); b.position.set(x,y,z); b.castShadow=b.receiveShadow=true; bench.add(b); }
// street lamp
{ const pole=new THREE.Mesh(new THREE.CylinderGeometry(0.045,0.06,3.45,16),iron); pole.position.set(-1.25,1.725,-0.45); pole.castShadow=true; scene.add(pole);
  const arm=new THREE.Mesh(new THREE.CylinderGeometry(0.025,0.025,0.46,8),iron); arm.rotation.z=Math.PI/2; arm.position.set(-1.03,3.42,-0.45); scene.add(arm);
  const hood=new THREE.Mesh(new THREE.ConeGeometry(0.16,0.14,24,1,true),iron); hood.position.set(LAMP.x,LAMP.y+0.06,LAMP.z); scene.add(hood); }
const bulb=new THREE.Mesh(new THREE.SphereGeometry(0.045,16,12),new THREE.MeshBasicMaterial({color:0xfff1d6})); bulb.position.copy(LAMP); scene.add(bulb);
function glowTex(){ const c=document.createElement('canvas'); c.width=c.height=128; const g=c.getContext('2d'); const r=g.createRadialGradient(64,64,0,64,64,64);
  r.addColorStop(0,'rgba(255,255,255,1)'); r.addColorStop(0.18,'rgba(255,255,255,0.55)'); r.addColorStop(0.5,'rgba(255,255,255,0.12)'); r.addColorStop(1,'rgba(255,255,255,0)'); g.fillStyle=r; g.fillRect(0,0,128,128);
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; return t; }
const GLOW=glowTex();
const glow=(col,s,op)=>{ const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:GLOW,color:col,transparent:true,opacity:op,depthWrite:false,blending:THREE.AdditiveBlending,fog:false})); sp.scale.set(s,s,1); scene.add(sp); return sp; };
const lampGlow=glow(0xffd7a0,0.9,0.75); lampGlow.position.copy(LAMP);
for(const [x,z] of [[-9,-15],[8,-22],[-22,-30],[19,-12]]){ const g=glow(0xffc98a,1.4,0.5); g.position.set(x,3.3,z); const p=new THREE.PointLight(0xffc98a,6,9,2); p.position.set(x,3.2,z); scene.add(p); }

// lights
const spot=new THREE.SpotLight(0xffc787,46,0,0.66,0.75,2); spot.position.copy(LAMP); spot.target.position.set(0.0,0.45,0.25); spot.castShadow=true;
spot.shadow.mapSize.set(1024,1024); spot.shadow.bias=-0.0004; spot.shadow.camera.near=0.5; spot.shadow.camera.far=12; scene.add(spot,spot.target);
scene.add(new THREE.HemisphereLight(0x22365e,0x0a0c10,0.55));
const moonL=new THREE.DirectionalLight(0x6f8fc8,0.35); moonL.position.set(-20,30,25); scene.add(moonL);
const goldL=new THREE.DirectionalLight(0xffd393,0); goldL.position.set(3,40,10); scene.add(goldL,goldL.target);
const himL=new THREE.PointLight(0xffd8a0,0,7,2); scene.add(himL);

// clouds (soft sprites) he rises through
function cloudTex(){ const c=document.createElement('canvas'); c.width=c.height=256; const g=c.getContext('2d'); const R=rng(99);
  for(let i=0;i<70;i++){ const x=60+R()*136, y=90+R()*76, r=18+R()*46; const gr=g.createRadialGradient(x,y,0,x,y,r); gr.addColorStop(0,'rgba(255,255,255,0.16)'); gr.addColorStop(1,'rgba(255,255,255,0)'); g.fillStyle=gr; g.fillRect(0,0,256,256); }
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; return t; }
const CLOUD=cloudTex(); const clouds=[];
{ const R=rng(31); for(let i=0;i<34;i++){ const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:CLOUD,color:0x323c56,transparent:true,opacity:0.0,depthWrite:false,fog:true}));
  const front=i%5===0; const x=front?(R()<0.5?-1:1)*(4+R()*8):(R()*2-1)*28, z=front?2+R()*6:-6-R()*34, y=8+R()*8; const s=7+R()*12; sp.scale.set(s*1.8,s,1); sp.position.set(x,y,z);
  sp.userData.base=0.35+R()*0.4; scene.add(sp); clouds.push(sp); } }

// ---------------------------------------------------------------- coins: the column under him and the stream that feeds it
function coinTextures(){
  const f=document.createElement('canvas'); f.width=f.height=256; const g=f.getContext('2d'); g.fillStyle='#808080'; g.fillRect(0,0,256,256);
  g.strokeStyle='#d8d8d8'; g.lineWidth=10; g.beginPath(); g.arc(128,128,112,0,7); g.stroke(); g.strokeStyle='#5a5a5a'; g.lineWidth=5; g.beginPath(); g.arc(128,128,96,0,7); g.stroke();
  g.fillStyle='#b8b8b8'; g.beginPath(); for(let i=0;i<10;i++){ const a=i*Math.PI/5-Math.PI/2, r=i%2?26:60; g.lineTo(128+Math.cos(a)*r,128+Math.sin(a)*r); } g.closePath(); g.fill();
  const s=document.createElement('canvas'); s.width=512; s.height=8; const h=s.getContext('2d'); for(let x=0;x<512;x+=4){ h.fillStyle=(x/4)%2?'#404040':'#c0c0c0'; h.fillRect(x,0,4,8); }
  const ft=new THREE.CanvasTexture(f), stx=new THREE.CanvasTexture(s); stx.wrapS=THREE.RepeatWrapping; return [ft,stx]; }
const [FACE_T,SIDE_T]=coinTextures();
const coinFace=new THREE.MeshStandardMaterial({color:0xe9b553,metalness:1,roughness:0.3,envMap:ENV,envMapIntensity:1.0,bumpMap:FACE_T,bumpScale:2.0});
const coinSide=new THREE.MeshStandardMaterial({color:0xd9a443,metalness:1,roughness:0.36,envMap:ENV,envMapIntensity:1.0,bumpMap:SIDE_T,bumpScale:1.5});
const coinGeo=new THREE.CylinderGeometry(COIN_R,COIN_R,TH*0.96,48,1);
const coins=new THREE.InstancedMesh(coinGeo,[coinSide,coinFace,coinFace],NC); coins.castShadow=true; coins.receiveShadow=true; coins.frustumCulled=false; scene.add(coins);
const CJ=[]; { const R=rng(77); for(let i=0;i<NC;i++) CJ.push({dx:(R()-0.5)*0.03,dz:(R()-0.5)*0.03,rx:(R()-0.5)*0.035,rz:(R()-0.5)*0.035,ry:R()*6.28,a0:Math.PI*(1.05+R()*0.9),sp:(R()<0.5?-1:1)*(3+R()*5),r0:0.8+R()*0.6,ax:R()*6.28}); }
const _m=new THREE.Matrix4(), _q=new THREE.Quaternion(), _p=new THREE.Vector3(), _s=new THREE.Vector3(), _e=new THREE.Euler(), ZERO=new THREE.Vector3(0,0,0);
function poseCoins(t){
  for(let i=0;i<NC;i++){ const j=CJ[i], tl=LAND[i], FLY=FLYI[i]; const slotY=SB+(i+0.5)*TH;
    if(t<tl-FLY){ _m.compose(_p.set(0,-50,0),_q.identity(),ZERO); coins.setMatrixAt(i,_m); continue; }
    if(t>=tl){ _q.setFromEuler(_e.set(j.rx,j.ry,j.rz)); _m.compose(_p.set(XHIM+j.dx,slotY,j.dz),_q,_s.set(1,1,1)); coins.setMatrixAt(i,_m); continue; }
    const u=(t-(tl-FLY))/FLY, w=1-u;                    // spiral in from the light above, flipping, and settle flat
    const r=j.r0*Math.pow(w,1.2), a=j.a0+j.sp*w*0.25; const y=slotY+1.6*w*w+0.3*w;
    _q.setFromEuler(_e.set(j.rx+Math.sin(j.ax)*w*7.0,j.ry+w*4,j.rz+Math.cos(j.ax)*w*7.0)); const sc=sstep(0,0.25,u);
    _m.compose(_p.set(XHIM+Math.cos(a)*r,y,Math.sin(a)*r),_q,_s.set(sc,sc,sc)); coins.setMatrixAt(i,_m); }
  coins.instanceMatrix.needsUpdate=true;
}

// ---------------------------------------------------------------- stickman rig (tubes + joints, classic single-point shoulders and hips)
const capGeo=new THREE.CylinderGeometry(1,1,1,16,1,true); const ballGeo=new THREE.SphereGeometry(1,32,20);
const herMat=new THREE.MeshStandardMaterial({color:0xf2ecdc,roughness:0.55,emissive:0x3a362c,emissiveIntensity:0.5});
const himMat=new THREE.MeshStandardMaterial({color:0xf2ecdc,roughness:0.55,metalness:0,emissive:0x3a362c,emissiveIntensity:0.5,envMap:ENV,envMapIntensity:0});
const BONES=[['P','N'],['N','C0'],['Sh','eL'],['eL','wL'],['Sh','eR'],['eR','wR'],['P','kL'],['kL','aL'],['aL','fL'],['P','kR'],['kR','aR'],['aR','fR']];
const JOINTS=['P','N','eL','eR','kL','kR','aL','aR'];
function makeFig(mat,bun){ const f={bones:[],joints:[],mat};
  const mk=(g)=>{ const m=new THREE.Mesh(g,mat); m.matrixAutoUpdate=false; m.frustumCulled=false; m.castShadow=true; scene.add(m); return m; };
  for(const b of BONES) f.bones.push(mk(capGeo)); for(const j of JOINTS) f.joints.push(mk(ballGeo)); f.hands=[mk(ballGeo),mk(ballGeo)]; f.feet=[mk(ballGeo),mk(ballGeo)];
  f.head=mk(ballGeo); f.nose=mk(ballGeo); if(bun) f.bun=mk(ballGeo); return f; }
const her=makeFig(herMat,true), him=makeFig(himMat,false);
const UPV=V(0,1,0);
function setM(mesh,p,q,s){ _m.compose(p,q,s); mesh.matrix.copy(_m); mesh.matrixWorld.copy(_m); }
function bone(mesh,a,b,r){ const d=b.clone().sub(a); const L=Math.max(d.length(),1e-4); _q.setFromUnitVectors(UPV,d.multiplyScalar(1/L)); setM(mesh,a.clone().add(b).multiplyScalar(0.5),_q,_s.set(r,L,r)); }
function ball(mesh,p,r){ setM(mesh,p,_q.identity(),_s.set(r,r,r)); }
function ik(S,T,pole){ const d=T.clone().sub(S); const dist=Math.min(d.length(),L_UP+L_FORE-0.002); const dn=d.normalize();
  const a=(L_UP*L_UP-L_FORE*L_FORE+dist*dist)/(2*dist); const h=Math.sqrt(Math.max(0,L_UP*L_UP-a*a));
  const p=pole.clone().addScaledVector(dn,-pole.dot(dn)).normalize(); return {E:S.clone().addScaledVector(dn,a).addScaledVector(p,h), Wr:S.clone().addScaledVector(dn,dist)}; }
// skeleton from a pose: P hip, lean (forward), roll (+x side), look target, leg mode, arm targets/poles
function skel(o){
  const U=V(Math.sin(o.roll),Math.cos(o.lean)*Math.cos(o.roll),Math.sin(o.lean)).normalize();
  const J={P:o.P.clone()}; J.N=J.P.clone().addScaledVector(U,L_T); J.Sh=J.N.clone().addScaledVector(U,-0.06);
  J.C=J.N.clone().addScaledVector(U,0.19); J.C0=J.N.clone().addScaledVector(U,0.07);
  const f=V(0,0,1), sw=o.swing||0;
  for(const [s,k] of [[-1,'L'],[1,'R']]){
    const kn=J.P.clone().add(V(s*0.1,o.dangle?-0.05:0.0,L_TH*0.99)); let an;
    if(o.dangle){ an=kn.clone().add(V(s*0.01,-L_SH*0.985,0.07+0.05*Math.sin(sw+s*1.3))); } else { an=V(kn.x+s*0.01,BR+0.045,kn.z+0.08); }
    J['k'+k]=kn; J['a'+k]=an; J['f'+k]=an.clone().add(V(s*0.02,o.dangle?-0.03:-0.01,0.12)); }
  const L=ik(J.Sh,o.tL,o.pL), R=ik(J.Sh,o.tR,o.pR); J.eL=L.E; J.wL=L.Wr; J.eR=R.E; J.wR=R.Wr;
  J.dir=o.look.clone().sub(J.C).normalize(); J.U=U; return J; }
function poseFig(F,J){
  BONES.forEach((b,i)=>bone(F.bones[i],J[b[0]],J[b[1]],BR)); JOINTS.forEach((j,i)=>ball(F.joints[i],J[j],BR*1.05));
  ball(F.hands[0],J.wL,BR*1.45); ball(F.hands[1],J.wR,BR*1.45); ball(F.feet[0],J.fL,BR*1.15); ball(F.feet[1],J.fR,BR*1.15);
  ball(F.head,J.C,HEAD_R); ball(F.nose,J.C.clone().addScaledVector(J.dir,HEAD_R*0.93),0.034);
  if(F.bun) ball(F.bun,J.C.clone().addScaledVector(J.dir,-0.1).addScaledVector(J.U,0.055),0.055); }
const handGlow=glow(0xffe2b0,0.32,0.0); const himHalo=glow(0xffc870,1.0,0.0);

// reach: hands hold while both can reach the clasp point; the moment they cannot is the parting time
const REACH=L_UP+L_FORE-0.01;
function leanHim(t){ return {lean:lerp(0.12,-0.07,sstep(6.0,7.6,t))+0.25*sstep(11.25,11.9,t), roll:lerp(-0.1,-0.27,sstep(2.5,5.6,t))*(1-sstep(5.8,7.2,t))-0.12*sstep(11.3,12.0,t)}; }
function leanHer(t,hs){ return {lean:0.08+0.06*Math.sin(t*0.9)*0.2, roll:lerp(0.1,0.24,sstep(2.5,5.6,t))*(1-sstep(6.2,8.0,t))+0.06*sstep(13.3,14.3,t)}; }
function shoulders(t){ const hs=seatH(t);
  const sh=(P,l)=>{ const U=V(Math.sin(l.roll),Math.cos(l.lean)*Math.cos(l.roll),Math.sin(l.lean)).normalize(); return P.clone().addScaledVector(U,L_T-0.06); };
  return {hs, Ph:V(XHIM,SB+hs+BR+0.004,0.0), Pf:V(XHER,SB+BR+0.004,0.0), get Sm(){ return sh(this.Ph,leanHim(t)); }, get Sf(){ return sh(this.Pf,leanHer(t,hs)); }}; }
let TPART=TL.part; { for(let t=0;t<11;t+=1/240){ const s=shoulders(t); if(s.Sm.distanceTo(s.Sf)>2*REACH*0.985){ TPART=t; break; } } }
function clasp(s){ const mid=s.Sm.clone().add(s.Sf).multiplyScalar(0.5); const d=s.Sm.distanceTo(s.Sf); return mid.add(V(0,-0.24*(1-clamp(d/(2*REACH))),0.13)); }

function poseAll(t){
  const s=shoulders(t), hs=s.hs; const lh=leanHim(t), lf=leanHer(t,hs);
  const kneeHim=s.Ph.clone().add(V(-0.1,-0.02,0.43)), kneeHimR=s.Ph.clone().add(V(0.1,-0.02,0.43)), kneeHer=s.Pf.clone().add(V(-0.1,0.02,0.43)), kneeHerR=s.Pf.clone().add(V(0.1,0.02,0.43));
  const holding=t<TPART; const cl=clasp(s); const clPart=clasp(shoulders(TPART));
  // his left (inner) hand: clasp -> drifts back to his knee after parting -> reaches straight down to her
  let tL; if(holding) tL=cl; else { const back=sstep(TPART+0.25,TPART+1.2,t); tL=clPart.clone().lerp(kneeHim.clone().add(V(0.03,0.05,0.02)),back); }
  const herHead=s.Pf.clone().add(V(0,L_T+0.19,0.05));
  const dn=sstep(11.35,11.95,t); if(dn>0){ const down=s.Sm.clone().add(herHead.clone().sub(s.Sm).normalize().multiplyScalar(1.0)); tL=tL.clone().lerp(down,dn); }
  // his right (outer) hand: on his knee, then reaching up to the light, then back down to the knee
  const up=sstep(7.0,9.5,t)*(1-sstep(11.0,11.6,t)); const tR=kneeHimR.clone().add(V(0.02,0.05,0.02)).lerp(s.Sm.clone().add(V(0.28,0.75,0.25)),up);
  const pLm=holding?V(0.2,-1,0.35):V(-0.6,-0.2,-0.6).lerp(V(0.5,0.2,1),dn); const pRm=V(0.8,-0.3*(1-up)+0.2*up,-0.4).normalize();
  const lookUp=s.Ph.clone().add(V(0.15,8,2.5)); const lookHer=herHead;
  let lookM; { const a=sstep(TPART+0.2,TPART+1.4,t), b=sstep(11.3,11.85,t); const la=s.Sf.clone().add(V(0,0.25,0.12)); lookM=la.lerp(lookUp,a).lerp(lookHer,b); }
  const Jm=skel({P:s.Ph,lean:lh.lean,roll:lh.roll,look:lookM,dangle:true,swing:t*2.2*(1-sstep(6,8,t))+0.6,tL,tR,pL:pLm,pR:pRm});
  // her right (inner) hand: clasp -> left reaching where his hand was -> lowered to her lap -> reaches up again in the wide shot
  let tRf; if(holding) tRf=cl; else { const lower=sstep(TPART+0.8,TPART+2.2,t); tRf=clPart.clone().lerp(kneeHerR.clone().add(V(-0.02,0.05,0.0)),lower); }
  const reachUp=sstep(13.2,14.3,t); if(reachUp>0) tRf=tRf.clone().lerp(s.Sf.clone().add(V(0.12,0.62,0.12)),reachUp);
  const tLf=kneeHer.clone().add(V(0.04,0.05,0.0));
  const Jf=skel({P:s.Pf,lean:lf.lean,roll:lf.roll,look:Jm.C.clone(),dangle:false,tL:tLf,tR:tRf,pL:V(-0.8,-0.2,-0.4),pR:holding?V(-0.2,-1,0.35):V(0.3,-0.6,-0.6)});
  poseFig(him,Jm); poseFig(her,Jf);
  const hg=holding?1:Math.exp(-(t-TPART)*5); handGlow.position.copy(Jm.wL.clone().add(Jf.wR).multiplyScalar(0.5)); handGlow.material.opacity=0.55*hg*(0.85+0.15*Math.sin(t*5)); handGlow.scale.setScalar(0.3+0.25*(holding?0:(1-hg)));
  himHalo.position.copy(Jm.C); const hw=sstep(12.3,13.6,t)*(1-sstep(16.4,17.2,t)); himHalo.material.opacity=0.85*hw; himHalo.scale.setScalar(1.6);
  return {Jm,Jf,hs};
}

// ---------------------------------------------------------------- camera
const WIDE={p:V(1.8,7.0,28),l:V(0.3,6.9,0)};
function camA(t,h){ const z=lerp(4.0,3.7,sstep(0,2.2,t))+h*0.95; return {p:V(0.3,1.02+h*0.62,z),l:V(0.04+0.12*clamp(h),0.74+h*0.56,0)}; }
function camB(t,Y){ const o=sstep(6.4,11.2,t); const x=lerp(0.6,1.5,o), z=lerp(3.7,3.3,o)-0.4*sstep(11.2,12.0,t);
  return {p:V(x,Y+0.15-0.25*o,z),l:V(XHIM-0.02,Y+0.42,0.05)}; }
function mixCam(a,b,u){ return {p:a.p.clone().lerp(b.p,u),l:a.l.clone().lerp(b.l,u)}; }
function camAt(t){
  const h=hSmooth(t), Y=SB+h;
  let c=mixCam(camA(t,h),camB(t,Y),sstep(TPART+0.15,TPART+1.4,t));
  const [h0]=[TL.hit]; if(t>=h0){ const u=clamp((t-h0)/2.2); const e=1-Math.pow(1-u,3.2); const from=camB(h0,SB+hSmooth(h0)); c=mixCam(from,WIDE,e);
    c.p.y+=Math.sin(Math.PI*e)*1.5; }                                        // a slight arc as it flies back
  const [w0,w1]=TL.wide; if(t>w0){ c.p.z-=1.2*sstep(w0,w1,t); }
  const [d0,d1]=TL.dive; if(t>d0){ const u=sstep(d0,d1,t); const from={p:WIDE.p.clone().add(V(0,0,-1.2)),l:WIDE.l.clone()}; c=mixCam(from,camA(0,hSmooth(0)),u*u*(3-2*u)); }
  return c; }

// ---------------------------------------------------------------- post
const composer=new EffectComposer(renderer); composer.setSize(W,H);
composer.addPass(new RenderPass(scene,cam));
const bloom=new UnrealBloomPass(new THREE.Vector2(W,H),0.42,0.6,0.82); composer.addPass(bloom);
const gradeU={tDiffuse:{value:null},uT:{value:0},uFlash:{value:0},uAsp:{value:W/H},uWarm:{value:0}};
composer.addPass(new ShaderPass({uniforms:gradeU,vertexShader:`varying vec2 vU; void main(){ vU=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
 fragmentShader:`varying vec2 vU; uniform sampler2D tDiffuse; uniform float uT,uFlash,uAsp,uWarm;
  float h(vec2 p){ return fract(sin(dot(p,vec2(12.9898,78.233))+uT*37.0)*43758.5453); }
  void main(){ vec2 c=vU-0.5; float r2=dot(c*vec2(uAsp,1.0),c*vec2(uAsp,1.0));
   vec2 off=c*0.0018*(1.0+r2*4.0);
   vec3 col=vec3(texture2D(tDiffuse,vU+off).r,texture2D(tDiffuse,vU).g,texture2D(tDiffuse,vU-off).b);
   col=vec3(1.0)-exp(-1.25*col);
   float l=dot(col,vec3(0.299,0.587,0.114)); col=mix(col*vec3(0.86,1.0,1.08),col*vec3(1.06,1.0,0.9),smoothstep(0.15,0.7,l)); col=mix(col,col*vec3(1.05,0.98,0.88),uWarm*0.4);
   float vig=1.0-smoothstep(0.12,0.5,r2)*0.72; col*=vig; col+=(h(vU*vec2(uAsp,1.0)*900.0)-0.5)*0.03; col+=uFlash*vec3(1.0,0.92,0.75);
   gl_FragColor=vec4(max(col,0.0),1.0);} `}));
composer.addPass(new OutputPass());

// ---------------------------------------------------------------- one sub-frame
function setT(t){
  const P=poseAll(t); poseCoins(t);
  const g=sstep(3.2,10.8,t);                              // money changes him: cream bone -> polished gold
  himMat.color.set(0xf2ecdc).lerp(new THREE.Color(0xf0b84e),g); himMat.metalness=0.95*g; himMat.roughness=lerp(0.55,0.24,g); himMat.envMapIntensity=1.1*g; himMat.emissiveIntensity=0.5*(1-g)+0.12*g; himMat.emissive.set(0x3a362c).lerp(new THREE.Color(0x4a2c08),g);
  const c=camAt(t); cam.position.copy(c.p); cam.lookAt(c.l); cam.fov=40; cam.updateProjectionMatrix();
  const up=sstep(4.0,11.0,t); skyU.uGold.value=0.15+1.1*up; skyU.uCamY.value=c.p.y;
  goldL.intensity=3.2*up; goldL.target.position.set(XHIM,SB+P.hs,0); goldL.position.set(XHIM+3,SB+P.hs+30,10); goldL.target.updateMatrixWorld();
  himL.intensity=4.5*up*(1-0.35*sstep(11.25,12,t)); himL.position.set(XHIM+0.7,SB+P.hs+1.3,1.3);
  for(const cl of clouds){ cl.material.opacity=cl.userData.base*0.14*(0.4+0.6*up); }
  spot.intensity=46; lampGlow.material.opacity=0.75;
  gradeU.uT.value=t; gradeU.uWarm.value=up*(1-sstep(12,13.5,t)); const d=t-TL.hit; gradeU.uFlash.value=(d>=0&&d<0.2)?0.12*(1-d/0.2):0;
  return P;
}
const acc=document.createElement('canvas'); acc.width=W; acc.height=H; const actx=acc.getContext('2d');
window.renderAt=function(t,Ksub=3){
  actx.globalAlpha=1; actx.clearRect(0,0,W,H); const shutter=1/60;
  for(let k=0;k<Ksub;k++){ setT(t+(Ksub>1?(k/(Ksub-1)-0.5)*shutter:0)); composer.render(); actx.globalAlpha=1/(k+1); actx.drawImage(renderer.domElement,0,0); }
  return acc.toDataURL('image/jpeg',0.95);
};
// screen positions and numbers for the overlay and the sound
const proj=v=>{ const p=v.clone().project(cam); return [ (p.x*0.5+0.5), (0.5-p.y*0.5) ]; };
window.metaAt=function(t){ const P=setT(t); cam.updateMatrixWorld(); return {t, worth:worthAt(t), herHead:proj(P.Jf.C), himHead:proj(P.Jm.C), herHand:proj(P.Jf.wR), himHand:proj(P.Jm.wL), seat:P.hs}; };
window.events={part:TPART, land:LAND, nc:NC, hf:HF};
window.ready=true;
