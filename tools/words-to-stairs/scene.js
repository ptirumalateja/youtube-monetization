// They Threw Words. He Built Stairs. (Slow Light Dark)
// Three slate men on the left throw stone blocks, each carrying an insult. The cream man catches every one, sets it down
// as the next step of a stair and climbs onto it, up into the gold lamp. When a block is set, its word burns into the
// stone face. The last block is the red one ("YOU'LL NEVER MAKE IT"), held by the third man since frame 0: it falls
// short and hits the floor. The men lower their arms and fade into the void; he stands on every word they threw.
//
// renderAt(t) is pure (no state between frames), so frames can render in parallel workers.
import * as THREE from 'three';
import * as SLD from './sld.js';
const {V,clamp,sstep,lerp,sm5,PAL,rng,rotY,yawOf,keys}=SLD;
const TL=await (await fetch('./timeline.json')).json();
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960, DUR=TL.duration;
await Promise.all([['SL','fonts/JetBrainsMono-SemiBold.ttf'],['SLB','fonts/JetBrainsMono-Bold.ttf']].map(async([n,u])=>{ const f=new FontFace(n,`url(${u})`); await f.load(); document.fonts.add(f); }));

// ---------------------------------------------------------------- layout
const D=V(0.5,0,-0.866).normalize();           // stair direction: right and away from camera
const DYAW=yawOf(D);
const BW=0.56, BH=0.18, BD=0.40, RUN=0.20, RISE=0.18, G=9.8;
const B0=V(0.30,0,0.62);
const NB=TL.words.length;
const slot=k=>B0.clone().addScaledVector(D,k*RUN).add(V(0,BH/2+k*RISE,0));
const stand=k=>B0.clone().addScaledVector(D,k<0?-RUN-0.1:(k>=NB-1?k*RUN:k*RUN-0.1)).add(V(0,(k+1)*RISE,0));
const HP=[V(-0.70,0,0.30),V(-1.00,0,-0.40),V(-1.22,0,0.62)];
const RED=2;

// ---------------------------------------------------------------- stage
const S=SLD.createStage({W,H,lamp:V(0.45,6.8,-0.5),lampTarget:V(0.05,0,0.1),cone:0.23,spot:62,fov:38});
const {scene,cam}=S;
const R=SLD.createRig(scene);
const hero=R.makeFig(PAL.CREAM,'hero',{rim:0.16,lift:0.07});
const haters=HP.map((p,i)=>R.makeFig(PAL.SLATE,'hater'+i,{rim:0.22,rimCol:0x9fb2d6,lift:0.03}));

// ---------------------------------------------------------------- text textures
function wordCanvas(word,{w=1024,h=256,col='#EDE6D6',halo=true,size=0}={}){
  const c=document.createElement('canvas'); c.width=w; c.height=h; const g=c.getContext('2d');
  let fs=size||Math.round(h*0.5); g.font=`600 ${fs}px SL`;
  while(g.measureText(word).width>w*0.9&&fs>10){ fs-=4; g.font=`600 ${fs}px SL`; }
  g.textAlign='center'; g.textBaseline='middle';
  if(halo){ g.shadowColor='rgba(0,0,0,0.85)'; g.shadowBlur=h*0.12; }
  g.fillStyle=col; g.fillText(word,w/2,h/2+fs*0.04); g.shadowBlur=0; g.fillText(word,w/2,h/2+fs*0.04);
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; t.anisotropy=8; return t; }
function faceCanvas(word){   // emissive map for the block's front face: white letters on black
  const c=document.createElement('canvas'); c.width=1024; c.height=Math.round(1024*BH/BW); const g=c.getContext('2d');
  g.fillStyle='#000'; g.fillRect(0,0,c.width,c.height);
  let fs=Math.round(c.height*0.5); g.font=`700 ${fs}px SLB`; while(g.measureText(word).width>c.width*0.86&&fs>10){ fs-=4; g.font=`700 ${fs}px SLB`; }
  g.textAlign='center'; g.textBaseline='middle'; g.fillStyle='#fff'; g.shadowColor='#fff'; g.shadowBlur=6; g.fillText(word,c.width/2,c.height/2+fs*0.05);
  const t=new THREE.CanvasTexture(c); t.anisotropy=8; return t; }

// ---------------------------------------------------------------- blocks
const stoneTex=SLD.noiseTex(256,13,120,80,60,0.2);
const blockGeo=new THREE.BoxGeometry(BW,BH,BD);
function makeBlock(word,i,red=false){
  const base=red?0x5c1c17:0x3c3a37;
  const side=SLD.rimify(new THREE.MeshStandardMaterial({color:base,roughness:0.86,metalness:0,map:stoneTex,emissive:red?PAL.RED:0x000000,emissiveIntensity:0}),red?0xff8a70:0xfff1d8,0.06,'blk'+i);
  const faceTex=faceCanvas(word);
  const face=SLD.rimify(new THREE.MeshStandardMaterial({color:base,roughness:0.86,metalness:0,map:stoneTex,emissive:red?PAL.RED:0xf2dcae,emissiveMap:faceTex,emissiveIntensity:0}),red?0xff8a70:0xfff1d8,0.06,'blkf'+i);
  const back=SLD.rimify(new THREE.MeshStandardMaterial({color:base,roughness:0.86,metalness:0,map:stoneTex,emissive:red?PAL.RED:0xf2dcae,emissiveMap:faceTex,emissiveIntensity:0}),red?0xff8a70:0xfff1d8,0.06,'blkb'+i);
  const m=new THREE.Mesh(blockGeo,[side,side,side,side,face,back]); m.castShadow=true; m.receiveShadow=true; scene.add(m);
  const spr=new THREE.Sprite(new THREE.SpriteMaterial({map:wordCanvas(word,{col:red?'#F0563F':'#EDE6D6'}),transparent:true,depthWrite:false,fog:false}));
  spr.scale.set(red?1.3:0.9,red?0.26:0.225,1); spr.renderOrder=8; scene.add(spr);
  const glow=SLD.glowSprite(scene,red?PAL.RED:PAL.GOLD,0);
  return {m,face,back,spr,glow,word,red}; }
const blocks=TL.words.map((w,i)=>makeBlock(w,i));
const redB=makeBlock(TL.red,99,true);

// sparks: small gold motes that lift off a face when its word burns in, and dust when the red block hits the floor
const NSP=40*NB+90, spPos=new Float32Array(NSP*3), spA=new Float32Array(NSP);
const spGeo=new THREE.BufferGeometry(); spGeo.setAttribute('position',new THREE.BufferAttribute(spPos,3)); spGeo.setAttribute('a',new THREE.BufferAttribute(spA,1));
const spU={uH:{value:H}};
const sparks=new THREE.Points(spGeo,new THREE.ShaderMaterial({uniforms:spU,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
  vertexShader:`attribute float a; varying float vA; uniform float uH; void main(){ vA=a; vec4 mv=modelViewMatrix*vec4(position,1.0); gl_Position=projectionMatrix*mv; gl_PointSize=clamp(0.016*uH/(-mv.z),1.0,18.0); }`,
  fragmentShader:`varying float vA; void main(){ float d=length(gl_PointCoord-0.5); gl_FragColor=vec4(vec3(1.0,0.78,0.45)*smoothstep(0.5,0.0,d)*vA,1.0); }`}));
sparks.frustumCulled=false; scene.add(sparks); S.NOREFL.push(sparks);
const SPR=(()=>{ const Rn=rng(9); return [...Array(NSP)].map(()=>[Rn(),Rn(),Rn(),Rn()]); })();

// ---------------------------------------------------------------- helpers
const fwdOf=y=>rotY(V(1,0,0),y);
const angLerp=(a,b,u)=>{ let d=((b-a+Math.PI)%(2*Math.PI)+2*Math.PI)%(2*Math.PI)-Math.PI; return a+d*u; };
const REL=k=>TL.catches[k]-TL.flight;

// ---------------------------------------------------------------- hero timeline
function heroRoot(t){
  let k=0; while(k<NB&&TL.catches[k]+0.95<=t) k++;      // steps completed
  if(k<NB){ const c=TL.catches[k], u=sstep(c+0.55,c+0.95,t); if(u>0){ const a=stand(k-1), b=stand(k); const p=a.clone().lerp(b,sm5(u)); p.y=lerp(a.y,b.y,sm5(clamp(u*1.35)))+0.06*Math.sin(Math.PI*u); return {root:p,stepU:u}; } }
  return {root:stand(k-1),stepU:0}; }
const catchYaw=k=>{ const s=stand(k-1); return yawOf(HP[TL.throwers[k]].clone().sub(s).setY(0)); };
const RYAW=yawOf(HP[RED].clone().sub(stand(NB-1)).setY(0));
function heroYaw(t){
  const C=TL.catches; if(t<C[0]+0.1) return catchYaw(0);
  for(let k=0;k<NB;k++){ const c=C[k], nx=k<NB-1?catchYaw(k+1):RYAW;
    if(t<c+0.1) return catchYaw(k);
    if(t<c+0.42) return angLerp(catchYaw(k),DYAW,sstep(c+0.1,c+0.42,t));
    if(t<c+0.85) return DYAW;
    if(t<c+1.05||k===NB-1) return angLerp(DYAW,nx,sstep(c+0.85,c+1.05,t));
    if(k<NB-1&&t<C[k+1]+0.1) return nx; }
  return RYAW; }
const heldPoint=(root,yaw)=>root.clone().addScaledVector(fwdOf(yaw),0.40).add(V(0,1.12,0));
const catchPoint=k=>heldPoint(stand(k-1),catchYaw(k));

// ---------------------------------------------------------------- hater timeline
const hold=(hp,yaw,kind)=>{ const f=fwdOf(yaw); const o={hold:[0.32,1.05],low:[0.30,0.84],wind:[-0.12,1.95],rel:[0.36,1.8]}[kind]; return hp.clone().addScaledVector(f,o[0]).add(V(0,o[1],0)); };
function haterYaw(i,t){ return yawOf(heroRoot(t).root.clone().sub(HP[i]).setY(0)); }
// position of a block in a hater's hands, rel = t - release time
function inHands(i,yaw,rel,low=false){
  const A=hold(HP[i],yaw,low?'low':'hold'), B=hold(HP[i],yaw,'wind'), C=hold(HP[i],yaw,'rel');
  if(rel<-0.55) return A; if(rel<-0.2) return A.clone().lerp(B,sm5(sstep(-0.55,-0.2,rel)));
  return B.clone().lerp(C,sstep(-0.2,0,rel)); }
function ballistic(p0,p1,T,u){ const vy=(p1.y-p0.y)/T+0.5*G*T, s=u*T; const p=p0.clone().lerp(p1,u); p.y=p0.y+vy*s-0.5*G*s*s; return p; }
const RED_LAND=V(-0.12,BH/2,0.78);

// block state: {pos, yaw, flip, vis, held:{by,i}}
function blockState(k,t){
  const c=TL.catches[k], r=REL(k), th=TL.throwers[k];
  if(t<r-1.0) return null;
  const hy=haterYaw(th,Math.min(t,r));
  if(t<r) return {pos:inHands(th,hy,t-r),yaw:hy-Math.PI/2,flip:0,a:sstep(r-1.0,r-0.75,t),hand:['h',th]};
  if(t<c){ const u=(t-r)/TL.flight; return {pos:ballistic(hold(HP[th],hy,'rel'),catchPoint(k),TL.flight,u),yaw:angLerp(hy-Math.PI/2,catchYaw(k)-Math.PI/2,sm5(u)),flip:2*Math.PI*sm5(u),a:1}; }
  const pl=c+TL.place;
  if(t<pl){ const {root}=heroRoot(t), yw=heroYaw(t); const u=sstep(c+0.12,pl,t); const p=heldPoint(root,yw).lerp(slot(k),u); p.y+=0.05*Math.sin(Math.PI*u);
    return {pos:p,yaw:yw-Math.PI/2,flip:0,a:1,hand:['me']}; }
  return {pos:slot(k),yaw:DYAW-Math.PI/2,flip:0,a:1,placed:t-pl}; }
function redState(t){
  const r=TL.redRelease, L=TL.redLand, hy=haterYaw(RED,Math.min(t,r));
  if(t<r) return {pos:inHands(RED,hy,t-r,true),yaw:hy-Math.PI/2,flip:0,a:1,hand:['h',RED]};
  if(t<L){ const u=(t-r)/(L-r); return {pos:ballistic(hold(HP[RED],hy,'rel'),RED_LAND,L-r,u),yaw:angLerp(hy-Math.PI/2,-0.25,u),flip:2*Math.PI*sm5(u),a:1}; }
  const s=t-L; const p=RED_LAND.clone(); p.y+=Math.max(0,0.07*Math.sin(Math.PI*clamp(s/0.22)))+0.015*Math.max(0,Math.sin(Math.PI*clamp((s-0.22)/0.1)));
  p.addScaledVector(V(-0.3,0,0.2).normalize(),0.07*sm5(clamp(s/0.5)));
  return {pos:p,yaw:-0.25+0.22*sm5(clamp(s/0.5)),flip:0,a:1,landed:s}; }
// hand grips on a block (its local x axis)
const grips=(st)=>{ const ax=rotY(V(1,0,0),st.yaw); return [st.pos.clone().addScaledVector(ax,BW/2-0.02),st.pos.clone().addScaledVector(ax,-BW/2+0.02)]; };

// ---------------------------------------------------------------- poses
const P_STAND=R.POSES.stand;
const P_PLACE={...R.POSES.crouch,p:1.05,tilt:0.35,aL:1.05,aR:0.75,kL:1.75,kR:1.35};
function heroPose(t){
  const {root,stepU}=heroRoot(t), yaw=heroYaw(t), f=fwdOf(yaw);
  let P={...P_STAND, p:0.06+0.015*Math.sin(t*1.9)};
  // place crouch after each catch
  let cr=0, absorb=0, hold=null, wHold=0, ready=null, wReady=0;
  for(let k=0;k<NB;k++){ const c=TL.catches[k];
    cr=Math.max(cr,sstep(c+0.12,c+0.40,t)*(1-sstep(c+0.46,c+0.66,t)));
    absorb=Math.max(absorb,Math.exp(-Math.pow((t-c-0.06)/0.08,2)));
    if(t>=c-0.55&&t<c){ ready=grips({pos:catchPoint(k),yaw:catchYaw(k)-Math.PI/2}); wReady=sstep(c-0.55,c-0.12,t); }
    if(t>=c&&t<c+TL.place+0.3){ const st=blockState(k,Math.min(t,c+TL.place)); hold=grips(st); wHold=1-sstep(c+TL.place,c+TL.place+0.28,t); } }
  P=R.blend(P,P_PLACE,sm5(cr));
  P.dy-=0.05*absorb; P.p+=0.08*absorb;
  if(stepU>0) P=R.gait(P,Math.PI*0.5+2*Math.PI*stepU,Math.sin(Math.PI*stepU),0.42,0.9,0.12);
  // finale: ready for the red block, then lower the hands as it falls short, look down at it, then stand tall
  const r=TL.redRelease;
  if(t>r-0.4){ const w=sstep(r-0.4,r+0.1,t)*(1-sstep(r+0.45,r+1.0,t)); if(w>0){ ready=grips({pos:heldPoint(root,yaw),yaw:yaw-Math.PI/2}); wReady=w*0.85; } }
  const look=sstep(TL.lookDown-0.15,TL.lookDown+0.35,t)*(1-sstep(TL.standTall,TL.standTall+0.8,t));
  P.tilt+=0.55*look; P.p+=0.12*look;
  const tall=sstep(TL.standTall,TL.standTall+0.9,t); P.p-=0.06*tall; P.tilt-=0.1*tall; P.sL+=0.05*tall; P.sR-=0.0*tall;
  const brC=Math.sin(t*2.1)*0.01; P.p+=brC;
  if(hold&&wHold>0){ P.tL=hold[1]; P.tR=hold[0]; P.wL=wHold; P.wR=wHold; P.pL=V(-0.3,-0.6,0.8); P.pR=V(-0.3,-0.6,-0.8); }
  else if(ready&&wReady>0){ P.tL=ready[1]; P.tR=ready[0]; P.wL=wReady; P.wR=wReady; P.pL=V(-0.3,-0.6,0.8); P.pR=V(-0.3,-0.6,-0.8); }
  return {P,root,yaw}; }
function haterPose(i,t){
  const yaw=haterYaw(i,t); let P={...P_STAND,p:0.08+0.012*Math.sin(t*1.7+i*2),hy:0.0};
  let hand=null, w=0;
  const mine=[]; TL.throwers.forEach((th,k)=>{ if(th===i) mine.push(REL(k)); });
  let lowHold=false; if(i===RED){ mine.push(TL.redRelease); lowHold=true; }
  for(const r of mine){ const rel=t-r; const isRed=(i===RED);
    if(rel>=(isRed?-99:-1.0)&&rel<0){ const st=isRed?redState(t):{pos:inHands(i,yaw,rel),yaw:yaw-Math.PI/2}; hand=grips(st); w=isRed?1:sstep(-1.0,-0.8,rel); }
    if(rel>=0&&rel<0.5){ const f=fwdOf(yaw); const tip=hold(HP[i],yaw,'rel').addScaledVector(f,0.15).add(V(0,-0.35*sstep(0,0.5,rel),0)); hand=[tip.clone().addScaledVector(rotY(V(0,0,1),yaw),-0.22),tip.clone().addScaledVector(rotY(V(0,0,1),yaw),0.22)]; w=1-sstep(0.05,0.5,rel); }
    // body: lean back on the wind-up, drive forward on the release, settle
    if(rel>-0.6&&rel<0.9){ P.p+=keys([[-0.55,0],[-0.2,-0.3],[0.0,0.34],[0.3,0.3],[0.85,0]],rel); P.aL+=0.22*sstep(-0.3,0.0,rel)*(1-sstep(0.4,0.85,rel)); P.kR+=0.2*sstep(-0.3,0,rel)*(1-sstep(0.4,0.85,rel)); P.tilt+=keys([[-0.55,0],[-0.2,-0.2],[0,0.1],[0.85,0]],rel); } }
  // after the red block lands: arms down, heads drop, the thrower slumps
  const L=TL.redLand; const dn=sstep(L+0.2,L+1.0,t);
  P.tilt+=0.35*dn; P.p+=(i===RED?0.22:0.12)*dn;
  if(hand&&w>0){ P.tR=hand[0]; P.tL=hand[1]; P.wL=w; P.wR=w; P.pL=V(-0.3,-0.5,0.9); P.pR=V(-0.3,-0.5,-0.9); }
  return {P,yaw}; }

// ---------------------------------------------------------------- blocks + words per frame
const tmpQ=new THREE.Quaternion(), qY=new THREE.Quaternion(), qX=new THREE.Quaternion();
function setBlock(B,st,t,idx){
  if(!st){ B.m.visible=false; B.spr.visible=false; B.glow.material.opacity=0; return; }
  B.m.visible=st.a>0.02; B.m.position.copy(st.pos);
  qY.setFromAxisAngle(V(0,1,0),st.yaw); qX.setFromAxisAngle(V(1,0,0),st.flip); B.m.quaternion.copy(qY).multiply(qX);
  B.side=B.m.material[0]; B.m.material.forEach(m=>{ const tr=st.a<0.999; if(m.transparent!==tr){ m.transparent=tr; m.needsUpdate=true; } m.opacity=st.a; });
  // the floating word: above the block while it travels; on placement it sinks into the face and the face lights up
  const faceN=rotY(V(0,0,1),st.yaw), faceC=st.pos.clone().addScaledVector(faceN,BD/2+0.01);
  let sa=st.a, sp=st.pos.clone().add(V(0,0.24,0)), sc=1;
  let em=0, gl=0;
  if(st.placed!==undefined){ const u=sstep(0,0.22,st.placed); sp.lerp(faceC,u); sc=lerp(1,0.62,u); sa=1-sstep(0.12,0.26,st.placed);
    em=1.6*Math.exp(-st.placed/0.35)*sstep(0.1,0.2,st.placed)+0.42*sstep(0.12,0.4,st.placed); gl=0.5*Math.exp(-Math.pow((st.placed-0.2)/0.15,2)); }
  if(B.red){ em=0.05; sa=sstep(TL.redRelease-0.6,TL.redRelease-0.3,t); const fl=sstep(TL.redRelease-0.5,TL.redRelease,t); gl=0.14*fl; B.m.material[0].emissiveIntensity=0.05+0.25*fl*(st.landed!==undefined?Math.exp(-st.landed/0.6):1); if(st.landed!==undefined){ const s=st.landed; gl=0.55*Math.exp(-s/0.25); sa=1-sstep(0.05,0.9,s); em=0.05+0.25*Math.exp(-s/0.3); } }
  B.spr.visible=sa>0.01; B.spr.material.opacity=sa; B.spr.position.copy(sp); B.spr.scale.set((B.red?1.3:0.9)*sc,(B.red?0.26:0.225)*sc,1);
  B.face.emissiveIntensity=em; B.back.emissiveIntensity=0;
  B.glow.position.copy(B.red?st.pos:faceC); B.glow.scale.setScalar(B.red?0.9:0.7); B.glow.material.opacity=gl; }
function setSparks(t){
  let n=0;
  for(let k=0;k<NB;k++){ const pl=TL.catches[k]+TL.place; const s=t-pl-0.12; const fc=slot(k).addScaledVector(rotY(V(0,0,1),DYAW-Math.PI/2),BD/2+0.02);
    for(let j=0;j<40;j++,n++){ const r=SPR[n]; if(s<0||s>2.0){ spA[n]=0; continue; }
      const x=(r[0]-0.5)*BW*0.9, life=0.8+1.0*r[2], u=s/life; if(u>1){ spA[n]=0; continue; }
      const ax=rotY(V(1,0,0),DYAW-Math.PI/2);
      const p=fc.clone().addScaledVector(ax,x).add(V(0,(r[1]-0.5)*BH*0.6+s*(0.12+0.25*r[3]),0)).addScaledVector(rotY(V(0,0,1),DYAW-Math.PI/2),s*0.05*r[1]);
      spPos.set([p.x,p.y,p.z],n*3); spA[n]=(1-u)*(1-u)*sstep(0,0.05,s)*(0.4+0.6*r[3]); } }
  const L=TL.redLand; for(let j=0;j<90;j++,n++){ const r=SPR[n], s=t-L; if(s<0||s>2.5){ spA[n]=0; continue; }
    const a=r[0]*6.283, sp=0.35+0.9*r[1], d=sp*(1-Math.exp(-s*3))/3*1.6; const p=RED_LAND.clone().add(V(Math.cos(a)*d,0.02+0.25*r[2]*(1-Math.exp(-s*2.5))+0.05*s*r[3],Math.sin(a)*d*0.7));
    spPos.set([p.x,p.y,p.z],n*3); spA[n]=0.22*Math.exp(-s/0.9)*(0.3+0.7*r[3]); }
  spGeo.attributes.position.needsUpdate=true; spGeo.attributes.a.needsUpdate=true; }

// ---------------------------------------------------------------- camera: close on the first catch, then crane up with him and pull out
const CAMK=[[0.0,[0.35,1.45,6.9],[-0.42,1.12,0.0]],[2.6,[0.35,1.48,7.0],[-0.4,1.15,0.0]],[6.5,[0.35,1.85,7.45],[-0.22,1.5,-0.1]],[10.6,[0.35,2.2,7.95],[-0.12,1.85,-0.2]],[13.0,[0.35,2.25,8.5],[-0.1,1.82,-0.25]],[DUR,[0.35,2.35,9.1],[-0.08,1.9,-0.3]]];
function camAt(t){ const P=[0,1,2].map(i=>keys(CAMK.map(k=>[k[0],k[1][i]]),t)), L=[0,1,2].map(i=>keys(CAMK.map(k=>[k[0],k[2][i]]),t));
  cam.position.set(...P); cam.lookAt(...L); }

// ---------------------------------------------------------------- frame
function setT(t){
  const h=heroPose(t); R.poseFig(hero,R.skel(h.P,h.root,h.yaw));
  const fade=1-sstep(TL.fade0,TL.fade1,t);
  haters.forEach((F,i)=>{ const p=haterPose(i,t); R.poseFig(F,R.skel(p.P,HP[i],p.yaw)); F.setAlpha(fade); });
  blocks.forEach((B,k)=>setBlock(B,blockState(k,t),t,k));
  setBlock(redB,redState(t),t,99);
  setSparks(t); camAt(t);
  const pay=0.14*sstep(TL.pay0,TL.pay1,t);
  S.tick(t,pay); }
window.renderAt=(t,K=3)=>S.renderAt(setT,t,K,{t0:0,t1:DUR});
window.metaAt=t=>{ let placed=0; for(let k=0;k<NB;k++) if(t>=TL.catches[k]+TL.place) placed++; return {t,placed}; };
window.events={...TL,place_times:TL.catches.map(c=>c+TL.place),release_times:TL.catches.map((c,k)=>REL(k)),step_times:TL.catches.map(c=>[c+0.55,c+0.95])};
window.ready=true;
