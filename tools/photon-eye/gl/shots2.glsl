#version 300 es
precision highp float;
uniform vec2 R;
uniform float uT,uZ,uPX,uPY,uA,uR;
// v2 continuous camera
uniform float uCx,uCy,uCz,uYaw,uPitch,uRoll,uF,uPx,uPy,uPz,uLit,uYS,uEx,uEz,uTe,uSG,uRing;
// v2 eye / sky
uniform float uCX2,uCY2,uS,uSX,uSY,uSun;
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


// ---------------------------------------------------------------- 5: one camera through the Sun and out of its surface
vec3 rotX(vec3 v,float a){float c=cos(a),s=sin(a);return vec3(v.x,v.y*c-v.z*s,v.y*s+v.z*c);}
vec3 rotY(vec3 v,float a){float c=cos(a),s=sin(a);return vec3(v.x*c+v.z*s,v.y,-v.x*s+v.z*c);}
vec3 rotZ(vec3 v,float a){float c=cos(a),s=sin(a);return vec3(v.x*c-v.y*s,v.x*s+v.y*c,v.z);}
float vor(vec2 p){
 vec2 i=floor(p),f=fract(p);float d=9.;
 for(int y=-1;y<=1;y++)for(int x=-1;x<=1;x++){vec2 g=vec2(x,y);vec2 h=vec2(h31(vec3(i+g,1.)),h31(vec3(i+g,2.)));
  h=.5+.38*sin(uT*1.6+6.283*h);d=min(d,length(g+h-f));}
 return d;
}
vec3 sunfly(vec2 uv){
 vec3 C=vec3(uCx,uCy,uCz),Ph=vec3(uPx,uPy,uPz);
 vec3 rd=normalize(vec3(uv*uF,1.));
 rd=rotY(rotX(rotZ(rd,uRoll),uPitch),uYaw);
 vec3 col=vec3(0);float T=1.;
 float t=.03+.02*h31(vec3(gl_FragCoord.xy,uT*7.));
 for(int i=0;i<76;i++){
  float dt=.018+.045*t;
  vec3 P=C+rd*t;
  float ys=uYS+.10*(fbm(vec3(P.xz*1.4,uT*.25),3)-.5);
  float below=ys-P.y;
  float inside=smoothstep(-.03,.03,below);
  // plasma at three speeds: a big slow body, a mid swirl, fast small wisps
  float big=smoke(P*1.05+vec3(.0,uT*.04,uT*.07),6);
  float wisp=fbm(P*4.4+vec3(uT*.55,-uT*.35,uT*.7),5);
  float s=(.78*big+.32*wisp-.33)*1.6+.30;   // ~[.25,.75]
  float d=smoothstep(.50,.70,s);
  d*=smoothstep(.10,.50,length(P-C))*(.25+.75*smoothstep(.04,.30,length(P-Ph)));
  float surfK=smoothstep(.55,0.,abs(below));
  float dens=d*inside+surfK*inside*.9;                         // the photosphere: a dense, glowing skin
  // corona wisps and the jet above the surface
  vec2 e=P.xz-vec2(uEx,uEz);float h=-below;
  dens+=(1.-inside)*smoothstep(.55,.85,s)*exp(-max(h,0.)*2.5)*.30;
  float jet=step(.001,uTe)*exp(-dot(e,e)/(.006+max(h,0.)*.05))*smoothstep(0.,.03,h)*smoothstep(.15+uTe*1.5,uTe*1.2,h)*smoothstep(.35,.75,wisp);
  dens+=jet*2.;
  float dl=length(P-Ph);
  float lit=1.6*uLit/(1.+dl*dl*4.5)+.02*uLit;
  // the Sun's own glow, brightest at the surface; granules boil there
  float gran=1.-smoothstep(.0,.7,vor(P.xz*15.+vec2(uT*.15,0.)));gran=mix(gran,smoothstep(.3,.8,big),.35);
  float glow=uSG*inside*exp(-max(below,0.)*3.2)*(1.+(gran*.9-.4)*surfK);
  float ringR=uRing;float ring=step(.001,uTe)*exp(-pow((length(e)-ringR)/(.05+.04*wisp),2.))*smoothstep(.6,0.,abs(below))*(.4+1.2*smoothstep(.4,.7,wisp));
  lit+=glow+ring*3.5+jet*3.;
  col+=T*(1.-inside)*exp(-max(h,0.)*5.)*vec3(.9,.38,.08)*.05*uSG*dt*10.;   // hot haze hugging the surface
  float edge=1.-smoothstep(.0,.12,abs(s-.56));
  float L1=min(lit,2.2);
  vec3 c=gold(.28+L1*.50+edge*.25*L1)*(L1*(1.+2.6*edge*inside)*1.9+.012*uLit);
  float k=dens*dt*5.;
  col+=T*c*k;
  T*=exp(-k*2.6);
  col+=T*vec3(1.,.58,.18)*.010*uLit*dt/(.006+dl*dl);
  t+=dt;
  if(T<.01||t>16.)break;
 }
 return col;
}
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
 vec2 p=vec2(uCX2,uCY2)+(uv-c)*.80/zz-vec2(uSX,uSY);float r=length(p)/.80;float a=atan(p.y,p.x);
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
 float ab=floor((a/6.2832+.5)*140.);float ext=.55+.5*h31(vec3(ab,3.,1.));      // fibres of different lengths
 float fib3=fbm(vec3(a*90.+fib2*4.,r*12.,13.),4);
 float t=smoothstep(.38,.80,fib*.6+wav*.5)*(.55+.45*smoothstep(ext+.05,ext-.10,r))+.25*smoothstep(.55,.8,fib3)*smoothstep(.3,.6,r);t=.10+.9*t*t*(.6+.6*fib2);
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
 vec3 eyecol=col;
 if(e.x>=0.)eyecol=mix(col,e*.95,mix(.85,1.,uS));
 col=eyecol;
 // cornea: big soft window reflection + sharp sun catchlight
 col+=exp(-pow(length((p-vec2(-.28,.30))*vec2(1.,1.6))/.16,2.))*.16*vec3(1.,.88,.7)*smoothstep(1.1,.9,r);
 col+=exp(-pow(length(p-vec2(-.27,.29)+vec2(uSX,uSY)*1.6)/.012,2.))*3.5*vec3(1.,.95,.85);
 float shade=smoothstep(0.,.25,top-p.y)*(.55+.45*smoothstep(0.,.15,p.y-bot));
 vec3 skin=vec3(.07,.03,.017)*(.5+.7*fbm(vec3(uv*5.,7.),5))*(.3+.9*max(0.,lightside));
 col=mix(skin,col*shade,open);
 // wet lid-margin highlight
 col+=exp(-pow((top-p.y)/.012,2.))*open*.0+exp(-pow((p.y-bot)/.01,2.))*.22*vec3(1.,.75,.5)*smoothstep(1.2,0.,abs(u));
 vec3 sp=vec3(0.);if(e.x>=0.)sp=e*.95;
 return mix(col,sp,uS);
}

// ---------------------------------------------------------------- 4: the sunset sky
vec3 sky(vec2 uv){
 float hz=-.42;
 vec2 S=vec2(.34,hz+.05-uSun);
 float zz=uZ>0.?uZ:1.;
 uv=S+(uv-S)/zz;
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
 vec2 uv=(gl_FragCoord.xy*2.-R)/R.x;
 vec3 c;
 if(SHOT==5)c=sunfly(uv);
 else if(SHOT==3)c=eye(uv);
 else c=sky(uv);
 c=aces(c*1.05);
 c=pow(c,vec3(1./1.06));
 o=vec4(c,1);
}
