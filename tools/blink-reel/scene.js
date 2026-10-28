// You Were Blind for 20 Minutes Today. One dark-warm studio flat (reading chair, window, desk, bed, wall mirror), an eye macro and a
// neural field. Screen-space eyelids (grade uLid) close on every blink; the hero blinks with them, except in the mirror.
// renderAt(t) is pure. Units are metres. Room at x=0, eye at x=60, neural field at x=120; the camera is always in front (+z).
import * as THREE from 'three';
import {Reflector} from 'three/addons/objects/Reflector.js';
import {createWarmStage,V,clamp,sstep,lerp} from './stage.js';
import * as SLD from './sld.js';
import {createFigure} from './figure.js';
import * as SETS from './sets.js';
const {M,B,C,S:SPH,P:PLN,plant,book,frame,canvasTex,rng}=SETS;
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960;
const DUR=19.0;
const ST=createWarmStage({W,H}); const scene=ST.scene; const R=SLD.createRig(scene); const sm5=SLD.sm5;

// ---------------------------------------------------------------- blinks (screen lids) and the shot list
// [time the lid starts closing]; close 0.06 s, shut 0.07 s, open 0.09 s. Frame 0 opens from shut; the last frames close again (loop).
const BLINKS=[0.95,3.1,5.2, 6.45,7.5,8.45,9.5, 10.05,10.3,10.52,10.72,10.9,11.06, 16.75,17.85];
const lidOne=(t,b)=>{ const u=t-b; if(u<0||u>0.22) return 0; if(u<0.06) return sm5(u/0.06); if(u<0.13) return 1; return 1-sm5((u-0.13)/0.09); };
function lidAt(t){ let l=0; if(t<0.14) l=1-sm5(clamp((t-0.03)/0.11)); if(t>18.8) l=Math.max(l,sm5(clamp((t-18.8)/0.08))); for(const b of BLINKS) l=Math.max(l,lidOne(t,b)); return l; }
const SHOTS=[
  {id:'read',  t0:0.0, t1:6.0,  tod:'night'},
  {id:'window',t0:6.0, t1:7.0,  tod:'morning'},
  {id:'desk',  t0:7.0, t1:8.0,  tod:'noon'},
  {id:'bed',   t0:8.0, t1:9.0,  tod:'evening'},
  {id:'read2', t0:9.0, t1:10.0, tod:'night'},
  {id:'wide',  t0:10.0,t1:12.0, tod:'night'},
  {id:'eye',   t0:12.0,t1:13.8},
  {id:'brain', t0:13.8,t1:16.0},
  {id:'mirror',t0:16.0,t1:19.0, tod:'night'} ];
const shotAt=t=>SHOTS.find(s=>t>=s.t0&&t<s.t1)||SHOTS[SHOTS.length-1];

// ---------------------------------------------------------------- the flat
const room=new THREE.Group(); scene.add(room); SETS.floorAndWalls(room,{wall:0x2e3546,floor:'#6e4a30'});
// window on the back wall with a sky that follows the time of day
const sky=new THREE.MeshBasicMaterial({color:0x101828,fog:false}); { const w=new THREE.Group(); B(w,1.3,1.45,0.06,M(0x2a1c12,{r:0.5}),0,0,0); const pane=PLN(w,1.18,1.33,sky,0,0,0.035); B(w,0.035,1.45,0.07,M(0x2a1c12),0,0,0.04); B(w,1.3,0.035,0.07,M(0x2a1c12),0,0,0.04); w.position.set(0.55,1.72,-2.17); room.add(w);
  const city=PLN(room,1.16,0.5,new THREE.MeshBasicMaterial({map:SETS.bokehTex(true,11,60),transparent:true,opacity:0.85,fog:false}),0.55,1.3,-2.14); room.userData.city=city;
  for(const sx of [-1,1]) B(room,0.3,1.95,0.1,M(0x6a3a36,{r:0.95}),0.55+sx*0.82,1.62,-2.08,{round:0.04}); }
// reading chair + floor lamp (left)
{ const ch=new THREE.Group(); const fab=M(0x7a4a3a,{r:0.95}); B(ch,0.78,0.42,0.74,fab,0,0.21,0,{round:0.08}); B(ch,0.78,0.62,0.18,fab,-0.02,0.64,-0.3,{round:0.08}); for(const sx of [-1,1]) B(ch,0.16,0.3,0.74,fab,sx*0.39,0.52,0,{round:0.06});
  ch.position.set(-1.55,0,-1.05); ch.rotation.y=0.35; room.add(ch);
  const lp=new THREE.Group(); C(lp,0.14,0.16,0.03,M(0x1c1c1e,{m:0.5}),0,0.015,0); C(lp,0.012,0.012,1.5,M(0x2a2a2c,{m:0.6}),0,0.76,0); C(lp,0.13,0.22,0.26,M(0xffe2b0,{e:0xffb860,ei:1.7,r:0.9}),0,1.55,0,{cast:false}); SPH(lp,0.06,M(0xfff0c8,{e:0xffd890,ei:3}),0,1.48,0,{cast:false}); lp.position.set(-2.35,0,-1.55); room.add(lp);
  B(room,0.5,0.45,0.4,M(0x5a3a22,{map:SETS.woodTex('#5a3a22',[1,1])}),-2.45,0.225,-0.55,{round:0.02}); C(room,0.06,0.05,0.1,M(0xe8e1d4,{r:0.4}),-2.4,0.5,-0.5); book(room,-2.55,0.45,-0.6,0.18,0.04,0.24,0x2f6b8a); plant(room,-2.85,0,-1.9,1.3,4); }
// desk + laptop (under the window, right of it)
const laptop=new THREE.Group(); const screenM=M(0x0,{e:0x9fc4ff,ei:0.0}); { const dk=new THREE.Group(); const wood=M(0x6b4428,{map:SETS.woodTex('#6b4428',[2,1])}); B(dk,1.3,0.05,0.62,wood,0,0.76,0,{round:0.01}); for(const [x,z] of [[-0.6,-0.26],[0.6,-0.26],[-0.6,0.26],[0.6,0.26]]) B(dk,0.05,0.76,0.05,M(0x3a2618),x,0.38,z);
  B(laptop,0.36,0.015,0.25,M(0x8a8c92,{m:0.6,r:0.35}),0,0.0,0); const lid=new THREE.Group(); B(lid,0.36,0.24,0.012,M(0x8a8c92,{m:0.6,r:0.35}),0,0.12,0); PLN(lid,0.33,0.21,screenM,0,0.12,0.007); lid.position.set(0,0.008,-0.12); lid.rotation.x=-0.25; laptop.add(lid); laptop.position.set(0.1,0.79,-0.05); dk.add(laptop);
  C(dk,0.045,0.04,0.1,M(0xd9c8a8,{r:0.4}),0.45,0.83,0.05); book(dk,-0.45,0.785,-0.1,0.22,0.06,0.3,0xc4452f); book(dk,-0.45,0.845,-0.1,0.2,0.05,0.28,0xd9a63a);
  dk.position.set(1.75,0,-1.8); room.add(dk);
  const chair=new THREE.Group(); B(chair,0.46,0.05,0.44,M(0x3a2a20),0,0.47,0); B(chair,0.46,0.5,0.05,M(0x3a2a20),0,0.75,0.22); for(const [x,z] of [[-0.2,-0.19],[0.2,-0.19],[-0.2,0.19],[0.2,0.19]]) B(chair,0.04,0.47,0.04,M(0x2a1c14),x,0.235,z); chair.position.set(1.85,0,-1.1); room.add(chair); }
// bed (right, foot towards camera)
{ const bed=new THREE.Group(); B(bed,1.3,0.3,2.1,M(0x5a3a22,{map:SETS.woodTex('#6b4428',[1,1])}),0,0.15,0,{round:0.03}); B(bed,1.2,0.2,2.0,M(0xf2ede4,{r:0.9}),0,0.4,0,{round:0.07}); B(bed,1.24,0.12,1.3,M(0xffffff,{r:0.95,map:SETS.plaidTex()}),0,0.54,0.33,{round:0.06}); B(bed,0.8,0.15,0.4,M(0xfaf6ee,{r:0.95}),0,0.56,-0.75,{round:0.07}); B(bed,1.3,0.9,0.08,M(0x5a3a22),0,0.6,-1.06);
  bed.position.set(2.75,0,-0.75); room.add(bed); }
// shelf, frames, rug
{ const sh=new THREE.Group(); B(sh,1.2,0.04,0.25,M(0x6b4428),0,0,0); const Rr=rng(4); const bc=[0xc4452f,0x2f6b8a,0xd9a63a,0x3f8a45,0x7a4a8a,0xe8e1d4]; for(let i=0;i<8;i++) book(sh,-0.5+i*0.07,0.02,0,0.05,0.18+Rr()*0.1,0.18,bc[i%6]); plant(sh,0.35,0.02,0,0.7,6); sh.position.set(-1.9,2.15,-2.08); room.add(sh); }
frame(room,2.3,2.0,-2.17,0.45,0.35,0x3f8a8a); frame(room,-2.6,1.6,-2.17,0.32,0.42,0xd9a63a);
B(room,2.6,0.02,1.7,M(0x3b4a63,{r:1}),-0.4,0.012,0.2,{round:0.01});
// wall mirror (between chair and window): a real reflection
const MIR={x:-0.62,y:1.38,w:0.62,h:1.25}; B(room,MIR.w+0.1,MIR.h+0.1,0.04,M(0x8a6a3a,{m:0.6,r:0.35}),MIR.x,MIR.y,-2.175);
const mirror=new Reflector(new THREE.PlaneGeometry(MIR.w,MIR.h),{textureWidth:Math.round(W*0.7),textureHeight:Math.round(W*0.7*MIR.h/MIR.w),color:0xb8b4ac,clipBias:0.003}); mirror.position.set(MIR.x,MIR.y,-2.15); room.add(mirror);
const fakeMirror=PLN(room,MIR.w,MIR.h,M(0x1a2030,{r:0.15,m:0.6}),MIR.x,MIR.y,-2.152);

// ---------------------------------------------------------------- props: book, mug, phone
const rbook=new THREE.Group(); { const pg=M(0xf4efe6,{r:0.9}), cv=M(0x8a2f2a,{r:0.7}); for(const sx of [-1,1]){ const h=new THREE.Group(); B(h,0.13,0.012,0.19,cv,sx*0.065,0,0); B(h,0.12,0.02,0.18,pg,sx*0.062,0.012,0); h.rotation.z=-sx*0.28; rbook.add(h); } } scene.add(rbook);
const mug=new THREE.Group(); { C(mug,0.045,0.04,0.1,M(0xe8e1d4,{r:0.4}),0,0,0); C(mug,0.04,0.04,0.005,M(0x3a2010,{r:0.2}),0,0.045,0); } scene.add(mug);
const phone=new THREE.Group(); { B(phone,0.075,0.15,0.01,M(0x0d0e12,{r:0.3,m:0.4}),0,0,0,{round:0.01}); B(phone,0.067,0.138,0.004,new THREE.MeshBasicMaterial({color:0xbcd4ff}),0,0,0.006,{cast:false}); } phone.scale.setScalar(1.4); scene.add(phone); const phoneLight=new THREE.PointLight(0xbcd4ff,0,2.2,2); scene.add(phoneLight);

// ---------------------------------------------------------------- the eye (macro)
const EYE=new THREE.Group(); EYE.position.set(60,0,0); scene.add(EYE);
const irisTex=canvasTex(2048,1024,(g,w,h)=>{ // equirect with the iris around the top pole (v=0); the ball is turned so that pole faces the camera
  g.fillStyle='#eadfd2'; g.fillRect(0,0,w,h); const Rr=rng(8); g.strokeStyle='rgba(170,50,45,0.28)'; g.lineWidth=2; for(let i=0;i<90;i++){ let x=Rr()*w, y=h*(0.3+Rr()*0.45); g.beginPath(); g.moveTo(x,y); for(let k=0;k<7;k++){ x+=(Rr()-0.5)*50; y-=Rr()*28; g.lineTo(x,y); } g.stroke(); }
  const rows=r=>r/Math.PI*h; const iR=rows(0.56), pR=rows(0.2), lR=rows(0.6);
  const gr=g.createLinearGradient(0,0,0,lR); gr.addColorStop(0,'#050403'); gr.addColorStop(pR/lR*0.98,'#050403'); gr.addColorStop(pR/lR*1.02,'#5a3412'); gr.addColorStop(0.55,'#b07a30'); gr.addColorStop(0.8,'#6a4218'); gr.addColorStop(iR/lR,'#24140a'); gr.addColorStop(1,'rgba(234,223,210,1)'); g.fillStyle=gr; g.fillRect(0,0,w,lR);
  for(let i=0;i<2600;i++){ const x=Rr()*w; g.strokeStyle=`rgba(${Rr()<0.55?'245,200,120':'30,16,8'},${0.08+Rr()*0.22})`; g.lineWidth=1+Rr()*4; g.beginPath(); g.moveTo(x,pR+2+Rr()*6); g.lineTo(x+(Rr()-0.5)*14,pR+(iR-pR)*(0.5+Rr()*0.5)); g.stroke(); }
  g.fillStyle='#050403'; g.fillRect(0,0,w,pR); });
const eyeM=new THREE.MeshPhysicalMaterial({map:irisTex,roughness:0.3,clearcoat:1,clearcoatRoughness:0.04});
const eyeBall=new THREE.Mesh(new THREE.SphereGeometry(1,128,96),eyeM); eyeBall.rotation.x=Math.PI/2; const eyeRig=new THREE.Group(); eyeRig.add(eyeBall); EYE.add(eyeRig);
const cornea=new THREE.Mesh(new THREE.SphereGeometry(0.62,64,32),new THREE.MeshPhysicalMaterial({color:0xffffff,roughness:0.0,transparent:true,opacity:0.12,clearcoat:1,clearcoatRoughness:0})); cornea.position.z=0.47; eyeRig.add(cornea);
const skinM=new THREE.MeshStandardMaterial({color:0x9a6a52,roughness:0.6}); const lidG=new THREE.SphereGeometry(1.06,96,48,0,Math.PI*2,0,Math.PI/2);
const lidTop=new THREE.Group(), lidBot=new THREE.Group(); { const a=new THREE.Mesh(lidG,skinM); lidTop.add(a); const b=new THREE.Mesh(lidG,skinM); b.rotation.x=Math.PI; lidBot.add(b); }
// lash line
{ const lm=new THREE.MeshStandardMaterial({color:0x1a0d08,roughness:0.8}); const lt=new THREE.Mesh(new THREE.TorusGeometry(1.06,0.03,8,96,Math.PI),lm); lt.rotation.x=Math.PI/2; lidTop.add(lt); const lb=lt.clone(); lb.rotation.set(Math.PI/2,0,0); lidBot.add(lb); }
EYE.add(lidTop,lidBot);
const face=new THREE.Mesh(new THREE.TorusGeometry(1.45,0.5,32,128),skinM); face.scale.set(1.35,0.95,0.7); face.position.z=0.1; EYE.add(face); const brow=new THREE.Mesh(new THREE.SphereGeometry(1.4,48,24),skinM); brow.scale.set(1.9,0.55,0.9); brow.position.set(0,1.55,0.05); EYE.add(brow);
const eyeLight=new THREE.PointLight(0xffc890,0,9,1.5); scene.add(eyeLight);
function eyeLids(open){ // open 1 = wide (lids rotated off the cornea), 0 = shut
  lidTop.rotation.x=-lerp(0.0,0.82,open); lidBot.rotation.x=lerp(0.0,0.62,open); }

// ---------------------------------------------------------------- the neural field (visual cortex)
const BRAIN=new THREE.Group(); BRAIN.position.set(120,0,0); scene.add(BRAIN);
const brainU={uT:{value:0},uB:{value:1},uH:{value:H}};
{ const N=90000, Rr=rng(31), pos=new Float32Array(N*3), sd=new Float32Array(N), col=new Float32Array(N*3);
  for(let i=0;i<N;i++){ const z=-Rr()*26, x=(Rr()-0.5)*7, y0=(Rr()-0.5)*9; const fold=0.55*Math.sin(x*1.7+z*0.35)+0.35*Math.sin(y0*1.3-z*0.5); const layer=Math.floor(Rr()*3)-1;
    pos[i*3]=x+0.2*Math.sin(z); pos[i*3+1]=y0+fold+layer*0.6; pos[i*3+2]=z+fold*0.5; sd[i]=Rr(); const g=Rr()<0.78; col[i*3]=g?1.0:0.36; col[i*3+1]=g?0.72:0.78; col[i*3+2]=g?0.38:0.75; }
  const geo=new THREE.BufferGeometry(); geo.setAttribute('position',new THREE.BufferAttribute(pos,3)); geo.setAttribute('seed',new THREE.BufferAttribute(sd,1)); geo.setAttribute('col',new THREE.BufferAttribute(col,3));
  const m=new THREE.Points(geo,new THREE.ShaderMaterial({uniforms:brainU,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,fog:false,
    vertexShader:`attribute float seed; attribute vec3 col; uniform float uT,uH,uB; varying vec3 vC; varying float vA;
      void main(){ vec3 p=position; float s=seed*6.283; p.x+=0.05*sin(uT*0.8+s); p.y+=0.05*cos(uT*0.6+s*1.3);
        float fire=pow(0.5+0.5*sin(uT*(1.5+seed*4.0)+s*3.0),6.0);
        vec4 mv=modelViewMatrix*vec4(p,1.0); gl_Position=projectionMatrix*mv; float sz=(0.028+0.045*fire)*uH/(-mv.z);
        gl_PointSize=clamp(sz,1.0,30.0); vC=col; vA=(0.25+0.9*fire)*uB*clamp(1.0-(-mv.z)/24.0,0.0,1.0)*min(1.0,sz/1.5); }`,
    fragmentShader:`varying vec3 vC; varying float vA; void main(){ float d=length(gl_PointCoord-0.5); float a=smoothstep(0.5,0.0,d); gl_FragColor=vec4(vC*a*a*vA*1.1,1.0); }`}));
  m.frustumCulled=false; BRAIN.add(m);
  // neurons: short glowing threads between nearby cells, a pulse runs along each
  const NL=14000, lp=new Float32Array(NL*6), la=new Float32Array(NL*2), ls=new Float32Array(NL*2);
  for(let i=0;i<NL;i++){ const a=Math.floor(Rr()*N); const ax=pos[a*3],ay=pos[a*3+1],az=pos[a*3+2]; const d=0.25+Rr()*0.6, th=Rr()*6.283, ph=(Rr()-0.5)*1.2;
    lp.set([ax,ay,az, ax+Math.cos(th)*Math.cos(ph)*d, ay+Math.sin(ph)*d, az+Math.sin(th)*Math.cos(ph)*d],i*6); la[i*2]=0; la[i*2+1]=1; ls[i*2]=ls[i*2+1]=Rr(); }
  const lg=new THREE.BufferGeometry(); lg.setAttribute('position',new THREE.BufferAttribute(lp,3)); lg.setAttribute('along',new THREE.BufferAttribute(la,1)); lg.setAttribute('seed',new THREE.BufferAttribute(ls,1));
  const lm=new THREE.LineSegments(lg,new THREE.ShaderMaterial({uniforms:brainU,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,fog:false,
    vertexShader:`attribute float along; attribute float seed; uniform float uT; varying float vL; varying float vS; varying float vD; void main(){ vL=along; vS=seed; vec4 mv=modelViewMatrix*vec4(position,1.0); vD=-mv.z; gl_Position=projectionMatrix*mv; }`,
    fragmentShader:`uniform float uT,uB; varying float vL; varying float vS; varying float vD; void main(){ float p=fract(uT*0.9+vS*7.0); float pulse=exp(-pow((vL-p)*7.0,2.0)); float fade=clamp(1.0-vD/20.0,0.0,1.0); gl_FragColor=vec4(vec3(1.0,0.74,0.4)*(0.05+0.6*pulse)*uB*fade,1.0); }`}));
  lm.frustumCulled=false; BRAIN.add(lm); }

// ---------------------------------------------------------------- the hero
const hero=createFigure(scene,{skin:0xf2e2c6,shirt:0x8aa0bc,pants:0x56648a,headR:0.152,hair:0x2a1c14});
const blinkHero=t=>lidAt(t)>0.45?1:0;
const sitP=(o={})=>({...R.P0,aL:1.5,aR:1.5,kL:1.5,kR:1.5,...o});
function heroPose(t,sh){ const id=sh.id; let J,face={mood:0.5,blink:blinkHero(t)},extra={};
  if(id==='read'||id==='read2'||id==='wide'){ // in the reading chair, book in both hands, page turn at 4 s
    const root=V(-1.6,0,-0.95), yaw=SLD.yawOf(V(0.35,0,0.94)); const br=0.012*Math.sin(t*1.4);
    const P=sitP({p:0.12+br,tilt:0.42,eL:1.0,eR:1.0}); const J0=R.skel(P,root,yaw); const f=J0.fwd, sd=V(-f.z,0,f.x);
    const bc=J0.neck.clone().addScaledVector(f,0.33).add(V(0,-0.2,0)); P.tL=bc.clone().addScaledVector(sd,0.1); P.wL=1; P.pL=V(-0.3,-0.7,0.6); P.tR=bc.clone().addScaledVector(sd,-0.1); P.wR=1; P.pR=V(-0.3,-0.7,-0.6);
    J=R.skel(P,root,yaw); extra.book={pos:bc,f}; face={mood:0.55,blink:blinkHero(t),fwd:J.fwd}; }
  else if(id==='window'){ const root=V(0.45,0,-1.45), yaw=SLD.yawOf(V(0.05,0,-1)); const P={...R.P0,p:0.02,tilt:-0.1}; const J0=R.skel(P,root,yaw); const mp=J0.neck.clone().addScaledVector(J0.fwd,0.22).add(V(0.0,-0.22+0.12*sstep(6.3,6.6,t)*(1-sstep(6.75,6.95,t)),0)).addScaledVector(V(-J0.fwd.z,0,J0.fwd.x),-0.12);
    P.tR=mp; P.wR=1; P.pR=V(-0.3,-0.7,-0.5); J=R.skel(P,root,yaw); extra.mug=J.hR.clone(); face={mood:0.6,blink:blinkHero(t),fwd:J.fwd}; }
  else if(id==='desk'){ const root=V(1.85,0,-1.1), yaw=SLD.yawOf(V(0,0,-1)); const P=sitP({p:0.3,tilt:0.25,eL:1.0,eR:1.0}); const ty=t*13;
    P.tL=V(1.75+0.0,0.82+Math.max(0,Math.sin(ty))*0.012,-1.72); P.wL=1; P.pL=V(-0.3,-0.7,0.5); P.tR=V(1.98,0.82+Math.max(0,Math.sin(ty+2))*0.012,-1.72); P.wR=1; P.pR=V(-0.3,-0.7,-0.5); J=R.skel(P,root,yaw); face={mood:0.45,blink:blinkHero(t),fwd:J.fwd}; }
  else if(id==='bed'){ const root=V(2.2,0,-0.4), yaw=SLD.yawOf(V(-0.9,0,0.45)); const P=sitP({p:0.4,tilt:0.55,eL:1.2,eR:1.2,dy:0.05}); const J0=R.skel(P,root,yaw); const pp=J0.neck.clone().addScaledVector(J0.fwd,0.28).add(V(0,-0.28,0));
    P.tL=pp.clone(); P.wL=1; P.pL=V(-0.3,-0.7,0.5); P.tR=pp.clone().add(V(0,0.02,0)); P.wR=1; P.pR=V(-0.3,-0.7,-0.5); J=R.skel(P,root,yaw); extra.phone={pos:pp.clone().add(V(0,0.04,0)),f:J.fwd}; face={mood:0.4,blink:blinkHero(t),fwd:J.fwd}; }
  else if(id==='mirror'){ const root=V(-0.68,0,-1.3), yaw=SLD.yawOf(V(0.05,0,-1)); const lean=sstep(16.2,17.4,t); const P={...R.P0,p:0.04+0.06*lean,tilt:0.0}; J=R.skel(P,root,yaw); face={mood:0.5,blink:0,fwd:J.fwd,wide:0.4*lean}; }   // the mirror never shows a blink
  else return null;
  return {J,face,extra}; }

// ---------------------------------------------------------------- lights per time of day
const TOD={ night:{sky:0x0b1220,city:0.85,key:[-2.3,1.9,-1.2,-1.6,0.6,-0.9,9],a:[-2.35,1.5,-1.5,0xffa458,3.0],b:[1.85,1.2,-1.7,0x9fc4ff,0.0],fill:0.35,hemi:0.22,bg:0x141923},
  morning:{sky:0x8fb4d8,city:0.25,key:[0.55,2.2,-3.2,0.5,0.6,0.5,26],a:[-2.35,1.5,-1.5,0xffa458,0.0],b:[0.55,1.7,-1.8,0xbfd8ff,2.2],fill:0.9,hemi:0.55,bg:0x1d2633},
  noon:{sky:0xd8e4ee,city:0.1,key:[0.55,2.4,-3.2,1.3,0.6,-0.8,30],a:[-2.35,1.5,-1.5,0xffa458,0.0],b:[1.85,1.2,-1.6,0xbfd8ff,1.6],fill:1.0,hemi:0.6,bg:0x222b36},
  evening:{sky:0xd8784a,city:0.5,key:[0.55,2.2,-3.2,2.2,0.6,-0.3,22],a:[-2.35,1.5,-1.5,0xffa458,1.4],b:[2.2,1.0,-0.3,0xbcd4ff,0.6],fill:0.6,hemi:0.4,bg:0x221a1a} };
function applyLights(tod){ const L=TOD[tod]; const k=L.key; ST.key.position.set(k[0],k[1],k[2]); ST.key.target.position.set(k[3],k[4],k[5]); ST.key.intensity=k[6]; ST.key.angle=1.1; ST.key.color.setHex(tod==='night'?0xffb066:(tod==='evening'?0xffa060:0xdce8ff));
  ST.lampA.position.set(L.a[0],L.a[1],L.a[2]); ST.lampA.color.setHex(L.a[3]); ST.lampA.intensity=L.a[4]; ST.lampB.position.set(L.b[0],L.b[1],L.b[2]); ST.lampB.color.setHex(L.b[3]); ST.lampB.intensity=L.b[4];
  ST.fill.position.set(0.8,1.8,4.2); ST.fill.color.setHex(0x5873b0); ST.fill.intensity=L.fill; ST.hemi.color.setHex(0x3a4c78); ST.hemi.groundColor.setHex(0x241c16); ST.hemi.intensity=L.hemi; ST.rim.intensity=0.35;
  sky.color.setHex(L.sky); room.userData.city.material.opacity=L.city; scene.background.setHex(L.bg); scene.fog.color.setHex(L.bg); scene.fog.near=7; scene.fog.far=24;
  screenM.emissiveIntensity=tod==='noon'?1.4:0.0; }
function faceLight(id){ if(id==='read'||id==='read2'||id==='wide'){ ST.lampB.position.set(-1.15,1.35,-0.35); ST.lampB.color.setHex(0xffc890); ST.lampB.intensity=0.9; } if(id==='mirror'){ ST.lampB.position.set(-0.2,2.3,-1.2); ST.lampB.color.setHex(0xffc080); ST.lampB.intensity=0.75; ST.lampA.intensity*=0.6; } }

// ---------------------------------------------------------------- cameras: [pos0, look0, pos1, look1]
const CAMS={ read:[[0.5,1.45,4.9],[-1.45,0.95,-0.95],[-0.35,1.25,2.7],[-1.55,0.98,-0.95]],
  window:[[1.9,1.45,2.3],[0.45,1.45,-1.7],[1.65,1.45,1.95],[0.45,1.45,-1.7]],
  desk:[[3.2,1.55,1.5],[1.8,1.0,-1.5],[2.95,1.5,1.2],[1.8,1.0,-1.5]],
  bed:[[0.3,1.35,2.6],[2.3,0.8,-0.5],[0.55,1.32,2.3],[2.3,0.8,-0.5]],
  read2:[[-0.55,1.75,1.5],[-1.6,1.18,-0.95],[-0.7,1.7,1.25],[-1.6,1.2,-0.95]],
  wide:[[-0.5,1.6,5.0],[-0.9,1.0,-1.0],[-0.4,1.75,6.2],[-0.8,1.05,-1.0]],
  mirror:[[-0.2,1.64,1.0],[MIR.x,MIR.y,-2.15],[-0.38,1.6,0.15],[MIR.x,MIR.y+0.02,-2.15]] };

// ---------------------------------------------------------------- one frame
function setT(t){ const sh=shotAt(t); const u=sm5(clamp((t-sh.t0)/(sh.t1-sh.t0)));
  room.visible=!!sh.tod; EYE.visible=sh.id==='eye'; BRAIN.visible=sh.id==='brain'; ST.grade.uniforms.uT.value=t; ST.grade.uniforms.uFlash.value=0;
  let lid=lidAt(t); if(sh.id==='eye'||sh.id==='brain') lid=0; ST.grade.uniforms.uLid.value=lid;
  rbook.visible=mug.visible=phone.visible=false; phoneLight.intensity=0; eyeLight.intensity=0;
  if(sh.tod){ applyLights(sh.tod); faceLight(sh.id); mirror.visible=sh.id==='mirror'; fakeMirror.visible=!mirror.visible;
    const hp=heroPose(t,sh); hero.setVisible(true); hero.pose(hp.J,hp.face,{belt:1});
    const e=hp.extra; if(e.book){ rbook.visible=true; rbook.position.copy(e.book.pos); rbook.lookAt(e.book.pos.clone().add(e.book.f.clone().multiplyScalar(-1)).add(V(0,0.9,0))); rbook.rotateX(-Math.PI/2); }
    if(e.mug){ mug.visible=true; mug.position.copy(e.mug).add(V(0,0.03,0)); }
    if(e.phone){ phone.visible=true; phone.position.copy(e.phone.pos); phone.lookAt(e.phone.pos.clone().addScaledVector(e.phone.f,-1).add(V(0,0.6,0))); phoneLight.position.copy(e.phone.pos).addScaledVector(e.phone.f,-0.25); phoneLight.intensity=0.5; }
    const cm=CAMS[sh.id]; let pos=V(...cm[0]).lerp(V(...cm[2]),u), look=V(...cm[1]).lerp(V(...cm[3]),u);
    ST.cam.fov=sh.id==='mirror'?30:36; ST.cam.updateProjectionMatrix(); ST.cam.position.copy(pos); ST.cam.lookAt(look); return; }
  hero.setVisible(false); mirror.visible=false; scene.background.setHex(0x0c0e14); scene.fog.color.setHex(0x0c0e14); scene.fog.near=30; scene.fog.far=90;
  if(sh.id==='eye'){ // macro: the eye looks back, blinks once (12.85), then we push into the pupil
    ST.key.position.set(57.8,2.8,5.0); ST.key.target.position.set(60,0,0); ST.key.intensity=26; ST.key.color.setHex(0xffb870); ST.key.angle=0.6;
    ST.lampA.position.set(62.5,1.2,3.0); ST.lampA.color.setHex(0x9fc4ff); ST.lampA.intensity=1.6; ST.lampB.intensity=0; ST.fill.intensity=0.2; ST.hemi.intensity=0.15; eyeLight.position.set(59.0,1.0,3.2); eyeLight.intensity=2.2;
    const b=t-12.85; const shut=b<0||b>0.34?0:(b<0.09?sm5(b/0.09):(b<0.16?1:1-sm5((b-0.16)/0.18))); eyeLids(1-shut);
    eyeRig.rotation.y=0.05*Math.sin(t*2.1); eyeRig.rotation.x=0.035*Math.sin(t*1.7);
    const pu=sstep(13.15,13.8,t); const z=lerp(6.6,1.16,Math.pow(pu,1.5)); ST.cam.fov=lerp(32,26,pu); ST.cam.updateProjectionMatrix(); cornea.visible=pu<0.8; ST.cam.position.set(60,0.0+0.15*(1-pu),z); ST.cam.lookAt(60,0,0); return; }
  // brain: flying through the field; activity dims twice in sync with blinks (14.55, 15.45)
  ST.key.intensity=0; ST.lampA.intensity=0; ST.lampB.intensity=0; ST.fill.intensity=0; ST.hemi.intensity=0.05;
  const dip=b=>{ const x=t-b; return x<-0.05||x>0.35?0:(x<0?sm5((x+0.05)/0.05):(x<0.15?1:1-sm5((x-0.15)/0.2))); };
  brainU.uT.value=t; brainU.uB.value=sstep(13.8,14.1,t)*(1-0.88*Math.max(dip(14.55),dip(15.45)));
  const v=(t-13.8)/2.2; ST.cam.fov=40; ST.cam.updateProjectionMatrix(); ST.cam.position.set(120+0.3*Math.sin(v*2),0.2*Math.cos(v*1.5),3.5-v*6.5); ST.cam.lookAt(120+0.2*Math.sin(v*2+0.5),0,-20); }
window.renderAt=(t,K=3)=>{ const sh=shotAt(t); const cut=SHOTS.some(s=>s.t0>0&&Math.abs(t-s.t0)<1/30); return ST.renderAt(setT,t,cut?K:K,{t0:sh.t0,t1:sh.t1,shutter:1/60}); };
window.events={DUR,BLINKS,SHOTS}; window.ready=true;
