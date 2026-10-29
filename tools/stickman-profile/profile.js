// Stickman profile photo, 29 Oct 2026. The sleep-reel hero (near-black pictogram, warm rim, thin stick limbs, floating head,
// glowing face.js face) as a 1080x1080 bust portrait on a dark-warm backdrop. Head sits inside the central circle for the IG crop.
// ?v=smile|wide|sleepy|laugh picks the expression and arm pose. renderAt(t) is pure, t only drifts the dust.
import * as THREE from 'three';
import * as SLD from './sld.js';
import {createFace,EX,NEUTRAL} from './face.js';
const {V}=SLD;
const q=new URLSearchParams(location.search); const W=+q.get('w')||1080, H=+q.get('h')||1080, VAR=q.get('v')||'smile';
const ST=SLD.createStage({W,H,lamp:V(0.35,4.2,1.6),lampTarget:V(0,1.35,0),cone:0.2,spot:34,beam:0.05,fov:26,motes:900});
const scene=ST.scene; const R=SLD.createRig(scene);
scene.background=new THREE.Color(0x120c0a); scene.fog=new THREE.FogExp2(0x120c0a,0.03);

// backdrop: warm charcoal wall with a soft lamp glow behind the head (never pure black)
{ const c=document.createElement('canvas'); c.width=c.height=1024; const g=c.getContext('2d');
  const gr=g.createRadialGradient(512,430,30,512,500,620); gr.addColorStop(0,'#6b4128'); gr.addColorStop(0.35,'#3a2519'); gr.addColorStop(0.75,'#1c1310'); gr.addColorStop(1,'#110c0b');
  g.fillStyle=gr; g.fillRect(0,0,1024,1024); const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace;
  const m=new THREE.Mesh(new THREE.PlaneGeometry(5,5),new THREE.MeshBasicMaterial({map:t,fog:false})); m.position.set(0,1.45,-1.6); scene.add(m); }

// hero, same build as tools/sleep-reel/scene.js
const hero=R.makeFig(0x0d0b0a,'hero',{rim:0.6,rimCol:0xffc27a,lift:0.0});
const PT={len:0.58,hipR:0.07,shR:0.132,capB:0.05,capT:0.075,limb:0.024};
const HEADR=0.165;
hero.bones[0].geometry=(()=>{ const pts=[], L=PT.len, N=14;
  for(let k=0;k<=N;k++){ const a=k/N*Math.PI/2; pts.push(new THREE.Vector2(PT.hipR*Math.sin(a), (PT.capB*(1-Math.cos(a)))/L-0.5)); }
  for(let k=1;k<N;k++){ const u=k/N, y=PT.capB+u*(L-PT.capB-PT.capT); pts.push(new THREE.Vector2(PT.hipR+(PT.shR-PT.hipR)*Math.pow(u,1.4), y/L-0.5)); }
  for(let k=0;k<=N;k++){ const a=k/N*Math.PI/2; pts.push(new THREE.Vector2(PT.shR*Math.cos(a)**0.6, (L-PT.capT+PT.capT*Math.sin(a))/L-0.5)); }
  const g=new THREE.LatheGeometry(pts,40); g.computeVertexNormals(); return g; })();
const FACE=createFace(scene);
function boneTo(m,a,b,r){ const d=b.clone().sub(a); const len=Math.max(d.length(),1e-4); m.position.copy(a).add(b).multiplyScalar(0.5); m.scale.set(r,len,r); m.quaternion.setFromUnitVectors(SLD.UPV,d.multiplyScalar(1/len)); m.visible=true; }
const ball=(m,p,r)=>{ m.position.copy(p); m.scale.setScalar(r); m.visible=true; };

// upright body: hip, lean (toward camera, rad), roll (sideways tilt), nod, turn, tilt (head roll), hand targets tL/tR
function bodyJ(o){ const d=V(Math.sin(o.roll||0),Math.cos(o.roll||0),0).applyAxisAngle(V(1,0,0),o.lean||0).normalize();
  const n=V(0,0,1).applyAxisAngle(V(1,0,0),o.lean||0); const l=d.clone().cross(n).normalize();
  const J={hip:o.hip.clone(),d,n,l}; J.neck=J.hip.clone().addScaledVector(d,PT.len);
  let hd=d.clone().applyAxisAngle(n,o.tilt||0); const nod=o.nod||0; hd=hd.multiplyScalar(Math.cos(nod)).addScaledVector(n,Math.sin(nod)).normalize();
  let f=n.clone().multiplyScalar(Math.cos(nod)).addScaledVector(d,-Math.sin(nod)).normalize(); f=f.applyAxisAngle(hd,o.turn||0);
  J.head=J.neck.clone().addScaledVector(hd,0.045+HEADR); J.hd=hd; J.f=f;
  for(const [s,sg] of [['L',1],['R',-1]]){ const S=J.neck.clone().addScaledVector(d,-0.075).addScaledVector(l,sg*0.125); J['sh'+s]=S;
    const T=o['t'+s]||J.hip.clone().addScaledVector(l,sg*0.2).addScaledVector(n,0.05);
    const r=R.ik(S,T,o['p'+s]||l.clone().multiplyScalar(sg).addScaledVector(d,-0.6)); J['el'+s]=r.E; J['h'+s]=r.Hd; }
  return J; }
function poseHero(J){ const B_=hero.bones, Jt=hero.joints, r=PT.limb; hero.all.forEach(m=>m.visible=false);
  const ax=J.d, a=J.hip.clone().addScaledVector(ax,-PT.capB), b=J.neck.clone().addScaledVector(ax,0.012), dd=b.clone().sub(a), len=dd.length();
  const T=B_[0]; T.position.copy(a).add(b).multiplyScalar(0.5); T.scale.set(1,len,1); T.quaternion.setFromUnitVectors(V(0,1,0),dd.normalize()); T.visible=true;
  boneTo(B_[5],J.shL,J.elL,r); boneTo(B_[6],J.elL,J.hL,r); boneTo(B_[7],J.shR,J.elR,r); boneTo(B_[8],J.elR,J.hR,r);
  ball(Jt[6],J.shL,r*1.6); ball(Jt[7],J.shR,r*1.6); ball(Jt[8],J.elL,r*1.05); ball(Jt[9],J.elR,r*1.05); ball(Jt[10],J.hL,r*1.45); ball(Jt[11],J.hR,r*1.45);
  ball(hero.head,J.head,HEADR); FACE.place(J.head,J.f,J.hd,HEADR); }

// variations: expression + body. l = viewer's right (+x) for the L side.
const HIP=V(0,0.92,0);
const nk=HIP.clone().add(V(0,PT.len,0));
const VARS={
  smile: {ex:{...EX.delight,mc:0.95,mw:1.0,blush:0.6}, o:{hip:HIP,tilt:-0.12,turn:0.06,
           tL:nk.clone().add(V(0.25,0.22,0.12)),pL:V(0.5,-1,0.2)}},                                    // waving hello
  wide:  {ex:{...EX.frozen,mo:0.45,mO:1,mc:0,mw:0.6,es:1.3,pr:0.24,by:0.8,ba:0.3}, o:{hip:HIP,lean:0.06,tilt:0.05,
           tL:nk.clone().add(V(0.16,0.17,0.12)),tR:nk.clone().add(V(-0.16,0.17,0.12)),pL:V(0.35,-1,0.8),pR:V(-0.35,-1,0.8)}}, // hands up to the cheeks
  sleepy:{ex:{...EX.sleepy,eo:0.22,mo:0.45,mO:0.85,mw:0.55,by:-0.1,ba:0.35,pr:0.46,py:-0.2}, o:{hip:HIP,tilt:0.22,nod:0.08,
           tR:nk.clone().add(V(-0.13,0.23,0.17)),pR:V(-0.3,-1,0.8)}, zzz:true},                           // head tilted, yawning, fist rubbing an eye
  laugh: {ex:{...EX.laugh,tear:0.8,mo:0.7,mw:1.1}, o:{hip:HIP,tilt:-0.08,lean:-0.05,
           tL:HIP.clone().add(V(0.12,0.2,0.16)),tR:HIP.clone().add(V(-0.12,0.2,0.16))}},              // holding the belly
};
const VV=VARS[VAR]||VARS.smile;

// sleepy Zzz: glowing cream letters beside the head
const Zs=[]; if(VV.zzz){ const c=document.createElement('canvas'); c.width=c.height=128; const g=c.getContext('2d'); g.font='bold 110px "DejaVu Sans", sans-serif'; g.textAlign='center'; g.textBaseline='middle'; g.shadowColor='rgba(255,226,180,0.9)'; g.shadowBlur=12; g.fillStyle='#fff0d4'; g.fillText('z',64,64);
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace;
  [[0.21,0.06,0.05],[0.27,0.13,0.065],[0.33,0.22,0.08]].forEach(([x,y,s])=>{ const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:t,transparent:true,fog:false,depthWrite:false})); sp.scale.setScalar(s); sp.userData={x,y}; scene.add(sp); Zs.push(sp); }); }

const J=bodyJ(VV.o);
const LOOK=J.head.clone().add(V(0,-0.12,0));
function setT(t){ FACE.draw({...NEUTRAL,...VV.ex}); poseHero(J);
  Zs.forEach(z=>z.position.copy(J.head).add(V(z.userData.x,z.userData.y,0.05)));
  ST.tick(t,0); ST.cam.position.copy(LOOK).add(V(0,0.04,1.75)); ST.cam.fov=26; ST.cam.updateProjectionMatrix(); ST.cam.lookAt(LOOK); }
window.renderAt=(t,K=1)=>ST.renderAt(setT,t,K,{shutter:0});
window.events={VAR}; window.ready=true;
