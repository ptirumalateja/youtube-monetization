// A stickman with a face and clothes (collar, rolled sleeves, trousers, shoes, optional tie / ID lanyard / side bag).
// Skeleton joints come from sld.js's rig math (R.skel) or from explicit joints (lying / propped poses); this file only builds the meshes.
import * as THREE from 'three';
const V=(x,y,z)=>new THREE.Vector3(x,y,z);
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x)); const sstep=(a,b,x)=>{const t=clamp((x-a)/(b-a));return t*t*(3-2*t)}; const lerp=(a,b,t)=>a+(b-a)*t;
const UP=V(0,1,0);
function limb(m,a,b,r){ const d=b.clone().sub(a); const len=Math.max(d.length(),1e-4); m.position.copy(a).add(b).multiplyScalar(0.5); m.scale.set(r,len,r); m.quaternion.setFromUnitVectors(UP,d.multiplyScalar(1/len)); }
function drawFace(g,W,H,m,blink,open,brow=0,wide=0){ g.clearRect(0,0,W,H); const cx=W/2, cy=H/2+8, dark='#2b1a12';
  const happy=sstep(0.7,0.92,m), glad=sstep(0.45,0.7,m), sad=1-sstep(0.12,0.5,m);
  if(happy>0){ g.fillStyle=`rgba(255,120,110,${0.4*happy})`; for(const sx of [-1,1]){ g.beginPath(); g.ellipse(cx+sx*128,cy+34,38,22,0,0,7); g.fill(); } }
  const ex=82, ey=cy-34; g.lineCap='round'; g.lineJoin='round';
  for(const sx of [-1,1]){ const x=cx+sx*ex;
    if(blink>0.75){ g.strokeStyle=dark; g.lineWidth=11; g.beginPath(); g.moveTo(x-26,ey+4); g.quadraticCurveTo(x,ey+12,x+26,ey+4); g.stroke(); }
    else if(blink>0.25){ g.fillStyle=dark; g.beginPath(); g.ellipse(x,ey+6,18,10,0,0,Math.PI); g.fill(); g.strokeStyle=dark; g.lineWidth=9; g.beginPath(); g.moveTo(x-24,ey+5); g.lineTo(x+24,ey+5); g.stroke(); }
    else if(happy>0.5){ g.strokeStyle=dark; g.lineWidth=12; g.beginPath(); g.arc(x,ey+16,26,Math.PI*1.12,Math.PI*1.88); g.stroke(); }
    else { g.fillStyle=dark; g.beginPath(); g.ellipse(x,ey,1.4*(13+3*glad)*(1+0.18*wide),1.4*(17+4*glad-6*sad)*(1+0.3*wide),0,0,7); g.fill(); g.fillStyle='rgba(255,255,255,0.85)'; g.beginPath(); g.arc(x+5,ey-8,6,0,7); g.fill();
      if(sad>0.3){ g.fillStyle='rgba(236,222,196,1)'; g.beginPath(); g.moveTo(x-sx*(-20),ey-24); g.lineTo(x+sx*(-26),ey-24); g.lineTo(x+sx*(-26),ey-24+ (10+12*sad)); g.closePath(); } }
    // brows: happy = high and arched, neutral = flat, sad = inner end up
    const by=ey-48-8*happy-4*glad+4*sad-22*brow, slope=-Math.max(0,0.5-m)*34;   /* V3: sad = inner ends UP (worry), flat otherwise; never the angry V */ g.strokeStyle=dark; g.lineWidth=13; g.beginPath(); g.moveTo(x-sx*22*0-24,by+(sx>0?1:-1)*0+slope*(sx>0?1:-1)*-0.0); g.moveTo(x-24,by+(sx<0? -slope:slope)*0.35); g.lineTo(x+24,by+(sx<0? slope:-slope)*0.35); g.stroke(); }
  // mouth
  const my=cy+66, w=44+30*happy, c=lerp(-26,26,m); g.strokeStyle=dark; g.lineWidth=9;
  if(open>0.15||happy>0.6){ const o=Math.max(open,happy*0.8); g.fillStyle='#4a1a14'; g.beginPath(); g.moveTo(cx-w,my-6); g.quadraticCurveTo(cx,my+4,cx+w,my-6); g.quadraticCurveTo(cx,my+8+60*o,cx-w,my-6); g.fill(); g.fillStyle='#ff8a85'; g.beginPath(); g.ellipse(cx,my+22+16*o,w*0.42,10+8*o,0,0,7); g.fill(); g.stroke(); }
  else { g.beginPath(); g.moveTo(cx-w,my+(c<0?8:0)); g.quadraticCurveTo(cx,my+c*1.1,cx+w,my+(c<0?8:0)); g.stroke(); } }
// V3: the one hero design used in every scene (cream shirt, navy trousers, short dark hair, crimson bag strap)
export const HERO={skin:0xf2e2c6,shirt:0xf1e9d8,pants:0x1f2a44,hair:0x2a1c14,strap:0xb83a30,headR:0.17};
export function createFigure(scene,{skin=0xf0dfc5,shirt=0xf4f0e8,pants=0x24262c,shoe=0x15171b,tie=0x3f4859,scale=1.0,headR=0.17,hair=null,strap=0x3a2a1e}={}){
  const g=new THREE.Group(); scene.add(g);
  const mk=(col,r=0.6)=>new THREE.MeshStandardMaterial({color:col,roughness:r,metalness:0});
  const skinM=mk(skin,0.55), shirtM=mk(shirt,0.75), pantsM=mk(pants,0.8), shoeM=mk(shoe,0.45), tieM=mk(tie,0.6), leatherM=mk(0x3a2a1e,0.7), idM=mk(0xffffff,0.5);
  const cyl=new THREE.CylinderGeometry(1,1,1,14,1,false), sph=new THREE.SphereGeometry(1,22,16);
  const part=(geo,mat)=>{ const m=new THREE.Mesh(geo,mat); m.castShadow=true; m.receiveShadow=true; m.frustumCulled=false; g.add(m); return m; };
  const P={ torso:part(cyl,shirtM), chest:part(sph,shirtM), pelvis:part(sph,pantsM), neck:part(cyl,skinM), head:part(sph,skinM),
    thighL:part(cyl,pantsM), thighR:part(cyl,pantsM), shinL:part(cyl,pantsM), shinR:part(cyl,pantsM), kneeL:part(sph,pantsM), kneeR:part(sph,pantsM),
    upL:part(cyl,shirtM), upR:part(cyl,shirtM), sleeveL:part(cyl,shirtM), sleeveR:part(cyl,shirtM), foreL:part(cyl,skinM), foreR:part(cyl,skinM), shL:part(sph,shirtM), shR:part(sph,shirtM), elL:part(sph,shirtM), elR:part(sph,shirtM), handL:part(sph,skinM), handR:part(sph,skinM),
    shoeL:part(new THREE.BoxGeometry(1,1,1),shoeM), shoeR:part(new THREE.BoxGeometry(1,1,1),shoeM),
    tie:part(new THREE.BoxGeometry(1,1,1),tieM), knot:part(new THREE.BoxGeometry(1,1,1),tieM), collarA:part(new THREE.BoxGeometry(1,1,1),shirtM), collarB:part(new THREE.BoxGeometry(1,1,1),shirtM), belt:part(cyl,leatherM),
    cord:part(cyl,tieM), card:part(new THREE.BoxGeometry(1,1,1),idM), bag:part(new THREE.BoxGeometry(1,1,1),leatherM), flap:part(new THREE.BoxGeometry(1,1,1),leatherM), strapF:part(cyl,mk(strap,0.7)), strapB:part(cyl,mk(strap,0.7)), thumbL:part(sph,skinM), thumbR:part(sph,skinM) };
  // face: a curved cap on the head sphere carrying a redrawn canvas
  const cv=document.createElement('canvas'); cv.width=512; cv.height=384; const cg=cv.getContext('2d'); const ft=new THREE.CanvasTexture(cv); ft.colorSpace=THREE.SRGBColorSpace; ft.anisotropy=4;
  const cap=new THREE.Mesh(new THREE.SphereGeometry(headR*1.012,28,20,Math.PI/2-0.78,1.56,Math.PI/2-0.6,1.2),new THREE.MeshBasicMaterial({map:ft,transparent:true,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-2})); cap.frustumCulled=false; g.add(cap);
  // hair, ears and a nose: a person, not a ball
  const hairM=mk(hair??0x2a1c14,0.85); const hairMesh=new THREE.Mesh(new THREE.SphereGeometry(headR*1.04,26,16,0,Math.PI*2,0,Math.PI*0.44),hairM); hairMesh.castShadow=true; hairMesh.frustumCulled=false; hairMesh.visible=hair!==null; g.add(hairMesh);
  const earL=part(sph,skinM), earR=part(sph,skinM), nose=part(sph,skinM);
  const F={group:g,parts:P,faceMood:-1,faceBlink:-1,faceOpen:-1};
  F.setVisible=v=>{ g.visible=v; hairMesh.visible=v&&hair!==null; };
  // pose: J joints (world), face {mood 0..1, blink, open, look(rad about head up), fwd Vector3}, dress {tie, lanyard, bag, belt} 0..1, hide: array of part names
  F.pose=(J,face={},dress={})=>{ const s=scale; const m=face.mood??0.5, blink=face.blink||0, open=face.open||0;
    const brow=face.brow||0, wide=face.wide||0; if(Math.abs(m-F.faceMood)>0.01||blink!==F.faceBlink||Math.abs(open-F.faceOpen)>0.02||Math.abs(brow-(F.faceBrow||0))>0.02||Math.abs(wide-(F.faceWide||0))>0.02){ drawFace(cg,512,384,m,blink,open,brow,wide); ft.needsUpdate=true; F.faceMood=m; F.faceBlink=blink; F.faceOpen=open; F.faceBrow=brow; F.faceWide=wide; }
    const up=J.neck.clone().sub(J.hip).normalize(); const hdir=J.head.clone().sub(J.neck).normalize(); const fwd0=(face.fwd||J.fwd||V(1,0,0)).clone();
    let f=fwd0.clone().addScaledVector(hdir,-fwd0.dot(hdir)).normalize(); if(face.look){ f.applyAxisAngle(hdir,face.look); }
    const hc=J.head.clone(); P.head.position.copy(hc); P.head.scale.setScalar(headR); cap.position.copy(hc);
    const hf=face.roll?hdir.clone().applyAxisAngle(f,face.roll):hdir; cap.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(hf.clone().cross(f).normalize(),hf,f));
    { const s_=hdir.clone().cross(f).normalize(); const pole=hdir.clone().multiplyScalar(0.85).addScaledVector(f,-0.52).normalize(); hairMesh.position.copy(hc); hairMesh.quaternion.setFromUnitVectors(UP,pole);
      for(const [e,sg] of [[earL,1],[earR,-1]]){ e.position.copy(hc).addScaledVector(s_,sg*headR*0.98).addScaledVector(hdir,-headR*0.05).addScaledVector(f,-headR*0.05); e.scale.set(headR*0.14,headR*0.22,headR*0.1); e.quaternion.setFromUnitVectors(UP,hdir); }
      nose.position.copy(hc).addScaledVector(f,headR*1.0).addScaledVector(hdir,-headR*0.18); nose.scale.setScalar(headR*0.11); }
    limb(P.neck,J.neck.clone().addScaledVector(up,-0.02),hc.clone().addScaledVector(hdir,-headR*0.8),0.04);
    limb(P.torso,J.hip,J.neck.clone().addScaledVector(up,-0.04),0.088); P.chest.position.copy(J.neck).addScaledVector(up,-0.1); P.chest.scale.set(0.105,0.09,0.1); P.pelvis.position.copy(J.hip); P.pelvis.scale.setScalar(0.1);
    limb(P.thighL,J.hipL,J.kL,0.057); limb(P.thighR,J.hipR,J.kR,0.057); limb(P.shinL,J.kL,J.fL,0.047); limb(P.shinR,J.kR,J.fR,0.047); P.kneeL.position.copy(J.kL); P.kneeL.scale.setScalar(0.054); P.kneeR.position.copy(J.kR); P.kneeR.scale.setScalar(0.054);
    for(const [sd,sh,el,hd] of [['L',J.shL,J.elL,J.hL],['R',J.shR,J.elR,J.hR]]){ limb(P['up'+sd],sh,el,0.043); P['sh'+sd].position.copy(sh); P['sh'+sd].scale.setScalar(0.052); P['el'+sd].position.copy(el); P['el'+sd].scale.setScalar(0.04);
      const cut=el.clone().lerp(hd,0.45); limb(P['sleeve'+sd],el,cut,0.04); limb(P['fore'+sd],cut,hd,0.032);
      // V3 mitten hand: a flattened palm along the forearm plus a thumb on the inner side, so the hand has a direction
      const fd=hd.clone().sub(el).normalize(); const hp=P['hand'+sd]; hp.position.copy(hd).addScaledVector(fd,0.035); hp.scale.set(0.036,0.062,0.05); hp.quaternion.setFromUnitVectors(UP,fd);
      const inner=up.clone().cross(fd).multiplyScalar(sd==='L'?-1:1); if(inner.lengthSq()<1e-4) inner.set(0,0,1); inner.normalize(); const th=P['thumb'+sd]; th.position.copy(hd).addScaledVector(fd,0.015).addScaledVector(inner,0.04); th.scale.set(0.018,0.03,0.018); th.quaternion.setFromUnitVectors(UP,fd.clone().add(inner).normalize()); }
    for(const [sd,ft_] of [['L',J.fL],['R',J.fR]]){ const sh=P['shoe'+sd]; sh.position.copy(ft_).add(V(0.05,-0.03,0)); sh.scale.set(0.22,0.075,0.1); }
    const side=J.hipL.clone().sub(J.hipR); side.y=0; side.length()>1e-4?side.normalize():side.set(0,0,1); const q=new THREE.Quaternion().setFromUnitVectors(UP,up);
    const tieA=dress.tie||0; for(const k of ['tie','knot','collarA','collarB']) P[k].visible=tieA>0.02||k.startsWith('collar')&&(dress.collar||0)>0.02;
    const fw=V(1,0,0).addScaledVector(up,-up.x).normalize(); if(Math.abs(fw.length()-1)>0.01||isNaN(fw.x)) fw.set(1,0,0); const fwdB=(J.fwd||fw).clone();
    P.collarA.position.copy(J.neck).addScaledVector(up,-0.02).addScaledVector(side,0.045).addScaledVector(fwdB,0.05); P.collarA.quaternion.copy(q); P.collarA.scale.set(0.07,0.02,0.05); P.collarA.rotateX(0.5);
    P.collarB.position.copy(J.neck).addScaledVector(up,-0.02).addScaledVector(side,-0.045).addScaledVector(fwdB,0.05); P.collarB.quaternion.copy(q); P.collarB.scale.set(0.07,0.02,0.05); P.collarB.rotateX(-0.5);
    P.knot.position.copy(J.neck).addScaledVector(up,-0.06).addScaledVector(fwdB,0.088); P.knot.quaternion.copy(q); P.knot.scale.set(0.04,0.04,0.025);
    P.tie.position.copy(J.neck).addScaledVector(up,-0.19).addScaledVector(fwdB,0.092); P.tie.quaternion.copy(q); P.tie.scale.set(0.034,0.22,0.014);
    const belt=dress.belt??1; P.belt.visible=belt>0.02; P.belt.position.copy(J.hip).addScaledVector(up,0.06); P.belt.quaternion.copy(q); P.belt.scale.set(0.094,0.03,0.094);
    const lan=dress.lanyard||0; P.cord.visible=P.card.visible=lan>0.02; if(lan>0.02){ const c0=J.neck.clone().addScaledVector(up,-0.04).addScaledVector(fwdB,0.09), c1=J.neck.clone().addScaledVector(up,-0.32).addScaledVector(fwdB,0.105); limb(P.cord,c0,c1,0.004); P.card.position.copy(c1).addScaledVector(up,-0.04); P.card.quaternion.copy(q); P.card.scale.set(0.055,0.08,0.006); }
    const bag=dress.bag||0; for(const k of ['bag','flap','strapF','strapB']) P[k].visible=bag>0.02;
    if(bag>0.02){ const bp=J.hip.clone().addScaledVector(side,0.13).addScaledVector(up,-0.03).addScaledVector(fwdB,-0.04); P.bag.position.copy(bp); P.bag.quaternion.copy(q); P.bag.scale.set(0.32,0.25,0.11); P.flap.position.copy(bp).addScaledVector(up,0.09); P.flap.quaternion.copy(q); P.flap.scale.set(0.335,0.1,0.118);
      const tb=bp.clone().addScaledVector(up,0.12); limb(P.strapF,J.shR.clone().addScaledVector(fwdB,0.05).addScaledVector(up,0.01),tb.clone().addScaledVector(fwdB,0.07),0.012); limb(P.strapB,J.shR.clone().addScaledVector(fwdB,-0.05).addScaledVector(up,0.01),tb.clone().addScaledVector(fwdB,-0.07),0.012); }
    return F; };
  F.setColors=({skin:sk,shirt:sh,pants:pn})=>{ if(sk!==undefined) skinM.color.setHex(sk); if(sh!==undefined) shirtM.color.setHex(sh); if(pn!==undefined) pantsM.color.setHex(pn); };
  return F; }
