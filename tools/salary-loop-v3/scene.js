// The Salary Loop V4 (19.3 s). The frozen plan is STORY.md; every time comes from timeline.json.
// V3's story in V2's places: his bedroom (wake, the one calendar tear, the end), the rent hallway, the bank counter, the veg stall, the petrol pump,
// the bills desk, the thali place, then his office desk where a wall calendar crosses itself off through the month.
// The phone faces him at the start and the end; every expense is a person or a thing he hands cash to. renderAt(t) is pure. Units are metres.
// Each set lives at x = 16 * index; the camera is always in front (+z), wide (he is small in a big dark room) except at the two emotional beats.
import * as THREE from 'three';
import {createWarmStage,V,clamp,sstep,lerp} from './stage.js';
import * as SLD from './sld.js';
import {createFigure,HERO} from './figure.js';
import * as SETS from './sets.js';
import {createBedSeq} from './bedseq.js';
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960;
const TL=await (await fetch('timeline.json')).json(); const DUR=TL.duration, DEB=TL.debits;
const ST=createWarmStage({W,H}); const R=SLD.createRig(ST.scene); const scene=ST.scene; const sm5=SLD.sm5;
const BS=createBedSeq(R);
const lin=(K,t)=>{ if(t<=K[0][0]) return K[0][1]; for(let i=1;i<K.length;i++) if(t<=K[i][0]){ const u=(t-K[i-1][0])/(K[i][0]-K[i-1][0]); return lerp(K[i-1][1],K[i][1],u); } return K[K.length-1][1]; };
const smooth=(K,t)=>SLD.keys(K,t);
const YAW=d=>SLD.yawOf(d);
// ---------------------------------------------------------------- sets
const SP=16; const order=['bed','rent','bank','market','pump','bills','food','desk'];
const builders={bed:SETS.buildBedroom,rent:SETS.buildRent,bank:SETS.buildBank,market:SETS.buildMarket,pump:SETS.buildPump,bills:SETS.buildBills,food:SETS.buildRestaurant,desk:SETS.buildDesk};
const sets={}; order.forEach((k,i)=>{ const g=builders[k](); g.position.x=i*SP; g.userData.ox=i*SP; g.visible=false; scene.add(g); sets[k]=g; });
const SET_OF={bed1:'bed',door:'bed',bed2:'bed',rent:'rent',bank:'bank',market:'market',pump:'pump',bills:'bills',food:'food',desk:'desk'};
const sceneAt=t=>TL.scenes.find(s=>t>=s.t0&&t<s.t1)||TL.scenes[TL.scenes.length-1];
// ---------------------------------------------------------------- the hero, the phone, the people he pays, the cash
const hero=createFigure(scene,HERO);
const phone=new THREE.Group(); { SETS.B(phone,0.072,0.15,0.01,SETS.M(0x0d0e12,{r:0.3,m:0.4}),0,0,0,{round:0.01}); const scr=new THREE.Mesh(new THREE.PlaneGeometry(0.064,0.136),new THREE.MeshBasicMaterial({color:0xd8e6f6})); scr.position.z=0.0055; phone.add(scr); phone.userData.scr=scr; }
phone.scale.setScalar(1.3); scene.add(phone); const phoneLight=new THREE.PointLight(0xcfe0ff,0,1.6,2); scene.add(phoneLight);
/* the six payments: where he stands, which way he faces, where his hand and theirs meet. HT = his hand, CP = their hand (set-local). */
const EXP={
  rent:{i:0,root:V(-0.6,0,0.05),dir:V(1,0,0.2),HT:V(-0.11,1.08,0.15),CPH:V(0.3,1.08,0.17)},
  bank:{i:1,root:V(-0.6,0,-0.22),dir:V(1,0,0.12),HT:V(-0.11,1.12,-0.12),CPH:V(0.3,1.12,-0.85)},
  market:{i:2,root:V(-0.6,0,-0.35),dir:V(1,0,0.2),HT:V(-0.11,1.08,-0.25),CPH:V(0.3,1.08,-0.25)},
  pump:{i:3,root:V(-0.85,0,0.1),dir:V(1,0,0.2),HT:V(-0.36,1.08,0.2),CPH:V(0.07,1.08,0.22)},
  bills:{i:4,HT:V(0.55,0.95,-0.9),CPH:V(1.0,0.98,-0.75)},
  food:{i:5,HT:V(-0.35,1.0,-0.55),CPH:V(-0.74,1.0,-0.5)} };
const extras=[]; function extra(setId,root,toward,arm,pose,mood,cols={}){ const f=createFigure(scene,{skin:cols.skin??0xe2c39a,shirt:cols.shirt??0x6a7a8a,pants:cols.pants??0x35343a,tie:cols.tie??0x7a3f3a,headR:0.165}); const e={f,setId,root,toward,arm,pose,mood,seed:extras.length*1.7,hand:EXP[setId]?EXP[setId].CPH:null,i:EXP[setId]?EXP[setId].i:-1}; extras.push(e); return e; }
const idle=(t,s)=>0.012*Math.sin(t*1.9+s);
extra('rent',V(0.75,0,0.05),V(-0.6,0,0.05),'L',{p:0.05},0.18,{skin:0xd9b48a,shirt:0x8a7a52,pants:0x4a3f33});          // the landlord, hand out
extra('bank',V(0.75,0,-1.45),V(-0.6,0,-0.22),'L',{p:0.08,tilt:0.1,aL:1.5,aR:1.5,kL:1.5,kR:1.5,sit:1},0.55,{skin:0xd9b48a,shirt:0x7a98b8,pants:0x2b3340,tie:0x7a3f3a});   // the clerk, seated behind the counter
extra('market',V(0.7,0,-0.3),V(-0.6,0,-0.35),'L',{p:0.1},0.8,{skin:0xb98a62,shirt:0xe8dcb0,pants:0x4a4038});              // the vendor, come round to the front
extra('pump',V(0.45,0,0.2),V(-0.85,0,0.1),'L',{p:0.05},0.5,{skin:0xd9b48a,shirt:0xe8e1d4,pants:0x3a3a40});                 // the attendant
extra('food',V(-1.0,0,-0.5),V(0.2,0,-0.96),'R',{p:0.06},0.7,{skin:0xb98a62,shirt:0xe8dcb0,pants:0x3a3a40});               // the waiter
extra('food',V(-1.9,0,-1.0),V(0.2,0,-0.5),null,{aL:1.5,aR:1.5,kL:1.5,kR:1.5,sit:1,p:0.1},0.7,{skin:0xd9b48a,shirt:0xa86a4a});   // diners behind
extra('food',V(2.0,0,-1.2),V(0.2,0,-0.5),null,{aL:1.5,aR:1.5,kL:1.5,kR:1.5,sit:1,p:0.15},0.6,{skin:0xb98a62,shirt:0x4a7a6a});
const notes=[]; for(let i=0;i<16;i++){ const n=SETS.B(scene,0.12,0.005,0.06,SETS.M(0xcfe3b5,{r:0.8,e:0x9fd08a,ei:0.5}),0,-9,0); notes.push(n); }
const tmp=new THREE.Vector3();
// ---------------------------------------------------------------- the month: wake-up pad (door only), the wall calendar, mood, hope
const DAYS=TL.days;
function dayState(t){ let i=0; for(let k=0;k<DAYS.length;k++) if(t>=DAYS[k][0]) i=k; const n=DAYS[i][1]; const prev=i>0?DAYS[i-1][1]:null;
  const dur=i>0?0.32:0.3; const tear=i>0?clamp((t-DAYS[i][0])/dur):1;
  return {n,prev,tear,left:n===30&&t<3.9?1:31-n,t0:DAYS[i][0]}; }
const crossedAt=t=>{ let c=0; for(const [tc,n] of TL.crosses) if(t>=tc) c=n; return c; };
const calCache=new Map(); const calTex=n=>{ if(!calCache.has(n)) calCache.set(n,SETS.calendarTex(n<30?n+1:0,n,'THE MONTH')); return calCache.get(n); };
const buzzAt=t=>{ let b=0; for(const bt of TL.buzz){ const u=t-bt; if(u>=-0.02&&u<0.45) b=Math.max(b,1-u/0.45); } return b; };
const moodAt=t=>smooth(TL.mood,t), hopeAt=t=>smooth(TL.hope,t);
const blinkAt=t=>{ const ph=(t*0.31+0.17)%1; return ph<0.03?1:(ph<0.05?0.5:0); };
function postureFrom(P,hope){ const sag=1-hope; P.p=(P.p||0)+0.3*sag; P.tilt=(P.tilt||0)+0.25*sag; return P; }
const handEnv=(tc,t)=>sstep(tc-0.5,tc-0.2,t)*(1-sstep(tc+0.35,tc+0.62,t));
// ---------------------------------------------------------------- hero poses (set-local; the set origin is added at the end)
function heroPose(t,sc){
  const m=moodAt(t), hope=hopeAt(t);
  // ---- the bed: the forward wake / get-up, and the same keys played back for the return (collapsing into bed, the frame-0 pose at the loop)
  if(sc.id==='bed1'||sc.id==='bed2'){ const s=lin(sc.id==='bed1'?TL.bedWarp1:TL.bedWarp2,t); const bp=BS.pose(s); const fc=BS.face(s);
    let face={roll:bp.roll||0,mood:fc.mood,brow:fc.brow,wide:fc.wide,open:fc.open,blink:fc.sleep?1:(s<1.2?(s<0.62?0.5:0):blinkAt(t)),fwd:bp.faceFwd};
    if(sc.id==='bed2') face={roll:bp.roll||0,mood:Math.min(0.2,m),brow:0,wide:0,open:0,blink:fc.sleep?1:sstep(17.9,18.4,t)*0.6+blinkAt(t)*0.4,fwd:bp.faceFwd};
    return {J:bp.J,face,dress:{bag:0,collar:1,belt:1},phone:bp.phone,phoneLit:bp.phoneLight,bp,quilt:bp.quilt}; }
  // ---- door: by the wall calendar he tears 30 -> 1, grins at nobody, slings the bag
  if(sc.id==='door'){ const root=V(1.02,0,-1.95), yaw=YAW(V(-0.5,0,0.7));   /* 3/4 to camera: we see his face while he tears the page */ const P={...R.P0,p:0.04,tilt:-0.04};
    const padTop=V(0.45,1.62,-2.1), padLow=V(0.5,1.15,-1.95);
    const reach=sstep(3.6,3.82,t), pull=sstep(3.86,4.02,t), back=sstep(4.02,4.18,t);
    let tL=V(0.85,0.85,-1.75).lerp(padTop,reach).lerp(padLow,pull).lerp(V(0.86,0.86,-1.7),back);
    const sling=sstep(4.08,4.24,t)*(1-sstep(4.26,4.38,t)); const J0=R.skel(P,root,yaw); const tR=V(1.2,0.88,-1.75).lerp(J0.head.clone().add(V(0,0.16,0)),sling);
    P.tL=tL; P.wL=1; P.tR=tR; P.wR=1; P.pR=V(-0.2,-0.3,-0.9);
    const J=R.skel(P,root,yaw); const look=sstep(4.0,4.18,t)*0.75;
    return {J,face:{mood:m,blink:blinkAt(t),fwd:J.fwd,look,brow:0.3*sstep(4.0,4.1,t)},dress:{bag:sstep(4.2,4.34,t),collar:1,belt:1},phone:null}; }
  const E=EXP[sc.id]; const dress={bag:1,collar:1,belt:1};
  // ---- the four standing payments: he faces the person, the paying hand comes out in front of him (never behind)
  if(sc.id==='rent'||sc.id==='bank'||sc.id==='market'||sc.id==='pump'){ const tc=DEB[E.i][0]; const env=handEnv(tc,t); const yaw=YAW(E.dir);
    let P={...R.P0,p:0.06+0.3*(1-m),tilt:0.1+0.12*(1-m)}; P.p+=0.01*Math.sin(t*1.9);
    P.tR=E.HT; P.wR=env; const J=R.skel(P,E.root,yaw);
    return {J,face:{mood:m,blink:blinkAt(t),fwd:J.fwd,look:0},dress,phone:null,hand:J.hR}; }
  // ---- the bills desk and the thali table: he sits behind them facing the camera
  if(sc.id==='bills'||sc.id==='food'){ const tc=DEB[E.i][0]; const env=handEnv(tc,t); const bills=sc.id==='bills';
    const P={...R.P0,aL:1.5,aR:1.5,kL:1.55,kR:1.45,eL:1.0,eR:1.0,p:0.16+0.3*(1-m),tilt:0.12+0.2*(1-m)}; const root=bills?V(0,0,-1.46):V(0.2,0,-0.96);
    P.tL=bills?V(-0.1,0.9,-0.95):V(0.0,0.88,-0.5); P.wL=1; P.pL=V(-0.35,-1,0.45);
    const rest=bills?V(0.25,0.9,-0.95):V(0.3,0.9,-0.55); P.tR=rest.clone().lerp(E.HT,env); P.wR=1; P.pR=V(-0.35,-1,-0.45);
    const J=R.skel(P,root,YAW(V(0,0,1)));
    return {J,face:{mood:m,blink:(t>8.7&&t<9.2)?0:blinkAt(t),fwd:J.fwd,look:0,wide:sc.id==='food'&&t>8.75?0.6:0},dress,phone:null,hand:J.hR}; }
  // ---- the desk: one chair, the whole month. camera-facing, laptop in front of him, the wall calendar to his right
  const root=V(0,0,-1.33), yaw=YAW(V(0,0,1)); const sitP={...R.P0,aL:1.5,aR:1.5,kL:1.55,kR:1.45,eL:1.0,eR:1.0,p:0.12,tilt:0.12};
  let P=postureFrom({...sitP},hope); P.p+=0.012*Math.sin(t*1.7);
  const J0=R.skel(P,root,yaw); const head=J0.head, fw=J0.fwd;
  const ty=t*14, kR=V(0.14,0.815+0.012*Math.max(0,Math.sin(ty)),-1.04), kL=V(-0.04,0.815+0.012*Math.max(0,Math.sin(ty+2.1)),-1.04);
  const phoneDesk=V(-0.26,0.795,-0.78), phoneFace=head.clone().addScaledVector(fw,0.3).add(V(-0.06,-0.3,0));
  let tL=kL.clone(), tRr=kR.clone(), lift=0, look=0;
  const fh=TL.falseHope[0]+0.1;   /* day 27: the phone buzzes; he grabs it, lifts it, a flicker of hope, then lays it down */
  { const u=(t-fh)/0.85; if(u>-0.15&&u<1.15){ const up=sstep(-0.05,0.25,u), dn=sstep(0.8,1.1,u); lift=up*(1-dn); look=sstep(-0.15,0.05,u)*(1-sstep(0.9,1.1,u)); } }
  if(lift>0.01) tL=tL.clone().lerp(phoneFace,lift);
  if(t>9.2&&t<9.9){ P.p-=0.06*sstep(9.2,9.5,t); P.tilt+=0.1*sstep(9.2,9.6,t); }          // the stare
  if(t>9.9&&t<10.8){ look=0; P.hy=-0.45*sstep(9.95,10.3,t); }                                // he turns to the calendar
  if(t>=10.8&&t<10.95) P.hy=-0.45*(1-sstep(10.8,10.95,t));
  const sl=sstep(15.75,16.7,t);   /* the end: the last X lands on 30, he shuts the laptop, hands drop to his lap, his head sags to his chest (nothing passes through the laptop) */
  const shut=sstep(15.3,15.7,t); tL=tL.clone().lerp(V(-0.05,0.9,-0.98),shut*(1-sl)); tRr=tRr.clone().lerp(V(0.08,0.9,-0.98),shut*(1-sl));
  P.p-=0.12*sl; P.tilt+=0.22*sl; tL=tL.clone().lerp(V(-0.3,0.83,-0.98),sl); tRr=tRr.clone().lerp(V(0.45,0.83,-0.98),sl);   /* hands rest on the desk either side of the shut laptop: no arm goes through it */
  P.tL=tL; P.wL=1; P.pL=V(-0.35,-1,0.45); P.tR=tRr; P.wR=1; P.pR=V(-0.35,-1,-0.45);
  const J=R.skel(P,root,yaw);
  const phonePos=lift>0.01?J.hL.clone().add(V(0,0.03,0)):phoneDesk.clone().add(V(0.004*Math.sin(t*90)*buzzAt(t),0,0));
  const n=lift>0.01?head.clone().sub(phonePos).normalize():V(0,1,0);
  const face={mood:m,blink:(t>9.1&&t<9.95)?0:(sl>0.5?1:blinkAt(t)),fwd:J.fwd,look:0,brow:0,wide:t>9.2&&t<9.8?0.6:0};   /* the stare holds the eyes open */
  if(look>0){ face.fwd=phoneFace.clone().sub(head).normalize().lerp(J.fwd,0.3).normalize(); }
  return {J,face,dress,phone:{pos:phonePos,n,held:lift},phoneLit:Math.max(buzzAt(t),lift)}; }
// ---------------------------------------------------------------- lights per set and time
const LIGHTS={ rent:{key:[-2.5,3,2.5,-0.2,1,0,20],a:[1.6,1.6,-1.4,0xffd890,1.6],b:[-0.5,2.4,-1,0xffa860,2],fill:[0.8,1.8,4.2,0x78a6ff,0.8],hemi:[0xffd9b0,0x2a2a2e,0.45],bg:0x1a1614},
  bank:{key:[-1,3.2,2.5,0.2,0.8,-0.5,24],a:[0.3,2.6,-0.5,0xfff0c8,3],b:[-1.5,2.4,0.5,0xffe0a8,1.5],fill:[0.8,1.8,4.2,0x88b0ff,0.9],hemi:[0xe8e0d0,0x2a2a2e,0.5],bg:0x161a1c},
  market:{key:[-1.5,2.8,2.5,0.2,0.9,-0.8,22],a:[0.2,2.2,-0.6,0xffb860,3.4],b:[-1.3,2.2,-0.5,0xffb860,2.6],fill:[0.8,1.8,4.2,0x8070c0,0.8],hemi:[0xffc890,0x2a2230,0.45],bg:0x120d16},
  bills:{key:[-1.8,2.6,2,0,0.9,-0.6,22],a:[-0.95,1.5,-1.2,0xffb868,3],b:[0.9,1.9,-1.2,0xfff0c8,1.6],fill:[0.8,1.8,4.2,0x78a6ff,0.9],hemi:[0xffd9b0,0x3a2a22,0.5],bg:0x1a1210},
  food:{key:[-1.5,2.8,2.2,0.1,0.9,-0.5,22],a:[-0.2,2.2,-1.4,0xffb860,3.2],b:[1.2,2.2,-1.4,0xffb860,2.6],fill:[0.8,1.8,4.2,0x78a6ff,0.7],hemi:[0xffc890,0x3a2418,0.5],bg:0x1c1210},
  pump:{key:[0,3.0,1.8,0.2,0.8,-0.8,34],a:[-1.8,2.9,-1.3,0xfff4dc,3.2],b:[1.8,2.9,-1.3,0xfff4dc,3.2],fill:[0.8,1.8,4.2,0x6a90e8,0.9],hemi:[0xaab8e0,0x201a24,0.4],bg:0x0d1018} };
/* the V2 dark-warm overrides: charcoal-navy rooms, one warm lamp, never black */
function lightsV2(id,ox){ const L=LIGHTS[id]; const k=L.key; ST.key.position.set(ox+k[0],k[1],k[2]); ST.key.target.position.set(ox+k[3],k[4],k[5]); ST.key.intensity=k[6]*0.38; ST.key.angle=1.15; ST.key.color.setHex(0xffb470);
  ST.lampA.position.set(ox+L.a[0],L.a[1],L.a[2]); ST.lampA.color.setHex(0xffae62); ST.lampA.intensity=L.a[4]*0.95; ST.lampB.position.set(ox+L.b[0],L.b[1],L.b[2]); ST.lampB.color.setHex(0xffb878); ST.lampB.intensity=L.b[4]*0.6;
  ST.fill.position.set(ox+L.fill[0],L.fill[1],L.fill[2]); ST.fill.color.setHex(0x5873b0); ST.fill.intensity=L.fill[4]*1.6*0.45; ST.hemi.color.setHex(0x3a4c78); ST.hemi.groundColor.setHex(0x241c16); ST.hemi.intensity=0.28; scene.background.setHex(0x161b25); }
function lights(set,ox,t){ const k=ST.key; const L=(o,x,y,z)=>o.position.set(ox+x,y,z);
  if(LIGHTS[set]) lightsV2(set,ox);
  else if(set==='bed'){ L(k,-1.8,2.4,1.2); const dr=t>=3.5&&t<4.5; k.target.position.set(ox+(dr?0.9:0.2),dr?1.0:0.6,dr?-1.9:-0.6); k.intensity=dr?30:11; k.color.setHex(0xffb866);
    L(ST.lampA,-1.95,0.95,-1.3); ST.lampA.color.setHex(0xffa24a); ST.lampA.intensity=2.4; L(ST.lampB,1.7,1.7,-1.3); ST.lampB.color.setHex(0xffb870); ST.lampB.intensity=0.9;
    L(ST.fill,0.8,1.8,4.2); ST.fill.color.setHex(0x78a6ff); ST.fill.intensity=1.3; ST.hemi.color.setHex(0xffd9b0); ST.hemi.groundColor.setHex(0x3a2a22); ST.hemi.intensity=(t>=3.5&&t<4.5)?0.6:0.3; scene.background.setHex(0x14110f); }
  else { // desk: the window is the clock. dn 0 = night, 1 = a grey day, one cycle per five crossed days
    const tl=t-10.8; let dn=0.25; if(tl>=0&&tl<2.5) dn=Math.pow(Math.sin(Math.PI*((tl/0.625)%1)),1.2); else if(t>=13.3&&t<14.4) dn=0.25; else if(t>=14.4) dn=0.25*(1-sstep(14.4,15.6,t));
    L(k,-1,3.2,1.8); k.target.position.set(ox,1,-1); k.intensity=4+5*dn; k.color.setHex(0xffe0b8);
    L(ST.lampA,0.62,1.12,-1.08); ST.lampA.color.setHex(0xffb86a); ST.lampA.intensity=1.2+2.2*(1-dn); L(ST.lampB,-0.1,1.8,-2.0); ST.lampB.color.setHex(0x9ec0ff); ST.lampB.intensity=0.6+2.0*dn;
    L(ST.fill,0.9,1.7,2.6); ST.fill.color.setHex(0x8fb0ff); ST.fill.intensity=1.2; ST.hemi.color.setHex(0xd8dcef); ST.hemi.groundColor.setHex(0x2a2a2e); ST.hemi.intensity=0.2+0.2*dn;
    sets.desk.userData.sky.color.setRGB(lerp(0.02,0.07,dn),lerp(0.03,0.1,dn),lerp(0.07,0.2,dn));   /* dark-warm: dusk-blue at best, never bright daylight */ scene.background.setHex(0x0e1118); }
  ST.rim.position.set(ox-3,4,-3); ST.rim.target.position.set(ox,1,0); }
// ---------------------------------------------------------------- cameras (set-local): [time, pos, look]
const CAMS={
  door:[[3.6,[2.55,1.5,1.25],[0.85,1.18,-1.9]],[4.4,[2.4,1.48,1.05],[0.9,1.18,-1.9]]],
  rent:[[4.4,[-0.05,1.45,4.0],[-0.1,1.15,0.1]],[5.2,[-0.1,1.45,3.6],[-0.1,1.15,0.1]]],
  bank:[[5.2,[-0.1,1.5,4.2],[-0.1,1.2,-0.5]],[6.0,[-0.1,1.45,3.8],[-0.1,1.2,-0.5]]],
  market:[[6.0,[-0.05,1.45,4.2],[-0.1,1.15,-0.4]],[6.8,[-0.05,1.45,3.8],[-0.1,1.15,-0.4]]],
  pump:[[6.8,[0.0,1.45,4.2],[-0.2,1.1,0.0]],[7.6,[0.0,1.45,3.8],[-0.2,1.1,0.0]]],
  bills:[[7.6,[0.05,1.4,3.6],[0.0,1.1,-1.0]],[8.4,[0.05,1.35,3.2],[0.0,1.1,-1.0]]],
  food:[[8.4,[0.1,1.35,3.6],[0.1,1.0,-0.7]],[9.2,[0.1,1.3,3.2],[0.1,1.0,-0.7]]],
  desk:[[9.2,[0.7,1.42,1.0],[-0.06,1.16,-1.3]],[9.9,[0.66,1.4,0.95],[-0.06,1.18,-1.3]],[10.5,[0.4,1.45,1.6],[-0.45,1.3,-1.3]],[13.3,[0.4,1.45,1.6],[-0.45,1.3,-1.3]],[13.5,[0.6,1.42,0.7],[-0.08,1.12,-1.25]],[14.35,[0.58,1.42,0.65],[-0.08,1.12,-1.25]],[14.7,[0.4,1.45,1.6],[-0.45,1.3,-1.3]],[17.0,[0.45,1.4,1.3],[-0.7,1.25,-1.3]]] };
function camAt(id,t){ const K=CAMS[id]; if(t<=K[0][0]) return {pos:V(...K[0][1]),look:V(...K[0][2])}; for(let i=1;i<K.length;i++) if(t<=K[i][0]){ const u=sm5((t-K[i-1][0])/(K[i][0]-K[i-1][0])); return {pos:V(...K[i-1][1]).lerp(V(...K[i][1]),u),look:V(...K[i-1][2]).lerp(V(...K[i][2]),u)}; } const L=K[K.length-1]; return {pos:V(...L[1]),look:V(...L[2])}; }
// ---------------------------------------------------------------- the money: cash notes fly from his hand to theirs on the beat of every debit
function payNotes(t,sc,ox){ let used=0; const E=EXP[sc.id];
  if(E){ const tc=DEB[E.i][0]; const u=(t-tc)/0.5; if(u>0&&u<1) for(let k=0;k<4;k++){ const n=notes[used++]; const uu=clamp(u-k*0.07); if(uu<=0||uu>=1){ n.position.set(0,-9,0); continue; } tmp.copy(E.HT).lerp(E.CPH,uu*uu*(3-2*uu)); tmp.y+=0.25*Math.sin(Math.PI*uu); n.position.set(ox+tmp.x,tmp.y,tmp.z); n.rotation.set(uu*6,uu*5,0); } }
  for(let k=used;k<notes.length;k++) notes[k].position.set(0,-9,0); }
// ---------------------------------------------------------------- the blanket (from salary-loop-dark: a height field draped over his limbs)
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
  extras.forEach(e=>{ const on=e.setId===set; e.f.setVisible(on); if(!on) return; const sit=e.pose.sit; const P={...R.P0,...e.pose}; delete P.sit; P.p=(P.p||0)+idle(t,e.seed);
    const dir=e.toward.clone().sub(e.root); dir.y=0; dir.normalize(); dir.z+=0.3; const yaw=YAW(dir);   /* they face him, turned a little to the camera */
    if(e.hand&&e.arm){ const env=handEnv(DEB[e.i][0],t); const hnd=e.hand.clone().add(V(ox,0,0)); P['t'+e.arm]=hnd.clone().sub(V(ox,0,0)); P['w'+e.arm]=env; }
    const J=R.skel(P,e.root,yaw); J.fwd=J.fwd||V(1,0,0); const sj=shift(J,ox);
    e.f.pose(sj,{mood:e.mood,blink:blinkAt(t+e.seed),fwd:J.fwd},{tie:e.setId==='bank'?1:0,collar:1,belt:1}); });
  phone.visible=!!hp.phone; phoneLight.intensity=0; phone.scale.setScalar(1.3);
  if(hp.phone){ const bp=hp.phone.pos?hp.phone:hp.phone; const p=(hp.phone.pos).clone().add(V(ox,0,0)); phone.position.copy(p); const zA=hp.phone.n.clone().normalize(); const ref=Math.abs(zA.y)>0.9?V(0,0,-1):V(0,1,0); const xA=ref.clone().cross(zA).normalize(); const yA=zA.clone().cross(xA); phone.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(xA,yA,zA));
    const lit=clamp(hp.phoneLit||0); phone.userData.scr.material.color.setRGB(lerp(0.05,0.55,lit),lerp(0.06,0.6,lit),lerp(0.08,0.68,lit)); phoneLight.position.copy(p).addScaledVector(zA,0.3); phoneLight.intensity=0.05*lit; }
  payNotes(t,sc,ox);
  if(set==='bed'){ const b=sets.bed; const qt=hp.quilt??1; updateBlanket(hp.bp?hp.bp.J:null,qt); b.userData.bag.visible=!(t>=4.2&&t<17.0);
    const ds=dayState(t); const home=sc.id==='bed2'?{n:30,left:1,tear:1,prev:null}:(t<3.9?{n:30,left:1,tear:1,prev:null}:{n:1,left:31,tear:clamp((t-3.9)/0.32),prev:30}); b.userData.pad.set(home.n,home.left,home.tear,home.prev); }
  if(set==='desk'){ const d=sets.desk; const cr=crossedAt(t); const tex=calTex(cr); if(d.userData.cal.material.map!==tex){ d.userData.cal.material.map=tex; d.userData.cal.material.emissiveMap=tex; }
    const lidA=lerp(-0.25,-1.5,sstep(15.3,15.65,t)); d.userData.lid.rotation.x=lidA; d.userData.screen.material.color.setRGB(...(t>15.5?[0.05,0.06,0.08]:[0.74,0.83,0.93]));
    const day=cr; d.userData.tiffin.visible=day>=10&&day<=26; d.userData.cups.forEach((c,i)=>{ c.visible=day>=[9,15,22][i]; }); d.userData.piles.forEach((p,i)=>{ const h=0.02+0.22*clamp((day-1)/29)*[1,0.7][i]; p.scale.y=h/0.1; p.position.y=0.78+h/2; }); }
  // camera
  let pos,look; if(sc.id==='bed1'||sc.id==='bed2'){ pos=hp.bp.cam.pos.clone(); look=hp.bp.cam.look.clone(); } else { const c=camAt(sc.id,t); pos=c.pos; look=c.look; }
  // WIDE like the approved V2 (he is small in a big, dark room); only the two emotional beats (the stare at 0, the false hope) push in
  { const WIDE=q.has('wide')?+q.get('wide'):1; const base=({bed:3.1,bills:1.9,food:1.9,desk:2.1})[set]*WIDE||2.5*WIDE; const c=Math.max(sstep(8.5,8.8,t)*(1-sstep(9.85,10.35,t)),sstep(13.4,13.6,t)*(1-sstep(14.3,14.5,t))); const k=lerp(base,Math.min(1.9,base),c); pos=look.clone().add(pos.clone().sub(look).multiplyScalar(k)); if(set==='bed') pos.y=Math.max(pos.y,1.2+0.35*k*0.3); }
  if(window.DBG){ pos=V(...window.DBG.pos); look=V(...window.DBG.look); }
  ST.cam.position.set(ox+pos.x,pos.y,pos.z); ST.cam.lookAt(ox+look.x,look.y,look.z);
  ST.grade.uniforms.uFlash.value=0; ST.grade.uniforms.uT.value=t; }
window.renderAt=(t,K=3)=>{ const fast=(t>10.8&&t<13.4)||(t>14.4&&t<15.5); return ST.renderAt(setT,t,fast?Math.max(K,4):K,{t0:0,t1:DUR,shutter:fast?1/40:1/60}); };
window.events={...TL}; window.ready=true;
