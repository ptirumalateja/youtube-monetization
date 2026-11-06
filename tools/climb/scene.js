// Build It As You Climb (Slow Light Dark): remake of the neuronvisuals "Perfectionist vs Action Taker" ladder reel.
// Same composition as the reference: two lanes side by side. Left, the perfectionist kneels between two tall pillars,
// sanding one perfect red rung. Right, the action taker climbs a ladder he builds as he goes: he pulls a plank off the
// bundle on his back, lashes it on above his head, steps up, repeats, and climbs into the light at the top.
// The camera pulls back and rises with him, holds on the light, then drops back to the perfectionist, who finally sets
// his one perfect rung between his pillars, looks up at the light, and sits down.
// Our additions: the gold lamp hatch and its beam, ember glints on every lashing, a plank bundle that runs out exactly
// at the top, rung counters (overlay.py), the perfectionist's look up at the end, recorded sound, seamless loop.
//
// renderAt(t) is pure (no state between frames), so frames can render in parallel workers.
import * as THREE from 'three';
import * as SLD from './sld.js';
const {V,clamp,sstep,lerp,PAL,rng,yawOf,keys}=SLD;
const TL=await (await fetch('./timeline.json')).json();
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960, DUR=TL.duration;

// ---------------------------------------------------------------- layout (metres; floor y = 0; camera on +z)
const SP=TL.spacing, X=0.65, RAILX=0.31, ZB=0.27, NR=TL.rungsTotal, N0=TL.rungsStart;
const HATCH=NR*SP+0.3;                       // underside of the light hatch
const PX=-1.05, PZ=-0.3, PILX=0.31;          // perfectionist lane: centre, his z, pillar half-gap
const NB=NR-N0;                              // planks he builds
const T=TL.cycle, BEND=NB*T;                 // build cycles, then fast steps up into the light
const FAST=TL.fastStep;

// ---------------------------------------------------------------- stage: 30 Friends look (dark void, warm lamp, motes)
const S=SLD.createStage({W,H,lamp:V(X,HATCH-0.02,0.05),lampTarget:V(X,0,0.25),cone:0.14,spot:TL.spot,beam:0.16,fov:38,motes:1900,vig:0.42});
const {scene,cam}=S;
S.renderer.localClippingEnabled=true;
scene.background=new THREE.Color(0x0b0c10); S.renderer.toneMappingExposure=1.1;
S.floor.scale.set(3,3,1); S.refl.scale.set(3,3,1);
scene.fog=new THREE.FogExp2(0x0b0c10,0.03);
scene.add(new THREE.HemisphereLight(0x8090b0,0x2a2218,0.34));
const key=new THREE.DirectionalLight(0xffe2b8,0.7); key.position.set(4.0,6.0,7.0); key.target.position.set(-0.3,2.5,0);
key.castShadow=true; key.shadow.mapSize.set(2048,2048); Object.assign(key.shadow.camera,{left:-5,right:5,top:9,bottom:-2,near:1,far:24}); key.shadow.bias=-0.0003; key.shadow.normalBias=0.02;
scene.add(key,key.target);
const rim=new THREE.DirectionalLight(0x9fb4e0,0.5); rim.position.set(-3,4,-5); scene.add(rim);
// a soft warm lamp over the perfectionist's bench so he never sinks into the void
const plamp=new THREE.PointLight(0xffd59a,2.2,4.5,1.6); plamp.position.set(PX+0.2,1.9,0.9); scene.add(plamp);

const R=SLD.createRig(scene);
const hero=R.makeFig(PAL.CREAM,'climber',{rim:0.18,lift:0.07});
const perf=R.makeFig(PAL.CREAM,'perf',{rim:0.18,lift:0.07});
const CLIP=new THREE.Plane(V(0,-1,0),HATCH+0.02); hero.mat.clippingPlanes=[CLIP]; hero.mat.clipShadows=true;

// ---------------------------------------------------------------- materials
const woodTex=SLD.noiseTex(256,31,128,70,40,0.18); woodTex.repeat.set(4,1);
const woodMat=k=>SLD.rimify(new THREE.MeshStandardMaterial({color:0xc9a477,roughness:0.78,metalness:0,map:woodTex,emissive:PAL.GOLD,emissiveIntensity:0}),0xffe0b0,0.08,'wood'+k);
const railMat=SLD.rimify(new THREE.MeshStandardMaterial({color:0xb08e62,roughness:0.8,metalness:0,map:woodTex}),0xffe0b0,0.1,'rail');
const pillarMat=SLD.rimify(new THREE.MeshStandardMaterial({color:0xd9d9de,roughness:0.55,metalness:0}),0xdfe6f5,0.12,'pillar');
const redMat=SLD.rimify(new THREE.MeshStandardMaterial({color:0xc8362a,roughness:0.32,metalness:0.05,emissive:PAL.RED,emissiveIntensity:0.18}),0xff9a80,0.25,'red');
const RUNG_L=0.74, RUNG_G=new THREE.BoxGeometry(RUNG_L,0.05,0.085);

// ---------------------------------------------------------------- the ladder: two rails up to the hatch, rungs
for(const sx of [-1,1]){ const m=new THREE.Mesh(new THREE.CylinderGeometry(0.03,0.034,HATCH+0.02,12),railMat); m.position.set(X+sx*RAILX,(HATCH+0.02)/2,0); m.castShadow=m.receiveShadow=true; scene.add(m); }
const rungY=j=>j*SP;
const rungs=[]; const rn=rng(7);
for(let j=1;j<=NR;j++){ const m=new THREE.Mesh(RUNG_G,woodMat(j)); m.castShadow=m.receiveShadow=true; m.rotation.z=(rn()-0.5)*0.05; scene.add(m);
  const gl=[SLD.glowSprite(scene,PAL.GOLD,0),SLD.glowSprite(scene,PAL.GOLD,0)]; rungs.push({m,gl,rz:m.rotation.z}); }
// the bundle on his back: the planks he still has to place
const bundle=[...Array(NB)].map((_,i)=>{ const m=new THREE.Mesh(RUNG_G,woodMat('b'+i)); m.castShadow=true; scene.add(m); return m; });
// the hatch: a slab of light at the top, the lamp sits just inside it
const hatchMat=new THREE.MeshBasicMaterial({color:new THREE.Color(1.0,0.86,0.6).multiplyScalar(2.2),fog:false});
const hatch=new THREE.Mesh(new THREE.BoxGeometry(1.0,0.05,0.9),hatchMat); hatch.position.set(X,HATCH+0.025,0.05); scene.add(hatch);
const rimSlab=new THREE.Mesh(new THREE.BoxGeometry(1.16,0.06,1.06),new THREE.MeshStandardMaterial({color:0x2a2622,roughness:0.9})); rimSlab.position.set(X,HATCH+0.075,0.05); scene.add(rimSlab);
const hGlow=SLD.glowSprite(scene,0xffd9a0,0.9); hGlow.position.set(X,HATCH+0.1,0.1); hGlow.scale.set(4.2,3.0,1);
const hGlow2=SLD.glowSprite(scene,0xffe8c8,0.8); hGlow2.position.set(X,HATCH+0.02,0.2); hGlow2.scale.set(1.8,1.0,1);
S.NOREFL.push(hGlow,hGlow2);

// ---------------------------------------------------------------- the perfectionist's lane: pillars, bench, red rung
for(const sx of [-1,1]){ const m=new THREE.Mesh(new THREE.BoxGeometry(0.1,2.5,0.1),pillarMat); m.position.set(PX+sx*PILX,1.25,0); m.castShadow=m.receiveShadow=true; scene.add(m); }
const bench=new THREE.Mesh(new THREE.BoxGeometry(0.62,0.26,0.24),new THREE.MeshStandardMaterial({color:0x5a5048,roughness:0.85,map:woodTex})); bench.position.set(PX,0.13,0.12); bench.castShadow=bench.receiveShadow=true; scene.add(bench);
const RED_L=2*PILX-0.1+0.01;
const redR=new THREE.Mesh(new THREE.BoxGeometry(RED_L,0.05,0.085),redMat); redR.castShadow=true; scene.add(redR);
const redGlow=SLD.glowSprite(scene,PAL.RED,0.18); redGlow.scale.set(0.9,0.35,1);
const dust=[...Array(14)].map(()=>{ const s=SLD.glowSprite(scene,0xffe6c0,0); s.scale.setScalar(0.035); return s; });

// ---------------------------------------------------------------- climber kinematics (world-space joints, then R.poseFig)
const LT=0.46;
function ik2(Sp,Tg,pole,l1=LT,l2=LT){ const d=Tg.clone().sub(Sp); const dist=Math.min(Math.max(d.length(),0.05),l1+l2-0.003); const dn=d.normalize();
  const a=(l1*l1-l2*l2+dist*dist)/(2*dist); const h=Math.sqrt(Math.max(0,l1*l1-a*a));
  const p=pole.clone().addScaledVector(dn,-pole.dot(dn)); if(p.lengthSq()<1e-6) p.set(0,0,-1); p.normalize();
  return {E:Sp.clone().addScaledVector(dn,a).addScaledVector(p,h), Hd:Sp.clone().addScaledVector(dn,dist)}; }
const arc=u=>Math.sin(Math.PI*clamp(u));
const qb=(a,b,c,u)=>a.clone().multiplyScalar((1-u)*(1-u)).addScaledVector(b,2*u*(1-u)).addScaledVector(c,u*u);
const HIP0=0.84;
// climber state at time t: hip, feet, hands, plank in hands, rungs placed, planks left
function climber(t){
  const o={look:0,lean:0.1};
  const bundleAt=(h)=>V(X,h+0.3,ZB+0.13);
  const railGrip=(f,side,dv)=>V(X+side*(RAILX-0.025),(f+dv)*SP+1.86,0.0);
  const climb=(f,v)=>{ // one step up from rung f to f+1
    const hip=f*SP+HIP0+SP*SLD.ease(sstep(0.12,0.88,v));
    const fL=V(X-0.12,(f+sstep(0.0,0.42,v))*SP+0.035+0.1*arc(sstep(0,0.42,v)),0.05+0.1*arc(sstep(0,0.42,v)));
    const fR=V(X+0.12,(f+sstep(0.45,0.88,v))*SP+0.035+0.1*arc(sstep(0.45,0.88,v)),0.05+0.1*arc(sstep(0.45,0.88,v)));
    const hL=railGrip(f,-1,sstep(0.08,0.4,v)).add(V(0,0,0.09*arc(sstep(0.08,0.4,v))));
    const hR=railGrip(f,1,sstep(0.5,0.82,v)).add(V(0,0,0.09*arc(sstep(0.5,0.82,v))));
    return {hip,fL,fR,hL,hR}; };
  if(t<BEND){ const k=Math.floor(t/T), u=t/T-k, f=N0-3+k, BU=TL.buildFrac;
    o.placed=N0+k+(u>=BU*0.68?1:0); o.left=NB-k-(u>=BU*0.3?1:0);
    if(u<BU){ const w=u/BU, hip=f*SP+HIP0;
      Object.assign(o,{hip,fL:V(X-0.12,f*SP+0.035,0.05),fR:V(X+0.12,f*SP+0.035,0.05)});
      const B=bundleAt(hip), TOP=V(X,hip+1.06,ZB-0.02), RG=V(X,rungY(f+4),0);
      let P;
      if(w<0.3) P=null; else if(w<0.68) P=qb(B,TOP,RG,SLD.ease(sstep(0.3,0.68,w))); else P=RG;
      const grab=sstep(0.04,0.28,w), toRail=sstep(0.84,1.0,w);
      const gL=railGrip(f,-1,0), gR=railGrip(f,1,0);
      const ends=P?[P.clone().add(V(-0.22,0.02,0)),P.clone().add(V(0.22,0.02,0))]:[B.clone().add(V(-0.22,0,0)),B.clone().add(V(0.22,0,0))];
      const tie=w>0.68&&w<0.86?0.035*Math.sin((w-0.68)*90):0;
      ends[0].add(V(0,tie,0.02*tie)); ends[1].add(V(0,-tie,-0.02*tie));
      o.hL=gL.clone().lerp(ends[0],grab).lerp(gL,toRail); o.hR=gR.clone().lerp(ends[1],grab).lerp(gR,toRail);
      o.carry=P; o.look=keys([[0,0],[0.15,-0.25],[0.35,0.4],[0.7,0.55],[0.9,0.1],[1,0]],w);   // glance back at the bundle, then up at the plank
      o.tie=w>0.68?w:0; o.tieRung=f+4;
    } else Object.assign(o,climb(f,(u-BU)/(1-BU)));
  } else { const tf=(t-BEND)/FAST, k=Math.floor(tf), v=tf-k, f=N0-3+NB+k; o.placed=NR; o.left=0; Object.assign(o,climb(f,v)); o.look=0.35; o.lean=0.04; }
  return o; }
function poseClimber(o){
  const hip=V(X,o.hip,ZB), J={};
  J.hip=hip; J.hipL=hip.clone().add(V(-0.07,0,0)); J.hipR=hip.clone().add(V(0.07,0,0));
  const lL=ik2(J.hipL,o.fL,V(-0.35,0.2,-1)), lR=ik2(J.hipR,o.fR,V(0.35,0.2,-1));
  J.kL=lL.E; J.fL=lL.Hd; J.kR=lR.E; J.fR=lR.Hd;
  J.neck=hip.clone().add(V(0,0.56*Math.cos(o.lean),-0.56*Math.sin(o.lean)));
  const hd=V(0,Math.cos(o.look*0.6),-0.25+0.4*Math.sin(-o.look*0.5)+0.18*o.look).normalize();
  J.head=J.neck.clone().addScaledVector(hd,0.2);
  for(const [s,sx] of [['L',-1],['R',1]]){ const Sh=J.neck.clone().add(V(sx*0.06,-0.06,0.01)); const r=R.ik(Sh,o['h'+s],V(sx*1,-0.6,0.5));
    J['sh'+s]=Sh; J['el'+s]=r.E; J['h'+s]=r.Hd; }
  R.poseFig(hero,J); }

// ---------------------------------------------------------------- perfectionist timeline
const YAW_P=yawOf(V(0,0,1));
const KNEEL={...R.P0,p:0.78,tilt:0.25,aL:0.12,aR:0.02,kL:1.62,kR:1.5,dy:0,fx:0};
const STAND={...R.P0,p:0.15,tilt:0.05};
const BENCH_RED=V(PX,0.285,0.12), SLOT=V(PX,TL.slotY,0);
function perfection(t){
  const ROOT=V(PX,0,PZ);
  let P, rp, rz=0, look=0;
  const sandX=0.1*Math.sin(t*8.5)*(1-sstep(TL.pStand-0.4,TL.pStand,t));
  // inspections: lift the rung to his eye and turn it, then back to sanding
  let insp=0; for(const [a,b] of TL.inspect) insp=Math.max(insp,sstep(a,a+0.35,t)*(1-sstep(b-0.35,b,t)));
  if(t<TL.pStand){
    rp=BENCH_RED.clone().lerp(V(PX,0.82,0.05),insp); rz=0.25*insp*Math.sin((t)*2.2);
    P={...KNEEL,p:lerp(0.78,0.42,insp),tilt:lerp(0.25,0.15,insp)};
    const off=V(sandX*(1-insp),0,0);
    P.tL=rp.clone().add(V(-0.17,0.03,0)).add(off); P.tR=rp.clone().add(V(0.17,0.03,0)).add(off); P.wL=P.wR=1; P.pL=V(-0.3,-0.6,0.8); P.pR=V(-0.3,-0.6,-0.8);
  } else if(t<TL.pSit){
    const up=sstep(TL.pStand,TL.pStand+0.7,t), place=sstep(TL.pPlace-0.55,TL.pPlace,t), lookUp=sstep(TL.pPlace+0.25,TL.pPlace+0.9,t);
    const carryPos=V(PX,0.95,-0.02);
    rp=BENCH_RED.clone().lerp(carryPos,sstep(TL.pStand+0.1,TL.pStand+0.7,t)).lerp(SLOT,place);
    P=R.blend(KNEEL,STAND,up); P.p=lerp(P.p,0.55,place*(1-lookUp)); P.tilt=lerp(P.tilt,-0.55,lookUp); P.p=lerp(P.p,0.0,lookUp);
    const hold=1-sstep(TL.pPlace+0.05,TL.pPlace+0.4,t);
    P.tL=rp.clone().add(V(-0.17,0.03,-0.02)); P.tR=rp.clone().add(V(0.17,0.03,-0.02)); P.wL=P.wR=hold; P.pL=V(-0.3,-0.6,0.8); P.pR=V(-0.3,-0.6,-0.8);
    look=lookUp;
  } else {
    rp=SLOT.clone(); const u=sstep(TL.pSit,TL.pSit+0.8,t);
    const stand={...STAND,p:0.0,tilt:-0.55};
    P=R.blend(stand,{...R.POSES.sit,tilt:lerp(-0.3,0.25,sstep(TL.pSit+0.6,TL.pSit+1.6,t))},u);
    if(u>0.3){ const hk=R.handsOnKnees(P,ROOT.clone().add(V(0,0,-0.35*u)),YAW_P,0.2); P.tL=hk.tL; P.tR=hk.tR; P.wL=P.wR=sstep(0.3,1,u); P.pL=hk.pL; P.pR=hk.pR; }
    ROOT.z-=0.35*u;
  }
  return {P,ROOT,rp,rz,look,insp,sand:t<TL.pStand?1-insp:0}; }

// ---------------------------------------------------------------- camera
const CK={
  tx:[[0,-0.25],[1.2,-0.25],[5.6,-0.1],[6.9,0.6],[8.1,0.6],[9.9,-0.2],[DUR,-0.2]],
  ty:[[0,1.8],[1.2,1.9],[5.6,3.5],[6.9,6.2],[8.1,6.3],[9.9,1.05],[DUR,1.0]],
  cy:[[0,2.0],[1.2,2.1],[5.6,3.6],[6.9,4.7],[8.1,4.8],[9.9,1.35],[DUR,1.3]],
  cx:[[0,0.35],[5.6,0.45],[6.9,1.0],[8.1,1.0],[9.9,0.05],[DUR,0.0]],
  d:[[0,7.5],[1.2,7.7],[5.6,10.4],[6.9,6.4],[8.1,6.0],[9.9,6.4],[DUR,6.1]],
};
function setCam(t){ cam.position.set(keys(CK.cx,t),keys(CK.cy,t),keys(CK.d,t)); cam.lookAt(keys(CK.tx,t),keys(CK.ty,t),0); cam.updateMatrixWorld(); }

// ---------------------------------------------------------------- frame
function setT(t){
  const o=climber(t); poseClimber(o);
  // rungs: placed ones on the ladder; the one being tied gets an ember glint at both lashings
  rungs.forEach((r,i)=>{ const j=i+1; const on=j<=o.placed; r.m.visible=on; r.m.position.set(X,rungY(j),0);
    let g=0; const tp=(N0<j)?(j-N0-1)*T+TL.buildFrac*T*0.68:-9; const dt=t-tp; if(dt>=0) g=Math.exp(-dt*2.4)*1.0+0.06; if(j<=N0) g=0.06;
    r.m.material.emissiveIntensity=on?0.25*Math.max(0,g-0.06):0;
    r.gl.forEach((s,k)=>{ s.position.set(X+(k?1:-1)*RAILX,rungY(j),0.05); s.material.opacity=on?0.9*Math.max(0,g-0.06)+0.0:0; s.scale.setScalar(0.32); }); });
  // bundle on his back
  const B0=V(X,o.hip+0.24,ZB+0.13);
  bundle.forEach((m,i)=>{ m.visible=i<o.left; m.position.copy(B0).add(V(0,-0.02+Math.floor(i/3)*0.055,(i%3)*0.09-0.02)); m.rotation.set(0,0,(i%3-1)*0.04); });
  // the plank in his hands
  if(o.carry){ const m=bundle[NB-1]; m.visible=true; m.position.copy(o.carry); m.rotation.set(0,0,0); }
  // perfectionist
  const p=perfection(t); const J=R.skel(p.P,p.ROOT,YAW_P); R.poseFig(perf,J);
  redR.position.copy(p.rp); redR.rotation.set(0,0,p.rz); redGlow.position.copy(p.rp).add(V(0,0,0.06));
  const placed=t>=TL.pPlace; redMat.emissiveIntensity=0.18+(placed?0.5*Math.exp(-(t-TL.pPlace)*2.5):0); redGlow.material.opacity=0.16+(placed?0.4*Math.exp(-(t-TL.pPlace)*2.5):0);
  dust.forEach((d,i)=>{ const ph=(t*1.7+i/dust.length)%1; d.position.copy(p.rp).add(V(Math.sin(i*7.1)*0.22,0.02+ph*0.18,0.05+Math.cos(i*3.3)*0.06)); d.material.opacity=p.sand*0.5*Math.sin(Math.PI*ph); });
  // light: the hatch grows as he nears it, flares as he goes through
  const pay=keys(TL.pay,t);
  hGlow.material.opacity=0.65+0.35*pay; hGlow.scale.set(4.2*(1+0.5*pay),3.0*(1+0.5*pay),1);
  hatchMat.color.setRGB(1.0,0.86,0.6).multiplyScalar(2.0+2.5*pay);
  setCam(t); S.tick(t,pay); }

window.renderAt=(t,K=3)=>S.renderAt(setT,t,K,{t0:0,t1:DUR});
window.metaAt=t=>{ setT(t); const pr=v=>{ const n=v.clone().project(cam); return [(n.x+1)/2,(1-n.y)/2]; };
  const o=climber(t); return {t,rungs:o.placed,prung:t>=TL.pPlace?1:0,lane:{perf:pr(V(PX,2.7,0)),act:pr(V(X,2.7,0)),perfFeet:pr(V(PX,-0.12,0))}}; };
window.events={...TL,placeTimes:[...Array(NB)].map((_,k)=>k*T+TL.buildFrac*T*0.68),grabTimes:[...Array(NB)].map((_,k)=>k*T+TL.buildFrac*T*0.3)};
window.ready=true;
