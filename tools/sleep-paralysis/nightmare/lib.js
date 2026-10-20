// Shared helpers: seeded random, tapered tube builder, recursive branch growth, ink material patches.
import * as T from 'three';

export function rng(seed){let s=seed>>>0;return()=>{s=(s+0x6D2B79F5)>>>0;let t=s;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return((t^t>>>14)>>>0)/4294967296;};}
export const V=(x=0,y=0,z=0)=>new T.Vector3(x,y,z);
export const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
export const smooth=(a,b,x)=>{const t=clamp((x-a)/(b-a));return t*t*(3-2*t);};
export const lerp=(a,b,t)=>a+(b-a)*t;

// Accumulates tapered tubes into one BufferGeometry. Every vertex carries:
// aCenter (axis point), aArc (0 root .. 1 tip of its own branch), aGrow (birth, duration),
// aSway (distance-from-core weight for the drift field), aSeed.
export class TubeBuilder{
 constructor(sides=5){this.sides=sides;this.pos=[];this.cen=[];this.arc=[];this.grow=[];this.sway=[];this.seed=[];this.shade=[];this.idx=[];this.n=0;}
 tube(pts,radii,o={}){
  const S=o.sides||this.sides,N=pts.length;if(N<2)return;
  const birth=o.birth??-99,dur=o.dur??1,sw0=o.sway0??0,sw1=o.sway1??sw0,seed=o.seed??0,shade=o.shade??0;
  let tan=V(),nor=V(),bin=V(),prevT=null;
  const len=[0];for(let i=1;i<N;i++)len.push(len[i-1]+pts[i].distanceTo(pts[i-1]));const L=len[N-1]||1;
  const base=this.n;
  for(let i=0;i<N;i++){
   if(i===0)tan.subVectors(pts[1],pts[0]);else if(i===N-1)tan.subVectors(pts[N-1],pts[N-2]);else tan.subVectors(pts[i+1],pts[i-1]);
   tan.normalize();
   if(!prevT){const a=Math.abs(tan.y)<.9?V(0,1,0):V(1,0,0);nor.crossVectors(tan,a).normalize();}
   else{const ax=V().crossVectors(prevT,tan);const s=ax.length();if(s>1e-6){ax.normalize();nor.applyAxisAngle(ax,Math.asin(clamp(s,-1,1)));}}
   bin.crossVectors(tan,nor).normalize();prevT=tan.clone();
   const r=typeof radii==='function'?radii(len[i]/L,i):radii[i],a=len[i]/L,sw=lerp(sw0,sw1,a);
   for(let k=0;k<S;k++){const th=k/S*Math.PI*2+(o.twist||0)*a;const c=Math.cos(th),s=Math.sin(th);
    this.pos.push(pts[i].x+(nor.x*c+bin.x*s)*r,pts[i].y+(nor.y*c+bin.y*s)*r,pts[i].z+(nor.z*c+bin.z*s)*r);
    this.cen.push(pts[i].x,pts[i].y,pts[i].z);this.arc.push(a);this.grow.push(birth,dur);this.sway.push(sw);this.seed.push(seed);this.shade.push(shade);}
  }
  for(let i=0;i<N-1;i++)for(let k=0;k<S;k++){const a=base+i*S+k,b=base+i*S+(k+1)%S,c=a+S,d=b+S;this.idx.push(a,c,b,b,c,d);}
  this.n+=N*S;
 }
 geometry(){const g=new T.BufferGeometry();
  g.setAttribute('position',new T.Float32BufferAttribute(this.pos,3));g.setAttribute('aCenter',new T.Float32BufferAttribute(this.cen,3));
  g.setAttribute('aArc',new T.Float32BufferAttribute(this.arc,1));g.setAttribute('aGrow',new T.Float32BufferAttribute(this.grow,2));
  g.setAttribute('aSway',new T.Float32BufferAttribute(this.sway,1));g.setAttribute('aSeed',new T.Float32BufferAttribute(this.seed,1));
  g.setAttribute('aShade',new T.Float32BufferAttribute(this.shade,1));
  g.setIndex(this.n>65535?new T.Uint32BufferAttribute(this.idx,1):new T.Uint16BufferAttribute(this.idx,1));g.computeBoundingSphere();g.boundingSphere.radius*=1.5;return g;}
}

// Random-walk polyline: bends, curls and is pulled by a bias direction (gravity, outward, up).
export function walk(R,start,dir,len,o={}){
 const step=o.step||Math.max(.012,len/14),n=Math.max(3,Math.ceil(len/step));const pts=[start.clone()];const d=dir.clone().normalize(),p=start.clone();
 const bias=o.bias||V(),jag=o.jag??.35;
 for(let i=0;i<n;i++){d.x+=(R()-.5)*jag+bias.x*step*4;d.y+=(R()-.5)*jag+bias.y*step*4;d.z+=(R()-.5)*jag+bias.z*step*4;d.normalize();p.addScaledVector(d,len/n);pts.push(p.clone());}
 return pts;
}
const tmpQ=new T.Quaternion();
export function deviate(R,dir,minDeg,maxDeg){const d=dir.clone().normalize();const a=Math.abs(d.y)<.9?V(0,1,0):V(1,0,0);const ax=V().crossVectors(d,a).normalize();
 ax.applyAxisAngle(d,R()*Math.PI*2);tmpQ.setFromAxisAngle(ax,(minDeg+(maxDeg-minDeg)*R())*Math.PI/180);return d.applyQuaternion(tmpQ);}

// Recursive thorny branch. Children are born when the parent's growth front reaches them.
export function branch(B,R,start,dir,len,rad,depth,o={}){
 const pts=walk(R,start,dir,len,o);const birth=o.birth??-99,dur=o.dur??1,sw0=o.sway0??0;
 const swayLen=o.swayPerM??.6,sw1=sw0+len*swayLen;
 B.tube(pts,a=>Math.max(o.minR??.0012,rad*(1-a*.92)*(1+.25*Math.sin(a*19+start.x*40))),{birth,dur,sway0:sw0,sway1:sw1,seed:R(),sides:rad>.012?6:rad>.004?4:3,shade:o.shade});
 const out={pts,birth,dur};
 if(depth<=0)return out;
 const kids=o.kids??3;const nk=Math.round(kids*(.6+R()*.8));
 for(let k=0;k<nk;k++){const a=.18+R()*.78,i=Math.min(pts.length-2,Math.floor(a*(pts.length-1)));const at=pts[i],tan=V().subVectors(pts[i+1],pts[i]).normalize();
  const cd=deviate(R,tan,o.spreadMin??22,o.spreadMax??62);if(o.childBias)cd.addScaledVector(o.childBias,.5).normalize();
  branch(B,R,at,cd,len*(o.lenK??.55)*(.6+R()*.7),rad*(1-a*.9)*(o.radK??.62),depth-1,{...o,birth:birth+dur*a,dur:dur*(o.durK??.7),sway0:sw0+len*a*swayLen});}
 // thorns: tiny hard spurs that make the silhouette prickle
 const nt=o.thorns??(rad>.003?Math.round(len*5*R()):0);
 for(let k=0;k<nt;k++){const a=.1+R()*.85,i=Math.min(pts.length-2,Math.floor(a*(pts.length-1)));const tan=V().subVectors(pts[i+1],pts[i]).normalize();
  const cd=deviate(R,tan,35,80);const tl=.012+R()*.03;const r0=Math.max(.0011,rad*(1-a*.9)*.7);
  B.tube([pts[i].clone(),pts[i].clone().addScaledVector(cd,tl)],[r0,.0003],{birth:birth+dur*a,dur:.25,sway0:sw0+len*a*swayLen,sway1:sw0+len*a*swayLen,seed:R(),sides:3});}
 return out;
}

// GLSL: growth front + coherent drift. Shared by visible and shadow-depth materials.
const GLSL_HEAD=`
uniform float uTime; uniform float uSwayAmp; uniform float uGrowShift;
attribute vec3 aCenter; attribute float aArc; attribute vec2 aGrow; attribute float aSway; attribute float aSeed; attribute float aShade;
varying float vArc; varying float vSeed; varying float vShade; varying vec3 vWP;
vec3 driftField(vec3 p,float t){
 return vec3(sin(p.y*2.3+t*.71+p.z*1.1)+.5*sin(p.z*5.1-t*1.13+p.x*3.), sin(p.x*1.9+t*.53+1.7)+.5*sin(p.x*4.3+t*.97+p.y*2.7), sin(p.y*1.7+t*.61+3.1+p.x*.8)+.5*sin(p.y*4.7-t*.89+p.z*3.3));
}`;
const GLSL_VERT=`
 float gT=clamp((uTime+uGrowShift-aGrow.x)/max(aGrow.y,.001),0.,1.);
 float grown=gT>=.999?1.:clamp((gT-aArc)/.07,0.,1.);
 vec3 transformed=aCenter+(position-aCenter)*grown;
 transformed+=driftField(aCenter*1.3,uTime)*aSway*uSwayAmp;
 vArc=aArc; vSeed=aSeed; vShade=aShade;
`;
let patchId=0;
export function patchGrowth(mat,uniforms,extraFrag){
 mat.onBeforeCompile=sh=>{Object.assign(sh.uniforms,uniforms);
  sh.vertexShader=GLSL_HEAD+'\n'+sh.vertexShader.replace('#include <begin_vertex>',GLSL_VERT).replace('#include <worldpos_vertex>','#include <worldpos_vertex>\n vWP=(modelMatrix*vec4(transformed,1.)).xyz;');
  if(sh.vertexShader.indexOf('vWP=')<0)sh.vertexShader=sh.vertexShader.replace('#include <project_vertex>','#include <project_vertex>\n vWP=(modelMatrix*vec4(transformed,1.)).xyz;');
  sh.fragmentShader='uniform float uTime; uniform float uPulseGain;\nvarying float vArc; varying float vSeed; varying float vShade; varying vec3 vWP;\n'+sh.fragmentShader;
  if(extraFrag)sh.fragmentShader=sh.fragmentShader.replace('#include <dithering_fragment>','#include <dithering_fragment>\n'+extraFrag);
 };
 const key='grow'+(++patchId);mat.customProgramCacheKey=()=>key;
 return mat;
}
