// Atmosphere: a ray-marched moonlight shaft through the barred window, drifting ink flecks, crimson petals, lit dust.
import * as T from 'three';
import {rng,V} from './lib.js';
import {ROOM} from './room.js';

// Parallelepiped from the window opening along the light direction. Ray-marched in its unit space.
export class LightShaft{
 constructor(scene,lightDir){
  const W=ROOM.win,o=V(ROOM.x0,W.y0,W.z0),e1=lightDir.clone().normalize().multiplyScalar(6.5),e2=V(0,W.y1-W.y0,0),e3=V(0,0,W.z1-W.z0);
  const m=new T.Matrix4().makeBasis(e1,e2,e3).setPosition(o);
  const g=new T.BoxGeometry(1,1,1);g.translate(.5,.5,.5);
  this.u={uTime:{value:0},uInv:{value:m.clone().invert()},uGain:{value:1},uFogC:{value:new T.Color()}};
  const mat=new T.ShaderMaterial({uniforms:this.u,transparent:true,depthWrite:false,blending:T.AdditiveBlending,side:T.BackSide,
   vertexShader:`varying vec3 vW;void main(){vec4 w=modelMatrix*vec4(position,1.);vW=w.xyz;gl_Position=projectionMatrix*viewMatrix*w;}`,
   fragmentShader:`uniform float uTime,uGain;uniform mat4 uInv;varying vec3 vW;
    float h(vec3 p){return fract(sin(dot(p,vec3(127.1,311.7,74.7)))*43758.5453);}
    float n3(vec3 p){vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(mix(h(i),h(i+vec3(1,0,0)),f.x),mix(h(i+vec3(0,1,0)),h(i+vec3(1,1,0)),f.x),f.y),mix(mix(h(i+vec3(0,0,1)),h(i+vec3(1,0,1)),f.x),mix(h(i+vec3(0,1,1)),h(i+vec3(1,1,1)),f.x),f.y),f.z);}
    float bars(vec3 q){ // window sash bars and frame cut the shaft into panes
      float b=1.;b*=smoothstep(.0,.03,abs(q.z-.5)-.013);b*=smoothstep(.0,.03,abs(q.y-.36)-.008);b*=smoothstep(.0,.03,abs(q.y-.70)-.008);
      b*=smoothstep(.0,.05,q.z)*smoothstep(.0,.05,1.-q.z)*smoothstep(.0,.04,q.y)*smoothstep(.0,.06,1.-q.y);return b;}
    void main(){
     vec3 ro=cameraPosition, rd=normalize(vW-cameraPosition);
     vec3 lo=(uInv*vec4(ro,1.)).xyz, ld=(uInv*vec4(rd,0.)).xyz;
     vec3 t0=(vec3(0)-lo)/ld, t1=(vec3(1)-lo)/ld; vec3 tn=min(t0,t1), tf=max(t0,t1);
     float a=max(max(tn.x,tn.y),max(tn.z,0.)), b=min(min(tf.x,tf.y),tf.z); if(b<=a) discard;
     float acc=0.; const int N=28; float dt=(b-a)/float(N); float jit=h(vec3(gl_FragCoord.xy,1.));
     for(int i=0;i<N;i++){ float tt=a+dt*(float(i)+jit); vec3 q=lo+ld*tt; vec3 w=ro+rd*tt;
       float d=.55+.45*n3(w*2.1+vec3(uTime*.05,-uTime*.02,0.))*n3(w*5.3-vec3(0.,uTime*.04,uTime*.03));
       acc+=bars(q)*d*exp(-q.x*2.2)*(1.-q.x);}
     float L=acc/float(N)*(b-a);
     gl_FragColor=vec4(vec3(.85,.84,.8)*L*.3*uGain,1.);
    }`});
  this.mesh=new T.Mesh(g,mat);this.mesh.matrixAutoUpdate=false;this.mesh.matrix.copy(m);this.mesh.frustumCulled=false;this.mesh.renderOrder=5;scene.add(this.mesh);
  this.matrix=m;
 }
}

export class Particles{
 constructor(scene,shaft){
  const R=rng(2718);
  const mk=(n,kind)=>{const pos=new Float32Array(n*3),vel=new Float32Array(n*3),rnd=new Float32Array(n*2);
   for(let i=0;i<n;i++){pos[i*3]=ROOM.x0+R()*(ROOM.x1-ROOM.x0);pos[i*3+1]=R()*ROOM.h;pos[i*3+2]=ROOM.z0+R()*(ROOM.z1-ROOM.z0);
    vel[i*3]=(R()-.5)*.05;vel[i*3+1]=kind===1?-.02-R()*.03:(R()-.5)*.03;vel[i*3+2]=(R()-.5)*.05;rnd[i*2]=R();rnd[i*2+1]=R();}
   const g=new T.BufferGeometry();g.setAttribute('position',new T.BufferAttribute(pos,3));g.setAttribute('aVel',new T.BufferAttribute(vel,3));g.setAttribute('aRnd',new T.BufferAttribute(rnd,2));return g;};
  const common={uTime:{value:0},uScale:{value:1000},uFogC:{value:new T.Color(.2,.2,.2)},uFogD:{value:.1},uInv:{value:shaft.u.uInv.value},uGain:{value:1}};
  this.u=common;
  const vs=`uniform float uTime,uScale;attribute vec3 aVel;attribute vec2 aRnd;varying vec2 vR;varying float vD;varying vec3 vW;uniform float uSize;
   vec3 wrapRoom(vec3 p){vec3 lo=vec3(${ROOM.x0.toFixed(2)},0.,${ROOM.z0.toFixed(2)}),sz=vec3(${(ROOM.x1-ROOM.x0).toFixed(2)},${ROOM.h.toFixed(2)},${(ROOM.z1-ROOM.z0).toFixed(2)});return lo+mod(p-lo,sz);}
   void main(){vec3 p=position+aVel*uTime;p+=.08*vec3(sin(uTime*.31+aRnd.x*40.),sin(uTime*.23+aRnd.y*31.),cos(uTime*.27+aRnd.x*17.));p=wrapRoom(p);vW=p;
    vec4 mv=viewMatrix*vec4(p,1.);vD=-mv.z;gl_Position=projectionMatrix*mv;gl_PointSize=uSize*(.5+aRnd.y)*uScale/max(vD,.05);vR=aRnd;}`;
  // ink flecks: torn black specks
  this.ink=new T.Points(mk(1400,0),new T.ShaderMaterial({uniforms:{...common,uSize:{value:.006}},transparent:true,depthWrite:false,vertexShader:vs,
   fragmentShader:`uniform vec3 uFogC;uniform float uFogD,uTime;varying vec2 vR;varying float vD;
    void main(){vec2 c=gl_PointCoord-.5;float a=atan(c.y,c.x);float r=length(c)*(1.+.35*sin(a*3.+vR.x*20.)+.2*sin(a*7.+vR.y*9.));if(r>.42)discard;
     float f=1.-exp(-vD*vD*uFogD*uFogD);gl_FragColor=vec4(mix(vec3(.02),uFogC,f),.85*(1.-smoothstep(.3,.42,r))*(1.-f*.7)*smoothstep(.05,.3,vD));}`}));
  // crimson petals: rare, slow, tumbling diamonds
  this.red=new T.Points(mk(70,1),new T.ShaderMaterial({uniforms:{...common,uSize:{value:.022}},transparent:true,depthWrite:false,vertexShader:vs,
   fragmentShader:`uniform vec3 uFogC;uniform float uFogD,uTime,uGain;varying vec2 vR;varying float vD;
    void main(){vec2 c=gl_PointCoord-.5;float an=uTime*(.4+vR.x)+vR.y*6.28;mat2 m=mat2(cos(an),-sin(an),sin(an),cos(an));c=m*c;c.x*=1.+.8*abs(sin(uTime*.9+vR.x*9.));
     float d=abs(c.x)*1.7+abs(c.y);if(d>.45)discard;float f=1.-exp(-vD*vD*uFogD*uFogD);
     gl_FragColor=vec4(mix(vec3(.46,.03,.03)*(.8+.4*vR.y),uFogC,f*.8),.9*smoothstep(.12,.4,vD)*uGain);}`}));
  // pale dust that only shows inside the moonlight shaft
  this.dust=new T.Points(mk(2600,0),new T.ShaderMaterial({uniforms:{...common,uSize:{value:.0035}},transparent:true,depthWrite:false,blending:T.AdditiveBlending,vertexShader:vs,
   fragmentShader:`uniform mat4 uInv;varying vec2 vR;varying float vD;varying vec3 vW;
    void main(){vec3 q=(uInv*vec4(vW,1.)).xyz;float in_=step(0.,q.x)*step(q.x,1.)*step(0.,q.y)*step(q.y,1.)*step(0.,q.z)*step(q.z,1.);
     float r=length(gl_PointCoord-.5);if(r>.5||in_<.5)discard;gl_FragColor=vec4(vec3(.9,.88,.82)*(1.-r*2.)*.55*exp(-q.x*2.),1.);}`}));
  for(const p of [this.ink,this.red,this.dust]){p.frustumCulled=false;scene.add(p);}
 }
 update(t,H,fogC,fogD){for(const m of [this.ink.material,this.red.material,this.dust.material]){m.uniforms.uTime.value=t;m.uniforms.uScale.value=H*.9;m.uniforms.uFogC.value.copy(fogC);m.uniforms.uFogD.value=fogD;}}
}
