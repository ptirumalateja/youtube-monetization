// Don't Tell Your Dreams (Slow Light Dark). A shot-for-shot restaging of the owner's reference reel in the series look:
// dark void, one gold lamp, cream stickmen, ink faces. A small hero holds a glowing star (his dream) among four tall
// "friends". They smile, then turn: knives behind their backs, hands reaching for the star. He hugs it, closes his eyes,
// takes it into his chest, opens them determined; the light bursts out and throws them to the floor.
// Shots and beats come from timeline.json (measured from the reference at 30 fps). renderAt(t) is pure, never blurs across a cut.
import * as THREE from 'three';
import * as SLD from './sld.js';
const {V,clamp,sstep,lerp,sm5,PAL,rng,rotY,yawOf}=SLD;
const TL=await (await fetch('./timeline.json')).json();
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960, DUR=TL.duration;

const S=SLD.createStage({W,H,lamp:V(0,4.6,0.4),lampTarget:V(0,0,0),cone:0.46,spot:38,motes:600});
S.bloom.strength=0.32;
const fillF=new THREE.DirectionalLight(0xfff0dc,0.55); fillF.position.set(0.3,1.4,4); fillF.target.position.set(0,1.1,0); S.scene.add(fillF,fillF.target);   // soft front fill: evens the faces between the lamp above and the star below
const R=SLD.createRig(S.scene);
const INK='#24180f', CAMV=V(0,0,1);
const bump=(t,a,d)=>{ const x=(t-a)/d; return x<=0||x>=1?0:Math.sin(Math.PI*x)**2; };

// ---------------------------------------------------------------- faces (ink on the cream heads)
function faceTex(kind){ const c=document.createElement('canvas'); c.width=c.height=256; const g=c.getContext('2d');
  g.strokeStyle=g.fillStyle=INK; g.lineCap='round'; g.lineJoin='round'; g.lineWidth=12;
  const dot=(x,y,r=12)=>{ g.beginPath(); g.ellipse(x,y,r*0.85,r*1.15,0,0,7); g.fill(); };
  const line=(...p)=>{ g.beginPath(); g.moveTo(p[0],p[1]); for(let i=2;i<p.length;i+=2) g.lineTo(p[i],p[i+1]); g.stroke(); };
  const arc=(x,y,r,a0,a1)=>{ g.beginPath(); g.arc(x,y,r,a0,a1); g.stroke(); };
  ({
    smile:()=>{ dot(98,108); dot(158,108); arc(128,128,40,0.22*Math.PI,0.78*Math.PI); },
    grin:()=>{ dot(98,104); dot(158,104); g.lineWidth=11; arc(128,118,48,0.15*Math.PI,0.85*Math.PI); },
    neutral:()=>{ dot(98,108); dot(158,108); line(106,168,150,168); },
    angry:()=>{ g.lineWidth=14; line(72,82,114,100); line(184,82,142,100); dot(100,118,11); dot(156,118,11); g.lineWidth=12; arc(128,196,36,1.2*Math.PI,1.8*Math.PI); },
    worried:()=>{ g.lineWidth=10; line(76,86,112,74); line(180,86,144,74); dot(100,112,13); dot(156,112,13); g.beginPath(); g.ellipse(128,170,15,19,0,0,7); g.fill(); },
    scared:()=>{ g.lineWidth=10; line(74,80,112,66); line(182,80,144,66); g.lineWidth=8; g.beginPath(); g.ellipse(100,110,17,21,0,0,7); g.stroke(); g.beginPath(); g.ellipse(156,110,17,21,0,0,7); g.stroke(); dot(100,114,8); dot(156,114,8);
      g.beginPath(); g.moveTo(104,180); g.quadraticCurveTo(128,146,152,180); g.closePath(); g.fill(); },
    closed:()=>{ g.lineWidth=9; arc(100,96,22,0.2*Math.PI,0.8*Math.PI); arc(156,96,22,0.2*Math.PI,0.8*Math.PI); line(84,124,116,124); line(140,124,172,124); g.lineWidth=11; arc(128,196,28,1.25*Math.PI,1.75*Math.PI); },
    determined:()=>{ g.lineWidth=15; line(70,92,116,100); line(186,92,140,100); g.beginPath(); g.ellipse(100,120,12,10,0,0,7); g.fill(); g.beginPath(); g.ellipse(156,120,12,10,0,0,7); g.fill(); g.lineWidth=11; arc(128,198,26,1.25*Math.PI,1.75*Math.PI); },
    sad:()=>{ g.lineWidth=10; line(76,90,112,78); line(180,90,144,78); dot(100,114,11); dot(156,114,11); g.lineWidth=11; arc(128,200,32,1.22*Math.PI,1.78*Math.PI); },
    dazed:()=>{ g.lineWidth=10; line(86,96,114,124); line(114,96,86,124); line(142,96,170,124); line(170,96,142,124); g.beginPath(); g.moveTo(100,172); g.quadraticCurveTo(114,160,128,172); g.quadraticCurveTo(142,184,156,172); g.stroke(); },
  })[kind]();
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; return t; }
const FACES={}; for(const k of ['smile','grin','neutral','angry','worried','scared','closed','determined','sad','dazed']) FACES[k]=new THREE.MeshBasicMaterial({map:faceTex(k),transparent:true,depthWrite:false});

// ---------------------------------------------------------------- characters
// hero: smaller (0.82), head kept full size (reads younger), three ink hair strands. Friends: taller (1.06).
function makeChar(id,scale,{hair=false}={}){
  const fig=R.makeFig(PAL.CREAM,id,{rim:0.14,lift:0.025}); fig.rs=scale<1?0.92:1.0; fig.hs=scale<1?1.06:1.0;
  const face=new THREE.Mesh(new THREE.PlaneGeometry(0.24,0.24),FACES.smile); face.renderOrder=4; S.scene.add(face);
  const props=new THREE.Group(); S.scene.add(props);
  if(hair){ const m=new THREE.MeshBasicMaterial({color:0x24180f});
    [[-0.05,0.35],[0.0,0.0],[0.05,-0.3],[-0.025,0.15]].forEach(([x,a])=>{ const h=new THREE.Mesh(new THREE.CylinderGeometry(0.006,0.008,0.085,6),m); h.position.set(x,0.135*1.06+0.03,0); h.rotation.z=a; props.add(h); }); }
  return {id,fig,face,props,scale}; }
const hero=makeChar('hero',0.82,{hair:true});
const FR=['L2','L1','R1','R2'].map(id=>makeChar(id,1.06));
const F_=Object.fromEntries(FR.map(f=>[f.id,f]));

// the star: an extruded five-point star, gold, self-lit, with a glow and a light
const starShape=new THREE.Shape(); for(let i=0;i<10;i++){ const a=Math.PI/2+i*Math.PI/5, r=i%2?0.058:0.14; const x=Math.cos(a)*r, y=Math.sin(a)*r; i?starShape.lineTo(x,y):starShape.moveTo(x,y); }
const starGeo=new THREE.ExtrudeGeometry(starShape,{depth:0.03,bevelEnabled:true,bevelThickness:0.012,bevelSize:0.01,bevelSegments:2}); starGeo.center();
const starMat=new THREE.MeshStandardMaterial({color:0xffd27a,emissive:0xffb84a,emissiveIntensity:1.3,roughness:0.35,transparent:true});
const star=new THREE.Mesh(starGeo,starMat); S.scene.add(star); const STARK=1.45;   // star size vs the hands
const starGlow=SLD.glowSprite(S.scene,0xffc060,0.9), chestGlow=SLD.glowSprite(S.scene,0xffc060,0), burstGlow=SLD.glowSprite(S.scene,0xfff0c8,0), ring=SLD.glowSprite(S.scene,0xffe0a8,0);
const starL=new THREE.PointLight(0xffb850,0.6,3,2); S.scene.add(starL);
S.NOREFL.push(starGlow,chestGlow,burstGlow,ring);

// knives: a steel blade and a dark handle, one per friend
function makeKnife(){ const g=new THREE.Group(); const sh=new THREE.Shape([new THREE.Vector2(-0.022,0),new THREE.Vector2(0.018,0),new THREE.Vector2(0.012,0.17),new THREE.Vector2(-0.022,0.21)].map(v=>v));
  const blade=new THREE.Mesh(new THREE.ExtrudeGeometry(sh,{depth:0.006,bevelEnabled:false}),new THREE.MeshStandardMaterial({color:0xd8dde2,metalness:0.7,roughness:0.25})); blade.position.set(0,0.05,-0.003);
  const hd=new THREE.Mesh(new THREE.BoxGeometry(0.03,0.1,0.022),new THREE.MeshStandardMaterial({color:0x3a2416,roughness:0.6})); hd.position.y=0.0;
  g.add(blade,hd); g.traverse(o=>{ o.castShadow=true; }); S.scene.add(g); return g; }
const KNIFE=Object.fromEntries(FR.map(f=>[f.id,makeKnife()]));

// ---------------------------------------------------------------- shots
const SHOTS=TL.shots.map(([t0,name],i)=>({t0,t1:i+1<TL.shots.length?TL.shots[i+1][0]:DUR,name}));
const shotAt=t=>SHOTS.filter(s=>t>=s.t0).pop();

// ---------------------------------------------------------------- skeleton helpers
// scaled skeleton: targets are brought into the unscaled frame, joints are scaled back about the root
function skelS(P,root,yaw,s){ const P2={...P}; for(const k of ['tL','tR']) if(P[k]) P2[k]=root.clone().add(P[k].clone().sub(root).divideScalar(s));
  const J=R.skel(P2,root,yaw); for(const k in J) if(k!=='fwd') J[k]=root.clone().add(J[k].clone().sub(root).multiplyScalar(s)); return J; }
// whole-body tumble: rotate every joint about the hip around axis by ang, then move the hip to hipTo
function tumble(J,axis,ang,hipTo){ const q=new THREE.Quaternion().setFromAxisAngle(axis,ang); const h=J.hip.clone();
  for(const k in J){ if(k==='fwd'){ J.fwd.applyQuaternion(q); continue; } J[k]=J[k].clone().sub(h).applyQuaternion(q).add(hipTo); } return q; }
const STAND={...R.P0,p:0.04,aL:0.06,aR:-0.06,kL:0.06,kR:0.06,sL:0.1,sR:0.1,eL:0.25,eR:0.25};

// ---------------------------------------------------------------- the friends' layout per shot (x, z, facing point)
const HOME={L2:V(-1.0,0,-0.32),L1:V(-0.52,0,-0.08),R1:V(0.52,0,-0.08),R2:V(1.0,0,-0.32)};
const yawTo=(from,to,cam=0.45)=>{ const d=to.clone().sub(from).setY(0).normalize(); d.lerp(CAMV,cam).normalize(); return yawOf(d); };

// returns {P, root, yaw, face, J (optional, already built), knife:{hand|world}}
function friendAt(f,t,sh,heroRoot){
  const home=HOME[f.id]; let root=home.clone(), face='grin', P={...STAND}, yaw=yawTo(home,heroRoot);
  const side=Math.sign(home.x), near=Math.abs(home.x)<0.8, idle=Math.sin(t*2.2+home.x*3);
  const fwdOf=y=>rotY(V(1,0,0),y);
  // lean in toward the hero, smiling (A, B start)
  P.p=0.18+0.03*idle; P.tilt=0.12; P.hy=-0.1*side;
  // knife hidden behind the back in the hand away from the hero
  const knifeHand=side<0?'L':'R';
  const behind=()=>{ const fw=fwdOf(yaw); const lat=V(fw.z,0,-fw.x).multiplyScalar(side<0?1:-1); return root.clone().addScaledVector(fw,-0.1).addScaledVector(lat,0.24).add(V(0,0.9,0)); };   // behind the hip, out to the side so the blade shows
  P['t'+knifeHand]=behind(); P['w'+knifeHand]=1; P['p'+knifeHand]=V(-0.6,-0.6,side<0?0.5:-0.5);
  let knife={hand:knifeHand,down:true};
  const name=sh.name, B=TL.B;
  if(name==='A'){ if(f.id==='L1'){ const k=sstep(TL.A.turn1,TL.A.turn1+0.4,t); P.p+=0.2*k; P.tilt+=0.15*k; }
    if(f.id==='R1') knife.show=sstep(TL.A.knifeIn,TL.A.knifeIn+0.15,t); else knife.show=0; }
  if(name==='B'){ knife.show=f.id==='R1'?1:0;
    if(f.id==='R1'&&t>B.r1Angry) face=t<B.r1Angry+0.1?'neutral':'angry';
    if(f.id==='L1'&&t>B.l1Angry) face='angry';
    if(f.id==='L2'||f.id==='R2') face=t>B.l1Angry+0.2?'angry':'grin';
    if(f.id==='R1'){ const r=sm5(sstep(B.reach0,B.reach1,t)); const other=knifeHand==='L'?'R':'L';
      P['t'+other]=V(0.14,1.1+0.03*Math.sin(t*9),0.26); P['w'+other]=r; P['p'+other]=V(-0.3,-1,0); } }
  if(name==='C'||name==='D'){ face='angry'; knife.show=(f.id==='R1'||f.id==='L1')?1:0;
    if(f.id==='R1'){ const other='L'; P['t'+other]=V(0.05+(name==='C'?-0.05:0.08),1.1+0.03*Math.sin(t*9),0.28); P['w'+other]=1; P['p'+other]=V(-0.3,-1,0); }
    if(name==='D'){ P.p=0.3; P.tilt=0.25; root=home.clone().multiply(V(0.85,1,1)).add(V(0,0,0.12)); }
    if(name==='C'&&f.id==='L1'){ P.p=0.38; P.tilt=0.35; } }
  if(name==='E'){ face='angry'; knife.show=0; }
  if(name==='F'){ const Fq=TL.F; knife.show=1; face='sad';
    root=V(home.x*1.08,0,home.z+0.05); yaw=yawTo(root,V(0,0,0.1),0.7);
    const back=sm5(sstep(Fq.back0,Fq.back1,t)); P={...STAND,p:0.22-0.32*back,tilt:0.2-0.25*back,kL:0.2,kR:0.2,aL:0.1,aR:-0.05};
    root.add(V(side*0.12*back,0,-0.08*back)); face=back>0.3?'worried':'sad';
    // knife held at the side, blade up
    const fw=fwdOf(yaw), lat=V(fw.z,0,-fw.x).multiplyScalar(side<0?1:-1);
    P['t'+knifeHand]=root.clone().addScaledVector(fw,0.12).addScaledVector(lat,0.2).add(V(0,0.86,0)); P['w'+knifeHand]=1; P['p'+knifeHand]=V(-0.5,-1,side<0?0.4:-0.4);
    knife.down=false;
    if(t>=Fq.burst){ return {blast:true,P,root,yaw,face,knife,side}; } }
  return {P,root,yaw,face,knife,side}; }

// the blast: thrown outward and up, tumbling, then flat on the floor
const BLAST={L2:[-1.6,1.64,1.9],L1:[-1.2,2.06,2.4],R1:[1.2,2.06,2.3],R2:[1.6,1.64,1.8]};   // landing hip x, z offset (x0.5), launch lift: flat in the foreground, feet toward him   // landing x, landing z offset, launch speed up
function blastJ(f,t,base){ const Fq=TL.F; const u=t-Fq.burst, [lx,lz,vy]=BLAST[f.id], side=Math.sign(lx);
  const T=Fq.land-Fq.burst-0.05+0.04*Math.abs(lx); const k=clamp(u/T);
  const p0=base.root.clone().add(V(0,0.95,0)), p1=V(lx,0.14,base.root.z+lz*0.5);
  const hip=p0.clone().lerp(p1,k); hip.y=lerp(p0.y,p1.y,k)+vy*T*k*(1-k)*1.1;
  const flail=k<1?Math.sin(u*28+lx):0;
  const P={...R.P0,p:-0.1,tilt:-0.3,aL:0.6+0.3*flail,aR:-0.6-0.3*flail,kL:0.3,kR:0.4,sL:2.4+0.4*flail,sR:2.2-0.4*flail,eL:0.4,eR:0.5};
  const L={...R.P0,p:0.0,tilt:0.0,aL:0.18,aR:-0.15,kL:0.05,kR:0.1,sL:1.2,sR:1.0,eL:0.3,eR:0.3};
  const Pf=k<1?P:L;
  const J=R.skel(Pf,V(0,0,0),base.yaw); for(const kk in J) if(kk!=='fwd') J[kk].multiplyScalar(f.scale);
  const ang=side*(k<1?Math.PI*2.5*k:Math.PI*2.5)%(Math.PI*2);   // a full cartwheel in the air, then flat on the floor, head toward him so the dazed face shows
  const axis=V(0,0,1);
  tumble(J,axis,ang,hip);
  // keep the lowest joint on the floor once landed
  if(k>=1){ let mn=9; for(const kk in J) if(kk!=='fwd') mn=Math.min(mn,J[kk].y); const dy=0.055-mn; for(const kk in J) if(kk!=='fwd') J[kk].y+=dy; }
  return {J,Pf,landed:k>=1,ang,axis,face:k<1?'scared':'dazed'}; }

// ---------------------------------------------------------------- the hero
function heroAt(t,sh){ const name=sh.name; let P={...STAND}, root=V(0,0,0.05), yaw=yawOf(CAMV), face='smile';
  const CHY=1.1, chest=(dx=0,dy=0,dz=0)=>V(dx,CHY+dy,0.2+dz);
  let starPos=chest(0,0.02,0.04), starOn=1, starScale=1, hold='both';
  P.p=0.03+0.015*Math.sin(t*2.4); P.tilt=-0.05;
  if(name==='A'){ const tr=sm5(sstep(TL.A.turn0,TL.A.turn1,t)); yaw=lerp(yawOf(CAMV),yawOf(V(-1,0,0.35)),tr);
    if(tr>0){ hold='L'; const fw=rotY(V(1,0,0),yaw); starPos=V(0,CHY+0.02,0.24).lerp(V(0,0,0.05).addScaledVector(fw,0.42).add(V(0,1.08,0)),tr); } }
  if(name==='B'){ P.tilt=-0.08; }
  if(name==='C'){ const C=TL.C; const pull=sm5(sstep(C.pull0,TL.shots[3][0],t)); yaw=lerp(yawOf(V(-1,0,0.3)),yawOf(CAMV),pull*0.6);
    const fw=rotY(V(1,0,0),yaw); hold='L'; starPos=V(0,0,0.05).addScaledVector(fw,0.4).add(V(0,1.08,0)).lerp(chest(0,0,0.04),pull);
    face=t<C.worried?'smile':'worried'; starScale=1-0.25*sstep(C.worried,C.worried+0.4,t); P.hy=t<C.worried?0:0.3; }
  if(name==='D'){ face='scared'; hold='hug'; P.p=0.12+0.01*Math.sin(t*30); P.kL=P.kR=0.18; starScale=0.8; }
  if(name==='E'){ const E=TL.E; hold='hug'; starScale=0.8;
    face=t<E.close?'scared':(t<E.open?'closed':'determined');
    const ab=sm5(sstep(E.absorb0,E.absorb1,t)); starScale=0.8*(1-0.85*ab); starOn=1-sstep(E.absorb1-0.4,E.absorb1,t); starPos=chest(0,0,0.04-0.12*ab);
    const lw=sm5(sstep(E.lower0,E.lower1,t)); if(lw>0) hold=lw>=1?'none':'hug-lower'; P.p=0.06; P.tilt=-0.08+0.1*(t>E.open?0:1)*0;
    return {P,root,yaw,face,starPos,starOn,starScale,hold,lw}; }
  if(name==='F'){ const Fq=TL.F; face='determined'; hold='none'; starOn=0; root=V(0,0,0.05+0.2*sm5(sstep(Fq.step0,Fq.step1,t)));
    P=R.gait({...STAND,p:-0.02,tilt:-0.06,sL:0.05,sR:0.05,eL:0.15,eR:0.15},sstep(Fq.step0,Fq.step1,t)*Math.PI*2,bump(t,Fq.step0,Fq.step1-Fq.step0)); }
  return {P,root,yaw,face,starPos,starOn,starScale,hold,lw:0}; }

// ---------------------------------------------------------------- cameras (one per shot)
function camFor(sh,t){ const u=clamp((t-sh.t0)/(sh.t1-sh.t0));
  const C={ A:[V(0.0,1.42,3.1),V(-0.05,1.2,0),44], B:[V(0.05,1.3,2.1),V(0.03,1.12,0),42], C:[V(0.28,1.35,2.6),V(-0.12,1.1,0),44],
            D:[V(0,1.05,1.75),V(0,1.22,0),48], E:[V(0,1.2,1.6),V(0,1.13,0),40], F:[V(0,1.3,4.6),V(0,1.0,0),44] }[sh.name];
  const pos=C[0].clone(), tg=C[1].clone(); let fov=C[2];
  if(sh.name==='A'){ const p=sm5(sstep(TL.A.turn0,sh.t1,t)); pos.x-=0.18*p; tg.x-=0.22*p; pos.z-=0.25*u; }
  else if(sh.name==='E'){ const p=sm5(sstep(TL.E.push0,sh.t1,t)); pos.z-=0.22*p; tg.y+=0.17*p; pos.y+=0.1*p; pos.z-=0.06*u; }
  else if(sh.name==='D'){ pos.z-=0.25*sm5(u); pos.add(V(0.006*Math.sin(t*41),0.006*Math.sin(t*37),0)); }
  else if(sh.name==='F'){ const k=t>=TL.F.burst?Math.exp(-(t-TL.F.burst)*6):0; pos.add(V(0.05*k*Math.sin(t*80),0.04*k*Math.sin(t*67),0)); pos.z-=0.15*u; }
  else pos.addScaledVector(tg.clone().sub(pos).normalize(),0.18*sm5(u));
  return {pos,tg,fov}; }

// ---------------------------------------------------------------- faces and hair follow the head
function placeFace(ch,J,P,yaw,tumbleQ=null){ const hd=(P.p||0)+(P.tilt||0);
  let fw=rotY(rotY(rotY(V(Math.cos(hd),-Math.sin(hd),0),P.hy||0),P.ty||0),yaw).normalize();
  let up=rotY(rotY(rotY(V(Math.sin(hd),Math.cos(hd),0),P.hy||0),P.ty||0),yaw).normalize();
  if(tumbleQ){ fw.applyQuaternion(tumbleQ); up.applyQuaternion(tumbleQ); }
  else { const toCam=S.cam.position.clone().sub(J.head).setY(0).normalize(); const y=fw.y; fw.setY(0).normalize().lerp(toCam,0.4).normalize().multiplyScalar(Math.sqrt(1-y*y)).setY(y); }
  const r=0.13*(ch.fig.hs||1); ch.face.position.copy(J.head).addScaledVector(fw,r+0.004); ch.face.scale.setScalar((ch.fig.hs||1)*1.0);
  ch.face.up.copy(up); ch.face.lookAt(J.head.clone().addScaledVector(fw,2));
  ch.props.position.copy(J.head); ch.props.up.copy(up); ch.props.lookAt(J.head.clone().addScaledVector(fw,1)); }

// ---------------------------------------------------------------- one frame
function setT(t){ const sh=shotAt(t); const c=camFor(sh,t); S.cam.fov=c.fov; S.cam.updateProjectionMatrix(); S.cam.position.copy(c.pos); S.cam.lookAt(c.tg);
  // hero
  const h=heroAt(t,sh); let P=h.P;
  const chestW=V(0,1.08,0.2).add(V(0,0,h.root.z-0.05));
  if(h.hold==='both'){ P.tL=h.starPos.clone().add(V(-0.15,-0.1,0.0)); P.tR=h.starPos.clone().add(V(0.15,-0.1,0.0)); P.wL=P.wR=1; P.pL=V(-0.3,-1,0.5); P.pR=V(-0.3,-1,-0.5); }
  if(h.hold==='L'){ P.tL=h.starPos.clone().add(V(0,-0.13,0)); P.wL=1; P.pL=V(-0.3,-1,0.4); }
  if(h.hold==='hug'||h.hold==='hug-lower'){ const lw=h.lw||0; const a=chestW.clone().add(V(0.08,0.06,0.03)), b=chestW.clone().add(V(-0.08,0.0,0.03));
    P.tL=a; P.tR=b; P.wL=P.wR=1-lw; P.pL=V(-0.6,-0.8,0.6); P.pR=V(-0.6,-0.8,-0.6); }
  const Jh=skelS(P,h.root,h.yaw,hero.scale); R.poseFig(hero.fig,Jh); hero.face.material=FACES[h.face]; placeFace(hero,Jh,P,h.yaw);
  // star (on the hero's hands or sinking into his chest) and the chest light
  star.visible=h.starOn>0.01; star.position.copy(h.starPos); star.scale.setScalar(h.starScale*STARK);
  star.rotation.set(0,(h.hold==='L'?h.yaw+Math.PI/2:0)+0.15*Math.sin(t*1.7),0.05*Math.sin(t*2.3)); starMat.opacity=h.starOn;
  starGlow.position.copy(h.starPos); starGlow.scale.setScalar(0.5*h.starScale+0.06); starGlow.material.opacity=0.55*h.starOn;
  const inside=sh.name==='E'?sstep(TL.E.absorb0+0.6,TL.E.absorb1,t):(sh.name==='F'?1:0);
  const Fq=TL.F, charge=sh.name==='F'?sstep(Fq.charge0,Fq.burst,t):0, post=sh.name==='F'&&t>=Fq.burst?Math.exp(-(t-Fq.burst)*2.5):0;
  const cpos=Jh.neck.clone().lerp(Jh.hip,0.3).add(V(0,0,0.05)); chestGlow.position.copy(cpos); chestGlow.scale.setScalar(0.5+0.5*charge+0.3*post); chestGlow.material.opacity=inside*(0.5+0.4*charge);
  starL.position.copy(inside>0.5?cpos:h.starPos); starL.intensity=0.5*(h.starOn+inside*0.8)+2*charge+6*post;
  // the burst: a flash from his chest, a ring along the floor
  const fl=sh.name==='F'?bump(t,Fq.burst-0.06,0.3):0; burstGlow.position.copy(cpos); burstGlow.scale.setScalar(2+14*sstep(Fq.burst-0.06,Fq.burst+0.2,t)); burstGlow.material.opacity=fl;
  const rk=sh.name==='F'&&t>=Fq.burst?clamp((t-Fq.burst)/0.6):0; ring.position.set(0,0.05,h.root.z); ring.scale.set(1+7*rk,0.35+0.6*rk,1); ring.material.opacity=0.7*(rk>0?1-rk:0);
  // friends
  const visibleIn={A:['L2','L1','R1','R2'],B:['L1','R1','L2','R2'],C:['L1','R1','R2'],D:['L1','R1','L2','R2'],E:[],F:['L2','L1','R1','R2']}[sh.name];
  for(const f of FR){ const on=visibleIn.includes(f.id); f.fig.setAlpha(on?1:0); f.face.visible=on; KNIFE[f.id].visible=false; if(!on) continue;
    const st=friendAt(f,t,sh,h.root); let J,Pp=st.P,q=null,face=st.face;
    if(st.blast){ const b=blastJ(f,t,st); J=b.J; Pp=b.Pf; face=b.face; q=new THREE.Quaternion().setFromAxisAngle(b.axis,b.ang); }
    else J=skelS(st.P,st.root,st.yaw,f.scale);
    R.poseFig(f.fig,J); f.face.material=FACES[face]; placeFace(f,J,Pp,st.yaw,q);
    // knife: in the hand (blade down behind the back / blade up at the side), or flying and stuck in the floor after the blast
    const kn=KNIFE[f.id], hand=f.fig.joints[st.knife.hand==='L'?10:11].position;
    if(st.blast){ const u=t-Fq.burst, [lx]=BLAST[f.id], s=Math.sign(lx); const T=0.75; const k=clamp(u/T);
      const p0=hand.clone(); const land=V(lx*1.25+s*0.1,0.1,st.root.z+0.55);
      const p=V(lerp(st.root.x,land.x,k),lerp(1.0,land.y,k)+2.2*T*k*(1-k)*1.4,lerp(st.root.z,land.z,k)); kn.position.copy(k<1?p:land);
      kn.rotation.set(0,0,k<1?u*18*s:s*2.7); kn.scale.setScalar(1.5); kn.visible=true; void p0; }
    else if(st.knife.show>0.01){ kn.visible=true; kn.position.copy(hand); kn.rotation.set(0,st.yaw+Math.PI/2,st.knife.down?Math.PI:0); kn.scale.setScalar(1.5*st.knife.show); } }
  S.tick(t,0.4*charge+1.2*fl+0.2*post); }

// ---------------------------------------------------------------- overlay data
window.metaAt=t=>{ setT(t); return {shot:shotAt(t).name}; };
window.events={...TL};
window.renderAt=(t,K=3)=>{ const sh=shotAt(t); return S.renderAt(setT,t,K,{t0:sh.t0,t1:sh.t1}); };
window.ready=true;
