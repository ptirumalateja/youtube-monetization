// =========================================================== G: ground, folds 7 -> ~28
SC.G=async function(){
  const S=new THREE.Scene(); const sunDir=new THREE.Vector3(-0.2,0.05,-1);
  const sky=new THREE.Mesh(new THREE.SphereGeometry(60000,64,32),skyMat('#1f3358','#b8574f','#ff9550',sunDir,'#ffd08a',0.0012)); sky.renderOrder=-5; S.add(sky);
  S.fog=new THREE.FogExp2('#c7704f',0.002);
  const cam=new THREE.PerspectiveCamera(24,W/H,0.003,300000);
  S.traverse(o=>{if(o.isMesh&&o!==sky){o.material.depthTest=false;o.material.depthWrite=false;o.renderOrder=-4;}}); sky.material.depthTest=false; sky.material.depthWrite=false;
  const ridges=new THREE.Group(); S.add(ridges); ridges.add(ridge(-14000,900,'#b9746a',3,40000)); ridges.add(ridge(-8000,620,'#8d5a5a',11,30000)); ridges.add(ridge(-4200,380,'#5c4048',29,20000)); ridges.add(ridge(-2000,150,'#3c2c33',47,12000));
  // ground: procedural, scale-aware detail so it looks right from 1 cm to 20 km
  const gmat=new THREE.ShaderMaterial({uniforms:{camH:{value:1},cp:{value:new THREE.Vector3()},fogC:{value:new THREE.Color('#c7704f')},fogD:{value:0.002}},
    vertexShader:`varying vec3 wp; void main(){wp=(modelMatrix*vec4(position,1.)).xyz; gl_Position=projectionMatrix*viewMatrix*vec4(wp,1.);}`,
    fragmentShader:`uniform float camH,fogD; uniform vec3 cp,fogC; varying vec3 wp; ${NOISE}
     float h2(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
     float vn(vec2 p){vec2 i=floor(p),f=fract(p); f=f*f*(3.-2.*f); return mix(mix(h2(i),h2(i+vec2(1,0)),f.x),mix(h2(i+vec2(0,1)),h2(i+vec2(1,1)),f.x),f.y);}
     void main(){ vec2 q=wp.xz; float cd=max(camH,0.02); float s=0.,wsum=0.;
      for(int k=0;k<12;k++){float lam=0.004*pow(4.,float(k)); float r=lam/cd; float w=smoothstep(0.012,0.06,r)*(1.-smoothstep(4.,25.,r)); s+=w*(vn(q/lam*1.7+float(k)*7.3)-0.5); wsum+=w;}
      s=s/max(wsum,0.3);
      float riverLine=-(160.+40.*sin(q.x/260.)); float river=1.-smoothstep(-2.,2.,q.y-riverLine+1.);
      vec3 pave=mix(vec3(0.22,0.14,0.12),vec3(0.46,0.30,0.23),clamp(0.5+s*3.2,0.,1.)); vec3 grass=mix(vec3(0.14,0.12,0.07),vec3(0.36,0.29,0.14),clamp(0.5+s*3.2,0.,1.));
      float zone=smoothstep(-0.3,0.3,sin(q.x/(60.+cd*0.2))+0.2*sin(q.y/(35.+cd*0.1)));
      vec3 c=mix(pave,grass,zone*0.6);
      float lg=log2(max(cd*0.6,0.03))/3.3219; float k0=floor(lg); float ff=lg-k0; 
      for(int g=0;g<2;g++){float tile=pow(10.,k0+float(g)); float wgt=g==0?(1.-ff):ff; vec2 fr=abs(fract(q/tile)-0.5); float ln=1.-smoothstep(0.0,0.012+0.004*cd/tile,0.5-max(fr.x,fr.y)); c*=1.-0.35*ln*wgt*(1.-smoothstep(0.,1500.,cd*0.5)*0.0);}
      float sx=abs(q.x-(-300.-(q.y-cp.z)*0.2)); float gl=exp(-sx*sx/(2.*pow(60.+abs(q.y-cp.z)*0.08,2.)));
      vec3 wc=vec3(0.10,0.06,0.08)+vec3(1.,0.7,0.4)*gl*(0.25+1.2*step(0.9,h2(floor(q/vec2(9.,2.5)))))*0.9+vec3(0.35,0.17,0.13)*smoothstep(0.,1.,s+0.5)*0.4;
      c=mix(c,wc,river*step(riverLine,q.y)*0.0 + river);
      float d=length(wp-cp); float f=1.-exp(-fogD*fogD*d*d*0.0 - fogD*d); c=mix(c,fogC,f);
      gl_FragColor=vec4(c,1.);}`});
  const gr=new THREE.Mesh(new THREE.PlaneGeometry(2,2),gmat); gr.rotation.x=-Math.PI/2; gr.position.y=-0.0; S.add(gr);
  const sun=new THREE.DirectionalLight('#ffc48a',3.0); sun.position.set(-320,60,-1000); S.add(sun); S.add(new THREE.HemisphereLight('#c98b74','#2b1c1c',0.7));
  // landmarks at true size
  const bronze=new THREE.MeshStandardMaterial({color:'#6b5444',roughness:0.5,metalness:0.4,emissive:'#3a2418',emissiveIntensity:0.5});
  const stone=new THREE.MeshStandardMaterial({color:'#6a5a50',roughness:0.8});
  const unity=new THREE.Group(); [[90,18],[74,22],[60,18]].reduce((y,[w,hh])=>{const b=new THREE.Mesh(new THREE.BoxGeometry(w,hh,w),stone); b.position.y=y+hh/2; unity.add(b); return y+hh;},0);
  const st=statue(bronze); st.position.y=58; unity.add(st); unity.position.set(-125,0,0); S.add(unity); // 240 m with base
  const qutub=new THREE.Group(); const qm=new THREE.MeshStandardMaterial({color:'#9a4a30',roughness:0.85});
  [[7.15,6.2,0,15.4],[6.2,4.9,15.4,32.2],[4.9,3.7,32.2,47.5],[3.7,3.0,47.5,58.4],[3.0,2.4,58.4,66.8],[2.3,1.35,66.8,72.5]].forEach(([r0,r1,y0,y1],i)=>{
    const c=new THREE.Mesh(new THREE.CylinderGeometry(r1,r0,y1-y0,24,1),qm); c.position.y=(y0+y1)/2; qutub.add(c);
    if(i<5){const bal=new THREE.Mesh(new THREE.CylinderGeometry(r1*1.22,r1*1.1,1.1,24),new THREE.MeshStandardMaterial({color:'#6e3a28',roughness:0.9})); bal.position.y=y1-0.4; qutub.add(bal);} });
  qutub.position.set(-46,0,0); S.add(qutub);
  const person=new THREE.Group(); const pm=new THREE.MeshStandardMaterial({color:'#8a766b',roughness:0.9,emissive:'#4a3a33',emissiveIntensity:0.7});
  const part=(g,x,y,z,rz=0)=>{const m=new THREE.Mesh(g,pm); m.position.set(x,y,z); m.rotation.z=rz; person.add(m); return m;};
  part(new THREE.CapsuleGeometry(0.17,0.5,6,12),0,1.17,0); part(new THREE.CapsuleGeometry(0.075,0.68,6,10),-0.09,0.43,0); part(new THREE.CapsuleGeometry(0.075,0.68,6,10),0.09,0.43,0);
  part(new THREE.CapsuleGeometry(0.055,0.55,6,8),-0.25,1.12,0,0.08); part(new THREE.CapsuleGeometry(0.055,0.55,6,8),0.25,1.12,0,-0.08); part(new THREE.SphereGeometry(0.105,16,12),0,1.63,0);
  person.position.set(-0.5,0,0.0); S.add(person);
  // column
  const colTex=strataTex(300,false); const colMat=new THREE.MeshStandardMaterial({color:'#fff6e8',map:colTex,roughness:0.6,emissive:'#ffcf96',emissiveMap:colTex,emissiveIntensity:0.9});
  const col=new THREE.Mesh(new THREE.BoxGeometry(1,1,1),colMat); S.add(col);
  const halo=sprite(softDot(),'#ffe2b0',1,new THREE.Vector3(),0.5); S.add(halo);
  // cloud decks for the climb through the sky
  const cloudTex=canvasTex(512,512,(g,w,h)=>{g.fillStyle='rgba(0,0,0,0)';g.clearRect(0,0,w,h); for(let i=0;i<500;i++){const x=rnd()*w,y=rnd()*h,r=14+rnd()*50; const rg=g.createRadialGradient(x,y,0,x,y,r); rg.addColorStop(0,'rgba(255,238,226,0.16)'); rg.addColorStop(1,'rgba(255,238,226,0)'); g.fillStyle=rg; g.fillRect(x-r,y-r,2*r,2*r);}});
  cloudTex.wrapS=cloudTex.wrapT=THREE.RepeatWrapping; cloudTex.repeat.set(4,4);
  const decks=[2300,3500,5200,7600,10500].map(y=>{const m=new THREE.Mesh(new THREE.PlaneGeometry(120000,120000),new THREE.MeshBasicMaterial({map:cloudTex,transparent:true,depthWrite:false,side:THREE.DoubleSide,fog:false,color:'#ffd2bc'})); m.rotation.x=-Math.PI/2; m.position.y=y; S.add(m); return m;});
  const birds=[]; for(let i=0;i<8;i++){const b=new THREE.Mesh(new THREE.PlaneGeometry(1,0.28),new THREE.MeshBasicMaterial({color:'#2a1a1c',fog:false})); S.add(b); birds.push(b);}
  const C=compose(S,cam,[0.35,0.6,0.85]);
  return {render(p){
    const n=clamp(p.n,6,30); const Hh=Lof(n); const w=Math.max(0.0262,0.034*Hh);
    col.scale.set(w,Hh,w*0.75); col.position.set(0,Hh/2,0); halo.position.set(0,Hh,0); halo.scale.set(Math.max(0.08,Hh*0.05),Math.max(0.08,Hh*0.05),1);
    colMat.map.repeat.set(1,Math.max(1,Math.min(40,0.6/Math.max(Hh,0.01)*Hh/ w )));
    const d=Math.max(0.1,3.2*Hh); const yaw=0.18+0.10*Math.sin(p.t*0.5);
    const cy=Hh*0.36+0.01, ty=Hh*0.5;
    cam.position.set(-0.17*d+Math.sin(yaw)*d*0.55, cy, d*Math.cos(yaw)); cam.lookAt(-0.12*d*0.5, ty, 0);
    const far=clamp(d*500,60,400000); cam.far=far; cam.near=Math.max(0.002,d*0.01); cam.updateProjectionMatrix();
    gmat.uniforms.camH.value=Math.max(cy,0.02); gmat.uniforms.cp.value.copy(cam.position);
    const fd=4.0/far; S.fog.density=fd; gmat.uniforms.fogD.value=fd;
    const ks=far*0.8/60000; sky.scale.setScalar(ks); sky.position.copy(cam.position); const kr=far*0.8/20000; ridges.scale.setScalar(kr); ridges.position.set(cam.position.x*(1-kr),0,cam.position.z*(1-kr)); gr.scale.setScalar(far*1.2); gr.position.set(cam.position.x,0,cam.position.z);
    birds.forEach((b,i)=>{b.position.set(-d*0.5+i*d*0.07,Hh*0.8+(i%3)*Hh*0.03,-d*0.5); b.scale.setScalar(Math.max(0.6,Hh*0.012)); b.visible=Hh>8;});
    decks.forEach(dk=>{dk.visible=cam.position.y>1200;});
    const marks=[ {id:'person',...project(cam,new THREE.Vector3(person.position.x,1.75,person.position.z))},
      {id:'qutub',...project(cam,new THREE.Vector3(-46,72.5,0))}, {id:'unity',...project(cam,new THREE.Vector3(-125,240,0))}, {id:'top',...project(cam,new THREE.Vector3(0,Hh,0))} ];
    C.render(); return {marks};
  }};
};

