// Born Rich (Slow Light Dark). Three cream runners on one dark track: MOTIVATION sprints and burns out, DISCIPLINE
// keeps a steady pace, EGO jogs, takes the lead and celebrates early. The series gold lamp follows the race. Then a
// black car with red tail lights blasts past in the near lane, snaps the finish tape and skids to a stop; the lamp
// swings onto it. The three freeze in the dark and turn to look. (Overlay asks: WAS IT EVER A FAIR RACE?)
//
// Track runs along +x (start x=-12, finish x=12); lanes at z = -0.95 / 0 / +0.95; the car's lane is z = +2.4 (camera side).
// renderAt(t) is pure (no state between frames), so frames can render in parallel workers.
import * as THREE from 'three';
import * as SLD from './sld.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
const {V,clamp,sstep,lerp,sm5,PAL,rng,rotY,yawOf}=SLD;
const TL=await (await fetch('./timeline.json')).json();
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960, DUR=TL.duration;
const X0=TL.startX, XF=TL.finishX, TF=TL.freeze, TC=TL.carCross;

// ---------------------------------------------------------------- stage (lamp moves with the race)
const LAMP_H=8.5;   // higher than the pilot's 4.6 m: one pool has to hold three wide lanes and a spread-out pack
const S=SLD.createStage({W,H,lamp:V(X0,LAMP_H,0.05),lampTarget:V(X0,0,0),cone:0.5,spot:175,beam:0.05,motes:14000,moteSpan:56,moteCx:2});
S.scene.fog.density=0.024;   // a 40 m track and a camera up to 24 m away: much lighter fog than the pilot
const {scene,cam}=S; const BEAM=S.NOREFL[0];
const R=SLD.createRig(scene);

// ---------------------------------------------------------------- race: speed profiles integrated once (pure lookups)
const DT=1/240, NS=Math.ceil((DUR+1)/DT);
const ramp=(t,a,b,v0,v1)=>lerp(v0,v1,sstep(a,b,t));
const stopK=t=>1-sstep(TF-0.15,TF+0.25,t);                              // everyone halts at the freeze
const SPEED={
  M:t=>t<TL.go?0:ramp(t,TL.go,1.0,0,7.0)*(1-sstep(TL.burnout0,TL.burnout1,t)),   // all-out sprint, then burns out
  D:t=>t<TL.go?0:ramp(t,TL.go,1.2,0,4.8)*stopK(t),                              // steady, never stops
  E:t=>t<TL.go?0:(ramp(t,TL.go,1.2,0,4.0)+ramp(t,TL.egoBoost,TL.egoBoost+0.6,0,3.5)-ramp(t,TL.celebrate,TL.celebrate+0.7,0,4.85))*stopK(t)};  // cruise, surge as Motivation fades, celebrate early
const XS={}; for(const k in SPEED){ const a=new Float32Array(NS); let x=X0; for(let i=0;i<NS;i++){ a[i]=x; x+=SPEED[k](i*DT)*DT; } XS[k]=a; }
const xAt=(k,t)=>{ const f=clamp(t,0,DUR)/DT, i=Math.min(NS-2,Math.floor(f)); return lerp(XS[k][i],XS[k][i+1],f-i); };
const LANE={M:2.8,D:0,E:-2.8};   // wide lanes: from the raised side camera each runner gets his own band of the frame

// ---------------------------------------------------------------- runners
const figs={M:R.makeFig(PAL.CREAM,'m',{rim:0.18,lift:0.08}),D:R.makeFig(PAL.CREAM,'d',{rim:0.18,lift:0.08}),E:R.makeFig(PAL.CREAM,'e',{rim:0.18,lift:0.08})};
// Ego's aura: when he surges, his rim and self-glow run hot (amber-red) and a soft halo rides behind him; it dies at the freeze
const egoHalo=SLD.glowSprite(scene,0xff7a2a,0); S.NOREFL.push(egoHalo);
function egoAura(t){ return sstep(TL.egoBoost,TL.egoBoost+0.5,t)*(1-0.35*sstep(TL.celebrate,TL.celebrate+0.8,t))*(1-sstep(TF,TF+0.6,t)); }
const P0=R.P0;
const CROUCH={...P0,p:0.9,tilt:-0.55,aL:0.95,aR:-0.15,kL:1.9,kR:1.25,dy:-0.03,sL:0.5,sR:0.5,eL:0.3,eR:0.3};
const RUN={...P0,p:0.3,tilt:-0.12,aL:0.05,aR:0.05,kL:0.35,kR:0.35,sL:0,sR:0,eL:1.55,eR:1.55};
const SWAG={...P0,p:-0.04,tilt:-0.24,aL:0.03,aR:0.03,kL:0.2,kR:0.2,sL:0.05,sR:0.05,eL:0.9,eR:0.9};
const CHEER={...P0,p:-0.12,tilt:-0.4,hy:0.55,ty:0.35,sL:2.75,sR:2.95,eL:0.35,eR:0.25,kL:0.15,kR:0.15};
const SPENT={...P0,p:0.95,tilt:0.28,aL:0.32,aR:0.22,kL:0.55,kR:0.48,dy:-0.08,sL:0.55,sR:0.55,eL:0.2,eR:0.2};
const STAND={...P0,p:0.06,kL:0.08,kR:0.08};
// stride per gait cycle grows with speed (cadence about 1.45 cycles/s when running)
function runPose(base,dist,v,amp,{A=0.62,K=1.35,arm=0.75}={}){ const ph=dist/Math.max(1.3,0.36*Math.max(v,0.1)+0.9)*2*Math.PI;   // stride per cycle: ~3.4 m at 7 m/s (about 2 cycles/s)
  const P=R.gait(base,ph,amp,A,K,arm); P.dy=(P.dy||0)-0.025*amp+0.05*amp*Math.abs(Math.cos(ph)); return P; }
function handsOn(P,root,yaw){ const J=R.skel(P,root,yaw); const f=J.fwd;
  return {...P,tL:J.kL.clone().addScaledVector(f,0.06).add(V(0,0.04,0)),tR:J.kR.clone().addScaledVector(f,0.06).add(V(0,0.04,0)),wL:1,wR:1,pL:V(-0.3,-0.4,0.8),pR:V(-0.3,-0.4,-0.8)}; }
const lookAtCar=(t,P,k)=>{ const u=sm5(sstep(TL.look0,TL.look1,t))*k; return {...P,hy:lerp(P.hy,-0.55,u),ty:lerp(P.ty,-0.2,u),tilt:lerp(P.tilt,0.05,u)}; };
function runner(k,t){
  const x=xAt(k,t), v=SPEED[k](t), root=V(x,0,LANE[k]), yaw=0;
  const go=sm5(sstep(TL.go-0.05,TL.go+0.35,t));
  const amp=clamp(v/2.6,0,1)*(t<TF?1:1-sstep(TF-0.1,TF+0.25,t));
  let P;
  if(k==='M'){ const sp=sstep(TL.burnout0+0.6,TL.burnout1,t); const run=runPose(RUN,x-X0,v,amp*1.05,{A:0.7,K:1.5,arm:0.9});
    P=R.blend(R.blend(CROUCH,run,go),SPENT,sm5(sp)); P.p+=0.05*Math.sin(2*Math.PI*1.6*t)*sp; if(sp>0.6) P=handsOn(P,root,yaw); }
  else if(k==='D'){ const run=runPose(RUN,x-X0,v,amp,{A:0.55,K:1.2,arm:0.62}); P=R.blend(CROUCH,run,go); if(t>TF-0.1) P=R.blend(P,STAND,sm5(sstep(TF-0.1,TF+0.3,t))); }
  else { const ch=sm5(sstep(TL.celebrate,TL.celebrate+0.5,t)); const base=R.blend(SWAG,CHEER,ch);
    const run=runPose(base,x-X0,v,Math.max(amp,0.35*(1-sstep(TF,TF+0.3,t))),{A:0.45-0.2*ch,K:0.9-0.4*ch,arm:0.5*(1-ch)});
    P=R.blend(CROUCH,run,go); P.ty+=0.12*Math.sin(2*Math.PI*1.1*t)*(1-ch);                 // swagger
    if(t>TF){ const dn=sm5(sstep(TF,TF+0.7,t)); P.sL=lerp(P.sL,1.2,dn); P.sR=lerp(P.sR,1.0,dn); P.hy=lerp(P.hy,0,dn); P.ty=lerp(P.ty,0,dn); } }
  if(t>TF) P=lookAtCar(t,P,1);
  return {P,root,yaw,x}; }

// ---------------------------------------------------------------- track: start line, faint lanes, finish posts and tape
const lineMat=new THREE.MeshStandardMaterial({color:0xcfc6b4,roughness:0.8,emissive:0xcfc6b4,emissiveIntensity:0.04});
const finMat=new THREE.MeshStandardMaterial({color:0xede6d6,roughness:0.7,emissive:0xede6d6,emissiveIntensity:0.1});
function stripe(x0,x1,z0,z1,mat){ const m=new THREE.Mesh(new THREE.PlaneGeometry(x1-x0,z1-z0),mat); m.rotation.x=-Math.PI/2; m.position.set((x0+x1)/2,0.003,(z0+z1)/2); m.receiveShadow=true; scene.add(m); return m; }
stripe(X0-0.55,X0-0.45,-4.0,4.0,lineMat);
stripe(XF-0.08,XF+0.08,-4.2,5.6,finMat);
const laneMat=new THREE.MeshStandardMaterial({color:0x3a3a40,roughness:0.85,transparent:true,opacity:0.55});
for(const z of [-4.2,-1.4,1.4,4.2]) stripe(X0-0.5,XF+6,z-0.012,z+0.012,laneMat);
const tickMat=new THREE.MeshStandardMaterial({color:0x6a6a72,roughness:0.8,transparent:true,opacity:0.6});
for(let x=X0+2;x<XF+8;x+=2) for(const z of [-4.2,-1.4,1.4,4.2]) stripe(x-0.03,x+0.03,z-0.28,z+0.28,tickMat);   // ticks every 2 m: the ground visibly rushes past
const POSTS=[V(XF,0,-4.1),V(XF,0,7.0)], TAPE_H=1.12;
const postMat=new THREE.MeshStandardMaterial({color:0x8a8f98,roughness:0.5,metalness:0.2});
for(const p of []){ const m=new THREE.Mesh(new THREE.CylinderGeometry(0.035,0.04,TAPE_H+0.08,16),postMat); m.position.copy(p).add(V(0,(TAPE_H+0.08)/2,0)); m.castShadow=true; scene.add(m); }
const TSEG=60, tapeMat=new THREE.MeshStandardMaterial({color:0xede6d6,roughness:0.6,emissive:0xede6d6,emissiveIntensity:0.12,side:THREE.DoubleSide});
const tape=new THREE.InstancedMesh(new THREE.BoxGeometry(1,0.045,0.004),tapeMat,TSEG); tape.castShadow=true; tape.frustumCulled=false;
const SPAN=POSTS[1].z-POSTS[0].z, BREAKZ=4.7, tmpO=new THREE.Object3D();
// one point on the tape: u in 0..1 from post A to post B
function tapePoint(u,t){ const z=lerp(POSTS[0].z,POSTS[1].z,u), sag=0.05*4*u*(1-u); const p=V(XF,TAPE_H-sag+0.012*Math.sin(t*3+u*9),z);
  if(t<TC) return p;
  const tau=t-TC, ub=(BREAKZ-POSTS[0].z)/SPAN, left=u<ub; const post=left?POSTS[0]:POSTS[1];
  const d=Math.abs(z-post.z);                                                       // distance along the tape from its post
  const sw=1-Math.exp(-tau/0.18);                                                   // whip forward and drop
  const ang=lerp(0,1.45,sw)+0.18*Math.exp(-tau/0.6)*Math.sin(tau*14);
  const dir=V(Math.sin(ang)*0.55*(1-sstep(0.2,1.6,tau)),-Math.sin(ang),Math.cos(ang)*(left?1:-1)).normalize();
  const q2=post.clone().add(V(0,TAPE_H,0)).addScaledVector(dir,d); q2.x+=0.9*d*Math.exp(-tau/0.25)*(1-Math.exp(-tau/0.05))*0.6;
  q2.x+=0.04*Math.sin(d*7-tau*10)*Math.exp(-tau/0.8); q2.y=Math.max(q2.y,0.006); return q2; }
function drawTape(t){ for(let i=0;i<TSEG;i++){ const u0=i/TSEG, u1=(i+1)/TSEG; const ub=(BREAKZ-POSTS[0].z)/SPAN;
    const a=tapePoint(u0,t), b=tapePoint(Math.min(u1,t>=TC&&u0<ub&&u1>ub?ub-1e-4:u1),t); const d=b.clone().sub(a); const len=d.length();
    tmpO.position.copy(a).add(b).multiplyScalar(0.5); tmpO.scale.set(Math.max(len,1e-4)*1.04,1,1); tmpO.quaternion.setFromUnitVectors(V(1,0,0),d.normalize()); tmpO.updateMatrix(); tape.setMatrixAt(i,tmpO.matrix); }
  tape.instanceMatrix.needsUpdate=true; }

// ---------------------------------------------------------------- the car: black coupe, red tail lights, cream rider
const pm=new THREE.PMREMGenerator(S.renderer); const ENV=pm.fromScene(new RoomEnvironment(),0.04).texture;
const paint=new THREE.MeshPhysicalMaterial({color:0x030304,metalness:0.6,roughness:0.28,clearcoat:1,clearcoatRoughness:0.06,envMap:ENV,envMapIntensity:0.22});
SLD.rimify(paint,0x9fb2d6,0.12,'paint');
const CAR=new THREE.Group(); scene.add(CAR); const CS=1.12;
// body: a lofted superellipse section along the length (smooth, low, wide), with a canopy bump; the canopy is tinted glass
function carBody(){ const NU=72, NV=56, L=2.3, g=new THREE.BufferGeometry(); const pos=[], col=[], idx=[];
  const hw=u=>0.98*Math.pow(Math.max(0,1-Math.pow(Math.abs(u),5)),0.22)*(1-0.05*u);                   // half width
  const ys=u=>0.74-0.16*Math.max(0,u-0.35)/0.65*1.2+0.05*Math.max(0,-u-0.5)/0.5;                   // shoulder height: low nose, high tail
  const cab=u=>0.42*Math.exp(-Math.pow((u+0.12)/0.36,2)*(u>-0.12?1.6:1.0));                         // canopy
  const y0=u=>0.2+0.04*Math.pow(Math.abs(u),4);
  for(let i=0;i<=NU;i++){ const u=-1+2*i/NU, w=Math.max(hw(u),0.02), x=u*L, b=y0(u), sh=ys(u);
    for(let j=0;j<=NV;j++){ const th=j/NV*2*Math.PI, c=Math.cos(th), sn=Math.sin(th);
      const z=w*Math.sign(c)*Math.pow(Math.abs(c),2/4.5);
      let y, glassy=0;
      if(sn>=0){ const zc=z/w; const top=sh+cab(u)*Math.pow(Math.max(0,1-Math.pow(zc/0.78,2)),0.55); const mid=(b+sh)/2+0.06;
        y=mid+(top-mid)*Math.pow(sn,2/4.0); glassy=(cab(u)>0.08&&y>sh+0.04)?1:0; }
      else { const mid=(b+sh)/2+0.06; y=mid+(b-mid)*Math.pow(-sn,2/6); }
      pos.push(x,y,z); const k=glassy?[0.05,0.07,0.09]:[0.02,0.02,0.025]; col.push(...k); } }
  for(let i=0;i<NU;i++) for(let j=0;j<NV;j++){ const a=i*(NV+1)+j, b2=a+NV+1; idx.push(a,b2,a+1, b2,b2+1,a+1); }
  g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3)); g.setAttribute('color',new THREE.Float32BufferAttribute(col,3)); g.setIndex(idx); g.computeVertexNormals();
  const m=new THREE.Mesh(g,paint); m.castShadow=true; m.receiveShadow=true; CAR.add(m); return m; }
paint.vertexColors=true; paint.color.set(0xffffff); carBody();
const tail=new THREE.Mesh(new THREE.BoxGeometry(0.05,0.045,1.5),new THREE.MeshBasicMaterial({color:new THREE.Color(PAL.RED).multiplyScalar(3.2),toneMapped:false}));
tail.position.set(-2.27,0.76,0); CAR.add(tail);
const headM=new THREE.MeshBasicMaterial({color:new THREE.Color(0xfff2dc).multiplyScalar(2.5),toneMapped:false});
for(const z of [-0.62,0.62]){ const h=new THREE.Mesh(new THREE.BoxGeometry(0.05,0.03,0.34),headM); h.position.set(2.18,0.5,z); h.rotation.z=-0.5; CAR.add(h); }
const WHEELS=[]; { const tyre=new THREE.MeshStandardMaterial({color:0x111113,roughness:0.85}), rim=new THREE.MeshStandardMaterial({color:0x2c2d31,metalness:0.8,roughness:0.35,envMap:ENV,envMapIntensity:0.4});
  for(const [x,z] of [[1.45,0.84],[1.45,-0.84],[-1.42,0.86],[-1.42,-0.86]]){ const g=new THREE.Group(); g.position.set(x,0.34,z);
    const ty=new THREE.Mesh(new THREE.CylinderGeometry(0.34,0.34,0.26,32),tyre); ty.rotation.x=Math.PI/2; g.add(ty);
    const sp=new THREE.Group(); { const b=new THREE.Mesh(new THREE.CylinderGeometry(0.22,0.22,0.02,24),rim); b.rotation.x=Math.PI/2; sp.add(b); } sp.position.z=Math.sign(z)*0.135; g.add(sp);
    g.children.forEach(c=>{ c.castShadow=true; }); CAR.add(g); WHEELS.push({g,sp}); } }
const tailHalo=SLD.glowSprite(scene,0xff2a1c,0); const exh=[SLD.glowSprite(scene,0xff5a1e,0),SLD.glowSprite(scene,0xff3a10,0)];
const headHalo=[SLD.glowSprite(scene,0xfff0d0,0),SLD.glowSprite(scene,0xfff0d0,0)];
const carLight=new THREE.PointLight(0xff3a24,0,6,2); scene.add(carLight);
CAR.scale.setScalar(CS); S.NOREFL.push(tailHalo,...exh,...headHalo);
// trail streaks behind the tail light (red light painting during the blast)
const trail=new THREE.Mesh(new THREE.PlaneGeometry(1,1),new THREE.ShaderMaterial({uniforms:{uA:{value:0}},transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,side:THREE.DoubleSide,fog:false,
  vertexShader:`varying vec2 vU; void main(){ vU=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
  fragmentShader:`uniform float uA; varying vec2 vU; void main(){ float a=pow(vU.x,2.2)*exp(-pow((vU.y-0.5)*5.0,2.0)); gl_FragColor=vec4(vec3(1.0,0.16,0.08)*a*uA,1.0); }`}));
scene.add(trail); S.NOREFL.push(trail);
// car path: constant 21 m/s in the near lane, crosses the line at TC, brakes hard and drifts to a stop under the lamp
const VC=26, DEC=110, LANEC=4.7;   // its own near lane, between the runners and the camera
function carAt(t){ const tau=t-TC; let x, v;
  if(tau<0){ x=XF+VC*tau; v=VC; } else { const ts=VC/DEC, u=Math.min(tau,ts); x=XF+VC*u-0.5*DEC*u*u; v=Math.max(0,VC-DEC*tau); }
  const dr=sm5(sstep(TC+0.05,TL.carStop+0.05,t)); const yaw=-0.12*dr, z=LANEC+0.15*dr;   // a short twitch as it brakes
  return {x,z,yaw,v,dist:x-(XF-VC*3)}; }
const CAR_STOP=carAt(DUR).x;

// ---------------------------------------------------------------- dust kicked up by the skid and by the runners' first steps
const puffU={uT:{value:0},uH:{value:H}};
{ const Rn=rng(5), A=[]; const add=(t0,o,v,life,amp)=>A.push([t0,o.x,o.y,o.z,v.x,v.y,v.z,life,amp]);
  for(let i=0;i<160;i++){ const t0=TC+0.05+Rn()*0.5, c=carAt(t0); add(t0,V(c.x-1.6*CS+Rn()*0.5,0.05,c.z+(Rn()<0.5?-1:1)*0.95*CS),V(-1.5-2*Rn(),0.3+0.6*Rn(),(Rn()-0.5)*1.2),1.6+Rn(),0.8); }
  for(const k of ['M','D','E']) for(let i=0;i<14;i++) add(TL.go+0.05+Rn()*0.35,V(X0+0.2*Rn(),0.03,LANE[k]+(Rn()-0.5)*0.3),V(-0.4-0.6*Rn(),0.15+0.3*Rn(),(Rn()-0.5)*0.4),1.2+Rn()*0.6,0.6);
  const N=A.length, pos=new Float32Array(N*3), a0=new Float32Array(N*4), a1=new Float32Array(N*4);
  A.forEach((r,i)=>{ pos.set([r[1],r[2],r[3]],i*3); a0.set([r[0],r[4],r[5],r[6]],i*4); a1.set([r[7],r[8],0,0],i*4); });
  const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.BufferAttribute(pos,3)); g.setAttribute('a0',new THREE.BufferAttribute(a0,4)); g.setAttribute('a1',new THREE.BufferAttribute(a1,4));
  const m=new THREE.Points(g,new THREE.ShaderMaterial({uniforms:puffU,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
    vertexShader:`attribute vec4 a0,a1; uniform float uT,uH; varying float vA;
      void main(){ float tau=uT-a0.x; vA=0.0; vec3 p=position; float sz=0.02;
        if(tau>0.0&&tau<a1.x){ float k=2.2; p+=a0.yzw*(1.0-exp(-k*tau))/k; p.y+=0.04*tau; vA=a1.y*smoothstep(0.0,0.06,tau)*(1.0-tau/a1.x); sz=0.06+0.25*tau; }
        vec4 mv=modelViewMatrix*vec4(p,1.0); gl_Position=projectionMatrix*mv; gl_PointSize=clamp(sz*uH/(-mv.z),1.0,160.0); }`,
    fragmentShader:`varying float vA; void main(){ float d=length(gl_PointCoord-0.5); float a=smoothstep(0.5,0.0,d); gl_FragColor=vec4(vec3(0.8,0.7,0.55)*a*a*vA*0.09,1.0); }`}));
  m.frustumCulled=false; scene.add(m); }

// ---------------------------------------------------------------- lamp: over the pack, leaning to the leader; swings onto the car
const smoothMax=(a,k=0.6)=>k*Math.log(a.reduce((s,x)=>s+Math.exp(x/k),0));
function lampX(t){ const xs=['M','D','E'].map(k=>xAt(k,t)); const lead=smoothMax(xs), mid=(Math.min(...xs)+lead)/2;
  let x=lerp(mid,lead,0.3);
  x=lerp(x,XF-1.8,sm5(sstep(7.2,8.3,t)));                       // settles near the line as the race closes
  return lerp(x,CAR_STOP-0.2,sm5(sstep(TC+0.02,TC+0.75,t))); }   // the light goes to the car
function lampZ(t){ return lerp(0.05,carAt(DUR).z,sm5(sstep(TC+0.02,TC+0.75,t))); }

// ---------------------------------------------------------------- camera: three-quarter, ahead and to the right of the pack, looking back at them
// fixed, from above and beyond the finish, looking back down the track: depth reads as height in the tall frame
// side-on tracking camera (near side, +z), a little raised so the lanes separate: who is ahead reads at a glance.
// It follows the pack, widening as the gaps open; after the car crosses it settles on the line with the car's tail in frame.
const LANE_MID=0.6, PORTRAIT_W=2*Math.tan(S.cam.fov*Math.PI/360)*(W/H);   // frame width per metre of distance
function camAt(t){ const xm=xAt('M',t), xd=xAt('D',t), xe=xAt('E',t);
  // once Motivation has burned out the camera lets him fall behind and stays with the race
  const drop=sm5(sstep(TL.burnout1+0.3,TL.burnout1+1.6,t)), lo=Math.min(lerp(Math.min(xm,xd,xe),Math.min(xd,xe),drop)), hi=Math.max(xm,xd,xe);
  let cx=(lo+hi)/2+0.35, need=hi-lo+3.4;
  const u=sm5(sstep(TC-0.15,TL.carStop+0.45,t)); cx=lerp(cx,XF+1.4,u); need=lerp(need,10.0,u);
  const d=clamp(need/PORTRAIT_W,13,24);
  const l=V(cx,1.0,LANE_MID), p=V(cx,0.9+0.55*d,LANE_MID+0.85*d);
  return {p,l}; }
const shakeAt=t=>{ let s=0; for(const [t0,a,d] of [[TC-0.05,0.8,0.3],[TL.carStop-0.05,0.5,0.25],[TL.go,0.25,0.15]]) if(t>t0) s+=a*Math.exp(-(t-t0)/d); return s; };

// ---------------------------------------------------------------- one sub-frame
function setT(t){
  const RN={}; for(const k of ['M','D','E']){ const r=runner(k,t); R.poseFig(figs[k],R.skel(r.P,r.root,r.yaw)); RN[k]=r; }
  { const au=egoAura(t), f=figs.E; f.mat.emissiveIntensity=0.08+0.32*au; f.mat.emissive.set(0xede6d6).lerp(new THREE.Color(0xff9a50),au);
    f.mat.userData.rim.value=0.18+0.55*au; const J=R.skel(RN.E.P,RN.E.root,RN.E.yaw); egoHalo.position.copy(J.neck).lerp(J.hip,0.5).add(V(-0.15,0,-0.05));
    egoHalo.scale.set(2.2+0.3*Math.sin(t*11),2.8,1); egoHalo.material.opacity=0.32*au*(0.85+0.15*Math.sin(t*17)); }
  // (finish tape dropped in the side-on version: its near post crossed the frame like a bar)
  // car
  const c=carAt(t), vis=c.x>XF-VC*1.2; CAR.visible=vis;
  CAR.position.set(c.x,0,c.z); CAR.rotation.y=c.yaw; CAR.updateMatrixWorld(true);
  WHEELS.forEach(w=>{ w.sp.rotation.z=-c.dist/(0.34*CS); });

  const blast=vis?sstep(XF-VC*1.15,XF-VC*0.9,c.x):0, fast=clamp(c.v/VC);
  const tl=CAR.localToWorld(V(-2.36,0.7,0)); tailHalo.position.copy(tl); tailHalo.scale.set(0.9,0.3,1); tailHalo.material.opacity=0.3*blast;
  carLight.position.copy(CAR.localToWorld(V(-2.9,0.5,0))); carLight.intensity=(0.08+0.7*fast)*blast;
  exh.forEach((s,i)=>{ const p=CAR.localToWorld(V(-2.4,0.34,i?0.48:-0.48)); s.position.copy(p); const f=0.75+0.25*Math.sin(t*90+i*2.1); s.scale.setScalar(0.55*f*fast+0.05); s.material.opacity=0.85*fast*blast*f; });
  headHalo.forEach((s,i)=>{ s.position.copy(CAR.localToWorld(V(2.3,0.56,i?0.68:-0.68))); s.scale.setScalar(0.5); s.material.opacity=0.45*blast; });
  trail.visible=fast>0.3&&vis; if(trail.visible){ const L=3.8*fast; trail.position.copy(tl).add(V(-L/2,0,0)); trail.scale.set(L,0.07,1); trail.lookAt(cam.position.clone().setX(trail.position.x)); trail.material.uniforms.uA.value=1.2*fast; }
  // lamp
  const lx=lampX(t), lz=lampZ(t); S.LAMP.set(lx+0.5,LAMP_H,lz+1.6); S.LAMP_T.set(lx,0,lz);   // lamp a little ahead and toward the camera so it lights the runners' faces and sides
  BEAM.position.copy(S.LAMP); const AX=S.LAMP_T.clone().sub(S.LAMP).normalize(); S.beamU.uAxis.value.copy(AX); BEAM.quaternion.setFromUnitVectors(V(0,-1,0),AX);
  S.spot.position.copy(S.LAMP); S.spot.target.position.copy(S.LAMP_T); S.spot.target.updateMatrixWorld();
  puffU.uT.value=t;
  // camera
  const cc=camAt(t); cam.position.copy(cc.p); cam.lookAt(cc.l); cam.updateProjectionMatrix();
  const sh=shakeAt(t); if(sh>0){ cam.rotateX(0.004*sh*Math.sin(t*131)); cam.rotateY(0.004*sh*Math.sin(t*97+1.3)); }
  const go=sstep(TL.go-0.08,TL.go,t)*(1-sstep(TL.go,TL.go+0.5,t));            // the start: the lamp kicks
  S.tick(t,0.35*go+(t>TC?0.12*sstep(TC,TC+0.8,t):0));
  return {RN,c}; }

// ---------------------------------------------------------------- render: motion blur (longer shutter on the blast)
const acc=document.createElement('canvas'); acc.width=W; acc.height=H; const actx=acc.getContext('2d');
window.renderAt=function(t,Ksub=3){ let K=Ksub, sh=1/60;
  if(t>TC-0.75&&t<TC+0.35){ K=Math.max(Ksub,7); sh=1/30; }
  actx.globalAlpha=1; actx.clearRect(0,0,W,H);
  for(let k=0;k<K;k++){ const tt=clamp(t+(K>1?(k/(K-1)-0.5)*sh:0),0,DUR-1e-4); setT(tt); S.renderer.shadowMap.needsUpdate=true; S.composer.render(); actx.globalAlpha=1/(k+1); actx.drawImage(S.renderer.domElement,0,0); }
  return acc.toDataURL('image/jpeg',0.95); };
// screen positions for the overlay labels (heads, car roof) and race numbers for the mix
const proj=v=>{ const p=v.clone().project(cam); return [p.x*0.5+0.5,0.5-p.y*0.5,p.z<1?1:0]; };
window.metaAt=function(t){ const s=setT(t); cam.updateMatrixWorld(); const o={t};
  for(const k of ['M','D','E']){ const J=R.skel(s.RN[k].P,s.RN[k].root,s.RN[k].yaw); o[k]=proj(J.head.clone().add(V(0,0.3,0))); o[k+'x']=s.RN[k].x; o[k+'v']=SPEED[k](t); }
  o.car=proj(CAR.localToWorld(V(-0.9,1.45,0))); o.carX=s.c.x; o.carV=s.c.v; o.carVis=CAR.visible?1:0; return o; };
window.events={...TL,carStopX:CAR_STOP};
window.ready=true;
