
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

window.__scenes={};
window.renderLayer=async(name,p)=>{ if(!window.__scenes[name])window.__scenes[name]=await SC[name](); const r=window.__scenes[name].render(p); return {img:R.domElement.toDataURL('image/jpeg',0.94),...r}; };
window.ready=true;
