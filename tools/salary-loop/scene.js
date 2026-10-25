// The Salary Loop (Slow Light Dark). One continuous world, 20 s, loops by a match cut on the phone.
//   0-2   the phone buzzes: SALARY CREDITED +50,000. The camera pulls back from its screen to a tired stickman at his desk; gold coins pour into the red wallet.
//   2-7   six bills (RENT, EMI, GROCERIES, ELECTRICITY/WATER/WI-FI, FOOD, FUEL) arrive as giant objects and pull coins out of the wallet, faster and faster.
//   7-10  silence, teal cold. He opens the empty wallet, one dust mote floats out, the camera pulls back to a huge calendar (TODAY: 6th), the alarm rings.
//   10-16 the grind: he walks on a treadmill (the world scrolls past), the city goes morning to night, he works, the coffee empties, the days race 6 -> 30.
//   16-20 corridor, a golden light, 1ST OF NEXT MONTH, his posture straightens, the phone buzzes in his hand, the camera rushes into its screen = frame 0.
// renderAt(t) is pure. Units are metres, floor y = 0, camera on +z, the hero faces +x. The single gold lamp is the sun.
import * as THREE from 'three';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';
import * as SLD from './sld.js';
const {V,sstep,lerp,clamp,PAL,sm5,rotY,keys}=SLD;
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960;
const TL=await (await fetch('timeline.json')).json(); const DUR=TL.duration, ITEMS=TL.items;
const S=SLD.createStage({W,H}); const R=SLD.createRig(S.scene); const scene=S.scene;
const eo=u=>1-Math.pow(1-clamp(u),3), eb=u=>{ const c=1.4; u=clamp(u); return 1+(c+1)*Math.pow(u-1,3)+c*Math.pow(u-1,2); };   // ease out, ease out with overshoot
const hero=R.makeFig(PAL.CREAM,'hero',{rim:0.16,lift:0.05});
const FONT="'DejaVu Sans Mono', 'Liberation Mono', monospace";

// ---------------------------------------------------------------- shared materials / textures
const WOOD=new THREE.MeshStandardMaterial({color:0x4b3b2d,roughness:0.5,metalness:0,map:SLD.noiseTex(256,31,128,60,60,0.12)});
const IRON=SLD.IRON();
const fades=[];                                          // materials that fade with the giant objects
function dark(key,col=0x2a2e36,rim=0.55,map=null,emis=0){ const m=SLD.rimify(new THREE.MeshStandardMaterial({color:col,roughness:0.7,metalness:0.1,map,emissive:map?0xffffff:0x000000,emissiveMap:map,emissiveIntensity:emis,transparent:true}),0x9fb2d6,rim,key); fades.push(m); return m; }
function winTex(seed,lit=0.28,cols=6,rows=12){ const c=document.createElement('canvas'); c.width=128; c.height=256; const g=c.getContext('2d'); g.fillStyle='#14161b'; g.fillRect(0,0,128,256); const Rn=SLD.rng(seed);
  for(let r=0;r<rows;r++) for(let k=0;k<cols;k++){ g.fillStyle=Rn()<lit?'#d9d3c1':'#1c2027'; g.fillRect(8+k*(112/cols),10+r*(236/rows),(112/cols)-8,(236/rows)-10); }
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; t.wrapS=t.wrapT=THREE.RepeatWrapping; return t; }
function screenTex(kind){ const c=document.createElement('canvas'); c.width=360; c.height=640; const g=c.getContext('2d'); g.textAlign='center'; g.textBaseline='middle';
  if(kind==='credit'){ g.fillStyle='#0d0e12'; g.fillRect(0,0,360,640); const gr=g.createRadialGradient(180,300,10,180,300,330); gr.addColorStop(0,'rgba(232,184,90,0.55)'); gr.addColorStop(1,'rgba(232,184,90,0)'); g.fillStyle=gr; g.fillRect(0,0,360,640);
    g.fillStyle='rgba(237,230,214,0.12)'; g.beginPath(); g.roundRect(26,150,308,250,22); g.fill(); g.strokeStyle='rgba(232,184,90,0.9)'; g.lineWidth=3; g.stroke();
    g.fillStyle='#e8b85a'; g.font=`bold 26px ${FONT}`; g.fillText('SALARY CREDITED',180,200); g.fillStyle='#fff3d6'; g.font=`bold 58px ${FONT}`; g.fillText('+₹50,000',180,280);
    g.fillStyle='rgba(237,230,214,0.8)'; g.font=`22px ${FONT}`; g.fillText('BALANCE  ₹50,000',180,350); g.fillStyle='rgba(237,230,214,0.5)'; g.font=`20px ${FONT}`; g.fillText('SLOW LIGHT BANK',180,40); }
  else { g.fillStyle='#0b1013'; g.fillRect(0,0,360,640); g.fillStyle='#bfe8ea'; g.font=`bold 92px ${FONT}`; g.fillText('07:00',180,250); g.font=`bold 30px ${FONT}`; g.fillText('AM',180,320);
    g.fillStyle='#8fc7cb'; g.font=`bold 36px ${FONT}`; g.fillText('OFFICE',180,420); g.fillStyle='rgba(143,199,203,0.5)'; g.font=`20px ${FONT}`; g.fillText('ALARM',180,40); }
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; t.anisotropy=4; return t; }
function calTex(){ const c=document.createElement('canvas'); c.width=512; c.height=640; const g=c.getContext('2d'); g.fillStyle='#17191e'; g.fillRect(0,0,512,640); g.strokeStyle='rgba(237,230,214,0.5)'; g.lineWidth=4; g.strokeRect(10,10,492,620);
  g.fillStyle='rgba(237,230,214,0.85)'; g.textAlign='center'; g.textBaseline='middle'; g.font=`bold 38px ${FONT}`; g.fillText('THIS MONTH',256,56);
  const cw=64, ch=76, x0=34, y0=120; for(let i=0;i<30;i++){ const x=x0+(i%7)*cw, y=y0+Math.floor(i/7)*ch; g.strokeStyle='rgba(237,230,214,0.25)'; g.lineWidth=2; g.strokeRect(x,y,cw-6,ch-8);
    g.fillStyle=i<5?'rgba(237,230,214,0.35)':'rgba(237,230,214,0.9)'; g.font=`bold 28px ${FONT}`; g.fillText(String(i+1),x+cw/2-3,y+ch/2-4); if(i<5){ g.strokeStyle='rgba(237,230,214,0.5)'; g.lineWidth=3; g.beginPath(); g.moveTo(x+6,y+6); g.lineTo(x+cw-12,y+ch-14); g.moveTo(x+cw-12,y+6); g.lineTo(x+6,y+ch-14); g.stroke(); } }
  g.strokeStyle='#ede6d6'; g.lineWidth=7; g.strokeRect(34+5*cw-4,120-4,cw+2,ch); g.fillStyle='#ede6d6'; g.font=`bold 34px ${FONT}`; g.fillText('TODAY: 6th',256,600);
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; t.anisotropy=4; return t; }
function gaugeTex(){ const c=document.createElement('canvas'); c.width=c.height=512; const g=c.getContext('2d'); g.fillStyle='#1a1d23'; g.beginPath(); g.arc(256,256,250,0,7); g.fill(); g.strokeStyle='rgba(237,230,214,0.7)'; g.lineWidth=8; g.beginPath(); g.arc(256,256,236,0,7); g.stroke();
  g.strokeStyle='rgba(237,230,214,0.8)'; g.lineWidth=6; for(let i=0;i<=8;i++){ const a=(-150+i*37.5)*Math.PI/180; g.beginPath(); g.moveTo(256+Math.cos(a)*190,256+Math.sin(a)*190); g.lineTo(256+Math.cos(a)*225,256+Math.sin(a)*225); g.stroke(); }
  g.fillStyle='#ede6d6'; g.font=`bold 70px ${FONT}`; g.textAlign='center'; g.textBaseline='middle'; g.fillText('F',400,200-30); g.fillText('E',112,200-30); g.font=`bold 44px ${FONT}`; g.fillText('FUEL',256,380);
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; return t; }

// ---------------------------------------------------------------- the three set groups: apartment, office, corridor (scroll left past the lamp)
const aptG=new THREE.Group(), offG=new THREE.Group(), corG=new THREE.Group(), floorG=new THREE.Group(); scene.add(aptG,offG,corG,floorG);
const OFFICE_X=4.2;
function desk(parent,mat){ const top=new THREE.Mesh(new RoundedBoxGeometry(1.5,0.05,0.8,4,0.012),mat); top.position.set(0.42,0.755,0.05); top.castShadow=top.receiveShadow=true; parent.add(top);
  for(const [x,z] of [[-0.25,-0.3],[1.09,-0.3],[-0.25,0.4],[1.09,0.4]]){ const l=new THREE.Mesh(new THREE.BoxGeometry(0.06,0.73,0.06),mat); l.position.set(x,0.365,z); l.castShadow=l.receiveShadow=true; parent.add(l); }
  const seat=new THREE.Mesh(new RoundedBoxGeometry(0.42,0.04,0.42,3,0.01),IRON); seat.position.set(-0.47,0.45,0); seat.castShadow=seat.receiveShadow=true; parent.add(seat);
  const back=new THREE.Mesh(new RoundedBoxGeometry(0.035,0.5,0.4,3,0.01),IRON); back.position.set(-0.7,0.72,0); back.castShadow=back.receiveShadow=true; parent.add(back);
  for(const [x,z] of [[-0.64,-0.17],[-0.3,-0.17],[-0.64,0.17],[-0.3,0.17]]){ const l=new THREE.Mesh(new THREE.CylinderGeometry(0.014,0.014,0.43,10),IRON); l.position.set(x,0.215,z); l.castShadow=true; parent.add(l); } }
desk(aptG,WOOD); desk(offG,new THREE.MeshStandardMaterial({color:0x3b3f46,roughness:0.55,metalness:0.1,map:SLD.noiseTex(256,9,128,30,40,0.1)})); offG.position.x=OFFICE_X;
// office: monitor, keyboard, coffee
const monMat=new THREE.MeshStandardMaterial({color:0x0b1013,roughness:0.4,emissive:0x8fc7cb,emissiveIntensity:0.1});
{ const mon=new THREE.Mesh(new RoundedBoxGeometry(0.62,0.38,0.03,3,0.01),monMat); mon.position.set(0.62,1.05,-0.2); mon.castShadow=true; offG.add(mon);
  const st=new THREE.Mesh(new THREE.BoxGeometry(0.04,0.2,0.04),IRON); st.position.set(0.62,0.9,-0.2); offG.add(st);
  const kb=new THREE.Mesh(new RoundedBoxGeometry(0.4,0.02,0.14,2,0.006),new THREE.MeshStandardMaterial({color:0x22262c,roughness:0.6})); kb.position.set(0.3,0.79,0.2); kb.castShadow=true; offG.add(kb); }
const cup=new THREE.Group(); const cupMat=new THREE.MeshStandardMaterial({color:0xcfc7b4,roughness:0.5}); const coffeeMat=new THREE.MeshStandardMaterial({color:0x3a2316,roughness:0.3});
{ const body=new THREE.Mesh(new THREE.CylinderGeometry(0.05,0.042,0.09,20,1,true),cupMat); body.castShadow=true; cup.add(body); const bot=new THREE.Mesh(new THREE.CylinderGeometry(0.042,0.042,0.004,20),cupMat); bot.position.y=-0.045; cup.add(bot);
  const cof=new THREE.Mesh(new THREE.CylinderGeometry(0.047,0.043,0.08,20),coffeeMat); cof.name='coffee'; cup.add(cof); const hnd=new THREE.Mesh(new THREE.TorusGeometry(0.03,0.007,8,14,Math.PI),cupMat); hnd.rotation.z=-Math.PI/2; hnd.position.x=0.055; cup.add(hnd); }
scene.add(cup);
// corridor: columns and ceiling strips (teal-white), a golden light at the far end
const stripMat=new THREE.MeshStandardMaterial({color:0x10151a,emissive:0x9fd3d8,emissiveIntensity:0.9}); const colMat=dark('col',0x20242b,0.5);
for(let i=0;i<8;i++){ const x=6.0+i*1.25; const c1=new THREE.Mesh(new THREE.BoxGeometry(0.22,3.2,0.22),colMat); c1.position.set(x,1.6,-0.95); corG.add(c1);
  const s=new THREE.Mesh(new THREE.BoxGeometry(0.7,0.04,0.12),stripMat); s.position.set(x+0.6,2.9,-0.2); corG.add(s); }
const END_X=11.1;
const endMat=new THREE.MeshBasicMaterial({color:0xe0a850,transparent:true,opacity:1,fog:false}); const endLight=new THREE.Mesh(new THREE.PlaneGeometry(1.5,3.2),endMat); endLight.position.set(END_X+1.2,1.5,-0.5); corG.add(endLight);
const endGlow=SLD.glowSprite(scene,0xffd890,0.5); endGlow.scale.set(7,7,1); corG.add(endGlow); endGlow.position.set(END_X+1.0,1.5,-0.4);
const endPt=new THREE.PointLight(0xffd890,0,6,2); endPt.position.set(END_X+0.5,1.4,0); corG.add(endPt);
// floor strips: the treadmill belt
const stripF=new THREE.MeshStandardMaterial({color:0x0e1014,emissive:0xcfc9b8,emissiveIntensity:0.05,roughness:0.9}); const strips=[]; for(let i=0;i<22;i++){ const m=new THREE.Mesh(new THREE.BoxGeometry(0.05,0.004,1.9),stripF); m.position.set(0,0.003,0.1); floorG.add(m); strips.push(m); }

// ---------------------------------------------------------------- city, sky: only seen on the commute and in the office
const skyMat=new THREE.MeshBasicMaterial({color:0x07080b,fog:false}); const sky=new THREE.Mesh(new THREE.PlaneGeometry(60,30),skyMat); sky.position.set(0,6,-9); scene.add(sky);
const cityG=new THREE.Group(); scene.add(cityG); const cityMats=[]; { const Rn=SLD.rng(5); for(let i=0;i<46;i++){ const w=0.8+Rn()*1.2, h=1.4+Rn()*3.6, x=-12+i*0.9+Rn()*0.4, z=-4.2-Rn()*2.2;
  const wt=winTex(100+i,0.16); wt.repeat.set(Math.max(1,Math.round(w/0.5)),Math.max(1,Math.round(h/1.0))); const m=new THREE.MeshStandardMaterial({color:0x15181e,roughness:0.9,map:wt,emissive:0xffffff,emissiveMap:wt,emissiveIntensity:0}); cityMats.push(m);
  const b=new THREE.Mesh(new THREE.BoxGeometry(w,h,0.6),m); b.position.set(x,h/2,z); cityG.add(b); } }

// ---------------------------------------------------------------- phone
const phoneMat=new THREE.MeshStandardMaterial({color:0x090a0d,roughness:0.35,metalness:0.4}); const scrCredit=screenTex('credit'), scrAlarm=screenTex('alarm');
const scrMat=new THREE.MeshBasicMaterial({map:scrCredit,toneMapped:false,fog:false});
const phone=new THREE.Group(); { const body=new THREE.Mesh(new RoundedBoxGeometry(0.125,0.222,0.012,4,0.012),phoneMat); body.castShadow=true; phone.add(body); const sc=new THREE.Mesh(new THREE.PlaneGeometry(0.113,0.208),scrMat); sc.position.z=0.0065; phone.add(sc); }
scene.add(phone); const phoneLight=new THREE.PointLight(0xe8b85a,0,1.6,2); scene.add(phoneLight);
const PH_DESK=V(-0.02,0.9,0.3);    // stands on the desk, leaning back, screen to camera

// ---------------------------------------------------------------- wallet (two panels on a hinge) and the coins
const walMat=new THREE.MeshStandardMaterial({color:PAL.RED,roughness:0.42,metalness:0.1,emissive:PAL.RED,emissiveIntensity:0.05});
const inMat=new THREE.MeshStandardMaterial({color:0x6e1812,roughness:0.8,emissive:PAL.RED,emissiveIntensity:0.02});
const wallet=new THREE.Group(); const panL=new THREE.Group(), panR=new THREE.Group(); wallet.add(panL,panR);
{ const mk=(par,sx)=>{ const b=new THREE.Mesh(new RoundedBoxGeometry(0.3,0.03,0.36,4,0.012),walMat); b.position.x=sx*0.15; b.castShadow=b.receiveShadow=true; par.add(b); const i=new THREE.Mesh(new THREE.BoxGeometry(0.26,0.004,0.32),inMat); i.position.set(sx*0.15,0.017,0); par.add(i); };
  mk(panL,-1); mk(panR,1); }
scene.add(wallet); const halo=SLD.glowSprite(scene,0xff3a2a,0.03); halo.scale.setScalar(0.9); const redLight=new THREE.PointLight(PAL.RED,0,1.4,2); scene.add(redLight);
const WAL=V(0.30,0.7975,0.05);
const NC=50, coinGeo=new THREE.CylinderGeometry(0.034,0.034,0.0075,18); const coinMat=new THREE.MeshStandardMaterial({color:PAL.GOLD,roughness:0.3,metalness:0.7,emissive:PAL.GOLD,emissiveIntensity:0.4});
const coins=new THREE.InstancedMesh(coinGeo,coinMat,NC); coins.castShadow=true; coins.frustumCulled=false; scene.add(coins);
const coinRest=k=>V(WAL.x+0.12+((k%5)-2)*0.068,WAL.y+0.021+Math.floor(k/5)*0.0085,WAL.z);
// coin k leaves the wallet for expense number `slot`; coins leave from the top of the stacks (k = 49, 48, ...)
const coinPlan=[]; { let k=NC-1; ITEMS.forEach((it,i)=>{ for(let j=0;j<it.coins;j++){ coinPlan[k]={item:i,j}; k--; } }); }

// ---------------------------------------------------------------- the giant expenses
const giants=ITEMS.map(()=>new THREE.Group()); giants.forEach(g=>scene.add(g));
const SINK=[V(-1.15,1.2,-1.0),V(0.55,1.7,-0.1),V(0.85,0.35,0.9),V(0.2,1.0,-1.2),V(-0.85,0.45,0.85),V(0.95,1.85,-1.1)];
// 0 RENT: an apartment block
{ const wt=winTex(1,0.25,6,16); wt.repeat.set(1,1); const m=dark('rent',0x1f232a,0.6,wt,0.4); const b=new THREE.Mesh(new THREE.BoxGeometry(1.2,3.6,0.9),m); b.position.set(0,1.8,0); b.castShadow=true; giants[0].add(b);
  const roof=new THREE.Mesh(new THREE.BoxGeometry(1.3,0.12,1.0),dark('rentroof',0x2a2e36)); roof.position.set(0,3.65,0); giants[0].add(roof); giants[0].position.set(-1.35,0,-1.0); }
// 1 EMI: a car silhouette hanging over the desk
{ const m=dark('car',0x23272e,0.7); const body=new THREE.Mesh(new RoundedBoxGeometry(1.6,0.38,0.75,3,0.08),m); body.position.y=0; const cab=new THREE.Mesh(new RoundedBoxGeometry(0.85,0.34,0.66,3,0.1),m); cab.position.set(-0.05,0.32,0);
  giants[1].add(body,cab); for(const [x,z] of [[-0.5,0.34],[0.5,0.34],[-0.5,-0.34],[0.5,-0.34]]){ const w=new THREE.Mesh(new THREE.CylinderGeometry(0.19,0.19,0.14,22),dark('wheel'+x+z,0x14161a,0.4)); w.rotation.x=Math.PI/2; w.position.set(x,-0.17,z); giants[1].add(w); }
  giants[1].children.forEach(c=>c.castShadow=true); giants[1].position.set(0.45,2.7,-0.05); giants[1].rotation.z=0.06; }
// 2 GROCERIES: bags piling up
{ const m=dark('bag',0x30343c,0.6); const Rn=SLD.rng(11); for(let i=0;i<8;i++){ const b=new THREE.Mesh(new THREE.BoxGeometry(0.3+Rn()*0.08,0.4+Rn()*0.1,0.2),m); b.position.set((i%4)*0.26-0.38+Rn()*0.06,0.2+Math.floor(i/4)*0.4,(i%2)*0.14); b.rotation.y=(Rn()-0.5)*0.6; b.castShadow=true; b.userData.k=i; giants[2].add(b);
  const h=new THREE.Mesh(new THREE.TorusGeometry(0.07,0.01,6,12,Math.PI),m); h.position.copy(b.position).add(V(0,0.26,0)); h.rotation.y=b.rotation.y; h.userData.k=i; giants[2].add(h); } giants[2].position.set(0.9,0,0.85); }
// 3 UTILITIES: cables and pipes wrapping the room
const cables=[]; { const m=dark('cable',0x1d2026,0.8); const paths=[[[-1.8,0.1,-1.3],[-1.2,1.4,-1.1],[-0.4,2.0,-0.7],[0.5,1.6,-0.9],[1.3,0.9,-0.3],[1.1,0.1,0.5]],[[1.9,0.15,-1.2],[1.0,1.9,-1.0],[0.0,2.3,-0.4],[-0.9,1.7,-0.2],[-1.0,0.9,0.4],[-0.6,0.05,0.9]],[[-1.5,2.5,-1.0],[-0.5,1.2,-1.3],[0.6,0.5,-1.2],[1.4,0.25,-0.5],[1.2,0.05,0.4]]];
  paths.forEach((p,i)=>{ const geo=new THREE.TubeGeometry(new THREE.CatmullRomCurve3(p.map(a=>V(...a))),90,i===2?0.05:0.03,8); const me=new THREE.Mesh(geo,m); me.castShadow=true; me.frustumCulled=false; giants[3].add(me); cables.push({geo,total:geo.index.count}); }); }
// 4 FOOD: a tower of plates
{ const m=dark('plate',0x2e323a,0.65); for(let i=0;i<10;i++){ const p=new THREE.Mesh(new THREE.CylinderGeometry(0.27,0.2,0.05,28),m); p.position.set(0.012*Math.sin(i*2.3),0.03+i*0.055,0.01*Math.cos(i*1.7)); p.castShadow=true; p.userData.k=i; giants[4].add(p); } giants[4].position.set(-0.85,0,0.85); }
// 5 FUEL: a gauge that drains
const needle=new THREE.Mesh(new THREE.BoxGeometry(0.02,0.3,0.012),new THREE.MeshStandardMaterial({color:0xede6d6,emissive:0xede6d6,emissiveIntensity:0.35,transparent:true})); fades.push(needle.material);
{ const gm=new THREE.MeshStandardMaterial({map:gaugeTex(),emissive:0xffffff,emissiveMap:gaugeTex(),emissiveIntensity:0.45,transparent:true,roughness:0.6}); fades.push(gm); const disc=new THREE.Mesh(new THREE.CircleGeometry(0.62,48),gm); giants[5].add(disc);
  const pv=new THREE.Group(); needle.position.y=0.16; pv.add(needle); pv.position.z=0.01; pv.name='pv'; giants[5].add(pv); giants[5].position.set(1.0,1.95,-1.05); }

// ---------------------------------------------------------------- calendar (the big reveal) and extra lights
const calMat=new THREE.MeshStandardMaterial({map:calTex(),emissive:0xffffff,emissiveMap:calTex(),emissiveIntensity:0.5,roughness:0.8,transparent:true,opacity:0}); const cal=new THREE.Mesh(new THREE.PlaneGeometry(2.5,3.1),calMat); cal.position.set(0.15,1.9,-1.55); scene.add(cal);
const teal=new THREE.DirectionalLight(0x4fa3a8,0); teal.position.set(-2,3,3); teal.target.position.set(0,0.8,0); scene.add(teal,teal.target);
const dust=SLD.glowSprite(scene,0xffffff,0); dust.scale.setScalar(0.05);

// ---------------------------------------------------------------- scroll, light, coins, giants
const scrollAt=t=>SLD.keys(TL.scroll,t);
const lightAt=t=>SLD.keys(TL.light,t);
const nightAt=t=>SLD.keys(TL.night,t);
const itemT=i=>ITEMS[i].t;
function applyGiants(t){ // each giant object arrives with its bill, then dissolves while the wallet opens and the calendar appears
  const out=1-sstep(8.3,9.2,t); fades.forEach(m=>{ m.opacity=1; });
  giants.forEach((g,i)=>{ const t0=itemT(i)-0.05, u=clamp((t-t0)/0.55); g.visible=t>=t0&&out>0.01; const e=eb(u);
    if(i===0){ g.position.y=lerp(-3.8,0,e); }
    if(i===1){ g.position.y=lerp(4.2,2.0+0.02*Math.sin(t*2),clamp(e)); }
    if(i===2){ g.children.forEach(c=>{ const k=c.userData.k; const a=sstep(t0+k*0.06,t0+k*0.06+0.18,t); c.visible=a>0.01; c.scale.setScalar(Math.max(a,0.001)); }); }
    if(i===3){ cables.forEach((c,j)=>{ const p=clamp((t-t0-j*0.08)/0.6); c.geo.setDrawRange(0,Math.floor(p*c.total/6)*6); }); }
    if(i===4){ g.children.forEach(c=>{ const k=c.userData.k; const a=sstep(t0+k*0.035,t0+k*0.035+0.12,t); c.visible=a>0.01; c.position.y=lerp(c.position.y,0.03+k*0.055,1); c.scale.setScalar(Math.max(a,0.001)); }); }
    if(i===5){ const pv=g.getObjectByName('pv'); pv.rotation.z=lerp(-1.1,1.1,sm5(clamp((t-t0-0.1)/0.7))); }
  });
  fades.forEach(m=>{ m.opacity=out; }); cal.visible=true; }
function coinState(k,t){ // returns {pos, vis, rot}
  const land=1.0+k*0.02, fl=0.45; const rest=coinRest(k); const plan=coinPlan[k];
  if(t<land-fl) return null;
  if(t<land){ const u=(t-(land-fl))/fl, e=eo(u); const from=PH_DESK.clone().add(V(0,0.05,0.05)); const p=from.lerp(rest,e); p.y+=0.3*Math.sin(Math.PI*e)*(1-0.4*e); return {p,r:u*9}; }
  const t0=itemT(plan.item)+plan.j*0.014, f=TL.coinFlight;
  if(t<t0) return {p:rest,r:0};
  if(t<t0+f){ const u=(t-t0)/f, e=u*u*(3-2*u); const p=rest.clone().lerp(SINK[plan.item].clone().add(giants[plan.item].userData.base||V(0,0,0)),e); p.y+=0.45*Math.sin(Math.PI*u); return {p,r:u*12,s:1-0.5*sstep(0.7,1,u)}; }
  return null; }
const dm=new THREE.Object3D();

// ---------------------------------------------------------------- hero
const SEAT_ROOT=V(-0.225,0,0), WALK_ROOT=V(-0.2,0,0.4);
const PK=V(-0.44,0.60,0.16);
const REST_L=V(0.02,0.805,0.26), REST_R=V(0.0,0.805,-0.2);
const slumpAt=t=>{ if(t<1.0) return 0.85; if(t<2.0) return lerp(0.85,0.05,sm5((t-1.0)/1.0)); let s=0.05; ITEMS.forEach(it=>{ s+=(0.95/ITEMS.length)*sstep(it.t,it.t+0.5,t); }); if(t>TL.work0) s=lerp(s,1.0,sstep(TL.work0,TL.work1,t)); if(t>TL.corridor0) s*=1-0.0; return Math.min(1.15,s); };
function walletHeld(t){ return sstep(TL.walletOpen-0.3,TL.walletOpen,t)*(1-sstep(TL.alarm-0.2,TL.alarm+0.1,t)); }
function seatPose(t){
  const sl=slumpAt(t); const rise=sstep(1.0,1.6,t)*(1-sstep(2.2,2.8,t)); let flinch=0; ITEMS.forEach(it=>{ const d=t-it.t; if(d>0&&d<0.45) flinch+=0.07*Math.sin(Math.PI*d/0.45)*Math.exp(-d*3); });
  const breathe=0.012*Math.sin(2*Math.PI*0.21*t); const hw=walletHeld(t);
  const P={...R.P0,aL:1.5,aR:1.5,kL:1.5,kR:1.5,sL:0.4,sR:0.4,eL:0.9,eR:0.9,p:0.04+0.42*sl-0.05*rise+breathe+flinch,tilt:-0.04+0.5*sl-0.2*rise+flinch*0.6+0.25*hw,hy:-0.05*Math.sin(t*0.4)};
  let tL=REST_L.clone(), tR=REST_R.clone(); const heldL=V(0.1,0.93,0.3), heldR=V(0.3,0.93,0.3); tL.lerp(heldL,hw); tR.lerp(heldR,hw);
  if(t>=TL.work0&&t<TL.work1+0.2){ const ty=t*14; const kl=V(0.12,0.815+Math.max(0,Math.sin(ty))*0.012,0.2), kr=V(0.34,0.815+Math.max(0,Math.sin(ty+2.3))*0.012,0.2); const w=sstep(TL.work0,TL.work0+0.3,t)*(1-sstep(TL.work1-0.1,TL.work1+0.2,t)); tL.lerp(kl,w); tR.lerp(kr,w);
    const sip=sstep(13.6,13.95,t)*(1-sstep(14.5,14.85,t)); if(sip>0) tR.lerp(V(0.02,1.18,0.2),sip); }
  if(t>=TL.credit[0]&&t<2.4){ const j=sstep(1.5,1.7,t)*(1-sstep(2.0,2.4,t)); tL.lerp(V(-0.02,0.9,0.36),0.0); }
  if(t>=TL.alarm&&t<TL.grind0){ const g=sstep(TL.alarm,TL.alarm+0.3,t); tL.lerp(PH_DESK.clone().add(V(-0.06,-0.06,0.04)),g*0.9); }
  P.tL=tL; P.wL=1; P.pL=V(-0.3,-0.75,0.35); P.tR=tR; P.wR=1; P.pR=V(-0.3,-0.75,-0.35); return P; }
function walkPose(t,amp,hope){ const sc=scrollAt(t); const ph=sc/1.3*2*Math.PI; const tired=1-hope;
  const base={...R.P0,p:0.06+0.3*tired,tilt:0.04+0.34*tired-0.1*hope,eL:0.5,eR:0.5}; return R.gait(base,ph,amp,0.34,0.62,0.18+0.12*hope); }
function heroState(t){ // returns {P, root, yaw, vis, walk, ph}
  const seatP=seatPose(t); const sc=scrollAt(t);
  const standU=sm5(clamp((t-TL.stand)/0.4)), sitU=sm5(clamp((t-TL.officeSit)/0.4)), standU2=sm5(clamp((t-TL.corridor0)/0.4));
  const hope=sstep(18.0,18.9,t);
  if(t<TL.stand) return {P:seatP,root:SEAT_ROOT,yaw:0,walk:0,ph:0};
  if(t<TL.officeSit){ const W_=walkPose(t,sstep(0,1,(sc>0.05)?1:0),0); const B=R.blend(seatP,W_,standU); B.p+=0.3*Math.sin(Math.PI*standU); return {P:B,root:SEAT_ROOT.clone().lerp(WALK_ROOT,standU),yaw:0,walk:standU,ph:sc/1.3*2*Math.PI}; }
  if(t<TL.corridor0){ const W_=walkPose(t,0.4*(1-sitU),0); const B=R.blend(W_,seatP,sitU); return {P:B,root:WALK_ROOT.clone().lerp(SEAT_ROOT,sitU),yaw:0,walk:1-sitU,ph:sc/1.3*2*Math.PI}; }
  const amp=1-sstep(18.9,19.1,t); const W_=walkPose(t,amp,hope);
  // the phone: his left hand digs it out of his pocket and lifts it in front of his chest
  const hand=sstep(18.7,19.05,t); const PHH=V(-0.02,1.08,0.45);
  if(hand>0){ W_.tL=PK.clone().add(V(0.0,0.05,0.0)).lerp(PHH.clone().add(V(0,-0.02,-0.05)),hand); W_.wL=hand; W_.pL=V(-0.3,-0.75,0.35); W_.tR=V(0.25,0.95,0.35); W_.wR=hand*0.5; W_.pR=V(-0.3,-0.75,-0.35); }
  const B=R.blend(seatP,W_,standU2); B.p+=0.3*Math.sin(Math.PI*standU2); return {P:B,root:SEAT_ROOT.clone().lerp(WALK_ROOT,standU2),yaw:0,walk:standU2*amp,ph:sc/1.3*2*Math.PI}; }

// ---------------------------------------------------------------- phone and wallet placement
function phoneState(t){ // position, rotation, screen kind, vibrate amount
  let pos=PH_DESK.clone(), rotX=-0.28, vis=true, kind='credit', vib=0;
  if(t<1.65) vib=1-sstep(1.2,1.65,t);
  if(t>=TL.alarm-0.1&&t<TL.grind0+0.2){ kind='alarm'; vib=sstep(TL.alarm-0.1,TL.alarm,t)*(1-sstep(TL.grind0-0.3,TL.grind0,t)); }
  if(t>=TL.grind0+0.2&&t<18.6) vis=false;
  if(t>=18.6){ const hand=sstep(18.7,19.05,t); const H_=heroState(t); const J=R.skel(H_.P,H_.root,H_.yaw); pos=J.hL.clone().add(V(0.02,0.07,0.1)); rotX=-0.1; kind='credit'; vib=sstep(18.75,18.95,t); vis=hand>0.02; if(hand>0.02) { const k=sstep(19.0,19.5,t); pos.lerp(V(-0.02,1.1,0.55),k); } }
  return {pos,rotX,vis,kind,vib}; }
function walletState(t){ // wallet on the desk until it is picked up, held open, then pocketed at the alarm
  const hw=walletHeld(t); let pos=WAL.clone(), open=0.0, vis=true, rot=V(0,0,0);
  if(hw>0){ const H_=heroState(t); const J=R.skel(H_.P,H_.root,H_.yaw); const held=V(0.2,0.93,0.34); pos=WAL.clone().lerp(held,hw); rot=V(Math.PI/2*0.9*hw,0,0); open=sstep(TL.walletOpen,TL.walletOpen+0.4,t)*1.9; }
  if(t>=TL.alarm+0.1) vis=false; if(t<1.0) vis=true;
  return {pos,open,vis,rot,hw}; }

// ---------------------------------------------------------------- camera
function phoneCam(ps){ const m=new THREE.Matrix4().makeRotationX(ps.rotX); const n=V(0,0,1).applyMatrix4(m); const pos=ps.pos.clone().addScaledVector(n,0.3); return {pos,look:ps.pos.clone()}; }
const CAM=[ // t, pos, look: free camera keys (smooth between)
 [0.9,[0.0,1.45,3.4],[0.0,1.0,0.1]],[2.0,[0.05,1.5,3.2],[0.15,1.0,0.1]],[2.4,[0.05,1.7,4.0],[0.05,1.05,0.0]],[6.5,[0.0,1.9,5.2],[0.0,1.25,0.0]],
 [7.3,[0.1,1.45,3.0],[0.1,1.0,0.3]],[8.1,[0.1,1.45,2.9],[0.1,1.0,0.3]],[9.4,[0.05,1.9,5.6],[0.05,1.5,0.0]],[10.3,[0.1,1.7,4.6],[0.15,1.2,0.0]],
 [12.0,[0.25,1.6,3.8],[0.3,1.1,0.0]],[15.3,[0.28,1.55,3.5],[0.34,1.1,0.0]],[16.2,[0.1,1.5,4.5],[0.4,1.1,0.0]],[18.8,[0.1,1.45,3.7],[0.4,1.15,0.0]],[20,[0.1,1.45,3.7],[0.4,1.15,0.0]]];
function freeCam(t){ if(t<=CAM[0][0]) return {pos:V(...CAM[0][1]),look:V(...CAM[0][2])}; for(let i=1;i<CAM.length;i++) if(t<=CAM[i][0]){ const u=sm5((t-CAM[i-1][0])/(CAM[i][0]-CAM[i-1][0])); return {pos:V(...CAM[i-1][1]).lerp(V(...CAM[i][1]),u),look:V(...CAM[i-1][2]).lerp(V(...CAM[i][2]),u)}; } const l=CAM[CAM.length-1]; return {pos:V(...l[1]),look:V(...l[2])}; }
function camAt(t,ps){ const f=freeCam(t); const close=(t<0.95)?1:(t<2.0?1-sm5((t-0.95)/1.05):(t>=18.9?sm5(clamp((t-18.9)/1.05)):0)); if(close<=0) return f;
  const pc=phoneCam(ps); return {pos:f.pos.clone().lerp(pc.pos,close),look:f.look.clone().lerp(pc.look,close)}; }

// ---------------------------------------------------------------- one frame
function setT(t){
  const sc=scrollAt(t);
  aptG.position.x=-sc; offG.position.x=OFFICE_X-sc; corG.position.x=-sc; cityG.position.x=-sc*0.3; floorG.visible=true;
  strips.forEach((m,i)=>{ let x=((i*0.9-sc)%19.8+19.8)%19.8-8; m.position.x=x; });
  aptG.visible=sc<4.5; offG.visible=sc>0.5&&sc<9.5; corG.visible=sc>3.5;
  // hero
  const H_=heroState(t); R.poseFig(hero,R.skel(H_.P,H_.root,H_.yaw));
  // phone
  const ps=phoneState(t); phone.visible=ps.vis; scrMat.map=ps.kind==='credit'?scrCredit:scrAlarm; phone.position.copy(ps.pos); phone.rotation.set(ps.rotX,0,0);
  if(ps.vib>0){ const j=Math.sin(t*2*Math.PI*40); phone.position.x+=0.0022*j*ps.vib; phone.position.y+=0.0015*Math.cos(t*2*Math.PI*37)*ps.vib; phone.rotation.z=0.015*j*ps.vib; }
  phoneLight.position.copy(ps.pos).add(V(0,0.12,0.3)); phoneLight.color.set(ps.kind==='credit'?0xe8b85a:0x8fc7cb); phoneLight.intensity=ps.vis?(0.5+0.25*Math.sin(t*30)*ps.vib):0;
  // wallet + coins
  const ws=walletState(t); wallet.visible=ws.vis; wallet.position.copy(ws.pos); wallet.rotation.set(ws.rot.x,0,0); panL.rotation.z=-(ws.open>0?ws.open*0.5:0); panR.rotation.z=(ws.open>0?ws.open*0.5:0);
  const empty=sstep(TL.zero,TL.zero+0.3,t); const warn=empty*(1-sstep(TL.alarm,TL.alarm+0.3,t))*(0.5+0.5*Math.sin(t*7));
  const credit=sstep(1.0,2.0,t)*(1-sstep(2.4,3.2,t));
  walMat.emissiveIntensity=0.05+0.12*credit+0.45*warn; halo.position.copy(wallet.position).add(V(0,0.05,0)); halo.material.opacity=(0.03+0.1*credit+0.35*warn)*(ws.vis?1:0); redLight.position.copy(wallet.position).add(V(0,0.3,0.2)); redLight.intensity=0.35*credit+0.9*warn;
  const hide=!aptG.visible||ws.hw>0.5; const wl=sc>0?0:1; if(sc>0.05&&ws.hw<=0) wallet.visible=false;
  giants.forEach((g,i)=>{ g.userData.base=V(0,0,0); }); applyGiants(t);
  for(let k=0;k<NC;k++){ const c=coinState(k,t); if(!c||ws.hw>0.1||sc>0.05){ dm.position.set(0,-9,0); dm.scale.setScalar(0.0001); } else { dm.position.copy(c.p); dm.rotation.set(c.r,c.r*0.7,0); dm.scale.setScalar(c.s||1); } dm.updateMatrix(); coins.setMatrixAt(k,dm.matrix); } coins.instanceMatrix.needsUpdate=true;
  // calendar reveal, dust mote, coffee
  calMat.opacity=sstep(TL.pullBack0,TL.pullBack1,t)*(1-sstep(10.0,10.5,t)); cal.visible=calMat.opacity>0.01; cal.position.x=0.15-sc;
  const du=clamp((t-TL.dust)/1.2); dust.material.opacity=du>0&&du<1?0.9*Math.sin(Math.PI*du):0; dust.position.set(0.06+0.05*Math.sin(du*5),1.0+0.55*du,0.38);
  cup.visible=offG.visible; const sip=sstep(13.6,13.95,t)*(1-sstep(14.5,14.85,t)); const J=R.skel(H_.P,H_.root,H_.yaw);
  cup.position.copy(V(0.05+OFFICE_X-sc,0.84,0.2)); if(sip>0.01) cup.position.copy(J.hR).add(V(0.02,0.0,0.0)); cup.rotation.z=-0.5*sip;
  cup.getObjectByName('coffee').scale.y=Math.max(0.04,1-0.96*sstep(12.6,15.2,t)); cup.getObjectByName('coffee').position.y=-0.04+0.04*cup.getObjectByName('coffee').scale.y;
  // city + sky
  const night=nightAt(t); const cityOn=sstep(9.9,10.6,t)*(1-sstep(15.4,16.4,t)); cityG.visible=cityOn>0.01; cityMats.forEach(m=>{ m.emissiveIntensity=night*0.5*cityOn; });
  const dayC=new THREE.Color(0x07080b).lerp(new THREE.Color(0x35404c),Math.sin(Math.PI*clamp((t-10)/4.8))*(1-night)*cityOn*0.9).lerp(new THREE.Color(0x3a2418),sstep(13.6,14.5,t)*(1-sstep(14.5,15.4,t))*0.8*cityOn); skyMat.color.copy(dayC); sky.visible=cityOn>0.01;
  // corridor light
  const arrive=sstep(15.8,18.9,t); endMat.opacity=0.3+0.5*arrive; endGlow.material.opacity=0.08+0.3*arrive; endPt.intensity=1.6*arrive;
  // lights: the lamp is the sun; teal cold at zero
  const Lk=lightAt(t)*(1+0.14*credit); S.spot.intensity=S.SPOT_I*Lk; S.beamU.uI.value=Lk; S.moteU.uOp.value=Lk;
  teal.intensity=0.5*sstep(TL.zero,TL.zero+0.6,t)*(1-sstep(TL.grind0,TL.grind0+0.6,t))+0.28*night;
  // camera
  const c=camAt(t,ps); let shake=0; ITEMS.forEach(it=>{ const d=t-it.t-0.1; if(d>0&&d<0.35) shake+=0.012*Math.exp(-d*9)*Math.sin(d*60); });
  S.cam.position.copy(c.pos).add(V(shake,shake*0.7,0)); S.cam.lookAt(c.look); S.tick(t); }
window.renderAt=(t,K=3)=>{ const fast=(t>TL.stand-0.3&&t<TL.officeSit+0.2)||(t>TL.corridor0-0.2&&t<TL.stop+0.5)||t>18.9||t<2.0; return S.renderAt(setT,t,fast?5:K,{t0:0,t1:DUR,shutter:fast?1/36:1/60}); };
window.events={...TL,steps:(()=>{ const out=[]; const N=Math.round(DUR*TL.fps); let prev=null; for(let f=0;f<N;f++){ const t=f/TL.fps; const h=heroState(t); if(h.walk<0.5){ prev=null; continue; } if(prev!==null&&Math.floor(h.ph/Math.PI)>Math.floor(prev/Math.PI)) out.push({t}); prev=h.ph; } return out; })()};
window.ready=true;
