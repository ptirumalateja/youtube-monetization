// Normal People vs Me (bedtime), 28 Oct 2026. Slow Light Dark stage (sld.js: void, one gold lamp beam with dust, soft-mirror floor),
// one bed in the pool of light, a bedside LED clock as the only counter, a window that goes pale at dawn.
// Hero: the blink-reel pictogram (near-black, warm rim, floating head) with thin stick limbs and a glowing expressive face (face.js).
// renderAt(t) is pure (parallel workers). Units are metres, floor y=0, bed along z with the headboard at z=-1.08.
import * as THREE from 'three';
import * as SLD from './sld.js';
import * as SETS from './sets.js';
import {createFace,EX,mix} from './face.js';
const {V,clamp,sstep,lerp,sm5,keys}=SLD;
const {M,B,C}=SETS;
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960;
const DUR=19.9;
const ST=SLD.createStage({W,H,lamp:V(0.5,4.4,1.3),lampTarget:V(0.08,0.5,-0.3),cone:0.3,spot:30,beam:0.09});
const scene=ST.scene; const R=SLD.createRig(scene);
const canvasTex=(w,h,fn)=>{ const c=document.createElement('canvas'); c.width=w; c.height=h; const g=c.getContext('2d'); fn(g,w,h); const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; t.userData={c,g}; return t; };

// ---------------------------------------------------------------- shots
const SHOTS=[
  {id:'normal', t0:0.0, t1:2.4},   // normal people: flop, blanket up, asleep, 9:00 -> 9:05, Zzz
  {id:'me',     t0:2.4, t1:4.0},   // ME: same flop, eyes shut... then snap open
  {id:'turn1',  t0:4.0, t1:5.0},   // 9:30 roll over + sigh
  {id:'turn2',  t0:5.0, t1:6.0},   // 10:00 pillow over the face
  {id:'turn3',  t0:6.0, t1:7.0},   // 11:00 blanket kicked off, starfish glare; the phone buzzes
  {id:'phone',  t0:7.0, t1:8.4},   // grabs the phone, face lit
  {id:'lapse',  t0:8.4, t1:10.6},  // 11:00 -> 3:00 time-lapse
  {id:'laugh',  t0:10.6,t1:12.8},  // laughs out loud, then hand over the mouth
  {id:'rooster',t0:12.8,t1:13.4},  // silence: he freezes, eyes up to the window
  {id:'window', t0:13.4,t1:14.6},  // the rooster crows on the fence
  {id:'five',   t0:14.6,t1:15.05}, // 5:00, shock
  {id:'alarm',  t0:15.05,t1:15.6}, // POV from his eyes: the phone screen says ALARM 6:00 AM
  {id:'fall',   t0:15.6,t1:16.1},  // the phone falls on his face
  {id:'up',     t0:16.1,t1:19.9} ];// bolt upright: ALARM IN 1 HOUR, then flops back (= frame 0)
const shotAt=t=>SHOTS.find(s=>t>=s.t0&&t<s.t1)||SHOTS[SHOTS.length-1];

// ---------------------------------------------------------------- the room: back wall with a window, bed, nightstand, LED clock
const WALL=M(0x1b1e27,{r:0.95}), WOOD=M(0x3a2a20,{r:0.65}), SHEET=M(0x8c867b,{r:0.95}), PILLOWM=M(0x9c968a,{r:0.95});
{ const w=new THREE.Mesh(new THREE.PlaneGeometry(9,4),WALL); w.position.set(0,2,-1.32); w.receiveShadow=true; scene.add(w); }
const winTex=canvasTex(512,576,()=>{});
function drawWindow(dawn,rooster,rb=0){ const {g}=winTex.userData, w=512, h=576; const gr=g.createLinearGradient(0,0,0,h);
  gr.addColorStop(0,`rgb(${lerp(10,96,dawn)|0},${lerp(14,122,dawn)|0},${lerp(32,168,dawn)|0})`); gr.addColorStop(0.75,`rgb(${lerp(16,214,dawn)|0},${lerp(22,170,dawn)|0},${lerp(44,150,dawn)|0})`); gr.addColorStop(1,`rgb(${lerp(20,250,dawn)|0},${lerp(24,196,dawn)|0},${lerp(40,140,dawn)|0})`);
  g.fillStyle=gr; g.fillRect(0,0,w,h);
  if(dawn<0.6){ const r=SLD.rng(5); g.fillStyle=`rgba(230,235,255,${0.8*(1-dawn/0.6)})`; for(let i=0;i<60;i++){ g.beginPath(); g.arc(r()*w,r()*h*0.7,0.6+r()*1.6,0,7); g.fill(); }
    g.fillStyle=`rgba(255,248,225,${1-dawn/0.6})`; g.beginPath(); g.arc(370,120,34,0,7); g.fill(); g.fillStyle=`rgb(${lerp(10,96,dawn)|0},${lerp(14,122,dawn)|0},${lerp(32,168,dawn)|0})`; g.beginPath(); g.arc(386,108,30,0,7); g.fill(); }
  // rooftops and a fence line
  g.fillStyle=`rgb(${lerp(6,40,dawn)|0},${lerp(7,38,dawn)|0},${lerp(12,52,dawn)|0})`; g.beginPath(); g.moveTo(0,h); g.lineTo(0,430); g.lineTo(90,380); g.lineTo(180,430); g.lineTo(260,430); g.lineTo(260,400); g.lineTo(380,400); g.lineTo(380,440); g.lineTo(512,420); g.lineTo(512,h); g.fill();
  g.fillRect(0,500,w,h-500);
  if(rooster){ g.save(); g.translate(372,505); g.rotate(-0.06*Math.sin(rb*30)); g.scale(1.55,1.55*(1+0.05*Math.sin(rb*30))); g.fillStyle='#07070a'; g.beginPath();   // rooster on the fence, beak open
    g.moveTo(-40,0); g.quadraticCurveTo(-58,-40,-46,-78); g.quadraticCurveTo(-30,-58,-22,-44); g.quadraticCurveTo(-10,-56,6,-50); g.quadraticCurveTo(18,-66,22,-80);
    g.lineTo(30,-88); g.lineTo(36,-80); g.lineTo(50,-84); g.lineTo(40,-76); g.lineTo(52,-72); g.lineTo(38,-70); g.quadraticCurveTo(40,-50,30,-34); g.quadraticCurveTo(26,-6,6,0); g.closePath(); g.fill();
    g.fillStyle='#b8261c'; g.beginPath(); g.moveTo(22,-86); g.lineTo(26,-98); g.lineTo(30,-90); g.lineTo(34,-100); g.lineTo(36,-88); g.closePath(); g.fill();
    g.strokeStyle='#07070a'; g.lineWidth=3; g.beginPath(); g.moveTo(-6,0); g.lineTo(-8,14); g.moveTo(8,0); g.lineTo(10,14); g.stroke(); g.restore(); }
  winTex.needsUpdate=true; }
const winM=new THREE.MeshBasicMaterial({map:winTex,fog:false,color:0x7a7a7a});
const WIN=new THREE.Group(); { B(WIN,0.98,1.1,0.06,WOOD,0,0,0); const p=new THREE.Mesh(new THREE.PlaneGeometry(0.86,0.97),winM); p.position.z=0.035; WIN.add(p); B(WIN,0.03,1.0,0.07,WOOD,0,0,0.04); B(WIN,0.9,0.03,0.07,WOOD,0,0.06,0.04); B(WIN,1.1,0.05,0.14,WOOD,0,-0.56,0.06); }
WIN.position.set(-0.15,1.62,-1.29); scene.add(WIN);
const dawnLight=new THREE.SpotLight(0xa8c4ff,0,7,0.8,0.7,1.1); dawnLight.position.set(-0.15,1.7,-1.5); dawnLight.target.position.set(0.3,0.6,0.2); scene.add(dawnLight,dawnLight.target);
// bed
{ const bd=new THREE.Group(); B(bd,1.18,0.3,2.16,WOOD,0,0.15,0,{round:0.03}); B(bd,1.12,0.2,2.08,SHEET,0,0.4,0,{round:0.06}); B(bd,1.2,1.05,0.07,WOOD,0,0.52,-1.1,{round:0.025}); B(bd,1.2,0.55,0.06,WOOD,0,0.3,1.1,{round:0.02}); scene.add(bd); }
const pillow=new THREE.Group(); B(pillow,0.66,0.13,0.38,PILLOWM,0,0,0,{round:0.06}); scene.add(pillow); const PILLOW0=V(0,0.555,-0.83);
// nightstand + LED clock + phone resting place
const NS=V(0.86,0,-0.85); { const ns=new THREE.Group(); B(ns,0.44,0.5,0.4,WOOD,0,0.25,0,{round:0.02}); B(ns,0.38,0.012,0.02,M(0x6a5240),0,0.32,0.201); ns.position.copy(NS); scene.add(ns); }
const clkTex=canvasTex(512,224,()=>{});
let clkLast=''; function drawClock(str,blink=1){ if(str+blink===clkLast) return; clkLast=str+blink; const {g}=clkTex.userData; g.fillStyle='#0b0606'; g.fillRect(0,0,512,224);
  g.font='bold 168px "DejaVu Sans Mono", monospace'; g.textAlign='center'; g.textBaseline='middle'; g.fillStyle='rgba(255,60,30,0.08)'; g.fillText('88:88',256,118);
  g.shadowColor='rgba(255,80,40,1)'; g.shadowBlur=26; g.fillStyle=`rgba(255,${90+40*blink|0},60,${0.35+0.65*blink})`; g.fillText(str,256,118); g.shadowBlur=0; clkTex.needsUpdate=true; }
const CLOCK=new THREE.Group(); { B(CLOCK,0.26,0.12,0.09,M(0x16110f,{r:0.4}),0,0,0,{round:0.02}); const s=new THREE.Mesh(new THREE.PlaneGeometry(0.22,0.096),new THREE.MeshBasicMaterial({map:clkTex,fog:false})); s.position.z=0.046; CLOCK.add(s); }
CLOCK.position.set(NS.x+0.02,0.565,NS.z-0.04); CLOCK.rotation.y=-0.55; scene.add(CLOCK);
const clkLight=new THREE.PointLight(0xff5a30,0.12,1.4,2); clkLight.position.set(NS.x-0.1,0.62,NS.z+0.12); scene.add(clkLight);

// ---------------------------------------------------------------- phone
const feedTex=canvasTex(360,760,()=>{});
function drawFeed(k,on){ const {g}=feedTex.userData; const r=SLD.rng(100+k); g.fillStyle='#0e0f14'; g.fillRect(0,0,360,760); if(!on){ feedTex.needsUpdate=true; return; }
  const hue=[200,330,18,45,280,160][k%6]; g.fillStyle=`hsl(${hue},60%,52%)`; g.fillRect(0,60,360,520); const gr=g.createLinearGradient(0,60,0,580); gr.addColorStop(0,'rgba(255,255,255,0.18)'); gr.addColorStop(1,'rgba(0,0,0,0.4)'); g.fillStyle=gr; g.fillRect(0,60,360,520);
  g.fillStyle='rgba(255,255,255,0.85)'; g.beginPath(); g.arc(180,300,46,0,7); g.fill(); g.fillStyle=`hsl(${hue},60%,40%)`; g.beginPath(); g.moveTo(166,276); g.lineTo(200,300); g.lineTo(166,324); g.fill();
  g.fillStyle='#ddd'; g.beginPath(); g.arc(34,628,18,0,7); g.fill(); g.fillStyle='rgba(230,230,235,0.8)'; g.fillRect(64,616,150*(0.6+0.4*r()),10); g.fillStyle='rgba(230,230,235,0.5)'; g.fillRect(64,640,220*(0.5+0.5*r()),9);
  feedTex.needsUpdate=true; }
const alarmTex=canvasTex(360,760,()=>{});
function drawAlarm(p){ const {g}=alarmTex.userData; g.fillStyle='#0b0c11'; g.fillRect(0,0,360,760); const r=g.createRadialGradient(180,330,10,180,330,300); r.addColorStop(0,`rgba(255,150,60,${0.28+0.18*p})`); r.addColorStop(1,'rgba(255,150,60,0)'); g.fillStyle=r; g.fillRect(0,0,360,760);
  g.textAlign='center'; g.fillStyle='#ff9a3c'; g.font='bold 40px "DejaVu Sans", sans-serif'; g.fillText('ALARM',180,170);
  g.save(); g.translate(180,260); g.rotate(0.14*Math.sin(p*Math.PI*2)); g.fillStyle='#ffd08a'; g.beginPath(); g.moveTo(-34,22); g.quadraticCurveTo(-34,-34,0,-38); g.quadraticCurveTo(34,-34,34,22); g.lineTo(42,32); g.lineTo(-42,32); g.closePath(); g.fill(); g.beginPath(); g.arc(0,40,9,0,7); g.fill(); g.restore();
  g.fillStyle='#fff'; g.font='bold 120px "DejaVu Sans", sans-serif'; g.fillText('6:00',180,440); g.font='bold 54px "DejaVu Sans", sans-serif'; g.fillText('AM',180,510);
  g.fillStyle='rgba(255,255,255,0.14)'; g.beginPath(); g.roundRect(40,620,280,76,38); g.fill(); g.fillStyle='rgba(255,255,255,0.8)'; g.font='28px "DejaVu Sans", sans-serif'; g.fillText('slide to stop',190,668); alarmTex.needsUpdate=true; }
drawAlarm(0);
const phoneScreenM=new THREE.MeshBasicMaterial({map:feedTex,fog:false,color:0xbdbdbd});
const PHONE=new THREE.Group(); { B(PHONE,0.072,0.15,0.009,M(0x0d0e12,{r:0.3,m:0.4}),0,0,0,{round:0.004}); const s=new THREE.Mesh(new THREE.PlaneGeometry(0.064,0.138),phoneScreenM); s.position.z=0.0052; PHONE.add(s); } PHONE.scale.setScalar(1.3); scene.add(PHONE);
const phoneLight=new THREE.PointLight(0x9cc0ff,0,1.6,1.6); scene.add(phoneLight);
const PHONE_REST=V(NS.x-0.1,0.506,NS.z+0.1);
function placePhone(pos,screenDir,upDir){ const z=screenDir.clone().normalize(), y=upDir.clone().addScaledVector(z,-upDir.dot(z)).normalize(), x=y.clone().cross(z); PHONE.position.copy(pos); PHONE.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(x,y,z)); }

// ---------------------------------------------------------------- Zzz
const zTex=canvasTex(128,128,(g)=>{ g.font='bold 104px "DejaVu Sans", sans-serif'; g.textAlign='center'; g.textBaseline='middle'; g.shadowColor='rgba(255,230,190,1)'; g.shadowBlur=14; g.fillStyle='#fff0d4'; g.fillText('Z',64,68); });
const Zs=[0,1,2].map(()=>{ const s=new THREE.Sprite(new THREE.SpriteMaterial({map:zTex,transparent:true,depthWrite:false,fog:false})); scene.add(s); return s; });

// ---------------------------------------------------------------- blanket: a height field draped over the body
const BL=new THREE.PlaneGeometry(1.26,2.14,56,96); BL.rotateX(-Math.PI/2); const BL0=Float32Array.from(BL.attributes.position.array);
const blanketTex=SLD.noiseTex(256,9,128,60,40,0.1); blanketTex.repeat.set(6,10);
const blanket=new THREE.Mesh(BL,new THREE.MeshStandardMaterial({color:0x2d3956,roughness:0.95,map:blanketTex,side:THREE.DoubleSide})); blanket.castShadow=true; blanket.receiveShadow=true; blanket.frustumCulled=false; scene.add(blanket);
function segD(px,pz,a,b){ const dx=b.x-a.x, dz=b.z-a.z, L2=dx*dx+dz*dz||1e-6; const u=clamp(((px-a.x)*dx+(pz-a.z)*dz)/L2); const x=a.x+dx*u-px, z=a.z+dz*u-pz; return Math.sqrt(x*x+z*z); }
// caps: [{a,b,r,top}] (top = body surface height to clear), zTop = blanket's upper edge, wob = shaking
function drape(caps,zTop,wob,t){ const p=BL.attributes.position.array, TOP=0.505;
  for(let i=0;i<p.length;i+=3){ const x0=BL0[i], z0=BL0[i+2]+0.02; let z=Math.max(z0,zTop); const fold=Math.max(0,zTop-z0); let x=x0, y=TOP;
    let lump=0; for(const c of caps){ const d=segD(x0,z,c.a,c.b), k=Math.exp(-Math.pow(d/(c.r+0.09),4)*1.6); lump=Math.max(lump,(c.top+0.03-TOP)*k); }
    y+=lump; if(wob) y+=wob*0.012*Math.sin(t*41+x0*9+z*7)*Math.min(1,lump*12);
    const ax=Math.abs(x0); if(ax>0.565){ x=Math.sign(x0)*(0.57+(ax-0.565)*0.12); y=Math.min(y,TOP-(ax-0.565)*3.2); }
    if(z>1.06){ z=1.07+(z-1.06)*0.1; y=Math.min(y,TOP-(z0-1.06)*3); }
    y+=Math.min(fold,0.05)*0.7+(fold>0?0.012:0); p[i]=x; p[i+1]=y; p[i+2]=z; }
  BL.attributes.position.needsUpdate=true; BL.computeVertexNormals(); }

// ---------------------------------------------------------------- the hero: pictogram with thin stick limbs, floating head, glowing face
const hero=R.makeFig(0x0d0b0a,'hero',{rim:0.55,rimCol:0xffc27a,lift:0.0});
const PT={len:0.58,hipR:0.07,shR:0.132,capB:0.05,capT:0.075,limb:0.024};
const HEADR=0.165;
hero.bones[0].geometry=(()=>{ const pts=[], L=PT.len, N=14;
  for(let k=0;k<=N;k++){ const a=k/N*Math.PI/2; pts.push(new THREE.Vector2(PT.hipR*Math.sin(a), (PT.capB*(1-Math.cos(a)))/L-0.5)); }
  for(let k=1;k<N;k++){ const u=k/N, y=PT.capB+u*(L-PT.capB-PT.capT); pts.push(new THREE.Vector2(PT.hipR+(PT.shR-PT.hipR)*Math.pow(u,1.4), y/L-0.5)); }
  for(let k=0;k<=N;k++){ const a=k/N*Math.PI/2; pts.push(new THREE.Vector2(PT.shR*Math.cos(a)**0.6, (L-PT.capT+PT.capT*Math.sin(a))/L-0.5)); }
  const g=new THREE.LatheGeometry(pts,40); g.computeVertexNormals(); return g; })();
const FACE=createFace(scene);
function boneTo(m,a,b,r){ const d=b.clone().sub(a); const len=Math.max(d.length(),1e-4); m.position.copy(a).add(b).multiplyScalar(0.5); m.scale.set(r,len,r); m.quaternion.setFromUnitVectors(SLD.UPV,d.multiplyScalar(1/len)); m.visible=true; }
const ball=(m,p,r)=>{ m.position.copy(p); m.scale.setScalar(r); m.visible=true; };
// body state: hip, pitch (0 sitting up, ~1.45 lying back), roll (+ = onto his left side, facing +x), nod (head toward chest), turn (head yaw),
// hands: tL/tR world targets (default: resting on the belly), legs: 'hidden' | {spread}
function bodyJ(o){ const up=V(0,1,0), A0=V(0,0,-1);
  const d=up.clone().multiplyScalar(Math.cos(o.pitch)).addScaledVector(A0,Math.sin(o.pitch)).normalize();
  const n0=A0.clone().multiplyScalar(-Math.cos(o.pitch)).addScaledVector(up,Math.sin(o.pitch)).normalize(); const l0=d.clone().cross(n0);
  const n=n0.clone().multiplyScalar(Math.cos(o.roll||0)).addScaledVector(l0,Math.sin(o.roll||0)).normalize(); const l=d.clone().cross(n).normalize();
  const J={hip:o.hip.clone(),d,n,l}; J.neck=J.hip.clone().addScaledVector(d,PT.len);
  const nod=o.nod||0; const hd=d.clone().multiplyScalar(Math.cos(nod)).addScaledVector(n,Math.sin(nod)).normalize();
  let f=n.clone().multiplyScalar(Math.cos(nod)).addScaledVector(d,-Math.sin(nod)).normalize(); const tu=o.turn||0; f=f.multiplyScalar(Math.cos(tu)).addScaledVector(hd.clone().cross(f),Math.sin(tu)).normalize();
  J.head=J.neck.clone().addScaledVector(hd,0.045+HEADR); J.hd=hd; J.f=f;
  for(const [s,sg] of [['L',1],['R',-1]]){ const S=J.neck.clone().addScaledVector(d,-0.075).addScaledVector(l,sg*0.125); J['sh'+s]=S;
    const T=o['t'+s]||J.hip.clone().addScaledVector(d,0.12).addScaledVector(n,0.15).addScaledVector(l,sg*0.2);
    const pole=o['p'+s]||l.clone().multiplyScalar(sg).addScaledVector(d,-0.4);
    const r=R.ik(S,T,pole); J['el'+s]=r.E; J['h'+s]=r.Hd; }
  if(o.legs&&o.legs!=='hidden'){ const sp=o.legs.spread||0.3; for(const [s,sg] of [['L',1],['R',-1]]){ const a=J.hip.clone().addScaledVector(l,sg*0.07);
      const dir=d.clone().multiplyScalar(-Math.cos(sp)).addScaledVector(l,sg*Math.sin(sp)).normalize(); const k=a.clone().addScaledVector(dir,R.L.thigh).addScaledVector(n,0.03), ft=k.clone().addScaledVector(dir,R.L.shin).addScaledVector(n,-0.03);
      J['hip'+s]=a; J['k'+s]=k; J['f'+s]=ft; } }
  return J; }
function poseHero(J,o){ const B_=hero.bones, Jt=hero.joints, r=PT.limb; hero.all.forEach(m=>m.visible=false);
  const ax=J.d, a=J.hip.clone().addScaledVector(ax,-PT.capB), b=J.neck.clone().addScaledVector(ax,0.012), dd=b.clone().sub(a), len=dd.length();
  const T=B_[0]; T.position.copy(a).add(b).multiplyScalar(0.5); T.scale.set(1,len,1); T.quaternion.setFromUnitVectors(V(0,1,0),dd.normalize()); T.visible=true;
  boneTo(B_[5],J.shL,J.elL,r); boneTo(B_[6],J.elL,J.hL,r); boneTo(B_[7],J.shR,J.elR,r); boneTo(B_[8],J.elR,J.hR,r);
  ball(Jt[6],J.shL,r*1.6); ball(Jt[7],J.shR,r*1.6); ball(Jt[8],J.elL,r*1.05); ball(Jt[9],J.elR,r*1.05); ball(Jt[10],J.hL,o.mittL||r*1.45); ball(Jt[11],J.hR,o.mittR||r*1.45);
  if(J.kL){ boneTo(B_[1],J.hipL,J.kL,r*1.1); boneTo(B_[2],J.kL,J.fL,r*1.1); boneTo(B_[3],J.hipR,J.kR,r*1.1); boneTo(B_[4],J.kR,J.fR,r*1.1); ball(Jt[2],J.kL,r*1.15); ball(Jt[3],J.kR,r*1.15); ball(Jt[4],J.fL,r*1.6); ball(Jt[5],J.fR,r*1.6); }
  ball(hero.head,J.head,HEADR); FACE.place(J.head,J.f,J.hd,HEADR,o.face!==false); }

// ---------------------------------------------------------------- timeline
const HIP=V(0,0.6,-0.02);
const fmt=m=>{ m=((Math.round(m)%1440)+1440)%1440; const h=Math.floor(m/60), mm=m%60; return `${(h%12)||12}:${String(mm).padStart(2,'0')}`; };
const EXK=(K,t)=>{ if(t<=K[0][0]) return EX[K[0][1]]; for(let i=1;i<K.length;i++) if(t<=K[i][0]){ const u=sm5(clamp((t-K[i-1][0])/(K[i][0]-K[i-1][0]))); const a=EX[K[i-1][1]], b=EX[K[i][1]]; return K[i-1][1]===K[i][1]?a:mix(a,b,u); } return EX[K[K.length-1][1]]; };
const blinkAt=(t,list)=>{ let v=0; for(const b of list){ const u=t-b; if(u>=0&&u<0.18) v=Math.max(v,u<0.06?u/0.06:u<0.1?1:1-(u-0.1)/0.08); } return v; };
// the flop: from half-sitting (pitch 0.75, frame 0) down onto the pillow with a small bounce
const flopPitch=u=>u<0?0.75:u<0.42?lerp(0.75,1.5,sm5(u/0.42)):1.5-0.05*Math.sin(Math.min(1,(u-0.42)/0.35)*Math.PI)*Math.exp(-(u-0.42)*3);
const CAM={
  top:   [[0.75,2.55,2.45],[0.08,0.78,-0.4],38],
  topIn: [[0.55,2.2,1.75],[0.06,0.74,-0.6],36],
  side1: [[1.9,2.1,0.85],[0.1,0.66,-0.55],38],
  high:  [[0.45,3.4,1.75],[0.1,0.5,-0.15],40],
  side:  [[1.75,1.4,-0.45],[0.12,0.8,-0.85],38],
  sideIn:[[1.3,1.2,-0.6],[0.12,0.82,-0.86],34],
  win:   [[0.3,1.1,0.6],[0.0,1.45,-1.29],34],
  winIn: [[0.25,1.15,0.2],[0.02,1.42,-1.29],32],
  ptop:  [[0.45,2.35,0.95],[0.06,0.74,-0.6],36],
  ptopIn:[[0.36,2.2,0.62],[0.05,0.72,-0.66],32],
  front: [[0.5,1.65,2.35],[0.04,1.22,-0.25],38],
  open:  [[0.42,1.95,1.7],[0.05,1.12,-0.55],34] };
function camLerp(a,b,u){ const A=CAM[a], Bc=CAM[b]; return [V(...A[0]).lerp(V(...Bc[0]),u),V(...A[1]).lerp(V(...Bc[1]),u),lerp(A[2],Bc[2],u)]; }

function state(t){ const sh=shotAt(t), id=sh.id, lt=t-sh.t0; const S={id,legs:'hidden',caps:null,zTop:-0.42,wob:0,phone:null,phoneOn:false,clock:'9:00',zzz:0,dawn:0,rooster:false,feedK:0,alarm:false,pillow:null};
  let o={hip:HIP.clone(),pitch:1.5,roll:0,nod:0.32,turn:0}; let ex=EX.neutral, cam;
  if(id==='normal'||id==='me'){ // calm bedtime routine: a yawn, lie back, pull the blanket up. NORMAL falls asleep; ME's eyes stay open (match cut)
    const lie=sm5(clamp((lt-0.12)/0.8)); o.pitch=lerp(0.6,1.5,lie)-0.025*Math.sin(Math.min(1,Math.max(0,(lt-0.9)/0.35))*Math.PI); o.nod=lerp(0.05,0.32,sstep(0.2,1.0,lt));
    const J0=bodyJ(o); const hand=sg=>{ const belly=J0.hip.clone().addScaledVector(J0.d,0.12).addScaledVector(J0.n,0.15).addScaledVector(J0.l,sg*0.2);
      const chest=J0.neck.clone().addScaledVector(J0.d,-0.14).addScaledVector(J0.n,0.17).addScaledVector(J0.l,sg*0.17);
      return belly.clone().lerp(chest,sstep(0.75,1.25,lt)).lerp(belly,sstep(1.5,1.9,lt)); };
    o.tL=hand(1); o.tR=hand(-1); o.pL=V(0.25,-1,0.1); o.pR=V(-0.25,-1,0.1);
    S.zTop=lerp(0.05,-0.42,sstep(0.8,1.35,lt));
    if(id==='normal'){ ex=EXK([[0,'yawn'],[0.45,'yawn'],[0.8,'sleepy'],[1.3,'content']],lt); S.clock=lt<1.45?'9:00':'9:05'; S.zzz=sstep(1.6,1.8,lt); cam=camLerp('open','topIn',sm5(clamp(lt/2.4))); }
    else { ex=lt<1.15?EXK([[0,'yawn'],[0.45,'yawn'],[0.8,'sleepy'],[1.1,'content']],lt):mix(EX.content,EX.wide,sstep(1.15,1.22,lt)); cam=camLerp('open','topIn',sm5(clamp(lt/1.6))); if(lt>1.15) ex={...ex,px:0,py:0.6}; } }
  else if(id==='turn1'){ S.clock='9:30'; o.roll=lerp(0.0,0.8,sm5(clamp((lt-0.35)/0.45))); o.nod=0.2; ex=EXK([[0,'wide'],[0.12,'sigh'],[0.5,'sigh'],[0.7,'annoyed'],[1.0,'annoyed']],lt);
    const J0=bodyJ(o); o.tR=J0.head.clone().addScaledVector(J0.f,0.1).addScaledVector(J0.hd,-0.14).addScaledVector(J0.l,-0.1).add(V(0,-0.06,0)); o.pR=V(0,-0.5,1);
    cam=camLerp('top','topIn',0.3+0.3*lt); }
  else if(id==='turn2'){ S.clock='10:00'; o.nod=0.2; const J0=bodyJ(o); const kick=Math.sin(lt*22)*sstep(0.2,0.3,lt)*(1-sstep(0.75,0.9,lt));
    const lift=sstep(0.8,0.97,lt); S.pillow={pos:J0.head.clone().addScaledVector(J0.f,0.2+0.3*lift).add(V(0,0.28*lift,0.01*kick)),rot:[0.25+0.5*lift,0,0.06*kick+0.3*lift]};
    o.tL=S.pillow.pos.clone().add(V(0.28,-0.02,0)); o.tR=S.pillow.pos.clone().add(V(-0.28,-0.02,0)); o.pL=V(0.6,0.3,0.5); o.pR=V(-0.6,0.3,0.5); S.wob=Math.abs(kick); ex=lt<0.84?EX.annoyed:mix(EX.annoyed,EX.glare,sstep(0.84,0.95,lt)); o.face=lt>0.84;
    cam=camLerp('top','topIn',0.4+0.2*lt); }
  else if(id==='turn3'){ S.clock='11:00'; o.nod=0.18; o.legs={spread:0.32}; S.zTop=0.78; const J0=bodyJ(o);
    o.tL=J0.shL.clone().addScaledVector(J0.l,0.5).addScaledVector(J0.d,0.22).add(V(0,-0.03,0)); o.tR=J0.shR.clone().addScaledVector(J0.l,-0.5).addScaledVector(J0.d,0.22).add(V(0,-0.03,0));
    const buzz=lt>0.5; ex=buzz?{...mix(EX.glare,EX.wide,sstep(0.62,0.8,lt)),px:sstep(0.6,0.8,lt)*0.95,py:lerp(0.7,0.0,sstep(0.6,0.8,lt))}:EX.glare; o.turn=-0.35*sstep(0.7,0.95,lt);
    S.phone={pos:PHONE_REST.clone().add(V(0,0.004*Math.sin(t*90)*(buzz?1:0),0)),dir:V(0,1,0),up:V(-0.3,0,-1)}; S.phoneOn=buzz&&Math.sin(lt*7)>-0.8; cam=camLerp('high','high',0); }
  else { // phone shots, on his back under the top camera so the face reads upright: phone, lapse, laugh, rooster, window, five
    o.roll=0.1; o.nod=0.36; o.pL=V(1,-0.3,0.3); o.pR=V(-1,-0.3,0.3);
    const J0=bodyJ(o); const hold=J0.neck.clone().addScaledVector(J0.n,0.24).addScaledVector(J0.d,-0.16);
    let ph=hold.clone(), pt=1, shake=0;
    if(id==='phone'){ pt=sstep(0.3,0.75,lt); const reach=sstep(0.0,0.28,lt); ph=PHONE_REST.clone().lerp(hold,pt); S.clock='11:00'; S.phoneOn=true; S.feedK=0;
      ex=pt<0.6?{...mix(EX.wide,EX.focus,sstep(0.1,0.3,lt)),px:0.8*(1-pt),py:-0.2}:{...mix(EX.focus,EX.delight,sstep(0.75,1.0,lt)),px:0,py:-0.35}; o.turn=-0.3*(1-pt)*reach;
      cam=camLerp('ptop','ptopIn',sm5(clamp(lt/1.4))*0.3);
      if(pt<0.02){ o.tL=J0.shL.clone().lerp(PHONE_REST,reach); } }
    else if(id==='lapse'){ const u=clamp(lt/2.15); const mins=23*60+Math.pow(u,1.8)*240; S.clock=lt>2.1?'3:00':fmt(mins); S.feedK=1+Math.floor(Math.pow(u,1.5)*30);
      ex=EXK([[0,'delight'],[0.5,'smirk'],[0.9,'focus'],[1.4,'wide'],[1.75,'smirk'],[2.2,'delight']],lt); ex={...ex,px:0,py:-0.35}; S.phoneOn=true; cam=camLerp('ptop','ptopIn',0.3+0.3*sm5(u)); }
    else if(id==='laugh'){ S.clock='3:00'; S.phoneOn=true; S.feedK=31; const cover=sstep(1.05,1.2,lt);
      ex=lt<1.1?mix(EX.delight,EX.laugh,sstep(0.0,0.1,lt)):EX.muffled; shake=(lt<1.1?1:0.55)*Math.sin(lt*38); o.roll+=0.06*shake; o.nod+=0.05*Math.sin(lt*19); S.wob=lt<1.1?1:0.6;
      const J1=bodyJ(o); if(cover>0){ o.tL=J1.head.clone().addScaledVector(J1.f,HEADR*0.85+0.02).addScaledVector(J1.hd,-0.115).addScaledVector(J1.l,-0.02).lerp(J1.shL.clone().addScaledVector(J1.n,0.2),1-cover); o.mittL=0.068*cover+PT.limb*1.45*(1-cover); o.pL=V(1,0.2,0.4); }
      cam=camLerp('ptopIn','ptopIn',0); }
    else if(id==='rooster'){ S.clock='4:59'; S.phoneOn=true; S.feedK=31; S.dawn=0.35; const look=sstep(0.2,0.45,lt);
      ex={...mix(EX.muffled,EX.frozen,sstep(0.0,0.12,lt)),px:-0.1*look,py:0.85*look}; o.nod=0.36-0.12*look; const drop=sstep(0.05,0.3,lt);
      const J1=bodyJ(o); o.tL=J1.head.clone().addScaledVector(J1.f,HEADR*0.85+0.02).addScaledVector(J1.hd,-0.115).addScaledVector(J1.l,-0.02).lerp(J1.shL.clone().addScaledVector(J1.n,0.2),drop); o.mittL=lerp(0.068,PT.limb*1.45,drop); o.pL=V(1,0.2,0.4);
      cam=camLerp('ptopIn','ptopIn',0); }
    else if(id==='window'){ S.clock='4:59'; S.phoneOn=true; S.feedK=31; S.dawn=0.55; S.rooster=true; ex=EX.frozen; cam=camLerp('win','winIn',sm5(clamp(lt/1.2))); S.rb=lt; }
    else if(id==='five'||id==='alarm'){ S.clock='5:00'; S.dawn=0.75; S.phoneOn=true; S.alarm=true; S.alarmP=(id==='alarm'?lt:lt+0.5)*2.2; ex=EX.shock;
      cam=camLerp('ptopIn','ptopIn',0); const punch=sstep(0,0.08,lt)*(1-sstep(0.08,0.4,lt)); if(id==='five') cam[2]-=5*punch;
      const buzz=0.003*Math.sin(t*95); ph=hold.clone().add(V(buzz,buzz,0)); S.phoneBuzz=id==='alarm'; }
    else { S.clock='5:00'; S.dawn=0.75; S.phoneOn=true; S.alarm=true; S.alarmP=1; const u=clamp((lt-0.08)/0.14), fall=u*u; ex=lt<0.22?EX.shock:{...EX.shock,eo:0,ec:-1,es:1,mo:0.35,mO:0,mc:-0.7,ba:0.9};
      const J1=bodyJ(o); const land=J1.head.clone().addScaledVector(J1.f,HEADR+0.014); const bounce=lt>0.22?0.012*Math.exp(-(lt-0.22)*12)*Math.abs(Math.sin((lt-0.22)*40)):0;
      ph=hold.clone().lerp(land,fall).add(V(0,bounce,0)); pt=1;
      const rest=J1.hip.clone().addScaledVector(J1.d,0.12).addScaledVector(J1.n,0.15); o.tL=J1.shL.clone().addScaledVector(J1.l,0.2).addScaledVector(J1.n,0.2).lerp(rest.clone().addScaledVector(J1.l,0.2),sstep(0.2,0.45,lt)); o.tR=J1.shR.clone().addScaledVector(J1.l,-0.2).addScaledVector(J1.n,0.2).lerp(rest.clone().addScaledVector(J1.l,-0.2),sstep(0.2,0.45,lt));
      cam=camLerp('ptopIn','ptopIn',0); if(lt>0.22) cam[2]+=1.4*Math.sin((lt-0.22)*70)*Math.exp(-(lt-0.22)*11); }
    const J1=bodyJ(o); const toFace=J1.head.clone().sub(ph).normalize();
    S.phone={pos:ph,dir:id==='fall'&&lt>0.2?J1.f.clone().negate():toFace.lerp(V(0,1,0),1-pt).normalize(),up:J1.hd.clone().lerp(V(-0.3,0,-1),1-pt)};
    if(id==='five'||id==='alarm'||id==='fall'){ // one continuous move: from the shock face, round to his eyes so the screen reads, then back out as the phone drops
      const hDir=J1.head.clone().sub(hold).normalize(); const Pc=[hold.clone().addScaledVector(hDir,0.46),hold.clone(),30], A0=camLerp('ptopIn','ptopIn',0);
      const u1=sm5(clamp((t-14.68)/0.82)), u2=sm5(clamp((t-15.64)/0.3)), uu=u1*(1-u2);
      cam=[A0[0].clone().lerp(Pc[0],uu).addScaledVector(J1.l,-0.24*Math.sin(Math.PI*uu)),A0[1].clone().lerp(Pc[1],uu),lerp(A0[2],Pc[2],uu)]; S.camUp=V(0,1,0).lerp(J1.hd,uu).normalize();
      if(id==='five') cam[2]-=5*sstep(0,0.08,lt)*(1-sstep(0.08,0.4,lt)); if(id==='fall'&&lt>0.22) cam[2]+=1.4*Math.sin((lt-0.22)*70)*Math.exp(-(lt-0.22)*11); }
    if(id==='phone'&&pt<0.02){ /* reaching: phone still on the nightstand */ }
    else { const side=J1.l; if(!o.tL) o.tL=ph.clone().addScaledVector(side,0.05).addScaledVector(J1.hd,-0.07); if(!o.tR) o.tR=ph.clone().addScaledVector(side,-0.05).addScaledVector(J1.hd,-0.07); } }
  if(id==='up'){ // bolt upright, the alarm line, then flop back down to frame 0
    S.clock='5:00'; S.dawn=0.85; S.alarm=true; const fb=sstep(2.85,3.8,lt); o.pitch=lt<0.18?lerp(1.3,0.02,sm5(lt/0.18)):lerp(0.02,0.75,sm5(fb)); o.nod=lerp(-0.05,0.05,fb); o.roll=0;
    ex=lt<2.85?{...EX.shock,px:0,py:0}:mix(EX.shock,EX.sleepy,sstep(2.85,3.3,lt)); S.zTop=0.05;
    const J0=bodyJ(o); for(const [s,sg] of [['L',1],['R',-1]]) o['t'+s]=J0.hip.clone().addScaledVector(J0.l,sg*0.24).addScaledVector(J0.n,0.12).add(V(0,0.06,0));
    o.tR=J0.neck.clone().addScaledVector(J0.n,0.32).addScaledVector(J0.l,-0.12).add(V(0,-0.1,0)); S.phone={pos:o.tR.clone().addScaledVector(J0.n,0.02),dir:J0.n.clone().negate(),up:V(0,1,0)}; S.phoneOn=true;
    cam=lt<2.85?camLerp('front','front',0):camLerp('front','top',sm5(sstep(2.85,3.8,lt))); if(lt<0.25){ cam[2]-=5*(1-lt/0.25); } }
  // blanket body caps
  const J=bodyJ(o); const sideK=Math.abs(Math.sin(o.roll));
  const legTop=0.6+0.075+0.02*sideK, foot=V(J.hip.x+0.04*Math.sin(o.roll),0,J.hip.z+0.92);
  S.caps=[{a:J.hip,b:foot,r:0.11-0.03*sideK,top:legTop},{a:foot.clone().add(V(0,0,-0.05)),b:foot,r:0.07,top:0.72}];
  if(o.pitch>1.0) S.caps.push({a:J.hip,b:J.neck.clone().addScaledVector(J.d,-0.08),r:0.11-0.02*sideK,top:0.6+0.12+0.03*sideK});
  else S.caps.push({a:J.hip,b:J.hip.clone().add(V(0,0,0.12)),r:0.12,top:0.62});
  return {S,o,ex,cam,J}; }

// ---------------------------------------------------------------- per frame
function setT(t){ let {S,o,ex,cam,J}=state(t); const blink=blinkAt(t,[3.75,5.75,8.9,9.95]);
  const E={...ex}; if(blink>0&&E.eo>0.1) E.eo=Math.min(E.eo,1-blink); FACE.draw(E);
  poseHero(J,o); drape(S.caps,S.zTop,S.wob,t);
  pillow.position.copy(PILLOW0); pillow.rotation.set(0,0,0); if(S.pillow){ pillow.position.copy(S.pillow.pos); pillow.rotation.set(...S.pillow.rot); }
  drawClock(S.clock,1); drawWindow(S.dawn,S.rooster,S.rb||0); dawnLight.intensity=S.dawn*5; winM.color.setScalar(lerp(0.48,0.8,S.dawn));
  PHONE.visible=!!S.phone; if(S.phone) placePhone(S.phone.pos,S.phone.dir,S.phone.up);
  if(S.alarm){ drawAlarm(S.alarmP||0); phoneScreenM.map=alarmTex; } else { phoneScreenM.map=feedTex; drawFeed(S.feedK,S.phoneOn); }
  phoneLight.intensity=S.phoneOn&&S.phone?(S.id==='turn3'?0.5:0.9):0; if(S.phone){ phoneLight.position.copy(S.phone.pos).addScaledVector(S.phone.dir,0.1); const hue=[0x9cc0ff,0xffa0d0,0xffc890,0xa0ffd0][S.feedK%4]; phoneLight.color.setHex(S.alarm?0xffc890:hue); }
  Zs.forEach((z,i)=>{ const u=((t*0.55+i/3)%1); z.visible=S.zzz>0; const base=J.head.clone().add(V(0.12,0.2,0)); z.position.copy(base).add(V(0.08*u+0.03*Math.sin(t*2+i),0.32*u,0)); z.scale.setScalar((0.06+0.07*u)); z.material.opacity=S.zzz*Math.sin(Math.PI*u); });
  ST.tick(t,0); const night=1-S.dawn*0.35; ST.spot.intensity*=night; ST.beamU.uI.value*=night*(S.id==='phone'||S.id==='lapse'||S.id==='laugh'?0.6:1);
  if(window.DBG&&window.DBG.cam){ const c=window.DBG.cam; cam=[V(...c[0]),V(...c[1]),c[2]]; } ST.cam.up.copy(S.camUp||V(0,1,0)); ST.cam.position.copy(cam[0]); ST.cam.fov=cam[2]; ST.cam.updateProjectionMatrix(); ST.cam.lookAt(cam[1]); }
drawWindow(0,false);
window.renderAt=(t,K=3)=>{ const sh=shotAt(t); return ST.renderAt(setT,t,K,{t0:sh.t0,t1:sh.t1,shutter:1/60}); };
window.events={DUR,SHOTS}; window.ready=true;
