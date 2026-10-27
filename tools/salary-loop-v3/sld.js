// Slow Light Dark: shared stage, stickman rig and helpers. Lifted from the approved pilot
// (tools/chain-never-locked/scene.js, 24 Oct 2026); values are the ones the owner signed off ("lighting, cream hero,
// red lock, gold lamp, dust, reflection: all perfect"). Change a look value here only with the owner's OK, then tell
// the other reels.
//
//   import * as SLD from '../slow-light-dark-common/sld.js';     (or copy this file next to your scene)
//   const S=SLD.createStage({W,H});                               renderer, scene, camera, lamp, beam, motes, floor, grade
//   const R=SLD.createRig(S.scene);                               stickman rig
//   const hero=R.makeFig(SLD.PAL.CREAM,'hero',{rim:0.16,lift:0.07});
//   function setT(t){ ...pose things...; S.cam.position...; S.tick(t); }
//   window.renderAt=(t,K)=>S.renderAt(setT,t,K,{t0:0,t1:DUR});
//
// Units are metres, floor y = 0, camera on +z. renderAt is pure: no state between frames (parallel workers).
import * as THREE from 'three';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {UnrealBloomPass} from 'three/addons/postprocessing/UnrealBloomPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';
import {ShaderPass} from 'three/addons/postprocessing/ShaderPass.js';
import {Reflector} from 'three/addons/objects/Reflector.js';

// ---------------------------------------------------------------- palette (series lock)
export const PAL={VOID:0x07080b, GOLD:0xe8b85a, CREAM:0xede6d6, SLATE:0x8a8f98, RED:0xd83a2e};

// ---------------------------------------------------------------- small helpers
export const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
export const sstep=(a,b,x)=>{const t=clamp((x-a)/(b-a));return t*t*(3-2*t)};
export const lerp=(a,b,t)=>a+(b-a)*t;
export const ease=u=>u<0.5?4*u*u*u:1-Math.pow(-2*u+2,3)/2;
export const sm5=u=>u*u*u*(u*(u*6-15)+10);
export const V=(x,y,z)=>new THREE.Vector3(x,y,z);
export const UPV=V(0,1,0);
export function rng(seed){ let s=seed>>>0; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; }
export const rotY=(v,y)=>V(v.x*Math.cos(y)+v.z*Math.sin(y),v.y,-v.x*Math.sin(y)+v.z*Math.cos(y));
export const yawOf=d=>Math.atan2(-d.z,d.x);   // yaw that turns local +x onto direction d
// keyframed scalar: [[t,v],...] with smoothstep between keys
export const keys=(K,t)=>{ if(t<=K[0][0]) return K[0][1]; for(let i=1;i<K.length;i++) if(t<=K[i][0]){ const u=(t-K[i-1][0])/(K[i][0]-K[i-1][0]); return lerp(K[i-1][1],K[i][1],u*u*(3-2*u)); } return K[K.length-1][1]; };

// ---------------------------------------------------------------- material helpers
// soft fresnel rim (view-space); give every material its own key (shared programs share uniforms: playbook lesson)
export function rimify(mat,col,amt,key){ mat.userData.rim={value:amt}; mat.onBeforeCompile=s=>{ s.uniforms.uRim=mat.userData.rim; s.uniforms.uRimCol={value:new THREE.Color(col)};
  s.fragmentShader=s.fragmentShader.replace('#include <common>','#include <common>\nuniform float uRim; uniform vec3 uRimCol;')
   .replace('#include <emissivemap_fragment>',`#include <emissivemap_fragment>
     { vec3 vd=normalize(vViewPosition); float fr=pow(1.0-clamp(dot(normal,vd),0.0,1.0),2.6); totalEmissiveRadiance+=uRimCol*fr*uRim; }`); };
  mat.customProgramCacheKey=()=>'rim-'+key; return mat; }
// dust that settles on up-facing surfaces; drive dustU.uDust (0..0.9) over time
export const dustU={uDust:{value:0}};
export function dustify(mat,key,inst=false){ mat.onBeforeCompile=s=>{ s.uniforms.uDust=dustU.uDust;
  s.vertexShader=s.vertexShader.replace('#include <common>','#include <common>\nvarying vec3 vDW; varying vec3 vDN;')
   .replace('#include <project_vertex>',`#include <project_vertex>
     { vec4 dw=vec4(transformed,1.0); vec3 dn=objectNormal;
       #ifdef USE_INSTANCING
         dw=instanceMatrix*dw; dn=mat3(instanceMatrix)*dn;
       #endif
       vDW=(modelMatrix*dw).xyz; vDN=normalize(mat3(modelMatrix)*dn); }`);
  s.fragmentShader=s.fragmentShader.replace('#include <common>',`#include <common>
     varying vec3 vDW; varying vec3 vDN; uniform float uDust; float dAmt;
     float dh(vec3 p){ return fract(sin(dot(p,vec3(12.9898,78.233,37.719)))*43758.5453); }
     float dn3(vec3 p){ vec3 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f);
       return mix(mix(mix(dh(i),dh(i+vec3(1,0,0)),f.x),mix(dh(i+vec3(0,1,0)),dh(i+vec3(1,1,0)),f.x),f.y),
                  mix(mix(dh(i+vec3(0,0,1)),dh(i+vec3(1,0,1)),f.x),mix(dh(i+vec3(0,1,1)),dh(i+vec3(1,1,1)),f.x),f.y),f.z); }`)
   .replace('#include <color_fragment>',`#include <color_fragment>
     { float up=smoothstep(-0.15,0.85,normalize(vDN).y); float n=dn3(vDW*55.0)*0.55+dn3(vDW*190.0)*0.45;
       dAmt=clamp(uDust*(0.1+0.9*up)*(0.45+0.8*n)-0.1,0.0,0.8); diffuseColor.rgb=mix(diffuseColor.rgb,vec3(0.12,0.11,0.1),dAmt); }`)
   .replace('#include <metalnessmap_fragment>','#include <metalnessmap_fragment>\nmetalnessFactor=mix(metalnessFactor,0.0,dAmt);')
   .replace('#include <roughnessmap_fragment>','#include <roughnessmap_fragment>\nroughnessFactor=mix(roughnessFactor,1.0,dAmt);'); };
  mat.customProgramCacheKey=()=>'dust-'+key+(inst?'-i':''); return mat; }
export function noiseTex(size,seed,base,amp,blobs,dark=0.25){ const c=document.createElement('canvas'); c.width=c.height=size; const g=c.getContext('2d'); const Rn=rng(seed);
  const im=g.createImageData(size,size); for(let i=0;i<size*size;i++){ const v=clamp(base+(Rn()-0.5)*amp,0,255); im.data[i*4]=im.data[i*4+1]=im.data[i*4+2]=v; im.data[i*4+3]=255; }
  g.putImageData(im,0,0); g.globalAlpha=dark; for(let k=0;k<blobs;k++){ g.fillStyle=Rn()<0.5?'#000':'#fff'; g.beginPath(); g.arc(Rn()*size,Rn()*size,Rn()*size*0.12,0,7); g.fill(); }
  const t=new THREE.CanvasTexture(c); t.wrapS=t.wrapT=THREE.RepeatWrapping; return t; }
// dark iron (posts, chains, rings): low metalness on purpose, there is no environment map to reflect
export const IRON=()=>new THREE.MeshStandardMaterial({color:0x4a4a50,roughness:0.48,metalness:0.4,map:noiseTex(128,77,128,90,20)});
let _glow=null;
function glowTex(){ if(_glow) return _glow; const c=document.createElement('canvas'); c.width=c.height=128; const g=c.getContext('2d'); const r=g.createRadialGradient(64,64,0,64,64,64);
  r.addColorStop(0,'rgba(255,255,255,1)'); r.addColorStop(0.18,'rgba(255,255,255,0.45)'); r.addColorStop(0.5,'rgba(255,255,255,0.1)'); r.addColorStop(1,'rgba(255,255,255,0)'); g.fillStyle=r; g.fillRect(0,0,128,128);
  _glow=new THREE.CanvasTexture(c); _glow.colorSpace=THREE.SRGBColorSpace; return _glow; }
// additive glow sprite (the red story object's soft halo, glints)
export function glowSprite(scene,col,op){ const s=new THREE.Sprite(new THREE.SpriteMaterial({map:glowTex(),color:col,transparent:true,opacity:op,depthWrite:false,blending:THREE.AdditiveBlending,fog:false})); scene.add(s); return s; }

// ---------------------------------------------------------------- the stage: void, one gold lamp, beam, motes, reflective floor, grade
// opts: W,H; lamp (V), lampTarget (V), cone (half-angle rad), spot (intensity), beam (haze gain), fov, motes (count)
export function createStage(o={}){
  const W=o.W||540, H=o.H||960;
  const LAMP=o.lamp||V(0.0,4.6,0.05), LAMP_T=o.lampTarget||V(0.02,0,0), CONE=o.cone??0.27, SPOT_I=o.spot??60, BEAMK=o.beam??0.14;
  const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true}); renderer.setPixelRatio(1); renderer.setSize(W,H);
  renderer.shadowMap.enabled=true; renderer.shadowMap.type=THREE.PCFSoftShadowMap; renderer.shadowMap.autoUpdate=false;
  renderer.toneMapping=THREE.ACESFilmicToneMapping; renderer.toneMappingExposure=1.0; document.body.appendChild(renderer.domElement);
  const scene=new THREE.Scene(); const VOID=new THREE.Color(PAL.VOID); scene.background=VOID; scene.fog=new THREE.FogExp2(VOID,0.085);
  const cam=new THREE.PerspectiveCamera(o.fov||38,W/H,0.02,60);
  // lights: the lamp does everything; a whisper of navy sky and a faint cool back light for edges. No front fill (it washes the floor).
  scene.add(new THREE.HemisphereLight(0x1c2338,0x2a2218,0.1));
  const spot=new THREE.SpotLight(PAL.GOLD,SPOT_I,0,CONE+0.08,0.85,1.2); spot.position.copy(LAMP); spot.target.position.copy(LAMP_T);
  spot.castShadow=true; spot.shadow.mapSize.set(2048,2048); spot.shadow.bias=-0.00025; spot.shadow.normalBias=0.012; spot.shadow.camera.near=1.5; spot.shadow.camera.far=7;
  scene.add(spot,spot.target);
  const back=new THREE.DirectionalLight(0x9aa8c8,0.1); back.position.set(0.6,3.2,-4.5); back.target.position.set(0,0.5,0); scene.add(back,back.target);
  // floor: soft (low-res) mirror under a 90% concrete skin. Reflector sits 6 mm down (less = z-fighting stripes).
  const refl=new Reflector(new THREE.PlaneGeometry(60,60),{textureWidth:Math.round(W/3),textureHeight:Math.round(H/3),color:0x404040,clipBias:0.002});
  refl.rotation.x=-Math.PI/2; refl.position.y=-0.006; scene.add(refl);
  const fTex=noiseTex(512,5,128,40,140,0.06); fTex.repeat.set(14,14);
  const floor=new THREE.Mesh(new THREE.PlaneGeometry(60,60),new THREE.MeshStandardMaterial({color:0x4a4a50,roughness:0.74,metalness:0,map:fTex,roughnessMap:fTex,transparent:true,opacity:0.9}));
  floor.rotation.x=-Math.PI/2; floor.receiveShadow=true; scene.add(floor);
  // additive haze is hidden from the mirror (it washed the foreground out)
  const NOREFL=[]; { const ob=refl.onBeforeRender; refl.onBeforeRender=function(...a){ NOREFL.forEach(x=>x.visible=false); ob.apply(this,a); NOREFL.forEach(x=>x.visible=true); }; }
  // the beam: back faces of a cone, ray-marched density with drifting haze
  const beamU={uT:{value:0},uI:{value:1},uApex:{value:LAMP},uAxis:{value:LAMP_T.clone().sub(LAMP).normalize()},uTan:{value:Math.tan(CONE)},uCol:{value:new THREE.Color(PAL.GOLD)}};
  { const h=LAMP.distanceTo(LAMP_T)+0.02, r=Math.tan(CONE)*h*1.02;
    const g=new THREE.CylinderGeometry(0.02,r,h,96,24,true); g.translate(0,-h/2,0);
    const m=new THREE.Mesh(g,new THREE.ShaderMaterial({uniforms:beamU,transparent:true,depthWrite:false,side:THREE.BackSide,blending:THREE.AdditiveBlending,fog:false,
      vertexShader:`varying vec3 vW; void main(){ vec4 w=modelMatrix*vec4(position,1.0); vW=w.xyz; gl_Position=projectionMatrix*viewMatrix*w; }`,
      fragmentShader:`varying vec3 vW; uniform vec3 uApex,uAxis,uCol; uniform float uT,uI,uTan;
        float h(vec3 p){ return fract(sin(dot(p,vec3(12.9898,78.233,37.719)))*43758.5453); }
        float n3(vec3 p){ vec3 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f);
          return mix(mix(mix(h(i),h(i+vec3(1,0,0)),f.x),mix(h(i+vec3(0,1,0)),h(i+vec3(1,1,0)),f.x),f.y),mix(mix(h(i+vec3(0,0,1)),h(i+vec3(1,0,1)),f.x),mix(h(i+vec3(0,1,1)),h(i+vec3(1,1,1)),f.x),f.y),f.z); }
        void main(){ vec3 ro=cameraPosition, rd=normalize(vW-cameraPosition); float tEnd=length(vW-cameraPosition); float acc=0.0;
          for(int i=0;i<16;i++){ float s=tEnd*(float(i)+0.5)/16.0; vec3 p=ro+rd*s; vec3 q=p-uApex; float ax=dot(q,uAxis); if(ax<=0.0) continue;
            float rr=length(q-uAxis*ax), rc=ax*uTan; float cone=pow(smoothstep(rc,rc*0.15,rr),1.6);
            float fl=smoothstep(0.0,0.35,p.y);
            float hz=0.62+0.55*n3(p*vec3(2.2,0.9,2.2)+vec3(0.0,-uT*0.05,uT*0.03))+0.25*n3(p*6.0+vec3(uT*0.08,0.0,0.0));
            acc+=cone*fl*hz/(0.6+ax*0.55); }
          acc*=tEnd/16.0; gl_FragColor=vec4(uCol*acc*uI*${BEAMK.toFixed(4)},1.0); }`}));
    m.position.copy(LAMP); m.quaternion.setFromUnitVectors(V(0,-1,0),LAMP_T.clone().sub(LAMP).normalize()); m.frustumCulled=false; m.renderOrder=5; scene.add(m); NOREFL.push(m); }
  // motes: world-fixed, drifting; only visible inside the cone
  const moteU={uT:{value:0},uH:{value:H},uApex:{value:LAMP},uAxis:{value:beamU.uAxis.value},uTan:{value:Math.tan(CONE)},uCol:{value:new THREE.Color(1.0,0.85,0.62)},uOp:{value:1}};
  { const N=o.motes||1700, Rn=rng(21), pos=new Float32Array(N*3), sd=new Float32Array(N);
    for(let i=0;i<N;i++){ const a=Rn()*6.283, r=Math.sqrt(Rn())*2.1; pos[i*3]=LAMP_T.x-0.2+Math.cos(a)*r; pos[i*3+1]=Rn()*3.4; pos[i*3+2]=LAMP_T.z+Math.sin(a)*r; sd[i]=Rn(); }
    const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.BufferAttribute(pos,3)); g.setAttribute('seed',new THREE.BufferAttribute(sd,1));
    const m=new THREE.Points(g,new THREE.ShaderMaterial({uniforms:moteU,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
      vertexShader:`attribute float seed; uniform float uT,uH,uTan; uniform vec3 uApex,uAxis; varying float vA;
        void main(){ vec3 p=position; float s=seed*6.283;
          p.y=mod(p.y-uT*(0.015+0.02*seed)+3.4,3.4); p.x+=0.06*sin(uT*0.37+s)+0.03*sin(uT*0.9+s*2.0); p.z+=0.06*cos(uT*0.31+s*1.3);
          vec3 q=p-uApex; float ax=dot(q,uAxis); float rr=length(q-uAxis*ax), rc=max(ax,0.0)*uTan;
          vA=smoothstep(rc*1.05,rc*0.5,rr)*(0.35+0.65*fract(seed*7.13))*(0.75+0.25*sin(uT*(1.0+seed*2.0)+s));
          vec4 mv=modelViewMatrix*vec4(p,1.0); gl_Position=projectionMatrix*mv;
          float sz=(0.0055+0.006*fract(seed*3.7))*uH/(-mv.z)*1.6; gl_PointSize=clamp(sz,1.0,26.0); vA*=clamp(1.6/sz,0.08,1.0)*min(1.0,sz); }`,
      fragmentShader:`uniform vec3 uCol; uniform float uOp; varying float vA; void main(){ vec2 c=gl_PointCoord-0.5; float d=length(c); float a=smoothstep(0.5,0.0,d); gl_FragColor=vec4(uCol*a*vA*uOp*0.9,1.0); }`}));
    m.frustumCulled=false; scene.add(m); NOREFL.push(m); }
  // post: bloom, soft clamp, vignette, faint navy corners (linear space: keep the values tiny), luminance-scaled grain
  const composer=new EffectComposer(renderer); composer.setSize(W,H);
  composer.addPass(new RenderPass(scene,cam));
  const bloom=new UnrealBloomPass(new THREE.Vector2(W,H),0.45,0.6,0.88); composer.addPass(bloom);
  const gradePass=new ShaderPass({uniforms:{tDiffuse:{value:null},uT:{value:0},uAsp:{value:W/H}},vertexShader:`varying vec2 vU; void main(){ vU=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
   fragmentShader:`varying vec2 vU; uniform sampler2D tDiffuse; uniform float uT,uAsp;
    float h(vec2 p){ return fract(sin(dot(p,vec2(12.9898,78.233))+uT*37.0)*43758.5453); }
    void main(){ vec2 c=vU-0.5; float r2=dot(c*vec2(uAsp,1.0),c*vec2(uAsp,1.0));
     vec3 col=texture2D(tDiffuse,vU).rgb; col=vec3(1.0)-exp(-1.15*col);
     float vig=1.0-smoothstep(0.06,0.42,r2)*0.62; col*=vig;
     col+=vec3(0.0006,0.0010,0.0028)*smoothstep(0.08,0.45,r2);
     col+=(h(vU*vec2(uAsp,1.0)*900.0)-0.5)*0.006*(0.3+col);
     gl_FragColor=vec4(max(col,0.0),1.0);} `});
  composer.addPass(gradePass); const GU=gradePass.uniforms;
  composer.addPass(new OutputPass());
  const acc=document.createElement('canvas'); acc.width=W; acc.height=H; const actx=acc.getContext('2d');
  const S={W,H,renderer,scene,cam,spot,beamU,moteU,refl,floor,NOREFL,composer,bloom,GU,LAMP,LAMP_T,CONE,SPOT_I,
    // per sub-frame: advance the shared animated uniforms; pay = gold payoff lift (0..~0.15)
    tick(t,pay=0){ spot.intensity=SPOT_I*(1+pay); beamU.uI.value=1+pay*1.2; beamU.uT.value=t; moteU.uT.value=t; GU.uT.value=t; },
    // motion-blurred frame: setT(t) poses the scene (and calls S.tick); never blur across a cut ([t0,t1] = current shot)
    renderAt(setT,t,Ksub=3,{t0=0,t1=1e9,shutter=1/60}={}){ actx.globalAlpha=1; actx.clearRect(0,0,W,H);
      for(let k=0;k<Ksub;k++){ const tt=clamp(t+(Ksub>1?(k/(Ksub-1)-0.5)*shutter:0),t0,t1-1e-4); setT(tt); renderer.shadowMap.needsUpdate=true; composer.render(); actx.globalAlpha=1/(k+1); actx.drawImage(renderer.domElement,0,0); }
      return acc.toDataURL('image/jpeg',0.95); }};
  return S; }

// ---------------------------------------------------------------- stickman rig: capsule limbs, sphere head, no face
export function createRig(scene){
  const L={thigh:0.46,shin:0.46,torso:0.56,neck:0.07,head:0.13,upper:0.31,fore:0.29};
  const LIMB=0.22*2*L.head*2;   // limb RADIUS = 0.22 x head diameter, i.e. limb width 0.44 x head (the literal 0.22x width read wire-thin)
  // color, unique key, {rim, rimCol, lift (self-emissive so the underside never goes black), castShadow}
  function makeFig(color,key,{rim=0.16,rimCol=0xfff1d8,lift=0.0}={}){
    const mat=rimify(new THREE.MeshStandardMaterial({color,roughness:0.62,metalness:0,emissive:color,emissiveIntensity:lift}),rimCol,rim,key);
    const cyl=new THREE.CylinderGeometry(1,1,1,16,1,true), sph=new THREE.SphereGeometry(1,24,16);
    const mk=g=>{ const m=new THREE.Mesh(g,mat); m.castShadow=true; m.receiveShadow=true; m.frustumCulled=false; scene.add(m); return m; };
    const F={mat,bones:[...Array(9)].map(()=>mk(cyl)),joints:[...Array(14)].map(()=>mk(sph)),head:mk(sph)};
    F.all=F.bones.concat(F.joints,[F.head]);
    // fade into / out of the void without pops: opacity a (0..1); shadows only when mostly solid.
    // Outside the beam a faded figure reads as its soft rim only: that is the intended look, not a seam.
    F.setAlpha=a=>{ const vis=a>0.004, fade=a<0.999; if(mat.transparent!==fade){ mat.transparent=fade; mat.needsUpdate=true; } mat.opacity=a;
      F.all.forEach(x=>{ x.visible=vis; x.castShadow=vis&&a>0.5; }); };
    return F; }
  function bone(m,a,b,r){ const d=b.clone().sub(a); const len=Math.max(d.length(),1e-4); m.position.copy(a).add(b).multiplyScalar(0.5); m.scale.set(r,len,r); m.quaternion.setFromUnitVectors(UPV,d.multiplyScalar(1/len)); }
  function ball(m,p,r){ m.position.copy(p); m.scale.setScalar(r); }
  function ik(S,Tg,pole){ const d=Tg.clone().sub(S); const dist=Math.min(Math.max(d.length(),0.05),L.upper+L.fore-0.003); const dn=d.normalize();
    const a=(L.upper*L.upper-L.fore*L.fore+dist*dist)/(2*dist); const h=Math.sqrt(Math.max(0,L.upper*L.upper-a*a));
    const p=pole.clone().addScaledVector(dn,-pole.dot(dn)); if(p.lengthSq()<1e-6) p.set(0,-1,0); p.normalize();
    return {E:S.clone().addScaledVector(dn,a).addScaledVector(p,h), Hd:S.clone().addScaledVector(dn,dist)}; }
  // pose: p torso pitch forward, tilt head pitch, hy head yaw, ty upper-body twist, aL/aR thigh angle, kL/kR knee bend,
  // sL/sR arm swing, eL/eR elbow, dy hip offset, fx forward body shift; tL/tR world hand targets with weights wL/wR (two-bone IK), pL/pR elbow poles (local).
  // No face, so the look direction is carried by head lean (hy/tilt move the head off the neck) and upper-body twist (ty).
  const P0={p:0.05,tilt:0,hy:0,ty:0,aL:0.05,aR:-0.05,kL:0.05,kR:0.05,sL:0.12,sR:-0.05,eL:0.2,eR:0.2,dy:0,fx:0};
  const POSES={
    stand:{...P0},
    hunch:{...P0,p:0.42,tilt:0.48,aL:0.12,aR:-0.08,kL:0.18,kR:0.12,sL:0.04,sR:0.02,eL:0.12,eR:0.1},
    crouch:{...P0,p:0.95,tilt:0.1,aL:1.25,aR:0.85,kL:2.05,kR:1.6,dy:-0.02,sL:0.9,sR:0.9,eL:0.2,eR:0.2},
    sit:{...P0,p:0.34,tilt:0.22,hy:-0.1,aL:1.95,aR:1.9,kL:2.58,kR:2.5,dy:-0.2,sL:0.8,sR:0.8,eL:0.6,eR:0.6},          // floor, knees up (use handsOnKnees)
    slump:{...P0,p:0.82,tilt:0.62,hy:-0.95,ty:-0.08,aL:2.08,aR:2.02,kL:2.78,kR:2.7,dy:-0.2,sL:0.5,sR:0.5,eL:0.4,eR:0.4,fx:-0.03},
  };
  const blend=(a,b,u)=>{ const o={}; for(const k in P0) o[k]=lerp(a[k]??P0[k],b[k]??P0[k],u); for(const s of ['L','R']){ const ta=a['t'+s], tb=b['t'+s]; const wa=a['w'+s]||0, wb=b['w'+s]||0;
    if(ta||tb){ o['t'+s]=(ta&&tb)?ta.clone().lerp(tb,u):(ta||tb).clone(); o['w'+s]=lerp(ta?wa:0,tb?wb:0,u); const pa=a['p'+s], pb=b['p'+s]; o['p'+s]=(pa&&pb)?pa.clone().lerp(pb,u).normalize():(pb||pa); /* V3: blend the poles, no mid-blend switch */ } } return o; };
  // world-space joints for a figure standing at root (feet level), facing yaw (local +x forward)
  function skel(P,root,yaw){
    const leg=(a,k)=>{ const kn=[Math.sin(a)*L.thigh,-Math.cos(a)*L.thigh]; const b=a-k; return [kn,[kn[0]+Math.sin(b)*L.shin,kn[1]-Math.cos(b)*L.shin]]; };
    const [kl,fl]=leg(P.aL,P.kL), [kr,fr]=leg(P.aR,P.kR);
    const hipY=-Math.min(fl[1],fr[1])+0.035+P.dy, hipX=-(fl[0]+fr[0])*0.5*0.6+P.fx;
    const W_=(x,y,z)=>rotY(V(x,y,z),yaw).add(root);
    const WU=(x,y,z)=>rotY(rotY(V(x-hipX,y,z),P.ty).add(V(hipX,0,0)),yaw).add(root);
    const J={}; J.hip=W_(hipX,hipY,0); J.hipL=W_(hipX,hipY,0.07); J.hipR=W_(hipX,hipY,-0.07);
    J.kL=W_(hipX+kl[0],hipY+kl[1],0.08); J.fL=W_(hipX+fl[0],hipY+fl[1],0.08); J.kR=W_(hipX+kr[0],hipY+kr[1],-0.08); J.fR=W_(hipX+fr[0],hipY+fr[1],-0.08);
    const nx=hipX+Math.sin(P.p)*L.torso, ny=hipY+Math.cos(P.p)*L.torso; J.neck=WU(nx,ny,0);
    const hd=P.p+P.tilt; const hdir=rotY(rotY(V(Math.sin(hd),Math.cos(hd),0),P.hy),P.ty);
    J.head=J.neck.clone().addScaledVector(rotY(hdir,yaw),L.neck+L.head);
    const shx=nx-Math.sin(P.p)*0.06, shy=ny-Math.cos(P.p)*0.06;
    for(const [s,z] of [['L',0.05],['R',-0.05]]){ const S=WU(shx,shy,z); const sa=clamp(P['s'+s],-0.9,2.6), ea=clamp(P['e'+s],0.05,2.5);   /* V3: joint limits, the forearm never bends backward */
      const E=WU(shx+Math.sin(sa)*L.upper,shy-Math.cos(sa)*L.upper,z*2.2); const Hd=WU(shx+Math.sin(sa)*L.upper+Math.sin(sa+ea)*L.fore,shy-Math.cos(sa)*L.upper-Math.cos(sa+ea)*L.fore,z*2.6);
      let E2=E,H2=Hd; const w=P['w'+s]||0;
      if(w>0&&P['t'+s]){ const tg=Hd.clone().lerp(P['t'+s],w); const pole=rotY(P['p'+s]?P['p'+s].clone():V(-0.35,-1,(s==='L'?1:-1)*0.45),yaw);   /* V3: a fixed anatomical pole (down, back, out), never derived from the FK elbow, so the elbow cannot flip behind the body */ const r=ik(S,tg,pole); E2=r.E; H2=r.Hd; }
      J['sh'+s]=S; J['el'+s]=E2; J['h'+s]=H2; }
    J.fwd=rotY(V(1,0,0),yaw); return J; }
  function poseFig(F,J){ const B=F.bones, r=LIMB/2;
    bone(B[0],J.hip,J.neck,r*1.25); bone(B[1],J.hipL,J.kL,r); bone(B[2],J.kL,J.fL,r); bone(B[3],J.hipR,J.kR,r); bone(B[4],J.kR,J.fR,r);
    bone(B[5],J.shL,J.elL,r); bone(B[6],J.elL,J.hL,r); bone(B[7],J.shR,J.elR,r); bone(B[8],J.elR,J.hR,r);
    [J.hipL,J.hipR,J.kL,J.kR,J.fL,J.fR,J.shL,J.shR,J.elL,J.elR,J.hL,J.hR,J.hip,J.neck].forEach((p,i)=>ball(F.joints[i],p,r*(i>=12?1.25:i>=10?1.3:i>=4&&i<6?1.15:1.0)));
    ball(F.head,J.head,L.head); }
  // walk cycle on top of any pose: phase ph (radians, stride 1.3 m per 2*PI), amplitude a 0..1
  function gait(P,ph,a,A=0.32,K=0.6,arm=0.22){ const s=Math.sin(ph), c=Math.cos(ph);
    return {...P,aL:P.aL+A*a*s,aR:P.aR-A*a*s,kL:P.kL+K*a*Math.max(0,c),kR:P.kR+K*a*Math.max(0,-c),sL:P.sL-arm*a*s,sR:P.sR+arm*a*s}; }
  // seated poses: rest the hands on the knees (s=0) or wrap the shins (s=1)
  function handsOnKnees(P,root,yaw,s=0){ const J=skel(P,root,yaw); const f=J.fwd;
    const knee=(k,ft,side)=>k.clone().lerp(ft,lerp(0.12,0.55,s)).addScaledVector(f,lerp(0.05,0.07,s)).add(V(0,lerp(0.045,0.0,s),0)).addScaledVector(rotY(V(0,0,1),yaw),side*lerp(0,0.05,s));
    return {...P,tL:knee(J.kL,J.fL,1),tR:knee(J.kR,J.fR,-1),wL:1,wR:1,pL:V(-0.2,-0.6,0.8),pR:V(-0.2,-0.6,-0.8)}; }
  return {L,LIMB,P0,POSES,makeFig,skel,poseFig,gait,blend,handsOnKnees,ik}; }
