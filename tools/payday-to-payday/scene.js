// Payday to Payday (Slow Light Dark). SALARY DAY: a happy cream stickman at a table under the gold lamp, a red wallet, a grey stack of
// bundled bills flies in (balance 50,000). Over DAY 1..5 grey strangers walk in and take a bundle a day: RENT, EMI, GROCERIES, FOOD,
// PARTY. By day 5 the wallet is empty, he is down. Then the routine: he gets up and goes to work, the lamp (the sun) sets and rises,
// the days run on (DAY 6..30), he comes home in the dark and sits, again and again. Day 30 is SALARY DAY again and the loop closes.
// renderAt(t) is pure (no state between frames). Units are metres, floor y = 0, camera on +z. Hero faces +x (side-on to camera).
import * as THREE from 'three';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';
import * as SLD from './sld.js';
const {V,sstep,lerp,clamp,PAL,sm5,rotY,yawOf,keys}=SLD;
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960;
const TL=await (await fetch('timeline.json')).json(); const DUR=TL.duration;
const S=SLD.createStage({W,H}); const R=SLD.createRig(S.scene); const scene=S.scene;
const eo=u=>1-Math.pow(1-clamp(u),3);                     // ease out
const hero=R.makeFig(PAL.CREAM,'hero',{rim:0.16,lift:0.04});

// ---------------------------------------------------------------- set: table, chair
const WOOD=new THREE.MeshStandardMaterial({color:0x4b3b2d,roughness:0.5,metalness:0,map:SLD.noiseTex(256,31,128,60,60,0.12)});
const table=new THREE.Group(); scene.add(table);
{ const top=new THREE.Mesh(new RoundedBoxGeometry(1.5,0.05,0.8,4,0.012),WOOD); top.position.set(0.42,0.755,0.05); top.castShadow=top.receiveShadow=true; table.add(top);
  for(const [x,z] of [[-0.25,-0.3],[1.09,-0.3],[-0.25,0.4],[1.09,0.4]]){ const l=new THREE.Mesh(new THREE.BoxGeometry(0.06,0.73,0.06),WOOD); l.position.set(x,0.365,z); l.castShadow=l.receiveShadow=true; table.add(l); } }
const IRON=SLD.IRON();
{ const seat=new THREE.Mesh(new RoundedBoxGeometry(0.42,0.04,0.42,3,0.01),IRON); seat.position.set(-0.47,0.45,0); seat.castShadow=seat.receiveShadow=true; scene.add(seat);
  const back=new THREE.Mesh(new RoundedBoxGeometry(0.035,0.5,0.4,3,0.01),IRON); back.position.set(-0.7,0.72,0); back.castShadow=back.receiveShadow=true; scene.add(back);
  for(const [x,z] of [[-0.64,-0.17],[-0.3,-0.17],[-0.64,0.17],[-0.3,0.17]]){ const l=new THREE.Mesh(new THREE.CylinderGeometry(0.014,0.014,0.43,10),IRON); l.position.set(x,0.215,z); l.castShadow=true; scene.add(l); } }

// ---------------------------------------------------------------- the red wallet (the one red object)
const WAL=V(0.30,0.7975,0.05), TOWER_X=WAL.x+0.16, WTOP=WAL.y+0.0175;
function walTex(){ const c=document.createElement('canvas'); c.width=512; c.height=300; const g=c.getContext('2d'); g.fillStyle='#d83a2e'; g.fillRect(0,0,512,300);
  g.strokeStyle='#8e231b'; g.lineWidth=5; g.setLineDash([16,10]); for(const [x0,w] of [[18,230],[264,230]]) g.strokeRect(x0,18,w,264);
  g.setLineDash([]); g.fillStyle='#8e231b'; g.fillRect(250,0,12,300);
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; return t; }
const walMat=new THREE.MeshStandardMaterial({color:0xffffff,map:walTex(),roughness:0.42,metalness:0.1,emissive:PAL.RED,emissiveIntensity:0.05});
const wallet=new THREE.Group(); scene.add(wallet);
{ const body=new THREE.Mesh(new RoundedBoxGeometry(0.6,0.035,0.36,4,0.014),walMat); body.castShadow=body.receiveShadow=true; wallet.add(body);
  const seam=new THREE.Mesh(new THREE.BoxGeometry(0.012,0.037,0.34),new THREE.MeshStandardMaterial({color:0x5a1712,roughness:0.6})); seam.position.x=-0.02; wallet.add(seam);
  const lip=new THREE.Mesh(new RoundedBoxGeometry(0.28,0.045,0.04,3,0.012),walMat); lip.position.set(0.16,0.018,0.15); lip.castShadow=true; wallet.add(lip);
  const lipB=lip.clone(); lipB.position.set(0.16,0.018,-0.15); wallet.add(lipB); }
const halo=SLD.glowSprite(scene,0xff3a2a,0.03); halo.scale.setScalar(0.9);
const redLight=new THREE.PointLight(PAL.RED,0,1.4,2); scene.add(redLight);

// ---------------------------------------------------------------- bundles of grey bills
function billTex(){ const c=document.createElement('canvas'); c.width=256; c.height=160; const g=c.getContext('2d');
  g.fillStyle='#8a8f98'; g.fillRect(0,0,256,160); g.strokeStyle='#5d626c'; g.lineWidth=5; g.strokeRect(8,8,240,144); g.lineWidth=2; g.strokeRect(20,20,216,120);
  g.strokeStyle='rgba(60,64,72,0.45)'; g.lineWidth=1; for(let i=0;i<12;i++){ g.beginPath(); g.ellipse(128,80,40+i*5,26+i*3,0,0,7); g.stroke(); }
  g.fillStyle='#4b5059'; g.font='bold 54px monospace'; g.textAlign='center'; g.textBaseline='middle'; g.fillText('₹500',128,80); g.font='bold 20px monospace'; g.fillText('500',44,38); g.fillText('500',212,122);
  g.fillStyle='#cfd2d8'; g.fillRect(104,0,48,160); g.fillStyle='#8f949d'; g.fillRect(104,0,3,160); g.fillRect(149,0,3,160);   // paper band
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; t.anisotropy=4; return t; }
const BT=billTex();
// stack order bottom to top = landing order; thickness is proportional to the amount
const ORDER=['PARTY','FOOD','GROCERIES','EMI','RENT'];
const item=k=>TL.items.find(i=>i.key===k);
const slabs={}; { let y=WTOP; for(const k of ORDER){ const it=item(k), th=it.amt/1000*0.0035;
  const mat=new THREE.MeshStandardMaterial({color:0xffffff,map:BT,roughness:0.85,metalness:0,transparent:true,opacity:1,emissive:0xffffff,emissiveMap:BT,emissiveIntensity:0.32});
  const m=new THREE.Mesh(new THREE.BoxGeometry(0.26,th,0.17),mat); m.castShadow=true; m.receiveShadow=true; m.frustumCulled=false; scene.add(m);
  slabs[k]={m,mat,th,rest:V(TOWER_X+0.004*Math.sin(k.length*3),y+th/2,WAL.z),yaw:0.05*Math.sin(k.length*5)}; y+=th; } }

// ---------------------------------------------------------------- takers (grey strangers)
const XT={RENT:0.40,EMI:0.52,GROCERIES:0.36,FOOD:0.50,PARTY:0.44}, ZT=-0.56, WALK_Z0=-3.2;
const takers=TL.items.map((it,i)=>({it,fig:R.makeFig(PAL.SLATE,'tk'+i,{rim:0.14,rimCol:0x9fb2d6,lift:0.05}),x:XT[it.key],side:i%2?1:-1}));
const STRIDE=1.3;
const hatMat=new THREE.MeshStandardMaterial({color:0xb9bdc6,roughness:0.6,transparent:true,emissive:0xb9bdc6,emissiveIntensity:0.12});
const hat=new THREE.Mesh(new THREE.ConeGeometry(0.075,0.2,20),hatMat); hat.castShadow=true; hat.visible=false; scene.add(hat);
function takerState(T,t){ const g=T.it.grab, x=T.x, a0=g-1.7, a1=g-0.35, b0=g+0.6, b1=g+2.4;
  const alpha=sstep(a0,a0+0.7,t)*(1-sstep(g+0.9,g+2.3,t));
  let pos,yaw=-Math.PI/2,walk=0,ph=0;
  if(t<a1){ const u=sm5(clamp((t-a0)/(a1-a0))); const sx=x+0.55*T.side, sz=WALK_Z0;
    pos=V(lerp(sx,x,u),0,lerp(sz,ZT,u)); walk=1-sstep(0.8,1.0,u)*0.9; ph=u*(ZT-sz)/STRIDE*2*Math.PI*1.4; yaw=-Math.PI/2+(1-u)*0.35*T.side;
  } else if(t<b0){ pos=V(x,0,ZT); ph=0; walk=0; yaw=-Math.PI/2+sm5(clamp((t-(g+0.2))/(0.55)))*Math.PI; }
  else { const u=sm5(clamp((t-b0)/(b1-b0))); pos=V(x,0,lerp(ZT,WALK_Z0,u)); walk=1-sstep(0.9,1.0,u)*0.0; ph=u*(ZT-WALK_Z0)/STRIDE*2*Math.PI*1.2; yaw=Math.PI/2; }
  return {alpha,pos,yaw,walk,ph}; }
const tmpHand=[];
function poseTaker(T,t,st){ const g=T.it.grab; const lean=sstep(g-0.6,g-0.1,t)*(1-sstep(g+0.15,g+0.55,t));
  let P=R.gait({...R.P0,p:0.06+0.55*lean,tilt:0.05+0.1*lean},st.ph,st.walk,0.34,0.62,0.22);
  const sl=slabs[T.it.key]; const slabTop=sl.rest.clone().add(V(0,sl.th/2,0));
  const carry=st.pos.clone().add(rotY(V(0.30,0.98,-0.06),st.yaw));
  const c=sstep(g-0.02,g+0.4,t); const tgt=slabTop.clone().lerp(carry,c);
  const w=sstep(g-0.6,g-0.2,t);
  P={...P,tR:tgt,wR:w,pR:V(0,-0.8,-0.6),eL:0.3};
  return P; }

// ---------------------------------------------------------------- the hero
const SEAT_ROOT=V(-0.225,0,0);
const PK=V(-0.44,0.60,0.16);              // his hip pocket
const OFFW=V(0.13,-0.045,0.0);            // wallet centre relative to the carrying hand
const REST_L=V(0.02,0.805,0.26), REST_R=V(0.0,0.805,-0.2);
const JOY_L=V(-0.22,1.36,0.30), JOY_R=V(-0.22,1.36,-0.30);
const CYC=TL.cycles, LIGHT=TL.light;
const lightAt=t=>SLD.keys(LIGHT,t);
// slump: one fifth per deduction; he stays down through the routine and straightens up for the next salary day
const slumpAt=t=>{ let s=0; for(const it of TL.items) s+=0.2*sstep(it.grab,it.grab+0.6,t); return s*(1-sstep(TL.salaryAgain,TL.salaryAgain+0.9,t)); };
function wallState(t){ // wallet: drawn from the pocket and laid down at the start, back in the pocket once it is empty
  const hx=WAL.clone().sub(OFFW); let hand=REST_L.clone(), wpos=WAL.clone(), sc=1;
  if(t<0.75){ const u=sm5(clamp(t/0.75)); hand=PK.clone().lerp(hx,u); hand.y+=0.12*Math.sin(Math.PI*u); wpos=hand.clone().add(OFFW); sc=sstep(0,0.15,t); }
  else if(t<1.5){ const u=sm5(clamp((t-0.75)/0.75)); hand=hx.clone().lerp(REST_L,u); }
  else if(t<TL.pick0){ }
  else if(t<TL.pick0+0.5){ const u=sm5((t-TL.pick0)/0.5); hand=REST_L.clone().lerp(hx,u); }
  else if(t<TL.pocket){ const u=sm5((t-TL.pick0-0.5)/(TL.pocket-TL.pick0-0.5)); hand=hx.clone().lerp(PK,u); hand.y+=0.1*Math.sin(Math.PI*u); wpos=hand.clone().add(OFFW.clone().multiplyScalar(1-0.6*u)); sc=1-0.9*sstep(0.8,1.0,u); }
  else { hand=PK.clone(); wpos=PK.clone(); sc=0; }
  // end of the loop: his hand drifts back to the pocket so frame 0 (drawing the wallet) follows on
  if(t>TL.salaryAgain+0.3){ const u=sm5(clamp((t-TL.salaryAgain-0.3)/0.9)); hand=REST_L.clone().lerp(PK,u); sc=0; }
  return {hand,wpos,sc}; }
function seatPose(t){
  const sl=slumpAt(t); const lift=sstep(TL.salaryAgain,TL.salaryAgain+0.9,t);
  const joy=sstep(0.95,1.35,t)*(1-sstep(2.5,3.0,t)); const bob=joy*0.012*Math.abs(Math.sin(t*9));
  const breathe=0.012*Math.sin(2*Math.PI*0.21*t);
  let flinch=0; for(const it of TL.items){ const d=t-it.grab; if(d>0&&d<0.5) flinch+=0.06*Math.sin(Math.PI*d/0.5)*Math.exp(-d*3); }
  const stare=sstep(9.2,10.0,t);
  const P={...R.P0,aL:1.5,aR:1.5,kL:1.5,kR:1.5,sL:0.4,sR:0.4,eL:0.9,eR:0.9,dy:bob,
    p:0.04+0.38*sl-0.03*joy+0.02*lift+breathe+flinch, tilt:-0.06*(1-sl)-0.12*joy+0.52*sl+0.1*stare*(1-lift)+flinch*0.5, hy:-0.04*Math.sin(t*0.4)};
  const ws=wallState(t);
  P.tL=ws.hand.clone().lerp(JOY_L,joy).add(V(0,0.004*Math.sin(t*1.3),0)); P.wL=1; P.pL=V(-0.3,-0.75,0.35);
  P.tR=REST_R.clone().lerp(JOY_R,joy).add(V(0.02*sl,0,0)); P.wR=1; P.pR=V(-0.3,-0.75,-0.35);
  return {P,ws}; }
// routine: each cycle he stands, walks out left to work, is gone, comes back in from the right in the dark and sits again
const OUT0=V(-0.62,0,0.35), OUT1=V(-1.7,0,0.85), IN0=V(1.5,0,0.85), IN1=V(-0.58,0,0.85), STRIDE_H=1.3;
function heroState(t){
  let k=-1; for(let i=0;i<CYC.length;i++) if(t>=CYC[i]) k=i;
  const base={seat:true,root:SEAT_ROOT.clone(),yaw:0,blend:0,walk:0,ph:0,vis:true};
  if(k<0||t>=CYC[k]+2.6) return base;
  const dt=t-CYC[k]; const o={seat:false,root:SEAT_ROOT.clone(),yaw:0,blend:0,walk:0,ph:0,vis:true};
  if(dt<0.35) return base;
  if(dt<0.75){ const u=sm5((dt-0.35)/0.4); o.blend=u; o.root.lerp(OUT0,u); o.yaw=Math.PI*sm5(clamp((u-0.3)/0.7)); return o; }
  if(dt<1.35){ const u=sstep(0,1,(dt-0.75)/0.6); o.blend=1; o.root=V(lerp(OUT0.x,OUT1.x,u),0,lerp(OUT0.z,OUT1.z,sstep(0,0.5,u))); o.yaw=Math.PI; o.walk=1; o.ph=u*(OUT0.x-OUT1.x)/STRIDE_H*2*Math.PI*2.2; return o; }
  if(dt<1.55){ o.vis=false; o.blend=1; return o; }
  if(dt<2.35){ const u=sstep(0,1,(dt-1.55)/0.8); o.blend=1; o.root=V(lerp(IN0.x,IN1.x,u),0,0.85); o.yaw=Math.PI; o.walk=1; o.ph=u*(IN0.x-IN1.x)/STRIDE_H*2*Math.PI*1.6; return o; }
  const u=sm5((dt-2.35)/0.25); o.blend=1-u; o.root=IN1.clone().lerp(SEAT_ROOT,u); o.yaw=Math.PI*(1-sm5(clamp(u*1.4))); o.walk=1-u; o.ph=0; return o; }
function poseHero(t){
  const {P:A,ws}=seatPose(t); const st=heroState(t); const sl=slumpAt(t);
  if(st.blend<=0.0001) return {P:A,ws,root:SEAT_ROOT,yaw:0,vis:true,st};
  const W_=R.gait({...R.P0,p:0.1+0.28*sl,tilt:0.12+0.34*sl,eL:0.5,eR:0.5},st.ph,st.walk,0.34,0.62,0.2);
  const B=R.blend(A,W_,st.blend); B.p+=0.3*Math.sin(Math.PI*st.blend)*(st.walk<1?1:0);
  return {P:B,ws,root:st.root,yaw:st.yaw,vis:st.vis,st}; }

// ---------------------------------------------------------------- camera: wide, slow drift that is periodic (loop), a short push to the slumped hero
function camAt(t){
  const d=0.12*Math.sin(Math.PI*t/DUR); const wp=V(-0.12,1.85,4.15-d), wl=V(-0.02,1.12,0.0);
  const push={pos:V(-0.3,1.55,3.05),look:V(-0.4,1.1,0.0)};
  const u=sm5(clamp((t-TL.push0)/0.9))*(1-sm5(clamp((t-TL.push1)/0.8)));
  return {pos:wp.lerp(push.pos,u),look:wl.lerp(push.look,u)}; }

// ---------------------------------------------------------------- one frame
function setT(t){
  const H_=poseHero(t); hero.setAlpha(H_.vis?1:0); if(H_.vis){ const Jh=R.skel(H_.P,H_.root,H_.yaw); R.poseFig(hero,Jh); }
  const ws=H_.ws; wallet.position.copy(ws.wpos); wallet.scale.setScalar(Math.max(ws.sc,0.0001)); wallet.visible=ws.sc>0.01;
  const push=sstep(9.4,10.0,t)*(1-sstep(TL.pick0-0.2,TL.pick0+0.4,t));
  walMat.emissiveIntensity=0.05+0.17*push; halo.material.opacity=(0.03+0.13*push)*(ws.sc>0.5?1:0); halo.position.copy(wallet.position).add(V(0,0.05,0)); redLight.position.copy(wallet.position).add(V(0,0.28,0.15)); redLight.intensity=0.5*push;
  hat.visible=false;
  for(const k of ORDER){ const sl=slabs[k], L=TL.land[k], Ls=L-TL.landDur, it=item(k); const T=takers.find(x=>x.it.key===k);
    let pos=sl.rest.clone(), yaw=sl.yaw, pitch=0, roll=0, vis=true, op=1;
    if(t<Ls) vis=false;
    else if(t<L){ const u=(t-Ls)/TL.landDur, e=eo(u); const kk=ORDER.indexOf(k); const s0=V(-1.75-0.08*kk,2.15+0.28*kk,0.75-0.2*kk);
      pos=s0.clone().lerp(sl.rest,e); pos.y+=0.55*Math.sin(Math.PI*e)*(1-e*0.2); yaw=lerp(2.4+kk*0.4,sl.yaw,e); pitch=lerp(1.1,0,e); roll=lerp(-0.8,0,e); }
    else if(t<it.grab+0.05){ const d=t-L; pos.y+=0.014*Math.exp(-d*14)*Math.abs(Math.cos(d*22)); }
    const st=takerState(T,t); T.fig.setAlpha(st.alpha); T.st=st;
    if(st.alpha>0.004){ const PT=poseTaker(T,t,st); const J=R.skel(PT,st.pos,st.yaw); R.poseFig(T.fig,J);
      if(k==='PARTY'){ hat.visible=true; hatMat.opacity=st.alpha; hat.position.copy(J.head).add(V(0,0.2,0)); }
      const a=sstep(it.grab-0.02,it.grab+0.18,t); if(a>0){ const hp=J.hR.clone().add(rotY(V(0.05,-0.02,0.0),st.yaw)); pos=pos.clone().lerp(hp,a); yaw=lerp(yaw,st.yaw+Math.PI/2,a); op=1-sstep(it.grab+0.9,it.grab+2.3,t); } }
    else if(t>it.grab+1) vis=false;
    sl.m.visible=vis&&op>0.004; sl.mat.opacity=op; sl.m.position.copy(pos); sl.m.rotation.set(pitch,yaw,roll,'YXZ'); }
  const c=camAt(t); S.cam.position.copy(c.pos); S.cam.lookAt(c.look); S.tick(t);
  // the lamp is the sun: it sets and rises with each day of the routine
  const Lk=lightAt(t); S.spot.intensity=S.SPOT_I*Lk; S.beamU.uI.value=Lk; S.moteU.uOp.value=Lk; }
window.renderAt=(t,K=3)=>{ const routine=t>TL.routine0-0.4&&t<TL.salaryAgain+0.3; return S.renderAt(setT,t,routine?6:K,{t0:0,t1:DUR,shutter:routine?1/36:1/60}); };
// foot plants (for the sound mix): the strangers and the hero's commute, sampled at the frame rate
window.events={...TL,steps:(()=>{ const out=[]; const N=Math.round(DUR*TL.fps);
  for(const T of takers){ let prev=null; for(let f=0;f<N;f++){ const t=f/TL.fps; const st=takerState(T,t); if(st.alpha<0.05||st.walk<0.2){ prev=null; continue; }
    if(prev!==null&&Math.floor(st.ph/Math.PI)>Math.floor(prev/Math.PI)) out.push({t,x:st.pos.x,z:st.pos.z,a:st.alpha,who:'t'}); prev=st.ph; } }
  let prev=null; for(let f=0;f<N;f++){ const t=f/TL.fps; const st=heroState(t); if(!st.vis||st.walk<0.3){ prev=null; continue; }
    if(prev!==null&&Math.floor(st.ph/Math.PI)>Math.floor(prev/Math.PI)) out.push({t,x:st.root.x,z:st.root.z,a:1,who:'h'}); prev=st.ph; }
  return out.sort((a,b)=>a.t-b.t); })()};
window.ready=true;
