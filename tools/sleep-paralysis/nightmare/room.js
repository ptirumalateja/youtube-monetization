// The bedroom: real geometry at real depths, shaded by an engraving material (world-anchored hatching, grain).
import * as T from 'three';
import {rng,V,TubeBuilder,branch,patchGrowth,clamp,smooth} from './lib.js';

const ENGRAVE_HEAD=`
varying vec3 vWPh;
float hh3(vec3 p){return fract(sin(dot(p,vec3(127.1,311.7,74.7)))*43758.5453);}
float vn3(vec3 p){vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
 return mix(mix(mix(hh3(i),hh3(i+vec3(1,0,0)),f.x),mix(hh3(i+vec3(0,1,0)),hh3(i+vec3(1,1,0)),f.x),f.y),
            mix(mix(hh3(i+vec3(0,0,1)),hh3(i+vec3(1,0,1)),f.x),mix(hh3(i+vec3(0,1,1)),hh3(i+vec3(1,1,1)),f.x),f.y),f.z);}
float hline(float x,float w){float aa=fwidth(x);float d=.5-abs(fract(x)-.5);float l=1.-smoothstep(w-aa*.8,w+aa*.8,d);return mix(l,w*2.,clamp(aa*1.6-.6,0.,1.));}
uniform float uHatchFreq; uniform vec3 uHatchA; uniform vec3 uHatchB;
`;
const ENGRAVE_FRAG=`
{
 vec3 wp=vWPh; vec3 c=gl_FragColor.rgb;
 float L=dot(c,vec3(.299,.587,.114));
 float wob=vn3(wp*7.)*.55+vn3(wp*23.)*.18;
 float w1=clamp((.3-L)*.9,0.,.4), w2=clamp((.16-L)*1.5,0.,.4), w3=clamp((.07-L)*2.6,0.,.4);
 float h=hline(dot(wp,uHatchA)*uHatchFreq+wob,w1);
 h=max(h,hline(dot(wp,uHatchB)*uHatchFreq*1.13+wob*1.3,w2));
 h=max(h,hline(dot(wp,normalize(uHatchA+uHatchB))*uHatchFreq*1.6+wob,w3));
 float grain=.66+.3*vn3(wp*160.)+.28*vn3(wp*9.)*vn3(wp*31.)+.1*vn3(wp*2.3);
 float stip=step(.985-L*.02,hh3(floor(wp*420.)));
 c*=grain*(1.-.62*h);
 c=mix(c,c*.4,stip*.6);
 gl_FragColor.rgb=c;
}
`;
let engId=0;
export function engrave(mat,o={}){
 const u={uHatchFreq:{value:o.freq??62},uHatchA:{value:(o.a||V(1,1.7,.35)).normalize()},uHatchB:{value:(o.b||V(-1,.45,1.2)).normalize()}};
 mat.onBeforeCompile=sh=>{Object.assign(sh.uniforms,u);
  sh.vertexShader='varying vec3 vWPh;\n'+sh.vertexShader.replace('#include <project_vertex>','#include <project_vertex>\n vWPh=(modelMatrix*vec4(transformed,1.)).xyz;');
  sh.fragmentShader=ENGRAVE_HEAD+sh.fragmentShader.replace('#include <opaque_fragment>','#include <opaque_fragment>\n'+ENGRAVE_FRAG);};
 const key='eng'+(++engId);mat.customProgramCacheKey=()=>key;return mat;
}
const lam=(g,o)=>engrave(new T.MeshLambertMaterial({color:new T.Color(g,g,g),...(o||{})}),o?.eng||{});

function plankTexture(){const c=document.createElement('canvas');c.width=1024;c.height=1024;const x=c.getContext('2d'),R=rng(4401);
 x.fillStyle='#8a8a8a';x.fillRect(0,0,1024,1024);
 for(let i=0;i<8;i++){const y=i*128;x.fillStyle=`rgb(${120+R()*30|0},${120+R()*30|0},${120+R()*30|0})`;x.fillRect(0,y,1024,128);
  for(let k=0;k<60;k++){x.strokeStyle=`rgba(30,30,30,${.08+R()*.15})`;x.lineWidth=.7+R();x.beginPath();const yy=y+R()*128;x.moveTo(0,yy);for(let s=0;s<=1024;s+=64)x.lineTo(s,yy+Math.sin(s*.01+k)*3*R());x.stroke();}
  x.fillStyle='rgba(10,10,10,.9)';x.fillRect(0,y,1024,3);let off=R()*1024;x.fillRect(off,y,3,128);}
 const t=new T.CanvasTexture(c);t.wrapS=t.wrapT=T.RepeatWrapping;t.colorSpace=T.SRGBColorSpace;t.anisotropy=8;return t;}

function skyTexture(){const c=document.createElement('canvas');c.width=1024;c.height=1024;const x=c.getContext('2d'),R=rng(777);
 const g=x.createRadialGradient(597,520,40,597,520,800);g.addColorStop(0,'#d8d6d0');g.addColorStop(.35,'#9b9a97');g.addColorStop(1,'#3b3b3c');x.fillStyle=g;x.fillRect(0,0,1024,1024);
 // clouds: soft banks with lit rims
 for(let i=0;i<70;i++){const cx=R()*1024,cy=380+R()*500,rw=60+R()*200,rh=14+R()*30;const gg=x.createRadialGradient(cx,cy,2,cx,cy,rw);const v=R()<.5?200:60;gg.addColorStop(0,`rgba(${v},${v},${v},${.25+R()*.3})`);gg.addColorStop(1,'rgba(0,0,0,0)');x.fillStyle=gg;x.beginPath();x.ellipse(cx,cy,rw,rh,0,0,7);x.fill();}
 // the moon: engraved disc with maria
 const mx=597,my=520,mr=110;const mg=x.createRadialGradient(mx-20,my-20,10,mx,my,mr);mg.addColorStop(0,'#f6f2e6');mg.addColorStop(1,'#cfcabd');x.fillStyle=mg;x.beginPath();x.arc(mx,my,mr,0,7);x.fill();
 x.save();x.beginPath();x.arc(mx,my,mr,0,7);x.clip();for(let i=0;i<40;i++){x.fillStyle=`rgba(90,88,84,${.08+R()*.18})`;x.beginPath();x.arc(mx+(R()-.5)*1.6*mr,my+(R()-.5)*1.6*mr,8+R()*40,0,7);x.fill();}
 for(let i=0;i<600;i++){x.fillStyle=`rgba(60,60,60,${R()*.25})`;x.fillRect(mx-mr+R()*2*mr,my-mr+R()*2*mr,1.5,1.5);}x.restore();
 const halo=x.createRadialGradient(mx,my,mr,mx,my,mr*2.6);halo.addColorStop(0,'rgba(240,236,225,.45)');halo.addColorStop(1,'rgba(240,236,225,0)');x.fillStyle=halo;x.fillRect(0,0,1024,1024);
 const t=new T.CanvasTexture(c);t.colorSpace=T.SRGBColorSpace;return t;}

export const ROOM={x0:-3.4,x1:3.0,z0:-3.0,z1:4.6,h:3.4,win:{z0:-2.75,z1:-1.65,y0:1.05,y1:3.05},door:{x0:1.25,x1:2.15,h:2.2},bed:{x0:-3.3,x1:-1.0,z0:-1.5,z1:-.1,top:.62}};

export class Room{
 constructor(scene,uniforms){
  this.scene=scene;this.group=new T.Group();scene.add(this.group);this.u=uniforms;const R=rng(5150),r=ROOM;
  const wall=lam(.78),wallDark=lam(.62),wood=lam(.22,{eng:{freq:80}}),cloth=lam(.82,{eng:{freq:90}});
  const floor=engrave(new T.MeshLambertMaterial({map:plankTexture(),color:new T.Color(.55,.55,.55)}),{freq:70,a:V(1,0,.2),b:V(.3,0,1)});
  this.mats={wall,wood,cloth};
  const box=(w,h,d,x,y,z,m,cast=true,recv=true)=>{const b=new T.Mesh(new T.BoxGeometry(w,h,d),m);b.position.set(x,y,z);b.castShadow=cast;b.receiveShadow=recv;this.group.add(b);return b;};
  this.box=box;
  // floor and ceiling
  const fl=new T.Mesh(new T.PlaneGeometry(r.x1-r.x0,r.z1-r.z0),floor);fl.rotation.x=-Math.PI/2;fl.position.set((r.x0+r.x1)/2,0,(r.z0+r.z1)/2);fl.receiveShadow=true;this.group.add(fl);
  floor.map.repeat.set(3.2,4);
  box(r.x1-r.x0+.4,.12,r.z1-r.z0+.4,(r.x0+r.x1)/2,r.h+.06,(r.z0+r.z1)/2,wallDark);
  // left wall with the tall window opening
  const W=r.win,lx=r.x0-.06;
  box(.12,r.h,W.z0-r.z0,lx,r.h/2,(r.z0+W.z0)/2,wall);box(.12,r.h,r.z1-W.z1,lx,r.h/2,(W.z1+r.z1)/2,wall);
  box(.12,W.y0,W.z1-W.z0,lx,W.y0/2,(W.z0+W.z1)/2,wall);box(.12,r.h-W.y1,W.z1-W.z0,lx,(W.y1+r.h)/2,(W.z0+W.z1)/2,wall);
  // window frame, sash bars and sill (they cast the barred light patch)
  const wz=(W.z0+W.z1)/2,wy=(W.y0+W.y1)/2,ww=W.z1-W.z0,wh=W.y1-W.y0;
  for(const z of [W.z0+.03,W.z1-.03])box(.16,wh,.06,lx,wy,z,wood);box(.16,.07,ww,lx,W.y1-.03,wz,wood);box(.3,.06,ww+.2,lx+.08,W.y0,wz,wood);
  box(.06,wh,.035,lx,wy,wz,wood);for(const y of [W.y0+wh*.36,W.y0+wh*.7])box(.06,.035,ww,lx,y,wz,wood);
  // arched top of the window: two small bars fan out
  for(const a of [-.5,.5]){const b=box(.05,.5,.03,lx,W.y1-.32,wz+a*.35,wood);b.rotation.x=a*.9;}
  // back wall with the door opening
  const D=r.door,bz=r.z0-.06;
  box(D.x0-r.x0,r.h,.12,(r.x0+D.x0)/2,r.h/2,bz,wall);box(r.x1-D.x1,r.h,.12,(D.x1+r.x1)/2,r.h/2,bz,wall);box(D.x1-D.x0,r.h-D.h,.12,(D.x0+D.x1)/2,(D.h+r.h)/2,bz,wall);
  for(const x of [D.x0-.04,D.x1+.04])box(.08,D.h+.04,.16,x,D.h/2,bz+.02,wood);box(D.x1-D.x0+.16,.08,.16,(D.x0+D.x1)/2,D.h+.04,bz+.02,wood);
  // the door stands ajar into the room, hinged on its right edge
  const door=new T.Group();door.position.set(D.x1,0,bz+.05);this.group.add(door);const slab=new T.Mesh(new T.BoxGeometry(D.x1-D.x0,D.h-.02,.05),lam(.4,{eng:{freq:70}}));slab.position.set(-(D.x1-D.x0)/2,D.h/2,0);slab.castShadow=slab.receiveShadow=true;door.add(slab);door.rotation.y=-1.05;this.door=door;
  for(const yy of [.55,1.55]){const p=new T.Mesh(new T.BoxGeometry(.6,.7,.02),lam(.32));p.position.set(-(D.x1-D.x0)/2,yy,.035);door.add(p);}
  // the corridor beyond: pale, empty, overexposed
  const hall=new T.MeshBasicMaterial({color:new T.Color(.82,.81,.78),fog:false});
  const hb=new T.Mesh(new T.PlaneGeometry(3,3),hall);hb.position.set((D.x0+D.x1)/2,1.3,r.z0-2.6);this.group.add(hb);
  const hs=lam(.7);box(.1,3,2.6,D.x0-.1,1.5,r.z0-1.35,hs,false);box(.1,3,2.6,D.x1+.4,1.5,r.z0-1.35,hs,false);box(1.6,.1,2.6,(D.x0+D.x1)/2,0,r.z0-1.35,lam(.5),false);
  // right and front walls
  box(.12,r.h,r.z1-r.z0,r.x1+.06,r.h/2,(r.z0+r.z1)/2,wall);box(r.x1-r.x0,r.h,.12,(r.x0+r.x1)/2,r.h/2,r.z1+.06,wall);
  // mouldings: picture rail, crown and skirting lines that sell perspective
  for(const y of [.1,2.45,r.h-.08]){box(r.x1-r.x0,.05,.04,(r.x0+r.x1)/2,y,r.z0+.02,wood,false);box(.04,.05,r.z1-r.z0,r.x0+.02,y,(r.z0+r.z1)/2,wood,false);box(.04,.05,r.z1-r.z0,r.x1-.02,y,(r.z0+r.z1)/2,wood,false);}
  // framed picture on the back wall (an old dark etching), plus a smaller one
  this.picture(-.05,1.75,.62,.82);this.picture(.85,1.95,.34,.44);
  this.bed();this.furniture();this.curtains();this.outside();
 }
 picture(x,y,w,h){const c=document.createElement('canvas');c.width=128;c.height=160;const g=c.getContext('2d'),R=rng(x*1000|0);g.fillStyle='#6c6a66';g.fillRect(0,0,128,160);
  for(let i=0;i<300;i++){g.strokeStyle=`rgba(20,20,20,${R()*.4})`;g.beginPath();const a=R()*128,b=R()*160;g.moveTo(a,b);g.lineTo(a+(R()-.5)*30,b+R()*30);g.stroke();}
  g.fillStyle='rgba(15,15,15,.75)';g.beginPath();g.ellipse(64,70,18,26,0,0,7);g.fill();g.fillRect(48,90,32,60);
  const t=new T.CanvasTexture(c);t.colorSpace=T.SRGBColorSpace;
  this.box(w+.08,h+.08,.05,x,y,ROOM.z0+.03,this.mats.wood);const p=new T.Mesh(new T.PlaneGeometry(w,h),engrave(new T.MeshLambertMaterial({map:t}),{}));p.position.set(x,y,ROOM.z0+.06);p.receiveShadow=true;this.group.add(p);}
 bed(){const b=ROOM.bed,wood=this.mats.wood,box=this.box,cz=(b.z0+b.z1)/2,wd=b.z1-b.z0;
  // headboard with posts, footboard, frame
  box(.08,1.15,wd+.1,b.x0,.58,cz,wood);for(const z of [b.z0-.05,b.z1+.05]){box(.09,1.3,.09,b.x0,.65,z,wood);box(.08,.85,.08,b.x1,.43,z,wood);const f=new T.Mesh(new T.SphereGeometry(.055,10,8),wood);f.position.set(b.x0,1.33,z);f.castShadow=true;this.group.add(f);}
  box(.07,.55,wd+.1,b.x1,.4,cz,wood);box(b.x1-b.x0,.18,.06,(b.x0+b.x1)/2,.3,b.z0-.03,wood);box(b.x1-b.x0,.18,.06,(b.x0+b.x1)/2,.3,b.z1+.03,wood);
  for(let i=0;i<5;i++)box(.035,.3,.035,b.x0+.08,.86+.0,b.z0+.12+i*(wd-.24)/4,wood);
  box(b.x1-b.x0-.08,.2,wd,(b.x0+b.x1)/2,.5,cz,this.mats.cloth);
  // pillow
  const pg=new T.SphereGeometry(1,28,16);pg.scale(.27,.085,.42);const pp=pg.attributes.position;for(let i=0;i<pp.count;i++){const x=pp.getX(i),z=pp.getZ(i);pp.setY(i,pp.getY(i)*(1-.35*Math.exp(-((x+.02)**2/.008+z*z/.02))));}pg.computeVertexNormals();
  const pil=new T.Mesh(pg,this.mats.cloth);pil.position.set(b.x0+.32,b.top+.06,cz);pil.castShadow=pil.receiveShadow=true;this.group.add(pil);
  // blanket: faceted, angular folds over a real body (shoulders, chest, pelvis, two legs, feet)
  const NX=46,NZ=26,x0=b.x0+.5,x1=b.x1+.06,z0=b.z0-.1,z1=b.z1+.1;const g=new T.PlaneGeometry(1,1,NX,NZ);g.rotateX(-Math.PI/2);
  const R=rng(31337),P=g.attributes.position;this.blanketBase=[];
  const ridge=[];for(let i=0;i<14;i++)ridge.push({a:R()*Math.PI,o:R()*2-1,s:.004+R()*.009,f:5+R()*7});
  for(let i=0;i<P.count;i++){const u=P.getX(i)+.5,v=P.getZ(i)+.5;const x=x0+(x1-x0)*u,z=z0+(z1-z0)*v;
   let y=b.top+.03;const zc=z-cz;
   const body=Math.exp(-((x-(b.x0+.95))**2/.09+zc*zc/.07))*.16+Math.exp(-((x-(b.x0+1.4))**2/.06+zc*zc/.05))*.1
    +Math.exp(-((zc-.11)**2)/.006)*smooth(b.x0+1.3,b.x0+1.6,x)*(1-smooth(b.x1-.15,b.x1,x))*.07+Math.exp(-((zc+.11)**2)/.006)*smooth(b.x0+1.3,b.x0+1.6,x)*(1-smooth(b.x1-.15,b.x1,x))*.07
    +Math.exp(-((x-(b.x1-.17))**2/.004+(Math.abs(zc)-.1)**2/.004))*.06;
   y+=body*smooth(b.x0+.48,b.x0+.62,x);
   const over=Math.max(0,Math.abs(zc)-wd/2);y-=over*3.2;y=Math.max(y,.26);
   if(x>b.x1)y-=(x-b.x1)*3;
   for(const q of ridge){const d=Math.cos(q.a)*(x-x0)+Math.sin(q.a)*(z-z0)+q.o;y+=q.s*Math.max(0,Math.sin(d*q.f));}
   y+=(R()-.5)*.012;
   P.setXYZ(i,x+(R()-.5)*.012,y,z+(R()-.5)*.012);this.blanketBase.push(x,y,z);}
  const ng=g.toNonIndexed();this.blanketGeo=ng;this.blanketSrc=Float32Array.from(ng.attributes.position.array);ng.computeVertexNormals();
  const bl=new T.Mesh(ng,lam(.56,{flatShading:true,side:T.DoubleSide,eng:{freq:115}}));bl.castShadow=bl.receiveShadow=true;this.group.add(bl);this.blanket=bl;
 }
 // chest heaves in shallow panic; a covered arm tries to lift and fails
 animateBlanket(t,attempt){const P=this.blanketGeo.attributes.position,S=this.blanketSrc,b=ROOM.bed,cz=(b.z0+b.z1)/2;
  const br=.012*Math.sin(t*5.2)*(.6+.4*Math.sin(t*.7))+.004*Math.sin(t*11.3);
  for(let i=0;i<P.count;i++){const x=S[i*3],y=S[i*3+1],z=S[i*3+2];const chest=Math.exp(-((x-(b.x0+.95))**2/.05+(z-cz)**2/.05));const arm=Math.exp(-((x-(b.x0+1.15))**2/.03+(z-(b.z1-.18))**2/.008));
   P.setY(i,y+chest*br+arm*attempt*.05);}
  P.needsUpdate=true;this.blanketGeo.computeVertexNormals();}
 furniture(){const wood=this.mats.wood,box=this.box,b=ROOM.bed;
  // nightstand + lamp between bed and window side
  box(.45,.6,.42,b.x0+.25,.3,b.z1+.36,wood);box(.5,.04,.46,b.x0+.25,.61,b.z1+.36,wood);
  for(let i=0;i<3;i++)box(.18,.03,.24,b.x0+.18,.65+i*.032,b.z1+.3,this.mats.cloth);
  const base=new T.Mesh(new T.CylinderGeometry(.03,.07,.38,14),wood);base.position.set(b.x0+.3,.82,b.z1+.42);base.castShadow=true;this.group.add(base);
  const shade=new T.Mesh(new T.CylinderGeometry(.11,.19,.24,20,1,true),lam(.3,{side:T.DoubleSide}));shade.position.set(b.x0+.3,1.1,b.z1+.42);shade.castShadow=true;this.group.add(shade);
  // dresser and chair on the right for foreground parallax
  box(.5,1.0,1.2,ROOM.x1-.3,.5,-1.6,wood);box(.52,.04,1.24,ROOM.x1-.3,1.02,-1.6,wood);for(let i=0;i<3;i++)box(.02,.22,1.0,ROOM.x1-.56,.2+i*.3,-1.6,lam(.3));
  const ch=new T.Group();ch.position.set(1.4,0,1.2);ch.rotation.y=.7;this.group.add(ch);
  const cb=(w,h,d,x,y,z)=>{const m=new T.Mesh(new T.BoxGeometry(w,h,d),wood);m.position.set(x,y,z);m.castShadow=true;ch.add(m);};
  cb(.45,.05,.45,0,.46,0);for(const [x,z] of [[-.2,-.2],[.2,-.2],[-.2,.2],[.2,.2]])cb(.04,.46,.04,x,.23,z);cb(.04,.6,.04,-.2,.78,-.2);cb(.04,.6,.04,.2,.78,-.2);cb(.44,.08,.03,0,1.05,-.2);cb(.44,.05,.03,0,.82,-.2);
  // clothes draped on the chair: a dark slumped shape (reads as another figure at a glance)
  const dr=new T.Mesh(new T.SphereGeometry(.22,10,8),lam(.2,{flatShading:true}));dr.scale.set(1,1.4,.5);dr.position.set(0,.85,-.16);dr.castShadow=true;ch.add(dr);
 }
 curtains(){const W=ROOM.win,m=new T.MeshLambertMaterial({color:new T.Color(.9,.9,.88),transparent:true,opacity:.42,side:T.DoubleSide,depthWrite:false});engrave(m,{freq:110,a:V(0,1,.05),b:V(0,1,-.05)});
  this.curtainMeshes=[];for(const s of [0,1]){const g=new T.PlaneGeometry(.55,2.6,18,30);g.rotateY(Math.PI/2);const c=new T.Mesh(g,m);c.position.set(ROOM.x0+.09,W.y1-1.2,s?W.z1+.12:W.z0-.12);c.renderOrder=3;this.group.add(c);c.userData.src=Float32Array.from(g.attributes.position.array);c.userData.s=s;this.curtainMeshes.push(c);}}
 animateCurtains(t){for(const c of this.curtainMeshes){const P=c.geometry.attributes.position,S=c.userData.src;for(let i=0;i<P.count;i++){const z=S[i*3+2],y=S[i*3+1];const hang=(1.3-y)/2.6;
   P.setX(i,S[i*3]+.04*Math.sin(z*28)+hang*hang*.06*(Math.sin(t*.8+z*4+c.userData.s*2)+.5*Math.sin(t*1.7+y*3)));}P.needsUpdate=true;}}
 outside(){
  const sky=new T.Mesh(new T.PlaneGeometry(60,60),new T.MeshBasicMaterial({map:skyTexture(),fog:false}));sky.position.set(-14,12,-16);sky.rotation.y=Math.PI/2;this.group.add(sky);this.sky=sky;
  // a dead tree outside: its branches are part of the shadow the moon throws into the room
  const B=new TubeBuilder(),R=rng(812);
  const trunk=[V(-5.0,-1,-3.4),V(-4.9,1,-3.2),V(-5.0,2.4,-2.9),V(-4.8,3.8,-2.7)];B.tube(trunk,a=>.22*(1-a*.5),{sides:8});
  for(let k=0;k<11;k++){const p=V(-4.95,1.4+k*.27,-3.0);branch(B,R,p,V(.6+R()*.5,.6+R()*.9,(R()-.3)*2.2).normalize(),1.6+R()*1.6,.05,4,{bias:V(0,.05,0),sway0:.0,swayPerM:.25,kids:3,lenK:.58,radK:.6});}
  for(let k=0;k<6;k++){const p=V(-9+R()*2,0,-9+R()*8);branch(B,R,p,V(.1,1,.1).normalize(),4+R()*2,.12,4,{bias:V(0,.04,0),swayPerM:.15,kids:3,lenK:.55,radK:.6});}
  const tm=patchGrowth(new T.MeshBasicMaterial({color:new T.Color(.05,.05,.055),fog:true}),this.u,'');const dm=patchGrowth(new T.MeshDepthMaterial({depthPacking:T.RGBADepthPacking}),this.u);
  const tree=new T.Mesh(B.geometry(),tm);tree.castShadow=true;tree.customDepthMaterial=dm;tree.frustumCulled=false;this.group.add(tree);
 }
}
