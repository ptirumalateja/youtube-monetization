// 30 Friends to 1 (Slow Light Dark). A long dark table under the gold lamp: 30 slate friends, the cream hero at the head,
// his cream best friend at his right, one red candle. AGE 20 -> 60: the friends stand, push their chairs in and walk into
// the dark (glasses stay), faster and faster; the two cream friends stoop a little; the lamp narrows onto them; the candle
// burns down. At 60 the friend slides him an abandoned glass; they clink; the lamp warms and the flame steadies.
//
// Table frame: u along the table (head edge at u=0, away from the camera), v across it (+v = side A = the hero's right).
// renderAt(t) is pure (no state between frames). metaAt(t) gives the overlay/sound data (age, friend count, labels).
import * as THREE from 'three';
import * as SLD from './sld.js';
const {V,clamp,sstep,lerp,sm5,rng,yawOf,PAL,UPV}=SLD;
const TL=await (await fetch('./timeline.json')).json();
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960, DUR=TL.duration;

// ---------------------------------------------------------------- table frame
const ANG=0.30;                                            // table yaw (rad): recedes up and to the right in the frame
const U=V(Math.sin(ANG),0,-Math.cos(ANG)), RT=U.clone().cross(UPV);
const W2=(u,v,y=0)=>V(0,y,0).addScaledVector(U,u).addScaledVector(RT,v);
const NSIDE=15, PITCH=0.52, U0=0.45, TOP=0.74, HALF=0.52, LT=U0*2+PITCH*(NSIDE-1);
const seatU=i=>U0+PITCH*i;

// ---------------------------------------------------------------- stage: the lamp hangs over the head end; wide and aimed down the table at 20, narrow on the two at 60
const LAMP=W2(0.75,0.1,5.2), AIM0=W2(2.8,0,0), AIM1=W2(0.16,0.22,0), CONE0=0.7, CONE1=0.29;
const S=SLD.createStage({W,H,lamp:LAMP,lampTarget:AIM0,cone:CONE0,spot:66,beam:0.12,motes:2600});
const R=SLD.createRig(S.scene);
S.spot.shadow.camera.far=15;
const beamMesh=S.NOREFL[0];
{ const h=12.5, r=Math.tan(CONE0)*h*1.05; const g=new THREE.CylinderGeometry(0.02,r,h,96,24,true); g.translate(0,-h/2,0); beamMesh.geometry.dispose(); beamMesh.geometry=g; }
// dither the ray-march start per pixel: the wide cone showed 16-step banding near the lamp
beamMesh.material.fragmentShader=beamMesh.material.fragmentShader.replace('float acc=0.0;','float acc=0.0; float jit=fract(sin(dot(gl_FragCoord.xy,vec2(12.9898,78.233)))*43758.5453)-0.5;')
  .replace('float s=tEnd*(float(i)+0.5)/16.0;','float s=tEnd*(float(i)+0.5+jit)/16.0;'); beamMesh.material.needsUpdate=true;
function aim(target,cone){ const d=target.clone().sub(LAMP).normalize();
  S.spot.target.position.copy(target); S.spot.target.updateMatrixWorld(); S.spot.angle=cone+0.08;
  S.beamU.uAxis.value.copy(d); S.beamU.uTan.value=Math.tan(cone); S.moteU.uTan.value=Math.tan(cone);
  beamMesh.quaternion.setFromUnitVectors(V(0,-1,0),d); }

// ---------------------------------------------------------------- materials
function woodTex(seed,base){ const c=document.createElement('canvas'); c.width=1024; c.height=256; const g=c.getContext('2d'); const Rn=rng(seed);
  g.fillStyle=base; g.fillRect(0,0,1024,256);
  for(let k=0;k<260;k++){ const y=Rn()*256, a=0.04+Rn()*0.1; g.strokeStyle=Rn()<0.6?`rgba(0,0,0,${a})`:`rgba(255,220,180,${a*0.5})`; g.lineWidth=0.6+Rn()*2.2;
    g.beginPath(); g.moveTo(0,y); for(let x=0;x<=1024;x+=32) g.lineTo(x,y+Math.sin(x*0.004+k)*3+Math.sin(x*0.021+k*1.7)*1.2); g.stroke(); }
  const t=new THREE.CanvasTexture(c); t.wrapS=t.wrapT=THREE.RepeatWrapping; t.colorSpace=THREE.SRGBColorSpace; return t; }
const WOOD=new THREE.MeshStandardMaterial({color:0x8a6a52,map:woodTex(3,'#3b2a1f'),roughness:0.5,metalness:0});
const CHAIRWOOD=new THREE.MeshStandardMaterial({color:0x7a5c46,map:woodTex(9,'#33241a'),roughness:0.62,metalness:0});
SLD.rimify(WOOD,0xffe6c8,0.05,'wood'); SLD.rimify(CHAIRWOOD,0xc8d4f0,0.07,'chair');

// ---------------------------------------------------------------- table
{ const top=new THREE.Mesh(new THREE.BoxGeometry(LT,0.05,HALF*2),WOOD); top.material.map.repeat.set(4,1);
  top.position.copy(W2(LT/2,0,TOP-0.025)); top.rotation.y=yawOf(U); top.castShadow=top.receiveShadow=true; S.scene.add(top);
  const apron=new THREE.Mesh(new THREE.BoxGeometry(LT-0.2,0.09,HALF*2-0.12),WOOD); apron.position.copy(W2(LT/2,0,TOP-0.095)); apron.rotation.y=yawOf(U); apron.castShadow=true; S.scene.add(apron);
  for(const u of [0.08,LT/3,2*LT/3,LT-0.08]) for(const v of [-HALF+0.07,HALF-0.07]){ const l=new THREE.Mesh(new THREE.BoxGeometry(0.07,TOP-0.05,0.07),WOOD); l.position.copy(W2(u,v,(TOP-0.05)/2)); l.rotation.y=yawOf(U); l.castShadow=true; S.scene.add(l); } }

// ---------------------------------------------------------------- chairs: group local +x faces the table
const chairGeo={seat:new THREE.BoxGeometry(0.42,0.04,0.42),leg:new THREE.BoxGeometry(0.035,0.44,0.035),post:new THREE.BoxGeometry(0.035,0.5,0.035),rail:new THREE.BoxGeometry(0.03,0.12,0.4)};
function makeChair(){ const g=new THREE.Group(); const add=(geo,x,y,z)=>{ const m=new THREE.Mesh(geo,CHAIRWOOD); m.position.set(x,y,z); m.castShadow=m.receiveShadow=true; g.add(m); };
  add(chairGeo.seat,0,0.44,0); for(const x of [-0.18,0.18]) for(const z of [-0.18,0.18]) add(chairGeo.leg,x,0.22,z);
  for(const z of [-0.18,0.18]) add(chairGeo.post,-0.19,0.71,z); add(chairGeo.rail,-0.19,0.88,0); add(chairGeo.rail,-0.19,0.68,0); S.scene.add(g); return g; }
function placeChair(c,u,v,facing){ c.position.copy(W2(u,v,0)); c.rotation.y=yawOf(facing); }

// ---------------------------------------------------------------- glasses: tumbler + dark liquid
const GLASSM=new THREE.MeshStandardMaterial({color:0xd8d2c4,roughness:0.12,metalness:0,transparent:true,opacity:0.42,depthWrite:false});
SLD.rimify(GLASSM,0xfff1d8,0.55,'glass');
const LIQM=new THREE.MeshStandardMaterial({color:0x4a2e16,roughness:0.2,metalness:0,transparent:true,opacity:0.85});
const glassGeo=new THREE.CylinderGeometry(0.033,0.027,0.11,20,1,true), liqGeo=new THREE.CylinderGeometry(0.029,0.025,0.06,20), baseGeo=new THREE.CylinderGeometry(0.027,0.027,0.012,20);
function makeGlass(){ const g=new THREE.Group(); const a=new THREE.Mesh(glassGeo,GLASSM); a.position.y=0.055; const l=new THREE.Mesh(liqGeo,LIQM); l.position.y=0.04; const b=new THREE.Mesh(baseGeo,GLASSM); b.position.y=0.006;
  [a,l,b].forEach(m=>{ m.castShadow=true; m.renderOrder=3; g.add(m); }); g.scale.setScalar(1.25); S.scene.add(g); return g; }

// ---------------------------------------------------------------- the red candle (the one red object): burns down 3..13 s, flame steadies after the clink
const CANDLE_AT=W2(1.02,0.0,TOP);
const candleM=new THREE.MeshStandardMaterial({color:PAL.RED,roughness:0.55,metalness:0,emissive:PAL.RED,emissiveIntensity:0.05});
SLD.rimify(candleM,0xff8a70,0.12,'candle');
const candle=new THREE.Mesh(new THREE.CylinderGeometry(0.032,0.034,1,28),candleM); candle.castShadow=true; S.scene.add(candle);
const dish=new THREE.Mesh(new THREE.CylinderGeometry(0.07,0.075,0.012,28),SLD.IRON()); dish.position.copy(CANDLE_AT).add(V(0,0.006,0)); dish.castShadow=true; S.scene.add(dish);
const wick=new THREE.Mesh(new THREE.CylinderGeometry(0.0025,0.0025,0.018,6),new THREE.MeshBasicMaterial({color:0x111111})); S.scene.add(wick);
const flame=SLD.glowSprite(S.scene,0xffb468,0.9), flameCore=SLD.glowSprite(S.scene,0xfff0d0,0.9), candleHalo=SLD.glowSprite(S.scene,0xff3a2a,0.03);
const candleLight=new THREE.PointLight(0xffa25a,0.6,2.2,2); S.scene.add(candleLight);
const candleH=t=>lerp(0.25,0.085,sstep(2.6,13.4,t));

// ---------------------------------------------------------------- people
const hero=R.makeFig(PAL.CREAM,'hero',{rim:0.16,lift:0.07});
const heroChair=makeChair();
const CHAIRP={...R.P0,p:0.07,tilt:0.0,aL:1.5,aR:1.47,kL:1.52,kR:1.47,sL:0.5,sR:0.5,eL:0.9,eR:0.9};
const HIPBACK=0.276;   // skel puts the hip this far behind the root for CHAIRP
// friends: id 0..14 side A (+v, hero's right), 15..29 side B. id 0 (A0) is the best friend.
const F=[]; const Rn=rng(30);
for(let id=0;id<30;id++){ const s=id<15?1:-1, i=id%15, u=seatU(i);
  const best=id===0; const fig=best?R.makeFig(PAL.CREAM,'best',{rim:0.16,lift:0.07}):R.makeFig(PAL.SLATE,'f'+id,{rim:0.08,rimCol:0x9fb2d6});
  const face=RT.clone().multiplyScalar(-s);                  // seated facing the table centre line
  const rdir=s;                                                // right hand points to +U on side A, -U on side B
  F.push({id,s,i,u,best,fig,chair:makeChair(),glass:makeGlass(),face,yaw:yawOf(face),rdir,
    ph:Rn()*6.283, chat:0.7+Rn()*0.6, lean:(Rn()<0.5?-1:1), laughs:[], sips:[], toast:0.15+Rn()*0.55, hand:Rn()}); }
// laugh bursts and sips (deterministic)
for(const f of F){ let t=-1.5+Rn()*1.2; while(t<DUR){ f.laughs.push([t,0.7+Rn()*0.7,0.6+Rn()*0.5]); t+=0.9+Rn()*2.4; }
  t=2.2+Rn()*3; while(t<DUR){ f.sips.push(t); t+=3+Rn()*4; } }

// departures: 30 -> 14 in four waves (several chairs scrape back at once, all over the lit table, while the camera is
// still wide), then the last 13 one at a time, nearest the two, five of them with a reason label. B0, the seat across
// from the best friend, is the last to go.
const PINS=[8,6,4,2], LBL={8:'MOVED',6:'MARRIED',4:'BUSY',2:'DRIFTED',15:'GONE'};
const order=[], tds=[], sps=[];
{ const rest=[]; for(let id=1;id<30;id++) if(id!==15&&!PINS.includes(id)) rest.push([F[id].i+Rn()*2.5,id]);
  rest.sort((x,y)=>y[0]-x[0]);                                   // far -> near
  // waves take seats from all over the lit table (gaps open everywhere at once); the nearest seats are kept for the solo exits
  const nW=TL.waves.reduce((a,w)=>a+w[1],0), nNear=rest.length-nW, near=rest.slice(-nNear), wave=rest.slice(0,-nNear).map(x=>x[1]);
  for(let j=wave.length-1;j>0;j--){ const k=Math.floor(Rn()*(j+1)); [wave[j],wave[k]]=[wave[k],wave[j]]; }   // each wave spans the table
  let p=0; for(const [t0,n] of TL.waves) for(let j=0;j<n;j++){ order.push(wave[p++]); tds.push(t0+j*0.085+Rn()*0.04); sps.push(1.15); }
  const singles=near.concat(PINS.map(id=>[F[id].i,id])).sort((x,y)=>y[0]-x[0]).map(x=>x[1]); singles.push(15);
  const [s0,s1]=TL.singles; singles.forEach((id,j)=>{ order.push(id); tds.push(s0+(s1-s0)*j/(singles.length-1)); sps.push(lerp(1.15,1.45,j/(singles.length-1))); }); }
const DEP=order.map((id,k)=>({k,id,td:tds[k],sp:sps[k],label:LBL[id]||null}));
DEP.forEach(d=>{ F[d.id].dep=d; });
// AGE 20 -> 35 while the table empties (the last friend leaves at 35), then 35 -> 60 with only the two of them left
const A35=TL.age35+TL.hold35;   // hold "AGE 35 / 1 FRIEND" long enough to read
const ageAt=t=>t<TL.age35?20+15*clamp((t-TL.age0)/(TL.age35-TL.age0)):35+25*clamp((t-A35)/(TL.age1-A35));
const agedK=t=>{ const a=clamp((ageAt(t)-20)/40); return a*a*(3-2*a); };   // 0 at 20, 1 at 60 (heroes' stoop)
const energy=t=>lerp(1,0.35,sstep(2.5,8.5,t));
const leftAt=d=>d.td+0.62/d.sp;                               // the moment a friend counts as gone (stood and turned away)
const countAt=t=>30-DEP.filter(d=>t>=leftAt(d)).length;

// ---------------------------------------------------------------- per-figure motion
const bump=(t,a,d)=>{ const x=(t-a)/d; return x<=0||x>=1?0:Math.sin(Math.PI*x)**2; };
function laughAt(f,t,E){ let L=0; for(const [a,d,g] of f.laughs) L=Math.max(L,bump(t,a,d)*g); return L*E; }
function glassRest(f){ return W2(f.u+0.17*f.rdir,f.s*0.27,TOP); }
function seatedPose(f,t,E){
  const L=laughAt(f,t,E), chat=Math.sin(t*f.chat+f.ph);
  const P={...CHAIRP};
  P.p+=0.12*E*Math.max(0,chat)*0.6-0.13*L+0.045*L*Math.sin(t*31+f.ph);   // lean in when talking, rock back and bounce when laughing
  P.tilt+=-0.38*L+0.08*E*Math.sin(t*2.3+f.ph);
  P.hy=0.35*E*f.lean*Math.max(0,Math.sin(t*0.6*f.chat+f.ph*1.3));         // look at a neighbour
  P.ty=0.16*E*f.lean*Math.max(0,Math.sin(t*0.6*f.chat+f.ph*1.3));
  // glass: toast at frame 0 (already rising), then sips; free hand rests or gestures
  const raise=E*(t<3.2?bump(t,-0.9+f.toast*0.4,2.3):0), sip=Math.max(...f.sips.map(a=>bump(t,a,1.3)))*E;
  const rest=glassRest(f), up=W2(f.u+0.08*f.rdir,f.s*0.12,1.2+0.06*Math.sin(t*1.7+f.ph)), mouth=W2(f.u+0.05*f.rdir,f.s*0.5,1.24);
  const gp=rest.clone().lerp(up,sm5(clamp(raise))).lerp(mouth,sm5(clamp(sip)));
  const free=W2(f.u-0.16*f.rdir,f.s*0.33,TOP+0.03).add(V(0,0.16*L+0.1*E*Math.max(0,Math.sin(t*3.1+f.ph))*f.hand,0));
  const side=f.s; // elbows out to the sides of the body
  const rTarget=gp.clone().add(V(0,0.06,0)).addScaledVector(RT,side*0.085);   // grip from the body side so the glass stays visible
  Object.assign(P,{tR:rTarget,wR:1,pR:V(-0.3,-0.7,-0.7),tL:free,wL:1,pL:V(-0.3,-0.7,0.7)});
  return {P,gp};
}
const STANDP={...R.P0,p:0.1,sL:0.1,sR:-0.05,eL:0.25,eR:0.25};
function friendAt(f,t){
  const E=energy(t), seatHip=W2(f.u,f.s*0.72), seatRoot=seatHip.clone().addScaledVector(f.face,HIPBACK);
  const chairSeat=f.s*0.8;
  const d=f.dep;
  if(f.best) return null;
  if(!d||t<d.td){ const {P,gp}=seatedPose(f,t,E); return {P,root:seatRoot,yaw:f.yaw,alpha:1,gp,chairV:chairSeat}; }
  const tt=(t-d.td)*d.sp;
  const sit=seatedPose(f,d.td,E);
  // 1. stand (chair shoved back)
  const st=sstep(0.05,0.55,tt);
  let P=R.blend(sit.P,STANDP,st);
  const standRoot=W2(f.u,f.s*1.0);
  let root=seatRoot.clone().lerp(standRoot,st), yaw=f.yaw;
  let chairV=lerp(chairSeat,f.s*1.18,sstep(0.0,0.35,tt));
  // 2. step beside the chair, push it in under the table
  const sideU=f.u+0.42, stepRoot=W2(sideU,f.s*1.22);
  const so=sstep(0.55,0.85,tt);
  if(tt>0.55){ root=standRoot.clone().lerp(stepRoot,so); P=R.gait(P,so*Math.PI*2*0.55,Math.sin(Math.PI*so)*0.8); }
  const push=sstep(0.85,1.25,tt);
  if(tt>0.8){ chairV=lerp(f.s*1.18,f.s*0.62,push);
    const back=W2(f.u+0.19,f.s*(Math.abs(chairV)+0.19),0.9);
    const reach=sstep(0.78,0.9,tt)*(1-sstep(1.25,1.4,tt));
    P={...P,p:P.p+0.25*reach,tL:back,wL:reach,pL:V(-0.3,-0.7,0.6)};   // left hand on the chair back (the chair is on his left)
    root=stepRoot.clone().addScaledVector(RT,-f.s*0.4*push); }
  // 3. turn and walk off down the table into the dark, fading
  if(tt>1.3){ const dir=(f.s>0?U.clone().multiplyScalar(0.5).addScaledVector(RT,0.87):U.clone().multiplyScalar(0.94).addScaledVector(RT,-0.34)).normalize();   // camera-side walkers go down the table, not at the lens
    const tw=tt-1.3, turn=sstep(0,0.32,tw);
    const ang0=f.yaw, ang1=yawOf(dir); let da=ang1-ang0; da=Math.atan2(Math.sin(da),Math.cos(da)); yaw=ang0+da*turn;
    const dist=1.15*(tw<0.4?tw*tw/0.8:tw-0.2);
    root=stepRoot.clone().addScaledVector(RT,-f.s*0.4).addScaledVector(dir,dist);
    P=R.gait({...STANDP,p:0.12},dist/1.3*Math.PI*2,sstep(0,0.3,tw)); }
  const alpha=1-sstep(1.5,3.3,tt);
  return {P,root,yaw,alpha,gp:sit.gp?glassRest(f):null,chairV,tt};
}

// heroes: the hero at the head (facing +U), the best friend at A0. Young: laughing, big gestures. Old: stooped, slow, still.
const HERO_HIP=W2(-0.47,0.0), HERO_ROOT=HERO_HIP.clone().addScaledVector(U,HIPBACK), HERO_YAW=yawOf(U);
const BF=F[0], BF_HIP=W2(BF.u,0.72), BF_ROOT=BF_HIP.clone().addScaledVector(BF.face,HIPBACK);
const A1G=glassRest(F[1]), HERO_G=W2(0.03,0.17,TOP), BF_G=glassRest(BF);
const MEET=W2(0.12,0.34,1.03);
function oldPose(P,ag,t,slow){ P.p+=0.2*ag; P.tilt+=0.2*ag; P.sL+=0.1*ag; P.sR+=0.1*ag;
  P.p+=0.015*Math.sin(2*Math.PI*0.22*t)*(1-ag*0.4); return P; }
function heroesAt(t){
  const ag=agedK(t), E=energy(t), young=1-sstep(2.6,6.5,t);
  // --- hero
  const L=Math.max(bump(t,-0.7,1.6),bump(t,1.3,1.4)*0.8,bump(t,3.6,1.2)*0.5)*young;
  // 35 to 60: just the two of them, still laughing together now and then (slower, smaller every decade)
  const LT=Math.max(bump(t,TL.together[0],1.3)*0.55,bump(t,TL.together[1],1.2)*0.35);
  let P={...CHAIRP}; P.p+=-0.14*L+0.05*L*Math.sin(t*29)-0.08*LT+0.02*LT*Math.sin(t*17); P.tilt+=-0.4*L-0.22*LT; P.hy=0.25*young*Math.sin(t*0.9+0.6)-0.22*(1-young)*sstep(4,9,t);
  oldPose(P,ag,t);
  let hL=W2(0.1,-0.24,TOP+0.03).add(V(0,0.25*L+0.08*young*Math.max(0,Math.sin(t*3.3)),0));   // slaps the table laughing
  let hR=W2(0.12,0.22,TOP+0.03).add(V(0,0.2*L,0)); let hg=null;
  // the clink: take the slid glass, raise it
  const take=sstep(TL.take,TL.take+0.35,t), lift=sstep(TL.raise,TL.clink,t);
  let heroGlass=null;
  if(t>=TL.slideGo){ const slideU=lerp(0,1,sstep(TL.slideGo,TL.slideStop,t));
    heroGlass=A1G.clone().lerp(HERO_G,1-Math.pow(1-clamp((t-TL.slideGo)/(TL.slideStop-TL.slideGo)),2.2)); }
  if(heroGlass&&t>=TL.take){ const hold=MEET.clone().addScaledVector(RT,-0.044).add(V(0,-0.03,0));
    const back=sstep(TL.clink+0.05,TL.clink+0.55,t), settle=sstep(TL.endHold-0.3,TL.endHold+0.6,t);
    let gp=HERO_G.clone().lerp(hold,sm5(lift)); if(t>TL.clink) gp.addScaledVector(RT,-0.03*back).add(V(0,-0.06*settle,0));
    if(t<TL.clink) gp.addScaledVector(RT,-0.012*Math.sin(Math.PI*lift)); heroGlass=gp;
    hR=W2(0.12,0.22,TOP+0.03).lerp(gp.clone().add(V(0,0.03,0)).addScaledVector(U,-0.05).addScaledVector(RT,-0.08),take); }
  if(t>TL.clink){ const ch=bump(t,TL.clink+0.35,1.3); P.p+=-0.05*ch+0.012*ch*Math.sin(t*14); P.tilt+=-0.12*ch; }   // a quiet old laugh
  Object.assign(P,{tL:hL,wL:1,pL:V(-0.3,-0.7,0.7),tR:hR,wR:1,pR:V(-0.3,-0.7,-0.7)});
  // --- best friend: toasts with everyone at 20; at 60 slides the glass from the empty seat beside him, then raises his own
  const bE=E*young;
  const raise=bump(t,-0.6,2.3)*young, sip=bump(t,5.2,1.4)*0.6;
  const up=W2(BF.u+0.08,0.12,1.2), mouth=W2(BF.u+0.05,0.5,1.24);
  let bg=BF_G.clone().lerp(up,sm5(clamp(raise))).lerp(mouth,sm5(clamp(sip)));
  const L2=Math.max(bump(t,-0.4,1.5),bump(t,1.6,1.3)*0.7)*young;
  let Q={...CHAIRP}; Q.p+=-0.12*L2+0.045*L2*Math.sin(t*27)-0.08*LT+0.02*LT*Math.sin(t*15); Q.tilt+=-0.35*L2-0.22*LT; Q.hy=-0.3*sstep(3,6,t)*(1-sstep(TL.empty,TL.empty+0.6,t))-0.35*sstep(TL.empty,TL.empty+0.6,t);
  Q.ty=-0.12*sstep(TL.empty,TL.empty+0.6,t); oldPose(Q,ag,t);
  let rHand=bg.clone().add(V(0,0.03,0)).addScaledVector(RT,0.1), lHand=W2(BF.u-0.16,0.33,TOP+0.03);
  let slid=null;
  if(t>=TL.slideGrab&&t<TL.slideGo+0.4){ const g=sstep(TL.slideGrab,TL.slideGo,t), rel=sstep(TL.slideGo+0.2,TL.slideGo+0.4,t);
    const handOn=A1G.clone().lerp(HERO_G,0.5*sstep(TL.slideGo,TL.slideGo+0.3,t));   // shove: hand rides the glass for the first part
    rHand=rHand.lerp(handOn.clone().add(V(0,0.05,0)),g*(1-rel)); Q.p+=0.12*g*(1-rel); Q.ty+=0.12*g*(1-rel); }
  const blift=sstep(TL.raise-0.2,TL.clink,t);
  if(t>=TL.take-0.2){ const hold=MEET.clone().addScaledVector(RT,0.044).add(V(0,-0.03,0));
    const back=sstep(TL.clink+0.05,TL.clink+0.55,t), settle=sstep(TL.endHold-0.3,TL.endHold+0.6,t);
    bg=BF_G.clone().lerp(hold,sm5(blift)); if(t>TL.clink) bg.addScaledVector(RT,0.03*back).add(V(0,-0.06*settle,0));
    if(t<TL.clink) bg.addScaledVector(RT,0.012*Math.sin(Math.PI*blift));
    rHand=rHand.clone().lerp(bg.clone().add(V(0,0.03,0)).addScaledVector(RT,0.1),sstep(TL.take-0.2,TL.take+0.2,t)); }
  Object.assign(Q,{tR:rHand,wR:1,pR:V(-0.3,-0.7,-0.7),tL:lHand,wL:1,pL:V(-0.3,-0.7,0.7)});
  return {P,Q,heroGlass,bg};
}

// ---------------------------------------------------------------- camera (side three-quarter): position from target + (dist, azimuth off the table axis, elevation)
function camAt(t){
  // near-static wide while the table is full, the push-in carries the second half, then a slow creep in on the two
  const u=t<3?0.03*t/3:t<11.6?0.03+0.83*Math.pow(sstep(3,11.6,t),1.6):0.86+0.14*sstep(11.6,DUR+0.6,t);
  const tg=W2(lerp(2.9,0.02,u),lerp(0.3,0.3,u),lerp(2.0,1.12,u));
  const dist=lerp(12.5,4.4,u), az=lerp(0.36,1.75,u), el=lerp(0.62,0.17,u);
  const back=U.clone().multiplyScalar(-Math.cos(az)).addScaledVector(RT,-Math.sin(az));
  const dir=back.multiplyScalar(Math.cos(el)).add(V(0,Math.sin(el),0));
  return {pos:tg.clone().addScaledVector(dir,dist),tg};
}

// ---------------------------------------------------------------- one frame
placeChair(heroChair,-0.6,0,U);
function setT(t){
  const ag=agedK(t);
  for(const f of F){ if(f.best) continue; const s=friendAt(f,t);
    f.fig.setAlpha(s.alpha); if(s.alpha>0.004) R.poseFig(f.fig,R.skel(s.P,s.root,s.yaw));
    placeChair(f.chair,f.u,s.chairV,f.face);
    f.glass.position.copy(s.gp); if(f.id===1&&t>=TL.slideGrab) f.glass.visible=false; }
  const h=heroesAt(t);
  R.poseFig(hero,R.skel(h.P,HERO_ROOT,HERO_YAW)); R.poseFig(BF.fig,R.skel(h.Q,BF_ROOT,BF.yaw));
  placeChair(BF.chair,BF.u,0.8,BF.face); BF.glass.position.copy(h.bg);
  heroG.visible=!!h.heroGlass; if(h.heroGlass) heroG.position.copy(h.heroGlass);
  // candle
  const ch=candleH(t); candle.scale.set(1,ch,1); candle.position.copy(CANDLE_AT).add(V(0,0.012+ch/2,0));
  const tipY=CANDLE_AT.y+0.012+ch; wick.position.copy(CANDLE_AT).setY(tipY+0.008);
  const steady=sstep(TL.clink,TL.clink+0.8,t), fl=(1-steady)*(0.5+0.5*ag);
  const fk=1+fl*(0.22*Math.sin(t*23.1)+0.15*Math.sin(t*37.7+1)+0.1*Math.sin(t*61.3+2));
  const sway=fl*0.006*Math.sin(t*5.3);
  flame.position.copy(CANDLE_AT).setY(tipY+0.035).addScaledVector(RT,sway); flame.scale.set(0.07,0.13*fk,1);
  flameCore.position.copy(CANDLE_AT).setY(tipY+0.026).addScaledVector(RT,sway*0.6); flameCore.scale.set(0.025,0.055*fk,1);
  flame.material.opacity=0.75+0.1*steady; candleLight.position.copy(CANDLE_AT).setY(tipY+0.06); candleLight.intensity=(0.5+0.25*steady)*fk;
  const push=sstep(10,15,t); candleM.emissiveIntensity=lerp(0.05,0.2,push); candleHalo.material.opacity=lerp(0.025,0.12,push);
  candleHalo.position.copy(CANDLE_AT).setY(tipY-0.03); candleHalo.scale.setScalar(0.28);
  // lamp narrows onto the two; warms at the clink
  // the lamp closes in a step with every exit: the light shrinks with the table
  let gone=0; for(const d of DEP) gone+=sstep(d.td+0.1/d.sp,d.td+1.3/d.sp,t); const la=sm5(gone/29); aim(AIM0.clone().lerp(AIM1,la),lerp(CONE0,CONE1,la));
  const pay=0.16*sstep(TL.clink,TL.clink+0.9,t);
  // camera
  const c=camAt(t); S.cam.position.copy(c.pos); S.cam.lookAt(c.tg);
  S.tick(t,pay); S.beamU.uI.value*=lerp(0.42,1.0,la); S.moteU.uOp.value=lerp(0.7,1,la);
}
const heroG=makeGlass();

// ---------------------------------------------------------------- overlay / sound data
const v3=new THREE.Vector3();
window.metaAt=t=>{ setT(t); S.cam.updateMatrixWorld(); const labels=[];
  for(const d of DEP){ if(!d.label) continue; const tt=(t-d.td)*d.sp; if(tt<0.45||tt>1.75) continue;
    v3.copy(labelAt(d)).project(S.cam);
    labels.push({text:d.label,x:(v3.x*0.5+0.5)*1080,y:(0.5-v3.y*0.5)*1920,a:sstep(0.45,0.7,tt)*(1-sstep(1.35,1.75,tt))}); }
  return {age:Math.floor(ageAt(t)+1e-6),count:countAt(t),labels}; };
// reason labels: five exits spread through the years, each on a walker that stays in frame (checked through the real camera)
// the label is pinned over the spot where he stands up (it reads as the reason he is leaving), not dragged along the walk
const labelAt=d=>W2(F[d.id].u,F[d.id].s*1.0,1.98);
function onScreen(d){ let n=0, m=0; for(let tt=0.4;tt<=2.0;tt+=0.2){ const t=d.td+tt/d.sp; const c=camAt(t);
    S.cam.position.copy(c.pos); S.cam.lookAt(c.tg); S.cam.updateMatrixWorld(); const p=labelAt(d).project(S.cam);
    m++; if(Math.abs(p.x)<0.8&&p.y<0.55&&p.y>-0.4) n++; } return n/m; }
window.labelVis=()=>DEP.filter(d=>d.label).map(d=>[d.k,d.id,d.label,+onScreen(d).toFixed(2)]);
function depPan(d){ const f=F[d.id], c=camAt(d.td); S.cam.position.copy(c.pos); S.cam.lookAt(c.tg); S.cam.updateMatrixWorld(); return clamp(W2(f.u,f.s).project(S.cam).x,-1,1); }
window.events={deps:DEP.map(d=>({k:d.k,id:d.id,td:d.td,sp:d.sp,label:d.label,side:F[d.id].s,seat:F[d.id].i,pan:depPan(d)})),...TL};
window.renderAt=(t,K=3)=>S.renderAt(setT,t,K,{t0:0,t1:DUR});
window.ready=true;
