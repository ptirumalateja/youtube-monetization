// Friends in Every Group (Slow Light Dark). Six friends at one table under the gold lamp. One by one each does their
// thing while the caption names them and a number pops over their head: the late one walks in out of the dark, the
// photographer needs one more photo (flash), one laughs at everything, one falls asleep, one eats the sleeper's fries,
// one slides the red bill (the one red object) across to the sleeper. End card: WHICH ONE ARE YOU?
//
// World: the table runs along z (near end z=0, far end z=-2), side L at x<0 faces +x, side R at x>0 faces -x.
// Seats: index 0 near, 1 middle, 2 far. Camera at the near end, raised, a little to the right.
// renderAt(t) is pure (no state between frames). metaAt(t) gives the overlay/sound data.
import * as THREE from 'three';
import * as SLD from './sld.js';
const {V,clamp,sstep,lerp,sm5,rng,yawOf,PAL}=SLD;
const TL=await (await fetch('./timeline.json')).json();
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960, DUR=TL.duration;

const S=SLD.createStage({W,H,lamp:V(0,4.8,-1.15),lampTarget:V(0,0,-1.15),cone:0.45,spot:44,motes:2200});
const R=SLD.createRig(S.scene);
const TOP=0.74, ZS=[-0.35,-1.15,-1.95];   // wide spacing so every action reads on its own

// ---------------------------------------------------------------- wood, table, chairs, plates, glasses, fries
function woodTex(seed,base){ const c=document.createElement('canvas'); c.width=1024; c.height=256; const g=c.getContext('2d'); const Rn=rng(seed);
  g.fillStyle=base; g.fillRect(0,0,1024,256);
  for(let k=0;k<260;k++){ const y=Rn()*256, a=0.04+Rn()*0.1; g.strokeStyle=Rn()<0.6?`rgba(0,0,0,${a})`:`rgba(255,220,180,${a*0.5})`; g.lineWidth=0.6+Rn()*2.2;
    g.beginPath(); g.moveTo(0,y); for(let x=0;x<=1024;x+=32) g.lineTo(x,y+Math.sin(x*0.004+k)*3+Math.sin(x*0.021+k*1.7)*1.2); g.stroke(); }
  const t=new THREE.CanvasTexture(c); t.wrapS=t.wrapT=THREE.RepeatWrapping; t.colorSpace=THREE.SRGBColorSpace; return t; }
const WOOD=SLD.rimify(new THREE.MeshStandardMaterial({color:0x8a6a52,map:woodTex(3,'#3b2a1f'),roughness:0.5,metalness:0}),0xffe6c8,0.05,'wood');
const CHAIRWOOD=SLD.rimify(new THREE.MeshStandardMaterial({color:0x7a5c46,map:woodTex(9,'#33241a'),roughness:0.62,metalness:0}),0xc8d4f0,0.07,'chair');
{ const top=new THREE.Mesh(new THREE.BoxGeometry(0.92,0.05,2.5),WOOD); top.position.set(0,TOP-0.025,-1.15); top.castShadow=top.receiveShadow=true; S.scene.add(top);
  for(const x of [-0.39,0.39]) for(const z of [0.05,-2.35]){ const l=new THREE.Mesh(new THREE.BoxGeometry(0.06,TOP-0.05,0.06),WOOD); l.position.set(x,(TOP-0.05)/2,z); l.castShadow=true; S.scene.add(l); } }
const chairGeo={seat:new THREE.BoxGeometry(0.42,0.04,0.42),leg:new THREE.BoxGeometry(0.035,0.44,0.035),post:new THREE.BoxGeometry(0.035,0.5,0.035),rail:new THREE.BoxGeometry(0.03,0.12,0.4)};
function makeChair(x,z,facing){ const g=new THREE.Group(); const add=(geo,a,b,c)=>{ const m=new THREE.Mesh(geo,CHAIRWOOD); m.position.set(a,b,c); m.castShadow=m.receiveShadow=true; g.add(m); };
  add(chairGeo.seat,0,0.44,0); for(const a of [-0.18,0.18]) for(const c of [-0.18,0.18]) add(chairGeo.leg,a,0.22,c);
  for(const c of [-0.18,0.18]) add(chairGeo.post,-0.19,0.71,c); add(chairGeo.rail,-0.19,0.88,0); add(chairGeo.rail,-0.19,0.68,0);
  g.position.set(x,0,z); g.rotation.y=yawOf(facing); S.scene.add(g); return g; }
const PLATEM=SLD.rimify(new THREE.MeshStandardMaterial({color:0x2a2a2e,roughness:0.35,metalness:0}),0xfff1d8,0.1,'plate');
const GLASSM=SLD.rimify(new THREE.MeshStandardMaterial({color:0xd8d2c4,roughness:0.12,metalness:0,transparent:true,opacity:0.42,depthWrite:false}),0xfff1d8,0.55,'glass');
const LIQM=new THREE.MeshStandardMaterial({color:0x4a2e16,roughness:0.2,metalness:0,transparent:true,opacity:0.85});
const FRYM=SLD.rimify(new THREE.MeshStandardMaterial({color:0xd9c49a,roughness:0.7,metalness:0}),0xfff1d8,0.12,'fry');
function makeGlass(x,z){ const g=new THREE.Group();
  const a=new THREE.Mesh(new THREE.CylinderGeometry(0.036,0.03,0.13,20,1,true),GLASSM); a.position.y=0.065;
  const l=new THREE.Mesh(new THREE.CylinderGeometry(0.032,0.028,0.08,20),LIQM); l.position.y=0.05;
  [a,l].forEach(m=>{ m.castShadow=true; m.renderOrder=3; g.add(m); }); g.position.set(x,TOP,z); S.scene.add(g); return g; }
const fryGeo=new THREE.BoxGeometry(0.012,0.012,0.075);
for(const s of [-1,1]) for(const [i,z] of ZS.entries()){
  const p=new THREE.Mesh(new THREE.CylinderGeometry(0.12,0.095,0.016,40),PLATEM); p.position.set(0.22*s,TOP+0.008,z); p.castShadow=p.receiveShadow=true; S.scene.add(p);
  makeGlass(0.3*s,z-0.17*s);
  const Rf=rng(40+i+(s>0?10:0)); const nF=(s<0&&i===1)?14:5;           // the sleeper's plate is full of fries (the thief's target)
  for(let k=0;k<nF;k++){ const f=new THREE.Mesh(fryGeo,FRYM); f.position.set(0.22*s+(Rf()-0.5)*0.12,TOP+0.024+Rf()*0.012,z+(Rf()-0.5)*0.12); f.rotation.set(0,Rf()*3,0.2*(Rf()-0.5)); f.castShadow=true; S.scene.add(f); } }
const heldFry=new THREE.Mesh(fryGeo,FRYM); heldFry.castShadow=true; S.scene.add(heldFry);

// ---------------------------------------------------------------- props: the red bill (the one red object), the photographer's phone
const billM=SLD.rimify(new THREE.MeshStandardMaterial({color:PAL.RED,roughness:0.5,metalness:0,emissive:PAL.RED,emissiveIntensity:0.12}),0xff8a70,0.2,'bill');
const bill=new THREE.Mesh(new THREE.BoxGeometry(0.13,0.014,0.21),billM); bill.castShadow=true; S.scene.add(bill);
const phoneM=new THREE.MeshStandardMaterial({color:0x1a1a1e,roughness:0.35,metalness:0.3});
const phone=new THREE.Group(); { const b=new THREE.Mesh(new THREE.BoxGeometry(0.075,0.15,0.01),phoneM); phone.add(b);
  const scr=new THREE.Mesh(new THREE.PlaneGeometry(0.065,0.135),new THREE.MeshBasicMaterial({color:0xede6d6})); scr.position.z=-0.006; scr.rotation.y=Math.PI; phone.add(scr); } S.scene.add(phone);
const flash=SLD.glowSprite(S.scene,0xfff4e0,0); const flashLight=new THREE.PointLight(0xfff4e0,0,4,2); S.scene.add(flashLight); S.NOREFL.push(flash);

// ---------------------------------------------------------------- faces (owner request for expression; the series sheet says no faces, this reel breaks it on purpose)
function faceTex(kind){ const c=document.createElement('canvas'); c.width=c.height=256; const g=c.getContext('2d');
  g.strokeStyle=g.fillStyle='#1d1610'; g.lineWidth=13; g.lineCap='round';
  const eye=(x,y)=>{ g.beginPath(); g.arc(x,y,13,0,7); g.fill(); };
  const closed=(x,y,up)=>{ g.beginPath(); up?g.arc(x,y+8,16,Math.PI*1.15,Math.PI*1.85):g.arc(x,y-10,16,Math.PI*0.15,Math.PI*0.85); g.stroke(); };
  if(kind==='smile'){ eye(96,110); eye(160,110); g.beginPath(); g.arc(128,140,34,0.2*Math.PI,0.8*Math.PI); g.stroke(); }
  if(kind==='laugh'){ closed(94,104,true); closed(162,104,true); g.beginPath(); g.moveTo(84,140); g.quadraticCurveTo(128,215,172,140); g.closePath(); g.fill(); }
  if(kind==='sleep'){ closed(94,116,false); closed(162,116,false); g.beginPath(); g.arc(128,162,10,0,7); g.stroke(); }
  if(kind==='sorry'){ eye(96,112); eye(160,112); g.lineWidth=9; g.beginPath(); g.moveTo(76,84); g.lineTo(108,94); g.moveTo(180,84); g.lineTo(148,94); g.stroke(); g.lineWidth=13; g.beginPath(); g.moveTo(100,166); g.quadraticCurveTo(128,150,156,166); g.stroke(); }
  if(kind==='excited'){ g.beginPath(); g.arc(96,106,17,0,7); g.arc(160,106,17,0,7); g.fill(); g.beginPath(); g.arc(128,138,36,0.05*Math.PI,0.95*Math.PI); g.closePath(); g.fill(); }
  if(kind==='chew'){ closed(94,108,true); closed(162,108,true); g.beginPath(); g.ellipse(128,156,22,13,0,0,7); g.fill(); }
  if(kind==='smug'){ g.beginPath(); g.moveTo(80,108); g.lineTo(112,108); g.moveTo(144,108); g.lineTo(176,108); g.stroke(); g.beginPath(); g.moveTo(96,152); g.quadraticCurveTo(140,170,166,140); g.stroke(); }
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; return t; }
const FACES={}; for(const k of ['smile','laugh','sleep','sorry','excited','chew','smug']) FACES[k]=new THREE.MeshBasicMaterial({map:faceTex(k),transparent:true,depthWrite:false,fog:false});
const faceGeo=new THREE.PlaneGeometry(0.235,0.235);

// ---------------------------------------------------------------- the six friends
const CHAIRP={...R.P0,p:0.07,tilt:0.0,aL:1.5,aR:1.47,kL:1.52,kR:1.47,sL:0.5,sR:0.5,eL:0.9,eR:0.9};
const STANDP={...R.P0,p:0.08};
const HIPBACK=0.276;
const GOLD_C=new THREE.Color(0xffc25a), CREAM_C=new THREE.Color(PAL.CREAM), SLATE_C=new THREE.Color(PAL.SLATE).multiplyScalar(0.7);
const SEATS={}; for(const [sd,s] of [['L',-1],['R',1]]) for(const i of [0,1,2]){ const face=V(-s,0,0);
  SEATS[sd+i]={id:sd+i,s,i,z:ZS[i],face,yaw:yawOf(face),root:V(s*0.72,0,ZS[i]).addScaledVector(face,HIPBACK),fig:R.makeFig(PAL.CREAM,'f'+sd+i,{rim:0.16,lift:0.07}),ph:i*1.7+(s>0?0.9:0)};
  { const f=new THREE.Mesh(faceGeo,FACES.smile); f.renderOrder=4; S.scene.add(f); SEATS[sd+i].face3=f; }
  makeChair(s*0.8,ZS[i],face); }
const BEAT={}; TL.beats.forEach(([t0,seat,lines],k)=>{ BEAT[seat]={t0,k,lines}; });
const bump=(t,a,d)=>{ const x=(t-a)/d; return x<=0||x>=1?0:Math.sin(Math.PI*x)**2; };
// hand helper: a point in front of a seat, in seat terms (fwd = toward the table centre line, up, side = +z)
const seatPt=(st,fwd,y,dz)=>V(st.s*0.72-st.s*fwd,y,st.z+dz);

function idle(st,t){
  const P={...CHAIRP}; const ph=st.ph;
  const talk=0.5+0.5*Math.sin(t*1.9+ph), L=Math.max(bump(t,(ph*0.7)%2.5,0.9),bump(t,3+(ph*1.3)%3,0.8)*0.7,bump(t,7+(ph*0.9)%3,0.8)*0.6);
  P.p+=0.08*talk-0.1*L+0.035*L*Math.sin(t*26); P.tilt+=-0.25*L+0.05*Math.sin(t*2.7+ph);
  P.hy=0.28*Math.sin(t*0.8+ph);  P.ty=0.1*Math.sin(t*0.8+ph);
  const hR=seatPt(st,0.42,TOP+0.04+0.1*Math.max(0,Math.sin(t*3.3+ph)),-0.11*st.s), hL=seatPt(st,0.4,TOP+0.04,0.11*st.s);
  Object.assign(P,{tR:hR,wR:1,pR:V(-0.3,-0.7,-0.7),tL:hL,wL:1,pL:V(-0.3,-0.7,0.7)});
  return P;
}
// returns {P, root} for a seat at time t, including its beat action
function lookAtActive(st,t,P){
  let act_=null, k=0; for(const o of Object.values(SEATS)){ const v=auraK(o,t); if(v>k){ k=v; act_=o; } }
  if(!act_||act_===st||st.id==='L1'&&t>BEAT.L1.t0) return P;
  const d=act_.root.clone().sub(st.root); const f=SLD.rotY(V(1,0,0),st.yaw), z=SLD.rotY(V(0,0,1),st.yaw);
  const y=clamp(Math.atan2(-d.dot(z),d.dot(f)),-1.3,1.3);
  P.hy=lerp(P.hy,y*0.75,k); P.ty=lerp(P.ty,y*0.3,k); return P; }
function faceKind(st,t){
  const u=t-BEAT[st.id].t0;
  if(st.id==='L1'&&u>0.3) return 'sleep';
  if(st.id==='R1'&&u<1.0) return 'sorry';
  if(st.id==='R2'&&(u>-0.05&&u<1.4||bump(u,1.9,1.2)>0.3||bump(u,4.2,1.1)>0.3)) return 'laugh';
  if(st.id==='L2'&&u>-0.15&&u<1.4) return 'excited';
  if(st.id==='L0'&&u>0.4&&u<2.6) return 'chew';
  if(st.id==='R0'&&u>0.8) return 'smug';
  return 'smile'; }
function act(st,t){
  const b=BEAT[st.id], u=t-b.t0; let P=lookAtActive(st,t,idle(st,t)), root=st.root.clone();
  switch(st.id){
    case 'R1': {   // the late one: walks in from the dark, sits down as his caption lands
      const arrive=b.t0+0.55, sat=b.t0+1.05;
      if(t<sat){ const x=lerp(2.2,1.12,clamp(t/arrive)); const standRoot=V(x,0,st.z);   // in frame from frame 0
        let Q=R.gait({...STANDP,p:0.22},(2.2-x)/1.1*Math.PI*2,1.25*(1-sstep(arrive-0.2,arrive,t)));   // hurrying in
        const sit=sstep(arrive,sat,t); P=R.blend(Q,P,sit); root=standRoot.lerp(st.root,sit); }
      { const w=Math.max(t<sat?0.9:0,bump(t,sat-0.2,1.1)); P.tL=(t<sat?root.clone().add(V(-0.12,1.55,0.25)):seatPt(st,0.1,1.48,0.2*st.s)).add(V(0,0.04*Math.sin(t*18),0)); P.wL=w; P.pL=V(0,-0.3,1); }   // 'sorry sorry' hand up
      break; }
    case 'L2': {   // the photographer: phone up high, "one more", flash
      const up=sstep(-0.15,0.25,u)*(1-sstep(1.15,1.5,u));
      P.tR=P.tR.clone().lerp(seatPt(st,0.18,1.72,-0.12),up); P.p+=0.12*up; P.tilt-=0.35*up; P.hy=lerp(P.hy,0,up);
      P.tL=P.tL.clone().lerp(seatPt(st,0.45,1.35,0.18+0.09*Math.sin(t*16)),up); P.wL=1;   // 'wait wait': the free hand waves the others in
      break; }
    case 'R2': {   // laughs at everything: rocks back, bounces, slaps the table
      const k=Math.max(bump(u,-0.05,1.45),bump(u,1.9,1.2)*0.6,bump(u,4.2,1.1)*0.45,bump(u,6.4,1.0)*0.4);
      P.p+=-0.38*k+0.07*k*Math.sin(t*30); P.tilt+=-0.75*k; P.hy*=(1-k);   // head thrown right back
      P.tR=P.tR.clone().lerp(seatPt(st,0.38,TOP+0.03+0.13*Math.abs(Math.sin(t*11)),-0.08*st.s),k);
      break; }
    case 'L1': {   // falls asleep: slumps onto folded arms and stays there
      const sl=sm5(sstep(0.0,0.55,u)), br=0.012*Math.sin(t*2.2);
      P.p=lerp(P.p,0.86+br,sl); P.tilt=lerp(P.tilt,0.55,sl); P.hy=lerp(P.hy,0.35,sl); P.ty=lerp(P.ty,0,sl);   // head down on the table
      P.tR=P.tR.clone().lerp(seatPt(st,0.36,TOP+0.05,-0.08*st.s),sl); P.tL=P.tL.clone().lerp(seatPt(st,-0.02,0.3,0.26*st.s),sl);   // one arm dangling off the side
      break; }
    case 'L0': {   // eats your food: reaches over to the sleeper's plate twice
      const g1=bump(u,0.05,0.75), g2=bump(u,0.75,0.6), grab=Math.max(g1,g2);
      const plate=V(-0.24,TOP+0.06,ZS[1]+0.1), mouth=seatPt(st,0.06,1.28,0);
      const reach=Math.min(1,grab*1.5);
      P.tR=P.tR.clone().lerp(plate,reach); P.p+=0.2*reach; P.hy=lerp(P.hy,0.4,reach); P.ty=lerp(P.ty,-0.25,reach);
      const eat=bump(u,0.55,0.4)+bump(u,1.2,0.45)+bump(u,2.0,0.4)*0.5;
      P.tR=P.tR.clone().lerp(mouth,Math.min(1,eat)); P.tilt+=-0.12*eat;
      break; }
    case 'R0': {   // never pays: pushes the red bill across to the sleeper, leans back, hands behind his head
      const push=bump(u,0.05,0.85), back=sstep(0.75,1.1,u);
      P.tR=P.tR.clone().lerp(V(lerp(0.3,-0.02,sstep(0.15,0.6,u)),TOP+0.03,ZS[0]+lerp(0,-0.25,sstep(0.15,0.6,u))),push); P.p+=0.2*push;
      const head=seatPt(st,-0.12,1.38,0);
      P.tR=P.tR.clone().lerp(head.clone().add(V(0,0,-0.1)),back); P.tL=P.tL.clone().lerp(head.clone().add(V(0,0,0.1)),back);
      P.p-=0.14*back; P.tilt-=0.12*back; P.pR=V(0.2,0.9,-0.5); P.pL=V(0.2,0.9,0.5);
      break; }
  }
  return {P,root};
}

// ---------------------------------------------------------------- camera: near end of the table, raised, a little right; slow push in, pull back for the end card
function camAt(t){
  const push=sm5(clamp(t/TL.endCard)), back=sstep(TL.endCard,TL.endCard+1.2,t);
  const tg=V(0.2,lerp(1.0,1.05,push),lerp(-1.2,-1.15,push));   // shifted so the right-hand seats (late one, laugher) never clip
  const dist=lerp(6.6,6.2,push)+0.4*back, az=lerp(0.1,0.06,push), el=lerp(0.95,0.9,push)+0.03*back;   // high: the table runs up the frame
  const dir=V(Math.sin(az)*Math.cos(el),Math.sin(el),Math.cos(az)*Math.cos(el));
  return {pos:tg.clone().addScaledVector(dir,dist),tg};
}

// ---------------------------------------------------------------- the ki aura (owner request): gold flames rise off whoever is being named
// Pure per frame: every flame's position is a function of t and its seed (no state between frames).
const AURA_N=900, auraPos=new Float32Array(AURA_N*3), auraA=new Float32Array(AURA_N), auraSeed=[];
{ const Ra=rng(77); for(let i=0;i<AURA_N;i++) auraSeed.push([Ra(),Ra(),Ra(),Ra(),Ra()]); }
const auraGeo=new THREE.BufferGeometry(); auraGeo.setAttribute('position',new THREE.BufferAttribute(auraPos,3)); auraGeo.setAttribute('alpha',new THREE.BufferAttribute(auraA,1));
const auraMat=new THREE.ShaderMaterial({uniforms:{uH:{value:H}},transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
  vertexShader:`attribute float alpha; uniform float uH; varying float vA; void main(){ vA=alpha; vec4 mv=modelViewMatrix*vec4(position,1.0); gl_Position=projectionMatrix*mv; gl_PointSize=clamp(0.09*uH/(-mv.z),2.0,70.0); }`,
  fragmentShader:`varying float vA; void main(){ vec2 c=gl_PointCoord-0.5; c.x*=1.8; float d=length(c); float a=smoothstep(0.5,0.0,d); gl_FragColor=vec4(mix(vec3(1.0,0.72,0.28),vec3(1.0,0.97,0.85),a*a)*a*vA,1.0); }`});
const aura=new THREE.Points(auraGeo,auraMat); aura.frustumCulled=false; aura.renderOrder=6; S.scene.add(aura); S.NOREFL.push(aura);
const auraGlow=SLD.glowSprite(S.scene,0xffc860,0); S.NOREFL.push(auraGlow);
const auraLight=new THREE.PointLight(0xffc860,0,2.2,2); S.scene.add(auraLight);
const auraK=(st,t)=>{ const t0=BEAT[st.id].t0; return sstep(t0-0.02,t0+0.12,t)*(1-sstep(BEAT[st.id].t0+TL.beatLen-0.2,BEAT[st.id].t0+TL.beatLen+0.05,t)); };
function updateAura(t){
  let st=null, k=0; for(const s of Object.values(SEATS)){ const v=auraK(s,t); if(v>k){ k=v; st=s; } }
  if(!st||k<0.003){ aura.visible=false; auraGlow.material.opacity=0; auraLight.intensity=0; return; }
  aura.visible=true;
  const J=st.fig.joints.map(j=>j.position).concat([st.fig.head.position]);
  for(let i=0;i<AURA_N;i++){ const [a,b,c,d,e]=auraSeed[i];
    const base=J[Math.floor(a*J.length)];
    const ph=(t*(2.6+1.8*b)+c)%1;                                   // each flame licks upward fast and dies, then starts again
    const ang=d*6.283, r=(0.06+0.06*e)*(1-0.5*ph);                   // hugs the body, narrows as it rises (flame shape)
    auraPos[i*3]=base.x+Math.cos(ang)*r; auraPos[i*3+1]=base.y-0.02+ph*(0.3+0.25*e); auraPos[i*3+2]=base.z+Math.sin(ang)*r;
    auraA[i]=k*0.14*Math.pow(Math.sin(Math.PI*ph),1.5)*(0.6+0.4*Math.sin(t*41+i)); }
  auraGeo.attributes.position.needsUpdate=true; auraGeo.attributes.alpha.needsUpdate=true;
  const hip=st.fig.joints[12].position; auraGlow.position.copy(hip).add(V(0,0.35,0)); auraGlow.scale.set(1.3,1.9,1); auraGlow.material.opacity=0.14*k*(0.9+0.1*Math.sin(t*23));
  auraLight.position.copy(hip).add(V(0,0.5,0)); auraLight.intensity=1.0*k*(0.9+0.1*Math.sin(t*19));
}

// ---------------------------------------------------------------- one frame
function setT(t){
  { const c=camAt(t); S.cam.position.copy(c.pos); S.cam.lookAt(c.tg); }
  for(const st of Object.values(SEATS)){
    const {P,root}=act(st,t); R.poseFig(st.fig,R.skel(P,root,st.yaw));
    { const hd=P.p+P.tilt, fl=SLD.rotY(SLD.rotY(V(Math.cos(hd),-Math.sin(hd),0),P.hy),P.ty), ul=SLD.rotY(SLD.rotY(V(Math.sin(hd),Math.cos(hd),0),P.hy),P.ty);
      const h=st.fig.head.position, toCam=S.cam.position.clone().sub(h).normalize();
      // cartoon cheat, sideways only: faces swing toward the camera around the vertical axis but keep the head's own up/down
      // angle (cheating the pitch too made every face look up at the high camera)
      const fT=SLD.rotY(fl,st.yaw), hz=V(fT.x,0,fT.z), hl=hz.length(), tc=V(toCam.x,0,toCam.z).normalize();
      hz.normalize().lerp(tc,0.55).normalize().multiplyScalar(hl);
      const fw=V(hz.x,fT.y,hz.z).normalize(), uw=SLD.rotY(ul,st.yaw);
      st.face3.position.copy(h).addScaledVector(fw,0.132); st.face3.up.copy(uw); st.face3.lookAt(h.clone().addScaledVector(fw,1)); st.face3.material=FACES[faceKind(st,t)]; st.face3.visible=!(st.id==='L1'&&t>BEAT.L1.t0+0.45); }   // face-down sleeper: the Z z z tells it
    // spotlight: the one being named stays bright cream, the other five sink toward slate (owner: highlight the selected one)
    let mine=auraK(st,t), any=0; for(const o of Object.values(SEATS)) any=Math.max(any,auraK(o,t));
    const dim=0.75*Math.max(0,any-mine);
    st.fig.mat.color.copy(CREAM_C).lerp(SLATE_C,dim); st.fig.mat.emissive.copy(st.fig.mat.color).lerp(GOLD_C,mine); st.fig.mat.emissiveIntensity=0.07*(1-dim)+0.26*mine;   // the named one glows gold head to toe
  }
  // phone: in the photographer's right hand, screen toward the table
  const ph=SEATS.L2.fig.joints[11].position; phone.position.copy(ph).add(V(0.03,0.06,0)); phone.rotation.set(0,-Math.PI/2,0.2);
  const u2=t-BEAT.L2.t0, f=Math.exp(-Math.max(0,u2-0.72)*14)*(u2>0.72?1:0);
  flash.position.copy(phone.position).add(V(0.05,0,0)); flash.scale.setScalar(0.6); flash.material.opacity=0.9*f; flashLight.position.copy(flash.position); flashLight.intensity=6*f;
  // the bill: in front of R0, slid across to the sleeper
  const u6=t-BEAT.R0.t0, sl=sm5(sstep(0.15,0.6,u6));
  bill.position.set(lerp(0.3,-0.2,sl),TOP+0.008,lerp(ZS[0]-0.02,ZS[1]+0.12,sl)); bill.rotation.y=lerp(0.2,-0.5,sl);
  // the stolen fry rides in the thief's hand between plate and mouth
  const u5=t-BEAT.L0.t0, carry=(u5>0.35&&u5<0.75)||(u5>1.0&&u5<1.4);
  heldFry.visible=carry; heldFry.position.copy(SEATS.L0.fig.joints[11].position).add(V(0.02,0.02,0)); heldFry.rotation.set(0.6,0.3,0);
  updateAura(t);
  const c=camAt(t); S.cam.position.copy(c.pos); S.cam.lookAt(c.tg);
  S.tick(t,0.08*sstep(TL.endCard,TL.endCard+0.8,t));
}

// ---------------------------------------------------------------- overlay / sound data: each friend's number sits above their head
const v3=new THREE.Vector3();
window.metaAt=t=>{ setT(t); S.cam.updateMatrixWorld(); const tags=[];
  for(const st of Object.values(SEATS)){ const b=BEAT[st.id]; const a=sstep(b.t0+0.1,b.t0+0.35,t)*1;
    v3.copy(st.fig.head.position).add(V(0,0.3,0)).project(S.cam);
    tags.push({seat:st.id,n:b.k+1,x:(v3.x*0.5+0.5)*1080,y:(0.5-v3.y*0.5)*1920,a,active:bump(t,b.t0,TL.beatLen)}); }
  return {tags}; };
window.events={...TL};
window.renderAt=(t,K=3)=>S.renderAt(setT,t,K,{t0:0,t1:DUR});
window.ready=true;


