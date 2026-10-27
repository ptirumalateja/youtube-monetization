// The Salary Loop, dark-warm restyle (full reel, wide shot). Teja's brief (27 Oct 2026): dark but not black, sad-real, not depressing.
// One wooden man alone at a table at 11 pm. The only light is a table lamp (warm, about 3000 K); the room falls off to charcoal and
// deep navy, never #000. Wall calendar (flips slowly in the full cut), wall clock at 11, a night window, his phone, an empty wallet.
// ?v=after (default): Day 24, balance 0, head in his hand.  ?v=before: Day 1, salary just credited, sitting up, phone lit.
// Units are metres; floor y = 0; the camera is on +z. Built on the Slow Light Dark kit (sld.js, with bg/fog/lift/vig options).
import * as THREE from 'three';
import * as SLD from './sld.js';
const {V,clamp,lerp,rng,yawOf,PAL,UPV}=SLD;
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960;
const TL=await (await fetch('./timeline.json')).json(); const DUR=TL.duration;
const BILLS=TL.bills;

// ---------------------------------------------------------------- palette: charcoal / deep navy room, one 3000 K lamp
const BG=0x161b25, K3000=0xffb46b;
const TOP=0.74, LAMPP=V(-0.52,TOP,-0.16), BULB=LAMPP.clone().add(V(0,0.4,0));
const S=SLD.createStage({W,H,lamp:BULB,lampTarget:V(-0.05,0,0.12),cone:1.05,spot:3.6,beam:0.0,motes:500,bg:BG,fogD:0.028,lift:[0.011,0.0135,0.021],vig:0.42,fov:36});
const R=SLD.createRig(S.scene);
S.spot.color.setHex(K3000); S.spot.penumbra=0.9; S.spot.decay=1.6; S.spot.shadow.camera.near=0.05; S.spot.shadow.camera.far=6; S.spot.shadow.radius=6;
S.moteU.uCol.value.setHex(0xffc890);
S.floor.material.color.setHex(0x40342b); S.floor.material.opacity=0.985; S.refl.material.uniforms.color.value.setHex(0x1a1a1a);
const spill=new THREE.PointLight(K3000,1.6,7,1.4); spill.position.copy(BULB).add(V(0,0.12,0)); S.scene.add(spill);   // upward/sideways spill onto the wall
const navy=new THREE.HemisphereLight(0x3a4c78,0x241c16,0.7); S.scene.add(navy);                                    // the night: a whisper of navy
const winLight=new THREE.PointLight(0x5a78b8,0.5,4,1.6); winLight.position.set(1.15,1.6,-1.1); S.scene.add(winLight);

// ---------------------------------------------------------------- materials
function canvasTex(w,h,fn){ const c=document.createElement('canvas'); c.width=w; c.height=h; const g=c.getContext('2d'); fn(g,w,h); const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; t.anisotropy=8; return t; }
function woodTex(seed,base){ const t=canvasTex(1024,256,(g)=>{ const Rn=rng(seed); g.fillStyle=base; g.fillRect(0,0,1024,256);
  for(let k=0;k<260;k++){ const y=Rn()*256, a=0.04+Rn()*0.1; g.strokeStyle=Rn()<0.6?`rgba(0,0,0,${a})`:`rgba(255,220,180,${a*0.5})`; g.lineWidth=0.6+Rn()*2.2;
    g.beginPath(); g.moveTo(0,y); for(let x=0;x<=1024;x+=32) g.lineTo(x,y+Math.sin(x*0.004+k)*3+Math.sin(x*0.021+k*1.7)*1.2); g.stroke(); } }); t.wrapS=t.wrapT=THREE.RepeatWrapping; return t; }
const WOOD=SLD.rimify(new THREE.MeshStandardMaterial({color:0x8a6a52,map:woodTex(3,'#3b2a1f'),roughness:0.5}),0xffe6c8,0.05,'wood');
const CHAIRWOOD=SLD.rimify(new THREE.MeshStandardMaterial({color:0x7a5c46,map:woodTex(9,'#33241a'),roughness:0.62}),0xc8d4f0,0.07,'chair');
const std=(color,key,{r=0.6,m=0,rim=0.08,rimCol=0xfff1d8,e=0,ei=0,map=null,emap=null}={})=>SLD.rimify(new THREE.MeshStandardMaterial({color,roughness:r,metalness:m,emissive:e,emissiveIntensity:ei,map,emissiveMap:emap}),rimCol,rim,key);
function add(geo,mat,parent=S.scene,cast=true){ const m=new THREE.Mesh(geo,mat); m.castShadow=cast; m.receiveShadow=true; parent.add(m); return m; }
function box(w,h,d,mat,x,y,z,parent){ const m=add(new THREE.BoxGeometry(w,h,d),mat,parent); m.position.set(x,y,z); return m; }

// ---------------------------------------------------------------- the room: back wall (charcoal navy), skirting
const WALLZ=-1.75;
const wallTex=canvasTex(512,512,(g)=>{ const Rn=rng(4); g.fillStyle='#808080'; g.fillRect(0,0,512,512); for(let i=0;i<9000;i++){ const v=110+Rn()*36; g.fillStyle=`rgba(${v},${v},${v},0.25)`; g.fillRect(Rn()*512,Rn()*512,2,2); } });
wallTex.wrapS=wallTex.wrapT=THREE.RepeatWrapping; wallTex.repeat.set(4,2);
const wall=add(new THREE.PlaneGeometry(12,5),std(0x55607a,'wall',{r:0.95,rim:0,map:wallTex}),S.scene,false); wall.position.set(0,2.5,WALLZ);
box(12,0.1,0.03,std(0x241c16,'skirt',{r:0.7,rim:0}),0,0.05,WALLZ+0.015);

// ---------------------------------------------------------------- the table, his chair
const TX=0.62, TZ=0.4;
{ const top=box(TX*2,0.05,TZ*2,WOOD,0,TOP-0.025,0); top.material.map.repeat.set(2,1);
  box(TX*2-0.16,0.09,TZ*2-0.12,WOOD,0,TOP-0.095,0);
  for(const x of [-TX+0.07,TX-0.07]) for(const z of [-TZ+0.07,TZ-0.07]) box(0.07,TOP-0.05,0.07,WOOD,x,(TOP-0.05)/2,z); }
function makeChair(){ const g=new THREE.Group(); const a=(w,h,d,x,y,z)=>{ const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),CHAIRWOOD); m.position.set(x,y,z); m.castShadow=m.receiveShadow=true; g.add(m); };
  a(0.42,0.04,0.42,0,0.44,0); for(const x of [-0.18,0.18]) for(const z of [-0.18,0.18]) a(0.035,0.44,0.035,x,0.22,z);
  for(const z of [-0.18,0.18]) a(0.035,0.5,0.035,-0.19,0.71,z); a(0.03,0.12,0.4,-0.19,0.88,0); a(0.03,0.12,0.4,-0.19,0.68,0); S.scene.add(g); return g; }
const HIPBACK=0.276, MANX=0.14, BACKZ=-0.74, FACE_Z=V(0,0,1);
const chair=makeChair(); chair.position.set(MANX,0,BACKZ); chair.rotation.y=yawOf(FACE_Z);
// the empty chair on our side, pushed in (nobody else at this table)


// ---------------------------------------------------------------- the table lamp (the only light)
let shadeM,halo,halo2;
const BRASS=std(0x6a5332,'brass',{r:0.38,m:0.5,rim:0.15});
{ const base=add(new THREE.CylinderGeometry(0.085,0.1,0.03,32),BRASS); base.position.copy(LAMPP).add(V(0,0.015,0));
  const stem=add(new THREE.CylinderGeometry(0.011,0.011,0.32,12),BRASS); stem.position.copy(LAMPP).add(V(0,0.19,0));
  shadeM=new THREE.MeshStandardMaterial({color:0xf1d7a8,roughness:0.9,emissive:0xffb050,emissiveIntensity:1.25,side:THREE.DoubleSide});
  const shade=add(new THREE.CylinderGeometry(0.085,0.16,0.17,40,1,true),shadeM,S.scene,false); shade.position.copy(LAMPP).add(V(0,0.43,0));
  const bulb=add(new THREE.SphereGeometry(0.035,20,14),new THREE.MeshBasicMaterial({color:0xfff0d0}),S.scene,false); bulb.position.copy(BULB);
  halo=SLD.glowSprite(S.scene,0xffb868,0.55); halo.position.copy(BULB).add(V(0,0.03,0)); halo.scale.setScalar(1.3);
  halo2=SLD.glowSprite(S.scene,0xff9a40,0.16); halo2.position.copy(BULB).add(V(0,0.03,0)); halo2.scale.setScalar(4.2); }
// lamp at the edge of the table; the spot hangs in the shade (no visible beam, just the pool of light)
S.spot.position.copy(BULB); S.spot.target.position.set(-0.05,0,0.12); S.spot.target.updateMatrixWorld(); S.spot.angle=1.12;

// ---------------------------------------------------------------- state from time
const sstep=SLD.sstep, bump=(t,a,d)=>{ const x=(t-a)/d; return x<=0||x>=1?0:Math.sin(Math.PI*x)**2; };
const WK=TL.work; const wu=t=>clamp((t-WK[0])/(WK[1]-WK[0]));
const ease=u=>u*u*(3-2*u);
function dayAt(t){ if(t<BILLS[0].t) return 1; if(t<TL.zero){ let d=0; BILLS.forEach((b,i)=>{ if(t>=b.t) d=i+1; }); return d; } if(t<WK[0]) return 6;
  if(t<TL.flipPage[0]) return Math.min(30,7+Math.floor(23.99*ease(wu(t)))); return 1; }
function balanceAt(t){ if(t>=TL.next||t<BILLS[0].t) return TL.salary; if(t>=TL.zero) return 0; let b=TL.salary; BILLS.forEach(x=>{ b-=x.amt*sstep(x.t,x.t+0.4,t); }); return Math.round(b/100)*100; }
const crossedAt=t=>t>=TL.flipPage[0]||t<BILLS[0].t?0:dayAt(t)-1;

// ---------------------------------------------------------------- calendar (flips slowly: one day at a time, then the page turns)
function drawCal(g,w,h,crossed,circled){ g.fillStyle='#efe8dc'; g.fillRect(0,0,w,h); g.fillStyle='#b8432f'; g.fillRect(0,0,w,96); g.fillStyle='#fff'; g.font='bold 52px monospace'; g.textAlign='center'; g.fillText('NOVEMBER',w/2,68);
  g.font='bold 30px monospace'; const cw=64,ch=86; for(let i=0;i<31;i++){ const x=32+(i%7)*cw+cw/2, y=172+Math.floor(i/7)*ch; g.fillStyle='#3a3530'; g.fillText(String(i+1),x,y);
    if(i<crossed){ g.strokeStyle='#b8432f'; g.lineWidth=5; g.beginPath(); g.moveTo(x-22,y-32); g.lineTo(x+22,y+8); g.moveTo(x+22,y-32); g.lineTo(x-22,y+8); g.stroke(); } }
  const i=circled-1, x=32+(i%7)*cw+cw/2, y=172+Math.floor(i/7)*ch; g.strokeStyle='#b8432f'; g.lineWidth=6; g.beginPath(); g.ellipse(x,y-12,32,30,0.2,0,7); g.stroke(); }
const mkCal=()=>{ const c=document.createElement('canvas'); c.width=512; c.height=660; const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; t.anisotropy=8; return {c,g:c.getContext('2d'),t,key:''}; };
const CAL=mkCal(), CAL2=mkCal(); drawCal(CAL2.g,512,660,0,1); CAL2.t.needsUpdate=true;
const CALPIVOT=new THREE.Group(); CALPIVOT.position.set(0.45,1.62+0.3225,WALLZ+0.012); S.scene.add(CALPIVOT);
const calFront=add(new THREE.PlaneGeometry(0.5,0.645),new THREE.MeshStandardMaterial({map:CAL.t,roughness:0.9}),CALPIVOT,false); calFront.position.y=-0.3225; calFront.material.emissive=new THREE.Color(0xffb878); calFront.material.emissiveMap=CAL.t; calFront.material.emissiveIntensity=0.07;
const calBack=add(new THREE.PlaneGeometry(0.5,0.645),new THREE.MeshStandardMaterial({map:CAL2.t,roughness:0.9,emissive:0xffb878,emissiveMap:CAL2.t,emissiveIntensity:0.07}),S.scene,false); calBack.position.set(0.45,1.62,WALLZ+0.008);
box(0.012,0.012,0.02,BRASS,0.45,1.96,WALLZ+0.02);

// ---------------------------------------------------------------- wall clock (time-lapse during the work: twelve evenings, ends at 11:00 again)
const CLK=new THREE.Group(); CLK.position.set(-0.1,2.0,WALLZ+0.02); S.scene.add(CLK);
{ const face=add(new THREE.CylinderGeometry(0.15,0.15,0.02,48),std(0xe8e0d0,'clk',{r:0.6,rim:0}),CLK); face.rotation.x=Math.PI/2; add(new THREE.TorusGeometry(0.15,0.014,10,48),std(0x2a221a,'clkr',{r:0.5,rim:0.1}),CLK);
  for(let i=0;i<12;i++){ const a=i/12*Math.PI*2; const tk=add(new THREE.BoxGeometry(0.008,0.022,0.004),std(0x2a221a,'tick',{r:0.5,rim:0}),CLK,false); tk.position.set(Math.sin(a)*0.125,Math.cos(a)*0.125,0.013); tk.rotation.z=-a; } }
const mkHand=(len,wd)=>{ const m=add(new THREE.BoxGeometry(wd,len,0.006),std(0x1c1814,'hand'+len,{r:0.5,rim:0}),CLK,false); m.geometry.translate(0,len/2-0.01,0); m.position.z=0.016; return m; };
const hHand=mkHand(0.085,0.014), mHand=mkHand(0.12,0.009);

// ---------------------------------------------------------------- the rest of the room (lots of background)
const DARKWOOD=std(0x3b2a1f,'dw',{r:0.7,rim:0.04});
{ // night window above the bed
  const nightTex=canvasTex(512,640,(g,w,h)=>{ const gr=g.createLinearGradient(0,0,0,h); gr.addColorStop(0,'#0e1630'); gr.addColorStop(1,'#1b2440'); g.fillStyle=gr; g.fillRect(0,0,w,h);
    const Rn=rng(11); for(let b=0;b<5;b++){ const bx=b*110-20+Rn()*30, bw=90+Rn()*40, by=260+Rn()*200; g.fillStyle='#0a0f1e'; g.fillRect(bx,by,bw,h-by);
      for(let yy=by+16;yy<h-10;yy+=34) for(let xx=bx+10;xx<bx+bw-14;xx+=24) if(Rn()<0.13){ g.fillStyle=Rn()<0.7?'rgba(255,190,110,0.85)':'rgba(170,200,255,0.7)'; g.fillRect(xx,yy,12,16); } }
    g.fillStyle='rgba(255,255,255,0.8)'; g.beginPath(); g.arc(400,90,18,0,7); g.fill(); });
  const win=new THREE.Group(); win.position.set(1.4,1.85,WALLZ+0.02); S.scene.add(win);
  const gl=new THREE.Mesh(new THREE.PlaneGeometry(0.66,0.84),new THREE.MeshBasicMaterial({map:nightTex,fog:false,color:0x9aa6c0})); gl.position.z=0.005; win.add(gl);
  for(const [w,h,x,y] of [[0.74,0.05,0,0.445],[0.74,0.05,0,-0.445],[0.05,0.94,-0.35,0],[0.05,0.94,0.35,0],[0.03,0.84,0,0],[0.66,0.03,0,0.03]]) box(w,h,0.06,DARKWOOD,x,y,0.02,win);
  box(0.84,0.04,0.12,DARKWOOD,0,-0.48,0.06,win); }
{ // bed in the right corner (his bed is right there, he just never gets to it)
  const bed=new THREE.Group(); bed.position.set(1.4,0,WALLZ+0.95); S.scene.add(bed);
  box(0.95,0.28,1.9,DARKWOOD,0,0.14,0,bed); box(0.88,0.18,1.84,std(0xcfc8bc,'mat',{r:0.9,rim:0.04}),0,0.37,0,bed);
  box(0.88,0.1,1.2,std(0x2b3b6a,'quilt2',{r:0.95,rim:0.05}),0,0.5,0.28,bed); box(0.55,0.1,0.3,std(0xd8d2c6,'pil',{r:0.95,rim:0.05}),0,0.5,-0.72,bed); box(0.95,0.7,0.06,DARKWOOD,0,0.5,-0.97,bed); }
{ // bookshelf and plant on the left, a door
  const sh=new THREE.Group(); sh.position.set(-0.75,1.65,WALLZ+0.1); S.scene.add(sh); const Rn=rng(9); const bc=[0xc4452f,0x2f6b8a,0xd9a63a,0x3f8a45,0x7a4a8a,0xe8e1d4];
  for(const y of [0,0.4]){ box(1.0,0.04,0.22,DARKWOOD,0,y,0,sh); for(let i=0;i<11;i++){ const hh=0.18+Rn()*0.1; box(0.05,hh,0.17,std(bc[i%6],'bk'+(i%6),{r:0.8,rim:0.04}),-0.45+i*0.078,y+0.02+hh/2,0,sh); } }
  const pot=add(new THREE.CylinderGeometry(0.09,0.07,0.14,20),std(0xb5562f,'pot',{r:0.8,rim:0.05})); pot.position.set(-1.7,0.07,WALLZ+0.35);
  const lm=std(0x2f6a3a,'leaf',{r:0.7,rim:0.05}); for(let i=0;i<9;i++){ const l=add(new THREE.SphereGeometry(0.08,14,10),lm); l.scale.set(0.6,1.4,0.6); l.position.set(-1.7+(Rn()-0.5)*0.2,0.3+Rn()*0.25,WALLZ+0.35+(Rn()-0.5)*0.2); l.rotation.set((Rn()-0.5)*0.8,0,(Rn()-0.5)*0.8); }
  box(0.9,2.0,0.05,std(0x2a2f3c,'door',{r:0.75,rim:0.04}),-1.45,1.0,WALLZ+0.025); const kn=add(new THREE.SphereGeometry(0.03,12,10),BRASS); kn.position.set(-1.12,1.0,WALLZ+0.07); }
{ // a rug under the table, a coat on the chair
  const rug=add(new THREE.BoxGeometry(2.0,0.012,1.5),std(0x3a2a38,'rug',{r:0.95,rim:0.02}),S.scene,false); rug.position.set(0.05,0.006,-0.1); }

// ---------------------------------------------------------------- on the table: phone (live screen), wallet, bill sheets, laptop, cup, work papers
const PH=V(0.42,TOP,-0.08);
const phCv=document.createElement('canvas'); phCv.width=300; phCv.height=600; const phG=phCv.getContext('2d'); const phTex=new THREE.CanvasTexture(phCv); phTex.colorSpace=THREE.SRGBColorSpace; let phKey='';
function drawPhone(t){ const cred=t<BILLS[0].t||t>=TL.next; const bal=balanceAt(t); const key=cred+'|'+bal+'|'+dayAt(t); if(key===phKey) return; phKey=key;
  phG.fillStyle='#0c0f14'; phG.fillRect(0,0,300,600); phG.textAlign='center'; phG.fillStyle='#8a93a6'; phG.font='bold 26px monospace'; phG.fillText(cred?'SALARY CREDITED':'BALANCE',150,230);
  phG.fillStyle=cred?'#5fe08a':(bal===0?'#ff5a4a':'#f2e6cc'); phG.font='bold 64px monospace'; phG.fillText(cred?'+₹50,000':'₹'+bal.toLocaleString('en-US'),150,320); phTex.needsUpdate=true; }
const phone=new THREE.Group(); S.scene.add(phone); phone.position.copy(PH).add(V(0,0.005,0)); phone.rotation.y=0.35;
const phMat=new THREE.MeshStandardMaterial({color:0x000000,roughness:0.25,emissive:0xffffff,emissiveMap:phTex,emissiveIntensity:1.5});
{ add(new THREE.BoxGeometry(0.078,0.009,0.158),std(0x15171b,'ph',{r:0.3,rim:0.2}),phone); const s=add(new THREE.PlaneGeometry(0.07,0.14),phMat,phone,false); s.rotation.x=-Math.PI/2; s.position.y=0.0047; }
const phHalo=SLD.glowSprite(S.scene,0xffd9a0,0.2); phHalo.position.copy(PH).add(V(0,0.05,0)); phHalo.scale.setScalar(0.4);
const phLight=new THREE.PointLight(0xffe0b0,0.18,1.0,2); phLight.position.copy(PH).add(V(0,0.12,0.02)); S.scene.add(phLight);
// wallet (open) with notes that vanish at zero
const walletNotes=[]; { const w=new THREE.Group(); S.scene.add(w); w.position.set(-0.34,TOP+0.006,-0.22); w.rotation.y=0.3;
  const wm=std(0x6a2e20,'wal',{r:0.55,rim:0.1}), im=std(0xc9b898,'wali',{r:0.8,rim:0.05});
  for(const sx of [-1,1]){ const p=new THREE.Group(); w.add(p); p.position.x=sx*0.004; p.rotation.z=sx*-0.03; box(0.105,0.01,0.14,wm,sx*0.055,0,0,p); box(0.095,0.004,0.13,im,sx*0.055,0.007,0,p); }
  for(let i=0;i<5;i++) walletNotes.push(box(0.09,0.003,0.05,std(0xcfe0b5,'note'+i,{r:0.8,rim:0.05,e:0x9fd08a,ei:0.12}),0.055+i*0.002,0.012+i*0.003,-0.01+i*0.004,w)); }
// bill sheets slide in from the right and stack at the left of the table
const billTex=canvasTex(256,340,(g,w,h)=>{ g.fillStyle='#ece6da'; g.fillRect(0,0,w,h); g.fillStyle='#3a3530'; g.font='bold 24px monospace'; g.fillText('DUE',18,40); g.fillStyle='#8a847a'; for(let i=0;i<8;i++) g.fillRect(18,70+i*24,120+((i*53)%90),6); });
const SHEET_AT=V(-0.3,TOP,0.08); const sheets=BILLS.map((b,i)=>{ const m=add(new THREE.BoxGeometry(0.15,0.0025,0.2),std(0xffffff,'bill'+i,{r:0.9,rim:0.03,map:billTex})); return m; });
function placeSheets(t){ sheets.forEach((m,i)=>{ const tb=BILLS[i].t; if(t<tb||t>=TL.next-0.2){ m.visible=false; return; } m.visible=true; const u=clamp((t-tb)/0.4); const e=ease(u);
  const rest=V(SHEET_AT.x+0.012*Math.sin(i*2.1),TOP+0.002+i*0.003,SHEET_AT.z+0.01*Math.cos(i*1.7)); const from=V(0.75,TOP+0.25,0.25); const p=from.clone().lerp(rest,e); p.y+=0.12*Math.sin(Math.PI*u)*(1-e); m.position.copy(p); m.rotation.set(0,0.25-0.12*i+(i%2?0.2:0)+(1-e)*1.2,0); }); }
// laptop: opens when he starts working
const LAP=new THREE.Group(); LAP.position.set(0.1,TOP+0.016,0.02); S.scene.add(LAP);
{ add(new THREE.BoxGeometry(0.34,0.016,0.24),std(0x2a2d33,'lapb',{r:0.4,rim:0.1}),LAP).position.set(0,-0.008,-0.12); }
const lid=new THREE.Group(); LAP.add(lid); { const sh=add(new THREE.BoxGeometry(0.34,0.22,0.008),std(0x2a2d33,'lapl',{r:0.4,rim:0.1}),lid); sh.position.y=0.11;
  const scr=add(new THREE.PlaneGeometry(0.31,0.19),new THREE.MeshStandardMaterial({color:0x000000,emissive:0xffe2b8,emissiveIntensity:0.3,roughness:0.3}),lid,false); scr.rotation.y=Math.PI; scr.position.set(0,0.11,-0.0045); }
const lapLight=new THREE.PointLight(0xffe2b8,0,1.4,2); lapLight.position.set(0.1,TOP+0.25,-0.4); S.scene.add(lapLight);
// cup and a pile of work papers + empty cups
{ const cup=add(new THREE.CylinderGeometry(0.035,0.028,0.085,24),std(0xd8d2c6,'cup',{r:0.35,rim:0.12})); cup.position.set(-0.2,TOP+0.0425,-0.3); const tea=add(new THREE.CylinderGeometry(0.031,0.031,0.004,24),std(0x6a3e1c,'tea',{r:0.2,rim:0})); tea.position.set(-0.2,TOP+0.075,-0.3); }
const workPile=add(new THREE.BoxGeometry(0.2,0.1,0.26),std(0xe8e1d4,'wp',{r:0.9,rim:0.03})); workPile.position.set(0.5,TOP+0.05,0.2); workPile.rotation.y=0.15;
const extraCups=[[0.3,0.28],[-0.45,0.25],[0.55,-0.3]].map(([x,z])=>{ const c=add(new THREE.CylinderGeometry(0.035,0.028,0.085,20),std(0xd8d2c6,'ecup',{r:0.35,rim:0.12})); c.position.set(x,TOP+0.0425,z); c.visible=false; return c; });

// ---------------------------------------------------------------- him
const man=R.makeFig(PAL.CREAM,'man',{rim:0.16,lift:0.04});
const hair=add(new THREE.SphereGeometry(1,26,16,0,Math.PI*2,0,Math.PI*0.5),std(0x2b1f18,'hair',{r:0.85,rim:0.1}));
function placeHair(J){ const hd=J.head.clone().sub(J.neck).normalize(); const pole=hd.clone().multiplyScalar(0.85).addScaledVector(J.fwd,-0.55).normalize();
  hair.position.copy(J.head); hair.scale.setScalar(0.13*1.05); hair.quaternion.setFromUnitVectors(UPV,pole); }
const ROOT=V(MANX,0,BACKZ+0.08+HIPBACK), YAW=yawOf(FACE_Z);
const SEAT={...R.P0,p:0.07,tilt:0.0,aL:1.5,aR:1.47,kL:1.52,kR:1.47,sL:0.5,sR:0.5,eL:0.9,eR:0.9};
const side=V(1,0,0);
const phoneTop=PH.clone().add(V(0,0.035,0));
function hands(P,tL,tR){ Object.assign(P,{tL,tR,wL:1,wR:1,pL:V(-0.3,-0.8,0.7),pR:V(-0.3,-0.8,-0.7)}); return P; }
// hook pose (frame 0 and the last frame are identical): upright, looking at the phone that has just lit, one hand resting on it
function hookPose(t){ const P={...SEAT,p:0.1+0.008*Math.sin(t*1.6),tilt:0.26}; return hands(P,V(-0.12,TOP+0.03,-0.22),phoneTop.clone().add(V(-0.07,0,-0.02))); }
function billPose(t){ const k=clamp((t-BILLS[0].t)/(TL.zero-BILLS[0].t)); const P={...SEAT,p:lerp(0.14,0.4,k)+0.008*Math.sin(t*1.5),tilt:lerp(0.3,0.5,k)};
  let pulse=0; BILLS.forEach(b=>{ pulse=Math.max(pulse,bump(t,b.t-0.15,0.7)); });
  return hands(P,V(-0.14,TOP+0.03,-0.22),phoneTop.clone().add(V(-0.07,0,-0.02)).lerp(SHEET_AT.clone().add(V(0.12,0.06,-0.05)),pulse)); }
function headHandPose(t){ const P={...SEAT,p:0.42,tilt:0.42,hy:0.12,ty:0.05}; const J0=R.skel(P,ROOT,YAW);
  return hands(P,PH.clone().add(V(0.0,0.03,-0.13)).setX(0.2),J0.head.clone().addScaledVector(J0.fwd,0.06).addScaledVector(side,-0.07)); }
function typePose(t){ const k=wu(t); const P={...SEAT,p:lerp(0.2,0.46,k),tilt:lerp(0.3,0.5,k),hy:0}; const ty=Math.sin(t*15); const kb=V(0.1,TOP+0.05,-0.14);
  return hands(P,kb.clone().add(V(-0.07,0.01*Math.max(0,ty),0)),kb.clone().add(V(0.07,0.01*Math.max(0,-ty),0))); }
const blendP=(a,b,u)=>R.blend(a,b,ease(clamp(u)));
function poseAt(t){ const Z=TL.zero, W0=WK[0], W1=WK[1];
  if(t<BILLS[0].t) return hookPose(t);
  if(t<Z-0.3) return blendP(hookPose(t),billPose(t),(t-BILLS[0].t)/0.5);
  if(t<W0-0.3) return blendP(billPose(t),headHandPose(t),(t-(Z-0.3))/0.6);
  if(t<W1) return blendP(headHandPose(t),typePose(t),(t-(W0-0.3))/0.5);
  if(t<TL.next-0.7) return blendP(typePose(t),hookPose(t),(t-W1)/1.4);
  return hookPose(t); }

// ---------------------------------------------------------------- camera: wide, small man; a slow push-in that returns to its start (clean loop)
function setT(t){
  const P=poseAt(t); const J=R.skel(P,ROOT,YAW); R.poseFig(man,J); placeHair(J);
  drawPhone(t); placeSheets(t);
  // calendar
  const cr=crossedAt(t), cc=dayAt(t), key=cr+'|'+cc; if(CAL.key!==key){ CAL.key=key; drawCal(CAL.g,512,660,cr,cc); CAL.t.needsUpdate=true; }
  const fp=sstep(TL.flipPage[0],TL.flipPage[1],t); CALPIVOT.scale.y=Math.max(0.02,1-fp); CALPIVOT.visible=t<TL.flipPage[1]&&!(t<0.001&&false);
  calFront.visible=t<TL.flipPage[1]; calBack.visible=true;
  // clock: 11:00 at rest; twelve evenings fly by during the work and it lands on 11:00 again
  const wr=ease(wu(t)); const turns=12*wr; mHand.rotation.z=-turns*Math.PI*2; hHand.rotation.z=-((11/12)+turns/12)*Math.PI*2;
  // laptop opens as he starts
  const open=sstep(WK[0]-0.5,WK[0]-0.1,t)*(1-sstep(TL.flipPage[0]-0.2,TL.flipPage[0]+0.5,t)); lid.rotation.x=lerp(-Math.PI/2+0.02,0.25,open); lapLight.intensity=0.12*open;
  // wallet notes, cups, papers
  walletNotes.forEach((n,i)=>{ n.visible=balanceAt(t)>[0,10000,20000,30000,40000][i]||t>=TL.next; });
  const w=wr; workPile.visible=t>=WK[0]&&t<TL.flipPage[0]; workPile.scale.y=0.15+3.0*w; workPile.position.y=TOP+0.0125+0.05*workPile.scale.y*0.5*1.0+0.01;
  extraCups.forEach((c,i)=>{ c.visible=t>=WK[0]+[0.25,0.5,0.75][i]*(WK[1]-WK[0])&&t<TL.flipPage[0]; });
  // lamp: a stumble the moment the balance hits zero, a little lower while he works, back to full for the loop
  const dip=bump(t,TL.zero-0.05,0.35); const lowt=sstep(TL.zero,TL.zero+0.6,t)*(1-sstep(WK[1]+0.2,TL.next,t)); const lk=(1-0.85*dip)*(1-0.12*lowt);
  S.spot.intensity=3.6*lk; spill.intensity=1.6*lk; shadeM.emissiveIntensity=1.25*lk; halo.material.opacity=0.55*lk; halo2.material.opacity=0.16*lk;
  const ph=t<BILLS[0].t||t>=TL.next; phHalo.material.opacity=ph?0.34:0.16; phLight.intensity=ph?0.3:0.14;
  // camera
  const k=Math.sin(Math.PI*t/DUR); S.cam.position.set(0.06,1.75,7.7-0.6*k); S.cam.lookAt(0.0,0.98,-0.4);
  S.tick(t); S.beamU.uI.value=0; S.moteU.uOp.value=0.35; }
window.events={...TL};
window.renderAt=(t,K=3)=>S.renderAt(setT,t,K,{t0:0,t1:DUR});
window.ready=true;
