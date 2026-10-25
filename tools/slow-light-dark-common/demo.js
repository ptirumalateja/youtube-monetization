// Slow Light Dark starter scene: a cream figure sitting under the lamp, one red story object, a grey stranger who
// fades up out of the void and back into it. Copy this file to start a new reel.
import * as THREE from 'three';
import * as SLD from './sld.js';
const {V,sstep,PAL}=SLD;
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960, DUR=6;
const S=SLD.createStage({W,H}); const R=SLD.createRig(S.scene);
const hero=R.makeFig(PAL.CREAM,'hero',{rim:0.16,lift:0.07});
const other=R.makeFig(PAL.SLATE,'other',{rim:0.08,rimCol:0x9fb2d6});
const red=new THREE.Mesh(new THREE.SphereGeometry(0.07,32,16),new THREE.MeshStandardMaterial({color:PAL.RED,roughness:0.38,metalness:0.35,emissive:PAL.RED,emissiveIntensity:0.05}));
red.castShadow=true; red.position.set(-0.6,0.07,0.1); S.scene.add(red); const halo=SLD.glowSprite(S.scene,0xff3a2a,0.03); halo.position.copy(red.position); halo.scale.setScalar(0.3);
const SEAT=V(0.35,0,0.05), YAW=SLD.yawOf(V(-1,0,0.3));
function setT(t){
  const P=R.handsOnKnees({...R.POSES.sit,p:R.POSES.sit.p+0.018*Math.sin(2*Math.PI*0.21*t)},SEAT,YAW,0); R.poseFig(hero,R.skel(P,SEAT,YAW));
  const x=2.8-1.2*t, a=sstep(0,1.6,t)*sstep(0,2.0,(x+2.8)/1.2); other.setAlpha(a);
  if(a>0.004) R.poseFig(other,R.skel(R.gait({...R.P0,p:0.08},(2.8-x)/1.3*2*Math.PI,1),V(x,0,-1.4),Math.PI));
  S.cam.position.set(0.06,0.8,5.6-0.1*t); S.cam.lookAt(V(-0.02,0.5,0)); S.tick(t); }
window.renderAt=(t,K=3)=>S.renderAt(setT,t,K,{t0:0,t1:DUR});
window.ready=true;
