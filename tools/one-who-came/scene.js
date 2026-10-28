// 30 People Said "I'm Here For You." One Came. (28 Oct 2026) Look stills on the approved Salary dark-warm kit:
// the same bedroom set, figure, stage and grade (tools/salary-loop-dark), with the wardrobe turned into a door.
// He sits on the floor against the bed, phone lit beside him. Thirty "here for you" messages, nobody comes; a knock;
// a friend walks in, sits down, turns the phone face down; his head drops onto the friend's shoulder.
//   ?shot=hook | count | knock | facedown | payoff
import * as THREE from 'three';
import {createWarmStage,V,clamp,lerp} from './stage.js';
import * as SLD from './sld.js';
import {createFigure} from './figure.js';
import * as SETS from './sets.js';
const {M,B}=SETS;
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960; const SHOT=q.get('shot')||'hook';
const ST=createWarmStage({W,H}); const R=SLD.createRig(ST.scene); const scene=ST.scene;
const room=SETS.buildBedroom(); scene.add(room); room.userData.note.visible=false;
room.children.forEach(m=>{ if(m.isMesh&&Math.abs(m.position.y-0.04)<1e-3&&m.position.z>0.8) m.visible=false; if(m.isMesh&&Math.abs(m.position.x-2.0)<0.3&&m.position.z>-0.5&&m.position.y<1.0) m.visible=false; });   // and the chair+bag hid the door   // the pair of shoes read as clutter next to the phone

// ---------------------------------------------------------------- lights: the Salary dark-warm bedroom values
{ ST.key.position.set(-1.8,2.4,1.2); ST.key.target.position.set(0.2,0.6,-0.6); ST.key.intensity=20*0.38; ST.key.angle=1.15; ST.key.color.setHex(0xffb470);
  ST.lampA.position.set(-1.95,0.95,-1.3); ST.lampA.color.setHex(0xffae62); ST.lampA.intensity=1.8*0.95;
  ST.lampB.position.set(1.7,1.7,-1.3); ST.lampB.color.setHex(0xffb878); ST.lampB.intensity=2.0*0.6;
  ST.fill.position.set(0.8,1.8,4.2); ST.fill.color.setHex(0x5873b0); ST.fill.intensity=0.9*1.6*0.45;
  ST.hemi.color.setHex(0x3a4c78); ST.hemi.groundColor.setHex(0x241c16); ST.hemi.intensity=0.28; scene.background.setHex(0x161b25); scene.fog.color.setHex(0x161b25); }
// rain on the window: streaks over the city bokeh
{ const c=document.createElement('canvas'); c.width=256; c.height=256; const g=c.getContext('2d'); let s=7; const rn=()=>((s=(s*1664525+1013904223)>>>0)/4294967296);
  for(let i=0;i<90;i++){ const x=rn()*256, y=rn()*256, l=10+rn()*40; g.strokeStyle=`rgba(200,215,255,${0.15+rn()*0.3})`; g.lineWidth=1+rn()*1.5; g.beginPath(); g.moveTo(x,y); g.lineTo(x+2,y+l); g.stroke(); }
  for(let i=0;i<40;i++){ g.fillStyle=`rgba(220,230,255,${0.25+rn()*0.3})`; g.beginPath(); g.arc(rn()*256,rn()*256,1+rn()*2.5,0,7); g.fill(); }
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; const m=new THREE.Mesh(new THREE.PlaneGeometry(1.36,1.36),new THREE.MeshBasicMaterial({map:t,transparent:true,blending:THREE.AdditiveBlending,depthWrite:false,fog:false}));
  m.position.set(1.7,1.75,-2.11); room.add(m); }

// ---------------------------------------------------------------- people
const him=createFigure(scene,{skin:0xf2e2c6,shirt:0x8aa0bc,pants:0x56648a,headR:0.152,hair:0x2a1c14});        // at home: soft blue tee, pyjama trousers
const friend=createFigure(scene,{skin:0xd9b48a,shirt:0x7a5a3a,pants:0x2b2c33,headR:0.152,hair:0x1a120c});    // came in from the rain: brown jacket
const FACE_CAM=-Math.PI/2;                       // yaw that faces +z (the camera)
const HIM=V(0.25,0,-0.38), FRIEND_SIT=V(SHOT==='payoff'?0.66:0.8,0,-0.38);
function seated(root,o={},s=1){ const P={...R.POSES.sit,...o}; return R.handsOnKnees(P,root,FACE_CAM,s); }
function place(F,P,root,yaw,face){ const J=R.skel(P,root,yaw); F.pose(J,face,{}); return J; }
// a wet sheen on the friend: a faint cool rim on his jacket is enough at this distance

// ---------------------------------------------------------------- phone on the floor (lit, then face down)
const phone=new THREE.Group(); scene.add(phone);
const pc=document.createElement('canvas'); pc.width=300; pc.height=600; const pg=pc.getContext('2d'); const ptex=new THREE.CanvasTexture(pc); ptex.colorSpace=THREE.SRGBColorSpace;
function drawPhone(n){ pg.fillStyle='#0d1018'; pg.fillRect(0,0,300,600); pg.fillStyle='#e8e2d6'; pg.textAlign='center'; pg.font='bold 64px monospace'; pg.fillText('2:17',150,120);
  for(let i=0;i<Math.min(5,n);i++){ pg.fillStyle='rgba(235,228,214,0.92)'; pg.beginPath(); pg.roundRect(22,170+i*78,256,64,14); pg.fill(); }
  pg.fillStyle='#ff5a4a'; pg.beginPath(); pg.arc(250,175,34,0,7); pg.fill(); pg.fillStyle='#fff'; pg.font='bold 34px monospace'; pg.fillText(String(n),250,187); ptex.needsUpdate=true; }
{ B(phone,0.075,0.012,0.15,M(0x0d0e12,{r:0.3,m:0.4}),0,0.006,0,{round:0.004}); const s=new THREE.Mesh(new THREE.PlaneGeometry(0.067,0.138),new THREE.MeshBasicMaterial({map:ptex})); s.rotation.x=-Math.PI/2; s.position.y=0.0125; phone.add(s); phone.userData.screen=s; }
phone.scale.setScalar(1.6);
const phoneLight=new THREE.PointLight(0xdfe6ff,0,2.2,2); scene.add(phoneLight);
const phoneGlow=SLD.glowSprite(scene,0xcfdcff,0.0); phoneGlow.scale.setScalar(0.5);
// hallway light through the open door: a warm wedge on the floor
const hallSpot=new THREE.SpotLight(0xffb468,0,0,0.42,0.6,1.3); hallSpot.position.set(2.7,1.9,-2.6); hallSpot.target.position.set(1.4,0,0.6); hallSpot.castShadow=true; hallSpot.shadow.mapSize.set(1024,1024); scene.add(hallSpot,hallSpot.target);

// ---------------------------------------------------------------- the five moments
const SH={
  hook:    {n:1,  door:0, friend:null},
  count:   {n:30, door:0, friend:null},
  knock:   {n:30, door:1.15, friend:'door'},
  facedown:{n:30, door:1.15, friend:'sit', flip:1},
  payoff:  {n:30, door:1.15, friend:'sit', flip:1, lean:1},
}[SHOT];
function setT(t){
  // him: on the floor against the bed, head on his knees (hook/count); head up toward the door (knock); leaning on the friend (payoff)
  let P, face={mood:0.12,blink:0};
  if(SHOT==='knock'){ P=seated(HIM,{p:0.32,tilt:0.0,hy:-0.9,ty:-0.25},0.6); face={mood:0.2,wide:0.6,fwd:V(1,0,-0.6).normalize()}; }
  else if(SH.lean){ P=seated(HIM,{p:0.38,tilt:0.65,hy:-1.45,ty:-0.18},0); face={mood:0.3,blink:1}; }
  else if(SHOT==='facedown'){ P=seated(HIM,{p:0.62,tilt:0.45,hy:-0.4},1); face={mood:0.15,blink:0}; }
  else { P=seated(HIM,{p:0.78,tilt:0.62},1); face={mood:0.1,blink:1}; }
  place(him,P,HIM,FACE_CAM,face);
  // phone
  const PH=SH.flip?V(0.62,0,-0.02):V(0.78,0,-0.08); phone.position.copy(PH); phone.rotation.set(SH.flip?Math.PI:0,0.5,0); drawPhone(SH.n);
  const lit=SH.flip?0:1; phoneLight.position.copy(PH).add(V(0,0.35,0.1)); phoneLight.intensity=1.1*lit; phoneGlow.position.copy(PH).add(V(0,0.04,0)); phoneGlow.material.opacity=0.7*lit; phoneGlow.scale.setScalar(0.8);
  // door + hallway
  room.userData.door.rotation.y=SH.door; room.userData.hall.visible=SH.door>0; hallSpot.intensity=SH.door>0?26:0;
  // friend
  friend.setVisible(!!SH.friend);
  if(SH.friend==='door'){ place(friend,{...R.P0,p:0.04,sL:0.15,sR:-0.05},V(2.65,0,-1.75),Math.atan2(0.9,-0.9)-0.2,{mood:0.35}); }
  if(SH.friend==='sit'){ const PF=SH.flip&&!SH.lean?seated(FRIEND_SIT,{p:0.5,tilt:0.25,hy:0.35},0.3):seated(FRIEND_SIT,{p:0.3,tilt:0.15,hy:0.25},0.4);
    if(SHOT==='facedown'){ PF.tR=PH.clone().add(V(0.02,0.05,0)); PF.wR=1; PF.pR=V(-0.2,-0.6,-0.8); }
    if(SH.lean){ const JH=R.skel(P,HIM,FACE_CAM); Object.assign(PF,{tL:JH.shL.clone().add(V(0,0.04,0)),wL:1,pL:V(-0.3,0.4,0.8),tR:PF.tR,wR:PF.wR}); }
    place(friend,PF,FRIEND_SIT,FACE_CAM,{mood:0.4,fwd:V(-0.5,0,1).normalize()}); }
  // camera: wide on the room (hook, knock), a step closer for the count, closest on the payoff
  const look={hook:V(0.4,0.6,-0.4),count:V(0.5,0.55,-0.4),knock:V(1.6,1.0,-1.0),facedown:V(0.55,0.65,-0.5),payoff:V(0.48,0.7,-0.45)}[SHOT];
  const off={hook:[1.1,0.9,7.4],count:[0.9,0.7,5.4],knock:[0.4,1.0,10.8],facedown:[1.0,0.7,5.6],payoff:[0.6,0.45,4.4]}[SHOT];
  ST.cam.position.set(look.x+off[0],look.y+off[1],look.z+off[2]); ST.cam.lookAt(look);
  ST.grade.uniforms.uT.value=t; }
window.renderAt=(t,K)=>ST.renderAt(setT,t,K,{t0:0,t1:100});
setT(0); window.ready=true;
