// The Salary Loop V3 (19.3 s). The frozen plan is STORY.md; every time comes from timeline.json.
// One hero (figure.js HERO), three sets: his bedroom (wake, the calendar tear, the return), his street (morning walk, night walk), his desk (the month).
// The phone faces him; every expense arrives as a buzz on that phone; a tear-off calendar is the only counter.
// renderAt(t) is pure. Units are metres. Each set lives at x = 16 * index; the camera is always in front (+z).
import * as THREE from 'three';
import {createWarmStage,V,clamp,sstep,lerp} from './stage.js';
import * as SLD from './sld.js';
import {createFigure,HERO} from './figure.js';
import * as SETS from './sets.js';
import {createBedSeq} from './bedseq.js';
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960;
const TL=await (await fetch('timeline.json')).json(); const DUR=TL.duration;
const ST=createWarmStage({W,H}); const R=SLD.createRig(ST.scene); const scene=ST.scene; const sm5=SLD.sm5;
const BS=createBedSeq(R);
const lin=(K,t)=>{ if(t<=K[0][0]) return K[0][1]; for(let i=1;i<K.length;i++) if(t<=K[i][0]){ const u=(t-K[i-1][0])/(K[i][0]-K[i-1][0]); return lerp(K[i-1][1],K[i][1],u); } return K[K.length-1][1]; };
const smooth=(K,t)=>SLD.keys(K,t);
// ---------------------------------------------------------------- sets
const SP=16; const sets={bed:SETS.buildBedroom(),street:SETS.buildStreet(),desk:SETS.buildDesk()};
Object.entries(sets).forEach(([k,g],i)=>{ g.position.x=i*SP; g.userData.ox=i*SP; g.visible=false; scene.add(g); });
const SET_OF={bed1:'bed',door:'bed',bed2:'bed',streetAM:'street',streetPM:'street',desk:'desk'};
const sceneAt=t=>TL.scenes.find(s=>t>=s.t0&&t<s.t1)||TL.scenes[TL.scenes.length-1];
// ---------------------------------------------------------------- the hero and the phone
const hero=createFigure(scene,HERO);
const phone=new THREE.Group(); { SETS.B(phone,0.072,0.15,0.01,SETS.M(0x0d0e12,{r:0.3,m:0.4}),0,0,0,{round:0.01}); const scr=new THREE.Mesh(new THREE.PlaneGeometry(0.064,0.136),new THREE.MeshBasicMaterial({color:0xd8e6f6})); scr.position.z=0.0055; phone.add(scr); phone.userData.scr=scr; }
phone.scale.setScalar(1.3); scene.add(phone); const phoneLight=new THREE.PointLight(0xcfe0ff,0,1.6,2); scene.add(phoneLight);
// ---------------------------------------------------------------- the month: day on the pad, tear progress, mood, hope
const DAYS=TL.days;
function dayState(t){ let i=0; for(let k=0;k<DAYS.length;k++) if(t>=DAYS[k][0]) i=k; const n=DAYS[i][1]; const prev=i>0?DAYS[i-1][1]:null;
  const dur=i>0?Math.min(0.32,Math.max(0.1,(DAYS[Math.min(i+1,DAYS.length-1)][0]-DAYS[i][0])*0.9)):0.3; const tear=i>0?clamp((t-DAYS[i][0])/dur):1;
  return {n,prev,tear,left:n===30&&t<3.9?1:31-n,t0:DAYS[i][0]}; }
const buzzAt=t=>{ let b=0; for(const bt of TL.buzz){ const u=t-bt; if(u>=-0.02&&u<0.45) b=Math.max(b,1-u/0.45); } return b; };
const moodAt=t=>smooth(TL.mood,t), hopeAt=t=>smooth(TL.hope,t);
const blinkAt=t=>{ const ph=(t*0.31+0.17)%1; return ph<0.03?1:(ph<0.05?0.5:0); };
function postureFrom(P,hope){ const sag=1-hope; P.p=(P.p||0)+0.3*sag; P.tilt=(P.tilt||0)+0.25*sag; return P; }
// ---------------------------------------------------------------- hero poses (set-local; the set origin is added at the end)
const YAW=d=>SLD.yawOf(d);
function heroPose(t,sc){
  const m=moodAt(t), hope=hopeAt(t);
  // ---- the bed: the forward wake / get-up, and the same keys played back for the return (lying down again, the frame-0 pose at the loop)
  if(sc.id==='bed1'||sc.id==='bed2'){ const s=lin(sc.id==='bed1'?TL.bedWarp1:TL.bedWarp2,t); const bp=BS.pose(s); const fc=BS.face(s);
    let face={roll:bp.roll||0,mood:fc.mood,brow:fc.brow,wide:fc.wide,open:fc.open,blink:fc.sleep?1:(s<1.2?(s<0.62?0.5:0):blinkAt(t)),fwd:bp.faceFwd};
    if(sc.id==='bed2') face={roll:bp.roll||0,mood:Math.min(0.2,m),brow:0,wide:0,open:0,blink:fc.sleep?1:sstep(17.9,18.4,t)*0.6+blinkAt(t)*0.4,fwd:bp.faceFwd};
    const bag=sc.id==='bed2'?1-sstep(16.25,16.45,t):0;
    return {J:bp.J,face,dress:{bag,collar:1,belt:1},phone:bp.phone,phoneLit:bp.phoneLight,bp,quilt:bp.quilt}; }
  // ---- door: by the wall calendar he tears 30 -> 1, grins at nobody, slings the bag
  if(sc.id==='door'){ const root=V(1.02,0,-1.95), yaw=YAW(V(-0.5,0,0.7));   /* 3/4 to camera: we see his face while he tears the page */ const P={...R.P0,p:0.04,tilt:-0.04};
    const padTop=V(0.42,1.5,-2.11), padLow=V(0.52,1.1,-1.95);
    const reach=sstep(3.6,3.82,t), pull=sstep(3.86,4.02,t), back=sstep(4.02,4.18,t);
    let tL=V(0.85,0.85,-1.75).lerp(padTop,reach).lerp(padLow,pull).lerp(V(0.86,0.86,-1.7),back);
    const sling=sstep(4.08,4.24,t)*(1-sstep(4.26,4.38,t)); const J0=R.skel(P,root,yaw); const tR=V(1.2,0.88,-1.75).lerp(J0.head.clone().add(V(0,0.16,0)),sling);
    P.tL=tL; P.wL=1; P.tR=tR; P.wR=1; P.pR=V(-0.2,-0.3,-0.9);
    const J=R.skel(P,root,yaw); const look=sstep(4.0,4.18,t)*0.75;
    return {J,face:{mood:m,blink:blinkAt(t),fwd:J.fwd,look,brow:0.3*sstep(4.0,4.1,t)},dress:{bag:sstep(4.2,4.34,t),collar:1,belt:1},phone:null}; }
  // ---- the street: morning (spring, head up, the rent buzz stops him) and night (a shuffle, the other way)
  if(sc.id==='streetAM'||sc.id==='streetPM'){ const am=sc.id==='streetAM'; const u=(t-sc.t0)/(sc.t1-sc.t0);
    const stop=am?sstep(4.86,4.98,t)*(1-sstep(5.36,5.5,t)):0; // he stops for the rent buzz
    const speed=am?1.25:0.75; const dist=(tt)=>{ let d=0; const N=40; for(let i=0;i<N;i++){ const ti=sc.t0+(tt-sc.t0)*(i+0.5)/N; const st=am?sstep(4.86,4.98,ti)*(1-sstep(5.36,5.5,ti)):0; d+=speed*(1-st)*(tt-sc.t0)/N; } return d; };
    const d=dist(t); const dir=am?V(1,0,0.18).normalize():V(-1,0,0.18).normalize(); const start=am?V(-1.1,0,-0.2):V(1.0,0,-0.2);
    const root=start.clone().addScaledVector(dir,d); const ph=d/(am?1.3:0.95)*2*Math.PI;
    let P={...R.P0,p:am?0.06:0.3,tilt:am?-0.06:0.32,eL:0.45,eR:0.45};
    P=R.gait(P,ph,(1-stop)*(am?1:0.7),am?0.34:0.22,am?0.62:0.4,am?0.22:0.06);
    let ph_=null;
    if(stop>0.01){ const J0=R.skel(P,root,YAW(dir)); const hold=J0.head.clone().addScaledVector(J0.fwd,0.26).add(V(0,-0.16,0)).add(dir.clone().cross(V(0,1,0)).multiplyScalar(-0.06)); P.tR=hold; P.wR=stop; P.pR=V(-0.3,-1,-0.5); ph_=hold; }
    const yaw=lerp(YAW(dir),YAW(V(am?0.35:-0.35,0,1)),0.55*stop);
    const J=R.skel(P,root,yaw); const face={mood:m,blink:blinkAt(t),fwd:J.fwd,look:0};
    return {J,face,dress:{bag:1,collar:1,belt:1},phone:ph_?{pos:J.hR.clone().add(V(0,0.04,0)),n:J.head.clone().sub(J.hR).normalize(),held:1}:null,phoneLit:stop}; }
  // ---- the desk: one chair, the whole month
  const root=V(0,0,-1.33), yaw=YAW(V(0,0,1)); const sitP={...R.P0,aL:1.5,aR:1.5,kL:1.55,kR:1.45,eL:1.0,eR:1.0,p:0.12,tilt:0.12};
  let P=postureFrom({...sitP},hope); P.p+=0.012*Math.sin(t*1.7);
  const J0=R.skel(P,root,yaw); const head=J0.head, fw=J0.fwd;
  const ds=dayState(t);
  // typing (right hand always on the keys, left hand when free)
  const ty=t*14, kR=V(0.14,0.815+0.012*Math.max(0,Math.sin(ty)),-1.04), kL=V(-0.04,0.815+0.012*Math.max(0,Math.sin(ty+2.1)),-1.04);
  const padTop=V(-0.4,1.06,-1.12), padOff=V(-0.3,0.98,-1.02);
  const phoneDesk=V(-0.26,0.795,-0.78), phoneFace=head.clone().addScaledVector(fw,0.3).add(V(-0.06,-0.3,0));
  let tL=kL.clone(), lift=0, faceUp=0, look=0;
  // morning tear of the pad (days 2..6 by hand; in the time-lapse the hand flicks every page)
  const tearU=ds.t0>5.6&&ds.t0<14.9?clamp((t-ds.t0+0.18)/0.42):1;
  if(tearU<1){ const a=sstep(0,0.4,tearU), b=sstep(0.4,0.75,tearU), c=sstep(0.75,1,tearU); tL=kL.clone().lerp(padTop,a).lerp(padOff,b).lerp(kL,c); const lean=Math.sin(Math.PI*tearU); P.ty=(P.ty||0)+0.35*lean; P.p+=0.12*lean; }   /* he leans and turns into the reach, so the arm stays bent */
  // the phone: buzz -> he looks -> he lifts it to his face -> puts it down
  const lifts=[[5.95,0.55],[6.7,0.45],[7.35,0.4],[7.95,0.35],[8.45,1.45],[13.5,0.85]];
  for(const [tb,len] of lifts){ const u=(t-tb)/len; if(u>-0.15&&u<1.15){ const up=sstep(-0.05,0.25,u), dn=sstep(0.8,1.1,u); lift=Math.max(lift,up*(1-dn)); look=Math.max(look,sstep(-0.15,0.05,u)*(1-sstep(0.9,1.1,u))); } }
  if(lift>0.01){ tL=tL.clone().lerp(phoneFace,lift); }
  // false hope (day 27): he grabs it fast, then lays it face down
  // the end of the month: the laptop closes, he stands into the night
  P.tL=tL; P.wL=1; P.pL=V(-0.35,-1,0.45); P.tR=kR; P.wR=1; P.pR=V(-0.35,-1,-0.45);
  if(t>8.75&&t<9.9){ P.p-=0.06*sstep(8.8,9.2,t); P.tilt+=0.1*sstep(8.8,9.3,t); }          // the stare
  if(t>9.9&&t<10.8){ look=0; P.hy=-0.45*sstep(9.95,10.3,t); }                               // he turns to the pad
  if(t>14.85){ const st=sstep(14.85,15.0,t); P.tL=kL.clone().lerp(V(-0.1,0.95,-0.85),st); P.tR=kR.clone().lerp(V(0.2,0.95,-0.85),st); }
  const J=R.skel(P,root,yaw);
  const phonePos=lift>0.01?J.hL.clone().add(V(0,0.03,0)):phoneDesk.clone().add(V(0.004*Math.sin(t*90)*buzzAt(t),0,0));
  const n=lift>0.01?head.clone().sub(phonePos).normalize():(t>13.9&&t<15?V(0,-1,0):V(0,1,0));
  const face={mood:m,blink:(t>8.7&&t<9.95)?0:blinkAt(t),fwd:J.fwd,look:0,brow:0,wide:t>8.75&&t<9.4?0.6:0};   /* the stare holds the eyes open */
  if(look>0){ face.fwd=phoneFace.clone().sub(head).normalize().lerp(J.fwd,0.3).normalize(); }
  return {J,face,dress:{bag:t>14.8?sstep(14.85,15.0,t):0,collar:1,belt:1},phone:{pos:phonePos,n,held:lift},phoneLit:Math.max(buzzAt(t),lift),ds}; }
// ---------------------------------------------------------------- lights per set and time
function lights(set,ox,t){ const k=ST.key; const L=(o,x,y,z)=>o.position.set(ox+x,y,z);
  if(set==='bed'){ L(k,-1.8,2.4,1.2); k.target.position.set(ox+0.2,0.6,-0.6); k.intensity=18; k.color.setHex(0xffb866);
    L(ST.lampA,-1.95,0.95,-1.3); ST.lampA.color.setHex(0xffa24a); ST.lampA.intensity=2.0; L(ST.lampB,1.7,1.7,-1.3); ST.lampB.color.setHex(0xffb870); ST.lampB.intensity=1.6;
    L(ST.fill,0.8,1.8,4.2); ST.fill.color.setHex(0x78a6ff); ST.fill.intensity=1.3; ST.hemi.color.setHex(0xffd9b0); ST.hemi.groundColor.setHex(0x3a2a22); ST.hemi.intensity=0.45; scene.background.setHex(0x1a1414); }
  else if(set==='street'){ const am=t<10; L(k,3,5,2); k.target.position.set(ox,1,-2); k.intensity=am?20:9; k.color.setHex(am?0xa8c4ff:0x8aa0e0);
    L(ST.lampA,1.4,2.8,-0.6); ST.lampA.color.setHex(0xffb868); ST.lampA.intensity=am?2.5:4.5; L(ST.lampB,-1.8,2.6,-1); ST.lampB.color.setHex(0xffa860); ST.lampB.intensity=am?1.5:3.2;
    L(ST.fill,0.4,1.7,3.6); ST.fill.color.setHex(0xcfe0ff); ST.fill.intensity=am?2.2:1.4; ST.hemi.color.setHex(am?0x9fb4dc:0x40507a); ST.hemi.groundColor.setHex(0x2a2a32); ST.hemi.intensity=am?0.9:0.45;
    sets.street.children[1].material.color.setHex(am?0x41557e:0x121a2c); scene.background.setHex(am?0x2a3554:0x0d1220); }
  else { // desk: the window is the clock. phase 0 = dawn at each tear, 0.5 = midday, 1 = night
    const ds=dayState(t); const ph=clamp((t-ds.t0)/Math.max(0.12,(nextTear(t)-ds.t0)));
    const dn=t<5.6?1:Math.max(0,Math.sin(Math.PI*Math.min(1,ph*1.15)))*(t>13.3?0.25:1)*(t>14.3?0:1);
    L(k,-1,3.2,1.8); k.target.position.set(ox,1,-1); k.intensity=6+10*dn; k.color.setHex(0xffe0b8);
    L(ST.lampA,0.62,1.12,-1.08); ST.lampA.color.setHex(0xffb86a); ST.lampA.intensity=1.2+2.2*(1-dn); L(ST.lampB,-0.1,1.8,-2.0); ST.lampB.color.setHex(0x9ec0ff); ST.lampB.intensity=0.6+2.0*dn;
    L(ST.fill,0.9,1.7,2.6); ST.fill.color.setHex(0x8fb0ff); ST.fill.intensity=1.2; ST.hemi.color.setHex(0xd8dcef); ST.hemi.groundColor.setHex(0x2a2a2e); ST.hemi.intensity=0.25+0.35*dn;
    sets.desk.userData.sky.color.setRGB(lerp(0.03,0.2,dn),lerp(0.04,0.27,dn),lerp(0.09,0.42,dn));   /* dark-warm: dusk-blue at best, never bright daylight */ scene.background.setHex(0x151820); }
  ST.rim.position.set(ox-3,4,-3); ST.rim.target.position.set(ox,1,0); }
const nextTear=t=>{ for(const [tt] of DAYS) if(tt>t+1e-6) return tt; return 99; };
// ---------------------------------------------------------------- cameras (set-local): [time, pos, look]
const CAMS={
  door:[[3.6,[2.55,1.5,1.25],[0.85,1.18,-1.9]],[4.4,[2.4,1.48,1.05],[0.9,1.18,-1.9]]],
  streetAM:[[4.4,[-0.7,1.4,4.4],[-0.6,1.0,-0.4]],[5.6,[0.2,1.4,4.2],[0.2,1.0,-0.4]]],
  streetPM:[[15.0,[1.2,1.4,4.4],[0.95,1.0,-0.4]],[15.8,[0.7,1.4,4.2],[0.4,1.0,-0.4]]],
  desk:[[5.6,[0.95,1.42,1.25],[-0.12,1.0,-1.1]],[8.3,[0.62,1.36,0.55],[-0.12,1.06,-1.15]],[8.75,[0.42,1.42,0.12],[-0.06,1.16,-1.3]],[9.85,[0.36,1.4,0.0],[-0.06,1.18,-1.3]],
    [10.3,[0.42,1.2,0.25],[-0.42,0.98,-1.05]],[10.8,[0.95,1.42,1.2],[-0.12,1.0,-1.1]],[13.3,[0.8,1.4,0.95],[-0.12,1.02,-1.1]],[13.5,[0.5,1.42,0.2],[-0.08,1.12,-1.25]],[14.35,[0.48,1.42,0.15],[-0.08,1.12,-1.25]],[14.45,[0.95,1.42,1.2],[-0.12,1.0,-1.1]],[15.0,[0.9,1.42,1.1],[-0.12,1.05,-1.1]]] };
function camAt(id,t){ const K=CAMS[id]; if(t<=K[0][0]) return {pos:V(...K[0][1]),look:V(...K[0][2])}; for(let i=1;i<K.length;i++) if(t<=K[i][0]){ const u=sm5((t-K[i-1][0])/(K[i][0]-K[i-1][0])); return {pos:V(...K[i-1][1]).lerp(V(...K[i][1]),u),look:V(...K[i-1][2]).lerp(V(...K[i][2]),u)}; } const L=K[K.length-1]; return {pos:V(...L[1]),look:V(...L[2])}; }
// ---------------------------------------------------------------- the blanket (from salary-loop-dark: a height field draped over his limbs)
const BL={nx:130,nw:84,x0:-0.56,x1:1.12}; const blGeo=new THREE.PlaneGeometry(1,1,BL.nx,BL.nw); const blMesh=new THREE.Mesh(blGeo,new THREE.MeshStandardMaterial({map:SETS.plaidTex(),roughness:0.95,side:THREE.DoubleSide})); blMesh.castShadow=true; blMesh.receiveShadow=true; blMesh.frustumCulled=false; sets.bed.add(blMesh); sets.bed.userData.quilt.visible=false;
{ const uv=blGeo.attributes.uv; for(let j=0;j<=BL.nw;j++) for(let i=0;i<=BL.nx;i++){ const k=j*(BL.nx+1)+i; uv.setXY(k,i/BL.nx*1.6,j/BL.nw*1.2); } }
function updateBlanket(J,qt){ const pos=blGeo.attributes.position; const segs=[]; if(J&&qt<0.98){ const add=(a,b,r)=>segs.push([a,b,r]); add(J.hip,J.neck,0.14); add(J.hipL,J.kL,0.085); add(J.hipR,J.kR,0.085); add(J.kL,J.fL,0.065); add(J.kR,J.fR,0.065); add(J.shL,J.elL,0.055); add(J.shR,J.elR,0.055); add(J.elL,J.hL,0.05); add(J.elR,J.hR,0.05); }
  const xa=lerp(BL.x0,0.5,qt), xb=BL.x1; const topY=0.545, zb=-1.8, zf=-0.6;
  for(let j=0;j<=BL.nw;j++){ const w=j/BL.nw; for(let i=0;i<=BL.nx;i++){ const x=lerp(xa,xb,i/BL.nx); let z,y; const sp=0.84;
      const zz=w<sp?lerp(zb,zf,w/sp):zf; let h=topY+0.004*Math.sin(x*23+zz*9); let wt=1-qt; let nd=1;
      if(segs.length){ for(const [a,b,r] of segs){ const dx=b.x-a.x, dz=b.z-a.z, L2=dx*dx+dz*dz+1e-6; let u=((x-a.x)*dx+(zz-a.z)*dz)/L2; u=clamp(u); const px=a.x+dx*u, pz=a.z+dz*u, py=a.y+(b.y-a.y)*u; const d=Math.hypot(x-px,zz-pz); const top=py+(r+0.008)*Math.exp(-Math.pow(d/(r*1.25),2)); if(top>h) h=top; nd=Math.min(nd,d-r); } if(x<-0.42) h=lerp(topY+0.02,h,clamp((x+0.56)/0.14)); }
      { const near=Math.exp(-Math.max(0,nd)/0.2); const amp=(0.004+0.013*near)*(1+2.0*Math.sin(Math.PI*clamp(qt))); h+=amp*(0.9*Math.sin(x*27+1.7*Math.sin(zz*5.3)+zz*2.1)+0.7*Math.sin(zz*19-x*13+Math.sin(x*7)*2)+0.5*Math.sin((x+zz)*43+Math.sin(zz*11)*1.5)); }
      h=lerp(topY,h,wt); h+=qt*0.15*(0.5+0.5*Math.sin(x*26+1))*Math.exp(-Math.pow((x-0.72)/0.3,2))*(0.6+0.4*Math.sin(zz*7));
      if(w<=sp){ z=zz; y=h; if(x>0.93) y-=Math.pow((x-0.93)*3.0,1.5); } else { const jj=(w-sp)/(1-sp); z=zf+0.06*Math.sin(jj*Math.PI/2)*(1-0.5*qt); y=h-(0.2+0.015*Math.sin(x*17+zz))*jj*(1-qt*0.6); if(x>0.93) y-=(x-0.93)*2.2; if(qt>0.6) y=Math.max(y,0.535); }
      const k=j*(BL.nx+1)+i; pos.setXYZ(k,x,y,z); } }
  pos.needsUpdate=true; blGeo.computeVertexNormals(); }
// ---------------------------------------------------------------- one frame
const shift=(J,ox)=>{ const o={}; for(const k in J) o[k]=(J[k]&&J[k].isVector3)?(k==='fwd'?J[k].clone():J[k].clone().add(V(ox,0,0))):J[k]; return o; };
function setT(t){ const sc=sceneAt(t); const set=SET_OF[sc.id]; const ox=sets[set].userData.ox; for(const k in sets) sets[k].visible=(k===set);
  lights(set,ox,t);
  const hp=heroPose(t,sc); hero.pose(shift(hp.J,ox),hp.face,hp.dress);
  phone.visible=!!hp.phone; phoneLight.intensity=0; phone.scale.setScalar(set==='street'?2.1:1.3);   /* readable in his hand on the wide street shots */
  if(hp.phone){ const p=hp.phone.pos.clone().add(V(ox,0,0)); phone.position.copy(p); const zA=hp.phone.n.clone().normalize(); const ref=Math.abs(zA.y)>0.9?V(0,0,-1):V(0,1,0); const xA=ref.clone().cross(zA).normalize(); const yA=zA.clone().cross(xA); phone.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(xA,yA,zA));
    const lit=clamp(hp.phoneLit||0); phone.userData.scr.material.color.setRGB(lerp(0.05,0.55,lit),lerp(0.06,0.6,lit),lerp(0.08,0.68,lit)); phoneLight.position.copy(p).addScaledVector(zA,0.3); phoneLight.intensity=0.05*lit; }
  // the tear-off pads
  const ds=dayState(t);
  if(set==='bed'){ const b=sets.bed; const qt=hp.quilt??1; blMesh.visible=true; updateBlanket(hp.bp?hp.bp.J:null,qt); b.userData.bag.visible=!(t>=4.2&&t<16.4); b.userData.bag.parent.children.forEach(()=>{});
    const home=sc.id==='bed2'?{n:30,left:1,tear:1,prev:null}:(t<3.9?{n:30,left:1,tear:1,prev:null}:{n:1,left:31,tear:clamp((t-3.9)/0.32),prev:30}); b.userData.pad.set(home.n,home.left,home.tear,home.prev); }
  if(set==='desk'){ const d=sets.desk; d.userData.pad.set(ds.n,ds.left,ds.tear,ds.prev);
    const lidA=t>14.6?lerp(-0.25,-1.5,sstep(14.6,14.85,t)):-0.25; d.userData.lid.rotation.x=-0.25+(lidA+0.25); d.userData.screen.material.color.setRGB(...(t>14.8?[0.05,0.05,0.06]:[0.74,0.83,0.93]));
    const day=ds.n; d.userData.tiffin.visible=day>=10&&day<=26; d.userData.cups.forEach((c,i)=>{ c.visible=day>=[9,15,22][i]; }); d.userData.piles.forEach((p,i)=>{ const h=0.02+0.22*clamp((day-1)/29)*[1,0.7][i]; p.scale.y=h/0.1; p.position.y=0.78+h/2; }); }
  // camera
  let pos,look; if(sc.id==='bed1'||sc.id==='bed2'){ pos=hp.bp.cam.pos.clone(); look=hp.bp.cam.look.clone(); } else { const c=camAt(sc.id,t); pos=c.pos; look=c.look; }
  if(window.DBG){ pos=V(...window.DBG.pos); look=V(...window.DBG.look); }
  ST.cam.position.set(ox+pos.x,pos.y,pos.z); ST.cam.lookAt(ox+look.x,look.y,look.z);
  ST.grade.uniforms.uFlash.value=0; ST.grade.uniforms.uT.value=t; }
window.renderAt=(t,K=3)=>{ const fast=(t>10.8&&t<13.4)||(t>4.4&&t<5.6)||(t>15&&t<15.8); return ST.renderAt(setT,t,fast?Math.max(K,4):K,{t0:0,t1:DUR,shutter:fast?1/40:1/60}); };
window.events={...TL}; window.ready=true;
