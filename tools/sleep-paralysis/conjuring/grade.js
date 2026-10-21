// Conjuring-style grade: filmic tone curve, sickly teal-green shadows, warm candle highlights, reds kept,
// heavy moving film grain, lens fringing, oppressive vignette, a red heartbeat throb and fade to black.
import * as T from 'three';

export const GradeShader={
 uniforms:{tDiffuse:{value:null},uRes:{value:new T.Vector2(1080,1920)},uTime:{value:0},uFrame:{value:0},uExpo:{value:1},uFade:{value:0},uRed:{value:0},uCA:{value:.012},uGrain:{value:.11}},
 vertexShader:`varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
 fragmentShader:`uniform sampler2D tDiffuse;uniform vec2 uRes;uniform float uTime,uFrame,uExpo,uFade,uRed,uCA,uGrain;varying vec2 vUv;
  vec3 aces(vec3 x){return clamp((x*(2.51*x+.03))/(x*(2.43*x+.59)+.14),0.,1.);}
  vec3 toS(vec3 c){c=max(c,0.);return mix(c*12.92,1.055*pow(c,vec3(1./2.4))-.055,step(.0031308,c));}
  float h(vec2 p){p=fract(p*vec2(.1031,.1030));p+=dot(p,p.yx+33.33);return fract((p.x+p.y)*p.x);}
  void main(){
   vec2 uv=vUv,d=uv-.5;float r2=dot(d*vec2(.75,1.),d*vec2(.75,1.));
   vec3 c=vec3(texture2D(tDiffuse,uv-d*uCA*r2*2.).r,texture2D(tDiffuse,uv).g,texture2D(tDiffuse,uv+d*uCA*r2*2.).b)*uExpo;
   c=toS(aces(c*1.1));
   float L=dot(c,vec3(.2126,.7152,.0722));
   float red=clamp((c.r-max(c.g,c.b)*1.25)*3.,0.,1.);
   float warm=clamp((c.r-c.b)*2.2,0.,1.)*smoothstep(.25,.7,L);
   c=mix(vec3(L),c,mix(.45,1.,max(red,warm*.8)));                       // drained colour, reds and flame survive
   vec3 shadowTint=vec3(.62,1.0,.9), highTint=vec3(1.04,.95,.8);
   c*=mix(shadowTint,highTint,smoothstep(.05,.6,L));
   c+=vec3(.0,.026,.022)*(1.-smoothstep(0.,.25,L));                     // lifted blacks go sickly green-teal
   c=pow(max(c,0.),vec3(1.12));                                          // crush
   // red heartbeat throb from the edges
   float rr=length(d*vec2(1.,1.25));
   c=mix(c,c*vec3(1.25,.35,.32)+vec3(.12,0.,0.)*smoothstep(.35,.8,rr),uRed*smoothstep(.2,.75,rr));
   // vignette
   c*=mix(1.,.12,smoothstep(.28,.85,rr));
   // grain: two scales, stronger in the darks, new every frame
   vec2 gp=uv*uRes;float s=uFrame*7.13;
   float g=(h(gp+s)+h(gp*1.7+s*1.3)+h(floor(gp/2.)+s*.7))/3.-.5;
   c+=g*uGrain*(1.25-L);
   // the odd dust speck and hair on the gate
   float sp=step(.99992,h(floor(gp/3.)+floor(uFrame)*13.7));c=mix(c,vec3(.02),sp*.8);
   c*=1.-uFade;
   gl_FragColor=vec4(clamp(c,0.,1.),1.);
  }`
};
