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