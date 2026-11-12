// The Old Shoes: Slow Light story lane, Story 1. Look test = the cold-open hook shot (0-3 s):
// dad walks to the door in his patched shoes, the loose sole flaps and slaps, the gift box sits closed on the rack.
// Units metres, floor y=0, back wall face z=0, camera on +z, dad walks toward +x (the door).
import * as THREE from 'three';
import * as SLD from './sld.js';
const {V,clamp,sstep,lerp,keys,rng,noiseTex,rimify,dustify,dustU,PAL}=SLD;
const Q=new URLSearchParams(location.search);
const W=+Q.get('w')||1080, H=+Q.get('h')||1920, SHOT=Q.get('shot')||'hook';
const DUR=28.0;
const LAMP=V(-0.1,3.4,1.0);
const S=SLD.createStage({W,H,lamp:LAMP,lampTarget:V(-0.05,0,0.75),cone:0.34,spot:40,beam:0,fov:44,bg:0x15110f,fog:0.05,vig:0.28,hemi:0.6,hemiSky:0x4a4a5a,motes:1500,floorCol:0x6a4a34});
const {scene,cam}=S;
const STAGE_KIDS=new Set(scene.children);
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

const cardTex=canvasTex(256,64,(g,w,h)=>{ g.fillStyle='#c99a5e'; g.fillRect(0,0,w,h); for(let x=0;x<w;x+=7){ g.fillStyle='rgba(90,60,30,0.45)'; g.fillRect(x,0,2,h);} g.fillStyle='rgba(255,230,190,0.25)'; g.fillRect(0,0,w,4); });
cardTex.wrapS=cardTex.wrapT=THREE.RepeatWrapping;
// everything built so far (minus the SLD stage and the lights) is the home set
const HOME=scene.children.filter(o=>!STAGE_KIDS.has(o)&&!o.isLight&&o!==ribGlow&&o!==gift&&!(o.type==='Object3D'));

// ================================================================== the market set (shot B): ochre street wall, shutters, a shoe stall
const MARKET=new THREE.Group(); scene.add(MARKET);
{ const mw=new THREE.MeshStandardMaterial({color:0x9a6a38,roughness:0.95,map:wallTex}); boxE(-4,4.5,0,3.4,-0.16,0,mw,MARKET);
  const shT=canvasTex(256,512,(g,w,h)=>{ g.fillStyle='#5f7a8c'; g.fillRect(0,0,w,h); for(let y=0;y<h;y+=10){ g.fillStyle='rgba(20,30,40,0.35)'; g.fillRect(0,y,w,3); g.fillStyle='rgba(255,255,255,0.08)'; g.fillRect(0,y+4,w,2);} const R=rng(5); for(let i=0;i<40;i++){ g.fillStyle=`rgba(120,60,30,${R()*0.25})`; g.beginPath(); g.ellipse(R()*w,R()*h,4+R()*20,3+R()*10,0,0,7); g.fill(); } });
  for(const [x0,x1] of [[-1.9,-0.7],[1.5,2.7]]) boxE(x0,x1,0,2.25,0,0.03,new THREE.MeshStandardMaterial({map:shT,roughness:0.6,metalness:0.2}),MARKET);
  const wt=noiseTex(256,14,128,50,20,0.12); wt.repeat.set(2,1); const wood=new THREE.MeshStandardMaterial({color:0x8a5a34,roughness:0.6,map:wt});
  boxE(0.25,1.05,0,0.74,0.3,0.75,wood,MARKET); boxE(0.2,1.1,0.74,0.78,0.27,0.78,std(0x6a4026,{r:0.5}),MARKET);
  // wall shelves of shoe boxes behind the seller
  const R=rng(9); const cols=[0xd8452e,0x2f6db0,0xe8b85a,0xefe6d6,0x3a8a5a,0xb04a7a];
  boxE(0.2,1.4,0.86,0.89,0.02,0.34,wood,MARKET); boxE(0.2,1.4,1.3,1.33,0.02,0.34,wood,MARKET); boxE(0.2,1.4,1.74,1.77,0.02,0.34,wood,MARKET);
  for(const y of [0.89,1.33,1.77]) for(let x=0.24;x<1.32;x+=0.2) box(0.18,0.11,0.28,std(cols[Math.floor(R()*cols.length)],{r:0.6}),x+0.08,y+0.055,0.18,MARKET);
  for(const y of [0.89,1.33]) for(let x=0.24;x<1.32;x+=0.2) box(0.18,0.11,0.28,std(cols[Math.floor(R()*cols.length)],{r:0.6}),x+0.08,y+0.165,0.18,MARKET);
  // striped awning
  const awT=canvasTex(512,64,(g,w,h)=>{ for(let x=0;x<w;x+=64){ g.fillStyle=(x/64)%2?'#efe6d6':'#c8382e'; g.fillRect(x,0,64,h);} });
  const aw=new THREE.Mesh(new THREE.PlaneGeometry(1.9,0.9),new THREE.MeshStandardMaterial({map:awT,side:THREE.DoubleSide,roughness:0.9})); aw.position.set(0.65,2.25,0.45); aw.rotation.x=-1.15; aw.castShadow=true; MARKET.add(aw);
  const bulb=new THREE.Mesh(new THREE.SphereGeometry(0.035,12,8),new THREE.MeshBasicMaterial({color:0xffe0a0})); bulb.position.set(0.65,1.95,0.55); MARKET.add(bulb);
  const bg=SLD.glowSprite(MARKET,0xffc070,0.5); bg.position.copy(bulb.position); bg.scale.setScalar(0.5); MARKET.add(bg); }
const bulbL=new THREE.PointLight(0xffc27a,0,4,1.4); bulbL.position.set(0.65,1.9,0.6); scene.add(bulbL);

// ------------------------------------------------------------------ props for the years shot (stool, height marks) and the coins
const stool=new THREE.Group(); scene.add(stool);
{ const wm=std(0x5a3a24,{r:0.6}); box(0.34,0.04,0.3,wm,0,0.43,0,stool); for(const [x,z] of [[-0.14,-0.11],[0.14,-0.11],[-0.14,0.11],[0.14,0.11]]) box(0.035,0.42,0.035,wm,x,0.21,z,stool); }
const MARKS=[1.12,1.43,1.69].map((y,i)=>{ const m=box(0.07,0.014,0.006,std(0x1e1712,{r:0.8}),DOOR.x0-0.035,y,0.044,scene,false); return m; });
const coinM=new THREE.MeshStandardMaterial({color:0xe8b85a,roughness:0.25,metalness:0.85,emissive:0x5a3c10,emissiveIntensity:0.6});
const coins=[0,1,2].map(()=>{ const c=new THREE.Mesh(new THREE.CylinderGeometry(0.02,0.02,0.004,20),coinM); c.castShadow=true; scene.add(c); return c; });
const cardPiece=box(0.34,0.005,0.13,new THREE.MeshStandardMaterial({map:cardTex,roughness:0.9,emissive:0x6a4420,emissiveIntensity:0.5}),0,0,0,scene);

// ================================================================== figures
const R=SLD.createRig(scene);
const RK=[0.6,0.78,0.92].map(sc=>SLD.createRig(scene,sc));     // the boy at 7, 11, 15
const DAD_C=0xd8d0c0, DAD_OLD=0xb4b0aa, SON_C=0xe2b672, SELL_C=0x7f8a98;
const dad=R.makeFig(DAD_C,'dad',{rim:0.1,lift:0.02});
const son=R.makeFig(SON_C,'son',{rim:0.12,lift:0.03});
const seller=R.makeFig(SELL_C,'seller',{rim:0.1,lift:0.02});
const kids=RK.map((r,i)=>r.makeFig(SON_C,'kid'+i,{rim:0.12,lift:0.03}));

// ------------------------------------------------------------------ the shoes
const SH={L:0.2,Wd:0.085,Ht:0.1,Sole:0.034,ank:-0.08};   // half-length, half-width, upper height, sole thickness, ankle x in shoe
const leatherTex=canvasTex(512,256,(g,w,h)=>{ const R=rng(31); g.fillStyle='#4a2e1e'; g.fillRect(0,0,w,h);
  for(let i=0;i<500;i++){ g.fillStyle=`rgba(${R()<0.6?20:150},${R()<0.6?10:110},${R()<0.6?6:80},${0.05+R()*0.12})`; g.beginPath(); g.ellipse(R()*w,R()*h,3+R()*26,2+R()*8,R()*3,0,7); g.fill(); }
  g.strokeStyle='rgba(205,170,130,0.16)'; g.lineWidth=2; for(let i=0;i<22;i++){ g.beginPath(); const x=R()*w, y=h*0.3+R()*h*0.6; g.moveTo(x,y); g.quadraticCurveTo(x+10,y-6+R()*12,x+16+R()*30,y+(R()-0.5)*10); g.stroke(); }
  g.strokeStyle='rgba(20,12,8,0.8)'; g.setLineDash([6,5]); g.lineWidth=2; g.beginPath(); g.moveTo(0,h*0.92); g.lineTo(w,h*0.92); g.stroke(); });
const cardTex2=cardTex;
const tapeTex=canvasTex(128,64,(g,w,h)=>{ const R=rng(77); g.fillStyle='#b9bcbf'; g.fillRect(0,0,w,h); for(let i=0;i<300;i++){ g.fillStyle=`rgba(${R()<0.5?60:255},${R()<0.5?60:255},${R()<0.5?60:255},0.12)`; g.fillRect(R()*w,R()*h,1+R()*5,1); } g.fillStyle='rgba(40,40,40,0.25)'; for(let x=0;x<w;x+=4) g.fillRect(x,0,1,h); });
function footprint(x0,x1,n=24){ const pts=[]; const wAt=x=>{ const u=x/SH.L; return SH.Wd*1.04*Math.sqrt(Math.max(0,1-Math.pow(Math.abs(u),2.4)))*(x<0?0.92:1); };
  for(let i=0;i<=n;i++){ const x=lerp(x0,x1,i/n); pts.push(new THREE.Vector2(x,wAt(x))); } for(let i=n;i>=0;i--){ const x=lerp(x0,x1,i/n); pts.push(new THREE.Vector2(x,-wAt(x))); } return new THREE.Shape(pts); }
function shoeGeo(geo,k=1){ geo.scale(SH.Ht*k,SH.L*(k>1?1.012:1),SH.Wd*k); geo.rotateZ(-Math.PI/2); const p=geo.attributes.position;
  for(let i=0;i<p.count;i++){ const x=p.getX(i), y=p.getY(i); const u=x/SH.L; const prof=lerp(1.0,0.42,sstep(-0.25,0.95,u)); p.setY(i,y*prof*(1+0.12*sstep(-1,-0.6,u))); }
  geo.computeVertexNormals(); return geo; }
// style: patched (dad), torn (the boy's old pair: toe through a hole), fresh (the boy's new white pair), smart (grown son)
function makeShoe(key,style,toeCol){
  const g=new THREE.Group(); const piv=new THREE.Group(); g.add(piv); piv.position.set(-SH.ank,-0.001,0);
  let upM;
  if(style==='fresh') upM=rimify(new THREE.MeshStandardMaterial({color:0xf3efe6,roughness:0.5,emissive:0x302c26,emissiveIntensity:0.4,side:THREE.DoubleSide}),0xffffff,0.25,'up'+key);
  else if(style==='smart') upM=rimify(new THREE.MeshStandardMaterial({color:0x2a1a12,roughness:0.3,side:THREE.DoubleSide}),0xffd9a8,0.3,'up'+key);
  else upM=rimify(new THREE.MeshStandardMaterial({map:leatherTex,roughness:0.68,color:style==='torn'?0xb89a80:0xffffff,side:THREE.DoubleSide,emissive:0x1a0e08,emissiveIntensity:0.5}),0xffd9a8,0.22,'up'+key);
  const up=new THREE.Mesh(shoeGeo(new THREE.SphereGeometry(1,48,28,-Math.PI/2,Math.PI,0,Math.PI)),upM); up.castShadow=true; up.receiveShadow=true; piv.add(up);
  const hole=new THREE.Mesh(new THREE.CircleGeometry(1,28),std(0x120a06,{r:1})); hole.rotation.x=-Math.PI/2; hole.scale.set(0.072,0.06,1); hole.position.set(SH.ank+0.005,SH.Ht*0.97,0); piv.add(hole);
  const laceM=std(style==='fresh'?0xd23a2e:0xd8ccb0,{r:0.7}); for(let k=0;k<3;k++){ const l=box(0.012,0.008,SH.Wd,laceM,k*0.03,SH.Ht*(0.86-k*0.1),0,piv,false); l.rotation.z=-0.45-k*0.05; }
  const soleM=std(style==='fresh'?0xe8e2d4:0x1b1410,{r:0.85});
  const ext=(x0,x1)=>{ const geo=new THREE.ExtrudeGeometry(footprint(x0,x1),{depth:SH.Sole,bevelEnabled:true,bevelThickness:0.004,bevelSize:0.004,bevelSegments:2}); geo.rotateX(-Math.PI/2); return geo; };
  const cardM=new THREE.MeshStandardMaterial({map:cardTex2,roughness:0.9,emissive:0x6a4420,emissiveIntensity:0.6});
  const heel=new THREE.Mesh(ext(-SH.L,0),soleM); heel.position.y=-SH.Sole; heel.castShadow=true; heel.receiveShadow=true; piv.add(heel);
  const flapP=new THREE.Group(); piv.add(flapP);
  const flap=new THREE.Mesh(ext(-0.0005,SH.L),style==='patched'?[cardM,soleM]:soleM); flap.position.set(0,-SH.Sole,0); flap.castShadow=true; flap.receiveShadow=true; flapP.add(flap);
  if(style==='patched'){ const cg=new THREE.ExtrudeGeometry(footprint(-0.01,SH.L*0.99),{depth:0.012,bevelEnabled:false}); cg.rotateX(-Math.PI/2);
    const cb=new THREE.Mesh(cg,new THREE.MeshStandardMaterial({map:cardTex2,roughness:0.9,emissive:0x3a2410,emissiveIntensity:0.5})); cb.scale.set(1.03,1,1.1); cb.position.y=-0.012; cb.castShadow=true; piv.add(cb);
    const tape=new THREE.Mesh(shoeGeo(new THREE.SphereGeometry(1,48,6,-Math.PI/2,Math.PI,0.42,0.3),1.04),new THREE.MeshStandardMaterial({map:tapeTex,roughness:0.35,metalness:0.35,color:0xffffff,emissive:0x202020})); tape.castShadow=true; piv.add(tape); }
  if(style==='fresh'){ const st=new THREE.Mesh(shoeGeo(new THREE.SphereGeometry(1,48,4,-Math.PI/2,Math.PI,1.2,0.22),1.02),std(0xd23a2e,{r:0.5})); piv.add(st); }
  let toe=null;
  if(style==='torn'){ const rim_=new THREE.Mesh(new THREE.CircleGeometry(0.04,20),std(0x120a06,{r:1})); rim_.rotation.y=Math.PI/2; rim_.position.set(SH.L*0.9,SH.Ht*0.2,0.0); rim_.rotation.z=0.3; piv.add(rim_);
    toe=new THREE.Mesh(new THREE.SphereGeometry(0.05,16,12),new THREE.MeshStandardMaterial({color:toeCol,roughness:0.62,emissive:toeCol,emissiveIntensity:0.05})); toe.position.set(SH.L*0.9,SH.Ht*0.2,0); toe.castShadow=true; piv.add(toe); }
  scene.add(g); return {g,flapP,toe,sc:1,style};
}
const dadSh=[makeShoe('dL','patched'),makeShoe('dR','patched')];
const kidTorn=[makeShoe('tL','torn',SON_C),makeShoe('tR','torn',SON_C)];
const kidNew=[makeShoe('nL','fresh'),makeShoe('nR','fresh')];
const sonSh=[makeShoe('sL','smart'),makeShoe('sR','smart')];
const ALLSHOES=[...dadSh,...kidTorn,...kidNew,...sonSh];
function placeShoe(sh,ank,yaw=0,pitch=0,flap=0,sc=1){ sh.g.visible=true; sh.g.scale.setScalar(sc); sh.g.position.copy(ank); sh.g.position.y-=0.035*(1-sc)*0.9;
  sh.g.rotation.set(0,yaw,-pitch); const hb=Math.max(0,ank.y-0.04); sh.flapP.rotation.z=-Math.min(flap,Math.atan2(hb,SH.L*sc)); }

// ================================================================== the walk: planted feet, 2-bone leg IK (fixed: the standing foot keeps its placement)
function legIK(Rg,dx,dy){ const T=Rg.L.thigh, Sh=Rg.L.shin; const d=Math.min(Math.hypot(dx,dy),T+Sh-0.002);
  const k=Math.PI-Math.acos(clamp((T*T+Sh*Sh-d*d)/(2*T*Sh),-1,1)); const al=Math.acos(clamp((T*T+d*d-Sh*Sh)/(2*T*d),-1,1)); return {a:Math.atan2(dx,-dy)+al,k}; }
function flapAt(f){ if(f.u<0) return 0; const u=f.u; let a=0.8*sstep(0.04,0.3,u)*(1-sstep(0.84,0.97,u)); a+=0.07*Math.sin(u*22)*sstep(0.1,0.3,u)*(1-sstep(0.7,0.9,u)); return Math.max(0,a); }
function makeWalk(o){   // o: Rg, sc, X0, STEP, TS, T0, ZW, HIPY, p, tilt
  const SW=0.82, sc=o.sc||1;
  function foot(side,t){ const tt=t-o.T0; const k=Math.floor(tt/o.TS); const ph=tt/o.TS-k; const mine=(k%2===0)===(side==='L'); const s=side==='L'?0:1;
    const land=j=>o.X0+s*o.STEP+j*2*o.STEP; const jP=mine?(k-s)/2:Math.floor((k-s-1)/2)+1;
    if(!mine) return {x:land(jP),lift:0,u:-1,pitch:0}; if(ph>SW) return {x:land(jP+1),lift:0,u:-1,pitch:0};
    const u=ph/SW; return {x:lerp(land(jP),land(jP+1),SLD.ease(u)),lift:(0.12*Math.sin(Math.PI*u)+0.02*Math.sin(Math.PI*Math.min(1,u*2)))*sc,u,
      pitch:0.38*Math.sin(Math.PI*Math.min(1,u*1.6))*(1-sstep(0.55,0.75,u))-0.16*sstep(0.6,0.85,u)*(1-sstep(0.9,1,u))}; }
  const hipX=t=>o.X0+(t-o.T0)*o.STEP/o.TS;
  function pose(F,shoes,t,flapOn=true,arms=null){
    const c=(t-o.T0)/o.TS*Math.PI; const hx=hipX(t)+0.03*sc*Math.sin(2*c), hy=o.HIPY-0.018*sc*Math.cos(2*c);
    const fL=foot('L',t), fR=foot('R',t);
    const aL=V(fL.x,0.035+fL.lift,o.ZW+0.08), aR=V(fR.x,0.035+fR.lift,o.ZW-0.08);
    const iL=legIK(o.Rg,aL.x-hx,aL.y-hy), iR=legIK(o.Rg,aR.x-hx,aR.y-hy); const sw=Math.sin(c);
    const P={...o.Rg.P0,p:o.p??0.16,tilt:o.tilt??0.12,aL:iL.a,kL:iL.k,aR:iR.a,kR:iR.k,sL:0.08-0.22*sw,sR:-0.04+0.22*sw,eL:0.3,eR:0.3,...(arms||{})};
    const T_=o.Rg.L.thigh, S_=o.Rg.L.shin;
    const fl=[Math.sin(P.aL)*T_+Math.sin(P.aL-P.kL)*S_,-Math.cos(P.aL)*T_-Math.cos(P.aL-P.kL)*S_], fr=[Math.sin(P.aR)*T_+Math.sin(P.aR-P.kR)*S_,-Math.cos(P.aR)*T_-Math.cos(P.aR-P.kR)*S_];
    P.fx=(fl[0]+fr[0])*0.3; P.dy=hy+Math.min(fl[1],fr[1])-0.035;
    const J=o.Rg.skel(P,V(hx,0,o.ZW),0); o.Rg.poseFig(F,J);
    if(shoes){ placeShoe(shoes[0],J.fL,0,fL.pitch,flapOn?flapAt(fL):0,sc); placeShoe(shoes[1],J.fR,0,fR.pitch,flapOn?flapAt(fR):0,sc); }
    return {hx,J,fL,fR}; }
  function slaps(t0,t1,off){ const ev=[]; for(let k=0;k<60;k++){ const tl=o.T0+k*o.TS+SW*o.TS*0.97; if(tl>=t0&&tl<t1) ev.push(+(tl+off).toFixed(3)); } return ev; }
  return {foot,hipX,pose,slaps};
}
const P0=R.P0;
function standFig(Rg,F,shoes,root,yaw,P,sc=1){ const J=Rg.skel({...Rg.P0,...P},root,yaw); Rg.poseFig(F,J); if(shoes){ placeShoe(shoes[0],J.fL,yaw,0,0,sc); placeShoe(shoes[1],J.fR,yaw,0,0,sc); } return J; }

// ================================================================== shot list (output seconds)
// A 0-2.55 hook: old dad walks past the closed box (2.55-3.0 is the rewind smear, done in compose)
// B1 3.0-4.2 the boy's toe through his torn shoe | B2 4.2-6.2 dad pays his coins | B3 6.2-9.0 walking home, new shoes vs flapping sole
// C 9.0-14.0 three years, three hard cuts: dad slides new cardboard in, the boy grows against the door frame
// D 14.0-19.0 the grown son gives the first-salary gift; dad hugs it
// E 19.0-28.0 years later: the box still closed under dust; dad walks in on the same patched shoes; hold for the ending lines
const SHOTS=[['A',0,3.0],['B1',3.0,4.2],['B2',4.2,6.2],['B3',6.2,9.0],['C',9.0,14.0],['D',14.0,19.0],['E',19.0,28.0]];
const shotAt=T=>{ for(const s of SHOTS) if(T>=s[1]&&T<s[2]) return s; return SHOTS[SHOTS.length-1]; };
const wA=makeWalk({Rg:R,X0:-0.4,STEP:0.3,TS:0.85,T0:-0.41,ZW:0.66,HIPY:0.86,p:0.24,tilt:0.18});
const wBd=makeWalk({Rg:R,X0:-0.95,STEP:0.3,TS:0.85,T0:-0.3,ZW:0.55,HIPY:0.875,p:0.12,tilt:0.08});
const wBk=makeWalk({Rg:RK[0],sc:0.6,X0:-0.62,STEP:0.17,TS:0.48,T0:-0.1,ZW:1.0,HIPY:0.535,p:0.05,tilt:-0.05});
const E_STOP=(5+0.9)*0.85;   // E walk freezes in double support
const wE=makeWalk({Rg:R,X0:-1.85,STEP:0.3,TS:0.85,T0:0,ZW:0.66,HIPY:0.86,p:0.26,tilt:0.2});
const CXO=0.03;
function hookCam(t){ const cx=CXO+0.03*t, z=keys([[0,2.05],[3.0,1.9]],t); cam.position.set(cx,0.42,0.66+z); cam.lookAt(cx,0.5,0.66-0.25); cam.fov=50; }
function setSets(home){ HOME.forEach(o=>o.visible=home); MARKET.visible=!home; bulbL.intensity=home?0:1.2; S.renderer.toneMappingExposure=home?0.95:0.72;
  S.floor.material.color.set(home?0xd8b0a0:0xa49488); }
function setSun(mode){ if(mode==='home'){ sun.color.set(0xffe6c0); sun.intensity=30; sun.position.set(2.9,1.9,-1.6); sun.target.position.set(-0.4,0,1.2); fill.intensity=0.45; wallWash.intensity=2.2; }
  if(mode==='late'){ sun.color.set(0xffa860); sun.intensity=22; sun.position.set(2.9,1.3,-1.6); sun.target.position.set(-0.4,0,1.2); fill.color.set(0xa8b4d8); fill.intensity=0.5; wallWash.intensity=1.5; }
  if(mode==='market'){ sun.color.set(0xfff0d0); sun.intensity=16; sun.position.set(3.2,4.2,3.4); sun.target.position.set(0.2,0.4,0.6); fill.intensity=0.3; wallWash.intensity=0.6; } }
const META={};
function hideAll(){ for(const F of [dad,son,seller,...kids]) F.all.forEach(m=>m.visible=false); ALLSHOES.forEach(s=>s.g.visible=false); coins.forEach(c=>c.visible=false); cardPiece.visible=false; stool.visible=false; MARKS.forEach(m=>m.visible=false); gift.visible=false; ribGlow.visible=false; }
function showFig(F,bareFeet=false){ F.all.forEach(m=>m.visible=true); F.joints[4].visible=bareFeet; F.joints[5].visible=bareFeet; }
function giftAt(p,ry=-0.1){ gift.visible=true; gift.position.copy(p); gift.rotation.set(0,ry,0); ribGlow.visible=true; ribGlow.position.set(p.x,p.y+BOX.h+0.03,p.z+0.05); }

function setT(T){
  hideAll(); const [id,t0]=shotAt(T); const t=T-t0; META.shot=id;
  dad.mat.color.set(DAD_C); dad.mat.emissive.set(DAD_C);
  if(id==='A'){ setSets(true); setSun('home'); dustU.uDust.value=0.5; dad.mat.color.set(DAD_OLD); dad.mat.emissive.set(DAD_OLD);
    showFig(dad); wA.pose(dad,dadSh,Math.min(T,2.95)); giftAt(V(BOX.x,BOX.y,BOX.z)); hookCam(Math.min(T,2.95)); }
  else if(id==='B1'){ setSets(false); setSun('market');
    showFig(dad); standFig(R,dad,dadSh,V(-0.32,0,0.95),-0.25,{p:0.12,tilt:0.1});
    showFig(kids[0]); const w=Math.sin(t*9)*0.5+0.5; standFig(RK[0],kids[0],kidTorn,V(0.15,0,0.98),-0.1,{p:0.06,tilt:0.25,aL:0.02,aR:-0.08},0.6);
    kidTorn.forEach((s,i)=>{ s.toe.position.x=SH.L*(0.9+0.12*(i===1?w:w*0.5)); });
    showFig(seller,true); standFig(R,seller,null,V(0.7,0,0.15),-Math.PI/2,{p:0.1});
    const cx=0.22+0.02*t; cam.position.set(cx,0.22,0.98+0.95-0.06*t); cam.lookAt(cx,0.2,0.98); cam.fov=45; }
  else if(id==='B2'){ setSets(false); setSun('market');
    // dad pays: hand over the counter 0.2-0.7, three coins fall 0.7-1.1 into the seller's palm; the boy lifts the new pair to his chest 1.1-1.7
    const reach=sstep(0.15,0.65,t)*(1-sstep(1.3,1.8,t)), give=sstep(1.1,1.6,t);
    showFig(dad); const dHand=V(0.33,1.0,0.78);
    standFig(R,dad,dadSh,V(-0.32,0,0.95),-0.25,{p:0.14,tilt:0.08,tR:dHand,wR:reach,pR:V(0.3,-0.5,-0.6)});
    showFig(seller,true); const sHand=V(0.36,0.86,0.76);
    standFig(R,seller,null,V(0.72,0,0.15),-Math.PI/2,{p:0.16,tilt:0.1,tR:sHand,wR:sstep(0.3,0.7,t)*(1-sstep(1.5,1.9,t)),pR:V(-0.3,-0.6,0.4),tL:V(0.9,0.8,0.55),wL:0.8});
    coins.forEach((c,i)=>{ const tc=0.7+i*0.12; c.visible=t>0.55; const u=clamp((t-tc)/0.22); const y=t<tc?dHand.y-0.03:lerp(dHand.y-0.03,sHand.y+0.01+i*0.005,u*u);
      c.position.set(dHand.x+0.02*i-0.02,y,dHand.z-0.01); c.rotation.set(0.3+(1-u)*t*7,0,0.2*i); });
    const kHome=V(0.35,0.82,0.7), kChest=V(0.32,0.72,1.0); const kp=kHome.clone().lerp(kChest,sstep(1.15,1.65,t));
    showFig(kids[0]); standFig(RK[0],kids[0],kidTorn,V(0.15,0,0.98),-0.1,{p:0.08+0.1*sstep(0.9,1.2,t)*(1-give),tilt:0.15,tL:kp.clone().add(V(0,0,0.07)),tR:kp.clone().add(V(0,0,-0.07)),wL:sstep(0.95,1.15,t),wR:sstep(0.95,1.15,t)},0.6);
    kidTorn.forEach(s=>{ s.toe.position.x=SH.L*0.95; });
    placeShoe(kidNew[0],kp.clone().add(V(0.0,-0.03,0.06)),0,give*0.5,0,0.6); placeShoe(kidNew[1],kp.clone().add(V(0.02,-0.03,-0.06)),0,give*0.5,0,0.6);
    const z=keys([[0,2.7],[2,2.5]],t); cam.position.set(0.25,1.05,0.75+z); cam.lookAt(0.25,0.88,0.6); cam.fov=50; META.coinT=[0.7,0.82,0.94].map(x=>+(x+t0).toFixed(3)); }
  else if(id==='B3'){ setSets(false); setSun('market');
    showFig(dad); showFig(kids[0]);
    wBk.pose(kids[0],kidNew,t,false,null); wBd.pose(dad,dadSh,t,true,null);
    const cx=-0.4+0.2*t; cam.position.set(cx,0.42,0.66+2.1); cam.lookAt(cx,0.48,0.66-0.25); cam.fov=50; }
  else if(id==='C'){ setSets(true); setSun('home'); dustU.uDust.value=0;
    const beat=Math.min(2,Math.floor(t/(5/3))), bt=t-beat*(5/3);
    stool.visible=true; stool.position.set(0.12,0,0.8);
    // dad on the stool, right foot bare, left foot in its patched shoe; the right shoe in his hand, new cardboard sliding in
    showFig(dad); dad.joints[5].visible=true;
    const shoePos=V(0.52,0.6,0.86), push=sstep(0.25,1.15,bt);
    const cbStart=shoePos.clone().add(V(-0.3,0.13,0)), cbEnd=shoePos.clone().add(V(-0.04,0.03,0)); const cb=cbStart.clone().lerp(cbEnd,push);
    cardPiece.visible=true; cardPiece.position.copy(cb).add(V(0.1,0,0)); cardPiece.rotation.set(0,0,lerp(-0.42,-0.12,push));
    const Pd={p:0.42,tilt:0.25,aL:1.52,aR:1.46,kL:1.5,kR:1.42,dy:0,fx:0.283,sL:0.6,sR:0.6,eL:0.9,eR:0.9,
      tL:shoePos.clone().add(V(-0.02,-0.01,0.08)),wL:1,pL:V(0,-0.6,0.8),tR:cb.clone().add(V(-0.08,0.02,-0.06)),wR:1,pR:V(-0.2,-0.6,-0.8)};
    const J=standFig(R,dad,null,V(0.12,0,0.8),0,Pd);
    placeShoe(dadSh[0],J.fL,0,0,0,1);
    placeShoe(dadSh[1],shoePos.clone().add(V(0.09,-0.035,0)),0,-0.12,0,1); dadSh[1].g.position.copy(shoePos); dadSh[1].g.rotation.set(0,0,0.12);
    // the boy against the door frame, a new pencil mark each year
    const ki=beat; const Rg=RK[ki]; showFig(kids[ki]); standFig(Rg,kids[ki],kidNew,V(0.88,0,0.22),Math.PI,{p:0.02,tilt:-0.06,sL:0.05,sR:-0.05},[0.6,0.78,0.92][ki]);
    MARKS.forEach((m,i)=>m.visible=i<ki||(i===ki&&bt>0.3));
    const z=keys([[0,2.95],[5/3,2.85]],bt); cam.position.set(0.55,0.95,0.6+z); cam.lookAt(0.55,0.85,0.5); cam.fov=50; META.beat=beat; META.cardT=[0,1,2].map(b=>+(t0+b*5/3+0.3).toFixed(3)); }
  else if(id==='D'){ setSets(true); setSun('home'); dustU.uDust.value=0;
    // son offers the box (0-1.2), dad takes it (1.2-2.2) and hugs it to his chest (2.2-3.0), holds it
    const ext=sstep(0.1,1.1,t), take=sstep(1.3,2.3,t), hug=sstep(2.3,3.0,t);
    const bSon=V(0.72,1.0,0.6), bMid=V(0.55,1.04,0.6), bDad=V(0.36,1.12,0.62);
    const bp=t<1.3?bSon.clone().lerp(bMid,ext):bMid.clone().lerp(bDad,take);
    const sway=0.01*Math.sin(t*2.2)*hug; bp.y+=sway;
    giftAt(V(bp.x,bp.y-BOX.h/2,bp.z),Math.PI/2); dustU.uDust.value=0;
    const ends=[bp.clone().add(V(0,0,BOX.w/2+0.015)),bp.clone().add(V(0,0,-BOX.w/2-0.015))];
    showFig(son); standFig(R,son,sonSh,V(0.98,0,0.6),Math.PI,{p:0.1+0.06*ext,tilt:-0.05+0.2*ext,tL:ends[1],tR:ends[0],wL:1-take*0.9,wR:1-take*0.9,pL:V(-0.2,-0.6,0.8),pR:V(-0.2,-0.6,-0.8)});
    showFig(dad); standFig(R,dad,dadSh,V(0.08,0,0.6),0,{p:0.1+0.18*hug,tilt:-0.15+0.2*sstep(0.8,1.3,t)+0.45*hug,tL:ends[0],tR:ends[1],wL:sstep(1.0,1.5,t),wR:sstep(1.0,1.5,t),pL:V(-0.2,-0.6,0.8),pR:V(-0.2,-0.6,-0.8)});
    const z=keys([[0,3.1],[5,2.7]],t); cam.position.set(0.53,1.05,0.6+z); cam.lookAt(0.53,0.98,0.5); cam.fov=50; }
  else if(id==='E'){ setSets(true); setSun('late'); dustU.uDust.value=0.85; dad.mat.color.set(DAD_OLD); dad.mat.emissive.set(DAD_OLD);
    giftAt(V(BOX.x,BOX.y,BOX.z));
    showFig(dad); wE.pose(dad,dadSh,Math.min(t,E_STOP),t<E_STOP);
    // push in on the box (0-2.2), crane down and back to the hook framing as his feet walk in (2.2-3.6), hold
    const u=sstep(2.2,3.6,t); const hc={p:V(CXO+0.03*0,0.42,0.66+2.05),l:V(CXO,0.5,0.41)};
    const bc={p:V(BOX.x-0.05,0.66,BOX.z+1.05-0.25*sstep(0,2.2,t)),l:V(BOX.x,0.55,BOX.z)};
    const hold=keys([[3.6,0],[9,0.12]],t);
    cam.position.copy(bc.p.clone().lerp(hc.p,u)).add(V(0,0,-hold)); cam.lookAt(bc.l.clone().lerp(hc.l,u)); cam.fov=lerp(42,50,u); }
  cam.updateProjectionMatrix(); S.tick(T);
}
// sound events in output seconds
const events=[];
wA.slaps(0,2.55,0).forEach(x=>events.push({t:x,type:'slap'}));
wBd.slaps(0,2.8,6.2).forEach(x=>events.push({t:x,type:'slap'}));
wBk.slaps(0,2.8,6.2).forEach(x=>events.push({t:x,type:'kidstep'}));
wE.slaps(2.0,E_STOP+0.01,19).forEach(x=>events.push({t:x,type:'slap'}));
[4.9,5.02,5.14].forEach(x=>events.push({t:x,type:'coin'}));
[0,1,2].forEach(b=>events.push({t:+(9+b*5/3+0.3).toFixed(3),type:'card'}));
events.push({t:14.2,type:'paper'},{t:16.5,type:'paper'});
setT(0);
window.metaAt=t=>{ setT(t); return {shot:META.shot,beat:META.beat??0}; };
window.events=events;
window.renderAt=(t,K)=>{ const [,a,b]=shotAt(t); return S.renderAt(setT,t,K,{t0:a,t1:b}); };
S.renderAt(setT,0.5,1,{t0:0,t1:3}); for(const T of [3.5,5,7,10,15,22]) S.renderAt(setT,T,1,{t0:0,t1:DUR}); S.renderAt(setT,0,1,{t0:0,t1:3});   // warm-up: upload every set's textures before the first real frame
window.ready=true;
