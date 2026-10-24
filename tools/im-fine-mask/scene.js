// I'm Fine (Slow Light Dark). A cream stickman lifts a porcelain mask with a thin red smile to his face. Work, friends,
// family: each in its own pool of gold light, the smile never changes. Alone at night he tries to take it off and it
// won't come; it creaks, a hairline crack. Across the dark a second lamp flickers on: a grey figure in the same mask.
// The grey one takes theirs off first. His loosens. Two faceless figures under two warm lamps.
// renderAt(t) is pure (no state carried between frames), so frames can be rendered in any order by parallel workers.
// World units are metres, floor is y = 0, the camera lives on +z. The pools sit in a row along +x (3.4 m apart, so
// only one is in frame at a time) and the camera trucks from pool to pool through the dark.
// Shared look (palette, rim/dust materials, floor, beam, motes, rig, grade) is copied from the series pilot
// tools/chain-never-locked/scene.js so the two reels match.
import * as THREE from 'three';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {UnrealBloomPass} from 'three/addons/postprocessing/UnrealBloomPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';
import {ShaderPass} from 'three/addons/postprocessing/ShaderPass.js';
import {Reflector} from 'three/addons/objects/Reflector.js';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';

const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960;
const TL=await (await fetch('timeline.json')).json(); const DUR=TL.duration;
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true}); renderer.setPixelRatio(1); renderer.setSize(W,H);
renderer.shadowMap.enabled=true; renderer.shadowMap.type=THREE.PCFSoftShadowMap; renderer.shadowMap.autoUpdate=false;
renderer.toneMapping=THREE.ACESFilmicToneMapping; renderer.toneMappingExposure=1.0; document.body.appendChild(renderer.domElement);
const scene=new THREE.Scene(); const VOID=new THREE.Color(0x07080b); scene.background=VOID; scene.fog=new THREE.FogExp2(VOID,0.085);
const cam=new THREE.PerspectiveCamera(38,W/H,0.02,60);

const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x)); const sstep=(a,b,x)=>{const t=clamp((x-a)/(b-a));return t*t*(3-2*t)}; const lerp=(a,b,t)=>a+(b-a)*t;
const ease=u=>u<0.5?4*u*u*u:1-Math.pow(-2*u+2,3)/2; const sm5=u=>u*u*u*(u*(u*6-15)+10); const V=(x,y,z)=>new THREE.Vector3(x,y,z);
function rng(seed){ let s=seed>>>0; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; }
const rotY=(v,y)=>V(v.x*Math.cos(y)+v.z*Math.sin(y),v.y,-v.x*Math.sin(y)+v.z*Math.cos(y));
const yawOf=d=>Math.atan2(-d.z,d.x);   // yaw that turns local +x onto direction d
const UPV=V(0,1,0);
const keys=(K,t)=>{ if(t<=K[0][0]) return K[0][1]; for(let i=1;i<K.length;i++) if(t<=K[i][0]){ const u=(t-K[i-1][0])/(K[i][0]-K[i-1][0]); return lerp(K[i-1][1],K[i][1],u*u*(3-2*u)); } return K[K.length-1][1]; };
const win=(t,a,b,fa=0.12,fb=0.12)=>sstep(a-fa,a,t)*(1-sstep(b,b+fb,t));   // 0..1 window with soft edges
const bump=(t,a,b)=>Math.sin(Math.PI*clamp((t-a)/(b-a)));

// ---------------------------------------------------------------- palette (series: Slow Light Dark)
const GOLD=new THREE.Color(0xe8b85a), CREAM=0xede6d6, SLATE=0x8a8f98, RED=0xd83a2e;

// ---------------------------------------------------------------- stage: pools in a row, the camera trucks between them
const POOL=[V(0,0,0),V(3.4,0,0),V(6.8,0,0),V(10.2,0,0),V(13.6,0,0)];
const NIGHT=POOL[4], GREYP=NIGHT.clone().add(V(1.6,0,-0.5));                 // the second night lamp, across the dark
const TR=TL.truck; const ARR=[0,...TR.map(x=>x[1])];                              // camera arrives at pool k at ARR[k]
const MID=TR.map(x=>(x[0]+x[1])/2);                                               // the hero changes pool at mid-truck (both out of frame)
const segAt=t=>{ let s=0; for(const m of MID) if(t>=m) s++; return s; };
// lamp k: overhead spot (pools 0-3, like the pilot) or a hanging night lamp (4 = his, 5 = the grey one's)
const LAMPS=[0,1,2,3].map(k=>({apex:POOL[k].clone().add(V(0,4.6,0.05)),tgt:POOL[k].clone().add(V(0.02,0,0)),cone:0.27,I:60,hang:false}));
LAMPS.push({apex:NIGHT.clone().add(V(0.05,2.2,0.05)),tgt:NIGHT.clone().add(V(0.05,0,0.05)),cone:0.56,I:15,hang:true});
LAMPS.push({apex:GREYP.clone().add(V(-0.08,2.2,0.08)),tgt:GREYP.clone().add(V(-0.08,0,0.08)),cone:0.56,I:15,hang:true});
// lamp k is live from the arrival at pool k-1 to the arrival at pool k+1 (two spot lights, alternating, are enough)
const lampLive=(k,t)=>k===5?t>=ARR[4]:(k<=1||t>=ARR[k-1])&&(k>=4||t<ARR[k+1]);
const BEAMK=+(q.get('beam')||0.14);

// ---------------------------------------------------------------- lights
scene.add(new THREE.HemisphereLight(0x1c2338,0x2a2218,0.1));
const spots=[0,1].map(()=>{ const s=new THREE.SpotLight(GOLD,0,0,0.35,0.85,1.2); s.castShadow=true; s.shadow.mapSize.set(2048,2048); s.shadow.bias=-0.00025; s.shadow.normalBias=0.012;
  scene.add(s,s.target); return s; });
const back=new THREE.DirectionalLight(0x9aa8c8,0.1); back.position.set(0.6,3.2,-4.5); back.target.position.set(0,0.5,0); scene.add(back,back.target);

// ---------------------------------------------------------------- material helpers: rim light, dust layer (from the pilot)
function rimify(mat,col,amt,key){ mat.userData.rim={value:amt}; mat.onBeforeCompile=s=>{ s.uniforms.uRim=mat.userData.rim; s.uniforms.uRimCol={value:new THREE.Color(col)};
  s.fragmentShader=s.fragmentShader.replace('#include <common>','#include <common>\nuniform float uRim; uniform vec3 uRimCol;')
   .replace('#include <emissivemap_fragment>',`#include <emissivemap_fragment>
     { vec3 vd=normalize(vViewPosition); float fr=pow(1.0-clamp(dot(normal,vd),0.0,1.0),2.6); totalEmissiveRadiance+=uRimCol*fr*uRim; }`); };
  mat.customProgramCacheKey=()=>'rim-'+key; return mat; }
function noiseTex(size,seed,base,amp,blobs,dark=0.25){ const c=document.createElement('canvas'); c.width=c.height=size; const g=c.getContext('2d'); const Rn=rng(seed);
  const im=g.createImageData(size,size); for(let i=0;i<size*size;i++){ const v=clamp(base+(Rn()-0.5)*amp,0,255); im.data[i*4]=im.data[i*4+1]=im.data[i*4+2]=v; im.data[i*4+3]=255; }
  g.putImageData(im,0,0); g.globalAlpha=dark; for(let k=0;k<blobs;k++){ g.fillStyle=Rn()<0.5?'#000':'#fff'; g.beginPath(); g.arc(Rn()*size,Rn()*size,Rn()*size*0.12,0,7); g.fill(); }
  const t=new THREE.CanvasTexture(c); t.wrapS=t.wrapT=THREE.RepeatWrapping; return t; }

// ---------------------------------------------------------------- floor: soft reflection under a dark, lit concrete skin (from the pilot)
// the mirror stops at z = 1.0: the near floor (bottom of the wide night frame) picked up stray gold streaks
const refl=new Reflector(new THREE.PlaneGeometry(80,31),{textureWidth:Math.round(W/3),textureHeight:Math.round(H/3),color:0x404040,clipBias:0.002});
refl.rotation.x=-Math.PI/2; refl.position.set(7,-0.006,-14.5); scene.add(refl); if(q.get('norefl')) refl.visible=false;
const fTex=noiseTex(512,5,128,40,140,0.06); fTex.repeat.set(18,14);
const floor=new THREE.Mesh(new THREE.PlaneGeometry(80,60),new THREE.MeshStandardMaterial({color:0x4a4a50,roughness:0.74,metalness:0,map:fTex,roughnessMap:fTex,transparent:true,opacity:0.9}));
floor.rotation.x=-Math.PI/2; floor.position.x=7; floor.receiveShadow=true; scene.add(floor);

const NOREFL=[];   // additive haze is not mirrored by the floor (it washed the foreground out)
// ---------------------------------------------------------------- furniture (dark, matte; it should never compete with the figures)
const WOOD=()=>new THREE.MeshStandardMaterial({color:0x3a3330,roughness:0.7,metalness:0.05,map:noiseTex(128,31,128,60,12)});
const METAL=()=>new THREE.MeshStandardMaterial({color:0x45464c,roughness:0.42,metalness:0.6});
const groups=POOL.map(()=>{ const g=new THREE.Group(); scene.add(g); return g; }); groups.push(groups[4]);
function add(g,mesh,pos,ry=0){ mesh.position.copy(pos); mesh.rotation.y=ry; mesh.castShadow=mesh.receiveShadow=true; g.add(mesh); return mesh; }
function chair(g,pos,ry,mat,back=true){   // pos = centre of the seat on the floor; seat top 0.45; back on the -x local side
  const c=new THREE.Group(); c.position.copy(pos); c.rotation.y=ry; g.add(c);
  const m=(geo,p)=>{ const o=new THREE.Mesh(geo,mat); o.position.copy(p); o.castShadow=o.receiveShadow=true; c.add(o); };
  m(new RoundedBoxGeometry(0.42,0.04,0.42,3,0.012),V(0,0.43,0));
  for(const [x,z] of [[-0.18,-0.18],[0.18,-0.18],[-0.18,0.18],[0.18,0.18]]) m(new THREE.CylinderGeometry(0.014,0.012,0.42,10),V(x,0.21,z));
  if(back){ m(new RoundedBoxGeometry(0.035,0.42,0.4,3,0.012),V(-0.2,0.66,0)); }
  return c; }
function stool(g,pos,mat){ add(g,new THREE.Mesh(new THREE.CylinderGeometry(0.17,0.17,0.04,28),mat),pos.clone().setY(0.43)); add(g,new THREE.Mesh(new THREE.CylinderGeometry(0.03,0.05,0.42,12),mat),pos.clone().setY(0.21)); }
function roundTable(g,pos,r,h,mat){ add(g,new THREE.Mesh(new THREE.CylinderGeometry(r,r,0.035,40),mat),pos.clone().setY(h)); add(g,new THREE.Mesh(new THREE.CylinderGeometry(0.035,0.035,h,12),mat),pos.clone().setY(h/2));
  add(g,new THREE.Mesh(new THREE.CylinderGeometry(0.2,0.22,0.03,24),mat),pos.clone().setY(0.015)); }
// hanging night lamp: cord, dark metal cone shade, warm bulb glow
function glowTex(){ const c=document.createElement('canvas'); c.width=c.height=128; const g=c.getContext('2d'); const r=g.createRadialGradient(64,64,0,64,64,64);
  r.addColorStop(0,'rgba(255,255,255,1)'); r.addColorStop(0.18,'rgba(255,255,255,0.45)'); r.addColorStop(0.5,'rgba(255,255,255,0.1)'); r.addColorStop(1,'rgba(255,255,255,0)'); g.fillStyle=r; g.fillRect(0,0,128,128);
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; return t; }
const GLOW=glowTex();
const sprite=(g,col,op)=>{ const s=new THREE.Sprite(new THREE.SpriteMaterial({map:GLOW,color:col,transparent:true,opacity:op,depthWrite:false,blending:THREE.AdditiveBlending,fog:false})); g.add(s); return s; };
function hangLamp(g,L){ const a=L.apex;
  add(g,new THREE.Mesh(new THREE.CylinderGeometry(0.004,0.004,4,6),METAL()),a.clone().add(V(0,2.14,0)));
  const outM=new THREE.MeshStandardMaterial({color:0x2a2b30,roughness:0.45,metalness:0.7,side:THREE.FrontSide});
  const inM=new THREE.MeshStandardMaterial({color:0x000000,emissive:GOLD,emissiveIntensity:0,side:THREE.BackSide});
  const geo=new THREE.CylinderGeometry(0.035,0.2,0.2,40,1,true);
  const o=add(g,new THREE.Mesh(geo,outM),a.clone().add(V(0,0.06,0))); o.castShadow=false;
  const i=add(g,new THREE.Mesh(geo,inM),a.clone().add(V(0,0.06,0))); i.castShadow=false;
  const bulb=new THREE.Mesh(new THREE.SphereGeometry(0.035,16,12),new THREE.MeshBasicMaterial({color:0xffe2a8})); bulb.position.copy(a).add(V(0,-0.0,0)); g.add(bulb);
  const glow=sprite(g,0xffc878,0); glow.position.copy(a).add(V(0,-0.02,0)); glow.scale.setScalar(0.5);
  L.fix={inM,bulb,glow}; NOREFL.push(bulb,glow,i); if(q.get('nofix')) [bulb,glow,i,o].forEach(x=>x.visible=false); }
for(const k of [4,5]) hangLamp(groups[4],LAMPS[k]);

// ---------------------------------------------------------------- stickman rig: capsule limbs, sphere head, no face (from the pilot)
const L={thigh:0.46,shin:0.46,torso:0.56,neck:0.07,head:0.13,upper:0.31,fore:0.29};
const LIMB=0.22*2*L.head*2;                               // limb radius = 0.22 x head diameter (limb diameter = 0.44 x)
function makeFig(color,key,rim,rimCol){
  const mat=rimify(new THREE.MeshStandardMaterial({color,roughness:0.62,metalness:0,emissive:color,emissiveIntensity:key==='hero'?0.07:0.06}),rimCol,rim,key);
  const cyl=new THREE.CylinderGeometry(1,1,1,16,1,true), sph=new THREE.SphereGeometry(1,24,16);
  const mk=g=>{ const m=new THREE.Mesh(g,mat); m.castShadow=true; m.receiveShadow=true; m.frustumCulled=false; scene.add(m); return m; };
  return {mat,bones:[...Array(9)].map(()=>mk(cyl)),joints:[...Array(14)].map(()=>mk(sph)),head:mk(sph)}; }
function bone(m,a,b,r){ const d=b.clone().sub(a); const len=Math.max(d.length(),1e-4); m.position.copy(a).add(b).multiplyScalar(0.5); m.scale.set(r,len,r); m.quaternion.setFromUnitVectors(UPV,d.multiplyScalar(1/len)); }
function ball(m,p,r){ m.position.copy(p); m.scale.setScalar(r); }
function ik(S,Tg,pole){ const d=Tg.clone().sub(S); const dist=Math.min(Math.max(d.length(),0.05),L.upper+L.fore-0.003); const dn=d.normalize();
  const a=(L.upper*L.upper-L.fore*L.fore+dist*dist)/(2*dist); const h=Math.sqrt(Math.max(0,L.upper*L.upper-a*a));
  const p=pole.clone().addScaledVector(dn,-pole.dot(dn)); if(p.lengthSq()<1e-6) p.set(0,-1,0); p.normalize();
  return {E:S.clone().addScaledVector(dn,a).addScaledVector(p,h), Hd:S.clone().addScaledVector(dn,dist)}; }
// pose: p torso pitch forward, tilt head pitch, hy head yaw, ty upper-body twist, aL/aR thigh angle, kL/kR knee bend,
// sL/sR arm swing, eL/eR elbow, dy hip offset, fx forward body shift; tL/tR world hand targets with weights wL/wR (two-bone IK).
const P0={p:0.05,tilt:0,hy:0,ty:0,aL:0.05,aR:-0.05,kL:0.05,kR:0.05,sL:0.12,sR:-0.05,eL:0.2,eR:0.2,dy:0,fx:0};
const blend=(a,b,u)=>{ const o={}; for(const k in P0) o[k]=lerp(a[k]??P0[k],b[k]??P0[k],u); for(const s of ['L','R']){ const ta=a['t'+s], tb=b['t'+s]; const wa=a['w'+s]||0, wb=b['w'+s]||0;
  if(ta||tb){ o['t'+s]=(ta&&tb)?ta.clone().lerp(tb,u):(ta||tb).clone(); o['w'+s]=lerp(ta?wa:0,tb?wb:0,u); o['p'+s]=(b['p'+s]||a['p'+s]); } } return o; };
function skel(P,root,yaw){
  const leg=(a,k)=>{ const kn=[Math.sin(a)*L.thigh,-Math.cos(a)*L.thigh]; const b=a-k; return [kn,[kn[0]+Math.sin(b)*L.shin,kn[1]-Math.cos(b)*L.shin]]; };
  const [kl,fl]=leg(P.aL,P.kL), [kr,fr]=leg(P.aR,P.kR);
  const hipY=-Math.min(fl[1],fr[1])+0.035+P.dy, hipX=-(fl[0]+fr[0])*0.5*0.6+P.fx;
  const W_=(x,y,z)=>rotY(V(x,y,z),yaw).add(root);
  const WU=(x,y,z)=>rotY(rotY(V(x-hipX,y,z),P.ty).add(V(hipX,0,0)),yaw).add(root);   // upper body, twisted about the hip
  const J={}; J.hip=W_(hipX,hipY,0); J.hipL=W_(hipX,hipY,0.07); J.hipR=W_(hipX,hipY,-0.07);
  J.kL=W_(hipX+kl[0],hipY+kl[1],0.08); J.fL=W_(hipX+fl[0],hipY+fl[1],0.08); J.kR=W_(hipX+kr[0],hipY+kr[1],-0.08); J.fR=W_(hipX+fr[0],hipY+fr[1],-0.08);
  const nx=hipX+Math.sin(P.p)*L.torso, ny=hipY+Math.cos(P.p)*L.torso; J.neck=WU(nx,ny,0);
  const hd=P.p+P.tilt; const hdir=rotY(rotY(V(Math.sin(hd),Math.cos(hd),0),P.hy),P.ty);
  J.head=J.neck.clone().addScaledVector(rotY(hdir,yaw),L.neck+L.head);
  J.hup=rotY(hdir,yaw).normalize(); J.hfwd=rotY(rotY(rotY(V(Math.cos(hd),-Math.sin(hd),0),P.hy),P.ty),yaw).normalize();   // head frame (for the mask)
  const shx=nx-Math.sin(P.p)*0.06, shy=ny-Math.cos(P.p)*0.06;
  for(const [s,z] of [['L',0.05],['R',-0.05]]){ const S=WU(shx,shy,z); const sa=P['s'+s], ea=P['e'+s];
    const E=WU(shx+Math.sin(sa)*L.upper,shy-Math.cos(sa)*L.upper,z*2.2); const Hd=WU(shx+Math.sin(sa)*L.upper+Math.sin(sa+ea)*L.fore,shy-Math.cos(sa)*L.upper-Math.cos(sa+ea)*L.fore,z*2.6);
    let E2=E,H2=Hd; const w=P['w'+s]||0;
    if(w>0&&P['t'+s]){ const tg=Hd.clone().lerp(P['t'+s],w); const pole=P['p'+s]?rotY(P['p'+s],yaw):E.clone().sub(S.clone().add(Hd).multiplyScalar(0.5)); const r=ik(S,tg,pole); E2=r.E; H2=r.Hd; }
    J['sh'+s]=S; J['el'+s]=E2; J['h'+s]=H2; }
  J.fwd=rotY(V(1,0,0),yaw); J.side=rotY(V(0,0,1),yaw); return J; }   // side = the figure's left
function poseFig(F,J){ const B=F.bones, r=LIMB/2;
  bone(B[0],J.hip,J.neck,r*1.25); bone(B[1],J.hipL,J.kL,r); bone(B[2],J.kL,J.fL,r); bone(B[3],J.hipR,J.kR,r); bone(B[4],J.kR,J.fR,r);
  bone(B[5],J.shL,J.elL,r); bone(B[6],J.elL,J.hL,r); bone(B[7],J.shR,J.elR,r); bone(B[8],J.elR,J.hR,r);
  [J.hipL,J.hipR,J.kL,J.kR,J.fL,J.fR,J.shL,J.shR,J.elL,J.elR,J.hL,J.hR,J.hip,J.neck].forEach((p,i)=>ball(F.joints[i],p,r*(i>=12?1.25:i>=10?1.3:i>=4&&i<6?1.15:1.0)));
  ball(F.head,J.head,L.head); }
function gait(P,ph,a,A=0.32,K=0.6,arm=0.22){ const s=Math.sin(ph), c=Math.cos(ph);
  return {...P,aL:P.aL+A*a*s,aR:P.aR-A*a*s,kL:P.kL+K*a*Math.max(0,c),kR:P.kR+K*a*Math.max(0,-c),sL:P.sL-arm*a*s,sR:P.sR+arm*a*s}; }
const figVisible=(F,v)=>F.bones.concat(F.joints,[F.head]).forEach(o=>o.visible=v);

const hero=makeFig(CREAM,'hero',0.16,0xfff1d8);
const GREYS=[0,1,2,3,4].map(i=>makeFig(SLATE,'grey'+i,0.13,0x9fb2d6));
// a small thumb for the thumbs-up
const thumbM=[new THREE.Mesh(new THREE.CylinderGeometry(1,1,1,10,1,true),hero.mat),new THREE.Mesh(new THREE.SphereGeometry(1,12,8),hero.mat)];
thumbM.forEach(m=>{ m.castShadow=true; scene.add(m); });

// ---------------------------------------------------------------- the mask: porcelain shell, painted eyes, the red smile (the one red object)
// local frame: +z out of the face, +y up, origin on the back rim plane. Canvas u runs left->right across the face.
const MASK={sx:0.152,sy:0.182,sz:0.092};
const maskGeo=new THREE.SphereGeometry(1,64,40,0,Math.PI,0.1*Math.PI,0.8*Math.PI); maskGeo.scale(MASK.sx,MASK.sy,MASK.sz);
const CRACK=(()=>{ const Rn=rng(77); const p=[[0.385,0.08]]; for(let i=0;i<9;i++){ const [x,y]=p[p.length-1]; p.push([x+0.012+0.014*(Rn()-0.35),y+0.034]); } return p; })();   // forehead toward the left eye
function makeMask(key){
  const cv=document.createElement('canvas'); cv.width=cv.height=1024; const g=cv.getContext('2d');
  const ev=document.createElement('canvas'); ev.width=ev.height=1024; const e=ev.getContext('2d');
  const map=new THREE.CanvasTexture(cv); map.colorSpace=THREE.SRGBColorSpace; map.anisotropy=8; const emap=new THREE.CanvasTexture(ev); emap.colorSpace=THREE.SRGBColorSpace;
  const S=1024; let last=-1;
  function draw(crack){ if(Math.abs(crack-last)<0.004) return; last=crack;
    const gr=g.createRadialGradient(S*0.5,S*0.42,S*0.05,S*0.5,S*0.5,S*0.62); gr.addColorStop(0,'#f8f6f1'); gr.addColorStop(1,'#d9d4ca'); g.fillStyle=gr; g.fillRect(0,0,S,S);
    // faint blush and brow shading so it reads as a face at a distance
    g.globalAlpha=0.08; g.fillStyle='#c7a493'; for(const x of [0.33,0.67]){ g.beginPath(); g.ellipse(S*x,S*0.56,S*0.07,S*0.04,0,0,7); g.fill(); } g.globalAlpha=1;
    // closed, smiling eyes (thin dark arcs)
    g.strokeStyle='#2c2a2b'; g.lineCap='round'; g.lineWidth=S*0.011;
    for(const x of [0.36,0.64]){ g.beginPath(); g.ellipse(S*x,S*0.425,S*0.062,S*0.035,0,Math.PI*1.08,Math.PI*1.92); g.stroke(); }
    // the smile: a thin red line
    const smile=c=>{ c.strokeStyle='#d83a2e'; c.lineCap='round'; c.lineWidth=S*0.012; c.beginPath(); c.ellipse(S*0.5,S*0.555,S*0.17,S*0.1,0,Math.PI*0.12,Math.PI*0.88); c.stroke(); };
    smile(g);
    // hairline crack, drawn up to `crack` (0..1) of its length
    if(crack>0){ const n=CRACK.length-1, upto=crack*n; g.strokeStyle='#5a534c'; g.lineWidth=S*0.0035; g.beginPath(); g.moveTo(CRACK[0][0]*S,CRACK[0][1]*S);
      for(let i=1;i<=Math.ceil(upto);i++){ const u=Math.min(1,upto-(i-1)); const a=CRACK[i-1], b=CRACK[i]; g.lineTo(S*lerp(a[0],b[0],u),S*lerp(a[1],b[1],u)); } g.stroke();
      if(upto>4){ const a=CRACK[4]; const u=clamp((upto-4)/3); g.lineWidth=S*0.0025; g.beginPath(); g.moveTo(a[0]*S,a[1]*S); g.lineTo(S*(a[0]-0.035*u),S*(a[1]+0.03*u)); g.stroke(); } }
    // emissive: a faint self-glow of the porcelain (so it reads white even with the lamp behind) plus the red line
    e.globalAlpha=1; e.fillStyle='#000'; e.fillRect(0,0,S,S); e.globalAlpha=0.2; e.drawImage(cv,0,0); e.globalAlpha=1; smile(e);
    map.needsUpdate=true; emap.needsUpdate=true; }
  draw(0);
  const mat=new THREE.MeshPhysicalMaterial({map,emissiveMap:emap,emissive:0xffffff,emissiveIntensity:1.0,roughness:0.24,metalness:0,clearcoat:1,clearcoatRoughness:0.1,side:THREE.DoubleSide});
  const m=new THREE.Mesh(maskGeo,mat); m.castShadow=true; m.receiveShadow=true; scene.add(m);
  return {m,draw}; }
const heroMask=makeMask('hero'), greyMask=makeMask('grey');
// mask transforms: {p, q}
const basisQ=(x,y,z)=>new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().makeBasis(x,y,z));
function faceT(J,off=0){ const z=J.hfwd.clone(), y=J.hup.clone().addScaledVector(z,-J.hup.dot(z)).normalize(), x=y.clone().cross(z);
  return {p:J.head.clone().addScaledVector(z,0.052+off).addScaledVector(y,-0.012),q:basisQ(x,y,z)}; }
function lookT(p,dir,upHint=UPV){ const z=dir.clone().normalize(); const y=upHint.clone().addScaledVector(z,-upHint.dot(z)).normalize(); return {p,q:basisQ(y.clone().cross(z),y,z)}; }
const mixT=(a,b,u)=>({p:a.p.clone().lerp(b.p,u),q:a.q.clone().slerp(b.q,u)});
const maskPt=(T,x,y,z)=>V(x,y,z).applyQuaternion(T.q).add(T.p);
function setMask(M,T){ M.m.position.copy(T.p); M.m.quaternion.copy(T.q); }
// both hands on the rim of the mask (used whenever he holds it)
const gripTargets=(T,w=1,pole=V(-0.3,-1,0))=>({tL:maskPt(T,MASK.sx*0.98,-0.02,0.025),tR:maskPt(T,-MASK.sx*0.98,-0.02,0.025),wL:w,wR:w,pL:pole.clone().setZ(0.6),pR:pole.clone().setZ(-0.6)});

// ---------------------------------------------------------------- the phone (FAMILY): "MOM" on the screen
const phone=new THREE.Group(); scene.add(phone);
const phoneCv=document.createElement('canvas'); phoneCv.width=256; phoneCv.height=512;
{ const g=phoneCv.getContext('2d'); const gr=g.createLinearGradient(0,0,0,512); gr.addColorStop(0,'#1b2233'); gr.addColorStop(1,'#0c0f18'); g.fillStyle=gr; g.fillRect(0,0,256,512);
  g.fillStyle='#ede6d6'; g.font='700 92px "JetBrains Mono", "DejaVu Sans Mono", monospace'; g.textAlign='center'; g.textBaseline='middle'; g.fillText('MOM',128,200);
  g.fillStyle='rgba(237,230,214,0.5)'; g.font='500 26px "JetBrains Mono", monospace'; g.fillText('calling', 128, 268);
  g.fillStyle='#3d8a5a'; g.beginPath(); g.arc(128,420,34,0,7); g.fill(); }
const phoneTex=new THREE.CanvasTexture(phoneCv); phoneTex.colorSpace=THREE.SRGBColorSpace;
const PH={w:0.115,h:0.23};   // a little oversized so MOM reads on a phone screen
{ const body=new THREE.Mesh(new RoundedBoxGeometry(PH.w,PH.h,0.011,4,0.008),new THREE.MeshStandardMaterial({color:0x101114,roughness:0.35,metalness:0.5})); body.castShadow=true; phone.add(body); }
const screenM=new THREE.MeshBasicMaterial({map:phoneTex,color:0xffffff,toneMapped:false}); const screen=new THREE.Mesh(new THREE.PlaneGeometry(PH.w*0.9,PH.h*0.92),screenM); screen.position.z=0.0062; phone.add(screen);
const phoneGlow=sprite(scene,0x9db4ff,0);

// ---------------------------------------------------------------- props per pool
const MATW=WOOD(), MATM=METAL();
// pool 1, WORK: he sits at a desk (to his left), two colleagues stand on his right
const H1={root:POOL[1].clone().add(V(-0.12,0,0.25)),dir:V(0.42,0,0.9)};
// pool 2, FRIENDS: round table, two friends; he sits on the near side
const H2={root:POOL[2].clone().add(V(-0.28,0,0.32)),dir:V(0.35,0,0.94)};
const H3={root:POOL[3].clone().add(V(0,0,0.15)),dir:V(0.2,0,0.98)};
const H4={root:NIGHT.clone().add(V(0,0,0.1)),dir:V(0.5,0,0.87)};
const SEATP={...P0,p:0.08,tilt:0.04,aL:1.52,aR:1.45,kL:1.48,kR:1.4,sL:0.3,sR:0.3,eL:0.95,eR:0.95};
const seatUnder=(root,dir,P=SEATP)=>{ const J=skel(P,root,yawOf(dir)); return J.hip.clone().addScaledVector(J.fwd,0.02).setY(0); };
chair(groups[1],seatUnder(H1.root,H1.dir),yawOf(H1.dir),MATM);
{ const g=groups[1], c=POOL[1];
  const desk=c.clone().add(V(-0.72,0,-0.32)), ry=yawOf(V(0.42,0,0.9))+Math.PI/2;
  add(g,new THREE.Mesh(new RoundedBoxGeometry(0.62,0.04,1.1,3,0.01),MATW),desk.clone().setY(0.74),ry);
  for(const [a,b] of [[-0.27,-0.5],[0.27,-0.5],[-0.27,0.5],[0.27,0.5]]){ const o=rotY(V(a,0,b),ry); add(g,new THREE.Mesh(new THREE.BoxGeometry(0.035,0.72,0.035),MATM),desk.clone().add(o).setY(0.36)); }
  const mon=desk.clone().add(rotY(V(-0.1,0,0.15),ry)); add(g,new THREE.Mesh(new THREE.BoxGeometry(0.05,0.2,0.05),MATM),mon.clone().setY(0.86),ry);
  const scr=add(g,new THREE.Mesh(new RoundedBoxGeometry(0.03,0.3,0.5,2,0.008),new THREE.MeshStandardMaterial({color:0x15171c,roughness:0.4,metalness:0.4,emissive:0x23304a,emissiveIntensity:0.6})),mon.clone().setY(1.08),ry); }
{ const g=groups[2], c=POOL[2]; roundTable(g,c.clone().add(V(0.22,0,-0.42)),0.42,0.72,MATW);
  stool(g,seatUnder(H2.root,H2.dir),MATW); }
const F1={root:POOL[2].clone().add(V(0.2,0,-1.02)),dir:V(0.1,0,1)}, F2={root:POOL[2].clone().add(V(0.85,0,-0.42)),dir:V(-0.95,0,0.3)};
stool(groups[2],seatUnder(F1.root,F1.dir),MATW); stool(groups[2],seatUnder(F2.root,F2.dir),MATW);
// night: his chair under his lamp; the grey one's chair and table under the other lamp
chair(groups[4],seatUnder(H4.root,H4.dir),yawOf(H4.dir),MATW);
const G4={root:GREYP.clone().add(V(0.12,0,0.05)),dir:V(-0.9,0,0.45)};
chair(groups[4],seatUnder(G4.root,G4.dir),yawOf(G4.dir),MATW);
const TABLE4=GREYP.clone().add(V(-0.3,0,0.2)); roundTable(groups[4],TABLE4,0.3,0.7,MATW);

// ---------------------------------------------------------------- hero, shot by shot
const STAND={...P0,p:0.03,aL:0.05,aR:-0.05,kL:0.05,kR:0.05,sL:0.06,sR:0.06,eL:0.12,eR:0.12};
const breathe=(P,t,a=1)=>{ const b=Math.sin(2*Math.PI*0.22*t)*a; return {...P,p:P.p+0.012*b,tilt:P.tilt+0.008*b}; };
function handsOnKnees(P,root,yaw,s=0){ const J=skel(P,root,yaw); const f=J.fwd;
  const kn=(k,h,side)=>k.clone().lerp(h,0.25).addScaledVector(f,-0.02).add(V(0,0.06,0)).addScaledVector(J.side,side*0.02);
  return {...P,tL:kn(J.kL,J.hipL,1),tR:kn(J.kR,J.hipR,-1),wL:1,wR:1,pL:V(0.2,-0.6,0.9),pR:V(0.2,-0.6,-0.9)}; }
function heroAt(t){
  const seg=segAt(t); let P, root, yaw, mask, thumb=0;
  if(seg===0){   // standing in the first pool: the mask at his chest, then up to his face
    root=POOL[0].clone().add(V(0,0,0.1)); yaw=yawOf(V(0,0,1));
    const u=sm5(sstep(TL.lift0,TL.lift1,t));
    P=breathe({...STAND,tilt:lerp(0.32,0.0,u)},t);   // looks down at it, then straight ahead
    const J=skel(P,root,yaw); const held=lookT(J.neck.clone().addScaledVector(J.fwd,0.27).add(V(0,-0.4,0)),V(0,0.45,1));
    const arc=lookT(J.neck.clone().addScaledVector(J.fwd,0.34).add(V(0,0.05,0)),V(0,0,1));
    const face=faceT(J); mask=u<0.5?mixT(held,arc,u*2):mixT(arc,face,u*2-1);
    const off=sstep(TL.lift1+0.1,TL.lift1+0.45,t);   // hands let go once it is on
    const gt=gripTargets(mask,1-off,V(-0.3,-1,0)); P={...P,...gt};
    if(off>0){ const rest=STAND; P=blend(P,{...P,sL:rest.sL,sR:rest.sR,eL:rest.eL,eR:rest.eR},off); }
    return {P,root,yaw,mask}; }
  if(seg===1){   // WORK: sits at the desk, turns to the colleagues, thumbs-up
    root=H1.root; yaw=yawOf(H1.dir); const th=win(t,TL.thumb0+0.2,TL.pat1+0.15,0.22,0.3);
    P=breathe({...SEATP,hy:-0.15+0.1*th,tilt:-0.03},t,0.6); P=handsOnKnees(P,root,yaw);
    const J=skel(P,root,yaw); const up=J.shR.clone().addScaledVector(J.fwd,0.26).addScaledVector(J.side,-0.1).add(V(0,0.06,0));
    P.tR=P.tR.clone().lerp(up,th); P.pR=V(0,-1,-0.6); thumb=th;
    P.p+=0.05*bump(t,TL.pat1,TL.pat1+0.4);   // the pat on the shoulder
    return {P,root,yaw,mask:null,thumb}; }
  if(seg===2){   // FRIENDS: laughing along, mask on
    root=H2.root; yaw=yawOf(H2.dir); const lg=win(t,TL.laugh0,TL.pat2+0.2,0.2,0.3);
    const lb=Math.abs(Math.sin((t-TL.laugh0)*2*Math.PI*1.9));
    P=breathe({...SEATP,p:0.1-0.07*lg*lb,tilt:-0.05-0.12*lg*lb,hy:0.35,ty:0.12},t,0.5); P=handsOnKnees(P,root,yaw);
    P.p+=0.05*bump(t,TL.pat2,TL.pat2+0.4);
    return {P,root,yaw,mask:null}; }
  if(seg===3){   // FAMILY: phone held out in his right hand, nodding along
    root=H3.root; yaw=yawOf(H3.dir); const nod=win(t,TL.phone0+0.15,TL.callEnd,0.1,0.1)*Math.max(0,Math.sin((t-TL.phone0)*2*Math.PI*1.6));
    const down=1-sstep(TL.callEnd+0.05,TL.callEnd+0.35,t);
    P=breathe({...STAND,tilt:0.38+0.12*nod,p:0.06},t,0.6);
    return {P,root,yaw,mask:null,phone:down}; }
  // NIGHT
  root=H4.root.clone(); yaw=yawOf(H4.dir);
  const sitU=sm5(sstep(TL.sit-0.45,TL.sit+0.05,t));
  const sat=handsOnKnees({...SEATP,p:0.14,tilt:0.12},root,yaw);
  if(sitU<1){ const st={...STAND,p:0.06,tilt:0.15}; P=blend(st,sat,Math.pow(sitU,1.4)); P.dy+=-0.02*bump(t,TL.sit-0.05,TL.sit+0.2); return {P,root,yaw,mask:null}; }
  // the struggle: grip, pull, release, pull harder, give up, slump
  const p1=bump(t,TL.pull1[0],TL.pull1[1]), p2=bump(t,TL.pull2[0],TL.pull2[1]);
  const pull=0.6*Math.pow(p1,0.7)+1.0*Math.pow(p2,0.6);
  const slump=sm5(sstep(TL.slump[0],TL.slump[1],t)); const look=sm5(sstep(TL.look[0],TL.look[1],t));
  const shake=(t>TL.pull1[0]&&t<TL.pull2[1])?0.006*pull*Math.sin(t*2*Math.PI*14):0;
  P={...SEATP,p:0.14+0.18*pull+0.3*slump-0.22*look,tilt:0.12+0.2*pull+0.42*slump-0.36*look+shake,hy:0.85*look,ty:0.42*look,sL:0.3,sR:0.3};
  P=breathe(P,t,1-0.6*pull);
  const gasp=bump(t,TL.gasp,TL.gasp+0.5); P.p-=0.05*gasp; P.tilt-=0.06*gasp;
  // at the end: his mask loosens; he lifts his head a little
  const low=sm5(sstep(TL.lower[0],TL.lower[1],t)); P.tilt-=0.12*low;
  P=handsOnKnees(P,root,yaw);
  return {P,root,yaw,mask:null,pull,slump,look,low}; }
const crackAt=t=>sstep(TL.crack,TL.crack+0.22,t);

// ---------------------------------------------------------------- the grey ones
// [pool group, figure] -> {P, root, yaw} or null
const GSTAND={...P0,p:0.04,sL:0.06,sR:0.06,eL:0.2,eR:0.2};
function walkOff(P,root,dir,t0,t,v=1.25){ if(t<t0) return {P,root}; const turnU=sm5(sstep(t0,t0+0.25,t)); const d=Math.max(0,t-t0-0.08)*v*sstep(t0,t0+0.35,t);
  return {P:gait(P,d/1.3*2*Math.PI,clamp(d*4)),root:root.clone().addScaledVector(dir,d),turnU}; }
function patTarget(J,t0,t){ return J.shL.clone().add(V(0,0.075+0.02*Math.max(0,Math.sin((t-t0)*2*Math.PI*4.5)),0)); }   // two small pats on his left shoulder
function greyAt(i,t,Jh){
  if(i===0){ if(segAt(t)!==1&&!(t>=ARR[0]&&t<ARR[2])) return null;   // WORK, colleague A: stands at his right, pats, walks off into the dark
    const root0=POOL[1].clone().add(V(0.5,0,-0.2)); let yaw=yawOf(H1.root.clone().sub(root0)); let P=breathe(GSTAND,t+1.3,0.6);
    const reach=win(t,TL.pat1,TL.pat1+0.42,0.16,0.18);
    if(Jh&&reach>0){ P={...P,p:0.12*reach,tR:patTarget(Jh,TL.pat1,t),wR:reach,pR:V(0,-1,-0.5)}; }
    const w=walkOff(P,root0,V(0.75,0,-0.66),TL.pat1+0.48,t); if(w.turnU) yaw=lerp(yaw,yawOf(V(0.75,0,-0.66)),w.turnU);
    return {P:w.P,root:w.root,yaw}; }
  if(i===1){ if(!(t>=ARR[0]&&t<ARR[2])) return null;   // WORK, colleague B: by the desk, nods, leaves
    const root0=POOL[1].clone().add(V(0.05,0,-0.75)); let yaw=yawOf(V(-0.1,0,1)); let P=breathe({...GSTAND,tilt:0.08*Math.max(0,Math.sin((t-2.5)*7))*win(t,2.6,3.2)},t+0.6,0.6);
    const w=walkOff(P,root0,V(-0.9,0,-0.45),TL.pat1+0.15,t,1.1); if(w.turnU) yaw=lerp(yaw,yawOf(V(-0.9,0,-0.45)),w.turnU);
    return {P:w.P,root:w.root,yaw}; }
  if(i===2||i===3){ if(!(t>=ARR[1]&&t<ARR[3])) return null;   // FRIENDS: two seated, laughing; friend 2 gets up, pats, leaves
    const F=i===2?F1:F2; let yaw=yawOf(F.dir); const lg=win(t,TL.laugh0-0.1,TL.pat2,0.15,0.25), ph=i===2?0.3:1.1;
    const lb=Math.abs(Math.sin((t-TL.laugh0)*2*Math.PI*1.9+ph));
    let P={...SEATP,p:0.12-0.16*lg*lb,tilt:-0.1-0.25*lg*lb,hy:i===2?-0.3:0.2,sL:0.5+0.25*lg*lb,sR:0.5,eL:1.2,eR:1.0};
    if(i===2) return {P,root:F.root,yaw};
    // friend 2: stands (pat2-0.45 .. pat2-0.1), walks behind him, pats, leaves to the left
    const up=sm5(sstep(TL.pat2-0.5,TL.pat2-0.15,t)); if(up<=0) return {P,root:F.root,yaw};
    const via=Jh?Jh.shL.clone().setY(0).addScaledVector(Jh.fwd,-0.42).addScaledVector(Jh.side,0.1):F.root;
    const mv=sm5(sstep(TL.pat2-0.3,TL.pat2+0.05,t)); let root=F.root.clone().lerp(via,mv);
    P=blend(P,{...GSTAND},up); if(mv>0&&mv<1) P=gait(P,mv*2*Math.PI*1.2,bump(mv,0,1)*0.8);
    yaw=lerp(yaw,yawOf(via.clone().sub(F.root)),sm5(sstep(TL.pat2-0.45,TL.pat2-0.2,t)));
    const reach=win(t,TL.pat2+0.02,TL.pat2+0.4,0.12,0.15); if(Jh&&reach>0){ P={...P,tR:patTarget(Jh,TL.pat2,t),wR:reach,pR:V(0,-1,-0.5)}; }
    const exit=V(-1,0,-0.25).normalize(); const w=walkOff(P,root,exit,TL.pat2+0.45,t,1.3); if(w.turnU) yaw=lerp(yaw,yawOf(exit),w.turnU);
    return {P:w.P,root:w.root,yaw}; }
  // i===4: the grey one at night (seated at the table, masked; first to take it off)
  if(t<ARR[3]) return null;
  const yaw=yawOf(G4.dir); const off=sm5(sstep(TL.greyOff[0],TL.greyOff[1],t));
  let P=breathe({...SEATP,p:0.2-0.06*off,tilt:0.18-0.08*off,hy:0.08},t+2.1,0.8);
  return {P,root:G4.root,yaw}; }

// ---------------------------------------------------------------- beams (one per lamp) and motes, as in the pilot
{ const ob=refl.onBeforeRender; refl.onBeforeRender=function(...a){ NOREFL.forEach(o=>o.visible&&(o.userData.hide=true,o.visible=false)); ob.apply(this,a); NOREFL.forEach(o=>{ if(o.userData.hide){ o.visible=true; o.userData.hide=false; } }); }; }
function makeBeam(Lp){
  const u={uT:{value:0},uI:{value:1},uApex:{value:Lp.apex},uAxis:{value:Lp.tgt.clone().sub(Lp.apex).normalize()},uTan:{value:Math.tan(Lp.cone)},uCol:{value:GOLD.clone()}};
  const h=Lp.apex.distanceTo(Lp.tgt)+0.02, r=Math.tan(Lp.cone)*h*1.02;
  const g=new THREE.CylinderGeometry(0.02,r,h,96,24,true); g.translate(0,-h/2,0);
  const k=(Lp.hang?0.55:1)*BEAMK, fall=Lp.hang?0.9:0.55;
  const m=new THREE.Mesh(g,new THREE.ShaderMaterial({uniforms:u,transparent:true,depthWrite:false,side:THREE.BackSide,blending:THREE.AdditiveBlending,fog:false,
    vertexShader:`varying vec3 vW; void main(){ vec4 w=modelMatrix*vec4(position,1.0); vW=w.xyz; gl_Position=projectionMatrix*viewMatrix*w; }`,
    fragmentShader:`varying vec3 vW; uniform vec3 uApex,uAxis,uCol; uniform float uT,uI,uTan;
      float h(vec3 p){ return fract(sin(dot(p,vec3(12.9898,78.233,37.719)))*43758.5453); }
      float n3(vec3 p){ vec3 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f);
        return mix(mix(mix(h(i),h(i+vec3(1,0,0)),f.x),mix(h(i+vec3(0,1,0)),h(i+vec3(1,1,0)),f.x),f.y),mix(mix(h(i+vec3(0,0,1)),h(i+vec3(1,0,1)),f.x),mix(h(i+vec3(0,1,1)),h(i+vec3(1,1,1)),f.x),f.y),f.z); }
      void main(){ vec3 ro=cameraPosition, rd=normalize(vW-cameraPosition); float tEnd=length(vW-cameraPosition);
        float acc=0.0; float t0=0.0; float t1=tEnd;
        for(int i=0;i<16;i++){ float s=mix(t0,t1,(float(i)+0.5)/16.0); vec3 p=ro+rd*s; vec3 q=p-uApex; float ax=dot(q,uAxis); if(ax<=0.0) continue;
          float rr=length(q-uAxis*ax), rc=ax*uTan; float cone=pow(smoothstep(rc,rc*0.15,rr),1.6);
          float fl=smoothstep(0.0,0.35,p.y);
          float hz=0.62+0.55*n3(p*vec3(2.2,0.9,2.2)+vec3(0.0,-uT*0.05,uT*0.03))+0.25*n3(p*6.0+vec3(uT*0.08,0.0,0.0));
          acc+=cone*fl*hz/(0.6+ax*${fall.toFixed(2)}); }
        acc*=(t1-t0)/16.0; gl_FragColor=vec4(uCol*acc*uI*${k.toFixed(4)},1.0); }`}));
  m.position.copy(Lp.apex); m.quaternion.setFromUnitVectors(V(0,-1,0),u.uAxis.value); m.frustumCulled=false; m.renderOrder=5; scene.add(m); NOREFL.push(m);
  // motes around this lamp
  const mu={uT:{value:0},uH:{value:H},uApex:{value:Lp.apex},uAxis:{value:u.uAxis.value},uTan:{value:Math.tan(Lp.cone)},uCol:{value:new THREE.Color(1.0,0.85,0.62)},uOp:{value:1}};
  const N=1100, Rn=rng(21+Math.round(Lp.apex.x*10)), pos=new Float32Array(N*3), sd=new Float32Array(N), top=Lp.apex.y-0.1;
  for(let i=0;i<N;i++){ const a=Rn()*6.283, r=Math.sqrt(Rn())*(Lp.hang?1.4:1.6); pos[i*3]=Lp.tgt.x+Math.cos(a)*r; pos[i*3+1]=Rn()*top; pos[i*3+2]=Lp.tgt.z+Math.sin(a)*r; sd[i]=Rn(); }
  const gg=new THREE.BufferGeometry(); gg.setAttribute('position',new THREE.BufferAttribute(pos,3)); gg.setAttribute('seed',new THREE.BufferAttribute(sd,1));
  const pts=new THREE.Points(gg,new THREE.ShaderMaterial({uniforms:mu,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
    vertexShader:`attribute float seed; uniform float uT,uH,uTan; uniform vec3 uApex,uAxis; varying float vA;
      void main(){ vec3 p=position; float s=seed*6.283;
        p.y=mod(p.y-uT*(0.015+0.02*seed)+${top.toFixed(2)},${top.toFixed(2)}); p.x+=0.06*sin(uT*0.37+s)+0.03*sin(uT*0.9+s*2.0); p.z+=0.06*cos(uT*0.31+s*1.3);
        vec3 q=p-uApex; float ax=dot(q,uAxis); float rr=length(q-uAxis*ax), rc=max(ax,0.0)*uTan;
        vA=smoothstep(rc*1.05,rc*0.5,rr)*(0.35+0.65*fract(seed*7.13))*(0.75+0.25*sin(uT*(1.0+seed*2.0)+s));
        vec4 mv=modelViewMatrix*vec4(p,1.0); gl_Position=projectionMatrix*mv;
        float sz=(0.0055+0.006*fract(seed*3.7))*uH/(-mv.z)*1.6; gl_PointSize=clamp(sz,1.0,26.0); vA*=clamp(1.6/sz,0.08,1.0)*min(1.0,sz); }`,
    fragmentShader:`uniform vec3 uCol; uniform float uOp; varying float vA; void main(){ vec2 c=gl_PointCoord-0.5; float d=length(c); float a=smoothstep(0.5,0.0,d); gl_FragColor=vec4(uCol*a*vA*uOp*0.9,1.0); }`}));
  pts.frustumCulled=false; scene.add(pts); NOREFL.push(pts);
  return {m,u,pts,mu}; }
const BEAMS=LAMPS.map(makeBeam);

// lamp brightness over time (1 = full). Night: his lamp is lower; the grey one's flickers on, both warm up at the end.
function lampLevel(k,t){
  if(k<4) return 1;
  const warm=sstep(TL.warm[0],TL.warm[1],t);
  if(k===4) return (0.9+0.18*warm)*sstep(ARR[3]-0.6,ARR[3]-0.1,t+0.0);
  const [f0,f1]=TL.flicker; if(t<f0) return 0;
  const FL=[[0,0],[0.05,0.7],[0.09,0.05],[0.2,0],[0.26,0.85],[0.31,0.3],[0.4,0.95],[0.55,0.9]];   // a filament catching: on, off, on
  const tt=(t-f0)/(f1-f0); let fl=0.9; if(tt<1){ for(const [a,v] of FL) if(tt>=a) fl=v; }
  return fl+0.18*warm; }

// ---------------------------------------------------------------- camera
// opening push-in; truck pool to pool (same framing each pool); night: push in to his mask, then pull out wide to find the other lamp
const FR=[ {p:V(0,1.25,3.9),l:V(0,0.98,0)},   // opening (push-in to the next one)
  {p:POOL[1].clone().add(V(0.1,1.45,4.35)),l:POOL[1].clone().add(V(0.02,0.82,-0.15))},
  {p:POOL[2].clone().add(V(0.05,1.5,4.35)),l:POOL[2].clone().add(V(0.02,0.8,-0.2))},
  {p:POOL[3].clone().add(V(0.2,1.5,4.2)),l:POOL[3].clone().add(V(0.0,0.9,0.0))},
  {p:NIGHT.clone().add(V(-0.25,1.38,3.5)),l:NIGHT.clone().add(V(0.1,0.82,0))} ];
const OPEN1={p:V(0,1.3,3.25),l:V(0,1.05,0)};
const WIDE={p:NIGHT.clone().add(V(-0.75,1.85,5.7)),l:NIGHT.clone().add(V(0.88,0.5,-0.35))}, WIDE2={p:NIGHT.clone().add(V(-0.62,1.75,5.15)),l:NIGHT.clone().add(V(0.86,0.52,-0.35))};
const lerpC=(a,b,u)=>({p:a.p.clone().lerp(b.p,u),l:a.l.clone().lerp(b.l,u)});
function holdAt(k,t){   // where the camera sits while it is at pool k (with a slow drift)
  if(k===0){ return lerpC(FR[0],OPEN1,sm5(clamp(t/TR[0][0]))); }
  const t0=ARR[k], t1=k<4?TR[k][0]:DUR; const u=clamp((t-t0)/Math.max(0.01,t1-t0));
  const c=lerpC(FR[k],FR[k],0); c.p.addScaledVector(c.l.clone().sub(c.p).normalize(),0.15*u); return c; }
let CU=null;
function camAt(t,Jh){
  for(let k=0;k<4;k++){ const [a,b]=TR[k]; if(t>=a&&t<b){ const u=sm5((t-a)/(b-a)); return lerpC(holdAt(k,a),holdAt(k+1,b),u); } }
  const k=segAt(t); if(k<4) return holdAt(k,t);
  // night
  if(!CU){ const J=heroRig(TL.pull2[0]).J; const f=J.hfwd.clone().setY(0).normalize(); CU={p:J.head.clone().addScaledVector(f,2.05).add(V(-0.08,0.04,0)),l:J.head.clone().add(V(0,-0.05,0))}; }
  if(t<TL.pullOut[0]){ const u=sm5(sstep(ARR[4],TL.pull1[0]+0.3,t)); const c=lerpC(holdAt(4,ARR[4]),CU,u); c.p.addScaledVector(c.l.clone().sub(c.p).normalize(),0.06*sstep(TL.pull1[0],TL.slump[0],t)-0.3*sstep(TL.slump[0],TL.pullOut[0]+0.3,t)); c.l.y-=0.12*sstep(TL.slump[0],TL.pullOut[0]+0.3,t); return c; }
  if(t<TL.pullOut[1]){ const u=sm5((t-TL.pullOut[0])/(TL.pullOut[1]-TL.pullOut[0])); const c0=lerpC(CU,CU,0); c0.p.addScaledVector(c0.l.clone().sub(c0.p).normalize(),0.06-0.3*sstep(TL.slump[0],TL.pullOut[0]+0.3,t)); c0.l.y-=0.12*sstep(TL.slump[0],TL.pullOut[0]+0.3,t);
    return {p:c0.p.clone().lerp(WIDE.p,u),l:c0.l.clone().lerp(WIDE.l,Math.pow(u,0.8))}; }
  return lerpC(WIDE,WIDE2,sm5(clamp((t-TL.pullOut[1])/(DUR-TL.pullOut[1])))); }
const shakeAt=t=>{ let s=0; for(const [t0,a] of [[TL.creak2,0.5],[TL.creak1,0.25]]) if(t>t0) s+=a*Math.exp(-(t-t0)/0.12); return s; };

// ---------------------------------------------------------------- post (from the pilot)
const composer=new EffectComposer(renderer); composer.setSize(W,H);
composer.addPass(new RenderPass(scene,cam));
const bloom=new UnrealBloomPass(new THREE.Vector2(W,H),0.45,0.6,0.88); composer.addPass(bloom);
const gradePass=new ShaderPass({uniforms:{tDiffuse:{value:null},uT:{value:0},uAsp:{value:W/H}},vertexShader:`varying vec2 vU; void main(){ vU=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
 fragmentShader:`varying vec2 vU; uniform sampler2D tDiffuse; uniform float uT,uAsp;
  float h(vec2 p){ return fract(sin(dot(p,vec2(12.9898,78.233))+uT*37.0)*43758.5453); }
  void main(){ vec2 c=vU-0.5; float r2=dot(c*vec2(uAsp,1.0),c*vec2(uAsp,1.0));
   vec3 col=texture2D(tDiffuse,vU).rgb; col=vec3(1.0)-exp(-1.15*col);
   float vig=1.0-smoothstep(0.06,0.42,r2)*0.62; col*=vig;
   col+=vec3(0.0006,0.0010,0.0028)*smoothstep(0.08,0.45,r2);
   col+=(h(vU*vec2(uAsp,1.0)*900.0)-0.5)*0.006*(0.3+col);
   gl_FragColor=vec4(max(col,0.0),1.0);} `});
composer.addPass(gradePass); const GU=gradePass.uniforms;
composer.addPass(new OutputPass());

// ---------------------------------------------------------------- one sub-frame
function heroRig(t){ const h=heroAt(t); const J=skel(h.P,h.root,h.yaw); return {h,J}; }
function setT(t){
  const {h,J:Jh0}=heroRig(t); let Jh=Jh0; const seg=segAt(t);
  // --- the hero's mask
  let MT=h.mask;
  if(!MT){ MT=faceT(Jh);
    if(seg===4&&t>=TL.grip-0.3){   // night: hands on the rim; it moves a few millimetres and stops
      const pull=h.pull||0, slump=h.slump||0, low=h.low||0;
      const loosen=sstep(TL.loosen,TL.loosen+0.2,t), wob=0.004*Math.sin((t-TL.loosen)*40)*Math.exp(-Math.max(0,t-TL.loosen)/0.15)*(t>TL.loosen?1:0);
      MT=faceT(Jh,0.006*pull+0.004*loosen+wob);
      const grip=sstep(TL.grip-0.3,TL.grip,t)*(1-sstep(TL.slump[0],TL.slump[0]+0.35,t));
      if(low>0){   // lowers it to his lap with his right hand, face up
        const lap=Jh.kR.clone().lerp(Jh.hipR,0.45).add(V(0,0.13,0)).addScaledVector(Jh.side,0.04);
        const LT=lookT(lap,V(-0.35,1,0.75),Jh.fwd.clone().negate());   // face up, tipped toward the camera so the smile reads
        const mid=lookT(Jh.neck.clone().addScaledVector(Jh.fwd,0.32).add(V(0,-0.05,0)),Jh.fwd.clone().add(V(0,0.5,0)));
        MT=low<0.5?mixT(MT,mid,sm5(low*2)):mixT(mid,LT,sm5(low*2-1)); }
      const take=sstep(TL.loosen-0.25,TL.loosen,t);
      const P=h.P; const g=gripTargets(MT,1,V(-0.3,-1,0)); let P2={...P};
      if(grip>0){ P2.tL=P.tL.clone().lerp(g.tL,grip); P2.tR=P.tR.clone().lerp(g.tR,grip); P2.pL=g.pL; P2.pR=g.pR; }
      if(take>0){ P2.tR=P2.tR.clone().lerp(low>0?maskPt(MT,-MASK.sx*0.9,0,0.03):g.tR,take); P2.pR=g.pR; P2.tL=P2.tL.clone().lerp(g.tL,take*(1-sstep(0.3,0.7,low))); }
      Jh=skel(P2,h.root,h.yaw); if(low<=0) MT=faceT(Jh,0.006*pull+0.004*loosen+wob); } }
  else if(seg===0){ /* opening: held mask, transform from heroAt */ }
  poseFig(hero,Jh); setMask(heroMask,MT); heroMask.draw(crackAt(t));
  // thumb
  const th=h.thumb||0; thumbM.forEach(m=>m.visible=th>0.05);
  if(th>0.05){ const base=Jh.hR.clone().add(V(0,0.03,0)); const tip=base.clone().add(V(0,0.06*th,0)); bone(thumbM[0],base,tip,LIMB*0.22); ball(thumbM[1],tip,LIMB*0.22); }
  // phone
  const ph=seg===3?(h.phone??0):0; phone.visible=seg===3; phoneGlow.visible=seg===3;
  if(seg===3){ const ring=sstep(TL.phone0-0.6,TL.phone0-0.4,t);
    const pos=Jh.neck.clone().addScaledVector(Jh.fwd,0.32).addScaledVector(Jh.side,-0.06).add(V(0,-0.2-0.25*(1-ph),0));
    const T=lookT(pos,Jh.fwd.clone().multiplyScalar(0.75).add(V(0,0.66,0)),V(0,1,0).addScaledVector(Jh.fwd,-0.4));
    phone.position.copy(T.p); phone.quaternion.copy(T.q);
    const P2={...h.P,tR:maskPt(T,0.01,-0.13,-0.03),wR:1,pR:V(0.2,-1,-0.8)}; Jh=skel(P2,h.root,h.yaw); poseFig(hero,Jh); setMask(heroMask,faceT(Jh));
    const lit=ring*(1-sstep(TL.callEnd,TL.callEnd+0.12,t)); screenM.color.setScalar(0.08+0.92*lit); phoneGlow.position.copy(maskPt(T,0,0,0.04)); phoneGlow.scale.setScalar(0.22); phoneGlow.material.opacity=0.1*lit; }
  // grey figures
  GREYS.forEach((F,i)=>{ const g=greyAt(i,t,Jh); figVisible(F,!!g); if(g){ let Jg=skel(g.P,g.root,g.yaw);
      if(i===4){ const P=g.P; const tbl=TABLE4.clone().setY(0.735);
        const onT={...P,tL:tbl.clone().addScaledVector(Jg.side,0.1).addScaledVector(Jg.fwd,-0.06),tR:tbl.clone().addScaledVector(Jg.side,-0.12).addScaledVector(Jg.fwd,-0.04),wL:1,wR:1,pL:V(0,-1,0.8),pR:V(0,-1,-0.8)};
        Jg=skel(onT,g.root,g.yaw);
        let GT=faceT(Jg); const lift=sm5(sstep(TL.greyLift[0],TL.greyLift[1],t)), off=sm5(sstep(TL.greyOff[0],TL.greyOff[1],t)), put=sm5(sstep(TL.greyOff[1],TL.clink,t));
        if(off>0){ const held=lookT(Jg.neck.clone().addScaledVector(Jg.fwd,0.36).add(V(0,-0.06,0)),Jg.fwd.clone().add(V(0,0.25,0)));
          const onTable=lookT(tbl.clone().add(V(0,0.04,0)).addScaledVector(Jg.side,-0.02).addScaledVector(Jg.fwd,0.1),V(-0.45,1,0.6),Jg.fwd.clone());   // resting on its rim, tipped toward us
          GT=put>0?mixT(held,onTable,put):mixT(GT,held,off); }
        const hold=lift*(1-sstep(TL.clink,TL.clink+0.3,t));
        if(hold>0){ const gt=gripTargets(GT,1,V(-0.3,-1,0)); const P2={...onT,tL:onT.tL.clone().lerp(gt.tL,hold),tR:onT.tR.clone().lerp(gt.tR,hold),pL:gt.pL,pR:gt.pR}; Jg=skel(P2,g.root,g.yaw); if(off<=0) GT=faceT(Jg); }
        setMask(greyMask,GT); }
      poseFig(F,Jg); } });
  greyMask.m.visible=t>=ARR[3];
  // furniture groups, lamps, beams
  groups.forEach((g,k)=>{ if(k<5) g.visible=lampLive(k,t)||(k===4&&t>=ARR[3]); });
  let si=[0,0];
  LAMPS.forEach((Lp,k)=>{ const live=lampLive(k,t), lev=live?lampLevel(k,t):0, B=BEAMS[k];
    B.m.visible=B.pts.visible=live&&lev>0.001&&!q.get('nobeam'); if(q.get('nomote')) B.pts.visible=false; B.u.uI.value=lev; B.u.uT.value=t; B.mu.uT.value=t; B.mu.uOp.value=lev;
    if(Lp.fix){ Lp.fix.inM.emissiveIntensity=1.4*lev; Lp.fix.bulb.material.color.setRGB(0.15+0.85*lev,0.12+0.76*lev,0.08+0.58*lev); Lp.fix.glow.material.opacity=0.55*lev; }
    if(live){ const s=spots[k%2]; s.position.copy(Lp.apex); s.target.position.copy(Lp.tgt); s.angle=Lp.cone+0.08; s.intensity=Lp.I*lev;
      const sc=s.shadow.camera; const n=Lp.hang?0.15:1.5, f=Lp.hang?4:7; if(sc.near!==n||sc.far!==f){ sc.near=n; sc.far=f; sc.updateProjectionMatrix(); } } });
  for(let s=0;s<2;s++) if(!LAMPS.some((Lp,k)=>k%2===s&&lampLive(k,t))) spots[s].intensity=0;
  // camera
  const c=camAt(t,Jh); cam.position.copy(c.p); cam.lookAt(c.l); cam.updateProjectionMatrix();
  const sh=shakeAt(t); if(sh>0){ cam.rotateX(0.004*sh*Math.sin(t*131.0)); cam.rotateY(0.004*sh*Math.sin(t*97.0+1.3)); }
  GU.uT.value=t;
  return {Jh,MT}; }
const acc=document.createElement('canvas'); acc.width=W; acc.height=H; const actx=acc.getContext('2d');
window.renderAt=function(t,Ksub=3){
  const inTruck=TR.some(([a,b])=>t>a-0.05&&t<b+0.05); if(inTruck) Ksub=Math.max(Ksub,6);
  // never blur across the mid-truck pool switch
  const m=MID.find(x=>Math.abs(t-x)<0.02);
  const shutter=1/60; actx.globalAlpha=1; actx.clearRect(0,0,W,H);
  for(let k=0;k<Ksub;k++){ let tt=t+(Ksub>1?(k/(Ksub-1)-0.5)*shutter:0); tt=clamp(tt,0,DUR-1e-4); if(m!==undefined) tt=(t<m)?Math.min(tt,m-1e-4):Math.max(tt,m);
    setT(tt); renderer.shadowMap.needsUpdate=true; composer.render(); actx.globalAlpha=1/(k+1); actx.drawImage(renderer.domElement,0,0); }
  return acc.toDataURL('image/jpeg',0.95); };
const proj=v=>{ const p=v.clone().project(cam); return [p.x*0.5+0.5,0.5-p.y*0.5,p.z<1?1:0]; };
window.metaAt=function(t){ const S=setT(t); cam.updateMatrixWorld(); return {t,seg:segAt(t),hero:proj(S.Jh.head),mask:proj(S.MT.p),grey:proj(GREYP.clone().add(V(0,1.1,0)))}; };
window.events={...TL,ARR,MID};
window.ready=true;
