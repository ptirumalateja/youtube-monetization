// Final grade: ink outlines, monochrome graphite/ivory with crimson preserved, paper tooth, vignette, ink bleed.
import * as T from 'three';

export const GradeShader={
 uniforms:{tDiffuse:{value:null},uRes:{value:new T.Vector2(1080,1920)},uInk:{value:0},uVig:{value:1},uExpo:{value:1},uTime:{value:0},uPaper:{value:null}},
 vertexShader:`varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
 fragmentShader:`uniform sampler2D tDiffuse,uPaper;uniform vec2 uRes;uniform float uInk,uVig,uExpo,uTime;varying vec2 vUv;
  vec3 toS(vec3 c){c=max(c,0.);return mix(c*12.92,1.055*pow(c,vec3(1./2.4))-.055,step(.0031308,c));}
  float lum(vec3 c){return dot(c,vec3(.299,.587,.114));}
  float h2(vec2 p){return fract(sin(dot(p,vec2(12.9898,78.233)))*43758.5453);}
  float n2(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h2(i),h2(i+vec2(1,0)),f.x),mix(h2(i+vec2(0,1)),h2(i+vec2(1,1)),f.x),f.y);}
  float fbm(vec2 p){float s=0.,a=.5;for(int i=0;i<5;i++){s+=a*n2(p);p*=2.03;a*=.5;}return s;}
  void main(){
   vec2 px=1./uRes; vec3 c=toS(texture2D(tDiffuse,vUv).rgb*uExpo);
   // ink edges: luminance gradient becomes a dark drawn line
   float l=lum(c);
   float gx=lum(toS(texture2D(tDiffuse,vUv+vec2(px.x,0)).rgb))-lum(toS(texture2D(tDiffuse,vUv-vec2(px.x,0)).rgb));
   float gy=lum(toS(texture2D(tDiffuse,vUv+vec2(0,px.y)).rgb))-lum(toS(texture2D(tDiffuse,vUv-vec2(0,px.y)).rgb));
   float edge=clamp(length(vec2(gx,gy))*2.2-.04,0.,.55);
   float red=clamp((c.r-max(c.g,c.b))*3.2,0.,1.);
   l*=1.-edge;
   // tone: crushed blacks, long graphite mids, ivory tops
   float t=smoothstep(.015,.95,l); t=pow(t,1.08); t=t*t*(3.-2.*t)*.35+t*.65;
   vec3 mono=mix(vec3(.010,.010,.012),vec3(.93,.90,.84),t);
   mono=mix(mono,mono*vec3(.96,.98,1.02),1.-t);
   vec3 crim=vec3(c.r*1.05,c.g*.35,c.b*.35)*(1.-edge*.5);
   vec3 o=mix(mono,crim,red);
   // paper tooth (static, never flickers) and fibre
   float p=texture2D(uPaper,vUv*vec2(uRes.x/1024.,uRes.y/1024.)).r;
   o*=.9+.16*p; o+= (p-.5)*.025;
   // vignette: oppressive dark edges
   vec2 q=(vUv-.5)*vec2(1.15,.95); float v=smoothstep(.35,.95,length(q)*1.3); o*=mix(1.,.25,v*uVig);
   // ink bleed: black crawling in from the frame edges along fbm tendrils
   if(uInk>0.){float r=length((vUv-.5)*vec2(1.,1.6));float f=fbm(vUv*vec2(5.,9.)+vec2(0.,uTime*.05))*.55+fbm(vUv*vec2(19.,34.))*.2;
     float th=-.2+uInk*1.35; float m=smoothstep(th,th-.08,1.-r+f*.6-.3); o*=1.-m;}
   gl_FragColor=vec4(clamp(o,0.,1.),1.);
  }`
};

export function paperTexture(seed=99){const c=document.createElement('canvas');c.width=c.height=1024;const x=c.getContext('2d');const img=x.createImageData(1024,1024);
 let s=seed;const R=()=>{s=(s*1664525+1013904223)>>>0;return s/4294967296;};
 for(let i=0;i<img.data.length;i+=4){const v=128+(R()-.5)*90;img.data[i]=img.data[i+1]=img.data[i+2]=v;img.data[i+3]=255;}x.putImageData(img,0,0);
 x.globalAlpha=.08;for(let i=0;i<3000;i++){x.strokeStyle=R()<.5?'#000':'#fff';x.lineWidth=.6;x.beginPath();const a=R()*1024,b=R()*1024,an=R()*6.28,l=4+R()*22;x.moveTo(a,b);x.lineTo(a+Math.cos(an)*l,b+Math.sin(an)*l);x.stroke();}
 x.globalAlpha=1;x.filter='blur(.6px)';x.drawImage(c,0,0);
 const t=new T.CanvasTexture(c);t.wrapS=t.wrapT=T.RepeatWrapping;return t;}
