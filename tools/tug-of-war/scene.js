// Tug of War (Slow Light Dark). A cream stickman strains on a thick rope under the gold lamp. The rope runs off into the
// dark over a black pit; a red ribbon marks its centre. He gains a little, gets yanked back. The camera pans along the
// rope across the pit, a second lamp fades up, and the one pulling against him is himself: same figure, same pose, and
// DOUBT etched faintly in the floor under him. He stops pulling and lets go; the twin stumbles; the ribbon swings back
// to the centre of the pit. Hold.
//
// World units are metres, floor y = 0, camera on +z. The pit is the strip |x| < PIT, open all the way down.
// The rope is analytic while it is taut (pure function of t), then a verlet rope simulated ONCE at page load from the
// moment he eases off (deterministic, sampled at 600 Hz), so renderAt(t) stays pure for the parallel render workers.
import * as THREE from 'three';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
import * as SLD from './sld.js';
import TL from './timeline.json' with {type:'json'};
const {V,clamp,sstep,lerp,sm5,keys,rng,PAL}=SLD;

const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960, DUR=TL.duration;
const PIT=0.6, LX=1.55;                                   // pit half-width; lamps over x = -LX (hero) and +LX (twin)
const S=SLD.createStage({W,H,lamp:V(-LX,4.6,1.1),lampTarget:V(-LX+0.02,0,0),spot:50});   // spot 50 (series 60): the tight, close-lit standing figure clips otherwise
const {scene,cam}=S; const R=SLD.createRig(scene);

// ---------------------------------------------------------------- second lamp (over the twin): fades up during the pan
const spot2=new THREE.SpotLight(PAL.GOLD,0,0,S.CONE+0.08,0.85,1.2); spot2.position.set(LX,4.6,1.1); spot2.target.position.set(LX-0.02,0,0);
spot2.castShadow=true; spot2.shadow.mapSize.set(2048,2048); spot2.shadow.bias=-0.00025; spot2.shadow.normalBias=0.012; spot2.shadow.camera.near=1.5; spot2.shadow.camera.far=7;
scene.add(spot2,spot2.target);
const B2=SLD.addBeam(scene,S.NOREFL,{LAMP:spot2.position.clone(),LAMP_T:spot2.target.position.clone(),CONE:S.CONE,BEAMK:0.14,H,motes:1700,seed:57});
const lamp2At=t=>sm5(sstep(TL.lamp2On0,TL.lamp2On1,t));

// ---------------------------------------------------------------- the pit: floor and mirror split in two ledges, dark cliff faces, a lit lip
{ const ledge=s=>{ const g=new THREE.PlaneGeometry(30,60); g.translate(s*(PIT+15),0,0); return g; };   // plane is XY, rotated flat below
  const flat=mergeGeometries([ledge(-1),ledge(1)]);
  S.refl.geometry.dispose(); S.refl.geometry=flat.clone(); S.floor.geometry.dispose(); S.floor.geometry=flat;
  const wallMat=new THREE.MeshStandardMaterial({color:0x2c2c30,roughness:0.9,map:S.floor.material.map});
  for(const s of [-1,1]){ const w=new THREE.Mesh(new THREE.PlaneGeometry(60,5),wallMat); w.rotation.y=-s*Math.PI/2; w.position.set(s*PIT,-2.5,0); w.receiveShadow=true; scene.add(w);
    const lip=new THREE.Mesh(new THREE.BoxGeometry(0.03,0.02,60),new THREE.MeshStandardMaterial({color:0x5a5a60,roughness:0.7})); lip.position.set(s*(PIT+0.015),-0.004,0); lip.receiveShadow=true; scene.add(lip); } }

// ---------------------------------------------------------------- DOUBT, etched faintly in the floor under the twin (PIL-made alpha map)
const doubtMat=new THREE.MeshStandardMaterial({color:0x0c0c0e,roughness:0.95,transparent:true,opacity:0,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-2});
const doubtHi=new THREE.MeshStandardMaterial({color:0x9a8e7a,roughness:0.6,transparent:true,opacity:0,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-1});
{ const tl=new THREE.TextureLoader(); const tx=tl.load('doubt.png'), th=tl.load('doubt_hi.png'); doubtMat.alphaMap=tx; doubtHi.alphaMap=th; doubtMat.needsUpdate=doubtHi.needsUpdate=true;
  // stretched in depth so it reads from the low camera; text "up" points away from the camera (-z)
  for(const m of [doubtMat,doubtHi]){ const d=new THREE.Mesh(new THREE.PlaneGeometry(1.0,0.62),m); d.rotation.x=-Math.PI/2; d.position.set(LX-0.05,0.0015,0.5); d.renderOrder=2; scene.add(d); } }

// ---------------------------------------------------------------- figures
const hero=R.makeFig(PAL.CREAM,'hero',{rim:0.16,lift:0.07});
const twin=R.makeFig(PAL.CREAM,'twin',{rim:0.16,lift:0.07});
const {P0,POSES,skel,poseFig,blend,gait}=R;
// tug stance: both feet ahead of the hips, leaning back about 34 degrees, head forward with the effort
const PULL={...P0,p:-0.6,tilt:0.34,hy:0,ty:0.12,aL:0.9,kL:0.5,aR:0.5,kR:0.85,sL:0.5,sR:0.6,eL:0.5,eR:0.4};
const EASE={...P0,p:-0.12,tilt:0.18,ty:0.05,aL:0.45,kL:0.3,aR:0.15,kR:0.35,sL:0.45,sR:0.5,eL:0.5,eR:0.4};
const STAND={...POSES.stand,tilt:-0.04,sL:0.06,sR:-0.06,eL:0.12,eR:0.12};
const mirrorP=P=>{ const o={...P}; for(const [a,b] of [['aL','aR'],['kL','kR'],['sL','sR'],['eL','eR'],['tL','tR'],['wL','wR'],['pL','pR']]){ o[a]=P[b]; o[b]=P[a]; }
  if(o.pL) o.pL=V(o.pL.x,o.pL.y,-o.pL.z); if(o.pR) o.pR=V(o.pR.x,o.pR.y,-o.pR.z); return o; };
const mirX=v=>V(-v.x,v.y,v.z);

// ---------------------------------------------------------------- the struggle: rope shift u (+ = toward the twin), heaves and yanks
// He heaves (u goes down: he gains), the other end yanks (u jumps up: his feet skid toward the pit). Net: the ribbon edges toward him.
const UK=[[0,0],[0.45,-0.05],[0.55,-0.05],[0.68,0.03],[1.05,0.03],[1.45,-0.03],[1.6,-0.03],[1.74,0.05],[2.2,0.05],[2.6,-0.02],[2.75,-0.02],[2.9,0.07],
  [3.35,0.07],[3.95,-0.03],[4.3,-0.03],[4.95,-0.17],[5.15,-0.17],[5.32,-0.07],[6.05,-0.07],[6.55,-0.15],[6.9,-0.15],[7.45,-0.21],[9.0,-0.215],[10.6,-0.2],[11.4,-0.235],[12.85,-0.225]];
const uAt=t=>keys(UK,t);
const jolt=(t,t0,a)=>{ const x=t-t0; return x>0?a*(x/0.07)*Math.exp(1-x/0.07):0; };
const yankAt=t=>TL.yanks.reduce((s,y,i)=>s+jolt(t,y+0.04,i===3?1.25:0.9),0);
const heaveAt=t=>clamp(-(uAt(t+0.03)-uAt(t-0.03))/0.06*0.55,0,0.14);
const tremor=t=>0.011*Math.sin(2*Math.PI*7.3*t)+0.006*Math.sin(2*Math.PI*11.7*t+1.1);
// he eases off, then lets go
const easeAt=t=>sm5(sstep(TL.cut+0.25,TL.letGo,t));          // 12.85 -> 13.25
const freeAt=t=>sm5(sstep(TL.letGo,TL.letGo+0.5,t));
const GRIP_Y=0.98;
// grips (world): front hand on the span, rear hand 0.3 m back along the rope; the twin's are the mirror image shifted by u
function grips(t){ const u=uAt(Math.min(t,TL.cut+0.25)); const e=easeAt(t), j=yankAt(t);
  const hf=V(-1.3+u+0.13*e+0.03*j,GRIP_Y-0.07*e+0.012*j+0.004*Math.sin(2*Math.PI*7.3*t),0.0);
  const hr=hf.clone().add(V(-0.3,0.03,0.0));
  // the twin: mirror of the hero's grip at u = 0, moved along the rope by u; after the hero lets go he stumbles back
  const st=sstep(TL.stumble-0.05,TL.stumble+0.35,t), rr=sm5(sstep(TL.stumble+0.5,TL.settle,t));
  const tf=V(1.3+u+0.13*e+0.34*st*(1-rr)+0.1*rr,lerp(GRIP_Y-0.07*e-0.1*st,0.74,rr),0.0), tr=tf.clone().add(V(0.3,0.03,0));
  return {hf,hr,tf,tr,u}; }
const ROOT_OFF=0.04;     // pelvis root sits this far behind the front grip in the tug stance
function heroAt(t){ const G=grips(t); let P={...PULL}; const j=yankAt(t), hv=heaveAt(t);
  P.p+=-hv*0.6+0.24*j+tremor(t); P.kL+=0.3*j; P.aL+=0.12*j-0.1*hv; P.tilt+=0.1*j; P.hy=0.04*Math.sin(t*0.9);
  let root=V(G.hf.x-ROOT_OFF,0,0);
  const hold={tL:G.hr,tR:G.hf,wL:1,wR:1,pL:V(0.1,-1,0.7),pR:V(0.2,-1,-0.6)};
  P={...P,...hold};
  if(t>TL.cut+0.25){ P=blend(P,{...EASE,...hold},easeAt(t)); root=V(G.hf.x-ROOT_OFF-0.05*easeAt(t),0,0); }
  if(t>TL.letGo){ const f=freeAt(t); const rel={...STAND,tL:G.hr,tR:G.hf,wL:0,wR:0};
    P=blend({...EASE,...hold},rel,f); P.wL=P.wR=1-f;
    const back=0.12*sstep(TL.letGo,TL.letGo+0.6,t); root=V(grips(TL.letGo).hf.x-ROOT_OFF-0.05-back,0,0);
    if(t<TL.letGo+0.7){ const ph=sstep(TL.letGo+0.05,TL.letGo+0.6,t)*Math.PI; P=gait(P,ph,0.45*Math.sin(ph)); } }
  if(t>TL.letGo+0.6){ const br=0.012*Math.sin(2*Math.PI*0.25*(t-TL.letGo)); P.p+=br; P.tilt+=-0.06*sstep(TL.settle-0.6,TL.settle+0.6,t); }   // breathes; head lifts
  return {P,root,yaw:0}; }
function twinAt(t){ const G=grips(t);
  // until the hero eases off, the twin is the hero's mirror image, on its own grips
  const base=mirrorP({...PULL,p:PULL.p+tremor(t+0.37)-heaveAt(t)*0.6,hy:0.04*Math.sin(t*0.9+0.5)});
  const hold={tL:G.tf,tR:G.tr,wL:1,wR:1,pL:V(0.1,-1,0.7),pR:V(0.2,-1,-0.6)};
  let P={...base,...hold};
  let root=V(G.tf.x+ROOT_OFF,0,0);
  if(t>TL.cut+0.25){ const e=easeAt(t); P=blend(P,{...mirrorP(EASE),tL:G.tf,tR:G.tr,wL:1,wR:1,pL:P.pL,pR:P.pR},e*0.5); root=V(G.tf.x+ROOT_OFF+0.05*e,0,0); }
  if(t>TL.stumble-0.05){ const st=sstep(TL.stumble-0.05,TL.stumble+0.35,t), rec=sm5(sstep(TL.stumble+0.3,TL.settle-0.2,t));
    const FALL={...mirrorP({...EASE,p:-0.75,tilt:0.45,aL:0.95,kL:0.25,aR:0.15,kR:0.8}),tL:G.tf,tR:G.tr,wL:1,wR:1,pL:P.pL,pR:P.pR};
    P=blend(P,FALL,st*(1-rec)); P=blend(P,{...mirrorP(STAND),tL:G.tf,tR:G.tr,wL:1,wR:1,pL:P.pL,pR:P.pR},rec);
    root=V(G.tf.x+ROOT_OFF+0.05,0,0);
    if(t<TL.stumble+0.9){ const ph=sstep(TL.stumble+0.1,TL.stumble+0.85,t)*2*Math.PI; P=gait(P,ph,0.55*Math.sin(ph/2)); } }
  if(t>TL.settle-0.4){ P.p+=0.012*Math.sin(2*Math.PI*0.25*(t-TL.letGo)+0.6); }
  return {P,root,yaw:Math.PI}; }

// ---------------------------------------------------------------- the rope
const RR=0.023;                                            // rope radius
const NT=38, NH=8, NS=66, SEG=0.04;                        // tail, hand-to-hand, span segment counts; segment length
const IHR=NT, IHF=NT+NH, ITF=IHF+NS, ITR=ITF+NH, NP=ITR+NT+1, IMID=IHF+NS/2;
function sampleCurve(fn,n){ const out=[]; for(let i=0;i<=n;i++) out.push(fn(i/n)); return out; }
// taut rope: sagging span between the front grips, short lengths between the hands, tails draping to the floor and lying behind
function tautRope(t){ const G=grips(t); const sag=0.045+0.06*easeAt(t);
  const wob=yankAt(t)*0.03+heaveAt(t)*0.05;
  const span=sampleCurve(s=>G.hf.clone().lerp(G.tf,s).add(V(0,-4*sag*s*(1-s)+wob*Math.sin(Math.PI*s)*Math.sin(t*41),0)),NS);
  const hand=(a,b)=>sampleCurve(s=>a.clone().lerp(b,s).add(V(0,-0.02*Math.sin(Math.PI*s),0)),NH);
  const tail=(hr,dir,zc)=>{ const f=V(hr.x+dir*0.6,RR,0.04*zc), e=V(hr.x+dir*1.45,RR,0.22*zc);
    return sampleCurve(s=>{ if(s<0.45){ const u=s/0.45; const c=V(hr.x+dir*0.42,0.12,0.02*zc); return hr.clone().multiplyScalar((1-u)*(1-u)).add(c.multiplyScalar(2*u*(1-u))).add(f.clone().multiplyScalar(u*u)); }
      const u=(s-0.45)/0.55; return f.clone().lerp(e,u).add(V(0,0,0.08*zc*Math.sin(Math.PI*u))); },NT); };
  const tl=tail(G.hr,-1,1).reverse(), tr=tail(G.tr,1,-1);
  return tl.concat(hand(G.hr,G.hf).slice(1),span.slice(1),hand(G.tf,G.tr).slice(1),tr.slice(1)); }
// verlet rope from when he eases off to the end: pinned to the grips while held, floor on the ledges, open pit, walls
const SIM_T0=TL.cut+0.25, SIM_HZ=600, SIM_N=Math.ceil((DUR-SIM_T0)*SIM_HZ)+2;
const SIM=new Float32Array(SIM_N*NP*3);
{ let P=tautRope(SIM_T0).map(v=>v.clone()), Q=tautRope(SIM_T0-1/SIM_HZ).map(v=>v.clone());
  const dt=1/SIM_HZ, g=-9.8*dt*dt; const rest=[]; for(let i=0;i<NP-1;i++) rest.push(P[i].distanceTo(P[i+1]));
  const store=k=>{ for(let i=0;i<NP;i++){ SIM[(k*NP+i)*3]=P[i].x; SIM[(k*NP+i)*3+1]=P[i].y; SIM[(k*NP+i)*3+2]=P[i].z; } };
  store(0);
  for(let k=1;k<SIM_N;k++){ const t=SIM_T0+k*dt; const G=grips(t);
    const pins=[]; if(t<TL.letGo+0.05) pins.push([IHR,G.hr],[IHF,G.hf]); pins.push([ITR,G.tr],[ITF,G.tf]);
    for(let i=0;i<NP;i++){ const p=P[i], o=Q[i]; const onF=p.y<=RR+0.002&&Math.abs(p.x)>PIT; const damp=onF?0.82:0.996;
      const nx=p.x+(p.x-o.x)*damp, ny=p.y+(p.y-o.y)*0.996+g, nz=p.z+(p.z-o.z)*damp; o.copy(p); p.set(nx,ny,nz); }
    for(let it=0;it<48;it++){
      for(let i=0;i<NP-1;i++){ const a=P[i], b=P[i+1]; const dx=b.x-a.x, dy=b.y-a.y, dz=b.z-a.z; const d=Math.sqrt(dx*dx+dy*dy+dz*dz)||1e-6; const k2=(d-rest[i])/d*0.5;
        a.x+=dx*k2; a.y+=dy*k2; a.z+=dz*k2; b.x-=dx*k2; b.y-=dy*k2; b.z-=dz*k2; }
      for(const [i,v] of pins) P[i].copy(v);
      for(let i=0;i<NP;i++){ const p=P[i]; const ax=Math.abs(p.x);
        if(ax>PIT-RR&&p.y<RR){ if(p.y>-0.06&&ax>PIT) p.y=RR; else if(p.y<=-0.06||ax<=PIT) { if(p.y<RR&&ax>PIT-RR&&ax<PIT+0.05&&p.y>-0.06) p.y=Math.max(p.y,RR*0.5); else p.x=Math.sign(p.x)*(PIT-RR); } }
        if(t>TL.ropeLand&&i===IMID) p.x+=(0-p.x)*0.0009;      // the marker settles at the centre of the pit
      } }
    store(k); } }
function simRope(t){ const f=clamp((t-SIM_T0)*SIM_HZ,0,SIM_N-1.001), k=Math.floor(f), u=f-k; const out=[];
  for(let i=0;i<NP;i++){ const a=(k*NP+i)*3, b=a+NP*3; out.push(V(lerp(SIM[a],SIM[b],u),lerp(SIM[a+1],SIM[b+1],u),lerp(SIM[a+2],SIM[b+2],u))); } return out; }
const ropeAt=t=>t<SIM_T0?tautRope(t):simRope(t);
// twisted-fibre look: diagonal stripes along the tube
const ropeTex=(()=>{ const c=document.createElement('canvas'); c.width=64; c.height=64; const g=c.getContext('2d'); g.fillStyle='#8a7c68'; g.fillRect(0,0,64,64);
  for(let k=-2;k<4;k++){ g.strokeStyle='rgba(30,24,18,0.75)'; g.lineWidth=7; g.beginPath(); g.moveTo(k*21,0); g.lineTo(k*21+64,64); g.stroke();
    g.strokeStyle='rgba(255,240,210,0.18)'; g.lineWidth=3; g.beginPath(); g.moveTo(k*21+8,0); g.lineTo(k*21+72,64); g.stroke(); }
  const t=new THREE.CanvasTexture(c); t.wrapS=t.wrapT=THREE.RepeatWrapping; t.colorSpace=THREE.SRGBColorSpace; return t; })();
ropeTex.repeat.set(Math.round(NP*SEG/0.034),3);
const ropeMat=new THREE.MeshStandardMaterial({color:0xb0a28a,roughness:0.86,metalness:0,map:ropeTex,bumpMap:ropeTex,bumpScale:0.6});
const rope=new THREE.Mesh(new THREE.BufferGeometry(),ropeMat); rope.castShadow=true; rope.receiveShadow=true; rope.frustumCulled=false; scene.add(rope);
function drawRope(pts){ rope.geometry.dispose(); rope.geometry=new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts,false,'centripetal'),pts.length*3,RR,10,false); }

// ---------------------------------------------------------------- the red ribbon: the one red object, tied at the rope's centre
const redMat=new THREE.MeshStandardMaterial({color:PAL.RED,roughness:0.5,metalness:0.0,emissive:PAL.RED,emissiveIntensity:0.3,side:THREE.DoubleSide});
const ribbon=new THREE.Group(); scene.add(ribbon);
const knot=new THREE.Mesh(new THREE.SphereGeometry(1,20,14),redMat); knot.scale.set(0.034,0.031,0.036); knot.castShadow=true; ribbon.add(knot);
const tails=[0,1].map(i=>{ const g=new THREE.PlaneGeometry(0.03,0.15,1,6); g.translate(0,-0.075,0); const m=new THREE.Mesh(g,redMat); m.castShadow=true; ribbon.add(m); return m; });
const redLight=new THREE.PointLight(0xff3a2a,0,0.9,2); scene.add(redLight);
const redHalo=SLD.glowSprite(scene,0xff3a2a,0.08); redHalo.scale.setScalar(0.42);
function drawRibbon(pts,t,close){ const p=pts[IMID], d=pts[IMID+1].clone().sub(pts[IMID-1]).normalize();
  ribbon.position.copy(p); ribbon.quaternion.setFromUnitVectors(V(1,0,0),d);
  const pp=ropeAt(t-0.06)[IMID]; const sw=clamp((p.x-pp.x)*3.0,-0.6,0.6);   // tails trail the motion
  tails.forEach((m,i)=>{ m.position.set(0,-0.01,0); m.rotation.set(0.0,(i?1:-1)*0.5,(i?1:-1)*0.22-sw+0.05*Math.sin(t*3.1+i*2.0),'YXZ'); });
  redMat.emissiveIntensity=lerp(0.22,0.4,close); redLight.position.copy(p).add(V(0,0.02,0.1)); redLight.intensity=lerp(0.03,0.07,close);
  redHalo.position.copy(p); redHalo.material.opacity=lerp(0.05,0.13,close); }

// ---------------------------------------------------------------- dust puffs: skidding feet, the stumble, the rope landing
const PUFFS=[]; const puffU={uT:{value:0},uH:{value:H}};
function addPuff(at,t0,n,spread,vel,seed,amp=1){ const Rn=rng(seed); for(let i=0;i<n;i++){ const a=Rn()*6.283; const r=Math.sqrt(Rn())*spread;
  PUFFS.push([at.x+Math.cos(a)*r,Math.max(0.01,at.y+Rn()*0.03),at.z+Math.sin(a)*r, Math.cos(a)*vel*(0.4+Rn()),vel*(0.25+0.9*Rn()),Math.sin(a)*vel*(0.4+Rn()), t0+Rn()*0.06, (0.6+Rn())*amp]); } }
const feetAt=(f,t)=>{ const s=f===hero?heroAt(t):twinAt(t); const J=skel(s.P,s.root,s.yaw); return [J.fL,J.fR]; };
{ TL.yanks.forEach((y,i)=>{ const [a,b]=feetAt(hero,y+0.1); addPuff(a.clone().setY(0.02),y+0.04,55,0.08,0.5,10+i,i===3?1.3:1); addPuff(b.clone().setY(0.02),y+0.06,35,0.06,0.4,20+i,0.8); });
  TL.heaves.forEach((h,i)=>{ const [a]=feetAt(hero,h+0.25); addPuff(a.clone().setY(0.02),h+0.15,18,0.05,0.25,40+i,0.5); });
  for(const tt of [TL.stumble+0.15,TL.stumble+0.55]){ const [a,b]=feetAt(twin,tt); addPuff(a.clone().setY(0.02),tt,40,0.08,0.4,60+Math.round(tt*10),0.9); addPuff(b.clone().setY(0.02),tt+0.05,30,0.07,0.35,70+Math.round(tt*10),0.8); }
  { const [a,b]=feetAt(hero,TL.letGo+0.55); addPuff(a.clone().setY(0.02),TL.letGo+0.45,25,0.06,0.3,80,0.6); }
  const land=simRope(TL.ropeLand+0.15); for(let k=4;k<NP-4;k+=7){ const p=land[k]; if(Math.abs(p.x)>PIT+0.02&&p.y<0.05) addPuff(p.clone().setY(0.02),TL.letGo+0.25+Math.abs(p.x+1.3)*0.05,6,0.04,0.25,90+k,0.7); }
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
  m.frustumCulled=false; scene.add(m); S.NOREFL.push(m); }

// ---------------------------------------------------------------- camera
// 0-3 tight on him, slow push-in; 3-4.4 drift out to a three-quarter view that shows the ribbon over the pit;
// 7-10 lateral pan along the rope across the pit; 10 lands on the twin in the mirror of the opening framing; cut 12.6 to a
// wide from behind his shoulder (both lamps, the pit, the ribbon), slow push-in to the end.
const K=(px,py,pz,lx,ly,lz)=>({p:V(px,py,pz),l:V(lx,ly,lz)});
const C0=K(-1.35,1.0,4.8,-1.5,0.77,0), C1=K(-1.4,0.97,4.3,-1.52,0.77,0);   // head clears the hook text (top 22%), floor and DOUBT stay above the watermark (80%)
const T0=K(-C0.p.x,C0.p.y,C0.p.z,-C0.l.x,C0.l.y,C0.l.z), T1=K(-C1.p.x,C1.p.y,C1.p.z,-C1.l.x,C1.l.y,C1.l.z);   // the twin's shot: the exact mirror of frame 0
const C2=K(-2.85,1.3,3.15,-0.78,0.6,0), C3=K(-2.7,1.25,2.95,-0.72,0.6,0);
const CM=K(-0.05,1.04,3.05,0.0,0.56,0), C4=T0, C5=T1;
const W0=K(0.0,1.9,10.8,0,0.66,0), W1=K(0.0,1.7,9.4,0,0.66,0);
const lerpK=(a,b,u)=>({p:a.p.clone().lerp(b.p,u),l:a.l.clone().lerp(b.l,u)});
const cr=(a,b,c,d,u)=>{ const u2=u*u,u3=u2*u; return b.clone().multiplyScalar(1.5*u3-2.5*u2+1).add(c.clone().multiplyScalar(-1.5*u3+2*u2+0.5*u)).add(a.clone().multiplyScalar(-0.5*u3+u2-0.5*u)).add(d.clone().multiplyScalar(0.5*u3-0.5*u2)); };
function camAt(t){
  if(t<TL.camOblique0) return lerpK(C0,C1,t/TL.camOblique0);
  if(t<TL.camOblique1) return lerpK(C1,C2,sm5((t-TL.camOblique0)/(TL.camOblique1-TL.camOblique0)));
  if(t<TL.pan0) return lerpK(C2,C3,(t-TL.camOblique1)/(TL.pan0-TL.camOblique1));
  if(t<TL.pan1){ const u=sm5((t-TL.pan0)/(TL.pan1-TL.pan0)); const pts=[C2,C3,CM,C4,C5];
    const s=u*2, i=Math.min(1,Math.floor(s)), f=s-i; const a=pts[i],b=pts[i+1],c=pts[i+2],d=pts[i+3];
    return {p:cr(a.p,b.p,c.p,d.p,f),l:cr(a.l,b.l,c.l,d.l,f)}; }
  if(t<TL.cut) return lerpK(C4,C5,sm5((t-TL.pan1)/(TL.cut-TL.pan1)));
  return lerpK(W0,W1,(t-TL.cut)/(DUR-TL.cut)); }
const shakeAt=t=>{ let s=0; for(const [t0,a] of [[TL.reveal,0.8],...TL.yanks.map(y=>[y+0.04,0.3])]) if(t>t0) s+=a*Math.exp(-(t-t0)/0.14); return s; };

// ---------------------------------------------------------------- one sub-frame
function setT(t){
  const h=heroAt(t), w=twinAt(t); const Jh=skel(h.P,h.root,h.yaw), Jw=skel(w.P,w.root,w.yaw); poseFig(hero,Jh); poseFig(twin,Jw);
  const l2=lamp2At(t); twin.mat.emissiveIntensity=0.07*l2; twin.mat.userData.rim.value=0.04+0.12*l2;
  const pts=ropeAt(t); drawRope(pts);
  const close=t<TL.pan0?sstep(TL.camOblique0+0.6,TL.camOblique1,t):t<TL.pan1?1-0.6*sstep(TL.pan0+1.2,TL.pan1,t):t<TL.cut?0.4:0.3;
  drawRibbon(pts,t,close);
  const dv=sstep(TL.reveal-0.4,TL.reveal+0.15,t); doubtMat.opacity=0.8*dv*l2; doubtHi.opacity=0.3*dv*l2;
  const c=camAt(t); cam.position.copy(c.p); cam.lookAt(c.l); cam.updateProjectionMatrix();
  const sh=shakeAt(t); if(sh>0){ cam.rotateX(0.005*sh*Math.sin(t*131.0)); cam.rotateY(0.005*sh*Math.sin(t*97.0+1.3)); }
  const pay=0.13*sstep(TL.endText,TL.settle+0.6,t);          // gold payoff: his lamp lifts a little once he has let go
  S.tick(t,pay);
  spot2.intensity=S.SPOT_I*l2; B2.beamU.uI.value=l2; B2.beamU.uT.value=t; B2.moteU.uT.value=t; B2.moteU.uOp.value=l2; puffU.uT.value=t;
  return {Jh,Jw,pts}; }
const CUTS=[0,TL.cut,DUR];
window.renderAt=(t,Ksub=3)=>{ const s=t<TL.cut?0:1; if(TL.yanks.some(y=>t>y-0.02&&t<y+0.3)||(t>TL.letGo-0.05&&t<TL.stumble+0.6)) Ksub=Math.max(Ksub,Ksub>1?6:1);
  return S.renderAt(setT,t,Ksub,{t0:CUTS[s],t1:CUTS[s+1]}); };
// screen positions and numbers for the overlay and the sound
const proj=v=>{ const p=v.clone().project(cam); return [p.x*0.5+0.5,0.5-p.y*0.5,p.z<1?1:0]; };
window.metaAt=t=>{ const o=setT(t); cam.updateMatrixWorld(); const m=o.pts[IMID];
  return {t,u:uAt(t),ribbon:[m.x,m.y,m.z],ribbonScr:proj(m),hero:proj(o.Jh.head),twin:proj(o.Jw.head),lamp2:lamp2At(t),yank:yankAt(t),heave:heaveAt(t),
    heroFeet:[o.Jh.fL.x,o.Jh.fR.x],twinFeet:[o.Jw.fL.x,o.Jw.fR.x]}; };
window.events={...TL};
window.ready=true;
