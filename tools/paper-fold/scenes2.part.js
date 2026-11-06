
const clamp=(x,a,b)=>Math.min(b,Math.max(a,x)); const lerp=(a,b,t)=>a+(b-a)*t; const sstep=(a,b,x)=>{const t=clamp((x-a)/(b-a),0,1);return t*t*(3-2*t)};
const ease=t=>t<0.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;
const LY=9.4607e15, GLY=LY*1e9;
const Lof=n=>1e-4*Math.pow(2,n); // column length in metres after n folds of a 0.1 mm sheet
const NOISE=`float h3(vec3 p){return fract(sin(dot(p,vec3(127.1,311.7,74.7)))*43758.5453);}
 float n3(vec3 p){vec3 i=floor(p),f=fract(p); f=f*f*(3.-2.*f); return mix(mix(mix(h3(i),h3(i+vec3(1,0,0)),f.x),mix(h3(i+vec3(0,1,0)),h3(i+vec3(1,1,0)),f.x),f.y),mix(mix(h3(i+vec3(0,0,1)),h3(i+vec3(1,0,1)),f.x),mix(h3(i+vec3(0,1,1)),h3(i+vec3(1,1,1)),f.x),f.y),f.z);}
 float fbm3(vec3 p){float a=0.5,s=0.;for(int i=0;i<5;i++){s+=a*n3(p);p*=2.03;a*=0.5;}return s;}`;
function project(cam,v){const p=v.clone().project(cam); return {x:(p.x*0.5+0.5)*W,y:(1-(p.y*0.5+0.5))*H,vis:p.z<1&&p.z>-1};}
const SC={};

// =========================================================== D: desk, folds 0 -> 7
SC.D=async function(){
  const S=new THREE.Scene(); S.background=new THREE.Color('#3a2b22'); S.fog=new THREE.Fog('#4a3628',0.5,2.2);
  const cam=new THREE.PerspectiveCamera(26,W/H,0.004,50);
  const wood=woodTex(); wood.wrapS=wood.wrapT=THREE.RepeatWrapping; wood.repeat.set(1.4,1.2);
  const desk=new THREE.Mesh(new THREE.BoxGeometry(2.2,0.04,1.6),new THREE.MeshStandardMaterial({map:wood,roughness:0.55}));
  desk.position.set(0.1,-0.02,0.1); desk.receiveShadow=true; S.add(desk);
  const wall=new THREE.Mesh(new THREE.PlaneGeometry(8,5),new THREE.MeshBasicMaterial({map:canvasTex(256,256,(g,w,h)=>{const r=g.createRadialGradient(70,90,10,128,128,240);
    r.addColorStop(0,'#6a4a36');r.addColorStop(0.5,'#45352a');r.addColorStop(1,'#3a2b22');g.fillStyle=r;g.fillRect(0,0,w,h);}),fog:false}));
  wall.position.set(0.1,0.5,-0.72); S.add(wall);
  const bk=bokehDisc(); const cols=['#ffb36a','#ffd49a','#ff9a55','#ffe2b8','#9fc0ff'];
  const bokeh=[]; for(let i=0;i<90;i++){const p=new THREE.Vector3(-0.5+rnd()*1.4,0.08+rnd()*0.5,-0.7); const sp=sprite(bk,cols[(rnd()*cols.length)|0],0.02+rnd()*0.05,p,0.12+rnd()*0.25); sp.material.fog=false; S.add(sp); bokeh.push(sp);}
  const key=new THREE.SpotLight('#ffb978',3.4,5,0.8,0.8,1.2); key.position.set(-0.45,0.7,0.5); key.target.position.set(0.1,0,0.1); key.castShadow=true; key.shadow.mapSize.set(2048,2048); key.shadow.radius=5; key.shadow.bias=-0.0003; S.add(key,key.target);
  S.add(new THREE.HemisphereLight('#6b5444','#1a120c',0.7));
  const glow=sprite(softDot(),'#ffb070',0.7,new THREE.Vector3(-0.45,0.5,-0.2),0.45); glow.material.fog=false; S.add(glow);
  const sheetM=new THREE.MeshStandardMaterial({color:'#f6f1e6',roughness:0.8,emissive:'#f3e8d4',emissiveIntensity:0.12});
  const sideM=new THREE.MeshStandardMaterial({map:strataTex(48,false),roughness:0.85,emissive:'#d9ccb4',emissiveIntensity:0.1});
  const mats=[sideM,sideM,sheetM,sheetM,sideM,sideM];
  const root=new THREE.Group(); S.add(root);
  const A=0.297,B=0.210;
  const stat=new THREE.Mesh(new THREE.BoxGeometry(1,1,1),mats); stat.castShadow=stat.receiveShadow=true; root.add(stat);
  const piv=new THREE.Group(); root.add(piv); const mov=new THREE.Mesh(new THREE.BoxGeometry(1,1,1),mats); mov.castShadow=mov.receiveShadow=true; piv.add(mov);
  // notebook for scale (slides in next to the 7-fold stack)
  const nb=new THREE.Group(); const paperM=new THREE.MeshStandardMaterial({color:'#f6f1e6',roughness:0.8});
  const pages=new THREE.Mesh(new THREE.BoxGeometry(0.148,0.0118,0.205),[sideM,sideM,paperM,paperM,sideM,sideM]); pages.position.y=0.0065; nb.add(pages);
  const coverM=new THREE.MeshStandardMaterial({color:'#2f5d7a',roughness:0.6});
  const top=new THREE.Mesh(new THREE.BoxGeometry(0.152,0.0008,0.209),coverM); top.position.y=0.0128; nb.add(top); const bot=top.clone(); bot.position.y=0.0004; nb.add(bot);
  const spine=new THREE.Mesh(new THREE.BoxGeometry(0.004,0.0132,0.209),coverM); spine.position.set(-0.076,0.0066,0); nb.add(spine);
  nb.traverse(o=>{o.castShadow=o.receiveShadow=true}); nb.rotation.y=-0.4; S.add(nb);
  const dd=softDot(); for(let i=0;i<60;i++){S.add(sprite(dd,'#ffd8a8',0.002+rnd()*0.004,new THREE.Vector3(-0.2+rnd()*0.5,0.02+rnd()*0.2,-0.1+rnd()*0.4),0.2+rnd()*0.35));}
  const C=compose(S,cam,[0.4,0.6,0.85]);
  let last=null;
  return {render(p){
    const k=clamp(p.k,0,7); const j=Math.min(6,Math.floor(k)); const pr=k>=7?1:k-j; const e=ease(clamp((pr-0.04)/0.9,0,1));
    let sx=A,sz=B; for(let i=0;i<j;i++){ if(i%2==0)sx/=2; else sz/=2; }
    const T=1e-4*Math.pow(2,j), eps=0.00004;
    if(j%2==0){ // fold the x extent
      stat.scale.set(sx/2,T,sz); stat.position.set(sx/4,T/2+eps,sz/2);
      piv.position.set(sx/2,T+eps,sz/2); piv.rotation.set(0,0,Math.PI*e); mov.scale.set(sx/2,T,sz); mov.position.set(sx/4,-T/2,0);
    } else {
      stat.scale.set(sx,T,sz/2); stat.position.set(sx/2,T/2+eps,sz/4);
      piv.position.set(sx/2,T+eps,sz/2); piv.rotation.set(-Math.PI*e,0,0); mov.scale.set(sx,T,sz/2); mov.position.set(0,-T/2,sz/4);
    }
    const nx=(j%2==0)?lerp(sx,sx/2,e):sx, nz=(j%2==1)?lerp(sz,sz/2,e):sz; const ext=Math.max(nx,nz); const thick=T*(1+e);
    const cx=nx/2, cz=nz/2; const dist=0.07+ext*5.8;
    const yaw=0.25+0.12*Math.sin(k*0.4); const el=0.36;
    cam.position.set(cx+Math.sin(yaw)*dist*0.9, thick+dist*el, cz+Math.cos(yaw)*dist*0.9);
    cam.lookAt(cx-ext*0.04, thick*0.6+ext*0.04, cz);
    cam.fov=26; cam.updateProjectionMatrix(); S.fog.near=dist*0.9; S.fog.far=dist*0.9+1.1;
    const sa=clamp((k-6.0)/0.8,0,1); nb.visible=sa>0.001;     nb.position.set(0.012+(1-ease(sa))*0.35,0,-0.17); nb.rotation.y=-0.12;
    bokeh.forEach((b,i)=>{b.material.opacity=0.12+0.2*(0.5+0.5*Math.sin(p.t*0.8+i))});
    C.render(); return {marks:[]};
  }};
};

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
    const d=Math.max(0.1,3.2*Hh); const yaw=0.10+0.06*Math.sin(p.t*0.5);
    const cy=Hh*0.34+0.01, ty=Hh*0.5;
    cam.position.set(-0.04*Hh+Math.sin(yaw)*d*0.4, cy, d*Math.cos(yaw)); cam.lookAt(-0.04*Hh, ty, 0);
    const far=clamp(d*500,60,400000); cam.far=far; cam.near=Math.max(0.002,d*0.01); cam.updateProjectionMatrix();
    gmat.uniforms.camH.value=Math.max(cy,0.02); gmat.uniforms.cp.value.copy(cam.position);
    const fd=4.0/far; S.fog.density=fd; gmat.uniforms.fogD.value=fd;
    const ks=far*0.8/60000; sky.scale.setScalar(ks); sky.position.copy(cam.position); const kr=far*0.8/20000; ridges.scale.setScalar(kr); ridges.position.set(cam.position.x*(1-kr),0,cam.position.z*(1-kr)); gr.scale.setScalar(far*1.2); gr.position.set(cam.position.x,0,cam.position.z);
    decks.forEach(dk=>{dk.visible=cam.position.y>1200;}); ev.visible=n>=25;
    const marks=[]; for(const k in pos){const q=pos[k]; marks.push({id:k,...project(cam,new THREE.Vector3(q[0],q[1],q[2]||0))});}
    marks.push({id:'plane',...project(cam,plane.position)}); marks.push({id:'top',...project(cam,new THREE.Vector3(0,Hh,0))}); marks.push({id:'base',...project(cam,new THREE.Vector3(0,0,0))});
    C.render(); return {marks};
  }};
};
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
  const ribM=new THREE.MeshStandardMaterial({color:'#f6efe2',roughness:0.7,emissive:'#efe2c8',emissiveIntensity:0.22,map:strataTex(160,false)});
  const beam=new THREE.Mesh(new THREE.BoxGeometry(0.014,1,0.014),ribM); beam.position.y=0.5; beam.visible=false; root.add(beam);
  const iss=new THREE.Group(); {const tm=new THREE.MeshStandardMaterial({color:'#d8dce4',roughness:0.4,metalness:0.6,emissive:'#6a7280',emissiveIntensity:0.4}); const pm=new THREE.MeshStandardMaterial({color:'#2a3f7a',roughness:0.3,metalness:0.4,emissive:'#1a2a5a',emissiveIntensity:0.7});
    const truss=new THREE.Mesh(new THREE.BoxGeometry(1,0.06,0.06),tm); iss.add(truss); for(const x of [-0.42,-0.26,0.26,0.42]){const pn=new THREE.Mesh(new THREE.BoxGeometry(0.12,0.01,0.34),pm); pn.position.set(x,0,0); iss.add(pn);} const mod=new THREE.Mesh(new THREE.CylinderGeometry(0.05,0.05,0.5,12),tm); mod.rotation.z=Math.PI/2; mod.position.z=0.07; iss.add(mod);} root.add(iss);
  const C=compose(S,cam0(),[0.8,0.55,0.55]);
  function cam0(){return window.__scam||(window.__scam=new THREE.PerspectiveCamera(40,W/H,1e-4,3e7));}
  const cam=cam0(); C.passes[0].camera=cam;
  const X=-0.33; // bodies sit left of the column
  const place=(obj,glow,y,r,minR,vis,gs)=>{obj.visible=vis; if(glow)glow.visible=vis; if(!vis)return; const rr=Math.max(r,minR); obj.position.set(X,y,0); obj.scale.setScalar(rr); if(glow){glow.position.set(X,y,0); glow.scale.setScalar(rr*gs);} };
  return {render(p){
    const n=p.n, L=Lof(n), u=1/L; const t=p.t;
    const s=sstep(99.5,103,n); const dist=lerp(1.9,3.35,s)*(1+ (p.push||0)); const lx=lerp(-0.09,-0.3,s), ly=lerp(0.5,0.66,s);
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
    iss.visible=n>=30&&n<=40; iss.position.set(X,4.08e5*u,0); iss.scale.setScalar(Math.max(109*u,0.085)); iss.rotation.z=0.25;
    const marks=[]; const P=(id,y,x=X)=>marks.push({id,...project(cam,new THREE.Vector3(x,y,0))});
    P('moon',mY); P('iss',4.08e5*u); P('sun',sY); P('nep',nY); P('prox',pY); P('mw',0.0,-0.26*mwD+0.0); marks.find(m=>m.id==='mw').y+=0; P('and',anY); marks.push({id:'uni',...project(cam,new THREE.Vector3(-(Ru+0.14),Ru*0.2,0))}); P('top',1.0,0); P('base',0.0,0);
    C.passes[1].strength=lerp(0.35,0.2,s); C.render(); return {marks,L};
  }};
};

// =========================================================== L: macro lens, the paper stack folding once per fold count
SC.L=async function(){
  const LS=640; const S=new THREE.Scene(); S.background=new THREE.Color('#2e231d');
  const cam=new THREE.PerspectiveCamera(30,1,0.01,50);
  const bg=new THREE.Mesh(new THREE.PlaneGeometry(10,6),new THREE.MeshBasicMaterial({map:canvasTex(256,256,(g,w,h)=>{const r=g.createRadialGradient(128,100,10,128,128,220);r.addColorStop(0,'#6a4a36');r.addColorStop(0.6,'#43332a');r.addColorStop(1,'#2e231d');g.fillStyle=r;g.fillRect(0,0,w,h);}),fog:false})); bg.position.set(0.3,0.5,-1.4); S.add(bg);
  const wood=woodTex(); wood.wrapS=wood.wrapT=THREE.RepeatWrapping; wood.repeat.set(1,1);
  const floor=new THREE.Mesh(new THREE.PlaneGeometry(6,4),new THREE.MeshStandardMaterial({map:wood,roughness:0.6})); floor.rotation.x=-Math.PI/2; floor.receiveShadow=true; S.add(floor);
  const key=new THREE.SpotLight('#ffd6a8',6,8,0.8,0.8,1.2); key.position.set(-1.6,2.6,1.6); key.target.position.set(0.4,0,0.2); key.castShadow=true; key.shadow.mapSize.set(1024,1024); key.shadow.radius=4; S.add(key,key.target);
  S.add(new THREE.HemisphereLight('#7a5a46','#1a120c',0.8));
  const sheetM=new THREE.MeshStandardMaterial({color:'#fbf7ee',roughness:0.8,emissive:'#f6efe0',emissiveIntensity:0.38});
  const sideTex=strataTex(40,false); sideTex.wrapS=sideTex.wrapT=THREE.RepeatWrapping; const sideM=new THREE.MeshStandardMaterial({map:sideTex,roughness:0.85,emissive:'#e8dcc4',emissiveIntensity:0.3});
  const mats=[sideM,sideM,sheetM,sheetM,sideM,sideM];
  const root=new THREE.Group(); S.add(root);
  const stat=new THREE.Mesh(new THREE.BoxGeometry(1,1,1),mats); stat.castShadow=stat.receiveShadow=true; root.add(stat);
  const piv=new THREE.Group(); root.add(piv); const mov=new THREE.Mesh(new THREE.BoxGeometry(1,1,1),mats); mov.castShadow=mov.receiveShadow=true; piv.add(mov);
  const C=new EffectComposer(R); C.setSize(LS,LS); C.addPass(new RenderPass(S,cam)); C.addPass(new UnrealBloomPass(new THREE.Vector2(LS,LS),0.25,0.5,0.9)); C.addPass(new OutputPass());
  const X=1.0,Z=0.62,Y=0.16, eps=0.0004;
  return {size:LS,render(p){
    const n=p.n, fi=Math.floor(n+1e-9), u=n-fi; const axis=fi%2; const e=ease(clamp((u-0.03)/0.82,0,1)); const q=sstep(0.8,1.0,u);
    sideTex.repeat.set(1,clamp(Math.pow(2,fi-4),1,10));
    if(axis===0){stat.scale.set(X/2,Y,Z); stat.position.set(X/4,Y/2+eps,Z/2); piv.position.set(X/2,Y+eps,Z/2); piv.rotation.set(0,0,Math.PI*e); mov.scale.set(X/2,Y,Z); mov.position.set(X/4,-Y/2,0);}
    else {stat.scale.set(X,Y,Z/2); stat.position.set(X/2,Y/2+eps,Z/4); piv.position.set(X/2,Y+eps,Z/2); piv.rotation.set(-Math.PI*e,0,0); mov.scale.set(X,Y,Z/2); mov.position.set(0,-Y/2,Z/4);}
    root.scale.set(axis===0?lerp(1,2,q):1, lerp(1,0.5,q), axis===1?lerp(1,2,q):1);
    const cx=(axis===0?X/4:X/2)*root.scale.x, cz=(axis===1?Z/4:Z/2)*root.scale.z; const ang=0.55+0.15*Math.sin(p.t*0.6);
    cam.position.set(cx+Math.sin(ang)*1.55, 0.78, cz+Math.cos(ang)*1.55); cam.lookAt(cx,0.12,cz);
    R.setSize(LS,LS); C.render(); return {marks:[]};
  }};
};

window.__scenes={};
window.renderLayer=async(name,p)=>{ if(!window.__scenes[name])window.__scenes[name]=await SC[name](); if(name!=='L')R.setSize(W,H); const r=window.__scenes[name].render(p); return {img:R.domElement.toDataURL('image/jpeg',0.94),...r}; };
window.ready=true;
