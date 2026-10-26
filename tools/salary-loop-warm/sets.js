// Lived-in sets for The Salary Loop (procedural props, warm practical lights). Each builder returns a Group centred at x=0, floor y=0, back wall near z=-2.2.
import * as THREE from 'three';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';
export const V=(x,y,z)=>new THREE.Vector3(x,y,z);
const mats=new Map();
export function M(color,{r=0.7,m=0,e=0,ei=0,map=null,t=false,o=1}={}){ const k=[color,r,m,e,ei,map&&map.uuid,t,o].join('|'); if(!mats.has(k)) mats.set(k,new THREE.MeshStandardMaterial({color,roughness:r,metalness:m,emissive:e,emissiveIntensity:ei,map,transparent:t||o<1,opacity:o})); return mats.get(k); }
export const B=(p,w,h,d,mat,x=0,y=0,z=0,{ry=0,rx=0,rz=0,round=0,cast=true}={})=>{ const g=round?new RoundedBoxGeometry(w,h,d,3,round):new THREE.BoxGeometry(w,h,d); const m=new THREE.Mesh(g,mat); m.position.set(x,y,z); m.rotation.set(rx,ry,rz); m.castShadow=cast; m.receiveShadow=true; p.add(m); return m; };
export const C=(p,rt,rb,h,mat,x=0,y=0,z=0,{rx=0,rz=0,seg=18,cast=true}={})=>{ const m=new THREE.Mesh(new THREE.CylinderGeometry(rt,rb,h,seg),mat); m.position.set(x,y,z); m.rotation.set(rx,0,rz); m.castShadow=cast; m.receiveShadow=true; p.add(m); return m; };
export const S=(p,r,mat,x=0,y=0,z=0,{sx=1,sy=1,sz=1,cast=true}={})=>{ const m=new THREE.Mesh(new THREE.SphereGeometry(r,20,14),mat); m.position.set(x,y,z); m.scale.set(sx,sy,sz); m.castShadow=cast; m.receiveShadow=true; p.add(m); return m; };
export const P=(p,w,h,mat,x=0,y=0,z=0,{ry=0,rx=0}={})=>{ const m=new THREE.Mesh(new THREE.PlaneGeometry(w,h),mat); m.position.set(x,y,z); m.rotation.set(rx,ry,0); m.receiveShadow=true; p.add(m); return m; };
const rng=(seed)=>{ let s=seed>>>0; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; };
function canvasTex(w,h,fn,{repeat=null}={}){ const c=document.createElement('canvas'); c.width=w; c.height=h; const g=c.getContext('2d'); fn(g,w,h); const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; t.anisotropy=4; if(repeat){ t.wrapS=t.wrapT=THREE.RepeatWrapping; t.repeat.set(...repeat); } return t; }
export const woodTex=(base='#8a5a36',repeat=[4,4])=>canvasTex(256,256,(g,w,h)=>{ g.fillStyle=base; g.fillRect(0,0,w,h); const R=rng(3); for(let i=0;i<14;i++){ g.fillStyle=`rgba(${R()<0.5?'40,22,10':'255,220,170'},${0.05+R()*0.07})`; g.fillRect(0,i*(h/14),w,h/14-1.5); } g.strokeStyle='rgba(20,10,4,0.4)'; g.lineWidth=2; for(let i=0;i<14;i++){ g.beginPath(); g.moveTo(0,i*(h/14)); g.lineTo(w,i*(h/14)); g.stroke(); const x=R()*w; g.beginPath(); g.moveTo(x,i*(h/14)); g.lineTo(x,(i+1)*(h/14)); g.stroke(); } },{repeat});
export const plaidTex=()=>canvasTex(256,256,(g,w,h)=>{ g.fillStyle='#2b3b6a'; g.fillRect(0,0,w,h); for(let i=0;i<4;i++){ g.fillStyle='rgba(120,150,220,0.42)'; g.fillRect(i*64+8,0,22,h); g.fillRect(0,i*64+8,w,22); g.fillStyle='rgba(10,16,40,0.35)'; g.fillRect(i*64+36,0,6,h); g.fillRect(0,i*64+36,w,6); } },{repeat:[3,2]});
export const bokehTex=(warm=true,seed=5,n=70)=>canvasTex(512,512,(g,w,h)=>{ g.fillStyle=warm?'#1b1222':'#0e1722'; g.fillRect(0,0,w,h); const R=rng(seed); const cols=warm?['255,190,110','255,150,80','255,226,160','140,170,255','255,120,100']:['120,170,255','255,200,130','180,220,255']; for(let i=0;i<n;i++){ const x=R()*w,y=R()*h,r=10+R()*34; const gr=g.createRadialGradient(x,y,0,x,y,r); const c=cols[Math.floor(R()*cols.length)]; gr.addColorStop(0,`rgba(${c},0.85)`); gr.addColorStop(0.6,`rgba(${c},0.35)`); gr.addColorStop(1,`rgba(${c},0)`); g.fillStyle=gr; g.beginPath(); g.arc(x,y,r,0,7); g.fill(); } });
export const calendarTex=(circled=6,crossed=0,month='JANUARY')=>canvasTex(512,640,(g,w,h)=>{ g.fillStyle='#f4efe6'; g.fillRect(0,0,w,h); g.fillStyle='#c4452f'; g.fillRect(0,0,w,92); g.fillStyle='#fff'; g.font='bold 54px monospace'; g.textAlign='center'; g.fillText(month,w/2,66);
  g.fillStyle='#3a3530'; g.font='bold 30px monospace'; const cw=64,ch=82; for(let i=0;i<31;i++){ const x=40+(i%7)*cw+cw/2, y=170+Math.floor(i/7)*ch; g.fillText(String(i+1),x,y); if(i<crossed){ g.strokeStyle='#c4452f'; g.lineWidth=6; g.beginPath(); g.moveTo(x-24,y-34); g.lineTo(x+24,y+10); g.moveTo(x+24,y-34); g.lineTo(x-24,y+10); g.stroke(); } }
  if(circled){ const i=circled-1; const x=40+(i%7)*cw+cw/2, y=170+Math.floor(i/7)*ch; g.strokeStyle='#c4452f'; g.lineWidth=7; g.beginPath(); g.ellipse(x,y-10,34,30,0.2,0,7); g.stroke(); } });
function plant(p,x,y,z,s=1,seed=1){ const R=rng(seed); const pot=C(p,0.11*s,0.085*s,0.16*s,M(0xb5562f,{r:0.8}),x,y+0.08*s,z); const lm=M(0x3f8a45,{r:0.7}); for(let i=0;i<9;i++){ const l=S(p,0.075*s,lm,x+(R()-0.5)*0.16*s,y+0.2*s+R()*0.2*s,z+(R()-0.5)*0.16*s,{sx:0.6,sy:1.3,sz:0.6}); l.rotation.set((R()-0.5)*0.8,0,(R()-0.5)*0.8); } return pot; }
function book(p,x,y,z,w,h,d,col){ return B(p,w,h,d,M(col,{r:0.8}),x,y+h/2,z); }
function frame(p,x,y,z,w,h,col,ry=0){ const g=new THREE.Group(); B(g,w,h,0.03,M(0x2a1c12,{r:0.6}),0,0,0); B(g,w*0.82,h*0.82,0.012,M(col,{r:0.9,e:col,ei:0.25}),0,0,0.02); g.position.set(x,y,z); g.rotation.y=ry; p.add(g); return g; }
export function floorAndWalls(g,{wall=0x6f5f58,floor='#8a5a36',w=7,d=5,h=3,backZ=-2.2,leftX=-3.2}={}){ const fl=P(g,w*2,d*2,M(0xffffff,{r:0.55,map:woodTex(floor,[6,6])}),0,0,0,{rx:-Math.PI/2}); const back=P(g,w*2,h,M(wall,{r:0.95}),0,h/2,backZ); const left=P(g,d*2,h,M(wall,{r:0.95}),leftX,h/2,0,{ry:Math.PI/2}); B(g,w*2,0.12,0.04,M(0x3a2a20,{r:0.7}),0,0.06,backZ+0.02); return {fl,back,left}; }

// ---------------------------------------------------------------- 1: the bedroom (hook, reality, the end)
export function buildBedroom(){ const g=new THREE.Group(); floorAndWalls(g,{wall:0x7a6a5e});
  // window with a city at night, curtains
  const win=new THREE.Group(); B(win,1.5,1.5,0.06,M(0x2a1c12,{r:0.5}),0,0,0); const city=P(win,1.36,1.36,new THREE.MeshBasicMaterial({map:bokehTex(true,5,90),fog:false}),0,0,0.04); B(win,0.04,1.5,0.07,M(0x2a1c12),0,0,0.03); B(win,1.5,0.04,0.07,M(0x2a1c12),0,0,0.03); win.position.set(1.7,1.75,-2.17); g.add(win);
  for(const sx of [-1,1]) B(g,0.34,1.9,0.12,M(0x8a3f3a,{r:0.95}),1.7+sx*0.95,1.6,-2.08,{round:0.04});
  // bed with plaid quilt
  const bed=new THREE.Group(); B(bed,2.25,0.32,1.25,M(0x5a3a22,{map:woodTex('#6b4428',[1,1]),r:0.6}),0,0.16,0,{round:0.03}); B(bed,2.1,0.2,1.15,M(0xf2ede4,{r:0.9}),0,0.42,0,{round:0.08}); const quilt=B(bed,1.35,0.3,1.22,M(0xffffff,{r:0.95,map:plaidTex()}),0.42,0.66,0,{round:0.1}); B(bed,0.5,0.15,0.66,M(0xfaf6ee,{r:0.95}),-0.8,0.62,-0.05,{round:0.07}); B(bed,0.45,0.17,0.5,M(0xe8e1d4,{r:0.95}),-0.82,0.74,-0.38,{round:0.07,rx:0.35}); B(bed,0.06,0.7,1.25,M(0x5a3a22,{r:0.6}),-1.14,0.5,0); bed.position.set(-0.2,0,-1.2); g.add(bed); g.userData.bed=bed; g.userData.quilt=quilt;
  // bedside table with warm lamp, clock, plant
  const nt=new THREE.Group(); B(nt,0.55,0.5,0.5,M(0x6b4428,{map:woodTex('#6b4428',[1,1])}),0,0.25,0,{round:0.02}); C(nt,0.015,0.015,0.32,M(0x2a2a2a,{m:0.6}),0,0.66,0); const shade=C(nt,0.1,0.17,0.2,M(0xffe2b0,{e:0xffc06a,ei:1.6,r:0.9}),0,0.9,0,{cast:false}); S(nt,0.06,M(0xfff0c8,{e:0xffd890,ei:3}),0,0.84,0,{cast:false}); B(nt,0.16,0.08,0.06,M(0x222,{r:0.4}),-0.13,0.54,0.12); nt.position.set(-1.95,0,-1.5); g.add(nt); g.userData.lampPos=V(-1.95,0.88,-1.5);
  plant(g,-2.4,0,-1.7,1.25,3);
  // shelf on the wall with books, plants, frames
  const sh=new THREE.Group(); B(sh,1.5,0.05,0.28,M(0x6b4428),0,0,0); B(sh,1.5,0.05,0.28,M(0x6b4428),0,0.55,0); const R=rng(9); const bc=[0xc4452f,0x2f6b8a,0xd9a63a,0x3f8a45,0x7a4a8a,0xe8e1d4]; for(let i=0;i<9;i++) book(sh,-0.62+i*0.075,0.025,0,0.055,0.2+R()*0.1,0.2,bc[i%6]); plant(sh,0.45,0.025,0,0.8,5); plant(sh,0.18,0.58,0,0.65,7); for(let i=0;i<4;i++) book(sh,-0.6+i*0.07,0.58,0,0.05,0.18+R()*0.06,0.2,bc[(i+2)%6]); sh.position.set(-0.9,1.7,-2.05); g.add(sh);
  frame(g,0.3,1.85,-2.17,0.42,0.54,0xd9a63a); frame(g,0.9,2.05,-2.17,0.3,0.4,0x3f8a8a); frame(g,-2.0,2.2,-2.17,0.5,0.35,0xc4452f);
  // wall calendar (changes through the story) and the sticky note (end)
  const cal=new THREE.Mesh(new THREE.PlaneGeometry(0.62,0.78),new THREE.MeshStandardMaterial({map:calendarTex(6,5),roughness:0.9})); cal.position.set(-0.1,1.55,-2.16); g.add(cal); g.userData.cal=cal;
  const note=P(g,0.3,0.3,M(0xffe36b,{r:0.9,e:0xffd24a,ei:0.15}),0.7,1.25,-2.15); g.userData.note=note; note.visible=false;
  // wardrobe, chair with a bag, rug, a pair of shoes
  B(g,1.0,2.2,0.6,M(0x5a3a22,{map:woodTex('#5a3a22',[1,1])}),2.7,1.1,-1.8,{round:0.03}); B(g,0.02,2.0,0.02,M(0x222),2.7,1.1,-1.48);
  B(g,0.5,0.06,0.5,M(0x6b4428),2.0,0.5,0.1); for(const [x,z] of [[-0.2,-0.2],[0.2,-0.2],[-0.2,0.2],[0.2,0.2]]) B(g,0.05,0.5,0.05,M(0x4a3020),2.0+x,0.25,0.1+z); B(g,0.5,0.55,0.06,M(0x6b4428),2.0,0.8,-0.15);
  const bag=B(g,0.42,0.3,0.16,M(0x3a2a1e,{r:0.7}),2.0,0.7,0.12,{round:0.04}); B(g,0.43,0.12,0.17,M(0x4a3626,{r:0.7}),2.0,0.82,0.12,{round:0.04}); g.userData.bag=bag;
  B(g,2.4,0.02,1.6,M(0x3b5a63,{r:1}),-0.2,0.012,0.5,{round:0.01});
  B(g,0.22,0.08,0.1,M(0x15171b),0.6,0.04,0.9); B(g,0.22,0.08,0.1,M(0x15171b),0.85,0.04,0.95,{ry:0.4});
  g.userData.bokeh=city; return g; }

// ---------------------------------------------------------------- shared small props
const warmBulb=(p,x,y,z,s=1)=>{ S(p,0.06*s,M(0xfff0c8,{e:0xffd890,ei:3}),x,y,z,{cast:false}); const w=new THREE.Mesh(new THREE.CylinderGeometry(0.004,0.004,0.5,5),M(0x111)); w.position.set(x,y+0.28,z); p.add(w); };
function sign(p,x,y,z,w,h,text,{bg='#f4efe6',fg='#3a2a20',ry=0,font=46,glow=0}={}){ const t=canvasTex(512,Math.round(512*h/w),(g,W,H)=>{ g.fillStyle=bg; g.fillRect(0,0,W,H); g.strokeStyle=fg; g.lineWidth=8; g.strokeRect(10,10,W-20,H-20); g.fillStyle=fg; g.font=`bold ${font*1.4}px monospace`; g.textAlign='center'; g.textBaseline='middle'; const lines=text.split('\n'); lines.forEach((l,i)=>g.fillText(l,W/2,H/2+(i-(lines.length-1)/2)*font*1.5)); }); const m=P(p,w,h,new THREE.MeshStandardMaterial({map:t,roughness:0.8,emissive:glow?0xffffff:0x000000,emissiveMap:glow?t:null,emissiveIntensity:glow}),x,y,z,{ry}); return m; }
function paperStack(p,x,y,z,n=6,seed=1){ const R=rng(seed); for(let i=0;i<n;i++) B(p,0.3,0.012,0.22,M(0xf4efe6,{r:0.9}),x+(R()-0.5)*0.03,y+0.006+i*0.013,z+(R()-0.5)*0.03,{ry:(R()-0.5)*0.25}); }
function lampTable(p,x,y,z){ C(p,0.012,0.012,0.35,M(0x222,{m:0.5}),x,y+0.18,z); C(p,0.09,0.15,0.17,M(0xffe2b0,{e:0xffc06a,ei:1.4,r:0.9}),x,y+0.46,z,{cast:false}); }
const ceilStrip=(p,x,y,z,w=1.2)=>B(p,w,0.04,0.12,M(0xfff4dc,{e:0xfff0c0,ei:2.2}),x,y,z,{cast:false});
function buildingBlock(p,x,z,w,h,col,seed){ const R=rng(seed); const wt=canvasTex(128,256,(g,W,H)=>{ g.fillStyle='#'+col.toString(16).padStart(6,'0'); g.fillRect(0,0,W,H); for(let r=0;r<10;r++) for(let c=0;c<5;c++){ g.fillStyle=R()<0.4?'#ffd890':'#2a2d36'; g.fillRect(10+c*23,10+r*24,14,16); } }); const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,1.2),new THREE.MeshStandardMaterial({map:wt,emissive:0xffffff,emissiveMap:wt,emissiveIntensity:0.35,roughness:0.9})); m.position.set(x,h/2,z); p.add(m); wt.wrapS=wt.wrapT=THREE.RepeatWrapping; wt.repeat.set(Math.max(1,Math.round(w/0.9)),Math.max(1,Math.round(h/2.4))); return m; }

// ---------------------------------------------------------------- 2: rent: the front door, the landlord's hand out
export function buildRent(){ const g=new THREE.Group(); floorAndWalls(g,{wall:0x4b6a6a,floor:'#7a5a40'});
  const door=new THREE.Group(); B(door,1.15,2.3,0.12,M(0x2a1c12,{r:0.5}),0,1.15,0); const panel=B(door,0.95,2.15,0.06,M(0x6b3f26,{map:woodTex('#6b3f26',[1,2])}),0,1.1,0.08); sign(door,0,1.65,0.12,0.2,0.12,'12',{font:36,bg:'#d9a63a',fg:'#2a1c12'}); S(door,0.04,M(0xc9a24a,{m:0.7,r:0.3}),0.35,1.05,0.13); door.position.set(-1.3,0,-2.1); g.add(door);
  // the open doorway on the right, hall light spilling out
  B(g,1.4,2.3,0.1,M(0xffe0a0,{e:0xffd890,ei:1.8}),1.6,1.15,-2.15,{cast:false}); B(g,0.12,2.4,0.2,M(0x2a1c12),0.88,1.2,-2.1); B(g,0.12,2.4,0.2,M(0x2a1c12),2.32,1.2,-2.1); B(g,1.6,0.12,0.2,M(0x2a1c12),1.6,2.4,-2.1);
  B(g,1.2,0.04,0.7,M(0x7a2f2a,{r:1}),0.2,0.02,-1.3); plant(g,2.6,0,-1.5,1.4,4); B(g,1.0,0.5,0.35,M(0x5a3a22,{map:woodTex('#5a3a22',[1,1])}),-2.5,0.25,-1.7); for(let i=0;i<3;i++) B(g,0.2,0.07,0.1,M([0x15171b,0x6b4a2a,0xd9d2c4][i]),-2.7+i*0.25,0.54,-1.7);
  warmBulb(g,0.2,2.5,-1.0); sign(g,-2.2,1.9,-2.17,0.7,0.3,'RENT DUE\n5TH',{font:30,bg:'#ffe36b'}); return g; }
// ---------------------------------------------------------------- 3: EMI: the bank counter
export function buildBank(){ const g=new THREE.Group(); floorAndWalls(g,{wall:0x3f5a5f,floor:'#9c8a70'});
  B(g,3.6,1.05,0.7,M(0x5a3a22,{map:woodTex('#5a3a22',[3,1])}),0.3,0.52,-0.9,{round:0.02}); B(g,3.7,0.06,0.8,M(0xd9cfbd,{r:0.4}),0.3,1.07,-0.9,{round:0.02}); B(g,3.5,0.7,0.04,M(0x9cc4d6,{r:0.1,o:0.28,t:true}),0.3,1.45,-0.55,{cast:false});
  B(g,0.7,0.45,0.05,M(0x1d2026,{r:0.3}),-0.4,1.3,-1.1,{rx:-0.2}); B(g,0.3,0.05,0.2,M(0x22262c),-0.4,1.1,-1.0); B(g,0.2,0.3,0.03,M(0x222),1.2,1.3,-1.2); sign(g,0.3,2.25,-2.17,1.8,0.45,'BANK  LOAN / EMI',{bg:'#1e3a5f',fg:'#ffe9b0',font:34,glow:0.6});
  for(let i=0;i<3;i++) ceilStrip(g,-1.2+i*1.5,2.9,-0.8); paperStack(g,1.0,1.1,-0.9,5,2); plant(g,-1.9,0,-0.6,1.4,6); B(g,0.08,0.9,0.08,M(0x333,{m:0.6}),2.2,0.45,0.2); B(g,0.08,0.9,0.08,M(0x333,{m:0.6}),2.9,0.45,0.2); B(g,0.7,0.03,0.03,M(0x7a1f1f),2.55,0.85,0.2); return g; }
// ---------------------------------------------------------------- 4: groceries: the market stall
export function buildMarket(){ const g=new THREE.Group(); floorAndWalls(g,{wall:0x2a2230,floor:'#6a5a4a',backZ:-3.4});
  const city=P(g,9,4,new THREE.MeshBasicMaterial({map:bokehTex(true,11,140),fog:false}),0,2,-3.35);
  B(g,3.4,0.9,0.9,M(0x7a5230,{map:woodTex('#7a5230',[2,1])}),0.2,0.45,-1.2,{round:0.02}); const R=rng(21); const veg=[0xd96b2b,0x4f9a3f,0xe8c33a,0xa5362b,0x7a4a8a];
  for(let i=0;i<5;i++){ B(g,0.6,0.22,0.6,M(0x8a5a2b,{map:woodTex('#8a5a2b',[1,1])}),-1.2+i*0.7,0.98,-1.2); for(let k=0;k<14;k++) S(g,0.075,M(veg[i],{r:0.5}),-1.2+i*0.7+(R()-0.5)*0.45,1.14+R()*0.05,-1.2+(R()-0.5)*0.45); }
  for(let i=0;i<7;i++){ const m=M(i%2?0xb98a54:0xc9a06a,{r:0.9}); B(g,0.3,0.4,0.2,m,1.5+(i%3)*0.3,0.2+Math.floor(i/3)*0.4,0.1+(i%2)*0.1,{ry:(R()-0.5)*0.5}); }
  const aw=new THREE.Group(); for(let i=0;i<8;i++) B(aw,0.5,0.06,1.3,M(i%2?0xf1e6d0:0xc4452f,{r:0.9}),-1.75+i*0.5,0,0); aw.position.set(0.1,2.35,-1.3); aw.rotation.x=0.18; g.add(aw);
  for(let i=0;i<4;i++) warmBulb(g,-1.3+i*0.9,2.15,-0.7,0.9); sign(g,-1.6,1.95,-0.6,0.7,0.28,'FRESH\nVEG',{bg:'#fff3c8',font:26}); return g; }
// ---------------------------------------------------------------- 5: bills: a desk buried in paper
export function buildBills(){ const g=new THREE.Group(); floorAndWalls(g,{wall:0x5f4a45,floor:'#7a5a40'});
  B(g,2.4,0.08,1.0,M(0x6b4428,{map:woodTex('#6b4428',[2,1])}),0,0.8,-0.9,{round:0.02}); for(const x of [-1.1,1.1]) B(g,0.08,0.8,0.8,M(0x4a3020),x,0.4,-0.9);
  for(let i=0;i<6;i++) paperStack(g,-0.9+i*0.35,0.84,-0.95+(i%2)*0.2,3+i%4,i+3); lampTable(g,-0.95,0.84,-1.25);
  // the three bills as things: a bulb (electricity), a tap (water), a wifi router
  S(g,0.13,M(0xfff0c8,{e:0xffd890,ei:2.2}),0.9,1.35,-1.5,{cast:false}); C(g,0.05,0.05,0.12,M(0x888,{m:0.7}),0.9,1.2,-1.5); const tap=C(g,0.03,0.03,0.3,M(0xb8c0c8,{m:0.8,r:0.3}),1.75,1.15,-2.05,{rx:Math.PI/2}); S(g,0.07,M(0x6ab4e8,{r:0.2,e:0x6ab4e8,ei:0.5}),1.75,0.98,-1.92);
  B(g,0.36,0.06,0.22,M(0x1b1e24,{r:0.4}),1.0,0.88,-0.75); for(let i=0;i<3;i++) C(g,0.01,0.01,0.28,M(0x1b1e24),0.9+i*0.1,1.03,-0.75,{rz:(i-1)*0.2}); S(g,0.012,M(0x4aff7a,{e:0x4aff7a,ei:3}),0.88,0.92,-0.64);
  B(g,0.45,0.05,0.45,M(0x4a3020),-0.5,0.45,-0.2); B(g,0.05,0.5,0.45,M(0x4a3020),-0.72,0.7,-0.2); for(const [x,z] of [[-0.3,-0.02],[-0.7,-0.02],[-0.3,-0.38],[-0.7,-0.38]]) B(g,0.04,0.45,0.04,M(0x3a2418),x,0.22,z); sign(g,-1.6,1.7,-2.17,0.62,0.4,'ELECTRICITY\nWATER\nWI-FI',{font:20,bg:'#fff3c8'}); plant(g,2.3,0,-1.4,1.3,8); B(g,0.5,0.5,0.4,M(0x6b4428),-2.2,0.25,-1.5); return g; }
// ---------------------------------------------------------------- 6: food: a small restaurant
export function buildRestaurant(){ const g=new THREE.Group(); floorAndWalls(g,{wall:0x6a3a2f,floor:'#6a4a34'});
  B(g,1.1,0.06,0.8,M(0xe8d9bd,{r:0.5}),0.2,0.78,-0.5,{round:0.02}); C(g,0.05,0.05,0.76,M(0x4a3020),0.2,0.38,-0.5); const plate=C(g,0.22,0.2,0.03,M(0xfdf8ee,{r:0.3}),0.2,0.83,-0.5); S(g,0.14,M(0xf2e4c0,{r:0.7}),0.2,0.88,-0.5,{sy:0.5}); S(g,0.08,M(0xd9822b,{r:0.6}),0.3,0.9,-0.45,{sy:0.5}); C(g,0.05,0.045,0.12,M(0xcfe6f4,{r:0.1,o:0.6,t:true}),0.5,0.87,-0.4);
  B(g,0.42,0.05,0.42,M(0x6b3f26),-0.5,0.47,-0.5); B(g,0.42,0.5,0.05,M(0x6b3f26),-0.5,0.75,-0.7);
  // other diners (blurred grey-warm figures are added by the scene), hanging lamps, menu board, kitchen pass
  for(let i=0;i<4;i++){ C(g,0.005,0.005,0.8,M(0x111),-1.6+i*1.4,2.7,-1.4); C(g,0.05,0.2,0.2,M(0xffd890,{e:0xffc06a,ei:1.8}),-1.6+i*1.4,2.25,-1.4,{cast:false}); }
  sign(g,1.8,1.9,-2.17,1.0,0.8,'MENU\nTHALI 150\nCHAI 20',{bg:'#2a1c12',fg:'#ffe9b0',font:26}); B(g,1.8,0.9,0.5,M(0x5a3a22),-1.9,0.45,-1.9); P(g,6,3,new THREE.MeshBasicMaterial({map:bokehTex(true,17,80),fog:false,transparent:true,opacity:0.6}),0,1.8,-2.15);
  for(let i=0;i<3;i++){ B(g,0.7,0.05,0.7,M(0xe8d9bd),-2.2+i*0.0,0.7,-0.1+ i*0.0); } return g; }
// ---------------------------------------------------------------- 7: fuel: a petrol pump at night
export function buildPump(){ const g=new THREE.Group(); const road=P(g,24,10,M(0x2a2a30,{r:0.9}),0,0,-1,{rx:-Math.PI/2}); B(g,24,0.02,0.2,M(0xe8c33a),0,0.01,1.8); P(g,9,4,new THREE.MeshBasicMaterial({map:bokehTex(false,23,110),fog:false}),0,2,-4.2);
  B(g,5,0.1,2.6,M(0xefe8da,{r:0.6}),0,3.2,-1.3); for(let i=0;i<4;i++) B(g,0.9,0.04,0.2,M(0xfff4dc,{e:0xfff0c0,ei:2.4}),-1.8+i*1.2,3.1,-1.3,{cast:false}); for(const x of [-2.3,2.3]) B(g,0.18,3.2,0.18,M(0xd9d2c4),x,1.6,-1.3);
  const pump=new THREE.Group(); B(pump,0.7,1.5,0.45,M(0xc4452f,{r:0.4}),0,0.75,0,{round:0.04}); B(pump,0.55,0.35,0.03,M(0x111,{r:0.3}),0,1.15,0.24); sign(pump,0,1.15,0.255,0.5,0.28,'FUEL\n3,200',{bg:'#0c1a10',fg:'#7aff9a',font:22,glow:0.9}); C(pump,0.025,0.025,0.4,M(0x222),0.42,0.9,0,{rx:0.4}); B(pump,0.08,0.3,0.05,M(0x222),0.46,0.78,0.1); pump.position.set(0.85,0,-0.7); g.add(pump);
  // a scooter by the pump
  const bike=new THREE.Group(); const bm=M(0x2f5f8a,{r:0.4}); B(bike,1.0,0.12,0.2,bm,0,0.38,0,{round:0.04}); B(bike,0.4,0.28,0.2,bm,-0.35,0.58,0,{round:0.08}); B(bike,0.3,0.1,0.2,M(0x15171b),-0.25,0.7,0,{round:0.04}); for(const x of [-0.5,0.5]){ const w=new THREE.Mesh(new THREE.TorusGeometry(0.17,0.055,10,22),M(0x15171b)); w.position.set(x,0.19,0); bike.add(w); } B(bike,0.05,0.6,0.05,M(0x222),0.5,0.62,0,{rz:-0.3}); B(bike,0.05,0.05,0.5,M(0x222),0.6,0.88,0); bike.position.set(-0.3,0,-0.6); g.add(bike); g.userData.bike=bike; return g; }
// ---------------------------------------------------------------- 8: the street at sunrise (seen through his own front door)
export function buildStreet(){ const g=new THREE.Group(); P(g,30,12,M(0x7a6a58,{r:0.95}),0,0,-3,{rx:-Math.PI/2}); const sky=P(g,40,18,new THREE.MeshBasicMaterial({color:0xffc98a,fog:false}),0,7,-9); const R=rng(31);
  for(let i=0;i<9;i++) buildingBlock(g,-8+i*2.2,-5-R()*1.5,1.6+R()*1.2,3+R()*4,[0xd9a066,0xc98a58,0xe8c08a,0xb88a6a][i%4],i+40);
  S(g,1.6,new THREE.MeshBasicMaterial({color:0xfff0c0,fog:false}),2.5,4,-8.5,{cast:false}); for(let i=0;i<5;i++){ C(g,0.1,0.14,1.3,M(0x5a3a22),-3+i*2.1,0.65,-1.8); S(g,0.7,M(0x4f9a3f,{r:0.8}),-3+i*2.1,1.7,-1.8); }
  // the door frame he steps through (foreground)
  B(g,0.3,3.2,0.3,M(0x2a1c12),-1.4,1.6,1.0); B(g,0.3,3.2,0.3,M(0x2a1c12),1.4,1.6,1.0); B(g,3.1,0.3,0.3,M(0x2a1c12),0,3.1,1.0); B(g,1.2,0.04,0.5,M(0x7a2f2a),0,0.02,0.8);
  for(let i=0;i<3;i++){ const car=new THREE.Group(); B(car,1.2,0.4,0.6,M([0xc4c0b8,0x2f5f8a,0xd9a63a][i],{r:0.4}),0,0.35,0,{round:0.08}); B(car,0.7,0.3,0.55,M(0x9cc4d6,{r:0.1}),-0.05,0.65,0,{round:0.08}); car.position.set(-2.5+i*2.4,0,-2.7); g.add(car); } return g; }
// ---------------------------------------------------------------- 9: the office
export function buildOffice(){ const g=new THREE.Group(); floorAndWalls(g,{wall:0x3c4a52,floor:'#6a6a6e',backZ:-2.6});
  const win=new THREE.Group(); const skyM=new THREE.MeshBasicMaterial({color:0xffd9a0,fog:false}); const sk=P(win,3.6,1.6,skyM,0,0,0); for(let i=0;i<6;i++) buildingBlock(win,-1.5+i*0.6,-0.1,0.5,0.4+((i*7)%5)*0.15,0x6a6a7a,60+i); B(win,3.7,0.06,0.06,M(0x1b1e24),0,0.8,0.05); B(win,3.7,0.06,0.06,M(0x1b1e24),0,-0.8,0.05); for(let i=0;i<4;i++) B(win,0.05,1.6,0.06,M(0x1b1e24),-1.8+i*1.2,0,0.05); win.position.set(0.8,1.9,-2.55); g.add(win); g.userData.sky=skyM;
  const desk=new THREE.Group(); B(desk,2.0,0.06,0.9,M(0x7a5a3a,{map:woodTex('#7a5a3a',[2,1])}),0,0.78,0,{round:0.02}); for(const x of [-0.9,0.9]) B(desk,0.06,0.78,0.8,M(0x3a2a1e),x,0.39,0); B(desk,0.62,0.4,0.04,M(0x0d1013,{r:0.3,e:0x9fd0ff,ei:0.6}),0.3,1.12,-0.28,{rx:-0.08,ry:0.5}); B(desk,0.05,0.2,0.05,M(0x222),0.3,0.92,-0.28); B(desk,0.42,0.02,0.15,M(0x22262c),0.2,0.82,0.1); B(desk,0.4,0.28,0.04,M(0x15171b,{r:0.3,e:0x9fd0ff,ei:0.3}),-0.5,1.0,-0.3,{rx:-0.3}); paperStack(desk,-0.75,0.81,0.1,8,4); lampTable(desk,-0.85,0.81,-0.3); desk.position.set(0.4,0,-1.2); g.add(desk); g.userData.desk=desk;
  B(g,0.5,0.06,0.5,M(0x1d2026),0.6,0.5,-0.5,{round:0.02}); B(g,0.5,0.6,0.06,M(0x1d2026),0.6,0.82,-0.22,{round:0.02}); C(g,0.03,0.03,0.5,M(0x333),0.6,0.25,-0.5);
  const cup=new THREE.Group(); C(cup,0.05,0.042,0.09,M(0xf2ede4,{r:0.4}),0,0,0); const cof=C(cup,0.047,0.043,0.01,M(0x3a2316,{r:0.3}),0,0.03,0); cup.position.set(0.9,0.86,-1.0); g.add(cup); g.userData.coffee=cof; g.userData.cupG=cup;
  const cal=new THREE.Mesh(new THREE.PlaneGeometry(0.62,0.78),new THREE.MeshStandardMaterial({map:calendarTex(0,6,'JANUARY'),roughness:0.9})); cal.position.set(-1.6,1.8,-2.57); g.add(cal); g.userData.cal=cal;
  const clock=C(g,0.17,0.17,0.04,M(0xf4efe6),-0.4,2.5,-2.56,{rx:Math.PI/2}); const ch=B(g,0.01,0.12,0.01,M(0x111),-0.4,2.5,-2.52); g.userData.clockHand=ch;
  for(let i=0;i<4;i++) ceilStrip(g,-1.6+i*1.4,3.0,-1.2); for(const x of [-2.3,2.7]){ const d=new THREE.Group(); B(d,1.4,0.06,0.7,M(0x7a5a3a),0,0.78,0); B(d,0.05,0.78,0.6,M(0x3a2a1e),-0.65,0.39,0); B(d,0.05,0.78,0.6,M(0x3a2a1e),0.65,0.39,0); B(d,0.5,0.34,0.04,M(0x0d1013,{e:0x9fd0ff,ei:0.4}),0,1.05,-0.2); d.position.set(x,0,-1.6); g.add(d); } plant(g,-2.7,0,-2.0,1.6,13); return g; }
