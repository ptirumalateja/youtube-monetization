
// ================================================================ PART 2: Check Your Friend's Bag
// Opens on Part 1's last frame (t1 = 17.9667 s). Everything above this line is Part 1's code, unchanged.
// t below is Part 2 video time (0..20 s). The friend's staircase is built beside the white one at z = BZ.
const P1=17.9667, DUR2=20.0;
const BZ=-1.85, IN=0.32;      // blue stair centre line; figures stand IN m in from the centre lines when handing across the gap
const FB=1.45;                // the friend's bag is Part 1's bag x 1.45: almost twice the white stickman's
const TL2={turn:[0.35,1.3],xray:3.4,collapse:[5.05,5.55],descend:[6.25,8.65],walk:[8.65,9.75],kneel:[9.75,10.25],tap:[10.35,10.95],
  point:[11.0,11.65],bagOff:[11.65,12.1],lift:[12.15,12.6],carry:[12.6,13.4],fetch:[13.5,13.9],load:[13.95,14.45],cyc2:14.45,
  place:[13.4,14.85,15.3,15.75,16.2,16.62,17.05],up:[17.05,17.45],bridge:18.3,bagDrop:18.45,bagLand:18.95};
// the descent: he hops from the top (rock 7) down to the ground, 7 hops; each white step flares as he lands on it
const DPATH=[TOPX,standX(6),standX(5),standX(4),standX(3),standX(2),standX(1),HX], DPY=[TOPY,standY(6),standY(5),standY(4),standY(3),standY(2),standY(1),0];
const hop=i=>TL2.descend[0]+(TL2.descend[1]-TL2.descend[0])*i/7;
TL2.flares=[TL2.descend[0]+0.05]; for(let i=1;i<7;i++) TL2.flares.push(+hop(i).toFixed(3));   // flare of step 7, 6, ..., 1
window.TL=TL2;

// ---------------------------------------------------------------- helpers
const angLerp=(a,b,u)=>{ let d=b-a; while(d>Math.PI) d-=2*Math.PI; while(d<-Math.PI) d+=2*Math.PI; return a+d*u; };
const kf=(K,t)=>{ if(t<=K[0][0]) return K[0][1]; for(let i=0;i<K.length-1;i++) if(t<=K[i+1][0]){ const u=ease((t-K[i][0])/(K[i+1][0]-K[i][0])); const a=K[i][1],b=K[i+1][1]; return a.map((v,j)=>lerp(v,b[j],u)); } return K[K.length-1][1]; };
const FACE_X=0, FACE_NZ=Math.PI/2, FACE_PZ=-Math.PI/2, FACE_NX=Math.PI;   // yaw that faces +x, -z, +z, -x
const sideOf=yaw=>rotY(V(0,0,1),yaw);
const hold2=(pos,yaw,half,w)=>({tL:pos.clone().addScaledVector(sideOf(yaw),half),tR:pos.clone().addScaledVector(sideOf(yaw),-half),wL:w,wR:w,pL:V(0,-0.6,1),pR:V(0,-0.6,-1)});

// ---------------------------------------------------------------- Part 1's final state (frozen)
const H1=heroAt(P1); const J1=skel(H1.P,H1.root,H1.yaw);
const WHITE=ROCKS.map((_,i)=>rockAt(i,P1));
const HB1=bagAt(P1);                                   // the empty bag on the ground
const CROWD1=CROWD.map(m=>crowdAt(m,P1,J1.head,H1.root));
const WX1=tab(WX_TAB,P1);

// ---------------------------------------------------------------- new things: the friend, his bag, his rocks
const friend=makeFig('#5872ad','#121d3c',0.04);
const fbU={uVis:{value:0},uX:{value:0},uFill:{value:1}};
friend.mat.transparent=true; const FIN=t=>sstep(0.2,0.9,t);
const fOuter=bagOuter.clone(), fInner=bagInner.clone(); fOuter.uniforms=fbU; fInner.uniforms=fbU;
const fbag=new THREE.Group(); fbag.matrixAutoUpdate=false; scene.add(fbag);
for(const ch of bag.children){ const m=new THREE.Mesh(ch.geometry,ch.material===bagOuter?fOuter:fInner); m.position.copy(ch.position); m.rotation.copy(ch.rotation); m.renderOrder=ch.renderOrder; m.frustumCulled=false; fbag.add(m); }
const fbGlow=glow(0xffa050,1.4,0);
// crack texture in white so the emissive colour sets the hue: dim rust ("pain") -> calm blue once it is a step
function crackW(seed){ const c=document.createElement('canvas'); c.width=512; c.height=256; const g=c.getContext('2d'); const Rn=rng(seed); g.fillStyle='#060606'; g.fillRect(0,0,512,256);
  const paths=[]; for(let k=0;k<11;k++){ let x=Rn()*512,y=Rn()*256,a=Rn()*6.28; const p=[[x,y]]; const n=6+Math.floor(Rn()*10); for(let i=0;i<n;i++){ a+=(Rn()-0.5)*1.4; const l=10+Rn()*26; x+=Math.cos(a)*l; y+=Math.sin(a)*l*0.6; p.push([x,y]); } paths.push(p); }
  for(const [w,col,b] of [[7,'rgba(255,255,255,0.3)',14],[3,'rgba(255,255,255,0.85)',6],[1.2,'rgba(255,255,255,1)',2]]){ g.strokeStyle=col; g.lineWidth=w; g.shadowColor=col; g.shadowBlur=b;
    for(const p of paths){ g.beginPath(); p.forEach(([x,y],i)=>i?g.lineTo(x,y):g.moveTo(x,y)); g.stroke(); } }
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; t.wrapS=THREE.RepeatWrapping; return t; }
const PAIN=new THREE.Color(0xc0602e), CALM=new THREE.Color(0x58a8ff), WARM=new THREE.Color(0xffa24a);
const FR=['ALONE','NO ONE CARES','TIRED','EVERYONE AHEAD','NOT GOOD ENOUGH',"WHAT'S THE POINT","I CAN'T",'TOO LATE'];
const XRL=[1,0,7,2,3];        // labels shown in the X-ray (top to bottom): NO ONE CARES / ALONE / TOO LATE / TIRED / EVERYONE AHEAD
const SLOT2=[[0.0,0.36,0.0],[-0.2,0.15,0.04],[0.2,0.14,-0.03],[-0.19,-0.08,-0.02],[0.2,-0.1,0.03],[-0.18,-0.31,0.02],[0.19,-0.32,-0.02],[0.01,-0.02,0.0]];
const FROCK=[]; { const Rn=rng(2024);
  for(let i=0;i<FR.length;i++){ const bridge=i===7; const mat=new THREE.MeshStandardMaterial({color:0x5a4e46,roughness:0.92,map:ROCK_COL,flatShading:true,emissive:PAIN.clone(),emissiveMap:crackW(300+i*29),emissiveIntensity:0.6});
    const m=new THREE.Mesh(rockGeo(1500+i*61),mat); m.castShadow=true; m.receiveShadow=true; m.matrixAutoUpdate=false; m.frustumCulled=false; scene.add(m);
    FROCK.push({txt:FR[i],m,mat,bridge,slot:V(...SLOT2[i]).multiplyScalar(FB),sb:V(0.36+Rn()*0.04,0.2+Rn()*0.03,0.3+Rn()*0.04),
      ss:bridge?V(0.5,0.17,Math.abs(BZ)+0.5):V(1.16+Rn()*0.06,0.47+Rn()*0.02,0.9+Rn()*0.08),yawB:(Rn()-0.5)*0.7,yawS:(Rn()-0.5)*0.16,zS:(Rn()-0.5)*0.06}); } }
const FILL=[]; { const Rn=rng(77); for(let i=0;i<7;i++){ const mat=new THREE.MeshStandardMaterial({color:0x5a4e46,roughness:0.92,map:ROCK_COL,flatShading:true,emissive:PAIN.clone(),emissiveMap:crackW(700+i*13),emissiveIntensity:0.5});
  const m=new THREE.Mesh(rockGeo(2100+i*31),mat); m.matrixAutoUpdate=false; m.frustumCulled=false; m.castShadow=true; scene.add(m);
  FILL.push({m,mat,slot:V((Rn()-0.5)*0.5,i<3?0.5+Rn()*0.08:(Rn()-0.5)*0.7,(Rn()-0.5)*0.3).multiplyScalar(FB),s:V(0.2+Rn()*0.08,0.13+Rn()*0.04,0.18+Rn()*0.06),yaw:Rn()*6}); } }
const coolLight=new THREE.PointLight(0x6fb2ff,0,4,2); scene.add(coolLight);

// ---------------------------------------------------------------- poses (Part 1's rig and pose keys)
const BENT={...POSES.heavy,p:0.95,tilt:-0.05,kL:0.4,kR:0.4,aL:0.2,aR:0.18,sL:0.55,sR:0.5,eL:1.45,eR:1.4};
const KNEES={...P0,p:0.85,tilt:0.15,aL:0.16,aR:0.1,kL:1.72,kR:1.68,sL:0.2,sR:0.12,eL:0.25,eR:0.3,dy:-0.03};
const KNEELUP={...KNEES,p:0.28,tilt:-0.3};
const KNEEL1={...P0,p:0.22,tilt:0.15,aL:0.02,aR:1.4,kL:1.57,kR:1.5,sL:0.15,sR:0.1,eL:0.3,eR:0.3,dy:-0.07};
const POINT={...KNEEL1,p:0.1,tilt:-0.3,sR:2.1,eR:0.05,sL:0.25,eL:0.4};
const LOOKDOWN={...POSES.tall,p:0.18,tilt:0.62};
const HAND={...POSES.stand,p:0.18,tilt:0.12};
const PLACE2={...POSES.place,p:0.85};
const stepUp=(P,v)=>{ const b=Math.sin(Math.PI*v); return {...P,p:P.p+0.3*b,aL:P.aL+0.9*b,kL:P.kL+1.2*b}; };

// ---------------------------------------------------------------- the friend
const F0=V(-3.45,0,-1.4), F1=V(-0.3,0,BZ);
function friendAt(t){
  const [c0,c1]=TL2.collapse; let root, yaw=FACE_X, P, bagOn=1, shake=0;
  if(t<c1){ // barely walking: each heavy step stalls
    const st=t*0.95; const prog=clamp((Math.floor(st)+sstep(0.2,1,st%1))/(c0*0.95)); root=F0.clone().lerp(F1,prog); yaw=yawTo(F0,F1);
    let B={...BENT,p:BENT.p+0.05*Math.sin(t*2.2)+0.1*sstep(3.6,c0,t)}; B=gait(B,st*Math.PI,0.55,0.22,0.4,0.06);
    P=blend(B,KNEES,ease(clamp((t-c0)/(c1-c0)))); shake=sstep(3.7,4.1,t)*(1-sstep(5.4,5.9,t)); yaw=angLerp(yaw,FACE_X,sstep(c0,c1,t));
    return {P,root,yaw,bagOn,shake}; }
  root=F1.clone();
  if(t<TL2.tap[0]) return {P:{...KNEES,p:KNEES.p+0.02*Math.sin(t*2.6)},root,yaw,bagOn};
  if(t<TL2.bagOff[0]){ const u=sstep(TL2.tap[0]+0.25,TL2.point[1],t); P=blend(KNEES,KNEELUP,u); yaw=angLerp(FACE_X,FACE_PZ*0.4,sstep(TL2.tap[0],TL2.tap[1],t)*(1-sstep(TL2.point[0],TL2.point[1],t)));
    return {P:{...P,hy:-0.4*sstep(TL2.tap[0],TL2.tap[1],t)*(1-sstep(TL2.point[0],TL2.point[0]+0.3,t))},root,yaw,bagOn}; }
  if(t<TL2.carry[0]){ bagOn=1-sstep(TL2.bagOff[0],TL2.bagOff[1],t);
    P=blend(KNEELUP,{...KNEELUP,p:0.8,tilt:-0.25,sL:1.0,sR:1.0,eL:0.3,eR:0.3},sstep(TL2.bagOff[0],TL2.lift[0],t)); yaw=angLerp(FACE_X,FACE_NZ*0.0-0.6,sstep(TL2.bagOff[1],TL2.lift[0],t)*(1-sstep(TL2.lift[1],TL2.carry[0],t)));
    return {P,root,yaw,bagOn:bagOn}; }
  if(t<TL2.place[0]){ const u=(t-TL2.carry[0])/(TL2.place[0]-TL2.carry[0]); root=F1.clone().lerp(V(0.05,0,BZ+0.05),sstep(0.25,0.7,u));
    P=u<0.4?blend(KNEELUP,POSES.carry,ease(u/0.4)):blend(POSES.carry,PLACE2,ease((u-0.4)/0.6)); if(u>0.25&&u<0.7) P=gait(P,(u-0.25)*14,0.5,0.25,0.4,0.0);
    return {P,root,yaw,bagOn:0}; }
  return buildAt(t,'friend');
}
// ---------------------------------------------------------------- the white stickman
function heroAt2(t){
  let root=V(TOPX,TOPY,0), yaw=0, P, bagOn=0;
  const breath=0.008*Math.sin(2*Math.PI*0.25*(t+P1));
  if(t<TL2.descend[0]){ const fr=friendAt(t).root; const look=yawTo(root,fr); const u=sstep(TL2.turn[0],TL2.turn[1],t);
    yaw=angLerp(0,look,u); P=blend({...POSES.tall,p:POSES.tall.p+breath},LOOKDOWN,u);
    if(t>5.7) yaw=angLerp(yaw,FACE_NX,sstep(5.7,6.25,t));
    const dn=Math.atan2(J1.head.y-0.8,Math.hypot(fr.x-root.x,fr.z-root.z)); P={...P,tilt:lerp(P.tilt,0.25+0.9*dn,u)};
    return {P,root,yaw,bagOn}; }
  if(t<TL2.descend[1]){ const s=(t-TL2.descend[0])/(TL2.descend[1]-TL2.descend[0])*7; const i=Math.min(6,Math.floor(s)), v=s-i;
    const x=lerp(DPATH[i],DPATH[i+1],ease(v)), y=lerp(DPY[i],DPY[i+1],sstep(0.25,0.85,v))+0.1*Math.sin(Math.PI*v);
    root=V(x,y,0); yaw=FACE_NX; P={...POSES.stand,p:0.12,tilt:0.3,aR:-0.05+0.8*Math.sin(Math.PI*v),kR:0.05+1.0*Math.sin(Math.PI*v),sL:0.12+0.3*Math.sin(Math.PI*v),sR:-0.05-0.3*Math.sin(Math.PI*v)};
    return {P,root,yaw,bagOn}; }
  const K0=V(-0.35,0,BZ+0.85);   // he kneels at his friend's side (the +z side), facing him
  if(t<TL2.kneel[0]){ const u=ease((t-TL2.walk[0])/(TL2.walk[1]-TL2.walk[0])); root=V(HX,0,0).lerp(K0,u); yaw=angLerp(FACE_NX,FACE_NZ,sstep(0.2,0.8,u));
    P=gait({...POSES.stand,p:0.14},(t-TL2.walk[0])*9,Math.sin(Math.PI*u),0.32,0.5,0.25); return {P,root,yaw,bagOn}; }
  root=K0.clone(); yaw=FACE_NZ;
  if(t<TL2.tap[0]) return {P:blend(POSES.stand,KNEEL1,ease(clamp((t-TL2.kneel[0])/(TL2.kneel[1]-TL2.kneel[0])))),root,yaw,bagOn};
  if(t<TL2.point[0]){ // two light taps on his shoulder (left hand to the friend's near shoulder)
    const F=friendAt(t), Jf=skel(F.P,F.root,F.yaw); const tap=0.05*Math.max(0,Math.sin((t-TL2.tap[0]-0.25)*22))*sstep(TL2.tap[0]+0.2,TL2.tap[0]+0.3,t);
    const w=sstep(TL2.tap[0],TL2.tap[0]+0.25,t)*(1-sstep(TL2.tap[1]-0.1,TL2.tap[1]+0.05,t));
    return {P:{...KNEEL1,tL:Jf.shL.clone().add(V(0,0.05+tap,0.03)),wL:w,pL:V(0,-1,0.3),hy:-0.2},root,yaw,bagOn}; }
  if(t<TL2.bagOff[0]+0.2){ const u=sstep(TL2.point[0],TL2.point[0]+0.35,t); return {P:blend(KNEEL1,POINT,u),root,yaw:angLerp(FACE_NZ,0.25,u),bagOn}; }
  if(t<TL2.carry[0]) return {P:blend(POINT,KNEEL1,sstep(TL2.bagOff[0]+0.2,TL2.bagOff[1]+0.1,t)),root,yaw:angLerp(0.25,FACE_NZ,sstep(TL2.bagOff[0]+0.2,TL2.lift[0],t)),bagOn};
  if(t<TL2.place[0]){ const u=(t-TL2.carry[0])/(TL2.place[0]-TL2.carry[0]); root=K0.clone().lerp(V(0.1,0,BZ+0.62),sstep(0.25,0.7,u)); yaw=angLerp(FACE_NZ,FACE_X,sstep(0.15,0.55,u));
    let P=u<0.4?blend(KNEEL1,POSES.carry,ease(u/0.4)):blend(POSES.carry,PLACE2,ease((u-0.4)/0.6)); if(u>0.25&&u<0.7) P=gait(P,(u-0.25)*14,0.5,0.25,0.4,0.0);
    return {P,root,yaw,bagOn}; }
  return buildAt(t,'hero');
}
// ---------------------------------------------------------------- building together (time-lapse) and the top
function cycOf(t){ const PL=TL2.place; for(let k=2;k<=7;k++){ if(t<PL[k-1]){ const a=k===2?TL2.cyc2:PL[k-2]; return {k,u:clamp((t-a)/(PL[k-1]-a))}; } } return {k:8,u:0}; }
function buildAt(t,who){
  const isH=who==='hero'; const z=isH?-IN:BZ+IN; let root, yaw, P, bagOn=isH?1:0;
  // 13.4-14.45: after step 1 the friend steps onto it; the white stickman fetches his own empty bag and comes to white step 1
  if(t<TL2.cyc2){
    if(!isH){ const v=sstep(13.7,14.2,t); root=V(lerp(0.05,standX(1),v),standY(1)*sstep(13.85,14.2,t)+0.1*Math.sin(Math.PI*v),lerp(BZ+0.05,z,v)); yaw=FACE_X;
      P=blend(PLACE2,POSES.stand,sstep(13.4,13.7,t)); if(v>0&&v<1) P=stepUp(P,v); return {P,root,yaw,bagOn}; }
    const bagP=V(HB1.p.x+0.45,0,HB1.p.z+0.15), start=V(0.1,0,BZ+0.62), end=V(standX(1),standY(1),z);
    if(t<TL2.fetch[1]){ const u=sstep(TL2.fetch[0],TL2.fetch[1],t); root=start.clone().lerp(bagP,u); yaw=yawTo(start,bagP); P=gait(blend(PLACE2,POSES.stand,sstep(13.4,13.55,t)),t*11,Math.sin(Math.PI*u),0.32,0.5,0.25);
      if(t>TL2.fetch[1]-0.15) P=blend(P,POSES.crouch,sstep(TL2.fetch[1]-0.15,TL2.fetch[1],t)); bagOn=0; return {P,root,yaw,bagOn}; }
    const u=sstep(TL2.fetch[1]+0.12,TL2.cyc2-0.02,t); root=bagP.clone().lerp(end,u); root.y=end.y*sstep(0.6,1,u)+0.1*Math.sin(Math.PI*sstep(0.6,1,u)); yaw=angLerp(yawTo(bagP,end),FACE_X,sstep(0.7,1,u));
    P=blend(POSES.crouch,POSES.stand,sstep(TL2.fetch[1],TL2.fetch[1]+0.15,t)); P=gait(P,t*11,Math.sin(Math.PI*u),0.32,0.5,0.25);
    bagOn=sstep(TL2.fetch[1],TL2.fetch[1]+0.12,t); return {P,root,yaw,bagOn}; }
  const c=cycOf(t);
  if(c.k<=7){ const s=c.k-1, u=c.u;
    root=V(standX(s),standY(s),z);
    if(u>0.8){ const v=ease((u-0.8)/0.2); root=V(lerp(standX(s),standX(s+1),v),lerp(standY(s),standY(s+1),sstep(0.15,0.8,v))+0.08*Math.sin(Math.PI*v),z); }
    if(isH){ yaw=angLerp(FACE_NZ,FACE_X,sstep(0.3,0.48,u)); P=u<0.3?blend(POSES.carry,HAND,sstep(0.0,0.12,u)):blend(HAND,POSES.stand,sstep(0.3,0.48,u)); }
    else { yaw=u<0.3?angLerp(FACE_X,FACE_PZ,sstep(0.0,0.1,u)):angLerp(FACE_PZ,FACE_X,sstep(0.3,0.5,u));
      P=u<0.3?blend(POSES.stand,HAND,sstep(0.05,0.2,u)):u<0.55?blend(HAND,POSES.carry,sstep(0.3,0.5,u)):u<0.8?blend(POSES.carry,PLACE2,ease((u-0.55)/0.25)):blend(PLACE2,POSES.stand,ease((u-0.8)/0.2)); }
    if(u>0.8) P=stepUp(P,(u-0.8)/0.2);
    return {P,root,yaw,bagOn}; }
  // both step up onto their top steps, lay the bridge, then stand tall and look forward
  const [u0,u1]=TL2.up; const v=sstep(u0,u1,t); root=V(lerp(standX(6),standX(7),ease(v)),lerp(standY(6),TOPY,sstep(0.15,0.8,v))+0.08*Math.sin(Math.PI*v),z);
  yaw=FACE_X; P=v<1?stepUp(POSES.stand,v):POSES.stand;
  const b=TL2.bridge, across=isH?FACE_NZ:FACE_PZ; const w=sstep(b-0.75,b-0.45,t)*(1-sstep(b+0.15,b+0.5,t));
  if(w>0){ yaw=angLerp(FACE_X,across,w); P=blend(P,{...PLACE2,p:0.9,kL:1.1,kR:0.6},w); }
  if(isH) bagOn=1-sstep(b+0.05,TL2.bagDrop,t);
  if(t>b+0.35) P=blend(P,{...POSES.tall,p:-0.03+0.006*Math.sin(t*1.6)},sstep(b+0.35,b+0.85,t));
  return {P,root,yaw,bagOn}; }

// ---------------------------------------------------------------- bags
function onBack(J,sc){ const u=J.up.clone(), back=J.fwd.clone().addScaledVector(u,-J.fwd.dot(u)).normalize().negate();
  const zA=back.clone().negate(), xA=u.clone().cross(zA).normalize(); const m=new THREE.Matrix4().makeBasis(xA,u,zA);
  const c=J.hip.clone().add(J.neck).multiplyScalar(0.5).addScaledVector(u,0.1*sc+0.12*(sc-1)).addScaledVector(back,BAG_D*sc*0.5+0.055);
  return {p:c,q:new THREE.Quaternion().setFromRotationMatrix(m)}; }
const FBG=V(-0.95,BAG_H*FB*0.5+0.002,BZ-0.7);                                     // where he sets his bag down
const fbGroundQ=new THREE.Quaternion().setFromEuler(new THREE.Euler(0,0.5,0));
function fbagAt(t,Jf,F){ // {p,q,sy}
  const empty=sstep(TL2.load[0],TL2.load[1],t); const sy=1-0.32*empty;
  const g={p:V(FBG.x,BAG_H*FB*0.5*sy+0.002,FBG.z),q:new THREE.Quaternion().setFromEuler(new THREE.Euler(-0.08*empty,0.5,0.05*empty)),sy};
  if(F.bagOn>=1){ const b=onBack(Jf,FB); if(F.shake){ b.p.x+=0.02*F.shake*Math.sin(t*53); b.p.y+=0.015*F.shake*Math.sin(t*71+1); b.q.multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(0.04*F.shake*Math.sin(t*37),0,0.05*F.shake*Math.sin(t*43)))); } return {...b,sy:1+0.02*Math.sin(t*3.0)}; }
  if(F.bagOn<=0) return g;
  const b=onBack(Jf,FB); const u=ease(1-F.bagOn); return {p:b.p.clone().lerp(g.p,u),q:b.q.clone().slerp(g.q,u),sy:1}; }
const HBTOP=V(TOPX+0.35,TOPY+0.45,0.45), HBLAND=V(TOPX+0.75,BAG_H*0.35,1.05);
function hbagAt(t,Jh,Hs){
  if(t<TL2.fetch[1]) return HB1;
  if(t<TL2.bagDrop && Hs.bagOn>0){ const b=onBack(Jh,1); if(Hs.bagOn>=1) return {...b,sy:1};
    if(t<TL2.cyc2) return {p:V(HB1.p.x,HB1.p.y,HB1.p.z).lerp(b.p,ease(Hs.bagOn)),q:HB1.q.clone().slerp(b.q,ease(Hs.bagOn)),sy:lerp(HB1.sy,1,Hs.bagOn)};
    return {p:b.p.clone().lerp(HBTOP,1-Hs.bagOn),q:b.q,sy:1}; }
  const a=clamp((t-TL2.bagDrop)/(TL2.bagLand-TL2.bagDrop)); const p=HBTOP.clone().lerp(HBLAND,a); p.y=lerp(HBTOP.y,HBLAND.y,a*a);
  const q=new THREE.Quaternion().setFromEuler(new THREE.Euler(0.15*a,1.2*a,-0.5*a*(1-a)+0.06*a)); return {p,q,sy:lerp(1,0.7,sstep(0.9,1,a))}; }
const inB=(B,v,sc=1)=>v.clone().multiplyScalar(sc).multiply(V(1,B.sy,1)).applyQuaternion(B.q).add(B.p);

// ---------------------------------------------------------------- the friend's rocks over time
const destOf=i=>{ const R_=FROCK[i]; if(R_.bridge) return {pos:V(standX(7)+0.12,TOPY+R_.ss.y*0.5-0.01,BZ*0.5),q:new THREE.Quaternion().setFromEuler(new THREE.Euler(0,0.04,0.02))};
  const k=i+1; return {pos:V(SX+k*T,(k-1)*R+R_.ss.y*0.5-0.012,BZ+R_.zS),q:new THREE.Quaternion().setFromEuler(new THREE.Euler(0,R_.yawS,0))}; };
const placeT=i=>FROCK[i].bridge?TL2.bridge:TL2.place[i];
function frockAt(i,t,ctx){ // ctx: {FB_, HB_, Jf, Jh}
  const Rk=FROCK[i], tp=placeT(i), d=destOf(i);
  const qB=ctx.FB_.q.clone().multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(0,Rk.yawB,0)));
  const inF={pos:inB(ctx.FB_,Rk.slot),q:qB,size:Rk.sb.clone()};
  const hands=J=>J.hL.clone().add(J.hR).multiplyScalar(0.5);
  const yq=y=>new THREE.Quaternion().setFromEuler(new THREE.Euler(0,y,0));
  if(t>=tp){ const u=clamp((t-tp)/0.2); const e=1+0.08*Math.sin(Math.PI*u)*(1-u); const size=Rk.sb.clone().lerp(Rk.ss,sstep(0,1,u)).multiplyScalar(e);
    const pos=d.pos.clone(); if(!Rk.bridge) pos.y=i*R+size.y*0.5-0.012; return {pos,q:d.q,size,state:2,age:t-tp}; }
  if(i===0){ // ALONE: he lifts it out of his own bag, they carry it together and set it as step 1
    if(t<TL2.lift[0]) return {...inF,state:0};
    const hf=hands(ctx.Jf);
    if(t<TL2.carry[0]){ const u=sstep(TL2.lift[0],TL2.lift[1],t); const top=inF.pos.clone().add(V(0,0.5,0)); return {pos:inF.pos.clone().lerp(top,sstep(0,0.5,u)).lerp(hf,sstep(0.4,1,u)),q:qB.slerp(yq(ctx.Ff.yaw),u),size:Rk.sb.clone(),state:1}; }
    const mid=hf.clone().lerp(hands(ctx.Jh),0.4); const u=(t-TL2.carry[0])/(tp-TL2.carry[0]);
    const land=V(d.pos.x-0.05,Rk.sb.y*0.5,d.pos.z); const p=u<0.75?mid:mid.clone().lerp(land,sstep(0.75,1,u)); return {pos:p,q:yq(0).slerp(d.q,sstep(0.75,1,u)),size:Rk.sb.clone(),state:1}; }
  // all the others first fly into the white stickman's bag at the load
  const L0=TL2.load[0]+0.045*i, L1=L0+0.3;
  if(t<L0) return {...inF,state:0};
  const hb=inB(ctx.HB_,V(0,0.1,0));
  if(t<L1){ const u=ease((t-L0)/(L1-L0)); const p=inF.pos.clone().lerp(hb,u); p.y+=0.7*Math.sin(Math.PI*u); return {pos:p,q:qB,size:Rk.sb.clone().multiplyScalar(1-0.5*u),state:1,hide:sstep(0.75,1,u)}; }
  if(Rk.bridge){ // TOO LATE: the last one out of his bag, at the top
    const b=TL2.bridge, a0=b-0.9; if(t<a0) return {pos:hb,q:qB,size:Rk.sb.clone().multiplyScalar(0.5),state:1,hide:1};
    const hh=hands(ctx.Jh), hf=hands(ctx.Jf); const out=sstep(a0,a0+0.3,t); const mid=hh.clone().lerp(hf,0.5*sstep(b-0.6,b-0.35,t));
    const p=hb.clone().lerp(mid,out).lerp(d.pos.clone().add(V(0,0.04,0)),sstep(b-0.35,b,t)); const g=sstep(b-0.5,b,t);
    return {pos:p,q:yq(FACE_NZ*0).slerp(d.q,g),size:Rk.sb.clone().multiplyScalar(lerp(0.5,1,out)).lerp(Rk.ss,g),state:1,hide:1-out}; }
  const c=cycOf(t), k=i+1;
  if(c.k<k) return {pos:hb,q:qB,size:Rk.sb.clone().multiplyScalar(0.5),state:1,hide:1};
  const u=c.u, hh=hands(ctx.Jh), hf=hands(ctx.Jf); let p;
  if(u<0.12) p=hb.clone().lerp(hh,ease(u/0.12)); else if(u<0.3) p=hh.clone().lerp(hf,ease((u-0.12)/0.18)); else if(u<0.62) p=hf; else p=hf.clone().lerp(V(d.pos.x-0.05,i*R+Rk.sb.y*0.5,d.pos.z),sstep(0.62,0.8,u));
  return {pos:p,q:yq(ctx.Ff.yaw).slerp(d.q,sstep(0.55,0.8,u)),size:Rk.sb.clone().multiplyScalar(lerp(0.5,1,sstep(0,0.12,u))),state:1,hide:1-sstep(0,0.08,u)}; }

// ---------------------------------------------------------------- camera
const CK2=[ // t, [pos, look, fov]
  [0.0, [8.6,0.32,6.65, 2.45,2.55,-0.7, 60]],
  [0.35,[8.6,0.32,6.65, 2.45,2.55,-0.7, 60]],
  [1.5, [6.05,5.75,1.3, -2.3,0.55,-1.45, 50]],   // high angle over his shoulder, looking back down at the friend
  [3.0, [5.7,5.5,1.15, -2.0,0.6,-1.5, 46]],
  [3.5, [2.3,2.15,1.75, -1.35,1.35,-1.65, 54]],  // fast drop to the friend (X-ray)
  [5.95,[1.9,1.75,1.35, -0.75,1.0,-1.8, 54]],
];
function heroTrack(t){ let x=0,y=0,n=0; for(let d=-0.3;d<=0.3001;d+=0.05){ const h=heroAt2(clamp(t+d,0,DUR2)); x+=h.root.x; y+=h.root.y; n++; } return V(x/n,y/n,0); }
function trackCam(t){ const h=heroTrack(t); const u=sstep(6.4,9.75,t); return {p:V(h.x-1.0-0.3*u,h.y+1.35-0.2*u,5.0-0.6*u),l:V(h.x-0.55,h.y+0.85,-0.6-0.3*u),fov:48}; }
function twoShot(t){ const u=sstep(CUT2,13.5,t); return {p:V(lerp(4.55,4.7,u),lerp(1.45,1.55,u),-1.0),l:V(lerp(-0.4,-0.1,u),lerp(0.75,0.7,u),lerp(-1.45,-1.4,u)),fov:50}; }
const WK2=[
  [13.5,[4.7,1.55,-1.0, -0.1,0.7,-1.4, 50]],
  [14.35,[-4.4,4.3,6.1, 2.3,1.55,-0.95, 50]],   // wide time-lapse, both staircases side by side
  [17.6,[-4.7,4.8,6.5, 2.6,2.15,-0.95, 50]],
  [18.6,[-6.4,1.7,8.9, 2.4,2.35,-1.0, 54]],     // hero wide: low, wider than Part 1's last frame, the afterglow behind them
  [20.0,[-7.0,1.3,9.6, 2.4,2.45,-1.0, 55]],
];
const CUT2=9.9;
const kc=(K,t)=>{ const v=kf(K,t); return {p:V(v[0],v[1],v[2]),l:V(v[3],v[4],v[5]),fov:v[6]}; };
const mixCam=(a,b,u)=>({p:a.p.clone().lerp(b.p,u),l:a.l.clone().lerp(b.l,u),fov:lerp(a.fov,b.fov,u)});
function camAt2(t){
  if(t<=6.0) return kc(CK2,t);
  if(t<6.45) return mixCam(kc(CK2,5.95),trackCam(6.45),ease((t-6.0)/0.45));
  if(t<CUT2) return trackCam(t);                                    // hard cut to the two-shot (a move would pass through the stair)
  if(t<13.5) return twoShot(t);
  return kc(WK2,t); }

// ---------------------------------------------------------------- dust puffs for Part 2 (Part 1's list is cleared)
PUFFS.length=0;
TL2.place.forEach((p,i)=>PUFFS.push({t0:p+0.02,p:V(SX+(i+1)*T,i*R+0.03,BZ),size:0.5,n:9,spread:0.55}));
PUFFS.push({t0:TL2.bridge,p:V(standX(7)+0.1,TOPY+0.05,BZ*0.5),size:0.45,n:10,spread:0.6});
PUFFS.push({t0:TL2.collapse[1]-0.05,p:F1.clone().add(V(0,0.03,0)),size:0.55,n:12,spread:0.5});
PUFFS.push({t0:TL2.bagOff[1],p:FBG.clone().setY(0.03),size:0.5,n:10,spread:0.5});
PUFFS.push({t0:TL2.bagLand,p:HBLAND.clone().setY(0.03),size:0.55,n:12,spread:0.6});
for(let i=1;i<=7;i++) PUFFS.push({t0:hop(i)-0.02,p:V(DPATH[i]+0.1,DPY[i]+0.03,0),size:0.28,n:4,spread:0.2});

// ---------------------------------------------------------------- one sub-frame
const _M2=new THREE.Matrix4();
const WIND2=t=>lerp(1.12,0.1,sstep(0.0,0.35,t))+0.25*sstep(18.0,19.5,t);   // Part 1's wind stops on frame 0
const WX2=[]; for(let i=0;i<=DUR2*100;i++) WX2.push(WX1+integ(WIND2,i/100));
const tab2=t=>{ const x=clamp(t,0,DUR2)*100, i=Math.min(WX2.length-2,Math.floor(x)); return lerp(WX2[i],WX2[i+1],x-i); };
const XRAY=t=>{ const d=t-TL2.xray; return d<0?0:1-sstep(0.45,0.95,d); };
let LAST={};
function setT2(t){
  const Hs=heroAt2(t), Jh=skel(Hs.P,Hs.root,Hs.yaw);
  const Fs=friendAt(t); const Jf=skel(Fs.P,Fs.root,Fs.yaw);
  const HB_=hbagAt(t,Jh,Hs), FB_=fbagAt(t,Jf,Fs); const ctx={FB_,HB_,Jf,Jh,Ff:Fs};
  // hands on the rocks they carry (IK)
  let Ph=Hs.P, Pf=Fs.P; const R0=frockAt(0,t,ctx);
  if(t>TL2.lift[0]+0.15&&t<TL2.place[0]+0.05){ const w=sstep(TL2.lift[0]+0.15,TL2.lift[1],t)*(1-sstep(TL2.place[0],TL2.place[0]+0.05,t)); Pf={...Pf,...hold2(R0.pos,Fs.yaw,R0.size.z*0.5+0.02,w)};
    const wh=sstep(TL2.carry[0],TL2.carry[0]+0.25,t)*(1-sstep(TL2.place[0],TL2.place[0]+0.05,t)); Ph={...Ph,tR:R0.pos.clone().add(V(0.05,0.04,0.16)),wR:wh,pR:V(0,-1,0.3)}; }
  const c=cycOf(t);
  if(c.k<=7&&t>=TL2.cyc2){ const r=frockAt(c.k-1,t,ctx); const u=c.u;
    const wh=sstep(0.02,0.12,u)*(1-sstep(0.28,0.34,u)), wf=sstep(0.15,0.3,u)*(1-sstep(0.78,0.82,u));
    if(wh>0) Ph={...Ph,...hold2(r.pos,FACE_NZ,0.17,wh)}; if(wf>0) Pf={...Pf,...hold2(r.pos,u<0.4?FACE_PZ:Fs.yaw,0.17,wf)}; }
  const rb=frockAt(7,t,ctx); const b=TL2.bridge;
  if(t>b-0.95&&t<b+0.1){ const w=sstep(b-0.95,b-0.75,t)*(1-sstep(b,b+0.1,t)); const ax=V(0,0,1);
    Ph={...Ph,tL:rb.pos.clone().addScaledVector(ax,rb.size.z*0.35).add(V(0.12,0.05,0)),tR:rb.pos.clone().addScaledVector(ax,rb.size.z*0.35).add(V(-0.12,0.05,0)),wL:w,wR:w,pL:V(0,-1,0.5),pR:V(0,-1,0.5)};
    const wf=sstep(b-0.6,b-0.4,t)*(1-sstep(b,b+0.1,t)); Pf={...Pf,tL:rb.pos.clone().addScaledVector(ax,-rb.size.z*0.35).add(V(-0.12,0.05,0)),tR:rb.pos.clone().addScaledVector(ax,-rb.size.z*0.35).add(V(0.12,0.05,0)),wL:wf,wR:wf,pL:V(0,-1,-0.5),pR:V(0,-1,-0.5)}; }
  const JH=skel(Ph,Hs.root,Hs.yaw), JF=skel(Pf,Fs.root,Fs.yaw); poseFig(hero,JH); poseFig(friend,JF);
  // crowd: still where Part 1 left them, looking up at the top of the stairs
  const tgt=t<6.2?JH.head:(t<16.5?V(TOPX,TOPY+1.6,0):V(TOPX,TOPY+1.6,BZ*0.5));
  CROWD.forEach((m,i)=>{ const c1=CROWD1[i]; const up=Math.atan2(tgt.y-1.45,Math.hypot(tgt.x-c1.root.x,tgt.z-c1.root.z)); const face=yawTo(c1.root,tgt);
    const P={...POSES.stand,p:0.04,tilt:-clamp(up,0,1)*0.9+0.02*Math.sin(t*0.9+i),hy:0}; const yaw=angLerp(c1.yaw,face,sstep(0,1.2,t)); const Jc=skel(P,c1.root,yaw); poseFig(m.f,Jc); m.J=Jc; });
  // white staircase: Part 1's final rocks; each flares as he lands on it on the way down
  const X=XRAY(t);
  for(let i=0;i<NR;i++){ const Rk=ROCKS[i], r=WHITE[i]; _M2.compose(r.pos,r.q,r.size); Rk.m.matrix.copy(_M2); Rk.m.matrixWorld.copy(_M2); Rk.m.visible=true;
    const fl=TL2.flares[6-i]; const a=t-fl; const pulse=a>=0?Math.exp(-a/0.35):0; const lit=a>=0?0.12:0;
    const e=(0.7+lit+1.6*pulse+0.15*sstep(17.5,18.6,t))*(1+0.3*X); Rk.mat.emissiveIntensity=e;
    Rk.gl.position.copy(r.pos); Rk.gl.material.opacity=(0.18+0.45*pulse)*Math.min(1,e); Rk.gl.scale.setScalar(1.3); Rk.pl.position.copy(r.pos).add(V(0.15,0.05,0.75)); Rk.pl.intensity=0.35+1.0*pulse; }
  // the friend's rocks: dim rust ("pain") in the bag, calm blue once they are steps
  const vis=lerp(0.28,1,sstep(TL2.xray,TL2.xray+0.05,t))*FIN(t); friend.mat.opacity=FIN(t); friend.mat.depthWrite=FIN(t)>0.99; let blueTop=0;
  for(let i=0;i<FROCK.length;i++){ const Rk=FROCK[i], r=frockAt(i,t,ctx); const hid=(r.state===0&&t<TL2.xray)||(r.hide||0)>0.98;
    _M2.compose(r.pos,r.q,r.size); Rk.m.matrix.copy(_M2); Rk.m.matrixWorld.copy(_M2); Rk.m.visible=!hid;
    const age=r.state===2?r.age:-1; const calm=age>=0?sstep(0,0.5,age):0; Rk.mat.emissive.copy(PAIN).lerp(Rk.bridge?WARM.clone().lerp(CALM,0.5):CALM,calm);
    Rk.mat.emissiveIntensity=(r.state===0?0.55+0.25*Math.sin(t*4+i):0.65)+(age>=0?1.6*Math.exp(-age/0.35)+0.3*calm:0); Rk.r=r; if(age>=0&&!Rk.bridge) blueTop=i+1; }
  coolLight.position.set(SX+blueTop*T,blueTop*R+0.8,BZ+0.6); coolLight.intensity=blueTop?1.1:0;
  FILL.forEach((f,i)=>{ const L0=TL2.load[0]+0.03*i, u=ease(sstep(L0,L0+0.3,t)); const p=inB(FB_,f.slot).lerp(inB(HB_,V(0,0.1,0)),u); p.y+=0.6*Math.sin(Math.PI*u);
    _M2.compose(p,FB_.q.clone().multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(0,f.yaw,0))),f.s.clone().multiplyScalar(1-0.6*u)); f.m.matrix.copy(_M2); f.m.matrixWorld.copy(_M2);
    f.m.visible=t>=TL2.xray&&u<0.95; f.mat.emissiveIntensity=0.5; });
  // bags
  _M2.compose(HB_.p,HB_.q,V(1,HB_.sy,1)); bag.matrix.copy(_M2); bag.matrixWorldNeedsUpdate=true; bag.visible=true;
  const hfill=t<TL2.load[0]?0:clamp(sstep(TL2.load[0],TL2.load[1],t)-0.12*Math.max(0,cycOf(t).k-2)*(t>=TL2.cyc2?1:0),0,1)*(1-sstep(TL2.bridge-0.9,TL2.bridge-0.6,t));
  bagU.uVis.value=1; bagU.uX.value=X*0.6; bagU.uFill.value=hfill; bagGlow.position.copy(HB_.p); bagGlow.material.opacity=0.2*(0.3+0.7*hfill); bagGlow.scale.setScalar(1.3);
  bagLight.position.copy(HB_.p); bagLight.intensity=2.2*(0.1+0.6*hfill);
  _M2.compose(FB_.p,FB_.q,V(FB,FB*FB_.sy,FB)); fbag.matrix.copy(_M2); fbag.matrixWorldNeedsUpdate=true;
  const ffill=1-sstep(TL2.load[0],TL2.load[1],t)*0.95-0.05*sstep(TL2.lift[0],TL2.lift[1],t); fbU.uVis.value=vis; fbU.uX.value=X; fbU.uFill.value=ffill;
  fbGlow.position.copy(FB_.p); fbGlow.material.opacity=vis*0.28*ffill; fbGlow.scale.setScalar(2.0);
  // lamp (Part 1's, fully lit)
  lamp.position.set(SX+7.75*T,TOPY,0.24); lamp.visible=true; const flick=0.92+0.08*Math.sin((t+P1)*17.0)*Math.sin((t+P1)*5.3);
  lampFlame.material.opacity=1; lampFlame.scale.setScalar(1); lampGlow.position.copy(lamp.position).add(V(0,0.13,0)); lampGlow.material.opacity=0.5*flick; lampGlow.scale.setScalar(0.6);
  lampLight.position.copy(lampGlow.position); lampLight.intensity=1.5*flick;
  // camera and light rigs
  const C=camAt2(t); cam.up.copy(UPV); cam.position.copy(C.p); cam.lookAt(C.l); cam.fov=C.fov; cam.updateProjectionMatrix();
  const focus=C.l.clone(); key.position.copy(focus).add(V(-5,11,8)); key.target.position.copy(focus); key.target.updateMatrixWorld();
  rim.position.copy(focus).add(SUN_DIR.clone().multiplyScalar(20)).add(V(0,3,0)); rim.target.position.copy(focus); rim.target.updateMatrixWorld(); rim.intensity=0.85+0.25*sstep(18,19.5,t);
  skyU.uGlow.value=1+0.35*sstep(18.0,20,t);
  moteU.camPos.value.copy(cam.position); moteU.t.value=t+P1; moteU.wx.value=tab2(t); moteU.box.value=C.p.distanceTo(C.l)>6?16:9; moteU.op.value=1;
  drawPuffs(t);
  GU.uT.value=t+P1; GU.uX.value=X*0.92; const df=t-TL2.xray; GU.uFlash.value=(df>=0&&df<0.18)?0.16*(1-df/0.18):0; bloom.strength=0.5+0.1*X;
  LAST={JH,JF,FB_,HB_}; return LAST; }

const acc2=document.createElement('canvas'); acc2.width=W; acc2.height=H; const actx2=acc2.getContext('2d');
window.renderAt=function(t,Ksub=3){ const shutter=1/60; actx2.globalAlpha=1; actx2.clearRect(0,0,W,H);
  const a0=t<CUT2?0:CUT2, a1=t<CUT2?CUT2-1e-4:DUR2;   // never blur across the cut
  for(let k=0;k<Ksub;k++){ const tt=clamp(t+(Ksub>1?(k/(Ksub-1)-0.5)*shutter:0),a0,a1); setT2(tt); composer.render(); actx2.globalAlpha=1/(k+1); actx2.drawImage(renderer.domElement,0,0); }
  return acc2.toDataURL('image/jpeg',0.95); };
// overlay data: projected label anchors for the friend's rocks, the ROCK counter
const proj2=v=>{ const p=v.clone().project(cam); return [p.x*0.5+0.5,0.5-p.y*0.5,p.z<1?1:0]; };
window.metaAt=function(t){ const S=setT2(t); cam.updateMatrixWorld();
  const labels=FROCK.map((Rk,i)=>{ const r=Rk.r; return {txt:Rk.txt,i,state:r.state,age:r.state===2?r.age:-1,hide:r.hide||0,xr:XRL.includes(i),at:proj2(r.pos.clone().add(V(0,r.size.y*0.5+0.04,0))),dist:cam.position.distanceTo(r.pos)}; });
  return {t,counter:TL2.place.filter(p=>p<=t).length,labels,bag:proj2(S.FB_.p),bagTop:proj2(S.FB_.p.clone().add(V(0,BAG_H*FB*0.55,0))),hero:proj2(S.JH.head),friend:proj2(S.JF.head)}; };
window.DUR=DUR2; window.ready=true;
