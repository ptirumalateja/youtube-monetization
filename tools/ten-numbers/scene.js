// Ten Numbers (Slow Light, logo palette: navy room, amber light, cream text). 19.2 s, one boy, one desk, one counter.
// A boy dials the red landline (10 amber number cards float around him). He grows up at the same desk; a smartphone
// arrives and the cards fly into it one by one; the phone dies; one card (HOME) is left; he dials the old landline.
// renderAt(t) is pure (no state between frames). All story times come from timeline.json (the mix reads the same file).
import * as THREE from 'three';
import * as SLD from './sld.js';
const {V,clamp,sstep,lerp,sm5,rng,yawOf,PAL}=SLD;
await Promise.all([document.fonts.load('700 64px "JetBrains Mono"'),document.fonts.load('600 34px "JetBrains Mono"')]);
const TL=await (await fetch('./timeline.json')).json();
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960, DUR=TL.duration;

const NAVY=0x161c2c, AMBER=0xffb24d;
const DESK_TOP=0.74, LAMP=V(0.05,3.3,0.15), AIM=V(0,0.7,-0.25);
const S=SLD.createStage({W,H,lamp:LAMP,lampTarget:AIM,cone:0.36,spot:17,beam:0.045,motes:1400,
  bg:NAVY,fog:0.04,hemi:1.1,hemiSky:0x3a4a7a,vig:0.25,floorCol:0x3a4058,fov:36});
S.spot.color.set(0xffc070); S.beamU.uCol.value.set(0xffb860);
S.spot.shadow.camera.far=6;
const R=SLD.createRig(S.scene);
{ const wt=SLD.noiseTex(256,11,70,26,60,0.04); wt.repeat.set(3,2);
  const wall=new THREE.Mesh(new THREE.PlaneGeometry(14,7),new THREE.MeshStandardMaterial({color:0x2c3554,roughness:0.95,map:wt,emissive:0x182036}));
  wall.position.set(0,3.5,-1.9); wall.receiveShadow=true; S.scene.add(wall); }

function woodTex(seed,base){ const c=document.createElement('canvas'); c.width=1024; c.height=256; const g=c.getContext('2d'); const Rn=rng(seed);
  g.fillStyle=base; g.fillRect(0,0,1024,256);
  for(let k=0;k<260;k++){ const y=Rn()*256, a=0.04+Rn()*0.1; g.strokeStyle=Rn()<0.6?`rgba(0,0,0,${a})`:`rgba(255,220,180,${a*0.5})`; g.lineWidth=0.6+Rn()*2.2;
    g.beginPath(); g.moveTo(0,y); for(let x=0;x<=1024;x+=32) g.lineTo(x,y+Math.sin(x*0.004+k)*3+Math.sin(x*0.021+k*1.7)*1.2); g.stroke(); }
  const t=new THREE.CanvasTexture(c); t.wrapS=t.wrapT=THREE.RepeatWrapping; t.colorSpace=THREE.SRGBColorSpace; return t; }
const WOOD=new THREE.MeshStandardMaterial({color:0x8a6a52,map:woodTex(3,'#3b2a1f'),roughness:0.5});
SLD.rimify(WOOD,0xffe6c8,0.05,'wood');
const add=(geo,mat,x,y,z,par=S.scene)=>{ const m=new THREE.Mesh(geo,mat); m.position.set(x,y,z); m.castShadow=m.receiveShadow=true; par.add(m); return m; };

// desk + chair
add(new THREE.BoxGeometry(1.3,0.05,0.62),WOOD,0,DESK_TOP-0.025,0);
for(const x of [-0.6,0.6]) for(const z of [-0.26,0.26]) add(new THREE.BoxGeometry(0.06,DESK_TOP-0.05,0.06),WOOD,x,(DESK_TOP-0.05)/2,z);
add(new THREE.BoxGeometry(1.24,0.68,0.03),new THREE.MeshStandardMaterial({color:0x6b5240,roughness:0.7,emissive:0x2a1e15}),0,0.36,0.285);
const CH_Z=-0.62;
{ const g=new THREE.Group(); g.position.set(0,0,CH_Z); S.scene.add(g);
  add(new THREE.BoxGeometry(0.42,0.04,0.42),WOOD,0,0.47,0,g);
  for(const x of [-0.18,0.18]) for(const z of [-0.18,0.18]) add(new THREE.BoxGeometry(0.035,0.47,0.035),WOOD,x,0.235,z,g);
  for(const x of [-0.18,0.18]) add(new THREE.BoxGeometry(0.035,0.55,0.035),WOOD,x,0.75,-0.19,g);
  add(new THREE.BoxGeometry(0.4,0.12,0.03),WOOD,0,0.93,-0.19,g); }

// ---------------------------------------------------------------- the red landline (the one red object; dulls with the years)
const RED=new THREE.MeshStandardMaterial({color:PAL.RED,roughness:0.35,emissive:PAL.RED,emissiveIntensity:0.04});
SLD.rimify(RED,0xff9a80,0.14,'phone');
const PH=V(-0.1,DESK_TOP,-0.4);
function holeAng(k){ return k/10*Math.PI*2*0.8+0.5; }
let dialMesh=null;
const phone=new THREE.Group(); phone.position.copy(PH); phone.rotation.y=0.35; S.scene.add(phone);
{ add(new THREE.BoxGeometry(0.22,0.07,0.2),RED,0,0.035,0,phone);
  add(new THREE.CylinderGeometry(0.075,0.09,0.03,32),RED,0,0.085,0.02,phone);
  const dialM=new THREE.MeshStandardMaterial({color:0xe9e2d2,roughness:0.4});
  dialMesh=add(new THREE.CylinderGeometry(0.06,0.06,0.01,32),dialM,0,0.105,0.02,phone);
  for(let k=0;k<10;k++){ const a=holeAng(k); add(new THREE.CylinderGeometry(0.0075,0.0075,0.012,10),new THREE.MeshStandardMaterial({color:0x2a2018,roughness:0.6}),Math.cos(a)*0.043,0.004,Math.sin(a)*0.043,dialMesh); }
  for(const x of [-0.07,0.07]) add(new THREE.BoxGeometry(0.03,0.03,0.04),RED,x,0.085,-0.06,phone); }
phone.updateMatrixWorld();
const CRADLE_W=new THREE.Vector3(); phone.localToWorld(CRADLE_W.set(0,0.115,-0.06));
const CORD_A=new THREE.Vector3(); phone.localToWorld(CORD_A.set(0.11,0.03,-0.02));
const receiver=new THREE.Group(); S.scene.add(receiver);
{ add(new THREE.CapsuleGeometry(0.022,0.16,6,16),RED,0,0,0,receiver).rotation.z=Math.PI/2;
  for(const x of [-0.095,0.095]) add(new THREE.SphereGeometry(0.034,16,12),RED,x,-0.008,0,receiver).scale.set(1,0.7,1); }
const cordM=new THREE.MeshStandardMaterial({color:0xb02e24,roughness:0.5});
let cord=null;
function setCord(a,b){ if(cord){ S.scene.remove(cord); cord.geometry.dispose(); }
  const mid=a.clone().lerp(b,0.5).add(V(0,-0.12-0.1*(1-clamp(a.distanceTo(b)/0.5)),0.04));
  const base=new THREE.QuadraticBezierCurve3(a,mid,b), pts=[];
  for(let i=0;i<=160;i++){ const u=i/160, p=base.getPoint(u), tg=base.getTangent(u); const n=V(0,1,0).cross(tg).normalize(), bn=tg.clone().cross(n);
    const ang=u*Math.PI*2*26; pts.push(p.addScaledVector(n,0.012*Math.cos(ang)).addScaledVector(bn,0.012*Math.sin(ang))); }
  cord=new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts),320,0.0035,6,false),cordM); cord.castShadow=true; S.scene.add(cord); }

// ---------------------------------------------------------------- the smartphone (arrives at phoneIn, dies at deadAt)
const SP_BASE=V(0.18,DESK_TOP+0.006,-0.38), SP_YAW=-0.3;
function screenTex(){ const c=document.createElement('canvas'); c.width=256; c.height=512; const g=c.getContext('2d');
  const gr=g.createLinearGradient(0,0,0,512); gr.addColorStop(0,'#c9d6ff'); gr.addColorStop(1,'#6f86d6'); g.fillStyle=gr; g.fillRect(0,0,256,512);
  g.fillStyle='rgba(20,28,60,0.75)'; g.font='700 36px "JetBrains Mono"'; g.textAlign='center'; g.fillText('CONTACTS',128,70);
  for(let i=0;i<9;i++){ g.fillStyle=`rgba(30,40,70,${0.18+0.05*(i%3)})`; g.beginPath(); g.roundRect(26,110+i*44,204,28,8); g.fill(); g.fillStyle='rgba(255,178,77,0.8)'; g.beginPath(); g.arc(40,124+i*44,7,0,6.3); g.fill(); }
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; return t; }
const spGroup=new THREE.Group(); S.scene.add(spGroup);
add(new THREE.BoxGeometry(0.118,0.018,0.222),new THREE.MeshStandardMaterial({color:0x0c0e16,roughness:0.25,metalness:0.5}),0,0,0,spGroup);
const spScreenMat=new THREE.MeshBasicMaterial({map:screenTex(),toneMapped:false,color:0xffffff});
const spScreen=new THREE.Mesh(new THREE.PlaneGeometry(0.1,0.196),spScreenMat); spScreen.rotation.x=-Math.PI/2; spScreen.position.y=0.0095; spGroup.add(spScreen);
const spLight=new THREE.PointLight(0xcfe0ff,0.0,2.2,2); S.scene.add(spLight);

// ---------------------------------------------------------------- the ten numbers
const NUMS={HOME:'2754 3189',NANI:'2471 0638',RAHUL:'2765 4402',PRIYA:'2331 9087',CHINTU:'2490 1176',TUITION:'2718 5530',ARJUN:'2385 6621',MAMAYYA:'2603 7714',KAVYA:'2444 9015','SURESH UNCLE':'2559 2048'};
const ORDER=['HOME','NANI','RAHUL','PRIYA','CHINTU','TUITION','ARJUN','MAMAYYA','KAVYA','SURESH UNCLE'];
function cardTex(name,num){ const c=document.createElement('canvas'); c.width=512; c.height=200; const g=c.getContext('2d');
  const grd=g.createRadialGradient(256,100,10,256,100,250); grd.addColorStop(0,'rgba(255,178,77,0.20)'); grd.addColorStop(1,'rgba(255,178,77,0)');
  g.fillStyle=grd; g.fillRect(0,0,512,200);
  g.strokeStyle='rgba(255,190,110,0.55)'; g.lineWidth=3; g.beginPath(); g.roundRect(18,18,476,164,18); g.stroke();
  g.fillStyle='rgba(255,214,160,0.85)'; g.font='600 34px "JetBrains Mono", monospace'; g.textAlign='center'; g.letterSpacing='8px'; g.fillText(name,256,74);
  g.fillStyle='#ffc77a'; g.font='700 64px "JetBrains Mono", monospace'; g.letterSpacing='4px'; g.fillText(num,256,146);
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; t.anisotropy=8; return t; }
const DEP={}; TL.depart.forEach(([n,t])=>{ DEP[n]=t; });
const LAY={HOME:[-0.42,0.08],NANI:[-0.5,0.26],RAHUL:[-0.4,0.44],PRIYA:[-0.33,0.62],CHINTU:[0,0.64],TUITION:[0.33,0.62],ARJUN:[0.4,0.44],MAMAYYA:[0,0.46],KAVYA:[0.5,0.26],'SURESH UNCLE':[0.42,0.08]};
const CARDS=ORDER.map((name,i)=>{ const Rn=rng(100+i);
  const mat=new THREE.MeshBasicMaterial({map:cardTex(name,NUMS[name]),transparent:true,depthWrite:false,depthTest:false,blending:THREE.AdditiveBlending,toneMapped:false,fog:false,color:0xffffff});
  const m=new THREE.Mesh(new THREE.PlaneGeometry(0.26,0.101),mat); m.renderOrder=6; S.scene.add(m);
  return {i,name,m,mat,off:LAY[name],dz:-0.3-0.15*(i%3)/2,ph:Rn()*6.283,sp:0.5+Rn()*0.4,dep:DEP[name]??null}; });
const light=new THREE.PointLight(AMBER,0.3,2.6,2); light.position.set(0,1.75,CH_Z-0.1); S.scene.add(light);

// ---------------------------------------------------------------- boy
const boy=R.makeFig(PAL.CREAM,'boy',{rim:0.14,lift:0.02});
const ROOT=V(0,0,CH_Z+0.05), YAW=yawOf(V(0,0,1));
const grow=t=>sm5(sstep(TL.growA,TL.growB,t));
const Kof=t=>lerp(0.72,0.96,grow(t));
function scaleFig(F,root,k){ for(const m of F.all){ m.position.sub(root).multiplyScalar(k).add(root); m.scale.multiplyScalar(k); } }
const bump=(t,a,d)=>{ const x=(t-a)/d; return x<=0||x>=1?0:Math.sin(Math.PI*x)**2; };

// ---------------------------------------------------------------- the landline dial: pulls [t0, hole, amplitude rad]
const PULLS=[...TL.pullsIntro,...TL.pullsEnd];
const D_APP=0.28, D_PULL=0.42, D_HOLD=0.06, D_RET=0.3, HOVER=0.075;
function dialKeys(){ const th=[],hh=[]; for(const [t0,k,amp] of PULLS){ const a=holeAng(k);
    th.push([t0-D_APP,a],[t0,a],[t0+D_PULL,a+amp],[t0+D_PULL+D_HOLD,a+amp],[t0+D_PULL+D_HOLD+0.05,a+amp]);
    hh.push([t0-D_APP,HOVER],[t0,0],[t0+D_PULL+D_HOLD,0],[t0+D_PULL+D_HOLD+0.14,HOVER]); }
  return {th,hh}; }
const DK=dialKeys();
function seqAt(K,t){ if(t<=K[0][0]) return K[0][1]; for(let i=1;i<K.length;i++){ if(t<=K[i][0]){ const u=(t-K[i-1][0])/Math.max(1e-6,K[i][0]-K[i-1][0]); return lerp(K[i-1][1],K[i][1],u*u*(3-2*u)); } } return K[K.length-1][1]; }
function wheelAt(t){ for(const [t0,k,amp] of PULLS){ if(t>=t0-0.01&&t<=t0+D_PULL+D_HOLD+D_RET){ const u=t-t0;
      if(u<D_PULL) return amp*sm5(clamp(u/D_PULL)); if(u<D_PULL+D_HOLD) return amp; return amp*(1-sm5(clamp((u-D_PULL-D_HOLD)/D_RET))); } } return 0; }
function dialWeight(t){ let w=0; for(const g of [TL.pullsIntro,TL.pullsEnd]){ const a=g[0][0]-0.55, b=g[g.length-1][0]+D_PULL+D_HOLD+0.4; w=Math.max(w,sstep(a,a+0.35,t)*(1-sstep(b-0.3,b+0.1,t))); } return w; }

// ---------------------------------------------------------------- camera: slow push-in that follows him up as he grows
function camAt(t){ const u=sm5(clamp(t/DUR)), g=grow(t);
  const tg=V(0.05,lerp(1.27,1.34,g),lerp(-0.4,-0.45,u)), dist=lerp(3.0,2.75,u)+0.3*g-0.28*sstep(14.5,TL.duration,t), az=lerp(0.3,0.16,u), el=lerp(0.15,0.1,u);
  return {pos:tg.clone().add(V(Math.sin(az)*Math.cos(el),Math.sin(el),Math.cos(az)*Math.cos(el)).multiplyScalar(dist)),tg}; }

// ---------------------------------------------------------------- one frame
const ageAt=t=>10+Math.floor(20*grow(t)+1e-6);
const countAt=t=>10-TL.depart.filter(([n,d])=>t>=d+TL.fly).length;
const phoneOn=t=>{ if(t<TL.phoneIn) return 0; if(t<TL.flickerFrom) return 1; if(t<TL.deadAt){ const f=(t-TL.flickerFrom)/(TL.deadAt-TL.flickerFrom); return Math.sin(f*47)>-0.2-0.6*f?1-0.6*f*Math.abs(Math.sin(f*31)):0.15; } return 0; };
const PULSE=TL.depart.map(([n,d])=>d+TL.fly);

function setT(t){
  const cam=camAt(t); S.cam.position.copy(cam.pos); S.cam.lookAt(cam.tg);
  const g=grow(t), K=Kof(t), pOn=phoneOn(t);
  const rv1=TL.recv1, rv2=TL.recv2;
  const lift1=sm5(sstep(rv1[0],rv1[0]+0.55,t))*(1-sm5(sstep(rv1[1],rv1[1]+0.5,t)));
  const lift2=sm5(sstep(rv2[0],rv2[0]+0.55,t));
  const lift=Math.max(lift1,lift2);
  const useRecv=Math.max(sstep(rv1[0]-0.35,rv1[0],t)*(1-sstep(rv1[1]+0.5,rv1[1]+0.8,t)), sstep(rv2[0]-0.35,rv2[0],t));
  const using=sstep(TL.phoneIn+0.2,TL.phoneIn+0.9,t)*(1-sstep(TL.setDown-0.25,TL.setDown,t));
  const look=sstep(TL.shake[1],TL.setDown+0.3,t);
  const dial=dialWeight(t), late=t>TL.setDown?1:0;
  let glance=0; for(const c of CARDS){ if(c.dep!==null) glance+=bump(t,c.dep-0.1,TL.fly+0.35)*Math.max(-1,Math.min(1,c.off[0]*2.2)); }
  const P={...R.P0,p:0.14,tilt:0.05,aL:1.55,aR:1.5,kL:1.25,kR:1.35,sL:0.5,sR:0.5,eL:0.9,eR:0.9,dy:0.43/K-0.485};
  P.p+=0.02*Math.sin(t*1.6)+0.05*using+0.1*g;
  P.tilt=0.3*(1-sstep(rv1[0]-0.2,rv1[0]+0.5,t))*(t<TL.phoneIn+0.2?1:0)+0.34*using+0.14*dial*late-0.2*lift+0.02;
  P.hy=-0.05+0.2*using-0.4*look*(1-lift)+0.18*lift-0.1*dial*late+0.28*glance*using;
  P.tilt-=0.12*Math.abs(glance)*using;
  const relief=sm5(sstep(TL.answer,TL.answer+0.9,t)); P.p+=0.07*relief; P.tilt+=0.12*relief;
  const Jp=R.skel(P,ROOT,YAW), headW=ROOT.clone().add(Jp.head.clone().sub(ROOT).multiplyScalar(K));
  const unK=p=>p.clone().sub(ROOT).multiplyScalar(1/K).add(ROOT);
  // landline dial hand (camera-left hand)
  const th=seqAt(DK.th,t), hh=seqAt(DK.hh,t), hgt=0.122+0.058*K+hh;
  const dialHand=phone.localToWorld(V(Math.cos(th)*0.043,hgt,0.02+Math.sin(th)*0.043));
  const restL=V(-0.3,DESK_TOP+0.04,-0.26);
  const handL=restL.clone().lerp(dialHand,dial);
  dialMesh.rotation.y=-wheelAt(t);
  // receiver
  const ear=headW.clone().add(V(0.085,-0.06,0.03)), cr=CRADLE_W.clone();
  const recvAt=cr.clone().lerp(ear,lift).add(V(0,0.12*Math.sin(Math.PI*lift),0));
  receiver.position.copy(recvAt); receiver.rotation.set(0,lerp(0.35,0.2,lift),lerp(0,1.25,lift));
  setCord(CORD_A,receiver.localToWorld(V(0.1,-0.01,0)));
  // smartphone: appears, taps, shaken at the end, goes dark
  const spPop=sm5(sstep(TL.phoneIn,TL.phoneIn+0.3,t)); spGroup.visible=spPop>0.01; spGroup.scale.setScalar(Math.max(0.01,spPop)*1.45);
  const shaking=(t>TL.shake[0]&&t<TL.shake[1])?1:0, held=0;
  const spHold=headW.clone().add(V(0.12,-0.34,0.28)); spHold.y=Math.max(spHold.y,DESK_TOP+0.2);
  const spPos=SP_BASE.clone().lerp(spHold,sm5(held));
  spPos.x+=0.025*Math.sin(t*38)*held*shaking; spPos.y+=0.02*Math.sin(t*31)*held*shaking;
  spGroup.position.copy(spPos); spGroup.rotation.set(-0.5*held,SP_YAW*(1-held),0.12*Math.sin(t*34)*held*shaking);
  let bright=pOn*0.62; for(const d of PULSE) bright+=pOn*0.5*bump(t,d-0.1,0.35);
  spScreenMat.color.setScalar(bright); spLight.position.copy(spPos).add(V(0.05,0.5,0.3)); spLight.intensity=0.12*pOn;
  // right hand: smartphone (tap), shaking it, or the receiver
  const tapD=x=>{ const f=x%1; return 0.022*sstep(0,0.08,f)*(1-sstep(0.08,0.22,f)); }, dip=tapD(t*2.7)*(1-shaking)+0.03*tapD(t*5.6)*shaking;
  const tapPos=SP_BASE.clone().add(V(0.0,0.08-dip,0.03*Math.sin(t*1.9)));
  const restR=SP_BASE.clone().add(V(0.0,0.075,0.0));
  let baseR=restR.clone().lerp(tapPos,using);
  baseR=baseR.lerp(spPos.clone().add(V(0.0,0.07,0.0)),sm5(held));
  const handR=baseR.clone().lerp(recvAt.clone().add(V(0.02,-0.03,0)),useRecv);
  Object.assign(P,{tL:unK(handL),wL:1,pL:V(-0.3,-0.8,0.6),tR:unK(handR),wR:1,pR:V(-0.2,-1,0.25)});
  R.poseFig(boy,R.skel(P,ROOT,YAW)); scaleFig(boy,ROOT,K);
  RED.color.set(PAL.RED).multiplyScalar(lerp(1,0.78,g));
  // cards
  const cy=lerp(1.12,1.26,g), spTarget=spPos.clone().add(V(0,0.05,0));
  const homeC=sm5(sstep(TL.homeCenterFrom,TL.homeCenterTo,t));
  for(const c of CARDS){ const b=0.03*Math.sin(t*c.sp+c.ph), b2=0.02*Math.cos(t*c.sp*0.7+c.ph);
    const home=V(c.off[0]*0.84-0.07,cy+c.off[1],CH_Z+c.dz).add(V(b2,b,0));
    let pos=home.clone(), sc=1, k=0.78+0.12*Math.sin(t*1.7+c.ph), vis=true;
    if(c.dep!==null){ const u=(t-c.dep)/TL.fly; if(u>=1) vis=false; else if(u>0){ const e=sm5(u); pos=home.clone().lerp(spTarget,e); pos.y+=0.4*Math.sin(Math.PI*e); pos.z+=0.55*Math.sin(Math.PI*e); sc=lerp(1,0.3,e); k*=1-0.9*sstep(0.7,1,u); } }
    else { const center=V(-0.03,cy+0.3,CH_Z-0.1); pos.lerp(center,homeC); let pl=0; for(const [t0] of TL.pullsEnd) pl+=bump(t,t0,0.5)*0.5; for(const r of TL.ringAt) pl+=bump(t,r+0.02,1.0)*0.9; pl+=0.8*bump(t,TL.answer,1.4);
      sc=lerp(1,1.55,homeC)*(1+0.1*pl); k=lerp(k,1.15+0.2*Math.sin(t*3.2),homeC)+0.55*pl; }
    c.m.visible=vis; c.m.position.copy(pos); c.m.scale.setScalar(sc); c.m.lookAt(S.cam.position); c.mat.color.setScalar(k); }
  // lamp: dips when the phone dies, warms when the line is answered
  const dipL=sm5(sstep(TL.deadAt-0.1,TL.deadAt+0.25,t))*(1-sm5(sstep(TL.setDown,TL.setDown+0.9,t)));
  const warm=sm5(sstep(TL.warmAt,TL.warmAt+0.9,t));
  S.tick(t,0.16*warm-0.62*dipL); light.intensity=(0.3+0.04*Math.sin(t*1.3))*(1-0.5*dipL)+0.1*warm;
}
window.metaAt=t=>({age:ageAt(t),count:countAt(t)});
window.events={...TL};
window.renderAt=(t,Ks=3)=>S.renderAt(setT,t,Ks,{t0:0,t1:DUR});
window.ready=true;
