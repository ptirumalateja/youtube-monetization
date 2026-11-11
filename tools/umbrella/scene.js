// Checkers vs Chess, the umbrella reel (Slow Light Dark). Remake of the neuronvisuals "Some people play checkers.
// Others play chess." reel, same composition, sizes, beats and length (11.8 s), rebuilt in our look.
//
// Beats (ref timing): 0-3.0 rain. The cream man walks with his umbrella held upside down, a bowl filling with rain; the
// grey man walks behind him under a normal umbrella, points and laughs (HA HA). 3.0 lightning, the clouds clear,
// 3.75 the sun. 3.9-5.0 grey man shuts his umbrella and throws it away behind him; the wet ground dries and cracks.
// 6.0-6.9 the cream man fills a cup from the umbrella's tip, 7.0-8.0 drinks. Grey man hunches in the heat, wipes his
// brow, 8.0 drops to his knees, crawls to his umbrella and 9.0 holds it up, upside down, under an empty sky. Fade.
//
// renderAt(t) is pure (no state between frames), so frames can render in parallel workers.
import * as THREE from 'three';
import * as SLD from './sld.js';
const {V,clamp,sstep,lerp,PAL,rng,yawOf,keys,rotY}=SLD;
const TL=await (await fetch('./timeline.json')).json();
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960, DUR=TL.duration;
const QK=(n,d)=>+(q.get(n)??d);

// ---------------------------------------------------------------- layout (metres; floor y = 0; camera on +z)
const HX=-0.42, HZ=0.45, GX=0.56, GZ=-0.6;            // hero (cream) and the grey man
const F=V(-1,0,0.32).normalize(), YAW=yawOf(F);        // both walk toward camera-left
const SL=rotY(V(0,0,1),YAW), SR=SL.clone().negate();   // their left (far) side, right (camera) side
const F2=V(1,0,0.25).normalize(), YAW2=yawOf(F2);       // grey man turned toward his thrown umbrella
const CAM={x:QK('cx',-0.28),y:QK('cy',3.05),z:QK('cz',9.1),tx:QK('tx',-0.28),ty:QK('ty',1.62),fov:QK('fov',36)};

// ---------------------------------------------------------------- stage
const LAMP=V(0.25,7.2,1.2), LAMP_T=V(0.25,0,-0.05);
const S=SLD.createStage({W,H,lamp:LAMP,lampTarget:LAMP_T,cone:0.25,spot:QK('spot',70),beam:0.02,fov:CAM.fov,motes:1400,vig:0.3});
const {scene,cam}=S;
const BG_RAIN=new THREE.Color(0x07090d), BG_SUN=new THREE.Color(0x0e0807);
scene.background=BG_RAIN.clone(); scene.fog=new THREE.FogExp2(0x07090d,0.075);
S.renderer.toneMappingExposure=1.05;
S.floor.scale.set(2,2,1); S.refl.scale.set(2,2,1);
const hemi=new THREE.HemisphereLight(0x8a96b4,0x241c16,0.45); scene.add(hemi);
const key=new THREE.DirectionalLight(0xfff0dc,0.9); key.position.set(-3.5,6.0,7.5); key.target.position.set(0.2,1.0,0);
key.castShadow=true; key.shadow.mapSize.set(2048,2048); Object.assign(key.shadow.camera,{left:-4,right:4,top:5,bottom:-1,near:1,far:24}); key.shadow.bias=-0.0003; key.shadow.normalBias=0.02;
scene.add(key,key.target);
const sunRim=new THREE.DirectionalLight(0xff5a32,0); sunRim.position.set(0.3,5,-9); sunRim.target.position.set(0.2,1,0); scene.add(sunRim,sunRim.target);
const flashL=new THREE.DirectionalLight(0xdfe8ff,0); flashL.position.set(2,8,-3); scene.add(flashL);

const R=SLD.createRig(scene);
const hero=R.makeFig(PAL.CREAM,'hero',{rim:0.2,lift:0.1});
const grey=R.makeFig(0x9a9ea8,'grey',{rim:0.16,lift:0.05});

// ---------------------------------------------------------------- materials / textures
const ribTex=(()=>{ const c=document.createElement('canvas'); c.width=512; c.height=64; const g=c.getContext('2d'); g.fillStyle='#fff'; g.fillRect(0,0,512,64);
  g.fillStyle='rgba(0,0,0,0.28)'; for(let k=0;k<8;k++){ g.fillRect(k*64-1,0,3,64); } const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; return t; })();
const canopyMat=(col,k,side)=>SLD.rimify(new THREE.MeshStandardMaterial({color:col,roughness:0.42,metalness:0.0,side,map:ribTex,emissive:col,emissiveIntensity:0.06}),0xfff1d8,0.22,k);
const metal=new THREE.MeshStandardMaterial({color:0xd8d8dc,roughness:0.3,metalness:0.55,emissive:0x303034,emissiveIntensity:0.5});

// ---------------------------------------------------------------- umbrella model
// local frame: y=0 is the TIP, +y runs up the shaft to the hook. Canopy apex sits at y=ca, its rim at ca+DEPTH (toward
// the hook), so with the tip up it is a dome, and turned over (tip down) it is a bowl.
const UR=0.47, DEPTH=0.17, LS=1.32;
function canopyGeo(){ const pts=[]; for(let i=0;i<=24;i++){ const r=UR*i/24; pts.push(new THREE.Vector2(Math.max(r,0.001),DEPTH*(r/UR)**2)); }
  const g=new THREE.LatheGeometry(pts,64); const p=g.attributes.position;
  for(let i=0;i<p.count;i++){ const x=p.getX(i), z=p.getZ(i), r=Math.hypot(x,z), th=Math.atan2(z,x); // scalloped rim between the 8 ribs
    p.setY(i,p.getY(i)-0.05*(r/UR)**3*(0.5-0.5*Math.cos(8*th))); }
  g.computeVertexNormals(); return g; }
function makeUmbrella(col,colIn,key,ca,LS=1.32){
  const G=new THREE.Group(); scene.add(G);
  const cg=new THREE.Group(); cg.position.y=ca; G.add(cg);
  const geo=canopyGeo();
  const outer=new THREE.Mesh(geo,canopyMat(col,key+'o',THREE.BackSide)), inner=new THREE.Mesh(geo,canopyMat(colIn,key+'i',THREE.FrontSide));
  for(const m of [outer,inner]){ m.castShadow=true; m.receiveShadow=true; cg.add(m); }
  const rim=new THREE.Mesh(new THREE.TorusGeometry(UR,0.008,6,96),metal); rim.rotation.x=Math.PI/2; rim.position.y=DEPTH-0.025; cg.add(rim);
  const shaft=new THREE.Mesh(new THREE.CylinderGeometry(0.011,0.011,LS,10),metal); shaft.position.y=LS/2; shaft.castShadow=true; G.add(shaft);
  const tip=new THREE.Mesh(new THREE.SphereGeometry(0.018,10,8),metal); G.add(tip);
  const hook=new THREE.Mesh(new THREE.TorusGeometry(0.065,0.014,8,24,Math.PI),new THREE.MeshStandardMaterial({color:0xe9e3d6,roughness:0.4,emissive:0x3a3630,emissiveIntensity:0.6}));
  hook.position.set(0.065,LS,0); G.add(hook); hook.castShadow=true;
  const hookEnd=new THREE.Mesh(new THREE.CylinderGeometry(0.014,0.014,0.06,8),hook.material); hookEnd.position.set(0.13,LS-0.03,0); G.add(hookEnd);
  return {G,cg,outer,inner,ca}; }
// pose: tip position + direction tip->hook, roll about the shaft; close 0 (open)..1 (furled)
const _q=new THREE.Quaternion(), _q2=new THREE.Quaternion();
function placeUmb(U,tipP,dir,roll=0,close=0){ U.G.position.copy(tipP); _q.setFromUnitVectors(V(0,1,0),dir.clone().normalize()); _q2.setFromAxisAngle(V(0,1,0),roll); U.G.quaternion.copy(_q).multiply(_q2);
  const s=lerp(1,0.09,close); U.cg.scale.set(s,lerp(1,3.6,close),s); }
const heroU=makeUmbrella(0xf2ece0,0xcfc8bb,'hu',0.86);
const GLS=0.88; const greyU=makeUmbrella(0x8d929c,0x6c717a,'gu',0.12,GLS);
// water in the hero's bowl
const water=new THREE.Mesh(new THREE.CircleGeometry(1,64),SLD.rimify(new THREE.MeshStandardMaterial({color:0xdfe9f2,roughness:0.08,metalness:0.2,emissive:0x9fb6cc,emissiveIntensity:0.35}),0xffffff,0.3,'water'));
water.rotation.x=-Math.PI/2; heroU.cg.add(water);
const waterGlint=SLD.glowSprite(scene,0xdfefff,0); waterGlint.scale.set(0.9,0.25,1);

// ---------------------------------------------------------------- the cup + the stream
const cupG=new THREE.Group(); scene.add(cupG);
const cupMat=SLD.rimify(new THREE.MeshStandardMaterial({color:0xf1ece2,roughness:0.25,metalness:0,transparent:true,opacity:0.82,side:THREE.DoubleSide,emissive:0xf1ece2,emissiveIntensity:0.08}),0xffffff,0.35,'cup');
const CUPH=0.14;
const cupBody=new THREE.Mesh(new THREE.CylinderGeometry(0.058,0.046,CUPH,24,1,true),cupMat); cupBody.position.y=CUPH/2; cupG.add(cupBody);
const cupBot=new THREE.Mesh(new THREE.CircleGeometry(0.046,24),cupMat); cupBot.rotation.x=-Math.PI/2; cupBot.position.y=0.002; cupG.add(cupBot);
const cupWater=new THREE.Mesh(new THREE.CylinderGeometry(0.052,0.045,1,24),new THREE.MeshStandardMaterial({color:0xbfd6ea,roughness:0.1,metalness:0.1,emissive:0x8aa6c0,emissiveIntensity:0.4,transparent:true,opacity:0.9}));
cupG.add(cupWater);
const stream=new THREE.Mesh(new THREE.CylinderGeometry(0.008,0.006,1,8),new THREE.MeshStandardMaterial({color:0xe6f2ff,roughness:0.05,emissive:0xbfdcff,emissiveIntensity:1.2,transparent:true,opacity:0.85}));
scene.add(stream);
const clip=new THREE.Mesh(new THREE.TorusGeometry(0.03,0.006,6,16),metal); scene.add(clip);

// ---------------------------------------------------------------- sky: clouds, sun, lightning (placed on camera rays)
function onRay(nx,ny,dist){ const p=V(nx,ny,0.5).unproject(cam); return cam.position.clone().add(p.sub(cam.position).normalize().multiplyScalar(dist)); }
const cloudTex=(()=>{ const c=document.createElement('canvas'); c.width=1024; c.height=256; const g=c.getContext('2d'); const Rn=rng(11);
  const grd=g.createLinearGradient(0,0,0,256); grd.addColorStop(0,'#1a1b20'); grd.addColorStop(0.55,'#3a3c44'); grd.addColorStop(1,'#4a4d56');
  g.fillStyle=grd; g.fillRect(0,0,1024,150);
  for(let x=-20;x<1060;x+=38+Rn()*26){ const r=26+Rn()*20; g.beginPath(); g.arc(x,150+Rn()*14-6,r,0,7); g.fill(); }
  g.globalCompositeOperation='source-atop'; for(let k=0;k<70;k++){ { const v=Rn()<0.5?0:120; g.fillStyle=`rgba(${v},${v},${v+6},0.08)`; } g.beginPath(); g.arc(Rn()*1024,Rn()*200,20+Rn()*60,0,7); g.fill(); }
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; return t; })();
const cloudMat=new THREE.MeshBasicMaterial({map:cloudTex,transparent:true,fog:false,depthWrite:false,color:0xffffff});
const cloud=new THREE.Mesh(new THREE.PlaneGeometry(1,0.25),cloudMat); scene.add(cloud); S.NOREFL.push(cloud);
const sunMat=new THREE.MeshBasicMaterial({color:new THREE.Color(1.25,0.1,0.05),fog:false,transparent:true,opacity:0,depthWrite:false});
const sun=new THREE.Mesh(new THREE.CircleGeometry(1,64),sunMat); scene.add(sun);
const sunGlow=SLD.glowSprite(scene,0xff3a20,0), sunGlow2=SLD.glowSprite(scene,0xff6030,0);
for(const m of [sunGlow,sunGlow2,sun]){ m.material.depthTest=false; m.renderOrder=10; } S.NOREFL.push(sunGlow,sunGlow2);
// lightning bolt: a jagged tube from the clouds to the ground behind the grey man
const boltPts=(()=>{ const Rn=rng(5), pts=[]; let x=0; for(let i=0;i<=14;i++){ const y=1-i/14; x+=(Rn()-0.5)*0.16; pts.push(V(x,y,0)); } return pts; })();
const boltMat=new THREE.MeshBasicMaterial({color:new THREE.Color(3.2,3.4,4.0),fog:false,transparent:true,opacity:0});
const bolt=new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(boltPts,false,'catmullrom',0.1),80,0.004,6,false),boltMat); scene.add(bolt);

// ---------------------------------------------------------------- rain: streaks (hidden under the umbrellas) + splashes
const rainU={uCy:{value:0},uT:{value:0},uA:{value:1},uU1:{value:new THREE.Vector4()},uU2:{value:new THREE.Vector4()}};
{ const N=2300, Rn=rng(3), pos=new Float32Array(N*2*3), sd=new Float32Array(N*2), en=new Float32Array(N*2);
  for(let i=0;i<N;i++){ const x=-4+Rn()*8.5, y=Rn()*7, z=-6+Rn()*8.5, s=Rn(); for(const e of [0,1]){ const k=i*2+e; pos[k*3]=x; pos[k*3+1]=y; pos[k*3+2]=z; sd[k]=s; en[k]=e; } }
  const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.BufferAttribute(pos,3)); g.setAttribute('seed',new THREE.BufferAttribute(sd,1)); g.setAttribute('endp',new THREE.BufferAttribute(en,1));
  const m=new THREE.LineSegments(g,new THREE.ShaderMaterial({uniforms:rainU,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
    vertexShader:`attribute float seed; attribute float endp; uniform float uT; uniform vec4 uU1,uU2; varying float vA;
      void main(){ vec3 p=position; float sp=7.5+3.0*seed; p.y=mod(p.y-uT*sp,7.0); p.x+=-0.06*p.y*0.1; float L=0.16+0.14*seed;
        vec3 q=p+vec3(0.012,L,0.0)*endp; vA=(0.25+0.5*fract(seed*13.7))*(endp>0.5?0.0:1.0)+(endp>0.5?0.5:0.0);
        float hid=0.0; vec2 d1=p.xz-uU1.xy; if(dot(d1,d1)<uU1.w*uU1.w && p.y<uU1.z) hid=1.0; vec2 d2=p.xz-uU2.xy; if(dot(d2,d2)<uU2.w*uU2.w && p.y<uU2.z) hid=1.0;
        vA*= (1.0-hid)*smoothstep(0.0,0.15,p.y)*smoothstep(5.2,4.4,p.y);
        gl_Position=projectionMatrix*modelViewMatrix*vec4(q,1.0); }`,
    fragmentShader:`uniform float uA,uCy; varying float vA; void main(){ if(gl_FragCoord.y>uCy) discard; gl_FragColor=vec4(vec3(0.72,0.78,0.88)*vA*uA*0.42,1.0); }`}));
  m.frustumCulled=false; scene.add(m); S.NOREFL.push(m); }
const splU={uT:{value:0},uA:{value:1},uH:{value:H}};
{ const N=520, Rn=rng(9), pos=new Float32Array(N*3), sd=new Float32Array(N);
  for(let i=0;i<N;i++){ pos[i*3]=-3.2+Rn()*7; pos[i*3+1]=0.01; pos[i*3+2]=-3.5+Rn()*6; sd[i]=Rn(); }
  const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.BufferAttribute(pos,3)); g.setAttribute('seed',new THREE.BufferAttribute(sd,1));
  const m=new THREE.Points(g,new THREE.ShaderMaterial({uniforms:splU,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
    vertexShader:`attribute float seed; uniform float uT,uH; varying float vA; varying float vPh;
      void main(){ float per=0.45+0.5*fract(seed*7.1); float ph=fract(uT/per+seed*5.3); vPh=ph; vA=(1.0-ph);
        vec4 mv=modelViewMatrix*vec4(position,1.0); gl_Position=projectionMatrix*mv; gl_PointSize=clamp((0.05+0.12*ph)*uH/(-mv.z),1.0,40.0); }`,
    fragmentShader:`uniform float uA; varying float vA; varying float vPh; void main(){ vec2 c=gl_PointCoord-0.5; c.y*=2.6; float d=length(c);
      float ring=smoothstep(0.08,0.0,abs(d-0.42*vPh-0.06)); gl_FragColor=vec4(vec3(0.75,0.8,0.9)*ring*vA*uA*0.7,1.0); }`}));
  m.frustumCulled=false; scene.add(m); S.NOREFL.push(m); }

// ---------------------------------------------------------------- ground: wet (glossy, puddles) -> dry cracked earth
const wetTex=(()=>{ const c=document.createElement('canvas'); c.width=c.height=512; const g=c.getContext('2d'); const Rn=rng(17);
  g.fillStyle='#bbb'; g.fillRect(0,0,512,512); for(let k=0;k<22;k++){ const x=Rn()*512,y=Rn()*512,r=12+Rn()*40; const gr=g.createRadialGradient(x,y,0,x,y,r); gr.addColorStop(0,'#222'); gr.addColorStop(0.7,'#333'); gr.addColorStop(1,'rgba(187,187,187,0)'); g.fillStyle=gr; g.beginPath(); g.ellipse(x,y,r*1.6,r,0,0,7); g.fill(); }
  const t=new THREE.CanvasTexture(c); t.wrapS=t.wrapT=THREE.RepeatWrapping; t.repeat.set(5,5); return t; })();
S.floor.material.alphaMap=wetTex; S.floor.material.needsUpdate=true;
const crackTex=(()=>{ const N=1024, c=document.createElement('canvas'); c.width=c.height=N; const g=c.getContext('2d'); const Rn=rng(23);
  // dry earth: warm grey with mottling, then voronoi crack lines
  g.fillStyle='#5c554f'; g.fillRect(0,0,N,N); for(let k=0;k<900;k++){ g.fillStyle=`rgba(${Rn()<0.5?40:200},${Rn()<0.5?34:186},${Rn()<0.5?28:170},0.05)`; g.beginPath(); g.arc(Rn()*N,Rn()*N,4+Rn()*40,0,7); g.fill(); }
  const P=[]; for(let i=0;i<190;i++) P.push([Rn()*N,Rn()*N]);
  const P9=[]; for(const [x,y] of P) for(const dx of [-N,0,N]) for(const dy of [-N,0,N]) P9.push([x+dx,y+dy]);
  const im=g.getImageData(0,0,N,N), D=im.data;
  for(let y=0;y<N;y++) for(let x=0;x<N;x++){ let a=1e9,b=1e9; for(const [px,py] of P9){ const dd=(px-x)**2+(py-y)**2; if(dd<a){ b=a; a=dd; } else if(dd<b) b=dd; }
    const e=Math.sqrt(b)-Math.sqrt(a); const k=(y*N+x)*4; const cr=e<1.4?0.12:e<3.5?0.5+0.14*e:1.0; const ed=e<9?0.9+0.1*e/9:1.0; for(let j=0;j<3;j++) D[k+j]*=cr*ed; }
  g.putImageData(im,0,0); const t=new THREE.CanvasTexture(c); t.wrapS=t.wrapT=THREE.RepeatWrapping; t.repeat.set(18,18); t.colorSpace=THREE.SRGBColorSpace; t.anisotropy=8; return t; })();
const dryMat=new THREE.MeshStandardMaterial({color:0xffffff,map:crackTex,roughness:0.95,metalness:0,transparent:true,opacity:0,bumpMap:crackTex,bumpScale:1.2});
const dry=new THREE.Mesh(new THREE.PlaneGeometry(120,120),dryMat); dry.rotation.x=-Math.PI/2; dry.position.y=0.003; dry.receiveShadow=true; scene.add(dry);
const dryFront=(t)=>sstep(4.35,5.4,t);   // the drying sweeps in

// ---------------------------------------------------------------- shared kinematics
function ik2(Sp,Tg,pole,l1,l2){ const d=Tg.clone().sub(Sp); const dist=Math.min(Math.max(d.length(),0.05),l1+l2-0.003); const dn=d.normalize();
  const a=(l1*l1-l2*l2+dist*dist)/(2*dist); const h=Math.sqrt(Math.max(0,l1*l1-a*a));
  const p=pole.clone().addScaledVector(dn,-pole.dot(dn)); if(p.lengthSq()<1e-6) p.set(0,-1,0); p.normalize(); return {E:Sp.clone().addScaledVector(dn,a).addScaledVector(p,h),Hd:Sp.clone().addScaledVector(dn,dist)}; }
const lp=(A,B,u)=>A.clone().lerp(B,u);
const at=(root,f,s,side,y)=>root.clone().addScaledVector(f,s).addScaledVector(side,side===undefined?0:0).add(V(0,y,0));
function P3(root,yaw,fw,sd,y){ return root.clone().add(rotY(V(fw,y,sd),yaw)); }   // local (forward, side(+far), up) -> world

// ---------------------------------------------------------------- hero (cream): walks, collects, pours, drinks
const STEP=2*Math.PI*1.08;
function heroState(t){
  const root=V(HX,0,HZ); const amp=1-sstep(5.1,5.75,t); const ph=t*STEP;
  let P=R.gait({...R.P0,p:0.07,sL:0.0,sR:0.0},ph,amp,0.3,0.55,0.2);
  P.dy=-0.02*amp*Math.abs(Math.cos(ph));
  // drinking: head back
  const up=sstep(7.05,7.4,t)*(1-sstep(7.85,8.2,t)); P.tilt=-0.42*up; P.p=0.07-0.08*up;
  P.hy=0.25*sstep(9.3,9.9,t)*(1-sstep(10.6,11.2,t));          // a glance back at the grey man
  const J0=R.skel(P,root,YAW);
  // umbrella hand (far side): in front of the chest
  const bob=J0.neck.y-1.52;
  const HU=P3(root,YAW,0.3,0.03,1.34+bob);
  // cup: on a clip at the hip, then in the near hand
  const clipP=J0.hipR.clone().add(rotY(V(0.05,-0.08,-0.09),YAW));
  const tipP=HU.clone().add(V(0,-0.12,0));
  const pourP=tipP.clone().add(V(0,-0.36,0)).add(rotY(V(0.02,0,0),YAW));
  const mouth=J0.head.clone().add(rotY(V(0.17,-0.1,-0.02),YAW));
  const rest=P3(root,YAW,0.24,-0.2,0.96);
  let cp, tilt=0, wR=0;
  if(t<5.85){ cp=clipP; }
  else { wR=sstep(5.85,6.1,t);
    cp=lp(clipP,pourP,sstep(6.05,6.4,t)); cp=lp(cp,mouth,sstep(7.0,7.35,t)); cp=lp(cp,rest,sstep(7.95,8.35,t));
    tilt=1.05*sstep(7.3,7.55,t)*(1-sstep(7.8,8.05,t)); }
  P.tR=cp.clone().add(V(0,0.06,0)).addScaledVector(rotY(V(0,0,1),YAW),-0.05); P.wR=wR; P.pR=V(-0.2,-0.7,-0.6);
  P.tL=HU; P.wL=1; P.pL=V(-0.2,-0.7,0.7);
  const fill=sstep(6.45,6.95,t)*(1-0.85*sstep(7.4,7.9,t));
  const bowl=Math.min(1,0.1+t/3.0*0.75)-0.12*sstep(6.45,6.95,t);
  return {P,root,HU,tipP,cp,tilt,fill,bowl,clipP,pour:sstep(6.42,6.5,t)*(1-sstep(6.9,7.0,t))}; }

// ---------------------------------------------------------------- grey man: laughs, throws, wilts, kneels with it
const REL=4.47, LAND=5.0;
const LANDP=V(GX+0.12,0.03,GZ+0.45), LANDDIR=V(1,0,-0.12).normalize();
function greyState(t){
  const root=V(GX,0,GZ);
  const amp=1-sstep(5.3,5.9,t); const ph=t*STEP+0.9;
  let P=R.gait({...R.P0,p:0.06},ph,amp,0.28,0.5,0.18);
  let yaw=YAW;
  // laugh: bent and bobbing
  const lg=sstep(1.05,1.3,t)*(1-sstep(2.5,2.8,t)); const bob=Math.sin(t*2*Math.PI*3.6);
  P.p=lerp(P.p,0.42+0.1*bob,lg); P.tilt=lerp(0,0.15-0.25*bob,lg);
  P.tilt+= -0.55*sstep(3.05,3.5,t)*(1-sstep(3.85,4.15,t));          // looks up as the rain stops
  // heat: hunch
  const hunch=sstep(4.7,5.6,t);
  P=R.blend(P,{...R.POSES.hunch,p:0.32,tilt:0.18,aL:P.aL,aR:P.aR,kL:P.kL+0.12,kR:P.kR+0.12,sL:P.sL,sR:P.sR},hunch*(1-sstep(7.9,8.05,t)));
  P.fx=0.03*Math.sin(t*2.1)*hunch;
  // wipe the brow
  const wipe=sstep(6.45,6.7,t)*(1-sstep(7.25,7.5,t));
  // umbrella hand (near side)
  const J0=R.skel(P,root,yaw);
  const hold=P3(root,yaw,-0.04,-0.22,1.62+(J0.neck.y-1.52));
  let HR=hold.clone(), wR=1, uDir=V(0,-1,0), close=0, umbTip=null, umbDir=null;
  // throw: wind up high behind, fling back over his near shoulder (to screen right)
  const wind=P3(root,yaw,-0.22,-0.32,1.95), fling=P3(root,yaw,-0.55,-0.38,1.4);
  close=sstep(3.92,4.2,t);
  HR=lp(HR,wind,sstep(3.95,4.25,t)); HR=lp(HR,fling,sstep(4.25,REL,t));
  const back=rotY(V(-1,0.25,-0.3),yaw).normalize();
  uDir=V(0,-1,0).lerp(back.clone().negate(),sstep(4.15,REL,t)).normalize();    // tip -> hook direction
  P.tR=HR; P.wR=t<REL+0.05?1:1-sstep(REL+0.05,REL+0.4,t); P.pR=V(-0.4,-0.5,-0.8);
  // pointing (0-1.05, 2.65-3.0) and the hand on the belly while laughing
  const point=(1-sstep(0.95,1.15,t))+sstep(2.55,2.8,t)*(1-sstep(2.95,3.2,t));
  const shL=J0.neck.clone().add(rotY(V(0,-0.06,0.05),yaw));
  const pointP=shL.clone().add(rotY(V(0.6,0.03,-0.05),yaw)), belly=J0.hip.clone().add(rotY(V(0.16,0.26,0.02),yaw));
  const brow=J0.head.clone().add(rotY(V(0.1,0.03,0.04),yaw));
  let tL=pointP, wL=point;
  if(lg>0.01){ tL=belly; wL=Math.max(wL,lg); }
  if(wipe>0.01){ tL=lp(brow,brow.clone().add(rotY(V(0,0,-0.12),yaw)),sstep(6.75,7.2,t)); wL=wipe; }
  P.tL=tL; P.wL=wL; P.pL=V(-0.3,-0.5,0.8);
  let rootOut=root, yawOut=yaw;
  // collapse: turn to the umbrella, knees, then hands to the ground, crawl reach, grab, kneel up with it overhead
  if(t>=7.9){
    const turn=sstep(7.9,8.2,t), turnBack=sstep(9.0,9.4,t);
    yawOut=lerp(lerp(YAW,YAW2-2*Math.PI*(YAW2-YAW>Math.PI?1:0),turn),YAW+0.15,turnBack);
    const KNEEL={...R.P0,p:0.12,tilt:0.25,aL:0.05,aR:-0.0,kL:1.62,kR:1.56,sL:0.1,sR:0.1};
    const CRAWL={...R.P0,p:1.25,tilt:-0.9,aL:0.12,aR:0.0,kL:1.7,kR:1.62,fx:0.0};
    const KUP={...R.P0,p:-0.02,tilt:-0.3,aL:0.05,aR:-1.1,kL:1.62,kR:-1.0+1.1+0.05,sL:0.1,sR:0.1};
    // kneel up with one knee forward (right foot planted)
    KUP.aR=1.35; KUP.kR=1.4;
    let Q=R.blend({...R.POSES.hunch},KNEEL,sstep(8.0,8.25,t));
    Q=R.blend(Q,CRAWL,sstep(8.22,8.5,t)); Q=R.blend(Q,KUP,sstep(8.82,9.15,t));
    Q.fx=0.0; const tremble=0.012*Math.sin(t*31)*sstep(9.3,9.6,t);
    rootOut=root.clone().add(rotY(V(-0.32+0.1*sstep(8.2,8.5,t)*(1-sstep(8.82,9.15,t)),0,0),yawOut));
    const J1=R.skel(Q,rootOut,yawOut);
    const hand=(fw,sd,y)=>P3(rootOut,yawOut,fw,sd,y);
    const crawlH=[hand(0.62,0.12,0.05),hand(0.68,-0.14,0.05)];
    const grab=sstep(8.5,8.75,t), lift=sstep(8.85,9.15,t);
    const handleP=LANDP.clone().add(LANDDIR.clone().multiplyScalar(GLS-0.05));
    const over=hand(0.16,0.0,1.7+tremble);
    let hL=crawlH[0], hR2=lp(crawlH[1],handleP,grab);
    hL=lp(hL,over.clone().add(rotY(V(0,0,0.07),yawOut)),lift); hR2=lp(hR2,over.clone().add(rotY(V(0,0,-0.07),yawOut)),lift);
    const w=sstep(8.15,8.35,t);
    Q.tL=hL; Q.wL=w; Q.tR=hR2; Q.wR=w; Q.pL=V(-0.3,-0.6,0.8); Q.pR=V(-0.3,-0.6,-0.8);
    P=R.blend(P,Q,sstep(7.95,8.1,t)); P.tL=Q.tL; P.tR=Q.tR; P.wL=lerp(P.wL,Q.wL,sstep(7.95,8.1,t)); P.wR=Q.wR; P.pL=Q.pL; P.pR=Q.pR;
    // the umbrella: lying, dragged by the handle, then lifted, turned tip-down (a bowl) and snapped open
    if(t>=8.62){ const flip=SLD.ease(sstep(8.95,9.15,t));
      const lyingTip=LANDP.clone(); const holdTip=over.clone().add(V(0,-0.08,0));
      const dragged=lp(lyingTip,handleP.clone().add(V(0,0.25,0)).addScaledVector(LANDDIR,-(GLS-0.05)),sstep(8.62,8.85,t));
      umbTip=lp(dragged,holdTip,flip);
      umbDir=LANDDIR.clone().negate().lerp(V(0,1,0),sstep(8.62,8.9,t)*0.0+flip).normalize();
      if(flip<0.02) umbDir=LANDDIR.clone().negate().multiplyScalar(-1);
      umbDir=lp(LANDDIR,V(0,1,0),flip).normalize();
      close=1-sstep(9.02,9.18,t); } }
  return {P,root:rootOut,yaw:yawOut,HR,uDir,close,umbTip,umbDir,hunch}; }

// umbrella flight after the throw: parabola + one tumble, lands lying on the ground, small bounce
function greyUmb(t,gs,J){
  if(gs.umbTip) return {tip:gs.umbTip,dir:gs.umbDir,close:gs.close};
  if(t<REL){ // in his hand: grip near the hook
    const dir=gs.uDir; const tip=J.hR.clone().addScaledVector(dir,-(GLS-0.07)); return {tip,dir,close:gs.close}; }
  // release state (recomputed purely from the pose at REL)
  const gr=greyState(REL); const Jr=R.skel(gr.P,gr.root,gr.yaw); const d0=gr.uDir; const tip0=Jr.hR.clone().addScaledVector(d0,-(GLS-0.07));
  const c0=tip0.clone().addScaledVector(d0,GLS/2), c1=LANDP.clone().addScaledVector(LANDDIR,GLS/2);
  const u=clamp((t-REL)/(LAND-REL)); const c=lp(c0,c1,u); c.y+=1.0*u*(1-u)*1.6;
  if(t>LAND){ const b=t-LAND; c.y+=0.07*Math.abs(Math.sin(b*14))*Math.exp(-b*9); }
  const q0=new THREE.Quaternion().setFromUnitVectors(V(0,1,0),d0), q1=new THREE.Quaternion().setFromUnitVectors(V(0,1,0),LANDDIR);
  const qq=q0.clone().slerp(q1,SLD.ease(u)); const spin=new THREE.Quaternion().setFromAxisAngle(rotY(V(0,0,1),YAW),2*Math.PI*(1-SLD.ease(u)));
  const dir=V(0,1,0).applyQuaternion(spin.multiply(qq)).normalize();
  return {tip:c.clone().addScaledVector(dir,-GLS/2),dir,close:1}; }

// ---------------------------------------------------------------- weather
const rainA=t=>1-sstep(3.0,3.65,t);
const sunA=t=>sstep(3.55,4.1,t);
const flash=t=>{ let f=0; for(const [t0,a] of [[2.98,1],[3.1,0.6],[3.22,0.35]]){ const d=t-t0; if(d>=0) f=Math.max(f,a*Math.exp(-d*16)); } return f; };

// ---------------------------------------------------------------- frame
function setCam(){ cam.fov=CAM.fov; cam.updateProjectionMatrix(); cam.position.set(CAM.x,CAM.y,CAM.z); cam.lookAt(CAM.tx,CAM.ty,0); cam.updateMatrixWorld(); }
setCam();
let last={};
function setT(t){
  setCam();
  const ra=rainA(t), sa=sunA(t), fl=flash(t), dr=dryFront(t);
  // hero
  const hs=heroState(t); const JH=R.skel(hs.P,hs.root,YAW); R.poseFig(hero,JH);
  const hDir=V(0,1,0); const hTip=JH.hL.clone().add(V(0,-0.1,0));
  placeUmb(heroU,hTip,hDir,0.4,0);
  const lvl=DEPTH*clamp(hs.bowl,0.02,0.92); water.position.y=lvl; water.scale.setScalar(UR*Math.sqrt(lvl/DEPTH)*0.97);
  water.material.emissiveIntensity=0.35+1.4*fl;
  // cup
  const cupBase=t<5.85?hs.clipP:JH.hR.clone().add(V(0,-0.06,0)).addScaledVector(rotY(V(0,0,1),YAW),0.05);
  cupG.position.copy(cupBase); cupG.quaternion.setFromAxisAngle(SR.clone(),-hs.tilt);
  const fh=Math.max(0.002,CUPH*0.85*hs.fill); cupWater.scale.set(1,fh,1); cupWater.position.y=fh/2+0.003; cupWater.visible=hs.fill>0.01;
  clip.position.copy(hs.clipP).add(V(0,CUPH+0.01,0)); clip.visible=t<5.9;
  // stream from the tip into the cup
  stream.visible=hs.pour>0.01; if(stream.visible){ const a=hTip.clone(), b=cupBase.clone().add(V(0,0.04+fh,0)); const L=a.distanceTo(b);
    stream.position.copy(a).lerp(b,0.5); stream.scale.set(1,L,1); stream.material.opacity=0.85*hs.pour; }
  // grey
  const gs=greyState(t); const JG=R.skel(gs.P,gs.root,gs.yaw); R.poseFig(grey,JG);
  const gu=greyUmb(t,gs,JG); placeUmb(greyU,gu.tip,gu.dir,0.2,gu.close);
  // rain occluders: hero bowl, grey canopy (only while open and over him)
  const bc=heroU.G.position.clone().add(V(0,0.86,0));
  rainU.uU1.value.set(bc.x,bc.z,bc.y+DEPTH,UR*0.98);
  const gc=greyU.G.position.clone().addScaledVector(gu.dir,0.18);
  rainU.uU2.value.set(gc.x,gc.z,gc.y,t<3.9?UR*0.98:0);
  rainU.uT.value=t; rainU.uCy.value=H*(1-0.135); rainU.uA.value=ra; splU.uT.value=t; splU.uA.value=ra;
  // sky
  const cyN=1-2*(0.115+(-0.12)*sstep(3.1,3.9,t)); const cp=onRay(0,cyN,15); cloud.position.copy(cp); cloud.lookAt(cam.position);
  const wv=2*15*Math.tan(THREE.MathUtils.degToRad(cam.fov/2))*cam.aspect*1.1; cloud.scale.set(wv,wv,1);
  cloudMat.opacity=1-sstep(3.15,3.85,t); cloudMat.color.setScalar(1+5*fl);
  const sp=onRay(0,1-2*0.29,16); sun.position.copy(sp); sun.lookAt(cam.position);
  const sr=16*Math.tan(THREE.MathUtils.degToRad(cam.fov/2))*cam.aspect*0.155; sun.scale.setScalar(sr*(1+0.01*Math.sin(t*3)));
  sunMat.opacity=sa; sunGlow.position.copy(sp); sunGlow.scale.setScalar(sr*7); sunGlow.material.opacity=0.55*sa; sunGlow2.position.copy(sp); sunGlow2.scale.setScalar(sr*3.2); sunGlow2.material.opacity=0.6*sa*(0.9+0.1*Math.sin(t*2.3));
  const b0=onRay(0.86,0.66,13.5), b1=onRay(0.8,0.0,13.5); bolt.position.copy(b1); bolt.scale.set(b0.distanceTo(b1)*0.9,b0.y-b1.y,1); bolt.lookAt(cam.position.clone().setY(b1.y)); bolt.scale.z=1;
  boltMat.opacity=t>=2.98&&t<3.3?Math.min(1,fl*2.2):0; bolt.visible=boltMat.opacity>0.01;
  // light
  scene.background.copy(BG_RAIN).lerp(BG_SUN,sa).lerp(new THREE.Color(0x3a3f4a),fl*0.6); scene.fog.color.copy(scene.background);
  hemi.intensity=0.7-0.2*sa+2.4*fl; hemi.color.setHex(0x8a96b4).lerp(new THREE.Color(0xffc0a0),sa);
  flashL.intensity=4*fl; sunRim.intensity=0.9*sa;
  key.color.setHex(0xe8eefc).lerp(new THREE.Color(0xffd6b0),sa); key.intensity=1.25-0.25*sa;
  S.spot.color.setHex(0xcbd6ea).lerp(new THREE.Color(0xffd2a8),sa);
  S.floor.material.opacity=lerp(0.62,0.9,dr); S.floor.material.color.setHex(0x5a5e66);
  dryMat.opacity=dr; dryMat.color.setRGB(0.8,0.8,0.8).lerp(new THREE.Color(0.86,0.76,0.7),sa*0.5);
  S.moteU.uOp.value=sa*0.35;
  waterGlint.position.copy(bc).add(V(0,lvl+0.02,0.05)); waterGlint.material.opacity=0.0;
  S.tick(t,0); S.spot.intensity=QK('spot',70)*(1.0+0.1*sa);
  // fade to black at the end
  S.GU.uT.value=t;
  last={hs,gs,JH,JG};
}
// final fade is applied in compose (frame-exact); renderAt stays pure
window.renderAt=(t,K=3)=>S.renderAt(setT,t,K,{t0:0,t1:DUR});
window.metaAt=t=>{ setT(t); const pr=v=>{ const n=v.clone().project(cam); return [+((n.x+1)/2).toFixed(4),+((1-n.y)/2).toFixed(4)]; };
  const {JH,JG}=last; return {t,heroHead:pr(JH.head.clone().add(V(0,0.13,0))),heroFeet:pr(JH.fL),greyHead:pr(JG.head.clone().add(V(0,0.13,0))),greyHeadC:pr(JG.head),greyFeet:pr(JG.fR),
    bowlRim:pr(heroU.G.position.clone().add(V(0,0.86+DEPTH,0))),bowlL:pr(heroU.G.position.clone().add(V(-UR,0.86+DEPTH,0))),bowlR:pr(heroU.G.position.clone().add(V(UR,0.86+DEPTH,0)))}; };
window.ready=true;
