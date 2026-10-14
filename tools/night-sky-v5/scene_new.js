// ---------------------------------------------------------------- Sun extras: cinematic blue anamorphic streak + glints (distinct from the ladder's textured Sun)
const streakMat=(c,o)=>new THREE.ShaderMaterial({transparent:true,depthTest:false,depthWrite:false,blending:THREE.AdditiveBlending,uniforms:{uC:{value:new THREE.Color(...c)},uO:{value:o}},
 vertexShader:`varying vec2 vU; void main(){ vU=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
 fragmentShader:`varying vec2 vU; uniform vec3 uC; uniform float uO; void main(){ float ax=abs(vU.x-0.5)*2.0, ay=abs(vU.y-0.5)*2.0; float a=pow(max(1.0-ax,0.0),2.2)*exp(-ay*ay*60.0); gl_FragColor=vec4(uC*a*uO,1.0);} `});
const sunStreak=new THREE.Mesh(new THREE.PlaneGeometry(1,1),streakMat([0.45,0.75,1.0],0.55)); sunStreak.scale.set(1500,70,1); sunStreak.position.copy(SUN_P); sunStreak.renderOrder=19; scene.add(sunStreak);
// ---------------------------------------------------------------- procedural 3D galaxy generator (differential rotation in the vertex shader, inclined disc, dust lanes)
let GID=0;
function makeGalaxy(o){ const id=GID++; const g=new THREE.Group(); g.rotation.order='ZXY'; g.rotation.set(o.tilt[0],o.tilt[1],o.tilt[2]); g.position.copy(o.pos); scene.add(g);
  const mk=(n,order,px)=>{ const mat=pointsMat({uGal:{value:1},uMWR:{value:o.R},uAmp:{value:0},uMin:{value:1.3*SC},uMax:{value:px*SC}}); mat.customProgramCacheKey=()=>'gx'+id+'_'+order; const P=makePoints(n,mat); scene.remove(P.pts); g.add(P.pts); P.pts.renderOrder=order; return {P,mat}; };
  const tw=r=>o.wind*Math.log(1+o.k*r); const mix=(a,b,t)=>[a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t,a[2]*(1-t)+b[2]*t];
  const put=(P,i,r,th,z,c,br,sz)=>{ P.ag[i*4]=r; P.ag[i*4+1]=th; P.ag[i*4+2]=z; P.col[i*3]=c[0]*br; P.col[i*3+1]=c[1]*br; P.col[i*3+2]=c[2]*br; P.sz[i]=sz; P.ph[i]=R(); };
  // bulge (and bar)
  const B=mk(o.nBulge,8,16); for(let i=0;i<o.nBulge;i++){ let x=gauss()*o.bulgeR, y=gauss()*o.bulgeR*(o.bar?0.55:1.0), z=gauss()*o.bulgeR*0.75; if(o.bar){ const a=o.barAng, xr=x*Math.cos(a)-y*Math.sin(a), yr=x*Math.sin(a)+y*Math.cos(a); x=xr; y=yr; x*=1.0+o.bar; }
    const r=Math.hypot(x,y), th=Math.atan2(y,x); const core=Math.exp(-r/(o.bulgeR*0.6)); put(B.P,i,r,th,z,mix(o.cBulge,[1,0.95,0.85],core*0.6),0.35+0.65*core*R(),o.szBulge*(0.6+0.8*R())); }
  // disc: exponential profile, log-spiral arms + inter-arm
  const D=mk(o.nDisc,9,12); for(let i=0;i<o.nDisc;i++){ const r=Math.min(1,-Math.log(1-R()*0.985)*o.scaleLen+0.04); const inArm=R()<o.armFrac; let th; let c,br,sz=o.szDisc*(0.6+0.9*R()*R());
    if(inArm){ const k=Math.floor(R()*o.arms); th=tw(r)+k*6.2832/o.arms+gauss()*(o.armSpread*(0.5+r)); c=mix(o.cArm,o.cArm2,R()); br=(0.35+0.65*R())*(0.8+0.5*Math.sin(r*20+th*3)*0.5); if(R()<0.035){ c=o.cHII; br=1.0; sz*=2.2; } }
    else { th=R()*6.2832; c=mix(o.cInter,o.cBulge,Math.max(0,1-r*1.6)); br=(0.18+0.5*R())*(1-0.55*r); }
    put(D.P,i,r,th,gauss()*0.012*(1+2*r),c,br,sz); }
  // ring
  let Rg=null; if(o.nRing>0){ Rg=mk(o.nRing,10,12); for(let i=0;i<o.nRing;i++){ const r=o.ringR+gauss()*o.ringW, th=R()*6.2832; put(Rg.P,i,r,th,gauss()*0.01,mix(o.cRing,o.cArm,R()*0.5),0.4+0.6*R(),o.szDisc*(0.8+R())); } }
  // dust lanes (dark, normal blending): lie just inside the arms
  const DU=mk(o.nDust,11,40); DU.mat.fragmentShader=`varying vec3 vc; uniform float uDust; void main(){ vec2 c=gl_PointCoord-0.5; float r=length(c)*2.0; float a=smoothstep(1.0,0.0,r); gl_FragColor=vec4(0.0,0.0,0.0,a*a*uDust);} `; DU.mat.uniforms.uDust={value:0}; DU.mat.blending=THREE.NormalBlending; DU.mat.needsUpdate=true;
  for(let i=0;i<o.nDust;i++){ const r=0.12+R()*0.78; const k=Math.floor(R()*o.arms); const th=tw(r)+k*6.2832/o.arms-o.dustOff+gauss()*0.035; put(DU.P,i,r,th,gauss()*0.006,[0,0,0],1.0,o.szDust*(0.6+0.9*R())); }
  const all=[B,D,DU]; if(Rg) all.push(Rg); all.forEach(a=>{ a.P.pts.geometry.attributes.aG.needsUpdate=true; a.P.pts.geometry.attributes.color.needsUpdate=true; a.P.pts.geometry.attributes.aSize.needsUpdate=true; });
  return {g,B,D,Rg,DU,setAmp(a,d){ B.mat.uniforms.uAmp.value=a*o.aBulge; D.mat.uniforms.uAmp.value=a*o.aDisc; if(Rg) Rg.mat.uniforms.uAmp.value=a*o.aDisc*1.1; DU.mat.uniforms.uDust.value=d; },setTime(t){ all.forEach(x=>x.mat.uniforms.uTime.value=t); },tw,set visible(v){ g.visible=v; }}; }
// ---------------------------------------------------------------- Andromeda: the approved plate as a depth-bulged point cloud + soft plate plane, with companions
const andG=new THREE.Group(); andG.position.set(0,0,AND_Z); andG.rotation.set(-0.18,0.22,0.0); scene.add(andG);
const andMat=new THREE.MeshBasicMaterial({transparent:true,depthTest:false,depthWrite:false,blending:THREE.AdditiveBlending,opacity:0.0});
const andPlane=new THREE.Mesh(new THREE.PlaneGeometry(AND_W,AND_H),andMat); andPlane.renderOrder=6; andG.add(andPlane);
const andPtsMat=pointsMat({uAmp:{value:0.0},uMin:{value:1.3*SC},uMax:{value:14*SC}}); const andP=makePoints(220000,andPtsMat); scene.remove(andP.pts); andG.add(andP.pts); andP.pts.renderOrder=7; andP.pts.visible=false;
new THREE.TextureLoader().load('andro_1080.png',tex=>{ 
  { const pc=document.createElement('canvas'); pc.width=540; pc.height=960; const px=pc.getContext('2d'); px.drawImage(tex.image,0,0,540,960); const im=px.getImageData(0,0,540,960); const dd=im.data;
    for(let y=0;y<960;y++) for(let x=0;x<540;x++){ const i=(y*540+x)*4; const ex=Math.min(x,539-x)/70, ey=Math.min(y,959-y)/120; const f=Math.min(1,ex)*Math.min(1,ey); const ff=f*f*(3-2*f);
      for(let c=0;c<3;c++){ dd[i+c]=Math.max(0,dd[i+c]-26)*1.12*ff; } dd[i+3]=255; }
    px.putImageData(im,0,0); const ct=new THREE.CanvasTexture(pc); ct.colorSpace=THREE.SRGBColorSpace; andMat.map=ct; andMat.needsUpdate=true; }
  const cv=document.createElement('canvas'); const cw=432, ch=768; cv.width=cw; cv.height=ch; const c2d=cv.getContext('2d'); c2d.drawImage(tex.image,0,0,cw,ch); const d=c2d.getImageData(0,0,cw,ch).data;
  // build cumulative luminance distribution
  const lum=new Float32Array(cw*ch); let tot=0; for(let i=0;i<cw*ch;i++){ const r=d[i*4]/255,g=d[i*4+1]/255,b=d[i*4+2]/255; const l=Math.max(0,0.3*r+0.59*g+0.11*b-0.06); lum[i]=Math.pow(l,1.35); tot+=lum[i]; }
  const cum=new Float64Array(cw*ch); let a=0; for(let i=0;i<cw*ch;i++){ a+=lum[i]; cum[i]=a/tot; }
  const n=andP.n; for(let k=0;k<n;k++){ const u=R(); let lo=0,hi=cw*ch-1; while(lo<hi){ const m=(lo+hi)>>1; if(cum[m]<u) lo=m+1; else hi=m; } const px=lo%cw, py=(lo/cw)|0; const fx=(px+R())/cw, fy=(py+R())/ch; const li=lum[lo];
    const X=(fx-0.5)*AND_W, Y=(0.5-fy)*AND_H, Z=Math.pow(Math.min(1,li*2.2),1.2)*130+gauss()*22-40;
    andP.pos[k*3]=X; andP.pos[k*3+1]=Y; andP.pos[k*3+2]=Z; const br=0.35+0.65*Math.min(1,li*2.0)*R(); const cr_=d[lo*4]/255, cg=d[lo*4+1]/255, cb=d[lo*4+2]/255; const mxv=Math.max(cr_,cg,cb,0.05);
    andP.col[k*3]=cr_/mxv*br; andP.col[k*3+1]=cg/mxv*br; andP.col[k*3+2]=cb/mxv*br; andP.sz[k]=1.1+2.2*R()*R()+li*2.0; andP.ph[k]=R(); }
  andP.pts.geometry.attributes.position.needsUpdate=true; andP.pts.geometry.attributes.color.needsUpdate=true; andP.pts.geometry.attributes.aSize.needsUpdate=true; andP.pts.visible=true; window.andReady=true; });
{ const n=70000, mat=pointsMat({uAmp:{value:0.0},uMin:{value:1.3*SC},uMax:{value:12*SC}}); const P=makePoints(n,mat); scene.remove(P.pts); andG.add(P.pts); P.pts.renderOrder=7; window.andHaloMat=mat;
  for(let i=0;i<n;i++){ const r=Math.pow(R(),1.5)*1500; const d=V3(gauss(),gauss()*0.8,gauss()*0.5).normalize(); P.pos[i*3]=d.x*r; P.pos[i*3+1]=d.y*r*1.6; P.pos[i*3+2]=d.z*r*0.5; const k=R(); const c=k<0.6?[1.0,0.85,0.6]:(k<0.85?[0.7,0.85,1.0]:[1.0,1.0,1.0]); const br=0.25+0.75*R()*(1-r/1800); P.col[i*3]=c[0]*br; P.col[i*3+1]=c[1]*br; P.col[i*3+2]=c[2]*br; P.sz[i]=2+5*R()*R(); P.ph[i]=R(); }
  P.pts.geometry.attributes.position.needsUpdate=true; }
const andHalo1=ringPts(V3(0,0,0),1500,'circle',[1.0,0.85,0.6],1.2), andHalo2=ringPts(V3(0,0,0),1750,'circle',[0.6,0.8,1.0],1.2); andG.add(andHalo1); andG.add(andHalo2); andHalo1.position.set(0,0,-6); andHalo2.position.set(0,0,-6);
const AND_C=V3(0,0,AND_Z);
const andCoreGlow=glowMesh([1.0,0.80,0.50],1100,0.0,0,2.2); andCoreGlow.position.copy(AND_C); andCoreGlow.renderOrder=7;
const andWhite=glowMesh([1.0,0.95,0.85],200,0.0,0,1.8); andWhite.position.copy(AND_C); andWhite.renderOrder=12;
const andStreak=new THREE.Mesh(new THREE.PlaneGeometry(1,1),streakMat([0.45,0.72,1.0],0.0)); andStreak.scale.set(5200,300,1); andStreak.position.copy(AND_C); andStreak.renderOrder=12; scene.add(andStreak);
const andRays=[]; for(let k=0;k<7;k++){ const m=new THREE.Mesh(new THREE.PlaneGeometry(1,1),spikeMat([1.0,0.82,0.55],0.0)); m.scale.set(3600+900*R(),220,1); m.position.copy(AND_C); m.renderOrder=6; m.userData.a=k*0.449+R()*0.3; scene.add(m); andRays.push(m); }
const haloG=andG; // halo rings live inside andG (from the plate block)
const shock=ringPts(V3(0,0,0),1000,'circle',[1.0,0.9,0.7],2.6); const shockG=new THREE.Group(); shockG.position.copy(AND_C); shockG.add(shock); scene.add(shockG);
// ---------------------------------------------------------------- our galaxy, seen from outside (barred spiral, warm, tilted) with a gold dot where we are
const MWR=7000;
const MWG=makeGalaxy({R:MWR,pos:V3(0,0,0),tilt:[0.95,0.15,-0.45],nBulge:60000,nDisc:300000,nRing:0,nDust:12000,bulgeR:0.075,szBulge:34,szDisc:24,szDust:56,wind:3.3,k:4.0,arms:4,armFrac:0.68,armSpread:0.08,scaleLen:0.55,ringR:0,ringW:0,dustOff:0.14,
  cBulge:[1.0,0.82,0.5],cInter:[1.0,0.9,0.7],cArm:[0.85,0.88,1.0],cArm2:[1.0,0.82,0.6],cHII:[1.0,0.5,0.55],cRing:[1,1,1],aBulge:0.55,aDisc:1.35,bar:0.9,barAng:0.5});
const US_R=0.55; const US_TH=MWG.tw(US_R); const US_L=V3(US_R*MWR*Math.cos(US_TH),US_R*MWR*Math.sin(US_TH),0);
MWG.g.updateMatrixWorld(true); { const wl=US_L.clone().applyEuler(MWG.g.rotation); MWG.g.position.copy(STAR0).sub(wl); }
const mwCenter=MWG.g.position.clone();
const mwGlow=glowMesh([1.0,0.82,0.55],2600,0.0,0,2.6); mwGlow.position.copy(mwCenter); mwGlow.renderOrder=7;
const usDot=glowMesh([1.0,0.80,0.35],120,0.0,0,2.2); usDot.renderOrder=22;
// ---------------------------------------------------------------- unified cinematic grade (teal shadows, warm highlights, vignette, grain)
{ const gp=new ShaderPass({uniforms:{tDiffuse:{value:null},uTime:{value:0}},vertexShader:`varying vec2 vUv; void main(){vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,
  fragmentShader:`uniform sampler2D tDiffuse; uniform float uTime; varying vec2 vUv; float hash(vec2 p){ return fract(sin(dot(p,vec2(12.9898,78.233)))*43758.5453); }
   void main(){ vec3 col=texture2D(tDiffuse,vUv).rgb; float l=dot(col,vec3(0.299,0.587,0.114)); col+=vec3(0.004,0.012,0.020)*(1.0-smoothstep(0.0,0.30,l));
    col*=mix(vec3(1.0),vec3(1.06,1.0,0.93),smoothstep(0.35,1.1,l)); vec2 q=vUv-0.5; col*=1.0-0.9*dot(q,q); col+=(hash(vUv*vec2(540.0,960.0)+fract(uTime)*37.0)-0.5)*0.012; gl_FragColor=vec4(col,1.0);} `}); comp.insertPass(gp,comp.passes.length-1); window.gradePass=gp; }
// (portals placed after camera path is defined)
const warpGlow=glowMesh([0.7,0.82,1.0],900,0.0,0,2.4); warpGlow.renderOrder=3;
// ---------------------------------------------------------------- camera: spline through the fly-by waypoints; head turns to each object as it passes; arc out of Andromeda; log-spaced plunge home
const PK=[[2.10,0,0,22],[2.45,4.5,2.2,-8],[2.80,0.6,0.3,-30],[3.20,-2.0,1.0,-46],[3.55,-2.6,1.2,-60],[4.30,-3.0,1.0,-100],[5.30,-8,3,-230],[6.30,-4,2,-340],[7.20,17,-4,-520],[8.20,10,0,-800],[10.80,60,25,-1900],[12.0,40,8,-9000],[13.2,10,2,-18000],[13.9,8,1.6,-18200],[15.0,260,-120,-20800],[16.3,380,-150,-21900],[17.0,-300,90,-22600],[18.0,300,250,-23200],[19.2,1400,500,-23600]];
const PASSES=[[2.45,STAR0.x,STAR0.y,STAR0.z],[3.55,MOON_C.x,MOON_C.y,MOON_C.z],[5.30,SUN_P.x,SUN_P.y,SUN_P.z],[7.20,PROX_C.x,PROX_C.y,PROX_C.z]];
const P_END=V3(1400,500,-23600), T_PL0=19.2, T_PL1=21.0, T_END=21.0;
const L_PL=Math.log(P_END.distanceTo(STAR0)/8.0);
function camPos(t){ if(t>T_PL0){ const u=Math.min(1,(t-T_PL0)/(T_PL1-T_PL0)); const f=Math.exp(-L_PL*u); return STAR0.clone().add(P_END.clone().sub(STAR0).multiplyScalar(f)); } const k=cr(PK,t); return V3(k[0],k[1],k[2]); }
// ---------------------------------------------------------------- PORTALS v2: depth gates on the flight path (camera flies THROUGH nested ring tunnels; shape language per realm)
function makePortal(kind,col,r,spacing,n,seed){ const g=new THREE.Group(); const rings=[]; const mats=[];
  for(let i=0;i<n;i++){ const rr=r*(1+0.16*i); const sub=ringPts(V3(0,0,-i*spacing),rr,kind,col,1.0,2.6); sub.userData.spin=(i%2?1:-1)*(0.35+0.08*i)*(seed%2?1:-1); sub.userData.i=i; g.add(sub); rings.push(sub); sub.traverse(o=>{ if(o.isPoints) mats.push({m:o.material,i}); }); }
  // helical filaments along the tunnel (depth cue)
  const nf=6, per=1500; for(let f=0;f<nf;f++){ const mat=pointsMat({uAmp:{value:0.8},uMin:{value:1.6*SC},uMax:{value:12*SC}}); const P=makePoints(per,mat); scene.remove(P.pts); g.add(P.pts); P.pts.renderOrder=12; mats.push({m:mat,i:99});
    for(let k=0;k<per;k++){ const u=k/per; const z=-u*spacing*(n-1); const ang=f/nf*6.2832+u*7.0; const rad=r*(1+0.16*u*(n-1))*(0.97+0.03*Math.sin(u*40)); P.pos[k*3]=rad*Math.cos(ang); P.pos[k*3+1]=rad*Math.sin(ang); P.pos[k*3+2]=z;
      const br=0.4+0.6*R(); P.col[k*3]=col[0]*br; P.col[k*3+1]=col[1]*br; P.col[k*3+2]=col[2]*br; P.sz[k]=r*(0.008+0.006*R()); P.ph[k]=R(); } P.pts.geometry.attributes.position.needsUpdate=true; }
  const mem=[]; for(let i=0;i<3;i++){ const gm=glowMesh(col,2*r*(1+0.16*i)*1.12,0.0,1,1); gm.position.set(0,0,-i*spacing); scene.remove(gm); g.add(gm); mem.push(gm); gm.renderOrder=11; }
  scene.add(g); return {g,rings,mats,n,spacing,mem}; }
function placePortal(P,tp){ const c=camPos(tp); const tan=camPos(tp+0.05).sub(camPos(tp-0.05)).normalize(); P.g.position.copy(c); P.g.quaternion.setFromUnitVectors(V3(0,0,-1),tan); P.tp=tp; P.c=c; }
const PORTALS=[
 {tp:2.85,kind:'circle',col:[0.82,0.92,1.0],r:2.8,sp:8.0,n:6},
 {tp:4.65,kind:'circle',col:[1.0,0.80,0.40],r:5.0,sp:14.0,n:6},
 {tp:6.65,kind:'circle',col:[1.0,0.45,0.32],r:4.0,sp:12.0,n:6},
 {tp:13.45,kind:'circle',col:[0.65,0.82,1.0],r:60.0,sp:200.0,n:7}
].map((o,i)=>{ const P=makePortal(o.kind,o.col,o.r,o.sp,o.n,i); P.o=o; return P; });
PORTALS.forEach(P=>placePortal(P,P.o.tp));
// chain of small gates along the path: keeps the space between realms alive (nested-ring time tunnel, colour drifts realm to realm)
const CHAIN=[]; { const stops=[[2.4,[0.82,0.92,1.0]],[4.65,[1.0,0.80,0.40]],[6.65,[1.0,0.40,0.30]],[8.35,[1.0,0.56,0.24]],[13.45,[0.65,0.82,1.0]]];
  const colAt=t=>{ for(let i=0;i<stops.length-1;i++){ const a=stops[i],b=stops[i+1]; if(t<=b[0]){ const u=Math.min(1,Math.max(0,(t-a[0])/(b[0]-a[0]))); return [a[1][0]*(1-u)+b[1][0]*u,a[1][1]*(1-u)+b[1][1]*u,a[1][2]*(1-u)+b[1][2]*u]; } } return stops[stops.length-1][1]; };
  for(let tk=2.5;tk<2.4;tk+=0.34){ const c=camPos(tk); const spd=camPos(tk+0.05).distanceTo(camPos(tk-0.05))/0.1; const r=Math.max(2.2,0.14*spd); const tan=camPos(tk+0.05).sub(camPos(tk-0.05)).normalize();
    const sub=ringPts(V3(0,0,0),r,'circle',colAt(tk),1.0,2.2); const grp=new THREE.Group(); grp.position.copy(c); grp.quaternion.setFromUnitVectors(V3(0,0,-1),tan); grp.add(sub); scene.add(grp); CHAIN.push({grp,sub,tk,r}); } }
const WK=[[0,0],[2.1,2.1],[3.0,3.55],[4.7,5.3],[6.4,7.2],[7.4,10.8],[9.3,13.2],[10.05,14.0],[12.1,16.2],[13.0,17.4],[14.6,19.2],[15.9,21.0],[16.5,21.6]];
function Wp(tn){ if(tn<=WK[0][0]) return tn; return cr(WK,Math.min(tn,WK[WK.length-1][0]))[0]; }
function posAtNew(tn){ return camPos(Math.min(Math.max(Wp(tn),2.1),21.0)); }
const _m=new THREE.Matrix4(), _q1=new THREE.Quaternion(), _q2=new THREE.Quaternion(), _q3=new THREE.Quaternion();
function lookQ(pos,target,up,out){ _m.lookAt(pos,target,up); out.setFromRotationMatrix(_m); return out; }
const ssm=(a,b,x)=>{const k=Math.min(1,Math.max(0,(x-a)/(b-a)));return k*k*(3-2*k)};
const _tmp=new THREE.Vector3();
function setT(tn){ const t=Wp(tn);
  const tc=Math.min(Math.max(t,2.1),T_END); const pos=camPos(tc); const up=V3(0,1,0);
  let ahead; if(tc>T_PL0) ahead=STAR0.clone(); else { ahead=camPos(Math.min(tc+0.7,T_PL0)); if(tc>13.9&&tc<17.0) ahead.set(0,0,AND_Z-3000); }
  lookQ(pos,ahead,up,_q1);
  PASSES.forEach(p=>{ const w=0.92*Math.exp(-Math.pow((tc-p[0])/0.95,2)); if(w>0.002){ lookQ(pos,V3(p[1],p[2],p[3]),up,_q2); _q1.slerp(_q2,w); } });
  const ub=ssm(16.2,17.4,tc); if(ub>0){ lookQ(pos,STAR0,up,_q3); _q1.slerp(_q3,ub); }
  cam.position.copy(pos); cam.quaternion.copy(_q1);
  const upl=(tc-T_PL0)/(T_PL1-T_PL0);
  const roll=0.07*Math.sin(tc*0.6)+0.12*Math.sin((tc-3.55)*1.5)*Math.exp(-Math.pow((tc-3.55)/1.0,2))-0.14*Math.exp(-Math.pow((tc-9.6)/1.2,2))+0.16*ssm(16.2,17.4,tc)*Math.sin((tc-16.6)*1.6)*(1-ssm(17.4,18.2,tc))+(tc>T_PL0?0.55*Math.sin(upl*5.5)*Math.sin(Math.PI*Math.min(1,upl)):0);
  cam.rotateZ(roll); cam.updateMatrixWorld(); cam.updateProjectionMatrix();
  const speed=posAtNew(tn+0.05).distanceTo(posAtNew(tn-0.05))/0.1; window.__speed=speed;
  glows.forEach(g=>g.quaternion.copy(cam.quaternion));
  const dF=(p)=>pos.distanceTo(p);
  spikes.forEach(m=>{ m.quaternion.copy(cam.quaternion); m.rotateZ(m.userData.k*0.7854+0.06*t); });
  star0Spikes.forEach(m=>{ m.quaternion.copy(cam.quaternion); m.rotateZ(m.userData.base+0.2*t); });
  sunStreak.quaternion.copy(cam.quaternion); andStreak.quaternion.copy(cam.quaternion); andRays.forEach(m=>{ m.quaternion.copy(cam.quaternion); m.rotateZ(m.userData.a+0.03*t); });
  { const fwd=V3(0,0,-1).applyQuaternion(cam.quaternion); warpGlow.position.copy(pos).addScaledVector(fwd,2500); warpGlow.scale.set(1400,1400,1); warpGlow.opacity=0.34*ssm(1500,6000,speed)*(1-ssm(13.2,13.9,t)); }
  const dS=dF(SUN_P), dM=dF(MOON_C), dP=dF(PROX_C), dB=dF(BET_C), d0=dF(STAR0);
  const wnd=(a,b)=>ssm(a,a+0.5,t)*(1-ssm(b-0.5,b,t));
  const wM=wnd(2.7,5.2), wS=wnd(4.2,7.4), wP=wnd(6.2,8.9), wB=0;
  moonMat.uniforms.uFade.value=wM; moon.visible=dM<4000&&wM>0.002; prox.visible=dP<3000&&wP>0.002; bet.visible=dB<30000&&wB>0.002; proxMat.uniforms.uGain.value=0.7*wP; betMat.uniforms.uGain.value=0.6*wB;
  sunCore.opacity=0.42*(1-ssm(20,10,dS))*wS; sunHalo.opacity=0.08*(1-ssm(2500,9000,dS))*wS; sunWhite.opacity=0.8*(1-ssm(700,5000,dS))*wS;
  spikes.forEach(m=>m.material.uniforms.uO.value=(m.userData.k%2?0.28:0.4)*(1-ssm(1500,6000,dS))*(0.3+0.7*ssm(10,120,dS))*wS);
  sunStreak.scale.set(1500,Math.min(70,Math.max(5,0.09*dS)),1); sunStreak.material.uniforms.uO.value=0.5*(1-ssm(300,900,dS))*wS; sunStreak.visible=dS<1000;
  star0Glow.opacity=0.5*ssm(0.8,6,d0)*(1-ssm(150,1200,d0)); star0Core.opacity=1.0*ssm(0.6,4,d0)*(1-ssm(60,900,d0));
  star0Spikes.forEach(m=>m.material.uniforms.uO.value=0.9*ssm(1,8,d0)*(1-ssm(30,500,d0)));
  proxGlow.opacity=0.4*(1-ssm(300,2500,dP))*wP; betGlow.opacity=0.3*(1-ssm(BET_R*8,BET_R*60,dB))*wB;
  proxMat.uniforms.uTime.value=t; betMat.uniforms.uTime.value=t; window.proxBurst.uniforms.uT.value=t;
  ringStar0.visible=d0<60; ringStar0.rotation.z=t*0.8;
  PORTALS.forEach((P,pi)=>{ const dd=pos.distanceTo(P.c); const vis=dd<P.o.sp*P.o.n*5+600&&tc>P.tp-2.6&&tc<P.tp+2.4; P.g.visible=vis; if(!vis) return;
    const fade=ssm(P.tp-2.6,P.tp-1.4,tc)*(1-ssm(P.tp+1.0,P.tp+2.2,tc));
    P.rings.forEach(rg=>{ rg.rotation.z=t*rg.userData.spin; }); P.mats.forEach(o=>{ o.m.uniforms.uAmp.value=(0.6+0.4*Math.sin(t*3.0-o.i*0.7+pi))*2.4*fade*(o.i===99?0.9:1.0); o.m.uniforms.uTime.value=t; });
    P.mem.forEach((gm,mi)=>{ gm.quaternion.copy(P.g.quaternion.clone().invert().multiply(cam.quaternion)); gm.opacity=(0.55-0.12*mi)*fade*(0.7+0.3*Math.sin(t*4+mi)); }); });
  ringMoon.visible=false; ringSun.visible=false; ringProx.visible=false; ringBet.visible=false;
  CHAIN.forEach((c,ci)=>{ const dt=c.tk-tc; const vis=dt>-0.6&&dt<2.6; c.grp.visible=vis; if(!vis) return; const f=ssm(2.6,1.2,dt)*(1-ssm(-0.1,-0.5,-dt*1.0+0.0)*0.0)*(dt<0?1-ssm(0,-0.6,dt):1); c.sub.rotation.z=t*(ci%2?0.5:-0.5);
    c.grp.traverse(o=>{ if(o.isPoints) o.material.uniforms.uAmp.value=1.5*ssm(2.6,0.9,dt)*(dt<0?1-ssm(0,-0.6,dt):1); }); });
  // ---- Andromeda reveal (approved plate as depth-bulged point cloud + plane) with cinematic effects
  const dA=Math.abs(pos.z-AND_Z); const ar=ssm(13.9,14.25,t); const gone=1-ssm(16.2,16.9,t); const gone2=1-ssm(17.0,18.3,t);
  andMat.opacity=0.62*ar*gone*ssm(250,1500,dA); andPlane.visible=ar>0.001&&gone>0.001;
  andPtsMat.uniforms.uAmp.value=0.40*ar*gone*(0.25+0.75*ssm(250,2600,dA)); andP.pts.visible=window.andReady&&gone>0.001; andPtsMat.uniforms.uTime.value=t;
  window.andHaloMat.uniforms.uAmp.value=0.7*ar*gone2; window.andHaloMat.uniforms.uTime.value=t;
  andHalo1.rotation.z=t*0.25; andHalo2.rotation.z=-t*0.3; andHalo1.visible=andHalo2.visible=ar>0.01&&gone2>0.001;
  const aa=ar*gone2;
  andCoreGlow.opacity=0.18*aa*ssm(200,1500,dA); andWhite.opacity=0.30*ar*gone*ssm(60,500,dA);
  andStreak.material.uniforms.uO.value=0.28*ar*gone*ssm(150,1200,dA); andStreak.visible=aa>0.001;
  andRays.forEach(m=>{ m.material.uniforms.uO.value=0.07*ar*gone*ssm(200,1500,dA); m.visible=aa>0.001; });
  { const su=(t-14.0)/1.3; shockG.visible=su>0&&su<1; shockG.scale.setScalar(0.05+4.0*Math.pow(Math.max(0,su),0.6)); shockG.quaternion.copy(cam.quaternion); ringGlobalAmp(shock,2.6*(1-ssm(0.4,1.0,su))); }
  // ---- our galaxy from outside (look-back) and the plunge home
  const wb=ssm(16.4,17.5,tc)*(1-ssm(T_PL1-0.35,T_PL1,t)); const mwNear=ssm(400,6000,pos.distanceTo(mwCenter));
  MWG.setAmp(0.75*wb*(0.4+0.6*mwNear),0.16*wb); MWG.setTime(t); MWG.g.visible=wb>0.001; mwGlow.opacity=0.22*wb*(1-ssm(3000,9000,pos.distanceTo(mwCenter))*0.0)*ssm(600,8000,pos.distanceTo(mwCenter));
  MWG.g.updateMatrixWorld(true); usDot.position.copy(STAR0); usDot.opacity=1.0*ssm(16.9,17.6,t)*(1-ssm(T_PL0+0.4,T_PL0+1.2,t)); window.usDotPos=usDot.position;
  wrapLayers.forEach(l=>{ const sc=Math.max(Math.min(dist_ref(pos),1e5),1); const w=Math.exp(-0.5*Math.pow(Math.log(sc/(l.P*0.9))/0.95,2)); l.mat.uniforms.uAmp.value=0.55*w*(1-0.8*ssm(16.8,17.6,t)*(1-ssm(T_PL0,T_PL0+0.5,t)))*(1+Math.min(3.5,(window.__speed||0)/900)); l.pts.visible=w>0.01; l.mat.uniforms.uCam.value.copy(cam.position); l.mat.uniforms.uTime.value=t; });
  window.gradePass.uniforms.uTime.value=t;
  return {pos};
}
function ringGlobalAmp(g,a){ g.parent.traverse(o=>{ if(o.isPoints) o.material.uniforms.uAmp.value=a; }); }
function dist_ref(pos){ const ds=[pos.distanceTo(STAR0),pos.distanceTo(MOON_C)*1.2,pos.distanceTo(SUN_P)*0.8,pos.distanceTo(PROX_C)*1.2,pos.distanceTo(BET_C)*0.35];
  const sp=window.__speed||1; return Math.max(Math.min(Math.min(...ds),sp*0.9+30),8); }
window.renderAt=(t,exp)=>{ setT(t); const sp=window.__speed||0; const ns=sp>600?6:(sp>120?4:2); const shut=sp>600?1/30:1/60;
  for(let i=0;i<ns;i++){ const tt=t+(i/(ns-1)-0.5)*shut; setT(tt); comp.render(); ctx.globalAlpha=1/(i+1); ctx.drawImage(renderer.domElement,0,0); }
  if(exp!==undefined&&exp<1){ ctx.globalAlpha=1-exp; ctx.fillStyle='#000'; ctx.fillRect(0,0,W,H); } ctx.globalAlpha=1; return c2.toDataURL('image/jpeg',0.94); };
window.scene=scene; window.setT=setT; window.cam=cam; window.renderer=renderer; window.comp=comp; window.THREE=THREE;
window.ready=true;
