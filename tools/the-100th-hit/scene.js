// The 100th Hit (Slow Light Dark). Split screen: two identical stages (top, bottom), each a cream stickman with a
// sledgehammer and a dark boulder under the series gold lamp. Every hit adds glowing red cracks; the pace eases from
// 0.9 s to 0.06 s per hit. Top quits at 99 (drops the hammer, walks off, his boulder cools to grey); bottom lifts once
// more and hit 100 bursts the boulder open on a gold light. Then the top camera tilts in: one hit away.
//
// One stage is rendered twice per frame (half 0 = top, half 1 = bottom); both halves share every state up to hit 99.
// renderAt(t) is pure (no state between frames), so frames can render in parallel workers.
import * as THREE from 'three';
import * as SLD from './sld.js';
const {V,clamp,sstep,lerp,sm5,PAL,rng,rotY,yawOf}=SLD;
const TL=await (await fetch('./timeline.json')).json();
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960, HH=Math.round(H/2), DUR=TL.duration;
const D2R=Math.PI/180;

// ---------------------------------------------------------------- hit times: interval d_k = dMin + (dMax-dMin) e^(-k/tau), tau solved so hit 99 lands at t99
function hitTimes(){ const n=TL.hits-1, d=(tau,k)=>TL.dMin+(TL.dMax-TL.dMin)*Math.exp(-k/tau);
  const span=tau=>{ let s=0; for(let k=0;k<n-1;k++) s+=d(tau,k); return s; };
  let lo=0.3,hi=80; for(let i=0;i<80;i++){ const m=(lo+hi)/2; if(span(m)>TL.t99-TL.t1) hi=m; else lo=m; }
  const T=[0,TL.t1]; for(let k=0;k<n-1;k++) T.push(T[T.length-1]+d(lo,k)); T[n]=TL.t99; T.push(TL.t100); return {T,tau:lo}; }
const {T:HT,tau:TAU}=hitTimes();          // HT[1..100]
const lastHit=99;
function hitsAt(t,half){ const top=half===0?lastHit:100; let k=0; while(k<top&&HT[k+1]<=t) k++; return k; }

// ---------------------------------------------------------------- stage
const S=SLD.createStage({W,H:HH,lamp:V(-0.16,4.6,0.05),lampTarget:V(-0.14,0,0)});
const {scene,cam}=S;
const R=SLD.createRig(scene);
const man=R.makeFig(PAL.CREAM,'hero',{rim:0.16,lift:0.07});

// world layout: man on the right facing -x, boulder on the left; the lamp sits between them
const YAW=yawOf(V(-1,0,0)), FWD=V(-1,0,0), UP=V(0,1,0), LAT=FWD.clone().cross(UP).normalize();
const MAN=V(0.86,0,0.02);

// ---------------------------------------------------------------- boulder: faceted displaced sphere (unit radius in object space)
function h3(x,y,z){ const s=Math.sin(x*127.1+y*311.7+z*74.7)*43758.5453; return s-Math.floor(s); }
function vn(x,y,z){ const ix=Math.floor(x),iy=Math.floor(y),iz=Math.floor(z), fx=x-ix,fy=y-iy,fz=z-iz; const u=fx*fx*(3-2*fx),v=fy*fy*(3-2*fy),w=fz*fz*(3-2*fz);
  const L=(a,b,t)=>a+(b-a)*t; const c=(i,j,k)=>h3(ix+i,iy+j,iz+k);
  return L(L(L(c(0,0,0),c(1,0,0),u),L(c(0,1,0),c(1,1,0),u),v),L(L(c(0,0,1),c(1,0,1),u),L(c(0,1,1),c(1,1,1),u),v),w); }
const fbm=(x,y,z)=>vn(x,y,z)*0.55+vn(x*2.1+5,y*2.1,z*2.1)*0.3+vn(x*4.3,y*4.3+9,z*4.3)*0.15;
const CUTS=(()=>{ const Rn=rng(4); const c=[[V(0,-1,0),0.70]]; for(let i=0;i<7;i++){ const n=V(Rn()-0.5,(Rn()-0.35)*0.9,Rn()-0.5).normalize(); c.push([n,0.84+0.1*Rn()]); } return c; })();
function rDir(d){ let r=1+0.16*(fbm(d.x*1.5+3,d.y*1.5,d.z*1.5)-0.5)+0.05*(fbm(d.x*5,d.y*5,d.z*5+2)-0.5);
  for(const [n,o] of CUTS){ const k=d.dot(n); if(k>1e-3) r=Math.min(r,o/k+0.02*(fbm(d.x*7,d.y*7,d.z*7)-0.5)); } return r; }
const BR=0.56, BSC=V(BR*1.08,BR*0.98,BR*1.0);
const rockGeo=(()=>{ const g=new THREE.IcosahedronGeometry(1,48); const p=g.attributes.position; const d=V(0,0,0);
  for(let i=0;i<p.count;i++){ d.set(p.getX(i),p.getY(i),p.getZ(i)).normalize(); const r=rDir(d); p.setXYZ(i,d.x*r,d.y*r,d.z*r); }
  g.computeVertexNormals(); return g; })();
const BC=V(0,0.70*BSC.y-0.012,0);          // set after the contact solve (x)
const BROT=0.6;
const rockU={uImp:{value:V(0,0,0)},uN:{value:0},uHeat:{value:1},uPulse:{value:0},uCool:{value:0},uFin:{value:0},uRed:{value:new THREE.Color(PAL.RED)}};
const rockMat=new THREE.MeshStandardMaterial({color:0x3a3632,roughness:0.92,metalness:0,map:SLD.noiseTex(512,31,128,70,160,0.18)});
rockMat.onBeforeCompile=s=>{ Object.assign(s.uniforms,rockU);
  s.vertexShader=s.vertexShader.replace('#include <common>','#include <common>\nvarying vec3 vOP;').replace('#include <begin_vertex>','#include <begin_vertex>\nvOP=position;');
  s.fragmentShader=s.fragmentShader.replace('#include <common>',`#include <common>
    varying vec3 vOP; uniform vec3 uImp,uRed; uniform float uN,uHeat,uPulse,uCool,uFin; float gCr,gHalo,gD;
    vec3 hh3(vec3 p){ p=vec3(dot(p,vec3(127.1,311.7,74.7)),dot(p,vec3(269.5,183.3,246.1)),dot(p,vec3(113.5,271.9,124.6))); return fract(sin(p)*43758.5453); }
    float hh(vec3 p){ return fract(sin(dot(p,vec3(12.9898,78.233,37.719)))*43758.5453); }
    float n3(vec3 p){ vec3 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f);
      return mix(mix(mix(hh(i),hh(i+vec3(1,0,0)),f.x),mix(hh(i+vec3(0,1,0)),hh(i+vec3(1,1,0)),f.x),f.y),mix(mix(hh(i+vec3(0,0,1)),hh(i+vec3(1,0,1)),f.x),mix(hh(i+vec3(0,1,1)),hh(i+vec3(1,1,1)),f.x),f.y),f.z); }
    float vEdge(vec3 x){ vec3 i=floor(x), f=fract(x); float d1=8.0, d2=8.0;
      for(int a=-1;a<=1;a++) for(int b=-1;b<=1;b++) for(int c=-1;c<=1;c++){ vec3 g=vec3(float(a),float(b),float(c)); vec3 r=g+hh3(i+g)-f; float d=dot(r,r);
        if(d<d1){ d2=d1; d1=d; } else if(d<d2) d2=d; }
      return sqrt(d2)-sqrt(d1); }`)
   .replace('#include <color_fragment>',`#include <color_fragment>
    { vec3 p=vOP; gD=length(p-uImp); gCr=0.0; gHalo=0.0;
      if(uN>0.0005){
        vec3 q=p+0.22*vec3(n3(p*2.7),n3(p*2.7+7.3),n3(p*2.7+13.1))-0.11;
        float jit=0.45*(n3(p*3.3+4.0)-0.5);
        float uV=pow(uN,0.6);   // spread runs ahead of the heat so the first hits already show a crack
        float R1=2.35*pow(uV,0.7), R2=2.2*pow(uV,0.9)-0.06, R3=2.0*pow(uV,1.15)-0.12;
        float m1=smoothstep(R1+0.02,R1-0.22,gD+jit), m2=smoothstep(R2+0.02,R2-0.2,gD+jit*1.3), m3=smoothstep(R3+0.02,R3-0.18,gD+jit*1.6);
        float e1=vEdge(q*2.1), e2=vEdge(q*4.8+3.1), e3=m3>0.0?vEdge(q*10.5+9.7):1.0;
        float w1=0.035+0.08*uN, w2=0.022+0.04*uN, w3=0.014+0.018*uN;
        float l1=1.0-smoothstep(w1*0.3,w1,e1), l2=1.0-smoothstep(w2*0.3,w2,e2), l3=1.0-smoothstep(w3*0.3,w3,e3);
        // only some cell edges are cracks: more of them open as the hits add up (reads as branching, not a honeycomb)
        float o1=smoothstep(0.66-0.42*uV,0.74-0.42*uV,n3(q*3.4+1.0)), o2=smoothstep(0.7-0.4*uV,0.78-0.4*uV,n3(q*6.1+5.0)), o3=smoothstep(0.72-0.35*uV,0.8-0.35*uV,n3(q*9.0+2.0));
        float near=1.0-smoothstep(0.0,0.9,gD); o1=max(o1,near); o2=max(o2,near*0.8);
        l1*=o1; l2*=o2*max(o1,0.35); l3*=o3;
        gCr=max(l1*m1,max(0.8*l2*m2,0.55*l3*m3));
        float imp=1.0-smoothstep(0.0,0.06+0.16*uN,gD+0.04*jit); gCr=max(gCr,imp*0.85);
        gHalo=m1*o1*(1.0-smoothstep(0.0,0.2,e1))*0.6+m2*o2*(1.0-smoothstep(0.0,0.1,e2))*0.3+imp*0.5;
      }
      diffuseColor.rgb*=1.0-0.88*gCr; }`)
   .replace('#include <emissivemap_fragment>',`#include <emissivemap_fragment>
    { float I=uHeat*(0.85+0.75*pow(uN,1.2))*(1.0+0.6*uPulse)*(0.45+0.55*exp(-gD*1.3));
      vec3 hot=mix(uRed,vec3(1.0,0.3,0.09),clamp(gCr*gCr*gCr*uN,0.0,0.45));
      totalEmissiveRadiance+=(hot*gCr+uRed*gHalo*0.16)*I*(1.0-uCool);
      totalEmissiveRadiance+=uRed*gCr*uFin*(1.0-smoothstep(0.2,0.6,gD))*1.1; }`); };
rockMat.customProgramCacheKey=()=>'rock-cracks';
const rock=new THREE.Mesh(rockGeo,rockMat); rock.scale.copy(BSC); rock.rotation.y=BROT; rock.castShadow=true; rock.receiveShadow=true; scene.add(rock);
const redLight=new THREE.PointLight(0xff3a24,0,4,2); scene.add(redLight);
const redHalo=SLD.glowSprite(scene,0xff3020,0);
// inside test in world space (for the hammer contact solve)
function insideRock(pw){ const l=rock.worldToLocal(pw.clone()); const len=l.length(); return len<rDir(l.clone().divideScalar(len)); }

// ---------------------------------------------------------------- sledgehammer
const IRONM=SLD.IRON(); IRONM.color.set(0x77777f); SLD.rimify(IRONM,0xfff1d8,0.18,'hammer');
const handle=new THREE.Mesh(new THREE.CylinderGeometry(0.017,0.02,1,12),new THREE.MeshStandardMaterial({color:0x8a6a4c,roughness:0.6}));
const head=new THREE.Mesh(new THREE.BoxGeometry(0.28,0.12,0.12),IRONM);
for(const m of [handle,head]){ m.castShadow=true; m.receiveShadow=true; scene.add(m); }
const HL0=-0.07, HL1=0.80, HEADD=0.74, HALF_HEAD=0.14;
const dirA=(a,fwd=FWD)=>fwd.clone().multiplyScalar(Math.cos(a*D2R)).addScaledVector(UP,Math.sin(a*D2R));
// hammer pose from grip point g and angle theta (deg, from forward-horizontal, up positive) in the swing plane
function placeHammer(g,dir,m){ const a=g.clone().addScaledVector(dir,HL0), b=g.clone().addScaledVector(dir,HL1);
  handle.position.copy(a).add(b).multiplyScalar(0.5); handle.scale.set(1,HL1-HL0,1); handle.quaternion.setFromUnitVectors(UP,dir);
  const hc=g.clone().addScaledVector(dir,HEADD); head.position.copy(hc);
  const z=m.clone().cross(dir).normalize(); head.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(m,dir,z));
  return {hc,face:hc.clone().addScaledVector(m,-HALF_HEAD)}; }

// ---------------------------------------------------------------- swing body
// s = wind-up fraction (0 at impact, 1 hammer overhead behind). Weight goes back on the wind-up and drops into the hit.
function swingPose(th,extra={}){ const s=clamp((th+20)/225);
  return {...R.P0,p:lerp(0.46,-0.07,s),tilt:lerp(0.22,-0.18,s),aL:0.34,aR:-0.24,kL:lerp(0.5,0.16,s),kR:lerp(0.42,0.12,s),dy:-lerp(0.07,0.0,s),fx:lerp(0.07,-0.04,s),...extra}; }
const phiOf=th=>th<60?th:60+(th-60)*0.36;            // hands stop above the head, the wrists carry the rest
function gripAt(P,th,root=MAN,yaw=YAW){ const J=R.skel(P,root,yaw); const sh=J.shL.clone().add(J.shR).multiplyScalar(0.5); const fwd=J.fwd;
  const s=clamp((th+20)/225); const g=sh.clone().addScaledVector(dirA(phiOf(th),fwd),lerp(0.57,0.43,s)).addScaledVector(LAT,0.02); return {g,J,fwd,s}; }
function hammerGeom(P,th){ const {g,fwd,s}=gripAt(P,th); const dir=dirA(th,fwd), m=dirA(th+90,fwd); const hc=g.clone().addScaledVector(dir,HEADD); return {g,dir,m,s,hc,face:hc.clone().addScaledVector(m,-HALF_HEAD)}; }
// solve the layout once: put the boulder where a hammer at -18 deg lands on its upper front, then find the exact contact angle
const TH_NOM=-18;
{ const h=hammerGeom(swingPose(TH_NOM),TH_NOM); rock.position.set(0,BC.y,0); rock.updateMatrixWorld(true);
  let x=h.face.x-0.2; for(let i=0;i<400;i++){ rock.position.x=x; rock.updateMatrixWorld(true); if(insideRock(h.face)) break; x+=0.002; }
  // nudge the boulder 1 cm deeper so the contact sits on the solid part of the surface
  rock.position.x+=0.01; rock.updateMatrixWorld(true); BC.x=rock.position.x; }
let TH_I=60; for(;TH_I>-80;TH_I-=0.1){ const h=hammerGeom(swingPose(TH_I),TH_I); if(insideRock(h.face)) break; }
const HIMP=hammerGeom(swingPose(TH_I),TH_I); const CONTACT=HIMP.face.clone();
rockU.uImp.value.copy(rock.worldToLocal(CONTACT.clone()));
let TH_R=-40; for(;TH_R>-90;TH_R-=0.2){ const h=hammerGeom(swingPose(TH_R),TH_R); if(Math.min(h.hc.y,h.face.y)<0.055) break; }   // hammer resting on the floor
const TH_TOP=205;
const BCW=rock.position.clone();

// ---------------------------------------------------------------- the swing curve
// a(D): swing amplitude from the beat interval D: full overhead swings at 0.9 s, short frantic chops at 0.06 s
const ampOf=D=>Math.pow(clamp((D-0.045)/0.8),0.55);
function cycleTheta(u,D){ const top=TH_I+(TH_TOP-TH_I)*ampOf(D), UL=0.6;
  if(u<UL){ const v=u/UL; return TH_I+(top-TH_I)*(v*v*(3-2*v)); }
  const v=(u-UL)/(1-UL); return top+(TH_I-top)*v*v; }
// returns {th, P, wHands, hammerFree, alpha, root, yaw}
function manAt(t,half){
  const base={wHands:1,alpha:1,root:MAN,yaw:YAW,free:null,P:null,th:0};
  if(t<HT[1]){   // hit 1 from rest: a slow heavy lift, a held top, the drop
    let th; const a=0.05, b=1.42, c=1.56;
    if(t<b){ const v=sstep(a,b,t); th=TH_R+(TH_TOP-TH_R)*v; } else if(t<c) th=TH_TOP; else { const v=(t-c)/(HT[1]-c); th=TH_TOP+(TH_I-TH_TOP)*v*v; }
    return {...base,th,P:swingPose(th)}; }
  if(t<HT[lastHit]){ let k=2; while(HT[k]<=t) k++; const D=HT[k]-HT[k-1]; const th=cycleTheta((t-HT[k-1])/D,D); return {...base,th,P:swingPose(th)}; }
  if(half===0){   // the quitter
    const P0=swingPose(TH_I);
    const QP={...R.POSES.hunch,p:0.36,tilt:0.62,hy:-0.05,aL:0.12,aR:-0.08,kL:0.12,kR:0.08,sL:0.04,sR:-0.02,eL:0.12,eR:0.1};
    const us=sm5(sstep(TL.slump,TL.turn,t)); let P=R.blend(P0,QP,us);
    P.p+=0.02*Math.sin(2*Math.PI*0.45*(t-TL.slump))*sstep(TL.slump,TL.turn,t);
    const wH=1-sstep(TL.release,TL.release+0.16,t);
    // turn away then walk off into the dark (back right), slow
    const away=V(0.05,0,-1).normalize(); const yaw=lerp(YAW,yawOf(away)+2*Math.PI*0,sm5(sstep(TL.turn,TL.walk+0.25,t)));
    const sw=Math.max(0,t-TL.walk), dist=0.62*(sw-0.6*(1-Math.exp(-sw/0.6)));
    const root=MAN.clone().addScaledVector(away,dist).add(V(0.0,0,0));
    const ga=sstep(TL.turn,TL.walk+0.3,t); const ph=(dist+0.12*sstep(TL.turn,TL.walk,t))/1.3*2*Math.PI;
    if(ga>0) P=R.gait(P,ph,ga*0.75,0.26,0.5,0.12);
    return {...base,th:TH_I,P,wHands:wH,alpha:1-sstep(TL.fade0,TL.fade1,t),root,yaw,free:t>=TL.release};
  }
  // the one who keeps going
  let th, ex={};
  if(t<TL.lift0){ th=TH_I+(TH_R-TH_I)*sm5(sstep(HT[lastHit]+0.02,TL.breath,t));
    const br=sstep(TL.rest,TL.breath,t); ex={p:lerp(swingPose(th).p,0.3,br)+0.045*br*Math.sin(2*Math.PI*0.62*(t-TL.rest)),tilt:lerp(swingPose(th).tilt,0.42,br)}; }
  else if(t<TL.lift1){ const v=sstep(TL.lift0,TL.lift1,t); th=TH_R+(TH_TOP-TH_R)*Math.pow(v,1.15); const br=1-sstep(TL.lift0,TL.lift0+0.5,t);
    ex={p:lerp(swingPose(th).p,0.3,br),tilt:lerp(swingPose(th).tilt,0.42,br)}; }
  else if(t<TL.strike0) th=TH_TOP;
  else if(t<HT[100]){ const v=(t-TL.strike0)/(HT[100]-TL.strike0); th=TH_TOP+(TH_I-TH_TOP)*v*v; }
  else { const v=1-Math.exp(-(t-HT[100])/0.09); th=TH_I+(TH_R+8-TH_I)*v;   // through: nothing stops the hammer now
    const look=sm5(sstep(16.9,17.8,t)); ex={tilt:lerp(swingPose(th).tilt,-0.12,look),p:swingPose(th).p-0.12*look}; }
  return {...base,th,P:swingPose(th,ex)}; }

// dropped hammer (top, after the release): the head slides off the rock and falls, the handle tips onto the floor
const DROP=(()=>{ const hc=CONTACT.clone().addScaledVector(FWD,-0.12); hc.y=0.048; const dir=dirA(-4); return {hc,dir}; })();
function freeHammer(t){ const u=clamp((t-TL.release)/(TL.land-TL.release)); const v=u*u;
  const bounce=t>TL.land?0.022*Math.max(0,Math.sin(Math.PI*clamp((t-TL.land)/0.14)))+0.006*Math.max(0,Math.sin(Math.PI*clamp((t-TL.land-0.14)/0.08))):0;
  const th=lerp(TH_I,-4,v);
  const hc=HIMP.hc.clone().lerp(DROP.hc,v); hc.y+=bounce;
  const dir=dirA(th), m=dirA(th+90); const g=hc.clone().addScaledVector(dir,-HEADD); return {g,dir,m}; }

// ---------------------------------------------------------------- particles: sparks + dust per hit, gold dust on hit 100
const partU={uT:{value:0},uHalf:{value:0},uH:{value:HH},uOrg:{value:CONTACT.clone()},uCen:{value:BCW.clone()}};
{ const Rn=rng(99), A=[]; const nrm=CONTACT.clone().sub(BCW).normalize();
  for(let k=1;k<=100;k++){ const big=k===100, n=big?0:10+Math.round(8*k/99), nd=big?0:3;
    for(let i=0;i<n;i++){ const d=nrm.clone().multiplyScalar(0.7).add(V(Rn()-0.5,Rn()*0.9,Rn()-0.5)).normalize(); const sp=1.2+2.6*Rn();
      A.push([HT[k],d.x*sp,d.y*sp,d.z*sp,0.25+0.45*Rn(),0,0,Rn()]); }
    for(let i=0;i<nd;i++){ const d=nrm.clone().add(V(Rn()-0.5,Rn()*0.4,Rn()-0.5)).normalize(); const sp=0.15+0.3*Rn(); A.push([HT[k],d.x*sp,d.y*sp+0.05,d.z*sp,1.2+0.8*Rn(),2,0,Rn()]); } }
  for(let i=0;i<900;i++){ const d=V(Rn()-0.5,Rn()-0.35,Rn()-0.5).normalize(); const sp=0.3+1.6*Math.pow(Rn(),1.5); A.push([HT[100],d.x*sp,d.y*sp,d.z*sp,1.6+1.6*Rn(),1,1,Rn()]); }
  for(let i=0;i<60;i++){ const d=V(Rn()-0.5,Rn()*0.3,Rn()-0.5).normalize(); const sp=0.3+0.5*Rn(); A.push([HT[100],d.x*sp,d.y*sp,d.z*sp,2.2+Rn(),2,1,Rn()]); }
  const N=A.length, a0=new Float32Array(N*4), a1=new Float32Array(N*4), pos=new Float32Array(N*3);
  A.forEach((r,i)=>{ a0.set([r[0],r[1],r[2],r[3]],i*4); a1.set([r[4],r[5],r[6],r[7]],i*4); });
  const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.BufferAttribute(pos,3)); g.setAttribute('a0',new THREE.BufferAttribute(a0,4)); g.setAttribute('a1',new THREE.BufferAttribute(a1,4));
  const m=new THREE.Points(g,new THREE.ShaderMaterial({uniforms:partU,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
    vertexShader:`attribute vec4 a0,a1; uniform float uT,uHalf,uH; uniform vec3 uOrg,uCen; varying vec3 vC; varying float vA;
      void main(){ float tau=uT-a0.x, life=a1.x, kind=a1.y; vA=0.0; vC=vec3(0.0); vec3 p=uOrg; float sz=0.0;
        bool on=tau>=0.0&&tau<life&&(a1.z<0.5||uHalf>0.5);
        if(on){ vec3 v=a0.yzw; float u=tau/life;
          if(kind<0.5){ p=uOrg+v*tau+vec3(0.0,-4.9,0.0)*tau*tau; if(p.y<0.0) p.y=-p.y*0.25; vC=mix(vec3(1.0,0.78,0.42),vec3(0.95,0.16,0.06),smoothstep(0.0,0.6,u)); vA=(1.0-u)*(1.0-u)*1.6; sz=0.011; }
          else if(kind<1.5){ float k=1.7; vec3 o=uCen+normalize(v+1e-4)*0.18*fract(a1.w*7.7); p=o+v*(1.0-exp(-k*tau))/k+vec3(0.0,0.05*tau,0.0); vC=vec3(1.0,0.74,0.36); vA=smoothstep(0.0,0.08,tau)*(1.0-u)*(0.5+0.5*fract(a1.w*13.1))*1.2; sz=0.006+0.006*fract(a1.w*3.3); }
          else { float k=2.5; p=uOrg+v*(1.0-exp(-k*tau))/k+vec3(0.0,0.06*tau,0.0); vC=vec3(0.62,0.56,0.5); vA=smoothstep(0.0,0.06,tau)*(1.0-u)*0.035; sz=0.05+0.14*tau; } }
        vec4 mv=modelViewMatrix*vec4(p,1.0); gl_Position=on?projectionMatrix*mv:vec4(2.0,2.0,2.0,1.0);
        float px=sz*uH/(-mv.z)*1.3; gl_PointSize=clamp(px,1.0,120.0); vA*=min(1.0,px); }`,
    fragmentShader:`varying vec3 vC; varying float vA; void main(){ float d=length(gl_PointCoord-0.5); float a=smoothstep(0.5,0.0,d); gl_FragColor=vec4(vC*a*a*vA,1.0); }`}));
  m.frustumCulled=false; m.renderOrder=6; scene.add(m); var PARTS=m; }

// ---------------------------------------------------------------- hit 100: the boulder bursts open on a gold light
const CH_N=80;
const chunkMat=new THREE.MeshStandardMaterial({color:0x3a3632,roughness:0.9,map:rockMat.map,emissive:0xff4a1c,emissiveIntensity:0});
const chunks=new THREE.InstancedMesh((()=>{ const g=new THREE.IcosahedronGeometry(1,1); const p=g.attributes.position; const Rn=rng(8);
  for(let i=0;i<p.count;i++){ const s=0.75+0.5*h3(p.getX(i)*3.1,p.getY(i)*3.1,p.getZ(i)*3.1); p.setXYZ(i,p.getX(i)*s,p.getY(i)*s,p.getZ(i)*s); } g.computeVertexNormals(); return g; })(),chunkMat,CH_N);
chunks.castShadow=true; chunks.receiveShadow=true; chunks.frustumCulled=false; scene.add(chunks);
const CH=(()=>{ const Rn=rng(17), A=[]; while(A.length<CH_N){ const d=V(Rn()*2-1,Rn()*2-1,Rn()*2-1); if(d.length()>1) continue; const len=d.length(); const dir=d.clone().normalize();
    const r=rDir(dir)*0.92; const lp=dir.clone().multiplyScalar(r*Math.cbrt(Math.max(0.12,len))); const w=lp.clone().multiply(BSC).applyAxisAngle(UP,BROT).add(BCW);
    if(w.y<0.04) continue; const low=w.y<0.28; const sz=(low?0.15:0.09)+0.1*Rn();
    const out=w.clone().sub(BCW).setY(0).normalize(); const vel=dir.clone().applyAxisAngle(UP,BROT).multiplyScalar(low?0.25+0.3*Rn():0.6+1.5*Rn()).add(out.multiplyScalar(0.2)).add(V(0,low?0.05:0.35*Rn(),0));
    A.push({p:w,v:vel,s:V(sz*(0.8+0.5*Rn()),sz*(0.7+0.5*Rn()),sz*(0.8+0.5*Rn())),ax:V(Rn()-0.5,Rn()-0.5,Rn()-0.5).normalize(),w:(Rn()-0.5)*5}); } return A; })();
const goldLight=new THREE.PointLight(PAL.GOLD,0,6,1.6); goldLight.position.copy(BCW); scene.add(goldLight);
const goldCore=new THREE.Mesh(new THREE.SphereGeometry(0.15,24,16),new THREE.MeshBasicMaterial({color:0xffd590,transparent:true,opacity:0,fog:false})); goldCore.position.copy(BCW); scene.add(goldCore);
const goldHalo=SLD.glowSprite(scene,0xffc870,0); goldHalo.position.copy(BCW);
const goldHalo2=SLD.glowSprite(scene,0xe8a850,0); goldHalo2.position.copy(BCW);
const RAYS=(()=>{ const Rn=rng(23), G=new THREE.Group(); const rayU={uA:{value:0},uT:{value:0}};
  for(let i=0;i<14;i++){ const len=1.6+1.4*Rn(), r=0.06+0.1*Rn(); const g=new THREE.ConeGeometry(r,len,24,1,true); g.translate(0,-len/2,0); g.rotateX(Math.PI);
    const m=new THREE.Mesh(g,new THREE.ShaderMaterial({uniforms:{...rayU,uS:{value:Rn()}},transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,side:THREE.DoubleSide,fog:false,
      vertexShader:`varying float vV; varying vec3 vN,vP; void main(){ vV=uv.y; vec4 mv=modelViewMatrix*vec4(position,1.0); vP=mv.xyz; vN=normalize(normalMatrix*normal); gl_Position=projectionMatrix*mv; }`,
      fragmentShader:`uniform float uA,uT,uS; varying float vV; varying vec3 vN,vP; void main(){ float edge=pow(abs(dot(normalize(vN),normalize(-vP))),1.5);
        float a=pow(vV,1.6)*edge*uA*(0.75+0.25*sin(uT*3.0+uS*20.0)); gl_FragColor=vec4(vec3(1.0,0.72,0.34)*a*0.22,1.0); }`}));
    const d=V(Rn()-0.5,0.15+Rn()*0.9,Rn()-0.5).normalize(); m.quaternion.setFromUnitVectors(UP,d); G.add(m); }
  G.position.copy(BCW); G.userData.u=rayU; scene.add(G); return G; })();
// keep the halos and rays out of the floor mirror (they wash it out), like the beam
S.NOREFL.push(redHalo,goldHalo,goldHalo2,RAYS,goldCore,PARTS);

// ---------------------------------------------------------------- crack state
function crackAt(t,half){ // continuous hit count: each hit's crack spreads over ~0.1 s
  const k=hitsAt(t,half); const kk=Math.min(k,99); let c=kk; if(kk>=1&&kk<99){ const D=HT[kk+1]-HT[kk]; c=kk-1+sstep(HT[kk],HT[kk]+Math.min(0.12,D*0.9),t); } else if(kk===99) c=98+sstep(HT[99],HT[99]+0.12,t);
  let pulse=0; for(let j=Math.max(1,kk-25);j<=kk;j++) pulse+=Math.exp(-(t-HT[j])/0.11)*0.9; pulse=Math.min(pulse,1.6);
  const cool=half===0?sstep(TL.cool0,TL.cool1,t):0;
  const fin=half===0?1.1*sstep(TL.fin0,TL.fin0+0.35,t)*(1-sstep(TL.fin1-0.6,TL.fin1,t)):0;
  // bottom, waiting for 100: the glow breathes with him (pressure still inside)
  const breathe=half===1&&t>HT[99]?0.12*Math.sin(2*Math.PI*0.62*(t-TL.rest))*sstep(HT[99],TL.breath,t):0;
  return {n:c/100,pulse,cool,fin,heat:1+breathe+(half===1?0.35*sstep(TL.lift0,HT[100],t):0)}; }

// ---------------------------------------------------------------- camera: three-quarter, low, looking slightly up
const QC=(q.get('cam')||'').split(',').map(Number);
const CT=QC.length===6?V(QC[3],QC[4],QC[5]):V(-0.02,0.98,0.0);
const CAM0=QC.length===6?V(QC[0],QC[1],QC[2]):V(-0.02+4.05*1.1,0.3,3.6*1.1);
function camAt(t,half){ let p=CAM0.clone(), l=CT.clone();
  p.x+=0.05*Math.sin(t*0.21); p.z-=0.12*sstep(0,14,t);          // a slow push across the build-up
  if(half===0){ const u=sm5(sstep(TL.tilt0,TL.tilt1,t)); const fo=CONTACT.clone().lerp(BCW,0.35); l.lerp(fo,u); p.lerp(fo.clone().add(V(1.6,0.1,1.5)),u*0.55); }
  else { const u=sm5(sstep(HT[100]+0.1,DUR,t)); p.lerp(p.clone().add(V(0.1,0.12,0.35)),u); }
  return {p,l}; }
function shakeAt(t,half){ let s=0; const k=hitsAt(t,half);
  for(let j=Math.max(1,k-20);j<=k;j++){ const a=j===100?5.0:0.35+0.85*j/99; s+=a*Math.exp(-(t-HT[j])/(j===100?0.22:0.07)); } return Math.min(s,j100(t,half)?6:1.6); }
const j100=(t,half)=>half===1&&t>=HT[100];

// ---------------------------------------------------------------- one sub-frame
function setT(t,half){
  const M=manAt(t,half);
  let P=M.P; const geo=M.free?null:hammerGeom(P,M.th);
  let hp;
  if(!M.free){ hp=placeHammer(geo.g,geo.dir,geo.m); }
  else { const f=freeHammer(t); hp=placeHammer(f.g,f.dir,f.m); }
  if(M.wHands>0&&geo){ const g2=geo.g.clone().addScaledVector(geo.dir,lerp(0.06,0.2,geo.s));
    P={...P,tL:geo.g,tR:g2,wL:M.wHands,wR:M.wHands,pL:V(-0.4,-0.7,0.6),pR:V(-0.4,-0.7,-0.6)}; }
  else if(M.wHands>0&&M.free){ const f=freeHammer(TL.release); const g2=f.g.clone().addScaledVector(f.dir,0.06);
    P={...P,tL:f.g,tR:g2,wL:M.wHands,wR:M.wHands,pL:V(-0.4,-0.7,0.6),pR:V(-0.4,-0.7,-0.6)}; }
  R.poseFig(man,R.skel(P,M.root,M.yaw)); man.setAlpha(M.alpha);
  // boulder + cracks
  const C=crackAt(t,half); const burst=j100(t,half);
  rock.visible=!burst; rockU.uN.value=C.n; rockU.uPulse.value=C.pulse; rockU.uCool.value=C.cool; rockU.uFin.value=C.fin; rockU.uHeat.value=C.heat;
  const glow=burst?0:(0.06+2.2*Math.pow(C.n,1.6))*(1+0.6*C.pulse)*C.heat*(1-C.cool);
  redLight.position.copy(CONTACT).add(V(0.25,0.1,0.25)); redLight.intensity=glow*0.25;
  redHalo.position.copy(CONTACT.clone().lerp(BCW,0.4)); redHalo.scale.setScalar(0.9+0.9*C.n); redHalo.material.opacity=Math.min(0.22,0.02+0.1*Math.pow(C.n,1.5)*(1+0.5*C.pulse))*(1-C.cool)*(burst?0:1)+C.fin*0.03;
  // burst
  const tau=burst?t-HT[100]:-1;
  if(tau>=0){ const k=1.6; const tmp=new THREE.Object3D();
    CH.forEach((c,i)=>{ const s=(1-Math.exp(-k*tau))/k; const p=c.p.clone().addScaledVector(c.v,s); p.y-=0.12*tau*tau; p.y=Math.max(p.y,c.s.y*0.7);
      tmp.position.copy(p); tmp.scale.copy(c.s); tmp.quaternion.setFromAxisAngle(c.ax,c.w*s); tmp.updateMatrix(); chunks.setMatrixAt(i,tmp.matrix); });
    chunks.instanceMatrix.needsUpdate=true; chunks.visible=true; chunkMat.emissiveIntensity=0.35*Math.exp(-tau/0.12);
    const env=sstep(0,0.06,tau)*(0.62+0.38*Math.exp(-tau/0.5));
    goldLight.intensity=3*env; goldCore.material.opacity=0.85*env; goldCore.scale.setScalar(0.7+0.5*sstep(0,0.4,tau));
    goldHalo.material.opacity=0.55*env; goldHalo.scale.setScalar(1.2+0.6*sstep(0,0.5,tau)); goldHalo2.material.opacity=0.16*env; goldHalo2.scale.setScalar(3.4);
    RAYS.visible=true; RAYS.userData.u.uA.value=env*sstep(0,0.25,tau); RAYS.userData.u.uT.value=t; RAYS.rotation.y=0.05*tau; }
  else { chunks.visible=false; goldLight.intensity=0; goldCore.material.opacity=0; goldHalo.material.opacity=0; goldHalo2.material.opacity=0; RAYS.visible=false; }
  partU.uT.value=t; partU.uHalf.value=half;
  // camera + shake
  const c=camAt(t,half); cam.position.copy(c.p); cam.lookAt(c.l);
  // both halves: shift the frame window down (same angle) so the stage sits clear of the divider text and the platform caption area
  cam.setViewOffset(W,HH,0,Math.round((half===1?0.13:-0.01)*HH),W,HH);   // bottom a little higher: the watermark sits on the floor reflection, not the boulder
  const sh=shakeAt(t,half); if(sh>0){ cam.rotateX(0.0035*sh*Math.sin(t*151.0+half)); cam.rotateY(0.0035*sh*Math.sin(t*113.0+1.3)); cam.position.y+=0.004*sh*Math.sin(t*97.0); }
  const pay=burst?0.14*sstep(0,0.6,tau):0;
  S.tick(t,pay);
  return {M,C}; }

// ---------------------------------------------------------------- split-screen render: top half then bottom half, motion-blurred
const acc=document.createElement('canvas'); acc.width=W; acc.height=H; const actx=acc.getContext('2d');
const fastAt=t=>t>HT[8]&&t<HT[99]+0.05;
window.renderAt=function(t,Ksub=3){
  actx.globalAlpha=1; actx.fillStyle='#000'; actx.fillRect(0,0,W,H);
  for(const half of [0,1]){ let K=Ksub, shutter=1/60;
    if(fastAt(t)){ K=Math.max(Ksub,5); shutter=1/40; }
    if(half===1&&t>HT[100]-0.05&&t<HT[100]+0.3) K=Math.max(Ksub,7);
    for(let k=0;k<K;k++){ const tt=clamp(t+(K>1?(k/(K-1)-0.5)*shutter:0),0,DUR-1e-4); setT(tt,half); S.renderer.shadowMap.needsUpdate=true; S.composer.render();
      actx.globalAlpha=1/(k+1); actx.drawImage(S.renderer.domElement,0,half*HH); } }
  return acc.toDataURL('image/jpeg',0.95); };
// per-frame numbers for the overlay and the sound
window.metaAt=t=>({t,top:hitsAt(t,0),bot:hitsAt(t,1)});
window.events={...TL,HT,TAU,TH_I,TH_R,contact:CONTACT.toArray(),boulder:BCW.toArray()};
window.ready=true;
