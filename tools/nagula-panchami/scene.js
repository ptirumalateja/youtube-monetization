// Nagula Panchami: stickman remake of the Telugu film dialogue clip (14.2 s, the clip's own audio).
// Two sets: the hero's bedroom (origin) and the hallway outside his door (x offset HX).
// Units metres, floor y=0, back walls face z=0, camera on +z. renderAt is pure (parallel workers).
import * as THREE from 'three';
import * as SLD from './sld.js';
const {V,clamp,sstep,lerp,keys,rng,noiseTex,rimify,PAL}=SLD;
const Q=new URLSearchParams(location.search);
const W=+Q.get('w')||1080, H=+Q.get('h')||1920;
const DUR=14.2;
// shot cuts copied from the reference clip (scene-change detection)
const CUTS=[0,4.5,8.8,11.2167,13.05,DUR];
const SHOTS=['H1','U1','H2','U2','H3'];
const shotAt=t=>{ for(let i=0;i<SHOTS.length;i++) if(t<CUTS[i+1]) return [SHOTS[i],CUTS[i],CUTS[i+1]]; return [SHOTS[4],CUTS[4],CUTS[5]]; };

const S=SLD.createStage({W,H,lamp:V(-2.2,3.2,1.6),lampTarget:V(0.0,0.5,0.6),cone:0.6,spot:38,beam:0.05,fov:46,bg:0xf2dfc4,fog:0.012,vig:0.0,hemi:0.9,hemiSky:0xfff1dc,motes:900,floorCol:0xcfc2b0});
const {scene,cam}=S;
S.renderer.toneMappingExposure=0.82; S.bloom.strength=0.18; S.bloom.threshold=0.92;
const canvasTex=(w,h,draw,srgb=true)=>{ const c=document.createElement('canvas'); c.width=w; c.height=h; draw(c.getContext('2d'),w,h); const t=new THREE.CanvasTexture(c); if(srgb) t.colorSpace=THREE.SRGBColorSpace; t.anisotropy=8; return t; };
const std=(color,o={})=>new THREE.MeshStandardMaterial({color,roughness:o.r??0.8,metalness:o.m??0,...o.x});
const box=(w,h,d,mat,x,y,z,parent=scene,cast=true)=>{ const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat); m.position.set(x,y,z); m.castShadow=cast; m.receiveShadow=true; parent.add(m); return m; };
const boxE=(x0,x1,y0,y1,z0,z1,mat,parent=scene,cast=true)=>box(x1-x0,y1-y0,z1-z0,mat,(x0+x1)/2,(y0+y1)/2,(z0+z1)/2,parent,cast);
const plane=(w,h,mat,x,y,z,parent=scene)=>{ const m=new THREE.Mesh(new THREE.PlaneGeometry(w,h),mat); m.position.set(x,y,z); m.receiveShadow=true; parent.add(m); return m; };
const texMat=(tex,o={})=>new THREE.MeshStandardMaterial({map:tex,roughness:o.r??0.7,emissive:o.e??0x000000,emissiveIntensity:o.ei??0,emissiveMap:o.ei?tex:null});

// floor: light marble tiles (both sets)
{ const ft=canvasTex(1024,1024,(g,w,h)=>{ const R=rng(8); g.fillStyle='#d9cfc2'; g.fillRect(0,0,w,h);
    for(let i=0;i<700;i++){ g.strokeStyle=`rgba(${120+R()*60},${110+R()*50},${100+R()*40},${0.05+R()*0.08})`; g.lineWidth=1+R()*2; g.beginPath(); let x=R()*w,y=R()*h; g.moveTo(x,y); for(let k=0;k<4;k++){ x+=(R()-0.5)*80; y+=(R()-0.5)*80; g.lineTo(x,y);} g.stroke(); }
    g.fillStyle='rgba(90,80,70,0.35)'; for(let k=0;k<=2;k++){ g.fillRect(0,k*512-2,w,4); g.fillRect(k*512-2,0,4,h); } });
  ft.wrapS=ft.wrapT=THREE.RepeatWrapping; ft.repeat.set(30,30);
  S.floor.material.map=ft; S.floor.material.color.set(0xffffff); S.floor.material.roughness=0.35; S.floor.material.opacity=0.93; S.floor.material.needsUpdate=true; }

const wallTex=(base,seed)=>{ const t=canvasTex(512,512,(g,w,h)=>{ const R=rng(seed); g.fillStyle=base; g.fillRect(0,0,w,h);
  for(let i=0;i<420;i++){ g.fillStyle=`rgba(${R()<0.5?60:255},${R()<0.5?40:240},${R()<0.5?30:220},${0.02+R()*0.035})`; g.beginPath(); g.ellipse(R()*w,R()*h,8+R()*50,8+R()*40,0,0,7); g.fill(); } });
  t.wrapS=t.wrapT=THREE.RepeatWrapping; t.repeat.set(3,2); return t; };

// ================================================================== ROOM (hero's bedroom)
const DOOR={x0:0.78,x1:1.62,y1:2.12};
const roomWall=new THREE.MeshStandardMaterial({color:0xffffff,map:wallTex('#f2c9a0',3),roughness:0.95});
const WIN={x0:-1.75,x1:-0.95,y0:0.95,y1:2.05};
[[-4,WIN.x0,0,3.4],[WIN.x1,DOOR.x0,0,3.4],[DOOR.x1,4,0,3.4],[WIN.x0,WIN.x1,0,WIN.y0],[WIN.x0,WIN.x1,WIN.y1,3.4],[DOOR.x0,DOOR.x1,DOOR.y1,3.4]].forEach(([a,b,c,d])=>boxE(a,b,c,d,-0.14,0,roomWall));
// left side wall (adds depth on the wide frames)
boxE(-2.3,-2.16,0,3.4,-0.14,4,roomWall);
const skirtM=std(0xb07a52,{r:0.6}); boxE(-2.16,DOOR.x0-0.07,0,0.09,0,0.015,skirtM); boxE(DOOR.x1+0.07,4,0,0.09,0,0.015,skirtM);
const woodM=(c,s)=>{ const t=noiseTex(256,s,128,60,30,0.1); t.repeat.set(2,2); return new THREE.MeshStandardMaterial({color:c,roughness:0.55,map:t}); };
const trimM=std(0xf6efe4,{r:0.5});
// window: white frame, green grill, bright sky + neighbour's coconut tree beyond, curtains
{ const t=0.06; boxE(WIN.x0-t,WIN.x0,WIN.y0-t,WIN.y1+t,0,0.04,trimM); boxE(WIN.x1,WIN.x1+t,WIN.y0-t,WIN.y1+t,0,0.04,trimM);
  boxE(WIN.x0-t,WIN.x1+t,WIN.y1,WIN.y1+t,0,0.04,trimM); boxE(WIN.x0-t-0.05,WIN.x1+t+0.05,WIN.y0-t-0.03,WIN.y0,0,0.09,trimM);
  const grill=std(0x3f7a5a,{r:0.4});
  for(let i=1;i<6;i++){ const x=lerp(WIN.x0,WIN.x1,i/6); boxE(x-0.008,x+0.008,WIN.y0,WIN.y1,-0.08,-0.065,grill); }
  for(const y of [WIN.y0+0.36,WIN.y0+0.73]) boxE(WIN.x0,WIN.x1,y-0.008,y+0.008,-0.08,-0.065,grill);
  const sky=canvasTex(256,512,(g,w,h)=>{ const gr=g.createLinearGradient(0,0,0,h); gr.addColorStop(0,'#bfe3ff'); gr.addColorStop(0.7,'#fff6e0'); gr.addColorStop(1,'#ffe9c0'); g.fillStyle=gr; g.fillRect(0,0,w,h);
    g.fillStyle='#7aa05a'; g.beginPath(); g.ellipse(70,300,90,60,0.3,0,7); g.fill(); g.fillStyle='#5f8a48'; for(let k=0;k<7;k++){ g.beginPath(); g.ellipse(170,140,110,16,k*0.45-0.2,0,7); g.fill(); }
    g.fillStyle='#8a6a48'; g.fillRect(165,140,12,380); g.fillStyle='#e8d8c0'; g.fillRect(0,420,w,92); });
  const m=new THREE.Mesh(new THREE.PlaneGeometry(1.6,1.9),new THREE.MeshBasicMaterial({map:sky,fog:false})); m.position.set((WIN.x0+WIN.x1)/2,1.45,-0.9); scene.add(m);
  const curT=canvasTex(128,256,(g,w,h)=>{ g.fillStyle='#e07b39'; g.fillRect(0,0,w,h); for(let x=0;x<w;x+=16){ const gr=g.createLinearGradient(x,0,x+16,0); gr.addColorStop(0,'rgba(0,0,0,0.18)'); gr.addColorStop(0.5,'rgba(255,255,255,0.12)'); gr.addColorStop(1,'rgba(0,0,0,0.18)'); g.fillStyle=gr; g.fillRect(x,0,16,h);} for(let y=10;y<h;y+=40){ g.fillStyle='rgba(255,230,160,0.5)'; g.fillRect(0,y,w,4);} });
  for(const [x0,x1] of [[WIN.x0-0.32,WIN.x0+0.04],[WIN.x1-0.04,WIN.x1+0.3]]){ const g=new THREE.CylinderGeometry(1,1,1,24,1,true,0,Math.PI);
    for(let k=0;k<4;k++){ const c=new THREE.Mesh(g,new THREE.MeshStandardMaterial({map:curT,roughness:0.9,side:THREE.DoubleSide})); const w=(x1-x0)/4; c.scale.set(w*0.6,1.35,0.05); c.rotation.y=Math.PI/2*0+Math.PI; c.position.set(x0+w*(k+0.5),1.42,0.09); c.castShadow=true; scene.add(c);} }
  boxE(WIN.x0-0.4,WIN.x1+0.4,2.12,2.14,0.07,0.1,std(0xb08850,{r:0.4})); }
// door (latched shut) on a pivot group so it can rattle on every bang
const doorG=new THREE.Group(); doorG.position.set(DOOR.x0+0.005,0,-0.02); scene.add(doorG);
{ const dm=woodM(0x8a5532,9); box(DOOR.x1-DOOR.x0-0.01,DOOR.y1-0.01,0.045,dm,(DOOR.x1-DOOR.x0)/2,DOOR.y1/2,0,doorG);
  for(const [y0,y1] of [[0.18,0.95],[1.1,1.95]]) box(0.6,y1-y0,0.02,std(0x9a6038,{r:0.45}),(DOOR.x1-DOOR.x0)/2,(y0+y1)/2,0.03,doorG);
  const brass=std(0xd9a441,{r:0.25,m:0.7}); box(0.035,0.12,0.03,brass,0.72,1.0,0.045,doorG); box(0.16,0.022,0.03,brass,0.63,1.3,0.045,doorG);
  // towel on a hook on the door
  const tw=canvasTex(64,128,(g,w,h)=>{ g.fillStyle='#2f8fb0'; g.fillRect(0,0,w,h); g.fillStyle='#f4e6c8'; for(let y=8;y<h;y+=30) g.fillRect(0,y,w,6); });
  box(0.22,0.5,0.03,texMat(tw,{r:0.95}),0.25,1.45,0.05,doorG); }
{ const t=0.07; boxE(DOOR.x0-t,DOOR.x0,0,DOOR.y1+t,0,0.04,trimM); boxE(DOOR.x1,DOOR.x1+t,0,DOOR.y1+t,0,0.04,trimM); boxE(DOOR.x0-t,DOOR.x1+t,DOOR.y1,DOOR.y1+t,0,0.04,trimM); }
// wall clock: 10:40 (late for office)
{ const ct=canvasTex(256,256,(g,w,h)=>{ g.fillStyle='#fffaf0'; g.beginPath(); g.arc(128,128,124,0,7); g.fill(); g.lineWidth=14; g.strokeStyle='#c0392b'; g.stroke();
    g.fillStyle='#222'; for(let k=0;k<12;k++){ const a=k/12*6.283; g.fillRect(128+Math.sin(a)*100-4,128-Math.cos(a)*100-4,8,8); }
    const hand=(a,l,wd)=>{ g.lineWidth=wd; g.strokeStyle='#1a1a1a'; g.lineCap='round'; g.beginPath(); g.moveTo(128,128); g.lineTo(128+Math.sin(a)*l,128-Math.cos(a)*l); g.stroke(); };
    hand((10+40/60)/12*6.283,58,12); hand(40/60*6.283,92,8); g.fillStyle='#c0392b'; g.beginPath(); g.arc(128,128,10,0,7); g.fill(); });
  const c=new THREE.Mesh(new THREE.CylinderGeometry(0.16,0.16,0.04,40),[std(0xc0392b,{r:0.4}),new THREE.MeshStandardMaterial({map:ct,roughness:0.4}),std(0xc0392b)]);
  c.rotation.x=Math.PI/2; c.position.set(0.25,2.25,0.03); c.castShadow=true; scene.add(c); }
// wall calendar with the festival circled
{ const ct=canvasTex(256,360,(g,w,h)=>{ g.fillStyle='#fffdf6'; g.fillRect(0,0,w,h); g.fillStyle='#d63a2a'; g.fillRect(0,0,w,92);
    g.fillStyle='#ffe9a8'; g.font='bold 30px sans-serif'; g.textAlign='center'; g.fillText('SHRAVANAM',w/2,58);
    g.fillStyle='#d63a2a'; g.font='bold 150px sans-serif'; g.fillText('5',w/2,240);
    g.strokeStyle='#d63a2a'; g.lineWidth=7; g.beginPath(); g.ellipse(w/2,192,78,74,0,0,7); g.stroke();
    g.fillStyle='#1d5a3a'; g.font='bold 26px sans-serif'; g.fillText('NAGULA',w/2,300); g.fillText('PANCHAMI',w/2,332); });
  const m=plane(0.34,0.48,new THREE.MeshStandardMaterial({map:ct,roughness:0.8}),0.42,1.62,0.012); m.castShadow=true;
  box(0.03,0.03,0.02,std(0x333333),0.42,1.88,0.01); }
// posters above the bed
{ const p1=canvasTex(300,420,(g,w,h)=>{ const gr=g.createLinearGradient(0,0,0,h); gr.addColorStop(0,'#ff8a3d'); gr.addColorStop(0.6,'#ffcf5a'); gr.addColorStop(1,'#3a2a4a'); g.fillStyle=gr; g.fillRect(0,0,w,h);
    g.fillStyle='#2a1a2a'; g.beginPath(); g.arc(80,330,40,0,7); g.arc(220,330,40,0,7); g.fill(); g.fillRect(70,280,170,30); g.beginPath(); g.moveTo(120,280); g.lineTo(170,240); g.lineTo(200,280); g.fill();
    g.fillStyle='#fff6e0'; g.font='bold 44px sans-serif'; g.textAlign='center'; g.fillText('RIDE',w/2,90); g.fillText('FREE',w/2,140); });
  const p2=canvasTex(300,420,(g,w,h)=>{ g.fillStyle='#1f3b5a'; g.fillRect(0,0,w,h); g.fillStyle='#ffd23f'; g.font='bold 58px sans-serif'; g.textAlign='center';
    g.fillText('SUNDAY',w/2,150); g.fillText('MOOD',w/2,215); g.fillStyle='#111'; g.fillRect(70,270,70,40); g.fillRect(160,270,70,40); g.fillRect(140,280,20,8); g.fillStyle='#ffd23f'; g.fillRect(40,340,220,6); });
  const pm=t=>new THREE.MeshStandardMaterial({map:t,roughness:0.6});
  plane(0.42,0.58,pm(p1),-0.7,1.75,0.012).rotation.z=0.03; plane(0.42,0.58,pm(p2),-0.15,1.72,0.012).rotation.z=-0.04; }
// bed: headboard on the back wall, mattress running toward camera
const BED={x0:-0.95,x1:0.3,z1:2.05,top:0.5};
{ const wm=woodM(0x7a4a2e,12); boxE(BED.x0-0.04,BED.x1+0.04,0,1.0,0,0.07,wm); boxE(BED.x0-0.04,BED.x1+0.04,0.1,0.32,0.07,BED.z1,wm);
  const st=canvasTex(512,512,(g,w,h)=>{ g.fillStyle='#9fd0e8'; g.fillRect(0,0,w,h); const R=rng(2); for(let i=0;i<90;i++){ g.fillStyle=`rgba(255,255,255,${0.35+R()*0.3})`; g.beginPath(); g.arc(R()*w,R()*h,6+R()*10,0,7); g.fill(); } });
  const mattress=new THREE.Mesh(new THREE.BoxGeometry(BED.x1-BED.x0,0.18,BED.z1-0.1,8,2,12),new THREE.MeshStandardMaterial({map:st,roughness:0.9}));
  mattress.position.set((BED.x0+BED.x1)/2,BED.top-0.09,(0.07+BED.z1)/2+0.02); mattress.castShadow=mattress.receiveShadow=true; scene.add(mattress);
  const pil=new THREE.MeshStandardMaterial({color:0xfff7ea,roughness:0.95});
  for(const [x,y,z,rx] of [[-0.62,0.66,0.22,0.5],[-0.12,0.66,0.2,0.5],[-0.38,0.76,0.15,0.75]]){ const p=new THREE.Mesh(new THREE.SphereGeometry(1,24,16),pil); p.scale.set(0.27,0.1,0.17); p.position.set(x,y,z); p.rotation.x=rx; p.castShadow=p.receiveShadow=true; scene.add(p); }
  // rumpled blanket at the foot of the bed
  const bt=canvasTex(256,256,(g,w,h)=>{ g.fillStyle='#e8a33a'; g.fillRect(0,0,w,h); g.strokeStyle='#b5442e'; g.lineWidth=10; for(let k=-h;k<w;k+=40){ g.beginPath(); g.moveTo(k,0); g.lineTo(k+h,h); g.stroke(); } });
  const bg=new THREE.SphereGeometry(1,32,16); const pos=bg.attributes.position; const R=rng(5);
  for(let i=0;i<pos.count;i++){ const x=pos.getX(i),y=pos.getY(i),z=pos.getZ(i); const n=0.12*Math.sin(x*7+z*5)+0.08*Math.sin(z*11-x*3); pos.setXYZ(i,x*(1+n*0.3),Math.max(y,-0.2)*(1+n),z); } bg.computeVertexNormals();
  const bl=new THREE.Mesh(bg,new THREE.MeshStandardMaterial({map:bt,roughness:0.95})); bl.scale.set(0.62,0.13,0.4); bl.position.set(-0.33,BED.top+0.0,1.9); bl.castShadow=bl.receiveShadow=true; scene.add(bl); }
// bedside table with phone + water bottle, office bag with ID lanyard on the floor
{ const wm=woodM(0x8a5a38,14); boxE(0.42,0.86,0,0.55,0.05,0.5,wm); boxE(0.45,0.83,0.3,0.32,0.5,0.505,std(0x5a3a22));
  const ph=box(0.08,0.012,0.16,std(0x111111,{r:0.3}),0.6,0.556,0.3); ph.rotation.y=0.3;
  const scr=canvasTex(64,128,(g,w,h)=>{ const gr=g.createLinearGradient(0,0,w,h); gr.addColorStop(0,'#5ad1ff'); gr.addColorStop(1,'#b05aff'); g.fillStyle=gr; g.fillRect(0,0,w,h); });
  const s=plane(0.07,0.15,new THREE.MeshBasicMaterial({map:scr}),0.6,0.563,0.3); s.rotation.set(-Math.PI/2,0,0.3);
  const bt=new THREE.Mesh(new THREE.CylinderGeometry(0.035,0.035,0.24,20),new THREE.MeshPhysicalMaterial({color:0x7fd6ff,roughness:0.1,transmission:0.0,transparent:true,opacity:0.75})); bt.position.set(0.76,0.67,0.2); bt.castShadow=true; scene.add(bt);
  box(0.04,0.03,0.04,std(0x2a7fd6),0.76,0.8,0.2);
  const bagM=std(0x2c2f36,{r:0.7}); const bag=box(0.38,0.42,0.14,bagM,0.95,0.21,0.85); bag.rotation.y=-0.35; box(0.3,0.16,0.02,std(0x3a3f48),0.0,-0.05,0.075,bag,false);
  const card=canvasTex(128,180,(g,w,h)=>{ g.fillStyle='#fff'; g.fillRect(0,0,w,h); g.fillStyle='#2a6fdb'; g.fillRect(0,0,w,40); g.fillStyle='#fff'; g.font='bold 20px sans-serif'; g.textAlign='center'; g.fillText('OFFICE ID',w/2,28); g.fillStyle='#ccc'; g.fillRect(34,56,60,70); g.fillStyle='#333'; g.fillRect(24,140,80,8); g.fillRect(34,156,60,6); });
  const cm=plane(0.07,0.1,new THREE.MeshStandardMaterial({map:card,roughness:0.5}),0.0,0.08,0.081,bag); cm.rotation.z=0.15;
  const lan=new THREE.Mesh(new THREE.TorusGeometry(0.11,0.006,6,30,Math.PI*1.2),std(0x2a6fdb)); lan.position.set(0,0.17,0.08); lan.rotation.z=-Math.PI*0.1-Math.PI; bag.add(lan); }
// slippers by the bed
{ const sm=std(0x2a6fdb,{r:0.6}); for(const [x,z,r] of [[0.42,1.25,0.2],[0.55,1.32,-0.1]]){ const s=new THREE.Mesh(new THREE.CapsuleGeometry(0.04,0.14,4,10),sm); s.scale.set(1,0.25,1); s.rotation.set(Math.PI/2,0,r); s.position.set(x,0.012,z); s.castShadow=true; scene.add(s); } }
// sunlight through the window: the stage spot already acts as the sun (shadows); add a warm room fill and a cool bounce
{ const fill=new THREE.DirectionalLight(0xfff0e0,0.9); fill.position.set(1.5,2.5,5); fill.target.position.set(0,0.8,0.4); scene.add(fill,fill.target);
  const bounce=new THREE.PointLight(0xffd9b0,3.0,6,1.6); bounce.position.set(0.2,2.6,1.4); scene.add(bounce); }

// ================================================================== HALLWAY (outside the door) at x offset HX
const HX=12;
const hallWall=new THREE.MeshStandardMaterial({color:0xffffff,map:wallTex('#f3df9a',7),roughness:0.95});
const HDOOR={x:HX+1.3,z0:0.25,z1:1.09,y1:2.12};    // his door, on the right-hand wall (plane x=HDOOR.x), seen from the hall side
boxE(HX-3,HX+1.3,0,3.4,-0.14,0,hallWall);
boxE(HDOOR.x,HDOOR.x+0.14,0,3.4,-0.14,HDOOR.z0,hallWall); boxE(HDOOR.x,HDOOR.x+0.14,0,3.4,HDOOR.z1,4,hallWall); boxE(HDOOR.x,HDOOR.x+0.14,HDOOR.y1,3.4,HDOOR.z0,HDOOR.z1,hallWall);
boxE(HX-3,HX+1.3,0,0.09,0,0.015,skirtM);
const hdoorG=new THREE.Group(); hdoorG.position.set(HDOOR.x+0.02,0,HDOOR.z0); scene.add(hdoorG);
{ const dm=woodM(0x8a5532,9); box(0.045,HDOOR.y1-0.01,HDOOR.z1-HDOOR.z0-0.01,dm,0,HDOOR.y1/2,(HDOOR.z1-HDOOR.z0)/2,hdoorG);
  for(const [y0,y1] of [[0.18,0.95],[1.1,1.95]]) box(0.02,y1-y0,0.6,std(0x9a6038,{r:0.45}),-0.03,(y0+y1)/2,(HDOOR.z1-HDOOR.z0)/2,hdoorG);
  const brass=std(0xd9a441,{r:0.25,m:0.7}); box(0.03,0.12,0.035,brass,-0.045,1.0,0.72,hdoorG);
  // auspicious mango-leaf toran over the door frame for the festival
  const t=0.07; boxE(HDOOR.x-0.04,HDOOR.x,0,HDOOR.y1+t,HDOOR.z0-t,HDOOR.z0,trimM); boxE(HDOOR.x-0.04,HDOOR.x,0,HDOOR.y1+t,HDOOR.z1,HDOOR.z1+t,trimM); boxE(HDOOR.x-0.04,HDOOR.x,HDOOR.y1,HDOOR.y1+t,HDOOR.z0-t,HDOOR.z1+t,trimM);
  const leaf=std(0x3f8f3a,{r:0.6}), mari=std(0xffa21a,{r:0.6,x:{emissive:0x803000,emissiveIntensity:0.2}});
  for(let k=0;k<9;k++){ const z=lerp(HDOOR.z0-0.02,HDOOR.z1+0.02,k/8); const l=new THREE.Mesh(new THREE.SphereGeometry(1,10,8),leaf); l.scale.set(0.012,0.08,0.025); l.position.set(HDOOR.x-0.06,HDOOR.y1-0.06,z); scene.add(l);
    if(k%2===0){ const f=new THREE.Mesh(new THREE.SphereGeometry(0.028,10,8),mari); f.position.set(HDOOR.x-0.06,HDOOR.y1+0.0,z); scene.add(f);} } }
// back wall dressing: framed photo with marigold garland, switchboard, wooden shelf with the Nagula Panchami puja (snake idol, milk)
{ const ph=canvasTex(240,300,(g,w,h)=>{ g.fillStyle='#6a3a1a'; g.fillRect(0,0,w,h); g.fillStyle='#f6e2b8'; g.fillRect(16,16,w-32,h-32); g.fillStyle='#c98a3a'; g.beginPath(); g.ellipse(w/2,h/2-10,60,80,0,0,7); g.fill(); g.fillStyle='#8a5a2a'; g.beginPath(); g.arc(w/2,h/2-50,30,0,7); g.fill(); g.fillRect(w/2-50,h/2+20,100,90); });
  const m=plane(0.4,0.5,new THREE.MeshStandardMaterial({map:ph,roughness:0.5}),HX+0.1,1.85,0.015); m.castShadow=true;
  const mari=std(0xff9a1a,{r:0.6,x:{emissive:0x7a3000,emissiveIntensity:0.2}});
  for(let k=0;k<=14;k++){ const u=k/14; const x=HX+0.1+lerp(-0.2,0.2,u), y=2.1-Math.sin(u*Math.PI)*0.36; const f=new THREE.Mesh(new THREE.SphereGeometry(0.026,10,8),k%3===1?std(0xfff1d0):mari); f.position.set(x,y,0.05); scene.add(f); }
  boxE(HX+0.95,HX+1.2,1.2,1.38,0,0.02,std(0xf8f6f0,{r:0.4})); for(let k=0;k<3;k++) boxE(HX+0.98+k*0.08,HX+1.02+k*0.08,1.27,1.32,0.02,0.03,std(0x333333));
  const sh=woodM(0x7a4a2e,15); boxE(HX-0.40,HX+0.60,0.95,0.99,0,0.26,sh); boxE(HX-0.35,HX-0.32,0.75,0.95,0,0.2,sh); boxE(HX+0.52,HX+0.55,0.75,0.95,0,0.2,sh);
  const gold=std(0xd9a441,{r:0.3,m:0.6}); const plate=new THREE.Mesh(new THREE.CylinderGeometry(0.17,0.15,0.02,32),gold); plate.position.set(HX+0.10,1.0,0.13); scene.add(plate);
  const snake=new THREE.Mesh(new THREE.TorusKnotGeometry(0.04,0.012,64,8,2,3),std(0x3a5a3a,{r:0.4,m:0.2})); snake.position.set(HX+0.03,1.06,0.13); snake.rotation.x=Math.PI/2; scene.add(snake);
  const hood=new THREE.Mesh(new THREE.SphereGeometry(1,16,10),std(0x3a5a3a,{r:0.4,m:0.2})); hood.scale.set(0.035,0.05,0.012); hood.position.set(HX+0.03,1.13,0.14); scene.add(hood);
  const milk=new THREE.Mesh(new THREE.CylinderGeometry(0.03,0.025,0.07,16),std(0xc8c8d0,{r:0.25,m:0.8})); milk.position.set(HX+0.21,1.045,0.13); scene.add(milk);
  const mk=new THREE.Mesh(new THREE.CylinderGeometry(0.027,0.027,0.005,16),std(0xffffff,{r:0.3})); mk.position.set(HX+0.21,1.078,0.13); scene.add(mk);
  for(let k=0;k<6;k++){ const f=new THREE.Mesh(new THREE.SphereGeometry(0.018,8,6),k%2?std(0xff9a1a):std(0xd8203a)); f.position.set(HX+0.10+Math.cos(k)*0.12,1.02,0.13+Math.sin(k)*0.08); scene.add(f); }
  const lamp=new THREE.Mesh(new THREE.SphereGeometry(1,16,8,0,Math.PI*2,Math.PI/2,Math.PI/2),gold); lamp.scale.set(0.035,0.02,0.035); lamp.position.set(HX+0.35,1.035,0.13); scene.add(lamp);
  const flame=SLD.glowSprite(scene,0xffb040,0.9); flame.position.set(HX+0.35,1.07,0.15); flame.scale.setScalar(0.07);
  // a plant pot and a shoe rack to fill the lower frame
  const pot=new THREE.Mesh(new THREE.CylinderGeometry(0.16,0.12,0.32,24),std(0xb5552e,{r:0.7})); pot.position.set(HX-0.2,0.16,0.35); pot.castShadow=true; scene.add(pot);
  for(let k=0;k<8;k++){ const l=new THREE.Mesh(new THREE.SphereGeometry(1,10,8),std(0x3f8f3a,{r:0.6})); l.scale.set(0.04,0.28,0.09); l.position.set(HX-0.2+Math.cos(k*0.8)*0.07,0.55,0.35+Math.sin(k*0.8)*0.07); l.rotation.set(Math.sin(k)*0.5,k*0.8,Math.cos(k*1.7)*0.5); l.castShadow=true; scene.add(l); } }
{ const hs=new THREE.SpotLight(0xfff0d8,15,0,0.75,0.6,0.6); hs.position.set(HX-1.6,3.0,2.6); hs.target.position.set(HX+0.3,0.6,0.5); hs.castShadow=true; hs.shadow.mapSize.set(1024,1024); hs.shadow.bias=-0.0004; hs.shadow.camera.near=0.5; hs.shadow.camera.far=8; scene.add(hs,hs.target);
  const hf=new THREE.PointLight(0xffe6c0,3.0,6,1.5); hf.position.set(HX-0.2,2.5,1.6); scene.add(hf); }

// ================================================================== characters
const rig=SLD.createRig(scene);
const {L}=rig, LR=rig.LIMB/2;
const SKIN=0xb9784c;
const hero=rig.makeFig(SKIN,'hero',{rim:0.12,lift:0.05});
const uncle=rig.makeFig(SKIN,'uncle',{rim:0.12,lift:0.05});
const clothM=(c,r=0.85,key='c')=>rimify(new THREE.MeshStandardMaterial({color:c,roughness:r}),0xfff1d8,0.08,key);
const unitCyl=new THREE.CylinderGeometry(1,1,1,20,1,false), unitSph=new THREE.SphereGeometry(1,24,16);
const mesh=(g,m,parent=scene)=>{ const x=new THREE.Mesh(g,m); x.castShadow=true; x.receiveShadow=true; x.frustumCulled=false; parent.add(x); return x; };
function boneM(m,a,b,r,rz=r){ const d=b.clone().sub(a); const len=Math.max(d.length(),1e-4); m.position.copy(a).add(b).multiplyScalar(0.5); m.scale.set(r,len,rz); m.quaternion.setFromUnitVectors(SLD.UPV,d.multiplyScalar(1/len)); }
const along=(a,b,u)=>a.clone().lerp(b,u);
// clothing: shirt (torso + shoulder cap + sleeves), lower (shorts or lungi), optional belly
function makeOutfit(o){ const sh=clothM(o.shirt,0.85,o.key+'s'), lo=clothM(o.lower,0.9,o.key+'l');
  const C={o,torso:mesh(unitCyl,sh),cap:mesh(unitSph,sh),waist:mesh(unitSph,sh),slL:mesh(unitCyl,sh),slR:mesh(unitCyl,sh),jL:mesh(unitSph,sh),jR:mesh(unitSph,sh)};
  if(o.collar) C.collar=mesh(new THREE.TorusGeometry(1,0.35,8,20),clothM(o.collar,0.7,o.key+'k'));
  if(o.lungi){ C.lungi=mesh(new THREE.CylinderGeometry(0.92,1.0,1,24,1,false),lo); C.lband=mesh(new THREE.CylinderGeometry(1,1,1,24,1,true),clothM(0x2a5a9a,0.8,o.key+'b')); }
  else { C.thL=mesh(unitCyl,lo); C.thR=mesh(unitCyl,lo); C.pelvis=mesh(unitSph,lo); }
  if(o.belly) C.belly=mesh(unitSph,sh);
  return C; }
function dressOutfit(C,J,fw){ const o=C.o, r=o.r;
  const up=J.neck.clone().sub(J.hip).normalize();
  const top=J.neck.clone().addScaledVector(up,-0.06), bot=J.hip.clone().addScaledVector(up,-0.03);
  boneM(C.torso,bot,top,r,r*0.82);
  C.cap.position.copy(top); C.cap.scale.set(r*1.02,r*0.55,r*0.86); C.cap.quaternion.copy(C.torso.quaternion);
  C.waist.position.copy(bot); C.waist.scale.set(r*1.0,r*0.45,r*0.84); C.waist.quaternion.copy(C.torso.quaternion);
  // shoulders: torso rotation about the spine follows the shoulder line
  const sl=J.shL.clone().sub(J.shR); sl.addScaledVector(up,-sl.dot(up)).normalize();
  const q=new THREE.Quaternion().setFromUnitVectors(SLD.UPV,up); const zx=V(0,0,1).applyQuaternion(q); const ang=Math.atan2(zx.clone().cross(sl).dot(up),zx.dot(sl));
  const qa=new THREE.Quaternion().setFromAxisAngle(up,ang); [C.torso,C.cap,C.waist].forEach(m=>m.quaternion.premultiply(qa));
  const slv=o.sleeve??0.55;
  boneM(C.slL,J.shL,along(J.shL,J.elL,slv),LR*1.75); boneM(C.slR,J.shR,along(J.shR,J.elR,slv),LR*1.75);
  C.jL.position.copy(J.shL); C.jL.scale.setScalar(LR*1.8); C.jR.position.copy(J.shR); C.jR.scale.setScalar(LR*1.8);
  if(C.collar){ C.collar.position.copy(J.neck).addScaledVector(up,-0.035); C.collar.scale.setScalar(0.055); C.collar.quaternion.setFromUnitVectors(V(0,0,1),up); }
  if(C.belly){ C.belly.position.copy(along(bot,top,0.32)).addScaledVector(fw,r*0.42); C.belly.scale.set(r*0.95,r*1.05,r*0.9); C.belly.quaternion.copy(C.torso.quaternion); }
  if(C.lungi){ const fm=J.fL.clone().add(J.fR).multiplyScalar(0.5); const a=J.hip.clone().addScaledVector(up,0.03), b=V(fm.x,Math.max(fm.y,0)+0.09,fm.z);
    const spread=Math.max(0.17,J.fL.distanceTo(J.fR)*0.55+0.08);
    boneM(C.lungi,b,a,r*1.02,r*0.88); C.lungi.scale.x=r*1.0; C.lungi.geometry.parameters; // top radius r, bottom flares (geometry)
    C.lungi.scale.set(r*1.3,a.distanceTo(b),r*1.1);
    boneM(C.lband,a.clone().addScaledVector(up,-0.03),a.clone().addScaledVector(up,0.02),r*1.04,r*0.9); C.lband.quaternion.copy(C.torso.quaternion); }
  else { const mid=(a,b)=>along(a,b,0.62);
    boneM(C.thL,J.hipL.clone().addScaledVector(up,0.02),mid(J.hipL,J.kL),LR*1.9); boneM(C.thR,J.hipR.clone().addScaledVector(up,0.02),mid(J.hipR,J.kR),LR*1.9);
    C.pelvis.position.copy(J.hip); C.pelvis.scale.set(r*0.98,r*0.6,r*0.82); C.pelvis.quaternion.copy(C.torso.quaternion); } }
// head accessories live in a head frame: +x face forward, +y up the head, +z the figure's local +z side
function headFrame(P,yaw){ const hd=P.p+P.tilt; const f=SLD.rotY(SLD.rotY(SLD.rotY(V(Math.cos(hd),-Math.sin(hd),0),P.hy),P.ty),yaw); const u=SLD.rotY(SLD.rotY(SLD.rotY(V(Math.sin(hd),Math.cos(hd),0),P.hy),P.ty),yaw); const z=f.clone().cross(u);
  return new THREE.Matrix4().makeBasis(f,u,z); }
const onSphere=(R,th,ph)=>V(Math.cos(ph)*Math.cos(th)*R,Math.sin(ph)*R,Math.sin(th)*Math.cos(ph)*R);
// hero head: curly hair, stubble beard, black wayfarer goggles
const heroHead=new THREE.Group(); scene.add(heroHead);
{ const hairM=clothM(0x1c1410,0.95,'hair'), beardM=clothM(0x2a201a,0.98,'beard'); const R=rng(11); const HR=L.head;
  for(let i=0;i<150;i++){ const th=R()*Math.PI*2, ph=Math.asin(R()*2-1); const p=onSphere(1,th,ph); // th=0 is +x (face)
    const front=p.x>0.25, top=p.y>0.32, back=p.x<-0.05&&p.y>-0.55;
    if(top&&(p.x<0.72||p.y>0.45)||back||(Math.abs(p.z)>0.7&&p.y>0.05&&p.x<0.45)){ const s=mesh(unitSph,hairM,heroHead); const rr=0.03+R()*0.016; s.position.copy(p.multiplyScalar(HR*0.97)); s.scale.setScalar(rr); }
    else if(p.y<-0.18&&p.x>0.0&&!(p.y>-0.42&&Math.abs(p.z)<0.32&&p.x>0.85)){ const s=mesh(unitSph,beardM,heroHead); s.position.copy(p.multiplyScalar(HR*0.95)); s.scale.setScalar(0.024+R()*0.008); } }
  // mouth gap (beard) is left open on the front; goggles
  const gl=new THREE.MeshPhysicalMaterial({color:0x07080a,roughness:0.08,metalness:0.2,clearcoat:1,clearcoatRoughness:0.05});
  const fr=new THREE.MeshStandardMaterial({color:0x0c0c0e,roughness:0.35});
  for(const s of [-1,1]){ const lens=mesh(new THREE.BoxGeometry(0.018,0.06,0.088,1,2,2),gl,heroHead); lens.position.set(HR*0.93,0.022,s*0.052); lens.rotation.y=-s*0.22;
    const rimT=mesh(new THREE.BoxGeometry(0.024,0.016,0.096),fr,heroHead); rimT.position.set(HR*0.94,0.054,s*0.052); rimT.rotation.y=-s*0.22;
    const tmp=mesh(new THREE.BoxGeometry(0.15,0.012,0.008),fr,heroHead); tmp.position.set(HR*0.42,0.045,s*(HR*0.98)); tmp.rotation.y=s*0.06;
    const glint=new THREE.Mesh(new THREE.PlaneGeometry(0.012,0.05),new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:0.55,depthWrite:false})); glint.position.set(HR*0.93+0.011,0.03,s*0.052-0.02); glint.rotation.set(0,Math.PI/2-s*0.22,0.6); heroHead.add(glint); }
  const br=mesh(new THREE.BoxGeometry(0.014,0.012,0.03),fr,heroHead); br.position.set(HR*1.0,0.04,0); }
// uncle head: bald, thick moustache with curled ends, heavy eyebrows (raised for sarcasm)
const uncleHead=new THREE.Group(); scene.add(uncleHead);
const browL=new THREE.Group(), browR=new THREE.Group();
{ const HR=L.head, mm=clothM(0x111111,0.9,'must');
  for(const s of [-1,1]){ for(let k=0;k<7;k++){ const u=k/6; const th=s*(0.08+u*0.62), ph=-0.33+u*u*0.12+(u>0.8?(u-0.8)*1.8:0); const p=onSphere(HR*1.0,th,ph); const m=mesh(unitSph,mm,uncleHead); m.position.copy(p); m.scale.set(0.022,0.024-u*0.008,0.03-u*0.012); }
    const g=s<0?browL:browR; uncleHead.add(g); const b=mesh(new THREE.CapsuleGeometry(0.012,0.055,4,8),mm,g); b.rotation.x=Math.PI/2; b.position.set(0,0,0); g.position.copy(onSphere(HR*0.99,s*0.36,0.3)); g.rotation.y=-s*0.36; }
  // shine on the bald head
  const sh=new THREE.Mesh(new THREE.SphereGeometry(1,16,10),new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:0.35,depthWrite:false})); sh.scale.set(0.03,0.018,0.045); sh.position.copy(onSphere(HR*1.0,0.2,0.85)); uncleHead.add(sh); }
const heroOut=makeOutfit({key:'h',r:0.105,shirt:0x34383f,lower:0x2b3f66,sleeve:0.5});
const uncleOut=makeOutfit({key:'u',r:0.13,shirt:0xe6e2d6,lower:0xf2efe6,lungi:true,belly:true,collar:0x2fb8c8,sleeve:0.6});
// lungi checks
{ const lt=canvasTex(256,256,(g,w,h)=>{ g.fillStyle='#f4f1e8'; g.fillRect(0,0,w,h); g.fillStyle='rgba(40,90,170,0.55)'; for(let k=0;k<w;k+=64){ g.fillRect(k,0,8,h); g.fillRect(0,k,w,8);} g.fillStyle='rgba(40,90,170,0.25)'; for(let k=24;k<w;k+=64){ g.fillRect(k,0,3,h); g.fillRect(0,k,w,3);} g.fillStyle='rgba(30,70,150,0.7)'; g.fillRect(0,h-26,w,18); });
  lt.wrapS=lt.wrapT=THREE.RepeatWrapping; lt.repeat.set(3,1); uncleOut.lungi.material.map=lt; uncleOut.lungi.material.needsUpdate=true; }
// shirt pocket + buttons on uncle (on the torso mesh, local)
{ const t=uncleOut.torso; const pm=clothM(0xeceae2,0.85,'pk'); const p=mesh(new THREE.BoxGeometry(0.28,0.22,0.06),pm,t); p.position.set(0.8,0.18,0.45); p.scale.set(1/1,1,1); p.visible=false; }

function placeHead(G,J,P,yaw){ G.position.copy(J.head); G.quaternion.setFromRotationMatrix(headFrame(P,yaw)); }
function poseHero(P,root,yaw){ const J=rig.skel(P,root,yaw); rig.poseFig(hero,J); dressOutfit(heroOut,J,J.fwd); placeHead(heroHead,J,P,yaw); return J; }
function poseUncle(P,root,yaw,brow=0){ const J=rig.skel(P,root,yaw); rig.poseFig(uncle,J); dressOutfit(uncleOut,J,J.fwd); placeHead(uncleHead,J,P,yaw);
  browL.position.y=uncleHead.userData.by??browL.position.y; for(const g of [browL,browR]){ g.userData.y0??=g.position.y; g.position.y=g.userData.y0+0.018*brow; } browL.rotation.x=0.25*brow; browR.rotation.x=-0.25*brow; return J; }

// ================================================================== animation
// dialogue (seconds, from the clip): uncle "Office endhukoni?" 0.82-1.50 (through the door) | hero "Nagula Panchami iyyala" 3.38-4.26
// | "Aa?" 4.78, "Nagula Panchami" 5.24-5.94 | uncle "...atla kooda istarra mee office lo?" 6.70-8.78 | hero "Maa office lo istaru" 9.10-9.92
// | uncle mocking echo 10.26-11.08 | uncle "Maaku teledu mari, memu chaduvukole" 11.50-12.86 | "Ey abba" 13.38-13.96
const BANGS=[0.0,0.27,0.52];
const bangAmt=t=>{ let a=0; for(const b of BANGS){ const u=t-b; if(u>=0&&u<0.35) a+=Math.exp(-u/0.07)*Math.sin(u*90); } return a; };
const HROOT=V(-0.4,BED.top,1.02), HYAW=SLD.yawOf(V(0.32,0,1));
const heroBase={...rig.P0,p:-0.5,tilt:0.42,hy:0,ty:0,aL:1.52,kL:0.12,aR:1.45,kR:0.18,dy:-0.1,sL:0.3,sR:0.3,eL:0.6,eR:0.6};
function heroPose(t){
  const P={...heroBase};
  // head: toward the door on the bangs/voice, back to camera; chin up on his answers
  P.hy=keys([[0,0.15],[0.25,0.75],[1.6,0.75],[2.2,0.2],[3.2,0.25],[3.45,0.6],[4.4,0.55],[8.8,0.45],[9.05,0.15],[9.9,0.05],[10.3,0.55],[11.1,0.6],[13.05,0.5],[13.4,0.7],[14.2,0.6]],t);
  P.tilt=heroBase.tilt+keys([[0,0],[3.3,0],[3.55,-0.12],[4.3,-0.05],[9.0,0],[9.2,-0.16],[9.95,-0.1],[10.4,0.05],[11.1,0.12],[13.05,0.1],[13.4,-0.25],[14.2,-0.3]],t);
  P.p=heroBase.p+keys([[0,0],[8.8,0],[9.1,0.42],[10.0,0.38],[10.4,0.3],[11.2,0.28],[13.05,0.28],[13.45,-0.12],[14.2,-0.08]],t);
  // head bob while he talks
  const talk=(a,b)=>t>a&&t<b?Math.sin((t-a)*16)*0.04*sstep(a,a+0.1,t)*(1-sstep(b-0.1,b,t)):0;
  P.tilt+=talk(3.38,4.26)+talk(9.1,9.92)+talk(13.38,13.96);
  return P; }
function heroHands(P,t,J0){
  // targets in world space, computed from a first skeleton pass (hands behind the head = chill)
  const F=headFrame(P,HYAW); const f=V(),u=V(),z=V(); F.extractBasis(f,u,z);
  const behind=s=>J0.head.clone().addScaledVector(f,-0.11).addScaledVector(z,s*0.12).addScaledVector(u,0.02);
  const goggles=J0.head.clone().addScaledVector(f,0.17).addScaledVector(u,0.03).addScaledVector(z,0.03);
  const chest=J0.neck.clone().addScaledVector(f,0.15).addScaledVector(u,-0.14);
  const towardDoor=J0.neck.clone().add(V(0.42,0.05,-0.12));
  const lap=J0.hip.clone().addScaledVector(J0.fwd,0.25).add(V(0,0.06,0));
  const T={};
  // right-of-screen hand ('L' rig side here is world -x... we pick per side by name)
  const wa=keys([[0,1],[1.5,1],[1.75,0],[2.9,0],[3.1,0],[3.3,0],[4.35,0],[4.6,1],[8.8,1],[8.95,1],[9.1,0],[11.2,0],[13.05,0.2],[13.5,1],[14.2,1]],t); // hand A behind head
  const wb=keys([[0,1],[3.2,1],[3.45,0],[4.35,0],[4.6,1],[8.8,1],[9.0,0],[12.9,0],[13.05,0.2],[13.5,1],[14.2,1]],t);
  // hand A: goggles push 1.75-2.9, then behind head
  const gogA=sstep(1.5,1.85,t)*(1-sstep(2.6,2.95,t));
  const tA=behind(1).lerp(goggles.clone().addScaledVector(u,-0.02*Math.sin(Math.max(0,t-1.85)*8)),gogA);
  // hand B: open palm toward the door on "Nagula Panchami iyyala" 3.4-4.3
  const doorB=sstep(3.2,3.5,t)*(1-sstep(4.2,4.55,t));
  // H2: hand A taps chest "MAA office" 9.1-9.9, then rests on lap; hand B on lap
  const chestA=sstep(8.9,9.15,t)*(1-sstep(10.0,10.35,t));
  const lapA=sstep(9.9,10.35,t)*(1-sstep(13.05,13.3,t)), lapB=sstep(8.8,9.05,t)*(1-sstep(13.05,13.3,t));
  let A=tA, B=behind(-1);
  if(doorB>0) B=B.clone().lerp(towardDoor,doorB);
  if(chestA>0) A=A.clone().lerp(chest.clone().addScaledVector(f,0.03*Math.abs(Math.sin((t-9.1)*11))),chestA);
  if(lapA>0) A=A.clone().lerp(lap.clone().addScaledVector(z,0.12),lapA);
  if(lapB>0) B=B.clone().lerp(lap.clone().addScaledVector(z,-0.12),lapB);
  const wA=Math.max(wa,gogA,chestA,lapA,1), wB=1;
  return {...P,tL:A,tR:B,wL:wA,wR:wB,pL:V(-0.3,0.4,1.0),pR:V(-0.3,0.4,-1.0)}; }

const UROOT0=V(HX+0.62,0,0.66);
function unclePose(t){
  // U1: last bang with the fist (4.5-4.7), leans in "Aa?" (4.78), straightens, turns to us half-way for the sarcastic line, hands on hips
  // U2: palms up "maaku teledu mari", hand on chest "memu chaduvukole", shakes head
  const P={...rig.P0,p:0.06,sL:0.1,sR:-0.05,eL:0.3,eR:0.3};
  const turn=keys([[4.5,0],[6.4,0],[6.9,0.75],[8.8,0.8],[11.2167,0.95],[13.05,1.0]],t);
  const yaw=lerp(0,-1.6,turn);   // 0 = facing the door (+x); +0.95 turns his face toward camera (+z)
  P.p=0.06+keys([[4.5,0.04],[4.75,0.16],[5.1,0.14],[5.3,0.02],[6.6,0.02],[8.8,0.05],[11.2,0.0],[12.2,0.0],[12.4,0.1],[12.9,0.06]],t);
  P.tilt=keys([[4.5,0],[4.75,0.12],[5.2,0.05],[5.6,-0.12],[6.5,-0.05],[7.4,0.08],[8.8,0.05],[11.3,-0.05],[12.3,0.0],[12.5,0.15],[13.05,0.1]],t);
  const wob=(a,b,f=9,amp=0.18)=>t>a&&t<b?Math.sin((t-a)*f)*amp*sstep(a,a+0.15,t)*(1-sstep(b-0.15,b,t)):0;   // Indian head wobble
  P.hy=keys([[4.5,0],[6.6,0],[7.0,0.25],[8.8,0.3],[11.2,0.3],[13.05,0.3]],t)+wob(6.7,8.8,10,0.16)+wob(11.5,12.9,8,0.14);
  P.ty=wob(6.7,8.8,5,0.06);
  return {P,yaw}; }
function uncleHands(P,t,yaw,J0){ const f=J0.fwd, side=SLD.rotY(V(0,0,1),yaw);
  const hipL=J0.hip.clone().addScaledVector(side,0.2).addScaledVector(f,0.02).add(V(0,0.04,0)), hipR=J0.hip.clone().addScaledVector(side,-0.2).addScaledVector(f,0.02).add(V(0,0.04,0));
  const fistUp=J0.neck.clone().addScaledVector(f,0.32).addScaledVector(side,-0.1).add(V(0,0.12,0));
  const knock=J0.neck.clone().addScaledVector(f,0.5).addScaledVector(side,-0.12).add(V(0,0.05,0));
  const ear=J0.head.clone().addScaledVector(side,-0.15).addScaledVector(f,0.02);
  const palm=s=>J0.neck.clone().addScaledVector(f,0.36).addScaledVector(side,s*0.22).add(V(0,-0.22,0));
  const chest=J0.neck.clone().addScaledVector(f,0.14).add(V(0,-0.15,0));
  const point=J0.neck.clone().addScaledVector(f,0.15).addScaledVector(side,-0.38).add(V(0,0.0,0));
  let A=hipR, B=hipL;   // A = his door-side hand
  const k1=sstep(4.5,4.6,t)*(1-sstep(4.62,4.75,t)); A=A.clone().lerp(fistUp,1-sstep(4.55,4.9,t)).lerp(knock,k1*0.6);
  const earW=sstep(4.75,4.95,t)*(1-sstep(5.6,5.9,t)); A=A.lerp(ear,earW);
  const hipW=sstep(5.8,6.3,t);   // hands on hips for the sarcastic line, door hand points at the door on "mee office lo"
  B=B.clone();
  const pt=sstep(7.9,8.1,t)*(1-sstep(8.75,8.8,t)); A=A.lerp(point,pt);
  if(t>=11.2167){ A=hipR.clone(); B=hipL.clone(); const pu=sstep(11.25,11.5,t)*(1-sstep(12.1,12.3,t)); A.lerp(palm(-1),pu); B.lerp(palm(1),pu);
    const ch=sstep(12.15,12.35,t); A.lerp(chest,ch); B.lerp(hipL,0); }
  return {...P,tL:B,tR:A,wL:1,wR:1,pL:V(-0.4,-0.2,1),pR:V(-0.4,-0.2,-1)}; }

let META={shot:'H1'};
function setT(T){
  const [shot,t0,t1]=shotAt(T); META.shot=shot; const room=shot[0]==='H';
  const b=bangAmt(T);
  doorG.rotation.y=-0.012*b; doorG.position.z=-0.02+0.006*b; hdoorG.rotation.z=0; hdoorG.position.x=HDOOR.x+0.02+0.004*bangAmt(T-4.5+0.0);
  // hero
  const P0=heroPose(T); const J0=rig.skel(P0,HROOT,HYAW); poseHero(heroHands(P0,T,J0),HROOT,HYAW);
  // uncle
  const {P,yaw}=unclePose(T); const ur=UROOT0.clone(); const UY=SLD.yawOf(V(1,0,-0.15))+yaw; const J1=rig.skel(P,ur,UY);
  const brow=keys([[4.5,0],[4.75,1],[5.2,0.4],[6.6,0.3],[6.9,1],[8.8,1],[11.2,0.6],[11.5,1],[13.05,0.8]],T);
  poseUncle(uncleHands(P,T,UY,J1),ur,UY,brow);
  // cameras
  const u=(T-t0)/(t1-t0);
  if(shot==='H1'){ // opens wide on the room (door rattling), pushes in on the hero
    const a=sm(sstep(0,4.5,T));
    cam.position.set(lerp(0.15,-0.05,a),lerp(1.32,1.18,a),lerp(3.6,2.75,a)); cam.lookAt(lerp(0.12,-0.3,a),lerp(1.08,0.98,a),lerp(0.5,0.8,a)); cam.fov=lerp(58,46,a);
    }
  else if(shot==='H2'){ cam.position.set(lerp(-0.1,-0.15,u),lerp(1.12,1.1,u),lerp(2.45,2.3,u)); cam.lookAt(-0.38,1.0,0.85); cam.fov=44; }
  else if(shot==='H3'){ cam.position.set(lerp(0.2,0.25,u),lerp(1.22,1.26,u),lerp(2.95,3.1,u)); cam.lookAt(-0.12,1.0,0.6); cam.fov=48; }
  else if(shot==='U1'){ cam.position.set(HX+lerp(0.3,0.42,u),lerp(1.42,1.4,u),lerp(2.85,2.55,u)); cam.lookAt(HX+0.72,1.36,0.6); cam.fov=48; }
  else { cam.position.set(HX+lerp(0.5,0.52,u),1.45,lerp(2.3,2.15,u)); cam.lookAt(HX+0.72,1.42,0.65); cam.fov=46; }
  cam.updateProjectionMatrix();
  S.tick(T);
}
function sm(x){ return x*x*(3-2*x); }
const events=BANGS.map(t=>({t,type:'bang'}));
setT(0);
window.metaAt=t=>{ setT(t); return {shot:META.shot}; };
window.events=events;
window.renderAt=(t,K)=>{ const [,a,b]=shotAt(t); return S.renderAt(setT,t,K,{t0:a,t1:b}); };
for(const T of [0.5,5,9,12,13.5]) S.renderAt(setT,T,1,{t0:0,t1:DUR}); S.renderAt(setT,0,1,{t0:0,t1:4.5});
window.ready=true;
