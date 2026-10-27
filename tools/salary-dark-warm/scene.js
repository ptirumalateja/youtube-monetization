// The Salary Loop, dark-warm restyle (reference stills). Teja's brief (27 Oct 2026): dark but not black, sad-real, not depressing.
// One wooden man alone at a table at 11 pm. The only light is a table lamp (warm, about 3000 K); the room falls off to charcoal and
// deep navy, never #000. Wall calendar (flips slowly in the full cut), wall clock at 11, a night window, his phone, an empty wallet.
// ?v=after (default): Day 24, balance 0, head in his hand.  ?v=before: Day 1, salary just credited, sitting up, phone lit.
// Units are metres; floor y = 0; the camera is on +z. Built on the Slow Light Dark kit (sld.js, with bg/fog/lift/vig options).
import * as THREE from 'three';
import * as SLD from './sld.js';
const {V,clamp,lerp,rng,yawOf,PAL,UPV}=SLD;
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960;
const AFTER=(q.get('v')||'after')!=='before';

// ---------------------------------------------------------------- palette: charcoal / deep navy room, one 3000 K lamp
const BG=0x161b25, K3000=0xffb46b;
const TOP=0.74, LAMPP=V(-0.52,TOP,-0.16), BULB=LAMPP.clone().add(V(0,0.4,0));
const S=SLD.createStage({W,H,lamp:BULB,lampTarget:V(-0.05,0,0.12),cone:1.05,spot:3.6,beam:0.0,motes:500,bg:BG,fogD:0.06,lift:[0.011,0.0135,0.021],vig:0.42,fov:36});
const R=SLD.createRig(S.scene);
S.spot.color.setHex(K3000); S.spot.penumbra=0.9; S.spot.decay=1.6; S.spot.shadow.camera.near=0.05; S.spot.shadow.camera.far=6; S.spot.shadow.radius=6;
S.moteU.uCol.value.setHex(0xffc890);
S.floor.material.color.setHex(0x40342b);
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
const BRASS=std(0x6a5332,'brass',{r:0.38,m:0.5,rim:0.15});
{ const base=add(new THREE.CylinderGeometry(0.085,0.1,0.03,32),BRASS); base.position.copy(LAMPP).add(V(0,0.015,0));
  const stem=add(new THREE.CylinderGeometry(0.011,0.011,0.32,12),BRASS); stem.position.copy(LAMPP).add(V(0,0.19,0));
  const shadeM=new THREE.MeshStandardMaterial({color:0xf1d7a8,roughness:0.9,emissive:0xffb050,emissiveIntensity:1.25,side:THREE.DoubleSide});
  const shade=add(new THREE.CylinderGeometry(0.085,0.16,0.17,40,1,true),shadeM,S.scene,false); shade.position.copy(LAMPP).add(V(0,0.43,0));
  const bulb=add(new THREE.SphereGeometry(0.035,20,14),new THREE.MeshBasicMaterial({color:0xfff0d0}),S.scene,false); bulb.position.copy(BULB);
  const halo=SLD.glowSprite(S.scene,0xffb868,0.55); halo.position.copy(BULB).add(V(0,0.03,0)); halo.scale.setScalar(0.9);
  const halo2=SLD.glowSprite(S.scene,0xff9a40,0.16); halo2.position.copy(BULB).add(V(0,0.03,0)); halo2.scale.setScalar(2.6); }
// lamp at the edge of the table; the spot hangs in the shade (no visible beam, just the pool of light)
S.spot.position.copy(BULB); S.spot.target.position.set(-0.05,0,0.12); S.spot.target.updateMatrixWorld(); S.spot.angle=1.12;

// ---------------------------------------------------------------- the wall: calendar, clock at 11, a night window
const DAY=AFTER?24:1;
const calTex=canvasTex(512,660,(g,w,h)=>{ g.fillStyle='#efe8dc'; g.fillRect(0,0,w,h); g.fillStyle='#b8432f'; g.fillRect(0,0,w,96); g.fillStyle='#fff'; g.font='bold 56px monospace'; g.textAlign='center'; g.fillText('OCTOBER',w/2,68);
  g.fillStyle='#3a3530'; g.font='bold 30px monospace'; const cw=64,ch=86; for(let i=0;i<31;i++){ const x=32+(i%7)*cw+cw/2, y=172+Math.floor(i/7)*ch; g.fillStyle=i<6?'#3a3530':'#5a544c'; g.fillText(String(i+1),x,y);
    if(i<DAY-1){ g.strokeStyle='#b8432f'; g.lineWidth=5; g.beginPath(); g.moveTo(x-22,y-32); g.lineTo(x+22,y+8); g.moveTo(x+22,y-32); g.lineTo(x-22,y+8); g.stroke(); } }
  { const i=DAY-1, x=32+(i%7)*cw+cw/2, y=172+Math.floor(i/7)*ch; g.strokeStyle='#b8432f'; g.lineWidth=6; g.beginPath(); g.ellipse(x,y-12,32,30,0.2,0,7); g.stroke(); } });
const cal=add(new THREE.PlaneGeometry(0.5,0.645),std(0xffffff,'cal',{r:0.9,rim:0,map:calTex}),S.scene,false); cal.position.set(0.62,1.62,WALLZ+0.012);
box(0.012,0.012,0.02,BRASS,0.62,1.96,WALLZ+0.02);
// clock: 11:00 (hour hand at 11, minute at 12)
{ const g=new THREE.Group(); g.position.set(-0.52,1.86,WALLZ+0.02); S.scene.add(g);
  const face=add(new THREE.CylinderGeometry(0.15,0.15,0.02,48),std(0xe8e0d0,'clk',{r:0.6,rim:0}),g); face.rotation.x=Math.PI/2;
  const rimM=add(new THREE.TorusGeometry(0.15,0.014,10,48),std(0x2a221a,'clkr',{r:0.5,rim:0.1}),g);
  const hand=(len,wd,ang,col)=>{ const m=add(new THREE.BoxGeometry(wd,len,0.006),std(col,'hand'+len,{r:0.5,rim:0}),g,false); m.geometry.translate(0,len/2-0.01,0); m.position.z=0.016; m.rotation.z=-ang; };
  hand(0.085,0.014,(11/12)*Math.PI*2,0x1c1814); hand(0.12,0.009,AFTER?0.03:0.0,0x1c1814);
  for(let i=0;i<12;i++){ const a=i/12*Math.PI*2; const tk=add(new THREE.BoxGeometry(0.008,0.022,0.004),std(0x2a221a,'tick',{r:0.5,rim:0}),g,false); tk.position.set(Math.sin(a)*0.125,Math.cos(a)*0.125,0.013); tk.rotation.z=-a; } }
// window at the right: deep-navy night, a few lit windows across the street
{ const nightTex=canvasTex(512,640,(g,w,h)=>{ const gr=g.createLinearGradient(0,0,0,h); gr.addColorStop(0,'#0e1630'); gr.addColorStop(1,'#1b2440'); g.fillStyle=gr; g.fillRect(0,0,w,h);
    const Rn=rng(11); for(let b=0;b<5;b++){ const bx=b*110-20+Rn()*30, bw=90+Rn()*40, by=260+Rn()*200; g.fillStyle='#0a0f1e'; g.fillRect(bx,by,bw,h-by);
      for(let yy=by+16;yy<h-10;yy+=34) for(let xx=bx+10;xx<bx+bw-14;xx+=24) if(Rn()<0.13){ g.fillStyle=Rn()<0.7?'rgba(255,190,110,0.85)':'rgba(170,200,255,0.7)'; g.fillRect(xx,yy,12,16); } }
    g.fillStyle='rgba(255,255,255,0.8)'; g.beginPath(); g.arc(400,90,18,0,7); g.fill(); });
  const fr=std(0x241a12,'wfr',{r:0.6,rim:0.06}); const win=new THREE.Group(); win.position.set(1.3,1.62,WALLZ+0.02); S.scene.add(win);
  const gl=new THREE.Mesh(new THREE.PlaneGeometry(0.72,0.9),new THREE.MeshBasicMaterial({map:nightTex,fog:false,color:0x9aa6c0})); gl.position.z=0.005; win.add(gl);
  box(0.8,0.05,0.06,fr,0,0.47,0.02,win); box(0.8,0.05,0.06,fr,0,-0.47,0.02,win); box(0.05,0.98,0.06,fr,-0.38,0,0.02,win); box(0.05,0.98,0.06,fr,0.38,0,0.02,win);
  box(0.03,0.9,0.05,fr,0,0,0.02,win); box(0.72,0.03,0.05,fr,0,0.05,0.02,win);
  box(0.9,0.04,0.12,fr,0,-0.5,0.06,win); }

// ---------------------------------------------------------------- on the table: his phone, the empty wallet, the bills, a cold cup of tea
const PH=V(0.2,TOP,0.12);
const phScr=canvasTex(300,600,(g,w,h)=>{ g.fillStyle='#0c0f14'; g.fillRect(0,0,w,h); g.textAlign='center';
  g.fillStyle='#8a93a6'; g.font='bold 26px monospace'; g.fillText(AFTER?'A/C BALANCE':'SALARY CREDITED',w/2,220);
  g.fillStyle=AFTER?'#ff5a4a':'#5fe08a'; g.font='bold 78px monospace'; g.fillText(AFTER?'₹0':'+₹50,000',w/2,320);
  g.fillStyle='#5a6274'; g.font='22px monospace'; g.fillText(AFTER?'24 OCT  23:02':'01 OCT  23:02',w/2,380); });
const phone=new THREE.Group(); S.scene.add(phone); phone.position.copy(PH).add(V(0,0.005,0)); phone.rotation.y=0.35;
{ const b=add(new THREE.BoxGeometry(0.078,0.009,0.158),std(0x15171b,'ph',{r:0.3,rim:0.2}),phone);
  const sm=new THREE.MeshStandardMaterial({color:0x000000,roughness:0.25,emissive:0xffffff,emissiveMap:phScr,emissiveIntensity:AFTER?0.9:1.1}); const s=add(new THREE.PlaneGeometry(0.07,0.14),sm,phone,false); s.rotation.x=-Math.PI/2; s.position.y=0.0047; }
const phHalo=SLD.glowSprite(S.scene,AFTER?0xff7060:0x80ffb0,AFTER?0.05:0.14); phHalo.position.copy(PH).add(V(0,0.04,0)); phHalo.scale.setScalar(0.32);
const phLight=new THREE.PointLight(AFTER?0xff8070:0x9affc0,AFTER?0.12:0.14,0.9,2); phLight.position.copy(PH).add(V(0,0.12,0.02)); S.scene.add(phLight);
// wallet: open, empty (after) / fat with notes (before)
{ const w=new THREE.Group(); S.scene.add(w); w.position.set(0.44,TOP+0.006,0.14); w.rotation.y=-0.3;
  const wm=std(0x6a2e20,'wal',{r:0.55,rim:0.1}), im=std(0xc9b898,'wali',{r:0.8,rim:0.05});
  for(const sx of [-1,1]){ const p=new THREE.Group(); w.add(p); p.position.x=sx*0.004; p.rotation.z=sx*(AFTER?-0.05:-0.02);
    box(0.105,0.01,0.14,wm,sx*0.055,0,0,p); box(0.095,0.004,0.13,im,sx*0.055,0.007,0,p); }
  if(!AFTER) for(let i=0;i<5;i++) box(0.09,0.003,0.05,std(0xcfe0b5,'note'+i,{r:0.8,rim:0.05,e:0x9fd08a,ei:0.12}),0.055+i*0.002,0.012+i*0.003,-0.01+i*0.004,w); }
// bills: a small pile, the top one stamped PAID (after: the pile is bigger)
{ const billTex=canvasTex(256,340,(g,w,h)=>{ g.fillStyle='#ece6da'; g.fillRect(0,0,w,h); g.fillStyle='#3a3530'; g.font='bold 22px monospace'; g.fillText('RENT  OCT',18,40); g.fillStyle='#8a847a';
    for(let i=0;i<8;i++) g.fillRect(18,70+i*24,120+((i*53)%90),6); g.save(); g.translate(150,250); g.rotate(-0.3); g.strokeStyle='#b8432f'; g.lineWidth=5; g.strokeRect(-70,-26,140,52); g.fillStyle='#b8432f'; g.font='bold 34px monospace'; g.textAlign='center'; g.fillText('PAID',0,12); g.restore(); });
  const n=AFTER?6:1; for(let i=0;i<n;i++){ const sh=add(new THREE.BoxGeometry(0.15,0.0025,0.2),std(0xffffff,'bill'+(i===n-1?'t':''),{r:0.9,rim:0.03,map:i===n-1?billTex:null}));
    sh.position.set(-0.16+0.012*Math.sin(i*2.1),TOP+0.0015+i*0.003,0.16+0.01*Math.cos(i*1.7)); sh.rotation.y=0.25-0.12*i+(i%2?0.2:0); } }
// cup of tea, gone cold (after) / steaming (before)
{ const cup=add(new THREE.CylinderGeometry(0.035,0.028,0.085,24),std(0xd8d2c6,'cup',{r:0.35,rim:0.12})); cup.position.set(-0.2,TOP+0.0425,-0.2);
  const tea=add(new THREE.CylinderGeometry(0.031,0.031,0.004,24),std(0x6a3e1c,'tea',{r:0.2,rim:0})); tea.position.set(-0.2,TOP+0.075,-0.2);
  if(!AFTER){ const st=SLD.glowSprite(S.scene,0xffe0b0,0.12); st.position.set(-0.2,TOP+0.17,-0.2); st.scale.setScalar(0.18); } }

// ---------------------------------------------------------------- him: the cream wooden figure, dark hair cap
const man=R.makeFig(PAL.CREAM,'man',{rim:0.16,lift:0.04});
const hair=add(new THREE.SphereGeometry(1,26,16,0,Math.PI*2,0,Math.PI*0.5),std(0x2b1f18,'hair',{r:0.85,rim:0.1}));
function placeHair(J){ const hd=J.head.clone().sub(J.neck).normalize(); const pole=hd.clone().multiplyScalar(0.85).addScaledVector(J.fwd,-0.55).normalize();
  hair.position.copy(J.head); hair.scale.setScalar(0.13*1.05); hair.quaternion.setFromUnitVectors(UPV,pole); }
const ROOT=V(MANX,0,BACKZ+0.08+HIPBACK), YAW=yawOf(FACE_Z);
const SEAT={...R.P0,p:0.07,tilt:0.0,aL:1.5,aR:1.47,kL:1.52,kR:1.47,sL:0.5,sR:0.5,eL:0.9,eR:0.9};
function pose(){
  const side=V(1,0,0);   // his left as we look at him is our right (+x)
  if(AFTER){ // slumped forward, forehead in his right hand (elbow on the table), left hand flat beside the phone
    const P={...SEAT,p:0.42,tilt:0.42,hy:0.12,ty:0.05};
    const J0=R.skel(P,ROOT,YAW);
    P.tR=J0.head.clone().addScaledVector(J0.fwd,0.06).addScaledVector(side,-0.07).add(V(0,0.0,0)); P.wR=1; P.pR=V(0.2,-1.0,-0.6);
    P.tL=PH.clone().add(V(0.0,0.03,-0.13)); P.wL=1; P.pL=V(-0.2,-0.8,0.8);
    return R.skel(P,ROOT,YAW); }
  // before: sitting up, phone in both hands near the table edge, head tilted down to it
  const P={...SEAT,p:0.18,tilt:0.3,hy:0.05};
  P.tR=PH.clone().add(V(-0.05,0.09,-0.12)); P.wR=1; P.pR=V(-0.3,-0.8,-0.7);
  P.tL=PH.clone().add(V(0.05,0.09,-0.12)); P.wL=1; P.pL=V(-0.3,-0.8,0.7);
  return R.skel(P,ROOT,YAW); }
if(!AFTER){ phone.position.copy(PH).add(V(0,0.1,-0.1)); phone.rotation.set(-0.9,0,0); phHalo.position.copy(phone.position); phLight.position.copy(phone.position).add(V(0,0.1,0.1)); }

// ---------------------------------------------------------------- camera
const CAM=JSON.parse(q.get('cam')||'null')||{p:[0.72,1.3,2.55],l:[0.06,0.98,-0.4]};
function setT(t){ const J=pose(); R.poseFig(man,J); placeHair(J);
  S.cam.position.set(...CAM.p); S.cam.lookAt(...CAM.l);
  S.tick(t); S.beamU.uI.value=0; S.moteU.uOp.value=0.35; }
window.events={};
window.renderAt=(t,K=3)=>S.renderAt(setT,t,K,{});
window.ready=true;
