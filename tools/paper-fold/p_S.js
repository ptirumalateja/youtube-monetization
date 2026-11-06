// =========================================================== S: space, normalised so the column is always 1 unit long
SC.S=async function(){
  const S=new THREE.Scene(); const [eT,eL,cl,mT]=await Promise.all([load('tex/earth_atmos_2048.jpg'),load('tex/earth_lights_2048.png'),load('tex/clouds_a.png'),load('tex/moon_1024.jpg')]);
  const sunDir=new THREE.Vector3(0.9,0.18,0.5).normalize();
  const neb=new THREE.Mesh(new THREE.SphereGeometry(5e6,48,24),new THREE.ShaderMaterial({side:THREE.BackSide,depthWrite:false,uniforms:{},
    vertexShader:`varying vec3 vd; void main(){vd=normalize(position); gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
    fragmentShader:`varying vec3 vd; ${NOISE} float h(vec3 p){return h3(p);} void main(){vec3 d=normalize(vd); vec3 c=vec3(0.035,0.045,0.10);
      float band=exp(-pow(dot(d,normalize(vec3(0.8,-0.25,0.35))),2.)*9.); float f=fbm3(d*3.5),f2=fbm3(d*9.+3.);
      c+=vec3(0.20,0.09,0.26)*band*f*0.8+vec3(0.08,0.14,0.30)*f2*0.3+vec3(0.55,0.32,0.22)*band*pow(f2,3.)*1.0;
      float st=pow(h(floor(d*900.)),400.)*2.5+pow(h(floor(d*400.)+7.),900.)*5.; c+=vec3(st)*(0.6+band); gl_FragColor=vec4(c,1.);}`})); neb.renderOrder=-5; S.add(neb);
  const root=new THREE.Group(); S.add(root);
  // Earth
  const earthMat=new THREE.ShaderMaterial({uniforms:{d:{value:eT},l:{value:eL},c:{value:cl},sd:{value:sunDir},detail:{value:1}},
    vertexShader:`varying vec2 vu; varying vec3 vn,wp,op; void main(){vu=uv; op=position; vn=normalize(mat3(modelMatrix)*normal); wp=(modelMatrix*vec4(position,1.)).xyz; gl_Position=projectionMatrix*viewMatrix*vec4(wp,1.);}`,
    fragmentShader:`uniform sampler2D d,l,c; uniform vec3 sd; uniform float detail; varying vec2 vu; varying vec3 vn,wp,op; ${NOISE}
     void main(){float k=dot(normalize(vn),sd); float day=smoothstep(-0.12,0.25,k); vec3 alb=texture2D(d,vu).rgb; float cl=texture2D(c,vu).r;
      vec3 q=normalize(op); float nz=fbm3(q*60.)*0.7+fbm3(q*400.)*0.5; cl=clamp(cl*(0.55+detail*nz*1.2)+detail*(nz-0.62)*0.8,0.,1.); alb*=0.85+detail*(nz-0.5)*0.5;
      vec3 col=mix(alb,vec3(1.),cl*0.85)*max(k,0.)*1.6+vec3(0.02,0.03,0.06); col+=texture2D(l,vu).rgb*(1.-day)*(1.-cl)*1.4;
      vec3 v=normalize(cameraPosition-wp); float rim=pow(1.-max(dot(normalize(vn),v),0.),3.); col+=vec3(0.3,0.55,1.)*rim*(0.25+day);
      gl_FragColor=vec4(col,1.);}`});
  const earth=new THREE.Mesh(new THREE.SphereGeometry(1,160,96),earthMat); const inD=new THREE.Vector3(0.194,0.358,-0.913);
  earth.quaternion.setFromUnitVectors(inD.clone().normalize(),new THREE.Vector3(0,1,0)); root.add(earth);
  const atm=new THREE.Mesh(new THREE.SphereGeometry(1.012,96,48),new THREE.ShaderMaterial({transparent:true,side:THREE.BackSide,depthWrite:false,blending:THREE.AdditiveBlending,
    vertexShader:`varying vec3 vn,wp; void main(){vn=normalize(mat3(modelMatrix)*normal); wp=(modelMatrix*vec4(position,1.)).xyz; gl_Position=projectionMatrix*viewMatrix*vec4(wp,1.);}`,
    fragmentShader:`varying vec3 vn,wp; void main(){vec3 v=normalize(cameraPosition-wp); float f=pow(max(dot(-normalize(vn),v),0.),1.6); gl_FragColor=vec4(vec3(0.25,0.5,1.0)*f*0.9,1.);}`})); root.add(atm);
  // generic bodies
  const bodies={};
  const mkBall=(map,color,emis)=>{const m=new THREE.Mesh(new THREE.SphereGeometry(1,48,32),map?new THREE.MeshStandardMaterial({map,roughness:1}):new THREE.MeshBasicMaterial({color})); root.add(m); return m;};
  bodies.moon=mkBall(mT); bodies.sun=mkBall(null,'#ffd9a0'); bodies.nep=mkBall(null,'#5f8fe8');
  const dot=softDot(); const mkGlow=(col,op)=>{const sp=sprite(dot,col,1,new THREE.Vector3(),op); root.add(sp); return sp;};
  const sunGlow=mkGlow('#ffb060',0.95), sunGlow2=mkGlow('#ff8a40',0.4), nepGlow=mkGlow('#6a9cff',0.6), proxGlow=mkGlow('#ff7a4a',1.0), proxGlow2=mkGlow('#ff9a60',0.5), moonGlow=mkGlow('#cfd8ff',0.25);
  const sl=new THREE.DirectionalLight('#fff4e6',3.0); sl.position.copy(sunDir).multiplyScalar(10); S.add(sl); S.add(new THREE.AmbientLight('#56607e',0.6));
  // galaxies (procedural spiral sprites)
  const spiral=(core,arm,sz)=>canvasTex(512,512,(g,w,h)=>{g.fillStyle='rgba(0,0,0,0)';g.clearRect(0,0,w,h); g.translate(w/2,h/2);
    for(let i=0;i<5200;i++){const arm_=i%2; const t=Math.pow(rnd(),0.7)*3.4; const a=t*1.9+arm_*Math.PI+ (rnd()-0.5)*0.55*(1+t*0.15); const r=18+t*66+ (rnd()-0.5)*18*(1+t*0.4);
      const x=Math.cos(a)*r, y=Math.sin(a)*r*0.92; const al=0.16*(1-t/3.6)+0.02; g.fillStyle=`rgba(${arm},${al})`; g.beginPath(); g.arc(x,y,0.8+rnd()*1.6,0,7); g.fill();}
    const rg=g.createRadialGradient(0,0,0,0,0,sz); rg.addColorStop(0,`rgba(${core},0.95)`); rg.addColorStop(0.3,`rgba(${core},0.35)`); rg.addColorStop(1,`rgba(${core},0)`); g.fillStyle=rg; g.fillRect(-w/2,-h/2,w,h);});
  const mwTex=spiral('255,226,170','190,205,255',70), andTex=spiral('255,214,160','170,190,255',60);
  const mw=new THREE.Mesh(new THREE.PlaneGeometry(1,1),new THREE.MeshBasicMaterial({map:mwTex,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,side:THREE.DoubleSide})); root.add(mw);
  const an=new THREE.Mesh(new THREE.PlaneGeometry(1,1),new THREE.MeshBasicMaterial({map:andTex,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,side:THREE.DoubleSide})); an.rotation.z=0.5; root.add(an);
  // dust galaxies / cosmic web as scaled points
  function web(N,mode){const pos=new Float32Array(N*3),col=new Float32Array(N*3),siz=new Float32Array(N); const nodes=[];for(let i=0;i<46;i++){const v=new THREE.Vector3(rnd()-0.5,rnd()-0.5,rnd()-0.5).normalize().multiplyScalar(Math.cbrt(rnd())*0.95);nodes.push(v);}
    for(let i=0;i<N;i++){let v; const r=rnd(); if(r<0.55){const a=nodes[(rnd()*46)|0],b=nodes[(rnd()*46)|0]; const t=rnd(); v=a.clone().lerp(b,t).add(new THREE.Vector3(rnd()-0.5,rnd()-0.5,rnd()-0.5).multiplyScalar(0.045));}
      else if(r<0.88){const a=nodes[(rnd()*46)|0]; v=a.clone().add(new THREE.Vector3(rnd()-0.5,rnd()-0.5,rnd()-0.5).multiplyScalar(0.16*rnd()));} else v=new THREE.Vector3(rnd()-0.5,rnd()-0.5,rnd()-0.5).multiplyScalar(2);
      if(v.length()>1)v.setLength(rnd()*0.99); pos.set([v.x,v.y,v.z],i*3); const w=rnd(); const c=w<0.18?[1,0.78,0.55]:[0.72,0.82,1]; const b=0.5+rnd()*0.8; col.set([c[0]*b,c[1]*b,c[2]*b],i*3); siz[i]=0.6+rnd()*1.6;}
    const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.BufferAttribute(pos,3)); g.setAttribute('color',new THREE.BufferAttribute(col,3)); g.setAttribute('sz',new THREE.BufferAttribute(siz,1));
    const m=new THREE.ShaderMaterial({transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,uniforms:{base:{value:1},op:{value:1},scr:{value:H}},
      vertexShader:`attribute vec3 color; attribute float sz; uniform float base,scr; varying vec3 vc; void main(){vc=color; vec4 mv=modelViewMatrix*vec4(position,1.); gl_Position=projectionMatrix*mv; gl_PointSize=clamp(sz*base*scr/(-mv.z)*0.9,1.6,11.);}`,
      fragmentShader:`uniform float op; varying vec3 vc; void main(){vec2 p=gl_PointCoord-0.5; float d=length(p); float a=smoothstep(0.5,0.0,d); gl_FragColor=vec4(vc*a*1.4,a*op);}`});
    const pts=new THREE.Points(g,m); pts.frustumCulled=false; root.add(pts); return pts;}
  const layers=[0,1,2,3,4,5].map(i=>({r:Math.pow(0.1,i),pts:web(9000,'web')}));
  const baseDot=sprite(dot,'#7fb4ff',0.07,new THREE.Vector3(0,0,0),0.9); root.add(baseDot);
  // observable universe shell (CMB look)
  const uni=new THREE.Mesh(new THREE.SphereGeometry(1,96,64),new THREE.ShaderMaterial({transparent:true,depthWrite:false,side:THREE.DoubleSide,uniforms:{op:{value:0}},
    vertexShader:`varying vec3 vn,wp,op3; void main(){op3=position; vn=normalize(mat3(modelMatrix)*normal); wp=(modelMatrix*vec4(position,1.)).xyz; gl_Position=projectionMatrix*viewMatrix*vec4(wp,1.);}`,
    fragmentShader:`uniform float op; varying vec3 vn,wp,op3; ${NOISE} void main(){vec3 p=normalize(op3); float a=fbm3(p*3.2+2.)*0.65+fbm3(p*9.)*0.35; vec3 warm=vec3(1.0,0.62,0.30), cool=vec3(0.36,0.52,0.95); vec3 c=mix(cool,warm,smoothstep(0.36,0.64,a));
      c=mix(c,vec3(1.,0.9,0.78),smoothstep(0.62,0.8,a)*0.5); vec3 v=normalize(cameraPosition-wp); float fr=pow(1.-abs(dot(normalize(vn),v)),2.); c+=vec3(0.7,0.8,1.)*fr*0.35; gl_FragColor=vec4(c*0.62,op);}`})); root.add(uni);
  // the column
  const beam=new THREE.Mesh(new THREE.CylinderGeometry(0.0055,0.0055,1,20,1,true),new THREE.ShaderMaterial({transparent:true,blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide,
    vertexShader:`varying vec3 vn,wp; void main(){vn=normalize(mat3(modelMatrix)*normal); wp=(modelMatrix*vec4(position,1.)).xyz; gl_Position=projectionMatrix*viewMatrix*vec4(wp,1.);}`,
    fragmentShader:`varying vec3 vn,wp; void main(){vec3 v=normalize(cameraPosition-wp); float f=abs(dot(normalize(vn),v)); float core=pow(f,2.5); vec3 c=mix(vec3(1.,0.55,0.22),vec3(1.,0.9,0.72),core); gl_FragColor=vec4(c*(0.5+core*2.2),1.);}`}));
  beam.position.y=0.5; root.add(beam);
  const glowB=new THREE.Mesh(new THREE.CylinderGeometry(0.03,0.03,1,24,1,true),new THREE.ShaderMaterial({transparent:true,blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide,
    vertexShader:`varying vec3 vn,wp; void main(){vn=normalize(mat3(modelMatrix)*normal); wp=(modelMatrix*vec4(position,1.)).xyz; gl_Position=projectionMatrix*viewMatrix*vec4(wp,1.);}`,
    fragmentShader:`varying vec3 vn,wp; void main(){vec3 v=normalize(cameraPosition-wp); float f=pow(abs(dot(normalize(vn),v)),4.); gl_FragColor=vec4(vec3(1.,0.6,0.3)*f*0.4,1.);}`})); glowB.position.y=0.5; root.add(glowB);
  const tip=sprite(dot,'#ffe2b0',0.16,new THREE.Vector3(0,1,0),0.7); root.add(tip);
  const C=compose(S,cam0(),[0.8,0.55,0.55]);
  function cam0(){return window.__scam||(window.__scam=new THREE.PerspectiveCamera(40,W/H,1e-4,3e7));}
  const cam=cam0(); C.passes[0].camera=cam;
  const X=-0.33; // bodies sit left of the column
  const place=(obj,glow,y,r,minR,vis,gs)=>{obj.visible=vis; if(glow)glow.visible=vis; if(!vis)return; const rr=Math.max(r,minR); obj.position.set(X,y,0); obj.scale.setScalar(rr); if(glow){glow.position.set(X,y,0); glow.scale.setScalar(rr*gs);} };
  return {render(p){
    const n=p.n, L=Lof(n), u=1/L; const t=p.t;
    const s=sstep(99.5,103,n); const dist=lerp(1.9,3.35,s)*(1+ (p.push||0)); const lx=lerp(-0.171,-0.36,s), ly=lerp(0.5,0.66,s);
    const orb=0.10*Math.sin(t*0.45);
    cam.position.set(lx+Math.sin(orb)*dist*0.4, ly+0.05*Math.sin(t*0.3), dist*Math.cos(orb)); cam.lookAt(lx,ly,0); cam.near=0.02; cam.far=4e6; cam.fov=40; cam.updateProjectionMatrix();
    const RE=6.371e6*u; earth.visible=atm.visible=RE>1e-3&&n<66;
    if(earth.visible){earth.scale.setScalar(RE); earth.position.set(0,-RE,0); atm.scale.setScalar(RE); atm.position.copy(earth.position); earthMat.uniforms.detail.value=sstep(0.02,2,RE/dist*0.2)*1.0+0.15;}
    const mY=3.844e8*u, sY=1.496e11*u, nY=4.5e12*u, pY=4.02e16*u;
    place(bodies.moon,moonGlow,mY,1.737e6*u,0.034,n>=37&&n<=48,3.2);
    place(bodies.sun,sunGlow,sY,6.96e8*u,0.05,n>=44&&n<=63,3.6); sunGlow2.visible=bodies.sun.visible; sunGlow2.position.copy(sunGlow.position); sunGlow2.scale.setScalar(sunGlow.scale.x*2.4);
    place(bodies.nep,nepGlow,nY,2.46e7*u,0.034,n>=50&&n<=66,3.0);
    proxGlow.visible=proxGlow2.visible=(n>=62&&n<=78); proxGlow.position.set(X,pY,0); proxGlow.scale.setScalar(0.11); proxGlow2.position.copy(proxGlow.position); proxGlow2.scale.setScalar(0.26);
    // galaxies
    const mwD=9.46e20*u; mw.visible=n>=76&&n<=96; mw.scale.setScalar(mwD); mw.position.set(-0.26*mwD,0,-0.01); mw.rotation.z=0.0;
    const anY=2.37e22*u, anD=2.08e21*u; an.visible=n>=82&&n<=97; an.scale.setScalar(Math.max(anD,0.13)); an.position.set(X,anY,-0.01);
    // cosmic web: ball of radius 46.5 Gly centred on Earth, only rendered once it is big enough to matter
    const Ru=46.5*GLY*u; layers.forEach(Ly=>{const rr=Ru*Ly.r; const rl=rr/1; const o=sstep(2.5,8,rl)*(1-sstep(60,300,rl))*sstep(82,86,n); Ly.pts.visible=o>0.01; Ly.pts.scale.setScalar(rr); Ly.pts.position.set(0,0,0); Ly.pts.material.uniforms.base.value=rr*0.0022; Ly.pts.material.uniforms.op.value=o;});
    baseDot.visible=n>=38&&n<=64; baseDot.position.set(0,0,0); baseDot.scale.setScalar(0.07+0.03*Math.sin(t*3));
    uni.visible=n>=100.6; uni.material.uniforms.op.value=sstep(100.6,102,n)*0.92; uni.scale.setScalar(Ru); uni.position.set(-(Ru+0.14),Ru,0);
    beam.scale.set(1,1,1);
    const marks=[]; const P=(id,y,x=X)=>marks.push({id,...project(cam,new THREE.Vector3(x,y,0))});
    P('moon',mY); P('sun',sY); P('nep',nY); P('prox',pY); P('mw',0.0,-0.26*mwD+0.0); marks.find(m=>m.id==='mw').y+=0; P('and',anY); marks.push({id:'uni',...project(cam,new THREE.Vector3(-(Ru+0.14),Ru*0.2,0))}); P('top',1.0,0);
    C.passes[1].strength=lerp(0.8,0.3,s); C.render(); return {marks,L};
  }};
};

