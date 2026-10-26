// Your Parents Are Aging While You Are Busy (Slow Light Dark, the trilogy closer after 30 Friends to 1 and The Salary Loop).
// The parents' table under the gold lamp: Mom (bun, saree) hands her 8-year-old his tiffin, he hugs her and grows up inside the
// hug, then walks off into the dark with a backpack. Hard cut: far away a second, cooler lamp clicks on over his desk and bed.
// Every call is a gold light crossing the dark from the red phone on their table to his phone: at 18 he picks up, at 23 he
// turns the phone face down, at 25 he doesn't look, at 28 he sends one a week. The parents grey and stoop (Dad gets a stick)
// but stay alive. Push in on the two of them waiting by the phone, his chair pushed in, his plate covered. The lamp narrows
// onto the red phone; one ring; Mom's hand goes to it.
//
// Units are metres; floor y = 0; the table's long axis is x, the camera is on +z. renderAt(t) is pure (parallel workers).
import * as THREE from 'three';
import * as SLD from './sld.js';
const {V,clamp,sstep,lerp,sm5,rng,yawOf,PAL,UPV,keys}=SLD;
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960;
const TL=await (await fetch('./'+(q.get('tl')||'timeline.json'))).json(); const DUR=TL.duration;
const bump=(t,a,d)=>{ const x=(t-a)/d; return x<=0||x>=1?0:Math.sin(Math.PI*x)**2; };
const win=(t,a,b,f=0.2)=>sstep(a,a+f,t)*(1-sstep(b-f,b,t));

// ---------------------------------------------------------------- stage: the gold lamp over the parents' table
const TOP=0.74;
const LAMP=V(0.2,4.7,0.4), AIM_A=V(0.75,0,0.25), AIM_B=V(0.0,0,-0.15), CONE_A=0.34, CONE_B=0.4, CONE_END=0.13;
const S=SLD.createStage({W,H,lamp:LAMP,lampTarget:AIM_A,cone:CONE_B,spot:64,beam:0.12,motes:2400});
const R=SLD.createRig(S.scene);
S.spot.shadow.camera.far=9;
const beamMesh=S.NOREFL[0];
{ const h=6.5, r=Math.tan(CONE_B)*h*1.05; const g=new THREE.CylinderGeometry(0.02,r,h,96,24,true); g.translate(0,-h/2,0); beamMesh.geometry.dispose(); beamMesh.geometry=g; }
function ditherBeam(m){ m.material.fragmentShader=m.material.fragmentShader.replace('float acc=0.0;','float acc=0.0; float jit=fract(sin(dot(gl_FragCoord.xy,vec2(12.9898,78.233)))*43758.5453)-0.5;')
  .replace('float s=tEnd*(float(i)+0.5)/16.0;','float s=tEnd*(float(i)+0.5+jit)/16.0;'); m.material.needsUpdate=true; }
ditherBeam(beamMesh);
function aim(target,cone){ const d=target.clone().sub(LAMP).normalize();
  S.spot.target.position.copy(target); S.spot.target.updateMatrixWorld(); S.spot.angle=cone+0.08;
  S.beamU.uAxis.value.copy(d); S.beamU.uTan.value=Math.tan(cone); S.moteU.uTan.value=Math.tan(cone);
  beamMesh.quaternion.setFromUnitVectors(V(0,-1,0),d); }

// his lamp (the city): cooler, smaller, far back and to the right; same ray-marched beam, its own uniforms
const HIS=V(2.9,0,-6.6);
const LAMP2=HIS.clone().add(V(0.15,3.9,0.35)), AIM2=HIS.clone().add(V(-0.25,0,-0.15)), CONE2=0.36;
const spot2=new THREE.SpotLight(0xcfdcff,0,0,CONE2+0.08,0.85,1.2); spot2.position.copy(LAMP2); spot2.target.position.copy(AIM2);
spot2.castShadow=true; spot2.shadow.mapSize.set(1024,1024); spot2.shadow.bias=-0.0003; spot2.shadow.normalBias=0.012; spot2.shadow.camera.near=1.5; spot2.shadow.camera.far=6;
S.scene.add(spot2,spot2.target);
const beam2U={uT:S.beamU.uT,uI:{value:0},uApex:{value:LAMP2},uAxis:{value:AIM2.clone().sub(LAMP2).normalize()},uTan:{value:Math.tan(CONE2)},uCol:{value:new THREE.Color(0xbfd2ff)}};
{ const h=LAMP2.distanceTo(AIM2)+0.02, r=Math.tan(CONE2)*h*1.05; const g=new THREE.CylinderGeometry(0.02,r,h,96,24,true); g.translate(0,-h/2,0);
  const m=new THREE.Mesh(g,new THREE.ShaderMaterial({uniforms:beam2U,transparent:true,depthWrite:false,side:THREE.BackSide,blending:THREE.AdditiveBlending,fog:false,
    vertexShader:beamMesh.material.vertexShader,fragmentShader:beamMesh.material.fragmentShader.replace(/\*0\.1200\b/,'*0.1000')}));
  m.position.copy(LAMP2); m.quaternion.setFromUnitVectors(V(0,-1,0),beam2U.uAxis.value); m.frustumCulled=false; m.renderOrder=5; S.scene.add(m); S.NOREFL.push(m); }
const screenLight=new THREE.PointLight(0x9fc8ff,0,2.2,2); S.scene.add(screenLight);

// ---------------------------------------------------------------- materials (the Friends table and chairs)
function woodTex(seed,base){ const c=document.createElement('canvas'); c.width=1024; c.height=256; const g=c.getContext('2d'); const Rn=rng(seed);
  g.fillStyle=base; g.fillRect(0,0,1024,256);
  for(let k=0;k<260;k++){ const y=Rn()*256, a=0.04+Rn()*0.1; g.strokeStyle=Rn()<0.6?`rgba(0,0,0,${a})`:`rgba(255,220,180,${a*0.5})`; g.lineWidth=0.6+Rn()*2.2;
    g.beginPath(); g.moveTo(0,y); for(let x=0;x<=1024;x+=32) g.lineTo(x,y+Math.sin(x*0.004+k)*3+Math.sin(x*0.021+k*1.7)*1.2); g.stroke(); }
  const t=new THREE.CanvasTexture(c); t.wrapS=t.wrapT=THREE.RepeatWrapping; t.colorSpace=THREE.SRGBColorSpace; return t; }
// the plaid quilt from The Salary Loop's bed
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

// ---------------------------------------------------------------- the parents' table: 1.9 x 0.9
const TX0=-0.95, TX1=0.95, TZ=0.45;
{ const top=box(TX1-TX0,0.05,TZ*2,WOOD,0,TOP-0.025,0); top.material.map.repeat.set(2,1);
  box(TX1-TX0-0.16,0.09,TZ*2-0.12,WOOD,0,TOP-0.095,0);
  for(const x of [TX0+0.07,TX1-0.07]) for(const z of [-TZ+0.07,TZ-0.07]) box(0.07,TOP-0.05,0.07,WOOD,x,(TOP-0.05)/2,z); }
const chairGeo={seat:new THREE.BoxGeometry(0.42,0.04,0.42),leg:new THREE.BoxGeometry(0.035,0.44,0.035),post:new THREE.BoxGeometry(0.035,0.5,0.035),rail:new THREE.BoxGeometry(0.03,0.12,0.4)};
function makeChair(mat=CHAIRWOOD){ const g=new THREE.Group(); const a=(geo,x,y,z)=>{ const m=new THREE.Mesh(geo,mat); m.position.set(x,y,z); m.castShadow=m.receiveShadow=true; g.add(m); };
  a(chairGeo.seat,0,0.44,0); for(const x of [-0.18,0.18]) for(const z of [-0.18,0.18]) a(chairGeo.leg,x,0.22,z);
  for(const z of [-0.18,0.18]) a(chairGeo.post,-0.19,0.71,z); a(chairGeo.rail,-0.19,0.88,0); a(chairGeo.rail,-0.19,0.68,0); S.scene.add(g); return g; }
function placeChair(c,p,facing){ c.position.copy(p); c.rotation.y=yawOf(facing); }
const HIPBACK=0.276, CHAIRP={...R.P0,p:0.07,tilt:0.0,aL:1.5,aR:1.47,kL:1.52,kR:1.47,sL:0.5,sR:0.5,eL:0.9,eR:0.9};
const MOM_X=0.3, DAD_X=-0.35, BACKZ=-0.8, FACE_Z=V(0,0,1);
const momChair=makeChair(), dadChair=makeChair(), sonChair=makeChair(), spareChair=makeChair();
placeChair(spareChair,V(-1.22,0,0.02),V(1,0,0));
const seatRoot=(x)=>V(x,0,BACKZ+0.08+HIPBACK);
// plates (his at the right end), steel lids for the cold dinner at the end
const PL={mom:V(MOM_X,TOP,-0.22), dad:V(DAD_X,TOP,-0.22), son:V(0.02,TOP,0.24)};
const lids={}; for(const k in PL){ const p=add(new THREE.CylinderGeometry(0.13,0.11,0.018,32),PLATE); p.position.copy(PL[k]).add(V(0,0.009,0));
  const l=add(new THREE.SphereGeometry(0.105,28,12,0,Math.PI*2,0,Math.PI/2),STEEL); l.scale.set(1,0.62,1); l.position.copy(PL[k]).add(V(0,0.02,0)); lids[k]=l; }
// two steel tumblers
for(const [x,z] of [[MOM_X+0.2,-0.2],[DAD_X+0.2,-0.18]]){ const g=add(new THREE.CylinderGeometry(0.03,0.025,0.1,20),STEEL); g.position.set(x,TOP+0.05,z); }

// ---------------------------------------------------------------- the red phone (the one red object): base, dial, receiver, coiled cord
const PH_BASE=V(-0.03,TOP,-0.1);
const redM=new THREE.MeshStandardMaterial({color:PAL.RED,roughness:0.42,metalness:0,emissive:PAL.RED,emissiveIntensity:0.05}); SLD.rimify(redM,0xff8a70,0.14,'phone');
const phone=new THREE.Group(); S.scene.add(phone); phone.position.copy(PH_BASE); phone.rotation.y=0.35;
{ const b=new THREE.Mesh(new THREE.BoxGeometry(0.21,0.07,0.17),redM); b.position.y=0.035; b.castShadow=true; phone.add(b);
  const b2=new THREE.Mesh(new THREE.BoxGeometry(0.17,0.04,0.13),redM); b2.position.set(0,0.085,0.005); b2.rotation.x=-0.25; b2.castShadow=true; phone.add(b2);
  const dial=new THREE.Mesh(new THREE.CylinderGeometry(0.042,0.042,0.008,28),std(0xe8dcc8,'dial',{r:0.4,rim:0.1})); dial.position.set(0,0.108,0.03); dial.rotation.x=-0.25; phone.add(dial);
  for(const x of [-0.07,0.07]){ const c=new THREE.Mesh(new THREE.BoxGeometry(0.03,0.03,0.05),redM); c.position.set(x,0.11,-0.04); phone.add(c); } }
const receiver=new THREE.Group(); S.scene.add(receiver);
{ const h=new THREE.Mesh(new THREE.CylinderGeometry(0.018,0.02,0.16,16),redM); h.rotation.z=Math.PI/2; h.castShadow=true; receiver.add(h);
  for(const x of [-0.09,0.09]){ const e=new THREE.Mesh(new THREE.CylinderGeometry(0.034,0.03,0.035,20),redM); e.position.set(x,-0.012,0); e.castShadow=true; receiver.add(e); } }
const CRADLE=PH_BASE.clone().add(V(0,0.145,-0.02));
const cordM=new THREE.MeshStandardMaterial({color:0x8a1f18,roughness:0.5}); let cord=null;
function setCord(a,b){ const pts=[]; const n=60; for(let i=0;i<=n;i++){ const u=i/n; const p=a.clone().lerp(b,u); p.y-=0.09*Math.sin(Math.PI*u)*Math.min(1,a.distanceTo(b)*2.5);
    const coil=u>0.12&&u<0.88?0.008:0; p.x+=coil*Math.cos(u*170); p.y+=coil*Math.sin(u*170); pts.push(p); }
  const g=new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts),180,0.0042,6,false); if(!cord){ cord=new THREE.Mesh(g,cordM); cord.castShadow=true; S.scene.add(cord); } else { cord.geometry.dispose(); cord.geometry=g; } }
const redHalo=SLD.glowSprite(S.scene,0xff3a2a,0.03), redLight=new THREE.PointLight(0xff5a40,0,1.6,2); S.scene.add(redLight);

// ---------------------------------------------------------------- the steel tiffin, Dad's newspaper and stick, the backpack
const tiffin=new THREE.Group(); S.scene.add(tiffin); const tifM=STEEL.clone(); tifM.transparent=true; SLD.rimify(tifM,0xfff1d8,0.32,'tiffin');
{ for(let i=0;i<3;i++){ const c=new THREE.Mesh(new THREE.CylinderGeometry(0.062,0.058,0.055,24),tifM); c.position.y=-0.04-i*0.06; c.castShadow=true; tiffin.add(c); }
  const lid=new THREE.Mesh(new THREE.SphereGeometry(0.062,24,8,0,Math.PI*2,0,Math.PI/2),tifM); lid.scale.y=0.35; lid.position.y=-0.012; tiffin.add(lid);
  const hdl=new THREE.Mesh(new THREE.TorusGeometry(0.045,0.006,8,24,Math.PI),tifM); hdl.position.y=0.0; tiffin.add(hdl);
  for(const x of [-0.066,0.066]){ const r=new THREE.Mesh(new THREE.BoxGeometry(0.008,0.2,0.012),tifM); r.position.set(x,-0.09,0); tiffin.add(r); } }
const paperM=std(0xa59e90,'paper',{r:0.95,rim:0.03}); paperM.side=THREE.DoubleSide;
const paper=add(new THREE.PlaneGeometry(0.4,0.28),paperM);
const stickM=std(0x3a2618,'stick',{r:0.5,rim:0.1}); const stick=new THREE.Group(); S.scene.add(stick);
{ const s=new THREE.Mesh(new THREE.CylinderGeometry(0.012,0.012,0.86,10),stickM); s.position.y=0.43; s.castShadow=true; stick.add(s);
  const c=new THREE.Mesh(new THREE.TorusGeometry(0.045,0.013,8,20,Math.PI),stickM); c.position.set(0.045,0.86,0); c.castShadow=true; stick.add(c); }
const bagM=std(0x3c4350,'bag',{r:0.7,rim:0.12,rimCol:0x9fb2d6}); bagM.transparent=true;
const bag=add(new THREE.BoxGeometry(0.15,0.38,0.3),bagM);

// ---------------------------------------------------------------- his island: desk, laptop, phone, chair, the Salary Loop's bed and bag
const isl=new THREE.Group(); S.scene.add(isl); isl.position.copy(HIS);
{ box(1.1,0.05,0.55,WOOD,0,0.76,-0.42,isl); for(const x of [-0.5,0.5]) for(const z of [-0.65,-0.2]) box(0.05,0.74,0.05,WOOD,x,0.37,z,isl);
  box(0.36,0.018,0.25,std(0x2a2d33,'lap',{r:0.4,rim:0.1}),0,0.794,-0.38,isl);
  const scr=box(0.36,0.24,0.012,new THREE.MeshStandardMaterial({color:0x0d1013,roughness:0.3,emissive:0x9fc8ff,emissiveIntensity:0.9}),0,0.92,-0.5,isl); scr.rotation.x=-0.18;
  const bed=new THREE.Group(); isl.add(bed); bed.position.set(-1.45,0,-0.35);
  box(0.98,0.3,2.0,CHAIRWOOD,0,0.15,0,bed); box(0.92,0.18,1.94,std(0xf0ebe2,'mattress',{r:0.9,rim:0.06}),0,0.39,0,bed);
  box(0.94,0.12,1.2,std(0xffffff,'quilt',{r:0.95,rim:0.05,map:plaidTex()}),0,0.52,0.32,bed); box(0.6,0.12,0.32,std(0xfaf6ee,'pillow',{r:0.95,rim:0.05}),0,0.53,-0.75,bed);
  box(0.06,0.7,0.98,CHAIRWOOD,0,0.5,-1.0,bed).rotation.y=Math.PI/2;
  box(0.42,0.3,0.16,std(0x3a2a1e,'obag',{r:0.7,rim:0.08}),0.62,0.15,0.4,isl); }
const hisChair=makeChair(); placeChair(hisChair,HIS.clone().add(V(0,0,0.18)),V(0,0,-1));
const HIS_ROOT=HIS.clone().add(V(0,0,0.18-0.08-HIPBACK));
const mob=new THREE.Group(); S.scene.add(mob);
const mobScrM=new THREE.MeshStandardMaterial({color:0x0d0e12,roughness:0.3,emissive:0xd8e6ff,emissiveIntensity:0});
{ const b=new THREE.Mesh(new THREE.BoxGeometry(0.075,0.009,0.15),std(0x15171b,'mob',{r:0.3,rim:0.2})); b.castShadow=true; mob.add(b);
  const s=new THREE.Mesh(new THREE.BoxGeometry(0.066,0.002,0.136),mobScrM); s.position.y=0.0055; mob.add(s); }
const MOB_REST=HIS.clone().add(V(0.36,0.79,-0.24));
const mobHalo=SLD.glowSprite(S.scene,0xcfe0ff,0);

// ---------------------------------------------------------------- the family: three cream wooden figures (no faces), hair caps that grey
const mom=R.makeFig(0xf0e4d0,'mom',{rim:0.16,lift:0.07}), dad=R.makeFig(0xe8dfcf,'dad',{rim:0.16,lift:0.07}), son=R.makeFig(PAL.CREAM,'son',{rim:0.16,lift:0.07});
const SC={mom:[0.93,0.95],dad:[1.0,1.0]};
function hairCap(key,r){ const m=std(0x2b1f18,key,{r:0.85,rim:0.1}); const h=add(new THREE.SphereGeometry(1,26,16,0,Math.PI*2,0,Math.PI*0.5),m); h.userData.r=r; return h; }
const momHair=hairCap('mh'), dadHair=hairCap('dh'), sonHair=hairCap('sh');
const bun=add(new THREE.SphereGeometry(1,20,14),momHair.material);
const sareeM=std(0xc8a3b2,'saree',{r:0.8,rim:0.14,rimCol:0xffd8e0,e:0xc8a3b2,ei:0.05}); sareeM.side=THREE.DoubleSide;
const pallu=add(new THREE.CylinderGeometry(1,1,1,12),sareeM), skirt=add(new THREE.CylinderGeometry(0.62,1,1,28,1,true),sareeM);
const HAIR_DARK=new THREE.Color(0x2b1f18), HAIR_GREY=new THREE.Color(0x8e8a84), HAIR_WHITE=new THREE.Color(0xdcd8cf);
function hairCol(m,g){ const c=g<0.5?HAIR_DARK.clone().lerp(HAIR_GREY,g*2):HAIR_GREY.clone().lerp(HAIR_WHITE,(g-0.5)*2); m.material.color.copy(c); }
function placeHair(h,J,hs,back=0.55){ const hd=J.head.clone().sub(J.neck).normalize(); const f=J.fwd.clone(); const pole=hd.clone().multiplyScalar(0.85).addScaledVector(f,-back).normalize();
  h.position.copy(J.head); h.scale.setScalar(0.13*hs*1.05); h.quaternion.setFromUnitVectors(UPV,pole); }
function limbMesh(m,a,b,r,rz=r){ const d=b.clone().sub(a); const len=Math.max(d.length(),1e-4); m.position.copy(a).add(b).multiplyScalar(0.5); m.scale.set(r,len,rz); m.quaternion.setFromUnitVectors(UPV,d.multiplyScalar(1/len)); }

// ---------------------------------------------------------------- ages
const sonAge=t=>keys(TL.ageKeys,t);
const pAge=t=>sonAge(t)+TL.parentGap;
const ageInt=t=>Math.floor(sonAge(t)+1e-6);
const greyMom=t=>sstep(42,60,pAge(t)), greyDad=t=>sstep(40,58,pAge(t));
const stoop=t=>sstep(46,58,pAge(t));
const grown=t=>sm5(clamp((t-TL.grow[0])/(TL.grow[1]-TL.grow[0])));

// ---------------------------------------------------------------- shot A: the hug that grows up
const M_ROOT=V(0.12,0,0.7), M_YAW=0;                           // Mom standing in front of the table, facing +x (the boy)
const SON_DIR=V(1,0,-0.32).normalize();                         // where he walks off to (right, past his chair, into the dark)
function shotA(t){
  const g=grown(t), ag=stoop(t);
  const take=sstep(TL.take[0],TL.take[1],t), hug=sstep(TL.hug[0],TL.hug[1],t), rel=sstep(TL.release[0],TL.release[1],t);
  const sS=lerp(0.64,1.0,g), sH=lerp(0.86,1.0,g);
  // son: stands in front of her, steps into the hug, grows, steps back, turns and walks off
  const gap=lerp(0.48,lerp(0.27,0.31,g),hug)+0.24*rel;
  let sRoot=M_ROOT.clone().add(V(gap,0,0)), sYaw=Math.PI;
  const tw=Math.max(0,t-TL.walk[0]);
  let P={...R.P0,p:0.04,tilt:lerp(-0.25,0.05,g)*(1-rel)+0.05*rel};
  const bounce=0.02*Math.sin(t*9)*(1-take)*(1-hug);
  P.p+=bounce;
  R.setScale(SC.mom[0],SC.mom[1]);
  // Mom: bends down to the boy, straightens as he grows, looks up at him at 18
  let Q={...R.P0,p:lerp(0.36,0.04,g)+0.18*hug*(1-g),tilt:lerp(0.22,-0.32,sm5(clamp(g*1.3-0.3)))*(1-0.5*rel)};
  const momJ0=R.skel(Q,M_ROOT,M_YAW);
  R.setScale(sS,sH);
  const sonJ0=R.skel(P,sRoot,sYaw);
  // tiffin hand-off point, between them at the boy's chest
  const HP=V(M_ROOT.x+0.27,lerp(0.82,0.86,take),M_ROOT.z+0.06);
  // hug targets: his hands on her back (waist when small, shoulder blades at 18); hers on his back
  const mF=momJ0.fwd, sF=sonJ0.fwd, side=V(0,0,1);
  const hY=Math.min(sonJ0.shL.y-0.12*sS,momJ0.neck.y-0.12);
  const backM=V(M_ROOT.x-0.1,hY,M_ROOT.z);
  const hugS=hug*(1-rel);
  if(t<TL.hug[1]){ const hold=1-hug; const tL=HP.clone().add(V(0.02,0.03,0.07)), tR=HP.clone().add(V(0.02,0.03,-0.07));
    const reach=sstep(0.0,TL.take[0]+0.2,t);
    P.tL=sonJ0.shL.clone().lerp(tL,reach).lerp(backM.clone().add(V(0,0,-0.11)),hug); P.wL=1; P.pL=V(-0.2,-0.5,0.8);
    P.tR=sonJ0.shR.clone().lerp(tR,reach).lerp(backM.clone().add(V(0,0,0.11)),hug); P.wR=reach; P.pR=V(-0.2,-0.5,-0.8); }
  else { P.tL=backM.clone().add(V(0,0,-0.11)); P.wL=hugS; P.pL=V(-0.2,-0.3,0.9); P.tR=backM.clone().add(V(0,0,0.11)); P.wR=hugS; P.pR=V(-0.2,-0.3,-0.9); }
  // hold her tight: lean in, head turned onto her (small) / her head on his chest (grown)
  P.p+=0.08*hugS; P.hy=0.35*hugS*(1-g); P.tilt+=0.12*hugS*(1-g);
  if(rel>0&&t<TL.walk[0]+0.3){ P.p=lerp(P.p,0.04,rel); }
  // walking off
  if(tw>0){ const turn=sstep(0,0.35,tw); const d0=V(-1,0,0); const a0=yawOf(d0), a1=yawOf(SON_DIR); let da=a1-a0; da=Math.atan2(Math.sin(da),Math.cos(da)); sYaw=a0+da*turn;
    const dist=1.25*(tw<0.45?tw*tw/0.9:tw-0.225); sRoot=sRoot.clone().addScaledVector(SON_DIR,dist*sstep(0.05,0.3,tw)+0.0);
    P=R.gait({...R.P0,p:0.1,tilt:0.02},dist/1.3*Math.PI*2,sstep(0.05,0.3,tw)); P.sR=-0.1; P.eR=0.5; }
  R.setScale(sS,sH); const sonJ=R.skel(P,sRoot,sYaw);
  // Mom's hands: hold the tiffin out, then on the boy (his head / back), then one hand reaches after him and waves
  const backS=sonJ.neck.clone().addScaledVector(sonJ.fwd,-0.11*sS).add(V(0,-0.1*sS,0));
  const mY=Math.min(momJ0.shL.y-0.18,backS.y);
  if(t<TL.hug[0]){ Q.tL=HP.clone().add(V(-0.02,0.04,0.0)); Q.wL=1-take*0.0; Q.pL=V(-0.2,-0.6,0.8); Q.tR=momJ0.hipR.clone().add(V(0.05,-0.05,-0.08)); Q.wR=0.0; }
  else { const onBack=sstep(TL.hug[0],TL.hug[1],t)*(1-rel);
    Q.tL=V(sRoot.x+0.06,mY,sRoot.z-0.12+0.0); Q.wL=onBack; Q.pL=V(-0.2,-0.3,0.9); Q.tR=V(sRoot.x+0.06,mY,sRoot.z+0.12); Q.wR=onBack; Q.pR=V(-0.2,-0.3,-0.9); }
  if(rel>0){ const wave=sstep(TL.walk[0]+0.1,TL.walk[0]+0.45,t); const reachOut=rel*(1-wave);
    const after=momJ0.neck.clone().addScaledVector(SON_DIR,0.42).add(V(0.06,-0.12,0.18));
    const up=momJ0.shL.clone().add(V(0.12,0.36+0.03*Math.sin(t*11),0.12+0.06*Math.sin(t*9)));
    Q.tL=after.clone().lerp(up,wave); Q.wL=Math.max(reachOut,wave); Q.pL=V(-0.3,-0.6,0.8);
    Q.hy=-0.5*wave; Q.ty=-0.25*wave; Q.tilt=lerp(Q.tilt,-0.05,rel); }
  Q.p+=0.04*hugS*g; // her head rests on his chest
  R.setScale(SC.mom[0],SC.mom[1]); const momJ=R.skel(Q,M_ROOT,M_YAW);
  // tiffin: in her hand -> his hands -> hangs from his hand on her back -> fades as he grows
  let tp=HP.clone().add(V(0,0.03,0)); if(t>TL.take[1]) tp=sonJ.hR.clone().add(V(0,-0.02,0)); else tp=HP.clone().lerp(sonJ.hR.clone(),take*0.4);
  const tA=1-sstep(TL.grow[0],TL.grow[0]+0.6,t);
  // Dad at the back: reading the paper, looks over (laughs) at the hug, stands up to see him off, waves
  const up=sstep(TL.dadUp[0],TL.dadUp[1],t);
  const dRoot=seatRoot(DAD_X).lerp(V(DAD_X,0,BACKZ+0.36),up);
  let D=R.blend({...CHAIRP},{...R.P0,p:0.05},up); D.p+=0.02*Math.sin(t*1.7);
  const look=sstep(1.2,1.9,t); D.hy=-0.55*look*(1-0.3*up); D.ty=-0.15*look;
  const laugh=bump(t,1.7,1.3); D.p+=-0.06*laugh+0.02*laugh*Math.sin(t*26); D.tilt=-0.2*laugh;
  const read=1-sstep(1.0,1.8,t);
  R.setScale(1,1); const dJ0=R.skel(D,dRoot,yawOf(FACE_Z));
  const paperC=V(DAD_X,lerp(1.02,0.8,1-read)+0.0,-0.18-0.08*read);
  if(up<0.5){ D.tL=paperC.clone().add(V(-0.2,0.0,0)); D.tR=paperC.clone().add(V(0.2,0.0,0)); D.wL=D.wR=1-up*2; D.pL=V(-0.3,-0.7,0.7); D.pR=V(-0.3,-0.7,-0.7); }
  const dwave=sstep(TL.walk[0]+0.2,TL.walk[0]+0.6,t);
  if(dwave>0){ D.tR=dJ0.shR.clone().add(V(0.14,0.36+0.03*Math.sin(t*10+1),0.08)); D.wR=dwave; D.pR=V(-0.3,-0.6,-0.8); D.hy=-0.5; }
  const dJ=R.skel(D,dRoot,yawOf(FACE_Z));
  return {momJ,sonJ,dadJ:dJ,sS,sH,g,tiffin:{pos:tp,a:tA},paper:{pos:paperC,a:1-up,fold:1-read},dadChairZ:BACKZ-0.25*up,bagA:sstep(0.75,0.95,g),standingMom:true,ag};
}

// ---------------------------------------------------------------- shot B: two lamps in the dark, the calls
const CALLS=TL.calls;
const callAt=t=>{ for(const c of CALLS){ const u=(t-c.t)/c.dur; if(u>-0.05&&u<1.25) return {c,u}; } return null; };
const P0=PH_BASE.clone().add(V(0,0.16,0)), P1=MOB_REST.clone().add(V(0,0.04,0));
const arc=(a,b,u,hgt=0.9)=>a.clone().lerp(b,u).add(V(0,hgt*4*u*(1-u),0));
function shotB(t){
  const ag=stoop(t);
  const cu=callAt(t);
  // --- parents seated side by side, facing the camera, the phone between them on Mom's left
  const mR=seatRoot(MOM_X), dR=seatRoot(DAD_X);
  let Q={...CHAIRP,p:0.12+0.2*ag,tilt:0.1+0.12*ag}; Q.p+=0.012*Math.sin(2*Math.PI*0.25*t);
  let D={...CHAIRP,p:0.1+0.26*ag,tilt:0.12+0.12*ag}; D.p+=0.012*Math.sin(2*Math.PI*0.22*t+1);
  R.setScale(SC.mom[0],SC.mom[1]); const mJ0=R.skel(Q,mR,yawOf(FACE_Z));
  const ear=mJ0.head.clone().add(V(-0.12,-0.02,0.02));
  // Mom between calls: hands folded on the table, looking at the phone
  const fold=V(MOM_X-0.02,TOP+0.03,-0.2);
  Q.tL=fold.clone().add(V(-0.06,0,0.02)); Q.tR=fold.clone().add(V(0.06,0,0.0)); Q.wL=Q.wR=1; Q.pL=V(-0.3,-0.7,0.7); Q.pR=V(-0.3,-0.7,-0.7);
  Q.hy=-0.3; Q.tilt+=0.1;
  let rcv=null, lift=0, ringing=0, momLit=0, hisLit=0, hisLift=0, flip=0, pulse=null;
  if(cu){ const {c,u}=cu;
    if(c.dir==='in'){ lift=sstep(0.0,0.17,u)*(1-sstep(c.ans?0.86:0.9,c.ans?1.0:1.12,u)); hisLit=sstep(0.52,0.56,u)*(1-sstep(c.ans?0.9:(c.flip?0.66:0.88),c.ans?1.0:(c.flip?0.72:1.0),u));
      if(u>0.1&&u<0.6) pulse={u:Math.pow(clamp((u-0.1)/0.46),1.8),from:P0,to:P1,a:1-sstep(0.54,0.6,u)};
      if(c.ans) hisLift=sstep(0.58,0.72,u)*(1-sstep(0.86,0.98,u)); if(c.flip) flip=sstep(0.6,0.72,u);
      momLit=c.ans?win(u,0.7,0.9,0.05):0; }
    else { hisLit=sstep(0.0,0.08,u)*(1-sstep(0.8,0.9,u)); hisLift=sstep(0.02,0.16,u)*(1-sstep(0.78,0.9,u));
      if(u>0.12&&u<0.55) pulse={u:1-Math.pow(1-clamp((u-0.12)/0.38),1.8),from:P1,to:P0,a:1-sstep(0.48,0.55,u)};
      ringing=win(u,0.48,0.62,0.02); lift=sstep(0.56,0.66,u)*(1-sstep(0.98,1.15,u)); momLit=win(u,0.64,0.98,0.05); } }
  if(lift>0){ Q.tL=Q.tL.clone().lerp(ear.clone().add(V(0.0,-0.06,0.03)),lift); Q.pL=V(-0.5,-0.4,0.6); Q.hy=lerp(-0.3,0.12,lift); Q.tilt-=0.12*lift; Q.ty=0.1*lift;
    rcv=CRADLE.clone().lerp(ear,sm5(lift)); }
  // she brightens while he talks (a small lift of the shoulders), sinks a little when he doesn't pick up
  const sink=cu&&cu.c.dir==='in'&&!cu.c.ans?sstep(0.6,0.95,cu.u)*(1-sstep(1.1,1.25,cu.u)):0;
  Q.p+=-0.06*momLit+0.07*sink; Q.tilt+=0.15*sink;
  R.setScale(SC.mom[0],SC.mom[1]); const momJ=R.skel(Q,mR,yawOf(FACE_Z));
  // --- Dad: hands on the table, later on his stick; turns to Mom when she's on the phone
  const stickA=sstep(TL.stick,TL.stick+0.6,t);
  const stickTop=V(DAD_X-0.3,0.88,-0.34);
  D.tR=V(DAD_X+0.08,TOP+0.03,-0.22); D.wR=1; D.pR=V(-0.3,-0.7,-0.7);
  D.tL=V(DAD_X-0.12,TOP+0.03,-0.22).lerp(stickTop.clone().add(V(-0.03,0.02,0)),stickA); D.wL=1; D.pL=V(-0.3,-0.7,0.7);
  D.hy=0.35*Math.max(lift,ringing); D.ty=0.1*lift;
  R.setScale(1,1); const dadJ=R.skel(D,dR,yawOf(FACE_Z));
  // --- him: at the desk, back to us, typing; picks up (turns a little, leans back), flips the phone, or doesn't look
  let P={...CHAIRP,p:0.22,tilt:0.18}; const type=Math.sin(t*14);
  const kb=HIS.clone().add(V(0,0.81,-0.33));
  P.tL=kb.clone().add(V(0.09,0.01*Math.max(0,type),0)); P.tR=kb.clone().add(V(-0.09,0.01*Math.max(0,-type),0)); P.wL=P.wR=1; P.pL=V(-0.3,-0.7,0.6); P.pR=V(-0.3,-0.7,-0.6);
  R.setScale(1,1); const sJ0=R.skel(P,HIS_ROOT,yawOf(V(0,0,-1)));
  const hisEar=sJ0.head.clone().add(V(0.12,-0.02,0.0));
  let mobPos=MOB_REST.clone(), mobRot=0;
  if(hisLift>0){ P.tL=P.tL.clone().lerp(hisEar.clone().add(V(0,-0.05,0.02)),hisLift); P.pL=V(-0.5,-0.4,0.7); P.p=lerp(P.p,0.02,hisLift); P.tilt=lerp(P.tilt,-0.08,hisLift); P.ty=-0.25*hisLift; P.hy=0.2*hisLift;
    mobPos=MOB_REST.clone().lerp(hisEar,sm5(hisLift)); }
  if(flip>0){ const r=sstep(0.0,0.5,flip)*(1-sstep(0.6,1,flip)); P.tL=P.tL.clone().lerp(MOB_REST.clone().add(V(0,0.04,0)),r); P.hy=0.25*r; mobRot=Math.PI*sstep(0.3,0.7,flip); }
  const glance=cu&&cu.c.dir==='in'&&!cu.c.ans&&!cu.c.flip?0:0;
  R.setScale(1,1); const sonJ=R.skel(P,HIS_ROOT,yawOf(V(0,0,-1)));
  return {momJ,dadJ,sonJ,rcv,ringing,pulse,hisLit:hisLit*(flip>0.5?0:1),mobPos,mobRot,hisLift,stickA,stickTop,ag,glance};
}

// ---------------------------------------------------------------- the end: waiting by the silent phone
function endPose(t,B){ // modifies shot B's parents after the push-in starts: Mom's hand near the phone, hope at the ring
  const ring=sstep(TL.ring,TL.ring+0.25,t), reach=sstep(TL.ring+0.35,TL.silence+0.4,t);
  const ag=stoop(t);
  let Q={...CHAIRP,p:0.12+0.2*ag+0.012*Math.sin(2*Math.PI*0.25*t),tilt:0.22+0.12*ag};
  const near=V(MOM_X-0.22,TOP+0.03,-0.12);
  Q.tR=V(MOM_X+0.05,TOP+0.03,-0.22); Q.wR=1; Q.pR=V(-0.3,-0.7,-0.7);
  Q.tL=near.clone().lerp(CRADLE.clone().add(V(0.08,-0.01,0.03)),sm5(reach)); Q.wL=1; Q.pL=V(-0.3,-0.7,0.7);
  Q.hy=-0.38-0.12*ring; Q.tilt+=0.08-0.18*ring; Q.p-=0.05*ring;
  R.setScale(SC.mom[0],SC.mom[1]); B.momJ=R.skel(Q,seatRoot(MOM_X),yawOf(FACE_Z)); B.rcv=null;
  B.ringing=win(t,TL.ring,TL.ring+0.75,0.03);
  return B; }

// ---------------------------------------------------------------- camera: Catmull-Rom through the keys of the current shot
const CAMS=TL.cams.map(([t,p,l])=>({t,p:V(...p),l:V(...l)}));
const SHOTS=[]; { let s=0; for(let i=1;i<CAMS.length;i++) if(CAMS[i].t===CAMS[i-1].t){ SHOTS.push(CAMS.slice(s,i)); s=i; } SHOTS.push(CAMS.slice(s)); }
const cr=(a,b,c,d,u)=>{ const u2=u*u,u3=u2*u; return b.clone().multiplyScalar(2).add(c.clone().sub(a).multiplyScalar(u)).add(a.clone().multiplyScalar(2).sub(b.clone().multiplyScalar(5)).add(c.clone().multiplyScalar(4)).sub(d).multiplyScalar(u2)).add(b.clone().multiplyScalar(3).sub(a).sub(c.clone().multiplyScalar(3)).add(d).multiplyScalar(u3)).multiplyScalar(0.5); };
function camAt(t){ const sh=SHOTS.find((s,i)=>i===SHOTS.length-1||t<SHOTS[i+1][0].t);
  const k=sh; if(k.length===1) return {pos:k[0].p.clone(),look:k[0].l.clone(),t0:k[0].t,t1:DUR};
  let i=0; while(i<k.length-2&&t>=k[i+1].t) i++;
  const u=sm5(clamp((t-k[i].t)/(k[i+1].t-k[i].t)))*0.5+clamp((t-k[i].t)/(k[i+1].t-k[i].t))*0.5;
  const g=(j)=>k[Math.max(0,Math.min(k.length-1,j))];
  const pos=cr(g(i-1).p,g(i).p,g(i+1).p,g(i+2).p,u), look=cr(g(i-1).l,g(i).l,g(i+1).l,g(i+2).l,u);
  const idx=SHOTS.indexOf(sh); return {pos,look,t0:k[0].t,t1:idx<SHOTS.length-1?SHOTS[idx+1][0].t:DUR}; }

// ---------------------------------------------------------------- pulse (a call): a gold light with a fading trail
const NTR=30; const trail=[]; for(let i=0;i<NTR;i++) trail.push(SLD.glowSprite(S.scene,i===0?0xfff0d0:0xffc878,0));
const pulseLight=new THREE.PointLight(0xffc878,0,3.2,2); S.scene.add(pulseLight);
const core=SLD.glowSprite(S.scene,0xffffff,0);
function setPulse(p){ if(!p){ trail.forEach(s=>s.material.opacity=0); core.material.opacity=0; pulseLight.intensity=0; return; }
  for(let i=0;i<NTR;i++){ const u=p.u-i*0.014; const s=trail[i]; if(u<0){ s.material.opacity=0; continue; }
    s.position.copy(arc(p.from,p.to,u)); const k=1-i/NTR; s.scale.setScalar((i===0?1.7:0.95)*(0.3+0.7*k)); s.material.opacity=p.a*(i===0?1.0:0.8*k*k); }
  core.position.copy(arc(p.from,p.to,p.u)); core.scale.setScalar(0.45); core.material.opacity=p.a;
  pulseLight.position.copy(arc(p.from,p.to,p.u)); pulseLight.intensity=2.5*p.a; }

// ---------------------------------------------------------------- one frame
function poseMom(J,hs,standing){ R.setScale(SC.mom[0],SC.mom[1]); R.poseFig(mom,J);
  placeHair(momHair,J,SC.mom[1]); const hd=J.head.clone().sub(J.neck).normalize();
  bun.position.copy(J.head).addScaledVector(J.fwd,-0.115*SC.mom[1]).addScaledVector(hd,0.03); bun.scale.setScalar(0.058);
  // pallu: over the left shoulder, across the chest to the right hip; skirt only while standing (seated, the table hides her legs)
  limbMesh(pallu,J.shL.clone().addScaledVector(J.fwd,0.035).add(V(0,0.03,0)),J.hipR.clone().addScaledVector(J.fwd,0.06),0.05,0.02);
  skirt.visible=standing; if(standing){ const top=J.hip.y+0.03, bot=0.05; const c=V(J.hip.x,(top+bot)/2,J.hip.z); skirt.position.copy(c); skirt.scale.set(0.17,top-bot,0.155); skirt.rotation.set(0,0,0); } }
function setT(t){
  const shotBActive=t>=TL.cut;
  const pA=shotBActive?null:shotA(t);
  let B=shotBActive?shotB(t):null; if(B&&t>=TL.push[0]) B=endPose(t,B);
  const st=pA||B;
  // --- figures
  if(pA){ R.setScale(pA.sS,pA.sH); R.poseFig(son,pA.sonJ); placeHair(sonHair,pA.sonJ,pA.sH,0.45);
    poseMom(pA.momJ,SC.mom[1],true); R.setScale(1,1); R.poseFig(dad,pA.dadJ); placeHair(dadHair,pA.dadJ,1,0.5); }
  else { R.setScale(1,1); R.poseFig(son,B.sonJ); placeHair(sonHair,B.sonJ,1,0.45);
    poseMom(B.momJ,SC.mom[1],false); R.setScale(1,1); R.poseFig(dad,B.dadJ); placeHair(dadHair,B.dadJ,1,0.5); }
  hairCol(momHair,greyMom(t)); hairCol(dadHair,greyDad(t)); sonHair.material.color.copy(HAIR_DARK);
  dadHair.scale.multiplyScalar(1.0-0.0*greyDad(t));
  // --- chairs
  placeChair(momChair,V(MOM_X,0,pA?BACKZ-0.2:BACKZ),FACE_Z); placeChair(dadChair,V(DAD_X,0,pA?pA.dadChairZ:BACKZ),FACE_Z);
  // his chair: pulled out at the right end while he is a boy; once he's gone it stands pushed in on our side of the table, facing them
  if(shotBActive) placeChair(sonChair,V(0.02,0,0.6),V(0,0,-1)); else placeChair(sonChair,V(1.22,0,0.02),V(-1,0,0));
  // --- tiffin, paper, bag, stick
  tiffin.visible=!!pA&&pA.tiffin.a>0.01; if(tiffin.visible){ tiffin.position.copy(pA.tiffin.pos); tifM.opacity=pA.tiffin.a; tifM.transparent=pA.tiffin.a<0.999; }
  paper.visible=!!pA&&pA.paper.a>0.01; if(paper.visible){ paper.position.copy(pA.paper.pos); paper.rotation.set(-0.15-1.2*pA.paper.fold,0,0); paperM.opacity=pA.paper.a; paperM.transparent=pA.paper.a<0.999; }
  { const J=pA?pA.sonJ:B.sonJ; const a=pA?pA.bagA:0; bag.visible=a>0.01; if(bag.visible){ const up=J.neck.clone().sub(J.hip).normalize(); const c=J.hip.clone().lerp(J.neck,0.55).addScaledVector(J.fwd,-0.16*(pA?pA.sS:1));
    bag.position.copy(c); bag.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(J.fwd.clone(),up,J.fwd.clone().cross(up).normalize())); bagM.opacity=a; bagM.transparent=a<0.999; } }
  stick.visible=!!B&&B.stickA>0.01; if(stick.visible){ stick.position.set(DAD_X-0.38,0,-0.27); stick.rotation.set(0.05,Math.PI,0.09); }
  // lids on the plates: the dinner going cold (from the wide shot on)
  const lidA=shotBActive?sstep(12.4,13.2,t)*0+1:0; for(const k in lids){ lids[k].visible=shotBActive&&(k!=='son'||true); }
  // --- the phone: receiver on the cradle or at her ear; ringing jiggle; cord
  const rp=st.rcv||CRADLE; const jig=(B?B.ringing:0)*0.006*Math.sin(t*2*Math.PI*21);
  receiver.position.copy(rp).add(V(0,jig,0));
  if(st.rcv){ const toHead=(B.momJ.head.clone().sub(st.rcv)); receiver.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(V(0,1,0).clone().cross(V(0,0,1)).negate(),V(0,1,0),V(0,0,1))); receiver.rotation.set(0,0,Math.PI/2*sstep(0,1,st.rcv.distanceTo(CRADLE)/0.4)); }
  else receiver.rotation.set(0,0.35,0);
  setCord(PH_BASE.clone().add(V(-0.1,0.03,0.0)),receiver.position.clone().add(V(st.rcv?0:-0.09,-0.02,0)));
  const ringI=B?B.ringing:0;
  // --- his lamp, screen glow, mobile glow
  const on=shotBActive?sstep(TL.lampOn,TL.lampOn+0.12,t):0;
  spot2.intensity=46*on; beam2U.uI.value=on; screenLight.intensity=0.5*on; screenLight.position.copy(HIS).add(V(0,1.0,-0.3));
  mob.visible=shotBActive; if(B){ mob.position.copy(B.mobPos); mob.rotation.set(B.mobRot,0,0); mobScrM.emissiveIntensity=2.2*B.hisLit; mobHalo.position.copy(B.mobPos).add(V(0,0.05,0)); mobHalo.scale.setScalar(0.42); mobHalo.material.opacity=0.55*B.hisLit; } else mobHalo.material.opacity=0;
  setPulse(B?B.pulse:null);
  // --- the gold lamp: aimed at the hug (shot A), the table (shot B), narrows onto the red phone at the end
  const nar=sm5(sstep(TL.narrow[0],TL.narrow[1],t));
  if(pA) aim(AIM_A,CONE_A); else aim(AIM_B.clone().lerp(PH_BASE.clone().setY(0.0).add(V(0.02,0,0.02)),nar),lerp(CONE_B,CONE_END,nar));
  const push=shotBActive?sstep(TL.push[0],TL.push[1],t):0;
  redM.emissiveIntensity=lerp(0.05,0.2,push)+0.35*ringI; redHalo.position.copy(PH_BASE).add(V(0,0.1,0)); redHalo.scale.setScalar(0.42+0.3*ringI); redHalo.material.opacity=lerp(0.03,0.1,push)+0.16*ringI;
  redLight.position.copy(PH_BASE).add(V(0,0.25,0.1)); redLight.intensity=0.12*push+0.45*ringI;
  // --- camera
  const c=camAt(t); S.cam.position.copy(c.pos); S.cam.lookAt(c.look);
  const pay=0.1*(B?B.ringing:0);
  S.tick(t,pay); S.beamU.uI.value*=lerp(1.0,0.75,nar); S.moteU.uOp.value=lerp(1,0.8,nar);
  // the end stays dark but not black: a whisper of warm fill keeps the two of them readable as she reaches for the phone
}

// ---------------------------------------------------------------- overlay / sound data
const v3=new THREE.Vector3();
const LBL_AT=HIS.clone().add(V(-0.3,2.35,0));
window.metaAt=t=>{ setT(t); S.cam.updateMatrixWorld(); const labels=[];
  for(const c of CALLS){ if(!c.label) continue; const u=(t-c.t)/c.dur; if(u<0.45||u>1.25) continue;
    v3.copy(LBL_AT).project(S.cam); labels.push({text:c.label,x:(v3.x*0.5+0.5)*1080,y:(0.5-v3.y*0.5)*1920,a:sstep(0.45,0.6,u)*(1-sstep(1.05,1.25,u))}); }
  return {age:ageInt(t),page:Math.floor(pAge(t)+1e-6),labels}; };
window.events={...TL};
window.renderAt=(t,K=3)=>{ const c=camAt(t); return S.renderAt(setT,t,K,{t0:c.t0,t1:c.t1}); };
window.DBGF=()=>({trail:trail.slice(0,3).map(s=>[s.position.toArray().map(x=>+x.toFixed(2)),+s.material.opacity.toFixed(2)])});
window.ready=true;
