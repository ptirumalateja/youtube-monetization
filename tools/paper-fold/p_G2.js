// =========================================================== G: ground lineup with familiar things, folds 7 -> ~29
SC.G=async function(){
  const S=new THREE.Scene(); const sunDir=new THREE.Vector3(-0.2,0.05,-1);
  const sky=new THREE.Mesh(new THREE.SphereGeometry(60000,64,32),skyMat('#27406a','#c4685a','#ffa060',sunDir,'#ffd08a',0.0012)); sky.renderOrder=-5; S.add(sky);
  S.fog=new THREE.FogExp2('#cf8060',0.002);
  const cam=new THREE.PerspectiveCamera(24,W/H,0.003,300000);
  const ridges=new THREE.Group(); S.add(ridges); ridges.add(ridge(-14000,900,'#b9746a',3,40000)); ridges.add(ridge(-8000,620,'#8d5a5a',11,30000)); ridges.add(ridge(-4200,380,'#5c4048',29,20000)); ridges.add(ridge(-2000,150,'#3c2c33',47,12000));
  S.traverse(o=>{if(o.isMesh&&o!==sky){o.material.depthTest=false;o.material.depthWrite=false;o.renderOrder=-4;}}); sky.material.depthTest=false; sky.material.depthWrite=false;
  const gmat=new THREE.ShaderMaterial({uniforms:{camH:{value:1},cp:{value:new THREE.Vector3()},fogC:{value:new THREE.Color('#cf8060')},fogD:{value:0.002}},
    vertexShader:`varying vec3 wp; void main(){wp=(modelMatrix*vec4(position,1.)).xyz; gl_Position=projectionMatrix*viewMatrix*vec4(wp,1.);}`,
    fragmentShader:`uniform float camH,fogD; uniform vec3 cp,fogC; varying vec3 wp;
     float h2(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
     float vn(vec2 p){vec2 i=floor(p),f=fract(p); f=f*f*(3.-2.*f); return mix(mix(h2(i),h2(i+vec2(1,0)),f.x),mix(h2(i+vec2(0,1)),h2(i+vec2(1,1)),f.x),f.y);}
     void main(){ vec2 q=wp.xz; float cd=max(camH,0.02); float s=0.,wsum=0.;
      for(int k=0;k<12;k++){float lam=0.004*pow(4.,float(k)); float r=lam/cd; float w=smoothstep(0.012,0.06,r)*(1.-smoothstep(4.,25.,r)); s+=w*(vn(q/lam*1.7+float(k)*7.3)-0.5); wsum+=w;}
      s=s/max(wsum,0.3);
      vec3 pave=mix(vec3(0.30,0.22,0.19),vec3(0.62,0.46,0.36),clamp(0.5+s*3.2,0.,1.));
      float lg=log2(max(cd*0.6,0.03))/3.3219; float k0=floor(lg); float ff=lg-k0; vec3 c=pave;
      for(int g=0;g<2;g++){float tile=pow(10.,k0+float(g)); float wgt=g==0?(1.-ff):ff; vec2 fr=abs(fract(q/tile)-0.5); float ln=1.-smoothstep(0.0,0.012+0.004*cd/tile,0.5-max(fr.x,fr.y)); c*=1.-0.30*ln*wgt;}
      float d=length(wp-cp); float f=1.-exp(-fogD*d); c=mix(c,fogC,f); gl_FragColor=vec4(c,1.);}`});
  const gr=new THREE.Mesh(new THREE.PlaneGeometry(2,2),gmat); gr.rotation.x=-Math.PI/2; S.add(gr);
  // ---- city: instanced towers with procedural lit windows (world-space), fog like the ground
  const cityMat=new THREE.ShaderMaterial({uniforms:{cp:{value:new THREE.Vector3()},fogC:{value:new THREE.Color('#cf8060')},fogD:{value:0.002}},
    vertexShader:`attribute vec3 ic; varying vec3 wp,wn,vc; void main(){ vec4 w=modelMatrix*instanceMatrix*vec4(position,1.); wp=w.xyz; wn=normalize(mat3(modelMatrix)*mat3(instanceMatrix)*normal); vc=ic; gl_Position=projectionMatrix*viewMatrix*w;}`,
    fragmentShader:`uniform vec3 cp,fogC; uniform float fogD; varying vec3 wp,wn,vc;
      float h2(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
      void main(){ vec3 n=normalize(wn); vec3 sd=normalize(vec3(-0.45,0.35,-0.8)); float lam=max(dot(n,sd),0.);
        vec3 wall=mix(vec3(0.20,0.15,0.20),vec3(0.95,0.60,0.42),lam*0.85)*(0.7+0.5*vc.x); vec3 c=wall; float d=length(wp-cp);
        if(abs(n.y)<0.5){ vec2 t=vec2(dot(wp.xz,vec2(-n.z,n.x)),wp.y); vec2 cell=vec2(3.6,3.9); vec2 id=floor(t/cell); vec2 fr=fract(t/cell);
          float win=step(0.16,fr.x)*step(fr.x,0.84)*step(0.22,fr.y)*step(fr.y,0.78); float lit=step(0.80,h2(id+floor(vc.yz*97.)));
          vec3 glass=mix(vec3(0.10,0.13,0.22),vec3(0.55,0.35,0.30),lam*0.7+0.1); vec3 wc=mix(glass,vec3(1.0,0.78,0.42),lit);
          float px=length(fwidth(t/cell)); float aa=1.-smoothstep(0.12,0.45,px); float far=(1.-smoothstep(900.,4000.,d))*aa; vec3 avg=mix(wall,mix(glass,vec3(1.0,0.78,0.42),0.2)*1.0,0.35); c=mix(mix(c,avg,1.-aa),wc,win*far*0.95); }
        else c=vec3(0.28,0.24,0.26)*(0.7+0.4*vc.x);
        float f=1.-exp(-fogD*d); c=mix(c,fogC,f); gl_FragColor=vec4(c,1.);}`});
  const mkCity=(sel,cap)=>{ const pos=[]; const cell=78; for(let ix=-80;ix<=80;ix++)for(let iz=-80;iz<=40;iz++){ const x=ix*cell+(rnd()-0.5)*8, z=iz*cell+(rnd()-0.5)*8; if(!sel(x,z))continue; const dc=Math.hypot(x,z)/6000; const u=rnd(); if(u<0.07)continue;
      const h=16+Math.pow(rnd(),2.6)*210*(1.15-0.6*Math.min(dc,1))+(rnd()<0.04?90:0); pos.push([x,z,Math.min(h,cap),42+rnd()*18,42+rnd()*18,rnd()]); } 
    const gm=new THREE.BoxGeometry(1,1,1); gm.translate(0,0.5,0); const im=new THREE.InstancedMesh(gm,cityMat,pos.length); const icA=new Float32Array(pos.length*3); const m=new THREE.Matrix4();
    pos.forEach((p,i)=>{ m.compose(new THREE.Vector3(p[0],0,p[1]),new THREE.Quaternion(),new THREE.Vector3(p[3],p[2],p[4])); im.setMatrixAt(i,m); icA[i*3]=p[5]; icA[i*3+1]=rnd(); icA[i*3+2]=rnd(); });
    gm.setAttribute('ic',new THREE.InstancedBufferAttribute(icA,3)); im.frustumCulled=false; im.renderOrder=-3; return im; };
  const cityA=mkCity((x,z)=>z<-380&&z>-5500&&Math.abs(x)<6200,270); S.add(cityA);
  const cityB=mkCity((x,z)=>z>=-380&&z<4200&&Math.abs(x)<4200&&!(x>-1100&&x<500&&z>-420&&z<420),240); cityB.visible=false; S.add(cityB);
  const sun=new THREE.DirectionalLight('#ffd6a8',3.4); sun.position.set(-300,380,900); S.add(sun); S.add(new THREE.HemisphereLight('#e0b098','#4a3430',1.0));
  // the lineup, each at true size, left of the paper
  const items=[['mug',mkMug(),0.095],['bat',mkBat(),0.86],['person',(()=>{const o=mkPerson();o.scale.setScalar(0.96);return o;})(),1.65],['hoop',mkHoop(),3.05],['giraffe',mkGiraffe(),5.7],['liberty',mkLiberty(),93],['eiffel',mkEiffel(),330],['burj',mkBurj(),828]];
  const pos={}; items.forEach(([k,o,hh])=>{const x=(k==='giraffe'?-0.62:-0.42)*hh-(k==='mug'?0.03:0); o.position.set(x,0,k==='hoop'?-0.4:0); S.add(o); pos[k]=[x,hh];});
  const ev=mkEverest(); ev.position.set(-9000,0,-40000); ev.visible=false; S.add(ev); pos.everest=[-9000,8849,-40000];
  const plane=mkAirliner(); plane.position.set(-2400,11000,-4000); plane.scale.setScalar(1); S.add(plane);
  const ct=new THREE.Mesh(new THREE.PlaneGeometry(26000,38),new THREE.MeshBasicMaterial({color:'#fff3e8',transparent:true,opacity:0.55,fog:false,side:THREE.DoubleSide})); ct.position.set(-2400-13500,11000,-4000); S.add(ct); ct.rotation.x=0;
  const colTex=strataTex(300,false); const colMat=new THREE.MeshStandardMaterial({color:'#f7f1e5',map:colTex,roughness:0.65,emissive:'#f1e4cc',emissiveIntensity:0.18});
  const col=new THREE.Mesh(new THREE.BoxGeometry(1,1,1),colMat); S.add(col);
  const cloudTex=canvasTex(512,512,(g,w,h)=>{g.clearRect(0,0,w,h); for(let i=0;i<500;i++){const x=rnd()*w,y=rnd()*h,r=14+rnd()*50; const rg=g.createRadialGradient(x,y,0,x,y,r); rg.addColorStop(0,'rgba(255,238,226,0.16)'); rg.addColorStop(1,'rgba(255,238,226,0)'); g.fillStyle=rg; g.fillRect(x-r,y-r,2*r,2*r);}});
  cloudTex.wrapS=cloudTex.wrapT=THREE.RepeatWrapping; cloudTex.repeat.set(4,4);
  const decks=[2300,3500,5200,7600,10500].map(y=>{const m=new THREE.Mesh(new THREE.PlaneGeometry(120000,120000),new THREE.MeshBasicMaterial({map:cloudTex,transparent:true,depthWrite:false,side:THREE.DoubleSide,fog:false,color:'#ffd2bc'})); m.rotation.x=-Math.PI/2; m.position.y=y; S.add(m); return m;});
  const C=compose(S,cam,[0.3,0.55,0.9]);
  return {render(p){
    const n=clamp(p.n,6,30); const Hh=Lof(n); const w=Math.max(0.0262,0.02*Hh);
    col.visible=false; col.scale.set(w,Hh,w*0.7); col.position.set(0,Hh/2,0);
    colMat.map.repeat.set(1,clamp(Hh/(w*3),1,40));
    const d=Math.max(0.1,3.2*Hh); const yaw=0.10+0.02*Math.sin(p.t*0.5);
    const cy=Hh*0.34+0.01, ty=Hh*0.5;
    cam.position.set(-0.04*Hh+Math.sin(yaw)*d*0.4, cy, d*Math.cos(yaw)); cam.lookAt(-0.04*Hh, ty, 0);
    const far=clamp(d*500,60,400000); cam.far=far; cam.near=Math.max(0.002,d*0.01); cam.updateProjectionMatrix();
    gmat.uniforms.camH.value=Math.max(cy,0.02); gmat.uniforms.cp.value.copy(cam.position);
    const fd=4.0/far; S.fog.density=fd; gmat.uniforms.fogD.value=fd;
    const ks=far*0.8/60000; sky.scale.setScalar(ks); sky.position.copy(cam.position); const kr=far*0.8/20000; ridges.scale.setScalar(kr); ridges.position.set(cam.position.x*(1-kr),0,cam.position.z*(1-kr)); gr.scale.setScalar(far*1.2); gr.position.set(cam.position.x,0,cam.position.z);
    cityMat.uniforms.cp.value.copy(cam.position); cityMat.uniforms.fogD.value=fd; cityB.visible=cam.position.y>650; cityA.visible=true; decks.forEach(dk=>{dk.visible=cam.position.y>1200;}); ev.visible=n>=25; if(pos.mug) {}; items.forEach(([k,o,hh])=>{ o.visible=hh<6*Hh; });
    const marks=[]; for(const k in pos){const q=pos[k]; marks.push({id:k,...project(cam,new THREE.Vector3(q[0],q[1],q[2]||0))});}
    marks.push({id:'plane',...project(cam,plane.position)}); marks.push({id:'top',...project(cam,new THREE.Vector3(0,Hh,0))}); marks.push({id:'base',...project(cam,new THREE.Vector3(0,0,0))});
    C.render(); return {marks};
  }};
};
