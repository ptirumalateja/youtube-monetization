// Friends in Every Group, v6 (warm cafe). Four friends on a cafe booth bench, all facing the camera, each with their own
// colour and prop so you can tell them apart instantly: LATE (blue, headphones), PHOTO (yellow, cap), HUNGRY (pink, hair
// bun), PAYS (green, glasses). Shots are hard cuts: a selfie from the phone's point of view (the late one's spot empty),
// then one tight shot per friend with their gag, then the selfie again with all four for the end card.
// The bill is the one red object. (v1-v5, the dark-void version, is kept as scene_v5.js for reference.)
//
// World: bench along x at the back (friends face +z, toward the camera), table in front of them, cafe wall behind.
// renderAt(t) is pure (no state between frames) and never blurs across a cut. metaAt(t) gives overlay/sound data.
import * as THREE from 'three';
import * as SLD from './sld.js';
const {V,clamp,sstep,lerp,sm5,rng,yawOf,PAL}=SLD;
const TL=await (await fetch('./timeline.json')).json();
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960, DUR=TL.duration;

// ---------------------------------------------------------------- stage: the series kit, re-lit as a warm cafe
const S=SLD.createStage({W,H,lamp:V(0,4.4,0.2),lampTarget:V(0,0,-0.2),cone:0.62,spot:46,beam:0.05,motes:900});
const R=SLD.createRig(S.scene);
const WARM=new THREE.Color(0x2b1a10); S.scene.background=WARM; S.scene.fog=new THREE.FogExp2(WARM,0.05);
S.scene.add(new THREE.HemisphereLight(0xffd9a8,0x3a2414,0.75));
const fillL=new THREE.DirectionalLight(0xffe2bc,0.55); fillL.position.set(-1.5,2.5,4); S.scene.add(fillL);
S.floor.material.color.set(0x5a3c28);
const TOP=0.74;

// cafe wall: warm plaster, string-light bokeh, two dark frames
function wallTex(){ const c=document.createElement('canvas'); c.width=1024; c.height=512; const g=c.getContext('2d'); const Rn=rng(8);
  const gr=g.createLinearGradient(0,0,0,512); gr.addColorStop(0,'#4a2e1c'); gr.addColorStop(1,'#6b4329'); g.fillStyle=gr; g.fillRect(0,0,1024,512);
  g.fillStyle='rgba(20,12,8,0.55)'; g.fillRect(150,170,170,120); g.fillRect(700,150,140,170);
  for(let k=0;k<70;k++){ const x=k/70*1024+Rn()*10, y=60+28*Math.sin(k*0.35)+Rn()*6, r=10+Rn()*14;
    const rg=g.createRadialGradient(x,y,0,x,y,r); rg.addColorStop(0,'rgba(255,214,150,0.95)'); rg.addColorStop(0.4,'rgba(255,190,110,0.35)'); rg.addColorStop(1,'rgba(255,170,90,0)'); g.fillStyle=rg; g.beginPath(); g.arc(x,y,r,0,7); g.fill(); }
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; return t; }
{ const wallShape=new THREE.Shape([new THREE.Vector2(-4.5,-2.25),new THREE.Vector2(4.5,-2.25),new THREE.Vector2(4.5,2.25),new THREE.Vector2(-4.5,2.25)]);
  wallShape.holes.push(new THREE.Path([new THREE.Vector2(1.5,-2.25),new THREE.Vector2(2.4,-2.25),new THREE.Vector2(2.4,0.1),new THREE.Vector2(1.5,0.1)]));
  const wallGeo=new THREE.ShapeGeometry(wallShape); { const uv=wallGeo.attributes.uv, pos=wallGeo.attributes.position; for(let i=0;i<uv.count;i++) uv.setXY(i,(pos.getX(i)+4.5)/9,(pos.getY(i)+2.25)/4.5); }
  const wall=new THREE.Mesh(wallGeo,new THREE.MeshStandardMaterial({map:wallTex(),roughness:0.9,emissive:0xffffff,emissiveMap:null,emissiveIntensity:0}));
  wall.position.set(0,2.0,-1.25); wall.receiveShadow=true; S.scene.add(wall);
  const glow=new THREE.Mesh(wallGeo,new THREE.MeshBasicMaterial({map:wall.material.map,transparent:true,opacity:0.35,blending:THREE.AdditiveBlending,depthWrite:false}));
  glow.position.set(0,2.0,-1.24); S.scene.add(glow); }
// pendant bulbs over the table
for(const x of [-1.1,0,1.1]){ const b=new THREE.Mesh(new THREE.SphereGeometry(0.06,20,12),new THREE.MeshBasicMaterial({color:0xffe1a8})); b.position.set(x,2.35,-0.1); S.scene.add(b);
  const cord=new THREE.Mesh(new THREE.CylinderGeometry(0.004,0.004,1.6),new THREE.MeshBasicMaterial({color:0x111111})); cord.position.set(x,3.15,-0.1); S.scene.add(cord);
  const pl=new THREE.PointLight(0xffc98a,0.9,3.2,2); pl.position.set(x,2.25,-0.1); S.scene.add(pl); SLD.glowSprite(S.scene,0xffc98a,0.35).position.set(x,2.35,-0.1); }

// ---------------------------------------------------------------- wood, bench, table, door, plates, glasses
function woodTex(seed,base){ const c=document.createElement('canvas'); c.width=1024; c.height=256; const g=c.getContext('2d'); const Rn=rng(seed);
  g.fillStyle=base; g.fillRect(0,0,1024,256);
  for(let k=0;k<260;k++){ const y=Rn()*256, a=0.04+Rn()*0.1; g.strokeStyle=Rn()<0.6?`rgba(0,0,0,${a})`:`rgba(255,220,180,${a*0.5})`; g.lineWidth=0.6+Rn()*2.2;
    g.beginPath(); g.moveTo(0,y); for(let x=0;x<=1024;x+=32) g.lineTo(x,y+Math.sin(x*0.004+k)*3+Math.sin(x*0.021+k*1.7)*1.2); g.stroke(); }
  const t=new THREE.CanvasTexture(c); t.wrapS=t.wrapT=THREE.RepeatWrapping; t.colorSpace=THREE.SRGBColorSpace; return t; }
const WOOD=new THREE.MeshStandardMaterial({color:0xb08560,map:woodTex(3,'#4a3020'),roughness:0.45,metalness:0});
const BENCH=new THREE.MeshStandardMaterial({color:0x2f6d6a,roughness:0.7});   // teal upholstered booth
const box=(w,h,d,m,x,y,z)=>{ const b=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m); b.position.set(x,y,z); b.castShadow=b.receiveShadow=true; S.scene.add(b); return b; };
box(2.9,0.1,0.5,BENCH,0,0.4,-0.66); box(2.9,0.36,0.46,WOOD,0,0.17,-0.66); box(2.9,0.75,0.12,BENCH,0,0.82,-0.95);
box(2.3,0.05,0.64,WOOD,0,TOP-0.025,0.05); box(2.3,0.62,0.04,WOOD,0,TOP-0.36,0.36);   // front panel: no legs showing under the table
// the door the late one comes in through (right side), with a bell
const DOORX=1.95;
box(0.9,2.15,0.6,new THREE.MeshBasicMaterial({color:0x0b0705}),DOORX,1.075,-1.55);   // the dark doorway behind the wall line
box(0.08,2.25,0.1,WOOD,DOORX-0.49,1.12,-1.22); box(0.08,2.25,0.1,WOOD,DOORX+0.49,1.12,-1.22); box(1.06,0.1,0.1,WOOD,DOORX,2.25,-1.22);
const doorPivot=new THREE.Group(); doorPivot.position.set(DOORX-0.45,0,-1.25); S.scene.add(doorPivot);
{ const d=new THREE.Mesh(new THREE.BoxGeometry(0.88,2.1,0.05),WOOD); d.position.set(0.44,1.05,0); d.castShadow=true; doorPivot.add(d); }
const bell=new THREE.Mesh(new THREE.SphereGeometry(0.05,16,10,0,Math.PI*2,0,Math.PI/2),new THREE.MeshStandardMaterial({color:0xd4a843,metalness:0.6,roughness:0.3})); bell.position.set(DOORX-0.35,2.15,-1.15); S.scene.add(bell);
const PLATEM=new THREE.MeshStandardMaterial({color:0xcfc6b6,roughness:0.5});
const FRYM=new THREE.MeshStandardMaterial({color:0xe8b85a,roughness:0.6});
const GLASSM=new THREE.MeshStandardMaterial({color:0xdde6ea,roughness:0.08,transparent:true,opacity:0.45,depthWrite:false});
const DRINK=[0xd96b2b,0x7a3b1c,0xe8c547,0x5aa0d8];
const fryGeo=new THREE.BoxGeometry(0.014,0.014,0.085);
const SEATX={PAYS:-0.66,PHOTO:-0.22,HUNGRY:0.22,LATE:0.66};
const FRIES={};
Object.entries(SEATX).forEach(([id,x],i)=>{ const p=new THREE.Mesh(new THREE.CylinderGeometry(0.13,0.1,0.018,40),PLATEM); p.position.set(x,TOP+0.009,0.02); p.receiveShadow=true; S.scene.add(p);
  const gl=new THREE.Mesh(new THREE.CylinderGeometry(0.035,0.03,0.13,20),GLASSM); gl.position.set(x+0.16,TOP+0.065,-0.08); S.scene.add(gl);
  const dr=new THREE.Mesh(new THREE.CylinderGeometry(0.031,0.027,0.08,20),new THREE.MeshStandardMaterial({color:DRINK[i],roughness:0.3})); dr.position.set(x+0.16,TOP+0.045,-0.08); S.scene.add(dr);
  const Rf=rng(40+i); FRIES[id]=[]; for(let k=0;k<9;k++){ const f=new THREE.Mesh(fryGeo,FRYM); f.position.set(x+(Rf()-0.5)*0.12,TOP+0.026+Rf()*0.012,0.02+(Rf()-0.5)*0.12); f.rotation.set(0,Rf()*3,0.2*(Rf()-0.5)); f.castShadow=true; S.scene.add(f); FRIES[id].push(f); } });
const heldFry=new THREE.Mesh(fryGeo,FRYM); S.scene.add(heldFry);
// the bill (the one red object)
const bill=new THREE.Mesh(new THREE.BoxGeometry(0.2,0.018,0.3),new THREE.MeshStandardMaterial({color:PAL.RED,roughness:0.5,emissive:PAL.RED,emissiveIntensity:0.15})); bill.castShadow=true; S.scene.add(bill);
// phones (the photographer's, the late one's, the payer's)
function makePhone(){ const g=new THREE.Group(); const b=new THREE.Mesh(new THREE.BoxGeometry(0.075,0.15,0.012),new THREE.MeshStandardMaterial({color:0x3a3d46,roughness:0.3,metalness:0.4}));
  const sc=new THREE.Mesh(new THREE.PlaneGeometry(0.065,0.135),new THREE.MeshBasicMaterial({color:0xcfe3ff})); sc.position.z=0.007; g.add(b,sc); S.scene.add(g); return g; }
const PHONES={PHOTO:makePhone(),LATE:makePhone(),PAYS:makePhone()}; PHONES.PHOTO.scale.setScalar(1.35);
const flash=SLD.glowSprite(S.scene,0xffffff,0); const flashL=new THREE.PointLight(0xffffff,0,5,2); S.scene.add(flashL); S.NOREFL.push(flash);

// ---------------------------------------------------------------- faces
function faceTex(kind){ const c=document.createElement('canvas'); c.width=c.height=256; const g=c.getContext('2d');
  g.strokeStyle=g.fillStyle='#1d1610'; g.lineWidth=13; g.lineCap='round';
  const eye=(x,y,r=13)=>{ g.beginPath(); g.arc(x,y,r,0,7); g.fill(); };
  const arcEye=(x,y,up)=>{ g.beginPath(); up?g.arc(x,y+8,16,Math.PI*1.15,Math.PI*1.85):g.arc(x,y-10,16,Math.PI*0.15,Math.PI*0.85); g.stroke(); };
  const mouthSmile=(r=34)=>{ g.beginPath(); g.arc(128,140,r,0.2*Math.PI,0.8*Math.PI); g.stroke(); };
  ({ smile:()=>{ eye(96,110); eye(160,110); mouthSmile(); },
     grin:()=>{ arcEye(94,106,true); arcEye(162,106,true); g.beginPath(); g.moveTo(84,140); g.quadraticCurveTo(128,205,172,140); g.closePath(); g.fill(); },
     chill:()=>{ g.beginPath(); g.moveTo(80,108); g.lineTo(112,108); g.moveTo(144,108); g.lineTo(176,108); g.stroke(); mouthSmile(26); },
     excited:()=>{ eye(96,104,17); eye(160,104,17); g.beginPath(); g.arc(128,138,36,0.05*Math.PI,0.95*Math.PI); g.closePath(); g.fill(); },
     bored:()=>{ g.beginPath(); g.moveTo(80,112); g.lineTo(112,112); g.moveTo(144,112); g.lineTo(176,112); g.stroke(); eye(96,120,8); eye(160,120,8); g.beginPath(); g.moveTo(104,160); g.lineTo(152,160); g.stroke(); },
     shock:()=>{ eye(96,104,16); eye(160,104,16); g.beginPath(); g.ellipse(128,160,16,22,0,0,7); g.fill(); },
     no:()=>{ arcEye(94,110,false); arcEye(162,110,false); g.beginPath(); g.moveTo(108,160); g.lineTo(148,160); g.stroke(); },
     chew:()=>{ arcEye(94,108,true); arcEye(162,108,true); g.beginPath(); g.ellipse(128,156,22,13,0,0,7); g.fill(); },
     sorry:()=>{ eye(96,112); eye(160,112); g.lineWidth=9; g.beginPath(); g.moveTo(76,84); g.lineTo(108,94); g.moveTo(180,84); g.lineTo(148,94); g.stroke(); g.lineWidth=13; g.beginPath(); g.moveTo(100,166); g.quadraticCurveTo(128,150,156,166); g.stroke(); },
     smug:()=>{ g.beginPath(); g.moveTo(80,108); g.lineTo(112,108); g.moveTo(144,108); g.lineTo(176,108); g.stroke(); g.beginPath(); g.moveTo(96,152); g.quadraticCurveTo(140,170,166,140); g.stroke(); },
  })[kind]();
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; return t; }
const FACES={}; for(const k of ['smile','grin','chill','excited','bored','shock','no','chew','sorry','smug']) FACES[k]=new THREE.MeshBasicMaterial({map:faceTex(k),transparent:true,depthWrite:false});
const faceGeo=new THREE.PlaneGeometry(0.235,0.235);

// ---------------------------------------------------------------- the four friends: own colour + own prop
const SKIN=new THREE.MeshStandardMaterial({color:0xf1e2cc,roughness:0.6,emissive:0xf1e2cc,emissiveIntensity:0.06});
const PROPM=c=>new THREE.MeshStandardMaterial({color:c,roughness:0.5});
const CHAIRP={...R.P0,p:0.07,tilt:0.0,aL:1.5,aR:1.47,kL:1.52,kR:1.47,sL:0.5,sR:0.5,eL:0.9,eR:0.9};
const STANDP={...R.P0,p:0.08};
const HIPBACK=0.276, FACE=V(0,0,1), YAW=yawOf(FACE);
const F={}; const COLORS={LATE:0x4f8fd6,PHOTO:0xe9b93a,HUNGRY:0xe9799f,PAYS:0x4fb37a};
for(const [id,x] of Object.entries(SEATX)){
  const fig=R.makeFig(COLORS[id],'f'+id,{rim:0.1,rimCol:0xfff1d8,lift:0.05}); fig.head.material=SKIN;
  const face=new THREE.Mesh(faceGeo,FACES.smile); face.renderOrder=4; S.scene.add(face);
  const prop=new THREE.Group(); S.scene.add(prop);
  if(id==='LATE'){ const band=new THREE.Mesh(new THREE.TorusGeometry(0.15,0.018,10,32,Math.PI),PROPM(0x222222)); prop.add(band);
    for(const s of [-1,1]){ const cup=new THREE.Mesh(new THREE.CylinderGeometry(0.055,0.055,0.04,20),PROPM(0x222222)); cup.rotation.z=Math.PI/2; cup.position.set(0.15*s,0,0); prop.add(cup); } }
  if(id==='PHOTO'){ const cap=new THREE.Mesh(new THREE.SphereGeometry(0.138,24,12,0,Math.PI*2,0,Math.PI/2),PROPM(0xc0392b)); prop.add(cap);
    const brim=new THREE.Mesh(new THREE.CylinderGeometry(0.11,0.11,0.012,24,1,false,-Math.PI/2,Math.PI),PROPM(0xc0392b)); brim.position.set(0,0.0,0.12); prop.add(brim); }
  if(id==='HUNGRY'){ const bun=new THREE.Mesh(new THREE.SphereGeometry(0.07,18,12),PROPM(0x3b2416)); bun.position.set(0,0.11,-0.08); prop.add(bun);
    const hair=new THREE.Mesh(new THREE.SphereGeometry(0.137,24,12,0,Math.PI*2,0,Math.PI*0.42),PROPM(0x3b2416)); hair.rotation.x=-0.35; prop.add(hair); }
  if(id==='PAYS'){ for(const s of [-1,1]){ const r=new THREE.Mesh(new THREE.TorusGeometry(0.038,0.008,8,24),PROPM(0x111111)); r.position.set(0.05*s,0.01,0.135); prop.add(r); }
    const br=new THREE.Mesh(new THREE.BoxGeometry(0.03,0.008,0.008),PROPM(0x111111)); br.position.set(0,0.015,0.138); prop.add(br); }
  F[id]={id,x,fig,face,prop,root:V(x,0,-0.62).addScaledVector(FACE,HIPBACK),ph:x*3};
}
const bump=(t,a,d)=>{ const x=(t-a)/d; return x<=0||x>=1?0:Math.sin(Math.PI*x)**2; };
const P_=(x,y,z)=>V(x,y,z);

// ---------------------------------------------------------------- shots
const SHOTS=TL.shots.map(([t0,name],i)=>({t0,t1:i+1<TL.shots.length?TL.shots[i+1][0]:DUR,name}));
const shotAt=t=>SHOTS.filter(s=>t>=s.t0).pop();

// ---------------------------------------------------------------- what everyone does at time t
function seated(f,t,{lean=0,look=0}={}){
  const P={...CHAIRP}; const talk=0.5+0.5*Math.sin(t*2.1+f.ph);
  P.p+=0.05*talk+lean; P.hy=look+0.12*Math.sin(t*0.9+f.ph); P.tilt+=0.04*Math.sin(t*2.6+f.ph);
  Object.assign(P,{tR:P_(f.x+0.1,TOP+0.04,-0.12),wR:1,pR:V(-0.3,-0.7,-0.7),tL:P_(f.x-0.1,TOP+0.04,-0.12),wL:1,pL:V(-0.3,-0.7,0.7)});
  return P; }
// head yaw to look at another seat (positive hy turns toward local -z; here local +x = world +z, local -z = world... use the sign that turns toward +x world)
const lookTo=(f,x)=>clamp((f.x-x)*1.2,-1.1,1.1);
const DOORX_=1.95;
function selfiePose(f,t,shot){
  // everyone squeezes toward the middle and leans into the lens; the photographer holds the phone out in front
  const P=seated(f,t,{lean:0.18,look:clamp(f.x*0.9,-0.5,0.5)}); P.tilt-=0.12;
  if(f.id==='PHOTO'){ P.tR=P_(0.0,1.62,0.45); P.pR=V(0.2,-0.6,-0.8); }
  else { const k=bump(t-shot.t0,0.0,0.9); P.tL=P_(f.x-0.05,1.15+0.35*k,-0.25); P.pL=V(0,-0.9,0.4); }   // peace-sign hand pops up
  return P; }

function poseAll(t){
  const sh=shotAt(t), out={};
  for(const f of Object.values(F)){
    let P=seated(f,t), root=f.root.clone(), face='smile', vis=true;
    const L=TL.late, Hh=TL.hungry, Py=TL.pays;
    if(sh.name==='selfie'||sh.name==='selfieEnd'){ P=selfiePose(f,t,sh); face=sh.name==='selfie'?'grin':'grin'; if(sh.name==='selfie'&&f.id==='LATE') vis=false; }
    if(sh.name==='late'){
      if(f.id==='LATE'){
        if(t<L.sit0){ const u=clamp((t-L.door)/(L.sit0-L.door)); const a=V(DOORX,0,-1.55), b=V(DOORX,0,-0.3), c=V(f.x+0.45,0,-0.3);
          const d1=a.distanceTo(b), d2=b.distanceTo(c), s=u*(d1+d2); root=s<d1?a.clone().lerp(b,s/d1):b.clone().lerp(c,(s-d1)/d2);
          out.walkYaw=s<d1?yawOf(V(0,0,1)):yawOf(V(-1,0,0));
          let Q=R.gait({...STANDP,p:0.05},s/1.3*Math.PI*2,1-sstep(L.sit0-0.2,L.sit0,t)); Q.wL=0; Q.wR=0;
          Q.tL=root.clone().add(V(-0.05,1.58,-0.13)); Q.wL=1; Q.pL=V(0,-1,0.2);          // phone at his ear, strolling
          P=Q; face='chill'; vis=t>L.door; }
        else { const s=sstep(L.sit0,L.sit1,t); const st=V(f.x+0.45,0,-0.25); root=st.lerp(f.root,s); P=R.blend({...STANDP},seated(f,t),s);
          const w=bump(t,L.wave,0.9); P.tL=P_(f.x-0.05,1.45+0.03*Math.sin(t*16),-0.2); P.wL=w; P.pL=V(0,-0.9,0.4); face=w>0.1?'sorry':'chill'; }
      } else { P=seated(f,t,{look:lookTo(f,2.0)*0.8}); face=t>L.door?'bored':'smile'; }
    }
    if(sh.name==='photo'){
      if(f.id==='PHOTO'){ P=seated(f,t,{lean:0.1}); P.tR=P_(f.x+0.32,1.68,0.1); P.pR=V(0.2,-0.6,-0.8); P.tilt-=0.15; face='excited';
        const om=bump(t,TL.oneMore,0.6); P.tL=P_(f.x-0.12,1.5,0.0); P.wL=om; P.pL=V(0,-0.9,0.4); }
      else { P=seated(f,t,{lean:0.3}); P.tilt+=0.35*sstep(4.6,5.4,t); face=t>4.9?'bored':'smile';
        if(f.id==='PAYS'){ P.tL=P_(f.x,1.3,-0.38); P.wL=sstep(5.2,5.6,t); }   // face-palm
      }
    }
    if(sh.name==='hungry'){
      if(f.id==='HUNGRY'){ P=seated(f,t); const no=sstep(Hh.no0,Hh.no0+0.15,t)*(1-sstep(Hh.no1-0.1,Hh.no1,t));
        P.hy=0.45*Math.sin((t-Hh.no0)*14)*no; P.tR=P.tR.clone().lerp(P_(f.x+0.05,1.15+0.04*Math.sin(t*18),0.2),no); face=no>0.2?'no':'smile';
        const targets=[SEATX.PHOTO,SEATX.LATE,SEATX.PAYS];
        Hh.grabs.forEach((g,i)=>{ const reach=bump(t,g-0.05,0.4), mouth=bump(t,g+Hh.toMouth-0.05,0.35);
          if(reach>0){ P.tR=P.tR.clone().lerp(P_(targets[i],TOP+0.05,0.04),Math.min(1,reach*1.5)); P.p+=0.25*reach; P.hy=lookTo(f,targets[i])*reach; }
          if(mouth>0){ P.tR=P.tR.clone().lerp(P_(f.x+0.02,1.26,-0.38),Math.min(1,mouth*1.6)); face='chew'; } });
        if(t>Hh.grabs[0]+0.2) face=face==='smile'?'chew':face;
      } else { P=seated(f,t,{look:lookTo(f,SEATX.HUNGRY)*sstep(Hh.grabs[0],Hh.grabs[0]+0.3,t)}); face=t>Hh.grabs[0]+0.1?'shock':'smile'; }
    }
    if(sh.name==='pays'){
      if(f.id==='PAYS'){ P=seated(f,t); const ph=sstep(Py.ring,Py.ring+0.25,t);
        P.tL=P.tL.clone().lerp(P_(f.x-0.13,1.36,-0.5),ph); P.pL=V(0,-1,0.2); face=t<Py.ring?'shock':'sorry';
        if(t>Py.stand0){ const s=sstep(Py.stand0,Py.stand1,t); const w=clamp((t-Py.stand1)/(Py.walk1-Py.stand1));
          const st=V(f.x,0,-0.2); root=f.root.clone().lerp(st,s).add(V(-1.8*w*w,0,0)); P=R.blend(P,{...STANDP,tL:root.clone().add(V(-0.13,1.58,0.05)),wL:1,pL:V(0,-1,0.2)},s);
          if(w>0){ P=R.gait({...STANDP,tL:root.clone().add(V(-0.05,1.58,-0.13)),wL:1,pL:V(0,-1,0.2)},w*1.8/1.3*Math.PI*2,1); out.paysYaw=yawOf(V(-1,0,0.15)); } face='smug'; }
      } else { const lb=sstep(Py.billLand,Py.billLand+0.25,t), lp=sstep(Py.stand0,Py.stand1,t);
        P=seated(f,t,{look:lerp(0,lookTo(f,SEATX.PAYS),lp)}); P.tilt+=0.3*lb*(1-lp); face=t>Py.stand0?'shock':(t>Py.billLand?'bored':'smile'); }
    }
    out[f.id]={P,root,face,vis};
  }
  return {sh,out};
}

// ---------------------------------------------------------------- cameras (one per shot, gentle drift inside each)
function camFor(sh,t){ const u=clamp((t-sh.t0)/(sh.t1-sh.t0));
  const C={ selfie:[V(-0.22,1.48,1.55),V(-0.22,1.22,-0.5),62], selfieEnd:[V(0.0,1.5,2.05),V(0,1.22,-0.5),70],
    late:[V(1.0,1.6,2.9),V(1.45,1.1,-0.6),46], photo:[V(-0.1,1.55,2.1),V(-0.05,1.35,-0.5),44],
    hungry:[V(0.25,1.75,1.45),V(0.22,0.95,-0.3),44], pays:[V(-0.9,1.5,2.4),V(-0.85,1.1,-0.4),46] }[sh.name];
  const pos=C[0].clone(), tg=C[1].clone(); let fov=C[2];
  if(sh.name.startsWith('selfie')){ pos.add(V(0.02*Math.sin(t*3.1),0.015*Math.sin(t*2.3),-0.12*u)); fov-=4*u; }   // handheld, a tiny push
  else pos.addScaledVector(tg.clone().sub(pos).normalize(),0.35*sm5(u));                                      // slow push in
  if(sh.name==='pays'){ const w=sstep(TL.pays.stand1,TL.pays.walk1,t); pos.x-=0.9*w; tg.x-=0.9*w; }                 // pan with him as he walks out
  return {pos,tg,fov}; }

// ---------------------------------------------------------------- one frame
function setT(t){
  const {sh,out}=poseAll(t);
  const c=camFor(sh,t); S.cam.fov=c.fov; S.cam.updateProjectionMatrix(); S.cam.position.copy(c.pos); S.cam.lookAt(c.tg);
  for(const f of Object.values(F)){ const o=out[f.id]; let yaw=YAW; if(f.id==='LATE'&&out.walkYaw!==undefined) yaw=out.walkYaw; if(f.id==='PAYS'&&out.paysYaw!==undefined) yaw=out.paysYaw;
    f.fig.setAlpha(o.vis?1:0); f.face.visible=o.vis; f.prop.visible=o.vis; if(!o.vis) continue;
    R.poseFig(f.fig,R.skel(o.P,o.root,yaw));
    const P=o.P, hd=P.p+P.tilt, fl=SLD.rotY(SLD.rotY(V(Math.cos(hd),-Math.sin(hd),0),P.hy),P.ty), ul=SLD.rotY(SLD.rotY(V(Math.sin(hd),Math.cos(hd),0),P.hy),P.ty);
    const h=f.fig.head.position, fw=SLD.rotY(fl,yaw).normalize(), uw=SLD.rotY(ul,yaw).normalize();
    f.face.position.copy(h).addScaledVector(fw,0.132); f.face.up.copy(uw); f.face.lookAt(h.clone().addScaledVector(fw,1)); f.face.material=FACES[o.face];
    f.prop.position.copy(h); f.prop.up.copy(uw); f.prop.lookAt(h.clone().addScaledVector(fw,1)); }
  // phones
  const hand=(id,side)=>F[id].fig.joints[side==='R'?11:10].position;
  PHONES.PHOTO.visible=true; PHONES.PHOTO.position.copy(hand('PHOTO','R')).add(V(0,0.13,0.02)); PHONES.PHOTO.lookAt(S.cam.position.clone().setY(PHONES.PHOTO.position.y)); PHONES.PHOTO.rotateY(Math.PI);
  PHONES.LATE.visible=sh.name==='late'&&t<TL.late.sit0+0.2&&out.LATE.vis; PHONES.LATE.position.copy(hand('LATE','L')); PHONES.LATE.rotation.set(0,Math.PI/2,0);
  PHONES.PAYS.visible=sh.name==='pays'&&t>TL.pays.ring; PHONES.PAYS.position.copy(hand('PAYS','L')); PHONES.PAYS.rotation.set(0,-Math.PI/2,0);
  // flashes: the selfie flashes and the photographer's burst
  let fl=0; for(const ft of [TL.flash0,TL.flashEnd,...TL.photoFlashes]) if(t>=ft) fl=Math.max(fl,Math.exp(-(t-ft)*16));
  flash.position.copy(PHONES.PHOTO.position); flash.scale.setScalar(0.5); flash.material.opacity=0.85*fl; flashL.position.copy(PHONES.PHOTO.position); flashL.intensity=2.2*fl;
  // the door swings open for the late one
  const dk=sstep(TL.late.door-0.1,TL.late.door+0.25,t)*(1-sstep(TL.late.door+0.9,TL.late.door+1.4,t)); doorPivot.rotation.y=1.3*dk;   // swings in, away from the camera
  // fries vanish as she eats them; the stolen fry rides in her hand
  const eaten=TL.hungry.grabs.filter(g=>t>g+0.1).length; ['PHOTO','LATE','PAYS'].forEach((id,i)=>{ FRIES[id].forEach((fr,k)=>{ fr.visible=!(i<eaten&&k<3); }); });
  const carrying=TL.hungry.grabs.some(g=>t>g+0.05&&t<g+TL.hungry.toMouth+0.15)&&sh.name==='hungry';
  heldFry.visible=carrying; heldFry.position.copy(hand('HUNGRY','R')).add(V(0,0.03,0.02)); heldFry.rotation.set(0.9,0.3,0);
  // the bill drops onto the table in the middle
  const b=sstep(TL.pays.billLand-0.25,TL.pays.billLand,t); bill.visible=t>TL.pays.billLand-0.25&&sh.name==='pays';
  bill.position.set(lerp(-0.2,-0.42,b),TOP+0.008+0.5*(1-b),lerp(0.6,0.12,b)); bill.rotation.set(0,0.3,0);
  S.tick(t,0);
}

// ---------------------------------------------------------------- overlay / sound data
const v3=new THREE.Vector3();
const NUM={LATE:1,PHOTO:2,HUNGRY:3,PAYS:4};
window.metaAt=t=>{ setT(t); S.cam.updateMatrixWorld(); const sh=shotAt(t); const heads={};
  for(const f of Object.values(F)){ const h=f.fig.head.position; v3.copy(h).project(S.cam); const x=(v3.x*0.5+0.5)*1080, y=(0.5-v3.y*0.5)*1920;
    const e=h.clone().add(V(0.13,0,0)).project(S.cam); const r=Math.abs((e.x*0.5+0.5)*1080-x);   // head radius on screen
    heads[f.id]={n:NUM[f.id],x,y,r,on:f.fig.head.visible&&v3.z<1}; }
  return {shot:sh.name,heads}; };
window.events={...TL};
window.renderAt=(t,K=3)=>{ const sh=shotAt(t); return S.renderAt(setT,t,K,{t0:sh.t0,t1:sh.t1}); };   // never blur across a cut
window.ready=true;
