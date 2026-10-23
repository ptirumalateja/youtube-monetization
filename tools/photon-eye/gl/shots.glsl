#version 300 es
precision highp float;
uniform vec2 R;
uniform float uT,uZ,uPX,uPY,uA,uR;   // local time, zoom, photon screen pos, shot param, roll
out vec4 o;
#define SHOT SHOT_ID

float h31(vec3 p){p=fract(p*.1031);p+=dot(p,p.zyx+31.32);return fract((p.x+p.y)*p.z);}
float n3(vec3 x){vec3 i=floor(x),f=fract(x);f=f*f*(3.-2.*f);
 return mix(mix(mix(h31(i),h31(i+vec3(1,0,0)),f.x),mix(h31(i+vec3(0,1,0)),h31(i+vec3(1,1,0)),f.x),f.y),
            mix(mix(h31(i+vec3(0,0,1)),h31(i+vec3(1,0,1)),f.x),mix(h31(i+vec3(0,1,1)),h31(i+vec3(1,1,1)),f.x),f.y),f.z);}
const mat3 M=mat3(.00,.80,.60,-.80,.36,-.48,-.60,-.48,.64);
float fbm(vec3 p,int oc){float a=.5,s=0.;for(int i=0;i<8;i++){if(i>=oc)break;s+=a*n3(p);p=M*p*2.03;a*=.5;}return s;}
float smoke(vec3 p,int oc){
 vec3 q=vec3(fbm(p,4),fbm(p+vec3(5.2,1.3,2.8),4),fbm(p+vec3(1.1,7.4,3.3),4));
 return fbm(p+2.6*q,oc);
}
vec3 aces(vec3 x){return clamp((x*(2.51*x+.03))/(x*(2.43*x+.59)+.14),0.,1.);}
vec3 gold(float t){ // dark ember -> amber -> gold -> cream
 t=clamp(t,0.,1.);
 vec3 a=vec3(.05,.012,.0),b=vec3(.60,.20,.02),c=vec3(1.25,.66,.14),d=vec3(1.8,1.35,.75);
 return t<.4?mix(a,b,t/.4):t<.75?mix(b,c,(t-.4)/.35):mix(c,d,(t-.75)/.25);
}

// ---------------------------------------------------------------- 1: inside the Sun (tunnel of lit plasma)
vec2 rot2(vec2 v,float a){return mat2(cos(a),-sin(a),sin(a),cos(a))*v;}
vec3 trap(vec2 uv){
 vec3 col=vec3(0);float T=1.;
 float zz=uZ>0.?uZ:1.;
 uv=rot2(uv,uR)/zz;
 vec2 ph=rot2(vec2(uPX,uPY),uR)/zz;
 vec3 L=vec3(ph*1.25,1.25);            // the photon (lights the fog wherever it is)
 const int N=60;
 float jit=h31(vec3(gl_FragCoord.xy,7.));
 for(int i=0;i<N;i++){
  float fi=(float(i)+jit)/float(N);
  float z=.30+fi*2.4;
  float dz=2.4/float(N);
  vec2 w=uv*z;
  float r=length(w*vec2(1.,.62));
  float a=.35*z+.07/(r+.1)+uT*.05;
  w=mat2(cos(a),-sin(a),sin(a),cos(a))*w;
  float s=smoke(vec3(w*2.0,z*2.4-uT*.32),8);
  float wall=smoothstep(.42,.95,r+.45*(s-.5));
  float d=smoothstep(.48,.66,s)*wall;
  d+=.35*smoothstep(.60,.72,s)*(1.-wall);   // thin veils drifting in the hollow
  vec3 P=vec3(uv*z,z);
  float dl=length(P-L);
  float lit=1./(1.+dl*dl*4.)+.03;
  float edge=1.-smoothstep(.0,.12,abs(s-.56));    // fog fronts catch the light
  vec3 c=gold(.22+lit*1.2+edge*.5*lit)*(lit*(1.+2.6*edge)*2.3+.012);
  float k=d*dz*5.;
  col+=T*c*k;
  T*=exp(-k*2.6);
  col+=T*vec3(1.,.58,.18)*.010*dz/(.006+dl*dl);
 }
 return col;
}

// ---------------------------------------------------------------- 2: the escape (Sun limb, corona smoke, shockwave)
vec3 escape(vec2 uv){
 vec2 C=vec2(0.,-2.05);float Rs=1.55;
 float d=length(uv-C)-Rs;              // >0 above the surface
 vec2 sp=vec2(.10,C.y+Rs+.005);        // where the photon breaks out (just right of centre)
 vec3 col=vec3(0);
 vec2 g=floor(uv*200.);float st=h31(vec3(g,1.));col+=step(.997,st)*vec3(.8,.85,1.)*h31(vec3(g,2.))*1.4*smoothstep(.1,.4,d);
 vec2 q=uv-C;float an=atan(q.y,q.x);
 // photosphere: billowing plasma with dark lanes, limb darkened
 if(d<0.){
  float s=smoke(vec3(q*6.5,uT*.22),8);
  float gr=1.-abs(fbm(vec3(q*30.,1.),4)*2.-1.);
  float t=smoothstep(.30,.80,s)*.65+.35*gr;
  float limb=smoothstep(0.,.30,-d);
  col=gold(.15+t*.72*(.6+.4*limb))*(.3+.95*limb)*(.45+.8*t);
  float near=exp(-length((uv-sp)*vec2(1.,2.2))*4.);
  col+=near*vec3(1.6,1.0,.45)*(.5+t)*1.3;
 }
 // corona: smoky wisps streaming off the limb
 if(d>0.){
  float s=smoke(vec3(an*5.,d*4.-uT*.7,.7+uT*.1),7);
  float wisps=smoothstep(.40,.80,s)*exp(-d*4.5)*1.3+exp(-d*16.)*.8;
  col+=wisps*gold(.45+.45*s)*1.15;
  col+=exp(-d*2.5)*vec3(.30,.09,.02);
 }
 // shockwave: a soft dome of light (no hard shell) + a jet of plasma torn up behind the photon
 vec2 sv=(uv-sp)*vec2(1.,1.25);
 float rr=length(sv);
 float sm=smoke(vec3(sv*5.,3.1+uT*.3),8);
 float above=smoothstep(-.03,.04,d);
 float x=rr-(.12+.48*smoothstep(0.,1.3,uT));
 float fres=.15+1.2*pow(abs(sv.x)/max(rr,1e-3),5.);
 col+=above*exp(-abs(x)*9.)*fres*(.35+.5*sm)*vec3(1.3,.65,.2);
 col+=above*exp(-rr*3.2)*.55*vec3(1.2,.6,.18);
 vec2 jp=uv-sp;float hgt=max(jp.y,0.);
 float wid=.035+hgt*.22;
 float js=smoke(vec3(jp.x*7.,jp.y*3.5-uT*1.6,5.),8);
 float reach=.12+.75*uT;
 float jet=exp(-pow(jp.x/wid,2.))*smoothstep(.0,.02,jp.y)*exp(-hgt*2.2)*smoothstep(.35,.7,js)*smoothstep(reach,reach-.2,hgt);
 col+=above*jet*gold(.5+.5*exp(-hgt*4.))*(1.+4.*exp(-hgt*6.));
 // rim light racing along the limb from the break-out
 float spread=.10+.95*smoothstep(0.,1.6,uT);float ax=abs(uv.x-sp.x);
 float along=exp(-pow(ax/spread,2.))+exp(-pow((ax-spread)/.05,2.))*1.4;
 col+=exp(-abs(d)/.007)*along*vec3(3.,2.,1.1)*1.2+exp(-abs(d)/.05)*along*vec3(1.2,.5,.12)*.8;
 // the burst at the surface
 col+=exp(-length((uv-sp)*vec2(.7,1.6))*9.)*vec3(4.,3.,2.)*(.45+1.8*exp(-uT*2.5));
 return col;
}

// ---------------------------------------------------------------- 3: the eye (macro iris, Earth in the pupil)
vec3 earth(vec2 p,float r){
 float d=length(p);if(d>r)return vec3(-1);
 vec3 n=vec3(p/r,sqrt(max(0.,1.-dot(p,p)/(r*r))));
 vec2 q=n.xy/(n.z+.6)*1.6+vec2(.3+uT*.06,.1);
 float land=smoothstep(.52,.56,fbm(vec3(q*2.2,3.),6));
 float cl=smoothstep(.55,.75,smoke(vec3(q*3.,9.),5));
 vec3 c=mix(vec3(.02,.10,.32),vec3(.20,.32,.12),land);c=mix(c,vec3(.95),cl*.85);
 float lit=clamp(dot(n,normalize(vec3(-.6,.5,.65))),0.,1.);
 c*=.08+1.2*lit;
 c+=pow(1.-n.z,3.)*vec3(.3,.55,1.)*.9;
 return c;
}
vec3 eye(vec2 uv){
 vec2 c=vec2(0.,.0);
 float zz=uZ>0.?uZ:1.;
 vec2 p=(uv-c)*.80/zz;float r=length(p)/.80;float a=atan(p.y,p.x);
 // lids crop the iris top and bottom: macro framing
 float u=p.x/1.25;
 float top=.80*pow(max(0.,1.-u*u),.75)-.02, bot=-.70*pow(max(0.,1.-u*u),1.0)+.02;
 float open=smoothstep(-.01,.01,top-p.y)*smoothstep(-.01,.01,p.y-bot);
 vec2 Ld=normalize(vec2(-.45,1.));
 float lightside=.5+.5*dot(normalize(p+1e-4),Ld);
 // iris: fine radial fibres woven with a coarser layer, gold flecks near the pupil, deep blue-grey outer ring
 float fib=fbm(vec3(a*60.,r*4.+sin(uT*2.3)*.03,1.+uT*.06),6);
 float fib2=fbm(vec3(a*14.,r*2.,5.),5);
 float wav=fbm(vec3(a*24.+fib2*3.,r*9.,9.),5);
 float t=smoothstep(.38,.80,fib*.6+wav*.5);t=.10+.9*t*t*(.6+.6*fib2);
 vec3 inner=mix(vec3(.16,.06,.01),vec3(1.35,.80,.25),t);
 vec3 outer=mix(vec3(.04,.025,.015),vec3(.70,.40,.12),t);
 vec3 ir=mix(inner,outer,smoothstep(.45,.85,r));
 ir+=exp(-pow((r-.43)/.04,2.))*vec3(.5,.28,.08)*(.4+fib);           // collarette
 ir*=mix(1.,.04,smoothstep(.82,1.,r));                                // limbal ring
 ir*=.30+1.1*smoothstep(1.,.3,r);
 ir*=.35+1.25*lightside;
 float pr=uA>0.?uA:.25;
 ir*=smoothstep(pr,pr+.10,r)*.6+.4;                                    // shadowed pupil margin
 vec3 sc=vec3(.70,.62,.58)*(.18+.6*smoothstep(1.7,.95,r))*(.35+.7*lightside);
 vec3 col=mix(sc,ir,smoothstep(1.015,.985,r));
 col=mix(col,vec3(.003,.002,.004),smoothstep(pr+.006,pr-.006,r));
 // Earth reflected in the pupil (cornea as a curved mirror: small, soft, bright)
 vec3 e=earth(p-vec2(.035,.03),.085);
 if(e.x>=0.)col=mix(col,e*.95,.85*(1.-smoothstep(1.4,2.6,zz)));
 // cornea: big soft window reflection + sharp sun catchlight
 col+=exp(-pow(length((p-vec2(-.28,.30))*vec2(1.,1.6))/.16,2.))*.16*vec3(1.,.88,.7)*smoothstep(1.1,.9,r);
 col+=exp(-pow(length(p-vec2(-.27,.29))/.012,2.))*3.5*vec3(1.,.95,.85);
 float shade=smoothstep(0.,.25,top-p.y)*(.55+.45*smoothstep(0.,.15,p.y-bot));
 vec3 skin=vec3(.07,.03,.017)*(.5+.7*fbm(vec3(uv*5.,7.),5))*(.3+.9*max(0.,lightside));
 col=mix(skin,col*shade,open);
 // wet lid-margin highlight
 col+=exp(-pow((top-p.y)/.012,2.))*open*.0+exp(-pow((p.y-bot)/.01,2.))*.22*vec3(1.,.75,.5)*smoothstep(1.2,0.,abs(u));
 return col;
}

// ---------------------------------------------------------------- 4: the sunset sky
vec3 sky(vec2 uv){
 float hz=-.42;
 vec2 S=vec2(.34,hz+.05-uT*.012);
 float h=uv.y-hz;
 float d=length((uv-S)*vec2(1.,1.15));
 vec3 col=mix(vec3(1.7,.70,.20),vec3(.95,.30,.12),smoothstep(0.,.35,h));
 col=mix(col,vec3(.30,.08,.12),smoothstep(.25,.85,h));
 col=mix(col,vec3(.05,.02,.07),smoothstep(.8,1.5,h));
 col=mix(col,vec3(.008,.008,.02),smoothstep(1.4,2.,h));
 // layered clouds, undersides lit by the low sun
 for(int i=0;i<2;i++){
  float fi=float(i);
  float y0=.12+fi*.32;
  float cl=smoke(vec3(uv.x*(1.3+fi*.5)+fi*3.+uT*.05*(1.+fi),(uv.y-hz-y0)*6.5,1.+fi*4.+uT*.04),7);
  float band=exp(-pow((h-y0)/(.10+fi*.06),2.));
  float cd=smoothstep(.45,.70,cl)*band;
  float edge=smoothstep(.45,.55,cl)-smoothstep(.58,.75,cl);
  float near=exp(-d*(1.6+fi));
  vec3 cc=mix(vec3(.16,.05,.07)*(1.-fi*.4),vec3(2.2,1.1,.4),near*(.5+edge*1.4)+.08*edge);
  col=mix(col,cc,cd*.95);
 }
 // sun disc + glow
 col+=smoothstep(.105,.098,d)*vec3(6.,4.4,2.6)+exp(-d*7.)*vec3(2.2,1.2,.45)+exp(-d*2.)*vec3(.7,.28,.07);
 float an=atan(uv.y-S.y,uv.x-S.x);
 col+=pow(.5+.5*sin(an*27.+fbm(vec3(an*4.,0.,1.),3)*7.),3.)*exp(-d*2.)*.30*vec3(1.,.55,.2)*smoothstep(-.02,.05,uv.y-S.y);
 // horizon haze
 col+=exp(-abs(h)*14.)*vec3(1.2,.5,.15)*(.35+1.4*exp(-abs(uv.x-S.x)*1.8));
 if(h<0.){vec3 g=vec3(.22,.07,.03)*(.35+1.4*exp(-abs(uv.x-S.x)*1.6));col=mix(g,vec3(.02,.01,.01),smoothstep(0.,-.12,h));}
 return col;
}

void main(){
 vec2 uv=(gl_FragCoord.xy*2.-R)/R.x;          // x in [-1,1]
 vec3 c;
 if(SHOT==1)c=trap(uv);
 else if(SHOT==2)c=escape(uv);
 else if(SHOT==3)c=eye(uv);
 else c=sky(uv);
 c=aces(c*1.05);
 c=pow(c,vec3(1./1.06));
 o=vec4(c,1);
}
