// The Rock Never Moved (Slow Light Dark). A cream stickman pushes a boulder every day under the series gold lamp.
// Hard cuts on every push (DAY 1 -> DAY 365), each from a new angle; the rock never moves, two dim figures laugh at
// the edge of the light, and cut by cut he is visibly stronger (F.thick, the rig's muscle scale). On day 365 he steps
// back and looks at his arms. Then, in one continuous shot, he crouches, lifts the rock to his chest and presses it
// overhead: the boom and the lamp flare land together (TL.boom).
//
// World: rock at the origin, man on +x facing -x. renderAt(t) is pure and never blurs across a cut.
import * as THREE from 'three';
import * as SLD from './sld.js';
const {V,clamp,sstep,lerp,sm5,PAL,rng,yawOf}=SLD;
const TL=await (await fetch('./timeline.json')).json();
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960, DUR=TL.duration;

const S=SLD.createStage({W,H,lamp:V(0.75,4.6,0.1),lampTarget:V(0.75,0,0),cone:0.4,spot:70,motes:500});
const R=SLD.createRig(S.scene);
const man=R.makeFig(PAL.CREAM,'hero',{rim:0.16,lift:0.07});
const YAW=yawOf(V(-1,0,0));

// ---------------------------------------------------------------- the boulder (faceted, displaced sphere)
function h3(x,y,z){ const s=Math.sin(x*127.1+y*311.7+z*74.7)*43758.5453; return s-Math.floor(s); }
function vn(x,y,z){ const ix=Math.floor(x),iy=Math.floor(y),iz=Math.floor(z), fx=x-ix,fy=y-iy,fz=z-iz; const u=fx*fx*(3-2*fx),v=fy*fy*(3-2*fy),w=fz*fz*(3-2*fz);
  const L=(a,b,t)=>a+(b-a)*t; const c=(i,j,k)=>h3(ix+i,iy+j,iz+k);
  return L(L(L(c(0,0,0),c(1,0,0),u),L(c(0,1,0),c(1,1,0),u),v),L(L(c(0,0,1),c(1,0,1),u),L(c(0,1,1),c(1,1,1),u),v),w); }
const fbm=(x,y,z)=>vn(x,y,z)*0.55+vn(x*2.1+5,y*2.1,z*2.1)*0.3+vn(x*4.3,y*4.3+9,z*4.3)*0.15;
const CUTS=(()=>{ const Rn=rng(11); const c=[[V(0,-1,0),0.8]]; for(let i=0;i<7;i++){ const n=V(Rn()-0.5,(Rn()-0.35)*0.9,Rn()-0.5).normalize(); c.push([n,0.86+0.1*Rn()]); } return c; })();
function rDir(d){ let r=1+0.16*(fbm(d.x*1.5+3,d.y*1.5,d.z*1.5)-0.5)+0.05*(fbm(d.x*5,d.y*5,d.z*5+2)-0.5);
  for(const [n,o] of CUTS){ const k=d.dot(n); if(k>1e-3) r=Math.min(r,o/k+0.02*(fbm(d.x*7,d.y*7,d.z*7)-0.5)); } return r; }
const BR=0.8;   // taller than his shoulders: he pushes up into it
const rockGeo=(()=>{ const g=new THREE.IcosahedronGeometry(1,40); const p=g.attributes.position; const d=V(0,0,0);
  for(let i=0;i<p.count;i++){ d.set(p.getX(i),p.getY(i),p.getZ(i)).normalize(); const r=rDir(d); p.setXYZ(i,d.x*r,d.y*r,d.z*r); }
  g.computeVertexNormals(); return g; })();
const rock=new THREE.Mesh(rockGeo,new THREE.MeshStandardMaterial({color:0x4a4540,roughness:0.92,map:SLD.noiseTex(512,31,128,70,160,0.18)}));
rock.scale.set(BR*1.05,BR,BR); rock.rotation.y=0.6; rock.castShadow=rock.receiveShadow=true; S.scene.add(rock);
const ROCK0=V(0,BR*0.8-0.01,0);                     // resting centre (the flat bottom cut sits on the floor)

// ---------------------------------------------------------------- the mockers: two dim figures at the edge of the light
const mockers=[R.makeFig(PAL.CREAM,'m1',{rim:0.2,lift:0.02}),R.makeFig(PAL.CREAM,'m2',{rim:0.2,lift:0.02})];
const MOCKAT=[V(-1.55,0,-0.75),V(-1.2,0,-1.3)];

// ---------------------------------------------------------------- dust ring + flare for the lift
const liftL=new THREE.PointLight(0xffd9a0,0,9,1.6); liftL.position.set(2.6,2.3,2.6); S.scene.add(liftL);   // the rock overhead blocks the lamp: a warm front light for the lift
const dust=SLD.glowSprite(S.scene,0xffe2b0,0); const flare=SLD.glowSprite(S.scene,0xfff0c8,0); S.NOREFL.push(dust,flare);

// ---------------------------------------------------------------- timing
const CUT=TL.cuts.map(([t0,day],i)=>({t0,t1:i+1<TL.cuts.length?TL.cuts[i+1][0]:TL.lift.cut,day,i}));
const SHOTS=[...CUT.map(c=>({t0:c.t0,t1:c.t1,name:'push',c})),{t0:TL.lift.cut,t1:DUR,name:'lift'}];
const shotAt=t=>SHOTS.filter(s=>t>=s.t0).pop();
const thickOf=day=>1+1.15*Math.pow(day/365,0.7);          // muscle: 1.0 on day 1, 2.15 on day 365

// ---------------------------------------------------------------- poses
// the push: leaning hard into the rock, back leg driving, hands flat on its face
const PUSHX=1.72;
function pushPose(t,c){ const u=t-c.t0, imp=1-sstep(0,TL.impactLag+0.06,u);          // drives in over the first beat
  const shiver=0.02*Math.sin(t*47+c.i)*sstep(0.1,0.25,u);
  const P={...R.P0,p:1.08+shiver,tilt:-0.65,hy:0,aL:0.42,kL:0.95,aR:-0.78,kR:0.06,dy:0,fx:0.0};
  const slip=0.07*sstep(0.15,c.t1-c.t0,u)*(c.i%2?1:0.5);                                 // the feet slide back: it won't budge
  const root=V(PUSHX+0.16*imp+slip,0,0.02);
  P.tL=V(0.7+0.16*imp+slip*0.3,1.16,0.18); P.tR=V(0.72+0.16*imp+slip*0.3,1.06,-0.16); P.wL=P.wR=1; P.pL=V(-0.3,-1,0.6); P.pR=V(-0.3,-1,-0.6);
  return {P,root}; }
function stopPose(t){ const s=TL.stop; const c=CUT[CUT.length-1]; const {P:P0,root:r0}=pushPose(s.off,c);
  const off=sm5(sstep(s.off,s.back1,t)); const STAND={...R.P0,p:0.06,tilt:0.1};
  let P=R.blend(P0,STAND,off); const root=r0.clone().lerp(V(1.98,0,0.02),off);
  P=R.gait(P,off*Math.PI*1.2,(1-off)*off*3.5);                                            // two steps back
  const lk=sm5(sstep(s.look0,s.look0+0.35,t));                                            // looks down at his arms
  const f=V(-1,0,0); P.tilt=lerp(P.tilt,0.75,lk); P.p=lerp(P.p,0.16,lk);
  P.tL=root.clone().addScaledVector(f,0.36).add(V(0,1.12+0.03*Math.sin(t*3),0.16)); P.tR=root.clone().addScaledVector(f,0.4).add(V(0,1.18,-0.12));
  P.wL=P.wR=lk; P.pL=V(-0.4,-1,0.8); P.pR=V(-0.4,-1,-0.8);
  return {P,root}; }
// the lift: crouch and grip, stand with the rock at the chest, press it overhead
const LIFTX=1.28;
function liftAt(t){ const L=TL.lift;
  const g=sm5(sstep(L.cut,L.grip,t)), ch=sm5(sstep(L.chest0,L.chest1,t)), pr=sstep(L.press0,L.press1,t), prE=1-Math.pow(1-pr,3);
  const root=V(LIFTX,0,0.02);
  const CROUCH={...R.P0,p:0.72,tilt:-0.25,aL:1.15,aR:0.8,kL:1.9,kR:1.45,dy:-0.02};
  const STAND={...R.P0,p:-0.08,tilt:-0.15,aL:0.18,aR:-0.1,kL:0.22,kR:0.18};
  const OVER={...R.P0,p:-0.02,tilt:-0.35,aL:0.22,aR:-0.2,kL:0.12,kR:0.1};
  let P=R.blend(R.blend(R.blend({...R.P0,p:0.2},CROUCH,g),STAND,ch),OVER,prE);
  P.p+=0.025*Math.sin(t*41)*sstep(L.chest0,L.chest0+0.1,t)*(1-pr);                      // strain
  const rc=ROCK0.clone().lerp(V(0.38,1.38,0.02),ch).lerp(V(LIFTX-0.06,2.72,0.02),prE);
  const hold=rc.clone().add(V(0.45,-0.15,0)).lerp(rc.clone().add(V(0.05,-0.62,0)),prE);
  P.tL=hold.clone().add(V(0,0,lerp(0.5,0.38,prE))); P.tR=hold.clone().add(V(0,0,-lerp(0.5,0.38,prE))); P.wL=P.wR=1;
  P.pL=V(-0.6,-0.6,0.9); P.pR=V(-0.6,-0.6,-0.9);
  return {P,root,rc,rot:0.6+0.25*ch-0.15*prE}; }

// ---------------------------------------------------------------- cameras: a new angle on every cut
const CAMS=[
  [V(1.25,1.3,4.6),V(1.2,1.0,0),44],       // DAY 1: side, wide
  [V(3.4,0.45,1.6),V(0.6,1.2,0),50],       // low, behind him: the rock looms
  [V(2.9,0.9,2.9),V(1.2,0.85,0),46],       // three-quarter from behind, the feet sliding back
  [V(0.55,1.5,4.7),V(0.15,1.0,-0.4),54],   // wide, with the two laughing at the edge of the light
  [V(2.4,2.5,3.0),V(1.1,0.9,0),46],        // high three-quarter
  [V(0.7,1.35,4.7),V(0.25,1.0,-0.4),52],   // wide again: still laughing
  [V(3.6,1.9,3.4),V(1.15,1.1,0),34],      // shoulders and arms on the rock (long lens)
  [V(-0.8,0.45,3.3),V(1.0,1.15,0),52],     // low, from the rock's side
  [V(1.25,1.35,4.7),V(1.15,1.0,0),50],      // DAY 365: side, slow push-in through the stop
];
function camFor(sh,t){
  if(sh.name==='lift'){ const u=sstep(TL.lift.cut,DUR,t), b=sm5(sstep(TL.lift.chest0,TL.boom+0.6,t));
    return {pos:V(lerp(2.5,2.8,b),lerp(0.45,0.38,b),lerp(3.2,4.7,b)),tg:V(lerp(0.85,1.15,b),lerp(1.2,1.95,b),0),fov:lerp(52,56,u)}; }
  const c=sh.c, [p,tg,fov]=CAMS[c.i]; const u=clamp((t-c.t0)/(c.t1-c.t0)); const pos=p.clone();
  pos.addScaledVector(tg.clone().sub(p).normalize(),(c.i===8?0.5:0.22)*sm5(u));                       // slow push-in
  const k=Math.exp(-Math.max(0,t-c.t0-TL.impactLag)*14)*(t>=c.t0+TL.impactLag);                       // impact shake
  pos.add(V(0.02*k*Math.sin(t*90),0.025*k*Math.sin(t*77),0));
  return {pos,tg:tg.clone(),fov}; }

// ---------------------------------------------------------------- one frame
function setT(t){ const sh=shotAt(t);
  let P,root,rc=ROCK0.clone(),rot=0.6,thick;
  if(sh.name==='push'){ const c=sh.c; thick=thickOf(c.day); ({P,root}=t>=TL.stop.off&&c.i===CUT.length-1?stopPose(t):pushPose(t,c)); }
  else { thick=thickOf(365); ({P,root,rc,rot}=liftAt(t)); }
  man.thick=thick; R.poseFig(man,R.skel(P,root,YAW));
  rock.position.copy(rc); rock.rotation.set(0,rot,0);
  // mockers: only in their cuts; one points, one doubles over laughing
  const mk=sh.name==='push'&&TL.mock.includes(sh.c.i);
  mockers.forEach((m,j)=>{ m.setAlpha(mk?0.55:0); if(!mk) return; const b=Math.abs(Math.sin(t*9+j));
    const yaw=yawOf(V(PUSHX,0,0).sub(MOCKAT[j]).setY(0).normalize());
    const Q=j===0?{...R.P0,p:0.1+0.08*b,tilt:-0.1,tR:MOCKAT[j].clone().add(V(0.45,1.45,0.25)),wR:1,pR:V(0,-1,-0.5)}
                 :{...R.P0,p:0.55+0.15*b,tilt:0.2,sL:0.6,sR:0.6,eL:1.2,eR:1.2};
    R.poseFig(m,R.skel(Q,MOCKAT[j],yaw)); });
  // the payoff: dust ring on the floor and a flare from the lamp as the rock locks out overhead
  const bk=t>=TL.boom?Math.exp(-(t-TL.boom)*3.2):0;
  dust.position.set(LIFTX-0.1,0.08,0.02); dust.scale.set(2.8*(1-bk)+0.6,0.5,1); dust.material.opacity=0.6*bk;
  liftL.intensity=sh.name==='lift'?30+70*bk:0;
  flare.position.set(LIFTX,2.9,0.1); flare.scale.setScalar(2.2); flare.material.opacity=0.55*bk;
  const c=camFor(sh,t); S.cam.fov=c.fov; S.cam.updateProjectionMatrix(); S.cam.position.copy(c.pos); S.cam.lookAt(c.tg);
  S.tick(t,0.9*bk+0.25*(t>=TL.boom?1:0)); }

// ---------------------------------------------------------------- overlay / sound data
const v3=new THREE.Vector3();
window.metaAt=t=>{ setT(t); S.cam.updateMatrixWorld(); const sh=shotAt(t); const out={shot:sh.name,cut:sh.name==='push'?sh.c.i:-1,day:sh.name==='push'?sh.c.day:365};
  const pr=(p)=>{ v3.copy(p).project(S.cam); return [(v3.x*0.5+0.5)*1080,(0.5-v3.y*0.5)*1920,v3.z<1]; };
  out.mockers=MOCKAT.map(p=>pr(p.clone().add(V(0,1.75,0)))); out.head=pr(man.head.position); return out; };
window.events={...TL};
window.renderAt=(t,K=3)=>{ const sh=shotAt(t); return S.renderAt(setT,t,K,{t0:sh.t0,t1:sh.t1}); };
window.ready=true;
