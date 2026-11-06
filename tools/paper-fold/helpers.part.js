function canvasTex(w,h,draw,srgb=true){const c=document.createElement('canvas');c.width=w;c.height=h;draw(c.getContext('2d'),w,h);
  const t=new THREE.CanvasTexture(c); if(srgb)t.colorSpace=THREE.SRGBColorSpace; t.anisotropy=8; return t;}
function softDot(){return canvasTex(128,128,(g,w,h)=>{const r=g.createRadialGradient(64,64,0,64,64,64);
  r.addColorStop(0,'rgba(255,255,255,1)');r.addColorStop(0.55,'rgba(255,255,255,0.55)');r.addColorStop(0.8,'rgba(255,255,255,0.12)');r.addColorStop(1,'rgba(255,255,255,0)');g.fillStyle=r;g.fillRect(0,0,w,h);});}
function bokehDisc(){return canvasTex(128,128,(g,w,h)=>{const r=g.createRadialGradient(64,64,0,64,64,62);
  r.addColorStop(0,'rgba(255,255,255,0.55)');r.addColorStop(0.82,'rgba(255,255,255,0.75)');r.addColorStop(0.93,'rgba(255,255,255,0.9)');r.addColorStop(1,'rgba(255,255,255,0)');g.fillStyle=r;g.fillRect(0,0,w,h);});}
function sprite(tex,color,size,pos,opacity=1){const m=new THREE.SpriteMaterial({map:tex,color,transparent:true,opacity,depthWrite:false,blending:THREE.AdditiveBlending});
  const s=new THREE.Sprite(m); s.scale.set(size,size,1); s.position.copy(pos); return s;}

function compose(scene,cam,bloom){const c=new EffectComposer(R); c.setSize(W,H); c.addPass(new RenderPass(scene,cam));
  c.addPass(new UnrealBloomPass(new THREE.Vector2(W,H),bloom[0],bloom[1],bloom[2])); c.addPass(new OutputPass()); return c;}

// Paper layers texture: fine strata lines for the side faces of a folded block.
function strataTex(n,rounded){return canvasTex(512,512,(g,w,h)=>{g.fillStyle='#f4efe4';g.fillRect(0,0,w,h);
  for(let i=0;i<n;i++){const y=(i+0.5)/n*h; g.strokeStyle=`rgba(120,105,85,${0.25+0.25*rnd()})`; g.lineWidth=0.8+rnd()*0.8;
    g.beginPath(); g.moveTo(0,y+rnd()*1.5); for(let x=0;x<=w;x+=32)g.lineTo(x,y+(rnd()-0.5)*1.6); g.stroke();}
  if(rounded){const gr=g.createLinearGradient(0,0,w,0);gr.addColorStop(0,'rgba(255,255,255,0.0)');gr.addColorStop(1,'rgba(255,250,240,0.15)');g.fillStyle=gr;g.fillRect(0,0,w,h);} });}
function woodTex(){return canvasTex(2048,1024,(g,w,h)=>{g.fillStyle='#5a3a24';g.fillRect(0,0,w,h);
  for(let i=0;i<260;i++){const y=rnd()*h, a=0.05+rnd()*0.12, l=rnd()>0.5?'rgba(30,16,8,':'rgba(140,96,60,'; g.strokeStyle=l+a+')'; g.lineWidth=1+rnd()*5;
    g.beginPath(); let yy=y; g.moveTo(0,yy); for(let x=0;x<=w;x+=40){yy+=(rnd()-0.5)*3+Math.sin(x*0.004+i)*0.8; g.lineTo(x,yy);} g.stroke();}
  for(let k=0;k<5;k++){const x=rnd()*w,y=rnd()*h; for(let r=4;r<40;r+=5){g.strokeStyle='rgba(40,22,10,0.12)';g.beginPath();g.ellipse(x,y,r*2.6,r*0.7,0,0,7);g.stroke();}} });}


function skyMat(top,mid,hor,sunDir,sunCol,sunSize){return new THREE.ShaderMaterial({side:THREE.BackSide,depthWrite:false,fog:false,
  uniforms:{top:{value:new THREE.Color(top)},mid:{value:new THREE.Color(mid)},hor:{value:new THREE.Color(hor)},sd:{value:sunDir.clone().normalize()},sc:{value:new THREE.Color(sunCol)},ss:{value:sunSize}},
  vertexShader:`varying vec3 vd; void main(){vd=normalize(position); gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
  fragmentShader:`uniform vec3 top,mid,hor,sc,sd; uniform float ss; varying vec3 vd;
   float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5);}
   float n(vec2 p){vec2 i=floor(p),f=fract(p); f=f*f*(3.-2.*f); return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y);}
   void main(){float y=vd.y; vec3 c=mix(hor,mid,smoothstep(0.0,0.18,y)); c=mix(c,top,smoothstep(0.15,0.75,y));
    float d=max(dot(vd,sd),0.); c+=sc*(pow(d,10.)*0.18+pow(d,90.)*0.6); c+=sc*smoothstep(1.-ss,1.-ss*0.6,d)*6.0;
    vec2 uv=vd.xz/(vd.y+0.25)*2.0; float cl=n(uv*1.3)*0.6+n(uv*3.1)*0.3; cl=smoothstep(0.55,0.85,cl)*smoothstep(0.02,0.12,y)*(1.-smoothstep(0.35,0.6,y));
    c=mix(c,mix(vec3(0.45,0.22,0.25),sc*1.2,pow(d,3.)),cl*0.55);
    gl_FragColor=vec4(c,1.);}`});}
function ridge(z,height,color,seed,width=6000){const pts=[]; const N=120; let s=seed;
  const r=()=> (s=(s*16807)%2147483647)/2147483647; let ph=[r()*10,r()*10,r()*10];
  for(let i=0;i<=N;i++){const x=-width/2+width*i/N; const y=height*(0.55+0.25*Math.sin(x*0.0021+ph[0])+0.15*Math.sin(x*0.0067+ph[1])+0.06*Math.sin(x*0.019+ph[2]));pts.push(new THREE.Vector2(x,y));}
  const sh=new THREE.Shape(); sh.moveTo(-width/2,-50); pts.forEach(p=>sh.lineTo(p.x,p.y)); sh.lineTo(width/2,-50);
  const m=new THREE.Mesh(new THREE.ShapeGeometry(sh),new THREE.MeshBasicMaterial({color,fog:false})); m.position.z=z; return m;}
function statue(mat){ // stylised standing figure with draped shawl, 182 m tall on y=0
  const g=new THREE.Group(); const L=(pts,y0=0)=>{const m=new THREE.Mesh(new THREE.LatheGeometry(pts.map(p=>new THREE.Vector2(p[0],p[1])),48),mat); m.position.y=y0; g.add(m); return m;};
  // dhoti / lower body as one tapering skirt-like form, feet apart
  L([[0,0],[22,0],[21,6],[17,40],[15.5,70],[16,82],[0,82]]);
  // torso wrapped in shawl, broad shoulders
  const tor=L([[0,0],[16.5,0],[19,20],[22.5,42],[25.5,62],[23,72],[12,78],[0,79]],80); tor.scale.z=0.72;
  // arms hanging at the sides inside the shawl
  for(const sx of [-1,1]){const a=new THREE.Mesh(new THREE.CapsuleGeometry(5.2,58,6,16),mat); a.position.set(sx*22.5,112,1); a.rotation.z=sx*0.06; g.add(a);
    const hnd=new THREE.Mesh(new THREE.SphereGeometry(4.6,16,12),mat); hnd.position.set(sx*24.5,80,2); g.add(hnd);}
  // shawl fold falling from the left shoulder
  const sw=new THREE.Mesh(new THREE.CylinderGeometry(8,14,70,24,1,true,-0.6,1.8),mat); sw.position.set(-8,118,6); g.add(sw);
  // neck + head
  const nk=new THREE.Mesh(new THREE.CylinderGeometry(6,7,8,24),mat); nk.position.y=161; g.add(nk);
  const hd=new THREE.Mesh(new THREE.SphereGeometry(10.5,32,24),mat); hd.scale.set(0.82,1.02,0.86); hd.position.y=172; g.add(hd);
  return g;}
