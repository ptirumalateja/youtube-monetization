// Your Parents Are Aging While You Are Busy, V2 (Slow Light Dark): built to Teja's V2 brief, "stupid simple" like 30 Friends.
// One table, one warm lamp, three chairs, three ages. AT 8 the three of them eat together (he sits on our side, back to us).
// AT 18 he grows up in his chair, takes his bag, pushes the chair back and walks away into the dark toward his desk and bed;
// Mom calls, he picks up while walking. AT 25: one fixed wide shot of the whole distance; Mom grey, Dad bent with a stick;
// their plates full, his empty and dusty; she calls, he doesn't pick up; the lamp cools and dims. Black for 0.2 s, then a slow
// push-in on his empty chair: their sweaters on their chairs, the red phone by his empty plate rings once, then silence.
//
// Units are metres; floor y = 0; the table's long axis is x, the camera is on +z. renderAt(t) is pure (parallel workers).
import * as THREE from 'three';
import * as SLD from './sld.js';
const {V,clamp,sstep,lerp,sm5,rng,yawOf,PAL,UPV,keys}=SLD;
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960;
const TL=await (await fetch('./'+(q.get('tl')||'timeline.json'))).json(); const DUR=TL.duration;
const bump=(t,a,d)=>{ const x=(t-a)/d; return x<=0||x>=1?0:Math.sin(Math.PI*x)**2; };
const win=(t,a,b,f=0.2)=>sstep(a,a+f,t)*(1-sstep(b-f,b,t));
const SC=TL.scenes;   // [s1 start, s2, s3, black, s4]

// ---------------------------------------------------------------- stage: one warm lamp over the table (Friends), dust, mirror floor
const TOP=0.74;
const LAMP=V(0.1,4.7,0.55), AIM=V(0.08,0,0.15), CONE=0.4;
const S=SLD.createStage({W,H,lamp:LAMP,lampTarget:AIM,cone:CONE,spot:TL.spot??50,beam:0.12,motes:2400});
const R=SLD.createRig(S.scene);
S.spot.shadow.camera.far=9;
const beamMesh=S.NOREFL[0];
beamMesh.material.fragmentShader=beamMesh.material.fragmentShader.replace('float acc=0.0;','float acc=0.0; float jit=fract(sin(dot(gl_FragCoord.xy,vec2(12.9898,78.233)))*43758.5453)-0.5;')
  .replace('float s=tEnd*(float(i)+0.5)/16.0;','float s=tEnd*(float(i)+0.5+jit)/16.0;'); beamMesh.material.needsUpdate=true;
function aim(target,cone){ const d=target.clone().sub(LAMP).normalize();
  S.spot.target.position.copy(target); S.spot.target.updateMatrixWorld(); S.spot.angle=cone+0.08;
  S.beamU.uAxis.value.copy(d); S.beamU.uTan.value=Math.tan(cone); S.moteU.uTan.value=Math.tan(cone);
  beamMesh.quaternion.setFromUnitVectors(V(0,-1,0),d); }
aim(AIM,CONE);
const GOLD=new THREE.Color(PAL.GOLD), COLD=new THREE.Color(0xb8c2d6);

// ---------------------------------------------------------------- materials (the Friends table and chairs)
function woodTex(seed,base){ const c=document.createElement('canvas'); c.width=1024; c.height=256; const g=c.getContext('2d'); const Rn=rng(seed);
  g.fillStyle=base; g.fillRect(0,0,1024,256);
  for(let k=0;k<260;k++){ const y=Rn()*256, a=0.04+Rn()*0.1; g.strokeStyle=Rn()<0.6?`rgba(0,0,0,${a})`:`rgba(255,220,180,${a*0.5})`; g.lineWidth=0.6+Rn()*2.2;
    g.beginPath(); g.moveTo(0,y); for(let x=0;x<=1024;x+=32) g.lineTo(x,y+Math.sin(x*0.004+k)*3+Math.sin(x*0.021+k*1.7)*1.2); g.stroke(); }
  const t=new THREE.CanvasTexture(c); t.wrapS=t.wrapT=THREE.RepeatWrapping; t.colorSpace=THREE.SRGBColorSpace; return t; }
function plaidTex(){ const c=document.createElement('canvas'); c.width=c.height=256; const g=c.getContext('2d'); g.fillStyle='#2b3b6a'; g.fillRect(0,0,256,256);
  for(let i=0;i<4;i++){ g.fillStyle='rgba(120,150,220,0.42)'; g.fillRect(i*64+8,0,22,256); g.fillRect(0,i*64+8,256,22); g.fillStyle='rgba(10,16,40,0.35)'; g.fillRect(i*64+36,0,6,256); g.fillRect(0,i*64+36,256,6); }
  const t=new THREE.CanvasTexture(c); t.wrapS=t.wrapT=THREE.RepeatWrapping; t.repeat.set(3,2); t.colorSpace=THREE.SRGBColorSpace; return t; }
const WOOD=new THREE.MeshStandardMaterial({color:0x8a6a52,map:woodTex(3,'#3b2a1f'),roughness:0.5,metalness:0});
const CHAIRWOOD=new THREE.MeshStandardMaterial({color:0x7a5c46,map:woodTex(9,'#33241a'),roughness:0.62,metalness:0});
SLD.rimify(WOOD,0xffe6c8,0.05,'wood'); SLD.rimify(CHAIRWOOD,0xc8d4f0,0.07,'chair');
const std=(color,key,{r=0.6,m=0,rim=0.08,rimCol=0xfff1d8,e=0,ei=0,map=null}={})=>SLD.rimify(new THREE.MeshStandardMaterial({color,roughness:r,metalness:m,emissive:e,emissiveIntensity:ei,map}),rimCol,rim,key);
const STEEL=std(0xc9ccd2,'steel',{r:0.28,m:0.25,rim:0.32});
const PLATE=std(0xe9e4da,'plate',{r:0.35,rim:0.12});
function add(geo,mat,parent=S.scene,cast=true){ const m=new THREE.Mesh(geo,mat); m.castShadow=cast; m.receiveShadow=true; parent.add(m); return m; }
function box(w,h,d,mat,x,y,z,parent){ const m=add(new THREE.BoxGeometry(w,h,d),mat,parent); m.position.set(x,y,z); return m; }

// ---------------------------------------------------------------- the table, three chairs (Mom and Dad across, his on our side)
const TX=0.8, TZ=0.42;
{ const top=box(TX*2,0.05,TZ*2,WOOD,0,TOP-0.025,0); top.material.map.repeat.set(2,1);
  box(TX*2-0.16,0.09,TZ*2-0.12,WOOD,0,TOP-0.095,0);
  for(const x of [-TX+0.07,TX-0.07]) for(const z of [-TZ+0.07,TZ-0.07]) box(0.07,TOP-0.05,0.07,WOOD,x,(TOP-0.05)/2,z); }
const chairGeo={seat:new THREE.BoxGeometry(0.42,0.04,0.42),leg:new THREE.BoxGeometry(0.035,0.44,0.035),post:new THREE.BoxGeometry(0.035,0.5,0.035),rail:new THREE.BoxGeometry(0.03,0.12,0.4)};
function makeChair(){ const g=new THREE.Group(); const a=(geo,x,y,z)=>{ const m=new THREE.Mesh(geo,CHAIRWOOD); m.position.set(x,y,z); m.castShadow=m.receiveShadow=true; g.add(m); };
  a(chairGeo.seat,0,0.44,0); for(const x of [-0.18,0.18]) for(const z of [-0.18,0.18]) a(chairGeo.leg,x,0.22,z);
  for(const z of [-0.18,0.18]) a(chairGeo.post,-0.19,0.71,z); a(chairGeo.rail,-0.19,0.88,0); a(chairGeo.rail,-0.19,0.68,0); S.scene.add(g); return g; }
function placeChair(c,p,facing){ c.position.copy(p); c.rotation.y=yawOf(facing); }
const HIPBACK=0.276, CHAIRP={...R.P0,p:0.07,tilt:0.0,aL:1.5,aR:1.47,kL:1.52,kR:1.47,sL:0.5,sR:0.5,eL:0.9,eR:0.9};
const MOM_X=0.36, DAD_X=-0.36, SON_X=0.0, BACKZ=-0.78, FRONTZ=0.78, FACE_Z=V(0,0,1), FACE_NZ=V(0,0,-1);
const momChair=makeChair(), dadChair=makeChair(), sonChair=makeChair();
placeChair(momChair,V(MOM_X,0,BACKZ),FACE_Z); placeChair(dadChair,V(DAD_X,0,BACKZ),FACE_Z);
const backRoot=x=>V(x,0,BACKZ+0.08+HIPBACK);
// plates: three with warm food (a soft glow) at 8; at 25 theirs full, his empty, dusty, no glow
const PL={mom:V(MOM_X,TOP,-0.2), dad:V(DAD_X,TOP,-0.2), son:V(SON_X,TOP,0.2)};
const food={}, foodM={}; const sonPlateM=PLATE.clone(); SLD.rimify(sonPlateM,0xfff1d8,0.12,'splate');
for(const k in PL){ add(new THREE.CylinderGeometry(0.13,0.11,0.018,32),k==='son'?sonPlateM:PLATE).position.copy(PL[k]).add(V(0,0.009,0));
  foodM[k]=new THREE.MeshStandardMaterial({color:0xe8b56a,roughness:0.6,emissive:0xffb24a,emissiveIntensity:0.35});
  const f=add(new THREE.SphereGeometry(0.075,24,12,0,Math.PI*2,0,Math.PI/2),foodM[k]); f.scale.set(1,0.5,1); f.position.copy(PL[k]).add(V(0,0.018,0)); food[k]=f; }
const bowl=add(new THREE.CylinderGeometry(0.11,0.08,0.09,28),STEEL); bowl.position.set(0.0,TOP+0.045,-0.08);
const bowlFood=add(new THREE.CylinderGeometry(0.1,0.1,0.01,28),foodM.mom); bowlFood.position.set(0.0,TOP+0.085,-0.08);
const ladle=new THREE.Group(); S.scene.add(ladle); { const c=add(new THREE.SphereGeometry(0.035,16,8,0,Math.PI*2,Math.PI/2,Math.PI/2),STEEL,ladle); const h=add(new THREE.CylinderGeometry(0.006,0.006,0.26,8),STEEL,ladle); h.position.set(0,0.13,0); }
for(const [x,z] of [[MOM_X+0.2,-0.22],[DAD_X-0.2,-0.22]]){ add(new THREE.CylinderGeometry(0.03,0.025,0.1,20),STEEL).position.set(x,TOP+0.05,z); }
const steam=[]; for(let i=0;i<3;i++) steam.push(SLD.glowSprite(S.scene,0xffd6a0,0));

// ---------------------------------------------------------------- the red phone (the one red object)
const PH0=V(-0.62,TOP,-0.05), PH_END=V(0.28,TOP,0.24);
const redM=new THREE.MeshStandardMaterial({color:PAL.RED,roughness:0.42,metalness:0,emissive:PAL.RED,emissiveIntensity:0.05}); SLD.rimify(redM,0xff8a70,0.14,'phone');
const phone=new THREE.Group(); S.scene.add(phone);
{ const b=new THREE.Mesh(new THREE.BoxGeometry(0.21,0.07,0.17),redM); b.position.y=0.035; b.castShadow=true; phone.add(b);
  const b2=new THREE.Mesh(new THREE.BoxGeometry(0.17,0.04,0.13),redM); b2.position.set(0,0.085,0.005); b2.rotation.x=-0.25; b2.castShadow=true; phone.add(b2);
  const dial=new THREE.Mesh(new THREE.CylinderGeometry(0.042,0.042,0.008,28),std(0xe8dcc8,'dial',{r:0.4,rim:0.1})); dial.position.set(0,0.108,0.03); dial.rotation.x=-0.25; phone.add(dial);
  for(const x of [-0.07,0.07]){ const c=new THREE.Mesh(new THREE.BoxGeometry(0.03,0.03,0.05),redM); c.position.set(x,0.11,-0.04); phone.add(c); } }
const receiver=new THREE.Group(); S.scene.add(receiver);
{ const h=new THREE.Mesh(new THREE.CylinderGeometry(0.018,0.02,0.16,16),redM); h.rotation.z=Math.PI/2; h.castShadow=true; receiver.add(h);
  for(const x of [-0.09,0.09]){ const e=new THREE.Mesh(new THREE.CylinderGeometry(0.034,0.03,0.035,20),redM); e.position.set(x,-0.012,0); e.castShadow=true; receiver.add(e); } }
const cordM=new THREE.MeshStandardMaterial({color:0x8a1f18,roughness:0.5}); let cord=null;
function setCord(a,b){ const pts=[]; const n=60; for(let i=0;i<=n;i++){ const u=i/n; const p=a.clone().lerp(b,u); p.y-=0.09*Math.sin(Math.PI*u)*Math.min(1,a.distanceTo(b)*2.5);
    const coil=u>0.12&&u<0.88?0.008:0; p.x+=coil*Math.cos(u*170); p.y+=coil*Math.sin(u*170); pts.push(p); }
  const g=new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts),180,0.0042,6,false); if(!cord){ cord=new THREE.Mesh(g,cordM); cord.castShadow=true; S.scene.add(cord); } else { cord.geometry.dispose(); cord.geometry=g; } }
const redHalo=SLD.glowSprite(S.scene,0xff3a2a,0.03), redLight=new THREE.PointLight(0xff5a40,0,1.6,2); S.scene.add(redLight);

// ---------------------------------------------------------------- his bag, Dad's stick, the two sweaters (scene 4)
const bagM=std(0x3c4350,'bag',{r:0.7,rim:0.12,rimCol:0x9fb2d6});
const bag=add(new THREE.BoxGeometry(0.15,0.38,0.3),bagM);
const stickM=std(0x3a2618,'stick',{r:0.5,rim:0.1}); const stick=new THREE.Group(); S.scene.add(stick);
{ const s=add(new THREE.CylinderGeometry(0.012,0.012,0.86,10),stickM,stick); s.position.y=0.43; const c=add(new THREE.TorusGeometry(0.045,0.013,8,20,Math.PI),stickM,stick); c.position.set(0.045,0.86,0); }
function sweater(col,key,x){ const g=new THREE.Group(); const m=std(col,key,{r:0.95,rim:0.18,e:col,ei:0.05}); m.side=THREE.DoubleSide;   // a cardigan hung over the backrest
  const roll=add(new THREE.CylinderGeometry(0.035,0.035,0.44,14),m,g); roll.rotation.set(Math.PI/2,0,0); roll.position.set(-0.19,0.955,0);
  const front=add(new THREE.BoxGeometry(0.014,0.3,0.42),m,g); front.position.set(-0.155,0.8,0); front.rotation.z=-0.04;     // hangs on the seat side
  const back=add(new THREE.BoxGeometry(0.014,0.22,0.42),m,g); back.position.set(-0.225,0.85,0);
  for(const z of [-0.15,0.15]){ const sl=add(new THREE.CylinderGeometry(0.03,0.036,0.34,10),m,g); sl.position.set(-0.14,0.64,z); sl.rotation.z=0.18; }
  for(const y of [0.9,0.82,0.74]){ const bt=add(new THREE.SphereGeometry(0.008,8,6),std(0xe8dcc8,key+'b',{r:0.4}),g); bt.position.set(-0.146,y,0.02); }
  g.position.set(x,0,BACKZ); g.rotation.y=yawOf(FACE_Z); g.visible=false; S.scene.add(g); return g; }
const momSweater=sweater(0xa784b2,'msw',MOM_X), dadSweater=sweater(0x98a0aa,'dsw',DAD_X);

// ---------------------------------------------------------------- his place far away: desk, laptop, mobile, the Salary Loop's plaid bed
const HIS=V(1.75,0,-3.0);
const isl=new THREE.Group(); S.scene.add(isl); isl.position.copy(HIS);
let lapScrM;
{ box(1.0,0.05,0.5,WOOD,0,0.76,-0.4,isl); for(const x of [-0.45,0.45]) for(const z of [-0.6,-0.2]) box(0.05,0.74,0.05,WOOD,x,0.37,z,isl);
  box(0.36,0.018,0.25,std(0x2a2d33,'lap',{r:0.4,rim:0.1}),0,0.794,-0.38,isl);
  lapScrM=new THREE.MeshStandardMaterial({color:0x0d1013,roughness:0.3,emissive:0x9fc8ff,emissiveIntensity:0.9});
  const scr=box(0.36,0.24,0.012,lapScrM,0,0.92,-0.5,isl); scr.rotation.x=-0.18;
  const bed=new THREE.Group(); isl.add(bed); bed.position.set(1.2,0,-0.5);
  box(0.98,0.3,2.0,CHAIRWOOD,0,0.15,0,bed); box(0.92,0.18,1.94,std(0xf0ebe2,'mattress',{r:0.9,rim:0.06}),0,0.39,0,bed);
  box(0.94,0.12,1.2,std(0xffffff,'quilt',{r:0.95,rim:0.05,map:plaidTex()}),0,0.52,0.32,bed); box(0.6,0.12,0.32,std(0xfaf6ee,'pillow',{r:0.95,rim:0.05}),0,0.53,-0.75,bed);
  box(0.42,0.3,0.16,std(0x3a2a1e,'obag',{r:0.7,rim:0.08}),-0.7,0.15,0.2,isl); }
const hisChair=makeChair(); placeChair(hisChair,HIS.clone().add(V(0,0,0.18)),FACE_NZ);
const HIS_ROOT=HIS.clone().add(V(0,0,0.18-0.08-HIPBACK));
const deskLamp=new THREE.PointLight(0xffc890,0,4.0,1.4); deskLamp.position.copy(HIS).add(V(-0.35,1.25,-0.3)); S.scene.add(deskLamp);
const screenLight=new THREE.PointLight(0x9fc8ff,0,2.2,2); screenLight.position.copy(HIS).add(V(0,1.0,-0.25)); S.scene.add(screenLight);
const mob=new THREE.Group(); S.scene.add(mob);
const mobScrM=new THREE.MeshStandardMaterial({color:0x0d0e12,roughness:0.3,emissive:0xff6a5a,emissiveIntensity:0});
{ const b=new THREE.Mesh(new THREE.BoxGeometry(0.075,0.009,0.15),std(0x15171b,'mob',{r:0.3,rim:0.2})); b.castShadow=true; mob.add(b);
  const s=new THREE.Mesh(new THREE.BoxGeometry(0.066,0.002,0.136),mobScrM); s.position.y=0.0055; mob.add(s); }
const MOB_DESK=HIS.clone().add(V(0.34,0.79,-0.22));
const mobHalo=SLD.glowSprite(S.scene,0xffd0c0,0);

// ---------------------------------------------------------------- the family: cream wooden figures, hair caps that grey, Mom's saree
const mom=R.makeFig(0xf0e4d0,'mom',{rim:0.16,lift:0.05}), dad=R.makeFig(0xe8dfcf,'dad',{rim:0.16,lift:0.05}), son=R.makeFig(PAL.CREAM,'son',{rim:0.16,lift:0.05});
const MSC=[0.93,0.95];
function hairCap(key){ const m=std(0x2b1f18,key,{r:0.85,rim:0.1}); return add(new THREE.SphereGeometry(1,26,16,0,Math.PI*2,0,Math.PI*0.5),m); }
const momHair=hairCap('mh'), dadHair=hairCap('dh'), sonHair=hairCap('sh');
const bun=add(new THREE.SphereGeometry(1,20,14),momHair.material);
const sareeM=std(0x7e5a8c,'saree',{r:0.8,rim:0.14,rimCol:0xffd8f0,e:0x7e5a8c,ei:0.04}); sareeM.side=THREE.DoubleSide;   // purple saree (brief)
const pallu=add(new THREE.CylinderGeometry(1,1,1,12),sareeM);
const HAIR_DARK=new THREE.Color(0x2b1f18), HAIR_GREY=new THREE.Color(0x8e8a84), HAIR_WHITE=new THREE.Color(0xdcd8cf);
function hairCol(m,g){ m.material.color.copy(g<0.5?HAIR_DARK.clone().lerp(HAIR_GREY,g*2):HAIR_GREY.clone().lerp(HAIR_WHITE,(g-0.5)*2)); }
function placeHair(h,J,hs,back=0.55){ const hd=J.head.clone().sub(J.neck).normalize(); const pole=hd.clone().multiplyScalar(0.85).addScaledVector(J.fwd,-back).normalize();
  h.position.copy(J.head); h.scale.setScalar(0.13*hs*1.05); h.quaternion.setFromUnitVectors(UPV,pole); }
function limbMesh(m,a,b,r,rz=r){ const d=b.clone().sub(a); const len=Math.max(d.length(),1e-4); m.position.copy(a).add(b).multiplyScalar(0.5); m.scale.set(r,len,rz); m.quaternion.setFromUnitVectors(UPV,d.multiplyScalar(1/len)); }

// ---------------------------------------------------------------- ages and aging: three beats (8, 18, 25)
const age=t=>t<SC[1]?8:t<SC[2]?18:25;
const grey=t=>t<SC[1]?0:t<SC[2]?0.22:lerp(0.42,0.6,sstep(SC[2],SC[3],t));      // Mom 40% grey at 25
const stoop=t=>t<SC[2]?0:lerp(0.7,1,sstep(SC[2],SC[3],t));
const grow=t=>sm5(sstep(TL.grow[0],TL.grow[1],t));

// ---------------------------------------------------------------- poses
function seatedAt(P,x,face,s=1){ // root for a figure of scale s sitting on a chair at (x, z of chair)
  return x; }
function parents(t){
  const st=stoop(t), A=t<SC[1]; const call=TL.call25, rc=TL.call18;
  // --- Mom: serves him at 8 (ladle from the bowl to his plate), watches him leave at 18, calls at 18 and at 25
  let Q={...CHAIRP,p:0.1+0.22*st,tilt:0.08+0.14*st}; Q.p+=0.012*Math.sin(2*Math.PI*0.25*t);
  R.setScale(MSC[0],MSC[1]); const mJ0=R.skel(Q,backRoot(MOM_X),yawOf(FACE_Z));
  const ear=mJ0.head.clone().add(V(-0.12,-0.02,0.02));
  const restL=V(MOM_X-0.08,TOP+0.03,-0.18), restR=V(MOM_X+0.1,TOP+0.03,-0.2);
  let tL=restL.clone(), tR=restR.clone(), rcv=null;
  if(A){ const sv=sstep(TL.serve[0],TL.serve[0]+0.5,t)*(1-sstep(TL.serve[1]-0.4,TL.serve[1],t)); const pour=sstep(TL.serve[0]+0.5,TL.serve[0]+1.1,t);
    const over=V(0.0,TOP+0.2,-0.08).lerp(PL.son.clone().add(V(0.05,0.14,-0.02)),pour); tL=tL.lerp(over,sv); Q.p+=0.18*sv; Q.hy=-0.25*sv; }
  // she lifts the red phone (18: while he walks away; 25: he doesn't pick up, she holds on, then lowers it)
  let lift=0;
  for(const c of [rc,call]){ lift=Math.max(lift,sstep(c[0],c[0]+0.35,t)*(1-sstep(c[1]-0.5,c[1],t))); }
  if(lift>0){ tL=tL.lerp(ear.clone().add(V(0,-0.06,0.03)),lift); Q.tilt-=0.1*lift; Q.hy=0.15*lift; rcv=V(PH0.x,PH0.y+0.145,PH0.z).lerp(ear,sm5(lift)); }
  // watching him go (18): heads turn to follow
  const watch=win(t,TL.leave[0],SC[2]-0.05,0.4);
  Q.hy=(Q.hy||0)+0.55*watch; Q.ty=0.15*watch;
  const sag=t>call[0]?sstep(call[1]-0.6,call[1]+0.4,t):0; Q.p+=0.08*sag; Q.tilt+=0.15*sag;
  Object.assign(Q,{tL,tR,wL:1,wR:1,pL:V(-0.3,-0.7,0.7),pR:V(-0.3,-0.7,-0.7)});
  R.setScale(MSC[0],MSC[1]); const momJ=R.skel(Q,backRoot(MOM_X),yawOf(FACE_Z));
  // --- Dad: eats at 8 (laughs once), watches him go, bent with a stick at 25
  let D={...CHAIRP,p:0.1+0.32*st,tilt:0.12+0.16*st}; D.p+=0.012*Math.sin(2*Math.PI*0.22*t+1);
  const eat=A?Math.max(bump(t,0.6,1.1),bump(t,2.3,1.1)):0; const laugh=A?bump(t,1.6,1.2):0;
  D.p+=-0.06*laugh+0.02*laugh*Math.sin(t*26); D.tilt-=0.2*laugh;
  const dR=V(DAD_X+0.12,TOP+0.03,-0.2).lerp(V(DAD_X+0.05,1.12,-0.3),eat);
  const stickTop=V(DAD_X-0.33,0.88,-0.3);
  const dL=st>0?stickTop.clone().add(V(-0.03,0.02,0)):V(DAD_X-0.1,TOP+0.03,-0.2);
  D.hy=0.5*watch+0.25*lift*(t>SC[2]?1:0); D.ty=0.12*watch;
  Object.assign(D,{tL:dL,tR:dR,wL:1,wR:1,pL:V(-0.3,-0.7,0.7),pR:V(-0.3,-0.7,-0.7)});
  R.setScale(1,1); const dadJ=R.skel(D,backRoot(DAD_X),yawOf(FACE_Z));
  return {momJ,dadJ,rcv,ringing:0};
}
// the son: seated on our side (back to the camera) at 8, grows up in the chair, takes his bag, pushes the chair back, walks to his desk
const PATH=[V(SON_X,0,FRONTZ+0.35),V(0.75,0,FRONTZ+0.25),V(1.3,0,0.2),V(1.6,0,-1.5),V(1.75,0,-2.6)];
const PLEN=[0]; for(let i=1;i<PATH.length;i++) PLEN.push(PLEN[i-1]+PATH[i].distanceTo(PATH[i-1]));
const pathAt=d=>{ d=clamp(d,0,PLEN[PLEN.length-1]); let i=1; while(i<PLEN.length-1&&d>PLEN[i]) i++; const u=(d-PLEN[i-1])/(PLEN[i]-PLEN[i-1]);
  return {p:PATH[i-1].clone().lerp(PATH[i],u),dir:PATH[i].clone().sub(PATH[i-1]).normalize()}; };
function sonAt(t){
  const g=grow(t), s=lerp(0.66,1.0,g), hs=lerp(0.86,1.0,g);
  if(t>=SC[2]){ // at his desk, back to us, typing; the mobile buzzes beside him and he does not look
    let P={...CHAIRP,p:0.24,tilt:0.2}; const ty=Math.sin(t*14); const kb=HIS.clone().add(V(0,0.81,-0.33));
    Object.assign(P,{tL:kb.clone().add(V(0.09,0.01*Math.max(0,ty),0)),tR:kb.clone().add(V(-0.09,0.01*Math.max(0,-ty),0)),wL:1,wR:1,pL:V(-0.3,-0.7,0.6),pR:V(-0.3,-0.7,-0.6)});
    R.setScale(1,1); return {J:R.skel(P,HIS_ROOT,yawOf(FACE_NZ)),s:1,hs:1,bag:0,chairZ:FRONTZ+0.5,mob:{pos:MOB_DESK.clone(),inHand:0}}; }
  const up=sstep(TL.stand[0],TL.stand[1],t);
  const chairZ=FRONTZ+0.5*sstep(TL.stand[0]-0.1,TL.stand[0]+0.45,t);
  // seated: hip on the seat, whatever his size
  const seatHip=V(SON_X,0,FRONTZ-0.08), root0=seatHip.clone().addScaledVector(FACE_NZ,HIPBACK*s);
  let P={...CHAIRP,p:0.12,tilt:0.06};
  R.setScale(s,hs); const hip0=R.skel(P,root0,yawOf(FACE_NZ)).hip.y; P.dy=0.475-hip0;
  // eating at 8: spoon from plate to mouth
  const eat=t<SC[1]?Math.max(bump(t,0.2,1.0),bump(t,1.5,1.0),bump(t,2.8,1.0)):0;
  const J0=R.skel(P,root0,yawOf(FACE_NZ)); const mouth=J0.head.clone().addScaledVector(J0.fwd,0.12*hs).add(V(0,-0.08*hs,0));
  const plate=PL.son.clone().add(V(0.04,0.04,0));
  P.tR=plate.clone().lerp(mouth,eat); P.wR=1-up; P.pR=V(-0.3,-0.7,-0.7); P.tL=PL.son.clone().add(V(-0.16,0.03,0.05)); P.wL=1-up; P.pL=V(-0.3,-0.7,0.7);
  let root=root0.clone(), yaw=yawOf(FACE_NZ), J;
  if(t<TL.stand[0]){ R.setScale(s,hs); J=R.skel(P,root,yaw); }
  else { // stand (chair shoved back), shoulder the bag, turn and walk the path; the call at 18: phone to his ear, a happy bounce, keeps walking
    const standRoot=V(SON_X,0,FRONTZ+0.18);
    let Q=R.blend({...P,dy:P.dy*(1-up)},{...R.P0,p:0.06},up); root=root0.clone().lerp(standRoot,up);
    const tw=Math.max(0,t-TL.leave[0]);
    if(tw>0){ const d=1.35*(tw<0.5?tw*tw/1.0:tw-0.25); const pp=pathAt(d); root=standRoot.clone().lerp(pp.p,sstep(0,0.4,tw));
      const turn=sstep(0,0.45,tw); let a0=yawOf(FACE_NZ), a1=yawOf(pp.dir), da=Math.atan2(Math.sin(a1-a0),Math.cos(a1-a0)); yaw=a0+da*turn;
      Q=R.gait({...R.P0,p:0.1,tilt:0.02},d/1.3*Math.PI*2,sstep(0,0.35,tw)); }
    R.setScale(1,1); const Jq=R.skel(Q,root,yaw);
    const callH=sstep(TL.call18[0]+0.25,TL.call18[0]+0.6,t)*(1-sstep(TL.call18[1]-0.4,TL.call18[1],t));
    if(callH>0){ const earS=Jq.head.clone().addScaledVector(Jq.fwd.clone().cross(UPV).normalize(),-0.12).add(V(0,-0.03,0)); Q.tR=earS; Q.wR=callH; Q.pR=V(-0.5,-0.4,-0.7); Q.tilt=-0.12*callH; Q.p+=0.03*Math.sin(t*9)*callH; }
    R.setScale(1,1); J=R.skel(Q,root,yaw);
    return {J,s:1,hs:1,bag:sstep(TL.stand[1]-0.1,TL.stand[1]+0.25,t),chairZ,mob:{pos:J.hR.clone(),inHand:callH}}; }
  return {J,s,hs,bag:0,chairZ,mob:null};
}

// ---------------------------------------------------------------- camera: keys per shot (Catmull-Rom), hard cuts where two keys share a time
const CAMS=TL.cams.map(([t,p,l])=>({t,p:V(...p),l:V(...l)}));
const SHOTS=[]; { let s=0; for(let i=1;i<CAMS.length;i++) if(CAMS[i].t===CAMS[i-1].t){ SHOTS.push(CAMS.slice(s,i)); s=i; } SHOTS.push(CAMS.slice(s)); }
const cr=(a,b,c,d,u)=>{ const u2=u*u,u3=u2*u; return b.clone().multiplyScalar(2).add(c.clone().sub(a).multiplyScalar(u)).add(a.clone().multiplyScalar(2).sub(b.clone().multiplyScalar(5)).add(c.clone().multiplyScalar(4)).sub(d).multiplyScalar(u2)).add(b.clone().multiplyScalar(3).sub(a).sub(c.clone().multiplyScalar(3)).add(d).multiplyScalar(u3)).multiplyScalar(0.5); };
function camAt(t){ const idx=SHOTS.findIndex((s,i)=>i===SHOTS.length-1||t<SHOTS[i+1][0].t); const k=SHOTS[idx];
  const t1=idx<SHOTS.length-1?SHOTS[idx+1][0].t:DUR;
  if(k.length===1) return {pos:k[0].p.clone(),look:k[0].l.clone(),t0:k[0].t,t1};
  let i=0; while(i<k.length-2&&t>=k[i+1].t) i++;
  const u=sm5(clamp((t-k[i].t)/(k[i+1].t-k[i].t)));
  const g=j=>k[Math.max(0,Math.min(k.length-1,j))];
  return {pos:cr(g(i-1).p,g(i).p,g(i+1).p,g(i+2).p,u),look:cr(g(i-1).l,g(i).l,g(i+1).l,g(i+2).l,u),t0:k[0].t,t1}; }

// ---------------------------------------------------------------- one frame
function poseMom(J){ R.setScale(MSC[0],MSC[1]); R.poseFig(mom,J); placeHair(momHair,J,MSC[1]);
  const hd=J.head.clone().sub(J.neck).normalize(); bun.position.copy(J.head).addScaledVector(J.fwd,-0.115*MSC[1]).addScaledVector(hd,0.03); bun.scale.setScalar(0.058);
  limbMesh(pallu,J.shL.clone().addScaledVector(J.fwd,0.035).add(V(0,0.03,0)),J.hipR.clone().addScaledVector(J.fwd,0.06),0.05,0.02); }
function setVis(F,v){ F.all.forEach(x=>x.visible=v); }
function setT(t){
  const s4=t>=SC[4], black=t>=SC[3]&&t<SC[4];
  // --- people (scene 4: nobody, only their sweaters on their chairs)
  const pr=parents(t); const sn=sonAt(t);
  for(const [F,on] of [[mom,!s4],[dad,!s4],[son,!s4]]) setVis(F,on);
  for(const h of [momHair,dadHair,bun,pallu]) h.visible=!s4; sonHair.visible=!s4;
  if(!s4){ poseMom(pr.momJ); R.setScale(1,1); R.poseFig(dad,pr.dadJ); placeHair(dadHair,pr.dadJ,1,0.5);
    R.setScale(sn.s,sn.hs); R.poseFig(son,sn.J); placeHair(sonHair,sn.J,sn.hs,0.45); }
  hairCol(momHair,grey(t)); hairCol(dadHair,Math.min(1,grey(t)*1.25)); sonHair.material.color.copy(HAIR_DARK);
  momSweater.visible=dadSweater.visible=s4;
  // --- his chair: in place at 8, shoved back when he stands, left there (empty) after
  placeChair(sonChair,V(SON_X,0,sn.chairZ),FACE_NZ); if(s4) sonChair.position.z=FRONTZ+0.12;
  bag.visible=sn.bag>0.01&&!s4; if(bag.visible){ const J=sn.J; const up=J.neck.clone().sub(J.hip).normalize(); bag.position.copy(J.hip.clone().lerp(J.neck,0.55).addScaledVector(J.fwd,-0.16));
    bag.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(J.fwd.clone(),up,J.fwd.clone().cross(up).normalize())); }
  stick.visible=t>=SC[2]&&!s4; stick.position.set(DAD_X-0.42,0,-0.24); stick.rotation.set(0.05,Math.PI,0.09);
  if(s4){ stick.visible=true; stick.position.set(DAD_X-0.3,0,BACKZ+0.25); stick.rotation.set(0.0,Math.PI,0.2); }
  // --- food: warm at 8, his plate empty and dusty from 18 on; theirs full but no longer glowing at 25
  const warm=t<SC[2]?1:0.15; for(const k of ['mom','dad']){ foodM[k].emissiveIntensity=0.35*warm; }
  food.son.visible=t<TL.leave[0]; foodM.son.emissiveIntensity=0.35;
  sonPlateM.color.setHex(t>=SC[2]?0x9a958c:0xe9e4da); sonPlateM.roughness=t>=SC[2]?0.95:0.35;
  steam.forEach((s,i)=>{ const k=['mom','dad','son'][i]; s.position.copy(PL[k]).add(V(0,0.12+0.03*Math.sin(t*2+i),0)); s.scale.setScalar(0.22); s.material.opacity=t<SC[1]?0.18:0; });
  ladle.visible=t<SC[1]; if(ladle.visible){ ladle.position.copy(pr.momJ.hL).add(V(0,-0.12,0)); }
  // --- the red phone: by Mom at the table, by his empty plate in scene 4
  const ph=s4?PH_END:PH0; phone.position.copy(ph); phone.rotation.y=s4?-0.25:0.5;
  const ringI=s4?win(t,TL.ring,TL.ring+0.75,0.03):0; const jig=ringI*0.006*Math.sin(t*2*Math.PI*21);
  const cradle=ph.clone().add(V(0,0.145,-0.02));
  phone.position.y+=jig*0.4;
  if(pr.rcv&&!s4){ receiver.position.copy(pr.rcv); receiver.rotation.set(0,0,Math.PI/2*0.9); } else { receiver.position.copy(cradle).add(V(0,jig,0)); receiver.rotation.set(0,phone.rotation.y,0); }
  setCord(ph.clone().add(V(-0.1,0.03,0)),receiver.position.clone().add(V(pr.rcv&&!s4?0:-0.09,-0.02,0)));
  redM.emissiveIntensity=0.05+(s4?0.12:0)+0.35*ringI; redHalo.position.copy(ph).add(V(0,0.1,0)); redHalo.scale.setScalar(0.4+0.3*ringI); redHalo.material.opacity=(s4?0.08:0.03)+0.18*ringI;
  redLight.position.copy(ph).add(V(0,0.25,0.1)); redLight.intensity=(s4?0.1:0)+0.5*ringI;
  // --- his place: the desk lamp and laptop are on from 18; the mobile (in his hand at 18, on the desk buzzing red at 25)
  const on=t>=SC[1]?1:0; deskLamp.intensity=2.6*on*(s4?0:1); screenLight.intensity=1.2*on*(s4?0:1); lapScrM.emissiveIntensity=0.9*on;
  const missed=t>=SC[2]&&!s4?win(t,TL.call25[0]+0.2,TL.call25[1],0.05):0;
  mob.visible=(!!sn.mob&&(sn.mob.inHand>0.01||t>=SC[2]))&&!s4;
  if(mob.visible){ const buzz=missed*0.004*Math.sin(t*2*Math.PI*30); mob.position.copy(sn.mob.pos).add(V(buzz,0,0)); mob.rotation.set(t>=SC[2]?0:1.2,0,0);
    mobScrM.emissiveIntensity=2.4*missed; mobHalo.position.copy(sn.mob.pos).add(V(0,0.05,0)); mobHalo.scale.setScalar(0.35); mobHalo.material.opacity=0.45*missed; } else mobHalo.material.opacity=0;
  // --- the lamp: warm gold; at 25 it cools and dims (12-14 s); scene 4 narrower and low, warm again on the ring
  const dim=sstep(TL.dim[0],TL.dim[1],t);
  const col=GOLD.clone().lerp(COLD,0.55*dim*(s4?0:1)); S.spot.color.copy(col); S.beamU.uCol.value.copy(col);
  if(s4) aim(V(0.04,0,-0.1),0.36); else aim(AIM,CONE);
  // --- camera
  const c=camAt(t); S.cam.position.copy(c.pos); S.cam.lookAt(c.look);
  S.tick(t,0.08*ringI);
  const k=s4?0.75:(1-0.42*dim); S.spot.intensity*=k; S.beamU.uI.value*=k;
  if(black){ S.spot.intensity=0; S.beamU.uI.value=0; S.moteU.uOp.value=0; } else S.moteU.uOp.value=1;
  S.scene.visible=!black;
}

// ---------------------------------------------------------------- overlay / sound data
window.metaAt=t=>({age:age(t),phone:t>=SC[2]&&t<SC[3]?'missed':(t>=TL.call18[0]&&t<TL.call18[1]?'calling':null)});
window.events={...TL};
window.renderAt=(t,K=3)=>{ const c=camAt(t); return S.renderAt(setT,t,K,{t0:c.t0,t1:c.t1}); };
window.ready=true;
