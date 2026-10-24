// The Chain Was Never Locked (Slow Light Dark). A cream stickman sits under one gold lamp, chained at the ankle to an
// iron post. In year one he pulls twice, the chain snaps taut, nothing. He sits down and never tugs again. Years pass,
// grey strangers walk through the beam, dust gathers. The camera pushes in to the red padlock: its shackle was open
// the whole time. Cut wide on a sub-boom: he looks at the lock.
// renderAt(t) is pure (no state carried between frames), so frames can be rendered in any order by parallel workers.
// World units are metres, floor is y = 0. The post stands at x < 0, he sits at x > 0, the camera lives on +z.
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
// keyframed scalar: [[t,v],...] with smoothstep between keys
const keys=(K,t)=>{ if(t<=K[0][0]) return K[0][1]; for(let i=1;i<K.length;i++) if(t<=K[i][0]){ const u=(t-K[i-1][0])/(K[i][0]-K[i-1][0]); return lerp(K[i-1][1],K[i][1],u*u*(3-2*u)); } return K[K.length-1][1]; };

// ---------------------------------------------------------------- palette (series: Slow Light Dark)
const GOLD=new THREE.Color(0xe8b85a), CREAM=0xede6d6, SLATE=0x8a8f98, RED=0xd83a2e;

// ---------------------------------------------------------------- time: years, slump, dust
const YEARS=TL.years;                                    // YEAR 2..12 appear at these times
const yearAt=t=>{ let y=1; for(const s of YEARS) if(t>=s) y++; return y; };
const yearF=t=>{ if(t<YEARS[0]) return 1; for(let i=1;i<YEARS.length;i++) if(t<YEARS[i]) return 2+i-1+(t-YEARS[i-1])/(YEARS[i]-YEARS[i-1]); return Math.min(12,12+(t-YEARS[YEARS.length-1])/0.3); };
const slumpAt=t=>t<YEARS[0]?0:t>=TL.cut?1:sm5(clamp((yearF(t)-1)/11));   // posture sinks a little more every year
const dustAt=t=>t<YEARS[0]?0.04:t>=TL.cut?0.9:lerp(0.04,0.9,clamp((yearF(t)-1.2)/10.8));

// ---------------------------------------------------------------- stage
const POST=V(-0.85,0,-0.12), POST_R=0.075, POST_H=1.5;
const DR=V(0.8,0,0.6).normalize();                       // the ring on the post points this way
const RING_R=0.046, RING_TUBE=0.0095, SHK_TUBE=0.0085*1.3;
const RINGC=POST.clone().addScaledVector(DR,POST_R+RING_R+0.004).setY(0.42);
const APEX=RINGC.clone().add(V(0,-(RING_R+RING_TUBE+SHK_TUBE)+0.002,0));     // lock hangs from the ring here (pivot)
const DIRH=V(1,0,0.12).normalize();                      // from the lock toward him (horizontal)
const SEAT=V(APEX.x,0,APEX.z).addScaledVector(DIRH,1.3);
const SIT_FWD=rotY(DIRH.clone().negate(),-0.22);          // sits facing the post, turned toward camera
const SIT_YAW=yawOf(SIT_FWD), PULL_YAW=yawOf(DIRH.clone().negate());
const CHAIN_LEN=2.3, S1=0.98, PITCH=0.05, NL=Math.round(CHAIN_LEN/PITCH), LINK_Y=0.0105;
const LAMP=V(0.0,4.6,0.05), LAMP_T=V(0.02,0,0.0), CONE=0.27, SPOT_I=+(q.get('spot')||60), BEAMK=+(q.get('beam')||0.14);

// ---------------------------------------------------------------- lights
scene.add(new THREE.HemisphereLight(0x1c2338,0x2a2218,0.1));
const spot=new THREE.SpotLight(GOLD,SPOT_I,0,CONE+0.08,0.85,1.2); spot.position.copy(LAMP); spot.target.position.copy(LAMP_T);
spot.castShadow=true; spot.shadow.mapSize.set(2048,2048); spot.shadow.bias=-0.00025; spot.shadow.normalBias=0.012; spot.shadow.camera.near=1.5; spot.shadow.camera.far=7;
scene.add(spot,spot.target);
const back=new THREE.DirectionalLight(0x9aa8c8,0.1); back.position.set(0.6,3.2,-4.5); back.target.position.set(0,0.5,0); scene.add(back,back.target);
const fill=new THREE.DirectionalLight(0xa89880,0.0); fill.position.set(1.0,0.6,5); scene.add(fill);


// ---------------------------------------------------------------- material helpers: rim light, dust layer
const dustU={uDust:{value:0}};
function rimify(mat,col,amt,key){ mat.userData.rim={value:amt}; mat.onBeforeCompile=s=>{ s.uniforms.uRim=mat.userData.rim; s.uniforms.uRimCol={value:new THREE.Color(col)};
  s.fragmentShader=s.fragmentShader.replace('#include <common>','#include <common>\nuniform float uRim; uniform vec3 uRimCol;')
   .replace('#include <emissivemap_fragment>',`#include <emissivemap_fragment>
     { vec3 vd=normalize(vViewPosition); float fr=pow(1.0-clamp(dot(normal,vd),0.0,1.0),2.6); totalEmissiveRadiance+=uRimCol*fr*uRim; }`); };
  mat.customProgramCacheKey=()=>'rim-'+key; return mat; }
function dustify(mat,key,inst=false){ mat.onBeforeCompile=s=>{ s.uniforms.uDust=dustU.uDust;
  s.vertexShader=s.vertexShader.replace('#include <common>','#include <common>\nvarying vec3 vDW; varying vec3 vDN;')
   .replace('#include <project_vertex>',`#include <project_vertex>
     { vec4 dw=vec4(transformed,1.0); vec3 dn=objectNormal;
       #ifdef USE_INSTANCING
         dw=instanceMatrix*dw; dn=mat3(instanceMatrix)*dn;
       #endif
       vDW=(modelMatrix*dw).xyz; vDN=normalize(mat3(modelMatrix)*dn); }`);
  s.fragmentShader=s.fragmentShader.replace('#include <common>',`#include <common>
     varying vec3 vDW; varying vec3 vDN; uniform float uDust; float dAmt;
     float dh(vec3 p){ return fract(sin(dot(p,vec3(12.9898,78.233,37.719)))*43758.5453); }
     float dn3(vec3 p){ vec3 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f);
       return mix(mix(mix(dh(i),dh(i+vec3(1,0,0)),f.x),mix(dh(i+vec3(0,1,0)),dh(i+vec3(1,1,0)),f.x),f.y),
                  mix(mix(dh(i+vec3(0,0,1)),dh(i+vec3(1,0,1)),f.x),mix(dh(i+vec3(0,1,1)),dh(i+vec3(1,1,1)),f.x),f.y),f.z); }`)
   .replace('#include <color_fragment>',`#include <color_fragment>
     { float up=smoothstep(-0.15,0.85,normalize(vDN).y); float n=dn3(vDW*55.0)*0.55+dn3(vDW*190.0)*0.45;
       dAmt=clamp(uDust*(0.1+0.9*up)*(0.45+0.8*n)-0.1,0.0,0.8); diffuseColor.rgb=mix(diffuseColor.rgb,vec3(0.12,0.11,0.1),dAmt); }`)
   .replace('#include <metalnessmap_fragment>','#include <metalnessmap_fragment>\nmetalnessFactor=mix(metalnessFactor,0.0,dAmt);')
   .replace('#include <roughnessmap_fragment>','#include <roughnessmap_fragment>\nroughnessFactor=mix(roughnessFactor,1.0,dAmt);'); };
  mat.customProgramCacheKey=()=>'dust-'+key+(inst?'-i':''); return mat; }
function noiseTex(size,seed,base,amp,blobs,dark=0.25){ const c=document.createElement('canvas'); c.width=c.height=size; const g=c.getContext('2d'); const Rn=rng(seed);
  const im=g.createImageData(size,size); for(let i=0;i<size*size;i++){ const v=clamp(base+(Rn()-0.5)*amp,0,255); im.data[i*4]=im.data[i*4+1]=im.data[i*4+2]=v; im.data[i*4+3]=255; }
  g.putImageData(im,0,0); g.globalAlpha=dark; for(let k=0;k<blobs;k++){ g.fillStyle=Rn()<0.5?'#000':'#fff'; g.beginPath(); g.arc(Rn()*size,Rn()*size,Rn()*size*0.12,0,7); g.fill(); }
  const t=new THREE.CanvasTexture(c); t.wrapS=t.wrapT=THREE.RepeatWrapping; return t; }

// ---------------------------------------------------------------- floor: soft reflection under a dark, lit concrete skin
const refl=new Reflector(new THREE.PlaneGeometry(60,60),{textureWidth:Math.round(W/3),textureHeight:Math.round(H/3),color:0x404040,clipBias:0.002});
refl.rotation.x=-Math.PI/2; refl.position.y=-0.006; scene.add(refl);
const fTex=noiseTex(512,5,128,40,140,0.06); fTex.repeat.set(14,14);
const floor=new THREE.Mesh(new THREE.PlaneGeometry(60,60),new THREE.MeshStandardMaterial({color:0x4a4a50,roughness:0.74,metalness:0,map:fTex,roughnessMap:fTex,transparent:true,opacity:0.9}));
floor.rotation.x=-Math.PI/2; floor.receiveShadow=true; scene.add(floor);

// ---------------------------------------------------------------- the iron post, its ring, the ankle cuff
// the post rocks 3-4% of its height on each snap (pivot at the base); the ring and the lock ride with it
const POST_BASE=V(POST.x,0,POST.z); const postG=new THREE.Group(); postG.position.copy(POST_BASE); scene.add(postG);
function postTilt(t){ let a=0; for(const [s,amp] of [[TL.snap1,0.024],[TL.snap2,0.034]]) if(t>s){ const x=t-s; a+=amp*Math.exp(-x/0.32)*Math.sin(2*Math.PI*4.2*x+0.35)/Math.sin(0.35+Math.PI/2); }
  a+=0.006*tensionAt(t); return new THREE.Quaternion().setFromUnitVectors(UPV,UPV.clone().addScaledVector(DIRH,Math.tan(a)).normalize()); }
const onPost=(p,t)=>p.clone().sub(POST_BASE).applyQuaternion(postTilt(t)).add(POST_BASE);
const IRON=()=>new THREE.MeshStandardMaterial({color:0x4a4a50,roughness:0.48,metalness:0.4,map:noiseTex(128,77,128,90,20)});
{ const m=dustify(IRON(),'post');
  const post=new THREE.Mesh(new THREE.CylinderGeometry(POST_R,POST_R*1.04,POST_H,40),m); post.position.copy(POST).setY(POST_H/2);
  const cap=new THREE.Mesh(new THREE.CylinderGeometry(POST_R*1.25,POST_R*1.25,0.05,40),m); cap.position.copy(POST).setY(POST_H+0.02);
  const knob=new THREE.Mesh(new THREE.SphereGeometry(POST_R*0.95,32,16,0,Math.PI*2,0,Math.PI/2),m); knob.position.copy(POST).setY(POST_H+0.045);
  const base=new THREE.Mesh(new THREE.CylinderGeometry(POST_R*1.9,POST_R*2.1,0.06,40),m); base.position.copy(POST).setY(0.03);
  const band=new THREE.Mesh(new THREE.CylinderGeometry(POST_R*1.12,POST_R*1.12,0.04,40),m); band.position.copy(POST).setY(0.42);
  const plate=new THREE.Mesh(new THREE.BoxGeometry(0.03,0.07,0.035),m); plate.position.copy(POST).addScaledVector(DR,POST_R+0.004).setY(0.42); plate.rotation.y=yawOf(DR);
  for(const o of [post,cap,knob,base,band,plate]){ o.castShadow=o.receiveShadow=true; o.position.sub(POST_BASE); postG.add(o); }
  // bolts on the base plate
  for(let i=0;i<4;i++){ const a=i*Math.PI/2+0.4; const b=new THREE.Mesh(new THREE.CylinderGeometry(0.012,0.012,0.02,12),m); b.position.set(Math.cos(a)*POST_R*1.6,0.066,Math.sin(a)*POST_R*1.6); b.castShadow=true; scene.add(b); b.position.add(POST_BASE); } }
// the ring hangs in the plane of DR and up
const ring=new THREE.Mesh(new THREE.TorusGeometry(RING_R,RING_TUBE,16,48),dustify(IRON(),'ring')); ring.position.copy(RINGC); ring.rotation.y=yawOf(DR); ring.castShadow=ring.receiveShadow=true; ring.position.sub(POST_BASE); postG.add(ring);
const cuff=new THREE.Mesh(new THREE.TorusGeometry(0.052,0.016,14,32),dustify(IRON(),'cuff')); cuff.castShadow=true; scene.add(cuff);

// ---------------------------------------------------------------- the padlock (the one red object). Its shackle is OPEN: lifted out of the body and swung.
const LOCK={bw:0.086,bh:0.096,bd:0.034,leg:0.026,lift:0.03,swing:-0.75};
const LS=1.3; const lockG=new THREE.Group(), lockIn=new THREE.Group(); lockG.add(lockIn); lockG.scale.setScalar(LS); scene.add(lockG);
const lockMat=dustify(new THREE.MeshStandardMaterial({color:RED,roughness:0.38,metalness:0.35,emissive:RED,emissiveIntensity:0.05}),'lock');
const steel=dustify(new THREE.MeshStandardMaterial({color:0x9a9ca3,roughness:0.28,metalness:0.95}),'shackle');
{ const body=new THREE.Mesh(new RoundedBoxGeometry(LOCK.bw,LOCK.bh,LOCK.bd,5,0.013),lockMat); body.position.set(0,-0.0675-LOCK.bh/2,0); body.castShadow=body.receiveShadow=true; lockIn.add(body);
  // keyhole + a thin bevelled face plate
  const dark=new THREE.MeshStandardMaterial({color:0x050505,roughness:0.6});
  const kh=new THREE.Mesh(new THREE.CylinderGeometry(0.0062,0.0062,0.004,20),dark); kh.rotation.x=Math.PI/2; kh.position.set(0,body.position.y+0.008,LOCK.bd/2+0.0005); lockIn.add(kh);
  const ks=new THREE.Mesh(new THREE.BoxGeometry(0.0042,0.014,0.004),dark); ks.position.set(0,body.position.y-0.0015,LOCK.bd/2+0.0005); lockIn.add(ks);
  const plateM=new THREE.MeshStandardMaterial({color:0x8e8f94,roughness:0.3,metalness:0.9});
  const fp=new THREE.Mesh(new THREE.CylinderGeometry(0.0115,0.0115,0.002,28),plateM); fp.rotation.x=Math.PI/2; fp.position.set(0,body.position.y+0.004,LOCK.bd/2-0.0002); lockIn.add(fp);
  // two holes on top (the free one is visible when the shackle is open)
  for(const x of [-LOCK.leg,LOCK.leg]){ const h=new THREE.Mesh(new THREE.CylinderGeometry(SHK_TUBE*1.15,SHK_TUBE*1.15,0.002,20),dark); h.position.set(x,-0.0672,0); lockIn.add(h); } }
// shackle: long leg at x=-leg (pivot), short leg at x=+leg; closed apex at the origin
const shk=new THREE.Group(); lockIn.add(shk);
{ const pts=[]; const a=LOCK.leg; pts.push(V(-a,-0.098,0)); for(let i=0;i<=24;i++){ const th=Math.PI-i/24*Math.PI; pts.push(V(Math.cos(th)*a,-a+Math.sin(th)*a,0)); } pts.push(V(a,-0.0725,0));
  const curve=new THREE.CatmullRomCurve3([V(-a,-0.098,0),V(-a,-0.06,0),V(-a,-a,0),...pts.slice(2,25),V(a,-a,0),V(a,-0.0725,0)],false,'centripetal');
  const m=new THREE.Mesh(new THREE.TubeGeometry(curve,96,SHK_TUBE,14,false),steel); m.castShadow=true; shk.add(m);
  const tip=new THREE.Mesh(new THREE.SphereGeometry(SHK_TUBE,14,10),steel); tip.position.set(a,-0.0725,0); shk.add(tip); }
// open: lift, then swing about the long leg. lockIn is offset so the open apex sits at the group origin (the pivot on the ring).
shk.position.set(-LOCK.leg,LOCK.lift,0); shk.children.forEach(c=>c.position.x+=LOCK.leg); shk.rotation.y=LOCK.swing;
const APEX_L=V(-LOCK.leg+LOCK.leg*Math.cos(LOCK.swing),LOCK.lift,-LOCK.leg*Math.sin(LOCK.swing)); lockIn.position.copy(APEX_L).negate();
const lockLight=new THREE.PointLight(0xff4a36,0.06,0.6,2); scene.add(lockLight);
// small gold glint that catches the gap between the free leg and the body
function glowTex(){ const c=document.createElement('canvas'); c.width=c.height=128; const g=c.getContext('2d'); const r=g.createRadialGradient(64,64,0,64,64,64);
  r.addColorStop(0,'rgba(255,255,255,1)'); r.addColorStop(0.18,'rgba(255,255,255,0.45)'); r.addColorStop(0.5,'rgba(255,255,255,0.1)'); r.addColorStop(1,'rgba(255,255,255,0)'); g.fillStyle=r; g.fillRect(0,0,128,128);
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; return t; }
const GLOW=glowTex();
const sprite=(col,op)=>{ const s=new THREE.Sprite(new THREE.SpriteMaterial({map:GLOW,color:col,transparent:true,opacity:op,depthWrite:false,blending:THREE.AdditiveBlending,fog:false})); scene.add(s); return s; };
const lockGlow=sprite(0xff3a2a,0.16), glint=sprite(0xffd890,0), tipLight=sprite(0xffe2b0,0);
// pose of the lock: hangs from the ring, tilts toward the chain while it is taut, sways after
function lockPose(t){ const T=tensionAt(t); let ax=0;
  const sway=(t0,a,tau,f)=>t>t0?a*Math.exp(-(t-t0)/tau)*Math.sin((t-t0)*f):0;
  ax+=0.55*T+sway(TL.snap1,0.12,0.25,22)+sway(TL.snap2,0.16,0.25,22)+sway(TL.release,-0.22,0.45,11)+sway(TL.creak,0.05,0.6,7);
  const axis=V(-DIRH.z,0,DIRH.x);           // horizontal, perpendicular to the pull
  const qy=new THREE.Quaternion().setFromAxisAngle(UPV,0.12), qs=new THREE.Quaternion().setFromAxisAngle(axis,ax);
  return {p:onPost(APEX,t),q:postTilt(t).multiply(qs.multiply(qy))}; }
// the chain's first link hangs on the shackle next to the ring
const lockLinkPoint=(t)=>{ const L=lockPose(t); return V(-0.034,-0.03,-0.03).applyQuaternion(L.q).add(L.p); };   // on the long leg of the shackle

// ---------------------------------------------------------------- stickman rig: capsule limbs, sphere head, no face
const L={thigh:0.46,shin:0.46,torso:0.56,neck:0.07,head:0.13,upper:0.31,fore:0.29};
const LIMB=0.22*2*L.head*2;                               // limb radius = 0.22 x head diameter (limb diameter = 0.44 x)
function makeFig(color,key,rim,rimCol){
  const mat=rimify(new THREE.MeshStandardMaterial({color,roughness:0.62,metalness:0,emissive:color,emissiveIntensity:key==='hero'?0.07:0.0}),rimCol,rim,key);
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
  const shx=nx-Math.sin(P.p)*0.06, shy=ny-Math.cos(P.p)*0.06;
  for(const [s,z] of [['L',0.05],['R',-0.05]]){ const S=WU(shx,shy,z); const sa=P['s'+s], ea=P['e'+s];
    const E=WU(shx+Math.sin(sa)*L.upper,shy-Math.cos(sa)*L.upper,z*2.2); const Hd=WU(shx+Math.sin(sa)*L.upper+Math.sin(sa+ea)*L.fore,shy-Math.cos(sa)*L.upper-Math.cos(sa+ea)*L.fore,z*2.6);
    let E2=E,H2=Hd; const w=P['w'+s]||0;
    if(w>0&&P['t'+s]){ const tg=Hd.clone().lerp(P['t'+s],w); const pole=P['p'+s]?rotY(P['p'+s],yaw):E.clone().sub(S.clone().add(Hd).multiplyScalar(0.5)); const r=ik(S,tg,pole); E2=r.E; H2=r.Hd; }
    J['sh'+s]=S; J['el'+s]=E2; J['h'+s]=H2; }
  J.fwd=rotY(V(1,0,0),yaw); return J; }
function poseFig(F,J){ const B=F.bones, r=LIMB/2;
  bone(B[0],J.hip,J.neck,r*1.25); bone(B[1],J.hipL,J.kL,r); bone(B[2],J.kL,J.fL,r); bone(B[3],J.hipR,J.kR,r); bone(B[4],J.kR,J.fR,r);
  bone(B[5],J.shL,J.elL,r); bone(B[6],J.elL,J.hL,r); bone(B[7],J.shR,J.elR,r); bone(B[8],J.elR,J.hR,r);
  [J.hipL,J.hipR,J.kL,J.kR,J.fL,J.fR,J.shL,J.shR,J.elL,J.elR,J.hL,J.hR,J.hip,J.neck].forEach((p,i)=>ball(F.joints[i],p,r*(i>=12?1.25:i>=10?1.3:i>=4&&i<6?1.15:1.0)));
  ball(F.head,J.head,L.head); }
function gait(P,ph,a,A=0.32,K=0.6,arm=0.22){ const s=Math.sin(ph), c=Math.cos(ph);
  return {...P,aL:P.aL+A*a*s,aR:P.aR-A*a*s,kL:P.kL+K*a*Math.max(0,c),kR:P.kR+K*a*Math.max(0,-c),sL:P.sL-arm*a*s,sR:P.sR+arm*a*s}; }

const hero=makeFig(CREAM,'hero',0.16,0xfff1d8);

// ---------------------------------------------------------------- hero poses
// sitting on the floor, knees up. slump 0 (year one) -> 1 (year twelve): folds over his knees, head down and turned away.
const SIT0={...P0,p:0.34,tilt:0.22,hy:-0.1,aL:1.95,aR:1.9,kL:2.58,kR:2.5,dy:-0.2,sL:0.8,sR:0.8,eL:0.6,eR:0.6};
const SIT1={...P0,p:0.82,tilt:0.62,hy:-0.95,ty:-0.08,aL:2.08,aR:2.02,kL:2.78,kR:2.7,dy:-0.2,sL:0.5,sR:0.5,eL:0.4,eR:0.4,fx:-0.03};
const LOOK={...P0,p:0.42,tilt:0.62,hy:0.25,ty:0.18,aL:2.0,aR:1.96,kL:2.7,kR:2.6,dy:-0.2,sL:0.6,sR:0.6,eL:0.5,eR:0.5};
function sitPose(s,t){ const br=Math.sin(2*Math.PI*0.21*t)*(1-0.5*s); const P=blend(SIT0,SIT1,s); P.p+=0.018*br; P.tilt+=0.01*br; return P; }
function handsOnKnees(P,root,yaw,s){ const J=skel(P,root,yaw); const f=J.fwd;
  const knee=(k,ft,side)=>k.clone().lerp(ft,lerp(0.12,0.55,s)).addScaledVector(f,lerp(0.05,0.07,s)).add(V(0,lerp(0.045,0.0,s),0)).addScaledVector(rotY(V(0,0,1),yaw),side*lerp(0,0.05,s));
  return {...P,tL:knee(J.kL,J.fL,1),tR:knee(J.kR,J.fR,-1),wL:1,wR:1,pL:V(-0.2,-0.6,0.8),pR:V(-0.2,-0.6,-0.8)}; }

// ---------------------------------------------------------------- year one: stand, grab, pull twice, give up, sit
// he pulls the chain toward himself; hd = how far (horizontally from the lock) his hands try to go; the chain stops them at HMAX
const GY=0.78, HMAX=Math.sqrt(S1*S1-Math.pow(GY-0.3,2));
const HD_K=[[TL.grab,HMAX-0.25],[2.6,HMAX-0.07]];
function hdWant(t){
  if(t<2.6) return keys(HD_K,t);
  const seg=(t0,t1,a,b,p)=>lerp(a,b,Math.pow(clamp((t-t0)/(t1-t0)),p));
  if(t<TL.snap1) return seg(2.6,TL.snap1,HMAX-0.07,HMAX,2.2);                               // heave 1, accelerating into the snap
  if(t<3.0) return HMAX+0.06*sstep(TL.snap1,3.0,t);                                   // keeps straining against it
  if(t<3.25) return lerp(HMAX+0.06,HMAX-0.04,sstep(3.0,3.25,t));                          // gives a little slack, resets
  if(t<TL.snap2) return seg(3.25,TL.snap2,HMAX-0.04,HMAX,2.4);                            // heave 2, harder
  if(t<3.78) return HMAX+0.12*sstep(TL.snap2,3.78,t);
  return lerp(HMAX+0.12,HMAX-0.03,sstep(3.78,TL.release,t)); }
const hdAt=t=>Math.min(hdWant(t),HMAX);
const strainAt=t=>(t<2.6||t>TL.release+0.1)?0:clamp((hdWant(t)-HMAX)/0.08);
const tensionAt=t=>(t<2.5||t>TL.release)?0:sstep(HMAX-0.012,HMAX,hdAt(t))*(1-sstep(TL.release-0.06,TL.release,t));
const jolt=(t,t0,a)=>{ const x=t-t0; return x>0?a*(x/0.07)*Math.exp(1-x/0.07):0; };   // one smooth recoil bump
const gripAt=t=>{ const h=hdAt(t); const up=keys([[TL.grab,0],[2.6,1]],t); const c0=chainRestPoint(S1);
  const g=V(APEX.x,0,APEX.z).addScaledVector(DIRH,h).setY(GY-0.06*strainAt(t));
  return t<2.6?c0.clone().lerp(g,ease(up)):g; };
function pullPose(t){
  const st=strainAt(t), lean=-0.22-0.45*st-0.12*sstep(2.45,2.7,t);
  const j=jolt(t,TL.snap1,0.07)+jolt(t,TL.snap2,0.1);
  const P={...P0,p:lean+j*1.4,tilt:-0.15+0.25*st,aL:0.55,aR:-0.42-0.08*st,kL:0.62+0.25*st,kR:0.25+0.1*st,dy:-0.03-0.05*st,fx:-0.06*st+j*0.25};
  return P; }
// SEAT matches the pull stance, so standing up is nearly in place
const PULL_ROOT=t=>V(APEX.x,0,APEX.z).addScaledVector(DIRH,hdAt(t)+0.47+0.05*strainAt(t)-(jolt(t,TL.snap1,0.07)+jolt(t,TL.snap2,0.1))*0.4);
const CROUCH={...P0,p:0.95,tilt:0.1,aL:1.25,aR:0.85,kL:2.05,kR:1.6,dy:-0.02,sL:0.9,sR:0.9,eL:0.2,eR:0.2};
const HUNCH={...P0,p:0.42,tilt:0.48,aL:0.12,aR:-0.08,kL:0.18,kR:0.12,sL:0.04,sR:0.02,eL:0.12,eR:0.1};

function heroAt(t){
  let P, root=SEAT.clone(), yaw=SIT_YAW;
  if(t<TL.stand0 || t>=TL.sitDown+0.25){                       // sitting
    let s=slumpAt(t);
    if(t>=TL.sitDown+0.25&&t<YEARS[0]) s=0.06*sstep(TL.sitDown,5.0,t);
    P=sitPose(s,t);
    if(t>=TL.cut){ const u=sm5(sstep(TL.look0,TL.look1,t)); P=blend(P,{...LOOK,p:LOOK.p+0.012*Math.sin(2*Math.PI*0.2*t)},u); s=lerp(1,0.55,u); }
    if(t>=TL.creak-0.25&&t<TL.creak+0.5){ const b=Math.sin(Math.PI*clamp((t-TL.creak+0.25)/0.75)); P.kR+=0.07*b; P.aR+=0.03*b; }   // shifts his leg: the chain moves
    P=handsOnKnees(P,root,yaw,s);
    return {P,root,yaw}; }
  if(t<TL.grab){ const u=sstep(TL.stand0,TL.grab,t);              // gets up into a crouch, reaches for the chain
    yaw=lerp(SIT_YAW,PULL_YAW,u); const g=chainRestPoint(S1);
    P=blend(handsOnKnees(SIT0,root,SIT_YAW,0),{...CROUCH,tL:g.clone().add(rotY(V(0,0,0.06),PULL_YAW)),tR:g.clone().add(rotY(V(0,0,-0.06),PULL_YAW)),wL:1,wR:1},sm5(u));
    root=SEAT.clone().lerp(PULL_ROOT(2.6),u*0.3); return {P,root,yaw}; }
  yaw=PULL_YAW; const g=gripAt(t), side=rotY(V(0,0,1),yaw);
  const handsOn=1-sstep(TL.release-0.02,TL.release+0.1,t);
  if(t<2.6){ const u=sm5(sstep(TL.grab,2.6,t));                 // rises with the chain in his hands
    P=blend(CROUCH,pullPose(t),u); root=SEAT.clone().lerp(PULL_ROOT(2.6),0.3+0.7*u); }
  else if(t<TL.release+0.15){ P=pullPose(t); root=PULL_ROOT(t); }
  else if(t<TL.sitDown-0.5){ const u=sm5(sstep(TL.release+0.15,TL.release+0.45,t)); P=blend(pullPose(TL.release+0.15),HUNCH,u); root=PULL_ROOT(TL.release+0.15); }
  else { const u=sstep(TL.sitDown-0.5,TL.sitDown+0.02,t);           // turns and drops down to the floor
    yaw=lerp(PULL_YAW,SIT_YAW,sm5(sstep(TL.sitDown-0.5,TL.sitDown-0.15,t)));
    const sit=handsOnKnees(SIT0,SEAT,SIT_YAW,0);
    P=blend(HUNCH,sit,Math.pow(u,1.6)); P.dy+= -0.03*Math.sin(Math.PI*clamp((t-TL.sitDown)/0.25))*(t>TL.sitDown?1:0);
    root=PULL_ROOT(TL.release+0.15).lerp(SEAT,u); }
  if(handsOn>0&&t<TL.release+0.12){ const tg={tL:g.clone().addScaledVector(side,0.05),tR:g.clone().addScaledVector(side,-0.05),wL:handsOn,wR:handsOn,pL:V(-0.2,-1,0.5),pR:V(-0.2,-1,-0.5)}; P={...P,...tg}; }
  return {P,root,yaw}; }
const ankleOf=J=>J.fR.clone().addScaledVector(J.kR.clone().sub(J.fR).normalize(),0.075);

// ---------------------------------------------------------------- the chain: parabolic sag, lies on the floor, sideways slack on the floor
function sagCurve(A,B,len,n=72){
  const D=B.clone().sub(A); const dist=D.length(); let side=V(-D.z,0,D.x); if(side.lengthSq()<1e-8) side.set(0,0,1); side.normalize(); if(side.z<0) side.negate();
  const build=(d,w)=>{ const p=[]; for(let i=0;i<=n;i++){ const s=i/n; const v=A.clone().lerp(B,s); v.y-=4*d*s*(1-s); v.addScaledVector(side,w*Math.pow(Math.sin(Math.PI*s),1.3)*(1+0.18*Math.sin(s*9.0))); v.y=Math.max(v.y,LINK_Y); p.push(v); } return p; };
  const lenOf=p=>{ let s=0; for(let i=1;i<p.length;i++) s+=p[i].distanceTo(p[i-1]); return s; };
  if(dist>=len*0.9995) return build(0,0);
  if(lenOf(build(6,0))>=len){ let lo=0,hi=6; for(let k=0;k<26;k++){ const m=(lo+hi)/2; if(lenOf(build(m,0))<len) lo=m; else hi=m; } return build(hi,0); }
  let lo=0,hi=1.5; for(let k=0;k<26;k++){ const m=(lo+hi)/2; if(lenOf(build(6,m))<len) lo=m; else hi=m; } return build(6,hi); }
// sample link centres and tangents every PITCH along a polyline
function sampleLinks(poly){ const cum=[0]; for(let i=1;i<poly.length;i++) cum.push(cum[i-1]+poly[i].distanceTo(poly[i-1]));
  const out=[]; let j=1; for(let k=0;k<NL;k++){ const s=Math.min((k+0.5)*PITCH,cum[cum.length-1]-1e-5); while(j<cum.length-1&&cum[j]<s) j++;
    const u=(s-cum[j-1])/Math.max(1e-6,cum[j]-cum[j-1]); out.push({p:poly[j-1].clone().lerp(poly[j],u),d:poly[j].clone().sub(poly[j-1]).normalize()}); } return out; }
const SEAT_ANKLE=(()=>{ const P=handsOnKnees(SIT0,SEAT,SIT_YAW,0); return ankleOf(skel(P,SEAT,SIT_YAW)); })();
function chainRestPoint(s){ const poly=sagCurve(lockLinkPoint(TL.stand0),SEAT_ANKLE,CHAIN_LEN); let acc=0; for(let i=1;i<poly.length;i++){ const d=poly[i].distanceTo(poly[i-1]); if(acc+d>=s) return poly[i-1].clone().lerp(poly[i],(s-acc)/d); acc+=d; } return poly[poly.length-1].clone(); }
function chainAt(t,ankle){ const A=lockLinkPoint(t);
  const single=()=>sagCurve(A,ankle,CHAIN_LEN);
  const double=()=>{ const g=gripAt(t); const a=sagCurve(A,g,S1), b=sagCurve(g,ankle,CHAIN_LEN-S1); return a.concat(b.slice(1)); };
  const held=t>=TL.grab&&t<TL.release;
  let links=sampleLinks(held?double():single());
  const mixWith=(other,u)=>{ const o=sampleLinks(other); links=links.map((l,i)=>({p:l.p.clone().lerp(o[i].p,u),d:l.d.clone().lerp(o[i].d,u).normalize()})); };
  if(held&&t<TL.grab+0.12) mixWith(single(),1-sstep(TL.grab,TL.grab+0.12,t));
  if(!held&&t>=TL.release&&t<TL.chainLand){ const u=sstep(TL.release,TL.chainLand,t);   // falls from his hands: drop under gravity, then settle
    const g=gripAt(TL.release); const a=sagCurve(A,g,S1), b=sagCurve(g,ankle,CHAIN_LEN-S1); const from=sampleLinks(a.concat(b.slice(1)));
    links=from.map((l,i)=>{ const to=links[i]; const p=l.p.clone().lerp(to.p,u*u); return {p,d:l.d.clone().lerp(to.d,u).normalize()}; }); }
  return links; }
const linkMesh=new THREE.InstancedMesh(new THREE.TorusGeometry(0.021,0.0085,10,28),dustify(IRON(),'chain',true),NL);
linkMesh.castShadow=true; linkMesh.receiveShadow=true; linkMesh.frustumCulled=false; scene.add(linkMesh);
const _M=new THREE.Matrix4(), _B=new THREE.Matrix4();
function drawChain(links){ links.forEach((l,k)=>{ const X=l.d.clone(); let up=UPV.clone().addScaledVector(X,-X.dot(UPV)); if(up.lengthSq()<1e-6) up=V(0,0,1).addScaledVector(X,-X.z); up.normalize();
    const Z=(k%2===0)?up:X.clone().cross(up).normalize(); const Y=Z.clone().cross(X).normalize();
    _B.makeBasis(X,Y,Z); _B.scale(V(1.55,1,1)); _B.setPosition(l.p.x,Math.max(l.p.y,k%2===0?0.0085:0.022),l.p.z); linkMesh.setMatrixAt(k,_B); });
  linkMesh.instanceMatrix.needsUpdate=true; }

// ---------------------------------------------------------------- the others: slate grey strangers walking through the beam, fading into the dark
// [start time, x0, x1, z, speed m/s, glances back]
const WALK=[[5.05,2.7,-2.8,-0.95,1.15,1],[6.15,-2.9,2.9,-1.9,1.55,0],[6.95,3.0,-3.0,-3.1,2.1,0],[7.6,-2.9,2.9,-1.25,2.7,0],[8.2,3.0,-3.0,-2.5,3.3,0],[8.65,-3.0,3.0,-1.6,4.0,0],[9.05,3.2,-3.2,-3.6,4.6,0],[9.35,-3.1,3.1,-1.1,5.4,0]];
const walkers=WALK.map((w,i)=>{ const f=makeFig(SLATE,'walker'+i,0.08,0x9fb2d6); f.mat.transparent=true; return {w,f}; });
const GL0=6.05, GL1=7.25;   // walker 1 slows and looks back at him
function walkerAt(m,t){ const [t0,x0,x1,z,v,gl]=m.w; const dir=Math.sign(x1-x0);
  if(t<t0-0.01) return null;
  const n=40; let d=0; const tt=t-t0; for(let i=0;i<n;i++){ const ti=t0+(i+0.5)/n*tt; const b=gl?sstep(GL0,GL0+0.4,ti)*(1-sstep(GL1-0.4,GL1,ti)):0; d+=v*(1-0.5*b)*tt/n; }
  const x=x0+dir*d; if(dir*(x-x1)>0) return null;
  const b=gl?sstep(GL0,GL0+0.45,t)*(1-sstep(GL1-0.45,GL1,t)):0;
  const P=gait({...P0,p:0.08,tilt:0.05,ty:-0.55*b*dir,hy:-0.5*b*dir},d/1.3*2*Math.PI,1,0.34,0.62,0.24);
  const T=Math.abs(x1-x0)/v, left=Math.abs(x1-x)/v;   // fade up out of the void, then back into it (about 2 s when the walk allows)
  const al=sstep(0,Math.min(1.6,0.4*T),tt)*sstep(0,Math.min(2.0,0.45*T),left);
  return {P,root:V(x,0,z),yaw:dir>0?0:Math.PI,ph:d/1.3*2*Math.PI,a:al}; }

const NOREFL=[];   // additive haze is not mirrored by the floor (it washed the foreground out)
{ const ob=refl.onBeforeRender; refl.onBeforeRender=function(...a){ NOREFL.forEach(o=>o.visible=false); ob.apply(this,a); NOREFL.forEach(o=>o.visible=true); }; }
// ---------------------------------------------------------------- the beam: volumetric cone with drifting haze, plus dust motes
const beamU={uT:{value:0},uI:{value:1},uApex:{value:LAMP},uAxis:{value:LAMP_T.clone().sub(LAMP).normalize()},uTan:{value:Math.tan(CONE)},uCol:{value:GOLD.clone()}};
{ const h=LAMP.distanceTo(LAMP_T)+0.02, r=Math.tan(CONE)*h*1.02;
  const g=new THREE.CylinderGeometry(0.02,r,h,96,24,true); g.translate(0,-h/2,0);
  const m=new THREE.Mesh(g,new THREE.ShaderMaterial({uniforms:beamU,transparent:true,depthWrite:false,side:THREE.DoubleSide,blending:THREE.AdditiveBlending,fog:false,
    vertexShader:`varying vec3 vW; void main(){ vec4 w=modelMatrix*vec4(position,1.0); vW=w.xyz; gl_Position=projectionMatrix*viewMatrix*w; }`,
    fragmentShader:`varying vec3 vW; uniform vec3 uApex,uAxis,uCol; uniform float uT,uI,uTan;
      float h(vec3 p){ return fract(sin(dot(p,vec3(12.9898,78.233,37.719)))*43758.5453); }
      float n3(vec3 p){ vec3 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f);
        return mix(mix(mix(h(i),h(i+vec3(1,0,0)),f.x),mix(h(i+vec3(0,1,0)),h(i+vec3(1,1,0)),f.x),f.y),mix(mix(h(i+vec3(0,0,1)),h(i+vec3(1,0,1)),f.x),mix(h(i+vec3(0,1,1)),h(i+vec3(1,1,1)),f.x),f.y),f.z); }
      // integrate the cone's density along the view ray (16 steps between the near and far wall)
      void main(){ vec3 ro=cameraPosition, rd=normalize(vW-cameraPosition); float tEnd=length(vW-cameraPosition);
        float acc=0.0; float t0=0.0; float t1=tEnd;
        for(int i=0;i<16;i++){ float s=mix(t0,t1,(float(i)+0.5)/16.0); vec3 p=ro+rd*s; vec3 q=p-uApex; float ax=dot(q,uAxis); if(ax<=0.0) continue;
          float rr=length(q-uAxis*ax), rc=ax*uTan; float cone=pow(smoothstep(rc,rc*0.15,rr),1.6);
          float fl=smoothstep(0.0,0.35,p.y);                                    // fades into the floor
          float hz=0.62+0.55*n3(p*vec3(2.2,0.9,2.2)+vec3(0.0,-uT*0.05,uT*0.03))+0.25*n3(p*6.0+vec3(uT*0.08,0.0,0.0));
          acc+=cone*fl*hz/(0.6+ax*0.55); }
        acc*=(t1-t0)/16.0; gl_FragColor=vec4(uCol*acc*uI*${BEAMK.toFixed(4)},1.0); }`}));
  m.position.copy(LAMP); m.quaternion.setFromUnitVectors(V(0,-1,0),LAMP_T.clone().sub(LAMP).normalize()); m.frustumCulled=false; m.renderOrder=5; scene.add(m);
  m.material.side=THREE.BackSide; NOREFL.push(m); }   // back faces only: one ray integration per pixel, also from inside the cone
// motes: world-fixed, drifting slowly; bright inside the cone, dim outside
const moteU={uT:{value:0},uH:{value:H},uApex:{value:LAMP},uAxis:{value:beamU.uAxis.value},uTan:{value:Math.tan(CONE)},uCol:{value:new THREE.Color(1.0,0.85,0.62)},uOp:{value:1}};
{ const N=1700, Rn=rng(21), pos=new Float32Array(N*3), sd=new Float32Array(N);
  for(let i=0;i<N;i++){ const a=Rn()*6.283, r=Math.sqrt(Rn())*2.1; pos[i*3]=-0.2+Math.cos(a)*r; pos[i*3+1]=Rn()*3.4; pos[i*3+2]=Math.sin(a)*r; sd[i]=Rn(); }
  const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.BufferAttribute(pos,3)); g.setAttribute('seed',new THREE.BufferAttribute(sd,1));
  const m=new THREE.Points(g,new THREE.ShaderMaterial({uniforms:moteU,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
    vertexShader:`attribute float seed; uniform float uT,uH,uTan; uniform vec3 uApex,uAxis; varying float vA;
      void main(){ vec3 p=position; float s=seed*6.283;
        p.y=mod(p.y-uT*(0.015+0.02*seed)+3.4,3.4); p.x+=0.06*sin(uT*0.37+s)+0.03*sin(uT*0.9+s*2.0); p.z+=0.06*cos(uT*0.31+s*1.3);
        vec3 q=p-uApex; float ax=dot(q,uAxis); float rr=length(q-uAxis*ax), rc=max(ax,0.0)*uTan;
        vA=smoothstep(rc*1.05,rc*0.5,rr)*(0.35+0.65*fract(seed*7.13))*(0.75+0.25*sin(uT*(1.0+seed*2.0)+s));
        vec4 mv=modelViewMatrix*vec4(p,1.0); gl_Position=projectionMatrix*mv;
        float sz=(0.0055+0.006*fract(seed*3.7))*uH/(-mv.z)*1.6; gl_PointSize=clamp(sz,1.0,26.0); vA*=clamp(1.6/sz,0.08,1.0)*min(1.0,sz); }`,
    fragmentShader:`uniform vec3 uCol; uniform float uOp; varying float vA; void main(){ vec2 c=gl_PointCoord-0.5; float d=length(c); float a=smoothstep(0.5,0.0,d); gl_FragColor=vec4(uCol*a*vA*uOp*0.9,1.0); }`}));
  m.frustumCulled=false; scene.add(m); NOREFL.push(m); }
// dust puffs: kicked up by the snaps, the chain landing and him sitting down
const PUFFS=[]; const puffU={uT:{value:0},uH:{value:H}};
function addPuff(at,t0,n,spread,vel,seed,amp=1){ const Rn=rng(seed); for(let i=0;i<n;i++){ const a=Rn()*6.283; const r=Math.sqrt(Rn())*spread;
  PUFFS.push([at.x+Math.cos(a)*r,Math.max(0.01,at.y+Rn()*0.03),at.z+Math.sin(a)*r, Math.cos(a)*vel*(0.4+Rn()),vel*(0.25+0.9*Rn()),Math.sin(a)*vel*(0.4+Rn()), t0+Rn()*0.06, (0.6+Rn())*amp]); } }
{ const base=V(POST.x,0.02,POST.z).addScaledVector(DR,0.12);
  addPuff(base,TL.snap1,70,0.12,0.5,1); addPuff(base,TL.snap2,110,0.16,0.65,2,1.2); addPuff(APEX.clone().setY(0.3),TL.snap2,30,0.05,0.25,3,0.7);
  // along the chain on the floor where it slaps down
  const rest=sagCurve(lockLinkPoint(TL.chainLand+0.1),SEAT_ANKLE,CHAIN_LEN); for(let k=10;k<rest.length-6;k+=6) addPuff(rest[k].clone().setY(0.02),TL.chainLand-0.02+k*0.0008,8,0.04,0.28,40+k,0.8);
  addPuff(SEAT.clone().setY(0.02),TL.sitDown,90,0.3,0.45,7,1.0);
  const g=new THREE.BufferGeometry(); const A=new Float32Array(PUFFS.length*3), B=new Float32Array(PUFFS.length*4), C=new Float32Array(PUFFS.length);
  PUFFS.forEach((p,i)=>{ A.set(p.slice(0,3),i*3); B.set([p[3],p[4],p[5],p[6]],i*4); C[i]=p[7]; });
  g.setAttribute('position',new THREE.BufferAttribute(A,3)); g.setAttribute('vel',new THREE.BufferAttribute(B,4)); g.setAttribute('amp',new THREE.BufferAttribute(C,1));
  const m=new THREE.Points(g,new THREE.ShaderMaterial({uniforms:puffU,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
    vertexShader:`attribute vec4 vel; attribute float amp; uniform float uT,uH; varying float vA;
      void main(){ float tau=uT-vel.w; vA=0.0; vec3 p=position; float sz=1.0;
        if(tau>0.0&&tau<2.6){ float k=3.2; float s=(1.0-exp(-k*tau))/k; p+=vel.xyz*s; p.y+=0.03*tau; p.y=max(p.y,0.005);
          vA=amp*exp(-tau/0.75)*smoothstep(0.0,0.05,tau); sz=0.012+0.05*tau; }
        vec4 mv=modelViewMatrix*vec4(p,1.0); gl_Position=projectionMatrix*mv; gl_PointSize=clamp(sz*uH/(-mv.z),1.0,90.0); }`,
    fragmentShader:`varying float vA; void main(){ float d=length(gl_PointCoord-0.5); float a=smoothstep(0.5,0.0,d); gl_FragColor=vec4(vec3(0.85,0.72,0.52)*a*a*vA*0.16,1.0); }`}));
  m.frustumCulled=false; scene.add(m); }

// ---------------------------------------------------------------- camera
// 0-5 slow push-in; 5-10 slow pull-out as the years pass; 10-12.75 log push-in to the padlock; cut at 13.0 to the wide; 13-16 ends where frame 0 starts
const WA0={p:V(0.06,0.8,5.6),l:V(-0.02,0.5,0)}, WA5={p:V(0.24,0.84,5.3),l:V(0.2,0.66,0)};
const WB10={p:V(0.0,1.05,6.9),l:V(-0.08,0.62,-0.7)};
const WD13={p:V(0.03,0.82,5.95),l:V(-0.02,0.5,0)};
const LOCKC=(t=0)=>onPost(APEX,t).add(V(0,-0.085*LS,0));
const CLOSE={off:V(0.12,0.08,0.66).applyQuaternion(lockPose(12.75).q)};
function camAt(t){
  if(t<5){ const u=t/5; return {p:WA0.p.clone().lerp(WA5.p,u),l:WA0.l.clone().lerp(WA5.l,u)}; }
  if(t<TL.pushIn0){ const u=sm5((t-5)/(TL.pushIn0-5)); return {p:WA5.p.clone().lerp(WB10.p,u),l:WA5.l.clone().lerp(WB10.l,u)}; }
  if(t<TL.cut){ const u=sm5(clamp((t-TL.pushIn0)/(TL.pushIn1-TL.pushIn0))); const lc=LOCKC();
    const l=WB10.l.clone().lerp(lc,Math.pow(u,0.55)); const d0=WB10.p.distanceTo(WB10.l), d1=CLOSE.off.length();
    const dir=WB10.p.clone().sub(WB10.l).normalize().lerp(CLOSE.off.clone().normalize(),Math.pow(u,0.8)).normalize();
    const d=Math.exp(lerp(Math.log(d0),Math.log(d1),u)); const drift=Math.max(0,t-TL.pushIn1)*0.012;
    return {p:l.clone().addScaledVector(dir,d-drift),l}; }
  const u=(t-TL.cut)/(DUR-TL.cut); return {p:WD13.p.clone().lerp(WA0.p,u),l:WD13.l.clone().lerp(WA0.l,u)}; }
const shakeAt=t=>{ let s=0; for(const [t0,a] of [[TL.snap1,0.6],[TL.snap2,1.0],[TL.sitDown,0.35]]) if(t>t0) s+=a*Math.exp(-(t-t0)/0.12); return s; };

// ---------------------------------------------------------------- post
const composer=new EffectComposer(renderer); composer.setSize(W,H);
composer.addPass(new RenderPass(scene,cam));
const bloom=new UnrealBloomPass(new THREE.Vector2(W,H),0.45,0.6,0.88); composer.addPass(bloom);
const gradePass=new ShaderPass({uniforms:{tDiffuse:{value:null},uT:{value:0},uAsp:{value:W/H}},vertexShader:`varying vec2 vU; void main(){ vU=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
 fragmentShader:`varying vec2 vU; uniform sampler2D tDiffuse; uniform float uT,uAsp;
  float h(vec2 p){ return fract(sin(dot(p,vec2(12.9898,78.233))+uT*37.0)*43758.5453); }
  void main(){ vec2 c=vU-0.5; float r2=dot(c*vec2(uAsp,1.0),c*vec2(uAsp,1.0));
   vec3 col=texture2D(tDiffuse,vU).rgb; col=vec3(1.0)-exp(-1.15*col);
   float vig=1.0-smoothstep(0.06,0.42,r2)*0.62; col*=vig;
   col+=vec3(0.0006,0.0010,0.0028)*smoothstep(0.08,0.45,r2);                 // faint navy in the corners (linear: tiny values)
   col+=(h(vU*vec2(uAsp,1.0)*900.0)-0.5)*0.006*(0.3+col);
   gl_FragColor=vec4(max(col,0.0),1.0);} `});
composer.addPass(gradePass); const GU=gradePass.uniforms;
composer.addPass(new OutputPass());

// ---------------------------------------------------------------- one sub-frame
function setT(t){
  dustU.uDust.value=dustAt(t);
  const h=heroAt(t); const Jh=skel(h.P,h.root,h.yaw); poseFig(hero,Jh);
  const ankle=ankleOf(Jh); cuff.position.copy(ankle); cuff.quaternion.setFromUnitVectors(V(0,0,1),Jh.kR.clone().sub(Jh.fR).normalize());
  drawChain(chainAt(t,ankle));
  const L=lockPose(t); lockG.position.copy(L.p); lockG.quaternion.copy(L.q);
  const close=t<TL.cut?sstep(TL.pushIn0+0.6,TL.pushIn1-0.3,t):0;   // 0 in the wide shots (lock half in shadow), 1 in the close-up
  const lc=LOCKC(t); lockLight.position.copy(lc).add(V(0.05,0.0,0.08)); lockLight.intensity=lerp(0.012,0.06,close); lockMat.emissiveIntensity=lerp(0.05,0.22,close);
  lockGlow.position.copy(lc); lockGlow.scale.setScalar(0.32); lockGlow.material.opacity=lerp(0.025,0.16,close);
  lockG.updateMatrixWorld(true);
  const gapW=V(0,-0.055,0).add(V(LOCK.leg+0.004,0,0)); const gw=lockIn.localToWorld(gapW.clone());
  const gl=sstep(TL.glint-0.2,TL.glint+0.1,t)*(1-sstep(TL.glint+0.25,TL.glint+0.9,t)); glint.position.copy(gw); glint.scale.setScalar(0.05+0.03*gl); glint.material.opacity=0.8*gl;
  shk.children[1].getWorldPosition(tipLight.position); tipLight.scale.setScalar(0.035); tipLight.material.opacity=0.32*(1-close);   // catch-light on the free tip: the rewatch hint
  for(const m of walkers){ const w=walkerAt(m,t); const vis=!!w&&w.a>0.004; m.f.bones.concat(m.f.joints,[m.f.head]).forEach(o=>{ o.visible=vis; o.castShadow=vis&&w.a>0.5; }); if(vis){ m.f.mat.opacity=w.a; poseFig(m.f,skel(w.P,w.root,w.yaw)); } }
  const c=camAt(t); cam.position.copy(c.p); cam.lookAt(c.l); cam.updateProjectionMatrix();
  const sh=shakeAt(t); if(sh>0){ cam.rotateX(0.006*sh*Math.sin(t*131.0)); cam.rotateY(0.006*sh*Math.sin(t*97.0+1.3)); }
  const pay=t>=TL.cut?0.14*sstep(TL.look0,TL.look1,t):0;      // the gold payoff: the lamp lifts a little as he looks
  spot.intensity=SPOT_I*(1+pay); beamU.uI.value=1+pay*1.2; beamU.uT.value=t; moteU.uT.value=t; puffU.uT.value=t; GU.uT.value=t;
  return {Jh}; }
const acc=document.createElement('canvas'); acc.width=W; acc.height=H; const actx=acc.getContext('2d');
const CUTS=[0,TL.cut,DUR];
window.renderAt=function(t,Ksub=3){
  const s=t<TL.cut?0:1, t0=CUTS[s], t1=CUTS[s+1]-1e-4; const shutter=(t>7.5&&t<10)?1/30:1/60;   // time-lapse walkers get a longer shutter
  if([TL.snap1,TL.snap2,TL.sitDown].some(x=>t>x-0.05&&t<x+0.3)) Ksub=Math.max(Ksub,7);   // smooth blur on the jolts
  actx.globalAlpha=1; actx.clearRect(0,0,W,H);
  for(let k=0;k<Ksub;k++){ const tt=clamp(t+(Ksub>1?(k/(Ksub-1)-0.5)*shutter:0),t0,t1); setT(tt); renderer.shadowMap.needsUpdate=true; composer.render(); actx.globalAlpha=1/(k+1); actx.drawImage(renderer.domElement,0,0); }
  return acc.toDataURL('image/jpeg',0.95); };
// screen positions and numbers for the overlay and the sound
const proj=v=>{ const p=v.clone().project(cam); return [p.x*0.5+0.5,0.5-p.y*0.5,p.z<1?1:0]; };
window.metaAt=function(t){ const S=setT(t); cam.updateMatrixWorld();
  return {t,year:yearAt(t),slump:slumpAt(t),dust:dustAt(t),lock:proj(LOCKC()),hero:proj(S.Jh.head),walkers:walkers.map(m=>{ const w=walkerAt(m,t); return w?[w.root.x,w.root.z,w.ph]:null; })}; };
window.events={...TL,HMAX};
window.ready=true;
