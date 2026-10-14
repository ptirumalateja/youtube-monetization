// ================================================================== v8: ONE AXIS. camera looks down -Z the whole time (except the final pull-back arc); targets first; rings centred
const ssm=(a,b,x)=>{const k=Math.min(1,Math.max(0,(x-a)/(b-a)));return k*k*(3-2*k)};
// ---------------------------------------------------------------- Sun as a clear golden disc (not the ladder's H-alpha Sun), Proxima as a red-orange sphere
const sunBall=new THREE.Mesh(new THREE.SphereGeometry(18,96,64),starMat([1.0,0.58,0.18],5.0,0.5,0.9)); sunBall.position.copy(SUN_P); sunBall.renderOrder=21; scene.add(sunBall);
moon.renderOrder=22; prox.renderOrder=20; prox.scale.setScalar(6.0/1.7); sunStreak.visible=false;
bet.visible=false; betGlow.opacity=0; if(window.betShell) window.betShell.visible=false; window.proxBurst.uniforms.uT0.value=1e9;
[ringMoon,ringSun,ringProx,ringBet].forEach(r=>r.visible=false);
// ---------------------------------------------------------------- centred ring tunnels
const RINGS=[]; const RT={moon:[2.4,3.7],sun:[4.45,5.4],prox:[6.65,7.3],hyper:[8.35,12.0]};
function addRing(z,r,col,grp,amp){ const g=ringPts(V3(0,0,z),r,'circle',col,1.0,2.4); g.userData={z,r,grp,amp:amp||1,t0:RT[grp][0],t1:RT[grp][1]}; RINGS.push(g); }
[-14,-22,-30,-38].forEach(z=>addRing(z,2.1,[0.85,0.93,1.0],'moon'));
[-100,-125,-150,-175].forEach(z=>addRing(z,6.5,[1.0,0.80,0.40],'sun'));
[-450,-530,-610,-690,-770].forEach(z=>addRing(z,19,[1.0,0.46,0.30],'prox'));
for(let i=0;i<23;i++){ const u=i/22; const c=u<0.5?[1.0-0.35*u*2,0.42+0.4*u*2,0.30+0.1*u*2]:[0.65+0.0,0.82,1.0-0.0]; const col=u<0.5?[1.0,0.45+0.35*(u*2),0.30+0.2*(u*2)]:[1.0-0.35*((u-0.5)*2),0.80+0.02*((u-0.5)*2),0.50+0.5*((u-0.5)*2)]; addRing(-1500-500*i,130,col,'hyper'); }
// ---------------------------------------------------------------- light ripple: a ring that leaves the object and arrives at the camera while the counter ticks
const RIP=[{t0:3.3,z:MOON_C.z,r:MOON_R*1.2,col:[0.85,0.93,1.0]},{t0:5.2,z:SUN_P.z,r:22,col:[1.0,0.82,0.45]},{t0:7.1,z:PROX_C.z,r:8.5,col:[1.0,0.5,0.35]},{t0:10.9,z:AND_Z,r:700,col:[0.85,0.9,1.0]}].map(o=>{ const g=ringPts(V3(0,0,0),1.0,'circle',o.col,1.0,3.0); g.userData=o; return g; });
// ---------------------------------------------------------------- the pull-back picture: our galaxy as a node, Andromeda as a node, a light beam between them
const MIDZ=-11000;
const mwNode=new THREE.Group(); mwNode.position.set(0,0,-8); mwNode.rotation.set(0.62,0.2,0.4); scene.add(mwNode);
{ const n=70000, mat=pointsMat({uAmp:{value:0.0},uMin:{value:1.5*SC},uMax:{value:10*SC}}); const P=makePoints(n,mat); scene.remove(P.pts); mwNode.add(P.pts); P.pts.renderOrder=8; window.mwNodeMat=mat;
  for(let i=0;i<n;i++){ const bulge=R()<0.22; let x,y,z; if(bulge){ x=gauss()*230; y=gauss()*230; z=gauss()*140; } else { const r=Math.min(1,-Math.log(1-R()*0.985)*0.30+0.03)*1900; const arm=Math.floor(R()*2); const th=2.4*Math.log(1+4*r/1900)+arm*3.1416+gauss()*0.16; x=r*Math.cos(th); y=r*Math.sin(th); z=gauss()*40; }
    const c=bulge?[1.0,0.84,0.55]:(R()<0.5?[1.0,0.9,0.72]:[0.78,0.86,1.0]); const br=0.25+0.75*R(); P.pos[i*3]=x; P.pos[i*3+1]=y; P.pos[i*3+2]=z; P.col[i*3]=c[0]*br; P.col[i*3+1]=c[1]*br; P.col[i*3+2]=c[2]*br; P.sz[i]=14+26*R(); P.ph[i]=R(); }
  P.pts.geometry.attributes.position.needsUpdate=true; }
const mwGlow2=glowMesh([1.0,0.85,0.6],4200,0.0,0,2.6); mwGlow2.position.set(0,0,-8); mwGlow2.renderOrder=7;
const beamGeo=new THREE.BufferGeometry().setFromPoints([V3(0,0,-8),V3(0,0,AND_Z+300)]); const beam=new THREE.Line(beamGeo,new THREE.LineBasicMaterial({color:new THREE.Color(1.0,0.84,0.52),transparent:true,opacity:0.0,blending:THREE.AdditiveBlending,depthTest:false,depthWrite:false})); beam.renderOrder=9; scene.add(beam);
const beamPts=(()=>{ const n=5000, mat=pointsMat({uAmp:{value:0.0},uMin:{value:1.4*SC},uMax:{value:6*SC}}); const P=makePoints(n,mat); scene.remove(P.pts); scene.add(P.pts); P.pts.renderOrder=9;
  for(let i=0;i<n;i++){ const u=R(); P.pos[i*3]=gauss()*8; P.pos[i*3+1]=gauss()*8; P.pos[i*3+2]=-8+(AND_Z+300+8)*u; const br=0.3+0.7*R(); P.col[i*3]=1.0*br; P.col[i*3+1]=0.84*br; P.col[i*3+2]=0.55*br; P.sz[i]=6+8*R(); P.ph[i]=R(); }
  P.pts.geometry.attributes.position.needsUpdate=true; return mat; })();
const pulse=glowMesh([1.0,0.92,0.7],900,0.0,0,2.2); pulse.renderOrder=23;
const usDot=glowMesh([1.0,0.82,0.4],160,0.0,0,2.2); usDot.position.copy(STAR0); usDot.renderOrder=24;
// ---------------------------------------------------------------- camera: keys in the NEW timeline, all on the axis
const PK=[[2.10,0.3,0.15,22],[2.50,0.2,0.1,-8],[2.90,0,0,-28],[3.50,0,0,-46],[4.40,0,0,-52],[4.55,3,0.2,-58],[4.75,6,0.4,-80],[5.00,3,0.2,-150],[5.20,0,0,-204],[6.30,0,0,-218],[6.50,12,0.5,-285],[6.70,28,1,-345],[6.90,14,0.5,-500],[7.10,0,0,-822],[8.20,0,0,-834],[8.35,6,0.3,-860],[8.50,15,0.5,-905],[8.75,6,0.2,-1700],[9.00,0,0,-3500],[9.60,0,0,-11000],[10.00,0,0,-13000],[10.50,0,0,-13200],[11.50,0,0,-19500],[12.60,0,0,-21400],[13.20,9000,1800,-20800],[13.80,32000,4500,-15500],[14.40,56000,6000,-11000],[14.90,30000,3000,-4000],[15.30,4000,400,200],[15.65,0,0,45]];
function camPos(t){ const k=cr(PK,Math.min(Math.max(t,2.1),15.65)); return V3(k[0],k[1],k[2]); }
const _m=new THREE.Matrix4(), _q1=new THREE.Quaternion();
function lookQ(pos,target,up,out){ _m.lookAt(pos,target,up); out.setFromRotationMatrix(_m); return out; }
const AND_C2=V3(0,0,AND_Z), MID=V3(0,0,MIDZ);
function setT(t){
  const pos=camPos(t); cam.position.copy(pos);
  // orientation: straight down the axis, except the pull-back arc and the dive home
  if(t<12.6){ cam.quaternion.identity(); }
  else if(t<14.4){ const a=ssm(12.9,14.2,t), b=ssm(13.0,14.3,t); const tgt=AND_C2.clone().lerp(MID,a); const up=V3(0,1,0).lerp(V3(0,0,-1),b).normalize(); lookQ(pos,tgt,up,_q1); cam.quaternion.copy(_q1); }
  else { const a=ssm(14.6,15.5,t), b=ssm(14.5,15.5,t); const tgt=MID.clone().lerp(STAR0,a); const up=V3(0,0,-1).lerp(V3(0,1,0),b).normalize(); lookQ(pos,tgt,up,_q1); cam.quaternion.copy(_q1); }
  cam.updateMatrixWorld(); cam.updateProjectionMatrix();
  const speed=camPos(t+0.05).distanceTo(camPos(t-0.05))/0.1; window.__speed=speed;
  glows.forEach(g=>g.quaternion.copy(cam.quaternion));
  spikes.forEach(m=>{ m.quaternion.copy(cam.quaternion); m.rotateZ(m.userData.k*0.7854+0.06*t); });
  star0Spikes.forEach(m=>{ m.quaternion.copy(cam.quaternion); m.rotateZ(m.userData.base+0.2*t); });
  andStreak.quaternion.copy(cam.quaternion); andRays.forEach(m=>{ m.quaternion.copy(cam.quaternion); m.rotateZ(m.userData.a+0.03*t); });
  const d0=pos.distanceTo(STAR0), dM=pos.distanceTo(MOON_C), dS=pos.distanceTo(SUN_P), dP=pos.distanceTo(PROX_C);
  // ---- object windows (each object only exists around its own moment)
  const wM=ssm(2.3,2.7,t)*(1-ssm(4.8,5.2,t)), wS=ssm(4.2,4.6,t)*(1-ssm(6.6,7.0,t)), wP=ssm(6.3,6.7,t)*(1-ssm(8.5,8.9,t));
  moonMat.uniforms.uFade.value=wM; moon.visible=wM>0.002; sunBall.visible=wS>0.002; prox.visible=wP>0.002;
  starMatSet(sunBall,0.62*wS); proxMat.uniforms.uGain.value=0.7*wP; proxMat.uniforms.uTime.value=t; betMat.uniforms.uGain.value=0;
  sunCore.scale.set(52,52,1); sunHalo.scale.set(120,120,1); sunWhite.scale.set(10,10,1);
  sunCore.opacity=0.22*wS; sunHalo.opacity=0.035*wS; sunWhite.opacity=0.10*wS;
  spikes.forEach(m=>{ m.scale.set(m.userData.k%2?90:150,70,1); m.material.uniforms.uO.value=(m.userData.k%2?0.07:0.10)*wS; });
  proxGlow.scale.set(44,44,1); proxGlow.opacity=0.5*wP;
  // star0: the opening star and the star we dive back to
  const w0=(1-ssm(2.7,3.2,t))+ssm(14.7,15.2,t);
  star0Glow.opacity=0.5*ssm(0.8,6,d0)*w0*(1-ssm(150,1200,d0)); star0Core.opacity=1.0*ssm(0.6,4,d0)*w0*(1-ssm(60,900,d0));
  star0Spikes.forEach(m=>m.material.uniforms.uO.value=0.9*ssm(1,8,d0)*w0*(1-ssm(30,500,d0)));
  ringStar0.visible=w0>0.01&&d0<60; ringStar0.rotation.z=t*0.8;
  // ---- ring tunnels (always centred on the axis; vanishing point = frame centre)
  RINGS.forEach((g,i)=>{ const u=g.userData; const dA=pos.z-u.z; const vis=dA>0&&dA<60*u.r+2000&&t>=u.t0&&t<u.t1&&pos.x*pos.x+pos.y*pos.y<(u.r*1.2)*(u.r*1.2); g.visible=vis; if(!vis) return;
    const far=Math.min(60*u.r,9000); const a=1.6*u.amp*(1-ssm(far*0.5,far,dA))*ssm(0.02*u.r,0.35*u.r,dA)*ssm(u.t0,u.t0+0.15,t)*(1-ssm(u.t1-0.15,u.t1,t)); g.rotation.z=t*(i%2?0.4:-0.4);
    g.traverse(o=>{ if(o.isPoints){ o.material.uniforms.uAmp.value=a; o.material.uniforms.uTime.value=t; } }); });
  // ---- light ripples
  RIP.forEach(g=>{ const o=g.userData; const u=Math.min(1,Math.max(0,(t-o.t0)/0.8)); g.visible=u>0&&u<1; if(!g.visible) return;
    const d0r=Math.max(40,Math.abs(pos.z-o.z)); const d=Math.max(d0r*(1-u),1.5); const half=Math.tan(14.7*Math.PI/180); const th0=Math.atan2(o.r,d0r); const th=th0+(0.95*14.7*Math.PI/180-th0)*u*u; g.position.set(0,0,pos.z-d); g.scale.setScalar(Math.max(d*Math.tan(th),0.05));
    const a=2.2*Math.sin(Math.PI*Math.min(1,u*1.05)); g.traverse(q=>{ if(q.isPoints){ q.material.uniforms.uAmp.value=a; q.material.uniforms.uTime.value=t; } }); });
  // ---- Andromeda: a faint oval at the vanishing point during the tunnel (target first), a soft bloom, then the full reveal
  const dA=Math.abs(pos.z-AND_Z); const ar=ssm(8.6,9.8,t); const gone=1-ssm(13.9,14.6,t)*0.0;
  andMat.opacity=0.62*ar*ssm(250,1500,dA); andPlane.visible=ar>0.001;
  andPtsMat.uniforms.uAmp.value=0.40*ar*(0.25+0.75*ssm(250,2600,dA)); andP.pts.visible=window.andReady&&ar>0.001; andPtsMat.uniforms.uTime.value=t;
  andHalo1.visible=false; andHalo2.visible=false; shockG.visible=false; window.andHaloMat.uniforms.uAmp.value=0;
  const bloom=Math.exp(-Math.pow((t-10.7)/0.35,2));
  andCoreGlow.opacity=(0.12*ar+0.28*bloom+0.4*ssm(12.7,13.6,t)*(1-ssm(14.6,15.2,t)))*ssm(200,1500,dA); andWhite.opacity=(0.18*bloom+0.5*ssm(12.7,13.6,t)*(1-ssm(14.6,15.2,t)))*ssm(60,500,dA);
  andStreak.material.uniforms.uO.value=0.22*ar*ssm(150,1200,dA)*(1-ssm(11.4,11.9,t)); andRays.forEach(m=>{ m.material.uniforms.uO.value=0.06*ar*ssm(200,1500,dA)*(1-ssm(11.4,11.9,t)); });
  // ---- pull-back picture: two nodes + beam + travelling pulse
  const pb=ssm(12.4,13.4,t)*(1-ssm(15.2,15.62,t));
  mwNode.visible=pb>0.001; window.mwNodeMat.uniforms.uAmp.value=0.9*pb; window.mwNodeMat.uniforms.uTime.value=t; mwGlow2.opacity=0.30*pb;
  beam.visible=pb>0.001; beam.material.opacity=0.55*pb; beamPts.uniforms.uAmp.value=0.8*pb; beamPts.uniforms.uTime.value=t;
  const pu=((t-12.9)/1.4); pulse.visible=pb>0.001&&pu>0&&pu<1.3; pulse.position.set(0,0,-8+(AND_Z+300+8)*Math.min(1,Math.max(0,pu))); pulse.opacity=1.2*pb*(pu<1?1:Math.max(0,1-(pu-1)/0.3));
  usDot.opacity=1.0*ssm(12.6,13.2,t)*(1-ssm(15.3,15.62,t)); window.usDotPos=usDot.position;
  // ---- dust: present near objects, thin in the long vacuum of the arc
  wrapLayers.forEach(l=>{ const sc=Math.max(Math.min(dist_ref(pos),1e5),1); const w=Math.exp(-0.5*Math.pow(Math.log(sc/(l.P*0.9))/0.95,2)); l.mat.uniforms.uAmp.value=0.55*w*(1-0.85*ssm(12.7,13.6,t)*(1-ssm(14.8,15.3,t)))*(1+Math.min(3.5,(window.__speed||0)/900)); l.pts.visible=w>0.01; l.mat.uniforms.uCam.value.copy(cam.position); l.mat.uniforms.uTime.value=t; });
  window.gradePass.uniforms.uTime.value=t; warpGlow.opacity=0.0;
  return {pos};
}
function starMatSet(mesh,g){ mesh.material.uniforms.uGain.value=g; mesh.material.uniforms.uTime.value=window.__tNow||0; }
function dist_ref(pos){ const ds=[pos.distanceTo(STAR0),pos.distanceTo(MOON_C)*1.2,pos.distanceTo(SUN_P)*0.8,pos.distanceTo(PROX_C)*1.2]; const sp=window.__speed||1; return Math.max(Math.min(Math.min(...ds),sp*0.9+30),8); }
window.renderAt=(t,exp)=>{ window.__tNow=t; setT(t); const sp=window.__speed||0; const ns=sp>600?6:(sp>120?4:2); const shut=sp>600?1/30:1/60;
  for(let i=0;i<ns;i++){ const tt=t+(i/(ns-1)-0.5)*shut; window.__tNow=tt; setT(tt); comp.render(); ctx.globalAlpha=1/(i+1); ctx.drawImage(renderer.domElement,0,0); }
  if(exp!==undefined&&exp<1){ ctx.globalAlpha=1-exp; ctx.fillStyle='#000'; ctx.fillRect(0,0,W,H); } ctx.globalAlpha=1; return c2.toDataURL('image/jpeg',0.94); };
window.scene=scene; window.setT=setT; window.cam=cam; window.renderer=renderer; window.comp=comp; window.THREE=THREE; window.camPos=camPos;
window.ready=true;
