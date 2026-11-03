// Their Words Became His Wall (Slow Light Dark). V2 of "They Threw Words": a wall instead of stairs.
// Camera behind three slate men in the foreground. They hurl stone blocks, each carrying an insult, at the cream man in
// the lamp. He catches every one and sets it into a wall between them (3 x 4 blocks), word facing out: their words
// face them. The last block is the red one ("YOU'LL NEVER MAKE IT"), held by the third man since frame 0: it smashes
// into the wall and drops. He rests his hands on top of the wall; the men lower their heads and fade into the void.
//
// renderAt(t) is pure (no state between frames), so frames can render in parallel workers.
import * as THREE from 'three';
import * as SLD from './sld.js';
const {V,clamp,sstep,lerp,sm5,PAL,rng,rotY,yawOf,keys}=SLD;
const TL=await (await fetch('./timeline.json')).json();
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960, DUR=TL.duration;
await Promise.all([['SL','fonts/JetBrainsMono-SemiBold.ttf'],['SLB','fonts/JetBrainsMono-Bold.ttf']].map(async([n,u])=>{ const f=new FontFace(n,`url(${u})`); await f.load(); document.fonts.add(f); }));

// ---------------------------------------------------------------- layout (wall along x at z = 0, text faces +z / camera / the men)
const BW=0.50, BH=0.26, BD=0.30, G=9.8, NC=3;
const NB=TL.words.length;
const colOf=k=>k%NC, rowOf=k=>Math.floor(k/NC);
const slot=k=>V((colOf(k)-1)*BW*1.005+(rowOf(k)%2?0.03:-0.02),BH/2+rowOf(k)*BH*1.003,0);
const WALL_TOP=Math.ceil(NB/NC)*BH;
const Y0=yawOf(V(0,0,1));                          // facing +z (toward the men / camera)
const HZ=-0.50;                                    // he stands behind the wall
const hx=k=>k>=NB?0:(colOf(k)-1)*0.36;
const HP=[V(-1.42,0,0.25),V(-1.70,0,-0.30),V(-2.0,0,0.50)];
const RED=2;

// ---------------------------------------------------------------- stage
const S=SLD.createStage({W,H,lamp:V(-0.1,6.6,-0.95),lampTarget:V(-0.15,0,-0.2),cone:0.22,spot:64,fov:38});
const {scene,cam}=S;
const R=SLD.createRig(scene);
const hero=R.makeFig(PAL.CREAM,'hero',{rim:0.16,lift:0.07});
const haters=HP.map((p,i)=>R.makeFig(PAL.SLATE,'hater'+i,{rim:0.24,rimCol:0x9fb2d6,lift:0.035}));

// ---------------------------------------------------------------- text textures
function wordCanvas(word,{w=1024,h=256,col='#EDE6D6'}={}){
  const c=document.createElement('canvas'); c.width=w; c.height=h; const g=c.getContext('2d');
  let fs=Math.round(h*0.5); g.font=`600 ${fs}px SL`; while(g.measureText(word).width>w*0.9&&fs>10){ fs-=4; g.font=`600 ${fs}px SL`; }
  g.textAlign='center'; g.textBaseline='middle'; g.shadowColor='rgba(0,0,0,0.85)'; g.shadowBlur=h*0.12;
  g.fillStyle=col; g.fillText(word,w/2,h/2+fs*0.04); g.shadowBlur=0; g.fillText(word,w/2,h/2+fs*0.04);
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; t.anisotropy=8; return t; }
function faceCanvas(word){
  const c=document.createElement('canvas'); c.width=1024; c.height=Math.round(1024*BH/BW); const g=c.getContext('2d');
  g.fillStyle='#000'; g.fillRect(0,0,c.width,c.height);
  let fs=Math.round(c.height*0.34); g.font=`700 ${fs}px SLB`; while(g.measureText(word).width>c.width*0.84&&fs>10){ fs-=4; g.font=`700 ${fs}px SLB`; }
  g.textAlign='center'; g.textBaseline='middle'; g.fillStyle='#fff'; g.shadowColor='#fff'; g.shadowBlur=6; g.fillText(word,c.width/2,c.height/2+fs*0.05);
  const t=new THREE.CanvasTexture(c); t.anisotropy=8; return t; }

// ---------------------------------------------------------------- blocks
const stoneTex=SLD.noiseTex(256,13,120,80,60,0.2);
const blockGeo=new THREE.BoxGeometry(BW,BH,BD);
function makeBlock(word,i,red=false){
  const base=red?0x5c1c17:0x3c3a37;
  const mk=(em,key)=>SLD.rimify(new THREE.MeshStandardMaterial({color:base,roughness:0.86,metalness:0,map:stoneTex,emissive:red?PAL.RED:(em?0xf2dcae:0x000000),emissiveMap:em?faceCanvas(word):null,emissiveIntensity:0}),red?0xff8a70:0xfff1d8,0.06,key);
  const side=mk(false,'blk'+i), face=mk(true,'blkf'+i);
  const m=new THREE.Mesh(blockGeo,[side,side,side,side,face,side]); m.castShadow=true; m.receiveShadow=true; scene.add(m);
  const spr=new THREE.Sprite(new THREE.SpriteMaterial({map:wordCanvas(word,{col:red?'#F0563F':'#EDE6D6'}),transparent:true,depthWrite:false,fog:false}));
  spr.renderOrder=8; scene.add(spr);
  const glow=SLD.glowSprite(scene,red?PAL.RED:PAL.GOLD,0);
  return {m,face,side,spr,glow,word,red,sw:red?1.25:0.85,sh:red?0.25:0.21}; }
const blocks=TL.words.map((w,i)=>makeBlock(w,i));
const redB=makeBlock(TL.red,99,true);

// sparks: gold motes lifting off a face when its word burns in; dust at the red impact and where it lands
const NSP=36*NB+160, spPos=new Float32Array(NSP*3), spA=new Float32Array(NSP);
const spGeo=new THREE.BufferGeometry(); spGeo.setAttribute('position',new THREE.BufferAttribute(spPos,3)); spGeo.setAttribute('a',new THREE.BufferAttribute(spA,1));
const sparks=new THREE.Points(spGeo,new THREE.ShaderMaterial({uniforms:{uH:{value:H}},transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
  vertexShader:`attribute float a; varying float vA; uniform float uH; void main(){ vA=a; vec4 mv=modelViewMatrix*vec4(position,1.0); gl_Position=projectionMatrix*mv; gl_PointSize=clamp(0.016*uH/(-mv.z),1.0,18.0); }`,
  fragmentShader:`varying float vA; void main(){ float d=length(gl_PointCoord-0.5); gl_FragColor=vec4(vec3(1.0,0.78,0.45)*smoothstep(0.5,0.0,d)*vA,1.0); }`}));
sparks.frustumCulled=false; scene.add(sparks); S.NOREFL.push(sparks);
const SPR=(()=>{ const Rn=rng(9); return [...Array(NSP)].map(()=>[Rn(),Rn(),Rn(),Rn()]); })();

// ---------------------------------------------------------------- helpers
const fwdOf=y=>rotY(V(1,0,0),y);
const angLerp=(a,b,u)=>{ let d=((b-a+Math.PI)%(2*Math.PI)+2*Math.PI)%(2*Math.PI)-Math.PI; return a+d*u; };
const REL=k=>TL.catches[k]-TL.flight;
function ballistic(p0,p1,T,u){ const vy=(p1.y-p0.y)/T+0.5*G*T, s=u*T; const p=p0.clone().lerp(p1,u); p.y=p0.y+vy*s-0.5*G*s*s; return p; }
const shake=t=>{ const s=t-TL.redHit; return s<0?0:Math.exp(-s/0.13)*Math.sin(s*70); };

// ---------------------------------------------------------------- hero
const XK=(()=>{ const K=[[0,hx(0)]]; TL.catches.forEach((c,k)=>{ K.push([c+TL.place+0.12,hx(k)],[c+TL.place+0.42,hx(k+1)]); }); return K; })();
function heroRoot(t){ const x=keys(XK,t); let mv=0; TL.catches.forEach((c,k)=>{ const a=c+TL.place+0.12,b=c+TL.place+0.42; if(t>a&&t<b&&Math.abs(hx(k+1)-hx(k))>0.01) mv=(t-a)/(b-a); }); return {root:V(x,0,HZ),mv}; }
const catchYaw=k=>{ const s=V(hx(k),0,HZ); return angLerp(Y0,yawOf(HP[TL.throwers[k]].clone().sub(s).setY(0)),0.8); };
function heroYaw(t){ let y=Y0; TL.catches.forEach((c,k)=>{ const w=sstep(c-0.45,c-0.15,t)*(1-sstep(c+0.05,c+0.3,t)); if(w>0) y=angLerp(Y0,catchYaw(k),w); });
  const r=TL.redRelease; const w=sstep(r-0.3,r+0.1,t)*(1-sstep(TL.redHit,TL.redHit+0.5,t)); if(w>0) y=angLerp(Y0,yawOf(HP[RED].clone().sub(V(0,0,HZ)).setY(0)),0.5*w);
  return y; }
const heldPoint=(root,yaw)=>root.clone().addScaledVector(fwdOf(yaw),0.30).add(V(0,1.32,0));
const catchPoint=k=>heldPoint(V(hx(k),0,HZ),catchYaw(k));

// ---------------------------------------------------------------- men
const holdPt=(hp,yaw,kind)=>{ const f=fwdOf(yaw); const o={hold:[0.32,1.05],low:[0.30,0.86],wind:[-0.14,1.98],rel:[0.38,1.85]}[kind]; return hp.clone().addScaledVector(f,o[0]).add(V(0,o[1],0)); };
const haterYaw=(i,t)=>yawOf(heroRoot(t).root.clone().sub(HP[i]).setY(0));
function inHands(i,yaw,rel,low=false){
  const A=holdPt(HP[i],yaw,low?'low':'hold'), B=holdPt(HP[i],yaw,'wind'), C=holdPt(HP[i],yaw,'rel');
  if(rel<-0.55) return A; if(rel<-0.2) return A.clone().lerp(B,sm5(sstep(-0.55,-0.2,rel)));
  return B.clone().lerp(C,sstep(-0.2,0,rel)); }
const IMP=V(-BW*1.5-BW/2-0.03,0.82,0.05);
function blockState(k,t){
  const c=TL.catches[k], r=REL(k), th=TL.throwers[k];
  if(t<r-0.95) return null;
  const hy=haterYaw(th,Math.min(t,r));
  if(t<r) return {pos:inHands(th,hy,t-r),yaw:hy+Math.PI/2,flip:0,a:sstep(r-0.95,r-0.75,t)};
  if(t<c){ const u=(t-r)/TL.flight; return {pos:ballistic(holdPt(HP[th],hy,'rel'),catchPoint(k),TL.flight,u),yaw:angLerp(hy+Math.PI/2,catchYaw(k)+Math.PI/2,sm5(u)),flip:2*Math.PI*sm5(u),a:1}; }
  const pl=c+TL.place;
  if(t<pl){ const {root}=heroRoot(t), yw=heroYaw(t); const u=sm5(sstep(c+0.06,pl,t)); const p=heldPoint(root,yw).lerp(slot(k),u); p.y+=0.10*Math.sin(Math.PI*u);
    return {pos:p,yaw:angLerp(yw+Math.PI/2,0,u),flip:0,a:1}; }
  const p=slot(k); p.z+=0.012*shake(t)*(1-rowOf(k)*0.1); p.x+=0.004*shake(t+0.01);
  return {pos:p,yaw:0,flip:0,a:1,placed:t-pl}; }
function redState(t){
  const r=TL.redRelease, Hh=TL.redHit, L=TL.redLand, hy=haterYaw(RED,Math.min(t,r));
  if(t<r) return {pos:inHands(RED,hy,t-r,true),yaw:hy+Math.PI/2,flip:0,a:1};
  if(t<Hh){ const u=(t-r)/(Hh-r); return {pos:ballistic(holdPt(HP[RED],hy,'rel'),IMP,Hh-r,u),yaw:angLerp(hy+Math.PI/2,0.15,u),flip:2*Math.PI*sm5(u),a:1}; }
  if(t<L){ const s=t-Hh, T=L-Hh; const vy=(BH/2-IMP.y+0.5*G*T*T)/T; const p=IMP.clone().add(V(-1.05*s,vy*s-0.5*G*s*s,0.35*s)); return {pos:p,yaw:0.15+0.5*s,flip:-Math.PI*0.9*(s/T),a:1,hit:s}; }
  const s=t-L, T=L-Hh; const p=IMP.clone().add(V(-1.05*T,0,0.35*T)); p.y=BH/2+Math.max(0,0.05*Math.sin(Math.PI*clamp(s/0.18)));
  p.add(V(-0.2,0,0.08).multiplyScalar(sm5(clamp(s/0.45))));
  return {pos:p,yaw:0.15+0.5*T+0.25*sm5(clamp(s/0.45)),flip:-Math.PI*lerp(0.9,1.0,sm5(clamp(s/0.3))),a:1,landed:s,hit:t-Hh}; }
const grips=st=>{ const ax=rotY(V(1,0,0),st.yaw); return [st.pos.clone().addScaledVector(ax,BW/2-0.02),st.pos.clone().addScaledVector(ax,-BW/2+0.02)]; };

// ---------------------------------------------------------------- poses
const P_STAND=R.POSES.stand;
const P_PLACE={...R.POSES.crouch,p:1.0,tilt:0.35,aL:1.0,aR:0.75,kL:1.65,kR:1.3};
const POLES={pL:V(-0.3,-0.6,0.8),pR:V(-0.3,-0.6,-0.8)};
function heroPose(t){
  const {root,mv}=heroRoot(t), yaw=heroYaw(t);
  let P={...P_STAND,p:0.06+0.015*Math.sin(t*1.9)};
  let cr=0, absorb=0, hold=null, wHold=0, ready=null, wReady=0;
  for(let k=0;k<NB;k++){ const c=TL.catches[k], depth=[1,0.62,0.28,0.05][rowOf(k)];
    cr=Math.max(cr,depth*sstep(c+0.06,c+0.32,t)*(1-sstep(c+TL.place,c+TL.place+0.2,t)));
    absorb=Math.max(absorb,Math.exp(-Math.pow((t-c-0.05)/0.07,2)));
    if(t>=c-0.5&&t<c){ ready=grips({pos:catchPoint(k),yaw:catchYaw(k)+Math.PI/2}); wReady=sstep(c-0.5,c-0.1,t); }
    if(t>=c&&t<c+TL.place+0.25){ const st=blockState(k,Math.min(t,c+TL.place)); hold=grips(st); wHold=1-sstep(c+TL.place,c+TL.place+0.22,t); } }
  P=R.blend(P,P_PLACE,sm5(cr));
  P.dy-=0.05*absorb; P.p+=0.08*absorb;
  if(mv>0) P=R.gait(P,2*Math.PI*mv,Math.sin(Math.PI*mv)*0.6,0.25,0.5,0.06);
  // finale: ready for the red block, flinch when it hits the wall, then hands on top of the wall, looking down at it
  const r=TL.redRelease, Hh=TL.redHit;
  const wr=sstep(r-0.35,r+0.1,t)*(1-sstep(Hh-0.05,Hh+0.25,t)); if(wr>0){ ready=grips({pos:heldPoint(root,yaw),yaw:yaw+Math.PI/2}); wReady=0.75*wr; }
  const fl=Math.exp(-Math.pow((t-Hh-0.08)/0.12,2)); P.p-=0.14*fl; P.dy-=0.03*fl; P.tilt-=0.15*fl;
  const lk=sstep(TL.lookOver-0.2,TL.lookOver+0.5,t);
  P.p+=0.18*lk; P.tilt+=0.32*lk*(1-0.5*sstep(TL.pay0+0.6,TL.pay1+0.8,t));
  P.p+=Math.sin(t*2.1)*0.01;
  if(hold&&wHold>0){ Object.assign(P,{tL:hold[1],tR:hold[0],wL:wHold,wR:wHold},POLES); }
  else if(ready&&wReady>0){ Object.assign(P,{tL:ready[1],tR:ready[0],wL:wReady,wR:wReady},POLES); }
  else if(lk>0){ const top=WALL_TOP+0.035; Object.assign(P,{tL:V(root.x-0.26,top,-0.08),tR:V(root.x+0.26,top,-0.08),wL:lk,wR:lk},POLES); }
  return {P,root,yaw}; }
function haterPose(i,t){
  const yaw=haterYaw(i,t); let P={...P_STAND,p:0.08+0.012*Math.sin(t*1.7+i*2)};
  let hand=null, w=0;
  const mine=[]; TL.throwers.forEach((th,k)=>{ if(th===i) mine.push(REL(k)); });
  if(i===RED) mine.push(TL.redRelease);
  for(const r of mine){ const rel=t-r, isRed=(i===RED);
    if(rel>=(isRed?-99:-0.95)&&rel<0){ const st=isRed?redState(t):{pos:inHands(i,yaw,rel),yaw:yaw+Math.PI/2}; hand=grips(st); w=isRed?1:sstep(-0.95,-0.78,rel); }
    if(rel>=0&&rel<0.5){ const f=fwdOf(yaw), side=rotY(V(0,0,1),yaw); const tip=holdPt(HP[i],yaw,'rel').addScaledVector(f,0.15).add(V(0,-0.35*sstep(0,0.5,rel),0));
      hand=[tip.clone().addScaledVector(side,-0.22),tip.clone().addScaledVector(side,0.22)]; w=1-sstep(0.05,0.5,rel); }
    if(rel>-0.6&&rel<0.9){ P.p+=keys([[-0.55,0],[-0.2,-0.3],[0.0,0.36],[0.3,0.3],[0.85,0]],rel); P.aL+=0.24*sstep(-0.3,0.0,rel)*(1-sstep(0.4,0.85,rel)); P.kR+=0.2*sstep(-0.3,0,rel)*(1-sstep(0.4,0.85,rel)); P.tilt+=keys([[-0.55,0],[-0.2,-0.22],[0,0.12],[0.85,0]],rel); } }
  // the shout on the wind-up: head jut forward
  const sh=TL.throwers.map((th,k)=>th===i?Math.exp(-Math.pow((t-REL(k)+TL.shoutLead-0.1)/0.15,2)):0).reduce((a,b)=>Math.max(a,b),0);
  P.tilt+=0.12*sh;
  const L=TL.redLand; const dn=sstep(L+0.2,L+1.1,t); P.tilt+=0.4*dn; P.p+=(i===RED?0.24:0.13)*dn;
  if(hand&&w>0) Object.assign(P,{tR:hand[0],tL:hand[1],wL:w,wR:w,pL:V(-0.3,-0.5,0.9),pR:V(-0.3,-0.5,-0.9)});
  return {P,yaw}; }

// ---------------------------------------------------------------- blocks + words per frame
const qY=new THREE.Quaternion(), qX=new THREE.Quaternion();
function setBlock(B,st,t){
  if(!st){ B.m.visible=false; B.spr.visible=false; B.glow.material.opacity=0; return; }
  B.m.visible=st.a>0.02; B.m.position.copy(st.pos);
  qY.setFromAxisAngle(V(0,1,0),st.yaw); qX.setFromAxisAngle(V(1,0,0),st.flip); B.m.quaternion.copy(qY).multiply(qX);
  [B.side,B.face].forEach(m=>{ const tr=st.a<0.999; if(m.transparent!==tr){ m.transparent=tr; m.needsUpdate=true; } m.opacity=st.a; });
  const faceN=rotY(V(0,0,1),st.yaw), faceC=st.pos.clone().addScaledVector(faceN,BD/2+0.01);
  let sa=st.a, sp=st.pos.clone().add(V(0,0.27,0)), sc=1, em=0, gl=0;
  if(st.placed!==undefined){ const u=sstep(0,0.2,st.placed); sp.lerp(faceC,u); sc=lerp(1,0.6,u); sa=1-sstep(0.1,0.24,st.placed);
    em=1.6*Math.exp(-st.placed/0.35)*sstep(0.08,0.18,st.placed)+0.42*sstep(0.1,0.4,st.placed); gl=0.45*Math.exp(-Math.pow((st.placed-0.18)/0.14,2)); }
  if(B.red){ const r=TL.redRelease; sa=sstep(r-0.6,r-0.3,t); const fl=sstep(r-0.5,r,t); gl=0.14*fl; em=0.05; let se=0.05+0.25*fl;
    if(st.hit!==undefined){ gl=0.14*fl+0.8*Math.exp(-st.hit/0.12); sa*=1-sstep(0.05,0.8,st.hit); se=0.05+0.3*Math.exp(-st.hit/0.5); em=0.05+0.3*Math.exp(-st.hit/0.4); }
    B.side.emissiveIntensity=se; }
  B.spr.visible=sa>0.01; B.spr.material.opacity=sa; B.spr.position.copy(sp); B.spr.scale.set(B.sw*sc,B.sh*sc,1);
  B.face.emissiveIntensity=em;
  B.glow.position.copy(B.red?st.pos:faceC); B.glow.scale.setScalar(B.red?1.0:0.65); B.glow.material.opacity=gl; }
function setSparks(t){
  let n=0; const ax=V(1,0,0), zf=V(0,0,1);
  for(let k=0;k<NB;k++){ const s=t-TL.catches[k]-TL.place-0.1; const fc=slot(k).addScaledVector(zf,BD/2+0.02);
    for(let j=0;j<36;j++,n++){ const r=SPR[n]; const life=0.8+1.0*r[2], u=s/life; if(s<0||u>1){ spA[n]=0; continue; }
      const p=fc.clone().addScaledVector(ax,(r[0]-0.5)*BW*0.9).add(V(0,(r[1]-0.5)*BH*0.6+s*(0.12+0.25*r[3]),s*0.06*r[1]));
      spPos.set([p.x,p.y,p.z],n*3); spA[n]=(1-u)*(1-u)*sstep(0,0.05,s)*(0.4+0.6*r[3]); } }
  for(let j=0;j<80;j++,n++){ const r=SPR[n], s=t-TL.redHit; if(s<0||s>1.8){ spA[n]=0; continue; }   // stone dust off the wall face
    const a=r[0]*6.283, d=(0.25+0.7*r[1])*(1-Math.exp(-s*4))/4*1.8; const p=IMP.clone().add(V(-0.05-d*0.6*r[2],Math.sin(a)*d*0.7-0.15*s*s,Math.cos(a)*d));
    spPos.set([p.x,p.y,p.z],n*3); spA[n]=0.35*Math.exp(-s/0.5)*(0.3+0.7*r[3]); }
  for(let j=0;j<80;j++,n++){ const r=SPR[n], s=t-TL.redLand; if(s<0||s>2.2){ spA[n]=0; continue; }
    const st=redState(TL.redLand); const a=r[0]*6.283, d=(0.35+0.9*r[1])*(1-Math.exp(-s*3))/3*1.5;
    const p=st.pos.clone().add(V(Math.cos(a)*d,-BH/2+0.02+0.22*r[2]*(1-Math.exp(-s*2.5)),Math.sin(a)*d*0.7));
    spPos.set([p.x,p.y,p.z],n*3); spA[n]=0.2*Math.exp(-s/0.8)*(0.3+0.7*r[3]); }
  spGeo.attributes.position.needsUpdate=true; spGeo.attributes.a.needsUpdate=true; }

// ---------------------------------------------------------------- camera: behind the men, a slow push-in as the wall rises, a jolt on the red hit
const CAMK=[[0.0,[-0.66,1.62,9.2],[-0.66,1.42,0.0]],[11.4,[-0.63,1.62,8.8],[-0.63,1.42,0.0]],[DUR,[-0.6,1.62,8.45],[-0.6,1.42,0.0]]];
function camAt(t){ const P=[0,1,2].map(i=>keys(CAMK.map(k=>[k[0],k[1][i]]),t)), L=[0,1,2].map(i=>keys(CAMK.map(k=>[k[0],k[2][i]]),t));
  const j=shake(t); cam.position.set(P[0]+0.004*j,P[1]+0.012*j,P[2]); cam.lookAt(L[0],L[1]+0.006*shake(t+0.02),L[2]); }

// ---------------------------------------------------------------- frame
function setT(t){
  const h=heroPose(t); R.poseFig(hero,R.skel(h.P,h.root,h.yaw));
  const fade=1-sstep(TL.fade0,TL.fade1,t);
  haters.forEach((F,i)=>{ const p=haterPose(i,t); R.poseFig(F,R.skel(p.P,HP[i],p.yaw)); F.setAlpha(fade); });
  blocks.forEach((B,k)=>setBlock(B,blockState(k,t),t));
  setBlock(redB,redState(t),t);
  setSparks(t); camAt(t);
  S.tick(t,0.14*sstep(TL.pay0,TL.pay1,t)); }
window.renderAt=(t,K=3)=>S.renderAt(setT,t,K,{t0:0,t1:DUR});
window.metaAt=t=>{ let placed=0; for(let k=0;k<NB;k++) if(t>=TL.catches[k]+TL.place) placed++; return {t,placed}; };
window.events={...TL,release_times:TL.catches.map((c,k)=>REL(k))};
window.ready=true;
