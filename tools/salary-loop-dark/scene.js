// The Salary Loop (warm). A lived-in miniature film: his bedroom (hook, reality, the end), the rent door, the bank, the market, the bills desk,
// a restaurant, the petrol pump, his street at sunrise, his office. One stickman with a face (mood 0..1 = hap), office clothes and a side bag.
// renderAt(t) is pure. Units are metres. Each set lives at x = 16 * index; the camera is always in front (+z).
import * as THREE from 'three';
import {createWarmStage,V,clamp,sstep,lerp} from './stage.js';
import * as SLD from './sld.js';
import {createFigure} from './figure.js';
import * as SETS from './sets.js';
import {createBedSeq} from './bedseq.js';
const {M,B,C,S: SPH,P: PLN}=SETS;
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960;
const TL=await (await fetch('timeline.json')).json(); const DUR=TL.duration, ITEMS=TL.items;
const ST=createWarmStage({W,H}); const R=SLD.createRig(ST.scene); const scene=ST.scene; const sm5=SLD.sm5, keys=SLD.keys;
const SP=16; const BS=createBedSeq(R);
// ---------------------------------------------------------------- sets
const sets={}; const order=['bed','rent','bank','market','bills','food','pump','street','office'];
const builders={bed:SETS.buildBedroom,rent:SETS.buildRent,bank:SETS.buildBank,market:SETS.buildMarket,bills:SETS.buildBills,food:SETS.buildRestaurant,pump:SETS.buildPump,street:SETS.buildStreet,office:SETS.buildOffice};
order.forEach((k,i)=>{ const g=builders[k](); g.position.x=i*SP; g.visible=false; scene.add(g); sets[k]=g; g.userData.ox=i*SP; });
{ const o=sets.office; o.userData.piles=[[-0.35,-1.05],[1.12,-0.98],[0.55,-1.12]].map(([x,z])=>B(o,0.24,0.1,0.17,M(0xf1ece0,{r:0.9}),x,0.86,z,{ry:0.2})); o.userData.cups=[[1.2,-0.85],[0.05,-1.0],[-0.1,-0.8]].map(([x,z])=>{ const c=new THREE.Group(); C(c,0.05,0.042,0.09,M(0xf2ede4,{r:0.4}),0,0,0); c.position.set(x,0.865,z); c.visible=false; o.add(c); return c; }); }
const SCENES=TL.scenes.map(s=>({...s,set:{bed1:'bed',bed2:'bed',bed3:'bed',rent:'rent',bank:'bank',market:'market',pump:'pump',bills:'bills',food:'food',street:'street',office:'office'}[s.id]}));
const sceneAt=t=>SCENES.find(s=>t>=s.t0&&t<s.t1)||SCENES[SCENES.length-1];
// ---------------------------------------------------------------- people
const hero=createFigure(scene,{skin:0xf2e2c6,shirt:0xf6f2ea,pants:0x2b2c33,headR:0.152,hair:0x2a1c14});
const extras=[]; function extra(setId,root,yaw,pose,mood,cols={}){ const f=createFigure(scene,{skin:cols.skin??0xe2c39a,shirt:cols.shirt??0x6a7a8a,pants:cols.pants??0x35343a,tie:cols.tie??0x7a3f3a,headR:0.165}); const e={f,setId,root,yaw,pose,mood,seed:extras.length*1.7,look:cols.look||0}; extras.push(e); return e; }
const idle=(t,s)=>0.012*Math.sin(t*1.9+s);
const stand=(root,yaw,o={})=>({root,yaw,P:{...R.P0,...o}});
extra('rent',V(0.55,0,0.0),-2.7,{p:0.05,tilt:0.0,sL:0.2,tL:V(0.0,1.1,0.25),wL:1,pL:V(-0.3,-0.7,0.3)},0.18,{skin:0xd9b48a,shirt:0x8a7a52,pants:0x4a3f33});          // the landlord, hand out
extra('bank',V(0.75,0,-1.45),Math.PI*0.8,{p:0.08,tilt:0.1,aL:1.5,aR:1.5,kL:1.5,kR:1.5,sit:1},0.55,{skin:0xd9b48a,shirt:0x7a98b8,pants:0x2b3340});                         // the clerk (sitting behind the counter)
extra('market',V(0.7,0,-1.9),Math.PI*0.9,{p:0.1,tilt:0.0},0.8,{skin:0xb98a62,shirt:0xe8dcb0,pants:0x4a4038});                                                    // the vendor
extra('food',V(-1.9,0,-1.0),0.5,{aL:1.5,aR:1.5,kL:1.5,kR:1.5,sit:1,p:0.1},0.7,{skin:0xd9b48a,shirt:0xa86a4a});                                                  // diners
extra('food',V(2.0,0,-1.2),Math.PI-0.4,{aL:1.5,aR:1.5,kL:1.5,kR:1.5,sit:1,p:0.15},0.6,{skin:0xb98a62,shirt:0x4a7a6a});
extra('pump',V(0.6,0,-0.3),Math.PI+0.4,{p:0.05,tilt:0.0},0.5,{skin:0xd9b48a,shirt:0xe8e1d4,pants:0x3a3a40});                                                       // the attendant
for(const [x,s] of [[-1.9,0.4],[2.2,-0.4]]) extra('office',V(x,0,-1.0),s>0?-0.8:Math.PI+0.5,{aL:1.5,aR:1.5,kL:1.5,kR:1.5,sit:1,p:0.2,tilt:0.2},0.4,{skin:0xd9b48a,shirt:s>0?0x7a98b8:0xb89a7a});
// ---------------------------------------------------------------- props: phone, wallet, cash notes
const phone=new THREE.Group(); { B(phone,0.075,0.15,0.01,M(0x0d0e12,{r:0.3,m:0.4}),0,0,0,{round:0.01}); B(phone,0.067,0.138,0.004,new THREE.MeshBasicMaterial({color:0xc9a860}),0,0,0.006,{cast:false}); } phone.scale.setScalar(1.6); scene.add(phone); const phoneLight=new THREE.PointLight(0xffd890,0,2.4,2); scene.add(phoneLight);
const wallet=new THREE.Group(); const panL=new THREE.Group(), panR=new THREE.Group(); wallet.add(panL,panR); { const wm=M(0x8a3a28,{r:0.55}), im=M(0xd9c8a8,{r:0.8}); for(const [par,sx] of [[panL,-1],[panR,1]]){ B(par,0.11,0.012,0.15,wm,sx*0.055,0,0,{round:0.005}); B(par,0.1,0.004,0.14,im,sx*0.055,0.008,0,{cast:false}); } } scene.add(wallet);
const notes=[]; for(let i=0;i<16;i++){ const n=B(scene,0.12,0.005,0.06,M(0xcfe3b5,{r:0.8,e:0x9fd08a,ei:0.5}),0,-9,0); notes.push(n); }
const tmp=new THREE.Vector3();
// ---------------------------------------------------------------- mood
const hapAt=t=>keys(TL.hap,t);
const blinkAt=t=>((t*0.37)%1)<0.045?1:0;
const dayAt=t=>{ let d=0; ITEMS.forEach((it,i)=>{ if(t>=it.t-0.1) d=i+1; }); return d; };
// ---------------------------------------------------------------- hero poses (set-local root, world origin added)
function proppedPose(){ return {...R.P0,aL:1.3,aR:1.3,kL:0.12,kR:0.12,p:-0.95,tilt:1.25,sL:0.5,sR:0.5,eL:1.4,eR:1.4}; }
function heroPose(t,sc){ const ox=sets[sc.set].userData.ox; const m=hapAt(t); const fwdT=(x,z)=>SLD.yawOf(V(x,0,z));
  const o=(J)=>{ for(const k in J) if(J[k].isVector3&&k!=='fwd') J[k].x+=ox; return J; };
  let J,face={mood:m,blink:blinkAt(t)},dress={};
  const hold=(P,hand,tgtL)=>{ P.tL=tgtL; P.wL=hand; P.pL=V(-0.3,-0.7,0.35); };
  if(sc.id==='bed1'||sc.id==='bed3'){ const s=sc.id==='bed3'?(t-18.6)*1.5:t; const bp=BS.pose(s); const fc=BS.face(s); const lying=s<2.4;
    face={roll:bp.roll||0,mood:fc.mood,brow:fc.brow,wide:fc.wide,open:fc.open,blink:fc.sleep?1:(s<1.2?0:blinkAt(t)),fwd:bp.faceFwd};
    return {J:o(bp.J),face,dress:{},phone:!!bp.phone,phonePos:bp.phone.pos.clone().add(V(ox,0,0)),phoneN:bp.phone.n,phoneLit:bp.phoneLight,bp}; }
  if(sc.id==='bed2'){ // reality: on the bed edge, the empty wallet turned upside down; the alarm; he pulls on his office shirt, takes the bag and leaves
    const w0=TL.wake[0], w1=TL.wake[1], al=TL.alarm; const t0=sc.t0;
    const sit={...R.P0,aL:1.5,aR:1.5,kL:1.5,kR:1.5,sL:0.4,sR:0.4,eL:0.8,eR:0.8,p:0.3+0.25*sstep(al-0.6,al-0.1,t)*(1-sstep(al,al+0.2,t)),tilt:0.35}; const st={...R.P0,p:0.2,tilt:0.1}; const wk=sm5(clamp((t-w0)/(w1-w0)));
    const wu=Math.max(0,t-w1); const rt=V(0.25,0,-0.3).lerp(V(0.5,0,0.5),wk).add(V(wu*1.0,0,0)); const yaw=lerp(SLD.yawOf(V(0.35,0,0.94)),SLD.yawOf(V(1,0,0.12)),sstep(w1,w1+0.3,t));
    let P=R.blend(sit,st,wk); if(wu>0) P=R.gait({...P},wu*7.5,sstep(w1,w1+0.2,t)*0.9,0.34,0.62,0.2);
    const flip=sstep(t0+0.1,t0+0.7,t), shake=(t>t0+0.3&&t<t0+0.9)?0.02*Math.sin(t*34):0; const place=sstep(al+0.0,al+0.4,t); const wp0=V(rt.x+0.12,0.74+0.22*flip+shake,rt.z+0.38); const wp=wp0.clone().lerp(V(-0.35,0.575,-0.95),place); wp.y+=0.18*Math.sin(Math.PI*place); const hold=1-sstep(al,al+0.3,t);
    const dr=sstep(w0+0.1,w0+0.22,t)*(1-sstep(w0+0.34,w0+0.46,t));   // both arms up: the shirt goes on
    if(t<w0&&hold>0){ P.tL=wp.clone().add(V(-0.06,0,0)); P.wL=hold; P.pL=V(-0.3,-0.7,0.35); P.tR=wp.clone().add(V(0.06,0,0)); P.wR=hold; P.pR=V(-0.3,-0.7,-0.35); }
    else if(dr>0){ P.tL=V(rt.x+0.05,1.72,rt.z+0.12); P.wL=dr; P.pL=V(-0.5,0.2,0.6); P.tR=V(rt.x+0.05,1.72,rt.z-0.12); P.wR=dr; P.pR=V(-0.5,0.2,-0.6); }
    J=R.skel(P,rt,yaw); const bag=sstep(w0+0.3,w1,t); const clothed=t>w0+0.25; dress=clothed?{bag,tie:bag,collar:1,lanyard:bag}:{}; face={mood:m,blink:blinkAt(t),fwd:J.fwd};
    return {J:o(J),face,dress,phone:false,wallet:{pos:wp.clone().add(V(ox,0,0)),flip,held:true}}; }
  dress={tie:1,collar:1,lanyard:1,bag:1,belt:1};
  const yawF=SLD.yawOf(V(0.5,0,0.85));
  if(sc.id==='rent'){ const P=R.gait({...R.P0,p:0.06+0.25*(1-m),tilt:0.1,sL:0.1},0,0); P.tR=V(0.02,1.05,0.25); P.wR=sstep(TL.items[0].t-0.4,TL.items[0].t,t); P.pR=V(0,-0.6,-0.5); J=R.skel(P,V(-0.4,0,0.2),yawF); }
  else if(sc.id==='bank'){ const P={...R.P0,p:0.05+0.25*(1-m),tilt:0.1}; P.tR=V(0.2,1.12,-0.2); P.wR=sstep(TL.items[1].t-0.4,TL.items[1].t,t); P.pR=V(0,-0.6,-0.5); J=R.skel(P,V(-0.45,0,0.25),yawF); }
  else if(sc.id==='market'){ const P={...R.P0,p:0.06+0.28*(1-m),tilt:0.12}; P.tR=V(0.0,1.0,-0.1); P.wR=sstep(TL.items[2].t-0.4,TL.items[2].t,t); P.pR=V(0,-0.6,-0.5); P.tL=V(-0.6,0.62,0.45); P.wL=sstep(TL.items[2].t,TL.items[2].t+0.4,t); J=R.skel(P,V(-0.5,0,0.3),yawF); }
  else if(sc.id==='bills'){ const P={...R.P0,aL:1.5,aR:1.5,kL:1.5,kR:1.5,p:0.2+0.25*(1-m),tilt:0.1+0.15*(1-m),eL:1.0,eR:1.0}; P.tL=V(-0.1,0.95,-0.6); P.wL=1; P.pL=V(-0.3,-0.7,0.4); P.tR=V(0.1,0.95,-0.6); P.wR=1; P.pR=V(-0.3,-0.7,-0.4); J=R.skel(P,V(-0.2,0,-0.15),yawF); }
  else if(sc.id==='food'){ const P={...R.P0,aL:1.5,aR:1.5,kL:1.5,kR:1.5,p:0.2+0.3*(1-m),tilt:0.3,eL:1.1,eR:1.1}; P.tR=V(0.25,0.95,-0.45); P.wR=1; P.pR=V(-0.3,-0.7,-0.4); P.tL=V(0.12,0.9,-0.4); P.wL=1; P.pL=V(-0.3,-0.7,0.4); J=R.skel(P,V(-0.2,0,-0.5),SLD.yawOf(V(0.8,0,0.6))); }
  else if(sc.id==='pump'){ const P={...R.P0,p:0.08+0.3*(1-m),tilt:0.2}; P.tR=V(0.5,0.95,-0.3); P.wR=1; P.pR=V(0,-0.6,-0.5); J=R.skel(P,V(-0.15,0,0.3),SLD.yawOf(V(0.5,0,0.85))); }
  else if(sc.id==='street'){ const u=(t-sc.t0)/(sc.t1-sc.t0); const ph=u*14; const P=R.gait({...R.P0,p:0.12,tilt:0.1,eL:0.5,eR:0.5},ph,1,0.34,0.62,0.2); J=R.skel(P,V(lerp(-0.6,0.6,u),0,lerp(1.1,-1.6,u)),SLD.yawOf(V(0.25,0,-1))); face={mood:m,blink:0,fwd:J.fwd}; return {J:o(J),face,dress,phone:false}; }
  else { // office: one continuous desk time-lapse: typing, coffee, rubbing his eyes, working on as the window goes day-night-day and the pile grows, the slump, then a hopeful look up
    const O0=TL.office[0], O1=TL.office[1]; const u=clamp((t-O0)/(O1-O0));
    const slump=sstep(0.5,0.76,u), hope=sstep(0.8,0.9,u), rub=sstep(0.47,0.52,u)*(1-sstep(0.6,0.65,u));
    const look=sstep(0.8,0.9,u); const P={...R.P0,aL:1.5,aR:1.5,kL:1.5,kR:1.5,p:0.25+0.3*slump*(1-hope)+0.03*Math.sin(t*1.3),tilt:0.45+0.25*slump-0.8*hope,eL:1.0,eR:1.0,hy:0.95*look,ty:0.3*look};
    const root=V(0.6,0,-0.5), yaw=SLD.yawOf(V(0,0,-1)); const J0=R.skel(P,root,yaw); const hd=J0.head, fw=J0.fwd.clone();
    const ty=t*13; const tying=1-rub;
    const kL=V(0.72,0.86+Math.max(0,Math.sin(ty))*0.012*tying,-1.0), kR=V(0.48,0.86+Math.max(0,Math.sin(ty+2))*0.012*tying,-1.0);
    const cupBase=V(1.0,0.93,-1.0), mouth=hd.clone().addScaledVector(fw,0.17).add(V(0,-0.1,0.0));
    const c1=sstep(0.19,0.225,u), c2=sstep(0.225,0.26,u), c3=sstep(0.30,0.335,u), c4=sstep(0.335,0.37,u);
    let tR=kR.clone().lerp(cupBase,c1).lerp(mouth,c2).lerp(cupBase,c3).lerp(kR,c4); let tL=kL.clone();
    const eyeR=hd.clone().addScaledVector(fw,0.15).add(V(-0.06,-0.02,0)), eyeL=hd.clone().addScaledVector(fw,0.15).add(V(0.06,-0.02,0));
    tR=tR.lerp(eyeR,rub); tL=tL.lerp(eyeL,rub);
    P.tL=tL; P.wL=1; P.pL=V(-0.3,-0.7,0.5); P.tR=tR; P.wR=1; P.pR=V(-0.3,-0.7,-0.5);
    J=R.skel(P,root,yaw);
    const grabbed=(u>0.225&&u<0.335); const cupPos=grabbed?J.hR.clone().add(V(0,0.0,0)):V(1.0,0.86,-1.0);
    face={mood:Math.max(0.06,m*0.6+0.45*hope),blink:rub>0.5?1:blinkAt(t),fwd:J.fwd,look:0.95*look,brow:0.5*hope};
    return {J:o(J),face,dress,phone:false,cupPos,u,eyeRub:rub}; }
  face={mood:m,blink:blinkAt(t),fwd:J.fwd}; return {J:o(J),face,dress,phone:false}; }
// ---------------------------------------------------------------- lights per scene
const LIGHTS={ bed:{key:[-1.8,2.4,1.2,0.2,0.6,-0.6,20],a:[-1.95,0.95,-1.3,0xffa24a,1.8],b:[1.7,1.7,-1.3,0xffb870,2.0],fill:[2.5,1.6,3,0x78a6ff,0.9],hemi:[0xffd9b0,0x3a2a22,0.5],bg:0x201512},
  rent:{key:[-2.5,3,2.5,-0.2,1,0,20],a:[1.6,1.6,-1.4,0xffd890,1.6],b:[-0.5,2.4,-1,0xffa860,2],fill:[2.5,1.6,3,0x78a6ff,0.8],hemi:[0xffd9b0,0x2a2a2e,0.45],bg:0x1a1614},
  bank:{key:[-1,3.2,2.5,0.2,0.8,-0.5,24],a:[0.3,2.6,-0.5,0xfff0c8,3],b:[-1.5,2.4,0.5,0xffe0a8,1.5],fill:[2.5,1.6,3,0x88b0ff,0.9],hemi:[0xe8e0d0,0x2a2a2e,0.5],bg:0x161a1c},
  market:{key:[-1.5,2.8,2.5,0.2,0.9,-0.8,22],a:[0.2,2.2,-0.6,0xffb860,3.4],b:[-1.3,2.2,-0.5,0xffb860,2.6],fill:[2.5,1.6,3,0x8070c0,0.8],hemi:[0xffc890,0x2a2230,0.45],bg:0x120d16},
  bills:{key:[-1.8,2.6,2,0,0.9,-0.6,22],a:[-0.95,1.5,-1.2,0xffb868,3],b:[0.9,1.9,-1.2,0xfff0c8,1.6],fill:[2.5,1.6,3,0x78a6ff,0.9],hemi:[0xffd9b0,0x3a2a22,0.5],bg:0x1a1210},
  food:{key:[-1.5,2.8,2.2,0.1,0.9,-0.5,22],a:[-0.2,2.2,-1.4,0xffb860,3.2],b:[1.2,2.2,-1.4,0xffb860,2.6],fill:[2.5,1.6,3,0x78a6ff,0.7],hemi:[0xffc890,0x3a2418,0.5],bg:0x1c1210},
  pump:{key:[0,3.0,1.8,0.2,0.8,-0.8,34],a:[-1.8,2.9,-1.3,0xfff4dc,3.2],b:[1.8,2.9,-1.3,0xfff4dc,3.2],fill:[2.5,1.6,3,0x6a90e8,0.9],hemi:[0xaab8e0,0x201a24,0.4],bg:0x0d1018},
  street:{key:[3,5,2,0,1,-2,28],a:[1.4,2.8,-0.6,0xffb868,4.5],b:[-1.8,2.6,-1,0xffa860,3],fill:[2.5,1.6,3,0xa0c0ff,0.8],hemi:[0xffe0b0,0x5a4a3a,0.8],bg:0xffc98a},
  office:{key:[-1,3.2,1.8,0.2,1,-1,24],a:[0.4,1.6,-1.6,0xb8d8ff,2.4],b:[0.6,3,-0.8,0xfff0c8,2],fill:[2.5,1.6,3,0x78a6ff,0.9],hemi:[0xe8e0d0,0x2a2a2e,0.5],bg:0x161a1c} };
function applyLights(id,ox,t){ const L=LIGHTS[id]; const k=L.key; ST.key.position.set(ox+k[0],k[1],k[2]); ST.key.target.position.set(ox+k[3],k[4],k[5]); ST.key.intensity=k[6]; ST.key.angle=1.15; ST.lampA.position.set(ox+L.a[0],L.a[1],L.a[2]); ST.lampA.color.setHex(L.a[3]); ST.lampA.intensity=L.a[4]; ST.lampB.position.set(ox+L.b[0],L.b[1],L.b[2]); ST.lampB.color.setHex(L.b[3]); ST.lampB.intensity=L.b[4]; ST.fill.position.set(ox+L.fill[0],L.fill[1],L.fill[2]); ST.fill.color.setHex(L.fill[3]); ST.fill.intensity=L.fill[4]*1.6; ST.fill.position.set(ox+0.8,1.8,4.2); ST.hemi.color.setHex(L.hemi[0]); ST.hemi.groundColor.setHex(L.hemi[1]); ST.hemi.intensity=L.hemi[2]; const BGN=id==='street'?0x1b2233:0x161b25; ST.key.intensity*=0.38; ST.key.color.setHex(0xffb470); ST.lampA.color.setHex(0xffae62); ST.lampA.intensity*=0.95; ST.lampB.color.setHex(0xffb878); ST.lampB.intensity*=0.6; ST.fill.color.setHex(0x5873b0); ST.fill.intensity*=0.45; ST.hemi.color.setHex(0x3a4c78); ST.hemi.groundColor.setHex(0x241c16); ST.hemi.intensity=0.28; scene.background.setHex(BGN); scene.fog.color.setHex(BGN); }
// ---------------------------------------------------------------- cameras (set-local pos, look at start and end of each scene)
const CAMS={ bed1:[[0.55,1.2,3.3],[-0.45,0.95,-0.9],[0.55,1.25,3.2],[-0.3,1.0,-0.7]], rent:[[-0.1,1.45,4.0],[-0.15,1.15,0.1],[-0.15,1.45,3.6],[-0.15,1.15,0.1]], bank:[[-0.1,1.5,4.2],[-0.15,1.2,-0.3],[-0.1,1.45,3.8],[-0.15,1.2,-0.3]], market:[[-0.05,1.45,4.2],[-0.1,1.15,-0.4],[-0.05,1.45,3.8],[-0.1,1.15,-0.4]],
  bills:[[0.05,1.4,3.6],[-0.1,1.05,-0.4],[0.05,1.35,3.2],[-0.1,1.05,-0.4]], food:[[0.1,1.35,3.6],[0.0,1.0,-0.4],[0.1,1.3,3.2],[0.0,1.0,-0.4]], pump:[[0.0,1.45,4.2],[-0.05,1.1,-0.2],[0.0,1.45,3.8],[-0.05,1.1,-0.2]], bed2:[[0.8,1.35,4.6],[0.3,0.95,-0.3],[0.9,1.35,4.4],[0.55,0.95,-0.2]],
  street:[[0.0,1.5,5.0],[0.0,1.1,-1.0],[0.0,1.45,4.0],[0.0,1.1,-1.0]], office:[[0.35,1.45,3.8],[0.2,1.15,-0.8],[0.3,1.4,3.4],[0.2,1.15,-0.8]], bed3:[[0.55,1.25,3.2],[-0.3,1.0,-0.7],[0.55,1.2,3.3],[-0.45,0.95,-0.9]] };
// ---------------------------------------------------------------- the money: cash notes fly from his hand to the counterpart
function payNotes(t){ let used=0; if(sceneAt(t).id==='bed1') { for(const n of notes) n.position.set(0,-9,0); return; } ITEMS.forEach((it,i)=>{ const u=(t-it.t)/0.5; if(u>0&&u<1){ for(let k=0;k<4;k++){ const n=notes[used++]; const uu=clamp(u*1.0-k*0.07); if(uu<=0||uu>=1){ n.position.set(0,-9,0); continue; } const sc=sceneAt(t); const ox=sets[sc.set].userData.ox; const a=V(-0.4,1.05,0.4), b=[V(0.3,1.1,0.2),V(0.5,1.2,-0.7),V(0.6,1.1,-1.6),V(1.2,0.9,-0.9),V(0.4,0.9,-0.9),V(0.2,0.9,-0.5)][i]; tmp.copy(a).lerp(b,uu*uu*(3-2*uu)); tmp.y+=0.3*Math.sin(Math.PI*uu); n.position.set(ox+tmp.x,tmp.y,tmp.z); n.rotation.set(uu*6,uu*5,0); } } }); for(let k=used;k<notes.length;k++) notes[k].position.set(0,-9,0); }

// ---------------------------------------------------------------- the blanket: a thin cloth draped over his body (height field from his limbs), tucked at the back, hanging over the front edge
const BL={nx:130,nw:84,x0:-0.56,x1:1.12}; const blGeo=new THREE.PlaneGeometry(1,1,BL.nx,BL.nw); const blMesh=new THREE.Mesh(blGeo,new THREE.MeshStandardMaterial({map:SETS.plaidTex(),roughness:0.95,side:THREE.DoubleSide})); blMesh.castShadow=true; blMesh.receiveShadow=true; blMesh.frustumCulled=false; sets.bed.add(blMesh); sets.bed.userData.quilt.visible=false;
{ const uv=blGeo.attributes.uv; for(let j=0;j<=BL.nw;j++) for(let i=0;i<=BL.nx;i++){ const k=j*(BL.nx+1)+i; uv.setXY(k,i/BL.nx*1.6,j/BL.nw*1.2); } }
function updateBlanket(J,qt){ const pos=blGeo.attributes.position; const segs=[]; if(J&&qt<0.98){ const add=(a,b,r)=>segs.push([a,b,r]); add(J.hip,J.neck,0.14); add(J.hipL,J.kL,0.085); add(J.hipR,J.kR,0.085); add(J.kL,J.fL,0.065); add(J.kR,J.fR,0.065); add(J.shL,J.elL,0.055); add(J.shR,J.elR,0.055); add(J.elL,J.hL,0.05); add(J.elR,J.hR,0.05); }
  const xa=lerp(BL.x0,0.5,qt), xb=BL.x1; const topY=0.545, zb=-1.8, zf=-0.6;
  for(let j=0;j<=BL.nw;j++){ const w=j/BL.nw; for(let i=0;i<=BL.nx;i++){ const x=lerp(xa,xb,i/BL.nx); let z,y; const sp=0.84;
      const zz=w<sp?lerp(zb,zf,w/sp):zf; let h=topY+0.004*Math.sin(x*23+zz*9); let wt=1-qt; let nd=1;
      if(segs.length){ for(const [a,b,r] of segs){ const dx=b.x-a.x, dz=b.z-a.z, L2=dx*dx+dz*dz+1e-6; let u=((x-a.x)*dx+(zz-a.z)*dz)/L2; u=clamp(u); const px=a.x+dx*u, pz=a.z+dz*u, py=a.y+(b.y-a.y)*u; const d=Math.hypot(x-px,zz-pz); const top=py+(r+0.008)*Math.exp(-Math.pow(d/(r*1.25),2)); if(top>h) h=top; nd=Math.min(nd,d-r); } if(x<-0.42) h=lerp(topY+0.02,h,clamp((x+0.56)/0.14)); }
      { const near=Math.exp(-Math.max(0,nd)/0.2); const amp=(0.004+0.013*near)*(1+2.0*Math.sin(Math.PI*clamp(qt))); h+=amp*(0.9*Math.sin(x*27+1.7*Math.sin(zz*5.3)+zz*2.1)+0.7*Math.sin(zz*19-x*13+Math.sin(x*7)*2)+0.5*Math.sin((x+zz)*43+Math.sin(zz*11)*1.5)); }
      h=lerp(topY,h,wt); // bunched at the foot once he pushes it off
      h+=qt*0.15*(0.5+0.5*Math.sin(x*26+1))*Math.exp(-Math.pow((x-0.72)/0.3,2))*(0.6+0.4*Math.sin(zz*7));
      if(w<=sp){ z=zz; y=h; if(x>0.93) y-=Math.pow((x-0.93)*3.0,1.5); } else { const jj=(w-sp)/(1-sp); z=zf+0.06*Math.sin(jj*Math.PI/2)*(1-0.5*qt); y=h-(0.2+0.015*Math.sin(x*17+zz))*jj*(1-qt*0.6); if(x>0.93) y-=(x-0.93)*2.2; if(qt>0.6) y=Math.max(y,0.535); }
      const k=j*(BL.nx+1)+i; pos.setXYZ(k,x,y,z); } }
  pos.needsUpdate=true; blGeo.computeVertexNormals(); }
// ---------------------------------------------------------------- one frame
const WIDE=q.has('wide')?+q.get('wide'):1;
const XF=q.has('xf')?+q.get('xf'):0.1;   // half-width of the dissolve at each cut in seconds; ?xf=0 gives hard cuts (v2)
function pickScene(t,k,K){ if(XF<=0) return sceneAt(t); for(let i=1;i<SCENES.length;i++){ const s0=SCENES[i].t0; if(Math.abs(t-s0)<XF){ const a=sstep(s0-XF,s0+XF,t); return ((k+0.5)/K<a)?SCENES[i]:SCENES[i-1]; } } return sceneAt(t); }
function setT(t,k=0,K=1){ const sc=pickScene(t,k,K); const ox=sets[sc.set].userData.ox; order.forEach(k=>{ sets[k].visible=(k===sc.set); });
  applyLights(sc.set,ox,t); { const pj=(sc.id==='bed1'||sc.id==='bed3'||(sc.id==='bed2'&&t<TL.wake[0]+0.25)); if(hero.pj!==pj){ hero.pj=pj; hero.setColors(pj?{shirt:0x8aa0bc,pants:0x56648a}:{shirt:0xf6f2ea,pants:0x2b2c33}); } }
  const hp=heroPose(t,sc); hero.setVisible(true); hero.pose(hp.J,hp.face,hp.dress);
  extras.forEach(e=>{ const on=e.setId===sc.set&&!(e.setId==='office'&&e.root.x>1); e.f.setVisible(on); if(!on) return; const sit=e.pose.sit; const P={...R.P0,...e.pose}; delete P.sit; P.p=(P.p||0)+idle(t,e.seed); const root=e.root.clone().add(V(ox,sit?0:0,0)); const J=R.skel(P,root,e.yaw); J.fwd=J.fwd||V(1,0,0); e.f.pose(J,{mood:e.mood,blink:blinkAt(t+e.seed),fwd:J.fwd},{tie:e.setId==='bank'||e.setId==='office'?1:0,collar:1,belt:1}); });
  phone.visible=!!hp.phone; if(hp.phone){ phone.position.copy(hp.phonePos); { const zA=hp.phoneN.clone(); const yA=V(1,0,0).addScaledVector(zA,-zA.x).normalize(); const xA=yA.clone().cross(zA); phone.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(xA,yA,zA)); } const lit=hp.phoneLit; phoneLight.position.copy(hp.phonePos).addScaledVector(hp.phoneN,0.3); phoneLight.intensity=0.09*lit; } else phoneLight.intensity=0;
  wallet.visible=!!hp.wallet; if(hp.wallet){ wallet.position.copy(hp.wallet.pos); wallet.rotation.set(Math.PI/2*0.9,0,Math.PI*hp.wallet.flip); const op=0.9*sstep(sc.t0,sc.t0+0.3,t); panL.rotation.z=-op*0.4; panR.rotation.z=op*0.4; }
  payNotes(t);
  let cm=CAMS[sc.id]; let u=sm5(clamp((t-sc.t0)/(sc.t1-sc.t0)));
  let pos=V(...cm[0]).lerp(V(...cm[2]),u), look=V(...cm[1]).lerp(V(...cm[3]),u);
  if(hp.bp){ pos=hp.bp.cam.pos.clone(); look=hp.bp.cam.look.clone(); }
  if(sc.id==='office'){ const e=sm5(clamp((t-sc.t0)/(sc.t1-sc.t0))); pos=V(lerp(3.1,2.7,e),1.45,lerp(2.2,1.0,e)); look=V(0.45,0.98,lerp(-0.6,-0.9,e)); const f=sstep(0.78,0.97,(t-sc.t0)/(sc.t1-sc.t0)); pos.lerp(V(1.9,1.35,0.7),f); look.lerp(V(-0.2,1.35,-1.4),f); }
  if(window.DBG){ pos=V(...window.DBG.pos); look=V(...window.DBG.look); }
  if(WIDE!==1&&!window.DBG){ pos=look.clone().add(pos.clone().sub(look).multiplyScalar(WIDE*((sc.set==='bed')?1.3:1))); }
  ST.cam.position.set(ox+pos.x,pos.y,pos.z); ST.cam.lookAt(ox+look.x,look.y,look.z);
  ST.grade.uniforms.uFlash.value=0; ST.grade.uniforms.uT.value=t;
  let fl=0; SCENES.forEach(s=>{ if(s.t0>0.1) fl=Math.max(fl,0.45*Math.max(0,1-Math.abs(t-s.t0)/0.09)); }); if(XF<=0) fl=0;   // hard cuts: no warm flash either ST.grade.uniforms.uFlash.value=fl; ST.grade.uniforms.uT.value=t;
  if(sc.set==='office'){ const o=sets.office; const uo=clamp((t-TL.office[0])/(TL.office[1]-TL.office[0])); const dn=0.12*(0.5+0.5*Math.cos(2*Math.PI*2.4*uo)); // 1 = bright day, 0 = night; ends in the evening
    o.userData.sky.color.setRGB(0.02+0.03*dn,0.03+0.03*dn,0.07+0.06*dn); ST.hemi.intensity*=0.35+0.65*dn; ST.key.intensity*=0.3+0.7*dn; ST.lampA.intensity*=0.3+0.7*dn; scene.background.setRGB(lerp(0.02,0.09,dn),lerp(0.03,0.1,dn),lerp(0.06,0.11,dn));
    { const dw=0; if(dw>0){ const sk=o.userData.sky.color; sk.r=lerp(sk.r,1.0,dw); sk.g=lerp(sk.g,0.78,dw); sk.b=lerp(sk.b,0.45,dw); ST.hemi.intensity*=1+0.8*dw; ST.key.intensity*=1+0.5*dw; ST.hemi.color.setHex(0xffd9a0); scene.background.setRGB(0.25*dw,0.18*dw,0.1*dw); } o.userData.glow=dw; }
    o.userData.coffee.position.y=0.03-0.02*sstep(0.22,0.3,uo)-0.012*sstep(0.6,0.9,uo); o.userData.clockHand.rotation.z=-t*6;
    const cal=o.userData.cal; const x=uo>0.93?31:6+Math.floor(24.99*uo); if(cal.userData.x!==x){ cal.userData.x=x; cal.material.map.dispose(); cal.material.map=x===31?SETS.calendarTex(1,0,'FEBRUARY'):SETS.calendarTex(0,x,'JANUARY'); cal.material.needsUpdate=true; } cal.material.emissive.setRGB(1,0.75,0.35); cal.material.emissiveIntensity=0.55*(o.userData.glow||0); cal.material.emissiveMap=cal.material.map;
    const cg=o.userData.cupG; if(cg&&hp.cupPos) cg.position.set(hp.cupPos.x,hp.cupPos.y,hp.cupPos.z);
    // the pile on his desk grows; empty cups pile up
    const pl=o.userData.piles; pl.forEach((p,i)=>{ const h=0.02+0.3*Math.pow(uo,1.1)*[1,0.8,0.55][i]; p.scale.y=h/0.1; p.position.y=0.81+h/2; });
    o.userData.cups.forEach((c,i)=>{ c.visible=uo>[0.34,0.58,0.78][i]; }); }
  if(sc.set==='bed'){ const qt=hp.bp?hp.bp.quilt:1; blMesh.visible=true; updateBlanket(hp.bp?hp.bp.J:null,qt); const b=sets.bed; { const key=sc.id==='bed2'?'7/6':'1/0'; const cal=b.userData.cal; if(cal.userData.k!==key){ cal.userData.k=key; cal.material.map.dispose(); cal.material.map=sc.id==='bed2'?SETS.calendarTex(7,6,'JANUARY'):SETS.calendarTex(1,0,'JANUARY'); cal.material.needsUpdate=true; } } const x=sc.id==='bed2'?6:5; b.userData.note.visible=(sc.id==='bed3'||sc.id==='bed1'); }
}
window.renderAt=(t,K=3)=>{ let cut=false; for(let i=1;i<SCENES.length;i++) if(Math.abs(t-SCENES[i].t0)<0.1) cut=true; const walk=(t>11.6&&t<13.4); return ST.renderAt(setT,t,cut?Math.max(K,6):(walk?Math.max(K,4):K),{t0:0,t1:DUR,shutter:walk?1/36:1/60}); };
window.events={...TL}; window.ready=true;
