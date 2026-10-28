// "One of these Simpsons predictions is fake" (28 Oct 2026): look stills. Character-free on purpose: no Simpsons footage,
// characters or yellow. The old CRT is the portal; every prediction is a full-bleed set in the dark-warm grade
// (charcoal/navy, never #000; warm 3000 K practicals; haze, bloom). Built on the Slow Light Dark kit (sld.js).
//   ?shot=room | tiger | gate | president | chalk | shelf
// Units are metres; floor y = 0; camera on +z.
import * as THREE from 'three';
import * as SLD from './sld.js';
const {V,clamp,lerp,rng}=SLD;
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960; const SHOT=q.get('shot')||'room';
const K3000=0xffb46b, TVBLUE=0xa8c2ff;

// ---------------------------------------------------------------- helpers
function canvasTex(w,h,fn,srgb=true){ const c=document.createElement('canvas'); c.width=w; c.height=h; const g=c.getContext('2d'); fn(g,w,h); const t=new THREE.CanvasTexture(c); if(srgb) t.colorSpace=THREE.SRGBColorSpace; t.anisotropy=8; return t; }
function woodTex(seed,base){ const t=canvasTex(1024,256,(g)=>{ const Rn=rng(seed); g.fillStyle=base; g.fillRect(0,0,1024,256);
  for(let k=0;k<260;k++){ const y=Rn()*256, a=0.04+Rn()*0.1; g.strokeStyle=Rn()<0.6?`rgba(0,0,0,${a})`:`rgba(255,220,180,${a*0.5})`; g.lineWidth=0.6+Rn()*2.2;
    g.beginPath(); g.moveTo(0,y); for(let x=0;x<=1024;x+=32) g.lineTo(x,y+Math.sin(x*0.004+k)*3+Math.sin(x*0.021+k*1.7)*1.2); g.stroke(); } }); t.wrapS=t.wrapT=THREE.RepeatWrapping; return t; }
function grainTex(seed,rep=[4,2]){ const t=canvasTex(512,512,(g)=>{ const Rn=rng(seed); g.fillStyle='#808080'; g.fillRect(0,0,512,512); for(let i=0;i<9000;i++){ const v=110+Rn()*36; g.fillStyle=`rgba(${v},${v},${v},0.25)`; g.fillRect(Rn()*512,Rn()*512,2,2); } });
  t.wrapS=t.wrapT=THREE.RepeatWrapping; t.repeat.set(...rep); return t; }
let KEY=0; const std=(color,{r=0.6,m=0,rim=0.06,rimCol=0xfff1d8,e=0,ei=0,map=null,emap=null,side=THREE.FrontSide}={})=>SLD.rimify(new THREE.MeshStandardMaterial({color,roughness:r,metalness:m,emissive:e,emissiveIntensity:ei,map,emissiveMap:emap,side}),rimCol,rim,'k'+(KEY++));
function add(geo,mat,parent,cast=true){ const m=new THREE.Mesh(geo,mat); m.castShadow=cast; m.receiveShadow=true; (parent||S.scene).add(m); return m; }
function box(w,h,d,mat,x,y,z,parent){ const m=add(new THREE.BoxGeometry(w,h,d),mat,parent); m.position.set(x,y,z); return m; }
function cyl(rt,rb,h,mat,x,y,z,seg=24,parent){ const m=add(new THREE.CylinderGeometry(rt,rb,h,seg),mat,parent); m.position.set(x,y,z); return m; }
// extra volumetric cone (same ray-march as the stage beam)
const BEAMS=[];
function beam(apex,target,cone,col,k,{len=null,floorFade=true}={}){
  const U={uT:{value:0},uApex:{value:apex},uAxis:{value:target.clone().sub(apex).normalize()},uTan:{value:Math.tan(cone)},uCol:{value:new THREE.Color(col)}};
  const h=len||apex.distanceTo(target)+0.02, r=Math.tan(cone)*h*1.02;
  const g=new THREE.CylinderGeometry(0.02,r,h,96,24,true); g.translate(0,-h/2,0);
  const m=new THREE.Mesh(g,new THREE.ShaderMaterial({uniforms:U,transparent:true,depthWrite:false,side:THREE.BackSide,blending:THREE.AdditiveBlending,fog:false,
    vertexShader:`varying vec3 vW; void main(){ vec4 w=modelMatrix*vec4(position,1.0); vW=w.xyz; gl_Position=projectionMatrix*viewMatrix*w; }`,
    fragmentShader:`varying vec3 vW; uniform vec3 uApex,uAxis,uCol; uniform float uT,uTan;
      float h(vec3 p){ return fract(sin(dot(p,vec3(12.9898,78.233,37.719)))*43758.5453); }
      float n3(vec3 p){ vec3 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f);
        return mix(mix(mix(h(i),h(i+vec3(1,0,0)),f.x),mix(h(i+vec3(0,1,0)),h(i+vec3(1,1,0)),f.x),f.y),mix(mix(h(i+vec3(0,0,1)),h(i+vec3(1,0,1)),f.x),mix(h(i+vec3(0,1,1)),h(i+vec3(1,1,1)),f.x),f.y),f.z); }
      void main(){ vec3 ro=cameraPosition, rd=normalize(vW-cameraPosition); float tEnd=length(vW-cameraPosition); float acc=0.0;
        for(int i=0;i<24;i++){ float s=tEnd*(float(i)+0.5)/24.0; vec3 p=ro+rd*s; vec3 q=p-uApex; float ax=dot(q,uAxis); if(ax<=0.0||ax>${h.toFixed(3)}) continue;
          float rr=length(q-uAxis*ax), rc=ax*uTan; float cone=pow(smoothstep(rc,rc*0.15,rr),1.6);
          float fl=${floorFade?'smoothstep(0.0,0.35,p.y)':'1.0'};
          float hz=0.62+0.55*n3(p*vec3(2.2,0.9,2.2)+vec3(0.0,-uT*0.05,uT*0.03))+0.25*n3(p*6.0+vec3(uT*0.08,0.0,0.0));
          acc+=cone*fl*hz/(0.6+ax*0.55); }
        acc*=tEnd/24.0; gl_FragColor=vec4(uCol*acc*${k.toFixed(4)},1.0); }`}));
  m.position.copy(apex); m.quaternion.setFromUnitVectors(V(0,-1,0),target.clone().sub(apex).normalize()); m.frustumCulled=false; m.renderOrder=5; S.scene.add(m); S.NOREFL.push(m); BEAMS.push(U); return m; }
// glowing particles (sparks, embers, firework shells, rain)
function points(pos,col,size,op=1,parent){ const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.BufferAttribute(new Float32Array(pos),3));
  const m=new THREE.Points(g,new THREE.ShaderMaterial({uniforms:{uCol:{value:new THREE.Color(col)},uS:{value:size*H},uOp:{value:op}},transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
    vertexShader:`uniform float uS; varying float vA; void main(){ vec4 mv=modelViewMatrix*vec4(position,1.0); gl_Position=projectionMatrix*mv; float sz=uS/(-mv.z); gl_PointSize=clamp(sz,1.5,40.0); vA=min(1.0,sz/1.5); }`,
    fragmentShader:`uniform vec3 uCol; uniform float uOp; varying float vA; void main(){ float d=length(gl_PointCoord-0.5); gl_FragColor=vec4(uCol*smoothstep(0.5,0.0,d)*uOp*vA,1.0); }`}));
  m.frustumCulled=false; (parent||S.scene).add(m); S.NOREFL.push(m); return m; }
function lines(pos,col,op){ const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.BufferAttribute(new Float32Array(pos),3));
  const m=new THREE.LineSegments(g,new THREE.LineBasicMaterial({color:col,transparent:true,opacity:op,blending:THREE.AdditiveBlending,depthWrite:false,fog:true})); m.frustumCulled=false; S.scene.add(m); S.NOREFL.push(m); return m; }

// ---------------------------------------------------------------- per-shot stage settings
const STAGES={
  room:     {lamp:V(-0.12,0.86,-0.95),lampTarget:V(-0.05,0.2,2.4),cone:0.62,spot:3.2,beam:0.07,motes:900,bg:0x141a26,fogD:0.05,lift:[0.011,0.0135,0.021],vig:0.5,fov:40},
  shelf:    {lamp:V(-0.12,0.86,-0.95),lampTarget:V(0.3,0.2,1.4),cone:0.62,spot:3.2,beam:0.05,motes:700,bg:0x141a26,fogD:0.05,lift:[0.011,0.0135,0.021],vig:0.55,fov:40},
  tiger:    {lamp:V(-0.2,4.4,0.3),lampTarget:V(-0.25,0,0.35),cone:0.27,spot:38,beam:0.15,motes:1500,bg:0x0f121a,fogD:0.06,lift:[0.010,0.012,0.019],vig:0.55,fov:38},
  gate:     {lamp:V(0,7.5,1.5),lampTarget:V(0,2.2,-2.6),cone:0.42,spot:55,beam:0.05,motes:300,bg:0x0e1526,fogD:0.04,lift:[0.012,0.016,0.028],vig:0.45,fov:46},
  president:{lamp:V(0,0.3,-6),lampTarget:V(0,5,-14),cone:0.55,spot:45,beam:0.0,motes:10,bg:0x0d1424,fogD:0.03,lift:[0.012,0.016,0.028],vig:0.45,fov:40},
  chalk:    {lamp:V(0.25,2.9,-0.5),lampTarget:V(0,1.0,-1.5),cone:0.55,spot:9,beam:0.11,motes:1200,bg:0x10151c,fogD:0.05,lift:[0.011,0.0135,0.021],vig:0.5,fov:40},
};
const S=SLD.createStage({W,H,...STAGES[SHOT]});
S.spot.penumbra=0.85; S.spot.shadow.camera.near=0.05; S.spot.shadow.camera.far=30; S.spot.shadow.radius=4;
const navy=new THREE.HemisphereLight(0x3a4c78,0x241c16,SHOT==='president'||SHOT==='gate'?0.45:0.22); S.scene.add(navy);
let setShot=()=>{};

// =================================================================== ROOM (hook) + SHELF (close): the TV room
function buildRoom(close){
  S.spot.color.setHex(TVBLUE); S.beamU.uCol.value.setHex(TVBLUE); S.moteU.uCol.value.setHex(0xc8d8ff); S.spot.decay=1.4;
  S.floor.material.color.setHex(0x3a2e26); S.floor.material.opacity=0.97; S.refl.material.uniforms.color.value.setHex(0x161616);
  const WALLZ=-1.9;
  const wall=add(new THREE.PlaneGeometry(12,5),std(0x4e5872,{r:0.95,rim:0,map:grainTex(4)}),null,false); wall.position.set(0,2.5,WALLZ);
  box(12,0.1,0.03,std(0x241c16,{rim:0}),0,0.05,WALLZ+0.015);
  // rug
  const rug=add(new THREE.PlaneGeometry(2.2,1.6),std(0x4a2a22,{r:1,rim:0,map:canvasTex(512,384,(g,w,h)=>{ g.fillStyle='#6a3a2c'; g.fillRect(0,0,w,h); g.strokeStyle='#c09060'; g.lineWidth=10; g.strokeRect(24,24,w-48,h-48); g.lineWidth=3; g.strokeRect(48,48,w-96,h-96);
    const Rn=rng(8); for(let i=0;i<5000;i++){ g.fillStyle=`rgba(0,0,0,${Rn()*0.15})`; g.fillRect(Rn()*w,Rn()*h,3,3); } })}),null,false); rug.rotation.x=-Math.PI/2; rug.position.set(0.1,0.004,0.1);
  // TV cabinet
  const WOOD=std(0x8a6a52,{map:woodTex(3,'#3b2a1f'),r:0.5,rim:0.05});
  const CT=0.58; box(1.6,0.04,0.5,WOOD,0,CT-0.02,-1.4); box(1.56,CT-0.06,0.46,std(0x2a1e16,{map:woodTex(5,'#2a1d14'),r:0.6}),0,(CT-0.04)/2,-1.4);
  box(0.02,0.4,0.01,std(0x6a5332,{m:0.5,r:0.35}),-0.02,0.3,-1.165); box(0.02,0.4,0.01,std(0x6a5332,{m:0.5,r:0.35}),0.02,0.3,-1.165);
  // CRT: body, bezel, static screen, rabbit ears
  const PL=std(0x26262a,{r:0.45,rim:0.12,rimCol:0xc8d8ff});
  const tv=new THREE.Group(); tv.position.set(-0.12,CT,-1.36); S.scene.add(tv);
  box(0.66,0.52,0.46,PL,0,0.26,0,tv); box(0.5,0.38,0.12,PL,0,0.26,-0.28,tv);
  box(0.66,0.04,0.06,std(0x1a1a1e,{r:0.5}),0,0.02,0.22,tv);
  const scr=canvasTex(512,384,(g,w,h)=>{ const Rn=rng(11); const im=g.createImageData(w,h); for(let y=0;y<h;y++) for(let x=0;x<w;x++){ const i=(y*w+x)*4; const sc=(y%3===0)?0.55:1; const v=(40+Rn()*215)*sc; im.data[i]=v*0.82; im.data[i+1]=v*0.9; im.data[i+2]=v; im.data[i+3]=255; }
    g.putImageData(im,0,0); const r=g.createRadialGradient(w/2,h/2,40,w/2,h/2,w*0.62); r.addColorStop(0,'rgba(0,0,0,0)'); r.addColorStop(1,'rgba(0,0,0,0.75)'); g.fillStyle=r; g.fillRect(0,0,w,h); });
  const sg=new THREE.SphereGeometry(1.2,48,32,Math.PI/2-0.21,0.42,Math.PI/2-0.16,0.32);   // a shallow bulge = curved CRT glass
  const screen=add(sg,new THREE.MeshStandardMaterial({color:0x000000,emissive:0xffffff,emissiveMap:scr,emissiveIntensity:1.6,roughness:0.15}),tv,false);
  screen.position.set(0,0.27,0.262-1.2);
  box(0.58,0.05,0.02,PL,0,0.03+0.0,0.232,tv); box(0.58,0.05,0.02,PL,0,0.495,0.232,tv); box(0.05,0.5,0.02,PL,-0.305,0.26,0.232,tv); box(0.05,0.5,0.02,PL,0.305,0.26,0.232,tv);
  for(let i=0;i<2;i++){ const k=cyl(0.012,0.012,0.012,std(0x888888,{m:0.6,r:0.3}),0.24,0.12+i*0.06,0.235,12,tv); k.rotation.x=Math.PI/2; }
  for(const s of [-1,1]){ const a=cyl(0.004,0.004,0.62,std(0x9a9aa0,{m:0.8,r:0.25,rim:0.3,rimCol:0xc8d8ff}),0,0,0,8,tv); a.position.set(s*0.14,0.52+0.28,-0.05); a.rotation.z=-s*0.5; }
  cyl(0.05,0.06,0.03,PL,0,0.535,-0.05,16,tv);
  const halo=SLD.glowSprite(S.scene,TVBLUE,0.16); halo.position.set(-0.12,CT+0.27,-1.05); halo.scale.set(1.4,1.1,1);
  const tvFill=new THREE.PointLight(TVBLUE,1.2,4,1.5); tvFill.position.set(-0.12,CT+0.3,-0.95); S.scene.add(tvFill);
  // VHS tapes: four story tapes leaning at the right, a messy stack at the left
  const labels=[['TIGER','1993'],['FOX','1998'],['PRES.','2000'],['HIGGS','1998']];
  const tapeBody=std(0x121214,{r:0.4,rim:0.1,rimCol:0xc8d8ff});
  labels.forEach(([a,b],i)=>{ const g=new THREE.Group(); g.position.set(0.36+i*0.105,CT,-1.33+i*0.012); g.rotation.set(0,-0.08-i*0.04,0.05+i*0.015); S.scene.add(g);
    box(0.104,0.19,0.026,tapeBody,0,0.095,0,g);
    const lt=canvasTex(256,384,(c,w,h)=>{ c.fillStyle='#ece3cf'; c.fillRect(0,0,w,h); const Rn=rng(30+i); for(let k=0;k<1800;k++){ c.fillStyle=`rgba(90,70,40,${Rn()*0.08})`; c.fillRect(Rn()*w,Rn()*h,3,3); }
      c.strokeStyle='rgba(180,60,50,0.55)'; c.lineWidth=3; for(let y=80;y<h;y+=46){ c.beginPath(); c.moveTo(14,y); c.lineTo(w-14,y); c.stroke(); }
      c.fillStyle='#1a1a22'; c.textAlign='center'; c.font='bold 64px Inter, sans-serif'; c.fillText(a,w/2,150); c.font='900 92px Inter, sans-serif'; c.fillText(b,w/2,270); });
    const lab=add(new THREE.PlaneGeometry(0.084,0.13),std(0xffffff,{r:0.85,map:lt,rim:0}),g,false); lab.position.set(0,0.098,0.0135); });
  for(let i=0;i<5;i++) box(0.19,0.026,0.105,tapeBody,-0.62+(i%2)*0.012,CT+0.013+i*0.027,-1.38+i*0.006).rotation.y=0.06*(i-2);
  // warm practical: floor lamp at the left
  const BR=std(0x6a5332,{m:0.5,r:0.38,rim:0.15});
  cyl(0.12,0.14,0.03,BR,-0.92,0.015,-1.45); cyl(0.012,0.012,1.4,BR,-0.92,0.72,-1.45,10);
  const shade=add(new THREE.CylinderGeometry(0.13,0.2,0.26,40,1,true),new THREE.MeshStandardMaterial({color:0x5a3e24,emissive:K3000,emissiveIntensity:1.2,side:THREE.DoubleSide,roughness:0.9}),null,false); shade.position.set(-0.92,1.5,-1.45);
  const warm=new THREE.PointLight(K3000,2.6,5,1.5); warm.position.set(-0.92,1.42,-1.45); warm.castShadow=false; S.scene.add(warm);
  const wh=SLD.glowSprite(S.scene,K3000,0.5); wh.position.set(-0.92,1.42,-1.4); wh.scale.set(0.9,0.9,1);
  // window at the right: navy night, blinds
  const winTex=canvasTex(256,384,(g,w,h)=>{ const r=g.createLinearGradient(0,0,0,h); r.addColorStop(0,'#2a3d6e'); r.addColorStop(1,'#101a33'); g.fillStyle=r; g.fillRect(0,0,w,h);
    g.fillStyle='rgba(255,236,200,0.9)'; const Rn=rng(3); for(let i=0;i<14;i++) g.fillRect(Rn()*w,h*0.65+Rn()*h*0.35,3,3); g.fillStyle='rgba(0,0,0,0.75)'; for(let y=0;y<h;y+=22) g.fillRect(0,y,w,9); });
  const win=add(new THREE.PlaneGeometry(0.55,0.8),new THREE.MeshBasicMaterial({map:winTex,fog:false}),null,false); win.position.set(0.55,1.75,WALLZ+0.01);
  for(const [w,h,x,y] of [[0.62,0.04,0.55,2.16],[0.62,0.04,0.55,1.34],[0.04,0.86,0.25,1.75],[0.04,0.86,0.85,1.75],[0.7,0.03,0.55,1.31]]) box(w,h,0.04,std(0x2c2a2e,{r:0.6}),x,y,WALLZ+0.02);
  const winL=new THREE.PointLight(0x5a78b8,0.6,3,1.6); winL.position.set(0.55,1.7,-1.4); S.scene.add(winL);
  // framed picture above the TV (abstract, no content), wall clock
  box(0.42,0.32,0.02,std(0x3a2a1c,{r:0.5}),-0.15,1.75,WALLZ+0.012); add(new THREE.PlaneGeometry(0.36,0.26),std(0x3c4a5a,{r:0.9,rim:0}),null,false).position.set(-0.15,1.75,WALLZ+0.024);
  // armchair, back to camera, facing the TV
  const FAB=std(0x4a2620,{r:0.95,rim:0.22,rimCol:0xc8d8ff,map:grainTex(12,[2,2])});
  const ch=new THREE.Group(); ch.position.set(0.62,0,0.85); ch.rotation.y=0.35; S.scene.add(ch);
  box(0.74,0.22,0.7,FAB,0,0.3,0,ch); box(0.74,0.62,0.18,FAB,0,0.68,0.3,ch); box(0.14,0.3,0.7,FAB,-0.36,0.5,0,ch); box(0.14,0.3,0.7,FAB,0.36,0.5,0,ch);
  for(const x of [-0.32,0.32]) for(const z of [-0.3,0.3]) cyl(0.022,0.016,0.18,std(0x2a1d14),x,0.09,z,8,ch);
  S.spot.shadow.camera.far=6;
  setShot=(t)=>{ const u=t/3; if(close){ S.cam.position.set(0.46,0.86,-0.3); S.cam.lookAt(0.52,0.7,-1.34); } else { S.cam.position.set(-0.05+u*0.02,0.62,3.1-u*0.15); S.cam.lookAt(-0.02,0.95,-1.2); } };
}

// =================================================================== TIGER: a stage, one spotlight, a white tiger at the edge of the light
function buildTiger(){
  S.spot.color.setHex(0xffd9a0); S.beamU.uCol.value.setHex(0xffd9a0); S.spot.penumbra=0.5;
  S.floor.material.color.setHex(0x2e231c); S.floor.material.map.repeat.set(10,10); S.floor.material.opacity=0.93; S.refl.material.uniforms.color.value.setHex(0x2a2a2a);
  // curtain: deep red velvet folds
  const cg=new THREE.PlaneGeometry(10,6,400,1); const p=cg.attributes.position; for(let i=0;i<p.count;i++){ const x=p.getX(i); p.setZ(i,Math.sin(x*7.5)*0.09+Math.sin(x*2.3)*0.05); } cg.computeVertexNormals();
  const cur=add(cg,std(0x5a0f14,{r:0.85,rim:0.18,rimCol:0xff9070}),null,false); cur.position.set(0,3,-2.6);
  // stage lip
  box(10,0.12,0.1,std(0x1c1410,{r:0.6}),0,0.06,1.8);
  // the magician's props, left behind in the light: top hat on its side, wand
  const HAT=std(0x101014,{r:0.35,rim:0.25});
  const hat=new THREE.Group(); hat.position.set(-0.35,0.13,0.35); hat.rotation.set(0,0.6,Math.PI/2-0.08); S.scene.add(hat);
  cyl(0.11,0.12,0.26,HAT,0,0.13,0,32,hat); cyl(0.19,0.19,0.012,HAT,0,0,0,40,hat); cyl(0.121,0.121,0.04,std(0x6a1018,{r:0.5}),0,0.03,0,32,hat);
  const wand=cyl(0.008,0.008,0.36,std(0x0a0a0c,{r:0.3}),-0.05,0.009,0.62,8); wand.rotation.set(Math.PI/2,0,0.9); const tip=cyl(0.0085,0.0085,0.05,std(0xeeeeee,{r:0.4}),0,0.16,0,8,wand);
  // white tiger: head + shoulders emerging from the dark at the right edge of the pool
  const fur=canvasTex(1024,512,(g,w,h)=>{ g.fillStyle='#e9e4da'; g.fillRect(0,0,w,h); const Rn=rng(7); for(let i=0;i<40000;i++){ const v=200+Rn()*55; g.fillStyle=`rgba(${v},${v-4},${v-12},0.35)`; g.fillRect(Rn()*w,Rn()*h,1,4); }
    g.fillStyle='rgba(38,32,30,0.92)'; for(let k=0;k<26;k++){ const x=Rn()*w, wd=6+Rn()*14, y0=Rn()*h*0.3; g.beginPath(); g.moveTo(x,y0); for(let y=y0;y<h*0.85;y+=8) g.lineTo(x+Math.sin(y*0.02+k)*14+ (y-y0)*0.05, y); for(let y=h*0.85;y>y0;y-=8) g.lineTo(x+wd*(1-(y-y0)/(h))+Math.sin(y*0.02+k)*14+(y-y0)*0.05,y); g.fill(); } });
  const FUR=std(0xffffff,{map:fur,r:0.95,rim:0.35,rimCol:0xd8e4ff});
  const tg=new THREE.Group(); tg.position.set(0.5,0,-1.25); tg.rotation.y=-0.35; S.scene.add(tg);   // local +z = the tiger's forward
  const ell=(sx,sy,sz,x,y,z,mat=FUR,rx=0)=>{ const m=add(new THREE.SphereGeometry(1,40,28),mat,tg); m.scale.set(sx,sy,sz); m.position.set(x,y,z); m.rotation.x=rx; return m; };
  const DFUR=std(0x55524c,{map:fur,r:0.95,rim:0.22,rimCol:0xb8ccff});
  // only the eyes: the tiger stays in the dark (a modelled cat read as a toy)
  for(const s of [-1,1]){     const eye=ell(0.032,0.022,0.02,s*0.085,0.955,0.375,new THREE.MeshStandardMaterial({color:0x000000,emissive:0x9fe0ff,emissiveIntensity:4.5}));
    const gl=SLD.glowSprite(S.scene,0x8fd0ff,0.7); gl.scale.set(0.14,0.14,1); tg.updateMatrixWorld(); gl.position.copy(tg.localToWorld(V(s*0.085,0.955,0.4))); }
  // breath in the cold light
  const br=SLD.glowSprite(S.scene,0xdfe8ff,0.07); tg.updateMatrixWorld(); br.position.copy(tg.localToWorld(V(0,0.84,0.62))); br.scale.set(0.5,0.3,1);
  // cool rim from behind-right so the white fur separates from the void
  const rimL=new THREE.SpotLight(0x9ab4ff,9,0,0.5,0.8,1.5); rimL.position.set(2.2,2.6,-2.0); rimL.target.position.set(0.6,0.8,-0.2); S.scene.add(rimL,rimL.target);
  const keyL=new THREE.SpotLight(0xffd9a0,0,0,0.35,0.9,1.5); keyL.position.set(-0.4,2.5,2.4); keyL.target.position.set(0.55,0.9,0); S.scene.add(keyL,keyL.target);
  setShot=(t)=>{ S.cam.position.set(-0.1,0.55,3.3); S.cam.lookAt(0.1,0.9,-0.4); };
}

// =================================================================== GATE: a studio gate at night, fog, searchlights, fireworks
function buildGate(){
  S.spot.color.setHex(0xffc890); S.spot.decay=1.0; S.floor.material.color.setHex(0x1e2026); S.floor.material.opacity=0.72; S.refl.material.uniforms.color.value.setHex(0x5a5a5a);
  const ST=std(0x8a8478,{r:0.8,rim:0.1,map:grainTex(9,[1,3])});
  for(const s of [-1,1]){ box(0.7,4.2,0.7,ST,s*1.75,2.1,-2.6); box(0.86,0.22,0.86,ST,s*1.75,4.3,-2.6); box(0.9,0.3,0.9,ST,s*1.75,0.15,-2.6);
    const lamp=SLD.glowSprite(S.scene,K3000,0.8); lamp.position.set(s*1.75,4.65,-2.55); lamp.scale.set(0.8,0.8,1); cyl(0.1,0.12,0.25,std(0x2a2620,{r:0.5}),s*1.75,4.5,-2.6,16); }
  // the sign: a long dark board with a marquee of bulbs (no lettering, no logo)
  box(3.6,1.0,0.3,std(0x1a1c22,{r:0.5,rim:0.12}),0,5.1,-2.6); box(3.8,0.08,0.4,ST,0,4.56,-2.6); box(3.8,0.08,0.4,ST,0,5.64,-2.6);
  const bulbs=[]; for(let i=0;i<=36;i++){ const x=-1.72+i*3.44/36; bulbs.push(x,4.68,-2.44, x,5.52,-2.44); } for(let i=1;i<6;i++){ const y=4.68+i*0.84/6; bulbs.push(-1.72,y,-2.44,1.72,y,-2.44); }
  points(bulbs,0xffcf8a,0.05,1.0);
  const sl=new THREE.PointLight(K3000,2.5,6,1.6); sl.position.set(0,4.6,-1.8); S.scene.add(sl);
  // iron gate leaves, half open
  const IRON=SLD.IRON();
  for(const s of [-1,1]){ const g=new THREE.Group(); g.position.set(s*1.4,0,-2.6); g.rotation.y=s*0.9; S.scene.add(g);
    for(let i=0;i<12;i++) box(0.03,2.6,0.03,IRON,-s*0.11*i,1.3,0,g); box(1.3,0.05,0.05,IRON,-s*0.6,0.25,0,g); box(1.3,0.05,0.05,IRON,-s*0.6,2.5,0,g); }
  // sound stages receding into the fog
  const SS=std(0x5a5e66,{r:0.9,rim:0.05});
  for(const [x,z,w,h,d] of [[-4.5,-9,4,5,7],[4.6,-10,4.2,5.5,8],[-5,-19,4.4,6,8],[5.2,-21,4.5,6.5,9],[0,-32,6,8,8]]){ box(w,h,d,SS,x,h/2,z);
    const r=add(new THREE.CylinderGeometry(w/2,w/2,d,32,1,false,0,Math.PI),SS); r.rotation.set(Math.PI/2,0,Math.PI/2); r.position.set(x,h,z); r.scale.set(1,1,0.35);
    const dl=SLD.glowSprite(S.scene,K3000,0.5); dl.position.set(x+(x<0?w/2+0.02:-w/2-0.02),2.0,z+1); dl.scale.set(0.7,0.9,1); }
  // street lamps lining the drive
  for(const z of [-5,-12,-19]) for(const s of [-1,1]){ cyl(0.04,0.05,3.6,std(0x22252a,{r:0.5}),s*2.6,1.8,z,8); const g=SLD.glowSprite(S.scene,0xffc070,0.7); g.position.set(s*2.6,3.65,z); g.scale.set(0.7,0.7,1); }
  // searchlights crossing in the sky, from behind the gate
  beam(V(-2.8,0.2,-7),V(-0.9,30,-18),0.035,0xdfe6ff,0.6,{len:40,floorFade:false});
  beam(V(2.8,0.2,-7),V(1.6,30,-15),0.035,0xdfe6ff,0.6,{len:40,floorFade:false});
  // fireworks: gold shells bursting over the lot
  const fw=[]; const Rn=rng(19);
  for(const [cx,cy,cz,r,n] of [[-2.2,13,-16,3.6,900],[2.6,16,-20,4.4,1000],[0.6,10.5,-12,2.0,450]]) for(let i=0;i<n;i++){ const u=Rn()*2-1, a=Rn()*6.283, s=Math.sqrt(1-u*u); const rr=r*(0.82+0.18*Rn());
    for(let k=0;k<5;k++){ const f=rr*(1-k*0.06); fw.push(cx+Math.cos(a)*s*f,cy+u*f-k*k*0.03,cz+Math.sin(a)*s*f); } }
  points(fw,0xffc878,0.06,1.4);
  const fl=new THREE.PointLight(0xffb060,90,40,1.4); fl.position.set(0.5,12,-15); S.scene.add(fl);
  setShot=(t)=>{ S.cam.position.set(0.15,1.05,6.4); S.cam.lookAt(0,4.4,-6); };
}

// =================================================================== PRESIDENT: the White House south front at night, rain, one window lit
function buildPresident(){
  S.spot.color.setHex(0xe8ecff); S.spot.decay=1.0; S.spot.castShadow=false;
  S.floor.material.color.setHex(0x182418); S.floor.material.opacity=0.88; S.refl.material.uniforms.color.value.setHex(0x3a3a3a);
  const MAR=std(0xb8b4ac,{r:0.75,rim:0.06,map:grainTex(6,[6,2])});
  const Z=-14, FW=18, H1=3.4, H2=3.2, TOPY=H1+H2+0.4;
  box(FW,TOPY,3,MAR,0,TOPY/2+0.6,Z-1.5); box(FW+0.4,0.7,3.4,MAR,0,0.35,Z-1.3);                 // body on a ground storey plinth
  box(FW+0.3,0.35,3.3,MAR,0,TOPY+0.75,Z-1.5);                                                      // cornice
  for(let i=0;i<60;i++){ box(0.08,0.45,0.08,MAR,-FW/2+0.15+i*(FW-0.3)/59,TOPY+1.15,Z-0.02); } box(FW,0.08,0.14,MAR,0,TOPY+1.4,Z-0.02);   // roof balustrade
  // windows: two rows, pediments on the upper row
  const DARK=new THREE.MeshStandardMaterial({color:0x0c0f16,roughness:0.2,emissive:0x0,metalness:0.2});
  const WARM=new THREE.MeshStandardMaterial({color:0x000000,emissive:0xffb46b,emissiveIntensity:4.0});
  const DIM =new THREE.MeshStandardMaterial({color:0x000000,emissive:0xff9a50,emissiveIntensity:0.35});
  const lit=new Set(['1,-3']); const dim=new Set(['0,4','1,5','0,-6']);
  for(let row=0;row<2;row++) for(let c=-8;c<=8;c++){ if(Math.abs(c)<=1 && true) continue; const x=c*1.0, y=0.6+(row?H1+1.4:1.5);
    const key=row+','+c; const m=add(new THREE.PlaneGeometry(0.5,1.25),lit.has(key)?WARM:dim.has(key)?DIM:DARK,null,false); m.position.set(x,y,Z+0.005);
    box(0.62,0.08,0.06,MAR,x,y+0.7,Z+0.03); box(0.62,0.06,0.08,MAR,x,y-0.66,Z+0.04);
    if(lit.has(key)){ const l=new THREE.PointLight(0xffb46b,6,4,1.6); l.position.set(x,y,Z+0.6); S.scene.add(l); const g=SLD.glowSprite(S.scene,0xffb46b,0.35); g.position.set(x,y,Z+0.1); g.scale.set(1.4,1.8,1); } }
  // the bowed south portico: columns on a half circle, balcony, roof
  const R=2.3, PZ=Z+0.1, CH=H1+H2-0.2;
  for(let i=0;i<6;i++){ const a=Math.PI*(0.08+0.84*i/5); const x=Math.cos(a)*R, z=PZ+Math.sin(a)*R; cyl(0.17,0.2,CH,MAR,x,0.7+CH/2,z,20); cyl(0.26,0.26,0.16,MAR,x,0.78,z,20); cyl(0.26,0.22,0.2,MAR,x,0.7+CH-0.05,z,20); }
  const ring=(r0,r1,h,y)=>{ const g=new THREE.CylinderGeometry(r1,r1,h,48,1,false,0,Math.PI); const m=add(g,MAR); m.position.set(0,y,PZ); m.rotation.y=Math.PI/2; return m; };
  ring(0,R+0.35,0.5,0.7+CH+0.25); ring(0,R+0.25,0.2,0.7+H1-0.05);                                // entablature, balcony floor
  for(let i=0;i<40;i++){ const a=Math.PI*i/39; box(0.06,0.4,0.06,MAR,Math.cos(a)*(R+0.2),0.7+H1+0.25,PZ+Math.sin(a)*(R+0.2)); }   // balcony balusters
  for(let i=0;i<40;i++){ const a=Math.PI*i/39; box(0.07,0.45,0.07,MAR,Math.cos(a)*(R+0.3),0.7+CH+0.75,PZ+Math.sin(a)*(R+0.3)); }
  // central doors + windows behind the columns: the lit one is on the curve
  for(const [x,y,m] of [[0,1.55,DIM],[-1.0,1.55,DARK],[1.0,1.55,DARK],[0,H1+2.0,WARM],[-1.0,H1+2.0,DARK],[1.0,H1+2.0,DARK]]){ const p=add(new THREE.PlaneGeometry(0.55,1.4),m,null,false); p.position.set(x,y,Z+0.01); }
  { const l=new THREE.PointLight(0xffb46b,7,4.5,1.6); l.position.set(0,H1+2.0,Z+0.8); S.scene.add(l); const g=SLD.glowSprite(S.scene,0xffb46b,0.4); g.position.set(0,H1+2.0,Z+0.15); g.scale.set(1.5,1.9,1); }
  // flag on the roof
  cyl(0.03,0.03,2.4,std(0xcccccc,{m:0.6,r:0.3}),0,TOPY+2.4,Z-1.5,8);
  const flag=add(new THREE.PlaneGeometry(1.1,0.7,20,1),std(0x8a8a90,{r:0.8,side:THREE.DoubleSide}),null,false); { const p=flag.geometry.attributes.position; for(let i=0;i<p.count;i++) p.setZ(i,Math.sin(p.getX(i)*5)*0.06); } flag.position.set(0.58,TOPY+3.2,Z-1.5);
  // up-lights along the base (cool white wash) + the stage spot from the lawn
  for(const x of [-7,-4.5,4.5,7]){ const s=new THREE.SpotLight(0xe8ecff,18,0,0.5,0.8,1.2); s.position.set(x,0.2,Z+3.5); s.target.position.set(x,5,Z); S.scene.add(s,s.target); }
  // trees, dark silhouettes left and right
  const TREE=std(0x0c140e,{r:1,rim:0.1,rimCol:0x6a84b8});
  for(const [x,z,s] of [[-6.2,-6,2.4],[6.8,-7,2.8],[-9,-10,3],[9.5,-11,3.2]]){ cyl(0.15,0.22,2.2,TREE,x,1.1,z,8); const c=add(new THREE.SphereGeometry(s,16,12),TREE); c.position.set(x,2.2+s*0.7,z); c.scale.y=1.15; }
  // rain: slanted streaks, catching the light
  const rp=[]; const Rn=rng(5); for(let i=0;i<5000;i++){ const x=(Rn()-0.5)*14, y=Rn()*14, z=6-Rn()*20; const L=0.25+Rn()*0.25; rp.push(x,y,z,x+L*0.12,y-L,z); }
  lines(rp,0xb8c8e8,0.13);
  // fog glow at the base
  const fg=SLD.glowSprite(S.scene,0x8aa0d0,0.08); fg.position.set(0,1.2,Z+3); fg.scale.set(22,4,1);
  setShot=(t)=>{ S.cam.position.set(2.4,1.0,7.0); S.cam.lookAt(0.2,4.1,-14); };
}

// =================================================================== CHALK: the blackboard, 775 burning like embers
function buildChalk(){
  S.spot.color.setHex(K3000); S.beamU.uCol.value.setHex(K3000); S.moteU.uCol.value.setHex(0xffc890);
  S.floor.material.color.setHex(0x35291f); S.floor.material.opacity=0.97; S.refl.material.uniforms.color.value.setHex(0x141414);
  const WZ=-1.9;
  const wall=add(new THREE.PlaneGeometry(12,5),std(0x56606e,{r:0.95,rim:0,map:grainTex(14)}),null,false); wall.position.set(0,2.5,WZ);
  // board texture: dark slate green, chalk smudges, the equation
  const BW=3.2, BH=1.35, TW=2048, TH=Math.round(TW*BH/BW);
  const drawChalk=(g,text,x,y,size,col,blur)=>{ g.font=`italic ${size}px "DejaVu Serif", serif`; const Rc=rng(text.length*7+size); g.globalAlpha=0.28; g.fillStyle=col; for(let k=0;k<7;k++) g.fillText(text,x+(Rc()-0.5)*5,y+(Rc()-0.5)*5); g.globalAlpha=1; };
  const board=canvasTex(TW,TH,(g,w,h)=>{ g.fillStyle='#22382e'; g.fillRect(0,0,w,h); const Rn=rng(2);
    for(let i=0;i<60;i++){ g.fillStyle=`rgba(220,230,220,${0.015+Rn()*0.03})`; g.beginPath(); g.ellipse(Rn()*w,Rn()*h,80+Rn()*260,20+Rn()*60,Rn()*3,0,7); g.fill(); }
    for(let i=0;i<20000;i++){ g.fillStyle=`rgba(255,255,255,${Rn()*0.03})`; g.fillRect(Rn()*w,Rn()*h,2,2); }
    g.textAlign='left'; const C='rgba(235,235,225,0.82)';
    drawChalk(g,'M(H⁰) =',560,330,92,C,0); drawChalk(g,'≈',560,520,110,C,0); drawChalk(g,'GeV',1210,520,92,C,0);
    drawChalk(g,'ħc / G',1240,330,70,'rgba(235,235,225,0.5)',0); drawChalk(g,'Ω(t₀) > 1',1500,720,58,'rgba(235,235,225,0.42)',0); drawChalk(g,'Δλ',330,700,58,'rgba(235,235,225,0.4)',0);
    g.strokeStyle='rgba(235,235,225,0.4)'; g.lineWidth=5; g.beginPath(); g.moveTo(520,580); g.bezierCurveTo(800,610,1100,590,1400,575); g.stroke(); });
  const emb=canvasTex(TW,TH,(g,w,h)=>{ g.fillStyle='#000'; g.fillRect(0,0,w,h); g.textAlign='left'; g.font='bold 150px "DejaVu Sans", sans-serif';
    g.shadowColor='#ff7a2a'; g.shadowBlur=40; g.fillStyle='#ffb070'; g.fillText('775',760,525); g.shadowBlur=0;
    const Rn=rng(9); g.globalCompositeOperation='destination-out'; for(let i=0;i<260;i++){ g.beginPath(); g.arc(1010+Rn()*80,400+Rn()*160,2+Rn()*9,0,7); g.fill(); } });   // the right edge is already crumbling
  const BM=new THREE.MeshStandardMaterial({color:0xffffff,map:board,roughness:0.95,emissive:0xffffff,emissiveMap:emb,emissiveIntensity:2.4});
  const b=add(new THREE.PlaneGeometry(BW,BH),BM,null,false); b.position.set(0,1.5,WZ+0.03);
  const FR=std(0x6a4a30,{map:woodTex(4,'#4a3220'),r:0.5});
  box(BW+0.12,0.06,0.06,FR,0,1.5+BH/2+0.03,WZ+0.03); box(BW+0.12,0.05,0.06,FR,0,1.5-BH/2-0.025,WZ+0.03); box(0.06,BH,0.06,FR,-BW/2-0.03,1.5,WZ+0.03); box(0.06,BH,0.06,FR,BW/2+0.03,1.5,WZ+0.03);
  box(BW,0.03,0.1,FR,0,1.5-BH/2-0.06,WZ+0.08); cyl(0.008,0.008,0.07,std(0xf0f0e8,{r:0.9}),0.4,1.5-BH/2-0.035,WZ+0.09,8).rotation.z=Math.PI/2;
  // embers drifting off the 7s, up and to the right
  const ep=[]; const Rn=rng(31); for(let i=0;i<260;i++){ const u=Rn(); ep.push(0.0+u*0.5+(Rn()-0.5)*0.08, 1.5+0.12+u*u*0.9+(Rn()-0.5)*0.12, WZ+0.06+u*0.25); }
  points(ep,0xff8a3a,0.006,1.2);
  const glow=SLD.glowSprite(S.scene,0xff7a2a,0.35); glow.position.set(-0.05,1.55,WZ+0.12); glow.scale.set(1.3,0.6,1);
  const eL=new THREE.PointLight(0xff7a2a,1.6,2.5,1.6); eL.position.set(-0.05,1.55,WZ+0.4); S.scene.add(eL);
  // hanging lamp
  cyl(0.004,0.004,0.6,std(0x222222),0.25,3.25,-0.5,6); const sh=add(new THREE.ConeGeometry(0.16,0.14,32,1,true),new THREE.MeshStandardMaterial({color:0x2a2620,side:THREE.DoubleSide,roughness:0.5,emissive:K3000,emissiveIntensity:0.15}),null,false); sh.position.set(0.25,2.98,-0.5);
  const lg=SLD.glowSprite(S.scene,K3000,0.8); lg.position.set(0.25,2.9,-0.5); lg.scale.set(0.35,0.35,1);
  // teacher's desk in the foreground, chair, a stack of papers
  const DW=std(0x7a5a42,{map:woodTex(6,'#35261a'),r:0.55,rim:0.08});
  box(1.4,0.05,0.7,DW,-0.25,0.76,0.05); box(1.36,0.6,0.04,DW,-0.25,0.45,0.38); for(const x of [-0.92,0.42]) box(0.05,0.74,0.66,DW,x,0.37,0.05);
  box(0.3,0.04,0.22,std(0xe8e0cc,{r:0.9}),-0.5,0.8,0.05).rotation.y=0.2; cyl(0.04,0.035,0.1,std(0x7a2a1a,{r:0.6}),0.15,0.83,-0.05,16);
  setShot=(t)=>{ S.cam.position.set(0.12,1.5,2.1); S.cam.lookAt(0.0,1.45,-1.9); };
}

({room:()=>buildRoom(false),shelf:()=>buildRoom(true),tiger:buildTiger,gate:buildGate,president:buildPresident,chalk:buildChalk})[SHOT]();
function setT(t){ setShot(t); BEAMS.forEach(u=>u.uT.value=t); S.tick(t); }
window.renderAt=(t,K)=>S.renderAt(setT,t,K,{t0:0,t1:100});
setT(0); window.ready=true;
