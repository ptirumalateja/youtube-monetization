// Ghosts of Almost (Tiny Stick Tales), Nov 2026.
// One pictogram stickman (the sleep-reel / profile hero: near-black, warm rim, thin stick limbs, floating head, glowing face)
// and behind him a crowd of see-through copies of himself, each holding a glowing unfinished thing.
// renderAt(t) is pure (no state between frames), so frames can render in parallel workers.
import * as THREE from 'three';
import * as SLD from './sld.js';
import {createFace,EX,NEUTRAL,mix} from './face.js';
const {V,keys,clamp,lerp,rotY}=SLD;
const q=new URLSearchParams(location.search); const W=+q.get('w')||1080, H=+q.get('h')||1920;

// ---------------------------------------------------------------- stage: dark-warm (30 Friends look), weak vignette, no black edges
const ST=SLD.createStage({W,H,lamp:V(0.25,4.4,1.5),lampTarget:V(0,0.7,0),cone:0.3,spot:22,beam:0.06,fov:40,motes:1200,vig:0.22});
const scene=ST.scene; const R=SLD.createRig(scene);
const BG=0x3a271d; scene.background=new THREE.Color(BG); scene.fog=new THREE.FogExp2(BG,0.03);
ST.refl.visible=false;
{ const c=document.createElement('canvas'); c.width=c.height=1024; const g=c.getContext('2d'); const gr=g.createRadialGradient(512,470,10,512,512,520);
  gr.addColorStop(0,'#5c3f2e'); gr.addColorStop(0.3,'#45301f'); gr.addColorStop(0.7,'#3d2a1f'); gr.addColorStop(1,'#3a271d'); g.fillStyle=gr; g.fillRect(0,0,1024,1024);
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; const fm=ST.floor.material; fm.map=t; fm.roughnessMap=null; fm.color.set(0xffffff); fm.opacity=1; fm.transparent=false;
  fm.emissive=new THREE.Color(0xffffff); fm.emissiveMap=t; fm.emissiveIntensity=0.55; fm.needsUpdate=true; ST.floor.scale.set(0.5,0.5,1); ST.floor.position.z=-4; }
{ const c=document.createElement('canvas'); c.width=512; c.height=1024; const g=c.getContext('2d');
  const gr=g.createRadialGradient(256,560,20,256,560,640); gr.addColorStop(0,'#5a3b2a'); gr.addColorStop(0.35,'#3a271d'); gr.addColorStop(0.7,'#3a271d'); gr.addColorStop(1,'#2e1f17');
  g.fillStyle=gr; g.fillRect(0,0,512,1024); const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace;
  const m=new THREE.Mesh(new THREE.PlaneGeometry(30,60),new THREE.MeshBasicMaterial({map:t,fog:false})); m.position.set(0,6,-16); scene.add(m); }

// ---------------------------------------------------------------- pictogram figure (same build as tools/stickman-profile)
const PT={len:0.58,hipR:0.07,shR:0.132,capB:0.05,capT:0.075,limb:0.024}; const HEADR=0.165, HIPY=0.92;
const TORSO=(()=>{ const pts=[], L=PT.len, N=14;
  for(let k=0;k<=N;k++){ const a=k/N*Math.PI/2; pts.push(new THREE.Vector2(PT.hipR*Math.sin(a),(PT.capB*(1-Math.cos(a)))/L-0.5)); }
  for(let k=1;k<N;k++){ const u=k/N, y=PT.capB+u*(L-PT.capB-PT.capT); pts.push(new THREE.Vector2(PT.hipR+(PT.shR-PT.hipR)*Math.pow(u,1.4),y/L-0.5)); }
  for(let k=0;k<=N;k++){ const a=k/N*Math.PI/2; pts.push(new THREE.Vector2(PT.shR*Math.cos(a)**0.6,(L-PT.capT+PT.capT*Math.sin(a))/L-0.5)); }
  const g=new THREE.LatheGeometry(pts,40); g.computeVertexNormals(); return g; })();
const CYL=new THREE.CylinderGeometry(1,1,1,14,1,true), SPH=new THREE.SphereGeometry(1,24,16);
function makeFig(mat,shadow,faceSize){ const mk=g=>{ const m=new THREE.Mesh(g,mat); m.frustumCulled=false; m.castShadow=shadow; m.receiveShadow=shadow; scene.add(m); return m; };
  const F={mat,torso:mk(TORSO),bones:[...Array(8)].map(()=>mk(CYL)),joints:[...Array(12)].map(()=>mk(SPH)),head:mk(SPH),face:createFace(scene,{size:faceSize})};
  F.all=[F.torso,...F.bones,...F.joints,F.head]; return F; }
function boneTo(m,a,b,r){ const d=b.clone().sub(a); const len=Math.max(d.length(),1e-4); m.position.copy(a).add(b).multiplyScalar(0.5); m.scale.set(r,len,r); m.quaternion.setFromUnitVectors(SLD.UPV,d.multiplyScalar(1/len)); m.visible=true; }
const ball=(m,p,r)=>{ m.position.copy(p); m.scale.setScalar(r); m.visible=true; };

// standing body in the figure's local frame (faces +z, its left = +x), then placed at pos with yaw.
// o: pos, yaw, lean (fwd), roll, nod, turn (head yaw), tilt (head roll), hL/hR local hand targets, pL/pR elbow poles, step
function figJ(o){ const yaw=o.yaw||0, P=v=>rotY(v,yaw).add(o.pos), Dv=v=>rotY(v,yaw);
  const d=V(Math.sin(o.roll||0),Math.cos(o.roll||0),0).applyAxisAngle(V(1,0,0),o.lean||0).normalize();
  const n=V(0,0,1).applyAxisAngle(V(1,0,0),o.lean||0); const l=d.clone().cross(n).normalize();   // +x
  const hip=V(0,HIPY,0), neck=hip.clone().addScaledVector(d,PT.len);
  let hd=d.clone().applyAxisAngle(n,o.tilt||0); const nod=o.nod||0; hd=hd.multiplyScalar(Math.cos(nod)).addScaledVector(n,Math.sin(nod)).normalize();
  let f=n.clone().multiplyScalar(Math.cos(nod)).addScaledVector(d,-Math.sin(nod)).normalize(); f=f.applyAxisAngle(hd,o.turn||0);
  const J={hip:P(hip),neck:P(neck),d:Dv(d),head:P(neck.clone().addScaledVector(hd,0.045+HEADR)),hd:Dv(hd),f:Dv(f)};
  for(const [s,sg] of [['L',1],['R',-1]]){ const S=neck.clone().addScaledVector(d,-0.075).addScaledVector(l,sg*0.125);
    const T=o['h'+s]||hip.clone().addScaledVector(l,sg*0.19).add(V(0,-0.03,0.04));
    const r=R.ik(P(S),P(T),Dv(o['p'+s]||l.clone().multiplyScalar(sg).add(V(0,-0.6,-0.3))));
    J['sh'+s]=P(S); J['el'+s]=r.E; J['h'+s]=r.Hd;
    const st=(o.step||0)*sg, hp=hip.clone().addScaledVector(l,sg*0.065).add(V(0,-0.02,0)), ft=V(sg*0.1,0.03,0.02+st);
    J['hp'+s]=P(hp); J['ft'+s]=P(ft); J['kn'+s]=P(hp.clone().add(ft).multiplyScalar(0.5).add(V(sg*0.008,0,0.03))); }
  return J; }
function poseFig(F,J,ex,faceOn=true){ const r=PT.limb, d=J.d;
  const a=J.hip.clone().addScaledVector(d,-PT.capB), b=J.neck.clone().addScaledVector(d,0.012), dd=b.clone().sub(a), len=dd.length();
  F.torso.position.copy(a).add(b).multiplyScalar(0.5); F.torso.scale.set(1,len,1); F.torso.quaternion.setFromUnitVectors(V(0,1,0),dd.normalize()); F.torso.visible=true;
  const B=F.bones, Jt=F.joints;
  boneTo(B[0],J.hpL,J.knL,r); boneTo(B[1],J.knL,J.ftL,r); boneTo(B[2],J.hpR,J.knR,r); boneTo(B[3],J.knR,J.ftR,r);
  boneTo(B[4],J.shL,J.elL,r); boneTo(B[5],J.elL,J.hL,r); boneTo(B[6],J.shR,J.elR,r); boneTo(B[7],J.elR,J.hR,r);
  ball(Jt[0],J.knL,r*1.05); ball(Jt[1],J.knR,r*1.05); ball(Jt[2],J.ftL,r*1.7); ball(Jt[3],J.ftR,r*1.7);
  ball(Jt[4],J.shL,r*1.6); ball(Jt[5],J.shR,r*1.6); ball(Jt[6],J.elL,r*1.05); ball(Jt[7],J.elR,r*1.05); ball(Jt[8],J.hL,r*1.45); ball(Jt[9],J.hR,r*1.45);
  ball(Jt[10],J.hpL,r*1.1); ball(Jt[11],J.hpR,r*1.1);
  ball(F.head,J.head,HEADR); F.face.draw({...NEUTRAL,...ex}); F.face.place(J.head,J.f,J.hd,HEADR,faceOn); }

// hero: near-black with the warm rim (profile build)
const heroMat=SLD.rimify(new THREE.MeshStandardMaterial({color:0x0d0b0a,roughness:0.62,metalness:0}),0xffc27a,0.6,'hero');
const hero=makeFig(heroMat,true,512);

// ghost: see-through copy. Fresnel shell, additive, feet dissolve, fades with distance.
function ghostMat(col){ return new THREE.ShaderMaterial({uniforms:{uCol:{value:new THREE.Color(col)},uOp:{value:1},uBase:{value:0}},transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,fog:false,
  vertexShader:`varying vec3 vN; varying vec3 vV; varying vec3 vW; void main(){ vec4 w=modelMatrix*vec4(position,1.0); vW=w.xyz; vec4 mv=viewMatrix*w; vV=-mv.xyz; vN=normalize(normalMatrix*normal); gl_Position=projectionMatrix*mv; }`,
  fragmentShader:`uniform vec3 uCol; uniform float uOp,uBase; varying vec3 vN; varying vec3 vV; varying vec3 vW;
    void main(){ float fr=pow(1.0-abs(dot(normalize(vN),normalize(vV))),2.2); float feet=smoothstep(uBase-0.02,uBase+0.6,vW.y);
      float dist=length(vV); float a=(0.11+0.85*fr)*feet*uOp*exp(-max(dist-3.5,0.0)*0.06); gl_FragColor=vec4(uCol*a,1.0); }`}); }

// ---------------------------------------------------------------- the unfinished things (canvas cards + a 3D gym bag)
function card(w,h,px,draw){ const c=document.createElement('canvas'); c.width=px; c.height=Math.round(px*h/w); const g=c.getContext('2d'); draw(g,c.width,c.height);
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; t.anisotropy=8;
  const m=new THREE.Mesh(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({map:t,transparent:true,side:THREE.DoubleSide,fog:false,depthWrite:false}));
  m.material.color.setScalar(0.7); m.renderOrder=4; return m; }
const rr=(g,x,y,w,h,r)=>{ g.beginPath(); g.roundRect(x,y,w,h,r); };
const FONT='"Inter","DejaVu Sans",sans-serif';
const ITEMS={
  msg:()=>card(0.13,0.24,260,(g,w,h)=>{ rr(g,0,0,w,h,30); g.fillStyle='#10131a'; g.fill(); rr(g,10,10,w-20,h-20,22); g.fillStyle='#e9f1ff'; g.fill();
    g.fillStyle='#7d8aa3'; g.font=`600 20px ${FONT}`; g.fillText('Dad',24,52);
    rr(g,22,80,170,58,18); g.fillStyle='#d3dbe8'; g.fill(); g.fillStyle='#38404e'; g.font=`20px ${FONT}`; g.fillText('you free sunday?',34,116);
    rr(g,20,h-92,w-40,58,28); g.fillStyle='#ffffff'; g.fill(); g.strokeStyle='#9aa7bd'; g.lineWidth=3; g.stroke();
    g.fillStyle='#1d2330'; g.font=`22px ${FONT}`; g.fillText("I'm sorry I nev",36,h-54); g.fillStyle='#3d7bff'; g.fillRect(196,h-76,3,30); }),
  video:()=>card(0.24,0.14,420,(g,w,h)=>{ rr(g,0,0,w,h,26); g.fillStyle='#10131a'; g.fill(); rr(g,10,10,w-20,h-20,18);
    const gr=g.createLinearGradient(0,0,w,h); gr.addColorStop(0,'#ffcf8a'); gr.addColorStop(1,'#ff7a59'); g.fillStyle=gr; g.fill();
    g.fillStyle='rgba(255,255,255,0.95)'; g.beginPath(); g.moveTo(w/2-26,h/2-32); g.lineTo(w/2+34,h/2); g.lineTo(w/2-26,h/2+32); g.fill();
    g.fillStyle='#ff2d2d'; g.beginPath(); g.arc(38,40,11,0,7); g.fill(); g.fillStyle='#fff'; g.font=`700 22px ${FONT}`; g.fillText('DRAFT',56,48);
    g.fillStyle='rgba(0,0,0,0.45)'; g.fillRect(20,h-44,w-40,8); g.fillStyle='#fff'; g.fillRect(20,h-44,(w-40)*0.12,8); }),
  plan:()=>card(0.2,0.27,300,(g,w,h)=>{ g.fillStyle='#fbf3e2'; g.fillRect(0,0,w,h); g.fillStyle='#2a2320'; g.font=`800 26px ${FONT}`; g.fillText('BUSINESS PLAN',24,52);
    g.font=`20px ${FONT}`; ['1. The idea  ✓','2. Who buys it','3. Money'].forEach((s,i)=>g.fillText(s,26,100+i*36));
    g.strokeStyle='#2a2320'; g.lineWidth=2; g.beginPath(); g.moveTo(26,226); g.lineTo(130,226); g.stroke();
    g.strokeStyle='#d8cfbf'; for(let i=0;i<5;i++){ g.beginPath(); g.moveTo(26,262+i*30); g.lineTo(w-26,262+i*30); g.stroke(); } }),
  book:()=>card(0.19,0.25,300,(g,w,h)=>{ g.fillStyle='#f6eedd'; g.fillRect(0,0,w,h); g.fillStyle='#8a2f2f'; g.fillRect(0,0,16,h);
    g.fillStyle='#2a2320'; g.font=`italic 700 28px ${FONT}`; g.fillText('Chapter 1',36,60); g.font=`17px ${FONT}`;
    ['It was raining the night','she finally left the city,','and nobody'].forEach((s,i)=>g.fillText(s,36,104+i*28));
    g.strokeStyle='#e0d6c4'; g.lineWidth=2; for(let i=0;i<7;i++){ g.beginPath(); g.moveTo(36,212+i*28); g.lineTo(w-24,212+i*28); g.stroke(); } }),
  canvas:()=>card(0.26,0.2,360,(g,w,h)=>{ g.fillStyle='#fffaf0'; g.fillRect(0,0,w,h); const sk=g.createLinearGradient(0,0,0,h); sk.addColorStop(0,'#ff9a5a'); sk.addColorStop(1,'#ffd27a');
    g.save(); g.beginPath(); g.rect(0,0,w*0.45,h); g.clip(); g.fillStyle=sk; g.fillRect(0,0,w,h); g.fillStyle='#5a3a6a'; g.beginPath(); g.moveTo(0,h*0.75); g.lineTo(w*0.3,h*0.42); g.lineTo(w*0.6,h*0.8); g.lineTo(0,h); g.fill(); g.restore();
    g.strokeStyle='#9c948a'; g.lineWidth=2; g.beginPath(); g.moveTo(w*0.3,h*0.42); g.lineTo(w*0.6,h*0.8); g.moveTo(w*0.55,h*0.7); g.lineTo(w*0.8,h*0.38); g.lineTo(w,h*0.62); g.stroke();
    g.strokeStyle='#6b4a34'; g.lineWidth=10; g.strokeRect(5,5,w-10,h-10); }),
  bag:()=>{ const o=new THREE.Group(); const m=new THREE.MeshStandardMaterial({color:0x2a1408,emissive:0xff7a2e,emissiveIntensity:1.1,roughness:0.6});
    const body=new THREE.Mesh(new THREE.CapsuleGeometry(0.085,0.22,8,20),m); body.rotation.z=Math.PI/2; o.add(body);
    const strap=new THREE.Mesh(new THREE.TorusGeometry(0.08,0.008,8,24,Math.PI),m); strap.position.y=0.07; o.add(strap);
    const band=new THREE.Mesh(new THREE.CylinderGeometry(0.087,0.087,0.03,24),new THREE.MeshStandardMaterial({color:0xffffff,emissive:0xfff0d8,emissiveIntensity:1.4})); band.rotation.z=Math.PI/2; band.position.x=0.11; o.add(band);
    o.traverse(x=>{ if(x.isMesh){ x.frustumCulled=false; } }); return o; },
};
const ITEMGLOW={msg:0x9fc4ff,video:0xff9a5a,plan:0xffe2b0,book:0xffe2b0,canvas:0xffb070,bag:0xff7a2e};

// ---------------------------------------------------------------- the crowd
const GCOL=0x9cd2ff;
const IS=1.55;   // items drawn larger than life so they read on a phone
const ORDER=['msg','plan','video','bag','book','canvas'];
const ROWS=[4,5,6,7,8];
const FRONT=[{x:-0.62,z:-0.45,type:'msg',pose:'offer'},{x:0.6,z:-0.35,type:'plan',pose:'reach'},{x:-1.2,z:-1.2,type:'video',pose:'hold',ex:{eo:0.7,py:-0.3}},{x:1.22,z:-1.25,type:'bag',pose:'slump',ex:{eo:0.45,py:-0.6}}];
const GH=[]; { const rn=SLD.rng(7); let k=0;
  const mkG=(x,y,z,type,r,pose,ex)=>{ const item=ITEMS[type](); item.scale.setScalar(IS); scene.add(item);
      const glow=SLD.glowSprite(scene,ITEMGLOW[type],0.22);
      const mat=ghostMat(GCOL); const F=makeFig(mat,false,256);
      const dm=new THREE.MeshBasicMaterial({colorWrite:false,depthWrite:true,transparent:true,polygonOffset:true,polygonOffsetFactor:2,polygonOffsetUnits:2}); F.pre=F.all.map(m=>{ const c=new THREE.Mesh(m.geometry,dm); c.frustumCulled=false; scene.add(c); return c; });
      F.face.mesh.material.blending=THREE.AdditiveBlending; F.face.mesh.material.color.set(0x9cc8ff);
      GH.push({F,item,glow,type,pos:V(x,y,z),seed:rn()*6.28,row:r,idx:GH.length,pose,front:r<0,ex}); };
  const PLEAD={...EX.neutral,ba:0.75,by:0.25,mc:-0.3,mw:0.6,pr:0.46};
  FRONT.forEach(f=>mkG(f.x,0.1,f.z,f.type,-1,f.pose,{...PLEAD,...(f.ex||{})}));
  ROWS.forEach((n,r)=>{ const z=-2.3-r*1.2, hs=1.0+0.78*r;
    for(let i=0;i<n;i++){ let x=lerp(-hs,hs,(i+0.5)/n)+(rn()-0.5)*0.35; if(r===0&&Math.abs(x)<0.3) x+=x<0?-0.25:0.25;
      const type=ORDER[k%ORDER.length]; mkG(x,0.18+0.28*r+0.04*rn(),z+(rn()-0.5)*0.4,type,r,'hold',[EX.sigh,{...EX.neutral,ba:0.55,by:0.15,mc:-0.25,py:-0.2},{...EX.sleepy,ba:0.4,mc:-0.1},{...EX.neutral,eo:0.8,ba:0.35,mc:-0.15}][k%4]); k++; } });
  // back-to-front draw order so the per-ghost prepass never hides a farther ghost
  GH.forEach(G=>{ const k=G.front?0.85:0.6*Math.exp(-G.row*0.12); G.item.traverse(m=>{ if(m.material&&m.material.map) m.material.color.setScalar(k); else if(m.material) m.material.emissiveIntensity*=k/0.85; }); G.glow.material.opacity*=G.front?1.3:0.6; });
  [...GH].sort((a,b)=>a.pos.z-b.pos.z).forEach((G,i)=>{ const o=20+i*2; G.F.pre.forEach(m=>m.renderOrder=o); G.F.all.forEach(m=>m.renderOrder=o+1); G.F.face.mesh.renderOrder=o+1.5; G.item.traverse(m=>m.renderOrder=o+1.8); G.glow.renderOrder=o+1.7; }); }

// local hold poses per item type (item centre in the figure's frame; hand targets)
function holdPose(type,br){ const c=V(0,1.18+br,0.24);
  if(type==='bag') return {item:V(0.17,0.5,0.06),itemRot:0,hL:V(0.17,0.6,0.06),pL:V(1,0,-0.3)};
  if(type==='msg') return {item:c.clone().add(V(0,0.02,0.04)),itemRot:-0.25,hL:c.clone().add(V(0.05,-0.15,0.02)),hR:c.clone().add(V(-0.05,-0.15,0.02)),pL:V(1,-0.5,-0.5),pR:V(-1,-0.5,-0.5)};
  const w=IS*{video:0.12,plan:0.1,book:0.095,canvas:0.13}[type];
  return {item:c,itemRot:-0.12,hL:c.clone().add(V(w,-0.07,0)),hR:c.clone().add(V(-w,-0.07,0)),pL:V(1,-0.6,-0.4),pR:V(-1,-0.6,-0.4)}; }

// ---------------------------------------------------------------- labels (paper tags pinned beside a few ghosts)
function tag(text){ const c=document.createElement('canvas'); c.width=640; c.height=160; const g=c.getContext('2d'); g.font=`800 64px ${FONT}`;
  const tw=g.measureText(text).width+64; const x0=(640-tw)/2; rr(g,x0,24,tw,112,14); g.fillStyle='#fff6e4'; g.fill(); g.fillStyle='#2a1d17'; g.textAlign='center'; g.textBaseline='middle'; g.fillText(text,320,82);
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace;
  const s=new THREE.Sprite(new THREE.SpriteMaterial({map:t,transparent:true,fog:false,depthTest:false})); s.renderOrder=9; s.scale.set(0.5,0.125,1); s.visible=false; scene.add(s); return s; }
const nearG=(x,r)=>GH.filter(G=>G.row===r).reduce((a,b)=>Math.abs(b.pos.x-x)<Math.abs(a.pos.x-x)?b:a).idx;
const TAGS=[{g:1,text:'STARTS MONDAY'},{g:2,text:'DRAFT, 2019'},{g:0,text:'NEVER SENT'},{g:3,text:'DAY 1 (OF 1)'}].map(o=>({...o,s:tag(o.text)}));

// hero's phone: the thing he does instead
const PHONE=ITEMS.msg(); PHONE.material.color.setScalar(0.95); PHONE.material.depthWrite=true; PHONE.renderOrder=200; PHONE.material.map.image.getContext('2d'); scene.add(PHONE);
{ const g=PHONE.material.map.image.getContext('2d'); const w=260,h=476; g.fillStyle='#10131a'; g.beginPath(); g.roundRect(0,0,w,h,30); g.fill();
  const gr=g.createLinearGradient(0,0,0,h); gr.addColorStop(0,'#2b3550'); gr.addColorStop(1,'#141a28'); g.fillStyle=gr; g.beginPath(); g.roundRect(10,10,w-20,h-20,22); g.fill();
}
let feedLast=-1; function drawFeed(off){ off=Math.round(off); if(off===feedLast) return; feedLast=off; const g=PHONE.material.map.image.getContext('2d'); const w=260,h=476;
  g.clearRect(0,0,w,h); g.fillStyle='#10131a'; g.beginPath(); g.roundRect(0,0,w,h,30); g.fill();
  g.save(); g.beginPath(); g.roundRect(10,10,w-20,h-20,22); g.clip(); g.fillStyle='#141a28'; g.fillRect(0,0,w,h);
  const cols=['#4a5d8a','#8a4a5d','#4a8a76','#8a7a4a','#5d4a8a'];
  for(let i=-1;i<6;i++){ const k=Math.floor(off/110)+i, y=30+i*110-(off%110); g.fillStyle=cols[((k%5)+5)%5]; g.fillRect(24,y,w-48,80); g.fillStyle='#8fa2c8'; g.fillRect(24,y+86,120,8); }
  g.restore(); PHONE.material.map.needsUpdate=true; }
const PBACK=new THREE.Mesh(new THREE.BoxGeometry(0.13,0.24,0.008),new THREE.MeshStandardMaterial({color:0x15161a,roughness:0.5})); PBACK.position.z=-0.005; PHONE.add(PBACK);
const phoneLight=new THREE.PointLight(0x9fb8ff,0.9,0.42,2); scene.add(phoneLight);

// ---------------------------------------------------------------- timeline
// 0-2.4 hook (crowd already there, he scrolls), 2.4-3.4 he turns to face them.
const CAMK={x:[[0,0],[2.4,0.1],[2.55,0.1],[3.15,0.8],[5,0.66]], y:[[0,1.7],[2.4,1.64],[3.15,1.55],[5,1.55]], z:[[0,3.25],[2.4,2.8],[2.55,2.78],[3.15,2.1],[5,1.85]],
  lx:[[0,0],[2.55,0.02],[3.15,-0.1],[5,-0.12]], ly:[[0,1.3],[2.55,1.36],[3.15,1.48],[5,1.5]], lz:[[0,-1.5],[2.55,-1.5],[3.15,-2.0],[5,-2.0]], fov:[[0,40],[2.55,40],[3.15,46],[5,44]]};
function setT(t){
  const turn=keys([[0,0],[2.55,0],[3.05,1]],t); drawFeed(keys([[0,0],[0.35,0],[0.55,140],[1.05,140],[1.25,290],[1.7,290],[1.9,420]],t));
  // hero
  const hy=Math.PI*0.86*turn, sense=SLD.sstep(2.25,2.45,t);
  const ho={pos:V(0,0,0.15),yaw:hy,nod:lerp(0.32,-0.06,turn),turn:0.32*sense*(1-turn),tilt:-0.04+0.03*Math.sin(t*0.7),
    hL:V(0.045,1.24,0.3),hR:V(-0.045,1.23,0.3),pL:V(1,-0.8,-0.2),pR:V(-1,-0.8,-0.2)};
  const phoneDown=SLD.sstep(2.5,2.95,t); ho.hL.lerp(V(0.19,0.9,0.05),phoneDown); ho.hR.lerp(V(-0.19,0.9,0.05),phoneDown);
  const J=figJ(ho);
  const bored={...EX.neutral,eo:0.62,py:-0.9,ba:0.6,by:0.1,mc:-0.05}; const exH=mix(mix(bored,{...EX.wide,px:0.85,py:-0.2},sense),EX.frozen,SLD.sstep(2.8,3.15,t));
  poseFig(hero,J,exH);
  // phone in his hands (screen toward his face)
  const pc=J.hL.clone().add(J.hR).multiplyScalar(0.5).add(V(0,0.06,0)); PHONE.position.copy(pc);
  PHONE.lookAt(J.head.clone().lerp(ST.cam.position,0.55)); PHONE.material.side=THREE.FrontSide; PHONE.visible=phoneDown<0.6; PHONE.material.opacity=1-phoneDown;
  phoneLight.position.copy(J.head).addScaledVector(J.f,0.24).add(V(0,-0.08,0)); phoneLight.intensity=0.5*(1-phoneDown);
  // ghosts: still, swaying, all staring at him
  for(const G of GH){ const br=0.012*Math.sin(t*1.1+G.seed); let hp=holdPose(G.type,br);
    const look=Math.atan2(J.head.x-G.pos.x,J.head.z-G.pos.z);
    const o={pos:G.pos,yaw:look*(G.front?1:0.85)+0.04*Math.sin(t*0.5+G.seed),roll:0.025*Math.sin(t*0.8+G.seed),nod:0.06+0.04*Math.sin(t*0.6+G.seed*2),tilt:0.12*Math.sin(G.seed*3)};
    const toLocal=p=>rotY(p.clone().sub(G.pos),-o.yaw);
    if(G.pose==='offer'){ o.lean=0.16; o.nod=-0.02; const c=V(0,1.32+br,0.42); hp={item:c,itemRot:0.05,hL:c.clone().add(V(0.05,-0.15,0)),hR:c.clone().add(V(-0.05,-0.15,0)),pL:V(1,-0.8,0),pR:V(-1,-0.8,0)}; }
    if(G.pose==='reach'){ o.lean=0.08+0.06*SLD.sstep(0,2.3,t); const sh=toLocal(J.shR.x<J.shL.x===(G.pos.x>0)?J.shL:J.shR); const side=sh.x>0?1:-1;
      const tgt=V(0,1.38,0).lerp(sh,lerp(0.55,1.0,SLD.sstep(0.2,2.3,t))-0.12*SLD.sstep(2.6,3.0,t)); const c=V(-side*0.24,0.98+br,0.12);
      hp={item:c,itemRot:-0.05,['h'+(side>0?'L':'R')]:tgt,['p'+(side>0?'L':'R')]:V(side,-0.4,-0.6),['h'+(side>0?'R':'L')]:c.clone().add(V(0,0.12,0)),['p'+(side>0?'R':'L')]:V(-side,-0.5,-0.3)}; }
    if(G.front&&G.pose!=='reach') o.lean=(o.lean||0)+0.06*SLD.sstep(0,2.4,t);
    if(G.pose==='slump'){ o.nod=0.38; o.lean=0.08; o.roll=0.06; hp=holdPose('bag',br); }
    Object.assign(o,{hL:hp.hL,hR:hp.hR,pL:hp.pL,pR:hp.pR});
    const GJ=figJ(o); G.F.mat.uniforms.uBase.value=G.pos.y; G.F.mat.uniforms.uOp.value=(G.front?1.45:0.8*Math.exp(-G.row*0.08))*(0.88+0.12*Math.sin(t*1.7+G.seed*5)); poseFig(G.F,GJ,G.ex); G.F.pre.forEach((c,i)=>{ const m=G.F.all[i]; c.position.copy(m.position); c.quaternion.copy(m.quaternion); c.scale.copy(m.scale); c.visible=m.visible; });
    G.F.face.mesh.material.opacity=(G.front?0.85:0.55)*G.F.mat.uniforms.uOp.value*Math.exp(-Math.max(G.row,0)*0.18);
    G.item.position.copy(rotY(hp.item,o.yaw).add(G.pos)); G.item.rotation.set(hp.itemRot,o.yaw,0,'YXZ');
    if(G.type==='bag') G.item.rotation.set(0,o.yaw+0.2,0.08*Math.sin(t*1.3+G.seed));
    G.glow.position.copy(G.item.position).add(V(0,0,-0.05)); G.glow.scale.setScalar(0.8); }
  // tags appear while he looks back (body) — shown from 1.4 s in the test
  TAGS.forEach((T,i)=>{ const G=GH[T.g]; const a=SLD.sstep(1.2+i*0.12,1.5+i*0.12,t); T.s.visible=false; T.s.material.opacity=a;
    T.s.position.copy(G.item.position).add(V(0,G.type==='bag'?0.2:0.3,0.06)); T.s.scale.set(0.42,0.105,1); });
  ST.tick(t,0);
  const C=ST.cam; C.position.set(keys(CAMK.x,t),keys(CAMK.y,t),keys(CAMK.z,t)); C.fov=keys(CAMK.fov,t); C.updateProjectionMatrix(); C.lookAt(keys(CAMK.lx,t),keys(CAMK.ly,t),keys(CAMK.lz,t)); }
window.projAt=t=>{ setT(t); return GH.filter(G=>G.front).map(G=>{ const p=G.item.position.clone().project(ST.cam); return [G.type,(p.x*0.5+0.5)*W,(0.5-p.y*0.5)*H]; }); };
window.renderAt=(t,K=1)=>ST.renderAt(setT,t,K,{shutter:1/60});
ST.renderAt(setT,0.5,1); window.events={}; window.ready=true;   // warm-up: first render uploads canvas textures
