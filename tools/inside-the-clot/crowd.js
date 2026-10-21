// ================================================================== CROWD (video 0-3.2 s): point-cloud people on a dark wet plaza
const CO=new THREE.Vector3(4000,0,0); const CROWD_END=3.2;
const crowdGroup=new THREE.Group(); crowdGroup.position.copy(CO); scene.add(crowdGroup);
// body: capsules [boneIndex, radius, nPts]; bones are joint pairs filled per frame
const BONES=[['pelvis','neck',0.135,520],['neck','head',0.055,60],['head','headTop',0.105,300],['shL','elL',0.048,130],['elL','haL',0.040,110],['shR','elR',0.048,130],['elR','haR',0.040,110],['hiL','knL',0.068,190],['knL','ftL',0.052,170],['hiR','knR',0.068,190],['knR','ftR',0.052,170],['shL','shR',0.06,90]];
const RB=rnd(77); const PTS_PER=BONES.reduce((a,b)=>a+b[3],0);
const tmpl=[]; BONES.forEach((b,bi)=>{ for(let i=0;i<b[3];i++){ const u=RB(); const a=RB()*6.283; tmpl.push([bi,u,a,b[2]*(0.85+0.3*RB())]); } });
const NFIG=64; const figs=[];
for(let i=0;i<NFIG;i++){ let x,z,h; do{ x=(RB()-0.5)*16; z=-16+RB()*20; }while(Math.abs(x)<1.3&&z>-4&&z<2.5);
  const dir=RB()<0.6?(RB()<0.5?Math.PI/2:-Math.PI/2):(RB()<0.5?0:Math.PI); h=dir+(RB()-0.5)*0.5;
  figs.push({x,z,h,sp:1.05+0.45*RB(),ph:RB()*6.283,f:0.85+0.2*RB(),sc:0.92+0.16*RB(),hero:false}); }
const HERO={x:0,z:-1.4,h:0,sp:0,ph:0.6,f:0.95,sc:1.0,hero:true}; figs.push(HERO);
const NCP=figs.length*PTS_PER; const cpG=new THREE.BufferGeometry(); const cpPos=new Float32Array(NCP*3), cpCol=new Float32Array(NCP*3), cpSz=new Float32Array(NCP);
figs.forEach((fg,fi)=>{ for(let k=0;k<PTS_PER;k++){ const o=(fi*PTS_PER+k); const rr=RB(); let c;
  if(fg.hero){ c=rr<0.75?CREAM:GOLD; const br=0.55+0.4*RB(); cpCol[o*3]=c[0]*br; cpCol[o*3+1]=c[1]*br; cpCol[o*3+2]=c[2]*br; cpSz[o]=0.016; }
  else { c=rr<0.55?TEAL:(rr<0.85?CREAM:[0.45,0.55,0.9]); const br=0.16+0.18*RB(); cpCol[o*3]=c[0]*br; cpCol[o*3+1]=c[1]*br; cpCol[o*3+2]=c[2]*br; cpSz[o]=0.016; } } });
cpG.setAttribute('position',new THREE.BufferAttribute(cpPos,3)); cpG.setAttribute('color',new THREE.BufferAttribute(cpCol,3)); cpG.setAttribute('aSize',new THREE.BufferAttribute(cpSz,1));
const cpMat=new THREE.ShaderMaterial({transparent:true,depthTest:false,depthWrite:false,blending:THREE.AdditiveBlending,uniforms:{uK:{value:HALF/TAN},uMin:{value:1.0*SC},uMax:{value:10*SC},uFog:{value:0.075}},
  vertexShader:`attribute vec3 color; attribute float aSize; uniform float uK,uMin,uMax,uFog; varying vec3 vc; void main(){ vec4 mv=modelViewMatrix*vec4(position,1.0); float d=max(-mv.z,0.05); gl_PointSize=clamp(aSize*uK/d,uMin,uMax); vc=color*exp(-d*uFog)*(0.35+0.65*smoothstep(0.2,1.2,d)); gl_Position=projectionMatrix*mv; }`,
  fragmentShader:`varying vec3 vc; void main(){ float r=length(gl_PointCoord-0.5)*2.0; float a=smoothstep(1.0,0.0,r); gl_FragColor=vec4(vc*a*a,1.0);} `});
cpMat.customProgramCacheKey=()=>'crowd';
const crowdPts=new THREE.Points(cpG,cpMat); crowdPts.frustumCulled=false; crowdPts.renderOrder=3; crowdGroup.add(crowdPts);
// wet plaza floor: tiles, light pools, reflections of the hero's heart glow
const floorMat=new THREE.ShaderMaterial({uniforms:{uHero:{value:new THREE.Vector3()},uGlow:{value:0},uFog:{value:0.06}},
  vertexShader:`varying vec3 vW; varying float vD; void main(){ vec4 w=modelMatrix*vec4(position,1.0); vW=w.xyz; vec4 mv=viewMatrix*w; vD=-mv.z; gl_Position=projectionMatrix*mv; }`,
  fragmentShader:`uniform vec3 uHero; uniform float uGlow,uFog; varying vec3 vW; varying float vD;
   float h(vec2 p){ return fract(sin(dot(p,vec2(12.9898,78.233)))*43758.5453); }
   void main(){ vec2 p=vW.xz; vec2 g=abs(fract(p*0.8)-0.5); float line=1.0-smoothstep(0.0,0.025,min(g.x,g.y)); float tile=h(floor(p*0.8));
     vec3 c=vec3(0.012,0.025,0.04)+vec3(0.02,0.05,0.06)*tile*0.6+vec3(0.06,0.22,0.24)*line*0.35;
     for(int i=0;i<5;i++){ vec2 lp=vec2(-7.0+3.5*float(i),-6.0-2.0*mod(float(i),2.0)); float d=length(p-lp); c+=vec3(1.0,0.72,0.4)*0.10*exp(-d*d*0.08); }
     float dh=length(p-uHero.xz); c+=vec3(1.0,0.35,0.15)*uGlow*0.30*exp(-dh*dh*1.6)+vec3(1.0,0.75,0.45)*0.05*exp(-dh*dh*0.2);
     gl_FragColor=vec4(c*exp(-vD*uFog),1.0); }`});
floorMat.customProgramCacheKey=()=>'floor';
const floor=new THREE.Mesh(new THREE.PlaneGeometry(80,80),floorMat); floor.rotation.x=-Math.PI/2; floor.renderOrder=0; crowdGroup.add(floor);
// city lights behind: soft bokeh
const cityB=[]; for(let i=0;i<70;i++){ const k=RB(); const m=new THREE.Sprite(new THREE.SpriteMaterial({map:GT_EARLY(),color:new THREE.Color(...(k<0.5?GOLD:(k<0.8?CREAM:TEAL))),transparent:true,depthTest:false,depthWrite:false,blending:THREE.AdditiveBlending,opacity:0.05+0.12*RB()}));
  m.position.set((RB()-0.5)*40,0.5+RB()*9,-18-RB()*16); const s=0.6+2.2*RB(); m.scale.set(s,s,1); m.renderOrder=1; crowdGroup.add(m); cityB.push(m); }
// the hero's heart glow (beats), sits behind his left chest
const heroGlow=new THREE.Sprite(new THREE.SpriteMaterial({map:GT_EARLY(),color:0xff6a3a,transparent:true,depthTest:false,depthWrite:false,blending:THREE.AdditiveBlending,opacity:0}));
heroGlow.renderOrder=6; crowdGroup.add(heroGlow);
const heroCore=new THREE.Sprite(new THREE.SpriteMaterial({map:GT_EARLY(),color:0xffd090,transparent:true,depthTest:false,depthWrite:false,blending:THREE.AdditiveBlending,opacity:0}));
heroCore.renderOrder=7; crowdGroup.add(heroCore);
// skeleton
function rotY(v,h){ const c=Math.cos(h),s=Math.sin(h); return new THREE.Vector3(v.x*c+v.z*s,v.y,-v.x*s+v.z*c); }
function ik2(S,T,l1,l2,pole){ const d=T.clone().sub(S); const L=Math.min(d.length(),l1+l2-1e-3); const dn=d.clone().normalize(); const a=(l1*l1+L*L-l2*l2)/(2*l1*L); const ang=Math.acos(Math.max(-1,Math.min(1,a)));
  const side=pole.clone().sub(dn.clone().multiplyScalar(pole.dot(dn))).normalize(); const E=S.clone().add(dn.clone().multiplyScalar(Math.cos(ang)*l1)).add(side.multiplyScalar(Math.sin(ang)*l1)); return E; }
function pose(fg,t){ const J={}; let x=fg.x, z=fg.z, h=fg.h, amp=1, ph, hunch=0, clutch=0;
  if(fg.hero){ const k=sm(0.0,1.25,t); z=-1.4+1.35*(1-Math.pow(1-k,2)); amp=1-sm(0.75,1.25,t); ph=fg.ph+6.283*fg.f*Math.min(t,1.15); clutch=sm(1.15,1.75,t); hunch=0.22*sm(1.3,2.2,t); }
  else { x+=Math.sin(h)*fg.sp*t; z+=Math.cos(h)*fg.sp*t; ph=fg.ph+6.283*fg.f*t; }
  const sc=fg.sc; const bob=0.025*Math.abs(Math.cos(ph))*amp; const P=(v)=>rotY(v.multiplyScalar(sc),h).add(new THREE.Vector3(x,0,z));
  const pel=new THREE.Vector3(0,0.95+bob,0); const sp=new THREE.Vector3(0,0.5*Math.cos(hunch),0.5*Math.sin(hunch)); const nk=pel.clone().add(sp);
  J.pelvis=P(pel.clone()); J.neck=P(nk.clone()); J.head=P(nk.clone().add(new THREE.Vector3(0,0.09,0.03+0.08*hunch))); J.headTop=P(nk.clone().add(new THREE.Vector3(0,0.26,0.05+0.15*hunch)));
  const shL=nk.clone().add(new THREE.Vector3(0.19,-0.05,0)), shR=nk.clone().add(new THREE.Vector3(-0.19,-0.05,0)); J.shL=P(shL.clone()); J.shR=P(shR.clone());
  for(const s of [1,-1]){ const sw=-0.38*Math.sin(ph)*s*amp; const hip=new THREE.Vector3(0.1*s,0.92+bob,0); const th=0.42*Math.sin(ph)*s*amp; const kn=(0.1+0.6*Math.max(0,Math.sin(ph*s>0?ph:ph+Math.PI)))*amp+0.05;
    const knee=hip.clone().add(new THREE.Vector3(0,-0.45*Math.cos(th),0.45*Math.sin(th))); const foot=knee.clone().add(new THREE.Vector3(0,-0.45*Math.cos(th-kn),0.45*Math.sin(th-kn)));
    const tag=s>0?'L':'R'; J['hi'+tag]=P(hip.clone()); J['kn'+tag]=P(knee.clone()); J['ft'+tag]=P(foot.clone());
    const sh=s>0?shL:shR; let el=sh.clone().add(new THREE.Vector3(0.02*s,-0.30*Math.cos(sw),0.30*Math.sin(sw))); let ha=el.clone().add(new THREE.Vector3(0.01*s,-0.27*Math.cos(sw+0.3),0.27*Math.sin(sw+0.3)));
    if(s<0&&clutch>0){ const T=nk.clone().add(new THREE.Vector3(0.07,-0.17,0.13+0.1*hunch)); const el2=ik2(sh,T,0.30,0.27,new THREE.Vector3(-0.6,-1,0.3)); el.lerp(el2,clutch); ha.lerp(T,clutch); }
    if(s>0&&clutch>0){ el.lerp(sh.clone().add(new THREE.Vector3(0.05,-0.29,0.06)),clutch); ha.lerp(sh.clone().add(new THREE.Vector3(0.06,-0.55,0.12)),clutch); }
    J['el'+tag]=P(el); J['ha'+tag]=P(ha); }
  return J; }
let heroChest=new THREE.Vector3();
function setCrowd(t){ const b=beat(t); let o=0; const A=new THREE.Vector3(), B=new THREE.Vector3(), ax=new THREE.Vector3(), n1=new THREE.Vector3(), n2=new THREE.Vector3(), up=new THREE.Vector3(0,1,0), alt=new THREE.Vector3(1,0,0);
  for(const fg of figs){ const J=pose(fg,t); const bonesJ=BONES.map(bb=>[J[bb[0]],J[bb[1]]]);
    for(let k=0;k<PTS_PER;k++,o++){ const tp=tmpl[k]; const [Ja,Jb]=bonesJ[tp[0]]; ax.copy(Jb).sub(Ja); const L=ax.length(); ax.normalize(); n1.copy(Math.abs(ax.y)>0.9?alt:up).cross(ax).normalize(); n2.copy(ax).cross(n1);
      const r=tp[3]*(tp[0]===0?1.0:1.0); const ca=Math.cos(tp[2]), sa=Math.sin(tp[2])*(tp[0]===0?0.7:1);
      cpPos[o*3]=Ja.x+ax.x*L*tp[1]+(n1.x*ca+n2.x*sa)*r; cpPos[o*3+1]=Ja.y+ax.y*L*tp[1]+(n1.y*ca+n2.y*sa)*r; cpPos[o*3+2]=Ja.z+ax.z*L*tp[1]+(n1.z*ca+n2.z*sa)*r; }
    if(fg.hero){ heroChest.copy(J.neck).lerp(J.pelvis,0.33); const fwd=rotY(new THREE.Vector3(0,0,1),fg.h); const left=rotY(new THREE.Vector3(1,0,0),fg.h); heroChest.add(left.multiplyScalar(0.05)).add(fwd.multiplyScalar(0.02)); } }
  cpG.attributes.position.needsUpdate=true;
  const g=sm(1.2,1.9,t); const pulse=0.55+0.45*b; heroGlow.position.copy(heroChest); heroCore.position.copy(heroChest);
  heroGlow.material.opacity=g*0.55*pulse; const gs=0.35+0.25*g+0.12*b+1.2*sm(2.5,3.2,t); heroGlow.scale.set(gs,gs,1); heroCore.material.opacity=g*0.9*pulse; heroCore.scale.set(0.09+0.05*b,0.09+0.05*b,1);
  floorMat.uniforms.uHero.value.set(heroChest.x,0,heroChest.z); floorMat.uniforms.uGlow.value=g*pulse;
  // camera: high-wide over the crowd -> onto the man -> into his chest
  const C=heroChest.clone().add(CO);
  const keys=[[0,0.6,6.8,12.5,1.0],[0.9,0.5,4.6,9.0,1.1],[1.7,0.25,2.4,4.2,1.25],[2.5,0.1,1.45,1.25,1.3],[3.2,0.03,1.32,0.12,1.32]];
  const k=catm(keys,t); cam.position.set(CO.x+k[0],k[1],CO.z+k[2]); const look=new THREE.Vector3(CO.x,k[3],CO.z-1.0).lerp(C,sm(0.6,2.0,t)); cam.up.set(Math.sin(0.03*Math.sin(t)),1,0); cam.lookAt(look); cam.updateMatrixWorld(); }
window.heroChestScreen=()=>{ const v=heroChest.clone().add(CO).project(cam); return [(v.x+1)/2,(1-v.y)/2]; };
// video -> scene time warp (monotone cubic through the VO-locked knots)
const WK=[[3.2,0.4],[4.4,2.25],[9.75,8.6],[10.75,9.3],[14.4,13.55],[19.0,18.7],[21.6,21.0],[24.9,24.0]];
const WM=(()=>{ const n=WK.length, d=[], m=[]; for(let i=0;i<n-1;i++) d.push((WK[i+1][1]-WK[i][1])/(WK[i+1][0]-WK[i][0])); m.push(d[0]); for(let i=1;i<n-1;i++) m.push(d[i-1]*d[i]<=0?0:2/(1/d[i-1]+1/d[i])); m.push(d[n-2]); return m; })();
function warp(t){ if(t<=WK[0][0]) return WK[0][1]; const n=WK.length; if(t>=WK[n-1][0]) return WK[n-1][1]; let i=0; while(t>WK[i+1][0]) i++; const h=WK[i+1][0]-WK[i][0], u=(t-WK[i][0])/h;
  const h00=2*u*u*u-3*u*u+1, h10=u*u*u-2*u*u+u, h01=-2*u*u*u+3*u*u, h11=u*u*u-u*u; return h00*WK[i][1]+h10*h*WM[i]+h01*WK[i+1][1]+h11*h*WM[i+1]; }
window.warp=warp;
function setVideo(t){ const cr=t<CROWD_END; crowdGroup.visible=cr;
  if(cr){ heart.visible=false; dust.visible=false; wall.visible=false; rbc.visible=false; platelets.visible=false; fibrin.visible=false; debris.visible=false; moPts.visible=false; crys.visible=false; bokeh.forEach(m=>m.visible=false); pGlow.material.opacity=0; setCrowd(t); bloom.strength=0.8; }
  else { setT(warp(t)); } }
