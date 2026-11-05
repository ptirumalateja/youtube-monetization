// The Phone at Dinner (Slow Light Dark). A small dark table for two under the gold lamp. He (cream) sits looking down at
// the one red object, his phone, glowing in his hand. She (cream) talks, laughs, reaches across, then goes quiet; dinner
// after dinner (counter 1 -> 1,825) she turns slate grey and fades into the void while the phone's red light grows. One
// night he looks up and puts the phone face down: her chair is empty, her glass still full.
//
// World: table centre at the origin, he sits at -x facing +x, she sits at +x facing -x, camera on +z.
// renderAt(t) is pure (no state between frames). metaAt(t) gives the overlay/sound data.
import * as THREE from 'three';
import * as SLD from './sld.js';
const {V,clamp,sstep,lerp,sm5,rng,yawOf,PAL}=SLD;
const TL=await (await fetch('./timeline.json')).json();
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960, DUR=TL.duration;

const S=SLD.createStage({W,H,lamp:V(0,4.6,0.05),lampTarget:V(0,0,0)});
const R=SLD.createRig(S.scene);
// the lamp drifts off her side of the table over the years, so her half sinks into shadow as she fades (vidIQ note)
const LAMP=V(0,4.6,0.05), beamMesh=S.NOREFL[0];
function aim(target){ const d=target.clone().sub(LAMP).normalize();
  S.spot.target.position.copy(target); S.spot.target.updateMatrixWorld(); S.beamU.uAxis.value.copy(d); beamMesh.quaternion.setFromUnitVectors(V(0,-1,0),d); }
const TOP=0.74, HALF=0.42;

// ---------------------------------------------------------------- wood, table, chairs, plates, glasses
function woodTex(seed,base){ const c=document.createElement('canvas'); c.width=1024; c.height=256; const g=c.getContext('2d'); const Rn=rng(seed);
  g.fillStyle=base; g.fillRect(0,0,1024,256);
  for(let k=0;k<260;k++){ const y=Rn()*256, a=0.04+Rn()*0.1; g.strokeStyle=Rn()<0.6?`rgba(0,0,0,${a})`:`rgba(255,220,180,${a*0.5})`; g.lineWidth=0.6+Rn()*2.2;
    g.beginPath(); g.moveTo(0,y); for(let x=0;x<=1024;x+=32) g.lineTo(x,y+Math.sin(x*0.004+k)*3+Math.sin(x*0.021+k*1.7)*1.2); g.stroke(); }
  const t=new THREE.CanvasTexture(c); t.wrapS=t.wrapT=THREE.RepeatWrapping; t.colorSpace=THREE.SRGBColorSpace; return t; }
const WOOD=SLD.rimify(new THREE.MeshStandardMaterial({color:0x8a6a52,map:woodTex(3,'#3b2a1f'),roughness:0.5,metalness:0}),0xffe6c8,0.05,'wood');
const CHAIRWOOD=SLD.rimify(new THREE.MeshStandardMaterial({color:0x7a5c46,map:woodTex(9,'#33241a'),roughness:0.62,metalness:0}),0xc8d4f0,0.07,'chair');
{ const top=new THREE.Mesh(new THREE.BoxGeometry(HALF*2,0.05,HALF*2),WOOD); top.position.set(0,TOP-0.025,0); top.castShadow=top.receiveShadow=true; S.scene.add(top);
  for(const x of [-HALF+0.06,HALF-0.06]) for(const z of [-HALF+0.06,HALF-0.06]){ const l=new THREE.Mesh(new THREE.BoxGeometry(0.06,TOP-0.05,0.06),WOOD); l.position.set(x,(TOP-0.05)/2,z); l.castShadow=true; S.scene.add(l); } }
const chairGeo={seat:new THREE.BoxGeometry(0.42,0.04,0.42),leg:new THREE.BoxGeometry(0.035,0.44,0.035),post:new THREE.BoxGeometry(0.035,0.5,0.035),rail:new THREE.BoxGeometry(0.03,0.12,0.4)};
function makeChair(x,facing){ const g=new THREE.Group(); const add=(geo,a,b,c)=>{ const m=new THREE.Mesh(geo,CHAIRWOOD); m.position.set(a,b,c); m.castShadow=m.receiveShadow=true; g.add(m); };
  add(chairGeo.seat,0,0.44,0); for(const a of [-0.18,0.18]) for(const c of [-0.18,0.18]) add(chairGeo.leg,a,0.22,c);
  for(const c of [-0.18,0.18]) add(chairGeo.post,-0.19,0.71,c); add(chairGeo.rail,-0.19,0.88,0); add(chairGeo.rail,-0.19,0.68,0);
  g.position.set(x,0,0); g.rotation.y=yawOf(facing); S.scene.add(g); return g; }
makeChair(-0.8,V(1,0,0)); makeChair(0.8,V(-1,0,0));
const PLATEM=SLD.rimify(new THREE.MeshStandardMaterial({color:0x2a2a2e,roughness:0.35,metalness:0}),0xfff1d8,0.1,'plate');
for(const x of [-0.22,0.22]){ const p=new THREE.Mesh(new THREE.CylinderGeometry(0.13,0.1,0.018,40),PLATEM); p.position.set(x,TOP+0.009,0.02); p.receiveShadow=p.castShadow=true; S.scene.add(p); }
const GLASSM=SLD.rimify(new THREE.MeshStandardMaterial({color:0xd8d2c4,roughness:0.12,metalness:0,transparent:true,opacity:0.42,depthWrite:false}),0xfff1d8,0.55,'glass');
const LIQM=new THREE.MeshStandardMaterial({color:0x4a2e16,roughness:0.2,metalness:0,transparent:true,opacity:0.85});
function makeGlass(x,z){ const g=new THREE.Group();
  const a=new THREE.Mesh(new THREE.CylinderGeometry(0.036,0.03,0.13,20,1,true),GLASSM); a.position.y=0.065;
  const l=new THREE.Mesh(new THREE.CylinderGeometry(0.032,0.028,0.08,20),LIQM); l.position.y=0.05;
  const b=new THREE.Mesh(new THREE.CylinderGeometry(0.03,0.03,0.012,20),GLASSM); b.position.y=0.006;
  [a,l,b].forEach(m=>{ m.castShadow=true; m.renderOrder=3; g.add(m); }); g.position.set(x,TOP,z); S.scene.add(g); return g; }
makeGlass(-0.2,-0.24); makeGlass(0.2,-0.24);   // hers stays full

// ---------------------------------------------------------------- the red phone (the one red object): its screen light grows as she fades
const phoneM=SLD.rimify(new THREE.MeshStandardMaterial({color:PAL.RED,roughness:0.4,metalness:0.2,emissive:PAL.RED,emissiveIntensity:0.15}),0xff8a70,0.2,'phone');
const phone=new THREE.Group(); phone.rotation.order='YZX'; { const body=new THREE.Mesh(new THREE.BoxGeometry(0.16,0.012,0.08),phoneM); body.castShadow=true; phone.add(body);
  const scr=new THREE.Mesh(new THREE.PlaneGeometry(0.145,0.068),new THREE.MeshBasicMaterial({color:0xff5a46,transparent:true,opacity:1,fog:false}));
  scr.rotation.x=-Math.PI/2; scr.position.y=0.0065; phone.add(scr); phone.userData.scr=scr; } phone.scale.setScalar(1.8); S.scene.add(phone);
const phoneLight=new THREE.PointLight(0xff3a2a,1.0,1.4,2); S.scene.add(phoneLight);
const phoneHalo=SLD.glowSprite(S.scene,0xff3a2a,0.2);
S.NOREFL.push(phoneHalo,phone);   // the floor mirror made red flares of them

// ---------------------------------------------------------------- the two of them
const him=R.makeFig(PAL.CREAM,'him',{rim:0.16,lift:0.07});
const her=R.makeFig(PAL.CREAM,'her',{rim:0.16,lift:0.07});
const CHAIRP={...R.P0,p:0.07,tilt:0.0,aL:1.5,aR:1.47,kL:1.52,kR:1.47,sL:0.5,sR:0.5,eL:0.9,eR:0.9};
const HIPBACK=0.276;
const HIM_ROOT=V(-0.72+HIPBACK,0,0), HIM_YAW=yawOf(V(1,0,0));
const HER_ROOT=V(0.72-HIPBACK,0,0), HER_YAW=yawOf(V(-1,0,0));
const bump=(t,a,d)=>{ const x=(t-a)/d; return x<=0||x>=1?0:Math.sin(Math.PI*x)**2; };
const CREAM=new THREE.Color(PAL.CREAM), SLATE=new THREE.Color(PAL.SLATE);

const dinnerAt=t=>1+Math.floor((TL.dinners-1)*Math.pow(clamp((t-TL.dinner0)/(TL.dinner1-TL.dinner0)),TL.dinnerPow)+1e-9);
const greyK=t=>sstep(TL.grey[0],TL.grey[1],t), fadeA=t=>1-sstep(TL.fade[0],TL.fade[1],t);
const talkK=t=>1-sstep(TL.quiet-0.6,TL.quiet+0.4,t);          // she talks freely until she goes quiet
const lookK=t=>sstep(TL.lookUp[0],TL.lookUp[1],t), downK=t=>sstep(TL.phoneDown[0],TL.phoneDown[1],t);

function herAt(t){
  const tk=talkK(t), slump=sstep(TL.quiet,TL.grey[1],t);
  const L=Math.max(bump(t,-0.5,1.4),bump(t,1.6,1.1)*0.8,bump(t,3.2,0.9)*0.5)*tk;   // laughs at her own story, he doesn't look up
  const P={...CHAIRP};
  P.p+=0.1*tk*(0.5+0.5*Math.sin(t*2.1))-0.12*L+0.04*L*Math.sin(t*28)+0.22*slump;  // leans in to talk; later sinks
  P.tilt+=-0.3*L+0.06*tk*Math.sin(t*3.3)+0.35*slump;                               // head drops when she gives up
  P.hy=0.05*tk*Math.sin(t*1.3);
  // hands: talking gestures over the table; one reach across to touch his hand; later folded in her lap
  const g=tk*(0.5+0.5*Math.sin(t*4.2)), g2=tk*(0.5+0.5*Math.sin(t*3.1+1.4));
  let hR=V(0.33,TOP+0.05+0.16*g,-0.12+0.04*g), hL=V(0.33,TOP+0.05+0.13*g2,0.13);
  const reach=bump(t,TL.touch[0],TL.touch[1]-TL.touch[0]);
  hR=hR.lerp(V(-0.2,TOP+0.03,-0.12),sm5(Math.min(1,reach*1.6)));                  // her hand rests on his; nothing
  P.p+=0.25*reach;
  const lap=sstep(TL.quiet,TL.quiet+1.2,t);
  hR=hR.lerp(V(0.43,0.6,-0.08),lap); hL=hL.lerp(V(0.43,0.6,0.08),lap);
  Object.assign(P,{tR:hR,wR:1,pR:V(-0.3,-0.7,-0.7),tL:hL,wL:1,pL:V(-0.3,-0.7,0.7)});
  return P;
}
function himAt(t){
  const lk=lookK(t), dn=downK(t);
  const P={...CHAIRP};
  P.p+=0.16*(1-lk)+0.03*(1-lk)*sstep(3,12,t);                  // hunched over the screen, a little more every year
  P.tilt+=0.62*(1-lk)-0.05*lk;                                   // eyes down... then up at her chair
  P.hy=0.03*Math.sin(t*0.7)*(1-lk);
  // phone: held low in front of his chest, thumb scrolling; at the look-up it goes face down on the table
  const scroll=0.006*Math.sin(t*9.5)*(1-lk);
  const held=V(-0.3,1.0+scroll,0.16), table=V(-0.28,TOP+0.01,0.14);   // held out in front of him, on the camera side: readable from frame 0
  const pp=held.clone().lerp(table,sm5(dn));
  const hR=pp.clone().add(V(-0.07,-0.05,-0.035)), hL=V(-0.22,TOP+0.03,-0.12);
  Object.assign(P,{tR:hR,wR:1,pR:V(-0.3,-0.7,-0.7),tL:hL,wL:1,pL:V(-0.3,-0.7,0.7)});
  return {P,pp,tiltPhone:lerp(0.85,0,sm5(dn)),flip:sm5(dn)};
}

// ---------------------------------------------------------------- camera: both in frame; a slow push toward him over the years; a slow pull back on the empty chair
function camAt(t){
  const push=Math.pow(sstep(0,TL.lookUp[0],t),1.3), back=sstep(TL.lookUp[1],DUR,t);
  const tg=V(lerp(0.0,0.05,push)+0.2*back,lerp(0.92,0.95,push),0);   // the empty chair must stay fully in frame for the twist
  const dist=lerp(5.6,5.0,push)+0.9*back, az=lerp(0.28,0.2,push), el=lerp(0.2,0.16,push);
  const dir=V(Math.sin(az)*Math.cos(el),Math.sin(el),Math.cos(az)*Math.cos(el));
  return {pos:tg.clone().addScaledVector(dir,dist),tg};
}

// ---------------------------------------------------------------- one frame
function setT(t){
  // her: cream -> slate -> gone
  const gk=greyK(t), a=fadeA(t);
  her.mat.color.copy(CREAM).lerp(SLATE,gk); her.mat.emissive.copy(her.mat.color); her.mat.emissiveIntensity=0.07*(1-gk);
  her.mat.userData.rim.value=lerp(0.16,0.08,gk); her.setAlpha(a);
  if(a>0.004) R.poseFig(her,R.skel(herAt(t),HER_ROOT,HER_YAW));
  const h=himAt(t); R.poseFig(him,R.skel(h.P,HIM_ROOT,HIM_YAW));
  // phone: tilted toward his face while held, lies flat face down after
  phone.position.copy(h.pp); phone.rotation.set(Math.PI*h.flip,0.55*(1-h.flip),h.tiltPhone);   // angled so the screen also shows to the camera
  const glow=(0.55+0.45*sstep(3,12,t))*(1-sstep(TL.phoneDown[0]+0.15,TL.phoneDown[1],t))*(1+0.06*Math.sin(t*13));
  phone.userData.scr.material.opacity=glow; phoneM.emissiveIntensity=0.06+0.25*glow;
  phoneLight.position.copy(h.pp).add(V(0.02,0.08,0)); phoneLight.intensity=1.15*glow;
  phoneHalo.position.copy(h.pp).add(V(0,0.02,0)); phoneHalo.scale.setScalar(0.32+0.12*glow); phoneHalo.material.opacity=0.22*glow;
  // the lamp loses a little warmth to the phone over the years (no warm payoff in this one)
  const c=camAt(t); S.cam.position.copy(c.pos); S.cam.lookAt(c.tg);
  aim(V(-0.34*sstep(4.5,12.4,t),0,0));
  S.tick(t,-0.18*sstep(4,12.5,t)*(1-0.5*lookK(t)));
}

// ---------------------------------------------------------------- overlay / sound data
window.metaAt=t=>({dinner:dinnerAt(t),herAlpha:fadeA(t),herTalk:talkK(t),glow:(0.55+0.45*sstep(3,12,t))*(1-sstep(TL.phoneDown[0]+0.15,TL.phoneDown[1],t))});
window.events={...TL};
window.renderAt=(t,K=3)=>S.renderAt(setT,t,K,{t0:0,t1:DUR});
window.ready=true;
