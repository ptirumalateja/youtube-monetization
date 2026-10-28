// You Were Blind for 20 Minutes Today, Slow Light Dark look (V2, 28 Oct 2026): the void, one gold lamp beam with dust, a soft-mirror floor and
// the cream free-flowing stickman (sld.js). Each moment of his day is staged in the same pool of light. Screen-space eyelids (grade uLid)
// close on every blink; his two eye dots close with them, except in the mirror. Then an eye macro and a neural field.
// renderAt(t) is pure. Units are metres. Pool at the origin, eye at x=60, neural field at x=120.
import * as THREE from 'three';
import {Reflector} from 'three/addons/objects/Reflector.js';
import * as SLD from './sld.js';
import * as SETS from './sets.js';
import {buildEye} from './eye.js';
const {V,clamp,sstep,lerp,sm5,PAL}=SLD;
const {M,B,C,S:SPH,P:PLN,canvasTex,rng}=SETS;
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960;
const DUR=19.0;
const ST=SLD.createStage({W,H}); const scene=ST.scene; const R=SLD.createRig(scene);

// ---------------------------------------------------------------- blinks (screen lids) and the shot list
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

// ---------------------------------------------------------------- the props, each staged in the pool of light (dark materials, faint rim)
const IRONM=M(0x3a3b40,{r:0.55,m:0.3}), DARKW=M(0x2a2420,{r:0.7}), FAB=M(0x4a3a36,{r:0.95});
const G={}; const mk=id=>{ const g=new THREE.Group(); g.visible=false; scene.add(g); G[id]=g; return g; };
{ const ch=mk('chair'); B(ch,0.78,0.42,0.74,FAB,0,0.21,0,{round:0.08}); B(ch,0.78,0.62,0.18,FAB,-0.02,0.64,-0.3,{round:0.08}); for(const sx of [-1,1]) B(ch,0.16,0.3,0.74,FAB,sx*0.39,0.52,0,{round:0.06}); ch.position.set(0.05,0,-0.05); ch.rotation.y=0.3; }
const paneM=new THREE.MeshBasicMaterial({color:0xbfd6f0,fog:false});
{ const w=mk('window'); B(w,1.3,1.6,0.06,DARKW,0,0,0); PLN(w,1.18,1.48,paneM,0,0,0.035); B(w,0.035,1.6,0.07,DARKW,0,0,0.04); B(w,1.3,0.035,0.07,DARKW,0,0,0.04); w.position.set(0,1.55,-1.45); }
const winLight=new THREE.SpotLight(0xcfe0ff,0,8,0.7,0.6,1.2); winLight.position.set(0,1.6,-1.8); winLight.target.position.set(0,0.9,1.5); scene.add(winLight,winLight.target);
const screenM=new THREE.MeshBasicMaterial({color:0xbcd4ff,fog:false});
{ const dk=mk('desk'); B(dk,1.2,0.05,0.6,DARKW,0,0.76,0,{round:0.01}); for(const [x,z] of [[-0.55,-0.25],[0.55,-0.25],[-0.55,0.25],[0.55,0.25]]) B(dk,0.04,0.76,0.04,IRONM,x,0.38,z);
  const lt=new THREE.Group(); B(lt,0.36,0.015,0.25,M(0x8a8c92,{m:0.6,r:0.35}),0,0,0); const lid=new THREE.Group(); B(lid,0.36,0.24,0.012,M(0x8a8c92,{m:0.6,r:0.35}),0,0.12,0); PLN(lid,0.33,0.21,screenM,0,0.12,0.007); lid.position.set(0,0.008,-0.12); lid.rotation.x=-0.25; lt.add(lid); lt.position.set(0,0.79,-0.02); lt.rotation.y=Math.PI; dk.add(lt);
  C(dk,0.045,0.04,0.1,M(0xd9c8a8,{r:0.4}),0.42,0.83,0.05); B(dk,0.46,0.05,0.44,DARKW,0,0.47,0.62); B(dk,0.46,0.5,0.05,DARKW,0,0.75,0.84); for(const [x,z] of [[-0.2,0.43],[0.2,0.43],[-0.2,0.81],[0.2,0.81]]) B(dk,0.04,0.47,0.04,IRONM,x,0.235,z);
  dk.position.set(0,0,-0.45); }
const lapLight=new THREE.PointLight(0xbcd4ff,0,2.2,2); scene.add(lapLight);
{ const bd=mk('bed'); B(bd,2.0,0.3,1.3,DARKW,0,0.15,0,{round:0.03}); B(bd,1.9,0.2,1.2,M(0xd8d2c6,{r:0.9}),0,0.4,0,{round:0.07}); B(bd,1.2,0.12,1.24,M(0x3a4258,{r:0.95}),0.35,0.54,0,{round:0.06}); B(bd,0.4,0.15,0.8,M(0xe8e2d6,{r:0.95}),-0.75,0.56,0,{round:0.07}); bd.position.set(0.05,0,-0.35); }
const MIR={w:0.62,h:1.5}; const mirG=mk('mirror'); B(mirG,MIR.w+0.1,MIR.h+0.1,0.05,M(0x8a6a3a,{m:0.6,r:0.35}),0,0,-0.03); for(const sx of [-1,1]) B(mirG,0.04,0.5,0.04,IRONM,sx*0.25,-0.95,-0.15,{rx:0.4});
const mirror=new Reflector(new THREE.PlaneGeometry(MIR.w,MIR.h),{textureWidth:Math.round(W*0.7),textureHeight:Math.round(W*0.7*MIR.h/MIR.w),color:0xb8b4ac,clipBias:0.003}); mirG.add(mirror); mirG.position.set(0,1.05,-1.55);
// distant furniture silhouettes at the edge of the light, so the void has depth (shelf, lamp stand, plant)
{ const bg=mk('bg'); bg.visible=true; B(bg,1.1,1.9,0.35,M(0x1c1c20,{r:0.9}),-2.6,0.95,-3.2); B(bg,0.9,0.04,0.25,M(0x26262a),2.4,1.6,-3.4); B(bg,0.9,0.04,0.25,M(0x26262a),2.4,1.1,-3.4); C(bg,0.12,0.09,0.22,M(0x2a2420),2.9,0.11,-2.6); }

// ---------------------------------------------------------------- small props: book, mug, phone
const rbook=new THREE.Group(); { const pg=M(0xf4efe6,{r:0.9}), cv=M(0x5a4a3a,{r:0.7}); for(const sx of [-1,1]){ const h=new THREE.Group(); B(h,0.13,0.012,0.19,cv,sx*0.065,0,0); B(h,0.12,0.02,0.18,pg,sx*0.062,0.012,0); h.rotation.z=-sx*0.28; rbook.add(h); } } scene.add(rbook);
const mug=new THREE.Group(); C(mug,0.045,0.04,0.1,M(0xe8e1d4,{r:0.4}),0,0,0); scene.add(mug);
const phone=new THREE.Group(); { B(phone,0.075,0.15,0.01,M(0x0d0e12,{r:0.3,m:0.4}),0,0,0,{round:0.01}); B(phone,0.067,0.138,0.004,new THREE.MeshBasicMaterial({color:0xbcd4ff}),0,0,0.006,{cast:false}); } phone.scale.setScalar(1.4); scene.add(phone); const phoneLight=new THREE.PointLight(0xbcd4ff,0,2.2,2); scene.add(phoneLight);

// ---------------------------------------------------------------- the hero: cream free-flowing stickman with two eye dots
const hero=R.makeFig(PAL.CREAM,'hero',{rim:0.16,lift:0.07});
const eyeDotM=new THREE.MeshStandardMaterial({color:0x14151a,roughness:0.4}); const eyes=[0,1].map(()=>{ const e=new THREE.Mesh(new THREE.SphereGeometry(1,16,12),eyeDotM); e.frustumCulled=false; scene.add(e); return e; });
function placeEyes(J,shut){ const hd=J.head, up=J.head.clone().sub(J.neck).normalize(); let f=J.fwd.clone().addScaledVector(up,-J.fwd.dot(up)).normalize(); const sd=f.clone().cross(up).normalize();
  eyes.forEach((e,i)=>{ e.position.copy(hd).addScaledVector(f,0.118).addScaledVector(sd,(i?1:-1)*0.046).addScaledVector(up,0.018); e.scale.set(0.017,0.024*(shut?0.12:1),0.012); e.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(sd,up,f)); e.visible=true; }); }
const EYE=new THREE.Group(); EYE.position.set(60,0,0); scene.add(EYE);
const irisTex=canvasTex(2048,1024,(g,w,h)=>{ // equirect with the iris around the top pole (v=0); the ball is turned so that pole faces the camera
  g.fillStyle='#eadfd2'; g.fillRect(0,0,w,h); const Rr=rng(8); g.strokeStyle='rgba(170,50,45,0.28)'; g.lineWidth=2; for(let i=0;i<90;i++){ let x=Rr()*w, y=h*(0.3+Rr()*0.45); g.beginPath(); g.moveTo(x,y); for(let k=0;k<7;k++){ x+=(Rr()-0.5)*50; y-=Rr()*28; g.lineTo(x,y); } g.stroke(); }
  const rows=r=>r/Math.PI*h; const iR=rows(0.56), pR=rows(0.2), lR=rows(0.6);
  const gr=g.createLinearGradient(0,0,0,lR); gr.addColorStop(0,'#050403'); gr.addColorStop(pR/lR*0.98,'#050403'); gr.addColorStop(pR/lR*1.02,'#5a3412'); gr.addColorStop(0.55,'#b07a30'); gr.addColorStop(0.8,'#6a4218'); gr.addColorStop(iR/lR,'#24140a'); gr.addColorStop(1,'rgba(234,223,210,1)'); g.fillStyle=gr; g.fillRect(0,0,w,lR);
  for(let i=0;i<2600;i++){ const x=Rr()*w; g.strokeStyle=`rgba(${Rr()<0.55?'245,200,120':'30,16,8'},${0.08+Rr()*0.22})`; g.lineWidth=1+Rr()*4; g.beginPath(); g.moveTo(x,pR+2+Rr()*6); g.lineTo(x+(Rr()-0.5)*14,pR+(iR-pR)*(0.5+Rr()*0.5)); g.stroke(); }
  g.fillStyle='#050403'; g.fillRect(0,0,w,pR); });
const eyeM=new THREE.MeshPhysicalMaterial({map:irisTex,roughness:0.3,clearcoat:1,clearcoatRoughness:0.04});
const eyeBall=new THREE.Mesh(new THREE.SphereGeometry(1,128,96),eyeM); eyeBall.rotation.x=Math.PI/2; const eyeRig=new THREE.Group(); eyeRig.add(eyeBall);
const cornea=new THREE.Mesh(new THREE.SphereGeometry(0.62,64,32),new THREE.MeshPhysicalMaterial({color:0xffffff,roughness:0.0,transparent:true,opacity:0.12,clearcoat:1,clearcoatRoughness:0})); cornea.position.z=0.47; eyeRig.add(cornea);
const skinM=new THREE.MeshStandardMaterial({color:0x9a6a52,roughness:0.6}); const lidG=new THREE.SphereGeometry(1.06,96,48,0,Math.PI*2,0,Math.PI/2);
const lidTop=new THREE.Group(), lidBot=new THREE.Group(); { const a=new THREE.Mesh(lidG,skinM); lidTop.add(a); const b=new THREE.Mesh(lidG,skinM); b.rotation.x=Math.PI; lidBot.add(b); }
// lash line
{ const lm=new THREE.MeshStandardMaterial({color:0x1a0d08,roughness:0.8}); const lt=new THREE.Mesh(new THREE.TorusGeometry(1.06,0.03,8,96,Math.PI),lm); lt.rotation.x=Math.PI/2; lidTop.add(lt); const lb=lt.clone(); lb.rotation.set(Math.PI/2,0,0); lidBot.add(lb); }
// V2.1: the old stylised eye stays built (shared helpers) but is replaced on screen by eye.js

const face=new THREE.Mesh(new THREE.TorusGeometry(1.45,0.5,32,128),skinM); face.scale.set(1.35,0.95,0.7); face.position.z=0.1; const brow=new THREE.Mesh(new THREE.SphereGeometry(1.4,48,24),skinM); brow.scale.set(1.9,0.55,0.9); brow.position.set(0,1.55,0.05);
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
  lm.frustumCulled=false; BRAIN.add(lm); }const eyeSpot=new THREE.SpotLight(0xffc890,0,14,0.5,0.7,1.2); eyeSpot.position.set(57.6,3.0,5.0); eyeSpot.target.position.set(60,0,0); scene.add(eyeSpot,eyeSpot.target);
const EYEM=buildEye(ST.renderer); EYE.add(EYEM.group);

// ---------------------------------------------------------------- hero poses, all inside the pool of light
const sitP=(o={})=>({...R.P0,aL:1.5,aR:1.5,kL:1.5,kR:1.5,...o});
const breathe=t=>0.014*Math.sin(2*Math.PI*0.23*t);
function heroPose(t,id){ const ex={}; let J,P,root,yaw;
  if(id==='read'||id==='read2'||id==='wide'){ root=V(0.0,0,0.05); yaw=SLD.yawOf(V(0.3,0,0.95)); P=sitP({p:0.14+breathe(t),tilt:0.42+0.03*Math.sin(t*0.9),hy:0.06*Math.sin(t*0.5),eL:1.0,eR:1.0});
    const J0=R.skel(P,root,yaw); const f=J0.fwd, sd=V(-f.z,0,f.x); const bc=J0.neck.clone().addScaledVector(f,0.33).add(V(0,-0.2,0));
    if(t>3.85&&t<4.3){ bc.addScaledVector(sd,0.04*Math.sin(Math.PI*(t-3.85)/0.45)); }    // page turn
    P.tL=bc.clone().addScaledVector(sd,0.1); P.wL=1; P.pL=V(-0.3,-0.7,0.6); P.tR=bc.clone().addScaledVector(sd,-0.1); P.wR=1; P.pR=V(-0.3,-0.7,-0.6); J=R.skel(P,root,yaw); ex.book={pos:bc,f}; }
  else if(id==='window'){ root=V(0,0,-0.7); yaw=SLD.yawOf(V(0.05,0,-1)); P={...R.P0,p:0.03+breathe(t),tilt:-0.12}; const J0=R.skel(P,root,yaw);
    const sip=sstep(6.3,6.6,t)*(1-sstep(6.75,6.95,t)); const mp=J0.neck.clone().addScaledVector(J0.fwd,0.24).add(V(0,-0.24+0.13*sip,0)).addScaledVector(V(-J0.fwd.z,0,J0.fwd.x),-0.13);
    P.tR=mp; P.wR=1; P.pR=V(-0.3,-0.7,-0.5); J=R.skel(P,root,yaw); ex.mug=J.hR.clone(); }
  else if(id==='desk'){ root=V(0,0,0.17); yaw=SLD.yawOf(V(0,0,-1)); P=sitP({p:0.3+breathe(t),tilt:0.25,eL:1.0,eR:1.0}); const ty=t*13;
    P.tL=V(-0.1,0.83+Math.max(0,Math.sin(ty))*0.014,-0.36); P.wL=1; P.pL=V(-0.3,-0.7,0.5); P.tR=V(0.12,0.83+Math.max(0,Math.sin(ty+2))*0.014,-0.36); P.wR=1; P.pR=V(-0.3,-0.7,-0.5); J=R.skel(P,root,yaw); }
  else if(id==='bed'){ root=V(0.1,0,0.42); yaw=SLD.yawOf(V(0.2,0,1)); P=sitP({p:0.42+breathe(t),tilt:0.55,eL:1.2,eR:1.2,dy:0.05}); const J0=R.skel(P,root,yaw); const pp=J0.neck.clone().addScaledVector(J0.fwd,0.28).add(V(0,-0.28,0));
    P.tL=pp.clone(); P.wL=1; P.pL=V(-0.3,-0.7,0.5); P.tR=pp.clone().add(V(0,0.02,0)); P.wR=1; P.pR=V(-0.3,-0.7,-0.5); J=R.skel(P,root,yaw); ex.phone={pos:pp.clone().add(V(0,0.04,0)),f:J.fwd}; }
  else { root=V(0,0,-0.8); yaw=SLD.yawOf(V(0.03,0,-1)); const lean=sstep(16.2,17.4,t); P={...R.P0,p:0.04+0.07*lean+breathe(t),tilt:0.0,hy:0.08*Math.sin(t*0.7)}; J=R.skel(P,root,yaw); }
  return {J,ex}; }

// ---------------------------------------------------------------- light per time of day (the lamp changes colour; window / screen / phone add their own)
const TOD={ night:{col:PAL.GOLD,k:1.0}, morning:{col:0xd8e4f6,k:0.55}, noon:{col:0xfff0d8,k:0.55}, evening:{col:0xff9a52,k:0.9} };
const CAMS={ read:[[0.6,1.35,7.6],[0,0.8,0],[0.2,1.2,5.3],[0,1.0,0]],
  window:[[0.95,1.35,3.9],[0,1.25,-1.0],[0.75,1.35,3.4],[0,1.25,-1.0]],
  desk:[[2.4,1.55,3.6],[0,0.85,-0.2],[2.15,1.5,3.2],[0,0.85,-0.2]],
  bed:[[-1.7,1.25,4.6],[0.1,0.7,0.1],[-1.4,1.22,4.2],[0.1,0.7,0.1]],
  read2:[[-0.45,1.95,3.9],[0,1.1,0.05],[-0.55,1.88,3.45],[0,1.12,0.05]],
  wide:[[0,1.9,7.4],[0,1.0,0],[0,2.1,8.8],[0,1.0,0]],
  mirror:[[1.9,1.5,6.2],[-0.1,1.1,-1.1],[1.5,1.45,4.9],[-0.1,1.15,-1.2]] };
const PROPS={read:'chair',read2:'chair',wide:'chair',window:'window',desk:'desk',bed:'bed',mirror:'mirror'};

function setT(t){ const sh=shotAt(t); const id=sh.id; const u=sm5(clamp((t-sh.t0)/(sh.t1-sh.t0)));
  ST.GU.uLid.value=(id==='eye'||id==='brain')?0:lidAt(t);
  for(const k of ['chair','window','desk','bed','mirror']) G[k].visible=(PROPS[id]===k);
  rbook.visible=mug.visible=phone.visible=false; phoneLight.intensity=0; lapLight.intensity=0; winLight.intensity=0; eyeLight.intensity=0; eyeSpot.intensity=0;
  EYE.visible=id==='eye'; BRAIN.visible=id==='brain';
  if(sh.tod){ const L=TOD[sh.tod]; scene.fog.density=0.085; ST.spot.color.setHex(L.col); ST.beamU.uCol.value.setHex(L.col); ST.tick(t,0); ST.spot.intensity*=L.k; ST.beamU.uI.value*=L.k;
    if(id==='window') winLight.intensity=6; if(id==='desk'){ lapLight.position.set(0,0.95,-0.35); lapLight.intensity=0.6; }
    const hp=heroPose(t,id); hero.all.forEach(m=>m.visible=true); R.poseFig(hero,hp.J); placeEyes(hp.J,id==='mirror'?false:lidAt(t)>0.45);
    const e=hp.ex; if(e.book){ rbook.visible=true; rbook.position.copy(e.book.pos); rbook.lookAt(e.book.pos.clone().add(e.book.f.clone().multiplyScalar(-1)).add(V(0,0.9,0))); rbook.rotateX(-Math.PI/2); }
    if(e.mug){ mug.visible=true; mug.position.copy(e.mug).add(V(0,0.03,0)); }
    if(e.phone){ phone.visible=true; phone.position.copy(e.phone.pos); phone.lookAt(e.phone.pos.clone().addScaledVector(e.phone.f,-1).add(V(0,0.6,0))); phoneLight.position.copy(e.phone.pos).addScaledVector(e.phone.f,0.25); phoneLight.intensity=0.35; }
    const cm=CAMS[id]; const pos=V(...cm[0]).lerp(V(...cm[2]),u), look=V(...cm[1]).lerp(V(...cm[3]),u);
    ST.cam.fov=38; ST.cam.updateProjectionMatrix(); ST.cam.position.copy(pos); ST.cam.lookAt(look); return; }
  hero.all.forEach(m=>m.visible=false); eyes.forEach(e=>e.visible=false); scene.fog.density=0.012; ST.tick(t,0);
  if(id==='eye'){ eyeSpot.intensity=26; eyeLight.position.set(62.2,0.8,3.2); eyeLight.color.setHex(0x9fb2d6); eyeLight.intensity=0.8;
    const b=t-12.85; const shut=b<0||b>0.34?0:(b<0.09?sm5(b/0.09):(b<0.16?1:1-sm5((b-0.16)/0.18))); EYEM.update(1-shut,t);
    const pu=sstep(13.15,13.8,t); const z=lerp(+(window.EYEZ||9.5),1.16,Math.pow(pu,1.5)); ST.cam.fov=lerp(30,26,pu); ST.cam.updateProjectionMatrix(); EYEM.cornea.visible=pu<0.55&&shut<0.6; ST.cam.position.set(60,0.15*(1-pu),z); ST.cam.lookAt(60,0,0); return; }
  const dip=b=>{ const x=t-b; return x<-0.05||x>0.35?0:(x<0?sm5((x+0.05)/0.05):(x<0.15?1:1-sm5((x-0.15)/0.2))); };
  brainU.uT.value=t; brainU.uB.value=sstep(13.8,14.1,t)*(1-0.88*Math.max(dip(14.55),dip(15.45)));
  const v=(t-13.8)/2.2; ST.cam.fov=40; ST.cam.updateProjectionMatrix(); ST.cam.position.set(120+0.3*Math.sin(v*2),0.2*Math.cos(v*1.5),3.5-v*6.5); ST.cam.lookAt(120+0.2*Math.sin(v*2+0.5),0,-20); }
window.renderAt=(t,K=3)=>{ const sh=shotAt(t); return ST.renderAt(setT,t,K,{t0:sh.t0,t1:sh.t1,shutter:1/60}); };
window.events={DUR,BLINKS,SHOTS}; window.ready=true;
