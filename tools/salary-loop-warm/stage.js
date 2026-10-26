// Warm stage for The Salary Loop (a lived-in, Pixar-like look: warm practical lights, soft shadows, bloom, vignette, grain).
// One fixed pool of lights is re-aimed per set (the shader never recompiles). renderAt() accumulates sub-frames for motion blur.
import * as THREE from 'three';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {UnrealBloomPass} from 'three/addons/postprocessing/UnrealBloomPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';
import {ShaderPass} from 'three/addons/postprocessing/ShaderPass.js';
export const V=(x,y,z)=>new THREE.Vector3(x,y,z);
export const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
export const sstep=(a,b,x)=>{const t=clamp((x-a)/(b-a));return t*t*(3-2*t)};
export const lerp=(a,b,t)=>a+(b-a)*t;
export function createWarmStage({W,H}){
  const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true}); renderer.setPixelRatio(1); renderer.setSize(W,H);
  renderer.shadowMap.enabled=true; renderer.shadowMap.type=THREE.PCFSoftShadowMap; renderer.shadowMap.autoUpdate=false;
  renderer.toneMapping=THREE.ACESFilmicToneMapping; renderer.toneMappingExposure=1.05; document.body.appendChild(renderer.domElement);
  const scene=new THREE.Scene(); scene.background=new THREE.Color(0x1a1210); scene.fog=new THREE.Fog(0x1a1210,6,22);
  const cam=new THREE.PerspectiveCamera(36,W/H,0.05,80);
  const hemi=new THREE.HemisphereLight(0xffd9b0,0x3a2a22,0.55); scene.add(hemi);
  const key=new THREE.SpotLight(0xffb866,90,0,0.9,0.7,1.4); key.castShadow=true; key.shadow.mapSize.set(1536,1536); key.shadow.bias=-0.0003; key.shadow.normalBias=0.02; key.shadow.camera.near=0.5; key.shadow.camera.far=16; scene.add(key,key.target);
  const lampA=new THREE.PointLight(0xffa24a,3.0,7,1.6), lampB=new THREE.PointLight(0xff9a40,2.0,6,1.6), fill=new THREE.PointLight(0x78a6ff,1.2,12,1.5); scene.add(lampA,lampB,fill);
  const rim=new THREE.DirectionalLight(0x9fc4ff,0.5); rim.position.set(-3,4,-3); scene.add(rim,rim.target);
  const composer=new EffectComposer(renderer); composer.setSize(W,H); composer.addPass(new RenderPass(scene,cam));
  const bloom=new UnrealBloomPass(new THREE.Vector2(W,H),0.38,0.75,0.82); composer.addPass(bloom);
  const grade=new ShaderPass({uniforms:{tDiffuse:{value:null},uT:{value:0},uAsp:{value:W/H},uWarm:{value:1.0},uFlash:{value:0}},vertexShader:`varying vec2 vU; void main(){ vU=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
    fragmentShader:`varying vec2 vU; uniform sampler2D tDiffuse; uniform float uT,uAsp,uWarm,uFlash;
     float h(vec2 p){ return fract(sin(dot(p,vec2(12.9898,78.233))+uT*37.0)*43758.5453); }
     void main(){ vec2 c=vU-0.5; float r2=dot(c*vec2(uAsp,1.0),c*vec2(uAsp,1.0)); vec3 col=texture2D(tDiffuse,vU).rgb;
      col=vec3(1.0)-exp(-1.12*col); col*=vec3(1.04,1.0,0.94*mix(1.0,1.0,uWarm)); col=mix(col,col*col*(3.0-2.0*col),0.35);   // soft S-curve, warm tint
      col*=1.0-smoothstep(0.08,0.46,r2)*0.5; col+=(h(vU*vec2(uAsp,1.0)*900.0)-0.5)*0.012*(0.4+col); col+=vec3(1.0,0.86,0.6)*uFlash;
      gl_FragColor=vec4(max(col,0.0),1.0);} `});
  composer.addPass(grade); composer.addPass(new OutputPass());
  const acc=document.createElement('canvas'); acc.width=W; acc.height=H; const actx=acc.getContext('2d');
  return {W,H,renderer,scene,cam,hemi,key,lampA,lampB,fill,rim,bloom,grade,composer,
    renderAt(setT,t,Ksub=3,{t0=0,t1=1e9,shutter=1/60}={}){ actx.globalAlpha=1; actx.clearRect(0,0,W,H);
      for(let k=0;k<Ksub;k++){ const tt=clamp(t+(Ksub>1?(k/(Ksub-1)-0.5)*shutter:0),t0,t1-1e-4); setT(tt,k,Ksub); renderer.shadowMap.needsUpdate=true; composer.render(); actx.globalAlpha=1/(k+1); actx.drawImage(renderer.domElement,0,0); }
      return acc.toDataURL('image/jpeg',0.95); }}; }
