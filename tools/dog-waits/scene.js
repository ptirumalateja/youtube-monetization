// He Waits All Day: Slow Light remake of a papercut "dog waits by the door" reference reel (13 s).
// ?shot=dog  full-frame room (1080x1920): the dog, the door, the day passing, the reunion.
// ?shot=day  top split panel (1080x960) 2.2-5.0 s: the owner's day (job / friends / a life), sets behind the camera.
// Units metres, floor y=0, back wall face z=0, room camera on +z.
import * as THREE from 'three';
import * as SLD from './sld.js';
const {V,clamp,sstep,lerp,keys,rng,noiseTex,glowSprite,rimify,PAL}=SLD;
const Q=new URLSearchParams(location.search);
const W=+Q.get('w')||1080, H=+Q.get('h')||1920, SHOT=Q.get('shot')||'dog';
const DUR=13.0;
const LAMP=V(-0.32,3.7,0.95);
const S=SLD.createStage({W,H,lamp:LAMP,lampTarget:V(-0.28,0,0.95),cone:0.3,spot:SHOT==='dog'?42:0,beam:SHOT==='dog'?0.12:0,fov:44,bg:0x0a0e1a,fog:0.045,vig:0.32,hemi:0.55,hemiSky:0x34406a,motes:1400,floorCol:0x6a4a34});
const {scene,cam}=S;
S.renderer.toneMappingExposure=1.18; S.bloom.strength=0.3; S.bloom.threshold=0.9;
const upWash=new THREE.SpotLight(0xffe0b8,SHOT==='dog'?4.5:0,0,0.7,0.9,0); upWash.position.set(0.1,1.0,3.6); upWash.target.position.set(-0.1,2.7,0); scene.add(upWash,upWash.target);
const rim=new THREE.SpotLight(0xffd9a0,0,0,0.5,0.6,0); rim.position.set(-0.7,1.9,0.1); rim.target.position.set(0.4,1.0,0.9); scene.add(rim,rim.target);
const fill=new THREE.DirectionalLight(0x9fb0d8,SHOT==='dog'?0.55:0.25); fill.position.set(0.8,2.2,6); fill.target.position.set(0,0.8,0); scene.add(fill,fill.target);
const wash=new THREE.SpotLight(0xffc890,SHOT==="dog"?3.5:0,0,0.9,0.9,0); wash.position.set(-0.3,2.6,3.2); wash.target.position.set(0.0,1.3,0); scene.add(wash,wash.target);
const canvasTex=(w,h,draw,srgb=true)=>{ const c=document.createElement('canvas'); c.width=w; c.height=h; draw(c.getContext('2d'),w,h); const t=new THREE.CanvasTexture(c); if(srgb) t.colorSpace=THREE.SRGBColorSpace; t.anisotropy=4; return t; };
const std=(color,o={})=>new THREE.MeshStandardMaterial({color,roughness:o.r??0.8,metalness:o.m??0,...o.x});
const box=(w,h,d,mat,x,y,z,parent=scene,cast=true)=>{ const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat); m.position.set(x,y,z); m.castShadow=cast; m.receiveShadow=true; parent.add(m); return m; };
const boxE=(x0,x1,y0,y1,z0,z1,mat,parent=scene,cast=true)=>box(x1-x0,y1-y0,z1-z0,mat,(x0+x1)/2,(y0+y1)/2,(z0+z1)/2,parent,cast);

// ------------------------------------------------------------------ floor: warm planks over the glossy SLD mirror
const floorTex=canvasTex(1024,256,(g,w,h)=>{ const R=rng(4); g.fillStyle='#6b4a33'; g.fillRect(0,0,w,h);
  for(let row=0;row<8;row++){ let x=-R()*200; while(x<w){ const L=150+R()*260; const v=R(); g.fillStyle=`rgb(${100+v*30|0},${68+v*22|0},${46+v*16|0})`; g.fillRect(x+2,row*32+2,L-4,28);
      for(let k=0;k<6;k++){ g.fillStyle=`rgba(40,25,15,${0.05+R()*0.08})`; g.fillRect(x+R()*L,row*32+4+R()*22,40+R()*90,1.5); } x+=L; } }
  g.fillStyle='rgba(20,12,8,0.9)'; for(let row=0;row<=8;row++) g.fillRect(0,row*32-1,w,2); });
floorTex.wrapS=floorTex.wrapT=THREE.RepeatWrapping; floorTex.repeat.set(16,64);
S.floor.material.map=floorTex; S.floor.material.color.set(0xb89a80); S.floor.material.roughness=0.45; S.floor.material.opacity=0.86; S.floor.material.needsUpdate=true;

// ------------------------------------------------------------------ the room (back wall with window + front door)
const WIN={x0:-1.2,x1:-0.42,y0:0.95,y1:1.85}, DOOR={x0:0.12,x1:1.0,y1:2.08};
const wallTex=noiseTex(256,3,128,26,60,0.05); wallTex.repeat.set(6,4);
const wallMat=new THREE.MeshStandardMaterial({color:0x35507e,roughness:0.92,map:wallTex});
const trimMat=std(0x9a9fb0,{r:0.55});
[[-3.5,WIN.x0,0,3.6],[WIN.x1,DOOR.x0,0,3.6],[DOOR.x1,3.5,0,3.6],[WIN.x0,WIN.x1,0,WIN.y0],[WIN.x0,WIN.x1,WIN.y1,3.6],[DOOR.x0,DOOR.x1,DOOR.y1,3.6]]
  .forEach(([a,b,c,d])=>boxE(a,b,c,d,-0.16,0,wallMat));
// dado rail + baseboard
boxE(-3.5,DOOR.x0-0.08,0,0.12,0,0.025,trimMat); boxE(DOOR.x1+0.08,3.5,0,0.12,0,0.025,trimMat);
// window casing, sill, muntins
{ const t=0.07; boxE(WIN.x0-t,WIN.x0,WIN.y0-0.04,WIN.y1+t,0,0.04,trimMat); boxE(WIN.x1,WIN.x1+t,WIN.y0-0.04,WIN.y1+t,0,0.04,trimMat);
  boxE(WIN.x0-t,WIN.x1+t,WIN.y1,WIN.y1+t,0,0.04,trimMat); boxE(WIN.x0-0.12,WIN.x1+0.12,WIN.y0-0.06,WIN.y0,-0.16,0.1,trimMat);
  const mx=(WIN.x0+WIN.x1)/2, my=(WIN.y0+WIN.y1)/2; boxE(mx-0.015,mx+0.015,WIN.y0,WIN.y1,-0.09,-0.06,trimMat); boxE(WIN.x0,WIN.x1,my-0.015,my+0.015,-0.09,-0.06,trimMat); }
// curtains
const curtMat=new THREE.MeshStandardMaterial({color:0x8a2f2a,roughness:0.95,side:THREE.DoubleSide});
for(const [xc,w] of [[WIN.x0-0.12,0.24],[WIN.x1+0.12,0.24]]){ const g=new THREE.PlaneGeometry(w,1.22,24,1); const p=g.attributes.position; for(let i=0;i<p.count;i++) p.setZ(i,0.025*Math.sin(p.getX(i)/w*Math.PI*6)); g.computeVertexNormals();
  const m=new THREE.Mesh(g,curtMat); m.position.set(xc,WIN.y1+0.1-0.61,0.09); m.castShadow=true; m.receiveShadow=true; scene.add(m); }
// sky behind the window: colour follows the clock
const skyU={uDay:{value:0}};
{ const m=new THREE.Mesh(new THREE.PlaneGeometry(6,4),new THREE.ShaderMaterial({uniforms:skyU,fog:false,
    vertexShader:`varying vec2 vU; void main(){ vU=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
    fragmentShader:`varying vec2 vU; uniform float uDay;
      vec3 sky(float d,float y){ vec3 mT=vec3(0.45,0.66,0.95), mB=vec3(0.95,0.85,0.7); vec3 nT=vec3(0.32,0.58,0.95), nB=vec3(0.75,0.86,0.98);
        vec3 sT=vec3(0.42,0.36,0.62), sB=vec3(1.0,0.55,0.28); vec3 dT=vec3(0.05,0.07,0.16), dB=vec3(0.32,0.2,0.3);
        vec3 T=d<0.35?mix(mT,nT,d/0.35):d<0.8?mix(nT,sT,(d-0.35)/0.45):mix(sT,dT,(d-0.8)/0.2);
        vec3 B=d<0.35?mix(mB,nB,d/0.35):d<0.8?mix(nB,sB,(d-0.35)/0.45):mix(sB,dB,(d-0.8)/0.2); return mix(B,T,smoothstep(0.25,0.75,y)); }
      void main(){ vec3 c=sky(uDay,vU.y); float hills=0.33+0.04*sin(vU.x*9.0)+0.03*sin(vU.x*23.0+1.0);
        if(vU.y<hills) c=mix(vec3(0.16,0.28,0.2),vec3(0.05,0.08,0.09),smoothstep(0.75,1.0,uDay))*(0.7+0.3*vU.y/hills);
        gl_FragColor=vec4(c*0.9,1.0);} `}));
  m.position.set(-0.8,1.3,-2.75); scene.add(m); }
// door casing, hallway, door on a hinge at the right edge (swings into the hall)
{ const t=0.08; boxE(DOOR.x0-t,DOOR.x0,0,DOOR.y1+t,0,0.04,trimMat); boxE(DOOR.x1,DOOR.x1+t,0,DOOR.y1+t,0,0.04,trimMat); boxE(DOOR.x0-t,DOOR.x1+t,DOOR.y1,DOOR.y1+t,0,0.04,trimMat); }
const hallMat=new THREE.MeshStandardMaterial({color:0xd9c09a,roughness:0.9});
boxE(-0.35,1.8,0,2.8,-2.6,-2.5,hallMat); boxE(-0.35,-0.25,0,2.8,-2.5,-0.16,hallMat); boxE(1.7,1.8,0,2.8,-2.5,-0.16,hallMat); boxE(-0.35,1.8,2.7,2.8,-2.5,-0.16,hallMat);
scene.children.forEach(m=>{ if(m.material===hallMat) m.receiveShadow=false; });
const hallLight=new THREE.PointLight(0xffc27a,0,6,1.2); hallLight.position.set(0.55,2.2,-1.4); scene.add(hallLight);
const doorSpot=new THREE.SpotLight(0xffbf78,0,0,0.75,0.6,0.6); doorSpot.position.set(0.56,1.9,-1.6); doorSpot.target.position.set(0.3,0,1.6); doorSpot.castShadow=false; doorSpot.shadow.mapSize.set(1024,1024); doorSpot.shadow.bias=-0.0006; doorSpot.shadow.normalBias=0.02; scene.add(doorSpot,doorSpot.target);
const doorPivot=new THREE.Group(); doorPivot.position.set(DOOR.x1-0.005,0,-0.06); scene.add(doorPivot);
const woodTex=noiseTex(256,9,128,60,30,0.1); woodTex.repeat.set(2,2);
const doorMat=new THREE.MeshStandardMaterial({color:0x6a4632,roughness:0.55,map:woodTex});
{ const w=DOOR.x1-DOOR.x0-0.01, h=DOOR.y1-0.02; box(w,h,0.05,doorMat,-w/2,h/2+0.01,0,doorPivot);
  for(const [y0,y1] of [[0.2,0.95],[1.12,1.9]]) for(const [x0,x1] of [[0.08,0.4],[0.47,0.8]]) box(x1-x0,y1-y0,0.02,std(0x7a5440,{r:0.5}),-w+(x0+x1)/2,(y0+y1)/2,0.03,doorPivot);
  const knob=new THREE.Mesh(new THREE.SphereGeometry(0.035,16,10),new THREE.MeshStandardMaterial({color:0xe8b85a,roughness:0.25,metalness:0.85,emissive:0x3a2a10})); knob.position.set(-w+0.08,0.98,0.06); doorPivot.add(knob); }
// warm gap under the door (glows as he arrives)
const leakMat=new THREE.MeshBasicMaterial({color:0xffc98a,transparent:true,opacity:0,fog:false});
{ const leak=new THREE.Mesh(new THREE.PlaneGeometry(DOOR.x1-DOOR.x0,0.018),leakMat); leak.position.set((DOOR.x0+DOOR.x1)/2,0.009,0.01); scene.add(leak); }
// wall clock (cream face, gold rim, hands follow the story clock)
const clockG=new THREE.Group(); clockG.position.set(-0.78,2.18,0.03); scene.add(clockG);
{ const face=canvasTex(256,256,(g,w)=>{ g.fillStyle='#efe7d4'; g.beginPath(); g.arc(128,128,124,0,7); g.fill(); g.fillStyle='#2a2a30';
    for(let i=0;i<12;i++){ const a=i/12*Math.PI*2; g.save(); g.translate(128,128); g.rotate(a); g.fillRect(-3,-112,6,i%3?14:24); g.restore(); } });
  const f=new THREE.Mesh(new THREE.CircleGeometry(0.15,48),new THREE.MeshStandardMaterial({map:face,roughness:0.6,emissive:0xffffff,emissiveMap:face,emissiveIntensity:0.12})); f.position.z=0.02; clockG.add(f);
  const rim=new THREE.Mesh(new THREE.TorusGeometry(0.155,0.018,12,48),std(0xc89a48,{r:0.3,m:0.7})); rim.position.z=0.02; clockG.add(rim); }
const handMat=std(0x1e1e24,{r:0.5});
const hourH=new THREE.Group(), minH=new THREE.Group(); clockG.add(hourH,minH); hourH.position.z=0.03; minH.position.z=0.035;
box(0.016,0.075,0.006,handMat,0,0.035,0,hourH,false); box(0.01,0.115,0.006,handMat,0,0.055,0,minH,false);
// leash on a hook by the door, food bowl, plant
{ boxE(-0.2,-0.12,1.48,1.52,0,0.06,std(0xc89a48,{r:0.3,m:0.7}));
  const c=new THREE.CatmullRomCurve3([V(-0.16,1.5,0.06),V(-0.2,1.25,0.07),V(-0.13,0.98,0.07),V(-0.09,1.2,0.07),V(-0.15,1.49,0.06)]);
  const l=new THREE.Mesh(new THREE.TubeGeometry(c,40,0.012,8,false),std(0xc8382e,{r:0.5})); l.castShadow=true; scene.add(l);
  const bowl=new THREE.Mesh(new THREE.CylinderGeometry(0.11,0.08,0.06,28),std(0x3e5c9a,{r:0.35})); bowl.position.set(-1.05,0.03,0.55); bowl.castShadow=true; scene.add(bowl);
  const pot=new THREE.Mesh(new THREE.CylinderGeometry(0.13,0.1,0.26,20),std(0xb0603c,{r:0.7})); pot.position.set(1.32,0.13,0.35); pot.castShadow=true; scene.add(pot);
  const leafM=std(0x3f7a4a,{r:0.6}); const R=rng(8); for(let i=0;i<9;i++){ const lf=new THREE.Mesh(new THREE.ConeGeometry(0.035,0.45+R()*0.2,6),leafM); const a=R()*6.28, tl=0.25+R()*0.35;
    lf.position.set(1.32+Math.cos(a)*0.06,0.45,0.35+Math.sin(a)*0.06); lf.rotation.set(Math.sin(a)*tl,0,-Math.cos(a)*tl); lf.castShadow=true; scene.add(lf); } }
// rug under the waiting spot
{ const rt=canvasTex(512,256,(g,w,h)=>{ g.fillStyle='#8a2c26'; g.beginPath(); g.ellipse(w/2,h/2,w/2-2,h/2-2,0,0,7); g.fill(); g.setLineDash([18,12]); g.strokeStyle='#e9d2a8'; g.lineWidth=6; g.beginPath(); g.ellipse(w/2,h/2,w/2-26,h/2-22,0,0,7); g.stroke(); });
  const r=new THREE.Mesh(new THREE.PlaneGeometry(1.5,0.75),new THREE.MeshStandardMaterial({map:rt,transparent:true,roughness:1})); r.rotation.x=-Math.PI/2; r.position.set(-0.3,0.004,0.95); r.receiveShadow=true; scene.add(r); }
// the sun: through the window, slides across the floor as the clock runs
const sun=new THREE.SpotLight(0xfff0d8,0,0,0.42,0.25,0); sun.castShadow=true; sun.shadow.mapSize.set(1024,1024); sun.shadow.bias=-0.0004; sun.shadow.normalBias=0.02; sun.shadow.camera.near=2; sun.shadow.camera.far=14; scene.add(sun,sun.target);

// ------------------------------------------------------------------ the dog: keyframed side-view skeleton, capsule body
const FUR=0xd9a05a, FUR_D=0xa86f38;
function makeDog(){
  const fur=rimify(new THREE.MeshStandardMaterial({color:FUR,roughness:0.7,emissive:FUR,emissiveIntensity:0.05}),0xfff1d8,0.22,'dogfur');
  const furD=rimify(new THREE.MeshStandardMaterial({color:FUR_D,roughness:0.75}),0xfff1d8,0.12,'dogear');
  const cream=new THREE.MeshStandardMaterial({color:0xf0e2c4,roughness:0.7});
  const black=new THREE.MeshStandardMaterial({color:0x14100e,roughness:0.25});
  const collar=new THREE.MeshStandardMaterial({color:PAL.RED,roughness:0.45,emissive:PAL.RED,emissiveIntensity:0.12});
  const cyl=new THREE.CylinderGeometry(1,1,1,16,1,true), sph=new THREE.SphereGeometry(1,24,16);
  const G=new THREE.Group(); scene.add(G);
  const mk=(g,m)=>{ const x=new THREE.Mesh(g,m); x.castShadow=true; x.receiveShadow=true; x.frustumCulled=false; G.add(x); return x; };
  const seg=(m)=>({c:mk(cyl,m),e:mk(sph,m)});
  const D={G,torso:mk(cyl,fur),chest:mk(sph,fur),haunch:mk(sph,fur),neck:mk(cyl,fur),head:mk(sph,fur),snout:mk(cyl,cream),snT:mk(sph,cream),nose:mk(sph,black),
    eyeN:mk(sph,black),glint:mk(sph,new THREE.MeshBasicMaterial({color:0xffffff})),eyeF:mk(sph,black),brow:mk(sph,fur),earN:mk(sph,furD),earF:mk(sph,furD),collar:mk(new THREE.TorusGeometry(1,0.18,10,28),collar),tag:mk(sph,new THREE.MeshStandardMaterial({color:0xe8b85a,metalness:0.8,roughness:0.25,emissive:0x5a3c10})),
    legs:[...Array(4)].map(()=>[seg(fur),seg(fur),seg(fur)]), paws:[...Array(4)].map(()=>mk(sph,cream)), tail:[...Array(6)].map(()=>seg(fur)), belly:mk(sph,cream), creamMat:cream};
  return D; }
const DOG=makeDog();
const POSE={
  stand:{ha:[-0.27,0.48],ch:[0.17,0.5],hd:[0.37,0.77],sn:-0.12,fs:[0.18,0.42],fe:[0.2,0.24],fp:[0.21,0.035],rh:[-0.27,0.42],rk:[-0.19,0.27],rhk:[-0.31,0.13],rp:[-0.29,0.035],tb:[-0.38,0.52],ta:0.7,ear:0.35},
  sit:{ha:[-0.22,0.21],ch:[0.1,0.47],hd:[0.24,0.78],sn:-0.02,fs:[0.12,0.39],fe:[0.15,0.22],fp:[0.17,0.035],rh:[-0.22,0.19],rk:[-0.02,0.22],rhk:[-0.12,0.06],rp:[0.03,0.035],tb:[-0.33,0.13],ta:-0.12,ear:0.35},
  lie:{ha:[-0.29,0.165],ch:[0.12,0.175],hd:[0.33,0.41],sn:-0.12,fs:[0.14,0.13],fe:[0.2,0.06],fp:[0.44,0.035],rh:[-0.29,0.13],rk:[-0.06,0.1],rhk:[-0.2,0.05],rp:[-0.05,0.035],tb:[-0.4,0.13],ta:-0.1,ear:0.0},
  chin:{ha:[-0.29,0.16],ch:[0.12,0.165],hd:[0.4,0.185],sn:-0.02,fs:[0.14,0.12],fe:[0.2,0.06],fp:[0.44,0.035],rh:[-0.29,0.13],rk:[-0.06,0.1],rhk:[-0.2,0.05],rp:[-0.05,0.035],tb:[-0.4,0.12],ta:-0.12,ear:-0.15},
  up:{ha:[-0.2,0.36],ch:[0.1,0.8],hd:[0.25,1.08],sn:0.08,fs:[0.13,0.75],fe:[0.27,0.84],fp:[0.37,0.95],rh:[-0.2,0.32],rk:[-0.1,0.19],rhk:[-0.28,0.09],rp:[-0.19,0.035],tb:[-0.3,0.33],ta:0.5,ear:0.7},
  hug2:{ha:[-0.17,0.38],ch:[0.08,0.86],hd:[0.27,1.13],sn:-0.12,fs:[0.1,0.82],fe:[0.24,0.93],fp:[0.35,1.0],rh:[-0.17,0.34],rk:[-0.07,0.2],rhk:[-0.25,0.09],rp:[-0.16,0.035],tb:[-0.27,0.36],ta:0.5,ear:0.3},
  hug:{ha:[-0.17,0.32],ch:[0.1,0.76],hd:[0.27,1.0],sn:-0.05,fs:[0.12,0.7],fe:[0.26,0.82],fp:[0.36,0.94],rh:[-0.18,0.27],rk:[-0.08,0.17],rhk:[-0.26,0.08],rp:[-0.17,0.035],tb:[-0.28,0.28],ta:0.45,ear:0.15},
};
const mixP=(A,B,u)=>{ const o={}; for(const k in A) o[k]=Array.isArray(A[k])?[lerp(A[k][0],B[k][0],u),lerp(A[k][1],B[k][1],u)]:lerp(A[k],B[k],u); return o; };
// [t, pose] keys; smooth blend between consecutive keys
function poseAt(K,t){ if(t<=K[0][0]) return POSE[K[0][1]]; for(let i=1;i<K.length;i++) if(t<=K[i][0]){ const u=(t-K[i-1][0])/(K[i][0]-K[i-1][0]); return mixP(POSE[K[i-1][1]],POSE[K[i][1]],u*u*(3-2*u)); } return POSE[K[K.length-1][1]]; }
function segP(s,a,b,r){ const d=b.clone().sub(a); const len=Math.max(d.length(),1e-4); s.c.position.copy(a).add(b).multiplyScalar(0.5); s.c.scale.set(r,len,r); s.c.quaternion.setFromUnitVectors(SLD.UPV,d.multiplyScalar(1/len)); s.e.position.copy(b); s.e.scale.setScalar(r); }
// st: {P pose, x, z, yaw, wag (0..1 amplitude), wagF, headTilt (roll, rad), headDX/DY (extra head offset), blink (0..1), breath, run (gallop amount), ph (gallop phase), earAdd}
function poseDog(st,t){
  const D=DOG, P=st.P, root=V(st.x,0,st.z), yaw=st.yaw||0;
  const W3=(p,z=0)=>SLD.rotY(V(p[0],p[1],z),yaw).add(root);
  const br=1+0.025*Math.sin(t*2*Math.PI*(st.breathF||0.45))*(st.breath??1);
  let run=st.run||0, ph=st.ph||0;
  const bob=run*0.04*Math.abs(Math.sin(ph));
  const lift=p=>[p[0],p[1]+bob];
  const ha=W3(lift(P.ha)), ch=W3(lift(P.ch));
  segP({c:D.torso,e:D.haunch},ch,ha,0.15*br); D.haunch.scale.setScalar(0.158*br);
  D.chest.position.copy(ch); D.chest.scale.set(0.17*br,0.175*br,0.165*br);
  D.belly.position.copy(ha.clone().lerp(ch,0.55).add(V(0,-0.075,0))); D.belly.scale.set(0.2,0.075,0.105); D.belly.visible=P.ch[1]-P.ha[1]<0.25;
  const hd=W3(lift([P.hd[0]+(st.headDX||0),P.hd[1]+(st.headDY||0)]));
  const nb=ch.clone().add(SLD.rotY(V(0.05,0.07,0),yaw));
  segP({c:D.neck,e:D.head},nb,hd,0.085); D.head.scale.set(0.12,0.11,0.105);
  // head frame: forward f (snout pitch), up u, side s (+z near side)
  const tilt=st.headTilt||0, sn=P.sn+(st.snAdd||0);
  const f=SLD.rotY(V(Math.cos(sn),Math.sin(sn),0),yaw), s0=SLD.rotY(V(0,0,1),yaw);
  let u=new THREE.Vector3().crossVectors(s0,f).normalize(); let s=s0.clone();
  if(tilt){ const q=new THREE.Quaternion().setFromAxisAngle(f,tilt); u.applyQuaternion(q); s.applyQuaternion(q); }
  const hq=new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().makeBasis(f,u,s)); D.head.quaternion.copy(hq);
  const sb=hd.clone().addScaledVector(f,0.04).addScaledVector(u,-0.03), stp=hd.clone().addScaledVector(f,0.15).addScaledVector(u,-0.035);
  segP({c:D.snout,e:D.snT},sb,stp,0.052); D.snout.scale.x=0.055;
  D.nose.position.copy(stp.clone().addScaledVector(f,0.035).addScaledVector(u,0.012)); D.nose.scale.set(0.026,0.022,0.028);
  const bl=1-(st.blink||0)*0.85;
  D.eyeN.position.copy(hd.clone().addScaledVector(f,0.07).addScaledVector(u,0.035).addScaledVector(s,0.06)); D.eyeN.scale.set(0.02,0.022*bl,0.02); D.glint.position.copy(D.eyeN.position.clone().addScaledVector(f,0.006).addScaledVector(u,0.008).addScaledVector(s,0.016)); D.glint.scale.setScalar(0.0055*(bl>0.5?1:0));
  D.eyeF.position.copy(hd.clone().addScaledVector(f,0.07).addScaledVector(u,0.035).addScaledVector(s,-0.06)); D.eyeF.scale.set(0.017,0.019*bl,0.017);
  D.brow.position.copy(hd.clone().addScaledVector(f,0.055).addScaledVector(u,0.065).addScaledVector(s,0.045)); D.brow.scale.set(0.03,0.01,0.022); D.brow.quaternion.copy(hq).multiply(new THREE.Quaternion().setFromAxisAngle(V(0,0,1),-(st.sad??0.5)*0.55));
  // ears hang from the top-sides of the head; ear>0 perks them up/forward
  const ear=clamp(P.ear+(st.earAdd||0),-0.3,1);
  for(const [m,sd] of [[D.earN,1],[D.earF,-1]]){ const base=hd.clone().addScaledVector(u,0.06).addScaledVector(s,sd*0.075).addScaledVector(f,-0.02);
    const a=-0.25+ear*0.9; const dir=u.clone().multiplyScalar(-Math.cos(a)).addScaledVector(f,-Math.sin(a)*0.6).addScaledVector(s,sd*0.25).normalize();
    m.position.copy(base.clone().addScaledVector(dir,0.07)); m.scale.set(0.035,0.085,0.06);
    m.quaternion.setFromUnitVectors(V(0,1,0),dir.clone().negate()); }
  // collar + tag
  const cn=nb.clone().lerp(hd,0.3); const nd=hd.clone().sub(nb).normalize(); D.collar.position.copy(cn); D.collar.scale.setScalar(0.082); D.collar.quaternion.setFromUnitVectors(V(0,0,1),nd);
  D.tag.position.copy(cn.clone().addScaledVector(f,0.06).add(V(0,-0.06,0))); D.tag.scale.setScalar(0.02);
  // legs: front pair z +/-0.075, rear pair +/-0.085; gallop offsets swing the paws
  const legs=[['fs','fe',null,'fp',0.075,0],['fs','fe',null,'fp',-0.075,0.5],['rh','rk','rhk','rp',0.085,0.25],['rh','rk','rhk','rp',-0.085,0.75]];
  legs.forEach(([a,b,c,p],i)=>{ const z=legs[i][4]; const g=Math.sin(ph+legs[i][5]*Math.PI*2)*run, gl=Math.max(0,Math.cos(ph+legs[i][5]*Math.PI*2))*run;
    const off=(q,k)=>[q[0]+g*0.11*k,q[1]+gl*0.07*k+bob*(1-k)];
    const A=W3(lift(P[a]),z*0.8), B=W3(off(P[b],0.5),z), Cc=c?W3(off(P[c],0.85),z):null, Pp=W3(off(P[p],1),z);
    const L=DOG.legs[i]; segP(L[0],A,B,0.064); if(Cc){ segP(L[1],B,Cc,0.05); segP(L[2],Cc,Pp,0.045); } else { segP(L[1],B,Pp,0.052); L[2].c.visible=L[2].e.visible=false; }
    const pw=DOG.paws[i]; pw.position.copy(Pp.clone().add(SLD.rotY(V(0.02,0.005,0),yaw))); pw.scale.set(0.062,0.04,0.05); pw.rotation.y=yaw; });
  // tail: 6 segments, base angle ta (up from horizontal-back), wag = side swish
  let pt=W3(lift(P.tb)), ang=P.ta; const wg=(st.wag||0)*Math.sin(t*2*Math.PI*(st.wagF||5));
  for(let i=0;i<6;i++){ const k=(i+1)/6; const a=ang+0.12*i*(P.ta>0.2?-1:0.3); const sw=wg*(0.4+k)*0.9;
    const d=SLD.rotY(V(-Math.cos(a)*Math.cos(sw),Math.sin(a)*Math.cos(sw)+Math.abs(sw)*0.15,Math.sin(sw)),yaw).multiplyScalar(0.055);
    const nx=pt.clone().add(d); if(nx.y<0.03) nx.y=0.03; segP(DOG.tail[i],pt,nx,0.036*(1-k*0.6)); pt=nx; }
}

// ------------------------------------------------------------------ the owner (cream stickman) + day sets
const R=SLD.createRig(scene);
const man=R.makeFig(PAL.CREAM,'man',{rim:0.18,lift:0.015});
const extras=[R.makeFig(0xc8b8a0,'f1',{rim:0.14,lift:0.03}),R.makeFig(0xb7c0cc,'f2',{rim:0.14,lift:0.03})];
const DAYZ=14;   // day sets live behind the room camera (camera looks +z there)
const SETX={job:-9,fr:0,life:9};
const daySpots=[];
function setSpot(x,col,I){ const s=new THREE.SpotLight(col,I,9,0.5,0.7,0.6); s.position.set(x,4.2,DAYZ-0.6); s.target.position.set(x,0,DAYZ); s.castShadow=SHOT==='day'; s.shadow.mapSize.set(1024,1024); scene.add(s,s.target); daySpots.push(s); return s; }
// JOB: desk, glowing monitor with a chart, paper stack
{ const x=SETX.job; setSpot(x,0xffe2b0,SHOT==='day'?20:0);
  const desk=std(0x5a4636,{r:0.55}); boxE(x-0.75,x+0.75,0.72,0.77,DAYZ-0.1,DAYZ+0.6,desk); for(const dx of [-0.7,0.7]) boxE(x+dx-0.03,x+dx+0.03,0,0.72,DAYZ,DAYZ+0.5,desk);
  const scr=canvasTex(512,320,(g,w,h)=>{ g.fillStyle='#0f2a3a'; g.fillRect(0,0,w,h); g.strokeStyle='#7fe0c0'; g.lineWidth=10; g.beginPath(); [[30,250],[120,170],[190,220],[270,110],[350,160],[470,50]].forEach(([a,b],i)=>i?g.lineTo(a,b):g.moveTo(a,b)); g.stroke();
    g.fillStyle='rgba(127,224,192,0.18)'; for(let i=0;i<6;i++) g.fillRect(30+i*80,280,50,10); });
  const mon=new THREE.Mesh(new THREE.PlaneGeometry(0.62,0.39),new THREE.MeshBasicMaterial({map:scr,fog:false})); mon.position.set(x+0.15,1.1,DAYZ+0.42); mon.rotation.y=Math.PI; scene.add(mon);
  boxE(x-0.18,x+0.48,0.88,1.32,DAYZ+0.44,DAYZ+0.48,std(0x1a1c22,{r:0.4})); boxE(x+0.12,x+0.18,0.77,0.9,DAYZ+0.45,DAYZ+0.5,std(0x1a1c22));
  const glow=new THREE.PointLight(0x8fe8ff,SHOT==='day'?2.2:0,3,1.5); glow.position.set(x+0.15,1.1,DAYZ+0.1); scene.add(glow);
  for(let i=0;i<6;i++) boxE(x-0.62,x-0.32,0.77+i*0.03,0.795+i*0.03,DAYZ+0.1,DAYZ+0.32,std(0xf0ebe0,{r:0.9}));
  boxE(x-0.22,x+0.22,0.44,0.48,DAYZ-0.55,DAYZ-0.15,std(0x30343e)); boxE(x-0.22,x+0.22,0.48,1.0,DAYZ-0.6,DAYZ-0.55,std(0x30343e));  // chair
}
// FRIENDS: round table, string lights (cream glowing dots)
const bulbs=[];
{ const x=SETX.fr; setSpot(x,0xffc98a,SHOT==='day'?20:0);
  const tb=new THREE.Mesh(new THREE.CylinderGeometry(0.55,0.55,0.04,40),std(0x6a4a34,{r:0.5})); tb.position.set(x,0.74,DAYZ+0.15); tb.castShadow=tb.receiveShadow=true; scene.add(tb);
  boxE(x-0.04,x+0.04,0,0.74,DAYZ+0.11,DAYZ+0.19,std(0x3a2a20));
  for(const [mx,mz] of [[-0.2,0.05],[0.25,0.2]]){ const m=new THREE.Mesh(new THREE.CylinderGeometry(0.04,0.035,0.11,14),std(0xe8b85a,{r:0.3,x:{emissive:0x5a3810}})); m.position.set(x+mx,0.815,DAYZ+mz); scene.add(m); }
  for(let i=0;i<15;i++){ const u=i/14; const bx=x-1.3+u*2.6, by=2.25-0.35*Math.sin(u*Math.PI)+0.05*Math.sin(u*31); const sp=glowSprite(scene,0xffd08a,0.95); sp.position.set(bx,by,DAYZ+0.9); sp.scale.setScalar(0.22); bulbs.push(sp);
    const b=new THREE.Mesh(new THREE.SphereGeometry(0.025,10,8),new THREE.MeshBasicMaterial({color:0xfff0c8})); b.position.copy(sp.position); scene.add(b); }
}
// LIFE: bike ride at sunset, posts slide past
const bike=new THREE.Group(); scene.add(bike); bike.position.set(SETX.life,0,DAYZ+0.2);
const wheels=[];
{ const fm=std(0xc8382e,{r:0.35,m:0.3}), tm=std(0x1a1a1e,{r:0.6});
  for(const wx of [-0.5,0.5]){ const wg=new THREE.Group(); wg.position.set(wx,0.34,0); bike.add(wg); const t=new THREE.Mesh(new THREE.TorusGeometry(0.31,0.025,10,40),tm); t.castShadow=true; wg.add(t);
    for(let k=0;k<6;k++){ const sp=new THREE.Mesh(new THREE.CylinderGeometry(0.005,0.005,0.6,4),std(0xaaaaaa,{m:0.6})); sp.rotation.z=k/6*Math.PI; wg.add(sp); } wheels.push(wg); }
  const tube=(a,b)=>{ const m=new THREE.Mesh(new THREE.CylinderGeometry(0.02,0.02,1,8),fm); const d=b.clone().sub(a); m.position.copy(a).add(b).multiplyScalar(0.5); m.scale.y=d.length(); m.quaternion.setFromUnitVectors(SLD.UPV,d.normalize()); m.castShadow=true; bike.add(m); };
  const BB=V(0,0.36,0), SEAT=V(-0.12,0.86,0), HEAD=V(0.4,0.86,0);
  tube(V(-0.5,0.34,0),BB); tube(BB,SEAT); tube(V(-0.5,0.34,0),SEAT); tube(SEAT,HEAD); tube(BB,HEAD); tube(V(0.5,0.34,0),HEAD); tube(HEAD,V(0.37,1.0,0)); tube(V(0.37,1.0,-0.2),V(0.37,1.0,0.2));
  const seat=box(0.2,0.04,0.1,std(0x1a1a1e),-0.14,0.89,0,bike); }
for(const [x,c0,c1,dots] of [[SETX.job,'#1c2c4a','#33507a',1],[SETX.fr,'#3a2430','#7a4a3a',2]]){
  const tex=canvasTex(256,256,(g,w,h)=>{ const gr=g.createLinearGradient(0,0,0,h); gr.addColorStop(0,c0); gr.addColorStop(1,c1); g.fillStyle=gr; g.fillRect(0,0,w,h); const R=rng(5+dots);
    if(dots===1){ for(let bx=0;bx<w;bx+=26){ const bh=80+R()*120; g.fillStyle='rgba(10,16,30,0.55)'; g.fillRect(bx,h-bh,22,bh); for(let wy=h-bh+6;wy<h;wy+=10) for(let wx=bx+3;wx<bx+19;wx+=6) if(R()<0.35){ g.fillStyle='rgba(255,214,140,0.8)'; g.fillRect(wx,wy,3,4);} } }
    else { for(let i=0;i<40;i++){ const r=4+R()*12; const gg=g.createRadialGradient(0,0,0,0,0,r); g.save(); g.translate(R()*w,R()*h*0.7); gg.addColorStop(0,'rgba(255,200,120,0.55)'); gg.addColorStop(1,'rgba(255,200,120,0)'); g.fillStyle=gg; g.fillRect(-r,-r,2*r,2*r); g.restore(); } } });
  const m=new THREE.Mesh(new THREE.PlaneGeometry(9,5),new THREE.MeshBasicMaterial({map:tex,fog:false})); m.position.set(x,2.2,DAYZ+3.2); m.rotation.y=Math.PI; scene.add(m); }
const sunsetBg=new THREE.Mesh(new THREE.PlaneGeometry(16,7),new THREE.MeshBasicMaterial({fog:false,map:canvasTex(64,256,(g,w,h)=>{ const gr=g.createLinearGradient(0,0,0,h); gr.addColorStop(0,'#1a1f3c'); gr.addColorStop(0.45,'#6a3a5a'); gr.addColorStop(0.75,'#e0784a'); gr.addColorStop(1,'#ffb070'); g.fillStyle=gr; g.fillRect(0,0,w,h); })}));
sunsetBg.position.set(SETX.life,2.6,DAYZ+7); sunsetBg.rotation.y=Math.PI; scene.add(sunsetBg);
const sunDisc=glowSprite(scene,0xff9a50,1.0); sunDisc.position.set(SETX.life-1.0,1.25,DAYZ+6); sunDisc.scale.setScalar(3.2);
const sunCore=new THREE.Mesh(new THREE.CircleGeometry(0.42,40),new THREE.MeshBasicMaterial({color:0xffc070,fog:false})); sunCore.position.set(SETX.life-1.0,1.25,DAYZ+6.9); sunCore.rotation.y=Math.PI; scene.add(sunCore);
const posts=[]; for(let i=0;i<6;i++){ const g=new THREE.Group(); const p=new THREE.Mesh(new THREE.CylinderGeometry(0.025,0.03,1.6,8),std(0x2a2a30)); p.position.y=0.8; p.castShadow=true; g.add(p);
  const s=glowSprite(scene,0xffd08a,0.9); s.scale.setScalar(0.35); g.add(s); s.position.y=1.62; scene.remove(s); g.add(s); g.visible=false; scene.add(g); posts.push(g); }
// ground line for the ride (dashes slide by)
const dashes=[]; for(let i=0;i<10;i++){ const d=box(0.35,0.005,0.05,new THREE.MeshBasicMaterial({color:0xe8d8b0}),0,0.003,DAYZ+0.75,scene,false); dashes.push(d); }

// hearts (gold glow) for the reunion
const heartTex=canvasTex(128,128,(g)=>{ g.fillStyle='#fff'; g.beginPath(); g.moveTo(64,112); g.bezierCurveTo(10,72,6,30,36,22); g.bezierCurveTo(52,18,62,30,64,40); g.bezierCurveTo(66,30,76,18,92,22); g.bezierCurveTo(122,30,118,72,64,112); g.fill(); });
const hearts=[]; { const Rh=rng(33); for(let i=0;i<16;i++){ const m=new THREE.Sprite(new THREE.SpriteMaterial({map:heartTex,color:i%3?0xff8a6a:0xffc46a,transparent:true,opacity:0,depthWrite:false,fog:false})); scene.add(m); hearts.push({m,c:i%4===2,t0:[8.7,9.4,10.75,12.2][i%4]+(i%4===2?Rh()*0.12:Rh()*0.4),x:0.36+(Rh()-0.5)*0.3,z:1.12+(Rh()-0.5)*0.15,sz:0.07+Rh()*0.05,sw:Rh()*6}); } }
const heartGlow=glowSprite(scene,0xffb46a,0);

// ------------------------------------------------------------------ story clock (minutes since midnight)
const CK=[[0,487],[0.6,494],[1.5,565],[1.6,567],[1.6001,570],[5.0,707],[5.0001,763],[6.4,928],[6.4001,1007],[7.4,1064],[7.4001,1080],[13,1090]];
const clockMin=t=>{ for(let i=1;i<CK.length;i++) if(t<=CK[i][0]) return lerp(CK[i-1][1],CK[i][1],(t-CK[i-1][0])/(CK[i][0]-CK[i-1][0])); return CK[CK.length-1][1]; };
// shots (cuts): [t0,t1,camFrom,camTo] {p:pos,l:look,f:fov}
const SHOTS=[
  [0.0,0.55,{p:[0.45,0.95,3.35],l:[0.04,0.75,0.3],f:46},{p:[0.4,0.93,3.15],l:[0.04,0.75,0.3],f:46}],
  [0.55,1.6,{p:[0.05,1.0,4.25],l:[-0.05,0.86,0],f:44},{p:[0.02,0.95,4.0],l:[-0.05,0.84,0],f:44}],
  [1.6,5.0,{p:[0.05,0.95,4.1],l:[-0.05,0.62,0],f:44},{p:[0.02,0.9,3.9],l:[-0.05,0.6,0],f:44}],
  [5.0,5.7,{p:[1.25,0.55,2.75],l:[-0.05,0.35,0.7],f:40},{p:[1.18,0.53,2.6],l:[-0.05,0.35,0.7],f:40}],
  [5.7,6.4,{p:[-0.94,0.52,2.17],l:[0.45,0.45,0.35],f:44},{p:[-0.84,0.5,2.04],l:[0.45,0.45,0.35],f:44}],
  [6.4,7.4,{p:[0.15,0.8,3.2],l:[0.0,0.6,0.4],f:44},{p:[0.12,0.78,3.0],l:[0.0,0.6,0.4],f:44}],
  [7.4,8.6,{p:[0.2,1.15,5.0],l:[0.25,1.08,0],f:44},{p:[0.2,1.15,4.8],l:[0.25,1.08,0],f:44}],
  [8.6,13.0,{p:[1.55,1.3,3.7],l:[0.25,0.95,0.6],f:40},{p:[1.4,1.28,3.4],l:[0.25,0.97,0.6],f:40}],
];
const shotOf=t=>SHOTS.find(s=>t>=s[0]&&t<s[1])||SHOTS[SHOTS.length-1];
// dog pose keys
const DK=[[0,'sit'],[0.58,'sit'],[1.12,'lie'],[1.6,'lie'],[3.6,'lie'],[4.2,'chin'],[6.45,'chin'],[6.62,'lie'],[6.9,'lie'],[7.12,'sit'],[7.38,'sit'],[7.52,'stand'],[7.9,'stand'],[8.06,'up'],[8.55,'up'],[9.05,'hug2']];
// man keys: position + pose
function manState(t){
  const P=R.POSES;
  if(t<7.38) return null;
  const walk=sstep(7.38,7.95,t); const x=lerp(0.6,0.66,walk), z=lerp(-0.75,0.6,walk);
  let p={...P.stand}, yaw=-Math.PI/2+lerp(0,-0.9,sstep(7.8,8.1,t)); // walks toward camera, then turns to the dog (faces -x)
  if(t<8.05) p=R.gait(p,(t-7.38)*10,1-sstep(7.85,8.05,t));
  // arms up, laughing, as he gets jumped
  const joy=sstep(7.95,8.12,t)*(1-sstep(8.5,8.8,t));
  p=R.blend(p,{...P.stand,p:-0.08,tilt:-0.25,sL:2.5,sR:2.7,eL:0.35,eR:0.25,aL:0.12,aR:-0.25,kL:0.1,kR:0.2},joy);
  // kneel and hug
  const kn=sstep(8.5,9.05,t); const rock=sstep(8.9,9.3,t)*Math.sin((t-8.9)*3.4)*1.6;
  const kneel={...R.P0,p:0.3+0.05*rock,tilt:-0.12,hy:0.05,aL:1.5,kL:1.5,aR:0.05,kR:1.55,sL:0.6,sR:0.6,eL:1.0,eR:1.0,dy:0,fx:0};
  p=R.blend(p,kneel,kn);
  return {p,x:x+0.015*rock,z:lerp(z,0.82,sstep(8.1,9.0,t)),yaw:lerp(yaw,-Math.PI*0.96,sstep(8.1,8.5,t)),kn};
}
let LAST={};
function setState(t){
  const min=clockMin(t), day=clamp((min-480)/(1080-480));
  skyU.uDay.value=day;
  hourH.rotation.z=-(min/720)*Math.PI*2; minH.rotation.z=-(min/60)*Math.PI*2;
  // sun through the window
  const sx=lerp(3.2,-2.6,day), sy=lerp(5.8,4.6,Math.abs(day-0.45)*2);
  sun.position.set(sx,sy,-4.2); { const wc=V((WIN.x0+WIN.x1)/2,(WIN.y0+WIN.y1)/2,0); const d=wc.clone().sub(sun.position); const k=-sun.position.y/d.y; sun.target.position.copy(sun.position.clone().addScaledVector(d,k)); }
  const sc=day<0.6?new THREE.Color(1.0,0.95,0.86):new THREE.Color().setRGB(1.0,lerp(0.95,0.55,sstep(0.6,0.95,day)),lerp(0.86,0.3,sstep(0.6,0.95,day)));
  sun.color.copy(sc); sun.intensity=SHOT==='dog'?7.5*(1-sstep(0.9,1.0,day)):0;
  // door + hall
  const dOpen=sstep(7.4,7.66,t)*(1-0.62*sstep(8.7,9.6,t)); const dShut=0.95*(1-sstep(0.0,0.3,t)); doorPivot.rotation.y=-(dOpen*1.45+dShut);
  const hallI=SHOT==='dog'?Math.max(sstep(6.3,7.0,t)*0.4,dOpen*0.8,dShut*1.2):0;
  DOG.creamMat.color.setHex(SHOT==='dog'&&t>=8.6?0xe2c08c:0xf0e2c4);            // muzzle/paws separate from the owner's cream hands in the hug
  S.bloom.strength=(SHOT==='dog'&&((t>=1.6&&t<6.4)||t>=8.6))?0.18:0.3;           // less glow on dog close-ups
  hallLight.intensity=hallI*(t>7?2.4:9); doorSpot.intensity=(dOpen*0.35+dShut*0.9)*(SHOT==='dog'?14:0)*(1-0.6*sstep(8.6,9.4,t)); rim.intensity=SHOT==='dog'?9*sstep(8.5,8.9,t):0; leakMat.opacity=sstep(6.35,6.8,t)*(1-dOpen)*0.9;
  // dog
  const P=poseAt(DK,t);
  let x=-0.35, run=0, ph=0;
  x=lerp(-0.35,0.06,sstep(7.5,7.95,t)); run=sstep(7.45,7.58,t)*(1-sstep(7.88,8.02,t)); ph=(t-7.45)*20;
  x=lerp(x,0.08,sstep(8.5,9.05,t));
  const wag=Math.max(sstep(6.95,7.1,t)*0.8,sstep(7.9,8.1,t)*1.1)+(t<0.3?0.3:0);
  const tilt=0.3*sstep(0.6,0.8,t)*(1-sstep(0.95,1.15,t)) + 0.18*sstep(6.6,6.75,t)*(1-sstep(6.9,7.1,t));
  const blinks=[0.44,1.25,2.9,4.6,5.35,6.05,10.4,12.1]; let blink=0; for(const b of blinks) blink=Math.max(blink,1-Math.abs(t-b)/(b<0.5?0.1:0.07));
  const nuzz=sstep(9.05,9.3,t);
  const st={P,x,z:0.95,yaw:0,wag,wagF:t>8?6:4.5,headTilt:tilt+nuzz*0.25*Math.sin((t-9.05)*4.6),headDX:nuzz*0.035*Math.max(0,Math.sin((t-9.05)*9.0)),headDY:t<0.55?-0.03*sstep(0.3,0.5,t):0,blink:t>9.1?Math.max(clamp(blink),0.45+0.15*Math.sin(t*2.1)):clamp(blink),
    breath:t<6.4?1.4:0.6,breathF:t<6.4?0.38:1.6,run,ph,earAdd:0.6*sstep(6.47,6.6,t)*(1-sstep(7.6,8.0,t))+0.6*(1-sstep(0.3,0.5,t))-0.3*sstep(0.3,0.5,t)*(1-sstep(0.55,0.7,t)),snAdd:(t<0.3?0.15:t<0.55?0.15-0.5*sstep(0.3,0.5,t):t<0.9?0.18:0)+(t>5&&t<6.4?0.05:0),sad:t<0.3?0.0:1.0};
  // eyes look up at the door from the chin pose: slight head lift
  if(t>=5.0&&t<6.45) st.headDY=0.012*Math.sin(t*1.3);
  poseDog(st,t);
  // man
  const ms=manState(t);
  if(SHOT==='dog'){
    man.setAlpha(ms?1:0); extras.forEach(e=>e.setAlpha(0)); bike.visible=false;
    if(ms){ let p=ms.p; const root=V(ms.x,0,ms.z);
      if(ms.kn>0.01){ // hug: hands wrap the dog's back
        const back=V(x-0.12,0.52,0.95);
        p={...p,tL:back.clone().add(V(-0.02,0.0,0.17)),tR:back.clone().add(V(0.02,0.0,-0.16)),wL:ms.kn,wR:ms.kn,pL:V(0,-0.4,0.8),pR:V(0,-0.4,-0.8)}; }
      R.poseFig(man,R.skel(p,root,ms.yaw)); }
  } else daySet(t);
  // hearts
  for(const h of hearts){ const u=(t-h.t0)/2.2; if(u<0||u>1||SHOT!=='dog'){ h.m.material.opacity=0; continue; }
    h.m.position.set(h.c?0.24+(h.x-0.36)*0.5+0.05*Math.sin(u*6+h.sw):h.x-0.16+0.05*Math.sin(u*6+h.sw),(h.c?1.3:1.2)+u*(h.c?0.25:0.22),h.z); h.m.scale.setScalar(h.sz*(0.4+0.6*sstep(0,0.15,u)));
    h.m.material.opacity=sstep(0,0.1,u)*(1-sstep(0.65,1,u))*0.95; }
  heartGlow.position.set(0.36,1.05,1.1); heartGlow.scale.setScalar(1.6); heartGlow.material.opacity=SHOT==='dog'?sstep(9.0,10.0,t)*0.28:0;
  // overhead lamp: warmer payoff at the reunion
  S.tick(t,SHOT==='dog'?0.25*sstep(8.5,10,t):0);
  // camera
  if(SHOT==='dog'){ const s=shotOf(t); const u=sstep(s[0],s[1],t)*0.5+((t-s[0])/(s[1]-s[0]))*0.5; const A=s[2],B=s[3];
    cam.position.set(lerp(A.p[0],B.p[0],u),lerp(A.p[1],B.p[1],u),lerp(A.p[2],B.p[2],u)); cam.fov=lerp(A.f,B.f,u); cam.updateProjectionMatrix();
    cam.lookAt(lerp(A.l[0],B.l[0],u),lerp(A.l[1],B.l[1],u),lerp(A.l[2],B.l[2],u)); }
  LAST={t,dOpen};
  return LAST;
}
function daySet(t){
  const P=R.POSES; bike.visible=true;
  const set=t<2.7?'job':t<3.8?'fr':'life';
  const seatPose=(lean)=>({...R.P0,p:lean,tilt:0.1,aL:1.55,aR:1.5,kL:1.5,kR:1.45,sL:0.7,sR:0.7,eL:0.9,eR:0.9,dy:0,fx:0});
  const face=-Math.PI/2*-1; // facing +z (toward the far side): yaw that turns +x onto +z
  extras.forEach(e=>e.setAlpha(set==='fr'?1:0));
  if(set==='job'){ const x=SETX.job; const root=V(x,0.0,DAYZ-0.35); let p=seatPose(0.22); const yaw=SLD.yawOf(V(0,0,1));
    const ty=(k)=>Math.sin(t*28+k)*0.02;
    p={...p,dy:0.06,tL:V(x-0.12,0.8+ty(0),DAYZ+0.18),tR:V(x+0.2,0.8+ty(2),DAYZ+0.16),wL:1,wR:1,pL:V(-0.3,-0.5,0.8),pR:V(-0.3,-0.5,-0.8),hy:0.12*Math.sin(t*3)};
    man.setAlpha(1); R.poseFig(man,R.skel(p,root,yaw));
    cam.position.set(x-1.4+0.25*(t-1.6),1.55,DAYZ-2.4+0.2*(t-1.6)); cam.fov=40; cam.updateProjectionMatrix(); cam.lookAt(x+0.05,0.95,DAYZ+0.15); }
  if(set==='fr'){ const x=SETX.fr; const laugh=Math.max(0,Math.sin((t-2.7)*9)); const hi=sstep(2.75,2.95,t)*(1-sstep(3.3,3.5,t));
    const seats=[[man,V(x,0,DAYZ-0.55),V(0,0,1)],[extras[0],V(x-0.62,0,DAYZ+0.45),V(1,0,-0.6)],[extras[1],V(x+0.62,0,DAYZ+0.45),V(-1,0,-0.6)]];
    seats.forEach(([F,root,dir],i)=>{ let p=seatPose(0.05-laugh*0.12*(i?0.6:1)); p.dy=0.03+laugh*0.03; p.tilt=-0.35*laugh; const yaw=SLD.yawOf(dir);
      if(i<2){ p={...p,sR:2.6*hi+0.7*(1-hi),eR:0.2,sL:0.7,eL:1.2}; } else { p={...p,sL:1.2+0.6*laugh,eL:1.6}; }
      R.poseFig(F,R.skel(p,root,yaw)); });
    man.setAlpha(1);
    bulbs.forEach((b,i)=>b.material.opacity=0.7+0.3*Math.sin(t*5+i*1.7));
    cam.position.set(x+0.0,1.35,DAYZ-2.75); cam.fov=40; cam.updateProjectionMatrix(); cam.lookAt(x,0.95,DAYZ+0.15); }
  if(set==='life'){ const x=SETX.life; const ph=(t-3.8)*9; const yaw=0;
    wheels.forEach(w=>w.rotation.z=-ph*1.3);
    const root=V(x-0.22,0.1,DAYZ+0.2); let p={...R.P0,p:0.5,tilt:-0.2,aL:1.3+0.35*Math.sin(ph),aR:1.3-0.35*Math.sin(ph),kL:1.45+0.5*Math.max(0,Math.cos(ph)),kR:1.45+0.5*Math.max(0,-Math.cos(ph)),dy:0.42,fx:0};
    p={...p,tL:V(x+0.37,1.0,DAYZ+0.38),tR:V(x+0.37,1.0,DAYZ+0.02),wL:1,wR:1,pL:V(0,-0.5,0.5),pR:V(0,-0.5,-0.5)};
    { const J=R.skel(p,root,yaw); const seat=V(x-0.16,0.93,DAYZ+0.2); root.add(seat.sub(J.hip)); }
    man.setAlpha(1); R.poseFig(man,R.skel(p,root,yaw));
    posts.forEach((g,i)=>{ const px=((i*1.4-(t-3.8)*3.2)%8.4+8.4)%8.4-4.2; g.position.set(x+px,0,DAYZ+1.1); });
    dashes.forEach((d,i)=>{ const px=((i*0.85-(t-3.8)*3.2)%8.5+8.5)%8.5-4.25; d.position.x=x+px; });
    cam.position.set(x+0.05,1.05,DAYZ-2.35+0.3*(t-3.8)); cam.fov=40; cam.updateProjectionMatrix(); cam.lookAt(x+0.0,0.95,DAYZ+0.2); }
  // only this set's light on
  dayFill.intensity=(SHOT==='day'&&set==='fr')?3.5:0; dayFill.position.set(SETX.fr+0.3,1.5,DAYZ-2.2);
  daySpots.forEach((s,i)=>s.intensity=([ 'job','fr','life'][i]===set)?(SHOT==='day'?20:0):0);
  sunDisc.visible=sunCore.visible=sunsetBg.visible=set==='life'; posts.forEach(g=>g.visible=set==='life'); dashes.forEach(d=>d.visible=set==='life');
}
const dayFill=new THREE.PointLight(0xffd8b0,0,6,1.5); scene.add(dayFill);
const setT=t=>setState(t);
window.renderAt=(t,K=3)=>{ const s=SHOT==='dog'?shotOf(t):(t<2.7?[1.6,2.7]:t<3.8?[2.7,3.8]:[3.8,5.0]); return S.renderAt(setT,t,K,{t0:s[0],t1:s[1]}); };
const proj=v=>{ const p=v.clone().project(cam); return [Math.round((p.x*0.5+0.5)*W),Math.round((0.5-p.y*0.5)*H)]; };
window.metaAt=t=>{ setState(t); return {t,clock:proj(V(-0.78,2.18,0.05)),door:proj(V(DOOR.x0+0.1,1.0,0.05)),knob:proj(V(DOOR.x0+0.08,0.98,0.05)),min:Math.round(clockMin(t))}; };
window.events=[];
window.ready=true;
