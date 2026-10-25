// The Salary Loop (warm). A lived-in miniature film: his bedroom (hook, reality, the end), the rent door, the bank, the market, the bills desk,
// a restaurant, the petrol pump, his street at sunrise, his office. One stickman with a face (mood 0..1 = hap), office clothes and a side bag.
// renderAt(t) is pure. Units are metres. Each set lives at x = 16 * index; the camera is always in front (+z).
import * as THREE from 'three';
import {createWarmStage,V,clamp,sstep,lerp} from './stage.js';
import * as SLD from './sld.js';
import {createFigure} from './figure.js';
import * as SETS from './sets.js';
const {M,B,C,S: SPH,P: PLN}=SETS;
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960;
const TL=await (await fetch('timeline.json')).json(); const DUR=TL.duration, ITEMS=TL.items;
const ST=createWarmStage({W,H}); const R=SLD.createRig(ST.scene); const scene=ST.scene; const sm5=SLD.sm5, keys=SLD.keys;
const SP=16;
// ---------------------------------------------------------------- sets
const sets={}; const order=['bed','rent','bank','market','bills','food','pump','street','office'];
const builders={bed:SETS.buildBedroom,rent:SETS.buildRent,bank:SETS.buildBank,market:SETS.buildMarket,bills:SETS.buildBills,food:SETS.buildRestaurant,pump:SETS.buildPump,street:SETS.buildStreet,office:SETS.buildOffice};
order.forEach((k,i)=>{ const g=builders[k](); g.position.x=i*SP; g.visible=false; scene.add(g); sets[k]=g; g.userData.ox=i*SP; });
const SCENES=TL.scenes.map(s=>({...s,set:{bed1:'bed',bed2:'bed',bed3:'bed',rent:'rent',bank:'bank',market:'market',bills:'bills',food:'food',pump:'pump',street:'street',office:'office'}[s.id]}));
const sceneAt=t=>SCENES.find(s=>t>=s.t0&&t<s.t1)||SCENES[SCENES.length-1];
// ---------------------------------------------------------------- people
const hero=createFigure(scene,{skin:0xf2e2c6,shirt:0xf6f2ea,pants:0x2b2c33});
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
const phone=new THREE.Group(); { B(phone,0.075,0.15,0.01,M(0x0d0e12,{r:0.3,m:0.4}),0,0,0,{round:0.01}); B(phone,0.067,0.138,0.004,new THREE.MeshBasicMaterial({color:0xc9a860}),0,0,0.006,{cast:false}); } scene.add(phone); const phoneLight=new THREE.PointLight(0xffd890,0,2.4,2); scene.add(phoneLight);
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
  if(sc.id==='bed1'||sc.id==='bed3'){ const tt=sc.id==='bed3'?t-20+TL.duration*0:t; // the loop: bed3 ends exactly where bed1 starts
    const lift=sc.id==='bed1'?(1-sstep(0.5,1.0,t)):sstep(TL.notify[0],TL.notify[0]+0.3,t); const phoneUp=1; const prop=proppedPose(); const root=V(0.3,0.34,-1.0);
    if(sc.id==='bed1'&&t>=TL.rise[0]){ const u=sm5(clamp((t-TL.rise[0])/(TL.rise[1]-TL.rise[0]))); const stand_={...R.P0,p:0.05,tilt:-0.1}; const B_=R.blend(prop,stand_,u); const rt=root.clone().lerp(V(0.4,0,0.45),u); const dn=t>=TL.dance[0]; let P=B_;
      if(dn){ const d=(t-TL.dance[0])*7.5, w=Math.sin(Math.PI*clamp((t-TL.dance[0])/(TL.dance[1]-TL.dance[0])))*0.0+1; P={...stand_,kL:0.5*w*Math.abs(Math.sin(d)),kR:0.5*w*Math.abs(Math.cos(d)),aL:0.25*w*Math.sin(d),aR:-0.25*w*Math.sin(d),dy:-0.04*w*Math.abs(Math.sin(d*2)),tilt:-0.2,
        tL:V(rt.x+0.25+0.1*Math.sin(d),1.7+0.12*Math.sin(d*2),rt.z+0.5),wL:1,pL:V(0,-1,0.4),tR:V(rt.x+0.25+0.1*Math.cos(d),1.7+0.12*Math.cos(d*2),rt.z-0.45),wR:1,pR:V(0,-1,-0.4)}; }
      J=R.skel(P,rt,SLD.yawOf(V(0.5,0,0.85))); face={mood:Math.max(m,0.9),blink:0,open:dn?0.8:0.3,fwd:J.fwd}; return {J:o(J),face,dress,phone:false}; }
    // propped on the pillow, the phone in his hands lighting his face; the buzz makes his head lift and his eyes widen (a happy flinch)
    const P=prop; const j=0.01*Math.sin(t*40)*(t<0.9?1-sstep(0.5,0.9,t):0)*(sc.id==='bed1'?1:0)+0.01*Math.sin(t*40)*(sc.id==='bed3'?sstep(TL.notify[0],TL.notify[0]+0.1,t):0);
    P.tilt=1.25-0.35*lift; const J0=R.skel(P,root,0); const ph=J0.head.clone().add(V(0.28,-0.24,0.04)); P.tL=ph.clone().add(V(-0.03,-0.04,0.05)); P.wL=1; P.pL=V(0,-0.9,0.6); P.tR=ph.clone().add(V(0.04,-0.05,-0.04)); P.wR=1; P.pR=V(0,-0.9,-0.6);
    J=R.skel(P,root,0); J.fwd=V(0.86,0.0,0.5).normalize(); const f=J.fwd; face={mood:sc.id==='bed1'?Math.max(m,0.8):m,blink:lift>0.5?0:blinkAt(t),open:0.1+0.6*lift,fwd:f}; face.fwd=V(0.9,-0.2,0.45).normalize();
    return {J:o(J),face,dress,phone:true,phonePos:ph.clone().add(V(ox+j,0.0,0.0)),phoneN:V(-0.15,0.6,-0.6).normalize()}; }
  if(sc.id==='bed2'){ // reality: on the bed edge, the empty wallet turned upside down; the alarm; he gets up and puts the bag on
    const sit={...R.P0,aL:1.5,aR:1.5,kL:1.5,kR:1.5,sL:0.4,sR:0.4,eL:0.8,eR:0.8,p:0.3,tilt:0.35}; const st={...R.P0,p:0.2,tilt:0.35}; const wk=sm5(clamp((t-TL.wake[0])/(TL.wake[1]-TL.wake[0]))); const rt=V(0.25,0,-0.3).lerp(V(0.5,0,0.5),wk);
    const P=R.blend(sit,st,wk); const flip=sstep(9.0,9.5,t), shake=(t>9.1&&t<10.2)?0.02*Math.sin(t*34):0; const wp=V(rt.x+0.12,0.74+0.22*flip+shake,rt.z+0.38);
    if(t<TL.wake[0]){ P.tL=wp.clone().add(V(-0.06,0,0)); P.wL=1; P.pL=V(-0.3,-0.7,0.35); P.tR=wp.clone().add(V(0.06,0,0)); P.wR=1; P.pR=V(-0.3,-0.7,-0.35); }
    J=R.skel(P,rt,SLD.yawOf(V(0.35,0,0.94))); const bag=sstep(TL.wake[0]+0.2,TL.wake[1],t); dress={bag,tie:bag,collar:1,lanyard:bag}; face={mood:m,blink:blinkAt(t),fwd:J.fwd};
    return {J:o(J),face,dress,phone:false,wallet:{pos:wp.clone().add(V(ox,0,0)),flip,held:t<TL.wake[0]&&t>8.75}}; }
  dress={tie:1,collar:1,lanyard:1,bag:1,belt:1};
  const yawF=SLD.yawOf(V(0.5,0,0.85));
  if(sc.id==='rent'){ const P=R.gait({...R.P0,p:0.06+0.25*(1-m),tilt:0.1,sL:0.1},0,0); P.tR=V(0.02,1.05,0.25); P.wR=sstep(TL.items[0].t-0.4,TL.items[0].t,t); P.pR=V(0,-0.6,-0.5); J=R.skel(P,V(-0.4,0,0.2),yawF); }
  else if(sc.id==='bank'){ const P={...R.P0,p:0.05+0.25*(1-m),tilt:0.1}; P.tR=V(0.2,1.12,-0.2); P.wR=sstep(TL.items[1].t-0.4,TL.items[1].t,t); P.pR=V(0,-0.6,-0.5); J=R.skel(P,V(-0.45,0,0.25),yawF); }
  else if(sc.id==='market'){ const P={...R.P0,p:0.06+0.28*(1-m),tilt:0.12}; P.tR=V(0.0,1.0,-0.1); P.wR=sstep(TL.items[2].t-0.4,TL.items[2].t,t); P.pR=V(0,-0.6,-0.5); P.tL=V(-0.6,0.62,0.45); P.wL=sstep(TL.items[2].t,TL.items[2].t+0.4,t); J=R.skel(P,V(-0.5,0,0.3),yawF); }
  else if(sc.id==='bills'){ const P={...R.P0,aL:1.5,aR:1.5,kL:1.5,kR:1.5,p:0.2+0.25*(1-m),tilt:0.1+0.15*(1-m),eL:1.0,eR:1.0}; P.tL=V(-0.1,0.95,-0.6); P.wL=1; P.pL=V(-0.3,-0.7,0.4); P.tR=V(0.1,0.95,-0.6); P.wR=1; P.pR=V(-0.3,-0.7,-0.4); J=R.skel(P,V(-0.2,0,-0.15),yawF); }
  else if(sc.id==='food'){ const P={...R.P0,aL:1.5,aR:1.5,kL:1.5,kR:1.5,p:0.2+0.3*(1-m),tilt:0.3,eL:1.1,eR:1.1}; P.tR=V(0.25,0.95,-0.45); P.wR=1; P.pR=V(-0.3,-0.7,-0.4); P.tL=V(0.12,0.9,-0.4); P.wL=1; P.pL=V(-0.3,-0.7,0.4); J=R.skel(P,V(-0.2,0,-0.5),SLD.yawOf(V(0.8,0,0.6))); }
  else if(sc.id==='pump'){ const P={...R.P0,p:0.08+0.3*(1-m),tilt:0.2}; P.tR=V(0.5,0.95,-0.3); P.wR=1; P.pR=V(0,-0.6,-0.5); J=R.skel(P,V(-0.15,0,0.3),SLD.yawOf(V(0.5,0,0.85))); }
  else if(sc.id==='street'){ const u=(t-sc.t0)/(sc.t1-sc.t0); const ph=u*14; const P=R.gait({...R.P0,p:0.12,tilt:0.1,eL:0.5,eR:0.5},ph,1,0.34,0.62,0.2); J=R.skel(P,V(lerp(-0.6,0.6,u),0,lerp(1.1,-1.6,u)),SLD.yawOf(V(0.25,0,-1))); face={mood:m,blink:0,fwd:J.fwd}; return {J:o(J),face,dress,phone:false}; }
  else { // office: at his desk, head on his hand, the coffee; a hopeful glance up at the calendar
    const g=sstep(15.3,15.6,t)*(1-sstep(15.9,16.2,t))+sstep(16.9,17.2,t)*(1-sstep(17.5,17.8,t));
    const P={...R.P0,aL:1.5,aR:1.5,kL:1.5,kR:1.5,p:0.28-0.14*g,tilt:0.55-0.45*g,eL:1.0,eR:1.0,hy:-0.1*g}; const ty=t*13; P.tL=V(0.32+0.0,0.86+Math.max(0,Math.sin(ty))*0.01,-0.7); P.wL=1; P.pL=V(-0.3,-0.7,0.4); P.tR=V(0.58,0.86+Math.max(0,Math.sin(ty+2))*0.01,-0.7); P.wR=1; P.pR=V(-0.3,-0.7,-0.4);
    const rest=sstep(15.6,16.0,t)*(1-sstep(16.9,17.1,t)); if(rest>0){ P.tR=V(0.3,1.1,-0.7).lerp(P.tR,1-rest); } J=R.skel(P,V(0.1,0,-0.2),SLD.yawOf(V(0.25,0,0.97))); face={mood:Math.max(m,0.2+0.28*g),blink:blinkAt(t),fwd:J.fwd}; return {J:o(J),face,dress,phone:false}; }
  face={mood:m,blink:blinkAt(t),fwd:J.fwd}; return {J:o(J),face,dress,phone:false}; }
// ---------------------------------------------------------------- lights per scene
const LIGHTS={ bed:{key:[-1.8,2.4,1.2,0.2,0.6,-0.6,20],a:[-1.95,0.95,-1.3,0xffa24a,1.8],b:[1.7,1.7,-1.3,0xffb870,2.0],fill:[2.5,1.6,3,0x78a6ff,0.9],hemi:[0xffd9b0,0x3a2a22,0.5],bg:0x201512},
  rent:{key:[-2.5,3,2.5,-0.2,1,0,20],a:[1.6,1.6,-1.4,0xffd890,3.5],b:[-0.5,2.4,-1,0xffa860,2],fill:[2.5,1.6,3,0x78a6ff,0.8],hemi:[0xffd9b0,0x2a2a2e,0.45],bg:0x1a1614},
  bank:{key:[-1,3.2,2.5,0.2,0.8,-0.5,24],a:[0.3,2.6,-0.5,0xfff0c8,3],b:[-1.5,2.4,0.5,0xffe0a8,1.5],fill:[2.5,1.6,3,0x88b0ff,0.9],hemi:[0xe8e0d0,0x2a2a2e,0.5],bg:0x161a1c},
  market:{key:[-1.5,2.8,2.5,0.2,0.9,-0.8,22],a:[0.2,2.2,-0.6,0xffb860,3.4],b:[-1.3,2.2,-0.5,0xffb860,2.6],fill:[2.5,1.6,3,0x8070c0,0.8],hemi:[0xffc890,0x2a2230,0.45],bg:0x120d16},
  bills:{key:[-1.8,2.6,2,0,0.9,-0.6,22],a:[-0.95,1.5,-1.2,0xffb868,3],b:[0.9,1.9,-1.2,0xfff0c8,1.6],fill:[2.5,1.6,3,0x78a6ff,0.9],hemi:[0xffd9b0,0x3a2a22,0.5],bg:0x1a1210},
  food:{key:[-1.5,2.8,2.2,0.1,0.9,-0.5,22],a:[-0.2,2.2,-1.4,0xffb860,3.2],b:[1.2,2.2,-1.4,0xffb860,2.6],fill:[2.5,1.6,3,0x78a6ff,0.7],hemi:[0xffc890,0x3a2418,0.5],bg:0x1c1210},
  pump:{key:[0,3.0,1.8,0.2,0.8,-0.8,34],a:[-1.8,2.9,-1.3,0xfff4dc,3.2],b:[1.8,2.9,-1.3,0xfff4dc,3.2],fill:[2.5,1.6,3,0x6a90e8,0.9],hemi:[0xaab8e0,0x201a24,0.4],bg:0x0d1018},
  street:{key:[3,5,2,0,1,-2,28],a:[1,2.4,-1.4,0xffe0a0,3],b:[-1.5,2.4,-1,0xffd090,2],fill:[2.5,1.6,3,0xa0c0ff,0.8],hemi:[0xffe0b0,0x5a4a3a,0.8],bg:0xffc98a},
  office:{key:[-1,3.2,1.8,0.2,1,-1,24],a:[0.4,1.6,-1.6,0xb8d8ff,2.4],b:[0.6,3,-0.8,0xfff0c8,2],fill:[2.5,1.6,3,0x78a6ff,0.9],hemi:[0xe8e0d0,0x2a2a2e,0.5],bg:0x161a1c} };
function applyLights(id,ox,t){ const L=LIGHTS[id]; const k=L.key; ST.key.position.set(ox+k[0],k[1],k[2]); ST.key.target.position.set(ox+k[3],k[4],k[5]); ST.key.intensity=k[6]; ST.key.angle=1.15; ST.lampA.position.set(ox+L.a[0],L.a[1],L.a[2]); ST.lampA.color.setHex(L.a[3]); ST.lampA.intensity=L.a[4]; ST.lampB.position.set(ox+L.b[0],L.b[1],L.b[2]); ST.lampB.color.setHex(L.b[3]); ST.lampB.intensity=L.b[4]; ST.fill.position.set(ox+L.fill[0],L.fill[1],L.fill[2]); ST.fill.color.setHex(L.fill[3]); ST.fill.intensity=L.fill[4]*1.6; ST.fill.position.set(ox+0.8,1.8,4.2); ST.hemi.color.setHex(L.hemi[0]); ST.hemi.groundColor.setHex(L.hemi[1]); ST.hemi.intensity=L.hemi[2]; scene.background.setHex(L.bg); scene.fog.color.setHex(L.bg); }
// ---------------------------------------------------------------- cameras (set-local pos, look at start and end of each scene)
const CAMS={ bed1:[[0.55,1.2,3.3],[-0.45,0.95,-0.9],[0.55,1.25,3.2],[-0.3,1.0,-0.7]], rent:[[-0.1,1.45,4.0],[-0.15,1.15,0.1],[-0.15,1.45,3.6],[-0.15,1.15,0.1]], bank:[[-0.1,1.5,4.2],[-0.15,1.2,-0.3],[-0.1,1.45,3.8],[-0.15,1.2,-0.3]], market:[[-0.05,1.45,4.2],[-0.1,1.15,-0.4],[-0.05,1.45,3.8],[-0.1,1.15,-0.4]],
  bills:[[0.05,1.4,3.6],[-0.1,1.05,-0.4],[0.05,1.35,3.2],[-0.1,1.05,-0.4]], food:[[0.1,1.35,3.6],[0.0,1.0,-0.4],[0.1,1.3,3.2],[0.0,1.0,-0.4]], pump:[[0.0,1.45,4.2],[-0.05,1.1,-0.2],[0.0,1.45,3.8],[-0.05,1.1,-0.2]], bed2:[[0.8,1.35,3.9],[0.3,0.95,-0.3],[0.7,1.3,3.5],[0.35,0.95,-0.2]],
  street:[[0.0,1.5,5.0],[0.0,1.1,-1.0],[0.0,1.45,4.0],[0.0,1.1,-1.0]], office:[[0.35,1.45,3.8],[0.2,1.15,-0.8],[0.3,1.4,3.4],[0.2,1.15,-0.8]], bed3:[[0.55,1.25,3.2],[-0.3,1.0,-0.7],[0.55,1.2,3.3],[-0.45,0.95,-0.9]] };
// ---------------------------------------------------------------- the money: cash notes fly from his hand to the counterpart
function payNotes(t){ let used=0; ITEMS.forEach((it,i)=>{ const u=(t-it.t)/0.5; if(u>0&&u<1){ for(let k=0;k<4;k++){ const n=notes[used++]; const uu=clamp(u*1.0-k*0.07); if(uu<=0||uu>=1){ n.position.set(0,-9,0); continue; } const sc=sceneAt(t); const ox=sets[sc.set].userData.ox; const a=V(-0.4,1.05,0.4), b=[V(0.3,1.1,0.2),V(0.5,1.2,-0.7),V(0.6,1.1,-1.6),V(0.4,0.9,-0.9),V(0.2,0.9,-0.5),V(1.2,0.9,-0.9)][i]; tmp.copy(a).lerp(b,uu*uu*(3-2*uu)); tmp.y+=0.3*Math.sin(Math.PI*uu); n.position.set(ox+tmp.x,tmp.y,tmp.z); n.rotation.set(uu*6,uu*5,0); } } }); for(let k=used;k<notes.length;k++) notes[k].position.set(0,-9,0); }
// ---------------------------------------------------------------- one frame
function setT(t){ const sc=sceneAt(t); const ox=sets[sc.set].userData.ox; order.forEach(k=>{ sets[k].visible=(k===sc.set); });
  applyLights(sc.set,ox,t);
  const hp=heroPose(t,sc); hero.setVisible(true); hero.pose(hp.J,hp.face,hp.dress);
  extras.forEach(e=>{ const on=e.setId===sc.set; e.f.setVisible(on); if(!on) return; const sit=e.pose.sit; const P={...R.P0,...e.pose}; delete P.sit; P.p=(P.p||0)+idle(t,e.seed); const root=e.root.clone().add(V(ox,sit?0:0,0)); const J=R.skel(P,root,e.yaw); J.fwd=J.fwd||V(1,0,0); e.f.pose(J,{mood:e.mood,blink:blinkAt(t+e.seed),fwd:J.fwd},{tie:e.setId==='bank'||e.setId==='office'?1:0,collar:1,belt:1}); });
  phone.visible=!!hp.phone; if(hp.phone){ phone.position.copy(hp.phonePos); phone.quaternion.setFromUnitVectors(V(0,0,1),hp.phoneN); const lit=sc.id==='bed1'?(t<TL.rise[0]?1:0):sstep(TL.notify[0],TL.notify[0]+0.12,t); phoneLight.position.copy(hp.phonePos).add(V(0.0,0.2,0.1)); phoneLight.intensity=0.3*lit; } else phoneLight.intensity=0;
  wallet.visible=!!hp.wallet; if(hp.wallet){ wallet.position.copy(hp.wallet.pos); wallet.rotation.set(Math.PI/2*0.9,0,Math.PI*hp.wallet.flip); const op=0.9*sstep(8.6,8.9,t); panL.rotation.z=-op*0.4; panR.rotation.z=op*0.4; }
  payNotes(t);
  let cm=CAMS[sc.id]; let u=sm5(clamp((t-sc.t0)/(sc.t1-sc.t0)));
  if(sc.id==='bed1'){ cm=[CAMS.bed1[0],CAMS.bed1[1],[0.45,1.45,3.7],[0.4,1.05,0.2]]; u=sm5(clamp((t-1.35)/0.85)); }   // frame the bed, then follow him up and into his dance
  const pos=V(...cm[0]).lerp(V(...cm[2]),u), look=V(...cm[1]).lerp(V(...cm[3]),u);
  ST.cam.position.set(ox+pos.x,pos.y,pos.z); ST.cam.lookAt(ox+look.x,look.y,look.z);
  // transitions: a short warm flash at every cut
  let fl=0; SCENES.forEach(s=>{ if(s.t0>0.1) fl=Math.max(fl,0.45*Math.max(0,1-Math.abs(t-s.t0)/0.09)); }); ST.grade.uniforms.uFlash.value=fl; ST.grade.uniforms.uT.value=t;
  // office: the day passes through the window (sun to dusk), the coffee goes, the clock hand spins
  if(sc.set==='office'){ const o=sets.office; const dd=sstep(14.0,18.0,t); o.userData.sky.color.setRGB(lerp(1.0,0.35,dd),lerp(0.85,0.2,dd),lerp(0.62,0.35,dd)); o.userData.coffee.position.y=0.03-0.036*sstep(14.5,17.5,t); o.userData.clockHand.rotation.z=-t*6; const cal=o.userData.cal; const x=Math.floor(7+23*Math.min(1,Math.pow((t-14.0)/3.4,1.6))); if(cal.userData.x!==x){ cal.userData.x=x; cal.material.map.dispose(); cal.material.map=SETS.calendarTex(0,x,'JANUARY'); cal.material.needsUpdate=true; } }
  if(sc.set==='bed'){ const b=sets.bed; const x=sc.id==='bed2'?6:5; b.userData.note.visible=(sc.id==='bed3'||sc.id==='bed1'); }
}
window.renderAt=(t,K=3)=>{ const fast=t>11.9&&t<14.1; return ST.renderAt(setT,t,fast?5:K,{t0:0,t1:DUR,shutter:fast?1/36:1/60}); };
window.events={...TL}; window.ready=true;
