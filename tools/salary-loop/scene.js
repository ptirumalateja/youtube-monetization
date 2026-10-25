// The Salary Loop v2 (Slow Light Dark). One continuous, lived-in world, 20 s, a true loop (he ends where he began: on his bed, phone in hand).
//   0-2    POV of the buzzing phone: SALARY CREDITED +50,000. The camera pulls back: he lies on his bed scrolling; gold coins pour into the red wallet.
//   2-3.4  he springs up and does a tiny dance (the lamp, the sun, brightens).
//   3.4-7  reality hits: the landlord knocks (RENT), a bike drops in (EMI), grocery bags hit the table, the fan and the meter spin, food, the fuel gauge drains.
//   7-10   balance 0: he turns the wallet upside down, nothing falls out; the calendar says the 6th; the alarm rings for work.
//   10-17  the grind: backpack and tie, treadmill walk to the bus, the bus and traffic, the office, the coffee empties, the walk home in the dark, he drops on his bed.
//   17-20  the 1st: the phone buzzes in his hand, SALARY CREDITED. A knock at the door before he can get up. The camera rushes into the phone = frame 0.
// renderAt(t) is pure. Units are metres, floor y = 0, camera on +z, the hero faces +x. The single gold lamp is the sun.
import * as THREE from 'three';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';
import * as SLD from './sld.js';
const {V,sstep,lerp,clamp,PAL,sm5}=SLD;
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960;
const TL=await (await fetch('timeline.json')).json(); const DUR=TL.duration, ITEMS=TL.items;
const LAMPX=0.3;
const S=SLD.createStage({W,H,lamp:V(LAMPX,4.6,0.05),lampTarget:V(LAMPX+0.02,0,0)}); const R=SLD.createRig(S.scene); const scene=S.scene;
const eo=u=>1-Math.pow(1-clamp(u),3), eb=u=>{ const c=1.4; u=clamp(u); return 1+(c+1)*Math.pow(u-1,3)+c*Math.pow(u-1,2); };
const hero=R.makeFig(PAL.CREAM,'hero',{rim:0.16,lift:0.05});
const FONT="'DejaVu Sans Mono', 'Liberation Mono', monospace";
const scrollAt=t=>SLD.keys(TL.scroll,t), lightAt=t=>SLD.keys(TL.light,t), nightAt=t=>SLD.keys(TL.night,t);

// ---------------------------------------------------------------- materials / textures
const WOOD=new THREE.MeshStandardMaterial({color:0x4b3b2d,roughness:0.5,metalness:0,map:SLD.noiseTex(256,31,128,60,60,0.12)});
const IRON=SLD.IRON();
const fades=[];                                          // the bills' objects fade out when the calendar appears
function dark(key,col=0x2a2e36,rim=0.55,map=null,emis=0,fade=true){ const m=SLD.rimify(new THREE.MeshStandardMaterial({color:col,roughness:0.7,metalness:0.1,map,emissive:map?0xffffff:0x000000,emissiveMap:map,emissiveIntensity:emis,transparent:true}),0x9fb2d6,rim,key); if(fade) fades.push(m); return m; }
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
  g.fillStyle='#ede6d6'; g.font=`bold 70px ${FONT}`; g.textAlign='center'; g.textBaseline='middle'; g.fillText('F',400,170); g.fillText('E',112,170); g.font=`bold 44px ${FONT}`; g.fillText('FUEL',256,380);
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; return t; }
function meterTex(){ const c=document.createElement('canvas'); c.width=256; c.height=256; const g=c.getContext('2d'); g.fillStyle='#1a1d23'; g.fillRect(0,0,256,256); g.strokeStyle='rgba(237,230,214,0.8)'; g.lineWidth=5; g.strokeRect(10,10,236,236);
  g.fillStyle='#0b0c0f'; g.fillRect(34,50,188,60); g.fillStyle='#d9d3c1'; g.font=`bold 44px ${FONT}`; g.textAlign='center'; g.textBaseline='middle'; g.fillText('0482.6',128,81); g.font=`bold 26px ${FONT}`; g.fillText('kWh',128,150); g.fillText('ELECTRIC',128,215);
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; return t; }

// ---------------------------------------------------------------- set groups: apartment (start), bus, office, street poles, apartment again (end)
const aptG=new THREE.Group(), apt2G=new THREE.Group(), busG=new THREE.Group(), offG=new THREE.Group(), stG=new THREE.Group(), floorG=new THREE.Group(); scene.add(aptG,apt2G,busG,offG,stG,floorG);
const BASE={apt:0,bus:3.0,off:7.2,apt2:11.4};
function chairAndDesk(parent,mat,{chair=true,desk=true}={}){ if(desk){ const top=new THREE.Mesh(new RoundedBoxGeometry(1.5,0.05,0.8,4,0.012),mat); top.position.set(0.42,0.755,0.05); top.castShadow=top.receiveShadow=true; parent.add(top);
  for(const [x,z] of [[-0.25,-0.3],[1.09,-0.3],[-0.25,0.4],[1.09,0.4]]){ const l=new THREE.Mesh(new THREE.BoxGeometry(0.06,0.73,0.06),mat); l.position.set(x,0.365,z); l.castShadow=l.receiveShadow=true; parent.add(l); } }
  if(!chair) return;
  const seat=new THREE.Mesh(new RoundedBoxGeometry(0.42,0.04,0.42,3,0.01),IRON); seat.position.set(-0.47,0.45,0); seat.castShadow=seat.receiveShadow=true; parent.add(seat);
  const back=new THREE.Mesh(new RoundedBoxGeometry(0.035,0.5,0.4,3,0.01),IRON); back.position.set(-0.7,0.72,0); back.castShadow=back.receiveShadow=true; parent.add(back);
  for(const [x,z] of [[-0.64,-0.17],[-0.3,-0.17],[-0.64,0.17],[-0.3,0.17]]){ const l=new THREE.Mesh(new THREE.CylinderGeometry(0.014,0.014,0.43,10),IRON); l.position.set(x,0.215,z); l.castShadow=true; parent.add(l); } }
const SHEET=new THREE.MeshStandardMaterial({color:0x4a463e,roughness:0.9}), BLANKET=new THREE.MeshStandardMaterial({color:0x3a3f4a,roughness:0.9});
function buildBed(parent){ const fr=new THREE.Mesh(new RoundedBoxGeometry(1.98,0.2,0.98,3,0.02),IRON); fr.position.set(-0.55,0.2,0.15); fr.castShadow=fr.receiveShadow=true; parent.add(fr);
  const mat=new THREE.Mesh(new RoundedBoxGeometry(1.9,0.18,0.9,4,0.05),SHEET); mat.position.set(-0.55,0.38,0.15); mat.castShadow=mat.receiveShadow=true; parent.add(mat);
  const pil=new THREE.Mesh(new RoundedBoxGeometry(0.4,0.11,0.55,4,0.04),new THREE.MeshStandardMaterial({color:0x9a958a,roughness:0.9})); pil.position.set(-1.3,0.52,0.15); pil.castShadow=true; parent.add(pil);
  const door=new THREE.Group(); const dm=new THREE.MeshStandardMaterial({color:0x2f2924,roughness:0.6,map:SLD.noiseTex(128,3,128,40,30,0.1)});
  const panel=new THREE.Mesh(new THREE.BoxGeometry(0.9,2.0,0.05),dm); panel.position.y=1.0; panel.castShadow=true; door.add(panel); const frm=new THREE.Mesh(new THREE.BoxGeometry(1.04,2.06,0.04),IRON); frm.position.set(0,1.03,-0.03); door.add(frm);
  const knob=new THREE.Mesh(new THREE.SphereGeometry(0.035,12,10),new THREE.MeshStandardMaterial({color:0x8a8f98,metalness:0.6,roughness:0.3})); knob.position.set(0.32,1.0,0.05); door.add(knob);
  const slit=new THREE.Mesh(new THREE.BoxGeometry(0.88,0.012,0.01),new THREE.MeshBasicMaterial({color:0xffe2a0,fog:false})); slit.position.set(0,0.02,0.03); door.add(slit);
  door.position.set(0.55,0,-1.1); parent.add(door); parent.userData.door=door; }
const tblG=new THREE.Group(); tblG.position.x=0.9; aptG.add(tblG); chairAndDesk(tblG,WOOD,{chair:false}); buildBed(aptG);
buildBed(apt2G); apt2G.position.x=BASE.apt2;
const fan=new THREE.Group(); { const hub=new THREE.Mesh(new THREE.CylinderGeometry(0.07,0.07,0.07,16),IRON); fan.add(hub); for(let i=0;i<4;i++){ const b=new THREE.Mesh(new THREE.BoxGeometry(0.75,0.012,0.14),IRON); b.position.x=0.4; const pv=new THREE.Group(); pv.rotation.y=i*Math.PI/2; pv.add(b); fan.add(pv); }
  const rod=new THREE.Mesh(new THREE.CylinderGeometry(0.012,0.012,0.5,8),IRON); rod.position.y=0.28; fan.add(rod); fan.position.set(LAMPX+0.55,2.1,-0.1); aptG.add(fan); }
const meterDisc=new THREE.Mesh(new THREE.CircleGeometry(0.1,24),new THREE.MeshBasicMaterial({color:0xcfc9b8})); const meterMark=new THREE.Mesh(new THREE.BoxGeometry(0.012,0.1,0.003),new THREE.MeshBasicMaterial({color:0x14161b}));
{ const box=new THREE.Mesh(new THREE.BoxGeometry(0.3,0.38,0.08),new THREE.MeshStandardMaterial({map:meterTex(),emissive:0xffffff,emissiveMap:meterTex(),emissiveIntensity:0.5,roughness:0.6})); box.position.set(1.75,1.45,-1.1); aptG.add(box);
  meterDisc.position.set(1.75,1.28,-1.05); meterDisc.scale.setScalar(0.6); aptG.add(meterDisc); meterMark.position.set(1.75,1.28,-1.045); aptG.add(meterMark); }
{ const bm=dark('bus',0x181b20,0.12,null,0,false); const fl=new THREE.Mesh(new THREE.BoxGeometry(3.2,0.06,1.3),bm); fl.position.set(0.3,0.2,0); busG.add(fl); const roof=new THREE.Mesh(new THREE.BoxGeometry(3.3,0.08,1.4),bm); roof.position.set(0.3,2.35,0); roof.castShadow=true; busG.add(roof);
  for(const [x,z] of [[-1.25,-0.6],[1.85,-0.6],[-1.25,0.6],[1.85,0.6],[0.3,-0.62]]){ const p=new THREE.Mesh(new THREE.BoxGeometry(0.06,2.15,0.06),bm); p.position.set(x,1.28,z); busG.add(p); }
  const rail=new THREE.Mesh(new THREE.CylinderGeometry(0.014,0.014,3.0,8),IRON); rail.rotation.z=Math.PI/2; rail.position.set(0.3,2.05,0.3); busG.add(rail);
  for(let i=0;i<4;i++){ const st=new THREE.Mesh(new THREE.CylinderGeometry(0.008,0.008,0.4,6),IRON); st.position.set(-0.7+i*0.7,1.85,0.3); busG.add(st); }
  const seat=new THREE.Mesh(new RoundedBoxGeometry(1.6,0.06,0.42,3,0.01),IRON); seat.position.set(-0.17,0.45,0); busG.add(seat); const bk=new THREE.Mesh(new RoundedBoxGeometry(1.6,0.4,0.04,3,0.01),IRON); bk.position.set(-0.17,0.72,-0.2); busG.add(bk);
  const head=new THREE.Mesh(new THREE.BoxGeometry(0.2,0.06,0.04),new THREE.MeshBasicMaterial({color:0xcfd8e0})); head.position.set(1.95,0.55,0.4); busG.add(head); }
const offDeskMat=new THREE.MeshStandardMaterial({color:0x3b3f46,roughness:0.55,metalness:0.1,map:SLD.noiseTex(256,9,128,30,40,0.1)}); chairAndDesk(offG,offDeskMat);
const monMat=new THREE.MeshStandardMaterial({color:0x0b1013,roughness:0.4,emissive:0x8fc7cb,emissiveIntensity:0.1});
{ const mon=new THREE.Mesh(new RoundedBoxGeometry(0.62,0.38,0.03,3,0.01),monMat); mon.position.set(0.62,1.05,-0.2); mon.castShadow=true; offG.add(mon);
  const st=new THREE.Mesh(new THREE.BoxGeometry(0.04,0.2,0.04),IRON); st.position.set(0.62,0.9,-0.2); offG.add(st);
  const kb=new THREE.Mesh(new RoundedBoxGeometry(0.4,0.02,0.14,2,0.006),new THREE.MeshStandardMaterial({color:0x22262c,roughness:0.6})); kb.position.set(0.3,0.79,0.2); kb.castShadow=true; offG.add(kb); }
const cup=new THREE.Group(); const cupMat=new THREE.MeshStandardMaterial({color:0xcfc7b4,roughness:0.5}); const coffeeMat=new THREE.MeshStandardMaterial({color:0x3a2316,roughness:0.3});
{ const body=new THREE.Mesh(new THREE.CylinderGeometry(0.05,0.042,0.09,20,1,true),cupMat); body.castShadow=true; cup.add(body); const bot=new THREE.Mesh(new THREE.CylinderGeometry(0.042,0.042,0.004,20),cupMat); bot.position.y=-0.045; cup.add(bot);
  const cof=new THREE.Mesh(new THREE.CylinderGeometry(0.047,0.043,0.08,20),coffeeMat); cof.name='coffee'; cup.add(cof); const hnd=new THREE.Mesh(new THREE.TorusGeometry(0.03,0.007,8,14,Math.PI),cupMat); hnd.rotation.z=-Math.PI/2; hnd.position.x=0.055; cup.add(hnd); }
scene.add(cup);
const poleMat=dark('pole',0x20242b,0.5,null,0,false), headMat=new THREE.MeshStandardMaterial({color:0x10151a,emissive:0x9fd3d8,emissiveIntensity:1.0});
for(let i=0;i<8;i++){ const x=BASE.off+1.8+i*1.5; const p=new THREE.Mesh(new THREE.BoxGeometry(0.08,2.8,0.08),poleMat); p.position.set(x,1.4,-0.9); stG.add(p); const hd=new THREE.Mesh(new THREE.BoxGeometry(0.4,0.05,0.14),headMat); hd.position.set(x+0.15,2.8,-0.9); stG.add(hd); }
const stripF=new THREE.MeshStandardMaterial({color:0x0e1014,emissive:0xcfc9b8,emissiveIntensity:0.05,roughness:0.9}); const strips=[]; for(let i=0;i<22;i++){ const m=new THREE.Mesh(new THREE.BoxGeometry(0.05,0.004,1.9),stripF); m.position.set(0,0.003,0.1); floorG.add(m); strips.push(m); }

// ---------------------------------------------------------------- city, sky, traffic
const skyMat=new THREE.MeshBasicMaterial({color:0x07080b,fog:false}); const sky=new THREE.Mesh(new THREE.PlaneGeometry(60,30),skyMat); sky.position.set(0,6,-9); scene.add(sky);
const cityG=new THREE.Group(); scene.add(cityG); const cityMats=[]; { const Rn=SLD.rng(5); for(let i=0;i<46;i++){ const w=0.8+Rn()*1.2, h=1.4+Rn()*3.6, x=-12+i*0.9+Rn()*0.4, z=-4.4-Rn()*2.2;
  const wt=winTex(100+i,0.16); wt.repeat.set(Math.max(1,Math.round(w/0.5)),Math.max(1,Math.round(h/1.0))); const m=new THREE.MeshStandardMaterial({color:0x15181e,roughness:0.9,map:wt,emissive:0xffffff,emissiveMap:wt,emissiveIntensity:0}); cityMats.push(m);
  const b=new THREE.Mesh(new THREE.BoxGeometry(w,h,0.6),m); b.position.set(x,h/2,z); cityG.add(b); } }
const trafficG=new THREE.Group(); scene.add(trafficG); const cars=[]; { const cm=dark('traffic',0x1b1e24,0.7,null,0,false); const hl=new THREE.MeshBasicMaterial({color:0xffe9bd,fog:false}), tl=new THREE.MeshBasicMaterial({color:0xcfd8e0,fog:false});
  for(let i=0;i<9;i++){ const g=new THREE.Group(); const b=new THREE.Mesh(new RoundedBoxGeometry(1.1,0.36,0.55,2,0.07),cm); b.position.y=0.28; const c=new THREE.Mesh(new RoundedBoxGeometry(0.6,0.3,0.5,2,0.07),cm); c.position.set(-0.05,0.56,0);
    const h1=new THREE.Mesh(new THREE.BoxGeometry(0.04,0.07,0.1),hl); h1.position.set(0.56,0.32,0.17); const h2=h1.clone(); h2.position.z=-0.17; const t1=new THREE.Mesh(new THREE.BoxGeometry(0.03,0.06,0.1),tl); t1.position.set(-0.56,0.32,0.17); const t2=t1.clone(); t2.position.z=-0.17;
    g.add(b,c,h1,h2,t1,t2); g.userData={x0:-9+i*2.4,v:(i%2?-1:1)*(2.0+0.4*(i%3))}; g.position.z=i%2?-2.8:-3.4; trafficG.add(g); cars.push(g); } }

// ---------------------------------------------------------------- phone, wallet, coins
const phoneMat=new THREE.MeshStandardMaterial({color:0x090a0d,roughness:0.35,metalness:0.4}); const scrCredit=screenTex('credit'), scrAlarm=screenTex('alarm');
const scrMat=new THREE.MeshBasicMaterial({map:scrCredit,toneMapped:false,fog:false});
const phone=new THREE.Group(); { const body=new THREE.Mesh(new RoundedBoxGeometry(0.125,0.222,0.012,4,0.012),phoneMat); body.castShadow=true; phone.add(body); const sc=new THREE.Mesh(new THREE.PlaneGeometry(0.113,0.208),scrMat); sc.position.z=0.0065; phone.add(sc); }
scene.add(phone); const phoneLight=new THREE.PointLight(0xe8b85a,0,1.6,2); scene.add(phoneLight);
const walMat=new THREE.MeshStandardMaterial({color:PAL.RED,roughness:0.42,metalness:0.1,emissive:PAL.RED,emissiveIntensity:0.05});
const inMat=new THREE.MeshStandardMaterial({color:0x6e1812,roughness:0.8,emissive:PAL.RED,emissiveIntensity:0.02});
const wallet=new THREE.Group(); const panL=new THREE.Group(), panR=new THREE.Group(); wallet.add(panL,panR);
{ const mk=(par,sx)=>{ const b=new THREE.Mesh(new RoundedBoxGeometry(0.3,0.03,0.36,4,0.012),walMat); b.position.x=sx*0.15; b.castShadow=b.receiveShadow=true; par.add(b); const i=new THREE.Mesh(new THREE.BoxGeometry(0.26,0.004,0.32),inMat); i.position.set(sx*0.15,0.017,0); par.add(i); }; mk(panL,-1); mk(panR,1); }
scene.add(wallet); const halo=SLD.glowSprite(scene,0xff3a2a,0.03); halo.scale.setScalar(0.9); const redLight=new THREE.PointLight(PAL.RED,0,1.4,2); scene.add(redLight);
const WAL=V(0.95,0.7975,0.05), WAL_HELD=V(0.8,1.05,0.8);
const NC=50, coinGeo=new THREE.CylinderGeometry(0.034,0.034,0.0075,18); const coinMat=new THREE.MeshStandardMaterial({color:PAL.GOLD,roughness:0.3,metalness:0.7,emissive:PAL.GOLD,emissiveIntensity:0.4});
const coins=new THREE.InstancedMesh(coinGeo,coinMat,NC); coins.castShadow=true; coins.frustumCulled=false; scene.add(coins);
const coinRest=k=>V(WAL.x+0.12+((k%5)-2)*0.068,WAL.y+0.021+Math.floor(k/5)*0.0085,WAL.z);
const coinPlan=[]; { let k=NC-1; ITEMS.forEach((it,i)=>{ for(let j=0;j<it.coins;j++){ coinPlan[k]={item:i,j}; k--; } }); }

// ---------------------------------------------------------------- the six bills as things in his room
const giants=ITEMS.map(()=>new THREE.Group()); giants.forEach(g=>aptG.add(g));
const SINK=[V(0.55,1.1,-1.05),V(1.15,0.7,-0.85),V(1.55,0.95,0.0),V(0.85,2.0,-0.1),V(1.95,0.5,0.75),V(2.15,1.7,-1.05)];
{ const wt=winTex(1,0.25,6,16); const m=dark('rent',0x1f232a,0.6,wt,0.35); const b=new THREE.Mesh(new THREE.BoxGeometry(1.5,4.2,0.9),m); b.position.set(0,2.1,0); b.castShadow=true; giants[0].add(b); giants[0].position.set(0.55,0,-2.0); }   // 0 RENT: the door shakes, a block looms behind it
const bikeParts=[]; { const m=dark('bike',0x23272e,0.8); const wm=dark('bikewheel',0x14161a,0.7); const tank=new THREE.Mesh(new THREE.SphereGeometry(0.22,18,14),m); tank.scale.set(1.3,0.8,0.7); tank.position.set(0.1,0.78,0); giants[1].add(tank);   // 1 EMI: a motorbike drops in
  const seat=new THREE.Mesh(new RoundedBoxGeometry(0.55,0.09,0.2,2,0.04),m); seat.position.set(-0.32,0.82,0); giants[1].add(seat); const fr=new THREE.Mesh(new THREE.BoxGeometry(0.9,0.07,0.07),m); fr.position.set(0.0,0.55,0); fr.rotation.z=0.25; giants[1].add(fr);
  const fk=new THREE.Mesh(new THREE.BoxGeometry(0.05,0.62,0.05),m); fk.position.set(0.5,0.4,0); fk.rotation.z=-0.28; giants[1].add(fk); const hb=new THREE.Mesh(new THREE.BoxGeometry(0.05,0.05,0.5),m); hb.position.set(0.42,0.9,0); giants[1].add(hb);
  const hl=new THREE.Mesh(new THREE.SphereGeometry(0.06,12,10),new THREE.MeshBasicMaterial({color:0xffe9bd,fog:false})); hl.position.set(0.58,0.82,0); giants[1].add(hl);
  for(const x of [-0.55,0.62]){ const w=new THREE.Mesh(new THREE.TorusGeometry(0.28,0.05,10,24),wm); w.position.set(x,0.3,0); giants[1].add(w); bikeParts.push(w); }
  giants[1].traverse(c=>{ if(c.isMesh) c.castShadow=true; }); giants[1].scale.setScalar(1.25); giants[1].position.set(1.15,0,-0.85); }
{ const m=dark('bag',0x30343c,0.6); const Rn=SLD.rng(11); for(let i=0;i<7;i++){ const b=new THREE.Mesh(new THREE.BoxGeometry(0.2+Rn()*0.05,0.28+Rn()*0.06,0.14),m); b.userData.k=i; b.userData.rest=V(1.3+(i%4)*0.17+Rn()*0.03,0.8+0.15+Math.floor(i/4)*0.28,-0.02+(i%2)*0.14); b.userData.yaw=(Rn()-0.5)*0.7; b.castShadow=true; giants[2].add(b);   // 2 GROCERIES: bags drop on the table
  const h=new THREE.Mesh(new THREE.TorusGeometry(0.05,0.008,6,12,Math.PI),m); h.userData.k=i; h.userData.handle=true; h.userData.rest=b.userData.rest; giants[2].add(h); } }
{ const m=new THREE.Mesh(new THREE.BoxGeometry(0.28,0.05,0.18),dark('router',0x1a1d22,0.7)); m.position.set(1.75,0.83,-0.22); giants[3].add(m); for(let i=0;i<3;i++){ const a=new THREE.Mesh(new THREE.CylinderGeometry(0.008,0.008,0.22,6),dark('ant'+i,0x23272e,0.6)); a.position.set(1.65+i*0.1,0.97,-0.22); a.rotation.z=(i-1)*0.25; giants[3].add(a); } }   // 3 UTILITIES: fan + meter spin, router
{ const m=dark('plate',0x2e323a,0.65); for(let i=0;i<10;i++){ const p=new THREE.Mesh(new THREE.CylinderGeometry(0.27,0.2,0.05,28),m); p.position.set(0.012*Math.sin(i*2.3),0.03+i*0.055,0.01*Math.cos(i*1.7)); p.castShadow=true; p.userData.k=i; giants[4].add(p); } giants[4].position.set(1.95,0,0.75); }   // 4 FOOD: plates
const needle=new THREE.Mesh(new THREE.BoxGeometry(0.02,0.3,0.012),new THREE.MeshStandardMaterial({color:0xede6d6,emissive:0xede6d6,emissiveIntensity:0.35,transparent:true})); fades.push(needle.material);
{ const gm=new THREE.MeshStandardMaterial({map:gaugeTex(),emissive:0xffffff,emissiveMap:gaugeTex(),emissiveIntensity:0.45,transparent:true,roughness:0.6}); fades.push(gm); const disc=new THREE.Mesh(new THREE.CircleGeometry(0.55,48),gm); giants[5].add(disc);
  const pv=new THREE.Group(); needle.position.y=0.14; pv.add(needle); pv.position.z=0.01; pv.name='pv'; giants[5].add(pv); giants[5].position.set(2.15,1.7,-1.05); }   // 5 FUEL: gauge drains

// ---------------------------------------------------------------- calendar, extra lights, dust, backpack, tie
const calMat=new THREE.MeshStandardMaterial({map:calTex(),emissive:0xffffff,emissiveMap:calTex(),emissiveIntensity:0.5,roughness:0.8,transparent:true,opacity:0}); const cal=new THREE.Mesh(new THREE.PlaneGeometry(2.0,2.5),calMat); cal.position.set(0.8,1.8,-1.6); scene.add(cal);
const teal=new THREE.DirectionalLight(0x4fa3a8,0); teal.position.set(-2,3,3); teal.target.position.set(0,0.8,0); scene.add(teal,teal.target);
const dust=SLD.glowSprite(scene,0xffffff,0); dust.scale.setScalar(0.05);
const bagMat=new THREE.MeshStandardMaterial({color:0x2c3139,roughness:0.8}); const pack=new THREE.Group(); { const b=new THREE.Mesh(new RoundedBoxGeometry(0.16,0.38,0.3,3,0.04),bagMat); b.castShadow=true; pack.add(b); const pk=new THREE.Mesh(new RoundedBoxGeometry(0.06,0.18,0.24,2,0.02),bagMat); pk.position.x=-0.09; pack.add(pk); } scene.add(pack);
const tie=new THREE.Mesh(new THREE.BoxGeometry(0.035,0.2,0.012),new THREE.MeshStandardMaterial({color:0x6b717c,roughness:0.6})); scene.add(tie);
const strap=new THREE.Mesh(new THREE.CylinderGeometry(1,1,1,8),new THREE.MeshStandardMaterial({color:0x2c3139,roughness:0.8})); scene.add(strap);

// ---------------------------------------------------------------- hero
const STAND_ROOT=V(0.5,0,0.55), SEAT_ROOT=V(LAMPX-0.225,0,0), LIE_HIP=V(-0.58,0.56,0.15), STAND_HIP=V(STAND_ROOT.x,0.99,STAND_ROOT.z);
const PH_LIE=V(-0.95,0.95,0.15), PH_NORMAL=V(-0.25,-0.35,0.9).normalize();
const phoneBasis=n=>{ const z=n.clone().normalize(); const x=V(0,1,0).cross(z).normalize(); const y=z.clone().cross(x); return new THREE.Matrix4().makeBasis(x,y,z); };
function xform(J,fn){ const o={}; for(const k in J) o[k]=J[k].isVector3?fn(J[k].clone()):J[k]; return o; }
const standPose=(hunch,extra={})=>({...R.P0,p:0.05+0.32*hunch,tilt:0.44*hunch,sL:0.12,sR:-0.05,...extra});
const slumpAt=t=>{ if(t<2.5) return 0; let s=0; ITEMS.forEach(it=>{ s+=(0.9/ITEMS.length)*sstep(it.t,it.t+0.5,t); }); if(t>TL.morning) s=Math.max(s,0.9); if(t>TL.officeSit) s=lerp(s,1.05,sstep(TL.officeSit,TL.work1,t)); return s; };
function lyingJoints(lie,hipFrom,phoneTarget){ const P=standPose(0,{aL:0,aR:0,kL:0,kR:0,sL:0.1,sR:0.1,eL:0.4,eR:0.4,tilt:0.45*lie,p:0});
  const J0=R.skel(P,V(0,0,0),0); const piv=J0.hip.clone(); const th=lie*Math.PI/2; const c=Math.cos(th), s=Math.sin(th); const hipPos=hipFrom.clone().lerp(LIE_HIP,lie);
  const J=xform(J0,v=>{ const d=v.sub(piv); return V(d.x*c-d.y*s+hipPos.x,d.x*s+d.y*c+hipPos.y,d.z+hipPos.z); });
  if(phoneTarget){ const tg=phoneTarget.clone().add(V(0.02,-0.03,-0.08)); const r=R.ik(J.shL,tg,V(0.1,-1,-0.5)); J.elL=r.E; J.hL=r.Hd; const r2=R.ik(J.shR,J.hip.clone().add(V(-0.12,0.1,-0.04)),V(0,-0.4,0.9)); J.elR=r2.E; J.hR=r2.Hd; }
  return J; }
function seatPoseTired(t){ const sl=Math.min(1.05,slumpAt(t)); return {...R.P0,aL:1.5,aR:1.5,kL:1.5,kR:1.5,sL:0.4,sR:0.4,eL:0.9,eR:0.9,p:0.04+0.42*sl+0.012*Math.sin(2*Math.PI*0.21*t),tilt:0.5*sl,tL:V(SEAT_ROOT.x+0.55,0.805,0.26),wL:1,pL:V(-0.3,-0.75,0.35),tR:V(SEAT_ROOT.x+0.5,0.805,-0.2),wR:1,pR:V(-0.3,-0.75,-0.35)}; }
function heroJ(t){ // {J, phone, walk, ph, sip}
  const sc=scrollAt(t); const ph=sc/1.3*2*Math.PI;
  if(t<TL.rise[0]){ const j=0.012*Math.sin(t*11)*(t>1.3&&t<1.7?1:0); const tgt=PH_LIE.clone().add(V(j,j*0.5,0)); return {J:lyingJoints(1,LIE_HIP,tgt),phone:{pos:tgt,n:PH_NORMAL},walk:0,ph:0}; }
  if(t<TL.rise[1]){ const u=sm5((t-TL.rise[0])/(TL.rise[1]-TL.rise[0])); return {J:lyingJoints(1-u,STAND_HIP,null),phone:null,walk:0,ph:0}; }
  if(t>=TL.bed0){ const lie=sm5(clamp((t-TL.bed0)/(TL.bed1-TL.bed0))); if(t<TL.bed1) return {J:lyingJoints(lie,STAND_HIP,null),phone:null,walk:0,ph:0}; return {J:lyingJoints(1,LIE_HIP,PH_LIE),phone:{pos:PH_LIE,n:PH_NORMAL},walk:0,ph:0}; }
  const hunch=Math.min(1,slumpAt(t)); let P=standPose(hunch);
  if(t<TL.dance[1]){ const d=(t-TL.dance[0])*7.5; const w=sstep(TL.dance[0],TL.dance[0]+0.2,t)*(1-sstep(TL.dance[1]-0.2,TL.dance[1]+0.1,t));
    P={...P,kL:0.5*w*Math.abs(Math.sin(d)),kR:0.5*w*Math.abs(Math.cos(d)),aL:0.25*w*Math.sin(d),aR:-0.25*w*Math.sin(d),dy:-0.04*w*Math.abs(Math.sin(d*2)),hy:0.6*w*Math.sin(d*0.5),p:0.02,tilt:-0.12*w};
    const hand=ph2=>V(STAND_ROOT.x+0.1+0.05*Math.sin(d+ph2),1.55+0.12*Math.sin(d*2+ph2),STAND_ROOT.z+0.3*(ph2?-1:1)); P.tL=hand(0); P.tR=hand(Math.PI); P.wL=w; P.wR=w; P.pL=V(-0.3,-0.2,0.9); P.pR=V(-0.3,-0.2,-0.9);
    return {J:R.skel(P,STAND_ROOT.clone().add(V(0.08*w*Math.sin(d*0.5),0,0)),0),phone:null,walk:0,ph:0}; }
  if(t<TL.morning){ let flinch=0; ITEMS.forEach(it=>{ const d=t-it.t; if(d>0&&d<0.4) flinch+=0.08*Math.sin(Math.PI*d/0.4)*Math.exp(-d*3); });
    const knock=t>=TL.knock[0]&&t<ITEMS[0].t+0.5;
    P={...P,p:P.p+flinch,tilt:P.tilt+flinch*0.6,hy:(knock?0.7:0.0)};
    const up=sstep(TL.walletUp,TL.walletUp+0.35,t)*(1-sstep(TL.alarm-0.1,TL.alarm+0.1,t)), shake=(t>TL.flip&&t<TL.dust+0.4)?0.03*Math.sin(t*34):0;
    const wp=WAL_HELD.clone().add(V(0,0.08*sstep(TL.flip-0.2,TL.flip+0.3,t),0)); const phs=sstep(TL.alarm-0.1,TL.alarm+0.2,t);
    if(up>0||phs>0){ P.tL=wp.clone().add(V(-0.1,shake,0)); P.wL=up; P.pL=V(-0.3,-0.75,0.35); P.tR=wp.clone().add(V(0.1,-shake,0)); P.wR=up; P.pR=V(-0.3,-0.75,-0.35);
      if(phs>0){ P.tL=V(0.8,1.12,0.85); P.wL=Math.max(up,phs); P.tR=V(0.78,1.06,0.8); P.wR=phs*0.4; } }
    return {J:R.skel(P,STAND_ROOT,0),phone:phs>0.1?{pos:V(0.8,1.14,0.9),n:V(-0.1,0,1)}:null,walk:0,ph:0}; }
  const walkP=(amp,tired)=>R.gait({...R.P0,p:0.05+0.3*tired,tilt:0.04+0.4*tired,eL:0.5,eR:0.5},ph,amp,0.34,0.62,0.18);
  if(t<TL.board){ const amp=sstep(TL.morning,TL.morning+0.5,t); return {J:R.skel(walkP(amp,0.9),STAND_ROOT,0),phone:null,walk:amp,ph}; }
  if(t<TL.officeWalk){ const u=sm5(clamp((t-TL.board)/0.5)); const sp=seatPoseTired(t); sp.tL=V(SEAT_ROOT.x+0.3,0.62,0.12); sp.tR=V(SEAT_ROOT.x+0.28,0.6,-0.1); const B=R.blend(walkP(0.6*(1-u),0.9),sp,u); const rt=STAND_ROOT.clone().lerp(V(BASE.bus+SEAT_ROOT.x-sc,0,0),u); return {J:R.skel(B,rt,0),phone:null,walk:(1-u)*0.6,ph}; }
  if(t<TL.officeSit){ const u=sm5(clamp((t-TL.officeWalk)/0.35)), u2=sm5(clamp((t-(TL.officeSit-0.45))/0.45)); const B=R.blend(R.blend(seatPoseTired(t),walkP(1,0.9),u),seatPoseTired(t),u2);
    const rt=V(lerp(BASE.bus+SEAT_ROOT.x-sc,STAND_ROOT.x,u),0,lerp(0,STAND_ROOT.z,u)).lerp(SEAT_ROOT,u2); return {J:R.skel(B,rt,0),phone:null,walk:u*(1-u2),ph}; }
  if(t<TL.home0){ const w=sstep(TL.officeSit,TL.officeSit+0.3,t)*(1-sstep(TL.work1-0.1,TL.work1+0.2,t)); const sp=seatPoseTired(t); const ty=t*14;
    const kl=V(0.12+LAMPX,0.815+Math.max(0,Math.sin(ty))*0.012,0.2), kr=V(0.34+LAMPX,0.815+Math.max(0,Math.sin(ty+2.3))*0.012,0.2); sp.tL=sp.tL.clone().lerp(kl,w); sp.tR=sp.tR.clone().lerp(kr,w);
    const sip=sstep(14.6,14.95,t)*(1-sstep(15.1,15.4,t)); if(sip>0) sp.tR=sp.tR.clone().lerp(V(SEAT_ROOT.x+0.35,1.18,0.2),sip);
    return {J:R.skel(sp,SEAT_ROOT,0),phone:null,walk:0,ph:0,sip}; }
  const standU=sm5(clamp((t-TL.home0)/0.35)); const B=R.blend(seatPoseTired(t),walkP(1,1.0),standU); B.p+=0.25*Math.sin(Math.PI*standU);
  return {J:R.skel(B,SEAT_ROOT.clone().lerp(STAND_ROOT,standU),0),phone:null,walk:standU,ph}; }

// ---------------------------------------------------------------- phone / wallet / coins / bills
function phoneState(t,h){ let vis=false, kind='credit', vib=0, pos=V(0,0,0), n=PH_NORMAL;
  if(h.phone){ vis=true; pos=h.phone.pos.clone(); n=h.phone.n; if(t<TL.rise[0]) vib=1-sstep(1.2,1.65,t); else if(t>=TL.bed1) vib=sstep(TL.bed1+0.05,TL.bed1+0.3,t); else { kind='alarm'; vib=sstep(TL.alarm-0.1,TL.alarm,t)*(1-sstep(TL.morning-0.3,TL.morning,t)); } }
  return {pos,R3:phoneBasis(n),vis,kind,vib}; }
function walletState(t){ let pos=WAL.clone(), vis=true, rotX=0, rotZ=0, open=0, held=0;
  const up=sstep(TL.walletUp,TL.walletUp+0.35,t)*(1-sstep(TL.alarm-0.1,TL.alarm+0.1,t));
  if(up>0){ held=up; pos=WAL.clone().lerp(WAL_HELD.clone().add(V(0,0.08*sstep(TL.flip-0.2,TL.flip+0.3,t),0)),up); rotX=Math.PI/2*0.9*up; open=sstep(TL.walletUp,TL.walletUp+0.4,t)*1.9; rotZ=Math.PI*sstep(TL.flip-0.1,TL.flip+0.35,t); if(t>TL.flip&&t<TL.dust+0.4) pos.x+=0.015*Math.sin(t*34); }
  if(t>=TL.alarm+0.1) vis=false; return {pos,vis,rotX,rotZ,open,held}; }
function coinState(k,t){ const land=1.0+k*0.02, fl=0.45; const rest=coinRest(k); const plan=coinPlan[k];
  if(t<land-fl) return null; if(t<land){ const u=(t-(land-fl))/fl, e=eo(u); const p=PH_LIE.clone().add(V(0.0,0.05,0.05)).lerp(rest,e); p.y+=0.6*Math.sin(Math.PI*e)*(1-0.4*e); return {p,r:u*9}; }
  const t0=ITEMS[plan.item].t+plan.j*0.014, f=TL.coinFlight; if(t<t0) return {p:rest,r:0};
  if(t<t0+f){ const u=(t-t0)/f, e=u*u*(3-2*u); const p=rest.clone().lerp(SINK[plan.item],e); p.y+=0.45*Math.sin(Math.PI*u); return {p,r:u*12,s:1-0.5*sstep(0.7,1,u)}; } return null; }
const dm=new THREE.Object3D();
function applyGiants(t){ const out=1-sstep(8.4,9.2,t); fades.forEach(m=>{ m.opacity=out; });
  const door=aptG.userData.door; let sh=0; TL.knock.forEach(k=>{ const dd=t-k; if(dd>0&&dd<0.14) sh+=Math.sin(dd/0.14*Math.PI*3)*0.012; }); const dd2=t-ITEMS[0].t; if(dd2>0&&dd2<0.4) sh+=0.02*Math.exp(-dd2*8)*Math.sin(dd2*60); door.position.x=0.55+sh; door.rotation.y=sh*0.2;
  const door2=apt2G.userData.door; let sh2=0; [19.4,19.58].forEach(k=>{ const dd=t-k; if(dd>0&&dd<0.14) sh2+=Math.sin(dd/0.14*Math.PI*3)*0.012; }); door2.position.x=0.55+sh2; door2.rotation.y=sh2*0.2;
  giants.forEach((g,i)=>{ const t0=ITEMS[i].t-0.05, u=clamp((t-t0)/0.5); g.visible=t>=t0&&out>0.01&&t<TL.morning+0.4; const e=eb(u);
    if(i===0) g.position.y=lerp(-4.4,0,e);
    if(i===1){ g.position.y=lerp(3.2,0,clamp(e)); g.rotation.z=0.06*(1-clamp(u)); bikeParts.forEach(w=>{ w.rotation.z=t*6; }); }
    if(i===2) g.children.forEach(c=>{ const k=c.userData.k; const ts=t0+k*0.05, uu=clamp((t-ts)/0.28); const dropY=lerp(2.0,0,uu*uu); const r=c.userData.rest; if(c.userData.handle) c.position.set(r.x,r.y+dropY+0.17,r.z); else { c.position.set(r.x,r.y+dropY,r.z); c.rotation.y=c.userData.yaw; } c.visible=t>=ts; });
    if(i===3){ const sp=sstep(t0,t0+0.6,t); fan.rotation.y=t*(1.0+14*sp); meterDisc.rotation.z=-t*(0.5+16*sp); meterMark.rotation.z=-t*(0.5+16*sp); }
    if(i===4) g.children.forEach(c=>{ const k=c.userData.k; const a=sstep(t0+k*0.03,t0+k*0.03+0.1,t); c.visible=a>0.01; c.scale.setScalar(Math.max(a,0.001)); });
    if(i===5){ const pv=g.getObjectByName('pv'); pv.rotation.z=lerp(-1.1,1.1,sm5(clamp((t-t0-0.1)/0.6))); } }); }

// ---------------------------------------------------------------- camera
function phoneCam(R3,pos){ const n=V(0,0,1).applyMatrix4(R3), yv=V(0,1,0).applyMatrix4(R3); return {pos:pos.clone().addScaledVector(n,0.3),look:pos.clone(),up:yv}; }
const CAM=[[0.9,[-0.95,1.3,2.2],[-0.6,0.85,0.12]],[2.0,[-0.55,1.5,3.4],[-0.55,0.8,0.1]],[2.5,[-0.1,1.55,4.0],[0.05,1.28,0.15]],[3.4,[0.55,1.55,3.7],[0.75,1.28,0.1]],[7.3,[0.8,1.65,4.0],[0.95,1.38,0.0]],
  [7.9,[0.8,1.5,3.2],[0.8,1.33,0.5]],[8.5,[0.8,1.5,3.2],[0.8,1.33,0.5]],[9.3,[0.75,1.9,5.6],[0.75,1.68,0.0]],[10.4,[0.5,1.7,4.7],[0.5,1.43,0.0]],[12.2,[0.35,1.6,4.2],[0.3,1.38,0.0]],[13.0,[0.2,1.55,4.0],[0.2,1.38,0.0]],[14.3,[0.25,1.55,3.8],[0.3,1.36,0.0]],
  [15.3,[0.3,1.5,3.9],[0.3,1.38,0.0]],[16.8,[0.2,1.45,4.4],[-0.1,1.28,0.0]],[17.6,[-0.7,1.6,4.4],[-0.75,0.85,0.1]],[18.9,[-0.8,1.4,3.4],[-0.95,0.85,0.12]],[20,[-0.8,1.4,3.4],[-0.95,0.85,0.12]]];
function freeCam(t){ if(t<=CAM[0][0]) return {pos:V(...CAM[0][1]),look:V(...CAM[0][2])}; for(let i=1;i<CAM.length;i++) if(t<=CAM[i][0]){ const u=sm5((t-CAM[i-1][0])/(CAM[i][0]-CAM[i-1][0])); return {pos:V(...CAM[i-1][1]).lerp(V(...CAM[i][1]),u),look:V(...CAM[i-1][2]).lerp(V(...CAM[i][2]),u)}; } const l=CAM[CAM.length-1]; return {pos:V(...l[1]),look:V(...l[2])}; }
function camAt(t,ps){ const f=freeCam(t); const close=(t<0.95)?1:(t<2.0?1-sm5((t-0.95)/1.05):(t>=18.9?sm5(clamp((t-18.9)/1.05)):0)); if(close<=0||!ps.vis) return {...f,up:V(0,1,0)};
  const pc=phoneCam(ps.R3,ps.pos); return {pos:f.pos.clone().lerp(pc.pos,close),look:f.look.clone().lerp(pc.look,close),up:V(0,1,0).lerp(pc.up,close).normalize()}; }

// ---------------------------------------------------------------- one frame
function setT(t){
  const sc=scrollAt(t);
  aptG.position.x=-sc+BASE.apt; busG.position.x=BASE.bus+LAMPX-sc+(1-sm5(clamp((t-TL.bus0)/0.7)))*3.2; offG.position.x=BASE.off+LAMPX-sc; stG.position.x=-sc; apt2G.position.x=BASE.apt2-sc;
  strips.forEach((m,i)=>{ m.position.x=((i*0.9-sc)%19.8+19.8)%19.8-8; });
  aptG.visible=sc<4.0; busG.visible=t>=TL.bus0-0.1&&t<TL.officeSit-0.2; offG.visible=sc>3.0&&sc<11.0; apt2G.visible=sc>6.5; stG.visible=sc>5.5;
  const H_=heroJ(t); const J=H_.J; R.poseFig(hero,J);
  const gear=sstep(TL.morning,TL.morning+0.5,t)*(1-sstep(TL.bed0,TL.bed0+0.3,t)); pack.visible=tie.visible=strap.visible=gear>0.02;
  if(gear>0.02){ const ax=J.neck.clone().sub(J.hip); const L=ax.length(); const up=ax.clone().normalize(); const fwd=V(1,0,0).addScaledVector(up,-up.x).normalize(); const mid=J.hip.clone().addScaledVector(up,L*0.62);
    pack.position.copy(mid).addScaledVector(fwd,-0.14); pack.quaternion.setFromUnitVectors(V(0,1,0),up); pack.scale.setScalar(gear);
    tie.position.copy(J.neck).addScaledVector(up,-0.11).addScaledVector(fwd,0.075); tie.quaternion.setFromUnitVectors(V(0,1,0),up); tie.scale.setScalar(gear);
    const a=J.shL.clone().addScaledVector(fwd,0.02), b=pack.position.clone().addScaledVector(up,-0.12).addScaledVector(fwd,0.06); const d=b.clone().sub(a); strap.position.copy(a).add(b).multiplyScalar(0.5); strap.scale.set(0.012,d.length(),0.012); strap.quaternion.setFromUnitVectors(V(0,1,0),d.normalize()); }
  const ps=phoneState(t,H_); phone.visible=ps.vis; scrMat.map=ps.kind==='credit'?scrCredit:scrAlarm;
  if(ps.vis){ phone.position.copy(ps.pos); phone.quaternion.setFromRotationMatrix(ps.R3);
    if(ps.vib>0){ const j=Math.sin(t*2*Math.PI*40); phone.position.x+=0.0011*j*ps.vib; phone.position.y+=0.0008*Math.cos(t*2*Math.PI*37)*ps.vib; phone.rotateZ(0.008*j*ps.vib); }
    phoneLight.position.copy(ps.pos).addScaledVector(V(0,0,1).applyMatrix4(ps.R3),0.35); phoneLight.color.set(ps.kind==='credit'?0xe8b85a:0x8fc7cb); phoneLight.intensity=0.5+0.25*Math.sin(t*30)*ps.vib; } else phoneLight.intensity=0;
  const ws=walletState(t); wallet.visible=ws.vis; wallet.position.copy(ws.pos); wallet.position.x-=sc; wallet.rotation.set(ws.rotX,0,ws.rotZ); panL.rotation.z=-(ws.open>0?ws.open*0.5:0); panR.rotation.z=(ws.open>0?ws.open*0.5:0);
  const empty=sstep(TL.zero,TL.zero+0.3,t); const warn=empty*(1-sstep(TL.alarm,TL.alarm+0.3,t))*(0.5+0.5*Math.sin(t*7)); const credit=sstep(1.0,2.0,t)*(1-sstep(2.4,3.2,t));
  walMat.emissiveIntensity=0.05+0.12*credit+0.45*warn; halo.position.copy(wallet.position).add(V(0,0.05,0)); halo.material.opacity=(0.03+0.1*credit+0.35*warn)*(ws.vis?1:0); redLight.position.copy(wallet.position).add(V(0,0.3,0.2)); redLight.intensity=0.35*credit+0.35*warn;
  applyGiants(t);
  for(let k=0;k<NC;k++){ const c=coinState(k,t); if(!c||ws.held>0.1||sc>0.05){ dm.position.set(0,-9,0); dm.scale.setScalar(0.0001); } else { dm.position.copy(c.p); dm.position.x-=sc; dm.rotation.set(c.r,c.r*0.7,0); dm.scale.setScalar(c.s||1); } dm.updateMatrix(); coins.setMatrixAt(k,dm.matrix); } coins.instanceMatrix.needsUpdate=true;
  calMat.opacity=sstep(TL.calendar0,TL.calendar1,t)*(1-sstep(10.1,10.5,t)); cal.visible=calMat.opacity>0.01; cal.position.x=0.8-sc;
  const du=clamp((t-TL.dust)/1.2); dust.material.opacity=du>0&&du<1?0.9*Math.sin(Math.PI*du):0; dust.position.set(WAL_HELD.x-sc+0.04*Math.sin(du*5),WAL_HELD.y+0.15-0.7*du,WAL_HELD.z);   // one mote falls out of the upturned wallet
  cup.visible=offG.visible; const sip=H_.sip||0; cup.position.set(BASE.off+LAMPX+0.05-sc,0.84,0.2); if(sip>0.01) cup.position.copy(J.hR).add(V(0.02,0.0,0.0)); cup.rotation.z=-0.5*sip;
  cup.getObjectByName('coffee').scale.y=Math.max(0.04,1-0.96*sstep(TL.officeSit+0.2,TL.work1,t)); cup.getObjectByName('coffee').position.y=-0.04+0.04*cup.getObjectByName('coffee').scale.y;
  const night=nightAt(t); const cityOn=sstep(10.7,11.3,t)*(1-sstep(16.2,16.9,t)); cityG.visible=trafficG.visible=sky.visible=cityOn>0.01;
  cityG.position.x=-(sc*0.3+(t>TL.board?Math.min(t-TL.board,TL.officeWalk-TL.board)*1.4:0));
  cityMats.forEach(m=>{ m.emissiveIntensity=night*0.5*cityOn; });
  const boost=1+3*sstep(TL.board-0.2,TL.board+0.5,t)*(1-sstep(TL.officeWalk-0.2,TL.officeWalk+0.3,t));
  cars.forEach(c=>{ let x=c.userData.x0+c.userData.v*boost*t*0.9; x=((x+10)%20+20)%20-10; c.position.x=x; c.rotation.y=c.userData.v<0?Math.PI:0; });
  skyMat.color.copy(new THREE.Color(0x07080b).lerp(new THREE.Color(0x35404c),Math.sin(Math.PI*clamp((t-10.5)/4.0))*(1-night)*cityOn*0.9).lerp(new THREE.Color(0x3a2418),sstep(13.4,14.2,t)*(1-sstep(14.2,15.0,t))*0.8*cityOn));
  const Lk=lightAt(t)*(1+0.14*credit+0.12*sstep(17.5,18.2,t)*(1-sstep(19.2,19.9,t))); S.spot.intensity=S.SPOT_I*Lk; S.beamU.uI.value=Lk; S.moteU.uOp.value=Lk;
  teal.intensity=0.5*sstep(TL.zero,TL.zero+0.6,t)*(1-sstep(TL.morning,TL.morning+0.6,t))+0.28*night;
  const c=camAt(t,ps); let shake=0; ITEMS.forEach(it=>{ const d=t-it.t-0.1; if(d>0&&d<0.35) shake+=0.012*Math.exp(-d*9)*Math.sin(d*60); });
  S.cam.up.copy(c.up); S.cam.position.copy(c.pos).add(V(shake,shake*0.7,0)); S.cam.lookAt(c.look); S.tick(t); }
window.renderAt=(t,K=3)=>{ const fast=(t>TL.morning-0.3&&t<TL.officeSit+0.2)||(t>TL.home0-0.2&&t<TL.bed1+0.2)||t>18.9||t<2.0||(t>TL.rise[0]-0.1&&t<TL.dance[1]+0.1); return S.renderAt(setT,t,fast?5:K,{t0:0,t1:DUR,shutter:(fast&&t>2.0&&t<18.9)?1/36:1/60}); };
window.events={...TL,steps:(()=>{ const out=[]; const N=Math.round(DUR*TL.fps); let prev=null; for(let f=0;f<N;f++){ const t=f/TL.fps; const h=heroJ(t); if(h.walk<0.5){ prev=null; continue; } if(prev!==null&&Math.floor(h.ph/Math.PI)>Math.floor(prev/Math.PI)) out.push({t}); prev=h.ph; } return out; })()};
window.ready=true;
