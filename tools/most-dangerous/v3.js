// v3: real camera moves. Every shot is a small three.js set; the stickman, walls and shadow are canvas-drawn
// textures on planes, so a low-angle crane up to eye level gives true perspective. Hard cuts on the words.
// Teja 5 Nov: "immersive zoom-ins for the hook... from low angle we zoom in and up the camera to eye level, same for the shadow".
import * as THREE from 'three';
import { rng, clamp, lerp, sm, out3, ramp, K, mk, rad, glow, noiseCanvas, IMG, loadImg, stick, head, blinkAt, breathe } from './lib.js';
const q=new URLSearchParams(location.search); const W=+q.get('w')||1080, H=+q.get('h')||1920;
const out=mk(W,H); document.body.appendChild(out); const g=out.getContext('2d');
const R3=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true}); R3.setPixelRatio(1); R3.setSize(W,H); R3.outputColorSpace=THREE.SRGBColorSpace;
const ease=u=>{u=clamp(u);return u<0.5?4*u*u*u:1-Math.pow(-2*u+2,3)/2;};
const V=(x,y,z)=>new THREE.Vector3(x,y,z);

// ---------------------------------------------------------------- helpers
function tex(c){ const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; t.anisotropy=4; return t; }
function plane(w,h,map,o={}){ const m=new THREE.MeshBasicMaterial({map,transparent:true,depthWrite:o.depthWrite??true,side:THREE.DoubleSide,fog:o.fog??true,opacity:o.opacity??1,blending:o.add?THREE.AdditiveBlending:THREE.NormalBlending,toneMapped:false});
  if(o.add) m.depthWrite=false; const p=new THREE.Mesh(new THREE.PlaneGeometry(w,h),m); if(o.order!=null) p.renderOrder=o.order; return p; }
function glowTex(col,size=256){ const c=mk(size,size), x=c.getContext('2d'); x.fillStyle=rad(x,size/2,size/2,size/2,[[0,`rgba(${col},1)`],[0.25,`rgba(${col},0.45)`],[1,`rgba(${col},0)`]]); x.fillRect(0,0,size,size); return tex(c); }
function concrete(w,h,base,seed,amt=0.5){ const c=mk(w,h), x=c.getContext('2d'); x.fillStyle=base; x.fillRect(0,0,w,h); const n=noiseCanvas(w/2,h/2,Math.max(w,h)/6,5,seed);
  x.globalAlpha=amt; x.globalCompositeOperation='overlay'; x.drawImage(n,0,0,w,h); x.globalCompositeOperation='multiply'; x.globalAlpha=amt*0.6; x.drawImage(noiseCanvas(w/2,h/2,24,3,seed+5),0,0,w,h); x.globalAlpha=1; x.globalCompositeOperation='source-over'; return c; }
// volumetric beam: open cone, bright core, fades with height and toward the rim
function beam(rTop,rBot,h,col,a){ const m=new THREE.ShaderMaterial({transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,side:THREE.DoubleSide,
  uniforms:{c:{value:new THREE.Color(col)},a:{value:a}},
  vertexShader:'varying vec3 n; varying vec3 vp; varying float y; void main(){ n=normalize(normalMatrix*normal); vec4 p=modelViewMatrix*vec4(position,1.); vp=p.xyz; y=uv.y; gl_Position=projectionMatrix*p; }',
  fragmentShader:'uniform vec3 c; uniform float a; varying vec3 n; varying vec3 vp; varying float y; void main(){ float f=abs(dot(normalize(n),normalize(-vp))); float k=pow(f,2.2)*(0.25+0.75*y); gl_FragColor=vec4(c*k*a,1.); }'});
  const msh=new THREE.Mesh(new THREE.CylinderGeometry(rTop,rBot,h,48,1,true),m); return msh; }
// a character = a canvas on a vertical plane (1200 px per metre), feet at y=0
const PX=1200;
function charLayer(wm,hm){ const c=mk(Math.round(wm*PX),Math.round(hm*PX)), t=tex(c), p=plane(wm,hm,t); p.geometry.translate(0,hm/2,0); return {c,x:c.getContext('2d'),t,p,wm,hm}; }
function reflect(L,op){ const m=new THREE.MeshBasicMaterial({map:L.t,transparent:true,opacity:op,depthWrite:false,side:THREE.DoubleSide}); const p=new THREE.Mesh(L.p.geometry,m); p.scale.y=-1; return p; }
// standing pose in canvas px: centre cx, feet at fy, head radius r
function standJ(cx,fy,r,b=0,arm=0){ const neckY=fy-r*5.15+b, hy=neckY-r; return { r, head:[cx,hy], neck:[cx,neckY], hip:[cx,neckY+r*2.45], le:[cx-r*0.45-arm,neckY+r*1.35], lh:[cx-r*0.36-arm*0.6,neckY+r*2.45], re:[cx+r*0.45+arm,neckY+r*1.35], rh:[cx+r*0.36+arm*0.6,neckY+r*2.45],
  lk:[cx-r*0.27,neckY+r*3.75], lf:[cx-r*0.42,fy-r*0.1], rk:[cx+r*0.27,neckY+r*3.75], rf:[cx+r*0.42,fy-r*0.1], lfd:-1, rfd:1 }; }
function walkJ(cx,fy,r,ph){ const bob=-Math.abs(Math.sin(ph))*r*0.14, J=standJ(cx,fy,r,bob,0), L=Math.max(0,Math.sin(ph)), Rr=Math.max(0,-Math.sin(ph));
  J.lf=[J.lf[0]+L*r*0.08,J.lf[1]-L*r*0.55]; J.lk=[J.lk[0]-L*r*0.04,J.lk[1]-L*r*0.45]; J.rf=[J.rf[0]-Rr*r*0.08,J.rf[1]-Rr*r*0.55]; J.rk=[J.rk[0]+Rr*r*0.04,J.rk[1]-Rr*r*0.45];
  const sw=Math.sin(ph)*r*0.28; J.lh=[J.lh[0]-r*0.05,J.lh[1]+sw]; J.le=[J.le[0]-r*0.08,J.le[1]+sw*0.4]; J.rh=[J.rh[0]+r*0.05,J.rh[1]-sw]; J.re=[J.re[0]+r*0.08,J.re[1]-sw*0.4]; return J; }
// tear: a glossy drop sliding down from the eye (drawn in head-local space by a hook)
function tear(c,x,y,r,u){ if(u<=0) return; const yy=y+r*0.05+u*r*0.55; c.save(); c.fillStyle='rgba(210,230,255,0.85)'; c.beginPath(); c.moveTo(x,yy-r*0.12); c.quadraticCurveTo(x+r*0.07,yy,x,yy+r*0.06); c.quadraticCurveTo(x-r*0.07,yy,x,yy-r*0.12); c.fill();
  c.strokeStyle='rgba(210,230,255,0.4)'; c.lineWidth=r*0.03; c.beginPath(); c.moveTo(x,y+r*0.02); c.lineTo(x,yy-r*0.1); c.stroke(); c.fillStyle='#fff'; c.beginPath(); c.arc(x-r*0.015,yy-r*0.02,r*0.018,0,7); c.fill(); c.restore(); }

// ---------------------------------------------------------------- set 1: spotlight studio
const S1={ scene:new THREE.Scene(), cam:new THREE.PerspectiveCamera(50,W/H,0.05,100) };
{ const s=S1.scene; s.background=new THREE.Color('#040507'); s.fog=new THREE.FogExp2('#040507',0.11);
  const fl=plane(40,40,tex(concrete(1024,1024,'#2a2b30',3,0.7))); fl.rotation.x=-Math.PI/2; fl.material.opacity=0.86; fl.material.map.wrapS=fl.material.map.wrapT=THREE.RepeatWrapping; fl.material.map.repeat.set(8,8); s.add(fl);
  const pool=plane(5.5,5.5,glowTex('210,214,225'),{add:true}); pool.rotation.x=-Math.PI/2; pool.position.y=0.005; pool.material.opacity=0.55; s.add(pool);
  const wall=plane(30,14,tex(concrete(1024,512,'#1c1d22',8,0.8))); wall.position.set(0,7,-7); s.add(wall);
  const wp=plane(9,9,glowTex('170,175,190'),{add:true}); wp.position.set(0,4.5,-6.95); wp.material.opacity=0.22; s.add(wp);
  const b=beam(0.22,1.5,7.2,'#dfe4f0',0.5); b.position.set(0,3.6,0); s.add(b); S1.beam=b;
  const lamp=plane(1.4,1.4,glowTex('245,247,255'),{add:true}); lamp.position.set(0,7.1,0); s.add(lamp);
  // dust motes in the beam
  const N=420, pos=new Float32Array(N*3), R=rng(5); S1.seed=[]; for(let i=0;i<N;i++){ S1.seed.push([R(),R(),R(),R()]); }
  const geo=new THREE.BufferGeometry(); geo.setAttribute('position',new THREE.BufferAttribute(pos,3));
  S1.dust=new THREE.Points(geo,new THREE.PointsMaterial({size:0.018,map:glowTex('255,255,255',64),transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,opacity:0.8})); s.add(S1.dust);
  S1.man=charLayer(1.1,2.2); s.add(S1.man.p); const rf=reflect(S1.man,0.18); s.add(rf);
  const sh=plane(1.6,0.5,glowTex('0,0,0'),{}); sh.material.blending=THREE.NormalBlending; sh.rotation.x=-Math.PI/2; sh.position.y=0.01; sh.material.opacity=0.8; s.add(sh); }
function drawMan1(t){ const L=S1.man, c=L.x, w=L.c.width, h=L.c.height; c.clearRect(0,0,w,h);
  const r=320, b=breathe(t,10), J=standJ(w/2,h-30,r,b,Math.sin(t*1.3)*6);
  const lookDown=ramp(t,0.85,1.2), up=1-lookDown;
  c.save(); c.filter='blur(10px)'; stick(c,J,{},{lw:50,ink:'rgba(175,188,212,0.55)'}); c.restore();
  stick(c,J,{eyes:'open',lx:Math.sin(t*2.3)*0.15*up,ly:lerp(-0.95,0.05,lookDown),brow:lookDown>0.5?'sad':'worried',mouth:lookDown>0.6?'flat':'frown',lid:lerp(0,0.22,lookDown)+blinkAt(t,[0.55]),rot:Math.sin(t*1.1)*0.025},{lw:34});
  L.t.needsUpdate=true; }
function set1(t){ const s=S1, u=ease(t/1.5);
  // low on the floor, looking up at him under the light -> craning up to his eye line, close
  const p=V(lerp(0.45,0.0,u),lerp(0.08,1.62,ease(clamp((t-0.1)/1.4))),lerp(3.1,1.75,u)), look=V(0,lerp(1.75,1.5,u),0);
  const sh=0.004; p.x+=Math.sin(t*9.1)*sh; p.y+=Math.sin(t*7.3)*sh;
  s.cam.fov=lerp(62,34,u); s.cam.position.copy(p); s.cam.lookAt(look); s.cam.updateProjectionMatrix();
  s.man.p.position.set(0,0,0); s.man.p.children; drawMan1(t);
  const pa=s.dust.geometry.attributes.position; s.seed.forEach((k,i)=>{ const y=((k[1]*7+t*(0.05+k[2]*0.12))%7), rr=(0.2+y*0.17)*Math.sqrt(k[0]), a=k[3]*6.283+t*0.2; pa.setXYZ(i,Math.cos(a)*rr,7-y,Math.sin(a)*rr); }); pa.needsUpdate=true;
  s.beam.material.uniforms.a.value=0.5*(0.92+0.08*Math.sin(t*31)*Math.sin(t*11));
  R3.render(s.scene,s.cam); }

// ---------------------------------------------------------------- set 2: the alley and his shadow
const S2={ scene:new THREE.Scene(), cam:new THREE.PerspectiveCamera(50,W/H,0.05,100) };
const WALL={ x:1.7, z0:-7, len:9, hgt:7, px:220 };
function buildS2(){ const s=S2.scene; s.background=new THREE.Color('#05060a'); s.fog=new THREE.FogExp2('#06070b',0.07);
  if(IMG.alley){ const c=mk(IMG.alley.width,IMG.alley.height), x=c.getContext('2d'); x.filter='grayscale(0.9) brightness(0.55) contrast(1.25)'; x.translate(c.width,0); x.scale(-1,1); x.drawImage(IMG.alley,0,0);
    const bg=plane(9.4,14.3,tex(c),{fog:false}); bg.position.set(-0.6,4.2,-9); s.add(bg); }
  // right wall (lit concrete) that carries the shadow
  const wc=mk(WALL.len*WALL.px,WALL.hgt*WALL.px); S2.wallC=wc; S2.wallBase=concrete(wc.width,wc.height,'#5d6068',12,0.75);
  { const x=S2.wallBase.getContext('2d'); x.strokeStyle='rgba(20,22,26,0.35)'; x.lineWidth=5; for(let yy=0;yy<wc.height;yy+=120){ x.beginPath(); x.moveTo(0,yy); x.lineTo(wc.width,yy+8); x.stroke(); }
    const lg=x.createLinearGradient(0,0,0,wc.height); lg.addColorStop(0,'rgba(0,0,0,0.75)'); lg.addColorStop(0.5,'rgba(0,0,0,0.1)'); lg.addColorStop(1,'rgba(0,0,0,0.35)'); x.fillStyle=lg; x.fillRect(0,0,wc.width,wc.height);
    x.fillStyle=rad(x,wc.width*0.62,wc.height*0.55,wc.height*0.7,[[0,'rgba(200,208,220,0.35)'],[1,'rgba(0,0,0,0)']]); x.fillRect(0,0,wc.width,wc.height); }
  S2.wallT=tex(wc); const wall=plane(WALL.len,WALL.hgt,S2.wallT); wall.rotation.y=-Math.PI/2; wall.position.set(WALL.x,WALL.hgt/2,WALL.z0+WALL.len/2); s.add(wall);
  // wet floor + puddle glints
  const fl=plane(14,16,tex(concrete(1024,1024,'#1e2026',17,0.8))); fl.rotation.x=-Math.PI/2; fl.position.set(0,0,-3); fl.material.opacity=0.8; s.add(fl);
  for(const [x,z,w,o] of [[0.3,-0.4,2.2,0.35],[-0.4,-3,1.6,0.25],[0.8,1.2,1.2,0.2]]){ const gp=plane(w,w*2.4,glowTex('190,205,230'),{add:true}); gp.rotation.x=-Math.PI/2; gp.position.set(x,0.006,z); gp.material.opacity=o; s.add(gp); }
  // fluorescent tube on the left wall + its glow
  const tube=plane(0.08,1.2,glowTex('235,242,255',64),{add:true}); tube.position.set(-1.6,3.3,-2.5); tube.material.opacity=1; s.add(tube); S2.tube=tube;
  const tg=plane(3.5,3.5,glowTex('200,215,240'),{add:true}); tg.position.set(-1.5,3.3,-2.45); s.add(tg); S2.tg=tg;
  // the man
  S2.man=charLayer(1.1,2.2); S2.man.p.position.set(-0.25,0,0.2); S2.man.p.rotation.y=0.25; s.add(S2.man.p); const rf=reflect(S2.man,0.2); rf.rotation.y=0.25; s.add(rf); S2.refl=rf;
  // eye glows (crisp, additive, on the wall)
  S2.eyes=[-1,1].map(k=>{ const e=plane(0.9,0.9,glowTex('255,40,25'),{add:true}); e.rotation.y=-Math.PI/2; s.add(e); return e; });
  // rain
  const N=700, pos=new Float32Array(N*6), R=rng(8); S2.rs=[]; for(let i=0;i<N;i++) S2.rs.push([R()*5-2.5,R()*7,R()*10-8,0.8+R()*0.4]);
  const geo=new THREE.BufferGeometry(); geo.setAttribute('position',new THREE.BufferAttribute(pos,3)); S2.rain=new THREE.LineSegments(geo,new THREE.LineBasicMaterial({color:'#9fb0c8',transparent:true,opacity:0.35})); s.add(S2.rain); }
// shadow on the wall: u along the wall (m from z0), v up (m); head centre at (SU,SV)
const SU=5.3, SV=4.3;
// he walks towards the camera through the whole alley sequence; the shadow slides along the wall with him
const WALK={ z:t=>lerp(-0.6,1.9,(t-1.5)/2.93), ph:t=>(t-1.5)*2*Math.PI*0.95 };
function drawWall(t){ const c=S2.wallC.getContext('2d'), P=WALL.px, Hh=S2.wallC.height; c.drawImage(S2.wallBase,0,0);
  const X=u=>u*P, Y=v=>Hh-v*P, sw=Math.sin(t*1.4)*0.05, ig=sm((t-2.6)/0.35);
  c.save(); c.filter='blur(6px)'; c.fillStyle='rgba(4,5,7,0.93)'; c.strokeStyle='rgba(4,5,7,0.93)'; c.lineCap='round'; c.lineJoin='round';
  const su=SU+(WALK.z(t)-0.2)*0.9, hx=su+sw, hy=SV+Math.abs(Math.sin(WALK.ph(t)))*-0.08, hr=0.78+0.03*ig;
  c.beginPath(); c.ellipse(X(hx),Y(hy),hr*P,hr*1.08*P,sw*0.3,0,7); c.fill();
  const sl=(w,...p)=>{ c.lineWidth=w*P; c.beginPath(); c.moveTo(X(p[0][0]),Y(p[0][1])); for(let i=1;i<p.length;i++) c.lineTo(X(p[i][0]),Y(p[i][1])); c.stroke(); };
  const SU_=su, nk=[hx-0.02,hy-0.8], hp=[su+0.05,1.5], hunch=ig*0.15, lg=Math.sin(WALK.ph(t))*0.35;
  sl(0.62,nk,hp); sl(0.3,[nk[0]-0.2,nk[1]-0.05],[SU_-1.05-hunch,2.55],[SU_-1.15-hunch-lg*0.4,1.45]); sl(0.3,[nk[0]+0.2,nk[1]-0.05],[SU_+1.1+hunch,2.6],[SU_+1.2+hunch+lg*0.4,1.5]);
  sl(0.34,hp,[SU_-0.45+lg*0.5,0.75],[SU_-0.62+lg,0]); sl(0.34,hp,[SU_+0.55-lg*0.5,0.75],[SU_+0.7-lg,0]);
  for(const [x,y] of [[SU_-1.15-hunch-lg*0.4,1.35],[SU_+1.2+hunch+lg*0.4,1.4]]){ c.beginPath(); c.arc(X(x),Y(y),0.26*P*(1+ig*0.12),0,7); c.fill(); }
  c.restore();
  // angry brows/eye slits + scowl, carved slightly lighter
  c.save(); c.fillStyle=`rgba(${60+150*ig|0},${30-10*ig|0},${28},${0.75+0.25*ig})`; for(const k of [-1,1]){ c.beginPath(); c.moveTo(X(hx+k*0.12),Y(hy+0.12)); c.lineTo(X(hx+k*0.55),Y(hy+0.34)); c.lineTo(X(hx+k*0.48),Y(hy+0.02)); c.closePath(); c.fill(); }
  c.strokeStyle='rgba(60,62,70,0.8)'; c.lineWidth=0.07*P; c.lineCap='round'; c.beginPath(); c.moveTo(X(hx-0.28),Y(hy-0.42)); c.quadraticCurveTo(X(hx),Y(hy-0.3),X(hx+0.28),Y(hy-0.42)); c.stroke(); c.restore();
  S2.wallT.needsUpdate=true;
  const wz=u=>WALL.z0+u; S2.eyes.forEach((e,i)=>{ const k=i?1:-1; e.position.set(WALL.x-0.02,hy+0.2,wz(hx+k*0.33)); e.material.opacity=0.15+0.95*ig*(0.85+0.15*Math.sin(t*13+i)); e.scale.setScalar(0.6+0.6*ig); }); }
function drawMan2(t,close){ const L=S2.man, c=L.x, w=L.c.width, h=L.c.height; c.clearRect(0,0,w,h);
  const r=320, J=walkJ(w/2,h-30,r,WALK.ph(t));
  const tr=close?sm((t-3.55)/0.8):0;
  c.save(); c.filter='blur(10px)'; stick(c,J,{},{lw:52,ink:'rgba(175,188,212,0.6)'}); c.restore();
  stick(c,J,{eyes:'half',lx:close?Math.sin(t*20)*0.04:0.25,ly:close?0.0:0.3,brow:'sad',mouth:'frown',lid:close?0.18+0.1*sm((t-3.4)/0.6):0.12+blinkAt(t,[2.2]),rot:-0.04+Math.sin(t)*0.015},
    {lw:34,skin:['#f2f3f6','#d2d4da','#8e929c'],shade:close?`rgba(255,40,20,${0.10+0.08*Math.sin(t*9)})`:null});
  if(close){ const [hx,hy]=J.head; tear(c,hx-r*0.36,hy-r*0.05,r,tr); }
  L.t.needsUpdate=true; }
function set2(t){ const s=S2, cam=s.cam; drawWall(t); const mz=WALK.z(t); s.man.p.position.set(-0.25,0,mz); s.refl.position.set(-0.25,0,mz);
  let p, look, fov;
  if(t<2.573){ // wide, low: small man, the shadow towering over him
    const u=ease((t-1.5)/1.07); p=V(lerp(-1.0,-0.85,u),lerp(0.15,0.45,u),lerp(3.3,3.1,u)); look=V(0.45,lerp(2.2,2.4,u),mz-1.0); fov=lerp(58,52,u); drawMan2(t,false); }
  else if(t<3.36){ // ANGER: low on the shadow -> rise to its eye line, eyes ignite
    const u=ease((t-2.573)/0.787), su=WALL.z0+SU+(mz-0.2)*0.9; p=V(lerp(0.2,-1.2,u),lerp(0.9,SV+0.2,u),lerp(su+1.6,su+0.15,u)); look=V(WALL.x,lerp(SV-0.6,SV+0.1,u),su); fov=lerp(50,40,u); drawMan2(t,false); }
  else { // GROWS WITHIN SOMEONE: his face, close, red spill from the shadow
    const u=ease((t-3.36)/1.07), hp=s.man.p.position; p=V(hp.x-0.25+lerp(0,0.05,u),1.62,hp.z+lerp(1.75,1.4,u)); look=V(hp.x+0.02,1.6,hp.z); fov=lerp(36,32,u); drawMan2(t,true); }
  const sh=0.005; p.x+=Math.sin(t*8.3)*sh; p.y+=Math.sin(t*6.1)*sh; cam.fov=fov; cam.position.copy(p); cam.lookAt(look); cam.updateProjectionMatrix();
  const fk=0.8+0.2*Math.sin(t*37)*Math.sin(t*13.3)-(Math.sin(t*91)>0.96?0.5:0); s.tube.material.opacity=fk; s.tg.material.opacity=0.45*fk;
  const pa=s.rain.geometry.attributes.position; s.rs.forEach((k,i)=>{ const y=7-((k[1]+t*8*k[3])%7); pa.setXYZ(i*2,k[0],y,k[2]); pa.setXYZ(i*2+1,k[0]-0.02,y-0.28,k[2]); }); pa.needsUpdate=true;
  R3.render(s.scene,cam); }

// ---------------------------------------------------------------- edit: cuts, captions, grade
const CUTS=[0,1.5,2.573,3.36,4.43]; const DUR=+q.get('dur')||4.43;
let WORDS=[["PSYCHOLOGY",0.0],["SAYS",0.968],["/",1.63],["THE",1.63],["MOST",1.819],["DANGEROUS",2.007],["/",2.573],["ANGER",2.573],["/",3.36],["GROWS",3.36],["WITHIN",3.574],["SOMEONE",4.002],["/",4.43],["WHO",4.43],["HAS",4.644],["A",4.858]];
function captions(t){ let start=0; for(let i=0;i<WORDS.length;i++){ if(WORDS[i][0]==='/'&&WORDS[i][1]<=t) start=i+1; }
  const line=[]; for(let i=start;i<WORDS.length&&WORDS[i][0]!=='/';i++) line.push(WORDS[i]); if(!line.length||line[0][1]>t+0.001) return;
  let act=0; line.forEach((w,i)=>{ if(w[1]<=t) act=i; }); const pop=1+0.12*Math.exp(-(t-line[act][1])*18);
  g.save(); g.font='80px "Anton"'; g.textBaseline='middle'; const sp=g.measureText(' ').width*0.9, ws=line.map(w=>g.measureText(w[0]).width), tw=ws.reduce((a,b)=>a+b,0)+sp*(line.length-1);
  let x=W/2-tw/2*(W/1080); const y=H*0.647; g.translate(0,0); const k=W/1080; g.scale(k,k); x/=k;
  line.forEach((w,i)=>{ g.save(); if(i===act){ g.translate(x+ws[i]/2,y/k); g.scale(pop,pop); g.translate(-(x+ws[i]/2),-y/k); }
    g.lineJoin='round'; g.shadowColor='rgba(0,0,0,0.8)'; g.shadowBlur=12; g.shadowOffsetY=3; g.lineWidth=10; g.strokeStyle='#000'; g.strokeText(w[0],x,y/k); g.shadowColor='transparent';
    g.fillStyle=i===act?'#e5161a':'#ffffff'; g.fillText(w[0],x,y/k); g.restore(); x+=ws[i]+sp; });
  g.restore(); }
let NZ; const GT=mk(W,H), gx=GT.getContext('2d');
function grade(t){ gx.clearRect(0,0,W,H); gx.filter='brightness(0.92) contrast(1.2) saturate(0.7)'; gx.drawImage(R3.domElement,0,0); gx.filter='none'; g.drawImage(GT,0,0);
  g.save(); g.globalCompositeOperation='soft-light'; g.fillStyle='rgba(70,110,170,0.3)'; g.fillRect(0,0,W,H); g.restore();
  g.save(); g.globalCompositeOperation='screen'; g.globalAlpha=0.05; g.drawImage(NZ,-W*0.2+((t*18)%(W*0.2)),0,W*1.4,H); g.restore();
  const vg=g.createRadialGradient(W/2,H*0.47,W*0.3,W/2,H*0.5,H*0.7); vg.addColorStop(0,'rgba(0,0,0,0)'); vg.addColorStop(1,'rgba(2,4,10,0.55)'); g.fillStyle=vg; g.fillRect(0,0,W,H);
  // hard-cut punch: 2-frame flash on every cut
  for(const c of CUTS.slice(1)){ const d=t-c; if(d>=0&&d<0.07){ g.fillStyle=`rgba(255,255,255,${0.22*(1-d/0.07)})`; g.fillRect(0,0,W,H); } }
  if(t<0.12){ g.fillStyle=`rgba(255,255,255,${0.8*(1-t/0.12)})`; g.fillRect(0,0,W,H); }
  const Rn=rng(Math.floor(t*30)+7), im=g.getImageData(0,0,W,H), d=im.data; for(let i=0;i<d.length;i+=4){ const n=(Rn()-0.5)*10; d[i]+=n; d[i+1]+=n; d[i+2]+=n; } g.putImageData(im,0,0); }
window.renderAt=t=>{ if(t<1.5) set1(t); else set2(t); g.setTransform(1,0,0,1,0,0); grade(t); captions(t); return out.toDataURL('image/jpeg',0.93); };
window.DUR=DUR;
(async()=>{ const f=new FontFace('Anton','url(fonts/Anton-Regular.ttf)'); await f.load(); document.fonts.add(f); await loadImg('alley'); NZ=noiseCanvas(540,960,120,5,3); buildS2(); window.renderAt(0.5); window.renderAt(2.0); window.ready=true; })();
