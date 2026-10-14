// ================================================================== NIGHT SKY v5: time tunnel (3D fly-by along the line of sight)
const V3=(x,y,z)=>new THREE.Vector3(x,y,z);
const MOON_C=V3(0,0,-70), MOON_R=4.0;
const SUN_P=V3(0,0,-320);
const PROX_C=V3(0,0,-900);
const BET_C=V3(4000,4000,-1e6), BET_R=130;
const AND_Z=-22000, AND_W=1800, AND_H=3200;
const STAR0=V3(0,0,-8);
// ---------------------------------------------------------------- generic procedural star/planet surface material
const surfVS=`varying vec3 vP; varying vec3 vN; varying vec3 vV; void main(){ vP=normalize(position); vec4 mv=modelViewMatrix*vec4(position,1.0); vN=normalize(normalMatrix*normal); vV=normalize(-mv.xyz); gl_Position=projectionMatrix*mv; }`;
const starMat=(col,scale,speed,gain)=>new THREE.ShaderMaterial({uniforms:{uTime:{value:0},uCol:{value:new THREE.Color(...col)},uScale:{value:scale},uSpeed:{value:speed},uGain:{value:gain}},depthTest:false,depthWrite:false,vertexShader:surfVS,
 fragmentShader:`${NOISE} varying vec3 vP; varying vec3 vN; varying vec3 vV; uniform float uTime,uScale,uSpeed,uGain; uniform vec3 uCol;
  void main(){ vec3 p=normalize(vP); float t=uTime*uSpeed; vec3 w=p*2.0+vec3(0.0,0.0,t*0.2); vec3 warp=vec3(snoise(w),snoise(w+5.1),snoise(w+9.7));
   float g=fbm(p*uScale+warp*0.8+vec3(0.0,t*0.15,0.0)); float c=1.0-abs(snoise(p*uScale*2.0+warp*1.5+t*0.1)); c=pow(c,3.0);
   float L=0.55+0.55*g+0.45*c; float mu=clamp(dot(vN,vV),0.0,1.0); L*=0.35+0.65*pow(mu,0.55);
   vec3 col=uCol*L*1.25+vec3(1.0,0.6,0.25)*pow(max(L,0.0),3.2)*0.55; col+=uCol*pow(1.0-mu,3.0)*0.9; gl_FragColor=vec4(col*uGain,1.0); }`});
// ---------------------------------------------------------------- Moon (silver, crater field, one-sided light)
const moonMat=new THREE.ShaderMaterial({uniforms:{uL:{value:new THREE.Vector3(-0.78,0.28,0.56).normalize()},uFade:{value:1}},depthTest:false,depthWrite:false,vertexShader:surfVS,
 fragmentShader:`${NOISE} varying vec3 vP; varying vec3 vN; varying vec3 vV; uniform vec3 uL; uniform float uFade;
  float h1(vec3 p){ return fract(sin(dot(p,vec3(127.1,311.7,74.7)))*43758.5453); }
  vec3 h3(vec3 p){ return fract(sin(vec3(dot(p,vec3(127.1,311.7,74.7)),dot(p,vec3(269.5,183.3,246.1)),dot(p,vec3(113.5,271.9,124.6))))*43758.5453); }
  float crater(vec3 p,float s){ vec3 q=p*s; vec3 i=floor(q), f=fract(q); float h=0.0;
    for(int x=-1;x<=1;x++) for(int y=-1;y<=1;y++) for(int z=-1;z<=1;z++){ vec3 g=vec3(float(x),float(y),float(z)); vec3 o=h3(i+g); vec3 r=g+o-f; float d=length(r); float rad=0.16+0.30*h1(i+g+3.3); float rr=d/rad;
      if(rr<1.5){ h+=-(1.0-smoothstep(0.0,0.9,rr))*0.85+exp(-pow((rr-1.0)*4.5,2.0))*0.5; } } return h; }
  float H(vec3 p){ return 0.55*crater(p,3.2)+0.32*crater(p,7.5)+0.16*crater(p,16.0)+0.05*fbm(p*30.0); }
  void main(){ vec3 p=normalize(vP); vec3 n=p; vec3 t1=normalize(cross(n,vec3(0.0,1.0,0.0013))); vec3 t2=cross(n,t1); float e=0.012;
   float h0=H(p); float ha=H(normalize(p+e*t1)); float hb=H(normalize(p+e*t2)); vec3 nb=normalize(n-0.10*((ha-h0)/e*t1+(hb-h0)/e*t2));
   float mar=smoothstep(-0.05,0.35,fbm(p*2.2+1.7)); vec3 alb=mix(vec3(0.90,0.92,0.97),vec3(0.42,0.44,0.50),mar*0.85); alb*=0.8+0.2*smoothstep(-1.0,0.6,h0);
   float lam=max(dot(nb,uL),0.0); float term=smoothstep(-0.05,0.25,dot(n,uL)); vec3 col=alb*(lam*term*0.62+0.012);
   float mu=clamp(dot(vN,vV),0.0,1.0); col+=vec3(0.35,0.5,0.9)*pow(1.0-mu,4.0)*0.18*term; gl_FragColor=vec4(col*uFade,1.0); }`});
const moon=new THREE.Mesh(new THREE.SphereGeometry(MOON_R,96,64),moonMat); moon.position.copy(MOON_C); moon.renderOrder=20; scene.add(moon);
// ---------------------------------------------------------------- Sun: blazing flare star (NOT the ladder's textured sphere): core, spikes, streak, orbiting sparks
const sunCore=glowMesh([1.0,0.80,0.45],50,0.6,0,3.0); sunCore.position.copy(SUN_P); sunCore.renderOrder=18;
const sunHalo=glowMesh([1.0,0.62,0.22],300,0.14,0,2.4); sunHalo.position.copy(SUN_P); sunHalo.renderOrder=17;
const sunWhite=glowMesh([1.0,0.97,0.9],9,0.8,0,2.0); sunWhite.position.copy(SUN_P); sunWhite.renderOrder=19;
const spikeMat=(c,o)=>new THREE.ShaderMaterial({transparent:true,depthTest:false,depthWrite:false,blending:THREE.AdditiveBlending,uniforms:{uC:{value:new THREE.Color(...c)},uO:{value:o}},
 vertexShader:`varying vec2 vU; void main(){ vU=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
 fragmentShader:`varying vec2 vU; uniform vec3 uC; uniform float uO; void main(){ float ax=abs(vU.x-0.5)*2.0, ay=abs(vU.y-0.5)*2.0; float a=pow(max(1.0-ax,0.0),5.0)*exp(-ay*ay*900.0); gl_FragColor=vec4(uC*a*uO,1.0);} `});
const spikes=[]; for(let k=0;k<4;k++){ const m=new THREE.Mesh(new THREE.PlaneGeometry(1,1),spikeMat([1.0,0.78,0.42],k%2?0.35:0.6)); m.scale.set(k%2?300:520,300,1); m.position.copy(SUN_P); m.renderOrder=19; m.userData.k=k; scene.add(m); spikes.push(m); }
// ---------------------------------------------------------------- marker rings (spark points): circle / double+cross / hexagon / counter-rotating halos
function ringPts(center,r,kind,col,amp,szm){ const n=2600, mat=pointsMat({uAmp:{value:amp},uMin:{value:1.6*SC},uMax:{value:9*SC}}); const g=new THREE.Group(); g.position.copy(center); scene.add(g);
  const P=makePoints(n,mat); scene.remove(P.pts); g.add(P.pts); P.pts.renderOrder=12;
  for(let i=0;i<n;i++){ let x,y,z=gauss()*r*0.004; const u=R();
    if(kind==='hex'){ const e=Math.floor(R()*6), t2=R(), a0=e/6*6.2832, a1=(e+1)/6*6.2832; x=r*((1-t2)*Math.cos(a0)+t2*Math.cos(a1)); y=r*((1-t2)*Math.sin(a0)+t2*Math.sin(a1)); }
    else if(kind==='double'){ const a=R()*6.2832; const rr=u<0.5?r:r*1.17; x=rr*Math.cos(a); y=rr*Math.sin(a); if(u>0.86){ const q=Math.floor(R()*4); const L2=(R()*2-1)*r*1.9; x=(q%2?L2:0); y=(q%2?0:L2); } }
    else { const a=R()*6.2832; x=r*Math.cos(a)+gauss()*r*0.004; y=r*Math.sin(a)+gauss()*r*0.004; }
    P.pos[i*3]=x; P.pos[i*3+1]=y; P.pos[i*3+2]=z; const c=col; const br=0.5+0.5*R(); P.col[i*3]=c[0]*br; P.col[i*3+1]=c[1]*br; P.col[i*3+2]=c[2]*br; P.sz[i]=r*(0.004+0.006*R())*(szm||1); P.ph[i]=R(); }
  P.pts.geometry.attributes.position.needsUpdate=true; return g; }
const ringMoon=ringPts(MOON_C,MOON_R*3.2,'circle',[0.75,0.85,1.0],1.2); ringMoon.rotation.set(0.35,-0.5,0);
const ringStar0=ringPts(STAR0,5.0,'circle',[1.0,0.85,0.6],1.4);
const ringSun=ringPts(SUN_P,60,'double',[1.0,0.78,0.38],1.4); ringSun.rotation.set(0.25,0.3,0);
const ringProx=ringPts(PROX_C,9,'hex',[1.0,0.35,0.28],1.6); ringProx.rotation.set(-0.3,0.4,0);
const ringBet=ringPts(BET_C,BET_R*2.2,'circle',[1.0,0.55,0.25],1.2); ringBet.rotation.set(0.5,-0.3,0);
// ---------------------------------------------------------------- Proxima (small red dwarf) + flare burst; Betelgeuse (mottled supergiant) + gas shells
const proxMat=starMat([1.0,0.16,0.06],5.0,1.2,0.7); const prox=new THREE.Mesh(new THREE.SphereGeometry(1.7,64,48),proxMat); prox.position.copy(PROX_C); prox.renderOrder=20; scene.add(prox);
const proxGlow=glowMesh([1.0,0.22,0.12],30,0.5,0,2.4); proxGlow.position.copy(PROX_C); proxGlow.renderOrder=18;
const betMat=starMat([1.0,0.22,0.04],2.6,0.5,0.6); const bet=new THREE.Mesh(new THREE.SphereGeometry(BET_R,96,64),betMat); bet.position.copy(BET_C); bet.renderOrder=20; scene.add(bet);
const betGlow=glowMesh([1.0,0.38,0.10],BET_R*3.5,0.3,0,2.2); betGlow.position.copy(BET_C); betGlow.renderOrder=17;
{ const n=26000, mat=pointsMat({uAmp:{value:0.9},uMin:{value:1.4*SC},uMax:{value:10*SC}}); const P=makePoints(n,mat); scene.remove(P.pts); const g=new THREE.Group(); g.position.copy(BET_C); scene.add(g); g.add(P.pts); P.pts.renderOrder=13; window.betShell=g;
  for(let i=0;i<n;i++){ const shell=1.25+Math.pow(R(),1.5)*2.4; const d=V3(gauss(),gauss(),gauss()).normalize(); const lump=1+0.55*Math.sin(d.x*3.1+1.0)*Math.sin(d.y*2.3)+0.4*Math.sin(d.z*4.1+d.x*2.0); const rr=BET_R*shell*lump;
    P.pos[i*3]=d.x*rr; P.pos[i*3+1]=d.y*rr; P.pos[i*3+2]=d.z*rr; const k=R(); const c=k<0.6?[1.0,0.38,0.12]:(k<0.9?[1.0,0.62,0.25]:[0.9,0.2,0.2]); const br=(0.2+0.7*R())/(0.6+0.4*shell); P.col[i*3]=c[0]*br; P.col[i*3+1]=c[1]*br; P.col[i*3+2]=c[2]*br; P.sz[i]=BET_R*(0.006+0.014*R()); P.ph[i]=R(); }
  P.pts.geometry.attributes.position.needsUpdate=true; }
{ const n=3000, mat=new THREE.ShaderMaterial({transparent:true,depthTest:false,depthWrite:false,blending:THREE.AdditiveBlending,uniforms:{uT:{value:0},uT0:{value:7.0},uK:{value:HALF/TAN}},
  vertexShader:`attribute vec3 color; attribute float aSize; varying vec3 vc; uniform float uT,uT0,uK; void main(){ float a=max(uT-uT0,0.0); vec3 d=normalize(position); vec3 p=d*(1.2+a*(6.0+8.0*aSize*60.0)); vec4 mv=modelViewMatrix*vec4(p,1.0); float dist=max(-mv.z,0.5); gl_PointSize=clamp(1.6*uK/dist*0.9*(1.0+aSize*30.0),1.5,8.0); vc=color*exp(-a*0.55)*step(0.0,uT-uT0)*1.4; gl_Position=projectionMatrix*mv; }`,
  fragmentShader:`varying vec3 vc; void main(){ float r=length(gl_PointCoord-0.5)*2.0; float a=smoothstep(1.0,0.0,r); gl_FragColor=vec4(vc*a*a,1.0);} `});
  const g=new THREE.BufferGeometry(); const pos=new Float32Array(n*3), col=new Float32Array(n*3), sz=new Float32Array(n);
  for(let i=0;i<n;i++){ const d=V3(gauss(),gauss(),gauss()).normalize(); d.z=-Math.abs(d.z)*0.4+d.z*0.4; d.normalize(); pos[i*3]=d.x; pos[i*3+1]=d.y; pos[i*3+2]=d.z; const k=R(); const c=k<0.5?[1.0,0.4,0.2]:[1.0,0.75,0.5]; const b=0.5+0.5*R(); col[i*3]=c[0]*b; col[i*3+1]=c[1]*b; col[i*3+2]=c[2]*b; sz[i]=R()*0.02; }
  g.setAttribute('position',new THREE.BufferAttribute(pos,3)); g.setAttribute('color',new THREE.BufferAttribute(col,3)); g.setAttribute('aSize',new THREE.BufferAttribute(sz,1));
  const pts=new THREE.Points(g,mat); pts.position.copy(PROX_C); pts.frustumCulled=false; pts.renderOrder=14; scene.add(pts); window.proxBurst=mat; }
// ---------------------------------------------------------------- the first star (the flare the viewer was watching)
const star0Glow=glowMesh([1.0,0.95,0.85],7,0.5,0,2.2); star0Glow.position.copy(STAR0); star0Glow.renderOrder=19;
const star0Core=glowMesh([1.0,1.0,1.0],1.6,1.0,0,1.6); star0Core.position.copy(STAR0); star0Core.renderOrder=19;
const star0Spikes=[0,1].map(k=>{ const m=new THREE.Mesh(new THREE.PlaneGeometry(1,1),spikeMat([1.0,0.95,0.85],0.9)); m.scale.set(34,26,1); m.position.copy(STAR0); m.rotation.z=k*1.5708; m.renderOrder=19; m.userData.base=k*1.5708; scene.add(m); return m; });
