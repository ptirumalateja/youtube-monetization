// Their Words Became His Wall (Slow Light Dark), V3: the reference's side-angled layout, read frame by frame
// (concepts/wall-reel-frame-read.md). Four slate men at the left, a long clean 16 x 6 wall in the middle (plain bricks,
// no words), the cream man at its right end. The men throw word-bricks AT HIS FACE; he catches each in front of his face
// and sets it into the last 6 gaps of the top row. Last comes the big red "YOU'LL NEVER MAKE IT": it is big enough to
// cover his face when he catches it. He holds it, then sets it on top of the wall's end as the capstone. The men fade.
//
// renderAt(t) is pure (no state between frames), so frames can render in parallel workers.
import * as THREE from 'three';
import * as SLD from './sld.js';
const {V,clamp,sstep,lerp,sm5,PAL,rng,rotY,yawOf,keys}=SLD;
const TL=await (await fetch('./timeline.json')).json();
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960, DUR=TL.duration;
await Promise.all([['SL','fonts/JetBrainsMono-SemiBold.ttf'],['SLB','fonts/JetBrainsMono-Bold.ttf']].map(async([n,u])=>{ const f=new FontFace(n,`url(${u})`); await f.load(); document.fonts.add(f); }));

// ---------------------------------------------------------------- layout: wall along x at z = 0, camera at front-right
const BW=0.30, BH=0.20, BD=0.22, G=16, NC=16, NR=6;
const NB=TL.words.length, NPRE=NC*NR-NB, X0=-2.25;
const END=X0+(NC-1)*BW+BW/2, START=X0-BW/2, TOP=NR*BH;
const offRow=r=>(NR-1-r)%2===1;                                   // running bond; the top row is a full row
const slotTop=c=>V(X0+c*BW,BH/2+(NR-1)*BH,0);
const slot=k=>slotTop(NC-NB+k);                                   // thrown brick k fills top-row column 10+k
const HZ=-0.30, FACE_H=1.66;
const hx=k=>Math.min(slot(Math.min(k,NB-1)).x+0.42,END+0.34);
const HX_END=END+0.34;
const HP=[V(-3.15,0,0.15),V(-3.5,0,-0.35),V(-3.85,0,0.3),V(-2.95,0,0.85)];
const RED=3;                                                      // the front man holds the red brick low from frame 0
const RW=0.46, RH=0.32, RD=0.28;
const CAP=V(END-RW/2+0.01,TOP+RH/2+0.003,0);

// ---------------------------------------------------------------- stage: clean studio light over the series lamp
const S=SLD.createStage({W,H,lamp:V(END+0.1,6.4,-0.5),lampTarget:V(END-0.2,0,-0.1),cone:0.2,spot:42,beam:0.06,fov:+(q.get('fov')||44),motes:900});
const {scene,cam}=S;
scene.background=new THREE.Color(0x23262e); S.renderer.toneMappingExposure=1.12;
S.floor.scale.set(3,3,1); S.refl.scale.set(3,3,1);
scene.fog=new THREE.FogExp2(0x23262e,0.045);
scene.add(new THREE.HemisphereLight(0x8d98b0,0x2a2622,0.4));
const key=new THREE.DirectionalLight(0xfff0dc,1.25); key.position.set(4.5,6.5,6.5); key.target.position.set(-0.5,0.6,0);
key.castShadow=true; key.shadow.mapSize.set(2048,2048); Object.assign(key.shadow.camera,{left:-6,right:6,top:5,bottom:-3,near:1,far:20}); key.shadow.bias=-0.0003; key.shadow.normalBias=0.02;
scene.add(key,key.target);
const rim=new THREE.DirectionalLight(0x9fb4e0,0.6); rim.position.set(-3,3.5,-5); scene.add(rim);
S.floor.material.color.set(0x36363c); S.floor.material.opacity=0.9;
const R=SLD.createRig(scene);
const hero=R.makeFig(PAL.CREAM,'hero',{rim:0.16,lift:0.07});
const haters=HP.map((p,i)=>R.makeFig(PAL.SLATE,'hater'+i,{rim:0.24,rimCol:0x9fb2d6,lift:0.035}));

// ---------------------------------------------------------------- the wall already standing (clean, plain bricks)
const stoneTex=SLD.noiseTex(256,13,128,46,60,0.12);
const brickMat=SLD.rimify(new THREE.MeshStandardMaterial({color:0xa4a6ae,roughness:0.82,metalness:0,map:stoneTex}),0xdfe6f5,0.05,'wall');
const brickGeo=new THREE.BoxGeometry(1,1,1);
const pieces=[];
for(let r=0;r<NR;r++){ const y=BH/2+r*BH;
  if(offRow(r)){ pieces.push([START+BW/4,y,BW/2]); for(let j=0;j<NC-1;j++) pieces.push([X0+BW/2+j*BW,y,BW]); pieces.push([END-BW/4,y,BW/2]); }
  else for(let c=0;c<NC;c++){ if(r===NR-1&&c>=NC-NB) continue; pieces.push([X0+c*BW,y,BW]); } }
const wallIM=new THREE.InstancedMesh(brickGeo,brickMat,pieces.length); wallIM.castShadow=true; wallIM.receiveShadow=true;
{ const m=new THREE.Matrix4(), Rn=rng(4), col=new THREE.Color();
  pieces.forEach(([x,y,w],i)=>{ m.makeScale(w-0.012,BH-0.012,BD); m.setPosition(x,y,0); wallIM.setMatrixAt(i,m); const v=0.93+0.12*Rn(); wallIM.setColorAt(i,col.setRGB(v,v,v*1.01)); }); }
scene.add(wallIM);
// mortar core behind the bricks: the joints read as thin dark lines
const core=new THREE.Mesh(new THREE.BoxGeometry(END-START-0.02,TOP-BH-0.01,BD-0.04),new THREE.MeshStandardMaterial({color:0x1a1a1d,roughness:1}));
core.position.set((START+END)/2,(TOP-BH)/2,0); scene.add(core);
const coreTop=new THREE.Mesh(new THREE.BoxGeometry((NC-NB)*BW-0.02,BH-0.01,BD-0.04),core.material); coreTop.position.set(START+(NC-NB)*BW/2,TOP-BH/2,0); scene.add(coreTop);

// ---------------------------------------------------------------- thrown bricks + floating words
function wordCanvas(word,col){
  const c=document.createElement('canvas'); c.width=1024; c.height=256; const g=c.getContext('2d');
  let fs=128; g.font=`700 ${fs}px SLB`; while(g.measureText(word).width>c.width*0.92&&fs>10){ fs-=4; g.font=`700 ${fs}px SLB`; }
  g.textAlign='center'; g.textBaseline='middle'; g.shadowColor='rgba(0,0,0,0.9)'; g.shadowBlur=24;
  g.fillStyle=col; g.fillText(word,512,132); g.shadowBlur=0; g.fillText(word,512,132);
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; t.anisotropy=8; return t; }
function makeBrick(word,red=false){
  const mat=SLD.rimify(new THREE.MeshStandardMaterial({color:red?0xc0392b:0xa4a6ae,roughness:red?0.6:0.8,metalness:0,map:stoneTex,emissive:red?PAL.RED:PAL.GOLD,emissiveIntensity:0}),red?0xff9a80:0xdfe6f5,0.06,red?'red':'b'+word);
  const m=new THREE.Mesh(new THREE.BoxGeometry(red?RW:BW-0.012,red?RH:BH-0.012,red?RD:BD),mat); m.castShadow=true; m.receiveShadow=true; scene.add(m);
  const spr=new THREE.Sprite(new THREE.SpriteMaterial({map:wordCanvas(word,red?'#FF5A44':'#F1E7D2'),transparent:true,depthWrite:false,fog:false}));
  spr.renderOrder=8; scene.add(spr);
  const glow=SLD.glowSprite(scene,red?PAL.RED:PAL.GOLD,0);
  return {m,mat,spr,glow,red,sw:red?1.5:0.95,sh:red?0.375:0.24}; }
const bricks=TL.words.map(w=>makeBrick(w));
const redB=makeBrick(TL.red,true);

// sparks: gold motes off each brick as it is set, a red burst at the capstone
const NSP=30*NB+90, spPos=new Float32Array(NSP*3), spA=new Float32Array(NSP);
const spGeo=new THREE.BufferGeometry(); spGeo.setAttribute('position',new THREE.BufferAttribute(spPos,3)); spGeo.setAttribute('a',new THREE.BufferAttribute(spA,1));
const sparks=new THREE.Points(spGeo,new THREE.ShaderMaterial({uniforms:{uH:{value:H}},transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
  vertexShader:`attribute float a; varying float vA; uniform float uH; void main(){ vA=a; vec4 mv=modelViewMatrix*vec4(position,1.0); gl_Position=projectionMatrix*mv; gl_PointSize=clamp(0.02*uH/(-mv.z),1.0,18.0); }`,
  fragmentShader:`varying float vA; void main(){ float d=length(gl_PointCoord-0.5); gl_FragColor=vec4(vec3(1.0,0.78,0.45)*smoothstep(0.5,0.0,d)*vA,1.0); }`}));
sparks.frustumCulled=false; scene.add(sparks); S.NOREFL.push(sparks);
const SPR=(()=>{ const Rn=rng(9); return [...Array(NSP)].map(()=>[Rn(),Rn(),Rn(),Rn()]); })();

// ---------------------------------------------------------------- helpers
const fwdOf=y=>rotY(V(1,0,0),y);
const angLerp=(a,b,u)=>{ let d=((b-a+Math.PI)%(2*Math.PI)+2*Math.PI)%(2*Math.PI)-Math.PI; return a+d*u; };
const REL=k=>TL.catches[k]-TL.flight;
function ballistic(p0,p1,T,u){ const vy=(p1.y-p0.y)/T+0.5*G*T, s=u*T; const p=p0.clone().lerp(p1,u); p.y=p0.y+vy*s-0.5*G*s*s; return p; }
const jolt=(t,t0,d=0.13)=>{ const s=t-t0; return s<0?0:Math.exp(-s/d)*Math.sin(s*60); };
const PLACED=k=>TL.catches[k]+TL.place;

// ---------------------------------------------------------------- hero
const XK=(()=>{ const K=[[0,hx(0)]]; TL.catches.forEach((c,k)=>{ const b=k<NB-1?hx(k+1):HX_END; K.push([PLACED(k)+0.05,hx(k)],[PLACED(k)+0.32,b]); }); return K; })();
function heroRoot(t){ let x=keys(XK,t), mv=0; TL.catches.forEach((c,k)=>{ const a=PLACED(k)+0.05,b=PLACED(k)+0.32; if(t>a&&t<b) mv=(t-a)/(b-a); });
  const kb=TL.redCatch; x+=0.14*sstep(kb,kb+0.12,t)*(1-sstep(kb+0.25,TL.redHold,t));      // knocked back by the red brick
  return {root:V(x,0,HZ),mv}; }
const Y0=yawOf(V(-1,0,0.25));
const faceYaw=(root,i)=>yawOf(HP[i].clone().sub(root).setY(0));
const facePt=(root,yaw,d=0.26)=>root.clone().addScaledVector(fwdOf(yaw),d).add(V(0,FACE_H,0));
function heroYaw(t){ const {root}=heroRoot(t); let y=Y0;
  TL.catches.forEach((c,k)=>{ const wc=sstep(c-0.45,c-0.15,t)*(1-sstep(c+0.02,c+0.14,t)); if(wc>0) y=angLerp(y,faceYaw(V(hx(k),0,HZ),TL.throwers[k]),wc);
    const wp=sstep(c+0.04,c+0.2,t)*(1-sstep(PLACED(k)+0.02,PLACED(k)+0.25,t)); if(wp>0) y=angLerp(y,yawOf(slot(k).sub(root).setY(0)),wp); });
  const r=TL.redRelease; const wr=sstep(r-0.3,r+0.05,t)*(1-sstep(TL.redHold,TL.redHold+0.25,t)); if(wr>0) y=angLerp(y,faceYaw(V(HX_END,0,HZ),RED),wr);
  const wcap=sstep(TL.redHold,TL.redHold+0.3,t); if(wcap>0) y=angLerp(y,yawOf(CAP.clone().sub(root).setY(0)),wcap*(1-0.6*sstep(TL.redPlace+0.3,TL.redPlace+1.2,t)));
  return y; }
const catchPt=k=>{ const r=V(hx(k),0,HZ); return facePt(r,faceYaw(r,TL.throwers[k])); };
const redCatchPt=()=>{ const r=V(HX_END,0,HZ); return facePt(r,faceYaw(r,RED),0.24); };

// ---------------------------------------------------------------- men
const holdPt=(hp,yaw,kind)=>{ const f=fwdOf(yaw); const o={hold:[0.32,1.05],low:[0.34,0.82],wind:[-0.14,1.98],rel:[0.38,1.88]}[kind]; return hp.clone().addScaledVector(f,o[0]).add(V(0,o[1],0)); };
const haterYaw=(i,t)=>yawOf(heroRoot(t).root.clone().sub(HP[i]).setY(0));
function inHands(i,yaw,rel,low=false){
  const A=holdPt(HP[i],yaw,low?'low':'hold'), B=holdPt(HP[i],yaw,'wind'), C=holdPt(HP[i],yaw,'rel');
  if(rel<-0.5) return A; if(rel<-0.18) return A.clone().lerp(B,sm5(sstep(-0.5,-0.18,rel)));
  return B.clone().lerp(C,sstep(-0.18,0,rel)); }
function brickState(k,t){
  const c=TL.catches[k], r=REL(k), th=TL.throwers[k];
  if(t<r-0.9) return null;
  const hy=haterYaw(th,Math.min(t,r));
  if(t<r) return {pos:inHands(th,hy,t-r),yaw:hy+Math.PI/2,flip:0,a:sstep(r-0.9,r-0.7,t)};
  if(t<c){ const u=(t-r)/TL.flight; const cy=faceYaw(V(hx(k),0,HZ),th);
    return {pos:ballistic(holdPt(HP[th],hy,'rel'),catchPt(k),TL.flight,u),yaw:angLerp(hy+Math.PI/2,cy+Math.PI/2,sm5(u)),flip:2*Math.PI*sm5(u),a:1}; }
  const pl=PLACED(k);
  if(t<pl){ const {root}=heroRoot(t), yw=heroYaw(t); const hold=facePt(root,yw,0.3).add(V(0,-0.12,0)); const u=sm5(sstep(c+0.08,pl,t));
    const p=hold.lerp(slot(k),u); p.y+=0.08*Math.sin(Math.PI*u); return {pos:p,yaw:angLerp(yw+Math.PI/2,0,u),flip:0,a:1}; }
  return {pos:slot(k),yaw:0,flip:0,a:1,placed:t-pl}; }
function redState(t){
  const r=TL.redRelease, C=TL.redCatch, Hd=TL.redHold, P=TL.redPlace, hy=haterYaw(RED,Math.min(t,r));
  if(t<r) return {pos:inHands(RED,hy,t-r,t<r-0.5),yaw:hy+Math.PI/2,flip:0};
  if(t<C){ const u=(t-r)/(C-r); const cy=faceYaw(V(HX_END,0,HZ),RED);
    return {pos:ballistic(holdPt(HP[RED],hy,'rel'),redCatchPt(),C-r,u),yaw:angLerp(hy+Math.PI/2,cy+Math.PI/2,sm5(u)),flip:2*Math.PI*sm5(u)}; }
  const {root}=heroRoot(t), yw=heroYaw(t);
  if(t<Hd){ const p=facePt(root,yw,0.24); p.y-=0.03*Math.exp(-Math.pow((t-C-0.06)/0.06,2)); return {pos:p,yaw:yw+Math.PI/2,flip:0,caught:t-C}; }
  if(t<P){ const u=sm5(sstep(Hd,P,t)); const p=facePt(root,yw,0.24).lerp(CAP,u); p.y+=0.14*Math.sin(Math.PI*u); return {pos:p,yaw:angLerp(yw+Math.PI/2,0,u),flip:0,caught:t-C}; }
  return {pos:CAP.clone(),yaw:0,flip:0,caught:t-C,placed:t-P}; }
const grips=(st,half)=>{ const ax=rotY(V(1,0,0),st.yaw); return [st.pos.clone().addScaledVector(ax,half),st.pos.clone().addScaledVector(ax,-half)]; };

// ---------------------------------------------------------------- poses
const P_STAND=R.POSES.stand;
const POLES={pL:V(-0.3,-0.6,0.8),pR:V(-0.3,-0.6,-0.8)};
function heroPose(t){
  const {root,mv}=heroRoot(t), yaw=heroYaw(t);
  let P={...P_STAND,p:0.06+0.015*Math.sin(t*1.9)};
  let hold=null, wHold=0, ready=null, wReady=0;
  for(let k=0;k<NB;k++){ const c=TL.catches[k], pl=PLACED(k);
    const ab=Math.exp(-Math.pow((t-c-0.04)/0.07,2)); P.dy-=0.035*ab; P.p-=0.05*ab;
    P.p+=0.22*sstep(c+0.1,pl,t)*(1-sstep(pl,pl+0.2,t));                               // lean to set it on the wall
    if(t>=c-0.5&&t<c){ ready=grips({pos:catchPt(k),yaw:faceYaw(V(hx(k),0,HZ),TL.throwers[k])+Math.PI/2},BW/2-0.03); wReady=sstep(c-0.5,c-0.12,t); }
    if(t>=c&&t<pl+0.22){ hold=grips(brickState(k,Math.min(t,pl)),BW/2-0.03); wHold=1-sstep(pl,pl+0.2,t); } }
  if(mv>0) P=R.gait(P,2*Math.PI*mv,Math.sin(Math.PI*mv)*0.6,0.25,0.5,0.06);
  // the red brick: ready, caught over his face (knocked back), held, set on the wall's end; then he stands tall
  const r=TL.redRelease, C=TL.redCatch, Pl=TL.redPlace;
  if(t>=r-0.4&&t<C){ ready=grips({pos:redCatchPt(),yaw:faceYaw(V(HX_END,0,HZ),RED)+Math.PI/2},RW/2-0.03); wReady=sstep(r-0.4,r+0.1,t); }
  if(t>=C&&t<Pl+0.3){ hold=grips(redState(Math.min(t,Pl)),RW/2-0.03); wHold=1-sstep(Pl,Pl+0.28,t); }
  const kb=Math.exp(-Math.pow((t-C-0.09)/0.12,2)); P.p-=0.24*kb; P.tilt-=0.2*kb; P.dy-=0.05*kb; P.kL+=0.25*kb; P.kR+=0.25*kb;
  P.p+=0.2*sstep(TL.redHold,Pl,t)*(1-sstep(Pl,Pl+0.35,t));
  const tall=sstep(Pl+0.3,Pl+1.0,t); P.tilt-=0.12*tall; P.p-=0.04*tall;
  P.p+=Math.sin(t*2.1)*0.01;
  if(hold&&wHold>0) Object.assign(P,{tL:hold[1],tR:hold[0],wL:wHold,wR:wHold},POLES);
  else if(ready&&wReady>0) Object.assign(P,{tL:ready[1],tR:ready[0],wL:wReady,wR:wReady},POLES);
  return {P,root,yaw}; }
function haterPose(i,t){
  const yaw=haterYaw(i,t); let P={...P_STAND,p:0.08+0.012*Math.sin(t*1.7+i*2)};
  let hand=null, w=0;
  const mine=[]; TL.throwers.forEach((th,k)=>{ if(th===i) mine.push(REL(k)); });
  if(i===RED) mine.push(TL.redRelease);
  for(const r of mine){ const rel=t-r, isRed=(i===RED);
    if(rel>=(isRed?-99:-0.9)&&rel<0){ const st=isRed?redState(t):{pos:inHands(i,yaw,rel),yaw:yaw+Math.PI/2}; hand=grips(st,(isRed?RW:BW)/2-0.03); w=isRed?1:sstep(-0.9,-0.72,rel); }
    if(rel>=0&&rel<0.5){ const f=fwdOf(yaw), side=rotY(V(0,0,1),yaw); const tip=holdPt(HP[i],yaw,'rel').addScaledVector(f,0.15).add(V(0,-0.35*sstep(0,0.5,rel),0));
      hand=[tip.clone().addScaledVector(side,-0.2),tip.clone().addScaledVector(side,0.2)]; w=1-sstep(0.05,0.5,rel); }
    if(rel>-0.6&&rel<0.9){ P.p+=keys([[-0.5,0],[-0.18,-0.3],[0.0,0.38],[0.3,0.3],[0.85,0]],rel); P.aL+=0.24*sstep(-0.3,0.0,rel)*(1-sstep(0.4,0.85,rel)); P.kR+=0.2*sstep(-0.3,0,rel)*(1-sstep(0.4,0.85,rel)); P.tilt+=keys([[-0.5,0],[-0.18,-0.2],[0,0.12],[0.85,0]],rel); } }
  const dn=sstep(TL.redPlace+0.1,TL.redPlace+0.9,t); P.tilt+=0.4*dn; P.p+=(i===RED?0.22:0.13)*dn;
  if(hand&&w>0) Object.assign(P,{tR:hand[0],tL:hand[1],wL:w,wR:w,pL:V(-0.3,-0.5,0.9),pR:V(-0.3,-0.5,-0.9)});
  return {P,yaw}; }

// ---------------------------------------------------------------- bricks per frame
const qY=new THREE.Quaternion(), qX=new THREE.Quaternion();
function setBrick(B,st,t,k){
  if(!st){ B.m.visible=false; B.spr.visible=false; B.glow.material.opacity=0; return; }
  B.m.visible=(st.a??1)>0.02; B.m.position.copy(st.pos);
  qY.setFromAxisAngle(V(0,1,0),st.yaw); qX.setFromAxisAngle(V(1,0,0),st.flip); B.m.quaternion.copy(qY).multiply(qX);
  const tr=(st.a??1)<0.999; if(B.mat.transparent!==tr){ B.mat.transparent=tr; B.mat.needsUpdate=true; } B.mat.opacity=st.a??1;
  let sa, em=0, gl=0;
  if(!B.red){ const c=TL.catches[k]; sa=(st.a??1)*(1-sstep(c+0.05,c+0.3,t));
    if(st.placed!==undefined){ em=0.9*Math.exp(-st.placed/0.3)*sstep(0,0.06,st.placed); gl=0.35*Math.exp(-Math.pow((st.placed-0.08)/0.14,2)); } }
  else { const r=TL.redRelease, C=TL.redCatch; sa=sstep(r-0.6,r-0.3,t)*(1-sstep(C+0.25,C+0.6,t));
    em=0.12+0.25*sstep(r-0.5,r,t); gl=0.12*sstep(r-0.5,r,t);
    if(st.caught!==undefined) gl+=0.5*Math.exp(-st.caught/0.12);
    if(st.placed!==undefined){ em=0.37+0.9*Math.exp(-st.placed/0.35)+0.15*sstep(TL.pay0,TL.pay1,t); gl=0.12+0.7*Math.exp(-st.placed/0.25); } }
  B.spr.visible=sa>0.01; B.spr.material.opacity=sa; B.spr.position.copy(st.pos).add(V(0,B.red?0.36:0.27,0)); B.spr.scale.set(B.sw,B.sh,1);
  B.mat.emissiveIntensity=em;
  B.glow.position.copy(st.pos).add(V(0,0,0.12)); B.glow.scale.setScalar(B.red?1.1:0.6); B.glow.material.opacity=gl; }
function setSparks(t){
  let n=0;
  for(let k=0;k<NB;k++){ const s=t-PLACED(k); const fc=slot(k).add(V(0,BH/2,0));
    for(let j=0;j<30;j++,n++){ const r=SPR[n]; const life=0.6+0.8*r[2], u=s/life; if(s<0||u>1){ spA[n]=0; continue; }
      const p=fc.clone().add(V((r[0]-0.5)*BW,s*(0.15+0.3*r[3]),(r[1]-0.5)*BD+s*0.1));
      spPos.set([p.x,p.y,p.z],n*3); spA[n]=(1-u)*(1-u)*(0.4+0.6*r[3]); } }
  for(let j=0;j<90;j++,n++){ const r=SPR[n], s=t-TL.redPlace; if(s<0||s>2.0){ spA[n]=0; continue; }
    const a=r[0]*6.283, d=(0.2+0.6*r[1])*(1-Math.exp(-s*3));
    const p=CAP.clone().add(V(Math.cos(a)*d*0.8,RH/2+s*(0.2+0.4*r[2]),Math.sin(a)*d*0.5));
    spPos.set([p.x,p.y,p.z],n*3); spA[n]=0.6*Math.exp(-s/0.6)*(0.3+0.7*r[3]); }
  spGeo.attributes.position.needsUpdate=true; spGeo.attributes.a.needsUpdate=true; }

// ---------------------------------------------------------------- camera: side view from the front-right, slightly high (as the reference)
const CB=V(9.7,3.4,5.5), CL=V(0.3,1.0,0.0), CD=CB.clone().sub(CL);
const CAMK=[[0.0,0.93],[1.1,1.0],[8.4,1.0],[DUR,0.93]];
function camAt(t){ const d=keys(CAMK,t); const pc=CL.clone().addScaledVector(CD,d), lk=CL.clone().add(V(0.2*(1-d)/0.07,0,0)); const P=[pc.x,pc.y,pc.z], L=[lk.x,lk.y,lk.z];
  if(q.get('cam')){ const c=q.get('cam').split(',').map(Number); P[0]=c[0];P[1]=c[1];P[2]=c[2];L[0]=c[3];L[1]=c[4];L[2]=c[5]; }
  const j=jolt(t,TL.redCatch)+0.6*jolt(t,TL.redPlace); cam.position.set(P[0]+0.005*j,P[1]+0.014*j,P[2]); cam.lookAt(L[0],L[1],L[2]); }

// ---------------------------------------------------------------- frame
function setT(t){
  const h=heroPose(t); R.poseFig(hero,R.skel(h.P,h.root,h.yaw));
  const fade=1-sstep(TL.fade0,TL.fade1,t);
  haters.forEach((F,i)=>{ const p=haterPose(i,t); R.poseFig(F,R.skel(p.P,HP[i],p.yaw)); F.setAlpha(fade); });
  bricks.forEach((B,k)=>setBrick(B,brickState(k,t),t,k));
  setBrick(redB,redState(t),t,-1);
  setSparks(t); camAt(t);
  S.tick(t,0.18*sstep(TL.pay0,TL.pay1,t)); }
window.renderAt=(t,K=3)=>S.renderAt(setT,t,K,{t0:0,t1:DUR});
window.metaAt=t=>{ let placed=0; for(let k=0;k<NB;k++) if(t>=PLACED(k)) placed++; return {t,placed}; };
window.events={...TL,release_times:TL.catches.map((c,k)=>REL(k))};
window.ready=true;
