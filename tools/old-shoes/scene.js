// The Old Shoes: Slow Light story lane, Story 1. Look test = the cold-open hook shot (0-3 s):
// dad walks to the door in his patched shoes, the loose sole flaps and slaps, the gift box sits closed on the rack.
// Units metres, floor y=0, back wall face z=0, camera on +z, dad walks toward +x (the door).
import * as THREE from 'three';
import * as SLD from './sld.js';
const {V,clamp,sstep,lerp,keys,rng,noiseTex,rimify,dustify,dustU,PAL}=SLD;
const Q=new URLSearchParams(location.search);
const W=+Q.get('w')||1080, H=+Q.get('h')||1920, SHOT=Q.get('shot')||'hook';
const DUR=4.0;
const LAMP=V(-0.1,3.4,1.0);
const S=SLD.createStage({W,H,lamp:LAMP,lampTarget:V(-0.05,0,0.75),cone:0.34,spot:40,beam:0,fov:44,bg:0x15110f,fog:0.05,vig:0.28,hemi:0.6,hemiSky:0x4a4a5a,motes:1500,floorCol:0x6a4a34});
const {scene,cam}=S;
S.renderer.toneMappingExposure=0.95; S.bloom.strength=0.28; S.bloom.threshold=0.9;
const canvasTex=(w,h,draw,srgb=true)=>{ const c=document.createElement('canvas'); c.width=w; c.height=h; draw(c.getContext('2d'),w,h); const t=new THREE.CanvasTexture(c); if(srgb) t.colorSpace=THREE.SRGBColorSpace; t.anisotropy=8; return t; };
const std=(color,o={})=>new THREE.MeshStandardMaterial({color,roughness:o.r??0.8,metalness:o.m??0,...o.x});
const box=(w,h,d,mat,x,y,z,parent=scene,cast=true)=>{ const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat); m.position.set(x,y,z); m.castShadow=cast; m.receiveShadow=true; parent.add(m); return m; };
const boxE=(x0,x1,y0,y1,z0,z1,mat,parent=scene,cast=true)=>box(x1-x0,y1-y0,z1-z0,mat,(x0+x1)/2,(y0+y1)/2,(z0+z1)/2,parent,cast);

// ------------------------------------------------------------------ floor: worn red-oxide floor (common in old Indian homes)
const floorTex=canvasTex(1024,1024,(g,w,h)=>{ const R=rng(4); g.fillStyle='#7a3a2a'; g.fillRect(0,0,w,h);
  for(let i=0;i<900;i++){ g.fillStyle=`rgba(${R()<0.5?30:160},${R()<0.5?14:80},${R()<0.5?10:60},${0.03+R()*0.05})`; g.beginPath(); g.ellipse(R()*w,R()*h,10+R()*60,6+R()*30,R()*3,0,7); g.fill(); }
  g.fillStyle='rgba(25,10,6,0.55)'; for(let k=0;k<=4;k++){ g.fillRect(0,k*256-1,w,3); g.fillRect(k*256-1,0,3,h); } });
floorTex.wrapS=floorTex.wrapT=THREE.RepeatWrapping; floorTex.repeat.set(15,15);
S.floor.material.map=floorTex; S.floor.material.color.set(0xd8b0a0); S.floor.material.roughness=0.38; S.floor.material.opacity=0.985; S.floor.material.needsUpdate=true;

// ------------------------------------------------------------------ back wall (faded teal lime-wash), skirting, the open front door on the right
const DOOR={x0:1.05,x1:1.95,y1:2.1};
const wallTex=canvasTex(512,512,(g,w,h)=>{ const R=rng(3); g.fillStyle='#808080'; g.fillRect(0,0,w,h);
  for(let i=0;i<500;i++){ g.fillStyle=`rgba(${R()<0.5?0:255},${R()<0.5?0:255},${R()<0.5?0:255},${0.02+R()*0.04})`; g.beginPath(); g.ellipse(R()*w,R()*h,8+R()*50,8+R()*40,0,0,7); g.fill(); }
  for(let i=0;i<25;i++){ g.strokeStyle='rgba(40,40,40,0.18)'; g.lineWidth=1; g.beginPath(); let x=R()*w,y=R()*h; g.moveTo(x,y); for(let k=0;k<6;k++){ x+=(R()-0.5)*30; y+=R()*20; g.lineTo(x,y);} g.stroke(); } },false);
wallTex.wrapS=wallTex.wrapT=THREE.RepeatWrapping; wallTex.repeat.set(4,3);
const wallMat=new THREE.MeshStandardMaterial({color:0x4f7a74,roughness:0.95,map:wallTex});
[[-4,DOOR.x0,0,3.4],[DOOR.x1,4.5,0,3.4],[DOOR.x0,DOOR.x1,DOOR.y1,3.4]].forEach(([a,b,c,d])=>boxE(a,b,c,d,-0.16,0,wallMat));
const skirt=std(0x2f4a46,{r:0.6}); boxE(-4,DOOR.x0-0.07,0,0.1,0,0.02,skirt); boxE(DOOR.x1+0.07,4.5,0,0.1,0,0.02,skirt);
const trimMat=std(0x6b4a30,{r:0.55});
{ const t=0.07; boxE(DOOR.x0-t,DOOR.x0,0,DOOR.y1+t,0,0.04,trimMat); boxE(DOOR.x1,DOOR.x1+t,0,DOOR.y1+t,0,0.04,trimMat); boxE(DOOR.x0-t,DOOR.x1+t,DOOR.y1,DOOR.y1+t,0,0.04,trimMat);
  boxE(DOOR.x0,DOOR.x1,0,0.035,-0.16,0.05,std(0x5a3a26,{r:0.5})); }   // threshold step
// outside: bright morning (lane wall + sky), emissive so it reads as daylight
{ const tex=canvasTex(256,512,(g,w,h)=>{ const gr=g.createLinearGradient(0,0,0,h); gr.addColorStop(0,'#fff4dc'); gr.addColorStop(0.55,'#ffe2b0'); gr.addColorStop(0.56,'#d8b890'); gr.addColorStop(1,'#b89070'); g.fillStyle=gr; g.fillRect(0,0,w,h); });
  const m=new THREE.Mesh(new THREE.PlaneGeometry(3,3.2),new THREE.MeshBasicMaterial({map:tex,fog:false,color:0xffffff})); m.position.set(1.5,1.2,-1.4); scene.add(m); }
// the open door leaf, swung inward against the right wall
{ const piv=new THREE.Group(); piv.position.set(DOOR.x1-0.01,0,0.02); piv.rotation.y=-1.75; scene.add(piv);
  const woodTex=noiseTex(256,9,128,60,30,0.1); woodTex.repeat.set(2,2); const dm=new THREE.MeshStandardMaterial({color:0x5a3826,roughness:0.6,map:woodTex});
  box(0.88,2.06,0.045,dm,-0.44,1.04,0,piv); for(const [y0,y1] of [[0.2,0.95],[1.12,1.9]]) box(0.68,y1-y0,0.02,std(0x6a4632,{r:0.5}),-0.44,(y0+y1)/2,0.03,piv); }
// daylight pouring in through the door: long warm shadows across the floor toward camera-left
const sun=new THREE.SpotLight(0xffe6c0,30,0,0.5,0.35,0.4); sun.position.set(2.9,1.9,-1.6); sun.target.position.set(-0.4,0,1.2);
sun.castShadow=true; sun.shadow.mapSize.set(2048,2048); sun.shadow.bias=-0.0004; sun.shadow.normalBias=0.02; sun.shadow.camera.near=0.5; sun.shadow.camera.far=9; scene.add(sun,sun.target);
const wallWash=new THREE.SpotLight(0xffe2c0,2.2,0,0.9,0.9,0); wallWash.position.set(0,1.0,3.2); wallWash.target.position.set(-0.3,1.0,0); scene.add(wallWash,wallWash.target);
const fill=new THREE.DirectionalLight(0xc0c8e0,0.45); fill.position.set(-1,1.5,5); fill.target.position.set(0,0.3,0.6); scene.add(fill,fill.target);
const kick=new THREE.SpotLight(0xffd9a8,6,0,0.6,0.8,0.5); kick.position.set(-1.2,0.6,2.4); kick.target.position.set(0,0.12,0.8); scene.add(kick,kick.target);   // low warm kick on the shoes

// ------------------------------------------------------------------ the shoe rack by the wall, and the gift box on it (closed, dusty)
const RACK={x0:0.05,x1:0.75,h:0.46,d:0.3};
{ const wt=noiseTex(256,12,128,50,20,0.12); wt.repeat.set(2,1); const wm=new THREE.MeshStandardMaterial({color:0x6a4630,roughness:0.6,map:wt});
  const {x0,x1,h,d}=RACK; boxE(x0,x0+0.025,0,h,0.01,d,wm); boxE(x1-0.025,x1,0,h,0.01,d,wm); boxE(x0,x1,h-0.025,h,0.01,d,wm); boxE(x0,x1,0.2,0.222,0.01,d,wm); boxE(x0,x1,0.0,0.04,0.01,d,wm);
  boxE(x0,x1,0.04,h-0.025,0.0,0.009,std(0x2a1c14,{r:0.9})).receiveShadow=false; }
const BOX={x:0.27,y:RACK.h,z:0.15,w:0.38,h:0.15,d:0.24};
const wrapTex=canvasTex(512,256,(g,w,h)=>{ g.fillStyle='#b8862e'; g.fillRect(0,0,w,h); const R=rng(6);
  for(let i=0;i<60;i++){ g.fillStyle=`rgba(255,226,150,${0.35+R()*0.2})`; const x=R()*w,y=R()*h; g.beginPath(); for(let k=0;k<5;k++){ const a=k/5*6.283-1.57, b=a+0.63; g.lineTo(x+Math.cos(a)*9,y+Math.sin(a)*9); g.lineTo(x+Math.cos(b)*4,y+Math.sin(b)*4);} g.fill(); } });
const giftMat=dustify(new THREE.MeshStandardMaterial({color:0xffffff,map:wrapTex,roughness:0.55,emissive:0x2a2010,emissiveIntensity:0.1}),'gift');
const ribMat=new THREE.MeshStandardMaterial({color:PAL.RED,roughness:0.35,emissive:PAL.RED,emissiveIntensity:0.18});
const gift=new THREE.Group(); gift.position.set(BOX.x,BOX.y,BOX.z); gift.rotation.y=-0.1; scene.add(gift);
{ const b=box(BOX.w,BOX.h,BOX.d,giftMat,0,BOX.h/2,0,gift); const lid=box(BOX.w+0.012,0.035,BOX.d+0.012,giftMat,0,BOX.h-0.012,0,gift);
  box(0.05,BOX.h+0.006,BOX.d+0.018,ribMat,0.04,BOX.h/2,0,gift); box(BOX.w+0.018,BOX.h+0.006,0.05,ribMat,0,BOX.h/2,0,gift);
  for(const s of [-1,1]){ const loop=new THREE.Mesh(new THREE.TorusGeometry(0.06,0.015,10,24),ribMat); loop.scale.set(1,0.55,1); loop.position.set(0.04+s*0.045,BOX.h+0.03,0); loop.rotation.set(Math.PI/2*0.25,0,s*0.35); loop.castShadow=true; gift.add(loop);
    const tail=box(0.03,0.006,0.09,ribMat,0.04+s*0.03,BOX.h+0.008,s*0.05,gift); tail.rotation.y=s*0.5; }
  const knot=new THREE.Mesh(new THREE.SphereGeometry(0.018,12,8),ribMat); knot.position.set(0.04,BOX.h+0.022,0); gift.add(knot); }
dustU.uDust.value=0.42;
const ribGlow=SLD.glowSprite(scene,PAL.RED,0.16); ribGlow.position.set(BOX.x+0.04,BOX.y+BOX.h+0.03,BOX.z+0.05); ribGlow.scale.setScalar(0.35);

// ------------------------------------------------------------------ dad
const R=SLD.createRig(scene);
const dad=R.makeFig(0xd8d0c0,'dad',{rim:0.1,lift:0.02});
// hide the foot balls: the shoes carry the ankle
dad.joints[4].visible=false; dad.joints[5].visible=false;

// ------------------------------------------------------------------ the shoes: worn leather upper, split sole flap, cardboard insole, silver tape across the toe
const SH={L:0.2,Wd:0.085,Ht:0.1,Sole:0.034,ank:-0.08};   // half-length, half-width, upper height, sole thickness, ankle x in shoe
const leatherTex=canvasTex(512,256,(g,w,h)=>{ const R=rng(31); g.fillStyle='#4a2e1e'; g.fillRect(0,0,w,h);
  for(let i=0;i<500;i++){ g.fillStyle=`rgba(${R()<0.6?20:150},${R()<0.6?10:110},${R()<0.6?6:80},${0.05+R()*0.12})`; g.beginPath(); g.ellipse(R()*w,R()*h,3+R()*26,2+R()*8,R()*3,0,7); g.fill(); }
  g.strokeStyle='rgba(205,170,130,0.16)'; g.lineWidth=2; for(let i=0;i<22;i++){ g.beginPath(); const x=R()*w, y=h*0.3+R()*h*0.6; g.moveTo(x,y); g.quadraticCurveTo(x+10,y-6+R()*12,x+16+R()*30,y+(R()-0.5)*10); g.stroke(); }   // scuffs, creases
  g.strokeStyle='rgba(20,12,8,0.8)'; g.setLineDash([6,5]); g.lineWidth=2; g.beginPath(); g.moveTo(0,h*0.92); g.lineTo(w,h*0.92); g.stroke(); });       // welt stitches
const cardTex=canvasTex(256,64,(g,w,h)=>{ g.fillStyle='#c99a5e'; g.fillRect(0,0,w,h); for(let x=0;x<w;x+=7){ g.fillStyle='rgba(90,60,30,0.45)'; g.fillRect(x,0,2,h);} g.fillStyle='rgba(255,230,190,0.25)'; g.fillRect(0,0,w,4); });
cardTex.wrapS=cardTex.wrapT=THREE.RepeatWrapping;
const tapeTex=canvasTex(128,64,(g,w,h)=>{ const R=rng(77); g.fillStyle='#b9bcbf'; g.fillRect(0,0,w,h); for(let i=0;i<300;i++){ g.fillStyle=`rgba(${R()<0.5?60:255},${R()<0.5?60:255},${R()<0.5?60:255},0.12)`; g.fillRect(R()*w,R()*h,1+R()*5,1); } g.fillStyle='rgba(40,40,40,0.25)'; for(let x=0;x<w;x+=4) g.fillRect(x,0,1,h); });
function footprint(x0,x1,n=24){ const pts=[]; const wAt=x=>{ const u=x/SH.L; return SH.Wd*1.04*Math.sqrt(Math.max(0,1-Math.pow(Math.abs(u),2.4)))*(x<0?0.92:1); };
  for(let i=0;i<=n;i++){ const x=lerp(x0,x1,i/n); pts.push(new THREE.Vector2(x,wAt(x))); } for(let i=n;i>=0;i--){ const x=lerp(x0,x1,i/n); pts.push(new THREE.Vector2(x,-wAt(x))); } return new THREE.Shape(pts); }
function shoeGeo(geo,k=1){ geo.scale(SH.Ht*k,SH.L*(k>1?1.012:1),SH.Wd*k); geo.rotateZ(-Math.PI/2); const p=geo.attributes.position;
  for(let i=0;i<p.count;i++){ const x=p.getX(i), y=p.getY(i); const u=x/SH.L; const prof=lerp(1.0,0.42,sstep(-0.25,0.95,u)); p.setY(i,y*prof*(1+0.12*sstep(-1,-0.6,u))); }
  geo.computeVertexNormals(); return geo; }
function makeShoe(key,patched){
  const g=new THREE.Group(); const piv=new THREE.Group(); g.add(piv);   // g at the ankle, piv offsets so the ankle sits over the heel
  piv.position.set(-SH.ank,-0.005,0);
  const lm=rimify(new THREE.MeshStandardMaterial({map:leatherTex,roughness:0.68,color:0xffffff,side:THREE.DoubleSide,emissive:0x1a0e08,emissiveIntensity:0.5}),0xffd9a8,0.22,'leather'+key);
  const up=new THREE.Mesh(shoeGeo(new THREE.SphereGeometry(1,48,28,-Math.PI/2,Math.PI,0,Math.PI)),lm); up.castShadow=true; up.receiveShadow=true; piv.add(up);
  const hole=new THREE.Mesh(new THREE.CircleGeometry(1,28),std(0x120a06,{r:1})); hole.rotation.x=-Math.PI/2; hole.scale.set(0.072,0.06,1); hole.position.set(SH.ank+0.005,SH.Ht*0.97,0); piv.add(hole);
  const collar=new THREE.Mesh(new THREE.TorusGeometry(1,0.12,8,32),std(0x3a2416,{r:0.5})); collar.rotation.x=-Math.PI/2; collar.scale.set(0.072,0.06,0.06); collar.position.copy(hole.position); collar.visible=false; piv.add(collar);
  // laces: three cream crossings over the instep
  const laceM=std(0xd8ccb0,{r:0.7}); for(let k=0;k<3;k++){ const l=box(0.012,0.008,SH.Wd*1.0,laceM,0.0+k*0.03,SH.Ht*(0.86-k*0.1),0,piv,false); l.rotation.z=-0.45-k*0.05; }
  const soleM=std(0x1b1410,{r:0.85}); const ext=(x0,x1)=>{ const geo=new THREE.ExtrudeGeometry(footprint(x0,x1),{depth:SH.Sole,bevelEnabled:true,bevelThickness:0.004,bevelSize:0.004,bevelSegments:2}); geo.rotateX(-Math.PI/2); return geo; };
  const cardM=new THREE.MeshStandardMaterial({map:cardTex,roughness:0.9,emissive:0x6a4420,emissiveIntensity:0.6});
  const HINGE=0.0;
  const heel=new THREE.Mesh(ext(-SH.L,HINGE),soleM); heel.position.y=-SH.Sole; heel.castShadow=true; heel.receiveShadow=true; piv.add(heel);
  const flapP=new THREE.Group(); flapP.position.set(HINGE,0,0); piv.add(flapP);   // the loose front half of the sole, hinged at the ball of the foot (top edge)
  const flap=new THREE.Mesh(ext(-0.0005,SH.L),[cardM,soleM]); flap.position.set(-HINGE,-SH.Sole,0); flap.castShadow=true; flap.receiveShadow=true; flapP.add(flap);
  // cardboard insole: the front piece rides with the upper, its ragged edge sticks out past the leather
  if(patched){ const cg=new THREE.ExtrudeGeometry(footprint(HINGE-0.01,SH.L*0.99),{depth:0.012,bevelEnabled:false}); cg.rotateX(-Math.PI/2);
    const cm=new THREE.MeshStandardMaterial({map:cardTex,roughness:0.9,emissive:0x3a2410,emissiveIntensity:0.5}); const cb=new THREE.Mesh(cg,cm); cb.scale.set(1.03,1,1.1); cb.position.y=-0.012; cb.castShadow=true; piv.add(cb);
    const tm=new THREE.MeshStandardMaterial({map:tapeTex,roughness:0.35,metalness:0.35,color:0xffffff,emissive:0x202020});
    const tape=new THREE.Mesh(shoeGeo(new THREE.SphereGeometry(1,48,6,-Math.PI/2,Math.PI,0.42,0.3),1.04),tm); tape.castShadow=true; piv.add(tape); }
  scene.add(g); return {g,flapP};
}
const shoeL=makeShoe('L',true), shoeR=makeShoe('R',true);

// ------------------------------------------------------------------ the walk: planted feet (no sliding in a close-up), 2-bone leg IK
const STEP=0.3, TS=0.85, X0=-0.4, HIPY=0.86, ZW=0.66;
// step k (k>=0) runs over [k*TS, (k+1)*TS); odd steps move the right foot, even the left. Feet start mid-stride so frame 0 already has a foot in the air.
const T0=-0.41;   // time offset: frame 0 sits late in the left foot's swing, sole hanging open; it slaps down at ~0.19 s
function footAt(side,t){   // returns {x,lift,u(swing 0..1 or -1),pitch}
  const tt=t-T0; const k=Math.floor(tt/TS); const ph=tt/TS-k; const mine=(k%2===0)===(side==='L');
  const land=j=>X0+(side==='L'?0:STEP)+j*2*STEP;   // landing x of this foot's j-th placement
  const s=side==='L'?0:1, SW=0.82;   // SW: swing fraction of the step (rest is double support)
  const jPrev=mine?(k-s)/2:Math.floor((k-s-1)/2)+1;   // mine: swinging from placement jPrev; not mine: standing on placement jPrev
  if(!mine) return {x:land(jPrev),lift:0,u:-1,pitch:0};
  if(ph>SW) return {x:land(jPrev+1),lift:0,u:-1,pitch:0};
  const u=ph/SW; const x0=land(jPrev), x1=land(jPrev+1); const ue=SLD.ease(u);
  return {x:lerp(x0,x1,ue),lift:0.12*Math.sin(Math.PI*u)+0.02*Math.sin(Math.PI*Math.min(1,u*2)),u,pitch:0.38*Math.sin(Math.PI*Math.min(1,u*1.6))*(1-sstep(0.55,0.75,u))-0.16*sstep(0.6,0.85,u)*(1-sstep(0.9,1,u))};
}
function flapAt(f,t){   // sole flap angle (rad): hangs open while the foot is up, slaps shut on landing, small after-wobble
  if(f.u<0){ return 0; }
  const u=f.u; let a=0.8*sstep(0.04,0.3,u)*(1-sstep(0.84,0.97,u)); a+=0.07*Math.sin(u*22)*sstep(0.1,0.3,u)*(1-sstep(0.7,0.9,u)); return Math.max(0,a);
}
function hipX(t){ return X0+STEP*0.5+(t-T0)*STEP/TS - STEP*0.5; }
function legIK(dx,dy){ const T=R.L.thigh, Sh=R.L.shin; const d=Math.min(Math.hypot(dx,dy),T+Sh-0.002);
  const k=Math.PI-Math.acos(clamp((T*T+Sh*Sh-d*d)/(2*T*Sh),-1,1)); const al=Math.acos(clamp((T*T+d*d-Sh*Sh)/(2*T*d),-1,1)); return {a:Math.atan2(dx,-dy)+al,k}; }
function placeShoe(sh,f,ank,t){ sh.g.position.copy(ank); sh.g.rotation.set(0,0,-f.pitch); const hb=Math.max(0,ank.y-0.04); sh.flapP.rotation.z=-Math.min(flapAt(f,t),Math.atan2(hb,SH.L)+f.pitch*0.0); }
const events=[];   // sole slaps (for the sound mix)
for(let k=0;k<12;k++){ const tl=T0+k*TS+0.82*TS*0.97; if(tl>0&&tl<DUR) events.push({t:+tl.toFixed(3),type:'slap',side:k%2===0?'L':'R'}); }

function poseDad(t){
  const hx=hipX(t)+0.03*Math.sin((t-T0)/TS*Math.PI*2), hy=HIPY-0.018*Math.cos((t-T0)/TS*Math.PI*2);
  const fL=footAt('L',t), fR=footAt('R',t);
  const aL=V(fL.x,0.035+fL.lift,ZW+0.08), aR=V(fR.x,0.035+fR.lift,ZW-0.08);
  const iL=legIK(aL.x-hx,aL.y-hy), iR=legIK(aR.x-hx,aR.y-hy);
  const sw=Math.sin((t-T0)/TS*Math.PI);
  const P={...R.P0,p:0.16,tilt:0.12,aL:iL.a,kL:iL.k,aR:iR.a,kR:iR.k,sL:0.08-0.22*sw,sR:-0.04+0.22*sw,eL:0.3,eR:0.3};
  // cancel skel()'s automatic hip placement so the IK targets land exactly
  const fl=[Math.sin(P.aL)*R.L.thigh+Math.sin(P.aL-P.kL)*R.L.shin,-Math.cos(P.aL)*R.L.thigh-Math.cos(P.aL-P.kL)*R.L.shin];
  const fr=[Math.sin(P.aR)*R.L.thigh+Math.sin(P.aR-P.kR)*R.L.shin,-Math.cos(P.aR)*R.L.thigh-Math.cos(P.aR-P.kR)*R.L.shin];
  P.fx=(fl[0]+fr[0])*0.5*0.6; P.dy=hy+Math.min(fl[1],fr[1])-0.035;
  const J=R.skel(P,V(hx,0,ZW),0); R.poseFig(dad,J);
  placeShoe(shoeL,fL,J.fL,t); placeShoe(shoeR,fR,J.fR,t);
  return {hx,fL,fR,J};
}

// ------------------------------------------------------------------ camera: low, tight on the feet, tracking with a slight lag; slow push
const CXO=+(Q.get('cxo')??0.03);
function setT(t){
  const d=poseDad(t);
  // locked-off camera (a tracking camera made the walk read as a treadmill): he walks through the frame, past the box, toward the door
  const cx=CXO+0.03*t;
  const z=keys([[0,2.05],[3.0,1.9]],t);
  cam.position.set(cx,0.42,ZW+z); cam.lookAt(cx,0.5,ZW-0.25);
  cam.fov=50; cam.updateProjectionMatrix();
  S.tick(t);
}
setT(0);
window.metaAt=t=>{ const d=poseDad(t); return {hx:d.hx}; };
window.events=events;
window.renderAt=(t,K)=>S.renderAt(setT,t,K,{t0:0,t1:DUR});
S.renderAt(setT,0.5,1,{t0:0,t1:DUR}); S.renderAt(setT,0,1,{t0:0,t1:DUR});   // warm-up: upload canvas textures before the first real frame
window.ready=true;
