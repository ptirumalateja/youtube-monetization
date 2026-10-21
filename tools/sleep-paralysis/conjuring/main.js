// v4: the same bedroom and rigged wraith as the v2 nightmare scene, relit and regraded as a Conjuring-style
// horror film (candle, sick teal moonlight, red eyes, film grain), cut to the voiceover with title and captions.
import * as T from 'three';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {ShaderPass} from 'three/addons/postprocessing/ShaderPass.js';
import {UnrealBloomPass} from 'three/addons/postprocessing/UnrealBloomPass.js';
import {Wraith} from '../nightmare/wraith.js';
import {Room,ROOM} from '../nightmare/room.js';
import {LightShaft,Particles} from '../nightmare/fx.js';
import {rng,V} from '../nightmare/lib.js';
import {GradeShader} from './grade.js';
import {Overlay} from './overlay.js';
import {SPEC,FACE,build,candle,eyes,beats} from './timeline.js';

const q=new URLSearchParams(location.search);const Wd=+q.get('w')||SPEC.width,Hd=+q.get('h')||SPEC.height;
await Promise.all(['900 40px Cinzel','700 40px Oswald'].map(f=>document.fonts.load(f)));
const D=build(await (await fetch('./audio/vo_v4_timestamps.json')).json());const BEATS=beats(D.T);

const renderer=new T.WebGLRenderer({antialias:false,preserveDrawingBuffer:true,powerPreference:'high-performance'});
renderer.setPixelRatio(1);renderer.setSize(Wd,Hd);renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;renderer.outputColorSpace=T.LinearSRGBColorSpace;
const scene=new T.Scene();const fogC=new T.Color(.004,.009,.009);scene.background=fogC.clone();scene.fog=new T.FogExp2(fogC,.07);
const cam=new T.PerspectiveCamera(50,Wd/Hd,.02,120);

// ---------- the room, re-dressed: stained 70s wallpaper, dark varnished wood, dingy linen; no hatching
const wraith=new Wraith(scene);wraith.root.scale.setScalar(1.17);wraith.uniforms.uGrowShift.value=40;wraith.uniforms.uSwayAmp.value=.02;
const room=new Room(scene,wraith.uniforms);
function wallpaper(){const c=document.createElement('canvas');c.width=c.height=1024;const x=c.getContext('2d'),R=rng(1971);
 x.fillStyle='#7d8a6c';x.fillRect(0,0,1024,1024);
 for(let i=0;i<8;i++){x.fillStyle=i%2?'rgba(60,72,50,.35)':'rgba(150,150,110,.18)';x.fillRect(i*128,0,64,1024);}
 for(let yy=0;yy<1024;yy+=128)for(let xx=(yy/128%2)*64;xx<1024+64;xx+=128){x.strokeStyle='rgba(45,55,38,.55)';x.lineWidth=3;x.beginPath();
  x.moveTo(xx,yy+10);x.bezierCurveTo(xx+30,yy+30,xx+30,yy+70,xx,yy+100);x.bezierCurveTo(xx-30,yy+70,xx-30,yy+30,xx,yy+10);x.stroke();x.beginPath();x.arc(xx,yy+55,8,0,7);x.stroke();}
 for(let i=0;i<55;i++){const g=x.createRadialGradient(0,0,0,0,0,1);const cx=R()*1024,cy=R()*1024,r=30+R()*160;x.save();x.translate(cx,cy);x.scale(r,r*(1+R()*2));
  g.addColorStop(0,`rgba(${50+R()*30|0},${45+R()*20|0},20,${.25+R()*.3})`);g.addColorStop(1,'rgba(0,0,0,0)');x.fillStyle=g;x.beginPath();x.arc(0,0,1,0,7);x.fill();x.restore();}
 for(let i=0;i<40;i++){x.strokeStyle=`rgba(40,30,15,${.15+R()*.25})`;x.lineWidth=1+R()*3;const sx=R()*1024;let sy=R()*500;x.beginPath();x.moveTo(sx,sy);for(let k=0;k<12;k++){sy+=20+R()*30;x.lineTo(sx+(R()-.5)*6,sy);}x.stroke();}
 const t=new T.CanvasTexture(c);t.wrapS=t.wrapT=T.RepeatWrapping;t.colorSpace=T.SRGBColorSpace;t.anisotropy=8;return t;}
const wp=wallpaper();
const recolor=new Map([[room.mats.wall,{map:wp,color:[.62,.66,.56]}],[room.mats.wood,{color:[.085,.05,.032],roughness:.55}],[room.mats.cloth,{color:[.5,.47,.42]}]]);
room.group.traverse(o=>{if(!o.isMesh||!o.material||!o.material.isMeshLambertMaterial)return;const m=o.material;
 let spec=recolor.get(m);const g=m.color.r;
 if(!spec){if(m.map&&m.map.image&&m.map.image.width===1024)spec={map:m.map,color:[.32,.2,.12],roughness:.6};          // floorboards
  else if(m.map)spec={map:m.map,color:[.5,.5,.45]};                                                                 // pictures
  else if(o===room.blanket)spec={color:[.36,.3,.26]};
  else if(m.transparent)spec={color:[.55,.6,.52]};                                                                  // sheer curtains
  else if(Math.abs(g-.62)<.01)spec={color:[.2,.21,.19]};                                                            // ceiling
  else if(g<.45)spec={color:[.12,.075,.05],roughness:.6};                                                           // door, panels, shade
  else spec={color:[.05,.055,.05]};}                                                                                // the corridor walls: dark
 o.material=new T.MeshStandardMaterial({map:spec.map||null,color:new T.Color(...spec.color),roughness:spec.roughness??.9,metalness:0,transparent:m.transparent,opacity:m.opacity,side:m.side,flatShading:m.flatShading,depthWrite:m.depthWrite});});
wp.repeat.set(1.6,1.4);
room.group.traverse(o=>{if(o.isMesh&&o.material.isMeshBasicMaterial&&!o.material.map&&o.geometry.type==='PlaneGeometry')o.material.color.setRGB(.01,.02,.018);});  // the corridor beyond the door is black
room.sky.material.color.setRGB(.18,.26,.25);
// the bedside lamp goes; the candle and the clock take its place
room.group.traverse(o=>{if(o.isMesh&&o.geometry.type==='CylinderGeometry'&&Math.abs(o.position.x-(ROOM.bed.x0+.3))<.01)o.visible=false;});

// ---------- the sleeper: the engraved head asset on the pillow, now lit by the candle
const atlas=await new T.TextureLoader().loadAsync('../assets/generated/sleeper-head-hand-atlas-v1.png');atlas.colorSpace=T.SRGBColorSpace;atlas.anisotropy=8;
const headMat=new T.MeshLambertMaterial({map:atlas,transparent:true,alphaTest:.04,color:new T.Color(1.15,1.1,1.05),emissive:new T.Color(.012,.016,.015)});atlas.repeat.set(860/1774,1);
const pxm=.00062,head=new T.Mesh(new T.PlaneGeometry(860*pxm,887*pxm),headMat);
head.position.set(-2.95+(430-330)*pxm,.86-(443.5-420)*pxm,-.64);head.renderOrder=1;scene.add(head);
function eyeTexture(){const c=document.createElement('canvas');c.width=256;c.height=128;const x=c.getContext('2d'),R=rng(5);
 x.save();x.beginPath();x.moveTo(8,118);x.bezierCurveTo(60,20,170,6,248,96);x.bezierCurveTo(180,124,70,128,8,118);x.closePath();x.clip();
 const g=x.createLinearGradient(0,0,0,128);g.addColorStop(0,'#6a5f55');g.addColorStop(.45,'#cdbfae');g.addColorStop(1,'#9c8c7e');x.fillStyle=g;x.fillRect(0,0,256,128);
 for(let i=0;i<16;i++){x.strokeStyle=`rgba(160,10,10,${.35+R()*.4})`;x.lineWidth=.6+R()*.8;x.beginPath();let a=R()<.5?10:244,b=60+R()*50;x.moveTo(a,b);for(let k=0;k<6;k++){a+=(a<128?1:-1)*(8+R()*12);b+=(R()-.5)*14;x.lineTo(a,b);}x.stroke();}
 const ix=176,iy=66,ig=x.createRadialGradient(ix,iy,3,ix,iy,40);ig.addColorStop(0,'#020202');ig.addColorStop(.5,'#060606');ig.addColorStop(.62,'#3a3128');ig.addColorStop(1,'#16120f');x.fillStyle=ig;x.beginPath();x.ellipse(ix,iy,30,38,0,0,7);x.fill();
 x.fillStyle='rgba(255,240,220,.9)';x.beginPath();x.ellipse(ix+9,iy-12,4,3,0,0,7);x.fill();
 const sh=x.createLinearGradient(0,0,0,60);sh.addColorStop(0,'rgba(0,0,0,.85)');sh.addColorStop(1,'rgba(0,0,0,0)');x.fillStyle=sh;x.fillRect(0,0,256,60);x.restore();
 x.strokeStyle='#0a0908';x.lineWidth=7;x.beginPath();x.moveTo(6,118);x.bezierCurveTo(60,18,170,4,250,96);x.stroke();
 for(let i=0;i<34;i++){const u=i/33,px=6+u*244,py=118-Math.sin(u*Math.PI)*96+(u>.6?(u-.6)*-30:0);x.lineWidth=1.6;x.beginPath();x.moveTo(px,py);x.lineTo(px+4+u*6,py-14-R()*8);x.stroke();}
 const t=new T.CanvasTexture(c);t.colorSpace=T.SRGBColorSpace;return t;}
const eyePivot=new T.Group();eyePivot.position.set(4*pxm,(443.5-284)*pxm,.002);eyePivot.rotation.z=.26;head.add(eyePivot);
const eyeMesh=new T.Mesh(new T.PlaneGeometry(64*pxm,32*pxm),new T.MeshLambertMaterial({map:eyeTexture(),transparent:true,color:new T.Color(1.2,1.15,1.1),emissive:new T.Color(.02,.02,.02)}));eyeMesh.geometry.translate(0,16*pxm,0);eyeMesh.renderOrder=2;eyePivot.add(eyeMesh);

// ---------- props: a guttering candle and a digital clock on the nightstand
const NS={x:ROOM.bed.x0+.25,z:ROOM.bed.z1+.36,top:.63};
const flameTex=(()=>{const c=document.createElement('canvas');c.width=64;c.height=128;const x=c.getContext('2d');const g=x.createRadialGradient(32,88,2,32,80,40);
 g.addColorStop(0,'rgba(255,250,230,1)');g.addColorStop(.25,'rgba(255,200,110,.95)');g.addColorStop(.6,'rgba(255,110,30,.5)');g.addColorStop(1,'rgba(255,60,0,0)');
 x.fillStyle=g;x.beginPath();x.moveTo(32,4);x.bezierCurveTo(52,60,58,90,32,124);x.bezierCurveTo(6,90,12,60,32,4);x.fill();return new T.CanvasTexture(c);})();
const candleG=new T.Group();candleG.position.set(NS.x+.12,NS.top,NS.z-.13);scene.add(candleG);
{const wax=new T.MeshStandardMaterial({color:new T.Color(.62,.58,.48),roughness:.5,emissive:new T.Color(.12,.06,.02)});
 const dish=new T.Mesh(new T.CylinderGeometry(.06,.05,.012,20),new T.MeshStandardMaterial({color:new T.Color(.25,.2,.12),metalness:.6,roughness:.4}));dish.position.y=.006;candleG.add(dish);
 const stub=new T.Mesh(new T.CylinderGeometry(.022,.024,.09,16),wax);stub.position.y=.057;stub.castShadow=false;candleG.add(stub);
 for(let i=0;i<3;i++){const dr=new T.Mesh(new T.SphereGeometry(.007,6,6),wax);dr.scale.set(1,2.4,1);dr.position.set(Math.cos(i*2.2)*.022,.07-i*.012,Math.sin(i*2.2)*.022);candleG.add(dr);}
 const wick=new T.Mesh(new T.CylinderGeometry(.0015,.0015,.014,4),new T.MeshBasicMaterial({color:0x050302}));wick.position.y=.109;candleG.add(wick);}
const flame=new T.Sprite(new T.SpriteMaterial({map:flameTex,color:new T.Color(1.8,1.25,.75),blending:T.AdditiveBlending,depthWrite:false,fog:false}));flame.center.set(.5,.08);flame.position.y=.105;flame.scale.set(.028,.06,1);candleG.add(flame);
const halo=new T.Sprite(new T.SpriteMaterial({map:flameTex,color:new T.Color(.5,.25,.08),blending:T.AdditiveBlending,depthWrite:false,fog:false,opacity:.5}));halo.position.y=.13;halo.scale.set(.18,.2,1);candleG.add(halo);
const candleLight=new T.PointLight(new T.Color(1,.56,.24),1.4,0,2);candleLight.position.set(0,.16,0);candleLight.castShadow=true;candleLight.shadow.mapSize.set(1024,1024);candleLight.shadow.bias=-.002;candleLight.shadow.radius=4;candleG.add(candleLight);
// clock
const clockC=document.createElement('canvas');clockC.width=256;clockC.height=110;const clockX=clockC.getContext('2d');const clockT=new T.CanvasTexture(clockC);clockT.colorSpace=T.SRGBColorSpace;
let clockShown='';function setClock(s){if(s===clockShown)return;clockShown=s;const x=clockX;x.fillStyle='#050404';x.fillRect(0,0,256,110);x.font='700 92px Oswald';x.textAlign='center';x.textBaseline='middle';
 x.fillStyle='rgba(90,0,0,.35)';x.fillText('8:88',128,58);x.fillStyle='#ff2414';x.shadowColor='#ff0000';x.shadowBlur=16;x.fillText(s,128,58);x.shadowBlur=0;x.font='700 18px Oswald';x.fillText('AM',232,24);clockT.needsUpdate=true;}
setClock('2:59');
const clock=new T.Group();clock.position.set(NS.x+.06,NS.top,NS.z+.14);clock.rotation.y=.95;scene.add(clock);
{const body=new T.Mesh(new T.BoxGeometry(.2,.09,.07),new T.MeshStandardMaterial({color:new T.Color(.03,.03,.03),roughness:.4}));body.position.y=.045;body.castShadow=true;clock.add(body);
 const face=new T.Mesh(new T.PlaneGeometry(.17,.072),new T.MeshBasicMaterial({map:clockT,color:new T.Color(2.2,2.2,2.2),fog:false}));face.position.set(0,.046,.0355);clock.add(face);}
const clockGlow=new T.PointLight(new T.Color(1,.05,.02),.05,0,2);clockGlow.position.set(0,.06,.12);clock.add(clockGlow);

// ---------- its eyes: two embers inside the tangled skull, with glow and a red spill light
const eyeGlowTex=(()=>{const c=document.createElement('canvas');c.width=c.height=64;const x=c.getContext('2d');const g=x.createRadialGradient(32,32,0,32,32,32);g.addColorStop(0,'rgba(255,255,255,1)');g.addColorStop(.2,'rgba(255,255,255,.6)');g.addColorStop(1,'rgba(255,255,255,0)');x.fillStyle=g;x.fillRect(0,0,64,64);return new T.CanvasTexture(c);})();
const redEyes=[];for(const s of [-1,1]){const g=new T.Group();g.position.set(s*.043,.07,.245);wraith.bones.head.add(g);
 const core=new T.Mesh(new T.SphereGeometry(.011,10,8),new T.MeshBasicMaterial({color:new T.Color(9,.6,.3),fog:false}));core.scale.set(1.5,.7,.6);core.rotation.z=-s*.25;g.add(core);
 const gl=new T.Sprite(new T.SpriteMaterial({map:eyeGlowTex,color:new T.Color(1.6,.04,.02),blending:T.AdditiveBlending,depthWrite:false,fog:false}));gl.scale.set(.14,.1,1);g.add(gl);redEyes.push({g,core,gl});}
const eyeLight=new T.PointLight(new T.Color(1,.04,.02),0,0,2);eyeLight.position.set(0,.06,.35);wraith.bones.head.add(eyeLight);

// ---------- light: sick teal moonlight through the barred window, a cold whisper of fill
const lightDir=V(1,-.55,.42).normalize();
const moon=new T.DirectionalLight(new T.Color(.42,.78,.72),.9);moon.position.copy(V(-1.5,1.2,-1.2).addScaledVector(lightDir,-9));moon.target.position.copy(V(-1.5,1.2,-1.2));scene.add(moon,moon.target);
moon.castShadow=true;moon.shadow.mapSize.set(2048,2048);Object.assign(moon.shadow.camera,{left:-6,right:6,top:6,bottom:-6,near:.5,far:22});moon.shadow.bias=-.0004;moon.shadow.normalBias=.02;
const hemi=new T.HemisphereLight(new T.Color(.25,.42,.4),new T.Color(.05,.04,.03),.22);scene.add(hemi);
// faint teal from the corridor so its silhouette can be read against the doorway
const hall=new T.PointLight(new T.Color(.35,.7,.62),2.2,0,2);hall.position.set(1.7,1.6,-3.6);scene.add(hall);
// a cold pool of light on the wall behind it, so its shape always reads as a silhouette
const backL=new T.PointLight(new T.Color(.4,.78,.7),2.4,0,2);scene.add(backL);
const shaft=new LightShaft(scene,lightDir);shaft.u.uGain.value=.55;
const parts=new Particles(scene,shaft);parts.red.visible=false;

// ---------- post
const rt=new T.WebGLRenderTarget(Wd,Hd,{type:T.HalfFloatType,samples:4});
const composer=new EffectComposer(renderer,rt);composer.setPixelRatio(1);composer.setSize(Wd,Hd);
composer.addPass(new RenderPass(scene,cam));
const bloom=new UnrealBloomPass(new T.Vector2(Wd,Hd),.6,.5,1.1);composer.addPass(bloom);
const grade=new ShaderPass(GradeShader);grade.uniforms.uRes.value.set(Wd,Hd);composer.addPass(grade);
const out=document.createElement('canvas');out.width=Wd;out.height=Hd;const ox=out.getContext('2d');document.body.appendChild(out);
const overlay=new Overlay(Wd,Hd,D);

const smooth=(a,b,x)=>{const t=Math.min(1,Math.max(0,(x-a)/(b-a)));return t*t*(3-2*t);};
const noise=(t,s)=>Math.sin(t*13.1+s)*.5+Math.sin(t*29.7+s*2.3)*.3+Math.sin(t*51.3+s*4.1)*.2;
const headW=new T.Vector3();
function update(t){
 const T_=D.T,sh=D.shots.find(s=>t>=s.t0&&t<s.t1)||D.shots[D.shots.length-1];const u=(t-sh.t0)/(sh.t1-sh.t0);
 const fx={candle:candle(t,T_)};
 if(sh.black){grade.uniforms.uFade.value=1;return fx;}
 grade.uniforms.uFade.value=0;
 // the thing
 const w=sh.wraith(u,t);wraith.root.position.set(w.x,w.y,w.z);wraith.root.rotation.y=w.rot;backL.position.set(w.x+.15,1.9,Math.max(-2.85,w.z-.55));backL.intensity=sh.i>=8?.6:2.4;
 wraith.pose(t,{reach:w.reach,open:w.open,claw:w.claw,lean:w.lean,headTilt:w.headTilt,headTurn:w.headTurn,headDown:w.headDown});
 wraith.uniforms.uPulseGain.value=1.2+.6*Math.sin(t*2);
 const e=eyes(t,T_);for(const r of redEyes){r.core.visible=r.gl.visible=e>0;r.core.material.color.setRGB(9*e,.6*e,.3*e);r.gl.material.color.setRGB(1.6*e,.04*e,.02*e);}eyeLight.intensity=.25*e;
 wraith.root.updateMatrixWorld(true);wraith.bones.head.getWorldPosition(headW);
 // the sleeper
 room.animateBlanket(t,t>T_.body-.3&&t<T_.trapped?Math.max(0,Math.sin((t-T_.body+.3)*7))*.9:0);room.animateCurtains(t);
 const eo=t<T_.wake?0:Math.min(1.08,(t-T_.wake)/.12);eyeMesh.visible=eo>.01;eyeMesh.scale.y=Math.max(.001,eo>1?1+.04*Math.sin(t*40):eo);
 // candle and clock
 const c=fx.candle;candleLight.intensity=.9*c;flame.visible=halo.visible=c>.02;flame.scale.set(.026+.004*c,.05*(.7+.4*c)+.006*Math.sin(t*17),1);flame.material.rotation=.06*Math.sin(t*5.3);halo.material.opacity=.22*c;
 setClock(t<T_.three?'2:59':'3:00');
 // heartbeat: the frame throbs red from "corner" on
 let hb=0;for(const b of BEATS){const d=t-b;if(d>=0&&d<.5)hb=Math.max(hb,Math.exp(-d*9)+.6*Math.exp(-Math.max(0,d-.17)*10)*(d>.17));}
 grade.uniforms.uRed.value=t>T_.corner?Math.min(1,hb*.55*(.5+.5*smooth(T_.corner,T_.black,t))):0;
 // camera
 const cv=sh.cam(u,{head:headW.toArray()});const p=cv.pos,l=[...cv.look];
 const sk=cv.shake||.0004;l[0]+=noise(t,1)*sk*60;l[1]+=noise(t,2)*sk*60;l[2]+=noise(t,3)*sk*30;
 cam.position.set(...p);cam.up.set(0,1,0);cam.lookAt(...l);if(cv.roll)cam.rotateZ(cv.roll);
 let fov=cv.fov;if(sh.i===2||sh.i===6)fov*=1-.035*hb;cam.fov=fov;cam.updateProjectionMatrix();
 head.rotation.y=Math.max(-.2,Math.min(.75,Math.atan2(cam.position.x-head.position.x,cam.position.z-head.position.z)*.7));
 parts.update(t,Hd/(2*Math.tan(cam.fov*Math.PI/360)),fogC,scene.fog.density);shaft.u.uTime.value=t;
 grade.uniforms.uTime.value=t;grade.uniforms.uFrame.value=Math.round(t*SPEC.fps);
 grade.uniforms.uExpo.value=(sh.i===8?.85:1.2)*(.94+.06*c);
 return fx;
}
function draw(t){const fx=update(t);composer.render();ox.drawImage(renderer.domElement,0,0);overlay.draw(ox,t,fx);}
window.renderJpg=t=>{draw(t);return out.toDataURL('image/jpeg',.94);};
window.diag=()=>({head:headW.toArray().map(v=>+v.toFixed(2)),calls:renderer.info.render.calls,tris:renderer.info.render.triangles});
window.timing=D.T;window.cuts=D.shots.map(s=>+s.t0.toFixed(2));
draw(+q.get('t')||0);
window.ready=true;
