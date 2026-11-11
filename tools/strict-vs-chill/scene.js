// Strict vs Chill Parents: Slow Light remake of a split-screen reference reel.
// One bedroom set, rendered twice per frame (?panel=0 strict / ?panel=1 chill) at panel size (1080x558).
// Units metres; floor y=0; back wall face at z=0; camera on +z looking flat at the wall (like the ref).
import * as THREE from 'three';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {UnrealBloomPass} from 'three/addons/postprocessing/UnrealBloomPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';
import {ShaderPass} from 'three/addons/postprocessing/ShaderPass.js';
import * as SLD from './sld.js';
const {V,clamp,sstep,lerp,keys,rng,yawOf,noiseTex,glowSprite,rimify}=SLD;

const Q=new URLSearchParams(location.search);
const W=+Q.get('w')||1080, H=+Q.get('h')||558, PANEL=+Q.get('panel')||0;
const DUR=11.2;

// ------------------------------------------------------------------ renderer / camera / post
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true}); renderer.setPixelRatio(1); renderer.setSize(W,H);
renderer.shadowMap.enabled=true; renderer.shadowMap.type=THREE.PCFSoftShadowMap; renderer.shadowMap.autoUpdate=false;
renderer.toneMapping=THREE.ACESFilmicToneMapping; renderer.toneMappingExposure=1.0; document.body.appendChild(renderer.domElement);
const scene=new THREE.Scene(); scene.background=new THREE.Color(0x0b1020);
const cam=new THREE.PerspectiveCamera(16.6,W/H,0.5,60); cam.position.set(0,1.75,14); cam.lookAt(0,1.6,0);

// ------------------------------------------------------------------ materials / textures
const canvasTex=(w,h,draw,srgb=true)=>{ const c=document.createElement('canvas'); c.width=w; c.height=h; draw(c.getContext('2d'),w,h); const t=new THREE.CanvasTexture(c); if(srgb) t.colorSpace=THREE.SRGBColorSpace; t.anisotropy=4; return t; };
const std=(color,o={})=>new THREE.MeshStandardMaterial({color,roughness:o.r??0.8,metalness:0,...o.x});
const WALL_C=0x46506e, TRIM_C=0x8d93a6, WOOD_C=0x5a3f2c, WOOD_D=0x3e2b1f;
const wallTex=noiseTex(256,3,128,26,60,0.05); wallTex.repeat.set(6,4);
const wallMat=new THREE.MeshStandardMaterial({color:WALL_C,roughness:0.92,map:wallTex});
const woodTex=noiseTex(256,9,128,60,30,0.1); woodTex.repeat.set(2,2);
const woodMat=new THREE.MeshStandardMaterial({color:WOOD_C,roughness:0.6,map:woodTex});
const woodDark=new THREE.MeshStandardMaterial({color:WOOD_D,roughness:0.65,map:woodTex});
const trimMat=std(TRIM_C,{r:0.55});
const floorTex=canvasTex(1024,256,(g,w,h)=>{ const R=rng(4); g.fillStyle='#6b4a33'; g.fillRect(0,0,w,h);
  for(let row=0;row<8;row++){ let x=-R()*200; while(x<w){ const L=150+R()*260; const v=R(); g.fillStyle=`rgb(${100+v*30|0},${68+v*22|0},${46+v*16|0})`; g.fillRect(x+2,row*32+2,L-4,28);
      for(let k=0;k<6;k++){ g.fillStyle=`rgba(40,25,15,${0.05+R()*0.08})`; g.fillRect(x+R()*L,row*32+4+R()*22,40+R()*90,1.5); } x+=L; } }
  g.fillStyle='rgba(20,12,8,0.9)'; for(let row=0;row<=8;row++) g.fillRect(0,row*32-1,w,2); });
floorTex.wrapS=floorTex.wrapT=THREE.RepeatWrapping; floorTex.repeat.set(3,3);
const box=(w,h,d,mat,x,y,z,parent=scene,cast=true)=>{ const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat); m.position.set(x,y,z); m.castShadow=cast; m.receiveShadow=true; parent.add(m); return m; };
// box by extents
const boxE=(x0,x1,y0,y1,z0,z1,mat,parent=scene,cast=true)=>box(x1-x0,y1-y0,z1-z0,mat,(x0+x1)/2,(y0+y1)/2,(z0+z1)/2,parent,cast);

// ------------------------------------------------------------------ geometry constants
const WIN={x0:-1.85,x1:-0.45,y0:1.0,y1:2.78}, WINX=(WIN.x0+WIN.x1)/2;
const DOOR={x0:1.6,x1:2.65,y1:2.82}, DOORX=(DOOR.x0+DOOR.x1)/2;
const MAT_TOP=0.62, BED={x0:-2.55,x1:-0.05,z0:0.0,z1:1.45};
const LAMP_P=V(0.5,1.02,0.28);

// ------------------------------------------------------------------ the room
// floor
{ const f=new THREE.Mesh(new THREE.PlaneGeometry(14,8),new THREE.MeshStandardMaterial({color:0xffffff,map:floorTex,roughness:0.55,metalness:0}));
  f.rotation.x=-Math.PI/2; f.position.set(0,0,2); f.receiveShadow=true; scene.add(f); }
// back wall with window + door openings (thickness 0.16)
const WZ0=-0.16, WZ1=0;
[[-7,WIN.x0,0,4.5],[WIN.x1,DOOR.x0,0,4.5],[DOOR.x1,7,0,4.5],[WIN.x0,WIN.x1,0,WIN.y0],[WIN.x0,WIN.x1,WIN.y1,4.5],[DOOR.x0,DOOR.x1,DOOR.y1,4.5]]
  .forEach(([a,b,c,d])=>boxE(a,b,c,d,WZ0,WZ1,wallMat));
// baseboard + crown
boxE(-7,DOOR.x0-0.08,0,0.13,0,0.025,trimMat); boxE(DOOR.x1+0.08,7,0,0.13,0,0.025,trimMat);
// window: casing, sill, upper sash fixed, lower sash slides
const winG=new THREE.Group(); scene.add(winG);
{ const t=0.09; boxE(WIN.x0-t,WIN.x0,WIN.y0-0.05,WIN.y1+t,0,0.04,trimMat); boxE(WIN.x1,WIN.x1+t,WIN.y0-0.05,WIN.y1+t,0,0.04,trimMat);
  boxE(WIN.x0-t,WIN.x1+t,WIN.y1,WIN.y1+t,0,0.04,trimMat); boxE(WIN.x0-0.16,WIN.x1+0.16,WIN.y0-0.07,WIN.y0,-0.16,0.12,trimMat); }
const sashMat=std(0x9aa0b2,{r:0.5});
const glassMat=new THREE.MeshBasicMaterial({color:0x9fb6e6,transparent:true,opacity:0.07,depthWrite:false});
function sash(y0,y1,z){ const g=new THREE.Group(); const t=0.045; const w=WIN.x1-WIN.x0;
  boxE(WIN.x0,WIN.x1,y0,y0+t,z-0.02,z+0.02,sashMat,g); boxE(WIN.x0,WIN.x1,y1-t,y1,z-0.02,z+0.02,sashMat,g);
  boxE(WIN.x0,WIN.x0+t,y0,y1,z-0.02,z+0.02,sashMat,g); boxE(WIN.x1-t,WIN.x1,y0,y1,z-0.02,z+0.02,sashMat,g);
  boxE(WINX-0.015,WINX+0.015,y0,y1,z-0.015,z+0.015,sashMat,g); boxE(WIN.x0,WIN.x1,(y0+y1)/2-0.015,(y0+y1)/2+0.015,z-0.015,z+0.015,sashMat,g);
  const gl=new THREE.Mesh(new THREE.PlaneGeometry(w,y1-y0),glassMat); gl.position.set(WINX,(y0+y1)/2,z); g.add(gl); winG.add(g); return g; }
const WMID=(WIN.y0+WIN.y1)/2;
sash(WMID-0.02,WIN.y1,-0.11);
const lowSash=sash(WIN.y0,WMID+0.02,-0.06);
// night sky + city behind the window (unlit)
{ const tex=canvasTex(1024,1152,(g,w,h)=>{ const R=rng(11);
    const gr=g.createLinearGradient(0,0,0,h); gr.addColorStop(0,'#0d1630'); gr.addColorStop(0.6,'#1b2a52'); gr.addColorStop(1,'#33406a'); g.fillStyle=gr; g.fillRect(0,0,w,h);
    for(let i=0;i<260;i++){ const a=R(); g.fillStyle=`rgba(235,230,214,${0.25+a*0.7})`; const s=R()<0.92?1.2:2.4; g.fillRect(R()*w,R()*h*0.62,s,s); }
    // crescent moon
    const mx=w*0.33, my=h*0.36, mr=38; const halo=g.createRadialGradient(mx,my,mr*0.6,mx,my,mr*4); halo.addColorStop(0,'rgba(240,232,210,0.35)'); halo.addColorStop(1,'rgba(240,232,210,0)'); g.fillStyle=halo; g.fillRect(0,0,w,h);
    { const mc=document.createElement('canvas'); mc.width=mc.height=128; const q=mc.getContext('2d'); q.fillStyle='#f3ead4'; q.beginPath(); q.arc(64,64,mr,0,7); q.fill(); q.globalCompositeOperation='destination-out'; q.beginPath(); q.arc(64+17,64-11,mr*0.9,0,7); q.fill(); g.drawImage(mc,mx-64,my-64); }
    // skyline: two layers
    for(const [base,col,lit,hmin,hmax] of [[h*0.73,'#18213c',0.12,90,230],[h*0.80,'#0c1226',0.28,60,300]]){ let x=-20; while(x<w){ const bw=40+R()*90, bh=hmin+R()*(hmax-hmin); g.fillStyle=col; g.fillRect(x,base-bh,bw,h-base+bh);
        for(let wy=base-bh+10;wy<base+40;wy+=14) for(let wx=x+6;wx<x+bw-8;wx+=11) if(R()<lit){ const warm=R()<0.8; g.fillStyle=warm?`rgba(255,${180+R()*40|0},${90+R()*40|0},${0.55+R()*0.45})`:'rgba(200,220,255,0.6)'; g.fillRect(wx,wy,5,7); }
        x+=bw+R()*8; } } });
  const m=new THREE.Mesh(new THREE.PlaneGeometry(4.0,4.5),new THREE.MeshBasicMaterial({map:tex,fog:false}));
  m.position.set(-1.6,2.0,-5); scene.add(m); }
// curtains (folded planes) + rod
const curtMat=new THREE.MeshStandardMaterial({color:0x3b4f86,roughness:0.95,side:THREE.DoubleSide});
function curtain(xc,w){ const g=new THREE.PlaneGeometry(w,2.15,40,1); const p=g.attributes.position; for(let i=0;i<p.count;i++){ const x=p.getX(i); p.setZ(i,0.035*Math.sin(x/w*Math.PI*7)); } g.computeVertexNormals();
  const m=new THREE.Mesh(g,curtMat); m.position.set(xc,WIN.y1+0.12-1.075,0.13); m.castShadow=true; m.receiveShadow=true; scene.add(m); return m; }
curtain(WIN.x0-0.2,0.42); curtain(WIN.x1+0.2,0.42);
boxE(WIN.x0-0.5,WIN.x1+0.5,WIN.y1+0.13,WIN.y1+0.16,0.1,0.15,std(0x2a2422,{r:0.4}));
// door casing + hallway + door panel on a hinge at the right edge (opens toward the camera)
{ const t=0.09; boxE(DOOR.x0-t,DOOR.x0,0,DOOR.y1+t,0,0.04,trimMat); boxE(DOOR.x1,DOOR.x1+t,0,DOOR.y1+t,0,0.04,trimMat); boxE(DOOR.x0-t,DOOR.x1+t,DOOR.y1,DOOR.y1+t,0,0.04,trimMat); }
const hallMat=new THREE.MeshStandardMaterial({color:0xcdb89a,roughness:0.9});
{ boxE(0.6,3.6,0,3.2,-2.9,-2.8,hallMat); boxE(0.6,3.6,3.0,3.1,-2.8,-0.16,hallMat); boxE(3.1,3.2,0,3.2,-2.8,-0.16,hallMat);
  const hf=new THREE.Mesh(new THREE.PlaneGeometry(3,2.7),new THREE.MeshStandardMaterial({color:0xffffff,map:floorTex,roughness:0.6})); hf.rotation.x=-Math.PI/2; hf.position.set(2.1,0.001,-1.5); hf.receiveShadow=true; scene.add(hf);
  // a framed picture in the hall
  boxE(1.75,2.45,1.35,1.9,-2.8,-2.76,woodDark); }
const doorPivot=new THREE.Group(); doorPivot.position.set(DOOR.x1-0.005,0,-0.035); scene.add(doorPivot);
const doorMat=new THREE.MeshStandardMaterial({color:0x4a3a30,roughness:0.6,map:woodTex});
{ const w=DOOR.x1-DOOR.x0-0.01; box(w,DOOR.y1-0.03,0.05,doorMat,-w/2,(DOOR.y1-0.03)/2+0.02,0,doorPivot);
  for(const [y0,y1] of [[0.25,1.25],[1.5,2.6]]) box(w*0.7,y1-y0,0.02,std(0x56443a,{r:0.55}),-w/2,(y0+y1)/2,0.03,doorPivot);
  const knob=new THREE.Mesh(new THREE.SphereGeometry(0.035,16,10),new THREE.MeshStandardMaterial({color:0xd8b26a,roughness:0.3,metalness:0.8})); knob.position.set(-w+0.09,1.0,0.06); doorPivot.add(knob); }
// light leak under the closed door + floor glow
const leakMat=new THREE.MeshBasicMaterial({color:0xffc98a,transparent:true,opacity:1,fog:false});
const leak=new THREE.Mesh(new THREE.PlaneGeometry(DOOR.x1-DOOR.x0,0.022),leakMat); leak.position.set(DOORX,0.011,0.01); scene.add(leak);
const leakGlowTex=canvasTex(256,64,(g,w,h)=>{ const gr=g.createLinearGradient(0,0,0,h); gr.addColorStop(0,'rgba(255,200,140,0.9)'); gr.addColorStop(1,'rgba(255,200,140,0)'); g.fillStyle=gr; g.fillRect(0,0,w,h);
  const m=g.createLinearGradient(0,0,w,0); m.addColorStop(0,'rgba(0,0,0,1)'); m.addColorStop(0.15,'rgba(0,0,0,0)'); m.addColorStop(0.85,'rgba(0,0,0,0)'); m.addColorStop(1,'rgba(0,0,0,1)'); g.globalCompositeOperation='destination-out'; g.fillStyle=m; g.fillRect(0,0,w,h); });
const leakGlowMat=new THREE.MeshBasicMaterial({map:leakGlowTex,transparent:true,opacity:0.5,depthWrite:false,blending:THREE.AdditiveBlending});
const leakGlow=new THREE.Mesh(new THREE.PlaneGeometry(1.3,0.7),leakGlowMat); leakGlow.rotation.x=-Math.PI/2; leakGlow.position.set(DOORX,0.004,0.35); scene.add(leakGlow);
// dresser + picture + bits
{ boxE(-3.55,-2.45,0,0.95,0.0,0.5,woodMat); for(let i=0;i<3;i++) boxE(-3.48,-2.52,0.08+i*0.29,0.33+i*0.29,0.5,0.53,woodDark);
  for(let i=0;i<3;i++) for(const kx of [-3.25,-2.75]){ const k=new THREE.Mesh(new THREE.SphereGeometry(0.022,10,8),std(0xd8b26a,{r:0.3,x:{metalness:0.7}})); k.position.set(kx,0.205+i*0.29,0.55); scene.add(k); }
  const pic=canvasTex(256,240,(g,w,h)=>{ g.fillStyle='#1e2847'; g.fillRect(0,0,w,h); const gr=g.createRadialGradient(170,70,4,170,70,60); gr.addColorStop(0,'rgba(255,190,100,0.95)'); gr.addColorStop(0.3,'rgba(255,178,77,0.5)'); gr.addColorStop(1,'rgba(255,178,77,0)'); g.fillStyle=gr; g.fillRect(0,0,w,h);
    g.fillStyle='#ffd08a'; g.beginPath(); g.arc(170,70,14,0,7); g.fill(); g.fillStyle='#3a4670'; g.beginPath(); g.moveTo(0,h); g.lineTo(80,110); g.lineTo(150,190); g.lineTo(200,140); g.lineTo(w,200); g.lineTo(w,h); g.fill();
    g.fillStyle='#2a3458'; g.beginPath(); g.moveTo(0,h); g.lineTo(60,180); g.lineTo(130,h); g.fill(); });
  boxE(-3.3,-2.6,1.5,2.15,0,0.035,woodDark); const pm=new THREE.Mesh(new THREE.PlaneGeometry(0.6,0.55),new THREE.MeshStandardMaterial({map:pic,roughness:0.7,emissive:0xffffff,emissiveMap:pic,emissiveIntensity:0.08})); pm.position.set(-2.95,1.825,0.04); scene.add(pm);
  // books + a small clock radio silhouette + globe
  [[0x7a3b2e,0.05],[0x2f4a6a,0.04],[0xb08a4a,0.045]].forEach(([c,t],i)=>boxE(-3.45,-3.12,0.95+i*0.05,0.95+i*0.05+t,0.12,0.38,std(c,{r:0.7})));
  const gl=new THREE.Mesh(new THREE.SphereGeometry(0.13,24,16),std(0x3f6f7a,{r:0.5})); gl.position.set(-2.72,1.18,0.25); gl.castShadow=true; scene.add(gl); boxE(-2.76,-2.68,0.95,1.05,0.21,0.29,woodDark); }
// bed
const blanketTex=canvasTex(512,128,(g,w,h)=>{ g.fillStyle='#4f66a8'; g.fillRect(0,0,w,h); for(let x=0;x<w;x+=32){ g.fillStyle='#3d5292'; g.fillRect(x,0,14,h); g.fillStyle='rgba(255,255,255,0.05)'; g.fillRect(x+14,0,2,h); } });
{ boxE(BED.x0,BED.x1-0.08,0.18,0.36,BED.z0+0.05,BED.z1,woodMat);           // frame
  boxE(BED.x0+0.03,BED.x1-0.1,0.36,0.55,BED.z0+0.07,BED.z1-0.03,std(0xd9d2c2,{r:0.9}));  // mattress
  const bl=boxE(BED.x0,BED.x1-0.52,0.48,MAT_TOP,BED.z0+0.05,BED.z1+0.04,new THREE.MeshStandardMaterial({color:0xffffff,map:blanketTex,roughness:0.95}));
  boxE(BED.x0-0.005,BED.x1-0.52,0.2,0.5,BED.z1+0.0,BED.z1+0.05,new THREE.MeshStandardMaterial({color:0xffffff,map:blanketTex,roughness:0.95}));  // blanket overhang
  const pil=new THREE.Mesh(new THREE.CapsuleGeometry(0.12,0.75,6,16),std(0xe9e3d4,{r:0.9})); pil.rotation.x=Math.PI/2; pil.scale.set(1.6,1,0.75); pil.position.set(-0.36,MAT_TOP+0.03,0.6); pil.castShadow=true; scene.add(pil);
  boxE(BED.x1-0.08,BED.x1+0.04,0,1.18,BED.z0,BED.z1,woodDark);   // headboard (right end)
  boxE(BED.x0-0.1,BED.x0,0,0.82,BED.z0,BED.z1,woodDark);         // footboard
  for(const z of [0.06,1.4]) for(const x of [BED.x0+0.1,BED.x1-0.2]) boxE(x-0.03,x+0.03,0,0.18,z-0.03,z+0.03,woodDark); }
// nightstand + lamp
const shadeMat=new THREE.MeshStandardMaterial({color:0xe9dcc0,roughness:0.8,emissive:0xffb24d,emissiveIntensity:0,side:THREE.DoubleSide});
{ boxE(0.2,0.8,0,0.62,0.05,0.5,woodMat); boxE(0.25,0.75,0.36,0.56,0.5,0.52,woodDark);
  const base=new THREE.Mesh(new THREE.CylinderGeometry(0.07,0.09,0.06,20),std(0x9aa0aa,{r:0.4,x:{metalness:0.5}})); base.position.set(LAMP_P.x,0.65,LAMP_P.z); scene.add(base);
  const stem=new THREE.Mesh(new THREE.CylinderGeometry(0.012,0.012,0.26,8),std(0x9aa0aa,{r:0.4})); stem.position.set(LAMP_P.x,0.79,LAMP_P.z); scene.add(stem);
  const shade=new THREE.Mesh(new THREE.CylinderGeometry(0.09,0.16,0.2,24,1,true),shadeMat); shade.position.set(LAMP_P.x,0.98,LAMP_P.z); scene.add(shade); }
// rug
{ const rt=canvasTex(512,256,(g,w,h)=>{ g.fillStyle='#4a3a4e'; g.beginPath(); g.ellipse(w/2,h/2,w/2-2,h/2-2,0,0,7); g.fill(); g.strokeStyle='#6a5670'; g.lineWidth=10; g.beginPath(); g.ellipse(w/2,h/2,w/2-26,h/2-22,0,0,7); g.stroke(); });
  const r=new THREE.Mesh(new THREE.PlaneGeometry(2.6,1.0),new THREE.MeshStandardMaterial({map:rt,transparent:true,roughness:1})); r.rotation.x=-Math.PI/2; r.position.set(-0.4,0.003,1.95); r.receiveShadow=true; scene.add(r); }

// ------------------------------------------------------------------ lights
const hemi=new THREE.HemisphereLight(0x8090c8,0x4a3a2c,2.6); scene.add(hemi);
const amb=new THREE.AmbientLight(0x4a5888,0.9); scene.add(amb);
// moonlight through the window: cool spot from outside, wall/sash cast the window pattern
const moon=new THREE.SpotLight(0xa9bff0,50,0,0.42,0.6,1.3); moon.position.set(WINX-0.6,6.2,-2.6); moon.target.position.set(-0.7,0,0.9);
moon.castShadow=true; moon.shadow.mapSize.set(2048,2048); moon.shadow.bias=-0.0004; moon.shadow.camera.near=1; moon.shadow.camera.far=14; scene.add(moon,moon.target);
// hallway light: warm, enters the room only through the doorway
const hall=new THREE.SpotLight(0xffc27a,38,0,0.75,0.7,1.4); hall.position.set(DOORX+0.2,2.85,-2.2); hall.target.position.set(DOORX-0.6,0,2.4);
hall.castShadow=true; hall.shadow.mapSize.set(1024,1024); hall.shadow.bias=-0.0004; hall.shadow.camera.near=0.5; hall.shadow.camera.far=12; scene.add(hall,hall.target);
const hallFill=new THREE.PointLight(0xffc890,8,0,1.6); hallFill.position.set(DOORX,2.6,-1.7); scene.add(hallFill);
const hallGlow=glowSprite(scene,0xffd9a0,0.5); hallGlow.position.set(DOORX,2.95,-2.0); hallGlow.scale.set(1.2,0.6,1);
// bedside lamp
const lamp=new THREE.PointLight(0xffb24d,0,0,1.6); lamp.position.copy(LAMP_P).add(V(0,-0.02,0.02)); lamp.castShadow=true; lamp.shadow.mapSize.set(512,512); lamp.shadow.bias=-0.002; lamp.shadow.camera.near=0.1; scene.add(lamp);
const lampGlow=glowSprite(scene,0xffc070,0); lampGlow.position.copy(LAMP_P).add(V(0,0,0.15)); lampGlow.scale.set(1.6,1.6,1);

// ------------------------------------------------------------------ figures
const RK=SLD.createRig(scene,0.86), RP=SLD.createRig(scene,1.0);
const kid=RK.makeFig(SLD.PAL.CREAM,'kid',{rim:0.24,lift:0.2});
const par=RP.makeFig(0x6c7282,'par',{rim:0.22,rimCol:0xc8d4f0,lift:0.08});

// ------------------------------------------------------------------ choreography helpers
const Y_R=0, Y_CAM=-Math.PI/2, Y_L=-Math.PI, Y_WALL=Math.PI/2, Y_WALLm=-1.5*Math.PI;
const ZW=1.9;                                    // walking lane
const P=RK.POSES;
// position track: [[t,x,y,z],...] smoothstep between keys
const track=(K,t)=>V(keys(K.map(k=>[k[0],k[1]]),t),keys(K.map(k=>[k[0],k[2]]),t),keys(K.map(k=>[k[0],k[3]]),t));
// gait phase from horizontal path length (numerical, pure)
function walkInfo(K,t,stride){ let len=0, prev=track(K,0); const dt=1/120; for(let s=dt;s<=t+1e-9;s+=dt){ const p=track(K,s); if(p.y===prev.y||Math.abs(p.y-prev.y)<0.002) len+=Math.hypot(p.x-prev.x,p.z-prev.z); prev=p; }
  const a=track(K,t-0.04), b=track(K,t+0.04); const sp=Math.hypot(b.x-a.x,b.z-a.z)/0.08; return {ph:len/stride*Math.PI*2, amp:clamp(sp/0.9)}; }
// pose track: [[t,pose],...] blended with smoothstep
function poseAt(K,t){ if(t<=K[0][0]) return K[0][1]; for(let i=1;i<K.length;i++) if(t<=K[i][0]){ const u=sstep(K[i-1][0],K[i][0],t); return RK.blend(K[i-1][1],K[i][1],u); } return K[K.length-1][1]; }
const fade=(t,a,b)=>clamp((t-a)/(b-a));
// bed-edge sit, facing camera: hips on the mattress edge
const bedsit=sc=>({...P.stand,p:0.12,tilt:0.05,aL:1.5,aR:1.42,kL:1.5,kR:1.42,dy:0.69-(0.49*sc+0.035),sL:0.35,sR:0.35,eL:0.9,eR:0.9});
const SIT_Z=sc=>1.3+0.275*sc;
const stand=(o={})=>({...P.stand,...o});

// ------------------------------------------------------------------ STRICT (panel 0)
function strict(t){
  // kid
  const kK=[[0,0.55,0,ZW],[2.0,0.55,0,ZW],[2.65,WINX+0.05,0,ZW],[2.95,WINX,MAT_TOP,0.85],[3.1,WINX,MAT_TOP,0.6],[3.35,WINX,1.0,-0.7],[3.7,WINX,-1.6,-0.9],
            [5.9,WINX,-1.6,-0.9],[6.15,WINX,1.0,-0.7],[6.5,WINX,MAT_TOP,0.65],[6.75,WINX-0.12,MAT_TOP,0.85]];
  const kp=track(kK,t); const kw=walkInfo(kK,t,1.15);
  let kyaw=keys([[0,Y_R],[1.75,Y_R],[2.0,Y_L],[2.65,Y_L],[2.85,-1.5*Math.PI],[6.2,-1.5*Math.PI],[6.6,-2*Math.PI],[6.8,-2*Math.PI]],t);
  let kpose=poseAt([[0,stand({sR:0.3,eR:0.6})],[0.9,stand({sR:0.6,eR:1.1})],[1.4,stand()],[1.9,stand({p:0.12,tilt:0.18})],[2.0,stand()],[2.65,stand()],
                    [2.8,P.crouch],[2.95,stand({sL:2.6,sR:2.6,eL:0.3,eR:0.3})],[3.1,stand({sL:2.4,sR:2.4,eL:0.4,eR:0.4})],[3.3,P.crouch],[6.15,P.crouch],[6.5,P.crouch],
                    [6.7,stand()],[6.85,stand({sL:2.7,sR:-0.3,eL:0.2,dy:0.06})],[7.1,stand({sL:0.4,sR:0.1})],[7.9,stand({sL:0.3})],[8.1,stand({sL:0.55,sR:0.5,eL:1.1,eR:1.0,tilt:-0.08,dy:0.03})],[8.35,stand({sL:0.3,sR:0.25,eL:0.5,eR:0.4,tilt:0.05})],[9.4,stand({sL:0.15,sR:0.1,eL:0.2,eR:0.2,tilt:0.28,p:0.1})],[11.2,stand({sL:0.1,sR:0.05,eL:0.15,eR:0.15,tilt:0.36,p:0.12})]],t);
  if(kw.amp>0.02 && kp.y<0.01) kpose=RK.gait(kpose,kw.ph,kw.amp);
  // parent
  const pK=[[0,DOORX-0.1,0,-0.3],[1.2,DOORX-0.1,0,-0.3],[1.55,DOORX+0.1,0,-1.6],[3.6,DOORX+0.1,0,-1.6],[3.85,DOORX-0.1,0,0.4],[4.05,1.0,0,ZW-0.15],[4.45,WINX+0.5,0,1.75],[4.8,WINX+0.5,0,1.75],[5.1,-0.32,0,SIT_Z(1)]];
  const pp=track(pK,t); const pw=walkInfo(pK,t,1.3);
  const sitP=bedsit(1);
  let pyaw=keys([[0,Y_L],[1.15,Y_L],[1.35,Y_WALLm],[1.6,Y_WALLm],[3.55,Y_WALLm-0.0],[3.6,Y_CAM-2*Math.PI],[3.95,Y_L],[4.4,Y_L],[4.55,-Math.PI*1.5],[4.85,-Math.PI*1.5],[5.0,Y_CAM-2*Math.PI]],t);
  let ppose=poseAt([[0,stand({sL:0.1})],[0.6,stand()],[0.75,stand({sL:0.5,eL:1.6,p:0.1})],[1.15,stand({sL:0.4,eL:1.4,p:0.1})],[1.3,stand()],
                    [4.05,stand()],[4.2,stand({sL:0.9,sR:0.9,eL:1.2,eR:1.2,dy:0.0,p:-0.05})],[4.7,stand({sL:0.6,sR:0.6,eL:1.6,eR:1.6,tilt:0.15})],[4.85,stand()],[5.1,sitP],
                    [5.5,{...sitP,p:0.5,tilt:0.4}],[6.2,{...sitP,p:0.55,tilt:0.42}],[6.4,{...sitP,p:0.25,tilt:0.0,ty:0.5}],[6.55,{...sitP,p:0.25,ty:0.4}],[6.9,{...sitP,p:0.18,ty:-0.5,hy:-0.3}],[9.5,{...sitP,p:0.25,ty:-0.55,hy:-0.35,tilt:0.15}],[11.2,{...sitP,p:0.32,ty:-0.55,hy:-0.4,tilt:0.25}]],t);
  if(t>5.0 && t<6.25){ ppose=SLD.lerp?ppose:ppose; ppose=RP.handsOnKnees(ppose,pp,pyaw,0); }
  // lamp reach: right arm out to the lamp at 6.35-6.6
  const reach=sstep(6.15,6.4,t)*(1-sstep(6.75,7.1,t));
  if(reach>0){ ppose={...ppose,tR:LAMP_P.clone().add(V(-0.05,-0.25,0.05)),wR:reach,pR:V(0,-0.5,-1)}; }
  if(pw.amp>0.02 && t<5.0) ppose=RP.gait(ppose,pw.ph,pw.amp);
  // states
  const door=keys([[0,1.25],[1.25,1.25],[1.75,0],[3.55,0],[3.85,1.3],[4.6,1.3],[5.3,0]],t);
  const sashUp=keys([[0,0],[2.9,0],[3.1,0.8],[11.2,0.8]],t);
  const lampOn=t>=6.42?1:0;
  return {kp,kyaw,kpose,ka:1,pp,pyaw,ppose,pa:1,door,sashUp,lampOn,hallOn:1};
}

// ------------------------------------------------------------------ CHILL (panel 1)
function chill(t){
  const sk=bedsit(0.86);
  const kK=[[0,0.55,0,ZW],[1.2,0.55,0,ZW],[1.7,DOORX-0.3,0,ZW-0.6],[2.15,DOORX-0.1,0,-1.0],[2.4,DOORX-0.9,0,-1.6],
            [4.3,DOORX-0.9,0,-1.6],[4.45,DOORX-0.1,0,-0.6],[4.85,DOORX-0.4,0,ZW],[5.45,-1.05,0,ZW],[5.75,-1.05,0,SIT_Z(0.86)],
            [9.3,-1.05,0,SIT_Z(0.86)],[9.75,-1.25,MAT_TOP,0.75]];
  const kp=track(kK,t); const kw=walkInfo(kK,t,1.15);
  let kyaw=keys([[0,Y_R],[1.2,Y_R],[1.55,Y_R],[1.75,Y_WALL],[2.2,Y_WALL],[2.35,Math.PI],[4.3,Math.PI],[4.4,Y_CAM+2*Math.PI],[4.85,Y_CAM+2*Math.PI],[5.0,Math.PI],[5.4,Math.PI],[5.7,Y_CAM+2*Math.PI],[9.3,Y_CAM+2*Math.PI],[9.7,Y_CAM+2*Math.PI-0.25]],t);
  const talk=(s,a,b,c)=>({...sk,ty:0.35,hy:0.25,p:0.1,sL:a,eL:b,sR:c,eR:1.2,dy:sk.dy+0.0});
  let kpose=poseAt([[0,stand({sR:0.3,eR:0.6})],[0.9,stand({sR:0.6,eR:1.1})],[1.1,stand({sR:0.2,eR:0.4,dy:0.04})],[1.3,stand()],[5.5,stand()],[5.75,sk],
                    [6.0,talk(0,1.6,1.4,0.4)],[6.35,talk(0,2.4,0.6,1.0)],[6.7,talk(0,1.2,1.6,1.8)],[7.05,talk(0,2.6,0.3,0.6)],[7.4,talk(0,1.0,1.8,1.6)],[7.75,talk(0,2.2,0.8,0.5)],[8.1,talk(0,1.4,1.5,1.4)],
                    [8.4,{...sk,ty:0.2,hy:0.15,p:0.05,tilt:-0.2}],[9.3,{...sk,ty:0.0,p:0.1}],[9.75,{...P.sit,p:0.3,tilt:0.25}],[11.2,{...P.sit,p:0.38,tilt:0.35}]],t);
  if(t>9.3){ kpose=RK.handsOnKnees(kpose,kp,kyaw,sstep(9.3,9.9,t)); }
  if(kw.amp>0.02 && kp.y<0.01 && t<5.6) kpose=RK.gait(kpose,kw.ph,kw.amp);
  const sp=bedsit(1);
  const pK=[[0,DOORX-0.1,0,-0.3],[1.25,DOORX-0.1,0,-0.3],[1.55,DOORX+0.3,0,-0.9],[2.05,DOORX+0.3,0,-0.9],[2.45,DOORX-0.9,0,-1.7],
            [4.45,DOORX-0.9,0,-1.7],[4.6,DOORX-0.1,0,-1.0],[5.0,DOORX-0.1,0,0.6],[5.25,1.0,0,ZW],[5.75,-0.42,0,ZW],[6.0,-0.42,0,SIT_Z(1)],
            [8.3,-0.42,0,SIT_Z(1)],[8.55,-0.42,0,ZW],[9.1,DOORX-0.1,0,0.5],[9.5,DOORX-0.1,0,-0.8],[9.9,DOORX-0.9,0,-1.7]];
  const pp=track(pK,t); const pw=walkInfo(pK,t,1.3);
  let pyaw=keys([[0,Y_L],[1.25,Y_L],[1.35,Y_WALLm],[2.05,Y_WALLm],[2.45,Y_L],[4.45,Y_L],[4.55,Y_CAM-2*Math.PI],[5.0,Y_CAM-2*Math.PI],[5.2,Y_L],[5.6,Y_L],[5.9,Y_CAM-2*Math.PI],
                 [8.3,Y_CAM-2*Math.PI],[8.5,-2*Math.PI],[9.0,-2*Math.PI],[9.2,Y_WALLm-2*Math.PI],[9.6,Y_WALLm-2*Math.PI],[9.9,Y_L-2*Math.PI]],t);
  const listen=(n)=>({...sp,ty:-0.4,hy:-0.3,p:0.15,tilt:n,sL:0.4,eL:0.9});
  let ppose=poseAt([[0,stand({sL:0.1})],[0.9,stand()],[1.05,stand({sL:2.5,eL:0.3,p:-0.05})],[1.3,stand({sL:2.2,eL:0.6})],[1.5,stand()],
                    [4.6,stand()],[4.75,stand({sR:0.6,eR:1.2})],[5.0,stand({sR:0.5,eR:1.2})],[5.3,stand()],[5.75,stand()],[6.0,sp],
                    [6.3,listen(0.05)],[6.6,listen(0.22)],[6.9,listen(0.02)],[7.2,listen(0.25)],[7.5,{...listen(-0.15),p:-0.05}],[7.8,listen(0.2)],[8.1,listen(0.05)],[8.3,sp],[8.55,stand({sL:1.9,eL:0.4})],[8.8,stand()],[9.9,stand()]],t);
  // pat on the head as he gets up
  const pat=sstep(8.35,8.5,t)*(1-sstep(8.75,8.95,t));
  if(pat>0){ const KJ=RK.skel(kpose,kp,kyaw); ppose={...ppose,tL:KJ.head.clone().add(V(0,0.12,0)),wL:pat,pL:V(0,-0.4,1)}; }
  if(pw.amp>0.02 && (t<5.9 || t>8.4)) ppose=RP.gait(ppose,pw.ph,pw.amp);
  // lamp switched on by the parent as they sit
  const reach=sstep(5.75,5.95,t)*(1-sstep(6.1,6.3,t));
  if(reach>0) ppose={...ppose,tR:LAMP_P.clone().add(V(-0.05,-0.25,0.05)),wR:reach,pR:V(0,-0.5,-1)};
  const door=keys([[0,1.25],[1.3,1.25],[1.45,1.6],[2.4,1.6],[2.85,0],[4.2,0],[4.45,1.4],[11.2,1.4]],t);
  const lampOn=t>=5.95?1:0;
  const ka=t<2.3?1:t<4.35?0:1, pa=t<2.4?1:t<4.5?0:(t<9.8?1:1-fade(t,9.8,10.0));
  return {kp,kyaw,kpose,ka,pp,pyaw,ppose,pa,door,sashUp:0,lampOn,hallOn:1};
}

// ------------------------------------------------------------------ frame
function setState(t){
  const s=PANEL===0?strict(t):chill(t);
  RK.poseFig(kid,RK.skel(s.kpose,s.kp,s.kyaw)); kid.setAlpha(s.ka);
  RP.poseFig(par,RP.skel(s.ppose,s.pp,s.pyaw)); par.setAlpha(s.pa);
  doorPivot.rotation.y=s.door;
  lowSash.position.y=s.sashUp;
  const closed=1-clamp(s.door/0.12);
  leakMat.opacity=closed; leakGlowMat.opacity=0.55*closed+0.0;
  lamp.intensity=s.lampOn*5.0; shadeMat.emissiveIntensity=s.lampOn*2.2; lampGlow.material.opacity=s.lampOn*0.55;
  return s;
}
const acc=document.createElement('canvas'); acc.width=W; acc.height=H; const actx=acc.getContext('2d');
const composer=new EffectComposer(renderer); composer.setSize(W,H); composer.addPass(new RenderPass(scene,cam));
const bloom=new UnrealBloomPass(new THREE.Vector2(W,H),0.5,0.55,0.82); composer.addPass(bloom);
const grade=new ShaderPass({uniforms:{tDiffuse:{value:null},uT:{value:0},uAsp:{value:W/H},uFade:{value:1}},
  vertexShader:`varying vec2 vU; void main(){ vU=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
  fragmentShader:`varying vec2 vU; uniform sampler2D tDiffuse; uniform float uT,uAsp,uFade;
    float h(vec2 p){ return fract(sin(dot(p,vec2(12.9898,78.233))+uT*37.0)*43758.5453); }
    void main(){ vec2 c=vU-0.5; float r2=dot(c*vec2(uAsp,1.0),c*vec2(uAsp,1.0)); vec3 col=texture2D(tDiffuse,vU).rgb;
      col*=1.0-smoothstep(0.15,0.9,r2)*0.22; col+=(h(vU*vec2(uAsp,1.0)*900.0)-0.5)*0.008*(0.3+col); gl_FragColor=vec4(max(col*uFade,0.0),1.0);} `});
composer.addPass(grade); composer.addPass(new OutputPass());

window.renderAt=(t,K=2)=>{ actx.globalAlpha=1; actx.clearRect(0,0,W,H); const sh=1/60;
  for(let k=0;k<K;k++){ const tt=clamp(t+(K>1?(k/(K-1)-0.5)*sh:0),0,DUR); setState(tt); grade.uniforms.uT.value=tt; renderer.shadowMap.needsUpdate=true; composer.render(); actx.globalAlpha=1/(k+1); actx.drawImage(renderer.domElement,0,0); }
  return acc.toDataURL('image/jpeg',0.94); };
// screen positions of both heads (for speech bubbles), in panel pixels
window.metaAt=t=>{ const s=setState(t); const pr=v=>{ const p=v.clone().project(cam); return [Math.round((p.x*0.5+0.5)*W),Math.round((0.5-p.y*0.5)*H)]; };
  return {t,kid:pr(kid.head.position.clone().add(V(0,0.13*0.86,0))),par:pr(par.head.position.clone().add(V(0,0.13,0))),lamp:s.lampOn,door:+s.door.toFixed(3),sash:+s.sashUp.toFixed(3),ka:s.ka,pa:s.pa}; };
window.events=[];
window.ready=true;
