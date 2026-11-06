
const clamp=(x,a,b)=>Math.min(b,Math.max(a,x)); const lerp=(a,b,t)=>a+(b-a)*t; const sstep=(a,b,x)=>{const t=clamp((x-a)/(b-a),0,1);return t*t*(3-2*t)};
const ease=t=>t<0.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;
const LY=9.4607e15, GLY=LY*1e9;
const Lof=n=>1e-4*Math.pow(2,n); // column length in metres after n folds of a 0.1 mm sheet
const NOISE=`float h3(vec3 p){return fract(sin(dot(p,vec3(127.1,311.7,74.7)))*43758.5453);}
 float n3(vec3 p){vec3 i=floor(p),f=fract(p); f=f*f*(3.-2.*f); return mix(mix(mix(h3(i),h3(i+vec3(1,0,0)),f.x),mix(h3(i+vec3(0,1,0)),h3(i+vec3(1,1,0)),f.x),f.y),mix(mix(h3(i+vec3(0,0,1)),h3(i+vec3(1,0,1)),f.x),mix(h3(i+vec3(0,1,1)),h3(i+vec3(1,1,1)),f.x),f.y),f.z);}
 float fbm3(vec3 p){float a=0.5,s=0.;for(int i=0;i<5;i++){s+=a*n3(p);p*=2.03;a*=0.5;}return s;}`;
function project(cam,v){const p=v.clone().project(cam); return {x:(p.x*0.5+0.5)*W,y:(1-(p.y*0.5+0.5))*H,vis:p.z<1&&p.z>-1};}
const SC={};

