import * as T from 'three';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {ShaderPass} from 'three/addons/postprocessing/ShaderPass.js';
import {Wraith} from './wraith.js';
import {Room,ROOM} from './room.js';
import {LightShaft,Particles} from './fx.js';
import {GradeShader,paperTexture} from './post.js';
import {SPEC,camPos,camLook,camFov,W,FX} from './timeline.js';
import {V} from './lib.js';

const q=new URLSearchParams(location.search);const Wd=+q.get('w')||SPEC.width,Hd=+q.get('h')||SPEC.height;
const renderer=new T.WebGLRenderer({antialias:false,preserveDrawingBuffer:true,powerPreference:'high-performance'});
renderer.setPixelRatio(1);renderer.setSize(Wd,Hd);renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;renderer.outputColorSpace=T.LinearSRGBColorSpace;
document.body.appendChild(renderer.domElement);
const scene=new T.Scene();const fogC=new T.Color(.2,.2,.205);scene.background=fogC.clone();scene.fog=new T.FogExp2(fogC,q.has('nofog')?0:.085);
const cam=new T.PerspectiveCamera(56,Wd/Hd,.03,120);

// the thing
const wraith=new Wraith(scene);
wraith.root.position.set(-1.9,0,-2.1);wraith.root.rotation.y=-.6;wraith.root.scale.setScalar(1.17);
// a pool of ink where it stands
{const c=document.createElement('canvas');c.width=c.height=256;const x=c.getContext('2d');let s=7;const R=()=>{s=(s*1664525+1013904223)>>>0;return s/4294967296;};
 for(let i=0;i<60;i++){const a=R()*6.28,r=R()*90;x.fillStyle=`rgba(0,0,0,${.15+R()*.4})`;x.beginPath();x.ellipse(128+Math.cos(a)*r,128+Math.sin(a)*r*.7,6+R()*40,4+R()*22,R()*3,0,7);x.fill();}
 for(let i=0;i<14;i++){x.fillStyle='rgba(110,6,6,.55)';x.beginPath();x.arc(128+(R()-.5)*170,128+(R()-.5)*120,1+R()*4,0,7);x.fill();}
 const t=new T.CanvasTexture(c);t.colorSpace=T.SRGBColorSpace;const m=new T.Mesh(new T.PlaneGeometry(1.8,1.8),new T.MeshBasicMaterial({map:t,transparent:true,depthWrite:false,fog:true}));m.rotation.x=-Math.PI/2;m.position.set(-1.9,.004,-2.1);scene.add(m);}

const room=new Room(scene,wraith.uniforms);

// sleeper: the separately authored engraved head (project asset) registered on the pillow
const atlas=await new T.TextureLoader().loadAsync('../assets/generated/sleeper-head-hand-atlas-v1.png');atlas.colorSpace=T.SRGBColorSpace;atlas.anisotropy=8;
const headMat=new T.MeshBasicMaterial({map:atlas.clone(),transparent:true,alphaTest:.04,fog:true,color:new T.Color(.78,.78,.78)});headMat.map.repeat.set(860/1774,1);headMat.map.offset.set(0,0);headMat.map.needsUpdate=true;
const pxm=.00062,head=new T.Mesh(new T.PlaneGeometry(860*pxm,887*pxm),headMat);
// image (330,420) is the head centre; place it on the pillow
head.position.set(-2.95+(430-330)*pxm,.86-(443.5-420)*pxm,-.64);head.renderOrder=1;scene.add(head);
// the open eye: an engraved overlay registered on the closed lid; the upper lid lifts from the crease
function eyeTexture(){const c=document.createElement('canvas');c.width=256;c.height=128;const x=c.getContext('2d');let sd=5;const R=()=>{sd=(sd*1664525+1013904223)>>>0;return sd/4294967296;};
 x.save();x.beginPath();x.moveTo(8,118);x.bezierCurveTo(60,20,170,6,248,96);x.bezierCurveTo(180,124,70,128,8,118);x.closePath();x.clip();
 const g=x.createLinearGradient(0,0,0,128);g.addColorStop(0,'#5a5650');g.addColorStop(.45,'#b9b3a8');g.addColorStop(1,'#8d877e');x.fillStyle=g;x.fillRect(0,0,256,128);
 for(let i=0;i<9;i++){x.strokeStyle=`rgba(125,12,10,${.25+R()*.3})`;x.lineWidth=.8;x.beginPath();let a=R()<.5?14:240,b=70+R()*40;x.moveTo(a,b);for(let k=0;k<5;k++){a+=(a<128?1:-1)*(8+R()*14);b+=(R()-.5)*14;x.lineTo(a,b);}x.stroke();}
 const ix=176,iy=66;const ig=x.createRadialGradient(ix,iy,4,ix,iy,40);ig.addColorStop(0,'#050505');ig.addColorStop(.42,'#0b0b0b');ig.addColorStop(.6,'#2c2a27');ig.addColorStop(1,'#141312');x.fillStyle=ig;x.beginPath();x.ellipse(ix,iy,30,38,0,0,7);x.fill();
 for(let i=0;i<40;i++){const a=R()*6.28;x.strokeStyle=`rgba(200,195,185,${R()*.18})`;x.beginPath();x.moveTo(ix+Math.cos(a)*14,iy+Math.sin(a)*16);x.lineTo(ix+Math.cos(a)*29,iy+Math.sin(a)*36);x.stroke();}
 x.fillStyle='rgba(235,230,220,.85)';x.beginPath();x.ellipse(ix+9,iy-12,4,3,0,0,7);x.fill();
 const sh=x.createLinearGradient(0,0,0,70);sh.addColorStop(0,'rgba(0,0,0,.85)');sh.addColorStop(1,'rgba(0,0,0,0)');x.fillStyle=sh;x.fillRect(0,0,256,70);x.restore();
 x.strokeStyle='#0a0908';x.lineWidth=7;x.beginPath();x.moveTo(6,118);x.bezierCurveTo(60,18,170,4,250,96);x.stroke();
 for(let i=0;i<34;i++){const u=i/33;const px=6+u*244,py=118-Math.sin(u*Math.PI)*96+ (u>.6?(u-.6)*-30:0);x.lineWidth=1.6;x.beginPath();x.moveTo(px,py);x.lineTo(px+4+u*6,py-14-R()*8);x.stroke();}
 x.lineWidth=2.5;x.strokeStyle='rgba(20,18,16,.8)';x.beginPath();x.moveTo(8,118);x.bezierCurveTo(70,128,180,124,248,96);x.stroke();
 const t=new T.CanvasTexture(c);t.colorSpace=T.SRGBColorSpace;return t;}
const eyePivot=new T.Group();eyePivot.position.set(4*pxm,(443.5-284)*pxm,.002);eyePivot.rotation.z=.26;head.add(eyePivot);
const eyeMesh=new T.Mesh(new T.PlaneGeometry(64*pxm,32*pxm),new T.MeshBasicMaterial({map:eyeTexture(),transparent:true,fog:true,color:new T.Color(.9,.9,.9)}));eyeMesh.geometry.translate(0,16*pxm,0);eyeMesh.renderOrder=2;eyePivot.add(eyeMesh);
const handMat=new T.MeshBasicMaterial({map:atlas.clone(),transparent:true,alphaTest:.04,fog:true,color:new T.Color(.72,.72,.72)});handMat.map.repeat.set(880/1774,330/887);handMat.map.offset.set(894/1774,1-(720/887));handMat.map.needsUpdate=true;
const hand=new T.Group();hand.visible=false;hand.position.set(-2.12,.80,-.16);scene.add(hand);const handCard=new T.Mesh(new T.PlaneGeometry(880*pxm*.62,330*pxm*.62),handMat);handCard.position.set(880*pxm*.31-.06,0,0);hand.add(handCard);

// moonlight: enters through the barred window and throws the room's only hard light
const lightDir=V(1,-.55,.42).normalize();
const moon=new T.DirectionalLight(new T.Color(.93,.94,1),4.2);moon.position.copy(V(-1.5,1.2,-1.2).addScaledVector(lightDir,-9));moon.target.position.copy(V(-1.5,1.2,-1.2));scene.add(moon,moon.target);
moon.castShadow=true;moon.shadow.mapSize.set(4096,4096);Object.assign(moon.shadow.camera,{left:-6,right:6,top:6,bottom:-6,near:.5,far:22});moon.shadow.bias=-.0004;moon.shadow.normalBias=.02;moon.shadow.radius=2;
const hemi=new T.HemisphereLight(new T.Color(.75,.76,.8),new T.Color(.25,.24,.25),2.0);scene.add(hemi);
// the corridor glow spilling through the door
const hall=new T.PointLight(new T.Color(1,.97,.9),2.2,7,1.6);hall.position.set(1.7,1.6,-3.3);scene.add(hall);

const shaft=new LightShaft(scene,lightDir);
const parts=new Particles(scene,shaft);

// post
const rt=new T.WebGLRenderTarget(Wd,Hd,{type:T.HalfFloatType,samples:4});
const composer=new EffectComposer(renderer,rt);composer.setPixelRatio(1);composer.setSize(Wd,Hd);
composer.addPass(new RenderPass(scene,cam));const grade=new ShaderPass(GradeShader);grade.uniforms.uRes.value.set(Wd,Hd);grade.uniforms.uPaper.value=paperTexture();composer.addPass(grade);

if(q.has('solo')){room.group.visible=false;head.visible=hand.visible=false;scene.background=new T.Color(.45,.45,.45);}
if(q.has('nopost'))composer.passes[1].enabled=false;
const qc=q.get('cam'),ql=q.get('look');
function update(t){
 const k={reach:W.reach(t),open:W.open(t),claw:W.claw(t),lean:W.lean(t),headTilt:W.headTilt(t),headTurn:W.headTurn(t),headDown:W.headDown(t)};
 wraith.pose(t,k);wraith.uniforms.uPulseGain.value=FX.pulse(t);
 room.animateBlanket(t,FX.attempt(t));room.animateCurtains(t);
 eyeMesh.scale.y=Math.max(.001,FX.eye(t));eyeMesh.visible=FX.eye(t)>.01;
 hand.rotation.z=FX.attempt(t)*.07+Math.sin(t*9)*.004*FX.attempt(t);
 const mo=FX.moon(t);moon.intensity=4.2*mo;shaft.u.uGain.value=mo;shaft.u.uTime.value=t;
 const p=qc?qc.split(',').map(Number):camPos(t),l=ql?ql.split(',').map(Number):camLook(t);
 cam.position.set(...p);cam.lookAt(...l);cam.fov=+q.get('fov')||camFov(t);cam.updateProjectionMatrix();
 head.rotation.y=Math.max(-.2,Math.min(.75,Math.atan2(cam.position.x-head.position.x,cam.position.z-head.position.z)*.7));
 parts.update(t,Hd/ (2*Math.tan(cam.fov*Math.PI/360)) /1000*1000,fogC,scene.fog.density);
 grade.uniforms.uInk.value=FX.ink(t);grade.uniforms.uTime.value=t;
}
function draw(t){update(t);composer.render();}
window.renderAt=t=>{draw(t);return renderer.domElement.toDataURL('image/png');};
window.renderJpg=t=>{draw(t);return renderer.domElement.toDataURL('image/jpeg',.93);};
window.diag=()=>({wristR:wraith.bones.wristR.getWorldPosition(new T.Vector3()).toArray().map(v=>+v.toFixed(2)),head:wraith.bones.head.getWorldPosition(new T.Vector3()).toArray().map(v=>+v.toFixed(2)),joints:wraith.jointScales().every(s=>s.every(v=>v===1)),tris:renderer.info.render.triangles,calls:renderer.info.render.calls});
draw(+q.get('t')||0);
window.ready=true;
