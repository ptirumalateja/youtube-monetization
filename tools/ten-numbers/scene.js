// Ten Numbers (Slow Light, logo palette: navy room, amber light, cream text).
// Look test: the hook beat. A 10-year-old at a desk under the lamp dials the red landline; the ten numbers he knows by
// heart float around him as glowing amber cards. renderAt(t) is pure (no state between frames).
import * as THREE from 'three';
import * as SLD from './sld.js';
const {V,clamp,sstep,lerp,sm5,rng,yawOf,PAL}=SLD;
await Promise.all([document.fonts.load('700 64px "JetBrains Mono"'),document.fonts.load('600 34px "JetBrains Mono"')]);
const TL=await (await fetch('./timeline.json')).json();
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960, DUR=TL.duration;

// ---------------------------------------------------------------- palette: Slow Light logo
const NAVY=0x161c2c, AMBER=0xffb24d;
const DESK_TOP=0.74, LAMP=V(0.05,3.3,0.15), AIM=V(0,0.7,-0.25);
const S=SLD.createStage({W,H,lamp:LAMP,lampTarget:AIM,cone:0.36,spot:17,beam:0.045,motes:1400,
  bg:NAVY,fog:0.04,hemi:1.1,hemiSky:0x3a4a7a,vig:0.25,floorCol:0x3a4058,fov:36});
S.spot.color.set(0xffc070); S.beamU.uCol.value.set(0xffb860);
S.spot.shadow.camera.far=6;
const R=SLD.createRig(S.scene);
// back wall: navy plaster, so the frame reads as a room (not a black void) and the edges stay off black
{ const wt=SLD.noiseTex(256,11,70,26,60,0.04); wt.repeat.set(3,2);
  const wall=new THREE.Mesh(new THREE.PlaneGeometry(14,7),new THREE.MeshStandardMaterial({color:0x2c3554,roughness:0.95,map:wt,emissive:0x182036,emissiveIntensity:1}));
  wall.position.set(0,3.5,-1.9); wall.receiveShadow=true; S.scene.add(wall); }

// ---------------------------------------------------------------- wood
function woodTex(seed,base){ const c=document.createElement('canvas'); c.width=1024; c.height=256; const g=c.getContext('2d'); const Rn=rng(seed);
  g.fillStyle=base; g.fillRect(0,0,1024,256);
  for(let k=0;k<260;k++){ const y=Rn()*256, a=0.04+Rn()*0.1; g.strokeStyle=Rn()<0.6?`rgba(0,0,0,${a})`:`rgba(255,220,180,${a*0.5})`; g.lineWidth=0.6+Rn()*2.2;
    g.beginPath(); g.moveTo(0,y); for(let x=0;x<=1024;x+=32) g.lineTo(x,y+Math.sin(x*0.004+k)*3+Math.sin(x*0.021+k*1.7)*1.2); g.stroke(); }
  const t=new THREE.CanvasTexture(c); t.wrapS=t.wrapT=THREE.RepeatWrapping; t.colorSpace=THREE.SRGBColorSpace; return t; }
const WOOD=new THREE.MeshStandardMaterial({color:0x8a6a52,map:woodTex(3,'#3b2a1f'),roughness:0.5});
SLD.rimify(WOOD,0xffe6c8,0.05,'wood');
const add=(geo,mat,x,y,z,par=S.scene)=>{ const m=new THREE.Mesh(geo,mat); m.position.set(x,y,z); m.castShadow=m.receiveShadow=true; par.add(m); return m; };

// desk (x across, z depth) and the kid's chair behind it
add(new THREE.BoxGeometry(1.3,0.05,0.62),WOOD,0,DESK_TOP-0.025,0);
for(const x of [-0.6,0.6]) for(const z of [-0.26,0.26]) add(new THREE.BoxGeometry(0.06,DESK_TOP-0.05,0.06),WOOD,x,(DESK_TOP-0.05)/2,z);
add(new THREE.BoxGeometry(1.24,0.5,0.03),WOOD,0,DESK_TOP-0.3,0.285);   // modesty panel: hides the dangling legs
const CH_Z=-0.62;
{ const g=new THREE.Group(); g.position.set(0,0,CH_Z); S.scene.add(g);
  add(new THREE.BoxGeometry(0.42,0.04,0.42),WOOD,0,0.47,0,g);
  for(const x of [-0.18,0.18]) for(const z of [-0.18,0.18]) add(new THREE.BoxGeometry(0.035,0.47,0.035),WOOD,x,0.235,z,g);
  for(const x of [-0.18,0.18]) add(new THREE.BoxGeometry(0.035,0.55,0.035),WOOD,x,0.75,-0.19,g);
  add(new THREE.BoxGeometry(0.4,0.12,0.03),WOOD,0,0.93,-0.19,g); }

// ---------------------------------------------------------------- the red landline (the one red object)
const RED=new THREE.MeshStandardMaterial({color:PAL.RED,roughness:0.35,emissive:PAL.RED,emissiveIntensity:0.04});
SLD.rimify(RED,0xff9a80,0.14,'phone');
const PH=V(-0.12,DESK_TOP,-0.3);
let dialMesh=null;
const phone=new THREE.Group(); phone.position.copy(PH); phone.rotation.y=0.35; S.scene.add(phone);
{ const body=add(new THREE.BoxGeometry(0.22,0.07,0.2),RED,0,0.035,0,phone); body.geometry.translate(0,0,0);
  const top=add(new THREE.CylinderGeometry(0.075,0.09,0.03,32),RED,0,0.085,0.02,phone);
  const dialM=new THREE.MeshStandardMaterial({color:0xe9e2d2,roughness:0.4});
  dialMesh=add(new THREE.CylinderGeometry(0.06,0.06,0.01,32),dialM,0,0.105,0.02,phone);
  for(let k=0;k<10;k++){ const a=k/10*Math.PI*2*0.8+0.5; add(new THREE.CylinderGeometry(0.0075,0.0075,0.012,10),new THREE.MeshStandardMaterial({color:0x2a2018,roughness:0.6}),Math.cos(a)*0.043,0.004,Math.sin(a)*0.043,dialMesh); }
  for(const x of [-0.07,0.07]) add(new THREE.BoxGeometry(0.03,0.03,0.04),RED,x,0.085,-0.06,phone); }   // cradle forks
const DIAL_W=new THREE.Vector3(); phone.updateMatrixWorld(); phone.localToWorld(DIAL_W.set(0,0.11,0.02));
const CRADLE_W=new THREE.Vector3(); phone.localToWorld(CRADLE_W.set(0,0.115,-0.06));
const receiver=new THREE.Group(); S.scene.add(receiver);
{ add(new THREE.CapsuleGeometry(0.022,0.16,6,16),RED,0,0,0,receiver).rotation.z=Math.PI/2;
  for(const x of [-0.095,0.095]) add(new THREE.SphereGeometry(0.034,16,12),RED,x,-0.008,0,receiver).scale.set(1,0.7,1); }
// coiled cord: a tube along a helix from the phone body to the receiver
const cordM=new THREE.MeshStandardMaterial({color:0xb02e24,roughness:0.5});
let cord=null;
function setCord(a,b){ if(cord){ S.scene.remove(cord); cord.geometry.dispose(); }
  const mid=a.clone().lerp(b,0.5).add(V(0,-0.12-0.1*(1-clamp(a.distanceTo(b)/0.5)),0.04));
  const base=new THREE.QuadraticBezierCurve3(a,mid,b), pts=[];
  for(let i=0;i<=160;i++){ const u=i/160, p=base.getPoint(u), tg=base.getTangent(u); const n=V(0,1,0).cross(tg).normalize(), bn=tg.clone().cross(n);
    const ang=u*Math.PI*2*26; pts.push(p.addScaledVector(n,0.012*Math.cos(ang)).addScaledVector(bn,0.012*Math.sin(ang))); }
  cord=new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts),320,0.0035,6,false),cordM); cord.castShadow=true; S.scene.add(cord); }
const CORD_A=new THREE.Vector3(); phone.localToWorld(CORD_A.set(0.11,0.03,-0.02));

// ---------------------------------------------------------------- the ten numbers: amber cards floating around him
const NUMS=[['HOME','2754 3189'],['NANI','2471 0638'],['RAHUL','2765 4402'],['PRIYA','2331 9087'],['CHINTU','2490 1176'],
  ['TUITION','2718 5530'],['ARJUN','2385 6621'],['MAMAYYA','2603 7714'],['KAVYA','2444 9015'],['SURESH UNCLE','2559 2048']];
function cardTex(name,num){ const c=document.createElement('canvas'); c.width=512; c.height=200; const g=c.getContext('2d');
  g.clearRect(0,0,512,200);
  const grd=g.createRadialGradient(256,100,10,256,100,250); grd.addColorStop(0,'rgba(255,178,77,0.20)'); grd.addColorStop(1,'rgba(255,178,77,0)');
  g.fillStyle=grd; g.fillRect(0,0,512,200);
  g.strokeStyle='rgba(255,190,110,0.55)'; g.lineWidth=3; g.beginPath(); g.roundRect(18,18,476,164,18); g.stroke();
  g.fillStyle='rgba(255,214,160,0.85)'; g.font='600 34px "JetBrains Mono", monospace'; g.textAlign='center'; g.letterSpacing='8px'; g.fillText(name,256,74);
  g.fillStyle='#ffc77a'; g.font='700 64px "JetBrains Mono", monospace'; g.letterSpacing='4px'; g.fillText(num,256,146);
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; t.anisotropy=8; return t; }
const HEAD0=V(0,1.12,CH_Z+0.08);
const CARDS=NUMS.map(([name,num],i)=>{ const Rn=rng(100+i);
  const a=lerp(-2.0,2.0,i/9)+(Rn()-0.5)*0.06, r=0.5+(i%2)*0.1;
  const home=V(Math.sin(a)*r*0.85, 1.3+Math.cos(a)*r*0.62, CH_Z-0.22-0.2*(i%3)/2);
  const mat=new THREE.MeshBasicMaterial({map:cardTex(name,num),transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,toneMapped:false,fog:false,color:0xffffff});
  const m=new THREE.Mesh(new THREE.PlaneGeometry(0.3,0.117),mat); m.renderOrder=6; S.scene.add(m);
  const halo=SLD.glowSprite(S.scene,AMBER,0.0);
  return {i,name,m,mat,halo,home,ph:Rn()*6.283,sp:0.5+Rn()*0.4}; });
const light=new THREE.PointLight(AMBER,0.3,2.6,2); light.position.set(0,1.75,CH_Z-0.1); S.scene.add(light);   // the numbers light him from behind

// ---------------------------------------------------------------- the boy (cream, 0.72 scale, feet dangling off the chair)
const boy=R.makeFig(PAL.CREAM,'boy',{rim:0.14,lift:0.02});
const K=0.72, ROOT=V(0,0,CH_Z+0.05), YAW=yawOf(V(0,0,1));
const SITP={...R.P0,p:0.14,tilt:0.05,aL:1.55,aR:1.5,kL:1.25,kR:1.35,sL:0.5,sR:0.5,eL:0.9,eR:0.9,dy:0.07};
function scaleFig(F,root,k){ for(const m of F.all){ m.position.sub(root).multiplyScalar(k).add(root); m.scale.multiplyScalar(k); } }
const unK=p=>p.clone().sub(ROOT).multiplyScalar(1/K).add(ROOT);       // world target -> unscaled rig space

// ---------------------------------------------------------------- camera: slow push-in, low three-quarter, settling on him
function camAt(t){ const u=sm5(clamp(t/DUR));
  const tg=V(0.07,lerp(1.2,1.16,u),lerp(-0.3,-0.35,u)), dist=lerp(3.5,2.95,u), az=lerp(0.3,0.18,u), el=lerp(0.36,0.3,u);
  return {pos:tg.clone().add(V(Math.sin(az)*Math.cos(el),Math.sin(el),Math.cos(az)*Math.cos(el)).multiplyScalar(dist)),tg}; }

// ---------------------------------------------------------------- one frame
const bump=(t,a,d)=>{ const x=(t-a)/d; return x<=0||x>=1?0:Math.sin(Math.PI*x)**2; };
function setT(t){
  const cam=camAt(t); S.cam.position.copy(cam.pos); S.cam.lookAt(cam.tg);
  // boy: dials the first digits (right hand circles on the dial), then lifts the receiver to his ear and waits
  const P={...SITP}; P.hy=0.25*Math.sin(t*0.8)*0.3+lerp(-0.05,0.18,sstep(TL.lift,TL.lift+0.5,t)); P.tilt=lerp(0.32,0.02,sstep(TL.lift-0.2,TL.lift+0.5,t));
  P.p+=lerp(0.18,0.02,sstep(TL.lift-0.2,TL.lift+0.5,t));
  // right hand: dialing (one finger, small arcs) until the lift, then rests on the desk edge
  const dialing=1-sstep(TL.lift-0.3,TL.lift,t), spin=(t*2.4)%1, arc=Math.sin(Math.PI*spin)*0.9;
  const th=0.6+arc*1.7;   // finger in a hole, drags the wheel clockwise, lets go, returns
  const dialHand=phone.localToWorld(V(Math.cos(th)*0.043,0.135,0.02+Math.sin(th)*0.043));
  dialMesh.rotation.y=-(arc*1.7)*0.9;
  const restR=V(-0.2,DESK_TOP+0.03,-0.16);
  const hR=restR.clone().lerp(dialHand,dialing);
  // left hand: holds the receiver to his ear after TL.lift
  const lift=sm5(sstep(TL.lift,TL.lift+0.55,t));
  R.poseFig(boy,R.skel(P,ROOT,YAW)); scaleFig(boy,ROOT,K); const hd=boy.head.position.clone();
  const ear=hd.clone().add(V(0.085,-0.06,0.03)), cr=CRADLE_W.clone();
  const recvAt=cr.clone().lerp(ear,lift).add(V(0,0.12*Math.sin(Math.PI*lift),0));
  const restL=V(0.18,DESK_TOP+0.03,-0.14), hL=restL.clone().lerp(cr,sstep(TL.lift-0.35,TL.lift,t)*(1-lift)).lerp(recvAt.clone().add(V(-0.02,-0.03,0)),lift);
  Object.assign(P,{tL:unK(hR),wL:1,pL:V(-0.3,-0.8,0.6),tR:unK(hL),wR:1,pR:V(-0.3,-0.9,-0.5)});   // L hand dials (camera-left), R hand takes the receiver
  R.poseFig(boy,R.skel(P,ROOT,YAW)); scaleFig(boy,ROOT,K);
  receiver.position.copy(recvAt); receiver.rotation.set(0,lerp(0.35,0.2,lift),lerp(0,1.25,lift));
  setCord(CORD_A,receiver.localToWorld(V(0.1,-0.01,0)));
  // cards: drift and breathe; the one he is dialing (RAHUL) flares as he dials it
  for(const c of CARDS){ const b=0.03*Math.sin(t*c.sp+c.ph), b2=0.02*Math.cos(t*c.sp*0.7+c.ph);
    c.m.position.copy(c.home).add(V(b2,b,0)); c.m.lookAt(S.cam.position);
    const flare=c.name==='RAHUL'?sstep(0.3,1.2,t)*(1-sstep(TL.lift+0.6,TL.lift+1.6,t)):0;
    const k=(0.78+0.12*Math.sin(t*1.7+c.ph))*(1+0.6*flare);
    c.mat.color.setScalar(k); c.halo.position.copy(c.m.position).add(V(0,0,-0.02)); c.halo.scale.set(0.6,0.34,1); c.halo.material.opacity=0.05+0.12*flare; }
  S.tick(t,0); light.intensity=0.28+0.04*Math.sin(t*1.3);
}
window.metaAt=t=>({age:10,count:10});
window.renderAt=(t,Ks=3)=>S.renderAt(setT,t,Ks,{t0:0,t1:DUR});
window.ready=true;
